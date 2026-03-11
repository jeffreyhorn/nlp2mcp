# pak: MCP Locally Infeasible — Incomplete Stationarity

**GitHub Issue:** #1049 (https://github.com/jeffreyhorn/nlp2mcp/issues/1049)
**Status:** Open — Root cause identified but requires architectural changes
**Severity:** Medium — Model translates without structural errors, but PATH reports locally infeasible
**Date:** 2026-03-11
**Affected Models:** pak (and potentially other models with superset/subset domain patterns)

---

## Problem Summary

After fixing the structural MCP errors (#1042 unmatched equation, resolved by #1045 lead/lag fix), the pak model now reaches the PATH solver without structural pairing errors. However, PATH reports **Locally Infeasible** (MODEL STATUS 5, SOLVER STATUS 1). The largest infeasibility is at `stat_s('1985')` with a normal map residual of 1.163e+05.

---

## Root Cause Analysis (Updated 2026-03-11)

Deep investigation revealed **three distinct bugs** causing incorrect stationarity equations. These are NOT specific to `stat_s` — they affect **most** stationarity equations in the pak model.

### Bug 1: Subset/Superset Domain Mismatch — Unconditional Sum

**Location:** `src/kkt/stationarity.py:_add_indexed_jacobian_terms()` (lines 2089-2092)

The pak model has set `t(te)` where `t` = {1963..1985} is a subset of `te` = {1962..1985}. Variables like `c(te)`, `ti(te)`, `ks(te,j)` are indexed by the superset `te`, but some constraints like `incd(t)`, `invd(t)` are indexed by the subset `t`.

When building the stationarity for `c(te)`, the contribution from `incd(t)` should only include `nu_incd(te)` when `te ∈ t`. However, the code treats `t` and `te` as **completely disjoint** set names (since `"t" ≠ "te"`), and wraps the contribution in `Sum(('t',), ...)`, which sums over ALL t values unconditionally.

**Generated (wrong):**
```gams
stat_c(te).. ... + sum(t, (-1) * nu_incd(t)) + ... =E= 0;
```

**Correct:**
```gams
stat_c(te).. ... + (-1) * nu_incd(te)$(t(te)) + ... =E= 0;
```

**Affected equations:** `stat_c(te)`, `stat_ti(te)`, `stat_ks(te,j)` — all variables indexed by `te` that have contributions from constraints indexed by `t ⊂ te`.

**Fix required:** The domain overlap logic in `_add_indexed_jacobian_terms()` needs to recognize when a constraint's domain set is a subset/superset of the variable's domain set (not just when their names match or are disjoint). When `t ⊂ te`, the term should be `derivative * mult(te)$(t(te))` (direct substitution with subset guard), not `Sum(('t',), derivative * mult(t))`.

### Bug 2: First-Instance Gradient Template Assumption

**Location:** `src/kkt/stationarity.py:_build_indexed_gradient_term()` (lines 942-943)

The function uses the gradient from the **first variable instance** as a template for all instances: "For now, we use the gradient from the first instance as a placeholder. This assumes the gradient structure is uniform across instances."

For `c(te)`, the first instance is `c("1962")`, which has gradient `Const(0)` because `c(1962)` is fixed and doesn't appear in the objective sum `sum(t, delt(t)*c(t))` (which sums over `t` = {1963..1985}). As a result, the gradient term `-delt(te)` is entirely **missing** from `stat_c(te)`.

Similarly, `gnp("1985")` should have gradient `-d*dis` from `wdef`, but this is also missing due to Bug 3 below.

**Generated (wrong):**
```gams
stat_c(te).. [no gradient term] + sum(t, (-1) * nu_incd(t)) + ... =E= 0;
```

**Correct:**
```gams
stat_c(te).. (-1) * delt(te)$(t(te)) + (-1) * nu_incd(te)$(t(te)) + ... =E= 0;
```

**Fix required:** The gradient builder needs to handle non-uniform gradients. When different instances have different gradient structures, it should either:
1. Find a representative non-zero instance and generalize, or
2. Build a conditional expression that handles different cases

### Bug 3: Quoted String Literal Index Mismatch

**Location:** `src/ir/parser.py` (string literal handling) or `src/ad/derivative_rules.py` (index matching)

In `wdef.. w =E= sum(t, delt(t)*c(t)) - gama*fb + d*dis*gnp("1985")`, the expression `gnp("1985")` stores the index as `'"1985"'` (with quotes), while the variable instance `gnp(('1985',))` uses unquoted `'1985'`. The differentiation system fails to match these, so `∂wdef/∂gnp(1985) = 0` instead of the correct value `-d*dis`.

**Fix required:** Either strip quotes from string literal indices during parsing, or normalize them during differentiation to ensure `gnp("1985")` matches `gnp(1985)`.

---

### PATH Solver Output

```
SOLVER STATUS     1 Normal Completion
MODEL STATUS      5 Locally Infeasible

FINAL STATISTICS
Inf-Norm of Complementarity . .  2.6259e+04 eqn: (stat_s('1985'))
Inf-Norm of Normal Map. . . . .  1.1630e+05 eqn: (stat_s('1985'))
Inf-Norm of Minimum Map . . . .  1.6599e+01 eqn: (incd('1963'))
Inf-Norm of Fischer Function. .  3.0734e+01 eqn: (comp_conl('1963'))

771 row/cols, 5218 non-zeros
20,625 iterations
```

---

## Investigation Performed

1. **Verified Jacobian entries are correct:** The `J_eq` and `J_ineq` Jacobian matrices contain the correct derivatives for all constraints. For example, `savl(1963) x s(1963) = Const(1.0)` and `conl(1962) x c(1962) = -(1+p)` are both correct.

2. **Verified sign convention is correct:** By comparing with the working model `ajax`, confirmed that the code's convention (`+λ * J` for all inequality constraints) is mathematically correct. The `negated` flag in `ComplementarityPair` does NOT need to change the stationarity sign.

3. **Confirmed `stat_s(t)` itself is correct:** The stationarity for `s(t)` has all the right terms — variable `s` only appears in `invd(t)` and `savl(t)`, and both contributions have correct signs. The PATH infeasibility at `stat_s('1985')` is a downstream effect of other equations being wrong (e.g., `stat_c`, `stat_ti`), which causes dual variables like `nu_invd` to diverge.

4. **Verified the issue is NOT a simple fix:** The three bugs identified require architectural changes to:
   - Domain subset/superset recognition in stationarity builder
   - Non-uniform gradient handling
   - Index quoting normalization

---

## How to Reproduce

```bash
python -m src.cli data/gamslib/raw/pak.gms -o data/gamslib/mcp/pak_mcp.gms
cd data/gamslib/mcp && gams pak_mcp.gms
# Check pak_mcp.lst for: "MODEL STATUS 5 Locally Infeasible"
# and "Inf-Norm of Normal Map... stat_s('1985')"
```

---

## Prerequisites Before Another Fix Attempt

1. **Bug 1 (Subset/Superset Domains):** Implement subset recognition in `_add_indexed_jacobian_terms()`. When `mult_domain = ('t',)` and `var_domain = ('te',)`, check if `t ⊂ te` in the model's set definitions. If so, substitute `te` for `t` in the multiplier reference and add a `$(t(te))` guard instead of wrapping in `Sum(('t',), ...)`.

2. **Bug 2 (Non-uniform Gradient):** Refactor `_build_indexed_gradient_term()` to handle cases where the first instance has zero gradient but others don't. One approach: scan all instances to find one with a non-zero gradient and use that as the template.

3. **Bug 3 (Quoted Indices):** Normalize string literal indices during parsing or differentiation to strip quotes, ensuring `gnp("1985")` matches `gnp(1985)`.

4. After fixing all three bugs, regenerate pak_mcp.gms and verify with GAMS PATH solver.

---

## Related Issues

- #1042 — pak MCP unmatched equation comp_conl(1962) — FIXED (by #1045)
- #1045 — etamac MCP lead/lag stationarity — FIXED (PR #1047)

---

## Files Involved

- `src/kkt/stationarity.py` — `_build_indexed_gradient_term()` (Bug 2), `_add_indexed_jacobian_terms()` (Bug 1)
- `src/ad/constraint_jacobian.py` — Jacobian computation (correct, not the source of bugs)
- `src/ad/derivative_rules.py` — Index matching during differentiation (Bug 3)
- `src/ir/parser.py` — String literal index handling (Bug 3)
- `data/gamslib/mcp/pak_mcp.gms` — Generated MCP file
- `data/gamslib/raw/pak.gms` — Original model

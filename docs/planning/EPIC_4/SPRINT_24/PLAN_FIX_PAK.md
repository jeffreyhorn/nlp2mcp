# Plan: Fix pak Model Infeasibility (#1049)

**Goal:** Resolve pak MODEL STATUS 5 (Locally Infeasible) by fixing remaining
stationarity equation issues.

**Estimated effort:** 4-6 hours
**Models unblocked:** pak (and potentially other models with subset/superset patterns)

---

## Current State (Sprint 24 Day 11)

The pak issue (#1049) documented 3 bugs. Sprint 24 fixes have partially
addressed them:

| Bug | Status | Details |
|-----|--------|---------|
| Bug 1: Subset/superset sum wrapping | **PARTIALLY FIXED** | `nu_incd(te)` is direct (not sum-wrapped), but gradient uses `sum(t$(sameas(t,te)), ...)` instead of direct substitution |
| Bug 2: First-instance gradient template | **PARTIALLY FIXED** | Gradient IS present via sameas pattern, but may have wrong structure for some variables |
| Bug 3: Quoted string literal index | **FIXED** | `gnp("1985")` correctly matched; `stat_gnp` has `$(sameas(t,'1985'))` guard |

**523 infeasible rows remain.** However, the stationarity equations appear
structurally correct — the infeasibility may be a PATH convergence issue
rather than KKT formulation bugs.

---

## Model Structure

### Sets
- `te = {1962..1985}` — extended planning period (24 years)
- `t(te) = {1963..1985}` — planning period (23 years, subset of te)
- `j = {non-traded, traded}` — sectors

### Key Pattern: Superset/Subset Domain Mismatch
Variables indexed by `te` (superset) appear in equations indexed by both
`te` and `t` (subset). This creates domain mismatch in the Jacobian:

```
Variable c(te)     — indexed by superset
Equation incd(t)   — indexed by subset, references c(t)
Equation conl(te)  — indexed by superset, references c(te)
```

The stationarity `stat_c(te)` must combine contributions from both
`incd(t)` (subset) and `conl(te)` (superset), applying the correct
domain conditioning.

### Equations (15 total)
```
gnpd(t)..      gnp(t) =e= sum(j, v(t,j))
invd(t)..      ti(t) =e= s(t) + f(t)
invt(te)..     ti(te) =e= sum(j, i(te,j))
tgap(t)..      f(t) =e= m(t) - e(t) - v(t,"traded")
incd(t)..      gnp(t) =e= c(t) + ti(t) - f(t)
capb(t,j)..    v(t,j) =l= vb(j) + 1/k(j)*ks(t,j)
kbal(te+1,j).. ks(te+1,j) =e= ks(te,j) + i(te,j)
savl(t)..      s(t) =l= sb + alpha*(gnp(t) - gnpb)
impl(t)..      m(t) =g= mb + mgnp*(gnp(t)-gnpb) + mi*(ti(t)-tib)
invu(te+1)..   ti(te+1) =l= (1+beta)*ti(te)
invl(te+1)..   ti(te+1) =g= ti(te)
conl(te+1)..   c(te+1) =g= (1+p)*c(te)
fup(t)..       f(t) =l= q*gnp(t)
taid..         fb =e= sum(t, delt(t)*f(t))
wdef..         w =e= sum(t, delt(t)*c(t)) - gama*fb + d*dis*gnp("1985")
```

### Variables (10)
```
gnp(t), c(te), ti(te), ks(te,j), f(t), m(t), s(t), v(t,j), i(te,j), w, fb
e(t) is a parameter (exports, computed from growth)
```

---

## Investigation: Are the Equations Actually Correct?

### Test 1: Check stat_c(te) structure

**Current output:**
```gams
stat_c(te).. sum(t$(sameas(t, te)), (((-1) * delt(t)))$(t(te)))
  + nu_c_fx_1962$(sameas(te, '1962'))
  - nu_incd(te)
  + (1 + p) * lam_conl(te)
  + ((-1) * lam_conl(te-1))$(ord(te) > 1)
  =E= 0;
```

**Expected (hand-derived):**
```gams
stat_c(te).. -delt(te)$(t(te))        [objective gradient]
  + nu_c_fx_1962$(sameas(te,'1962'))   [fixing constraint]
  - nu_incd(te)$(t(te))               [from incd(t)]
  + (1+p)*lam_conl(te)                [from conl(te+1) w.r.t. c(te)]
  - lam_conl(te-1)$(ord(te)>1)        [from conl(te) w.r.t. c(te-1)]
  =E= 0;
```

**Issue found:** `nu_incd(te)` should have `$(t(te))` guard — the equation
`incd` only exists for `t ∈ te`, so the multiplier should be zero for `te=1962`.
The `.fx` line `nu_incd.fx(te)$(not t(te)) = 0` handles this at the GAMS level,
but having it in the equation body would be cleaner and potentially help PATH.

The gradient term `sum(t$(sameas(t,te)), (-1)*delt(t))$(t(te))` is functionally
correct but verbose. It could be simplified to `(-1)*delt(te)$(t(te))`.

### Test 2: Check kbal lead/lag handling

```gams
kbal(te+1,j).. ks(te+1,j) =e= ks(te,j) + i(te,j)
```

This uses `te+1` in the equation head. The stationarity `stat_ks(te,j)` should
have lead-shifted multiplier terms from `kbal`.

**Check:** Does `stat_ks` correctly handle the `te+1` offset?

### Test 3: Check that all constraint contributions are present

For each variable, verify that ALL equations referencing it contribute to
the stationarity. Cross-reference the 15 equations against the variable
domains.

---

## Fix Plan

### Phase 1: Verify correctness (1-2h)

1. **Hand-derive stat_c, stat_ti, stat_ks** and compare term-by-term with
   the generated MCP output
2. **Check all multiplier `.fx` lines** — ensure out-of-subset instances
   are fixed correctly for all equations indexed by `t` (subset)
3. **Check kbal lead/lag terms** — verify offset multiplier handling for
   `kbal(te+1,j)` contribution to `stat_ks(te,j)` and `stat_i(te,j)`

### Phase 2: Fix identified issues (2-3h)

Based on Phase 1 findings:

1. **If equations are correct but PATH can't converge:** The fix is
   better initialization. Add `nu_*.l = 0.1` or similar warm-start
   values. This is a "not fixable by nlp2mcp" conclusion.

2. **If subset conditioning is missing:** Add `$(t(te))` guards directly
   in the stationarity expression (not just via `.fx`). The stationarity
   builder needs to detect subset relationships and apply guards inline.

3. **If lead/lag multiplier offsets are wrong:** Fix `_add_indexed_jacobian_terms`
   offset handling for equations with domain offsets like `kbal(te+1,j)`.

4. **If gradient sameas pattern has issues:** Simplify
   `sum(t$(sameas(t,te)), (-1)*delt(t))$(t(te))` to
   `(-1)*delt(te)$(t(te))` — the sameas pattern may cause evaluation
   issues in PATH.

### Phase 3: Test and verify (0.5h)

1. Regenerate `pak_mcp.gms` with fixes
2. Run GAMS/PATH — check MODEL STATUS
3. Verify no regressions on dispatch canary

---

## Reproduction

**Prerequisite:** GAMSlib raw sources in `data/gamslib/raw/`
(run `python scripts/gamslib/download_models.py`).

```bash
# Generate MCP
.venv/bin/python -m src.cli data/gamslib/raw/pak.gms -o /tmp/pak_mcp.gms --quiet

# Run GAMS
gams /tmp/pak_mcp.gms lo=0

# Check result
grep "MODEL STATUS\|INFEAS" /tmp/pak_mcp.lst

# Verify stat_c structure
grep "stat_c(te)" /tmp/pak_mcp.gms
```

---

## Key Questions to Answer

1. Is the `sum(t$(sameas(t,te)), ...)` gradient pattern mathematically
   correct? Does PATH handle it the same as `expr$(t(te))`?

2. Are there missing Jacobian contributions for any variable? Specifically
   for `ks(te,j)` from `kbal(te+1,j)` — does the lead offset produce
   correct multiplier terms?

3. Does `c(1962)` have the right treatment? It's fixed via `c.fx`, and
   `stat_c(1962)` should be inactive. Is it?

4. Are the `lam_conl(te-1)$(ord(te)>1)` terms correct? The `conl(te+1)`
   equation contributes to `stat_c` via both `c(te+1)` (direct) and
   `c(te)` (lagged).

---

## Files Involved

| File | Relevance |
|------|-----------|
| `src/kkt/stationarity.py` | Domain matching, gradient building |
| `src/ad/constraint_jacobian.py` | Jacobian computation |
| `data/gamslib/raw/pak.gms` | Original model (~200 lines) |

---

## Risk Assessment

**Medium risk.** Subset/superset domain handling changes affect many models.
Any fix must be validated against the full test suite and regression-tested
on solved models (dispatch, sparta, ramsey).

# Day 11 Overflow Task: Subset-Superset Domain Violation Fix

**Estimated effort:** 3-5 hours
**Affected models:** chenery (#1164), shale (#1164), otpop (#1175), hhfair (unfiled)
**Root cause:** Stationarity equations iterate over superset but reference parameters/variables declared over strict subsets

---

## 1. Problem Statement

When a GAMS model declares `Set t(i)` (t is a subset of i) and `Parameter alp(t)`, the stationarity builder generates `stat_e(i).. alp(i) * ... =E= 0`. GAMS raises **$171 domain violation** because `alp` is only valid for indices in `t`, not all of `i`.

Replacing `alp(i)` with `alp(t)` causes **$149 uncontrolled set** because `t` is not controlled by the equation domain `(i)`.

The **only valid GAMS form** is: `stat_e(t).. alp(t) * ... =E= 0` — the equation must iterate over the subset.

---

## 2. Reproduction

```bash
# All four models translate but fail GAMS compilation:
for model in chenery shale otpop hhfair; do
  python -m src.cli data/gamslib/raw/${model}.gms -o /tmp/${model}_mcp.gms --skip-convexity-check
  (cd /tmp && gams ${model}_mcp.gms lo=2) 2>&1 | grep '$171'
done
```

---

## 3. Per-Model Details

### 3.1 chenery (Issue #1164)

**Sets:** `i = {light-ind, food+agr, heavy-ind, services}`, `t(i) = {light-ind, food+agr, heavy-ind}`

**Errors ($171):**
- `stat_e(i).. (alp(i) * nu_dh(i) + ...)$(t(i)) =E= 0;` — `alp` declared as `Parameter alp(t)`
- `stat_m(i).. (((-1) * xsi(i)) * nu_dg(i) + ...)$(t(i)) =E= 0;` — `xsi` declared as `Parameter xsi(t)`

**MCP pairing:** `stat_e(i)` pairs with variable `e(i)` (declared over `i`, superset)

### 3.2 shale (Issue #1164)

**Sets:** `tf = {1985-89..2005-09}`, `t(tf) = {1990-94..2005-09}`, `c = {24 commodities}`, `cf(c) = {final products}`

**Error ($171):**
- `stat_x(c,tf).. ((-1) * pf(c,tf)) * nu_arev(tf) + ...$(cf(c) and t(tf)) =E= 0;` — `pf` declared as `Parameter pf(c,t)` where `t(tf)`

**MCP pairing:** `stat_x(c,tf)` pairs with variable `x(c,tf)` (declared over superset `tf`)

### 3.3 otpop (Issue #1175)

**Sets:** `tt = {1965..1990}`, `t(tt) = {1974..1990}`, `tp(tt) = {1975..1990}`

**Errors ($171 + $145/$148):**
- `stat_p(tt).. ... db(tt) * p(tt) ... =E= 0;` — `db` declared as `Parameter db(t)` where `t(tt)`
- `stat_d(tt).. ... pd(1966-l) ...` — malformed index expression (separate issue)
- `stat_x(tt).. ... p(1974+(card(t)-ord(t))) ...` — complex arithmetic index (separate issue)

**MCP pairing:** `stat_p(tt)` pairs with variable `p(tt)` (declared over superset `tt`)

### 3.4 hhfair (unfiled)

**Sets:** `tl = {0..3}`, `t(tl) = {1..3}`, `tt(t) = {3}`

**Error ($171):**
- `stat_m(tl).. ... + n(tl) * nu_timemoney(tl) + ... =E= 0;` — `n` declared as `Variable n(t)` where `t(tl)`

**Note:** This is a **VarRef** (not ParamRef). The `_preserve_subset_var_indices` function (line 1880) should protect it, but `_rewrite_subset_to_superset` (called at line 4011) rewrites `n(t)` → `n(tl)` afterward.

**MCP pairing:** `stat_m(tl)` pairs with variable `m(tl)` (declared over superset `tl`)

---

## 4. Root Cause in Code

Two code paths contribute:

### Path A: `_replace_indices_in_expr` (line 1609)

- **VarRef** (line 1684): Has `_preserve_subset_var_indices` that detects subset domain and returns the variable's declared domain. Works correctly.
- **ParamRef** (line 1702): **No equivalent subset preservation.** Uses `_replace_matching_indices` with `prefer_declared_domain=True`, but `element_to_set` overrides this by mapping concrete elements to the equation's domain variable.

### Path B: `_rewrite_subset_to_superset` (line 2688)

Called at line 4011 with `subset_rename = {t: tt}` (or equivalent). This rewrites **ALL** index references (VarRef, ParamRef, MultiplierRef) from subset to superset. Even if Path A correctly preserves subset indices, Path B overwrites them.

**Both paths must be fixed.**

---

## 5. Fix Approach

### Option A: Narrow the equation domain (Recommended)

**Concept:** When a stationarity equation references parameters/variables declared over strict subsets, narrow the equation domain to the intersection of all referenced domains. Fix the paired variable to zero for superset-only elements.

**Steps:**

1. **Detection phase** (in `_add_indexed_jacobian_terms` or `build_stationarity_equations`):
   - For each stationarity equation `stat_v(D)`, collect all ParamRef/VarRef domains in the equation body
   - If any declared domain `S` is a strict subset of `D`, flag the equation

2. **Domain narrowing:**
   - Change the equation domain from `D` to `S` (the most restrictive subset)
   - Example: `stat_e(i)` → `stat_e(t)` where `t(i)`
   - All index references in the body naturally use `t` instead of `i`

3. **MCP pairing fix:**
   - The paired variable `e(i)` has domain `i` (superset)
   - Add `.fx` for superset-only elements: `nu_e.fx(i)$(not t(i)) = 0;`
   - This is already done for some cases (Issue #1053 multiplier domain widening)

4. **`_rewrite_subset_to_superset` guard:**
   - Skip rewriting ParamRef indices when the parameter's declared domain matches the subset
   - Skip rewriting VarRef indices when the variable's declared domain matches the subset
   - Only rewrite MultiplierRef and EquationRef (which are generated and always match the equation domain)

**Files to modify:**
- `src/kkt/stationarity.py`: `_add_indexed_jacobian_terms` (domain narrowing), `_rewrite_subset_to_superset` (guard)
- `src/emit/emit_gams.py`: May need `.fx` emission for narrowed equations

### Option B: Extend parameter domain (Alternative)

**Concept:** Create extended parameters declared over the superset, populated from the subset parameter with zeros for out-of-subset elements.

**Steps:**
1. For each subset-declared parameter `alp(t)` referenced in `stat_e(i)`:
   - Emit `Parameter alp_ext(i); alp_ext(i)$(t(i)) = alp(t);` before the stationarity equations
   - Replace `alp(i)` → `alp_ext(i)` in the stationarity body

**Drawback:** Creates extra parameters and assignments, cluttering the MCP output.

---

## 6. Implementation Plan (Option A)

### Step 1: Add `_preserve_subset_param_indices` (30 min)

Add subset preservation for ParamRef in `_replace_indices_in_expr`, analogous to the existing VarRef handling. This handles Path A. Reuse the existing `_preserve_subset_var_indices` function (which works for any domain tuple, not just variables):

```python
# In _replace_indices_in_expr, ParamRef case (around line 1733):
if param_domain and equation_domain and model_ir:
    preserved = _preserve_subset_var_indices(
        param_domain, equation_domain, model_ir
    )
    if preserved is not None:
        return ParamRef(param_ref.name, preserved)
```

### Step 2: Guard `_rewrite_subset_to_superset` for ParamRef and VarRef (1 hour)

Modify `_rewrite_subset_to_superset` to accept `model_ir` and skip rewriting when:
- ParamRef's declared domain contains the subset index being renamed
- VarRef's declared domain contains the subset index being renamed

This handles Path B (the hhfair VarRef case).

### Step 3: Narrow stationarity equation domain when needed (1-2 hours)

In `build_stationarity_equations` or `_add_indexed_jacobian_terms`:

1. After building a stationarity term, check if it references subset-declared symbols
2. If the equation domain is a strict superset, narrow it to the subset
3. Add `.fx` statements for the paired multiplier at superset-only elements

This is the most complex step because it affects MCP pairing and multiplier declarations.

### Step 4: Test and validate (1 hour)

- Run quality gate: `make typecheck && make lint && make format && make test`
- Smoke-test all 4 models:
  ```bash
  for m in chenery shale otpop hhfair; do
    python -m src.cli data/gamslib/raw/$m.gms -o /tmp/${m}_mcp.gms --skip-convexity-check
    (cd /tmp && gams ${m}_mcp.gms lo=2 2>&1) | grep -c '$171'
  done
  ```
- Verify MCP compiles (zero $171 errors)
- Run GAMS solve and check for MODEL STATUS 1 Optimal
- Run regression tests for all existing solved models

---

## 7. Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Domain narrowing breaks MCP pairing | Add `.fx` for out-of-subset multiplier instances |
| Regression in existing solved models | Run full test suite before/after |
| Multiple subsets in one equation | Take intersection of all subset domains |
| Alias-subset interactions | Resolve aliases to root sets before subset detection |
| `_rewrite_subset_to_superset` guard too aggressive | Only skip for ParamRef/VarRef with explicit subset domain match |

---

## 8. Success Criteria

- [ ] chenery compiles with zero $171 errors
- [ ] shale compiles with zero $171 errors
- [ ] otpop $171 error on `db(tt)` resolved (other errors may remain from `pd(1966-l)`)
- [ ] hhfair $171 error on `n(tl)` resolved
- [ ] All 4358+ existing tests pass
- [ ] No regressions in currently-solving models

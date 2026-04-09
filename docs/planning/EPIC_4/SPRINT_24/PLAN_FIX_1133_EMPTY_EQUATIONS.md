# Plan: Fix Empty MCP Equation Detection (#1133)

**Goal:** Detect equation instances that have no variable references (all
coefficient sums are zero) and emit `.fx = 0` for their associated multipliers,
preventing GAMS EXECERROR on empty MCP equation pairs.

**Estimated effort:** 4-6 hours
**Models unblocked:** fawley (and potentially any model with sparse coefficient data)

---

## Problem Recap

GAMS MCP refuses to pass empty equations (0 =E= 0) to PATH. For fawley,
`mbal(vacuum-res)` is empty because:
- `u(c)$cr(c)` → vacuum-res not in cr → 0
- `sum(p, ap(c,p)*z(p))` → ap('vacuum-res',p) all zero → 0
- `sum(tr, at(c,tr)*trans(tr))` → at('vacuum-res',tr) all zero → 0
- `import(c)$ci(c)` → vacuum-res not in ci → 0
- `sum(cfq$bposs(cfq,c), bq(c,cfq))` → no bposs entries → 0
- `invent(c)` → PARAMETER, not variable → no variable reference
- `sum((cfr,r), recipes(cfr,c,r)*rb(cfr,r))` → recipes all zero → 0

No GAMS option (holdFixed, execError, $onEmpty, domlim) bypasses this.
Explicit `nu_mbal.fx('vacuum-res') = 0` is confirmed as the fix.

---

## Approach: Static Coefficient Sparsity Analysis

### Core Idea

For each equality equation `eq(domain)`, check whether there exist domain
instances where ALL variable-referencing terms have zero coefficients. For those
instances, emit `.fx = 0` for the paired multiplier.

### Key Insight

An equation term like `sum(p, ap(c,p)*z(p))` references variable `z(p)` with
coefficient `ap(c,p)`. If `ap(c_val, p)` is zero for ALL values of `p`, the
sum contributes no variable to the equation at `c = c_val`.

Similarly, `u(c)$cr(c)` contributes variable `u` only when `c ∈ cr`.

### Algorithm

```
For each equality equation eq(d1, d2, ...) in the model:
  For each instance (v1, v2, ...) of the equation domain:
    has_variable = False
    For each variable v referenced in the equation body:
      if v appears unconditionally (e.g., x(c)):
        has_variable = True
        break
      if v appears in sum(idx, coeff(c,idx)*v(idx)):
        if any(coeff(v1, idx_val) != 0 for idx_val in idx_set):
          has_variable = True
          break
      if v appears conditioned (e.g., u(c)$cr(c)):
        if v1 ∈ cr:
          has_variable = True
          break
    if not has_variable:
      emit: nu_eq.fx('v1', 'v2', ...) = 0;
```

---

## Implementation Plan

### Step 1: Build Equation Variable Coverage Map (~2h)

**File:** `src/kkt/empty_equation_detector.py` (new)

Create a function `detect_empty_equation_instances(model_ir) → dict[str, set[tuple]]`:

1. For each equality equation:
   a. Walk the equation body (LHS - RHS) to find all VarRef nodes
   b. For each VarRef, determine its "coverage condition":
      - **Unconditional**: `x(domain_idx)` → covers all instances
      - **Set-conditioned**: `u(c)$cr(c)` → covers instances where c ∈ cr
      - **Sum with coefficients**: `sum(p, ap(c,p)*z(p))` → covers instances
        where `∃p: ap(c_val, p) ≠ 0`
      - **Sum with set condition**: `sum(cfq$bposs(cfq,c), bq(c,cfq))` →
        covers instances where `∃cfq: bposs(cfq, c_val) ≠ 0`
   c. Combine: an instance is "covered" if ANY variable has nonzero coverage
   d. Instances NOT covered are "empty"

2. For coefficient checks, use `ParameterDef.values`:
   - `ap.values` maps `(c_val, p_val) → value`
   - Check if `any(ap.values.get((c_val, p_val), 0) != 0 for p_val in p_set)`

3. For set conditions, use `SetDef.members`:
   - `cr.members` contains the set elements
   - Check if `c_val in cr.members`

**Key challenge:** Distinguishing VarRef indices that match the equation domain
vs. sum indices. Need to traverse Sum/DollarConditional structure.

### Step 2: Emit Multiplier Fixes (~1h)

**File:** `src/emit/emit_gams.py` (modify section after fx_lines)

For each equation with empty instances, emit:
```gams
nu_eq.fx('vacuum-res') = 0;
```

Use per-element `.fx` (not a domain-wide condition) since the empty instances
may not follow a simple set membership pattern.

### Step 3: Handle Edge Cases (~1h)

- **Parameters with no values dict:** Treat missing or empty `ParameterDef.values`
  as unknown, and conservatively assume coverage (don't mark as empty based on
  that parameter alone)
- **Dynamic subsets in conditions:** If set members are unknown, conservatively
  assume coverage (don't mark as empty)
- **Nested sums:** `sum((i,j), coeff(c,i,j)*v(i,j))` — check 2D sparsity
- **DollarConditional wrapping sums:** The condition may be on the sum body
- **Aliases:** Resolve alias indices when checking parameter data

### Step 4: Unit Tests (~1h)

**File:** `tests/unit/kkt/test_empty_equation_detector.py` (new)

Test cases:
1. Equation with unconditional variable reference → no empty instances
2. Equation with all-conditioned terms and sparse data → detect empty instances
3. Equation with sum over sparse parameter → detect empty instances
4. Mixed: some instances empty, some not

### Step 5: Integration Test (~0.5h)

- Verify fawley compiles and reaches PATH (MODEL STATUS 5 or better)
- Verify no regressions on dispatch canary and other solved models

---

## Simplified Alternative (Phase 1)

If the full coefficient analysis is too complex, implement a simpler version:

**Approach:** After generating the MCP GAMS code, emit a GAMS-side runtime
check that fixes multipliers for empty equations:

```gams
* Auto-detect empty equation instances
Set c_empty(c);
c_empty(c) = yes$(mbal.scale(c) = 0);
nu_mbal.fx(c)$c_empty(c) = 0;
```

This uses GAMS's equation scaling attribute which is 0 for empty equations.
However, `.scale` may not be available before Solve. An alternative:

```gams
* Emit after equation definitions but before Solve
* For each equality multiplier nu_eq(domain):
Parameter _eq_activity(domain);
_eq_activity(domain) = abs(eq.l(domain));
nu_eq.fx(domain)$(_eq_activity(domain) = 0) = 0;
```

This checks the equation's LHS value at the initial point. If it's exactly 0
(no variable contributes), the multiplier is fixed. This works because variables
are initialized to 0 or their `.l` values, so terms with nonzero coefficients
will produce nonzero LHS.

**Caveat:** If all variables happen to be 0 at the initial point AND the
constant term is also 0, a non-empty equation could be misidentified as empty.
This is unlikely but possible. The static analysis approach avoids this.

---

## Recommended Sequence

1. **Phase 1 (quick, ~1h):** Implement GAMS-side runtime check using equation
   `.l` values after model generation. Test on fawley.
2. **Phase 2 (thorough, ~3-4h):** If Phase 1 has false positives, implement
   static coefficient analysis for precise detection.

---

## Files Modified

| File | Change |
|------|--------|
| `src/kkt/empty_equation_detector.py` | NEW — static analysis (Phase 2) |
| `src/emit/emit_gams.py` | Emit `.fx = 0` for detected empty instances |
| `tests/unit/kkt/test_empty_equation_detector.py` | NEW — unit tests |
| `tests/unit/emit/test_empty_eq_fx.py` | NEW — emission test |

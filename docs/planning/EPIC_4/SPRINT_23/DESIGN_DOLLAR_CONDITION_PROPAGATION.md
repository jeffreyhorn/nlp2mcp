# Design: Dollar-Condition Propagation Through AD/Stationarity Pipeline

**Issue:** #1112
**Sprint:** 23 (Priority 3 — Match Rate Improvement)
**Created:** 2026-03-20
**Status:** Design Complete — Ready for Implementation
**Related:** #862 (sambal), #983 (elec), DESIGN_ALIAS_DIFFERENTIATION.md (#1111)

---

## 1. Problem Statement

Dollar conditions (`$cond`) on sum expressions in objective/constraint equations are not fully propagated through the AD differentiation and stationarity builder pipeline. This causes stationarity equations to include terms for index combinations that should be excluded, leading to division-by-zero errors and incorrect MCP formulations.

### Concrete Example: sambal

**Original GAMS (objective):**
```gams
devsqr..  dev  =e= sum((i,j)$xw(i,j), xw(i,j)*sqr(xb(i,j) - x(i,j))/xb(i,j))
               +  sum(i$tw(i), tw(i)*sqr(tb(i) - t(i))/tb(i));
```

The `$xw(i,j)` condition restricts the sum to only index pairs where `xw(i,j) ≠ 0`. When `xw(i,j) = 0`, `xb(i,j)` is also 0, so the expression `1/xb(i,j)` would divide by zero.

**What the stationarity equation should look like:**
```gams
stat_x(i,j)$(xw(i,j)).. <gradient terms> =E= 0;
```
The equation-level `$(xw(i,j))` guard ensures the stationarity equation is only generated for instances where the original condition holds, avoiding the division by zero.

**What currently happens:**
```gams
stat_x(i,j).. ... * 1$(xw(i,j)) + ... =E= 0;
```
The condition is preserved *within* the gradient expression as a term-level `1$(xw(i,j))` multiplier, but there is **no equation-level guard**. GAMS still evaluates the full expression for all `(i,j)` pairs, triggering division by zero before the `$` multiplier can zero out the result.

---

## 2. Pipeline Trace: Where Conditions Are Lost

### Stage 1: IR Representation (Correct)

`DollarConditional` is a first-class AST node in `src/ir/ast.py:293-317`:

```python
@dataclass(frozen=True)
class DollarConditional(Expr):
    value_expr: Expr    # Expression evaluated when condition is true
    condition: Expr     # Condition (non-zero = true)
```

The parser correctly creates `Sum` nodes with `condition` fields for conditioned sums:
- `sum((i,j)$xw(i,j), body)` → `Sum(index_sets=("i","j"), body=..., condition=ParamRef("xw", ("i","j")))`

### Stage 2: AD Differentiation (Condition Preserved as Multiplier)

In `src/ad/derivative_rules.py`, `_diff_sum()` (lines 1592-1762) handles conditioned sums correctly during differentiation:

1. **Sum collapse** (line 1652): When differentiating `sum(i$cond, f(x(i)))` w.r.t. `x(i1)`, the sum collapses and the condition is preserved as a multiplicative factor:
   ```python
   # Line 1668-1678: Issue #720
   if expr.condition is not None:
       result = Binary("*", result, _ensure_numeric_condition(expr.condition))
   ```
   This produces `df/dx(i1) * cond(i1)`, not `(df/dx(i1))$(cond(i1))`. The multiplication form is intentional — GAMS treats `$` as structural exclusion, which would prevent multiplier variables from being recognized.

2. **DollarConditional differentiation** (`_diff_dollar_conditional()`, lines 1526-1569): For `expr$cond`, the derivative is `(d/dx[expr])$cond` — condition is preserved but only the value expression is differentiated.

3. **Non-collapsing sums** (line 1758-1762): When the sum doesn't collapse, the condition passes through unchanged in the new Sum node.

**Result:** Gradient expressions contain conditions embedded as multiplicative factors or `DollarConditional` wrappers, but these are at the *expression level*, not the *equation level*.

### Stage 3: Gradient Storage (No Condition Extraction) — **GAP 1**

In `src/ad/gradient.py`, `compute_objective_gradient()` (lines 197-276) stores gradient derivatives in a `GradientVector` without extracting embedded conditions:

```python
# Line 262: derivative contains embedded DollarConditional/multiplied conditions
derivative = differentiate_expr(obj_expr, var_name, indices, config)
# Line 274: stored as-is, no condition extraction
gradient.set_derivative(col_id, derivative)
```

The `GradientVector` and `KKTSystem` have **no field to store per-variable gradient conditions**. `KKTSystem.stationarity_conditions` (line 131-135 of `kkt_system.py`) stores access conditions detected by `_find_variable_access_condition()`, but this function only scans **equation bodies**, not **gradient expressions**.

### Stage 4: Stationarity Builder (Condition Detection Incomplete) — **GAP 2**

In `src/kkt/stationarity.py`, `build_stationarity_equations()` (lines 756-945) attempts to detect conditions via three mechanisms:

1. **`_find_variable_access_condition()`** (lines 343-424): Scans equation bodies for consistent dollar conditions on variable access. Works for constraints, but **does NOT scan the objective gradient** — only equation LHS/RHS expressions.

2. **`_find_variable_subset_condition()`** (lines 427-634): Detects subset index patterns. Not relevant to dollar-condition propagation.

3. **`_extract_all_conditioned_guard()`** (lines 233-340): Extracts guards when ALL additive terms in the stationarity expression are `DollarConditional`. This *partially* addresses the problem — if the gradient term is `DollarConditional` and all Jacobian terms are also `DollarConditional`, the guard is extracted. But this fails when:
   - Some Jacobian terms are unconditional (mixed conditioned/unconditioned)
   - The gradient condition is embedded as a multiplicative factor (not `DollarConditional`)
   - Bound multiplier terms (`-π_lo + π_up`) are unconditional

### Stage 5: Stationarity Emission (Correct for What It Receives)

The emitter (`src/emit/expr_to_gams.py:638-652`) correctly emits `DollarConditional` nodes as `value$(condition)`. If the stationarity equation has `condition` set on its `EquationDef`, it emits as `stat_x(i,j)$(cond)..`. The emitter is not the problem.

### Summary of Gaps

| Stage | Component | Status | Issue |
|-------|-----------|--------|-------|
| IR | Parser | ✅ Correct | Conditions correctly parsed |
| AD | `_diff_sum()` | ⚠️ Partial | Condition preserved as multiplier, not extracted |
| AD | `_diff_dollar_conditional()` | ✅ Correct | Condition preserved on derivative |
| Gradient | `compute_objective_gradient()` | ❌ **GAP 1** | No condition extraction from gradient expressions |
| Jacobian | `compute_constraint_jacobian()` | ⚠️ Partial | Conditions preserved in expressions but not extracted |
| Stationarity | `_find_variable_access_condition()` | ❌ **GAP 2** | Only scans equation bodies, not gradients |
| Stationarity | `_extract_all_conditioned_guard()` | ⚠️ Partial | Works only when ALL terms are DollarConditional |
| Emit | `expr_to_gams()` | ✅ Correct | Emits whatever conditions it receives |

---

## 3. Proposed Design

### 3.1 Architecture Overview

The fix requires coordinated changes across 3 files to:
1. **Extract** conditions from gradient/Jacobian expressions
2. **Store** conditions in `KKTSystem`
3. **Apply** conditions to stationarity equations

```
                   ┌─────────────────┐
                   │  gradient.py    │
                   │                 │
 obj_expr ─────►   │ differentiate() │
                   │      │          │
                   │      ▼          │
                   │ gradient[col] = │
                   │   deriv_expr    │──── NEW: extract_gradient_conditions()
                   └─────────────────┘         │
                                               ▼
                   ┌─────────────────┐   gradient_conditions:
                   │ kkt_system.py   │   dict[str, Expr]
                   │                 │◄─── NEW field
                   │ KKTSystem       │
                   └─────────────────┘
                          │
                          ▼
                   ┌─────────────────┐
                   │ stationarity.py │
                   │                 │
                   │ build_stat_eqs()│──── ENHANCED: check gradient_conditions
                   │      │          │     in addition to equation access patterns
                   │      ▼          │
                   │ EquationDef     │
                   │ .condition =    │
                   │   merged_cond   │
                   └─────────────────┘
```

### 3.2 Step 1: Add `_extract_gradient_conditions()` to `src/ad/gradient.py`

**New function** (after `compute_objective_gradient()`, ~line 277):

```python
def _extract_gradient_conditions(
    gradient: GradientVector, model_ir: ModelIR
) -> dict[str, Expr]:
    """Extract embedded dollar conditions from gradient expressions.

    Scans each non-zero gradient entry for DollarConditional wrappers
    or multiplicative condition factors (Binary("*", ..., cond))
    introduced by _diff_sum() when a conditioned sum collapses.

    Returns:
        Mapping: var_name -> condition_expr (single equation-level guard per variable).
        Only includes variables where ALL gradient entries share the same condition.
    """
```

**Logic:**
1. For each non-zero gradient entry `(col_id, derivative)`:
   - Inspect only the **top level** of the derivative expression
   - If the top-level expression is `DollarConditional(value, cond)` → extract `cond`
   - Else, if the top-level expression is `Binary("*", ..., DollarConditional(Const(1.0), cond))` → extract `cond`
   - Do **not** attempt to combine multiple conditions or walk/merge nested condition trees; at most one guard is extracted from the top level
2. Group by variable name
3. Return only variables where ALL instances share a common condition structure (same as `_find_variable_access_condition()` does for equation bodies)

**Condition extraction patterns** (from `_diff_sum` output, top-level only):

| Derivative Pattern | Extracted Condition |
|---|---|
| `DollarConditional(deriv, cond)` | `cond` |
| `Binary("*", deriv, DollarConditional(Const(1.0), cond))` | `cond` (unwrapped from numeric condition wrapper) |

### 3.3 Step 2: Add `gradient_conditions` field to `KKTSystem`

**File:** `src/kkt/kkt_system.py`, after `stationarity_conditions` (line 135):

```python
# Issue #1112: Dollar conditions extracted from gradient expressions.
# Maps var_name -> condition Expr for variables whose objective gradient
# was computed from a conditioned sum. Used by the stationarity builder
# to add equation-level guards.
gradient_conditions: dict[str, Expr] = field(default_factory=dict)
```

**Population:** In `src/kkt/kkt_system.py` (wherever `KKTSystem` is constructed), call `_extract_gradient_conditions()` after gradient computation and store the result.

### 3.4 Step 3: Enhance condition detection in `build_stationarity_equations()`

**File:** `src/kkt/stationarity.py`, lines 856-881

After the existing three-stage condition detection (access condition → subset condition → all-conditioned guard), add a fourth stage:

```python
# Stage 4 (Issue #1112): Check gradient conditions.
# If the objective gradient for this variable was computed from a
# conditioned sum (e.g., sum((i,j)$xw(i,j), ...)), the gradient
# carries an embedded condition that should become an equation-level
# guard on the stationarity equation.
if access_cond is None and var_name in kkt.gradient_conditions:
    access_cond = kkt.gradient_conditions[var_name]
```

**Merging logic:** Stage 4 is fallback-only. If no `access_cond` was found from equation analysis and a gradient condition exists, use that gradient condition as `access_cond`. If an `access_cond` already exists, Stage 4 does not modify it (no `AND`-merge is performed). In practice, a variable is usually either fully conditioned in equations or conditioned only in the gradient, so the fallback-only approach is sufficient.

### 3.5 Step 4: Handle Jacobian conditions (if needed)

**Assessment:** The Jacobian pathway already has partial condition handling:

1. **Equation-level conditions** (stationarity.py:2757-2770): Issue #877 already propagates `eq_def.condition` into Jacobian terms as `DollarConditional` wrappers. This handles constraints with explicit `$` conditions.

2. **Sum conditions in constraints**: When a constraint has `sum(i$cond, ...)`, the AD differentiation embeds `cond` in the Jacobian derivative expression (same as for gradients). `_extract_all_conditioned_guard()` can detect these if ALL terms are conditioned.

**Gap:** If a constraint uses a conditioned sum for only SOME of the terms involving a variable, the Jacobian derivative carries the condition but `_extract_all_conditioned_guard()` won't fire (not all terms are conditioned). This is a separate, lower-priority issue — it doesn't cause division-by-zero because the condition multiplier zeros out the term, and the unconditional terms provide a valid stationarity equation.

**Recommendation:** Focus on gradient conditions first (the primary cause of sambal/qsambal failures). Jacobian condition extraction can be a follow-up if additional models require it.

---

## 4. Affected Models

### 4.1 Primary Targets (Known Failures)

| Model | Issue | Pattern | Current Status |
|-------|-------|---------|----------------|
| **sambal** | #862 | `sum((i,j)$xw(i,j), .../xb(i,j))` — division by zero when `xb=0` | path_solve_terminated |
| **qsambal** | — | Same pattern as sambal (quadratic variant) | path_solve_terminated |

### 4.2 Secondary Targets (Potential Improvement)

| Model | Dollar-Cond Count | Status | Notes |
|-------|-------------------|--------|-------|
| elec | 1 | path_solve_terminated | `$(ut(i,j))` correctly preserved; current failure is PATH convergence, not dollar-condition |
| fawley | 6 | path_solve_terminated | May benefit if conditions prevent domain errors |
| sroute | 2 | path_syntax_error | #919: empty stationarity; may be related |

### 4.3 Models with Dollar Conditions (42 total in corpus)

High-occurrence models: andean (42), mexls (27), gancnsx (18), ganges (18), gangesx (18), minlphi (12), turkey (12), indus89 (11), turkpow (11), dinam (10), nebrazil (9), ferts (8), iswnm (8), lop (7), fawley (6), pdi (6), shale (6), tfordy (6), egypt (5), msm (5), phosdis (5), sarf (5), gtm (2), partssupply (2), qsambal (2), sambal (2), sddp (2), sroute (2), weapons (2), agreste (1), plus additional models.

**Key observation:** Most of these 42 models either (a) already solve correctly because the conditions don't guard against domain errors, or (b) have other blocking issues (translation timeout, parse failure) that mask the dollar-condition problem. Only sambal/qsambal have confirmed dollar-condition propagation as the primary failure cause.

### 4.4 Regression Risk

**Low.** The change adds equation-level guards to stationarity equations, making them *more* restrictive (fewer instances evaluated). This cannot cause new incorrect evaluations — it can only prevent evaluations that would have been zero anyway. The main regression risk is:

1. **Over-extraction:** Extracting a condition from the gradient that doesn't belong at the equation level. Mitigated by requiring ALL gradient entries for a variable to share the same condition (consistent-condition check).

2. **Guard conflicts with existing conditions:** If `_find_variable_access_condition()` already found a condition AND gradient extraction finds a different condition, the AND-merge could be overly restrictive. Mitigated by the precedence chain: only check gradient conditions when the first three stages found nothing.

3. **Existing tests:** 42 models use dollar conditions; most already pass. The existing test suite (~4,145 tests) provides broad regression coverage.

---

## 5. Interaction with Alias Differentiation (#1111)

### 5.1 Code Location Overlap

| Component | #1111 (Alias) | #1112 (Dollar-Condition) | Overlap? |
|-----------|---------------|--------------------------|----------|
| `derivative_rules.py:_diff_varref()` | **Modified** — adds alias matching | Not modified | No |
| `derivative_rules.py:_diff_sum()` | **Modified** — adds `bound_indices` parameter | Not modified (existing condition handling is sufficient) | No |
| `derivative_rules.py:differentiate_expr()` | **Modified** — threads `bound_indices` | Not modified | No |
| `gradient.py` | Not modified | **Modified** — adds `_extract_gradient_conditions()` | No |
| `kkt_system.py` | Not modified | **Modified** — adds `gradient_conditions` field | No |
| `stationarity.py:build_stationarity_equations()` | Not modified | **Modified** — adds gradient condition check | No |
| `stationarity.py:_find_variable_access_condition()` | Not modified | Not modified | No |

### 5.2 Independence Assessment

**The two fixes are architecturally independent.** They modify different files and different functions:

- **#1111 (Alias):** Modifies how `_diff_varref()` matches indices, with `bound_indices` context from `_diff_sum()`. Changes are entirely within `src/ad/derivative_rules.py`.
- **#1112 (Dollar-Condition):** Adds condition extraction from gradient/Jacobian results and applies to stationarity equation definitions. Changes span `gradient.py`, `kkt_system.py`, and `stationarity.py`.

**No shared data structures.** The alias fix uses `bound_indices: frozenset[str]` threaded through `differentiate_expr()`. The dollar-condition fix uses `gradient_conditions: dict[str, Expr]` stored on `KKTSystem`. These don't interact.

**Implementation order:** Either fix can be implemented first. However, implementing #1112 first is slightly preferred because:
1. It has a simpler code footprint (3 localized changes vs. threading a parameter through the entire AD call stack)
2. It unblocks sambal/qsambal immediately
3. The alias fix's `bound_indices` changes to `differentiate_expr()` signature could cause merge conflicts if done simultaneously, but since #1112 doesn't touch `differentiate_expr()`, no conflict.

### 5.3 Models Requiring Both Fixes

No model has been identified that requires BOTH alias differentiation AND dollar-condition propagation to solve correctly. The affected model sets are disjoint:
- **Alias:** qabel, catmix, fdesign, harker, hydro, pindyck, port (7 verified-convex mismatches)
- **Dollar-condition:** sambal, qsambal (division-by-zero from missing guards)

This confirms the fixes can be tested independently.

---

## 6. Implementation Plan

### 6.1 Files to Modify

| File | Change | Lines | Effort |
|------|--------|-------|--------|
| `src/ad/gradient.py` | Add `_extract_gradient_conditions()` | ~277 (new, ~40 lines) | 1h |
| `src/kkt/kkt_system.py` | Add `gradient_conditions` field | ~136 (1 line + docstring) | 10min |
| `src/kkt/stationarity.py` | Add gradient condition check in `build_stationarity_equations()` | ~882 (5-10 lines) | 30min |

### 6.2 Estimated Effort

| Phase | Time |
|-------|------|
| Implementation (3 files) | 2h |
| Unit tests | 1h |
| Smoke test (sambal, qsambal) | 30min |
| Pipeline retest | 30min |
| **Total** | **4h** |

### 6.3 Test Plan

1. **Unit test: `_extract_gradient_conditions()`**
   - Test with gradient containing `DollarConditional` wrapper → extracts condition
   - Test with gradient containing `Binary("*", deriv, DollarConditional(Const(1.0), cond))` → extracts condition
   - Test with mixed (some entries conditioned, some not) → returns None
   - Test with all entries sharing same condition → returns condition

2. **Integration test: sambal**
   - Generate MCP: `python -m src.cli data/gamslib/raw/sambal.gms -o /tmp/sambal_mcp.gms`
   - Verify stationarity equation has equation-level `$(xw(i,j))` guard
   - If GAMS available: verify MODEL STATUS ≠ 4/5

3. **Integration test: qsambal**
   - Same as sambal (quadratic variant)

4. **Regression test: existing pipeline**
   - Run `make test` (all ~4,145 tests)
   - Run full pipeline: verify no solve/match regressions

---

## 7. Detailed Condition Extraction Algorithm

### 7.1 Expression Patterns from `_diff_sum()`

When `_diff_sum()` collapses a conditioned sum `sum(i$cond, f(x))` w.r.t. `x(i1)`, it produces:

```python
Binary("*", f'(x(i1)), _ensure_numeric_condition(cond))
```

**Note:** In the current AD implementation, the `_diff_sum()` collapse path preserves the sum condition in **symbolic** index form (e.g. `xw(i,j)`), as documented in `src/ad/derivative_rules.py` (see Issue #1085). Gradient entries are therefore already annotated with symbolic conditions, so no index "de-concretization" helper is required.

`_ensure_numeric_condition()` converts conditions to numeric 0/1 form:
- `Const` → used directly (folded to `Const(1.0)` or `Const(0.0)`)
- Any non-`Const` condition (including `ParamRef`, `VarRef`, `SetMembershipTest`, etc.) → wrapped as `DollarConditional(Const(1.0), cond)` to get 0/1 semantics while preserving the symbolic condition inside `cond`

So the gradient derivative for variable `x(i1)` always looks like:
- `Binary("*", deriv, DollarConditional(Const(1.0), cond))`
  where `cond` contains the original symbolic condition (e.g. a `ParamRef("xw", ("i", "j"))` or a `SetMembershipTest`).

### 7.2 Extraction Logic

```python
def _extract_condition_from_expr(expr: Expr) -> Expr | None:
    """Extract the condition from a gradient derivative expression.

    Recognizes patterns:
    1. Binary("*", value, condition_factor) — from _diff_sum collapse
    2. DollarConditional(value, condition) — from _diff_dollar_conditional
    3. Binary("*", DollarConditional(value, c1), c2) — combined

    Returns the condition expression, or None if no condition found.
    """
    if isinstance(expr, DollarConditional):
        return expr.condition
    if isinstance(expr, Binary) and expr.op == "*":
        # Check right operand for condition pattern
        right_cond = _is_condition_factor(expr.right)
        if right_cond is not None:
            return right_cond
        # Check left operand (condition may be on either side after simplification)
        left_cond = _is_condition_factor(expr.left)
        if left_cond is not None:
            return left_cond
    return None

def _is_condition_factor(expr: Expr) -> Expr | None:
    """Check if an expression is a condition factor from _ensure_numeric_condition.

    Since _ensure_numeric_condition() wraps ALL non-Const conditions as
    DollarConditional(Const(1.0), cond), this only needs to match that pattern.

    Returns the underlying condition, or None.
    """
    if isinstance(expr, DollarConditional) and isinstance(expr.value_expr, Const) and expr.value_expr.value == 1.0:
        return expr.condition
    return None
```

### 7.3 Per-Variable Aggregation

```python
# Sentinel to mark variables that have at least one unconditional gradient entry,
# meaning no common equation-level guard is possible.
_NO_COMMON_CONDITION = object()

def _extract_gradient_conditions(
    gradient: GradientVector, model_ir: ModelIR
) -> dict[str, Expr]:
    """Extract common conditions from gradient entries, grouped by variable."""
    var_conditions: dict[str, object | list[Expr]] = {}

    for col_id in range(gradient.num_cols):
        derivative = gradient.get_derivative(col_id)
        if derivative is None or (isinstance(derivative, Const) and derivative.value == 0):
            continue

        var_name, indices = gradient.index_mapping.col_to_var[col_id]
        cond = _extract_condition_from_expr(derivative)
        if cond is None:
            # This variable has an unconditional gradient entry —
            # no common condition possible
            var_conditions[var_name] = _NO_COMMON_CONDITION
            continue

        if var_conditions.get(var_name) is _NO_COMMON_CONDITION:
            continue  # Already marked unconditional, skip
        if var_name not in var_conditions:
            var_conditions[var_name] = []
        var_conditions[var_name].append(cond)

    # For each variable, check if all entries share a structurally identical condition.
    # Because _diff_sum() preserves conditions in symbolic index form (see Issue #1085),
    # gradient entries already carry symbolic conditions like xw(i,j), so no
    # concrete-to-symbolic reconstruction is needed.
    result: dict[str, Expr] = {}
    for var_name, conds in var_conditions.items():
        if conds is _NO_COMMON_CONDITION or not conds:
            continue
        first = conds[0]
        if all(repr(c) == repr(first) for c in conds):
            result[var_name] = first
    return result
```

### 7.4 Symbolic Condition Handling

Because gradients already carry the sum's condition in symbolic form (per Issue #1085), the stationarity builder should:

- Read the symbolic condition directly from any gradient entry associated with the variable (e.g. `xw(i,j)`), and
- Normalize/propagate that condition into the generated stationarity equation without attempting to remap concrete index values back to symbolic ones.

This design deliberately avoids:

- Modifying `_diff_sum()` solely to expose conditions, and
- Post-hoc reconstruction of symbolic conditions from concrete index tuples.

The `_extract_gradient_conditions()` function in §7.3 implements this directly: it reads the condition from gradient entries and, since all entries for a given variable share the same symbolic condition, uses it as-is for the equation-level guard.

---

## 8. Risk Assessment

### 8.1 Regression Risk: LOW

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Over-extraction (condition applied where it shouldn't be) | Low | Medium | Require ALL gradient entries to share same condition |
| Guard conflicts with existing conditions | Very Low | Low | Only apply when no other condition found (Stage 4 in priority chain) |
| Simplification removes condition factors | Low | Medium | Extract before simplification, or handle simplified forms |
| Test failures in existing suite | Low | Low | Run full `make test` before and after |

### 8.2 Model Impact Risk: VERY LOW

- When applied under the "apply guard only when safe" criteria (Sections 4–6), this change only adds equation-level guards that are more restrictive, never less
- Under those criteria, it is not expected to cause new incorrect evaluations
- Under those criteria, it is not expected to introduce new infeasibilities, because guarded instances are constructed so that all other stationarity terms are structurally zero when the guard is false and the equation reduces to 0=0
- The intended effect is to *fix* existing division-by-zero or domain errors; violating the guard-safety criteria could change the KKT system and must be avoided by implementation checks

### 8.3 Performance Risk: NEGLIGIBLE

- Condition extraction runs once per gradient computation (O(num_variables × num_instances))
- Adds one dict lookup per stationarity equation in `build_stationarity_equations()`
- No change to differentiation performance

---

## 9. KU Verification Results

### KU-14: Dollar-Condition Propagation Scope

**Result:** ❌ REFUTED — Dollar-condition propagation requires changes to BOTH gradient AND (eventually) Jacobian pathways.

**Evidence:**
- **Gradient (primary):** `compute_objective_gradient()` in `gradient.py` stores derivatives with embedded conditions but never extracts them. `_find_variable_access_condition()` in `stationarity.py` only scans equation bodies, not gradient expressions. This is the primary gap causing sambal/qsambal failures.
- **Jacobian (secondary):** `compute_constraint_jacobian()` similarly preserves conditions within derivative expressions. The stationarity builder's Issue #877 code (`_extract_all_conditioned_guard()`) partially handles this for the case where ALL terms are conditioned, but misses mixed-condition cases. Constraint-level conditions are already propagated via `eq_def.condition` (Issue #877, stationarity.py:2757-2770).
- **Sprint 23 scope:** Gradient-only fix sufficient for sambal/qsambal. Jacobian condition extraction is a potential follow-up if additional models need it.

The original assumption ("primarily requires changes to gradient only") was partially correct for the Sprint 23 scope, but the full architectural fix spans both pathways.

### KU-15: Independence of Alias and Dollar-Condition Fixes

**Result:** ✅ VERIFIED — The two fixes are architecturally independent with no code overlap.

**Evidence:**
- **#1111 (Alias)** modifies `src/ad/derivative_rules.py` only: `_diff_varref()`, `_diff_sum()`, `differentiate_expr()` (adding `bound_indices` parameter).
- **#1112 (Dollar-Condition)** modifies `src/ad/gradient.py`, `src/kkt/kkt_system.py`, and `src/kkt/stationarity.py` (adding condition extraction and storage). Does NOT touch `derivative_rules.py`.
- No shared data structures: alias fix uses `bound_indices: frozenset[str]` threaded through `differentiate_expr()`; dollar-condition fix uses `gradient_conditions: dict[str, Expr]` on `KKTSystem`.
- No shared affected models: alias targets qabel/catmix/fdesign/etc.; dollar-condition targets sambal/qsambal.
- Either fix can be implemented first without affecting the other.

---

## 10. References

### Files

| File | Relevant Lines | Purpose |
|------|---------------|---------|
| `src/ir/ast.py` | 293-317 | `DollarConditional` class definition |
| `src/ad/derivative_rules.py` | 1526-1569 | `_diff_dollar_conditional()` |
| `src/ad/derivative_rules.py` | 1592-1762 | `_diff_sum()` with condition handling |
| `src/ad/gradient.py` | 197-276 | `compute_objective_gradient()` |
| `src/ad/constraint_jacobian.py` | 250-351 | `compute_constraint_jacobian()` |
| `src/kkt/kkt_system.py` | 73-191 | `KKTSystem` dataclass |
| `src/kkt/stationarity.py` | 233-340 | `_extract_all_conditioned_guard()` |
| `src/kkt/stationarity.py` | 343-424 | `_find_variable_access_condition()` |
| `src/kkt/stationarity.py` | 756-945 | `build_stationarity_equations()` |
| `src/kkt/stationarity.py` | 2757-2770 | Issue #877 equation condition propagation |

### Issues

- #1112: KKT: Dollar-condition propagation through AD/stationarity pipeline
- #862: sambal domain conditioning (Bug 1 unfixed)
- #983: elec division by zero (resolved — now PATH convergence issue)
- #877: All-conditioned guard extraction
- #720: Sum condition preservation during collapse
- #724: Variable access conditions for stationarity
- #1005: Free index detection for condition validation

### Related Design Documents

- `DESIGN_ALIAS_DIFFERENTIATION.md` — #1111 alias-aware differentiation design
- `docs/issues/ISSUE_862_sambal-kkt-domain-conditioning.md` — sambal root cause analysis
- `docs/issues/ISSUE_983_elec-mcp-division-by-zero-distance.md` — elec analysis (resolved differently)

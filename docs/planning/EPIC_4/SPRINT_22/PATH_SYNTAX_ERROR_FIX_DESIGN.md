# path_syntax_error Fix Design (Sprint 22 Prep Task 7)

**Created:** 2026-03-06
**Sprint:** 22 (Prep Task 7)
**Status:** Complete
**Dependencies:** Task 2 (PATH_SYNTAX_ERROR_STATUS.md)
**Unknowns Verified:** KU-02, KU-04

---

## Executive Summary

This document designs the implementation approach for fixing Sprint 22's three target path_syntax_error subcategories: **C** (10 models, $149 uncontrolled sets), **B** (2 models, $170 domain violations), and **G** (4 models, $125 set index reuse). Combined, these fixes address **16 models** in an estimated **5-9h** of implementation effort.

Each subcategory has been traced to specific source code, with proposed changes, LOC estimates, test strategies, and regression risk assessments.

---

## 1. Subcategory C: Uncontrolled Set in Stationarity Equations

### 1.1 Models Affected (10)

ampl, dyncge, glider, harker, korcge, paklive, robert, shale, tabora, trnspwl

### 1.2 Error Pattern

GAMS Error $149: "Set `x` is not controlled by any index."

The KKT stationarity generator emits equations with set indices that are not controlled by the equation's domain or any enclosing Sum/Prod aggregation. GAMS requires every set index to be controlled either by the equation domain or by an enclosing aggregation operator.

### 1.3 Root Cause Analysis

**Primary file:** `src/kkt/stationarity.py`
**Key functions:** `_add_indexed_jacobian_terms()` (lines 1616-1816), `_collect_free_indices()` (lines 1543-1613)

The existing Issue #670 logic (lines 1748-1759 for indexed constraints, lines 1774-1783 for scalar constraints) already attempts to detect and wrap uncontrolled indices in Sum nodes. However, it fails in two sub-patterns:

#### Sub-pattern 1: Scalar Stationarity with Indexed Symbols (ampl, dyncge, glider)

The stationarity variable is scalar (no domain), but the derivative expression contains free set indices from the original constraint's inner sums. The Issue #670 scalar path (lines 1774-1783) wraps uncontrolled indices in Sum, but `_collect_free_indices()` may not detect all cases — particularly when:
- The derivative includes `ParamRef` indices from parameters with implicit domains (e.g., `a(i,j)` where `i` and `j` are not in the equation domain)
- `SymbolRef` nodes in the derivative tree reference set indices not recognized as "known sets" by `_is_known_set()`

#### Sub-pattern 2: Domain Mismatch in Stationarity (harker, korcge, paklive, robert, shale, tabora, trnspwl)

The stationarity equation has a domain (e.g., `stat_x(i)`), but the derivative expression contains additional set indices beyond that domain (e.g., `j` from a cross-indexed sum `sum(j, a(i,j) * ...)`). The Issue #670 indexed path (lines 1748-1759) computes:

```python
controlled = var_domain_set | mult_domain_set
free_in_deriv = _collect_free_indices(indexed_deriv, kkt.model_ir)
uncontrolled = free_in_deriv - controlled
```

The issue is that `_collect_free_indices()` correctly identifies free indices but the `controlled` set may be incomplete — it uses `var_domain_set` (the stationarity variable's domain) and `mult_domain_set` (the multiplier's domain) but does not account for indices that should be controlled by the equation domain itself or by outer Sum nodes already wrapping the term.

### 1.4 Proposed Fix

**Approach:** Enhance the domain conditioning logic in `_add_indexed_jacobian_terms()` to correctly identify and wrap ALL uncontrolled indices.

**Specific changes:**

1. **Enhance `_collect_free_indices()` robustness** (~20 LOC):
   - Ensure `EquationRef` indices are walked (currently handled but verify edge cases)
   - Add handling for `SetAttrRef` nodes that may contain set indices
   - Verify that case-insensitive matching is consistent between `_is_known_set()` and the `controlled` set computation

2. **Fix the `controlled` set computation** (~15 LOC, lines 1748-1759):
   - Currently: `controlled = var_domain_set | mult_domain_set`
   - After the Sum wrapping, the newly-added Sum indices become controlled, but they're not removed from subsequent checks
   - Ensure the controlled set includes indices from any enclosing Sum/Prod already in the expression

3. **Add domain conditioning for the scalar path** (~15 LOC, lines 1774-1783):
   - The scalar path computes `uncontrolled = free_in_deriv - {d.lower() for d in var_domain}`
   - Verify this correctly handles cases where `var_domain` is empty (scalar variable) — all derivative indices become uncontrolled
   - Add a guard: if the stationarity equation is scalar and the derivative has free indices, wrap ALL free indices in a single Sum

**Files to modify:**
| File | Lines | Change | Est. LOC |
|------|-------|--------|----------|
| `src/kkt/stationarity.py` | 1543-1613 | Enhance `_collect_free_indices()` | ~20 |
| `src/kkt/stationarity.py` | 1748-1759 | Fix indexed-constraint domain conditioning | ~15 |
| `src/kkt/stationarity.py` | 1774-1783 | Fix scalar-constraint domain conditioning | ~15 |
| `tests/unit/kkt/test_stationarity_uncontrolled_indices.py` | new | Unit tests for uncontrolled index detection | ~60 |

**Total estimated LOC:** ~110
**Estimated effort:** 3-5h

### 1.5 Regression Risk Assessment (KU-02 Verification)

**Status: VERIFIED — LOW regression risk**

**Key finding:** The fix is **additive** — it enhances the existing Sum-wrapping logic to catch cases it currently misses. It does NOT modify the core stationarity equation derivation logic.

**Evidence:**

1. **Fix only activates when uncontrolled indices are detected.** The existing code path (lines 1748-1759, 1774-1783) already has an `if uncontrolled:` guard. The fix improves what indices are detected as uncontrolled; it does not change what happens when no uncontrolled indices exist.

2. **Currently-solving models have no uncontrolled indices.** If they did, GAMS would raise $149 and they wouldn't solve. The fix's Sum-wrapping logic is only triggered for models that currently fail with $149.

3. **`_collect_free_indices()` changes are narrowing, not broadening.** The function may be enhanced to detect additional free indices (improving detection), but it cannot cause false positives for indices that ARE controlled — the walk explicitly tracks bound indices from enclosing Sum/Prod nodes (line 1576).

4. **Existing test coverage.** Stationarity generation and `_collect_free_indices()` behavior are already covered by unit tests under `tests/unit/kkt/`. The regression test strategy (Section 4) will add specific tests for the 10 affected models within that suite.

**Mitigation:** Run full pipeline retest after implementation. Compare solve/match counts before vs after. Any currently-solving model that regresses indicates a bug in the fix, not an inherent risk.

### 1.6 Test Strategy

1. **Unit tests:** Add tests under `tests/unit/kkt/` (extending the existing `_collect_free_indices()` coverage) verifying:
   - `_collect_free_indices()` correctly identifies uncontrolled indices in representative derivative expressions
   - Sum wrapping is applied when uncontrolled indices are detected
   - Sum wrapping is NOT applied when all indices are controlled (regression guard)

2. **Integration tests:** For 3 representative models (dyncge, harker, trnspwl):
   - Verify MCP file compiles without $149 errors
   - Verify PATH solver runs (may not match — that's acceptable at this stage)

3. **Regression test:** Full pipeline retest (`run_full_test.py --only-parse --quiet` + solve) — verify no currently-solving model regresses.

---

## 2. Subcategory B: Domain Violation in Emitted Parameter Data

### 2.1 Models Affected (2)

cesam, cesam2

### 2.2 Error Pattern

GAMS Error $170: "Domain violation for element `x`."

The emitter writes parameter data entries for domain combinations where one or more elements don't belong to the declared domain set. GAMS performs domain checking and rejects entries with invalid domain elements.

### 2.3 Root Cause Analysis

**Primary file:** `src/emit/original_symbols.py`
**Key function:** `emit_original_parameters()` (lines 706-834)

The parameter data emission loop (lines 789-815) iterates over `param_def.values.items()` and emits each `(key_tuple, value)` pair directly. It performs several filters:
- `_expand_table_key()` for dimension matching (line 791)
- Skip subset-qualified values (line 800)
- Skip zero-valued entries (line 807)

**Missing filter:** No domain membership validation. The loop does not check whether each element of `key_tuple` is a member of the parameter's declared domain set. When the IR parser captures table data with a Cartesian product of row/column headers, some entries have domain elements that don't exist in the declared domain sets (e.g., a parameter `p(i,j)` where a key contains an element not in set `i`).

This is the same class of issue that affected egypt/fawley in Sprint 21, but cesam/cesam2 are newly-translating models encountering it for the first time.

### 2.4 Proposed Fix

**Approach:** Add a domain membership validation filter in the parameter data emission loop.

**Specific changes:**

1. **Add `_is_in_domain()` helper** (~25 LOC):
   ```python
   def _is_in_domain(key_tuple: tuple[str, ...], domain: tuple[str, ...], model_ir: ModelIR) -> bool:
       """Check if each element of key_tuple is a member of its corresponding domain set."""
       for element, set_name in zip(key_tuple, domain):
           set_def = model_ir.sets.get(set_name)
           if set_def is None:
               continue  # unknown domain — allow
           # Check membership (case-insensitive)
           if element.lower() not in {e.lower() for e in set_def.elements}:
               return False
       return True
   ```

2. **Insert domain check in emission loop** (~5 LOC, after line 795):
   ```python
   # Skip entries with domain violations
   if domain and not _is_in_domain(expanded_key, domain, model_ir):
       continue
   ```

**Files to modify:**
| File | Lines | Change | Est. LOC |
|------|-------|--------|----------|
| `src/emit/original_symbols.py` | ~795 | Add domain membership check | ~5 |
| `src/emit/original_symbols.py` | new helper | `_is_in_domain()` function | ~25 |
| `tests/unit/emit/test_original_symbols.py` | new | Unit tests for domain filtering | ~40 |

**Total estimated LOC:** ~70
**Estimated effort:** 1-2h

### 2.5 Regression Risk Assessment

**LOW risk.**

1. **Filter is purely subtractive** — it removes invalid entries that would cause GAMS $170 errors. Currently-solving models by definition don't have domain-violating entries (GAMS would reject them).

2. **Conservative membership check** — unknown domains (set not found in IR) default to ALLOW, preventing false filtering.

3. **Precedent:** Sprint 21 used a similar approach for egypt/fawley without regressions.

**Mitigation:** The `_is_in_domain()` helper uses set element membership. Edge case risk: if the IR's set elements are incomplete (not all elements captured from the source GAMS file), valid entries could be filtered out. To guard against this, add a logging/warning path for filtered entries during development.

### 2.6 Test Strategy

1. **Unit tests:** Test `_is_in_domain()` with valid and invalid domain entries, empty domains, unknown sets.

2. **Integration tests:** For cesam and cesam2:
   - Verify MCP file compiles without $170 errors
   - Verify no existing parameter data was incorrectly filtered

3. **Regression test:** Full pipeline retest — verify no currently-solving model regresses.

---

## 3. Subcategory G: Set Index Reuse Conflict in Sum

### 3.1 Models Affected (4)

kand, prolog, spatequ, srkandw

### 3.2 Error Pattern

GAMS Error $125: "Set `x` is used in a nested fashion."

The emitter outputs sum/prod expressions where an inner aggregation reuses an index name that's already bound by an outer aggregation or the equation domain. GAMS prohibits this shadowing.

### 3.3 Root Cause Analysis

**Primary file:** `src/emit/expr_to_gams.py`
**Key functions:** `collect_index_aliases()` (lines 670-745), `resolve_index_conflicts()` (lines 748-868)

The existing alias detection (`collect_index_aliases()`) only checks Sum/Prod indices against the **equation domain** (line 702):

```python
for idx in index_sets:
    if idx in domain_set:
        aliases_needed.add(idx)
```

This misses two critical conflict patterns:

#### Pattern 1: Nested Same-Name Reuse (spatequ, srkandw)

An outer Sum uses index `cc` and an inner Sum also uses `cc`:
```
sum(cc, ... sum(cc, ...) ...)
```

The inner `cc` conflicts with the outer `cc`, not with the equation domain. `collect_index_aliases()` would only detect this if `cc` were also in the equation domain.

#### Pattern 2: Case-Insensitive Collision (kand, prolog)

The equation domain uses `(r,c)` but the KKT derivation introduces `sum((R,C), ...)`. GAMS is case-insensitive, so `R` conflicts with `r` and `C` conflicts with `c`. The current comparison `idx in domain_set` is case-sensitive and misses this.

### 3.4 Proposed Fix (KU-04 Verification)

**Status: VERIFIED — Simple aliasing IS sufficient, but detection must be enhanced.**

**Approach:** Enhance `collect_index_aliases()` to detect both nested conflicts and case-insensitive collisions.

**Specific changes:**

1. **Track bound indices through nesting levels** (~30 LOC):
   - Modify `_collect()` to accept a `bound_indices: set[str]` parameter (lowercase-normalized)
   - When entering a Sum/Prod, add its indices to `bound_indices` before recursing
   - Check each Sum/Prod index against BOTH `domain_set` AND `bound_indices`

   ```python
   def _collect(e: Expr, bound: set[str]) -> None:
       match e:
           case Sum(index_sets, body, condition) | Prod(index_sets, body, condition):
               for idx in index_sets:
                   idx_lower = idx.lower()
                   if idx_lower in domain_set_lower or idx_lower in bound:
                       aliases_needed.add(idx)
               # Recurse with expanded bound set
               new_bound = bound | {idx.lower() for idx in index_sets}
               if condition is not None:
                   _collect(condition, new_bound)
               _collect(body, new_bound)
           # ... other cases unchanged
   ```

2. **Normalize domain_set to lowercase** (~5 LOC):
   - Change `domain_set = set(equation_domain)` to `domain_set_lower = {d.lower() for d in equation_domain}`
   - Compare with `idx.lower() in domain_set_lower`

3. **Update `resolve_index_conflicts()` to handle nested aliases** (~20 LOC):
   - The resolution function (lines 748-868) already tracks `active_aliases` through nesting
   - Enhance it to also check inner Sum indices against outer Sum indices (not just equation domain)
   - Use case-insensitive comparison for conflict detection

**Files to modify:**
| File | Lines | Change | Est. LOC |
|------|-------|--------|----------|
| `src/emit/expr_to_gams.py` | 670-745 | Enhance `collect_index_aliases()` with nesting + case | ~30 |
| `src/emit/expr_to_gams.py` | 748-868 | Enhance `resolve_index_conflicts()` for nested aliases | ~20 |
| `tests/unit/emit/test_expr_to_gams.py` | new | Unit tests for nested/case conflicts | ~50 |

**Total estimated LOC:** ~100
**Estimated effort:** 1-2h

### 3.5 Regression Risk Assessment

**LOW risk.**

1. **Alias renaming is semantically transparent.** Replacing `sum(i, ...)` with `sum(i__, ...)` (and all references to `i` within the sum body) preserves mathematical meaning. The `__` suffix convention is already established (line 667).

2. **Detection enhancement is strictly broadening.** The fix detects MORE conflicts (nested reuse, case collisions) but doesn't change the aliasing mechanism itself.

3. **Existing models with resolved conflicts continue to work.** The fix adds new detections; it doesn't remove any. Models that already have aliases applied are unaffected.

4. **Naming collision risk is minimal.** The `__` suffix is unlikely to collide with user-defined set names. A collision guard (check `alias_name not in model_ir.sets`) can be added as a safety measure.

**Mitigation:** Test with all 4 affected models. Verify aliased output compiles without $125 errors. Run full pipeline retest.

### 3.6 Test Strategy

1. **Unit tests:** Add tests to `tests/emit/test_expr_to_gams.py` verifying:
   - Nested same-name conflict: `Sum(("i",), Sum(("i",), body))` → detects `i` as needing alias
   - Case-insensitive conflict: equation domain `("r",)`, inner `Sum(("R",), body)` → detects `R`
   - No conflict: equation domain `("i",)`, inner `Sum(("j",), body)` → no alias needed
   - Deeply nested conflict: `Sum(("i",), Sum(("j",), Sum(("i",), body)))` → detects inner `i`

2. **Integration tests:** For all 4 models (kand, prolog, spatequ, srkandw):
   - Verify MCP file compiles without $125 errors
   - Verify aliased indices correctly renamed throughout the sum body

3. **Regression test:** Full pipeline retest — verify no currently-solving model regresses.

---

## 4. Cross-Cutting Concerns

### 4.1 Implementation Order

**Recommended order:** C → G → B

Rationale:
1. **Subcategory C first** (3-5h): Highest model count (10). Changes are in `stationarity.py` which is the most complex code path — tackle it with fresh cognitive budget.
2. **Subcategory G second** (1-2h): Changes are in `expr_to_gams.py` — a different file from C, enabling clean separation. Quick win after the larger C fix.
3. **Subcategory B last** (1-2h): Simplest fix (emitter data filtering). Lowest risk. Can be done quickly even with diminished cognitive budget.

### 4.2 Regression Test Plan

After ALL three subcategories are fixed:

1. `make test` — verify no unit/integration test failures
2. Full pipeline retest — verify:
   - All 10 Subcategory C models no longer show $149 errors
   - Both Subcategory B models no longer show $170 errors
   - All 4 Subcategory G models no longer show $125 errors
   - No currently-solving model regresses (solve count ≥ baseline)
   - Parse count stable at 154/157
3. Track which fixed models reach `model_optimal` vs shift to `model_infeasible` or `path_solve_terminated` (KU-24)

### 4.3 Interaction Between Subcategories

**No interactions.** The three fixes operate on different files and different pipeline stages:
- **Subcategory C:** `src/kkt/stationarity.py` (KKT generation stage)
- **Subcategory B:** `src/emit/original_symbols.py` (data emission stage)
- **Subcategory G:** `src/emit/expr_to_gams.py` (expression emission stage)

No fix depends on or modifies code touched by another fix. They can be implemented and tested independently.

### 4.4 Budget Summary

| Subcategory | Models | Effort | LOC | Leverage |
|-------------|--------|--------|-----|----------|
| C (uncontrolled sets) | 10 | 3-5h | ~110 | 2.0-3.3 models/h |
| G (set index reuse) | 4 | 1-2h | ~100 | 2.0-4.0 models/h |
| B (domain violations) | 2 | 1-2h | ~70 | 1.0-2.0 models/h |
| **Total** | **16** | **5-9h** | **~280** | **1.8-3.2 models/h** |

---

## 5. Known Unknown Verification Results

### KU-02: Subcategory C Fix Regression Risk

**Status:** VERIFIED — LOW REGRESSION RISK

**Finding:** The Subcategory C fix is additive — it enhances the existing `_collect_free_indices()` + Sum-wrapping logic to catch cases it currently misses. The fix does NOT modify the core stationarity equation derivation or change behavior for models where all indices are already controlled.

**Evidence:**
1. The `if uncontrolled:` guard (stationarity.py:1757, 1781) ensures Sum wrapping only activates when free indices are detected. Currently-solving models have no uncontrolled indices (GAMS would raise $149).
2. `_collect_free_indices()` tracks bound indices from enclosing Sum/Prod nodes (line 1576) — it cannot produce false positives for controlled indices.
3. Existing test coverage in `tests/kkt/test_stationarity.py` covers the stationarity generation path.
4. Full pipeline regression test (Section 4.2) will verify no regressions.

**Action:** Implement with confidence. Full pipeline retest is sufficient mitigation.

### KU-04: Subcategory G Set Index Reuse — Aliasing Sufficient?

**Status:** VERIFIED — ALIASING IS SUFFICIENT (with enhanced detection)

**Finding:** The existing `resolve_index_conflicts()` mechanism in `expr_to_gams.py` (lines 748-868) correctly renames conflicting indices and updates all references within the sum body. The mechanism is sound — the issue is that `collect_index_aliases()` fails to **detect** two conflict patterns: nested same-name reuse and case-insensitive collisions.

**Evidence:**
1. The `resolve_index_conflicts()` function already handles alias propagation through nested expressions, tracking `active_aliases` through recursion (line 781). It correctly substitutes in VarRef (line 823), ParamRef (line 833), MultiplierRef (line 846), and EquationRef (line 853) indices.
2. The `__` suffix naming convention (line 667) is unique enough to avoid collisions with user-defined identifiers.
3. The fix enhances detection (what gets aliased) without changing the aliasing mechanism (how aliases are applied).
4. All 4 affected models exhibit the two identified patterns — no third pattern was found.

**Action:** Enhance detection in `collect_index_aliases()` and `resolve_index_conflicts()`. The existing aliasing mechanism handles the resolution correctly once conflicts are detected.

---

## Appendix: Representative Error Examples

### Subcategory C Example (dyncge)

```
*** Error 149 in stat_pf(f) :
  Set "s" is not controlled by any index
```

The stationarity equation `stat_pf(f)` has domain `(f)` but the derivative contains `s` from an inner sum in the original constraint. The Issue #670 logic should wrap `s` in a Sum but fails to detect it.

### Subcategory B Example (cesam)

```
*** Error 170 in /data/ for parameter p(i,j) :
  Domain violation for element "x" in index position 1
```

The parameter `p` is declared over domain `(i,j)` but the emitted data block includes an entry with element `"x"` which is not a member of set `i`.

### Subcategory G Example (spatequ)

```
*** Error 125 in stat_... :
  Set "cc" is used in a nested fashion
```

The stationarity equation contains `sum(cc, ... sum(cc, ...) ...)` where the inner `cc` shadows the outer `cc`. GAMS requires unique index names at each nesting level.

### Subcategory G Example (kand — case collision)

```
*** Error 125 in stat_x(r,c) :
  Set "R" is used in a nested fashion
```

The equation domain uses `(r,c)` but the KKT-generated derivative contains `sum((R,C), ...)`. GAMS treats `R` and `r` as the same identifier.

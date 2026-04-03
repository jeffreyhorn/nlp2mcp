# Alias Differentiation Architecture V2

**Created:** 2026-04-03
**Sprint:** 24 (Prep Task 3)
**Predecessor:** `docs/planning/EPIC_4/SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md`

---

## Executive Summary

**Key Finding: The core alias differentiation architecture is already implemented.** Sprint 23 PRs #1135/#1136 implemented the `bound_indices` parameter threading, `_alias_match()` helper, and `_same_root_set()` resolver across the entire derivative chain. The mechanism is wired from `differentiate_expr()` through `_diff_sum()`, `_diff_varref()`, and `_partial_collapse_sum()`.

Sprint 24's alias differentiation work should focus on:
1. **Verifying** the existing implementation against all 12 issues
2. **Debugging** why the implementation doesn't resolve all Pattern A issues (the mechanism exists but may have edge cases)
3. **Extending** for Pattern C (offset-alias, may need `IndexOffset.base` extraction improvements)
4. **Investigating** Patterns B and D post-implementation

---

## Architecture Status

### Already Implemented (Sprint 23)

| Component | File | Status |
|-----------|------|--------|
| `bound_indices` parameter | `src/ad/derivative_rules.py:74` | Implemented as keyword-only `frozenset[str]` |
| Threading through all diff functions | `src/ad/derivative_rules.py:138-168` | All diff handlers (10 primary + specialized) receive `bound_indices` |
| `_same_root_set()` | `src/ad/derivative_rules.py:238-255` | Implemented with cycle detection |
| `_alias_match()` | `src/ad/derivative_rules.py:258-312` | Implemented with bound-index guard |
| `_diff_sum()` bound augmentation | `src/ad/derivative_rules.py:1946-1948` | Augments `bound_indices` with sum's `index_sets` |
| `_diff_varref()` alias check | `src/ad/derivative_rules.py:395-410` | Calls `_alias_match()` when exact match fails |
| `_partial_collapse_sum()` alias matching | `src/ad/derivative_rules.py:2093-2250` | Uses `_same_root_set()` for index matching |

### Needs Investigation/Extension

| Component | Pattern | Issue |
|-----------|---------|-------|
| Edge cases in `_alias_match()` for concrete indices | A | Why do Pattern A models still mismatch? |
| `IndexOffset.base` extraction in alias context | C | polygon/himmel16 offset-alias interaction |
| Multi-level alias nesting | B | kand tree structure |
| Condition-scope alias interaction | D | launch dollar-conditional scoping |

---

## Per-Pattern Design

### Pattern A: Summation Index Not Tracked (6 issues)

**Current State:** The mechanism exists but Pattern A models (#1137-#1140, #1145, #1150) still show gradient mismatches.

**Investigation Strategy:**
1. For qabel (simplest Pattern A model), trace the derivative computation step-by-step:
   ```python
   # In _diff_varref, add debug logging:
   # print(f"_diff_varref: expr={expr.name}{expr.indices} wrt={wrt_var}{wrt_indices}")
   # print(f"  exact_match={_indices_match(...)}")
   # print(f"  alias_match={_alias_match(...)}")
   # print(f"  bound_indices={bound_indices}")
   ```
2. Check if the issue is:
   - `_alias_match()` returning `None` when it should return a guard (false negative)
   - `_partial_collapse_sum()` not enumerating all valid matchings
   - `bound_indices` being over-inclusive (marking free aliases as bound)
   - Index normalization issues (case sensitivity, quote handling)

**Likely Root Cause:** The `_diff_sum()` adds ALL sum index_sets to `bound_indices`, but some of those may be the differentiation target's own indices. When differentiating `sum((k,n,np), f(x(n,k), x(np,k)))` w.r.t. `x(n,k)`:
- `bound_indices` = `{k, n, np}` (all sum variables)
- When checking `x(np,k)` against `x(n,k)`:
  - `np` is in `bound_indices` → `_alias_match` returns `None`
  - This is **correct for independent iteration** but **wrong when we're differentiating the full sum**

**Fix Approach:** The partial collapse logic should handle this — `_partial_collapse_sum()` substitutes the wrt_indices for the matching sum variables and then differentiates the body with the remaining indices still bound. Verify this path is executing correctly.

### Pattern C: Offset + Alias Interaction (2 issues)

**Current State:** `_alias_match()` handles `IndexOffset` via structural equality only (line ~268):
```python
if isinstance(expr_idx, IndexOffset) or isinstance(wrt_idx, IndexOffset):
    if expr_idx == wrt_idx:
        continue  # Structurally identical
    return None  # Different offsets
```

**Issue:** For polygon, the stationarity equations have concrete element offsets (`i1+1`) instead of symbolic offsets (`i+1`). The `_apply_offset_substitution()` in stationarity.py should convert these, but may not be handling the alias case.

**Fix Approach:**
1. Check if `_apply_offset_substitution()` runs before or after alias resolution
2. If concrete offsets persist, add `IndexOffset.base` extraction to `_alias_match()`:
   ```python
   if isinstance(expr_idx, IndexOffset) and isinstance(wrt_idx, str):
       # Check if offset base aliases wrt
       if _same_root_set(expr_idx.base, wrt_idx, aliases):
           # Generate offset-aware guard
           ...
   ```

### Pattern B: Root-Set Mapping (1 issue — kand)

**Investigation:** Run kand through the pipeline with debug logging in `_alias_match()` to identify where the tree structure causes failures. May need enhancement to `_same_root_set()` for multi-level alias chains.

### Pattern D: Condition-Scope (1 issue — launch)

**Investigation:** Check if dollar-conditional derivatives properly scope alias resolution. The `_diff_dollar_conditional()` function passes `bound_indices` through, but the condition expression may introduce alias scope that's not tracked.

---

## Regression Test Plan

### Canary Test (Must Pass First)
- **dispatch:** `Alias(i,j); sum((i,j), p(i)*b(i,j)*p(j))` — bound_indices prevents `j` from matching `i`
- Run before any other testing

### Golden-File Tests (49 Matching Models)

**Prerequisite:** Ensure raw GAMS models are available locally (`data/gamslib/raw/*.gms` is gitignored; download via `scripts/gamslib/download_models.py` if not present).

Generate and store stationarity equations before any changes:
```bash
for model in $(python -c "
import json
with open('data/gamslib/gamslib_status.json') as f:
    data = json.load(f)
for m in sorted(data.get('models', []), key=lambda x: x.get('model_id', '')):
    if m.get('solution_comparison', {}).get('comparison_status') == 'match':
        print(m.get('model_id', ''))
"); do
    python -m src.cli data/gamslib/raw/$model.gms -o /tmp/golden_${model}_mcp.gms --skip-convexity-check 2>/dev/null
done
```

After changes, compare:
```bash
for model in ...; do
    python -m src.cli data/gamslib/raw/$model.gms -o /tmp/new_${model}_mcp.gms --skip-convexity-check 2>/dev/null
    diff /tmp/golden_${model}_mcp.gms /tmp/new_${model}_mcp.gms || echo "CHANGED: $model"
done
```

### Per-Pattern Tests

| Pattern | Test Models | Expected Outcome |
|---------|-------------|------------------|
| A | qabel, irscge, meanvar | Gradient mismatch reduced or eliminated |
| B | kand | Investigate; may not change |
| C | polygon, himmel16 | Offset-alias handling improved |
| D | launch | Investigate; may not change |
| E | catmix, camshape | No change expected (separate bugs) |

### Full Pipeline
- Run `scripts/gamslib/run_full_test.py --quiet` after all changes
- Compare solve/match counts against baseline

---

## Rollout Strategy: Incremental

**Recommendation: Incremental rollout, Pattern A first.**

**Phase 1 (Days 1-3):** Debug Pattern A
- Add logging to `_diff_varref` and `_partial_collapse_sum`
- Trace qabel derivative computation end-to-end
- Identify and fix the specific edge case preventing correct alias matching
- Run dispatch canary + qabel validation

**Phase 2 (Days 3-5):** Validate Pattern A across all models
- Test all Pattern A models (CGE, meanvar, PS-family, cclinpts)
- Run golden-file regression on all 49 matching models
- Checkpoint 1 decision: proceed to Patterns B/C or investigate Pattern A further

**Phase 3 (Days 5-7):** Address Pattern C (offset-alias)
- Enhance `_alias_match()` for `IndexOffset.base` extraction if needed
- Test polygon and himmel16
- Run full pipeline regression

**Phase 4 (Days 7-9):** Post-investigation for Patterns B/D
- Debug kand (Pattern B) with logging
- Debug launch (Pattern D) with logging
- File issues for any remaining edge cases

**Decision Criteria for Each Phase:**
- Proceed if regression count = 0 (no matching models lost)
- Proceed if at least 2 models improve per phase
- Stop and investigate if any regression detected

---

## Effort Estimate

| Activity | Estimated Hours | Notes |
|----------|----------------|-------|
| Debug Pattern A (trace + fix edge case) | 4-6h | Main implementation work |
| Validate Pattern A across all models | 2-3h | Testing + golden-file comparison |
| Pattern C offset-alias extension | 2-3h | May be included in Pattern A fix |
| Pattern B/D investigation | 2-3h | Post-implementation debugging |
| Full pipeline regression | 1-2h | ~75 min for full run |
| **Total** | **11-17h** | Within PROJECT_PLAN 14-18h estimate |

**KU-26 Assessment:** The 14-18h estimate from PROJECT_PLAN is reasonable. The architecture is already implemented — Sprint 24 effort is debugging/extending, not building from scratch. **Estimate VERIFIED.**

---

## Files to Modify

| File | Changes | Risk |
|------|---------|------|
| `src/ad/derivative_rules.py` | Debug logging, edge case fixes in `_alias_match`/`_partial_collapse_sum` | MEDIUM — core AD |
| `src/kkt/stationarity.py` | Possible `_apply_offset_substitution` enhancement for Pattern C | LOW — localized |
| `tests/unit/ad/` | New regression tests for alias patterns | NONE — test-only |

---

## Key Insight

The Sprint 23 design was fully implemented but the 12 issues persist. This means the implementation has edge cases or the root cause is subtler than expected. Sprint 24's primary task is **debugging the existing implementation**, not designing a new architecture. The design is sound — the implementation needs targeted fixes.

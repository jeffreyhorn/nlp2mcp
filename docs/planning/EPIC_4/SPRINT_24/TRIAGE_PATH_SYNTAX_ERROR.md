# path_syntax_error Triage — Sprint 24

**Created:** 2026-04-03
**Sprint:** 24 (Prep Task 4)
**Models Analyzed:** 24

---

## Executive Summary

24 models currently fail with path_syntax_error (up from 20 in Sprint 23 baseline). 11 new models entered the category (from translate recovery/pipeline changes), while 8 were resolved. A major new subcategory (H: concrete element offsets) affects 8 models and is the highest-priority fix target. 15 of 24 models (62.5%) use aliases, confirming significant overlap with alias differentiation (Priority 1).

**Target:** Reduce from 24 to ≤ 15 (fix at least 9 models).

---

## Subcategory Classification

| Subcategory | Count | Models | Root Cause | Fix Effort |
|---|---|---|---|---|
| **A** (Missing Data) | 9 | china, decomp, dinam, harker, indus, ramsey, sample, saras, worst | Parameters/subsets not initialized ($140/$141) | 2-3h per model |
| **A+** (Complex Missing) | 2 | cclinpts, lmp2 | Missing data + alias/condition interactions | 3-4h per model |
| **B** (Domain Violation) | 1 | otpop | Alias-as-subset condition ($171) | 2-3h |
| **C** (Dynamic Sets) | 2 | clearlak, turkey | Uninitialized dynamic subsets ($352/$149) | 3-4h per model |
| **G** (Index Reuse) | 1 | prolog | Set index reuse (possible regression) | 2h |
| **H** (Concrete Offsets) | 8 | catmix, ferts, ganges, gangesx, partssupply, polygon, tricp, turkpow | Set(index±const) not handled ($171+) | 4-6h (batch fix) |
| **T** (Translate Fail) | 1 | feedtray | LhsConditionalAssign not in IR | 3-4h |

---

## Alias Overlap Analysis

| Model | Has Aliases? | Alias Differentiation Overlap? |
|---|---|---|
| catmix | Yes | Yes — Pattern E (non-diff bug) |
| cclinpts | Yes | Yes — Pattern A (summation index) |
| china | Yes | Possible |
| clearlak | No | No |
| decomp | No | No |
| dinam | Yes | Possible |
| feedtray | No | No |
| ferts | Yes | Yes — offset+alias |
| ganges | Yes | Yes — offset+alias |
| gangesx | Yes | Yes — offset+alias |
| harker | Yes | Possible |
| indus | Yes | Possible |
| lmp2 | Yes | Possible |
| otpop | Yes | Yes — domain violation |
| partssupply | Yes | Yes — offset+alias |
| polygon | Yes | Yes — Pattern C (offset-alias) |
| prolog | Yes | Possible |
| ramsey | No | No |
| sample | No | No |
| saras | Yes | Possible |
| tricp | Yes | Yes — offset+alias |
| turkey | Yes | Possible |
| turkpow | Yes | Yes — offset+alias |
| worst | No | No |

**15 of 24 models use aliases (62.5%).** All 8 subcategory H models have aliases.

---

## Priority Ranking for ≤ 15 Target

### Tier 1: Subcategory H — Concrete Offsets (8 models, batch fix)
**Estimated effort:** 4-6h (single architectural fix)
**Models:** catmix, ferts, ganges, gangesx, partssupply, polygon, tricp, turkpow

These all share the same root cause: set membership with index offsets (e.g., `nh(i+1)`) not properly handled in the stationarity builder/emitter. A single fix to handle `IndexOffset` in set domain contexts would recover all 8.

### Tier 2: Subcategory A — Quick Data Fixes (select 2-3)
**Estimated effort:** 2-3h per model
**Best candidates:** decomp (137 lines, simple), ramsey (129 lines, simple), worst (124 lines, simple)

Small models with straightforward missing data initialization. Fix 2-3 to reach the ≤ 15 target.

### Tier 3: Other (lower priority)
- prolog (G): Investigate regression — may be quick fix
- otpop (B): Domain violation — investigated in Sprint 23
- clearlak (C): Dynamic sets — complex
- feedtray (T): Translate fail — needs IR extension

---

## Sprint 23 Changes

**Resolved since Sprint 23 baseline (7 models):**
- camcge, cesam2, chenery, hhfair, nonsharp, shale, srkandw

**Note:** china was partially improved but still fails (subcategory A).

**New since Sprint 23 baseline (11+ models):**
- catmix, cclinpts, ferts, ganges, gangesx, lmp2, partssupply, polygon, tricp, turkey, turkpow

Most new entries are from translate recovery — models that now successfully translate but have compilation errors in the generated MCP.

---

## Recommendations

1. **Fix Subcategory H first** (8 models, single architectural fix) — highest leverage
2. **Fix 1-2 Subcategory A models** (decomp, ramsey, or worst) — small/simple
3. **Investigate prolog regression** — may be quick fix
4. **Total target:** 9-11 models fixed → 24 - 11 = 13 (below ≤ 15 target)
5. **Alias differentiation (Priority 1) may automatically fix some** — monitor during implementation

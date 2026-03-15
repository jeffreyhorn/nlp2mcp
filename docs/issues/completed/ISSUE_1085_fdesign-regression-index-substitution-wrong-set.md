# fdesign: Regression — Index Substitution Maps to Wrong Set

**GitHub Issue:** [#1085](https://github.com/jeffreyhorn/nlp2mcp/issues/1085)
**Status:** FIXED
**Severity:** High — model_optimal/match regressed to path_solve_terminated
**Fix:** Keep sum dollar conditions symbolic (using sum index names, not substituted concrete values) in all three collapse paths of `derivative_rules.py` (`_diff_sum` direct, partial index match, and `_partial_collapse_sum`). This avoids ambiguity when `_replace_indices_in_expr` maps elements back to set names. Now fdesign translates, solves to optimal, and matches.
**Date:** 2026-03-14
**Affected Models:** fdesign
**Regressing PR:** #1083 (Sprint 22 Day 9)

---

## Problem Summary

The fdesign model (GAMSlib SEQ=379, minimax linear phase lowpass FIR filter) regressed from
model_optimal (match) to path_solve_terminated after PR #1083 changed how
`_apply_index_substitution` handles `SymbolRef` nodes and how `_ensure_numeric_condition`
wraps conditions.

The generated MCP has 324 equations vs 322 variables (2 unmatched), causing GAMS to abort
before solving.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/fdesign.gms -o /tmp/fdesign_mcp.gms
gams /tmp/fdesign_mcp.gms lo=2
# **** MCP pair comp_stopband_bnds.lam_stopband_bnds has unmatched equation
#      comp_stopband_bnds(179)
# **** MCP pair comp_stopband_bnds2.lam_stopband_bnds2 has unmatched equation
#      comp_stopband_bnds2(179)
# SINGLE EQUATIONS 324, SINGLE VARIABLES 322
# **** SOLVE ABORTED, EXECERROR = 2
```

---

## Root Cause

### Model Structure

fdesign has sets `i / 0*179 /` (180 points) and `k / 0*10 /` (11 filter taps). Elements
`'0'`-`'10'` appear in **both** sets. The constraint body uses:
```gams
sum(k$[ord(k) < card(k)], h(k)*cosomega(i,k))
```

### The Bug

When differentiating `sum(k$[ord(k) < card(k)], h(k)*...)` w.r.t. `h('0')`, the sum
collapses and index `k` is substituted with concrete value `'0'`. PR #1083 made two changes:

1. **`_apply_index_substitution` now substitutes SymbolRef**: `SymbolRef("k")` inside
   `ord(k)` becomes `SymbolRef("0")`
2. **`_ensure_numeric_condition` wraps all non-Const conditions**: The condition becomes
   `1$(ord('0') < card('0'))`

Then `_replace_indices_in_expr` maps `SymbolRef("0")` back to a symbolic set name. Since
`"0"` is a member of both `i` (180 elements) and `k` (11 elements), it resolves `"0"` → `"i"`
instead of `"0"` → `"k"`, producing:

**Before PR #1083 (correct):**
```gams
stat_h(k)$(ord(k) < card(k)).. sum(i, (... * (ord(k) < card(k)) * lam_...)$omega_pass(i))
```

**After PR #1083 (broken):**
```gams
stat_h(k)$(ord(k) < card(k)).. sum(i, (... * 1$(ord(i) < card(i)) * lam_...)$(omega_pass(i)))
```

### Impact

`ord(i) < card(i)` evaluates to False when `i='179'` (the last element). This zeros out
the coefficient of `lam_stopband_bnds('179')` in ALL stationarity equations. GAMS removes
the variable as empty, leaving 2 unmatched equations.

---

## Suggested Fix

**Option A (Recommended):** When a sum collapses during differentiation, preserve the
original symbolic index in the dollar condition when the collapsed sum index coincides with
the stationarity equation's domain index. Skip substitution on `expr.condition` (line
1918-1921 of `derivative_rules.py`) when the matched sum indices are the same as the
outer equation domain.

**Option B:** In `_replace_indices_in_expr`, when processing `Call("ord", (SymbolRef("0"),))`
or `Call("card", ...)`, use context to determine which set the element belongs to (the
sum's collapsed index set `k`, not arbitrary set `i`).

**Option C:** Revert `_apply_index_substitution` changes for SymbolRef inside `ord()`/`card()`
function calls.

---

## Files to Modify

| File | Change |
|------|--------|
| `src/ad/derivative_rules.py:1918-1921` | Skip condition substitution when sum index = equation domain index |
| `src/ad/derivative_rules.py:2114-2121` | (Option C) Revert SymbolRef substitution in function call arguments |
| `src/kkt/stationarity.py` | (Option B) Pass context about which set an element belongs to |

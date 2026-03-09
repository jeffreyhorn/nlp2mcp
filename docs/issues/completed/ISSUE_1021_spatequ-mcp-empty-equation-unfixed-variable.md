# spatequ: MCP Empty Equation with Unfixed Paired Variable

**GitHub Issue:** [#1021](https://github.com/jeffreyhorn/nlp2mcp/issues/1021)
**Status:** FIXED
**Severity:** High — 12 execution errors, solve aborted
**Date:** 2026-03-08
**Fixed:** 2026-03-09
**Affected Models:** spatequ

---

## Problem Summary

The spatequ model (spatial price equilibrium) translates to MCP without compilation errors, but GAMS reports 12 execution errors at solve time: "MCP pair has empty equation but associated variable is NOT fixed." The equations `comp_DOM_TRAD(r,rr,c)` and `comp_PDIF(r,rr,c)` are trivially satisfied (reduce to `0 >= 0`) when `r = rr` because `TCost(r,r,c) = 0` (no trade cost for same-region pairs). The MCP solver requires that variables paired with empty equations be fixed to zero.

---

## Fix Details

Three changes were made to fix this issue:

### 1. Parser: Fix repeated-index expansion in `_expand_variable_indices` (`src/ir/parser.py`)

The parser's `_expand_variable_indices` incorrectly computed the full Cartesian product for `X.fx(r,r,c) = 0`, producing 18 entries (3×3×2) instead of 6 diagonal entries. In GAMS, when the same index variable `r` appears in multiple positions, it acts as a single running index — only diagonal entries are assigned.

**Fix:** Track which positions share the same set-name symbol and filter the Cartesian product to keep only entries where repeated positions have matching values.

### 2. Emitter: Re-emit numeric `.fx_map` entries (`src/emit/emit_gams.py`)

The emitter only handled expression-based bounds (`.fx_expr`, `.fx_expr_map`) but dropped numeric per-element `.fx_map` entries from the original model. This meant `X.fx(r,r,c) = 0` was parsed but never re-emitted in the generated MCP file.

**Fix:** Added emission of numeric `fx_map` entries as `.fx` statements in the Variable Bounds section.

### 3. Emitter: Enhanced diagonal trivial-equation detection (`src/emit/emit_gams.py`)

Section 2c's trivial-equation check only detected two simple patterns: `LHS == RHS` and `Binary("-", A, A)` where `A == A`. For spatequ, the diagonal substitution produces `p(r,c) + TCost(r,r,c) - p(r,c) >= 0` where VarRef terms cancel but the remaining ParamRef term isn't detected as trivial.

**Fix:** Added `_collect_additive_terms()` and `_is_trivial_after_cancellation()` helper functions that flatten an expression into signed additive terms, cancel matching VarRef pairs, and check if only ParamRef/Const terms remain. This correctly detects the spatequ pattern and emits `lam_DOM_TRAD.fx(r,rr,c)$(ord(r) = ord(rr)) = 0` and `lam_PDIF.fx(r,rr,c)$(ord(r) = ord(rr)) = 0`.

### Result

- All 12 execution errors eliminated
- GAMS exits with code 0 (no execution errors)
- Model solves but reports Model Status 5 (Locally Infeasible) — see Issue #1026 for the residual infeasibility from overconstrained KKT system

---

## Files Changed

| File | Change |
|------|--------|
| `src/ir/parser.py` | Fixed `_expand_variable_indices` to handle repeated set-name symbols (diagonal only) |
| `src/emit/emit_gams.py` | Added numeric `fx_map` emission; added `_collect_additive_terms` and `_is_trivial_after_cancellation` for enhanced diagonal detection |

---

## Related Issues

- Issue #1026: spatequ KKT overconstrained — model infeasible (residual issue)
- Issue #942: Diagonal trivial equation detection (original section 2c implementation)

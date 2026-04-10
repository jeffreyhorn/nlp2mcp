# robustlp: Model Infeasible — Diagonal Parameter Expansion Bug

**GitHub Issue:** [#1105](https://github.com/jeffreyhorn/nlp2mcp/issues/1105)
**Status:** PARTIALLY FIXED (primary bug resolved, secondary PATH convergence remains)
**Model:** robustlp (GAMSlib SEQ=318)
**Error category:** `model_infeasible` → `path_solve_terminated` (after fix)
**MCP solve status:** MODEL STATUS 5 (Locally Infeasible) — from PATH cold-start difficulty

## Description

The robustlp model (Robust Linear Programming as SOCP) translates to MCP but solves as model_infeasible. Two issues: (1) a parser bug expanding diagonal parameter assignments to all combinations, and (2) PATH solver convergence from cold start.

## Primary Fix: Diagonal Parameter Expansion (RESOLVED)

**Root cause:** `src/ir/parser.py` (lines ~4471-4489) domain-over parameter expansion built a full Cartesian product without checking for repeated index symbols. `P(i,j,j)` expanded to 112 entries (7*4*4) instead of 28 diagonal entries (7*4).

**Fix applied:** Ported the diagonal constraint logic from `_handle_variable_bounds_assignment` (Issue #1021, lines 6596-6718) to the parameter expansion code. Added `symbol_positions` tracking to detect repeated index symbols, then filtered the Cartesian product so linked positions share the same value.

**File changed:** `src/ir/parser.py` (lines ~4471-4510)
- Track `symbol_positions` for expanding positions with same index name
- Detect `repeated_groups` (positions sharing the same symbol)
- Build slot-based mapping to link repeated positions
- Generate only diagonal combinations via projected Cartesian product

**Verification:**
- Before fix: `P` had 112 entries (all combinations)
- After fix: `P` has 28 entries (only diagonal where 2nd and 3rd indices are equal)
- Zero off-diagonal entries confirmed

## Secondary Issue: PATH Convergence from Cold Start (REMAINING)

Even with the corrected diagonal P matrix, PATH returns MODEL STATUS 5 (Locally Infeasible, obj=-1.662) from default initialization. The NLP reference objective is -2.33.

The SOCP complementarity structure creates a nonlinear landscape that PATH struggles to navigate from zero initialization. Warm-starting from the QCP solution produces MODEL STATUS 1 (Optimal).

This is a known `path_solve_terminated` category issue requiring warm-start infrastructure (deferred).

## Sprint 24 Retest

Retested after accumulated Sprint 24 fixes. No change — PATH still returns
MODEL STATUS 5 (Locally Infeasible) with 12 infeasible rows, 4285 iterations.
The cold-start convergence issue is not affected by KKT/stationarity fixes.

**NOT FIXED** — warm-start infrastructure required (deferred).

## Related Issues

- #1021: Variable bounds diagonal expansion fix (same pattern, already resolved — ported from)
- #938: Previous robustlp issue was digamma derivative (RESOLVED)

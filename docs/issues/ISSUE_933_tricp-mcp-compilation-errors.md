# tricp: Translation Timeout — Triangular Graph Circle Packing

**GitHub Issue:** [#933](https://github.com/jeffreyhorn/nlp2mcp/issues/933)
**Status:** OPEN — **re-scoped 2026-10-14** (Sprint 40 Prep Task 7): the compile errors below no longer reproduce; tricp now compiles, reaches PATH and is a `case_b` emit bug. See *Current Status (2026-10-14)* at the end.
**Severity:** Medium — Model parses but translation times out (>60s)
**Date:** 2026-02-26
**Affected Models:** tricp
**Sprint:** 21 (Day 11 triage)

---

## Problem Summary

The `tricp.gms` model (GAMSlib SEQ=378, "Triangular Graph Circle Packing") parses successfully but times out during KKT translation (>60s). This is a QCP (Quadratically Constrained Program) with nonlinear constraints.

---

## Model Details

| Property | Value |
|----------|-------|
| GAMSlib SEQ | 378 |
| Solve Type | QCP |
| Convexity | likely_convex |
| Reference Objective | 3838.2686 |
| Parse Status | success (~1.5s) |
| Translate Status | timeout (>60s) |
| Variables | 6 |
| Equations | 3 |
| Sets | 3 |
| Parameters | 6 |

### Key Variables

| Variable | Domain |
|----------|--------|
| x | (n,k) |
| r | (n) |
| slp | (n,n) |
| sln | (n,n) |
| z | — |
| obj | — |

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/tricp.gms -o /tmp/tricp_mcp.gms
# Or:
python scripts/gamslib/run_full_test.py --model tricp --only-translate --verbose
```

---

## Root Cause

Despite having only 6 variables and 3 equations, the model uses dense 2-dimensional variables `slp(n,n)` and `sln(n,n)` over a potentially large set `n`. The QCP equations contain quadratic terms requiring genuine symbolic differentiation. The Jacobian computation generates too many entries for the variable instance × equation instance pairs to complete within 60 seconds.

---

## Possible Fixes

| Approach | Impact | Effort |
|----------|--------|--------|
| Sparsity-aware Jacobian (only compute interacting variable/equation pairs) | High | High |
| Increase timeout limit | Low — may succeed if set `n` is moderate | Trivial |
| Variable instance threshold with early abort | Low | Low |

---

## Related Issues

- #885 (sarf): Same timeout pattern
- dinam, egypt, ferts, ganges, gangesx, iswnm, nebrazil: Same timeout category

---

## Current Status (2026-03-29)

**Translation timeout: FIXED** (with increased 300s timeout). Translation now completes at ~135s.

**Current blocker: MCP compilation errors (10 errors)**
- $148 Dimension mismatch (2 occurrences)
- $149 Uncontrolled set entered as constant (6 occurrences)
- $141/$257 cascading from above

These are index domain errors in the generated MCP, likely related to equation index domains not being properly propagated.

Parse: fast | Translate: ~135s | Compile: FAIL | Solve: N/A

## Investigation (2026-04-01)

The compilation errors stem from three distinct issues in the stationarity builder:

1. **$148 on `stat_r(n)`**: `nu_eq1(n)` and `lam_eq2(n)` — dimension mismatch. These multipliers are declared over `(n,n)` (from `eq1(e(i,j))` and `eq2(n,n)`) but referenced with single index `(n)` in the stationarity equation. The stationarity builder incorrectly collapses a 2D multiplier to 1D.

2. **$149 on `stat_sln(n,n)` and `stat_slp(n,n)`**: `$(e(n,i))` — uncontrolled `i`. The condition from the original equation `eq1(e(i,j))` uses index variables `i,j` which are not controlled in the stationarity equation domain `(n,n)`. The condition should be remapped to use the stationarity domain variables.

3. **$149 on `.fx` statements**: Same uncontrolled `i` issue — `sln.fx(n,n)$(not (e(n,i))) = 0` should remap the condition indices to the stationarity domain (e.g., using distinct alias indices for the two `n` positions).

**Fix requires:** The stationarity builder's condition propagation needs to remap equation domain indices (`i,j` from `eq1(e(i,j))`) to the stationarity equation domain (`n,n` from `stat_slp(n,n)`).

## Current Status (2026-10-14) — Sprint 40 Prep Task 7, licensed

Triaged against a real compile, in a throwaway worktree under the retention patch (`docs/planning/EPIC_4/SPRINT_40/COHORT_DRY_RUN.md`):

- **Translate:** 3.7 s. The committed golden is **byte-identical** to a HEAD re-emit and carries the Sprint 38 Day 11 repeated-domain fix (`slp(n,n)`).
- **Compile: clean.** The run's own listing has **0** compile-error markers. None of the 2026-04-01 errors (`$148` ×2, `$149` ×6, `$141`/`$257`) reproduce.
- **Solve:** PATH runs. The cold MCP is `model_infeasible` (MS 5); the `--nlp-presolve` retry is also MS 5.
- **`kkt_residual.py`: `case_b` (emit bug).** The worst stationarity row is `stat_x(n1,k0)`, relative residual 1.69, with the same value at every `n`. ⚠ The dual-transfer self-check reports a max equality residual of 6.15e6 while marked consistent; check that first.

**Re-scoped:** the open defect is no longer compilation. It is a **wrong stationarity equation for `x(n,k)`**, routed to Sprint 40 P2 as routing note **R-B-tricp**. The title and the Sprint-21 sections above describe history.


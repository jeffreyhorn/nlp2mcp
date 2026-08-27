# elec: MCP PATH Convergence Failure (non-convex)

**GitHub Issue:** [#983](https://github.com/jeffreyhorn/nlp2mcp/issues/983)
**Status:** ✅ **RESOLVED (2026-08-26)** — Sprint 38 Day 12, PR #1704, main `31340922`, together with **#1325**
**⚠ The former status line — "Not fixable (non-convex model, PATH convergence issue)" — was WRONG.** It was an emit defect all along: two of them, in the AD layer and in the KKT re-symbolization. This document's *"Why Division-by-Zero No Longer Occurs"* section was also wrong and stayed wrong for four sprints; both are corrected in *Resolution — Sprint 38 Day 12* below.
**Severity:** Low — MCP generates correctly; solver cannot converge
**Date:** 2026-03-03
**Last Updated:** 2026-03-17
**Affected Models:** elec

---

## Problem Summary

The elec model (electrons on a sphere, GAMSlib SEQ=230) parses and translates to MCP
successfully. The original issue described division-by-zero errors, but this has been
resolved — the `$(ut(i,j))` set membership condition IS correctly preserved in the
stationarity equations, filtering out self-pairs.

The remaining issue is that PATH terminates with MODEL STATUS 6 (Intermediate Infeasible).
This is a non-convex model (25 electrons, 75 variables, 25 quadratic ball constraints)
where the KKT system has multiple solutions and PATH cannot converge from the given
initial point.

---

## Current Status (2026-03-17)

- **Translation**: Success — MCP file generates without errors
- **GAMS compilation**: Success — no compilation or execution errors
- **PATH solve**: MODEL STATUS 6 (Intermediate Infeasible), SOLVER STATUS 4 (Terminated by Solver)
- **Stationarity equations**: `stat_x(i).. sum(j$(ut(i,j)), derivative_terms) + ... =E= 0;`
  - The `$(ut(i,j))` condition correctly excludes self-pairs
  - No division-by-zero errors occur during equation generation
- **Large INFES values**: PATH shows massive infeasibilities in all stationarity equations
  (INFES values ranging from 3 to 391), indicating the KKT system solution is unreachable

---

## Why Division-by-Zero No Longer Occurs

The original issue doc stated that `$(ut(i,j))` filtering was lost during differentiation.
This was incorrect — the parser correctly converts `sum{ut(i,j), body}` into
`Sum((i,j), body, condition=SetMembershipTest("ut", (i,j)))`, and the AD engine preserves
the condition through differentiation. The emitted stationarity equations contain
`sum(j$(ut(i,j)), ...)` as expected.

---

## Root Cause of PATH Failure

The elec model is **strongly non-convex**:
- The objective `sum(ut, 1/distance)` is non-convex (reciprocal of Euclidean distance)
- The ball constraints `sqr(x) + sqr(y) + sqr(z) = 1` are nonlinear equalities
- The KKT system has many local solutions (one for each local minimum of the NLP)
- PATH's initial point (random uniform on sphere) is likely far from any KKT solution

This is the same class of issue as #757 (bearing) — non-convex NLP where the MCP is
structurally correct but PATH cannot converge.

---

## Files

- MCP file: `data/gamslib/mcp/elec_mcp.gms`
- Original GAMS model: `data/gamslib/raw/elec.gms`
- Stationarity builder: `src/kkt/stationarity.py`
- AD differentiation: `src/ad/derivative_rules.py`

## Phase 0: Acceptance Gate

**Authored:** Sprint 38 Day 2 (P7 backfill) · **Fingerprint re-reproduced at `b823a9a5`**, GAMS 54.2.1 / PATH 5.2.01.

> **⚠ THIS DOC CONTAINS A STALE CLAIM.** The section *"Why Division-by-Zero No Longer Occurs"* is **contradicted by measurement**: at `b823a9a5` the emitted `elec` MCP still aborts with
> ```
> **** Exec Error at line  99: division by zero (0)      ← stat_x
> **** Exec Error at line 100: division by zero (0)      ← stat_y
> **** Exec Error at line 101: division by zero (0)      ← stat_z
> **** SOLVE from line 133 ABORTED, EXECERROR = 3
> ```
> The division-by-zero **does** occur. That section describes a state that is no longer (or was never) true, and it should not be read as current.

### Hand-Derived KKT Shape

See **`ISSUE_1325`'s Phase-0 gate**, which is the **live specification for this defect** and carries the full derivation. In brief: the objective sums over the strictly upper-triangular pair set `ut(i,j)`, so every real term has `i ≠ j` and a strictly positive divisor. The gradient w.r.t. a point `p` is the sum over pairs where `p` is the *first* member plus the sum where it is the *second*, **each restricted to pairs containing `p`**.

### Expected Emit Pattern

Every `$(ut(...))` condition must name **its own enclosing summation index** paired with the free index. The current emit violates this twice — `ut(i,i)` (structurally empty, silently dropping half the gradient) and `ut(i,j)` guarding a `sum(i__, …)` (unconstrained, admitting `i__ = i` and hence `d = 0`). Full pattern and traced fix-surface: **`ISSUE_1325`**.

### Verification Methodology

**Identical to `ISSUE_1325`'s** — fail-before at lines 99/100/101 with `EXECERROR = 3`; structural assertion that **no `ut(i,i)` remains**; `kkt_residual.py elec` → `CASE_A`; leak gate showing only `elec` drifting, **with the in-scope count stated** (185 after P4's Day-8 adoption); determinism ×3.

**The structural and residual checks are not optional here.** This issue's own history is the reason: it was written up as resolved on the strength of the model no longer erroring, and the defect persisted. **Termination is not correctness.**

### PROCEED/REPLAN Signal

**PROCEED** — as `ISSUE_1325`: zero div-by-zero exec errors, no `ut(i,i)`, residual `CASE_A`, no collateral drift. **Closing this issue requires the same evidence**; it may not be closed on a non-erroring emit alone.

**REPLAN** — residual stays `CASE_B`, or collateral drift.

### Bucket / KPI

**0 bucket.** `elec` is `path_solve_terminated` with `solver_version: None` (aborts before PATH) and is **non-convex** — no Solve or Match gain may be projected.


---

## Resolution — Sprint 38 Day 12 (2026-08-25)

**FIXED together with #1325 — they are the same defect at different stages.** See `ISSUE_1325`'s *Resolution* section for the full record: two independent defects (`_diff_sum`'s partial-collapse condition substitution in `src/ad/derivative_rules.py`, and the self-mapped-sum-index misclassification in `_replace_indices_in_expr` in `src/kkt/stationarity.py`), both required, verified by `kkt_residual.py` reaching **`CASE_A`** and by a leak gate that drifted **exactly `elec`** of 185 in-scope goldens.

**⚠ This document's section *"Why Division-by-Zero No Longer Occurs"* was WRONG and stayed wrong for four sprints.** Division by zero reproduced at `b823a9a5` and again at `cf8c0284`, at lines 99/100/101 (`stat_x`/`stat_y`/`stat_z`). It is fixed now — but by the changes described above, not by anything that section claims. **Do not read that section as history; it was never accurate.** The lesson recorded in Sprint 38 Day 2's gate stands: *a merely non-erroring emit is not a pass* — the structural assertion (every `$(ut(...))` naming its own summation index) is what distinguishes a fix from a coincidence.

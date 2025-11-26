# Sprint 11 Plan Review

## Conformance to Task 12 Instructions
- Missing mandatory scope: Task 12 objective and acceptance criteria require maxmin.gms (100% Tier 1) in Phase 1 (Days 1-3); PLAN defers maxmin entirely, so the plan cannot satisfy the stated sprint goals.
- Checkpoint misalignment: Required checkpoints on Days 3 (maxmin), 5 (term reduction), and 7 (CI). PLAN defines checkpoints on Days 5, 8, and 10, omitting the Day 3 and Day 7 gates.
- Phase/order mismatch: Instructions call for Phase 1 maxmin (Days 1-3), Phase 2 simplification core (Days 3-5), Phase 3 simplification advanced (Days 5-7), Phase 4 CI (Days 6-8). PLAN front-loads CI (Days 1-2), delays simplification to Days 3-6, and omits maxmin entirely.
- Daily allocations deviate from guidance: Several days exceed/underrun the expected ~3-4h/day (e.g., Day 2: 5h; Days 7-8: 2-2.5h; Day 9: 4h). Acceptance criteria expect consistent daily effort.
- Success criteria drift: Sprint 11 acceptance in PREP_PLAN includes 100% Tier 1 parse rate and PATH/PATH-scope CI considerations; PLAN sets a different success set (simplification + CI + diagnostics, with maxmin/PATH deferred).
- Unknowns 6.1 and 7.1: Task 12 asked to research and decide include/defer; PLAN defers but does not surface the decision rationale or explicit updates within the schedule/checkpoints.

## Feasibility (10-day sprint, 20-30h target)
- Hours total (27.5-28.5h) fit the 20-30h target, but the mix of low-hour days and a 5h day suggests uneven load; maxmin omission removes a major 8-12h item, so feasibility is achieved by reducing scope rather than by scheduling efficiency.
- Critical path risk: With maxmin absent, the plan no longer meets the acceptance criteria; feasibility to *meet requirements* is effectively zero unless scope restored.

## Ordering and Flow
- Dependency order inverted: CI is scheduled before simplification and before any parser/maxmin work, contrary to the required phase ordering and the Day 3 checkpoint dependency on maxmin completion.
- Checkpoints are late or misplaced (first at Day 5), reducing early detection of failure on the critical maxmin item.
- Integration/validation is late relative to aggressive simplification delivery; a Day 3/Day 5 cadence was requested to gate progress.

## Recommendations to Revise PLAN.md
- Restore required scope: Re-introduce maxmin.gms as Phase 1 on Days 1-3 with Day 3 checkpoint targeting 100% Tier 1; keep simplification/CI/diagnostics as secondary phases in their instructed slots.
- Align phases and checkpoints to instructions: Day 3 (maxmin), Day 5 (≥20% term reduction on ≥3 models), Day 7 (CI workflow running). Move CI work to Days 6-8, simplification core to Days 3-5, advanced to Days 5-7.
- Normalize daily effort to ~3-4h and keep within 20-30h total without dropping required scope; rebalance oversized Day 2 (5h) and undersized Days 7-8 (2-2.5h).
- Reconcile success criteria: Explicitly include 100% Tier 1 parse rate (maxmin), CI guardrails, diagnostics, and the requested risk items (PATH/licensing). Document rationale for Unknowns 6.1/7.1 within the plan.
- Add early synthetic/integration validation tied to checkpoints (post-Day 2/Day 3 for maxmin, Day 5 for simplification effectiveness) to catch regressions sooner.

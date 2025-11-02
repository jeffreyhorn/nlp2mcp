# Sprint 4 Plan Review – Findings & Recommendations

## Findings
- **Completed unknowns still embedded in daily tasks** – Day 1–4 task lists in `docs/planning/SPRINT_4/PLAN_ORIGINAL.md` explicitly call out Unknowns 1.1, 1.2, 1.4, 1.5, 2.1, 2.2, and 6.1 even though they are marked COMPLETE in the Known Unknowns doc (see e.g. lines 69-175 and 215-229). The prep instructions require removing completed unknowns from the schedule.
- **Developer ergonomics scope from PROJECT_PLAN.md is missing** – The Sprint 4 project brief expects error message improvements, configuration/flag work (`pyproject` options), and logging/verbosity updates, yet no day contains tasks covering those deliverables (reviewed across lines 55-700 of `PLAN_ORIGINAL.md`).
- **Scaling flag options incomplete** – Acceptance criteria on lines 479-491 mandate only `--scale none|auto`, but the Sprint 4 plan in `PROJECT_PLAN.md` requires `--scale none|auto|byvar`.
- **No work allocated for “10 mid-size examples” deliverable** – PROJECT_PLAN.md calls for additional example models in Sprint 4, but the current day-by-day schedule (lines 55-780) never budgets time for creating or curating those examples.
- **Success metric contradicts PATH licensing constraint** – The Success Metrics section targets resolving “All Known Unknowns by Day 6” (line 41), yet the schedule intentionally defers PATH-related Unknowns (2.4, 5.1–5.4) to Days 7–8 because the solver license arrives late (lines 560-629). This inconsistency makes the metric unattainable.
- **PATH-dependent follow-on research not isolated per instructions** – Day 1–6 sections embed Unknown summaries within the main task lists instead of placing remaining research into “Follow-On Research Items” blocks after the daily plan, as required. This is most noticeable in Day 3 (lines 215-276) and Day 4 (lines 290-315).
- **Heavy Day 8 workload** – Planned effort on Day 8 totals ~10 hours (Tasks 1–5 sum to 9h plus the 1h checkpoint; lines 581-629 and 631-638), leaving no slack on the critical PATH validation day.

## Recommendations
- Remove completed Unknown references from the daily task lists. Instead, keep a brief note that prerequisites were satisfied and reserve the “Follow-On Research Items” sections for any remaining INCOMPLETE Unknowns.
- Add explicit Day-level tasks for developer ergonomics (enhanced diagnostics/error messaging, configuration, logging) to match PROJECT_PLAN.md expectations, or document the deferment.
- Expand scaling work to cover the `byvar` mode so the CLI matches the agreed `--scale none|auto|byvar` contract.
- Schedule time (e.g., late Sprint day) to create or adapt the 10 mid-size example models promised in PROJECT_PLAN.md.
- Update the Success Metrics to acknowledge that PATH-related Unknowns complete on Day 8, or pull non-PATH dependencies forward if a Day-6 completion goal is still desired.
- Introduce explicit “Follow-On Research Items” subsections after each day’s main tasks so remaining Unknown investigations (especially the INCOMPLETE ones) are tracked separately from implementation work, per the sprint planning instructions.
- Re-scope Day 8 by moving low-risk documentation or option-setting tasks to Day 7 or 9, ensuring the solver-validation day stays within an 8-hour budget.

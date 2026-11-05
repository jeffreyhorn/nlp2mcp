# ISSUE #1799 — reporting: an MCP that proves infeasibility against an optimal NLP is recorded `not_tested`; report it as `mismatch` (P9a)

**GitHub:** [#1799](https://github.com/jeffreyhorn/nlp2mcp/issues/1799) · **Status:** 🟡 **OPEN** — Sprint 40 Day 11 (2026-11-05), P9a
**Layer:** **pipeline reporting** — `scripts/gamslib/test_solve.py::compare_solutions` (`_own_infeasible_answer`, Case 6) **and** `scripts/gamslib/run_full_test.py::run_pipeline` (the post-solve cascade, ~L1166)
**Positive control:** the cascade site left unchanged (site 1 alone) → the 13-model re-run leaves the DB byte-identical, proving site 2 is load-bearing

## Summary

A completed MCP solve that PROVES infeasibility (model status 4/5/6/19, solver status 1, our own attributed and completed model) against an NLP that solved optimally is recorded `comparison_status: "not_tested"` ("Skipped due to solve failure"). The owner decided on 2026-10-16 (`PROCESS_AND_SMALL_ITEMS.md` §P9a) that the honest verdict is **`mismatch`**: our MCP answered, and the answer disagrees with the NLP.

This is **KPI-visible**, so it has its own gate. It is a **relabel, not a fix**: no emit changes, and no model solves that did not solve before.

## Phase 0: Acceptance Gate

### Hand-Derived KKT Shape

There is no KKT change. The hand-derived object is each row's **verdict**:

| NLP | our MCP | today | after |
|---|---|---|---|
| optimal (MS 1/2) | proved infeasible (MS 4/5/6/19, SS 1, ours + complete) | `not_tested` (cascade) | **`mismatch` / `compare_status_mismatch`** (Case 4) |
| infeasible | proved infeasible | `not_tested` (cascade) | `match` / `compare_both_infeasible` (Case 3). **No row in today's DB has this shape.** |
| anything | failed to run, or not attributable | `not_tested` / `skipped` | unchanged |

### Expected Emit Pattern

No emit changes: `src/` is untouched. The expected DB pattern, **stated before the change**:
- **`kpi_block.py`: 0 figures move.** It reads `== "match"` only, and no affected row becomes a match.
- **DB tally:** `mismatch` **+13**, `not_tested` **−13**. No other row and no other field moves except the comparison block and run stamps.
- **The `--resolve-changed` checkpoint: 13 `forward` moves, all of them relabels, not fixes.** No checkpoint exception is added (see the PROCEED/REPLAN signal).

**Identity pin**, derived on 2026-11-05 from the DB at `91d7f0ff` with the widened condition. It is a set, not a count:
- **prep's 7, all still present:** agreste, camcge, cesam, fawley, lnts, mine, rocket. P5 was banked, so none dropped.
- **the cohort additions:** egypt, robot, shale, sroute and tricp, which are Task 7's five, re-derived rather than copied. Plus **tfordy**, persisted on 2026-11-05.
- sroute is in the set because its forward row (Day 8) was never persisted.

### Nearest Existing Mechanism

The nearest is **Case 3's own-infeasible exemption** (PR #1740 review): `_own_infeasible_answer` already lets a completed own-infeasible solve past Case 6.
- **Why it does not apply here.** The exemption is scoped to `nlp_infeasible` by design, so it covers only the both-infeasible shape and returns `skipped` for an optimal NLP.
- **It is also not reached from the pipeline.** `run_full_test.py` cascades every `status != "success"` solve to `not_tested` before the compare stage runs. So widening the exemption alone is **DB-inert** (§P9a.1).
- **Two sites are required.** A PR touching only Case 6 must be rejected as inert.
- **One shared predicate for both sites**, so they cannot drift. `test_solve.is_completed_own_infeasible(mcp_solve)` is: infeasible model status, solver status 1, and `status_is_ours_and_complete`.

### Verification Methodology

1. **Unit:**
   - `compare_solutions` on an NLP-optimal / own-infeasible row gives `mismatch`;
   - an NLP-infeasible one still gives `match`;
   - an unattributed or uncompleted one still gives `skipped`;
   - the cascade predicate admits exactly the own-infeasible shape.
   - Each test fails on `main`.
2. **The 13-model re-run** (`run_full_test.py --model <id>` × 13, in a scratch worktree):
   - exactly these 13 rows change `not_tested` → `mismatch`, and no other row changes;
   - each changed row's `mcp_solve` block is otherwise identical (outcome, MS, edition);
   - `kpi_block.py --json` is identical before and after, for both corpora.
3. **Positive control:** the same re-run with **site 2 reverted** leaves the DB unchanged on these rows (still `not_tested`).
4. `make test`.

### PROCEED/REPLAN Signal

- **PROCEED** if 1–4 hold with **exactly** the 13 names. A different set means the derivation or the predicate is wrong, and that is a stop.
- **REPLAN** if any `kpi_block` figure moves, if any row outside the 13 moves, or if the positive control shows site 2 is not load-bearing.
- **Regression note:** none is needed for the checkpoint. After landing, a fall-back of these rows to `not_tested` can only come from a real full-pipeline regression, because a stage-limited run does not touch `solution_comparison` (§P9a.3). That is correctly `backward`. **No checkpoint exception is added.**
- **Owner decision:** recorded 2026-10-16 (report as `mismatch`).

## Result (Sprint 40 Day 11): PROCEED, *k* = 12

**The set measured on landing is 12, not the 13 derived in advance. sroute drops out by name.**
- Its DB row was stale: Day 8's forward move was never persisted.
- On a real re-run it solves (`model_optimal_presolve`, match, through Day 8's #1787 landing), so it is no longer an own-infeasible row.
- That is the "drop by name any that another landing moved" rule. It is not a predicate error: the predicate ran on the stale row, exactly as specified.
- sroute is **not** persisted here. Its match needs `check_mcp_solve_attribution` before it is booked.

**The re-run of the 13 ran in a scratch worktree, in two passes.**
- **Pass A** has both sites; **pass B** has site 2 reverted.
- Each pass, compared with the committed DB, also shows two **re-run effects** unrelated to P9a:
  - sroute's presolve match;
  - 7 legacy rows (agreste, camcge, cesam, fawley, lnts, mine, rocket) gaining `license_edition: licensed`. Their stored rows predate schema 3.1.0's writer and held `null`.
- **A vs B isolates P9a:**
  - exactly **12** rows go `not_tested` → `mismatch` / `compare_status_mismatch`: agreste, camcge, cesam, egypt, fawley, lnts, mine, robot, rocket, shale, tfordy, tricp;
  - only `solution_comparison` fields differ, and `mcp_solve` does not move;
  - **`kpi_block.py --json` is identical** for both corpora.
- **The positive control (pass B) holds:** with site 2 reverted, none of the 12 moves. Site 2 is load-bearing.

**Persisted:** the 12 rows, by `run_full_test.py --model <id>` in the repo. The DB diff against the committed one:
- the 12 comparison changes and nothing else;
- the 7 `license_edition` refreshes, which are a stale-row correction;
- tally `mismatch` **+12**, `not_tested` **−12**;
- `kpi_block.py --json`: the only key that differs is `db_dirty`. **0 KPI figures move.**

**The checkpoint after landing:** the next `--resolve-changed` over these models reads **12 `forward` moves, all relabels, not fixes**. No checkpoint exception is added.

**Side effect, noted:** under the optional `--check-convexity` flag, stage 3b now also runs for these rows. Its docstring already covers a failed cold result.

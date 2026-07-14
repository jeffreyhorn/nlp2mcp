# Sprint 32 Per-Day Execution Prompts

One self-contained prompt per day (Day 0 + Days 1–13). Each is derived from `../PLAN.md` and the Sprint-32 prep outputs. Run one per day.

## How to Use

Paste the day's prompt as the task. Each prompt names its objective, branch, Phase-0 gate, quality gate, and the PR + wait-for-review step. Branches: `planning/sprint32-dayN-<slug>`.

## Cross-Cutting Rules (every day)

- **PR24 (Day-0 traced fix surface):** the banked `file:line` is a *hypothesis* — re-confirm it with `kkt_residual.py` / a `/tmp` control **before** any `src/` change. **The sign flip is BANNED for P5** (control-refuted 4× S30–S31).
- **Check the dual side (Sprint-30 camcge lesson):** any transform that redefines a dual must reach the target on the KKT *dual* (a `/tmp` prototype to MS-1), not just the primal. **Assert `modelstat` before reading any objective; `x.up=inf` is BANNED** (the Sprint-31 Day-2 measurement error).
- **PR25 (projection discipline):** track genuine-floor vs methodology separately; re-baseline after any pipeline-methodology change. The genuine-floor ramp is *conditional* (Task 9) — only emit-changing tracks advance it; **P5 = 0 floor**.
- **Emit-touching PRs:** include the regenerated `.gms` diff (PR14), pass the golden-staleness check (PR26) + the presolve-divergence detector, and (Day 5+) the `--resolve-changed --since-commit 4cbf8bff` checkpoint.
- **Quality gate (any `*.py` change):** `make typecheck && make format && make lint && make test` must pass before commit. Docs-only days skip it.
- **REPLAN honesty:** each REPLAN-gated day has a firm part that lands regardless; file the Sprint-33 carryforward on REPLAN (reallocation order P6 → P7 → rocket tail).

---

## Day 0 Prompt — Kickoff + Day-0 Traces + Tractability Probes (~6 h)

Confirm Day-0 = Sprint 31 final (`../BASELINE_METRICS.md`: Solve 107 / Match 92 / genuine floor 74 / model_infeasible 7 / Translate 135 / Tests 5,074). Verify `git diff 4cbf8bff..HEAD -- src/ scripts/` is empty before skipping the retest; if non-empty, run a fresh retest. Run the **Day-0 traces (PR24)** and re-confirm each Phase-0 gate's `Traced Fix-Surface (Day-0)` `file:line` (`../PHASE_0_ACCEPTANCE_GATES.md`): mine (`kkt_residual.py` → CASE_B `stat_x(3,1,1)` rel 2.37, duals CONSISTENT), camcge (CASE_B `stat_mps`, `mps.m = −209.861`), sarf (the 2-D gate + the 369K-vs-398 timing), rocket (Case-c clean at the NLP point — boundary `stat_ht`/`stat_step`), hhfair (D1 `stat_u` rel 2.0, `nu_obj=±1`). Then run the **three tractability probes:** (1) **P1 warm-residual→0 `/tmp`** — apply `piL_x=max(N,0)`, `piU_x=max(−N,0)` to a scratch `mine_mcp_presolve.gms` → the harness reports Case-a at the bound-active `stat_x` rows (`modelstat` asserted); (2) **P3 dual-consistent `/tmp`** — hand-edit `camcge_mcp.gms` with `nu_mps_fx.l = -mps.m` + the dual-consistent Walras redefinition → reach MS-1 at omega 191.7346 (check the dual side); (3) **P2 sarf O(active) timing** — confirm the sparsified `stat_task$taskposs` emits 398 active (not 369,024), translate in seconds. Restate the PR25 tally (genuine 74 / methodology 21; the → ≥ 75 conversion map: mine [P1] + camcge [P3] cold-match; P6 cpack/fawley). Docs/trace-only (no `src/`). **No PR** (or a docs-only trace-notes PR).

## Day 1 Prompt — Priority 1: mine bound-multiplier emit (start) (~6 h)

Branch `planning/sprint32-day1-mine-boundmult`. Replace the presolve bound-multiplier transfer (`src/emit/emit_gams.py:1548–1577`, currently `piL_x/piU_x = ±x.m`) with the **residual-`N` derivation** `piL_x = max(N,0)`, `piU_x = max(−N,0)` (`N` = the non-bound part of `stat_x` after the `lam_pr` transfer) — closing `stat_x = N − piL_x + piU_x = 0` at bound-active rows (`../MINE_BOUND_MULTIPLIER_DESIGN.md`). **Gate the `N`-derivation to the head-offset-coupled case** (or `--resolve-changed`-verify) so the non-mine presolve cohort stays byte-stable; keep the S31 head-offset foundation (16 guard tests) green. **Phase-0 gate:** `docs/issues/ISSUE_1443_*.md` §P1 (the Day-0 `/tmp` warm-residual→0 must be Case-a before src). Quality gate + emit-touching PR (WIP if incomplete) + wait for review.

## Day 2 Prompt — Priority 1: mine warm→cold verification (~6 h)

Re-run `kkt_residual.py data/gamslib/raw/mine.gms` after the `N`-derivation → **warm residual → 0 (Case-a**, `modelstat` asserted). Then the presolve solve → **MS-1** (+1 Solve; +1 genuine floor if it cold-matches). Confirm the 16 head-offset foundation guard tests stay green (`test_head_domain_offsets.py` + `test_head_offset_presolve_transfer.py` + `test_head_offset_marginal_map.py`) and the non-mine presolve goldens byte-stable (`--resolve-changed --since-commit 4cbf8bff`). Quality gate + emit-touching PR + wait for review.

## Day 3 Prompt — Priority 1: mine close-or-REPLAN (~5 h)

Complete the mine bound-multiplier fix. **PROCEED** (mine `model_infeasible → model_optimal`, +1 Solve; +1 genuine floor if cold-match) if the warm residual closes with no fresh residual. **REPLAN mine → a Sprint-33 deeper head-offset bound-complementarity architecture** (prior Medium) if a **5th coupling** surfaces — a fresh `stat_x` residual persists at the NLP optimum, or `sign(N)` contradicts the bound-active status — file the carryforward; the bound-multiplier design + the S31 IR foundation land regardless; freed ~8–14 h → P6/P7 (Task 9). **Phase-0 gate:** `docs/issues/ISSUE_1443_*.md` §P1. Quality gate + emit-touching PR + wait for review.

## Day 4 Prompt — Priority 3: camcge `stat_mps` + Walras (start, REPLAN-gated) (~7.5 h)

Branch `planning/sprint32-day4-camcge`. **Step 1 (general emit fix):** extend the #1462 fixed-variable-marginal transfer block (`src/emit/emit_gams.py`) to emit `nu_mps_fx.l = -mps.m` (sign per the multiplier's stationarity role; `mps.m = −209.861`) → `stat_mps` **Case-a** (`../CAMCGE_STAT_MPS_WALRAS_DESIGN.md` §1). **Step 2 (Epic 5, from the Day-0 `/tmp` prototype):** keep every market-clearing row + the consumption-weighted numéraire + redefine the redundant market's dual via Walras' law; add the **S1∧S2∧S3 degeneracy detector** (S3 cold-MCP-singular = the false-positive guard; pass-through default — never transform a well-posed model). **Phase-0 gate:** `docs/issues/ISSUE_1330_*.md` §P3 (the `/tmp` prototype must have reached MS-1 at 191.7346 Day 0 before src). Quality gate + emit-touching PR (WIP) + wait for review.

## Day 5 Prompt — Priority 3: camcge close-or-REPLAN + Checkpoint 1 (~7.5 h)

Complete camcge. **The empirical gate (Unknown 3.1/3.2): PROCEED** if the transformed camcge reaches **MS-1 at omega 191.7346** (non-singular basis) **and** the S1∧S2∧S3 detector flags only camcge across irscge/lrgcge/moncge/stdcge (+1 Solve). **REPLAN** if the `/tmp` prototype can't reach MS-1 or the detector false-flags: step 1 still lands (a cleaner CASE_B → Case-a general emit fix), the numéraire → a per-model-numéraire-declaration **Epic-5** item (camcge stays `model_infeasible` in S32); freed step-2 ~6–12 h → P6/P7. Then **Checkpoint 1:** `--resolve-changed --since-commit 4cbf8bff` re-solve of the changed-golden set (bucket-diff vs the committed DB) + golden-staleness + the PR25 re-baseline. **NO-GO** if any changed-golden model moved backward → investigate before proceeding. *(Both firm +Solve movers have now fired their gates.)* **Phase-0 gate:** `docs/issues/ISSUE_1330_*.md` §P3. Quality gate + emit-touching PR + wait for review.

## Day 6 Prompt — Priority 2: sarf 4-D `task` sparsification (start, REPLAN-gated) (~6 h)

Branch `planning/sprint32-day6-sarf`. Extend `_is_blowup_dynamic_subset_equation` (`src/ad/index_mapping.py`) from srpchase's 1-D to sarf's **2-D** dynamic-subset shape (`tbal(g,t)$taskposs`, `equipb1/equipb2`); begin the **new parametric `stat_task` emit** in `src/kkt/stationarity.py` — one symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)` (the banked 7-guarded-term derivation) + `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0`, **no set-name-literal multiplier indices** (the Sprint-26 `nu_slack("srn")` failure; scan `grep -En 'nu_[[:alnum:]_]+\("' sarf_mcp.gms` = empty). Atomic (re-emit + 2-D gate + cross-terms + `task.fx` together) (`../SARF_STAT_TASK_SPARSIFICATION_DESIGN.md`). **Phase-0 gate:** `docs/issues/ISSUE_1385_*.md` §P2. Quality gate + emit-touching PR (WIP) + wait for review.

## Day 7 Prompt — Priority 2: sarf tractability gate (~6 h)

Finish the sarf emit. **The tractability gate (Unknown 2.1):** the re-emit must be **O(active = 398), not O(369,024)** — time `sarf_mcp.gms` (target seconds, cf. srpchase's 1-D 6.56 s; well under the > 180 s Option-1 timeout). **PROCEED** (sarf `translate_failure → translate`, +1 Translate) if sub-budget; **REPLAN to Sprint 33** (a documented parametric-emit re-scoping; freed ~8–16 h → P6/P7) if it re-triggers the timeout. Quality gate + emit-touching PR + wait for review.

## Day 8 Prompt — Priority 2: sarf close + golden (~5 h)

Close sarf: the `stat_task` matches the banked 7-guarded-term derivation (grep-scan clean); sarf's *new* `sarf_mcp.gms` golden is byte-stable (caught by the golden-staleness gate, since `--resolve-changed` diffs existing goldens) and `--resolve-changed` GO. **Verifies:** 2.2, 2.3, 2.4. Quality gate + emit-touching PR + wait for review.

## Day 9 Prompt — Priority 4: rocket PATH-consultation input (~9 h)

Branch `planning/sprint32-day9-rocket`. Re-confirm the emit residual is **clean at the NLP point (Case-c boundary signature** — `stat_ht(h0)`/`stat_step`/`stat_ht(h50)` move with the warm-start value, interior near tolerance**) before** any forcing (PR27). Confirm no untried emittable lever crosses (PATH options 477→382; μ-continuation / multistart / the division-by-variable reformulation all MS-5). **Finalize the PATH-consultation input** for the renumbered Sprint 33 (`../ROCKET_PATH_CONSULTATION_INPUT.md` — the concrete question + the ruled-out-lever survey + the `--force` scaffold); **+1 Solve only if** a lever unexpectedly crosses. **Phase-0 gate:** `docs/issues/ISSUE_1462_*.md` §P4. Quality gate (if any `*.py`) + PR (docs unless a lever lands emit) + wait for review.

## Day 10 Prompt — Priority 5: hhfair + CGE Case-c classifier + Checkpoint 2 (~8 h)

Branch `planning/sprint32-day10-casec`. Add the **`kkt_residual.py` Case-c auto-classifier** (`scripts/diagnostics/kkt_residual.py` — the diagnostic harness, **not** `src/` emit; `../CASE_C_CLASSIFIER_DESIGN.md`): a post-verdict reclassification pass — CASE_B + **D1** (the max-residual `stat_<var>`'s `<var>` is the objective-defining intermediate variable, `obj =e= f(<var>)`, `nu_obj=±1`) ∧ **D3** (cold-start MCP reaches a spurious KKT point) → `case_c (objective-defining-intermediate-variable non-convexity)`. **THE SIGN FLIP STAYS BANNED.** Re-confirm all four members Case-c (hhfair `stat_u` rel 2.0; irscge/lrgcge/moncge `stat_xp` rel ~0.06); close `ISSUE_1236` as documented-non-convex (methodology, **0 genuine floor**). Then **Checkpoint 2:** `--resolve-changed` re-solve + golden-staleness + PR25 tally. **Phase-0 gate:** `docs/issues/ISSUE_1236_*.md` §P5. Quality gate + PR + wait for review.

## Day 11 Prompt — Priority 6: adjacent backlog + REPLAN-slack (~11 h)

Branch `planning/sprint32-day11-backlog`. **Offset-alias generalization (`../TOOLING_AND_BACKLOG_ANALYSIS.md` §2):** emit-diff the highest-prior #1111/#1112 second-index-transpose candidates beyond polygon/ps2 — **cpack** (circle-packing distance sibling) first, then ps3_s_scp/ps5_s_mn/ps10_s_mn/partssupply — via the landed general-alias core; land any that change the cold emit AND pass the `--resolve-changed --since-commit 4cbf8bff` **GO** gate. **Failure-cohort (§3):** attempt **fawley** (convex LP, uniform `stat_bq(*,fuel-oil)` rel 0.973 — a clean second-index Case-b, the strongest cohort +Solve) if the core generalizes; agreste is scope-caveated (verify the double-`solve` driver scope first); cesam/lnts stay banked Case-c. **REPLAN-slack:** absorb whatever the mine/camcge/sarf REPLANs freed (Task 9 order P6 → P7 → rocket). Deliverable: ≥ 1 model recovered OR the cohort re-triaged. Quality gate + PR (emit-touching if a candidate lands, else docs) + wait for review.

## Day 12 Prompt — Priority 7 infrastructure + REPLAN-slack (~8 h)

Branch `planning/sprint32-day12-infra`. **P7 property fixtures:** add **shape12** (head-offset 4th-site bound-multiplier — guards the P1 emit) + **shape13** (sarf 4-D `task` — guards the P2 emit) to `tests/integration/emit/test_ad_crossterm_shapes.py` (fail-before/pass-after; add only for tracks that landed). Recompute the **PR25 genuine-floor tracking** against the S32–S35 footnote-⁸ ramp (S32 ≥ 75); refresh the `--resolve-changed` checkpoint targets; begin the **Epic-4 `SUMMARY.md` skeleton** (one row per Sprint 18–35). **REPLAN-slack:** absorb residual freed budget. Quality gate + PR (tests/ + docs) + wait for review.

## Day 13 Prompt — Final Retest + Closeout (~8 h)

Full pipeline retest under ≥ 3 `PYTHONHASHSEED` values (PR12); recompute the DB (machine-portable paths) + the Sprint 31 → 32 metrics comparison; **PR25 genuine-vs-methodology re-baseline** (genuine floor → ≥ 75 target). **Closeout:** `SPRINT_LOG.md` final entry + top-table + per-priority summary; `SPRINT_RETROSPECTIVE.md` authored; file the Sprint-33 carryforwards (mine if REPLAN'd → deeper head-offset architecture; the camcge numéraire if P3 step-2 REPLAN'd → Epic 5; sarf if P2 REPLAN'd → re-scoping; rocket PATH-consultation input; cesam/lnts Case-c; any un-landed P6 candidate). Docs/DB-only PR (no quality gate unless `*.py` changed).

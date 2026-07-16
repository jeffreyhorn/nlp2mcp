# Sprint 33 Per-Day Execution Prompts

One self-contained prompt per day (Day 0 + Days 1–13). Each is derived from `../PLAN.md` and the Sprint-33 prep outputs. Run one per day.

## How to Use

Paste the day's prompt as the task. Each prompt names its objective, branch, Phase-0 gate, quality gate, and the PR + wait-for-review step. Branches: `planning/sprint33-dayN-<slug>`.

## Cross-Cutting Rules (every day)

- **PR24 (Day-0 traced fix surface):** the banked `file:line` is a *hypothesis* — re-confirm it with `kkt_residual.py` / a `/tmp` control **before** any `src/` change. **For P1 mine the cross-term premise is REFUTED** (Task 3: the emitted `stat_x` cross-term is algebraically correct) — the fix is **multiplier-keying (H1)**, NOT a term/sign change. **The objective-gradient sign flip is BANNED for P5** (control-refuted 4× S30–S31).
- **Assert `modelstat` before reading any objective; `x.up=inf` is BANNED** (the Sprint-31 Day-2 measurement error). **Check the dual side (Sprint-30 camcge lesson):** any transform that redefines a dual must reach the target on the KKT *dual* (a `/tmp` prototype to MS-1), not just the primal.
- **PR25 (projection discipline):** track genuine-floor vs methodology separately; re-baseline after any pipeline-methodology change. The genuine-floor ramp is *conditional* (Task 9) — only emit-changing tracks advance it; **P5 = 0 floor**. Anchor 74.
- **Emit-touching PRs:** include the regenerated `.gms` diff (PR14), pass the golden-staleness check (PR26) + the presolve-divergence detector, and (Day 5+) the `--resolve-changed --since-commit ee51ed9e` checkpoint (the **Day-0 code anchor**; `4cbf8bff` is the DB byte-anchor, a different purpose).
- **Quality gate (any `*.py` change):** `make typecheck && make format && make lint && make test` must pass before commit. Docs-only days skip it.
- **REPLAN honesty:** each REPLAN-gated day has a firm part that lands regardless; file the Sprint-34 carryforward on REPLAN (reallocation order P6 → P7 → the rocket forcing tail).

---

## Day 0 Prompt — Kickoff + Day-0 Traces + Control Probes (~6 h)

Confirm Day-0 = Sprint 32 close (`../BASELINE_METRICS.md`: Solve 107 / Match 92 / genuine floor 74 / model_infeasible 7 / Translate 135 / all-219 Match 95 / Tests 5,085). Verify `git diff ee51ed9e..HEAD -- src/ scripts/` is empty before skipping the retest; if non-empty, run a fresh retest. Run the **Day-0 traces (PR24)** and re-confirm each Phase-0 gate's Day-0 fingerprint (`../PHASE_0_ACCEPTANCE_GATES.md` §1): mine (`kkt_residual.py` → CASE_B `stat_x(3,1,1)` rel 2.37, duals CONSISTENT — **and** the Task-3 cross-term-correct finding: residual = the 6 bound-active `c`-boundary rows only, interior at 0), sarf (the three enumeration sites + the 369K-vs-398-active count), fawley (CASE_B `stat_bq`, `max|stat_bq|` 473 → 18 [96%]), camcge (CASE_B `stat_mps` cleared by S32 step 1; residual MS-4 Walras), rocket (Case-c clean at the NLP point — boundary `stat_ht`/`stat_step`). Then run the **three control probes:** (1) **P1 H1 `/tmp` (run first — highest prior):** key `comp_pr`/`lam_pr` + the `stat_x` cross-term to the head label `(k,l+1,i,j)` via the unused `head_domain_offsets` IR on a scratch `mine_mcp_presolve.gms` → the harness reports `N → 0` at ALL 6 bound-active rows AND unchanged (0) at every interior row (`modelstat` asserted; `x.up=inf` BANNED) → presolve MS-1 @ 17500; (2) **P2 sarf O(active) probe:** confirm the sparsified `stat_task$taskposs` enumerates 398 active, not 369,024; (3) **P3 fawley localize-by-column `/tmp`:** re-confirm `max|stat_bq|` 473 → 18 and localize the residual 18.47 by column (the H-a/H-b discriminator). Restate the PR25 tally (genuine 74; the → +1 conversion map: P1 H1 cold-match; P3's genuine cross-term correction — the firmest lever, lands even under H-b). Docs/trace-only (no `src/`). **No PR** (or a docs-only trace-notes PR).

## Day 1 Prompt — Priority 1: mine H1 head-label multiplier re-keying (start) (~7 h)

Branch `planning/sprint33-day1-mine-multiplier-keying`. **The cross-term is already correct (Task 3) — do NOT change its terms/signs** (refuted twice: S32 `N`-derivation + S33 Task-3). Re-key `comp_pr`/`lam_pr` + the `stat_x` cross-term to the shifted head label `(k,l+1,i,j)` (where the NLP stores `pr.m`) via the currently-unused `head_domain_offsets` IR — `src/kkt/stationarity.py` (`_try_build_param_offset_crossterm:5712` + the multiplier keying) + `src/ad/…` head-label multiplier plumbing (`../MINE_CROSSTERM_DESIGN.md` §5, H1). Gate the re-keying to the head-offset-coupled case so the non-mine param-offset cohort (srpchase) stays byte-stable. **Phase-0 gate:** `../PHASE_0_ACCEPTANCE_GATES.md` §1 P1 (the Day-0 H1 `/tmp` warm-residual→0 at the 6 bound-active rows must have passed before src). Quality gate + emit-touching PR (WIP if incomplete) + wait for review.

## Day 2 Prompt — Priority 1: mine warm→cold verification (~7 h)

Re-run `kkt_residual.py data/gamslib/raw/mine.gms` after the H1 re-keying → **warm residual `N → 0` at all 6 bound-active rows, Case-a** (`modelstat` asserted), interior unchanged (0). Then the presolve solve → **MS-1 @ 17500** (+1 Solve; +1 genuine floor if it cold-matches). Confirm the S31 head-offset foundation guard tests stay green and the non-mine presolve goldens byte-stable (`--resolve-changed --since-commit ee51ed9e`). Quality gate + emit-touching PR + wait for review.

## Day 3 Prompt — Priority 1: mine close-or-REPLAN (~6 h)

Complete the mine H1 re-keying. **PROCEED** (mine `model_infeasible → model_optimal`, +1 Solve; +1 genuine floor if cold-match) if the warm residual closes with no fresh residual and no interior perturbation. **REPLAN mine → a Sprint-34 deeper head-offset dual-architecture subsystem** (prior **High** — the banked premise was twice-refuted) if H1 (and the H2 `d\c`-ring reconciliation) cannot drive `N → 0` without perturbing an interior row or regressing srpchase — file the carryforward; the cross-term-correct finding + the multiplier-coupling characterization + the S31 IR foundation land regardless; freed ~14–18 h → P6/P7 (Task 9). **Phase-0 gate:** `../PHASE_0_ACCEPTANCE_GATES.md` §1 P1. Quality gate + emit-touching PR + wait for review.

## Day 4 Prompt — Priority 3: fawley second-index `sameas`-guard generalization (start) (~7 h)

Branch `planning/sprint33-day4-fawley-secondindex`. Extend the general indexed cross-term `sameas`-guard path — `src/kkt/stationarity.py` (`_build_sameas_guard:4623` / `_get_or_create_fresh_alias:4496` in `_add_indexed_jacobian_terms`) — so **every** second-index `cfq` gets the `$(sameas(cfq__, cf))` restriction, covering the qsb/pbal 2-D cross-terms `bq(c,cf)` (`../FAWLEY_SECOND_INDEX_DESIGN.md`). **Do NOT touch the 1-D polygon core** (`_var_at_two_indices_complement:7291` — polygon/ps2) and **no mbal-term change**. **Phase-0 gate:** `../PHASE_0_ACCEPTANCE_GATES.md` §1 P3 (the Day-0 localize-by-column control identified the H-a/H-b split before src). Quality gate + emit-touching PR (WIP) + wait for review.

## Day 5 Prompt — Priority 3: fawley close-or-REPLAN + Checkpoint 1 (~7 h)

Complete fawley. Drive `max|stat_bq| → 0` (not 96%) at the warm point (`modelstat` asserted). **H-a — PROCEED (+1 Solve):** presolve → MS-1 @ 2899.25 (+1 genuine floor if cold-match). **H-b — the emit still ships (a floor lever):** `max|stat_bq| → 0` yet MS-5 @ 5739 (non-emit LP-convergence) → the genuine cross-term correction lands (a cold-emit change → +genuine floor) and fawley's +Solve **hands to the P5 forcing survey** — NOT a REPLAN. **REPLAN only** if the generalization leaks onto the mbal / first-index shape or regresses the 1-D core (correctness risk) → re-scope; freed ~6–12 h → P6/P7. Then **Checkpoint 1:** `--resolve-changed --since-commit ee51ed9e` re-solve of the changed-golden set (bucket-diff vs the committed DB) + golden-staleness + the PR25 re-baseline. **NO-GO** if any changed-golden model moved backward → investigate before proceeding. *(Both in-sprint +Solve movers have now fired their gates.)* **Phase-0 gate:** `../PHASE_0_ACCEPTANCE_GATES.md` §1 P3. Quality gate + emit-touching PR + wait for review.

## Day 6 Prompt — Priority 2: sarf three-site symbolic emit (start, REPLAN-gated) (~6 h)

Branch `planning/sprint33-day6-sarf-symbolic`. Begin the **atomic three-site O(active) symbolic re-emit** (`../SARF_EMIT_SUBSYSTEM_DESIGN.md`). Eliminate the 369,024-column materialization at all three sites (a partial = an inconsistent MCP): S1 the `acost3` body-differentiation (`src/ad/constraint_jacobian.py`), S2 the variable-column enumeration (`src/ad/index_mapping.py`), S3 the variable stationarity (`src/kkt/stationarity.py`) — replaced by one symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)` (the banked 7-term derivation) + `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0`. **No set-name-literal multiplier indices** (the Sprint-26 `nu_slack("srn")` failure, commit `243fe578`; scan two greps — `grep -E 'nu_[[:alnum:]_]+\("' sarf_mcp.gms` and `grep -E 'lam_[[:alnum:]_]+\("' sarf_mcp.gms`, both empty). **Phase-0 gate:** `../PHASE_0_ACCEPTANCE_GATES.md` §1 P2. Quality gate + emit-touching PR (WIP) + wait for review.

## Day 7 Prompt — Priority 2: sarf tractability gate (~6 h)

The re-emit must be **O(active = 398), not O(369,024)** — time `sarf_mcp.gms` (target **seconds**, cf. srpchase's 1-D analogue ~2.9s current runner / 6.56s S32 runner; the failure is > 75 s). **PROCEED** (sarf `translate_failure → translate`, +1 Translate) if sub-budget. **REPLAN to Sprint 34** (a documented parametric-emit re-scoping — a 4th enumeration site / builder-pipeline materialization; freed ~8–16 h → P6/P7) if it re-triggers the timeout. Verify the emitted `stat_task` term-for-term against the banked 7-term derivation. Quality gate + emit-touching PR + wait for review.

## Day 8 Prompt — Priority 2: sarf atomic land (~6 h)

Land the three-site fix **atomically** (S1 + S2 + S3 + the `task.fx` fixing in one PR — a re-emit without cross-terms is an inconsistent MCP). Confirm the emitted `stat_task$taskposs` is the symbolic guarded form over 398 active instances, no set-name literals. Quality gate + emit-touching PR + wait for review.

## Day 9 Prompt — Priority 2: sarf close + golden (~6 h)

Close sarf: golden byte-stable (sarf's *new* `sarf_mcp.gms` golden — caught by the golden-staleness gate, since `--resolve-changed` diffs *existing* goldens) + deterministic ×3 `PYTHONHASHSEED`; `--resolve-changed --since-commit ee51ed9e` GO (sarf the only changed golden). If the P2 tractability gate REPLAN'd (Day 7), file the Sprint-34 re-scoping instead and reallocate the freed budget → P6/P7. Quality gate + emit-touching PR + wait for review. *(P2 total ~24 h across Days 6–9.)*

## Day 10 Prompt — Priority 4 camcge Epic-5 gate + Priority 5 rocket/Case-c + Checkpoint 2 (~10 h)

Branch `planning/sprint33-day10-camcge-rocket`. **P4 camcge Epic-5 `/tmp` gate (confirm the deferral — `../CAMCGE_WALRAS_DESIGN.md`):** run the `/tmp` prototype of the full dual-consistent redefinition (keep every market-clearing row + the consumption-weighted numéraire + redefine the redundant market's dual via Walras' law), checking the KKT **dual** side. **Expected: MS-4** → Epic-5-deferred (camcge stays `model_infeasible`; the numéraire recipe + the S1∧S2∧S3 detector are the Epic-5 hand-off). **Promote to +1 Solve only if** it unexpectedly reaches MS-1 at omega 191.7346 (step 1 already landed S32). **P5 rocket/Case-c (`../ROCKET_CASEC_FORCING_PLAN.md` — no emit fix, sign flip BANNED):** re-confirm each Case-c model's residual is clean at the NLP point BEFORE any forcing (rocket boundary; hhfair/CGE `case_c_objdef`, `nu_obj=±1`); **submit** the FINALIZED rocket PATH-consultation input to the Sprint-34 hand-off; run the `--force {homotopy,multistart,optfile}` survey across hhfair + irscge/lrgcge/moncge ("a lever crosses" = global MS-1 → conditional +Match/+genuine; else banked Case-c, the modal outcome; **0 genuine floor**). **Checkpoint 2:** `--resolve-changed --since-commit ee51ed9e` re-solve + golden-staleness + the PR25 tally. PR (P4 docs unless the `/tmp` crosses to emit; P5 docs + the survey) + wait for review.

## Day 11 Prompt — Priority 6: failure-cohort re-triage + REPLAN-slack (~11 h)

Branch `planning/sprint33-day11-p6-cohort`. **P6 agreste scope-verify (`../TOOLING_AND_BACKLOG_ANALYSIS.md` §2):** inspect the agreste source for the double-`solve` scope (two `solve agreste maximizing yfarm using lp`, lines 294/298) BEFORE treating the CASE_B `stat_sales` rel 2.0 as an emit bug. If the single-solve scope holds CASE_B → a factor-of-2 dropped-gradient Case-b (+Solve candidate, `--resolve-changed`-gated); if a driver artifact → bank. **P6 `path_syntax_error` cohort (bonus back-half):** the 8 convex models whose emitted MCP fails at the PATH compile stage (clearlak/dinam/ganges/gangesx/indus/sample/turkey/turkpow) — scope the shared translate-syntax root (a single fix may recover several); each `--resolve-changed --since-commit ee51ed9e`-gated + a golden-staleness check on the new goldens. (cesam/lnts stay banked Case-c — bilinear SAM / bilinear-`step`.) **REPLAN-slack:** whatever the P1/P2/P3 REPLANs freed re-allocates here first (Task 9 order: P6 → P7 → the rocket tail). Deliverable: ≥ 1 model recovered OR the cohort re-triaged with banked diagnoses. Quality gate (if a candidate lands emit) + PR + wait for review.

## Day 12 Prompt — Priority 7: infrastructure + REPLAN-slack (~8 h)

Branch `planning/sprint33-day12-p7-infra`. **P7 property fixtures (each fail-before/pass-after, only once its fix landed):** **shape12** (head-offset bound-active — guards P1), **shape13** (sarf symbolic `stat_task` — guards P2), and a **new fawley 2-D second-index fixture** (guards P3, distinct from the 1-D shape10/11) → `tests/integration/emit/test_ad_crossterm_shapes.py`. **Genuine-floor tracking:** recompute the PR25 genuine-floor tracking (re-baselined to **74**); refresh the `--resolve-changed` checkpoint targets for the newly-touched emit sites. **Epic-4 `SUMMARY.md` row-33 continuation:** (1) reconcile the theme cell — row 33 currently reads "PATH author consultation & solution forcing" (that is Sprint 34's theme); Sprint 33's is "Sprint 32 REPLAN'd carryforwards"; (2) fill the cells in the rows-28–32 format {Theme / Headline KPIs / Firm landing(s) / REPLAN'd → carryforward}. **REPLAN-slack:** absorb residual freed budget per the Task-9 reallocation order. Quality gate (tests/ changed) + PR + wait for review.

## Day 13 Prompt — Final Retest + Closeout (~8 h)

Branch `planning/sprint33-day13-close`. **Full pipeline retest** under ≥ 3 `PYTHONHASHSEED` values (PR12); recompute the DB (machine-portable paths) + the Sprint 32 → 33 metrics comparison; **PR25 genuine-vs-methodology re-baseline** recomputed (genuine floor anchor 74). **Closeout:** `SPRINT_LOG.md` final entry + top-table + per-priority summary; `SPRINT_RETROSPECTIVE.md` authored; the Sprint-34 carryforwards filed (mine if REPLAN'd → deeper head-offset dual subsystem; sarf if REPLAN'd → re-scoping; fawley +Solve → the P5 forcing tail if H-b; the camcge numéraire → Epic 5; the rocket PATH-consultation input → the Sprint-34 consultation; cesam/lnts Case-c; any un-landed P6 candidate). Fill the SUMMARY row-33 cells. Docs/DB PR + wait for review.

---

**Document Created:** 2026-07-16 · **Owner:** Sprint 33 Planning Team · derived from `../PLAN.md` + the Tasks 1–10 prep outputs.

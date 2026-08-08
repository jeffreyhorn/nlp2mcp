# Sprint 36 Per-Day Execution Prompts

**Covers:** Sprint 36 Day 0 + Days 1–13 (front-loaded P1 markov Days 1–3; P3 fawley co-scheduled Day 4; Checkpoints Day 5 / Day 10; final retest Day 13). Schedule: `../PLAN.md`.

## How to Use

Paste one day's prompt per session. Each references the prep docs in `docs/planning/EPIC_4/SPRINT_36/` (this file is in `prompts/`, so sibling docs are `../<DOC>.md`). Per-day workflow: branch `planning/sprint36-dayN-<slug>` from `main` → work → quality gate ONLY if `*.py` changed → commit → push → PR → wait for review → on merge, "checkout main and pull".

## Cross-Cutting Rules (every day)

- **Anchor:** the DB / `--resolve-changed --since-commit` / banked-fingerprint anchor is **`78ceaead`** (DB byte-unchanged since it; markov/fawley/ganges emit + AD paths byte-identical; the only `src/` delta is the turkey `original_symbols.py` + the allowlist). The S36 Day-0 *code* state = S35 close `597d9d08`.
- **Emit-touching PRs:** include the regenerated `.gms` diff (PR14); pass the **2-D-cohort golden-staleness** check (`scripts/sprint_audit/check_golden_staleness.py --models cesam2,camcge,ps2_f_s,ps2_s,ps3_s_gic,polygon` — **scoped**, never the unscoped `make regen-goldens`) + the presolve-divergence detector; determinism ×3 `{0,1,42}` (PR12); and the `--resolve-changed --since-commit 78ceaead` checkpoint.
- **`/tmp` control BEFORE `src/`** on every emit-touching gate (PR24/PR27); cite `kkt_residual.py`.
- **`modelstat` asserted before every objective read; `x.up=inf` BANNED (mine); the Case-c objective-gradient sign flip BANNED (refuted 4×).**
- **No co-authored-by / no Claude-Code attribution** in commits/PRs; reply to each PR review comment thread individually.

## Day 0 Prompt — Kickoff + fingerprint re-confirm + GO/NO-GO (~6 h)

Confirm Day-0 = S35 close (`../DAY0_TRACE_NOTES.md`: Solve 108 / Match 93 / genuine floor 75 / Translate 135 / Parse 142 / model_infeasible 7 / path_syntax_error 7 / all-219 Match 96). Verify `git diff 78ceaead..HEAD -- src/` = only the turkey `original_symbols.py` + the presolve-divergence allowlist (markov/fawley/ganges paths byte-identical → the banked fingerprints reproduce). Re-confirm the Task-2 fingerprints (`../DAY0_TRACE_NOTES.md`): **markov** `CASE_B` `max|stat_z|` rel 13.3 (Part-1 → 1.55 deductive; `src/kkt/stationarity.py` + `src/ad/derivative_rules.py` unchanged); **fawley** the discriminator (summed constraint index absent from the coefficient); **sarf** O(active); **ganges** `$141`×15 / `$145` / `$149` + `_diff_prod:3276` unchanged; **camcge** the S1∧S2∧S3 detector fires only camcge (MS-4 @ omega 191.7346); **robustlp** the NA multiplier `.L` root (EXECERROR-84, `../FIXTURE_AND_HARNESS_CATALOG.md` §4). Restate the PR25 tally (floor 75; markov ∈ methodology → the +1 is real). **KU Day-0-blocker clearance:** all 30 unknowns resolved, **zero INCOMPLETE** (`../KNOWN_UNKNOWNS.md`; `../PLAN.md` §18 — GO). Docs/trace-only. **No PR** (or a docs-only trace-notes PR).

## Day 1 Prompt — P1 markov: Phase-0 `CASE_A` `/tmp` control + cold-solve gate (BEFORE `src/`) (~8 h)

Branch `planning/sprint36-day1-markov-control`. **PR27 `/tmp` control before any `src/`** (`../MARKOV_OFFDIAGONAL_DESIGN.md` + `../../SPRINT_35/DAY11_MARKOV_DIAGONAL_LEVER.md`): prototype **Part-1** (the diagonal-Kronecker split, `_kronecker_diag_correction` gated on `_mult_var_collision and _all_zero_offset` + the additive-const) and confirm `max|stat_z|` **13.3 → 1.55**. Then the **cold-solve gate** (markov is 2 vars / 3 eqns → local): emit the `CASE_A` `/tmp` MCP, assert `modelstat`, and confirm the **cold** solve (no presolve) reaches `model_optimal` + match — the methodology→genuine confirmation (floor 75 → 76). **REPLAN exit:** if the cold solve needs presolve even at `CASE_A` → the lever downgrades to **correctness-only** (land Part-1 as correctness or bank; 0 floor). `/tmp`-only (no `src/`). Docs/control-notes PR. Then wait for reviewer comments.

## Day 2 Prompt — P1 markov: Part-2 `σ=sp` — coordinated offset-key + emission (`/tmp` control) (~10 h)

Branch `planning/sprint36-day2-markov-offdiag`. The **deep blocker** (`../MARKOV_OFFDIAGONAL_DESIGN.md`): the off-diagonal `σ=sp` enumeration — the greedy first-canonical-match in `_compute_index_offset_key:5099` binds `sp` (canon `s`) to var position 0 instead of position 2 (s/sp/spp are aliases). Task 3 **proved a name-first tweak alone leaves `ngroups=45` AND crashes the emission** → implement the **coordinated offset-key + emission change** (Mechanism C — additive, gated on the markov-specific `σ=sp` signature, leaving the shared `_compute_index_offset_key` matcher untouched). `/tmp` control: reproduce the `nu_constr(s,i)` direct term + the `σ=sp` off-diagonal sum, drive `max|stat_z| → ~0` (`CASE_A`), and run the **2-D-cohort golden-staleness harness** (byte-identical). **REPLAN exit:** if the coordinated change can't be made leak-free / `σ=sp` can't be enumerated → **land Part-1 correctness-only** (Day 3) + bank Part-2 to a dedicated effort. `/tmp`-only. Docs/control-notes PR. Then wait for reviewer comments.

## Day 3 Prompt — P1 markov: `src/` land + per-model verify + fixture (~8 h)

Branch `planning/sprint36-day3-markov-land`. Land Mechanism C in `src/kkt/stationarity.py` (additive gated branch). Per-model verify: markov emit → `max|stat_z|` = 0 (`CASE_A`) → **cold** solve `model_optimal` + match (`modelstat` asserted) → **genuine floor 75 → 76**. Add the fast `shape_markov_diagonal_kronecker` fixture (`../FIXTURE_AND_HARNESS_CATALOG.md` §1, inline `make test` guard, skip-if-absent) + **flip & sharpen** `tests/integration/kkt/test_markov_multi_pattern.py::TestMarkovMultiPatternIntegration::test_markov_stationarity_has_correction_term` to the `σ=sp` target (kept `slow`) — §3. Run the 2-D-cohort golden-staleness harness (**only markov drifts**) + determinism ×3 + `--resolve-changed --since-commit 78ceaead` GO. Quality gate (Python touched). Emit-touching PR. Then wait for reviewer comments.

## Day 4 Prompt — P3 fawley: constraint-index-diagonal correction (co-scheduled) (~8 h)

Branch `planning/sprint36-day4-fawley-diag`. The `/tmp` control (`../FAWLEY_DISCRIMINATOR_DESIGN.md`): the second-index transpose term fires **only when the summed constraint index is absent from the derivative coefficient** — **disjoint from markov** (proven). Drive `max|stat_bq| → 0`; run the **shared 2-D-cohort golden-staleness harness** (markov + fawley both landed → cohort byte-identical). **REPLAN exit (gate leak / H-b):** any cohort drift or `max|stat_bq|` not reaching 0 → DEFER (a dedicated effort); **the +Solve is out of P3 scope** — H-b keeps the MCP at MS-5 @ 4399.557 vs the LP optimum 2899.25, so the +Solve is the P5 `--force` survey, not a `stat_bq` fix. Correctness-only (0 bucket) if it lands. Quality gate if Python touched. Emit-touching PR IF it lands; else docs-only. Then wait for reviewer comments.

## Day 5 Prompt — Checkpoint 1: markov + fawley verdict (~7 h)

Branch `planning/sprint36-day5-checkpoint1`. **Checkpoint 1:** `--resolve-changed --since-commit 78ceaead` re-solve (bucket-diff vs the committed DB) + the 2-D-cohort golden-staleness + the presolve-divergence detector + the PR25 re-baseline. **NO-GO** if any *unchanged* golden moved backward (`match→mismatch`, `model_optimal→model_infeasible`). Record: markov's floor verdict (75→76 genuine, or flat-correctness if Part-2 REPLAN'd); fawley's disposition. **Freed-budget reallocation:** if markov Part-2 REPLAN'd, its budget joins P2/P4. Docs or emit-touching PR per the landings. Then wait for reviewer comments.

## Day 6 Prompt — P2 sarf: symbolic-emit re-architecture, part 1 (~9 h)

Branch `planning/sprint36-day6-sarf-symbolic`. The 369K-column `task` blow-up re-arch (`../SARF_DESIGN_REFRESH.md`): **PR27 timing control first** — confirm the O(369K) → O(active) reduction (ncart=54 / ndomain=18 / nactive=4 validated under GAMS 54) prototypes under the cap. **REPLAN exit:** if the re-arch still exceeds the ~303 s cap or is not surgical → **bank** to a dedicated effort (no `src/`; +1 Translate is the lowest-leverage KPI, never displaces a bucket track). `modelstat` asserted. `/tmp`/control PR (or docs/bank). Then wait for reviewer comments.

## Day 7 Prompt — P2 sarf: symbolic-emit re-architecture, part 2 (~9 h)

Branch `planning/sprint36-day7-sarf-land`. If Day 6's control passed: land the O(active) symbolic emit in `src/`; verify sarf emits under the cap → `translate=success` (+1 Translate); determinism ×3 + `--resolve-changed --since-commit 78ceaead` GO + golden-staleness. If Day 6 REPLAN'd: finalize the bank (docs). Quality gate if Python touched. Emit-touching PR IF it lands; else docs/bank. Then wait for reviewer comments.

## Day 8 Prompt — P4 ganges/gangesx: cascade + rPower surfaced EARLY (~8 h)

Branch `planning/sprint36-day8-p4-ganges`. The ordered recovery (`../GANGES_RECOVERY_SEQUENCING.md`): re-apply `$141`+`$145` (from git `a8ff626c`; `$141` helper = `_expr_contains_varref_attribute`, `original_symbols.py:1392`) + `$149` (`_diff_prod` §5 patch, `derivative_rules.py:3276`) → **surface `rPower` FIRST** (the presolve embedded-NLP `x**y,x=0,y<0`, the #1378/#1424 class — the likely REPLAN; do NOT leave it to Day 12). Per-model: ganges AND gangesx each emit → compile → count residual `$NNN` (assert 0) → solve cold AND presolve (`modelstat` asserted) → bucket → match. The **335 s emits** use a **nightly/async golden-regen slot** (`--models ganges,gangesx --fix`), not the PR gate. **REPLAN exit:** `rPower` as hard as the precedents, or the `$66` `ac(i+2,r)` match artifact, or a 6th blocker → **bank** (ganges/gangesx stay `path_syntax_error`, Solve 108; hand-off = Task 6 + `a8ff626c`). `/tmp` control before `src/`. Docs/control PR. Then wait for reviewer comments.

## Day 9 Prompt — P4 ganges/gangesx: `src/` land or bank + per-model verify (~8 h)

Branch `planning/sprint36-day9-p4-land`. If Day 8's `rPower`/`$66` controls passed: land the cascade fixes in `src/`; per-model verify both ganges + gangesx (compile-clean-but-not-solving is NOT a recovery — report `path_syntax_error → model_infeasible` as such); regen the slow goldens (async slot) + determinism ×3 + `--resolve-changed` GO. **+2 Solve/Match if both paths land, else 0.** If Day 8 REPLAN'd: finalize the bank (docs). Quality gate if Python touched. Emit-touching PR IF it lands; else docs/bank. Then wait for reviewer comments.

## Day 10 Prompt — Checkpoint 2 + P7: robustlp de-allowlist + GAMS-54 re-baseline (~8 h)

Branch `planning/sprint36-day10-p7-infra`. **P7(a) robustlp NA de-allowlist** (`../FIXTURE_AND_HARNESS_CATALOG.md` §4, bounded): NA-guard the presolve multiplier `.L` warm-start transfer (reuse the `#1322` idiom `<mult>.l$(NOT (<mult>.l > -inf and <mult>.l < inf)) = 0;` in the marginal-transfer emit — NOT `emit_post_assignment_na_cleanup`), regen `robustlp_mcp_presolve.gms`, confirm EXECERROR-84 gone, **remove robustlp from `scripts/diagnostics/presolve_divergence_allowlist.txt`**. **P7(b):** land the **async GAMS-54 re-baseline result** (`../GAMS54_TESTBED_PLAN.md` — the demo re-solve + the 5 OBJ-GAP bucket-diff) + the genuine-floor recompute + the SUMMARY row-36 groundwork. **Checkpoint 2:** `--resolve-changed --since-commit 78ceaead` + golden-staleness + the PR25 tally. Quality gate (Python touched). Emit-touching PR. Then wait for reviewer comments.

## Day 11 Prompt — P5 consultation submission/scoping day (no `src/`) + REPLAN-slack (~7 h)

Branch `planning/sprint36-day11-p5` (docs). Per `../P5_CONSULTATION_FINALIZATION.md`: submit the FINALIZED rocket input (§1) to the PATH authors; pose the mine primal-degenerate-LP question (§2); run the **camcge Walras `/tmp` MS-1 demo control** (§3 — demo-reachable, 641 rows; assert `modelstat`; expected MS-4 → the per-model-numéraire Epic-5 declaration fallback, `../../../EPIC_5/CGE_DEGENERACY_SCOPING.md`); run the fawley `--force` survey (§4 — homotopy/multistart/optfile vs the H-b divergence). Absorb any Day-5/Day-9 REPLAN reallocation. **No `src/`.** Docs PR. Then wait for reviewer comments.

## Day 12 Prompt — Sprint-37 carryforward drafting + pre-retest staging (~7 h)

Branch `planning/sprint36-day12-carryforwards` (docs). Draft `SPRINT_37_CARRYFORWARDS.md` (any markov Part-2 / P4 / sarf REPLAN + the rocket PATH reply + the camcge Epic-5 gate result + the mine consultation + the turkey testbed solve + the GAMS-54 v53→v54 decision). Stage the Day-13 retest (the stable-model determinism set, the `--resolve-changed` command, the DB byte-check). Docs PR. Then wait for reviewer comments.

## Day 13 Prompt — Final Retest + Closeout (~8 h)

Branch `planning/sprint36-day13-close`. Determinism ×3 `{0,1,42}` (a stable-model md5); `--resolve-changed --since-commit 78ceaead` GO; DB byte-check; golden-staleness clean; the PR25 floor recompute (75 or 76); the **GAMS-54 v53→v54 version decision** (keep-v53 unless the re-baseline showed zero bucket regressions). Write `SPRINT_LOG.md` + `SPRINT_RETROSPECTIVE.md`; update `../../SUMMARY.md` row 36 against the floor-75 anchor + the actual close. Docs/DB PR. Then wait for reviewer comments.

---

**Covers:** Sprint 36 Day 0 + Days 1–13 (front-loaded P1 markov per Task 10; P3 fawley co-scheduled Day 4; Checkpoints Day 5 / Day 10; final retest Day 13). The honest projection: **genuine floor 75 or 76 (markov-contingent); Solve 108–110 (P4-bimodal); Translate 135 or 136 (sarf); robustlp de-allowlisted; turkey +1 testbed-deferred.**

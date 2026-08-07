# Sprint 36 Detailed Schedule (Day 0 + Days 1–13)

**Prep:** Tasks 1–10 complete (10 design/scoping docs + this schedule). **Anchor:** the S36 Day-0 code state = S35 close `597d9d08` (prep is docs-only); the `--resolve-changed --since-commit` / DB / banked-fingerprint anchor is **`78ceaead`** (the DB is byte-unchanged since it, and the markov/fawley/ganges emit + AD paths are byte-identical since it — the only `src/` delta since is the turkey `original_symbols.py` compile-recovery + the presolve-divergence allowlist, both unrelated to the S36 tracks; Task 2 `DAY0_TRACE_NOTES.md`).
**Budget:** ≤ 12 h/day over 14 days (Day 0 + Days 1–13); 168 h cap. Risk **LOW-to-flat**, with **markov the one local +1-floor lever** and **P4 the one bimodal +2 bucket gate**.

---

## 1. Sprint 36 Goal

Land the Sprint-35 carryforwards, structured around the single discovery that changes the sprint's shape: **markov's `stat_z` diagonal-Kronecker emit bug is a genuine cold-emit defect with a concrete +1-floor payoff** (methodology→genuine, 75→76) — the **only bucket-relevant emit lever found in S35, and fully local** (markov is 2 vars / 3 eqns, no testbed). So — inverting the ganges-front-loaded S35 — **P1 markov is front-loaded Days 1–3**, with **P3 fawley co-scheduled** (both touch the shared `_add_indexed_jacobian_terms`, so they share the 2-D-cohort leak gate). The remaining tracks are de-risked in prep: **P2 sarf** (369K symbolic re-arch, +1 Translate — the lowest-leverage KPI), **P4 ganges/gangesx** (the ≥5-blocker cascade, +2 Solve/Match or 0 — bimodal), **P5 consultation** (rocket/mine/camcge/fawley — a submission/scoping day, no `src/`), **P6 turkey** (testbed-gated +1, deferred), **P7 infra** (robustlp NA de-allowlist + the GAMS-54 re-baseline + fixtures + floor tracking).

## 2. Acceptance Criteria (honest projection)

| KPI | Day-0 (S35 close) | markov lands (Part-1+Part-2 cold-match) | markov Part-2 REPLANs / P4 flat |
|---|---|---|---|
| genuine floor | **75** | **76** (+1, markov methodology→genuine) | **75** (flat — Part-1 correctness-only) |
| Solve | 108 | 108, or **110** if P4 lands both paths | 108 |
| Match | 93 | 93, or **94/95** with P4 | 93 |
| Translate | 135 | **136** if sarf re-arch lands | 135 |

- **The one local, highest-probability lever is markov +1 floor** (no testbed, tiny model); its risk is **Part-2 `σ=sp`** (Task 3 proved a tweak alone crashes the emission — a *coordinated* offset-key + emission change is required). Part-1 alone is correctness-only (0 bucket).
- **P4 ganges is bimodal +2 or 0** — the `$66` (cold) + `rPower` (presolve embedded-NLP divergence) terminals must *both* be solved; the honest modal outcome is **0** (the P4-flat branch), matching S32–S35.
- **turkey's +1 is testbed-gated** (no licensed >1000-row GAMS-54 exists — Task 7); **deferred**, not in the in-sprint projection.
- **robustlp de-allowlist** (P7) is a bounded WARN-clearance, not a KPI bucket.
- **Do not promise floor > 76 or Solve > 110.** The realistic close, given the three-sprint flat record, is **floor 75 or 76** decided by markov Part-2, with P4 the bimodal upside.

## 3. Sequencing Constraints (from the prep outputs)

- **Front-load P1 markov (Days 1–3)** — the one local bucket lever; its Part-2 `σ=sp` REPLAN surfaces by the **Day-5 checkpoint**. Day 1 = the Phase-0 `CASE_A` `/tmp` control + cold-solve gate *before* `src/` (markov is tiny → cold-solve is local and immediate).
- **Co-schedule P3 fawley with P1 (Day 4)** — both touch `_add_indexed_jacobian_terms`; Task 4 proved the fawley discriminator **disjoint from markov** (fires only when the summed constraint index is absent from the coefficient). The **shared 2-D-cohort golden-staleness harness** (Task 9, `check_golden_staleness.py --models cesam2,camcge,ps2_f_s,ps2_s,ps3_s_gic,polygon`) is the leak gate for *both* changes — run after each.
- **Both markov + fawley are leak-free by design (Task 3/Task 4), empirically gated at PR time** by the cohort harness (minutes-scale → the harness is the nightly/targeted backstop; the fast per-fix fixtures `shape_markov_diagonal_kronecker` / `shape_fawley_2d_second_index` are the inline `make test` guard — Task 9).
- **P2 sarf (Days 6–7)** is a big symbolic-emit re-arch (Task 5, O(active) validated); its REPLAN exit is a **timeout** (still > 303 s) → bank. Lowest-leverage (+1 Translate).
- **P4 ganges (Days 8–9)** is the ≥5-blocker cascade (Task 6); **schedule `rPower` early** (the likely REPLAN); the 335 s emits need a **nightly/async golden-regen slot**, not the PR gate.
- **P5 (Day 11)** ships **no `src/`** — a submission/scoping day (Task 8): rocket → PATH authors; mine → the LP-degeneracy question; camcge → the Walras `/tmp` MS-1 demo control (now demo-reachable, 641 rows — Task 8); fawley → the `--force` survey.
- **Async testbed thread (Task 7):** the GAMS-54 corpus re-baseline (demo-runnable — the baseline is demo-built) + the 5 OBJ-GAP bucket re-check run **async before Day 10**, feeding the Day-13 version decision; turkey's solve is **license-gated** (runs only if a license is procured — not on the calendar).
- **Checkpoints:** Day 5 (markov + fawley PROCEED/REPLAN), Day 10 (Checkpoint 2 + P7 + the re-baseline result), Day 13 (final retest under ≥ 3 `PYTHONHASHSEED`).
- **`modelstat` asserted before every objective read; `x.up=inf` BANNED (mine); the Case-c objective-gradient sign flip BANNED (refuted 4×).**

## 4. Day 0 — Kickoff + fingerprint re-confirm + GO/NO-GO (≤ 6 h)

Confirm Day-0 = S35 close (Solve 108 / Match 93 / genuine floor 75 / Translate 135 / Parse 142 / model_infeasible 7 / path_syntax_error 7 / all-219 Match 96). Verify `git diff 78ceaead..HEAD -- src/` = only the turkey `original_symbols.py` + the allowlist (the known S35 delta; markov/fawley/ganges paths byte-identical → the banked fingerprints reproduce). Re-confirm the Task-2 fingerprints: **markov** `CASE_B` `max|stat_z|` rel 13.3 (Part-1 → 1.55 deductive); **fawley** the discriminator (summed index absent from coefficient); **sarf** O(active); **ganges** the `$141`×15 / `$145` / `$149` cascade + `_diff_prod:3276` unchanged; **camcge** the S1∧S2∧S3 detector fires only camcge (MS-4 @ omega 191.7346); **robustlp** the NA multiplier `.L` root (EXECERROR-84). Restate the PR25 tally (floor 75; markov ∈ methodology → the +1 is real). **KU Day-0-blocker clearance:** all 30 unknowns resolved (28 ✅ / 6.1 ❌→bounded / 6.2 🔍 BLOCKED→deferred) — **zero INCOMPLETE**. Assert GO for Day 1. Docs/trace-only. **No PR** (or a docs-only trace-notes PR).

## 5. Day 1 — P1 markov: Phase-0 `CASE_A` `/tmp` control + cold-solve gate (BEFORE `src/`) (~8 h)

Branch `planning/sprint36-day1-markov-control`. **PR27 `/tmp` control before any `src/`** (`MARKOV_OFFDIAGONAL_DESIGN.md` Task 3 + `../SPRINT_35/DAY11_MARKOV_DIAGONAL_LEVER.md`): prototype **Part-1** (the diagonal-Kronecker split, `_kronecker_diag_correction` gated on `_mult_var_collision and _all_zero_offset` + the additive-const) and confirm `max|stat_z|` **13.3 → 1.55** reproduces; then the **cold-solve gate** — markov is tiny, so emit the `CASE_A` `/tmp` MCP and confirm the **cold** solve (no presolve) reaches `model_optimal` + match (the methodology→genuine confirmation). **REPLAN exit:** if the cold solve needs presolve even at `CASE_A` → the lever downgrades to **correctness-only** (0 floor; land Part-1 as a correctness fix or bank). `modelstat` asserted. `/tmp`-only (no `src/`). Docs/control-notes PR.

## 6. Day 2 — P1 markov: Part-2 `σ=sp` — coordinated offset-key + emission (`/tmp` control) (~10 h)

Branch `planning/sprint36-day2-markov-offdiag`. The **deep blocker** (Task 3): the off-diagonal `σ=sp` enumeration — the multiplier index is an independent var index the offset machinery can't represent, and the greedy first-canonical-match in `_compute_index_offset_key:5099` binds `sp` to var position 0 not position 2. Task 3 **proved a name-first tweak alone leaves `ngroups=45` AND crashes the emission** → a **coordinated offset-key + emission change** (Mechanism C, additive + gated on the markov-specific `σ=sp` signature, leaving the shared matcher untouched). `/tmp` control: reproduce the `nu_constr(s,i)` direct term + the `σ=sp` off-diagonal sum, drive `max|stat_z| → ~0` (`CASE_A`), and run the **2-D-cohort golden-staleness harness** (byte-identical). **REPLAN exit:** if the coordinated change can't be made leak-free / `σ=sp` can't be enumerated → **land Part-1 correctness-only** (Day 3) + bank Part-2 to a dedicated effort. `/tmp`-only. Docs/control-notes PR.

## 7. Day 3 — P1 markov: `src/` land + per-model verify + fixture (~8 h)

Branch `planning/sprint36-day3-markov-land`. Land Mechanism C in `src/kkt/stationarity.py` (additive gated branch). Per-model verify: markov emit → `max|stat_z|` = 0 (`CASE_A`) → **cold** solve `model_optimal` + match → **genuine floor 75 → 76**. Add the fast `shape_markov_diagonal_kronecker` fixture (inline `make test` guard) + **flip & sharpen** `TestMarkovMultiPatternIntegration::test_markov_stationarity_has_correction_term` to the `σ=sp` target (kept `slow`) — Task 9. Run the 2-D-cohort golden-staleness harness (**only markov drifts**) + determinism ×3 + `--resolve-changed --since-commit 78ceaead` GO. Quality gate (Python touched). Emit-touching PR. **This is where the +1 floor lands or REPLANs to correctness-only.**

## 8. Day 4 — P3 fawley: constraint-index-diagonal correction (co-scheduled) (~8 h)

Branch `planning/sprint36-day4-fawley-diag`. The `/tmp` control (Task 4 `FAWLEY_DISCRIMINATOR_DESIGN.md`): the second-index transpose term fires **only when the summed constraint index is absent from the derivative coefficient** — **disjoint from markov** (proven). Drive `max|stat_bq| → 0`; run the **shared 2-D-cohort golden-staleness harness** (both markov + fawley now landed → cohort still byte-identical). **REPLAN exit (gate leak / H-b):** any cohort drift or `max|stat_bq|` not reaching 0 → DEFER; **the +Solve is out of P3 scope** (H-b → the P5 `--force` survey, the MCP stays MS-5 @ 4399.557 vs the LP optimum 2899.25). Correctness-only (0 bucket) if it lands. Emit-touching IF it lands; else docs-only.

## 9. Day 5 — Checkpoint 1: markov + fawley verdict (~7 h)

**Checkpoint 1:** `--resolve-changed --since-commit 78ceaead` re-solve (bucket-diff vs the committed DB) + golden-staleness (the 2-D cohort) + the presolve-divergence detector + the PR25 re-baseline. **NO-GO** if any *unchanged* golden moved backward. Record: markov's floor verdict (75→76 or flat-correctness); fawley's disposition (correctness-landed or deferred). **Freed-budget reallocation:** if markov Part-2 REPLAN'd, its budget joins P2/P4. Docs or emit-touching PR per the landings. **REPLAN exits explicit.**

## 10. Days 6–7 — P2 sarf: symbolic-emit re-architecture (~18 h)

Branch `planning/sprint36-day6-sarf-symbolic` (+ day7). The 369K-column `task` blow-up re-arch (Task 5 `SARF_DESIGN_REFRESH.md`): the O(active) symbolic emit (ncart=54 / ndomain=18 / nactive=4 validated under GAMS 54). PR27 timing control first. **REPLAN exit:** if the re-arch still exceeds the ~303 s cap (or the O(active) rewrite is not surgical) → **bank** to a dedicated effort (no `src/` ships); +1 Translate is the lowest-leverage KPI, so this never displaces a bucket track. `modelstat` asserted. Emit-touching IF it lands; else docs/bank PR.

## 11. Days 8–9 — P4 ganges/gangesx: ≥5-blocker cascade (rPower surfaced early) (~16 h)

Branch `planning/sprint36-day8-p4-ganges` (+ day9). The ordered recovery (Task 6 `GANGES_RECOVERY_SEQUENCING.md`): re-apply `$141`+`$145` (from git `a8ff626c`, `$141` helper = `_expr_contains_varref_attribute`) → `$149` (`_diff_prod` §5 patch) → **surface `rPower` (the presolve embedded-NLP `x**y,x=0,y<0` — the likely REPLAN) EARLY on Day 8**, not Day 12 → `$66` (cold calibration params). Per-model: each of ganges/gangesx independently emit → compile → count residual `$NNN` (assert 0) → solve (cold AND presolve, `modelstat` asserted) → bucket → match. The **335 s emits** → a **nightly/async golden-regen slot** (not the PR gate). **REPLAN exit:** `$66`'s `ac(i+2,r)` match artifact, or `rPower` proves as hard as the #1378/#1424 precedents, or a 6th blocker → **bank** (ganges/gangesx stay `path_syntax_error`, Solve 108; the hand-off is Task 6 + `a8ff626c`). **+2 Solve/Match if both paths land, else 0.** Emit-touching IF it lands; else docs/bank PR.

## 12. Day 10 — Checkpoint 2 + P7 infra (robustlp de-allowlist + re-baseline) (~8 h)

Branch `planning/sprint36-day10-p7-infra`. **P7:** (a) **robustlp NA de-allowlist** (Task 9, bounded) — NA-guard the presolve multiplier `.L` warm-start transfer (reuse the `#1322` idiom `<mult>.l$(NOT (<mult>.l > -inf and <mult>.l < inf)) = 0;`), regen the golden, confirm EXECERROR-84 gone, **remove robustlp from `presolve_divergence_allowlist.txt`**; (b) land the **async GAMS-54 re-baseline result** (Task 7 — demo-run, the 5 OBJ-GAP bucket-diff) + the genuine-floor recompute + the SUMMARY row-36 groundwork. **Checkpoint 2:** `--resolve-changed --since-commit 78ceaead` + golden-staleness + the PR25 tally. Quality gate (Python touched). Emit-touching PR (robustlp).

## 13. Day 11 — P5 consultation submission/scoping day (no `src/`) + REPLAN-slack (~7 h)

Branch `planning/sprint36-day11-p5` (docs). Submit the FINALIZED rocket input (Task 8 §1) to the PATH authors; pose the mine primal-degenerate-LP question (§2); run the **camcge Walras `/tmp` MS-1 demo control** (§3 — now demo-reachable, 641 rows; expected MS-4 → the per-model-numéraire Epic-5 declaration fallback); run the fawley `--force` survey (§4 — homotopy/multistart/optfile). Absorb any Day-5/Day-9 REPLAN reallocation. **No `src/`.** Docs PR (+ any Epic-5 declaration).

## 14. Day 12 — Sprint-37 carryforward drafting + pre-retest staging (~7 h)

Branch `planning/sprint36-day12-carryforwards` (docs). Draft `SPRINT_37_CARRYFORWARDS.md` (any markov Part-2 / P4 / sarf REPLAN + the rocket PATH reply + the camcge Epic-5 gate + the mine consultation + the turkey testbed solve + the GAMS-54 re-baseline decision). Stage the Day-13 retest. Docs PR.

## 15. Day 13 — Final Retest + Closeout (~8 h)

Determinism ×3 `{0,1,42}` (a stable-model md5); `--resolve-changed --since-commit 78ceaead` GO; DB byte-check; golden-staleness clean; the PR25 floor recompute; the **GAMS-54 v53→v54 version decision** (Task 7 — keep-v53 unless the re-baseline shows zero bucket regressions). Write `SPRINT_LOG.md` + `SPRINT_RETROSPECTIVE.md`; update `../SUMMARY.md` row 36 against the floor-75 anchor. Docs/DB PR.

## 16. Budget Summary

| Days | Priority / work | Nominal h |
|---|---|---|
| 0 | Kickoff + fingerprint re-confirm + GO/NO-GO | ≤ 6 |
| 1–3 | **P1 markov** (Phase-0 `CASE_A` + cold-solve Day 1; Part-2 `σ=sp` `/tmp` Day 2; `src/` land + fixture Day 3 — the +1-floor lever) | ~26 |
| 4 | **P3 fawley** constraint-index-diagonal (co-scheduled, shares the cohort gate) | ~8 |
| 5 | Checkpoint 1 (markov + fawley verdict) | ~7 |
| 6–7 | **P2 sarf** symbolic re-arch (+1 Translate; timeout REPLAN) | ~18 |
| 8–9 | **P4 ganges/gangesx** ≥5-blocker cascade (rPower early; +2 or 0) | ~16 |
| 10 | Checkpoint 2 + **P7** robustlp de-allowlist + re-baseline | ~8 |
| 11 | **P5** consultation submission/scoping (no `src/`) + REPLAN-slack | ~7 |
| 12 | Sprint-37 carryforwards + staging | ~7 |
| 13 | Final retest + closeout | ~8 |

Nominal ~111 h over the 168 h cap (≤ 12 h/day) — comfortable slack for a thorough markov + P4 push.

## 17. Phase-0 Coverage (PR24 + PR27)

Emit-touching tracks: **P1 markov**, **P3 fawley**, **P2 sarf**, **P4 ganges**, **P7 robustlp**. **P5 ships no `src/`** (submissions + a demo `/tmp` control). Each emit-touching gate runs a `/tmp` control BEFORE `src/` (markov `CASE_A` Day 1; fawley discriminator Day 4; sarf timing Day 6; ganges `$149`/`rPower` Day 8; robustlp NA-guard Day 10), cites `kkt_residual.py` (PR27), and passes determinism ×3 (PR12) + the 2-D-cohort golden-staleness (PR26, scoped `--models` for the shared-function changes) + presolve-divergence + `--resolve-changed --since-commit 78ceaead`. **"No bucket → no `src/`"** (the sarf/P4-bank exception: fast/regenerable goldens + `--resolve-changed` GO). **`modelstat` asserted before every objective read; `x.up=inf` BANNED; the Case-c sign flip BANNED.**

## 18. Known Unknowns Status Snapshot + GO/NO-GO

| Status | Count | Notes |
|---|---|---|
| ✅ VERIFIED | 28 | all Critical/High resolved; markov (1.1–1.5), fawley (3.1–3.4), sarf (2.1–2.4), ganges (4.1–4.5, 6.3), P5 (5.1–5.4), infra (7.1, 7.3–7.5) |
| ❌ WRONG → bounded Day-0 risk | 1 | 6.1 (no licensed >1000-row testbed — but the re-baseline is demo-runnable; only turkey is gated) |
| 🔍 BLOCKED → deferred | 1 | 6.2 (turkey solve — license-gated; the +1 is carried, not in-projection) |
| 🔍 INCOMPLETE | **0** | — |

**⇒ GO for Day 0.** Every unknown is resolved, taken as a bounded risk, or carried as a deferred exit; the one local bucket lever (markov) is front-loaded with its `σ=sp` REPLAN surfacing by the Day-5 checkpoint; the fixture/harness leak gates are specced; the async testbed dependency is bounded (only turkey's +1 needs a license the sprint doesn't have — deferred). The honest projection binds: **floor 75 or 76 (markov-contingent); Solve 108–110 (P4-bimodal); Translate 135 or 136 (sarf); robustlp de-allowlisted; turkey +1 deferred.**

## 19. Risk Register + Mitigations

| Risk | Mitigation |
|---|---|
| markov Part-2 `σ=sp` can't be made leak-free / enumerable (Med — the one live floor lever) | The Day-2 `/tmp` control + the 2-D-cohort harness surface it by the Day-5 checkpoint; REPLAN → land Part-1 correctness-only (0 floor, no broken code) + bank Part-2. |
| A markov/fawley change leaks onto the 2-D cohort (the fawley Day-9 precedent) | Both are additive gated branches leaving the shared matcher untouched (Task 3/4, disjoint by construction); the cohort golden-staleness harness is the mechanical PR-time backstop → any drift = revert. |
| P4 `$66`/`rPower` don't both solve (Med-High — the bimodal gate) | rPower surfaced Day 8 (early); REPLAN → bank all roots (no `src/`, the S35 outcome) + the Task-6 hand-off. |
| sarf re-arch still > 303 s | The Day-6 timing control before `src/`; REPLAN → bank (lowest-leverage KPI, no bucket cost). |
| No licensed testbed for turkey / the >1000-row re-baseline | The re-baseline is demo-runnable (Task 7); only turkey's +1 is gated → deferred, not a blocker. |
| The sprint closes flat (markov correctness-only, P4 banks) | Within the projection; the firm product is markov Part-1 correctness + robustlp de-allowlist + the de-risked banks + the Sprint-37 bundle — zero broken code (the S32–S35 pattern). |

## 20. Related Documents

- **Prep:** `PREP_PLAN.md` · `KNOWN_UNKNOWNS.md` · `DAY0_TRACE_NOTES.md` (Task 2) · `MARKOV_OFFDIAGONAL_DESIGN.md` (Task 3) · `FAWLEY_DISCRIMINATOR_DESIGN.md` (Task 4) · `SARF_DESIGN_REFRESH.md` (Task 5) · `GANGES_RECOVERY_SEQUENCING.md` (Task 6) · `GAMS54_TESTBED_PLAN.md` (Task 7) · `P5_CONSULTATION_FINALIZATION.md` (Task 8) · `FIXTURE_AND_HARNESS_CATALOG.md` (Task 9) · this `PLAN.md` (Task 10)
- **Execution:** `prompts/PLAN_PROMPTS.md` (Day 0 + Days 1–13)
- **Bundle + banked S35:** `CONSULTATION_BUNDLE.md` (the S35-assembled bundle, now a SPRINT_36 sibling) · `../SPRINT_35/DAY11_MARKOV_DIAGONAL_LEVER.md` · `../SPRINT_35/DAY3_P4_BANK_CARRYFORWARD.md`

---

**Status:** Sprint 36 is **GO for Day 0** — all 10 prep tasks complete; the schedule front-loads P1 markov (Days 1–3, the one local +1-floor lever) so its `σ=sp` REPLAN surfaces by the Day-5 checkpoint, with P3 fawley co-scheduled (Day 4, shared cohort gate), P2 sarf (Days 6–7), P4 ganges (Days 8–9, rPower early), Checkpoint 2 + P7 robustlp de-allowlist (Day 10), P5 consultation (Day 11), carryforwards (Day 12), and the final retest (Day 13). The honest projection binds: **genuine floor 75 or 76 (markov-contingent); Solve 108–110 (P4-bimodal); Translate 135 or 136 (sarf); robustlp de-allowlisted; turkey +1 testbed-deferred.**
**Last Updated:** 2026-08-07 · **Owner:** Sprint 36 Execution Team

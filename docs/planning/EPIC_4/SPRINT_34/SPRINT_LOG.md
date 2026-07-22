# Sprint 34 — Progress Log

**Sprint:** 34 (S33 carryforward — mine head-offset dual [P1] · sarf symbolic-emit [P2] · fawley 2nd-index [P3] · P4 bound-transfer · camcge Walras [Epic 5] · rocket/Case-c [P5] · P6 ganges cohort) · **Weeks 33–34**
**Code anchor:** S33 close `750803b2` · **DB byte-anchor:** `750803b2` (byte-unchanged all sprint)

## Headline KPIs (142 convex-candidate corpus)

| Metric | Day-0 | Close | Δ |
|---|---|---|---|
| Parse | 142 | 142 | — |
| Translate | 135 | 135 | — |
| Solve | 108 | 108 | — |
| Match (as-measured) | 93 | 93 | — |
| genuine floor | 75 | 75 | — (≥ 76 target missed — modal-flat) |
| model_infeasible | 7 | 7 | — |
| path_syntax_error | 7 | 7 | — |
| all-219 Match | 96 | 96 | — |
| Determinism | — | ✅ ×3 `{0,1,42}` | byte-identical (P4 presolve path + cold path) |

**Full modal-flat close — zero bucket moves, exactly the Task-9 projection.** Every deep track REPLAN'd/deferred (P1/P2/P3), P4 shipped a correctness fix with no +Solve (a-priori), P5 handed off (Epic 5 / Sprint 35), P6 re-triaged (the `$141` fix verified + banked). The sprint's firm product is **de-risking**: six control-confirmed dispositions + two banked-and-verified fixes (P4 shipped; P6 `$141`), zero broken code shipped. DB byte-unchanged since the S33 close.

---

## Day 0 — Kickoff + Day-0 traces + control probes → GO (2026-07-20)
GO/NO-GO GREEN (`git diff 750803b2..HEAD -- src/ scripts/` empty; DB md5 byte-identical to baseline). Re-confirmed all four Phase-0 fingerprints exactly: mine CASE_B `stat_x(3,1,1)` 2.37, fawley CASE_B `stat_bq` 0.973/473, camcge `stat_tm` MS-4 Walras, rocket CASE_C_OBJDEF `stat_ht(h0)` 1.0. `DAY0_TRACE_NOTES.md`.

## Day 1 — P1 mine Phase-0 control → **REPLAN (H3′)** (2026-07-20)
The pre-`src/` cold-MS-1 control refuted H_dual: mine's head-offset dual boundary is `x.m=0`-degenerate; no keying-invariant emit change reaches cold MS-1. Task-9 P1-High-prior REPLAN realized → the deeper head-offset dual subsystem (dedicated effort). No `src/`. `DAY1_PROGRESS_NOTES.md`.

## Day 4 — P4 max-convention bound-transfer-sign → **SHIPPED (Option B); no +Solve** (2026-07-20)
Made the `--nlp-presolve` bound-multiplier warm-start transfer objective-sense-aware (`_emit_nlp_presolve`): for MAXIMIZE, drop the min-convention sign gate, keep the active-bound position gate, transfer `= abs(var.m)`; **MINIMIZE emit byte-identical**. The agreste `/tmp` +Solve survey stayed MS-5 (structural, the P6 double-`solve` driver) → no +Solve, the a-priori documented outcome. 11 MAXIMIZE presolve goldens regenerated; `--resolve-changed` GO. The firm value = the general MAXIMIZE warm-start-correctness fix. `DAY4_PROGRESS_NOTES.md`.

## Day 5 — P3 fawley constraint-index-diagonal → **DEFER** + Checkpoint 1 GO (2026-07-20)
Re-confirmed the qsb/pbal `sameas` over-sum gap live; the fix surface is a constraint-index-diagonal change in the ~1430-line `_add_indexed_jacobian_terms` (a dozen `sameas` paths, shared with mbal/cesam2/camcge/ps2) — high blast radius for **zero in-sprint bucket** (fawley H-b: sameas + all bound-transfers → warm residual ~0 but MCP still MS-5 @ 4399.557). Deliberate risk/reward DEFER (the design's own gate-leak exit), not a correctness REPLAN. Checkpoint 1 GO. `DAY5_PROGRESS_NOTES.md`.

## Day 6 — P2 sarf three-site symbolic emit → **REPLAN (scope/risk)** (2026-07-21)
Re-confirmed the three enumeration sites (S1 `acost3` body-diff · S2 `enumerate_variable_instances` materializing 369,024 `task` columns · S3 per-column `stat_task`) + the absent variable-blowup gate. `enumerate_variable_instances` is foundational (builds the `col_to_var` index the whole Jacobian→gradient→stationarity flow iterates for all 142 models) → making `task` symbolic is a coordinated corpus-wide re-architecture (a new parametric cross-term path), atomic, 20–28 h, for the lowest-leverage bucket (+1 Translate). REPLAN (design sound, scope/risk) → dedicated effort. No `src/`. `DAY6_PROGRESS_NOTES.md`.

## Day 10 — P5 camcge Epic-5-deferred + rocket → Sprint-35; Checkpoint 2 GO (2026-07-21)
The S1∧S2∧S3 detector cohort confirmed live (camcge cold MS-4 @ omega 191.7346; the four CGE siblings cold MS-1 → fires only camcge). The full Walras-law dual redefinition is Epic-5 research (banked price-pin MS-4 + 3+ sprints failed → MS-1 a-priori refuted); camcge stays `model_infeasible`. rocket Case-c re-confirmed (CASE_C_OBJDEF, dual CONSISTENT); the FINALIZED PATH-consultation input submitted to Sprint-35. Checkpoint 2 GO. No `src/`. `DAY10_PROGRESS_NOTES.md`.

## Day 11 — P6 failure-cohort re-triage; the `$141` fix verified + banked (2026-07-21)
Compiled the whole `path_syntax_error` cohort live and **corrected the prep diagnosis**: the ganges/gangesx `$141`/`$145`/`$149` are **three independent roots**, not one, and **no cohort model recovers** from the `$141` fix. `$141` (the `.l`-calibration NaN-cleanup self-reference) fix written + verified (removes all 15) but **banked** (0 bucket; touches only slow-emit CGE goldens un-regenerable in the CI budget). `$149` = a deep CES/LES product-rule stationarity uncontrolled-index AD bug (gates ganges/gangesx/dinam/indus/turkpow/clearlak); turkey is a distinct `$161` dotted-tuple set-emit root. The de-risked hand-off is banked. No `src/`. `DAY11_PROGRESS_NOTES.md`.

## Day 12 — P7 infra: P4 fixture + floor recompute (maintain 75) + SUMMARY row-34 (2026-07-22)
Added the one property fixture whose track shipped `src/` (`test_p4_maximize_bound_transfer_sense_aware` + `shape_p4_max_bound_transfer.gms` — fail-before/pass-after on the sense-aware `abs(var.m)` transfer). shape12/13/fawley-2-D fixtures correctly deferred (P1/P2/P3 didn't land); no P6-recovered fixture. Genuine-floor recompute: **maintain 75** (P4 is warm-start-only → 0 floor; the ≥ 76 step was contingent on mine/fawley, both REPLAN'd/deferred). Epic-4 `SUMMARY.md` row-34 filled + rows 35/36 reconciled. `make test` 5037 passed. Tests + docs. `DAY12_P7_INFRA.md`.

## Day 13 — Final retest + closeout (2026-07-22)
**Determinism ✅ ×3 `{0,1,42}`** — 5 representative models (3 P4-MAXIMIZE-presolve + 2 cold) byte-identical across seeds. **Final `--resolve-changed --since-commit 750803b2` GO** — the 11 P4 goldens (the sprint's only emit change) held their bucket; DB byte-unchanged. **PR25 genuine-vs-methodology re-baseline: genuine floor 75** (63 cold + 12 genuine-presolve; methodology 21; all-219 Match 96). Closeout: this log + `SPRINT_RETROSPECTIVE.md` + `SPRINT_35_CARRYFORWARDS.md`; SUMMARY row-34 filled (Day 12). `SPRINT_RETROSPECTIVE.md`.

---

## Per-priority summary

| Priority | Track | Disposition | Bucket | `src/` |
|---|---|---|---|---|
| P1 | mine head-offset dual | REPLAN (H3′ — `x.m=0` degeneracy, cold-MS-1 refuted) → dedicated effort | 0 | none |
| P2 | sarf symbolic `stat_task` | REPLAN (scope/risk — corpus-wide re-architecture) → dedicated effort | 0 | none |
| P3 | fawley constraint-index-diagonal | DEFER (risk/reward — H-b, ~1430-line blast radius) → dedicated effort | 0 | none |
| P4 | max-convention bound-transfer-sign | **SHIPPED** (Option B, sense-aware `abs(var.m)`; MINIMIZE byte-identical) — general warm-start correctness, no +Solve | 0 | `emit_gams.py` |
| P5 | camcge Walras / rocket PATH | Epic-5-deferred (detector cohort confirmed) / Sprint-35 submission | 0 | none |
| P6 | ganges/gangesx `$141` cohort | Re-triage — 3 independent roots; `$141` fix verified + **banked**; `$149` deep AD hand-off | 0 | none (banked) |
| P7 | infra | P4 fixture + floor-75 recompute + SUMMARY row-34 | — | tests |

# Sprint 35 — Day-0 Baseline Metrics + Genuine-Floor Re-Baseline

**Created:** 2026-07-23
**Prep Task:** 2 (Sprint 34 → Sprint 35 Day-0 Baseline + Genuine-Floor Re-Baseline — PR15 + PR17 + PR25)
**Day-0 code anchor:** `78ceaeadb5cebe422cd4343f56b8bb15096ee169` — the Sprint 34 close merge (PR #1602, `Merge pull request #1602 from jeffreyhorn/planning/sprint34-day13-close`)
**Day-0 tree:** `78b81615d1b8178d48d74030d4eaa680597e9482` (`main` at the S35 prep Task-1 merge, PR #1604)
**DB:** `data/gamslib/gamslib_status.json` (schema 2.2.1), md5 `6166acab90dcaff8789255f8ada83c54`

---

## 1. Summary

Sprint 35's Day-0 baseline **equals the Sprint 34 close** — recomputed from the committed DB and byte-for-byte reused (no fresh retest), because there is **no `src/`/`scripts/` drift** since the S34 close:

```
git diff --quiet 78ceaead..HEAD -- src/ scripts/   →  clean (no drift)
```

| Metric (142 convex-candidate corpus) | Day-0 | Sprint 35 target |
|---|---|---|
| Parse | **142** | maintain 142 |
| Translate | **135** | maintain ≥ 135 (stretch +1 → 136 via #1385 sarf, P2) |
| Solve | **108** (64 cold + 44 presolve) | maintain ≥ 108 (+1–4 via mine [P1] / fawley-forcing [P3] / ganges·gangesx [P4] / camcge [P5-Epic5]; **stretch ≥ 112**) |
| Match (as-measured, 142) | **93** | maintain ≥ 93 |
| genuine floor (PR25) | **75** | **≥ 76** (up to ≥ 78 if mine [P1] / fawley [P3] / ganges·gangesx [P4] cold-match) |
| model_infeasible | **7** | ≤ 7 (−1 per recovery) |
| path_syntax_error | **7** | ≤ 7 (**−2 → 5 via ganges/gangesx**, P4) |
| all-219 Match tally | **96** | (tracked; 93 candidates + 3 non-candidate) |
| Determinism | ✅ ×3 `{0,1,42}` | maintain |

**No change vs the Sprint 34 close** (the expected Day-0 state — the committed DB *is* the S34-close DB, and it has been byte-unchanged since the S33 close). Every Sprint-35 KPI delta is measured against this baseline and against the `--resolve-changed` code anchor `78ceaead`.

> ### ⚠️ Anchor note — the code anchor ADVANCES, the DB does not
>
> Sprint 34's anchor situation is **inverted** this sprint, and getting it wrong would silently invalidate every no-regression claim in the sprint.
>
> - The **DB is byte-unchanged since `750803b2`** (the S33 close). Its last modifying commit is still `1568a531` ("Sprint 33 Day 11 (P6): sample recovered"), and `git diff --quiet 750803b2..HEAD -- data/gamslib/gamslib_status.json` is clean. Sprint 34 closed **full modal-flat, 0 bucket moves**, so it never touched the DB.
> - But **`src/` DID change during Sprint 34.** Exactly one `src/` commit landed — `b71da11a` "Sprint 34 Day 4 (P4): sense-aware bound-transfer sign (Option B)" — together with **11 regenerated presolve goldens** (agreste, camshape, cclinpts, fawley, korcge, otpop, polygon, ps2_f_s, ps2_s, ps3_s_gic, rocket).
>
> Therefore `750803b2` is **historical** for `--resolve-changed` purposes: re-using it would re-flag those 11 P4 goldens as "changed" on every checkpoint. The Sprint-35 Day-0 code anchor is the **S34-close SHA `78ceaead`**. *The DB may be reused; the anchor may not.*

---

## 2. Day-0 anchor + provenance verification

### 2.1 Code anchor derivation (portable)

The Sprint-33 close merge body ended with the literal string `SPRINT 33 CLOSED`, so Sprint 34's derivation grepped for it. **The Sprint-34 close merge does NOT contain "SPRINT 34 CLOSED"** — its subject is `Merge pull request #1602 from jeffreyhorn/planning/sprint34-day13-close` and its body is "Sprint 34 Day 13: Final retest + CLOSE — full modal-flat (0 bucket moves, Solve 108/Match 93/floor 75)". Bumping the number in the old pattern yields an **empty** result, and an empty rev makes the drift check below (`"$S34"..HEAD` → `..HEAD` → `HEAD..HEAD`) pass **vacuously**. So the derivation matches the stable branch slug **or** the closeout text, case-insensitively, and guards for a non-empty result:

```bash
S34=$(git log --first-parent main -i -E --grep='sprint34-day13-close|Sprint 34 Day 13.*CLOSE' --format=%H -n 1)
[ -n "$S34" ] || { echo "ERROR: could not resolve the Sprint 34 close SHA (expected 78ceaead)"; exit 1; }
[ "$(git rev-parse --short=8 "$S34")" = "78ceaead" ] || echo "WARN: resolved $S34 != the recorded 78ceaead"
# → 78ceaeadb5cebe422cd4343f56b8bb15096ee169   (Merge pull request #1602 … planning/sprint34-day13-close)
```

*(The same generic form resolves `750803b2` for N=33, so it is back-compatible with the S33 close.)*

### 2.2 Drift check

```
git diff --quiet 78ceaead..HEAD -- src/ scripts/   →  clean
```

Safe to reuse the committed DB with **no fresh retest**. (`main` has advanced past the S34 close only by docs-only PRs: #1603 the PROJECT_PLAN Sprint-35 cascade, and #1604 the S35 prep plan + Known Unknowns + task prompts.)

### 2.3 `--resolve-changed` at Day 0

```
run_full_test.py --resolve-changed --since-commit 78ceaead --dry-run
→ GO: no emit goldens changed since 78ceaead
```

0 changed goldens ⇒ the Day-0 tree matches the anchor.

### 2.4 Determinism ×3 `PYTHONHASHSEED` {0,1,42}

Byte-identical emit spot-check across the carryforward set. **Every md5 also matches the value recorded at the Sprint-34 Day-0 baseline**, which independently confirms zero emit drift across the whole of Sprint 34 for these models:

| Model | md5 (×3 seeds) | vs S34 Day-0 | Verdict |
|---|---|---|---|
| mine (P1) | `a394cbc3dee15015aa099d7a84e0fa30` | identical | byte-identical ✓ |
| fawley (P3) | `d2eb48f11bdd2b6743151490ca993e6f` | identical | byte-identical ✓ |
| sample (S33 P6 recovery, cold match) | `cf7d631f9a4fbde68528aa630a6bea40` | identical | byte-identical ✓ |

> **Early P4/Task-3 signal.** A determinism run on **ganges** was attempted and **exceeded a 2-minute wall-clock budget per seed** without completing, so it is excluded from the spot-check above. This is the first live confirmation of the slow-emit CGE constraint that forced Sprint 34 to bank its verified `$141` fix (`SPRINT_34/DAY11_PROGRESS_NOTES.md`). Prep **Task 3** owns the measured budget (Unknown 4.5); this data point is handed to it, not resolved here.

---

## 3. Day-0 bucket tally (142 convex candidates)

`get_candidate_models` = the 142 models with `convexity.status ∈ {verified_convex, likely_convex}` (142 of 219 total). Recomputed from the committed DB (`mcp_solve.outcome_category` + `solution_comparison.comparison_status`):

| Bucket | Count | Definition |
|---|---|---|
| Parse success | 142 | `nlp2mcp_parse.status = success` |
| Translate success | 135 | `nlp2mcp_translate.status = success` |
| **Solve success** | **108** | `mcp_solve.status = success` = 64 `model_optimal` (cold) + 44 `model_optimal_presolve` |
| **Match** | **93** | `solution_comparison.comparison_status = match` |
| model_infeasible | 7 | `outcome_category = model_infeasible` |
| path_syntax_error | 7 | `outcome_category = path_syntax_error` |
| path_solve_license | 9 | `outcome_category = path_solve_license` |
| path_solve_terminated | 4 | `outcome_category = path_solve_terminated` |
| non-translate (no solve) | 7 | `outcome_category = None` (never reached solve) |

### Bucket members (enumerated)

- **model_infeasible (7):** `agreste`, `camcge`, `cesam`, `fawley`, `lnts`, `mine`, `rocket`
  *(P1 owns mine; P3 fawley; P5 camcge + rocket; P6 agreste/cesam/lnts)*
- **path_syntax_error (7):** `clearlak`, `dinam`, `ganges`, `gangesx`, `indus`, `turkey`, `turkpow`
  *(P4 owns ganges + gangesx [+ turkey `$161`]; P6 the remaining four)*
- **path_solve_terminated (4):** `dyncge`, `elec`, `tricp`, `twocge`
- **path_solve_license (9):** `egypt`, `ferts`, `glider`, `robot`, `shale`, `sroute`, `srpchase`, `tabora`, `tfordy`
- **non-candidate Match (all-219 minus the 142 corpus):** `ps2_f_s`, `ps2_s`, `ps3_s_gic` (3 → all-219 Match 96 = 93 candidate + 3 non-candidate)

Identical to the Sprint-34 Day-0 membership in every bucket — consistent with the S34 full modal-flat close (0 bucket moves).

---

## 4. Genuine-vs-methodology partition (PR25) — genuine floor 75

**Operational definition** (unchanged from PR25 / S32 / S33 / S34): the **methodology** set = `model_optimal_presolve` **AND** `comparison_status = match` whose **cold** MCP failed/mismatched (the warm-start was *required*) with the cold emit **byte-identical to its pre-fix state** — already-emit-correct models the broadened presolve-retry *validates*, not repeatable cross-term gains. The **genuine floor** = every other match: a cold match, OR a match whose cold emit a real fix *changed* (still genuine even if a non-convex model needs presolve to converge).

| Population | Count | Provenance |
|---|---|---|
| **Genuine, stable (floor)** | **75** | S28 genuine 68 **+1** S29 (maxmin `-1` #1447 + catmix) **+1** S30 (robert cold obj-grad) **+4** S31 (P2 #1111/#1112: polygon methodology→genuine + ps2_f_s/ps2_s/ps3_s_gic mismatch→genuine) **+1** S33 (P6 sample: `path_syntax_error` → cold match @ 726.679) **+0** S34 (P4 is warm-start-only — MINIMIZE emit byte-identical, so 0 floor by definition) |
| **Methodology-recovered** | **21** | `model_optimal_presolve` matches whose cold emit is byte-identical to pre-fix |
| **As-measured (all-219) Match** | **96** | 75 genuine + 21 methodology |

### 4.1 Reproduction from the committed DB

The partition is **fully reconstructed**, not asserted. The all-219 Match (96) splits by `outcome_category` into **63 cold** (`model_optimal`) + **33 presolve** (`model_optimal_presolve`). The 21 methodology members are all presolve matches, so 33 − 21 = **12 genuine-but-presolve-recovered**, and 63 + 12 = **75**. ✓

- **Methodology (21):** `cpack`, `etamac`, `harker`, `himmel16`, `irscge`, `like`, `lrgcge`, `marco`, `markov`, `mathopt1`, `mathopt3`, `mathopt4`, `mingamma`, `moncge`, `paperco`, `qsambal`, `sambal`, `stdcge`, `tforss`, `weapons`, `worst`
- **Genuine-presolve (12):** `bearing`, `camshape`, `catmix`, `cclinpts`, `launch`, `maxmin`, `polygon`, `ps2_f_s`, `ps2_s`, `ps3_s_gic`, `robert`, `robustlp`
  *(camshape + cclinpts = the S28 genuine presolve fixes; catmix + maxmin = S29; robert = S30; polygon + ps2_f_s/ps2_s/ps3_s_gic = S31; bearing/launch/robustlp = the residue of the S28 "6 non-methodology presolve matches")*

Cross-check: the 21-member methodology set matches the S31/S32/S33 enumeration exactly (the S31 list plus `mathopt3`, which those docs covered as "+ residue"). `sample` is **not** in either presolve list — it matches **cold** (`model_optimal`), so it sits in the 63.

**Genuine floor = 75** is the Sprint-35 Day-0 anchor. It spans candidates **and** non-candidates, so it is not a 142-corpus-only count.

### 4.2 Genuine-floor → ≥ 76 conversion map

Sprint-35 tracks that convert a non-matching candidate into a **genuine cold match** (+1 genuine floor each). Only a **cold-emit** change counts — the S34 P4 precedent is definitive: a warm-start-only fix yields **0** floor by definition, however correct it is.

| Track | Day-0 bucket | +1 genuine floor if… | Assessment |
|---|---|---|---|
| **ganges** (P4) | `path_syntax_error` | all three roots (`$141`+`$145`+`$149`) land and it cold-matches | **the firmest** — a cold-emit fix by construction; but S34 proved **no model recovers from one root alone**, so this is all-or-nothing (Unknown 4.4) |
| **gangesx** (P4) | `path_syntax_error` | same, verified **independently** (never inferred from ganges) | same, with the per-model discipline binding (Unknown 6.2) |
| **mine** (P1 #1443) | `model_infeasible` (MS 5) | the head-offset dual reconciliation cold-matches (infeasible → optimal) | **conditional** — four-times-carried, H_dual refuted, boundary `x.m = 0`-degenerate (Unknowns 1.1/1.2) |
| **fawley** (P3 #1111/#1112) | `model_infeasible` (MS 5, LP opt 2899.25) | the constraint-index-diagonal `sameas` correction cold-matches | **contingent** — fawley is **H-b** (MS-5 persists with the residual closed), so the +Solve is a forcing hand-off and the floor credit needs a cold match under H-b (Unknowns 3.3/3.4) |
| **camcge** (P5 #1330 → Epic 5) | `model_infeasible` (MS 4) | the dual-consistent Walras numéraire lands | **excluded** — Epic-5-scoped, explicitly *not* an in-sprint mover |

**Footnote-⁸ ramp alignment** (`PROJECT_PLAN.md` footnote ⁸, as renumbered by the Sprint-35 insertion): **S30 70 → S31 ≥ 73 → S32 actual 74 → S33 actual 75 → S34 actual 75** (the ≥ 76 step **missed** — full modal-flat) **→ S35 → ≥ 76 → S36 maintain ≥ 76 → S37 ≥ 77 → S38 ≥ 78.** Day-0 genuine floor **75** is the ramp's Sprint-35 anchor, and Sprint 35 re-targets the **≥ 76** step that Sprint 34 missed.

Per the Sprint-30 §3 lesson — borne out in S32, S33 and S34 — the genuine-floor ramp is **conditional, not a sequence of independent +1s**. Three consecutive sprints have front-loaded mine/sarf/fawley for zero bucket movement while the failure-cohort track produced the only genuine gain in that window (S33's sample). That makes **P4 (ganges/gangesx) the Day-0 favourite** to supply the ≥ 76 step; Task 11 owns the formal projection.

---

## 5. Per-model provenance for the 13 Sprint-35 target models (Day-0 → expected Day-13)

| Model | Priority | conv | Day-0 bucket | MS | Failure code | Expected Day-13 | Corpus |
|---|---|---|---|---|---|---|---|
| **mine** | P1 (Solve/floor) | verified_convex | model_infeasible | 5 | — | MODEL STATUS 1 (+1 Solve, +1 floor if it cold-matches) **OR** a documented deeper-architecture REPLAN | candidate |
| **sarf** | P2 (Translate) | verified_convex | non-translate (`translate.status = failure`) | — | translate blow-up (369,024 `task` columns) | translate (+1 Translate → 136) **OR** a documented re-scoping | candidate |
| **fawley** | P3 (floor) | verified_convex | model_infeasible | 5 | — | genuine `sameas` cold-emit correction (+1 floor **if** it cold-matches); **+Solve is H-b** → forcing hand-off | candidate |
| **ganges** | P4 (Solve/Match/floor) | likely_convex | path_syntax_error | — | `$141`×15, `$145`×3, `$149`×9 | model_optimal + match (+1 Solve/Match, −1 pse, +1 floor if cold) **OR** a documented residual blocker | candidate |
| **gangesx** | P4 (Solve/Match/floor) | likely_convex | path_syntax_error | — | same three roots (**verify independently**) | same, verified per-model | candidate |
| **camcge** | P5 (Epic 5) | likely_convex | model_infeasible | 4 | Walras rank-deficiency | stays model_infeasible (Epic-5-deferred; the `/tmp`-to-MS-1 Walras prototype is the Epic-5 gate) | candidate |
| **rocket** | P5 (PATH) | likely_convex | model_infeasible | 5 | Case-c (CASE_C_OBJDEF) | consultation input **submitted to Sprint 36**; +1 Solve conditional on forcing (not in-sprint) | candidate |
| **turkey** | P4/P6 (placement TBD) | likely_convex | path_syntax_error | — | `$161` (dotted-tuple set decl; its `$141`/`$257` are cascades) | root fixed **OR** re-triaged; P4/P6 placement decided in Task 5 | candidate |
| **dinam** | P6 (residual cohort) | verified_convex | path_syntax_error | — | `$140` + `$149` | `$149` half unblocked by P4; `$140` residual is per-model | candidate |
| **indus** | P6 (residual cohort) | verified_convex | path_syntax_error | — | `$140` + `$149` | same | candidate |
| **turkpow** | P6 (residual cohort) | verified_convex | path_syntax_error | — | `$149` + `$171` | `$149` half unblocked by P4; `$171` residual is per-model | candidate |
| **clearlak** | P6 (residual cohort) | verified_convex | path_syntax_error | — | `$149` + `$171` | same | candidate |
| **agreste** | P6 (re-triage) | verified_convex | model_infeasible | 5 | CASE_B `stat_sales`; double-`solve` scope | S34 P4 confirmed its MAXIMIZE divergence is **structural**, not warm-residual-driven (identical MS-5 with the sign-robust transfer) — re-triage only | candidate |

**Failure-code attributions** are carried from `SPRINT_34/DAY11_PROGRESS_NOTES.md` (the live compile diagnosis) and are **hypotheses to re-confirm per model at execution**, not facts — the standing lesson, and the exact assumption S34 got wrong. Prep Task 4 owns the live re-tabulation (Unknown 6.1).

---

## 6. Known Unknowns verified by this task

- **Unknown 7.2 (primary)** — ✅ **VERIFIED.** The Day-0 baseline = the S34 close (Solve 108 / Match 93 / genuine floor 75 / mi 7 / pse 7 / Translate 135 / Parse 142 / all-219 96); the PR25 anchor is **75**, reproduced from the DB (63 cold + 12 genuine-presolve, with both sets enumerated); the Day-0 code anchor **advances** to the S34-close SHA `78ceaead` (`750803b2` is historical: one `src/` commit `b71da11a` + 11 presolve goldens landed in that window, while the DB stayed byte-unchanged). `--resolve-changed --since-commit 78ceaead --dry-run` = **GO**.
- **Unknown 1.3 (Day-0-bucket aspect)** — ✅ mine is `model_infeasible` (MS 5) at Day 0, a `verified_convex` candidate, and its emit is byte-identical to the S34 Day-0 record (md5 `a394cbc3…`, determinism ×3). The *fingerprint / 22-row / +16000* aspect is Task 6's.
- **Unknown 3.3 (Day-0-bucket aspect)** — ✅ fawley is `model_infeasible` (MS 5) at Day 0, a `verified_convex` candidate, emit byte-identical to the S34 Day-0 record (md5 `d2eb48f1…`). Note the S34 P4 change **did** regenerate `fawley_mcp_presolve.gms`, so its *warm* path moved even though its cold emit did not — Task 8 must re-confirm the H-b figures (MS-5 @ 4399.557) against that. The *H-b* aspect is Task 8's.
- **Unknown 4.4 (Day-0-provenance aspect)** — ✅ ganges and gangesx are both `path_syntax_error` `likely_convex` candidates at Day 0 (never reached solve; `model_status = None`). The *recovery verdict* — whether all three roots are sufficient, verified independently per model — is Task 5's, and remains the open question S34 got wrong.

---

**Document Status:** ✅ Complete — Sprint 35 Prep Task 2
**Last Updated:** 2026-07-23
**Owner:** Sprint 35 Planning Team

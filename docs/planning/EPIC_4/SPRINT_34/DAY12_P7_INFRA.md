# Sprint 34 — Day 12 (P7 infrastructure + REPLAN-slack)

**Date:** 2026-07-22
**Branch:** `planning/sprint34-day12-p7-infra`
**Track:** P7 — property fixtures + genuine-floor tracking + Epic-4 `SUMMARY.md` continuation
**Scope (given the sprint's actual landings):** the **P4 MAXIMIZE bound-transfer fixture** (the one track that shipped `src/`), the **genuine-floor recompute** (maintain 75), and the **Epic-4 `SUMMARY.md` row-34** reconciliation + rows 35/36. The **shape12 / shape13 / fawley 2-D fixtures are correctly deferred** (P1/P2/P3 REPLAN'd/deferred — no fix to guard), and there is **no recovered-P6-model fixture** (P6 recovered nothing — the `$141` fix is banked). Tests + docs.

---

## 1. Property fixture — P4 MAXIMIZE bound-transfer (the one that lands)

The Day-4 (P4) Option-B fix made the `--nlp-presolve` bound-multiplier warm-start transfer **objective-sense-aware** (`_emit_nlp_presolve`, `src/emit/emit_gams.py`): for MAXIMIZE it drops the min-convention sign gate, keeps the active-bound position gate, and transfers `abs(var.m)` (MINIMIZE emit byte-identical). This shipped `src/`, so it gets a fail-before/pass-after guard.

- **Fixture:** `tests/fixtures/crossterm_shapes/shape_p4_max_bound_transfer.gms` — a MAXIMIZE NLP with an active lower bound on `x`.
- **Test:** `test_p4_maximize_bound_transfer_sense_aware` in `tests/integration/emit/test_ad_crossterm_shapes.py` (the `_emit` helper extended with `nlp_presolve=True`, passing the fixture as `source_file`). Asserts the emitted lower-bound transfer is `piL_x.l$(abs(x.l - x.lo) < 1e-6) = abs(x.m);` — **with** the `abs()` and **without** the `and x.m > 0` min-convention sign gate.
- **Fail-before:** the pre-fix path emits the min-convention form `piL_x.l$(… and x.m > 0) = x.m;` (no `abs`, with the sign gate) — the `else` branch that is still exactly the MINIMIZE path — so the assertion genuinely fails pre-fix and passes post-fix (the `is_max` branch *is* the P4 fix). Verified: the fixture emits the sense-aware form; the full `test_ad_crossterm_shapes.py` suite is 12 passed.

**Deferred (correctly — no landed fix to guard):** shape12 (head-offset dual → P1 REPLAN), shape13 (sarf symbolic `stat_task` → P2 REPLAN), the fawley 2-D second-index fixture (→ P3 DEFER), and any recovered-P6-model raw-emit fixture (P6 recovered nothing; the `$141` fix is banked). These re-arm when their tracks' fixes land (the S33 discipline: a fixture only lands with its fix).

## 2. Genuine-floor tracking recompute — **maintain 75** (the ≥ 76 step MISSED, modal-flat as projected)

Recomputed live from the committed DB (byte-unchanged since the S33 close — **no bucket moved this sprint**):

| Metric (142 convex candidates) | Day-0 (S33 close) | Day-12 (S34) |
|---|---|---|
| Solve | 108 | **108** |
| Match | 93 | **93** |
| Genuine floor (PR25) | 75 | **75** (maintained) |
| all-219 Match tally | 96 | **96** (63 cold + 33 presolve) |

**Why 75 holds (no +1):** the genuine floor advances only on a **genuine cold-emit correction** (a real fix that changes the cold MCP so it cold-matches — the S33 P6 sample precedent). Sprint 34's sole `src/` landing is **P4**, a `--nlp-presolve` **warm-start** correctness fix (MINIMIZE byte-identical; it improves the presolve-recovery substrate but does **not** change any cold emit → 0 floor). The ≥ 76 step was **contingent on mine [P1] / fawley [P3] cold-matching**, and both **REPLAN'd/deferred** — so the floor holds at 75, the **modal-flat outcome the Task-9 projection predicted** (BASELINE_METRICS §4 / footnote-⁸ ramp: S34 anchor 75, target ≥ 76). The all-219 Match partition is byte-identical to the S33 close (96 = 75 genuine + 21 methodology = 63 cold + 33 presolve). ✓

## 3. Epic-4 `SUMMARY.md` — row-34 reconciliation + rows 35/36

Per the Sprint-34 insertion, the pre-insertion row 34 (Quality / PATH-feedback) shifts out; Sprint 34's actual theme is the **S33 REPLAN'd/deferred carryforwards**:

1. **Row 34 filled** (rows-28–33 format {Theme / Headline KPIs / Firm landing(s) / REPLAN'd → carryforward}): theme = the S33 carryforwards; **Headline KPIs = Solve 108 / Match 93 / floor 75, all maintained — modal flat, 0 bucket move**; **firm landing = P4** sense-aware bound-transfer (general MAXIMIZE warm-start correctness, no +Solve); carryforwards = mine [P1 dual REPLAN] · sarf [P2 symbolic-emit REPLAN → dedicated] · fawley [P3 constraint-index-diagonal DEFER] · camcge [Walras → Epic 5] · rocket [→ Sprint 35 PATH consultation] · P6 ganges/gangesx [`$141` banked; `$149` deep CES/LES AD + `$145`] · turkey [`$161`].
2. **Row 35 reconciled** = the pre-insertion row-34 theme (Quality, performance & PATH-feedback integration, incl. the rocket PATH author consultation), `(planned)`.
3. **Row 36 added** = v2.0.0 release & Epic 5 planning (camcge dual-consistent Walras), `(planned)`.

## 4. Disposition

- **Tests-only + docs.** The P4 fixture (`*.gms` + one test) is the sole `src/`-adjacent change; the quality gate applies. No `src/` (`src/`) change — the emit is unchanged from Day 4.
- **`--resolve-changed --since-commit 750803b2` remains GO** (no emit/golden change on Day 12).
- **KPI unmoved (final Sprint-34 state):** Solve 108 / Match 93 / genuine floor 75 / model_infeasible 7 / path_syntax_error 7 — the full modal-flat close the Task-9 projection predicted.

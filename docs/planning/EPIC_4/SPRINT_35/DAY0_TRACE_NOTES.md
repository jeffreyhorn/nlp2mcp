# Sprint 35 — Day 0 Kickoff Trace Notes (PR24 fingerprint re-confirm + GO/NO-GO)

**Day:** 0 (Kickoff + Day-0 Traces + Control Probes) · **Date:** 2026-07-25 · **Owner:** Sprint 35 execution
**Day-0 code anchor:** `78ceaead` (S34 close) · **DB md5:** `6166acab90dcaff8789255f8ada83c54` · **Toolchain:** GAMS 53.1.0 (demo) · `.venv/bin/python`
**Verdict: ✅ GO for Day 1.** All Phase-0 fingerprints re-confirmed — **live** for the tracks that touch `src/` in-sprint (P4 compile, P1 mine, P3 fawley) and **spec-via-zero-drift** for the deferred tracks (P2 sarf, P5 camcge/rocket). Trace-only, no `src/`.

---

## 1. Baseline confirmation — Day-0 = S34 close (exact)

Recomputed from the committed DB (`get_candidate_models` = 142 convex candidates):

| KPI | Value | Detail |
|---|---|---|
| Parse | **142** | all candidates `nlp2mcp_parse.status=success` |
| Translate | **135** | `nlp2mcp_translate.status=success` |
| Solve | **108** | 64 `model_optimal` (cold) + 44 `model_optimal_presolve` |
| Match (142) | **93** | `solution_comparison.comparison_status=match` |
| all-219 Match | **96** | 93 candidate + 3 non-candidate |
| model_infeasible | **7** | agreste · camcge · cesam · fawley · lnts · mine · rocket |
| path_syntax_error | **7** | clearlak · dinam · ganges · gangesx · indus · turkey · turkpow |

Matches `BASELINE_METRICS.md` exactly. **Drift gate:** `git diff 78ceaead..HEAD -- src/ scripts/` is **empty** → the committed DB is reused byte-for-byte, no fresh retest. The 219 raw sources are present locally (so the compile probes below ran live).

## 2. P4 ganges/gangesx — the sole live bucket gate (LIVE compile probe)

The `$141` fix is correctly **not** in `src/` yet (built Day 1, not prep) — `_param_assignment_has_division:137` exists; the `_param_assignment_references_varref_attr` mirror does not. So the committed golden = the current pre-fix emit. Compiled each with `gams a=c` and counted `$code` occurrence-markers (GAMS concatenates adjacent codes, e.g. `$145$149`, so per-occurrence markers are authoritative, not the deduplicated description blocks):

| Model | `$141` | `$145` | `$149` | cascade |
|---|---|---|---|---|
| **ganges** | **15** | **3** | **9** | `$300`×1, `$257`×1 (solve-not-checked) |
| **gangesx** | **15** | **3** | **9** | `$300`×1, `$257`×1 |

**Exact match to Tasks 4/5** (`$141`×15 → 0 on the banked re-emit; `$145`×3; `$149`×9). GAMS reports 51 total errors/model (the 27 root markers + downstream cascade). Fix surfaces re-traced (hypotheses, PR24):
- **`$141`** → `src/emit/original_symbols.py:152` (`emit_post_assignment_na_cleanup`), the new skip mirroring `_param_assignment_has_division:137`. **Present as a surface; the fix itself is absent (correct — Day 1).**
- **`$149`** → `src/ad/derivative_rules.py:_diff_prod:3276` (Task 4), **NOT** `src/kkt/stationarity.py:_add_indexed_jacobian_terms:5861` (refuted). Hand-derived cross-term `prod(j,(pc(j)/pc00(j))**ac(j,r)) * ac(i,r)/pc(i)`.
- **18-model prod-in-stationarity regression set** (must stay byte-identical, minus the two beneficiaries): camcge, hhmax, irscge, dyncge, lrgcge, moncge, **gangesx**, hhfair, splcge, **lmp2**, korcge, prolog, imsl, **ganges**, quocge, weapons, stdcge, twocge — 18 goldens contain `prod(`, lmp2 (the most-sensitive non-beneficiary) present. ✓

## 3. P1 mine — pre-refuted gate (LIVE harness)

`kkt_residual.py mine.gms`: **verdict `CASE_B`** (emit_bug), **dual transfer CONSISTENT** (max comp infeas 0.00e+00 rel, max equality residual 0.00e+00 raw), **max-residual row `stat_x(3,1,1)` rel 2.37 (raw −3.20e+04)**, dual scale 1.35e+04; top rows `stat_x(3,1,1) 2.37 · stat_x(1,3,1) 2.00 · stat_x(4,1,1) 1.33`. Byte-for-byte the banked `x.m=0`-degenerate signature — the whole keying/pairing space is value-invariant, **no candidate reaches cold-MS-1 @ 17500**, so **no `/tmp` control is warranted** and the exit (→ Sprint-36 PATH consultation) is taken. **`x.up=inf` BANNED.** 0 in-sprint `src/`.

## 4. P3 fawley — correctness-only, 0 bucket (LIVE harness)

`kkt_residual.py fawley.gms`: **verdict `CASE_B`**, **dual CONSISTENT** (equality residual 1.82e-12 raw), **`stat_bq(res-arab-l,fuel-oil)` rel 0.973** (raw ~473 = 0.973 × 486 dual scale) — the P3 constraint-index-diagonal target — while **`stat_trans(tr-2)` rel 1.00 (raw −488) is the *harness max***. This is Task 8's H-b strengthening confirmed live: the dominant residual is an **emit-correct non-emit** row, so fawley's +Solve divergence is non-emit → the +Solve is a Sprint-36 `--force` survey, out of P3 scope. P3 stays a low-priority correctness-only landing (`max|stat_bq|` scoped `→ 0`), **must not displace P4/P6**. Surface hypothesis: the constraint-index-diagonal `$(sameas(cfq__,cf))` predicate in `_add_indexed_jacobian_terms` (`src/kkt/stationarity.py:5861`, distinct from #1049 `:7176`).

## 5. P2 sarf / P5 camcge / rocket — deferred (spec via zero-drift)

No `src/` this sprint, so the zero-drift proof (§1) guarantees these fingerprints are unchanged from the prep measurements (Tasks 7/9); not re-solved live.
- **P2 sarf** — O(active = 398)-not-369,024; measured baseline > 303 s. DEFER'd → dedicated effort; Translate holds 135 (no +1).
- **P5 camcge** — the S1∧S2∧S3 detector (`scripts/diagnostics/check_presolve_divergence.py` present); expected **MS-4** at omega 191.7346 → Epic-5 per-model-numéraire fallback. Excluded from the in-sprint Solve target.
- **rocket** — `CASE_C_OBJDEF`, dual CONSISTENT, clean at the NLP point → Sprint-36 hand-off. The Case-c sign flip stays **BANNED** (4×-refuted).

## 6. P6 residual cohort — LIVE compile probe (Days 6–7 preview) + one discrepancy flagged

| Model | codes (occurrence markers) | Task 4 catalog | reconcile |
|---|---|---|---|
| turkey | `$161`×6 (+cascade `$257`) | `$161` dotted-tuple | ✓ |
| dinam | `$140`×5, `$149`×3, `$171`×2 (+`$141`×1, `$37`, `$8`) | `$140`+`$149` | ✓ (+`$171` residual) |
| indus | `$140`×5, `$141`×8, `$149`×3, `$148`×2, … | `$140`+`$149` | ✓ |
| turkpow | `$149`×1, `$170`×6, `$171`×5 | `$149`+`$171` | ✓ |
| **clearlak** | `$149`×1, **`$352`×4** | `$149`+**`$171`** | ⚠ **`$352` not `$171`** — Task 4's clearlak second-code is off; re-trace at Days 6–7 |

**This is a P6-scope item (Days 6–7), not the P4 gate** — it does not affect the P4 sequence or the Day-0 GO. Noted so the P6 day re-traces clearlak's actual second root (`$352`, not `$171`). (`$141`/`$149` also appear in these models — the corpus-wide `$141` emit fix would reduce them too, but only ganges/gangesx are `$149` product-rule beneficiaries.)

## 7. Cross-cutting gates

- **`--resolve-changed --since-commit 78ceaead --dry-run` = GO** — "no emit goldens changed since 78ceaead" (0 changed at Day 0). ✓
- **Determinism ×3** — deferred to the P4 emit days (Days 1–5), the per-emit-PR gate. The ganges emit is minutes-scale (DB translate 335 s — a slow-emit model, reconfirming Task 3's finding), so the ×3 seed sweep runs on the P4 PRs, not Day 0.
- **PR25 floor anchor = 75** (63 cold + 12 genuine-presolve; 21 methodology). The → +2 conversion map is **entirely P4-contingent and specifically on a *cold* match** (presolve-only = methodology = 0 floor).
- **Standing BANs restated:** `x.up=inf` (mine, the S31 measurement error); the objective-gradient sign flip (Case-c, refuted 4×). `modelstat` asserted before every objective read.

## 8. GO/NO-GO for Day 1

**✅ GO.** The baseline is exact, drift is zero, and every Phase-0 fingerprint re-confirmed — **live** for P4 (compile), P1 mine (harness), P3 fawley (harness); **spec-via-zero-drift** for P2/P5/rocket. The sole live bucket gate (P4) enters exactly as designed (`$141`×15 / `$145`×3 / `$149`×9 on both ganges and gangesx; `_diff_prod:3276` surface; the 18-model regression set intact). The one discrepancy found (clearlak `$352` vs the catalog's `$171`) is P6-scope for Days 6–7 and does not touch the P4 gate. **Proceed to Day 1: P4 `$141` + `$145` banked-root re-apply** (`prompts/PLAN_PROMPTS.md` §Day 1).

---

**Document Status:** ✅ Complete — Sprint 35 Day 0
**Last Updated:** 2026-07-25
**Owner:** Sprint 35 Execution Team

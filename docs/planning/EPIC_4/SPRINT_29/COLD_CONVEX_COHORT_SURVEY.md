# Sprint 29 Prep Task 3 — Cold-Convex Cohort Survey + Case-(b/c) Partition

**Status:** COMPLETE
**Completed:** 2026-06-24
**Owner:** Sprint planning (AD/KKT specialist)
**Priority gate:** sizes Priority 4; feeds the Phase-0 gates (Task 4) and the schedule (Task 10)
**Verifies:** Known Unknowns 4.1, 4.2, 4.3, 4.4

---

## 1. Objective + Method

Survey the warm-start-only cohort — the models that match **only** via the `--nlp-presolve` warm-start (their cold MCP fails or mismatches, so they *behave* non-convexly even though the DB convexity status labels all 30 as `likely_convex`/`verified_convex` — see §6) — and partition them into:

- **Case b** — a genuine **cold-emit bug** the warm-start masks (a localizable stationarity/complementarity residual at the NLP KKT point) → **fixable in Sprint 29**.
- **Case c** — **inherent non-convexity** (the emit is correct; the cold MCP is Locally Infeasible / converges to a different local optimum) → cold infeasibility is *expected* → Sprint 30 forcing strategies.

**Cohort definition (from the Day-0 DB `data/gamslib/gamslib_status.json`):**
`mcp_solve.outcome_category = model_optimal_presolve` **AND** `solution_comparison.comparison_status = match` → **30 models**, all in canonical scope (0 out-of-scope `ps*`/`abel`). This is the BASELINE_METRICS §2 set (the 24 "methodology-recovered" + the 6 non-methodology presolve matches camshape/cclinpts/bearing/launch/mathopt3/robustlp). `otpop/chakra/chenery/kand/srkandw` are correctly **excluded** — they match **cold** (`model_optimal`), not via presolve.

**Tool:** `scripts/diagnostics/kkt_residual.py <model>.gms --json OUT.json` (Sprint-28 KKT-residual harness; `--json` takes the report path — the human summary always also goes to stdout, so `--json` may be omitted entirely). It warm-starts the MCP from the NLP optimum (primal + dual transfer), runs an `iterlim=0` residual evaluation, and emits the Case-(a/b/c) verdict + per-row residuals + a `--no-cold-start`-free Case-a-vs-c split. Verdicts:

| Verdict | Meaning | Disposition |
|---|---|---|
| **Case b** (`emit_bug`) | localizable non-zero stationarity residual at the NLP KKT point | **Sprint-29-fixable cold-emit bug** |
| **Case c** (`non_convexity`) | residual ≈ 0 **but** the cold (non-presolve) MCP is Locally Infeasible | emit correct → Sprint 30 forcing |
| **Case a** (`healthy`) | residual ≈ 0 **and** the cold MCP converges | emit correct, already cold-robust — no action |
| `dual_transfer_inconsistent` / harness abort | the warm-start transfer or residual MCP itself fails to build | **inconclusive** — needs a deeper trace (Task 4/9) |

Per-model JSON evidence: `/tmp/task3_kkt/<model>.json` (regenerable; not committed — analysis scratch).

---

## 2. Per-Model Harness Verdict (the cohort, ranked by residual)

| Model | Harness verdict | Max-residual row | Rel resid | DB convexity | Dual-transfer |
|---|---|---|---:|---|---|
| tforss | **Case b** (emit bug) | `stat_v` | 2.05e+03 | verified_convex | ✓ |
| cclinpts | **Case b** (emit bug) | `stat_fb` | 4.51e+01 | likely_convex | ✓ |
| markov | **Case b** (emit bug) | `stat_z` | 1.33e+01 | verified_convex | ✓ |
| robert | **Case b** (emit bug) | `stat_x` | 7.20e+00 | verified_convex | ✓ |
| marco | **Case b** (emit bug) | `stat_w` | 3.34e+00 | verified_convex | ✓ |
| harker | **Case b** (emit bug) | `stat_s` | 2.16e+00 | likely_convex | ✓ |
| stdcge | **Case b** (emit bug) | `stat_epsilon` | 2.03e+00 | likely_convex | ✓ |
| like | **Case b** (emit bug) | `stat_p` | 2.00e+00 | likely_convex | ✓ |
| himmel16 | **Case b** (emit bug) | `stat_area` | 2.00e+00 | likely_convex | ✓ |
| worst | **Case b** (emit bug) | `stat_d1` | 1.58e+00 | likely_convex | ✓ |
| camshape | **Case b** (emit bug) | `stat_r` | 1.02e+00 | likely_convex | ✓ |
| irscge | **Case b** (emit bug) | `stat_pz` | 1.00e+00 | likely_convex | ✓ |
| lrgcge | **Case b** (emit bug) | `stat_pz` | 1.00e+00 | likely_convex | ✓ |
| maxmin | **Case b** (emit bug) | `stat_mindist` | 1.00e+00 | likely_convex | ✓ |
| moncge | **Case b** (emit bug) | `stat_pz` | 1.00e+00 | likely_convex | ✓ |
| catmix | **Case b** (emit bug) | `stat_x1` | 9.52e-01 | likely_convex | ✓ |
| qsambal | **Case b** (emit bug) | `stat_x` | 7.80e-01 | likely_convex | ✓ |
| sambal | **Case b** (emit bug) | `stat_x` | 7.80e-01 | likely_convex | ✓ |
| etamac | **Case b** (emit bug) | `stat_c` | 7.26e-01 | likely_convex | ✓ |
| polygon | **Case b** (emit bug) | `stat_theta` | 4.92e-01 | likely_convex | ✓ |
| cpack | **Case b** (emit bug) | `stat_y` | 7.38e-02 | likely_convex | ✓ |
| paperco | _inconclusive_ (dual-transfer) | — | — | verified_convex | ✗ |
| weapons | _inconclusive_ (GAMS abort) | — | — | likely_convex | — |
| mingamma | Case a (healthy) | `stat_x2` | 4.39e-12 | likely_convex | ✓ |
| mathopt1 | Case a (healthy) | — | — | likely_convex | ✓ |
| mathopt4 | Case a (healthy) | — | — | likely_convex | ✓ |
| robustlp | Case c (non-convex) | `stat_v` | 7.80e-06 | verified_convex | ✓ |
| mathopt3 | Case c (non-convex) | `stat_x2` | 4.09e-11 | likely_convex | ✓ |
| launch | Case c (non-convex) | `stat_ms` | 1.45e-16 | likely_convex | ✓ |
| bearing | Case c (non-convex) | `stat_h` | 2.79e-17 | likely_convex | ✓ |

The residual axis separates cleanly: the Case-b residuals are **0.07 – 2052** (real localizable gaps), while Case-a/Case-c residuals are **≤ 8e-6** (numerically zero). There is no borderline noise — nothing sits just above the 1e-3 verdict threshold.

---

## 3. Partition + Counts

| Bucket | Count | Models |
|---|---:|---|
| **Case b** (Sprint-29-fixable cold-emit bug) | **21** | tforss, cclinpts, markov, robert, marco, harker, stdcge, like, himmel16, worst, camshape, irscge, lrgcge, maxmin, moncge, catmix, qsambal, sambal, etamac, polygon, cpack |
| **Case c** (emit correct; inherent non-convex → Sprint 30) | **4** | bearing, launch, mathopt3, robustlp |
| **Case a** (emit correct; already cold-robust → no action) | **3** | mingamma, mathopt1, mathopt4 |
| **Inconclusive** (harness-limited → re-trace Task 4/9) | **2** | paperco (dual-transfer infeasible), weapons (GAMS abort: `comp_minw.lam_minw` unmatched) |
| **Total** | **30** | — |

### 3a. ⚠️ Headline finding — the partition INVERTS the assumption

Unknown 4.1 assumed "a meaningful subset (≥ 2–4) are Case-b … and **the rest are Case-c**." The harness shows the **opposite**: **21 of 30 are Case-b**, only 4 are Case-c. The cold-convex cohort is **target-rich, not collapsing** — Priority 4 has many more fixable cold-emit bugs than planned.

**This also corrects BASELINE_METRICS §2's "these models were *always emit-correct*; the broadened retry now warm-start-*validates* them" claim.** That is true only for the 7 emit-correct models (4 Case-c + 3 Case-a). For the **21 Case-b**, the cold emit has a genuine stationarity bug — the production presolve emit *masks* it via the Layer-4 variable warm-start/fix, so they match warm despite a wrong cold stationarity row. → **feed this back to Task 8's re-baseline** (the methodology set is not uniformly emit-correct).

### 3b. The crucial caveat — Case b here is **Match-neutral**

All 21 Case-b models **already match (warm)**. Fixing their cold-emit bug makes them solve **cold** — that is **cold robustness**, raising the **genuine floor** (68 → up to ~89 if all 21 land), **not** headline +Match (per BASELINE_METRICS §3, a warm-match → cold-match is 0 net as-measured Match). A Case-b fix only moves the headline Match number if it *also* recovers a model that is currently `model_infeasible`/mismatch cold-only — none of these 21 are. **So the 21 Case-b ≠ 21 new Match.**

---

## 4. Shared-Shape Analysis (Unknown 4.2) — three fix-classes

The Case-b residuals cluster into three shapes. The recurring **exact-integer residuals (1.0, 2.0)** are the fingerprint of a *missing unit-coefficient cross-term* (the bare objective/defining gradient with the Jacobian-transpose `∑ multiplier` term absent), not a sign/scale artifact (which would give non-integer residuals). `dual_transfer.consistent = ✓` for all 21 confirms the residual is not a transfer artifact.

### Class A — objective/defining-variable cross-term (the maxmin shared shape) — **the best ROI**
A scalar or intermediate variable whose stationarity should couple a defining `=e=` multiplier to the objective; the cross-term is missing → residual ≈ the bare gradient.
- **maxmin** `stat_mindist` 1.0 (#1447 lead — `mindist` is the `max` objective var; `∑ lam_mindist1a` cross-term missing)
- **himmel16** `stat_area` 2.0 (`area(i)` couples `areadef(i)` + `obj2`)
- **like** `stat_p` 2.0 (`p(g)` couples the `like` objective + `pdef`)
- **catmix** `stat_x1` 0.95, **polygon** `stat_theta` 0.49 (#1143 offset-alias relatives), **camshape** `stat_r` 1.02 (a known genuine fix), **qsambal/sambal** `stat_x` 0.78
- **Hypothesis:** a single `src/kkt/stationarity.py` correction (the scalar/intermediate-var ← defining-`=e=`/objective Jacobian-transpose path) lands several at once. **maxmin is the confirmed lead + himmel16/like are clean confirmatory cases.**

### Class B — CGE price/numéraire family (camcge #1330 relatives) — **gate to Task 4, likely Epic 5**
- **irscge / lrgcge / moncge** `stat_pz` 1.0 (identical signature — `pz(j)` output-price var, `eqpzs(j)` defining row), **stdcge** `stat_epsilon` 2.0, **marco** `stat_w` 3.3
- These are the CGE-closure cohort that **camcge (#1330, Case-c degeneracy → Epic 5)** belongs to. The harness localizes a residual, but the price-normalization/Walras numéraire degeneracy may make the "fix" a closure change, not a clean stationarity correction. **Do not count as Sprint-29 wins until the Task-4 Phase-0 gate confirms a localizable fix (vs the camcge Walras-singularity Case-c).**

### Class C — model-specific large-residual Case-b
- **tforss** `stat_v` 2052, **cclinpts** `stat_fb` 45 (known genuine #1387), **markov** `stat_z` 13, **robert** `stat_x` 7.2, **harker** `stat_s` 2.16, **worst** `stat_d1` 1.58, **etamac** `stat_c` 0.73, **cpack** `stat_y` 0.074 — genuinely localizable, per-model fixes (no shared shape).

---

## 5. Sprint-29-Fixable Ranked List (Case b, by localizability)

Ranked for the Task-10 schedule: shared-shape + clean integer residual first (best ROI per fix-hour), CGE-family gated, model-specific last.

| Rank | Model | Row (resid) | Fix-class | Note |
|---:|---|---|---|---|
| 1 | **maxmin** | `stat_mindist` (1.0) | A | **lead — #1447 filed**; objective-var cross-term |
| 2 | **himmel16** | `stat_area` (2.0) | A | clean confirmatory; defining-`=e=` cross-term |
| 3 | **like** | `stat_p` (2.0) | A | clean; objective + `pdef` coupling |
| 4 | **catmix** | `stat_x1` (0.95) | A | clean |
| 5 | **polygon** | `stat_theta` (0.49) | A | #1143 offset-alias relative |
| 6 | camshape | `stat_r` (1.02) | A | known genuine; verify vs current emit |
| 7–8 | qsambal, sambal | `stat_x` (0.78) | A | identical signature pair |
| 9–13 | tforss, markov, robert, harker, worst | large resid | C | model-specific |
| 14–15 | etamac, cpack | `stat_c`/`stat_y` | C | smaller resid |
| — | irscge, lrgcge, moncge, stdcge, marco | `stat_pz`/`stat_epsilon`/`stat_w` | **B (gated)** | **CGE family — Task-4 gate before counting** |

**Deliverable check:** #1447 maxmin **confirmed** as the lead Case-b (`stat_mindist` rel = 1.0), and **≥ 1 additional Case-b confirmed** (himmel16, like, catmix, polygon — and 16 more). The "≥ 2 Case-b" prep target is exceeded by an order of magnitude.

---

## 6. Convexity-Seed Audit (Unknown 4.3)

- **The DB field is `convexity.status`, not `convexity.classification`** (the Unknown 4.3 assumption + its verification snippet name `classification`, which does not exist on the records).
- **Every one of the 30 cohort members is labeled convex** — 24 `likely_convex` + 6 `verified_convex`, **zero `non_convex`** — yet 4 are harness-**Case c** (genuine non-convexity) and 3 are borderline Case a. → **the DB convexity status cannot even flag the Case-c models**, so it is **useless as a Case-b/c seed for this cohort**.
- The "`verified_convex` that cold-fails ⇒ strong Case-b" heuristic holds *directionally* (of the 6 verified_convex: tforss/markov/robert/marco = Case b, paperco = inconclusive, **robustlp = Case c**) but is **not decisive** — robustlp is `verified_convex` yet Case c.
- **Conclusion:** the **harness Case-(a/b/c) verdict is authoritative**; the DB classification is a non-signal here and must be overridden by the harness whenever they disagree (which is essentially always — the DB labels all 30 convex).

---

## 7. Detector Soft-Classification (Unknown 4.4)

`scripts/diagnostics/check_presolve_divergence.py --model <m>` on the cohort sample (maxmin, catmix, himmel16, polygon):
- **No hard embedded-NLP divergence** (no abort / infeasible-embedded) on any.
- Informational `OBJ-GAP` only: himmel16 (embedded 0.674 vs ref 0.675, rel 0.001) + polygon (0.516 vs 0.7797, rel 0.264) — flagged "possibly a benign non-convex local optimum; review", **not** hard-fail.
- **Conclusion:** the detector correctly **soft-classifies** the cold-convex cohort — it will **not flood** the Day-5/Day-10 checkpoints with false hard-fails. No allowlist extension needed for the sampled models.

---

## 8. Budget Implication (feeds Task 4 + Task 10)

1. **Priority 4 is target-rich, not collapsing — the assumption's "mostly Case-c → free budget for P6/P7" is REFUTED.** 21 Case-b vs 4 Case-c. **Do not** pre-allocate freed P4 budget to Priorities 6/7 on a "P4 collapses" basis.
2. **But the 21 Case-b are Match-neutral** (already match warm). Their value is **genuine-floor lift** (68 → up to ~89) + **cold robustness**, *not* the as-measured Match target. Size Priority 4 by *how much genuine-floor conversion is worth* + *shared-fix ROI*, not by a +Match projection.
3. **The shared-shape clustering is the lever.** Fund **Class A** first (one `stationarity.py` fix-class plausibly clears maxmin + himmel16 + like + catmix + polygon + the `stat_x` pair — ~6–8 models for ~one fix's effort). **Gate Class B (the 5 CGE-family models) to the Task-4 Phase-0 gate** — they are likely the camcge (#1330) Walras degeneracy (Epic 5 / Sprint 30), not clean Sprint-29 wins.
4. **2 inconclusive** (paperco dual-transfer infeasibility; weapons harness MCP-matching abort) need a **harness-side trace** before disposition — assign to Task 4/9, do not count either way.
5. **Headline Match is still driven only by mine (#1443) + rocket (#1462) + hhfair (#1236)** (the `model_infeasible`/mismatch cold-only models) — unchanged by this survey. The cold-convex Case-b work is a *genuine-floor / robustness* track, reported separately per the PR25 re-baseline discipline.

---

## Appendix — Reproduction

```bash
# Enumerate the cohort into a space-separated shell variable
COHORT=$(.venv/bin/python - <<'PY'
import json
db=json.load(open("data/gamslib/gamslib_status.json"))
coh=[m["model_id"] for m in db["models"]
     if (m.get("mcp_solve") or {}).get("outcome_category")=="model_optimal_presolve"
     and (m.get("solution_comparison") or {}).get("comparison_status")=="match"]
print(" ".join(sorted(coh)))
PY
)
echo "cohort ($(echo $COHORT | wc -w) models): $COHORT"

# Per-model harness verdict (Case a/b/c + max-residual row)
for m in $COHORT; do
  .venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/$m.gms --json /tmp/$m.json
done
```

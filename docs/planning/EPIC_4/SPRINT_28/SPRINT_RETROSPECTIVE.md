# Sprint 28 Retrospective

**Sprint window:** 2026-06-12 (Day 0) → 2026-06-20 (Day 13)
**Day-0 baseline SHA:** `68be9cca` (Sprint 27 final; `git diff 68be9cca..HEAD -- src/ scripts/` was empty at Day 0, so Sprint 28 Day 0 = Sprint 27 final — no fresh baseline retest required).
**Final metrics (142-model GAMSlib corpus, Day-13 full retest):** Parse **142** · Translate **135** · Solve **107** (+2) · Match **92** (+30) · model_infeasible **7** · Tests **~4,935** · Determinism **byte-identical ×3 seeds** ✅
**Headline outcome:** **Match target ≥65 EXCEEDED → 92.** The +30 decomposes as **+7 genuine cross-term-fix matches** (camshape, otpop, cclinpts, chakra, chenery, kand, srkandw — documented + harness-verified), **~+24 methodology-driven** (the Day-9 #1387 PR broadened the presolve-retry to fire on cold-*mismatch*, not just STATUS-5; this warm-start-validates non-convex models that were *already emit-correct* — 22 of them byte-identical to Day-0), and **−1 stale-baseline correction** (rocket #1462, **not a regression** — see below). Genuine cross-term contribution = **+7, zero regressions**. **Solve missed** (stretch ≥110 / firm 109 → **107**, −2) and **model_infeasible missed** (≤5 → **7**, +2) — by exactly the two tracks REPLAN'd at their Task-6 gates (**mine #1443** deeper cold-infeasible LCP coupling; **camcge #1330** Epic-5 CGE Walras degeneracy) plus the rocket stale-baseline correction. Tests / Parse / Translate / Determinism **met**. **The Day-13 full retest revealed a stale Sprint-27 baseline (rocket #1462)** — a reminder that per-PR golden-stability checks don't substitute for a re-solve. Shipped four diagnostic/CI guards (KKT-residual harness, golden-staleness gate, embedded-NLP-divergence detector, AD cross-term property tests).

---

## What Went Well

1. **The KKT-residual harness (Priority 9) turned every REPLAN gate from a guess into an evidence-based decision.** The Case-(a/b/c) verdict + the dual-transfer self-check localized the max-residual row (or proved a structural singularity) for each gated track: **PROCEED** for #1387 cclinpts (anchor fix is local), #1390 kand (`stat_x(raw-2,time-1)` rel 1.04, CASE_B → localizable), and **REPLAN** for camcge (CASE_B `stat_mps` shown to be a fix-multiplier-transfer artifact; cold MS-4 singular signature = CGE Walras degeneracy). It also pinned otpop's final match gate as a *new* AD bug (#1452) once #1449 unblocked it. The gates were front-loaded (Days 1–3) so every subsequent priority day had the tool ready.

2. **Cascading AD cross-term fixes repeatedly fixed sibling models for free.** Each correct stationarity/AD fix supplied a missing cross-term that recovered a second model: cclinpts → **chakra** (#1387/#1455, `∂obj/∂c`), kand → **srkandw** (#1390 body-offset), and otpop's #1393 `kdef` fix corrected **chenery** to match. Of the **7 genuine cross-term-fix matches**, only 4 were the named carryforward targets (camshape, otpop, cclinpts, kand); 3 were bonus recoveries (chenery, chakra, srkandw) surfaced by the same fixes.

3. **The otpop chain showed disciplined incremental decomposition.** A single target decomposed into four landed fixes — #1393 (`kdef` scalar subset-sum over-count) + #1335 (`zdef` `card(t)-ord(t)` time-reversal cross-term) + #1449 (`--nlp-presolve` `$184` widened-param/`$include` conflict) + #1452 (`pdef` `ord(n)-1` cross-term) — each verified by the harness residual driving to ~0, ending at a clean `pi = 4217.7978` match in 0 PATH iterations from the warm start.

4. **Task-6 REPLAN discipline avoided sinking effort into inherent/architectural problems.** mine (#1443) and camcge (#1330) were REPLAN'd at their gates with *documented* causes — mine's correct MCP is still cold-infeasible (a convex LP whose KKT LCP PATH can't pivot cold, a `pr(k,l+1,i,j)` head-domain-offset dual-transfer misalignment plus deeper coupling), camcge's is an Epic-5 CGE Walras-law singularity (no price numéraire) — rather than forcing a fragile local patch. The harness made each REPLAN defensible, not a capitulation.

5. **The two systematic CI guards (Priority 8 + 10) proved their value immediately.** The golden-staleness gate caught a real **cross-platform byte non-determinism on indus** (macOS-stable but ubuntu-divergent, #1461) that the local run could not see; the embedded-NLP-divergence detector correctly flags the **korcge #1439** abort and was hardened (during PR review) from a noisy fresh-re-solve comparison into a DB-reference, hard-fail/soft-`obj_gap` design that doesn't false-flag non-convex local optima.

6. **Determinism held end-to-end.** The Day-13 3× `PYTHONHASHSEED` retest was byte-identical modulo wall-time, and #1400 (Sprint 11) removed the last machine-portability leak (repo-relative warning paths in the captured `message` field).

## What We'd Do Differently

1. **Three of the Solve/Match wins depend on the `--nlp-presolve` warm-start, not a cold-robust MCP.** otpop, cclinpts, and camshape match only because the pipeline's two-pass retry re-translates with `--nlp-presolve` and lands PATH at the NLP KKT point; their *cold* MCP is non-convex-infeasible. These are genuine matches (the warm-start is a first-class pipeline path), but cold-convex robustness for this class is unsolved and should be named as its own future track rather than implied by the headline count.

2. **mine's Task-6 gate over-scoped the fix.** The prep hypothesis "`stat_x` offset inversion ⇒ +1 Solve" was incomplete — the harness (Day 4) showed the cold MCP still MS-5 with `x → 4e10`, a deeper complementarity/bound coupling. The PR25 genuine-vs-bucket-forward tally correctly reclassified it as bucket-forward and the +1 Solve was re-scoped to #1443. Keep banking only genuine bucket-to-success transitions; the early projection had over-counted mine.

3. **The divergence detector's first cut was convexity-naive.** Comparing the embedded NLP to a *fresh cold re-solve* false-flagged five non-convex models (chain/agreste/fawley/cesam/rocket) as divergences, because a cold re-solve lands at a different local optimum. The review-driven redesign (DB reference + hard-fail only on abort/infeasible) fixed it — but convexity-awareness should have been a design premise, not a review finding, for any tool that compares two NLP solves.

4. **The Day-13 full retest is the only thing that caught the rocket stale baseline (#1462) — and the committed DB had been carrying a stale match for at least a sprint.** The Sprint-27 DB recorded rocket as `model_optimal_presolve` + match (1.0128), but the *actual* Sprint-27 golden **aborts (`EXECERROR=1`) on current `main`** — so the match never reproduced and rocket was already broken at Sprint-27 close. The Sprint-28 #1449 unfix only moved it `abort → MS5-infeasible` (forward), so this is **not a Sprint-28 regression** — but it exposes that **golden-stability checks (re-emit byte-identical) don't catch a broken *solve***, and that a recorded DB match can silently go stale across environment/emit drift without a re-solve. Recommend wiring a "re-solve the changed-golden set" step into the Day-5/Day-10 checkpoints (the golden diff is the exact at-risk list), not just golden-staleness, so a stale match surfaces mid-sprint rather than at the final retest.

5. **The Day-13 retest also revealed that the as-measured Day-0 baseline under-counted matches by ~24.** The Day-9 broadening of the presolve-retry to cold-mismatch lifted Match far beyond the projected genuine gains (62→92 vs a +6 genuine contribution). The projections (CP1/CP2: 63/67) were correct *as genuine-gain forecasts*, but the headline number conflates them with a methodology lift. Future sprints should re-baseline immediately after any pipeline-methodology change so the headline delta stays attributable.

## Sprint 29 Recommendations / Carryforwards

| Track | Issue | Carryforward |
|---|---|---|
| **mine +1 Solve** | **#1443** (OPEN) | Head-domain-offset (`pr(k,l+1,i,j)`) MCP infeasibility: the presolve dual-transfer should read `pr.m` at `l+1`, plus the deeper cold-infeasible complementarity/bound coupling under a convex LP. Re-scoped from #1224 (whose `stat_x` inversion landed). |
| **camcge** | **#1330** (OPEN → Epic 5) | Inherent CGE Walras-law degeneracy — `equil(i)` goods + `lmequil(lc)` labor market-clearing linearly dependent given budget balance, no price numéraire. Requires a CGE-domain structural transformation (single redundant-row drop + numéraire fix preserving the economic solution), not a general emit change. |
| **Translation timeout** | **#1385** (OPEN) | Option-1 short-circuit redesign — symbolic-instance cross-terms / atomic re-emit (the runtime-guard eq-body re-emit + `J_g^T·lam` cross-terms; deferred together since a re-emit without cross-terms is an inconsistent MCP). Deferred Day 11 per the PLAN slip guidance. |
| **rocket (stale baseline)** | **#1462** (OPEN, NEW) | rocket's Sprint-27 match (1.0128) was stale — the Sprint-27 golden aborts on current `main`. Not a Sprint-28 regression. Root cause localized: the `nu_*_fx_h0` `_fx_`-multipliers aren't warm-started (nonzero `stat_v('h0')` residual). Sprint-29 fix: warm-start `nu_<var>_fx_<idx>.l = <var>.m(<idx>)` (mirrors the piL/piU warm-starts) — necessary but not sufficient (MS5 persists at 1.016), then harness-investigate the residual non-convex convergence. |
| **Cold-convex robustness** | (new) | otpop/cclinpts/camshape (and the ~24 methodology-recovered models) match only via the `--nlp-presolve` warm-start; their cold MCP is non-convex-infeasible. Track cold robustness for this class separately. |

## KU Coverage Summary

All 🟡 design-scope Known Unknowns verified on their owning priority days: **9.1/9.2/9.3** (KKT-residual harness, Days 1–3); **1.2/1.3** (mine, Day 4 — gate found the hypothesis incomplete → #1443); **2.2/2.3** (camshape, Day 5); **3.2/3.3** (otpop, Days 6–7 + follow-ons); **4.2/4.3** (cclinpts, Days 8–9); **5.x** (kand, Day 10); **6.1** (camcge, Day 11 — gate → REPLAN); **8.2/10.1/10.2/10.3** (golden-staleness + divergence detector + AD property tests, Day 12). The headline Day-0 finding (the #1335 premise was partially wrong — the `card(t)-ord(t)` offset *does* evaluate for ∂/∂x; only ∂/∂p was dropped) is exactly the prep-surface correction the PR24 trace discipline exists to catch.

## Process Recommendations Delivery

- **PR24 (Day-0 traced fix-surface):** every priority had a Day-0 structural localization; the harness confirmed or corrected it on the priority day. Two corrections caught early (mine over-scope, #1335 ∂/∂p-only).
- **PR25 (genuine vs bucket-forward):** the tally was restated at Day 0 / Day 5 / Day 10 / Day 13; mine was correctly held as bucket-forward, camcge as no-transition. No over-count survived to the headline.
- **PR12 (determinism):** 3× `PYTHONHASHSEED` retest byte-identical; the golden-staleness gate now enforces emit reproducibility continuously (and flagged the indus cross-platform case, #1461).

## Related Documents

- `PLAN.md`, `BASELINE_METRICS.md`, `SPRINT_LOG.md`, `KNOWN_UNKNOWNS.md`
- Resolved (CLOSED): #1387, #1455, #1390, #1393, #1335, #1449, #1452, #1388, #1374, #1400
- Carryforwards (OPEN): #1443 (mine), #1330 (camcge → Epic 5), #1385 (translation timeout); new: #1462 (rocket presolve regression), #1461 (indus cross-platform emit determinism)

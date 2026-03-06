# Match Rate Improvement Analysis (Sprint 22 Prep Task 9)

**Created:** 2026-03-06
**Sprint:** 22 (Prep Task 9)
**Status:** Complete
**Data Source:** `data/gamslib/gamslib_status.json` (snapshot as of 2026-03-06 on `main`)
**Baseline:** 30/65 match (46.2%) — see BASELINE_METRICS.md

---

## 1. Executive Summary

Sprint 22 targets Match >= 35 (+5 from baseline 30). This analysis classifies the 35 non-matching models by divergence type to identify improvement opportunities and project Sprint 22 match rate.

**Key Findings:**

1. **7 verified_convex models mismatch** — these are strong KKT formulation bug indicators (for a convex NLP the optimal objective value is global, so any MCP/NLP objective divergence points to a formulation bug)
2. **7 principal-agent (ps*) models are non-convex** — multiple KKT points; not fixable through tolerance relaxation (Issues #958–#964)
3. **4 CGE models converge to identical MCP objective (25.508)** — likely a shared CGE-specific formulation issue
4. **5 models have MCP objective ~0** — likely missing objective terms or broken variable initialization
5. **Tolerance relaxation cannot recover any near-miss models** — even the closest (ps2_f_s at 0.5%) is 2.54x the threshold

**Sprint 22 Match Projection:**

| Source | Models | Confidence |
|--------|--------|------------|
| Baseline matches | 30 | Confirmed |
| Newly-solving verified_convex models | +5 to +8 | High |
| Newly-solving likely_convex models | +3 to +6 | Medium |
| Existing mismatch fixes (KKT bugs) | +2 to +5 | Medium |
| **Projected total** | **37–51** | — |

Sprint 22 target of >= 35 is **achievable** through newly-solving models from path_syntax_error and path_solve_terminated fixes alone, without fixing any existing mismatches.

---

## 2. Mismatch Model Classification

### 2.1 Classification Summary

| Category | Count | Models | Actionability |
|----------|-------|--------|--------------|
| A: KKT formulation bug (verified_convex) | 7 | aircraft, apl1p, apl1pca, jobt, mine, senstran, sparta | **High — should match; bug in KKT derivation** |
| B: Non-convex multi-optima (ps* family) | 7 | ps2_f_s, ps2_s, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp, ps10_s | Low — fundamentally different KKT points |
| C: CGE cluster (shared MCP objective) | 4 | irscge, lrgcge, moncge, stdcge | Medium — shared root cause |
| D: Missing/broken MCP objective | 5 | catmix, himmel16, mathopt1, polygon, qdemo7 | **High — likely emitter bug** |
| E: Large divergence (likely KKT bug) | 7 | abel, cclinpts, least, process, qabel, trig, weapons | Medium — diverse root causes |
| F: Moderate divergence (various causes) | 5 | chakra, chenery, circle, hydro, like | Low — model-specific issues |

### 2.2 Category A: KKT Formulation Bugs — Verified Convex (7 models)

These models are **verified_convex** (LP optimal with solver status 1), meaning the solver proved a global optimum. While convex problems (especially LPs) can have multiple optimal solutions, the optimal objective value is the same for all of them. Any MCP/NLP objective divergence is therefore a bug in the KKT derivation, not a multi-optima issue.

| Model | NLP Obj | MCP Obj | Rel Diff | Likely Root Cause |
|-------|---------|---------|----------|-------------------|
| apl1p | 24515.65 | 23700.15 | 3.3% | LP with complex constraint structure |
| senstran | 163.98 | 153.68 | 6.3% | Transportation model — likely index/domain issue |
| sparta | 3466.38 | 4959.35 | 30.1% | LP — significant divergence suggests structural KKT bug |
| apl1pca | 15902.49 | 23700.15 | 32.9% | Same MCP obj as apl1p — shared MCP bug |
| mine | 17500.00 | 29000.00 | 39.7% | LP — integer-like objective suggests constraint formulation error |
| jobt | 21343.06 | 81000.00 | 73.7% | LP — large divergence, likely missing constraints in KKT |
| aircraft | 1566.04 | 7332.50 | 78.6% | LP — 4.7x objective ratio, structural KKT error |

**Note:** apl1p and apl1pca converge to the same MCP objective (23700.15), suggesting a shared bug in how these related models are translated.

**Sprint 22 action:** Investigate 2–3 representative models (apl1p, senstran, jobt) to identify the KKT derivation pattern that produces incorrect MCP formulations for LP models. Fixing the shared root cause could recover 5–7 models.

### 2.3 Category B: Non-Convex Multi-Optima — Principal-Agent Family (7 models)

These 7 models (Issues #958–#964) share a non-convex revenue function `b(i) = x(i)**0.5` with multiple KKT stationary points. The NLP solver (CONOPT/IPOPT) and MCP solver (PATH) converge to different local optima from default initialization.

| Model | NLP Obj | MCP Obj | Rel Diff | Issue | Root Cause |
|-------|---------|---------|----------|-------|------------|
| ps2_f_s | 0.87 | 0.86 | 0.5% | #958 | Multi-solve warm-start loss |
| ps2_s | 0.87 | 0.86 | 0.5% | #959 | Multiple KKT points |
| ps3_s_mn | 1.05 | 1.03 | 2.2% | #963 | Multi-solve (3x sequential) |
| ps3_s_scp | -0.61 | -0.62 | 2.3% | #962 | Multi-solve + SCP constraints |
| ps3_s | 1.16 | 1.06 | 9.1% | #960 | Multiple KKT points (3x3 IC) |
| ps3_s_gic | 1.16 | 1.06 | 9.1% | #961 | Multiple KKT points (generalized IC) |
| ps10_s | 0.53 | 0.39 | 27.4% | #964 | Multiple KKT points (10x10 IC) |

**Mismatch grows with constraint complexity:** ps2 (0.5%), ps3 (2–9%), ps10 (27.4%).

**Sprint 22 action:** These are **NOT Sprint 22 priority**. Fixing requires multi-solve support (6–8h) or multi-start MCP (4–6h) — substantial infrastructure work better deferred to Sprint 23. The models are correctly classified as `non_convex` in the convexity framework.

### 2.4 Category C: CGE Cluster (4 models)

Four CGE (Computable General Equilibrium) models all converge to the same MCP objective value (25.508), despite having different NLP objectives. This strongly suggests a shared CGE-specific formulation issue.

| Model | NLP Obj | MCP Obj | Rel Diff |
|-------|---------|---------|----------|
| lrgcge | 25.77 | 25.51 | 1.0% |
| moncge | 25.98 | 25.51 | 1.8% |
| irscge | 26.09 | 25.51 | 2.2% |
| stdcge | 26.09 | 25.51 | 2.2% |

All are `likely_convex`. The identical MCP objective (25.508) across 4 different models is diagnostic — the MCP appears to converge to a "base case" equilibrium that ignores model-specific perturbations. Possible root causes:
- CGE models often use Walras' law with a numeraire — MCP may not preserve numeraire normalization
- Calibration parameters may be evaluated at wrong point
- The 4 models may share a common CGE template with model-specific overlays that are lost in translation

**Sprint 22 action:** Medium priority. Investigate one model (stdcge, simplest) to identify the CGE-specific pattern. A single fix could recover all 4 models.

### 2.5 Category D: Missing/Broken MCP Objective (5 models)

These models have MCP objective approximately zero while NLP objective is non-zero, or vice versa. This suggests missing objective terms, broken variable initialization, or emitter bugs.

| Model | NLP Obj | MCP Obj | Rel Diff | Likely Cause |
|-------|---------|---------|----------|-------------|
| mathopt1 | 1.00 | 0.00 | 100% | Objective variable not linked to MCP |
| polygon | 0.78 | 0.00 | 100% | Objective variable zeroed in MCP |
| qdemo7 | 1589042.39 | -0.00 | 100% | Massive objective lost — likely missing constraints |
| catmix | -0.05 | 0.00 | 100% | Small negative objective → zero |
| himmel16 | 0.68 | -0.00 | 100% | Objective → zero |

All are `likely_convex`. The zero MCP objectives suggest the objective function terms are not being properly included in the KKT formulation or the objective variable's stationarity equation is trivially satisfied.

**Sprint 22 action:** High priority for investigation. Examine mathopt1 (simplest) and qdemo7 (largest divergence) to identify the pattern. These are likely quick wins — emitter or KKT builder bugs.

### 2.6 Category E: Large Divergence — Likely KKT Bugs (7 models)

These models have large (>20%) relative divergence with diverse root causes. Not verified_convex, but the divergence magnitude suggests formulation bugs rather than multi-optima.

| Model | NLP Obj | MCP Obj | Rel Diff | Convexity |
|-------|---------|---------|----------|-----------|
| weapons | 1735.57 | 1361.56 | 21.5% | likely_convex |
| cclinpts | -3.00 | -9.96 | 69.9% | likely_convex |
| abel | 225.19 | 2557.43 | 91.2% | likely_convex |
| qabel | 46965.04 | 668024.80 | 93.0% | likely_convex |
| trig | 0.00 | 0.23 | 100% | likely_convex |
| least | 14085.14 | 21027.50 | 33.0% | likely_convex |
| process | 2410.83 | 1161.34 | 51.8% | likely_convex |

Notable patterns:
- **abel/qabel**: Related models (quadratic version) with >90% divergence — likely shared KKT bug
- **trig**: NLP obj ~0 but MCP obj 0.23 — may be a near-zero objective precision issue
- **cclinpts**: NLP was a solve_terminated model in Sprint 21 that now solves — may have pre-existing formulation issues

**Sprint 22 action:** Low-to-medium priority. Investigate abel (shared with qabel) for potential quick win.

### 2.7 Category F: Moderate Divergence (5 models)

These models have 5–25% divergence with model-specific causes unlikely to share a common fix pattern.

| Model | NLP Obj | MCP Obj | Rel Diff | Convexity |
|-------|---------|---------|----------|-----------|
| chakra | 179.13 | 177.87 | 0.7% | likely_convex |
| like | -1138.41 | -1218.44 | 6.6% | likely_convex |
| circle | 4.57 | 4.07 | 11.0% | likely_convex |
| hydro | 4366944.16 | 4975400.49 | 12.2% | likely_convex |
| chenery | 1058.92 | 839.77 | 20.7% | likely_convex |

**Sprint 22 action:** Low priority. Model-specific investigation only if time permits.

---

## 3. Known Unknown Verification

### KU-11: Non-Matching Models Are Primarily Multi-Optima Cases

**Status: PARTIALLY REFUTED**

The assumption that most divergence is from non-convexity/multi-optima is only partially correct:
- **7 models (20%)** are confirmed non-convex multi-optima (Category B: ps* family)
- **7 models (20%)** are verified_convex with KKT bugs (Category A) — these should NOT mismatch
- **5 models (14%)** have zero MCP objectives (Category D) — likely emitter bugs, not multi-optima
- **4 models (11%)** are CGE cluster with shared root cause (Category C)
- **12 models (34%)** have various causes (Categories E, F)

**Conclusion:** The 35 non-matching models have diverse root causes. Multi-optima (Category B) accounts for only 20%. KKT formulation bugs (Categories A, D) account for 34% and are the most actionable.

### KU-12: Combined Tolerance Formula Appropriateness

**Status: VERIFIED — TOLERANCE IS APPROPRIATE**

Analysis of the 10 nearest-miss models shows:

| Model | Abs Diff | Threshold | Ratio | Needed rtol |
|-------|----------|-----------|-------|-------------|
| ps2_f_s | 0.0044 | 0.0017 | 2.54x | 0.0051 |
| ps2_s | 0.0044 | 0.0017 | 2.54x | 0.0051 |
| chakra | 1.2666 | 0.3583 | 3.54x | 0.0071 |
| lrgcge | 0.2599 | 0.0515 | 5.04x | 0.0101 |
| moncge | 0.4739 | 0.0520 | 9.12x | 0.0182 |
| ps3_s_mn | 0.0227 | 0.0021 | 10.79x | 0.0216 |
| irscge | 0.5834 | 0.0522 | 11.18x | 0.0224 |
| stdcge | 0.5846 | 0.0522 | 11.20x | 0.0224 |
| ps3_s_scp | 0.0140 | 0.0012 | 11.27x | 0.0225 |
| apl1p | 815.50 | 49.03 | 16.63x | 0.0333 |

**Findings:**
- Even the nearest miss (ps2_f_s/ps2_s at 0.5% relative) is **2.54x the tolerance threshold**
- To match the nearest miss, rtol would need to increase from 0.002 to 0.005 (2.5x relaxation)
- The nearest misses are non-convex models (#958/#959) — relaxing tolerance would accept genuinely different KKT solutions as "matches," which would be mathematically incorrect
- No model is "almost matching" due to tolerance strictness — all mismatches represent genuinely different solutions
- The formula handles zero objectives correctly (atol catches the case) and large objectives correctly (rtol scales)

**Conclusion:** The current tolerance (rtol=2e-3) is appropriate. Relaxation would mask real formulation issues rather than recover valid matches. No tolerance changes recommended for Sprint 22.

### KU-13: Newly-Solving Models Will Mostly Match

**Status: PARTIALLY CONFIRMED — DEPENDS ON CONVEXITY**

Current match rates by convexity:
- **verified_convex**: 7/14 (50.0%)
- **likely_convex**: 23/51 (45.1%)
- **overall**: 30/65 (46.2%)

However, the 50% rate for verified_convex is misleadingly low — the 7 verified_convex mismatches are likely KKT bugs (Category A), not inherent MCP limitations. If those bugs are fixed, the verified_convex match rate would be 14/14 (100%).

**path_syntax_error model convexity (40 of 43 models in pipeline test set; 2 excluded, 1 non-convex):**
- verified_convex: 17 (42.5%)
- likely_convex: 23 (57.5%)

**path_solve_terminated model convexity (12 models):**
- verified_convex: 4 (33.3%)
- likely_convex: 8 (66.7%)

**Projection for newly-solving models:**
- Verified_convex models **should match at ~100%** (since proven convex NLPs have a global optimal objective value and we use a consistent KKT formulation between NLP and MCP) IF the KKT formulation is correct for their model type
- Likely_convex models should match at **45–70%** (accounting for non-convex models misclassified as likely_convex, and CGE/specialized model types)
- Conservative estimate: **50% match rate** for newly-solving models (consistent with current baseline)
- Optimistic estimate: **70% match rate** (if most newly-solving models are simple NLPs)

**Conclusion:** The Match >= 35 target requires +5 matches. If Sprint 22 adds +10 newly-solving models (from path_syntax_error and path_solve_terminated fixes), even a 50% match rate yields +5 new matches, meeting the target.

### KU-26: NLP Solution Data Available for All Models

**Status: PARTIALLY VERIFIED — COVERAGE IS LIMITED**

NLP `.lst` files tracked in `data/gamslib/raw/` in this repo: **0 files**

The `.lst` files are generated locally when running GAMSlib models via `gams <model>.gms` and are not committed to version control (`.gitignore` excludes them). During this analysis, 18 `.lst` files were present in the local workspace from prior pipeline runs, covering 5 of 35 mismatch models (14%). However, `gamslib_status.json` already contains NLP and MCP objective values extracted from pipeline runs, which is sufficient for the quantitative analysis performed here.

**Conclusion:** `.lst` coverage is local-only and insufficient for comprehensive variable-level divergence case studies. For deeper case studies, NLP solves can be run on demand for any model (`gams data/gamslib/raw/<model>.gms`, <1 min each). This is a minor inconvenience, not a blocker.

---

## 4. Sprint 22 Match Rate Projection

### 4.1 Match Improvement from Newly-Solving Models

Sprint 22's **committed** target is +10 new solves from path_syntax_error fixes (reducing from 40 to ≤30). Additional solves from path_solve_terminated (≤5 target, +7 models) and model_infeasible fixes (+3 models) represent **stretch** capacity, for up to +20 total new solves if all workstreams succeed.

**Projected new solves by source (potential capacity):**

| Source | Target | Convexity | Expected Match Rate |
|--------|--------|-----------|-------------------|
| path_syntax_error fixes | +10 (committed) | 17 VC + 23 LC | 50–70% |
| path_solve_terminated fixes | +7 (stretch) | 4 VC + 8 LC | 50–70% |
| model_infeasible fixes | +3 (stretch) | varies | 30–50% |

**Conservative projection (committed scope, 50% match rate):**
- +10 new solves × 50% = +5 new matches → **35 total (meets target)**

**Optimistic projection (all workstreams, 70% match rate):**
- +20 new solves × 70% = +14 new matches → **44 total (exceeds target)**

### 4.2 Match Improvement from Existing Mismatch Fixes

Additional matches possible from fixing existing mismatch root causes:

| Fix | Models | Effort | Confidence |
|-----|--------|--------|-----------|
| Category A (LP KKT bugs) investigation | 2–5 of 7 | 4–8h | Medium |
| Category D (zero MCP obj) investigation | 2–3 of 5 | 2–4h | Medium |
| Category C (CGE cluster) investigation | 0–4 | 3–5h | Low |

**Conservative from existing fixes:** +2 models (one Category A, one Category D fix)
**Optimistic from existing fixes:** +10 models (most A + D + C)

### 4.3 Combined Projection

| Scenario | New Solves | Match Rate | Existing Fixes | Total Match | Delta |
|----------|-----------|-----------|----------------|-------------|-------|
| Conservative | +10 | 50% | +2 | 37 | +7 |
| Expected | +15 | 60% | +3 | 42 | +12 |
| Optimistic | +20 | 70% | +7 | 51 | +21 |

**Sprint 22 target (>= 35) is achievable** in all scenarios, including the most conservative.

---

## 5. Recommendations for Sprint 22

### Priority 1: Focus on Solve Improvements (Primary Match Driver)

The most effective way to increase match count is to **add more solving models**. Each newly-solving model has ~50–70% chance of matching. Sprint 22's path_syntax_error and path_solve_terminated workstreams are the primary match improvement mechanism.

### Priority 2: Investigate Category A (Verified_Convex Mismatches)

The 7 verified_convex mismatches are definitive KKT bugs. Investigating 2–3 representative models (apl1p, senstran, jobt) could reveal a shared root cause pattern affecting LP models. If a single fix addresses the LP KKT derivation pattern, it could recover 5–7 matches with moderate effort (4–8h).

**Recommended investigation:** Day 8–10 of Sprint 22 (after primary solve improvements are complete).

### Priority 3: Investigate Category D (Zero MCP Objectives)

The 5 models with zero MCP objectives likely have emitter bugs (missing objective function terms). Investigating mathopt1 (simplest, obj=1.0 → 0.0) could reveal the pattern quickly. Effort: 2–4h.

**Recommended investigation:** Day 10–12 of Sprint 22 (lower priority than Category A).

### Not Recommended for Sprint 22

- **Category B (ps* non-convex):** Requires multi-solve support or multi-start MCP infrastructure (10–20h). Defer to Sprint 23.
- **Category C (CGE cluster):** Requires CGE-specific understanding. Investigate only if time permits after Categories A and D.
- **Category F (moderate divergence):** Model-specific, low leverage. Defer.
- **Tolerance relaxation:** Not recommended. Current tolerance is appropriate; relaxation would mask bugs.

---

## 6. Match Rate by Divergence Tier

For reference, the full 35-model breakdown by divergence magnitude:

### Near-Miss (<5% relative difference): 10 models

| Model | NLP Obj | MCP Obj | Rel Diff | Category |
|-------|---------|---------|----------|----------|
| ps2_f_s | 0.87 | 0.86 | 0.5% | B (non-convex) |
| ps2_s | 0.87 | 0.86 | 0.5% | B (non-convex) |
| chakra | 179.13 | 177.87 | 0.7% | F (moderate) |
| lrgcge | 25.77 | 25.51 | 1.0% | C (CGE cluster) |
| moncge | 25.98 | 25.51 | 1.8% | C (CGE cluster) |
| ps3_s_mn | 1.05 | 1.03 | 2.2% | B (non-convex) |
| irscge | 26.09 | 25.51 | 2.2% | C (CGE cluster) |
| stdcge | 26.09 | 25.51 | 2.2% | C (CGE cluster) |
| ps3_s_scp | -0.61 | -0.62 | 2.3% | B (non-convex) |
| apl1p | 24515.65 | 23700.15 | 3.3% | A (KKT bug) |

### Moderate (5–25%): 8 models

| Model | NLP Obj | MCP Obj | Rel Diff | Category |
|-------|---------|---------|----------|----------|
| senstran | 163.98 | 153.68 | 6.3% | A (KKT bug) |
| like | -1138.41 | -1218.44 | 6.6% | F (moderate) |
| ps3_s | 1.16 | 1.06 | 9.1% | B (non-convex) |
| ps3_s_gic | 1.16 | 1.06 | 9.1% | B (non-convex) |
| circle | 4.57 | 4.07 | 11.0% | F (moderate) |
| hydro | 4366944.16 | 4975400.49 | 12.2% | F (moderate) |
| chenery | 1058.92 | 839.77 | 20.7% | F (moderate) |
| weapons | 1735.57 | 1361.56 | 21.5% | E (large) |

### Large (>25%): 17 models

| Model | NLP Obj | MCP Obj | Rel Diff | Category |
|-------|---------|---------|----------|----------|
| ps10_s | 0.53 | 0.39 | 27.4% | B (non-convex) |
| sparta | 3466.38 | 4959.35 | 30.1% | A (KKT bug) |
| apl1pca | 15902.49 | 23700.15 | 32.9% | A (KKT bug) |
| least | 14085.14 | 21027.50 | 33.0% | E (large) |
| mine | 17500.00 | 29000.00 | 39.7% | A (KKT bug) |
| process | 2410.83 | 1161.34 | 51.8% | E (large) |
| cclinpts | -3.00 | -9.96 | 69.9% | E (large) |
| jobt | 21343.06 | 81000.00 | 73.7% | A (KKT bug) |
| aircraft | 1566.04 | 7332.50 | 78.6% | A (KKT bug) |
| abel | 225.19 | 2557.43 | 91.2% | E (large) |
| qabel | 46965.04 | 668024.80 | 93.0% | E (large) |
| mathopt1 | 1.00 | 0.00 | 100% | D (zero obj) |
| polygon | 0.78 | 0.00 | 100% | D (zero obj) |
| qdemo7 | 1589042.39 | -0.00 | 100% | D (zero obj) |
| catmix | -0.05 | 0.00 | 100% | D (zero obj) |
| himmel16 | 0.68 | -0.00 | 100% | D (zero obj) |
| trig | 0.00 | 0.23 | 100% | E (large) |

---

## 7. Cross-References

### Issue Documents
- Issues #958–#964: Principal-agent model family objective mismatches (Category B)
- BASELINE_METRICS.md: Full mismatch table with objective values
- PATH_SYNTAX_ERROR_STATUS.md: 40 path_syntax_error models (fix source for new matches)
- PATH_SOLVE_TERMINATED_STATUS.md: 12 path_solve_terminated models (fix source for new matches)
- PATH_SYNTAX_ERROR_FIX_DESIGN.md: Fix strategy for subcategories C, B, G
- MODEL_INFEASIBLE_TRIAGE.md: 15 model_infeasible models
- CONVEXITY_VERIFICATION_DESIGN.md: Convexity classification methodology

### KU Verification Summary

| KU | Status | Finding |
|----|--------|---------|
| KU-11 | **PARTIALLY REFUTED** | Multi-optima is only 20% (7 models). KKT bugs (Categories A+D) account for 34% and are more actionable |
| KU-12 | **VERIFIED** | Tolerance is appropriate. Nearest miss is 2.54x threshold. Relaxation would mask bugs |
| KU-13 | **PARTIALLY CONFIRMED** | ~50–70% match rate for new solves; depends on convexity. Target achievable with +10 new solves |
| KU-26 | **PARTIALLY VERIFIED** | No `.lst` files tracked in repo (local-only, 18 generated from prior runs). `gamslib_status.json` objective data is sufficient; on-demand NLP solves available for deeper analysis |

---

**Document Created:** 2026-03-06
**Next Steps:** Use findings for Task 10 (Sprint 22 Detailed Schedule) — prioritize solve improvements as primary match driver; schedule Category A/D investigation for Days 8–12

# Sprint 24 — Issue Fix Opportunities (Prioritized)

**Generated:** 2026-04-08
**Open issues:** 60 in `docs/issues/ISSUE_*.md`
**Current metrics:** parse 147/147, translate 140/147, solve 86, match 49
**Goal:** Identify low-hanging fruit for maximum model advancement per hour.

---

## Current Pipeline Breakdown

| Category | Count | Models |
|----------|-------|--------|
| model_optimal | 94 | (working) |
| path_syntax_error | 21 | china, clearlak, decomp, dinam, feedtray, ferts, ganges, gangesx, harker, indus, lmp2, otpop, partssupply, prolog, ramsey, sample, saras, tricp, turkey, turkpow, worst |
| path_solve_terminated | 15 | camcge, camshape, catmix, cclinpts, cesam2, dyncge, elec, etamac, fawley, gtm, hhfair, polygon, qsambal, sambal, twocge |
| model_infeasible | 11 | agreste, bearing, cesam, chain, chenery, korcge, lnts, mathopt3, pak, robustlp, rocket |
| path_solve_license | 8 | danwolfe, egypt, glider, robot, shale, sroute, tabora, tfordy |
| permanent_exclusion | 3 | orani, feasopt1, iobalance |
| translate_timeout | 6 | gastrans, iswnm, mexls, nebrazil, sarf, srpchase |
| translate_internal_error | 1 | mine |

---

## EASY FIX (< 1 hour effort)

High-confidence fixes with clear diagnosis, single-file changes, minimal regression risk.

| Priority | Issue | Model(s) | Current Status | Problem | Fix Description | Models Promoted |
|----------|-------|----------|----------------|---------|-----------------|-----------------|
| **E1** | #1178 | otpop | path_syntax_error | Malformed index expression in emitter | Fix index expression emission for specific pattern. Single emitter fix. | **1** (→ solve) |
| **E2** | #1179 | hhfair | path_solve_terminated | EXECERROR at runtime | Fix runtime execution error in pre-solve assignments. Emitter fix. | **1** (→ solve) |
| **E3** | #1192 | gtm | path_solve_terminated | Division by zero at runtime | Fix zero-division guard in emitted code. Emitter fix. | **1** (→ solve) |
| **E4** | #1195 | sambal, qsambal | path_solve_terminated | NA values in stationarity | Emit `$(param <> na)` guards for NA parameter values. | **2** (→ solve) |

---

## MEDIUM FIX (1–3 hour effort)

Well-understood patterns requiring parser/emitter/stationarity changes. Moderate cross-file impact.

| Priority | Issue | Model(s) | Current Status | Problem | Fix Description | Models Promoted |
|----------|-------|----------|----------------|---------|-----------------|-----------------|
| **M1** | #1133 | fawley | path_solve_terminated | Empty mbal equation — SetMembershipTest | Add 2D SetMembershipTest support in condition_eval.py or fix empty-equation multiplier fixup. | **1** (→ solve) |
| **M2** | #1041 | cesam2 | path_solve_terminated | Empty MCP pair (EXECERROR 486) | Fix conditioned stationarity equation pairing. Partially fixed already. | **1** (→ solve) |
| **M3** | #952 | lmp2 | path_syntax_error | Empty dynamic subsets — 3 compile errors | Emit loop-body parameter assignments for dynamic subset initialization. | **1** (→ solve) |
| **M4** | #882 | camcge | path_solve_terminated | 12 MCP matching errors — subset bound complementarity | Restrict comp equations to bound subset domain. 2 files. | **1** (→ solve) |
| **M5** | #1227 | prolog | path_syntax_error | Multiplier dimension mismatch lam_mp(i) vs lam_mp(i,t) | Fix spurious collapsed-dimension multiplier in stationarity builder. | **1** (→ solve) |
| **M6** | #1223 | worst | path_syntax_error | Conditioned equation zero stationarity (d1/d2 → 0=0) | Fix errorf differentiation or conditioned gradient propagation in AD. | **1** (→ solve) |
| **M7** | #1062 | tricp | path_syntax_error | 760 unmatched slp/sln variables | Condition stationarity on edge set; fix off-edge instances. | **1** (→ solve) |
| **M8** | #906 | twocge | path_solve_terminated | Missing SAM post-solve trade equations | Emit missing post-solve assignment block. | **1** (→ match) |
| **M9** | #1081 | sparta | model_infeasible | PATH locally infeasible — bal4 equation | Debug Jacobian for bal4 constraint. Near-feasible (< 0.01). | **1** (→ solve) |
| **M10** | #1105 | robustlp | model_infeasible | PATH convergence — diagonal parameter expansion | Improve initialization for degenerate starting point. | **1** (→ solve) |

---

## LONGER FIX (3–6 hour effort)

Larger scope, multiple interacting systems, or deep architectural changes.

| Priority | Issue | Model(s) | Current Status | Problem | Fix Description | Models Promoted |
|----------|-------|----------|----------------|---------|-----------------|-----------------|
| **L1** | #1137–#1146 | ~15 models | various (mismatch) | Alias-aware differentiation family | Deeper fixes to `_partial_collapse_sum` / Jacobian transpose for alias cross-terms. Partial fix in Sprint 24 Day 3-5. | **~5–15** (mismatch→match) |
| **L2** | #926–933 | 6 models | translate_timeout | Translation timeouts (LP/NLP combinatorial explosion) | LP-specific fast path or instance pruning for large models. | **~6** (→ translate) |
| **L3** | #1134 | rocket | model_infeasible | Jacobian explosion from lag-indexed equations | Lag-domain guard in constraint Jacobian for `∂v_eqn(h')/∂g(h)`. | **1** (→ solve) |
| **L4** | #1049 | pak | model_infeasible | Superset/subset domain stationarity incomplete | Architectural changes to handle domain-mismatch Jacobians. | **1** (→ solve) |
| **L5** | #1222 | decomp | path_syntax_error | Multi-solve Benders — equation marginals | Support `.m` attribute or detect multi-solve and skip. | **1** (→ solve or exclude) |
| **L6** | #1224 | mine | translate_internal_error | ParamRef index offsets (li(k)) | Support parameter-valued offsets or concrete expansion. | **1** (→ translate) |
| **L7** | #1228 | iswnm | translate_timeout | Empty set nb → instance explosion | Short-circuit unevaluable conditions with empty result instead of include-all. | **1** (→ translate) |
| **L8** | #1225 | kand | path_syntax_error (mismatch) | Multi-solve model — comparison target wrong | Fix comparison pipeline to use correct solve, or mark as multi-solve. | **1** (→ match) |
| **L9** | #871/#882 | camcge | path_solve_terminated | Division by zero + subset bound complementarity | Multiple interacting bugs. Partially fixed. | **1** (→ solve) |

---

## NOT FIXABLE (Known Limitations)

| Issue | Model | Current Status | Reason |
|-------|-------|----------------|--------|
| #765 | orani | permanent_exclusion | Linearized percentage-change CGE; structural incompatibility |
| — | feasopt1 | permanent_exclusion | GAMS test model; structural incompatibility |
| — | iobalance | permanent_exclusion | Balance model; structural incompatibility |
| #983 | elec | path_solve_terminated | Non-convex KKT; MCP correct but PATH can't solve |
| #927 | egypt | path_solve_license | Demo license limit (>300 equations) |
| — | danwolfe, glider, robot, shale, sroute, tabora, tfordy | path_solve_license | Demo license limit |

---

## Recommended Fix Order for Maximum Impact

**Phase 1 — Quick wins (Days 10-11, ~4-6h total, +4-6 models):**

1. **E4 (#1195)** — sambal/qsambal NA guards → **2 models**, <1h
2. **E1 (#1178)** — otpop index expression → **1 model**, <1h
3. **E2 (#1179)** — hhfair EXECERROR → **1 model**, <1h
4. **E3 (#1192)** — gtm division by zero → **1 model**, <1h

**Phase 2 — Medium wins (Days 11-12, ~6-8h total, +3-5 models):**

5. **M1 (#1133)** — fawley SetMembershipTest → **1 model**, 1-2h
6. **M5 (#1227)** — prolog multiplier dimension → **1 model**, 1-2h
7. **M2 (#1041)** — cesam2 conditioned stationarity → **1 model**, 1-2h
8. **M3 (#952)** — lmp2 dynamic subsets → **1 model**, 1-2h

**Phase 3 — High-leverage (Days 12-14, ~8-12h total, +5-15 models):**

9. **L1 (#1137-1146)** — alias differentiation family → **~5-15 models** (mismatch→match), 4-6h
10. **L2 (#926-933)** — translation timeouts → **~6 models**, 3-5h

**Expected cumulative impact:**
- Phase 1: solve 86 → ~90, match 49 → ~51
- Phase 2: solve ~90 → ~94, match ~51 → ~52
- Phase 3: solve ~94 → ~100, match ~52 → ~60+

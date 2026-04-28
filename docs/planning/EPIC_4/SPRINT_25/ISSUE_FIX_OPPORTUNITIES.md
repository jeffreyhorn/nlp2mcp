# Sprint 25 — Issue Fix Opportunities (Prioritized)

**Generated:** 2026-04-27 (Day 11 baseline, post-Day-10 #1278 merge)
**Open issues:** 73 in GitHub + 74 docs in `docs/issues/ISSUE_*.md` (some docs are
stale-OPEN for already-merged code fixes — see "Stale doc status" table at the end)
**Current pipeline (143-scope):** parse 143/143, translate 135/143, solve 106, match 54

**Goal:** Identify low-hanging fruit for maximum model advancement per hour over the
remainder of Sprint 25 (Days 11–14) and as queue for Sprint 26.

---

## Current Pipeline Breakdown (143-model scope)

The breakdown below uses the **143-model Sprint 25 active working set**. For
corpus context, the v2.2.1 exclusions (14 MINLP + 7 legacy + 2 multi-solve
driver = 23) reduce the 219-model corpus to 196 post-migration candidates; the
143-model scope here is the narrower working set tracked by this pipeline view
(53 of the 196 fall into additional gating beyond v2.2.1 — verified-non-NLP /
parse-not-attempted classes — and are not in the active Sprint 25 retest loop;
see `BASELINE_METRICS.md` for the full scope-reduction lineage).
These are the following **mutually exclusive terminal buckets**:

| Terminal Bucket | Count | Denominator / Notes |
|-----------------|-------|---------------------|
| translate failure | 8 | Overall 143-model scope (`143 - 135 translated`); 5 timeouts (iswnm, mexls, nebrazil, sarf, srpchase) + 3 internal_error (danwolfe, decomp, mine) |
| solve failure after translation | 29 | Translated subset (`135 translated - 106 solved`); 11 path_syntax_error + 10 path_solve_terminated + 7 path_solve_license; **AND** 8 model_infeasible (agreste, camshape, cesam, chain, fawley, korcge, lnts, robustlp) which classify as solve-failure even though PATH returned with a non-success status. ⚠ **Bookkeeping note:** the model_infeasible total of 8 plus the other three failure totals (11+10+7=28) sums to 36, but `135 - 106 = 29`, so the per-status subtotals currently overcount this bucket by 7 due to overlapping classifications in the status JSON. Some models appear in both `model_infeasible` and another solve-failure status, and the exact overlap remains open audit work for Day 11 baseline reconciliation. The 29 figure is the headline for "translated but did not solve"; the per-status totals are useful for triage but exceed 29 due to that overlap. |
| solve OK / mismatch | 46 | Solved subset; compared, but did not match: abel, catmix, cclinpts, chakra, chenery, china, circle, cpack, harker, hhfair, himmel16, imsl, irscge, kand, launch, like, lrgcge, marco, markov, mathopt1, mexss, mingamma, moncge, otpop, paperco, polygon, prodsp2, ps10_s, ps2_f_s, ps2_s, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp, qabel, qdemo7, qsambal, robert, sambal, spatequ, srkandw, stdcge, tforss, trig, weapons, worst |
| match | 54 | Solved subset; matched target |
| presolve-only / no_compare | 6 | Solved subset; bearing-class warm-start cases |

**Top-level identity check:** `8 (translate fail) + 29 (translated-but-not-solved) + 46 (mismatch) + 54 (match) + 6 (no_compare) = 143`. Solved = `46 + 54 + 6 = 106`.

_Sprint 25 targets: Translate ≥135, Solve ≥102, Match ≥60 (stretch ≥62)._

---

## SIMPLE FIX (< 2 hour effort)

High-confidence fixes with single-file or tightly-scoped changes, minimal regression risk.

| Priority | Issue | Model(s) | Current Status | Fix Description | Models Promoted |
|----------|-------|----------|----------------|-----------------|-----------------|
| **S1** | #1268 | (decomp,danwolfe — excluded; future single-model multi-solve) | excluded | Add missing `bound_scalar` / `bound_indexed` handlers to `_loop_tree_to_gams_subst_dispatch`; direct port from canonical dispatcher. Per-issue effort: 1–2h. | **0 immediate** (avoids future Error 140 silent-emission regressions for any single-model multi-solve script that reads `eq.m` / `var.l` inside a loop body) |
| **S2** | #1192 | gtm | path_solve_terminated | Runtime division by zero in stationarity (`supb/(supc-s)` with `supc=0` for 3 regions). Emit `$(supc(r) <> 0)` guard or initialize `s.l(r)` to feasible value. Single-file emitter touch. | **1** (→ solve, possibly match) |
| **S3** | #1243 | lmp2 | path_solve_terminated | Runtime div-by-zero in `stat_y` (`1/y(p)` from product-aggregate derivative undefined at `y.l=0`). Two options: (a) emit `y.l(p) = 1;` initialization; (b) emit `$(y(p) <> 0)` guard. | **1** (→ solve, partial — stacked with #1315) |
| **S4** | #1245 | camcge | path_solve_terminated | Runtime div-by-zero for non-traded elements (`pd(i)` zero for services/publiques). Condition stationarity on traded subset `it(i)` or emit `$(pd(i) <> 0)` guard. | **1** (→ solve) |
| **S5** | #1313 | qabel/abel/ganges (warm-start path only) | n/a (presolve flag) | `--nlp-presolve` writes dual-transfer lines BEFORE the `$include` of NLP source, so duals reference original equation symbols/marginals not yet in scope (e.g., `stateq.m(...)`); GAMS emits an Error 141 cascade. Reorder to: (1) `$include` first; (2) dual-transfer block second. | **0 immediate** (unblocks the warm-start verification path for non-convex models like abel; pairs with #1199 bearing-class) |
| **S6** | #1280 | mathopt4 | path_syntax_error | `nlp2mcp_uel_registry` emits unquoted UELs containing dots (`hu.bar`); GAMS rejects. Fix: unconditionally single-quote-wrap every UEL emitted to the registry. _Note: doc says OPEN but PR may have landed in Sprint 25 Day 1; verify before scheduling._ | **1** (→ solve) |
| **S7** | #1234 | otpop | mismatch | Scalar-constant offset `pd(tt-l)` with `l = /4/` not evaluated at IR-build; emitter produces `pd(tt-l)` instead of `pd(tt-4)`. Fix: resolve scalar-constant offsets in IR normalize or in emitter before stationarity. | **1** (→ match) |

**Subtotal:** ~7–10h, **+4–5 solve, +1 match** (plus 2 emitter-hardening side benefits).

---

## MEDIUM FIX (2–6 hour effort)

Well-understood patterns requiring parser / emitter / stationarity changes. Moderate cross-file impact, regression test required.

| Priority | Issue | Model(s) | Current Status | Fix Description | Models Promoted |
|----------|-------|----------|----------------|-----------------|-----------------|
| **M1** | #1290 | ferts | path_syntax_error | Multiplier names exceed GAMS 63-char identifier limit (e.g., `nu_some_long_eqname_eqname` = 67 chars). Fix: shorten name format (drop `nu_` prefix, use abbreviated hash, or cap-and-warn). 2–3h per issue doc. | **1** (→ solve) |
| **M2** | #1316 | turkpow | path_syntax_error | Table-data emission produces spurious entries when source rows have empty cells / `+inf` values, triggering Error 170 cascade post-#1292 line-wrap. Audit `_expand_table_key` or filter post-parse table data. | **1** (→ solve) |
| **M3** | #1315 | lmp2 | path_solve_terminated | Dynamic-subset SET assignments (`m(mm) = yes$(...)`) inside multi-solve loop body not extracted into `emit_pre_solve_param_assignments`. Extend to accept set assignments (currently only handles parameter assignments). Stacks with #1243. | **1** (→ solve) |
| **M4** | #1251 | twocge | path_solve_terminated | Empty trade equations when `r=rr` produce 8 MCP pairing errors (8 multiplier instances unfixed). Extend empty-equation detector to recognize `ord(r) <> ord(rr)` (and similar alias-comparison) conditions; emit multiplier `.fx` on the negated condition. _Now actionable post-Day-10 #1278 fix._ | **1** (→ solve, possibly match) |
| **M5** | #1291 | clearlak | path_syntax_error | Statement ordering: emitter hoists `tmp1 = sum(leaf, ...)` before `leaf(n) = yes` assignment, so sum iterates over empty set (observed compile errors: 352 set not initialized, 149 uncontrolled set, 141 no values assigned). Track set-init dependencies in statement-ordering graph. 3–4h. | **1** (→ solve) |
| **M6** | #1192+#1243+#1245 (combined "div-by-zero hardening") | gtm, lmp2, camcge, possibly elec | all path_solve_terminated | If S2/S3/S4 share a common emitter helper (emit `$(denom <> 0)` guard around any stationarity term that contains `/<param-or-var>`), do them as one shared change instead of three one-offs. | **3–4** combined |
| **M7** | #918 | qdemo7 | mismatch | Empty MCP equations for conditionally-absent variables. Likely related to dollar-condition propagation (#1112). Verify whether already addressed by Sprint 24/25 alias-AD work. | **1** (→ match) |
| **M8** | #919 | sroute | path_solve_license | Empty stationarity equations — KKT gradient failure. License-blocked downstream so no immediate model promotion, BUT fix may also recover other patterns. Skip unless investigating root cause for other models. | **0 immediate** (license-blocked) |
| **M9** | #1239 | sambal, qsambal | mismatch (massive; `1028 vs 3.97`) | Squared-deviation objective with NA-cleanup side-effects. Verify dollar-condition propagation in AD; check if `_diff` of a `$(param <> NA)` body is correctly handled. | **2** (→ match) |
| **M10** | #1236 | hhfair | mismatch (37%) | Product-aggregate + CES utility. Verify product derivative `_diff_prod` and check variable initialization. May couple with #1243 (product-aggregate `1/y(p)` issue). | **1** (→ match) |
| **M11** | #1247 | prolog | mismatch | After #1227 dimension fix, prolog now solves to a different KKT point (`-73.5 vs -0.0`). May be the same multi-model variant-selection issue as kand (#1225); investigate KKT structure correctness vs. comparison-target choice. | **1** (→ match) |
| **M12** | #970 | twocge | path_solve_terminated | MCP locally infeasible at warm-start (after the trade-equation fix #1251 lands and `model_infeasible` exposes the deeper issue). Requires per-instance debugging. _Schedule AFTER #1251 lands._ | **1** (→ solve, possibly match) |

**Subtotal:** ~30–40h if all addressed individually; ~20–25h if M6 is consolidated, **+8–12 solve, +5–7 match**.

---

## LONGER FIX (> 6 hour effort)

Larger architectural changes, deep AD/IR/emitter coupling, or open-ended investigation. Plan for Sprint 26 unless one is selected as a sprint-end stretch.

| Priority | Issue | Model(s) | Current Status | Fix Description | Models Promoted |
|----------|-------|----------|----------------|-----------------|-----------------|
| **L1** | #1111 (Pattern A core) | irscge, lrgcge, moncge, stdcge (#1138); meanvar (#1139); ps2_f_s, ps2_s, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp, ps10_s (#1140); cclinpts (#1145); qabel, abel (#1137 partial) | all mismatch | Multi-index `_partial_collapse_sum` concrete→symbolic recovery (Sprint 24's stubbed gap, per AUDIT_ALIAS_AD_CARRYFORWARD.md). Phase 1–2 of DESIGN_ALIAS_AD_ROLLOUT.md, ~10–15h with the regression matrix. | **~15** (mismatch → match), high variance — some are genuine non-convex mismatch (ps-family) and won't actually recover |
| **L2** | #1306 + #1307 (Pattern C remainder) | polygon (#1143), himmel16 (#1146), kand (#1141/#1225), launch (#1142/#1226), twocge (#1317) | all mismatch | Extend Pattern C consolidation to: (a) plain alias sums without `$`-condition (#1317 — twocge); (b) cyclic offset-aliases (#1146); (c) the `$ge(ss,s)` mis-scoped condition (#1307). The Day-6 launch-style gate is the foundation; ~6–10h of incremental gate widening + fixture validation. | **~3–5** (mismatch → match for those that aren't actually multi-model-comparison-target issues like kand) |
| **L3** | #1144 + #1147 (alias domain inference + compilation) | catmix, camshape | model_infeasible (catmix mismatch in earlier classification, now infeasible) | Alias domain inference regression: variables with aliased domains lose position info. Pattern A may subsume; verify after L1 lands. | **2** (→ solve / match) |
| **L4** | #1150 | (general AD regression class) | indirectly affects ~5+ alias-using models | AD engine: alias-aware differentiation collapses distinct sum indices in nested sums. Couples with L1; should be tested as part of Pattern A regression matrix. | **0 direct** (force multiplier for L1) |
| **L5** | #1112 | (general dollar-condition class) | indirectly affects ~5+ models with `$`-conditions | KKT: dollar-condition propagation through AD/stationarity pipeline. Affects M7 (#918 qdemo7), M9 (#1239 sambal), and possibly more mismatch cases where dollar-conditioned terms are silently dropped from the gradient. ~6–10h scoping + fix + regression. | **2–4** (→ match) |
| **L6** | #885 + #929 + #930 + #931 + #932 (translate timeouts) | sarf, ganges, gangesx, iswnm, nebrazil, mexls (#1185), srpchase | translate_timeout | All 5 hard-timeouts share the same root cause per PROFILE_HARD_TIMEOUTS.md: `SetMembershipTest` dynamic-subset fallback in `enumerate_equation_instances`. Unified Option-1 fix (short-circuit empty-subset fallback) per Sprint 25 Prep Task 8 design. ~4–6h coding + 2h regression on all 5 — fits Sprint 25 stretch. | **5** (→ translate; downstream solve gain ≤2 per Task 8 estimate) |
| **L7** | #1062 + #933 + #1038 (KKT structural pattern) | tricp, spatequ | path_solve_terminated / mismatch | Sparse edge-set conditioning in stationarity (760 unmatched slp/sln in tricp, similar in spatequ). Architectural; condition stationarity on edge set. ~6–8h. | **2** (→ solve/match) |
| **L8** | #1224 | mine | translate_internal_error | Parameter-valued index offsets (`i+li(k)`) unsupported. Either enumerate concrete instances at IR-build (combinatorial in worst case) or extend the IR's `IndexOffset` to accept `ParamRef`. ~6–8h. | **1** (→ translate) |
| **L9** | #1228 | iswnm | translate_timeout | Same family as L6; deferred to Sprint 26 per PROFILE_HARD_TIMEOUTS.md. Listed separately since the doc describes the iswnm-specific empty-set diagnosis. | (covered by L6) |
| **L10** | #1169 + #1185 | lop, mexls | translate_timeout | LP combinatorial-explosion class (Lange's profile). Either route LPs through a fast-path that skips the `compute_constraint_jacobian` enumeration, or add LP-specific instance pruning. ~6–10h. | **2** (→ translate) |
| **L11** | #1271 | (refactor — no model promotion) | n/a | Collapse `_loop_tree_to_gams` and `_loop_tree_to_gams_subst_dispatch` into one with optional `token_subst` kwarg. Eliminates the recurring "missing handler in subst dispatcher" bug class (#1268 was the most recent instance). 4–5h per DESIGN_SMALL_PRIORITIES.md. | **0 immediate**, prevents future regressions |
| **L12** | #1270 | saras (and 2–3 others) | mismatch (saras) | Multi-solve gate extension (Approach A: cross-reference `eq.m` reads against later solve constraint bodies). 3.5–4.5h. ~3–4 models flagged out of scope; saras is the only currently-broken one impacted. Likely net-negative on Match: gussrisk + sparta are confirmed must-NOT-flag canaries. | **0 net** (saras would be flagged, not promoted) |
| **L13** | #1283 (parser non-determinism) | chenery, indus, indus89, clearlak | model_infeasible / path_syntax_error | Non-deterministic table parsing for multi-row-label rows. Per Prep Task 3, fix is Option D (post-parse disambiguation in `_resolve_ambiguities()`). ~3–4h + 1h Option E (PYTHONHASHSEED determinism regression test). _Doc says CLOSED but verify on Day 11 baseline._ | **1–2** (→ solve) if the doc's CLOSED status is wrong; otherwise 0 |
| **L14** | #1089 + #1049 + #1041 | qabel (regression PARTIALLY FIXED), pak, cesam2 | path_solve_terminated / model_infeasible | Three different deep KKT bugs that share an "incomplete stationarity at boundary instance" theme. Each is 4–8h. Schedule individually if a sprint-end window opens. | **3** (→ solve/match) |

**Subtotal:** ~50–80h cumulative; ~20–30h achievable in remaining Sprint 25 days; rest queues to Sprint 26.

---

## NOT FIXABLE (Known Limitations)

| Issue | Model(s) | Reason |
|-------|----------|--------|
| #765 | orani | Linearized percentage-change CGE (>30% fixed exogenous variables); structurally incompatible with NLP→MCP. Permanent exclusion. |
| — | feasopt1, iobalance | GAMS structural test models; permanent exclusion. |
| #983 | elec | Non-convex KKT with division by zero in pairwise distance gradient; MCP correct but PATH cannot solve. May stack with M6 if a guard helps; currently classified as a known limitation. |
| #927 | egypt | PATH demo license limit (>300 equations). |
| (license) | danwolfe, glider, robot, shale, sroute, tabora, tfordy | Demo license limit. |
| #1199, #757 (closed) | bearing | Now in `model_optimal_presolve` set; warm-start works, no further fix. |

---

## Recommended Fix Order — Days 11–14 (Maximum Impact)

**Day 11 (today, ~4–6h, +3–4 solve):**

1. **S2 #1192** — gtm div-by-zero — 1h, +1 solve
2. **S4 #1245** — camcge div-by-zero — 1h, +1 solve
3. **S3+M3 #1243+#1315** — lmp2 div-by-zero + multi-solve set extraction (stacked) — 2–3h, +1 solve
4. **S6 #1280** verify status — 30min audit; if open and reproducible, +1 solve at <1h

**Day 12 (~6–8h, +2 solve, +2 match):**

5. **M2 #1316** — turkpow table-data — 3h, +1 solve
6. **M4 #1251** — twocge empty trade equations — 3h, +1 solve (and likely +1 match — was the original Day 10 #1278 motivation)
7. **S7 #1234** — otpop scalar-offset — 1h, +1 match

**Day 13 (~6–8h, +1–2 solve, +1 match):**

8. **M1 #1290** — ferts identifier limit — 2.5h, +1 solve
9. **M5 #1291** — clearlak ordering — 3.5h, +1 solve
10. **M9 #1239** — sambal/qsambal NA propagation — 2h diagnosis, may push to Day 14

**Day 14 (~4–6h, validation + ramp-down):**

11. Sprint-end retest pipeline; address regressions; document Sprint 26 carry-forward queue.
12. **L11 #1271** dispatcher refactor as buffer if all preceding fixes land cleanly — 4–5h, prevents future #1268-class regressions.

**Cumulative expected impact (Sprint 25 endpoint):**
- **Solve:** 106 → ~112–115 (target: ≥102 ✅ even at low end)
- **Match:** 54 → ~58–60 (target: ≥60 marginal; stretch ≥62 unlikely without Pattern A)

**Key deferral to Sprint 26:** L1 (Pattern A multi-index). Worth ~5–10 match if Pattern A and Pattern C are jointly completed, but exceeds the remaining day budget.

---

## Stale doc status — verification needed before scheduling

The following issue docs say `Status: OPEN` but the corresponding code fix may have landed in Sprint 25. Verify with `git log --grep` or `gh issue view` before scheduling work; if already fixed, mark the doc CLOSED and update the GitHub issue.

| Issue | Doc says | Likely actual | Verification command |
|-------|----------|---------------|----------------------|
| #1276 | OPEN — Deferred to Sprint 25 | **CODE LANDED** in Day 9 PR #1314 (fawley `.fx` dedup) — **but model still infeasible from a separate root cause** | `git log --oneline --grep '#1276'` |
| #1278 | (n/a — closed by Day 10 PR #1318) | CLOSED | confirmed |
| #1281 | OPEN — Deferred to Sprint 25 | **CODE LANDED** in Day 9 PR #1314 (lmp2 Parameter dedup) — but lmp2 still terminated from #1243 + #1315 | `git log --oneline --grep '#1281'` |
| #1283 | OPEN | CLOSED — Day 1 grammar fix | confirmed (GitHub issue closed; doc still says OPEN — needs same-PR or follow-up doc update) |
| #1289 | OPEN | CLOSED — Day 4 ganges-family | confirmed (GitHub issue closed; doc still says OPEN — needs same-PR or follow-up doc update) |
| #1292 | OPEN — Sprint 25 Priority 2 | **CODE LANDED** in Day 9 PR #1314 (turkpow line wrap) — but turkpow still in path_syntax_error from #1316 (table data) | `git log --oneline --grep '#1292'` |
| #1311 | (closed; per memory) | CLOSED — Day 8 abel-reassess | confirmed |
| #1312 | (closed; per memory) | CLOSED — Day 8 abel non-convex marker | confirmed |
| #1280 | OPEN | uncertain — may have landed in a Day 1–2 PR; needs audit | `git log --oneline --grep '#1280' src/emit/` |
| #1275 | OPEN — Deferred to Sprint 25 | uncertain | `git log --oneline --grep '#1275'` |

---

## Comparison to Sprint 24 Day 11 list

The Sprint 24 Day 11 list (`docs/planning/EPIC_4/SPRINT_24/ISSUE_FIX_OPPORTUNITIES_DAY11.md`)
identified compilation-error fixes (harker, fawley, china), division-by-zero guards, and
the alias-AD family as the highest-leverage areas. Status of those Sprint 24 picks now:

| Sprint 24 pick | Sprint 25 status |
|----------------|------------------|
| harker (Error 140) | **FIXED** (Day 6 Pattern C side-effect; harker now solves OK but `mismatch`) |
| fawley (Error 125 + zero stationarity) | partial — `.fx` dedup fixed (#1276); still `model_infeasible` from a separate root cause |
| china/turkey (Error 161 dimension) | **FIXED** for china; turkey still `path_syntax_error` |
| div-by-zero (camcge/elec/lmp2/gtm) | UNCHANGED — same 4 candidates listed as S2/S4/S3 above |
| cclinpts MCP pairing | partial — alias-class issue, queued under L1 |
| sambal/qsambal stationarity | UNCHANGED — listed as M9 |
| Status 5 models (agreste/chain/korcge/lnts) | UNCHANGED — none picked up |
| Translate timeouts | UNCHANGED — queued under L6 |

**Net Sprint 25 progress vs. Sprint 24 baseline:** Match 49 → 54 (+5), Solve 86 → 106 (+20).
The biggest gains came from **Pattern C Day-6 gate** (harker, china, irscge/lrgcge/moncge ax-fix
side-effect) and the **Day 9 emitter cleanups** (fawley `.fx`, lmp2 Parameter, turkpow line-wrap),
not from the alias-AD work which remains the highest-leverage outstanding lever for Sprint 26.

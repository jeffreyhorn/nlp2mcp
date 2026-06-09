# Sprint 27 Log

**Sprint:** 27
**Status:** 🟢 IN PROGRESS — Day 0 complete (kickoff landed; Priority 3 binding signals recorded)
**Start date:** 2026-06-01 (Day 0)
**End date:** TBD (Day 13)
**Owner:** Sprint 27 engineer
**Budget:** ≤ 168 hours over 14 days (Day 0 + Days 1–13); planned ~142h with ~26h slack
**Goal:** Push Solve 103 → ≥ 111 and Match 59 → ≥ 66; land all 4 Sprint 26 architectural reclassifications (#1381, #1385, #1390, #1393+#1335); apply 4 process recommendations (PR20–PR23).

**See:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` for the canonical day-by-day schedule
- `docs/planning/EPIC_4/SPRINT_27/prompts/PLAN_PROMPTS.md` for per-day execution prompts
- `docs/planning/EPIC_4/SPRINT_27/BASELINE_METRICS.md` for the Day 0 baseline
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` for KU status

---

## Day 0 Anchor SHA

`148662a5cfba7034920965e1c4e3bb38e40be184` — `main` tip at Sprint 27 Day 0 kickoff (2026-06-01). Used by `scripts/sprint_audit/changed_emit_artifacts.py --since-commit <SHA>` for every mid-sprint retest (Days 5, 10, 13).

---

## Cumulative Metrics Tracker

Filled in at each checkpoint (Days 5, 10, 13). Track delta vs Day 0 baseline.

| Metric | Day 0 baseline | Day 5 (Checkpoint 1) | Day 10 (Checkpoint 2) | Day 13 (Final) | Target |
|---|---|---|---|---|---|
| Parse success | 142/142 | 142/142 | 142/142 | 142/142 | ≥ 142/142 ✅ |
| Translate success | 131/142 | 132/142 | 133/142 | 135/142 | ≥ 135/142 ✅ |
| Solve success | 103/142 | 105/142 | 105/142 | 105/142 | ≥ 111/142 ❌ (S28) |
| Solution match | 59/142 | 61/142 | 62/142 | 62/142 | ≥ 66/142 ❌ (S28) |
| path_syntax_error | 14 | 9 | 7 | 8 | ≤ 6 ❌ |
| path_solve_terminated | 5 | 5 | 5 | 5 | ≤ 5 (maintain) ✅ |
| model_infeasible | 4 | 5 | 7 | 8 | ≤ 3 ❌ (fwd moves) |
| Tests passing | 4,737 | 4,758 | 4,768 | 4,779 | ≥ 4,750 ✅ |
| Determinism (3 `PYTHONHASHSEED`) | n/a | n/a | n/a | byte-identical ✅ | byte-identical ✅ |

---

## Day 0 — Sprint Kickoff

**Date:** 2026-06-01
**Status:** 🟢 COMPLETE
**Hours budgeted:** ≤ 8
**Hours actual:** ~6 (agent-executed)

### Tasks completed
- **0.1** Anchor SHA `148662a5` recorded in PLAN.md §4 + SPRINT_LOG.md (this file).
- **0.2** PR22 baseline audit → 0 commits / 0 changes (expected; Day 0 = anchor).
- **0.3** PR19 target-list widening (30 models; dry-run **11/19/30** GREEN — `launch` corrected to pattern-c Day 0 per PR #1413 CI: MODEL STATUS 5 Locally Infeasible, the #1378 target) → **PR #1413 opened**.
- **0.4–0.6** 3 AD architectural Phase 0 validation experiments executed serially (C→A→B); all prototypes model-guarded + **reverted (zero `src/` diff)**.
- **0.7** launch + qdemo7 anchor KKT hand-derived → `DAY0_ANCHOR_SCRATCH_NOTES.md`.
- **0.8** KU 6.1 → STANDALONE (no #1224/#1385 bundle).
- **0.9** Binding signals recorded in `PRIORITY_3_RISK_ASSESSMENT.md` §3.5/§4.5/§5.6 + new §8.5 consolidated table; KNOWN_UNKNOWNS 3.1–3.5 + 6.1 updated.

### Deliverables
- PR #1413 (anchor SHA + PR19 widening + Phase 0 prep notes).
- `DAY0_ANCHOR_SCRATCH_NOTES.md` (2 of 8 anchor KKT derivations).
- `PRIORITY_3_RISK_ASSESSMENT.md` §8.5 binding verdicts + budget-reallocation recommendation.

### Binding signals (Priority 3 — Days 6–8 gate)
| Exp | Sub-priority | Signal | One-line reason |
|---|---|---|---|
| C | #1393+#1335 otpop (Approach C) | 🔴 **REPLAN** | `_is_concrete_instance_of` never reached; patch inert (byte-identical emit). |
| A | #1390 kand (predicate-guarded Sum) | 🔴 **REPLAN** | bug is in `stationarity.py::_apply_offset_substitution` (×22), not `constraint_jacobian.py:903/1027`. |
| B | #1385 srpchase (Option B) | 🟡 **SCOPED-PROCEED** | translate 6.0s + clean compile ✓, but cross-term emit (runtime-guard) unproven. |

**Headline finding:** all 3 prep patch sites were mis-scoped to the **AD layer**; the bugs live in the **KKT stationarity/emit layer**. Per the `PRIORITY_3_RISK_ASSESSMENT.md` §6.4 cascading rule (2+ REPLAN), the Priority 3 Days 6–8 budget (~30–48h) should NOT commit as planned — see `PRIORITY_3_RISK_ASSESSMENT.md` §8.5 budget-reallocation recommendation. **Match target (`PLAN.md` §2) +1 from #1390 is now at risk.**

### KUs verified
- ✅ 3.1 (#1390 → REPLAN), 3.2 (#1385 → scoped-PROCEED), 3.3 (#1335 → Approach C disproven, fallback to B), 3.4/3.5 (Day 0 cross-ref), 6.1 (standalone).

### Carryforward to Day 1
- Priority 1 #1398: complete hand-derivation for 6 remaining anchors (ferts, sambal, ganges, sroute, turkpow, dinam ×2) per `DAY0_ANCHOR_SCRATCH_NOTES.md` queue; first prototype of tightened `_find_pattern_c_alias_sum`.
- **Day 0 retrospective decision needed:** re-scope #1390/#1393/#1335 against the redirected `stationarity.py` surfaces (re-run Phase 0 on the correct layer) OR defer to Sprint 28; reallocate freed Days 6–8 budget. Land #1385 translate-time short-circuit only (defer cross-terms to Sprint 28).
- PR #1413: verify PR19 CI fires on the widened 30-model list; merge.

### PR22 audit-script baseline output
```
## Mid-sprint retest surface

- **Range:** 148662a5cfba..HEAD
- **Commits:** 0 — **emit changes:** 0 (0 unique paths)

_(no emit-affecting changes in range)_
```

---

## Day 1 — Priority 1 Phase 0 anchors complete + first prototype

**Date:** 2026-06-02
**Status:** 🟢 COMPLETE
**Hours budgeted:** ≤ 10
**Hours actual:** ~7 (agent-executed)

### Tasks completed
- Hand-derived KKT for the 6 remaining anchors (ferts, sambal, ganges, sroute, turkpow, dinam) from raw GAMS sources → `DAY0_ANCHOR_SCRATCH_NOTES.md` Day 1 section. All 8 anchors now derived.
- **Implemented + verified the #1398 gate-predicate tightening** at `src/kkt/stationarity.py::_find_pattern_c_alias_sum`: the Pattern C `alias↔eq_dom` swap now fires only when `alias_name` and `eq_domain_index` resolve to the **same canonical set** (genuine self-alias, the launch shape). Cross-set alias sums (qdemo7's `sc(s,c)`, ferts's `ppos(p,i)`, ganges's `ri(r,i)`) fall through to the correct naive emit.
- Added regression test `test_cross_set_alias_sum_is_not_pattern_c_swapped` (asserts the gate does NOT swap cross-set sums).
- Quality gate: `make format/typecheck/lint` ✅; `make test` → **4737 passed, 10 skipped, 1 xfailed** (no regressions; new test +1 → 4738 with the unit test, run separately ✅).

### Deliverables
- `src/kkt/stationarity.py` 1-condition tightening (same-canonical-set guard) + explanatory comment.
- 8 anchor hand-derivations in `DAY0_ANCHOR_SCRATCH_NOTES.md`.
- New unit regression test in `tests/unit/kkt/test_pattern_c_alias_offset_gate.py`.

### Anchor verification (regenerated vs committed baseline)
| Anchor | Δ | correct per hand-derivation |
|---|---|---|
| launch | byte-stable | ✅ (KU 4.2 anchor preserved) |
| qdemo7 | changed | ✅ `sc(s,c)`/`lam_plow(s)` |
| ferts | changed | ✅ `ppos(p,i)`/`lam_mb(c,i)` |
| sambal | byte-stable | ✅ `nu_cbal(i)` |
| ganges | changed | ✅ `ri(r,i)` |
| sroute | byte-stable | ✅ |
| turkpow | byte-stable | ✅ (order-relation self-alias) |
| dinam | changed | ✅ row-mult-collapse, no `te` leak |
| 11 Tier 0/1 canaries | byte-stable | ✅ zero regressions |

### KUs verified
- **KU 1.3 ✅ VERIFIED** — the tightened gate fires only on same-canonical-set self-aliases (launch shape); no positional info from the source Sum body is needed. The distinguishing signal is purely `canonical(alias) == canonical(eq_dom)`.

### Carryforward to Day 2
- **Doc fix (DONE Day 2):** `PRIORITY_1_ANCHOR_MAPPING.md` §4.2 (ferts) + §4.4 (ganges) grep specs documented the *buggy baseline* (swapped arg order + eq-index leak) — corrected to source-order shapes on Day 2. (qdemo7 §4.1 was already correct.)
- Regenerate the full 15-model #1398 cohort + bucket-provenance (egypt/shale/qsambal/harker/tfordy/gangesx/srpchase timed out at the 120s cap on Day 1 — re-run with a longer cap); verify qdemo7 → compare_match, etc.
- Open the P1 PR (PR14 + PR20 cross-reference; pure `src/kkt/stationarity.py` change → PR23 N/A).

---

## Day 2 — Priority 1 full regression + PR open

**Date:** 2026-06-03
**Status:** 🟢 COMPLETE — full regression + bucket-provenance + doc-spec fix + **PR #1414 opened, reviewed, and MERGED** (merge `853000ef`, 2026-06-03)
**Hours budgeted:** ≤ 10
**Hours actual:** ~3 (carryforward portion)

### Tasks completed
- **Corrected the buggy anchor-mapping grep specs:** `PRIORITY_1_ANCHOR_MAPPING.md` §4.2 (ferts) + §4.4 (ganges) documented the *gate-mangled Day 0 baseline* (transposed condition + eq-index leak). Rewrote both to the hand-derived source-order shapes (ferts `ppos(p,i)`/`lam_mb(c,i)`; ganges `ri(r,i)`/`nu_qdep(i)`) with regression-check grep lines; verified all match the regenerated emit. (qdemo7 §4.1 was already correct.)
- **Regenerated the full 15-model #1398 cohort + launch** through the pipeline (translate + PATH solve + compare). **9 `_mcp.gms` artifacts changed** (corrected emit): dinam, egypt, fawley, ferts, ganges, gangesx, qdemo7, shale, srpchase. The other 6 affected + launch + all 11 Tier 0/1 canaries are byte-identical.

### Bucket-provenance (Sprint 27 Day 0 → Day 2, post-#1398)
| model | Day 0 bucket | Day 2 bucket | note |
|---|---|---|---|
| **qdemo7** | path_syntax_error | **compare_match** | ✅ +1 Solve / +1 Match recovery anchor |
| egypt | path_syntax_error | path_solve_license | ✅ recovered past syntax → license gate |
| ferts | path_syntax_error | path_solve_license | ✅ recovered → license |
| shale | path_syntax_error | path_solve_license | ✅ recovered → license |
| srpchase | translate_timeout | path_solve_license | ✅ now translates → license |
| ganges | translate_timeout | path_syntax_error | ✅ recovered from timeout (residual non-#1398 syntax) |
| dinam | path_syntax_error | path_syntax_error | emit corrected (−2 `$149` errors vs git baseline); residual `$140/$141/$171/$257` pre-existing |
| gangesx | path_syntax_error | path_syntax_error | emit corrected; residual errors pre-existing |
| turkpow | path_syntax_error | path_syntax_error | byte-identical to baseline — path_syntax_error entirely pre-existing |
| sambal/qsambal/harker | compare_mismatch | compare_mismatch | unchanged (correct; pre-existing numerics) |
| tfordy/sroute | path_solve_license | path_solve_license | unchanged (license-gated) |
| fawley | path_syntax_error | path_syntax_error | folded into #1356 (P5), not P1 |
| launch | compare_mismatch | compare_mismatch | byte-identical (KU 4.2 anchor; #1378 target) |

**No regressions** — every model is at its Day 0 bucket or better. The #1398 fix fully clears the Pattern C over-reach; dinam/gangesx/turkpow's residual `path_syntax_error` is **pre-existing** — independent GAMS compile errors in non-Pattern-C equations, with **model-dependent** codes (not a shared set): dinam `$140/$141/$171/$257`, turkpow `$141/$149/$170/$171/$257`, gangesx `$141/$145/$149/$257/$300`. turkpow is byte-identical to baseline (confirms pre-existing); dinam has *fewer* errors than baseline. Out of #1398 scope (Sprint 28 candidates).

### KUs verified
- KU 1.3 ✅ (Day 1). Bucket-provenance confirms the Day 0 recovery projections (§2 acceptance): qdemo7 → compare_match; egypt/ferts/shale → path_solve_license.

### Carryforward to Day 3
- ✅ P1 #1398 PR opened + merged (PR #1414, merge `853000ef`). One review comment (ferts §4.2 header consistency) addressed.
- Day 3: verify PR19 widening CI fired correctly on the merged commit; start P2 #1381 Phase 0 hand-derivation (camcge `nu_ieq` cross-term).
- **Sprint 28 candidate filed:** dinam/gangesx/turkpow residual (non-#1398) path_syntax_error — pre-existing GAMS errors in non-Pattern-C equations, **model-dependent** (union across the group: `$140`/`$141`/`$145`/`$149`/`$170`/`$171`/`$257`/`$300`; no single model has them all) (recorded in PLAN.md §13 Day 13 carryforward).

### PR opened
- **PR #1414** — "Sprint 27 P1: #1398 Phase A gate tightening (qdemo7 → compare_match; no regressions)". PR14: 9 regenerated `_mcp.gms` in diff. PR20: `DAY0_ANCHOR_SCRATCH_NOTES.md` hand-derivations + `PRIORITY_1_ANCHOR_MAPPING.md` §4 (§4.2/§4.4 corrected). PR23 N/A. **MERGED to main 2026-06-03 (`853000ef`).**

---

## Day 3 — Priority 1 merge + Priority 2 Phase 0 start

**Date:** 2026-06-03
**Status:** 🟢 COMPLETE
**Hours budgeted:** ≤ 8
**Hours actual:** ~4 (agent-executed)

### Tasks completed
- **Task 3 — PR19 CI verified:** PR #1414's `pr19-emit-solve-validation` run on the final PR head sha `0bd1d8d2` (run id 26911925363) **passed (37s, ≈ §7 projection)** — the widened 30-model target list fires correctly with the recovered emit (launch soft-fails as pattern-c; Tier 0/1 hard-fail all pass). (PR19 re-ran on each push to PR #1414 because the PR's cumulative diff includes `src/kkt/stationarity.py`; the head-sha run above is the authoritative one.)
- **Task 4 — Priority 2 (#1381) Phase 0 started:** hand-derived all **5 camcge** Pattern C consolidation variants from source → `DAY3_P2_PHASE0_NOTES.md`, and identified/stated **cesam2** as the dim-mismatch (B-3) second anchor (full cesam2 derivation finalizes Day 4). Derived the **consolidation rule** (source coeff positions preserved; sum-index slot → stat index `i`, eq-index slot → alias `j`; multiplier alias-indexed) — the invariant Phase B's source-body-driven builder must honor.
- **Tasks 5–6** — KNOWN_UNKNOWNS KU 2.1 → 🟡 PARTIALLY VERIFIED (design-ready; binding Day 4); this Day 3 entry.

### Deliverables
- `DAY3_P2_PHASE0_NOTES.md` — camcge stat_dk/stat_xd/stat_p (×3) hand-derived KKTs + cesam2 B-3 shape + Day-4 per-term grep verification specs.
- KU 2.1 updated (generalizes under one source-body design with 3 sub-builders B-1/B-2/B-3).

### Phase 0 baseline (camcge, current main `8f755328`)
path_syntax_error (`$141`×2 + `$257`). The #1398 (Phase A) gate does NOT fire (camcge alias-Sums have no `$`-condition) → phantom-offset enumeration (~20 guarded terms/multiplier; 40 for prodinv). Phase B consolidates each into a single alias-Sum.

| eq | stat | correct consolidated form | sub-phase |
|---|---|---|---|
| ieq | stat_dk | `sum(j, (-imat(j,i)) * nu_ieq(j))` | B-1 |
| inteq | stat_xd | `sum(j, (-io(j,i)) * nu_inteq(j))` | B-1 |
| actp | stat_p | `sum(j, (-io(i,j)) * nu_actp(j))` | B-1 |
| pkdef | stat_p | `sum(j, (-imat(i,j)) * nu_pkdef(j))` | B-1 |
| prodinv | stat_p | `dst(i) * sum(j, kio(j) * nu_prodinv(j))` | B-2 |
| cesam2 COLSUM | stat_tsam | `nu_COLSUM(j)$(jj(j))` (no outer Sum) | B-3 |

### KUs verified
- KU 1.3 ✅ VERIFIED (Day 1, merged in PR #1414). KU 2.1 → 🟡 PARTIALLY VERIFIED (Day 3 hand-derivation; binding Day 4). KU 1.1/1.2/1.4 verified at prep.

### Carryforward to Day 4
- Finalize cesam2 (B-3) hand-derivation (read `TSAM`/`COLSUM`/`jj` decls; confirm binding-position inference + `jj ⊆ i` subset).
- Implement Phase B-1/B-2/B-3 per ISSUE_1381 §Files Involved (`_build_pattern_c_consolidated_term`, `_classify_eq_body_factors`, `_build_pattern_c_dim_mismatch_term`); regenerate camcge + cesam2; byte-verify against the §"Phase 0 verification specs"; expect 11 plain-alias canaries (quocge/prolog/paklive/…) to byte-shift (consolidation) — regenerate goldens per PR14.

### PR merged
- **PR #1414** (P1 #1398) merged to main `853000ef`. Bucket recovery: qdemo7 → compare_match (+1 Solve/Match); egypt/ferts/shale/srpchase → path_solve_license; no regressions.

---

## Day 4 — Priority 2 Pattern C Phase B implement

**Date:** 2026-06-04
**Status:** 🟡 IN PROGRESS
**Hours budgeted:** ≤ 12
**Hours actual:** —

### Tasks completed
- **B-1 (plain-alias Pattern C consolidated builder)** landed (commit `2870b47e`): `_find_plain_alias_pattern_c` + `_build_plain_alias_consolidated_term` in `src/kkt/stationarity.py` consolidate plain-alias sums from the source body (camcge ieq/inteq/actp/pkdef). 23 goldens byte-shift, chenery reverted to baseline (single-pattern guard), zero solve regressions.
- **Parameter-ordering $141 fix** (this entry): root-caused camcge's `path_syntax_error`. GAMS `name(args)` is ambiguous between function call and indexed param ref, so `gamma(it)` parsed as a `Call` node; `_collect_param_refs` (`src/emit/original_symbols.py`) only inspected `ParamRef`, so the `at → gamma` dependency edge was invisible to the statement-level topo sort and `at(it) = …gamma(it)…` emitted **before** `gamma(it) = …` → $141. Fix: also collect `Call.func` names (downstream consumers intersect with actual computed params, so genuine function names are harmless). **camcge: `path_syntax_error` → `model_infeasible`** (now compiles + translates cleanly). New unit test `test_call_node_param_dependency_ordered`.

### Verification
- Corpus regen (153 models): only **camcge** golden changed (exact `at`-after-`gamma` reorder); all others byte-identical; the 7 CLI FAILs (danwolfe/decomp/mine/nemhaus/nonsharp/saras/trnspwl) are **pre-existing** (fail on baseline too).
- `make typecheck && make format && make lint`: clean. `make test`: 4739 passed, 0 failed.

### B-2 + B-3 + dynamic-subset (completed)
- **B-2 (camcge `prodinv`)** — eq-domain factor `kio(i)` sits OUTSIDE the inner alias-Sum. New `_walk_b2_alias_sum`/`_find_b2_pattern_c` descend through `*` to capture outer factors; `_classify_eq_body_factors` splits eq-side (`kio(i)` → inside, reindexed `kio(j)`) from var-side (constants → outside); `_build_b2_consolidated_term` emits `dst(i) * sum(j, kio(j) * nu_prodinv(j))`. **camcge compiles `a=c`-clean**, all 5 variants correct, 0 phantom offsets.
- **B-3 (cesam2 `COLSUM`/`ROWSUM`)** — dim-mismatch 1-D eq over 2-D var (both coords canonical `i`). New `_find_dim_mismatch_pattern_c`/`_build_pattern_c_dim_mismatch_term` infer the binding position from the source var-ref and emit `nu_COLSUM(j)$(jj(j))` / `nu_ROWSUM(i)$(ii(i))`, NO outer Sum; guarded to `=e=` + same-canonical-set (won't touch trnsport's `demand(j) =g=`). **Bonus: also fixes `iobalance`** — `stat_a(i,j)` collapses a 5-way phantom `sum(i__kkt1..5,…)$(sameas…)` block (+5 spurious aliases) to the correct `x(j)*nu_colbal(j)` (math-verified); iobalance now solves cleanly.
- **Dynamic-subset assignment drop (cesam2 `wbar1`)** — `wbar1(ii,jwt1)=1/7` over the runtime-populated subset `ii(i)` was dropped (Issue #622 expansion path: empty static members → silent skip → $141). Fix in `src/ir/parser.py`: when an expand position has empty members, store as an expression so the solver expands the runtime set. (The earlier "loop-body drop" concern was a FALSE ALARM — `loop((ii,jj)$NONZERO,…)` bodies emit as a literal `loop` statement, not via `param.expressions`.)

### Bucket outcomes (B-2/B-3)
- **cesam2:** `path_syntax_error` → **solves** (`compare_mismatch`). **camcge:** `path_syntax_error` → `model_infeasible` (correct emit; residual infeasibility is separate numerics). **egypt:** `path_syntax_error` → `path_solve_license`. **iobalance:** now solves cleanly. Net: **+1 Solve** (cesam2), **−2 path_syntax_error** (camcge/cesam2/egypt all leave the bucket).
- Corpus regen: 6 goldens changed (camcge/cesam2/cesam/egypt/iobalance/korcge), all verified; **korcge stays `compare_match`** (no regression); 7 CLI FAILs pre-existing. `make test`: 4744 passed, 0 failed. typecheck/format/lint clean.

### KUs verified
- KU 2.1 / 2.2 / 2.3 — Phase B-1/B-2/B-3 builders all landed and verified.

### Carryforward to Day 5
- camcge `model_infeasible` + cesam2 `compare_mismatch` are deeper numerics/emit issues beyond Pattern C consolidation (Sprint 28 candidates).

### PR opened
- PR #1417 (`planning/sprint27-day4-p2-phaseb`) — B-1 + ordering fix + B-2/B-3 + dynamic-subset.

---

## Day 5 — Checkpoint 1: Pipeline Retest + Priority 5 start + Priority 3 first sub-priority

**Date:** 2026-06-06
**Status:** 🟡 CHECKPOINT MISS (Solve 105 < 106, Match 61 < 62) — both shortfalls traced to **camcge = model_infeasible** (known singular-Jacobian CGE degeneracy from Day 4), NOT a P1 #1398 regression (qdemo7 recovered). Branch `planning/sprint27-day5-checkpoint1`.
**Hours budgeted:** ≤ 10

### Checkpoint 1 metrics (from full pipeline retest, anchor 148662a5 → HEAD)
| Metric | Day 0 | Day 5 | Δ | Checkpoint target |
|---|---|---|---|---|
| Solve | 103 | **105** | +2 | ≥ 106 ❌ (miss 1) |
| Match | 59 | **61** | +2 | ≥ 62 ❌ (miss 1) |
| path_syntax_error | 14 | **9** | −5 | (improving) |
| Translate | 131 | **132** | +1 | — |
| Tests | 4,737 | **4,758** | +21 | green (4,754 Day-4 merge + 4 comp_up Day-5) |

Solve breakdown: 132 translate-success → 105 solve-success; failures = model_infeasible 5, path_syntax_error 9, path_solve_terminated 5, path_solve_license 8.

### Checkpoint verdict — the +1 shortfall is camcge, NOT qdemo7
The criterion warned "Solve = 105 indicates qdemo7 did not recover." **That is NOT what happened.** Per-model truth from `gamslib_status.json`:
- **qdemo7** → solve=model_optimal, **compare_objective_match** ✅ (P1 #1398 gain HELD: +1 Solve, +1 Match).
- **cesam2** → solve=model_optimal, **compare_objective_match** ✅ (P2 Day-4 gain: +1 Solve, +1 Match).
- **camcge** → solve=**model_infeasible** ✗ — translates `action=c`-clean but the MCP is infeasible (singular-Jacobian CGE degeneracy; documented Day 4 as separate from Pattern C). **This is the missing +1 on BOTH Solve and Match.** Not a regression — camcge's Pattern-C emit is correct; the infeasibility is a distinct CGE-degeneracy issue → Sprint 28 candidate.

So the realized gains are P1 qdemo7 (+1/+1) + P2 cesam2 (+1/+1) = +2/+2; camcge's projected +1/+1 did not land. The checkpoint formula (which assumed camcge would solve) misses by exactly that 1.

### PR22 audit-script Day 5 output
Full output: `/tmp/sprint27_day5_retest_audit.md` (`changed_emit_artifacts.py --since-commit 148662a5 --mode retest`). Range `148662a5..HEAD`, 7 commits, 49 emit changes (34 unique paths). Confirms the expected artifacts: **cesam2 + cesam + ganges + gangesx** (Day-4 cesam2 bug-class), **camcge** (Pattern-C B-1/B-2/B-3 + `$141` + `*`-continuation), the **#1398 cohort** (dinam/egypt/fawley/ferts/ganges/gangesx/qdemo7/shale/srpchase), and the B-1 plain-alias canary set (abel/quocge/korcge/iobalance/…). ✅ all expected P1 #1398 + P2 #1381 artifacts present.

### Bucket-provenance updates (per PR17)
| Model | Day 0 bucket | Day 5 bucket | Rationale |
|---|---|---|---|
| qdemo7 | path_solve (#1398-affected) | **compare_match** | P1 #1398 gate fix (merged Day 3) — recovered + matches |
| cesam2 | path_syntax_error | **compare_match** | P2 Day-4 KKT bug class (#1 objgrad + #2 dual dim-mismatch + #3 scalar sign) — solves to NLP optimum 0.50796 |
| camcge | path_syntax_error | **model_infeasible** | P2 Pattern-C B-1/B-2 unblocked the `$141`/syntax → compiles clean; MCP infeasible from singular-Jacobian CGE degeneracy (separate issue → Sprint 28) |
| fawley | path_syntax_error | **model_infeasible** | P5 #1356 comp_up narrowing (Day 5) cleared the `$171`; cold MCP locally infeasible (needs further work) |
| otpop | path_syntax_error | **model_infeasible** | P5 #1357 comp_up narrowing (Day 5) cleared the `$171`; locally infeasible — **confirms it additionally needs #1393+#1335** (deferred to Sprint 28) |
| kand | compare_mismatch | **compare_mismatch** (unchanged) | #1390 re-scoped Phase 0 = re-REPLAN; the phantom-term collapse is solution-equivalent (MCP 195.0 unchanged ≠ NLP 2613.0) — not the mismatch cause |

### Tasks completed
- **PR22 audit script** run + captured (artifacts confirmed). ✅
- **Full pipeline retest** (142 models): Solve 105 / Match 61 / Translate 132 / path_syntax_error 9. ✅
- **P5 #1356 fawley + #1357 otpop** comp_up subset/superset narrowing (`src/kkt/complementarity.py`, Option a single-file). Both clear `$171` → leave path_syntax_error; blast radius = fawley+otpop only; 4 new unit tests; committed `05589235`. ✅ (first prototype = the committed fix)
- **#1390 re-scoped Phase 0** on the `stationarity.py` offset layer: env-guarded prototype confirmed the 22→1 predicate-Sum collapse compiles clean but is **solution-equivalent** (MCP stays 195.0 ≠ NLP 2613.0) → **binding re-REPLAN** recorded in `PRIORITY_3_RISK_ASSESSMENT.md` §3.5; prototype reverted (zero `src/` diff). ✅
- **otpop ↔ #1393+#1335 interaction verified**: comp_up fix alone leaves otpop locally infeasible → deferring #1393+#1335 defers the #1357 Solve gain (PLAN §2 risk realized). ✅

### Deliverables
- `src/kkt/complementarity.py` comp_up subset-narrowing + `tests/unit/kkt/test_comp_up_subset_narrowing.py` (committed `05589235`); regenerated `fawley_mcp.gms` + `otpop_mcp.gms`.
- `PRIORITY_3_RISK_ASSESSMENT.md` §3.5 Day-5 re-scoped binding verdict (re-REPLAN).
- Day-5 retest baseline (`gamslib_status.json`) + this SPRINT_LOG entry.

### KUs verified
- **KU 5.1** (#1356 fawley comp_up fix surface) → ✅ VERIFIED end-to-end (Option a narrowing emits the expected shape, zero `$171`).
- **#1390 re-scoped Phase 0** → binding **re-REPLAN** signal recorded (the §3.5 redirected surface is correct, but the documented fix is insufficient).

### Carryforward to Day 6
- **#1390 → Sprint 28** (re-diagnose the true kand mismatch source; the `tree`-predicate collapse is NOT it). Days 6–7 freed → redirect per Option 1 §6.4 (P7/P4 or #1385 translate-time short-circuit). **Sprint 27 Match target → 65** (record Day 13 §17).
- **fawley/otpop**: `$171` cleared but locally infeasible — fawley needs further investigation; otpop needs #1393+#1335 (Sprint 28). The #1356/#1357 firm Solve gains do NOT land this sprint as projected.
- **camcge**: model_infeasible (singular-Jacobian CGE degeneracy) → Sprint 28 candidate; not a Pattern-C regression.

---

## Day 6 — #1390 SKIP (re-REPLAN) + Sprint 28 carryforward + P5 #1357 confirmed + P7 #1387 implemented→reverted→Sprint 28

**Date:** 2026-06-06
**Status:** 🟢 DONE (re-REPLAN branch) — #1390 implementation SKIPPED per the Day-5 re-scoped Phase 0 verdict; freed Day 6–7 budget redirected to P7 #1387, which was greenlit, implemented, and then REVERTED (re-symbolization-anchor blocker) → deferred to Sprint 28. See below.
**Hours budgeted:** ≤ 12

### Gating decision
Day 6 is **gated on the Day 5 #1390 re-scoped Phase 0**, which returned **re-REPLAN** (the 22→1 predicate-Sum collapse is achievable but solution-equivalent — MCP `cost` stays 195.0 ≠ NLP 2613.0; the phantom terms are NOT the mismatch cause). Per the Day 6 prompt + PLAN §8 "if it re-REPLAN'd": **skip the #1390 implementation rows, defer #1390 to Sprint 28, Match → 65, pull P7 #1387 / P4 forward into this slot.**

### Tasks completed
- **#1390 Sprint 28 carryforward FILED** — `docs/issues/ISSUE_1390_*.md` status → DEFERRED to Sprint 28 with the Day-5 re-REPLAN evidence + re-diagnosis direction (true mismatch source is NOT the `tree`-predicate re-symbolization; candidates: `bal`/`x` stationarity, `t-1`↔`t+1` lag duality, LP first-stage/recourse coupling). `PRIORITY_3_RISK_ASSESSMENT.md` §3.5 (Day-5 binding block) + PLAN §17 risk row updated; **Match target 66 → 65** recorded. ✅
- **P5 #1357 otpop — confirmed CLOSED (landed Day 5)**: the comp_up subset/superset narrowing committed Day 5 (`05589235`, merged PR #1418) is the same single fix for #1356 fawley AND #1357 otpop. `otpop_mcp.gms` on main carries `comp_up_x(t)$(xb(t) < inf).. xb(t) - x(t) =G= 0;` — `$171` cleared. Solve gap (locally infeasible) needs #1393+#1335 → Sprint 28. ✅
- **P7 #1387 cclinpts redirect — diagnosed, implemented, REVERTED → Sprint 28** (full record in `docs/issues/ISSUE_1387_*.md`). Empirical diagnosis (residual check at the NLP optimum) CORRECTED the `PRIORITY_7_FIX_SURFACE.md` §3.1/§3.3 framing:
  - **"Bug 1 (sign-flip)" is a MISDIAGNOSIS — do NOT touch the sign logic.** The outer `(-1)` in `stat_b`/`stat_fb` is the standard maximize negation (`src/ad/gradient.py:265-267`, applied to every MAX model); combined with the inner `(-1)` from `d(b_M − b_j)/db_j` it yields the CORRECT `T1 − T2` signs under the codebase's `stat = −∇f + Jᵀν = 0` convention. §3.1/§3.3 hand-derived the *un-negated* `∂ObjV` and so flagged a sign error that does not exist; changing the sign logic would break every maximize model.
  - **Bug 2 (missing j+1 offset cross-terms) is REAL; the corrected form is residual-verified.** The per-instance objective gradient omits the `j+1`-offset contributions (where the wrt-variable appears as `fb((j+1)−1)`/`b((j+1)−1)` inside the sum). Hand-patching the missing negated terms makes the NLP optimum satisfy the eliminated KKT condition to **max|residual| = 5e-8**. Root site = `_diff_sum`'s collapse path in `src/ad/derivative_rules.py`.
  - **Implementation attempt + revert.** Greenlit to implement; built the offset enumeration in `_diff_sum` (gated `_try_diff_sum_offset_crossterms`). The per-instance derivatives are mathematically correct, **but reverted:** the gradient→stationarity re-symbolization anchors a pure-offset term (the `δ=−1` term is pure-`fb`, with no `b` reference to anchor on) on the WRONG element (`s11` not the col `s10`), mapping `fb(s11)−fb(s10) → fb(j)−fb(j-1)` (offset 0) which CANCELS the diagonal → cclinpts *worse*. cclinpts ALSO needs a warm-start (non-convex: PATH cold-converges to a spurious degenerate KKT point b≈const). Three coupled changes (AD enumeration + re-symbolization anchor + warm-start) → **deferred to Sprint 28** (the §3.7 escalation). `_diff_sum` change reverted; cclinpts byte-identical to baseline.

### Deliverables
- `docs/issues/ISSUE_1390_*.md` Sprint 28 carryforward section; Match→65 recorded in `PLAN.md` §17 (risk row) and `PRIORITY_3_RISK_ASSESSMENT.md` §3.5 (Day-5 binding block).
- `docs/issues/ISSUE_1387_*.md` updated with the Day-6 diagnosis + implementation-attempt finding (the re-symbolization-anchor blocker) + the well-specified Sprint 28 scope.
- This Day 6 SPRINT_LOG entry. No net `src/` changes Day 6 — the #1390 prototype was reverted Day 5, and the #1387 `_diff_sum` change was implemented and then reverted (re-symbolization-anchor blocker; cclinpts byte-identical to baseline).

### KUs verified
- **KU 3.1** (#1390 kand) → re-verified on the redirected `stationarity.py` layer as **re-REPLAN** (the collapse is achievable but inert to the objective); deferred to Sprint 28.

### Carryforward to Day 7
- **P7 #1387** → **Sprint 28** (NOT awaiting greenlight — greenlight was given, the AD offset-enumeration was implemented and reverted; the remaining blockers are technical (re-symbolization anchoring + non-convex warm-start), well-specified in `ISSUE_1387`). Per PLAN §8, #1385 translate-time-only short-circuit is the Day-7 item.
- #1390, #1393+#1335, #1387 → Sprint 28 carryforwards filed.

---

## Day 7 — #1385 translate-time-only short-circuit (srpchase) + P5 close-out

**Date:** 2026-06-07
**Status:** 🟢 DONE — #1385 translate-time short-circuit LANDED (cross-terms → Sprint 28); #1390 PR N/A (re-REPLAN'd Day 5/6); P5 already closed Day 5 (PR #1418), clearlak re-verified.
**Hours budgeted:** ≤ 12

### Adjusted scope (vs the prompt)
- **#1390 PR — N/A.** Day 5/6 re-scoped Phase 0 = re-REPLAN → deferred to Sprint 28; there is no #1390 implementation to PR.
- **P5 close — already MERGED Day 5** (PR #1418): the comp_up subset/superset narrowing is one fix for both #1356 fawley and #1357 otpop. Day 7 re-runs the clearlak byte-stability check (KU 5.3).

### Tasks completed
- **#1385 translate-time-only short-circuit — LANDED** (`src/ad/index_mapping.py`). Generalized the Day-0 model-name guard (`'purchase'`) to a tight STRUCTURAL gate `_is_blowup_dynamic_subset_equation`: a 1-D **dynamic** subset (0 static members) of a **large** parent (≥100), single (optionally negated) `SetMembershipTest` condition, body summing over a **2-D set** (`sum(ancestor(srn,n), …)`) → `enumerate_equation_instances` returns `[]`, skipping the `differentiate_expr` blow-up.
  - **srpchase: 6.56s** (was >180s `translate_timeout`), GAMS `action=c`-clean, 0 quoted-literal set-name indices. **Translate-bucket gain, NOT Solve/Match** (slack/demand cross-terms deferred → srpchase does not reach `compare_match`).
  - **Blast radius = srpchase ONLY** — full-corpus byte scan: 136 byte-identical (gate didn't fire), 7 pre-existing FAILs unchanged, parse-timeout models stay `translate_timeout` both sides (no bucket change; none are scenario-tree shapes). 5 new unit tests (`tests/unit/ad/test_blowup_enumeration_skip.py`).
  - **Sprint 28 follow-on FILED** (`ISSUE_1385` updated): the runtime-guard equation-body re-emit (`src/kkt/stationarity.py`) + the `J_gᵀ·lam` cross-terms — coupled, must land together (re-emitting constraints without cross-terms = inconsistent MCP).
- **P5 clearlak byte-stability (KU 5.3)** — re-verified clearlak byte-identical to HEAD (the #1385 gate does not fire for clearlak; the P5 comp_up change merged Day 5 left it byte-stable).

### Deliverables
- `src/ad/index_mapping.py` #1385 gate + skip; `tests/unit/ad/test_blowup_enumeration_skip.py` (5 tests); regenerated `data/gamslib/mcp/srpchase_mcp.gms`.
- `ISSUE_1385` updated (status PARTIALLY DONE; Sprint 28 deferred scope).

### KUs verified
- **KU 3.2** (#1385 short-circuit) → ✅ VERIFIED **as scoped (translate-time only)**: srpchase <10s + clean compile; cross-terms deferred to Sprint 28.
- **KU 5.1 / 5.2 / 5.3** (#1356/#1357 comp_up) → ✅ VERIFIED (merged Day 5 PR #1418; clearlak byte-stable re-confirmed Day 7).

### Carryforward to Day 8
- **#1385 Sprint 28 follow-on** (runtime-guard emit + cross-terms) + **#1390, #1393+#1335, #1387** → Sprint 28 carryforwards filed.
- Per PLAN §8 Day 8: P7 #1387 was pulled forward but → Sprint 28 (Day 6 diagnosis); #1393+#1335 Sprint 28 carryforward filing.

### PRs opened
- Day-7 PR (#1385 translate-time short-circuit). #1390 PR N/A; P5 PR already merged Day 5 (#1418).

---

## Day 8 — #1385 PR merged + Sprint 28 carryforwards filed (#1393, #1335, #1387)

**Date:** 2026-06-07
**Status:** 🟢 DONE — #1385 PR (#1420) merged to main; #1393, #1335, #1387 filed as Sprint 28 carryforwards (NONE implemented). P7 #1387 implementation NOT attempted (Day 6 already diagnosed + reverted → Sprint 28).
**Hours budgeted:** ≤ 12
**Hours actual:** —

### Adjusted scope (vs the prompt)
- **Task 1 (#1385 PR) — already complete.** PR #1420 opened + review-iterated (Copilot `quiet=True` fix, commit `dc95c703`) + **merged to main** (`59c22931`). The scoped/translate-only boundary + Sprint 28 cross-term follow-on are stated in `ISSUE_1385`.
- **Task 3 (#1387 implement, pulled forward from Day 10) — NOT attempted.** The Day 8 prompt's premise is **superseded by Day 6**: #1387's "Bug 1 sign-flip" is a misdiagnosis (maximize negation is correct), the real "Bug 2" offset-enumeration was implemented AND reverted (re-symbolization-anchor blocker), and cclinpts additionally needs a non-convex warm-start. Three coupled changes → deferred to Sprint 28. Re-implementing per the stale prompt would re-derive a non-bug and re-apply a change Day 6 proved makes cclinpts worse. **User-confirmed** the adjusted plan (file as carryforward, skip implementation).

### Tasks completed
- **#1393+#1335 Sprint 28 carryforward filed** (replaces the disproven Approach-C implementation):
  - `ISSUE_1393` — Status → DEFERRED to Sprint 28; added "Sprint 28 carryforward" section with the Day 0 binding REPLAN evidence (Approach C inert — `_is_concrete_instance_of` never reached, `otpop_mcp.gms` byte-identical, no `src/` diff); redirected fix surface = the `stationarity.py` symbolic-collapse path; old Approach-C "Root cause" framing marked HISTORICAL.
  - `ISSUE_1335` — Status → DEFERRED to Sprint 28; confirmed **now DISTINCT from #1393** (Approach C never subsumed it); Sprint 28 fix = Approach B (`_try_eval_offset` for `card(t)-ord(t)` symbolic resolution, no Sum expansion).
- **#1387 Sprint 28 carryforward filed** — `ISSUE_1387` Status → DEFERRED to Sprint 28; added a Day-8 filing section formalizing the three-coupled-changes deferral (AD offset-enumeration + re-symbolization-anchor fix + non-convex warm-start) on top of the existing Day-6 binding diagnosis. No implementation; working tree carries no `src/` change.

### Deliverables
- `docs/issues/ISSUE_1393_*.md`, `docs/issues/ISSUE_1335_*.md`, `docs/issues/ISSUE_1387_*.md` — Sprint 28 carryforward sections + status updates.
- This SPRINT_LOG Day 8 entry. **Docs-only day** (no `src/` or test changes → no quality-gate run required).

### KUs verified
- **KU 3.3** (#1393+#1335 Sprint 28 carryforward) → ✅ reflects the Day 0 REPLAN + the now-distinct #1393/#1335 split (filed Day 8).

### Carryforward to Day 9
- Sprint 28 carryforwards now filed: **#1390** (Day 6), **#1385** cross-terms (Day 7), **#1393**, **#1335**, **#1387** (Day 8). Match target → 65.
- Per PLAN §9: Priority 3 close + Priority 4 (#1378) launch-numerics start.

### PRs opened
- None (docs-only). #1385 PR #1420 already merged to main (`59c22931`); a Day-8 docs PR will carry the carryforward filings.

---

## Day 9 — Priority 4 #1378 launch PATH-numerics: launch → MATCH (double-applied param fix)

**Date:** 2026-06-07
**Status:** 🟢 DONE — **launch recovered from `compare_objective_mismatch` (13.3%) to `compare_match`** via a presolve-emit fix (no `_apply_pattern_c_swap_to_term` change). Match +1.
**Hours budgeted:** ≤ 10

### Adjusted scope (vs the prompt)
- **Task 1 (merge P3 PRs) — nothing to merge.** No open PRs: #1385 (PR #1420) merged Day 7; #1393+#1335 carryforward (PR #1421) merged Day 8; #1390 has no PR. 
- **Task 2 (open P7 #1387 PR "implemented Day 8") — N/A.** #1387 was NOT implemented (Day 6 diagnosed+reverted → Sprint 28 carryforward, filed Day 8). No PR to open.
- **Day 9 = Priority 4 #1378 only.** User-directed: pursue the launch MATCH (path "B") with up to 8h, solver-tuning-first.

### Investigation + fix (#1378)
- **Baseline:** cold `launch_mcp.gms` → MODEL STATUS 5 Locally Infeasible (6194 iters). The committed `launch_mcp_presolve.gms` + `run_full_test.py`'s STATUS-5 presolve-retry already recover the SOLVE (`model_optimal_presolve`) — but launch **mismatched** (MCP 2604.01 vs NLP ref 2257.80, 13.3%).
- **Root cause (NOT non-convexity, NOT sign/scaling):** launch.gms adjusts coefficients in place — `pre2('stage-3') = pre2('stage-3')*10**pre3(...)` and the same for `pre4`. The presolve emit re-emitted these AND `$include`d launch.gms, so under `$onMultiR` they were **double-applied** (`pre2('stage-3')` −0.001→−3.95e-5; `pre4('stage-3')` 52.5→165.3), corrupting the objective for both the embedded NLP pre-solve and the final MCP. Confirmed via `iterlim=0` start dumps (identical), identical model stats, and a `Display pre2,pre4` probe. Also proved 2257.80 IS a valid MCP KKT point by warm-starting the MCP from the good NLP optimum via a GDX hand-off → MCP converged to 2257.80.
- **Fix:** `skip_self_ref_presolve` flag in `emit_computed_parameter_assignments` (`src/emit/original_symbols.py`), threaded from `emit_gams.py` as `presolve_will_emit`. Under `--nlp-presolve`, self-referential source param assignments are skipped (the `$include` applies them once). Result: embedded NLP and MCP both reach **2257.7976 → `[COMPARE] MATCH`** (rel_diff 0.0).
- **Blast radius:** presolve-only. Cold `launch_mcp.gms` byte-identical (KU 4.2 anchor preserved). True fix delta touches only launch (→match) and cesam (`model_infeasible`; presolve emit made more correct, compiles clean action=c). The 7 currently-matching presolve models have no self-referential assignments → unaffected (regenerated byte-identical). fawley/korcge presolve-golden diffs are **pre-existing staleness on main**, not this fix.

### Deliverables
- `src/emit/original_symbols.py` (`skip_self_ref_presolve` param + skip), `src/emit/emit_gams.py` (hoisted `presolve_will_emit`, threaded to both param-assignment passes).
- `data/gamslib/mcp/launch_mcp_presolve.gms` regenerated (−5 lines: the 2 double-applied `pre2`/`pre4` assignments + empty block).
- `tests/integration/emit/test_launch_presolve_double_apply.py` (2 tests: presolve omits self-ref, cold keeps it).
- `data/gamslib/gamslib_status.json`: launch → `compare_match` (rel_diff 0.0).

### KUs verified
- **KU 4.1** → ✅ VERIFIED: PATH-numerics IS solver-tunable (warm-start), and the MATCH is delivered by the presolve double-apply fix — NOT a `_apply_pattern_c_swap_to_term` sign/scaling change.
- **KU 4.2** → ✅ VERIFIED (anchor PRESERVED): fix is presolve-only; cold `launch_mcp.gms` byte-identical.

### Carryforward to Day 10
- Pre-existing staleness in several `*_mcp_presolve.gms` goldens (cesam/fawley/korcge) is independent of #1378 — candidate housekeeping (not gating; no presolve byte-test exists). cesam/fawley remain blocked by their own issues (model_infeasible / path_syntax_error).
- Sprint 28 carryforwards unchanged: #1390, #1385 cross-terms, #1393, #1335, #1387.

### PRs opened
- Day-9 PR (#1378 launch match): branch `planning/sprint27-day9-1378`.

---

## Day 10 — Checkpoint 2: full pipeline retest (Solve 105 / Match 62; no regression, gap = Sprint 28 deferrals)

**Date:** 2026-06-08
**Status:** 🟢 DONE — full 142-model retest complete. **Solve 105/142, Match 62/142**, both **below the optimistic targets (≥108 / ≥65) by exactly the Sprint 28 deferrals** (camcge, otpop, fawley — all `model_infeasible`). **No silent regression**: the Solve-success and Match sets are byte-identical to the committed (Day-9) DB.

### Adjusted scope (vs the prompt)
- **Task 4 (Priority 4 close) — done.** PR #1422 (launch #1378) merged.
- **Task 5 (merge P7 #1387) — N/A.** #1387 was never implemented (Day 6 diagnosed + reverted → Sprint 28 carryforward, filed Day 8). No PR to merge.
- Day 10 = PR22 audit + full pipeline retest + this checkpoint entry.

### Checkpoint 2 metrics (full pipeline retest, all 142 models)
| Metric | Day 0 | Day 5 | Day 10 | CP2 target | Δ Day 0 → Day 10 |
|---|---|---|---|---|---|
| Parse | 142 | 142 | **142** | — | +0 |
| Translate | 131 | 132 | **133** | — | +2 |
| Solve | 103 | 105 | **105** | ≥ 108 | **+2** (miss −3) |
| Match | 59 | 61 | **62** | ≥ 65 | **+3** (miss −3) |
| path_syntax_error | 14 | 9 | **7** | ≤ 6 | −7 (miss −1) |
| path_solve_terminated | 5 | 5 | **5** | ≤ 5 | +0 (met) |

Solve-failure bucket reconciliation (133 translated = 105 solved + 28 failed): `path_solve_license` 9 · `model_infeasible` 7 · `path_syntax_error` 7 · `path_solve_terminated` 5.

### No-regression verification (the prompt's "investigate if Match=62" gate)
Compared the retest DB against the committed (Day-9) `gamslib_status.json`:
- **Match set: identical** (62 = 62; 0 gained, 0 lost). **Solve-success set: identical** (0 gained, 0 lost).
- The only deltas are **reclassifications within the failure set** (this is the first full re-solve since Day 5, refreshing stale buckets): `path_syntax_error` 9 → 7, `model_infeasible` 5 → 7, `path_solve_license` 8 → 9. None of these moved a model out of Solve/Match.
- **Conclusion: the 62 is NOT a silent recovery failure.** The realized firm Match gains are exactly `qdemo7` (#1398, Day 5) + `cesam2` (#1381, Day 4) + `launch` (#1378, Day 9) = baseline 59 **+3 = 62**. The Day-0 "+6 firm" projection assumed `fawley` (#1356), `otpop` (#1357), and a second `#1381` model (`camcge`) would also deliver Match — but all three went **`model_infeasible`** (documented Days 4–5: forward bucket moves needing the deferred #1393+#1335 / the CGE singular-Jacobian degeneracy). Same story for Solve: realized firm gains = `qdemo7` + `cesam2` = +2 → 105; the other 3 projected solves are the deferred infeasibles.

### Named non-success buckets (Day 10)
- **Match (62):** baseline 59 + qdemo7 + cesam2 + launch.
- **model_infeasible (7):** agreste, **camcge**, camshape, cesam, **fawley**, lnts, **otpop** — bold = Sprint 28 carryforward Solve/Match targets (#1393+#1335, CGE degeneracy).
- **path_syntax_error (7):** clearlak, dinam, gangesx, indus, sample, turkey, turkpow — pre-existing (non-#1398; turkpow byte-identical to baseline per Day-5 notes).
- **path_solve_license (9):** egypt, ferts, glider, robot, shale, sroute, srpchase, tabora, tfordy (license-limited, not a translation defect).
- **path_solve_terminated (5):** dyncge, elec, maxmin, tricp, twocge.

### PR22 audit-script Day 10 output (`scripts/sprint_audit/changed_emit_artifacts.py --since-commit 148662a5 --mode retest`)
- **Range:** `148662a5cfba..HEAD` — **11 commits, 54 emit changes (36 unique `*_mcp.gms` paths).**
- Changed emit artifacts (P1 #1398 + P2 #1381 + P5 #1356/#1357 + P4 #1378 sweep): abel, agreste(+presolve), camcge, cesam, cesam2, dinam, dyncge, egypt, fawley, feasopt1, ferts, ganges, gangesx, iobalance, irscge, korcge, **launch_mcp_presolve**, lrgcge, markov, meanvar, moncge, orani, otpop, ps10_s, ps2_f_s, ps2_s, ps3_s(+gic/mn/scp), qdemo7, quocge, shale, srpchase, stdcge. Full per-commit table: `/tmp/sprint27_day10_retest.md`.

### Tasks completed
- Full 142-model pipeline retest (`run_full_test.py`) — refreshed `gamslib_status.json` (authoritative Checkpoint 2 state); determinism confirmed (Solve/Match sets byte-identical to committed).
- PR22 audit-script invocation (above).
- This checkpoint entry.

### Deliverables
- `data/gamslib/gamslib_status.json` (refreshed Checkpoint 2 DB). Docs-only otherwise (no `src/` change → no quality-gate run; the retest IS the verification).

### KUs verified
- Checkpoint 2 confirms the realized Solve/Match deltas (+2 / +3) match the landed work; the gap to target is the recorded Sprint 28 deferrals (#1390, #1393+#1335, #1387) — per PLAN §17, Match 62 (target-minus-3, all deferral-attributable) is recorded, not treated as a regression.

### Carryforward to Day 11
- **Sprint 28 carryforwards (Solve/Match-bearing):** #1393+#1335 (otpop/camcge/cesam infeasible), #1390 (kand), #1387 (cclinpts), + camcge CGE singular-Jacobian degeneracy. These are the Solve 105→108 / Match 62→65 gap.
- Per PLAN §11: Priority 7 #1388 discriminator + Priority 6 #1224 start. (#1387 already → Sprint 28.)
- **Pre-existing `*_mcp_presolve.gms` golden staleness** (cesam/fawley/korcge) noted Day 9 — still candidate housekeeping, not gating.

---

## Day 11 — Priority 7 #1388 §4.6 discriminator → #1424 subset-corruption fix LANDED + #1388 Case (b) → Sprint 28

**Date:** 2026-06-08
**Status:** 🟢 DONE — §4.6 discriminator run; uncovered + shipped a separable emit bug (#1424); #1388 classified Case (b) (multi-bug) → Sprint 28 carryforward. #1224 not started (the §4.6 dive + #1424 fix consumed the day).
**Hours budgeted:** ≤ 10

### Adjusted scope (vs the prompt)
- Prompt context "#1387 implemented Day 8 + closed Day 9–10" is **stale** — #1387 was never implemented (Day 6 diagnosed + reverted → Sprint 28 carryforward, filed Day 8). Not a Day 11 task.
- The §4.6 discriminator surfaced a **separable, previously-undiagnosed emit bug (#1424)** that had to be fixed before the discriminator was even valid; that + its 19-golden blast-radius verification consumed the day. **#1224 (Priority 6) deferred to Day 12.**

### #1388 §4.6 3-way discriminator result
- **NLP-warm-start MODEL STATUS:** 5 Locally Infeasible (from a verified-complete warm-start, after #1424).
- **All 10 warm-startable symbols verified loaded:** ✅ (area=4.284, lam_convexity≈194, lam_convex_edge1(i1)=198.17, nu_eqrdiff≈−0.94, rdiff loaded; lam_convex_edge3/4, piL_r, piU_r correctly 0 — inactive in NLP).
- **Per-term shape-divergence:** **non-inert** — `stat_r(i1)` INFES ≈ 396 at the NLP KKT point (dominated by the unbalanced `convex_edge1` cross-term); distinct from the §4.3 boundary-guard mismatch (proven *inert*).
- **Case classification:** **(b)** — emit bug (structural `stat_r` divergence), NOT pure non-convexity.
- **Action:** **Sprint 28 carryforward** (`ISSUE_1388` updated). camshape's +1 Solve needs BOTH #1424 (landed) AND the Case-(b) `stat_r` fix (~4.5h, per-term stationarity-emit diagnosis at `stationarity.py:1835`/`constraint_jacobian.py`).
- **Note:** Approach A's warm-start was initially *invalid* — camshape's `--nlp-presolve` embedded NLP was MS 4 Infeasible (area=5.009) due to **#1424** (subset corruption). Fixing #1424 restored the embedded NLP to MS 2 / area=4.2841, enabling a valid discriminator.

### #1424 subset-corruption emit bug — FIXED (Sprint 27)
- **Bug:** `_emit_dynamic_subset_defaults` blanket-populates `subset(parent)=yes` for dynamic subsets with no static members referenced in stationarity (#952). For subsets the model assigns **element-wise** (camshape `first('i1')=yes`; cclinpts `first/last`), the blanket runs first and isn't cleared → `first`/`last` become all-`i`, `middle(first)=no` empties `middle` → constraint domains corrupted (emit solves the wrong problem) + the `--nlp-presolve` warm-start broke.
- **Fix:** `_emit_dynamic_subset_defaults` skips the blanket for any subset in `model_ir.set_assignments`. Genuinely-empty subsets (#952, e.g. nonsharp `acol`) keep the default.
- **Blast radius:** 16 goldens change. camshape/cclinpts = real correction (element-wise). The other 14 (qdemo7, cesam2, korcge, qabel, srpchase, abel, …) reassign the subset **wholesale** (`cn(c)=yes$(...)`, `srn(n)=prob(n)`) which overrides the blanket at runtime → byte-only golden change, **solve-identical**. lmp2 unchanged (`n` not a set-assignment); decomp/nemhaus untouched (pre-existing translate failures, confirmed on main).
- **Regression: NONE.** All 4 currently-matching affected models re-solved to the SAME objective (qdemo7 1589042.386, cesam2 0.508, qabel 46965.036, korcge 339.213) → all stay `compare_match`. #952 preserved (unit test).
- **No Solve gain by itself** (camshape stays MS 5 — the Case-(b) `stat_r` bug remains).

### Deliverables
- `src/emit/emit_gams.py` (`_emit_dynamic_subset_defaults` skip), 16 regenerated `*_mcp.gms` goldens.
- `tests/integration/emit/test_dynamic_subset_default_skip.py` (2 tests: model-assigned → no blanket; genuinely-empty → blanket preserved).
- `docs/issues/ISSUE_1424_*.md` (new, with Phase 0 acceptance gate); `docs/issues/ISSUE_1388_*.md` (Day-11 §4.6 result + Sprint 28 carryforward).
- GitHub issue #1424 filed.

### KUs verified
- **KU 7.2 / 7.3** (#1388 §4.6 discriminator) → ✅ run: Case (b), multi-bug; subset bug (#1424) split out and fixed, `stat_r` Case-(b) divergence → Sprint 28.

### Carryforward to Day 12
- **#1224 (Priority 6, standalone)** — not started Day 11; → Day 12.
- **Sprint 28:** #1388 (`stat_r` Case-(b) fix), plus the prior carryforwards (#1390, #1393+#1335, #1387, camcge CGE).

---

## Day 12 — Priority 6 #1224 FULL (carried from Day 11): +1 Translate (mine); #1400/#1374 → Day 13

**Date:** 2026-06-08
**Status:** 🟢 #1224 DONE (+1 Translate) — the non-negotiable Day-12 deliverable landed. **#1400 + #1374 slip to Day 13 buffer** per the PLAN §12 slip guidance (the #1224 carryforward consumed the day's budget).
**Hours budgeted:** ≤ 10

### #1224 mine — parameter-valued index offsets → +1 Translate (PR #1426)
- **Bug:** mine's `pr(k,l+1,i,j)$c(l,i,j).. x(l, i+li(k), j+lj(k)) =g= x(l+1,i,j)` uses parameter-valued offsets (`li(k)`/`lj(k)`). Translation aborted with `NotImplementedError: Complex offset expressions not yet supported: ParamRef(li(k))`.
- **Corrected fix surface** (NOT the prep-doc guess `_try_eval_offset` / `derivative_rules.py:2793`): the `pr` complementarity is kept **symbolic over `k`**, so the offset can never reduce to a constant at emit; the hard error is in **`src/ir/ast.py` `IndexOffset.to_gams_string()`** (the emit phase, reached past AD). GAMS natively accepts a parameter lead/lag amount, so the fix adds a `ParamRef` branch rendering `base+li(k)` (mirrors the existing `Call` branch).
- **Result: +1 Translate** — mine `translate_internal_error` → `translate_success`, **compiles clean** (`action=c`, 0 errors). **Additive / zero-regression** blast radius: the branch only fires where emit previously *raised*, so no currently-translating model is affected (none have parameter-valued offsets).
- **KU 6.2 (next failure mode): `model_infeasible`.** The emitted MCP solves MS 4 Infeasible — `stat_x`'s `pr` cross-term doesn't invert the parameter-valued offset (`sum(k, lam_pr(k,l,i,j))` instead of `sum(k, lam_pr(k,l,i-li(k),j-lj(k)))`) and drops the `-sum(k, lam_pr(k,l-1,i,j))` term. The correct stationarity (the AD/Jacobian path the prep doc named) is the **conditional Solve gain → Sprint 28**.
- KU 6.1 ✅ (STANDALONE confirmed — fix is `src/ir/ast.py`, no `index_mapping.py`/#1385 overlap). KU 6.2 ✅ VERIFIED (`model_infeasible`).

### Deliverables
- `src/ir/ast.py` (`IndexOffset.to_gams_string()` ParamRef branch).
- `tests/unit/ir/test_index_offset_paramref.py` (5 tests: ParamRef lead renders, ParamRef lag `i-li(k)` renders, Const/symbol unchanged, circular ParamRef rejected, mine translates end-to-end).
- `docs/issues/ISSUE_1224_*.md` (resolution + Phase 0 section); KNOWN_UNKNOWNS KU 6.2 ✅.

### KUs verified
- **KU 6.1** ✅ (STANDALONE), **KU 6.2** ✅ (`model_infeasible` next failure mode).

### Carryforward to Day 13
- **#1400 (Priority 8) + #1374 (Priority 9)** slip to Day 13 per the PLAN §12 slip guidance — Day 12 was the full-#1224 carryforward from Day 11.
- **Sprint 28:** #1224 Solve (parameter-valued-offset KKT cross-term inversion), plus the prior carryforwards (#1390, #1393+#1335, #1387, #1388, camcge CGE).

### #1400 absolute-path-leak audit-grep result
_(deferred to Day 13)_

### #1374 corpus-sweep results
- _(deferred to Day 13)_
- **Sprint 27 fix scope:** TBD shapes (most common)
- **Sprint 28 carryforward:** TBD shapes

---

## Day 13 — #1400 + #1374 (slipped) + Final Retest (deterministic) + closeout

**Date:** 2026-06-08
**Status:** 🟢 DONE — #1400 + #1374 landed; final 3× `PYTHONHASHSEED` retest **fully deterministic**; SPRINT_LOG final + SPRINT_RETROSPECTIVE authored. Final: **Translate 135 ✅ / Solve 105 / Match 62 / determinism ✅**; Solve/Match miss targets by the documented Sprint 28 deferrals.

### #1400 (Priority 8) + #1374 (Priority 9) — slipped from Day 12, landed
See PR #1427. #1400: `mcp_file_used` → repo-relative (`_repo_relative_path`); 6 DB entries cleaned (0 absolute remain); KU 8.1/8.2 ✅. #1374: `.fx`-restore duplicate shape fixed (otpop/dinam); `.l` shape (robot) → Sprint 28; KU 9.4 ✅. make test 4779.

### Final pipeline retest under 3 `PYTHONHASHSEED` values — DETERMINISTIC ✅
| `PYTHONHASHSEED` | Parse | Translate | Solve | Match | Mismatch |
|---|---|---|---|---|---|
| 0 | 142 | 135 | 105 | 62 | 37 |
| 1 | 142 | 135 | 105 | 62 | 37 |
| 42 | 142 | 135 | 105 | 62 | 37 |

**Determinism: PASS** — the three `gamslib_status.json` outputs are **byte-identical modulo wall-time fields** (`seed0 == seed1 == seed42`, verified after stripping date/time/duration keys). The `mcp_file_used` path-relativization (#1400) holds across the retest (0 absolute paths).

### Final headline metrics
| Metric | Day 0 baseline | Day 13 final | Δ | Target | Met? |
|---|---|---|---|---|---|
| Parse | 142/142 | **142/142** | +0 | ≥ 142/142 | ✅ |
| Translate | 131/142 | **135/142** | +4 | ≥ 135/142 | ✅ |
| Solve | 103/142 | **105/142** | +2 | ≥ 111/142 | ❌ (−6, all Sprint 28 deferrals) |
| Match | 59/142 | **62/142** | +3 | ≥ 66/142 | ❌ (−4, all Sprint 28 deferrals) |
| path_syntax_error | 14 | **8** | −6 | ≤ 6 | ❌ (−2; pre-existing non-#1398) |
| path_solve_terminated | 5 | **5** | +0 | ≤ 5 | ✅ |
| model_infeasible | 4 | **8** | +4 | ≤ 3 | ❌ (forward bucket moves: fawley/otpop/camshape/cesam/agreste/lnts + camcge + **mine** #1224) |
| Tests | 4,737 | **4,779** | +42 | ≥ 4,750 | ✅ |
| Determinism | n/a | **byte-identical ×3** | n/a | byte-identical × 3 seeds | ✅ |

**Realized vs target:** Parse / Translate / Tests / Determinism **met**; Solve / Match / path_syntax_error / model_infeasible **missed** — every miss is attributable to a documented **Sprint 28 carryforward** (not a regression). Translate +4 = #1381 Pattern-C unblocks + #1385 srpchase + **#1224 mine**. Solve +2 = qdemo7 (#1398) + cesam2 (#1381). Match +3 = qdemo7 + cesam2 + launch (#1378). model_infeasible rose because P5 (#1356/#1357) moved fawley/otpop **forward** from `path_syntax_error` to `model_infeasible`, and #1224 added mine (translates → infeasible; its Solve needs the Sprint 28 parameter-valued-offset KKT cross-term).

### Named non-success buckets (final)
- **model_infeasible (8):** agreste, camcge, camshape, cesam, fawley, lnts, **mine**, otpop.
- **path_syntax_error (8):** clearlak, dinam, ganges, gangesx, indus, sample, turkey, turkpow.
- **path_solve_license (9):** egypt, ferts, glider, robot, shale, sroute, srpchase, tabora, tfordy.
- **path_solve_terminated (5):** dyncge, elec, maxmin, tricp, twocge.

### Sprint 28 carryforwards filed (in their `docs/issues/ISSUE_*.md`)
- **#1390** kand tree-predicate Sum (re-diagnose true mismatch source) · **#1393 + #1335** otpop scalar-eq Sum-collapse (`stationarity.py` symbolic-collapse + `_try_eval_offset` `card(t)-ord(t)`) · **#1387** cclinpts (AD offset-enum + re-symbolization-anchor + non-convex warm-start) · **#1388** camshape Case-(b) `stat_r` divergence (`#1424` landed; `stat_r` fix remains) · **#1224** mine Solve (parameter-valued-offset KKT cross-term inversion) · **#1385** runtime-guard cross-terms · **#1374** `.l` denominator/override dedup shape (robot) · **#1400** `message`-field captured-warning path relativization · **camcge** singular-Jacobian CGE degeneracy.

### KUs verified (cumulative)
- All Sprint 27 KUs resolved across Days 0–13 (KU 8.1/8.2/9.4 closed Day 13; 6.1/6.2 Day 12; 4.1/4.2 Day 9; 3.x re-planned Day 0/5; 7.x Days 6/11; 5.x Day 5; 1.x Days 0–1).

### Deliverables
- `src/emit/emit_gams.py` (#1374), `scripts/gamslib/run_full_test.py` (#1400); regenerated otpop/dinam goldens + `mine_mcp.gms` (+Translate); cleaned `gamslib_status.json` (final metrics, relative paths); 2 new test files; ISSUE_1374/KNOWN_UNKNOWNS updates.
- This final SPRINT_LOG entry + `SPRINT_RETROSPECTIVE.md`.

---

## End-of-Sprint Cumulative Summary

### Per-priority delivery status
| Priority | Issue(s) | Status | Solve gain | Match gain | Notes |
|---|---|---|---|---|---|
| 1 | #1398 | ✅ LANDED | +1 | +1 | qdemo7 → compare_match (Phase A cross-set alias-sum gate fix) |
| 2 | #1381 | ✅ LANDED | +1 | +1 | cesam2 → match (Pattern C Phase B); camcge → model_infeasible (CGE degeneracy → S28) |
| 3 | #1390 | ⏭ Sprint 28 | 0 | 0 | re-REPLAN'd (phantom-term collapse proven inert; re-diagnose true mismatch) |
| 3 | #1385 | ✅ LANDED (translate-only) | 0 | 0 | srpchase translate <10s (was >180s); cross-terms → S28 |
| 3 | #1393+#1335 | ⏭ Sprint 28 | 0 | 0 | Approach C disproven inert Day 0; now distinct fixes |
| 4 | #1378 | ✅ LANDED | 0 | +1 | launch → match (double-applied self-ref param under --nlp-presolve) |
| 5 | #1356 + #1357 | ✅ LANDED (forward move) | 0 | 0 | comp_up narrowing cleared $171; fawley/otpop → model_infeasible (need S28) |
| 6 | #1224 | ✅ LANDED (translate-only) | 0 | 0 | mine +1 Translate; Solve (param-offset KKT cross-term) → S28 |
| 7 | #1387 + #1388 | ⏭ Sprint 28 (#1424 landed) | 0 | 0 | both multi-bug; #1388's subset-corruption (#1424) fixed, stat_r → S28; #1387 → S28 |
| 8 | #1400 | ✅ LANDED | n/a | n/a | mcp_file_used repo-relative; determinism ✅ |
| 9 | #1374 | ✅ LANDED (.fx shape) | n/a | n/a | otpop/dinam deduped; .l shape (robot) → S28 |
| — | #1424 (new, found Day 11) | ✅ LANDED | 0 | 0 | dynamic-subset blanket corruption; camshape/cclinpts domains corrected |

**Net realized:** Translate **+4** (131→135), Solve **+2** (103→105), Match **+3** (59→62). Targets (Solve ≥111 / Match ≥66) missed by exactly the Sprint 28 deferrals (#1390, #1393+#1335, #1387, #1388 stat_r, camcge, #1224 Solve).

### Process recommendations delivery
| Rec | Description | Status |
|---|---|---|
| PR20 | Phase 0 acceptance-gate codified + 4 backlog issue sections | ✅ done in prep (Task 2 / PR #1403) |
| PR21 | Prep-task end-to-end emit verification template | ✅ done in prep (Task 6 / Priority 3 risk assessment) |
| PR22 | Mid-sprint audit script | ✅ done in prep (Task 9 / PR #1410) |
| PR23 | CI-workflow PR self-review checklist | ✅ done in prep (Task 10 / PR #1411) |

### Total hours spent
- **Budgeted:** ≤ 168h
- **Actual:** TBD
- **Slack used:** TBD

### Related documents
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md`
- `docs/planning/EPIC_4/SPRINT_27/prompts/PLAN_PROMPTS.md`
- `docs/planning/EPIC_4/SPRINT_27/BASELINE_METRICS.md`
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md`
- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md`
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 27"

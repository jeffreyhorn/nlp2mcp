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
| Parse success | 142/142 | TBD | TBD | TBD | ≥ 142/142 |
| Translate success | 131/142 | TBD | TBD | TBD | ≥ 135/142 |
| Solve success | 103/142 | TBD | TBD | TBD | ≥ 111/142 |
| Solution match | 59/142 | TBD | TBD | TBD | ≥ 66/142 |
| path_syntax_error | 14 | TBD | TBD | TBD | ≤ 6 |
| path_solve_terminated | 5 | TBD | TBD | TBD | ≤ 5 (maintain) |
| model_infeasible | 4 | TBD | TBD | TBD | ≤ 3 |
| Tests passing | 4,737 | TBD | TBD | TBD | ≥ 4,750 |
| Determinism (3 `PYTHONHASHSEED`) | n/a | n/a | n/a | TBD | byte-identical |

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
- **Doc fix:** `PRIORITY_1_ANCHOR_MAPPING.md` §4.1/§4.2/§4.4 grep specs for qdemo7/ferts/ganges document the *buggy baseline* (swapped arg order) — update to the corrected source-order shapes before they gate the PR.
- Regenerate the full 15-model #1398 cohort + bucket-provenance (egypt/shale/qsambal/harker/tfordy/gangesx/srpchase timed out at the 120s cap on Day 1 — re-run with a longer cap); verify qdemo7 → compare_match, etc.
- Open the P1 PR (PR14 + PR20 cross-reference; pure `src/kkt/stationarity.py` change → PR23 N/A).

---

## Day 2 — Priority 1 full regression + PR open

**Date:** TBD
**Status:** 🔵 NOT STARTED
**Hours budgeted:** ≤ 10
**Hours actual:** —

### Tasks completed
- _(to be filled in during execution)_

### Deliverables
- _(to be filled in during execution)_

### KUs verified
- _(to be filled in during execution)_

### Carryforward to Day 3
- _(to be filled in during execution)_

### PR opened
- _(P1 #1398 PR link + PR14 regenerated `.gms` artifact list (via PR22 audit script) + PR20 Phase 0 cross-reference to `PRIORITY_1_ANCHOR_MAPPING.md` §4 anchor-by-anchor hand-derived KKT shapes. PR23 not applicable — pure `src/kkt/stationarity.py` change.)_

---

## Day 3 — Priority 1 merge + Priority 2 Phase 0 start

**Date:** TBD
**Status:** 🔵 NOT STARTED
**Hours budgeted:** ≤ 8
**Hours actual:** —

### Tasks completed
- _(to be filled in during execution)_

### Deliverables
- _(to be filled in during execution)_

### KUs verified
- _(target: KU 1.3 ✅ VERIFIED on merge)_

### Carryforward to Day 4
- _(to be filled in during execution)_

### PR merged
- _(P1 #1398 PR — merge SHA + bucket-recovery summary)_

---

## Day 4 — Priority 2 Pattern C Phase B implement

**Date:** TBD
**Status:** 🔵 NOT STARTED
**Hours budgeted:** ≤ 12
**Hours actual:** —

### Tasks completed
- _(to be filled in during execution)_

### Deliverables
- _(to be filled in during execution)_

### KUs verified
- _(target: 2.1, 2.2, 2.3)_

### Carryforward to Day 5
- _(to be filled in during execution)_

### PR opened
- _(P2 #1381 PR link)_

---

## Day 5 — Checkpoint 1: Pipeline Retest + Priority 5 start + Priority 3 first sub-priority

**Date:** TBD
**Status:** 🔵 NOT STARTED
**Hours budgeted:** ≤ 10
**Hours actual:** —

### Checkpoint 1 metrics (from full pipeline retest)
| Metric | Day 0 | Day 5 | Δ |
|---|---|---|---|
| Solve | 103 | TBD | TBD |
| Match | 59 | TBD | TBD |
| path_syntax_error | 14 | TBD | TBD |
| Translate | 131 | TBD | TBD |
| Tests | 4,737 | TBD | TBD |

### PR22 audit-script Day 5 output
_(paste `/tmp/sprint27_day5_retest.md` here)_

### Bucket-provenance updates (per PR17)
_(table: model → Day 0 bucket → Day 5 bucket; rationale)_

### Tasks completed
- _(to be filled in)_

### Deliverables
- _(to be filled in)_

### KUs verified
- _(to be filled in)_

### Carryforward to Day 6
- _(to be filled in)_

---

## Day 6 — Priority 3 #1390 kand + parallel Priority 5 #1357 otpop

**Date:** TBD
**Status:** 🔵 NOT STARTED
**Hours budgeted:** ≤ 12
**Hours actual:** —

### Tasks completed
- _(to be filled in)_

### Deliverables
- _(to be filled in)_

### KUs verified
- _(target: KU 3.1)_

### Carryforward to Day 7
- _(to be filled in)_

---

## Day 7 — #1390 PR + Priority 3 #1385 srpchase + Priority 5 close

**Date:** TBD
**Status:** 🔵 NOT STARTED
**Hours budgeted:** ≤ 12
**Hours actual:** —

### Tasks completed
- _(to be filled in)_

### Deliverables
- _(to be filled in)_

### KUs verified
- _(target: KUs 3.2, 5.1, 5.2, 5.3)_

### Carryforward to Day 8
- _(to be filled in)_

### PRs opened
- _(#1390 PR, P5 combined fawley+otpop PR)_

---

## Day 8 — #1385 PR + Priority 3 #1393+#1335 + Priority 7 #1387 start

**Date:** TBD
**Status:** 🔵 NOT STARTED
**Hours budgeted:** ≤ 12
**Hours actual:** —

### Tasks completed
- _(to be filled in)_

### Deliverables
- _(to be filled in)_

### KUs verified
- _(target: KU 3.3)_

### Carryforward to Day 9
- _(to be filled in)_

### PRs opened
- _(#1385 PR; #1387 Phase 0 in progress)_

---

## Day 9 — Priority 3 close + Priority 4 launch numerics start

**Date:** TBD
**Status:** 🔵 NOT STARTED
**Hours budgeted:** ≤ 10
**Hours actual:** —

### Tasks completed
- _(to be filled in)_

### Deliverables
- _(to be filled in)_

### KUs verified
- _(target: KUs 3.4, 3.5, 4.1, 4.2)_

### Carryforward to Day 10
- _(to be filled in)_

### PRs merged
- _(all Priority 3 PRs)_

---

## Day 10 — Checkpoint 2: Pipeline Retest + Priority 4 close + Priority 7 #1387 implement

**Date:** TBD
**Status:** 🔵 NOT STARTED
**Hours budgeted:** ≤ 10
**Hours actual:** —

### Checkpoint 2 metrics (from full pipeline retest)
| Metric | Day 0 | Day 5 | Day 10 | Δ Day 0 → Day 10 |
|---|---|---|---|---|
| Solve | 103 | TBD | TBD | TBD |
| Match | 59 | TBD | TBD | TBD |
| path_syntax_error | 14 | TBD | TBD | TBD |
| Translate | 131 | TBD | TBD | TBD |
| Tests | 4,737 | TBD | TBD | TBD |

### PR22 audit-script Day 10 output
_(paste `/tmp/sprint27_day10_retest.md` here)_

### Bucket-provenance updates
_(table)_

### Tasks completed
- _(to be filled in)_

### Deliverables
- _(to be filled in)_

### KUs verified
- _(to be filled in)_

### Carryforward to Day 11
- _(to be filled in)_

---

## Day 11 — Priority 7 #1388 discriminator + #1387 close + Priority 6 #1224 start

**Date:** TBD
**Status:** 🔵 NOT STARTED
**Hours budgeted:** ≤ 10
**Hours actual:** —

### #1388 §4.6 3-way discriminator result
- **NLP-warm-start MODEL STATUS:** TBD
- **All 10 warm-startable symbols verified loaded (3 primals + 7 multipliers):** TBD
- **Per-term Phase 0 shape-divergence grep result (non-inert?):** TBD
- **Case classification:** TBD (a / b / c)
- **Action:** TBD (Sprint 27 fix OR Sprint 28 carryforward)

### Tasks completed
- _(to be filled in)_

### Deliverables
- _(to be filled in)_

### KUs verified
- _(target: KUs 7.1, 7.2, 7.3)_

### Carryforward to Day 12
- _(to be filled in)_

---

## Day 12 — Priority 6 close + Priority 8 #1400 + Priority 9 #1374

**Date:** TBD
**Status:** 🔵 NOT STARTED
**Hours budgeted:** ≤ 10
**Hours actual:** —

### Tasks completed
- _(to be filled in)_

### Deliverables
- _(to be filled in)_

### KUs verified
- _(target: KUs 6.2, 8.1, 8.2, 9.4)_

### Carryforward to Day 13
- _(to be filled in)_

### #1400 absolute-path-leak audit-grep result
_(paste `grep -oE '"[^"]+": "/[^"]+"' data/gamslib/gamslib_status.json | sort -u` output)_

### #1374 corpus-sweep results
- **Total models scanned:** TBD
- **Models with duplicate-init pattern:** TBD
- **Distinct shapes found:** TBD
- **Sprint 27 fix scope:** TBD shapes (most common)
- **Sprint 28 carryforward:** TBD shapes

---

## Day 13 — Final Pipeline Retest + SPRINT_LOG + SPRINT_RETROSPECTIVE

**Date:** TBD
**Status:** 🔵 NOT STARTED
**Hours budgeted:** ≤ 8
**Hours actual:** —

### Final pipeline retest under 3 `PYTHONHASHSEED` values
| `PYTHONHASHSEED` | Solve | Match | path_syntax_error | Translate | Tests | `gamslib_status.json` SHA256 (modulo wall-time) |
|---|---|---|---|---|---|---|
| 0 | TBD | TBD | TBD | TBD | TBD | TBD |
| 1 | TBD | TBD | TBD | TBD | TBD | TBD |
| 42 | TBD | TBD | TBD | TBD | TBD | TBD |

### Final headline metrics
| Metric | Day 0 baseline | Day 13 final | Δ | Target | Met? |
|---|---|---|---|---|---|
| Parse | 142/142 | TBD | TBD | ≥ 142/142 | TBD |
| Translate | 131/142 | TBD | TBD | ≥ 135/142 | TBD |
| Solve | 103/142 | TBD | TBD | ≥ 111/142 | TBD |
| Match | 59/142 | TBD | TBD | ≥ 66/142 | TBD |
| path_syntax_error | 14 | TBD | TBD | ≤ 6 | TBD |
| path_solve_terminated | 5 | TBD | TBD | ≤ 5 | TBD |
| model_infeasible | 4 | TBD | TBD | ≤ 3 | TBD |
| Tests | 4,737 | TBD | TBD | ≥ 4,750 | TBD |
| Determinism | n/a | TBD | n/a | byte-identical × 3 seeds | TBD |

### PR22 audit-script Day 13 final output
_(paste `/tmp/sprint27_day13_final.md` here)_

### Sprint 28 carryforwards filed
- _(list of issues + their Sprint 28 priority placement, e.g., "#1388 camshape Case (c) → Sprint 28 Priority TBD; #1374 deferred shapes → Sprint 28 observation task")_

### KUs verified (cumulative)
- _(target: all 28 ✅ VERIFIED)_

### Deliverables
- SPRINT_LOG.md final entry (this file)
- SPRINT_RETROSPECTIVE.md (separate file)

---

## End-of-Sprint Cumulative Summary

### Per-priority delivery status
| Priority | Issue(s) | Status | Solve gain | Match gain | Notes |
|---|---|---|---|---|---|
| 1 | #1398 | TBD | TBD | TBD | TBD |
| 2 | #1381 | TBD | TBD | TBD | TBD |
| 3 | #1390 | TBD | TBD | TBD | TBD |
| 3 | #1385 | TBD | TBD | TBD | TBD |
| 3 | #1393+#1335 | TBD | TBD | TBD | TBD |
| 4 | #1378 | TBD | TBD | TBD | TBD |
| 5 | #1356 + #1357 | TBD | TBD | TBD | TBD |
| 6 | #1224 | TBD | TBD | TBD | TBD |
| 7 | #1387 + #1388 | TBD | TBD | TBD | TBD |
| 8 | #1400 | TBD | n/a | n/a | TBD (pipeline-determinism only) |
| 9 | #1374 | TBD | TBD | TBD | TBD |

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

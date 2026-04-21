# Sprint 25 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 25 begins
**Timeline:** Complete before Sprint 25 Day 1
**Goal:** Set up Sprint 25 for success — Alias Differentiation Carryforward & Emitter Backlog (solve 99 → ≥ 105, match 54 → ≥ 62)

**Key Insight from Sprint 24:** Two consecutive sprints (S23 + S24) targeted alias-aware differentiation as Priority 1 and both only partially landed it. The failure mode was "Day-1 start but Days 4–7 absorbed by other urgent work." Sprint 25 prep must (a) defend the 8–12-day alias-AD block per PR11, (b) front-load root-cause analysis so Day 1 execution is not blocked on classification, and (c) verify the #1283 parser non-determinism fix plan early because it may be confounding other ongoing investigations. Day 13 Addendum confirmed translate-recovery alone is low-leverage for Match — emitter/stationarity cleanup on recovered models is the downstream leverage point (PR13).

**Branching:** All prep task branches should be created from `main` and PRs should target `main`.

---

## Executive Summary

Sprint 25 inherits the alias-aware differentiation workstream from Sprint 24, with 11 open issues (#1138–#1147, #1150) affecting ~20 models. This is the single highest-leverage workstream for Match rate (54 → ≥ 62). Alongside alias-AD, Sprint 25 clears the emitter / stationarity bug backlog surfaced during the Sprint 24 Day 13 review (#1275–#1281, #1283 — 8 issues), which is the leverage point for the 5 "recovered translates that don't solve" (`ganges`, `gangesx`, `ferts`, `clearlak`, `turkpow`) identified in the Day 13 Addendum. Lower-priority work includes the multi-solve gate extension (#1270), the loop-tree dispatcher refactor (#1271), and algorithmic attacks on 5 remaining hard translation timeouts.

This prep plan focuses on:

1. **Risk identification** — Sprint 25 Known Unknowns List covering alias-AD completion risk, emitter-backlog scope, non-determinism root cause, and recovered-translate outcomes
2. **Alias-AD carryforward analysis** — Survey of Sprint 24's partial progress; Pattern A/B/C/D reclassification of the 11 open issues; rollout design
3. **Non-determinism root-cause prep** — Early investigation of #1283 (multi-row-label table parsing), since it may have been contaminating chenery's #1177 investigation throughout Sprint 24
4. **Emitter backlog categorization** — Group 7 emitter bugs by code path and fix complexity; identify parallelizable work
5. **Recovered-translate leverage analysis** — Map which emitter fixes unblock which of the 5 `ganges`-family models
6. **Determinism infrastructure (PR12)** — Design a byte-stability regression test across `PYTHONHASHSEED` values
7. **Baseline establishment (PR6, PR15)** — Full pipeline baseline + freeze v2.2.x exclusions before Day 0
8. **Sprint planning** — Detailed schedule with 2 checkpoints (Day 5, Day 10) and day-by-day prompts

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|----------------------|
| 1 | Create Sprint 25 Known Unknowns List | Critical | 2–3h | None | All priorities — risk identification |
| 2 | Audit Alias-AD Carryforward State | Critical | 3–4h | Task 1 | Priority 1: alias differentiation (~20 models) |
| 3 | Investigate Parser Non-Determinism (#1283) | Critical | 2–3h | Task 1 | Priority 2 leader: #1283 fix blocks confident retest |
| 4 | Categorize Emitter Bug Backlog (#1275–#1281) | High | 2–3h | Task 1 | Priority 2: emitter fixes (7 issues) |
| 5 | Analyze Recovered-Translate Models | High | 2–3h | Task 4 | Priority 2: leverage mapping |
| 6 | Design Alias-AD Rollout Plan | Critical | 3–4h | Task 2 | Priority 1: Day 1–12 schedule |
| 7 | Scope Multi-Solve Gate + Dispatcher Refactor | Medium | 2–3h | Task 1 | Priorities 3, 4 |
| 8 | Profile Hard Translation Timeouts (5 models) | Low | 2–3h | None | Priority 5 (low leverage per PR13) |
| 9 | Run Full Pipeline Baseline + Freeze Scope (PR6 / PR15) | Critical | 1–2h | None | All priorities — baseline metrics |
| 10 | Design Byte-Stability Test Infrastructure (PR12) | High | 1–2h | Task 3 | Process — determinism guard |
| 11 | Plan Sprint 25 Detailed Schedule | Critical | 3–4h | Tasks 1–10 | All priorities — sprint planning |

**Total Estimated Time:** 23–34 hours (~3–4.5 working days)

**Critical Path:** Task 1 → Task 2 → Task 6 → Task 11 (alias-AD design chain)
**Secondary Path:** Task 1 → Task 3 → Task 10 → Task 11 (determinism infrastructure chain)
**Parallelizable:** Tasks 4 + 5 (emitter backlog); Task 7 (small-design items); Task 8 (timeout profiling); Task 9 (baseline)

---

## Task 1: Create Sprint 25 Known Unknowns List

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 25 Day 1
**Owner:** Sprint planning
**Dependencies:** None

### Objective

Create proactive list of assumptions and unknowns for Sprint 25 to prevent late discoveries during implementation. This is the first task because it surfaces risks that inform the design of all other prep tasks — particularly the alias-AD rollout (Task 6) and the Priority 2 emitter-backlog ordering (Task 4).

### Why This Matters

Sprint 24's end-of-sprint discoveries (KU-27 through KU-32 in `docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md`) included the Lark 1.1.9 vs 1.2+ ambiguity (resolved in PR #1267), the `requirements.txt` pinning divergence (process lesson), and the emitter/stationarity backlog that seeded issues #1275–#1281 and #1283. Sprint 25's highest-risk area is alias-AD architectural correctness — a third consecutive attempt at the same workstream — and early documentation of the specific regressions and edge cases to guard against is the single most valuable prep activity.

### Background

- Sprint 24 Known Unknowns: `docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md` (26 prep + 6 end-of-sprint KUs across 6 categories)
- Sprint 24 Retrospective: `docs/planning/EPIC_4/SPRINT_24/SPRINT_RETROSPECTIVE.md` (§Sprint 25 Recommendations, §New Recommendations PR12–PR15)
- 18+ issues labeled `sprint-25` in GitHub (11 alias-AD, 7 emitter/stationarity, 1 non-determinism, 3 translation timeout, plus multi-solve gate extension + dispatcher refactor)
- Sprint 24 carryforward KUs: KU-29 (saras-style multi-solve), KU-30 (dispatcher duplication), KU-31 (decomp emitter bugs), KU-32 (sameas guard validation)

### What Needs to Be Done

1. **Review Sprint 24 deferred / carryforward KUs** — KU-29 through KU-32 continue into Sprint 25; also KU-13 and KU-17 (influx risk) which were marked INCOMPLETE pending the actual alias-AD landing.

2. **For each Priority area, brainstorm unknowns:**

   **Priority 1 (Alias-AD Carryforward):**
   - Which of the 11 issues share Pattern A (summation index) vs Pattern B (bound-index guard) vs Pattern C (offset-alias) vs Pattern D (condition-scope)?
   - Will the completed fix regress any of the 54 currently-matching models? (Dispatch is the canary; what are the other high-risk golden models?)
   - Is `#1150` (AD regression: distinct sum indices collapse) the same root cause as the `#1137`-family?
   - Can the fix be feature-flagged for rollout, or is it all-or-nothing?
   - Does `sameas()` guard generation affect compile time on large CGE models?

   **Priority 2 (Emitter/Stationarity Backlog):**
   - Is `#1283` (non-deterministic table parsing) a dict/set iteration-order bug, a regex backtracking bug, or a Lark ambiguity issue?
   - Will the `#1275` presolve-path fix affect any committed MCP artifacts (diff churn)?
   - Do `#1277` and `#1278` twocge bugs share a root cause with `#1143` polygon (Pattern C)?
   - How many of the 5 `ganges`-family recovered-translate models are unblocked by each individual emitter fix?
   - Does fixing `#1281` (lmp2 duplicate Parameter) accidentally remove legitimate declarations in other models?

   **Priority 3 (Multi-Solve Gate Extension):**
   - Does Approach A (cross-reference) produce false positives on any corpus model's post-solve reporting?
   - Are there corpus models besides `saras` that the extended gate should catch?

   **Priority 4 (Dispatcher Refactor):**
   - Is the substituting dispatcher genuinely equivalent after refactor, or are there subtle differences in how silent grammar tokens are handled?
   - How many currently-tracked MCP outputs will byte-diff after the refactor? (Target: zero.)

   **Priority 5 (Hard Translation Timeouts):**
   - Are any of `iswnm` / `mexls` / `nebrazil` / `sarf` / `srpchase` actually tractable with a different differentiation algorithm (e.g., reverse-mode AD, sparse Jacobian)?
   - Is the bottleneck in parsing, IR construction, AD, KKT assembly, or emission?

   **Cross-cutting:**
   - Will the PR12 determinism regression test catch `#1283`-class bugs in other models?
   - What's the realistic error-influx budget for alias-AD landings? (Day 13 Addendum showed 100% for translate-recovery but alias-AD may have different dynamics.)

3. **Categorize by topic, prioritize by risk, define verification method.**

4. **Assign verification deadlines** (Day 0–1 for Critical, Day 2–3 for High, Day 5+ for Medium/Low).

5. **Create document** following `../SPRINT_24/KNOWN_UNKNOWNS.md` format, including a Task-to-Unknown mapping table.

### Changes

Created `docs/planning/EPIC_4/SPRINT_25/KNOWN_UNKNOWNS.md` with 27 unknowns across 6 categories. Updated Tasks 2–11 of this PREP_PLAN with "Unknowns Verified" metadata lines mapping each prep task to the specific unknowns it researches. Added CHANGELOG.md entry summarizing Task 1 completion.

### Result

27 unknowns documented across 6 categories:

- **Category 1: Alias-AD Carryforward** (8 KUs, 1.1–1.8) — pattern classification, regression risk on 54 matching models, #1150 relationship, derivative-rule scope, sameas guards, offset-alias Pattern C, model_infeasible recovery, rollout strategy.
- **Category 2: Emitter / Stationarity Backlog** (6 KUs, 2.1–2.6) — #1283 root cause, #1283 scope, presolve-path fixes (#1275), twocge subsume analysis (#1277/#1278), #1281 dedup safety, recovered-translate leverage mapping.
- **Category 3: Multi-Solve Gate Extension** (3 KUs, 3.1–3.3) — Approach A false-positive risk, beyond-saras coverage, partssupply regression.
- **Category 4: Dispatcher Refactor** (3 KUs, 4.1–4.3) — equivalence verification, byte-diff baseline, translate-time overhead.
- **Category 5: Translation Timeout — Algorithmic** (4 KUs, 5.1–5.4) — tractability per model, stage-level profiling, sparse Jacobian feasibility, `srpchase` distinctness.
- **Category 6: Pipeline Retest + Determinism** (3 KUs, 6.1–6.3) — scope-freeze durability, PYTHONHASHSEED sample size, alias-AD influx assumption.

Priority distribution: Critical 7 (26%), High 11 (41%), Medium 7 (26%), Low 2 (7%). Research is performed across prep Tasks 2–11; the authoritative task-time budget is 21–31 hours for Tasks 2–11 (per the §Prep Task Overview table). Individual per-KU estimates in KNOWN_UNKNOWNS.md sum higher because many unknowns are verified in parallel within a single task (e.g., Task 2 verifies 7 unknowns simultaneously during one code-audit pass).

Sprint 24 carryforward KUs (KU-29, KU-30, KU-32, KU-13/17) are mapped into Sprint 25 unknown numbers in the document's Appendix.

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_25/KNOWN_UNKNOWNS.md && echo "EXISTS" || echo "MISSING"
wc -l docs/planning/EPIC_4/SPRINT_25/KNOWN_UNKNOWNS.md
# Count only numbered unknowns (exclude the template header "Unknown X.Y: ...")
grep -cE "^## Unknown [0-9]+\.[0-9]+:" docs/planning/EPIC_4/SPRINT_25/KNOWN_UNKNOWNS.md
# Expected: 27
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_25/KNOWN_UNKNOWNS.md` with 27 unknowns across 6 categories
- Task-to-Unknown mapping table (Appendix)
- "Unknowns Verified" metadata added to PREP_PLAN.md Tasks 2–11
- CHANGELOG.md updated with Task 1 completion entry

### Acceptance Criteria

- [x] ≥ 20 unknowns documented (27 created)
- [x] All 5 priority areas have at least 3 unknowns each (Category 1: 8, Category 2: 6, Category 3: 3, Category 4: 3, Category 5: 4, Category 6: 3)
- [x] Sprint 24 carryforward KUs (KU-29, KU-30, KU-32, plus KU-13/17) mapped to Sprint 25 numbers (Appendix)
- [x] Verification deadlines assigned (Day 0–1 for Critical, Day 2–3 for High)
- [x] Task-to-Unknown mapping includes this prep plan's Tasks 2–11

---

## Task 2: Audit Alias-AD Carryforward State

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 25 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 1 (KU list informs which edge cases to look for)
**Unknowns Verified:** 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 1.8

### Objective

Survey exactly what landed in Sprint 24's partial alias-AD work, classify the 11 remaining open issues by Pattern (A/B/C/D), and produce a state-of-play document that Task 6 (rollout design) can build on. This is the single most important analysis task — getting it wrong leads to the Sprint 24 outcome ("Day 1 starts but classification drift stalls Day 4–7").

### Why This Matters

Sprint 24's Priority 1 was alias-AD, but the sprint ended with 11 issues deferred. The retrospective noted this was because "Days 4–7 were absorbed by other urgent fixes" and "the architectural complexity doesn't shrink to fit a compressed schedule." Sprint 25's alias-AD effort needs to start Day 1 with a fully-classified issue list and a known pass/fail state for each pattern — not re-derive that on-the-fly.

### Background

- Sprint 24 retrospective §What Could Be Improved #1: "Alias Differentiation Didn't Fully Land"
- Sprint 24 Day 1–3 findings in `../SPRINT_24/SPRINT_LOG.md` (Pattern A single-index sum collapse, Pattern C offset-alias, Pattern D condition-scope)
- Existing design doc: `docs/planning/EPIC_4/SPRINT_24/DESIGN_ALIAS_DIFFERENTIATION_V2.md`
- Sprint 24 Day 5 Checkpoint 1 evaluation (3 regressions → fixed → GO with narrowed guards)
- 11 open issues: #1138 (CGE), #1139 (meanvar), #1140 (PS-family), #1141 (kand), #1142 (launch), #1143 (polygon), #1144 (catmix), #1145 (cclinpts), #1146 (himmel16), #1147 (camshape), #1150 (AD regression)
- Related KUs from Sprint 24: KU-01 (Pattern A), KU-04 (Pattern C offset-alias), KU-13 (influx), KU-17 (infeasibility influx)

### What Needs to Be Done

1. **Inventory landed Sprint 24 work:**
   - Grep `src/ad/` and `src/kkt/` for summation-context / alias-match helpers added during Sprint 24
   - Read PRs merged during Sprint 24 that touched alias-AD (cross-reference with SPRINT_LOG.md Day-by-day entries)
   - Document what's partial vs complete (e.g., single-index sum collapse landed; multi-index `_partial_collapse_sum` did not)

2. **Re-run each of the 11 open issues' reproductions:**
   - For each issue, attempt a translate + solve on the corpus model today
   - Record current state: pass / near-pass / fail, and the specific failure signature
   - Cross-reference with the Day 13 Addendum `gamslib_status.json` for each model's solve outcome

3. **Classify each open issue by Pattern:**
   - Pattern A (summation index): which issues fall here?
   - Pattern B (bound-index guard): which?
   - Pattern C (offset-alias): which?
   - Pattern D (condition-scope): which?
   - Note any that are now in Pattern E (non-differentiation bug) per the Sprint 23 classification

4. **Map Pattern → architectural fix site:**
   - Which code paths in `src/ad/` need changes?
   - Are any issues dependent on each other (fix order matters)?
   - Which issues are "subsumed by" the primary fix vs "need separate work"?

5. **Identify regression risks among the 54 currently-matching models:**
   - Which of the 54 use aliases? (Sprint 23 identified 8 alias users: dispatch, gussrisk, nemhaus, ps2_f, ps3_f, quocge, ship, splcge — re-verify)
   - Rank canary-test priority beyond dispatch

### Changes

- Created `docs/planning/EPIC_4/SPRINT_25/AUDIT_ALIAS_AD_CARRYFORWARD.md` — 7-section state-of-play document covering:
  - Landed-vs-stubbed inventory for Sprint 23 base layer + Sprint 24 additions (helpers, guards, emitter fixes) in `src/ad/derivative_rules.py` and `src/kkt/stationarity.py` with exact line references.
  - Full classification table for all 11 open alias issues (#1138, #1139, #1140, #1141, #1142, #1143, #1144, #1145, #1146, #1147, #1150) including current reproduction state (translate/solve/compare/rel_diff) as of the Day 13 Addendum snapshot.
  - Pattern A/B/C/D/E section headings with S24-vs-S25 deltas (Patterns B and D reclassified empty; Pattern E gained kand; Pattern A gained launch).
  - Fix-site map from each active Pattern to specific source locations; subsume-opportunity graph; dependency graph (Pattern C depends on Pattern A).
  - Canary-test priority ladder, Tier 0–Tier 5 (6 tiers: dispatch → alias-users → golden-file → Pattern A targets → Pattern C targets → infeasibility-adjacent informational).
  - Cross-reference to Sprint 24 KU-01 / KU-04 / KU-13 / KU-17.
  - Open questions explicitly routed to Task 6 (rollout design).
- Updated `docs/planning/EPIC_4/SPRINT_25/KNOWN_UNKNOWNS.md` — Verification Results filled in for Unknowns 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 1.8 (status changed from 🔍 INCOMPLETE → ✅ VERIFIED, with findings/evidence/decision sections). Unknown 1.5 remains INCOMPLETE because its verification activity is Task 6's remit.

### Result

- **Pattern distribution (revised from Sprint 24):** Pattern A = 6 issues / ~16 comparison-scope models (#1138, #1139, #1140, #1142, #1145, #1150; #1140's authoritative list per ISSUE_1140 = ps2_f_s, ps2_s, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp, ps10_s); Pattern C = 2 issues (#1143, #1146); Pattern E = 3 issues (#1141, #1144, #1147) routed out of scope. Patterns B and D are empty.
- **Pattern reclassifications from Sprint 24 Day 9 investigations:** kand (#1141) moved B → E (multi-solve comparison bug, not AD); launch (#1142) moved D → A (alias-family per Day 9 #1226).
- **Landed inventory:** Sprint 23's `bound_indices`/`_alias_match`/`_same_root_set`/`_partial_collapse_sum` threading is fully in place. Sprint 24 added `_collect_bound_indices`, `_find_var_indices_in_body`, single-index sum-collapse concrete→symbolic recovery (Day 3), `_apply_alias_offset_to_deriv` (Day 4), `_body_has_alias_sum` + `_var_inside_alias_sum` + `_var_has_alias_coindex` narrowed guards (Day 5), and `_replace_indices_in_expr` IndexOffset.base emitter canonicalization (Day 6).
- **Stubbed / not landed:** (1) multi-index partial-collapse concrete→symbolic (primary gap for Patterns A); (2) `IndexOffset.base` extraction in `_alias_match()` (Pattern C extension); (3) multi-position offset handling in `_apply_alias_offset_to_deriv`; (4) deep Jacobian-transpose assembly rewrite (representative-instance bug, Day 1–2 finding — out of first-round scope).
- **Regression canary list (revised):** 10 alias-using matching models (not the 8 from Sprint 23 — nemhaus dropped via MINLP exclusion; partssupply / prolog / sparta joined). Primary canary: dispatch. Tier 1 list of 10 adds 9 alias-using models (quocge, partssupply, prolog, ps2_f, ps3_f, ship, sparta, splcge, gussrisk) + paklive (non-alias-using but included defensively, since Sprint 24 Day 5 regressed it via the same `_collect_bound_indices` path). marco no longer in matching set; dropped from canary list.

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_25/AUDIT_ALIAS_AD_CARRYFORWARD.md && echo "EXISTS" || echo "MISSING"
# Document must classify all 11 open issues by Pattern
grep -cE "^### Pattern [A-E]" docs/planning/EPIC_4/SPRINT_25/AUDIT_ALIAS_AD_CARRYFORWARD.md
# Expect ≥ 4 Pattern headings with all 11 issues assigned
# ACTUAL: 5 Pattern headings (A through E, B and D marked as closed/empty); all 11 issues in classification table
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_25/AUDIT_ALIAS_AD_CARRYFORWARD.md` — state-of-play document ✅
- Pattern classification table for all 11 open issues ✅ (Section 2)
- Landed-vs-stubbed inventory for `src/ad/` and `src/kkt/` alias-AD helpers ✅ (Section 1)
- Canary test priority list (beyond `dispatch`) ✅ (Section 5)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 1.8 ✅

### Acceptance Criteria

- [x] All 11 open alias issues classified by Pattern (A/B/C/D/E)
- [x] For each issue, current reproduction state recorded (pass/near-pass/fail + signature)
- [x] Inventory of Sprint 24 landed vs stubbed alias-AD work
- [x] Regression-risk canary list beyond `dispatch`
- [x] Cross-reference with KU-01, KU-04, KU-13, KU-17 from SPRINT_24/KNOWN_UNKNOWNS.md
- [x] Unknowns 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 1.8 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: Investigate Parser Non-Determinism (#1283)

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 25 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 1 (KU list captures suspected root causes)
**Unknowns Verified:** 2.1, 2.2

### Objective

Root-cause the non-deterministic parser behavior on multi-row-label tables like `(low,medium,high).ynot`, or at minimum narrow it to 1–2 candidate code paths. A deterministic parser is a prerequisite for trusting every other Sprint 25 metric — the PR12 byte-stability infrastructure in Task 10 depends on a working fix landing early in the sprint.

### Why This Matters

The Sprint 24 Day 13 Addendum discovered that `chenery_mcp.gms` was intermittently corrupt (2 correct + 1 corrupted per 3 CLI runs). The `#1177` chenery model_infeasible investigation spent multiple Sprint 24 days debugging KKT theories against a baseline that was sometimes wrong. Until this bug is fixed, every chenery-touching investigation — and possibly any model using similar multi-row-label tables — is suspect. Front-loading the root-cause investigation lets the actual fix land Day 1–2 of Sprint 25 rather than Day 10+.

### Background

- Issue: [#1283](https://github.com/jeffreyhorn/nlp2mcp/issues/1283) — Non-deterministic multi-row-label table parsing
- In-tree doc: `docs/issues/ISSUE_1283_parser-non-deterministic-multi-row-label-table.md`
- Reproducer: `data/gamslib/raw/chenery.gms` ddat / tdat tables
- Suspected root causes (from Task 1 / issue doc):
  - Dict / set iteration order for keys containing hyphens (`light-ind`, `food+agr`)
  - Regex backtracking during column-header tokenization
  - Lark ambiguity resolution
- Related: KU-27 (Lark 1.1.9 vs 1.2+ ambiguity) resolved defensively in PR #1267 — similar pattern
- Related: KU-28 (requirements.txt pinning) — process lesson about CI-vs-local divergence

### What Needs to Be Done

1. **Reliably reproduce under controlled conditions:**
   - Run `src.cli chenery.gms` 20× with `PYTHONHASHSEED=0..19` and count correct vs corrupted runs
   - Find the minimum reproduction (smallest table that triggers the bug)
   - Check if reversed-order iteration ever produces yet a third output

2. **Narrow to the source file:**
   - Add targeted `logger.debug` calls in `src/ir/parser.py` table-parsing paths and `src/gams/gams_grammar.lark` rule handlers
   - Compare the IR between a correct and corrupted run — identify exactly where they diverge
   - Check if the Lark parse tree differs (ambiguity) or only the IR walk differs (iteration order)

3. **Document the specific trigger:**
   - What property of the column headers causes it? (Hyphens? Plus signs? Length?)
   - What property of the row labels? (Multi-value `(a,b,c).col` syntax?)
   - Is it sensitive to the number of columns / rows?

4. **Propose a fix approach** (don't implement yet — that's Sprint 25 Day 1–2 work):
   - Option A: replace intermediate `set` with `list` to force deterministic ordering
   - Option B: anchor the column-header tokenization to avoid backtracking
   - Option C: force Lark into unambiguous mode for the table rule
   - Document expected regression surface for each option

### Changes

- Created `docs/planning/EPIC_4/SPRINT_25/INVESTIGATION_PARSER_NON_DETERMINISM.md` — 7-section investigation covering:
  - Reliable reproduction recipe with `PYTHONHASHSEED=0..19` sweep
  - Minimum reproducer: 2-row-label × 3-column table with plain-ID columns (no hyphens / plus signs)
  - Root-cause narrowing via direct Lark parse-tree probes under `ambiguity="explicit"` + `ambiguity="resolve"`
  - Fix-site map and Options A–E with regression-surface analysis
  - Cross-reference to Sprint 24 KU-27 (same Earley-ambiguity family, different rule)
- Updated `docs/planning/EPIC_4/SPRINT_25/KNOWN_UNKNOWNS.md` — Verification Results filled in for Unknowns 2.1 and 2.2.

### Result

- **Corruption rate (20-seed sweep on chenery):** 13/20 = **65% corruption**; exactly 2 distinct outputs (7 correct : 13 corrupted). Initial issue-doc observation ("2 correct per 3 runs") is inverted relative to this sweep's majority; the exact ratio varies with Lark's internal tiebreak heuristics, but the 2-output structure is stable.
- **Minimum reproducer:** small GAMS table example with a `(low,medium).a  1  2  3` table row — same 7 correct : 13 corrupted distribution; rules out the hyphen/plus-sign hypothesis from the initial issue doc. Full reproducer listed in `SPRINT_25/INVESTIGATION_PARSER_NON_DETERMINISM.md` §Section 2.
- **Root cause narrowed to 1 grammar-level bug (not 2 code paths):** the `table_row_label` → `simple_label` → `dotted_label` rule chain in `src/gams/gams_grammar.lark` allows a bare `NUMBER` to parse as either a `table_value` (intended) or a `simple_label` row label (also valid). Earley finds two legal parses; `ambiguity="resolve"` picks one per run with Python-hash-seed-dependent tiebreak. This is the same family as Sprint 24 KU-27 (different ambiguous rule, same structural class).
- **Affected corpus:** 4 models (chenery, clearlak, indus, indus89). Only chenery currently exhibits the bug at the pipeline comparison layer; the other 3 are masked by unrelated downstream failures.
- **Proposed fix: Option D** (post-parse disambiguation in `_resolve_ambiguities()` that prefers the alternative packing the most `table_value` children into the fewest `table_row` nodes). Rationale: localized change, near-zero regression surface (only affects `_ambig` nodes containing `table_row`), direct precedent in Sprint 24 PR #1267's KU-27 defensive fix. Option E (PYTHONHASHSEED determinism regression test) is required as a complement.

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_25/INVESTIGATION_PARSER_NON_DETERMINISM.md && echo "EXISTS" || echo "MISSING"

# The investigation must have a reliable reproduction command and a narrowed root cause
grep -E -c "^## Reliable Reproduction|^## Narrowed Root Cause|^## Proposed Fix" \
    docs/planning/EPIC_4/SPRINT_25/INVESTIGATION_PARSER_NON_DETERMINISM.md
# Expect ≥ 3
# ACTUAL: 3 (all required section headings present)
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_25/INVESTIGATION_PARSER_NON_DETERMINISM.md`
- Reliable reproduction recipe (with `PYTHONHASHSEED` sweep)
- Minimum reproducer (smallest table that triggers it)
- Narrowed root cause or ranked candidates
- Proposed fix approach with regression-surface analysis
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.1, 2.2

### Acceptance Criteria

- [x] Corruption rate measured across ≥ 10 `PYTHONHASHSEED` values (measured across 20; 7 correct : 13 corrupted)
- [x] Root cause narrowed to ≤ 2 specific code paths (narrowed to 1: grammar-level Earley ambiguity in `table_row` → `simple_label` → `dotted_label`)
- [x] Fix approach documented with expected behavior on other table patterns (Options A–E with regression-surface analysis; Option D recommended)
- [x] Cross-reference to related KUs in Sprint 25 KNOWN_UNKNOWNS (KU-27 cross-referenced; SPRINT_25 KUs 2.1 and 2.2 updated)
- [x] Unknowns 2.1, 2.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 4: Categorize Emitter Bug Backlog (#1275–#1281)

**Status:** ✅ COMPLETE
**Priority:** High
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 25 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 1
**Unknowns Verified:** 2.3, 2.4, 2.5

### Objective

Group the 7 emitter / stationarity issues surfaced by the Sprint 24 Day 13 review into a fix-order that (a) surfaces shared code paths so one fix can subsume multiple issues and (b) identifies which fixes are parallelizable so the sprint can dispatch them across days without blocking.

### Why This Matters

The retrospective estimates the emitter backlog at 12–18 hours — short, but fragmented across 7 issues. Without categorization, Sprint 25 risks spending a day on each issue and burning the 12-day alias-AD block on emitter work. A good categorization can compress the backlog to 3–4 focused fixes (each subsuming 1–3 issues) and preserve the alias-AD time.

### Background

- 7 issues filed during Sprint 24 Day 13 review (#1275–#1281):
  - **#1275** — presolve `$include` absolute paths (emitter)
  - **#1276** — fawley duplicate `.fx` emission (emitter)
  - **#1277** — twocge `stat_tz` mixed offsets (stationarity / alias-AD adjacent)
  - **#1278** — twocge `ord(r) <> ord(r)` tautology (AD / substitution)
  - **#1279** — robustlp `defobj(i)` scalar-equation widening (IR normalize)
  - **#1280** — mathopt4 unquoted UELs with dots (emitter)
  - **#1281** — lmp2 duplicate `Parameter` declarations (emitter)
- In-tree docs: `docs/issues/ISSUE_127{5,6,7,8,9}_*.md`, `docs/issues/ISSUE_1280_*.md`, `docs/issues/ISSUE_1281_*.md`
- Sprint 24 retrospective suggests: fix #1283 first (non-determinism), then emitter bugs in parallel, then stationarity bugs (which may overlap with alias-AD)

### What Needs to Be Done

1. **Re-read each issue's in-tree doc** to understand the fix scope.

2. **Classify each issue by code path:**
   - **Emitter (`src/emit/`)**: #1275, #1276, #1280, #1281
   - **IR normalization (`src/ir/normalize.py`)**: #1279
   - **Stationarity / AD (`src/kkt/`, `src/ad/`)**: #1277, #1278
   - Note: #1277/#1278 may be subsumed by the Task 2 alias-AD carryforward fix

3. **Identify shared code paths:**
   - #1275 (absolute paths) and #1281 (duplicate Parameter) both touch the presolve-wrapper emission — same function?
   - #1276 (duplicate .fx) and #1281 (duplicate Parameter) both about emitter deduplication — share a symbol-tracking helper?
   - #1280 (UEL quoting) is structurally similar to other emitter-string-formatting work

4. **Propose a fix order:**
   - **Batch 1** (Day 1–2 alongside alias-AD start): `#1283` (unblocks other investigations) + `#1275` (quick emitter win)
   - **Batch 2** (Day 3–4): `#1280`, `#1276`, `#1281` — emitter dedup/quoting family
   - **Batch 3** (Day 5+): `#1279` (IR normalize) + verification of `#1277`/`#1278` post-alias-AD

5. **Estimate per-fix effort** so Task 11 can assign them to specific days.

### Changes

- Created `docs/planning/EPIC_4/SPRINT_25/CATALOG_EMITTER_BACKLOG.md` — 4-section catalog covering:
  - Per-issue classification table for all 7 issues (#1275–#1281) by code path, fix site, effort estimate, and subsume relationships.
  - Shared-code-path analysis with 2 subsume-opportunities identified (`_emit_nlp_presolve` cluster: #1275 + #1281; emitter-idempotency pattern: #1276 + #1281 via shared `_DeclaredSymbolTracker` helper).
  - Task 2 alias-AD cross-reference: #1277 partially subsumed by Pattern C; #1278 NOT subsumed (separate substitution bug).
  - Proposed 3-batch fix order (Batch 1: Day 1–2 / 3–5h; Batch 2: Day 3–4 / 6–9h; Batch 3: Day 5–7 post-Pattern-C / 4–6h).
  - Reproduction verification for all 7 issues; appendix on PR12 regression-fixture integration.
- Updated `docs/planning/EPIC_4/SPRINT_25/KNOWN_UNKNOWNS.md` — Verification Results for Unknowns 2.3, 2.4, 2.5 filled in with findings/evidence/decision.

### Result

- **Code-path classification:** 4 emitter (#1275, #1276, #1280, #1281), 1 IR normalize (#1279), 2 stationarity/AD (#1277, #1278).
- **Subsume opportunities identified:**
  1. #1275 and #1281 share `_emit_nlp_presolve` site in `src/emit/emit_gams.py:889` (NOT `src/emit/original_symbols.py` as Unknown 2.3 originally assumed — file-path corrected).
  2. #1276 and #1281 share the "emitter idempotency" pattern; propose landing a shared `_DeclaredSymbolTracker` helper once.
- **#1277 partially subsumed by Task 2 Pattern C fix** — likely needs one small extension to `_apply_alias_offset_to_deriv` to cover VarRef operands alongside ParamRefs.
- **#1278 NOT subsumed by Task 2** — separate substitution-preservation bug in instance enumeration.
- **Proposed batches:**
  - Batch 1 (Days 1–2, 3–5h): #1275 (presolve absolute paths) + #1280 (unquoted UELs) — quick emitter wins, zero coupling to alias-AD.
  - Batch 2 (Days 3–4, 6–9h): #1279 (robustlp defobj widening) + #1276 (fawley .fx dedup, introduces `_DeclaredSymbolTracker`) + #1281 (lmp2 duplicate Parameter, reuses helper).
  - Batch 3 (Days 5–7, 4–6h): #1277 post-Pattern-C validation + #1278 standalone substitution fix.
- **Total:** per-issue estimates sum to 13–20h. Baseline expected effort is **13–18h**, within the retrospective's 12–18h bound; the high end of 20h is a contingency buffer for Batch 3 if #1277's Pattern-C extension or #1278's substitution fix expand during implementation.

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_25/CATALOG_EMITTER_BACKLOG.md && echo "EXISTS" || echo "MISSING"
# Each of the 7 issues must be classified by code path
for n in 1275 1276 1277 1278 1279 1280 1281; do
    grep -q "#$n" docs/planning/EPIC_4/SPRINT_25/CATALOG_EMITTER_BACKLOG.md && echo "#$n ✓" || echo "#$n MISSING"
done
# ACTUAL: EXISTS + all 7 issue numbers present in catalog
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_25/CATALOG_EMITTER_BACKLOG.md`
- Per-issue classification by code path and fix complexity
- Shared-code-path map identifying subsume-opportunities
- Proposed batch ordering with per-fix effort estimate
- Cross-reference: which of #1277 / #1278 are subsumed by Task 2's alias-AD fix
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.3, 2.4, 2.5

### Acceptance Criteria

- [x] All 7 issues (#1275–#1281) classified by code path (4 emitter, 1 IR normalize, 2 stationarity/AD)
- [x] Shared-code-path analysis identifies ≥ 1 subsume opportunity (2 identified: `_emit_nlp_presolve` cluster and emitter-idempotency helper)
- [x] Fix order proposed as 3 batches with per-fix effort estimate (Batch 1: 3–5h, Batch 2: 6–9h, Batch 3: 4–6h)
- [x] Total estimate reconciled against retrospective's 12–18h bound (catalog baseline: 13–18h within bound; per-issue summation range 13–20h with a +2h Batch 3 contingency documented)
- [x] Unknowns 2.3, 2.4, 2.5 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 5: Analyze Recovered-Translate Models

**Status:** ✅ COMPLETE
**Priority:** High
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 25 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 4 (emitter catalog informs which fixes map to which models)
**Unknowns Verified:** 2.6

### Objective

Map each of the 5 "recovered-translate → path_syntax_error" models (`ganges`, `gangesx`, `ferts`, `clearlak`, `turkpow`) to the specific emitter bugs that broke their MCPs, so Task 11 can schedule fixes that actually unblock new solves. Without this mapping, Sprint 25's emitter work might fix 7 issues and still produce 0 new solves on these models.

### Why This Matters

The Sprint 24 Day 13 Addendum discovered that doubling translate timeouts recovered 5 models but produced **zero new solves** — every recovered translate went straight to `path_syntax_error` (PR10 budget exceeded to 100%). These 5 models are the most accessible leverage for Sprint 25's Solve target (99 → ≥ 105): if emitter fixes convert even 3 of them to `model_optimal`, the Solve target is likely met. But we need to know which emitter fixes matter for each.

### Background

- Day 13 Addendum finding (from SPRINT_LOG.md): 5 models recovered → all hit path_syntax_error
- Models: `ganges`, `gangesx`, `ferts`, `clearlak`, `turkpow`
- Their current `gamslib_status.json` state: `translate=success, mcp_solve.outcome_category=path_syntax_error`
- Sprint 24 retrospective §What Could Be Improved #2: "Translate-Recovery Influx Was 100%"
- Sprint 25 retrospective Priority 2 rationale: "the leverage point for the 5 recovered translates that don't solve"
- Task 4 catalog provides the emitter-bug code-path map

### What Needs to Be Done

1. **For each of the 5 models:**
   - Compile the current `<model>_mcp.gms` with GAMS (just compile, not solve)
   - Record the specific compile error(s): error code, line, offending token
   - Map each error to one of the 7 emitter bugs (#1275–#1281) OR identify it as a new bug

2. **Build a leverage matrix:**

   | Model | Blocked by #1275 | Blocked by #1276 | ... | Other bug |
   |---|---|---|---|---|
   | ganges | | | | |
   | gangesx | | | | |
   | ferts | | | | |
   | clearlak | | | | |
   | turkpow | | | | |

   Fill in which emitter fix each model depends on.

3. **Identify new emitter bugs:** any compile error not explained by #1275–#1281 needs a new Sprint 25 tracking issue filed (add to Priority 2 backlog).

4. **Rank fix priority by model-unblocking leverage:**
   - Which single fix unblocks the most models?
   - Which pairs of fixes unblock all 5?
   - Which fixes unblock 0 of these 5 (deprioritize as "correctness-only, no solve leverage")?

### Changes

- Created `docs/planning/EPIC_4/SPRINT_25/ANALYSIS_RECOVERED_TRANSLATES.md` — 4-section analysis covering:
  - Per-model compile-error captures via `gams <model>_mcp.gms action=c lo=2` for all 5 models
  - 12-column leverage matrix (5 models × 8 existing tracked bugs + 4 new issues)
  - Priority 2 scope reconciliation showing the 4 new issues add ~10–15h beyond Task 4's baseline
  - Cross-references to Tasks 2, 3, 4 (alias-AD, parser non-determinism, emitter backlog)
- Filed 4 new GitHub issues with `sprint-25` label: #1289 (ganges/gangesx), #1290 (ferts), #1291 (clearlak), #1292 (turkpow)
- Created in-tree issue docs at `docs/issues/ISSUE_{1289,1290,1291,1292}_*.md`
- Updated `docs/planning/EPIC_4/SPRINT_25/KNOWN_UNKNOWNS.md` — Unknown 2.6 marked **❌ WRONG** with revised assumption documented (assumption was inverted: 0 of 5 unblocked by existing bugs, not 3+).

### Result

- **All 5 recovered-translate models hit distinct, previously-untracked compile errors.** None of #1275–#1281 or #1283 unblocks any of them.
- **Compile errors per model:**
  - `ganges` + `gangesx`: 16 × Error 66 (parameters declared but never assigned — calibration-from-`.l`-values block stripped by emitter)
  - `ferts`: many × Error 109/108 (multiplier identifiers up to 67 chars > GAMS's 63-char limit)
  - `clearlak`: Error 352/149/141 (statement-ordering bug hoists `sum(leaf, ...)` before `leaf(n) = yes$(...)` — verified deterministic across 3 hash seeds, NOT #1283)
  - `turkpow`: Error 98 (line 200 of MCP = 144,454 chars; `stat_zt` emitted as one line with hundreds of `sameas()` cross-product clauses)
- **Highest-leverage single fix:** [#1289](https://github.com/jeffreyhorn/nlp2mcp/issues/1289) (ganges calibration stripping) unblocks 2 of 5.
- **Priority 2 scope expansion:** original Task 4 baseline 13–18h → revised **23–33h** (with 4 new issues #1289–#1292). Sprint 25 planning decision required — absorb the +10–15h or defer a subset to Sprint 26.
- **Realistic Solve-target contribution:** if all 4 new issues land cleanly, expected gain is +2–3 of 5 (some unblocked MCPs will hit secondary failure modes). Combined with Priority 1's expected +1, this brings net Solve gain to +3–4 — just short of the +6 target unless contingencies break favorably.

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_25/ANALYSIS_RECOVERED_TRANSLATES.md && echo "EXISTS" || echo "MISSING"
# Each of the 5 models must appear in the analysis
for m in ganges gangesx ferts clearlak turkpow; do
    grep -q "\`$m\`" docs/planning/EPIC_4/SPRINT_25/ANALYSIS_RECOVERED_TRANSLATES.md && echo "$m ✓" || echo "$m MISSING"
done
# ACTUAL: EXISTS + all 5 models present
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_25/ANALYSIS_RECOVERED_TRANSLATES.md`
- Per-model compile-error list (for the 5 recovered-translate models: `ganges`, `gangesx`, `ferts`, `clearlak`, `turkpow`)
- Leverage matrix (model × emitter-bug)
- Any new emitter bugs filed as Sprint 25 tracking issues
- Ranked fix priority by solve-unblocking leverage
- Updated KNOWN_UNKNOWNS.md with verification results for Unknown 2.6

### Acceptance Criteria

- [x] All 5 models have their current MCP compile errors recorded (saved at `/tmp/task5-compile/<model>_mcp.lst`; summarized in §Section 1)
- [x] Every compile error mapped to a known bug or a new tracking issue (4 new issues filed: #1289–#1292)
- [x] Leverage matrix identifies the highest-leverage single fix (#1289 — unblocks 2 of 5 models)
- [x] Cross-reference with Task 4 catalog updated if new subsume opportunities appear (§Section 4 cross-references; #1291 noted as adjacent to #1279 in `src/ir/normalize.py`)
- [x] Unknown 2.6 verified (❌ WRONG — assumption inverted; revised in KNOWN_UNKNOWNS.md)

---

## Task 6: Design Alias-AD Rollout Plan

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 25 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 2 (carryforward state informs rollout)
**Unknowns Verified:** 1.5, 1.8 (integrates Task 2's findings on 1.1–1.4, 1.6, 1.7)

### Objective

Produce a day-by-day rollout design for the alias-AD carryforward work (Sprint 25 Priority 1), with explicit regression-guard strategy, per-pattern validation gates, and a defined "stop the sprint" trigger if regression risk exceeds the canary-test budget. This design is the contract that PR11 (defend the reserved Day 1–12 block) operates against.

### Why This Matters

Sprint 24's outcome was "Day 1 started but Days 4–7 lost to urgent fixes" because there was no explicit contract about what counted as "urgent enough" to interrupt alias-AD. A formal rollout plan with phase gates makes the trade-off explicit: "if regression-X happens, we stop and investigate; otherwise we continue." The alternative — leaving Day-to-Day scope to planning as work progresses — has now failed twice.

### Background

- Sprint 24 retrospective §What We'd Do Differently #1: "Start Alias Differentiation on Day 1 and Defend the Time"
- Sprint 23 DESIGN_ALIAS_DIFFERENTIATION: `docs/planning/EPIC_4/SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md`
- Sprint 24 DESIGN_ALIAS_DIFFERENTIATION_V2: `docs/planning/EPIC_4/SPRINT_24/DESIGN_ALIAS_DIFFERENTIATION_V2.md`
- Task 2 audit output: Pattern classification + landed-vs-stubbed inventory
- Sprint 24 Day 5 Checkpoint 1 procedure (from PLAN.md) — use as template
- Known regression risks: KU-03 (49 matching models, now 54), KU-17 (infeasibility influx)

### What Needs to Be Done

_(Task 6 is now COMPLETE. The bullets below were the initial sketch from pre-Task-2 planning; the finalized 4-phase plan is in §Result and `DESIGN_ALIAS_AD_ROLLOUT.md`. Some initial-sketch items changed based on Task 2's Pattern reclassification — notably Patterns B/D are empty, so the original Phase 3 was re-scoped to Pattern C; #1150 consolidates into Pattern A instead of a dedicated Phase 4; Checkpoint 1 shifts from Day 5 to Day 6.)_

**Finalized plan** (see §Result and `DESIGN_ALIAS_AD_ROLLOUT.md`):

1. **Phases** based on Task 2's Pattern classification:
   - **Phase 1 (Days 1–3):** Pattern A single-index validation (qabel, abel, launch) + multi-index `_partial_collapse_sum` recovery prototype
   - **Phase 2 (Days 4–6):** Pattern A across the 6-issue audit set (#1138, #1139, #1140, #1142, #1145, #1150); Checkpoint 1 at Day 6
   - **Phase 3 (Days 7–9):** Pattern C `IndexOffset.base` extraction (polygon, himmel16, twocge `stat_tz` #1277); Pattern B/D reclassified empty per Task 2
   - **Phase 4 (Days 10–12):** Final regression sweep + Pattern E routing (#1141, #1144, #1147 routed out of scope); Checkpoint 2 at Day 10

2. **Per-phase gates** (pass → continue; fail → stop + investigate):
   - Dispatch canary passes (non-negotiable)
   - Golden-file regression on 54 matching models passes
   - Target models for the phase show measurable improvement (mismatch → match or infeasible → optimal)
   - No new path_syntax_error or model_infeasible appears
   - Full quantitative thresholds in `DESIGN_ALIAS_AD_ROLLOUT.md` §Gate 1–4

3. **Regression-guard infrastructure:**
   - Golden-file set for the 54 matching models (generate if not already present)
   - 6-tier canary ladder beyond `dispatch` (from Task 2 audit §Section 5)
   - Per-model verification script that reports pass/near-pass/fail
   - `PYTHONHASHSEED=0` pinning until Task 3's #1283 fix lands

4. **"Stop the sprint" triggers** (5 documented in design doc §Section 4):
   - ≥ 2 golden-file regressions that can't be root-caused within 1 day
   - dispatch canary fails
   - Checkpoint 1 (Day 6) evaluation returns NO-GO
   - New path_syntax_error or model_infeasible on any currently-matching model
   - `make test` regression

5. **Parallel-work allocation:** Priority 2 (emitter) Batches 1–3 and Task 5's new issues #1289–#1292 mapped to specific days in `DESIGN_ALIAS_AD_ROLLOUT.md` §Section 5; Day 8 identified as highest-leverage.

### Changes

- Created `docs/planning/EPIC_4/SPRINT_25/DESIGN_ALIAS_AD_ROLLOUT.md` — 8-section rollout design covering:
  - 4 phases (Phase 1 Days 1–3, Phase 2 Days 4–6, Phase 3 Days 7–9, Phase 4 Days 10–12) with day-by-day execution detail and target-model lists
  - 4 quantitative gates (Phase 1, Checkpoint 1 / Phase 2, Phase 3, Checkpoint 2 / Phase 4) using Sprint 24's GO / CONDITIONAL GO / NO-GO template
  - Regression-guard infrastructure: 6-tier canary ladder (Tier 0 dispatch → Tier 5 informational, i.e., tiers 0–5), 54-model golden-file generation script, per-model verification harness, `PYTHONHASHSEED=0` pinning until #1283 lands
  - 5 stop-the-sprint triggers (golden-file regression budget, dispatch canary fail, Checkpoint 1 NO-GO, new path_syntax_error / model_infeasible, `make test` regression)
  - Parallel-work allocation table mapping Priority 2 (emitter) Batches 1–3 + Task 5's new issues #1289–#1292 to specific days; Day 8 identified as highest-leverage (Phase 3 Pattern C + Batch 3 + #1289)
  - 20-test `sameas()` guard regression matrix (5 element types × 4 scenarios) addressing Unknown 1.5
  - All-or-nothing per-PR rollout decision + per-checkpoint git-revert rollback procedure addressing Unknown 1.8
  - Pre-Sprint checklist (Appendix B) for Sprint 25 Day 0 readiness
- Updated `docs/planning/EPIC_4/SPRINT_25/KNOWN_UNKNOWNS.md`:
  - Unknown 1.5: marked ✅ VERIFIED with the 20-test matrix design
  - Unknown 1.8: rollback procedure now codified (status updated to reflect Task 6 completion of Task 2's deferred work)

### Result

- **Phase 1 (Days 1–3):** Pattern A single-index validation (qabel, abel, launch) + multi-index `_partial_collapse_sum` recovery prototype. Gate at Day 3.
- **Phase 2 (Days 4–6):** Pattern A across the 6-issue Task 2 audit set — **#1138** (CGE: irscge, lrgcge, moncge, stdcge), **#1139** (meanvar), **#1140** (PS-family), **#1142** (launch), **#1145** (cclinpts), **#1150** (qabel, abel). Match delta target ≥ +3. Checkpoint 1 at Day 6.
- **Phase 3 (Days 7–9):** Pattern C — extend `_alias_match()` with `IndexOffset.base`; validate polygon, himmel16, twocge `stat_tz` (#1277). Gate at Day 9.
- **Phase 4 (Days 10–12):** Final regression sweep + Pattern E routing (#1141, #1144, #1147 routed out of scope). Checkpoint 2 at Day 10.
- **Stop triggers (5):** (1) ≥ 2 golden-file regressions un-root-caused in 1 day; (2) dispatch canary fails; (3) Checkpoint 1 NO-GO; (4) new path_syntax_error / model_infeasible on a matching model; (5) `make test` regression.
- **Rollout strategy:** all-or-nothing per PR (no feature flag — would double the test matrix for zero operational benefit); rollback via per-PR git revert.
- **`sameas()` guard regression matrix:** 5 element types × 4 test scenarios = 20 unit tests under `tests/unit/ad/test_sameas_guards.py`, lands alongside Phase 1 Day 2 PR.
- **Cumulative Match-target ladder:** Phase 1 (Day 3) baseline → Phase 2 ≥ +3 → Phase 3 ≥ +5 → Phase 4 ≥ +6; stretch ≥ +8 (full PROJECT_PLAN target).

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_25/DESIGN_ALIAS_AD_ROLLOUT.md && echo "EXISTS" || echo "MISSING"
# The design must have explicit phase gates
grep -E -c "^### Phase [1-4]:|^### Gate|^### Stop Trigger" \
    docs/planning/EPIC_4/SPRINT_25/DESIGN_ALIAS_AD_ROLLOUT.md
# Expect ≥ 8
# Example current output: 13 (4 Phase + 4 Gate + 5 Stop Trigger headings) — may drift if headings evolve
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_25/DESIGN_ALIAS_AD_ROLLOUT.md`
- 4 phases with explicit day ranges and target-model lists
- Per-phase gate definitions (pass → continue; fail → stop)
- "Stop the sprint" trigger list
- Parallel-work allocation for Priority 2 during alias-AD wait states
- Regression-guard infrastructure design (golden files + canary list)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.5, 1.8

### Acceptance Criteria

- [x] 4 phases mapped to 12 days (Days 1–12) — Phase 1 (1–3), Phase 2 (4–6), Phase 3 (7–9), Phase 4 (10–12)
- [x] Each phase has at least one gate with a quantitative pass/fail criterion (4 gates: Phase 1 Day 3, Checkpoint 1 Day 6, Phase 3 Day 9, Checkpoint 2 Day 10)
- [x] ≥ 3 "stop the sprint" triggers defined (5 triggers documented in §Section 4)
- [x] Regression-guard infrastructure specified (6-tier canary ladder, Tier 0–Tier 5, 54-model golden-file generation script, per-model verification harness, PYTHONHASHSEED pinning)
- [x] Cross-reference with Task 2 Pattern classification (§Section 8 cross-reference table)
- [x] Cross-reference with Sprint 24 KU-03 and KU-17 (regression risks) (§Section 8 cross-reference table)
- [x] Unknowns 1.5, 1.8 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 7: Scope Multi-Solve Gate + Dispatcher Refactor

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 25 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 1
**Unknowns Verified:** 3.1, 3.2, 3.3, 4.1, 4.2, 4.3

### Objective

Produce lightweight design notes for the two smaller Sprint 25 priorities (#1270 multi-solve gate extension, #1271 dispatcher refactor) so they can be dispatched as 1-day work items without needing further design during the sprint.

### Why This Matters

Sprint 24 demonstrated that "small" tasks can bleed scope when they're picked up mid-sprint without a design. The dispatcher refactor (#1271) is a mechanical cleanup but needs a regression strategy that covers every currently-translating model. The multi-solve gate extension (#1270) needs a false-positive-avoidance approach that doesn't break post-solve reporting patterns. Both benefit from 1–2 hours of thought before Sprint 25, not during.

### Background

- Issue: [#1270](https://github.com/jeffreyhorn/nlp2mcp/issues/1270) — Multi-solve gate extension for saras-style patterns
- Issue: [#1271](https://github.com/jeffreyhorn/nlp2mcp/issues/1271) — Dispatcher refactor
- In-tree docs: `docs/issues/ISSUE_1270_*.md`, `docs/issues/ISSUE_1271_*.md`
- Sprint 24 KU-29 (saras-style marginal reads): 3 candidate approaches (cross-reference / sequence awareness / allowlist)
- Sprint 24 KU-30 (dispatcher duplication): root cause of recurring "handler added in one but not the other" bugs (hit in PR #1264 partssupply, PR #1268 decomp)

### What Needs to Be Done

1. **#1270 Multi-Solve Gate Extension:**
   - Commit to Approach A (cross-reference: flag `eq.m` reads whose receiving parameter later appears in another model's constraint body)
   - Enumerate the corpus for saras-style patterns (manual survey: which NLPs have top-level `eq.m` reads between solves?)
   - Define the test fixture matrix: saras fixture (must flag), post-solve reporting fixture (must NOT flag), multi-stage display fixture (must NOT flag)
   - Identify the single `src/validation/driver.py` function that needs extension

2. **#1271 Dispatcher Refactor:**
   - Define the unified dispatcher signature: `_loop_tree_to_gams(tree, token_subst=None)`
   - List callers of the current two dispatchers and confirm the renaming plan
   - Define the byte-diff regression strategy: translate every currently-solving model (99 models) before and after, diff the outputs, expect zero diffs
   - Document the backward-compatibility window (if any)

3. **Combined effort estimate and day allocation** for the sprint schedule.

### Changes

_To be completed._

### Result

_To be completed._

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_25/DESIGN_SMALL_PRIORITIES.md && echo "EXISTS" || echo "MISSING"
grep -E -c "^### #1270|^### #1271" docs/planning/EPIC_4/SPRINT_25/DESIGN_SMALL_PRIORITIES.md
# Expect ≥ 2
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_25/DESIGN_SMALL_PRIORITIES.md`
- #1270 design: Approach A commit, corpus survey for saras-style patterns, test-fixture matrix
- #1271 design: unified signature, caller inventory, byte-diff regression strategy
- Day allocation for both items within the Sprint 25 schedule
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.2, 3.3, 4.1, 4.2, 4.3

### Acceptance Criteria

- [ ] #1270 design commits to a single approach with rationale
- [ ] #1270 corpus survey identifies which models (beyond `saras`) the extended gate will flag
- [ ] #1271 byte-diff regression strategy specifies pre/post comparison across all 99 currently-translating models
- [ ] Combined effort estimate ≤ 7h (aligns with retrospective bound)
- [ ] Unknowns 3.1, 3.2, 3.3, 4.1, 4.2, 4.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 8: Profile Hard Translation Timeouts (5 models)

**Status:** 🔵 NOT STARTED
**Priority:** Low
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 25 Day 1
**Owner:** Sprint planning
**Dependencies:** None
**Unknowns Verified:** 5.1, 5.2, 5.3, 5.4

### Objective

Profile the 5 remaining hard translation timeouts (`iswnm`, `mexls`, `nebrazil`, `sarf`, `srpchase`) under the 600s budget to identify whether the bottleneck is parsing, AD, KKT assembly, or emission. This directly determines whether Sprint 25's Priority 5 work is tractable (targeted optimization) or fundamentally intractable (requires algorithmic redesign out of Sprint 25 scope).

### Why This Matters

Per the Sprint 24 retrospective §PR13 recommendation, translation-timeout work has lower near-term Match leverage than originally scoped. Profiling before the sprint answers: is any of these 5 a 20% optimization away from success, or are they all genuinely intractable? That determines whether to budget Priority 5 at 4–6h (one shot at the most-tractable model) or 0h (defer wholesale to Sprint 26).

### Background

- Sprint 24 Day 13 Addendum: 5 models still time out at 600s
- Related issues: #1169 (lop — though lop was recovered), #1185 (mexls), #1192 (gtm)
- Sprint 24 KU-19 (timeout models fundamentally intractable): partially wrong — `srpchase` is 107 lines / 3 eqs (tiny), suggesting the bottleneck is pattern-specific not size-driven
- Sprint 24 KU-20 (sparse Jacobian feasibility): INCOMPLETE — needs profiling first
- Python profiling tools: `cProfile`, `py-spy`, custom stage-timing

### What Needs to Be Done

1. **For each of the 5 models, instrument stage timing:**
   - Parse time (Lark)
   - IR build time (`_ModelBuilder.build`)
   - Normalize time (`normalize_model`)
   - AD time (`build_stationarity_equations`)
   - KKT emit time (`emit_gams_mcp`)

2. **Under a 600s budget, run each model 1× and record where the time goes:**
   - Which stage dominates?
   - Is any stage growing super-linearly in model size?
   - Where exactly does the 600s cap interrupt?

3. **Classify each model:**
   - **Likely tractable** (< 30% over budget, clear single-stage bottleneck)
   - **Likely intractable at current architecture** (> 2× over budget, multiple stages)
   - **Unclear** (profiling inconclusive)

4. **For "likely tractable" models, propose a specific optimization:**
   - Caching opportunity?
   - Redundant computation?
   - Algorithm swap (e.g., forward-mode → reverse-mode)?

### Changes

_To be completed._

### Result

_To be completed._

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_25/PROFILE_HARD_TIMEOUTS.md && echo "EXISTS" || echo "MISSING"
for m in iswnm mexls nebrazil sarf srpchase; do
    grep -q "\`$m\`" docs/planning/EPIC_4/SPRINT_25/PROFILE_HARD_TIMEOUTS.md && echo "$m ✓" || echo "$m MISSING"
done
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_25/PROFILE_HARD_TIMEOUTS.md`
- Per-model stage-timing breakdown (parse / IR / normalize / AD / emit)
- Per-model tractability classification
- For tractable models: specific optimization proposal
- Sprint 25 Priority 5 scope recommendation (fix N models or defer)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.1, 5.2, 5.3, 5.4

### Acceptance Criteria

- [ ] All 5 models profiled with stage-timing data
- [ ] Each model classified as tractable / intractable / unclear
- [ ] At least 1 model has a specific optimization proposal OR all 5 recommended for Sprint 26+ deferral
- [ ] Cross-reference with KU-19, KU-20 from SPRINT_24/KNOWN_UNKNOWNS.md
- [ ] Unknowns 5.1, 5.2, 5.3, 5.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 9: Run Full Pipeline Baseline + Freeze Scope (PR6 / PR15)

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 1–2 hours
**Deadline:** Before Sprint 25 Day 0
**Owner:** Sprint planning
**Dependencies:** None
**Unknowns Verified:** 6.1

### Objective

Record Sprint 25's Day 0 baseline via a full pipeline run (per PR6) and freeze the pipeline scope (v2.2.x exclusions) before Sprint 25 starts (per PR15, new for Sprint 25 from Sprint 24 retrospective). Any mid-sprint scope change invalidates the acceptance-criteria evaluation.

### Why This Matters

Sprint 24's Day-0 metrics came from the end of Sprint 23 (147-scope) but the pipeline scope shifted to 143 mid-sprint via the multi-solve driver exclusion. This created target-vs-actual ambiguity that showed up in the Sprint 24 retrospective and its PR reviews (baseline column needed reconciliation between pipeline and triage scopes). PR15 is the direct response: freeze scope before Day 0 so acceptance criteria evaluation is unambiguous.

### Background

- Sprint 24 retrospective §What Could Be Improved #4: "Scope Shift Mid-Sprint Created Accounting Complexity"
- Sprint 24 retrospective §New Recommendations PR15: "Freeze pipeline scope before Day 0"
- Sprint 24 Day 13 Addendum final state: 143 models in-scope (v2.2.1 exclusions: 14 MINLP, 7 legacy, 2 multi-solve driver)
- Full pipeline runner: `scripts/gamslib/run_full_test.py --quiet`
- Typical run time: ~2h under doubled timeouts

### What Needs to Be Done

1. **Snapshot current `data/gamslib/gamslib_status.json`** pre-retest for diffing.

2. **Run the full pipeline:**
   ```bash
   .venv/bin/python scripts/gamslib/run_full_test.py --quiet
   ```

3. **Verify the run produced stable results** (per Task 10's determinism work — run 2× and confirm byte-identical `.gms` output for known-deterministic models; expect #1283 corruption on chenery until fixed, but note the rate).

4. **Record the baseline numbers** in `SPRINT_25/BASELINE_METRICS.md`:
   - Parse / Translate / Solve / Match
   - path_syntax_error / path_solve_terminated / model_infeasible / path_solve_license
   - Scope breakdown (143 in-scope, exclusions by reason)

5. **Freeze scope (PR15):**
   - Document the current v2.2.1 exclusion set
   - Commit to no exclusion changes during Sprint 25 unless a new `multi_solve_driver_out_of_scope` or similar keyword emerges and the gate adds it automatically
   - Document the freeze decision in SPRINT_25/BASELINE_METRICS.md

### Changes

_To be completed._

### Result

_To be completed._

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md && echo "EXISTS" || echo "MISSING"
grep -E "Parse|Translate|Solve|Match|path_syntax|path_solve|model_infeasible" \
    docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md | head -15
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md` — complete baseline snapshot
- Frozen pipeline-scope declaration (v2.2.1 exclusions: 14 MINLP, 7 legacy, 2 multi-solve)
- Confirmation that acceptance criteria denominator is 143 (locked)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknown 6.1

### Acceptance Criteria

- [ ] Full pipeline run completed within 2h
- [ ] All 8 acceptance-criteria metrics recorded
- [ ] Scope-freeze decision documented with reasoning
- [ ] Cross-reference with Sprint 24 PR15 recommendation
- [ ] Unknown 6.1 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 10: Design Byte-Stability Test Infrastructure (PR12)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 1–2 hours
**Deadline:** Before Sprint 25 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 3 (non-determinism investigation informs what to test)
**Unknowns Verified:** 6.2

### Objective

Design the byte-stability regression test infrastructure (PR12 from Sprint 24 retrospective) — a test harness that runs the pipeline under multiple `PYTHONHASHSEED` values and asserts byte-identical `.gms` output across runs. This catches `#1283`-class bugs in CI instead of via manual reviewer inspection.

### Why This Matters

Sprint 24 only discovered `#1283` because a reviewer happened to spot the corrupt values during Day 13 review. Without a determinism test, other `#1283`-class bugs could be lurking in the corpus output, silently affecting metrics. PR12 makes determinism a CI-enforced invariant.

### Background

- Sprint 24 retrospective §New Recommendations PR12
- Issue: [#1283](https://github.com/jeffreyhorn/nlp2mcp/issues/1283) — the reference bug
- Python's `PYTHONHASHSEED` environment variable controls dict / set iteration randomization
- CI workflow: `.github/workflows/ci.yml` (fast test suite runs under `pytest -n auto`)
- Typical pipeline wall-clock: ~2h for all 143 models; too slow for a per-commit CI gate

### What Needs to Be Done

1. **Decide the test scope:**
   - **Option A (cheap):** Single-model determinism test — pick 5 representative models (including chenery), run each 10× under different hash seeds, assert byte-identical output. Fast (~30s), runs per-commit.
   - **Option B (comprehensive):** Full-pipeline determinism test — run the whole pipeline 2× under different seeds, diff all `.gms` outputs. Slow (~4h); runs on a nightly or weekly cadence.
   - **Option C (both):** Option A per-commit + Option B nightly.

2. **Define the test fixture set for Option A:**
   - `chenery` (known reproducer for #1283)
   - A model with multi-row-label tables but NOT known-broken (regression guard)
   - A simple model (to confirm the test framework works when there's no bug)
   - 2 more from different families (CGE, alias-heavy)

3. **Decide the seed set:**
   - Fixed seeds: 0, 1, 42, 12345 (reproducible)
   - Or: random sample of 5 seeds per run with seed values logged

4. **Design the assertion:**
   - Byte-identical MCP output across all seed runs
   - On failure: log the first-differing seed and a diff of the output

5. **Decide the CI integration:**
   - New test file: `tests/integration/test_pipeline_determinism.py`?
   - New pytest marker: `@pytest.mark.determinism`?
   - CI workflow wiring (fast suite, nightly, or both)

### Changes

_To be completed._

### Result

_To be completed._

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_25/DESIGN_DETERMINISM_TESTS.md && echo "EXISTS" || echo "MISSING"
grep -E -c "^## Scope|^## Fixture Set|^## Seed Set|^## CI Integration" \
    docs/planning/EPIC_4/SPRINT_25/DESIGN_DETERMINISM_TESTS.md
# Expect ≥ 4
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_25/DESIGN_DETERMINISM_TESTS.md`
- Test scope decision (Option A / B / C) with rationale
- Fixture model list (5 models)
- Seed set (fixed or random) with rationale
- CI integration plan (file path, marker, workflow)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknown 6.2

### Acceptance Criteria

- [ ] Scope decision made with rationale
- [ ] ≥ 5 fixture models selected
- [ ] Seed set defined
- [ ] CI integration plan ready for Sprint 25 Day 2 implementation
- [ ] Unknown 6.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 11: Plan Sprint 25 Detailed Schedule

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 25 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1–10 (all prep outputs inform the schedule)
**Unknowns Verified:** 6.3 (integrates all verified unknowns from Tasks 2–10)

### Objective

Integrate the outputs of Tasks 1–10 into a day-by-day Sprint 25 schedule with 2 checkpoints and day-by-day execution prompts, mirroring the Sprint 23/24 planning infrastructure. The schedule is the contract that the sprint runs against.

### Why This Matters

The 15-day schedule with 2 checkpoints has been the single most effective planning tool across Sprints 20–24. Sprint 25 needs the same infrastructure but tailored to its priorities: the 8–12-day alias-AD block (defended per PR11), the emitter backlog (parallelizable), and the smaller Priority 3/4 items. Without this schedule the sprint drifts into ad-hoc scoping — which is exactly how Sprint 24's alias-AD time got absorbed.

### Background

- Sprint 24 plan: `docs/planning/EPIC_4/SPRINT_24/PLAN.md` — use as template
- Sprint 24 day-by-day prompts: `docs/planning/EPIC_4/SPRINT_24/prompts/PLAN_PROMPTS.md`
- Sprint 25 retrospective recommendations (§Sprint 25 Recommendations Priority 1–5)
- PROJECT_PLAN.md Sprint 25 section (components, deliverables, acceptance criteria)
- All prep outputs from Tasks 1–10

### What Needs to Be Done

1. **Draft Sprint 25 schedule** at `docs/planning/EPIC_4/SPRINT_25/PLAN.md`:
   - Day 0: prep-task review, sprint kickoff, baseline snapshot
   - Days 1–12: Priority 1 alias-AD (per Task 6 rollout design) + parallel Priority 2 emitter work (per Task 4 catalog)
   - Day 5: Checkpoint 1 (alias-AD Phase 1–2 complete, ≥ 3 models improved, 0 regressions)
   - Day 10: Checkpoint 2 (alias-AD Phase 3 complete, emitter backlog complete, ≥ 6 new matches)
   - Day 13: Final pipeline retest
   - Day 14: Sprint close + retrospective

2. **Write day-by-day execution prompts** at `docs/planning/EPIC_4/SPRINT_25/prompts/PLAN_PROMPTS.md` (mirror Sprint 24's PLAN_PROMPTS.md format).

3. **Define checkpoint evaluation criteria:**
   - Checkpoint 1 (Day 5) GO / CONDITIONAL / NO-GO criteria
   - Checkpoint 2 (Day 10) GO / CONDITIONAL / NO-GO criteria

4. **Allocate parallel work:** map Priority 2 emitter batches (from Task 4) to specific days where alias-AD is in Phase-transition wait.

5. **Update SPRINT_25/PREP_PLAN.md summary** with final prep-task status (all tasks marked complete).

### Changes

_To be completed._

### Result

_To be completed._

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_25/PLAN.md && echo "EXISTS" || echo "MISSING"
test -f docs/planning/EPIC_4/SPRINT_25/prompts/PLAN_PROMPTS.md && echo "EXISTS" || echo "MISSING"
# Schedule must cover all 15 days
grep -c "^### Day " docs/planning/EPIC_4/SPRINT_25/PLAN.md
# Expect ≥ 15 (Days 0–14)
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_25/PLAN.md` — 15-day detailed schedule
- `docs/planning/EPIC_4/SPRINT_25/prompts/PLAN_PROMPTS.md` — day-by-day execution prompts
- 2 checkpoint evaluation criteria (Day 5 and Day 10)
- Parallel-work allocation for Priority 2 during alias-AD waits
- Updated `SPRINT_25/PREP_PLAN.md` with final prep-task status
- Updated KNOWN_UNKNOWNS.md with verification results for Unknown 6.3

### Acceptance Criteria

- [ ] Schedule covers all 15 days (Day 0 – Day 14)
- [ ] 2 checkpoints defined with quantitative GO / NO-GO criteria
- [ ] Day-by-day prompts match Sprint 24's format (1 prompt per day)
- [ ] Parallel-work allocation covers Priority 2 emitter batches from Task 4
- [ ] Cross-references with all 10 prior prep-task outputs
- [ ] Unknown 6.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Summary

Sprint 25 preparation comprises 11 tasks spanning ~23–34 hours (3–4.5 working days), covering:

- **Risk identification** (Task 1): Sprint 25 Known Unknowns with ≥ 20 entries
- **Alias-AD preparation** (Tasks 2, 6): Carryforward audit + rollout design
- **Non-determinism preparation** (Task 3): Root-cause investigation of #1283
- **Emitter-backlog preparation** (Tasks 4, 5): Catalog + recovered-translate leverage analysis
- **Small-priority design** (Task 7): #1270 multi-solve gate + #1271 dispatcher refactor
- **Hard-timeout preparation** (Task 8): Profile 5 remaining hard timeouts
- **Baseline + scope freeze** (Task 9): Full pipeline baseline per PR6; scope freeze per PR15
- **Determinism infrastructure** (Task 10): PR12 test design
- **Sprint planning** (Task 11): 15-day schedule + day-by-day prompts

### Success Criteria for Prep Phase

- [ ] All 11 prep tasks complete before Sprint 25 Day 1
- [ ] `SPRINT_25/KNOWN_UNKNOWNS.md` documents ≥ 20 unknowns across ≥ 5 categories
- [ ] `SPRINT_25/AUDIT_ALIAS_AD_CARRYFORWARD.md` classifies all 11 open alias issues by Pattern
- [ ] `SPRINT_25/INVESTIGATION_PARSER_NON_DETERMINISM.md` narrows #1283 to ≤ 2 code paths
- [ ] `SPRINT_25/CATALOG_EMITTER_BACKLOG.md` groups all 7 emitter issues by code path
- [ ] `SPRINT_25/ANALYSIS_RECOVERED_TRANSLATES.md` maps each of the 5 recovered-translate models to specific emitter bugs
- [ ] `SPRINT_25/DESIGN_ALIAS_AD_ROLLOUT.md` has 4 phases with gates and stop triggers
- [ ] `SPRINT_25/DESIGN_SMALL_PRIORITIES.md` commits to specific designs for #1270 and #1271
- [ ] `SPRINT_25/PROFILE_HARD_TIMEOUTS.md` classifies each of 5 timeout models
- [ ] `SPRINT_25/BASELINE_METRICS.md` records the frozen Day-0 baseline
- [ ] `SPRINT_25/DESIGN_DETERMINISM_TESTS.md` specifies PR12 infrastructure
- [ ] `SPRINT_25/PLAN.md` + `SPRINT_25/prompts/PLAN_PROMPTS.md` cover all 15 days

### Critical-Path Summary

**Alias-AD chain (mandatory before Day 1):**
Task 1 → Task 2 → Task 6 → Task 11

**Determinism chain (mandatory before Day 1):**
Task 1 → Task 3 → Task 10 → Task 11

**Emitter-backlog chain (mandatory before Day 1):**
Task 1 → Task 4 → Task 5 → Task 11

All three chains converge at Task 11 (final schedule). The longest single chain is 4 tasks; with parallel execution across the three chains, the entire prep phase should complete in ~2–3 working days of focused effort.

---

## Appendix A: Document Cross-References

### Sprint 25 Inputs (read for prep)

- `docs/planning/EPIC_4/PROJECT_PLAN.md` §Sprint 25 (components, deliverables, acceptance criteria)
- `docs/planning/EPIC_4/SPRINT_24/SPRINT_RETROSPECTIVE.md` §Sprint 25 Recommendations, §New Recommendations PR12–PR15
- `docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md` §End-of-Sprint Discoveries (KU-27 through KU-32)
- `docs/planning/EPIC_4/SPRINT_24/SPRINT_LOG.md` §Day 13 Addendum (recovered-translate finding)
- `docs/planning/EPIC_4/SPRINT_24/DESIGN_ALIAS_DIFFERENTIATION_V2.md` (Sprint 24 design carryforward)
- `docs/planning/EPIC_4/SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md` (original Sprint 23 design)

### Issue Tracking

- Alias-AD carryforward: #1138, #1139, #1140, #1141, #1142, #1143, #1144, #1145, #1146, #1147, #1150 (11 open, `sprint-25` label)
- Emitter/stationarity backlog: #1275, #1276, #1277, #1278, #1279, #1280, #1281, #1283 (8 open, `sprint-25` label)
- Multi-solve gate extension: #1270
- Dispatcher refactor: #1271
- Translation timeouts: #1169 (lop), #1185 (mexls), #1192 (gtm)
- Chenery model_infeasible: #1177
- In-tree issue docs: `docs/issues/ISSUE_127{0,1,5,6,7,8,9}_*.md`, `docs/issues/ISSUE_128{0,1,3}_*.md`

### Prior-Sprint Retrospectives (for process recommendations)

- Sprint 24: `docs/planning/EPIC_4/SPRINT_24/SPRINT_RETROSPECTIVE.md` (PR6–PR15 review)
- Sprint 23: `docs/planning/EPIC_4/SPRINT_23/SPRINT_RETROSPECTIVE.md` (PR9–PR11)
- Sprint 22: `docs/planning/EPIC_4/SPRINT_22/SPRINT_RETROSPECTIVE.md` (PR6–PR8)

### Related Research (reference only)

- `docs/research/multidimensional_indexing.md` — IndexOffset / alias theoretical background
- `docs/research/nested_subset_indexing_research.md` — subset/alias interaction
- `docs/research/minmax_objective_reformulation.md` — reformulation pattern (reference for future Epic 5 work)

### CHANGELOG Context

- `CHANGELOG.md` §[Unreleased] §Sprint 24 Summary — includes list of Sprint 25 carryforward issues

---

**Document Created:** 2026-04-19
**Total Prep Tasks:** 11
**Estimated Total Effort:** 23–34 hours
**Critical Path Length:** 4 tasks (Tasks 1, 2, 6, 11)

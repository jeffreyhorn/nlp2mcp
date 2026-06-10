# Sprint 28 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 28 begins
**Timeline:** Complete before Sprint 28 Day 1
**Goal:** Set up Sprint 28 for success — land the Sprint 27 Solve/Match carryforwards (#1224, #1388, #1393+#1335, #1387, #1390, camcge) and build the diagnostic + CI tooling the Sprint 27 retrospective recommended (golden-staleness CI check, KKT-residual harness, embedded-NLP-divergence detector, AD cross-term property tests). Targets: Solve 105 → ≥ 110; Match 62 → ≥ 65; path_syntax_error 8 → ≤ 6; model_infeasible 8 → ≤ 5; Tests 4,779 → ≥ 4,800.

**Key Insight from Sprint 27:** Across Days 0/6/11/12/13 the prep-doc `file:line` fix surfaces were **wrong more often than right** — the real surfaces were `src/kkt/stationarity.py`, `src/ir/ast.py`, and the emit restore pass, NOT the AD `_try_eval_offset` / `constraint_jacobian` sites the prep named (Sprint 27 retro §"What We'd Do Differently #1"). The Phase 0 acceptance gate (PR20) repeatedly caught these mis-scopes *before* wasted implementation, turning them into cheap REPLANs. Sprint 28 prep MUST therefore (a) codify the new **PR24 rule** — prep records the *symptom + reproducer* only; the fix surface is established by a Day-0 trace and never trusted from the prep doc — and (b) front-load the **KKT-residual verification harness** (Sprint 27's GDX warm-from-good-optimum experiment, now formalized) so the Case-(a/b/c) emit-bug-vs-non-convexity discriminator is mechanical for the diagnosis-heavy carryforwards (#1387, #1390, camcge). A second Sprint 27 lesson — the Day-0 "+6 firm Match" projection over-counted because it conflated `path_syntax_error → model_infeasible` **bucket-forward** moves with genuine Solve/Match gains — drives **PR25 projection discipline**: every Day-0 projection must label each delta as a genuine bucket-to-success transition vs a forward move within the failure set.

**Branching:** All prep task branches should be created from `main` and PRs should target `main`.

---

## Executive Summary

Sprint 28 inherits the Sprint 27 carryforward backlog of **10 issues** carried to Sprint 28: six Solve/Match carryforwards with a documented Phase-0 diagnosis already on file (#1224 mine parameter-valued-offset KKT cross-term inversion; #1388 camshape Case-(b) `stat_r` divergence; #1393 + #1335 otpop scalar-eq Sum-collapse + `card(t)-ord(t)` evaluator; #1387 cclinpts three coupled AD changes; #1390 kand re-diagnosis; camcge singular-Jacobian CGE degeneracy) plus three lower-priority cleanups (#1374 `.l` shape, #1400 `message`-field path leak, #1385 runtime-guard cross-terms) and the #1424 follow-through context. The single highest-leverage Solve workstream is **#1224 + #1388** — both are AD/KKT cross-term defects with a hand-derived target shape already recorded (+1 Solve each, firm).

Sprint 28 differs from prior sprints in one structural way: it is the first sprint to pair the carryforward fixes with a deliberate **diagnostic + CI tooling investment** (Priorities 8–10 in `PROJECT_PLAN.md`). The Sprint 27 retrospective identified that the same bug classes recurred across Sprints 24–27 and were re-diagnosed by hand each time; Sprint 28 mechanizes the three recurring diagnostic patterns — the KKT-residual Case-(a/b/c) discriminator, the golden-staleness check, and the embedded-NLP-divergence detector — so the carryforward diagnoses accelerate and future regressions are caught automatically.

This prep plan focuses on:

1. **Risk identification** — Sprint 28 Known Unknowns List covering the six carryforward fix-surfaces (with the PR24 caveat that the surfaces are hypotheses to be re-traced at Day 0), the three diagnosis-heavy REPLAN-prone tracks (#1387/#1390/camcge), the three infrastructure deliverables' scope, and process recommendations PR24/PR25.
2. **Day-0 baseline + projection discipline (PR15 + PR17 + PR25)** — Sprint 27 final → Sprint 28 Day 0 per-failing-model bucket provenance; every projected delta labeled bucket-forward vs genuine gain.
3. **Process recommendation codification (PR24 + PR25)** — the Day-0 traced-fix-surface rule and the projection-discipline rule codified in CONTRIBUTING.md and the Phase-0 template **before** any Day 0 work begins (this changes how the Phase 0 gates are authored).
4. **KKT-residual verification harness design (PR27 / Priority 9)** — front-loaded design spec so the harness is the first thing built in-sprint (Days 1–3) and the Phase-0 "Verification Methodology" sections can reference it.
5. **Phase 0 acceptance gates for the six carryforwards (PR20 + PR24)** — author/refresh the hand-derived KKT shape + traced fix-surface + harness-based verification method for #1224, #1388, #1393+#1335, #1387, #1390, camcge.
6. **Diagnosis-heavy track REPLAN assessment (PR16 application)** — apply hypothesis-validation to the three REPLAN-prone tracks (#1387 three-coupled-change, #1390 195-vs-2613 re-diagnosis, camcge singular-Jacobian) and pin explicit Sprint 29 REPLAN exits.
7. **Golden-staleness drift audit + CI-check design (PR26 / Priority 8)** — catalog the existing drift (cesam/fawley/korcge/dinam) and design the regenerate-diff-report check + CI integration.
8. **Divergence detector + AD cross-term property-test catalog (Priority 10)** — design the presolve-divergence detector interface and catalog the recurring cross-term shapes (#1224/#1388/#1390) for the property-test suite.
9. **Lower-priority cleanups fix-surface analysis (Priority 7)** — #1374, #1400, #1385 patch-site identification.
10. **Sprint planning** — detailed 14-day schedule (Day 0 setup + Days 1–13 execution) with day-by-day prompts; ≤ 12 hours/day per the PROJECT_PLAN.md Sprint 28 entry.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|----------------------|
| 1 | Create Sprint 28 Known Unknowns List | Critical | 3–4h | None | All priorities — risk identification |
| 2 | Sprint 27 → Sprint 28 Bucket-Provenance Baseline + Projection Discipline (PR15 + PR17 + PR25) | Critical | 4–5h | None | All priorities — baseline metrics |
| 3 | Codify Process Recommendations PR24 (Day-0 Traced Fix-Surface) + PR25 (Projection Discipline) | Critical | 2–3h | Task 1 | Process — primary mitigation against prep-doc mis-scope |
| 4 | Design the KKT-Residual Verification Harness (PR27 / Priority 9) | High | 3–4h | Task 1 | Priorities 1, 2, 5 — Case-(a/b/c) discriminator |
| 5 | Author / Refresh Phase 0 Acceptance Gates for the Six Carryforwards (PR20 + PR24) | Critical | 5–7h | Tasks 1, 3, 4 | Priorities 1–6 — primary scope-correctness gate |
| 6 | Diagnosis-Heavy Track REPLAN Risk Assessment (#1387, #1390, camcge; PR16) | High | 4–6h | Task 5 | Priorities 4, 5, 6 — REPLAN-prone tracks |
| 7 | Golden-Staleness Drift Audit + CI-Check Design (PR26 / Priority 8) | High | 3–4h | Task 2 | Priority 8 — infrastructure |
| 8 | Divergence Detector + AD Cross-Term Property-Test Catalog Design (Priority 10) | Medium | 3–4h | Task 1 | Priority 10 — infrastructure |
| 9 | Lower-Priority Cleanups Fix-Surface Analysis (#1374, #1400, #1385) | Medium | 2–3h | Task 1 | Priority 7 — cleanups |
| 10 | Plan Sprint 28 Detailed Schedule | Critical | 3–4h | Tasks 1–9 | All priorities — sprint planning |

**Total Estimated Time:** 32–44 hours (~4–5.5 working days)

**Critical Path:** Task 1 → Task 3 → Task 5 → Task 10 (the Phase-0 codification chain — PR24 changes how the carryforward Phase 0 gates are authored, so the process rule must land before the gates).
**Secondary Path:** Task 1 → Task 4 → Task 5 → Task 10 (the KKT-residual harness design feeds the Phase-0 "Verification Methodology" sections).
**Tertiary Path:** Task 2 → Task 7 → Task 10 (baseline → golden-staleness drift audit → schedule).
**Parallelizable:** Tasks 1 + 2 (independent); Tasks 7 + 8 + 9 (independent infrastructure/cleanup analyses after their respective deps); Task 6 follows Task 5.

---

## Task 1: Create Sprint 28 Known Unknowns List

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 3–4 hours (actual: ~3.5h)
**Completed:** 2026-06-09
**Deadline:** Before Sprint 28 Day 1
**Owner:** Sprint planning
**Dependencies:** None

### Objective

Create a proactive list of assumptions and unknowns for Sprint 28 to prevent late discoveries during implementation. This is the first task because it surfaces risks that inform every other prep task — particularly the PR24/PR25 codification (Task 3), the KKT-residual harness design (Task 4), the Phase 0 gates (Task 5), and the diagnosis-heavy REPLAN assessment (Task 6). This task also carries forward the end-of-sprint unknowns from Sprint 27 (the KU-coverage summary in `SPRINT_27/SPRINT_RETROSPECTIVE.md` §"KU Coverage Summary" plus any open items in `SPRINT_27/KNOWN_UNKNOWNS.md`).

### Why This Matters

Sprint 27's central lesson (retro §"What We'd Do Differently #1") is that the prep-doc fix surfaces were wrong 4× — so the Sprint 28 Known Unknowns List must explicitly treat every carryforward fix-surface as an *unverified hypothesis* with a Day-0 trace as its verification method, not as established fact. A Known Unknowns List authored under the old assumption ("the surface is known, just implement it") would re-introduce exactly the mis-scope that Phase 0 caught four times last sprint.

The three diagnosis-heavy tracks (#1387 cclinpts three-coupled-change, #1390 kand 195-vs-2613 re-diagnosis, camcge singular-Jacobian) each carry untested architectural hypotheses; per the Sprint 26/27 PR16 methodology these must be flagged as Critical unknowns with a single-model hypothesis-validation as their verification, so the REPLAN decision (Task 6) is made on evidence, not optimism. The infrastructure deliverables (P8–P10) also carry scope unknowns — e.g., the golden-staleness allowlist size, the KKT-residual harness's GDX-transfer mechanics for duals, and the presolve-divergence detector's false-positive surface — that must be surfaced now so they don't expand mid-sprint.

### Background

- Sprint 27 Retrospective: `docs/planning/EPIC_4/SPRINT_27/SPRINT_RETROSPECTIVE.md` (§"Sprint 28 Recommendations" Priorities 1–7; §"What We'd Do Differently" #1–#4; §"What Went Well" #1–#5; §"KU Coverage Summary")
- Sprint 27 Known Unknowns: `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` (Cat 1–9, all resolved Days 0–13 — review for any open/end-of-sprint items)
- Sprint 28 scope: `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 28 (Weeks 21–22)" (Priorities 1–10 + Process Recommendations PR24/PR25)
- Carryforward issues: `docs/issues/ISSUE_{1224,1388,1393,1335,1387,1390,1374,1385}_*.md` (each has a Phase-0 diagnosis or a re-scoped filing). Note: #1400 has **no** dedicated issue doc — it is a scripts-only pipeline fix tracked in `scripts/gamslib/run_full_test.py` (the Sprint 27 `mcp_file_used` relativization; the `message`-field second leak is the Sprint 28 carryforward).
- #1424 context (the subset-corruption co-bug that landed in Sprint 27 but unblocks #1388 warm-start): `docs/issues/ISSUE_1424_*.md`

### What Needs to Be Done

1. **Review Sprint 27 carryforward / end-of-sprint KUs.** Migrate any open items from `SPRINT_27/KNOWN_UNKNOWNS.md` and the retro KU-coverage summary into Sprint 28 numbering with full text and forward-links to the Sprint 28 categories they drive.

2. **For each Priority area, brainstorm unknowns** (assumption / how-to-verify / priority / risk-if-wrong), organized by category aligned to the PROJECT_PLAN priorities:

   **Category 1 (#1224 mine — parameter-valued-offset cross-term inversion):**
   - Is the AD/Jacobian inversion the correct fix surface, or — per PR24 — does a Day-0 trace localize it elsewhere (e.g., the same `src/ir/ast.py` emit-render layer the Sprint 27 translate fix touched)?
   - Does the inverse-offset stationarity term `sum(k, lam_pr(k, l, i-li(k), j-lj(k)))` need the `l-1` companion term emitted in the same pass, or are they separable?
   - Will the parameter-valued offset `i-li(k)` render correctly at all domain boundaries (does GAMS lead/lag clip or wrap)?

   **Category 2 (#1388 camshape — Case-(b) `stat_r` divergence):**
   - Is the missing/mis-signed term in the interior `stat_r(i)` or the edge `lam_convex_edge*` cross-terms? (Sprint 27 §4.6 pinned `stat_r(i1)` INFES ≈ 396 but not the specific term.)
   - Does the fix at `stationarity.py:1835` (`_build_indexed_stationarity_expr`) risk the same blast-radius as Sprint 27's cesam2 bug-class fixes (cesam/shale/ganges/gangesx)?

   **Category 3 (#1393 + #1335 otpop):**
   - Which `stationarity.py` symbolic-collapse code path does the `t→t__` aliasing actually flow through (#1393)? Day-0 trace required — Approach C was proven inert in Sprint 27.
   - Does the `_try_eval_offset` `card(t)-ord(t)` extension (#1335, Approach B) interact with the #1393 collapse, requiring sequenced implementation?

   **Category 4 (#1387 cclinpts — three coupled AD changes):**
   - Does the gradient→stationarity re-symbolization anchor fix (change 2) prove architectural (touching all re-symbolization callers), forcing the Sprint 29 REPLAN exit? **(Critical — PR16 hypothesis-validation target.)**
   - Is the non-convex warm-start (change 3) cclinpts-specific or does it generalize?
   - Confirm the "sign-flip" is a misdiagnosis (do NOT touch sign logic) — re-verify against the Day-6 binding diagnosis.

   **Category 5 (#1390 kand — re-diagnosis):**
   - Where is the 195.0-vs-2613.0 gap — `bal(j,t,n)`/`x` stationarity, the `t-1`↔`t+1` lag duality, or LP first-stage/recourse coupling? **(Critical — the phantom-term collapse is proven inert; a fresh Day-0 trace is the only verification.)**
   - Is the gap a deeper LP-recourse-coupling architectural issue (→ Sprint 29 re-scope) or a localizable stationarity/complementarity row?

   **Category 6 (camcge — singular-Jacobian CGE degeneracy):**
   - Is the singularity a redundant market-clearing / Walras-law row, a missing price-numéraire fix, or a PATH preprocessing/scaling option? **(Critical — may be inherent CGE degeneracy → Epic 5 observation task.)**

   **Category 7 (lower-priority cleanups #1374/#1400/#1385):**
   - #1374: is the robot second-shape dedup at emit time isolated, or does it share the `fx_to_l_override` path with the Sprint 27 #1374 dominant-shape fix?
   - #1385: do the runtime-guard equation-body re-emit and the `J_gᵀ·lam` cross-terms have to land atomically (re-emit without cross-terms = inconsistent MCP)?

   **Category 8 (infrastructure P8–P10):**
   - Golden-staleness: how large is the known-failing/non-deterministic allowlist, and will the regenerate-diff check be byte-stable under the PR12 determinism guard?
   - KKT-residual harness: what is the GDX dual-transfer mechanism for inequality multipliers that became `comp_*` equations (cf. Sprint 27 Day-9 `pwl_m`/`pwu_m` workaround)?
   - Presolve-divergence detector: what is the false-positive surface (models where embedded ≠ standalone NLP objective for a *legitimate* reason)?

3. **Categorize, prioritize by risk, define a testable verification method and a verification deadline (Day 0 / Day N)** for each unknown — Critical/High unknowns get a Day-0 trace or single-model hypothesis-validation.

4. **Write the document** with all categories, the priority-definition legend, and the update/resolution template (matching the Sprint 27 KNOWN_UNKNOWNS.md structure).

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Document exists and has the expected structure
test -f docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md && echo "KU file present"

# At least 8 categories aligned to the PROJECT_PLAN priorities
grep -c '^## ' docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md

# Every Critical/High unknown has a verification method column populated
grep -E 'Critical|High' docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md | grep -c 'Day '

# Carryforward issues are referenced
grep -oE '#1(224|388|393|335|387|390|374|400|385)' docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md | sort -u
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md` with 25+ unknowns across 8 categories
- Every carryforward fix-surface treated as a Day-0-traceable hypothesis (PR24 alignment)
- The three diagnosis-heavy tracks (#1387/#1390/camcge) flagged Critical with hypothesis-validation verification
- Forward-links from each unknown to the Sprint 28 priority it drives

### Acceptance Criteria

- [x] Document created with 25+ unknowns across 8+ categories (29 unknowns across 10 categories)
- [x] All unknowns have assumption, verification method, priority, risk-if-wrong
- [x] All Critical/High unknowns have a Day-0 trace or single-model hypothesis-validation as their verification
- [x] Carryforward fix-surfaces are framed as hypotheses per PR24 (not as established fact)
- [x] #1387/#1390/camcge flagged Critical (REPLAN-prone) — Unknowns 4.1, 5.1, 6.1
- [x] Infrastructure scope unknowns (P8–P10) captured (Categories 8, 9, 10)
- [x] Update/resolution template defined (§"Template for New Unknowns")

---

## Task 2: Sprint 27 → Sprint 28 Bucket-Provenance Baseline + Projection Discipline (PR15 + PR17 + PR25)

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 4–5 hours
**Deadline:** Before Sprint 28 Day 1
**Owner:** Sprint planning
**Dependencies:** None
**Unknowns Verified:** 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 6.2

### Objective

Establish the Sprint 28 Day-0 baseline metrics with per-failing-model bucket provenance (Sprint 27 final → Sprint 28 Day 0), and produce a **projection table** that labels every projected Solve/Match delta as either a genuine bucket-to-success transition or a forward move within the failure set (PR25). This is the measured starting point against which all Sprint 28 acceptance criteria are evaluated.

### Why This Matters

Sprint 27's Day-0 "+6 firm Match" projection over-counted (retro §"What We'd Do Differently #2"): it assumed fawley/otpop/camcge would land, but all three went `model_infeasible` — forward bucket moves needing deferred work, not Solve/Match gains. The realized Match was +3 (qdemo7/cesam2/launch), exactly the genuine bucket-to-success transitions. Sprint 28 must not repeat this: with six carryforwards whose deliverables are described as "+1 firm" or "+1 conditional," an honest projection that distinguishes the two is the only way to set an achievable target and to recognize a genuine gain at the Day-5/Day-10 checkpoints.

The bucket-provenance baseline also anchors the regression guard: Sprint 27's checkpoint discipline ("measure, don't sweep") depended on knowing the exact committed Solve/Match sets so that any delta could be classified as a real change vs noise. Sprint 28's golden-staleness check (Priority 8) partially mechanizes this, but the Day-0 frozen baseline remains the reference.

### Background

- Sprint 27 final metrics: Parse 142 · Translate 135 · Solve 105 · Match 62 (`SPRINT_27/SPRINT_RETROSPECTIVE.md` header + `SPRINT_LOG.md` final entry)
- Sprint 27 Day-10 Checkpoint 2 full retest buckets: `SPRINT_LOG.md` Day 10 — model_infeasible(7): agreste, camcge, camshape, cesam, fawley, lnts, otpop; path_syntax_error(7): clearlak, dinam, gangesx, indus, sample, turkey, turkpow; path_solve_license(9): egypt, ferts, glider, robot, shale, sroute, srpchase, tabora, tfordy
- Pipeline DB: `gamslib_status.json` (machine-portable paths after Sprint 27 #1400)
- Pipeline runner: `scripts/gamslib/run_full_test.py` (full retest ~4h wall for 142 models; ganges ~8min)
- PR15 (bucket provenance) + PR17 (scope freeze) + PR25 (projection discipline) — Sprint 26/27 process recommendations

### What Needs to Be Done

1. **Run the Day-0 pipeline baseline** (or reuse the committed Sprint 27 final DB if main is unchanged since the Day-13 retest) and record Parse/Translate/Solve/Match + every failure bucket with per-model membership.

2. **Build the bucket-provenance table** — for each carryforward target model (mine, camshape, otpop, cclinpts, kand, camcge) record its Sprint 27 Day-0 → Sprint 27 final → Sprint 28 Day-0 bucket and the issue that gates it.

3. **Author the PR25 projection table** — for each Sprint 28 priority, state the projected delta and label it:
   - **Genuine gain** = a bucket-to-success transition (failure bucket → solve, or solve → match)
   - **Bucket-forward** = a move within the failure set (e.g., model_infeasible → still-failing-but-closer)
   - Tally only genuine gains toward the Solve ≥ 110 / Match ≥ 65 targets; carry bucket-forward moves as "progress, not target credit."

4. **Freeze the Sprint 28 scope** — write the BASELINE_METRICS.md scope-freeze note: which models are in-target, which are explicitly deferred to Sprint 29 (the REPLAN exits), and the committed Solve/Match sets that the regression guard protects.

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Baseline metrics doc exists with the four headline counts
grep -E 'Parse|Translate|Solve|Match' docs/planning/EPIC_4/SPRINT_28/BASELINE_METRICS.md

# Projection table labels each delta genuine-gain vs bucket-forward
grep -Ei 'genuine|bucket-forward' docs/planning/EPIC_4/SPRINT_28/BASELINE_METRICS.md | wc -l

# Carryforward target models each have a provenance row
for m in mine camshape otpop cclinpts kand camcge; do
  grep -q "$m" docs/planning/EPIC_4/SPRINT_28/BASELINE_METRICS.md && echo "$m: present" || echo "$m: MISSING"
done
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_28/BASELINE_METRICS.md` — Day-0 counts + per-failing-model bucket provenance
- PR25 projection table: each priority's delta labeled genuine-gain vs bucket-forward, with only genuine gains tallied toward targets
- Scope-freeze note: in-target vs Sprint-29-deferred models + the committed Solve/Match regression-guard sets
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 6.2

### Acceptance Criteria

- [ ] Day-0 baseline counts recorded (Parse/Translate/Solve/Match + all failure buckets with membership)
- [ ] Bucket-provenance table for the six carryforward target models
- [ ] PR25 projection table distinguishes genuine gains from bucket-forward moves
- [ ] Only genuine gains tallied toward Solve ≥ 110 / Match ≥ 65
- [ ] Scope-freeze note identifies in-target vs deferred models
- [ ] Committed Solve/Match regression-guard sets recorded
- [ ] Unknowns 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 6.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: Codify Process Recommendations PR24 (Day-0 Traced Fix-Surface) + PR25 (Projection Discipline)

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 28 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 1
**Unknowns Verified:** 1.1, 2.1, 3.1, 4.1, 5.1

### Objective

Codify the two new Sprint 27-derived process rules in CONTRIBUTING.md and the Phase-0 acceptance-gate template, **before** the carryforward Phase 0 gates are authored (Task 5), because PR24 changes how those gates establish their fix surface:
- **PR24 — Day-0 traced fix-surface:** prep records the *symptom + reproducer* only; the fix surface is established by a Day-0 trace, never trusted from the prep doc. Phase-0 PROCEED requires citing the *traced* surface.
- **PR25 — Projection discipline:** Solve/Match projections must label each delta as a genuine bucket-to-success transition vs a forward move within the failure set; only the former counts toward the target.

### Why This Matters

The prep-doc fix surface was wrong 4× in Sprint 27 (Days 0/6/11/12) — the real surfaces were `stationarity.py`, `src/ir/ast.py`, and the emit restore pass, NOT the AD sites the prep named. Without a codified rule, the Sprint 28 Phase 0 gates would again cite the prep-doc surface as fact and risk the same wasted-implementation-then-revert cycle that the Phase 0 prototype-before-production discipline narrowly converted into cheap REPLANs. Codifying PR24 turns "treat the surface as a hypothesis" from a per-author habit into a gate requirement. PR25 similarly turns the over-optimistic projection lesson into a standing rule so the Sprint 28 targets are credible.

### Background

- Sprint 27 Retrospective §"What We'd Do Differently #1 (fix surfaces)" + "#2 (projections)"
- Existing process recommendations PR20–PR23 (Sprint 26) already in CONTRIBUTING.md — PR24/PR25 extend them
- CONTRIBUTING.md Phase-0 acceptance-gate section (the 4-subsection template: Hand-Derived KKT Shape, Expected Emit Pattern, Verification Methodology, PROCEED/REPLAN Signal)
- PROJECT_PLAN.md Sprint 28 §"Process Recommendations from Sprint 27" (PR24/PR25 text)

### What Needs to Be Done

1. **Draft the PR24 rule text for CONTRIBUTING.md** — a hard rule: "The prep doc records the symptom and a minimal reproducer. The fix surface (`file:line`) is established by a Day-0 trace at sprint start and is never carried as fact from the prep doc. A Phase-0 PROCEED signal must cite the *traced* surface, with the trace command/evidence recorded."

2. **Amend the Phase-0 template** — add a "Traced Fix-Surface (Day-0)" line to the PROCEED/REPLAN Signal subsection requiring the traced surface + evidence; reword the "Expected Emit Pattern" subsection to note the prep surface is a hypothesis.

3. **Draft the PR25 rule text** — "Every Solve/Match projection labels each delta genuine-gain (bucket-to-success) vs bucket-forward (within the failure set); only genuine gains count toward sprint targets. Day-0 and checkpoint projections must show both tallies."

4. **Cross-reference the new infra tooling** — note in the Phase-0 "Verification Methodology" template that the KKT-residual harness (Task 4 / Priority 9) is the standard Case-(a/b/c) discriminator command (PR27), and that emit-touching PRs must pass the golden-staleness check (PR26).

5. **Verify the rules are self-consistent** with the existing PR20–PR23 text (no contradictions; PR24 strengthens PR20's hand-derived-KKT requirement rather than replacing it).

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# PR24 + PR25 present in CONTRIBUTING.md
grep -E 'PR24|PR25' CONTRIBUTING.md

# Phase-0 template references the traced fix-surface rule
grep -i 'traced fix-surface\|Day-0 trace' CONTRIBUTING.md

# Phase-0 verification-methodology references the KKT-residual harness (PR27)
grep -i 'kkt.residual\|kkt_residual' CONTRIBUTING.md
```

### Deliverables

- CONTRIBUTING.md updated with the PR24 (Day-0 traced fix-surface) hard rule
- CONTRIBUTING.md updated with the PR25 (projection discipline) rule
- Phase-0 template amended: "Traced Fix-Surface (Day-0)" requirement in PROCEED/REPLAN; KKT-residual harness referenced in Verification Methodology (PR27); golden-staleness check referenced (PR26)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 2.1, 3.1, 4.1, 5.1

### Acceptance Criteria

- [ ] PR24 rule codified in CONTRIBUTING.md as a hard Phase-0 requirement
- [ ] PR25 rule codified in CONTRIBUTING.md
- [ ] Phase-0 template requires citing the traced (not prep-doc) surface on PROCEED
- [ ] Phase-0 Verification Methodology references the KKT-residual harness (PR27)
- [ ] No contradiction with existing PR20–PR23 text
- [ ] Rules land before Task 5 (Phase 0 gate authoring) begins
- [ ] Unknowns 1.1, 2.1, 3.1, 4.1, 5.1 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 4: Design the KKT-Residual Verification Harness (PR27 / Priority 9)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 28 Day 1
**Owner:** Development team
**Dependencies:** Task 1
**Unknowns Verified:** 9.1, 9.2, 9.3, 1.3, 2.2, 5.1, 5.2

### Objective

Produce the design spec for the KKT-residual verification harness (`scripts/diagnostics/kkt_residual.py`) so it is the first thing built in-sprint (Days 1–3) and the Phase-0 "Verification Methodology" sections (Task 5) can reference its exact command interface. The harness formalizes Sprint 27's GDX warm-from-good-optimum experiment: given a model, solve the NLP (or load a provided GDX), warm-start the MCP from that solution + transferred duals, and report per-row stationarity/complementarity residuals + a Case-(a/b/c) verdict.

### Why This Matters

The Case-(a/b/c) discriminator — does the NLP KKT point satisfy the emitted stationarity (residual ≈ 0 ⇒ non-convexity, Case c) or not (residual ≠ 0 ⇒ emit bug, Case b)? — was the single most reused diagnostic tool in Sprint 27 (retro §"What Went Well #2"): it classified camshape Case (b) on Day 11, proved kand's phantom-collapse inert on Day 5, and proved launch's 2257.80 a valid KKT point on Day 9. Three of the six Sprint 28 carryforwards (#1224 mine, #1388 camshape, #1390 kand) need exactly this discriminator at their Phase-0 gate. Front-loading the *design* in prep (so the *build* is Days 1–3) means the harness accelerates the carryforward diagnoses that follow rather than being built reactively per-model.

### Background

- Sprint 27 GDX warm-from-good-optimum experiments: `SPRINT_27/SPRINT_LOG.md` Days 9/11 + memory `project_*` entries (launch double-apply; camshape §4.6 discriminator)
- The Day-9 dual-transfer workaround: inequality multipliers that became `comp_*` equations were loaded via parameters `pwl_m`/`pwu_m` (the harness must generalize this — load `.m` marginals into the corresponding `comp_*` / multiplier variables)
- Existing emit knows the multiplier↔equation correspondence (`src/kkt/`, `src/emit/emit_gams.py`) — the harness can reuse this mapping
- PROJECT_PLAN.md Sprint 28 Priority 9 (harness spec) + PR27 (Phase-0 integration)

### What Needs to Be Done

1. **Specify the CLI interface** — `kkt_residual.py <model.gms> [--gdx <solution.gdx>] [--tol 1e-6]`: if no GDX, solve the NLP first; emit the MCP; warm-start it from the NLP primal + transferred duals; run `iterlim=0` (or a residual-only evaluation) and report per-row residuals.

2. **Specify the dual-transfer mechanism** — map each NLP constraint marginal to its MCP multiplier variable (nu_*/lam_*/piL_*/piU_*), including the inequality→`comp_*` case (generalize the Day-9 `pwl_m`/`pwu_m` parameter-load pattern). Document how bounds multipliers (piL/piU) are recovered from `.m` at the solution.

3. **Specify the Case-(a/b/c) verdict logic:**
   - **Case a** = NLP and MCP both solve and match (residual ≈ 0, PATH converges) — no bug.
   - **Case b** = residual ≠ 0 at the NLP KKT point — **emit bug** (the emitted stationarity is wrong).
   - **Case c** = residual ≈ 0 but PATH diverges from a cold start — **non-convexity** (needs warm-start, not an emit fix).
   - Output a per-row residual table + the verdict + the max-residual row (the prime suspect term).

4. **Specify the output format** — machine-readable (JSON) + human summary; integrate as the standard Phase-0 "Verification Methodology" command.

5. **Identify the first three consumers** — mine (#1224), camshape (#1388), kand (#1390) — and sketch the expected harness invocation for each in the spec.

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Design spec exists
test -f docs/planning/EPIC_4/SPRINT_28/PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md && echo "spec present"

# Spec covers the three case verdicts and the dual-transfer mechanism
grep -Ei 'Case a|Case b|Case c|dual.transfer|marginal' docs/planning/EPIC_4/SPRINT_28/PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md

# First-consumer invocations sketched
grep -E 'mine|camshape|kand' docs/planning/EPIC_4/SPRINT_28/PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_28/PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md` — CLI interface, dual-transfer mechanism, Case-(a/b/c) verdict logic, output format
- Worked invocation sketches for the three first consumers (mine/camshape/kand)
- The exact Phase-0 "Verification Methodology" command string for Task 3/Task 5 to reference
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 9.1, 9.2, 9.3, 1.3, 2.2, 5.1, 5.2

### Acceptance Criteria

- [ ] Design spec created with CLI interface fully specified
- [ ] Dual-transfer mechanism documented (including inequality→`comp_*` case)
- [ ] Case-(a/b/c) verdict logic specified with residual thresholds
- [ ] Machine-readable + human output format defined
- [ ] First three consumers (mine/camshape/kand) have sketched invocations
- [ ] The Phase-0 reference command string is finalized for Tasks 3 and 5
- [ ] Unknowns 9.1, 9.2, 9.3, 1.3, 2.2, 5.1, 5.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 5: Author / Refresh Phase 0 Acceptance Gates for the Six Carryforwards (PR20 + PR24)

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 5–7 hours
**Deadline:** Before Sprint 28 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 3, 4
**Unknowns Verified:** 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.2

### Objective

Author or refresh the Phase 0 acceptance gate on each of the six carryforward issue docs (#1224, #1388, #1393+#1335, #1387, #1390, camcge) so each has the four required subsections — Hand-Derived KKT Shape, Expected Emit Pattern (as a hypothesis per PR24), Verification Methodology (referencing the KKT-residual harness per PR27), and PROCEED/REPLAN Signal (citing the Day-0 *traced* surface per PR24). This is the central scope-correctness gate that caught four mis-scopes in Sprint 27.

### Why This Matters

PR20's Phase 0 gate is the primary mitigation against the alias-AD architectural-drift class that has hit five consecutive sprints (S23–S27): a hand-derived KKT shape verified against the emit *before* committing src/ effort. Sprint 27 proved this catches regressions that unit + integration tests miss (Day-11 #1424 discovery; the cesam2 bug-class fixes). For Sprint 28, the gates must additionally embed PR24 (the surface is a Day-0-traced hypothesis) and PR27 (the KKT-residual harness is the verification command) so the gates are executable, not aspirational. Most of the six already have a documented Phase-0 diagnosis from Sprint 27 — the work is to *refresh* them into the new template and flag the three diagnosis-heavy ones (#1387/#1390/camcge) for the Task 6 REPLAN assessment.

### Background

- Carryforward issue docs (each with a Sprint 27 Phase-0 diagnosis or re-scoped filing):
  - `docs/issues/ISSUE_1224_mine-paramref-index-offset-unsupported.md`
  - `docs/issues/ISSUE_1388_camshape-mcp-locally-infeasible-post-pattern-e-reclassification.md`
  - `docs/issues/ISSUE_1393_ad-scalar-eq-sum-collapse-symbolic-superset.md` + `ISSUE_1335_ad-missing-zdef-cross-term-time-reversal-index.md`
  - `docs/issues/ISSUE_1387_*.md` (cclinpts three coupled changes — Day-6 binding diagnosis)
  - `docs/issues/ISSUE_1390_kand-tree-predicate-aliased-sum-architecture-redesign.md`
  - camcge (singular-Jacobian CGE degeneracy — may need a new issue doc if none exists)
- PROJECT_PLAN.md Sprint 28 Priorities 1–6 (each has a per-priority Phase-0 gate description + hand-derived target shape)
- Sprint 27 PRIORITY_*.md fix-surface docs (`PRIORITY_3_RISK_ASSESSMENT.md`, etc.) for the prior diagnoses
- CONTRIBUTING.md Phase-0 template (as amended by Task 3)

### What Needs to Be Done

1. **For each of the six carryforwards, author/refresh the four Phase-0 subsections:**
   - **Hand-Derived KKT Shape** — the per-term Lagrangian stationarity (e.g., for #1224: `stat_x(l,i,j)` with the inverse-offset `sum(k, lam_pr(k,l,i-li(k),j-lj(k)))` − the `l-1` term; for #1388: interior `stat_r(i)` + edge `lam_convex_edge*` cross-terms).
   - **Expected Emit Pattern (hypothesis)** — the GAMS the emit *should* produce, explicitly labeled as the prep hypothesis pending the Day-0 trace.
   - **Verification Methodology** — the exact `kkt_residual.py` invocation + the expected residual + the target PATH solution (e.g., mine MODEL STATUS 1; camshape area ≈ 4.2841; otpop cost ≈ 4217.80; cclinpts rel_diff < 1%; kand 2613.0).
   - **PROCEED/REPLAN Signal** — PROCEED requires the Day-0 traced surface + a residual confirming the hand-derived shape; REPLAN exits explicitly named for #1387/#1390/camcge (→ Sprint 29 with a re-scoped Phase-0 filing).

2. **Flag the diagnosis-heavy three** (#1387, #1390, camcge) in their PROCEED/REPLAN sections with a pointer to the Task 6 hypothesis-validation as a precondition for committing src/ effort.

3. **Cross-link** each gate to its KNOWN_UNKNOWNS.md category (Task 1) and to the BASELINE_METRICS.md provenance row (Task 2).

4. **Sanity-check the hand-derived shapes** against the Sprint 27 diagnoses (do not re-derive from scratch where Sprint 27 already verified — e.g., #1387's per-instance math was residual-verified to 5e-8; #1224's inverse-offset shape is recorded; reuse and cite).

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Each of the six issue docs has a Phase 0 Acceptance Gate with 4 subsections
for f in 1224 1388 1393 1387 1390; do
  echo "=== ISSUE_$f ==="
  grep -l "Phase 0" docs/issues/ISSUE_${f}_*.md && \
  grep -cE '^### (Hand-Derived KKT Shape|Expected Emit Pattern|Verification Methodology|PROCEED)' docs/issues/ISSUE_${f}_*.md
done

# camcge gate present (issue doc or PROJECT_PLAN-linked note)
grep -ril 'camcge' docs/issues/ | head

# Verification Methodology references the KKT-residual harness
grep -l 'kkt_residual' docs/issues/ISSUE_122*.md docs/issues/ISSUE_138*.md
```

### Deliverables

- Refreshed Phase 0 acceptance gates (4 subsections each) on the six carryforward issue docs
- A camcge Phase-0 gate (new issue doc if none exists)
- Each gate references the KKT-residual harness (PR27) and the Day-0 traced-surface rule (PR24)
- REPLAN exits to Sprint 29 explicitly named for #1387/#1390/camcge
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.2

### Acceptance Criteria

- [ ] All six carryforwards have a Phase 0 Acceptance Gate with the four required subsections
- [ ] Hand-derived KKT shapes recorded (reused/cited from Sprint 27 where already verified)
- [ ] Expected Emit Pattern labeled as a hypothesis pending Day-0 trace (PR24)
- [ ] Verification Methodology cites the exact KKT-residual harness invocation + target solution (PR27)
- [ ] PROCEED requires the traced surface; REPLAN exits named for the three diagnosis-heavy tracks
- [ ] Each gate cross-linked to its KNOWN_UNKNOWNS category and BASELINE provenance row
- [ ] Unknowns 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 6: Diagnosis-Heavy Track REPLAN Risk Assessment (#1387, #1390, camcge; PR16)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 4–6 hours
**Deadline:** Before Sprint 28 Day 1
**Owner:** Development team
**Dependencies:** Task 5
**Unknowns Verified:** 4.1, 4.3, 5.1, 5.2, 5.3, 6.1, 6.2

### Objective

Apply the PR16 single-model hypothesis-validation methodology to the three REPLAN-prone carryforwards (#1387 cclinpts three-coupled-change, #1390 kand 195-vs-2613 re-diagnosis, camcge singular-Jacobian) to decide — on evidence, before the sprint commits the 32–46h of combined budget — whether each is a Sprint 28 implementation or a Sprint 29 re-scope. Produce a risk-assessment doc with a PROCEED/REPLAN recommendation per track.

### Why This Matters

Sprint 27's pattern (retro §"What We'd Do Differently #4" + the deep-AD-fix history) is that deep AD fixes routinely prove multi-bug: cclinpts (#1387) was diagnosed, implemented, and *reverted* in Sprint 27 Day 6 because the gradient→stationarity re-symbolization anchor blocker made it three coupled changes, not one. kand (#1390) had its first hypothesis (phantom-term collapse) proven inert after a full env-guarded prototype. camcge is a singular-Jacobian degeneracy that may be inherent (formulation change → Epic 5), not fixable in-sprint. Committing the full budget to all three without a pre-sprint hypothesis-validation risks the exact "partial progress, rest deferred" drift the sprint is trying to avoid. PR16 validation on a single representative scenario per track makes the REPLAN decision cheap and evidence-based.

### Background

- #1387 Day-6 binding diagnosis: three coupled changes (AD offset-enumeration + gradient→stationarity re-symbolization anchor + non-convex warm-start); "sign-flip" is a misdiagnosis (`SPRINT_27/SPRINT_LOG.md` Day 6; memory `MEMORY.md` Day 6 entry)
- #1390 Day-5 re-REPLAN: phantom-term collapse proven inert (MCP stays 195.0 ≠ NLP 2613.0); re-diagnosis surfaces = bal/x stationarity, t-1↔t+1 lag duality, LP recourse coupling (`PRIORITY_3_RISK_ASSESSMENT.md` §3.5)
- camcge: translates `action=c`-clean but model_infeasible from singular-Jacobian CGE degeneracy (distinct from Pattern C)
- PR16 hypothesis-validation methodology (Sprint 26/27 prep: env-guarded prototype, zero src diff, single representative model)
- KKT-residual harness design (Task 4) — the validation instrument

### What Needs to Be Done

1. **#1387 cclinpts** — design (do not implement) the single-model validation: confirm the three coupled changes are still required (re-verify the anchor blocker against current `main`), and assess whether the re-symbolization anchor fix is *architectural* (touching all re-symbolization callers) or *local* (gated to the offset case). Recommendation: PROCEED if local; REPLAN to Sprint 29 if architectural.

2. **#1390 kand** — design the Day-0 trace plan: use the KKT-residual harness to localize the 195-vs-2613 gap to a specific stationarity/complementarity row (bal/x vs lag-duality vs LP-recourse). Recommendation: PROCEED with a fix if the gap is a localizable row; REPLAN to Sprint 29 if it is LP-recourse-coupling architecture. The phantom-term re-symbolization stays explicitly out of scope (proven inert).

3. **camcge** — design the singular-row identification plan: PATH listing basis-singularity report + Jacobian rank check at the NLP point; assess whether a numéraire fix / redundant-row drop preserves the economic solution. Recommendation: PROCEED if a clean numéraire/row fix exists; otherwise document "inherent CGE degeneracy needs formulation change" (→ Epic 5 observation task).

4. **Write the risk-assessment doc** with the per-track PROCEED/REPLAN recommendation, the validation instrument, the budget-at-risk, and the Sprint 29 re-scope path for each.

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Risk-assessment doc exists with a recommendation per track
test -f docs/planning/EPIC_4/SPRINT_28/PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md && echo present
grep -Ei 'PROCEED|REPLAN' docs/planning/EPIC_4/SPRINT_28/PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md

# All three tracks covered
grep -Ei 'cclinpts|#1387|kand|#1390|camcge' docs/planning/EPIC_4/SPRINT_28/PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md | head
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_28/PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md` — per-track hypothesis-validation design + PROCEED/REPLAN recommendation
- Single-model validation plan for each of #1387/#1390/camcge (the instrument, the signal, the decision)
- Explicit Sprint 29 re-scope path per track
- Budget-at-risk tally feeding Task 10's schedule (the lower-bound effort estimate assumes these three partially slip)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.3, 5.1, 5.2, 5.3, 6.1, 6.2

### Acceptance Criteria

- [ ] All three diagnosis-heavy tracks have a single-model hypothesis-validation design
- [ ] Each has a PROCEED/REPLAN recommendation with the deciding signal stated
- [ ] #1387's architectural-vs-local anchor question is the explicit decision pivot
- [ ] #1390's Day-0 trace plan uses the KKT-residual harness to localize the gap
- [ ] camcge's singular-row identification plan + numéraire/Epic-5 fork documented
- [ ] Sprint 29 re-scope path named for each track
- [ ] Unknowns 4.1, 4.3, 5.1, 5.2, 5.3, 6.1, 6.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 7: Golden-Staleness Drift Audit + CI-Check Design (PR26 / Priority 8)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 28 Day 1
**Owner:** Development team
**Dependencies:** Task 2
**Unknowns Verified:** 8.1, 8.2, 8.3

### Objective

Catalog the existing golden-staleness drift across the corpus (which `*_mcp.gms` / `*_mcp_presolve.gms` goldens differ from current emit) and design the `scripts/sprint_audit/check_golden_staleness.py` check + its CI integration + the `make regen-goldens` bulk-refresh target. The audit produces the allowlist (known-failing / non-deterministic models) and sizes the one-time corpus-refresh commit.

### Why This Matters

Sprint 27 retro §"What We'd Do Differently #3": several goldens (cesam/fawley/korcge/dinam) silently drifted from current emit and surfaced as noise in unrelated PRs across Days 9/10/13, forcing per-PR "is this my change or pre-existing staleness?" reconciliation. A regenerate-diff-report check with a CI gate prevents this class of noise entirely and replaces the ad-hoc "measure, don't sweep" reconciliation from Sprint 27. Designing it in prep (and cataloging the current drift) means the in-sprint build (Priority 8) starts from a known drift inventory and a defined allowlist rather than discovering the scope mid-implementation.

### Background

- Sprint 27 staleness incidents: cesam/fawley/korcge/dinam goldens (`SPRINT_27/SPRINT_LOG.md` Days 9/10/13; the Day-10 "reverted incidental retest golden regens" note)
- Golden artifacts: `data/gamslib/mcp/*_mcp.gms` + `*_mcp_presolve.gms`
- Pipeline runner / emit entry: `scripts/gamslib/run_full_test.py`, `src/cli.py`, `src/emit/emit_gams.py`
- Determinism guard (PR12): byte-identical under ≥ 3 `PYTHONHASHSEED` values — the check must be determinism-clean
- PROJECT_PLAN.md Sprint 28 Priority 8 + PR26

### What Needs to Be Done

1. **Run a drift audit** — regenerate every translating model's golden and diff against the committed artifact; produce the current drift inventory (model → drifted/clean → reason).

2. **Define the allowlist** — known-failing (non-translating) and non-deterministic models that the check must exclude, with a documented reason per entry.

3. **Design the check interface** — `check_golden_staleness.py [--fix]`: regenerate → diff → report (and `--fix` to refresh in bulk = `make regen-goldens`); exit non-zero on unexpected drift (not on allowlisted models).

4. **Design the CI integration** — a job under `.github/workflows/` that runs the check on PRs touching `src/{ad,kkt,emit,ir}/`; specify the runtime budget and the failure message format.

5. **Size the one-time corpus-refresh commit** — list the models whose goldens the Day-0/early-sprint refresh will regenerate (cesam/fawley/korcge/dinam/…) so the refresh is a single reviewable commit, separate from any fix.

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Design doc + drift inventory present
test -f docs/planning/EPIC_4/SPRINT_28/PRIORITY_8_GOLDEN_STALENESS_DESIGN.md && echo present

# Drift inventory lists the known Sprint-27 stale models
grep -Ei 'cesam|fawley|korcge|dinam' docs/planning/EPIC_4/SPRINT_28/PRIORITY_8_GOLDEN_STALENESS_DESIGN.md

# Allowlist + CI-integration sections present
grep -Ei 'allowlist|\.github/workflows|regen-goldens' docs/planning/EPIC_4/SPRINT_28/PRIORITY_8_GOLDEN_STALENESS_DESIGN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_28/PRIORITY_8_GOLDEN_STALENESS_DESIGN.md` — current drift inventory, allowlist, check interface, CI integration design, refresh-commit scope
- A drift inventory (model → drifted/clean → reason) sizing the one-time refresh
- The allowlist of known-failing / non-deterministic models with reasons
- `make regen-goldens` target design + CI job design
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 8.1, 8.2, 8.3

### Acceptance Criteria

- [ ] Drift audit run; current drift inventory documented
- [ ] Allowlist defined with a reason per entry
- [ ] Check interface (`check_golden_staleness.py [--fix]`) designed with exit-code semantics
- [ ] CI integration designed (trigger paths, runtime budget, failure-message format)
- [ ] One-time corpus-refresh commit scope sized (which models)
- [ ] Determinism-clean under the PR12 guard confirmed in the design
- [ ] Unknowns 8.1, 8.2, 8.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 8: Divergence Detector + AD Cross-Term Property-Test Catalog Design (Priority 10)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 28 Day 1
**Owner:** Development team
**Dependencies:** Task 1
**Unknowns Verified:** 10.1, 10.2, 10.3

### Objective

Design the `scripts/diagnostics/check_presolve_divergence.py` detector (compare embedded-NLP objective to standalone-NLP objective per `--nlp-presolve` model, flag divergence) and catalog the recurring AD cross-term shapes (offset sums, alias sums, parameter-valued offsets) into a property-test specification (≥ 6 synthetic models with hand-derived KKT) that systematically guards the #1224/#1388/#1390 cross-term defect class.

### Why This Matters

The "embedded NLP pre-solve diverges from standalone" bug class (the `$include` re-running source statements under `$onMultiR`) drove two of Sprint 27's wins (#1378 launch double-applied param; #1424 camshape subset corruption) and is on the running list of recurring patterns (memory `MEMORY.md` Day 11 "Key reusable finding"). A detector that compares the two objectives at translate time would have caught both at Day 0 instead of mid-investigation. The AD cross-term property tests address the deeper recurrence: #1224/#1388/#1390 are all cross-term defects (offset/alias/parameter-valued-offset stationarity), and ad-hoc per-model goldens didn't catch them — synthetic models with a known hand-derived KKT, asserting the emit's cross-terms match, turn this defect class into a systematic guard.

### Background

- Embedded-NLP-divergence wins: #1378 launch (`src/emit/original_symbols.py` self-ref skip), #1424 camshape (`src/emit/emit_gams.py` subset-default skip) — both diverged embedded vs standalone (`SPRINT_27/SPRINT_LOG.md` Days 9/11)
- `--nlp-presolve` emit path: `src/emit/emit_gams.py` (`_will_emit_nlp_presolve`, the `$include` under `$onMultiR`)
- Cross-term defect class: #1224 parameter-valued offset, #1388 `stat_r` interior+edge, #1390 tree-predicate aliased Sum — see the respective ISSUE docs + `docs/research/multidimensional_indexing.md`, `docs/research/nested_subset_indexing_research.md`
- Existing AD/KKT unit-test conventions: `tests/unit/` + `@pytest.mark.unit`
- PROJECT_PLAN.md Sprint 28 Priority 10

### What Needs to Be Done

1. **Design the divergence detector** — `check_presolve_divergence.py`: for each presolve model, extract the embedded-NLP objective (from the `$include`d pre-solve) and the standalone-NLP objective; flag when they diverge beyond tolerance; specify the false-positive handling (models that legitimately differ) via an allowlist.

2. **Catalog the recurring cross-term shapes** — enumerate the synthetic-model shapes needed: (a) single-axis offset Sum `sum(t, ... x(t+1) ...)`; (b) self-alias Sum `sum(jj, a(i,jj)·x(jj))`; (c) cross-set alias Sum; (d) parameter-valued offset `x(i-li(k))`; (e) interior+edge convex-combination (camshape shape); (f) tree-predicate-conditioned aliased Sum (kand shape). For each, write the hand-derived stationarity cross-term the emit must produce.

3. **Specify the property-test suite** — ≥ 6 synthetic GAMS models (small, hand-checkable) + the assertion that the emit's stationarity cross-terms match the hand-derived shape; specify where they live (`tests/unit/ad/` or `tests/integration/emit/`) and how they wire into CI.

4. **Write the design doc** with both components, the synthetic-model shapes, and the CI wiring.

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Design doc present with both components
test -f docs/planning/EPIC_4/SPRINT_28/PRIORITY_10_DIVERGENCE_PROPERTY_TESTS_DESIGN.md && echo present
grep -Ei 'check_presolve_divergence|property test|cross-term' docs/planning/EPIC_4/SPRINT_28/PRIORITY_10_DIVERGENCE_PROPERTY_TESTS_DESIGN.md

# At least 6 synthetic shapes catalogued
grep -cE '^\s*[-*0-9].*offset|alias|parameter-valued|interior|edge|tree' docs/planning/EPIC_4/SPRINT_28/PRIORITY_10_DIVERGENCE_PROPERTY_TESTS_DESIGN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_28/PRIORITY_10_DIVERGENCE_PROPERTY_TESTS_DESIGN.md` — detector design + cross-term shape catalog + property-test spec
- Divergence-detector interface (embedded-vs-standalone objective comparison + allowlist)
- ≥ 6 catalogued synthetic cross-term shapes, each with its hand-derived stationarity term
- CI-wiring plan for both the detector and the property tests
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 10.1, 10.2, 10.3

### Acceptance Criteria

- [ ] Divergence-detector interface designed (embedded-vs-standalone comparison + false-positive allowlist)
- [ ] ≥ 6 recurring cross-term shapes catalogued with hand-derived stationarity terms
- [ ] Property-test suite specified (location, assertion shape, CI wiring)
- [ ] The #1224/#1388/#1390 defect shapes are explicitly represented in the catalog
- [ ] Detector would have caught #1378 + #1424 (validated against those cases in the design)
- [ ] Unknowns 10.1, 10.2, 10.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 9: Lower-Priority Cleanups Fix-Surface Analysis (#1374, #1400, #1385)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 28 Day 1
**Owner:** Development team
**Dependencies:** Task 1
**Unknowns Verified:** 7.1, 7.2, 7.3

### Objective

Identify the candidate fix surfaces (as Day-0-traceable hypotheses per PR24) for the three Sprint 27 lower-priority cleanups so the in-sprint work (Priority 7) starts from a scoped patch-site analysis rather than a cold investigation: #1374 `.l` denominator/override dedup (robot's second shape), #1400 `message`-field captured-warning path relativization (the second absolute-path leak), and #1385 runtime-guard cross-terms (srpchase `J_gᵀ·lam` coupled with the equation-body re-emit).

### Why This Matters

These three are small, well-understood cleanups that round out Sprint 27's deferred work, but each has a coupling risk that must be scoped before implementation: #1374's robot shape may share the `fx_to_l_override` path with the Sprint 27 dominant-shape fix (regression risk); #1385's cross-terms and equation-body re-emit must land atomically (re-emit without cross-terms = inconsistent MCP); #1400's second leak is in the warning-capture path, distinct from the `mcp_file_used` field already fixed. Scoping these in prep keeps them genuinely "lower-priority" (fast, low-risk) instead of expanding mid-sprint.

### Background

- #1374: `docs/issues/ISSUE_1374_emitter-redundant-duplicate-variable-initializations.md`; Sprint 27 fixed the dominant `.fx` shape, robot's `rho.l('h0') = 4.5;` second shape (denominator-init block + `fx_to_l_override`) deferred
- #1400: Sprint 27 fixed `mcp_file_used` (`scripts/gamslib/run_full_test.py:_repo_relative_path`); the `message`-field captured-warning path leak (`…/src/…py:NNN` in warning text) is the second leak
- #1385: `docs/issues/ISSUE_1385_*.md`; srpchase runtime-guard eq-body re-emit (`src/kkt/stationarity.py`) + `J_gᵀ·lam` cross-terms — must land together
- Sprint 27 `PRIORITY_7_FIX_SURFACE.md` for the prior cleanup analyses

### What Needs to Be Done

1. **#1374** — locate the robot second-shape emission (the denominator-init block + `fx_to_l_override`); determine whether dedup is isolatable from the Sprint 27 dominant-shape fix; sketch the emit-time dedup.

2. **#1400** — locate the warning-capture path that emits `…/src/…py:NNN` into the `message` field; sketch the relativization (reuse `_repo_relative_path` or an equivalent) so `gamslib_status.json` is fully machine-portable.

3. **#1385** — confirm the runtime-guard equation-body re-emit (`stationarity.py`) and the `J_gᵀ·lam` cross-terms are the atomic unit; sketch the combined change or document the re-scope if the cross-terms prove larger.

4. **Write the fix-surface analysis** with the candidate surfaces (flagged as Day-0-trace hypotheses), the coupling risks, and the per-item estimate.

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Fix-surface analysis present, all three items covered
test -f docs/planning/EPIC_4/SPRINT_28/PRIORITY_7_CLEANUPS_FIX_SURFACE.md && echo present
grep -Ei '#1374|#1400|#1385|robot|message|srpchase' docs/planning/EPIC_4/SPRINT_28/PRIORITY_7_CLEANUPS_FIX_SURFACE.md | head

# Candidate surfaces flagged as hypotheses (PR24)
grep -i 'hypothes\|Day-0 trace' docs/planning/EPIC_4/SPRINT_28/PRIORITY_7_CLEANUPS_FIX_SURFACE.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_28/PRIORITY_7_CLEANUPS_FIX_SURFACE.md` — candidate fix surfaces (as hypotheses), coupling risks, per-item estimates for #1374/#1400/#1385
- Explicit note that #1385's cross-terms + re-emit are atomic
- Confirmation that #1374's robot shape is/ isn't coupled to the Sprint 27 dominant-shape fix
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 7.1, 7.2, 7.3

### Acceptance Criteria

- [ ] All three cleanups have a candidate fix surface (flagged as a Day-0-trace hypothesis)
- [ ] #1374 robot-shape coupling to the Sprint 27 fix assessed
- [ ] #1400 second-leak (warning-capture path) located
- [ ] #1385 atomic-landing requirement documented
- [ ] Per-item estimate recorded (feeding Task 10's schedule)
- [ ] Unknowns 7.1, 7.2, 7.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 10: Plan Sprint 28 Detailed Schedule

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 28 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1–9
**Unknowns Verified:** (integrates all — Unknowns 1.1–10.3)

### Objective

Create the detailed Sprint 28 plan (`docs/planning/EPIC_4/SPRINT_28/PLAN.md`) and the day-by-day execution prompts (`prompts/PLAN_PROMPTS.md`), incorporating every prior prep task: the Known Unknowns (Task 1), the baseline + projection discipline (Task 2), the codified PR24/PR25 rules (Task 3), the front-loaded KKT-residual harness (Task 4), the Phase 0 gates (Task 5), the REPLAN assessment (Task 6), and the three infrastructure designs + cleanups (Tasks 7–9). This is the final prep task because it depends on all the others.

### Why This Matters

Sprint 27's schedule had two failure modes the Sprint 28 plan must avoid: Day 12 was over-packed (forcing #1224 to consume the whole day and slipping #1400/#1374 to Day 13), and the PLAN_PROMPTS.md repeatedly carried stale assumptions (e.g., "#1387 implemented Day 8" when it never was). The Sprint 28 plan must (a) front-load the KKT-residual harness (Days 1–3) so it accelerates the carryforward diagnoses, (b) sequence the diagnosis-heavy tracks (#1387/#1390/camcge) with their REPLAN exits explicit so a slip is planned, not a surprise, (c) keep ≤ 12 hours/day with real slack for the REPLAN-prone work, and (d) schedule the two checkpoints (Day 5, Day 10) + final retest (Day 13) with the projection-discipline tally (PR25) at each.

### Background

- Sprint 28 scope: `PROJECT_PLAN.md` §"Sprint 28" (Priorities 1–10 + PR24/PR25; Estimated Effort 98–144h; Risk HIGH)
- Sprint 27 schedule lessons: retro §"What We'd Do Differently #4" (Day-12 over-pack); the stale-prompt incidents (memory)
- Effort estimates from Tasks 5/6/7/8/9 (per-priority budgets)
- Sprint 27 PLAN.md + prompts/PLAN_PROMPTS.md as structural templates
- ≤ 12 hours/day budget (14 × 12 = 168h cap; 98–144h estimated work)

### What Needs to Be Done

1. **Author `PLAN.md`** with: Sprint Goals (from PROJECT_PLAN); Day-0 setup + Days 1–13 day-by-day plan; the front-loaded harness (Days 1–3); the carryforward sequence with the diagnosis-heavy tracks gated on their Task-6 REPLAN signals; the two infrastructure tracks (P8 golden-staleness, P10 divergence/property-tests) interleaved as lower-risk fill; per-day integration risks + complexity estimates; the checkpoint schedule (Day 5, Day 10) + final retest (Day 13) with the PR25 projection tally; acceptance criteria; contingency/REPLAN plans.

2. **Author `prompts/PLAN_PROMPTS.md`** — one execution prompt per day, each stating the day's scope, the Phase-0 gate to clear, the KKT-residual harness invocation where relevant, and the "flag stale assumptions" reminder. Ensure no prompt carries a forward-looking claim about work not yet done (the Sprint 27 stale-prompt failure mode).

3. **Verify the schedule fits the budget** — sum the per-day estimates ≤ 168h with the lower bound assuming #1387/#1390/camcge partially slip (per Task 6); confirm no day exceeds 12h.

4. **Cross-link** the plan to the KNOWN_UNKNOWNS, BASELINE_METRICS, the Phase-0 gates, and the three infra design docs.

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Plan + prompts exist
test -f docs/planning/EPIC_4/SPRINT_28/PLAN.md && echo "PLAN present"
test -f docs/planning/EPIC_4/SPRINT_28/prompts/PLAN_PROMPTS.md && echo "PROMPTS present"

# Days 0-13 all present in the plan
for d in 0 1 2 3 4 5 6 7 8 9 10 11 12 13; do
  grep -q "Day $d" docs/planning/EPIC_4/SPRINT_28/PLAN.md || echo "Day $d MISSING"
done

# Checkpoints + final retest scheduled
grep -Ei 'Checkpoint|retest' docs/planning/EPIC_4/SPRINT_28/PLAN.md | head
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_28/PLAN.md` — Day-0 + Days 1–13 with risks, estimates, checkpoints, acceptance criteria, contingency/REPLAN plans
- `docs/planning/EPIC_4/SPRINT_28/prompts/PLAN_PROMPTS.md` — one prompt per day, no stale forward-looking claims
- A schedule that front-loads the KKT-residual harness and gates the diagnosis-heavy tracks on their REPLAN signals
- ≤ 12h/day verified; checkpoints (Day 5/10) + final retest (Day 13) with PR25 tally
- KNOWN_UNKNOWNS.md fully reconciled — all Unknowns 1.1–10.3 carry a final status integrated into the schedule

### Acceptance Criteria

- [ ] `PLAN.md` created with all required sections (Goals, Days 0–13, risks, estimates, checkpoints, acceptance, contingency)
- [ ] `prompts/PLAN_PROMPTS.md` created with one prompt per day, no stale forward-looking claims
- [ ] KKT-residual harness front-loaded (Days 1–3)
- [ ] Diagnosis-heavy tracks (#1387/#1390/camcge) gated on Task-6 REPLAN signals
- [ ] Two checkpoints (Day 5, Day 10) + final 3× determinism retest (Day 13) scheduled with the PR25 tally
- [ ] ≤ 12h/day budget verified; no day over-packed
- [ ] Cross-linked to KNOWN_UNKNOWNS, BASELINE_METRICS, Phase-0 gates, infra design docs
- [ ] Unknowns 1.1–10.3 reconciled (integrated) in KNOWN_UNKNOWNS.md

---

## Summary: Prep Task Execution Order

Execute in this logical order:

**Phase 1: Risk Identification + Baseline (parallel, no deps)**
1. Task 1: Create Sprint 28 Known Unknowns List (3–4h)
2. Task 2: Sprint 27 → Sprint 28 Bucket-Provenance Baseline + Projection Discipline (4–5h)

**Phase 2: Process Codification + Harness Design (the gate-correctness foundation)**
3. Task 3: Codify PR24 (Day-0 Traced Fix-Surface) + PR25 (Projection Discipline) (2–3h) — *must precede Task 5*
4. Task 4: Design the KKT-Residual Verification Harness (3–4h) — *feeds Task 5's verification methodology*

**Phase 3: Phase 0 Gates + REPLAN Assessment**
5. Task 5: Author / Refresh Phase 0 Acceptance Gates for the Six Carryforwards (5–7h)
6. Task 6: Diagnosis-Heavy Track REPLAN Risk Assessment (#1387, #1390, camcge) (4–6h)

**Phase 4: Infrastructure + Cleanup Designs (parallel)**
7. Task 7: Golden-Staleness Drift Audit + CI-Check Design (3–4h)
8. Task 8: Divergence Detector + AD Cross-Term Property-Test Catalog Design (3–4h)
9. Task 9: Lower-Priority Cleanups Fix-Surface Analysis (#1374, #1400, #1385) (2–3h)

**Phase 5: Planning**
10. Task 10: Plan Sprint 28 Detailed Schedule (3–4h)

**Total Time:** 32–44 hours (~4–5.5 working days)

**Critical Path:** Task 1 → Task 3 → Task 5 → Task 10 (the Phase-0 codification chain — PR24 changes how the gates are authored, so the rule must land before the gates).

---

## Prep Completion Checklist

Before Sprint 28 Day 1, verify:

### Critical (Must Complete)
- [x] Known unknowns list created (29 unknowns across 10 categories, fix-surfaces framed as Day-0-trace hypotheses) — `KNOWN_UNKNOWNS.md`, 2026-06-09
- [ ] Day-0 baseline + PR25 projection table (genuine-gain vs bucket-forward) created
- [ ] PR24 (traced fix-surface) + PR25 (projection discipline) codified in CONTRIBUTING.md
- [ ] Phase 0 acceptance gates authored/refreshed for all six carryforwards
- [ ] Sprint 28 detailed schedule + day-by-day prompts created (≤ 12h/day)

### High Priority (Should Complete)
- [ ] KKT-residual harness design spec complete (referenced by the Phase-0 gates)
- [ ] Diagnosis-heavy REPLAN risk assessment (#1387/#1390/camcge) with PROCEED/REPLAN recommendations
- [ ] Golden-staleness drift audit + CI-check design complete

### Medium Priority (Can Complete Early in Sprint 28)
- [ ] Divergence detector + AD cross-term property-test catalog design
- [ ] Lower-priority cleanups fix-surface analysis (#1374/#1400/#1385)

### Verification

```bash
# All prep artifacts present
ls docs/planning/EPIC_4/SPRINT_28/

# Phase-0 gates on the six carryforwards
for f in 1224 1388 1393 1387 1390; do grep -l "Phase 0" docs/issues/ISSUE_${f}_*.md; done

# Process rules codified
grep -E 'PR24|PR25' CONTRIBUTING.md

# Schedule fits the budget
grep -Ei 'Day [0-9]' docs/planning/EPIC_4/SPRINT_28/PLAN.md | head -20
```

**When all critical items checked: Sprint 28 ready to begin.**

---

## Success Criteria

This prep plan succeeds if Sprint 28 starts with:

1. **No unverified fix-surfaces taken as fact** — every carryforward surface is a Day-0-trace hypothesis (PR24), so the four-times-repeated Sprint 27 mis-scope cannot recur silently.
2. **A credible, honestly-labeled target** — the PR25 projection distinguishes genuine gains from bucket-forward moves, so Solve ≥ 110 / Match ≥ 65 is set on real transitions.
3. **A mechanized Case-(a/b/c) discriminator** — the KKT-residual harness design is ready to build Days 1–3 and is the verification method in every relevant Phase-0 gate.
4. **Planned REPLANs, not surprises** — the three diagnosis-heavy tracks (#1387/#1390/camcge) have explicit PROCEED/REPLAN signals and Sprint 29 exits.
5. **Durable tooling leverage** — the golden-staleness check, divergence detector, and AD cross-term property tests are designed to catch the recurring bug classes automatically, so even if the hardest carryforwards slip, Sprint 28 leaves the pipeline more defensible than it found it.

**Estimated prep investment:** 4–5.5 days
**Expected benefit:** avoids the Sprint 27 mis-scope-then-REPLAN overhead on six carryforwards + establishes the diagnostic tooling that accelerates every subsequent AD/KKT sprint.

---

## Appendix: Document Cross-References

### Sprint 28 Scope + Goals
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 28 (Weeks 21–22): Sprint 27 Carryforward — KKT Cross-Term Correctness, AD Architectural Fixes & Diagnostic/CI Tooling" (Priorities 1–10 + Process Recommendations PR24/PR25 + Acceptance Criteria + Estimated Effort)
- `docs/planning/EPIC_4/GOALS.md` (Epic 4: Full GAMSLIB LP/NLP/QCP coverage; Solve Completion + Solution Matching themes)

### Sprint 27 Source Material
- `docs/planning/EPIC_4/SPRINT_27/SPRINT_RETROSPECTIVE.md` (§"Sprint 28 Recommendations" Priorities 1–7; §"What We'd Do Differently" #1–#4 → PR24/PR25; §"What Went Well" #2 → KKT-residual harness + divergence detector; §"KU Coverage Summary")
- `docs/planning/EPIC_4/SPRINT_27/SPRINT_LOG.md` (per-day entries; Day-10 Checkpoint 2 full bucket membership; final metrics)
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` (Cat 1–9, all resolved — open-item migration source)
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` + `prompts/PLAN_PROMPTS.md` (structural templates for Task 10)
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md` (#1390 §3.5 re-REPLAN), `PRIORITY_7_FIX_SURFACE.md` (#1385/#1374/#1400 cleanup context), `PRIORITY_1_ANCHOR_MAPPING.md`, `PRIORITY_5_FIX_SURFACE.md`

### Carryforward Issues (Phase-0 gate targets)
- `docs/issues/ISSUE_1224_mine-paramref-index-offset-unsupported.md` (P1 — parameter-valued-offset cross-term inversion)
- `docs/issues/ISSUE_1388_camshape-mcp-locally-infeasible-post-pattern-e-reclassification.md` (P2 — Case-(b) `stat_r`)
- `docs/issues/ISSUE_1393_ad-scalar-eq-sum-collapse-symbolic-superset.md` + `ISSUE_1335_ad-missing-zdef-cross-term-time-reversal-index.md` (P3 — otpop)
- `docs/issues/ISSUE_1387_*.md` (P4 — cclinpts three coupled changes)
- `docs/issues/ISSUE_1390_kand-tree-predicate-aliased-sum-architecture-redesign.md` (P5 — kand re-diagnosis)
- `docs/issues/ISSUE_1374_emitter-redundant-duplicate-variable-initializations.md` (P7 — robot `.l` dedup)
- `docs/issues/ISSUE_1385_option-1-short-circuit-redesign-symbolic-instance-handling.md` (P7 — runtime-guard cross-terms)
- `docs/issues/ISSUE_1424_emit-dynamic-subset-defaults-corrupts-model-assigned-subsets.md` (#1388 warm-start unblock context — landed Sprint 27)

### Related Research
- `docs/research/multidimensional_indexing.md`, `docs/research/nested_subset_indexing_research.md` (cross-term / offset shapes for the Task 8 property-test catalog)
- `docs/research/convexity_detection.md`, `docs/research/CONVEXITY_VERIFICATION_DESIGN.md` (Case-c non-convexity context for the KKT-residual harness verdict)
- `docs/research/minmax_path_validation_findings.md` (PATH solve-status interpretation)

### Process / Tooling
- `CONTRIBUTING.md` §"Phase 0 Acceptance Gate" (PR20 template; amended by Task 3 with PR24/PR25)
- `scripts/gamslib/run_full_test.py` (pipeline runner; `_repo_relative_path` for #1400)
- `scripts/sprint_audit/changed_emit_artifacts.py` (PR22 mid-sprint audit; reused at checkpoints)
- `data/gamslib/mcp/*_mcp.gms`, `*_mcp_presolve.gms` (golden artifacts for the Task 7 staleness check)

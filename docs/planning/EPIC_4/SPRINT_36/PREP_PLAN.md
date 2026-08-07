# Sprint 36 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 36 (the Sprint-35 carryforward sprint) begins
**Timeline:** Complete before Sprint 36 Day 1
**Goal:** De-risk the Sprint-35 REPLAN'd/deferred/banked carryforwards so each track starts Day 1 with a control-confirmed, precisely-pinned specification — not an open question

**Key Insight from Sprint 35:** the control-first REPLAN discipline (PR24/PR27) held for the fifth+ consecutive sprint — every deep track was refuted or banked on control evidence *before* any bad ship (zero broken code). Sprint 35's genuine discovery — the **markov diagonal-Kronecker +1-floor lever** — is half-de-risked already (Part 1 of the fix verified, residual 13.3→1.55). This prep phase carries that discipline forward: re-confirm every banked diagnosis on the current tree, then design the one deep unknown per track (markov Part-2 `σ=sp`, fawley's derivative-structure discriminator, ganges's `$66`/`rPower`) *before* Day 1.

---

## Executive Summary

`PROJECT_PLAN.md` (Sprint 36, Weeks 37–38) defines the Sprint-35 carryforward sprint. Sprint 35 closed **modal-flat** (Solve 108 / Match 93 / genuine floor 75 — the third consecutive), so each carryforward inherits a de-risked diagnosis rather than a raw problem. Sprint 36 will address:

1. **Priority 1 (Critical — the headline lever):** markov `stat_z` diagonal-Kronecker correction — a control-confirmed `CASE_B` cold-emit bug making a `verified_convex` model a *methodology* match; the two-part fix flips it methodology→genuine (floor 75→76, fully local). Part 1 verified; Part 2 (`σ=sp` off-diagonal enumeration) is the deep unknown.
2. **Priority 2 (High):** sarf symbolic-emit subsystem (#1385) — the 369K-column `task` materialization needs a from-scratch symbolic/parametric emit MODE (O(active=398), not O(369K)).
3. **Priority 3 (High):** fawley constraint-index-diagonal correction (#1111/#1112) — control-verified (473→1.14e-13) but the general predicate leaks onto markov #1110; needs a **derivative-structure discriminator**. +Solve is H-b → a `--force` survey.
4. **Priority 4 (High):** ganges/gangesx multi-root recovery — a ≥5-blocker cascade (`$141`/`$145`/`$149` → `$66` → `rPower`); the `$149` `_diff_prod` fix is verified+banked.
5. **Priority 5 (Medium):** the rocket/mine consultation trio + camcge Walras (**Epic 5**).
6. **Priority 6 (Medium):** turkey v54 testbed re-solve + the residual multi-root cohort.
7. **Priority 7 (Medium — infrastructure):** the GAMS-54 corpus re-baseline (the v53→v54 transition's first infra task) + robustlp NA fix + property fixtures + genuine-floor tracking.

This prep plan focuses on the research, design, and setup tasks that must complete before Sprint 36 Day 1 to prevent Day-1-through-Day-5 blocking on an un-designed deep track or an unverified banked diagnosis.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint 36 Goal Addressed |
|---|------|----------|-----------|--------------|--------------------------|
| 1 | Create Sprint 36 Known Unknowns List | Critical | 3-4 hours | None | Proactive unknown identification across all 7 priorities |
| 2 | Re-Confirm the Sprint-35 Baseline & Banked-Diagnosis Fingerprints | Critical | 3-4 hours | Task 1 | Verify 108/93/75 + the control fingerprints still hold on current `main` |
| 3 | markov P1 — Part-2 (`σ=sp`) Off-Diagonal Enumeration Design | Critical | 5-7 hours | Tasks 1, 2 | P1 markov diagonal-Kronecker +1-floor lever |
| 4 | fawley P3 — Derivative-Structure Discriminator Design | High | 4-6 hours | Tasks 1, 2, 3 | P3 fawley constraint-index-diagonal correction |
| 5 | sarf P2 — Symbolic-Emit Subsystem Design Refresh & Blow-Up Re-Measurement | High | 4-5 hours | Tasks 1, 2 | P2 sarf symbolic-emit subsystem |
| 6 | ganges/gangesx P4 — ≥5-Blocker Cascade Re-Verification & Recovery Sequencing | High | 3-4 hours | Tasks 1, 2 | P4 ganges/gangesx multi-root recovery |
| 7 | GAMS-54 Licensed-Testbed Re-Baseline Harness Plan (P7 + turkey P6) | Medium | 3-4 hours | Tasks 1, 2 | P7 GAMS-54 re-baseline + P6 turkey testbed re-solve |
| 8 | Consultation Bundle Finalization (rocket/mine P5) + camcge Epic-5 Gate Scoping | Medium | 2-3 hours | Tasks 1, 2 | P5 rocket/mine consultation + camcge Walras (Epic 5) |
| 9 | Property-Fixture & 2-D-Cohort Regression-Harness Catalog + robustlp NA Survey | Medium | 3-4 hours | Tasks 1, 3, 4 | P7 fixtures / genuine-floor tracking / robustlp NA fix |
| 10 | Plan Sprint 36 Detailed Schedule | Critical | 3-4 hours | All tasks (1–9) | Day-by-day schedule + REPLAN exits + budget |

**Total Estimated Time:** ~33-45 hours (~4-6 working days)

**Critical Path:** Tasks 1 → 2 → 3 → 4 → 9 → 10 (the markov P1 design and its shared-function interaction with fawley P3 gate the fixture catalog and the schedule).

**Note:** Task 1 (Known Unknowns) is the standing first prep task; it must be created before the design tasks (3–9) so each design is scoped against an explicit risk register.

---

## Task 1: Create Sprint 36 Known Unknowns List

**Status:** ✅ COMPLETE (2026-08-06)
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 36 Day 1
**Owner:** Sprint 36 execution team
**Dependencies:** None

### Objective

Create `docs/planning/EPIC_4/SPRINT_36/KNOWN_UNKNOWNS.md` cataloguing every open question, assumption, and risk across the seven Sprint-36 priorities, each with an assumption statement, a verification method, a priority, and a target resolution point (prep task or sprint day).

### Why This Matters

The Known-Unknowns process has caught late surprises before they became mid-sprint blockers across Sprints 27–35. Sprint 36 front-loads two deep unknowns (markov Part-2 `σ=sp` enumeration; fawley's derivative-structure discriminator) plus a testbed dependency (the GAMS-54 re-baseline needs a licensed >1000-row solve). Surfacing these as tracked unknowns on Day 0 lets the design tasks (3–9) resolve them proactively rather than discovering them on Day 3.

### Background

Each prior sprint's `KNOWN_UNKNOWNS.md` (e.g. `docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md`) partitions unknowns into VERIFIED / REPLAN / DESIGN-SPECIFIED / INCOMPLETE and drives the Day-0 fingerprint re-confirmation. Sprint 35 closed with the banked diagnoses in `SPRINT_35/SPRINT_36_CARRYFORWARDS.md`; Sprint 36's unknowns are the *residual* questions those carryforwards leave open (e.g. "does the markov Part-1 diagonal split still leak onto the 2-D cohort?", "is the ganges `$149` `_diff_prod` fix still byte-clean on current `main`?", "does the fawley discriminator interact with the markov #1110 path?").

### What Needs to Be Done

1. **Enumerate unknowns per priority (P1–P7).** For each track, list the residual open questions from its banked carryforward doc:
   - **P1 markov:** does the Part-1 diagonal split still drive residual 13.3→1.55 on current `main`? Does the `σ=sp` enumeration have a representable offset form, or does it need a new multiplier-index mechanism? Will the fix leak onto cesam2/camcge/ps2/ps3/polygon?
   - **P2 sarf:** is the 369K blow-up still >303s on current `main`? Does the O(active=398) guarded-emit form pass GAMS instantiation?
   - **P3 fawley:** can a derivative-structure key distinguish fawley's constraint-index-diagonal from the markov #1110 off-diagonal? Does the discriminator co-exist with the P1 markov change in `_add_indexed_jacobian_terms`?
   - **P4 ganges:** does the banked `$149` `_diff_prod` fix still apply? Are `$66`/`rPower` still the terminal blockers? Can the slow CGE goldens be regenerated in the sprint budget?
   - **P5 rocket/mine/camcge:** is the rocket consultation input still submission-ready? Is the camcge Walras Epic-5 gate reachable in a `/tmp` control?
   - **P6 turkey/residual:** is a licensed GAMS-54 testbed available to solve turkey's 3,866-row MCP?
   - **P7 GAMS-54:** which of the 5 OBJ-GAP models shift buckets under v54? What is the robustlp NA root term?
2. **Assign each unknown:** assumption, verification method, priority (Critical/High/Medium/Low), and target resolution (which prep task or which sprint day).
3. **Tag each with a disposition slot:** VERIFIED / REPLAN / DESIGN-SPECIFIED / INCOMPLETE (initially INCOMPLETE for open ones).
4. **Flag Day-0 blockers** — any unknown whose non-resolution blocks Day 1.

### Changes

Created `docs/planning/EPIC_4/SPRINT_36/KNOWN_UNKNOWNS.md` (30 unknowns across 7 categories, numbered `X.Y` per category) following the Sprint-35 KNOWN_UNKNOWNS conventions: Executive Summary, How to Use This Document (with priority definitions), Summary Statistics, Table of Contents, the 7 category blocks, a Confirmed Knowledge section, the Template for New Unknowns, Next Steps, and an `## Appendix: Task-to-Unknown Mapping` table. Added a "Deferred-unknown lineage" note tracing each track to its Sprint-35 disposition. Also added the "**Unknowns Verified:**" metadata + a KNOWN_UNKNOWNS-update deliverable + acceptance criterion to PREP_PLAN.md Tasks 2–10.

### Result

30 unknowns documented (Critical 8 / High 12 / Medium 7 / Low 3 = ~27/40/23/10%; ~35h total research time — within the 28–36h target). Every unknown carries Priority, Assumption, 3–5 Research Questions, How to Verify, Risk if Wrong, Estimated Research Time, Owner, and a `🔍 Status: INCOMPLETE` Verification Results slot. The Task-to-Unknown mapping assigns every unknown (1.1–7.5) to ≥1 prep task (Tasks 2–9), with the 8 Critical unknowns front-loaded into Tasks 2–7. Zero Day-0 blockers remain unmapped. The two deep prep-phase design priorities (Unknown 1.2 markov `σ=sp`; Unknown 3.2 the fawley/markov shared-function collision) are called out in the Executive Summary and Next Steps.

### Verification

```bash
# The document exists and has the expected structure
test -f docs/planning/EPIC_4/SPRINT_36/KNOWN_UNKNOWNS.md && echo "KU doc exists"
# All seven priorities are represented
for p in markov sarf fawley ganges rocket turkey "GAMS[.-]54"; do
  grep -qiE "$p" docs/planning/EPIC_4/SPRINT_36/KNOWN_UNKNOWNS.md && echo "  covers: $p"
done
# Each unknown carries an assumption + verification + priority
grep -ciE "assumption|verification|priority" docs/planning/EPIC_4/SPRINT_36/KNOWN_UNKNOWNS.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_36/KNOWN_UNKNOWNS.md` — the Sprint-36 unknowns register (all 7 priorities), each with assumption / verification / priority / target resolution / disposition slot
- A count of Day-0 blockers (target: 0 unresolved at Day 1)

### Acceptance Criteria

- [x] Document created covering all seven priorities (P1–P7) — 30 unknowns
- [x] Each unknown has an assumption, a verification method (How to Verify), a priority, and a target resolution point (the verifying prep task)
- [x] Each unknown carries a disposition slot (`🔍 Status: INCOMPLETE`, to advance to VERIFIED / WRONG during prep)
- [x] Day-0 blockers explicitly flagged (and mapped to Tasks 2–7; the Task-10 GO/NO-GO gates them)
- [x] The two deep unknowns (Unknown 1.2 markov `σ=sp`; Unknown 3.2 fawley/markov shared-function collision) are called out as the prep-phase design priorities

---

## Task 2: Re-Confirm the Sprint-35 Baseline & Banked-Diagnosis Fingerprints

**Status:** ✅ COMPLETE (2026-08-06)
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 36 Day 1
**Owner:** Sprint 36 execution team
**Dependencies:** Task 1
**Unknowns Verified:** 1.1, 3.3, 3.4

### Objective

Re-verify, on the current `main`, that the Sprint-35-close baseline (Solve 108 / Match 93 / genuine floor 75) and each banked control fingerprint still hold — so Sprint 36's designs build on measured reality, not a two-week-old snapshot.

### Why This Matters

Sprint 36's carryforwards are "de-risked specifications," but that de-risking was measured at the S35 close (`597d9d08`). Between then and Sprint 36 Day 1, `main` advanced (the Sprint-36 plan insertion, and any other merges). A silent baseline drift or a fingerprint that no longer reproduces would invalidate a design task's premise. This is the standard Day-0 anchor re-confirmation (the "prep-doc `file:line` fix-surfaces are HYPOTHESES; verify before implementing" lesson).

### Background

The S35-close anchor is `597d9d08`; the sprint anchor for `--resolve-changed` is `78ceaead`. The DB was byte-unchanged since the anchor (0 bucket move). The banked fingerprints to re-confirm: markov `CASE_B` `max|stat_z|` rel 13.3 (`kkt_residual.py markov`); fawley `CASE_B` `stat_bq` 0.973 + `stat_trans(tr-2)` H-b; ganges ≥5-blocker cascade; the S35 P4 markov Part-1 diagonal split residual 13.3→1.55 (documented in `DAY11_MARKOV_DIAGONAL_LEVER.md` §6). markov is tiny (2 vars / 3 eqns) so its control is seconds-scale and fully local.

### What Needs to Be Done

1. **Re-compute the KPI baseline** from the committed DB over the 142 convex candidates: confirm Solve 108 / Match 93 / Translate 135 / path_syntax_error 7 / genuine floor 75.
2. **Confirm DB + emit integrity vs the anchor:** `git diff 78ceaead..HEAD` on `data/gamslib/gamslib_status.json` (expect empty) and on `src/` (expect only the turkey `original_symbols.py` delta).
3. **Re-run the markov control** (`kkt_residual.py data/gamslib/raw/markov.gms`) — confirm `CASE_B`, `max|stat_z|` rel ≈ 13.3 on `stat_z(empty,disrupted,*)`, dual transfer CONSISTENT.
4. **Re-confirm the markov Part-1 diagonal split reduces the residual** by re-reading `DAY11_MARKOV_DIAGONAL_LEVER.md` §6 and (optionally) re-applying the documented Part-1 change on a scratch branch to confirm 13.3→1.55 still reproduces (revert after — this is a measurement, not a landing).
5. **Re-run the fawley control** (`kkt_residual.py`) — confirm `CASE_B`, `stat_bq` ≈ 0.973, and the emit-correct `stat_trans(tr-2)` H-b divergence.
6. **Re-confirm the ganges cascade shape** — re-read `DAY3_P4_BANK_CARRYFORWARD.md`; confirm the `$149` `_diff_prod` fix location (`derivative_rules.py`) is unchanged on `main`.
7. **Record each result** in the KU doc's disposition slots (VERIFIED / drift-detected).

### Changes

Created `docs/planning/EPIC_4/SPRINT_36/DAY0_TRACE_NOTES.md` (the Day-0 baseline & fingerprint re-confirmation: KPI recompute, DB/emit/golden integrity vs the anchor, the markov + fawley control outputs, the emit/AD code-surface integrity, and the ganges `$149`/`$141` surface confirmation). Marked Unknowns 1.1, 3.3, 3.4 → ✅ VERIFIED in `KNOWN_UNKNOWNS.md` (with Findings/Evidence/Decision), and added Task-2 contribution notes to Unknowns 4.1, 5.4, 7.5.

### Result

**GO — every fingerprint re-confirms exactly on current `main`.** KPI recompute over the 142 convex candidates = **Translate 135 / Solve 108 / Match 93 (63 cold + 30 presolve) / pse 7 / mi 7 / all-219 96 / genuine floor 75** (= S35 close). DB byte-unchanged vs `78ceaead`; the only `src/` delta is the turkey `original_symbols.py`; the only changed golden is `turkey_mcp.gms`. markov control = `CASE_B`, `max|stat_z|` rel **13.3**, dual CONSISTENT (exact S35 Day-11 match); markov stays methodology (`model_optimal_presolve`+match). fawley control = `CASE_B`, `stat_bq` rel **0.973**, harness max = the emit-correct H-b `stat_trans(tr-2)` rel 1.00. `stationarity.py` + `derivative_rules.py` are byte-identical to the S35 measurement tree, and the fawley/markov goldens are unchanged — so the banked reductions (markov 13.3→1.55; fawley 473→1.14e-13) reproduce on identical inputs. The `$149` `_diff_prod` surface (`derivative_rules.py:3276`) and the correct `$141` helper (`_expr_contains_varref_attribute`) are present and unchanged. **No drift detected.** Verifies Unknowns 1.1, 3.3, 3.4; contributes to 4.1, 5.4, 7.5.

### Verification

```bash
# DB + emit integrity vs the sprint anchor
git diff 78ceaead..HEAD --stat -- data/gamslib/gamslib_status.json   # expect empty
git diff 78ceaead..HEAD --stat -- src/                               # expect only original_symbols.py

# markov control reproduces CASE_B (tiny model, fast)
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/markov.gms 2>&1 | grep -E "verdict|max-residual"

# KPI recompute over the 142 convex candidates
.venv/bin/python - <<'PY'
import json
db=json.load(open('data/gamslib/gamslib_status.json'))['models']
cvx=[m for m in db if (m.get('convexity') or {}).get('status') in ('verified_convex','likely_convex')]
solve=sum(1 for m in cvx if (m.get('mcp_solve') or {}).get('outcome_category') in ('model_optimal','model_optimal_presolve'))
match=sum(1 for m in cvx if ((m.get('solution_comparison') or {}).get('comparison_status'))=='match')
print(f"candidates={len(cvx)} Solve={solve} Match={match}")
PY
```

### Deliverables

- A Day-0 baseline re-confirmation note (in the KU doc or a short `DAY0_TRACE_NOTES.md`): KPIs re-computed, DB/emit integrity vs anchor, and each banked fingerprint marked VERIFIED or drift-detected
- The markov / fawley control outputs captured (verdict + max-residual rows)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 3.3, 3.4

### Acceptance Criteria

- [x] KPI baseline re-computed = 108 / 93 / 75 (Solve / Match / floor), Translate 135, pse 7 — exact S35-close match, no drift
- [x] DB byte-unchanged vs `78ceaead`; `src/` delta = only the turkey fix (`original_symbols.py`)
- [x] markov control reproduces `CASE_B` `max|stat_z|` rel ≈ 13.3 (dual transfer CONSISTENT)
- [x] fawley control reproduces `CASE_B` `stat_bq` ≈ 0.973 (H-b `stat_trans(tr-2)` rel 1.00 the harness max)
- [x] The markov Part-1 diagonal split still reduces the residual to ≈ 1.55 (reproduces deductively — `stationarity.py` + `markov_mcp.gms` byte-identical to the Day-11 tree)
- [x] The ganges `$149` `_diff_prod` fix surface is unchanged on `main` (`derivative_rules.py:3276`)
- [x] Every re-confirmation recorded in the KU disposition slots + `DAY0_TRACE_NOTES.md`
- [x] Unknowns 1.1, 3.3, 3.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: markov P1 — Part-2 (`σ=sp`) Off-Diagonal Enumeration Design

**Status:** ✅ COMPLETE (2026-08-06)
**Priority:** Critical
**Estimated Time:** 5-7 hours
**Deadline:** Before Sprint 36 Day 1
**Owner:** Sprint 36 execution team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 1.2, 1.3, 1.4

### Objective

Produce a written design for the markov fix's **Part 2** — the off-diagonal enumeration where the constraint multiplier index equals an *independent* variable index (`σ=sp`, the variable's 3rd) that the current offset machinery cannot represent — so Sprint 36 Day 1 starts with a control-gated implementation plan, not an open research question.

### Why This Matters

markov is the sprint's only fully-local +1-floor lever (methodology→genuine, no testbed gate). Part 1 (the diagonal-Kronecker split) is already implemented + verified (13.3→1.55), but Part 2 is the deep blocker: reaching `CASE_A` requires the off-diagonal contribution `−b·Σ_τ pr(i,τ)·nu_constr(sp,τ)` with `σ=sp`, and the S35 Day-11 attempt showed the offset machinery expresses `σ` only as offsets from `s` (the 1st index), degenerating into 44 spurious groups. Without a Part-2 design, Day 1 spends its budget re-discovering the S35 finding.

### Background

`DAY11_MARKOV_DIAGONAL_LEVER.md` §6 has the full diagnosis: markov's `stat_z/z` splits into 45 offset groups (#1045); the diagonal is its own single-key group `(0,0,999)` (Part-1 handles it); the off-diagonal needs a multiplier index bound to `sp` (an independent var index), which `_compute_index_offset_key` / `_add_indexed_jacobian_terms` (`src/kkt/stationarity.py:5861+`) cannot encode as an offset-from-`s`. The correct target form and the derivation are in the doc; the open design question is the *mechanism* — how to represent a determined-but-non-first multiplier index in the offset/multi-pattern machinery.

### What Needs to Be Done

1. **Re-read `DAY11_MARKOV_DIAGONAL_LEVER.md` §2–§6** — the derivation, the Part-1 implementation, and the Part-2 blocker.
2. **Characterize the `σ=sp` representation gap:** document precisely why `_compute_index_offset_key` produces `(offset-from-s, …, SENTINEL)` and cannot express `σ=sp`. Identify the exact code path (offset-key computation + the sub-group emission).
3. **Enumerate candidate mechanisms:** e.g. (a) a new "bound-to-var-index" offset-key marker (analogous to the SENTINEL) that maps a multiplier position directly to a var position; (b) a `sameas`-guarded direct term (like the diagonal Part-1) for the `σ=sp` slice; (c) a dedicated multi-pattern branch for the "independent-index multiplier" shape. For each: sketch the emitted GAMS and the blast radius.
4. **Pick the minimal, lowest-blast-radius mechanism** and specify the code change surface (which function, which branch).
5. **Specify the Phase-0 control:** the exact `/tmp` hand-edit (or scratch-branch) experiment that must drive `kkt_residual.py markov` → `CASE_A` (rel < tol) *before* the `src/` change.
6. **Specify the leak-freedom gate:** the golden-staleness check (only markov drifts; cesam2/camcge/ps2/ps3/polygon byte-identical) and how it interacts with the fawley P3 discriminator (Task 4).

### Changes

Created `docs/planning/EPIC_4/SPRINT_36/MARKOV_OFFDIAGONAL_DESIGN.md` — the Part-2 design: the root-caused representation gap, the correct target form, three candidate mechanisms (+ blast radius), the recommendation + code surface, the Phase-0 `CASE_A` control spec, the leak-freedom gate, and the go/no-go + REPLAN exit. Marked Unknowns 1.2, 1.3, 1.4 → ✅ VERIFIED in `KNOWN_UNKNOWNS.md`. (A scratch `src/` prototype was used to gather evidence and then reverted — the branch is docs-only.)

### Result

**GO with a REPLAN exit.** Root cause pinned precisely: `_compute_index_offset_key`'s greedy first-canonical-match (`stationarity.py:5099`) binds constr's `sp` index to var position 0 (`s`, canon-only) instead of position 2 (`sp`, exact-name) — since `s`/`sp`/`spp` are aliases — so `σ=sp` is expressed as an offset-from-`s`, degenerating into **44 spurious off-diagonal groups** (instrumented: keys `(-7..+7,{-1,0,1},999)`; the sibling `equil` binds correctly to 1 group). A scratch prototype proved the offset-key-only change is insufficient (`ngroups` stayed 45) **and crashes emission** → Part-2 is a *coordinated* offset-key + emission change. **Recommended: Mechanism C** — a targeted additive off-diagonal correction (parallel to the verified Part-1), gated on the `σ=sp` signature, that suppresses the 44 groups and emits `−b·sum(j, pi(s,i,sp,j,sp)·nu_constr(sp,j))` **without touching the shared offset-key matcher** (the cohort-leak surface). Two higher-blast-radius alternatives (A: fix the matcher; B: a bound-to-var-index marker) are documented as fallbacks. The Phase-0 `/tmp` `CASE_A` control (local, seconds-scale on tiny markov) + the golden-staleness leak gate are specified. Landable in the P1 14–20h budget; front-load Days 1–3 with "ship Part-1 + bank Part-2" as the REPLAN exit. Verifies Unknowns 1.2, 1.3, 1.4.

### Verification

```bash
# The design doc exists and names the σ=sp mechanism + the Phase-0 control
test -f docs/planning/EPIC_4/SPRINT_36/MARKOV_OFFDIAGONAL_DESIGN.md && echo "design exists"
grep -qiE "sigma=sp|σ=sp|off-diagonal|CASE_A" docs/planning/EPIC_4/SPRINT_36/MARKOV_OFFDIAGONAL_DESIGN.md && echo "covers σ=sp + CASE_A gate"
# Confirm the cited code surface still exists
grep -nE "_compute_index_offset_key|_add_indexed_jacobian_terms" src/kkt/stationarity.py | head
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_36/MARKOV_OFFDIAGONAL_DESIGN.md` — the Part-2 `σ=sp` enumeration design: the representation-gap characterization, the chosen mechanism (+ 1–2 rejected alternatives), the exact code surface, the Phase-0 `CASE_A` control spec, and the leak-freedom gate
- A go/no-go note on whether Part 2 is landable in the P1 budget (14–20h) or is a documented REPLAN exit
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.2, 1.3, 1.4

### Acceptance Criteria

- [x] The `σ=sp` representation gap is characterized against the exact code path (`_compute_index_offset_key:5099` greedy canon-match; 44-group instrumentation)
- [x] ≥ 2 candidate mechanisms sketched (emitted GAMS + blast radius) — Mechanism C recommended, A/B as fallbacks
- [x] The Phase-0 control that must reach `CASE_A` is specified (`/tmp` hand-edit → `kkt_residual.py` gate, local/seconds-scale)
- [x] The leak-freedom gate (2-D cohort byte-identical) is specified and coordinated with Task 4 (shared `_add_indexed_jacobian_terms`)
- [x] A REPLAN exit is defined (ship Part-1 + bank Part-2 if the control can't reach `CASE_A` or the gate leaks)
- [x] Unknowns 1.2, 1.3, 1.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 4: fawley P3 — Derivative-Structure Discriminator Design

**Status:** ✅ COMPLETE (2026-08-06)
**Priority:** High
**Estimated Time:** 4-6 hours
**Deadline:** Before Sprint 36 Day 1
**Owner:** Sprint 36 execution team
**Dependencies:** Tasks 1, 2, 3
**Unknowns Verified:** 3.1, 3.2

### Objective

Design the **derivative-structure discriminator** that lets the fawley constraint-index-diagonal `sameas` correction fire *without* leaking onto the markov #1110 multi-pattern off-diagonal — the exact leak that forced the S35 Day-9 revert — and specify how it co-exists with the Task-3 markov change in the shared `_add_indexed_jacobian_terms`.

### Why This Matters

The fawley correctness fix is control-verified (`max|stat_bq|` 473→1.14e-13), but the S35 Day-9 general surface-pattern predicate leaked onto markov #1110 (both live in the ~1430-line `_add_indexed_jacobian_terms`). Since Sprint 36 *also* changes that function for markov (Task 3), the fawley discriminator and the markov Part-2 change must be designed together or they will collide. Designing the discriminator in prep — rather than re-discovering the leak on Day 3 — is what turns fawley from a repeat-DEFER into a landable correctness fix.

### Why the shared function makes this a joint design

`_add_indexed_jacobian_terms` (`src/kkt/stationarity.py:5861+`) is the single most-patched emit function, serving the whole 2-D cohort (cesam2/camcge/ps2/ps3/polygon) plus markov (#1110) and fawley (#1111/#1112). A change for one must be leak-proofed against all. Task 3 and Task 4 both touch it in Sprint 36; the discriminator must key on *derivative structure* (per `DAY9_P3_FAWLEY_CONTROL_DEFER.md`), not a surface pattern, precisely so it does not re-fire on markov's off-diagonal.

### Background

`DAY9_P3_FAWLEY_CONTROL_DEFER.md` records: the `/tmp` control drove `max|stat_bq|` 473→1.14e-13; the general `src/` predicate added a wrong `$(sameas(j,i))` to markov's #1110 emit → reverted. `FAWLEY_DIAGONAL_DESIGN.md` has the fixture (`shape_fawley_2d_second_index`). The discriminator must distinguish fawley's constraint-index-diagonal (`cfq=cf`) from markov's off-diagonal — the `_derivative_structure_key` machinery (Task 3 territory) is the natural home for the distinction.

### What Needs to Be Done

1. **Re-read `DAY9_P3_FAWLEY_CONTROL_DEFER.md` + `FAWLEY_DIAGONAL_DESIGN.md`** — the verified control, the leak, and the fixture.
2. **Characterize the leak surface:** why the surface-pattern predicate over-fires on markov #1110 (same surface shape, different derivative structure).
3. **Design the discriminator:** a derivative-structure key (or an extension of `_derivative_structure_key`) that fires the fawley `sameas` guard only when the summed multiplier index is a *constraint* domain index in the variable's stat position, distinct from the markov off-diagonal. Specify the predicate and where it sits relative to the Task-3 markov change.
4. **Prove co-existence with Task 3:** show the fawley discriminator and the markov Part-2 change do not overlap (different branches / keys), and that the combined change leaves the 2-D cohort byte-identical.
5. **Specify the Phase-0 control:** the `/tmp` hand-edit driving `max|stat_bq| → 0`, and the golden-staleness gate (only fawley drifts; markov + cohort byte-identical).
6. **Note the H-b +Solve hand-off:** the fawley correctness fix is 0-bucket on its own (H-b, MS-5 @ 4399.557); the +Solve is the `--force` survey — cross-reference Task 8 / `CONSULTATION_BUNDLE.md` §3.

### Changes

Created `docs/planning/EPIC_4/SPRINT_36/FAWLEY_DISCRIMINATOR_DESIGN.md` — the derivative-structure discriminator design, the joint markov/fawley change-surface map, the Phase-0 `max|stat_bq|→0` control, the leak-freedom gate, the +Solve hand-off, and the go/no-go. Marked Unknowns 3.1, 3.2 → ✅ VERIFIED in `KNOWN_UNKNOWNS.md`. (Evidence gathered from the committed goldens — no `src/` change.)

### Result

**GO with a REPLAN exit.** The S35 Day-9 *surface-pattern* predicate leaked onto markov because it checked the *positional orientation* (a constraint index in the variable's stat position) but not whether the derivative depends on that index. The **derivative-structure discriminator** fixes this: **fire the `$(sameas(cfq__,cf))` guard only when the summed constraint index is ABSENT from the derivative coefficient** (present only in the multiplier + domain guards). Confirmed from both goldens — fawley's qsb/pbal coefficients (`prop·char·bposs`) lack `cfq__` (pure over-count → guard corrects it); markov's off-diagonal coefficient contains the summed index via `pi` (genuine sum → no guard). **Co-existence with the Task-3 markov change (Unknown 3.2):** disjoint firing conditions — markov's terms all carry the summed index in the coefficient and/or an additive `Const`; fawley's carry neither, so the `summed-index-in-coefficient` test alone partitions them (the fawley discriminator never fires on markov; the markov mechanisms never fire on fawley). Both are additive gated branches; neither touches the shared `_compute_index_offset_key`. The Phase-0 `max|stat_bq|→0` control + the golden-staleness leak gate + the `shape_fawley_2d_second_index` fixture are specified. fawley is **H-b** (Task 2 re-confirmed) → the +1 floor is cold-match-contingent (expected 0 in-sprint bucket); the +Solve is the Task-8 `--force` survey. Verifies Unknowns 3.1, 3.2.

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_36/FAWLEY_DISCRIMINATOR_DESIGN.md && echo "design exists"
grep -qiE "derivative-structure|discriminator|_derivative_structure_key|leak" docs/planning/EPIC_4/SPRINT_36/FAWLEY_DISCRIMINATOR_DESIGN.md && echo "covers discriminator + leak"
# Confirm the shared function + the fawley fixture reference still exist
grep -nE "_derivative_structure_key|_add_indexed_jacobian_terms" src/kkt/stationarity.py | head
grep -rnE "shape_fawley_2d_second_index|fawley" docs/planning/EPIC_4/SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md | head
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_36/FAWLEY_DISCRIMINATOR_DESIGN.md` — the derivative-structure discriminator design, its co-existence proof with the Task-3 markov change, the Phase-0 `max|stat_bq|→0` control, and the leak-freedom (2-D-cohort byte-identical) gate
- A joint markov/fawley change-surface map for `_add_indexed_jacobian_terms` (which branches each touches)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.2

### Acceptance Criteria

- [x] The markov #1110 leak surface is characterized (the surface predicate checked position, not derivative-dependence)
- [x] A derivative-structure discriminator is specified (summed-index-absent-from-coefficient; `_collect_free_indices` on the coefficient in `_add_indexed_jacobian_terms`)
- [x] Co-existence with the Task-3 markov change is demonstrated (disjoint firing conditions via the joint change-surface map; neither touches the shared matcher)
- [x] The Phase-0 `max|stat_bq|→0` control + the golden-staleness gate are specified
- [x] The H-b +Solve hand-off to the `--force` survey (Task 8) is cross-referenced
- [x] Unknowns 3.1, 3.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 5: sarf P2 — Symbolic-Emit Subsystem Design Refresh & Blow-Up Re-Measurement

**Status:** ✅ COMPLETE (2026-08-07)
**Priority:** High
**Estimated Time:** 4-5 hours
**Deadline:** Before Sprint 36 Day 1
**Owner:** Sprint 36 execution team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 2.1, 2.2, 2.3, 2.4

### Objective

Refresh the banked sarf symbolic-emit design against the current `main`, re-measure the 369K-column blow-up, and confirm the O(active=398) guarded-emit approach and its Phase-0 timing gate are still valid — so Sprint 36's largest single track (20–28h) starts with a verified spec.

### Why This Matters

sarf is the thrice-carried, highest-budget track (a corpus-wide re-architecture of `enumerate_variable_instances`), and its lower-leverage payoff (+1 Translate) makes a mid-sprint re-scope expensive. Re-measuring the blow-up and re-validating the O(active) approach in prep ensures the sprint doesn't burn 20+ hours re-establishing the baseline the S35 design already recorded.

### Background

`SARF_SYMBOLIC_EMIT_DESIGN.md` + `PHASE_0_ACCEPTANCE_GATES.md` (Sprint 35) specify: the blow-up is `enumerate_variable_instances` materializing 369,024 `task` columns (foundational — the `col_to_var` index the whole flow iterates for all 142 models); the active subset (`taskposs ∧ tech` = 398) is not statically enumerable (`taskposs` runtime-computed); the fix emits one guarded `stat_task(g,t,m,n)$taskposs` + `task.fx(...)$(not (...)) = 0`. The Phase-0 gate is O(active=398), not O(369K) — timed `sarf_mcp.gms` in single-digit seconds (baseline >303s, non-terminating), atomic S1/S2/S3, byte-stable golden, determinism ×3, no set-name-literal indices.

### What Needs to Be Done

1. **Re-read `SARF_SYMBOLIC_EMIT_DESIGN.md` + `PHASE_0_ACCEPTANCE_GATES.md`.**
2. **Re-measure the blow-up on current `main`:** attempt a sarf emit under a time cap and confirm it is still >303s / non-terminating (the O(369K) failure). Record the measured wall-clock at the cap.
3. **Re-validate the 7-term `stat_task` derivation** against `sarf.gms` (the banked derivation) — confirm no source drift.
4. **Confirm the O(active) guarded-emit shape** (`stat_task(g,t,m,n)$taskposs` + `task.fx` guard) is still the target; note any parser/emitter changes since S35 that affect it.
5. **Re-confirm the Phase-0 timing gate + the regression harness** (full-corpus `--resolve-changed`, byte-stable golden, determinism ×3, no set-name-literal indices).
6. **Flag the re-scope exit:** the condition under which the parametric emit re-triggers the timeout → documented re-scoping (per the deliverable).

### Changes

Created `docs/planning/EPIC_4/SPRINT_36/SARF_DESIGN_REFRESH.md` — the re-measured blow-up, the re-validated 7-term derivation, the O(active) guarded-emit GAMS-54 confirmation, the Phase-0 gate + regression harness, and the go/no-go. Marked Unknowns 2.1, 2.2, 2.3, 2.4 → ✅ VERIFIED in `KNOWN_UNKNOWNS.md`.

### Result

**GO — the S35 banked design applies UNCHANGED.** Every premise re-confirms on current `main`: (2.1) the sarf emit is **still >303s / non-terminating** (measured at a 330s cap — the O(369K) failure, identical to the S35 baseline); counts re-verified (16·24·31·31 = **369,024** declared / **398** active); the 3 sites' code surfaces (`constraint_jacobian.py`, `index_mapping.py`, `stationarity.py`) **byte-unchanged since the anchor**. (2.2) the O(active) guarded-emit shape **compiles clean under GAMS 54.2.1** and GAMS natively prunes the instantiation (synthetic `ncart=54` vs `ndomain=18` vs `nactive=4`) — O(active), not O(Cartesian). (2.3) the 7-term derivation's constraint bodies (tbal/labor/equipb1/equipb2/acost3/task.lo) are all present + structurally unchanged, own-domain multipliers (no set-name-literals). (2.4) no set-name-literal indices by design; the determinism ×3 + byte-stable-golden harness is the landing gate. **Disposition unchanged:** a 20–28h atomic, foundational re-architecture for +1 Translate (the 4×-failed path), not landable without the full-corpus regression harness; the standing REPLAN triggers hold. Schedule it early so a REPLAN surfaces before Day 12. Verifies Unknowns 2.1, 2.2, 2.3, 2.4.

### Verification

```bash
# The banked design docs exist
ls docs/planning/EPIC_4/SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md docs/planning/EPIC_4/SPRINT_35/PHASE_0_ACCEPTANCE_GATES.md
# The refresh note exists and records a re-measured blow-up + the O(active) gate
test -f docs/planning/EPIC_4/SPRINT_36/SARF_DESIGN_REFRESH.md && echo "refresh exists"
grep -qiE "369|O\(active|398|taskposs|>303s" docs/planning/EPIC_4/SPRINT_36/SARF_DESIGN_REFRESH.md && echo "covers blow-up + O(active)"
# The enumerate_variable_instances surface still exists
grep -rn "enumerate_variable_instances" src/ | head
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_36/SARF_DESIGN_REFRESH.md` — a refresh note: the re-measured blow-up (wall-clock at the cap), the re-validated 7-term `stat_task` derivation, the confirmed O(active=398) guarded-emit target, and the Phase-0 timing gate + regression harness
- A go/no-go on whether the S35 design applies unchanged or needs an update for any `main` drift
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.1, 2.2, 2.3, 2.4

### Acceptance Criteria

- [x] The 369K blow-up re-measured on current `main` (>303s / non-terminating confirmed at a 330s cap)
- [x] The 7-term `stat_task` derivation re-validated against `sarf.gms` (all 7 constraint bodies present + structurally unchanged)
- [x] The O(active=398) guarded-emit shape confirmed as the target (compiles + instantiates O(active) under GAMS 54.2.1)
- [x] The Phase-0 timing gate + regression harness (byte-stable golden, determinism ×3, no set-name-literal indices) re-confirmed
- [x] The re-scope exit condition documented (the standing REPLAN triggers)
- [x] Unknowns 2.1, 2.2, 2.3, 2.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 6: ganges/gangesx P4 — ≥5-Blocker Cascade Re-Verification & Recovery Sequencing

**Status:** ✅ COMPLETE (2026-08-07)
**Priority:** High
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 36 Day 1
**Owner:** Sprint 36 execution team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 4.1, 4.2, 4.3, 4.4, 4.5, 6.3

### Objective

Re-verify the ganges/gangesx ≥5-blocker cascade on current `main`, confirm the banked `$149` `_diff_prod` fix still applies cleanly, and sequence the recovery (`$141` → `$145` → `$149` → `$66` → `rPower`) — including the slow-CGE-golden regeneration budget — so P4 starts Day 1 with an ordered, verified plan.

### Why This Matters

ganges/gangesx is the largest potential bucket move (+2 Solve/Match/floor if both cold-match) but also the deepest cascade — no model recovers from any single fix. A recovery that isn't sequenced (and whose banked `$149` fix isn't re-verified) risks burning the 16–22h P4 budget on the wrong blocker order or on a fix that no longer applies. The `$149` fix also unblocks the `$149` half of dinam/indus/turkpow/clearlak (P6), so verifying it has cross-track value.

### Background

`DAY3_P4_BANK_CARRYFORWARD.md` + `GANGES_RECOVERY_DESIGN.md` + `GANGES_149_PRODUCT_RULE_ANALYSIS.md` record the cascade: `$141` (NaN-cleanup self-referential guard over `.l`-calibration params — **use the existing `_expr_contains_varref_attribute`**, not the buggy proposed `_expr_contains_varref_attr`, a PR-review catch) / `$145` (universal-set `*`-domain NaN-cleanup gap) / `$149` (the `_diff_prod` cross-index CES/LES product-rule fix — verified, ganges `$149` 9→0, lmp2/camcge byte-identical) → `$66` (cold, presolve-gated `.l`-calibration params unassigned-but-referenced-in-stationarity) → `rPower` (presolve `$onMultiR` re-runs `ganges0`, aborts `x**y, x=0, y<0`; raw ganges NLP solves fine standalone MS2). The slow CGE goldens are regenerable in a nightly/dedicated budget.

### What Needs to Be Done

1. **Re-read the three banked docs.**
2. **Re-verify the `$149` `_diff_prod` fix location** (`src/ad/derivative_rules.py`, the `_diff_prod` collapse branch) is unchanged on `main` and the banked patch still applies.
3. **Confirm the `$141` helper correction:** the plan uses the existing `_expr_contains_varref_attribute` (`original_symbols.py`), not the buggy `_expr_contains_varref_attr`.
4. **Re-confirm the cascade order and terminal blockers** (`$66` cold, `rPower` presolve) — verify the `$66`/`rPower` characterization still holds (do a scratch compile of ganges after the banked `$141`/`$145`/`$149` are notionally applied, if feasible within the emit budget).
5. **Estimate the slow-golden regeneration cost** and identify the budget slot (nightly / dedicated day).
6. **Sequence the recovery** as an ordered Day-plan with a `--resolve-changed` gate after each fix.

### Changes

Created `docs/planning/EPIC_4/SPRINT_36/GANGES_RECOVERY_SEQUENCING.md` — the re-verified cascade, the confirmed `$149`/`$141` fix surfaces, the ordered recovery plan with per-fix `--resolve-changed` gates, the slow-golden regen budget, and the cross-track `$149`-unblock + residual-cohort notes. Marked Unknowns 4.1, 4.2, 4.3, 4.4, 4.5, 6.3 → ✅ VERIFIED in `KNOWN_UNKNOWNS.md`.

### Result

**GO — the cascade + fix surfaces re-confirm; disposition unchanged.** (4.1) `derivative_rules.py` byte-unchanged since the anchor → the banked `$149` `_diff_prod` §5 patch applies (`_diff_prod` at `:3276`). (4.2) the correct `$141` helper `_expr_contains_varref_attribute` is present (`:1392`); the buggy variant absent; the Day-1 `$141`/`$145` patches are in git at `a8ff626c`. (4.3) emitting ganges (**335s**) + compiling the cold MCP under GAMS 54.2.1 reproduces the documented cascade starting point (`$141`×15, `$145`, `$149`, `$257`); the `$66` (cold, unassigned calibration params) + `rPower` (presolve `$onMultiR` embedded-NLP `x**y,x=0,y<0`) terminals are structural to the byte-stable `ganges.gms` + emit code; the pipeline seal (presolve retry only on cold STATUS-5) means both the cold `$66` and presolve `rPower` paths must be solved. (4.4) the ganges emit is 335s → the slow-golden regen needs a **nightly/dedicated slot** (~35 min for both + determinism ×3), affordable in a dedicated effort. (4.5) the general `$149` fix unblocks the `$149` half of dinam/indus/turkpow/clearlak (necessary-not-sufficient — other roots remain). (6.3) the residual cohort roots (turkpow ragged-Table / clearlak dynamic-sets / dinam-indus `$140`+`$149`) hold; all still `path_syntax_error`. **Disposition unchanged:** a ≥5-blocker dedicated deep effort (16–22h); +2 Solve/Match/floor if both paths land, else 0 (the P4-flat branch); schedule so the `rPower` deep blocker surfaces early. Verifies Unknowns 4.1, 4.2, 4.3, 4.4, 4.5, 6.3.

### Verification

```bash
# The banked docs exist
ls docs/planning/EPIC_4/SPRINT_35/DAY3_P4_BANK_CARRYFORWARD.md docs/planning/EPIC_4/SPRINT_35/GANGES_RECOVERY_DESIGN.md docs/planning/EPIC_4/SPRINT_35/GANGES_149_PRODUCT_RULE_ANALYSIS.md
# The recovery-sequencing note exists
test -f docs/planning/EPIC_4/SPRINT_36/GANGES_RECOVERY_SEQUENCING.md && echo "sequencing exists"
grep -qiE "\\\$141|\\\$145|\\\$149|\\\$66|rPower|_diff_prod|_expr_contains_varref_attribute" docs/planning/EPIC_4/SPRINT_36/GANGES_RECOVERY_SEQUENCING.md && echo "covers cascade"
# The $149 fix surface + the correct $141 helper still exist
grep -n "_diff_prod" src/ad/derivative_rules.py | head
grep -rn "_expr_contains_varref_attribute" src/ | head
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_36/GANGES_RECOVERY_SEQUENCING.md` — the re-verified cascade, the confirmed `$149`/`$141` fix surfaces, the ordered recovery plan with per-fix `--resolve-changed` gates, and the slow-golden regeneration budget slot
- A cross-note to P6: the `$149` fix's unblocking of dinam/indus/turkpow/clearlak's `$149` half
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.2, 4.3, 4.4, 4.5, 6.3

### Acceptance Criteria

- [x] The `$149` `_diff_prod` fix location is unchanged on `main` and the banked patch still applies (`derivative_rules.py` byte-unchanged; `_diff_prod:3276`)
- [x] The `$141` helper plan uses the existing `_expr_contains_varref_attribute` (`:1392`; the buggy variant absent)
- [x] The cascade order + terminal blockers (`$66` cold, `rPower` presolve) re-confirmed (cold-MCP compile `$141`×15/`$145`/`$149`/`$257`; terminals structural)
- [x] The slow-CGE-golden regeneration cost estimated with a budget slot (335s ganges emit → nightly/dedicated slot)
- [x] An ordered recovery plan with per-fix `--resolve-changed` gates is produced
- [x] The P6 cross-track `$149`-unblock is noted (dinam/indus/turkpow/clearlak)
- [x] Unknowns 4.1, 4.2, 4.3, 4.4, 4.5, 6.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 7: GAMS-54 Licensed-Testbed Re-Baseline Harness Plan (P7 + turkey P6)

**Status:** ✅ COMPLETE (2026-08-07)
**Priority:** Medium
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 36 Day 1
**Owner:** Sprint 36 execution team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 6.1, 6.2, 7.1, 7.2

### Objective

Plan the licensed-testbed harness for the GAMS-54 corpus re-baseline (the v53→v54 transition's first infra task) and turkey's >1000-row solve — the two Sprint-36 items that cannot run on the local 1000-row demo license — so the sprint knows Day 0 what testbed access it needs and what the re-baseline will diff.

### Why This Matters

The 108/93/75 baseline was built under GAMS 53; CI + local now validate under 54.2.1. Two Sprint-36 outcomes (the turkey +1 and the corpus re-baseline decision) are *testbed-gated* — a licensed GAMS-54 that can solve >1000-row MCPs. If the testbed availability isn't confirmed and the re-baseline scope isn't planned in prep, P6/P7 stall on infrastructure mid-sprint. The emit-level gates (determinism / `--resolve-changed` / golden-staleness) are version-independent and stay local; only the *solve* buckets carry the v53→v54 risk.

### Background

`FOLLOWUPS_GAMS54_TRANSITION.md` records: GAMS 53's demo license expired ~2026-07-29; CI/local bumped to 54.2.1; GAMS 54 is stricter (robustlp NA rejected → allowlisted; 5 OBJ-GAPs: agreste/cesam/chain/fawley/rocket). `DAY13_RETEST_STAGING.md` §3 + `SPRINT_36_CARRYFORWARDS.md` §10 record the decision framing: report the v53 KPIs as the S35 baseline, open the v54 re-baseline as the first Sprint-36 infra task. turkey's MCP is 3,866 rows (`DAY6_P6_TURKEY_AND_TESTFIX.md`); its `path_syntax_error → path_solve_license` shift confirms the compile-recovery is real and the solve is demo-limit-gated.

### What Needs to Be Done

1. **Confirm testbed access:** identify the licensed GAMS-54 environment (CI runner / dedicated machine) that can solve >1000-row MCPs; document how to invoke it.
2. **Scope the re-baseline diff:** the corpus re-solve under v54 vs the v53-built DB — which buckets to diff, the 5 OBJ-GAP models to re-check, the PR19 Tier-0/1 canary confirmation.
3. **Plan the turkey solve:** the specific `run_full_test.py` / testbed invocation to solve turkey's 3,866-row MCP and record the bucket.
4. **Specify the decision output:** pin the DB to v54 (re-baseline) vs keep v53 where a license solves — the criteria and the artifact.
5. **Confirm the emit-level gates stay local** (version-independent) and need no testbed.
6. **Identify the Day-slot** for the testbed run (it may be nightly / async, feeding Day-10 checkpoint or Day-13 close).

### Changes

- Created `docs/planning/EPIC_4/SPRINT_36/GAMS54_TESTBED_PLAN.md` — the license probe (local + both CI workflows), the bounded Day-0 risk, the demo-runnable re-baseline scope, the turkey solve invocation, the DB-version decision + criteria, the local-vs-testbed checklist (§5), and the async Day-slot (§6).
- Probed the GAMS license on `main`: local `Versions/54/Resources/gamslice.txt` = **`GAMS Demo`** (54.2.1, 1000-row limit, stops Nov 26 2026); **both** CI workflows (`pr19-emit-solve-validation.yml`, `presolve-divergence.yml`) run "Install GAMS demo" (54.2.1) → **no licensed >1000-row testbed exists.**
- Established the load-bearing bound: DB `gams_version` = `51.3.0` (demo) → the whole Solve/Match baseline is demo-built → the v54 re-baseline of the solving set is demo-runnable; only turkey (3,866 rows) is license-gated.
- Confirmed the 5 OBJ-GAP models are demo-solvable (tiny; all produced DB results) → their v54 bucket re-check is demo-runnable, not license-gated.
- Set KNOWN_UNKNOWNS.md 6.1 → ❌ WRONG (bounded Day-0 risk), 6.2 → 🔍 BLOCKED (license-gated, deferred), 7.1 → ✅ VERIFIED (demo-runnable re-check), 7.2 → ✅ VERIFIED (keep-v53 decision made).

### Result

**GO with a bounded Day-0 risk.** No licensed >1000-row GAMS-54 testbed exists (6.1 wrong) — but because the KPI baseline is demo-built, the v54 corpus re-baseline + the 5 OBJ-GAP bucket re-check + the v53-vs-v54 version decision are **all demo-runnable in-sprint** (7.1/7.2 resolved on the demo, no new infra). Only turkey's +1 is license-gated (6.2 blocked/deferred — a pre-existing S35 carryforward). **Decision: keep the v53(51.3.0)-built KPIs (108/93/75) as the S36 baseline; open the v54 re-baseline as an async infra slot before Day-10; re-pin to v54 only on confirmed zero bucket regressions.** No `*.py` changed → quality gate N/A.

### Verification

```bash
# The follow-ups + staging docs exist
ls docs/planning/EPIC_4/SPRINT_35/FOLLOWUPS_GAMS54_TRANSITION.md docs/planning/EPIC_4/SPRINT_35/DAY13_RETEST_STAGING.md
# The testbed-harness plan exists
test -f docs/planning/EPIC_4/SPRINT_36/GAMS54_TESTBED_PLAN.md && echo "testbed plan exists"
grep -qiE "1000-row|testbed|re-baseline|turkey|OBJ-GAP|54.2.1" docs/planning/EPIC_4/SPRINT_36/GAMS54_TESTBED_PLAN.md && echo "covers testbed scope"
# The GAMS resolver + row-limit handling still present
grep -rnE "path_solve_license|find_gams_executable|Versions/Current" scripts/ src/ | head
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_36/GAMS54_TESTBED_PLAN.md` — the testbed access confirmation, the re-baseline diff scope (buckets + 5 OBJ-GAP models + PR19 canaries), the turkey solve invocation, the DB-version decision criteria, and the Day-slot for the async testbed run
- A checklist of what stays local (emit-level gates) vs what needs the testbed (solve buckets)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 6.1, 6.2, 7.1, 7.2

### Acceptance Criteria

- [x] A licensed GAMS-54 testbed capable of >1000-row solves is identified (or its absence flagged as a Day-0 risk) — **absence flagged**: local + both CI are demo (1000-row); no licensed testbed. Bounded (§1)
- [x] The re-baseline diff scope is specified (buckets, 5 OBJ-GAP models, PR19 canaries) — §2, demo-runnable
- [x] The turkey solve invocation is specified — §3, license-gated/deferred
- [x] The DB-version decision criteria + artifact are defined — §4 (keep-v53; `GAMS54_REBASELINE_DIFF.md`)
- [x] The emit-level (local) vs solve (testbed) split is documented — §5 checklist
- [x] The testbed Day-slot is identified — §6 (async, before Day-10; turkey gated on license, not calendar)
- [x] Unknowns 6.1, 6.2, 7.1, 7.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 8: Consultation Bundle Finalization (rocket/mine P5) + camcge Epic-5 Gate Scoping

**Status:** ✅ COMPLETE (2026-08-07)
**Priority:** Medium
**Estimated Time:** 2-3 hours
**Deadline:** Before Sprint 36 Day 1
**Owner:** Sprint 36 execution team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 5.1, 5.2, 5.3, 5.4

### Objective

Confirm the rocket PATH-consultation input is submission-ready, finalize the mine primal-degenerate-LP question, and scope the camcge Walras Epic-5 `/tmp` control gate — so P5 (the consultation trio + the Epic-5 hand-off) is a bounded submission/scoping day, not an open research task.

### Why This Matters

P5 is not an emit-fix track — rocket and mine are *consultation submissions* (the emit is correct; the blocker is a solver/reformulation question), and camcge is Epic-5 research. Their value is a clean, precise hand-off. If the rocket input isn't verified submission-ready or the camcge Epic-5 gate isn't scoped, P5 slips into re-authoring instead of submitting.

### Background

`CONSULTATION_BUNDLE.md` (Sprint 36) bundles the three: §1 rocket (PATH consult; the FINALIZED input renumbered S33→S36 ×11, authoring preserved; feeds the Sprint-37 consultation); §2 mine (primal-degenerate-LP question; value-invariant, LP-side reformulation only; `x.up=inf` BANNED); §3 fawley (the H-b `--force` survey — cross-references Task 4). `DAY8_P5_CAMCGE_SPRINT36.md` records the camcge Epic-5 deferral: the S1∧S2∧S3 detector fires only camcge (cold MS-4 @ omega 191.7346); the price-pin variant reaches the correct primal but stays MS-4; MS-1 is the Epic-5 gate. The Case-c sign flip stays BANNED.

### What Needs to Be Done

1. **Re-read `CONSULTATION_BUNDLE.md` §1–§3 + `DAY8_P5_CAMCGE_SPRINT36.md` + `MINE_DUAL_ARCHITECTURE_DESIGN.md`.**
2. **Verify the rocket input is submission-ready:** the concrete question + the ruled-out-lever survey + the reproducible case + the `--force` scaffold reference are all present and renumbered.
3. **Finalize the mine question:** confirm the primal-degenerate-LP framing is precise and the value-invariance finding (S34) + the `x.up=inf` BAN are stated.
4. **Scope the camcge Epic-5 gate:** the `/tmp` control that would prototype the full dual-consistent Walras redefinition to MS-1; note the price-pin fallback (correct primal, MS-4).
5. **Cross-reference the fawley `--force` survey** (§3 / Task 4) so the H-b +Solve hand-off is coherent.
6. **Note the consultation is a submission** (feeds the Sprint-37 consultation sprint) — no emit fix expected in P5.

### Changes

- Created `docs/planning/EPIC_4/SPRINT_36/P5_CONSULTATION_FINALIZATION.md` — rocket submission-readiness (§1), the finalized mine question (§2), the camcge Epic-5 `/tmp` Walras gate scope (§3), the fawley `--force` cross-reference (§4), and the P5-is-a-submission-day note (§5).
- Dispatched an Explore agent to digest `../SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`, `../SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md`, `../SPRINT_35/DAY8_P5_CAMCGE_SPRINT36.md` — confirmed rocket's 4 components + renumber ×11, mine's framing + S34 value-invariance + `x.up=inf` BAN.
- Re-confirmed the camcge S1∧S2∧S3 detector cohort from the byte-unchanged DB (camcge MS-4 @ omega 191.7346; irscge/lrgcge/moncge/stdcge MS-1 match).
- **Measured the camcge MCP generated size:** 641 single (scalar) equations / 641 single variables under GAMS 54.2.1 demo (listing `BLOCKS OF EQUATIONS 85 / SINGLE EQUATIONS 641`; the demo limit is on the generated single count, not blocks+singles), solves MS-4 — **< the 1000-row demo limit**, correcting `DAY8`'s stale "exceeds the demo limit" claim → the Walras `/tmp` gate is a local demo step, not testbed-gated.
- Set KNOWN_UNKNOWNS.md 5.1/5.2/5.4 → ✅ VERIFIED, 5.3 → ✅ VERIFIED (with the `DAY8` correction).

### Result

**GO — P5 is a bounded submission/scoping day, no `src/`.** rocket is submission-ready (all four components, renumbered S33→S36 ×11, FINALIZED, reproducer live at `src/cli.py:207`); the mine primal-degenerate-LP question is precise + guarded (S34 value-invariance + `x.up=inf` BAN); the camcge detector fires only on camcge (DB-confirmed); and — correcting `DAY8` — the camcge Walras `/tmp` MS-1 gate is **locally demo-reachable** (641-row MCP < the 1000-row limit), not a licensed-testbed step. P5's product is submissions (rocket → PATH authors, mine → LP-degeneracy question) + a scoping decision (camcge Epic-5 gate, fawley `--force` survey), feeding the Sprint-37 consultation. No `*.py` changed → quality gate N/A.

### Verification

```bash
# The bundle + camcge + mine docs exist
ls docs/planning/EPIC_4/SPRINT_36/CONSULTATION_BUNDLE.md docs/planning/EPIC_4/SPRINT_35/DAY8_P5_CAMCGE_SPRINT36.md docs/planning/EPIC_4/SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md
# The P5 finalization note exists
test -f docs/planning/EPIC_4/SPRINT_36/P5_CONSULTATION_FINALIZATION.md && echo "P5 note exists"
grep -qiE "rocket|mine|camcge|Epic 5|primal-degenerate|Walras" docs/planning/EPIC_4/SPRINT_36/P5_CONSULTATION_FINALIZATION.md && echo "covers the trio + Epic-5 gate"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_36/P5_CONSULTATION_FINALIZATION.md` — a submission-readiness confirmation for rocket, the finalized mine primal-degenerate-LP question, the camcge Epic-5 `/tmp` gate scope, and the cross-reference to the fawley `--force` survey
- A note confirming P5 is a submission/scoping day (no emit fix), feeding the Sprint-37 consultation
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.1, 5.2, 5.3, 5.4

### Acceptance Criteria

- [x] The rocket consultation input is confirmed submission-ready (question + ruled-out survey + reproducer + `--force` scaffold) — §1, all four present + renumbered ×11
- [x] The mine primal-degenerate-LP question is finalized (value-invariance + `x.up=inf` BAN stated) — §2
- [x] The camcge Walras Epic-5 `/tmp` gate is scoped (with the price-pin MS-4 fallback) — §3; **locally demo-reachable** (641-row MCP), correcting `DAY8`
- [x] The fawley `--force` survey cross-reference (Task 4) is coherent — §4 (disjoint-from-markov per `FAWLEY_DISCRIMINATOR_DESIGN.md`)
- [x] The Case-c sign flip + `x.up=inf` BANs are restated — §2, §6 (bundle carries the Case-c BAN)
- [x] Unknowns 5.1, 5.2, 5.3, 5.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 9: Property-Fixture & 2-D-Cohort Regression-Harness Catalog + robustlp NA Survey

**Status:** ✅ COMPLETE (2026-08-07)
**Priority:** Medium
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 36 Day 1
**Owner:** Sprint 36 execution team
**Dependencies:** Tasks 1, 3, 4
**Unknowns Verified:** 1.3, 1.5, 7.3, 7.4, 7.5

### Objective

Catalog the property fixtures Sprint 36 will add (the markov diagonal-Kronecker fixture, the fawley 2-D second-index fixture), specify the 2-D-cohort golden-staleness regression harness that guards the shared `_add_indexed_jacobian_terms` changes, decide the markov `slow`-test disposition, and survey the robustlp NA-coefficient root term.

### Why This Matters

The markov (Task 3) and fawley (Task 4) fixes both touch the high-blast-radius `_add_indexed_jacobian_terms`; they need fail-before/pass-after fixtures *and* a cohort regression harness so the leak-freedom gate is mechanical, not ad-hoc. Cataloguing these in prep (against the Task-3/Task-4 designs) means Day-1 lands the fix *with* its guard. The robustlp NA survey and the markov `slow`-test disposition are the remaining P7 infra items.

### Background

Sprint-35 P7 established that the sole `src/` landing (turkey) already carries its 3 fail-before/pass-after unit tests; Sprint 36 adds fixtures for the *landed* deep tracks. `DAY11_MARKOV_DIAGONAL_LEVER.md` §5 requires the markov `slow` test `test_markov_stationarity_has_correction_term` to flip red→green with the fix (its `slow`/`xfail` disposition decided then). `FAWLEY_DIAGONAL_DESIGN.md` §6 specifies `shape_fawley_2d_second_index`. `FOLLOWUPS_GAMS54_TRANSITION.md` Follow-up 1 records robustlp's NA matrix coeffs (#1322 class) — allowlisted, needing a real emit fix to de-allowlist. The 2-D cohort is cesam2/camcge/ps2_f_s/ps2_s/ps3_s_gic/polygon.

### What Needs to Be Done

1. **Catalog the fixtures to add:** the markov diagonal-Kronecker fixture (fail-before/pass-after, gated on Task-3's Part-1/Part-2 landing) and the fawley `shape_fawley_2d_second_index` fixture (gated on Task-4). Specify each fixture's assertion + skip-if-absent pattern.
2. **Specify the 2-D-cohort regression harness:** the golden-staleness check that confirms cesam2/camcge/ps2/ps3/polygon are byte-identical after the markov + fawley changes (the leak-freedom gate).
3. **Decide the markov `slow`-test disposition:** with the Task-3 fix, does the test flip green (un-mark `slow` / keep as a fast unit shape guard)? Record the decision.
4. **Survey the robustlp NA root:** trace which emitted term goes NA under GAMS 54 (#1322 family); scope the emit fix and the de-allowlist step.
5. **Note the genuine-floor tracking recompute** (S36 anchor 75 → ≥76 if markov/fawley/ganges cold-match) + the Epic-4 `SUMMARY.md` row-36 groundwork.

### Changes

- Created `docs/planning/EPIC_4/SPRINT_36/FIXTURE_AND_HARNESS_CATALOG.md` — the two per-fix fixture specs (§1), the shared 2-D-cohort golden-staleness harness (§2), the markov `slow`-test disposition (§3), the robustlp NA root survey + de-allowlist plan (§4), and the genuine-floor recompute + SUMMARY row-36 groundwork (§5).
- **Reproduced robustlp EXECERROR-84 live** (GAMS 54.2.1 demo) → **corrected the allowlist's root**: the NA is in the multiplier `.L` warm-start levels (`lam_socpqcpcons(1..7)`, `piL_y(1..7)` = NA; finite Matrix range), NOT the Jacobian coefficients; `emit_post_assignment_na_cleanup` misses it (indexed-param-division-only) → bounded fix in the presolve marginal-transfer emit + de-allowlist.
- **Measured markov emit = 12.4 s** (subprocess) → disposition: add the fast in-process `shape_markov_diagonal_kronecker` fixture (primary `make test` guard) + flip & sharpen the integration test to the `σ=sp` target, kept `slow`.
- Confirmed all six cohort goldens present; the shared gate is the existing `check_golden_staleness.py --models …`.
- Recomputed the floor partition from the byte-unchanged DB (108 / 93 = 63+30; markov ∈ methodology → the +1 is real; anchor 75).
- Set KNOWN_UNKNOWNS.md 1.5/7.3/7.4/7.5 → ✅ VERIFIED, added a Task-9 addendum to the already-VERIFIED 1.3.

### Result

**GO — the fixture/harness scaffolding + the robustlp fix are catalogued and bounded.** Two per-fix fixtures map 1:1 to the Task-3/Task-4 landings; the shared cohort golden-staleness harness is the mechanical leak backstop (leak-free by design, Day-1 gate); the markov `slow`-test disposition closes the silent-regression window with a fast in-process fixture; the **robustlp NA root is reproduced + corrected (NA multiplier `.L` level, not a Jacobian coefficient) + the de-allowlist fix bounded**; the genuine-floor anchor holds at 75 with markov the tracked +1. No `*.py` changed (the fixtures/fix land in execution) → quality gate N/A.

### Verification

```bash
# The fixture/harness catalog exists
test -f docs/planning/EPIC_4/SPRINT_36/FIXTURE_AND_HARNESS_CATALOG.md && echo "catalog exists"
grep -qiE "markov|fawley|2-D cohort|golden-staleness|robustlp|slow-test|xfail" docs/planning/EPIC_4/SPRINT_36/FIXTURE_AND_HARNESS_CATALOG.md && echo "covers fixtures + harness + robustlp"
# The markov slow-test + the robustlp allowlist still exist
grep -rn "test_markov_stationarity_has_correction_term" tests/ | head
grep -rn "robustlp" scripts/diagnostics/presolve_divergence_allowlist.txt
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_36/FIXTURE_AND_HARNESS_CATALOG.md` — the markov + fawley fixture specs (assertion + skip-if-absent), the 2-D-cohort golden-staleness regression harness, the markov `slow`-test disposition decision, the robustlp NA root survey + de-allowlist plan, and the genuine-floor tracking recompute note
- A mapping of each fixture to the Task-3/Task-4 landing it guards
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.3, 1.5, 7.3, 7.4, 7.5

### Acceptance Criteria

- [x] The markov diagonal-Kronecker fixture is specified (fail-before/pass-after, skip-if-absent) — §1 `shape_markov_diagonal_kronecker`
- [x] The fawley `shape_fawley_2d_second_index` fixture is specified — §1 (guards Task 4, disjoint from markov)
- [x] The 2-D-cohort golden-staleness regression harness (leak-freedom gate) is specified — §2 `check_golden_staleness.py --models …`
- [x] The markov `slow`-test disposition is decided (with the Task-3 fix) — §3 (fast fixture primary + sharpened green integration test, kept slow)
- [x] The robustlp NA root is surveyed with a de-allowlist plan — §4; **corrected**: NA multiplier `.L` level (not a Jacobian coefficient); bounded presolve-emit fix + de-allowlist
- [x] The genuine-floor tracking recompute (anchor 75) + SUMMARY row-36 groundwork are noted — §5 (75; markov ∈ methodology → +1 real)
- [x] Unknowns 1.3, 1.5, 7.3, 7.4, 7.5 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 10: Plan Sprint 36 Detailed Schedule

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 36 Day 1
**Owner:** Sprint 36 execution team
**Dependencies:** All tasks (1–9)
**Unknowns Verified:** All (integrates every verified unknown 1.1–7.5)

### Objective

Synthesize the prep outputs into a day-by-day Sprint 36 schedule (Day 0 + Days 1–13) that front-loads the deepest tracks, places the two checkpoints (Day 5, Day 10) and the final retest (Day 13), threads the async testbed run, and attaches an explicit REPLAN exit to each track — within the 168-hour / ≤12h-day budget.

### Why This Matters

The per-priority budgets (P1 14–20h … P7 10–14h; 94–134h total) only fit the 14-day sprint if the deep/REPLAN-prone tracks (markov P1 `σ=sp`, sarf P2, ganges `$66`/`rPower`) are front-loaded and each has a clean exit. A schedule built from the prep designs (Tasks 3–9) turns the plan's budget table into an executable day plan and prevents the "everything lands on Day 13" failure mode.

### Background

`PROJECT_PLAN.md` (Sprint 36) gives the per-priority budgets, the checkpoints (Day 5 / Day 10), the Day-13 retest (determinism ×3, `--resolve-changed --since <S35-close>` GO, PR25 tally), and the REPLAN exits. The per-day workflow is the standing one (branch → work → quality gate only if `*.py` changed → commit → PR → merge → re-baseline). The markov P1 lever is the highest-value, fully-local upside (front-load Days 1–3); sarf P2 is the highest-budget (front-load); the testbed run (Task 7) is async (feeds Day 10 / Day 13).

### What Needs to Be Done

1. **Sequence the tracks by risk + value:** front-load P1 markov (Days 1–3, the fully-local +1) and P2 sarf (highest budget); interleave P3 fawley (co-designed with P1 in `_add_indexed_jacobian_terms`), P4 ganges, then P5/P6/P7.
2. **Place the checkpoints:** Checkpoint 1 (Day 5), Checkpoint 2 (Day 10) — each a `--resolve-changed` re-solve + golden-staleness + PR25 tally.
3. **Thread the async testbed run** (Task 7) so its result lands by Day 10 / Day 13.
4. **Attach a REPLAN exit to each track** (from Tasks 3–9): P1 `σ=sp` architectural depth / cohort leak; P2 timeout re-trigger; P3 gate-leak / H-b hand-off; P4 `$66`/`rPower` depth; P5 Epic-5 deferral.
5. **Budget the days** at ≤12h/day (168h cap), with the ~11h heaviest day (markov `σ=sp` + sarf verification) placed mid-sprint.
6. **Write the Day-0 kickoff checklist** (the fingerprint re-confirmation from Task 2 + the KU Day-0-blocker clearance).
7. **Author `prompts/PLAN_PROMPTS.md`** (Day 0 + Days 1–13) if following the S35 execution pattern.

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# The schedule (and PLAN + prompts) exist
test -f docs/planning/EPIC_4/SPRINT_36/PLAN.md && echo "PLAN exists"
grep -qiE "Day 0|Day 1|Day 5|Day 10|Day 13|Checkpoint|REPLAN" docs/planning/EPIC_4/SPRINT_36/PLAN.md && echo "covers day-by-day + checkpoints + REPLAN exits"
# The per-day prompts exist (if following the S35 pattern)
test -f docs/planning/EPIC_4/SPRINT_36/prompts/PLAN_PROMPTS.md && echo "prompts exist"
# Budget sanity: total within 168h
grep -qiE "168|≤ ?12|94–134|94-134" docs/planning/EPIC_4/SPRINT_36/PLAN.md && echo "budget stated"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_36/PLAN.md` — the Day-0-through-Day-13 schedule: track sequencing (front-loaded P1/P2), the two checkpoints, the async testbed thread, per-track REPLAN exits, the ≤12h/day budget, and the Day-0 kickoff checklist
- `docs/planning/EPIC_4/SPRINT_36/prompts/PLAN_PROMPTS.md` — the per-day execution prompts (Day 0 + Days 1–13), if following the S35 pattern
- A one-line GO/NO-GO for Day 0 (all Day-0 blockers cleared)
- Confirmation that all Unknowns 1.1–7.5 are resolved (✅ VERIFIED / ❌ WRONG-with-correction) in KNOWN_UNKNOWNS.md, with any residual carried as a REPLAN exit

### Acceptance Criteria

- [ ] A day-by-day schedule (Day 0 + Days 1–13) is produced within the 168h / ≤12h-day budget
- [ ] P1 markov + P2 sarf are front-loaded; P3 fawley is co-scheduled with P1 (shared function)
- [ ] Checkpoints (Day 5 / Day 10) + the Day-13 retest are placed
- [ ] The async testbed run (Task 7) is threaded to land by Day 10 / Day 13
- [ ] Each track has an explicit REPLAN exit
- [ ] The Day-0 kickoff checklist (fingerprint re-confirm + KU blocker clearance) is written
- [ ] A GO/NO-GO for Day 0 is stated
- [ ] All Unknowns 1.1–7.5 confirmed resolved (or carried as REPLAN exits) in KNOWN_UNKNOWNS.md

---

## Summary and Critical Path

### Critical Path (Must Complete Before Sprint 36 Day 1)

1. **Task 1: Create Sprint 36 Known Unknowns List** (3-4 hours) — Critical
2. **Task 2: Re-Confirm the Baseline & Banked-Diagnosis Fingerprints** (3-4 hours) — Critical
3. **Task 3: markov P1 — Part-2 (`σ=sp`) Enumeration Design** (5-7 hours) — Critical (the headline lever's deep unknown)
4. **Task 4: fawley P3 — Derivative-Structure Discriminator Design** (4-6 hours) — High (shares `_add_indexed_jacobian_terms` with Task 3)
5. **Task 9: Property-Fixture & Regression-Harness Catalog** (3-4 hours) — Medium (guards the Task-3/Task-4 landings)
6. **Task 10: Plan Sprint 36 Detailed Schedule** (3-4 hours) — Critical (depends on all)

**Total Critical Path Time:** ~21-29 hours (~3-4 working days)

### High Priority (Should Complete Before Sprint 36)

- **Task 5: sarf P2 Design Refresh & Blow-Up Re-Measurement** (4-5 hours) — the highest-budget track's spec
- **Task 6: ganges/gangesx ≥5-Blocker Cascade Re-Verification** (3-4 hours) — the largest potential bucket move

**Total High Priority Time:** ~7-9 hours (~1 working day)

### Medium Priority (Complete Before Sprint 36 or by Day 1 kickoff)

- **Task 7: GAMS-54 Testbed Harness Plan** (3-4 hours) — the testbed dependency for P6/P7
- **Task 8: Consultation Bundle Finalization + camcge Epic-5 Scoping** (2-3 hours) — the P5 submission/scoping readiness

**Total Medium Priority Time:** ~5-7 hours

### Overall Prep Time: ~33-45 hours (~4-6 working days)

---

## Prep Week Schedule

Suggested schedule for completing the prep tasks (adjust to available prep days before Sprint 36 Day 1):

**Day -5:**
- Task 1: Create Sprint 36 Known Unknowns List (3-4h)

**Day -4:**
- Task 2: Re-Confirm the Baseline & Banked-Diagnosis Fingerprints (3-4h)

**Day -3:**
- Task 3: markov P1 — Part-2 (`σ=sp`) Enumeration Design (5-7h)

**Day -2:**
- Task 4: fawley P3 — Derivative-Structure Discriminator Design (4-6h)
- Task 8: Consultation Bundle Finalization + camcge Epic-5 Scoping (2-3h)

**Day -1:**
- Task 5: sarf P2 Design Refresh (4-5h)
- Task 6: ganges/gangesx Cascade Re-Verification (3-4h)
- Task 7: GAMS-54 Testbed Harness Plan (3-4h)
- Task 9: Property-Fixture & Regression-Harness Catalog (3-4h)

**Day 0 (prep close):**
- Task 10: Plan Sprint 36 Detailed Schedule (3-4h) + Day-0 GO/NO-GO

**Sprint 36 Day 1:** 🚀 Sprint begins with all prep complete and every deep track control-gated

---

## Success Criteria for Prep Phase

- [ ] Known Unknowns document created (all 7 priorities; Day-0 blockers flagged)
- [ ] The Sprint-35 baseline (108/93/75) + every banked fingerprint re-confirmed on current `main`
- [ ] The markov Part-2 (`σ=sp`) enumeration has a control-gated design (or a documented REPLAN exit)
- [ ] The fawley derivative-structure discriminator is designed and proven to co-exist with the markov change (2-D cohort byte-identical)
- [ ] The sarf blow-up is re-measured and the O(active) approach re-validated
- [ ] The ganges ≥5-blocker cascade is re-verified and the recovery sequenced
- [ ] The GAMS-54 testbed harness (re-baseline + turkey solve) is planned with confirmed access (or the gap flagged)
- [ ] The P5 consultation bundle is submission-ready and the camcge Epic-5 gate scoped
- [ ] The fixture/harness catalog + robustlp NA survey are complete
- [ ] The Day-0-through-Day-13 schedule is produced within the 168h / ≤12h-day budget with per-track REPLAN exits

**Overall Goal:** every Sprint-36 track starts Day 1 with a control-confirmed, precisely-pinned specification — no un-designed deep unknowns, no unverified banked diagnoses, no Day-0 blockers.

---

## Notes and Risks

### Key Differences from the Sprint 35 Prep

1. **A verified +1-floor lever exists up front** (markov) — unlike S35's bimodal projection, S36 opens with a fully-local, half-de-risked genuine-floor mover; the prep centers on finishing its Part-2 design rather than gating on a single live bucket lever.
2. **Two Sprint-36 outcomes are testbed-gated** (turkey +1, the GAMS-54 re-baseline) — the prep must confirm licensed >1000-row testbed access, a dependency S35 did not carry.
3. **Two tracks share one high-blast-radius function** (markov P1 + fawley P3 both touch `_add_indexed_jacobian_terms`) — the prep co-designs them (Tasks 3 → 4) so they don't collide mid-sprint.

### Potential Risks

1. **Risk:** the markov `σ=sp` off-diagonal enumeration proves architectural (no bounded offset-key mechanism).
   - **Mitigation:** Task 3 enumerates ≥2 candidate mechanisms and a control-gated Phase-0 experiment before Day 1.
   - **Contingency:** a documented P1 REPLAN exit — ship Part 1 (no bucket) + bank Part 2 with the sharpened spec.
2. **Risk:** the fawley discriminator collides with the markov change in `_add_indexed_jacobian_terms`.
   - **Mitigation:** Task 4 depends on Task 3 and produces a joint change-surface map proving non-overlapping branches.
   - **Contingency:** stage the two changes (markov first, fawley second) with a golden-staleness gate between them.
3. **Risk:** no licensed GAMS-54 testbed is available for the >1000-row solves.
   - **Mitigation:** Task 7 confirms access on Day 0 or flags it as a Day-0 risk.
   - **Contingency:** report the v53 KPIs as the S36 baseline and carry the v54 re-baseline + turkey +1 to a later testbed cycle (the emit-level gates stay local and valid).
4. **Risk:** the banked `$149`/`$141` ganges fixes no longer apply cleanly on current `main`.
   - **Mitigation:** Task 6 re-verifies the fix surfaces before Day 1.
   - **Contingency:** re-derive from `GANGES_149_PRODUCT_RULE_ANALYSIS.md` (the derivation is banked, not just the patch).

### Sprint 36 Success Definition

**Minimum Success (B Grade):**
- ✅ markov Part 1 lands (or is re-confirmed) + the Part-2 design is control-gated
- ✅ every deep track re-verified; zero broken code shipped (the control-first discipline holds)
- ✅ the GAMS-54 re-baseline decision is made (even if the testbed run is async)

**Target Success (A Grade):**
- ✅ markov methodology→genuine lands — **genuine floor 75→76 (+1)**, fully local
- ✅ ganges/gangesx OR fawley cold-matches (a second genuine-floor mover)
- ✅ the rocket consultation is submitted + the camcge Epic-5 gate scoped

**Exceptional Success (A+ Grade):**
- ✅ markov + ganges pair + fawley all land — **Solve stretch ≥ 112, genuine floor ≥ 78**
- ✅ sarf recovers to translate (+1 Translate → 136)
- ✅ turkey's +1 realized on the testbed

---

## Appendix: Document Cross-References

### Sprint 36 goals

- `docs/planning/EPIC_4/PROJECT_PLAN.md` — **Sprint 36 (Weeks 37–38)** section (the Goal, the 7 Priorities with Phase-0 gates, Deliverables, Acceptance Criteria, the 94–134h budget, and the Risk Level)
- `docs/planning/EPIC_4/GOALS.md` — Epic 4 strategic themes (Solve Completion, Solution Matching / PATH consultation) that Sprint 36's Solve/Match/floor targets serve

### Sprint 35 carryforward + banked-diagnosis sources (per-track Background)

- `docs/planning/EPIC_4/SPRINT_35/SPRINT_36_CARRYFORWARDS.md` — the consolidated carryforward hand-off (all 7 tracks)
- `docs/planning/EPIC_4/SPRINT_35/SPRINT_RETROSPECTIVE.md` §5 — "Carried into Sprint 36"
- `docs/planning/EPIC_4/SPRINT_35/DAY11_MARKOV_DIAGONAL_LEVER.md` — **P1** markov (§6 = Part-1 implemented + the two-part spec)
- `docs/planning/EPIC_4/SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md` + `PHASE_0_ACCEPTANCE_GATES.md` — **P2** sarf
- `docs/planning/EPIC_4/SPRINT_35/DAY9_P3_FAWLEY_CONTROL_DEFER.md` + `FAWLEY_DIAGONAL_DESIGN.md` — **P3** fawley
- `docs/planning/EPIC_4/SPRINT_35/DAY3_P4_BANK_CARRYFORWARD.md` + `GANGES_RECOVERY_DESIGN.md` + `GANGES_149_PRODUCT_RULE_ANALYSIS.md` — **P4** ganges/gangesx
- `docs/planning/EPIC_4/SPRINT_36/CONSULTATION_BUNDLE.md` + `SPRINT_35/DAY8_P5_CAMCGE_SPRINT36.md` + `SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md` — **P5** rocket/mine/camcge
- `docs/planning/EPIC_4/SPRINT_35/DAY6_P6_TURKEY_AND_TESTFIX.md` + `DAY7_P6_TURKPOW_CLEARLAK.md` — **P6** turkey + residual cohort

### Follow-on / infrastructure items

- `docs/planning/EPIC_4/SPRINT_35/FOLLOWUPS_GAMS54_TRANSITION.md` — the v53→v54 transition follow-ups (**P7** GAMS-54 re-baseline, robustlp NA, the markov `slow`-test)
- `docs/planning/EPIC_4/SPRINT_35/DAY13_RETEST_STAGING.md` §3 — the GAMS-version-axis decision framing
- `docs/planning/EPIC_4/SPRINT_35/DAY10_P7_INFRA_CHECKPOINT2.md` — the P7 fixture-disposition precedent + Checkpoint-2 pattern

### Related research documents

- `docs/research/multidimensional_indexing.md` — multi-dimensional index handling (relevant to the markov `σ=sp` / offset-enumeration work)
- `docs/research/nested_subset_indexing_research.md` — subset/superset index semantics (relevant to the shared `_add_indexed_jacobian_terms` sameas/offset machinery)
- `docs/research/minmax_objective_reformulation.md` — objective/reformulation context for the non-convex forcing / consultation tracks

### Tooling reused throughout (Background for the design tasks)

- `scripts/diagnostics/kkt_residual.py` — the KKT-residual Case-(a/b/c) harness (markov/fawley controls; the PR24/PR27 PROCEED/REPLAN gate)
- `scripts/sprint_audit/check_golden_staleness.py` — the golden-staleness / leak-freedom gate (2-D cohort byte-identical)
- `scripts/gamslib/run_full_test.py --resolve-changed --since-commit <SHA>` — the checkpoint re-solve GO gate
- `scripts/diagnostics/presolve_divergence_allowlist.txt` — the robustlp allowlist (P7 de-allowlist target)

---

**Document Status:** 🔵 NOT STARTED — Sprint 36 prep phase
**Last Updated:** 2026-08-05
**Owner:** Sprint 36 Execution Team

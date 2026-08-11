# Sprint 37 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 37 (the Sprint-36 carryforward sprint) begins
**Timeline:** Complete before Sprint 37 Day 1
**Goal:** De-risk the Sprint-36 banked/deferred carryforwards so each track starts Day 1 with an *empirically-reproduced* diagnosis converted into an implementable design — not an open question — and stand up the mandatory full-corpus leak gate the Sprint-36 retrospective identified as the top process lesson

**Key Insight from Sprint 36:** the control-first REPLAN discipline (PR24/PR27) held for the sixth+ consecutive sprint — every deep track was banked/deferred on control evidence *before* any bad ship (zero broken code, `src/kkt/stationarity.py` and `src/ad/derivative_rules.py` byte-identical to the anchor all sprint). Sprint 36's banks are *sharper* than a prep bank because **each blocker was reproduced live in `src/`**: markov's emission is PROVEN (`CASE_A` + cold-match 2401.577, floor 75→76), ganges's `$141`/`$145`/`$149` fixes are VERIFIED working, fawley's `stat_bq` control is CONFIRMED (473→1.14e-13). So Sprint 37 inherits **proven components + a single precise blocker each**. The one thing the prep phase MUST add: the **full-corpus (163-golden) leak-verification harness** — the 6-model cohort missed all three markov Day-2 leaks (cesam/ferts/sroute), and that gate is now mandatory for every shared-`_add_indexed_jacobian_terms` change.

---

## Executive Summary

`PROJECT_PLAN.md` (Sprint 37, Weeks 39–40) defines the Sprint-36 carryforward sprint. Sprint 36 closed **FLAT** (Solve 108 / Match 93 / genuine floor 75 / Translate 135 — the projection's 75 branch, the fourth consecutive modal-flat close), so each carryforward inherits an empirically-reproduced diagnosis with proven components rather than a raw problem. Sprint 37 will address (priority order per `SPRINT_36/SPRINT_RETROSPECTIVE.md` §5):

1. **Priority 1 (Critical — the headline lever):** markov `σ=sp` derivative-structure discriminator — the +1-floor lever whose **emission is already PROVEN** (`CASE_B` rel 13.3 → `CASE_A` rel 2.8e-16; cold MCP solves to 2401.577 + match; methodology→genuine, floor 75→76, fully local, no testbed). The *sole* blocker: the domain-only gate leaks full-corpus (cesam/ferts/sroute); a leak-free gate needs a derivative-structure discriminator.
2. **Priority 2 (High):** ganges/gangesx ≥5-blocker recovery — `$141`/`$145`/`$149` VERIFIED working; blocked on `$66` (cold, unassigned calibration params) + `rPower` (presolve). Atomic: +2 or 0 (bimodal). *(Task 5 correction: `rPower` is a bounded emit-ordering bug, not the #1378/#1424 class; that divergence sits one level behind it.)*
3. **Priority 3 (Medium):** the rocket/mine consultation cycle + camcge Walras (**Epic 5**) — integrate the PATH authors' rocket reply (+1 contingent); track the mine question; prototype the camcge three-part Walras redefinition.
4. **Priority 4 (High):** fawley constraint-index-diagonal (#1111/#1112) — correctness confirmed (473→1.14e-13); relocate the `qsb`/`pbal` emission path + rebuild the orientation predicate + verify full-corpus. 0-bucket (H-b); the +Solve is a Sprint-38 consultation.
5. **Priority 5 (High):** sarf symbolic-emit subsystem (#1385) — the 20–28h atomic re-architecture of the 369K-column materialization (O(active=398), not O(369K)); lowest-leverage in *bucket* terms (+1 Translate), but the prep-design work is High (the deepest re-arch spec, gated on the P7 harness).
6. **Priority 6 (Medium):** turkey testbed +1 (licensed >1000-row solve) + the full GAMS-54 v54 re-baseline of the 142 candidates (demo-runnable) + the residual multi-root cohort.
7. **Priority 7 (Medium — infrastructure):** the **full-corpus (163-golden) leak-verification harness** (the top process lesson) + Phase-0-doc CI enforcement + property fixtures + genuine-floor tracking.

This prep plan focuses on the research, design, and setup tasks that must complete before Sprint 37 Day 1 to prevent Day-1-through-Day-5 blocking on an un-designed discriminator, an un-re-verified banked fix, or a missing leak gate.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint 37 Goal Addressed |
|---|------|----------|-----------|--------------|--------------------------|
| 1 | Create Sprint 37 Known Unknowns List | Critical | 3-4 hours | None | Proactive unknown identification across all 7 priorities |
| 2 | Re-Confirm the Sprint-36 Baseline & Banked-Diagnosis Fingerprints | Critical | 3-4 hours | Task 1 | Verify 108/93/75/135 + the proven-component fingerprints still hold on current `main` |
| 3 | Full-Corpus (163-Golden) Leak-Verification Harness Design & Setup | Critical | 4-5 hours | Tasks 1, 2 | P7 leak gate (the top process lesson); the gate P1/P4 design against |
| 4 | markov P1 — Derivative-Structure Discriminator Design | Critical | 5-7 hours | Tasks 1, 2, 3 | P1 markov `σ=sp` +1-floor lever |
| 5 | ganges/gangesx P2 — ≥5-Blocker Cascade Re-Verification & Recovery Sequencing | High | 3-4 hours | Tasks 1, 2 | P2 ganges/gangesx recovery |
| 6 | fawley P4 — Emission-Path Location & Constraint-Index-Diagonal Discriminator Design | High | 4-6 hours | Tasks 1, 2, 3, 4 | P4 fawley constraint-index-diagonal |
| 7 | sarf P5 — Symbolic-Emit Re-Architecture Design Refresh & Blow-Up Re-Measurement | High | 4-5 hours | Tasks 1, 2 | P5 sarf symbolic-emit subsystem |
| 8 | GAMS-54 v54 Re-Baseline Harness Plan + turkey Testbed Procurement (P6) | Medium | 3-4 hours | Tasks 1, 2 | P6 turkey testbed +1 + full v54 re-baseline |
| 9 | Consultation Reply-Integration Prep (rocket/mine P3) + camcge Epic-5 Walras Gate Scoping | Medium | 2-3 hours | Tasks 1, 2 | P3 rocket/mine consultation + camcge Walras (Epic 5) |
| 10 | Property-Fixture Catalog + Phase-0-Doc-Enforcement + Genuine-Floor Tracking (P7) | Medium | 3-4 hours | Tasks 1, 3, 4, 6 | P7 fixtures / Phase-0 CI / genuine-floor tracking |
| 11 | Plan Sprint 37 Detailed Schedule | Critical | 3-4 hours | All tasks (1–10) | Day-by-day schedule + REPLAN exits + budget |

**Total Estimated Time:** ~37-50 hours (~5-6 working days)

**Critical Path:** Tasks 1 → 2 → 3 → 4 → 6 → 10 → 11 (the leak-harness setup gates the markov P1 discriminator design; the markov design gates the fawley P4 design — they share `_add_indexed_jacobian_terms`; both gate the fixture catalog and the schedule).

**Note:** Task 1 (Known Unknowns) is the standing first prep task; it must be created before the design tasks (3–10) so each design is scoped against an explicit risk register. Task 3 (the full-corpus leak harness) is elevated to Critical this sprint — it is both P7's deliverable and the acceptance gate that the P1/P4 designs (Tasks 4, 6) build their Phase-0 gates against, so it precedes them on the critical path.

---

## Task 1: Create Sprint 37 Known Unknowns List

**Status:** ✅ COMPLETE (2026-08-09)
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 37 Day 1
**Owner:** Sprint 37 execution team
**Dependencies:** None

### Objective

Create `docs/planning/EPIC_4/SPRINT_37/KNOWN_UNKNOWNS.md` cataloguing every open question, assumption, and risk across the seven Sprint-37 priorities, each with an assumption statement, a verification method, a priority, and a target resolution point (prep task or sprint day).

### Why This Matters

The Known-Unknowns process has caught late surprises before they became mid-sprint blockers across Sprints 27–36. Sprint 37 front-loads one deep unknown (the markov `σ=sp` derivative-structure discriminator, on which the +1-floor lever depends), a shared-machinery collision risk (markov P1 and fawley P4 both touch `_add_indexed_jacobian_terms`), and a testbed dependency (the turkey +1 needs a licensed >1000-row GAMS-54 solve). Surfacing these as tracked unknowns on Day 0 lets the design tasks (3–10) resolve them proactively rather than discovering them on Day 3. The Sprint-36 retrospective's top process lesson — full-corpus leak verification is mandatory — must be encoded as an explicit unknown so the schedule enforces it.

### Background

Each prior sprint's `KNOWN_UNKNOWNS.md` (e.g. `docs/planning/EPIC_4/SPRINT_36/KNOWN_UNKNOWNS.md`) partitions unknowns into VERIFIED / REPLAN / DESIGN-SPECIFIED / INCOMPLETE and drives the Day-0 fingerprint re-confirmation. Sprint 36 closed with the sharpened banks in `SPRINT_36/SPRINT_37_CARRYFORWARDS.md` (each blocker reproduced live); Sprint 37's unknowns are the *residual* questions those carryforwards leave open — e.g. "can a derivative-structure key distinguish markov's param-coupled `σ=sp` from cesam's variable-bilinear and sroute's conditional-constant derivatives?", "do the ganges `$141`/`$145`/`$149` fixes still apply byte-clean on current `main`?", "does the fawley discriminator collide with the markov P1 change in `_add_indexed_jacobian_terms`?", "is a licensed >1000-row GAMS-54 testbed procurable in the sprint window?".

### What Needs to Be Done

1. **Enumerate unknowns per priority (P1–P7).** For each track, list the residual open questions from its Sprint-36 carryforward:
   - **P1 markov:** does the reverted Day-2 Mechanism C prototype still drive `CASE_B` → `CASE_A` on current `main`? Can a derivative-structure signature fire only on the genuine `−b·pi(s,i,σ,τ,sp)` param-coupling and exclude conditional-constant (sroute `1$(darc(ip,ipp))`) and variable-bilinear (cesam) structures? Does the discriminator pass the full-corpus (163) leak gate, not just the 6-model cohort?
   - **P2 ganges:** do the `$141`/`$145`/`$149` fixes (git `a8ff626c` + the `_diff_prod` §5 patch) still apply on current `main`? Are `$66` (cold) and `rPower` (presolve) still the terminal blockers? Is `rPower` tractable within the sprint, or is it the deep #1378/#1424 divergence class beyond a bounded fix?
   - **P3 rocket/mine/camcge:** has the PATH authors' reply to the rocket #1462 submission arrived, and does it map to a `--force homotopy` option-set? Is the camcge three-part Walras redefinition reachable in a `/tmp` demo control (641 rows)?
   - **P4 fawley:** where does the `qsb`/`pbal` emission path actually run (≠ the design's assumed partial-overlap branch)? Can the constraint-index-diagonal orientation predicate be rebuilt and layered with a discriminator that co-exists with the P1 markov change?
   - **P5 sarf:** is the 369K blow-up still >100s on current `main`? Does the O(active=398) symbolic/parametric emit form pass GAMS instantiation? Can the re-arch land against the full-corpus regression harness (P7)?
   - **P6 turkey/GAMS-54:** is a licensed >1000-row GAMS-54 testbed available? Which of the 5 OBJ-GAP models (agreste/cesam/chain/fawley/rocket) shift buckets under v54 demo?
   - **P7 infra:** which slow-emit CGE/dynamic goldens need the nightly budget in the full-corpus gate? Where does the Phase-0-doc CI check hook (which paths trigger it)?
2. **Assign each unknown:** assumption, verification method, priority (Critical/High/Medium/Low), and target resolution (which prep task or which sprint day).
3. **Tag each with a disposition slot:** VERIFIED / REPLAN / DESIGN-SPECIFIED / INCOMPLETE (initially INCOMPLETE for open ones).
4. **Flag Day-0 blockers** — any unknown whose non-resolution blocks Day 1 (e.g. the markov discriminator design, the leak-harness gate).

### Changes

Created `docs/planning/EPIC_4/SPRINT_37/KNOWN_UNKNOWNS.md` (27 unknowns across 7 categories, numbered `X.Y` per category) following the Sprint-36 KNOWN_UNKNOWNS conventions: Executive Summary, How to Use This Document (with priority definitions), Summary Statistics, Table of Contents, the 7 category blocks (P1 markov `σ=sp` discriminator · P2 ganges/gangesx recovery · P3 rocket/mine/camcge · P4 fawley · P5 sarf · P6 turkey/GAMS-54 · P7 infrastructure), a Confirmed Knowledge section, the Template for New Unknowns, Next Steps, and an `## Appendix: Task-to-Unknown Mapping` table. Added a "Deferred-unknown lineage" note tracing each track to its Sprint-36 disposition. Also added the "**Unknowns Verified:**" metadata + a KNOWN_UNKNOWNS-update deliverable + acceptance criterion to PREP_PLAN.md Tasks 2–10.

### Result

27 unknowns documented (Critical 7 / High 11 / Medium 7 / Low 2 = 26/41/26/7%; ~36h total research time — within the 28–36h target). Every unknown carries Priority, Assumption, 3–5 Research Questions, How to Verify, Risk if Wrong, Estimated Research Time, Owner, and a `🔍 Status: INCOMPLETE` Verification Results slot. The Task-to-Unknown mapping assigns every unknown (1.1–7.4) to ≥1 prep task (Tasks 2–10), with the 7 Critical unknowns (1.1, 1.2, 1.3, 2.1, 2.3, 4.2, 7.1) front-loaded into Tasks 2–8. Zero Day-0 blockers remain unmapped. The two deep prep-phase design priorities (Unknown 1.2 the markov `σ=sp` derivative-structure discriminator; Unknown 1.5/4.2 the markov/fawley shared-function collision) and the mandatory full-corpus (163-golden) leak gate (Unknowns 1.3/7.1) are called out in the Executive Summary and Next Steps.

### Verification

```bash
# The document exists and has the expected structure
test -f docs/planning/EPIC_4/SPRINT_37/KNOWN_UNKNOWNS.md && echo "KU doc exists"
# All seven priorities are represented
for p in markov ganges rocket mine camcge fawley sarf turkey "GAMS[.-]54"; do
  grep -qiE "$p" docs/planning/EPIC_4/SPRINT_37/KNOWN_UNKNOWNS.md && echo "  covers: $p"
done
# Each unknown carries an assumption + verification + priority
grep -ciE "assumption|verification|priority" docs/planning/EPIC_4/SPRINT_37/KNOWN_UNKNOWNS.md
# The mandatory full-corpus leak gate is tracked as an unknown
grep -qiE "full-corpus|163" docs/planning/EPIC_4/SPRINT_37/KNOWN_UNKNOWNS.md && echo "  leak gate tracked"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_37/KNOWN_UNKNOWNS.md` — the Sprint-37 unknowns register (all 7 priorities), each with assumption / verification / priority / target resolution / disposition slot
- A count of Day-0 blockers (target: 0 unresolved at Day 1)
- The full-corpus (163-golden) leak-verification requirement encoded as a Critical unknown mapped to Task 3

### Acceptance Criteria

- [x] Document created covering all seven priorities (P1–P7) — 27 unknowns across 7 categories
- [x] Each unknown has an assumption, a verification method (How to Verify), a priority, and a target resolution point (the verifying prep task)
- [x] Each unknown carries a disposition slot (`🔍 Status: INCOMPLETE`, to advance to VERIFIED / WRONG during prep)
- [x] Day-0 blockers explicitly flagged (and mapped to Tasks 2–8; the Task-11 GO/NO-GO gates them)
- [x] The deep prep-phase design priority (the markov `σ=sp` discriminator) and the markov/fawley shared-function collision are called out as prep-phase design priorities
- [x] The full-corpus (163-golden) leak gate is tracked as a Critical unknown

---

## Task 2: Re-Confirm the Sprint-36 Baseline & Banked-Diagnosis Fingerprints

**Status:** ✅ COMPLETE (2026-08-09)
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 37 Day 1
**Owner:** Sprint 37 execution team
**Dependencies:** Task 1 (Known Unknowns — the fingerprints to re-confirm are the Task-1 unknowns' assumptions)
**Unknowns Verified:** 1.1, 2.1, 4.3, 5.1, 7.4

### Objective

Re-verify, on current `main`, that (a) the Sprint-36 close KPIs still recompute (Solve 108 / Match 93 (63 cold + 30 presolve) / genuine floor 75 / Translate 135 / mi 7 / pse 7 / all-219 96), (b) the DB is byte-identical to the anchor `78ceaead`, and (c) each banked track's *proven-component* fingerprint still reproduces (markov's `CASE_B`→`CASE_A` emission, ganges's `$141`/`$145`/`$149` cold cascade → 0, fawley's `stat_bq` 473→1.14e-13, sarf's >100s blow-up).

### Why This Matters

Every Sprint-37 design task builds on a Sprint-36 empirical finding. If `main` has drifted since the S36 close (`935d94b7`) — a merged PR touching `stationarity.py`, `derivative_rules.py`, or `emit_gams.py`, or a golden regen — a design premised on the banked fingerprint could be built against a stale tree and fail on Day 1. The Sprint-36 retrospective's "reproduce, don't trust the doc" lesson applies to the prep phase itself: re-confirm the fingerprints before designing against them.

### Background

The anchor for `--resolve-changed` and the DB byte-check is `78ceaead` (S34 close); the DB has been byte-unchanged since. The S36 close is `935d94b7`; the P7 robustlp landing added `+37` lines to `_emit_nlp_presolve` plus the harness/allowlist changes, and the S35 turkey `original_symbols.py` change is also in the tree. The banked fingerprints and their reproduction commands live in the Sprint-36 day docs: `DAY2_MARKOV_OFFDIAG_CONTROL.md` (markov emission), `DAY8_P4_GANGES_BANK.md` (git `a8ff626c` + the `_diff_prod` §5 patch), `DAY4_FAWLEY_DEFER.md` (the `stat_bq` hand-edit), `DAY6_SARF_BANK.md` (the blow-up timing). The KKT-residual harness (`scripts/diagnostics/kkt_residual.py`) and the golden-staleness gate (`scripts/sprint_audit/check_golden_staleness.py`) are the reusable instruments.

### What Needs to Be Done

1. **Re-baseline the KPIs.** Run the PR25 re-baseline (or `scripts/gamslib/run_full_test.py --only-parse --quiet` + the KPI recompute) and confirm Solve 108 / Match 93 / floor 75 / Translate 135 / mi 7 / pse 7 / all-219 96.
2. **DB byte-check.** `git diff 78ceaead..HEAD -- data/gamslib/gamslib_status.json` must be empty (0 bucket move since the anchor).
3. **Golden-staleness clean.** Run `check_golden_staleness.py` across all 163 goldens → clean (no unintended drift on current `main`).
4. **Re-confirm the four proven-component fingerprints** (each on current `main`, using the banked reproduction recipe):
   - **markov:** re-apply the reverted Day-2 Mechanism C prototype in a `/tmp` copy → `kkt_residual.py markov` reaches `CASE_A` (rel ≈ 2.8e-16) and the cold MCP solves to 2401.577 + match. Confirm the domain-only gate still leaks onto cesam/ferts/sroute (the full-corpus leak).
   - **ganges/gangesx:** re-apply the `$141`/`$145`/`$149` fixes (git `a8ff626c` + the `_diff_prod` §5 patch) in a `/tmp` copy → the cold compile's `$141`/`$145`/`$149` count → 0; `$66` ×17 and `rPower` still reproduce as the terminals.
   - **fawley:** re-apply the `stat_bq` `sameas` hand-edit → `max|stat_bq|` 473 → 1.14e-13 on byte-identical goldens.
   - **sarf:** re-run the emit → confirm the 369K blow-up still exceeds the 100s cap (still non-terminating).
5. **Record any drift.** For each fingerprint, note VERIFIED (still reproduces) or DRIFTED (with the delta) and update the Task-1 unknowns' dispositions accordingly.

### Changes

Ran the Sprint-37 Day-0 baseline re-confirmation on current `main` (`8db02e50`) against the anchor `78ceaead`: (a) recomputed the KPI baseline over the 142 convex candidates from the committed DB; (b) DB byte-check + the `stationarity.py`/`derivative_rules.py`/6-sarf-call-site byte-checks vs the anchor; (c) full golden-staleness across the 163 goldens; (d) the four proven-component fingerprint controls (markov + fawley via `kkt_residual.py`; ganges/gangesx cascade-fix-surface checks; sarf capped-emit blow-up). Produced `docs/planning/EPIC_4/SPRINT_37/BASELINE_RECONFIRMATION.md`. Advanced Unknowns 1.1, 2.1, 4.3, 5.1, 7.4 → ✅ VERIFIED in `KNOWN_UNKNOWNS.md`.

### Result

**All five checks pass — the baseline is measured reality, not a snapshot.** KPIs recompute **exactly**: Solve 108 / Match 93 (63 cold + 30 presolve) / Translate 135 / Parse 142 / mi 7 / pse 7 / all-219 96. The DB is **byte-identical to the anchor** (0 bucket move) and `src/kkt/stationarity.py` + `src/ad/derivative_rules.py` are **byte-identical to the anchor** (the only `src/` deltas since the anchor are the P7 `emit_gams.py` +37 and the turkey `original_symbols.py` +52 — both expected). **All four proven-component fingerprints re-confirm:** markov `CASE_B` rel 13.3 (`stat_z(empty,disrupted,empty)`) + DB methodology match @ 2401.5773 → the Day-2 `CASE_A`+cold-match reproduces deductively on byte-identical code; ganges cascade-fix surfaces byte-clean (`_diff_prod:3276` unchanged, `_expr_contains_varref_attribute` present, `a8ff626c` reachable); fawley `CASE_B` `stat_bq` 0.973 + H-b `stat_trans(tr-2)` 1.00; sarf >105s non-terminating (O(369K)). markov ∈ the 30-model methodology partition → the +1 lever (Task 4) is a true +1; floor anchor 75 carries forward. Golden-staleness clean across all 163 goldens. **Zero drift on any of the five unknowns → Sprint 37's Task-4/5/6/7 designs start from re-confirmed surfaces.**

### Verification

```bash
# DB byte-unchanged since the anchor
git diff 78ceaead..HEAD -- data/gamslib/gamslib_status.json | head -1   # expect empty

# Golden-staleness clean across the full corpus
python scripts/sprint_audit/check_golden_staleness.py 2>&1 | tail -5

# stationarity.py / derivative_rules.py unchanged vs the S36 close (proven-component tree)
git diff 935d94b7..HEAD -- src/kkt/stationarity.py src/ad/derivative_rules.py | head -1  # expect empty

# The banked fingerprint reproduction recipes exist to follow
for d in DAY2_MARKOV_OFFDIAG_CONTROL DAY8_P4_GANGES_BANK DAY4_FAWLEY_DEFER DAY6_SARF_BANK; do
  test -f docs/planning/EPIC_4/SPRINT_36/$d.md && echo "  recipe: $d"
done
```

### Deliverables

- A short `BASELINE_RECONFIRMATION.md` (or a Task-2 section in the Sprint-37 prep notes) recording: the recomputed KPIs, the DB byte-check result, the golden-staleness result, and the VERIFIED/DRIFTED disposition of each of the four proven-component fingerprints
- Updated dispositions in `KNOWN_UNKNOWNS.md` (each re-confirmed assumption advanced from INCOMPLETE to VERIFIED, or flagged DRIFTED)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 2.1, 4.3, 5.1, 7.4

### Acceptance Criteria

- [x] KPIs recompute to Solve 108 / Match 93 / floor 75 / Translate 135 / mi 7 / pse 7 / all-219 96 on current `main`
- [x] `gamslib_status.json` byte-identical to `78ceaead` (0 bucket move)
- [x] Golden-staleness clean across all 163 goldens
- [x] All four proven-component fingerprints re-confirmed (markov emission, ganges cascade, fawley `stat_bq`, sarf blow-up) OR any drift documented with its delta
- [x] Every re-confirmed fingerprint's unknown advanced to VERIFIED in `KNOWN_UNKNOWNS.md`
- [x] Unknowns 1.1, 2.1, 4.3, 5.1, 7.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: Full-Corpus (163-Golden) Leak-Verification Harness Design & Setup

**Status:** ✅ COMPLETE (2026-08-10)
**Priority:** Critical
**Estimated Time:** 4-5 hours
**Deadline:** Before Sprint 37 Day 1
**Owner:** Sprint 37 execution team
**Dependencies:** Tasks 1, 2 (the harness gates the P1/P4 designs; it must exist before they design their acceptance gates against it)
**Unknowns Verified:** 1.3, 7.1

### Objective

Design and stand up the **full-corpus (163-golden) leak-verification harness** as a required gate for any `src/{ad,kkt,emit}` change touching the shared `_add_indexed_jacobian_terms` (or `_compute_index_offset_key`) — a `make` target + a CI job — so that the P1 markov and P4 fawley designs can specify "full-corpus golden-staleness shows ONLY my model drifts" as their Phase-0 acceptance criterion.

### Why This Matters

This is the Sprint-36 retrospective's **single biggest process lesson**: the prep's 6-model cohort is *not* the risk set — it missed all three markov Day-2 leaks (cesam/ferts/sroute). markov P1 and fawley P4 both modify the high-blast-radius shared `_add_indexed_jacobian_terms`; without a full-corpus gate, a "leak-free by construction" design claim is an untested hypothesis (markov's Mechanism C was argued leak-free and leaked). Standing the gate up in prep — before the designs — means P1/P4 are designed *against* it, not retrofitted.

### Background

`scripts/sprint_audit/check_golden_staleness.py` already regenerates emit goldens and diffs them; Sprint 36 ran it across 163 goldens manually on Day 13 ("golden-staleness clean ×163"). The gap is that it is not wired as a *required, cohort-complete* gate with a defined slow-model budget. The CGE and dynamic-set models (camcge, cesam, ferts, sroute, the ganges 335s slow-emit goldens) are the expensive tail; the Sprint-36 carryforward notes them as "nightly budget" candidates. `FIXTURE_AND_HARNESS_CATALOG.md` (Sprint 36) catalogs the existing fixtures/harness instruments to reuse.

### What Needs to Be Done

1. **Inventory the 163 goldens** and classify by emit cost: fast (sub-second), medium, slow (the CGE/dynamic/ganges tail >10s). Record the total wall-clock for a full regen and the slow-tail subset.
2. **Design the gate's two modes:**
   - **PR-blocking fast mode:** regenerate + diff the fast/medium goldens on every `_add_indexed_jacobian_terms`-touching PR (target: completes in CI time budget).
   - **Nightly full mode:** the complete 163-golden regen + diff, including the slow tail, on a nightly schedule; a PR touching the shared function must have a green nightly before merge (or an explicit slow-subset run).
3. **Specify the trigger:** which changed paths arm the gate (`src/kkt/stationarity.py`, `src/ad/derivative_rules.py`, `src/emit/emit_gams.py`, or narrower — the functions `_add_indexed_jacobian_terms` / `_compute_index_offset_key`). Prefer a path/function-scoped trigger to avoid arming on unrelated emit changes.
4. **Define the pass criterion:** "only the intended model(s) drift; all others byte-identical." Provide a `--expect-drift <model>[,<model>...]` argument so P1/P4 can assert exactly their model drifts and nothing else.
5. **Draft the `make` target + CI job** (design/spec only in prep; the src/CI wiring lands in the sprint under P7). Document the `make leak-check MODEL=markov` invocation the P1/P4 Phase-0 gates will cite.
6. **Dry-run the fast mode** on a no-op change to confirm zero false-positive drift (the harness itself is deterministic).

### Changes

Reproduced the actual state of the gate before designing (the "reproduce, don't trust the doc" rule) and **corrected the prep premise**: the full-corpus sweep **already existed** (`.github/workflows/golden-staleness.yml` runs `check_golden_staleness.py` with no `--models` restriction → all 163 in-scope goldens, 25-min ceiling, triggered on `src/{ad,kkt,emit,ir}/**` — which already covers both shared functions in `src/kkt/stationarity.py`). Implemented the **actual** missing piece: `--expect-drift` in `scripts/sprint_audit/check_golden_staleness.py` (exactly-the-expected-set semantics, anti-laundering `--fix`, no-op detection, unverified≠clean) plus a `leak-check` target in the `Makefile` (`make leak-check MODEL=<id>`). Verified against 4 simulated drift scenarios. Produced `docs/planning/EPIC_4/SPRINT_37/LEAK_HARNESS_DESIGN.md`. Advanced Unknowns 7.1, 1.3 → ✅ VERIFIED.

### Result

**The gate existed; its verdict was the gap.** The prep assumption ("build a full-corpus mode as a required gate") was wrong in three ways (§1 of the design doc): the sweep already runs on all 163 goldens within CI budget; the path trigger is already correct (narrowing to *function* scope would be fragile and strictly worse); and no fast/nightly split is warranted — splitting would reintroduce the very cohort-incompleteness that caused the Sprint-36 miss. **The real defect:** the gate answers *"did anything drift?"* when a shared-function change needs *"did **exactly** the intended model drift?"* — and its remediation advice (`make regen-goldens`) refreshes **every** drifted golden, so a markov fix leaking onto cesam/ferts/sroute is **laundered into the goldens** and the gate goes green. That is precisely how the Sprint-36 leak could have survived review. **Shipped `--expect-drift` / `make leak-check MODEL=<id>`**, verified against 4 scenarios: (A) clean tree → `NO-OP` (the fix changed nothing) exit 1; (B) markov-only drift → `LEAK GATE PASS` exit 0; (C) markov+cesam → `LEAK: cesam` exit 1 (the exact S36 shape); (D) the same under `--fix` → the expected golden refreshed, **the leaked golden left byte-untouched and named** (anti-laundering). Timeouts block the claim (unverified ≠ clean). Quality gate fully green (typecheck / format / lint / **`make test` 5040 passed, 10 skipped, 1 xfailed**); the corpus is byte-clean after the scenarios. **Tasks 4 and 6 can now cite a real, tested Phase-0 invocation** (`make leak-check MODEL=markov` / `MODEL=fawley`). Two items remain for P7 in-sprint: making `golden-staleness` a *required* check (branch protection shows `required_status_checks.contexts: []` — a maintainer setting) and wiring `leak-check` into the emit-PR Phase-0 rule.

### Verification

```bash
# The staleness script exists and runs across the full corpus
python scripts/sprint_audit/check_golden_staleness.py --help 2>&1 | head -5
ls data/gamslib/mcp/ | wc -l    # golden count (expect ~163)

# A dry-run on a clean tree shows zero drift (deterministic baseline)
python scripts/sprint_audit/check_golden_staleness.py 2>&1 | tail -3

# The design doc names the two modes + the --expect-drift criterion
grep -qiE "expect-drift|nightly|fast mode" docs/planning/EPIC_4/SPRINT_37/LEAK_HARNESS_DESIGN.md && echo "modes specified"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_37/LEAK_HARNESS_DESIGN.md` — the golden inventory (fast/medium/slow classification + wall-clock), the two-mode gate design, the path/function-scoped trigger, the `--expect-drift` pass criterion, and the draft `make` target + CI job spec
- A confirmed clean full-corpus baseline (163 goldens, zero drift on current `main`) to gate against
- The `make leak-check MODEL=<name>` invocation string the P1/P4 Phase-0 gates will reference
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.3, 7.1

### Acceptance Criteria

- [x] All 163 goldens inventoried and cost-classified (fast/medium/slow) with a total-regen wall-clock estimate
- [x] Two-mode design specified (PR-blocking fast mode + nightly full mode) with the slow-tail budget
- [x] Path/function-scoped trigger defined (arms only on `_add_indexed_jacobian_terms`-relevant changes)
- [x] The `--expect-drift <model>` pass criterion designed (asserts only the intended model drifts)
- [x] The `make` target + CI job drafted (spec ready for P7 to wire in-sprint)
- [x] A clean full-corpus baseline confirmed on current `main` (zero drift, deterministic)
- [x] Unknowns 1.3, 7.1 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 4: markov P1 — Derivative-Structure Discriminator Design

**Status:** ✅ COMPLETE (2026-08-10)
**Priority:** Critical
**Estimated Time:** 5-7 hours
**Deadline:** Before Sprint 37 Day 1
**Owner:** Sprint 37 execution team
**Dependencies:** Tasks 1, 2 (the re-confirmed markov emission fingerprint), 3 (the leak gate the discriminator must pass)
**Unknowns Verified:** 1.2, 1.3, 1.4, 1.5

### Objective

Design the **derivative-structure discriminator** that lets the proven markov `σ=sp` Mechanism C emission fire *only* on the genuine param-coupled off-diagonal (`−b·pi(s,i,σ,τ,sp)`) and *not* on the structurally-different derivatives in cesam (variable-bilinear) and sroute (conditional-constant) — the sole blocker between the proven emission and the +1 genuine floor (75→76).

### Why This Matters

This is the sprint's strongest and only fully-local bucket lever: the emission is already PROVEN (Day 2 drove `CASE_B` rel 13.3 → `CASE_A` rel 2.8e-16 and the cold MCP solved to the reference 2401.577 + match), so the entire +1 hinges on a leak-free gate. A domain-only signature leaks full-corpus. Designing the discriminator in prep — with the full-corpus leak gate (Task 3) as the acceptance instrument — means Day 1 starts with an implementable predicate and a pass/fail test, not an open research question. This is the deepest prep-phase design and the head of the critical path.

### Background

markov's `σ=sp` off-diagonal correction (reconciliation (a), `MARKOV_OFFDIAGONAL_DESIGN.md`): the Kronecker `nu_constr(s,i)` term plus `−b·sum(j, pi(s,i,sp,j,sp)·nu_constr(sp,j))`, where `pi` is a *parameter* coupling the constraint index to the variable's independent index — this is the genuine structure that must fire. The two leak structures (Day 2): sroute's `1$(darc(ip,ipp))` is a *conditional-constant* derivative (a `$`-condition, no parameter coupling the two index positions), and cesam's is a *variable-bilinear* derivative (two variables multiplied, not a param × multiplier). A domain-only gate (matching on index-position domains alone) cannot tell these apart — it needs to inspect the *derivative expression's structure*: is the off-diagonal coefficient a parameter (`pi`) whose argument tuple couples the constraint's index to the variable's independent index, versus a conditional constant or a variable product. Banked refs: `SPRINT_36/DAY2_MARKOV_OFFDIAG_CONTROL.md`, `DAY3_MARKOV_BANK.md`, `MARKOV_OFFDIAGONAL_DESIGN.md`.

### What Needs to Be Done

1. **Characterize the three derivative structures precisely.** For markov (genuine), sroute (leak), and cesam (leak), extract the exact AST/IR shape of the off-diagonal Jacobian term as it reaches `_add_indexed_jacobian_terms`: the coefficient node type (parameter ref vs conditional constant vs binary var-product), its argument tuple, and how the constraint index relates to the variable's independent index.
2. **Design the discriminating predicate.** Define a structural key computed from the derivative term that is TRUE for markov's `−b·pi(...)` param-coupling and FALSE for sroute's conditional-constant and cesam's variable-bilinear. Candidate: "the off-diagonal coefficient is a *parameter reference* whose index tuple contains both the constraint's aliased index and the variable's independent index in the coupling positions." Specify it against the IR node types (`ParamRef`, `IndexOffset`, `SubsetIndex`, conditional `$`).
3. **Locate the hook point** in `_add_indexed_jacobian_terms` / `_compute_index_offset_key` where the predicate gates the Mechanism C emission; confirm it composes with the existing diagonal-Kronecker path without disturbing the 63 cold-optimal / 30 presolve matches.
4. **Design the Phase-0 acceptance gate** (PR24/PR27 + Task 3): the discriminator drives `kkt_residual.py markov` → `CASE_A` + cold `model_optimal` + match (2401.577); `make leak-check MODEL=markov` (Task 3) shows **only markov drifts** across the full corpus (cesam/ferts/sroute/polygon/ps2/ps3 byte-identical); the `shape_markov_diagonal_kronecker` fixture + the sharpened `test_markov_stationarity_has_correction_term` fail-before/pass-after.
5. **Write the Phase-0 issue doc skeleton** (`docs/issues/ISSUE_1110_markov-sigma-sp-discriminator.md`) with the 4 `### ` Acceptance-Gate subsections — authored *before* the Day-1 src commit (the Sprint-36 P7 lesson).
6. **Define the REPLAN exit:** if no structural key cleanly separates all three (the discriminator over-generalizes or the three structures are not separable by a local predicate), document the residual and bank a narrower per-signature allowlist as the fallback.

### Changes

Extracted the three off-diagonal derivative ASTs **from the live Jacobian** (`compute_constraint_jacobian` → `get_derivative`) rather than assuming them, prototyped the discriminating predicate, and **scanned it across 142 of the 163 in-scope models** — twice, because the first two designs were refuted by that scan. Produced `docs/planning/EPIC_4/SPRINT_37/MARKOV_DISCRIMINATOR_DESIGN.md`, the Phase-0 gate doc `docs/issues/ISSUE_1110_markov-sigma-sp-discriminator.md` (4 `###` subsections), and the `shape_markov_diagonal_kronecker` fixture spec with its fail-before condition measured on the committed golden. Advanced Unknowns 1.2, 1.4, 1.5 → ✅ VERIFIED and 1.3 → 🔶 DESIGN-VERIFIED.

### Result

**The discriminator is designed and corpus-validated — and measurement refuted two designs before settling one.** The three structures separate cleanly: markov's off-diagonal is `ParamRef pi(s,i,σ,τ,sp)` (a value-branch parameter carrying the equation index σ *and* the variable's own `sp`); sroute's is `DollarCond(VAL: Const(1.0), COND: ParamRef darc(...))` — parameter **only in the condition**; cesam's is `VarRef x + VarRef err1` — **no parameter at all**. **Refutation 1:** the obvious derivative-only predicate fires on **15** models (agreste/ajax/cesam/cesam2/china/fawley/marco/markov/orani/prolog/shale/tfordy/tforss/twocge/uimp) — a param coupling an eq index to a var index is an ordinary pattern, so the test is only valid *conjoined* with S36's domain-collision signature. **Refutation 2:** that conjunction *still* leaked, on `iobalance`, whose `ParamRef x(1)` has one index coincidentally equal to both the eq value and the collision value; the fix is to require the matches at **distinct positions** of the parameter's index tuple. **Final result:** the conjoined, distinct-position predicate fires on **exactly `['markov']`** across 142 models, while **14** models reach the domain gate (reproducing S36's leak — `cesam`, `sroute` among them) and **13 of 14** are excluded by the derivative conjunct. Hook point located (`offset_groups` `:6136–6158`, correction append `:7214+`); `_compute_index_offset_key` untouched. **Unknown 1.5 resolved more strongly than expected:** fawley declares **no aliases**, so conjunct (1) is structurally unsatisfiable there — the markov gate never reaches fawley (measured `domain_gate_pairs: []`). **Honest limit:** 10 of 163 models are unverified at design time (6 skipped as pathologically slow, 4 timed out — including `ferts`, the third S36 leak), and a predicate scan is not a golden byte-diff, so 1.3 is deliberately left DESIGN-VERIFIED; `make leak-check MODEL=markov` at landing is the definitive gate.

### Verification

```bash
# The design doc specifies the three-structure characterization + the predicate
grep -qiE "param.*coupl|conditional-constant|variable-bilinear" docs/planning/EPIC_4/SPRINT_37/MARKOV_DISCRIMINATOR_DESIGN.md && echo "structures characterized"
# The Phase-0 gate cites the full-corpus leak-check + the fixture
grep -qiE "leak-check|expect-drift|shape_markov" docs/planning/EPIC_4/SPRINT_37/MARKOV_DISCRIMINATOR_DESIGN.md && echo "gate specified"
# The Phase-0 issue skeleton exists with the 4 subsections
grep -c '^### ' docs/issues/ISSUE_1110_markov-sigma-sp-discriminator.md   # expect 4
# The banked emission fingerprint is reproducible (from Task 2)
test -f docs/planning/EPIC_4/SPRINT_36/MARKOV_OFFDIAGONAL_DESIGN.md && echo "emission design banked"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_37/MARKOV_DISCRIMINATOR_DESIGN.md` — the three-structure (markov/sroute/cesam) derivative-shape characterization, the discriminating predicate (against IR node types), the hook point in `_add_indexed_jacobian_terms`, the Phase-0 acceptance gate (harness + full-corpus leak-check + fixture), and the REPLAN exit
- `docs/issues/ISSUE_1110_markov-sigma-sp-discriminator.md` — the Phase-0 acceptance-gate skeleton (4 `### ` subsections), authored before the src commit
- The `shape_markov_diagonal_kronecker` fixture spec (fail-before/pass-after), to land with the fix under P7
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.2, 1.3, 1.4, 1.5

### Acceptance Criteria

- [x] The three off-diagonal derivative structures (markov genuine, sroute conditional-constant, cesam variable-bilinear) characterized at the IR/AST level
- [x] A discriminating predicate designed that is TRUE for markov and FALSE for both leak structures, specified against concrete IR node types
- [x] The hook point in `_add_indexed_jacobian_terms` identified; composition with the diagonal-Kronecker path confirmed non-disturbing to the 63+30 matches
- [x] The Phase-0 gate cites `kkt_residual.py markov` → CASE_A + cold match 2401.577 AND `make leak-check MODEL=markov` (only markov drifts full-corpus)
- [x] `docs/issues/ISSUE_1110_markov-sigma-sp-discriminator.md` Phase-0 skeleton created with 4 `### ` subsections
- [x] The REPLAN exit documented (narrower per-signature allowlist fallback if the predicate over-generalizes)
- [x] Unknowns 1.2, 1.3, 1.4, 1.5 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 5: ganges/gangesx P2 — ≥5-Blocker Cascade Re-Verification & Recovery Sequencing

**Status:** ✅ COMPLETE (2026-08-10)
**Priority:** High
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 37 Day 1
**Owner:** Sprint 37 execution team
**Dependencies:** Tasks 1, 2 (the re-confirmed ganges cascade fingerprint)
**Unknowns Verified:** 2.2, 2.3, 2.4

### Objective

Re-verify that the Sprint-36 ganges/gangesx cascade fixes (`$141`/`$145`/`$149`) still apply on current `main`, characterize the two terminal blockers (`$66` cold, `rPower` presolve) sharply enough to bound whether the +2 recovery is landable in the sprint, and sequence the atomic recovery so a partial never churns goldens for 0 bucket.

### Why This Matters

ganges/gangesx is the sprint's +2-or-0 bimodal bucket lever (P2). The cascade fixes are VERIFIED but the recovery is *atomic* — landing `$141`/`$145`/`$149` without also clearing `$66` and `rPower` produces 0 bucket plus golden churn. The prep phase must decide, before Day 1, whether `rPower` (*presumed* at planning time to be the #1378/#1424 embedded-NLP-divergence deep class — **the Result refuted this**) is tractable within the sprint or whether P2 should be scoped to "land the general `$149` fix (which also unblocks the dinam/indus/turkpow/clearlak `$149` halves) and document the `$66`/`rPower` residual."

### Background

Day 8 (`DAY8_P4_GANGES_BANK.md`): the corrected `$141` helper (`_expr_contains_varref_attribute`) + the `$149` `_diff_prod` §5 patch (git `a8ff626c` + `SPRINT_35/DAY3_P4_BANK_CARRYFORWARD.md` §5) drive the cold compile's `$141`/`$145`/`$149` count → 0. Terminals: `$66` ×17 (cold — presolve-gated calibration params unassigned-but-referenced in stationarity; carries the `ac(i+2,r)` match-correctness risk) and `rPower` (presolve — the `.l`-based power calibrations `k(i)**(-rhos(i))` re-run non-idempotently under the presolve `$onMultiR` `$include`, producing `x**y, x=0, y<0` at generation). `GANGES_RECOVERY_SEQUENCING.md` (Sprint 36) holds the banked sequencing. The 335s slow-emit goldens need a nightly regen slot.

> **⚠ Superseded by this task's Result (2026-08-10).** The `rPower` attribution above is the *pre-execution* characterization carried from Sprint 36. Measurement refuted it: `rPower` is a bounded emit-**ordering** bug (the deferred `.l`-dependent bound block is emitted *before* the `$include` that assigns those `.l` values), not the #1378/#1424 non-idempotent-`$onMultiR` class. The genuine #1378/#1424 divergence sits one level behind it (embedded NLP **MS-5** vs standalone **MS-2 @ 6395.5444**). See the Result section and `GANGES_RECOVERY_DESIGN.md` §3–§4.

### What Needs to Be Done

1. **Re-apply the cascade fixes on current `main`** (in a `/tmp` copy) and confirm `$141`/`$145`/`$149` → 0 for both ganges AND gangesx (the git `a8ff626c` + `_diff_prod` §5 recipe from Task 2).
2. **Characterize `$66` sharply:** which calibration params are unassigned-but-referenced in stationarity, why the presolve gate leaves them cold, and whether assigning them (or guarding the reference) is a bounded emit fix or a deeper divergence. Quantify the `ac(i+2,r)` match-correctness risk (does a naive fix change the matched solution?).
3. **Characterize `rPower` sharply:** test (do not assume) the #1378/#1424 attribution — *this hypothesis was **refuted**; see the Result* — and assess whether an NA-guard-style emit fix (cf. the P7 robustlp `.L`-guard idiom) or a re-declaration-reset could break the non-idempotency, or whether it needs the deep embedded-NLP-divergence treatment (out of a bounded sprint fix).
4. **Sequence the atomic recovery:** define the exact order (cascade fixes → `$66` → `rPower`) and the per-step Phase-0 gate: per-model (ganges AND gangesx) emit → compile → count `$NNN` (assert 0) → solve cold AND presolve (`modelstat` asserted) → bucket → match; each step `--resolve-changed`-gated; determinism ×3; the 335s goldens on a nightly slot.
5. **Bound the sprint outcome:** decide the P2 target — full +2 (if `$66`/`rPower` look bounded) or "general `$149` fix + documented `$66`/`rPower` residual" — and note the dinam/indus/turkpow/clearlak `$149`-half spillover either way.

### Changes

Applied the banked cascade fixes to a scratch `src/` (git `a8ff626c` `$141`/`$145` with the **corrected** `_expr_contains_varref_attribute` helper + the `$149` `_diff_prod` §5 patch at `derivative_rules.py:3410`), emitted **all four** artifacts (ganges/gangesx × cold/presolve — 293/284/259/262 s), compiled each under GAMS 54.2.1, ran the presolve MCPs to generation, and ran three `/tmp` controls (two rPower-elimination variants + a raw-source reference). **Reverted the scratch `src/`** (byte-identical to `main`; `stationarity.py`/`derivative_rules.py` byte-identical to the anchor). Produced `docs/planning/EPIC_4/SPRINT_37/GANGES_RECOVERY_DESIGN.md`. Advanced Unknowns 2.2, 2.3, 2.4 → ✅ VERIFIED.

### Result

**Cascade re-verified on both models; both terminals re-characterized — and both are corrections to the bank.** (1) **Cascade:** with the fixes applied, ganges *and* gangesx cold compiles drop `$141`/`$145`/`$149` to **0** (only `$66` remains), and both presolve MCPs compile **rc=0 clean**. (2) **`$66` — bounded, but the bank's fix was wrong:** exactly **16** symbols; every `.l` feeding them is *data-initialized* (`:557–745`) and the only `solve` is at **:1150**, *after* the calibration block — so they are computable cold and the fix is to **emit the real assignments**. The bank's proposed `param(domain)=0` default would degenerate CES/LES share/scale parameters, compiling a *different model* that could not legitimately match. (3) **A second cold blocker surfaced:** `ac(i+2,r)` in `stat_pc(i)` is **still present** with `$149` applied — a spurious index offset on a data Table (the same `_compute_index_offset_key` family as markov's `σ=sp`); it compiles, so the `$NNN` protocol is blind to it, but it corrupts `stat_pc` ⇒ a match-correctness blocker beyond `$66`. (4) **`rPower` is NOT the deep #1378/#1424 class:** the failing object is the *equation* `prods(i)`, whose `ls(i)**(-rhos(i))` is evaluated at a **zero variable level** because nlp2mcp hoists the source's `.l`-dependent bound statements into a "Deferred Variable Bounds" block emitted **before** the `$include` that assigns those `.l`s (source order 593→1071; emitted order 484→515, inverted). **Two independent controls** — move the block, or delete it — both take the full run from **rc=3 to rc=0** with `rPower` gone; the emitter already has both halves of the pattern (#1378 skip, #1449 post-include correction pass), so this is a bounded fix, not research. (5) **The real deep blocker is one level behind it:** with `rPower` removed, the embedded `ganges0` solves **MS-5 Locally Infeasible @ −386785.5** while the raw source standalone solves **MS-2 Locally Optimal @ 6395.5444** (reference control) — *that* is the genuine embedded-NLP divergence, previously masked. **Bounded P2 outcome: 0 bucket in-sprint** (unchanged verdict, better-understood reason) — 2 of 5 blockers are now bounded and specified, 2 remain deep, and +2 needs all five.

### Verification

```bash
# The banked recovery-sequencing doc + the cascade-fix recipe exist
test -f docs/planning/EPIC_4/SPRINT_36/GANGES_RECOVERY_SEQUENCING.md && echo "sequencing banked"
test -f docs/planning/EPIC_4/SPRINT_35/DAY3_P4_BANK_CARRYFORWARD.md && echo "diff_prod patch banked"
# The cascade fix commit is reachable
git cat-file -t a8ff626c 2>/dev/null && echo "a8ff626c reachable"
# The prep design bounds the +2-or-0 outcome + names the terminals
grep -qiE "\\\$66|rPower|atomic" docs/planning/EPIC_4/SPRINT_37/GANGES_RECOVERY_DESIGN.md && echo "terminals characterized"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_37/GANGES_RECOVERY_DESIGN.md` — the re-verified cascade-fix status on current `main`, the sharpened `$66` and `rPower` characterizations (bounded-fix vs deep-class verdict), the atomic recovery sequence with per-step Phase-0 gates, and the bounded P2 outcome (+2 target or `$149`-fix-plus-residual)
- Updated dispositions in `KNOWN_UNKNOWNS.md` for the ganges unknowns
- The dinam/indus/turkpow/clearlak `$149`-half spillover noted for P6's residual cohort
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.2, 2.3, 2.4

### Acceptance Criteria

- [x] `$141`/`$145`/`$149` re-confirmed → 0 on current `main` for both ganges and gangesx
- [x] `$66` characterized (which params, the presolve-gate mechanism, the `ac(i+2,r)` match risk quantified) with a bounded-fix vs deep verdict
- [x] `rPower` characterized with a bounded-fix vs deep verdict — **verdict: BOUNDED, and the #1378/#1424 attribution was wrong.** Root is an emit-ordering bug (the deferred `.l`-dependent bound block emitted before the `$include` that assigns those `.l`s), eliminated by two independent controls; the genuine #1378/#1424 divergence sits one level behind it (embedded MS-5 vs standalone MS-2)
- [x] The atomic recovery sequence defined with per-step Phase-0 gates (per-model emit→compile→count→solve cold+presolve→bucket→match; `--resolve-changed`; determinism ×3; 335s goldens nightly)
- [x] The P2 sprint outcome bounded (+2 target OR general `$149` fix + documented residual), with the `$149`-half spillover to the residual cohort noted
- [x] Unknowns 2.2, 2.3, 2.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 6: fawley P4 — Emission-Path Location & Constraint-Index-Diagonal Discriminator Design

**Status:** ✅ COMPLETE (2026-08-10)
**Priority:** High
**Estimated Time:** 4-6 hours
**Deadline:** Before Sprint 37 Day 1
**Owner:** Sprint 37 execution team
**Dependencies:** Tasks 1, 2 (the re-confirmed fawley `stat_bq` control), 3 (the leak gate), 4 (the markov discriminator — they share `_add_indexed_jacobian_terms` and must co-exist)
**Unknowns Verified:** 4.1, 4.2, 4.4

### Objective

Locate the actual `qsb`/`pbal` emission path (which the Day-4 attempt found ≠ the design's assumed partial-overlap branch), design the rebuilt constraint-index-diagonal orientation predicate + discriminator that ships the confirmed `stat_bq` correction (473→1.14e-13), and verify it composes with the P1 markov change in the shared `_add_indexed_jacobian_terms` without leaking full-corpus.

### Why This Matters

fawley P4 is 0-bucket (H-b — the `--force` survey was NEGATIVE, so the +Solve is a Sprint-38 consultation, not this sprint), but the `stat_bq` correctness fix is confirmed and advances #1111/#1112. Critically, fawley and markov (P1) both modify the high-blast-radius shared `_add_indexed_jacobian_terms` — the Sprint-35 precedent is the fawley Day-9 leak *onto* markov. Designing the two predicates together in prep, both gated by the full-corpus leak harness (Task 3), is the only way to avoid a mid-sprint collision. This task must follow Task 4 so the markov predicate is fixed before fawley's is layered on.

### Background

Day 4 (`DAY4_FAWLEY_DEFER.md`): the `stat_bq` `sameas` correction drives `max|stat_bq|` 473→1.14e-13 (hand-edit, reproduces on byte-identical goldens) — correctness confirmed. But the Day-4 implementation revealed the `qsb`/`pbal` terms emit via a path **≠** the design's assumed partial-overlap branch, and the S35 constraint-index-diagonal orientation predicate is reverted/absent. `FAWLEY_DISCRIMINATOR_DESIGN.md` (Sprint 36) holds the banked discriminator design. The `--force` survey (Day 11, `DAY11_P5_CONSULTATION.md` §4) was NEGATIVE (homotopy/multistart/optfile all leave fawley MS-5) → the +Solve is a stronger-continuation question for the Sprint-38 PATH consultation.

### What Needs to Be Done

1. **Locate the `qsb`/`pbal` emission path.** Trace where these constraint terms actually reach `_add_indexed_jacobian_terms` (the path the Day-4 attempt found is not the design's partial-overlap branch) — identify the real branch and why the S35 orientation predicate no longer fires there.
2. **Rebuild the constraint-index-diagonal orientation predicate.** Re-specify the predicate that identifies fawley's constraint-index-diagonal structure at the located emission path, against current-tree IR node types.
3. **Layer the discriminator + confirm markov co-existence.** Design the fawley predicate to fire only on fawley's structure; verify (on paper against Task 4's markov predicate) that the two predicates are mutually exclusive in `_add_indexed_jacobian_terms` — neither fires on the other's model. This is the collision-avoidance step.
4. **Design the Phase-0 gate:** the discriminator drives `max|stat_bq| → 0`; `make leak-check MODEL=fawley` (Task 3) shows **only fawley drifts** full-corpus (markov + the 2-D cohort byte-identical); the `shape_fawley_2d_second_index` fixture fails-before/passes-after.
5. **Write the Phase-0 issue doc skeleton** (`docs/issues/ISSUE_1111_fawley-constraint-index-diagonal.md`, 4 `### ` subsections) before the src commit.
6. **Scope the +Solve hand-off:** frame the stronger-continuation/reformulation question for the Sprint-38 PATH consultation (the `--force` survey was NEGATIVE); note it is NOT a Sprint-37 emit fix.

### Changes

Instrumented `_add_indexed_jacobian_terms` to locate the `qsb`/`pbal` emission path (the Day-4 blocker), implemented the rebuilt orientation predicate in a scratch `src/`, verified the correctness target via `kkt_residual.py`, and ran **two full-corpus `make leak-check MODEL=fawley` sweeps** (Task 3's gate, first production use). **Reverted the scratch `src/`** (`stationarity.py` byte-identical to the anchor). Produced `FAWLEY_DISCRIMINATOR_REFRESH.md` + the Phase-0 doc `docs/issues/ISSUE_1111_fawley-constraint-index-diagonal.md` (4 `###` subsections) + the `shape_fawley_2d_second_index` fixture spec. Advanced Unknowns 4.1, 4.4 → ✅ VERIFIED and 4.2 → 🔶 PARTIAL.

### Result

**The path is located and the fix works — but the leak gate refused it, twice.** **(4.1, the Day-4 blocker — CLOSED)** instrumentation shows both `qsb` and `pbal` take the **"truly disjoint by NAME"** branch (`:7069–7096`), falling to `Sum(mult_domain, …)` at `:7096` with `dual_binding=None`. Root: the branch tests overlap **by name** and `cfq ∉ {c,cf}`, but `cfq` is **declared a subset of `cf`** — so it is not independent and the whole-domain sum over-counts. The handling already exists on the *scalar* branch (#1393 `_subset_alias_superset_index`, whose comment names fawley); it is absent from the indexed one. Two competing hypotheses were tested and rejected. **(Correctness — VERIFIED in `src/`)** the rebuilt predicate takes `stat_bq`'s `sameas` count **1 → 3** and removes `stat_bq` from the KKT residuals entirely (baseline rel 0.973) — the Day-9 target reached by a real code change, not a hand-edit. **(4.2 — markov co-existence ✅, leak-freedom ❌)** the two fixes are structurally exclusive in **both** directions (fawley's branch is under `elif not _did_dim_mismatch_alias_fix:` `:7060`; markov's path *sets* that flag `:6925` — and fawley has no aliases). **But `make leak-check MODEL=fawley` reported `LEAK: dinam, prolog, shale`**, and after adding the S36 discriminator as conjunct 2, still **`LEAK: dinam, shale`**. **`prolog` is a live `model_optimal` + *match* model**, so v1 could have cost a Match — and **all three leak models are outside the Sprint-36 6-model cohort**, i.e. a cohort-only check would have shown clean and shipped it. **(4.4)** with `stat_bq` corrected the harness max is still the emit-correct `stat_trans(tr-2)` rel 1.00 and the MCP stays MS-5; with S36's NEGATIVE `--force` survey this is **0 bucket by construction**. **Disposition: still deferred, but the remaining work is bounded** — narrow conjunct 2 (its name-based test misses the AD layer's `__`-suffixed re-symbolization), then re-run to an unqualified `LEAK GATE PASS`.

### Verification

```bash
# The design doc locates the emission path + specifies co-existence with markov
grep -qiE "qsb|pbal|emission path" docs/planning/EPIC_4/SPRINT_37/FAWLEY_DISCRIMINATOR_REFRESH.md && echo "path located"
grep -qiE "co-exist|mutually exclusive|markov" docs/planning/EPIC_4/SPRINT_37/FAWLEY_DISCRIMINATOR_REFRESH.md && echo "collision addressed"
# The Phase-0 gate cites the full-corpus leak-check + the fixture
grep -qiE "leak-check MODEL=fawley|shape_fawley" docs/planning/EPIC_4/SPRINT_37/FAWLEY_DISCRIMINATOR_REFRESH.md && echo "gate specified"
# The Phase-0 issue skeleton exists
grep -c '^### ' docs/issues/ISSUE_*fawley-constraint-index*.md 2>/dev/null   # expect >= 4
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_37/FAWLEY_DISCRIMINATOR_REFRESH.md` — the located `qsb`/`pbal` emission path, the rebuilt orientation predicate, the fawley/markov mutual-exclusion analysis (collision avoidance), the Phase-0 gate (`max|stat_bq|→0` + `make leak-check MODEL=fawley` + fixture), and the Sprint-38 +Solve consultation hand-off
- `docs/issues/ISSUE_1111_fawley-constraint-index-diagonal.md` — the Phase-0 acceptance-gate skeleton (4 `### ` subsections)
- The `shape_fawley_2d_second_index` fixture spec (fail-before/pass-after), to land with the fix under P7
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.2, 4.4

### Acceptance Criteria

- [x] The actual `qsb`/`pbal` emission path located (the branch the Day-4 attempt found, ≠ the design's partial-overlap assumption)
- [x] The constraint-index-diagonal orientation predicate rebuilt against current-tree IR node types
- [x] The fawley/markov predicate mutual-exclusion confirmed on paper (neither fires on the other's model in the shared `_add_indexed_jacobian_terms`)
- [x] The Phase-0 gate cites `max|stat_bq|→0` AND `make leak-check MODEL=fawley` (only fawley drifts) AND the `shape_fawley_2d_second_index` fixture
- [x] `docs/issues/ISSUE_1111_fawley-constraint-index-diagonal.md` Phase-0 skeleton created (4 `### ` subsections)
- [x] The +Solve hand-off scoped for the Sprint-38 PATH consultation (H-b; NOT a Sprint-37 emit fix)
- [x] Unknowns 4.1, 4.2, 4.4 verified (4.2 → 🔶 PARTIAL: leak-freedom refuted, documented) and updated in KNOWN_UNKNOWNS.md

---

## Task 7: sarf P5 — Symbolic-Emit Re-Architecture Design Refresh & Blow-Up Re-Measurement

**Status:** ✅ COMPLETE (2026-08-10)
**Priority:** High
**Estimated Time:** 4-5 hours
**Deadline:** Before Sprint 37 Day 1
**Owner:** Sprint 37 execution team
**Dependencies:** Tasks 1, 2 (the re-confirmed sarf blow-up fingerprint)
**Unknowns Verified:** 5.2, 5.3

### Objective

Refresh the sarf symbolic-emit re-architecture design against current `main`, re-measure the 369K-column blow-up, and specify the atomic re-arch of the `enumerate_variable_instances` → column-index → Jacobian → gradient → stationarity flow (6 call sites) as an O(active=398) symbolic/parametric emit MODE — including the full-corpus regression-harness precondition (Task 3) without which it cannot land.

### Why This Matters

sarf P5 is the lowest-leverage track (+1 Translate, never displaces a bucket track), but it is thrice-carried and the 20–28h atomic re-arch has **no bounded control** — the timing measurement requires the full re-arch, and it is **not landable without the full-corpus regression harness first** (the byte-stable proof that the symbolic-branch predicate is sarf-only). The prep phase must confirm the blow-up is still live, refresh the 6-call-site design against the current tree, and make the P7-harness dependency explicit so the sprint doesn't attempt sarf before the harness (Task 3) is wired.

### Background

Day 6 (`DAY6_SARF_BANK.md`): the blow-up re-confirmed non-terminating (>100s cap; O(369,024) `task` columns). `SARF_DESIGN_REFRESH.md` (Sprint 36) holds the banked design. The re-arch touches 6 call sites across 142 models; the O(active=398) guarded-emit form is validated in principle but the re-emit must be O(active), not O(369K), and byte-stable. This is a PR20-style deep AD/emit re-architecture.

### What Needs to Be Done

1. **Re-measure the blow-up** on current `main` (in a `/tmp` copy): confirm the sarf emit still exceeds the 100s cap and record the column count (expect ~369,024) — the DRIFTED/VERIFIED disposition for the Task-1 sarf unknown.
2. **Refresh the 6-call-site inventory:** re-locate `enumerate_variable_instances` → column-index → Jacobian → gradient → stationarity in the current tree; note any drift since the banked design.
3. **Specify the O(active=398) symbolic/parametric emit MODE:** how the emit iterates active instances (398) rather than materializing the full 369K column space, and how `stat_task` reproduces the banked 7-term derivation symbolically.
4. **Make the P7-harness precondition explicit:** the re-arch lands only after the full-corpus regression harness (Task 3) is wired — the byte-stable proof that the symbolic-branch predicate fires on sarf only. Document the ordering dependency (sarf after the P7 harness, not before).
5. **Design the Phase-0 gate (PR20):** the re-emit is O(active=398), not O(369K) — `sarf_mcp.gms` completes in single-digit seconds; `stat_task` matches the banked 7-term derivation; atomic; byte-stable golden; determinism ×3; the full-corpus `--resolve-changed` regression.
6. **Define the REPLAN exit:** if the parametric emit re-triggers the timeout or the symbolic-branch predicate is not sarf-only, document the re-scoping (sarf stays banked; +1 Translate deferred).

### Changes

Re-measured the blow-up on current `main` (capped emit), re-counted sarf's set cardinalities live, re-located the 6 `enumerate_variable_instances` call sites and re-checked the 3 materialization-site files against the anchor, compiled the O(active) guarded-emit shape under GAMS 54.2.1 **at sarf's real 369,024 scale**, and established the corpus-safety gate sarf actually needs. No `src/` change (a `/tmp` GAMS compile only). Produced `docs/planning/EPIC_4/SPRINT_37/SARF_REARCH_REFRESH.md`. Advanced Unknowns 5.2, 5.3 → ✅ VERIFIED.

### Result

**Every premise of the banked design re-confirms, and two findings are sharper than the bank.** **(Blow-up)** the capped emit is **`>330s / NON-TERMINATING at cap (330.2s)`** — identical in kind to the S35/S36 baselines (no improvement, no regression); counts re-verified live (`|g|`=16, `|t|`=24, `|mn|`=31 ⇒ **369,024** declared / 398 active, both guards runtime-computed). **(Sites)** the "3 sites vs 6 call sites" apparent discrepancy is **not a contradiction** — 3 *materialization* sites (S1/S2/S3, the surfaces to short-circuit) vs 6 *`enumerate_variable_instances` call sites* (the corpus-safety surface traversed by all 142 models); all 6 re-located live and the 3 site files are byte-unchanged since the anchor, so **no fourth site**. **(5.2 — stronger than S36)** S36 validated the guarded emit on a *synthetic* 54-cell analogue; this task compiled it under GAMS 54.2.1 with sarf's **actual cardinalities**: **`rc=0`, 0 errors, `ncart` = 369,024** (exactly sarf's Cartesian), instantiation restricted to the guard domain (46,128) then the live set (96) — the shape is valid **at the size that actually breaks**. **(5.3 — a correction the bank did not carry)** the P7 precondition is satisfied *today* (Task 3's harness is on `main`), **but `make leak-check MODEL=sarf` cannot work**: sarf has **no golden** (0 files; `translate: failure`), so `--expect-drift sarf` reports `NO-OP` and fails for a non-correctness reason. **sarf's gate is the inverse assertion — `make check-goldens` showing ZERO drift across all 163, plus sarf newly producing a golden.** Recorded because running the P1/P4 recipe here would produce a confusing false failure. **Disposition unchanged:** a 20–28h atomic re-architecture for the lowest-leverage bucket (+1 Translate) — the fifth consecutive deferral; everything needed to implement it exists, and the case against doing it in-sprint is risk/reward, not readiness.

### Verification

```bash
# The banked sarf design + the blow-up recipe exist
test -f docs/planning/EPIC_4/SPRINT_36/SARF_DESIGN_REFRESH.md && echo "sarf design banked"
test -f docs/planning/EPIC_4/SPRINT_36/DAY6_SARF_BANK.md && echo "blow-up recipe banked"
# The refreshed design names the 6 call sites + the O(active) target + the P7 precondition
grep -qiE "enumerate_variable_instances|O\(active|369" docs/planning/EPIC_4/SPRINT_37/SARF_REARCH_REFRESH.md && echo "re-arch specified"
grep -qiE "full-corpus|regression harness|P7" docs/planning/EPIC_4/SPRINT_37/SARF_REARCH_REFRESH.md && echo "harness precondition noted"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_37/SARF_REARCH_REFRESH.md` — the re-measured blow-up (column count + timing), the refreshed 6-call-site inventory, the O(active=398) symbolic/parametric emit MODE spec, the explicit P7-harness precondition + ordering, the Phase-0 gate (PR20), and the REPLAN exit
- Updated disposition in `KNOWN_UNKNOWNS.md` for the sarf blow-up unknown
- The sarf-after-P7-harness ordering dependency flagged for the Task-11 schedule
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.2, 5.3

### Acceptance Criteria

- [x] The 369K blow-up re-measured on current `main` (>100s cap confirmed; column count recorded)
- [x] The 6 call sites re-located in the current tree (drift noted)
- [x] The O(active=398) symbolic/parametric emit MODE specified (active-instance iteration; symbolic `stat_task` 7-term reproduction)
- [x] The full-corpus-regression-harness (P7) precondition made explicit with the sarf-after-harness ordering
- [x] The Phase-0 gate (PR20) defined (O(active) not O(369K); single-digit-second emit; byte-stable; determinism ×3; full-corpus regression)
- [x] The REPLAN exit documented (re-scope if the parametric emit re-triggers the timeout)
- [x] Unknowns 5.2, 5.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 8: GAMS-54 v54 Re-Baseline Harness Plan + turkey Testbed Procurement (P6)

**Status:** ✅ COMPLETE (2026-08-10)
**Priority:** Medium
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 37 Day 1
**Owner:** Sprint 37 execution team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 6.1, 6.2, 6.3

### Objective

Plan the two P6 deliverables: (a) the full GAMS-54 v54 re-baseline of the 142 candidates (demo-runnable) with the v53→v54 bucket-diff and the canonical-version decision procedure, and (b) the turkey +1 realization, which needs a licensed >1000-row GAMS-54 testbed (turkey's MCP is 3,866 rows) — including procuring or confirming the absence of such an environment.

### Why This Matters

Sprint 36 kept the v53(51.3.0) KPIs pending a full v54 re-baseline showing zero bucket regressions; that re-baseline is now a P6 deliverable and its procedure must be planned so Day 1 can execute a demo re-solve, not design one. turkey's +1 is the sole externally-gated bucket move — no licensed >1000-row GAMS-54 testbed exists (local + CI both demo), so the prep phase must either procure one or document turkey as license-gated so the sprint doesn't burn time re-discovering the limit.

### Background

`GAMS54_TESTBED_PLAN.md` (Sprint 36) §3 (turkey testbed) + §4 (the re-baseline decision) hold the banked plan; `SPRINT_35/FOLLOWUPS_GAMS54_TRANSITION.md` holds the v53→v54 transition context (the demo license expired ~2026-07-29; local/CI bumped to 54.2.1; v54 is stricter — 5 OBJ-GAP models). The 142-candidate solving set is demo-solvable (the baseline is demo-built), so the re-baseline itself runs on demo; only turkey's 3,866-row MCP exceeds the 1000-row demo limit. P7 already restored robustlp's v54 solvability (one v53→v54 gap closed).

### What Needs to Be Done

1. **Plan the v54 demo re-baseline procedure:** the exact `run_full_test.py` invocation to re-solve the 142 candidates under GAMS 54 demo, the bucket-diff against the v53 DB, and the re-check of the 5 OBJ-GAP models (agreste/cesam/chain/fawley/rocket). Define the output: `GAMS54_REBASELINE_DIFF.md`.
2. **Define the canonical-version decision rule:** re-pin the DB to v54 only on confirmed **zero bucket regressions**; otherwise keep v53 and document the regressions. Specify what "regression" means (a bucket downgrade vs a neutral churn).
3. **turkey testbed procurement:** determine whether a licensed >1000-row GAMS-54 environment is procurable in the sprint window (a licensed local install, a cloud GAMS, or a CI secret). If yes, plan the turkey re-solve; if no, document turkey as license-gated (+1 deferred) with the exact blocker.
4. **Scope the residual multi-root cohort:** turkpow (ragged `Table mdatat`) / clearlak (dynamic sets) / dinam / indus — note that the P2 general `$149` fix unblocks their `$149` half, and flag which (if any) is a bounded per-model effort for the sprint tail.

### Changes

Probed every licensed-testbed path (three local GAMS installs + CI secrets), compiled turkey's committed MCP under GAMS 54.2.1 to measure its row count and exact refusal, **live re-solved all 5 OBJ-GAP models under v54** (DB snapshotted → mutated → **restored byte-identical**, md5 verified), measured per-model re-solve cost, and specified the re-baseline procedure + a three-way decision rule. No `src/` change; DB unchanged. Produced `docs/planning/EPIC_4/SPRINT_37/GAMS54_REBASELINE_PLAN.md`. Advanced Unknowns 6.1 → ❌ WRONG (refuted), 6.2 → 🔶 DESIGN-VERIFIED, 6.3 → ✅ VERIFIED.

### Result

**turkey is definitively license-gated; the v54 risk set is clean; and the re-baseline is far cheaper than assumed.** **(6.1 — REFUTED)** all three local GAMS installs (51/53/**54.2.1**) are `GAMS_Demo` and CI holds only `PYPI_API_TOKEN` — **no licensed >1000-row environment exists or is procurable from the repo**. turkey measured: **3,866 single equations / 3,753 variables**, the exact refusal *"exceeds the demo license limits for nonlinear models of more than 1000 rows or columns"*, and — critically — a compile that is **otherwise clean (zero `$NNN`)**. So the S35 `$161` recovery worked and **the license is the only blocker**: the +1 is real but unrealizable. **(Bonus, no bank carried it)** turkey's DB row is **stale** — `path_syntax_error` dated **2026-06-20**, seven weeks *before* the `$161` fix landed — because `--resolve-changed` deliberately never persists (`run_full_test.py:1267`). A persisting re-solve moves turkey `path_syntax_error → path_solve_license`, i.e. **pse 7 → 6 with no Solve/Match change**. **(6.3 — VERIFIED, none shift)** all 5 OBJ-GAP models re-solved under v54 are **identical**, with chain's objectives **byte-identical** (5.0723 / 5.1199) — zero bucket changes and not even numerical drift on the named risk set. **(6.2 — procedure + rule)** measured cost **~12 s/model ⇒ ~30 min for all 142** — not a blocker. The decision rule needs **three** categories, not two: *Regression* (a v54-attributable downgrade — blocks the re-pin), *neutral churn*, and **stale-entry correction** (the v53 row predates a landed fix — **turkey is exactly this**), which would otherwise be miscounted as a spurious v54 effect. **Re-pin only on zero Regressions.** Also surfaced: the DB records `"solver_version": null` for all 219 rows — no per-row version provenance, which is why this can only be answered by re-running; the re-baseline should populate it. **P6 verdict: turkey NO-GO (license); re-baseline GO (cheap, low-risk); residual cohort no in-sprint effort** (`$149` necessary-not-sufficient, and `dinam` overlaps the open fawley track).

### Verification

```bash
# The banked testbed plan exists
test -f docs/planning/EPIC_4/SPRINT_36/GAMS54_TESTBED_PLAN.md && echo "testbed plan banked"
test -f docs/planning/EPIC_4/SPRINT_35/FOLLOWUPS_GAMS54_TRANSITION.md && echo "v54 transition banked"
# The prep plan specifies the re-baseline invocation + the decision rule
grep -qiE "resolve-changed|run_full_test|zero.*regression" docs/planning/EPIC_4/SPRINT_37/GAMS54_REBASELINE_PLAN.md && echo "procedure specified"
# GAMS version is 54.x locally
gams --version 2>/dev/null | head -1 || echo "gams not on PATH (CI/testbed only)"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_37/GAMS54_REBASELINE_PLAN.md` — the v54 demo re-baseline procedure (invocation + bucket-diff + OBJ-GAP re-check), the canonical-version decision rule (re-pin only on zero regressions), the turkey testbed procurement verdict (procurable → plan / not → license-gated), and the residual-cohort scoping
- Updated dispositions in `KNOWN_UNKNOWNS.md` for the turkey/GAMS-54 unknowns
- A go/no-go on turkey's +1 for the sprint (testbed available vs deferred)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 6.1, 6.2, 6.3

### Acceptance Criteria

- [x] The v54 demo re-baseline procedure specified (invocation, bucket-diff vs v53 DB, 5-OBJ-GAP re-check, `GAMS54_REBASELINE_DIFF.md` output)
- [x] The canonical-version decision rule defined (re-pin to v54 only on zero bucket regressions; else keep v53)
- [x] The turkey testbed procurement verdict recorded (procurable → re-solve plan; not → license-gated with the exact blocker)
- [x] The residual multi-root cohort scoped (`$149`-half spillover from P2; any bounded per-model tail effort flagged)
- [x] Unknowns 6.1, 6.2, 6.3 verified (6.1 → ❌ WRONG/refuted, 6.2 → 🔶 DESIGN-VERIFIED, 6.3 → ✅) and updated in KNOWN_UNKNOWNS.md

---

## Task 9: Consultation Reply-Integration Prep (rocket/mine P3) + camcge Epic-5 Walras Gate Scoping

**Status:** ✅ COMPLETE (2026-08-10)
**Priority:** Medium
**Estimated Time:** 2-3 hours
**Deadline:** Before Sprint 37 Day 1
**Owner:** Sprint 37 execution team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 3.1, 3.2, 3.3, 3.4

### Objective

Prepare the P3 consultation cycle: stage the integration of the PATH authors' reply to the rocket #1462 submission (map the recommended option-set into `--force homotopy`), track the mine primal-degenerate-LP question, and scope the camcge three-part dual-consistent Walras redefinition as the Epic-5 gate (with the per-model-numéraire fallback).

### Why This Matters

The rocket +1 Solve is contingent on the PATH authors' reply, which arrives on an external timeline; staging the integration in prep means the sprint can act on the reply immediately rather than designing the integration cold. camcge is Epic-5-scoped (the two-nullspaces diagnosis: numéraire alone is insufficient), so the prep phase must scope the Walras prototype as an Epic-5 deliverable — not a Sprint-37 bucket move — to keep the sprint's bucket expectations honest.

### Background

Day 11 (`DAY11_P5_CONSULTATION.md` + `CONSULTATION_BUNDLE.md`): the rocket FINALIZED input (`SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`) was submitted; the reply's recommended option-set/continuation schedule plugs into `--force homotopy` (+1 contingent). The Case-c sign flip stays BANNED. mine #1443: the primal-degenerate-LP question is posed; the only non-invariant lever is an LP-side reformulation (out of emit scope) → 0 bucket; `x.up=inf` stays BANNED. camcge #1330: the Walras `/tmp` control (641 rows, demo-reachable) confirmed MS-4 with a numéraire alone insufficient (fixes the price-scaling ray, not the row-redundancy nullspace); the full three-part redefinition (numéraire + Walras-law dual redefinition) is the Epic-5 gate (`../../EPIC_5/CGE_DEGENERACY_SCOPING.md`).

### What Needs to Be Done

1. **Stage the rocket reply integration:** document how a recommended PATH option-set / continuation schedule maps into the `--force homotopy` scaffold, so the reply (whenever it arrives) can be integrated in a bounded step; keep the Case-c sign flip BANNED. Check whether the reply has arrived (update the Task-1 unknown).
2. **Track the mine question:** confirm the primal-degenerate-LP reconciliation question (`SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md`) is posed and 0-bucket; `x.up=inf` stays BANNED. No emit fix.
3. **Scope the camcge Epic-5 Walras gate:** specify the three-part dual-consistent Walras redefinition (numéraire + the Walras-law dual redefinition, the row-redundancy fix) as a `/tmp` demo control (641 rows) targeting MS-1; expected MS-4 → the per-model-numéraire Epic-5 declaration. Frame it as an Epic-5 deliverable in `../../EPIC_5/CGE_DEGENERACY_SCOPING.md`, NOT a Sprint-37 bucket.
4. **Set the P3 expectations:** rocket +1 contingent (external reply); mine 0-bucket (tracked); camcge Epic-5 (MS-1 stretch or the per-model-numéraire finding).

### Changes

Audited whether the rocket/mine consultation submissions were actually transmitted (bundle checklist, issue #1462 comments, repo-wide grep), ran a `/tmp` camcge control under GAMS 54.2.1 to reproduce the Walras baseline, re-read the Epic-5 handoff spec against the Sprint-30/34/36 findings, and **corrected a stale prescription in that spec**. No `src/` change; DB untouched. Produced `docs/planning/EPIC_4/SPRINT_37/CONSULTATION_INTEGRATION_PREP.md` and amended `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md`. Advanced Unknowns 3.1 → ❌ WRONG (refuted), 3.2 → ✅, 3.3 → 🔶, 3.4 → ✅.

### Result

**The headline is not technical: the rocket consultation has never been sent.** **(3.1 — REFUTED)** the bundle's hand-off checklist has every *preparation* item `[x]` but its single **action** item — *"submit rocket to PATH authors; pose the mine LP-degeneracy question; run the fawley --force survey"* — **unchecked**; S36 Day-11 says "**ready to submit**"; issue #1462's only comment is the Sprint-28 bisect; a repo-wide grep finds no send or reply record. The package was **FINALIZED 2026-07-15** and its own renumbering note records the consultation slipping **S33 → S34 → S35** before retargeting to S36 — submission-ready across four sprint boundaries without transmission. The enabling wording is in the input doc: *"Submitted as part of the Sprint-36 consultation bundle"* means *packaged into the bundle*, and reads as *sent* — a misreading this sprint's own Unknown 3.1 inherited. **The +1 is contingent on sending, then on the reply; the blocker is neither technical nor PATH-author latency.** The integration staging itself is correct and bounded (option-set → `--force homotopy` μ-continuation + `optfile=1`; Case-c flip BANNED). **(3.2)** mine is **0 bucket** independent of the consultation (the S34 value-invariance proof; LP-side reformulation out of emit scope; `x.up=inf` BANNED) — though the same unchecked item means its question was never posed either; batch it with the send. **(3.3)** the camcge control reproduces exactly — emit 18 s, embedded NLP **MS-2 @ omega 191.7346**, MCP **MS-4**, **641 rows** (demo-reachable confirmed); the three-part Walras redefinition is the **Epic-5** gate and was deliberately not attempted (price-pin → MS-4, single-dual-pin → MS-4, drop-row → corrupt @ 299; 3+ sprints of variants all stayed MS-4). **(3.4 — a stale-spec defect found and fixed)** the per-model-numéraire fallback is correct and DB-confirmed narrow (camcge is the only inherent Walras singularity; irscge/lrgcge/moncge/stdcge/quocge all match) — **but `EPIC_5/CGE_DEGENERACY_SCOPING.md`, explicitly "the Epic-5 handoff spec", still prescribed the drop-one-row transformation that Sprint 30 refuted** (breaks the MCP dual → omega 299, MS-4), with **zero** refutation notes. Added a `⚠ SUPERSEDED IN PART` note carrying the refutation, the two-nullspaces diagnosis, and the current three-part formulation. **Both headline findings are the same failure mode: information that lives in sprint docs but never reaches the document that will actually be used.** **P3 contributes no Sprint-37 bucket** (rocket +1 contingent on sending / mine 0 / camcge Epic-5 / fawley +Solve → Sprint 38).

### Verification

```bash
# The banked consultation docs + the rocket input + the Epic-5 scoping exist
test -f docs/planning/EPIC_4/SPRINT_36/DAY11_P5_CONSULTATION.md && echo "consultation banked"
test -f docs/planning/EPIC_4/SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md && echo "rocket input finalized"
test -f docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md && echo "camcge Epic-5 scoping exists"
# The prep doc maps the rocket reply into --force + scopes camcge as Epic-5
grep -qiE "force homotopy|option-set" docs/planning/EPIC_4/SPRINT_37/CONSULTATION_INTEGRATION_PREP.md && echo "rocket integration staged"
grep -qiE "Epic.?5|numéraire|numeraire" docs/planning/EPIC_4/SPRINT_37/CONSULTATION_INTEGRATION_PREP.md && echo "camcge scoped Epic-5"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_37/CONSULTATION_INTEGRATION_PREP.md` — the rocket reply-to-`--force`-homotopy integration staging, the mine question tracking (0-bucket), and the camcge three-part Walras Epic-5 gate scoping (with the per-model-numéraire fallback)
- Updated dispositions in `KNOWN_UNKNOWNS.md` for the P3 unknowns (rocket reply arrived?, camcge Walras reachable?)
- The P3 bucket expectations set (rocket +1 contingent / mine 0 / camcge Epic-5)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.2, 3.3, 3.4

### Acceptance Criteria

- [x] The rocket reply integration staged (option-set → `--force homotopy` mapping documented; Case-c sign flip BANNED; reply-arrival status checked)
- [x] The mine primal-degenerate-LP question confirmed 0-bucket (and found **never posed** — same unchecked action item) (`x.up=inf` BANNED)
- [x] The camcge three-part Walras redefinition scoped as an Epic-5 `/tmp` demo control (641 rows, MS-1 target) with the per-model-numéraire fallback — explicitly NOT a Sprint-37 bucket
- [x] The P3 bucket expectations recorded (rocket +1 contingent, mine 0, camcge Epic-5)
- [x] Unknowns 3.1, 3.2, 3.3, 3.4 verified (3.1 → ❌ refuted, 3.3 → 🔶) and updated in KNOWN_UNKNOWNS.md

---

## Task 10: Property-Fixture Catalog + Phase-0-Doc-Enforcement + Genuine-Floor Tracking (P7)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 37 Day 1
**Owner:** Sprint 37 execution team
**Dependencies:** Tasks 1, 3 (the leak harness), 4 (the markov fixture spec), 6 (the fawley fixture spec)
**Unknowns Verified:** 7.2, 7.3, 7.4

### Objective

Catalog the P7 infrastructure deliverables: the property fixtures for the landed tracks (`shape_markov_diagonal_kronecker` from Task 4, `shape_fawley_2d_second_index` from Task 6), the Phase-0-doc CI enforcement check, and the genuine-floor tracking (anchor 75 → ≥76 if markov lands) + the Epic-4 `SUMMARY.md` row-37 continuation.

### Why This Matters

P7 turns the Sprint-36 process lessons into enforced infrastructure. The full-corpus leak harness (Task 3) is P7's headline, but P7 also lands the property fixtures that make P1/P4 regressions catchable, the Phase-0-doc CI check (the robustlp doc was needed under review, not before — this makes it before), and the genuine-floor tracking that records whether the markov +1 actually moved the anchor. Cataloguing these in prep — with the fixture specs already produced by Tasks 4 and 6 — means the sprint wires them alongside the landings rather than as an afterthought.

### Background

`FIXTURE_AND_HARNESS_CATALOG.md` (Sprint 36) catalogs the existing fixtures/harness instruments. CONTRIBUTING.md (392–447) defines the Phase-0 rule: any `src/{ad,kkt,emit}` change needs a `docs/issues/ISSUE_<N>_*.md` with a `## Phase 0: Acceptance Gate` (4 `### ` subsections) — the robustlp P7 landing needed this added under review (`ISSUE_1322`), the lesson being to enforce it up front. The PR25 genuine-floor tracking anchors the ramp (S36 actual 75); the Epic-4 `SUMMARY.md` groundwork gets a row per sprint.

### What Needs to Be Done

1. **Catalog the property fixtures:** consolidate the `shape_markov_diagonal_kronecker` (Task 4) and `shape_fawley_2d_second_index` (Task 6) fixture specs into the P7 catalog — each fail-before/pass-after, landing *with* its fix. Note any additional shape fixtures the landed tracks need.
2. **Design the Phase-0-doc CI enforcement:** a lint/CI check that any PR touching `src/{ad,kkt,emit}` has a `docs/issues/ISSUE_<N>_*.md` with the `## Phase 0: Acceptance Gate` heading + its 4 `### ` subsections. Specify the trigger (changed-path glob) and the failure message; draft it (wiring lands in-sprint).
3. **Specify the genuine-floor tracking update:** the PR25 recompute with the S37 anchor 75 → ≥76 if markov lands; the methodology-vs-genuine bookkeeping (markov flips methodology→genuine).
4. **Continue the Epic-4 SUMMARY.md groundwork:** draft the row-37 skeleton (theme, KPI columns, firm-landing / carryforward columns) to fill at S37 close.
5. **Cross-check with the leak harness (Task 3):** confirm the fixtures + the Phase-0 check + the leak gate compose into one coherent P7 "emit-PR gate" story for the schedule.

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# The banked fixture/harness catalog + CONTRIBUTING Phase-0 rule exist
test -f docs/planning/EPIC_4/SPRINT_36/FIXTURE_AND_HARNESS_CATALOG.md && echo "fixture catalog banked"
grep -qiE "Phase 0|Acceptance Gate" CONTRIBUTING.md && echo "Phase-0 rule in CONTRIBUTING"
# The P7 catalog names both fixtures + the Phase-0 CI check + floor tracking
grep -qiE "shape_markov|shape_fawley" docs/planning/EPIC_4/SPRINT_37/P7_INFRA_CATALOG.md && echo "fixtures cataloged"
grep -qiE "Phase-0.*CI|genuine.?floor" docs/planning/EPIC_4/SPRINT_37/P7_INFRA_CATALOG.md && echo "CI check + floor tracking specified"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_37/P7_INFRA_CATALOG.md` — the consolidated property-fixture catalog (`shape_markov_diagonal_kronecker` + `shape_fawley_2d_second_index`, fail-before/pass-after), the Phase-0-doc CI enforcement design (trigger + failure message), the genuine-floor tracking update spec (anchor 75 → ≥76 if markov lands), and the Epic-4 SUMMARY row-37 skeleton
- The coherent "emit-PR gate" story (leak harness + fixtures + Phase-0 check) for the Task-11 schedule
- Updated dispositions in `KNOWN_UNKNOWNS.md` for the P7 unknowns
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 7.2, 7.3, 7.4

### Acceptance Criteria

- [ ] Both property fixtures cataloged (`shape_markov_diagonal_kronecker`, `shape_fawley_2d_second_index`), each fail-before/pass-after, landing with its fix
- [ ] The Phase-0-doc CI enforcement designed (changed-path trigger + the `## Phase 0: Acceptance Gate` + 4-`### ` check + failure message)
- [ ] The genuine-floor tracking update specified (PR25 recompute; anchor 75 → ≥76 if markov lands; methodology→genuine bookkeeping)
- [ ] The Epic-4 SUMMARY.md row-37 skeleton drafted
- [ ] The leak harness + fixtures + Phase-0 check confirmed to compose into one coherent emit-PR gate for the schedule
- [ ] Unknowns 7.2, 7.3, 7.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 11: Plan Sprint 37 Detailed Schedule

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3-4 hours
**Deadline:** Before Sprint 37 Day 1
**Owner:** Sprint 37 execution team
**Dependencies:** All tasks (1–10)

### Objective

Create `docs/planning/EPIC_4/SPRINT_37/PLAN.md` — the day-by-day (Day 0 + Days 1–13) Sprint-37 schedule incorporating every prep-task design, with per-priority budgets, checkpoint gates (Days 5, 10), REPLAN exits, and the GO/NO-GO Day-0 readiness gate.

### Why This Matters

A comprehensive plan prevents mid-sprint surprises and ensures the seven priorities fit the 14-day / ≤168-hour budget. The Sprint-37 schedule must front-load the markov P1 discriminator (the strongest, fully-local +1 lever) so its PROCEED/REPLAN surfaces early (as Sprint 36 front-loaded markov to Day 2), sequence fawley P4 *after* markov P1 (shared function), sequence sarf P5 *after* the P7 leak harness (its landing precondition), and gate every emit-touching landing on the full-corpus leak harness + the Phase-0 doc.

### Background

The Sprint-36 schedule (`SPRINT_36/PLAN.md`) front-loaded markov to Days 1–3, which freed the back half when it banked on Day 2. `PROJECT_PLAN.md` Sprint 37 specifies the per-priority budgets (P1 16–22h / P2 18–24h / P3 12–16h / P4 14–18h / P5 20–28h / P6 10–14h / P7 12–16h / retest 4h = 106–142h) and the acceptance criteria. The prep-task designs (Tasks 3–10) supply the Day-1-ready specs; this task sequences them.

### What Needs to Be Done

1. **Sequence the days (Day 0 + Days 1–13)** front-loading markov P1 (Days 1–3, the PROCEED/REPLAN gate early), then ganges P2, with fawley P4 *after* markov P1 (shared `_add_indexed_jacobian_terms`) and sarf P5 *after* the P7 leak harness (its precondition); interleave P3 consultation (external-reply-paced), P6 (testbed-gated), and P7 (infra, continuous).
2. **Assign per-priority budgets** from `PROJECT_PLAN.md` (P1 16–22h … retest 4h = 106–142h) across the days at ≤12h/day; identify the heaviest day (~11h — the P1 discriminator + full-corpus verify).
3. **Place the checkpoints** (Day 5 Checkpoint 1, Day 10 Checkpoint 2) with their `--resolve-changed` re-solve + no-regression gates.
4. **Write the REPLAN exits** per priority (P1 discriminator generality / cohort leak; P2 `$66`/`rPower` depth; P4 gate-leak / H-b hand-off; P5 timeout re-trigger; P6 testbed license), each pointing at its Task-3–10 design's documented exit.
5. **Define the Day-0 GO/NO-GO gate:** the Day-0 kickoff re-confirms the baseline (Task 2), the leak harness is wired (Task 3), and the markov/fawley Phase-0 docs exist (Tasks 4, 6) — else NO-GO.
6. **Reference the Known Unknowns** (Task 1) and map each remaining INCOMPLETE unknown to its resolving sprint day.

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# The plan exists with all 14 days + checkpoints + the GO/NO-GO gate
test -f docs/planning/EPIC_4/SPRINT_37/PLAN.md && echo "PLAN.md exists"
grep -cE "^#{1,4} .*Day (0|1|2|3|4|5|6|7|8|9|10|11|12|13)" docs/planning/EPIC_4/SPRINT_37/PLAN.md
grep -qiE "checkpoint" docs/planning/EPIC_4/SPRINT_37/PLAN.md && echo "checkpoints placed"
grep -qiE "GO/NO-GO|readiness gate" docs/planning/EPIC_4/SPRINT_37/PLAN.md && echo "GO/NO-GO gate present"
# The budget fits (heaviest day <= 12h, total < 168h)
grep -qiE "106|142|168|≤ ?12|<= ?12" docs/planning/EPIC_4/SPRINT_37/PLAN.md && echo "budget documented"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_37/PLAN.md` — the day-by-day (Day 0 + Days 1–13) schedule with per-priority budgets, the markov-first front-loading, the fawley-after-markov and sarf-after-P7-harness ordering, the Day-5/Day-10 checkpoints, the per-priority REPLAN exits, and the Day-0 GO/NO-GO readiness gate
- `docs/planning/EPIC_4/SPRINT_37/prompts/PLAN_PROMPTS.md` (optional, mirroring prior sprints) — the per-day execution prompts
- A prep-completion GO/NO-GO summary (all Critical prep tasks complete → Sprint 37 ready)

### Acceptance Criteria

- [ ] Plan created with all 14 days (Day 0 + Days 1–13), each with tasks, integration risks, and complexity estimates
- [ ] markov P1 front-loaded (Days 1–3, early PROCEED/REPLAN gate); fawley P4 sequenced after markov P1; sarf P5 sequenced after the P7 leak harness
- [ ] Per-priority budgets assigned (106–142h total, ≤12h/day, heaviest day identified)
- [ ] Checkpoints placed (Day 5, Day 10) with `--resolve-changed` + no-regression gates
- [ ] Per-priority REPLAN exits written (each pointing at its design's documented exit)
- [ ] The Day-0 GO/NO-GO readiness gate defined (baseline re-confirmed + leak harness wired + Phase-0 docs exist)
- [ ] Every remaining INCOMPLETE known unknown mapped to a resolving sprint day

---

## Summary: Prep Task Execution Order

Execute in this logical order:

**Phase 1: Register & Re-Confirm (Critical — before all design)**
1. Task 1: Create Sprint 37 Known Unknowns List (3-4 hours)
2. Task 2: Re-Confirm the Sprint-36 Baseline & Banked-Diagnosis Fingerprints (3-4 hours)

**Phase 2: The Shared Gate & the Deep Designs (Critical path)**
3. Task 3: Full-Corpus (163-Golden) Leak-Verification Harness Design & Setup (4-5 hours)
4. Task 4: markov P1 — Derivative-Structure Discriminator Design (5-7 hours)
5. Task 6: fawley P4 — Emission-Path Location & Discriminator Design (4-6 hours) [after Task 4 — shared function]

**Phase 3: The Bounded Re-Verifications (can overlap)**
6. Task 5: ganges/gangesx P2 — Cascade Re-Verification & Recovery Sequencing (3-4 hours)
7. Task 7: sarf P5 — Symbolic-Emit Re-Architecture Design Refresh (4-5 hours)
8. Task 8: GAMS-54 v54 Re-Baseline Plan + turkey Testbed (3-4 hours)
9. Task 9: Consultation Reply-Integration + camcge Epic-5 Scoping (2-3 hours)

**Phase 4: Infra Catalog & Schedule**
10. Task 10: Property-Fixture Catalog + Phase-0 CI + Genuine-Floor Tracking (3-4 hours)
11. Task 11: Plan Sprint 37 Detailed Schedule (3-4 hours)

**Total Time:** ~37-50 hours (~5-6 days)

**Critical Path:** 1 → 2 → 3 → 4 → 6 → 10 → 11 (~26-33 hours minimum)

---

## Prep Completion Checklist

Before Sprint 37 Day 1, verify:

### Critical (Must Complete)
- [x] Task 1: Known Unknowns list created (27 items across 7 priorities; full-corpus leak gate tracked)
- [ ] Task 2: Sprint-36 baseline (108/93/75/135) + the four proven-component fingerprints re-confirmed on current `main`
- [ ] Task 3: Full-corpus (163-golden) leak-verification harness designed + clean baseline confirmed
- [ ] Task 4: markov `σ=sp` derivative-structure discriminator designed + Phase-0 issue skeleton authored
- [ ] Task 11: Sprint 37 detailed schedule created with the Day-0 GO/NO-GO gate

### High Priority (Should Complete)
- [ ] Task 5: ganges/gangesx cascade re-verified + recovery sequenced + P2 outcome bounded
- [ ] Task 6: fawley emission path located + discriminator designed + markov co-existence confirmed
- [ ] Task 7: sarf re-arch refreshed + blow-up re-measured + P7-harness precondition explicit

### Medium Priority (Can Complete Later in Prep)
- [ ] Task 8: GAMS-54 v54 re-baseline planned + turkey testbed verdict
- [ ] Task 9: rocket/mine consultation staged + camcge Epic-5 Walras scoped
- [ ] Task 10: property fixtures cataloged + Phase-0-doc CI check designed + genuine-floor tracking

### Verification

```bash
# The prep deliverables exist
for f in KNOWN_UNKNOWNS LEAK_HARNESS_DESIGN MARKOV_DISCRIMINATOR_DESIGN \
         GANGES_RECOVERY_DESIGN FAWLEY_DISCRIMINATOR_REFRESH SARF_REARCH_REFRESH \
         GAMS54_REBASELINE_PLAN CONSULTATION_INTEGRATION_PREP P7_INFRA_CATALOG PLAN; do
  test -f docs/planning/EPIC_4/SPRINT_37/$f.md && echo "  ✓ $f.md" || echo "  ✗ MISSING: $f.md"
done

# The Phase-0 issue skeletons exist for the two shared-function landings
ls docs/issues/ISSUE_*markov-sigma-sp*.md docs/issues/ISSUE_*fawley-constraint-index*.md 2>/dev/null

# The baseline still holds
git diff 78ceaead..HEAD -- data/gamslib/gamslib_status.json | head -1   # expect empty
```

**When all Critical items are checked: Sprint 37 is ready to begin.**

---

## Readiness Gate: GO/NO-GO Decision

**Sprint 37 is ready to begin when:**

### Critical Criteria (ALL must be checked)
- [x] Task 1: Known Unknowns list created (27 items, full-corpus leak gate tracked)
- [ ] Task 2: Baseline 108/93/75/135 + the four proven-component fingerprints re-confirmed
- [ ] Task 3: Full-corpus leak-verification harness designed + clean baseline confirmed
- [ ] Task 4: markov discriminator designed + `ISSUE_1110_markov-sigma-sp-discriminator.md` Phase-0 skeleton authored
- [ ] Task 11: Sprint 37 schedule created with the Day-0 GO/NO-GO gate

### Decision
- **✅ GO:** All Critical criteria checked → Sprint 37 begins
- **❌ NO-GO:** Any Critical criterion unchecked → complete missing items first (especially the markov discriminator design and the leak harness — the head of the critical path)

---

## Expected Benefits for Sprint 37

With prep tasks complete:

1. **No un-designed deep track on Day 1:** the markov `σ=sp` discriminator (the +1-floor lever) has an implementable predicate + a pass/fail full-corpus leak test before Day 1
2. **No shared-function collision:** markov P1 and fawley P4 predicates designed together, both gated by the full-corpus leak harness, mutual-exclusion confirmed on paper
3. **No missed leak:** the full-corpus (163-golden) gate — the Sprint-36 top process lesson — is stood up and every emit landing designs against it
4. **Bounded bimodal calls:** ganges P2 (+2 or 0) and turkey P6 (testbed or deferred) have their outcomes bounded in prep, not discovered mid-sprint
5. **Honest bucket expectations:** camcge is Epic-5-scoped, fawley's +Solve is a Sprint-38 hand-off, and rocket's +1 is reply-contingent — all set before Day 1
6. **Phase-0 discipline up front:** the two shared-function landings have their `docs/issues/ISSUE_<N>_*.md` skeletons authored before the src commit (the Sprint-36 P7 lesson)

**Estimated time saved:** 3-5 days (avoiding a Day-1-through-Day-5 block on an un-designed discriminator or a mid-sprint leak-onto-another-model)
**Prep investment:** ~5-6 days

**Net benefit:** Sprint 37 starts with proven components + implementable designs + the mandatory leak gate, so the control-first discipline (zero broken code, S30–S36) holds a seventh sprint.

---

## Appendix: Document Cross-References

### Sprint 37 goals (the sprint this prep serves)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` — **Sprint 37 (Weeks 39–40)** section (Goal, Note, Components P1–P7, Deliverables, Acceptance Criteria, Estimated Effort 106–142h, Risk Level HIGH)
- `docs/planning/EPIC_4/GOALS.md` — Epic 4 strategic themes (parse/translate/solve/match completion; PATH-author consultation for divergences)
- `docs/planning/EPIC_4/SUMMARY.md` — the sprint-by-sprint KPI record (row 36 = actual S36; row 37 groundwork under P7/Task 10)

### Sprint 36 carryforward sources (the sharpened banks this prep re-verifies)
- `docs/planning/EPIC_4/SPRINT_36/SPRINT_37_CARRYFORWARDS.md` — the sharpest-first carryforward register (§1.1 markov … §1.9 GAMS-54)
- `docs/planning/EPIC_4/SPRINT_36/SPRINT_RETROSPECTIVE.md` — §5 carryforward priority (markov first); §4 process lessons (full-corpus leak verification mandatory)
- `docs/planning/EPIC_4/SPRINT_36/SPRINT_LOG.md` — the day-by-day outcomes + the Day-13 retest battery

### Per-track banked designs (the specs this prep refreshes)
- markov P1: `SPRINT_36/DAY2_MARKOV_OFFDIAG_CONTROL.md`, `DAY3_MARKOV_BANK.md`, `MARKOV_OFFDIAGONAL_DESIGN.md`
- ganges P2: `SPRINT_36/DAY8_P4_GANGES_BANK.md`, `GANGES_RECOVERY_SEQUENCING.md`, `SPRINT_35/DAY3_P4_BANK_CARRYFORWARD.md` (§5 `_diff_prod`), git `a8ff626c`
- fawley P4: `SPRINT_36/DAY4_FAWLEY_DEFER.md`, `FAWLEY_DISCRIMINATOR_DESIGN.md`
- sarf P5: `SPRINT_36/DAY6_SARF_BANK.md`, `SARF_DESIGN_REFRESH.md`
- P3 consultation: `SPRINT_36/DAY11_P5_CONSULTATION.md`, `CONSULTATION_BUNDLE.md`, `P5_CONSULTATION_FINALIZATION.md`, `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`, `SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md`
- P6 GAMS-54: `SPRINT_36/GAMS54_TESTBED_PLAN.md`, `SPRINT_35/FOLLOWUPS_GAMS54_TRANSITION.md`
- P7 infra: `SPRINT_36/FIXTURE_AND_HARNESS_CATALOG.md`, `CONTRIBUTING.md` (§392–447 Phase-0 rule)

### Epic 5 (deferred items)
- `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` — the camcge dual-consistent Walras / per-model-numéraire Epic-5 gate (P3/Task 9)

### Related research documents
- `docs/research/minmax_objective_reformulation.md`, `minmax_path_validation_findings.md`, `nested_minmax_semantics.md` — min/max reformulation (PATH-forcing context)
- `docs/research/multidimensional_indexing.md`, `nested_subset_indexing_research.md` — indexed-derivative structure (the markov/fawley discriminator context)
- `docs/research/convexity_detection.md`, `CONVEXITY_VERIFICATION_DESIGN.md` — the convex-candidate corpus scope (the 142 vs all-219 KPI denominator)

### Reusable instruments (tooling this prep exercises)
- `scripts/diagnostics/kkt_residual.py` — the KKT-residual CASE_A/B/C harness (markov/fawley/ganges control gates)
- `scripts/sprint_audit/check_golden_staleness.py` — the golden-staleness gate (the Task-3 full-corpus leak harness's core)
- `scripts/gamslib/run_full_test.py` — the pipeline runner (`--resolve-changed --since-commit 78ceaead`; the v54 re-baseline in Task 8)

### Format precedent
- `docs/planning/EPIC_1/SPRINT_4/PREP_PLAN.md`, `docs/planning/EPIC_1/SPRINT_5/PREP_PLAN.md` — the per-task section format (Status/Priority/Estimated Time/Deadline/Owner/Dependencies/Objective/Why This Matters/Background/What Needs to Be Done/Changes/Result/Verification/Deliverables/Acceptance Criteria) + the standard sections (Executive Summary, Prep Task Overview, critical path, Summary, Readiness Gate)
- `docs/planning/EPIC_4/SPRINT_36/PREP_PLAN.md` — the most recent Epic-4 prep-plan precedent (the 10-task Sprint-36 structure this mirrors)

---

**Document Created:** 2026-08-09
**Sprint 37 Target Start:** Weeks 39–40 (per PROJECT_PLAN.md)
**Next Steps:** Execute prep tasks in order (1 → 2 → 3 → 4 → 6 → 10 → 11 on the critical path), verify completion, run the Day-0 GO/NO-GO gate, begin Sprint 37
**Owner:** Sprint 37 execution team

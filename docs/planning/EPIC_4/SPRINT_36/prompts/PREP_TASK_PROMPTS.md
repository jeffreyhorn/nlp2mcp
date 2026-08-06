# Sprint 36 Prep Task Prompts (Tasks 2–10)

**Purpose:** ready-to-paste execution prompts for the Sprint-36 preparation tasks defined in `docs/planning/EPIC_4/SPRINT_36/PREP_PLAN.md`. Paste one prompt per prep task, in order. Task 1 (Create Known Unknowns List) is already ✅ COMPLETE.

**Standing conventions (apply to every prompt below):**
- Work on a branch **`planning/sprint36-task<Z>`** where `<Z>` is the task number (e.g. Task 3 → `planning/sprint36-task3`), branched from `main`.
- **Verify each associated Known Unknown**: update `docs/planning/EPIC_4/SPRINT_36/KNOWN_UNKNOWNS.md` — change each unknown's Verification Results from `🔍 **Status:** INCOMPLETE` to **`✅ **Status:** VERIFIED`** (or **`❌ **Status:** WRONG`** with the correction), and add **Findings**, **Evidence**, and **Decision** lines under it (mirroring the Sprint-35 resolved-unknown format).
- **Update `PREP_PLAN.md`**: set the task **Status → ✅ COMPLETE (date)**, fill the **Changes** and **Result** sections (replace "To be completed"), and check off **all** acceptance criteria `- [ ]` → `- [x]` (including the "Unknowns … verified and updated in KNOWN_UNKNOWNS.md" criterion).
- **Update `CHANGELOG.md`**: add a Task-completion entry under `[Unreleased]` (newest first) summarizing what was verified/produced.
- **Quality gate (only if `*.py` changed):** run `make typecheck && make lint && make format && make test` and confirm all pass **before** committing. Prep tasks are docs/analysis by default (docs-only → the gate is N/A); if a task touches `src/`/`tests/`, the gate is mandatory.
- **Commit message:** `Complete Sprint 36 Prep Task <Z>: <Task Title>` (single commit; list the verified unknowns + the produced artifact in the body). No `Co-Authored-By` line; no "Generated with Claude Code" attribution.
- **Open a PR** with `gh pr create` (summary + the unknowns verified + the deliverables), push the branch, **then wait for reviewer comments**. Address each review comment on its own thread (`gh api repos/jeffreyhorn/nlp2mcp/pulls/<N>/comments/<id>/replies -f body="..."`), not as a top-level comment.

Reference: the full task definitions live in `docs/planning/EPIC_4/SPRINT_36/PREP_PLAN.md`; the unknowns in `docs/planning/EPIC_4/SPRINT_36/KNOWN_UNKNOWNS.md`; the sprint scope in `docs/planning/EPIC_4/PROJECT_PLAN.md` (Sprint 36).

---

## Prep Task 2 Prompt — Re-Confirm the Sprint-35 Baseline & Banked-Diagnosis Fingerprints

On a new branch `planning/sprint36-task2` (from `main`), execute Sprint-36 Prep Task 2.

**Objective:** Re-verify, on the current `main`, that the Sprint-35-close baseline (Solve 108 / Match 93 / genuine floor 75) and each banked control fingerprint still hold — so Sprint 36's designs build on measured reality, not a two-week-old snapshot.

**What to do:** (1) recompute the KPI baseline from the committed DB over the 142 convex candidates; (2) confirm DB + emit integrity vs the anchor `78ceaead` (`git diff` on `gamslib_status.json` empty; `src/` delta = only the turkey `original_symbols.py`); (3) re-run the markov control (`kkt_residual.py data/gamslib/raw/markov.gms` → expect `CASE_B`, `max|stat_z|` rel ≈ 13.3, dual CONSISTENT); (4) re-confirm the markov Part-1 diagonal split still reduces the residual to ≈ 1.55 (re-read `DAY11_MARKOV_DIAGONAL_LEVER.md` §6, optionally re-apply on a scratch branch and revert); (5) re-run the fawley control (expect `CASE_B`, `stat_bq` ≈ 0.973, H-b `stat_trans(tr-2)`); (6) confirm the ganges `$149` `_diff_prod` fix surface is unchanged on `main`; (7) record each result in the KU disposition slots.

**Deliverables:**
- A Day-0 baseline re-confirmation note (in the KU doc or a short `DAY0_TRACE_NOTES.md`): KPIs re-computed, DB/emit integrity vs anchor, each banked fingerprint marked VERIFIED or drift-detected.
- The markov / fawley control outputs captured (verdict + max-residual rows).
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.1, 3.3, 3.4.

**Unknowns to verify (update KNOWN_UNKNOWNS.md → ✅ VERIFIED / ❌ WRONG, with Findings/Evidence/Decision):** **1.1** (markov Part-1 residual 13.3→1.55 still reproduces), **3.3** (fawley control 473→1.14e-13 still holds), **3.4** (fawley +Solve is H-b). *(Also contributes the DB/fix-surface re-confirm for 4.1, 5.4, 7.5 — note these contributions in those unknowns.)*

Then update `PREP_PLAN.md` (Task 2 → ✅ COMPLETE, fill Changes/Result, check all acceptance criteria), update `CHANGELOG.md`, run the quality gate **only if** `*.py` changed (this task is expected docs/analysis-only), commit as `Complete Sprint 36 Prep Task 2: Re-Confirm the Sprint-35 Baseline & Banked-Diagnosis Fingerprints`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 3 Prompt — markov P1: Part-2 (`σ=sp`) Off-Diagonal Enumeration Design

On a new branch `planning/sprint36-task3` (from `main`), execute Sprint-36 Prep Task 3. **Depends on Tasks 1, 2.**

**Objective:** Produce a written design for the markov fix's **Part 2** — the off-diagonal enumeration where the constraint multiplier index equals an *independent* variable index (`σ=sp`, the variable's 3rd) that the current offset machinery cannot represent — so Sprint 36 Day 1 starts with a control-gated implementation plan, not an open research question.

**What to do:** (1) re-read `DAY11_MARKOV_DIAGONAL_LEVER.md` §2–§6; (2) characterize the `σ=sp` representation gap against the exact code path (`_compute_index_offset_key` + the sub-group emission in `_add_indexed_jacobian_terms`, `src/kkt/stationarity.py:5861+`); (3) enumerate ≥2 candidate mechanisms (e.g. a "bound-to-var-index" offset-key marker; a `sameas`-guarded direct term; a dedicated multi-pattern branch) with sketched emitted GAMS + blast radius; (4) pick the minimal, lowest-blast-radius mechanism and its code surface; (5) specify the Phase-0 `/tmp` control that must drive `kkt_residual.py markov` → `CASE_A` before any `src/` change; (6) specify the leak-freedom gate (2-D cohort byte-identical) and its interaction with the fawley Task-4 discriminator.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_36/MARKOV_OFFDIAGONAL_DESIGN.md` — the representation-gap characterization, the chosen mechanism (+ 1–2 rejected alternatives), the exact code surface, the Phase-0 `CASE_A` control spec, and the leak-freedom gate.
- A go/no-go on whether Part 2 is landable in the P1 budget (14–20h) or a documented REPLAN exit.
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.2, 1.3, 1.4.

**Unknowns to verify:** **1.2** (`σ=sp` has a bounded offset-key mechanism), **1.3** (the fix won't leak onto the 2-D cohort), **1.4** (markov cold-solves to `model_optimal` at `CASE_A` — the methodology→genuine +1).

Then update `PREP_PLAN.md` (Task 3 → ✅ COMPLETE, Changes/Result, ACs), update `CHANGELOG.md`, quality gate only if `*.py` changed, commit as `Complete Sprint 36 Prep Task 3: markov P1 Part-2 (sigma=sp) Off-Diagonal Enumeration Design`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 4 Prompt — fawley P3: Derivative-Structure Discriminator Design

On a new branch `planning/sprint36-task4` (from `main`), execute Sprint-36 Prep Task 4. **Depends on Tasks 1, 2, 3.**

**Objective:** Design the **derivative-structure discriminator** that lets the fawley constraint-index-diagonal `sameas` correction fire *without* leaking onto the markov #1110 multi-pattern off-diagonal (the exact leak that forced the S35 Day-9 revert), and specify how it co-exists with the Task-3 markov change in the shared `_add_indexed_jacobian_terms`.

**What to do:** (1) re-read `DAY9_P3_FAWLEY_CONTROL_DEFER.md` + `FAWLEY_DIAGONAL_DESIGN.md`; (2) characterize the leak surface (why the surface-pattern predicate over-fires on markov #1110); (3) design the discriminator (a derivative-structure key / an extension of `_derivative_structure_key`) that fires only on fawley's constraint-index-diagonal; (4) prove co-existence with the Task-3 markov change (non-overlapping branches; combined 2-D cohort byte-identical); (5) specify the Phase-0 `/tmp` `max|stat_bq|→0` control + the golden-staleness gate; (6) cross-reference the H-b +Solve `--force` survey (Task 8 / `CONSULTATION_BUNDLE.md` §3).

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_36/FAWLEY_DISCRIMINATOR_DESIGN.md` — the discriminator design, its co-existence proof with the Task-3 markov change, the Phase-0 control, and the leak-freedom gate.
- A joint markov/fawley change-surface map for `_add_indexed_jacobian_terms`.
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 3.1, 3.2.

**Unknowns to verify:** **3.1** (a derivative-structure key distinguishes fawley from markov #1110), **3.2** (the discriminator co-exists with the markov change — non-overlapping branches, cohort byte-identical).

Then update `PREP_PLAN.md` (Task 4 → ✅ COMPLETE, Changes/Result, ACs), update `CHANGELOG.md`, quality gate only if `*.py` changed, commit as `Complete Sprint 36 Prep Task 4: fawley P3 Derivative-Structure Discriminator Design`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 5 Prompt — sarf P2: Symbolic-Emit Subsystem Design Refresh & Blow-Up Re-Measurement

On a new branch `planning/sprint36-task5` (from `main`), execute Sprint-36 Prep Task 5. **Depends on Tasks 1, 2.**

**Objective:** Refresh the banked sarf symbolic-emit design against the current `main`, re-measure the 369K-column blow-up, and confirm the O(active=398) guarded-emit approach and its Phase-0 timing gate are still valid — so Sprint 36's largest single track (20–28h) starts with a verified spec.

**What to do:** (1) re-read `SARF_SYMBOLIC_EMIT_DESIGN.md` + `PHASE_0_ACCEPTANCE_GATES.md`; (2) re-measure the blow-up on current `main` (capped sarf emit; confirm >303s / non-terminating; record the wall-clock at the cap); (3) re-validate the 7-term `stat_task` derivation vs `sarf.gms`; (4) confirm the O(active) guarded-emit shape (`stat_task(g,t,m,n)$taskposs` + `task.fx` guard) passes GAMS instantiation (hand-construct a `/tmp` fragment + compile under GAMS 54); (5) re-confirm the Phase-0 timing gate + regression harness (byte-stable golden, determinism ×3, no set-name-literal indices); (6) flag the re-scope exit.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_36/SARF_DESIGN_REFRESH.md` — the re-measured blow-up, the re-validated 7-term derivation, the confirmed O(active=398) target, and the Phase-0 gate + regression harness.
- A go/no-go on whether the S35 design applies unchanged.
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 2.1, 2.2, 2.3, 2.4.

**Unknowns to verify:** **2.1** (369K blow-up still >303s), **2.2** (O(active=398) guarded emit passes GAMS instantiation), **2.3** (7-term derivation still valid), **2.4** (determinism ×3 + no set-name-literal indices).

Then update `PREP_PLAN.md` (Task 5 → ✅ COMPLETE, Changes/Result, ACs), update `CHANGELOG.md`, quality gate only if `*.py` changed, commit as `Complete Sprint 36 Prep Task 5: sarf P2 Symbolic-Emit Subsystem Design Refresh`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 6 Prompt — ganges/gangesx P4: ≥5-Blocker Cascade Re-Verification & Recovery Sequencing

On a new branch `planning/sprint36-task6` (from `main`), execute Sprint-36 Prep Task 6. **Depends on Tasks 1, 2.**

**Objective:** Re-verify the ganges/gangesx ≥5-blocker cascade on current `main`, confirm the banked `$149` `_diff_prod` fix still applies cleanly, and sequence the recovery (`$141` → `$145` → `$149` → `$66` → `rPower`) — including the slow-CGE-golden regeneration budget.

**What to do:** (1) re-read `DAY3_P4_BANK_CARRYFORWARD.md` + `GANGES_RECOVERY_DESIGN.md` + `GANGES_149_PRODUCT_RULE_ANALYSIS.md`; (2) re-verify the `$149` `_diff_prod` fix location (`src/ad/derivative_rules.py`) is unchanged and the banked patch still applies (ganges `$149` 9→0; lmp2/camcge byte-identical); (3) confirm the `$141` helper plan uses the existing `_expr_contains_varref_attribute` (NOT the buggy `_expr_contains_varref_attr`); (4) re-confirm the cascade order + terminal blockers (`$66` cold, `rPower` presolve) via a scratch three-fix apply + compile probe; (5) estimate the slow-golden regeneration cost + identify a budget slot; (6) sequence the recovery with a `--resolve-changed` gate after each fix.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_36/GANGES_RECOVERY_SEQUENCING.md` — the re-verified cascade, the confirmed `$149`/`$141` fix surfaces, the ordered recovery plan with per-fix `--resolve-changed` gates, and the golden-regen budget slot.
- A cross-note to P6: the `$149` fix's unblocking of dinam/indus/turkpow/clearlak's `$149` half.
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 4.1, 4.2, 4.3, 4.4, 4.5, 6.3.

**Unknowns to verify:** **4.1** ($149 fix still applies), **4.2** ($141 uses the existing helper), **4.3** ($66/rPower are the terminals), **4.4** (slow goldens regenerable in budget), **4.5** ($149 unblocks the four-model $149 half), **6.3** (residual cohort roots still accurate).

Then update `PREP_PLAN.md` (Task 6 → ✅ COMPLETE, Changes/Result, ACs), update `CHANGELOG.md`, quality gate only if `*.py` changed, commit as `Complete Sprint 36 Prep Task 6: ganges/gangesx P4 Cascade Re-Verification & Recovery Sequencing`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 7 Prompt — GAMS-54 Licensed-Testbed Re-Baseline Harness Plan (P7 + turkey P6)

On a new branch `planning/sprint36-task7` (from `main`), execute Sprint-36 Prep Task 7. **Depends on Tasks 1, 2.**

**Objective:** Plan the licensed-testbed harness for the GAMS-54 corpus re-baseline (the v53→v54 transition's first infra task) and turkey's >1000-row solve — the two Sprint-36 items that cannot run on the local 1000-row demo license.

**What to do:** (1) confirm licensed GAMS-54 testbed access (CI runner / dedicated machine) capable of >1000-row solves + document the invocation; (2) scope the re-baseline diff (corpus re-solve under v54 vs the v53 DB; the 5 OBJ-GAP models agreste/cesam/chain/fawley/rocket; the PR19 Tier-0/1 canaries); (3) plan the turkey 3,866-row solve invocation; (4) specify the DB-version decision (pin to v54 vs keep v53) criteria + artifact; (5) confirm the emit-level gates stay local (version-independent); (6) identify the async Day-slot (feeds Day-10 / Day-13).

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_36/GAMS54_TESTBED_PLAN.md` — the testbed access confirmation, the re-baseline diff scope, the turkey solve invocation, the DB-version decision criteria, and the async Day-slot.
- A checklist of what stays local (emit-level gates) vs what needs the testbed (solve buckets).
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 6.1, 6.2, 7.1, 7.2.

**Unknowns to verify:** **6.1** (licensed >1000-row testbed available), **6.2** (turkey solves to optimal+match), **7.1** (5 OBJ-GAP models' bucket stability), **7.2** (v53-vs-v54 canonical-baseline decision).

Then update `PREP_PLAN.md` (Task 7 → ✅ COMPLETE, Changes/Result, ACs), update `CHANGELOG.md`, quality gate only if `*.py` changed, commit as `Complete Sprint 36 Prep Task 7: GAMS-54 Licensed-Testbed Re-Baseline Harness Plan`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 8 Prompt — Consultation Bundle Finalization (rocket/mine P5) + camcge Epic-5 Gate Scoping

On a new branch `planning/sprint36-task8` (from `main`), execute Sprint-36 Prep Task 8. **Depends on Tasks 1, 2.**

**Objective:** Confirm the rocket PATH-consultation input is submission-ready, finalize the mine primal-degenerate-LP question, and scope the camcge Walras Epic-5 `/tmp` control gate — so P5 is a bounded submission/scoping day, not an open research task.

**What to do:** (1) re-read `CONSULTATION_BUNDLE.md` §1–§3 + `DAY8_P5_CAMCGE_SPRINT36.md` + `MINE_DUAL_ARCHITECTURE_DESIGN.md`; (2) verify the rocket input is submission-ready (question + ruled-out-lever survey + reproducible case + `--force` scaffold, renumbered); (3) finalize the mine primal-degenerate-LP question (value-invariance + `x.up=inf` BAN stated); (4) scope the camcge Epic-5 `/tmp` Walras MS-1 gate (with the price-pin MS-4 fallback); (5) cross-reference the fawley `--force` survey (§3 / Task 4); (6) note P5 is a submission/scoping day (no emit fix), feeding the Sprint-37 consultation.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_36/P5_CONSULTATION_FINALIZATION.md` — the rocket submission-readiness confirmation, the finalized mine question, the camcge Epic-5 `/tmp` gate scope, and the fawley `--force` cross-reference.
- A note confirming P5 is a submission/scoping day feeding the Sprint-37 consultation.
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 5.1, 5.2, 5.3, 5.4.

**Unknowns to verify:** **5.1** (rocket input submission-ready), **5.2** (mine question precise), **5.3** (camcge Walras Epic-5 gate reachability), **5.4** (S1∧S2∧S3 detector fires only camcge).

Then update `PREP_PLAN.md` (Task 8 → ✅ COMPLETE, Changes/Result, ACs), update `CHANGELOG.md`, quality gate only if `*.py` changed, commit as `Complete Sprint 36 Prep Task 8: Consultation Bundle Finalization + camcge Epic-5 Gate Scoping`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 9 Prompt — Property-Fixture & 2-D-Cohort Regression-Harness Catalog + robustlp NA Survey

On a new branch `planning/sprint36-task9` (from `main`), execute Sprint-36 Prep Task 9. **Depends on Tasks 1, 3, 4.**

**Objective:** Catalog the property fixtures Sprint 36 will add (the markov diagonal-Kronecker fixture, the fawley 2-D second-index fixture), specify the 2-D-cohort golden-staleness regression harness that guards the shared `_add_indexed_jacobian_terms` changes, decide the markov `slow`-test disposition, and survey the robustlp NA-coefficient root term.

**What to do:** (1) catalog the fixtures (markov diagonal-Kronecker, gated on Task-3; fawley `shape_fawley_2d_second_index`, gated on Task-4) with assertions + skip-if-absent; (2) specify the 2-D-cohort golden-staleness harness (cesam2/camcge/ps2/ps3/polygon byte-identical after either change); (3) decide the markov `slow`-test disposition with the Task-3 fix; (4) survey the robustlp NA root (which emitted term goes NA under GAMS 54, #1322 family) + scope the emit fix + the de-allowlist step; (5) note the genuine-floor tracking recompute (anchor 75 → ≥76) + the Epic-4 `SUMMARY.md` row-36 groundwork.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_36/FIXTURE_AND_HARNESS_CATALOG.md` — the fixture specs, the 2-D-cohort golden-staleness harness, the markov `slow`-test disposition, the robustlp NA root survey + de-allowlist plan, and the genuine-floor recompute note.
- A mapping of each fixture to the Task-3/Task-4 landing it guards.
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.3, 1.5, 7.3, 7.4, 7.5.

**Unknowns to verify:** **1.3** (cohort regression harness — jointly with Task 3), **1.5** (markov `slow`-test disposition), **7.3** (robustlp NA root + de-allowlist), **7.4** (shared fixture harness), **7.5** (genuine-floor recompute at anchor 75).

Then update `PREP_PLAN.md` (Task 9 → ✅ COMPLETE, Changes/Result, ACs), update `CHANGELOG.md`, quality gate only if `*.py` changed, commit as `Complete Sprint 36 Prep Task 9: Property-Fixture & Regression-Harness Catalog + robustlp NA Survey`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 10 Prompt — Plan Sprint 36 Detailed Schedule

On a new branch `planning/sprint36-task10` (from `main`), execute Sprint-36 Prep Task 10. **Depends on all tasks (1–9) — run last.**

**Objective:** Synthesize the prep outputs into a day-by-day Sprint 36 schedule (Day 0 + Days 1–13) that front-loads the deepest tracks, places the two checkpoints (Day 5, Day 10) and the final retest (Day 13), threads the async testbed run, and attaches an explicit REPLAN exit to each track — within the 168-hour / ≤12h-day budget.

**What to do:** (1) sequence the tracks by risk + value (front-load P1 markov Days 1–3 and P2 sarf; co-schedule P3 fawley with P1 since they share `_add_indexed_jacobian_terms`; then P4/P5/P6/P7); (2) place Checkpoint 1 (Day 5) + Checkpoint 2 (Day 10); (3) thread the async testbed run (Task 7) to land by Day 10 / Day 13; (4) attach a REPLAN exit to each track (P1 `σ=sp` depth / cohort leak; P2 timeout; P3 gate-leak / H-b; P4 `$66`/`rPower`; P5 Epic-5); (5) budget days at ≤12h/day; (6) write the Day-0 kickoff checklist (Task-2 fingerprint re-confirm + KU Day-0-blocker clearance); (7) author `prompts/PLAN_PROMPTS.md` (Day 0 + Days 1–13).

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_36/PLAN.md` — the Day-0-through-Day-13 schedule, the two checkpoints, the async testbed thread, per-track REPLAN exits, the ≤12h/day budget, and the Day-0 kickoff checklist.
- `docs/planning/EPIC_4/SPRINT_36/prompts/PLAN_PROMPTS.md` — the per-day execution prompts (Day 0 + Days 1–13).
- A one-line GO/NO-GO for Day 0 (all Day-0 blockers cleared).
- Confirmation that all Unknowns 1.1–7.5 are resolved (✅ VERIFIED / ❌ WRONG-with-correction) in `KNOWN_UNKNOWNS.md`, with any residual carried as a REPLAN exit.

**Unknowns to verify:** **All** — Task 10 integrates every verified unknown (1.1–7.5) into the schedule and confirms the Day-0 GO/NO-GO. Do a final pass over `KNOWN_UNKNOWNS.md` to confirm no unknown is still `🔍 INCOMPLETE` (or that any remaining one is explicitly carried as a REPLAN exit in the schedule).

Then update `PREP_PLAN.md` (Task 10 → ✅ COMPLETE, Changes/Result, ACs), update `CHANGELOG.md`, quality gate only if `*.py` changed, commit as `Complete Sprint 36 Prep Task 10: Plan Sprint 36 Detailed Schedule`, push, open a PR, and wait for reviewer comments.

---

**Document Status:** ✅ Complete — the per-task execution prompts for Sprint-36 prep (Tasks 2–10)
**Last Updated:** 2026-08-06
**Owner:** Sprint 36 Planning Team

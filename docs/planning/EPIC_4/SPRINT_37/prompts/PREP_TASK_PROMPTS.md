# Sprint 37 Prep Task Prompts (Tasks 2–11)

**Purpose:** ready-to-paste execution prompts for the Sprint-37 preparation tasks defined in `docs/planning/EPIC_4/SPRINT_37/PREP_PLAN.md`. Paste one prompt per prep task, in order. Task 1 (Create Known Unknowns List) is already ✅ COMPLETE.

**Standing conventions (apply to every prompt below):**
- Work on a branch **`planning/sprint37-task<Z>`** where `<Z>` is the task number (e.g. Task 4 → `planning/sprint37-task4`), branched from `main`.
- **Verify each associated Known Unknown**: update `docs/planning/EPIC_4/SPRINT_37/KNOWN_UNKNOWNS.md` — change each unknown's Verification Results from `🔍 **Status:** INCOMPLETE` to **`✅ **Status:** VERIFIED`** (or **`❌ **Status:** WRONG`** with the correction), and add **Findings**, **Evidence**, and **Decision** lines under it (mirroring the Sprint-36 resolved-unknown format).
- **Update `PREP_PLAN.md`**: set the task **Status → ✅ COMPLETE (date)**, fill the **Changes** and **Result** sections (replace "To be completed"), and check off **all** acceptance criteria `- [ ]` → `- [x]` (including the "Unknowns … verified and updated in KNOWN_UNKNOWNS.md" criterion).
- **Update `CHANGELOG.md`**: add a Task-completion entry under `[Unreleased]` → `### Sprint 37 Preparation` (newest first) summarizing what was verified/produced.
- **Quality gate (only if `*.py` changed):** run `make typecheck && make lint && make format && make test` and confirm all pass **before** committing. Prep tasks are docs/analysis by default (docs-only → the gate is N/A); if a task touches `src/`/`tests/`/`scripts/`, the gate is mandatory.
- **Commit message:** `Complete Sprint 37 Prep Task <Z>: <Task Title>` (single commit; list the verified unknowns + the produced artifact in the body). No `Co-Authored-By` line; no "Generated with Claude Code" attribution.
- **Open a PR** with `gh pr create` (summary + the unknowns verified + the deliverables), push the branch, **then wait for reviewer comments**. Address each review comment on its own thread (`gh api repos/jeffreyhorn/nlp2mcp/pulls/<N>/comments/<id>/replies -f body="..."`), not as a top-level comment.

Reference: the full task definitions live in `docs/planning/EPIC_4/SPRINT_37/PREP_PLAN.md`; the unknowns in `docs/planning/EPIC_4/SPRINT_37/KNOWN_UNKNOWNS.md`; the sprint scope in `docs/planning/EPIC_4/PROJECT_PLAN.md` (Sprint 37, Weeks 39–40); the sharpened banks in `docs/planning/EPIC_4/SPRINT_36/SPRINT_37_CARRYFORWARDS.md`.

**Recommended order (critical path):** 2 → 3 → 4 → 6 → 10 → 11, with Tasks 5, 7, 8, 9 overlapping. Task 3 (the full-corpus leak harness) must precede Tasks 4 and 6 (they design their Phase-0 gate against it); Task 4 (markov) must precede Task 6 (fawley) — they share `_add_indexed_jacobian_terms` and must be proven mutually exclusive.

---

## Prep Task 2 Prompt — Re-Confirm the Sprint-36 Baseline & Banked-Diagnosis Fingerprints

On a new branch `planning/sprint37-task2` (from `main`), execute Sprint-37 Prep Task 2. **Depends on Task 1.** (Priority: Critical; est. 3–4h.)

**Objective:** Re-verify, on the current `main`, that (a) the Sprint-36-close KPIs still recompute (Solve 108 / Match 93 [63 cold + 30 presolve] / genuine floor 75 / Translate 135 / mi 7 / pse 7 / all-219 96), (b) the DB is byte-identical to the anchor `78ceaead`, and (c) each banked track's *proven-component* fingerprint still reproduces — so Sprint 37's designs build on measured reality, not a two-week-old snapshot.

**What to do:** (1) recompute the KPI baseline from the committed DB over the 142 convex candidates (PR25 re-baseline); (2) DB byte-check — `git diff 78ceaead..HEAD -- data/gamslib/gamslib_status.json` empty (0 bucket move); (3) golden-staleness clean across all 163 goldens; (4) re-confirm the **four proven-component fingerprints** on current `main` using the banked recipes: **markov** (re-apply the reverted Day-2 Mechanism C prototype in a `/tmp` copy → `kkt_residual.py markov` reaches `CASE_A` rel ≈ 2.8e-16 + cold-solve 2401.577 + match; confirm the domain-only gate still leaks onto cesam/ferts/sroute), **ganges/gangesx** (re-apply `$141`/`$145`/`$149` from git `a8ff626c` + the `_diff_prod` §5 patch → cold `$NNN` count → 0; `$66`×17 + `rPower` still the terminals), **fawley** (re-apply the `stat_bq` `sameas` hand-edit → `max|stat_bq|` 473 → 1.14e-13), **sarf** (re-run the emit → the 369K blow-up still exceeds the 100s cap); (5) record each result (VERIFIED / DRIFTED with delta) in the KU disposition slots.

**Deliverables:**
- A `docs/planning/EPIC_4/SPRINT_37/BASELINE_RECONFIRMATION.md` (or a short Task-2 prep note): the recomputed KPIs, the DB byte-check + golden-staleness results, and the VERIFIED/DRIFTED disposition of each of the four proven-component fingerprints.
- The markov / fawley / ganges control outputs captured (verdict + max-residual rows / `$NNN` counts).
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.1, 2.1, 4.3, 5.1, 7.4.

**Unknowns to verify (update KNOWN_UNKNOWNS.md → ✅ VERIFIED / ❌ WRONG, with Findings/Evidence/Decision):** **1.1** (the reverted Day-2 markov prototype still drives `CASE_B`→`CASE_A` + cold-match 2401.577), **2.1** (the `$141`/`$145`/`$149` cascade fixes still apply byte-clean), **4.3** (the fawley `stat_bq` control still drives 473→1.14e-13), **5.1** (the sarf 369K blow-up still >100s), **7.4** (the genuine-floor tracking holds at anchor 75; markov ∈ methodology).

Then update `PREP_PLAN.md` (Task 2 → ✅ COMPLETE, fill Changes/Result, check all acceptance criteria), update `CHANGELOG.md`, run the quality gate **only if** `*.py` changed (this task is expected docs/analysis-only), commit as `Complete Sprint 37 Prep Task 2: Re-Confirm the Sprint-36 Baseline & Banked-Diagnosis Fingerprints`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 3 Prompt — Full-Corpus (163-Golden) Leak-Verification Harness Design & Setup

On a new branch `planning/sprint37-task3` (from `main`), execute Sprint-37 Prep Task 3. **Depends on Tasks 1, 2.** (Priority: Critical; est. 4–5h.)

**Objective:** Design and stand up the **full-corpus (163-golden) leak-verification harness** as a required gate for any `src/{ad,kkt,emit}` change touching the shared `_add_indexed_jacobian_terms` (or `_compute_index_offset_key`) — a `make` target + a CI job — so that the P1 markov (Task 4) and P4 fawley (Task 6) designs can specify "full-corpus golden-staleness shows ONLY my model drifts" as their Phase-0 acceptance criterion. This is the Sprint-36 retrospective's top process lesson (the 6-model cohort missed all three markov Day-2 leaks).

**What to do:** (1) inventory the 163 goldens and cost-classify (fast / medium / slow CGE-dynamic-ganges tail) with a total-regen wall-clock estimate; (2) design the two modes — a PR-blocking fast mode (fast/medium goldens, within CI budget) + a nightly full mode (all 163 incl. the slow tail); (3) specify the path/function-scoped trigger (arms only on `_add_indexed_jacobian_terms` / `_compute_index_offset_key`-relevant changes, not unrelated emit changes); (4) define the `--expect-drift <model>[,<model>]` pass criterion ("only the intended model(s) drift; all others byte-identical"); (5) draft the `make` target + CI job (spec in prep; the wiring lands in-sprint under P7); (6) dry-run the fast mode on a clean tree to confirm zero false-positive drift (the harness is deterministic).

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_37/LEAK_HARNESS_DESIGN.md` — the golden inventory (fast/medium/slow + wall-clock), the two-mode gate design, the path/function-scoped trigger, the `--expect-drift` pass criterion, and the draft `make` target + CI job spec.
- A confirmed clean full-corpus baseline (163 goldens, zero drift on current `main`).
- The `make leak-check MODEL=<name>` invocation string the P1/P4 Phase-0 gates will reference.
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.3, 7.1.

**Unknowns to verify:** **7.1** (the full-corpus harness can run as a required PR gate within CI budget — fast + nightly modes, `--expect-drift`, deterministic dry-run), **1.3** (the markov discriminator's full-corpus leak gate — jointly with Task 4; confirm the harness is the instrument that catches the cesam/ferts/sroute leaks the cohort missed).

Then update `PREP_PLAN.md` (Task 3 → ✅ COMPLETE, Changes/Result, ACs), update `CHANGELOG.md`, run the quality gate **only if** `*.py`/`scripts/` changed (a design-only stand-up may touch a `make`-target/CI draft — if it edits `scripts/` or a workflow, the gate is mandatory), commit as `Complete Sprint 37 Prep Task 3: Full-Corpus (163-Golden) Leak-Verification Harness Design & Setup`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 4 Prompt — markov P1: Derivative-Structure Discriminator Design

On a new branch `planning/sprint37-task4` (from `main`), execute Sprint-37 Prep Task 4. **Depends on Tasks 1, 2, 3.** (Priority: Critical; est. 5–7h — the head of the critical path.)

**Objective:** Design the **derivative-structure discriminator** that lets the *already-proven* markov `σ=sp` Mechanism C emission (Day-2: `CASE_B` rel 13.3 → `CASE_A` rel 2.8e-16, cold-solve 2401.577 + match) fire *only* on markov's genuine param-coupled off-diagonal (`−b·pi(s,i,σ,τ,sp)`) and *not* on cesam's variable-bilinear or sroute's conditional-constant derivatives — the sole blocker between the proven emission and the +1 genuine floor (methodology→genuine, 75→76).

**What to do:** (1) re-read `SPRINT_36/DAY2_MARKOV_OFFDIAG_CONTROL.md`, `DAY3_MARKOV_BANK.md`, `MARKOV_OFFDIAGONAL_DESIGN.md`; (2) characterize the three off-diagonal derivative structures at the IR/AST level as they reach `_add_indexed_jacobian_terms` — markov (genuine param-ref coupling), sroute (conditional-constant `1$(darc(ip,ipp))`), cesam (variable-bilinear); (3) design the discriminating predicate (e.g. "the off-diagonal coefficient is a *parameter reference* whose index tuple couples the constraint's aliased index and the variable's independent index") against concrete IR node types (`ParamRef`, `IndexOffset`, `SubsetIndex`, conditional `$`); (4) locate the lowest-blast-radius hook point in `_add_indexed_jacobian_terms` / `_compute_index_offset_key`; confirm composition with the diagonal-Kronecker path doesn't disturb the 63+30 matches; (5) specify the Phase-0 gate — the discriminator drives `kkt_residual.py markov` → `CASE_A` + cold match 2401.577 AND `make leak-check MODEL=markov` (Task 3) shows **only markov drifts** full-corpus (cesam/ferts/sroute byte-identical); (6) write the Phase-0 issue-doc skeleton with the 4 `### ` Acceptance-Gate subsections BEFORE any src commit; (7) document the REPLAN exit (narrower per-signature allowlist if the predicate over-generalizes).

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_37/MARKOV_DISCRIMINATOR_DESIGN.md` — the three-structure characterization, the discriminating predicate (against IR node types), the hook point, the Phase-0 gate (harness + full-corpus leak-check + fixture), and the REPLAN exit.
- `docs/issues/ISSUE_1110_markov-sigma-sp-discriminator.md` — the Phase-0 acceptance-gate skeleton (4 `### ` subsections), authored before the src commit. *(Created by Task 4; the number is now resolved.)*
- The `shape_markov_diagonal_kronecker` fixture spec (fail-before/pass-after), to land with the fix under P7.
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.2, 1.3, 1.4, 1.5.

**Unknowns to verify:** **1.2** (a derivative-structure discriminator distinguishes markov's param-coupled `σ=sp` from cesam's variable-bilinear and sroute's conditional-constant), **1.3** (the discriminator passes the full-corpus 163-golden leak gate — with Task 3), **1.4** (markov cold-solves to `model_optimal` + genuine match at `CASE_A` — the methodology→genuine +1), **1.5** (the markov discriminator co-exists with the fawley P4 change in the shared function — joint change-surface map, with Task 6).

Then update `PREP_PLAN.md` (Task 4 → ✅ COMPLETE, Changes/Result, ACs), update `CHANGELOG.md`, run the quality gate **only if** `*.py` changed (a fixture spec/design is docs-only; if you land the `shape_markov_diagonal_kronecker` fixture in `tests/`, the gate is mandatory), commit as `Complete Sprint 37 Prep Task 4: markov P1 Derivative-Structure Discriminator Design`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 5 Prompt — ganges/gangesx P2: ≥5-Blocker Cascade Re-Verification & Recovery Sequencing

On a new branch `planning/sprint37-task5` (from `main`), execute Sprint-37 Prep Task 5. **Depends on Tasks 1, 2.** (Priority: High; est. 3–4h.)

**Objective:** Re-verify the ganges/gangesx cascade fixes still apply on current `main`, characterize the two terminal blockers (`$66` cold, `rPower` presolve) sharply enough to bound whether the +2 recovery is landable in-sprint, and sequence the atomic recovery so a partial never churns goldens for 0 bucket.

**What to do:** (1) re-read `SPRINT_36/DAY8_P4_GANGES_BANK.md`, `GANGES_RECOVERY_SEQUENCING.md`, `SPRINT_35/DAY3_P4_BANK_CARRYFORWARD.md` (§5 `_diff_prod`); (2) re-apply the cascade fixes on current `main` (git `a8ff626c` + the `_diff_prod` §5 patch) → confirm `$141`/`$145`/`$149` → 0 for both ganges AND gangesx; (3) characterize `$66` sharply — which calibration params are unassigned-but-referenced, why the presolve gate leaves them cold, whether a fix is bounded, and the `ac(i+2,r)` match-correctness risk; (4) characterize `rPower` sharply — confirm the #1378/#1424 class (non-idempotent `$onMultiR` re-run of `.l`-based power calibrations) and whether an NA-guard/reset idiom (cf. the P7 robustlp `.L`-guard) can break it, or it needs the deep treatment; (5) sequence the atomic recovery (cascade → `$66` → `rPower`) with per-step Phase-0 gates (per-model emit → compile → count `$NNN` (assert 0) → solve cold AND presolve → bucket → match; each `--resolve-changed`-gated; determinism ×3; 335s goldens on a nightly slot); (6) bound the P2 outcome (+2 target or "general `$149` fix + documented `$66`/`rPower` residual") and note the dinam/indus/turkpow/clearlak `$149`-half spillover.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_37/GANGES_RECOVERY_DESIGN.md` — the re-verified cascade-fix status, the sharpened `$66`/`rPower` characterizations (bounded-fix vs deep-class verdict), the atomic recovery sequence with per-step Phase-0 gates, and the bounded P2 outcome.
- The dinam/indus/turkpow/clearlak `$149`-half spillover noted for P6's residual cohort.
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 2.2, 2.3, 2.4.

**Unknowns to verify:** **2.2** (`$66` is a bounded emit fix or a deeper divergence — the `ac(i+2,r)` match risk), **2.3** (`rPower` is tractable in-sprint or the deep #1378/#1424 class), **2.4** (the recovery is atomic +2-or-0; the general `$149` fix unblocks dinam/indus/turkpow/clearlak).

Then update `PREP_PLAN.md` (Task 5 → ✅ COMPLETE, Changes/Result, ACs), update `CHANGELOG.md`, run the quality gate **only if** `*.py` changed (this task is expected docs/analysis-only — scratch re-applies are reverted), commit as `Complete Sprint 37 Prep Task 5: ganges/gangesx P2 Cascade Re-Verification & Recovery Sequencing`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 6 Prompt — fawley P4: Emission-Path Location & Constraint-Index-Diagonal Discriminator Design

On a new branch `planning/sprint37-task6` (from `main`), execute Sprint-37 Prep Task 6. **Depends on Tasks 1, 2, 3, 4.** (Priority: High; est. 4–6h — must follow Task 4; they share `_add_indexed_jacobian_terms`.)

**Objective:** Locate the actual `qsb`/`pbal` emission path (which the S36 Day-4 attempt found ≠ the design's assumed partial-overlap branch), design the rebuilt constraint-index-diagonal orientation predicate + discriminator that ships the confirmed `stat_bq` correction (473→1.14e-13), and verify it composes with the P1 markov change in the shared `_add_indexed_jacobian_terms` without leaking full-corpus. fawley P4 is 0-bucket (H-b); the +Solve is a Sprint-38 consultation.

**What to do:** (1) re-read `SPRINT_36/DAY4_FAWLEY_DEFER.md`, `FAWLEY_DISCRIMINATOR_DESIGN.md`, `DAY11_P5_CONSULTATION.md` §4; (2) locate the `qsb`/`pbal` emission path — trace where these terms actually reach `_add_indexed_jacobian_terms` and why the S35 orientation predicate no longer fires there (reverted/absent); (3) rebuild the constraint-index-diagonal orientation predicate against current-tree IR node types; (4) layer the discriminator (summed constraint index absent from the derivative coefficient) so it fires only on fawley; confirm on paper against Task 4's markov predicate that the two are mutually exclusive in `_add_indexed_jacobian_terms` (the collision-avoidance step — the S35 fawley-leak-onto-markov precedent); (5) specify the Phase-0 gate — the discriminator drives `max|stat_bq| → 0` AND `make leak-check MODEL=fawley` (Task 3) shows **only fawley drifts** (markov + the 2-D cohort byte-identical) AND the `shape_fawley_2d_second_index` fixture fails-before/passes-after; (6) write the Phase-0 issue-doc skeleton (4 `### ` subsections) before any src commit; (7) frame the stronger-continuation/reformulation +Solve question for the Sprint-38 PATH consultation (the `--force` survey was NEGATIVE — NOT a Sprint-37 emit fix).

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_37/FAWLEY_DISCRIMINATOR_REFRESH.md` — the located `qsb`/`pbal` emission path, the rebuilt orientation predicate, the fawley/markov mutual-exclusion analysis, the Phase-0 gate (`max|stat_bq|→0` + `make leak-check MODEL=fawley` + fixture), and the Sprint-38 +Solve consultation hand-off.
- `docs/issues/ISSUE_<N>_fawley-constraint-index-diagonal.md` — the Phase-0 acceptance-gate skeleton (4 `### ` subsections).
- The `shape_fawley_2d_second_index` fixture spec (fail-before/pass-after), to land with the fix under P7.
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 4.1, 4.2, 4.4.

**Unknowns to verify:** **4.1** (where the `qsb`/`pbal` emission path actually runs — ≠ the design's partial-overlap branch), **4.2** (the orientation predicate can be rebuilt + layered with a discriminator that co-exists with the markov P1 change — full-corpus leak-clean), **4.4** (fawley's +Solve is H-b — the `--force` survey NEGATIVE → a Sprint-38 consultation).

Then update `PREP_PLAN.md` (Task 6 → ✅ COMPLETE, Changes/Result, ACs), update `CHANGELOG.md`, run the quality gate **only if** `*.py` changed (design/fixture-spec is docs-only; if you land the `shape_fawley_2d_second_index` fixture in `tests/`, the gate is mandatory), commit as `Complete Sprint 37 Prep Task 6: fawley P4 Emission-Path Location & Discriminator Design`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 7 Prompt — sarf P5: Symbolic-Emit Re-Architecture Design Refresh & Blow-Up Re-Measurement

On a new branch `planning/sprint37-task7` (from `main`), execute Sprint-37 Prep Task 7. **Depends on Tasks 1, 2.** (Priority: High; est. 4–5h.)

**Objective:** Refresh the sarf symbolic-emit re-architecture design against current `main`, re-measure the 369K-column blow-up, and specify the atomic re-arch of the `enumerate_variable_instances` → column-index → Jacobian → gradient → stationarity flow (6 call sites) as an O(active=398) symbolic/parametric emit MODE — including the full-corpus-regression-harness precondition (Task 3) without which it cannot land.

**What to do:** (1) re-read `SPRINT_36/DAY6_SARF_BANK.md`, `SARF_DESIGN_REFRESH.md`; (2) re-measure the blow-up on current `main` (capped sarf emit → confirm >100s / non-terminating; record the column count ~369,024); (3) refresh the 6-call-site inventory (re-locate the enumeration→column-index→Jacobian→gradient→stationarity flow; note drift); (4) specify the O(active=398) symbolic/parametric emit MODE (active-instance iteration rather than materializing the full 369K space; symbolic `stat_task` 7-term reproduction); (5) make the P7-harness precondition explicit — the re-arch lands only after the Task-3 full-corpus harness is wired (the byte-stable proof the symbolic-branch predicate is sarf-only); document the sarf-after-P7-harness ordering; (6) design the Phase-0 gate (PR20: O(active) not O(369K), single-digit-second emit, `stat_task` matches the 7-term derivation, byte-stable golden, determinism ×3, full-corpus `--resolve-changed`); (7) document the REPLAN exit (re-scope if the parametric emit re-triggers the timeout).

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_37/SARF_REARCH_REFRESH.md` — the re-measured blow-up (column count + timing), the refreshed 6-call-site inventory, the O(active=398) emit MODE spec, the explicit P7-harness precondition + ordering, the Phase-0 gate (PR20), and the REPLAN exit.
- The sarf-after-P7-harness ordering dependency flagged for the Task-11 schedule.
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 5.2, 5.3.

**Unknowns to verify:** **5.2** (the O(active=398) symbolic/parametric emit form passes GAMS-54 instantiation), **5.3** (the re-arch can land against the full-corpus regression harness — the P7 precondition + the sarf-after-harness ordering).

Then update `PREP_PLAN.md` (Task 7 → ✅ COMPLETE, Changes/Result, ACs), update `CHANGELOG.md`, run the quality gate **only if** `*.py` changed (this task is expected docs/analysis-only — the guarded-emit fragment is a `/tmp` GAMS compile, not a `src/` change), commit as `Complete Sprint 37 Prep Task 7: sarf P5 Symbolic-Emit Re-Architecture Design Refresh`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 8 Prompt — GAMS-54 v54 Re-Baseline Harness Plan + turkey Testbed Procurement (P6)

On a new branch `planning/sprint37-task8` (from `main`), execute Sprint-37 Prep Task 8. **Depends on Tasks 1, 2.** (Priority: Medium; est. 3–4h.)

**Objective:** Plan the two P6 deliverables: (a) the full GAMS-54 v54 re-baseline of the 142 candidates (demo-runnable) with the v53→v54 bucket-diff + the canonical-version decision procedure, and (b) the turkey +1 realization, which needs a licensed >1000-row GAMS-54 testbed (turkey's MCP is 3,866 rows) — including procuring or confirming the absence of such an environment.

**What to do:** (1) re-read `SPRINT_36/GAMS54_TESTBED_PLAN.md` §3–§4, `SPRINT_35/FOLLOWUPS_GAMS54_TRANSITION.md`; (2) plan the v54 demo re-baseline procedure — the `run_full_test.py` invocation to re-solve the 142 candidates under GAMS 54 demo, the bucket-diff vs the v53 DB, and the re-check of the 5 OBJ-GAP models (agreste/cesam/chain/fawley/rocket); define the output `GAMS54_REBASELINE_DIFF.md`; (3) define the canonical-version decision rule (re-pin to v54 only on confirmed **zero bucket regressions**; else keep v53, and specify what "regression" means — a bucket downgrade vs a neutral churn); (4) turkey testbed procurement — determine whether a licensed >1000-row GAMS-54 environment is procurable in the sprint window (a licensed local install, a cloud GAMS, or a CI secret); if yes, plan the turkey re-solve; if no, document turkey as license-gated (+1 deferred) with the exact blocker; (5) scope the residual multi-root cohort (turkpow/clearlak/dinam/indus — the P2 general `$149` fix unblocks their `$149` half; flag any bounded per-model tail effort).

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_37/GAMS54_REBASELINE_PLAN.md` — the v54 demo re-baseline procedure, the canonical-version decision rule, the turkey testbed procurement verdict (procurable → plan / not → license-gated), and the residual-cohort scoping.
- A go/no-go on turkey's +1 for the sprint (testbed available vs deferred).
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 6.1, 6.2, 6.3.

**Unknowns to verify:** **6.1** (a licensed >1000-row GAMS-54 testbed is procurable for turkey's 3,866-row MCP), **6.2** (the full v54 demo re-baseline of the 142 candidates shows zero bucket regressions — the re-pin decision), **6.3** (which of the 5 OBJ-GAP models shift buckets under v54; the `$149` fix unblocks the residual cohort).

Then update `PREP_PLAN.md` (Task 8 → ✅ COMPLETE, Changes/Result, ACs), update `CHANGELOG.md`, run the quality gate **only if** `*.py` changed (this task is expected docs/analysis-only — the demo re-solve, if run, does not change `src/`), commit as `Complete Sprint 37 Prep Task 8: GAMS-54 v54 Re-Baseline Plan + turkey Testbed Procurement`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 9 Prompt — Consultation Reply-Integration Prep (rocket/mine P3) + camcge Epic-5 Walras Gate Scoping

On a new branch `planning/sprint37-task9` (from `main`), execute Sprint-37 Prep Task 9. **Depends on Tasks 1, 2.** (Priority: Medium; est. 2–3h.)

**Objective:** Prepare the P3 consultation cycle: stage the integration of the PATH authors' reply to the rocket #1462 submission (map the recommended option-set into `--force homotopy`), track the mine primal-degenerate-LP question, and scope the camcge three-part dual-consistent Walras redefinition as the Epic-5 gate (with the per-model-numéraire fallback).

**What to do:** (1) re-read `SPRINT_36/DAY11_P5_CONSULTATION.md`, `CONSULTATION_BUNDLE.md`, `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`, `SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md`, `EPIC_5/CGE_DEGENERACY_SCOPING.md`; (2) stage the rocket reply integration — document how a recommended PATH option-set / continuation schedule maps into the `--force homotopy` scaffold; check whether the reply has arrived (update the Task-1 unknown); keep the Case-c sign flip BANNED; (3) track the mine question — confirm the primal-degenerate-LP reconciliation question is posed and 0-bucket (LP-side reformulation out of emit scope); `x.up=inf` stays BANNED; (4) scope the camcge Epic-5 Walras gate — specify the three-part dual-consistent Walras redefinition (numéraire + the Walras-law dual redefinition, the row-redundancy fix) as a `/tmp` demo control (641 rows) targeting MS-1; frame it as an Epic-5 deliverable (NOT a Sprint-37 bucket) with the per-model-numéraire fallback; (5) set the P3 expectations (rocket +1 contingent, mine 0, camcge Epic-5).

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_37/CONSULTATION_INTEGRATION_PREP.md` — the rocket reply-to-`--force`-homotopy integration staging, the mine question tracking (0-bucket), and the camcge three-part Walras Epic-5 gate scoping (with the per-model-numéraire fallback).
- The P3 bucket expectations set (rocket +1 contingent / mine 0 / camcge Epic-5).
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 3.1, 3.2, 3.3, 3.4.

**Unknowns to verify:** **3.1** (the PATH authors' rocket #1462 reply has arrived and maps to a `--force homotopy` option-set — +1 contingent), **3.2** (the mine primal-degenerate-LP question is truly 0-bucket), **3.3** (the camcge three-part Walras redefinition is reachable to MS-1 in a `/tmp` demo control — 641 rows), **3.4** (the per-model-numéraire fallback is the correct Epic-5 scoping — the two-nullspaces diagnosis).

Then update `PREP_PLAN.md` (Task 9 → ✅ COMPLETE, Changes/Result, ACs), update `CHANGELOG.md`, run the quality gate **only if** `*.py` changed (this task is a submission/scoping day — docs/analysis-only), commit as `Complete Sprint 37 Prep Task 9: Consultation Reply-Integration Prep + camcge Epic-5 Walras Gate Scoping`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 10 Prompt — Property-Fixture Catalog + Phase-0-Doc-Enforcement + Genuine-Floor Tracking (P7)

On a new branch `planning/sprint37-task10` (from `main`), execute Sprint-37 Prep Task 10. **Depends on Tasks 1, 3, 4, 6.** (Priority: Medium; est. 3–4h.)

**Objective:** Catalog the P7 infrastructure deliverables: the property fixtures for the landed tracks (`shape_markov_diagonal_kronecker` from Task 4, `shape_fawley_2d_second_index` from Task 6), the Phase-0-doc CI enforcement check, and the genuine-floor tracking (anchor 75 → ≥76 if markov lands) + the Epic-4 `SUMMARY.md` row-37 continuation.

**What to do:** (1) re-read `SPRINT_36/FIXTURE_AND_HARNESS_CATALOG.md`, `CONTRIBUTING.md` §392–447 (the Phase-0 rule); (2) catalog the two property fixtures (consolidate the Task-4 `shape_markov_diagonal_kronecker` + the Task-6 `shape_fawley_2d_second_index` specs — each fail-before/pass-after, landing with its fix; note any additional shape fixtures); (3) design the Phase-0-doc CI enforcement — a lint/CI check that any PR touching `src/{ad,kkt,emit}` has a `docs/issues/ISSUE_<N>_*.md` with the `## Phase 0: Acceptance Gate` heading + 4 `### ` subsections; specify the changed-path trigger + the failure message; draft it (wiring in-sprint); (4) specify the genuine-floor tracking update (the PR25 recompute with the S37 anchor 75 → ≥76 if markov lands; the methodology→genuine bookkeeping); (5) continue the Epic-4 `SUMMARY.md` groundwork (draft the row-37 skeleton); (6) cross-check with the Task-3 leak harness — confirm the fixtures + the Phase-0 check + the leak gate compose into one coherent P7 "emit-PR gate" story for the schedule.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_37/P7_INFRA_CATALOG.md` — the consolidated property-fixture catalog, the Phase-0-doc CI enforcement design (trigger + failure message), the genuine-floor tracking update spec (anchor 75 → ≥76 if markov lands), and the Epic-4 SUMMARY row-37 skeleton.
- The coherent "emit-PR gate" story (leak harness + fixtures + Phase-0 check) for the Task-11 schedule.
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 7.2, 7.3, 7.4.

**Unknowns to verify:** **7.2** (where the Phase-0-doc CI enforcement check hooks — the changed-path glob), **7.3** (the property fixtures fail-before/pass-after and skip-if-absent), **7.4** (the genuine-floor tracking holds at anchor 75 at S37 open — jointly with Task 2; markov ∈ methodology → the +1 is real).

Then update `PREP_PLAN.md` (Task 10 → ✅ COMPLETE, Changes/Result, ACs), update `CHANGELOG.md`, run the quality gate **only if** `*.py`/CI-workflow/`scripts/` changed (a design draft is docs-only; if you land the CI check or a fixture, the gate is mandatory), commit as `Complete Sprint 37 Prep Task 10: Property-Fixture Catalog + Phase-0-Doc CI + Genuine-Floor Tracking`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 11 Prompt — Plan Sprint 37 Detailed Schedule

On a new branch `planning/sprint37-task11` (from `main`), execute Sprint-37 Prep Task 11. **Depends on all tasks (1–10).** (Priority: Critical; est. 3–4h — the final prep task.)

**Objective:** Create `docs/planning/EPIC_4/SPRINT_37/PLAN.md` — the day-by-day (Day 0 + Days 1–13) Sprint-37 schedule incorporating every prep-task design, with per-priority budgets, checkpoint gates (Days 5, 10), REPLAN exits, and the Day-0 GO/NO-GO readiness gate. This task integrates all verified unknowns from Tasks 2–10.

**What to do:** (1) re-read `SPRINT_36/PLAN.md` (the schedule precedent) + `PROJECT_PLAN.md` Sprint 37 (the per-priority budgets P1 16–22h / P2 18–24h / P3 12–16h / P4 14–18h / P5 20–28h / P6 10–14h / P7 12–16h / retest 4h = 106–142h); (2) sequence the days front-loading markov P1 (Days 1–3, the PROCEED/REPLAN gate early), with fawley P4 *after* markov P1 (shared `_add_indexed_jacobian_terms`) and sarf P5 *after* the P7 leak harness (its precondition); interleave P3 (external-reply-paced), P6 (testbed-gated), P7 (infra, continuous); (3) assign per-priority budgets across the days at ≤12h/day; identify the heaviest day (~11h); (4) place the checkpoints (Day 5 Checkpoint 1, Day 10 Checkpoint 2) with `--resolve-changed` + no-regression gates; (5) write the per-priority REPLAN exits (each pointing at its Task-3–10 design's documented exit); (6) define the Day-0 GO/NO-GO gate (baseline re-confirmed [Task 2] + leak harness wired [Task 3] + markov/fawley Phase-0 docs exist [Tasks 4, 6]); (7) map each remaining INCOMPLETE unknown to its resolving sprint day.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_37/PLAN.md` — the day-by-day (Day 0 + Days 1–13) schedule with per-priority budgets, the markov-first front-loading, the fawley-after-markov and sarf-after-P7-harness ordering, the Day-5/Day-10 checkpoints, the per-priority REPLAN exits, and the Day-0 GO/NO-GO readiness gate.
- `docs/planning/EPIC_4/SPRINT_37/prompts/PLAN_PROMPTS.md` — the per-day execution prompts (mirroring prior sprints).
- A prep-completion GO/NO-GO summary (all Critical prep tasks complete → Sprint 37 ready).
- Updated `KNOWN_UNKNOWNS.md` — confirm all unknowns resolved (or the residual INCOMPLETE ones mapped to a resolving sprint day); note that Task 11 integrates all verified unknowns.

**Unknowns to verify:** **All (integration)** — Task 11 integrates every Task-2–10-verified unknown into the schedule, the REPLAN exits, and the Day-0 GO/NO-GO; confirm zero unmapped Day-0 blockers remain.

Then update `PREP_PLAN.md` (Task 11 → ✅ COMPLETE, Changes/Result, ACs; note all 11 prep tasks complete → **GO for Sprint 37 Day 0**), update `CHANGELOG.md`, run the quality gate **only if** `*.py` changed (this task is docs-only), commit as `Complete Sprint 37 Prep Task 11: Plan Sprint 37 Detailed Schedule`, push, open a PR, and wait for reviewer comments.

---

**Document Status:** ✅ Complete — Sprint 37 prep task prompts (Tasks 2–11).
**Last Updated:** 2026-08-09 · **Owner:** Sprint 37 Planning Team

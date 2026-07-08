# Sprint 31 Prep Task Execution Prompts

Self-contained prompts for Sprint 31 Prep Tasks 2–10. Each prompt can be copy-pasted into a new conversation to execute one prep task end-to-end, including the Known Unknowns updates, PREP_PLAN.md / CHANGELOG.md updates, quality gate, commit, and PR.

**Usage:**

1. Pick a task prompt below.
2. Paste it into a new conversation.
3. The agent creates the branch (`planning/sprint31-task<N>`), does the work, runs the quality gate, commits, pushes, and opens a PR.
4. Wait for reviewer comments on the PR.

Task 1 (Create Sprint 31 Known Unknowns List) is already ✅ COMPLETE — no prompt needed.

Tasks 2–10 are dispatchable in the following order per the Prep Task Overview table (Dependencies column) + the Critical/Secondary/Tertiary/Quaternary Path notes in `docs/planning/EPIC_4/SPRINT_31/PREP_PLAN.md` (Task 1 is done, so the tasks that depend only on it — or on nothing — are immediately dispatchable):

- **Immediately dispatchable:** Task 2 (no dependencies), Task 5 + Task 8 (need only the completed Task 1)
- **After Task 2:** Task 3 (the head-offset IR-plumbing design reuses the Day-0 baseline / mine bucket) + Task 4 (the offset-alias re-confirmation reuses the polygon bucket)
- **After Task 8:** Task 9 (the backlog fix-surface analysis reuses the tooling audit)
- **After Tasks 1 + 3 + 4 + 5:** Task 6 (the Phase-0 gate refresh consumes the three design docs)
- **After Tasks 3 + 4 + 5 + 6:** Task 7 (the REPLAN assessment consumes the designs + the gates)
- **After all (final integration):** Task 10

**Critical path:** Task 1 → Task 3 → Task 6 → Task 7 → Task 10.

**Cross-cutting conventions for every prompt below:**

- Branch from `main`; PR targets `main`.
- User preferences (enforce in every commit/PR): **NO `Co-Authored-By` lines** in commit messages; **NO "Generated with Claude Code"** in PR descriptions.
- Replace `YYYY-MM-DD` with the actual date at execution time.
- These are **docs/design/analysis-only** prep tasks — no Python source changes are expected (the fixes/scripts they design are *built in-sprint*, not in prep; the KKT-residual harness, presolve-divergence detector, golden-staleness gate, `--resolve-changed` mode, and the `--force` scaffold already exist on `main`). Run the full quality gate before committing regardless; if you did touch Python, it must pass.
- **PR24 discipline:** every banked Sprint-30 recipe is a Day-0-re-confirm *hypothesis*, never fact (Sprint 30 refuted five banked diagnoses via control experiments before any bad ship — the obj-grad sign flip 3×, the Class-B `stat_pz` "coefficient bug" which was case-normalization, and the camcge drop-row which broke the dual). Record the symptom + reproducer; frame the fix surface as a hypothesis to re-trace, and gate any high-blast-radius change on a control experiment.
- **Check the dual side** (the Sprint-30 camcge lesson): any structural transform that drops/adds rows must be verified against the KKT *dual*, not just the primal solution set.
- Every Known-Unknowns update uses the verification block: **Status** (✅ VERIFIED / ❌ WRONG), **Verified by**, **Date**, **Findings**, **Evidence**, **Decision**.

---

## Task 2 Prompt: Sprint 30 → Sprint 31 Day-0 Baseline + Genuine-Floor Re-Baseline (PR15 + PR17 + PR25)

**Branch:** Create a new branch named `planning/sprint31-task2` from `main`

**Priority:** Critical (3–4 hours)

**Objective:** Establish the authoritative Sprint 31 Day-0 baseline — the per-model bucket provenance (Parse / Translate / Solve / Match / model_infeasible / path_*) carried forward from the Sprint 30 final retest — and re-run the PR25 genuine-vs-methodology re-baseline so the genuine-floor ramp (70 → ≥73) is measured against a clean starting line, not the methodology-inflated Match 92. This is lighter than a from-scratch baseline because the re-baseline tooling and discipline already exist (Sprint 29 Priority 8 built `--resolve-changed` + the PR25 re-baseline step) — this task *applies* them to the Day-0 DB, it does not build them.

**Unknowns Verified:** 7.2 (and contributes the per-target Day-0 bucket to 1.3 / 2.1 / 3.1 / 5.1 / 6.1)

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_31/PREP_PLAN.md` §Task 2
- `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md` §Unknown 7.2 (genuine-floor tracking baseline) + the Category 1/2/3/5/6 per-target unknowns
- `docs/planning/EPIC_4/SPRINT_30/BASELINE_METRICS.md` (the bucket-provenance + genuine-vs-methodology template) + `docs/planning/EPIC_4/SPRINT_30/SPRINT_RETROSPECTIVE.md` §1 (the final metrics table: Solve 107 / Match 92 / genuine floor 70 / model_infeasible 7 / Translate 135 / Tests 4,997) + `docs/planning/EPIC_4/SPRINT_30/SPRINT_LOG.md` §"Day 13" (the final PR25 tally)
- `data/gamslib/gamslib_status.json` (the Sprint 30 final retest DB) + `scripts/gamslib/run_full_test.py` `--resolve-changed` mode + the `_cold_objective_mismatches_nlp` methodology source
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 31" (the footnote-⁸ Match re-baseline / genuine-floor ramp)

**Tasks to Complete:**

1. Assert Day-0 = Sprint 30 final — derive the close SHA and diff automatically (no manual placeholder lookup):
   ```bash
   # Use the OLDEST match (| tail -1) — later prep commits quote "SPRINT 30 CLOSED", so `-1` (newest)
   # would resolve to a docs-only review-fix commit, not the true close.
   S30=$(git log --grep='SPRINT 30 CLOSED' --format=%H | tail -1)
   git diff --quiet "$S30"..HEAD -- src/ scripts/ && echo "no src/ drift — reuse the committed DB, no fresh ~4h retest" || git diff --stat "$S30"..HEAD -- src/ scripts/
   ```
2. Recompute the canonical bucket tally from the committed DB (`get_candidate_models`, canonical 142): Solve 107 / Match 92 / model_infeasible 7 / Translate 135. Enumerate the 7 model_infeasible + the path_syntax_error / path_solve_terminated / path_solve_license members by name.
3. Re-run the PR25 genuine-vs-methodology partition — classify each of the 92 Match models genuine-cold vs methodology (warm/presolve/broadened-retry) so the genuine floor **70** is reproduced from first principles; identify the Sprint-31 targets that convert a methodology match to genuine (polygon [P2], hhfair + irscge/lrgcge/moncge [P5]) → the "genuine floor → ≥73" conversion map + the footnote-⁸ ramp alignment.
4. Pin the per-Sprint-31-target Day-0 bucket + projected delta (mine, polygon, camcge, sarf, hhfair + the CGE cluster, rocket), each labeled genuine bucket-to-success vs already-banked (mirror `SPRINT_30/BASELINE_METRICS.md`).
5. Confirm the `--resolve-changed --since-commit <Sprint-30-final-SHA>` checkpoint anchor selects the expected changed-emit set.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_31/BASELINE_METRICS.md` — Day-0 = Sprint 30 final; canonical bucket tally; genuine-floor-70 carry-forward + the genuine-vs-methodology partition; per-Sprint-31-target bucket provenance with PR25 projection labels
- Confirmation that no fresh retest is needed (no `src/` drift since the S30 close) + the checkpoint anchor
- Updated KNOWN_UNKNOWNS.md with verification results for Unknown 7.2 (genuine-floor baseline)
- CHANGELOG.md updated with the Task 2 completion entry

**Known Unknowns Updates:** For Unknown 7.2 in `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md`, set the "Verification Results" subsection: Status ✅ VERIFIED (or ❌ WRONG + correction), Verified by Task 2, Date, Findings (the genuine-floor-70 reproduction + the footnote-⁸ ramp alignment), Evidence (DB recompute + partition), Decision (the ≥73 conversion map). Also record the Day-0-bucket aspect of 1.3/2.1/3.1/5.1/6.1 (their fix-surface aspect is verified by Tasks 3/4/5/9).

**PREP_PLAN.md Updates:** In §Task 2: `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`; add `**Completed:** YYYY-MM-DD`; fill "Changes" (what was measured/authored) + "Result" (the Day-0 baseline + genuine floor 70); check off all Acceptance Criteria (`- [ ]` → `- [x]`).

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 31 Prep`, prepend:
```markdown
- **Prep Task 2 COMPLETE (YYYY-MM-DD):** Sprint 31 Day-0 baseline = Sprint 30 final (Solve 107 / Match 92 / genuine floor 70 / model_infeasible 7 / Translate 135 / Tests 4,997; no fresh retest — no `src/` drift). Genuine floor 70 reproduced from the PR25 partition with the genuine-floor → ≥73 conversion map (polygon P2 / hhfair+CGE P5) + the footnote-⁸ ramp alignment. Per-Sprint-31-target Day-0 bucket + PR25 projection labels. `--resolve-changed` checkpoint anchor confirmed. Verified Unknown 7.2.
```

**Quality Gate:**
```bash
make typecheck && make format && make lint && make test
```
Docs-only task — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 31 Prep Task 2: Day-0 Baseline + Genuine-Floor Re-Baseline

Day-0 = Sprint 30 final (Solve 107 / Match 92 / genuine floor 70 / model_infeasible 7
/ Translate 135 / Tests 4,997; no fresh retest — no src/ drift since the S30 close).
Genuine floor 70 reproduced from the PR25 partition with the genuine-floor -> >=73
conversion map. Per-Sprint-31-target Day-0 bucket + PR25 projection labels.
--resolve-changed checkpoint anchor confirmed.

## Deliverables
- docs/planning/EPIC_4/SPRINT_31/BASELINE_METRICS.md
- KNOWN_UNKNOWNS.md: Unknown 7.2 verified
- PREP_PLAN.md: Task 2 -> COMPLETE
- CHANGELOG.md: Task 2 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint31-task2
gh pr create --title "Complete Sprint 31 Prep Task 2: Day-0 Baseline + Genuine-Floor Re-Baseline" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs-only)
- [x] BASELINE_METRICS.md records Day-0 = Sprint 30 final + per-target buckets + the genuine-floor-70 carry-forward
- [x] Day-0 = Sprint 30 final confirmed (git diff empty)
- [x] Unknown 7.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 2 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 3 Prompt: mine Head-Offset IR-Plumbing Design + Round-Trip Reproduction (Priority 1 Foundation)

**Branch:** Create a new branch named `planning/sprint31-task3` from `main`

**Priority:** Critical (5–7 hours)

**Objective:** Turn the Sprint-30 Day-6 REPLAN of #1443 into a concrete **IR-plumbing design** — specify where the head-offset detail (position `l`, amount `+1`) + the parameter offsets `li(k)`/`lj(k)` are stored on `EquationDef`, how they survive normalization (which today collapses `pr.domain` to `(k,l,i,j)` and loses the `l+1` head), and how the KKT layer reads them — then establish the minimal round-trip unit reproduction that gates the Phase-2 shared 3-site helper. This is the deepest carryforward; sizing it before the schedule is the critical-path prerequisite. **This is a DESIGN task — no `src/` change; the IR plumbing is built in-sprint.**

**Unknowns Verified:** 1.1, 1.2, 1.3, 1.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_31/PREP_PLAN.md` §Task 3
- `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md` §Category 1 (Unknowns 1.1 IR round-trip, 1.2 shared-helper-vs-4th-site, 1.3 cold-LCP, 1.4 blast radius)
- `docs/issues/ISSUE_1443_*.md` (the head-offset 3-site trace + the "not stored in IR" blocker + the cold-INFES-by-direction characterization ~4.07e10) + `docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md` (the 3-site architecture)
- The IR + pipeline sites (read-only): `src/ir/ast.py` (`EquationDef`, `IndexOffset`, `has_head_domain_offset`), `src/ir/normalize.py` (the head-offset collapse), `src/kkt/stationarity.py` (the landed `stat_x` cross-term), `src/emit/emit_gams.py` `_emit_nlp_presolve` (the dual transfer)
- `scripts/diagnostics/kkt_residual.py` (the cold-LCP Case-(a/b/c) verdict) + `tests/integration/emit/test_ad_crossterm_shapes.py` (`shape4_parameter_valued_offset` is the closest existing guard; the new head-offset fixture is the P7 deliverable this design specifies)

**Tasks to Complete:**

1. **Specify the IR storage** — the `EquationDef` fields (or an `IndexOffset`-carrying structure) that store the head-offset position (`l`) + amount (`+1`) + the body param offsets `li(k)`/`lj(k)`, replacing the bare `has_head_domain_offset` bool; enumerate every producer (parser) + consumer (normalize, KKT, emit) touchpoint (Unknown 1.1).
2. **Design the normalize round-trip** — determine why normalization collapses `pr.domain` to `(k,l,i,j)` and the minimal change that preserves the head-offset detail through `normalize_model` without altering the domain semantics other equations rely on (blast-radius guard, Unknown 1.4).
3. **Author the round-trip unit reproduction** — a minimal mine-shaped fixture (committed under `tests/fixtures/`) whose parse→normalize output can be asserted to carry the head-offset δ + `li(k)`/`lj(k)` — the Phase-1 gate before any emit change (Unknown 1.1).
4. **Specify the Phase-2 shared 3-site helper signature** — parameterized by (head-offset δ on `l`, param offsets `li(k)`/`lj(k)`), consumed by `comp_pr` emission + the `--nlp-presolve` dual transfer + the landed `stat_x` cross-term, with the atomic-application requirement (all three or none, Unknown 1.2).
5. **Define the cold-INFES-by-direction success histogram** — the `kkt_residual.py` residual → 0 warm, then cold MS 1, per k-direction — the Phase-2 completion gate (Unknown 1.3). Name the 4th-site REPLAN exit (deeper architecture → Sprint 32).

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_31/HEAD_OFFSET_IR_PLUMBING_DESIGN.md` — the `EquationDef` head-offset storage design, the normalize round-trip design + blast-radius guard, the round-trip unit-reproduction spec, the Phase-2 shared 3-site helper signature, the cold-INFES-by-direction success histogram, and the 4th-site REPLAN exit
- The minimal round-trip fixture spec (mine-shaped) for `tests/fixtures/`
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3, 1.4
- CHANGELOG.md updated with the Task 3 completion entry

**Known Unknowns Updates:** For Unknowns 1.1–1.4 in `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md`, set each "Verification Results": Status (✅ VERIFIED / ❌ WRONG + correction), Verified by Task 3, Date, Findings (the IR-round-trip feasibility [1.1], the shared-helper-vs-4th-site sizing [1.2], the cold-LCP-consistency [1.3], the blast radius [1.4]), Evidence (the normalize-collapse trace + the round-trip fixture + the `kkt_residual.py` runs), Decision (PROCEED the IR plumbing / REPLAN mine if the round-trip is a deeper change or a 4th site surfaces).

**PREP_PLAN.md Updates:** In §Task 3: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 31 Prep`, prepend:
```markdown
- **Prep Task 3 COMPLETE (YYYY-MM-DD):** mine head-offset IR-plumbing design + round-trip reproduction (`HEAD_OFFSET_IR_PLUMBING_DESIGN.md`). Specifies the `EquationDef` head-offset storage (δ + `li(k)`/`lj(k)`, replacing the bare `has_head_domain_offset` bool), the normalize round-trip preserving the head-offset detail + the blast-radius guard, the round-trip unit-reproduction fixture (the Phase-1 gate), the shared 3-site helper signature (Phase 2), and the cold-INFES-by-direction success histogram + the 4th-site REPLAN exit. Verified Unknowns 1.1, 1.2, 1.3, 1.4. Docs/design-only (no `src/`; any probes were `/tmp` copies, reverted).
```

**Quality Gate:**
```bash
make typecheck && make format && make lint && make test
```
Docs/design-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 31 Prep Task 3: Head-Offset IR-Plumbing Design + Round-Trip Reproduction

HEAD_OFFSET_IR_PLUMBING_DESIGN.md — the EquationDef head-offset storage (delta +
li(k)/lj(k), replacing the bare has_head_domain_offset bool), the normalize round-trip
+ blast-radius guard, the round-trip unit-reproduction fixture (Phase-1 gate), the shared
3-site helper signature (Phase 2), and the cold-INFES-by-direction success histogram +
the 4th-site REPLAN exit.

## Deliverables
- docs/planning/EPIC_4/SPRINT_31/HEAD_OFFSET_IR_PLUMBING_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 1.1, 1.2, 1.3, 1.4 verified
- PREP_PLAN.md: Task 3 -> COMPLETE
- CHANGELOG.md: Task 3 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint31-task3
gh pr create --title "Complete Sprint 31 Prep Task 3: Head-Offset IR-Plumbing Design + Round-Trip Reproduction" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs/design-only)
- [x] HEAD_OFFSET_IR_PLUMBING_DESIGN.md specifies the EquationDef storage + the normalize round-trip + the round-trip fixture + the shared-helper signature + the cold-INFES histogram
- [x] The 4th-site REPLAN exit is named (deeper architecture → Sprint 32)
- [x] Unknowns 1.1, 1.2, 1.3, 1.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 3 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 4 Prompt: Offset-Alias #1111/#1112 Recipe Re-Confirmation + Distance-Jacobian Second-Index Design (Priority 2 Foundation)

**Branch:** Create a new branch named `planning/sprint31-task4` from `main`

**Priority:** High (4–6 hours)

**Objective:** Re-confirm the Sprint-30 Day-7 control-verified 4-term polygon recipe (warm-match 0.780) on the current tree (PR24 — banked recipe is a hypothesis), and design the coupled **distance-Jacobian second-index cross-term** — the general-alias core `_add_indexed_jacobian_terms` drops — that must land together with the already-verified-but-reverted objective-successor half. **This is a DESIGN task — no `src/` change; the coupled fix is built in-sprint.**

**Unknowns Verified:** 2.1, 2.2, 2.3, 2.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_31/PREP_PLAN.md` §Task 4
- `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md` §Category 2 (Unknowns 2.1 recipe re-confirm, 2.2 coupled second-index, 2.3 tight-gate-vs-core, 2.4 himmel16 non-convex)
- `docs/issues/ISSUE_1143_*.md` (the control-verified 4-term recipe, Day 7 warm-match 0.780; the Day-8 objective-half implement-and-revert) + `docs/issues/ISSUE_1146_*.md` (himmel16 non-convex, sign-fix refuted)
- GitHub #1111 (alias-aware differentiation), #1112 (dollar-condition propagation), #1110 (multi-pattern Jacobian diagonal-vs-off-diagonal topology)
- The AD sites (read-only): `src/ad/constraint_jacobian.py` (`_add_indexed_jacobian_terms` — the second-index drop), `src/kkt/stationarity.py` (`_build_indexed_gradient_term` — the reverted objective-successor half)
- `tests/integration/emit/test_ad_crossterm_shapes.py` — `shape8_offset_alias_successor` (strict-xfail, the P2 completion gate), `shape7_offset_alias_cyclic` (himmel16 cyclic decomposition guard) + `scripts/diagnostics/kkt_residual.py`

**Tasks to Complete:**

1. **Re-confirm the 4-term recipe** — reproduce the Sprint-30 Day-7 control experiment on the current tree (polygon warm-match 0.780 ≈ NLP 0.7797); record any drift from the banked recipe (PR24 — if it no longer reproduces, re-diagnose before design) (Unknown 2.1).
2. **Locate + specify the second-index restoration** — pin the exact point in `_add_indexed_jacobian_terms` where the second-index cross-term is dropped, and specify the restoration (the general-alias core) + the tight gate to the var-at-two-indices shape (Unknown 2.2).
3. **Confirm #1110 orthogonality** — verify the Issue #1110 multi-pattern (diagonal-vs-off-diagonal) correction is independent of var-at-two-indices, so restoring the second-index term does not regress the CGE multi-pattern cohort (`--resolve-changed` GO list) (Unknown 2.2).
4. **Specify the coupled-landing design + gate** — the objective-successor half + the distance-Jacobian second-index half land together; `shape8_offset_alias_successor` drops its strict-xfail as the completion gate (Unknown 2.3). Confirm the himmel16 non-convex scope guard (no emit fix expected, Unknown 2.4).
5. **Define the Sprint-32 REPLAN exit** — if the gate cannot be made tight, re-scope to the #1111/#1112 AD-engine filing (Unknown 2.3).

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_31/OFFSET_ALIAS_JACOBIAN_DESIGN.md` — the 4-term recipe re-confirmation result, the `_add_indexed_jacobian_terms` second-index restoration design + tight gate, the #1110 orthogonality confirmation, the coupled-landing design with `shape8` as the completion gate, the himmel16 non-convex scope guard, and the Sprint-32 REPLAN exit
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.1, 2.2, 2.3, 2.4
- CHANGELOG.md updated with the Task 4 completion entry

**Known Unknowns Updates:** For Unknowns 2.1–2.4 in `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md`, set each "Verification Results": Status (✅ VERIFIED / ❌ WRONG + correction), Verified by Task 4, Date, Findings (the recipe re-confirmation [2.1], the second-index drop site + #1110 orthogonality [2.2], the tight-gate-vs-core decision [2.3], the himmel16 non-convex confirmation [2.4]), Evidence (the Day-7 control-experiment re-run + the `_add_indexed_jacobian_terms` trace), Decision (localized fix ships / REPLAN to the #1111/#1112 core).

**PREP_PLAN.md Updates:** In §Task 4: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 31 Prep`, prepend:
```markdown
- **Prep Task 4 COMPLETE (YYYY-MM-DD):** offset-alias #1111/#1112 recipe re-confirmation + distance-Jacobian second-index design (`OFFSET_ALIAS_JACOBIAN_DESIGN.md`). Re-confirms the Day-7 control-verified 4-term polygon recipe (warm-match 0.780) on the current tree; locates the `_add_indexed_jacobian_terms` second-index drop + specifies the general-alias-core restoration tightly gated to var-at-two-indices; confirms #1110 multi-pattern orthogonality (no CGE regression); couples the objective-successor half with the second-index half (`shape8` enable = completion gate); records the himmel16 non-convex scope guard + the Sprint-32 #1111/#1112 AD-engine REPLAN exit. Verified Unknowns 2.1, 2.2, 2.3, 2.4. Docs/design-only (no `src/`; probes reverted).
```

**Quality Gate:**
```bash
make typecheck && make format && make lint && make test
```
Docs/design-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 31 Prep Task 4: Offset-Alias Recipe Re-Confirmation + Distance-Jacobian Design

OFFSET_ALIAS_JACOBIAN_DESIGN.md — re-confirms the Day-7 4-term polygon recipe
(warm-match 0.780) on the current tree; locates the _add_indexed_jacobian_terms
second-index drop + specifies the general-alias-core restoration tightly gated to
var-at-two-indices; confirms #1110 orthogonality; couples the objective-successor
half with the second-index half (shape8 enable = completion gate); records the
himmel16 non-convex scope guard + the Sprint-32 #1111/#1112 REPLAN exit.

## Deliverables
- docs/planning/EPIC_4/SPRINT_31/OFFSET_ALIAS_JACOBIAN_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 2.1, 2.2, 2.3, 2.4 verified
- PREP_PLAN.md: Task 4 -> COMPLETE
- CHANGELOG.md: Task 4 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint31-task4
gh pr create --title "Complete Sprint 31 Prep Task 4: Offset-Alias Recipe Re-Confirmation + Distance-Jacobian Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs/design-only)
- [x] The Day-7 4-term recipe is re-confirmed on the current tree (or re-diagnosed if drifted — PR24)
- [x] The second-index restoration is located + tightly gated; #1110 orthogonality confirmed
- [x] `shape8_offset_alias_successor` named as the completion gate; himmel16 non-convex scope guard recorded
- [x] Unknowns 2.1, 2.2, 2.3, 2.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 4 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 5 Prompt: camcge Dual-Consistent Walras Transform Design + Degeneracy-Detector Scope (Priority 3)

**Branch:** Create a new branch named `planning/sprint31-task5` from `main`

**Priority:** High (4–5 hours)

**Objective:** Design the **dual-consistent multiplier redefinition** the Sprint-30 Day-11 analysis proved is needed for camcge (#1330 → Epic 5) — express the dropped market-clearing row's dual via Walras' law so it stays available in the stationarity — plus the S1∧S2∧S3 degeneracy-detection heuristic scope that must flag *only* camcge across the CGE cohort. **This is a DESIGN task — no `src/` change; prototype the redefinition on `/tmp` only.**

**Unknowns Verified:** 3.1, 3.2, 3.3, 3.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_31/PREP_PLAN.md` §Task 5
- `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md` §Category 3 (Unknowns 3.1 dual-consistent redefinition, 3.2 detector false-positive, 3.3 redundant-row + numéraire, 3.4 Walras identity)
- `docs/issues/ISSUE_1330_*.md` (the price-pin recipe `p('services')=pd0` → omega 191.735 / MS-4 + the pinned dual-flaw) + `docs/planning/EPIC_5/CAMCGE_WALRAS_TRANSFORM_DESIGN.md` (the Day-11 refinement + the `CGE_DEGENERACY_SCOPING.md` §3/§5 open questions)
- The CGE cohort for the false-positive check: irscge / lrgcge / moncge / stdcge (well-posed — the detector must pass them through)
- `scripts/diagnostics/kkt_residual.py` (Case-a/b/c verdict on the dual-consistent prototype)
- **Sprint-30 lesson: check the dual side** — the paper-verified primal transform orphans a needed price/wage multiplier; verify against the KKT dual, not just the primal solution.

**Tasks to Complete:**

1. **Design the dual-consistent multiplier redefinition** — specify how the dropped market's dual is re-expressed via Walras' law (∑ excess-demand·price ≡ 0) so it remains available in the stationarity, replacing the naive row-drop; include the numéraire/price-ray pin (Unknown 3.1).
2. **Specify the S1∧S2∧S3 degeneracy detector** — define the three conjunctive conditions (the market-clearing redundancy signature) that flag camcge + the pass-through default for every other model (Unknown 3.2).
3. **Design the false-positive guard** — the per-model check that irscge/lrgcge/moncge/stdcge are NOT flagged (the detector's precision test, Unknown 3.2).
4. **Specify the prototype-on-`/tmp`-first plan** — reach MS 1 at omega 191.735 with the dual-consistent redefinition in a hand-edited `/tmp` MCP *before* the `src/` change (the Day-11-style control experiment, Unknown 3.1); verify the Walras identity holds across camcge's full market structure so the dropped dual is exactly recoverable (Unknown 3.4).
5. **Define the per-model-numéraire-declaration fallback** — if the automatic redundant-row + numéraire selection proves non-robust, the documented fallback + its Epic-5 scoping (Unknown 3.3).

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_31/CAMCGE_DUAL_CONSISTENT_DESIGN.md` (or an extension of `EPIC_5/CAMCGE_WALRAS_TRANSFORM_DESIGN.md`) — the dual-consistent multiplier redefinition, the S1∧S2∧S3 detector + false-positive guard, the prototype-on-`/tmp`-first plan + the Walras-identity verification, and the per-model-numéraire fallback
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.2, 3.3, 3.4
- CHANGELOG.md updated with the Task 5 completion entry

**Known Unknowns Updates:** For Unknowns 3.1–3.4 in `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md`, set each "Verification Results": Status (✅ VERIFIED / ❌ WRONG + correction), Verified by Task 5, Date, Findings (the dual-consistent redefinition reaching MS 1 / omega 191.735 on `/tmp` [3.1], the detector camcge-only precision [3.2], the redundant-row + numéraire selection rule [3.3], the Walras identity holding at the optimum [3.4]), Evidence (the `/tmp` prototype + the cohort predicate + the `kkt_residual.py` runs), Decision (PROCEED the dual-consistent transform / per-model-numéraire fallback).

**PREP_PLAN.md Updates:** In §Task 5: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 31 Prep`, prepend:
```markdown
- **Prep Task 5 COMPLETE (YYYY-MM-DD):** camcge dual-consistent Walras transform design + degeneracy-detector scope (`CAMCGE_DUAL_CONSISTENT_DESIGN.md`). Designs the dual-consistent multiplier redefinition (express the dropped market's dual via Walras' law so it stays in the stationarity) replacing the naive dual-breaking drop-row; the S1∧S2∧S3 degeneracy detector + the irscge/lrgcge/moncge/stdcge false-positive guard; the prototype-on-`/tmp`-first plan to MS 1 at omega 191.735 + the Walras-identity verification; the per-model-numéraire fallback. Checks the dual side (the Sprint-30 lesson). Verified Unknowns 3.1, 3.2, 3.3, 3.4. Docs/design-only (no `src/`; prototype on `/tmp`, reverted).
```

**Quality Gate:**
```bash
make typecheck && make format && make lint && make test
```
Docs/design-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 31 Prep Task 5: camcge Dual-Consistent Walras Transform Design

CAMCGE_DUAL_CONSISTENT_DESIGN.md — the dual-consistent multiplier redefinition
(express the dropped market's dual via Walras' law so it stays in the stationarity)
replacing the naive dual-breaking drop-row; the S1^S2^S3 degeneracy detector + the
irscge/lrgcge/moncge/stdcge false-positive guard; the prototype-on-/tmp-first plan to
MS 1 at omega 191.735 + the Walras-identity verification; the per-model-numeraire
fallback. Checks the dual side (the Sprint-30 lesson).

## Deliverables
- docs/planning/EPIC_4/SPRINT_31/CAMCGE_DUAL_CONSISTENT_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 3.1, 3.2, 3.3, 3.4 verified
- PREP_PLAN.md: Task 5 -> COMPLETE
- CHANGELOG.md: Task 5 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint31-task5
gh pr create --title "Complete Sprint 31 Prep Task 5: camcge Dual-Consistent Walras Transform Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs/design-only)
- [x] The dual-consistent multiplier redefinition (Walras' law) replaces the naive dual-breaking drop-row
- [x] The S1∧S2∧S3 detector + the irscge/lrgcge/moncge/stdcge false-positive guard specified
- [x] The prototype-on-/tmp-first plan (MS 1 at omega 191.735) + the Walras-identity verification required
- [x] Unknowns 3.1, 3.2, 3.3, 3.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 5 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 6 Prompt: Refresh + Author Phase 0 Acceptance Gates for the Sprint-31 Tracks (PR20 + PR24 + PR27)

**Branch:** Create a new branch named `planning/sprint31-task6` from `main`

**Priority:** Critical (4–6 hours) — **requires Tasks 3 + 4 + 5 done (consumes the three design docs)**

**Objective:** Refresh the existing Phase-0 acceptance gates for the Sprint-31 dispositions and author the new ones, so every emit-touching priority (P1–P6) has a written PROCEED/REPLAN gate before implementation. The gate is the primary scope-correctness control (PR20) plus the PR24 control-experiment-before-implement rule and the PR27 residual-clean-before-forcing rule.

**Unknowns Verified:** 1.2, 2.2, 3.1, 4.1, 5.1, 6.2

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_31/PREP_PLAN.md` §Task 6
- `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md` (Unknowns 1.2, 2.2, 3.1, 4.1, 5.1, 6.2 — the gate-bearing unknowns)
- The Task 3/4/5 design docs (`HEAD_OFFSET_IR_PLUMBING_DESIGN.md`, `OFFSET_ALIAS_JACOBIAN_DESIGN.md`, `CAMCGE_DUAL_CONSISTENT_DESIGN.md`) **← requires Tasks 3, 4, 5**
- `CONTRIBUTING.md` §"Phase 0 Acceptance Gate" (the PR20 template + the PR24/PR25 amendments) + the Sprint-30 gate document as the structural template
- The src-touching ISSUE docs (for the per-issue Phase-0 sections): `docs/issues/ISSUE_{1443,1143,1330,1385,1236}_*.md` + GitHub #1462
- `scripts/diagnostics/kkt_residual.py` (the PROCEED/REPLAN verdict engine for P1/P3/P5/P6)

**Tasks to Complete:**

1. **P1 gate (head-offset IR plumbing)** — PROCEED requires the round-trip unit reproduction (Task 3) green before the emit change; then the cold-INFES-by-direction histogram → residual 0 warm, cold MS 1. REPLAN exit: a 4th head-offset site (Unknown 1.2).
2. **P2 gate (offset-alias core)** — PROCEED requires the 4-term recipe re-confirmed (Task 4) + #1110 orthogonality; completion = `shape8` enabled with no CGE multi-pattern regression. REPLAN exit: the gate can't be made tight → #1111/#1112 filing (Unknown 2.2).
3. **P3 gate (camcge dual-consistent)** — PR24 control: the dual-consistent redefinition must reach MS 1 at omega 191.735 on `/tmp` *before* the src change; the detector flags only camcge. REPLAN exit: per-model-numéraire fallback (Unknown 3.1).
4. **P4 gate (sarf symbolic emit)** — the emit must be **O(constraints), not O(instances)** — `sarf_mcp.gms` timed against the translate budget; the re-emitted `stat_task` verified against the banked hand-derivation; regenerated golden byte-stable. REPLAN exit: timeout re-trigger (Unknown 4.1).
5. **P5 gate (cold-convex obj-grad)** — PR24/PR27 control: the ν_objective reduction must reach the NLP optimum on hhfair *before* the objective-gradient src change (the sign flip is BANNED — refuted three times). REPLAN exit: genuine Case-c → documented non-convexity (Unknown 5.1).
6. **P6 gate (rocket forcing)** — PR27: re-confirm the emit residual is clean at the NLP point (Case-c) *before* any forcing attempt; the deliverable is a match OR the finalized PATH-consultation input (Unknown 6.2).
7. **Author the per-issue Phase-0 sections** — add/refresh the `## Phase 0: Acceptance Gate` section in each src-touching ISSUE doc (#1443, #1143, #1330, #1385, hhfair/CGE, #1462).

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_31/PHASE_0_ACCEPTANCE_GATES.md` — the per-track (P1–P6) PROCEED/REPLAN gate criteria consolidated from Tasks 3/4/5/9
- Refreshed `## Phase 0: Acceptance Gate` sections in the src-touching ISSUE docs (#1443, #1143, #1330, #1385, hhfair/CGE obj-grad, #1462)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.2, 2.2, 3.1, 4.1, 5.1, 6.2
- CHANGELOG.md updated with the Task 6 completion entry

**Known Unknowns Updates:** For Unknowns 1.2, 2.2, 3.1, 4.1, 5.1, 6.2 in `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md`, add the gate-layer verification note to each "Verification Results" (the Task 3/4/5 design verdict is the primary; Task 6 records the PROCEED/REPLAN gate framing + the control-before-implement rule + the `kkt_residual.py` citation).

**PREP_PLAN.md Updates:** In §Task 6: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 31 Prep`, prepend:
```markdown
- **Prep Task 6 COMPLETE (YYYY-MM-DD):** refreshed + authored the Phase-0 acceptance gates for the six src-touching Sprint-31 priorities (`PHASE_0_ACCEPTANCE_GATES.md` + per-issue `## Phase 0` sections in ISSUE_{1443,1143,1330,1385,1236} + #1462). Each gate frames its fix-surface as a Day-0 hypothesis (PR24) + cites `kkt_residual.py` (PR27): P1 requires the IR round-trip reproduction green before the emit change (REPLAN on a 4th site); P2 the 4-term recipe + #1110 orthogonality (`shape8` = completion gate); P3 the dual-consistent prototype to MS 1 / omega 191.735 on `/tmp` before src (per-model-numéraire fallback); P4 the O(constraints) emit timed against the translate budget; P5 the ν_objective control experiment before src (the sign flip BANNED — refuted 3×); P6 the residual-clean-before-forcing rule. Verified Unknowns 1.2, 2.2, 3.1, 4.1, 5.1, 6.2. Docs-only (ISSUE-doc gate sections; no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make format && make lint && make test
```
Docs-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 31 Prep Task 6: Refresh + Author Phase 0 Acceptance Gates

PHASE_0_ACCEPTANCE_GATES.md + per-issue Phase-0 sections (ISSUE_1443/1143/1330/1385/1236
+ #1462). Each gate frames its fix-surface as a Day-0 hypothesis (PR24) + cites
kkt_residual.py (PR27): P1 IR round-trip before emit (REPLAN on a 4th site); P2 4-term
recipe + #1110 orthogonality (shape8 = completion gate); P3 dual-consistent prototype to
MS 1 / omega 191.735 on /tmp before src; P4 O(constraints) emit vs the translate budget;
P5 the nu_objective control experiment before src (sign flip BANNED); P6 residual-clean
before forcing.

## Deliverables
- docs/planning/EPIC_4/SPRINT_31/PHASE_0_ACCEPTANCE_GATES.md
- docs/issues/ISSUE_{1443,1143,1330,1385,1236}_*.md: Phase 0 sections
- KNOWN_UNKNOWNS.md: Unknowns 1.2, 2.2, 3.1, 4.1, 5.1, 6.2 gate-layer notes
- PREP_PLAN.md: Task 6 -> COMPLETE
- CHANGELOG.md: Task 6 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint31-task6
gh pr create --title "Complete Sprint 31 Prep Task 6: Refresh + Author Phase 0 Acceptance Gates" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs-only)
- [x] PHASE_0_ACCEPTANCE_GATES.md has a PROCEED/REPLAN gate for each of P1–P6
- [x] P3 requires the dual-consistent prototype to MS 1 at omega 191.735 on /tmp before src; P5 bans the sign flip + requires the ν_objective control experiment
- [x] Each src-touching ISSUE doc has a refreshed `## Phase 0: Acceptance Gate` section
- [x] Unknowns 1.2, 2.2, 3.1, 4.1, 5.1, 6.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 6 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 7 Prompt: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (PR16)

**Branch:** Create a new branch named `planning/sprint31-task7` from `main`

**Priority:** High (3–5 hours) — **requires Tasks 3 + 4 + 5 + 6 done (consumes the designs + the gates)**

**Objective:** Apply the PR16 hypothesis-validation discipline to the four deepest REPLAN-prone Sprint-31 tracks — P1 (foundational IR plumbing / 4th-site risk), P2 (#1111/#1112 general-alias core), P4 (symbolic-emit timeout re-trigger), and P5 (genuine Case-c obj-grad) — pinning each track's single-model / control-experiment validation, its explicit Sprint-32 REPLAN exit, and the budget reallocation if it stalls.

**Unknowns Verified:** 1.1, 1.2, 2.2, 2.3, 4.2, 5.1, 5.2

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_31/PREP_PLAN.md` §Task 7
- `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md` (Unknowns 1.1, 1.2, 2.2, 2.3, 4.2, 5.1, 5.2 — the deep-track unknowns)
- The Task 3/4/5 design docs + the Task 6 gates (`PHASE_0_ACCEPTANCE_GATES.md`) **← requires Tasks 3, 4, 5, 6** (this task consumes their REPLAN exits)
- `docs/planning/EPIC_4/SPRINT_30/SPRINT_RETROSPECTIVE.md` §1 + §3 (the accurate REPLAN prediction + the "genuine floor is conditional" lesson) + the Sprint-30 REPLAN-risk-assessment doc as the structural template
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 31" §"Risk Level: HIGH" (the per-priority REPLAN exits it names)

**Tasks to Complete:**

1. **P1 (head-offset IR plumbing)** — validation = the round-trip reproduction green by Day-1 + no 4th emit site by the Day-5 checkpoint. REPLAN exit: a 4th site → the deeper-architecture Sprint-32 filing; reallocate P1's remaining days to P5/P7 (Unknowns 1.1, 1.2).
2. **P2 (#1111/#1112 general-alias core)** — validation = the second-index cross-term gates tightly (no CGE multi-pattern regression) by the Day-5 checkpoint. REPLAN exit: the gate leaks → the #1111/#1112 AD-engine filing; polygon's genuine-floor +1 becomes conditional (Unknowns 2.2, 2.3).
3. **P4 (sarf symbolic emit)** — validation = the O(constraints) emit stays inside the translate budget on `sarf_mcp.gms`. REPLAN exit: timeout re-trigger → re-scope the parametric emit (Unknown 4.2).
4. **P5 (cold-convex obj-grad)** — validation = the ν_objective control experiment reaches the NLP optimum on hhfair. REPLAN exit: genuine Case-c → documented non-convexity for the family (Unknowns 5.1, 5.2).
5. **Set the honest KPI projection** — state which of Solve ≥109 (needs mine [P1] + camcge [P3]) and genuine floor ≥73 (needs polygon [P2] + hhfair/CGE [P5]) survives each single-track REPLAN, and the budget-reallocation order.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_31/REPLAN_RISK_ASSESSMENT.md` — per-track (P1/P2/P4/P5) single-model validation + Sprint-32 REPLAN exit + budget reallocation, plus the honest Solve ≥109 / genuine floor ≥73 KPI projection under each single-track REPLAN
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 2.2, 2.3, 4.2, 5.1, 5.2
- CHANGELOG.md updated with the Task 7 completion entry

**Known Unknowns Updates:** For Unknowns 1.1, 1.2, 2.2, 2.3, 4.2, 5.1, 5.2 in `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md`, add the risk/decision-layer note to each "Verification Results" (the Task 3/4/5/9 design verdict is primary; Task 7 records the PROCEED/REPLAN signal + the Sprint-32 exit + the budget reallocation).

**PREP_PLAN.md Updates:** In §Task 7: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 31 Prep`, prepend:
```markdown
- **Prep Task 7 COMPLETE (YYYY-MM-DD):** REPLAN-prone track risk assessment (`REPLAN_RISK_ASSESSMENT.md`). Per-track PROCEED/REPLAN signals + Sprint-32 exits + budget reallocation for the four deepest tracks — P1 mine head-offset IR plumbing (REPLAN on a 4th site → Sprint-32 architecture, reallocate to P5/P7), P2 #1111/#1112 general-alias core (REPLAN if the gate leaks → AD-engine filing), P4 sarf symbolic emit (REPLAN on a timeout re-trigger), P5 cold-convex obj-grad (REPLAN if genuine Case-c). **Solve ≥109 (needs mine + camcge) is the most REPLAN-sensitive KPI; the genuine-floor ramp ≥73 is conditional on the #1111/#1112 core [P2] + the dual-consistent CGE [P3] + the obj-grad reduction [P5], not independent +1s** (the Sprint-30 lesson). Verified Unknowns 1.1, 1.2, 2.2, 2.3, 4.2, 5.1, 5.2. Docs/analysis-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make format && make lint && make test
```
Docs/analysis-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 31 Prep Task 7: REPLAN-Prone Track Risk Assessment

REPLAN_RISK_ASSESSMENT.md — per-track PROCEED/REPLAN signals + Sprint-32 exits +
budget reallocation for the four deepest tracks (P1 head-offset IR plumbing, P2
#1111/#1112 general-alias core, P4 sarf symbolic emit, P5 cold-convex obj-grad).
Solve >=109 (mine + camcge) is the most REPLAN-sensitive KPI; the genuine-floor ramp
>=73 is conditional on P2 + P3 + P5, not independent +1s (the Sprint-30 lesson).

## Deliverables
- docs/planning/EPIC_4/SPRINT_31/REPLAN_RISK_ASSESSMENT.md
- KNOWN_UNKNOWNS.md: Unknowns 1.1, 1.2, 2.2, 2.3, 4.2, 5.1, 5.2 risk-layer notes
- PREP_PLAN.md: Task 7 -> COMPLETE
- CHANGELOG.md: Task 7 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint31-task7
gh pr create --title "Complete Sprint 31 Prep Task 7: REPLAN-Prone Track Risk Assessment" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs/analysis-only)
- [x] Each of P1/P2/P4/P5 has a single-model/control-experiment validation + a Sprint-32 REPLAN exit + a budget-reallocation target
- [x] The honest KPI projection ties Solve ≥109 to (mine + camcge) and genuine floor ≥73 to (polygon + hhfair/CGE)
- [x] Unknowns 1.1, 1.2, 2.2, 2.3, 4.2, 5.1, 5.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 7 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 8 Prompt: Reusable-Tooling Readiness Audit for the Sprint-31 Model Classes

**Branch:** Create a new branch named `planning/sprint31-task8` from `main`

**Priority:** Medium (3–4 hours)

**Objective:** Confirm the Sprint-28–30 diagnostic and regression tooling covers the new Sprint-31 model classes — the head-offset IR-round-trip test, the `--force` scaffold's forcing-lever entry point, the head-offset + `shape8` property fixtures, and the dual-consistent-Walras / symbolic-emit regression paths — and identify any minimal extension needed before implementation. **Audit-only — read-only tool runs, no `src/`.**

**Unknowns Verified:** 4.2, 6.1, 7.1, 7.3

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_31/PREP_PLAN.md` §Task 8
- `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md` §Category 7 (Unknowns 7.1 property fixtures, 7.3 checkpoint coverage) + Unknowns 4.2 (sarf emit budget), 6.1 (`--force` scaffold entry)
- The reused tools (read-only): `scripts/diagnostics/kkt_residual.py`, `scripts/diagnostics/check_presolve_divergence.py`, `scripts/sprint_audit/check_golden_staleness.py` + `changed_emit_artifacts.py` + the `--resolve-changed` mode of `scripts/gamslib/run_full_test.py`
- The `--force` scaffold: `src/emit/forcing.py` + `src/config.py` + `src/cli.py` (landed Sprint 30 — the P6 entry point)
- `tests/integration/emit/test_ad_crossterm_shapes.py` + `tests/fixtures/crossterm_shapes/` (the property catalog — `shape8` strict-xfail, `shape9` robert; the head-offset fixture is new) + the Task-3 round-trip fixture spec

**Tasks to Complete:**

1. **KKT-residual harness coverage** — confirm it produces a Case-(a/b/c) verdict for the head-offset cross-term shape (P1), the dual-consistent Walras prototype (P3), and the obj-grad reduction (P5); note any shape it can't score.
2. **`--force` scaffold entry point** — confirm the scaffold can take the rocket continuation/reformulation levers (P6) and that its harness output feeds the PATH-consultation input (Unknown 6.1).
3. **Property-fixture readiness** — confirm `shape8_offset_alias_successor` is the P2 completion gate and scope the new head-offset fixture (from Task 3's round-trip spec) for P7 (Unknown 7.1).
4. **Golden-staleness + `--resolve-changed` coverage** — confirm the gate + the checkpoint re-solve cover the newly-touched emit sites (the head-offset core, `_add_indexed_jacobian_terms`, the Walras redefinition, the sarf symbolic emit) (Unknowns 7.3, 4.2 — the sarf emit budget timing).
5. **Identify minimal extensions** — list any tool gap that must close before the relevant priority starts (feeds Task 9 + P7).

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_31/TOOLING_READINESS_AUDIT.md` — per-tool coverage confirmation for the Sprint-31 classes + a minimal-extension list (feeds Task 9 + P7)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.2, 6.1, 7.1, 7.3
- CHANGELOG.md updated with the Task 8 completion entry

**Known Unknowns Updates:** For Unknowns 4.2, 6.1, 7.1, 7.3 in `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md`, set each "Verification Results": Status (✅ VERIFIED / ❌ WRONG), Verified by Task 8, Date, Findings (the actual read-only tool-run results — the sarf emit-budget timing [4.2], the `--force` rocket-lever entry [6.1], the `shape8` + head-offset fixture readiness [7.1], the `--resolve-changed` checkpoint coverage [7.3]), Evidence (the tool-run output), Decision (any minimal extension + the priority it blocks).

**PREP_PLAN.md Updates:** In §Task 8: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 31 Prep`, prepend:
```markdown
- **Prep Task 8 COMPLETE (YYYY-MM-DD):** reusable-tooling readiness audit (`TOOLING_READINESS_AUDIT.md`, from actual read-only tool runs). Confirms the KKT-residual harness scores the head-offset / dual-consistent-Walras / obj-grad shapes; the `--force` scaffold takes the rocket continuation/reformulation levers + feeds the PATH-consultation input; `shape8_offset_alias_successor` is the P2 completion gate + the new head-offset fixture (from Task 3) is a clean one-file add for P7; the golden-staleness gate + `--resolve-changed` cover the newly-touched emit sites (head-offset core, `_add_indexed_jacobian_terms`, Walras redefinition, sarf symbolic emit); sarf's O(constraints) emit-budget timing checked. Minimal-extension list scoped. Verified Unknowns 4.2, 6.1, 7.1, 7.3. Audit-only (read-only tool runs; no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make format && make lint && make test
```
Audit-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 31 Prep Task 8: Reusable-Tooling Readiness Audit

TOOLING_READINESS_AUDIT.md (from actual read-only tool runs) — confirms the
KKT-residual harness scores the head-offset / dual-consistent-Walras / obj-grad shapes;
the --force scaffold takes the rocket levers + feeds the PATH-consultation input; shape8
is the P2 completion gate + the head-offset fixture is a clean P7 add; the golden-staleness
gate + --resolve-changed cover the newly-touched emit sites; sarf's O(constraints)
emit-budget timing checked. Minimal-extension list scoped.

## Deliverables
- docs/planning/EPIC_4/SPRINT_31/TOOLING_READINESS_AUDIT.md
- KNOWN_UNKNOWNS.md: Unknowns 4.2, 6.1, 7.1, 7.3 verified
- PREP_PLAN.md: Task 8 -> COMPLETE
- CHANGELOG.md: Task 8 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint31-task8
gh pr create --title "Complete Sprint 31 Prep Task 8: Reusable-Tooling Readiness Audit" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (audit-only)
- [x] The KKT-residual harness, presolve-divergence detector, golden-staleness gate, `--resolve-changed`, and `--force` scaffold confirmed for their Sprint-31 touchpoints
- [x] The `shape8` P2 gate + the new head-offset P7 fixture scoped
- [x] Any minimal tooling extension listed with the priority it blocks
- [x] Unknowns 4.2, 6.1, 7.1, 7.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 8 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 9 Prompt: Backlog Fix-Surface Analysis (#1385 sarf; hhfair/CGE obj-grad; rocket forcing/PATH input)

**Branch:** Create a new branch named `planning/sprint31-task9` from `main`

**Priority:** Medium (3–4 hours) — **requires Task 8 done (reuses the tooling audit)**

**Objective:** Turn the three implementation-lighter carryforwards into concrete fix-surface hypotheses with property-test fixtures: the #1385 sarf symbolic-emit patch site (P4), the cold-convex obj-grad reduction site (P5), and the rocket forcing-lever exhaustion + PATH-consultation-input draft (P6) — each a Day-0-re-confirm hypothesis (PR24), not a fact. **Analysis-only — Day-0 harness reads + doc, no `src/`.**

**Unknowns Verified:** 4.1, 4.3, 5.1, 5.2, 5.3, 5.4, 6.1, 6.3

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_31/PREP_PLAN.md` §Task 9
- `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md` §Category 4 (4.1 sarf gate, 4.3 atomicity), §Category 5 (5.1 ν_objective control, 5.2 CGE generalization, 5.3 rule-vs-patch, 5.4 case-normalization composition), §Category 6 (6.1 lever exhaustion, 6.3 Jacobian reformulation)
- `docs/issues/ISSUE_1385_*.md` (the banked 6-guarded-term `stat_task` derivation; the Sprint-26 `nu_slack("srn")` failure; sarf's 2-D `tbal(g,t)$taskposs` shape + 1,152 Cartesian instances) + the sarf emit sites (read-only): `src/ad/index_mapping.py` (`_is_blowup_dynamic_subset_equation`), `src/kkt/stationarity.py`
- The obj-grad reduction (read-only): hhfair `stat_u` rel 2.0; irscge/lrgcge/moncge `stat_xp` rel ~0.06 (after the Day-5 case-normalization fix); ν_objective in `src/kkt/stationarity.py` / `src/ad/gradient.py` + `docs/issues/ISSUE_1236_*.md`
- `docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md` §4 (the PATH-consultation-input draft scope; rocket's `1/ht²`,`1/m²` division-by-variable Jacobian + INFES 477→382) + the `--force` scaffold
- The Task-8 `TOOLING_READINESS_AUDIT.md` **← requires Task 8**
- `tests/integration/emit/test_ad_crossterm_shapes.py` (the fixture home for the sarf-shape + obj-grad-reduction guards) + `scripts/diagnostics/kkt_residual.py`

**Tasks to Complete:**

1. **P4 sarf fix-surface** — re-confirm the 2-D `_is_blowup_dynamic_subset_equation` extension surface + the parametric `stat_task` builder site on the current tree; spec the O(constraints) property fixture (a sarf-shaped synthetic guarding the 6-guarded-term derivation with no set-name multiplier indices) (Unknowns 4.1, 4.3).
2. **P5 obj-grad fix-surface** — re-confirm the ν_objective reduction site in the objective-gradient path (NOT the sign flip); spec the control experiment (hhfair → NLP optimum) + a property fixture for the objective-defining-intermediate-variable shape; check the CGE-cluster generalization + the rule-vs-patch + the case-normalization composition (Unknowns 5.1, 5.2, 5.3, 5.4).
3. **P6 rocket lever set + PATH input** — enumerate the remaining emittable levers (the `1/ht²`/`1/m²` Jacobian reformulation + scaled/relaxed continuation) and draft the concrete PATH-consultation question scope (feeds Sprint 32) (Unknowns 6.1, 6.3).
4. **Assemble the fix-surface + fixture summary** — each patch site as a re-confirmable hypothesis + its guarding fixture.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_31/BACKLOG_FIX_SURFACE_ANALYSIS.md` — the P4 sarf symbolic-emit patch site + fixture spec, the P5 ν_objective obj-grad reduction site + control-experiment + fixture spec, and the P6 emittable-lever set + PATH-consultation-input draft
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.3, 5.1, 5.2, 5.3, 5.4, 6.1, 6.3
- CHANGELOG.md updated with the Task 9 completion entry

**Known Unknowns Updates:** For Unknowns 4.1, 4.3, 5.1, 5.2, 5.3, 5.4, 6.1, 6.3 in `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md`, set each "Verification Results": Status (✅ VERIFIED / ❌ WRONG + correction), Verified by Task 9, Date, Findings (the fresh Day-0 harness reads — the sarf 2-D gate + parametric `stat_task` site + atomicity [4.1, 4.3], the ν_objective reduction control result + CGE generalization + rule-vs-patch + case-normalization [5.1, 5.2, 5.3, 5.4], the rocket lever exhaustion + Jacobian reformulation [6.1, 6.3]), Evidence (Day-0 harness reads), Decision (the patch site + the guarding fixture). **Note:** 5.1 is a shared Critical — Task 9 runs the control experiment, Task 6 gates it, Task 7 makes the Case-b/Case-c call.

**PREP_PLAN.md Updates:** In §Task 9: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 31 Prep`, prepend:
```markdown
- **Prep Task 9 COMPLETE (YYYY-MM-DD):** backlog fix-surface analysis (`BACKLOG_FIX_SURFACE_ANALYSIS.md`, Day-0 harness reads, PR24 hypotheses). **#1385 sarf:** the 2-D `_is_blowup_dynamic_subset_equation` extension + the parametric `stat_task` builder site (symbolic `(g,t,m,n)` indices, no set-name literals — the Sprint-26 failure mode) + the O(constraints) property fixture. **Cold-convex obj-grad:** the ν_objective reduction site (NOT the refuted sign flip) + the hhfair control experiment + the CGE-cluster generalization + the rule-vs-patch + the case-normalization composition + the property fixture. **rocket:** the remaining emittable-lever set (`1/ht²`/`1/m²` Jacobian reformulation + continuation) + the drafted PATH-consultation question scope. Verified Unknowns 4.1, 4.3, 5.1, 5.2, 5.3, 5.4, 6.1, 6.3. Analysis-only (Day-0 harness reads + doc; no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make format && make lint && make test
```
Analysis-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 31 Prep Task 9: Backlog Fix-Surface Analysis

BACKLOG_FIX_SURFACE_ANALYSIS.md (Day-0 harness reads, PR24 hypotheses). #1385 sarf:
the 2-D _is_blowup_dynamic_subset_equation extension + the parametric stat_task builder
(symbolic (g,t,m,n) indices, no set-name literals) + the O(constraints) fixture.
Cold-convex obj-grad: the nu_objective reduction site (NOT the refuted sign flip) + the
hhfair control experiment + the CGE-cluster generalization + fixture. rocket: the
remaining emittable-lever set + the drafted PATH-consultation question scope.

## Deliverables
- docs/planning/EPIC_4/SPRINT_31/BACKLOG_FIX_SURFACE_ANALYSIS.md
- KNOWN_UNKNOWNS.md: Unknowns 4.1, 4.3, 5.1, 5.2, 5.3, 5.4, 6.1, 6.3 verified
- PREP_PLAN.md: Task 9 -> COMPLETE
- CHANGELOG.md: Task 9 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint31-task9
gh pr create --title "Complete Sprint 31 Prep Task 9: Backlog Fix-Surface Analysis" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (analysis-only)
- [x] The sarf 2-D gate + parametric `stat_task` builder site re-confirmed with an O(constraints) fixture spec
- [x] The obj-grad fix-surface is the ν_objective reduction (the sign flip explicitly excluded) with a control-experiment + fixture spec
- [x] The rocket emittable-lever set + the drafted PATH-consultation question scope recorded
- [x] Unknowns 4.1, 4.3, 5.1, 5.2, 5.3, 5.4, 6.1, 6.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 9 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 10 Prompt: Plan Sprint 31 Detailed Schedule

**Branch:** Create a new branch named `planning/sprint31-task10` from `main`

**Priority:** Critical (3–4 hours) — **the terminal task; requires Tasks 1–9 done**

**Objective:** Produce the detailed 14-day Sprint 31 schedule (Day 0 setup + Days 1–13 execution) with day-by-day execution prompts, sequencing the seven priorities so the deepest track (P1 head-offset IR plumbing) and its foundational IR change lead, the checkpoints (Day 5 / Day 10) land the `--resolve-changed` re-solve, and no day exceeds 12 hours per the PROJECT_PLAN Sprint 31 entry.

**Unknowns Verified:** (integrates all 25 — no new verification; consumes the resolved unknowns)

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_31/PREP_PLAN.md` §Task 10 + all Task 2–9 prep outputs (the schedule consumes them) **← requires Tasks 1–9**
- `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md` (all 25 unknowns should now be ✅ VERIFIED / ❌ WRONG)
- `docs/planning/EPIC_4/SPRINT_30/PLAN.md` + `docs/planning/EPIC_4/SPRINT_30/prompts/PLAN_PROMPTS.md` (the day-by-day schedule + prompt template)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 31" (the 7 priorities + the per-priority Estimated-Effort budgets + the ≤12h/day budget + the ~11h heaviest-day note — the P1 IR-plumbing Phase 1 + Phase 2)
- `docs/planning/EPIC_4/SPRINT_29/PRIORITY_8_CHECKPOINT_RESOLVE_DESIGN.md` (the `--resolve-changed` checkpoint design)

**Tasks to Complete:**

1. **Sequence the priorities across Days 1–13** — P1 head-offset (early, contiguous: Phase-1 IR plumbing then Phase-2 helper); P2 offset-alias core; P3 camcge dual-consistent; P4 sarf symbolic emit; P5 cold-convex obj-grad; P6 rocket forcing/PATH input; P7 property fixtures + genuine-floor tracking (after P1/P2 land); respect ≤ 12h/day.
2. **Place Day 0 tractability probes** — the P1 round-trip reproduction, the P3 dual-consistent `/tmp` prototype, and the P5 hhfair ν_objective control experiment, so the deepest tracks are validated before the mid-sprint budget commits.
3. **Place the checkpoints** — Day 5 + Day 10 `--resolve-changed` re-solve + the REPLAN-reallocation decision points from Task 7; the final Day-13 retest under ≥ 3 `PYTHONHASHSEED` values + the PR25 genuine-floor recompute.
4. **Write the day-by-day execution prompts** (`prompts/PLAN_PROMPTS.md`) — one per day, each self-contained with objectives / branch / Phase-0 gate / deliverable / REPLAN exit / quality gate / PR + wait-for-review.
5. **Verify the budget** — ≤ 12h/day, total within the 92–134h work-item envelope; the ~11h heaviest day is the P1 Phase-1+Phase-2 day. Author the `SPRINT_LOG.md` skeleton.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_31/PLAN.md` — the 14-day schedule (Day 0 + Days 1–13) with per-day priority / Phase-0 gate / deliverable / REPLAN exit, the Day-0 tractability probes, the Day-5 / Day-10 checkpoints + the final determinism retest, and the ≤ 12h/day budget verification
- `docs/planning/EPIC_4/SPRINT_31/prompts/PLAN_PROMPTS.md` — the day-by-day execution prompts
- `docs/planning/EPIC_4/SPRINT_31/SPRINT_LOG.md` (skeleton for the sprint)
- CHANGELOG.md updated with the Task 10 completion entry (+ a "Sprint 31 prep phase COMPLETE" note)

**Known Unknowns Updates:** In `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md` §"Next Steps", update the PREP-PHASE note: all 25 unknowns VERIFIED (flag any that INVERTED / returned WRONG and how the schedule absorbs them), and mark "Sprint 31 is GO for Day 0." No new per-unknown verification blocks (Task 10 integrates, it does not verify).

**PREP_PLAN.md Updates:** In §Task 10: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria. Also update the §Summary "Prep Task → Deliverable Map" statuses to ✅ and add a "Prep phase COMPLETE" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 31 Prep`, prepend:
```markdown
- **Prep Task 10 COMPLETE (YYYY-MM-DD):** Sprint 31 14-day schedule (`docs/planning/EPIC_4/SPRINT_31/PLAN.md`, Day 0 + Days 1–13, ≤ 12h/day) + day-by-day execution prompts (`prompts/PLAN_PROMPTS.md`) + the `SPRINT_LOG.md` skeleton. Leads with P1 head-offset (contiguous Phase-1 IR plumbing → Phase-2 helper), front-loads the Day-0 tractability probes (P1 round-trip / P3 dual-consistent `/tmp` prototype / P5 hhfair control experiment), embeds the Day-5/Day-10 `--resolve-changed` checkpoint re-solve + the PR25 re-baseline, places the P1/P2/P4/P5 REPLAN decision points per the Task-7 assessment with reallocation, and closes with the ≥3-seed determinism retest. Budget within 92–134h, no day > 12h. **All 25 prep unknowns integrated; Sprint 31 is GO for Day 0. Sprint 31 prep phase COMPLETE** (Tasks 1–10).
```

**Quality Gate:**
```bash
make typecheck && make format && make lint && make test
```
Docs-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 31 Prep Task 10: Plan Sprint 31 Detailed Schedule

PLAN.md (Day 0 + Days 1-13, <=12h/day) + prompts/PLAN_PROMPTS.md + SPRINT_LOG.md
skeleton. Leads with P1 head-offset (contiguous Phase-1 IR plumbing -> Phase-2 helper),
front-loads the Day-0 tractability probes (P1 round-trip / P3 dual-consistent /tmp
prototype / P5 hhfair control experiment), embeds the Day-5/Day-10 --resolve-changed
checkpoint re-solve + the PR25 re-baseline, places the P1/P2/P4/P5 REPLAN decision points
per the Task-7 assessment with reallocation, closes with the >=3-seed determinism retest.
Budget within 92-134h, no day > 12h. Sprint 31 prep phase COMPLETE (Tasks 1-10);
Sprint 31 is GO for Day 0.

## Deliverables
- docs/planning/EPIC_4/SPRINT_31/PLAN.md
- docs/planning/EPIC_4/SPRINT_31/prompts/PLAN_PROMPTS.md
- docs/planning/EPIC_4/SPRINT_31/SPRINT_LOG.md
- KNOWN_UNKNOWNS.md: Next Steps -> prep phase COMPLETE
- PREP_PLAN.md: Task 10 -> COMPLETE + Summary map
- CHANGELOG.md: Task 10 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint31-task10
gh pr create --title "Complete Sprint 31 Prep Task 10: Plan Sprint 31 Detailed Schedule" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs-only)
- [x] PLAN.md covers Day 0 + Days 1–13; the 7 priorities sequenced with P1 head-offset leading (contiguous Phase-1 → Phase-2)
- [x] Day 0 runs the P1 round-trip / P3 dual-consistent /tmp prototype / P5 hhfair control-experiment tractability probes
- [x] The Day-5/Day-10 `--resolve-changed` checkpoint + PR25 re-baseline + the REPLAN-reallocation decision points + the final ≥3-seed determinism retest placed
- [x] PLAN_PROMPTS.md has one self-contained prompt per day; ≤ 12h/day (no day > 12h; within 92–134h)
- [x] KNOWN_UNKNOWNS.md Next Steps → prep phase COMPLETE; Task 10 Acceptance Criteria all checked
EOF
)"
```

**Then wait for reviewer comments.**

---

## Prep-Task → Branch → PR Summary

| Prep Task | Branch | Unknowns Verified | Depends On |
|-----------|--------|-------------------|------------|
| Task 2: Day-0 Baseline + Genuine-Floor Re-Baseline | `planning/sprint31-task2` | 7.2 | None |
| Task 3: Head-Offset IR-Plumbing Design + Round-Trip Reproduction | `planning/sprint31-task3` | 1.1, 1.2, 1.3, 1.4 | Tasks 1, 2 |
| Task 4: Offset-Alias Recipe Re-Confirmation + Distance-Jacobian Design | `planning/sprint31-task4` | 2.1, 2.2, 2.3, 2.4 | Tasks 1, 2 |
| Task 5: camcge Dual-Consistent Walras Transform Design | `planning/sprint31-task5` | 3.1, 3.2, 3.3, 3.4 | Task 1 |
| Task 6: Refresh + Author Phase 0 Acceptance Gates | `planning/sprint31-task6` | 1.2, 2.2, 3.1, 4.1, 5.1, 6.2 | Tasks 1, 3, 4, 5 |
| Task 7: REPLAN-Prone Track Risk Assessment | `planning/sprint31-task7` | 1.1, 1.2, 2.2, 2.3, 4.2, 5.1, 5.2 | Tasks 3, 4, 5, 6 |
| Task 8: Reusable-Tooling Readiness Audit | `planning/sprint31-task8` | 4.2, 6.1, 7.1, 7.3 | Task 1 |
| Task 9: Backlog Fix-Surface Analysis | `planning/sprint31-task9` | 4.1, 4.3, 5.1, 5.2, 5.3, 5.4, 6.1, 6.3 | Tasks 1, 8 |
| Task 10: Plan Sprint 31 Detailed Schedule | `planning/sprint31-task10` | (integrates all 25) | Tasks 1–9 |

**Critical path:** Task 1 → Task 3 → Task 6 → Task 7 → Task 10.
**Coverage:** every Sprint-31 unknown (1.1–7.3, 25 total) is verified by at least one prep task; Task 10 integrates all into the 14-day schedule.

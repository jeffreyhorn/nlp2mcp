# Sprint 28 Prep Task Execution Prompts

Self-contained prompts for Sprint 28 Prep Tasks 2–10. Each prompt can be copy-pasted into a new conversation to execute one prep task end-to-end, including the Known Unknowns updates, PREP_PLAN.md / CHANGELOG.md updates, quality gate, commit, and PR.

**Usage:**

1. Pick a task prompt below.
2. Paste it into a new conversation.
3. The agent creates the branch, does the work, runs the quality gate, commits, pushes, and opens a PR.
4. Wait for reviewer comments on the PR.

Task 1 (Create Sprint 28 Known Unknowns List) is already ✅ COMPLETE — no prompt needed.

Tasks 2–10 are dispatchable in the following order per the dependency graph in `docs/planning/EPIC_4/SPRINT_28/PREP_PLAN.md` (Task 1 is done, so its dependents are immediately dispatchable):

- **Parallel kickoff (no dependencies beyond the completed Task 1):** Tasks 2, 3, 4, 8, 9
- **After Task 2:** Task 7 (golden-staleness drift audit needs the Day-0 baseline)
- **After Tasks 3 + 4:** Task 5 (Phase 0 gates need the PR24 rule + the harness design they reference)
- **After Task 5:** Task 6 (REPLAN assessment consumes the Phase 0 gates)
- **After all (final integration):** Task 10

**Cross-cutting conventions for every prompt below:**

- Branch from `main`; PR targets `main`.
- User preferences (enforce in every commit/PR): **NO `Co-Authored-By` lines** in commit messages; **NO "Generated with Claude Code"** in PR descriptions.
- Replace `YYYY-MM-DD` with the actual date at execution time.
- These are **docs/design-only** prep tasks — no Python source changes are expected (the scripts they design are *built in-sprint*, not in prep). Run the full quality gate before committing regardless; if you did add Python, it must pass.

---

## Task 2 Prompt: Sprint 27 → Sprint 28 Bucket-Provenance Baseline + Projection Discipline (PR15 + PR17 + PR25)

**Branch:** Create a new branch named `planning/sprint28-task2` from `main`

**Priority:** Critical (4–5 hours)

**Objective:** Establish the Sprint 28 Day-0 baseline metrics with per-failing-model bucket provenance (Sprint 27 final → Sprint 28 Day 0), and produce a **projection table** that labels every projected Solve/Match delta as either a genuine bucket-to-success transition or a forward move within the failure set (PR25). This is the measured starting point against which all Sprint 28 acceptance criteria are evaluated.

**Unknowns Verified:** 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 6.2

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_28/PREP_PLAN.md` §Task 2
- `docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md` §Unknowns 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 6.2 (the "is model X still in bucket Y at Day 0?" research questions)
- `docs/planning/EPIC_4/SPRINT_27/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently #2" (the over-optimistic projection lesson) + header final metrics (Solve 105 / Match 62)
- `docs/planning/EPIC_4/SPRINT_27/SPRINT_LOG.md` Day-10 Checkpoint 2 full bucket membership + final-day entry
- `data/gamslib/gamslib_status.json` (current pipeline DB; `mcp_file_used` paths were relativized in Sprint 27 #1400, but the `message`-field absolute-path leak is still a Sprint 28 carryforward — Priority 7 — so the DB is not yet *fully* machine-portable)
- `scripts/gamslib/run_full_test.py` (pipeline runner; full retest ~4h wall)

**Tasks to Complete:**

1. Run the Day-0 pipeline baseline (or reuse the committed Sprint 27 final DB if `main` is unchanged since the Day-13 retest) and record Parse/Translate/Solve/Match + every failure bucket with per-model membership.
2. Build the bucket-provenance table — for each carryforward target model (mine, camshape, otpop, cclinpts, kand, camcge) record its Sprint 27 Day-0 → Sprint 27 final → Sprint 28 Day-0 bucket and the gating issue.
3. Author the PR25 projection table — for each Sprint 28 priority, state the projected delta and label it **genuine gain** (bucket-to-success) vs **bucket-forward** (within the failure set); tally only genuine gains toward Solve ≥ 110 / Match ≥ 65.
4. Freeze the Sprint 28 scope — write the scope-freeze note: in-target vs Sprint-29-deferred (REPLAN exit) models + the committed Solve/Match regression-guard sets.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_28/BASELINE_METRICS.md` — Day-0 counts + per-failing-model bucket provenance
- PR25 projection table (genuine-gain vs bucket-forward; only genuine gains tallied toward targets)
- Scope-freeze note (in-target vs Sprint-29-deferred + the committed regression-guard sets)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 6.2
- CHANGELOG.md updated with Task 2 completion entry

**Known Unknowns Updates:**

For each of Unknowns 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 6.2 in `docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md`, update the "Verification Results" subsection (only the baseline/bucket-provenance aspect — the fix-surface aspect of 1.1/2.1/3.1/4.1/5.1/6.1 is verified by Tasks 5/6):

- Status: ✅ VERIFIED (or ❌ WRONG with correction + new assumption)
- Verified by: Task 2 (Bucket-Provenance Baseline + Projection Discipline)
- Date: YYYY-MM-DD
- Findings: each target model's Day-0 bucket + the genuine-gain-vs-bucket-forward classification of its projected delta
- Evidence: the DB snapshot + the bucket-provenance table rows
- Decision: which deltas count toward the Solve/Match targets; any scope adjustment

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_28/PREP_PLAN.md` §Task 2:

- Change `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`
- Add `**Completed:** YYYY-MM-DD`
- Fill in the "Changes" section (what was measured + authored)
- Fill in the "Result" section (the genuine-gain tally + scope freeze)
- Check off all "Acceptance Criteria" (`- [ ]` → `- [x]`)

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 28 Preparation`, prepend:

```markdown
- **Prep Task 2 COMPLETE (YYYY-MM-DD):** Sprint 28 Day-0 baseline + bucket-provenance (Sprint 27 final → S28 Day 0): Parse <n> / Translate <n> / Solve <n> / Match <n>; per-failing-model buckets recorded. PR25 projection table labels each priority's delta genuine-gain vs bucket-forward (only genuine gains tallied toward Solve ≥ 110 / Match ≥ 65). Scope freeze: in-target vs Sprint-29-deferred + committed regression-guard sets. Verified Unknowns 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 6.2 (baseline aspect).
```

**Quality Gate:**

```bash
make typecheck && make format && make lint && make test
```

Docs-only task — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**

```
Complete Sprint 28 Prep Task 2: Bucket-Provenance Baseline + Projection Discipline

Day-0 baseline + per-failing-model bucket provenance (S27 final -> S28 Day 0).
PR25 projection table distinguishes genuine bucket-to-success gains from
forward moves within the failure set; only genuine gains count toward targets.
Scope freeze records in-target vs Sprint-29-deferred models + the committed
Solve/Match regression-guard sets.

## Deliverables
- docs/planning/EPIC_4/SPRINT_28/BASELINE_METRICS.md
- KNOWN_UNKNOWNS.md: Unknowns 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 6.2 verified (baseline)
- PREP_PLAN.md: Task 2 -> COMPLETE
- CHANGELOG.md: Task 2 entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint28-task2
gh pr create --title "Complete Sprint 28 Prep Task 2: Bucket-Provenance Baseline + Projection Discipline" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs-only)
- [x] BASELINE_METRICS.md records Day-0 counts + per-failing-model buckets
- [x] PR25 projection table distinguishes genuine gains from bucket-forward moves
- [x] Unknowns 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 6.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 2 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 3 Prompt: Codify Process Recommendations PR24 (Day-0 Traced Fix-Surface) + PR25 (Projection Discipline)

**Branch:** Create a new branch named `planning/sprint28-task3` from `main`

**Priority:** Critical (2–3 hours) — **must land before Task 5 (it changes how the Phase 0 gates establish their fix surface)**

**Objective:** Codify the two new Sprint 27-derived process rules in CONTRIBUTING.md and the Phase-0 acceptance-gate template, before the carryforward Phase 0 gates are authored (Task 5): **PR24 — Day-0 traced fix-surface** (prep records the symptom + reproducer only; the fix surface is established by a Day-0 trace, never trusted from the prep doc; Phase-0 PROCEED must cite the traced surface) and **PR25 — Projection discipline** (Solve/Match projections must label each delta genuine bucket-to-success vs bucket-forward; only the former counts toward targets).

**Unknowns Verified:** 1.1, 2.1, 3.1, 4.1, 5.1 (the fix-surface-as-hypothesis framing)

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_28/PREP_PLAN.md` §Task 3
- `docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md` §Unknowns 1.1, 2.1, 3.1, 4.1, 5.1
- `docs/planning/EPIC_4/SPRINT_27/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently #1 (fix surfaces)" + "#2 (projections)"
- `CONTRIBUTING.md` existing §"Phase 0 Acceptance Gate" + PR20–PR23 sections (PR24/PR25 extend them)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` Sprint 28 §"Process Recommendations from Sprint 27" (PR24/PR25 text)

**Tasks to Complete:**

1. Draft the PR24 rule text for CONTRIBUTING.md — hard rule: "The prep doc records the symptom and a minimal reproducer. The fix surface (`file:line`) is established by a Day-0 trace at sprint start and is never carried as fact from the prep doc. A Phase-0 PROCEED signal must cite the *traced* surface, with the trace command/evidence recorded."
2. Amend the Phase-0 template — add a "Traced Fix-Surface (Day-0)" line to the PROCEED/REPLAN Signal subsection (requires the traced surface + evidence); reword "Expected Emit Pattern" to note the prep surface is a hypothesis.
3. Draft the PR25 rule text — "Every Solve/Match projection labels each delta genuine-gain (bucket-to-success) vs bucket-forward (within the failure set); only genuine gains count toward sprint targets. Day-0 and checkpoint projections must show both tallies."
4. Cross-reference the new infra tooling — the Phase-0 "Verification Methodology" template references the KKT-residual harness (PR27) as the Case-(a/b/c) discriminator and notes emit-touching PRs must pass the golden-staleness check (PR26).
5. Verify the rules are self-consistent with PR20–PR23 (PR24 strengthens PR20, not replaces it).

**Deliverables:**

- CONTRIBUTING.md updated with the PR24 (Day-0 traced fix-surface) hard rule
- CONTRIBUTING.md updated with the PR25 (projection discipline) rule
- Phase-0 template amended: "Traced Fix-Surface (Day-0)" in PROCEED/REPLAN; KKT-residual harness referenced in Verification Methodology (PR27); golden-staleness check referenced (PR26)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 2.1, 3.1, 4.1, 5.1
- CHANGELOG.md updated with Task 3 completion entry

**Known Unknowns Updates:**

For each of Unknowns 1.1, 2.1, 3.1, 4.1, 5.1 in KNOWN_UNKNOWNS.md, update "Verification Results" (the framing aspect — these Critical fix-surface unknowns are now governed by the codified PR24 rule):

- Status: ✅ VERIFIED (or ❌ WRONG with correction)
- Verified by: Task 3 (Codify PR24 + PR25)
- Date: YYYY-MM-DD
- Findings: the codified rule that makes each fix-surface a Day-0-trace hypothesis
- Evidence: the CONTRIBUTING.md PR24/PR25 sections + the amended Phase-0 template
- Decision: Phase-0 PROCEED for these unknowns now requires the traced surface (Task 5 will apply it)

**PREP_PLAN.md Updates:**

In §Task 3: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all "Acceptance Criteria".

**CHANGELOG.md Update:**

```markdown
- **Prep Task 3 COMPLETE (YYYY-MM-DD):** Codified PR24 (Day-0 traced fix-surface — prep records symptom+reproducer; surface established by Day-0 trace, never trusted from the prep doc; PROCEED cites the traced surface) + PR25 (projection discipline — genuine bucket-to-success vs bucket-forward; only genuine gains count toward targets) in CONTRIBUTING.md. Amended the Phase-0 template (Traced Fix-Surface in PROCEED/REPLAN; KKT-residual harness per PR27; golden-staleness check per PR26). Verified Unknowns 1.1, 2.1, 3.1, 4.1, 5.1 (fix-surface-as-hypothesis framing).
```

**Quality Gate:**

```bash
make typecheck && make format && make lint && make test
```

Docs-only — run regardless; do NOT commit until all pass.

**Commit Message Format:**

```
Complete Sprint 28 Prep Task 3: Codify PR24 (Day-0 Traced Fix-Surface) + PR25

PR24 makes every prep-doc fix surface a Day-0-trace hypothesis (Sprint 27
proved them wrong 4x); PR25 forces projections to separate genuine
bucket-to-success gains from bucket-forward moves. Phase-0 template amended to
require the traced surface on PROCEED and to reference the KKT-residual harness
(PR27) + golden-staleness check (PR26).

## Deliverables
- CONTRIBUTING.md: PR24 + PR25 + amended Phase-0 template
- KNOWN_UNKNOWNS.md: Unknowns 1.1, 2.1, 3.1, 4.1, 5.1 verified
- PREP_PLAN.md: Task 3 -> COMPLETE
- CHANGELOG.md: Task 3 entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint28-task3
gh pr create --title "Complete Sprint 28 Prep Task 3: Codify PR24 (Day-0 Traced Fix-Surface) + PR25" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs-only)
- [x] CONTRIBUTING.md contains PR24 + PR25 + amended Phase-0 template (traced surface, PR26/PR27 references)
- [x] No contradiction with existing PR20–PR23 text
- [x] Unknowns 1.1, 2.1, 3.1, 4.1, 5.1 verified in KNOWN_UNKNOWNS.md
- [x] Task 3 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 4 Prompt: Design the KKT-Residual Verification Harness (PR27 / Priority 9)

**Branch:** Create a new branch named `planning/sprint28-task4` from `main`

**Priority:** High (3–4 hours) — front-loaded so the harness is the first thing built in-sprint (Days 1–3)

**Objective:** Produce the design spec for the KKT-residual verification harness (`scripts/diagnostics/kkt_residual.py`) so the Phase-0 "Verification Methodology" sections (Task 5) can reference its exact command interface. The harness formalizes Sprint 27's GDX warm-from-good-optimum experiment: given a model, solve the NLP (or load a provided GDX), warm-start the MCP from that solution + transferred duals, and report per-row stationarity/complementarity residuals + a Case-(a/b/c) verdict.

**Unknowns Verified:** 9.1, 9.2, 9.3, 1.3, 2.2, 5.1, 5.2

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_28/PREP_PLAN.md` §Task 4
- `docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md` §Unknowns 9.1, 9.2, 9.3, 1.3, 2.2, 5.1, 5.2
- `docs/planning/EPIC_4/SPRINT_27/SPRINT_LOG.md` Days 9/11 (the GDX warm-from-good-optimum experiments: launch double-apply; camshape §4.6 discriminator) — note the Day-9 dual-transfer workaround used parameters `pwl_m`/`pwu_m` for inequality multipliers → `comp_*`
- `src/emit/emit_gams.py` + `src/kkt/` (the multiplier↔equation correspondence the harness reuses)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` Sprint 28 Priority 9 + PR27

**Tasks to Complete:**

1. Specify the CLI interface — `kkt_residual.py <model.gms> [--gdx <solution.gdx>] [--tol 1e-6]`: no GDX ⇒ solve the NLP first; emit the MCP; warm-start from the NLP primal + transferred duals; run `iterlim=0` / residual-only; report per-row residuals.
2. Specify the dual-transfer mechanism — map each NLP constraint marginal to its MCP multiplier (nu_*/lam_*/piL_*/piU_*), including the inequality→`comp_*` case (generalize the `pwl_m`/`pwu_m` parameter-load pattern); document piL/piU recovery from `.m`.
3. Specify the Case-(a/b/c) verdict logic — Case a (match, residual ≈ 0, PATH converges); Case b (residual ≠ 0 at the NLP KKT point ⇒ **emit bug**); Case c (residual ≈ 0 but cold PATH diverges ⇒ **non-convexity**); output a per-row residual table + the verdict + the max-residual row.
4. Specify the output format — machine-readable (JSON) + human summary; the standard Phase-0 "Verification Methodology" command.
5. Identify the first three consumers — mine (#1224), camshape (#1388), kand (#1390) — with sketched invocations.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_28/PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md` — CLI, dual-transfer mechanism, Case-(a/b/c) verdict logic, output format
- Worked invocation sketches for mine/camshape/kand
- The exact Phase-0 "Verification Methodology" command string (for Tasks 3 + 5 to reference)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 9.1, 9.2, 9.3, 1.3, 2.2, 5.1, 5.2
- CHANGELOG.md updated with Task 4 completion entry

**Known Unknowns Updates:**

For each of Unknowns 9.1, 9.2, 9.3, 1.3, 2.2, 5.1, 5.2 in KNOWN_UNKNOWNS.md, update "Verification Results":

- Status: ✅ VERIFIED (or ❌ WRONG with correction)
- Verified by: Task 4 (Design the KKT-Residual Verification Harness)
- Date: YYYY-MM-DD
- Findings: the dual-transfer design (9.1), verdict thresholds (9.2), runtime/`--gdx` mitigation (9.3); for 1.3/2.2/5.1/5.2, how the harness is the verification instrument
- Evidence: the design-doc sections + the validation-against-known-cases plan (launch/camshape)
- Decision: harness is the standard Phase-0 verification command; first consumers mine/camshape/kand

**PREP_PLAN.md Updates:**

In §Task 4: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all "Acceptance Criteria".

**CHANGELOG.md Update:**

```markdown
- **Prep Task 4 COMPLETE (YYYY-MM-DD):** Designed the KKT-residual verification harness (`scripts/diagnostics/kkt_residual.py`) — CLI (`<model.gms> [--gdx] [--tol]`), dual-transfer mechanism (nu/lam/piL/piU incl. the inequality→`comp_*` generalization of the Sprint 27 `pwl_m`/`pwu_m` pattern), Case-(a/b/c) verdict logic (b = emit bug; c = non-convexity), JSON+human output. First consumers mine/camshape/kand sketched; the spec is the standard Phase-0 "Verification Methodology" command (PR27). Verified Unknowns 9.1, 9.2, 9.3, 1.3, 2.2, 5.1, 5.2.
```

**Quality Gate:**

```bash
make typecheck && make format && make lint && make test
```

Design-doc only (the harness is *built* in-sprint, not here) — run regardless; do NOT commit until all pass.

**Commit Message Format:**

```
Complete Sprint 28 Prep Task 4: Design the KKT-Residual Verification Harness

Design spec for scripts/diagnostics/kkt_residual.py — formalizes Sprint 27's
GDX warm-from-good-optimum experiment into the standard Case-(a/b/c) emit-bug
-vs-non-convexity discriminator. Dual-transfer generalizes the Day-9 pwl_m/pwu_m
pattern across nu/lam/piL/piU; first consumers mine/camshape/kand.

## Deliverables
- docs/planning/EPIC_4/SPRINT_28/PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 9.1, 9.2, 9.3, 1.3, 2.2, 5.1, 5.2 verified
- PREP_PLAN.md: Task 4 -> COMPLETE
- CHANGELOG.md: Task 4 entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint28-task4
gh pr create --title "Complete Sprint 28 Prep Task 4: Design the KKT-Residual Verification Harness" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (design-doc only)
- [x] Design spec covers CLI, dual-transfer (incl. inequality→comp_*), Case-(a/b/c) verdict, output format
- [x] mine/camshape/kand invocations sketched; Phase-0 command string finalized
- [x] Unknowns 9.1, 9.2, 9.3, 1.3, 2.2, 5.1, 5.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 4 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 5 Prompt: Author / Refresh Phase 0 Acceptance Gates for the Six Carryforwards (PR20 + PR24)

**Branch:** Create a new branch named `planning/sprint28-task5` from `main`

**Priority:** Critical (5–7 hours) — depends on Tasks 1, 3, 4

**Objective:** Author or refresh the Phase 0 acceptance gate on each of the six carryforward issue docs (#1224, #1388, #1393+#1335, #1387, #1390, camcge) so each has the four required subsections — Hand-Derived KKT Shape, Expected Emit Pattern (as a hypothesis per PR24), Verification Methodology (referencing the KKT-residual harness per PR27), and PROCEED/REPLAN Signal (citing the Day-0 traced surface per PR24). This is the central scope-correctness gate that caught four mis-scopes in Sprint 27.

**Unknowns Verified:** 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.2

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_28/PREP_PLAN.md` §Task 5
- `docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md` §Categories 1–4 (Unknowns 1.1–1.3, 2.1–2.3, 3.1–3.3, 4.2)
- `CONTRIBUTING.md` Phase-0 template **as amended by Task 3** (the four `###` subsections + the new Traced-Fix-Surface line) — Task 3 must be merged first
- `docs/planning/EPIC_4/SPRINT_28/PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md` (Task 4 — the harness invocation each gate references)
- `docs/planning/EPIC_4/SPRINT_28/BASELINE_METRICS.md` (Task 2 — the provenance row to cross-link)
- The six carryforward issue docs:
  - `docs/issues/ISSUE_1224_mine-paramref-index-offset-unsupported.md`
  - `docs/issues/ISSUE_1388_camshape-mcp-locally-infeasible-post-pattern-e-reclassification.md`
  - `docs/issues/ISSUE_1393_ad-scalar-eq-sum-collapse-symbolic-superset.md` + `docs/issues/ISSUE_1335_ad-missing-zdef-cross-term-time-reversal-index.md`
  - `docs/issues/ISSUE_1387_*.md`, `docs/issues/ISSUE_1390_kand-tree-predicate-aliased-sum-architecture-redesign.md`
  - camcge — create a new `docs/issues/ISSUE_<N>_camcge-singular-jacobian-cge-degeneracy.md` if none exists
- `docs/planning/EPIC_4/PROJECT_PLAN.md` Sprint 28 Priorities 1–6 (per-priority hand-derived target shapes) + `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md`

**Tasks to Complete:**

1. For each of the six carryforwards, author/refresh the four `###` Phase-0 subsections (use literal headings `### Hand-Derived KKT Shape`, `### Expected Emit Pattern`, `### Verification Methodology`, `### PROCEED/REPLAN Signal`):
   - **Hand-Derived KKT Shape** — the per-term Lagrangian stationarity (e.g. #1224 `stat_x(l,i,j)` with `sum(k, lam_pr(k,l,i-li(k),j-lj(k)))` − the `l-1` term; #1388 interior `stat_r(i)` + edge `lam_convex_edge*`).
   - **Expected Emit Pattern (hypothesis)** — the GAMS the emit *should* produce, explicitly labeled a prep hypothesis pending the Day-0 trace.
   - **Verification Methodology** — the exact `kkt_residual.py` invocation + expected residual + target PATH solution (mine MS 1; camshape area ≈ 4.2841; otpop cost ≈ 4217.80; cclinpts rel_diff < 1%; kand 2613.0; camcge MS 1).
   - **PROCEED/REPLAN Signal** — PROCEED requires the Day-0 traced surface + a confirming residual; REPLAN exits named for #1387/#1390/camcge (→ Sprint 29).
2. Flag the diagnosis-heavy three (#1387/#1390/camcge) in their PROCEED/REPLAN sections with a pointer to the Task 6 hypothesis-validation as a precondition for src/ effort.
3. Cross-link each gate to its KNOWN_UNKNOWNS category and its BASELINE_METRICS provenance row.
4. Sanity-check the hand-derived shapes against the Sprint 27 diagnoses (reuse and cite where already verified — e.g. #1387's 5e-8 residual, #1224's recorded inverse-offset shape).

**Deliverables:**

- Refreshed Phase 0 acceptance gates (4 subsections each) on the six carryforward issue docs
- A camcge Phase-0 gate (new issue doc if none exists)
- Each gate references the KKT-residual harness (PR27) + the Day-0 traced-surface rule (PR24)
- REPLAN exits to Sprint 29 explicitly named for #1387/#1390/camcge
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.2
- CHANGELOG.md updated with Task 5 completion entry

**Known Unknowns Updates:**

For each of Unknowns 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.2 in KNOWN_UNKNOWNS.md, update "Verification Results":

- Status: ✅ VERIFIED (or ❌ WRONG with correction + new assumption)
- Verified by: Task 5 (Author/Refresh Phase 0 Acceptance Gates)
- Date: YYYY-MM-DD
- Findings: the hand-derived KKT shape + the candidate (hypothesis) surface for each
- Evidence: links to the authored Phase-0 sections + the harness verification command
- Decision: PROCEED criteria per carryforward; the Day-0 trace required before src/ work

**PREP_PLAN.md Updates:**

In §Task 5: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result" (per-carryforward PROCEED/REPLAN outcome); check off all "Acceptance Criteria".

**CHANGELOG.md Update:**

```markdown
- **Prep Task 5 COMPLETE (YYYY-MM-DD):** Authored/refreshed Phase 0 acceptance gates (4 `###` subsections each) on the six Sprint 28 carryforwards — #1224 mine, #1388 camshape, #1393+#1335 otpop, #1387 cclinpts, #1390 kand, camcge (new issue doc) — per PR20 + PR24. Each gate: hand-derived KKT shape (reused/cited from Sprint 27 where verified), Expected Emit Pattern labeled a hypothesis (PR24), Verification Methodology citing the KKT-residual harness invocation + target solution (PR27), PROCEED/REPLAN with the Day-0 traced-surface requirement. #1387/#1390/camcge flagged for the Task 6 REPLAN assessment with Sprint 29 exits. Verified Unknowns 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.2.
```

**Quality Gate:**

```bash
make typecheck && make format && make lint && make test
```

Docs-only (issue docs + KNOWN_UNKNOWNS/PREP_PLAN/CHANGELOG) — run regardless; do NOT commit until all pass.

**Commit Message Format:**

```
Complete Sprint 28 Prep Task 5: Author/Refresh Phase 0 Acceptance Gates (PR20 + PR24)

Six carryforward issue docs (#1224, #1388, #1393+#1335, #1387, #1390, camcge)
each gain a Phase 0 gate with Hand-Derived KKT Shape + Expected Emit Pattern
(hypothesis, PR24) + Verification Methodology (KKT-residual harness, PR27) +
PROCEED/REPLAN (traced surface). #1387/#1390/camcge flagged for Task 6 with
explicit Sprint 29 REPLAN exits.

## Deliverables
- docs/issues/ISSUE_{1224,1388,1393,1335,1387,1390}_*.md + camcge issue doc: Phase 0 gates
- KNOWN_UNKNOWNS.md: Unknowns 1.1,1.2,1.3,2.1,2.2,2.3,3.1,3.2,3.3,4.2 verified
- PREP_PLAN.md: Task 5 -> COMPLETE
- CHANGELOG.md: Task 5 entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint28-task5
gh pr create --title "Complete Sprint 28 Prep Task 5: Author/Refresh Phase 0 Acceptance Gates (PR20 + PR24)" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs-only)
- [x] All six carryforwards have a Phase 0 gate with the four `###` subsections
- [x] Expected Emit Pattern labeled a hypothesis; Verification Methodology cites kkt_residual.py
- [x] REPLAN exits named for #1387/#1390/camcge
- [x] Unknowns 1.1,1.2,1.3,2.1,2.2,2.3,3.1,3.2,3.3,4.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 5 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 6 Prompt: Diagnosis-Heavy Track REPLAN Risk Assessment (#1387, #1390, camcge; PR16)

**Branch:** Create a new branch named `planning/sprint28-task6` from `main`

**Priority:** High (4–6 hours) — depends on Task 5

**Objective:** Apply the PR16 single-model hypothesis-validation methodology to the three REPLAN-prone carryforwards (#1387 cclinpts three-coupled-change, #1390 kand 195-vs-2613 re-diagnosis, camcge singular-Jacobian) to decide — on evidence, before the sprint commits the combined budget — whether each is a Sprint 28 implementation or a Sprint 29 re-scope. Produce a risk-assessment doc with a PROCEED/REPLAN recommendation per track.

**Unknowns Verified:** 4.1, 4.3, 5.1, 5.2, 5.3, 6.1, 6.2

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_28/PREP_PLAN.md` §Task 6
- `docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md` §Categories 4, 5, 6
- The six carryforwards' Phase 0 gates (Task 5 — these must be authored first)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` Sprint 28 Priorities 4, 5, 6
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md` §3.5 (#1390 re-REPLAN) + the Sprint 27 Day-6 #1387 binding diagnosis (`SPRINT_LOG.md` Day 6) — the "sign-flip is a misdiagnosis" finding + the three-coupled-change blocker
- `docs/planning/EPIC_4/SPRINT_28/PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md` (Task 4 — the validation instrument)

**Tasks to Complete:**

1. **#1387 cclinpts** — design (do not implement) the single-model validation: confirm the three coupled changes are still required (re-verify the anchor blocker against current `main`); assess whether the re-symbolization anchor fix is *architectural* (all re-symbolization callers) or *local* (gated to the offset case). Recommend PROCEED if local; REPLAN to Sprint 29 if architectural.
2. **#1390 kand** — design the Day-0 trace plan: use the KKT-residual harness to localize the 195-vs-2613 gap to a specific stationarity/complementarity row (bal/x vs lag-duality vs LP-recourse). Recommend PROCEED if a localizable row; REPLAN if LP-recourse-coupling architecture. Phantom-term re-symbolization stays out of scope (proven inert).
3. **camcge** — design the singular-row identification plan: PATH listing basis-singularity report + Jacobian rank check at the NLP point; assess whether a numéraire fix / redundant-row drop preserves the economic solution. Recommend PROCEED if a clean fix exists; else document "inherent CGE degeneracy → Epic 5 observation task".
4. Write the risk-assessment doc with the per-track PROCEED/REPLAN recommendation, the validation instrument, the budget-at-risk, and the Sprint 29 re-scope path.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_28/PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md` — per-track hypothesis-validation design + PROCEED/REPLAN recommendation
- Single-model validation plan for each of #1387/#1390/camcge (instrument, signal, decision)
- Explicit Sprint 29 re-scope path per track
- Budget-at-risk tally (feeds Task 10's schedule lower bound)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.3, 5.1, 5.2, 5.3, 6.1, 6.2
- CHANGELOG.md updated with Task 6 completion entry

**Known Unknowns Updates:**

For each of Unknowns 4.1, 4.3, 5.1, 5.2, 5.3, 6.1, 6.2 in KNOWN_UNKNOWNS.md, update "Verification Results":

- Status: ✅ VERIFIED (or ❌ WRONG with correction)
- Verified by: Task 6 (Diagnosis-Heavy Track REPLAN Risk Assessment)
- Date: YYYY-MM-DD
- Findings: the architectural-vs-local verdict (4.1), warm-start generalizability (4.3), the kand gap-localization + dual-transfer reliability (5.1/5.2), the kand NLP-reference check (5.3), the camcge singular-row finding (6.1), the camcge Day-0 bucket (6.2)
- Evidence: the hypothesis-validation design + harness output (or the plan to obtain it)
- Decision: PROCEED vs REPLAN-to-Sprint-29 per track

**PREP_PLAN.md Updates:**

In §Task 6: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result" (the three PROCEED/REPLAN recommendations); check off all "Acceptance Criteria".

**CHANGELOG.md Update:**

```markdown
- **Prep Task 6 COMPLETE (YYYY-MM-DD):** PR16 single-model REPLAN risk assessment for the three diagnosis-heavy carryforwards. #1387 cclinpts: <PROCEED if the re-symbolization anchor fix is local | REPLAN if architectural>. #1390 kand: <PROCEED if the 195-vs-2613 gap localizes to a stationarity/complementarity row | REPLAN if LP-recourse-coupling architecture>. camcge: <PROCEED if a numéraire/redundant-row fix preserves the economic solution | document inherent CGE degeneracy → Epic 5>. Budget-at-risk tally feeds the Task 10 schedule. Verified Unknowns 4.1, 4.3, 5.1, 5.2, 5.3, 6.1, 6.2.
```

**Quality Gate:**

```bash
make typecheck && make format && make lint && make test
```

Docs-only — run regardless; do NOT commit until all pass.

**Commit Message Format:**

```
Complete Sprint 28 Prep Task 6: Diagnosis-Heavy Track REPLAN Risk Assessment (PR16)

Single-model hypothesis-validation + PROCEED/REPLAN recommendation for #1387
cclinpts (anchor fix architectural-vs-local), #1390 kand (195-vs-2613 gap
localization), and camcge (singular-Jacobian / numeraire vs Epic-5). Explicit
Sprint 29 re-scope path per track; budget-at-risk feeds the Task 10 schedule.

## Deliverables
- docs/planning/EPIC_4/SPRINT_28/PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md
- KNOWN_UNKNOWNS.md: Unknowns 4.1, 4.3, 5.1, 5.2, 5.3, 6.1, 6.2 verified
- PREP_PLAN.md: Task 6 -> COMPLETE
- CHANGELOG.md: Task 6 entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint28-task6
gh pr create --title "Complete Sprint 28 Prep Task 6: Diagnosis-Heavy Track REPLAN Risk Assessment (PR16)" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs-only)
- [x] All three tracks have a single-model hypothesis-validation + PROCEED/REPLAN recommendation
- [x] Sprint 29 re-scope path named per track; budget-at-risk tallied
- [x] Unknowns 4.1, 4.3, 5.1, 5.2, 5.3, 6.1, 6.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 6 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 7 Prompt: Golden-Staleness Drift Audit + CI-Check Design (PR26 / Priority 8)

**Branch:** Create a new branch named `planning/sprint28-task7` from `main`

**Priority:** High (3–4 hours) — depends on Task 2

**Objective:** Catalog the existing golden-staleness drift across the corpus (which `*_mcp.gms` / `*_mcp_presolve.gms` goldens differ from current emit) and design the `scripts/sprint_audit/check_golden_staleness.py` check + its CI integration + the `make regen-goldens` bulk-refresh target. The audit produces the allowlist (known-failing / non-deterministic models) and sizes the one-time corpus-refresh commit.

**Unknowns Verified:** 8.1, 8.2, 8.3

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_28/PREP_PLAN.md` §Task 7
- `docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md` §Category 8 (Unknowns 8.1, 8.2, 8.3)
- `docs/planning/EPIC_4/SPRINT_28/BASELINE_METRICS.md` (Task 2 — the failure buckets that seed the allowlist)
- `docs/planning/EPIC_4/SPRINT_27/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently #3" (the silent golden drift — cesam/fawley/korcge/dinam)
- `scripts/gamslib/run_full_test.py`, `src/cli.py`, `src/emit/emit_gams.py` (emit entry); `data/gamslib/mcp/*_mcp.gms` + `*_mcp_presolve.gms` (golden artifacts)
- PR12 determinism guard (byte-identical under ≥ 3 `PYTHONHASHSEED`)

**Tasks to Complete:**

1. Run a drift audit — regenerate every translating model's golden and diff against the committed artifact; produce the drift inventory (model → drifted/clean → reason).
2. Define the allowlist — known-failing (non-translating) + non-deterministic models the check excludes, with a reason per entry.
3. Design the check interface — `check_golden_staleness.py [--fix]`: regenerate → diff → report (`--fix` = bulk refresh = `make regen-goldens`); exit non-zero on unexpected drift (not on allowlisted models).
4. Design the CI integration — a `.github/workflows/` job triggered on PRs touching `src/{ad,kkt,emit,ir}/`; specify the runtime budget + failure-message format (note the > 5 min/PR friction threshold).
5. Size the one-time corpus-refresh commit — list the models the early-sprint refresh regenerates (cesam/fawley/korcge/dinam/…) so it is a single reviewable commit.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_28/PRIORITY_8_GOLDEN_STALENESS_DESIGN.md` — drift inventory, allowlist, check interface, CI integration, refresh-commit scope
- The drift inventory (model → drifted/clean → reason) + the allowlist (with reasons)
- `make regen-goldens` target design + CI job design
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 8.1, 8.2, 8.3
- CHANGELOG.md updated with Task 7 completion entry

**Known Unknowns Updates:**

For each of Unknowns 8.1, 8.2, 8.3 in KNOWN_UNKNOWNS.md, update "Verification Results":

- Status: ✅ VERIFIED (or ❌ WRONG with correction)
- Verified by: Task 7 (Golden-Staleness Drift Audit + CI-Check Design)
- Date: YYYY-MM-DD
- Findings: the drift count + allowlist size (8.1), the CI trigger paths + runtime (8.2), the determinism-clean result (8.3)
- Evidence: the drift inventory table + the CI-timing measurement
- Decision: the check interface + CI trigger scope + refresh-commit model list

**PREP_PLAN.md Updates:**

In §Task 7: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all "Acceptance Criteria".

**CHANGELOG.md Update:**

```markdown
- **Prep Task 7 COMPLETE (YYYY-MM-DD):** Golden-staleness drift audit + CI-check design (PR26). Drift inventory: <n> translating models' goldens differ from current emit (incl. cesam/fawley/korcge/dinam); allowlist of <n> known-failing/non-deterministic models. Designed `scripts/sprint_audit/check_golden_staleness.py [--fix]` (regenerate→diff→report) + a `.github/workflows/` job on `src/{ad,kkt,emit,ir}/` PRs + a `make regen-goldens` target; sized the one-time corpus-refresh commit. Determinism-clean under the PR12 guard. Verified Unknowns 8.1, 8.2, 8.3.
```

**Quality Gate:**

```bash
make typecheck && make format && make lint && make test
```

The audit *runs* the existing emit but the deliverable is a design doc (the check is built in-sprint). Run the gate regardless; do NOT commit until all pass. If you committed a refresh of drifted goldens, confirm they are byte-stable under the PR12 guard.

**Commit Message Format:**

```
Complete Sprint 28 Prep Task 7: Golden-Staleness Drift Audit + CI-Check Design (PR26)

Drift inventory of *_mcp.gms / *_mcp_presolve.gms goldens vs current emit +
allowlist of known-failing/non-deterministic models. Designed
scripts/sprint_audit/check_golden_staleness.py [--fix], the src/{ad,kkt,emit,ir}/
CI gate, and make regen-goldens; sized the one-time corpus-refresh commit.

## Deliverables
- docs/planning/EPIC_4/SPRINT_28/PRIORITY_8_GOLDEN_STALENESS_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 8.1, 8.2, 8.3 verified
- PREP_PLAN.md: Task 7 -> COMPLETE
- CHANGELOG.md: Task 7 entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint28-task7
gh pr create --title "Complete Sprint 28 Prep Task 7: Golden-Staleness Drift Audit + CI-Check Design (PR26)" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS
- [x] Drift inventory + allowlist documented; CI trigger paths + runtime budget designed
- [x] check_golden_staleness.py interface + make regen-goldens designed; refresh-commit scope sized
- [x] Unknowns 8.1, 8.2, 8.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 7 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 8 Prompt: Divergence Detector + AD Cross-Term Property-Test Catalog Design (Priority 10)

**Branch:** Create a new branch named `planning/sprint28-task8` from `main`

**Priority:** Medium (3–4 hours) — depends on Task 1

**Objective:** Design the `scripts/diagnostics/check_presolve_divergence.py` detector (compare embedded-NLP objective to standalone-NLP objective per `--nlp-presolve` model, flag divergence) and catalog the recurring AD cross-term shapes (offset sums, alias sums, parameter-valued offsets) into a property-test specification (≥ 6 synthetic models with hand-derived KKT) that systematically guards the #1224/#1388/#1390 cross-term defect class.

**Unknowns Verified:** 10.1, 10.2, 10.3

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_28/PREP_PLAN.md` §Task 8
- `docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md` §Category 10 (Unknowns 10.1, 10.2, 10.3)
- `docs/planning/EPIC_4/SPRINT_27/SPRINT_LOG.md` Days 9/11 (#1378 launch self-ref param via `src/emit/original_symbols.py`; #1424 camshape subset corruption via `src/emit/emit_gams.py`) — the embedded-vs-standalone divergence wins
- `src/emit/emit_gams.py` (`_will_emit_nlp_presolve`; the `$include` under `$onMultiR`)
- `docs/research/multidimensional_indexing.md`, `docs/research/nested_subset_indexing_research.md` (cross-term shapes); the #1224/#1388/#1390 issue docs
- Existing AD/KKT unit-test conventions: `tests/unit/` + `@pytest.mark.unit`

**Tasks to Complete:**

1. Design the divergence detector — `check_presolve_divergence.py`: extract the embedded-NLP objective (from the `$include`d pre-solve) and the standalone-NLP objective per presolve model; flag divergence beyond tolerance; specify the false-positive allowlist (legitimately-differing models).
2. Catalog the recurring cross-term shapes — (a) single-axis offset Sum, (b) self-alias Sum, (c) cross-set alias Sum, (d) parameter-valued offset, (e) interior+edge convex-combination (camshape), (f) tree-predicate-conditioned aliased Sum (kand) — each with the hand-derived stationarity cross-term the emit must produce.
3. Specify the property-test suite — ≥ 6 synthetic GAMS models (small, hand-checkable) + the assertion that the emit's stationarity cross-terms match the hand-derived shape; specify location (`tests/unit/ad/` or `tests/integration/emit/`) + CI wiring.
4. Validate against the past wins — confirm in the design that the detector would have flagged #1378 + #1424 at translate time.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_28/PRIORITY_10_DIVERGENCE_PROPERTY_TESTS_DESIGN.md` — detector design + cross-term shape catalog + property-test spec
- Divergence-detector interface (embedded-vs-standalone objective comparison + allowlist)
- ≥ 6 catalogued synthetic cross-term shapes, each with its hand-derived stationarity term
- CI-wiring plan for both the detector and the property tests
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 10.1, 10.2, 10.3
- CHANGELOG.md updated with Task 8 completion entry

**Known Unknowns Updates:**

For each of Unknowns 10.1, 10.2, 10.3 in KNOWN_UNKNOWNS.md, update "Verification Results":

- Status: ✅ VERIFIED (or ❌ WRONG with correction)
- Verified by: Task 8 (Divergence Detector + AD Cross-Term Property-Test Catalog Design)
- Date: YYYY-MM-DD
- Findings: the detector reliability + #1378/#1424 replay result (10.1), the cross-term shape catalog (10.2), the property-test speed/stability (10.3)
- Evidence: the design-doc sections + the synthetic-model sketches
- Decision: the detector + property tests are CI-wired; the catalog covers the #1224/#1388/#1390 defect class

**PREP_PLAN.md Updates:**

In §Task 8: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all "Acceptance Criteria".

**CHANGELOG.md Update:**

```markdown
- **Prep Task 8 COMPLETE (YYYY-MM-DD):** Designed the embedded-NLP-divergence detector (`scripts/diagnostics/check_presolve_divergence.py` — embedded vs standalone NLP objective + false-positive allowlist; would have flagged #1378 + #1424 at translate time) + the AD cross-term property-test catalog (≥ 6 synthetic shapes — offset Sum, self-alias, cross-set alias, parameter-valued offset, interior+edge convex-combination, tree-conditioned aliased Sum — each with a hand-derived stationarity term, asserting the emit matches). Both CI-wired. Covers the #1224/#1388/#1390 cross-term defect class. Verified Unknowns 10.1, 10.2, 10.3.
```

**Quality Gate:**

```bash
make typecheck && make format && make lint && make test
```

Design-doc only (the detector + tests are built in-sprint) — run regardless; do NOT commit until all pass.

**Commit Message Format:**

```
Complete Sprint 28 Prep Task 8: Divergence Detector + AD Cross-Term Property-Test Catalog Design

Designed check_presolve_divergence.py (embedded-vs-standalone NLP objective;
catches the $onMultiR re-run bug class that drove #1378 + #1424) + a catalog of
>=6 AD cross-term synthetic shapes with hand-derived stationarity terms, guarding
the #1224/#1388/#1390 defect class. Both CI-wired.

## Deliverables
- docs/planning/EPIC_4/SPRINT_28/PRIORITY_10_DIVERGENCE_PROPERTY_TESTS_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 10.1, 10.2, 10.3 verified
- PREP_PLAN.md: Task 8 -> COMPLETE
- CHANGELOG.md: Task 8 entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint28-task8
gh pr create --title "Complete Sprint 28 Prep Task 8: Divergence Detector + AD Cross-Term Property-Test Catalog Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (design-doc only)
- [x] Detector interface designed; would have flagged #1378 + #1424
- [x] >=6 cross-term shapes catalogued with hand-derived terms; property-test CI wiring specified
- [x] Unknowns 10.1, 10.2, 10.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 8 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 9 Prompt: Lower-Priority Cleanups Fix-Surface Analysis (#1374, #1400, #1385)

**Branch:** Create a new branch named `planning/sprint28-task9` from `main`

**Priority:** Medium (2–3 hours) — depends on Task 1

**Objective:** Identify the candidate fix surfaces (as Day-0-traceable hypotheses per PR24) for the three Sprint 27 lower-priority cleanups so the in-sprint work (Priority 7) starts from a scoped patch-site analysis: #1374 `.l` denominator/override dedup (robot's second shape), #1400 `message`-field captured-warning path relativization (the second absolute-path leak), and #1385 runtime-guard cross-terms (srpchase `J_gᵀ·lam` coupled with the equation-body re-emit).

**Unknowns Verified:** 7.1, 7.2, 7.3

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_28/PREP_PLAN.md` §Task 9
- `docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md` §Category 7 (Unknowns 7.1, 7.2, 7.3)
- `docs/issues/ISSUE_1374_emitter-redundant-duplicate-variable-initializations.md` (Sprint 27 fixed the dominant `.fx` shape; robot `.l` shape deferred)
- `docs/issues/ISSUE_1385_option-1-short-circuit-redesign-symbolic-instance-handling.md`
- `scripts/gamslib/run_full_test.py` (`_repo_relative_path`; the `mcp_file_used` #1400 fix — the `message`-field leak is the second one)
- `src/emit/emit_gams.py` (Variable Bounds + suppressed-fx restore — the Sprint 27 #1374 dominant-shape fix) + `src/kkt/stationarity.py` (#1385 runtime-guard re-emit)
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_7_FIX_SURFACE.md` (prior cleanup analyses)

**Tasks to Complete:**

1. **#1374** — locate the robot second-shape emission (denominator-init block + `fx_to_l_override`); determine whether dedup is isolatable from the Sprint 27 dominant-shape fix; sketch the emit-time dedup.
2. **#1400** — locate the warning-capture path that writes `…/src/…py:NNN` into the `message` field; audit `gamslib_status.json` for absolute-path substrings in `message`; sketch the relativization (reuse `_repo_relative_path` or equivalent).
3. **#1385** — confirm the runtime-guard equation-body re-emit (`stationarity.py`) and the `J_gᵀ·lam` cross-terms are the atomic unit (re-emit without cross-terms = inconsistent MCP); sketch the combined change or document the re-scope if larger than a cleanup.
4. Write the fix-surface analysis with the candidate surfaces (flagged as Day-0-trace hypotheses), the coupling risks, and the per-item estimate.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_28/PRIORITY_7_CLEANUPS_FIX_SURFACE.md` — candidate fix surfaces (hypotheses), coupling risks, per-item estimates for #1374/#1400/#1385
- Explicit note that #1385's cross-terms + re-emit are atomic
- Confirmation of whether #1374's robot shape is coupled to the Sprint 27 dominant-shape fix
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 7.1, 7.2, 7.3
- CHANGELOG.md updated with Task 9 completion entry

**Known Unknowns Updates:**

For each of Unknowns 7.1, 7.2, 7.3 in KNOWN_UNKNOWNS.md, update "Verification Results":

- Status: ✅ VERIFIED (or ❌ WRONG with correction)
- Verified by: Task 9 (Lower-Priority Cleanups Fix-Surface Analysis)
- Date: YYYY-MM-DD
- Findings: robot dedup isolation (7.1), #1400 second-leak location + DB audit (7.2), #1385 atomic-landing requirement (7.3)
- Evidence: the emission-site traces + the `gamslib_status.json` audit
- Decision: the candidate (hypothesis) surface + per-item estimate; whether #1385 stays a cleanup or re-scopes

**PREP_PLAN.md Updates:**

In §Task 9: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all "Acceptance Criteria".

**CHANGELOG.md Update:**

```markdown
- **Prep Task 9 COMPLETE (YYYY-MM-DD):** Fix-surface analysis (as Day-0-trace hypotheses, PR24) for the three Sprint 27 lower-priority cleanups. #1374 robot `.l` dedup: <isolated from the Sprint 27 `.fx`-restore fix | coupled>. #1400 second path leak: located in the warning-capture `message`-field path (DB-audited). #1385: runtime-guard eq-body re-emit + `J_gᵀ·lam` cross-terms confirmed <atomic | larger-than-cleanup → re-scope>. Per-item estimates feed the Task 10 schedule. Verified Unknowns 7.1, 7.2, 7.3.
```

**Quality Gate:**

```bash
make typecheck && make format && make lint && make test
```

Docs-only — run regardless; do NOT commit until all pass.

**Commit Message Format:**

```
Complete Sprint 28 Prep Task 9: Lower-Priority Cleanups Fix-Surface Analysis

Candidate fix surfaces (Day-0-trace hypotheses, PR24) for #1374 robot .l dedup,
#1400 message-field path leak, and #1385 runtime-guard cross-terms, with the
coupling risks (robot-vs-Sprint-27 fix; #1385 atomic re-emit+cross-terms) and
per-item estimates for the Task 10 schedule.

## Deliverables
- docs/planning/EPIC_4/SPRINT_28/PRIORITY_7_CLEANUPS_FIX_SURFACE.md
- KNOWN_UNKNOWNS.md: Unknowns 7.1, 7.2, 7.3 verified
- PREP_PLAN.md: Task 9 -> COMPLETE
- CHANGELOG.md: Task 9 entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint28-task9
gh pr create --title "Complete Sprint 28 Prep Task 9: Lower-Priority Cleanups Fix-Surface Analysis" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs-only)
- [x] All three cleanups have a candidate fix surface (Day-0-trace hypothesis) + coupling risk + estimate
- [x] #1374 coupling assessed; #1400 second leak located; #1385 atomic-landing documented
- [x] Unknowns 7.1, 7.2, 7.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 9 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 10 Prompt: Plan Sprint 28 Detailed Schedule

**Branch:** Create a new branch named `planning/sprint28-task10` from `main`

**Priority:** Critical (3–4 hours) — depends on Tasks 1–9 (final integration; run last)

**Objective:** Create the detailed Sprint 28 plan (`docs/planning/EPIC_4/SPRINT_28/PLAN.md`) and the day-by-day execution prompts (`prompts/PLAN_PROMPTS.md`), incorporating every prior prep task: the Known Unknowns (Task 1), the baseline + projection discipline (Task 2), the codified PR24/PR25 rules (Task 3), the front-loaded KKT-residual harness (Task 4), the Phase 0 gates (Task 5), the REPLAN assessment (Task 6), and the three infrastructure designs + cleanups (Tasks 7–9).

**Unknowns Verified:** integrates all — Unknowns 1.1–10.3 (reconciled into the schedule)

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_28/PREP_PLAN.md` §Task 10 + the COMPLETE status of Tasks 1–9 (all prior prep PRs must be merged)
- `docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md` (all verification results filled by Tasks 2–9)
- `docs/planning/EPIC_4/SPRINT_28/BASELINE_METRICS.md` (Task 2), `PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md` (Task 4), the six Phase 0 gates (Task 5), `PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md` (Task 6), `PRIORITY_8_GOLDEN_STALENESS_DESIGN.md` (Task 7), `PRIORITY_10_DIVERGENCE_PROPERTY_TESTS_DESIGN.md` (Task 8), `PRIORITY_7_CLEANUPS_FIX_SURFACE.md` (Task 9)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` Sprint 28 (Estimated Effort 98–144h; ≤ 12h/day; Risk HIGH)
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` + `prompts/PLAN_PROMPTS.md` (structural templates)

**Tasks to Complete:**

1. Author `PLAN.md` — Sprint Goals; Day-0 setup + Days 1–13 day-by-day plan; the front-loaded harness (Days 1–3); the carryforward sequence with the diagnosis-heavy tracks gated on their Task-6 REPLAN signals; the two infrastructure tracks (P8, P10) interleaved as lower-risk fill; per-day integration risks + complexity estimates; the checkpoint schedule (Day 5, Day 10) + final retest (Day 13) with the PR25 projection tally; acceptance criteria; contingency/REPLAN plans.
2. Author `prompts/PLAN_PROMPTS.md` — one execution prompt per day (scope, the Phase-0 gate to clear, the KKT-residual harness invocation where relevant, the "flag stale assumptions" reminder); **no prompt carries a forward-looking claim about work not yet done** (the Sprint 27 stale-prompt failure mode).
3. Verify the schedule fits the budget — sum per-day estimates ≤ 168h with the lower bound assuming #1387/#1390/camcge partially slip (per Task 6); no day > 12h.
4. Cross-link the plan to KNOWN_UNKNOWNS, BASELINE_METRICS, the Phase-0 gates, and the three infra design docs.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_28/PLAN.md` — Day-0 + Days 1–13 with risks, estimates, checkpoints, acceptance criteria, contingency/REPLAN plans
- `docs/planning/EPIC_4/SPRINT_28/prompts/PLAN_PROMPTS.md` — one prompt per day, no stale forward-looking claims
- A schedule that front-loads the harness and gates the diagnosis-heavy tracks on their REPLAN signals; ≤ 12h/day verified; checkpoints (Day 5/10) + final retest (Day 13) with the PR25 tally
- KNOWN_UNKNOWNS.md fully reconciled — all Unknowns 1.1–10.3 carry a final status integrated into the schedule
- CHANGELOG.md updated with Task 10 completion entry

**Known Unknowns Updates:**

Reconcile **all** Unknowns 1.1–10.3 in KNOWN_UNKNOWNS.md — confirm each carries a ✅ VERIFIED / ❌ WRONG status from its owning task (Tasks 2–9). For any still 🔍 INCOMPLETE that is implementation-time-dependent, annotate the Sprint 28 day on which it will be VERIFIED (per the schedule), mirroring the Sprint 27 §16 approach. Record the reconciliation in this task's Verification Results pass:

- Status: the integrated status per unknown
- Verified by: Task 10 (Plan Sprint 28 Detailed Schedule) — integration
- Date: YYYY-MM-DD
- Findings: which unknowns are resolved pre-sprint vs scheduled for in-sprint VERIFICATION
- Decision: the day-by-day schedule honoring all PROCEED/REPLAN signals

**PREP_PLAN.md Updates:**

In §Task 10: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all "Acceptance Criteria". Add a "Final Prep-Task Status" table (all 10 prep tasks ✅ COMPLETE; total prep effort vs the 32–44h budget; the PR numbers).

**CHANGELOG.md Update:**

```markdown
- **Prep Task 10 COMPLETE (YYYY-MM-DD):** Integrated Tasks 1–9 into a 14-day Sprint 28 execution schedule (`docs/planning/EPIC_4/SPRINT_28/PLAN.md`) + per-day execution prompts (`prompts/PLAN_PROMPTS.md`) + SPRINT_LOG.md skeleton. Day 0 builds the KKT-residual harness (front-loaded Days 1–3); carryforward sequence gates #1387/#1390/camcge on their Task-6 REPLAN signals; P8 golden-staleness + P10 divergence/property-tests interleaved as lower-risk fill; checkpoints Day 5/Day 10 + final 3× PYTHONHASHSEED retest Day 13 with the PR25 projection tally. Per-day budget verified ≤ 12h within the 168h cap. All Unknowns 1.1–10.3 reconciled (resolved pre-sprint or scheduled for in-sprint VERIFICATION). Sprint 28 GO for Day 0.
```

**Quality Gate:**

```bash
make typecheck && make format && make lint && make test
```

Docs-only — run regardless; do NOT commit until all pass.

**Commit Message Format:**

```
Complete Sprint 28 Prep Task 10: Plan Sprint 28 Detailed Schedule

14-day schedule + per-day prompts integrating Tasks 1-9. KKT-residual harness
front-loaded (Days 1-3); diagnosis-heavy tracks gated on Task-6 REPLAN signals;
P8/P10 infra interleaved; checkpoints Day 5/10 + final 3x PYTHONHASHSEED retest
Day 13 with the PR25 tally. <=12h/day verified. All Unknowns 1.1-10.3 reconciled.

## Deliverables
- docs/planning/EPIC_4/SPRINT_28/PLAN.md + prompts/PLAN_PROMPTS.md
- KNOWN_UNKNOWNS.md: all Unknowns 1.1-10.3 reconciled
- PREP_PLAN.md: Task 10 -> COMPLETE + Final Prep-Task Status table
- CHANGELOG.md: Task 10 entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint28-task10
gh pr create --title "Complete Sprint 28 Prep Task 10: Plan Sprint 28 Detailed Schedule" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs-only)
- [x] PLAN.md covers Day 0 + Days 1–13 (risks, estimates, checkpoints, acceptance, contingency)
- [x] PLAN_PROMPTS.md has one prompt per day with no stale forward-looking claims
- [x] Harness front-loaded; diagnosis-heavy tracks gated on Task-6 REPLAN signals; ≤ 12h/day verified
- [x] All Unknowns 1.1–10.3 reconciled in KNOWN_UNKNOWNS.md
- [x] Task 10 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Appendix: Task → Branch → Unknowns Quick Reference

| Task | Branch | Priority | Depends on | Unknowns Verified |
|------|--------|----------|------------|-------------------|
| 2 | `planning/sprint28-task2` | Critical | Task 1 ✅ | 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 6.2 |
| 3 | `planning/sprint28-task3` | Critical | Task 1 ✅ | 1.1, 2.1, 3.1, 4.1, 5.1 |
| 4 | `planning/sprint28-task4` | High | Task 1 ✅ | 9.1, 9.2, 9.3, 1.3, 2.2, 5.1, 5.2 |
| 5 | `planning/sprint28-task5` | Critical | Tasks 1, 3, 4 | 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.2 |
| 6 | `planning/sprint28-task6` | High | Task 5 | 4.1, 4.3, 5.1, 5.2, 5.3, 6.1, 6.2 |
| 7 | `planning/sprint28-task7` | High | Task 2 | 8.1, 8.2, 8.3 |
| 8 | `planning/sprint28-task8` | Medium | Task 1 ✅ | 10.1, 10.2, 10.3 |
| 9 | `planning/sprint28-task9` | Medium | Task 1 ✅ | 7.1, 7.2, 7.3 |
| 10 | `planning/sprint28-task10` | Critical | Tasks 1–9 | integrates all (1.1–10.3) |

**Dispatch order:** Tasks 2, 3, 4, 8, 9 in parallel → Task 7 (after 2) + Task 5 (after 3, 4) → Task 6 (after 5) → Task 10 (after all).

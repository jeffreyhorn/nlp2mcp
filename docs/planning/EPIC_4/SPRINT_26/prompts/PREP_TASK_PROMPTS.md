# Sprint 26 Prep Task Execution Prompts

Self-contained prompts for Sprint 26 Prep Tasks 2–11. Each prompt can be copy-pasted into a new conversation to execute one prep task end-to-end, including the Known Unknowns updates, PREP_PLAN.md / CHANGELOG.md updates, quality gate, commit, and PR.

**Usage:**

1. Pick a task prompt below.
2. Paste it into a new conversation.
3. The agent creates the branch, does the work, runs the quality gate, commits, pushes, and opens a PR.
4. Wait for reviewer comments on the PR.

Task 1 (Create Sprint 26 Known Unknowns List) is already complete — no prompt needed.

Tasks 2–11 are dispatchable in the following order per the dependency graph in `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md`:

- **Parallel kickoff (no dependencies beyond Task 1):** Tasks 2, 3, 4, 5, 6, 7, 8, 10
- **After Task 2:** Task 9 (needs scope-shift documentation before recording the Sprint 26 baseline)
- **After all (final integration):** Task 11

---

## Task 2 Prompt: Identify Sprint 25 Scope-Shifted Model (PR18)

**Branch:** Create a new branch named `planning/sprint26-task2` from `main`

**Priority:** Critical (1–2 hours)

**Objective:** Identify which model's convexity status changed during Sprint 25 Days 1–10 to cause the in-scope denominator to shift from 143 to 142, and document the reason in `docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md` §5. This is **Sprint 25 retrospective process recommendation PR18** — codified as the first Sprint 26 prep deliverable.

**Unknowns Verified:** 6.5

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 2
- `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` §Unknown 6.5
- `docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md` §5 (Scope Freeze — the section that needs updating)
- `docs/planning/EPIC_4/SPRINT_25/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently" #5 (PR18 origin)
- `docs/planning/EPIC_4/SPRINT_25/SPRINT_LOG.md` Day 14 entry (current 142-vs-143 framing)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` footnote ⁶ (acknowledges the shift)

**Tasks to Complete:**

1. **Locate the Sprint 25 Day 0 baseline `gamslib_status.json`** — likely under `data/gamslib/archive/` (the earliest Sprint 25 archive, dated around 2026-04-21) or recoverable via `git log --follow data/gamslib/gamslib_status.json | head -50` to find the commit closest to Sprint 25 Day 0.
2. **Locate the Sprint 25 Day 14 final `gamslib_status.json`** — `git log --oneline -- data/gamslib/gamslib_status.json | grep "Sprint 25 Day 14"` should surface the commit (`58bcbdc1` or later).
3. **Diff the two snapshots** focused on the `convexity.status` field per model. Identify which model(s) changed status and what the new status is.
4. **Determine the trigger** — for each changed model, look at git history of the model's `data/gamslib/raw/<model>.gms` file (if changed) or the convexity-detection code (`src/ir/...` if applicable) to identify the Sprint-25 commit that triggered the reclassification.
5. **Document the finding** in `docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md` §5 ("Scope Freeze") under a new sub-§"Sprint 25 Mid-Sprint Reclassification": model name, prior status, new status, triggering commit (SHA + brief description), and the policy classification (runtime filter vs scope edit).
6. **Add a forward-link note** to `docs/planning/EPIC_4/SPRINT_25/SPRINT_LOG.md` Day 14 entry referencing the new sub-section.

**Deliverables:**

- Updated `docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md` §5 with a new sub-§"Sprint 25 Mid-Sprint Reclassification"
- Updated `docs/planning/EPIC_4/SPRINT_25/SPRINT_LOG.md` Day 14 entry forward-link to the new sub-section
- Updated `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` Unknown 6.5 with verification results

**Known Unknowns Updates:**

For Unknown 6.5 in `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md`, update Verification Results:

- Status: ✅ VERIFIED (or ❌ WRONG with correction)
- Verified by: Task 2 (Identify Sprint 25 Scope-Shifted Model PR18)
- Date: today's date (YYYY-MM-DD)
- Findings: identified model name + new convexity status + triggering commit
- Evidence: archive snapshot diff output, git log lines, source file changes
- Decision: whether the shift is reversible during Sprint 26 (informs Unknown 6.5 prediction)

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 2:

- Change `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`
- Fill in the "Changes" section with a summary of what was done
- Fill in the "Result" section with the identified model + reason
- Check off all items in "Acceptance Criteria" (change `- [ ]` → `- [x]`)

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 26 Preparation`, prepend a new bullet:

```markdown
- **Prep Task 2 COMPLETE (YYYY-MM-DD):** Identified Sprint 25 scope-shifted model (PR18). Sprint 25 Days 1–10 reclassified `<model>` from `<prior_status>` to `<new_status>` via commit `<SHA>` (`<brief description>`). Documented in `docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md` §5 sub-§"Sprint 25 Mid-Sprint Reclassification" with policy classification (runtime filter — same handling as `danwolfe`/`decomp` per §5 policy). Verified Unknown 6.5.
```

**Quality Gate:**

Task 2 is research/docs only. No Python source code is modified. **Skip the Python quality gate.** If you touched any `.py` file unexpectedly, run:

```bash
make typecheck && make lint && make format && make test
```

Do NOT proceed to commit until all pass.

**Commit Message Format:**

```
Complete Sprint 26 Prep Task 2: Identify Sprint 25 Scope-Shifted Model (PR18)

Sprint 25 retrospective PR18 codification — identifies which model
caused the in-scope denominator to shift from 143 → 142 during
Sprint 25 Days 1–10, and documents the reason in BASELINE_METRICS.md.

## Key findings

- Shifted model: <model_name>
- Prior convexity status: <prior_status>
- New convexity status: <new_status>
- Triggering commit: <SHA> (<one-line description>)
- Policy classification: <runtime filter / scope edit> per BASELINE_METRICS.md §5
- Reversible during Sprint 26: <yes / no / uncertain> (per Unknown 6.5)

## Deliverables

- Updated docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md §5 with new sub-section
- Updated docs/planning/EPIC_4/SPRINT_25/SPRINT_LOG.md Day 14 entry forward-link
- Updated docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md: Unknown 6.5 verified
- Updated docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md: Task 2 status → COMPLETE
- Updated CHANGELOG.md with Task 2 completion entry
```

**Pull Request:**

After committing, push the branch and open a PR:

```bash
git push -u origin planning/sprint26-task2
gh pr create --title "Complete Sprint 26 Prep Task 2: Identify Sprint 25 Scope-Shifted Model (PR18)" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] No Python source code modified — quality gate skipped per workflow rules
- [x] Sprint 25 Day 0 vs Day 14 archive snapshots diffed
- [x] Triggering commit identified
- [x] Unknown 6.5 verified in KNOWN_UNKNOWNS.md
- [x] Task 2 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 3 Prompt: Pattern C Hypothesis Validation (PR16)

**Branch:** Create a new branch named `planning/sprint26-task3` from `main`

**Priority:** Critical (6–8 hours) — **THE central new prep activity for Sprint 26**

**Objective:** Apply the Sprint 25 Day 5 methodology — **trace capture + emitted-artifact byte comparison against formal symbolic derivative** — to the Pattern C generalization hypothesis on 2–3 representative target models BEFORE committing the 12–18h Priority 1 budget. If the hypothesis is disproved on any of the 2–3 models, replan Priority 1 during prep rather than mid-sprint. This is the codified instance of Sprint 25 retrospective process recommendation **PR16**.

**Unknowns Verified:** 1.1, 1.2, 1.3, 1.4, 1.5, 1.6

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 3
- `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` §Category 1 (Unknowns 1.1–1.6)
- `docs/planning/EPIC_4/SPRINT_25/DAY5_PATTERN_A_INVESTIGATION.md` (the methodology reference)
- `docs/planning/EPIC_4/SPRINT_25/DAY7_COHORT_SWEEP.md` (per-model classification basis)
- `docs/planning/EPIC_4/SPRINT_25/SPRINT_RETROSPECTIVE.md` §"Day 5 Pivot Retrospective" + §"What We'd Do Differently" #1 (PR16)
- `docs/issues/ISSUE_1354_camcge-phantom-indexoffset-stationarity-141.md`
- `docs/issues/ISSUE_1355_cesam2-phantom-indexoffset-nu-colsum-141.md`
- `docs/issues/ISSUE_1356_fawley-stationarity-domain-violations-171.md`
- `docs/issues/ISSUE_1357_otpop-stationarity-domain-violations-171.md`

**Tasks to Complete:**

1. **Methodology pre-flight on 1 target model** (≤ 2 hours) — apply the Day 5 methodology to camcge first to confirm the per-model time budget (~1.5–2h) and the formal-derivative tractability before scaling to 3 models.
2. **Trace capture for 3 representative target models:**
   ```bash
   mkdir -p /tmp/sprint26-day0-validation
   for m in camcge cesam2 fawley; do
     SPRINT25_DAY2_DEBUG=1 .venv/bin/python -m src.cli \
       data/gamslib/raw/${m}.gms \
       -o /tmp/sprint26-day0-validation/${m}_mcp.gms \
       --skip-convexity-check --quiet \
       2> /tmp/sprint26-day0-validation/${m}_trace.stderr
   done
   ```
3. **Hand-derive the formal KKT** for one target stationarity equation per model (camcge `stat_dk`, cesam2 `stat_tsam`, fawley `stat_<simple>`). Write each in `/tmp/sprint26-day0-validation/<model>_formal_kkt.md`.
4. **Byte-compare** the emitted form against the hand-derived form per model. Document diverging terms (these are the Pattern C bug sites).
5. **Prototype the Pattern C generalization** as a 1-line patch in `src/kkt/stationarity.py` — remove the `$cond` filter from the launch-shape gate's predicate; add `sameas`-block awareness for cesam2.
6. **Tier 0/1 canary regression** — run the prototype patch against the 11 canaries (`dispatch, quocge, partssupply, prolog, sparta, gussrisk, ps2_f, ps3_f, ship, splcge, paklive`); byte-diff against baseline.
7. **Survey full corpus for unintended gate activation** — count gate firings across the 142 in-scope set with the prototype patch; expected 4–8 firings.
8. **Decide PROCEED / REPLAN** — write the recommendation in the validation document with rationale.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_26/PATTERN_C_HYPOTHESIS_VALIDATION.md` with per-model hypothesis status (CONFIRMED / DISPROVED / PARTIAL) + canary regression report + recommendation
- 1-line prototype patch (committed as a draft branch under `prototype/sprint26-pattern-c-validation` if recommendation is PROCEED; left as a code excerpt in the validation doc otherwise)
- Trace files at `/tmp/sprint26-day0-validation/` (advisory, not committed)
- Hand-derived formal KKT excerpts at `/tmp/sprint26-day0-validation/<model>_formal_kkt.md` (advisory, not committed)
- Updated `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` Unknowns 1.1, 1.2, 1.3, 1.4, 1.5, 1.6 with verification results

**Known Unknowns Updates:**

For each of Unknowns 1.1, 1.2, 1.3, 1.4, 1.5, 1.6 in `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md`, update Verification Results:

- Status: ✅ VERIFIED or ❌ WRONG (replace 🔍 INCOMPLETE)
- Verified by: Task 3 (Pattern C Hypothesis Validation PR16)
- Date: today's date
- Findings: per-model byte-comparison outcome + canary regression count + gate-firing count
- Evidence: trace file paths, hand-derived KKT excerpts, prototype-patch code excerpt, canary diff output
- Decision: PROCEED with Sprint 26 Priority 1 as planned / REPLAN Priority 1 (with proposed alternative)

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 3:

- Status → ✅ COMPLETE
- Fill "Changes" and "Result" sections (include PROCEED/REPLAN recommendation prominently)
- Check off all Acceptance Criteria

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 26 Preparation`, prepend:

```markdown
- **Prep Task 3 COMPLETE (YYYY-MM-DD):** Pattern C hypothesis validation (PR16). Applied the Day 5 methodology to <N> target models (<list>); per-model status: <CONFIRMED / DISPROVED / PARTIAL each>. Tier 0/1 canary regression: <N>/11 byte-stable. Recommendation: <PROCEED / REPLAN> with Sprint 26 Priority 1 — <one-line rationale>. Verified Unknowns 1.1, 1.2, 1.3, 1.4, 1.5, 1.6.
```

**Quality Gate:**

Task 3 may produce a prototype patch but does NOT commit it to main (committed to a `prototype/` branch instead). The validation document is docs-only. **Skip the Python quality gate** for the planning branch. If the prototype patch is committed to its own branch, run the quality gate there:

```bash
make typecheck && make lint && make format && make test
```

Do NOT proceed to commit until all pass.

**Commit Message Format:**

```
Complete Sprint 26 Prep Task 3: Pattern C Hypothesis Validation (PR16)

Sprint 25 retrospective PR16 codification applied PRE-Sprint-0 to the
Pattern C generalization hypothesis. Day 5 methodology (trace +
emitted-artifact byte comparison vs formal symbolic derivative) on 3
representative target models (camcge, cesam2, fawley) determines
whether Sprint 26 Priority 1 should PROCEED as planned or REPLAN.

## Key findings

- camcge: <CONFIRMED / DISPROVED / PARTIAL> — <evidence>
- cesam2: <CONFIRMED / DISPROVED / PARTIAL> — <evidence>
- fawley: <CONFIRMED / DISPROVED / PARTIAL> — <evidence>
- Tier 0/1 canary regression: <N>/11 byte-stable
- Gate-firing count on full 142 in-scope set: <N>
- Recommendation: <PROCEED / REPLAN> — <rationale>

## Deliverables

- docs/planning/EPIC_4/SPRINT_26/PATTERN_C_HYPOTHESIS_VALIDATION.md
- (optional) prototype/sprint26-pattern-c-validation branch with
  draft 1-line patch in src/kkt/stationarity.py
- Updated docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md: Unknowns 1.1, 1.2, 1.3, 1.4,
  1.5, 1.6 verified
- Updated docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md: Task 3 status → COMPLETE
- Updated CHANGELOG.md with Task 3 completion entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint26-task3
gh pr create --title "Complete Sprint 26 Prep Task 3: Pattern C Hypothesis Validation (PR16)" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] [Quality gate applicability — docs-only OR prototype-patch-with-quality-gate]
- [x] Day 5 methodology applied to 3 target models
- [x] Hand-derived formal KKT documented for at least 1 stationarity equation per model
- [x] Byte-comparison vs emitted form documented per model
- [x] Tier 0/1 canary regression test executed and results recorded
- [x] PROCEED / REPLAN recommendation documented with rationale
- [x] Unknowns 1.1, 1.2, 1.3, 1.4, 1.5, 1.6 verified in KNOWN_UNKNOWNS.md
- [x] Task 3 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 4 Prompt: Pattern A Cohort Reclassification Pre-Work

**Branch:** Create a new branch named `planning/sprint26-task4` from `main`

**Priority:** High (3–4 hours)

**Objective:** For each of the 6 Pattern A cohort issues (#1138, #1139, #1140, #1142, #1145, #1150), produce a per-issue action plan: **subsume** into existing tracker (e.g., #1334) / **close as duplicate** of new Priority 1 work / **close-and-refile** under correct shape / **investigate further** (Sprint 27).

**Unknowns Verified:** 2.1, 2.2, 2.3, 2.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 4
- `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` §Category 2 (Unknowns 2.1–2.4)
- `docs/planning/EPIC_4/SPRINT_25/DAY7_COHORT_SWEEP.md` §"Classification Table"
- `docs/planning/EPIC_4/SPRINT_25/AUDIT_ALIAS_AD_CARRYFORWARD.md` (original Pattern A/B/C/D/E classification)
- GitHub issues: #1138, #1139, #1140, #1142, #1145, #1150
- Sprint 25 Day 11 SPRINT_LOG entry (fix-in-place series #1338..#1352 may have side-effect-fixed some cohort issues)

**Tasks to Complete:**

1. **Per-issue current state** — `gh issue view #NNNN` for each of the 6 cohort issues; confirm OPEN with `sprint-26` label.
2. **Per-issue fingerprint re-verification** — translate + emit each canonical model on current main and grep for the documented bug fingerprint; determine if Sprint 25 fix-in-place series side-effect-fixed any issue.
3. **Per-issue action note** — write classification + action + (if "close-and-refile") draft new-issue title + body.
4. **Cross-reference test xfails** — `grep -rE "#(1138|1139|1140|1142|1145|1150)" tests/` to identify any test xfails or docstrings depending on these issue numbers.
5. **Cross-reference src/ + docs/ stale references** — recursive grep for issue-number references that need updating when closing each issue.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_26/PATTERN_A_RECLASSIFICATION_PLAN.md` with per-issue action plan (one section per issue)
- Test/source/docs cross-reference scan results (which references need updating per issue)
- Updated `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` Unknowns 2.1, 2.2, 2.3, 2.4 with verification results

**Known Unknowns Updates:**

For each of Unknowns 2.1, 2.2, 2.3, 2.4 in `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md`, update Verification Results:

- Status: ✅ VERIFIED or ❌ WRONG
- Verified by: Task 4 (Pattern A Cohort Reclassification Pre-Work)
- Date: today's date
- Findings: per-issue classification accuracy, action notes, cross-reference scan results
- Evidence: `gh issue view` outputs, fingerprint grep results, test/source xref output
- Decision: per-issue action committed; Sprint 26 Priority 2 budget refined

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 4:

- Status → ✅ COMPLETE
- Fill "Changes" and "Result" sections (with per-issue action distribution)
- Check off all Acceptance Criteria

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 26 Preparation`, prepend:

```markdown
- **Prep Task 4 COMPLETE (YYYY-MM-DD):** Pattern A cohort reclassification pre-work. Per-issue action plan for the 6 cohort issues (#1138 → <action>; #1139 → <action>; #1140 → <action>; #1142 → <action>; #1145 → <action>; #1150 → <action>). Test xfail scan: <N> affected tests. Sprint 26 Priority 2 effort refined to <X>h. Verified Unknowns 2.1, 2.2, 2.3, 2.4.
```

**Quality Gate:**

Task 4 is docs-only. No `.py` modified. **Skip the Python quality gate.** If you touched any `.py` file unexpectedly:

```bash
make typecheck && make lint && make format && make test
```

**Commit Message Format:**

```
Complete Sprint 26 Prep Task 4: Pattern A Cohort Reclassification Pre-Work

Per-issue action plan for the 6 Pattern A cohort issues based on the
Sprint 25 Day 7 cohort sweep (re-verified post Sprint 25 fix-in-place
series). Sprint 26 Priority 2 execution becomes mechanical
close-and-refile work rather than investigative.

## Key findings

- #1138: <action> — <evidence>
- #1139: <action> — <evidence>
- #1140: <action> — <evidence>
- #1142: <action> — <evidence>
- #1145: <action> — <evidence>
- #1150: <action> — <evidence>
- Test xfails referencing these issues: <N>
- Source/docs references requiring update: <N>

## Deliverables

- docs/planning/EPIC_4/SPRINT_26/PATTERN_A_RECLASSIFICATION_PLAN.md
- Updated docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md: Unknowns 2.1, 2.2, 2.3, 2.4
  verified
- Updated docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md: Task 4 status → COMPLETE
- Updated CHANGELOG.md with Task 4 completion entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint26-task4
gh pr create --title "Complete Sprint 26 Prep Task 4: Pattern A Cohort Reclassification Pre-Work" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] No Python source code modified — quality gate skipped per workflow rules
- [x] All 6 cohort issues have per-issue action notes
- [x] Test xfail cross-reference scan documented
- [x] Unknowns 2.1, 2.2, 2.3, 2.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 4 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 5 Prompt: Pattern E Carryforward Status Survey

**Branch:** Create a new branch named `planning/sprint26-task5` from `main`

**Priority:** High (2–3 hours)

**Objective:** Re-verify the 3 Pattern E carryforward issues (#1141 kand, #1144 catmix, #1147 camshape) under the post-Sprint-25 emit pipeline. Some may have shifted bucket via the Sprint 25 fix-in-place series #1338..#1352 (in particular catmix was on the SetMembershipTest fix list #1338 and may have been recovered).

**Unknowns Verified:** 3.1, 3.2, 3.3

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 5
- `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` §Category 3 (Unknowns 3.1, 3.2, 3.3)
- `docs/planning/EPIC_4/SPRINT_25/SPRINT_LOG.md` Day 11 entry (fix-in-place series #1338..#1352)
- `docs/planning/EPIC_4/SPRINT_25/DAY7_COHORT_SWEEP.md` (Phase E classification basis)
- `docs/planning/EPIC_4/SPRINT_25/DESIGN_ALIAS_AD_ROLLOUT.md` §Phase 4 (Phase E framing)
- GitHub issues: #1141, #1144, #1147

**Tasks to Complete:**

1. **Per-issue current state** — `gh issue view` for each of #1141, #1144, #1147; confirm OPEN, `sprint-26` label.
2. **Per-issue translate + compile-only check** on current main:
   ```bash
   mkdir -p /tmp/sprint26-pattern-e
   for m in kand catmix camshape; do
     .venv/bin/python -m src.cli data/gamslib/raw/${m}.gms \
       -o /tmp/sprint26-pattern-e/${m}_mcp.gms --skip-convexity-check --quiet
     gams /tmp/sprint26-pattern-e/${m}_mcp.gms action=c lo=2 \
       > /tmp/sprint26-pattern-e/${m}_compile.log 2>&1 || true
   done
   ```
3. **Per-model classification** of current bug shape: **Resolved** (model now translates AND solves) / **Bucket shifted** (fails differently — close original + file new) / **Unchanged Pattern E shape** (keep open as Sprint 26 Priority 3 work).
4. **Decide Phase E framing validity** — does the "Pattern E" designation still map cleanly post Sprint 25? Should any of the 3 issues fold into Priority 1 (Pattern C) or Priority 2 (cohort reclassification)?

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md` with per-model status + recommended action
- Updated `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` Unknowns 3.1, 3.2, 3.3 with verification results

**Known Unknowns Updates:**

For each of Unknowns 3.1, 3.2, 3.3 in `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md`, update Verification Results:

- Status: ✅ VERIFIED or ❌ WRONG
- Verified by: Task 5 (Pattern E Carryforward Status Survey)
- Date: today's date
- Findings: per-model classification + bucket-shift decisions
- Evidence: translate output + gams compile logs + emit excerpts
- Decision: Sprint 26 Priority 3 fix scope (which of the 3 actually need fix work)

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 5:

- Status → ✅ COMPLETE
- Fill "Changes" and "Result" sections (per-model status outcome)
- Check off all Acceptance Criteria

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 26 Preparation`, prepend:

```markdown
- **Prep Task 5 COMPLETE (YYYY-MM-DD):** Pattern E carryforward status survey. Per-model status: #1141 (kand) → <Resolved/Shifted/Unchanged>; #1144 (catmix) → <…>; #1147 (camshape) → <…>. Sprint 26 Priority 3 fix scope refined to <N> models (<list>). Verified Unknowns 3.1, 3.2, 3.3.
```

**Quality Gate:**

Task 5 is docs-only. No `.py` modified. **Skip the Python quality gate.**

**Commit Message Format:**

```
Complete Sprint 26 Prep Task 5: Pattern E Carryforward Status Survey

Re-verify the 3 Phase E carryforward issues (#1141, #1144, #1147)
under the post-Sprint-25 emit pipeline. Sprint 25 fix-in-place series
#1338..#1352 may have side-effect-shifted buckets — particularly
catmix (#1144) which was on the #1338 SetMembershipTest fix list.

## Key findings

- #1141 (kand): <classification> — <evidence>
- #1144 (catmix): <classification> — <evidence>
- #1147 (camshape): <classification> — <evidence>
- Sprint 26 Priority 3 fix scope: <N> models actually need fix work

## Deliverables

- docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md
- Updated docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md: Unknowns 3.1, 3.2, 3.3 verified
- Updated docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md: Task 5 status → COMPLETE
- Updated CHANGELOG.md with Task 5 completion entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint26-task5
gh pr create --title "Complete Sprint 26 Prep Task 5: Pattern E Carryforward Status Survey" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] No Python source code modified — quality gate skipped per workflow rules
- [x] All 3 Phase E models re-verified
- [x] Per-model classification (Resolved / Shifted / Unchanged) with evidence
- [x] Sprint 26 Priority 3 fix scope updated
- [x] Unknowns 3.1, 3.2, 3.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 5 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 6 Prompt: Profile Option 1 Short-Circuit Approach

**Branch:** Create a new branch named `planning/sprint26-task6` from `main`

**Priority:** High (3–4 hours)

**Objective:** Verify that the Option 1 short-circuit design from Sprint 25 `PROFILE_HARD_TIMEOUTS.md` is still valid post Sprint 25 #1338..#1341, identify exact `src/ad/index_mapping.py` patch sites, and draft the test fixture plan for srpchase + iswnm.

**Unknowns Verified:** 4.1, 4.2, 4.3, 4.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 6
- `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` §Category 4 (Unknowns 4.1, 4.2, 4.3, 4.4)
- `docs/planning/EPIC_4/SPRINT_25/PROFILE_HARD_TIMEOUTS.md` (the Option 1 design source)
- `docs/issues/ISSUE_1224_mine-paramref-index-offset-unsupported.md`
- Sprint 25 Day 11 SPRINT_LOG entry (#1338..#1341 IndexOffset/SetMembershipTest fixes)

**Tasks to Complete:**

1. **Verify patch sites still exist** in current `src/ad/index_mapping.py` and `src/ir/condition_eval.py`:
   ```bash
   grep -nE "def enumerate_equation_instances|def resolve_set_members" src/ad/index_mapping.py
   grep -nE "SetMembershipTest" src/ir/condition_eval.py | head -10
   ```
2. **Sprint 25 modification history** — `git log --oneline --diff-filter=M -- src/ad/index_mapping.py src/ir/condition_eval.py | head -10`
3. **Re-profile srpchase** under current main with SIGALRM 900s budget to confirm bottleneck shape unchanged.
4. **Re-profile {iswnm, mexls, nebrazil, sarf}** with extended SIGALRM 1800s to identify which (if any) recover under the longer budget — gives projected impact of Option 1.
5. **Draft the patch design** — short-circuit logic + flag/option + interaction with the existing fall-through path. Do NOT implement.
6. **Draft test fixture plan** — unit test for `enumerate_equation_instances` short-circuit + integration test for srpchase translate.
7. **#1224 deferral decision** — read ISSUE_1224 + estimate; decide whether to defer #1224 to Sprint 27+ or attempt narrow mine-specific fix in Sprint 26.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_26/DESIGN_OPTION_1_SHORT_CIRCUIT.md` with design + patch sites + test plan + projected impact
- Updated profile data for srpchase + 4 other timeout models (advisory, captured in design doc)
- Updated `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` Unknowns 4.1, 4.2, 4.3, 4.4 with verification results

**Known Unknowns Updates:**

For each of Unknowns 4.1, 4.2, 4.3, 4.4 in `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md`, update Verification Results:

- Status: ✅ VERIFIED or ❌ WRONG
- Verified by: Task 6 (Profile Option 1 Short-Circuit Approach)
- Date: today's date
- Findings: patch-site validity, profile re-confirmation, recovery projection per model, #1224 deferral decision, determinism analysis
- Evidence: grep output, profile timing data, ISSUE_1224 effort estimate
- Decision: Sprint 26 Priority 4 budget hold vs grow; #1224 deferred or bundled; determinism guarantees

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 6:

- Status → ✅ COMPLETE
- Fill "Changes" and "Result" sections
- Check off all Acceptance Criteria

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 26 Preparation`, prepend:

```markdown
- **Prep Task 6 COMPLETE (YYYY-MM-DD):** Profiled Option 1 short-circuit approach. Patch sites in `src/ad/index_mapping.py::enumerate_equation_instances` (+ supporting in `resolve_set_members` + `src/ir/condition_eval.py`) confirmed valid post-Sprint-25. srpchase re-profile: <translates / still timeouts> at <X>s. Other timeout models extended-budget recovery: <list>. #1224 deferral decision: <defer to Sprint 27+ / attempt narrow fix in Sprint 26>. Verified Unknowns 4.1, 4.2, 4.3, 4.4.
```

**Quality Gate:**

Task 6 is docs-only (no patch implementation). **Skip the Python quality gate.**

**Commit Message Format:**

```
Complete Sprint 26 Prep Task 6: Profile Option 1 Short-Circuit Approach

Verify Sprint 25 PROFILE_HARD_TIMEOUTS.md Option 1 design still valid
post Sprint 25 #1338..#1341 SetMembershipTest fixes; identify exact
patch sites; project Sprint 26 Priority 4 impact.

## Key findings

- Patch sites valid: <yes / no>
- Sprint 25 modifications to index_mapping.py / condition_eval.py: <list>
- srpchase profile: <translates in <X>s / still timeouts at 900s>
- Extended-budget recovery (1800s): <list of recovered models>
- Projected Sprint 26 Translate gain: <+1 / +2 / +3>
- #1224 (mine ParamRef IndexOffset): <defer to Sprint 27 / narrow Sprint 26 fix feasible>
- Determinism: short-circuit produces deterministic output (verified via PR12 harness)

## Deliverables

- docs/planning/EPIC_4/SPRINT_26/DESIGN_OPTION_1_SHORT_CIRCUIT.md
- Updated docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md: Unknowns 4.1, 4.2, 4.3, 4.4 verified
- Updated docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md: Task 6 status → COMPLETE
- Updated CHANGELOG.md with Task 6 completion entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint26-task6
gh pr create --title "Complete Sprint 26 Prep Task 6: Profile Option 1 Short-Circuit Approach" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] No Python source code modified — quality gate skipped per workflow rules
- [x] Patch sites verified to still exist in current src/
- [x] srpchase profile re-confirmed
- [x] Patch design documented (no implementation yet)
- [x] Test fixture plan documented
- [x] Projected impact stated
- [x] Unknowns 4.1, 4.2, 4.3, 4.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 6 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 7 Prompt: AD Residuals (#1334, #1335) Investigation Recap

**Branch:** Create a new branch named `planning/sprint26-task7` from `main`

**Priority:** High (2–3 hours)

**Objective:** Confirm [`docs/issues/completed/ISSUE_1334_ad-scalar-constraint-spurious-sum-on-subset-param-domain.md`](../../../issues/completed/ISSUE_1334_ad-scalar-constraint-spurious-sum-on-subset-param-domain.md) and [`docs/issues/ISSUE_1335_ad-missing-zdef-cross-term-time-reversal-index.md`](../../../issues/ISSUE_1335_ad-missing-zdef-cross-term-time-reversal-index.md) are still accurate after Sprint 25 fix-in-place series; verify the otpop NLP-warm-started reproducer; determine whether fixing #1334 actually subsumes #1357 (otpop `$171` from Sprint 25 Day 13) or if they are independent. *(Post-Sprint-26-Day-9 update: #1334 was close-and-refiled to Sprint 27 [#1393](https://github.com/jeffreyhorn/nlp2mcp/issues/1393); see [`docs/issues/ISSUE_1393_ad-scalar-eq-sum-collapse-symbolic-superset.md`](../../../issues/ISSUE_1393_ad-scalar-eq-sum-collapse-symbolic-superset.md) for the active Sprint 27 carryforward.)*

**Unknowns Verified:** 5.1, 5.2, 5.3, 5.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 7
- `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` §Category 5 (Unknowns 5.1, 5.2, 5.3, 5.4)
- `docs/issues/completed/ISSUE_1334_ad-scalar-constraint-spurious-sum-on-subset-param-domain.md`
- `docs/issues/ISSUE_1335_ad-missing-zdef-cross-term-time-reversal-index.md`
- `docs/issues/ISSUE_1357_otpop-stationarity-domain-violations-171.md`
- Sprint 25 Day 11 SPRINT_LOG entry (#1350 srkandw `tn(t,t)` self-alias touched stationarity.py)

**Tasks to Complete:**

1. **Re-read [`docs/issues/completed/ISSUE_1334_ad-scalar-constraint-spurious-sum-on-subset-param-domain.md`](../../../issues/completed/ISSUE_1334_ad-scalar-constraint-spurious-sum-on-subset-param-domain.md) and [`docs/issues/ISSUE_1335_ad-missing-zdef-cross-term-time-reversal-index.md`](../../../issues/ISSUE_1335_ad-missing-zdef-cross-term-time-reversal-index.md)** — confirm file:line references match current `src/kkt/stationarity.py` (note: #1334 is now in `completed/` after Sprint 26 Day 9 close-and-refile to Sprint 27 [#1393](https://github.com/jeffreyhorn/nlp2mcp/issues/1393); #1335 remains in `docs/issues/` as a Sprint 27 in-place carryforward post Day 9 rollback):
   ```bash
   grep -nE "^def _replace_indices_in_expr|^def _add_jacobian_transpose_terms_scalar" \
     src/kkt/stationarity.py
   ```
2. **Re-run otpop NLP-warm-started reproducer:** translate otpop, run NLP solve in GAMS, transfer duals, run MCP `iterlim=0`, capture per-equation residuals (specifically `stat_cd(ag-subsist)`).
3. **#1334 ↔ #1357 subsumption decision** — re-emit otpop and compare `$171` violation lines (217, 247) to the `_replace_indices_in_expr` ParamRef-substitution pattern documented in ISSUE_1334.md §Buggy Emit. If patterns match: #1334 subsumes #1357. If not: #1357 is independent.
4. **#1335 tractability assessment** — read ISSUE_1335; determine if it's a narrow Sprint-26-level fix or requires architectural change.
5. **Per-issue Sprint 26 work plan** — for each of #1334, #1335: prerequisite verification + fix approach + acceptance criteria.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_26/AD_RESIDUALS_RECAP.md` with #1334 / #1335 / #1357 relationship analysis
- (If file:line references are stale) updates to ISSUE_1334.md / ISSUE_1335.md
- Updated `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` Unknowns 5.1, 5.2, 5.3, 5.4 with verification results

**Known Unknowns Updates:**

For each of Unknowns 5.1, 5.2, 5.3, 5.4 in `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md`, update Verification Results:

- Status: ✅ VERIFIED or ❌ WRONG
- Verified by: Task 7 (AD Residuals Investigation Recap)
- Date: today's date
- Findings: file:line currency, otpop reproducer outcome, #1334 ↔ #1357 subsumption decision, #1335 tractability
- Evidence: grep output, otpop solve log + per-equation residuals, fingerprint comparison
- Decision: Sprint 26 Priority 5 fix scope clarified (do #1334 + #1335 alone close #1357?)

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 7:

- Status → ✅ COMPLETE
- Fill "Changes" and "Result" sections
- Check off all Acceptance Criteria

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 26 Preparation`, prepend:

```markdown
- **Prep Task 7 COMPLETE (YYYY-MM-DD):** AD residuals (#1334, #1335) investigation recap. ISSUE_1334.md / ISSUE_1335.md file:line references <accurate / updated>. otpop NLP-warm-started reproducer: `stat_cd(ag-subsist)` LHS = <X>. #1334 ↔ #1357 subsumption: <CONFIRMED / INDEPENDENT> based on <evidence>. #1335 tractability: <narrow Sprint 26 fix / requires architectural change>. Verified Unknowns 5.1, 5.2, 5.3, 5.4.
```

**Quality Gate:**

Task 7 is docs-only. **Skip the Python quality gate.**

**Commit Message Format:**

```
Complete Sprint 26 Prep Task 7: AD Residuals (#1334, #1335) Investigation Recap

Confirm ISSUE_1334.md / ISSUE_1335.md accuracy post Sprint 25
fix-in-place series; verify otpop NLP-warm-started reproducer;
determine #1334 ↔ #1357 subsumption.

## Key findings

- ISSUE_1334.md file:line references: <accurate / updated to current>
- ISSUE_1335.md file:line references: <accurate / updated to current>
- otpop reproducer: stat_cd(ag-subsist) LHS = <X> (documented: -1.4157)
- stat_x('1990') residual: <X>; stat_p('1986') residual: <X>
- #1334 ↔ #1357 subsumption: <CONFIRMED / INDEPENDENT> — <evidence>
- #1335 tractability: <narrow / architectural>
- Sprint 26 Priority 5 scope: <#1334 + #1335 alone close #1357 / 3 issues to fix>

## Deliverables

- docs/planning/EPIC_4/SPRINT_26/AD_RESIDUALS_RECAP.md
- (optional) Updates to ISSUE_1334.md / ISSUE_1335.md if file:line stale
- Updated docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md: Unknowns 5.1, 5.2, 5.3, 5.4 verified
- Updated docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md: Task 7 status → COMPLETE
- Updated CHANGELOG.md with Task 7 completion entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint26-task7
gh pr create --title "Complete Sprint 26 Prep Task 7: AD Residuals (#1334, #1335) Investigation Recap" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] No Python source code modified — quality gate skipped per workflow rules
- [x] ISSUE_1334.md and ISSUE_1335.md verified accurate (or updated)
- [x] otpop reproducer re-run; current residual documented
- [x] #1334 ↔ #1357 subsumption decision made with evidence
- [x] Sprint 26 fix scope clarified
- [x] Unknowns 5.1, 5.2, 5.3, 5.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 7 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 8 Prompt: Design Pre-Merge Solve-Time Validation CI (PR19)

**Branch:** Create a new branch named `planning/sprint26-task8` from `main`

**Priority:** High (3–4 hours)

**Objective:** Design the CI extension for emit-affecting changes per Sprint 25 retrospective process recommendation **PR19**. The extension runs a fast-suite `make test` PLUS a 30s PATH solve on a configurable target list when files under `src/emit/` or `src/kkt/stationarity.py` change. Specifically targets the structural-emit-change failure mode that bit Sprint 25's #1308 launch fix.

**Unknowns Verified:** 6.1, 6.2

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 8
- `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` §Unknowns 6.1, 6.2
- `docs/planning/EPIC_4/SPRINT_25/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently" #3 (PR19 origin)
- `.github/workflows/*.yml` (existing CI to extend)
- Sprint 25 Day 11 SPRINT_LOG (#1308 → #1351 launch fix → rollback case study)

**Tasks to Complete:**

1. **Survey existing CI** — `.github/workflows/*.yml` to understand current trigger/job structure.
2. **Decide trigger conditions** — file patterns (`src/emit/*.py`, `src/kkt/stationarity.py`, possibly `src/ad/derivative_rules.py`); PR-only; skippable via `skip-emit-solve-ci` PR label for refactor-only changes.
3. **Decide target model list** — recommended: 4 Pattern C targets (camcge, cesam2, fawley, otpop) + 3 Tier 0 canaries (dispatch, quocge, partssupply). Configurable via `.github/path-solve-ci-targets.txt`.
4. **Decide PATH timeout** — recommended 30s/model. Time the 11 Tier 0/1 canaries locally to confirm the budget.
5. **Decide failure handling** — hard-fail on Tier 0 canary regression; soft-fail on Pattern C target models (informational, expected to fail until Sprint 26 lands the fix). PR comment with per-model status.
6. **Document the design** in `docs/planning/EPIC_4/SPRINT_26/DESIGN_PR19_SOLVE_TIME_CI.md` — includes inline draft workflow YAML.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_26/DESIGN_PR19_SOLVE_TIME_CI.md` with trigger conditions + target list + timeout policy + failure handling + draft workflow YAML
- Target-list file design (`.github/path-solve-ci-targets.txt` format)
- Updated `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` Unknowns 6.1, 6.2 with verification results

**Known Unknowns Updates:**

For each of Unknowns 6.1, 6.2 in `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md`, update Verification Results:

- Status: ✅ VERIFIED or ❌ WRONG
- Verified by: Task 8 (Design Pre-Merge Solve-Time Validation CI PR19)
- Date: today's date
- Findings: per-canary local solve time, CI overhead estimate, target list size selected
- Evidence: timing output, existing CI workflow excerpts, historical PR analysis
- Decision: PR19 design committed (target list + timeout + failure-handling policy)

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 8:

- Status → ✅ COMPLETE
- Fill "Changes" and "Result" sections
- Check off all Acceptance Criteria

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 26 Preparation`, prepend:

```markdown
- **Prep Task 8 COMPLETE (YYYY-MM-DD):** Designed PR19 pre-merge solve-time validation CI extension. Trigger: `src/emit/*.py` + `src/kkt/stationarity.py` + `src/ad/derivative_rules.py` PRs. Target list: <N> models (<list>). Timeout: 30s/model (~<X>min CI overhead). Failure handling: hard-fail on Tier 0 canary regression; soft-fail on Pattern C target models. CI extension implementation lands during Sprint 26 execution. Verified Unknowns 6.1, 6.2.
```

**Quality Gate:**

Task 8 is design-only (no `.github/workflows/` files committed yet — that lands during Sprint 26 execution). **Skip the Python quality gate.**

**Commit Message Format:**

```
Complete Sprint 26 Prep Task 8: Design Pre-Merge Solve-Time Validation CI (PR19)

Sprint 25 retrospective PR19 codification — CI extension that catches
the structural-emit-change failure mode that bit Sprint 25's #1308
launch fix (passed unit + compile-only validation but produced
locally-infeasible MCP at full PATH solve).

## Key findings

- Trigger files: <list>
- PR-label exception: `skip-emit-solve-ci` for refactor-only PRs
- Target model list: <N> models
- PATH timeout: 30s/model
- Estimated CI overhead: ~<X>min on top of make test
- Failure handling: hard-fail on Tier 0 / soft-fail on Pattern C targets
- Per-canary local PATH solve time: <table or summary>

## Deliverables

- docs/planning/EPIC_4/SPRINT_26/DESIGN_PR19_SOLVE_TIME_CI.md
- Updated docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md: Unknowns 6.1, 6.2 verified
- Updated docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md: Task 8 status → COMPLETE
- Updated CHANGELOG.md with Task 8 completion entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint26-task8
gh pr create --title "Complete Sprint 26 Prep Task 8: Design Pre-Merge Solve-Time Validation CI (PR19)" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] No Python source code modified — quality gate skipped per workflow rules
- [x] Trigger file patterns documented
- [x] Target model list committed
- [x] PATH timeout policy documented
- [x] Failure handling policy documented
- [x] CI overhead estimate documented
- [x] Unknowns 6.1, 6.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 8 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 9 Prompt: Bucket-Provenance Baseline + Scope Freeze (PR17 + PR15)

**Branch:** Create a new branch named `planning/sprint26-task9` from `main`

**Priority:** Critical (2–3 hours)

**Objective:** Run a full pipeline baseline per **PR6**, freeze the v2.2.x exclusion set per **PR15**, and add the per-failing-model bucket-provenance column ("Sprint 25 bucket → Sprint 26 bucket") to `BASELINE_METRICS.md` per Sprint 25 retrospective process recommendation **PR17**.

**Unknowns Verified:** 6.3, 6.5 (jointly with Task 2)

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 9
- `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` §Unknowns 6.3, 6.5
- `docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md` (the format Sprint 26 baseline extends)
- `docs/planning/EPIC_4/SPRINT_25/SPRINT_LOG.md` Day 14 entry (per-model transitions table — informal bucket provenance)
- `docs/planning/EPIC_4/SPRINT_25/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently" #2 (PR17 origin) + KU-34 (bucket churn)
- **DEPENDENCY:** Task 2 must be COMPLETE (Sprint 25 scope-shift documented)

**Tasks to Complete:**

1. **Pre-baseline check** — confirm Task 2 is COMPLETE; the baseline write-up depends on accurately documenting the 142 in-scope set.
2. **Run full pipeline baseline:**
   ```bash
   .venv/bin/python scripts/gamslib/run_full_test.py --quiet 2>&1 | tee /tmp/sprint26-baseline.log
   ```
3. **Record headline metrics** — Parse / Translate / Solve / Match + 4 outcome_category counts. Compare against Sprint 25 final to confirm no inadvertent regressions between Sprint 25 close and Sprint 26 Day 0.
4. **Build bucket-provenance table** — for each model in any failure bucket, record: model name, Sprint 25 Day 14 bucket, Sprint 26 Day 0 bucket, transition note (unchanged/changed/new failure/recovered).
5. **Freeze v2.2.x exclusion set** — confirm `data/gamslib/gamslib_status.json` exclusion list unchanged from Sprint 25 final; record SHA / schema version.
6. **Create `docs/planning/EPIC_4/SPRINT_26/BASELINE_METRICS.md`** following Sprint 25 format with the new bucket-provenance column included in §"Failure Composition" sub-table.
7. **Commit `data/gamslib/gamslib_status.json`** if the baseline run produced changes (per Sprint 25 Day 14 prompt convention).

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_26/BASELINE_METRICS.md` with headline metrics + bucket-provenance column
- Updated `data/gamslib/gamslib_status.json` (committed)
- Updated `data/gamslib/mcp/*.gms` artifacts where regenerated (advisory per `BASELINE_METRICS.md` §6)
- Updated `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` Unknowns 6.3, 6.5 with verification results

**Known Unknowns Updates:**

For each of Unknowns 6.3, 6.5 in `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md`, update Verification Results:

- Status: ✅ VERIFIED or ❌ WRONG
- Verified by: Task 9 (Bucket-Provenance Baseline + Scope Freeze PR17 + PR15)
- Date: today's date
- Findings: bucket-provenance column readability assessment + scope-shift policy decision
- Evidence: BASELINE_METRICS.md draft + reader feedback
- Decision: Sprint 26 baseline frozen at <142> in-scope; bucket provenance added; scope-shift policy held

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 9:

- Status → ✅ COMPLETE
- Fill "Changes" and "Result" sections (with headline metrics)
- Check off all Acceptance Criteria

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 26 Preparation`, prepend:

```markdown
- **Prep Task 9 COMPLETE (YYYY-MM-DD):** Bucket-provenance baseline + scope freeze (PR17 + PR15). Sprint 26 Day 0 baseline: Parse <X>/142, Translate <X>/142, Solve <X>, Match <X>. Bucket-provenance column added to BASELINE_METRICS.md §"Failure Composition" — per-failing-model "Sprint 25 → Sprint 26" transition data. Scope frozen at 142 in-scope (v2.2.x exclusion set unchanged). Verified Unknowns 6.3, 6.5.
```

**Quality Gate:**

Task 9 modifies `data/gamslib/gamslib_status.json` and possibly some `data/gamslib/mcp/*.gms` artifacts. No `.py` modified. **Skip the Python quality gate** unless you touched any `.py` file unexpectedly.

**Commit Message Format:**

```
Complete Sprint 26 Prep Task 9: Bucket-Provenance Baseline + Scope Freeze (PR17 + PR15)

Sprint 26 Day 0 baseline per PR6, scope freeze per PR15, with the new
per-failing-model bucket-provenance column per PR17. Resolves Sprint
25 KU-34 (bucket churn dominates path_syntax_error metric).

## Key findings

- Sprint 26 baseline: Parse <X>/142, Translate <X>/142, Solve <X>, Match <X>
- Headline-metric deltas from Sprint 25 final: <list explained deltas if any>
- Bucket-provenance: <N> failing models tracked
- Scope freeze: 142 in-scope; v2.2.x exclusion set unchanged
- Pipeline run duration: <X>s

## Deliverables

- docs/planning/EPIC_4/SPRINT_26/BASELINE_METRICS.md
- Updated data/gamslib/gamslib_status.json (committed)
- Updated docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md: Unknowns 6.3, 6.5 verified
- Updated docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md: Task 9 status → COMPLETE
- Updated CHANGELOG.md with Task 9 completion entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint26-task9
gh pr create --title "Complete Sprint 26 Prep Task 9: Bucket-Provenance Baseline + Scope Freeze (PR17 + PR15)" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] No Python source code modified — quality gate skipped per workflow rules
- [x] Full pipeline baseline run completed (exit 0)
- [x] Headline metrics match Sprint 25 final (or deltas explained)
- [x] Bucket-provenance column added per failing model
- [x] Scope freeze documented
- [x] gamslib_status.json committed
- [x] Unknowns 6.3, 6.5 verified in KNOWN_UNKNOWNS.md
- [x] Task 9 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 10 Prompt: Update CONTRIBUTING.md for Emit-PR `.gms` Diffs (PR14 Reaffirmation)

**Branch:** Create a new branch named `planning/sprint26-task10` from `main`

**Priority:** Medium (1 hour)

**Objective:** Add a hard contributor rule to `CONTRIBUTING.md`: every PR that touches `src/emit/*.py` or `src/kkt/stationarity.py` must include at least one regenerated `.gms` artifact from an affected model in the diff. This is the codified instance of Sprint 25 retrospective **PR14 reaffirmation**.

**Unknowns Verified:** 6.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 10
- `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` §Unknown 6.4
- `docs/planning/EPIC_4/SPRINT_25/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently" #4 (PR14 reaffirmation origin)
- `CONTRIBUTING.md` (the file to update)
- `.github/PULL_REQUEST_TEMPLATE.md` (if exists)
- Sprint 25 PR #1360 review history (the case study — Copilot caught #1349 emit clobber by reading clearlak_mcp.gms)

**Tasks to Complete:**

1. **Read current `CONTRIBUTING.md`** to identify the right section for the new rule (likely §"PR Submission Checklist" or §"Code Changes").
2. **Draft the rule** with: trigger condition (file patterns), regeneration command, reviewer instruction, refactor-only exception via `byte-stable-refactor` PR label.
3. **Add the rule** to the appropriate `CONTRIBUTING.md` section.
4. **Add corresponding entry** to `.github/PULL_REQUEST_TEMPLATE.md` (if it exists) under the PR checklist.
5. **Survey Sprint 24/25 PR titles** for refactor-only candidates to estimate how often the `byte-stable-refactor` exception will be used.

**Deliverables:**

- Updated `CONTRIBUTING.md` with the emit-PR `.gms` artifact rule
- Updated `.github/PULL_REQUEST_TEMPLATE.md` (if it exists)
- Updated `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` Unknown 6.4 with verification results

**Known Unknowns Updates:**

For Unknown 6.4 in `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md`, update Verification Results:

- Status: ✅ VERIFIED or ❌ WRONG
- Verified by: Task 10 (Update CONTRIBUTING.md for Emit-PR `.gms` Diffs PR14 Reaffirmation)
- Date: today's date
- Findings: refactor-only exception count from Sprint 24/25 survey + design decision (label + PR-description requirement)
- Evidence: Sprint 24/25 PR title survey output
- Decision: rule wording committed to CONTRIBUTING.md

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 10:

- Status → ✅ COMPLETE
- Fill "Changes" and "Result" sections
- Check off all Acceptance Criteria

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 26 Preparation`, prepend:

```markdown
- **Prep Task 10 COMPLETE (YYYY-MM-DD):** Updated CONTRIBUTING.md with emit-PR `.gms` artifact rule (PR14 reaffirmation). Hard rule: every PR that touches `src/emit/*.py` or `src/kkt/stationarity.py` MUST include at least one regenerated `.gms` artifact from an affected model in the diff; reviewers MUST read the relevant section. Refactor-only exception via `byte-stable-refactor` PR label + PR description requirement. Verified Unknown 6.4.
```

**Quality Gate:**

Task 10 modifies `CONTRIBUTING.md` (and possibly `.github/PULL_REQUEST_TEMPLATE.md`). No `.py` modified. **Skip the Python quality gate.**

**Commit Message Format:**

```
Complete Sprint 26 Prep Task 10: Update CONTRIBUTING.md for Emit-PR `.gms` Diffs (PR14 Reaffirmation)

Sprint 25 retrospective PR14 reaffirmation — every PR that touches
`src/emit/*.py` or `src/kkt/stationarity.py` must include at least
one regenerated `.gms` artifact from an affected model in the diff.
Mitigates the failure mode where Sprint 25 PR #1349 .l clobber bug
landed and was only caught by Copilot reading clearlak_mcp.gms during
PR #1360 review.

## Key findings

- Refactor-only exception: `byte-stable-refactor` PR label + PR
  description requirement (document byte-diff verification command +
  result)
- Sprint 24/25 PRs that would have used the exception: <N> (per title
  survey)
- Companion CI rule: PR19 (Task 8) — automates a portion but doesn't
  replace human review

## Deliverables

- Updated CONTRIBUTING.md with the emit-PR .gms artifact rule
- Updated .github/PULL_REQUEST_TEMPLATE.md (if exists)
- Updated docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md: Unknown 6.4 verified
- Updated docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md: Task 10 status → COMPLETE
- Updated CHANGELOG.md with Task 10 completion entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint26-task10
gh pr create --title "Complete Sprint 26 Prep Task 10: Update CONTRIBUTING.md for Emit-PR .gms Diffs (PR14 Reaffirmation)" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] No Python source code modified — quality gate skipped per workflow rules
- [x] CONTRIBUTING.md has the new rule with rationale + regeneration command + reviewer instruction
- [x] Refactor-only exception documented
- [x] PULL_REQUEST_TEMPLATE.md updated (if exists)
- [x] Unknown 6.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 10 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 11 Prompt: Plan Sprint 26 Detailed Schedule

**Branch:** Create a new branch named `planning/sprint26-task11` from `main`

**Priority:** Critical (3–4 hours)

**Objective:** Integrate the outputs of all prior prep tasks into a 14-day Sprint 26 execution schedule + per-day execution prompts. The schedule must respect the PROJECT_PLAN.md Sprint 26 entry's ≤ 12 hours/day budget (max 168h total; 50–75h estimated effort with substantial slack).

**Unknowns Verified:** Integrates findings from all prior tasks (Tasks 2–10); does not introduce new unknowns.

**Prerequisites (read before starting — Tasks 2–10 MUST be COMPLETE):**

- `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 11
- `docs/planning/EPIC_4/PROJECT_PLAN.md` Sprint 26 entry (lines 931–1019)
- `docs/planning/EPIC_4/SPRINT_25/PLAN.md` (template — Sprint 25 schedule format)
- `docs/planning/EPIC_4/SPRINT_25/prompts/PLAN_PROMPTS.md` (template — Sprint 25 day-by-day prompts)
- All Sprint 26 prep outputs from Tasks 2–10:
  - `docs/planning/EPIC_4/SPRINT_26/PATTERN_C_HYPOTHESIS_VALIDATION.md` (Task 3 — most important, dictates Day 1 PROCEED/REPLAN)
  - `docs/planning/EPIC_4/SPRINT_26/PATTERN_A_RECLASSIFICATION_PLAN.md` (Task 4)
  - `docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md` (Task 5)
  - `docs/planning/EPIC_4/SPRINT_26/DESIGN_OPTION_1_SHORT_CIRCUIT.md` (Task 6)
  - `docs/planning/EPIC_4/SPRINT_26/AD_RESIDUALS_RECAP.md` (Task 7)
  - `docs/planning/EPIC_4/SPRINT_26/DESIGN_PR19_SOLVE_TIME_CI.md` (Task 8)
  - `docs/planning/EPIC_4/SPRINT_26/BASELINE_METRICS.md` (Task 9)
  - Updated CONTRIBUTING.md (Task 10)

**Tasks to Complete:**

1. **Draft Sprint 26 schedule** at `docs/planning/EPIC_4/SPRINT_26/PLAN.md`:
   - **Day 0:** Prep-task review, sprint kickoff, baseline snapshot, branch setup
   - **Days 1–3:** Priority 1 Pattern C generalization (per Task 3 PROCEED-or-REPLAN recommendation; if PROCEED, the prototype patch from Task 3 lands here)
   - **Day 4:** Priority 1 wrap-up + initial canary regression test under PR19 CI
   - **Day 5:** Checkpoint 1 (Priority 1 lands; +3 to +5 path_syntax_error → solve evidence)
   - **Days 6–7:** Priority 2 Pattern A reclassification (per Task 4 action plan — should be mechanical close-and-refile work)
   - **Days 6–7 (parallel):** Priority 3 Pattern E carryforward (per Task 5 status survey)
   - **Days 8–9:** Priority 4 Translation timeout Option 1 short-circuit (per Task 6 design)
   - **Days 8–10 (parallel):** Priority 5 AD residuals #1334 + #1335 (per Task 7 recap)
   - **Day 10:** Checkpoint 2 (all 5 priorities landing or scoped)
   - **Day 11:** Process recs PR17 (bucket provenance baseline already from Task 9; refresh with mid-sprint findings) + PR19 CI extension landing
   - **Day 12:** Buffer / overflow / emit artifact review pass (PR14 reaffirmation)
   - **Day 13:** Final pipeline retest + metric capture + bucket transition documentation
2. **Write day-by-day execution prompts** at `docs/planning/EPIC_4/SPRINT_26/prompts/PLAN_PROMPTS.md` (mirror Sprint 25's PLAN_PROMPTS.md format, adjusted for 14-day cadence).
3. **Define checkpoint evaluation criteria:**
   - Checkpoint 1 (Day 5) GO / CONDITIONAL / NO-GO criteria — Priority 1 landed; ≥3 of 4 Pattern C target models recovered
   - Checkpoint 2 (Day 10) GO / CONDITIONAL / NO-GO criteria — all 5 priorities landed-or-scoped; aggregate Match Δ ≥ +3
4. **Allocate parallel work** — Priority 2 + Priority 3 to Days 6–7 (mechanical reclassification, low compute-time); Priority 4 + Priority 5 to Days 8–10.
5. **Per-day budget check** — confirm no day exceeds 12 hours per the PROJECT_PLAN.md ≤ 12h/day rule. Total ≤ 168h; estimated 50–75h leaves 90+h slack.
6. **Update PREP_PLAN.md summary** with final prep-task status (all 11 tasks marked complete).

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_26/PLAN.md` — 14-day detailed schedule with per-day budget
- `docs/planning/EPIC_4/SPRINT_26/prompts/PLAN_PROMPTS.md` — day-by-day execution prompts (Day 0 + Days 1–13)
- 2 checkpoint evaluation criteria (Day 5 and Day 10)
- Parallel-work allocation across Priorities 2–5
- Updated `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` with final prep-task status (all 11 tasks COMPLETE)

**Known Unknowns Updates:**

Task 11 does not introduce new unknowns. Verify all prior task unknowns (1.1–6.5) are marked ✅ VERIFIED or ❌ WRONG in `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md`. If any are still 🔍 INCOMPLETE, flag and either (a) defer to Sprint 26 Day 0 verification, or (b) block this task pending the prior task's completion.

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 11:

- Status → ✅ COMPLETE
- Fill "Changes" and "Result" sections (sprint schedule highlights)
- Check off all Acceptance Criteria

Update §Summary "Final Prep-Task Status" table — all 11 tasks marked ✅ COMPLETE with date.

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 26 Preparation`, prepend:

```markdown
- **Prep Task 11 COMPLETE (YYYY-MM-DD):** Integrated Tasks 1–10 outputs into a 14-day Sprint 26 execution schedule (`docs/planning/EPIC_4/SPRINT_26/PLAN.md`) + per-day execution prompts (`docs/planning/EPIC_4/SPRINT_26/prompts/PLAN_PROMPTS.md`). 5 priorities allocated across Days 1–10; process recs (PR17/PR19) on Day 11; emit-artifact review pass (PR14) on Day 12; final pipeline retest Day 13. **2 checkpoints:** Checkpoint 1 Day 5 (Priority 1 Pattern C generalization landed; ≥3 of 4 target models recovered); Checkpoint 2 Day 10 (all 5 priorities landed-or-scoped; aggregate Match Δ ≥+3). **Sprint 26 Targets:** Solve ≥108, Match ≥64, path_syntax_error ≤6, Translate ≥135/142. Per-day budget verified ≤12h. **All 11 prep tasks complete; Sprint 26 ready to kick off.**
```

**Quality Gate:**

Task 11 is docs-only. **Skip the Python quality gate.**

**Commit Message Format:**

```
Complete Sprint 26 Prep Task 11: Plan Sprint 26 Detailed Schedule

Integrate Tasks 1–10 outputs into the Sprint 26 14-day execution
schedule + per-day prompts. Sprint 26 ready to kick off.

## Key findings

- Schedule covers Day 0 + Days 1–13 (14 days total)
- 5 priorities + process recs + retest allocated
- 2 checkpoints (Day 5, Day 10) with quantitative GO / NO-GO criteria
- Parallel-work allocation: Priority 2/3 on Days 6-7; Priority 4/5 on Days 8-10
- Per-day budget verified ≤12h (max 168h; estimated 50-75h with 90+h slack)
- All 11 prep tasks complete

## Sprint 26 Targets

- Translate ≥ 135/142 (95%; +2 via Option 1 short-circuit)
- Solve ≥ 108 (+4 via Pattern C generalization)
- Match ≥ 64 (+4 via Pattern C + AD residuals #1334/#1335)
- path_syntax_error ≤ 6 (-6 via Pattern C unblocking)
- path_solve_terminated maintain ≤ 5
- model_infeasible maintain ≤ 4
- Tests ≥ 4,750

## Deliverables

- docs/planning/EPIC_4/SPRINT_26/PLAN.md (14-day schedule)
- docs/planning/EPIC_4/SPRINT_26/prompts/PLAN_PROMPTS.md (day-by-day)
- 2 checkpoint evaluation criteria
- Parallel-work allocation
- Updated docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md: Task 11 status → COMPLETE; Final
  Prep-Task Status table all 11 tasks ✅ COMPLETE
- Updated CHANGELOG.md with Task 11 completion entry + Sprint 26
  ready-to-kick-off marker
```

**Pull Request:**

```bash
git push -u origin planning/sprint26-task11
gh pr create --title "Complete Sprint 26 Prep Task 11: Plan Sprint 26 Detailed Schedule" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] No Python source code modified — quality gate skipped per workflow rules
- [x] Schedule covers all 14 days (Day 0 + Days 1–13)
- [x] No day exceeds 12 hours of estimated work
- [x] Total estimated work ≤ 168h
- [x] 2 checkpoints defined with quantitative GO / NO-GO criteria
- [x] Day-by-day prompts match Sprint 25 format
- [x] Cross-references with all 10 prior prep-task outputs
- [x] Sprint 25 carryforward KUs (KU-33..KU-36) referenced where they drive day-level work
- [x] All 11 prep tasks marked COMPLETE in PREP_PLAN.md Final Prep-Task Status table
- [x] Task 11 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Common Workflow Notes

### Branching Convention

All prep task branches: `planning/sprint26-task<N>` from `main`. PRs target `main`.

### Per-Task Execution Workflow

1. **Create branch** `planning/sprint26-task<N>` from `main`.
2. **Read Prerequisites** — every prep task has a list of input docs and code paths to read before starting.
3. **Execute the task** — perform the research / analysis / design work in the order listed in "Tasks to Complete".
4. **Update KNOWN_UNKNOWNS.md** — replace 🔍 INCOMPLETE → ✅ VERIFIED (or ❌ WRONG with correction) for each assigned unknown, adding Findings / Evidence / Decision.
5. **Update PREP_PLAN.md** — mark the task's Status → ✅ COMPLETE; fill Changes / Result; check off every Acceptance Criterion (`- [ ]` → `- [x]`).
6. **Update CHANGELOG.md** — prepend a Sprint 26 Preparation bullet under `[Unreleased]`.
7. **Run quality gate if any `.py` file changed:** `make typecheck && make lint && make format && make test`. All four must succeed.
8. **Commit** with the commit message format specified in the prompt.
9. **Push** the branch: `git push -u origin planning/sprint26-task<N>`.
10. **Open PR** via `gh pr create` with the specified title + body.
11. **Wait for reviewer comments.** Do not proceed to the next task until this PR is merged.

### Determining "Unknown VERIFIED" vs "WRONG"

- ✅ **VERIFIED** means the assumption stated in the Unknown section was confirmed by the research. Cite specific evidence (file paths, output, test results).
- ❌ **WRONG** means the assumption was contradicted. Document the correct finding and explain the impact on sprint planning. Revise Task 11's schedule if the correction affects effort estimates.

### Verification Section Template

When updating a Verification Results subsection in KNOWN_UNKNOWNS.md:

```markdown
### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task <N> (<Task Name>)
**Date:** YYYY-MM-DD

**Findings:**
- [Finding 1]
- [Finding 2]

**Evidence:**
- [Specific file/line/issue reference]
- [Specific output or test result]

**Decision:**
- [What this means for Sprint 26 plan]
```

### Commit Message Conventions

- Every task's commit message starts with `Complete Sprint 26 Prep Task <N>: <Task Name>`.
- Body includes a `## Key findings` section with bulleted outcomes.
- Body includes a `## Deliverables` section listing every updated file.
- No `Co-Authored-By` lines.
- No "Generated with Claude Code" attribution in commit body OR PR description.

### Quality Gate Pass Criteria

Run these in order and proceed only if all succeed:

```bash
make typecheck    # mypy on src/
make lint         # ruff check src/ tests/
make format       # black check src/ tests/
make test         # full fast suite, pytest -n auto -m "not slow"
```

If the task is docs-only (no `.py` changes), skip the quality gate but note this in the PR description.

### Pull Request Body Template

```markdown
## Summary

[1-3 sentences describing what this PR does and which Sprint 26 prep task it completes]

## Key findings

[Bulleted list from the commit message body]

## Deliverables

- [New file path 1]
- [New file path 2]
- Updated `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md`: Unknowns X.Y, X.Z verified
- Updated `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md`: Task <N> status → COMPLETE
- Updated `CHANGELOG.md` with Task <N> completion entry

## Test plan

- [x] [Quality-gate applicability: run all 4 OR docs-only skip]
- [x] Unknowns X.Y, X.Z verified in KNOWN_UNKNOWNS.md
- [x] Task <N> Acceptance Criteria all checked in PREP_PLAN.md
- [x] [Task-specific verification bullets — e.g., "All 4 target models classified"]
```

### After PR Merges

When the user confirms the PR has merged:

1. `git checkout main && git pull` to sync local main.
2. Verify the merged commit is in main: `git log --oneline -3`.
3. Ready to pick up the next task prompt.

---

**Document Created:** 2026-05-07
**Prompts Covered:** Task 2 through Task 11 (10 prompts)
**Dependency Ordering:**

- Kickoff-parallel (no deps beyond Task 1): Tasks 2, 3, 4, 5, 6, 7, 8, 10
- Depends on Task 2: Task 9 (needs scope-shift documentation before recording the Sprint 26 baseline)
- Depends on all (final integration): Task 11

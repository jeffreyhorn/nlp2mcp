# Sprint 32 Prep Task Execution Prompts

Self-contained prompts for Sprint 32 Prep Tasks 2–11. Each prompt can be copy-pasted into a new conversation to execute one prep task end-to-end, including the Known Unknowns updates, PREP_PLAN.md / CHANGELOG.md updates, quality gate, commit, and PR.

**Usage:**

1. Pick a task prompt below.
2. Paste it into a new conversation.
3. The agent creates the branch (`planning/sprint32-task<N>`), does the work, runs the quality gate, commits, pushes, and opens a PR.
4. Wait for reviewer comments on the PR.

Task 1 (Create Sprint 32 Known Unknowns List) is already ✅ COMPLETE — no prompt needed.

Tasks 2–11 are dispatchable in the following order per the Prep Task Overview table (Dependencies column) + the Critical/Secondary/Tertiary/Quaternary Path notes in `docs/planning/EPIC_4/SPRINT_32/PREP_PLAN.md` (Task 1 is done, so the tasks that depend only on it — or on nothing — are immediately dispatchable):

- **Immediately dispatchable:** Task 2 (no dependencies), Task 5 + Task 6 + Task 7 (need only the completed Task 1)
- **After Task 2:** Task 3 (the mine bound-multiplier design reuses the Day-0 baseline / mine bucket) + Task 4 (the sarf sparsification design reuses the sarf bucket)
- **After Tasks 1 + 3 + 4 + 5:** Task 8 (the Phase-0 gate refresh consumes the three deep-track design docs)
- **After Tasks 1 + 8:** Task 10 (the tooling-readiness + backlog analysis reuses the gates)
- **After Tasks 3 + 4 + 5 + 8:** Task 9 (the REPLAN assessment consumes the designs + the gates)
- **After all (final integration):** Task 11

**Critical path:** Task 1 → Task 3 → Task 8 → Task 9 → Task 11.

**Cross-cutting conventions for every prompt below:**

- Branch from `main`; PR targets `main`. Branch name: `planning/sprint32-task<N>`.
- User preferences (enforce in every commit/PR): **NO `Co-Authored-By` lines** in commit messages; **NO "Generated with Claude Code"** in PR descriptions.
- Replace `YYYY-MM-DD` with the actual date at execution time.
- These are **docs/design/analysis-only** prep tasks — no Python source changes are expected (the fixes/scripts they design are *built in-sprint*, not in prep; the KKT-residual harness, presolve-divergence detector, golden-staleness gate, `--resolve-changed` mode, and the `--force` scaffold already exist on `main`). Run the full quality gate before committing regardless; if you did touch Python, it must pass.
- **PR24 discipline:** every pinned Sprint-31 root cause is a Day-0-re-confirm *hypothesis*, never fact (Sprint 31 REPLAN'd all five deep tracks after a control or harness re-diagnosis refuted the original premise — the mine "MS-1 17500" measurement error, the camcge CASE_B-not-Walras verdict, the sarf 369K-not-1,152 finding, the P5 inert-reduction control, the rocket exhausted-lever survey). Record the symptom + reproducer; frame the fix surface as a hypothesis to re-trace, and gate any high-blast-radius change on a control experiment.
- **Assert `modelstat` before reading an objective** (the Sprint-31 Day-2 measurement-error lesson: relaxing `x.up=inf` produced 34 unmatched-variable errors, so the "MS-1 17500" was the embedded LP, not the MCP). Any warm/cold solve experiment asserts `mcp_model.modelstat` before any objective read.
- **Check the dual side** (the Sprint-30 camcge lesson): any structural transform that drops/adds rows must be verified against the KKT *dual*, not just the primal solution set.
- Every Known-Unknowns update uses the verification block: **Status** (✅ VERIFIED / ❌ WRONG), **Verified by**, **Date**, **Findings**, **Evidence**, **Decision**.

---

## Task 2 Prompt: Sprint 31 → Sprint 32 Day-0 Baseline + Genuine-Floor Re-Baseline (PR15 + PR17 + PR25)

**Branch:** Create a new branch named `planning/sprint32-task2` from `main`

**Priority:** Critical (3–4 hours)

**Objective:** Establish the authoritative Sprint 32 Day-0 baseline — the per-model bucket provenance (Parse / Translate / Solve / Match / model_infeasible / path_*) carried forward from the Sprint 31 final retest — and re-run the PR25 genuine-vs-methodology re-baseline so the genuine-floor ramp (74 → ≥ 75) is measured against a clean starting line, not the methodology-inflated Match figure. Crucially, record the **142-corpus vs all-219** distinction the Sprint-31 closeout pinned (headline Match 92 is over the 142 convex candidates; the +3 ps2/ps3 gains land on non-candidate `non_convex` models → all-219 tally 95).

**Unknowns Verified:** 7.2 (and contributes the per-target Day-0 bucket to 1.1 / 2.1 / 3.1 baselines; pins the Sprint-31-final SHA that anchors 7.3)

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_32/PREP_PLAN.md` §Task 2
- `docs/planning/EPIC_4/SPRINT_32/KNOWN_UNKNOWNS.md` §Unknown 7.2 + the Category 1/2/3 per-target unknowns
- `docs/planning/EPIC_4/SPRINT_31/BASELINE_METRICS.md` (the bucket-provenance + genuine-vs-methodology template + the §5 Day-13 142-corpus vs all-219 recompute) + `docs/planning/EPIC_4/SPRINT_31/SPRINT_RETROSPECTIVE.md` §1 (the final metrics table: Solve 107 / Match 92 / genuine floor 74 / model_infeasible 7 / Translate 135 / Tests 5,074 / all-219 Match 95)
- `data/gamslib/gamslib_status.json` (the Sprint 31 final retest DB — changed at S31 Day 13 with the +3 ps2/ps3 persist) + `scripts/gamslib/run_full_test.py` `--resolve-changed` mode + `get_candidate_models` (the 142-candidate definition = `convexity.status ∈ {verified_convex, likely_convex}`)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 32" (the footnote-⁸ Match re-baseline / genuine-floor ramp S32 ≥ 75)

**Tasks to Complete:**

1. Assert Day-0 = Sprint 31 final — derive the close SHA and diff automatically:
   ```bash
   # Use the OLDEST match (| tail -1) — later commits may quote "SPRINT 31 CLOSED".
   S31=$(git log --grep='SPRINT 31 CLOSED' --format=%H | tail -1)
   git diff --quiet "$S31"..HEAD -- src/ scripts/ && echo "no src/ drift — reuse the committed DB, no fresh ~4h retest" || git diff --stat "$S31"..HEAD -- src/ scripts/
   ```
2. Recompute the canonical bucket tally from the committed DB (`get_candidate_models`, canonical 142): Parse 142 / Translate 135 / Solve 107 / Match 92 / model_infeasible 7. Enumerate the 7 model_infeasible (agreste/camcge/cesam/fawley/lnts/mine/rocket) + the path_syntax_error / path_solve_terminated / path_solve_license members by name.
3. Re-run the PR25 genuine-vs-methodology partition — reproduce the **genuine floor 74** from first principles (S30 70 + P2's +4: polygon + ps2_f_s/ps2_s/ps3_s_gic); record the operational definition (methodology = cold emit byte-identical to pre-fix, matches only via warm-start); identify the Sprint-32 targets that convert to genuine (mine [P1] + camcge [P3] cold-matches) → the "genuine floor → ≥ 75" conversion map + the footnote-⁸ ramp alignment.
4. **Record the 142-corpus vs all-219 distinction** explicitly (the Sprint-31 closeout finding): headline Match 92 over 142 candidates; all-219 tally 95 (+3 non-candidate `non_convex` ps2/ps3). Pin the per-Sprint-32-target Day-0 bucket + projected delta (mine, sarf, camcge, rocket, hhfair + the CGE cluster), each labeled genuine bucket-to-success vs already-banked, with its corpus scope.
5. Pin the Sprint-31-final SHA and confirm `--resolve-changed --since-commit <SHA>` selects the expected changed-emit set (0 at Day 0 = clean baseline).

**Deliverables (from PREP_PLAN.md §Task 2):**

- `docs/planning/EPIC_4/SPRINT_32/BASELINE_METRICS.md` — Day-0 per-model bucket table + the genuine-vs-methodology partition (genuine floor 74) + the 142-corpus vs all-219 scope note + the per-priority target-model list with current buckets
- The pinned Sprint-31-final SHA + confirmation that the `--resolve-changed` checkpoint anchor selects the correct changed-emit set (0 at Day 0)
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknown 7.2
- CHANGELOG.md updated with the Task 2 completion entry

**Known Unknowns Updates:** For Unknown 7.2 in `docs/planning/EPIC_4/SPRINT_32/KNOWN_UNKNOWNS.md`, set the "Verification Results" subsection: **Status** ✅ VERIFIED (or ❌ WRONG + correction), **Verified by** Task 2, **Date**, **Findings** (the genuine-floor-74 reproduction + the footnote-⁸ S32 ≥ 75 ramp alignment + the 142-corpus vs all-219 split), **Evidence** (DB recompute + partition), **Decision** (the ≥ 75 conversion map). Also record the Day-0-bucket aspect of 1.1/2.1/3.1 (their fix-surface aspect is verified by Tasks 3/4/5).

**PREP_PLAN.md Updates:** In §Task 2: `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`; add `**Completed:** YYYY-MM-DD`; fill "Changes" (what was measured/authored) + "Result" (the Day-0 baseline + genuine floor 74 + corpus scope); check off all Acceptance Criteria (`- [ ]` → `- [x]`), including the "Unknowns 7.2 verified" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 32 Prep`, prepend:
```markdown
- **Prep Task 2 COMPLETE (YYYY-MM-DD):** Sprint 32 Day-0 baseline = Sprint 31 final (Solve 107 / Match 92 / genuine floor 74 / model_infeasible 7 / Translate 135 / Tests 5,074 / all-219 Match 95; no fresh retest — no `src/` drift since the S31 close). Genuine floor 74 reproduced from the PR25 partition (polygon + ps2×3) with the → ≥ 75 conversion map (mine P1 / camcge P3) + the footnote-⁸ ramp alignment; the 142-corpus vs all-219 distinction recorded. Per-Sprint-32-target Day-0 bucket + PR25 projection labels; `--resolve-changed` checkpoint anchor pinned (0 at Day 0). Verified Unknown 7.2. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make format && make lint && make test
```
Docs-only task — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 32 Prep Task 2: Day-0 Baseline + Genuine-Floor Re-Baseline

Day-0 = Sprint 31 final (Solve 107 / Match 92 / genuine floor 74 / model_infeasible 7
/ Translate 135 / Tests 5,074 / all-219 Match 95; no fresh retest — no src/ drift since
the S31 close). Genuine floor 74 reproduced from the PR25 partition with the -> >=75
conversion map (mine P1 / camcge P3). 142-corpus vs all-219 distinction recorded.
Sprint-31-final SHA pinned; --resolve-changed checkpoint anchor confirmed (0 at Day 0).

## Deliverables
- docs/planning/EPIC_4/SPRINT_32/BASELINE_METRICS.md
- KNOWN_UNKNOWNS.md: Unknown 7.2 verified
- PREP_PLAN.md: Task 2 -> COMPLETE
- CHANGELOG.md: Task 2 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint32-task2
gh pr create --title "Complete Sprint 32 Prep Task 2: Day-0 Baseline + Genuine-Floor Re-Baseline" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs-only)
- [x] BASELINE_METRICS.md records Day-0 = Sprint 31 final + per-target buckets + the genuine-floor-74 carry-forward + the 142-corpus vs all-219 split
- [x] Day-0 = Sprint 31 final confirmed (git diff empty since the S31 close)
- [x] Unknown 7.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 2 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 3 Prompt: mine 4th Bound-Complementarity Site — Localization + Bound-Multiplier Design (Priority 1 Foundation)

**Branch:** Create a new branch named `planning/sprint32-task3` from `main`

**Priority:** Critical (5–7 hours)

**Objective:** Turn the Sprint-31 Day-3 REPLAN — the residual **4th bound-complementarity site** at bound-active `stat_x` rows — into a concrete **stationarity-consistent bound-multiplier design** that the Sprint-32 P1 implementation follows. Localize the 4th site with the KKT-residual harness on the current tree, and design the derivation that reconciles the LP reduced costs (`x.m` warm-started into `piU_x`) with the emitted `stat_x`, so mine reaches MODEL STATUS 1 (+1 Solve). This is the sprint's deepest track — size it BEFORE the schedule is set.

**Unknowns Verified:** 1.1, 1.2, 1.3, 1.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_32/PREP_PLAN.md` §Task 3
- `docs/planning/EPIC_4/SPRINT_32/KNOWN_UNKNOWNS.md` §Category 1 (Unknowns 1.1–1.4)
- `docs/issues/ISSUE_1443_mine-head-domain-offset-mcp-infeasible.md` (the Day-3 REPLAN block: the residual 4th site; the head-offset IR foundation + Site-2 dual transfer that landed Days 1–2; the cold-INFES-by-direction characterization)
- `scripts/diagnostics/kkt_residual.py` (the harness — the localization tool) + `src/ir/symbols.py` (`EquationDef.head_domain_offsets`) + `src/emit/emit_gams.py` (`head_offset_marginal_index_map`, the Site-2 transfer)
- `docs/planning/EPIC_4/SPRINT_31/SPRINT_LOG.md` Day 2/3 (the measurement-error correction: assert `modelstat`; `x.up=inf` is structurally invalid)

**Tasks to Complete (from PREP_PLAN.md §Task 3 "What Needs to Be Done"):**

1. Reproduce + localize the 4th site: `kkt_residual.py data/gamslib/raw/mine.gms`; confirm the CASE_B `stat_x` residual localizes to the bound-active rows, with the head-offset IR foundation + Site-2 transfer intact.
2. Characterize the bound-dual mismatch: for the bound-active `x` elements, tabulate the LP reduced cost (`x.m`), the emitted `piU_x`/`piL_x`, and the head-offset-coupled `stat_x` residual — showing why the `x.m` transfer does not satisfy `stat_x`.
3. Design the stationarity-consistent bound-multiplier derivation: specify how `piU_x`/`piL_x` should be derived (from the stationarity balance, not the LP reduced cost) at bound-active rows, coupled with the head-offset cross-term; identify the emit site(s) in `src/emit/`/`src/kkt/`.
4. Define the warm→cold residual gate: the design must reduce the warm-start residual to ≈ 0, THEN reach cold MS 1 — **asserting `modelstat` at each step** (the Day-2 lesson). Flag the 5th-coupling REPLAN exit if the bound-dual reconciliation surfaces a deeper IR need.

**Deliverables (from PREP_PLAN.md §Task 3):**

- `docs/planning/EPIC_4/SPRINT_32/MINE_BOUND_MULTIPLIER_DESIGN.md` — the 4th-site localization (harness output), the bound-dual mismatch characterization, the stationarity-consistent bound-multiplier derivation design + emit site(s), the warm→cold residual gate, and the explicit 5th-coupling REPLAN exit
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.1, 1.2, 1.3, 1.4
- CHANGELOG.md updated with the Task 3 completion entry

**Known Unknowns Updates:** For Unknowns 1.1 (bound-multiplier reconciliation), 1.2 (single-4th-site vs 5th-coupling), 1.3 (head-offset-foundation regression guard), 1.4 (`modelstat`-assertion protocol) in `docs/planning/EPIC_4/SPRINT_32/KNOWN_UNKNOWNS.md`, set each "Verification Results": **Status** ✅ VERIFIED / ❌ WRONG, **Verified by** Task 3, **Date**, **Findings**, **Evidence** (the harness output + the mismatch table), **Decision** (PROCEED to the bound-multiplier emit / REPLAN on a 5th coupling).

**PREP_PLAN.md Updates:** In §Task 3: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria (incl. "Unknowns 1.1, 1.2, 1.3, 1.4 verified").

**CHANGELOG.md Update:** Under `### Sprint 32 Prep`, prepend a `**Prep Task 3 COMPLETE (YYYY-MM-DD):**` entry summarizing the 4th-site localization, the bound-multiplier design + emit site, the warm→cold gate, the 5th-coupling REPLAN exit, and "Verified Unknowns 1.1–1.4. Docs/design-only (read-only harness; no `src/`)."

**Quality Gate:**
```bash
make typecheck && make format && make lint && make test
```
Docs/design-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 32 Prep Task 3: mine 4th-Site Localization + Bound-Multiplier Design

Localize the residual 4th bound-complementarity site (CASE_B stat_x at bound-active
rows) via kkt_residual.py; characterize the x.m-vs-piU_x-vs-stat_x mismatch; design
the stationarity-consistent bound-multiplier derivation + emit site. Warm->cold
residual gate defined (modelstat asserted each step); 5th-coupling REPLAN exit explicit.

## Deliverables
- docs/planning/EPIC_4/SPRINT_32/MINE_BOUND_MULTIPLIER_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 1.1-1.4 verified
- PREP_PLAN.md: Task 3 -> COMPLETE
- CHANGELOG.md: Task 3 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint32-task3
gh pr create --title "Complete Sprint 32 Prep Task 3: mine 4th-Site Localization + Bound-Multiplier Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs/design-only)
- [x] MINE_BOUND_MULTIPLIER_DESIGN.md records the 4th-site localization + the mismatch table + the derivation design + the 5th-coupling REPLAN exit
- [x] The head-offset IR foundation regression guard passes (test_head_domain_offsets.py green)
- [x] Unknowns 1.1-1.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 3 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 4 Prompt: sarf 4-D `task`-Variable Stationarity Sparsification Design (Priority 2 Foundation)

**Branch:** Create a new branch named `planning/sprint32-task4` from `main`

**Priority:** High (4–6 hours)

**Objective:** Design the **O(active-instances) symbolic `stat_task` emit** over the `$taskposs`-active subset that makes sarf translate — sparsifying the 369,024-instance 4-D `task(g,t,mn,mn)` variable's stationarity to the active entries (not the full Cartesian product) — coupled with the 2-D dynamic-subset constraint gate (built + reverted in Sprint 31).

**Unknowns Verified:** 2.1, 2.2, 2.3, 2.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_32/PREP_PLAN.md` §Task 4
- `docs/planning/EPIC_4/SPRINT_32/KNOWN_UNKNOWNS.md` §Category 2 (Unknowns 2.1–2.4)
- `docs/issues/ISSUE_1385_option-1-short-circuit-redesign-symbolic-instance-handling.md` (the Day-8 REPLAN: the 369,024-instance 4-D `task` finding; the 2-D gate necessary-but-insufficient; the banked `stat_task` hand-derivation; the atomicity constraint)
- `src/ad/index_mapping.py` (`_is_blowup_2d_condition_equation` — the 2-D gate, built + reverted S31 — + `enumerate_equation_instances`) + `src/kkt/stationarity.py` (the `stat_task` emit site) + commit `243fe578` (the reverted Sprint-26 `nu_slack("srn")` set-name-literal anti-pattern)

**Tasks to Complete (from PREP_PLAN.md §Task 4 "What Needs to Be Done"):**

1. Confirm the 369K figure + the active-subset size: enumerate `task(g,t,mn,mn)` Cartesian instances (16·24·31·31 = 369,024) vs the `$taskposs`-active subset; establish the target O(active) instance count.
2. Design the sparsified `stat_task` emit: specify how the parametric `stat_task` differentiates each short-circuited body once, restricted to the `$taskposs`-active entries, with symbolic (not set-name-literal) multiplier indices; identify the `src/kkt/stationarity.py` + `src/ad/index_mapping.py` sites.
3. Design the 2-D-gate coupling: specify how the re-landed 2-D constraint gate + the 4-D `task` sparsification land **atomically** (re-emit + cross-terms together — the ISSUE_1385 atomicity constraint).
4. Define the O(active) translate-budget gate: time `sarf_mcp.gms` against the translate budget; the design must stay O(active), not re-trigger the Option-1 timeout. Flag the re-scoping REPLAN exit if the parametric emit re-triggers.

**Deliverables (from PREP_PLAN.md §Task 4):**

- `docs/planning/EPIC_4/SPRINT_32/SARF_STAT_TASK_SPARSIFICATION_DESIGN.md` — the 369K vs `$taskposs`-active sizing, the sparsified `stat_task` emit design + sites, the 2-D-gate atomicity coupling, the O(active) translate-budget gate, and the re-scoping REPLAN exit
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 2.1, 2.2, 2.3, 2.4
- CHANGELOG.md updated with the Task 4 completion entry

**Known Unknowns Updates:** For Unknowns 2.1 (O(active) sparsification), 2.2 (2-D-gate atomicity), 2.3 (set-name-literal anti-pattern guard), 2.4 (`$taskposs`-active sizing), set each "Verification Results": **Status**, **Verified by** Task 4, **Date**, **Findings**, **Evidence** (the active-subset count + the design), **Decision** (PROCEED / re-scope REPLAN).

**PREP_PLAN.md Updates:** In §Task 4: Status → ✅ COMPLETE; add `**Completed:**`; fill "Changes" + "Result"; check off all Acceptance Criteria (incl. "Unknowns 2.1, 2.2, 2.3, 2.4 verified").

**CHANGELOG.md Update:** Under `### Sprint 32 Prep`, prepend a `**Prep Task 4 COMPLETE (YYYY-MM-DD):**` entry summarizing the 369K/active sizing, the sparsified `stat_task` design, the atomic coupling, the anti-pattern guard, and "Verified Unknowns 2.1–2.4. Docs/design-only (no `src/`)."

**Quality Gate:**
```bash
make typecheck && make format && make lint && make test
```
Docs/design-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 32 Prep Task 4: sarf 4-D task Stationarity Sparsification Design

Size the 369,024-instance task(g,t,mn,mn) Cartesian vs the $taskposs-active subset;
design the O(active) symbolic stat_task emit (symbolic indices, no set-name literals);
the 2-D-gate + 4-D-sparsification atomic coupling; the O(active) translate-budget gate;
the timeout-re-trigger REPLAN exit.

## Deliverables
- docs/planning/EPIC_4/SPRINT_32/SARF_STAT_TASK_SPARSIFICATION_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 2.1-2.4 verified
- PREP_PLAN.md: Task 4 -> COMPLETE
- CHANGELOG.md: Task 4 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint32-task4
gh pr create --title "Complete Sprint 32 Prep Task 4: sarf 4-D task Stationarity Sparsification Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs/design-only)
- [x] SARF_STAT_TASK_SPARSIFICATION_DESIGN.md records the 369K/active sizing + the sparsified emit + the atomic coupling + the anti-pattern guard + the REPLAN exit
- [x] Unknowns 2.1-2.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 4 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 5 Prompt: camcge `stat_mps` CASE_B + Dual-Consistent Walras Design + Degeneracy-Detector Scope (Priority 3 / Epic 5)

**Branch:** Create a new branch named `planning/sprint32-task5` from `main`

**Priority:** High (4–5 hours)

**Objective:** Design the two-step camcge fix the Sprint-31 CASE_B verdict established — **first** resolve the `stat_mps`/`nu_mps_fx` fixing-multiplier defect, **then** the dual-consistent Walras numéraire (price-pin omega 191.735) — plus the degeneracy-detector scope that must flag only camcge across the CGE cohort. This is an Epic-5-domain design.

**Unknowns Verified:** 3.1, 3.2, 3.3, 3.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_32/PREP_PLAN.md` §Task 5
- `docs/planning/EPIC_4/SPRINT_32/KNOWN_UNKNOWNS.md` §Category 3 (Unknowns 3.1–3.4)
- `docs/issues/ISSUE_1330_camcge-model-infeasible-after-1245.md` (the CASE_B verdict: `stat_mps` rel 1.05, the `nu_mps_fx` fixing-multiplier defect; the price-pin recipe omega 191.735, MS-4; the naive drop-row corrupts to omega 299)
- `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` (the camcge Epic-5 scoping) + `scripts/diagnostics/kkt_residual.py` (the CASE_B localization + the cohort false-positive check)

**Tasks to Complete (from PREP_PLAN.md §Task 5 "What Needs to Be Done"):**

1. Re-confirm the CASE_B `stat_mps` verdict on the current tree: `kkt_residual.py data/gamslib/raw/camcge.gms`; confirm the `stat_mps`/`nu_mps_fx` residual (rel ~1.05) with dual-transfer CONSISTENT.
2. Design the `stat_mps` fixing-multiplier fix: specify how `nu_mps_fx` (the multiplier for the `mps.fx` fixing) should be transferred/emitted so `stat_mps` balances; identify the emit site.
3. Design the dual-consistent Walras numéraire (Epic 5): specify the multiplier redefinition (express the dropped market's dual via Walras' law so it stays in the stationarity) that reaches MS 1 at omega 191.735, **gated on the `stat_mps` fix landing first** — and verify against the KKT **dual**, not just the primal (the "check the dual side" lesson).
4. Scope the degeneracy detector: specify the S1∧S2∧S3 (or equivalent) detector that flags **only** camcge across irscge/lrgcge/moncge/stdcge (no false-positive); define the pass-through default + the per-model-numéraire fallback. Prototype the `stat_mps` fix + dual-consistent redefinition on `/tmp` to MS 1 (asserting `modelstat`) **before** any `src/` change (PR27).

**Deliverables (from PREP_PLAN.md §Task 5):**

- `docs/planning/EPIC_4/SPRINT_32/CAMCGE_STAT_MPS_WALRAS_DESIGN.md` — the CASE_B `stat_mps` re-confirmation, the `nu_mps_fx` fixing-multiplier fix design, the dual-consistent Walras numéraire design (omega 191.735, gated on `stat_mps` first), and the degeneracy-detector scope (flags only camcge; pass-through default; per-model-numéraire fallback)
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 3.1, 3.2, 3.3, 3.4 (+ an `EPIC_5/CGE_DEGENERACY_SCOPING.md` cross-link)
- CHANGELOG.md updated with the Task 5 completion entry

**Known Unknowns Updates:** For Unknowns 3.1 (`stat_mps`-first), 3.2 (dual-consistent Walras MS 1), 3.3 (detector false-positive), 3.4 (automatic-rule-vs-fallback), set each "Verification Results": **Status**, **Verified by** Task 5, **Date**, **Findings**, **Evidence** (the harness verdict + the `/tmp` prototype), **Decision** (PROCEED / Epic-5-deferral).

**PREP_PLAN.md Updates:** In §Task 5: Status → ✅ COMPLETE; add `**Completed:**`; fill "Changes" + "Result"; check off all Acceptance Criteria (incl. "Unknowns 3.1, 3.2, 3.3, 3.4 verified").

**CHANGELOG.md Update:** Under `### Sprint 32 Prep`, prepend a `**Prep Task 5 COMPLETE (YYYY-MM-DD):**` entry summarizing the CASE_B re-confirm, the `stat_mps`-first-then-Walras design, the omega 191.735 target, the detector scope, and "Verified Unknowns 3.1–3.4. Docs/design-only (`/tmp` prototype; no `src/`)."

**Quality Gate:**
```bash
make typecheck && make format && make lint && make test
```
Docs/design-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 32 Prep Task 5: camcge stat_mps CASE_B + Dual-Consistent Walras Design

Re-confirm the CASE_B stat_mps verdict (nu_mps_fx fixing-multiplier defect); design the
stat_mps fix first, then the dual-consistent Walras numeraire (omega 191.735) verified
on the KKT dual side; scope the degeneracy detector to flag ONLY camcge across
irscge/lrgcge/moncge/stdcge; /tmp prototype to MS 1 before src. Epic-5 cross-link.

## Deliverables
- docs/planning/EPIC_4/SPRINT_32/CAMCGE_STAT_MPS_WALRAS_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 3.1-3.4 verified
- PREP_PLAN.md: Task 5 -> COMPLETE
- CHANGELOG.md: Task 5 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint32-task5
gh pr create --title "Complete Sprint 32 Prep Task 5: camcge stat_mps CASE_B + Dual-Consistent Walras Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs/design-only)
- [x] CAMCGE_STAT_MPS_WALRAS_DESIGN.md records the CASE_B re-confirm + the stat_mps-first design + the omega 191.735 target + the detector scope + the fallback
- [x] The degeneracy detector flags ONLY camcge across the CGE cohort (checked)
- [x] Unknowns 3.1-3.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 5 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 6 Prompt: rocket PATH-Consultation Input Packaging + Remaining-Lever Sweep (Priority 4)

**Branch:** Create a new branch named `planning/sprint32-task6` from `main`

**Priority:** Medium (2–3 hours)

**Objective:** Package the finalized **PATH-consultation input** for rocket (the concrete question set + the ruled-out-lever survey) that feeds the renumbered **Sprint 33** PATH consultation, and sweep for any remaining emittable lever the packaging surfaces. Confirm the emit residual is clean at the NLP point (Case-c) so rocket stays a forcing problem, not a latent emit bug.

**Unknowns Verified:** 4.1, 4.2, 4.3

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_32/PREP_PLAN.md` §Task 6
- `docs/planning/EPIC_4/SPRINT_32/KNOWN_UNKNOWNS.md` §Category 4 (Unknowns 4.1–4.3)
- `docs/issues/ISSUE_1462_rocket-fx-multiplier-warmstart-nonconvex.md` (the Day-11 exhausted-lever survey; the `--force` scaffold; the Case-c residual-clean gate)
- `docs/planning/EPIC_4/SPRINT_31/BACKLOG_FIX_SURFACE_ANALYSIS.md` §3 (the PATH-consultation question) + `docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md` §4 (the PATH hand-off draft + INFES 477 → 382) + the `--force {homotopy,multistart,optfile}` scaffold

**Tasks to Complete (from PREP_PLAN.md §Task 6 "What Needs to Be Done"):**

1. Re-confirm the Case-c scope guard: `kkt_residual.py data/gamslib/raw/rocket.gms`; confirm the residual is clean at the NLP point (the Case-c boundary signature per ISSUE_1462), so rocket stays a forcing problem.
2. Assemble the packaged PATH-consultation input: consolidate the ruled-out-lever survey (PATH-option INFES 477→382; continuation/multistart MS-5; the division-by-variable reformulation) into a single concrete question set targeting the intrinsic discretized-optimal-control structure.
3. Sweep for any remaining emittable lever: enumerate any lever the packaging surfaces (scaled/relaxed continuation schedules not yet tried, asserting `modelstat` at each step); note whether a Day-1 attempt is warranted or the hand-off is the deliverable.
4. Draft the Sprint-33 hand-off note: the finalized question + the `--force` scaffold + the ruled-out-lever survey as the de-risked hand-off.

**Deliverables (from PREP_PLAN.md §Task 6):**

- `docs/planning/EPIC_4/SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` — the Case-c scope-guard re-confirmation, the packaged PATH-consultation question set, the ruled-out-lever survey, the remaining-lever sweep result, and the Sprint-33 hand-off note
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 4.1, 4.2, 4.3
- CHANGELOG.md updated with the Task 6 completion entry

**Known Unknowns Updates:** For Unknowns 4.1 (Case-c scope guard), 4.2 (remaining-lever sweep), 4.3 (question concreteness), set each "Verification Results": **Status**, **Verified by** Task 6, **Date**, **Findings**, **Evidence** (the harness verdict + the sweep result), **Decision** (hand-off is the deliverable / conditional +1 Solve).

**PREP_PLAN.md Updates:** In §Task 6: Status → ✅ COMPLETE; add `**Completed:**`; fill "Changes" + "Result"; check off all Acceptance Criteria (incl. "Unknowns 4.1, 4.2, 4.3 verified").

**CHANGELOG.md Update:** Under `### Sprint 32 Prep`, prepend a `**Prep Task 6 COMPLETE (YYYY-MM-DD):**` entry summarizing the Case-c re-confirm, the packaged question set, the ruled-out survey, the Sprint-33 hand-off, and "Verified Unknowns 4.1–4.3. Docs/analysis-only (no `src/`)."

**Quality Gate:**
```bash
make typecheck && make format && make lint && make test
```
Docs/analysis-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 32 Prep Task 6: rocket PATH-Consultation Input Packaging

Re-confirm the Case-c scope guard (residual clean at the NLP point); package the concrete
PATH-consultation question (reformulation ruled out); consolidate the ruled-out-lever
survey (PATH-option 477->382, continuation/multistart MS-5); sweep any remaining lever;
draft the Sprint-33 hand-off note.

## Deliverables
- docs/planning/EPIC_4/SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md
- KNOWN_UNKNOWNS.md: Unknowns 4.1-4.3 verified
- PREP_PLAN.md: Task 6 -> COMPLETE
- CHANGELOG.md: Task 6 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint32-task6
gh pr create --title "Complete Sprint 32 Prep Task 6: rocket PATH-Consultation Input Packaging" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs/analysis-only)
- [x] ROCKET_PATH_CONSULTATION_INPUT.md records the Case-c re-confirm + the packaged question + the ruled-out survey + the Sprint-33 hand-off
- [x] Unknowns 4.1-4.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 6 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 7 Prompt: hhfair + CGE Cluster Case-c Formalization + Harness Classifier Design (Priority 5)

**Branch:** Create a new branch named `planning/sprint32-task7` from `main`

**Priority:** Medium (2–3 hours)

**Objective:** Design the `kkt_residual.py` **Case-c auto-classifier extension** for the objective-defining-intermediate-variable family (hhfair `stat_u` / CGE `stat_xp`) and the ISSUE-closure criteria, so Sprint 32 can formally close hhfair + the CGE cluster as documented genuine non-convex Case-c (no emit fix expected). **The sign flip is BANNED** (control-refuted 4× across S30–S31).

**Unknowns Verified:** 5.1, 5.2, 5.3, 5.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_32/PREP_PLAN.md` §Task 7
- `docs/planning/EPIC_4/SPRINT_32/KNOWN_UNKNOWNS.md` §Category 5 (Unknowns 5.1–5.4)
- `docs/issues/ISSUE_1236_hhfair-objective-mismatch.md` (the Day-10 Case-c control-refutation: the ν_objective reduction is inert; the CGE cluster cold `UU=25.5085` for both sign choices; the sign flip BANNED; the objective-defining-intermediate-variable family definition)
- `scripts/diagnostics/kkt_residual.py` (the Case-a/b/c verdict logic to extend)

**Tasks to Complete (from PREP_PLAN.md §Task 7 "What Needs to Be Done"):**

1. Specify the Case-c discriminator: define the objective-defining-intermediate-variable shape precisely (variable appears only in the objective defining equation `obj =e= f(x)` AND is market-cleared; cold solve reaches a spurious local KKT point; presolve warm-start reaches the match).
2. Design the `kkt_residual.py` classifier extension: specify how the harness auto-flags the family as Case-c (non-convex, presolve-required) vs a fixable Case-b, without false-positives.
3. Define the ISSUE-closure criteria: what "documented Case-c" means for closure (hhfair + irscge/lrgcge/moncge): the classifier flags them, the sign flip is recorded BANNED, and they are handed to the Sprint-33 forcing/PATH work.
4. Re-confirm the sign-flip ban: note the control-refutation history (4× S30–S31) so no Day-1 sign-flip attempt is made. Re-confirm all four members are genuine Case-c (cold-solve each asserting `modelstat`: cold ≠ match, presolve-match).

**Deliverables (from PREP_PLAN.md §Task 7):**

- `docs/planning/EPIC_4/SPRINT_32/CASE_C_CLASSIFIER_DESIGN.md` — the Case-c discriminator spec, the `kkt_residual.py` classifier-extension design, the ISSUE-closure criteria, and the sign-flip-ban re-confirmation
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 5.1, 5.2, 5.3, 5.4
- CHANGELOG.md updated with the Task 7 completion entry

**Known Unknowns Updates:** For Unknowns 5.1 (classifier discriminator), 5.2 (sign-flip ban), 5.3 (all-members-Case-c), 5.4 (closure criteria), set each "Verification Results": **Status**, **Verified by** Task 7, **Date**, **Findings**, **Evidence** (the discriminator + the cold/presolve re-confirmation), **Decision** (formalize Case-c / carve out a fixable member).

**PREP_PLAN.md Updates:** In §Task 7: Status → ✅ COMPLETE; add `**Completed:**`; fill "Changes" + "Result"; check off all Acceptance Criteria (incl. "Unknowns 5.1, 5.2, 5.3, 5.4 verified").

**CHANGELOG.md Update:** Under `### Sprint 32 Prep`, prepend a `**Prep Task 7 COMPLETE (YYYY-MM-DD):**` entry summarizing the Case-c discriminator, the classifier-extension design, the closure criteria, the sign-flip ban, and "Verified Unknowns 5.1–5.4. Docs/design-only (no `src/`)."

**Quality Gate:**
```bash
make typecheck && make format && make lint && make test
```
Docs/design-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 32 Prep Task 7: hhfair + CGE Cluster Case-c Formalization Design

Specify the objective-defining-intermediate-variable Case-c discriminator; design the
kkt_residual.py classifier extension (no false-positive on Case-b); define the ISSUE-
closure criteria for hhfair + irscge/lrgcge/moncge; re-confirm all four genuine Case-c;
re-confirm the sign-flip BAN (control-refuted 4x S30-S31).

## Deliverables
- docs/planning/EPIC_4/SPRINT_32/CASE_C_CLASSIFIER_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 5.1-5.4 verified
- PREP_PLAN.md: Task 7 -> COMPLETE
- CHANGELOG.md: Task 7 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint32-task7
gh pr create --title "Complete Sprint 32 Prep Task 7: hhfair + CGE Cluster Case-c Formalization Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs/design-only)
- [x] CASE_C_CLASSIFIER_DESIGN.md records the discriminator + the classifier extension + the closure criteria + the sign-flip ban
- [x] All four members (hhfair/irscge/lrgcge/moncge) re-confirmed genuine Case-c
- [x] Unknowns 5.1-5.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 7 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 8 Prompt: Refresh + Author Phase 0 Acceptance Gates for the Sprint-32 Tracks (PR20 + PR24 + PR27)

**Branch:** Create a new branch named `planning/sprint32-task8` from `main`

**Priority:** Critical (4–6 hours)

**Objective:** Author/refresh the Phase 0 acceptance gates (PR20 hand-derived-KKT-before-src; PR24 Day-0-traced fix-surface; PR27 control-experiment-before-implement) for each Sprint-32 track, so every emit-touching implementation starts behind a PROCEED/REPLAN gate. This is the primary scope-correctness gate. **Depends on the three deep-track design docs (Tasks 3/4/5).**

**Unknowns Verified:** 1.1, 2.1, 3.1, 4.1, 5.1

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_32/PREP_PLAN.md` §Task 8
- `docs/planning/EPIC_4/SPRINT_31/PHASE_0_ACCEPTANCE_GATES.md` (the template to refresh for the Sprint-32 dispositions)
- The Task 3/4/5 design docs (mine bound-multiplier / sarf sparsification / camcge `stat_mps`+Walras) — **these must be COMPLETE first**
- The PR-discipline definitions: PR20 (Phase-0 hand-derived KKT), PR24 (Day-0-traced fix-surface = hypothesis), PR27 (control-experiment-before-implement); `docs/issues/ISSUE_{1443,1385,1330,1462,1236}_*.md`

**Tasks to Complete (from PREP_PLAN.md §Task 8 "What Needs to Be Done"):**

1. Author the **P1** gate: the `kkt_residual.py` 4th-site localization + the warm-start residual → 0 (with `modelstat` asserted) → cold MS 1, before the bound-multiplier emit change; the 5th-coupling REPLAN exit.
2. Author the **P2** gate: the O(active-instances) translate-budget probe (time `sarf_mcp.gms`) + the `stat_task` verification against the banked hand-derivation + golden byte-stable, before the emit lands; the timeout-re-trigger REPLAN exit.
3. Author the **P3** gate: the `/tmp` prototype of the `stat_mps` fix + the dual-consistent Walras to MS 1 (omega 191.735) + the detector-flags-only-camcge check, before any `src/` change; the Epic-5-deferral REPLAN exit.
4. Author the **P4/P5** gates: P4 = Case-c residual-clean-at-NLP-point re-confirm before any forcing; P5 = control-experiment-before-implement (the sign flip is BANNED; default to the documented Case-c finding).
5. Cross-link each gate to its KNOWN_UNKNOWNS category + its design doc.

**Deliverables (from PREP_PLAN.md §Task 8):**

- `docs/planning/EPIC_4/SPRINT_32/PHASE_0_ACCEPTANCE_GATES.md` — one PROCEED/REPLAN gate per track (P1–P5), each with its control/probe step, its REPLAN exit, and a cross-link to its KNOWN_UNKNOWNS category + design doc
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.1, 2.1, 3.1, 4.1, 5.1 (gate-layer notes)
- CHANGELOG.md updated with the Task 8 completion entry

**Known Unknowns Updates:** For Unknowns 1.1, 2.1, 3.1, 4.1, 5.1 (the gate-layer aspect — the fix-surface framed as a Day-0 hypothesis gated on a control/probe), append a gate-layer note to each "Verification Results": **Verified by** Task 8, **Date**, **Findings** (the gate authored), **Decision** (the PROCEED/REPLAN criterion). (Their design-layer verification is Tasks 3/4/5/6/7.)

**PREP_PLAN.md Updates:** In §Task 8: Status → ✅ COMPLETE; add `**Completed:**`; fill "Changes" + "Result"; check off all Acceptance Criteria (incl. "Unknowns 1.1, 2.1, 3.1, 4.1, 5.1 verified").

**CHANGELOG.md Update:** Under `### Sprint 32 Prep`, prepend a `**Prep Task 8 COMPLETE (YYYY-MM-DD):**` entry summarizing the five per-track PROCEED/REPLAN gates + the control/probe steps + "Verified Unknowns 1.1/2.1/3.1/4.1/5.1 (gate-layer). Docs-only (gate doc; no `src/`)."

**Quality Gate:**
```bash
make typecheck && make format && make lint && make test
```
Docs-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 32 Prep Task 8: Refresh + Author Phase 0 Acceptance Gates

One PROCEED/REPLAN gate per Sprint-32 track (P1-P5): the mine warm->cold residual gate
(modelstat asserted; 5th-coupling exit); the sarf O(active) translate-budget gate; the
camcge stat_mps-then-Walras /tmp-prototype gate; the rocket Case-c-before-forcing gate;
the hhfair control-before-implement gate (sign flip BANNED). Each cross-links its
KNOWN_UNKNOWNS category + design doc.

## Deliverables
- docs/planning/EPIC_4/SPRINT_32/PHASE_0_ACCEPTANCE_GATES.md
- KNOWN_UNKNOWNS.md: Unknowns 1.1/2.1/3.1/4.1/5.1 verified (gate-layer)
- PREP_PLAN.md: Task 8 -> COMPLETE
- CHANGELOG.md: Task 8 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint32-task8
gh pr create --title "Complete Sprint 32 Prep Task 8: Refresh + Author Phase 0 Acceptance Gates" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs-only)
- [x] PHASE_0_ACCEPTANCE_GATES.md has a PROCEED/REPLAN gate for each of P1-P5 with a control/probe step + a REPLAN exit
- [x] Unknowns 1.1/2.1/3.1/4.1/5.1 verified (gate-layer) in KNOWN_UNKNOWNS.md
- [x] Task 8 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 9 Prompt: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (PR16)

**Branch:** Create a new branch named `planning/sprint32-task9` from `main`

**Priority:** High (3–5 hours)

**Objective:** Apply the PR16 hypothesis-validation methodology to the three deepest REPLAN-prone Sprint-32 tracks — P1 (mine 4th-site bound-dual, deeper-IR risk), P2 (sarf 4-D sparsification, timeout-re-trigger risk), and P3 (camcge Epic-5, dual-consistency risk) — and pin explicit **Sprint 33 REPLAN exits + budget reallocation** for each, so a stalled track hands off cleanly rather than over-running. **Depends on the design docs (Tasks 3/4/5) + the Phase-0 gates (Task 8).**

**Unknowns Verified:** 1.1, 1.2, 2.1, 3.1, 3.2

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_32/PREP_PLAN.md` §Task 9
- The Task 3/4/5 design docs + the Task 8 Phase-0 gates (the PROCEED/REPLAN criteria per track) — **these must be COMPLETE first**
- `docs/planning/EPIC_4/SPRINT_31/SPRINT_RETROSPECTIVE.md` §3 (all five deep tracks REPLAN'd; the reallocation order P5 → P7 → +Translate/forcing tails) + the PR16 hypothesis-validation methodology + the Sprint-30 retro §3 conditionality lesson

**Tasks to Complete (from PREP_PLAN.md §Task 9 "What Needs to Be Done"):**

1. For each of P1/P2/P3, state the hypothesis + the single-model validation (mine → MS 1; sarf → translate; camcge → MS 1) + the PROCEED/REPLAN threshold from Task 8.
2. Pin the Sprint-33 REPLAN exit per track (P1 → deeper-IR head-offset architecture; P2 → symbolic-emit re-scoping; P3 → Epic-5 per-model-numéraire fallback), each with the de-risked hand-off it produces.
3. Define the budget-reallocation order — which freed hours flow where (e.g., P1 slip → P6 offset-alias generalization + P7 property catalog), mirroring the Sprint-31 Task-7 reallocation.
4. Record the honest KPI projection — Solve ≥ 109 is conditional on ≥ 2 of {mine, camcge}; genuine floor ≥ 75 is conditional on those cold-matching; Translate +1 is conditional on sarf.

**Deliverables (from PREP_PLAN.md §Task 9):**

- `docs/planning/EPIC_4/SPRINT_32/REPLAN_RISK_ASSESSMENT.md` — per-track (P1/P2/P3) hypothesis + single-model validation + PROCEED/REPLAN threshold + Sprint-33 REPLAN exit + budget-reallocation order + the honest KPI projection
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.1, 1.2, 2.1, 3.1, 3.2 (REPLAN-prone / risk-layer notes)
- CHANGELOG.md updated with the Task 9 completion entry

**Known Unknowns Updates:** For Unknowns 1.1, 1.2 (mine deep track), 2.1 (sarf timeout), 3.1, 3.2 (camcge Epic-5), append a risk-layer note to each "Verification Results": **Verified by** Task 9, **Date**, **Findings** (the PROCEED/REPLAN prior + the single-model validation + the Sprint-33 exit + the reallocation), **Decision**.

**PREP_PLAN.md Updates:** In §Task 9: Status → ✅ COMPLETE; add `**Completed:**`; fill "Changes" + "Result"; check off all Acceptance Criteria (incl. "Unknowns 1.1, 1.2, 2.1, 3.1, 3.2 verified").

**CHANGELOG.md Update:** Under `### Sprint 32 Prep`, prepend a `**Prep Task 9 COMPLETE (YYYY-MM-DD):**` entry summarizing the per-track PROCEED/REPLAN signals + the Sprint-33 exits + the reallocation order + the honest KPI projection (Solve ≥ 109 conditional on mine + camcge; genuine floor ≥ 75 conditional) + "Verified Unknowns 1.1/1.2/2.1/3.1/3.2 (risk-layer). Docs/analysis-only (no `src/`)."

**Quality Gate:**
```bash
make typecheck && make format && make lint && make test
```
Docs/analysis-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 32 Prep Task 9: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment

Per-track PROCEED/REPLAN signals + Sprint-33 exits + budget reallocation for the three
deepest tracks (mine 4th-site bound-dual, sarf 4-D sparsification timeout, camcge Epic-5
dual-consistency). Honest KPI projection: Solve >=109 conditional on mine [P1] + camcge
[P3]; genuine floor >=75 conditional on those cold-matching; Translate +1 conditional on
sarf. Reallocation order P1 slip -> P6/P7.

## Deliverables
- docs/planning/EPIC_4/SPRINT_32/REPLAN_RISK_ASSESSMENT.md
- KNOWN_UNKNOWNS.md: Unknowns 1.1/1.2/2.1/3.1/3.2 verified (risk-layer)
- PREP_PLAN.md: Task 9 -> COMPLETE
- CHANGELOG.md: Task 9 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint32-task9
gh pr create --title "Complete Sprint 32 Prep Task 9: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs/analysis-only)
- [x] REPLAN_RISK_ASSESSMENT.md has per-track hypothesis + single-model validation + Sprint-33 exit + reallocation + the honest KPI projection
- [x] Unknowns 1.1/1.2/2.1/3.1/3.2 verified (risk-layer) in KNOWN_UNKNOWNS.md
- [x] Task 9 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 10 Prompt: Reusable-Tooling Readiness Audit + Backlog Fix-Surface Analysis (Priorities 6 + 7)

**Branch:** Create a new branch named `planning/sprint32-task10` from `main`

**Priority:** Medium (3–4 hours)

**Objective:** Confirm the Sprint-28–31 diagnostic tooling covers the new Sprint-32 model classes (the mine bound-multiplier residual test, the sarf 4-D sparsification path, the Case-c classifier), and analyze the Priority-6 backlog fix-surfaces (the #1111/#1112 offset-alias generalization beyond polygon/ps2; the residual `model_infeasible` cohort re-triage) plus the Priority-7 property-catalog + genuine-floor-tracking + Epic-4-`SUMMARY` groundwork.

**Unknowns Verified:** 6.1, 6.2, 6.3, 7.1, 7.3

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_32/PREP_PLAN.md` §Task 10
- `docs/planning/EPIC_4/SPRINT_32/KNOWN_UNKNOWNS.md` §Category 6 (6.1–6.3) + §Category 7 (7.1, 7.3) + the Task 8 Phase-0 gates
- The Sprint-28–31 tooling: `scripts/diagnostics/kkt_residual.py`, the golden-staleness gate, the presolve-divergence detector, the `--resolve-changed` mode of `scripts/gamslib/run_full_test.py`, the `--force` scaffold, the AD cross-term property catalog (`tests/integration/emit/test_ad_crossterm_shapes.py`)
- The P6 backlog: #1111/#1112 (offset-alias core, landed for polygon/ps2 in Sprint 31); the residual `model_infeasible` cohort (agreste/cesam/fawley/lnts). The P7 infra: the property-catalog extension surface, the PR25 genuine-floor tracking, the Epic-4 `SUMMARY.md` groundwork

**Tasks to Complete (from PREP_PLAN.md §Task 10 "What Needs to Be Done"):**

1. Tooling readiness audit: for each Sprint-32 track, confirm the reusable tool that guards it (P1 → `kkt_residual.py` + a bound-multiplier residual test; P2 → the translate-budget timer + golden-staleness; P3 → `kkt_residual.py` + the detector; P4 → the `--force` scaffold; P5 → the Case-c classifier extension); identify the minimal extension per track.
2. P6 offset-alias generalization analysis: audit the corpus for other 2-index-transpose models (the #1111/#1112 second-index shape) whose cold emit the general-alias core would correct; list the candidates + the `--resolve-changed` GO gate.
3. P6 failure-cohort re-triage analysis: run `kkt_residual.py` on agreste/cesam/fawley/lnts; record which (if any) re-triage to a fixable Case-b vs genuine Case-c, with banked diagnoses for Sprint 33.
4. P7 groundwork: enumerate the property-catalog fixtures to add (head-offset 4th-site + sarf 4-D), the genuine-floor-tracking recompute surface (S32–S35 footnote ⁸), and the Epic-4 `SUMMARY.md` skeleton (sprint-by-sprint history).

**Deliverables (from PREP_PLAN.md §Task 10):**

- `docs/planning/EPIC_4/SPRINT_32/TOOLING_AND_BACKLOG_ANALYSIS.md` — the per-track tooling-readiness audit + minimal extensions, the P6 offset-alias generalization candidate list + `--resolve-changed` gate, the P6 failure-cohort re-triage (Case-b vs Case-c per model), and the P7 property-catalog + genuine-floor-tracking + Epic-4-SUMMARY groundwork
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 6.1, 6.2, 6.3, 7.1, 7.3
- CHANGELOG.md updated with the Task 10 completion entry

**Known Unknowns Updates:** For Unknowns 6.1 (offset-alias generalization), 6.2 (failure-cohort re-triage), 6.3 (`--resolve-changed` GO gate), 7.1 (property fixtures), 7.3 (checkpoint coverage), set each "Verification Results": **Status**, **Verified by** Task 10, **Date**, **Findings** (the audit + the candidate list + the cohort verdicts), **Evidence** (the harness sweep), **Decision**. (Cross-check 7.2 with Task 2.)

**PREP_PLAN.md Updates:** In §Task 10: Status → ✅ COMPLETE; add `**Completed:**`; fill "Changes" + "Result"; check off all Acceptance Criteria (incl. "Unknowns 6.1, 6.2, 6.3, 7.1, 7.3 verified").

**CHANGELOG.md Update:** Under `### Sprint 32 Prep`, prepend a `**Prep Task 10 COMPLETE (YYYY-MM-DD):**` entry summarizing the per-track tooling readiness, the P6 offset-alias candidate list + the failure-cohort re-triage verdicts, the P7 groundwork, and "Verified Unknowns 6.1/6.2/6.3/7.1/7.3. Audit-only (read-only tool runs; no `src/`)."

**Quality Gate:**
```bash
make typecheck && make format && make lint && make test
```
Audit-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 32 Prep Task 10: Reusable-Tooling Readiness Audit + Backlog Fix-Surface

Per-track tooling-readiness audit + minimal extensions; P6 offset-alias generalization
candidate audit (other 2-index-transpose models) + --resolve-changed GO gate; P6
failure-cohort re-triage (agreste/cesam/fawley/lnts, Case-b vs Case-c); P7
property-catalog fixtures + genuine-floor-tracking recompute surface + Epic-4-SUMMARY
skeleton.

## Deliverables
- docs/planning/EPIC_4/SPRINT_32/TOOLING_AND_BACKLOG_ANALYSIS.md
- KNOWN_UNKNOWNS.md: Unknowns 6.1/6.2/6.3/7.1/7.3 verified
- PREP_PLAN.md: Task 10 -> COMPLETE
- CHANGELOG.md: Task 10 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint32-task10
gh pr create --title "Complete Sprint 32 Prep Task 10: Reusable-Tooling Readiness Audit + Backlog Fix-Surface" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (audit-only)
- [x] TOOLING_AND_BACKLOG_ANALYSIS.md records the tooling audit + the P6 candidate list + the cohort re-triage + the P7 groundwork
- [x] Unknowns 6.1/6.2/6.3/7.1/7.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 10 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 11 Prompt: Plan Sprint 32 Detailed Schedule

**Branch:** Create a new branch named `planning/sprint32-task11` from `main`

**Priority:** Critical (3–4 hours)

**Objective:** Create the detailed Sprint 32 day-by-day schedule (Day 0 setup + Days 1–13 execution) with per-day prompts, integration risks, complexity estimates, checkpoint schedule (Days 5 + 10), and contingency/REPLAN slip valves — incorporating every prep-task output. This is the FINAL prep task because it depends on all others (Tasks 1–10 must be COMPLETE).

**Unknowns Verified:** (integrates all — 1.1–7.3)

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_32/PREP_PLAN.md` §Task 11
- All prep-task outputs: KNOWN_UNKNOWNS (Task 1), BASELINE_METRICS (Task 2), the three design docs (Tasks 3/4/5), the rocket/hhfair packaging (Tasks 6/7), the Phase-0 gates (Task 8), the REPLAN risk assessment (Task 9), the tooling/backlog analysis (Task 10) — **all must be COMPLETE first**
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 32" (Priorities 1–7 + Acceptance Criteria + Estimated Effort 80–120h + Risk HIGH)
- The Sprint-31 detailed schedule (`docs/planning/EPIC_4/SPRINT_31/PLAN.md` + `prompts/PLAN_PROMPTS.md`) as the format template

**Tasks to Complete (from PREP_PLAN.md §Task 11 "What Needs to Be Done"):**

1. Author the day-by-day schedule (Day 0 + Days 1–13) with per-day objectives, prompts, integration risks, and complexity estimates; **front-load P1 (mine) + P3 (camcge)** — the two firm +Solve movers — so a REPLAN surfaces by the Day-5 checkpoint.
2. Place the checkpoints (Day 5 + Day 10) using the `--resolve-changed` checkpoint re-solve, with GO/NO-GO criteria referencing the Day-0 baseline (Task 2).
3. Wire the REPLAN slip valves (Task 9) into the schedule — which day each track's PROCEED/REPLAN gate fires, and where freed budget flows.
4. Set the day-by-day prompts (`prompts/PLAN_PROMPTS.md`), ≤ 12 h/day, with the final Day-13 retest + closeout.

**Deliverables (from PREP_PLAN.md §Task 11):**

- `docs/planning/EPIC_4/SPRINT_32/PLAN.md` — the day-by-day Sprint 32 schedule (Day 0 + Days 1–13) with per-day objectives/prompts/risks/complexity, the Day-5/Day-10 checkpoints, the REPLAN slip valves, and the Day-13 retest + closeout
- `docs/planning/EPIC_4/SPRINT_32/prompts/PLAN_PROMPTS.md` — the day-by-day execution prompts
- The `SPRINT_LOG.md` skeleton (if the epic convention uses one)
- Updated `KNOWN_UNKNOWNS.md` §"Next Steps" (mark the prep phase COMPLETE; note any in-sprint-only unknowns) + CHANGELOG.md updated with the Task 11 completion entry

**Known Unknowns Updates:** In `docs/planning/EPIC_4/SPRINT_32/KNOWN_UNKNOWNS.md` §"Next Steps", update the prep-phase checklist to ✅ COMPLETE (Tasks 1–11), confirm all 25 unknowns are ✅ VERIFIED (or note any that stay 🔍 INCOMPLETE by design as an in-sprint gate, with the reason), and record "Sprint 32 is GO for Day 0."

**PREP_PLAN.md Updates:** In §Task 11: Status → ✅ COMPLETE; add `**Completed:**`; fill "Changes" + "Result"; check off all Acceptance Criteria. Also update the top-level "Success Criteria (all prep tasks complete)" checklist + the "Sprint 32 is ready to start when" line.

**CHANGELOG.md Update:** Under `### Sprint 32 Prep`, prepend a `**Prep Task 11 COMPLETE (YYYY-MM-DD):**` entry summarizing the 14-day schedule (Day 0 + Days 1–13, ≤ 12h/day, front-loading mine + camcge), the Day-5/Day-10 checkpoints, the REPLAN slip valves, the day-by-day prompts, and "All 25 prep unknowns integrated; **Sprint 32 is GO for Day 0. Sprint 32 prep phase COMPLETE** (Tasks 1–11). Docs-only (no `src/`)."

**Quality Gate:**
```bash
make typecheck && make format && make lint && make test
```
Docs-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 32 Prep Task 11: Plan Sprint 32 Detailed Schedule

Sprint 32 14-day schedule (Day 0 + Days 1-13, <=12h/day) + day-by-day execution prompts
+ the SPRINT_LOG skeleton. Front-loads the two firm +Solve movers (mine P1 + camcge P3)
so a REPLAN surfaces by the Day-5 checkpoint; embeds the Day-5/Day-10 --resolve-changed
checkpoints + the REPLAN slip valves (Task 9); closes with the >=3-seed determinism
retest. All 25 prep unknowns integrated; Sprint 32 is GO for Day 0.

## Deliverables
- docs/planning/EPIC_4/SPRINT_32/PLAN.md
- docs/planning/EPIC_4/SPRINT_32/prompts/PLAN_PROMPTS.md
- KNOWN_UNKNOWNS.md: Next Steps -> prep phase COMPLETE
- PREP_PLAN.md: Task 11 -> COMPLETE
- CHANGELOG.md: Task 11 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint32-task11
gh pr create --title "Complete Sprint 32 Prep Task 11: Plan Sprint 32 Detailed Schedule" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make format && make lint && make test` all PASS (docs-only)
- [x] PLAN.md has Day 0 + Days 1-13 (each with objectives/prompts/risks/complexity), the Day-5/Day-10 checkpoints, the REPLAN slip valves, and the Day-13 retest + closeout
- [x] mine (P1) + camcge (P3) front-loaded; ≤12h/day budget honored (80-120h <= 168h)
- [x] KNOWN_UNKNOWNS.md Next Steps marks the prep phase COMPLETE (Sprint 32 GO for Day 0)
- [x] Task 11 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

**Document Created:** 2026-07-13
**Owner:** Sprint 32 Planning Team
**Covers:** Prep Tasks 2–11 (Task 1 already ✅ COMPLETE)

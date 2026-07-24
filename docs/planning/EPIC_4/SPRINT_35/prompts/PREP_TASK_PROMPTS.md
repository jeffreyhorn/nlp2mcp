# Sprint 35 Prep Task Execution Prompts

Self-contained prompts for Sprint 35 Prep Tasks 2–12. Each prompt can be copy-pasted into a new conversation to execute one prep task end-to-end, including the Known Unknowns verification updates, the `PREP_PLAN.md` / `CHANGELOG.md` updates, the quality gate, the commit, and the Pull Request.

**Usage:**

1. Pick a task prompt below.
2. Paste it into a new conversation.
3. The agent creates the branch (`planning/sprint35-task<N>`), does the work, verifies its Known Unknowns, runs the quality gate (only if it touched Python), commits, pushes, and opens a PR.
4. Wait for reviewer comments on the PR.

Task 1 (Create Sprint 35 Known Unknowns List) is already ✅ COMPLETE — no prompt needed (see `docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md`, 29 unknowns across 7 categories).

**Dispatch order** (per the Prep Task Overview dependencies + the critical path in `docs/planning/EPIC_4/SPRINT_35/PREP_PLAN.md`; Task 1 is done, so tasks depending only on it — or on nothing — are immediately dispatchable):

- **Immediately dispatchable:** Task 2 (no dependencies); Task 9 (needs only the completed Task 1)
- **After Tasks 1 + 2:** Task 3 + Task 4 + Task 6 + Task 7 + Task 8 (the tooling/regen survey, the `$149` root analysis, and the three deep-track designs)
- **After Tasks 3 + 4:** Task 5 (the ganges/gangesx recovery design consumes the `$149` derivation **and** the measured golden-regeneration budget)
- **After Tasks 4 + 5 + 6 + 7 + 8 + 9:** Task 10 (the Phase-0 gate authoring consumes every per-track design)
- **After Tasks 5 + 6 + 7 + 8 + 10:** Task 11 (the REPLAN assessment consumes the designs + the gates)
- **After all (final integration):** Task 12

**Critical path:** Task 1 → Task 4 → Task 5 → Task 10 → Task 11 → Task 12 — the **P4 ganges/gangesx chain**, Sprint 35's designated best-shot bucket mover. A near-critical secondary chain runs Task 1 → Task 6 → Task 10 → Task 11 → Task 12 (mine: the largest single budget line, 18–24h, and the highest REPLAN prior).

**Cross-cutting conventions for every prompt below:**

- Branch from `main`; the PR targets `main`. Branch name: `planning/sprint35-task<N>`.
- User preferences (enforce in every commit/PR): **NO `Co-Authored-By` lines** in commit messages; **NO "Generated with Claude Code"** in PR descriptions.
- Replace `YYYY-MM-DD` with the actual date at execution time.
- **The Day-0 code anchor is the S34-close SHA** — derive it with `git log --first-parent main --grep='SPRINT 34 CLOSED' --format=%H -n 1` (`--first-parent -n 1` picks the actual close merge on `main`, not an older matching closeout commit). **This anchor advances from Sprint 34's.** The DB has been byte-unchanged since `750803b2` (the S33 close), but `src/` *did* change during Sprint 34 (the Day-4 P4 sense-aware bound-transfer + 11 regenerated presolve goldens) — so `750803b2` is **historical** for `--resolve-changed` purposes and the S34-close SHA (`78ceaead`) is the Sprint-35 baseline.
- These are **docs/design/analysis-only** prep tasks — no Python source changes are expected (the fixes the designs specify are *built in-sprint*, not in prep; the KKT-residual harness incl. `case_c_objdef`, the presolve-divergence detector, the golden-staleness gate, the `--resolve-changed` mode, and the `--force` scaffold already exist on `main`, as do the S33 `test_sample_pruned_var_l_init.py` and S34 `test_p4_maximize_bound_transfer_sense_aware` fixture patterns). Run the quality gate before committing **only if you touched Python** — per the project's per-day workflow (quality gate only if `*.py` changed), a docs-only task skips it. If you did touch Python, `make typecheck && make lint && make format && make test` must all pass before you commit.
- **PR24/PR27 discipline:** every Sprint-34 control-confirmed characterization is a Day-0-**re-confirm hypothesis**, never fact — including its *sufficiency*, its *root structure*, and its *achievable KPI bucket*. Sprint 34 refuted or corrected its banked premise on every track it touched (mine's H_dual proven value-invariant on the cold solve; fawley's +Solve proven **H-b**; sarf proven a foundational corpus-wide re-architecture; P6's single-root hypothesis proven **three-root**). Record the symptom + reproducer; frame every fix surface as a hypothesis to re-trace; gate any high-blast-radius change on a `/tmp` control experiment BEFORE the `src/` change.
- **Assert `modelstat` before reading an objective off a solve** (the Sprint-31 measurement-error lesson: relaxing `x.up=inf` produced 34 unmatched-variable errors, so the "MS-1 17500" was the embedded LP, not the MCP). The `x.up=inf` experiment is **BANNED** for mine. The Case-c objective-gradient sign flip is **BANNED** (control-refuted 4×).
- **The failure cohort is multi-root** (the Sprint-34 lesson, learned the hard way): verify **per model**, never infer one model's roots from another's. S34's prep asserted "ganges/gangesx share one root; one fix recovers both" and Day 11 found three independent roots with no model recovering from `$141` alone.
- **Prep `file:line` fix-surfaces are hypotheses** — wrong roughly half the time across S27–S34. Label them as such and re-trace at Day 0.
- **"No bucket → no `src/`"**, with the S34 P4 exception criteria (fast, regenerable goldens + `--resolve-changed` GO). Sprint 35's P4 is *expected* to invoke this rule — see Task 3's golden-regeneration budget.
- Every Known-Unknowns update uses the verification block: **Status** (✅ VERIFIED / ❌ WRONG), **Verified by**, **Date**, **Findings**, **Evidence**, **Decision** — replacing the `🔍 **Status:** INCOMPLETE` stub.
- If a task's `/tmp` control cannot be executed inside a docs-only prep, say so explicitly: the PROCEED acceptance is a **spec**, not an executed result, and the unknown's status must reflect that (a DESIGN-SPECIFIED note rather than a false ✅ VERIFIED).

---

## Task 2 Prompt: Sprint 34 → Sprint 35 Day-0 Baseline + Genuine-Floor Re-Baseline (PR15 + PR17 + PR25)

**Branch:** Create a new branch named `planning/sprint35-task2` from `main`

**Priority:** Critical (3–4 hours)

**Objective:** Establish and document the Sprint 35 Day-0 baseline — per-model bucket provenance for the 142-model convex-candidate corpus — confirm it equals the Sprint 34 close (Solve 108 / Match 93 / genuine floor 75 / model_infeasible 7 / path_syntax_error 7 / Translate 135 / Parse 142 / all-219 Match 96), and **advance the `--resolve-changed` code anchor to the S34-close SHA `78ceaead`**.

**Unknowns Verified:** 1.3 (Day-0 mine bucket + fingerprint, contributes), 3.3 (Day-0 fawley bucket, contributes), 4.4 (Day-0 ganges/gangesx provenance, contributes), 7.2 (the PR25 genuine-floor anchor 75 + the code-anchor advance — **primary**)

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_35/PREP_PLAN.md` §Task 2
- `docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md` §Unknowns 1.3, 3.3, 4.4, 7.2
- `docs/planning/EPIC_4/SPRINT_34/BASELINE_METRICS.md` (the bucket-provenance + genuine-vs-methodology template; it pinned the S33-close SHA `750803b2` and floor 75)
- `docs/planning/EPIC_4/SPRINT_34/SPRINT_LOG.md` + `SPRINT_RETROSPECTIVE.md` §1 (the S34 close figures)
- `data/gamslib/gamslib_status.json` (the committed DB, schema 2.2.1) + `scripts/gamslib/run_full_test.py` (`--resolve-changed --since-commit`, `get_candidate_models` — the 142-candidate definition)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 35" (the footnote-⁸ genuine-floor ramp: S34 actual **75** → S35 **≥ 76**)

**Tasks to Complete:**

1. Derive the Day-0 code anchor portably and record it (full SHA + the DB md5):
   ```bash
   S34=$(git log --first-parent main --grep='SPRINT 34 CLOSED' --format=%H -n 1)
   [ -n "$S34" ] || { echo "ERROR: could not resolve the Sprint 34 close SHA — resolve it manually before diffing"; exit 1; }
   git diff --quiet "$S34"..HEAD -- src/ scripts/ || { echo "ERROR: src/scripts drift since the S34 close — a fresh retest is required; do NOT reuse the committed DB"; git diff --stat "$S34"..HEAD -- src/ scripts/; exit 1; }
   echo "no src/scripts drift — safe to reuse the committed DB; Day-0 code anchor = $S34"
   { command -v md5sum >/dev/null 2>&1 && md5sum data/gamslib/gamslib_status.json || md5 -q data/gamslib/gamslib_status.json; }
   ```
2. Recompute the canonical bucket tally from the committed DB (`get_candidate_models`, 142): Parse 142 / Translate 135 / Solve 108 (cold + presolve split) / Match 93 / model_infeasible 7 / path_syntax_error 7 / all-219 Match 96. Enumerate the 7 `model_infeasible` and the 7 `path_syntax_error` members **by name**.
3. Recompute the PR25 genuine-vs-methodology split and confirm the anchor is **75** (63 cold + 12 genuine-presolve; methodology 21; all-219 Match 96 = 63 cold + 33 presolve). Record the → ≥ 76 conversion map (which cold-emit mover supplies it: P4 ganges/gangesx, P1 mine, or P3 fawley) and the footnote-⁸ ramp alignment.
4. Record per-model bucket provenance (Day-0 → expected Day-13) for **every** Sprint-35 target model: mine, sarf, fawley, ganges, gangesx, camcge, rocket, turkey, dinam, indus, turkpow, clearlak, agreste — with its current bucket, failure code, and the priority that owns it.
5. Run `--resolve-changed --since-commit <anchor> --dry-run` and record the GO result as the Day-0 gate (expect 0 changed at Day 0).
6. **Note the anchor advance explicitly** in the document: the DB is byte-unchanged since `750803b2`, but the code anchor is now the S34 close — so no day of the sprint accidentally re-uses the stale anchor.
7. Confirm determinism ×3 `PYTHONHASHSEED` {0,1,42} on a representative Day-0 emit.
8. Write `docs/planning/EPIC_4/SPRINT_35/BASELINE_METRICS.md`.

**Deliverables (from PREP_PLAN.md §Task 2):**

- `docs/planning/EPIC_4/SPRINT_35/BASELINE_METRICS.md` with the Day-0 KPI table (142 corpus) + the Sprint-35 target column
- The Day-0 code anchor (S34-close SHA) + the DB md5 + the portable anchor-derivation snippet
- The PR25 genuine-vs-methodology recompute confirming the anchor **75**
- Per-model provenance rows for all 13 Sprint-35 target models
- The `--resolve-changed --dry-run` Day-0 GO record + the explicit anchor-advance note
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.3, 3.3, 4.4, 7.2

**Known Unknowns Updates:** For Unknowns 1.3, 3.3, 4.4, 7.2 in `docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md`, replace each `🔍 Status: INCOMPLETE` stub with: **Status** ✅ VERIFIED (or ❌ WRONG + correction), **Verified by** Task 2, **Date**, **Findings**, **Evidence** (the DB recompute + the PR25 partition + `git diff <S34-close>..HEAD -- src/ scripts/` empty + the `--dry-run` GO), **Decision**. Note explicitly that 1.3/3.3/4.4 are **partially** verified here — Task 2 supplies only their Day-0-bucket/provenance aspect; their fingerprint/H-b/recovery aspects belong to Tasks 6/8/5 respectively. 7.2 is Task 2's primary.

**PREP_PLAN.md Updates:** In §Task 2: `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`; add `**Completed:** YYYY-MM-DD` on the next line; fill "Changes" (what was measured/authored) and "Result" (the Day-0 baseline + floor 75 + the advanced anchor + the corpus scope); check off **all** Acceptance Criteria (`- [ ]` → `- [x]`), including the "Unknowns 1.3, 3.3, 4.4, 7.2 verified and updated in `KNOWN_UNKNOWNS.md`" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 35 Preparation`, prepend:
```markdown
- **Prep Task 2 COMPLETE (YYYY-MM-DD):** Sprint 35 Day-0 baseline = Sprint 34 close (Solve 108 / Match 93 / genuine floor 75 / model_infeasible 7 / path_syntax_error 7 / Translate 135 / Parse 142 / all-219 Match 96). **Day-0 code anchor advanced to the S34-close SHA** (the DB is byte-unchanged since `750803b2`, but `src/` changed at S34 Day 4 via the P4 sense-aware bound-transfer + 11 regenerated presolve goldens — `750803b2` is now historical for `--resolve-changed`); no `src/`/`scripts/` drift since the S34 close → committed DB reused byte-for-byte, no fresh retest. PR25 genuine floor **75** reproduced from the partition with the → ≥ 76 conversion map + the footnote-⁸ ramp alignment; the 142-corpus (Match 93) vs all-219 (Match 96) distinction recorded. Per-model Day-0 provenance pinned for all 13 Sprint-35 target models; determinism ✅ ×3 `{0,1,42}`; `--resolve-changed --since-commit <S34-close> --dry-run` = GO (0 changed at Day 0). Verified Unknowns 1.3, 3.3, 4.4, 7.2. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected, so the quality gate is not required (docs-only changes skip it, per the project convention). If you did touch Python, run it and do **NOT** commit until all four pass.

**Commit Message Format:**
```
Complete Sprint 35 Prep Task 2: Day-0 Baseline + Genuine-Floor Re-Baseline

Day-0 = Sprint 34 close (Solve 108 / Match 93 / genuine floor 75 / model_infeasible 7
/ path_syntax_error 7 / Translate 135 / Parse 142 / all-219 Match 96). Day-0 code
anchor ADVANCED to the S34-close SHA (DB byte-unchanged since 750803b2, but src/
changed at S34 Day 4 via P4; 750803b2 is now historical). No src/scripts drift since
the S34 close -> committed DB reused, no fresh retest. PR25 genuine floor 75
reproduced with the -> >=76 conversion map. Per-model provenance pinned for all 13
Sprint-35 target models. --resolve-changed --dry-run = GO; determinism x3.

## Deliverables
- docs/planning/EPIC_4/SPRINT_35/BASELINE_METRICS.md
- KNOWN_UNKNOWNS.md: Unknowns 1.3, 3.3, 4.4, 7.2 verified
- PREP_PLAN.md: Task 2 -> COMPLETE
- CHANGELOG.md: Task 2 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint35-task2
gh pr create --base main --title "Complete Sprint 35 Prep Task 2: Day-0 Baseline + Genuine-Floor Re-Baseline" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run `make typecheck && make lint && make format && make test` only if you touched Python)
- [x] BASELINE_METRICS.md records Day-0 = Sprint 34 close + bucket members + genuine floor 75 + the 142-vs-219 split
- [x] Day-0 code anchor advanced to the S34-close SHA, with the anchor-advance caveat called out
- [x] `--resolve-changed --since-commit <S34-close> --dry-run` = GO recorded
- [x] Unknowns 1.3, 3.3, 4.4, 7.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 2 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 3 Prompt: Reusable-Tooling Readiness Audit + Slow-Emit CGE Golden-Regeneration Budget + P7 Fixture Catalog

**Branch:** Create a new branch named `planning/sprint35-task3` from `main`

**Priority:** High (4–5 hours)

**Objective:** Confirm the Sprint-28–34 diagnostic tooling covers the new Sprint-35 emit classes without new tool code; **measure and budget the slow-emit CGE golden regeneration** (ganges, gangesx, clearlak, turkpow) that blocked Sprint 34 from shipping its verified `$141` fix; and catalog the P7 property fixtures each landing track will need.

**Unknowns Verified:** 4.5 (the golden-regeneration budget — **primary**), 7.1 (the P7 fixture catalog), 7.3 (the Epic-4 SUMMARY row-35 continuation)

**Why this task matters:** This removes the single operational blocker that turned a *working, verified* Sprint-34 fix into a banked one. S34 Day 11 shipped no `src/` for the `$141` fix specifically because `make regen-goldens` soft-timed-out on ganges/gangesx/clearlak/turkpow, refreshing **0** goldens — so shipping would have left stale goldens. Sprint 35's P4 is *defined* as the effort that "can afford the slow ganges/gangesx golden regen", but affording it requires knowing, before Day 1, how long it actually takes.

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_35/PREP_PLAN.md` §Task 3
- `docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md` §Unknowns 4.5, 7.1, 7.3
- `docs/planning/EPIC_4/SPRINT_34/TOOLING_AND_BACKLOG_ANALYSIS.md` (the precedent) + `SPRINT_34/DAY11_PROGRESS_NOTES.md` (the banked-fix rationale + the regen soft-timeout) + `SPRINT_34/DAY12_P7_INFRA.md` (the fixture patterns)
- Tooling: `scripts/diagnostics/kkt_residual.py` (Case-a/b/c + `case_c_objdef`) · `scripts/diagnostics/check_presolve_divergence.py` · `scripts/sprint_audit/check_golden_staleness.py` · `scripts/gamslib/run_full_test.py` (`--resolve-changed --since-commit`) · `src/cli.py` (`--force`) · `Makefile` (`regen-goldens`, ~line 72)
- Fixtures: `tests/integration/emit/test_ad_crossterm_shapes.py` + `tests/fixtures/crossterm_shapes/` (shapes 1–11 + `shape_p4_max_bound_transfer.gms`) · `tests/integration/emit/test_sample_pruned_var_l_init.py` (the skip-if-absent pattern)
- `docs/planning/EPIC_4/SUMMARY.md` (rows 33–35)

**Tasks to Complete:**

1. **Audit the reused tooling** against the new Sprint-35 classes — the head-offset dual residual test (P1), the sarf symbolic-emit path + a full-corpus regression harness (P2), the 2-D-cohort `sameas` regression harness (P3), the raw-emit compile check for the ganges roots (P4), the Case-c documentation path (P6). Record reuse vs gap; the target is **zero new diagnostic-tool code**.
2. **Measure the slow-emit golden regeneration** — time a single-model emit for ganges, gangesx, clearlak, turkpow (`data/gamslib/raw/` is present locally; these paths `pytest.skip` in CI). Record wall-clock per model, whether a scoped `regen-goldens` completes where the full run soft-timed-out, and the peak time under `sys.setrecursionlimit(50000)`. **Measure — do not estimate.**
3. **Budget the regeneration into the sprint** — a concrete plan: the scoped/per-model regen invocation, an out-of-band (nightly/background) run window, the determinism-×3 (`PYTHONHASHSEED` {0,1,42}) multiplier, and the follow-on `--resolve-changed` re-solve cost. **State explicitly whether P4 can ship inside a normal ≤ 12h day or needs a dedicated overnight slot** — Task 12 schedules against this verdict.
4. **Catalog the P7 property fixtures**, each gated on its own track's landing and each fail-before/pass-after: **shape12** (head-offset dual → P1), **shape13** (sarf symbolic → P2), a **fawley 2-D second-index** fixture (→ P3), and a **ganges recovery** raw-emit fixture (→ P4, following the `test_sample_pruned_var_l_init.py` skip-if-absent pattern since `data/gamslib/raw/` is absent in CI). Note the genuine-floor recompute (anchor 75) + the Epic-4 `SUMMARY.md` row-35 continuation scope.
5. **Re-run the Day-0 gate** — `--resolve-changed --since-commit <S34-close> --dry-run` = GO.
6. Write `docs/planning/EPIC_4/SPRINT_35/TOOLING_AND_BACKLOG_ANALYSIS.md`.

**Deliverables (from PREP_PLAN.md §Task 3):**

- `docs/planning/EPIC_4/SPRINT_35/TOOLING_AND_BACKLOG_ANALYSIS.md` with the tooling-readiness audit (reuse vs gap)
- A **measured** slow-emit golden-regeneration budget for ganges / gangesx / clearlak / turkpow (per-model wall-clock, scoped-regen feasibility, determinism-×3 multiplier, out-of-band run plan)
- An explicit "fits a normal ≤ 12h day / needs a dedicated overnight slot" verdict for P4
- The P7 fixture catalog (shape12 → P1, shape13 → P2, fawley 2-D → P3, ganges recovery → P4), each fail-before/pass-after and landing-gated
- The genuine-floor recompute note (anchor 75) + the Epic-4 `SUMMARY.md` row-35 continuation scope
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.5, 7.1, 7.3

**Known Unknowns Updates:** For Unknowns 4.5, 7.1, 7.3, replace each `🔍 Status: INCOMPLETE` stub with the verification block (**Status** ✅ VERIFIED / ❌ WRONG, **Verified by** Task 3, **Date**, **Findings** [the measured per-model wall-clock; the scoped-regen outcome; the fixture catalog; the SUMMARY row-35 state], **Evidence** [the timing runs + the tool inventory + the `--dry-run` GO], **Decision** [the shipping window verdict for P4]). If the regeneration proves infeasible even scoped, say so plainly — that is a ❌ WRONG on 4.5 and it changes P4's whole shipping story, which Task 11 must then weigh.

**PREP_PLAN.md Updates:** In §Task 3: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria, including the "Unknowns 4.5, 7.1, 7.3 verified and updated in `KNOWN_UNKNOWNS.md`" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 35 Preparation`, prepend:
```markdown
- **Prep Task 3 COMPLETE (YYYY-MM-DD):** Tooling-readiness audit + the **measured** slow-emit CGE golden-regeneration budget + the P7 fixture catalog. The S28–34 tooling (KKT-residual harness incl. `case_c_objdef`, presolve-divergence detector, golden-staleness gate, `--resolve-changed`, `--force`) covers every new Sprint-35 class — **zero new diagnostic-tool code**. **The S34 ship-blocker is now quantified:** per-model emit wall-clock measured for ganges / gangesx / clearlak / turkpow (the four models whose un-regenerable goldens forced S34 to bank a *verified working* `$141` fix), with a scoped-regen plan, the determinism-×3 multiplier, the follow-on `--resolve-changed` cost, and an explicit "fits a normal day / needs a dedicated overnight slot" verdict for P4 (Task 12 schedules against it). P7 fixtures catalogued and landing-gated (shape12 → P1, shape13 → P2, fawley 2-D → P3, ganges recovery → P4, the last following the `test_sample_pruned_var_l_init.py` skip-if-absent pattern). Genuine-floor anchor 75 + Epic-4 `SUMMARY.md` row-35 continuation scoped. `--resolve-changed --since-commit <S34-close> --dry-run` = GO. Verified Unknowns 4.5, 7.1, 7.3. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — the quality gate is not required unless you touched Python. Note: the timing measurements run emits, not tests; they do not require the gate. If you touched Python, all four must pass before you commit.

**Commit Message Format:**
```
Complete Sprint 35 Prep Task 3: Tooling Audit + Golden-Regen Budget + Fixture Catalog

The S28-34 tooling covers every new Sprint-35 class - zero new diagnostic-tool code.
Measured the slow-emit golden regeneration for ganges/gangesx/clearlak/turkpow (the
S34 ship-blocker that forced a verified $141 fix to be banked): per-model wall-clock,
scoped-regen feasibility, determinism-x3 multiplier, follow-on --resolve-changed cost,
and an explicit fits-a-day / needs-an-overnight-slot verdict for P4. Catalogued the
four P7 fixtures, each gated on its own track's landing.

## Deliverables
- docs/planning/EPIC_4/SPRINT_35/TOOLING_AND_BACKLOG_ANALYSIS.md
- KNOWN_UNKNOWNS.md: Unknowns 4.5, 7.1, 7.3 verified
- PREP_PLAN.md: Task 3 -> COMPLETE
- CHANGELOG.md: Task 3 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint35-task3
gh pr create --base main --title "Complete Sprint 35 Prep Task 3: Tooling Audit + Golden-Regen Budget + Fixture Catalog" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run `make typecheck && make lint && make format && make test` only if you touched Python)
- [x] Golden-regeneration wall-clock **measured** (not estimated) for all four slow-emit models
- [x] Explicit "fits a normal day / needs an overnight slot" verdict recorded for P4
- [x] P7 fixture catalog complete with landing gates + the skip-if-absent pattern for raw-dependent fixtures
- [x] Unknowns 4.5, 7.1, 7.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 3 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 4 Prompt: `$149` CES/LES `prod()` Product-Rule Stationarity AD Root Analysis + Uncontrolled-Index Cohort Catalog

**Branch:** Create a new branch named `planning/sprint35-task4` from `main`

**Priority:** Critical (5–7 hours) — **on the critical path**

**Objective:** Localize the `$149` "uncontrolled index" defect to a specific emit/AD surface, hand-derive the correct `stat_pc` cross-term for ganges's CES/LES `prod(j, (pc(j)/pc00(j))**ac(j,r))` term, and catalog exactly which `path_syntax_error` cohort members the fix unblocks — and which carry additional independent roots it does not touch.

**Unknowns Verified:** 4.3 (the `$149` localization + hand-derived cross-term — **primary**), 6.1 (which cohort members `$149` unblocks — **primary**), 6.2 (the multi-root discipline — **primary**)

**Why this task matters:** `$149` is the deepest blocker Sprint 35 owns and gates the most models (**ganges, gangesx, dinam, indus, turkpow, clearlak**). It is also the only root whose *fix shape* is unknown — S34 Day 11 characterized the symptom but did not localize the defect or derive the correction. Doing that analysis inside the sprint would consume the P4 budget and risk a second Day-11-style late correction.

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_35/PREP_PLAN.md` §Task 4
- `docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md` §Unknowns 4.3, 6.1, 6.2
- `docs/planning/EPIC_4/SPRINT_34/DAY11_PROGRESS_NOTES.md` (the three-root correction + the per-model cohort characterization) + `SPRINT_34/SPRINT_35_CARRYFORWARDS.md` §4
- `src/kkt/stationarity.py` (`_add_indexed_jacobian_terms`, ~line 5861 — the general indexed cross-term path) + `src/ad/` (the differentiation layer) + `src/ad/index_mapping.py`
- `data/gamslib/raw/ganges.gms` + the committed goldens under `data/gamslib/mcp/`
- `docs/research/multidimensional_indexing.md`
- **Standing lesson:** bugs of this class have historically lived in `src/kkt/stationarity.py`, **not** in the AD layer — but that is a hypothesis to verify, not a fact to assume.

**Tasks to Complete:**

1. **Reproduce `$149` live** — emit ganges (`sys.setrecursionlimit(50000)`) and compile the golden, capturing the exact offending `stat_pc` line(s) and the free index **verbatim**.
2. **Hand-derive the correct cross-term** — for `prod(j, (pc(j)/pc00(j))**ac(j,r))`, derive ∂/∂`pc(i)` symbolically (product rule; account for the `**` exponent and the `ac(j,r)` coefficient), and write the *correct* GAMS-emittable form with **every index bound**. Present both candidate emit forms (the explicit `prod` ratio `prod(j,f(j))/f(i)*f'(i)` and the `exp(sum(j, log …))` form), pick one, and justify the choice — note that the naive ratio form is numerically unsafe as `pc(i) → 0`.
3. **Localize the defect** — trace the emit path from the `prod()` AST node through the stationarity builder to the emitted string; identify the `file:line` where the free index is introduced. Start at `src/kkt/stationarity.py` (`_add_indexed_jacobian_terms` and the product/power handling); confirm **or refute** that the AD layer is not the surface. **Record the finding as a hypothesis with the evidence that supports it**, per the standing lesson.
4. **Build the cohort catalog** — for each of ganges, gangesx, dinam, indus, turkpow, clearlak, turkey: compile the committed golden, tabulate every distinct `$NNN` error code with its count, and mark which are `$149`-caused vs independent. Explicitly answer: **after a correct `$149` fix, which models still fail and on what?**
5. **Estimate the blast radius** — grep the corpus for other models emitting `prod()`/`**` stationarity terms (candidates: the CGE cluster, cesam2, camcge) and list them as the regression set the P4 gate must cover.
6. Write `docs/planning/EPIC_4/SPRINT_35/GANGES_149_PRODUCT_RULE_ANALYSIS.md`.

**Deliverables (from PREP_PLAN.md §Task 4):**

- `docs/planning/EPIC_4/SPRINT_35/GANGES_149_PRODUCT_RULE_ANALYSIS.md`
- The verbatim offending `stat_pc` emit line(s) + the identified free index
- The hand-derived correct ∂/∂`pc(i)` cross-term in GAMS-emittable form, with the emit-form choice justified
- A `file:line` fix-surface hypothesis with its supporting evidence (explicitly labelled a hypothesis)
- The per-model cohort catalog (7 models × distinct `$NNN` codes × counts) answering "what still fails after `$149`"
- The blast-radius regression set (other `prod()`/`**` stationarity models)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.3, 6.1, 6.2

**Known Unknowns Updates:** For Unknowns 4.3, 6.1, 6.2, replace each `🔍 Status: INCOMPLETE` stub with the verification block (**Status** ✅ VERIFIED / ❌ WRONG, **Verified by** Task 4, **Date**, **Findings** [the verbatim offending line; the derivation; the localization; the per-model code×count table], **Evidence** [the live emit + compile output + the emit-path trace], **Decision** [the correction to specify in Task 5, and which cohort members remain blocked]). If the localization refutes the `stationarity.py` hypothesis and the defect is in the AD core, mark 4.3's assumption ❌ WRONG with the correction — that materially changes P4's depth and Task 11 must weigh it.

**PREP_PLAN.md Updates:** In §Task 4: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria, including the "Unknowns 4.3, 6.1, 6.2 verified and updated in `KNOWN_UNKNOWNS.md`" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 35 Preparation`, prepend:
```markdown
- **Prep Task 4 COMPLETE (YYYY-MM-DD):** `$149` CES/LES `prod()` product-rule stationarity AD root analysis + the uncontrolled-index cohort catalog. Reproduced `$149` live on ganges and captured the offending `stat_pc` emit line verbatim; **hand-derived the correct ∂/∂`pc(i)` cross-term** for `prod(j, (pc(j)/pc00(j))**ac(j,r))` in fully index-bound GAMS (emit-form choice justified — the naive ratio form is numerically unsafe as `pc(i) → 0`); **localized the free-index defect to a `file:line` hypothesis** (labelled a hypothesis per the standing "prep fix-surfaces are wrong ~half the time" lesson) with its supporting emit-path trace. Built the **per-model cohort catalog** (ganges / gangesx / dinam / indus / turkpow / clearlak / turkey × distinct `$NNN` codes × counts), answering the question S34 got wrong: *which models still fail after `$149`, and on what* — dinam/indus additionally carry `$140`, turkpow/clearlak additionally carry `$171`, turkey is a separate `$161` root. Enumerated the blast-radius regression set (other `prod()`/`**` stationarity models) for the P4 gate. Verified Unknowns 4.3, 6.1, 6.2. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only/analysis task — the quality gate is not required unless you touched Python. Any instrumentation you add to trace the emit path must be reverted before committing (this is an analysis task, not a fix task). If you did leave Python changes, all four must pass.

**Commit Message Format:**
```
Complete Sprint 35 Prep Task 4: $149 Product-Rule Root Analysis + Cohort Catalog

Reproduced $149 live on ganges with the offending stat_pc line captured verbatim.
Hand-derived the correct d/d pc(i) cross-term for the CES/LES prod() term in fully
index-bound GAMS, with the emit-form choice justified. Localized the free-index defect
to a file:line hypothesis with its supporting emit-path trace. Built the per-model
cohort catalog (7 models x distinct $NNN codes x counts) answering "what still fails
after $149" - the question S34's prep got wrong. Enumerated the blast-radius set.

## Deliverables
- docs/planning/EPIC_4/SPRINT_35/GANGES_149_PRODUCT_RULE_ANALYSIS.md
- KNOWN_UNKNOWNS.md: Unknowns 4.3, 6.1, 6.2 verified
- PREP_PLAN.md: Task 4 -> COMPLETE
- CHANGELOG.md: Task 4 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint35-task4
gh pr create --base main --title "Complete Sprint 35 Prep Task 4: \$149 Product-Rule Root Analysis + Cohort Catalog" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only/analysis change — quality gate not required (any tracing instrumentation reverted)
- [x] `$149` reproduced live with the offending emit line captured verbatim
- [x] Correct cross-term hand-derived in fully index-bound, GAMS-emittable form
- [x] Fix surface localized to a `file:line` and explicitly labelled a hypothesis
- [x] All seven cohort models compiled and catalogued by code + count
- [x] Unknowns 4.3, 6.1, 6.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 4 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 5 Prompt: ganges/gangesx Multi-Root Recovery Design (Priority 4 Foundation)

**Branch:** Create a new branch named `planning/sprint35-task5` from `main`

**Priority:** Critical (5–7 hours) — **on the critical path**

**Dependencies:** Tasks 3 and 4 must be complete (this design consumes Task 4's `$149` derivation **and** Task 3's measured golden-regeneration budget).

**Objective:** Design the Priority-4 recovery as an ordered, individually-gated sequence of three independent root fixes (`$141` re-apply → `$145` universal-set skip → `$149` product-rule correction) plus turkey's separate `$161`, with a per-model verification protocol and a golden-regeneration plan that lets the fixes actually ship.

**Unknowns Verified:** 4.1 (the banked `$141` fix re-validation), 4.2 (`$145` independence), 4.3 (the `$149` correction spec — contributes, building on Task 4's derivation), 4.4 (the per-model recovery verdict + protocol — **primary**), 4.6 (turkey `$161`)

**Why this task matters:** P4 is Sprint 35's **designated best-shot bucket mover**: +2 Solve / +2 Match / −2 path_syntax_error (and +2 genuine floor if ganges/gangesx cold-match), against three deep tracks whose priors are all "no bucket". S34 proved that fixing one root recovers **nothing**, so the design must state up front what "progress" looks like after each root and how the three land as a coherent unit.

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_35/PREP_PLAN.md` §Task 5
- `docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md` §Unknowns 4.1, 4.2, 4.3, 4.4, 4.6
- `docs/planning/EPIC_4/SPRINT_35/GANGES_149_PRODUCT_RULE_ANALYSIS.md` (Task 4) + `docs/planning/EPIC_4/SPRINT_35/TOOLING_AND_BACKLOG_ANALYSIS.md` (Task 3) + `docs/planning/EPIC_4/SPRINT_35/BASELINE_METRICS.md` (Task 2)
- `docs/planning/EPIC_4/SPRINT_34/DAY11_PROGRESS_NOTES.md` + `SPRINT_34/SPRINT_35_CARRYFORWARDS.md` §4
- `src/emit/original_symbols.py` (`emit_post_assignment_na_cleanup` ~line 152, `_param_assignment_has_division` ~line 137 — the sibling the banked helper mirrors) + `src/emit/emit_gams.py` (the presolve-gated param assignment) + `src/kkt/stationarity.py`
- `data/gamslib/raw/ganges.gms`, `gangesx.gms`, `turkey.gms`

**Tasks to Complete:**

1. **Re-validate the banked `$141` fix against the current tree** — confirm the helper still applies cleanly (`_param_assignment_has_division` and `emit_post_assignment_na_cleanup` still at their recorded locations with the same signatures) and re-verify it removes all 15 `$141` from the ganges emit. Record any drift since S34 Day 11. Check for collateral emit changes on other models.
2. **Design the `$145` universal-set skip** — how the cleanup pass should treat a `*`-domain parameter (skip vs guard-with-domain), where in `emit_post_assignment_na_cleanup` the branch belongs, and the minimal reproducing shape. Confirm `$145` is independent of the `$141` criterion (or correct the assumption).
3. **Specify the `$149` correction** from Task 4's derivation — the concrete emit change at the localized `file:line`, the index-binding it introduces, and the hand-derived cross-term it must reproduce.
4. **Order the landings and gate each one** — `$141` → `$145` → `$149` (cheapest-and-verified first, deepest last), each with its own `--resolve-changed --since-commit <S34-close>` run and its own golden refresh. **State the expected bucket outcome after each step, explicitly noting that no bucket movement is expected until all three land** (the S34 finding), so a mid-sequence flat KPI is not misread as failure.
5. **Define the per-model verification protocol** — for ganges and gangesx **independently** (never inferred from one another): emit → compile → count residual `$NNN` by code → translate → solve (cold and presolve, `modelstat` asserted) → bucket → match classification. The multi-root discipline is a deliverable, not a note.
6. **Fold in the golden-regeneration plan from Task 3** — which models regenerate, in what window, with determinism ×3, and the follow-on `--resolve-changed` re-solve.
7. **Scope turkey's `$161`** as a separate, smaller item with its own gate, and decide whether it belongs in P4 or P6.
8. **Name the REPLAN exit** — what evidence would say the `$149` correction is out of reach in-sprint (e.g. the derivation implies a general AD-core restructure of `prod` differentiation), and where the budget goes if so (→ P6/P7).
9. Write `docs/planning/EPIC_4/SPRINT_35/GANGES_RECOVERY_DESIGN.md`.

**Deliverables (from PREP_PLAN.md §Task 5):**

- `docs/planning/EPIC_4/SPRINT_35/GANGES_RECOVERY_DESIGN.md`
- The re-validated `$141` fix (clean-apply confirmation + the 15-error removal re-verified against the current tree)
- The `$145` universal-set skip design + its minimal reproducing shape
- The `$149` correction specification derived from Task 4
- The ordered, individually-`--resolve-changed`-gated landing sequence with the expected per-step bucket outcome
- The per-model (ganges *and* gangesx, independently) verification protocol
- The golden-regeneration plan folded in from Task 3
- turkey `$161` scoped as a separate item with its own gate and P4/P6 placement decision
- The named REPLAN exit + budget reallocation target
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.2, 4.3, 4.4, 4.6

**Known Unknowns Updates:** For Unknowns 4.1, 4.2, 4.3, 4.4, 4.6, replace each `🔍 Status: INCOMPLETE` stub with the verification block (**Status** ✅ VERIFIED / ❌ WRONG, **Verified by** Task 5, **Date**, **Findings**, **Evidence**, **Decision**). For 4.3, append a Task-5 contribution block and **preserve Task 4's primary block**. For **4.4** be scrupulously honest: unless you have actually emitted, compiled, solved and classified both models with all three roots applied, the recovery verdict is a **design specification, not an executed result** — mark it DESIGN-SPECIFIED rather than ✅ VERIFIED, because this is exactly the assumption Sprint 34 got wrong.

**PREP_PLAN.md Updates:** In §Task 5: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria, including the "Unknowns 4.1, 4.2, 4.3, 4.4, 4.6 verified and updated in `KNOWN_UNKNOWNS.md`" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 35 Preparation`, prepend:
```markdown
- **Prep Task 5 COMPLETE (YYYY-MM-DD):** ganges/gangesx multi-root recovery design (P4 — the sprint's designated best-shot bucket mover). Re-validated the **banked-and-verified `$141` fix** against the current tree (clean apply; 15 `$141` removed; collateral emit changes checked). Designed the **`$145` universal-set (`*`-domain) skip** with its minimal reproducing shape. Specified the **`$149` correction** from Task 4's hand-derived cross-term at the localized `file:line`. **Ordered the landings `$141` → `$145` → `$149`**, each individually `--resolve-changed`-gated with its own golden refresh, and recorded the expected per-step bucket outcome — **explicitly: no bucket movement until all three land** (the S34 finding), so a mid-sequence flat KPI is not misread as failure. Defined the **per-model verification protocol** for ganges and gangesx *independently* (emit → compile → count residual `$NNN` → translate → solve with `modelstat` asserted → bucket → match), encoding the multi-root discipline S34 learned the hard way. Folded in Task 3's measured golden-regeneration window + determinism ×3 + the follow-on re-solve. Scoped turkey's `$161` separately with a P4/P6 placement decision. Named the REPLAN exit (an AD-core restructure) + the budget reallocation target. Verified Unknowns 4.1, 4.2, 4.3, 4.4, 4.6. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only design task — the quality gate is not required unless you touched Python. **The `$141` re-validation must be done in a scratch tree and reverted** — this is a design task, not the P4 landing. If any Python survives to the commit, all four must pass.

**Commit Message Format:**
```
Complete Sprint 35 Prep Task 5: ganges/gangesx Multi-Root Recovery Design

Re-validated the banked $141 fix against the current tree (clean apply, 15 errors
removed). Designed the $145 universal-set skip. Specified the $149 correction from
Task 4's derivation. Ordered the landings $141 -> $145 -> $149, each individually
--resolve-changed-gated, with the expected per-step bucket outcome recorded -
explicitly: no bucket movement until all three land (the S34 finding). Defined the
per-model verification protocol for ganges and gangesx independently. Folded in Task
3's golden-regeneration window. Scoped turkey $161 separately. Named the REPLAN exit.

## Deliverables
- docs/planning/EPIC_4/SPRINT_35/GANGES_RECOVERY_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 4.1, 4.2, 4.3, 4.4, 4.6 verified
- PREP_PLAN.md: Task 5 -> COMPLETE
- CHANGELOG.md: Task 5 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint35-task5
gh pr create --base main --title "Complete Sprint 35 Prep Task 5: ganges/gangesx Multi-Root Recovery Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (the `$141` re-validation was done in a scratch tree and reverted)
- [x] The banked `$141` fix re-validated against the current tree
- [x] The three roots ordered with a per-root `--resolve-changed` gate and per-step expected bucket outcome
- [x] "No bucket movement until all three land" stated explicitly
- [x] Per-model verification protocol defined for ganges and gangesx independently
- [x] Unknowns 4.1, 4.2, 4.3, 4.4, 4.6 verified in KNOWN_UNKNOWNS.md
- [x] Task 5 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 6 Prompt: mine Head-Offset Dual-Architecture Design (Priority 1 Foundation)

**Branch:** Create a new branch named `planning/sprint35-task6` from `main`

**Priority:** Critical (6–8 hours) — **near-critical path** (P1 is the largest single budget line, 18–24h, with the highest REPLAN prior)

**Objective:** Turn the Sprint-34 Day-1 refutation (H_dual is value-invariant; the head-offset dual boundary is **`x.m = 0`-degenerate**) into either a concrete head-offset dual-architecture design that can reach **cold MS-1 @ 17500**, or an explicitly-argued conclusion that no emit-side architecture can — in which case the track's disposition is decided in prep rather than on Day 3.

**Unknowns Verified:** 1.1 (boundary reachability), 1.2 (the reconciliation + cold-MS-1 gate), 1.3 (the 22-row / +16000 re-confirm), 1.4 (IR sufficiency), 1.5 (REPLAN prior + disposition)

**Why this task matters:** mine is **four-times-carried** (S32 → S33 → S34 → S35) and each sprint has refuted the then-current hypothesis with a control before shipping anything. Spending 18–24h of sprint budget on a fifth hypothesis without first asking whether the boundary is reachable at all would be the least defensible allocation in the plan. **An honest "REPLAN before Day 1" is a successful outcome for this task** — it frees the largest budget line to P4.

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_35/PREP_PLAN.md` §Task 6
- `docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md` §Unknowns 1.1–1.5
- `docs/planning/EPIC_4/SPRINT_34/DAY1_PROGRESS_NOTES.md` (the H_dual cold-MS-1 control: compiled with 0 errors but scalar-identical to baseline — both cold MS-5, profit 16747.0723, 51 INFES) + `SPRINT_34/MINE_DUAL_SUBSYSTEM_DESIGN.md` §§3.2/4/5 (the boundary needs +16000)
- `docs/planning/EPIC_4/SPRINT_33/MINE_CROSSTERM_DESIGN.md` + `SPRINT_33/DAY2_MINE_REPLAN.md` (H1 value-invariance, 22 → 22 rows, `d_N = d_Nh1`) + `SPRINT_32/MINE_5TH_COUPLING_REPLAN.md`
- `src/kkt/stationarity.py` + the S31 `EquationDef.head_domain_offsets` IR (`src/ir/parser.py`, `_domain_list_head_offsets`) + `scripts/diagnostics/kkt_residual.py` + `data/gamslib/raw/mine.gms`
- **PR24/PR27 + assert `modelstat` + `x.up=inf` BANNED + the objective-gradient sign flip BANNED** (see the cross-cutting conventions)

**Tasks to Complete:**

1. **Re-state the refutation precisely** — what S33 and S34 each proved, and what specifically remains unrefuted. Distinguish "this keying is value-invariant" from "no emit change can move the boundary".
2. **Characterize the degeneracy formally** — at the bound-active `stat_x` rows, write the stationarity identity with every available multiplier (`piU_x`, `piL_x`, `lam_pr`, the precedence duals) and show which terms are structurally zero when `x.m = 0`. Quantify the gap (+16000) against what each candidate contribution could supply.
3. **Re-confirm the Day-0 fingerprint** — `kkt_residual.py mine.gms` → CASE_B `stat_x(3,1,1)` rel 2.37, raw −32000, dual scale 1.35e4, dual CONSISTENT; 22 nonzero rows all on the `c`-boundary; the LP primal feasible/optimal at 17500 (`modelstat` asserted). Check whether the S34 P4 sense-aware bound-transfer perturbed any figure.
4. **Enumerate ≥ 4 candidate architectures** — for each, state the emit change, the IR support it needs from `head_domain_offsets`, and the mechanism by which it supplies the missing contribution. At minimum: (a) an explicit head-offset dual variable paired at the shifted label; (b) a reformulation of the precedence constraint so its dual lands at the base label; (c) an augmented complementarity pairing keeping both labels' multipliers live; (d) an LP-side reformulation upstream of emit.
5. **Score each candidate on reachability** — can it, in principle, supply the +16000 without the banned sign flip? **Reject the ones that cannot, on the record.**
6. **Design the surviving candidate to `file:line`** — the emit change in `src/kkt/stationarity.py`, the IR reads from `head_domain_offsets`, and the interior-row invariance argument. State the fix surface as a **hypothesis** (PR24).
7. **Specify the pre-`src/` `/tmp` control** — warm residual → 0 at **all** bound-active rows AND unchanged (0) at interior rows, **then** cold/presolve MS-1 @ 17500, `modelstat` asserted every time. Note explicitly that the warm residual `N → 0` is the **wrong** gate for a keying/pairing change (value-invariance) — the cold solve is the gate.
8. **If no candidate survives, write the REPLAN recommendation** — the disposition (deeper architecture in a later sprint vs the Sprint-36 PATH-consultation track as "an LP whose warm KKT point is not MCP-reconcilable") and the freed-budget target (→ P4/P6/P7).
9. Write `docs/planning/EPIC_4/SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md`.

**Deliverables (from PREP_PLAN.md §Task 6):**

- `docs/planning/EPIC_4/SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md`
- A precise restatement of what S33/S34 refuted vs what remains open
- The formal degeneracy characterization at the bound-active `stat_x` rows, with the quantified gap
- The enumerated candidate architectures, each scored on reachability, with rejections recorded
- Either a `file:line` design for the surviving candidate **or** a written REPLAN recommendation with its disposition and freed-budget target
- The pre-`src/` `/tmp` control specification (all-bound-active residual → 0, interior rows unchanged, then cold MS-1 @ 17500, `modelstat` asserted)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3, 1.4, 1.5

**Known Unknowns Updates:** For Unknowns 1.1–1.5, replace each `🔍 Status: INCOMPLETE` stub with the verification block (**Status** ✅ VERIFIED / ❌ WRONG, **Verified by** Task 6, **Date**, **Findings**, **Evidence** [the harness fingerprint + the residual decomposition + the candidate scoring], **Decision** [the surviving architecture or the REPLAN recommendation]). For 1.3, append to Task 2's Day-0-bucket block rather than replacing it. If the `/tmp` cold-MS-1 control cannot be executed in a docs-only prep, mark **1.2** DESIGN-SPECIFIED — the control is the in-sprint Day-1 gate — and say so plainly rather than claiming a verified PROCEED.

**PREP_PLAN.md Updates:** In §Task 6: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria, including the "Unknowns 1.1, 1.2, 1.3, 1.4, 1.5 verified and updated in `KNOWN_UNKNOWNS.md`" line. Note that a REPLAN recommendation satisfies the "design **or** argued REPLAN" criterion — do not manufacture a design to check a box.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 35 Preparation`, prepend:
```markdown
- **Prep Task 6 COMPLETE (YYYY-MM-DD):** mine head-offset dual-architecture design (P1 — the sprint's largest single budget line, 18–24h, four-times-carried). Re-stated the S33/S34 refutations precisely (H1 keying **value-invariant**, 22 → 22 rows; H_dual **value-invariant on the cold solve too** — the head-anchored prototype compiled clean but is scalar-identical to baseline, both cold MS-5 @ profit 16747.0723 / 51 INFES), separating "this keying is invariant" from "no emit change suffices". **Formally characterized the `x.m = 0` degeneracy** at the bound-active `stat_x` rows with the quantified +16000 gap, showing which multiplier terms are structurally zero. Re-confirmed the Day-0 fingerprint (CASE_B `stat_x(3,1,1)` rel 2.37, dual CONSISTENT, 22 `c`-boundary rows; LP primal optimal at 17500 with `modelstat` asserted). **Enumerated and scored ≥ 4 candidate dual architectures on reachability**, recording every rejection; [either] designed the surviving candidate to `file:line` with its `head_domain_offsets` IR reads and interior-row invariance argument [or] wrote the argued REPLAN recommendation with its disposition + freed-budget target. Specified the pre-`src/` `/tmp` control — **the cold solve is the gate, not the warm residual `N → 0`** (un-hittable by a keying/pairing change). Standing BANs restated (`x.up=inf`; the objective-gradient sign flip). Verified Unknowns 1.1, 1.2, 1.3, 1.4, 1.5. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only design task — the quality gate is not required unless you touched Python. Any `/tmp` prototype must stay in `/tmp`; nothing lands in `src/` from a prep task.

**Commit Message Format:**
```
Complete Sprint 35 Prep Task 6: mine Head-Offset Dual-Architecture Design

Re-stated the S33/S34 refutations (H1 and H_dual both value-invariant; the cold solve
is scalar-identical to baseline). Formally characterized the x.m=0 degeneracy at the
bound-active stat_x rows with the quantified +16000 gap. Re-confirmed the Day-0
fingerprint. Enumerated and scored >=4 candidate dual architectures on reachability,
recording every rejection, and [designed the survivor to file:line / wrote the argued
REPLAN recommendation with its freed-budget target]. Specified the pre-src/ /tmp
control - the cold solve is the gate, not the warm residual.

## Deliverables
- docs/planning/EPIC_4/SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 1.1, 1.2, 1.3, 1.4, 1.5 verified
- PREP_PLAN.md: Task 6 -> COMPLETE
- CHANGELOG.md: Task 6 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint35-task6
gh pr create --base main --title "Complete Sprint 35 Prep Task 6: mine Head-Offset Dual-Architecture Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (any `/tmp` prototype stayed in `/tmp`)
- [x] The `x.m = 0` degeneracy characterized formally with the quantified boundary gap
- [x] ≥ 4 candidate architectures enumerated and scored on reachability, rejections recorded
- [x] A `file:line` design for the survivor **or** an explicit, argued REPLAN recommendation
- [x] The `/tmp` control specified with `modelstat` asserted and the cold-solve gate (not the warm residual)
- [x] Standing BANs restated (`x.up=inf`; objective-gradient sign flip)
- [x] Unknowns 1.1, 1.2, 1.3, 1.4, 1.5 verified in KNOWN_UNKNOWNS.md
- [x] Task 6 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 7 Prompt: sarf Symbolic/Parametric Emit-Mode Re-Architecture Design (Priority 2 Foundation)

**Branch:** Create a new branch named `planning/sprint35-task7` from `main`

**Priority:** High (5–7 hours)

**Objective:** Design the symbolic/parametric emit mode that stops materializing sarf's 369,024 `task(g,t,mn,mn)` columns at all three sites atomically — including the corpus-wide safety argument for changing `enumerate_variable_instances`, which every one of the 142 models traverses — and the full-corpus regression harness that makes the change shippable.

**Unknowns Verified:** 2.1 (three-site completeness), 2.2 (the O(active) tractability gate), 2.3 (corpus safety for the other 141 models), 2.4 (the 7-term `stat_task` derivation), 2.5 (the guarded emit / 398 live rows)

**Why this task matters:** P2 is the second-largest budget line (20–28h) for the **lowest-leverage** bucket (+1 Translate — it moves neither Solve nor Match), and it has been deferred in three consecutive sprints on that risk/reward basis. There is no safe partial landing. A prep design that cannot articulate the corpus-safety argument and the regression harness is a design that should not be implemented — and saying so before Day 1 is worth more than discovering it on Day 7 for the fourth time.

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_35/PREP_PLAN.md` §Task 7
- `docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md` §Unknowns 2.1–2.5
- `docs/planning/EPIC_4/SPRINT_34/DAY6_PROGRESS_NOTES.md` (the three-site re-confirmation + the foundational finding) + `SPRINT_34/SARF_EMIT_MODE_DESIGN.md`
- `docs/planning/EPIC_4/SPRINT_33/SARF_EMIT_SUBSYSTEM_DESIGN.md` (the banked 7-term `stat_task` derivation) + `SPRINT_32/SARF_STAT_TASK_SPARSIFICATION_DESIGN.md` + `SPRINT_32/SARF_TRANSLATE_REPLAN.md`
- `src/ad/index_mapping.py` (`enumerate_variable_instances` ~line 327; `build_index_mapping`) + `src/kkt/stationarity.py` + the existing equation-level gate `_is_blowup_dynamic_subset_equation`
- `data/gamslib/raw/sarf.gms` + `docs/research/multidimensional_indexing.md`

**Tasks to Complete:**

1. **Re-confirm the three sites at Day-0 scope** — verify S1 (`acost3` scalar body-diff in `compute_constraint_jacobian`), S2 (`enumerate_variable_instances` materializing the columns), S3 (per-column `stat_task`) are still the complete set (S34 Day 6 found no fourth, but this is a re-confirm hypothesis), and that 369,024 = 16·24·31·31 and the 398 active count still hold.
2. **Design the symbolic-column concept** — how a variable presents as a domain expression + guard rather than an enumerated instance list, and what `col_to_var` becomes for such variables.
3. **Make the corpus-safety argument explicit** — how the other 141 models' `col_to_var` construction and ordering stay byte-identical (determinism is a hard requirement, PR12), and which code paths must branch on symbolic-vs-enumerated. Enumerate every call site.
4. **Design the parametric cross-term path** — the new path producing `stat_task`'s cross-terms without per-instance Jacobian entries, checked against the banked 7-term derivation, with every index bound and no set-name-literal indices.
5. **Specify the guarded emit** — `stat_task(g,t,m,n)$taskposs` + the `task.fx(...)$(not (...)) = 0` companion + the MCP matching, and argue it yields exactly the 398 live rows.
6. **Specify the tractability gate (PR20)** — the re-emit must be **O(active = 398), not O(369K)**: time `sarf_mcp.gms` emission (target seconds; the current failure is > 75s), with the measurement method pinned and the pass threshold stated. **Pre-classify a partial improvement that does not cross the threshold as a REPLAN, not as progress.**
7. **Specify the full-corpus regression harness** — the atomic-landing requirement, byte-stable goldens for all 141 other models, determinism ×3 (`PYTHONHASHSEED` {0,1,42}), and the `--resolve-changed --since-commit <S34-close>` full-corpus run.
8. **Name the REPLAN exit** — a fourth enumeration site, a determinism break, any non-byte-stable golden on an unrelated model, or a re-triggered timeout → re-scope and hand off, freed budget to P4/P6.
9. Write `docs/planning/EPIC_4/SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md`.

**Deliverables (from PREP_PLAN.md §Task 7):**

- `docs/planning/EPIC_4/SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md`
- The S1/S2/S3 re-confirmation (or a corrected site list) with the 369,024 / 398 counts re-verified
- The symbolic-column design + what `col_to_var` becomes for symbolic variables
- The corpus-safety argument (141 other models byte-identical; determinism preserved) with the branching code paths named
- The parametric cross-term path checked against the banked 7-term derivation
- The guarded emit specification (`$taskposs` + `task.fx` companion + MCP matching → exactly 398 live rows)
- The quantified tractability gate (O(active) vs the > 75s failure) with its measurement method
- The full-corpus regression harness specification
- The named REPLAN exit + freed-budget target
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.1, 2.2, 2.3, 2.4, 2.5

**Known Unknowns Updates:** For Unknowns 2.1–2.5, replace each `🔍 Status: INCOMPLETE` stub with the verification block (**Status** ✅ VERIFIED / ❌ WRONG, **Verified by** Task 7, **Date**, **Findings**, **Evidence** [the instrumented emit trace + the call-site enumeration + the hand re-derivation + the timing baseline], **Decision**). For **2.2**, record the *measured* current emit wall-clock as the baseline; the post-change figure is an in-sprint result, so mark that half DESIGN-SPECIFIED. For **2.4**, if any of the 7 terms fails to re-derive, mark ❌ WRONG with the correction — a silently wrong `stat_task` is the worst failure mode on this track.

**PREP_PLAN.md Updates:** In §Task 7: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria, including the "Unknowns 2.1, 2.2, 2.3, 2.4, 2.5 verified and updated in `KNOWN_UNKNOWNS.md`" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 35 Preparation`, prepend:
```markdown
- **Prep Task 7 COMPLETE (YYYY-MM-DD):** sarf symbolic/parametric emit-mode re-architecture design (P2 — 20–28h for the lowest-leverage bucket, +1 Translate, thrice-deferred). Re-confirmed the three enumeration sites (S1 `acost3` body-diff, S2 `enumerate_variable_instances`, S3 per-column `stat_task`) and the 369,024 = 16·24·31·31 Cartesian / 398 active counts. Designed the **symbolic-column concept** (a domain expression + guard rather than an enumerated instance list) and what `col_to_var` becomes for symbolic variables. **Made the corpus-safety argument explicit** — `enumerate_variable_instances` is foundational for all 142 models, so the design keeps the other 141 models' `col_to_var` construction and ordering byte-identical, with every branching call site named and determinism (PR12) preserved. Designed the parametric cross-term path against the banked 7-term `stat_task` derivation (every index bound, no set-name-literal indices). Specified the guarded emit (`stat_task(g,t,m,n)$taskposs` + the `task.fx` companion + MCP matching → exactly 398 live rows). **Quantified the PR20 tractability gate** — O(active = 398), not O(369K); the measured current emit baseline recorded, the pass threshold stated, and a partial improvement that does not cross it **pre-classified as a REPLAN, not progress**. Specified the full-corpus regression harness (atomic landing, 141 byte-stable goldens, determinism ×3, `--resolve-changed`). Named the REPLAN exit + freed-budget target. Verified Unknowns 2.1, 2.2, 2.3, 2.4, 2.5. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only design task — the quality gate is not required unless you touched Python. Any instrumentation added to trace the enumeration sites must be reverted before committing.

**Commit Message Format:**
```
Complete Sprint 35 Prep Task 7: sarf Symbolic Emit-Mode Re-Architecture Design

Re-confirmed the three enumeration sites and the 369,024 / 398 counts. Designed the
symbolic-column concept and what col_to_var becomes for symbolic variables. Made the
corpus-safety argument explicit - enumerate_variable_instances is foundational for all
142 models, so the other 141 stay byte-identical with determinism preserved and every
branching call site named. Designed the parametric cross-term path against the banked
7-term derivation. Quantified the PR20 tractability gate (O(active=398), not O(369K))
with a partial improvement pre-classified as a REPLAN. Specified the full-corpus
regression harness and named the REPLAN exit.

## Deliverables
- docs/planning/EPIC_4/SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 2.1, 2.2, 2.3, 2.4, 2.5 verified
- PREP_PLAN.md: Task 7 -> COMPLETE
- CHANGELOG.md: Task 7 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint35-task7
gh pr create --base main --title "Complete Sprint 35 Prep Task 7: sarf Symbolic Emit-Mode Re-Architecture Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (tracing instrumentation reverted)
- [x] The three sites re-confirmed (or corrected) with the Cartesian and active counts re-verified
- [x] Corpus-safety argument made explicitly for the other 141 models, determinism preserved
- [x] Parametric cross-term path checked against the banked 7-term derivation
- [x] Tractability gate quantified with a pinned measurement method and a partial-improvement REPLAN classification
- [x] Unknowns 2.1, 2.2, 2.3, 2.4, 2.5 verified in KNOWN_UNKNOWNS.md
- [x] Task 7 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 8 Prompt: fawley Constraint-Index-Diagonal Correction + Forcing Hand-Off Design (Priority 3 Foundation)

**Branch:** Create a new branch named `planning/sprint35-task8` from `main`

**Priority:** High (4–6 hours)

**Objective:** Design the genuine constraint-index-diagonal `sameas` cross-term correction inside `_add_indexed_jacobian_terms` — leak-free against the shared 2-D cohort (mbal, cesam2, camcge, ps2) and the 1-D core (polygon, ps2/ps3) — together with the explicit forcing hand-off for fawley's H-b +Solve, so the correctness win and the (non-emit) solve win are not conflated.

**Unknowns Verified:** 3.1 (`max|stat_bq| → 0`), 3.2 (leak-freedom against mbal / the 1-D core / the 2-D cohort), 3.3 (the H-b re-confirm), 3.4 (the conditional floor lift)

**Why this task matters:** P3 is the clearest case in the sprint of a **genuine correctness fix whose bucket value is contingent**. S34 Day 5 re-confirmed the gap is real (473 → 18.468 with `$(sameas(cfq__,cf))`) *and* that fawley is **H-b**: with the correction plus all bound transfers the warm residual goes to ~0 but the MCP still solves **MS-5 @ 4399.557** against an LP optimum of 2899.25. The design must deliver two separable things and make the separation explicit.

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_35/PREP_PLAN.md` §Task 8
- `docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md` §Unknowns 3.1–3.4
- `docs/planning/EPIC_4/SPRINT_34/DAY5_PROGRESS_NOTES.md` (the H-b finding + the fix-surface examination) + `SPRINT_34/FAWLEY_CORRECTION_FORCING_DESIGN.md` §6 (the gate-leak REPLAN exit)
- `docs/planning/EPIC_4/SPRINT_33/FAWLEY_SECOND_INDEX_DESIGN.md` + `SPRINT_33/DAY4_FAWLEY_CONTROL.md` + `SPRINT_33/DAY5_FAWLEY_CLOSE.md`
- `src/kkt/stationarity.py` (`_add_indexed_jacobian_terms` ~line 5861; the #1104/#1111 offset-group / fresh-alias machinery; the #1049 guard) + `data/gamslib/mcp/fawley_mcp.gms` (the `sameas` occurrences; the gap localized around line 238)
- `src/cli.py` (`--force {homotopy,multistart,optfile}`) + `docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md`

**Tasks to Complete:**

1. **Re-confirm the gap and the H-b finding at Day-0 scope** — `max|stat_bq|` 473 → 18.468 with the guard; MS-5 @ 4399.557 persisting with the residual closed; LP optimum 2899.25. Check whether the S34 P4 sense-aware bound-transfer (which now transfers fawley's `bq(cc-dist)` cell as `abs(var.m)`) changed any figure.
2. **Characterize the constraint-index diagonal precisely** — the index orientation (constraint dimension ≥ variable dimension) that distinguishes it from the #1049 guard (which fires only when the variable has *more* dims than the constraint), expressed as a predicate over the emit-time index structures.
3. **Design the guard** — where in `_add_indexed_jacobian_terms` the diagonal predicate belongs relative to the existing dozen `sameas` paths, with the **precedence argument against each of them** (this is the leak risk).
4. **Define the leak-free requirement operationally** — **no mbal term may change**, and the 1-D core (polygon, ps2, ps3) must be byte-identical; enumerate the 2-D cohort (mbal, cesam2, camcge, ps2) as the regression set and specify the harness.
5. **Specify the pre-`src/` `/tmp` control** — the generalization must drive `max|stat_bq| → 0` (**not** 96%, i.e. not merely 473 → 18.468), with `modelstat` asserted, before any `src/` change. Diagnose what accounts for the residual 18.468 in the partial control.
6. **Design the fawley 2-D second-index property fixture** — fail-before/pass-after, landing with the correction (the P7 catalog entry from Task 3).
7. **Specify the forcing hand-off** — which `--force` levers to survey for fawley's MS-5, what evidence would make the +Solve reachable, and the **explicit statement that the +Solve is not an in-sprint P3 deliverable** (it is a forcing tail; the floor +1 is contingent on a cold match).
8. **Name the REPLAN exit** — a gate leak (any mbal/1-D change) or `max|stat_bq|` not reaching 0 → defer again with the fix surface further characterized, budget to P4/P6.
9. Write `docs/planning/EPIC_4/SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md`.

**Deliverables (from PREP_PLAN.md §Task 8):**

- `docs/planning/EPIC_4/SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md`
- The Day-0 re-confirmation of the gap (473 → 18.468) and the H-b finding (MS-5 @ 4399.557 with the residual closed)
- The constraint-index-diagonal predicate, distinguished explicitly from the #1049 guard orientation
- The guard design with its placement + precedence argument against the existing `sameas` paths
- The operational leak-free requirement (no mbal term change; 1-D core byte-identical) + the 2-D-cohort regression harness
- The pre-`src/` `/tmp` control specification (`max|stat_bq| → 0`, `modelstat` asserted)
- The fawley 2-D second-index property fixture design (fail-before/pass-after)
- The forcing hand-off specification, with the +Solve explicitly excluded from P3's in-sprint deliverables
- The named REPLAN exit + budget reallocation target
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.2, 3.3, 3.4

**Known Unknowns Updates:** For Unknowns 3.1–3.4, replace each `🔍 Status: INCOMPLETE` stub with the verification block (**Status** ✅ VERIFIED / ❌ WRONG, **Verified by** Task 8, **Date**, **Findings**, **Evidence**, **Decision**). For 3.3, append to Task 2's Day-0-bucket block rather than replacing it. For **3.1**, if the `/tmp` control is not executed in prep, mark the "→ 0" half DESIGN-SPECIFIED — the 473 → 18.468 figure is banked evidence, but the closure is not.

**PREP_PLAN.md Updates:** In §Task 8: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria, including the "Unknowns 3.1, 3.2, 3.3, 3.4 verified and updated in `KNOWN_UNKNOWNS.md`" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 35 Preparation`, prepend:
```markdown
- **Prep Task 8 COMPLETE (YYYY-MM-DD):** fawley constraint-index-diagonal correction + forcing hand-off design (P3). Re-confirmed the gap (`max|stat_bq|` 473 → 18.468 with the `$(sameas(cfq__,cf))` guard) and the **H-b** finding (MS-5 @ 4399.557 persisting with the warm residual closed; LP optimum 2899.25) at Day-0 scope, checking the S34 P4 bound-transfer's effect on the warm point. **Characterized the constraint-index diagonal as a predicate** over the emit-time index structures, explicitly distinguished from the #1049 guard's opposite orientation. Designed the guard's placement in `_add_indexed_jacobian_terms` with a **precedence argument against each of the dozen existing `sameas` paths** (the leak risk). Defined the leak-free requirement operationally — **no mbal term may change**, the 1-D core (polygon, ps2, ps3) byte-identical — and enumerated the 2-D regression cohort (mbal, cesam2, camcge, ps2) with its harness. Specified the pre-`src/` `/tmp` control requiring `max|stat_bq| → 0` (**not** the 96% partial), `modelstat` asserted. Designed the fawley 2-D fixture (fail-before/pass-after). **Specified the forcing hand-off and excluded the +Solve from P3's in-sprint deliverables** (H-b; the floor +1 is contingent on a cold match). Named the gate-leak REPLAN exit + reallocation target. Verified Unknowns 3.1, 3.2, 3.3, 3.4. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only design task — the quality gate is not required unless you touched Python. Any `/tmp` control edits must stay in `/tmp`.

**Commit Message Format:**
```
Complete Sprint 35 Prep Task 8: fawley Constraint-Index-Diagonal + Forcing Design

Re-confirmed the gap (max|stat_bq| 473 -> 18.468) and the H-b finding (MS-5 @ 4399.557
with the residual closed; LP opt 2899.25). Characterized the constraint-index diagonal
as a predicate, distinguished from the #1049 guard's opposite orientation. Designed the
guard placement with a precedence argument against each existing sameas path. Defined
the leak-free requirement operationally (no mbal change; 1-D core byte-identical) with
the 2-D regression cohort. Specified the /tmp control requiring max|stat_bq| -> 0, not
the 96% partial. Excluded the +Solve from P3's in-sprint scope (H-b -> forcing).

## Deliverables
- docs/planning/EPIC_4/SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 3.1, 3.2, 3.3, 3.4 verified
- PREP_PLAN.md: Task 8 -> COMPLETE
- CHANGELOG.md: Task 8 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint35-task8
gh pr create --base main --title "Complete Sprint 35 Prep Task 8: fawley Constraint-Index-Diagonal + Forcing Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (any `/tmp` control edits stayed in `/tmp`)
- [x] The gap and the H-b finding re-confirmed with their exact figures
- [x] The diagonal characterized as a predicate and distinguished from #1049
- [x] Leak-free requirement stated operationally with the regression cohort enumerated
- [x] `/tmp` control requires `max|stat_bq| → 0`, not the 96% partial
- [x] The +Solve explicitly excluded from P3's in-sprint scope (H-b)
- [x] Unknowns 3.1, 3.2, 3.3, 3.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 8 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 9 Prompt: camcge Dual-Consistent Walras Design (Epic 5) + rocket PATH-Consultation Submission Plan (Priority 5)

**Branch:** Create a new branch named `planning/sprint35-task9` from `main`

**Priority:** Medium (3–4 hours) — immediately dispatchable (depends only on the completed Task 1)

**Objective:** Specify the camcge dual-consistent Walras redefinition as an Epic-5 `/tmp` prototype with an MS-1 gate, and produce the submission plan that delivers the FINALIZED rocket PATH-consultation input to the **Sprint-36** consultation.

**Unknowns Verified:** 5.1 (the Walras MS-1 `/tmp` gate + fallback), 5.2 (detector scope), 5.3 (the rocket submission, retargeted to Sprint 36), 6.3 (the Case-c family documented-non-convex status + the sign-flip BAN)

**Why this task matters:** P5 is the sprint's explicitly *non-KPI* priority — camcge is Epic-5-scoped and rocket is a hand-off — so its prep value is in preventing two specific failure modes. camcge has consumed budget in three sprints against a target the banked price-pin variant demonstrably does not reach, so the Epic-5 gate and its fallback must both be crisp. And the rocket submission carries a **renumbering hazard**: the input was authored for "the Sprint-35 consultation" and the consultation is now **Sprint 36**.

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_35/PREP_PLAN.md` §Task 9
- `docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md` §Unknowns 5.1, 5.2, 5.3, 6.3
- `docs/planning/EPIC_4/SPRINT_34/DAY10_PROGRESS_NOTES.md` (the detector cohort confirmed live: camcge cold **MS-4** @ omega **191.7346**; irscge/lrgcge/moncge/stdcge cold **MS-1**) + `SPRINT_34/CAMCGE_ROCKET_PLAN.md`
- `docs/planning/EPIC_4/SPRINT_33/CAMCGE_WALRAS_DESIGN.md` + `SPRINT_32/CAMCGE_STAT_MPS_WALRAS_DESIGN.md` + `SPRINT_32/CAMCGE_WALRAS_REPLAN.md` + `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md`
- `docs/planning/EPIC_4/SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` (the FINALIZED input) + `SPRINT_33/ROCKET_CASEC_FORCING_PLAN.md` + `SPRINT_30/NONCONVEX_FORCING_SURVEY.md` §4
- `docs/planning/EPIC_4/SPRINT_32/CASE_C_CLASSIFIER_DESIGN.md` + `docs/research/convexity_detection.md` + `scripts/diagnostics/kkt_residual.py` (`case_c_objdef`)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 36 (Weeks 37–38): PATH Author Consultation & Solution Forcing" — **the consultation sprint is now 36, not 35**

**Tasks to Complete:**

1. **Specify the full dual-consistent Walras redefinition** — keep every market-clearing row, add the consumption-weighted numéraire, and redefine the redundant market's dual via Walras' law so the reduced system is full-rank while the multiplier stays available. Write it as emittable GAMS and confirm the MCP stays square.
2. **Define the Epic-5 `/tmp` gate** — the prototype must reach **MS-1**, explicitly distinguished from the price-pin variant's correct-primal-at-MS-4 result (omega 191.7346), with `modelstat` asserted and the four INFES rows (`gdp`, `depreq`, `hhsaveq`, `gruse`) tracked.
3. **Define the acceptable fallback finding** — the per-model-numéraire Epic-5 result, so a non-MS-1 outcome is a documented deliverable rather than a failure.
4. **Re-confirm the degeneracy-detector scope** — S1∧S2∧S3 fires only on camcge; the four CGE siblings stay cold MS-1 (the false-positive guard). Check whether the S34 P4 bound-transfer altered any sibling's inputs.
5. **Write the rocket submission plan** — recipients, the artifact bundle (the FINALIZED input + the reproducible case + the `--force` scaffold + the ruled-out-lever survey), the response-tracking mechanism, and — explicitly — that the destination is the **Sprint-36** "PATH Author Consultation & Solution Forcing" sprint. **Grep the banked input for stale "Sprint 35" references and flag each for update at submission time.**
6. **Restate the standing BANs** — the rocket Case-c objective-gradient sign flip stays BANNED (control-refuted 4×); no re-litigation. Confirm the Case-c family (cesam, lnts, hhfair, the CGE cluster) stays documented non-convex under `case_c_objdef` with clean residuals at the NLP point (Unknown 6.3).
7. Write `docs/planning/EPIC_4/SPRINT_35/CAMCGE_ROCKET_PLAN.md`.

**Deliverables (from PREP_PLAN.md §Task 9):**

- `docs/planning/EPIC_4/SPRINT_35/CAMCGE_ROCKET_PLAN.md`
- The full dual-consistent Walras redefinition specification
- The Epic-5 `/tmp` MS-1 gate with `modelstat` asserted and the INFES rows tracked
- The per-model-numéraire fallback defined as an acceptable Epic-5 finding
- The degeneracy-detector scope re-confirmation (fires only camcge; siblings cold MS-1)
- The rocket submission plan targeting the **Sprint-36** consultation, with stale "Sprint 35" references flagged
- The restated Case-c sign-flip BAN
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.1, 5.2, 5.3, 6.3

**Known Unknowns Updates:** For Unknowns 5.1, 5.2, 5.3, 6.3, replace each `🔍 Status: INCOMPLETE` stub with the verification block (**Status** ✅ VERIFIED / ❌ WRONG, **Verified by** Task 9, **Date**, **Findings**, **Evidence**, **Decision**). For **5.1**, if the `/tmp` prototype is not built in prep, mark it DESIGN-SPECIFIED — the MS-1 gate is an in-sprint executed result.

**PREP_PLAN.md Updates:** In §Task 9: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria, including the "Unknowns 5.1, 5.2, 5.3, 6.3 verified and updated in `KNOWN_UNKNOWNS.md`" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 35 Preparation`, prepend:
```markdown
- **Prep Task 9 COMPLETE (YYYY-MM-DD):** camcge dual-consistent Walras design (Epic 5) + the rocket PATH-consultation submission plan (P5 — the sprint's explicitly non-KPI priority). Specified the **full Walras-law dual redefinition** (every market-clearing row kept + the consumption-weighted numéraire + the redundant market's dual redefined so the reduced system is full-rank while the multiplier stays available) as emittable GAMS with the MCP square. **Defined the Epic-5 gate as MS-1**, explicitly distinguished from the banked price-pin variant's correct-primal-at-**MS-4** result (omega 191.7346, INFES on `gdp`/`depreq`/`hhsaveq`/`gruse`), with `modelstat` asserted — and defined the **per-model-numéraire fallback as an acceptable Epic-5 finding**, so a non-MS-1 outcome is a deliverable rather than a failure. Re-confirmed the S1∧S2∧S3 detector scope (fires **only** on camcge; irscge/lrgcge/moncge/stdcge stay cold MS-1 — the false-positive guard holds). Wrote the **rocket submission plan targeting the Sprint-36 consultation** (recipients, artifact bundle, response tracking), flagging every stale "Sprint 35" reference in the banked FINALIZED input for update at submission time. Restated the Case-c sign-flip **BAN** (control-refuted 4×) and re-confirmed the Case-c family as documented non-convex under `case_c_objdef`. camcge is explicitly excluded from the in-sprint Solve commitment. Verified Unknowns 5.1, 5.2, 5.3, 6.3. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only design task — the quality gate is not required unless you touched Python.

**Commit Message Format:**
```
Complete Sprint 35 Prep Task 9: camcge Walras (Epic 5) + rocket PATH Submission Plan

Specified the full Walras-law dual redefinition as emittable GAMS with the MCP square.
Defined the Epic-5 gate as MS-1, distinguished from the price-pin variant's
correct-primal-at-MS-4 result, plus the per-model-numeraire fallback as an acceptable
finding. Re-confirmed the degeneracy detector fires only on camcge. Wrote the rocket
submission plan targeting the Sprint-36 consultation, flagging stale "Sprint 35"
references in the banked input. Restated the Case-c sign-flip BAN.

## Deliverables
- docs/planning/EPIC_4/SPRINT_35/CAMCGE_ROCKET_PLAN.md
- KNOWN_UNKNOWNS.md: Unknowns 5.1, 5.2, 5.3, 6.3 verified
- PREP_PLAN.md: Task 9 -> COMPLETE
- CHANGELOG.md: Task 9 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint35-task9
gh pr create --base main --title "Complete Sprint 35 Prep Task 9: camcge Walras (Epic 5) + rocket PATH Submission Plan" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required
- [x] The Epic-5 gate stated as MS-1, explicitly distinguished from the price-pin MS-4 result
- [x] The per-model-numéraire fallback defined as a successful Epic-5 outcome
- [x] The rocket submission plan targets **Sprint 36**, with stale "Sprint 35" references flagged
- [x] The Case-c sign-flip BAN restated with no re-litigation path
- [x] Unknowns 5.1, 5.2, 5.3, 6.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 9 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 10 Prompt: Author Phase 0 Acceptance Gates for the Sprint-35 Tracks (PR20 + PR24 + PR27)

**Branch:** Create a new branch named `planning/sprint35-task10` from `main`

**Priority:** Critical (4–6 hours) — **on the critical path**

**Dependencies:** Tasks 4, 5, 6, 7, 8, 9 must be complete (this task consolidates their `/tmp` controls).

**Objective:** Consolidate the per-track `/tmp` controls from Tasks 4–9 into a single `PHASE_0_ACCEPTANCE_GATES.md` — one gate per track, each with a measurable PROCEED/REPLAN criterion evaluated **before** any `src/` change, and each asserting `modelstat` wherever a solve result is read.

**Unknowns Verified:** 1.2, 2.2, 3.1, 4.3, 5.1 (each **contributes** via the gate design — the primary owner of each remains its per-track design task)

**Why this task matters:** This is the discipline that produced Sprint 32/33/34's defining outcome — **zero broken code shipped across three sprints of deep architectural work**. It is also the guard against the specific measurement error that has bitten before (reading an objective off a solve without asserting `modelstat` — the S31 `x.up=inf` error that read the embedded LP and produced 34 spurious unmatched-var errors).

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_35/PREP_PLAN.md` §Task 10
- `docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md` §Unknowns 1.2, 2.2, 3.1, 4.3, 5.1
- The completed design docs: `MINE_DUAL_ARCHITECTURE_DESIGN.md` (Task 6) · `SARF_SYMBOLIC_EMIT_DESIGN.md` (Task 7) · `FAWLEY_DIAGONAL_DESIGN.md` (Task 8) · `GANGES_149_PRODUCT_RULE_ANALYSIS.md` (Task 4) · `GANGES_RECOVERY_DESIGN.md` (Task 5) · `CAMCGE_ROCKET_PLAN.md` (Task 9) · `TOOLING_AND_BACKLOG_ANALYSIS.md` (Task 3) · `BASELINE_METRICS.md` (Task 2)
- `docs/planning/EPIC_4/SPRINT_34/PHASE_0_ACCEPTANCE_GATES.md` (the template) + `SPRINT_33/` and `SPRINT_32/PHASE_0_ACCEPTANCE_GATES.md` (the precedents)
- `scripts/diagnostics/kkt_residual.py` · `scripts/gamslib/run_full_test.py` (`--resolve-changed --since-commit <S34-close>`) · `scripts/diagnostics/check_presolve_divergence.py` · `scripts/sprint_audit/check_golden_staleness.py`

**Tasks to Complete:**

1. **P1 (mine) gate** — the reformulation must drive the warm residual → 0 at **all** bound-active `stat_x` rows AND leave interior rows unchanged at 0 in a `/tmp` control, **then** reach cold/presolve **MS-1 @ 17500**; `modelstat` asserted at every read; `x.up=inf` **BANNED**. State PROCEED/REPLAN. If Task 6 returned a REPLAN recommendation, record the gate as pre-refuted and the exit as taken.
2. **P2 (sarf) gate** — the re-emit must be **O(active = 398), not O(369K)**: timed `sarf_mcp.gms` emission in seconds (current failure > 75s); `stat_task` verified against the banked 7-term derivation; atomic landing; byte-stable goldens for the other 141 models; determinism ×3; full-corpus `--resolve-changed`. **This is a timing gate, not a residual gate.**
3. **P3 (fawley) gate** — the generalization must drive `max|stat_bq| → 0` (not 96%, not merely 473 → 18.468) in a `/tmp` control; `--resolve-changed --since-commit <S34-close>` GO with **no mbal-term change** and no 1-D polygon/ps2/ps3 regression; the +Solve explicitly out of scope (H-b → forcing).
4. **P4 (ganges/gangesx) gate** — **per-root**: each of `$141`/`$145`/`$149` individually `--resolve-changed`-gated; the `$149` correction verified against Task 4's hand-derived `stat_pc` cross-term in a `/tmp` control **before** `src/`; the slow-emit CGE goldens regenerated per Task 3's budget + determinism ×3; and the **per-model** protocol (ganges and gangesx independently: compile → residual-code count → solve → bucket → match) encoded into the gate so it cannot be skipped under time pressure.
5. **P5 (camcge) gate** — the Walras `/tmp` prototype at **MS-1** with `modelstat` asserted (the Epic-5 gate), plus the per-model-numéraire fallback as the documented alternative outcome; rocket's submission has no solve gate (it is a hand-off).
6. **Add the cross-cutting gates** — determinism ×3 (`PYTHONHASHSEED` {0,1,42}, PR12); the golden-staleness check (PR26); the presolve-divergence detector; and the **"no bucket → no `src/`"** shipping rule with the S34 P4 exception criteria (fast, regenerable goldens + `--resolve-changed` GO) written out, since P4 is *expected* to invoke it.
7. Write `docs/planning/EPIC_4/SPRINT_35/PHASE_0_ACCEPTANCE_GATES.md`.

**Deliverables (from PREP_PLAN.md §Task 10):**

- `docs/planning/EPIC_4/SPRINT_35/PHASE_0_ACCEPTANCE_GATES.md` with one gate per track (P1–P5)
- Each gate: the control to run, the measurable threshold, the PROCEED/REPLAN criterion, and the `modelstat` assertion requirement
- The P2 timing gate (O(active = 398), seconds not > 75s) and the P4 per-root gate sequence stated as first-class, distinct gate shapes
- The cross-cutting gates: determinism ×3 (PR12), golden-staleness (PR26), presolve-divergence, `--resolve-changed` (anchor = S34 close)
- The "no bucket → no `src/`" rule with the S34-P4 exception criteria written out for P4's expected use
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.2, 2.2, 3.1, 4.3, 5.1

**Known Unknowns Updates:** For Unknowns 1.2, 2.2, 3.1, 4.3, 5.1, **append a Task-10 contribution block** to each (do **not** overwrite the per-track design task's primary block): **Status** (contribution), **Verified by** Task 10, **Date**, **Findings** (the gate's feasibility + measurable threshold), **Evidence**, **Decision** (the PROCEED/REPLAN criterion as authored).

**PREP_PLAN.md Updates:** In §Task 10: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria, including the "Unknowns 1.2, 2.2, 3.1, 4.3, 5.1 verified and updated in `KNOWN_UNKNOWNS.md`" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 35 Preparation`, prepend:
```markdown
- **Prep Task 10 COMPLETE (YYYY-MM-DD):** Phase-0 acceptance gates authored for the Sprint-35 tracks (PR20 + PR24 + PR27) — one gate per track with a measurable PROCEED/REPLAN criterion evaluated **before** any `src/` change. **P1 mine:** warm residual → 0 at *all* bound-active rows + interior rows unchanged, **then** cold/presolve **MS-1 @ 17500** (`modelstat` asserted; `x.up=inf` BANNED). **P2 sarf:** a **timing** gate — O(active = 398), not O(369K); seconds, not the > 75s failure; `stat_task` checked against the banked 7-term derivation; atomic landing + 141 byte-stable goldens + determinism ×3 + full-corpus `--resolve-changed`. **P3 fawley:** `max|stat_bq| → 0` (not the 96% partial) with **no mbal-term change** and no 1-D regression; the +Solve explicitly out of scope (H-b). **P4 ganges/gangesx:** a **per-root** gate sequence (`$141`/`$145`/`$149` each individually `--resolve-changed`-gated; the `$149` correction checked against the hand-derived cross-term in a `/tmp` control before `src/`; the slow-emit goldens regenerated per Task 3's budget) with the **per-model** verification protocol encoded so it cannot be skipped under time pressure. **P5 camcge:** the Walras `/tmp` prototype at MS-1 with the numéraire fallback; rocket has no solve gate. Cross-cutting gates added: determinism ×3 (PR12), golden-staleness (PR26), presolve-divergence, `--resolve-changed` against the **S34-close** anchor, and the **"no bucket → no `src/`"** rule with the S34-P4 exception criteria written out for P4's expected use. Verified Unknowns 1.2, 2.2, 3.1, 4.3, 5.1 (gate-design contributions). Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — the quality gate is not required unless you touched Python.

**Commit Message Format:**
```
Complete Sprint 35 Prep Task 10: Phase 0 Acceptance Gates

One gate per track (P1-P5), each with a measurable PROCEED/REPLAN criterion evaluated
before any src/ change and modelstat asserted wherever a solve is read. P1 cold-MS-1 @
17500 (not the warm residual). P2 is a timing gate: O(active=398), not O(369K). P3
requires max|stat_bq| -> 0 with no mbal change. P4 is a per-root sequence with the
per-model protocol encoded so it cannot be skipped. P5 is the Walras MS-1 /tmp gate.
Cross-cutting: determinism x3, golden-staleness, presolve-divergence,
--resolve-changed against the S34-close anchor, and "no bucket -> no src/" with the
S34-P4 exception criteria written out.

## Deliverables
- docs/planning/EPIC_4/SPRINT_35/PHASE_0_ACCEPTANCE_GATES.md
- KNOWN_UNKNOWNS.md: Unknowns 1.2, 2.2, 3.1, 4.3, 5.1 (gate contributions)
- PREP_PLAN.md: Task 10 -> COMPLETE
- CHANGELOG.md: Task 10 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint35-task10
gh pr create --base main --title "Complete Sprint 35 Prep Task 10: Phase 0 Acceptance Gates" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required
- [x] A gate authored for each of P1–P5 with a measurable PROCEED/REPLAN criterion
- [x] Every gate that reads a solve result requires `modelstat` to be asserted
- [x] P2 is a **timing** gate and P4 is a **per-root** sequence — not generic residual gates
- [x] Standing BANs restated (`x.up=inf`; Case-c sign flip)
- [x] "No bucket → no `src/`" with the S34-P4 exception criteria written out for P4
- [x] Unknowns 1.2, 2.2, 3.1, 4.3, 5.1 updated with Task-10 contribution blocks (primaries preserved)
- [x] Task 10 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 11 Prompt: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment + Honest KPI Projection (PR16)

**Branch:** Create a new branch named `planning/sprint35-task11` from `main`

**Priority:** High (4–6 hours) — **on the critical path**

**Dependencies:** Tasks 5, 6, 7, 8, 10 must be complete.

**Objective:** Apply the PR16 hypothesis-validation methodology to the four deep/new tracks — P1 (mine dual architecture), P2 (sarf re-architecture), P3 (fawley gate-leak / H-b), P4 (ganges `$149` depth) — pinning per-track REPLAN priors with their refuting evidence, the freed-budget reallocation, the front-load ordering, and the honest projection of which KPI buckets can actually move.

**Unknowns Verified:** 1.5 (mine's fourth-carry disposition), 2.2 (sarf's timeout re-trigger — contributes), 3.2 (fawley's gate-leak risk — contributes), 4.5 (whether the golden-regen budget makes P4 shippable in-sprint — contributes)

**Why this task matters:** This projection has been accurate to the bucket for two consecutive sprints, and naming the modal outcome up front is what has kept those sprints focused on de-risking and banking rather than forcing a bad ship. Sprint 35 needs it more than either predecessor: mine, sarf and fawley have between them consumed roughly half of three sprints' budget and moved **zero** buckets, while the failure-cohort track produced the only genuine move in that window. An honest assessment likely concludes that **P4 is the sprint's designated best shot** and should be scheduled accordingly.

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_35/PREP_PLAN.md` §Task 11
- `docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md` §Unknowns 1.5, 2.2, 3.2, 4.5
- The completed design docs (Tasks 5–8) + `PHASE_0_ACCEPTANCE_GATES.md` (Task 10) + `TOOLING_AND_BACKLOG_ANALYSIS.md` (Task 3)
- `docs/planning/EPIC_4/SPRINT_34/REPLAN_RISK_ASSESSMENT.md` (the template — its modal-flat projection was borne out exactly, 0 bucket moves) + `SPRINT_33/REPLAN_RISK_ASSESSMENT.md` + `SPRINT_34/SPRINT_RETROSPECTIVE.md` §§1/3
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 35" (Risk Level **HIGH**; the per-priority REPLAN exits; Estimated Effort 92–134h)

**Tasks to Complete:**

1. **Assess each of P1/P2/P3/P4 for REPLAN probability**, naming the specific evidence that would refute it and the earliest day that evidence surfaces (**Day-5 checkpoint measurability is the requirement**). Weigh the carry count explicitly: mine ×4, sarf ×3, fawley ×3.
2. **Assess P5** (camcge Epic-5 deferral; rocket Sprint-36 submission) — both a-priori non-movers in-sprint.
3. **Pin the REPLAN exits and the freed-budget reallocation** — for each track, where its budget goes when it exits (→ P4 first, then P6/P7).
4. **Author the honest KPI projection** — the in-sprint Solve movers ({P4 ganges·gangesx firm-ish, P1 mine conditional}; **P3's +Solve is a forcing hand-off, not in-sprint**; camcge is Epic-5); Translate +1 via P2; the genuine floor (75 → ≥ 76 needs a **cold-emit** mover — P4 or P1 or a fawley cold match, *not* a warm-start fix, which yields 0 by definition); path_syntax_error −2 via P4; the stretch (Solve ≥ 112); and the modal outcome.
5. **Recommend the front-load ordering** — which tracks run early so their REPLANs surface by the Day-5 checkpoint. Given the three-sprint record, **argue explicitly for where P4 sits relative to P1/P2** rather than inheriting the previous sprints' ordering by default. Factor in Task 3's golden-regeneration window (an overnight slot constrains how late P4 can start).
6. **State the budget arithmetic** — the per-priority sizings (P1 18–24h, P2 20–28h, P3 12–18h, P4 14–20h, P5 10–16h, P6 8–14h, P7 6–10h, retest 4h = 92–134h) against the 168h cap, and what the reallocation looks like under early REPLANs.
7. Write `docs/planning/EPIC_4/SPRINT_35/REPLAN_RISK_ASSESSMENT.md`.

**Deliverables (from PREP_PLAN.md §Task 11):**

- `docs/planning/EPIC_4/SPRINT_35/REPLAN_RISK_ASSESSMENT.md`
- A per-track REPLAN prior (P1/P2/P3/P4) with the refuting evidence and its earliest surfacing day, weighing the carry counts
- The P5 disposition assessment (camcge Epic-5; rocket Sprint-36)
- The pinned REPLAN exits + freed-budget reallocation chain (→ P4, then P6/P7)
- The honest KPI projection: firm vs conditional movers, the genuine-floor conditionality, the stretch (Solve ≥ 112), and the modal outcome
- The front-load ordering recommendation, **argued** from the three-sprint record rather than inherited
- The budget arithmetic (92–134h work-items vs the 168h cap) including the early-REPLAN reallocation case
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.5, 2.2, 3.2, 4.5

**Known Unknowns Updates:** For Unknowns 1.5, 2.2, 3.2, 4.5, replace or append (1.5 is Task 11's primary alongside Task 6; 2.2/3.2/4.5 get **contribution** blocks that preserve their primary owners' findings) with: **Status**, **Verified by** Task 11, **Date**, **Findings** (the REPLAN prior + its refuting evidence + the earliest surfacing day), **Evidence**, **Decision** (the exit + the reallocation target + the front-load position).

**PREP_PLAN.md Updates:** In §Task 11: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria, including the "Unknowns 1.5, 2.2, 3.2, 4.5 verified and updated in `KNOWN_UNKNOWNS.md`" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 35 Preparation`, prepend:
```markdown
- **Prep Task 11 COMPLETE (YYYY-MM-DD):** REPLAN-prone track risk assessment + the honest KPI projection (PR16). Assigned a per-track REPLAN prior with its refuting evidence and earliest surfacing day for P1 (mine dual architecture), P2 (sarf re-architecture), P3 (fawley gate-leak / H-b) and P4 (the `$149` AD depth), **weighing the carry counts explicitly** — mine ×4, sarf ×3, fawley ×3, which between them have consumed roughly half of three sprints' budget for **zero** bucket moves, while the failure-cohort track produced the only genuine move in that window. Assessed P5 as an a-priori non-mover (camcge Epic-5; rocket → Sprint 36). Pinned the REPLAN exits + the freed-budget reallocation chain (→ **P4 first**, then P6/P7). Authored the honest KPI projection — firm vs conditional Solve movers, the **genuine-floor conditionality** (75 → ≥ 76 needs a *cold-emit* mover; a warm-start fix yields 0 by definition), Translate +1 via P2, path_syntax_error −2 via P4, the stretch (Solve ≥ 112), and the modal outcome. **Recommended the front-load ordering and argued P4's position from the three-sprint record** rather than inheriting the prior sprints' layout, factoring in Task 3's golden-regeneration window. Stated the budget arithmetic (92–134h work-items vs the 168h cap) with the early-REPLAN reallocation case. Verified Unknowns 1.5, 2.2, 3.2, 4.5. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — the quality gate is not required unless you touched Python.

**Commit Message Format:**
```
Complete Sprint 35 Prep Task 11: REPLAN Risk Assessment + Honest KPI Projection

Per-track REPLAN priors with refuting evidence and earliest surfacing day for
P1/P2/P3/P4, weighing the carry counts (mine x4, sarf x3, fawley x3 - zero bucket moves
across three sprints, while the failure-cohort track produced the only genuine move).
P5 assessed as an a-priori non-mover. REPLAN exits + freed-budget chain pinned (-> P4
first, then P6/P7). Honest KPI projection authored, including the genuine-floor
conditionality (only a cold-emit mover lifts it). Front-load ordering recommended and
argued from the three-sprint record, factoring in the golden-regeneration window.

## Deliverables
- docs/planning/EPIC_4/SPRINT_35/REPLAN_RISK_ASSESSMENT.md
- KNOWN_UNKNOWNS.md: Unknowns 1.5, 2.2, 3.2, 4.5 verified
- PREP_PLAN.md: Task 11 -> COMPLETE
- CHANGELOG.md: Task 11 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint35-task11
gh pr create --base main --title "Complete Sprint 35 Prep Task 11: REPLAN Risk Assessment + Honest KPI Projection" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required
- [x] P1/P2/P3/P4 each assigned a REPLAN prior with refuting evidence and earliest surfacing day
- [x] Carry counts (mine ×4, sarf ×3, fawley ×3) weighed explicitly in the priors
- [x] REPLAN exits + freed-budget reallocation chain pinned
- [x] The genuine-floor conditionality stated (a warm-start fix yields 0 floor by definition)
- [x] Front-load ordering **argued**, with P4's position justified from the three-sprint record
- [x] Budget arithmetic stated (92–134h vs the 168h cap) with the early-REPLAN case
- [x] Unknowns 1.5, 2.2, 3.2, 4.5 verified in KNOWN_UNKNOWNS.md
- [x] Task 11 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 12 Prompt: Plan Sprint 35 Detailed Schedule

**Branch:** Create a new branch named `planning/sprint35-task12` from `main`

**Priority:** Critical (3–4 hours) — **final integration; on the critical path**

**Dependencies:** Tasks 1–11 must all be complete.

**Objective:** Produce the detailed 14-day Sprint 35 schedule (Day 0 setup + Days 1–13 execution) with pasteable day-by-day prompts, front-loading per Task 11's recommendation so every deep-track REPLAN surfaces by the Day-5 checkpoint, at ≤ 12 hours/day within the 168-hour budget (92–134h work-items).

**Unknowns Verified:** None directly — **this task integrates all verified unknowns** into the schedule and makes the **GO/NO-GO determination**. It must confirm that every Critical/High unknown is resolved, flagged as a Day-0 blocker, or explicitly labelled DESIGN-SPECIFIED (an in-sprint execution gate by design).

**Why this task matters:** Two scheduling decisions carry most of the sprint's expected value: **where P4 sits** (Task 11's projection says it is the designated best shot, which argues for an early slot rather than the traditional back-half failure-cohort placement), and **where the slow-emit golden regeneration runs** (Task 3's measurement determines whether it fits a normal day or needs a dedicated overnight window — getting this wrong is precisely what banked S34's verified fix).

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_35/PREP_PLAN.md` §Task 12 + all of Tasks 2–11's deliverables
- `docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md` (all 29 unknowns — check every Critical/High status)
- `docs/planning/EPIC_4/SPRINT_35/REPLAN_RISK_ASSESSMENT.md` (Task 11 — the front-load recommendation) + `TOOLING_AND_BACKLOG_ANALYSIS.md` (Task 3 — the golden-regen window) + `PHASE_0_ACCEPTANCE_GATES.md` (Task 10)
- `docs/planning/EPIC_4/SPRINT_34/PLAN.md` + `SPRINT_34/prompts/PLAN_PROMPTS.md` (the format precedents)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 35" (Estimated Effort 92–134h; heaviest day ~11h; the 14-day / ≤ 12h-per-day budget)
- The per-day workflow: branch → work → quality gate ONLY if `*.py` changed → commit → push → PR → user merges → "checkout main and pull"; docs/DB/golden-only PRs skip the gate. Branch naming: `planning/sprint35-dayN-<slug>`.

**Tasks to Complete:**

1. **Lay out Day 0** — baseline confirmation (Task 2) + the per-track control re-confirms (mine boundary, the sarf O(active) timing probe, the fawley residual, the ganges per-model compile, the camcge detector) + the GO/NO-GO for Day 1.
2. **Place the tracks per Task 11's front-load recommendation** — with **P4's slot justified explicitly** (early if it is the designated best shot) and the deep tracks positioned so their REPLANs surface by the Day-5 checkpoint.
3. **Schedule the slow-emit golden regeneration** per Task 3's measured budget — as an in-day step or a dedicated window, with the determinism-×3 and follow-on `--resolve-changed` costs accounted.
4. **Place the checkpoints** — Day 5 (PROCEED/REPLAN + freed-budget reallocation) and Day 10; the Day-13 final retest under ≥ 3 `PYTHONHASHSEED` + closeout.
5. **Write the day-by-day prompts** — one per day, pasteable verbatim, each referencing its Phase-0 gate, its design doc, and its REPLAN exit.
6. **Verify the budget** — ≤ 12h/day, ≤ 168h total, heaviest ~11h; confirm the per-priority sizings sum to 92–134h.
7. **Confirm all Known Unknowns are resolved** — any Critical/High unknown still `🔍 INCOMPLETE` is either flagged as a **Day-0 blocker** or explicitly labelled **DESIGN-SPECIFIED**. Make the GO/NO-GO call.
8. Write `docs/planning/EPIC_4/SPRINT_35/PLAN.md` + `docs/planning/EPIC_4/SPRINT_35/prompts/PLAN_PROMPTS.md`.

**Deliverables (from PREP_PLAN.md §Task 12):**

- `docs/planning/EPIC_4/SPRINT_35/PLAN.md` — the 14-day schedule (Day 0 + Days 1–13) with the front-load, the checkpoints, the golden-regeneration window, and the budget verification
- `docs/planning/EPIC_4/SPRINT_35/prompts/PLAN_PROMPTS.md` — one pasteable prompt per day, each referencing its Phase-0 gate + design doc + REPLAN exit
- The explicit justification for P4's scheduled position (per Task 11's projection)
- The budget confirmation (≤ 12h/day, ≤ 168h total, 92–134h work-items, heaviest ~11h)
- The Known-Unknowns resolution status + the GO/NO-GO determination

**Known Unknowns Updates:** This task does not verify individual unknowns. Instead, update the **Next Steps** section and the **Document Status** footer of `KNOWN_UNKNOWNS.md` with the pre-Day-1 status: how many are resolved, which (if any) remain `🔍 INCOMPLETE` and why (DESIGN-SPECIFIED in-sprint gates vs genuine Day-0 blockers), and the **GO / NO-GO for Day 0** verdict — mirroring the Sprint-34 close-out of that section.

**PREP_PLAN.md Updates:** In §Task 12: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria. Also update the document footer `**Status:**` line to reflect that prep is complete (all 12 tasks) and check off the remaining "Success Criteria for Sprint 35 Prep" items.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 35 Preparation`, prepend:
```markdown
- **Prep Task 12 COMPLETE (YYYY-MM-DD) — Sprint 35 prep COMPLETE (Tasks 1–12); GO/NO-GO for Day 0 determined.** Authored the 14-day schedule (`PLAN.md`, Day 0 + Days 1–13) + the per-day prompts (`prompts/PLAN_PROMPTS.md`, one pasteable prompt per day, each citing its Phase-0 gate + design doc + REPLAN exit). **Day 0** = baseline confirm against the S34-close anchor + the per-track control probes (mine boundary, the sarf O(active) timing probe, the fawley residual, the ganges per-model compile, the camcge detector). **Front-load** per Task 11's argued recommendation, with **P4's slot justified explicitly** rather than inherited — the deep tracks positioned so every REPLAN surfaces by the **Day-5 checkpoint**, and the slow-emit golden-regeneration window placed per Task 3's *measured* budget (the constraint that banked S34's verified fix). Checkpoints at Day 5 (PROCEED/REPLAN + freed-budget reallocation) and Day 10; Day-13 final retest under ≥ 3 `PYTHONHASHSEED` + closeout. **Budget verified:** per-priority work-items P1 [18–24h] + P2 [20–28h] + P3 [12–18h] + P4 [14–20h] + P5 [10–16h] + P6 [8–14h] + P7 [6–10h] + retest [4h] = **92–134h**, heaviest day ~11h, no day > 12h, under the 168h cap. All 29 Known Unknowns accounted for (resolved / DESIGN-SPECIFIED in-sprint gates / Day-0 blockers) with the **GO-NO-GO verdict recorded** in `KNOWN_UNKNOWNS.md` §Next Steps and `PLAN.md`. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — the quality gate is not required unless you touched Python.

**Commit Message Format:**
```
Complete Sprint 35 Prep Task 12: Plan Sprint 35 Detailed Schedule

Authored the 14-day schedule (Day 0 + Days 1-13) with pasteable per-day prompts, each
citing its Phase-0 gate, design doc and REPLAN exit. Front-loaded per Task 11's argued
recommendation with P4's slot justified explicitly; the slow-emit golden-regeneration
window placed per Task 3's measured budget. Checkpoints at Day 5 and Day 10; Day-13
final retest under >=3 PYTHONHASHSEED. Budget verified: 92-134h work-items, heaviest
~11h, no day > 12h, under the 168h cap. All 29 Known Unknowns accounted for and the
GO/NO-GO for Day 0 recorded. Sprint 35 prep COMPLETE (Tasks 1-12).

## Deliverables
- docs/planning/EPIC_4/SPRINT_35/PLAN.md
- docs/planning/EPIC_4/SPRINT_35/prompts/PLAN_PROMPTS.md
- KNOWN_UNKNOWNS.md: Next Steps + Document Status updated with the GO/NO-GO verdict
- PREP_PLAN.md: Task 12 -> COMPLETE; prep status -> COMPLETE
- CHANGELOG.md: Task 12 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint35-task12
gh pr create --base main --title "Complete Sprint 35 Prep Task 12: Plan Sprint 35 Detailed Schedule" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required
- [x] Day 0 + Days 1–13 all present as pasteable prompts (14 day headers)
- [x] P4's scheduled position explicitly justified rather than inherited from prior sprints
- [x] The slow-emit golden-regeneration window scheduled per Task 3's measured budget
- [x] Checkpoints placed (Day 5 PROCEED/REPLAN + reallocation, Day 10, final retest Day 13)
- [x] Budget verified (≤ 12h/day, ≤ 168h, 92–134h work-items, heaviest ~11h)
- [x] All Critical/High unknowns resolved, flagged as Day-0 blockers, or labelled DESIGN-SPECIFIED
- [x] GO/NO-GO for Day 0 recorded in KNOWN_UNKNOWNS.md and PLAN.md
- [x] Task 12 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

**Document Created:** 2026-07-23
**Owner:** Sprint 35 Planning Team
**Covers:** Prep Tasks 2–12 (Task 1 ✅ COMPLETE — see `docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md`)

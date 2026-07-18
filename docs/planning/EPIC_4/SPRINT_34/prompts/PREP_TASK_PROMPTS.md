# Sprint 34 Prep Task Execution Prompts

Self-contained prompts for Sprint 34 Prep Tasks 2–11. Each prompt can be copy-pasted into a new conversation to execute one prep task end-to-end, including the Known Unknowns verification updates, the `PREP_PLAN.md` / `CHANGELOG.md` updates, the quality gate, the commit, and the Pull Request.

**Usage:**

1. Pick a task prompt below.
2. Paste it into a new conversation.
3. The agent creates the branch (`planning/sprint34-task<N>`), does the work, verifies its Known Unknowns, runs the quality gate (only if it touched Python), commits, pushes, and opens a PR.
4. Wait for reviewer comments on the PR.

Task 1 (Create Sprint 34 Known Unknowns List) is already ✅ COMPLETE — no prompt needed (see `docs/planning/EPIC_4/SPRINT_34/KNOWN_UNKNOWNS.md`).

**Dispatch order** (per the Prep Task Overview dependencies + the critical path in `docs/planning/EPIC_4/SPRINT_34/PREP_PLAN.md`; Task 1 is done, so tasks depending only on it — or on nothing — are immediately dispatchable):

- **Immediately dispatchable:** Task 2 (no dependencies); Task 7 (needs only the completed Task 1)
- **After Task 2:** Task 3 + Task 4 + Task 5 + Task 6 (the three deep-track designs + the NEW bound-transfer track need Tasks 1, 2)
- **After Tasks 1 + 3 + 4 + 5 + 6 + 7:** Task 8 (the Phase-0 gate authoring consumes the per-track design docs)
- **After Tasks 1 + 8:** Task 10 (the tooling-readiness + backlog analysis reuses the gates)
- **After Tasks 3 + 4 + 5 + 6 + 8:** Task 9 (the REPLAN assessment consumes the designs + the gates)
- **After all (final integration):** Task 11

**Critical path:** Task 1 → Task 3 → Task 8 → Task 9 → Task 11.

**Cross-cutting conventions for every prompt below:**

- Branch from `main`; the PR targets `main`. Branch name: `planning/sprint34-task<N>`.
- User preferences (enforce in every commit/PR): **NO `Co-Authored-By` lines** in commit messages; **NO "Generated with Claude Code"** in PR descriptions.
- Replace `YYYY-MM-DD` with the actual date at execution time.
- **The Day-0 code anchor is the S33-close SHA** (derive it with `git log --first-parent main --grep='SPRINT 33 CLOSED' --format=%H -n 1` — `--first-parent -n 1` picks the actual close merge on `main`, not an older matching closeout commit that `tail -1` would select). Unlike Sprint 33, the DB is **no longer byte-unchanged since `4cbf8bff`** — the S33 P6 sample fix changed `sample_mcp.gms` + the DB, so `4cbf8bff` is historical; use the S33-close SHA for the `--resolve-changed` baseline.
- These are **docs/design/analysis-only** prep tasks — no Python source changes are expected (the fixes/scripts they design are *built in-sprint*, not in prep; the KKT-residual harness incl. `case_c_objdef`, the presolve-divergence detector, the golden-staleness gate, the `--resolve-changed` mode, and the `--force` scaffold already exist on `main`, as does the S33 P6 `test_sample_pruned_var_l_init.py` fixture pattern). Run the quality gate before committing **only if you touched Python** — per the project's per-day workflow (quality gate only if `*.py` changed), a docs-only task skips it. If you did touch Python, `make typecheck && make lint && make format && make test` must pass.
- **PR24/PR27 discipline:** every Sprint-33 control-confirmed characterization is a Day-0-**re-confirm hypothesis**, never fact — including its *sufficiency* and its *achievable KPI bucket*. Sprint 33 *refuted* its banked fix hypothesis on every deep track before any bad ship (mine H1 proven **value-invariant** by a `/tmp` control; fawley reached **H-b** — the MCP diverges MS-5 even with the warm residual fully closed; sarf deferred as a from-scratch rebuild). Record the symptom + reproducer; frame the fix surface as a hypothesis to re-trace; gate any high-blast-radius change on a `/tmp` control experiment BEFORE the `src/` change.
- **Assert `modelstat` before reading an objective off a solve** (the Sprint-31 measurement-error lesson: relaxing `x.up=inf` produced 34 unmatched-variable errors, so the "MS-1 17500" was the embedded LP, not the MCP). The `x.up=inf` experiment is **BANNED** for mine.
- **Check the dual side** (the Sprint-30 camcge lesson): any structural transform that drops/adds rows must be verified against the KKT *dual*, not just the primal solution set.
- **The failure cohort is multi-root** (the Sprint-33 lesson): verify per-model, do not assume a single shared root (sample `$140` and ganges/gangesx `$141/$145/$149` were *different* roots).
- Every Known-Unknowns update uses the verification block: **Status** (✅ VERIFIED / ❌ WRONG), **Verified by**, **Date**, **Findings**, **Evidence**, **Decision** — replacing the `🔍 **Status:** INCOMPLETE` stub.

---

## Task 2 Prompt: Sprint 33 → Sprint 34 Day-0 Baseline + Genuine-Floor Re-Baseline (PR15 + PR17 + PR25)

**Branch:** Create a new branch named `planning/sprint34-task2` from `main`

**Priority:** Critical (3–4 hours)

**Objective:** Establish the Sprint 34 Day-0 baseline from the committed DB, confirm the per-model bucket provenance, pin the Day-0 **code anchor** (the S33-close SHA) for `--resolve-changed`, and re-confirm the PR25 genuine-vs-methodology partition (genuine floor **75**).

**Unknowns Verified:** 1.1 (Day-0 mine bucket, contributes), 3.1 (Day-0 fawley bucket, contributes), 7.2 (the PR25 genuine-floor anchor 75 + the S33-close code anchor — primary)

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_34/PREP_PLAN.md` §Task 2
- `docs/planning/EPIC_4/SPRINT_34/KNOWN_UNKNOWNS.md` §Unknowns 1.1, 3.1, 7.2
- `docs/planning/EPIC_4/SPRINT_33/BASELINE_METRICS.md` (the bucket-provenance + genuine-vs-methodology template) + `docs/planning/EPIC_4/SPRINT_33/SPRINT_LOG.md` (Solve 108 / Match 93 / genuine floor 75 / model_infeasible 7 / path_syntax_error 7 / Translate 135 / all-219 Match 96)
- `data/gamslib/gamslib_status.json` (the committed DB; changed at the S33 close by the P6 sample fix) + `scripts/gamslib/run_full_test.py` `--resolve-changed` mode + `get_candidate_models` (142-candidate definition)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 34" (the footnote-⁸ genuine-floor ramp S34 ≥ 76)

**Tasks to Complete:**

1. Derive the Day-0 code anchor (the S33-close SHA) and verify no `src/`/`scripts/` drift since — reuse the committed DB (no fresh retest) if clean:
   ```bash
   S33=$(git log --first-parent main --grep='SPRINT 33 CLOSED' --format=%H -n 1)   # --first-parent -n 1 picks the close merge on main, not an older matching commit
   [ -n "$S33" ] || { echo "ERROR: could not resolve the Sprint 33 close SHA — resolve it manually before diffing"; exit 1; }
   git diff --quiet "$S33"..HEAD -- src/ scripts/ || { echo "ERROR: src/scripts drift since the S33 close — a fresh retest is required; do NOT reuse the committed DB"; git diff --stat "$S33"..HEAD -- src/ scripts/; exit 1; }
   echo "no src/scripts drift — safe to reuse the committed DB; Day-0 code anchor = $S33"
   md5 -q data/gamslib/gamslib_status.json   # record the current DB hash (macOS; 'md5sum ...' on Linux)
   ```
2. Recompute the canonical bucket tally from the committed DB (`get_candidate_models`, 142): Parse 142 / Translate 135 / Solve 108 (cold 64 + presolve 44) / Match 93 / model_infeasible 7 / path_syntax_error 7 / all-219 Match 96. Enumerate the 7 model_infeasible + the residual path_syntax_error members by name.
3. Record per-model bucket provenance (Day-0 → expected Day-13) for every carryforward-touched model: mine, sarf, fawley (+ the MAXIMIZE cohort for P4), camcge, rocket, ganges, gangesx, agreste.
4. Re-confirm the PR25 genuine-floor anchor **75** (cold-emit-correct genuine vs presolve-methodology); identify the → ≥ 76 conversion map (mine [P1] / fawley [P3] cold-matches) + the footnote-⁸ ramp alignment; record the 142-corpus (Match 93) vs all-219 (Match 96) distinction.
5. Confirm determinism ×3 `PYTHONHASHSEED` {0,1,42} on the Day-0 emit; pin the Day-0 SHA + confirm `--resolve-changed --since-commit <S33-close SHA>` selects 0 changed at Day 0.
6. Write `docs/planning/EPIC_4/SPRINT_34/BASELINE_METRICS.md`.

**Deliverables (from PREP_PLAN.md §Task 2):**

- `docs/planning/EPIC_4/SPRINT_34/BASELINE_METRICS.md` with the 142-corpus Day-0 tally + bucket members
- The Day-0 code anchor (S33-close SHA) for `--resolve-changed`
- The PR25 genuine-vs-methodology partition (genuine floor 75) + the → ≥ 76 conversion map
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 3.1, 7.2

**Known Unknowns Updates:** For Unknowns 1.1, 3.1, 7.2 in `docs/planning/EPIC_4/SPRINT_34/KNOWN_UNKNOWNS.md`, replace the `🔍 Status: INCOMPLETE` stub with: **Status** ✅ VERIFIED (or ❌ WRONG + correction), **Verified by** Task 2, **Date**, **Findings** (the Day-0 mine/fawley buckets + the genuine-floor-75 reproduction + the S33-close anchor + the 142-vs-219 split), **Evidence** (DB recompute + partition + `git diff <S33-close>..HEAD` empty), **Decision** (the ≥ 76 conversion map). Note that the *fix-surface* aspects of 1.1/3.1 are verified by Tasks 3/5 (Task 2 verifies only their Day-0-bucket aspect); 7.2 is Task 2's primary.

**PREP_PLAN.md Updates:** In §Task 2: `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`; add `**Completed:** YYYY-MM-DD`; fill "Changes" (what was measured/authored) + "Result" (the Day-0 baseline + genuine floor 75 + the S33-close anchor + corpus scope); check off all Acceptance Criteria (`- [ ]` → `- [x]`), including the "Unknowns 1.1, 3.1, 7.2 verified" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 34 Prep`, prepend:
```markdown
- **Prep Task 2 COMPLETE (YYYY-MM-DD):** Sprint 34 Day-0 baseline = Sprint 33 close (Solve 108 / Match 93 / genuine floor 75 / model_infeasible 7 / path_syntax_error 7 / Translate 135 / all-219 Match 96). Day-0 code anchor = the S33-close SHA (the DB changed since `4cbf8bff` via the S33 P6 sample fix — `4cbf8bff` is historical); no `src/`/`scripts/` drift since the S33 close → committed DB reused, no fresh retest. Genuine floor 75 reproduced from the PR25 partition with the → ≥ 76 conversion map (mine P1 / fawley P3) + the footnote-⁸ ramp alignment; the 142-corpus (Match 93) vs all-219 (Match 96) distinction recorded. Per-carryforward-model Day-0 bucket provenance pinned; determinism ✅ ×3; `--resolve-changed --since-commit <S33-close>` confirmed (0 at Day 0). Verified Unknowns 1.1, 3.1, 7.2. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected, so the quality gate is not required (docs-only changes skip it, per the project convention). If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 34 Prep Task 2: Day-0 Baseline + Genuine-Floor Re-Baseline

Day-0 = Sprint 33 close (Solve 108 / Match 93 / genuine floor 75 / model_infeasible 7
/ path_syntax_error 7 / Translate 135 / all-219 Match 96). Day-0 code anchor = the
S33-close SHA (DB changed since 4cbf8bff via the P6 sample fix; no src/scripts drift
since the S33 close -> committed DB reused). Genuine floor 75 reproduced from the PR25
partition with the -> >=76 conversion map (mine P1 / fawley P3). 142-corpus vs all-219
distinction recorded. --resolve-changed anchor confirmed (0 at Day 0); determinism x3.

## Deliverables
- docs/planning/EPIC_4/SPRINT_34/BASELINE_METRICS.md
- KNOWN_UNKNOWNS.md: Unknowns 1.1, 3.1, 7.2 verified
- PREP_PLAN.md: Task 2 -> COMPLETE
- CHANGELOG.md: Task 2 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint34-task2
gh pr create --base main --title "Complete Sprint 34 Prep Task 2: Day-0 Baseline + Genuine-Floor Re-Baseline" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run `make typecheck && make lint && make format && make test` only if you touched Python)
- [x] BASELINE_METRICS.md records Day-0 = Sprint 33 close + bucket members + genuine floor 75 + the 142-vs-219 split
- [x] Day-0 code anchor = the S33-close SHA (no src/ drift; DB changed since 4cbf8bff via the P6 sample fix, now historical)
- [x] Unknowns 1.1, 3.1, 7.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 2 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 3 Prompt: mine Head-Offset Dual Subsystem — Design (Priority 1 Foundation)

**Branch:** Create a new branch named `planning/sprint34-task3` from `main`

**Priority:** Critical (6–8 hours)

**Objective:** Turn the Sprint-33 Day-2 control (H1 head-label re-keying is **value-invariant**; the residual is a deeper head-offset dual-architecture mismatch, 22-row breadth) into a concrete **head-offset dual-subsystem design** — how head-placed constraint duals reconcile into `stat_x` at the `c`-boundary so `N→0` at all bound-active rows — with a pre-`src/` `/tmp` control gate and a sizing.

**Unknowns Verified:** 1.1, 1.2, 1.3, 1.4, 1.5

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_34/PREP_PLAN.md` §Task 3
- `docs/planning/EPIC_4/SPRINT_34/KNOWN_UNKNOWNS.md` §Unknowns 1.1–1.5
- `docs/planning/EPIC_4/SPRINT_33/DAY2_MINE_REPLAN.md` (H1 value-invariance, 22→22 rows, `d_N = d_Nh1`) + `docs/planning/EPIC_4/SPRINT_33/DAY1_PROGRESS_NOTES.md` §5 (the validated residual decomposition, run from the repo root) + `docs/planning/EPIC_4/SPRINT_33/MINE_CROSSTERM_DESIGN.md` (the `c`-boundary classification, the cross-term-correct finding)
- `src/kkt/stationarity.py` `_try_build_param_offset_crossterm` + the S31 `EquationDef.head_domain_offsets` IR; `scripts/diagnostics/kkt_residual.py` (the harness); `data/gamslib/raw/mine.gms`
- **PR24/PR27 + `modelstat` + `x.up=inf` BANNED** (see the cross-cutting conventions)

**Tasks to Complete:**

1. Re-confirm the Day-0 fingerprint: `kkt_residual.py mine.gms` → CASE_B `stat_x(3,1,1)` rel 2.37, dual CONSISTENT; re-run the Day-1 residual decomposition **from the repo root** (the emit `$include` is repo-relative) to reproduce the 22-row `dbg_N`.
2. Re-confirm H1 value-invariance (`d_N = d_Nh1`, 22→22 rows); confirm at the max row `x.m=0`, the cross-term is structurally correct (−16000), and closing needs +16000 no emittable term supplies (assert `modelstat`; `x.up=inf` BANNED).
3. Characterize the dual-architecture mismatch (how the head-placed precedence dual `pr.m(k,l+1,i,j)` fails to map into `stat_x` at the `c`-boundary; the 22-row breadth vs the banked 6).
4. Design the reconciliation hypothesis (H_dual): the emit reformulation that maps head-placed constraint duals into `stat_x` consistently at the boundary (candidate: a boundary-row dual-transfer term keyed on the S31 `head_domain_offsets` IR). State the fix surface (`file:line`) as a **hypothesis** (PR24).
5. Specify the pre-`src/` `/tmp` control: the reconciliation prototype drives `N→0` at **all** bound-active rows AND unchanged (0) at interior rows → presolve MS-1 @ 17500 (`modelstat` asserted).
6. Pin the H3 REPLAN exit (a further-deferred head-offset dual architecture); size the track (design + `/tmp` control + emit/IR plumbing + regression fixture + determinism).
7. Write `docs/planning/EPIC_4/SPRINT_34/MINE_DUAL_SUBSYSTEM_DESIGN.md`.

**Deliverables (from PREP_PLAN.md §Task 3):**

- `docs/planning/EPIC_4/SPRINT_34/MINE_DUAL_SUBSYSTEM_DESIGN.md` with the dual-architecture characterization + the reconciliation hypothesis + the `/tmp` control gate
- The fix surface (as a Day-0-re-confirm hypothesis) + the sizing + the H3 REPLAN exit
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3, 1.4, 1.5

**Known Unknowns Updates:** For Unknowns 1.1–1.5, replace each `🔍 Status: INCOMPLETE` stub with the verification block (**Status** ✅ VERIFIED / ❌ WRONG, **Verified by** Task 3, **Date**, **Findings**, **Evidence** [the harness fingerprint + the residual decomposition + the value-invariance re-confirm], **Decision** [the H_dual design or the REPLAN exit]). If the `/tmp` control cannot be run in this docs-only prep, the PROCEED acceptance is a **spec**, not an executed result — say so explicitly.

**PREP_PLAN.md Updates:** In §Task 3: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria, including the "Unknowns 1.1, 1.2, 1.3, 1.4, 1.5 verified" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 34 Prep`, prepend:
```markdown
- **Prep Task 3 COMPLETE (YYYY-MM-DD):** mine #1443 head-offset dual subsystem design. Re-confirmed the Day-0 fingerprint (CASE_B `stat_x(3,1,1)` rel 2.37, dual CONSISTENT) + reproduced the 22-row residual decomposition from the repo root; re-confirmed H1 is value-invariant (`d_N = d_Nh1`). Characterized the head-offset dual-architecture mismatch (the +16000/−16000 `c`-boundary gap, `x.m=0`); designed the reconciliation hypothesis H_dual (the boundary-row dual-transfer keyed on `head_domain_offsets`) with the `file:line` fix surface as a Day-0-re-confirm hypothesis + the pre-`src/` `/tmp` control (`N→0` at all bound-active rows → MS-1 @ 17500, `modelstat` asserted, `x.up=inf` BANNED) + the H3 REPLAN exit. Sized [X–Yh]. Authored `docs/planning/EPIC_4/SPRINT_34/MINE_DUAL_SUBSYSTEM_DESIGN.md`; verified Unknowns 1.1–1.5. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected; the quality gate is not required. If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 34 Prep Task 3: mine Head-Offset Dual Subsystem Design

Re-confirmed the Day-0 fingerprint + reproduced the 22-row residual decomposition;
re-confirmed H1 value-invariance. Characterized the head-offset dual-architecture
mismatch (the +16000/-16000 c-boundary gap, x.m=0); designed the reconciliation
hypothesis H_dual with the file:line fix surface (a Day-0-re-confirm hypothesis) +
the pre-src/ /tmp control (N->0 all bound-active rows -> MS-1 @ 17500) + the H3
REPLAN exit. Sized [X-Yh]. modelstat asserted; x.up=inf BANNED.

## Deliverables
- docs/planning/EPIC_4/SPRINT_34/MINE_DUAL_SUBSYSTEM_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 1.1-1.5 verified
- PREP_PLAN.md: Task 3 -> COMPLETE
- CHANGELOG.md: Task 3 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint34-task3
gh pr create --base main --title "Complete Sprint 34 Prep Task 3: mine Head-Offset Dual Subsystem Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run the gate only if you touched Python)
- [x] MINE_DUAL_SUBSYSTEM_DESIGN.md characterizes the dual-architecture mismatch + states H_dual + the /tmp control + the H3 REPLAN exit
- [x] The Day-0 fingerprint re-confirmed; H1 value-invariance re-confirmed; the fix surface framed as a hypothesis (PR24)
- [x] modelstat asserted; x.up=inf BANNED
- [x] Unknowns 1.1-1.5 verified in KNOWN_UNKNOWNS.md
- [x] Task 3 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 4 Prompt: sarf Symbolic/Parametric `stat_task` Emit-Mode Design (Priority 2 Foundation)

**Branch:** Create a new branch named `planning/sprint34-task4` from `main`

**Priority:** High (5–7 hours)

**Objective:** Design the symbolic/parametric emit **mode** for `task(g,t,mn,mn)` that stops enumerating its 369,024 columns at all three sites (S1 `acost3` body-diff, S2 variable enumeration, S3 variable stationarity) atomically, emitting one guarded `stat_task$taskposs` + `task.fx` and letting GAMS instantiate the 398 live rows — with the O(active) translate-budget gate.

**Unknowns Verified:** 2.1, 2.2, 2.3, 2.4, 2.5

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_34/PREP_PLAN.md` §Task 4
- `docs/planning/EPIC_4/SPRINT_34/KNOWN_UNKNOWNS.md` §Unknowns 2.1–2.5
- `docs/planning/EPIC_4/SPRINT_33/DAY6_SARF_ASSESSMENT.md` + `docs/planning/EPIC_4/SPRINT_33/SARF_EMIT_SUBSYSTEM_DESIGN.md` (the blow-up locus, the 398-active sizing, the 7-term derivation, the atomicity spec)
- `src/ad/constraint_jacobian.py` (S1 `acost3` body-diff) + `src/ad/index_mapping.py:369` (`enumerate_variable_instances`, S2) + `src/kkt/stationarity.py` (S3); `data/gamslib/raw/sarf.gms`; srpchase (the ~2.9s translate reference)

**Tasks to Complete:**

1. Re-confirm the blow-up: a bounded translate probe (`> 75s` in `compute_constraint_jacobian`); confirm the 2-D gate is absent from `src/`.
2. Design the symbolic emit mode per site — S1 the `acost3` parametric body-diff (the guarded `nu_acost3` term, not 369K entries); S2 the `task` column short-circuit (emit symbolic, not enumerate); S3 the one symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)`.
3. Verify the 7-term `stat_task` derivation term-for-term against the constraint bodies; confirm no set-name-literal multiplier indices.
4. Specify the atomicity (the three sites + `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0` land in one change — a partial = an inconsistent MCP).
5. Specify the O(active) budget gate: translate in seconds (srpchase ~2.9s reference); byte-stable golden; determinism ×3; `--resolve-changed --since-commit <S33-close>` GO.
6. Pin the timeout-re-trigger REPLAN exit; size the track.
7. Write `docs/planning/EPIC_4/SPRINT_34/SARF_EMIT_MODE_DESIGN.md`.

**Deliverables (from PREP_PLAN.md §Task 4):**

- `docs/planning/EPIC_4/SPRINT_34/SARF_EMIT_MODE_DESIGN.md` with the three-site symbolic emit mode + the 7-term `stat_task` + the O(active) budget gate + atomicity spec
- The REPLAN exit + the sizing
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.1, 2.2, 2.3, 2.4, 2.5

**Known Unknowns Updates:** For Unknowns 2.1–2.5, replace each `🔍 Status: INCOMPLETE` stub with the verification block (**Status**, **Verified by** Task 4, **Date**, **Findings**, **Evidence** [the blow-up re-profile + the term-for-term derivation + the row-count check], **Decision**).

**PREP_PLAN.md Updates:** In §Task 4: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria, including the "Unknowns 2.1, 2.2, 2.3, 2.4, 2.5 verified" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 34 Prep`, prepend:
```markdown
- **Prep Task 4 COMPLETE (YYYY-MM-DD):** sarf #1385 symbolic/parametric `stat_task` emit-mode design. Re-confirmed the Day-0 blow-up (`compute_constraint_jacobian` > 75s; 2-D gate absent from `main`). Designed the symbolic emit mode per site (S1 `acost3` parametric ∂, S2 enumeration short-circuit, S3 one guarded `stat_task(g,t,m,n)$taskposs(g,t)`) + `task.fx$(not active)=0`, letting GAMS instantiate the 398 live rows; verified the 7-term derivation term-for-term (no set-name-literal indices); specified the atomic-landing requirement + the O(active) translate-budget gate (seconds vs srpchase ~2.9s, byte-stable, det ×3, `--resolve-changed` GO) + the timeout-re-trigger REPLAN exit. Sized [X–Yh]. Authored `docs/planning/EPIC_4/SPRINT_34/SARF_EMIT_MODE_DESIGN.md`; verified Unknowns 2.1–2.5. +1 Translate (→136) is the deliverable. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected; the quality gate is not required. If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 34 Prep Task 4: sarf Symbolic stat_task Emit-Mode Design

Re-confirmed the Day-0 blow-up (compute_constraint_jacobian > 75s; 2-D gate absent).
Designed the symbolic emit mode per site (S1 acost3 parametric d, S2 enumeration
short-circuit, S3 one guarded stat_task$taskposs) + task.fx$(not active)=0 letting
GAMS instantiate the 398 live rows; verified the 7-term derivation term-for-term
(no set-name-literal indices); specified atomicity + the O(active) budget gate +
the timeout-re-trigger REPLAN exit. Sized [X-Yh].

## Deliverables
- docs/planning/EPIC_4/SPRINT_34/SARF_EMIT_MODE_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 2.1-2.5 verified
- PREP_PLAN.md: Task 4 -> COMPLETE
- CHANGELOG.md: Task 4 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint34-task4
gh pr create --base main --title "Complete Sprint 34 Prep Task 4: sarf Symbolic stat_task Emit-Mode Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run the gate only if you touched Python)
- [x] SARF_EMIT_MODE_DESIGN.md designs the three-site symbolic emit + the 7-term stat_task + the O(active) gate + atomicity
- [x] The blow-up re-confirmed (> 75s); the derivation verified term-for-term; the REPLAN exit pinned
- [x] Unknowns 2.1-2.5 verified in KNOWN_UNKNOWNS.md
- [x] Task 4 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 5 Prompt: fawley Second-Index Correction + Forcing Design (Priority 3 Foundation)

**Branch:** Create a new branch named `planning/sprint34-task5` from `main`

**Priority:** High (4–6 hours)

**Objective:** Design the constraint-index-diagonal `sameas` extension (the genuine qsb/pbal cross-term correction) in `_add_indexed_jacobian_terms` + the forcing hand-off for the H-b +Solve — with the no-regression gate (no mbal / 1-D-core move).

**Unknowns Verified:** 3.1, 3.2, 3.3, 3.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_34/PREP_PLAN.md` §Task 5
- `docs/planning/EPIC_4/SPRINT_34/KNOWN_UNKNOWNS.md` §Unknowns 3.1–3.4
- `docs/planning/EPIC_4/SPRINT_33/DAY4_FAWLEY_CONTROL.md` (the 473→18.468 control, the H-b finding, §5 the bound-transfer-sign gap) + `docs/planning/EPIC_4/SPRINT_33/DAY5_FAWLEY_CLOSE.md` + `docs/planning/EPIC_4/SPRINT_33/FAWLEY_SECOND_INDEX_DESIGN.md`
- `src/kkt/stationarity.py` `_add_indexed_jacobian_terms` (~1400 lines, the dozen `sameas` paths); the 1-D polygon core `_var_at_two_indices_complement`; `data/gamslib/raw/fawley.gms`; `scripts/diagnostics/kkt_residual.py`

**Tasks to Complete:**

1. Re-confirm the control: `max|stat_bq|` 473 → 18.468 with the sameas patch; localize the residual + the H-a/H-b discriminator (Day-4 finding: H-b — MS-5 @ 4399.557 persists, LP opt 2899.25).
2. Design the constraint-index-diagonal `sameas`: how `_add_indexed_jacobian_terms` recognizes the *variable's-second-index = the constraint's-own-index* diagonal (qsb/pbal) and emits `$(sameas(cfq__,cf))`, symmetrically with the mbal first-index shape. State the fix surface (a hypothesis, PR24).
3. Specify the no-regression gate: no mbal-term change; no 1-D polygon/ps2 regression (a different path); `--resolve-changed --since-commit <S33-close>` GO.
4. Design the forcing hand-off: the genuine correction ships (a floor lever if fawley cold-matches); the H-b +Solve hands to the P5 `--force` survey; specify the boundary.
5. Pin the gate-leak REPLAN exit (the generalization leaks onto mbal / regresses the 1-D core); size the track (+ the fawley second-index fixture plan, following the S33 `test_sample_pruned_var_l_init.py` pattern).
6. Write `docs/planning/EPIC_4/SPRINT_34/FAWLEY_CORRECTION_FORCING_DESIGN.md`.

**Deliverables (from PREP_PLAN.md §Task 5):**

- `docs/planning/EPIC_4/SPRINT_34/FAWLEY_CORRECTION_FORCING_DESIGN.md` with the constraint-index-diagonal `sameas` design + the no-regression gate + the forcing hand-off
- The REPLAN exit + the sizing (+ the fawley second-index fixture plan)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.2, 3.3, 3.4

**Known Unknowns Updates:** For Unknowns 3.1–3.4, replace each `🔍 Status: INCOMPLETE` stub with the verification block (**Status**, **Verified by** Task 5, **Date**, **Findings** [the 473→18.468 re-confirm + the H-b discriminator + the floor-credit determination], **Evidence**, **Decision**). Apply the genuine-vs-methodology floor definition to 3.3 (does a corrected-but-forcing cold emit count toward the floor?).

**PREP_PLAN.md Updates:** In §Task 5: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria, including the "Unknowns 3.1, 3.2, 3.3, 3.4 verified" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 34 Prep`, prepend:
```markdown
- **Prep Task 5 COMPLETE (YYYY-MM-DD):** fawley #1111/#1112 second-index correction + forcing design. Re-confirmed the control (`max|stat_bq|` 473 → 18.468) + the **H-b** discriminator (MS-5 @ 4399.557 persists with the warm residual closed, LP opt 2899.25). Designed the constraint-index-diagonal `sameas` extension in `_add_indexed_jacobian_terms` (recognize the variable's-second-index = the constraint's-own-index diagonal on qsb/pbal, symmetric with mbal) with the fix surface as a hypothesis + the no-regression gate (no mbal / 1-D-core move; `--resolve-changed` GO) + the forcing hand-off for the H-b +Solve (to the P5 `--force` survey) + the fawley 2-D second-index fixture plan. Determined the genuine-floor credit for the corrected cold emit. Sized [X–Yh] + the gate-leak REPLAN exit. Authored `docs/planning/EPIC_4/SPRINT_34/FAWLEY_CORRECTION_FORCING_DESIGN.md`; verified Unknowns 3.1–3.4. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected; the quality gate is not required. If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 34 Prep Task 5: fawley Second-Index Correction + Forcing Design

Re-confirmed the control (max|stat_bq| 473 -> 18.468) + the H-b discriminator (MS-5
@ 4399.557 persists with the warm residual closed, LP opt 2899.25). Designed the
constraint-index-diagonal sameas extension in _add_indexed_jacobian_terms (qsb/pbal
diagonal, symmetric with mbal) with the fix surface as a hypothesis + the no-regression
gate + the forcing hand-off for the H-b +Solve + the fawley 2-D fixture plan.
Sized [X-Yh] + the gate-leak REPLAN exit.

## Deliverables
- docs/planning/EPIC_4/SPRINT_34/FAWLEY_CORRECTION_FORCING_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 3.1-3.4 verified
- PREP_PLAN.md: Task 5 -> COMPLETE
- CHANGELOG.md: Task 5 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint34-task5
gh pr create --base main --title "Complete Sprint 34 Prep Task 5: fawley Second-Index Correction + Forcing Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run the gate only if you touched Python)
- [x] FAWLEY_CORRECTION_FORCING_DESIGN.md designs the constraint-index-diagonal sameas + the no-regression gate + the forcing hand-off
- [x] The control re-confirmed (473 -> 18.468); the H-b discriminator; the floor-credit determination
- [x] Unknowns 3.1-3.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 5 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 6 Prompt: Max-Convention Bound-Transfer-Sign Track Design (Priority 4 — NEW)

**Branch:** Create a new branch named `planning/sprint34-task6` from `main`

**Priority:** High (4–6 hours)

**Objective:** Design the sign-robust `piL_*/piU_*` warm-start transfer (the general max-convention fix) + the MAXIMIZE-cohort +Solve survey — determining which max models' MCP divergence is warm-residual-driven (a +Solve lever) vs structural (like fawley's H-b).

**Unknowns Verified:** 4.1, 4.2, 4.3, 4.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_34/PREP_PLAN.md` §Task 6
- `docs/planning/EPIC_4/SPRINT_34/KNOWN_UNKNOWNS.md` §Unknowns 4.1–4.4
- `docs/planning/EPIC_4/SPRINT_33/DAY4_FAWLEY_CONTROL.md` §5 (the bound-transfer-sign analysis + the per-cell decomposition; the discovery cells — fawley `bq.m<0` at a lower bound, mine upper-bound multipliers)
- `src/emit/emit_gams.py` (the presolve `piL_*/piU_*` bound-transfer lines + the min-convention `.m > 0` / `.m < 0` gates); `data/gamslib/raw/`; `scripts/gamslib/run_full_test.py` `--resolve-changed`

**Tasks to Complete:**

1. Re-confirm the gap: locate the min-convention `.m > 0` / `.m < 0` gates in the presolve emit (`src/emit/emit_gams.py`); confirm the sign-robust `= abs(.m)` closes the warm residual on fawley + mine (a `/tmp` control; assert `modelstat`).
2. Enumerate the MAXIMIZE cohort: which corpus models `solve … maximizing …`; of those, which are `model_infeasible` / presolve-recovered (the +Solve candidates) vs already-solving (the regression-risk set).
3. Design the sign-robust transfer (drop the min-convention sign gate; `= abs(.m)` at the active bound), gated so it fires only at active bounds (no over-transfer on interior/presolve-match models). State the fix surface (a hypothesis, PR24).
4. Specify the +Solve survey: for each MAXIMIZE `model_infeasible` candidate, does the sign-robust transfer close the warm residual AND reach MS-1 (warm-residual-driven) vs stay MS-5 (structural, like fawley's H-b)?
5. Specify the no-regression gate: `--resolve-changed --since-commit <S33-close>` GO (no presolve-match cohort regression — the transfer fires only at active bounds).
6. Pin the REPLAN exit (over-transfer / all-structural cohort → a documented general-correctness finding); size the track.
7. Write `docs/planning/EPIC_4/SPRINT_34/BOUND_TRANSFER_SIGN_DESIGN.md`.

**Deliverables (from PREP_PLAN.md §Task 6):**

- `docs/planning/EPIC_4/SPRINT_34/BOUND_TRANSFER_SIGN_DESIGN.md` with the sign-robust transfer design + the MAXIMIZE-cohort +Solve survey + the no-regression gate
- The REPLAN exit + the sizing
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.2, 4.3, 4.4

**Known Unknowns Updates:** For Unknowns 4.1–4.4, replace each `🔍 Status: INCOMPLETE` stub with the verification block (**Status**, **Verified by** Task 6, **Date**, **Findings** [the min-convention gate location + the fawley/mine cell closure + the MAXIMIZE-cohort classification], **Evidence**, **Decision** [which candidate is a clean +Solve vs structural]).

**PREP_PLAN.md Updates:** In §Task 6: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria, including the "Unknowns 4.1, 4.2, 4.3, 4.4 verified" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 34 Prep`, prepend:
```markdown
- **Prep Task 6 COMPLETE (YYYY-MM-DD):** max-convention bound-transfer-sign track design (NEW). Re-confirmed the gap (the min-convention `.m > 0` / `.m < 0` gates in `src/emit/emit_gams.py`; the sign-robust `= abs(.m)` closes the warm residual on the fawley + mine discovery cells). Enumerated the MAXIMIZE cohort (the `model_infeasible` +Solve candidates vs the already-solving regression-risk set); designed the sign-robust transfer with active-bound gating (no over-transfer on presolve-match models) + the fix surface as a hypothesis + the +Solve survey (warm-residual-driven vs structural) + the no-regression gate (`--resolve-changed` GO) + the REPLAN exit. Sized [X–Yh]. The freshest, least-refuted +Solve lever. Authored `docs/planning/EPIC_4/SPRINT_34/BOUND_TRANSFER_SIGN_DESIGN.md`; verified Unknowns 4.1–4.4. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected; the quality gate is not required. If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 34 Prep Task 6: Max-Convention Bound-Transfer-Sign Track Design

Re-confirmed the gap (the min-convention .m>0/.m<0 gates in emit_gams.py; the
sign-robust = abs(.m) closes the warm residual on the fawley + mine discovery cells).
Enumerated the MAXIMIZE cohort (+Solve candidates vs the regression-risk set); designed
the sign-robust transfer with active-bound gating + the fix surface as a hypothesis +
the +Solve survey (warm-residual-driven vs structural) + the no-regression gate + the
REPLAN exit. Sized [X-Yh]. The freshest, least-refuted +Solve lever.

## Deliverables
- docs/planning/EPIC_4/SPRINT_34/BOUND_TRANSFER_SIGN_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 4.1-4.4 verified
- PREP_PLAN.md: Task 6 -> COMPLETE
- CHANGELOG.md: Task 6 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint34-task6
gh pr create --base main --title "Complete Sprint 34 Prep Task 6: Max-Convention Bound-Transfer-Sign Track Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run the gate only if you touched Python)
- [x] BOUND_TRANSFER_SIGN_DESIGN.md designs the sign-robust transfer + the MAXIMIZE-cohort +Solve survey + the no-regression gate
- [x] The gap re-confirmed on fawley + mine; the cohort enumerated; the fix surface framed as a hypothesis (PR24)
- [x] Unknowns 4.1-4.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 6 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 7 Prompt: camcge Dual-Consistent Walras Numéraire Design (Epic 5) + rocket PATH-Consultation Submission Plan (Priority 5)

**Branch:** Create a new branch named `planning/sprint34-task7` from `main`

**Priority:** Medium (3–4 hours)

**Objective:** Design the camcge per-model-numéraire + dual-consistent Walras redefinition (the Epic-5 `/tmp` gate to MS-1 at omega 191.7346) with the S1∧S2∧S3 degeneracy-detector scope, and plan the rocket PATH-consultation input submission to the Sprint-35 consultation.

**Unknowns Verified:** 5.1, 5.2, 5.3

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_34/PREP_PLAN.md` §Task 7
- `docs/planning/EPIC_4/SPRINT_34/KNOWN_UNKNOWNS.md` §Unknowns 5.1–5.3
- `docs/planning/EPIC_4/SPRINT_33/CAMCGE_WALRAS_DESIGN.md` (step 1 landed S32; step 2 omega 191.7346 but MS-4) + `docs/planning/EPIC_4/SPRINT_33/ROCKET_CASEC_FORCING_PLAN.md` (the FINALIZED consultation input) + `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` (the S1∧S2∧S3 detector, the numéraire recipe) + `docs/planning/EPIC_4/SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`
- `data/gamslib/gamslib_status.json` (camcge MS-4; irscge/lrgcge/moncge/stdcge MS-1) — **check the dual side, not just the primal**

**Tasks to Complete:**

1. Re-confirm camcge MS-4 (DB) + the S1∧S2∧S3 detector cohort (camcge fires; irscge/lrgcge/moncge/stdcge pass-through).
2. Design the full dual-consistent redefinition: keep every market-clearing row + the consumption-weighted numéraire + redefine the redundant market's dual via Walras' law; the `/tmp`-to-MS-1 prototype is the Epic-5 gate (check the dual side).
3. Scope the degeneracy detector: S1∧S2∧S3 flags only camcge (S3 = cold-MCP-singular-at-iter-0, the false-positive guard).
4. Plan the rocket submission: package the FINALIZED input + the reproducer + the `--force` scaffold as the Sprint-35 consultation brief; define the hand-off mechanism; re-affirm the Case-c sign-flip BAN (refuted 4×).
5. Pin the disposition: camcge Epic-5-deferred (expected); rocket = a Sprint-35 submission.
6. Write `docs/planning/EPIC_4/SPRINT_34/CAMCGE_ROCKET_PLAN.md`.

**Deliverables (from PREP_PLAN.md §Task 7):**

- `docs/planning/EPIC_4/SPRINT_34/CAMCGE_ROCKET_PLAN.md` with the dual-consistent Walras design (Epic-5 gate) + the detector scope + the rocket submission plan
- The Epic-5-deferral disposition + the Sprint-35 rocket hand-off
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.1, 5.2, 5.3

**Known Unknowns Updates:** For Unknowns 5.1–5.3, replace each `🔍 Status: INCOMPLETE` stub with the verification block (**Status**, **Verified by** Task 7, **Date**, **Findings** [camcge MS-4 + the detector cohort + the rocket-input completeness], **Evidence**, **Decision** [Epic-5-deferral + the Sprint-35 hand-off]). 5.1 is design-level (MS-1 is the Epic-5 gate, not an in-sprint result).

**PREP_PLAN.md Updates:** In §Task 7: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria, including the "Unknowns 5.1, 5.2, 5.3 verified" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 34 Prep`, prepend:
```markdown
- **Prep Task 7 COMPLETE (YYYY-MM-DD):** camcge #1330 dual-consistent Walras numéraire design (Epic 5) + rocket #1462 PATH-consultation submission plan — **Epic-5-deferred + Sprint-35 hand-off**. Re-confirmed camcge MS-4 + the S1∧S2∧S3 detector cohort (camcge flags; irscge/lrgcge/moncge/stdcge pass-through). Designed the per-model-numéraire + dual-consistent Walras redefinition (keep every market-clearing row + redefine the redundant market's dual via Walras' law → full-rank while the dual stays available; dual side checked) with the `/tmp`-to-MS-1 Epic-5 gate; scoped the S3 false-positive guard. Planned the rocket submission (the FINALIZED input + reproducer + `--force` scaffold → the Sprint-35 PATH-author consultation) + re-affirmed the Case-c sign-flip BAN. Authored `docs/planning/EPIC_4/SPRINT_34/CAMCGE_ROCKET_PLAN.md`; verified Unknowns 5.1 (design-level), 5.2, 5.3. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected; the quality gate is not required. If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 34 Prep Task 7: camcge Walras (Epic 5) + rocket PATH Submission Plan

Re-confirmed camcge MS-4 + the S1^S2^S3 detector cohort (camcge flags; the four CGE
siblings pass-through). Designed the per-model-numeraire + dual-consistent Walras
redefinition (redefine the redundant market's dual via Walras' law; dual side checked)
with the /tmp-to-MS-1 Epic-5 gate; scoped the S3 false-positive guard. Planned the
rocket submission (FINALIZED input + reproducer + --force scaffold -> the Sprint-35
consultation) + re-affirmed the Case-c sign-flip BAN. Epic-5-deferred.

## Deliverables
- docs/planning/EPIC_4/SPRINT_34/CAMCGE_ROCKET_PLAN.md
- KNOWN_UNKNOWNS.md: Unknowns 5.1-5.3 verified
- PREP_PLAN.md: Task 7 -> COMPLETE
- CHANGELOG.md: Task 7 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint34-task7
gh pr create --base main --title "Complete Sprint 34 Prep Task 7: camcge Walras (Epic 5) + rocket PATH Submission Plan" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run the gate only if you touched Python)
- [x] CAMCGE_ROCKET_PLAN.md designs the dual-consistent Walras (Epic-5 gate, dual side checked) + the detector scope + the rocket Sprint-35 submission
- [x] camcge MS-4 re-confirmed; the detector flags only camcge; the sign-flip BAN re-affirmed
- [x] Unknowns 5.1-5.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 7 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 8 Prompt: Author Phase 0 Acceptance Gates for the Sprint-34 Tracks (PR20 + PR24 + PR27)

**Branch:** Create a new branch named `planning/sprint34-task8` from `main`

**Priority:** Critical (4–6 hours)

**Objective:** Consolidate the per-track `/tmp` control specs from the Task-3–7 designs into one `PHASE_0_ACCEPTANCE_GATES.md` — one hand-derived gate per track (P1–P5) with the exact control, the pass criterion, the `modelstat` assertion, and the PROCEED/REPLAN decision.

**Unknowns Verified:** 1.2, 2.2, 3.1, 4.1, 5.1 (the per-track gate feasibility)

**Prerequisites (read before starting):** *(requires Tasks 3, 4, 5, 6, 7 complete)*

- `docs/planning/EPIC_4/SPRINT_34/PREP_PLAN.md` §Task 8
- `docs/planning/EPIC_4/SPRINT_34/KNOWN_UNKNOWNS.md` §Unknowns 1.2, 2.2, 3.1, 4.1, 5.1
- The five Task-3–7 design docs: `MINE_DUAL_SUBSYSTEM_DESIGN.md`, `SARF_EMIT_MODE_DESIGN.md`, `FAWLEY_CORRECTION_FORCING_DESIGN.md`, `BOUND_TRANSFER_SIGN_DESIGN.md`, `CAMCGE_ROCKET_PLAN.md` (all under `docs/planning/EPIC_4/SPRINT_34/`)
- `docs/planning/EPIC_4/SPRINT_33/PHASE_0_ACCEPTANCE_GATES.md` (the template); the CI gates: golden-staleness (`scripts/sprint_audit/check_golden_staleness.py`), presolve-divergence (`scripts/diagnostics/check_presolve_divergence.py`), `--resolve-changed`

**Tasks to Complete:**

1. Author one gate per track (P1–P5): the exact `/tmp` control + the pass criterion + the `modelstat` assertion + the PROCEED/REPLAN decision, carrying each design's disposition (P1 the dual-reconciliation warm-residual→0; P2 the O(active=398) probe; P3 the `max|stat_bq|→0` + the H-b forcing branch; P4 the sign-robust warm-residual→0 + the +Solve survey; P5 the Walras `/tmp` at MS-1 [Epic-5-deferral]).
2. Encode the standing BANs: mine `x.up=inf` BANNED; the Case-c objective-gradient sign flip BANNED.
3. Encode the emit-touching CI gates: golden-staleness (PR26), presolve-divergence detector, `--resolve-changed --since-commit <S33-close>` checkpoint.
4. Append Task-8 gate-feasibility notes to the mapped Known Unknowns (1.2, 2.2, 3.1, 4.1, 5.1) — WITHOUT overwriting the Task-3–7 primary blocks.
5. Write `docs/planning/EPIC_4/SPRINT_34/PHASE_0_ACCEPTANCE_GATES.md`.

**Deliverables (from PREP_PLAN.md §Task 8):**

- `docs/planning/EPIC_4/SPRINT_34/PHASE_0_ACCEPTANCE_GATES.md` — one PROCEED/REPLAN gate per track P1–P5 with the `/tmp` control + the pass criterion + the CI gates
- The standing BANs + the Task-8 gate-feasibility notes on the mapped unknowns
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.2, 2.2, 3.1, 4.1, 5.1

**Known Unknowns Updates:** For Unknowns 1.2, 2.2, 3.1, 4.1, 5.1, APPEND a **Task-8 gate-feasibility note** to the existing verification block (do not overwrite the Task-3/4/5/6/7 primary block) recording that the per-track `/tmp` control/gate is feasible with a clean PROCEED/REPLAN decision.

**PREP_PLAN.md Updates:** In §Task 8: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria, including the "Unknowns 1.2, 2.2, 3.1, 4.1, 5.1 verified" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 34 Prep`, prepend:
```markdown
- **Prep Task 8 COMPLETE (YYYY-MM-DD):** Phase 0 acceptance gates for the Sprint-34 tracks (P1–P5). Consolidated the per-track `/tmp` control specs from the five Task-3–7 design docs into one `PHASE_0_ACCEPTANCE_GATES.md` — one hand-derived gate per track with the exact control, the pass criterion, the `modelstat` assertion, and the PROCEED/REPLAN decision, carrying each design's disposition (P1 the dual-reconciliation warm-residual→0; P2 the O(active=398) probe; P3 the `max|stat_bq|→0` + the H-b forcing branch; P4 the sign-robust warm-residual→0 + the +Solve survey; P5 the Walras `/tmp` at MS-1, Epic-5-deferred). Encoded the standing BANs (mine `x.up=inf`; the Case-c sign flip) + the emit-touching CI gates (golden-staleness PR26, presolve-divergence, `--resolve-changed --since-commit <S33-close>`). Appended Task-8 gate-feasibility notes to Unknowns 1.2/2.2/3.1/4.1/5.1 (primary blocks preserved). Authored `docs/planning/EPIC_4/SPRINT_34/PHASE_0_ACCEPTANCE_GATES.md`; verified Unknowns 1.2, 2.2, 3.1, 4.1, 5.1 (gate feasibility). Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected; the quality gate is not required. If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 34 Prep Task 8: Phase 0 Acceptance Gates for the Sprint-34 Tracks

Consolidated the per-track /tmp control specs from the five Task-3-7 design docs into
one PHASE_0_ACCEPTANCE_GATES.md — one hand-derived gate per track P1-P5 (control +
pass criterion + modelstat + PROCEED/REPLAN), carrying each design's disposition.
Encoded the standing BANs (mine x.up=inf; the Case-c sign flip) + the emit-touching
CI gates (golden-staleness, presolve-divergence, --resolve-changed --since-commit
<S33-close>). Appended gate-feasibility notes to Unknowns 1.2/2.2/3.1/4.1/5.1.

## Deliverables
- docs/planning/EPIC_4/SPRINT_34/PHASE_0_ACCEPTANCE_GATES.md
- KNOWN_UNKNOWNS.md: Unknowns 1.2, 2.2, 3.1, 4.1, 5.1 verified (gate feasibility)
- PREP_PLAN.md: Task 8 -> COMPLETE
- CHANGELOG.md: Task 8 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint34-task8
gh pr create --base main --title "Complete Sprint 34 Prep Task 8: Phase 0 Acceptance Gates for the Sprint-34 Tracks" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run the gate only if you touched Python)
- [x] PHASE_0_ACCEPTANCE_GATES.md has one PROCEED/REPLAN gate per track P1-P5 with the /tmp control + pass criterion + CI gates
- [x] The standing BANs encoded; the gate-feasibility notes appended (primary blocks preserved)
- [x] Unknowns 1.2, 2.2, 3.1, 4.1, 5.1 verified in KNOWN_UNKNOWNS.md
- [x] Task 8 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 9 Prompt: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (PR16)

**Branch:** Create a new branch named `planning/sprint34-task9` from `main`

**Priority:** High (3–5 hours)

**Objective:** Apply the PR16 hypothesis-validation methodology to the four from-scratch/new tracks — P1 (deeper dual-architecture), P2 (timeout re-trigger), P3 (gate-leak / H-b), P4 (over-transfer / structural) — pinning explicit REPLAN exits, the freed-budget reallocation, and the honest projection of which KPI buckets can actually move.

**Unknowns Verified:** 1.5, 2.2, 3.2, 4.2 (the REPLAN-probability unknowns)

**Prerequisites (read before starting):** *(requires Tasks 3, 4, 5, 6, 8 complete)*

- `docs/planning/EPIC_4/SPRINT_34/PREP_PLAN.md` §Task 9
- `docs/planning/EPIC_4/SPRINT_34/KNOWN_UNKNOWNS.md` §Unknowns 1.5, 2.2, 3.2, 4.2
- The Task-3/4/5/6 design docs + `docs/planning/EPIC_4/SPRINT_34/PHASE_0_ACCEPTANCE_GATES.md` (Task 8)
- `docs/planning/EPIC_4/SPRINT_33/REPLAN_RISK_ASSESSMENT.md` (the template) + `docs/planning/EPIC_4/SPRINT_33/SPRINT_RETROSPECTIVE.md` §3 (the modal-flat-KPI lesson, borne out for the deep tracks but beaten by P6) + `PROJECT_PLAN.md` §"Sprint 34" Risk Level (HIGH)

**Tasks to Complete:**

1. For each of P1/P2/P3/P4, assess the REPLAN probability + the refuting control/harness evidence + how early the Day-5 checkpoint surfaces it. NB: P1 is **High** (banked premise twice-refuted); P4 is the freshest/least-refuted (the best +Solve odds).
2. Assess P5 (camcge Epic-5 deferral; rocket Sprint-35 submission).
3. Pin the REPLAN exits + the freed-budget reallocation (→ P6 failure-cohort + P7 fixtures).
4. Author the honest KPI projection: the in-sprint Solve movers ({P1 mine, P3-forcing, P4 bound-transfer, P6 ganges/gangesx}); Translate +1 via P2; genuine floor +1 via P1/P3 cold-match; the stretch (Solve ≥ 110); and the modal outcome (Sprint 33 showed the P6 failure-cohort is a genuine bucket source).
5. Recommend the front-load ordering (P1, P2 front-loaded; P4 early as the fresh lever).
6. Write `docs/planning/EPIC_4/SPRINT_34/REPLAN_RISK_ASSESSMENT.md`; append the Task-9 REPLAN-probability contributions to Unknowns 1.5/2.2/3.2/4.2 (not overwriting the Task-3/4/5/6 primary blocks).

**Deliverables (from PREP_PLAN.md §Task 9):**

- `docs/planning/EPIC_4/SPRINT_34/REPLAN_RISK_ASSESSMENT.md` with a per-track REPLAN-probability + refutation-evidence assessment (P1/P2/P3/P4)
- The pinned REPLAN exits + freed-budget reallocation (→ P6/P7)
- The honest KPI projection (firm/conditional movers, stretch, modal outcome) + the front-load ordering
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.5, 2.2, 3.2, 4.2

**Known Unknowns Updates:** For Unknowns 1.5, 2.2, 3.2, 4.2, APPEND a **Task-9 REPLAN-probability contribution** to the existing verification block (do not overwrite the Task-3/4/5/6 primary block).

**PREP_PLAN.md Updates:** In §Task 9: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria, including the "Unknowns 1.5, 2.2, 3.2, 4.2 verified" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 34 Prep`, prepend:
```markdown
- **Prep Task 9 COMPLETE (YYYY-MM-DD):** REPLAN-prone track risk assessment (PR16). Assessed the REPLAN probability + the refuting control/harness evidence for the four from-scratch/new tracks — **P1 mine High prior** (the banked premise twice-refuted: S32 `N`-derivation + S33 H1 value-invariance → mine enters on H_dual, a deeper head-offset dual-architecture hypothesis; H3 REPLAN); **P2 sarf Medium-High** (a fourth enumeration site re-triggers the timeout); **P3 fawley Medium correctness-REPLAN / H-b +Solve** (the correction ships as a floor lever, +Solve → forcing); **P4 bound-transfer** the freshest/least-refuted (over-transfer / all-structural-cohort exit). Assessed P5 (camcge Epic-5-deferral; rocket Sprint-35). Pinned the REPLAN exits + the freed-budget reallocation (→ P6 failure-cohort + P7 fixtures); authored the honest KPI projection (Solve movers {P1/P3-forcing/P4/P6}; Translate +1 on P2; genuine floor +1 on P1/P3 cold-match; stretch Solve ≥ 110; **modal flat-KPI, but the P6 failure-cohort is a genuine bucket source — S33's sample proved it**) + the deep-track + P4 front-load (REPLANs surface by the Day-5 checkpoint). Appended Task-9 contributions to Unknowns 1.5/2.2/3.2/4.2. Authored `docs/planning/EPIC_4/SPRINT_34/REPLAN_RISK_ASSESSMENT.md`; verified Unknowns 1.5, 2.2, 3.2, 4.2. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected; the quality gate is not required. If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 34 Prep Task 9: REPLAN-Prone Track Risk Assessment

Assessed the REPLAN probability + refuting evidence for P1/P2/P3/P4 (P1 mine High
prior, twice-refuted -> H_dual; P2 sarf timeout re-trigger; P3 fawley correctness-REPLAN
/ H-b +Solve -> forcing; P4 bound-transfer the freshest lever). Assessed P5 (camcge
Epic-5 / rocket Sprint-35). Pinned the REPLAN exits + the freed-budget reallocation
(-> P6/P7); authored the honest KPI projection (modal flat-KPI, but the P6 failure-cohort
is a genuine bucket source) + the deep-track + P4 front-load.

## Deliverables
- docs/planning/EPIC_4/SPRINT_34/REPLAN_RISK_ASSESSMENT.md
- KNOWN_UNKNOWNS.md: Unknowns 1.5, 2.2, 3.2, 4.2 verified
- PREP_PLAN.md: Task 9 -> COMPLETE
- CHANGELOG.md: Task 9 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint34-task9
gh pr create --base main --title "Complete Sprint 34 Prep Task 9: REPLAN-Prone Track Risk Assessment" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run the gate only if you touched Python)
- [x] REPLAN_RISK_ASSESSMENT.md assesses P1/P2/P3/P4 REPLAN probability + refuting evidence + the REPLAN exits + the honest KPI projection + the front-load ordering
- [x] The freed-budget reallocation pinned (-> P6/P7); the modal-flat-KPI reality + the P6 bucket source stated
- [x] Unknowns 1.5, 2.2, 3.2, 4.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 9 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 10 Prompt: Reusable-Tooling Readiness Audit + Backlog Fix-Surface Analysis (Priorities 6 + 7)

**Branch:** Create a new branch named `planning/sprint34-task10` from `main`

**Priority:** Medium (3–4 hours)

**Objective:** Confirm the Sprint-28–33 diagnostic tooling covers the new Sprint-34 emit classes, and analyze the P6 failure-cohort fix-surfaces (ganges/gangesx `$141/$145/$149`, agreste scope-verify) + the P7 infrastructure scope (shape12/shape13/fawley property fixtures, genuine-floor tracking, Epic-4-SUMMARY continuation).

**Unknowns Verified:** 6.1, 6.2, 6.3, 7.1, 7.3

**Prerequisites (read before starting):** *(requires Tasks 1, 8 complete)*

- `docs/planning/EPIC_4/SPRINT_34/PREP_PLAN.md` §Task 10
- `docs/planning/EPIC_4/SPRINT_34/KNOWN_UNKNOWNS.md` §Unknowns 6.1, 6.2, 6.3, 7.1, 7.3
- `docs/planning/EPIC_4/SPRINT_34/PHASE_0_ACCEPTANCE_GATES.md` (Task 8) + `docs/planning/EPIC_4/SPRINT_33/TOOLING_AND_BACKLOG_ANALYSIS.md` (the template) + `docs/planning/EPIC_4/SPRINT_33/DAY12_P7_INFRA.md` + the S33 `tests/integration/emit/test_sample_pruned_var_l_init.py` fixture pattern
- The reused tooling: `scripts/diagnostics/kkt_residual.py` (Case-a/b/c + `case_c_objdef`), `scripts/diagnostics/check_presolve_divergence.py`, `scripts/sprint_audit/check_golden_staleness.py`, `scripts/gamslib/run_full_test.py` `--resolve-changed`, `src/cli.py` `--force`; `data/gamslib/raw/{ganges,gangesx,agreste}.gms`; `docs/planning/EPIC_4/SUMMARY.md`

**Tasks to Complete:**

1. Audit the reused tooling: confirm the harness (Case-a/b/c + `case_c_objdef`), the presolve-divergence detector, the golden-staleness gate, the `--resolve-changed` checkpoint, and the `--force` scaffold cover the new Sprint-34 classes (the head-offset dual residual test; the sarf symbolic emit path; the bound-transfer warm-residual test; the second-index fixture). Note any gap.
2. Analyze the P6 fix-surfaces: ganges/gangesx (emit + compile one; find the shared `$141/$145/$149` translate-syntax root — a single fix may recover both; the referenced `.l`-init vars are declared, so the P6 sample fix does not apply); agreste (verify the double-`solve` scope before treating the CASE_B `stat_sales` as an emit bug). Each `--resolve-changed`-gated. **Verify per-model — the cohort is multi-root.**
3. Scope the P7 property fixtures: shape12 (head-offset dual), shape13 (sarf symbolic), fawley second-index — each fail-before/pass-after, landing *only once* P1/P2/P3 land (the S33 `test_sample_pruned_var_l_init.py` pattern); plus the genuine-floor recompute (anchor 75) + the Epic-4-`SUMMARY.md` row-34 continuation.
4. Write `docs/planning/EPIC_4/SPRINT_34/TOOLING_AND_BACKLOG_ANALYSIS.md`.

**Deliverables (from PREP_PLAN.md §Task 10):**

- `docs/planning/EPIC_4/SPRINT_34/TOOLING_AND_BACKLOG_ANALYSIS.md` with the tooling-readiness audit (reuse vs gap) + the P6 fix-surface + P7 fixture scope
- The ganges/gangesx `$141/$145/$149` root diagnosis + the agreste scope caveat
- The shape12/shape13/fawley fixture plan (gated on P1/P2/P3) + the genuine-floor recompute (anchor 75) + Epic-4-SUMMARY continuation
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 6.1, 6.2, 6.3, 7.1, 7.3

**Known Unknowns Updates:** For Unknowns 6.1, 6.2, 6.3, 7.1, 7.3, replace each `🔍 Status: INCOMPLETE` stub with the verification block (**Status**, **Verified by** Task 10, **Date**, **Findings** [the ganges/gangesx root + the agreste scope + the multi-root confirm + the fixture scope + the SUMMARY row-34 format], **Evidence**, **Decision**).

**PREP_PLAN.md Updates:** In §Task 10: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria, including the "Unknowns 6.1, 6.2, 6.3, 7.1, 7.3 verified" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 34 Prep`, prepend:
```markdown
- **Prep Task 10 COMPLETE (YYYY-MM-DD):** reusable-tooling readiness audit + backlog fix-surface analysis (P6 + P7). Audited the Sprint-28–33 tooling against the new Sprint-34 emit classes — the KKT-residual harness (incl. `case_c_objdef`), the presolve-divergence detector, the golden-staleness gate, the `--resolve-changed` checkpoint, and the `--force` scaffold cover the head-offset dual residual / sarf symbolic-emit / bound-transfer warm-residual / second-index fixture classes ([reuse confirmed / gap noted]). Analyzed the P6 fix-surfaces (ganges/gangesx `$141/$145/$149` translate-syntax root — a different root than sample's `$140`, their `.l`-init vars are *declared*; agreste double-`solve` scope-verify before treating CASE_B as an emit bug) — each `--resolve-changed`-gated, verified per-model (the cohort is multi-root). Scoped the P7 property fixtures (shape12 head-offset / shape13 sarf-symbolic / fawley 2-D second-index, fail-before/pass-after, gated on P1/P2/P3 landing) + the genuine-floor recompute (anchor 75) + the Epic-4-SUMMARY row-34 continuation. Authored `docs/planning/EPIC_4/SPRINT_34/TOOLING_AND_BACKLOG_ANALYSIS.md`; verified Unknowns 6.1, 6.2, 6.3, 7.1, 7.3. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected; the quality gate is not required. If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 34 Prep Task 10: Reusable-Tooling Audit + Backlog Fix-Surface Analysis

Audited the Sprint-28-33 tooling against the new Sprint-34 emit classes (harness incl.
case_c_objdef, presolve-divergence, golden-staleness, --resolve-changed, --force) —
[reuse confirmed / gap noted]. Analyzed the P6 fix-surfaces (ganges/gangesx $141/$145/$149
root, distinct from sample's $140; agreste double-solve scope-verify) — each
--resolve-changed-gated, verified per-model (multi-root). Scoped the P7 fixtures
(shape12/shape13/fawley, gated on P1/P2/P3) + the genuine-floor recompute (anchor 75)
+ the SUMMARY row-34 continuation.

## Deliverables
- docs/planning/EPIC_4/SPRINT_34/TOOLING_AND_BACKLOG_ANALYSIS.md
- KNOWN_UNKNOWNS.md: Unknowns 6.1, 6.2, 6.3, 7.1, 7.3 verified
- PREP_PLAN.md: Task 10 -> COMPLETE
- CHANGELOG.md: Task 10 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint34-task10
gh pr create --base main --title "Complete Sprint 34 Prep Task 10: Reusable-Tooling Audit + Backlog Fix-Surface Analysis" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run the gate only if you touched Python)
- [x] TOOLING_AND_BACKLOG_ANALYSIS.md has the tooling audit + the P6 fix-surface (ganges/gangesx root, agreste scope) + the P7 fixture scope
- [x] The cohort verified per-model (multi-root); the fixtures gated on P1/P2/P3; the anchor-75 recompute + SUMMARY row-34 noted
- [x] Unknowns 6.1, 6.2, 6.3, 7.1, 7.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 10 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 11 Prompt: Plan Sprint 34 Detailed Schedule

**Branch:** Create a new branch named `planning/sprint34-task11` from `main`

**Priority:** Critical (3–4 hours)

**Objective:** Produce the detailed 14-day Sprint 34 schedule (Day 0 setup + Days 1–13 execution) with day-by-day prompts, front-loading the deep tracks (P1, P2) + the fresh P4 lever so REPLANs surface by the Day-5 checkpoint, at ≤ 12 hours/day within the 168-hour budget (88–130h work-items).

**Unknowns Verified:** none directly — Task 11 *integrates* all verified unknowns into the schedule (it confirms every Critical/High unknown is resolved, or flags it as a Day-0 blocker).

**Prerequisites (read before starting):** *(requires Tasks 1–10 complete)*

- `docs/planning/EPIC_4/SPRINT_34/PREP_PLAN.md` §Task 11 + all prior prep task docs (Tasks 2–10)
- `docs/planning/EPIC_4/SPRINT_34/KNOWN_UNKNOWNS.md` (all 27 unknowns — confirm every Critical/High is VERIFIED or WRONG, none INCOMPLETE)
- `docs/planning/EPIC_4/SPRINT_34/PHASE_0_ACCEPTANCE_GATES.md` (Task 8) + `docs/planning/EPIC_4/SPRINT_34/REPLAN_RISK_ASSESSMENT.md` (Task 9)
- `docs/planning/EPIC_4/SPRINT_33/PLAN.md` + `docs/planning/EPIC_4/SPRINT_33/prompts/PLAN_PROMPTS.md` (the schedule + day-prompt templates) + `PROJECT_PLAN.md` §"Sprint 34" (Estimated Effort 88–130h, ≤ 12h/day)

**Tasks to Complete:**

1. Lay out Day 0: baseline confirmation (Task 2) + the per-track control re-confirms (mine, sarf, fawley, bound-transfer, camcge) + GO/NO-GO for Day 1.
2. Front-load the deep + fresh tracks: P1 (mine dual) + P2 (sarf) + P4 (bound-transfer, the fresh +Solve lever) across Days 1–7 so their REPLANs surface by the Day-5 checkpoint; P3 (fawley) + P5 (camcge/rocket) mid-sprint; P6 (failure-cohort — the S33 bucket source) + P7 in the back half.
3. Place the checkpoints: Day 5 (deep-track PROCEED/REPLAN + freed-budget reallocation) + Day 10; final retest Day 13 (≥ 3 `PYTHONHASHSEED`).
4. Write the day-by-day prompts: one per day, pasteable verbatim, each referencing its Phase-0 gate + design doc + REPLAN exit.
5. Verify the budget: ≤ 12h/day, ≤ 168h total, heaviest day ~11h; confirm the per-priority sizings sum to 88–130h.
6. Confirm all Known Unknowns resolved: if any Critical/High unknown is still `🔍 INCOMPLETE`, flag it as a Day-0 blocker.
7. Write `docs/planning/EPIC_4/SPRINT_34/PLAN.md` + `docs/planning/EPIC_4/SPRINT_34/prompts/PLAN_PROMPTS.md`.

**Deliverables (from PREP_PLAN.md §Task 11):**

- `docs/planning/EPIC_4/SPRINT_34/PLAN.md` — the 14-day schedule (Day 0 + Days 1–13) with the deep + P4 front-load, checkpoints, and budget verification
- `docs/planning/EPIC_4/SPRINT_34/prompts/PLAN_PROMPTS.md` — one pasteable prompt per day, each referencing its Phase-0 gate + design doc + REPLAN exit
- The budget confirmation (≤ 12h/day, ≤ 168h total, 88–130h work-items)

**Known Unknowns Updates:** Task 11 does not verify unknowns directly. Add a note to `KNOWN_UNKNOWNS.md` (e.g. in the Next Steps / a "Pre-Day-1 status" line) confirming all Critical/High unknowns are resolved (or listing any residual INCOMPLETE as a Day-0 blocker).

**PREP_PLAN.md Updates:** In §Task 11: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria. **Sprint 34 prep COMPLETE (Tasks 1–11)** — note this in the Result.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 34 Prep`, prepend:
```markdown
- **Prep Task 11 COMPLETE (YYYY-MM-DD):** Sprint 34 detailed schedule. Authored `docs/planning/EPIC_4/SPRINT_34/PLAN.md` (14-day schedule, Day 0 + Days 1–13) with the deep-track + P4 front-load — P1 mine dual + P2 sarf + P4 bound-transfer across Days 1–7 so their close-or-REPLAN gates fire by the **Day-5 checkpoint**; P3 fawley + P5 camcge/rocket mid-sprint; P6 failure-cohort (the S33 bucket source) + P7 infra in the back half; the Day-13 final retest (≥ 3 `PYTHONHASHSEED`) — and the budget verification (88–130h work-items, ≤ 12h/day, heaviest ~11h, ≤ 168h) + `docs/planning/EPIC_4/SPRINT_34/prompts/PLAN_PROMPTS.md` (one pasteable prompt per day, each referencing its Phase-0 gate + design doc + REPLAN exit). Integrates all 27 verified unknowns (no Day-0 blocker); the honest modal-flat-KPI projection (Task 9) binds the acceptance criteria (P1 High-prior on H_dual; P4 the fresh lever; P5 Epic-5/Sprint-35). **Sprint 34 prep COMPLETE (Tasks 1–11).** Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected; the quality gate is not required. If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 34 Prep Task 11: Sprint 34 Detailed Schedule

Authored PLAN.md (14-day schedule, Day 0 + Days 1-13) with the deep-track + P4
front-load (P1 mine dual + P2 sarf + P4 bound-transfer Days 1-7 -> REPLANs surface by
the Day-5 checkpoint; P3/P5 mid-sprint; P6/P7 back half; Day-13 final retest x3) + the
budget verification (88-130h, <=12h/day, heaviest ~11h, <=168h) + PLAN_PROMPTS.md (one
pasteable prompt per day). Integrates all 27 verified unknowns (no Day-0 blocker).
Sprint 34 prep COMPLETE (Tasks 1-11).

## Deliverables
- docs/planning/EPIC_4/SPRINT_34/PLAN.md
- docs/planning/EPIC_4/SPRINT_34/prompts/PLAN_PROMPTS.md
- PREP_PLAN.md: Task 11 -> COMPLETE (Sprint 34 prep COMPLETE)
- CHANGELOG.md: Task 11 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint34-task11
gh pr create --base main --title "Complete Sprint 34 Prep Task 11: Sprint 34 Detailed Schedule" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run the gate only if you touched Python)
- [x] PLAN.md lays out Day 0 + Days 1-13 with the deep + P4 front-load, the Day-5/10 checkpoints, and the budget verification
- [x] PLAN_PROMPTS.md has one pasteable prompt per day, each referencing its gate + design doc + REPLAN exit
- [x] All Critical/High unknowns confirmed resolved (no Day-0 blocker)
- [x] Task 11 Acceptance Criteria all checked; Sprint 34 prep COMPLETE (Tasks 1-11)
EOF
)"
```

**Then wait for reviewer comments.**

---

**Document Status:** 🔵 Active — Sprint 34 prep execution
**Last Updated:** 2026-07-18
**Owner:** Sprint 34 Planning Team

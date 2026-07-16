# Sprint 33 Prep Task Execution Prompts

Self-contained prompts for Sprint 33 Prep Tasks 2–11. Each prompt can be copy-pasted into a new conversation to execute one prep task end-to-end, including the Known Unknowns verification updates, the `PREP_PLAN.md` / `CHANGELOG.md` updates, the quality gate, the commit, and the Pull Request.

**Usage:**

1. Pick a task prompt below.
2. Paste it into a new conversation.
3. The agent creates the branch (`planning/sprint33-task<N>`), does the work, verifies its Known Unknowns, runs the quality gate, commits, pushes, and opens a PR.
4. Wait for reviewer comments on the PR.

Task 1 (Create Sprint 33 Known Unknowns List) is already ✅ COMPLETE — no prompt needed (see `docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md`).

**Dispatch order** (per the Prep Task Overview dependencies + the four critical paths in `docs/planning/EPIC_4/SPRINT_33/PREP_PLAN.md`; Task 1 is done, so tasks depending only on it — or on nothing — are immediately dispatchable):

- **Immediately dispatchable:** Task 2 (no dependencies); Task 6 + Task 7 (need only the completed Task 1)
- **After Task 2:** Task 3 + Task 4 + Task 5 (the three deep-track designs need Tasks 1, 2)
- **After Tasks 1 + 3 + 4 + 5 + 6 + 7:** Task 8 (the Phase-0 gate refresh consumes the per-track design docs)
- **After Tasks 1 + 8:** Task 10 (the tooling-readiness + backlog analysis reuses the gates)
- **After Tasks 3 + 4 + 5 + 8:** Task 9 (the REPLAN assessment consumes the designs + the gates)
- **After all (final integration):** Task 11

**Critical path:** Task 1 → Task 3 → Task 8 → Task 9 → Task 11.

**Cross-cutting conventions for every prompt below:**

- Branch from `main`; the PR targets `main`. Branch name: `planning/sprint33-task<N>`.
- User preferences (enforce in every commit/PR): **NO `Co-Authored-By` lines** in commit messages; **NO "Generated with Claude Code"** in PR descriptions.
- Replace `YYYY-MM-DD` with the actual date at execution time.
- These are **docs/design/analysis-only** prep tasks — no Python source changes are expected (the fixes/scripts they design are *built in-sprint*, not in prep; the KKT-residual harness, presolve-divergence detector, golden-staleness gate, `--resolve-changed` mode, and the `--force` scaffold already exist on `main`). Run the quality gate before committing **only if you touched Python** — per the project's per-day workflow (quality gate only if `*.py` changed), a docs-only task skips it. If you did touch Python, `make typecheck && make lint && make format && make test` must pass.
- **PR24/PR27 discipline:** every Sprint-32 control-confirmed root cause is a Day-0-**re-confirm hypothesis**, never fact — including its *sign* and *sufficiency*. Sprint 32 REPLAN'd all five deep tracks after a `/tmp` control refuted the original premise, and corrected two materially-wrong designs (camcge's `nu_mps_fx.l = -mps.m` → `= mps.m`; mine's `N`-derivation, proven insufficient at 6 bound-active rows). Record the symptom + reproducer; frame the fix surface as a hypothesis to re-trace; gate any high-blast-radius change on a `/tmp` control experiment BEFORE the `src/` change.
- **Assert `modelstat` before reading an objective off a solve** (the Sprint-31 measurement-error lesson: relaxing `x.up=inf` produced 34 unmatched-variable errors, so the "MS-1 17500" was the embedded LP, not the MCP). The `x.up=inf` experiment is **BANNED** for mine.
- **Check the dual side** (the Sprint-30 camcge lesson): any structural transform that drops/adds rows must be verified against the KKT *dual*, not just the primal solution set.
- Every Known-Unknowns update uses the verification block: **Status** (✅ VERIFIED / ❌ WRONG), **Verified by**, **Date**, **Findings**, **Evidence**, **Decision** — replacing the `🔍 **Status:** INCOMPLETE` stub.

---

## Task 2 Prompt: Sprint 32 → Sprint 33 Day-0 Baseline + Genuine-Floor Re-Baseline (PR15 + PR17 + PR25)

**Branch:** Create a new branch named `planning/sprint33-task2` from `main`

**Priority:** Critical (3–4 hours)

**Objective:** Establish the Sprint 33 Day-0 baseline with per-model bucket provenance, confirm it equals the Sprint 32 close, and re-affirm the PR25 genuine-vs-methodology floor anchor (74) that Sprint 33's Match/genuine-floor targets ramp from.

**Unknowns Verified:** 1.1 (Day-0 mine bucket, contributes), 3.1 (Day-0 fawley bucket, contributes), 7.2 (the PR25 genuine-floor anchor 74)

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_33/PREP_PLAN.md` §Task 2
- `docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md` §Unknowns 1.1, 3.1, 7.2
- `docs/planning/EPIC_4/SPRINT_32/BASELINE_METRICS.md` (the bucket-provenance + genuine-vs-methodology template + the 142-corpus vs all-219 recompute) + `docs/planning/EPIC_4/SPRINT_32/SPRINT_RETROSPECTIVE.md` §1 (Solve 107 / Match 92 / genuine floor 74 / model_infeasible 7 / Translate 135 / Tests 5,085 / all-219 Match 95)
- `data/gamslib/gamslib_status.json` (byte-unchanged since the S31 close `4cbf8bff`) + `scripts/gamslib/run_full_test.py` `--resolve-changed` mode + `get_candidate_models` (142-candidate definition)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 33" (the footnote-⁸ Match re-baseline / genuine-floor ramp S33 ≥ 75)

**Tasks to Complete:**

1. Confirm the Day-0 git anchor: derive the Sprint 32 close SHA and verify no `src/`/`scripts/` drift since — reuse the committed DB (no fresh retest) if clean:
   ```bash
   S32=$(git log --grep='SPRINT 32 CLOSED' --format=%H | tail -1)
   [ -n "$S32" ] || { echo "ERROR: could not resolve the Sprint 32 close SHA — resolve it manually before diffing"; exit 1; }
   git diff --quiet "$S32"..HEAD -- src/ scripts/ && echo "no src/ drift — reuse committed DB" || git diff --stat "$S32"..HEAD -- src/ scripts/
   md5 -q data/gamslib/gamslib_status.json   # macOS; on Linux: md5sum ...  (confirm byte-unchanged since 4cbf8bff)
   ```
2. Recompute the canonical bucket tally from the committed DB (`get_candidate_models`, 142): Parse 142 / Translate 135 / Solve 107 / Match 92 / model_infeasible 7. Enumerate the 7 model_infeasible + the path_syntax_error / path_solve_terminated members by name.
3. Record per-model bucket provenance (Day-0 → expected Day-13) for every carryforward-touched model: mine, sarf, fawley, camcge, rocket, hhfair/irscge/lrgcge/moncge, agreste, cesam, lnts.
4. Re-affirm the PR25 genuine-floor anchor 74 (cold-emit-correct genuine vs presolve-methodology); identify the mover levers (mine [P1] / fawley [P3] cold-matches → ≥ 75) + the footnote-⁸ ramp alignment; record the 142-corpus vs all-219 (95) distinction.
5. Confirm determinism ×3 `PYTHONHASHSEED` {0,1,42} on the Day-0 emit; pin the Day-0 SHA + confirm `--resolve-changed --since-commit <SHA>` selects 0 changed at Day 0.
6. Write `docs/planning/EPIC_4/SPRINT_33/BASELINE_METRICS.md`.

**Deliverables (from PREP_PLAN.md §Task 2):**

- `docs/planning/EPIC_4/SPRINT_33/BASELINE_METRICS.md` with the confirmed Day-0 buckets (142 corpus + all-219 Match 95)
- Per-model bucket provenance table for every carryforward-touched model (Day-0 → expected Day-13)
- The PR25 genuine-floor anchor (74) + the mover levers
- Determinism ×3 confirmation + the resolved Day-0 git anchor SHA
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 3.1, 7.2

**Known Unknowns Updates:** For Unknowns 1.1, 3.1, 7.2 in `docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md`, replace the `🔍 Status: INCOMPLETE` stub with: **Status** ✅ VERIFIED (or ❌ WRONG + correction), **Verified by** Task 2, **Date**, **Findings** (the Day-0 mine/fawley buckets + the genuine-floor-74 reproduction + the ramp alignment + the 142-vs-219 split), **Evidence** (DB recompute + partition), **Decision** (the ≥ 75 conversion map). Note that the *fix-surface* aspects of 1.1/3.1 are verified by Tasks 3/5 (Task 2 verifies only their Day-0-bucket aspect).

**PREP_PLAN.md Updates:** In §Task 2: `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`; add `**Completed:** YYYY-MM-DD`; fill "Changes" (what was measured/authored) + "Result" (the Day-0 baseline + genuine floor 74 + corpus scope); check off all Acceptance Criteria (`- [ ]` → `- [x]`), including the "Unknowns 1.1, 3.1, 7.2 verified" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 33 Prep`, prepend:
```markdown
- **Prep Task 2 COMPLETE (YYYY-MM-DD):** Sprint 33 Day-0 baseline = Sprint 32 close (Solve 107 / Match 92 / genuine floor 74 / model_infeasible 7 / Translate 135 / Tests 5,085 / all-219 Match 95; DB byte-unchanged since `4cbf8bff`, no fresh retest). Genuine floor 74 reproduced from the PR25 partition with the → ≥ 75 conversion map (mine P1 / fawley P3) + the footnote-⁸ ramp alignment; the 142-corpus vs all-219 distinction recorded. Per-carryforward-model Day-0 bucket provenance pinned; determinism ✅ ×3; `--resolve-changed` anchor confirmed (0 at Day 0). Verified Unknowns 1.1, 3.1, 7.2. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected, so the quality gate is not required (docs-only changes skip it, per the project convention). If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 33 Prep Task 2: Day-0 Baseline + Genuine-Floor Re-Baseline

Day-0 = Sprint 32 close (Solve 107 / Match 92 / genuine floor 74 / model_infeasible 7
/ Translate 135 / Tests 5,085 / all-219 Match 95; DB byte-unchanged since 4cbf8bff, no
fresh retest). Genuine floor 74 reproduced from the PR25 partition with the -> >=75
conversion map (mine P1 / fawley P3). 142-corpus vs all-219 distinction recorded.
Day-0 SHA pinned; --resolve-changed anchor confirmed (0 at Day 0); determinism x3.

## Deliverables
- docs/planning/EPIC_4/SPRINT_33/BASELINE_METRICS.md
- KNOWN_UNKNOWNS.md: Unknowns 1.1, 3.1, 7.2 verified
- PREP_PLAN.md: Task 2 -> COMPLETE
- CHANGELOG.md: Task 2 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint33-task2
gh pr create --base main --title "Complete Sprint 33 Prep Task 2: Day-0 Baseline + Genuine-Floor Re-Baseline" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run `make typecheck && make lint && make format && make test` only if you touched Python)
- [x] BASELINE_METRICS.md records Day-0 = Sprint 32 close + per-target buckets + genuine floor 74 + the 142-vs-219 split
- [x] Day-0 = Sprint 32 close confirmed (no src/ drift; DB byte-unchanged since 4cbf8bff)
- [x] Unknowns 1.1, 3.1, 7.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 2 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 3 Prompt: mine Head-Offset Bound-Active Cross-Term — Localization + Re-Derivation Design (Priority 1 Foundation)

**Branch:** Create a new branch named `planning/sprint33-task3` from `main`

**Priority:** Critical (6–8 hours)

**Objective:** Turn the Sprint-32 Day-1 control finding — the bound-multiplier `N`-derivation closes `stat_x` by construction but yields a wrong-sign residual at 6 bound-active rows — into a concrete, stationarity-consistent **re-derivation of the head-offset `stat_x` cross-term** that vanishes at every bound-active row, sizing Sprint 33's deepest (+1 Solve) track before the schedule is set.

**Unknowns Verified:** 1.1, 1.2, 1.3, 1.4, 1.5

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_33/PREP_PLAN.md` §Task 3
- `docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md` §Category 1 (Unknowns 1.1–1.5)
- `docs/planning/EPIC_4/SPRINT_32/MINE_5TH_COUPLING_REPLAN.md` (the wrong-sign `N` at the 6 bound-active rows `x(1,3,{1,2,3})`, `x(3,1,2)`, `x(3,2,1)`, `x(4,1,1)`) + the S31 head-offset IR foundation
- `src/kkt/stationarity.py` (the head-offset `stat_x` cross-term emit site; most emit bugs live here, NOT the AD layer) + the `EquationDef.head_domain_offsets` IR
- `docs/research/multidimensional_indexing.md`, `docs/research/nested_subset_indexing_research.md`
- `scripts/diagnostics/kkt_residual.py` (the harness for the `/tmp` control)

**Tasks to Complete:**

1. Re-confirm the Day-1 control (PR24 Day-0 re-confirm): re-run the `/tmp` mine control, **assert `modelstat`** (the `x.up=inf` experiment is BANNED), reproduce `N=0` interior + wrong-sign `N` at the 6 bound-active rows.
2. Localize the head-offset `stat_x` cross-term emit site in `src/kkt/stationarity.py`; trace how the `head_domain_offsets` shifted-label pairing feeds the term `sum(k, lam_pr(k,l,i−li,j−lj)$c − lam_pr(k,l−1,i,j)$c)`.
3. Hand-derive the correct bound-active-row stationarity; isolate which term carries the opposite bound's sign at a bound-active row vs an interior row.
4. Design the re-derivation as a `file:line` fix-surface **hypothesis** (sign correction, `$`-guard, or structural change); note whether it needs the shifted-label pairing or new IR plumbing.
5. Specify the pre-`src/` `/tmp` control: warm residual → 0 at all 6 bound-active rows AND unchanged at interior rows, then presolve MS-1 at 17500.
6. Size the track honestly (18–24h) + pin the deeper-coupling REPLAN exit.
7. Write `docs/planning/EPIC_4/SPRINT_33/MINE_CROSSTERM_DESIGN.md`.

**Deliverables (from PREP_PLAN.md §Task 3):**

- `docs/planning/EPIC_4/SPRINT_33/MINE_CROSSTERM_DESIGN.md` with the hand-derived bound-active-row stationarity + the cross-term re-derivation
- The `file:line` fix-surface hypothesis in `src/kkt/stationarity.py`
- The pre-`src/` `/tmp` control spec (warm residual → 0 at bound-active rows, then MS-1)
- The honest 18–24h sizing + the explicit deeper-coupling REPLAN exit
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3, 1.4, 1.5

**Known Unknowns Updates:** For Unknowns 1.1–1.5, replace the `🔍 Status: INCOMPLETE` stub with **Status** (✅ VERIFIED / ❌ WRONG), **Verified by** Task 3, **Date**, **Findings** (the localized cross-term + the offending term's sign + the IR-pairing confirmation + the sizing), **Evidence** (the `/tmp` control residual per row + the hand-derivation), **Decision** (the re-derivation hypothesis + the REPLAN exit). If the control shows a deeper coupling, mark 1.1 ❌ WRONG and record the deeper-coupling finding.

**PREP_PLAN.md Updates:** In §Task 3: `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria (including "Unknowns 1.1, 1.2, 1.3, 1.4, 1.5 verified").

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 33 Prep`, prepend:
```markdown
- **Prep Task 3 COMPLETE (YYYY-MM-DD):** mine #1443 head-offset bound-active cross-term design. Re-confirmed the Sprint-32 Day-1 control (wrong-sign `N` at the 6 bound-active rows, `modelstat` asserted, `x.up=inf` BANNED); localized the `stat_x` cross-term emit site in `src/kkt/stationarity.py`; hand-derived the correct bound-active-row stationarity + designed the cross-term re-derivation (file:line hypothesis) with the pre-`src/` `/tmp` control (residual → 0 at bound-active rows then MS-1 at 17500). Sized 18–24h + the deeper-coupling REPLAN exit. Verified Unknowns 1.1, 1.2, 1.3, 1.4, 1.5. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected, so the quality gate is not required (docs-only changes skip it, per the project convention). If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 33 Prep Task 3: mine Head-Offset Cross-Term Re-Derivation Design

Re-confirmed the Sprint-32 Day-1 control (wrong-sign N at 6 bound-active rows, modelstat
asserted, x.up=inf BANNED); localized the stat_x head-offset cross-term in
src/kkt/stationarity.py; hand-derived the correct bound-active-row stationarity and
designed the cross-term re-derivation (file:line hypothesis) + the pre-src /tmp control
(residual -> 0 at bound-active rows then MS-1 at 17500). Sized 18-24h + deeper-coupling
REPLAN exit.

## Deliverables
- docs/planning/EPIC_4/SPRINT_33/MINE_CROSSTERM_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 1.1-1.5 verified
- PREP_PLAN.md: Task 3 -> COMPLETE
- CHANGELOG.md: Task 3 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint33-task3
gh pr create --base main --title "Complete Sprint 33 Prep Task 3: mine Head-Offset Cross-Term Re-Derivation Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run `make typecheck && make lint && make format && make test` only if you touched Python)
- [x] MINE_CROSSTERM_DESIGN.md has the hand-derivation + the file:line hypothesis + the /tmp control spec
- [x] Day-1 control re-confirmed (wrong-sign N at the 6 bound-active rows, modelstat asserted)
- [x] Unknowns 1.1-1.5 verified in KNOWN_UNKNOWNS.md
- [x] Task 3 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 4 Prompt: sarf Symbolic Parametric `stat_task` Emit-Subsystem Design (Priority 2 Foundation)

**Branch:** Create a new branch named `planning/sprint33-task4` from `main`

**Priority:** High (5–7 hours)

**Objective:** Design the O(active = 398) symbolic parametric `stat_task` emit subsystem that eliminates the 369,024-column materialization *everywhere* it enumerates (the constraint Jacobian via `acost3`, the variable enumeration, and the variable stationarity), so sarf recovers to translate (+1 Translate → 136).

**Unknowns Verified:** 2.1, 2.2, 2.3, 2.4, 2.5

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_33/PREP_PLAN.md` §Task 4
- `docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md` §Category 2 (Unknowns 2.1–2.5)
- `docs/planning/EPIC_4/SPRINT_32/SARF_TRANSLATE_REPLAN.md` + `docs/planning/EPIC_4/SPRINT_32/SARF_STAT_TASK_SPARSIFICATION_DESIGN.md` (the 369K `acost3`+variable-path enumeration; the banked 7-term derivation; the working 2-D detector)
- `src/ad/constraint_jacobian.py` (the `compute_constraint_jacobian` blow-up) + `src/kkt/stationarity.py`
- `docs/research/multidimensional_indexing.md`

**Tasks to Complete:**

1. Re-profile the timeout (PR24 Day-0 re-confirm); confirm the three enumeration sites: `compute_constraint_jacobian` (via `acost3`), the variable enumeration, and the variable stationarity for `task(g,t,mn,mn)`.
2. Design the O(active) elimination at each site — how the `$taskposs(g,t)`-active subset (|active| = 398) replaces the 369K enumeration in the Jacobian, the variable list, and the stationarity.
3. Specify the single symbolic guarded emit `stat_task(g,t,m,n)$taskposs(g,t)` (the banked 7-term derivation) + `task.fx$(not active)=0`, with the `J_gᵀ·lam` cross-terms differentiated **once parametrically** (no set-name-literal multiplier indices).
4. Define the atomic-landing requirement (gate + parametric cross-terms + `task.fx` land together) + the O(active) budget test (time `sarf_mcp.gms` vs srpchase's 6.56s reference; grep-scan clean; byte-stable golden).
5. Size the track (20–28h) + pin the timeout-re-trigger REPLAN exit.
6. Write `docs/planning/EPIC_4/SPRINT_33/SARF_EMIT_SUBSYSTEM_DESIGN.md`.

**Deliverables (from PREP_PLAN.md §Task 4):**

- `docs/planning/EPIC_4/SPRINT_33/SARF_EMIT_SUBSYSTEM_DESIGN.md` with all three enumeration sites + the O(active) elimination per site
- The single symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)` emit spec (7-term derivation) + `task.fx` + parametric cross-terms
- The atomic-landing requirement + the O(active) budget/grep/byte-stable acceptance test
- The 20–28h sizing + the timeout-re-trigger REPLAN exit
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.1, 2.2, 2.3, 2.4, 2.5

**Known Unknowns Updates:** For Unknowns 2.1–2.5, replace the stub with **Status** (✅ VERIFIED / ❌ WRONG), **Verified by** Task 4, **Date**, **Findings** (the three sites confirmed + the active-subset count + the 7-term derivation check + the `task.fx` handling), **Evidence** (the re-profile + the hand-derivation + the grep-scan), **Decision** (the atomic-landing subsystem design + the REPLAN exit).

**PREP_PLAN.md Updates:** In §Task 4: `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria (including "Unknowns 2.1, 2.2, 2.3, 2.4, 2.5 verified").

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 33 Prep`, prepend:
```markdown
- **Prep Task 4 COMPLETE (YYYY-MM-DD):** sarf #1385 symbolic parametric `stat_task` emit-subsystem design. Re-profiled the timeout to `compute_constraint_jacobian` and confirmed all three 369K enumeration sites (`acost3` Jacobian + variable enumeration + variable stationarity); designed the O(active=398) elimination per site + the single symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)` emit (7-term derivation, no set-name literals) + `task.fx$(not active)=0`, with the atomic-landing requirement + the O(active) budget test (vs srpchase 6.56s). Sized 20–28h + the timeout-re-trigger REPLAN exit. Verified Unknowns 2.1, 2.2, 2.3, 2.4, 2.5. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected, so the quality gate is not required (docs-only changes skip it, per the project convention). If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 33 Prep Task 4: sarf Symbolic stat_task Emit-Subsystem Design

Re-profiled the timeout to compute_constraint_jacobian; confirmed all three 369K
enumeration sites (acost3 Jacobian + variable enumeration + variable stationarity);
designed the O(active=398) elimination per site + the single symbolic guarded
stat_task(g,t,m,n)$taskposs(g,t) emit (7-term derivation, no set-name literals) +
task.fx$(not active)=0, with the atomic-landing requirement + the O(active) budget test.
Sized 20-28h + timeout-re-trigger REPLAN exit.

## Deliverables
- docs/planning/EPIC_4/SPRINT_33/SARF_EMIT_SUBSYSTEM_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 2.1-2.5 verified
- PREP_PLAN.md: Task 4 -> COMPLETE
- CHANGELOG.md: Task 4 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint33-task4
gh pr create --base main --title "Complete Sprint 33 Prep Task 4: sarf Symbolic stat_task Emit-Subsystem Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run `make typecheck && make lint && make format && make test` only if you touched Python)
- [x] SARF_EMIT_SUBSYSTEM_DESIGN.md names all three sites + the O(active) elimination + the atomic-landing + budget test
- [x] The 7-term derivation checked against a hand-derivation; no set-name literals
- [x] Unknowns 2.1-2.5 verified in KNOWN_UNKNOWNS.md
- [x] Task 4 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 5 Prompt: fawley #1111/#1112 Second-Index Cross-Term Generalization Design (Priority 3 Foundation)

**Branch:** Create a new branch named `planning/sprint33-task5` from `main`

**Priority:** High (4–6 hours)

**Objective:** Design the extension of the landed #1111/#1112 second-index gate from the variable's-first-index shape (mbal) to the variable's-second-index-summed shape (qsb/pbal), so `max|stat_bq| → 0` (beyond the 96% the `/tmp` patch reached) and fawley reaches MS-1 at the LP optimum 2899.25 (+1 Solve).

**Unknowns Verified:** 3.1, 3.2, 3.3, 3.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_33/PREP_PLAN.md` §Task 5
- `docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md` §Category 3 (Unknowns 3.1–3.4)
- `docs/planning/EPIC_4/SPRINT_32/P6_BACKLOG_RETRIAGE.md` §3 (the qsb/pbal `sameas` gap; the `/tmp` patch 473 → 18 [96%]; the residual 18.47 + the MS-5 LP-convergence)
- `src/kkt/stationarity.py` (`_var_at_two_indices_complement` + `_build_complement_index_sum` — the landed #1111/#1112 core covering mbal/polygon/ps2)
- `docs/research/nested_subset_indexing_research.md`, `docs/research/multidimensional_indexing.md`

**Tasks to Complete:**

1. Re-confirm the Day-11 control (PR24 Day-0 re-confirm): re-run the `/tmp` fawley `$(sameas(cfq__,cf))` patch; confirm `max|stat_bq|` 473 → 18 (96%); localize the residual 18.47 term.
2. Diagnose the residual — is 18.47 a second over-sum (a further gate-leak) or a distinct qsb/pbal term? Determine whether closing it fixes the MS-5 LP-convergence.
3. Design the gate generalization in `src/kkt/stationarity.py` — extend the second-index gate from the variable's-first-index shape (mbal) to the variable's-second-index-summed shape (qsb/pbal) so `max|stat_bq| → 0`.
4. Specify the no-regression requirement (`--resolve-changed --since-commit 4cbf8bff` GO; no polygon/ps2/mbal move) + the `/tmp` control (`max|stat_bq| → 0`, MS-1 at 2899.25) BEFORE any `src/` change.
5. Size the track (12–18h) + pin the gate-leak REPLAN exit; confirm whether fawley cold-matches (genuine floor +1).
6. Write `docs/planning/EPIC_4/SPRINT_33/FAWLEY_SECOND_INDEX_DESIGN.md`.

**Deliverables (from PREP_PLAN.md §Task 5):**

- `docs/planning/EPIC_4/SPRINT_33/FAWLEY_SECOND_INDEX_DESIGN.md` with the residual-18.47 diagnosis + the gate-generalization design
- The `file:line` fix-surface hypothesis in `src/kkt/stationarity.py` (second-index gate extension)
- The no-regression (`--resolve-changed`) + `/tmp` (`max|stat_bq| → 0`, MS-1 at 2899.25) control specs
- The 12–18h sizing + the gate-leak REPLAN exit
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.2, 3.3, 3.4

**Known Unknowns Updates:** For Unknowns 3.1–3.4, replace the stub with **Status** (✅ VERIFIED / ❌ WRONG), **Verified by** Task 5, **Date**, **Findings** (the residual-18.47 diagnosis + the gate-generalization shape + the no-regression result + the cold-match/sizing), **Evidence** (the `/tmp` control + the `--resolve-changed` GO), **Decision** (the gate-generalization hypothesis + the REPLAN exit). If the residual is non-emit, mark 3.2 accordingly.

**PREP_PLAN.md Updates:** In §Task 5: `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria (including "Unknowns 3.1, 3.2, 3.3, 3.4 verified").

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 33 Prep`, prepend:
```markdown
- **Prep Task 5 COMPLETE (YYYY-MM-DD):** fawley #1111/#1112 second-index generalization design. Re-confirmed the Sprint-32 Day-11 control (`max|stat_bq|` 473 → 18, 96%); localized + diagnosed the residual 18.47; designed the second-index gate generalization (variable's-first-index → variable's-second-index-summed, covering qsb/pbal) in `src/kkt/stationarity.py` with the no-regression (`--resolve-changed`) + `/tmp` (`max|stat_bq| → 0`, MS-1 at 2899.25) controls. Sized 12–18h + the gate-leak REPLAN exit. Verified Unknowns 3.1, 3.2, 3.3, 3.4. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected, so the quality gate is not required (docs-only changes skip it, per the project convention). If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 33 Prep Task 5: fawley Second-Index Generalization Design

Re-confirmed the Sprint-32 Day-11 control (max|stat_bq| 473 -> 18, 96%); localized and
diagnosed the residual 18.47; designed the second-index gate generalization (variable's-
first-index -> variable's-second-index-summed, covering qsb/pbal) in
src/kkt/stationarity.py with the no-regression (--resolve-changed) + /tmp (max|stat_bq|
-> 0, MS-1 at 2899.25) controls. Sized 12-18h + gate-leak REPLAN exit.

## Deliverables
- docs/planning/EPIC_4/SPRINT_33/FAWLEY_SECOND_INDEX_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 3.1-3.4 verified
- PREP_PLAN.md: Task 5 -> COMPLETE
- CHANGELOG.md: Task 5 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint33-task5
gh pr create --base main --title "Complete Sprint 33 Prep Task 5: fawley Second-Index Generalization Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run `make typecheck && make lint && make format && make test` only if you touched Python)
- [x] FAWLEY_SECOND_INDEX_DESIGN.md has the residual-18.47 diagnosis + the gate design + the no-regression + /tmp controls
- [x] Day-11 control re-confirmed (473 -> 18, 96%)
- [x] Unknowns 3.1-3.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 5 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 6 Prompt: camcge Dual-Consistent Walras Numéraire Design + Degeneracy-Detector Scope (Priority 4 / Epic 5)

**Branch:** Create a new branch named `planning/sprint33-task6` from `main`

**Priority:** High (4–5 hours)

**Objective:** Design the per-model-numéraire declaration + dual-consistent Walras redefinition that reaches MS-1 at omega 191.7346 in a `/tmp` prototype, plus the S1∧S2∧S3 degeneracy-detector scope that flags only camcge (not irscge/lrgcge/moncge/stdcge) — resolving #1330 or empirically Epic-5-scoping it.

**Unknowns Verified:** 4.1, 4.2, 4.3, 4.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_33/PREP_PLAN.md` §Task 6
- `docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md` §Category 4 (Unknowns 4.1–4.4)
- `docs/planning/EPIC_4/SPRINT_32/CAMCGE_WALRAS_REPLAN.md` + `docs/planning/EPIC_4/SPRINT_32/CAMCGE_STAT_MPS_WALRAS_DESIGN.md` (omega 191.7346 but MS-4; the rank-deficiency on gdp/depreq/hhsaveq/gruse; the drop-row-breaks-the-dual finding) + `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md`
- `docs/research/convexity_detection.md`
- `scripts/diagnostics/kkt_residual.py`

**Tasks to Complete:**

1. Re-confirm step 2 (PR24 Day-0 re-confirm): re-run the numéraire `/tmp` prototype, **assert `modelstat`**, reproduce omega 191.7346 at MS-4 with the Walras singularity on the four accounting identities.
2. Design the per-model-numéraire declaration + Walras redefinition — keep every market-clearing row; redefine the redundant market's dual via Walras' law so the reduced system is full-rank while the dual stays available (**check the dual side**, not just the primal).
3. Define the S1∧S2∧S3 detector scope; run it across the five CGE models (camcge + irscge/lrgcge/moncge/stdcge) and confirm it flags only camcge.
4. Specify the `/tmp` prototype gate (MS-1 at omega 191.7346, `modelstat` asserted) BEFORE any `src/` change; decide the Sprint-33-vs-Epic-5 disposition; confirm the step-1 `nu_mps_fx` fix stays correct under the numéraire change.
5. Size the track (10–16h) + pin the Epic-5-deferral REPLAN exit.
6. Write `docs/planning/EPIC_4/SPRINT_33/CAMCGE_WALRAS_DESIGN.md`.

**Deliverables (from PREP_PLAN.md §Task 6):**

- `docs/planning/EPIC_4/SPRINT_33/CAMCGE_WALRAS_DESIGN.md` with the per-model-numéraire + dual-consistent Walras redefinition
- The S1∧S2∧S3 detector scope (flags only camcge)
- The `/tmp` prototype gate (MS-1 at omega 191.7346, `modelstat` asserted)
- The Sprint-33-vs-Epic-5 disposition + the 10–16h sizing + the Epic-5-deferral REPLAN exit
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.2, 4.3, 4.4

**Known Unknowns Updates:** For Unknowns 4.1–4.4, replace the stub with **Status** (✅ VERIFIED / ❌ WRONG), **Verified by** Task 6, **Date**, **Findings** (the prototype MS result + the detector scope across the 5 CGE models + the disposition + the step-1 stability), **Evidence** (the `/tmp` prototype + the detector run), **Decision** (in-scope vs Epic-5-deferred + the REPLAN exit).

**PREP_PLAN.md Updates:** In §Task 6: `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria (including "Unknowns 4.1, 4.2, 4.3, 4.4 verified").

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 33 Prep`, prepend:
```markdown
- **Prep Task 6 COMPLETE (YYYY-MM-DD):** camcge #1330 dual-consistent Walras numéraire design (Epic 5). Re-confirmed step 2 (omega 191.7346 at MS-4, Walras singularity on gdp/depreq/hhsaveq/gruse, `modelstat` asserted); designed the per-model-numéraire + Walras redefinition (full-rank, dual available — dual side checked); scoped the S1∧S2∧S3 detector (flags only camcge across the 5 CGE models); specified the `/tmp` prototype gate (MS-1 at omega 191.7346) + the Sprint-33-vs-Epic-5 disposition. Sized 10–16h + the Epic-5-deferral REPLAN exit. Verified Unknowns 4.1, 4.2, 4.3, 4.4. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected, so the quality gate is not required (docs-only changes skip it, per the project convention). If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 33 Prep Task 6: camcge Dual-Consistent Walras Numeraire Design

Re-confirmed step 2 (omega 191.7346 at MS-4, Walras singularity on gdp/depreq/hhsaveq/
gruse, modelstat asserted); designed the per-model-numeraire + Walras redefinition
(full-rank, dual available); scoped the S1∧S2∧S3 detector (flags only camcge across the
5 CGE models); specified the /tmp prototype gate (MS-1 at omega 191.7346) + the Sprint-33-
vs-Epic-5 disposition. Sized 10-16h + Epic-5-deferral REPLAN exit.

## Deliverables
- docs/planning/EPIC_4/SPRINT_33/CAMCGE_WALRAS_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 4.1-4.4 verified
- PREP_PLAN.md: Task 6 -> COMPLETE
- CHANGELOG.md: Task 6 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint33-task6
gh pr create --base main --title "Complete Sprint 33 Prep Task 6: camcge Dual-Consistent Walras Numeraire Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run `make typecheck && make lint && make format && make test` only if you touched Python)
- [x] CAMCGE_WALRAS_DESIGN.md has the redefinition + the detector scope + the /tmp gate + the disposition
- [x] Step 2 re-confirmed (omega 191.7346 at MS-4, modelstat asserted); detector flags only camcge
- [x] Unknowns 4.1-4.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 6 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 7 Prompt: rocket PATH-Consultation Submission Package + hhfair/CGE Case-c Forcing Plan (Priority 5)

**Branch:** Create a new branch named `planning/sprint33-task7` from `main`

**Priority:** Medium (2–3 hours)

**Objective:** Finalize the submission of the packaged rocket PATH-consultation input to the Sprint-34 consultation, and plan the `--force` (homotopy/multistart/optfile) lever survey for rocket + the hhfair/CGE Case-c family — the presolve-recovered non-convex models whose only remaining avenue is forcing/reformulation.

**Unknowns Verified:** 5.1, 5.2, 5.3

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_33/PREP_PLAN.md` §Task 7
- `docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md` §Category 5 (Unknowns 5.1–5.3)
- `docs/planning/EPIC_4/SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` (Status: FINALIZED — the concrete question + ruled-out-lever survey + `--force` scaffold) + `docs/planning/EPIC_4/SPRINT_32/CASE_C_CLASSIFIER_DESIGN.md` (the `case_c_objdef` family; ISSUE_1236 CLOSED; sign flip BANNED)
- `docs/research/convexity_detection.md`, `docs/research/minmax_objective_reformulation.md`
- The `--force {homotopy,multistart,optfile}` scaffold + `scripts/diagnostics/kkt_residual.py`

**Tasks to Complete:**

1. Confirm the rocket package is submission-ready (concrete question + ruled-out-lever survey + `--force` outputs); define the Sprint-34 submission mechanism (what is handed off, to whom).
2. Plan the `--force` lever survey (homotopy/multistart/optfile) on rocket + hhfair/irscge/lrgcge/moncge; define "a lever crosses" (a recovered +Solve at MS-1) vs "survey banked for the consultation".
3. Re-affirm the Case-c gate — each model's residual clean at the NLP point (Case-c, not a latent emit bug); the sign flip stays BANNED (do NOT re-litigate it).
4. Size the track (8–12h) + note the conditional (not-a-firm-KPI) nature of any +Solve.
5. Write `docs/planning/EPIC_4/SPRINT_33/ROCKET_CASEC_FORCING_PLAN.md`.

**Deliverables (from PREP_PLAN.md §Task 7):**

- `docs/planning/EPIC_4/SPRINT_33/ROCKET_CASEC_FORCING_PLAN.md` with the Sprint-34 submission mechanism + the `--force` lever survey plan
- The Case-c re-confirm gate (residual clean at the NLP point before forcing) + the BANNED sign-flip note
- The 8–12h sizing + the conditional +Solve note
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.1, 5.2, 5.3

**Known Unknowns Updates:** For Unknowns 5.1–5.3, replace the stub with **Status** (✅ VERIFIED / ❌ WRONG), **Verified by** Task 7, **Date**, **Findings** (the submission completeness + the `--force` survey plan + the Case-c/sign-flip re-confirm), **Evidence** (the package review + the harness re-run), **Decision** (the Sprint-34 hand-off + the forcing survey scope).

**PREP_PLAN.md Updates:** In §Task 7: `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria (including "Unknowns 5.1, 5.2, 5.3 verified").

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 33 Prep`, prepend:
```markdown
- **Prep Task 7 COMPLETE (YYYY-MM-DD):** rocket PATH-consultation submission package + hhfair/CGE Case-c forcing plan. Confirmed the FINALIZED rocket consultation input is submission-ready + defined the Sprint-34 hand-off mechanism; planned the `--force` (homotopy/multistart/optfile) lever survey for rocket + the hhfair/CGE Case-c family with the "lever crosses" (+Solve) vs "banked" criteria; re-affirmed the Case-c gate (residual clean at the NLP point) + the BANNED sign flip. Sized 8–12h + the conditional +Solve note. Verified Unknowns 5.1, 5.2, 5.3. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected, so the quality gate is not required (docs-only changes skip it, per the project convention). If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 33 Prep Task 7: rocket PATH-Consultation Submission + Case-c Forcing Plan

Confirmed the FINALIZED rocket consultation input is submission-ready + defined the
Sprint-34 hand-off mechanism; planned the --force (homotopy/multistart/optfile) lever
survey for rocket + the hhfair/CGE Case-c family with the "lever crosses" (+Solve) vs
"banked" criteria; re-affirmed the Case-c gate (residual clean at the NLP point) + the
BANNED sign flip. Sized 8-12h + conditional +Solve note.

## Deliverables
- docs/planning/EPIC_4/SPRINT_33/ROCKET_CASEC_FORCING_PLAN.md
- KNOWN_UNKNOWNS.md: Unknowns 5.1-5.3 verified
- PREP_PLAN.md: Task 7 -> COMPLETE
- CHANGELOG.md: Task 7 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint33-task7
gh pr create --base main --title "Complete Sprint 33 Prep Task 7: rocket PATH-Consultation Submission + Case-c Forcing Plan" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run `make typecheck && make lint && make format && make test` only if you touched Python)
- [x] ROCKET_CASEC_FORCING_PLAN.md has the Sprint-34 submission mechanism + the --force survey + the Case-c gate
- [x] The sign flip stays BANNED (not re-litigated)
- [x] Unknowns 5.1-5.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 7 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 8 Prompt: Refresh + Author Phase 0 Acceptance Gates for the Sprint-33 Tracks (PR20 + PR24 + PR27)

**Branch:** Create a new branch named `planning/sprint33-task8` from `main`

**Priority:** Critical (4–6 hours)

**Objective:** Author the Phase 0 acceptance gate for each Sprint-33 track (P1–P5) — the control-experiment-before-`src/` disposition that must pass before any high-blast-radius emit change — consolidating the per-track `/tmp` control specs from Tasks 3–7 into one `PHASE_0_ACCEPTANCE_GATES.md`.

**Unknowns Verified:** 1.1, 2.1, 3.1, 4.1, 5.1 (the per-track control/gate feasibility, contributes — the primary owners are Tasks 3/4/5/6/7)

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_33/PREP_PLAN.md` §Task 8
- `docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md` §Unknowns 1.1, 2.1, 3.1, 4.1, 5.1
- The five per-track design docs from Tasks 3–7: `MINE_CROSSTERM_DESIGN.md`, `SARF_EMIT_SUBSYSTEM_DESIGN.md`, `FAWLEY_SECOND_INDEX_DESIGN.md`, `CAMCGE_WALRAS_DESIGN.md`, `ROCKET_CASEC_FORCING_PLAN.md` (must be merged first — Task 8 depends on Tasks 3, 4, 5, 6, 7)
- `docs/planning/EPIC_4/SPRINT_32/PHASE_0_ACCEPTANCE_GATES.md` (the gate template)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 33" (the per-priority Phase-0 gate lines)

**Tasks to Complete:**

1. Consolidate the per-track `/tmp` control specs from Tasks 3 (mine), 4 (sarf), 5 (fawley), 6 (camcge), 7 (rocket/Case-c) into one gate document.
2. Author each gate: the exact `/tmp` control + the pass criterion (P1 warm residual → 0 at bound-active rows then MS-1; P2 O(active) translate budget + grep-clean + byte-stable golden; P3 `max|stat_bq| → 0` + MS-1 at 2899.25; P4 MS-1 at omega 191.7346; P5 Case-c residual clean before forcing), the `modelstat` assertion, and the PROCEED/REPLAN decision.
3. Encode the standing BANs (mine `x.up=inf`; Case-c sign flip) as explicit gate conditions.
4. Encode the emit-touching CI gates (the golden-staleness check PR26, the presolve-divergence detector, the `--resolve-changed` checkpoint re-solve) for every `src/`-touching PR.
5. Write `docs/planning/EPIC_4/SPRINT_33/PHASE_0_ACCEPTANCE_GATES.md`.

**Deliverables (from PREP_PLAN.md §Task 8):**

- `docs/planning/EPIC_4/SPRINT_33/PHASE_0_ACCEPTANCE_GATES.md` with one hand-derived gate per track (P1–P5)
- The `modelstat` assertion + the PROCEED/REPLAN criterion per gate
- The standing BANs (mine `x.up=inf`; Case-c sign flip) as explicit conditions
- The emit-touching CI gate references (golden-staleness, presolve-divergence, `--resolve-changed`)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 2.1, 3.1, 4.1, 5.1

**Known Unknowns Updates:** For Unknowns 1.1, 2.1, 3.1, 4.1, 5.1, add to the (Task-3/4/5/6/7-owned) verification blocks a **Task-8 gate-feasibility contribution** note: **Status** (✅ VERIFIED — the `/tmp` control is authored + feasible), **Verified by** Task 8 (gate), **Date**, **Findings** (the gate is executable + gives a clean PROCEED/REPLAN), **Evidence** (the gate doc), **Decision** (the gate is the Phase-0 disposition). Do not overwrite the primary owner's block; append the gate contribution.

**PREP_PLAN.md Updates:** In §Task 8: `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria (including "Unknowns 1.1, 2.1, 3.1, 4.1, 5.1 verified").

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 33 Prep`, prepend:
```markdown
- **Prep Task 8 COMPLETE (YYYY-MM-DD):** Phase 0 acceptance gates for the Sprint-33 tracks (P1–P5). Consolidated the per-track `/tmp` control specs from Tasks 3–7 into one `PHASE_0_ACCEPTANCE_GATES.md` — one hand-derived gate per track with the exact control, the pass criterion, the `modelstat` assertion, and the PROCEED/REPLAN decision; encoded the standing BANs (mine `x.up=inf`; Case-c sign flip) + the emit-touching CI gates (golden-staleness PR26, presolve-divergence, `--resolve-changed`). Verified Unknowns 1.1, 2.1, 3.1, 4.1, 5.1 (gate feasibility). Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected, so the quality gate is not required (docs-only changes skip it, per the project convention). If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 33 Prep Task 8: Phase 0 Acceptance Gates

Consolidated the per-track /tmp control specs from Tasks 3-7 into one
PHASE_0_ACCEPTANCE_GATES.md -- one hand-derived gate per track (P1-P5) with the exact
control, the pass criterion, the modelstat assertion, and the PROCEED/REPLAN decision;
encoded the standing BANs (mine x.up=inf; Case-c sign flip) + the emit-touching CI gates
(golden-staleness PR26, presolve-divergence, --resolve-changed).

## Deliverables
- docs/planning/EPIC_4/SPRINT_33/PHASE_0_ACCEPTANCE_GATES.md
- KNOWN_UNKNOWNS.md: Unknowns 1.1, 2.1, 3.1, 4.1, 5.1 verified (gate feasibility)
- PREP_PLAN.md: Task 8 -> COMPLETE
- CHANGELOG.md: Task 8 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint33-task8
gh pr create --base main --title "Complete Sprint 33 Prep Task 8: Phase 0 Acceptance Gates" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run `make typecheck && make lint && make format && make test` only if you touched Python)
- [x] PHASE_0_ACCEPTANCE_GATES.md has one gate per track P1-P5 with modelstat + PROCEED/REPLAN
- [x] The mine x.up=inf and Case-c sign-flip BANs are encoded; the emit-touching CI gates are referenced
- [x] Unknowns 1.1, 2.1, 3.1, 4.1, 5.1 verified in KNOWN_UNKNOWNS.md
- [x] Task 8 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 9 Prompt: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (PR16)

**Branch:** Create a new branch named `planning/sprint33-task9` from `main`

**Priority:** High (3–5 hours)

**Objective:** Apply the PR16 hypothesis-validation methodology to the three deepest from-scratch tracks — P1 (deeper cross-term coupling), P2 (timeout re-trigger), P3 (second-index gate-leak) — pinning explicit REPLAN exits, the freed-budget reallocation, and the honest projection of which KPI buckets can actually move.

**Unknowns Verified:** 1.2, 2.3, 3.3

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_33/PREP_PLAN.md` §Task 9
- `docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md` §Unknowns 1.2, 2.3, 3.3
- The Tasks 3/4/5 design docs + the Task 8 `PHASE_0_ACCEPTANCE_GATES.md` (must be merged first — Task 9 depends on Tasks 3, 4, 5, 8)
- `docs/planning/EPIC_4/SPRINT_32/REPLAN_RISK_ASSESSMENT.md` (the assessment template) + `docs/planning/EPIC_4/SPRINT_32/SPRINT_RETROSPECTIVE.md` §3 (the modal flat-KPI lesson)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 33" Risk Level (the P1/P2/P3 from-scratch risks + the REPLAN exits)

**Tasks to Complete:**

1. For each of P1/P2/P3, assess the REPLAN probability — the control/harness evidence that would refute the banked design (P1 a deeper coupling; P2 the parametric emit re-triggering the timeout; P3 the second-index gate leaking again) and how early the Day-5 checkpoint surfaces it.
2. Assess P4 (Epic-5 deferral) and P5 (conditional +Solve) dispositions.
3. Pin the REPLAN exits + the freed-budget reallocation (→ P6 failure-cohort re-triage + P7 property fixtures).
4. Author the honest KPI projection — firm movers (Solve +1 via any one of P1/P3/P4; Translate +1 via P2; genuine floor +1 via P1/P3 cold-match), the stretch (Solve ≥ 110), and the modal flat-KPI outcome.
5. Recommend the front-load ordering (deep tracks P1, P2 front-loaded so REPLANs surface by Day 5).
6. Write `docs/planning/EPIC_4/SPRINT_33/REPLAN_RISK_ASSESSMENT.md`.

**Deliverables (from PREP_PLAN.md §Task 9):**

- `docs/planning/EPIC_4/SPRINT_33/REPLAN_RISK_ASSESSMENT.md` with a per-track REPLAN-probability + refutation-evidence assessment (P1/P2/P3)
- The pinned REPLAN exits + freed-budget reallocation (→ P6/P7)
- The honest KPI projection (firm movers, stretch, modal flat-KPI outcome)
- The front-load ordering recommendation
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.2, 2.3, 3.3

**Known Unknowns Updates:** For Unknowns 1.2, 2.3, 3.3, replace the stub with **Status** (✅ VERIFIED / ❌ WRONG), **Verified by** Task 9, **Date**, **Findings** (the REPLAN probability + the refuting evidence per track), **Evidence** (the design docs + the gates), **Decision** (the REPLAN exit + the front-load ordering + the honest KPI projection).

**PREP_PLAN.md Updates:** In §Task 9: `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria (including "Unknowns 1.2, 2.3, 3.3 verified").

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 33 Prep`, prepend:
```markdown
- **Prep Task 9 COMPLETE (YYYY-MM-DD):** REPLAN-prone track risk assessment (PR16). Assessed the REPLAN probability + the refuting control/harness evidence for the three from-scratch tracks (P1 deeper cross-term coupling, P2 timeout re-trigger, P3 second-index gate-leak) + the P4/P5 dispositions; pinned the REPLAN exits + the freed-budget reallocation (→ P6/P7); authored the honest KPI projection (firm movers, stretch ≥ 110, modal flat-KPI) + the deep-track front-load ordering (REPLANs surface by Day 5). Verified Unknowns 1.2, 2.3, 3.3. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected, so the quality gate is not required (docs-only changes skip it, per the project convention). If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 33 Prep Task 9: REPLAN-Prone Track Risk Assessment

Assessed the REPLAN probability + the refuting control/harness evidence for the three
from-scratch tracks (P1 deeper cross-term coupling, P2 timeout re-trigger, P3 second-index
gate-leak) + the P4/P5 dispositions; pinned the REPLAN exits + the freed-budget
reallocation (-> P6/P7); authored the honest KPI projection (firm movers, stretch >=110,
modal flat-KPI) + the deep-track front-load ordering.

## Deliverables
- docs/planning/EPIC_4/SPRINT_33/REPLAN_RISK_ASSESSMENT.md
- KNOWN_UNKNOWNS.md: Unknowns 1.2, 2.3, 3.3 verified
- PREP_PLAN.md: Task 9 -> COMPLETE
- CHANGELOG.md: Task 9 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint33-task9
gh pr create --base main --title "Complete Sprint 33 Prep Task 9: REPLAN-Prone Track Risk Assessment" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run `make typecheck && make lint && make format && make test` only if you touched Python)
- [x] REPLAN_RISK_ASSESSMENT.md has the per-track REPLAN probability + exits + the honest KPI projection + the front-load ordering
- [x] Unknowns 1.2, 2.3, 3.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 9 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 10 Prompt: Reusable-Tooling Readiness Audit + Backlog Fix-Surface Analysis (Priorities 6 + 7)

**Branch:** Create a new branch named `planning/sprint33-task10` from `main`

**Priority:** Medium (3–4 hours)

**Objective:** Confirm the Sprint-28–32 diagnostic tooling covers the new Sprint-33 emit classes, and analyze the P6 failure-cohort fix-surfaces (agreste/cesam/lnts + residual `path_syntax_error`) and the P7 infrastructure scope (shape12/shape13/fawley property fixtures, genuine-floor tracking, Epic-4-SUMMARY continuation).

**Unknowns Verified:** 6.1, 6.2, 6.3, 7.1, 7.3

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_33/PREP_PLAN.md` §Task 10
- `docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md` §Category 6 (6.1–6.3) + §Unknowns 7.1, 7.3
- The Task 8 `PHASE_0_ACCEPTANCE_GATES.md` (must be merged first — Task 10 depends on Tasks 1, 8)
- `docs/planning/EPIC_4/SPRINT_32/TOOLING_AND_BACKLOG_ANALYSIS.md` + `docs/planning/EPIC_4/SPRINT_32/P6_BACKLOG_RETRIAGE.md` + `docs/planning/EPIC_4/SPRINT_32/P7_INFRASTRUCTURE.md` (the templates + the agreste/cesam/lnts diagnoses)
- The reused tooling: `scripts/diagnostics/kkt_residual.py` (incl. `case_c_objdef`), the presolve-divergence detector, the golden-staleness gate, `scripts/gamslib/run_full_test.py --resolve-changed`, the `--force` scaffold; `tests/**/test_ad_crossterm_shapes.py` (shapes 1–11); `docs/planning/EPIC_4/SUMMARY.md` (row 33)

**Tasks to Complete:**

1. Audit the reused tooling — confirm the KKT-residual harness (Case-a/b/c + `case_c_objdef`), the presolve-divergence detector, the golden-staleness gate, the `--resolve-changed` checkpoint, and the `--force` scaffold cover the new Sprint-33 classes (the bound-active cross-term residual test, the sarf symbolic emit path, the second-index property fixture). Note any gap.
2. Analyze the P6 fix-surfaces — agreste (verify the double-`solve` scope BEFORE treating it as CASE_B), cesam/lnts (Case-c re-confirm), residual `path_syntax_error` members, the srpchase/sarf symbolic-emit follow-ons; each gated by a `--resolve-changed` GO.
3. Scope the P7 property fixtures — shape12 (head-offset bound-active), shape13 (sarf symbolic), fawley second-index — each fail-before/pass-after, landing *only once* P1/P2/P3 land; plus the genuine-floor recompute (anchor 74) + the Epic-4-`SUMMARY.md` row-33 continuation.
4. Write `docs/planning/EPIC_4/SPRINT_33/TOOLING_AND_BACKLOG_ANALYSIS.md`.

**Deliverables (from PREP_PLAN.md §Task 10):**

- `docs/planning/EPIC_4/SPRINT_33/TOOLING_AND_BACKLOG_ANALYSIS.md` with the tooling-readiness audit (reuse vs gap) + the P6 fix-surface + P7 fixture scope
- The agreste double-`solve` scope caveat + the cesam/lnts Case-c re-confirm plan
- The shape12/shape13/fawley property-fixture plan (fail-before/pass-after, gated on P1/P2/P3) + the genuine-floor recompute + Epic-4-SUMMARY continuation
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 6.1, 6.2, 6.3, 7.1, 7.3

**Known Unknowns Updates:** For Unknowns 6.1, 6.2, 6.3, 7.1, 7.3, replace the stub with **Status** (✅ VERIFIED / ❌ WRONG), **Verified by** Task 10, **Date**, **Findings** (the agreste scope + the cesam/lnts Case-c + the adjacent unlock + the property-fixture fail-before feasibility + the SUMMARY scope), **Evidence** (the harness re-runs + the `--resolve-changed` GOs), **Decision** (the P6 fix-surface set + the P7 fixture plan).

**PREP_PLAN.md Updates:** In §Task 10: `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria (including "Unknowns 6.1, 6.2, 6.3, 7.1, 7.3 verified").

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 33 Prep`, prepend:
```markdown
- **Prep Task 10 COMPLETE (YYYY-MM-DD):** reusable-tooling readiness audit + backlog fix-surface analysis (P6 + P7). Audited the Sprint-28–32 tooling against the new Sprint-33 emit classes (reuse confirmed; gaps noted); analyzed the P6 failure cohort (agreste double-`solve` scope caveat, cesam/lnts Case-c re-confirm, residual path_syntax_error, srpchase/sarf follow-ons — each `--resolve-changed`-gated); scoped the P7 property fixtures (shape12/shape13/fawley, fail-before/pass-after, gated on P1/P2/P3) + the genuine-floor recompute (anchor 74) + the Epic-4-SUMMARY row-33 continuation. Verified Unknowns 6.1, 6.2, 6.3, 7.1, 7.3. Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected, so the quality gate is not required (docs-only changes skip it, per the project convention). If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 33 Prep Task 10: Tooling Readiness + Backlog Fix-Surface Analysis

Audited the Sprint-28-32 tooling against the new Sprint-33 emit classes (reuse confirmed;
gaps noted); analyzed the P6 failure cohort (agreste double-solve scope caveat, cesam/lnts
Case-c re-confirm, residual path_syntax_error, srpchase/sarf follow-ons -- each
--resolve-changed-gated); scoped the P7 property fixtures (shape12/shape13/fawley,
fail-before/pass-after, gated on P1/P2/P3) + the genuine-floor recompute + the
Epic-4-SUMMARY row-33 continuation.

## Deliverables
- docs/planning/EPIC_4/SPRINT_33/TOOLING_AND_BACKLOG_ANALYSIS.md
- KNOWN_UNKNOWNS.md: Unknowns 6.1, 6.2, 6.3, 7.1, 7.3 verified
- PREP_PLAN.md: Task 10 -> COMPLETE
- CHANGELOG.md: Task 10 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint33-task10
gh pr create --base main --title "Complete Sprint 33 Prep Task 10: Tooling Readiness + Backlog Fix-Surface Analysis" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run `make typecheck && make lint && make format && make test` only if you touched Python)
- [x] TOOLING_AND_BACKLOG_ANALYSIS.md has the tooling audit + the P6 fix-surfaces + the P7 fixture scope
- [x] The agreste double-solve caveat + the cesam/lnts Case-c re-confirm are recorded
- [x] Unknowns 6.1, 6.2, 6.3, 7.1, 7.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 10 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 11 Prompt: Plan Sprint 33 Detailed Schedule

**Branch:** Create a new branch named `planning/sprint33-task11` from `main`

**Priority:** Critical (3–4 hours)

**Objective:** Produce the detailed 14-day Sprint 33 schedule (Day 0 setup + Days 1–13 execution) with day-by-day prompts, front-loading the deep tracks (P1, P2) so REPLANs surface by the Day-5 checkpoint, at ≤ 12 hours/day within the 168-hour budget.

**Unknowns Verified:** None directly — Task 11 **integrates** all verified unknowns (Categories 1–7) into the day-by-day schedule; confirm every Critical/High unknown has a resolved verification result before finalizing the schedule (dependency on Tasks 2–10 being COMPLETE).

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_33/PREP_PLAN.md` §Task 11 (+ the full Prep Task Overview + critical paths)
- `docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md` (all 27 unknowns should be resolved by Tasks 2–10)
- All Tasks 2–10 outputs (must be merged first — Task 11 depends on Tasks 1–10): `BASELINE_METRICS.md`, the five design docs, `PHASE_0_ACCEPTANCE_GATES.md`, `REPLAN_RISK_ASSESSMENT.md`, `TOOLING_AND_BACKLOG_ANALYSIS.md`
- `docs/planning/EPIC_4/SPRINT_32/PLAN.md` + `SPRINT_32/prompts/PLAN_PROMPTS.md` (the schedule + day-prompt format)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 33" (the 86–126h Estimated Effort + the ~11h heaviest-day budget)

**Tasks to Complete:**

1. Lay out Day 0 — baseline confirmation (Task 2) + the four harness/control re-confirms (mine, sarf, fawley, camcge) + the GO/NO-GO for Day 1.
2. Front-load the deep tracks — P1 (mine, ~18–24h) + P2 (sarf, ~20–28h) across Days 1–7 so their REPLANs surface by the Day-5 checkpoint; P3 (fawley) + P4 (camcge) mid-sprint; P5 (rocket/Case-c) + P6 (failure-cohort) + P7 (infrastructure) in the back half.
3. Place the checkpoints — Day 5 (deep-track PROCEED/REPLAN + freed-budget reallocation) + Day 10; final retest Day 13 (≥ 3 `PYTHONHASHSEED`).
4. Write the day-by-day prompts — one per day, pasteable verbatim, each referencing its Phase-0 gate + design doc + REPLAN exit.
5. Verify the budget — ≤ 12h/day, ≤ 168h total, heaviest day ~11h; confirm the per-priority sizings sum to 86–126h.
6. Write `docs/planning/EPIC_4/SPRINT_33/PLAN.md` + `docs/planning/EPIC_4/SPRINT_33/prompts/PLAN_PROMPTS.md`.

**Deliverables (from PREP_PLAN.md §Task 11):**

- `docs/planning/EPIC_4/SPRINT_33/PLAN.md` — the 14-day schedule (Day 0 + Days 1–13) with the deep-track front-load, checkpoints, and budget verification
- `docs/planning/EPIC_4/SPRINT_33/prompts/PLAN_PROMPTS.md` — one pasteable prompt per day, each referencing its Phase-0 gate + design doc + REPLAN exit
- The budget confirmation (≤ 12h/day, ≤ 168h total, 86–126h work-items)

**Known Unknowns Updates:** Task 11 verifies no unknown directly. Confirm all 27 unknowns show a resolved verification result (✅ VERIFIED / ❌ WRONG) from Tasks 2–10; if any Critical/High unknown is still `🔍 INCOMPLETE`, flag it in the schedule as a Day-0 blocker rather than silently proceeding.

**PREP_PLAN.md Updates:** In §Task 11: `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 33 Prep`, prepend:
```markdown
- **Prep Task 11 COMPLETE (YYYY-MM-DD):** Sprint 33 detailed schedule. Authored `PLAN.md` (14-day schedule, Day 0 + Days 1–13) with the deep-track (P1, P2) front-load so REPLANs surface by the Day-5 checkpoint, the Day-5/Day-10 checkpoints + the Day-13 final retest (≥ 3 `PYTHONHASHSEED`), and the budget verification (≤ 12h/day, ≤ 168h, 86–126h work-items) + `prompts/PLAN_PROMPTS.md` (one pasteable prompt per day, each referencing its Phase-0 gate + design doc + REPLAN exit). Integrates all 27 verified unknowns. Sprint 33 prep COMPLETE (Tasks 1–11). Docs-only (no `src/`).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected, so the quality gate is not required (docs-only changes skip it, per the project convention). If you did touch Python, run it and do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 33 Prep Task 11: Plan Sprint 33 Detailed Schedule

Authored PLAN.md (14-day schedule, Day 0 + Days 1-13) with the deep-track (P1, P2)
front-load so REPLANs surface by the Day-5 checkpoint, the Day-5/Day-10 checkpoints +
the Day-13 final retest (>=3 PYTHONHASHSEED), and the budget verification (<=12h/day,
<=168h, 86-126h work-items) + prompts/PLAN_PROMPTS.md (one pasteable prompt per day).
Integrates all 27 verified unknowns. Sprint 33 prep COMPLETE (Tasks 1-11).

## Deliverables
- docs/planning/EPIC_4/SPRINT_33/PLAN.md
- docs/planning/EPIC_4/SPRINT_33/prompts/PLAN_PROMPTS.md
- PREP_PLAN.md: Task 11 -> COMPLETE
- CHANGELOG.md: Task 11 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint33-task11
gh pr create --base main --title "Complete Sprint 33 Prep Task 11: Plan Sprint 33 Detailed Schedule" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Docs-only change — quality gate not required (run `make typecheck && make lint && make format && make test` only if you touched Python)
- [x] PLAN.md has Day 0 + Days 1-13, the deep-track front-load, the Day-5/10 checkpoints, and the budget verification
- [x] prompts/PLAN_PROMPTS.md has one pasteable prompt per day (Day 0-13)
- [x] All 27 unknowns show a resolved verification result from Tasks 2-10
- [x] Task 11 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

**Document Created:** 2026-07-15
**Owner:** Sprint 33 Planning Team
**Covers:** Prep Tasks 2–11 (Task 1 is ✅ COMPLETE — see `docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md`)

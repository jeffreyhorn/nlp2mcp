# Sprint 30 Prep Task Execution Prompts

Self-contained prompts for Sprint 30 Prep Tasks 2–10. Each prompt can be copy-pasted into a new conversation to execute one prep task end-to-end, including the Known Unknowns updates, PREP_PLAN.md / CHANGELOG.md updates, quality gate, commit, and PR.

**Usage:**

1. Pick a task prompt below.
2. Paste it into a new conversation.
3. The agent creates the branch (`planning/sprint30-task<N>`), does the work, runs the quality gate, commits, pushes, and opens a PR.
4. Wait for reviewer comments on the PR.

Task 1 (Create Sprint 30 Known Unknowns List) is already ✅ COMPLETE — no prompt needed.

Tasks 2–10 are dispatchable in the following order per the dependency graph in `docs/planning/EPIC_4/SPRINT_30/PREP_PLAN.md` (Task 1 is done, so the tasks that depend only on it — or on nothing — are immediately dispatchable):

- **Immediately dispatchable:** Task 2 (no dependencies), Tasks 4 + 7 + 8 (need only the completed Task 1)
- **After Task 2:** Task 3 (the head-offset design reuses the Day-0 baseline / robert bucket)
- **After Task 3:** Task 5 (the Phase-0 gate refresh consumes the head-offset design)
- **After Task 8:** Task 9 (the backlog fix-surface analysis reuses the tooling audit)
- **After Tasks 3 + 4 + 5:** Task 6 (the REPLAN assessment consumes the head-offset design, the forcing survey, and the gates)
- **After all (final integration):** Task 10

**Critical path:** Task 1 → Task 3 → Task 5 → Task 6 → Task 10.

**Cross-cutting conventions for every prompt below:**

- Branch from `main`; PR targets `main`.
- User preferences (enforce in every commit/PR): **NO `Co-Authored-By` lines** in commit messages; **NO "Generated with Claude Code"** in PR descriptions.
- Replace `YYYY-MM-DD` with the actual date at execution time.
- These are **docs/design/analysis-only** prep tasks — no Python source changes are expected (the fixes/scripts they design are *built in-sprint*, not in prep; the harness/detector/gate + the `--resolve-changed` mode already exist on `main`). Run the full quality gate before committing regardless; if you did touch Python, it must pass.
- **PR24 discipline:** every banked Sprint-29 diagnosis is a Day-0-trace *hypothesis*, never fact (Sprint 29 proved the hhfair `$141` attribution wrong — the real blocker was `$184`). Record the symptom + reproducer; frame the fix surface as a hypothesis to re-trace.
- Every Known-Unknowns update uses the verification block: **Status** (✅ VERIFIED / ❌ WRONG), **Verified by**, **Date**, **Findings**, **Evidence**, **Decision**.

---

## Task 2 Prompt: Sprint 29 → Sprint 30 Day-0 Baseline + Genuine-Floor Re-Baseline (PR15 + PR17 + PR25)

**Branch:** Create a new branch named `planning/sprint30-task2` from `main`

**Priority:** Critical (3–4 hours)

**Objective:** Establish the Sprint 30 Day-0 baseline as the Sprint 29 final state, with per-model bucket provenance for the Sprint-30 target models and the genuine-vs-methodology Match split carried forward, so Sprint 30's targets land on genuine transitions. This is lighter than the Sprint-29 baseline task because the **re-baseline tooling and discipline already exist** (Sprint 29 Priority 8 built `--resolve-changed` + the PR25 re-baseline step) — this task *applies* them to the Day-0 DB, it does not build them.

**Unknowns Verified:** 8.2 (and contributes the per-target Day-0 bucket to 1.1 / 2.1 / 3.1 / 6.1)

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_30/PREP_PLAN.md` §Task 2
- `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md` §Unknown 8.2 (Day-0 baseline + genuine floor)
- `docs/planning/EPIC_4/SPRINT_29/BASELINE_METRICS.md` (the bucket-provenance + genuine-vs-methodology template) + `docs/planning/EPIC_4/SPRINT_29/SPRINT_LOG.md` §"Day 13" (the final PR25 tally: genuine floor 69; the Sprint-30-carryforward buckets)
- `data/gamslib/gamslib_status.json` (the Sprint 29 final retest DB: Solve 107 / Match 92 / model_infeasible 7 / Translate 135) + `scripts/gamslib/run_full_test.py` `_cold_objective_mismatches_nlp` (the methodology source)

**Tasks to Complete:**

1. Assert Day-0 = Sprint 29 final: `git diff <S29-close-SHA>..HEAD -- src/ scripts/` empty (only planning docs landed) → reuse the committed DB, no fresh ~4h retest. (`<S29-close-SHA>` = the "SPRINT 29 CLOSED" merge.)
2. Recompute the canonical bucket tally from the committed DB (`get_candidate_models`, canonical 142): Solve 107 / Match 92 / model_infeasible 7 / Translate 135.
3. Carry the genuine-vs-methodology split forward — genuine floor 69; document which Sprint-30 tracks convert methodology/warm matches into genuine cold matches (robert P1, hhfair P3, polygon/himmel16 P5, Class-B CGE P7) → the "genuine floor → ≥ 72" conversion map.
4. Pin the per-Sprint-30-target Day-0 bucket + projected delta (mine, rocket, hhfair, robert, sarf, polygon, himmel16, camcge, the Class-B CGE cluster), each labeled genuine bucket-to-success vs already-banked (mirror `SPRINT_29/BASELINE_METRICS.md §3`).

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_30/BASELINE_METRICS.md` — Day-0 = Sprint 29 final; canonical bucket tally; genuine-floor-69 carry-forward; per-Sprint-30-target bucket provenance with PR25 projection labels
- Confirmation that no fresh retest is needed (no `src/` drift since the S29 close)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknown 8.2 (Day-0 baseline + genuine floor)
- CHANGELOG.md updated with the Task 2 completion entry

**Known Unknowns Updates:** For Unknown 8.2 in `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md`, set the "Verification Results" subsection: Status ✅ VERIFIED (or ❌ WRONG + correction), Verified by Task 2, Date, Findings (the Day-0-baseline confirmation + the genuine-floor-69 carry-forward), Evidence (DB recompute + git diff), Decision (reuse the committed DB / any fresh-retest trigger). Also record the Day-0-bucket aspect of 1.1/2.1/3.1/6.1 (their fix-surface aspect is verified by Tasks 3/4/5).

**PREP_PLAN.md Updates:** In §Task 2: `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`; add `**Completed:** YYYY-MM-DD`; fill "Changes" (what was measured/authored) + "Result" (the Day-0 baseline + genuine floor); check off all Acceptance Criteria (`- [ ]` → `- [x]`).

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 30 Prep`, prepend:
```markdown
- **Prep Task 2 COMPLETE (YYYY-MM-DD):** Sprint 30 Day-0 baseline = Sprint 29 final (Solve 107 / Match 92 / model_infeasible 7 / Translate 135; no fresh retest — no `src/` drift). Genuine floor 69 carried forward with the genuine-floor → ≥ 72 conversion map (robert / hhfair / polygon-himmel16 / Class-B CGE). Per-Sprint-30-target Day-0 bucket + PR25 projection labels. Verified Unknown 8.2.
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 30 Prep Task 2: Day-0 Baseline + Genuine-Floor Re-Baseline

Day-0 = Sprint 29 final (Solve 107 / Match 92 / model_infeasible 7 / Translate 135;
no fresh retest — no src/ drift since the S29 close). Genuine floor 69 carried
forward with the genuine-floor -> >=72 conversion map. Per-Sprint-30-target Day-0
bucket + PR25 projection labels (genuine vs already-banked).

## Deliverables
- docs/planning/EPIC_4/SPRINT_30/BASELINE_METRICS.md
- KNOWN_UNKNOWNS.md: Unknown 8.2 verified
- PREP_PLAN.md: Task 2 -> COMPLETE
- CHANGELOG.md: Task 2 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint30-task2
gh pr create --title "Complete Sprint 30 Prep Task 2: Day-0 Baseline + Genuine-Floor Re-Baseline" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make lint && make format && make test` all PASS (docs-only)
- [x] BASELINE_METRICS.md records Day-0 = Sprint 29 final + per-target buckets + the genuine-floor-69 carry-forward
- [x] Day-0 = Sprint 29 final confirmed (git diff empty)
- [x] Unknown 8.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 2 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 3 Prompt: Head-Domain-Offset Emit-Architecture Design + robert Minimal Reproduction (Priority 1 Foundation)

**Branch:** Create a new branch named `planning/sprint30-task3` from `main`

**Priority:** Critical (5–7 hours) — **the critical-path anchor**

**Objective:** Turn the Sprint-29 Day-6/7 3-site head-offset trace into a concrete **index-map design** the Sprint-30 implementation follows, and establish **robert** as the minimal reproduction that de-risks the whole Priority-1 track. This is the hardest and highest-leverage prep task: Priority 1 is the deepest carryforward (a multi-site emit-architecture re-derivation), and its achievable scope is unknown until the index-map is designed and robert's generalization to mine is validated on paper.

**Unknowns Verified:** 1.1, 1.2, 1.3, 1.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_30/PREP_PLAN.md` §Task 3
- `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md` §Category 1 (Unknowns 1.1 robert→mine generalization, 1.2 3-site budget, 1.3 cold-LCP consistency, 1.4 robert `nu_sb` cross-term)
- `docs/issues/ISSUE_1443_*.md` (the Day-7 REPLAN + the Day-12 robert second-instance finding + the 3-site trace) + `docs/planning/EPIC_4/SPRINT_29/REPLAN_RISK_ASSESSMENT.md` Track A
- `src/emit/emit_gams.py` `_emit_nlp_presolve` (the dual transfer), `src/kkt/stationarity.py` `_try_build_param_offset_crossterm` (the landed `stat_x` cross-term), and the `comp_pr` emission path
- `scripts/diagnostics/kkt_residual.py` + `data/gamslib/raw/robert.gms` (the minimal reproduction) + `data/gamslib/raw/mine.gms` (the full case)

**Tasks to Complete:**

1. Hand-derive robert's head-offset cross-term + dual-transfer index map — for `sb(r,tt+1)`, derive the correct `x(p,tt)` cross-term `sum(r, a(r,p)*nu_sb(r,tt+1))` and the `--nlp-presolve` dual transfer reading `sb.m` at `tt+1`; confirm the eliminated-KKT residual → 0 at robert's NLP optimum via `kkt_residual.py`.
2. Design the three-site index-map coordination — which function at each of `comp_pr` / `_emit_nlp_presolve` / `stat_x` inverts the head offset onto the multiplier index; whether the constant-offset (robert) and parameter-offset (mine, `li(k)`/`lj(k)`) cases share one code path or branch; the gate that fires only on `has_head_domain_offset`.
3. Validate the robert → mine generalization on paper — show mine's `l+1 × li(k)/lj(k)` case is the constant-offset design with the parameter offset composed in (the `sum(k, lam_pr(k,l,i-li(k),j-lj(k)) - lam_pr(k,l-1,i,j))` shape). If it does NOT generalize (1.1 = WRONG), document mine as a separate multi-site fix and re-size P1.
4. Confirm the cold-LCP-consistency question — whether the head-offset fix alone resolves mine's `x → 4e10`, or a residual bound-complementarity coupling remains (feeds the Task-5 gate + the Task-6 REPLAN assessment).

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md` — robert's hand-derived head-offset cross-term + dual-transfer index map (with the `kkt_residual.py` residual → 0 confirmation); the three-site index-map coordination design; the robert → mine generalization verdict; the cold-LCP-consistency finding
- robert established as the P1 minimal reproduction; mine as the full multi-site case
- The P1 budget sized (one shared fix vs robert-then-mine) feeding Task 5 + Task 10
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3, 1.4
- CHANGELOG.md updated with the Task 3 completion entry

**Known Unknowns Updates:** For Unknowns 1.1, 1.2, 1.3, 1.4 in `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md`, set each "Verification Results": Status (✅ VERIFIED / ❌ WRONG), Verified by Task 3, Date, Findings (the robert derivation + residual, the 3-site design, the generalization verdict, the cold-LCP finding), Evidence (`kkt_residual.py` output on robert + mine; the emit-site trace), Decision (P1 = one-fix-two-models vs robert-then-mine split; the budget size fed to Tasks 5 + 10).

**PREP_PLAN.md Updates:** In §Task 3: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 30 Prep`, prepend:
```markdown
- **Prep Task 3 COMPLETE (YYYY-MM-DD):** head-domain-offset emit-architecture design + robert minimal reproduction. `HEAD_OFFSET_ARCHITECTURE_DESIGN.md` — robert's `sum(r, a(r,p)*nu_sb(r,tt+1))` cross-term + dual-transfer index map (harness residual → 0 at the NLP optimum); the 3-site (`comp_pr`/`_emit_nlp_presolve`/`stat_x`) coordination design; the robert → mine generalization verdict (P1 = [one-fix-two-models | robert-then-mine split]); the cold-LCP-consistency finding. Verified Unknowns 1.1, 1.2, 1.3, 1.4.
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs/design-only — no `src/` change (the fix is *built in-sprint*; any prototype probe is env-guarded + reverted, zero diff). Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 30 Prep Task 3: Head-Offset Architecture Design + robert Reproduction

HEAD_OFFSET_ARCHITECTURE_DESIGN.md: robert's head-offset cross-term
sum(r, a(r,p)*nu_sb(r,tt+1)) + dual-transfer index map (harness residual -> 0 at
the NLP optimum); the 3-site (comp_pr / _emit_nlp_presolve / stat_x) coordination
design; the robert -> mine generalization verdict; the cold-LCP-consistency finding.
P1 sized as [one-fix-two-models | robert-then-mine split].

## Deliverables
- docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 1.1, 1.2, 1.3, 1.4 verified
- PREP_PLAN.md: Task 3 -> COMPLETE
- CHANGELOG.md: Task 3 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint30-task3
gh pr create --title "Complete Sprint 30 Prep Task 3: Head-Offset Architecture Design + robert Reproduction" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make lint && make format && make test` all PASS (docs/design-only)
- [x] robert's cross-term + dual-transfer hand-derived; `kkt_residual.py` residual → 0 at the NLP optimum
- [x] The 3 emit sites + shared-vs-branched code path designed
- [x] The robert → mine generalization verdict recorded (Unknown 1.1)
- [x] The cold-LCP-consistency question resolved (Unknown 1.3)
- [x] Unknowns 1.1, 1.2, 1.3, 1.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 3 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 4 Prompt: Non-Convex Forcing Strategy Survey (rocket #1462 + Cold-Convex Case-c Residue) (Priority 2 Foundation)

**Branch:** Create a new branch named `planning/sprint30-task4` from `main`

**Priority:** High (4–6 hours)

**Objective:** Survey the candidate **solution-forcing** strategies for rocket #1462's intrinsic non-convergence — trust-region damping, homotopy/continuation, and multi-start from perturbed warm-starts — and determine which is expressible inside nlp2mcp's emitted GAMS vs which needs a PATH solver option, so Priority 2 implements a chosen lever and Priority 8's forcing-harness scaffold has a tested entry point. This is a research-before-design task: it precedes the P2 implementation and feeds the P8 scaffold + the Task-6 REPLAN assessment.

**Unknowns Verified:** 2.1, 2.2, 2.3, 7.2

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_30/PREP_PLAN.md` §Task 4
- `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md` §Category 2 (Unknowns 2.1 forcing lever, 2.2 nlp2mcp/PATH boundary, 2.3 Case-c shared payoff) + Unknown 7.2 (Case-c residue disposition)
- `docs/issues/ISSUE_1462_rocket-fx-multiplier-warmstart-nonconvex.md` (the `_fx_` warm-start landed Day 1; the Day-2 intrinsic-non-convergence finding) + `docs/planning/EPIC_4/SPRINT_29/REPLAN_RISK_ASSESSMENT.md` Track B
- `docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md` (the Case-c residue) + `docs/research/convexity_detection.md`, `docs/research/CONVEXITY_VERIFICATION_DESIGN.md`
- PATH solver documentation (trust-region / merit-function / crash options) — for the PATH-option boundary

**Tasks to Complete:**

1. Enumerate the forcing levers (trust-region damping / homotopy-continuation / multi-start) — for each: the mechanism, whether it is expressible as emitted GAMS (a continuation parameter loop / bound-relaxation schedule / `.l` perturbation) or requires a PATH option, and the expected effect on rocket's MS-5.
2. Prototype-probe one lever on rocket (env-guarded, zero `src/` diff) — apply the most promising lever to rocket's presolve MCP; measure the MODEL STATUS progression toward MS 1/2 at 1.0128 (or "needs a PATH option").
3. Check the shared payoff on the cold-convex Case-c residue — does the chosen lever move any Case-c cohort model toward a solve? Enumerate the post-forcing Case-c residue (feeds 7.2).
4. Define the nlp2mcp/PATH boundary — which levers stay in the Sprint-30 emit/scaffold vs which become the Sprint-31 PATH-consultation question.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md` — the forcing-lever enumeration (trust-region / homotopy / multi-start), the rocket prototype-probe result, the cold-convex Case-c shared-payoff check, and the nlp2mcp/PATH boundary
- The chosen P2 forcing lever + the P8 forcing-scaffold entry point
- The Sprint-31 PATH-consultation hand-off scope (the levers needing a PATH option)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.1, 2.2, 2.3, 7.2
- CHANGELOG.md updated with the Task 4 completion entry

**Known Unknowns Updates:** For Unknowns 2.1, 2.2, 2.3, 7.2 in `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md`, set each "Verification Results": Status, Verified by Task 4, Date, Findings (the lever survey + the rocket probe result + the Case-c residue), Evidence (`kkt_residual.py` / MODEL STATUS from the env-guarded probe), Decision (the chosen P2 lever + the nlp2mcp/PATH boundary + the Sprint-31 hand-off scope).

**PREP_PLAN.md Updates:** In §Task 4: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 30 Prep`, prepend:
```markdown
- **Prep Task 4 COMPLETE (YYYY-MM-DD):** non-convex forcing strategy survey. `NONCONVEX_FORCING_SURVEY.md` — enumerated trust-region / homotopy / multi-start levers with the nlp2mcp-emittable vs PATH-option boundary per lever; prototype-probed [chosen lever] on rocket (env-guarded, zero src/) → MODEL STATUS [result]; checked the cold-convex Case-c shared payoff. Chosen P2 lever = [X]; Sprint-31 PATH-consultation hand-off = [scope]. Verified Unknowns 2.1, 2.2, 2.3, 7.2.
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Research/design-only — any rocket probe is env-guarded + reverted (zero `src/` diff). Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 30 Prep Task 4: Non-Convex Forcing Strategy Survey

NONCONVEX_FORCING_SURVEY.md: enumerated trust-region / homotopy / multi-start
forcing levers with the nlp2mcp-emittable vs PATH-option boundary; prototype-probed
[chosen lever] on rocket (env-guarded, zero src/) -> MODEL STATUS [result]; checked
the cold-convex Case-c shared payoff. Chosen P2 lever + P8 scaffold entry point +
the Sprint-31 PATH-consultation hand-off scope.

## Deliverables
- docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md
- KNOWN_UNKNOWNS.md: Unknowns 2.1, 2.2, 2.3, 7.2 verified
- PREP_PLAN.md: Task 4 -> COMPLETE
- CHANGELOG.md: Task 4 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint30-task4
gh pr create --title "Complete Sprint 30 Prep Task 4: Non-Convex Forcing Strategy Survey" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make lint && make format && make test` all PASS (research/design-only)
- [x] The three forcing-lever families enumerated with the nlp2mcp/PATH boundary per lever
- [x] One lever prototype-probed on rocket (env-guarded, zero src/); MODEL STATUS recorded
- [x] The cold-convex Case-c shared payoff checked
- [x] Unknowns 2.1, 2.2, 2.3, 7.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 4 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 5 Prompt: Refresh + Author Phase 0 Acceptance Gates for the Sprint-30 Tracks (PR20 + PR24 + PR27)

**Branch:** Create a new branch named `planning/sprint30-task5` from `main`

**Priority:** Critical (4–6 hours)

**Objective:** Refresh the existing Phase 0 acceptance gates (authored in Sprint 29 Prep Task 4) with the Sprint-30 dispositions, and author the two new gates the Sprint-30 tracks need. Most Sprint-30 target issue docs (`ISSUE_{1443,1462,1236,1385,1146,1143,1330}`) already carry a `## Phase 0: Acceptance Gate` from Sprint 29 — this task updates them to reflect what Sprint 29 *learned* (mine+robert head-offset, rocket forcing, hhfair `$184`, the offset-alias Day-5 revert), and adds a **robert** gate (the P1 minimal reproduction) and a **Class-B CGE `stat_pz`** gate (the P7 general-emit backlog).

**Unknowns Verified:** 1.2, 1.3, 2.2, 3.1, 3.2, 4.1, 5.2, 6.1, 7.1, 7.3

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_30/PREP_PLAN.md` §Task 5
- `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md` §Unknowns 1.2, 1.3, 2.2, 3.1, 3.2, 4.1, 5.2, 6.1, 7.1, 7.3
- `docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md` (Task 3 — the mine+robert gate content) **← requires Task 3 done**
- `CONTRIBUTING.md` §"Phase 0 Acceptance Gate" (the PR20 template + PR24 traced-fix-surface + PR27 harness verification)
- The existing Sprint-29 gates in `docs/issues/ISSUE_{1443,1462,1236,1385,1146,1143,1330}_*.md` + `docs/planning/EPIC_4/SPRINT_29/BACKLOG_FIX_SURFACE_ANALYSIS.md` (offset-alias + Class-B fix-surface hypotheses)

**Tasks to Complete:**

1. Refresh the seven existing gates to the Sprint-30 disposition: #1443 mine (PROCEED via head-offset architecture per Task 3; robert minimal reproduction); #1462 rocket (PROCEED to a forcing lever per Task 4; the Case-c → Sprint-31 PATH exit); #1236 hhfair (the `$184` widened-VARIABLE blocker, **not** `$141`; CES verdict after the compile clears); #1385 (the banked cross-terms + sarf reference target); #1146/#1143 (the Day-5 revert coupling + the coordinated fix); #1330 camcge (the Walras transformation + the detection-heuristic gate per Task 7).
2. Author a robert gate (in `ISSUE_1443` shared with mine, or a new local `docs/issues/ISSUE_robert_*.md`): the hand-derived `sum(r, a(r,p)*nu_sb(r,tt+1))` cross-term, the expected emit, the `kkt_residual.py` PROCEED verdict, the traced `file:line` (Day-0).
3. Author a Class-B CGE `stat_pz` gate (the P7 general-emit backlog): the hand-derived `stat_pz` coefficient the harness localizes (confirmed NOT Walras), the expected emit, the per-model PROCEED condition.
4. Verify every gate cites `kkt_residual.py` as its verification method and has an explicit Sprint-31 REPLAN exit where applicable (P1 architectural, P2 non-convex, P5 #1111/#1112 core, P6 non-degenerate).

**Deliverables:**

- Refreshed `## Phase 0: Acceptance Gate` in `docs/issues/ISSUE_{1443,1462,1236,1385,1146,1143,1330}_*.md` to the Sprint-30 dispositions
- A robert Phase-0 gate (in ISSUE_1443 or a new local doc)
- A Class-B CGE `stat_pz` Phase-0 gate
- Every gate cites `kkt_residual.py`; REPLAN-prone gates have an explicit Sprint-31 exit
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.2, 1.3, 2.2, 3.1, 3.2, 4.1, 5.2, 6.1, 7.1, 7.3
- CHANGELOG.md updated with the Task 5 completion entry

**Known Unknowns Updates:** For Unknowns 1.2, 1.3, 2.2, 3.1, 3.2, 4.1, 5.2, 6.1, 7.1, 7.3 in `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md`, set each "Verification Results": Status, Verified by Task 5, Date, Findings (the gate's hand-derived shape + traced fix-surface), Evidence (the ISSUE-doc gate section + the `kkt_residual.py` verification method), Decision (PROCEED / Sprint-31 REPLAN exit per track).

**PREP_PLAN.md Updates:** In §Task 5: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 30 Prep`, prepend:
```markdown
- **Prep Task 5 COMPLETE (YYYY-MM-DD):** refreshed the seven Sprint-29 Phase-0 gates to the Sprint-30 dispositions (mine+robert head-offset, rocket forcing, hhfair `$184` widened-VARIABLE [corrected from `$141`], #1385 banked cross-terms, offset-alias Day-5 revert coupling, camcge Walras) + authored a robert gate (P1 minimal reproduction) and a Class-B CGE `stat_pz` gate (P7 general-emit, NOT Walras). Every gate frames its fix-surface as a Day-0 hypothesis (PR24) + cites `kkt_residual.py` (PR27); REPLAN-prone gates have a Sprint-31 exit. Verified Unknowns 1.2, 1.3, 2.2, 3.1, 3.2, 4.1, 5.2, 6.1, 7.1, 7.3.
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only (ISSUE-doc gate sections) — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 30 Prep Task 5: Refresh + Author Phase 0 Acceptance Gates

Refreshed the seven Sprint-29 gates (ISSUE_1443/1462/1236/1385/1146/1143/1330) to
the Sprint-30 dispositions (mine+robert, rocket-forcing, hhfair $184 [corrected from
$141], #1385-banked, offset-alias-coupled, camcge-Walras) + authored a robert gate
(P1 minimal reproduction) and a Class-B CGE stat_pz gate (P7 general-emit, NOT Walras).
Every gate frames its fix-surface as a Day-0 hypothesis (PR24) + cites kkt_residual.py
(PR27); REPLAN-prone gates have a Sprint-31 exit.

## Deliverables
- docs/issues/ISSUE_*.md: refreshed Phase-0 gates + robert + Class-B stat_pz
- KNOWN_UNKNOWNS.md: Unknowns 1.2, 1.3, 2.2, 3.1, 3.2, 4.1, 5.2, 6.1, 7.1, 7.3 verified
- PREP_PLAN.md: Task 5 -> COMPLETE
- CHANGELOG.md: Task 5 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint30-task5
gh pr create --title "Complete Sprint 30 Prep Task 5: Refresh + Author Phase 0 Acceptance Gates" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make lint && make format && make test` all PASS (docs-only)
- [x] The seven existing gates refreshed to the Sprint-30 dispositions
- [x] robert gate + Class-B `stat_pz` gate authored
- [x] hhfair gate corrected to the `$184` widened-VARIABLE blocker (not `$141`-only)
- [x] Every gate cites `kkt_residual.py`; REPLAN-prone gates have a Sprint-31 exit
- [x] Unknowns 1.2, 1.3, 2.2, 3.1, 3.2, 4.1, 5.2, 6.1, 7.1, 7.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 5 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 6 Prompt: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (#1443 multi-site, #1462 forcing, #1330 Epic-5; PR16)

**Branch:** Create a new branch named `planning/sprint30-task6` from `main`

**Priority:** High (3–5 hours)

**Objective:** Apply the PR16 hypothesis-validation methodology to the three Sprint-30 tracks most likely to prove deeper than budgeted — #1443 (the multi-site head-offset architecture: does the robert-minimal fix generalize to mine, or is mine a separate multi-site slip?), #1462 (non-convex forcing: does a lever move rocket, or is it a PATH-option Sprint-31 hand-off?), and #1330 camcge (the Epic-5 transformation: does the paper-verified drop-row + fix-numéraire reach MS 1 empirically, or does the detection heuristic prove unreliable?) — and pin an explicit PROCEED/REPLAN signal + Sprint-31 exit + budget reallocation for each.

**Unknowns Verified:** 1.1, 1.2, 2.1, 2.2, 6.1, 6.2

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_30/PREP_PLAN.md` §Task 6
- `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md` §Unknowns 1.1, 1.2 (head-offset), 2.1, 2.2 (rocket), 6.1, 6.2 (camcge)
- `docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md` (Task 3 — the robert → mine generalization verdict) **← requires Task 3**
- `docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md` (Task 4 — the rocket forcing-lever result + the PATH boundary) **← requires Task 4**
- The Sprint-30 Phase-0 gates (Task 5) **← requires Task 5**; `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` §5 (camcge open questions); `docs/planning/EPIC_4/SPRINT_29/REPLAN_RISK_ASSESSMENT.md` (the structural template)

**Tasks to Complete:**

1. For each of the three tracks: state the architectural hypothesis, the single-model validation experiment (the Task-3/4/7 result + any prototype-then-revert probe), the PROCEED signal, the REPLAN signal, and the Sprint-31 exit scope.
2. #1443: PROCEED if robert's fix generalizes to mine (Task 3 verdict) and the 3-site re-derivation fits ~14–20h; REPLAN mine (not robert) to a Sprint-31 head-offset-architecture workstream if it does not generalize or the cold-LCP coupling persists — robert (genuine-floor) still lands.
3. #1462: PROCEED if a Task-4 forcing lever moves rocket to MS 1/2; REPLAN to the Sprint-31 PATH consultation if the lever needs a PATH option — the forcing scaffold (P8) still lands.
4. #1330 camcge: PROCEED if the Walras transformation empirically reaches MS 1 at 191.7346 and the detection heuristic is reliable; REPLAN to a per-model-numéraire-declaration Epic-5 item if the heuristic false-flags or the numéraire selection proves per-model.
5. Budget-reallocation plan per REPLAN: mine slip → more Class-B CGE / offset-alias genuine-floor; rocket slip → the scaffold + hhfair; camcge slip → the Class-B general-emit fix.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md` with per-track hypothesis, validation experiment, PROCEED/REPLAN signals, Sprint-31 exit
- A budget-reallocation plan for each possible REPLAN
- The three REPLAN-prone unknowns resolved into scheduled decisions (feeds Task 10's slack allocation + fallback ordering)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 2.1, 2.2, 6.1, 6.2
- CHANGELOG.md updated with the Task 6 completion entry

**Known Unknowns Updates:** For Unknowns 1.1, 1.2, 2.1, 2.2, 6.1, 6.2 in `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md`, set/append each "Verification Results" with the REPLAN decision: Status, Verified by Task 6, Date, Findings (the PROCEED/REPLAN signal per track), Evidence (the Task-3/4/7 result), Decision (PROCEED vs Sprint-31 REPLAN + budget reallocation). (These unknowns may already be VERIFIED by Tasks 3/4/7 — Task 6 adds the risk/decision layer.)

**PREP_PLAN.md Updates:** In §Task 6: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 30 Prep`, prepend:
```markdown
- **Prep Task 6 COMPLETE (YYYY-MM-DD):** REPLAN-prone track risk assessment. `REPLAN_RISK_ASSESSMENT.md` — per-track PROCEED/REPLAN signals + Sprint-31 exits + budget reallocation for #1443 (mine multi-site: PROCEED if robert generalizes, else split), #1462 (rocket forcing: PROCEED if an in-GAMS lever moves it, else PATH-consultation hand-off), #1330 camcge (Epic-5: PROCEED if the Walras transform empirically reaches MS 1 + the detection heuristic is reliable, else per-model-declaration). Firm parts land regardless (robert / scaffold / Class-B fix). Verified Unknowns 1.1, 1.2, 2.1, 2.2, 6.1, 6.2.
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs/analysis-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 30 Prep Task 6: REPLAN-Prone Track Risk Assessment

REPLAN_RISK_ASSESSMENT.md: per-track hypothesis + single-model validation +
PROCEED/REPLAN signals + Sprint-31 exit + budget reallocation for #1443 (mine
multi-site), #1462 (rocket forcing), #1330 camcge (Epic-5). Firm parts land
regardless (robert / forcing scaffold / Class-B fix). Feeds the Task-10 schedule's
slack allocation and fallback ordering.

## Deliverables
- docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md
- KNOWN_UNKNOWNS.md: Unknowns 1.1, 1.2, 2.1, 2.2, 6.1, 6.2 verified
- PREP_PLAN.md: Task 6 -> COMPLETE
- CHANGELOG.md: Task 6 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint30-task6
gh pr create --title "Complete Sprint 30 Prep Task 6: REPLAN-Prone Track Risk Assessment" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make lint && make format && make test` all PASS (docs/analysis-only)
- [x] Risk assessment covers #1443 (multi-site), #1462 (forcing), #1330 (Epic-5)
- [x] Each track has PROCEED + REPLAN signals + a Sprint-31 exit + the firm part that lands
- [x] Budget-reallocation plan per REPLAN
- [x] Unknowns 1.1, 1.2, 2.1, 2.2, 6.1, 6.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 6 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 7 Prompt: camcge → Epic 5 Walras Transformation Design (Priority 6)

**Branch:** Create a new branch named `planning/sprint30-task7` from `main`

**Priority:** Medium (3–4 hours)

**Objective:** Turn the paper-verified Walras transformation in `EPIC_5/CGE_DEGENERACY_SCOPING.md` into an implementation design: the **degeneracy-detection heuristic** (how the preprocessing layer recognises a Walras-degenerate model without false-flagging a well-posed one), the **per-model numéraire + redundant-row selection** rule, and the **non-degenerate-model guard**, so the in-sprint Priority-6 implementation follows a design rather than re-deriving the open questions.

**Unknowns Verified:** 6.1, 6.2, 6.3

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_30/PREP_PLAN.md` §Task 7
- `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md` §Category 6 (Unknowns 6.1 empirical MS-1, 6.2 detection heuristic, 6.3 numéraire selection)
- `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` (the paper-verified transformation §3; the scope boundary §4; the open questions §5)
- `docs/issues/ISSUE_1330_*.md` (the camcge structural-singularity diagnosis; the MS-4-at-iteration-0 signature; the `equil`/`lmequil` linear dependence)
- The CGE cohort sources (`data/gamslib/raw/camcge.gms` + `irscge/lrgcge/moncge/stdcge` for the generality check) + `scripts/diagnostics/kkt_residual.py` + the PATH basis-singularity report

**Tasks to Complete:**

1. Design the degeneracy-detection heuristic — a rank check on the market-clearing block / the PATH basis-singularity report / a model-structure signature; specify the false-positive guard (a well-posed model must be left untouched) and how the layer decides to transform vs pass through.
2. Design the redundant-row + numéraire selection — the rule for which market-clearing row to drop + which price to fix (SAM-largest-sector / CPI aggregate / per-model declaration); verify it reproduces camcge's 191.7346 on paper.
3. Scope the empirical-confirmation experiment — the Day-0 GAMS run (drop-`lmequil` + fix-`cpi=1` → MS 1 at 191.7346) that Priority 6 runs first, and the cohort-generality check (is camcge the sole inherent case?).
4. Record the nlp2mcp/Epic-5 boundary — the transformation is CGE-domain preprocessing (Epic 5), invoked only for detected-degenerate models; the general-emit fixes (Class-B `stat_pz`) stay in nlp2mcp (P7).

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_30/CAMCGE_WALRAS_TRANSFORM_DESIGN.md` — the degeneracy-detection heuristic + false-positive guard; the redundant-row + numéraire-selection rule (reproducing 191.7346 on paper); the empirical-confirmation experiment scope; the cohort-generality check plan
- The three `CGE_DEGENERACY_SCOPING.md` §5 open questions resolved into a design
- The nlp2mcp/Epic-5 boundary (Class-B general-emit fixes stay in nlp2mcp)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 6.1, 6.2, 6.3
- CHANGELOG.md updated with the Task 7 completion entry

**Known Unknowns Updates:** For Unknowns 6.1, 6.2, 6.3 in `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md`, set each "Verification Results": Status, Verified by Task 7, Date, Findings (the detection heuristic + false-positive guard, the selection rule reproducing 191.7346, the empirical-experiment scope), Evidence (`CGE_DEGENERACY_SCOPING.md` §3/§5 + the cohort check), Decision (the design + the Epic-5 boundary; feeds the Task-6 REPLAN reliability judgment).

**PREP_PLAN.md Updates:** In §Task 7: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 30 Prep`, prepend:
```markdown
- **Prep Task 7 COMPLETE (YYYY-MM-DD):** camcge → Epic 5 Walras transformation design. `CAMCGE_WALRAS_TRANSFORM_DESIGN.md` — the degeneracy-detection heuristic + non-degenerate-model false-positive guard; the redundant-row + numéraire-selection rule (reproduces 191.7346 on paper); the empirical-confirmation experiment (drop-`lmequil` + fix-`cpi=1` → MS 1) scoped for P6 Day-0; the cohort-generality check (is camcge the sole inherent case?). The three `CGE_DEGENERACY_SCOPING.md` §5 open questions resolved into a design; Class-B general-emit stays in nlp2mcp. Verified Unknowns 6.1, 6.2, 6.3.
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs/design-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 30 Prep Task 7: camcge -> Epic 5 Walras Transformation Design

CAMCGE_WALRAS_TRANSFORM_DESIGN.md: the degeneracy-detection heuristic + non-degenerate-
model false-positive guard; the redundant-row + numeraire-selection rule (reproduces
191.7346 on paper); the empirical-confirmation experiment (drop-lmequil + fix-cpi=1 ->
MS 1) scoped for P6 Day-0; the cohort-generality check. Resolves the three
CGE_DEGENERACY_SCOPING.md section-5 open questions; Class-B general-emit stays in nlp2mcp.

## Deliverables
- docs/planning/EPIC_4/SPRINT_30/CAMCGE_WALRAS_TRANSFORM_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 6.1, 6.2, 6.3 verified
- PREP_PLAN.md: Task 7 -> COMPLETE
- CHANGELOG.md: Task 7 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint30-task7
gh pr create --title "Complete Sprint 30 Prep Task 7: camcge -> Epic 5 Walras Transformation Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make lint && make format && make test` all PASS (docs/design-only)
- [x] The detection heuristic designed with an explicit non-degenerate-model false-positive guard
- [x] The redundant-row + numéraire-selection rule reproduces 191.7346 on paper
- [x] The empirical-confirmation experiment (drop-`lmequil` + fix-`cpi=1` → MS 1) scoped for P6 Day-0
- [x] The cohort-generality check plan present; the nlp2mcp/Epic-5 boundary recorded
- [x] Unknowns 6.1, 6.2, 6.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 7 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 8 Prompt: Reusable-Tooling Readiness Audit for the Sprint-30 Model Classes

**Branch:** Create a new branch named `planning/sprint30-task8` from `main`

**Priority:** Medium (3–4 hours)

**Objective:** Audit the Sprint-29 diagnostic/CI tools — `kkt_residual.py`, `check_presolve_divergence.py`, `check_golden_staleness.py`, `changed_emit_artifacts.py`, and the `--resolve-changed` checkpoint re-solve — against the new Sprint-30 model classes (head-domain-offset multipliers `lam_pr`/`nu_sb`, the widened-VARIABLE presolve emit, the forcing-harness scaffold, the offset-alias-successor cross-term shape), and identify any *minimal* extension needed before Day 1 so the in-sprint work runs on tooling that already covers the cases.

**Unknowns Verified:** 1.4, 8.1, 8.3, 8.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_30/PREP_PLAN.md` §Task 8
- `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md` §Unknowns 1.4 (robert `nu_sb` harness dual-transfer), 8.1 (property-catalog extensibility), 8.3 (forcing scaffold), 8.4 (`--resolve-changed` reuse)
- `docs/planning/EPIC_4/SPRINT_29/TOOLING_READINESS_AUDIT.md` (the Sprint-29 audit template + the "gap list = none" verdict)
- `scripts/diagnostics/kkt_residual.py`, `scripts/diagnostics/check_presolve_divergence.py`, `scripts/sprint_audit/check_golden_staleness.py` + `scripts/sprint_audit/changed_emit_artifacts.py`, the `--resolve-changed` mode; `tests/integration/emit/test_ad_crossterm_shapes.py` + `tests/fixtures/crossterm_shapes/`; the golden-staleness + presolve-divergence allowlists

**Tasks to Complete:**

1. KKT-residual harness: run it on robert + mine (head-offset `lam_pr`/`nu_sb` multipliers) and confirm the dual-transfer self-check reports CONSISTENT; if it mis-transfers the head-offset multiplier, scope the minimal one-line index-mapping extension as a Day-0 task (feeds 1.4).
2. `--resolve-changed`: confirm it covers the widened-VARIABLE presolve regens (hhfair P3) and the head-offset goldens (mine/robert P1) — i.e., the changed-golden diff surfaces them as at-risk.
3. Property-test catalog: confirm `test_ad_crossterm_shapes.py` is extensible to the head-domain-offset + offset-alias-successor shapes (P8 adds these fixtures); no structural blocker.
4. Allowlists + detector: confirm the golden-staleness + divergence allowlists are current at Day 0; confirm the divergence detector soft-classifies the Class-B CGE + cold-convex residue (no false hard-fails). Produce a gap list (each Day-0 extension ≤ 1h) or "no extensions needed".

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_30/TOOLING_READINESS_AUDIT.md` — per-tool readiness verdict for the Sprint-30 classes (head-offset dual-transfer, widened-VARIABLE re-solve coverage, property-catalog extensibility, allowlist currency)
- A scoped gap list (Day-0 extensions ≤ 1h each) or "no extensions needed"
- Confirmation the `--resolve-changed` checkpoint covers the Sprint-30 changed-golden set
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.4, 8.1, 8.3, 8.4
- CHANGELOG.md updated with the Task 8 completion entry

**Known Unknowns Updates:** For Unknowns 1.4, 8.1, 8.3, 8.4 in `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md`, set each "Verification Results": Status, Verified by Task 8, Date, Findings (the harness dual-transfer verdict on robert/mine, the property-catalog extensibility, the allowlist currency), Evidence (`kkt_residual.py` output, the fixture list, `cat` of the allowlists), Decision (the gap list or "no extensions needed").

**PREP_PLAN.md Updates:** In §Task 8: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 30 Prep`, prepend:
```markdown
- **Prep Task 8 COMPLETE (YYYY-MM-DD):** reusable-tooling readiness audit. `TOOLING_READINESS_AUDIT.md` — validated the KKT-residual harness dual-transfer on robert + mine (head-offset `lam_pr`/`nu_sb` multipliers) [CONSISTENT | ≤1h extension]; confirmed `--resolve-changed` covers the widened-VARIABLE + head-offset goldens; confirmed `test_ad_crossterm_shapes.py` extensible to the head-offset + offset-alias-successor shapes; allowlists current + the divergence detector soft-classifies the Class-B/cold-convex residue. Gap list = [none needed | scoped Day-0 extensions]. Verified Unknowns 1.4, 8.1, 8.3, 8.4.
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Audit-only (read-only tool runs) — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 30 Prep Task 8: Reusable-Tooling Readiness Audit

TOOLING_READINESS_AUDIT.md: validated the KKT-residual harness dual-transfer on
robert + mine (head-offset multipliers); confirmed --resolve-changed covers the
widened-VARIABLE + head-offset goldens; confirmed the AD property-test catalog is
extensible to the head-offset + offset-alias-successor shapes; allowlists current +
divergence detector soft-classifies the Class-B/cold-convex residue. Gap list =
[none needed | scoped Day-0 extensions].

## Deliverables
- docs/planning/EPIC_4/SPRINT_30/TOOLING_READINESS_AUDIT.md
- KNOWN_UNKNOWNS.md: Unknowns 1.4, 8.1, 8.3, 8.4 verified
- PREP_PLAN.md: Task 8 -> COMPLETE
- CHANGELOG.md: Task 8 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint30-task8
gh pr create --title "Complete Sprint 30 Prep Task 8: Reusable-Tooling Readiness Audit" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make lint && make format && make test` all PASS (audit-only)
- [x] Harness dual-transfer validated on robert + mine (head-offset multipliers)
- [x] `--resolve-changed` confirmed to cover the widened-VARIABLE + head-offset goldens
- [x] Property-test catalog confirmed extensible to the head-offset + offset-alias shapes
- [x] Gap list produced (each ≤ 1h) or "no extensions needed"
- [x] Unknowns 1.4, 8.1, 8.3, 8.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 8 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 9 Prompt: Backlog Fix-Surface Analysis (#1385 sarf; #1146/#1143/#1112/#1111; Class-B CGE `stat_pz`)

**Branch:** Create a new branch named `planning/sprint30-task9` from `main`

**Priority:** Medium (3–4 hours)

**Objective:** Produce the Day-0 patch-site hypotheses (PR24) + property-test fixture plan for the Sprint-30 tracks whose diagnosis is *banked but not yet implemented*: the #1385 sarf runtime-guard cross-terms (hand-derived Sprint 29), the offset-alias #1146/#1143 + #1111/#1112 fix (reverted Sprint 29 Day 5), and the Class-B CGE `stat_pz` coefficient discrepancy (harness-localized Sprint 29 Day 12). This is analogous to the Sprint-29 backlog fix-surface task but for the Sprint-30 "banked" set.

**Unknowns Verified:** 3.3, 4.1, 4.2, 5.1, 5.2, 5.3, 7.1

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_30/PREP_PLAN.md` §Task 9
- `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md` §Unknowns 3.3 (hhfair widened-VARIABLE blast radius), 4.1 (sarf atomic cross-terms), 4.2 (sarf instance count), 5.1 (Day-5 revert coupling), 5.2 (localized-vs-architectural), 5.3 (offset-alias blast radius), 7.1 (Class-B `stat_pz` shared fix)
- `docs/planning/EPIC_4/SPRINT_29/BACKLOG_FIX_SURFACE_ANALYSIS.md` (the Sprint-29 template) + `docs/planning/EPIC_4/SPRINT_30/TOOLING_READINESS_AUDIT.md` (Task 8 — the property-catalog extensibility) **← requires Task 8**
- `docs/issues/ISSUE_1385_*.md` (the banked cross-terms + sarf target), `docs/issues/ISSUE_{1146,1143}_*.md` (the offset-alias gates + the Day-5 revert), GitHub #1111/#1112; `docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md` §"Class B" (the `stat_pz` cluster); `tests/integration/emit/test_ad_crossterm_shapes.py`

**Tasks to Complete:**

1. #1385 sarf — pin the emit site where the runtime-guard equation-body re-emit + the banked `J_gᵀ·lam` cross-terms materialize (`src/kkt/stationarity.py` + `src/ad/index_mapping.py`); record the smallest-target verification (no quoted-set-name multiplier indices; byte-stable golden) + the instance-count tractability (no translate-timeout re-intro).
2. Offset-alias #1146/#1143 + #1111/#1112 — record the Day-5 revert root cause (the offset-image cross-term coupled with the distance-Jacobian), the coordinated-fix hypothesis, the property-test fixture (the cyclic `i++1` / successor `ord(j)=ord(i)+1` shape), and the blast radius; flag the #1111/#1112 architectural-REPLAN boundary.
3. Class-B CGE `stat_pz` — trace the general-emit coefficient-discrepancy patch site (the harness-localized `stat_pz` row, confirmed NOT Walras); record whether one fix converts several models (irscge/lrgcge/moncge/stdcge/marco).
4. Property-test fixture plan — the two new fixtures (head-domain-offset from Task 3, offset-alias-successor) that P8 adds to `test_ad_crossterm_shapes.py`. Also confirm the hhfair widened-VARIABLE fix blast radius (3.3).

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_30/BACKLOG_FIX_SURFACE_ANALYSIS.md` — the #1385 sarf emit site, the offset-alias coordinated-fix hypothesis + Day-5 revert root cause, the Class-B CGE `stat_pz` patch site, and the property-test fixture plan
- The #1111/#1112 architectural-REPLAN boundary flagged for the Task-6 assessment
- The two new property-test fixtures scoped for P8
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.3, 4.1, 4.2, 5.1, 5.2, 5.3, 7.1
- CHANGELOG.md updated with the Task 9 completion entry

**Known Unknowns Updates:** For Unknowns 3.3, 4.1, 4.2, 5.1, 5.2, 5.3, 7.1 in `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md`, set each "Verification Results": Status, Verified by Task 9, Date, Findings (the patch-site hypotheses + the Day-5 revert coupling + the Class-B shared-fix conversion count), Evidence (`kkt_residual.py` on the Class-B cluster + the ISSUE-doc traces), Decision (the coordinated-fix hypothesis + the #1111/#1112 architectural boundary + the fixture plan).

**PREP_PLAN.md Updates:** In §Task 9: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 30 Prep`, prepend:
```markdown
- **Prep Task 9 COMPLETE (YYYY-MM-DD):** backlog fix-surface analysis for the banked Sprint-30 tracks. `BACKLOG_FIX_SURFACE_ANALYSIS.md` — the #1385 sarf runtime-guard emit site + instance-count tractability; the offset-alias #1146/#1143 Day-5 revert coupling (offset-image × distance-Jacobian) + coordinated-fix hypothesis + the #1111/#1112 architectural-REPLAN boundary; the Class-B CGE `stat_pz` general-emit patch site (one fix / several models); the hhfair widened-VARIABLE blast radius; the two new property-test fixtures (head-offset + offset-alias-successor) scoped for P8. All framed as Day-0 hypotheses (PR24). Verified Unknowns 3.3, 4.1, 4.2, 5.1, 5.2, 5.3, 7.1.
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Analysis-only — no Python expected (the fixtures are *added in-sprint*). Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 30 Prep Task 9: Backlog Fix-Surface Analysis

BACKLOG_FIX_SURFACE_ANALYSIS.md: the #1385 sarf runtime-guard emit site + instance-
count tractability; the offset-alias #1146/#1143 Day-5 revert coupling (offset-image x
distance-Jacobian) + coordinated-fix hypothesis + the #1111/#1112 architectural-REPLAN
boundary; the Class-B CGE stat_pz general-emit patch site (one fix / several models);
the hhfair widened-VARIABLE blast radius; the two new property-test fixtures scoped for
P8. All framed as Day-0 hypotheses (PR24).

## Deliverables
- docs/planning/EPIC_4/SPRINT_30/BACKLOG_FIX_SURFACE_ANALYSIS.md
- KNOWN_UNKNOWNS.md: Unknowns 3.3, 4.1, 4.2, 5.1, 5.2, 5.3, 7.1 verified
- PREP_PLAN.md: Task 9 -> COMPLETE
- CHANGELOG.md: Task 9 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint30-task9
gh pr create --title "Complete Sprint 30 Prep Task 9: Backlog Fix-Surface Analysis" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make lint && make format && make test` all PASS (analysis-only)
- [x] All three banked tracks referenced (#1385 sarf, #1146/#1143/#1112/#1111 offset-alias, Class-B `stat_pz`)
- [x] Each patch-site framed as a Day-0 hypothesis (PR24)
- [x] The offset-alias Day-5 revert coupling recorded + the coordinated-fix hypothesis
- [x] Property-test fixture plan (head-offset + offset-alias-successor) present; #1111/#1112 boundary flagged
- [x] Unknowns 3.3, 4.1, 4.2, 5.1, 5.2, 5.3, 7.1 verified in KNOWN_UNKNOWNS.md
- [x] Task 9 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 10 Prompt: Plan Sprint 30 Detailed Schedule

**Branch:** Create a new branch named `planning/sprint30-task10` from `main`

**Priority:** Critical (3–4 hours) — **the terminal task; requires Tasks 1–9 done**

**Objective:** Produce the detailed 14-day Sprint 30 schedule (Day 0 setup + Days 1–13 execution) with day-by-day execution prompts, consuming all prep outputs (the Known Unknowns, the baseline, the head-offset design, the forcing survey, the Phase-0 gates, the REPLAN assessment, the camcge design, the tooling audit, the backlog analysis), and respecting the ≤ 12 hours/day budget from the PROJECT_PLAN.md Sprint 30 entry.

**Unknowns Verified:** (integrates all 25 — no new verification; consumes the resolved unknowns)

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_30/PREP_PLAN.md` §Task 10 + all Task 2–9 prep outputs (the schedule consumes them) **← requires Tasks 1–9**
- `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md` (all 25 unknowns should now be ✅ VERIFIED / ❌ WRONG)
- `docs/planning/EPIC_4/SPRINT_29/PLAN.md` + `docs/planning/EPIC_4/SPRINT_29/prompts/PLAN_PROMPTS.md` (the day-by-day schedule + prompt template)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 30" (the 8 priorities + the ≤12h/day budget + the heaviest-day note)

**Tasks to Complete:**

1. Sequence the 8 priorities across Days 1–13 — front-load P1 (head-offset architecture: robert minimal reproduction first, then mine generalization), interleave P2 (rocket forcing) + P3 (hhfair `$184`) early (both feed the Solve target), place P4/P5/P7 (banked cross-terms) mid-sprint, P6 (camcge Epic-5) + P8 (infrastructure) as they fit; respect ≤ 12h/day.
2. Embed the checkpoint re-solve at Day 5 + Day 10 using the Sprint-29 `--resolve-changed` gate + the PR25 re-baseline recompute.
3. Place the REPLAN decision points (mine-generalization Day ~6–7, rocket-forcing Day ~2–3, camcge-empirical Day ~11) per the Task-6 assessment, each with the specified fallback.
4. Write the day-by-day execution prompts (`prompts/PLAN_PROMPTS.md`) — one per day, each self-contained with objectives / branch / Phase-0 gate / quality gate / PR + wait-for-review.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_30/PLAN.md` — the Day 0–13 schedule with per-day objectives, the front-loaded P1 (robert → mine), the embedded checkpoint re-solves, the REPLAN decision points
- `docs/planning/EPIC_4/SPRINT_30/prompts/PLAN_PROMPTS.md` — the day-by-day execution prompts
- Confirmation the schedule fits ≤ 12h/day (< 168h total)
- CHANGELOG.md updated with the Task 10 completion entry (+ a "Sprint 30 prep phase COMPLETE" note)

**Known Unknowns Updates:** In `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md` §"Next Steps", update the PREP-PHASE note: all 25 unknowns VERIFIED (flag any that INVERTED / returned WRONG and how the schedule absorbs them), and mark "Sprint 30 is GO for Day 0." No new per-unknown verification blocks (Task 10 integrates, it does not verify).

**PREP_PLAN.md Updates:** In §Task 10: Status → ✅ COMPLETE; add `**Completed:** YYYY-MM-DD`; fill "Changes" + "Result"; check off all Acceptance Criteria. Also update the §Summary "Prep Task → Deliverable Map" statuses to ✅ and add a "Prep phase COMPLETE" line.

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 30 Prep`, prepend:
```markdown
- **Prep Task 10 COMPLETE (YYYY-MM-DD):** Sprint 30 14-day schedule (`docs/planning/EPIC_4/SPRINT_30/PLAN.md`, Day 0 + Days 1–13, ≤ 12h/day) + day-by-day execution prompts (`prompts/PLAN_PROMPTS.md`). Front-loads P1 (robert minimal reproduction → mine generalization), interleaves P2 rocket forcing + P3 hhfair `$184` early, embeds the Day-5/Day-10 `--resolve-changed` checkpoint re-solve + the PR25 re-baseline, and places the three REPLAN decision points (mine Day ~6–7, rocket Day ~2–3, camcge Day ~11) per the Task-6 assessment with fallbacks. Budget < 168h, no day > 12h. **All 25 prep unknowns integrated; Sprint 30 is GO for Day 0. Sprint 30 prep phase COMPLETE** (Tasks 1–10).
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 30 Prep Task 10: Plan Sprint 30 Detailed Schedule

PLAN.md (Day 0 + Days 1-13, <=12h/day) + prompts/PLAN_PROMPTS.md. Front-loads P1
(robert minimal reproduction -> mine generalization), interleaves P2 rocket forcing +
P3 hhfair $184 early, embeds the Day-5/Day-10 --resolve-changed checkpoint re-solve +
the PR25 re-baseline, places the three REPLAN decision points (mine, rocket, camcge)
per the Task-6 assessment with fallbacks. Budget < 168h, no day > 12h. Sprint 30 prep
phase COMPLETE (Tasks 1-10); Sprint 30 is GO for Day 0.

## Deliverables
- docs/planning/EPIC_4/SPRINT_30/PLAN.md
- docs/planning/EPIC_4/SPRINT_30/prompts/PLAN_PROMPTS.md
- KNOWN_UNKNOWNS.md: Next Steps -> prep phase COMPLETE
- PREP_PLAN.md: Task 10 -> COMPLETE + Summary map
- CHANGELOG.md: Task 10 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint30-task10
gh pr create --title "Complete Sprint 30 Prep Task 10: Plan Sprint 30 Detailed Schedule" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make lint && make format && make test` all PASS (docs-only)
- [x] PLAN.md covers Day 0 + Days 1–13; the 8 priorities sequenced with P1 front-loaded
- [x] The Day-5/Day-10 `--resolve-changed` checkpoint + PR25 re-baseline embedded
- [x] The three REPLAN decision points placed per the Task-6 assessment with fallbacks
- [x] PLAN_PROMPTS.md has one self-contained prompt per day
- [x] ≤ 12h/day budget respected (no day > 12h; < 168h total)
- [x] KNOWN_UNKNOWNS.md Next Steps → prep phase COMPLETE; Task 10 Acceptance Criteria all checked
EOF
)"
```

**Then wait for reviewer comments.**

---

## Prep-Task → Branch → PR Summary

| Prep Task | Branch | Unknowns Verified | Depends On |
|-----------|--------|-------------------|------------|
| Task 2: Day-0 Baseline + Genuine-Floor Re-Baseline | `planning/sprint30-task2` | 8.2 | None |
| Task 3: Head-Offset Architecture Design + robert Reproduction | `planning/sprint30-task3` | 1.1, 1.2, 1.3, 1.4 | Tasks 1, 2 |
| Task 4: Non-Convex Forcing Strategy Survey | `planning/sprint30-task4` | 2.1, 2.2, 2.3, 7.2 | Task 1 |
| Task 5: Refresh + Author Phase 0 Acceptance Gates | `planning/sprint30-task5` | 1.2, 1.3, 2.2, 3.1, 3.2, 4.1, 5.2, 6.1, 7.1, 7.3 | Tasks 1, 3 |
| Task 6: REPLAN-Prone Track Risk Assessment | `planning/sprint30-task6` | 1.1, 1.2, 2.1, 2.2, 6.1, 6.2 | Tasks 3, 4, 5 |
| Task 7: camcge → Epic 5 Walras Transformation Design | `planning/sprint30-task7` | 6.1, 6.2, 6.3 | Task 1 |
| Task 8: Reusable-Tooling Readiness Audit | `planning/sprint30-task8` | 1.4, 8.1, 8.3, 8.4 | Task 1 |
| Task 9: Backlog Fix-Surface Analysis | `planning/sprint30-task9` | 3.3, 4.1, 4.2, 5.1, 5.2, 5.3, 7.1 | Tasks 1, 8 |
| Task 10: Plan Sprint 30 Detailed Schedule | `planning/sprint30-task10` | (integrates all 25) | Tasks 1–9 |

**Critical path:** Task 1 → Task 3 → Task 5 → Task 6 → Task 10.
**Coverage:** every Sprint-30 unknown (1.1–8.4, 25 total) is verified by at least one prep task; Task 10 integrates all into the 14-day schedule.

# Sprint 24 Day-by-Day Execution Prompts

Step-by-step execution prompts for Sprint 24 Days 0-14.

**Usage:** Copy the relevant day's prompt into a new conversation to execute that day's work.

---

## Day 0 Prompt: Setup

**Branch:** Create a new branch named `sprint24-day0-setup` from `main`

**Objective:** Verify baseline, generate golden files, set up regression canary.

**Prerequisites:**
- Ensure `data/gamslib/raw/` is populated (gitignored; download via `python scripts/gamslib/download_models.py` if missing)

**Tasks to Complete (~1-2 hours):**

1. **Verify baseline metrics** match BASELINE_METRICS.md (parse 147/147, translate 140/147, solve 86, match 49)
2. **Generate golden-file stationarity output** for all 49 matching models:
   - Create output directory: `mkdir -p /tmp/gamslib-golden`
   - For each matching model, translate and save MCP to temp: `python -m src.cli data/gamslib/raw/{model}.gms -o /tmp/gamslib-golden/{model}_mcp.gms --skip-convexity-check`
3. **Set up dispatch regression canary test** — verify dispatch currently matches
4. **Initialize SPRINT_LOG.md** Day 0 entry

**Quality Checks:** Run `make typecheck && make lint && make format && make test` if any code changes.

---

## Day 1 Prompt: WS1 Phase 1 — Debug Pattern A (qabel)

**Branch:** Create a new branch named `sprint24-day1-alias-debug` from `main`

**Objective:** Debug why the alias differentiation mechanism (already implemented) doesn't fix Pattern A models. Trace qabel derivative computation end-to-end.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_24/PLAN.md` — Day 1 section
- Read `docs/planning/EPIC_4/SPRINT_24/DESIGN_ALIAS_DIFFERENTIATION_V2.md` — investigation strategy
- Key source files: `src/ad/derivative_rules.py` (lines 258-312 `_alias_match`, lines ~1771+ `_diff_sum` with bound augmentation at 1946-1948, lines 2093-2250 `_partial_collapse_sum`)

**Tasks to Complete (~3-4 hours):**

1. Add debug logging to `_diff_varref` and `_partial_collapse_sum`
2. Translate qabel: `python -m src.cli data/gamslib/raw/qabel.gms -o /tmp/qabel_mcp.gms --skip-convexity-check`
3. Trace the derivative computation for a specific stationarity equation
4. Identify the specific edge case (bound_indices over-inclusive? partial collapse not enumerating? index normalization?)
5. Run dispatch canary: verify still matches
6. Document findings

**Quality Checks:** `make typecheck && make lint && make format && make test`

---

## Day 2 Prompt: WS1 Phase 1 — Fix Pattern A Edge Case

**Branch:** Continue on `sprint24-day1-alias-debug` or create `sprint24-day2-alias-fix`

**Objective:** Implement fix for the identified Pattern A edge case. Validate qabel improvement.

**Tasks to Complete (~3-4 hours):**

1. Implement the fix identified on Day 1
2. Validate qabel gradient improvement (compare before/after stationarity)
3. Run dispatch canary — MUST still match
4. Run golden-file comparison for all 49 matching models — check for regressions
5. Run quality gate

---

## Day 3 Prompt: WS1 Phase 2 — Validate Pattern A

**Branch:** Continue or create `sprint24-day3-alias-validate`

**Objective:** Test all Pattern A models. Run full pipeline regression.

**Tasks to Complete (~3-4 hours):**

1. Test all Pattern A models: qabel, abel, irscge, lrgcge, moncge, stdcge, meanvar, ps2_s, ps3_s, ps3_s_gic, ps3_s_mn, ps5_s_mn, ps10_s_mn, cclinpts
2. Run full pipeline regression on all 86 solving models
3. Document which models improved (match, solve status change)
4. Fix any secondary issues

---

## Day 4 Prompt: WS1 Phase 2 Continue

**Branch:** Continue

**Objective:** Complete Pattern A validation. Fix secondary issues.

**Tasks to Complete (~2-3 hours):**

1. Fix any remaining Pattern A secondary issues
2. Run quality gate
3. Commit and push; create PR for WS1 Phase 1-2

---

## Day 5 Prompt: Checkpoint 1 + WS1 Phase 3 + WS2 Start

**Branch:** Create `sprint24-day5-checkpoint1` from `main`

**Objective:** Run Checkpoint 1; begin offset-alias (Pattern C) and subcategory H fixes.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_24/PLAN.md` — Checkpoint 1 criteria

**Tasks to Complete (~3-4 hours):**

1. **Checkpoint 1 evaluation:**
   - Alias regression count (must be 0 for GO)
   - Pattern A improvement count (≥ 3 for GO)
   - All tests pass
   - Document in SPRINT_LOG.md
2. **WS1 Phase 3:** Begin Pattern C (offset-alias) — polygon, himmel16
3. **WS2 Tier 1:** Begin subcategory H batch fix (concrete offsets in stationarity)
   - Target: catmix, ferts, ganges, gangesx, partssupply, polygon, tricp, turkpow

---

## Day 6 Prompt: WS1 Phase 3 + WS2 Tier 1

**Branch:** Continue or create `sprint24-day6-pse-batch`

**Objective:** Complete offset-alias fix and subcategory H batch fix.

**Tasks to Complete (~3-4 hours):**

1. Continue/complete offset-alias fix for polygon, himmel16
2. Continue/complete subcategory H batch fix
3. Run regression tests
4. Quality gate

---

## Day 7 Prompt: WS2 Complete + WS3 Tier 1

**Branch:** Create `sprint24-day7-mi-exclude`

**Objective:** Complete path_syntax_error fixes. Exclude Category C model_infeasible models.

**Tasks to Complete (~3-4 hours):**

1. Complete any remaining WS2 Tier 1 fixes
2. WS3 Tier 1: Exclude orani, feasopt1, iobalance (mark as permanent exclusions)
3. Check if WS1 alias fix resolved chenery, cesam, korcge
4. Run pipeline retest on affected models

---

## Day 8 Prompt: WS2 Tier 2 + WS4

**Branch:** Create `sprint24-day8-fixes`

**Objective:** Fix subcategory A models and mine internal error.

**Tasks to Complete (~3-4 hours):**

1. WS2 Tier 2: Fix decomp, ramsey, worst (subcategory A quick fixes)
2. WS4: Fix mine SetMembershipTest domain mismatch
3. Quality gate
4. Commit and push

---

## Day 9 Prompt: WS1 Phase 4 + WS2 Tier 3 + WS4

**Branch:** Create `sprint24-day9-investigate`

**Objective:** Investigate remaining patterns and timeout models.

**Tasks to Complete (~3-4 hours):**

1. WS1 Phase 4: Investigate kand (Pattern B) with debug logging
2. WS1 Phase 4: Investigate launch (Pattern D)
3. WS2 Tier 3: Investigate prolog regression
4. WS4: Profile iswnm timeout

---

## Day 10 Prompt: Checkpoint 2 + WS3 Tier 3

**Branch:** Create `sprint24-day10-checkpoint2`

**Objective:** Run Checkpoint 2; fix remaining model_infeasible if time.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_24/PLAN.md` — Checkpoint 2 criteria

**Tasks to Complete (~3-4 hours):**

1. **Checkpoint 2 evaluation:**
   - Solve ≥ 92 for GO
   - Match ≥ 52 for GO
   - path_syntax_error ≤ 18 for GO
   - Document in SPRINT_LOG.md
2. WS3 Tier 3: Fix bearing, pak, rocket (if time permits)
3. Run full pipeline retest

---

## Day 11 Prompt: Buffer / Overflow + Stretch Goals

**Branch:** Create `sprint24-day11-buffer` from `main`

**Objective:** Address overflows from Days 1-10; attempt stretch goals.

**Tasks to Complete (~2-3 hours):**

1. Complete any unfinished tasks
2. Stretch: additional model fixes
3. Pipeline retest (if new fixes)

---

## Day 12 Prompt: Sprint Close Prep

**Branch:** Create `sprint24-day12-close-prep` from `main`

**Objective:** File issues for deferred items; update documentation.

**Tasks to Complete (~1-2 hours):**

1. File issues for deferred/blocked items (label `sprint-25`)
2. Update KNOWN_UNKNOWNS.md with end-of-sprint discoveries
3. Update SPRINT_LOG.md
4. Run `make test`

---

## Day 13 Prompt: Final Pipeline Retest

**Branch:** Create `sprint24-day13-final-retest` from `main`

**Objective:** Final definitive metrics; verify all acceptance criteria.

**Tasks to Complete (~2-3 hours):**

1. Run `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
2. Record definitive final metrics (per PR6, PR8)
3. model_infeasible final accounting (per PR7)
4. Verify all acceptance criteria
5. Update gamslib_status.json

---

## Day 14 Prompt: Sprint Close + Retrospective

**Branch:** Create `sprint24-day14-retrospective` from `main`

**Objective:** Write retrospective; update CHANGELOG and PROJECT_PLAN.

**Tasks to Complete (~1-2 hours):**

1. Write Sprint 24 Retrospective
2. Update CHANGELOG.md
3. Update PROJECT_PLAN.md Rolling KPIs
4. Sprint 25 recommendations

# Sprint 23 Day-by-Day Prompts

This file contains comprehensive prompts for each day of Sprint 23 (Days 0–14). Each prompt is designed to be used when starting work on that specific day.

**Sprint Duration:** 15 days (Day 0 – Day 14)
**Estimated Effort:** ~32–44 hours (~2.1–2.9h/day effective capacity)
**Baseline:** parse 156/160 (97.5%), translate 139/156 (89.1%), solve 89 (64.0%), match 47/160 (29.4%), tests 4,209

---

## Day 0 Prompt: Baseline Confirm + Sprint Kickoff

**Branch:** Create a new branch named `sprint23-day0-kickoff` from `main`

**Objective:** Verify clean baseline, internalize the plan, confirm all tests pass, initialize sprint log.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_23/PLAN.md` — sprint overview, targets, and workstream summaries
- Read `docs/planning/EPIC_4/SPRINT_23/BASELINE_METRICS.md` — exact baseline numbers at commit `main @ 2c33989e`
- Read `docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md` — note KU-05 (cascade risk), KU-12 (alias regression risk)

**Tasks to Complete (~2-2.5 hours):**

1. **Verify baseline** (0.25h)
   - Run `make test` — must show 4,209 passed
   - Run `git log --oneline -5` — confirm you are on a clean commit from `main`

2. **Initialize SPRINT_LOG.md** (0.25h)
   - Open `docs/planning/EPIC_4/SPRINT_23/SPRINT_LOG.md`
   - Fill in baseline metrics from BASELINE_METRICS.md
   - Record the baseline commit: `main @ 2c33989e`

3. **Run baseline pipeline** (1.5h — ~76 min per PR6)
   - Run `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
   - Confirm parse 156/160, solve 89, match 47
   - Note translate count (may vary ±2-4 due to borderline timeouts)

4. **Map open issues to workstreams** (0.25h)
   - Review GitHub issues: `gh issue list --label sprint-23 --state open`
   - Confirm mapping matches PLAN.md Issue-to-Day Mapping table
   - Record in SPRINT_LOG.md

**Deliverables:**
- `make test` passing (4,209 tests)
- `docs/planning/EPIC_4/SPRINT_23/SPRINT_LOG.md` filled with baseline metrics
- Pipeline baseline confirmed

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] `make test` passes (4,209 tests)
- [ ] SPRINT_LOG.md filled with baseline metrics
- [ ] Pipeline baseline confirmed
- [ ] Mark Day 0 as complete in PLAN.md
- [ ] Log progress to CHANGELOG.md

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 23 Day 0: Baseline Confirm + Sprint Kickoff" \
                --body "Completes Day 0 tasks: baseline verified, SPRINT_LOG.md initialized."
   ```
2. Request a review from Copilot: `gh pr edit --add-reviewer copilot`
3. Address all review comments, reply directly to each, merge when approved.

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_23/PLAN.md` (Day 0 section)
- `docs/planning/EPIC_4/SPRINT_23/BASELINE_METRICS.md`
- `docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md`

---

## Day 1 Prompt: WS1 Tier 1 Quick Wins + WS5 LhsConditionalAssign

**Branch:** Create a new branch named `sprint23-day1-quickwins-translate` from `main`

**Objective:** Fix 3 path_solve_terminated execution errors (rocket, fawley, gtm) and recover 4 translate failures (LhsConditionalAssign emission). Low-risk, high-leverage.

**Prerequisites:**
- Day 0 PR must be merged
- Read `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SOLVE_TERMINATED.md` — rocket (INF bounds), fawley (zero-denom), gtm (log/div-by-0)
- Read `docs/planning/EPIC_4/SPRINT_23/CATALOG_TRANSLATE_FAILURES.md` §Category C — LhsConditionalAssign root cause and fix approach
- Read `src/emit/original_symbols.py` — understand LhsConditionalAssign emission paths
- Read `src/kkt/stationarity.py` — understand bound complementarity generation

**Tasks to Complete (~5-7 hours):**

1. **WS1: Fix rocket (2-3h combined with fawley/gtm)**
   - In the KKT emitter, suppress `piU_*` variables and `comp_up_*` equations for variables where upper bound is `+INF`
   - Similarly suppress `piL_*`/`comp_lo_*` for lower bound `-INF`
   - This is a general fix benefiting all models with infinite bounds
   - Smoke-test: `python -m src.cli data/gamslib/raw/rocket.gms -o /tmp/rocket_mcp.gms`

2. **WS1: Fix fawley (1-2h)**
   - Add zero-denominator guard: parameter assignment `bp(k,p)` needs check that sum denominator ≠ 0
   - Smoke-test: `python -m src.cli data/gamslib/raw/fawley.gms -o /tmp/fawley_mcp.gms`

3. **WS1: Fix gtm (2-3h)**
   - Clamp `.l` values for variables appearing inside `log()` or as denominators to small positive value (e.g., 0.01)
   - Same pattern as etamac (#984) fix from Sprint 22
   - Smoke-test: `python -m src.cli data/gamslib/raw/gtm.gms -o /tmp/gtm_mcp.gms`

4. **WS5: LhsConditionalAssign emission (2-3h)**
   - Handle `LhsConditionalAssign` at the statement/assignment emission layer
   - Emit as `lhs$(condition) = rhs;` — preserve LHS-conditional semantics (NOT RHS-dollar which assigns 0)
   - Verify against: agreste, ampl, cesam, korcge
   - Smoke-test each: `python -m src.cli data/gamslib/raw/agreste.gms -o /tmp/agreste_mcp.gms`

5. **Unit tests** (0.5h)
   - ≥ 6 tests: INF bound suppression, zero-denominator guard, variable clamping, LhsConditionalAssign emission

**Deliverables:**
- rocket, fawley, gtm advance past execution errors
- agreste, ampl, cesam, korcge translate successfully
- ≥ 6 new unit tests

**Quality Checks:**
Run `make typecheck && make lint && make format && make test` before commit.

**Completion Criteria:**
- [ ] rocket no longer has `+-infinity * 0` error
- [ ] fawley no longer has division by zero at parameter init
- [ ] gtm no longer has log(0)/div-by-0 errors
- [ ] 4 LhsConditionalAssign models translate
- [ ] ≥ 6 unit tests pass
- [ ] All existing tests pass
- [ ] Mark Day 1 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 23 Day 1: WS1 Tier 1 quick wins + WS5 LhsConditionalAssign" \
             --body "Fixes execution errors for rocket/fawley/gtm; adds LhsConditionalAssign emission for 4 translate models."
```

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_23/PLAN.md` (Day 1 section)
- `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SOLVE_TERMINATED.md` (rocket, fawley, gtm)
- `docs/planning/EPIC_4/SPRINT_23/CATALOG_TRANSLATE_FAILURES.md` (§Category C)

---

## Day 2 Prompt: WS3 Alias-Aware Differentiation (#1111, Part 1)

**Branch:** Create a new branch named `sprint23-day2-alias-diff` from `main`

**Objective:** Implement alias-aware differentiation with summation-context tracking. This is the highest-leverage match rate fix (21 mismatch models affected).

**Prerequisites:**
- Day 1 PR must be merged
- Read `docs/planning/EPIC_4/SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md` — FULL document, especially §4 (Proposed Fix Design) and §5 (Regression Risk)
- Read `src/ad/derivative_rules.py` — understand `differentiate_expr()`, `_diff_varref()`, `_diff_sum()`, `_diff_prod()`
- Read `src/config.py:40` — Config.model_ir carries aliases
- Read `src/ir/model_ir.py:37` — ModelIR.aliases (CaseInsensitiveDict[AliasDef])
- Read `src/ir/symbols.py:58` — AliasDef dataclass

**Tasks to Complete (~3-4 hours):**

1. **Add helper functions** (0.5h)
   - `_same_root_set(a, b, aliases) -> bool` — resolve alias chains, compare roots
   - `_alias_match(expr_indices, wrt_indices, aliases, bound_indices) -> Expr | None` — produce sameas() guards for free alias matches
   - Handle both `AliasDef` objects and plain string alias values (per design doc §3.3)

2. **Add `bound_indices` parameter** (1h)
   - Add `bound_indices: frozenset[str] = frozenset()` keyword-only arg to `differentiate_expr()` and ALL `_diff_*` functions
   - Thread through every recursive call — this is the most mechanical but critical part
   - Functions to modify: `differentiate_expr`, `_diff_varref`, `_diff_sum`, `_diff_prod`, `_diff_binary`, `_diff_unary`, `_diff_call`, `_diff_dollar_conditional`

3. **Thread through Sum/Prod** (0.5h)
   - In `_diff_sum()`: `new_bound = bound_indices | frozenset(expr.index_sets)` before recursing
   - Same for `_diff_prod()`

4. **Alias-aware matching in `_diff_varref()`** (0.5h)
   - After exact `_indices_match()` fails, check `_alias_match()` if aliases are available
   - Return sameas() guard for free alias indices; return None (→ Const(0.0)) for bound aliases
   - **Update return type** from `-> Const` to `-> Expr` — review any downstream code that assumes `Const`

5. **Unit tests** (1h)
   - `test_alias_varref_free_index` — `d/d(x(n,k))` of `x(np,k)` → sameas(np,n)
   - `test_alias_varref_bound_index` — `d/d(p(i))` of `p(j)` in sum((i,j),...) → 0
   - `test_alias_sum_collapse` — sum(np, x(np,k)) w.r.t. x(n,k)
   - `test_no_alias_unchanged` — non-alias models produce identical derivatives
   - `test_same_root_set_resolution` — alias chain resolution

**Deliverables:**
- Alias-aware differentiation implemented in `src/ad/derivative_rules.py`
- `bound_indices` threaded through entire AD call stack
- ≥ 5 unit tests

**Quality Checks:**
Run `make typecheck && make lint && make format && make test` before commit.

**Completion Criteria:**
- [ ] `_same_root_set()` and `_alias_match()` implemented
- [ ] `bound_indices` parameter on all `_diff_*` functions
- [ ] `_diff_sum()` and `_diff_prod()` augment bound_indices before recursing
- [ ] `_diff_varref()` produces sameas() guards for free aliases
- [ ] ≥ 5 unit tests pass
- [ ] All existing tests pass (`make test`)
- [ ] Mark Day 2 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 23 Day 2: Alias-aware differentiation (#1111)" \
             --body "Implements summation-context tracking for alias-aware AD. Adds bound_indices parameter, alias matching in _diff_varref, sameas guard generation."
```

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md`
- `src/ad/derivative_rules.py`

---

## Day 3 Prompt: WS3 Alias Differentiation Integration + Pipeline Validation

**Branch:** Create a new branch named `sprint23-day3-alias-integration` from `main`

**Objective:** Integration testing for #1111. Verify qabel improves, dispatch doesn't regress, run pipeline regression check on all 89 solving models.

**Prerequisites:**
- Day 2 PR must be merged
- Read Day 2 results in SPRINT_LOG.md
- Read `docs/planning/EPIC_4/SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md` §6 (Test Plan)

**Tasks to Complete (~2-3 hours):**

1. **Integration test: qabel** (0.5h)
   - `python -m src.cli data/gamslib/raw/qabel.gms -o /tmp/qabel_mcp.gms`
   - Verify gradient includes cross-term derivatives (sameas guards in stationarity)
   - If GAMS available: run MCP, check if objective difference reduced

2. **Integration test: dispatch** (0.5h)
   - `python -m src.cli data/gamslib/raw/dispatch.gms -o /tmp/dispatch_mcp.gms`
   - **CRITICAL:** Verify dispatch still matches (regression canary)
   - Check that sum-bound aliases do NOT produce sameas guards

3. **Smoke-test all 8 matching alias models** (0.5h)
   - dispatch, gussrisk, nemhaus, ps2_f, ps3_f, quocge, ship, splcge
   - All must still produce correct MCP output

4. **Pipeline retest (solve subset)** (0.5h)
   - Run `.venv/bin/python scripts/gamslib/run_full_test.py --only-solve --quiet`
   - Check: no match regressions among 47 currently-matching models
   - Record how many alias mismatch models improved

5. **Fix edge cases** (0.5-1h buffer)
   - Address any failing tests or unexpected behaviors
   - Common edge cases: nested sums, partial collapse, multi-alias chains

**Deliverables:**
- qabel gradient verified to include alias cross-terms
- dispatch confirmed not regressed
- All 8 matching alias models stable
- Pipeline regression check: 0 match regressions
- Count of newly-matching models from alias fix

**Quality Checks:**
Run `make typecheck && make lint && make format && make test` before commit.

**Completion Criteria:**
- [ ] qabel gradient includes sameas cross-terms
- [ ] dispatch still matches (no regression)
- [ ] All 8 matching alias models stable
- [ ] 0 match regressions in pipeline retest
- [ ] ≥ 3 alias mismatch models improve or newly match
- [ ] Mark Day 3 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 23 Day 3: Alias differentiation integration + validation" \
             --body "Integration tests for #1111: qabel verified, dispatch not regressed, pipeline regression check clean."
```

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md` (§6 Test Plan, §2.3 regression models)

---

## Day 4 Prompt: WS3 Dollar-Condition Propagation (#1112) + WS1 maxmin

**Branch:** Create a new branch named `sprint23-day4-dollar-cond-maxmin` from `main`

**Objective:** Implement dollar-condition propagation through AD/stationarity pipeline (#1112); fix maxmin self-pair domain violation.

**Prerequisites:**
- Day 3 PR must be merged
- Read `docs/planning/EPIC_4/SPRINT_23/DESIGN_DOLLAR_CONDITION_PROPAGATION.md` — FULL document, especially §3 (Proposed Design) and §7 (Detailed Algorithm)
- Read `src/ad/gradient.py:197-276` — `compute_objective_gradient()`
- Read `src/kkt/kkt_system.py:73-191` — KKTSystem dataclass
- Read `src/kkt/stationarity.py:756-945` — `build_stationarity_equations()`
- Read `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SOLVE_TERMINATED.md` (maxmin section)

**Tasks to Complete (~3-4 hours):**

1. **#1112 Step 1: Add `_extract_gradient_conditions()` to gradient.py** (1h)
   - New function (~40 lines) after `compute_objective_gradient()`
   - Extract DollarConditional/multiplicative condition factors from gradient entries
   - Per-variable aggregation: only return condition if ALL entries share the same condition
   - See DESIGN doc §7.2-§7.3 for detailed algorithm

2. **#1112 Step 2: Add `gradient_conditions` field to KKTSystem** (10min)
   - Add `gradient_conditions: dict[str, Expr] = field(default_factory=dict)` to KKTSystem
   - Populate after gradient computation

3. **#1112 Step 3: Add Stage 4 check in `build_stationarity_equations()`** (30min)
   - After existing three-stage condition detection, add:
     ```python
     if access_cond is None and var_name in kkt.gradient_conditions:
         access_cond = kkt.gradient_conditions[var_name]
     ```
   - Stage 4 is fallback-only: only applies when no other condition found

4. **WS1: Fix maxmin self-pair** (2-3h)
   - Propagate `low(n,nn)` domain condition from `mindist1a` through Jacobian to stationarity
   - Add `$(low(n,nn))` guards on distance derivative terms where `n==nn` gives sqrt(0)
   - Smoke-test: `python -m src.cli data/gamslib/raw/maxmin.gms -o /tmp/maxmin_mcp.gms`

5. **Unit tests** (0.5h)
   - `_extract_gradient_conditions()`: DollarConditional wrapper extraction, multiplicative factor extraction, mixed (returns None), consistent condition
   - maxmin: self-pair guard generation

**Deliverables:**
- #1112 dollar-condition propagation implemented (3 files changed)
- maxmin advances past self-pair division by zero
- ≥ 4 unit tests

**Quality Checks:**
Run `make typecheck && make lint && make format && make test` before commit.

**Completion Criteria:**
- [ ] `_extract_gradient_conditions()` implemented in gradient.py
- [ ] `gradient_conditions` field on KKTSystem
- [ ] Stage 4 check in `build_stationarity_equations()`
- [ ] maxmin no longer has division by sqrt(0)
- [ ] ≥ 4 unit tests pass
- [ ] All existing tests pass
- [ ] Mark Day 4 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 23 Day 4: Dollar-condition propagation (#1112) + maxmin fix" \
             --body "Implements gradient condition extraction and stationarity propagation. Fixes maxmin self-pair domain violation."
```

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_23/DESIGN_DOLLAR_CONDITION_PROPAGATION.md`
- `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SOLVE_TERMINATED.md` (maxmin)

---

## Day 5 Prompt: Checkpoint 1 + WS1 Tier 2 (sambal, qsambal)

**Branch:** Create a new branch named `sprint23-day5-checkpoint1-sambal` from `main`

**Objective:** Run Checkpoint 1 full pipeline (per PR6); verify sambal/qsambal fixed by #1112.

**Prerequisites:**
- Day 4 PR must be merged
- Read `docs/planning/EPIC_4/SPRINT_23/PLAN.md` — Checkpoint 1 GO/NO-GO criteria
- Read `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SOLVE_TERMINATED.md` (sambal, qsambal)

**Tasks to Complete (~3-4 hours):**

1. **Full pipeline retest (per PR6)** (1.5h — ~76 min)
   - Run `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
   - Record ALL metrics: parse, translate, solve, match, error categories
   - Report metrics using both absolute counts and percentages (PR8)

2. **Checkpoint 1 evaluation** (0.5h)
   - Evaluate against GO/CONDITIONAL GO/NO-GO criteria:
     - Solve ≥ 95 → GO; ≥ 92 → CONDITIONAL; < 92 → NO-GO
     - Match ≥ 50 → GO; ≥ 48 → CONDITIONAL; < 48 → NO-GO
     - path_solve_terminated ≤ 7 → GO
     - Translate ≥ 143 → GO
     - #1111 PR merged → GO
   - Track model_infeasible gross fixes and influx (PR7)
   - Document decision in SPRINT_LOG.md

3. **WS1: Verify sambal fix** (0.5h)
   - `python -m src.cli data/gamslib/raw/sambal.gms -o /tmp/sambal_mcp.gms`
   - Check: stationarity equation has equation-level `$(xw(i,j))` guard
   - If GAMS available: verify MODEL STATUS ≠ 4/5

4. **WS1: Verify qsambal** (0.25h)
   - `python -m src.cli data/gamslib/raw/qsambal.gms -o /tmp/qsambal_mcp.gms`
   - Should inherit sambal fix automatically

5. **Update SPRINT_LOG.md** (0.25h)
   - Record Checkpoint 1 metrics
   - Record GO/NO-GO decision
   - Record model_infeasible gross/influx tracking

**Deliverables:**
- Checkpoint 1 metrics recorded (full pipeline per PR6)
- GO/CONDITIONAL GO/NO-GO decision documented
- sambal and qsambal verified
- model_infeasible gross/influx tracking (PR7)

**Quality Checks:**
Run `make typecheck && make lint && make format && make test` before commit (if code changes made).

**Completion Criteria:**
- [ ] Full pipeline run completed
- [ ] Checkpoint 1 evaluated
- [ ] sambal no longer has division by zero
- [ ] qsambal inherits fix
- [ ] SPRINT_LOG.md updated with Checkpoint 1 metrics
- [ ] Mark Day 5 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 23 Day 5: Checkpoint 1 + sambal/qsambal verification" \
             --body "Checkpoint 1 full pipeline run. Verifies sambal/qsambal fixed by #1112."
```

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_23/PLAN.md` (Checkpoint 1 criteria)
- `docs/planning/EPIC_4/SPRINT_23/BASELINE_METRICS.md`

---

## Day 6 Prompt: WS2 model_infeasible Tier 1 Part 1 (markov, pak)

**Branch:** Create a new branch named `sprint23-day6-markov-pak` from `main`

**Objective:** Fix markov multi-pattern Jacobian (#1110) and pak lead/lag Jacobian (#1049).

**Prerequisites:**
- Day 5 PR must be merged; Checkpoint 1 GO
- Read `docs/planning/EPIC_4/SPRINT_23/TRIAGE_MODEL_INFEASIBLE.md` (markov, pak sections)
- Read GitHub issue #1110 (markov) — detailed root cause
- Read GitHub issue #1049 (pak) — detailed root cause
- Read `src/kkt/stationarity.py` — understand `_add_indexed_jacobian_terms()`

**Tasks to Complete (~6-8 hours):**

1. **Fix markov (#1110)** (3-4h)
   - Root cause: stationarity builder uses single representative derivative for all constraint-variable pairings
   - Fix: generate per-pattern stationarity equations with sameas-guarded terms for each unique derivative pattern
   - File: `src/kkt/stationarity.py`, `_add_indexed_jacobian_terms()` area
   - Smoke-test: `python -m src.cli data/gamslib/raw/markov.gms -o /tmp/markov_mcp.gms`

2. **Fix pak (#1049)** (3-4h)
   - Root cause: lead/lag variable references in constraint bodies missing Jacobian entries
   - Fix: ensure lead/lag references generate correct Jacobian entries for shifted time period
   - Files: `src/ad/constraint_jacobian.py`, `src/kkt/stationarity.py`
   - Smoke-test: `python -m src.cli data/gamslib/raw/pak.gms -o /tmp/pak_mcp.gms`

3. **Unit tests** (0.5h)
   - ≥ 4 tests: multi-pattern Jacobian, lead/lag Jacobian entries

**Deliverables:**
- markov no longer model_infeasible
- pak no longer aborts on MCP pairing
- ≥ 4 unit tests

**Quality Checks:**
Run `make typecheck && make lint && make format && make test` before commit.

**Completion Criteria:**
- [ ] markov: per-pattern stationarity equations generated
- [ ] pak: lead/lag Jacobian entries correct
- [ ] Both models advance past model_infeasible/pairing error
- [ ] ≥ 4 unit tests
- [ ] All existing tests pass
- [ ] Mark Day 6 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 23 Day 6: Fix markov (#1110) and pak (#1049)" \
             --body "Multi-pattern Jacobian for markov; lead/lag Jacobian entries for pak."
```

---

## Day 7 Prompt: WS2 model_infeasible Tier 1 Part 2 (paperco, sparta)

**Branch:** Create a new branch named `sprint23-day7-paperco-sparta` from `main`

**Objective:** Fix paperco loop body parameter extraction (#953) and sparta bal4 KKT (#1081).

**Prerequisites:**
- Day 6 PR must be merged
- Read `docs/planning/EPIC_4/SPRINT_23/TRIAGE_MODEL_INFEASIBLE.md` (paperco, sparta sections)
- Read GitHub issue #953 (paperco) — loop body parameter extraction
- Read GitHub issue #1081 (sparta) — bal4 KKT bug
- Read `src/ir/parser.py` — understand `_handle_loop_stmt()`

**Tasks to Complete (~6-7 hours):**

1. **Fix paperco (#953)** (3-4h)
   - Root cause: parameter `pp(p)` assigned inside `loop(scenario, ...)` body not extracted
   - Fix: enhance loop body extraction in IR parser to walk and extract parameter assignments
   - File: `src/ir/parser.py`, `_handle_loop_stmt()`
   - Smoke-test: `python -m src.cli data/gamslib/raw/paperco.gms -o /tmp/paperco_mcp.gms`

2. **Fix sparta (#1081)** (2-3h)
   - Root cause: KKT derivation bug specific to bal4 constraint structure
   - Note: sparta is multi-solve (#1080) — comparison validation needs special handling
   - File: `src/kkt/stationarity.py`
   - Smoke-test: `python -m src.cli data/gamslib/raw/sparta.gms -o /tmp/sparta_mcp.gms`

3. **Unit tests** (0.5h)
   - ≥ 3 tests: loop body parameter extraction, bal4 KKT derivation

**Deliverables:**
- paperco no longer model_infeasible
- sparta KKT bug fixed (bal4)
- ≥ 3 unit tests

**Quality Checks:**
Run `make typecheck && make lint && make format && make test` before commit.

**Completion Criteria:**
- [ ] paperco: `pp(p)` parameter correctly emitted
- [ ] sparta: bal4 KKT derivation correct
- [ ] Both models advance
- [ ] ≥ 3 unit tests
- [ ] All existing tests pass
- [ ] Mark Day 7 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 23 Day 7: Fix paperco (#953) and sparta (#1081)" \
             --body "Loop body parameter extraction for paperco; bal4 KKT fix for sparta."
```

---

## Day 8 Prompt: WS2 spatequ (#1038) + WS4 srkandw (subcategory G)

**Branch:** Create a new branch named `sprint23-day8-spatequ-srkandw` from `main`

**Objective:** Fix spatequ Jacobian domain mismatch (#1038) and srkandw parser bug (subcategory G).

**Prerequisites:**
- Day 7 PR must be merged
- Read `docs/planning/EPIC_4/SPRINT_23/TRIAGE_MODEL_INFEASIBLE.md` (spatequ section)
- Read `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SYNTAX_ERROR_GB.md` (srkandw section)
- Read GitHub issue #1038 (spatequ)

**Tasks to Complete (~5-7 hours):**

1. **Fix spatequ (#1038)** (3-4h)
   - Root cause: sum index binding fails for 3D variable `X(r,rr,c)` vs 2D equation `(r,c)`
   - Fix: correct sum index binding in Jacobian assembly
   - Files: `src/ad/constraint_jacobian.py`, `src/kkt/assemble.py`
   - Smoke-test: `python -m src.cli data/gamslib/raw/spatequ.gms -o /tmp/spatequ_mcp.gms`

2. **Fix srkandw (subcategory G)** (2-3h)
   - Root cause: `_handle_aggregation()` incorrectly filters out subset domain index `n` because it appears in equation's free domain
   - Fix: do NOT filter indices that appear in subset specifications with literal co-indices
   - File: `src/ir/parser.py`, `_handle_aggregation()` (~line 4758)
   - Smoke-test: verify `sum(n$(tn('time-2',n)), 1)` is emitted correctly (not `sum(()$(tn(n)), 1)`)

3. **Unit tests** (0.5h)
   - ≥ 3 tests: Jacobian domain binding, aggregation subset filter

**Deliverables:**
- spatequ no longer model_infeasible (completes WS2 Tier 1)
- srkandw no longer has path_syntax_error
- ≥ 3 unit tests

**Quality Checks:**
Run `make typecheck && make lint && make format && make test` before commit.

**Completion Criteria:**
- [ ] spatequ: sum index binding correct for 3D/2D case
- [ ] srkandw: parser preserves subset domain index in aggregation
- [ ] ≥ 3 unit tests
- [ ] All existing tests pass
- [ ] Mark Day 8 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 23 Day 8: Fix spatequ (#1038) + srkandw (subcategory G)" \
             --body "Jacobian domain mismatch fix for spatequ; parser aggregation fix for srkandw."
```

---

## Day 9 Prompt: WS4 path_syntax_error B (chenery, shale)

**Branch:** Create a new branch named `sprint23-day9-chenery-shale` from `main`

**Objective:** Fix chenery index shadowing and shale subset condition domain (subcategory B).

**Prerequisites:**
- Day 8 PR must be merged
- Read `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SYNTAX_ERROR_GB.md` (chenery, shale sections)

**Tasks to Complete (~4-5 hours):**

1. **Fix chenery (subcategory B)** (1-2h)
   - Root cause: `t` used as both sum loop index and in condition `$(t(i))`
   - Fix: extend `resolve_index_conflicts()` to detect condition-scope shadowing; rename sum index
   - File: `src/emit/expr_to_gams.py`
   - Smoke-test: `python -m src.cli data/gamslib/raw/chenery.gms -o /tmp/chenery_mcp.gms`

2. **Fix shale (subcategory B)** (2-3h)
   - Root cause: `$(cf(c) and t(tf))` — subset condition on stationarity equation domain mismatch
   - Fix: verify set hierarchy `t` ⊂ `tf`; adjust condition or domain
   - File: `src/kkt/stationarity.py`
   - Smoke-test: `python -m src.cli data/gamslib/raw/shale.gms -o /tmp/shale_mcp.gms`

3. **Unit tests** (0.5h)
   - ≥ 2 tests: condition-scope shadowing, subset condition domain

**Deliverables:**
- chenery and shale no longer have path_syntax_error
- ≥ 2 unit tests

**Quality Checks:**
Run `make typecheck && make lint && make format && make test` before commit.

**Completion Criteria:**
- [ ] chenery: sum index renamed to avoid condition shadowing
- [ ] shale: subset condition domain corrected
- [ ] ≥ 2 unit tests
- [ ] All existing tests pass
- [ ] Mark Day 9 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 23 Day 9: Fix chenery + shale path_syntax_error (subcategory B)" \
             --body "Index shadowing fix for chenery; subset condition domain fix for shale."
```

---

## Day 10 Prompt: Checkpoint 2 + WS4 Remaining (otpop, hhfair)

**Branch:** Create a new branch named `sprint23-day10-checkpoint2` from `main`

**Objective:** Run Checkpoint 2 full pipeline (per PR6); complete remaining path_syntax_error fixes if GO.

**Prerequisites:**
- Day 9 PR must be merged
- Read `docs/planning/EPIC_4/SPRINT_23/PLAN.md` — Checkpoint 2 GO/NO-GO criteria
- Read `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SYNTAX_ERROR_GB.md` (otpop, hhfair sections)

**Tasks to Complete (~3-4 hours):**

1. **Full pipeline retest (per PR6)** (1.5h — ~76 min)
   - Run `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
   - Record ALL metrics (absolute counts + percentages per PR8)

2. **Checkpoint 2 evaluation** (0.5h)
   - Evaluate against GO/NO-GO criteria
   - Track model_infeasible gross fixes and influx (PR7)
   - Document decision in SPRINT_LOG.md

3. **WS4: Fix otpop (if GO)** (2-3h)
   - Root cause: `$(t(tt))` alias-as-subset condition on wrong domain level
   - Investigate subset/alias relationships; fix condition form
   - Smoke-test: `python -m src.cli data/gamslib/raw/otpop.gms -o /tmp/otpop_mcp.gms`

4. **WS4: Fix hhfair (if GO and time permits)** (2-3h)
   - Root cause: `nu_budget(tl+1)` — IndexOffset emission needs lag/lead syntax
   - Fix: emitter should use lead index alias instead of arithmetic on index
   - Smoke-test: `python -m src.cli data/gamslib/raw/hhfair.gms -o /tmp/hhfair_mcp.gms`

**Deliverables:**
- Checkpoint 2 metrics (full pipeline per PR6)
- GO/NO-GO decision
- otpop and hhfair fixed (if GO)

**Quality Checks:**
Run `make typecheck && make lint && make format && make test` before commit (if code changes).

**Completion Criteria:**
- [ ] Full pipeline run completed
- [ ] Checkpoint 2 evaluated and documented
- [ ] model_infeasible gross/influx recorded (PR7)
- [ ] otpop path_syntax_error fixed (if GO)
- [ ] hhfair path_syntax_error fixed (if GO and time)
- [ ] Mark Day 10 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 23 Day 10: Checkpoint 2 + WS4 otpop/hhfair" \
             --body "Checkpoint 2 full pipeline. Path_syntax_error fixes for otpop and hhfair."
```

---

## Day 11 Prompt: Buffer / Overflow + Stretch Goals

**Branch:** Create a new branch named `sprint23-day11-buffer` from `main`

**Objective:** Address overflows from Days 1-10; attempt stretch goals if schedule permits.

**Prerequisites:**
- Day 10 PR must be merged; Checkpoint 2 GO
- Review SPRINT_LOG.md — identify unfinished tasks and metrics gaps

**Tasks to Complete (~2-3 hours):**

1. **Complete any unfinished tasks** (varies)
   - Check SPRINT_LOG.md for incomplete items from Days 1-10
   - Priority order: WS2 Tier 1 (if any remain) > WS4 G+B > WS1 Tier 2

2. **WS5 Tier 2 (stretch): mine SetMembershipTest** (2-3h)
   - Add `SetMembershipTest` evaluation to `src/ir/condition_eval.py`
   - Recovers mine translate (+1)

3. **WS5 Tier 3 (stretch): mexls universal set (#940)** (3-4h)
   - Add implicit universal set to ModelIR or special-case `'*'` in index_mapping
   - Recovers mexls translate (+1)

4. **WS2 Tier 2 (stretch): bearing investigation** (1-2h)
   - Identify which equations/variables are unmatched
   - Document fix approach for Sprint 24 if not fixable

5. **Pipeline retest** (if new fixes)

**Deliverables:**
- All core workstream targets met
- Stretch: additional translate recoveries
- Updated metrics

**Quality Checks:**
Run `make typecheck && make lint && make format && make test` before commit (if code changes).

**Completion Criteria:**
- [ ] All unfinished Day 1-10 tasks completed or documented
- [ ] Stretch goals attempted (as schedule permits)
- [ ] Mark Day 11 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 23 Day 11: Buffer/overflow + stretch goals" \
             --body "Addresses overflows and stretch goals."
```

---

## Day 12 Prompt: Sprint Close Prep — Issues + Documentation

**Branch:** Create a new branch named `sprint23-day12-close-prep` from `main`

**Objective:** File issues for deferred items; update documentation.

**Prerequisites:**
- Day 11 PR must be merged
- Review all workstream results in SPRINT_LOG.md

**Tasks to Complete (~1-2 hours):**

1. **File issues for deferred/blocked items** (0.5h)
   - Label new issues with `sprint-24`
   - Include: elec convergence, dyncge/twocge CGE, remaining model_infeasible Tier 3, any new discoveries

2. **Update KNOWN_UNKNOWNS.md** (0.5h)
   - Add any new unknowns discovered during sprint
   - Update verification status for existing unknowns

3. **Update SPRINT_LOG.md** (0.25h)
   - Record current metrics
   - Document all PRs merged

4. **Run `make test`** (0.25h)
   - Confirm all tests pass

**Deliverables:**
- GitHub issues filed for deferred items
- KNOWN_UNKNOWNS.md updated
- SPRINT_LOG.md current

**Completion Criteria:**
- [ ] All deferred items have GitHub issues
- [ ] KNOWN_UNKNOWNS.md updated
- [ ] SPRINT_LOG.md up to date
- [ ] All tests pass
- [ ] Mark Day 12 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 23 Day 12: Close prep — issues + documentation" \
             --body "Files deferred issues, updates KNOWN_UNKNOWNS and SPRINT_LOG."
```

---

## Day 13 Prompt: Final Pipeline Retest + Sprint Close

**Branch:** Create a new branch named `sprint23-day13-final-retest` from `main`

**Objective:** Final definitive full pipeline metrics (per PR6); verify all acceptance criteria.

**Prerequisites:**
- Day 12 PR must be merged

**Tasks to Complete (~2-3 hours):**

1. **Final full pipeline retest (per PR6)** (1.5h — ~76 min)
   - Run `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
   - Record DEFINITIVE final metrics (this is the official Sprint 23 result)
   - Use absolute counts AND percentages (PR8)

2. **model_infeasible final accounting (per PR7)** (0.25h)
   - Record gross fixes: how many models fixed out of infeasible
   - Record gross influx: how many models newly entered infeasible
   - Record net change: gross fixes - gross influx

3. **Verify all acceptance criteria** (0.25h)
   - Solve ≥ 100? Match ≥ 55? path_solve_terminated ≤ 5? etc.
   - Check each criterion against final pipeline results
   - Document met/missed in SPRINT_LOG.md

4. **Update gamslib_status.json** (0.25h)
   - Ensure the pipeline results are committed

**Deliverables:**
- Final definitive metrics (full pipeline per PR6)
- model_infeasible gross/influx accounting (PR7)
- Acceptance criteria evaluation
- Updated gamslib_status.json

**Completion Criteria:**
- [ ] Final full pipeline run completed
- [ ] All metrics recorded in SPRINT_LOG.md
- [ ] model_infeasible gross/influx recorded (PR7)
- [ ] All acceptance criteria evaluated
- [ ] Mark Day 13 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 23 Day 13: Final pipeline retest + sprint close" \
             --body "Definitive Sprint 23 metrics. Final acceptance criteria evaluation."
```

---

## Day 14 Prompt: Sprint Close + Retrospective

**Branch:** Create a new branch named `sprint23-day14-retrospective` from `main`

**Objective:** Write Sprint 23 retrospective; update CHANGELOG and PROJECT_PLAN; outline Sprint 24 scope.

**Prerequisites:**
- Day 13 PR must be merged
- Read SPRINT_LOG.md — final metrics
- Read `docs/planning/EPIC_4/SPRINT_22/SPRINT_RETROSPECTIVE.md` — template/format

**Tasks to Complete (~1-2 hours):**

1. **Write Sprint 23 Retrospective** (0.75h)
   - Create `docs/planning/EPIC_4/SPRINT_23/SPRINT_RETROSPECTIVE.md`
   - Sections: Executive Summary, Goals and Results, Metrics Summary, Error Category Breakdown, What Went Well, What Could Be Improved, What We'd Do Differently, Sprint 24 Recommendations, Process Recommendation Review, Final Metrics Comparison (Sprint 20-23)
   - Include: workstream summary table (planned vs actual effort), deferred items

2. **Update CHANGELOG.md** (0.25h)
   - Add Sprint 23 summary under `[Unreleased]`
   - Include: metrics deltas, key changes, PRs

3. **Update PROJECT_PLAN.md Rolling KPIs** (0.25h)
   - Fill in Sprint 23 actuals in KPI table
   - Update Sprint 24 recommendations based on retrospective

4. **Sprint 24 recommendations** (0.25h)
   - Document in retrospective
   - Include: suggested targets, priority areas, deferred items

**Deliverables:**
- Sprint 23 Retrospective
- CHANGELOG.md updated
- PROJECT_PLAN.md Rolling KPIs updated
- Sprint 24 recommendations

**Completion Criteria:**
- [ ] Retrospective written with all sections
- [ ] CHANGELOG.md updated
- [ ] PROJECT_PLAN.md KPIs filled
- [ ] Sprint 24 scope outlined
- [ ] Mark Day 14 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 23 Day 14: Sprint close + retrospective" \
             --body "Sprint 23 retrospective, CHANGELOG update, PROJECT_PLAN KPIs."
```

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_22/SPRINT_RETROSPECTIVE.md` (template)
- `docs/planning/EPIC_4/SPRINT_23/SPRINT_LOG.md` (final metrics)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` (Rolling KPIs table)

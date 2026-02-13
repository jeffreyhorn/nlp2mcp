# Sprint 19 Day-by-Day Prompts

This file contains comprehensive prompts for each day of Sprint 19 (Days 0-14). Each prompt is designed to be used when starting work on that specific day.

**Sprint:** 19 (Epic 4)
**Duration:** 14 working days + Day 0 setup
**Total Effort:** 42-54 hours (~3-4h/day effective capacity)
**Baseline:** Parse 61/159 (38.4%), lexer_invalid_char: 72, internal_error: 24

---

## Day 0 Prompt: Sprint Initialization

**Branch:** Create a new branch named `sprint19-day0-init` from `main`

**Objective:** Initialize Sprint 19 infrastructure: create SPRINT_LOG.md, verify all prep task PRs are merged, confirm branch setup.

**Prerequisites:**
- Verify all 10 prep task PRs have been merged to `main`
- Read `docs/planning/EPIC_4/SPRINT_19/PLAN.md` — Full sprint plan
- Read `docs/planning/EPIC_4/SPRINT_19/BASELINE_METRICS.md` — Verified v1.2.0 baseline numbers
- Read `docs/planning/EPIC_2/SPRINT_11/incremental_documentation_guide.md` — Templates for SPRINT_LOG.md

**Tasks to Complete (1-2 hours):**

1. **Verify prep completion** (0.5h)
   - Checkout `main` and pull latest
   - Confirm all 10 prep task deliverables exist:
     - `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md`
     - `docs/planning/EPIC_4/SPRINT_19/INTERNAL_ERROR_ANALYSIS_PREP.md`
     - `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md`
     - `docs/planning/EPIC_4/SPRINT_19/ISSUE_670_DESIGN.md`
     - `docs/planning/EPIC_4/SPRINT_19/DEFERRED_ITEMS_AUDIT.md`
     - `docs/planning/EPIC_4/SPRINT_19/INDEX_OFFSET_DESIGN_OPTIONS.md`
     - `docs/planning/EPIC_4/SPRINT_19/TABLE_PARSING_ANALYSIS.md`
     - `docs/planning/EPIC_4/SPRINT_19/ISSUE_672_ANALYSIS.md`
     - `docs/planning/EPIC_4/SPRINT_19/BASELINE_METRICS.md`
     - `docs/planning/EPIC_4/SPRINT_19/PLAN.md`
   - Run `make test` to confirm all 3294 tests pass

2. **Create SPRINT_LOG.md** (0.5-1h)
   - Create `docs/planning/EPIC_4/SPRINT_19/SPRINT_LOG.md` following the incremental documentation guide template
   - Include header with sprint metadata (dates, baseline metrics, targets)
   - Create Day 0 section with initialization notes
   - Create placeholder sections for Days 1-14
   - Include metrics tracking tables (parse rate, lexer_invalid_char, internal_error, test count)

3. **Update PLAN.md** (0.25h)
   - Mark Day 0 as complete
   - Note any deviations from expected state

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_19/SPRINT_LOG.md` initialized with Day 0 entry
- All prep deliverables confirmed present
- Test suite confirmed green (3294 tests)

**Quality Checks:**
You do NOT need to run quality checks for this day — all changes are documentation files only.

**Completion Criteria:**
- [ ] All 10 prep task deliverables exist on `main`
- [ ] All 3294 tests pass
- [ ] SPRINT_LOG.md created with Day 0 entry and metrics placeholders
- [ ] Log progress to `docs/planning/EPIC_4/SPRINT_19/SPRINT_LOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 19 Day 0: Sprint Initialization" \
                --body "Initializes Sprint 19: creates SPRINT_LOG.md, verifies all prep deliverables present, confirms test suite green." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit <PR_NUMBER> --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (full document)
- `docs/planning/EPIC_4/SPRINT_19/BASELINE_METRICS.md` (baseline numbers)
- `docs/planning/EPIC_2/SPRINT_11/incremental_documentation_guide.md` (SPRINT_LOG template)

---

## Day 1 Prompt: Setup + Quick Wins + Checkpoint 0

**Branch:** Create a new branch named `sprint19-day1-setup-quick-wins` from `main`

**Objective:** Sprint kickoff — verify baseline, update error taxonomy to reclassify 21 silently-resolved internal_error models, implement set element description support (Subcategory G) for 4 new model parses.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 93-113) — Day 1 details
- Read `docs/planning/EPIC_4/SPRINT_19/BASELINE_METRICS.md` — Current metrics to verify against
- Read `docs/planning/EPIC_4/SPRINT_19/INTERNAL_ERROR_ANALYSIS_PREP.md` — 5 new error taxonomy patterns to implement
- Read `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` — Subcategory G (set element descriptions): 4 models, grammar fix details
- Review `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` — Unknown 6.2 (grammar ambiguities: monitor during changes)

**Tasks to Complete (3-4 hours):**

1. **Verify Sprint 19 baseline** (0.5h)
   - Run `make test` — confirm all 3294 tests pass
   - Run `.venv/bin/python scripts/gamslib/run_full_test.py` — confirm metrics match BASELINE_METRICS.md
   - Record baseline in SPRINT_LOG.md

2. **Update error taxonomy** (1h)
   - Implement 5 new error classification patterns from INTERNAL_ERROR_ANALYSIS_PREP.md:
     - "no objective function" → `model_no_objective_def`
     - "circular dependency" → new validation category
     - "expects N indices" → `semantic_domain_error`
     - "not declared" → `semantic_undefined_symbol`
     - "Unsupported expression type" → `parser_invalid_expression`
   - Re-run pipeline to reclassify 21 silently-resolved models
   - Verify internal_error count drops from 24 to 3 in pipeline

3. **Implement set element description support (Subcategory G)** (1-2h)
   - Extend grammar to handle set element descriptions (text after element names)
   - See LEXER_ERROR_CATALOG.md Subcategory G for affected models and syntax patterns
   - Test on 4 affected models
   - Run regression tests: `make test`

4. **Pipeline retest** (0.5h)
   - Run pipeline on affected models
   - Update gamslib_status.json
   - Record new metrics in SPRINT_LOG.md

**Deliverables:**
- Updated error taxonomy with 5 new patterns
- gamslib_status.json with 21 models reclassified from internal_error
- Grammar updated for set element descriptions — 4 models newly parsing
- Metrics recorded in SPRINT_LOG.md

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria (Checkpoint 0):**
- [ ] All tests pass (3294+)
- [ ] Pipeline metrics match BASELINE_METRICS.md (before changes)
- [ ] internal_error count drops from 24 to 3 (reclassification)
- [ ] 4 new models parsing (set element descriptions)
- [ ] Zero regressions
- [ ] Mark Day 1 as complete in `docs/planning/EPIC_4/SPRINT_19/PLAN.md`
- [ ] Log progress to `docs/planning/EPIC_4/SPRINT_19/SPRINT_LOG.md`
  - Update after each PR merge — Add PR entry to Day 1 section
  - Update parse rate table — Add row with new parse rate
  - Document decisions immediately — Capture context while fresh
- [ ] Log to `CHANGELOG.md`
- [ ] Check off Checkpoint 0 criteria in PLAN.md

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 19 Day 1: Setup + Quick Wins + Checkpoint 0" \
                --body "Day 1: Verifies baseline, updates error taxonomy (21 models reclassified), implements set element description support (4 new parses). Checkpoint 0 complete." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit <PR_NUMBER> --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 93-113)
- `docs/planning/EPIC_4/SPRINT_19/INTERNAL_ERROR_ANALYSIS_PREP.md`
- `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` (Subcategory G)
- `docs/planning/EPIC_4/SPRINT_19/BASELINE_METRICS.md`
- `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` (Unknown 6.2)

---

## Day 2 Prompt: Put Statement Format + Reserved Word Quoting

**Branch:** Create a new branch named `sprint19-day2-put-format-reserved-words` from `main`

**Objective:** Implement put statement `:width:decimals` format support (Subcategory C, 6 models) and reserved word quoting in emit layer (ps2_f family models).

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 115-128) — Day 2 details
- Read `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` — Subcategory C (put format): 6 models, grammar design
- Read `docs/planning/EPIC_4/SPRINT_19/DEFERRED_ITEMS_AUDIT.md` — Put statement format (2.5h) and reserved word quoting (2-3h) sections
- Read `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` — Unknown 5.1 (put format design — VERIFIED), Unknown 3.1 (reserved words — VERIFIED), Unknown 3.2 (quoting contexts — VERIFIED)
- Review `src/gams/gams_grammar.lark` (lines 493-500) — Current put statement grammar
- Review `src/emit/expr_to_gams.py` — `_quote_indices()` function for reserved word quoting

**Tasks to Complete (4-5 hours):**

1. **Implement put statement `:width:decimals` format** (2-2.5h)
   - Update grammar in `src/gams/gams_grammar.lark` to support `:width:decimals` format specifiers
   - Update parser semantic handler for put statements
   - Test on 6 affected models: ps5_s_mn, ps10_s, ps10_s_mn, and others from Subcategory C
   - Also handle `put_stmt_nosemi` for stdcge if applicable
   - Run regression: `make test`

2. **Implement reserved word quoting** (2-3h)
   - Add `GAMS_RESERVED_CONSTANTS` set (`inf`, `na`, `eps`, `undf`, etc.) to emit configuration
   - Update `_quote_indices()` in `src/emit/expr_to_gams.py` to quote reserved constants when used as set elements
   - Also update `src/emit/original_symbols.py` if needed (Unknown 3.2 confirmed both locations)
   - Test on ps2_f family models: ps2_f, ps2_f_eff, ps2_f_inf, ps2_f_s, ps2_s
   - Run regression: `make test`

3. **Run regression tests** (0.5h)
   - `make typecheck && make lint && make format && make test`
   - Run pipeline on affected models
   - Verify zero regressions

**Deliverables:**
- Grammar updated for put statement format specifiers — 6 models newly parsing
- Reserved word quoting in emit layer — ps2_f family models compile correctly
- Zero regressions confirmed

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] Put statement format specifiers working — 6 models newly parsing
- [ ] Reserved word quoting working — ps2_f family compiles
- [ ] Zero regressions in test suite
- [ ] Mark Day 2 as complete in `docs/planning/EPIC_4/SPRINT_19/PLAN.md`
- [ ] Log progress to `docs/planning/EPIC_4/SPRINT_19/SPRINT_LOG.md`
  - Update after each PR merge — Add PR entry to Day 2 section
  - Update parse rate table — Add row with new parse rate
  - Document decisions immediately — Capture context while fresh
- [ ] Log to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 19 Day 2: Put Statement Format + Reserved Word Quoting" \
                --body "Day 2: Implements put format specifiers (6 new parses) and reserved word quoting (ps2_f family compiles)." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit <PR_NUMBER> --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 115-128)
- `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` (Subcategory C)
- `docs/planning/EPIC_4/SPRINT_19/DEFERRED_ITEMS_AUDIT.md` (put format + reserved words sections)
- `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` (Unknowns 3.1, 3.2, 5.1)
- `src/gams/gams_grammar.lark` (lines 493-500)
- `src/emit/expr_to_gams.py` (`_quote_indices()`)

---

## Day 3 Prompt: Special Values + Circle Model Fix

**Branch:** Create a new branch named `sprint19-day3-special-values-circle-fix` from `main`

**Objective:** Implement special values grammar subset (Subcategory E partial, 3 models) and fix circle model MCP infeasibility by capturing uniform() random values as parameters.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 130-142) — Day 3 details
- Read `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` — Subcategory E (special values): grammar-fixable subset (3 models)
- Read `docs/planning/EPIC_4/SPRINT_19/DEFERRED_ITEMS_AUDIT.md` — Circle model MCP infeasibility section
- Read `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` — Unknown 1.1 (circle model — VERIFIED: capture and hardcode random values, 1.5-2h)
- Review `data/gamslib/raw/circle.gms` — Original model with uniform() calls

**Tasks to Complete (3-4 hours):**

1. **Implement special values grammar subset (Subcategory E partial)** (2-3h)
   - Add grammar support for special value constructs identified in LEXER_ERROR_CATALOG.md Subcategory E
   - Focus on the 3 grammar-fixable models (exclude preprocessor-required and investigation-needed models)
   - Test on affected models
   - Run regression: `make test`

2. **Fix circle model MCP infeasibility** (1.5-2h)
   - Implement value capture for `uniform()` stochastic function calls
   - Replace random value generation with hardcoded parameter values (or use `execseed` for deterministic evaluation)
   - Approach confirmed in Unknown 1.1: capture values as parameters at parse time
   - Regenerate circle_mcp.gms
   - Validate circle achieves `model_optimal` with PATH solver
   - Run regression: `make test`

**Deliverables:**
- Grammar updated for special values — 3 models newly parsing
- Circle model fix — circle achieves model_optimal
- Zero regressions confirmed

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] Special values grammar working — 3 models newly parsing
- [ ] Circle model achieves model_optimal
- [ ] Zero regressions in test suite
- [ ] Mark Day 3 as complete in `docs/planning/EPIC_4/SPRINT_19/PLAN.md`
- [ ] Log progress to `docs/planning/EPIC_4/SPRINT_19/SPRINT_LOG.md`
  - Update after each PR merge — Add PR entry to Day 3 section
  - Update parse rate table — Add row with new parse rate
  - Document decisions immediately — Capture context while fresh
- [ ] Log to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 19 Day 3: Special Values Grammar + Circle Model Fix" \
                --body "Day 3: Implements special values grammar (3 new parses) and fixes circle model MCP infeasibility (captures uniform() values)." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit <PR_NUMBER> --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 130-142)
- `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` (Subcategory E)
- `docs/planning/EPIC_4/SPRINT_19/DEFERRED_ITEMS_AUDIT.md` (circle model section)
- `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` (Unknown 1.1)
- `data/gamslib/raw/circle.gms`

---

## Day 4 Prompt: ISSUE_672 — MCP Case Sensitivity Fix

**Branch:** Create a new branch named `sprint19-day4-issue672-case-sensitivity` from `main`

**Objective:** Fix ISSUE_672 (MCP pairing failures in alkyl and bearing models) by normalizing VarRef names to lowercase at parse time, eliminating the case sensitivity mismatch between CaseInsensitiveDict.keys() and equation AST nodes.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 144-159) — Day 4 details
- Read `docs/planning/EPIC_4/SPRINT_19/ISSUE_672_ANALYSIS.md` — Full root cause analysis, proposed fix, affected models
- Read `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` — Unknown 8.4 (WRONG — case sensitivity, not bounds)
- Review `src/ir/parser.py` — Where VarRef nodes are created (normalization point)
- Review `src/ad/derivative_rules.py` (line 258) — `_diff_varref` case-sensitive comparison
- Review `src/utils/case_insensitive_dict.py` (line 81) — `keys()` returns lowercase
- Review `data/gamslib/raw/alkyl.gms` and `data/gamslib/raw/bearing.gms` — Affected models

**Tasks to Complete (3-4 hours):**

1. **Implement VarRef lowercase normalization** (1h)
   - In `src/ir/parser.py`, normalize variable names to lowercase when creating VarRef nodes
   - After resolving a name as a variable: `canonical_name = name.lower(); expr = VarRef(canonical_name, idx_tuple)`
   - This makes VarRef names consistent with CaseInsensitiveDict.keys()

2. **Add unit tests for mixed-case differentiation** (0.5h)
   - Create tests verifying `differentiate_expr()` produces correct (non-zero) derivatives for mixed-case variable names
   - Test both direct VarRef matching and nested expression differentiation

3. **Regenerate alkyl/bearing MCP files** (0.5h)
   - Run pipeline on alkyl and bearing models
   - Verify stationarity equations now have non-zero constraint multiplier coefficients
   - Check that emitted variable names are lowercase (expected and functionally correct — GAMS is case-insensitive)

4. **Run full regression suite** (0.5h)
   - `make typecheck && make lint && make format && make test`
   - Verify zero regressions across all 3294+ tests
   - Pay special attention to golden file tests — emitted variable names will change case

5. **Validate alkyl + bearing solve** (1h)
   - Run PATH solver on both models
   - Verify both models compile without "unmatched equation" errors
   - Check if models achieve `model_optimal` or if remaining issues exist (e.g., convergence)
   - Document solve status

**Deliverables:**
- VarRef lowercase normalization in parser.py
- Unit tests for mixed-case differentiation
- alkyl and bearing MCP files regenerated with correct stationarity equations
- Zero regressions confirmed
- Solve status documented for alkyl and bearing

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] VarRef names normalized to lowercase at parse time
- [ ] Unit tests pass for mixed-case differentiation
- [ ] alkyl/bearing MCP files have non-zero stationarity coefficients
- [ ] Both models compile without "unmatched equation" errors
- [ ] Zero regressions in test suite
- [ ] Mark Day 4 as complete in `docs/planning/EPIC_4/SPRINT_19/PLAN.md`
- [ ] Log progress to `docs/planning/EPIC_4/SPRINT_19/SPRINT_LOG.md`
  - Update after each PR merge — Add PR entry to Day 4 section
  - Update parse rate table if applicable
  - Document decisions immediately — Capture context while fresh
- [ ] Log to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 19 Day 4: ISSUE_672 — MCP Case Sensitivity Fix" \
                --body "Day 4: Fixes ISSUE_672 by normalizing VarRef names to lowercase at parse time. Eliminates case sensitivity mismatch that produced zero derivatives for mixed-case variable names. alkyl/bearing models now have correct stationarity equations." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit <PR_NUMBER> --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 144-159)
- `docs/planning/EPIC_4/SPRINT_19/ISSUE_672_ANALYSIS.md`
- `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` (Unknown 8.4)
- `src/ir/parser.py` (VarRef creation)
- `src/ad/derivative_rules.py` (line 258, `_diff_varref`)
- `src/utils/case_insensitive_dict.py` (line 81, `keys()`)

---

## Day 5 Prompt: ISSUE_670 — Cross-Indexed Sums (Part 1)

**Branch:** Create a new branch named `sprint19-day5-issue670-cross-indexed-sums` from `main`

**Objective:** Begin implementation of ISSUE_670 fix (highest-ROI item): implement `_collect_free_indices()` utility function and begin integration into stationarity equation builder.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 161-173) — Day 5 details
- Read `docs/planning/EPIC_4/SPRINT_19/ISSUE_670_DESIGN.md` — Full fix design (Option A: Post-Replacement Free Index Analysis), test strategy, affected models
- Read `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` — Unknowns 8.1, 8.2 (VERIFIED — all 6 models share cross-indexed sum pattern)
- Review `src/kkt/stationarity.py` — `_add_indexed_jacobian_terms()` where sum wrapping occurs
- Review `data/gamslib/raw/abel.gms` — Primary test model for validation
- Review `data/gamslib/mcp/abel_mcp.gms` — Current (incorrect) MCP output showing GAMS Error 149

**Tasks to Complete (4-5 hours):**

1. **Implement `_collect_free_indices()` utility** (3-4h)
   - Walk derivative expression tree to detect all free (unbound) indices
   - Return set of indices not bound by any enclosing Sum node
   - Handle edge cases: aliased indices, nested sums, scalar expressions
   - Write comprehensive unit tests
   - Location: `src/kkt/stationarity.py` (or new utility module)

2. **Begin integration into `_add_indexed_jacobian_terms()`** (1-2h)
   - Modify sum wrapping logic to use `_collect_free_indices()` result
   - Wrap indices not in `var_domain ∪ mult_domain` in appropriate Sum nodes
   - Initial integration — full validation on Day 6

**Deliverables:**
- `_collect_free_indices()` function with unit tests
- Initial integration into stationarity builder
- All existing tests still pass

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] `_collect_free_indices()` implemented and unit tested
- [ ] Integration into `_add_indexed_jacobian_terms()` started
- [ ] All existing tests pass (zero regressions)
- [ ] Mark Day 5 as complete in `docs/planning/EPIC_4/SPRINT_19/PLAN.md`
- [ ] Log progress to `docs/planning/EPIC_4/SPRINT_19/SPRINT_LOG.md`
  - Update after each PR merge — Add PR entry to Day 5 section
  - Document decisions immediately — Capture context while fresh
- [ ] Log to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 19 Day 5: ISSUE_670 — Cross-Indexed Sums (Part 1)" \
                --body "Day 5: Implements _collect_free_indices() utility for ISSUE_670 fix and begins integration into stationarity builder. Full validation on Day 6." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit <PR_NUMBER> --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 161-173)
- `docs/planning/EPIC_4/SPRINT_19/ISSUE_670_DESIGN.md`
- `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` (Unknowns 8.1, 8.2)
- `src/kkt/stationarity.py`
- `data/gamslib/raw/abel.gms`

---

## Day 6 Prompt: ISSUE_670 — Cross-Indexed Sums (Part 2) + Checkpoint 1

**Branch:** Create a new branch named `sprint19-day6-issue670-checkpoint1` from `main`

**Objective:** Complete ISSUE_670 fix — validate on all 6 affected models. Run Checkpoint 1 evaluation.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 175-197) — Day 6 details + Checkpoint 1 criteria
- Read `docs/planning/EPIC_4/SPRINT_19/ISSUE_670_DESIGN.md` — Affected models: abel, qabel, chenery, mexss, orani, robert
- Review Day 5 PR and commits — Current state of `_collect_free_indices()` integration
- Review `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 335-343) — Checkpoint Summary

**Tasks to Complete (4-5 hours):**

1. **Complete sum wrapping integration** (2-3h)
   - Finish integration of `_collect_free_indices()` into both indexed and scalar stationarity paths
   - Handle `_add_indexed_jacobian_terms()` and `_add_scalar_jacobian_terms()` paths
   - Ensure all free indices are wrapped in Sum nodes with correct domain sets

2. **Validate on abel (primary test model)** (1h)
   - Regenerate abel_mcp.gms
   - Verify GAMS Error 149 ("Uncontrolled set") is resolved
   - Run PATH solver — check if model compiles and solves
   - Compare with original NLP solution if available

3. **Validate on remaining 5 models** (1-2h)
   - Run pipeline on qabel, chenery, mexss, orani, robert
   - Verify all 6 models compile without Error 149
   - Document solve status for each model
   - Note: robert also depends on ISSUE_399 (table parsing, Day 10) for full pipeline

4. **Checkpoint 1 Evaluation** (0.5h)
   - Run full pipeline retest
   - Evaluate against Checkpoint 1 criteria:
     - ≥13 new models parsing (from quick wins: G=4, C=6, E=3)?
     - internal_error reclassified (24 → 3)?
     - ISSUE_672 fixed (alkyl/bearing)?
     - ISSUE_670 validated on abel (at minimum)?
     - circle model_optimal?
     - path_syntax_error reduced (6 → ≤2)?
     - Zero regressions?
     - Parse rate approaching 47%+ (75/159)?
   - Document results in SPRINT_LOG.md
   - **Go/No-Go:** If ISSUE_670 not working on abel, defer fix completion to Days 7-8 and prioritize lexer grammar work

**Deliverables:**
- ISSUE_670 fix complete — all 6 models compile without Error 149
- Checkpoint 1 evaluation documented in SPRINT_LOG.md
- All models' solve status documented

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] ISSUE_670 fix validated on abel (minimum)
- [ ] All 6 affected models compile without GAMS Error 149
- [ ] Checkpoint 1 criteria evaluated and documented
- [ ] Zero regressions in test suite
- [ ] Mark Day 6 as complete in `docs/planning/EPIC_4/SPRINT_19/PLAN.md`
- [ ] Log progress to `docs/planning/EPIC_4/SPRINT_19/SPRINT_LOG.md`
  - Update after each PR merge — Add PR entry to Day 6 section
  - Update parse rate table — Add row with new parse rate
  - Document Checkpoint 1 results
  - Document decisions immediately — Capture context while fresh
- [ ] Log to `CHANGELOG.md`
- [ ] Check off Checkpoint 1 criteria in PLAN.md

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 19 Day 6: ISSUE_670 Complete + Checkpoint 1" \
                --body "Day 6: Completes ISSUE_670 fix (6 models). Checkpoint 1 evaluation: [summarize results]." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit <PR_NUMBER> --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 175-197, 335-343)
- `docs/planning/EPIC_4/SPRINT_19/ISSUE_670_DESIGN.md`
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 346-396) — Contingency C1 if ISSUE_670 overruns

---

## Day 7 Prompt: ISSUE_670 Wrap-up + House Model Investigation

**Branch:** Create a new branch named `sprint19-day7-issue670-wrapup-house` from `main`

**Objective:** Complete any remaining ISSUE_670 edge cases and begin house model MCP investigation (KKT formulation issue).

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 199-211) — Day 7 details
- Read `docs/planning/EPIC_4/SPRINT_19/DEFERRED_ITEMS_AUDIT.md` — House model MCP infeasibility section
- Read `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` — Unknown 1.2 (house model — VERIFIED: complementarity contradiction identified, 2-4h)
- Review `data/gamslib/raw/house.gms` — Original model
- Review `data/gamslib/mcp/house_mcp.gms` — Current MCP output with contradictory complementarity conditions
- Review Day 6 Checkpoint 1 results — Determine if ISSUE_670 needs more work

**Tasks to Complete (3-4 hours):**

1. **ISSUE_670 edge case cleanup** (1-2h)
   - Fix any edge cases discovered during Day 5-6 validation
   - Handle any models that compile but don't solve correctly
   - Final regression test
   - If ISSUE_670 was not complete by Day 6 (contingency C1), allocate more time here

2. **House model MCP investigation** (2-3h)
   - Analyze contradictory complementarity conditions in house_mcp.gms
   - Investigate KKT formulation: do `comp_maxw` and `comp_minw` constraints produce contradictions?
   - Determine if fix is in KKT pairing logic or variable initialization
   - Implement fix if root cause is clear (cap at 3h investigation per contingency C5)
   - Validate house model compiles and solves
   - If not resolved after 3h: document findings, defer to Sprint 20

**Deliverables:**
- ISSUE_670 fully complete — all 6 models clean
- House model investigation results documented
- House model fix implemented (or documented blockers for Sprint 20)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] ISSUE_670 fully complete (all edge cases resolved)
- [ ] House model investigated (fix implemented or blockers documented)
- [ ] Zero regressions in test suite
- [ ] Mark Day 7 as complete in `docs/planning/EPIC_4/SPRINT_19/PLAN.md`
- [ ] Log progress to `docs/planning/EPIC_4/SPRINT_19/SPRINT_LOG.md`
  - Update after each PR merge — Add PR entry to Day 7 section
  - Document house model investigation results
  - Document decisions immediately — Capture context while fresh
- [ ] Log to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 19 Day 7: ISSUE_670 Wrap-up + House Model Investigation" \
                --body "Day 7: Completes ISSUE_670 edge cases. House model: [summarize investigation results]." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit <PR_NUMBER> --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 199-211)
- `docs/planning/EPIC_4/SPRINT_19/DEFERRED_ITEMS_AUDIT.md` (house model section)
- `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` (Unknown 1.2)
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 377-383) — Contingency C5

---

## Day 8 Prompt: Tuple/Compound Set Data Grammar (Phase 2, Part 1)

**Branch:** Create a new branch named `sprint19-day8-compound-set-data` from `main`

**Objective:** Begin core grammar work for tuple/compound set data (Subcategory A) — the highest-impact but highest-risk lexer subcategory (12 models).

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 217-229) — Day 8 details
- Read `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` — Subcategory A (tuple/compound set data): 12 models, syntax patterns, grammar design considerations
- Read `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` — Unknown 6.1 (VERIFIED — syntax constructs cataloged), Unknown 6.2 (INCOMPLETE — grammar ambiguities, monitor actively)
- Review `src/gams/gams_grammar.lark` — Current grammar rules for set data and dot notation
- Review `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 384-391) — Contingency C4 (compound set ambiguities)

**Tasks to Complete (4-5 hours):**

1. **Implement dot-separated compound key syntax** (4-5h)
   - Extend grammar to handle dot-separated tuple keys in set/parameter data (e.g., `coal.east.rail`)
   - **CRITICAL:** Watch for grammar ambiguities with existing dot notation used for set membership and domain references
   - Implement incrementally — start with simplest pattern, test after each grammar change
   - Run `make test` after EVERY grammar change (never batch — per contingency C2)
   - If ambiguity errors occur: fall back to semantic disambiguation (contingency C4)

2. **Test on 2-3 representative models** (0.5h)
   - Pick 2-3 models from Subcategory A with different dot-notation patterns
   - Verify they parse correctly with new grammar
   - Check for unexpected parse changes on currently-parsing models

**Deliverables:**
- Grammar updated for dot-separated compound keys (initial implementation)
- 2-3 representative models validating
- Zero regressions (critical — grammar changes are highest risk)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**IMPORTANT:** Run `make test` after EVERY grammar change. If tests fail, immediately revert and redesign.

**Completion Criteria:**
- [ ] Compound key grammar implemented (at least initial pattern)
- [ ] 2-3 representative models parsing correctly
- [ ] Zero regressions — no currently-parsing models affected
- [ ] Mark Day 8 as complete in `docs/planning/EPIC_4/SPRINT_19/PLAN.md`
- [ ] Log progress to `docs/planning/EPIC_4/SPRINT_19/SPRINT_LOG.md`
  - Update after each PR merge — Add PR entry to Day 8 section
  - Document grammar design decisions and any ambiguity issues
  - Document decisions immediately — Capture context while fresh
- [ ] Log to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 19 Day 8: Compound Set Data Grammar (Part 1)" \
                --body "Day 8: Implements dot-separated compound key syntax for Subcategory A. [N] models now parsing. Zero regressions." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit <PR_NUMBER> --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 217-229)
- `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` (Subcategory A)
- `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` (Unknowns 6.1, 6.2)
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 360-376, 384-391) — Contingencies C2, C4
- `src/gams/gams_grammar.lark`

---

## Day 9 Prompt: Compound Set Data (Part 2) + Model/Solve Issues

**Branch:** Create a new branch named `sprint19-day9-compound-set-model-solve` from `main`

**Objective:** Complete compound set data grammar, retest cascading models (Subcategory B), and fix model/solve statement issues (Subcategory I).

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 231-244) — Day 9 details
- Read `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` — Subcategory A (completion), Subcategory B (cascading), Subcategory I (model/solve)
- Read `docs/planning/EPIC_4/SPRINT_19/INTERNAL_ERROR_ANALYSIS_PREP.md` — harker/mathopt4 model attribute access (overlaps with Subcategory I)
- Review Day 8 implementation — Current state of compound set grammar
- Review `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` — Unknown 6.2 (grammar ambiguities — active monitoring)

**Tasks to Complete (4-5 hours):**

1. **Complete compound set data grammar** (2-3h)
   - Fix remaining edge cases from Day 8
   - Test on all 12 Subcategory A models
   - Verify all parse correctly

2. **Retest cascading models (Subcategory B)** (0.5h)
   - Re-run pipeline on 15 Subcategory B models
   - These should resolve automatically when root causes (A, C, E, etc.) are fixed
   - Document which cascading models now parse (~10-12 expected)

3. **Model/solve statement issues (Subcategory I)** (2-3h)
   - Fix model attribute access issues (`.objVal`, `.modelStat`, etc.)
   - This overlaps with harker/mathopt4 from internal_error analysis (WS4)
   - Test on 5 affected models
   - Run regression: `make test`

**Deliverables:**
- Compound set data grammar complete — 12 models newly parsing
- ~10-12 cascading models resolved
- Model/solve statement issues fixed — 5 models newly parsing
- Zero regressions

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All 12 Subcategory A models parsing
- [ ] ~10-12 cascading models resolved
- [ ] 5 Subcategory I models parsing
- [ ] Zero regressions in test suite
- [ ] Mark Day 9 as complete in `docs/planning/EPIC_4/SPRINT_19/PLAN.md`
- [ ] Log progress to `docs/planning/EPIC_4/SPRINT_19/SPRINT_LOG.md`
  - Update after each PR merge — Add PR entry to Day 9 section
  - Update parse rate table — Add row with new parse rate
  - Document cascading resolution count
  - Document decisions immediately — Capture context while fresh
- [ ] Log to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 19 Day 9: Compound Set Data Complete + Model/Solve Issues" \
                --body "Day 9: Completes compound set grammar (12 models), cascading resolves (~N models), model/solve fixes (5 models)." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit <PR_NUMBER> --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 231-244)
- `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` (Subcategories A, B, I)
- `docs/planning/EPIC_4/SPRINT_19/INTERNAL_ERROR_ANALYSIS_PREP.md` (harker/mathopt4)
- `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` (Unknown 6.2)

---

## Day 10 Prompt: Table Parsing (ISSUE_392 + ISSUE_399) + Subset Verification

**Branch:** Create a new branch named `sprint19-day10-table-parsing-subset` from `main`

**Objective:** Fix table parsing issues (ISSUE_392 for like model, ISSUE_399 for robert model) using semantic disambiguation. Verify subset relationship preservation.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 246-258) — Day 10 details
- Read `docs/planning/EPIC_4/SPRINT_19/TABLE_PARSING_ANALYSIS.md` — Full root cause, Option 3 (semantic disambiguation), affected models
- Read `docs/planning/EPIC_4/SPRINT_19/DEFERRED_ITEMS_AUDIT.md` — Subset relationship preservation section
- Read `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` — Unknown 8.3 (VERIFIED — semantic fix, no grammar changes), Unknown 2.1 (WRONG — already implemented in Sprint 17)
- Review `src/ir/parser.py` — `_handle_table_block()` semantic handler
- Review `data/gamslib/raw/like.gms` — Table with continuation/description
- Review `data/gamslib/raw/robert.gms` — Table with description as header

**Tasks to Complete (3-4 hours):**

1. **Table parsing semantic disambiguation (ISSUE_392 + ISSUE_399)** (3-4h)
   - Implement Option 3 from TABLE_PARSING_ANALYSIS.md in `_handle_table_block()`
   - Detect description misparse: check if first `table_row`'s label is a STRING token
   - Extract as description and reparse remaining tokens as column headers/data rows
   - Validate on like model: 62 values, currently 93.5% data loss → 0% loss
   - Validate on robert model: 9 values, currently 55% data loss → 0% loss
   - Note: robert also needs ISSUE_670 fix (completed Days 5-7) for full pipeline
   - Run regression: `make test`

2. **Subset relationship verification** (0.5-1h)
   - Check if subset declarations are preserved in emitted MCP output
   - Per Unknown 2.1 (WRONG): subset preservation was already implemented in Sprint 17
   - Verify on 2-3 models with subset declarations
   - If working: document verification result
   - If not: implement fix (estimate 1-2h additional)

**Deliverables:**
- Table parsing fix — like and robert models have correct table data
- Subset preservation verified (or implemented if needed)
- Zero regressions

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] like model parses with 0% table data loss
- [ ] robert model parses with 0% table data loss
- [ ] Subset preservation verified or implemented
- [ ] Zero regressions in test suite
- [ ] Mark Day 10 as complete in `docs/planning/EPIC_4/SPRINT_19/PLAN.md`
- [ ] Log progress to `docs/planning/EPIC_4/SPRINT_19/SPRINT_LOG.md`
  - Update after each PR merge — Add PR entry to Day 10 section
  - Document table parsing fix results
  - Document subset verification result
  - Document decisions immediately — Capture context while fresh
- [ ] Log to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 19 Day 10: Table Parsing Fix + Subset Verification" \
                --body "Day 10: Fixes ISSUE_392/399 (table parsing semantic disambiguation). Subset preservation verified." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit <PR_NUMBER> --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 246-258)
- `docs/planning/EPIC_4/SPRINT_19/TABLE_PARSING_ANALYSIS.md`
- `docs/planning/EPIC_4/SPRINT_19/DEFERRED_ITEMS_AUDIT.md` (subset section)
- `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` (Unknowns 2.1, 8.3)
- `src/ir/parser.py` (`_handle_table_block()`)

---

## Day 11 Prompt: Declaration/Syntax Gaps + Checkpoint 2

**Branch:** Create a new branch named `sprint19-day11-declaration-gaps-checkpoint2` from `main`

**Objective:** Fix declaration/syntax gap issues (Subcategory F, 6 models) and run Checkpoint 2 — the critical go/no-go for Sprint 19 targets.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 260-280) — Day 11 details + Checkpoint 2 criteria
- Read `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` — Subcategory F (declaration/syntax gaps): 6 grammar-fixable models + 1 preprocessor-required (uimp)
- Read `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 335-343) — Checkpoint Summary
- Read `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 415-429) — Daily Metrics targets for Day 11

**Tasks to Complete (4-5 hours):**

1. **Declaration/syntax gap fixes (Subcategory F)** (4-5h)
   - Fix 6 grammar-fixable models from Subcategory F
   - Skip uimp (preprocessor-required — uses `%gams.scrdir%` compile-time variable)
   - See LEXER_ERROR_CATALOG.md for specific syntax patterns per model
   - Run regression after each grammar change: `make test`

2. **Run full pipeline retest** (1h)
   - Run `.venv/bin/python scripts/gamslib/run_full_test.py` on all 159 models
   - Capture complete metrics snapshot
   - Compare against Day 6 (Checkpoint 1) and baseline

3. **Checkpoint 2 Evaluation** (0.5h)
   - Evaluate against Checkpoint 2 criteria:
     - Parse rate ≥55% (≥87/159)?
     - lexer_invalid_char below 30?
     - internal_error below 15?
     - All FIX_ROADMAP P1-P3 complete (ISSUE_670, 392, 399)?
     - ISSUE_672 resolved?
     - circle + house solve status?
     - Zero regressions?
   - Document results in SPRINT_LOG.md
   - **Go/No-Go:** If parse rate below 50%, prioritize remaining lexer fixes over IndexOffset (Days 12-13)

**Deliverables:**
- Declaration/syntax gap fixes — 6 models newly parsing
- Full pipeline metrics snapshot
- Checkpoint 2 evaluation documented

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] 6 Subcategory F models parsing
- [ ] Full pipeline retest complete
- [ ] Checkpoint 2 criteria evaluated and documented
- [ ] Parse rate ≥55% (or documented plan for remaining work)
- [ ] lexer_invalid_char below 30 (or documented gap)
- [ ] Zero regressions in test suite
- [ ] Mark Day 11 as complete in `docs/planning/EPIC_4/SPRINT_19/PLAN.md`
- [ ] Log progress to `docs/planning/EPIC_4/SPRINT_19/SPRINT_LOG.md`
  - Update after each PR merge — Add PR entry to Day 11 section
  - Update parse rate table — Add row with Checkpoint 2 metrics
  - Document Checkpoint 2 results with go/no-go decision
  - Document decisions immediately — Capture context while fresh
- [ ] Log to `CHANGELOG.md`
- [ ] Check off Checkpoint 2 criteria in PLAN.md

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 19 Day 11: Declaration Gaps + Checkpoint 2" \
                --body "Day 11: Fixes declaration/syntax gaps (6 models). Checkpoint 2: [summarize results — parse rate, lexer count, go/no-go decision]." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit <PR_NUMBER> --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 260-280, 335-343, 415-429)
- `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` (Subcategory F)

---

## Day 12 Prompt: IndexOffset AD Integration (Part 1)

**Branch:** Create a new branch named `sprint19-day12-indexoffset-ad` from `main`

**Objective:** Extend automatic differentiation to handle IndexOffset nodes — enable lead/lag variable differentiation for dynamic optimization models.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 282-294) — Day 12 details
- Read `docs/planning/EPIC_4/SPRINT_19/INDEX_OFFSET_DESIGN_OPTIONS.md` — Full design analysis, Option B (existing IR node), remaining AD work
- Read `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` — Unknown 7.3 (VERIFIED — AD interaction design confirmed), Unknown 7.4 (VERIFIED — grammar already parses lead/lag)
- Review `src/ad/derivative_rules.py` (line 1806) — `_apply_index_substitution()` where IndexOffset extension is needed
- Review `src/ir/ast.py` — IndexOffset node definition
- Review Checkpoint 2 results — If parse rate was below 50%, this day may be reprioritized for lexer fixes instead

**Tasks to Complete (4-5 hours):**

1. **Extend `_apply_index_substitution()` for IndexOffset** (4h)
   - Modify `src/ad/derivative_rules.py` to handle IndexOffset nodes during sum-collapse differentiation
   - When a VarRef has IndexOffset indices, preserve the offset during index substitution
   - Handle both `+N` (lead) and `-N` (lag) offsets
   - Handle circular variants (`++N`, `--N`) if present in corpus
   - Ensure correct chain rule application for offset variables

2. **Unit tests for IndexOffset differentiation** (1h)
   - Create tests for differentiating expressions with lead/lag variables
   - Test `d/dx(t) [x(t+1)]` = 0 (different time index)
   - Test `d/dx(t+1) [x(t+1)]` = 1 (same time index with offset)
   - Test nested expressions with IndexOffset

**Deliverables:**
- `_apply_index_substitution()` extended for IndexOffset nodes
- Unit tests for IndexOffset differentiation
- Zero regressions

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] `_apply_index_substitution()` handles IndexOffset nodes
- [ ] Unit tests pass for IndexOffset differentiation
- [ ] Zero regressions in test suite
- [ ] Mark Day 12 as complete in `docs/planning/EPIC_4/SPRINT_19/PLAN.md`
- [ ] Log progress to `docs/planning/EPIC_4/SPRINT_19/SPRINT_LOG.md`
  - Update after each PR merge — Add PR entry to Day 12 section
  - Document IndexOffset implementation decisions
  - Document decisions immediately — Capture context while fresh
- [ ] Log to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 19 Day 12: IndexOffset AD Integration (Part 1)" \
                --body "Day 12: Extends AD differentiation to handle IndexOffset nodes for lead/lag variables." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit <PR_NUMBER> --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 282-294)
- `docs/planning/EPIC_4/SPRINT_19/INDEX_OFFSET_DESIGN_OPTIONS.md`
- `docs/planning/EPIC_4/SPRINT_19/KNOWN_UNKNOWNS.md` (Unknowns 7.3, 7.4)
- `src/ad/derivative_rules.py` (line 1806, `_apply_index_substitution()`)
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 392-396) — Contingency C6

---

## Day 13 Prompt: IndexOffset Validation + Lead/Lag Grammar

**Branch:** Create a new branch named `sprint19-day13-indexoffset-validation` from `main`

**Objective:** Validate IndexOffset end-to-end on blocked models and implement lead/lag grammar fixes (Subcategory D) if needed.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 296-309) — Day 13 details
- Read `docs/planning/EPIC_4/SPRINT_19/INDEX_OFFSET_DESIGN_OPTIONS.md` — 8 blocked models: launch, mine, sparta, tabora, ampl, otpop, robert, pak
- Read `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` — Subcategory D (lead/lag indexing): 4 models + 2 cascading
- Review Day 12 implementation — Current state of IndexOffset AD integration

**Tasks to Complete (4-5 hours):**

1. **End-to-end IndexOffset pipeline validation** (2h)
   - Run full pipeline on 8 blocked models
   - Trace `unsup_index_offset` classification through pipeline stages
   - Identify which models now advance past translate stage
   - Document solve results for each model

2. **Test 8 blocked models** (2h)
   - launch, mine, sparta, tabora — direct translate failures from `x(t+1)` syntax
   - ampl, otpop — cascading from lead/lag
   - robert — also depends on ISSUE_670 + ISSUE_399
   - pak — also has `path_solve_terminated`
   - For each model: document which stage it now reaches and any remaining errors

3. **Lead/lag indexing grammar (Subcategory D)** (1-2h)
   - If IndexOffset already handles the grammar (it should — grammar was already implemented)
   - Verify 4 Subcategory D models parse correctly
   - Test 2 cascading models
   - If additional grammar changes needed: implement and test

**Deliverables:**
- IndexOffset pipeline validation — 8 models tested, status documented
- Lead/lag grammar verified — 4 + 2 cascading models
- Zero regressions

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] 8 IndexOffset-blocked models tested through pipeline
- [ ] Models advance past translate stage (or remaining blockers documented)
- [ ] Subcategory D lead/lag models verified
- [ ] Zero regressions in test suite
- [ ] Mark Day 13 as complete in `docs/planning/EPIC_4/SPRINT_19/PLAN.md`
- [ ] Log progress to `docs/planning/EPIC_4/SPRINT_19/SPRINT_LOG.md`
  - Update after each PR merge — Add PR entry to Day 13 section
  - Document IndexOffset validation results per model
  - Document decisions immediately — Capture context while fresh
- [ ] Log to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 19 Day 13: IndexOffset Validation + Lead/Lag Grammar" \
                --body "Day 13: Validates IndexOffset end-to-end on 8 blocked models. Lead/lag grammar verified for Subcategory D." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit <PR_NUMBER> --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 296-309)
- `docs/planning/EPIC_4/SPRINT_19/INDEX_OFFSET_DESIGN_OPTIONS.md`
- `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` (Subcategory D)

---

## Day 14 Prompt: Final Pipeline Retest + Documentation + Sprint Close

**Branch:** Create a new branch named `sprint19-day14-final-retest-release` from `main`

**Objective:** Final pipeline validation, metrics comparison, documentation, and release tagging.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 311-333) — Day 14 details + Final Acceptance Criteria
- Read `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 481-490) — Success Criteria
- Read `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 415-429) — Daily Metrics targets
- Read `docs/planning/EPIC_4/SPRINT_19/BASELINE_METRICS.md` — Starting point for comparison
- Review SPRINT_LOG.md — All previous day entries and metrics

**Tasks to Complete (3-4 hours):**

1. **Full pipeline retest** (1h)
   - Run `.venv/bin/python scripts/gamslib/run_full_test.py` on all 159 models
   - Capture final gamslib_status.json
   - Extract complete metrics: parse, translate, solve, full pipeline, error categories

2. **Compare final vs baseline metrics** (0.5h)
   - Create comparison table: baseline → final for all tracked metrics
   - Calculate improvements: models fixed per category, percentage changes
   - Identify any unexpected regressions

3. **Update SPRINT_LOG.md with Day 14 metrics** (0.5h)
   - Complete Day 14 section with final metrics
   - Update metrics tracking tables
   - Write sprint retrospective summary
   - Document lessons learned

4. **Run full test suite** (0.5h)
   - `make typecheck && make lint && make format && make test`
   - Record final test count
   - Confirm zero regressions

5. **Document remaining issues for Sprint 20** (0.5h)
   - List any deferred items (from scope cuts)
   - Document remaining lexer_invalid_char models (Subcategories H, J, K)
   - Document remaining solve failures
   - Note any Unknowns 6.2/6.3 observations from grammar work

6. **Tag release** (0.5h)
   - If all acceptance criteria met: tag as v1.3.0
   - If partially met: tag as v1.2.1 with documented scope
   - Update CHANGELOG.md with release entry

**Deliverables:**
- Final gamslib_status.json with complete pipeline results
- Sprint 19 achievement summary (baseline → final comparison)
- SPRINT_LOG.md Day 14 complete with retrospective
- Sprint 20 carryover list
- Release tag (v1.3.0 or v1.2.1)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria (Final Acceptance):**
- [ ] lexer_invalid_char below 30 (from 72)
- [ ] internal_error (parse) below 15 (from 24)
- [ ] Parse rate ≥55% of valid corpus (from 38.4%)
- [ ] IndexOffset AD integration complete
- [ ] FIX_ROADMAP P1-P3 resolved (ISSUE_670, 392, 399)
- [ ] ISSUE_672 resolved
- [ ] Zero regressions — all existing tests pass
- [ ] circle and house solve status documented
- [ ] put statement models parse
- [ ] Mark Day 14 as complete in `docs/planning/EPIC_4/SPRINT_19/PLAN.md`
- [ ] Log final metrics to `docs/planning/EPIC_4/SPRINT_19/SPRINT_LOG.md`
  - Complete Day 14 section
  - Update all metrics tables with final numbers
  - Write retrospective summary
  - See `docs/planning/EPIC_2/SPRINT_11/incremental_documentation_guide.md` for templates
- [ ] Log to `CHANGELOG.md` with release entry
- [ ] Release tagged

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 19 Day 14: Final Retest + Release" \
                --body "Day 14: Final pipeline validation. Sprint 19 results: Parse [X]/159 ([Y]%), lexer_invalid_char [N], internal_error [M]. Release tagged as v[X.Y.Z]." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit <PR_NUMBER> --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_19/PLAN.md` (lines 311-333, 415-429, 481-490)
- `docs/planning/EPIC_4/SPRINT_19/BASELINE_METRICS.md`
- `docs/planning/EPIC_2/SPRINT_11/incremental_documentation_guide.md`

---

## Usage Instructions

**For each day:**

1. **Start of day:**
   - Read the full prompt for that day
   - Review all prerequisite documents
   - Checkout `main` and pull latest
   - Create the specified branch
   - Review tasks and time estimates

2. **During the day:**
   - Complete tasks in order
   - Run quality checks after each significant change
   - Track progress against time estimates
   - If blocked: consult contingency plans in PLAN.md (lines 346-396)

3. **End of day:**
   - Verify all deliverables complete
   - Run final quality checks
   - Check off completion criteria
   - Update PLAN.md, SPRINT_LOG.md, and CHANGELOG.md
   - Create PR and request Copilot review
   - Address review comments
   - Merge once approved

4. **Quality checks reminder:**
   - ALWAYS run `make typecheck`, `make lint`, `make format`, `make test` before committing code changes
   - Skip quality checks only for documentation-only commits

5. **Sprint log updates (see `docs/planning/EPIC_2/SPRINT_11/incremental_documentation_guide.md`):**
   - Update after each PR merge — Add PR entry to appropriate Day section
   - Update parse rate table — Add row when parse rate changes
   - Document decisions immediately — Capture context while fresh
   - Update metrics at end — Complete metrics tables on Day 14

---

## Notes

- Each prompt is designed to be self-contained with all necessary context
- Prerequisites ensure you have the research context from prep tasks
- Quality checks ensure code quality throughout
- Completion criteria provide clear definition of "done"
- All prompts reference specific line numbers in PLAN.md
- PR & Review workflow ensures thorough code review before merging
- Contingency plans are referenced where relevant (PLAN.md lines 346-396)
- Scope cut priorities are in PLAN.md lines 398-413

# Sprint 17 Day-by-Day Prompts

This file contains comprehensive prompts for each day of Sprint 17 (Days 0-10). Each prompt is designed to be used when starting work on that specific day.

**Sprint Goal:** Translation/Solve Improvements, Final Assessment & Release v1.1.0  
**Duration:** 10 days (42h total = 38h core + 4h contingency)  
**Release Target:** v1.1.0 on Day 10

---

## Day 0 Prompt: Sprint Setup & Verification

**Branch:** Create a new branch named `sprint17-day0-setup` from `main`

**Objective:** Verify sprint readiness, confirm baseline metrics, and set up tracking infrastructure.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md` - Full sprint schedule and targets
- Read `docs/planning/EPIC_3/SPRINT_17/PREP_PLAN.md` - All 9 prep tasks completed
- Read `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md` - 26/27 unknowns verified (96%)
- Review Sprint 16 baseline: 48/160 parse (30%), 21/48 translate (44%), 11/21 solve (52%)

**Tasks to Complete (1-2 hours):**

1. **Verify Development Environment** (0.5h)
   - Run `make typecheck && make lint && make test` to confirm clean baseline
   - Verify all dependencies are up to date
   - Confirm GAMSLib test data is available

2. **Confirm Baseline Metrics** (0.5h)
   - Run full pipeline test to verify Sprint 16 baseline numbers
   - Document any discrepancies from expected baseline
   - Create baseline snapshot for comparison

3. **Set Up Sprint Tracking** (0.5h)
   - Create `docs/planning/EPIC_3/SPRINT_17/SPRINT_LOG.md` for daily progress logging
   - Review checkpoint criteria (CP1-CP5) in SPRINT_SCHEDULE.md
   - Prepare metrics tracking spreadsheet or notes

**Deliverables:**
- Confirmed clean development environment
- Verified baseline metrics matching Sprint 16 results
- SPRINT_LOG.md created with Day 0 entry

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] Development environment verified (all quality checks pass)
- [ ] Baseline metrics confirmed: 48/160 parse, 21/48 translate, 11/21 solve
- [ ] SPRINT_LOG.md created with initial entry
- [ ] Mark Day 0 as complete in `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_17/SPRINT_LOG.md`
  - Update after each PR merge - Add PR entry to appropriate Day section
  - Document any baseline discrepancies immediately

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 17 Day 0: Sprint Setup & Verification" \
                --body "Completes Day 0 tasks from Sprint 17 SPRINT_SCHEDULE.md

   - Verified development environment
   - Confirmed baseline metrics
   - Created SPRINT_LOG.md for progress tracking" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @me
   ```
3. Wait for review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md` (lines 1-50) - Sprint goals and targets
- `docs/planning/EPIC_3/SPRINT_17/PREP_PLAN.md` - Completed prep tasks
- `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md` (lines 1-80) - Summary statistics

---

## Day 1 Prompt: Translation Quick Wins (Part 1)

**Branch:** Create a new branch named `sprint17-day1-objective-extraction` from `main`

**Objective:** Enhance AD module objective extraction to increase translation success rate.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_17/TRANSLATION_ANALYSIS.md` - Translation failure analysis
- Read `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md` Category 1 (lines 100-300) - Translation unknowns
  - Unknown 1.1: Missing AD module functions
  - Unknown 1.2: Objective extraction limitations
- Review `src/ad/gradient.py` - Current objective extraction implementation
- Review `src/ad/derivative_rules.py` - Current derivative rules

**Tasks to Complete (4 hours):**

1. **Objective Extraction Enhancement** (4h)
   - Modify `src/ad/gradient.py` `find_objective_expression()` function
   - Search any equation containing the objective variable (not just explicit objective statements)
   - Handle cases where objective is defined through intermediate equations
   - Add tests for new objective extraction patterns
   - **Expected:** +5 models translating

**Deliverables:**
- Updated `src/ad/gradient.py` with enhanced objective extraction
- New test cases in `tests/ad/test_gradient.py`
- 5 additional models translating (from 21 to 26)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] `find_objective_expression()` enhanced to search all equations
- [ ] New test cases added and passing
- [ ] At least 5 new models translating (verify with test run)
- [ ] Mark Day 1 as complete in `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_17/SPRINT_LOG.md`
  - Update after each PR merge
  - Document translation count change
- [ ] **Checkpoint CP1:** Translation count check - verify +5 models

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 17 Day 1: Objective Extraction Enhancement" \
                --body "Completes Day 1 tasks from Sprint 17 SPRINT_SCHEDULE.md

   ## Changes
   - Enhanced find_objective_expression() to search all equations
   - Added test cases for new objective extraction patterns
   
   ## Metrics
   - Translation: X/48 (was 21/48)
   - Expected: +5 models translating
   
   ## Checkpoint CP1
   - [ ] Translation count increased by at least 5 models" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @me
   ```
3. Wait for review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md` (lines 52-70) - Day 1 tasks
- `docs/planning/EPIC_3/SPRINT_17/TRANSLATION_ANALYSIS.md` - Objective extraction analysis
- `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md` (lines 100-200) - Unknown 1.1, 1.2

---

## Day 2 Prompt: Translation Quick Wins (Part 2)

**Branch:** Create a new branch named `sprint17-day2-derivative-rules` from `main`

**Objective:** Add gamma/loggamma derivative rules to enable translation of models using special functions.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_17/TRANSLATION_ANALYSIS.md` - Special function failures
- Read `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md` Unknown 1.1 (lines 100-180) - Missing AD functions
- Review `src/ad/derivative_rules.py` - Current derivative implementations
- Review scipy documentation for digamma function

**Tasks to Complete (4 hours):**

1. **gamma/loggamma Derivative Rules** (4h)
   - Add `_diff_gamma()` function to `src/ad/derivative_rules.py`
   - Implement digamma (psi) function for gamma derivative: d/dx gamma(x) = gamma(x) * psi(x)
   - Use scipy.special.digamma or implement polynomial approximation
   - Add `_diff_loggamma()`: d/dx loggamma(x) = psi(x)
   - Add comprehensive test cases
   - **Expected:** +3 models translating

**Deliverables:**
- New derivative rules in `src/ad/derivative_rules.py`
- Test cases in `tests/ad/test_derivative_rules.py`
- 3 additional models translating (cumulative: ~29/48)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] `_diff_gamma()` implemented and tested
- [ ] `_diff_loggamma()` implemented and tested
- [ ] Digamma function available (scipy or approximation)
- [ ] At least 3 new models translating
- [ ] Mark Day 2 as complete in `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_17/SPRINT_LOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 17 Day 2: Gamma/Loggamma Derivative Rules" \
                --body "Completes Day 2 tasks from Sprint 17 SPRINT_SCHEDULE.md

   ## Changes
   - Added _diff_gamma() using digamma function
   - Added _diff_loggamma() derivative rule
   - Added comprehensive test cases
   
   ## Metrics
   - Translation: X/48 (was Y/48)
   - Expected: +3 models translating" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @me
   ```
3. Wait for review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md` (lines 72-86) - Day 2 tasks
- `docs/planning/EPIC_3/SPRINT_17/TRANSLATION_ANALYSIS.md` - Special function analysis
- `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md` (lines 100-180) - Unknown 1.1

---

## Day 3 Prompt: Translation Quick Wins (Part 3)

**Branch:** Create a new branch named `sprint17-day3-smin-set-sanitization` from `main`

**Objective:** Complete translation quick wins with smin smooth approximation and set element sanitization.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_17/TRANSLATION_ANALYSIS.md` - smin and set element issues
- Read `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md` Unknowns 1.3-1.5 - Translation fixes
- Review current smin handling in AD module
- Review set element processing in translation pipeline

**Tasks to Complete (4 hours):**

1. **smin Smooth Approximation** (2h)
   - Implement LogSumExp approximation: smin(a,b) ≈ -log(exp(-a/τ) + exp(-b/τ))·τ
   - Add derivative rule for smooth smin
   - Choose appropriate smoothing parameter τ
   - Add tests for smin derivative
   - **Expected:** +1 model translating

2. **Set Element Sanitization** (2h)
   - Identify models failing due to '+' in set element names
   - Implement sanitization or allow '+' in set element names
   - Update relevant parsers/emitters
   - Add test cases
   - **Expected:** +2 models translating

**Deliverables:**
- smin smooth approximation in AD module
- Set element sanitization fix
- Translation Phase 1 complete
- Target: 32/48 translate (66.7%), up from 21/48

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] smin smooth approximation implemented
- [ ] Set element sanitization complete
- [ ] At least 3 new models translating (cumulative: ~32/48)
- [ ] Mark Day 3 as complete in `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_17/SPRINT_LOG.md`
- [ ] **Checkpoint CP2:** Translation Phase 1 complete - Target: 32/48 translate (66.7%)

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 17 Day 3: smin Approximation & Set Sanitization" \
                --body "Completes Day 3 tasks from Sprint 17 SPRINT_SCHEDULE.md

   ## Changes
   - Implemented smin smooth approximation using LogSumExp
   - Fixed set element sanitization for '+' characters
   
   ## Metrics
   - Translation: X/48 (target: 32/48 = 66.7%)
   
   ## Checkpoint CP2
   - [ ] Translation Phase 1 complete
   - [ ] Target: 32/48 translate (66.7%)" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @me
   ```
3. Wait for review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md` (lines 88-110) - Day 3 tasks
- `docs/planning/EPIC_3/SPRINT_17/TRANSLATION_ANALYSIS.md` - smin and set element analysis
- `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md` (lines 200-350) - Unknowns 1.3-1.5

---

## Day 4 Prompt: Solve Improvements (Part 1)

**Branch:** Create a new branch named `sprint17-day4-computed-parameters` from `main`

**Objective:** Fix emit_gams.py to properly emit computed parameter assignments.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_17/SOLVE_INVESTIGATION_PLAN.md` - Solve failure analysis
- Read `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md` Category 2 (lines 400-600) - Solve unknowns
  - Unknown 2.1: emit_gams.py computed parameter issues
  - Unknown 2.2: Subset relationship preservation
- Review `src/emit/original_symbols.py` lines 130-185 - Current parameter emission
- Review failing models: chem, trnsport

**Tasks to Complete (4 hours):**

1. **Emit Computed Parameter Assignments** (4h)
   - Analyze `src/emit/original_symbols.py` lines 130-185
   - Fix emission of computed parameter assignments
   - Ensure parameter values are correctly propagated to GAMS output
   - Add test cases for computed parameter emission
   - **Expected:** +2 models solving (chem, trnsport)

**Deliverables:**
- Fixed `src/emit/original_symbols.py` for computed parameters
- Test cases for parameter emission
- 2 additional models solving (from 11 to 13)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] Computed parameter emission fixed
- [ ] chem and trnsport models now solving
- [ ] Test cases added and passing
- [ ] Mark Day 4 as complete in `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_17/SPRINT_LOG.md`
  - Document solve count change

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 17 Day 4: Computed Parameter Emission Fix" \
                --body "Completes Day 4 tasks from Sprint 17 SPRINT_SCHEDULE.md

   ## Changes
   - Fixed computed parameter emission in original_symbols.py
   - Added test cases for parameter emission
   
   ## Metrics
   - Solve: X/21 (was 11/21)
   - Expected: +2 models solving (chem, trnsport)" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @me
   ```
3. Wait for review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md` (lines 112-128) - Day 4 tasks
- `docs/planning/EPIC_3/SPRINT_17/SOLVE_INVESTIGATION_PLAN.md` - Parameter emission analysis
- `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md` (lines 400-500) - Unknown 2.1

---

## Day 5 Prompt: Solve Improvements (Part 2)

**Branch:** Create a new branch named `sprint17-day5-subset-relationships` from `main`

**Objective:** Fix subset relationship preservation and investigate non-syntax failures.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_17/SOLVE_INVESTIGATION_PLAN.md` - Subset issues
- Read `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md` Unknown 2.2 - Subset preservation
- Review `src/emit/original_symbols.py` lines 63-89 - Subset handling
- Review failing models: dispatch, port

**Tasks to Complete (5 hours):**

1. **Preserve Subset Relationships** (4h)
   - Analyze `src/emit/original_symbols.py` lines 63-89
   - Fix subset relationship preservation in GAMS output
   - Ensure subset declarations maintain their parent set references
   - Add test cases
   - **Expected:** +2 models solving (dispatch, port)

2. **Investigation of Non-Syntax Failures** (1h)
   - Analyze model_infeasible case
   - Analyze path_solve_terminated case
   - Document findings for potential future fixes

**Deliverables:**
- Fixed subset relationship preservation
- Investigation report for non-syntax failures
- Target: 15/21 solve (71.4%), up from 11/21

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] Subset relationship preservation fixed
- [ ] dispatch and port models now solving
- [ ] Investigation report documented
- [ ] Mark Day 5 as complete in `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_17/SPRINT_LOG.md`
- [ ] **Checkpoint CP3:** Solve improvements verified - Target: 15/21 solve (71.4%)

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 17 Day 5: Subset Relationship Fix & Investigation" \
                --body "Completes Day 5 tasks from Sprint 17 SPRINT_SCHEDULE.md

   ## Changes
   - Fixed subset relationship preservation in original_symbols.py
   - Documented investigation of non-syntax failures
   
   ## Metrics
   - Solve: X/21 (target: 15/21 = 71.4%)
   
   ## Checkpoint CP3
   - [ ] Solve improvements verified
   - [ ] Target: 15/21 solve (71.4%)" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @me
   ```
3. Wait for review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md` (lines 130-152) - Day 5 tasks
- `docs/planning/EPIC_3/SPRINT_17/SOLVE_INVESTIGATION_PLAN.md` - Subset analysis
- `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md` (lines 500-600) - Unknown 2.2

---

## Day 6 Prompt: Parse Improvements (Part 1)

**Branch:** Create a new branch named `sprint17-day6-lexer-quick-wins` from `main`

**Objective:** Implement lexer quick wins for reserved word conflicts and display statement continuation.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_17/LEXER_IMPROVEMENT_PLAN.md` - Parse improvement plan
- Read `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md` Category 3 (lines 700-900) - Parse unknowns
  - Unknown 3.1: Reserved word conflicts
  - Unknown 3.2: Display statement handling
- Review `src/parser/lexer.py` - Current lexer implementation
- Review `src/parser/grammar.py` - Current grammar rules

**Tasks to Complete (4 hours):**

1. **Reserved Word Conflicts (`inf`/`na`)** (2h)
   - Implement context-aware lexing in data sections
   - Allow `inf` and `na` as identifiers in appropriate contexts
   - Update lexer to handle reserved word conflicts
   - Add test cases
   - **Expected:** +12 models parsing

2. **Display Statement Continuation** (2h)
   - Implement multi-line display support
   - Handle display statements that span multiple lines
   - Add test cases
   - **Expected:** +6 models parsing

**Deliverables:**
- Reserved word conflict handling in lexer
- Display statement continuation support
- ~18 additional models parsing

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] Reserved word conflicts handled (`inf`/`na`)
- [ ] Display statement continuation working
- [ ] At least 18 new models parsing
- [ ] Mark Day 6 as complete in `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_17/SPRINT_LOG.md`
  - Update parse rate table with new numbers

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 17 Day 6: Lexer Quick Wins" \
                --body "Completes Day 6 tasks from Sprint 17 SPRINT_SCHEDULE.md

   ## Changes
   - Implemented context-aware lexing for reserved words (inf/na)
   - Added display statement continuation support
   
   ## Metrics
   - Parse: X/160 (was 48/160)
   - Expected: +18 models parsing" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @me
   ```
3. Wait for review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md` (lines 154-172) - Day 6 tasks
- `docs/planning/EPIC_3/SPRINT_17/LEXER_IMPROVEMENT_PLAN.md` - Phase 1 quick wins
- `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md` (lines 700-850) - Unknowns 3.1, 3.2

---

## Day 7 Prompt: Parse Improvements (Part 2)

**Branch:** Create a new branch named `sprint17-day7-grammar-additions` from `main`

**Objective:** Add grammar rules for square bracket conditionals and solve keyword variants.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_17/LEXER_IMPROVEMENT_PLAN.md` - Grammar additions
- Read `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md` Unknowns 3.3, 3.4 - Grammar unknowns
- Review `src/parser/grammar.py` - Current grammar rules
- Review failing models for bracket and solve keyword patterns

**Tasks to Complete (4 hours):**

1. **Square Bracket Conditionals** (2h)
   - Add `"[" condition "]"` alternative to grammar
   - Handle conditional expressions in square brackets
   - Add test cases
   - **Expected:** +3 models parsing

2. **Solve Keyword Variants** (2h)
   - Handle statement boundary issues with solve keyword
   - Support solve keyword variants (solve, solves, etc.)
   - Add test cases
   - **Expected:** +5 models parsing

**Deliverables:**
- Square bracket conditional support
- Solve keyword variant handling
- Target: 74/160 parse (46.3%), up from 48/160

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] Square bracket conditionals implemented
- [ ] Solve keyword variants handled
- [ ] At least 8 new models parsing
- [ ] Mark Day 7 as complete in `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_17/SPRINT_LOG.md`
- [ ] **Checkpoint CP4:** Parse improvements verified - Target: 74/160 parse (46.3%)

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 17 Day 7: Grammar Additions" \
                --body "Completes Day 7 tasks from Sprint 17 SPRINT_SCHEDULE.md

   ## Changes
   - Added square bracket conditional support
   - Implemented solve keyword variant handling
   
   ## Metrics
   - Parse: X/160 (target: 74/160 = 46.3%)
   
   ## Checkpoint CP4
   - [ ] Parse improvements verified
   - [ ] Target: 74/160 parse (46.3%)" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @me
   ```
3. Wait for review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md` (lines 174-196) - Day 7 tasks
- `docs/planning/EPIC_3/SPRINT_17/LEXER_IMPROVEMENT_PLAN.md` - Grammar additions
- `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md` (lines 850-1000) - Unknowns 3.3, 3.4

---

## Day 8 Prompt: Parse Improvements (Part 3) + Buffer

**Branch:** Create a new branch named `sprint17-day8-additional-fixes` from `main`

**Objective:** Complete parse improvements with acronym and curly brace support; use buffer for any blockers.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_17/LEXER_IMPROVEMENT_PLAN.md` - Additional parse fixes
- Read `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md` Unknown 3.5 - Parse target breakdown
- Review acronym statement patterns in GAMSLib models
- Review curly brace expression patterns

**Tasks to Complete (4 hours):**

1. **Acronym Statement Support** (1h)
   - Add `acronym_stmt` rule to grammar
   - Handle acronym declarations
   - Add test cases
   - **Expected:** +2 models parsing

2. **Curly Brace Expressions** (1h)
   - Add `"{" expr "}"` alternative to grammar
   - Handle curly brace expressions in appropriate contexts
   - Add test cases
   - **Expected:** +1 model parsing

3. **Contingency Buffer** (2h)
   - Address any blockers from earlier days
   - Additional testing and verification
   - Fix any failing tests or edge cases
   - **Note:** Use this time flexibly based on sprint progress

**Deliverables:**
- Acronym statement support
- Curly brace expression support
- All code fixes complete
- Target: 77/160 parse (48%), up from 74/160

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] Acronym statement support implemented
- [ ] Curly brace expressions implemented
- [ ] All blockers from earlier days addressed
- [ ] All code fixes complete
- [ ] Mark Day 8 as complete in `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_17/SPRINT_LOG.md`
  - Update parse rate table with final numbers

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 17 Day 8: Additional Parse Fixes + Buffer" \
                --body "Completes Day 8 tasks from Sprint 17 SPRINT_SCHEDULE.md

   ## Changes
   - Added acronym statement support
   - Added curly brace expression support
   - Addressed any blockers from earlier days
   
   ## Metrics
   - Parse: X/160 (target: 77/160 = 48%)
   
   ## All Code Fixes Complete
   - [ ] Translation fixes (Days 1-3)
   - [ ] Solve fixes (Days 4-5)
   - [ ] Parse fixes (Days 6-8)" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @me
   ```
3. Wait for review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md` (lines 198-222) - Day 8 tasks
- `docs/planning/EPIC_3/SPRINT_17/LEXER_IMPROVEMENT_PLAN.md` - Additional fixes
- `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md` (lines 1000-1200) - Unknown 3.5

---

## Day 9 Prompt: Documentation & Pre-Release

**Branch:** Create a new branch named `sprint17-day9-documentation` from `main`

**Objective:** Complete all documentation updates and verify pre-release readiness.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_17/DOCUMENTATION_PLAN.md` - Documentation gaps and updates
- Read `docs/planning/EPIC_3/SPRINT_17/RELEASE_CHECKLIST.md` - Release checklist
- Review `CHANGELOG.md` - Current changelog entries
- Review `docs/DOCUMENTATION_INDEX.md` - Documentation structure

**Tasks to Complete (5 hours):**

1. **CHANGELOG.md Update** (0.5h)
   - Document all Sprint 17 changes
   - Add entries for translation, solve, and parse improvements
   - Include metrics improvements

2. **v1.1.0 Release Notes** (1h)
   - Create `docs/releases/v1.1.0.md`
   - Summarize all changes since v1.0.0
   - Include migration notes if any
   - Add acknowledgments

3. **Version Bump in Docs** (0.5h)
   - Update version references in documentation
   - Ensure consistency across all docs

4. **DOCUMENTATION_INDEX.md Update** (1h)
   - Refresh documentation index for v1.1.0
   - Add links to new documentation
   - Update navigation structure

5. **Pre-Release Verification** (2h)
   - Run full test suite
   - Verify metrics meet targets
   - Check documentation accuracy
   - Verify all links work

**Deliverables:**
- Updated CHANGELOG.md
- v1.1.0 release notes
- Refreshed documentation
- Pre-release verification complete

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

For documentation-only changes, verify:
- All links work
- No broken references
- Consistent formatting

**Completion Criteria:**
- [ ] CHANGELOG.md updated with all Sprint 17 changes
- [ ] v1.1.0 release notes created at `docs/releases/v1.1.0.md`
- [ ] Version references updated
- [ ] DOCUMENTATION_INDEX.md refreshed
- [ ] Full test suite passes
- [ ] Metrics meet committed targets
- [ ] Mark Day 9 as complete in `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_17/SPRINT_LOG.md`
- [ ] **Checkpoint CP5:** Pre-release verification - All quality gates pass, metrics targets met

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 17 Day 9: Documentation & Pre-Release Verification" \
                --body "Completes Day 9 tasks from Sprint 17 SPRINT_SCHEDULE.md

   ## Changes
   - Updated CHANGELOG.md
   - Created v1.1.0 release notes
   - Updated version references
   - Refreshed DOCUMENTATION_INDEX.md
   
   ## Pre-Release Verification
   - [ ] Full test suite passes
   - [ ] Metrics meet targets:
     - Parse: ≥48% (77/160)
     - Translate: ≥57% (44/77)
     - Solve: ≥71% (15/21 original)
     - Full Pipeline: ≥12% (19/160)
   
   ## Checkpoint CP5
   - [ ] All quality gates pass
   - [ ] Metrics targets met" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @me
   ```
3. Wait for review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md` (lines 224-252) - Day 9 tasks
- `docs/planning/EPIC_3/SPRINT_17/DOCUMENTATION_PLAN.md` - Documentation requirements
- `docs/planning/EPIC_3/SPRINT_17/RELEASE_CHECKLIST.md` - Release checklist

---

## Day 10 Prompt: Release Execution

**Branch:** Create a new branch named `sprint17-day10-release` from `main`

**Objective:** Execute v1.1.0 release with final verification and GitHub release publication.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_17/RELEASE_CHECKLIST.md` - Complete release checklist
- Verify Checkpoint CP5 passed (Day 9)
- Review `pyproject.toml` - Current version
- Review GitHub release process

**Tasks to Complete (4 hours):**

1. **Final Verification** (1h)
   - Run full test suite one final time
   - Capture final metrics
   - Verify all documentation is accurate

2. **Version Bump in pyproject.toml** (0.5h)
   - Update version from X.X.X to 1.1.0
   - Verify version consistency

3. **Create Release Commit** (0.5h)
   - Create commit with message "Release v1.1.0"
   - Include version bump and final changes

4. **Create Git Tag v1.1.0** (0.5h)
   - Create annotated tag: `git tag -a v1.1.0 -m "Release v1.1.0"`
   - Push tag: `git push origin v1.1.0`

5. **Create GitHub Release** (0.5h)
   - Use `gh release create v1.1.0`
   - Include release notes from `docs/releases/v1.1.0.md`
   - Mark as latest release

6. **Post-Release Verification** (1h)
   - Smoke tests on released version
   - Verify documentation is live
   - Check all release artifacts

**Deliverables:**
- v1.1.0 released
- Git tag v1.1.0 created
- GitHub release published
- Post-release verification complete

**Quality Checks:**
ALWAYS run these commands before the release:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] Final verification complete
- [ ] Version bumped to 1.1.0 in pyproject.toml
- [ ] Release commit created
- [ ] Git tag v1.1.0 created and pushed
- [ ] GitHub release published
- [ ] Post-release verification complete
- [ ] Mark Day 10 as complete in `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md`
- [ ] Log final progress to `CHANGELOG.md`
- [ ] Log final progress to `docs/planning/EPIC_3/SPRINT_17/SPRINT_LOG.md`
  - Complete all metrics tables
  - Document final Sprint 17 results

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 17 Day 10: Release v1.1.0" \
                --body "Completes Day 10 tasks from Sprint 17 SPRINT_SCHEDULE.md

   ## Release v1.1.0
   - Version bumped to 1.1.0
   - Release commit created
   - Git tag v1.1.0 ready
   
   ## Final Metrics
   - Parse: X/160 (X%)
   - Translate: X/Y (X%)
   - Solve: X/Y (X%)
   - Full Pipeline: X/160 (X%)
   
   ## Post-Merge Actions
   1. Push tag: git push origin v1.1.0
   2. Create GitHub release: gh release create v1.1.0
   3. Post-release verification" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer @me
   ```
3. Wait for review to be completed
4. Address all review comments
5. Once approved, merge the PR
6. **IMPORTANT:** After merge, execute:
   ```bash
   git push origin v1.1.0
   gh release create v1.1.0 --title "v1.1.0" --notes-file docs/releases/v1.1.0.md
   ```

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md` (lines 254-280) - Day 10 tasks
- `docs/planning/EPIC_3/SPRINT_17/RELEASE_CHECKLIST.md` - Complete release checklist
- `docs/releases/v1.1.0.md` - Release notes (created Day 9)

---

## Usage Instructions

**For each day:**

1. **Start of day:**
   - Read the full prompt for that day
   - Review all prerequisite documents
   - Create the specified branch
   - Review tasks and time estimates

2. **During the day:**
   - Complete tasks in order
   - Run quality checks after each significant change
   - Track progress against time estimates

3. **End of day:**
   - Verify all deliverables complete
   - Run final quality checks
   - Check off completion criteria
   - Update SPRINT_SCHEDULE.md, README.md, and CHANGELOG.md
   - Update SPRINT_LOG.md with progress
   - Create PR and request review
   - Address review comments
   - Merge once approved

4. **Quality checks reminder:**
   - ALWAYS run `make typecheck`, `make lint`, `make format`, `make test` before committing code changes
   - Skip quality checks only for documentation-only commits

---

## Checkpoint Summary

| Checkpoint | Day | Verification | Target |
|------------|-----|--------------|--------|
| CP1 | 1 | Translation count check | +5 models |
| CP2 | 3 | Translation Phase 1 complete | 32/48 (66.7%) |
| CP3 | 5 | Solve improvements verified | 15/21 (71.4%) |
| CP4 | 7 | Parse improvements verified | 74/160 (46.3%) |
| CP5 | 9 | Pre-release verification | All gates pass |

---

## Sprint 17 Reference Quick Links

- [SPRINT_SCHEDULE.md](../SPRINT_SCHEDULE.md) - Full schedule and targets
- [PREP_PLAN.md](../PREP_PLAN.md) - Completed prep tasks
- [KNOWN_UNKNOWNS.md](../KNOWN_UNKNOWNS.md) - Verified unknowns (26/27)
- [TRANSLATION_ANALYSIS.md](../TRANSLATION_ANALYSIS.md) - Translation fix details
- [SOLVE_INVESTIGATION_PLAN.md](../SOLVE_INVESTIGATION_PLAN.md) - Solve fix details
- [LEXER_IMPROVEMENT_PLAN.md](../LEXER_IMPROVEMENT_PLAN.md) - Parse fix details
- [DOCUMENTATION_PLAN.md](../DOCUMENTATION_PLAN.md) - Documentation requirements
- [RELEASE_CHECKLIST.md](../RELEASE_CHECKLIST.md) - Release process

---

## Notes

- Each prompt is designed to be self-contained
- Prerequisites ensure you have necessary context
- Quality checks ensure code quality throughout
- Completion criteria provide clear definition of "done"
- All prompts reference specific documents for detailed task descriptions
- PR & Review workflow ensures thorough code review before merging
- Day 0 is optional but recommended for sprint setup verification
- Contingency buffer on Day 8 can be used flexibly based on sprint progress

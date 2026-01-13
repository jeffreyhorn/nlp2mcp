# Sprint 15 Day-by-Day Prompts

This file contains comprehensive prompts for each day of Sprint 15 (Days 0-10). Each prompt is designed to be used when starting work on that specific day.

**Sprint Goal:** Build Pipeline Testing Infrastructure & Establish Initial Baseline

**Key Deliverables:**
- Enhanced parse testing with 16 error categories
- Enhanced translation testing with 12 error categories
- New solve testing with PATH solver and solution comparison
- Full pipeline orchestrator with filtering framework
- Schema v2.1.0 with solve and comparison objects
- Initial baseline metrics

**Prep Phase Complete:** All 10 prep tasks done, 26 unknowns verified

---

## Day 0 Prompt: Sprint Setup and Preparation

**Branch:** Create a new branch named `sprint15-day0-setup` from `main`

**Objective:** Set up Sprint 15 infrastructure, create sprint log, and verify all prerequisites are in place.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_15/PLAN.md` - Full sprint plan with 10-day schedule
- Read `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md` - All 26 verified unknowns
- Read `docs/planning/EPIC_3/SPRINT_15/PREP_PLAN.md` - Summary of all prep task findings
- Review Sprint 14 deliverables in `data/gamslib/` and `scripts/gamslib/`

**Tasks to Complete (1-2 hours):**

1. **Verify Sprint 14 Deliverables** (30 min)
   - Confirm `data/gamslib/gamslib_status.json` exists with 219 models
   - Confirm `data/gamslib/schema.json` v2.0.0 is valid
   - Confirm `scripts/gamslib/batch_parse.py` runs: `python scripts/gamslib/batch_parse.py --help`
   - Confirm `scripts/gamslib/batch_translate.py` runs: `python scripts/gamslib/batch_translate.py --help`
   - Confirm `scripts/gamslib/db_manager.py` runs: `python scripts/gamslib/db_manager.py --help`

2. **Verify PATH Solver** (15 min)
   - Run: `gams --version` to confirm GAMS installed
   - Verify PATH solver available (confirmed in Task 5: GAMS 51.3.0, PATH 5.2.01)

3. **Create Sprint Log** (30 min)
   - Create `docs/planning/EPIC_3/SPRINT_15/SPRINT_LOG.md`
   - Include header with sprint goal, dates, and key metrics to track
   - Add Day 0 entry with setup verification results

4. **Review Prep Task Outputs** (30 min)
   - Scan all documents in `docs/planning/EPIC_3/SPRINT_15/prep-tasks/`
   - Verify schema draft exists: `prep-tasks/schema_v2.1.0_draft.json`
   - Verify error taxonomy exists: `prep-tasks/error_taxonomy.md`
   - Note any gaps or concerns

**Deliverables:**
- `docs/planning/EPIC_3/SPRINT_15/SPRINT_LOG.md` created
- All Sprint 14 dependencies verified
- PATH solver confirmed working

**Quality Checks:**
No code changes expected on Day 0. If any Python files are modified:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Sprint 14 database (219 models) accessible
  - [ ] Sprint 14 batch scripts run without errors
  - [ ] PATH solver verified (GAMS 51.3.0, PATH 5.2.01)
  - [ ] Sprint log created with Day 0 entry
  - [ ] All prep task documents reviewed
- [ ] Mark Day 0 as complete in `docs/planning/EPIC_3/SPRINT_15/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_15/SPRINT_LOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 15 Day 0: Sprint Setup and Preparation" \
                --body "Completes Day 0 tasks from Sprint 15 PLAN.md. Verifies all Sprint 14 dependencies and creates sprint log." \
                --base main
   ```
2. Wait for review (Copilot or manual)
3. Address any review comments
4. Merge when approved

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_15/PLAN.md` (full document)
- `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md` (Resolution Summary section)
- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/path_solver_integration.md` (PATH validation)

---

## Day 1 Prompt: Schema Update and Migration

**Branch:** Create a new branch named `sprint15-day1-schema-migration` from `main`

**Objective:** Update database schema to v2.1.0 and prepare infrastructure for solve testing.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_15/PLAN.md` lines 68-97 (Day 1 details)
- Read `docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_v2.1.0_draft.json` - Draft schema
- Read `docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_extensions.md` - Schema design docs
- Review `data/gamslib/schema.json` - Current v2.0.0 schema
- Review Unknowns 4.1-4.4 in KNOWN_UNKNOWNS.md (schema design decisions)

**Tasks to Complete (5 hours):**

1. **Review schema_v2.1.0_draft.json** (0.5h)
   - Verify all new objects defined: `mcp_solve_result`, `solution_comparison_result`, `model_statistics`
   - Verify error_category enum extended (7 → 36 values)
   - Verify new enums: `solve_outcome_category`, `comparison_result_category`

2. **Create schema.json v2.1.0** (1h)
   - Copy `prep-tasks/schema_v2.1.0_draft.json` to `data/gamslib/schema.json`
   - Update version field to "2.1.0"
   - Validate schema syntax with jsonschema
   - Run: `python -c "from jsonschema import Draft7Validator; import json; Draft7Validator.check_schema(json.load(open('data/gamslib/schema.json')))"`

3. **Create schema migration script** (1.5h)
   - Create `scripts/gamslib/migrate_schema_v2.1.0.py`
   - Add new optional objects to existing models (with null/not_tested defaults)
   - Preserve all existing data
   - Include `--dry-run` and `--validate` flags
   - Follow patterns from `migrate_catalog.py`

4. **Run migration on gamslib_status.json** (0.5h)
   - Create backup first: `cp data/gamslib/gamslib_status.json data/gamslib/archive/gamslib_status_v2.0.0_backup.json`
   - Run migration: `python scripts/gamslib/migrate_schema_v2.1.0.py`
   - Update schema_version field to "2.1.0"

5. **Validate all 219 entries** (0.5h)
   - Run: `python scripts/gamslib/db_manager.py validate`
   - Ensure all entries pass validation
   - Verify backward compatibility (all Sprint 14 data intact)

6. **Update db_manager.py for new objects** (1h)
   - Add support for getting/updating `mcp_solve_result` fields
   - Add support for getting/updating `solution_comparison_result` fields
   - Test: `python scripts/gamslib/db_manager.py get trnsport --format json`
   - Add unit tests for new field access

**Deliverables:**
- `data/gamslib/schema.json` v2.1.0
- `scripts/gamslib/migrate_schema_v2.1.0.py`
- Updated `data/gamslib/gamslib_status.json` (v2.1.0)
- Updated `scripts/gamslib/db_manager.py` with new object support
- Unit tests for migration and new db_manager features

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Schema v2.1.0 validates all existing 219 entries
  - [ ] New objects (mcp_solve_result, solution_comparison_result) can be added
  - [ ] db_manager.py update works with new nested fields
  - [ ] Backup created before migration
  - [ ] All unit tests pass
- [ ] Mark Day 1 as complete in `docs/planning/EPIC_3/SPRINT_15/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_15/SPRINT_LOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 15 Day 1: Schema Update and Migration" \
                --body "Updates schema to v2.1.0 with mcp_solve_result, solution_comparison_result, and model_statistics objects. Creates migration script and updates db_manager.py." \
                --base main
   ```
2. Wait for review completion
3. Address all review comments
4. Merge when approved

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_15/PLAN.md` (lines 68-97)
- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_v2.1.0_draft.json`
- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_extensions.md`
- `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md` (Unknowns 4.1-4.4)

---

## Day 2 Prompt: Error Taxonomy Integration

**Branch:** Create a new branch named `sprint15-day2-error-taxonomy` from `main`

**Objective:** Implement error categorization functions from Task 4 taxonomy with 44 outcome categories.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_15/PLAN.md` lines 99-127 (Day 2 details)
- Read `docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md` - Full taxonomy design
- Review Unknowns 1.2, 1.5, 2.3, 3.5 in KNOWN_UNKNOWNS.md (error categories)
- Review existing error handling in `scripts/gamslib/batch_parse.py`

**Tasks to Complete (6 hours):**

1. **Create error_taxonomy.py module** (2h)
   - Create `scripts/gamslib/error_taxonomy.py`
   - Define constants for all 44 outcome categories:
     - 16 parse error categories (lexer, parser, semantic, include)
     - 12 translation error categories (diff, structure, unsupported, codegen)
     - 16 solve outcome categories (PATH status, model status, comparison)
   - Implement `categorize_parse_error(error_message: str) -> str`
   - Implement `categorize_translate_error(error_message: str) -> str`
   - Implement `categorize_solve_outcome(solver_status: int, model_status: int) -> str`
   - Use regex patterns from error_taxonomy.md

2. **Integrate parse error detection** (1h)
   - Update `batch_parse.py` to import `error_taxonomy`
   - Replace simple 6-category detection with 16-category detection
   - Map old categories to new for backward compatibility
   - Test on a few known failure cases

3. **Integrate translate error detection** (1h)
   - Update `batch_translate.py` to import `error_taxonomy`
   - Add 12-category detection for translation errors
   - Capture error messages from subprocess output
   - Test on known translation failures

4. **Add solve outcome categorization** (1h)
   - Implement helper functions for solve outcomes
   - Map SOLVER STATUS codes (1-13) to categories
   - Map MODEL STATUS codes (1-19) to categories
   - Prepare for use in test_solve.py (Day 5)

5. **Write unit tests for taxonomy** (1h)
   - Create `tests/gamslib/test_error_taxonomy.py`
   - Test each categorization function with sample error messages
   - Test edge cases (empty strings, unknown patterns)
   - Ensure at least 20 test cases covering all categories
   - Run: `pytest tests/gamslib/test_error_taxonomy.py -v`

**Deliverables:**
- `scripts/gamslib/error_taxonomy.py` with all 44 categories
- Updated `scripts/gamslib/batch_parse.py` with refined categorization
- Updated `scripts/gamslib/batch_translate.py` with error categorization
- `tests/gamslib/test_error_taxonomy.py` with 20+ test cases

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] All 44 outcome categories implemented
  - [ ] Regex patterns detect errors correctly
  - [ ] Backward compatible with Sprint 14 categories
  - [ ] Unit tests pass (20+ test cases)
- [ ] Mark Day 2 as complete in `docs/planning/EPIC_3/SPRINT_15/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_15/SPRINT_LOG.md`
- [ ] **CHECKPOINT 1:** Check off all Checkpoint 1 criteria:
  - [ ] Schema v2.1.0 validates all entries
  - [ ] 44 error categories implemented

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 15 Day 2: Error Taxonomy Integration [Checkpoint 1]" \
                --body "Implements 44-category error taxonomy from prep Task 4. Creates error_taxonomy.py module and integrates with batch scripts. Completes Checkpoint 1." \
                --base main
   ```
2. Wait for review completion
3. Address all review comments
4. Merge when approved

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_15/PLAN.md` (lines 99-127)
- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md`
- `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md` (Unknowns 1.2, 1.5, 2.3, 3.5)

---

## Day 3 Prompt: Enhance batch_parse.py

**Branch:** Create a new branch named `sprint15-day3-parse-enhancement` from `main`

**Objective:** Add filtering and refined error categorization to parse testing.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_15/PLAN.md` lines 131-162 (Day 3 details)
- Read `docs/planning/EPIC_3/SPRINT_15/prep-tasks/batch_infrastructure_assessment.md` - Reuse strategy
- Read `docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md` - Filter API
- Review Unknowns 1.1, 1.4, 5.1 in KNOWN_UNKNOWNS.md (parse infrastructure)
- Review existing `scripts/gamslib/batch_parse.py`

**Tasks to Complete (6 hours):**

1. **Add filter flags to batch_parse.py** (2h)
   - Add `--only-failing` flag: only process models with parse failure
   - Add `--error-category=CATEGORY` flag: filter by specific error category
   - Add `--type=TYPE` flag: filter by model type (LP, NLP, QCP)
   - Add `--parse-success` and `--parse-failure` flags
   - Implement filter logic (AND combination from Task 7)
   - Add conflict detection (e.g., --parse-success --parse-failure)

2. **Integrate error_taxonomy.py** (1h)
   - Import `categorize_parse_error` from error_taxonomy
   - Replace existing 6-category logic with 16-category detection
   - Ensure all error messages are captured and categorized
   - Map to refined categories in database updates

3. **Add model statistics extraction** (1h)
   - Extract variable count from IR after successful parse
   - Extract equation count from IR
   - Store in `model_statistics` object in database
   - Handle cases where IR is not available

4. **Add timing improvements** (0.5h)
   - Use `time.perf_counter()` consistently
   - Record parse time for both success and failure
   - Store timing in database with 4 decimal precision

5. **Update database with refined categories** (0.5h)
   - Update `nlp2mcp_parse.error_category` with new enum values
   - Ensure backward compatibility with Sprint 14 data
   - Test database updates: `python scripts/gamslib/db_manager.py get trnsport`

6. **Test on subset of models** (1h)
   - Run on 10-20 models with various filters
   - Test: `python scripts/gamslib/batch_parse.py --only-failing --limit 10`
   - Test: `python scripts/gamslib/batch_parse.py --type NLP --limit 10`
   - Test: `python scripts/gamslib/batch_parse.py --error-category parser_unexpected_token --limit 5`
   - Verify filter logic works correctly

**Deliverables:**
- Enhanced `scripts/gamslib/batch_parse.py` with:
  - Filter flags (--only-failing, --error-category, --type, --parse-success/failure)
  - Refined 16-category error detection
  - Model statistics extraction
  - Improved timing
- Unit tests for new filter functionality
- Database entries with refined categories

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `--only-failing` filter works correctly
  - [ ] `--error-category=syntax_error` filters by category
  - [ ] `--type=NLP` filters by model type
  - [ ] Model statistics (var_count, eq_count) recorded
  - [ ] All 16 parse error categories can be assigned
- [ ] Mark Day 3 as complete in `docs/planning/EPIC_3/SPRINT_15/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_15/SPRINT_LOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 15 Day 3: Enhance batch_parse.py" \
                --body "Adds filtering flags, refined error categorization, model statistics, and timing improvements to batch_parse.py." \
                --base main
   ```
2. Wait for review completion
3. Address all review comments
4. Merge when approved

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_15/PLAN.md` (lines 131-162)
- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/batch_infrastructure_assessment.md`
- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md`
- `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md` (Unknowns 1.1, 1.4, 5.1)

---

## Day 4 Prompt: Enhance batch_translate.py

**Branch:** Create a new branch named `sprint15-day4-translate-enhancement` from `main`

**Objective:** Add filtering and error categorization to translation testing.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_15/PLAN.md` lines 164-193 (Day 4 details)
- Read `docs/planning/EPIC_3/SPRINT_15/prep-tasks/batch_infrastructure_assessment.md` - Reuse strategy
- Read `docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md` - Filter API
- Review Unknowns 2.1-2.4 in KNOWN_UNKNOWNS.md (translation infrastructure)
- Review existing `scripts/gamslib/batch_translate.py`

**Tasks to Complete (5 hours):**

1. **Add filter flags to batch_translate.py** (1.5h)
   - Add `--parse-success` flag: only process successfully parsed models
   - Add `--translate-failure` flag: only re-run failed translations
   - Add `--translate-success` flag: only process successful translations
   - Implement filter logic consistent with batch_parse.py
   - Add `--skip-completed` flag: skip models already translated

2. **Integrate error_taxonomy.py** (1h)
   - Import `categorize_translate_error` from error_taxonomy
   - Capture translation error messages from subprocess stderr
   - Apply 12-category detection to all failures
   - Store in `nlp2mcp_translate.error_category`

3. **Add MCP file validation** (1h)
   - Implement optional `--validate` flag
   - Use GAMS `action=c` to compile-check generated MCP
   - Report syntax errors without full solve
   - Store validation result in database (optional field)

4. **Add timing improvements** (0.5h)
   - Use `time.perf_counter()` for subprocess timing
   - Record translation time accurately
   - Include subprocess overhead in timing

5. **Update database with results** (0.5h)
   - Update `nlp2mcp_translate` object with new error categories
   - Store MCP file path correctly
   - Verify: `python scripts/gamslib/db_manager.py get trnsport --format json`

6. **Run on all 34 parsed models** (0.5h)
   - Run: `python scripts/gamslib/batch_translate.py --parse-success`
   - Verify all 34 parsed models are processed
   - Check translation success rate (should match Sprint 14: 94.1%)
   - Review any new failures with refined error categories

**Deliverables:**
- Enhanced `scripts/gamslib/batch_translate.py` with:
  - Filter flags (--parse-success, --translate-failure, --skip-completed)
  - 12-category error detection
  - Optional MCP validation (--validate)
  - Improved timing
- Unit tests for new functionality
- Updated database with translation results

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `--parse-success` only processes parsed models
  - [ ] All 12 translation error categories can be assigned
  - [ ] MCP files validated (optional, via --validate flag)
  - [ ] Translation timing recorded accurately
- [ ] Mark Day 4 as complete in `docs/planning/EPIC_3/SPRINT_15/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_15/SPRINT_LOG.md`
- [ ] **CHECKPOINT 2:** Check off all Checkpoint 2 criteria:
  - [ ] Filters working in both batch scripts
  - [ ] Refined error categories applied
  - [ ] Statistics recorded

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 15 Day 4: Enhance batch_translate.py [Checkpoint 2]" \
                --body "Adds filtering flags, error categorization, MCP validation, and timing improvements to batch_translate.py. Completes Checkpoint 2." \
                --base main
   ```
2. Wait for review completion
3. Address all review comments
4. Merge when approved

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_15/PLAN.md` (lines 164-193)
- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/batch_infrastructure_assessment.md`
- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md`
- `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md` (Unknowns 2.1-2.4)

---

## Day 5 Prompt: Create test_solve.py Core

**Branch:** Create a new branch named `sprint15-day5-solve-core` from `main`

**Objective:** Build solve testing infrastructure with PATH solver integration.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_15/PLAN.md` lines 197-228 (Day 5 details)
- Read `docs/planning/EPIC_3/SPRINT_15/prep-tasks/path_solver_integration.md` - PATH integration guide
- Read `docs/planning/EPIC_3/SPRINT_15/prep-tasks/solution_comparison_research.md` - Comparison strategy
- Review Unknowns 3.6, 3.7 in KNOWN_UNKNOWNS.md (PATH solver)
- Review `scripts/gamslib/verify_convexity.py` for .lst parsing patterns

**Tasks to Complete (6 hours):**

1. **Create test_solve.py skeleton** (1h)
   - Create `scripts/gamslib/test_solve.py`
   - Set up argparse with standard flags (--model, --limit, --verbose, --dry-run)
   - Set up logging (same pattern as batch scripts)
   - Import db_manager utilities for database access
   - Add `--translate-success` filter (only solve translated models)

2. **Implement PATH solver invocation** (2h)
   - Create `solve_mcp(mcp_file: str, timeout: int = 60) -> dict` function
   - Use subprocess with timeout (default 60 seconds)
   - Command: `gams {mcp_file} lo=3 o={lst_file}`
   - Handle timeout gracefully (return solver_status=3)
   - Capture stdout/stderr for error detection
   - Return structured result dict

3. **Implement status code extraction** (1h)
   - Reuse patterns from `verify_convexity.py::parse_gams_listing()`
   - Extract SOLVER STATUS (1-13) from .lst file
   - Extract MODEL STATUS (1-19) from .lst file
   - Handle missing/malformed .lst files
   - Map status codes to solve_outcome_category

4. **Implement objective extraction** (1h)
   - Parse objective value from .lst file
   - Handle MCP case (may not have explicit OBJECTIVE VALUE line)
   - Extract from variable section if needed
   - Handle cases with no objective (feasibility problems)

5. **Add database update for solve results** (1h)
   - Update `mcp_solve_result` object in database
   - Store: status, solver_status, model_status, objective_value, solve_time_seconds
   - Store: iterations (if available), outcome_category
   - Test: `python scripts/gamslib/db_manager.py get trnsport --format json`

**Deliverables:**
- `scripts/gamslib/test_solve.py` with:
  - PATH solver invocation with 60-second timeout
  - Status code extraction (SOLVER STATUS, MODEL STATUS)
  - Objective value extraction
  - Database integration for mcp_solve_result
- Unit tests for solve functionality
- Test runs on 2-3 MCP files for validation

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Can solve MCP file with PATH solver
  - [ ] Extracts solver status and model status
  - [ ] Extracts objective value (or handles MCP case)
  - [ ] Updates database with mcp_solve_result
  - [ ] 60-second timeout implemented
- [ ] Mark Day 5 as complete in `docs/planning/EPIC_3/SPRINT_15/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_15/SPRINT_LOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 15 Day 5: Create test_solve.py Core" \
                --body "Creates test_solve.py with PATH solver invocation, status/objective extraction, and database integration." \
                --base main
   ```
2. Wait for review completion
3. Address all review comments
4. Merge when approved

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_15/PLAN.md` (lines 197-228)
- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/path_solver_integration.md`
- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/solution_comparison_research.md`
- `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md` (Unknowns 3.6, 3.7)
- `scripts/gamslib/verify_convexity.py` (parse_gams_listing function)

---

## Day 6 Prompt: Solution Comparison Implementation

**Branch:** Create a new branch named `sprint15-day6-solution-comparison` from `main`

**Objective:** Implement objective comparison with tolerance and comparison decision tree.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_15/PLAN.md` lines 230-260 (Day 6 details)
- Read `docs/planning/EPIC_3/SPRINT_15/prep-tasks/solution_comparison_research.md` - Comparison strategy
- Read `docs/planning/EPIC_3/SPRINT_15/prep-tasks/numerical_tolerance_research.md` - Tolerance values
- Review Unknowns 3.1-3.4 in KNOWN_UNKNOWNS.md (tolerance, comparison)
- Review Day 5 test_solve.py implementation

**Tasks to Complete (6 hours):**

1. **Implement tolerance comparison** (1.5h)
   - Create `objectives_match(nlp_obj, mcp_obj, rtol=1e-6, atol=1e-8) -> tuple[bool, str]`
   - Formula: `|a - b| <= atol + rtol * max(|a|, |b|)`
   - Handle edge cases:
     - objective = 0 (use atol only)
     - Very large objectives > 1e6 (rtol dominates)
     - NaN/Infinity (return False with reason)
   - Return (match_result, reason_string)

2. **Create comparison decision tree** (1.5h)
   - Implement 7-outcome decision tree from Task 3:
     1. NLP solve failed → `nlp_solve_failed`
     2. MCP solve failed → `mcp_solve_failed`
     3. Both optimal, objectives match → `objective_match`
     4. Both optimal, objectives differ → `objective_mismatch`
     5. Both infeasible → `both_infeasible`
     6. Status mismatch (one optimal, one not) → `status_mismatch`
     7. Other cases → `comparison_error`
   - Return comparison_result_category enum value

3. **Handle NLP objective retrieval** (1h)
   - Get NLP objective from `convexity_verification.objective_value` in database
   - Handle missing convexity data (skip comparison)
   - Handle infeasible NLP solutions
   - Log when NLP objective is unavailable

4. **Implement solution_comparison_result** (1h)
   - Create `solution_comparison_result` object for database
   - Store: nlp_objective, mcp_objective, absolute_difference, relative_difference
   - Store: tolerance_absolute, tolerance_relative (values used)
   - Store: objective_match, status_match, comparison_result
   - Update database via db_manager

5. **Add CLI tolerance arguments** (0.5h)
   - Add `--rtol=1e-6` argument to test_solve.py
   - Add `--atol=1e-8` argument to test_solve.py
   - Support environment variable override: NLP2MCP_RTOL, NLP2MCP_ATOL
   - Log tolerance values used

6. **Test on translated models** (0.5h)
   - Run: `python scripts/gamslib/test_solve.py --model trnsport --verbose`
   - Test on 5-10 MCP files with known objectives
   - Verify comparison results are correct
   - Check edge cases (objective near 0, large objectives)

**Deliverables:**
- Enhanced `scripts/gamslib/test_solve.py` with:
  - `objectives_match()` function with combined tolerance formula
  - Comparison decision tree (7 outcomes)
  - NLP objective retrieval from database
  - solution_comparison_result database storage
  - CLI tolerance arguments (--rtol, --atol)
- Unit tests for comparison logic (10+ test cases)

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `objectives_match()` function works correctly
  - [ ] Handles objective=0 edge case (uses atol)
  - [ ] Handles very large objectives (uses rtol)
  - [ ] Comparison result stored with tolerances used
  - [ ] Decision tree produces correct outcome categories
- [ ] Mark Day 6 as complete in `docs/planning/EPIC_3/SPRINT_15/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_15/SPRINT_LOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 15 Day 6: Solution Comparison Implementation" \
                --body "Implements solution comparison with tolerance formula (rtol=1e-6, atol=1e-8), 7-outcome decision tree, and database storage." \
                --base main
   ```
2. Wait for review completion
3. Address all review comments
4. Merge when approved

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_15/PLAN.md` (lines 230-260)
- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/solution_comparison_research.md`
- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/numerical_tolerance_research.md`
- `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md` (Unknowns 3.1-3.4)

---

## Day 7 Prompt: Solve Testing Complete

**Branch:** Create a new branch named `sprint15-day7-solve-complete` from `main`

**Objective:** Run solve testing on all translated models, handle edge cases, generate summary report.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_15/PLAN.md` lines 262-293 (Day 7 details)
- Review Day 5-6 test_solve.py implementation
- Review all 32 MCP files in `data/gamslib/mcp/`
- Review error_taxonomy.py for solve outcome categories

**Tasks to Complete (6 hours):**

1. **Add error handling for edge cases** (1.5h)
   - Handle NaN in objective values
   - Handle Infinity in objective values
   - Handle missing NLP objective (skip comparison, log warning)
   - Handle .lst file parsing failures
   - Handle GAMS compilation errors in MCP files
   - Add graceful degradation for all failure modes

2. **Add solve outcome categorization** (1h)
   - Integrate `categorize_solve_outcome()` from error_taxonomy.py
   - Apply 16 solve categories to all results
   - Store outcome_category in mcp_solve_result
   - Map PATH solver status codes correctly

3. **Run solve test on all 32 MCPs** (1h)
   - Run: `python scripts/gamslib/test_solve.py --translate-success`
   - Process all 32 translated models
   - Record results in database
   - Handle any failures gracefully

4. **Analyze results and fix issues** (1.5h)
   - Review solve success/failure distribution
   - Investigate any unexpected failures
   - Fix bugs discovered during full run
   - Re-run failed models after fixes

5. **Generate solve summary report** (0.5h)
   - Create summary statistics:
     - Solve success rate
     - Objective match rate
     - Status mismatch count
     - Error category distribution
   - Output to console and log file
   - Store summary in sprint log

6. **Update documentation** (0.5h)
   - Document test_solve.py usage in docstring
   - Add example commands to --help
   - Update SPRINT_LOG.md with Day 7 results

**Deliverables:**
- Complete `scripts/gamslib/test_solve.py` with:
  - Full edge case handling
  - 16 solve outcome categories
  - Summary report generation
- Solve results for all 32 translated models in database
- Solve summary report in SPRINT_LOG.md

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] All 32 MCP files attempted
  - [ ] Solve outcome categories assigned correctly
  - [ ] Solution comparison performed for successful solves
  - [ ] Mismatches flagged for investigation
  - [ ] Summary report generated
- [ ] Mark Day 7 as complete in `docs/planning/EPIC_3/SPRINT_15/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_15/SPRINT_LOG.md`
- [ ] **CHECKPOINT 3:** Check off all Checkpoint 3 criteria:
  - [ ] PATH solver working
  - [ ] Solution comparison functional
  - [ ] All MCPs tested

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 15 Day 7: Solve Testing Complete [Checkpoint 3]" \
                --body "Completes test_solve.py with full edge case handling, runs on all 32 MCPs, generates summary report. Completes Checkpoint 3." \
                --base main
   ```
2. Wait for review completion
3. Address all review comments
4. Merge when approved

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_15/PLAN.md` (lines 262-293)
- `scripts/gamslib/error_taxonomy.py` (solve outcome categories)
- `docs/planning/EPIC_3/SPRINT_15/SPRINT_LOG.md` (for results)

---

## Day 8 Prompt: Create run_full_test.py

**Branch:** Create a new branch named `sprint15-day8-pipeline-orchestrator` from `main`

**Objective:** Build pipeline orchestrator with filtering framework.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_15/PLAN.md` lines 297-329 (Day 8 details)
- Read `docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md` - Full filter API
- Review Unknowns 5.1-5.3 in KNOWN_UNKNOWNS.md (pipeline, filtering)
- Review batch_parse.py, batch_translate.py, test_solve.py implementations

**Tasks to Complete (6.5 hours):**

1. **Create run_full_test.py skeleton** (1h)
   - Create `scripts/gamslib/run_full_test.py`
   - Set up argparse with all 14 MVP filter arguments from Task 7:
     - Model selection: --model, --type, --limit, --random
     - Status: --parse-success/failure, --translate-success/failure, --solve-success/failure
     - Stage: --only-parse, --only-translate, --only-solve
     - Convenience: --only-failing, --skip-completed, --quick
   - Set up logging and database access

2. **Implement filter logic** (2h)
   - Create `apply_filters(models: list, args) -> list` function
   - Implement AND combination logic (all filters must match)
   - Implement conflict detection:
     - --parse-success + --parse-failure = error
     - --only-parse + --only-translate = error
   - Report filter results: "Selected X of Y models matching filters"
   - Implement --dry-run to preview without execution

3. **Implement stage orchestration** (1.5h)
   - Define pipeline stages: Parse → Translate → Solve → Compare
   - Call appropriate functions from batch_parse, batch_translate, test_solve
   - Pass model list between stages
   - Track per-stage results
   - Respect --only-* flags to run specific stages

4. **Add cascade failure handling** (1h)
   - If parse fails: mark translate, solve, compare as `not_tested`
   - If translate fails: mark solve, compare as `not_tested`
   - If solve fails: mark compare as `not_tested`
   - Store `not_tested` status in database
   - Report cascade skips in summary

5. **Add progress reporting** (0.5h)
   - Report per-stage progress: "Parse: 10/160 complete"
   - Report overall progress: "Stage 2/4: Translate"
   - Support --verbose for detailed output
   - Support --quiet for minimal output

6. **Test with subset of models** (0.5h)
   - Test: `python scripts/gamslib/run_full_test.py --model trnsport --verbose`
   - Test: `python scripts/gamslib/run_full_test.py --quick` (first 10 models)
   - Test: `python scripts/gamslib/run_full_test.py --only-parse --limit 5`
   - Verify filter and cascade logic works correctly

**Deliverables:**
- `scripts/gamslib/run_full_test.py` with:
  - 14 MVP filter arguments
  - AND filter logic with conflict detection
  - Stage orchestration (Parse → Translate → Solve → Compare)
  - Cascade failure handling
  - Progress reporting
- Unit tests for filter and orchestration logic

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `--model=trnsport` runs single model through pipeline
  - [ ] `--only-parse` runs parse stage only
  - [ ] `--only-failing` re-runs failed models
  - [ ] Filter conflicts detected and reported
  - [ ] Cascade failures mark downstream stages correctly
- [ ] Mark Day 8 as complete in `docs/planning/EPIC_3/SPRINT_15/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_15/SPRINT_LOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 15 Day 8: Create run_full_test.py" \
                --body "Creates pipeline orchestrator with 14 MVP filters, AND logic, cascade handling, and stage orchestration." \
                --base main
   ```
2. Wait for review completion
3. Address all review comments
4. Merge when approved

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_15/PLAN.md` (lines 297-329)
- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md`
- `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md` (Unknowns 5.1-5.3)

---

## Day 9 Prompt: Pipeline Integration and Summary

**Branch:** Create a new branch named `sprint15-day9-pipeline-complete` from `main`

**Objective:** Complete pipeline runner with summary statistics and run full pipeline on all models.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_15/PLAN.md` lines 331-361 (Day 9 details)
- Read `docs/planning/EPIC_3/SPRINT_15/prep-tasks/performance_measurement.md` - Statistics format
- Review Day 8 run_full_test.py implementation
- Review test_filtering_requirements.md for summary statistics design

**Tasks to Complete (6 hours):**

1. **Add summary generation** (1.5h)
   - Create `generate_summary(results: dict) -> str` function
   - Include per-stage statistics:
     - Parse: attempted, success, failure, success rate
     - Translate: attempted, success, failure, success rate
     - Solve: attempted, success, failure, success rate
     - Compare: match, mismatch, skipped
   - Include error category breakdown
   - Include timing statistics (mean, median, p90)

2. **Add output formats** (1h)
   - Implement table output (default): formatted ASCII table
   - Implement JSON output (--json): machine-readable
   - Implement quiet output (--quiet): one-line summary
   - Implement verbose output (--verbose): detailed per-model results
   - Store format preference in args

3. **Add --dry-run mode** (0.5h)
   - Implement --dry-run: show which models would be processed
   - Show filter results without executing stages
   - Report: "Would process X models through Y stages"
   - Useful for testing filter combinations

4. **Run full pipeline on all models** (1h)
   - Run: `python scripts/gamslib/run_full_test.py --verbose`
   - Process all 160 verified/likely_convex models
   - Record all results in database
   - Generate summary report

5. **Fix integration issues** (1.5h)
   - Debug any failures from full run
   - Fix filter edge cases
   - Fix cascade handling issues
   - Re-run after fixes

6. **Document run_full_test.py** (0.5h)
   - Add comprehensive docstring with usage examples
   - Add --help documentation for all arguments
   - Update SPRINT_LOG.md with full pipeline results

**Deliverables:**
- Complete `scripts/gamslib/run_full_test.py` with:
  - Summary generation (per-stage stats, error breakdown, timing)
  - Output formats (table, JSON, quiet, verbose)
  - --dry-run mode
  - Documentation
- Full pipeline run results for all 160 models
- Summary statistics in SPRINT_LOG.md

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Full pipeline runs on all 160 verified/likely_convex models
  - [ ] Summary shows parse/translate/solve/compare stats
  - [ ] --dry-run previews filter results
  - [ ] --verbose shows detailed progress
  - [ ] --json outputs machine-readable results
- [ ] Mark Day 9 as complete in `docs/planning/EPIC_3/SPRINT_15/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_15/SPRINT_LOG.md`
- [ ] **CHECKPOINT 4:** Check off all Checkpoint 4 criteria:
  - [ ] Full pipeline runs
  - [ ] Filters work
  - [ ] Cascade handling correct

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 15 Day 9: Pipeline Integration Complete [Checkpoint 4]" \
                --body "Completes run_full_test.py with summary generation, output formats, and full pipeline run on 160 models. Completes Checkpoint 4." \
                --base main
   ```
2. Wait for review completion
3. Address all review comments
4. Merge when approved

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_15/PLAN.md` (lines 331-361)
- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/performance_measurement.md`
- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md`

---

## Day 10 Prompt: Establish Baseline and Complete Sprint

**Branch:** Create a new branch named `sprint15-day10-baseline-complete` from `main`

**Objective:** Record baseline metrics and finalize all documentation. Complete Sprint 15.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_15/PLAN.md` lines 365-396 (Day 10 details)
- Read `docs/planning/EPIC_3/SPRINT_15/prep-tasks/performance_measurement.md` - Baseline format
- Review full pipeline results from Day 9
- Review all Sprint 15 deliverables

**Tasks to Complete (5 hours):**

1. **Generate baseline metrics** (1h)
   - Extract from database:
     - Parse success rate and timing stats
     - Translate success rate and timing stats
     - Solve success rate and timing stats
     - Comparison match rate
   - Calculate statistics: count, mean, median, stddev, min, max, p90, p99
   - Group by model type (LP, NLP, QCP)

2. **Create baseline_metrics.json** (1h)
   - Create `data/gamslib/baseline_metrics.json`
   - Include version info: nlp2mcp version, GAMS version, PATH version
   - Include environment: Python version, OS, date
   - Include per-stage metrics
   - Include per-type breakdown
   - Validate JSON structure

3. **Create SPRINT_BASELINE.md** (1h)
   - Create `docs/planning/EPIC_3/SPRINT_15/SPRINT_BASELINE.md`
   - Human-readable baseline documentation
   - Include executive summary
   - Include per-stage success rates
   - Include timing statistics tables
   - Include error distribution
   - Include comparison with Sprint 14 (where applicable)

4. **Update GAMSLIB_STATUS.md** (0.5h)
   - Update `data/gamslib/GAMSLIB_STATUS.md` with current status
   - Include Sprint 15 results
   - Update success rate metrics
   - Update last run date

5. **Create/update GAMSLIB_TESTING.md** (1h)
   - Create/update `docs/guides/GAMSLIB_TESTING.md`
   - Document all testing scripts:
     - batch_parse.py usage and options
     - batch_translate.py usage and options
     - test_solve.py usage and options
     - run_full_test.py usage and options
   - Include example commands
   - Include troubleshooting section

6. **Sprint retrospective preparation** (0.5h)
   - Review all deliverables against PLAN.md
   - Note what went well
   - Note what could improve
   - Prepare for SPRINT_SUMMARY.md (can be separate PR)

**Deliverables:**
- `data/gamslib/baseline_metrics.json` - Machine-readable baseline
- `docs/planning/EPIC_3/SPRINT_15/SPRINT_BASELINE.md` - Human-readable baseline
- Updated `data/gamslib/GAMSLIB_STATUS.md`
- `docs/guides/GAMSLIB_TESTING.md` - Testing guide

**Quality Checks:**
Documentation-only changes do not require quality checks. If any Python files are modified:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Baseline metrics recorded for all stages
  - [ ] Timing statistics documented (mean, median, p90)
  - [ ] Success rates documented
  - [ ] Error distribution documented
  - [ ] Testing guide complete with examples
- [ ] Mark Day 10 as complete in `docs/planning/EPIC_3/SPRINT_15/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_15/SPRINT_LOG.md`
- [ ] **CHECKPOINT 5:** Check off all Checkpoint 5 criteria:
  - [ ] Baseline recorded
  - [ ] Documentation complete
  - [ ] All tests passing
- [ ] Mark all Sprint 15 deliverables complete in PLAN.md
- [ ] Update README.md with Sprint 15 completion

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 15 Day 10: Baseline and Documentation [SPRINT COMPLETE]" \
                --body "Establishes baseline metrics, creates documentation, completes Sprint 15. All checkpoints met." \
                --base main
   ```
2. Wait for review completion
3. Address all review comments
4. Merge when approved

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_15/PLAN.md` (lines 365-396)
- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/performance_measurement.md`
- `docs/planning/EPIC_3/SPRINT_15/SPRINT_LOG.md`

---

## Usage Instructions

**For each day:**

1. **Start of day:**
   - Read the full prompt for that day
   - Review all prerequisite documents
   - Create the specified branch from `main`
   - Review tasks and time estimates

2. **During the day:**
   - Complete tasks in order
   - Run quality checks after each significant change
   - Track progress against time estimates
   - Update SPRINT_LOG.md incrementally

3. **End of day:**
   - Verify all deliverables complete
   - Run final quality checks
   - Check off completion criteria
   - Update PLAN.md, CHANGELOG.md, and SPRINT_LOG.md
   - Create PR and request review
   - Address review comments
   - Merge once approved

4. **Quality checks reminder:**
   - ALWAYS run `make typecheck`, `make lint`, `make format`, `make test` before committing code changes
   - Skip quality checks only for documentation-only commits

5. **Checkpoint days (2, 4, 7, 9, 10):**
   - Verify all checkpoint criteria are met
   - Check off checkpoint in PLAN.md
   - Include "[Checkpoint N]" in PR title

---

## Notes

- Each prompt is designed to be self-contained with all necessary context
- Prerequisites ensure you have necessary background before starting
- Quality checks ensure code quality throughout the sprint
- Completion criteria provide clear definition of "done" for each day
- All prompts reference specific line numbers in PLAN.md for detailed task descriptions
- PR & Review workflow ensures thorough code review before merging
- Checkpoint days aggregate multiple days of work into verified milestones

---

## Key Reference Documents

| Document | Purpose |
|----------|---------|
| `PLAN.md` | Day-by-day schedule, tasks, deliverables |
| `KNOWN_UNKNOWNS.md` | All 26 verified unknowns and decisions |
| `PREP_PLAN.md` | Prep task summaries and findings |
| `prep-tasks/schema_v2.1.0_draft.json` | Schema design for Day 1 |
| `prep-tasks/error_taxonomy.md` | 44 error categories for Day 2 |
| `prep-tasks/path_solver_integration.md` | PATH solver guide for Day 5 |
| `prep-tasks/solution_comparison_research.md` | Comparison strategy for Day 6 |
| `prep-tasks/numerical_tolerance_research.md` | Tolerance values for Day 6 |
| `prep-tasks/test_filtering_requirements.md` | Filter API for Days 3-4, 8 |
| `prep-tasks/performance_measurement.md` | Timing/baseline format for Day 10 |

---

*Document created: January 13, 2026*  
*Sprint 15 Duration: 10 working days (Day 0 setup + Days 1-10 execution)*

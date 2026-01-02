# Sprint 14 Day-by-Day Prompts

This file contains comprehensive prompts for each day of Sprint 14 (Days 1-10). Each prompt is designed to be used when starting work on that specific day.

**Sprint Goal:** Complete Convexity Verification & JSON Database Infrastructure

**Key Deliverables:**
1. `gamslib_status.json` - New database with nested pipeline stage tracking
2. `schema.json` - JSON Schema (Draft-07) for validation
3. `db_manager.py` - Database management script with 8 subcommands
4. Batch verification results - nlp2mcp parse status for 160 models
5. Documentation - Schema specification and workflow guides

---

## Phase 1: Schema Finalization (Days 1-2)

---

## Day 1 Prompt: Schema Review and Finalization

**Branch:** Create a new branch named `sprint14-day1-schema-finalization` from `main`

**Objective:** Finalize schema.json from the draft created in prep phase. Review all field descriptions, add migration metadata, and create test entries for validation.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_14/DRAFT_SCHEMA.json` - The draft schema created in prep Task 5
- Read `docs/planning/EPIC_3/SPRINT_14/SCHEMA_DESIGN_NOTES.md` - Design rationale and decisions
- Read `docs/research/JSON_SCHEMA_BEST_PRACTICES.md` - JSON Schema best practices (Draft-07)
- Read `docs/research/JSONSCHEMA_LIBRARY_GUIDE.md` - jsonschema library usage patterns
- Review `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` - Unknowns 2.1-2.7 (Schema Design)
- Review `docs/planning/EPIC_3/SPRINT_14/CATALOG_QUALITY_REPORT.md` - Current catalog.json structure

**Tasks to Complete (~4.5 hours):**

1. **Review DRAFT_SCHEMA.json** (1 hour)
   - Verify all field types are correct
   - Check enum values match KNOWN_UNKNOWNS.md decisions
   - Ensure nested structure follows 2-level pattern from Unknown 2.2
   - Verify `additionalProperties: false` is set everywhere

2. **Update field descriptions** (1 hour)
   - Add/update `description` for every field
   - Document valid values for enums
   - Add examples where helpful
   - Ensure consistency with SCHEMA_DESIGN_NOTES.md

3. **Add migration metadata** (0.5 hours)
   - Add `migrated_from` field to track source (catalog.json)
   - Add `migration_date` field for when migration occurred
   - Consider adding `schema_version` at model entry level if needed

4. **Create schema.json** (0.5 hours)
   - Copy finalized schema to `data/gamslib/schema.json`
   - Update `$id` field to reference final location
   - Verify file is valid JSON

5. **Validate schema syntax** (0.5 hours)
   - Run `Draft7Validator.check_schema()` on the schema
   - Fix any validation errors
   - Document validation command in code

6. **Create test entries** (0.5 hours)
   - Create minimal valid entry (only required fields)
   - Create full entry (all fields populated)
   - Create error case entry (to test validation catches errors)
   - Store in `tests/gamslib/fixtures/` or similar

**Deliverables:**
- `data/gamslib/schema.json` (finalized)
- Test entry files for validation (3 files: minimal, full, error)
- Updated DRAFT_SCHEMA.json (if changes were needed)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

Note: If only creating JSON schema files and test fixtures (no Python code changes), quality checks may be skipped. However, if you add any Python validation scripts, run all checks.

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Schema passes Draft7Validator.check_schema()
  - [ ] All 3 test entries validate correctly (minimal and full pass, error fails)
  - [ ] Field descriptions complete for all fields
  - [ ] Schema copied to `data/gamslib/schema.json`
- [ ] Mark Day 1 as complete in `docs/planning/EPIC_3/SPRINT_14/PLAN.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_14/SPRINT_LOG.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 14 Day 1: Schema Review and Finalization" \
                --body "Completes Day 1 tasks from Sprint 14 PLAN.md

   ## Changes
   - Finalized schema.json from draft
   - Added field descriptions
   - Added migration metadata fields
   - Created test entry fixtures
   
   ## Validation
   - Schema passes Draft7Validator.check_schema()
   - All test entries validate correctly" \
                --base main
   ```
2. Wait for Copilot's review to be completed
3. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_14/PLAN.md` (lines 53-75) - Day 1 tasks
- `docs/planning/EPIC_3/SPRINT_14/DRAFT_SCHEMA.json` - Draft schema
- `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` (Category 2) - Schema unknowns

---

## Day 2 Prompt: Migration Script and Database Initialization

**Branch:** Create a new branch named `sprint14-day2-migration-script` from `main`

**Objective:** Create migration script to transform catalog.json to gamslib_status.json with the new schema. Initialize the new database with all 219 models.

**Prerequisites:**
- Read `data/gamslib/schema.json` - Finalized schema from Day 1
- Read `data/gamslib/catalog.json` - Source data (219 models)
- Read `docs/planning/EPIC_3/SPRINT_14/CATALOG_QUALITY_REPORT.md` - Field mapping analysis
- Read `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` - Unknown 1.5 (Update target file)
- Review `scripts/gamslib/catalog.py` - Existing catalog dataclasses for patterns

**Tasks to Complete (~5.5 hours):**

1. **Create migrate_catalog.py** (2 hours)
   - Create `scripts/gamslib/migrate_catalog.py`
   - Follow existing script patterns (argparse, logging, main())
   - Implement load_catalog() to read catalog.json
   - Implement transform_entry() to convert each model entry
   - Implement save_database() to write gamslib_status.json
   - Add --dry-run option to preview without writing
   - Add --validate option to validate output against schema

2. **Map catalog fields to new schema** (1 hour)
   - Map all 20 catalog.json fields to new schema structure
   - Handle convexity fields → nested `convexity` object
   - Set `nlp2mcp_parse`, `nlp2mcp_translate`, `mcp_solve` to null/absent
   - Add `migrated_from: "catalog.json"` and `migration_date`
   - Document field mapping in script comments or docstrings

3. **Handle missing optional fields** (0.5 hours)
   - Set sensible defaults for new fields not in catalog.json
   - Ensure optional nested objects are absent (not null)
   - Handle edge cases (empty strings, null values in source)

4. **Test migration** (1 hour)
   - Run migration on full catalog.json
   - Validate all 219 entries against schema
   - Check for any validation errors
   - Verify no data loss (compare field counts)
   - Test --dry-run and --validate options

5. **Create initial gamslib_status.json** (0.5 hours)
   - Run migration script to generate database
   - Save to `data/gamslib/gamslib_status.json`
   - Set top-level `schema_version: "2.0.0"`
   - Verify JSON is well-formatted (indent=2)

6. **Verify migration completeness** (0.5 hours)
   - Count models in source vs destination (should be 219)
   - Compare key fields (model_id, convexity_status)
   - Document migration results in commit message

**Deliverables:**
- `scripts/gamslib/migrate_catalog.py` - Migration script
- `data/gamslib/gamslib_status.json` (v2.0.0) - Initial database
- Unit tests for migration functions (optional but recommended)

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] All 219 models migrated to gamslib_status.json
  - [ ] No data loss from catalog.json
  - [ ] Database validates against schema.json
  - [ ] migrate_catalog.py has --dry-run and --validate options
- [ ] Mark Day 2 as complete in `docs/planning/EPIC_3/SPRINT_14/PLAN.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_14/SPRINT_LOG.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 14 Day 2: Migration Script and Database Initialization" \
                --body "Completes Day 2 tasks from Sprint 14 PLAN.md

   ## Changes
   - Created migrate_catalog.py script
   - Migrated all 219 models from catalog.json to gamslib_status.json
   - New database validates against schema.json
   
   ## Migration Results
   - Source: catalog.json (219 models)
   - Destination: gamslib_status.json (219 models)
   - Schema version: 2.0.0
   - Validation: All entries pass schema validation" \
                --base main
   ```
2. Wait for Copilot's review to be completed
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_14/PLAN.md` (lines 77-99) - Day 2 tasks
- `docs/planning/EPIC_3/SPRINT_14/CATALOG_QUALITY_REPORT.md` - Source data analysis

---

## Phase 2: db_manager.py Implementation (Days 3-5)

---

## Day 3 Prompt: Core Infrastructure and Basic Subcommands

**Branch:** Create a new branch named `sprint14-day3-db-manager-core` from `main`

**Objective:** Create db_manager.py skeleton with core infrastructure (argparse, logging, database I/O) and implement init, validate, and list subcommands.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_14/DB_MANAGER_DESIGN.md` - Complete db_manager specification
- Read `data/gamslib/schema.json` - Schema for validation
- Read `data/gamslib/gamslib_status.json` - Database to manage
- Review `scripts/gamslib/download_models.py` - Pattern for argparse/logging
- Review `scripts/gamslib/verify_convexity.py` - Pattern for complex CLI
- Read `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` - Unknowns 3.1, 3.5, 3.6 (db_manager patterns)
- Read `docs/research/JSONSCHEMA_LIBRARY_GUIDE.md` - Validation patterns

**Tasks to Complete (~7.5 hours):**

1. **Create db_manager.py structure** (1 hour)
   - Create `scripts/gamslib/db_manager.py`
   - Set up argparse with subparsers for subcommands
   - Use RawDescriptionHelpFormatter with usage examples in epilog
   - Set up logging with standard format from existing scripts
   - Create main() entry point

2. **Implement database loading** (1 hour)
   - Implement `load_database(path: Path) -> dict` function
   - Implement `save_database(path: Path, data: dict)` function
   - Use atomic writes (write to temp, then rename)
   - Add error handling for missing/invalid files
   - Define DB_PATH and SCHEMA_PATH constants

3. **Implement schema validation** (1 hour)
   - Implement `validate` subcommand
   - Load schema.json and database
   - Validate all entries using Draft7Validator
   - Report validation errors with field paths
   - Exit with code 0 (valid) or 1 (invalid)

4. **Implement init subcommand** (1 hour)
   - Implement `init` subcommand
   - Option 1: Initialize empty database with schema version
   - Option 2: Initialize from migration (run migrate_catalog.py)
   - Add --force flag to overwrite existing database
   - Create backup before overwriting

5. **Implement list subcommand** (1 hour)
   - Implement `list` subcommand
   - Show all 219 models with summary info
   - Display: model_id, gamslib_type, convexity_status
   - Add --format option (table, json, count)
   - Add --limit option for pagination

6. **Add backup functionality** (0.5 hours)
   - Create `data/gamslib/archive/` directory if not exists
   - Implement `create_backup()` function
   - Backup naming: `YYYYMMDD_HHMMSS_gamslib_status.json`
   - Call backup before destructive operations (init --force)
   - Implement backup pruning (keep last 10)

7. **Write unit tests** (1 hour)
   - Create `tests/gamslib/test_db_manager.py`
   - Test load_database() and save_database()
   - Test validate subcommand (valid and invalid data)
   - Test list subcommand output formats
   - Use pytest fixtures for test data

**Deliverables:**
- `scripts/gamslib/db_manager.py` (partial - init, validate, list)
- `tests/gamslib/test_db_manager.py` - Unit tests for core functions
- `data/gamslib/archive/` directory created

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `db_manager.py validate` works and reports valid/invalid
  - [ ] `db_manager.py list` shows all 219 models
  - [ ] `db_manager.py init` creates valid database (with --force)
  - [ ] Backups created in archive/ directory before destructive ops
  - [ ] All unit tests pass
- [ ] **CHECKPOINT (Day 3):** Schema complete and validated
  - [ ] schema.json finalized and in data/gamslib/
  - [ ] gamslib_status.json created with all 219 models
  - [ ] All entries validate against schema
- [ ] Mark Day 3 as complete in `docs/planning/EPIC_3/SPRINT_14/PLAN.md`
- [ ] Check off Checkpoint 1 criteria in PLAN.md
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_14/SPRINT_LOG.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 14 Day 3: Core Infrastructure and Basic Subcommands [Checkpoint 1]" \
                --body "Completes Day 3 tasks from Sprint 14 PLAN.md

   ## Checkpoint 1: Schema Complete and Validated
   - schema.json finalized
   - gamslib_status.json with 219 models
   - All entries validate against schema
   
   ## Changes
   - Created db_manager.py with core infrastructure
   - Implemented subcommands: init, validate, list
   - Added backup functionality
   - Added unit tests
   
   ## Subcommand Status
   - [x] init - Initialize database
   - [x] validate - Validate against schema
   - [x] list - List all models
   - [ ] get - (Day 4)
   - [ ] update - (Day 4)
   - [ ] query - (Day 5)
   - [ ] export - (Day 5)
   - [ ] stats - (Day 5)" \
                --base main
   ```
2. Wait for Copilot's review to be completed
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_14/PLAN.md` (lines 105-139) - Day 3 tasks
- `docs/planning/EPIC_3/SPRINT_14/DB_MANAGER_DESIGN.md` - Full specification
- `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` (Category 3) - db_manager unknowns

---

## Day 4 Prompt: CRUD Subcommands

**Branch:** Create a new branch named `sprint14-day4-crud-subcommands` from `main`

**Objective:** Implement get and update subcommands for db_manager.py, including support for nested field updates and validation after updates.

**Prerequisites:**
- Read `scripts/gamslib/db_manager.py` - Current implementation from Day 3
- Read `docs/planning/EPIC_3/SPRINT_14/DB_MANAGER_DESIGN.md` - get and update specifications
- Read `data/gamslib/schema.json` - Schema for validation
- Read `docs/research/JSONSCHEMA_LIBRARY_GUIDE.md` - Validation patterns for updates

**Tasks to Complete (~6.5 hours):**

1. **Implement get subcommand** (1.5 hours)
   - Add `get` subcommand to argparse
   - Accept model_id as positional argument
   - Return full model entry as JSON
   - Add --format option (json, table, yaml)
   - Add --field option to get specific field only
   - Handle model not found with clear error message

2. **Implement update subcommand** (2 hours)
   - Add `update` subcommand to argparse
   - Accept model_id and field=value pairs
   - Support multiple field updates in one command
   - Create backup before updating
   - Save database after successful update
   - Handle model not found error

3. **Handle nested field updates** (1 hour)
   - Support dot notation: `nlp2mcp_parse.status`
   - Parse nested paths and navigate to target field
   - Create nested objects if they don't exist
   - Example: `update trnsport nlp2mcp_parse.status success`
   - Test with various nesting levels

4. **Add update validation** (0.5 hours)
   - Validate updated entry against schema BEFORE saving
   - If validation fails, rollback changes and report error
   - Show which field/value caused validation failure
   - Do not save invalid data

5. **Write unit tests** (1.5 hours)
   - Test get subcommand with valid model_id
   - Test get with invalid model_id (error case)
   - Test get --field for specific field extraction
   - Test update with single field
   - Test update with multiple fields
   - Test update with nested field (dot notation)
   - Test update validation failure (invalid enum value)
   - Test update rollback on validation error

**Deliverables:**
- Updated `scripts/gamslib/db_manager.py` with get and update subcommands
- Updated `tests/gamslib/test_db_manager.py` with CRUD tests

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `db_manager.py get trnsport` returns model details
  - [ ] `db_manager.py update trnsport nlp2mcp_parse.status success` works
  - [ ] Invalid updates rejected with clear error message
  - [ ] Nested field updates work correctly
  - [ ] All unit tests pass
- [ ] Mark Day 4 as complete in `docs/planning/EPIC_3/SPRINT_14/PLAN.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_14/SPRINT_LOG.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 14 Day 4: CRUD Subcommands" \
                --body "Completes Day 4 tasks from Sprint 14 PLAN.md

   ## Changes
   - Implemented get subcommand with --format and --field options
   - Implemented update subcommand with nested field support
   - Added validation before saving updates
   - Added unit tests for CRUD operations
   
   ## Subcommand Status
   - [x] init
   - [x] validate
   - [x] list
   - [x] get - NEW
   - [x] update - NEW
   - [ ] query - (Day 5)
   - [ ] export - (Day 5)
   - [ ] stats - (Day 5)" \
                --base main
   ```
2. Wait for Copilot's review to be completed
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_14/PLAN.md` (lines 141-161) - Day 4 tasks
- `docs/planning/EPIC_3/SPRINT_14/DB_MANAGER_DESIGN.md` - get/update specifications

---

## Day 5 Prompt: Query and Export Subcommands

**Branch:** Create a new branch named `sprint14-day5-query-export` from `main`

**Objective:** Complete db_manager.py with query, export, and stats subcommands. All 8 subcommands should be functional by end of day.

**Prerequisites:**
- Read `scripts/gamslib/db_manager.py` - Current implementation from Days 3-4
- Read `docs/planning/EPIC_3/SPRINT_14/DB_MANAGER_DESIGN.md` - query, export, stats specifications
- Read `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` - Unknowns 3.3, 3.4 (Query and Export)

**Tasks to Complete (~7 hours):**

1. **Implement query subcommand** (2 hours)
   - Add `query` subcommand to argparse
   - Support key-value filters: `--type LP --convexity-status verified_convex`
   - Support nested field queries: `--nlp2mcp-parse-status success`
   - Use AND logic for multiple filters
   - Return matching models

2. **Add query output formats** (1 hour)
   - Add --format option: table (default), json, count
   - Table format: show key fields in columns
   - JSON format: output full matching entries
   - Count format: just show number of matches
   - Add --limit and --offset for pagination

3. **Implement export subcommand** (1.5 hours)
   - Add `export` subcommand to argparse
   - Support --format csv and --format markdown
   - CSV: flatten nested fields with dot notation
   - Markdown: generate table for documentation
   - Add --fields option to select specific fields
   - Add --query option to filter before export

4. **Implement stats subcommand** (1 hour)
   - Add `stats` subcommand to argparse
   - Show total model count (219)
   - Show counts by gamslib_type (LP, NLP, QCP)
   - Show counts by convexity_status
   - Show counts by nlp2mcp_parse.status (if populated)
   - Show counts by nlp2mcp_translate.status (if populated)

5. **Write unit tests** (1 hour)
   - Test query with single filter
   - Test query with multiple filters (AND logic)
   - Test query with nested field filter
   - Test query output formats (table, json, count)
   - Test export CSV format
   - Test export Markdown format
   - Test stats output

6. **Integration testing** (0.5 hours)
   - Run end-to-end workflow: init → update → query → export
   - Verify all 8 subcommands work together
   - Test help messages for all subcommands
   - Verify --help works for each subcommand

**Deliverables:**
- Complete `scripts/gamslib/db_manager.py` with all 8 subcommands
- Updated `tests/gamslib/test_db_manager.py` with comprehensive tests

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `db_manager.py query --type LP` returns 57 models
  - [ ] `db_manager.py export --format csv` produces valid CSV
  - [ ] `db_manager.py stats` shows summary statistics
  - [ ] All subcommands have --help documentation
  - [ ] All 8 subcommands functional
  - [ ] All unit tests pass
- [ ] **CHECKPOINT (Day 5):** db_manager core functions working
  - [ ] All 8 subcommands functional (init, get, update, query, validate, list, export, stats)
  - [ ] Tests passing for all subcommands
- [ ] Mark Day 5 as complete in `docs/planning/EPIC_3/SPRINT_14/PLAN.md`
- [ ] Check off Checkpoint 2 criteria in PLAN.md
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_14/SPRINT_LOG.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 14 Day 5: Query and Export Subcommands [Checkpoint 2]" \
                --body "Completes Day 5 tasks from Sprint 14 PLAN.md

   ## Checkpoint 2: db_manager Core Functions Working
   - All 8 subcommands implemented and tested
   - Comprehensive test coverage
   
   ## Changes
   - Implemented query subcommand with filters and output formats
   - Implemented export subcommand (CSV, Markdown)
   - Implemented stats subcommand
   - Added integration tests
   
   ## Subcommand Status - ALL COMPLETE
   - [x] init
   - [x] validate
   - [x] list
   - [x] get
   - [x] update
   - [x] query - NEW
   - [x] export - NEW
   - [x] stats - NEW" \
                --base main
   ```
2. Wait for Copilot's review to be completed
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_14/PLAN.md` (lines 163-189) - Day 5 tasks
- `docs/planning/EPIC_3/SPRINT_14/DB_MANAGER_DESIGN.md` - query/export/stats specifications

---

## Phase 3: Batch Verification Execution (Days 6-7)

---

## Day 6 Prompt: Batch Parse Script

**Branch:** Create a new branch named `sprint14-day6-batch-parse` from `main`

**Objective:** Create batch_parse.py to run nlp2mcp parse on all 160 candidate models (verified_convex + likely_convex) and update the database with results.

**Prerequisites:**
- Read `scripts/gamslib/db_manager.py` - Database management for updates
- Read `docs/planning/EPIC_3/SPRINT_14/PARSE_RATE_BASELINE.md` - Expected parse rate (~13.3%)
- Read `docs/planning/EPIC_3/SPRINT_14/PERFORMANCE_BASELINES.md` - Timing expectations (~3 min)
- Read `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` - Unknowns 1.1-1.5 (Verification)
- Review `src/cli.py` or equivalent - How to invoke nlp2mcp parser programmatically

**Tasks to Complete (~6 hours):**

1. **Create batch_parse.py** (2 hours)
   - Create `scripts/gamslib/batch_parse.py`
   - Follow existing script patterns (argparse, logging, main())
   - Load database to get list of candidate models
   - Filter for verified_convex and likely_convex (160 models)
   - Skip license_limited models (10 models)
   - Invoke nlp2mcp parser on each model
   - Capture success/failure and error messages

2. **Integrate with db_manager** (1 hour)
   - After each parse, update database entry
   - Set `nlp2mcp_parse.status` (success, failure, partial)
   - Set `nlp2mcp_parse.parse_date` to current timestamp
   - Set `nlp2mcp_parse.nlp2mcp_version` from package
   - Set `nlp2mcp_parse.error` if parse failed
   - Use db_manager update function or direct database write

3. **Add progress reporting** (0.5 hours)
   - Log progress every 10 models
   - Show: models processed, success count, failure count
   - Show estimated time remaining
   - Final summary at end

4. **Add error categorization** (1 hour)
   - Categorize parse errors into 5 categories from Task 6:
     - syntax_error
     - no_objective
     - unsupported_function
     - domain_error
     - undefined_variable
   - Store error category in `nlp2mcp_parse.error.category`
   - Store error message in `nlp2mcp_parse.error.message`

5. **Run batch parse** (0.5 hours)
   - Execute batch_parse.py on all 160 candidate models
   - Should complete in ~3 minutes
   - Monitor for any unexpected errors
   - Save final database state

6. **Analyze results** (1 hour)
   - Generate summary report of parse results
   - Count models by parse status
   - List successful models (expected: 15-25)
   - Analyze failure categories
   - Compare to baseline from PARSE_RATE_BASELINE.md
   - Document any surprises or anomalies

**Deliverables:**
- `scripts/gamslib/batch_parse.py` - Batch parse script
- Updated `data/gamslib/gamslib_status.json` with parse results
- Parse summary report (in SPRINT_LOG.md or separate file)

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] 160 models attempted (skipped 10 license-limited)
  - [ ] Parse status recorded for each model in database
  - [ ] Error categories assigned to failures
  - [ ] ~15-25 models parse successfully (~13% rate)
  - [ ] Summary report documents results
- [ ] Mark Day 6 as complete in `docs/planning/EPIC_3/SPRINT_14/PLAN.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_14/SPRINT_LOG.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 14 Day 6: Batch Parse Script" \
                --body "Completes Day 6 tasks from Sprint 14 PLAN.md

   ## Changes
   - Created batch_parse.py script
   - Ran batch parse on 160 candidate models
   - Updated database with parse results
   - Added error categorization
   
   ## Parse Results
   - Models attempted: 160
   - Models skipped (license-limited): 10
   - Parse success: [X] models ([Y]%)
   - Parse failure: [Z] models
   
   ## Error Category Breakdown
   - syntax_error: [count]
   - no_objective: [count]
   - unsupported_function: [count]
   - domain_error: [count]
   - undefined_variable: [count]" \
                --base main
   ```
2. Wait for Copilot's review to be completed
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_14/PLAN.md` (lines 197-224) - Day 6 tasks
- `docs/planning/EPIC_3/SPRINT_14/PARSE_RATE_BASELINE.md` - Expected results
- `docs/planning/EPIC_3/SPRINT_14/PERFORMANCE_BASELINES.md` - Timing expectations

---

## Day 7 Prompt: Batch Translate and Results Integration

**Branch:** Create a new branch named `sprint14-day7-batch-translate` from `main`

**Objective:** Create batch_translate.py to run nlp2mcp translation on successfully parsed models. Generate MCP output files and create comprehensive verification report.

**Prerequisites:**
- Read `scripts/gamslib/batch_parse.py` - Batch parse script from Day 6
- Read `data/gamslib/gamslib_status.json` - Database with parse results
- Read `docs/planning/EPIC_3/SPRINT_14/KNOWN_UNKNOWNS.md` - Unknown 1.5 (Results integration)
- Review `src/cli.py` - How to invoke nlp2mcp translator

**Tasks to Complete (~5.5 hours):**

1. **Create batch_translate.py** (1.5 hours)
   - Create `scripts/gamslib/batch_translate.py`
   - Load database and filter for `nlp2mcp_parse.status == "success"`
   - Run nlp2mcp translation on each successfully parsed model
   - Generate MCP output files in `data/gamslib/mcp/`
   - Capture success/failure and error messages

2. **Run batch translate** (0.5 hours)
   - Execute batch_translate.py on ~20 successfully parsed models
   - Should complete quickly (1-2 minutes)
   - Monitor for translation errors

3. **Verify MCP output files** (1 hour)
   - Check that MCP files were generated in `data/gamslib/mcp/`
   - Verify files are valid GAMS syntax (basic check)
   - Record file paths in database: `nlp2mcp_translate.output_file`
   - Note any translation failures

4. **Update database with results** (0.5 hours)
   - Set `nlp2mcp_translate.status` (success, failure)
   - Set `nlp2mcp_translate.translate_date`
   - Set `nlp2mcp_translate.nlp2mcp_version`
   - Set `nlp2mcp_translate.output_file` for successful translations
   - Set error details for failures

5. **Generate verification report** (1 hour)
   - Create comprehensive summary of all pipeline stages
   - Show: parse success rate, translate success rate
   - List all models that made it through full pipeline
   - Identify common failure patterns
   - Compare actual results to prep phase projections

6. **Review and document results** (1 hour)
   - Analyze any unexpected results
   - Document key findings in SPRINT_LOG.md
   - Note any parser/translator improvements needed
   - Identify models for manual review

**Deliverables:**
- `scripts/gamslib/batch_translate.py` - Batch translate script
- MCP output files in `data/gamslib/mcp/` directory
- Updated `data/gamslib/gamslib_status.json` with translate results
- Verification summary report (in SPRINT_LOG.md)

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] All successfully parsed models attempted translation
  - [ ] MCP files generated for successful translations
  - [ ] Database updated with all pipeline stages
  - [ ] Summary report documents all results
- [ ] **CHECKPOINT (Day 7):** Verification batch complete
  - [ ] 160 models processed through parse
  - [ ] Results recorded in database
  - [ ] MCP files generated for successful translations
- [ ] Mark Day 7 as complete in `docs/planning/EPIC_3/SPRINT_14/PLAN.md`
- [ ] Check off Checkpoint 3 criteria in PLAN.md
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_14/SPRINT_LOG.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 14 Day 7: Batch Translate and Results Integration [Checkpoint 3]" \
                --body "Completes Day 7 tasks from Sprint 14 PLAN.md

   ## Checkpoint 3: Verification Batch Complete
   - 160 models processed through parse
   - Results recorded in gamslib_status.json
   - MCP files generated for successful translations
   
   ## Changes
   - Created batch_translate.py script
   - Generated MCP output files in data/gamslib/mcp/
   - Updated database with translation results
   - Created comprehensive verification report
   
   ## Pipeline Results Summary
   - Parse attempted: 160 models
   - Parse success: [X] models ([Y]%)
   - Translate attempted: [X] models
   - Translate success: [Z] models
   - MCP files generated: [Z] files" \
                --base main
   ```
2. Wait for Copilot's review to be completed
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_14/PLAN.md` (lines 226-255) - Day 7 tasks
- `docs/planning/EPIC_3/SPRINT_14/PARSE_RATE_BASELINE.md` - Parse expectations

---

## Phase 4: Integration and Testing (Days 8-9)

---

## Day 8 Prompt: Integration Testing and Edge Cases

**Branch:** Create a new branch named `sprint14-day8-integration-testing` from `main`

**Objective:** Test full workflow end-to-end, handle edge cases, fix any discovered issues, and ensure comprehensive test coverage.

**Prerequisites:**
- Read all scripts created so far:
  - `scripts/gamslib/migrate_catalog.py`
  - `scripts/gamslib/db_manager.py`
  - `scripts/gamslib/batch_parse.py`
  - `scripts/gamslib/batch_translate.py`
- Read `data/gamslib/gamslib_status.json` - Current database state
- Read test files: `tests/gamslib/test_db_manager.py`

**Tasks to Complete (~6 hours):**

1. **End-to-end workflow test** (1.5 hours)
   - Test complete workflow: init → parse → translate → query
   - Start with fresh database (use --force)
   - Run batch_parse.py
   - Run batch_translate.py
   - Query results with db_manager.py
   - Export results to CSV and Markdown
   - Verify all steps complete without errors

2. **Test error recovery** (1 hour)
   - Test backup and restore functionality
   - Corrupt database intentionally, verify error handling
   - Test invalid updates are rejected
   - Test recovery from interrupted batch operations
   - Ensure backups are created appropriately

3. **Test concurrent access** (0.5 hours)
   - Test multiple read operations (should work)
   - Document any write contention issues
   - Note: Full concurrent write support is deferred (Unknown 3.2)
   - Verify sequential access works correctly

4. **Fix any discovered issues** (2 hours)
   - Buffer time for bug fixes
   - Address any issues found in steps 1-3
   - Fix edge cases that weren't handled
   - Update error messages if unclear

5. **Update tests for edge cases** (1 hour)
   - Add tests for discovered edge cases
   - Ensure error paths are tested
   - Add regression tests for fixed bugs
   - Verify test coverage is comprehensive

**Deliverables:**
- All edge cases handled in code
- Bug fixes implemented
- Updated test suite with edge case coverage
- Test coverage report (if tools available)

**Quality Checks:**
ALWAYS run these commands before any commit or push:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Full workflow completes without errors
  - [ ] Error recovery works correctly
  - [ ] All tests pass (including new edge case tests)
  - [ ] No critical bugs remaining
- [ ] Mark Day 8 as complete in `docs/planning/EPIC_3/SPRINT_14/PLAN.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_14/SPRINT_LOG.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 14 Day 8: Integration Testing and Edge Cases" \
                --body "Completes Day 8 tasks from Sprint 14 PLAN.md

   ## Changes
   - Completed end-to-end workflow testing
   - Fixed [X] bugs discovered during testing
   - Added [Y] edge case tests
   - Improved error handling
   
   ## Test Coverage
   - All scripts tested end-to-end
   - Error recovery verified
   - Edge cases covered
   
   ## Bugs Fixed
   - [List any bugs fixed]" \
                --base main
   ```
2. Wait for Copilot's review to be completed
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_14/PLAN.md` (lines 263-285) - Day 8 tasks

---

## Day 9 Prompt: Documentation and Schema Documentation

**Branch:** Create a new branch named `sprint14-day9-documentation` from `main`

**Objective:** Complete all documentation including schema specification, db_manager usage guide, and workflow documentation.

**Prerequisites:**
- Read all scripts for accurate documentation:
  - `scripts/gamslib/db_manager.py`
  - `scripts/gamslib/batch_parse.py`
  - `scripts/gamslib/batch_translate.py`
- Read `data/gamslib/schema.json` - Schema to document
- Read `docs/planning/EPIC_3/SPRINT_14/SCHEMA_DESIGN_NOTES.md` - Design rationale

**Tasks to Complete (~5.5 hours):**

1. **Create GAMSLIB_DATABASE_SCHEMA.md** (2 hours)
   - Create `docs/infrastructure/GAMSLIB_DATABASE_SCHEMA.md`
   - Document schema version (2.0.0) and Draft-07
   - Document all top-level fields
   - Document each nested object (convexity, nlp2mcp_parse, etc.)
   - Document all enum values with meanings
   - Include example valid entries
   - Document field requirements (required vs optional)

2. **Document db_manager usage** (1 hour)
   - Ensure all subcommands have comprehensive --help
   - Add usage examples to script epilog
   - Document common workflows
   - Document error messages and troubleshooting

3. **Update existing docs** (1 hour)
   - Update any references to catalog.json to mention gamslib_status.json
   - Update PROJECT_PLAN.md if needed
   - Update README.md if there are GAMSLIB references
   - Ensure consistent terminology across docs

4. **Create workflow guide** (1 hour)
   - Document standard workflow: init → batch_parse → batch_translate → query/export
   - Document how to add new pipeline stages
   - Document backup and recovery procedures
   - Document schema migration process

5. **Review and polish** (0.5 hours)
   - Proofread all new documentation
   - Check for broken links
   - Verify code examples work
   - Ensure consistency with SCHEMA_DESIGN_NOTES.md

**Deliverables:**
- `docs/infrastructure/GAMSLIB_DATABASE_SCHEMA.md` - Schema specification
- Updated db_manager.py with comprehensive --help
- Workflow guide (can be section in GAMSLIB_DATABASE_SCHEMA.md)

**Quality Checks:**
This is primarily a documentation day. Quality checks are optional unless Python code was modified (e.g., --help text updates):
1. `make typecheck` - If Python modified
2. `make lint` - If Python modified
3. `make format` - If Python modified
4. `make test` - If Python modified

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Schema fully documented in GAMSLIB_DATABASE_SCHEMA.md
  - [ ] All fields described with valid values
  - [ ] Usage examples for all db_manager subcommands
  - [ ] Workflow guide complete
- [ ] Mark Day 9 as complete in `docs/planning/EPIC_3/SPRINT_14/PLAN.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_14/SPRINT_LOG.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 14 Day 9: Documentation and Schema Documentation" \
                --body "Completes Day 9 tasks from Sprint 14 PLAN.md

   ## Changes
   - Created GAMSLIB_DATABASE_SCHEMA.md with full schema documentation
   - Updated db_manager.py --help documentation
   - Created workflow guide
   - Updated related documentation
   
   ## Documentation Added
   - docs/infrastructure/GAMSLIB_DATABASE_SCHEMA.md
   - Workflow guide for batch operations
   - Comprehensive --help for all subcommands" \
                --base main
   ```
2. Wait for Copilot's review to be completed
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_14/PLAN.md` (lines 287-310) - Day 9 tasks
- `docs/planning/EPIC_3/SPRINT_14/SCHEMA_DESIGN_NOTES.md` - Design rationale

---

## Phase 5: Review and Finalization (Day 10)

---

## Day 10 Prompt: Final Review and Sprint Completion

**Branch:** Create a new branch named `sprint14-day10-finalization` from `main`

**Objective:** Complete final validation, cleanup, create sprint summary, and merge all deliverables to main.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_14/PLAN.md` - All acceptance criteria
- Read `docs/planning/EPIC_3/PROJECT_PLAN.md` (lines 92-223) - Sprint 14 deliverables
- Review all created files and scripts
- Review `docs/planning/EPIC_3/SPRINT_14/SPRINT_LOG.md` - Progress throughout sprint

**Tasks to Complete (~5.5 hours):**

1. **Final database validation** (0.5 hours)
   - Run `db_manager.py validate` on final database
   - Verify all 219 models present
   - Check parse/translate results are recorded
   - Confirm no validation errors

2. **Final test run** (1 hour)
   - Run full test suite: `make test`
   - Verify all tests pass
   - Run typecheck, lint, format
   - Fix any final issues

3. **Code review and cleanup** (1 hour)
   - Remove any debug code or print statements
   - Ensure consistent code style
   - Remove unused imports
   - Add any missing docstrings
   - Final `make format` run

4. **Update CHANGELOG.md** (0.5 hours)
   - Document all Sprint 14 changes
   - List new files created
   - Document key metrics (parse rate, model counts)
   - Note any breaking changes

5. **Create SPRINT_SUMMARY.md** (1 hour)
   - Create `docs/planning/EPIC_3/SPRINT_14/SPRINT_SUMMARY.md`
   - Summarize all deliverables completed
   - Document actual vs planned metrics
   - List lessons learned
   - Note recommendations for future sprints
   - Include key statistics (parse rate, etc.)

6. **Final acceptance check** (0.5 hours)
   - Go through all acceptance criteria from PLAN.md
   - Verify each criterion is met
   - Document any deviations or exceptions
   - Get final sign-off

7. **Merge to main** (1 hour)
   - Create final PR with all remaining changes
   - Request Copilot review
   - Address any final comments
   - Merge to main branch
   - Tag release if applicable

**Deliverables:**
- All deliverables complete and validated
- `docs/planning/EPIC_3/SPRINT_14/SPRINT_SUMMARY.md`
- Updated `CHANGELOG.md`
- All code merged to main branch

**Quality Checks:**
ALWAYS run these commands before final commit:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] All acceptance criteria from PROJECT_PLAN.md met
  - [ ] All tests passing
  - [ ] Documentation complete
  - [ ] Code merged to main
- [ ] **CHECKPOINT (Day 10):** All deliverables ready
  - [ ] gamslib_status.json with 219 models and pipeline results
  - [ ] schema.json validated
  - [ ] db_manager.py with 8 working subcommands
  - [ ] batch_parse.py and batch_translate.py complete
  - [ ] Documentation complete
  - [ ] All tests passing
- [ ] Mark Day 10 as complete in `docs/planning/EPIC_3/SPRINT_14/PLAN.md`
- [ ] Check off Checkpoint 4 (Final) criteria in PLAN.md
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_14/SPRINT_LOG.md`
- [ ] Final update to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 14 Day 10: Final Review and Sprint Completion [Checkpoint 4 - FINAL]" \
                --body "Completes Day 10 tasks and Sprint 14

   ## Sprint 14 Complete
   All deliverables completed and validated.
   
   ## Final Deliverables
   - gamslib_status.json: 219 models with pipeline results
   - schema.json: JSON Schema (Draft-07) validated
   - db_manager.py: 8 subcommands (init, get, update, query, validate, list, export, stats)
   - batch_parse.py: Batch parse execution
   - batch_translate.py: Batch translate execution
   - GAMSLIB_DATABASE_SCHEMA.md: Full documentation
   - SPRINT_SUMMARY.md: Sprint retrospective
   
   ## Key Metrics
   - Models in database: 219
   - Parse attempts: 160
   - Parse success: [X] (~13%)
   - Translate success: [Y]
   - Test coverage: [Z]%
   
   ## All Checkpoints Complete
   - [x] Day 3: Schema complete
   - [x] Day 5: db_manager working
   - [x] Day 7: Verification batch complete
   - [x] Day 10: All deliverables ready" \
                --base main
   ```
2. Wait for Copilot's review to be completed
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_14/PLAN.md` (lines 318-350) - Day 10 tasks
- `docs/planning/EPIC_3/PROJECT_PLAN.md` (lines 92-223) - Sprint 14 acceptance criteria

---

## Usage Instructions

**For each day:**

1. **Start of day:**
   - Read the full prompt for that day
   - Review all prerequisite documents listed
   - Create the specified branch from main
   - Review tasks and time estimates

2. **During the day:**
   - Complete tasks in order listed
   - Run quality checks after each significant change
   - Track progress against time estimates
   - Update SPRINT_LOG.md with progress

3. **End of day:**
   - Verify all deliverables complete
   - Run final quality checks (make typecheck, lint, format, test)
   - Check off completion criteria
   - Update PLAN.md, SPRINT_LOG.md, and CHANGELOG.md
   - Create PR and request Copilot review
   - Address review comments
   - Merge once approved

4. **Quality checks reminder:**
   - ALWAYS run `make typecheck`, `make lint`, `make format`, `make test` before committing code changes
   - Skip quality checks only for documentation-only commits (no Python files changed)

5. **Checkpoint days (3, 5, 7, 10):**
   - Verify checkpoint criteria are met before proceeding
   - Check off checkpoint in PLAN.md
   - Note checkpoint completion in PR description

---

## Quick Reference

### Branch Naming Convention
- `sprint14-day1-schema-finalization`
- `sprint14-day2-migration-script`
- `sprint14-day3-db-manager-core`
- `sprint14-day4-crud-subcommands`
- `sprint14-day5-query-export`
- `sprint14-day6-batch-parse`
- `sprint14-day7-batch-translate`
- `sprint14-day8-integration-testing`
- `sprint14-day9-documentation`
- `sprint14-day10-finalization`

### Key Files to Create
- `data/gamslib/schema.json`
- `data/gamslib/gamslib_status.json`
- `scripts/gamslib/migrate_catalog.py`
- `scripts/gamslib/db_manager.py`
- `scripts/gamslib/batch_parse.py`
- `scripts/gamslib/batch_translate.py`
- `docs/infrastructure/GAMSLIB_DATABASE_SCHEMA.md`
- `docs/planning/EPIC_3/SPRINT_14/SPRINT_SUMMARY.md`

### Checkpoints
| Day | Checkpoint | Key Criteria |
|-----|------------|--------------|
| 3 | Schema Complete | schema.json validated, migration complete |
| 5 | db_manager Working | All 8 subcommands functional |
| 7 | Verification Complete | 160 models processed, results in database |
| 10 | Sprint Complete | All deliverables ready, merged to main |

### Expected Metrics
| Metric | Target |
|--------|--------|
| Models in database | 219 |
| Parse attempts | 160 |
| Parse success | ~15-25 (~13%) |
| db_manager subcommands | 8 |
| Test coverage | >80% |

---

## Notes

- Each prompt is designed to be self-contained with all necessary context
- Prerequisites ensure you have necessary background before starting
- Quality checks ensure code quality throughout the sprint
- Completion criteria provide clear definition of "done"
- All prompts reference specific line numbers in PLAN.md for detailed task descriptions
- PR & Review workflow ensures thorough code review before merging
- Checkpoint days require additional verification before proceeding

---

*Document created: January 1, 2026*
*Sprint 14 Execution Prompts*

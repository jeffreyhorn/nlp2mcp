# Sprint 13 Day-by-Day Prompts

This file contains comprehensive prompts for each day of Sprint 13 (Days 1-10). Each prompt is designed to be used when starting work on that specific day.

**Sprint Focus:** GAMSLIB Discovery, Download Infrastructure & Convexity Verification Foundation

**Estimated Total Effort:** 29-39 hours

---

## Day 1 Prompt: Directory Structure & Catalog Schema Implementation

**Branch:** Create a new branch named `sprint13-day1-catalog-schema` from `main`

**Objective:** Set up the directory structure for GAMSLIB data and implement the catalog dataclasses with unit tests.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 1-100) - Sprint overview and goals
- Review `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md` - Category 1 (GAMSLIB Access) and Category 5 (Integration)
- Review `docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md` - Task 7 (JSON Catalog Schema Design)
- Review `docs/infrastructure/GAMSLIB_CATALOG_SCHEMA.md` - Schema specification
- Review `data/gamslib/catalog_example.json` - Example catalog structure

**Tasks to Complete (3-4 hours):**

1. **Create Directory Structure** (30 min)
   - Create `data/gamslib/` directory
   - Create `data/gamslib/raw/` for downloaded .gms files
   - Create `data/gamslib/mcp/` for generated MCP files
   - Create `data/gamslib/archive/` for historical snapshots
   - Add `.gitignore` entries for raw files and generated MCPs
   - Create `scripts/gamslib/` directory for scripts

2. **Implement Catalog Dataclasses** (1.5-2 hours)
   - Create `scripts/gamslib/catalog.py`
   - Implement `ModelEntry` dataclass with fields:
     - model_id, sequence_number, model_name
     - gamslib_type (LP, NLP, QCP, etc.)
     - source_url, web_page_url, description, keywords
     - download_status, download_date, file_path, file_size_bytes
     - notes
   - Implement `GamslibCatalog` dataclass with:
     - schema_version, created_date, updated_date
     - gams_version, total_models
     - models list
   - Add JSON serialization/deserialization methods
   - Add catalog query methods (by type, by status)

3. **Create Empty Catalog** (15 min)
   - Create `data/gamslib/catalog.json` with schema
   - Initialize with empty models list
   - Set schema_version to "1.0.0"

4. **Write Unit Tests** (45 min - 1 hour)
   - Create `tests/test_gamslib_catalog.py`
   - Test ModelEntry creation and serialization
   - Test GamslibCatalog load/save
   - Test query methods (filter by type, filter by status)
   - Test edge cases (empty catalog, missing fields)

**Deliverables:**
- `data/gamslib/` directory structure with .gitignore
- `scripts/gamslib/catalog.py` with dataclasses
- `data/gamslib/catalog.json` (empty, with schema)
- `tests/test_gamslib_catalog.py` with passing tests

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Directory structure exists with proper .gitignore
  - [ ] Catalog dataclasses implemented and documented
  - [ ] Empty catalog.json created with correct schema
  - [ ] Unit tests pass for all catalog operations
- [ ] Mark Day 1 as complete in `docs/planning/EPIC_3/SPRINT_13/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_13/SPRINT_LOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 13 Day 1: Directory Structure & Catalog Schema" \
                --body "Completes Day 1 tasks from Sprint 13 PLAN.md

   ## Changes
   - Created data/gamslib/ directory structure
   - Implemented catalog dataclasses in scripts/gamslib/catalog.py
   - Created empty catalog.json with schema
   - Added unit tests for catalog operations

   ## Testing
   - All unit tests pass
   - Quality checks pass" \
                --base main
   ```
2. Wait for review
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 82-98)
- `docs/infrastructure/GAMSLIB_CATALOG_SCHEMA.md`
- `data/gamslib/catalog_example.json`

---

## Day 2 Prompt: Model List Population

**Branch:** Create a new branch named `sprint13-day2-model-discovery` from `main`

**Objective:** Create the model discovery script that populates the catalog with 50+ LP/NLP/QCP candidate models from GAMSLIB.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 99-111) - Day 2 tasks
- Review `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md` - Unknowns 1.1-1.4, 2.1-2.5
- Review `docs/research/GAMSLIB_ACCESS_RESEARCH.md` - GAMSLIB access methods
- Review `docs/research/GAMSLIB_MODEL_TYPES.md` - Model type definitions and counts
- Verify Day 1 deliverables are complete (catalog.py exists)

**Tasks to Complete (3-4 hours):**

1. **Create Model Discovery Script** (1.5-2 hours)
   - Create `scripts/gamslib/discover_models.py`
   - Implement GAMSLIB index parsing:
     - Use `gamslib -g` to generate model list
     - Parse output for model names and sequence numbers
   - Extract model types from solve statements:
     - Pattern: `solve ... using <type>`
     - Identify LP, NLP, QCP models
   - Extract metadata:
     - Model name from $title line
     - Description from comments
     - Keywords if available

2. **Implement Filtering Logic** (45 min)
   - Include: LP (57), NLP (49), QCP (9) = 115 candidates
   - Exclude: MIP, MINLP, MIQCP, MCP, MPEC, CNS, DNLP, EMP, MPSGE, GAMS, DECIS
   - Log excluded models with reasons
   - Target: 50+ models in final catalog

3. **Populate Catalog** (30 min)
   - Load existing catalog.json
   - Add discovered models as ModelEntry objects
   - Set download_status to "pending"
   - Save updated catalog

4. **Generate Discovery Report** (30 min)
   - Create `data/gamslib/discovery_report.md`
   - Summary statistics:
     - Total models discovered
     - Models by type (LP, NLP, QCP)
     - Excluded models count and reasons
   - List of included models

**Deliverables:**
- `scripts/gamslib/discover_models.py`
- Updated `data/gamslib/catalog.json` with 50+ entries
- `data/gamslib/discovery_report.md`

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Discovery script runs without errors
  - [ ] Catalog contains 50+ model entries
  - [ ] Models correctly typed (LP, NLP, QCP)
  - [ ] Discovery report generated with statistics
- [ ] Check off **Checkpoint Day 2** in PLAN.md:
  - [ ] Catalog contains 50+ candidate model entries
- [ ] Mark Day 2 as complete in `docs/planning/EPIC_3/SPRINT_13/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_13/SPRINT_LOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 13 Day 2: Model List Population" \
                --body "Completes Day 2 tasks from Sprint 13 PLAN.md

   ## Changes
   - Created discover_models.py script
   - Populated catalog with [X] candidate models
   - Generated discovery report

   ## Checkpoint
   - Catalog Populated: [X] models (>= 50 required)

   ## Model Distribution
   - LP: [X] models
   - NLP: [X] models  
   - QCP: [X] models

   ## Testing
   - All quality checks pass" \
                --base main
   ```
2. Wait for review
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 99-111)
- `docs/research/GAMSLIB_ACCESS_RESEARCH.md`
- `docs/research/GAMSLIB_MODEL_TYPES.md`
- `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md` (Unknowns 1.1-1.4)

---

## Day 3 Prompt: Download Script Development

**Branch:** Create a new branch named `sprint13-day3-download-script` from `main`

**Objective:** Create the download script that uses the `gamslib` command to extract models to the local filesystem.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 115-129) - Day 3 tasks
- Review `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md` - Unknown 1.2 (gamslib command)
- Review `scripts/download_gamslib_nlp.sh` - Existing download script for reference
- Verify Day 2 deliverables are complete (catalog.json populated)

**Tasks to Complete (4-5 hours):**

1. **Create Download Script** (2-2.5 hours)
   - Create `scripts/gamslib/download_models.py`
   - Implement `gamslib` command wrapper:
     ```python
     subprocess.run(['gamslib', model_name], cwd=target_dir)
     ```
   - Extract models to `data/gamslib/raw/`
   - Handle model extraction by name or sequence number

2. **Implement Idempotent Downloads** (45 min)
   - Check if file already exists before downloading
   - Skip existing files with informative logging
   - Add `--force` flag to re-download if needed
   - Track download attempts and successes

3. **Add Error Handling and Logging** (45 min)
   - Handle `gamslib` command failures
   - Log each download attempt (success/failure)
   - Capture error messages for failed downloads
   - Create download error log

4. **Update Catalog with Download Status** (30 min)
   - Update ModelEntry.download_status: "pending" → "downloaded" or "failed"
   - Record download_date timestamp
   - Record file_path for downloaded files
   - Save updated catalog after each batch

5. **Add CLI Interface** (30 min)
   - Add argparse for command-line options:
     - `--model`: Download specific model
     - `--all`: Download all pending models
     - `--force`: Re-download existing files
     - `--dry-run`: Show what would be downloaded
   - Add progress output

**Deliverables:**
- `scripts/gamslib/download_models.py` with CLI
- Updated `data/gamslib/catalog.json` with download status
- Download error log (if any failures)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Download script runs without errors
  - [ ] Can extract models using `gamslib` command
  - [ ] Idempotent operation works (skips existing)
  - [ ] Error handling captures failures
  - [ ] Catalog updated with download status
- [ ] Check off **Checkpoint Day 3** in PLAN.md:
  - [ ] Download script functional, can extract models
- [ ] Mark Day 3 as complete in `docs/planning/EPIC_3/SPRINT_13/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_13/SPRINT_LOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 13 Day 3: Download Script Development" \
                --body "Completes Day 3 tasks from Sprint 13 PLAN.md

   ## Changes
   - Created download_models.py with gamslib wrapper
   - Implemented idempotent downloads
   - Added error handling and logging
   - Added CLI interface

   ## Checkpoint
   - Download script functional: Yes
   - Test extraction successful: Yes

   ## Testing
   - Tested with 3-5 sample models
   - All quality checks pass" \
                --base main
   ```
2. Wait for review
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 115-129)
- `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md` (Unknown 1.2)
- `scripts/download_gamslib_nlp.sh` (existing script reference)

---

## Day 4 Prompt: Full Model Set Download & Validation

**Branch:** Create a new branch named `sprint13-day4-full-download` from `main`

**Objective:** Download all 50+ candidate models and validate file integrity.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 130-141) - Day 4 tasks
- Verify Day 3 deliverables are complete (download_models.py exists)
- Verify catalog.json has 50+ pending entries

**Tasks to Complete (2-3 hours):**

1. **Download All Candidate Models** (1 hour)
   - Run: `python scripts/gamslib/download_models.py --all`
   - Monitor progress and log output
   - Handle any failures gracefully
   - Retry failed downloads if needed

2. **Validate File Integrity** (30 min)
   - Verify all expected .gms files exist
   - Check file sizes are reasonable (not empty)
   - Verify files are valid GAMS syntax (basic check)
   - Count downloaded vs expected

3. **Handle Edge Cases** (30 min)
   - Document any missing models
   - Log models that failed to download
   - Create error report for failed downloads
   - Update catalog with failure reasons

4. **Update Catalog with File Sizes** (15 min)
   - Record file_size_bytes for each downloaded file
   - Update download_date for successful downloads
   - Ensure all metadata is complete

5. **Create Download Summary Report** (30 min)
   - Create `data/gamslib/download_report.md`
   - Summary:
     - Total models attempted
     - Successful downloads
     - Failed downloads (with reasons)
     - Total bytes downloaded
   - List of all downloaded models with sizes

**Deliverables:**
- All 50+ models downloaded to `data/gamslib/raw/`
- Updated `data/gamslib/catalog.json` with file metadata
- `data/gamslib/download_report.md`
- Error log (if any failures)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

Note: The downloaded .gms files in `data/gamslib/raw/` are gitignored and won't be committed.

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] 50+ models downloaded successfully
  - [ ] All files validated (exist, non-empty)
  - [ ] Catalog updated with file sizes
  - [ ] Download report generated
- [ ] Mark Day 4 as complete in `docs/planning/EPIC_3/SPRINT_13/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_13/SPRINT_LOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 13 Day 4: Full Model Set Download & Validation" \
                --body "Completes Day 4 tasks from Sprint 13 PLAN.md

   ## Changes
   - Downloaded [X] models to data/gamslib/raw/
   - Updated catalog with file metadata
   - Created download report

   ## Download Summary
   - Total attempted: [X]
   - Successful: [X]
   - Failed: [X]

   ## Testing
   - All quality checks pass
   - File integrity validated" \
                --base main
   ```
2. Wait for review
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 130-141)

---

## Day 5 Prompt: GAMS Execution Framework

**Branch:** Create a new branch named `sprint13-day5-gams-execution` from `main`

**Objective:** Create the convexity verification script with GAMS execution framework, .lst file parsing, and timeout handling.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 145-159) - Day 5 tasks
- Review `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md` - Category 3 (Convexity Verification), Unknowns 3.1-3.4
- Review `docs/research/CONVEXITY_VERIFICATION_DESIGN.md` - Verification approach
- Review `docs/testing/GAMS_ENVIRONMENT_STATUS.md` - GAMS batch execution
- Verify Day 4 deliverables are complete (models downloaded)

**Tasks to Complete (5-6 hours):**

1. **Create Verification Script** (1 hour)
   - Create `scripts/gamslib/verify_convexity.py`
   - Implement main entry point
   - Add argparse CLI:
     - `--model`: Verify specific model
     - `--all`: Verify all downloaded models
     - `--timeout`: Set timeout (default 60s)
   - Create result dataclass for verification results

2. **Implement GAMS Execution Wrapper** (1.5-2 hours)
   - Run GAMS via subprocess:
     ```python
     subprocess.run(['gams', model_path, 'lo=3'], 
                    timeout=timeout, capture_output=True)
     ```
   - Capture stdout and stderr
   - Handle process exit codes
   - Create .lst file in output directory

3. **Add .lst File Parsing** (1.5 hours)
   - Parse GAMS .lst file for results
   - Extract MODEL STATUS using regex:
     ```python
     pattern = r'\*\*\*\* MODEL STATUS\s+(\d+)'
     ```
   - Extract SOLVER STATUS using regex:
     ```python
     pattern = r'\*\*\*\* SOLVER STATUS\s+(\d+)'
     ```
   - Extract OBJECTIVE VALUE using regex:
     ```python
     pattern = r'\*\*\*\* OBJECTIVE VALUE\s+([\d.eE+-]+)'
     ```
   - Handle multiple solve statements

4. **Add Timeout Handling** (30 min)
   - Use subprocess timeout parameter
   - Catch subprocess.TimeoutExpired
   - Kill process on timeout
   - Record timeout in results

5. **Create Result Dataclass** (30 min)
   - Create `VerificationResult` dataclass:
     - model_id, model_path
     - solver_status, model_status
     - objective_value
     - solve_time_sec
     - error_message (if any)
     - timed_out (bool)
   - Add serialization methods

**Deliverables:**
- `scripts/gamslib/verify_convexity.py` with execution framework
- Result dataclass for verification results
- .lst file parsing working

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Can execute GAMS models via subprocess
  - [ ] .lst file parsing extracts STATUS codes
  - [ ] Timeout handling works correctly
  - [ ] Results captured in dataclass
- [ ] Check off **Checkpoint Day 5** in PLAN.md:
  - [ ] GAMS execution framework ready
- [ ] Mark Day 5 as complete in `docs/planning/EPIC_3/SPRINT_13/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_13/SPRINT_LOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 13 Day 5: GAMS Execution Framework" \
                --body "Completes Day 5 tasks from Sprint 13 PLAN.md

   ## Changes
   - Created verify_convexity.py script
   - Implemented GAMS subprocess execution
   - Added .lst file parsing for STATUS codes
   - Added timeout handling

   ## Checkpoint
   - GAMS execution framework: Ready
   - .lst parsing: Working
   - Timeout handling: Implemented

   ## Testing
   - Tested on sample model (trnsport.gms)
   - All quality checks pass" \
                --base main
   ```
2. Wait for review
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 145-159)
- `docs/research/CONVEXITY_VERIFICATION_DESIGN.md`
- `docs/testing/GAMS_ENVIRONMENT_STATUS.md`
- `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md` (Unknowns 3.1-3.4)

---

## Day 6 Prompt: Classification Logic & Initial Run

**Branch:** Create a new branch named `sprint13-day6-classification` from `main`

**Objective:** Implement the convexity classification logic and run verification on the test model set.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 160-172) - Day 6 tasks
- Review `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md` - Unknowns 3.1, 3.5, 3.7
- Review `docs/research/CONVEXITY_VERIFICATION_DESIGN.md` - Classification algorithm
- Review `tests/fixtures/gamslib_test_models/MANIFEST.md` - Test model expected results
- Verify Day 5 deliverables are complete (verify_convexity.py exists)

**Tasks to Complete (3-4 hours):**

1. **Implement Classification Logic** (1.5 hours)
   - Add classification function to verify_convexity.py
   - Classification rules:
     - MODEL STATUS 1 (Optimal) with LP → `verified_convex`
     - MODEL STATUS 1 or 2 with NLP/QCP → `likely_convex`
     - MODEL STATUS 3 (Unbounded) → `excluded`
     - MODEL STATUS 4 (Infeasible) → `excluded`
     - MODEL STATUS 5, 6, 19 (Infeasible variants) → `excluded`
     - Timeout or error → `error`
   - Return ConvexityStatus enum

2. **Handle LP Models** (30 min)
   - Auto-classify LP as `verified_convex` when STATUS 1
   - LP uses CPLEX by default (proves global optimum)
   - Log LP classification reasoning

3. **Handle NLP/QCP Models** (30 min)
   - Classify as `likely_convex` with STATUS 1 or 2
   - NLP uses CONOPT by default (local solver)
   - Cannot prove global optimality
   - Log NLP classification reasoning

4. **Run Verification on Test Models** (45 min)
   - Use 13 test models from `tests/fixtures/gamslib_test_models/`
   - Compare results against MANIFEST.md expected values
   - Validate classification logic
   - Log any discrepancies

5. **Update Catalog with Convexity Results** (30 min)
   - Add convexity status to catalog entries
   - Record solver used, solve time, objective
   - Save updated catalog

**Deliverables:**
- Classification logic in `scripts/gamslib/verify_convexity.py`
- Verification results for 13 test models
- Updated catalog with convexity status

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Classification logic implemented correctly
  - [ ] LP models classified as verified_convex
  - [ ] NLP/QCP models classified as likely_convex
  - [ ] All 13 test models verified
  - [ ] Results match expected values from MANIFEST.md
- [ ] Mark Day 6 as complete in `docs/planning/EPIC_3/SPRINT_13/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_13/SPRINT_LOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 13 Day 6: Classification Logic & Initial Run" \
                --body "Completes Day 6 tasks from Sprint 13 PLAN.md

   ## Changes
   - Implemented convexity classification logic
   - Added LP/NLP/QCP specific handling
   - Verified 13 test models

   ## Test Model Results
   - LP models: [X] verified_convex
   - NLP models: [X] likely_convex
   - Excluded: [X]

   ## Testing
   - All 13 test models verified
   - Results match MANIFEST.md expectations
   - All quality checks pass" \
                --base main
   ```
2. Wait for review
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 160-172)
- `docs/research/CONVEXITY_VERIFICATION_DESIGN.md`
- `tests/fixtures/gamslib_test_models/MANIFEST.md`
- `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md` (Unknowns 3.1, 3.5, 3.7)

---

## Day 7 Prompt: Integration Testing & Bug Fixes

**Branch:** Create a new branch named `sprint13-day7-integration` from `main`

**Objective:** Run the full pipeline on all 50+ models, fix any bugs, and generate the convexity summary report.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 176-189) - Day 7 tasks
- Verify Day 6 deliverables are complete (classification logic working)
- Verify all 50+ models downloaded to `data/gamslib/raw/`

**Tasks to Complete (3-4 hours):**

1. **Run Full Pipeline on 50+ Models** (1.5-2 hours)
   - Execute: `python scripts/gamslib/verify_convexity.py --all`
   - Monitor progress (may take 30-60 minutes)
   - Log all results
   - Note any failures or unexpected behavior

2. **Fix Bugs Discovered During Testing** (1 hour)
   - Address parsing failures
   - Fix classification edge cases
   - Handle unexpected solver output
   - Fix timeout handling issues

3. **Handle Edge Cases** (30 min)
   - Models with multiple solve statements
   - Models with unusual output formats
   - Models that fail to compile
   - License limit errors (if any)

4. **Generate Convexity Summary Report** (30 min)
   - Create `data/gamslib/convexity_report.md`
   - Statistics:
     - Total models verified
     - verified_convex count
     - likely_convex count
     - excluded count (by reason)
     - error count
   - List of models by classification

5. **Review and Update Catalog** (15 min)
   - Ensure all models have convexity status
   - Verify metadata is complete
   - Fix any inconsistencies

**Deliverables:**
- All 50+ models verified
- Bug fixes committed
- `data/gamslib/convexity_report.md`
- Updated `data/gamslib/catalog.json`

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] All 50+ models verified
  - [ ] Bugs fixed and tested
  - [ ] Edge cases handled
  - [ ] Convexity report generated
  - [ ] Catalog complete and accurate
- [ ] Check off **Checkpoint Day 7** in PLAN.md:
  - [ ] Convexity classification running
  - [ ] Test models classified
- [ ] Mark Day 7 as complete in `docs/planning/EPIC_3/SPRINT_13/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_13/SPRINT_LOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 13 Day 7: Integration Testing & Bug Fixes" \
                --body "Completes Day 7 tasks from Sprint 13 PLAN.md

   ## Changes
   - Ran full pipeline on [X] models
   - Fixed [X] bugs discovered during testing
   - Generated convexity report

   ## Checkpoint
   - Convexity verification: Working
   - All models classified: Yes

   ## Classification Summary
   - verified_convex: [X]
   - likely_convex: [X]
   - excluded: [X]
   - error: [X]

   ## Testing
   - All quality checks pass" \
                --base main
   ```
2. Wait for review
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 176-189)

---

## Day 8 Prompt: Documentation & Checkpoint Review

**Branch:** Create a new branch named `sprint13-day8-documentation` from `main`

**Objective:** Create model type documentation, update script docstrings, and review against acceptance criteria.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 190-203) - Day 8 tasks
- Review `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 260-305) - Acceptance Criteria
- Verify Day 7 deliverables are complete (all models verified)

**Tasks to Complete (2-3 hours):**

1. **Create GAMSLIB_MODEL_TYPES.md** (1 hour)
   - Create `docs/research/GAMSLIB_MODEL_TYPES.md`
   - Document all GAMS model types:
     - LP, NLP, QCP (included)
     - MIP, MINLP, MIQCP (excluded - integer)
     - MCP, MPEC (excluded - complementarity)
     - CNS (excluded - no objective)
     - DNLP (excluded - non-smooth)
     - EMP, MPSGE, GAMS, DECIS (excluded - specialized)
   - Include model counts and examples

2. **Document Exclusion Rationale** (30 min)
   - Why integer programs excluded (MIP, MINLP)
   - Why complementarity problems excluded (MCP, MPEC)
   - Why non-smooth excluded (DNLP)
   - Why specialized frameworks excluded

3. **Update Script Docstrings** (30 min)
   - Add module docstrings to all scripts
   - Add function docstrings with parameters
   - Document CLI usage
   - Add examples in docstrings

4. **Create Usage Examples** (30 min)
   - Add example commands to script help
   - Create `docs/guides/GAMSLIB_USAGE.md` with:
     - How to discover models
     - How to download models
     - How to verify convexity
     - How to query catalog

5. **Review Against Acceptance Criteria** (30 min)
   - Check each criterion in PLAN.md
   - Document any gaps
   - Create remediation plan for gaps

**Deliverables:**
- `docs/research/GAMSLIB_MODEL_TYPES.md`
- Updated script docstrings
- `docs/guides/GAMSLIB_USAGE.md`
- Acceptance criteria review

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to run quality checks if all changes are documentation files (.md files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] GAMSLIB_MODEL_TYPES.md created
  - [ ] Exclusion rationale documented
  - [ ] Script docstrings updated
  - [ ] Usage examples created
  - [ ] Acceptance criteria reviewed
- [ ] Mark Day 8 as complete in `docs/planning/EPIC_3/SPRINT_13/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_13/SPRINT_LOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 13 Day 8: Documentation & Checkpoint Review" \
                --body "Completes Day 8 tasks from Sprint 13 PLAN.md

   ## Changes
   - Created docs/research/GAMSLIB_MODEL_TYPES.md
   - Updated all script docstrings
   - Created docs/guides/GAMSLIB_USAGE.md

   ## Documentation
   - Model types documented: All 15 types
   - Exclusion rationale: Complete
   - Usage examples: Included

   ## Acceptance Criteria Review
   - [X criteria met / Y total]

   ## Testing
   - All quality checks pass (for any code changes)" \
                --base main
   ```
2. Wait for review
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 190-203, 260-305)

---

## Day 9 Prompt: Address Issues & Refinements

**Branch:** Create a new branch named `sprint13-day9-refinements` from `main`

**Objective:** Address any issues from Day 7-8 testing, improve error messages, and add robustness.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 207-218) - Day 9 tasks
- Review Day 7-8 PR comments and issues
- Review convexity_report.md for any failures

**Tasks to Complete (2-3 hours):**

1. **Address Issues from Testing** (1 hour)
   - Fix any bugs reported in Day 7-8 reviews
   - Address edge cases that failed
   - Improve handling of unusual models
   - Update tests for fixed issues

2. **Improve Error Messages** (30 min)
   - Make error messages user-friendly
   - Include context in errors (model name, file path)
   - Add suggestions for common errors
   - Improve logging output

3. **Add Edge Case Handling** (30 min)
   - Handle models with no solve statement
   - Handle models with compilation errors
   - Handle models with missing data
   - Handle unexpected .lst file formats

4. **Optimize Performance if Needed** (30 min)
   - Profile if verification is slow
   - Parallelize verification if helpful
   - Optimize .lst parsing if needed
   - Add progress indicators

5. **Update Tests for New Cases** (30 min)
   - Add tests for edge cases discovered
   - Add tests for error handling
   - Ensure test coverage is adequate

**Deliverables:**
- Bug fixes from Day 7-8
- Improved error messages
- Additional edge case handling
- Updated tests

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] All Day 7-8 issues addressed
  - [ ] Error messages improved
  - [ ] Edge cases handled
  - [ ] Tests updated and passing
- [ ] Mark Day 9 as complete in `docs/planning/EPIC_3/SPRINT_13/PLAN.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_3/SPRINT_13/SPRINT_LOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 13 Day 9: Address Issues & Refinements" \
                --body "Completes Day 9 tasks from Sprint 13 PLAN.md

   ## Changes
   - Fixed [X] issues from Day 7-8
   - Improved error messages
   - Added edge case handling
   - Updated tests

   ## Issues Addressed
   - [List specific issues fixed]

   ## Testing
   - All tests pass
   - All quality checks pass" \
                --base main
   ```
2. Wait for review
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 207-218)
- Day 7-8 PR comments

---

## Day 10 Prompt: Final Documentation & Sprint Review Prep

**Branch:** Create a new branch named `sprint13-day10-final` from `main`

**Objective:** Complete final documentation, update CHANGELOG, and prepare for sprint retrospective.

**Prerequisites:**
- Read `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 219-232) - Day 10 tasks
- Review `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 260-305) - Acceptance Criteria
- Verify Days 1-9 deliverables are complete

**Tasks to Complete (2-3 hours):**

1. **Final Catalog Review** (30 min)
   - Review all entries in catalog.json
   - Verify data quality and completeness
   - Fix any inconsistencies
   - Generate final statistics

2. **Create Sprint Summary Report** (45 min)
   - Create `docs/planning/EPIC_3/SPRINT_13/SPRINT_SUMMARY.md`
   - Include:
     - Sprint goals achieved
     - Deliverables completed
     - Model statistics
     - Convexity results
     - Lessons learned
     - Handoff to Sprint 14

3. **Update CHANGELOG.md** (30 min)
   - Add Sprint 13 release notes
   - List all new features:
     - GAMSLIB catalog infrastructure
     - Download script
     - Convexity verification
   - List all documentation added

4. **Prepare Sprint Retrospective Notes** (30 min)
   - What went well
   - What could be improved
   - Lessons learned
   - Recommendations for Sprint 14

5. **Final Acceptance Criteria Review** (30 min)
   - Check off each criterion in PLAN.md
   - Verify all deliverables exist
   - Document any deviations
   - Confirm sprint complete

**Deliverables:**
- Final `data/gamslib/catalog.json`
- `docs/planning/EPIC_3/SPRINT_13/SPRINT_SUMMARY.md`
- Updated `CHANGELOG.md`
- Sprint retrospective notes

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to run quality checks if all changes are documentation files (.md files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Catalog reviewed and finalized
  - [ ] Sprint summary created
  - [ ] CHANGELOG updated
  - [ ] Retrospective notes prepared
  - [ ] All acceptance criteria verified
- [ ] Check off **Checkpoint Day 10** in PLAN.md:
  - [ ] All acceptance criteria met
  - [ ] 100% criteria checked
- [ ] Mark Day 10 as complete in `docs/planning/EPIC_3/SPRINT_13/PLAN.md`
- [ ] Mark Sprint 13 as COMPLETE in PLAN.md
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log final progress to `docs/planning/EPIC_3/SPRINT_13/SPRINT_LOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 13 Day 10: Final Documentation & Sprint Complete" \
                --body "Completes Day 10 tasks and Sprint 13 PLAN.md

   ## Changes
   - Finalized catalog.json
   - Created SPRINT_SUMMARY.md
   - Updated CHANGELOG.md
   - Prepared retrospective notes

   ## Sprint 13 Complete
   - All acceptance criteria met: Yes
   - Total models cataloged: [X]
   - verified_convex: [X]
   - likely_convex: [X]

   ## Handoff to Sprint 14
   - Catalog ready for batch verification
   - Download and verification scripts complete
   - Gap: Add solver_type to ModelIR (deferred)" \
                --base main
   ```
2. Wait for review
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_3/SPRINT_13/PLAN.md` (lines 219-232, 260-305)

---

## Usage Instructions

**For each day:**

1. **Start of day:**
   - Read the full prompt for that day
   - Review all prerequisite documents
   - Create the specified branch from main
   - Review tasks and time estimates

2. **During the day:**
   - Complete tasks in order
   - Run quality checks after each significant change
   - Track progress against time estimates

3. **End of day:**
   - Verify all deliverables complete
   - Run final quality checks
   - Check off completion criteria
   - Update PLAN.md, and CHANGELOG.md
   - Update SPRINT_LOG.md with day summary
   - Create PR and wait for review
   - Address review comments
   - Merge once approved

4. **Quality checks reminder:**
   - ALWAYS run `make typecheck`, `make lint`, `make format`, `make test` before committing code changes
   - Skip quality checks only for documentation-only commits

---

## Notes

- Each prompt is designed to be self-contained
- Prerequisites ensure you have necessary context
- Quality checks ensure code quality throughout
- Completion criteria provide clear definition of "done"
- All prompts reference specific line numbers in PLAN.md for detailed task descriptions
- PR & Review workflow ensures thorough code review before merging
- Checkpoint days have additional criteria to verify

---

## Checkpoint Summary

| Day | Checkpoint | Criteria |
|-----|------------|----------|
| 2 | Catalog Populated | 50+ model entries in catalog.json |
| 3 | Download Functional | Download script extracts models |
| 5 | Execution Framework | GAMS execution framework ready |
| 7 | Verification Working | Convexity classification running |
| 10 | Sprint Complete | All acceptance criteria met |

---

## Reference Documents Index

| Document | Purpose |
|----------|---------|
| `docs/planning/EPIC_3/SPRINT_13/PLAN.md` | Sprint plan with tasks |
| `docs/planning/EPIC_3/SPRINT_13/KNOWN_UNKNOWNS.md` | Verified unknowns |
| `docs/planning/EPIC_3/SPRINT_13/PREP_PLAN.md` | Prep task results |
| `docs/research/GAMSLIB_ACCESS_RESEARCH.md` | GAMSLIB access methods |
| `docs/research/GAMSLIB_MODEL_TYPES.md` | Model type definitions |
| `docs/research/CONVEXITY_VERIFICATION_DESIGN.md` | Verification approach |
| `docs/infrastructure/GAMSLIB_CATALOG_SCHEMA.md` | Catalog schema |
| `docs/testing/GAMS_ENVIRONMENT_STATUS.md` | GAMS environment |
| `tests/fixtures/gamslib_test_models/MANIFEST.md` | Test model expected results |

---

## Changelog

- **2025-12-31:** Sprint 13 PLAN_PROMPTS.md created

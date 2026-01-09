# EPIC 3 Project Plan (GAMSLIB Validation Track)

This plan translates `GOALS.md` into sprint-ready guidance for Sprints 13–17 (two weeks each).

---

# Sprint 13 (Weeks 1–2): GAMSLIB Discovery, Download Infrastructure & Convexity Verification Foundation

**Goal:** Establish infrastructure to discover, download, and classify GAMSLIB models. Begin convexity verification system to identify models suitable for MCP reformulation testing.

## Components

### GAMSLIB Model Discovery & Classification (~12-15h)
- **Model Type Research (4-5h)**
  - Research GAMSLIB model metadata and classification schemes
  - Document model type codes: NLP, LP, QCP, MIP, MINLP, MPEC, CNS, DNLP, MPSGE
  - Create exclusion list: Integer Programs (MIP, MILP, MINLP), MPEC, MPSGE, CNS, DNLP
  - Identify target model types: NLP (nonlinear programs) and LP (linear programs)
  - **Deliverable:** `docs/research/GAMSLIB_MODEL_TYPES.md`

- **Initial Model Catalog Creation (4-5h)**
  - Scrape/parse GAMSLIB documentation pages for model listings
  - Extract metadata: model name, declared type, description, author, source URL
  - Filter to NLP and LP candidates (exclude specialized types)
  - Store in `data/gamslib/gamslib_status.json` (formerly `catalog.json`)
  - Target: 50+ candidate models identified
  - **Deliverable:** Initial catalog with metadata

- **Download Script Development (4-5h)**
  - Create `scripts/gamslib/download_models.py`
  - Support downloading from GAMS Model Library URLs
  - Handle authentication if required (GAMS website access)
  - Store raw .gms files in `data/gamslib/raw/` (gitignored)
  - Implement idempotent downloads (skip existing files)
  - Log download status, failures, and file sizes
  - **Deliverable:** Working download script with error handling

### Convexity Verification Foundation (~8-10h)
- **GAMS Execution Framework (5-6h)**
  - Create `scripts/gamslib/verify_convexity.py` (initial version)
  - Execute GAMS models locally via command-line interface
  - Capture solver output and termination status
  - Parse GAMS listing files (.lst) for solution information
  - Handle timeouts (configurable, default 60s per model)
  - **Deliverable:** Script that can run GAMS models and capture output

- **Convexity Classification Logic (3-4h)**
  - Analyze solver termination status:
    - `Optimal` (globally) → `verified_convex`
    - `Locally Optimal` → `locally_optimal` (exclude)
    - `Infeasible` → `infeasible` (exclude)
    - `Unbounded` → `unbounded` (exclude)
    - Solver error/timeout → `unknown` (flag for review)
  - For LP models: automatically classify as convex (LP = convex by definition)
  - Record solver used, solve time, objective value
  - **Deliverable:** Classification logic integrated into verify script

### Directory Structure Setup (~2h)
- Create `data/gamslib/` directory structure:
  ```
  data/gamslib/
    ├── raw/                    # Downloaded .gms files (gitignored)
    ├── mcp/                    # Generated MCP files (gitignored)
    ├── gamslib_status.json     # Model status database v2.0.0 (version controlled)
    ├── catalog.json            # Legacy catalog v1.0.0 (version controlled)
    ├── schema.json             # JSON Schema for validation
    └── archive/                # Database backups
  ```
- Create `.gitignore` entries for raw files and generated MCPs
- Initialize empty database with schema v2.0.0
- **Deliverable:** Directory structure ready for use

## Deliverables
- `docs/research/GAMSLIB_MODEL_TYPES.md` - Model type documentation
- `scripts/gamslib/download_models.py` - Download automation
- `scripts/gamslib/verify_convexity.py` - Initial convexity verification
- `data/gamslib/gamslib_status.json` - Model status database (50+ candidates)
- `data/gamslib/` directory structure with gitignore
- 50+ models downloaded and cataloged

## Acceptance Criteria
- **Model Discovery:** 50+ NLP/LP candidate models identified and cataloged
- **Download Script:** Successfully downloads models from GAMSLIB with proper error handling
- **Convexity Script:** Can execute GAMS models locally and classify by solver status
- **Catalog Structure:** JSON catalog contains metadata for all discovered models
- **Documentation:** Model type research documented with clear exclusion rationale
- **Quality:** All scripts have basic unit tests and error handling

**Estimated Effort:** 22-27 hours  
**Risk Level:** LOW (infrastructure work with clear deliverables)

---

# Sprint 14 (Weeks 3–4): Complete Convexity Verification & JSON Database Infrastructure

**Goal:** Complete convexity verification for all candidate models. Design and implement the JSON database schema and management tools for tracking model status through the nlp2mcp pipeline.

## Components

### Complete Convexity Verification (~10-12h)
- **Batch Verification Execution (4-5h)**
  - Run convexity verification on all 50+ candidate models
  - Handle solver failures, timeouts, and edge cases gracefully
  - Log detailed results for each model
  - Generate summary statistics (verified convex, locally optimal, infeasible, etc.)
  - **Target:** 30+ models verified as convex

- **Multi-Solver Validation (Optional) (3-4h)**
  - If available, verify with secondary solver (CONOPT, IPOPT, KNITRO)
  - Compare solutions between solvers
  - Flag disagreements as potential non-convexity
  - **Note:** Optional based on solver availability

- **Verification Results Integration (3h)**
  - Update database with convexity status for all models
  - Record: solver used, solve time, objective value, termination status
  - Create summary report of verification results
  - **Deliverable:** Updated catalog with convexity data

### JSON Database Schema Design (~6-8h)
- **Schema Specification (4-5h)**
  - Design comprehensive JSON schema for model tracking:
    ```json
    {
      "model_id": "trnsport",
      "model_name": "A Transportation Problem",
      "gamslib_type": "LP",
      "source_url": "https://...",
      "download_date": "2025-01-15",
      "file_size_bytes": 2345,
      
      "convexity": {
        "status": "verified_convex|locally_optimal|infeasible|unbounded|unknown|excluded",
        "solver": "CONOPT",
        "solve_time_sec": 0.12,
        "objective_value": 153.675,
        "verified_date": "2025-01-16"
      },
      
      "nlp2mcp_parse": {
        "status": "success|failure|partial",
        "error_message": null,
        "error_line": null,
        "parse_time_sec": 0.05,
        "variables_count": 6,
        "equations_count": 5,
        "tested_date": "2025-01-17",
        "nlp2mcp_version": "0.10.0"
      },
      
      "nlp2mcp_translate": {
        "status": "success|failure|not_tested",
        "error_message": null,
        "translate_time_sec": 0.15,
        "mcp_variables_count": 18,
        "mcp_equations_count": 17,
        "output_file": "data/gamslib/mcp/trnsport_mcp.gms",
        "tested_date": "2025-01-17",
        "nlp2mcp_version": "0.10.0"
      },
      
      "mcp_solve": {
        "status": "success|failure|mismatch|not_tested",
        "solver": "PATH",
        "solve_time_sec": 0.08,
        "objective_value": 153.675,
        "solution_match": true,
        "tolerance": 1e-6,
        "tested_date": "2025-01-17"
      },
      
      "notes": ""
    }
    ```
  - Document schema in `docs/infrastructure/GAMSLIB_DATABASE_SCHEMA.md`
  - Include field descriptions, valid values, and examples
  - **Deliverable:** Documented schema specification

- **Schema Validation (2-3h)**
  - Implement JSON schema validation (jsonschema library)
  - Create `data/gamslib/schema.json` for validation
  - Validate all database entries against schema
  - **Deliverable:** Schema validation integrated into db_manager

### Database Management Scripts (~8-10h)
- **Core Database Manager (6-8h)**
  - Create `scripts/gamslib/db_manager.py` with subcommands:
    - `init` - Initialize empty database with schema version
    - `add MODEL_ID` - Add new model entry
    - `update MODEL_ID FIELD VALUE` - Update specific field
    - `get MODEL_ID` - Get model details
    - `query --status=X --stage=Y` - Query by criteria
    - `list` - List all models with summary
    - `validate` - Validate database against schema
    - `export --format=csv|markdown` - Export for reporting
  - Implement atomic updates (write to temp, then rename)
  - Add backup before major changes
  - **Deliverable:** Fully functional db_manager script

- **Version Control Strategy (2h)**
  - Database file: `data/gamslib/gamslib_status.json` (version controlled)
  - Add schema version field for future migrations
  - Create archive strategy: `data/gamslib/archive/YYYYMMDD_gamslib_status.json`
  - Document version control workflow
  - **Deliverable:** Version control documentation

## Deliverables
- Updated `scripts/gamslib/verify_convexity.py` - Complete verification system
- `data/gamslib/gamslib_status.json` - Initial database with convexity data
- `data/gamslib/schema.json` - JSON schema for validation
- `scripts/gamslib/db_manager.py` - Database management tool
- `docs/infrastructure/GAMSLIB_DATABASE_SCHEMA.md` - Schema documentation
- 30+ verified convex models ready for pipeline testing

## Acceptance Criteria
- **Convexity Verification:** All 50+ candidate models verified with results recorded
- **Verified Convex Count:** At least 30 models classified as `verified_convex`
- **Database Schema:** Complete schema documented with all fields specified
- **Database Manager:** All subcommands functional (init, add, update, query, export)
- **Validation:** Schema validation catches invalid entries
- **Documentation:** Schema and workflow fully documented
- **Quality:** Database manager has comprehensive tests

**Estimated Effort:** 24-30 hours  
**Risk Level:** LOW-MEDIUM (schema design requires careful thought)

---

# Sprint 15 (Weeks 5–6): Pipeline Testing Infrastructure & Initial Baseline

**Goal:** Build automated testing infrastructure to run verified convex models through nlp2mcp parse/translate/solve pipeline. Establish initial baseline metrics.

## Components

### Parse Testing Infrastructure (~8-10h)
- **Parse Test Script (6-8h)**
  - Create `scripts/gamslib/test_parse.py`
  - For each verified convex model:
    - Run nlp2mcp parser on .gms file
    - Capture success/failure and error messages
    - Record parse time and model statistics (variables, equations)
    - Handle partial parses (record what was parsed)
  - Support modes: single model, batch (all), filtered (by status)
  - Update database with parse results automatically
  - **Deliverable:** Parse testing script with database integration

- **Parse Error Classification (2h)**
  - Categorize parse errors by type:
    - Unsupported syntax (specify which construct)
    - Lexer/tokenization errors
    - Grammar/parser errors
    - IR construction errors
  - Store error category in database for analysis
  - **Deliverable:** Error classification integrated into test script

### Translation Testing Infrastructure (~6-8h)
- **Translation Test Script (5-6h)**
  - Create `scripts/gamslib/test_translate.py`
  - For models that parse successfully:
    - Run full nlp2mcp translation pipeline
    - Generate MCP files to `data/gamslib/mcp/`
    - Capture success/failure and error messages
    - Record translation time and MCP statistics
  - Update database with translation results
  - **Deliverable:** Translation testing script

- **Translation Error Classification (1-2h)**
  - Categorize translation errors:
    - Differentiation errors (unsupported operations)
    - Min/max reformulation errors
    - KKT generation errors
    - Code generation errors
  - **Deliverable:** Error classification for translation

### MCP Solve Testing Infrastructure (~8-10h)
- **Solve Test Script (6-8h)**
  - Create `scripts/gamslib/test_solve.py`
  - For models that translate successfully:
    - Solve generated MCP with PATH solver
    - Compare MCP solution to original NLP solution:
      - Objective value match (within tolerance)
      - Solution status (optimal, infeasible, etc.)
    - Record solve time and iterations
  - Configurable tolerance (default: 1e-6 relative, 1e-8 absolute)
  - Update database with solve results
  - **Deliverable:** Solve testing script with solution comparison

- **Solution Mismatch Handling (2h)**
  - When solutions don't match:
    - Record both objective values
    - Flag for manual review
    - Store detailed comparison in notes
  - Handle cases: infeasibility, multiple optima, numerical issues
  - **Deliverable:** Mismatch detection and recording

### Full Pipeline Runner (~4-5h)
- **Orchestration Script (3-4h)**
  - Create `scripts/gamslib/run_full_test.py`
  - Orchestrate: verify → parse → translate → solve
  - Handle failures gracefully (continue to next model)
  - Generate summary after run
  - Support filters: `--only-parse`, `--only-translate`, `--only-failing`, `--model=NAME`
  - **Deliverable:** Full pipeline runner

- **Initial Baseline Run (1h)**
  - Run full pipeline on all verified convex models
  - Record baseline metrics in database
  - Generate initial status report
  - **Deliverable:** Baseline metrics recorded

## Deliverables
- `scripts/gamslib/test_parse.py` - Parse testing with error classification
- `scripts/gamslib/test_translate.py` - Translation testing
- `scripts/gamslib/test_solve.py` - Solve testing with solution comparison
- `scripts/gamslib/run_full_test.py` - Full pipeline orchestration
- Updated `data/gamslib/gamslib_status.json` with initial test results
- Initial baseline metrics documented

## Acceptance Criteria
- **Parse Testing:** Can test all verified convex models and record results
- **Translation Testing:** Can translate parsed models and record results
- **Solve Testing:** Can solve translated MCPs and compare solutions
- **Pipeline Runner:** Full pipeline runs without manual intervention
- **Database Updated:** All test results recorded in gamslib_status.json
- **Error Classification:** Parse and translation errors categorized
- **Baseline Recorded:** Initial metrics available for comparison
- **Quality:** All scripts have error handling and logging

**Estimated Effort:** 26-33 hours  
**Risk Level:** MEDIUM (PATH solver integration may have edge cases)

---

# Sprint 16 (Weeks 7–8): Reporting, Gap Analysis & Targeted Parser Improvements

**Goal:** Generate comprehensive reports from test results. Perform detailed gap analysis to identify improvement priorities. Begin implementing high-impact parser fixes.

## Components

### Reporting Infrastructure (~8-10h)
- **Status Summary Report Generator (4-5h)**
  - Create `scripts/gamslib/generate_report.py`
  - Generate markdown report: `data/gamslib/GAMSLIB_STATUS.md`
  - Include:
    - Total models in corpus
    - Models verified as convex
    - Parse success rate (count and percentage)
    - Translation success rate
    - Solve success rate (with solution match rate)
    - Overall pipeline success rate
  - Group by failure type for quick analysis
  - **Deliverable:** Automated report generation

- **Failure Analysis Report (3-4h)**
  - Generate `data/gamslib/FAILURE_ANALYSIS.md`
  - Group failures by error type/message
  - Identify most common failure modes
  - Calculate models affected by each failure type
  - Prioritize fixes by impact (models unblocked)
  - **Deliverable:** Prioritized failure analysis

- **Progress Tracking (1h)**
  - Create `data/gamslib/progress_history.json`
  - Record success rates with timestamp and nlp2mcp version
  - Enable historical comparison
  - **Deliverable:** Progress tracking infrastructure

### Gap Analysis (~6-8h)
- **Parse Failure Gap Analysis (3-4h)**
  - Categorize all parse failures by missing feature:
    - List specific unsupported GAMS constructs
    - Count models blocked by each construct
    - Estimate implementation effort (low/medium/high)
  - Create prioritized list for parser improvements
  - **Deliverable:** Parse gap analysis with priorities

- **Translation Failure Gap Analysis (2h)**
  - Categorize translation failures:
    - Unsupported operations in differentiation
    - Min/max handling issues
    - Bound handling issues
    - KKT generation errors
  - Cross-reference with existing known issues
  - **Deliverable:** Translation gap analysis

- **Solve Failure Gap Analysis (1-2h)**
  - Categorize solve failures:
    - PATH solver errors
    - Solution mismatches
    - Convergence issues
  - Identify if issue is in nlp2mcp or inherent difficulty
  - **Deliverable:** Solve gap analysis

- **Improvement Roadmap (1h)**
  - Create `data/gamslib/IMPROVEMENT_ROADMAP.md`
  - List all gaps with priority (HIGH/MEDIUM/LOW)
  - Estimate fix complexity
  - Map to remaining sprint work
  - **Deliverable:** Actionable improvement roadmap

### Targeted Parser Improvements (~10-14h)
- **Identify Top Parse Blockers (2h)**
  - From gap analysis, select top 3-5 missing features
  - Focus on features that unblock the most models
  - Create implementation plan for each
  - **Deliverable:** Implementation plan for priority features

- **Implement Priority Parser Features (8-12h)**
  - For each identified blocker:
    1. Analyze required GAMS syntax
    2. Extend grammar in `src/gams/grammar.lark`
    3. Update parser in `src/ir/parser.py`
    4. Add unit tests
    5. Verify previously-failing models now parse
  - Target: 3-5 features implemented
  - **Deliverable:** Parser improvements with tests

### Retest After Improvements (~2h)
- **Regression Testing (1h)**
  - Ensure existing passing models still pass
  - Run full test suite
  - **Deliverable:** No regressions

- **Re-run Baseline (1h)**
  - Run full pipeline with updated parser
  - Record new success rates
  - Compare to initial baseline
  - Document improvement in progress history
  - **Deliverable:** Updated metrics showing improvement

## Deliverables
- `scripts/gamslib/generate_report.py` - Report generation
- `data/gamslib/GAMSLIB_STATUS.md` - Status summary report
- `data/gamslib/FAILURE_ANALYSIS.md` - Detailed failure analysis
- `data/gamslib/IMPROVEMENT_ROADMAP.md` - Prioritized improvement plan
- `data/gamslib/progress_history.json` - Historical metrics
- Parser improvements for 3-5 high-priority features
- Updated metrics showing improvement over baseline

## Acceptance Criteria
- **Reports:** Status and failure analysis reports generated automatically
- **Gap Analysis:** All failures categorized with impact assessment
- **Improvement Roadmap:** Clear priorities for remaining work
- **Parser Improvements:** 3-5 features implemented with tests
- **Parse Rate Improvement:** 20%+ improvement from baseline
- **No Regressions:** All previously passing models still pass
- **Progress Tracked:** Before/after metrics recorded
- **Quality:** All new code has comprehensive tests

**Estimated Effort:** 26-34 hours  
**Risk Level:** MEDIUM (parser changes require careful testing)

---

# Sprint 17 (Weeks 9–10): Translation/Solve Improvements, Final Assessment & Release

**Goal:** Address remaining translation and solve failures. Complete final testing, documentation, and release v1.1.0 with comprehensive GAMSLIB validation infrastructure.

## Components

### Translation Improvements (~8-10h)
- **Identify Top Translation Blockers (2h)**
  - From gap analysis, select top translation issues
  - Focus on issues affecting multiple models
  - Common candidates:
    - Additional function support in differentiation
    - Edge cases in KKT generation
    - Bound handling improvements
  - **Deliverable:** Translation improvement plan

- **Implement Translation Fixes (6-8h)**
  - For each identified issue:
    1. Analyze root cause
    2. Implement fix
    3. Add regression tests
    4. Verify previously-failing models now translate
  - Target: Address top 3-5 translation issues
  - **Deliverable:** Translation improvements with tests

### Solve Improvements (~6-8h)
- **Investigate Solve Failures (3-4h)**
  - Analyze all solve failures and mismatches
  - Categorize by root cause:
    - PATH solver configuration
    - Initial point issues
    - Scaling/conditioning problems
    - Numerical tolerance
    - Actual nlp2mcp bugs
  - **Deliverable:** Solve failure analysis

- **Implement Solve Improvements (3-4h)**
  - Potential improvements:
    - Better initial point handling
    - PATH solver options tuning
    - Tolerance adjustments
    - Scaling improvements
  - **Deliverable:** Solve improvements

### Final Assessment (~6-8h)
- **Final Test Run (2h)**
  - Run complete pipeline on all verified convex models
  - Record final metrics
  - Compare to baseline and Sprint 16 results
  - **Deliverable:** Final test results

- **Final Reports (2-3h)**
  - Update `GAMSLIB_STATUS.md` with final results
  - Generate comparison: baseline → final
  - Document total improvement achieved
  - **Deliverable:** Final status report with comparison

- **Gap Documentation (2-3h)**
  - Document remaining gaps for future work
  - Identify models still failing and why
  - Prioritize for Epic 4
  - **Deliverable:** Remaining gaps documented

### Documentation & Release (~6-8h)
- **User Documentation (3-4h)**
  - Create `docs/guides/GAMSLIB_TESTING.md`
  - How to run local GAMSLIB tests
  - How to interpret results
  - How to add new models
  - Troubleshooting guide
  - **Deliverable:** User-facing documentation

- **Infrastructure Documentation (2h)**
  - Document all scripts and their usage
  - Database management guide
  - Report generation guide
  - **Deliverable:** Infrastructure documentation

- **Release Preparation (1-2h)**
  - Update CHANGELOG
  - Update version to v1.1.0
  - Create release notes
  - Tag release
  - **Deliverable:** v1.1.0 release

## Deliverables
- Translation improvements for top issues
- Solve improvements (configuration, tolerance, etc.)
- Final `GAMSLIB_STATUS.md` with complete results
- Progress comparison: baseline → Sprint 16 → final
- `docs/guides/GAMSLIB_TESTING.md` - User documentation
- Updated infrastructure documentation
- Release tag `v1.1.0`

## Acceptance Criteria

### Primary Metrics
- **Parse Success:** ≥70% of verified convex models parse successfully
- **Translation Success:** ≥60% of parsed models translate successfully
- **Solve Success:** ≥80% of translated models solve correctly (solution match)
- **Full Pipeline:** ≥50% of verified convex models complete full pipeline
- **Improvement:** ≥25% improvement in full pipeline success over baseline

### Infrastructure Complete
- **Reproducible:** Any developer can run tests and get same results
- **Documented:** Clear documentation for all scripts and workflows
- **Automated:** Full pipeline can run without manual intervention
- **Tracked:** All results recorded in version-controlled database

### Quality Gates
- All existing tests passing
- No regressions from Sprint 16
- All new code has tests
- Documentation complete and reviewed

### Release Ready
- v1.1.0 tagged and released
- CHANGELOG updated
- Release notes published

**Estimated Effort:** 26-34 hours  
**Risk Level:** LOW-MEDIUM (mostly polish and documentation)

---

## Rolling KPIs & Tracking

### Sprint-Level KPIs
| Metric | Sprint 13 | Sprint 14 | Sprint 15 | Sprint 16 | Sprint 17 |
|--------|-----------|-----------|-----------|-----------|-----------|
| Models Cataloged | 50+ | 50+ | 50+ | 50+ | 50+ |
| Verified Convex | - | 30+ | 30+ | 30+ | 30+ |
| Parse Success | - | - | Baseline | +20% | ≥70% |
| Translate Success | - | - | Baseline | Baseline | ≥60% |
| Solve Success | - | - | Baseline | Baseline | ≥80% |
| Full Pipeline | - | - | Baseline | Baseline | ≥50% |

### Dashboard Updates
- `data/gamslib/GAMSLIB_STATUS.md` - Updated after each test run
- `data/gamslib/progress_history.json` - Updated after each sprint
- Reports regenerated automatically via `scripts/gamslib/generate_report.py`

---

## Risk Mitigation Summary

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| GAMS licensing issues | HIGH | MEDIUM | Verify license early; document requirements |
| Few convex models | MEDIUM | LOW | Research GAMSLIB early; expand criteria if needed |
| Complex model dependencies | MEDIUM | MEDIUM | Handle gracefully; document skipped models |
| Solution comparison issues | MEDIUM | MEDIUM | Use appropriate tolerances; flag non-unique optima |
| Parser changes cause regressions | MEDIUM | LOW | Comprehensive test suite; regression testing |

---

## File Structure Summary

```
data/gamslib/
  ├── raw/                    # Downloaded .gms files (gitignored)
  ├── mcp/                    # Generated MCP files (gitignored)
  ├── gamslib_status.json     # Model status database v2.0.0 (version controlled)
  ├── catalog.json            # Legacy catalog v1.0.0 (version controlled)
  ├── schema.json             # JSON Schema for validation
  ├── progress_history.json   # Historical metrics (version controlled)
  ├── GAMSLIB_STATUS.md       # Summary report (version controlled)
  ├── FAILURE_ANALYSIS.md     # Failure analysis (version controlled)
  ├── IMPROVEMENT_ROADMAP.md  # Prioritized fixes (version controlled)
  └── archive/                # Historical snapshots

scripts/gamslib/
  ├── download_models.py      # Download from GAMSLIB
  ├── verify_convexity.py     # Verify models are convex
  ├── db_manager.py           # Database management
  ├── test_parse.py           # Test parsing
  ├── test_translate.py       # Test translation
  ├── test_solve.py           # Test MCP solving
  ├── run_full_test.py        # Run complete pipeline
  └── generate_report.py      # Generate reports

docs/
  ├── research/GAMSLIB_MODEL_TYPES.md
  ├── infrastructure/GAMSLIB_DATABASE_SCHEMA.md
  └── guides/GAMSLIB_TESTING.md
```

---

## Dependencies & Prerequisites

### External Dependencies
- GAMS software installed locally (with valid license)
- PATH solver available (included with GAMS)
- Internet access for GAMSLIB downloads
- Python 3.9+ with dependencies (requests, jsonschema)

### Internal Dependencies
- nlp2mcp core functionality from Epic 1-2
- Convexity detection from Epic 2 (optional, for additional validation)
- Existing test infrastructure

---

## Changelog

- **2025-12-29:** Initial EPIC_3 project plan created

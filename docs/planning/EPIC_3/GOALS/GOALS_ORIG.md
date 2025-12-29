# EPIC 3 Goals: GAMSLIB Validation & Comprehensive Testing Infrastructure

**Timeline:** 10 weeks (5 sprints of 2 weeks each)  
**Sprints:** 13-17  
**Target Release:** v1.1.0  
**Status:** Planning Phase

## Overview

Epic 3 focuses on building a comprehensive local testing infrastructure using the GAMS Model Library (GAMSLIB) as a validation corpus. The goal is to systematically identify, catalog, and test all convex nonlinear programs (NLPs) and linear programs (LPs) from GAMSLIB that are suitable for MCP reformulation, then measure and improve nlp2mcp's ability to parse, translate, and solve them correctly.

This epic does NOT include CI integration due to GAMS licensing constraints. All testing infrastructure will be designed for local execution with results tracked in version-controlled JSON databases.

## Strategic Themes

1. **GAMSLIB Corpus Discovery** - Identify and download all suitable convex NLP/LP models
2. **Convexity Verification** - Verify models are truly convex by solving with GAMS and confirming global solutions
3. **Local Database Infrastructure** - Build JSON-based cataloging and status tracking
4. **Pipeline Validation** - Measure parse/translate/solve success rates
5. **Targeted Improvements** - Systematically fix issues to improve success rates

---

## Goal Categories

### 1. GAMSLIB Problem Discovery & Download Infrastructure

**Priority:** HIGH  
**Estimated Effort:** Sprint 13 (2 weeks)

#### Motivation
Before we can test nlp2mcp against real-world models, we need to systematically discover and download all relevant problems from GAMSLIB. We need to filter for convex NLPs and LPs, excluding integer programs (MIP, MINLP), mathematical programs with equilibrium constraints (MPEC), and other specialized model types that are not suitable for standard MCP reformulation.

#### Objectives

- **1.1 GAMSLIB Model Type Classification**
  - Research GAMSLIB model metadata and classification scheme
  - Identify all NLP and LP models in the library
  - Exclude specialized types:
    - Integer Programs (MIP, MILP, MINLP)
    - MPEC (Mathematical Programs with Equilibrium Constraints)
    - MPSGE (General Equilibrium models)
    - CNS (Constrained Nonlinear Systems)
    - DNLP (Discontinuous NLP)
    - Other non-convex model types
  - Create initial candidate list of potentially convex models

- **1.2 Download Script Development**
  - Create `scripts/gamslib/download_models.py`
  - Download models from GAMS Model Library
  - Handle authentication/access if required
  - Store raw .gms files in `data/gamslib/raw/` (gitignored)
  - Log download status and any failures
  - Support incremental downloads (don't re-download existing files)

- **1.3 Model Metadata Extraction**
  - Parse GAMSLIB documentation pages for model metadata
  - Extract: model name, type, description, author, references
  - Store metadata in JSON format
  - Create initial catalog: `data/gamslib/catalog.json`

#### Success Criteria
- Script can download all NLP and LP models from GAMSLIB
- Initial catalog contains 50+ candidate models
- Models correctly categorized by declared type
- Download script is idempotent and handles failures gracefully

---

### 2. Convexity Verification System

**Priority:** HIGH  
**Estimated Effort:** Sprint 13-14 (2-3 weeks)

#### Motivation
Not all NLP models labeled as "NLP" in GAMSLIB are convex. We need to verify convexity by actually solving the models with GAMS and confirming the solver reports a global optimum (not just a local solution). This is essential because non-convex problems are not suitable for MCP reformulation.

#### Objectives

- **2.1 GAMS Solver Execution Framework**
  - Create `scripts/gamslib/verify_convexity.py`
  - Execute models locally using GAMS command-line interface
  - Capture solver output (solve status, solution values, marginals)
  - Parse GAMS listing files (.lst) for solution information
  - Handle solver timeouts and failures gracefully

- **2.2 Convexity Classification Logic**
  - Analyze solver termination status:
    - Optimal (globally) - convex candidate
    - Locally optimal - likely non-convex, exclude
    - Infeasible - exclude from testing
    - Unbounded - exclude from testing
    - Error - flag for manual review
  - Cross-reference with GAMS model declaration (MINIMIZE vs MAXIMIZE)
  - For LP models: automatically classify as convex
  - For NLP models: require global optimality status

- **2.3 Multi-Solver Validation (Optional)**
  - Solve with multiple NLP solvers (CONOPT, IPOPT, KNITRO if available)
  - Compare solutions to confirm consistency
  - Flag models where solvers disagree (potential non-convexity)

- **2.4 Update Catalog with Convexity Status**
  - Add `convexity_status` field to catalog entries:
    - `verified_convex` - solver confirms global optimum
    - `locally_optimal` - solver found local but not global solution
    - `infeasible` - no feasible solution exists
    - `unbounded` - problem is unbounded
    - `unknown` - solver failed or timed out
    - `excluded` - wrong model type (IP, MPEC, etc.)
  - Store solver output summary (objective value, solve time, solver used)

#### Success Criteria
- Can execute GAMS models locally and capture results
- Convexity verification correctly identifies non-convex models
- Catalog updated with convexity status for all candidate models
- At least 30+ models verified as convex and suitable for testing

---

### 3. JSON Database Infrastructure

**Priority:** HIGH  
**Estimated Effort:** Sprint 14 (2 weeks)

#### Motivation
We need a persistent, version-controlled database to track the status of each GAMSLIB model through the nlp2mcp pipeline. This database will enable progress tracking, regression detection, and reporting without requiring CI infrastructure.

#### Objectives

- **3.1 Database Schema Design**
  - Design comprehensive JSON schema for model tracking
  - Fields per model:
    ```json
    {
      "model_id": "trnsport",
      "model_name": "A Transportation Problem",
      "gamslib_type": "LP",
      "source_url": "https://...",
      "download_date": "2025-01-15",
      "file_size_bytes": 2345,
      
      "convexity": {
        "status": "verified_convex",
        "solver": "CONOPT",
        "solve_time_sec": 0.12,
        "objective_value": 153.675,
        "verified_date": "2025-01-16"
      },
      
      "nlp2mcp_parse": {
        "status": "success|failure|partial",
        "error_message": null,
        "parse_time_sec": 0.05,
        "variables_count": 6,
        "equations_count": 5,
        "tested_date": "2025-01-17",
        "nlp2mcp_version": "0.10.0"
      },
      
      "nlp2mcp_translate": {
        "status": "success|failure",
        "error_message": null,
        "translate_time_sec": 0.15,
        "mcp_variables_count": 18,
        "mcp_equations_count": 17,
        "output_file": "data/gamslib/mcp/trnsport_mcp.gms",
        "tested_date": "2025-01-17",
        "nlp2mcp_version": "0.10.0"
      },
      
      "mcp_solve": {
        "status": "success|failure|mismatch",
        "solver": "PATH",
        "solve_time_sec": 0.08,
        "objective_value": 153.675,
        "solution_match": true,
        "tolerance": 1e-6,
        "tested_date": "2025-01-17"
      },
      
      "notes": "Example transportation model, good test case"
    }
    ```

- **3.2 Database Management Scripts**
  - Create `scripts/gamslib/db_manager.py` with commands:
    - `init` - Initialize empty database
    - `add` - Add new model entry
    - `update` - Update model status
    - `query` - Query models by status/criteria
    - `export` - Export to CSV/markdown for reporting
    - `validate` - Validate database schema integrity

- **3.3 Version Control Strategy**
  - Database file: `data/gamslib/gamslib_status.json`
  - Raw .gms files: gitignored (too large, licensing concerns)
  - Generated MCP files: gitignored (can be regenerated)
  - Database and reports: version controlled
  - Create `.gitignore` entries for raw files

- **3.4 Database Backup & History**
  - Archive previous database versions before major updates
  - Track database schema version for migrations
  - Create `data/gamslib/archive/` for historical snapshots

#### Success Criteria
- JSON schema fully specified and documented
- Database manager script functional with all commands
- Can add, update, and query model entries
- Database validates against schema
- Version control strategy implemented

---

### 4. nlp2mcp Pipeline Testing Infrastructure

**Priority:** HIGH  
**Estimated Effort:** Sprint 15 (2 weeks)

#### Motivation
With the database in place, we need automated scripts to run all verified convex models through the nlp2mcp pipeline and record results. This will give us baseline metrics on parse/translate/solve success rates.

#### Objectives

- **4.1 Parse Testing Script**
  - Create `scripts/gamslib/test_parse.py`
  - Run nlp2mcp parser on each verified convex model
  - Capture parse success/failure and error messages
  - Record timing and model statistics
  - Update database with parse results
  - Support single model or batch testing

- **4.2 Translation Testing Script**
  - Create `scripts/gamslib/test_translate.py`
  - For models that parse successfully, run full translation
  - Generate MCP files to `data/gamslib/mcp/`
  - Capture translation success/failure and error messages
  - Record MCP model statistics (variable count, equation count)
  - Update database with translation results

- **4.3 MCP Solve Testing Script**
  - Create `scripts/gamslib/test_solve.py`
  - For models that translate successfully, solve with PATH
  - Compare MCP solution to original NLP solution:
    - Objective value match (within tolerance)
    - Variable values match (within tolerance)
    - Multiplier values reasonable
  - Record solve success/failure and any mismatches
  - Update database with solve results

- **4.4 Full Pipeline Test Runner**
  - Create `scripts/gamslib/run_full_test.py`
  - Orchestrate all three stages in sequence
  - Handle failures gracefully (continue to next model)
  - Generate summary statistics after run
  - Support filters: `--only-parse`, `--only-failing`, `--model=NAME`

#### Success Criteria
- Can run parse/translate/solve tests on all verified models
- Database accurately reflects current test status
- Can identify exactly which models fail at which stage
- Batch testing completes in reasonable time (<1 hour for full corpus)

---

### 5. Reporting & Analysis Tools

**Priority:** MEDIUM  
**Estimated Effort:** Sprint 15-16 (2 weeks)

#### Motivation
The database is only useful if we can generate meaningful reports and track progress over time. We need reporting tools to understand current status, identify patterns in failures, and measure improvement.

#### Objectives

- **5.1 Status Summary Report**
  - Create `scripts/gamslib/generate_report.py`
  - Generate markdown report: `data/gamslib/GAMSLIB_STATUS.md`
  - Include:
    - Total models in corpus
    - Models verified as convex
    - Parse success rate (with breakdown by failure type)
    - Translation success rate
    - Solve success rate (with solution match rate)
    - Overall pipeline success rate

- **5.2 Failure Analysis Report**
  - Group failures by error type/message
  - Identify most common failure modes:
    - Unsupported GAMS syntax
    - Differentiation errors
    - MCP generation errors
    - PATH solver failures
  - Prioritize fixes by impact (models affected)

- **5.3 Progress Tracking**
  - Create `data/gamslib/progress_history.json`
  - Record success rates after each major test run
  - Include nlp2mcp version and date
  - Generate progress chart data for documentation

- **5.4 Model Detail Reports**
  - Generate per-model detailed reports
  - Include: model description, test history, current status
  - Link to original GAMSLIB documentation
  - Useful for debugging specific failures

#### Success Criteria
- Can generate comprehensive status report from database
- Failure analysis correctly groups and prioritizes issues
- Progress tracking captures historical improvement
- Reports are version-controlled and updated with each test run

---

### 6. Baseline Measurement & Gap Analysis

**Priority:** HIGH  
**Estimated Effort:** Sprint 16 (2 weeks)

#### Motivation
Before we can improve, we need to measure. This goal establishes the baseline metrics and identifies the specific gaps between current capability and full GAMSLIB support.

#### Objectives

- **6.1 Initial Baseline Run**
  - Run full pipeline test on all verified convex models
  - Record baseline metrics:
    - Parse success: X / N models (Y%)
    - Translate success: X / N models (Y%)
    - Solve success: X / N models (Y%)
    - Full pipeline: X / N models (Y%)

- **6.2 Parse Failure Gap Analysis**
  - Categorize all parse failures by missing feature:
    - Unsupported GAMS syntax (list specific constructs)
    - Lexer/grammar errors
    - IR construction errors
  - Estimate effort to fix each category
  - Prioritize by number of models affected

- **6.3 Translation Failure Gap Analysis**
  - Categorize all translation failures:
    - Unsupported operations in differentiation
    - Min/max handling issues
    - Bound handling issues
    - KKT generation errors
  - Link to existing Epic 2 fixes where applicable

- **6.4 Solve Failure Gap Analysis**
  - Categorize all solve failures:
    - PATH solver errors (infeasibility, convergence)
    - Solution mismatch (wrong objective value)
    - Variable value mismatches
    - Non-convexity issues (despite verification)
  - Identify if issue is in nlp2mcp or inherent model difficulty

- **6.5 Create Improvement Roadmap**
  - Document in `data/gamslib/IMPROVEMENT_ROADMAP.md`
  - List all identified gaps with priority
  - Estimate fix complexity (low/medium/high)
  - Map fixes to potential sprint work

#### Success Criteria
- Baseline metrics recorded and documented
- All failures categorized by root cause
- Improvement roadmap created with priorities
- Clear understanding of effort needed for each improvement

---

### 7. Targeted Parser Improvements

**Priority:** MEDIUM-HIGH  
**Estimated Effort:** Sprint 16-17 (2-3 weeks)

#### Motivation
Based on gap analysis, implement the highest-impact parser improvements to increase the parse success rate.

#### Objectives

- **7.1 Identify Top Parse Blockers**
  - From gap analysis, select top 5-10 missing features
  - Focus on features that unblock the most models
  - Common candidates (to be confirmed by analysis):
    - Additional set operations
    - More parameter/scalar syntax variations
    - Equation definition variations
    - Model statement variations
    - Option/display statements (may just skip)

- **7.2 Implement Priority Parser Features**
  - For each identified blocker:
    1. Analyze required GAMS syntax
    2. Extend grammar in `src/gams/grammar.lark`
    3. Update parser in `src/ir/parser.py`
    4. Add unit tests
    5. Verify previously-failing models now parse
    6. Update database with new results

- **7.3 Re-run Baseline After Improvements**
  - Run full test suite after parser improvements
  - Record new success rates
  - Compare to baseline
  - Document improvement in progress history

#### Success Criteria
- Parse success rate improved by 20%+ from baseline
- At least 5 previously-failing models now parse
- All improvements have unit tests
- Database updated with new status

---

### 8. Targeted Translation & Solve Improvements

**Priority:** MEDIUM  
**Estimated Effort:** Sprint 17 (2 weeks)

#### Motivation
Address translation and solve failures identified in gap analysis to improve end-to-end pipeline success.

#### Objectives

- **8.1 Translation Improvements**
  - Fix top translation blockers identified in gap analysis
  - Focus on issues affecting multiple models:
    - Additional function support in differentiation
    - Edge cases in KKT generation
    - Bound handling improvements
  - Each fix includes tests and database update

- **8.2 Solve Success Improvements**
  - Investigate solve failures and mismatches
  - Potential improvements:
    - Better initial point handling
    - Scaling/preconditioning
    - Tolerance adjustments
    - PATH solver options tuning

- **8.3 Final Baseline Update**
  - Run complete test suite
  - Record final Sprint 17 metrics
  - Compare to initial baseline
  - Document total improvement achieved

#### Success Criteria
- Translation success rate improved by 15%+ from baseline
- Solve success rate improved by 10%+ from baseline
- Overall pipeline success rate documented
- Clear path identified for further improvements

---

## Sprint Breakdown

### Sprint 13 (Weeks 1-2): Discovery & Download Infrastructure
- Research GAMSLIB model types and classifications
- Implement model download script
- Create initial model catalog
- Begin convexity verification system
- Set up `data/gamslib/` directory structure

**Deliverables:**
- `scripts/gamslib/download_models.py`
- `data/gamslib/catalog.json` (initial)
- 50+ models downloaded and cataloged

### Sprint 14 (Weeks 3-4): Convexity Verification & Database
- Complete convexity verification system
- Verify all candidate models
- Design and implement JSON database schema
- Create database management scripts
- Document version control strategy

**Deliverables:**
- `scripts/gamslib/verify_convexity.py`
- `scripts/gamslib/db_manager.py`
- `data/gamslib/gamslib_status.json` (with convexity data)
- 30+ verified convex models ready for testing

### Sprint 15 (Weeks 5-6): Pipeline Testing Infrastructure
- Implement parse testing script
- Implement translation testing script
- Implement solve testing script
- Create full pipeline test runner
- Begin reporting infrastructure

**Deliverables:**
- `scripts/gamslib/test_parse.py`
- `scripts/gamslib/test_translate.py`
- `scripts/gamslib/test_solve.py`
- `scripts/gamslib/run_full_test.py`
- Initial test results in database

### Sprint 16 (Weeks 7-8): Baseline & Gap Analysis
- Run initial baseline tests
- Complete gap analysis for all failure types
- Create improvement roadmap
- Begin targeted parser improvements
- Implement reporting tools

**Deliverables:**
- `data/gamslib/GAMSLIB_STATUS.md` (baseline report)
- `data/gamslib/IMPROVEMENT_ROADMAP.md`
- `scripts/gamslib/generate_report.py`
- Initial parser improvements implemented

### Sprint 17 (Weeks 9-10): Improvements & Final Assessment
- Complete targeted parser improvements
- Address translation failures
- Address solve failures
- Final test run and metrics
- Documentation and release prep

**Deliverables:**
- Improved parse/translate/solve success rates
- Final `GAMSLIB_STATUS.md` report
- Progress comparison (baseline vs final)
- v1.1.0 release with GAMSLIB validation

---

## Success Metrics

### Quantitative
- **Corpus Size:** 30+ verified convex models from GAMSLIB
- **Parse Success:** 70%+ of verified models parse successfully
- **Translation Success:** 60%+ of parsed models translate successfully
- **Solve Success:** 80%+ of translated models solve correctly
- **Full Pipeline:** 50%+ of verified models complete full pipeline
- **Improvement:** 25%+ improvement in full pipeline success over baseline

### Qualitative
- **Infrastructure Complete:** Local testing can be run without CI
- **Reproducible:** Any developer can run tests and get same results
- **Documented:** Clear understanding of what works and what doesn't
- **Actionable:** Improvement roadmap provides clear next steps
- **Maintainable:** Database and tools are easy to use and extend

---

## File Structure

```
data/gamslib/
  ├── raw/                    # Downloaded .gms files (gitignored)
  │   ├── trnsport.gms
  │   ├── ...
  ├── mcp/                    # Generated MCP files (gitignored)
  │   ├── trnsport_mcp.gms
  │   ├── ...
  ├── catalog.json            # Model metadata (version controlled)
  ├── gamslib_status.json     # Test status database (version controlled)
  ├── progress_history.json   # Historical metrics (version controlled)
  ├── GAMSLIB_STATUS.md       # Summary report (version controlled)
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
```

---

## Risks & Mitigation

### Risk 1: GAMS Licensing for Local Testing
**Impact:** HIGH  
**Probability:** MEDIUM

**Mitigation:**
- Confirm GAMS demo/community license supports GAMSLIB models
- Document license requirements clearly
- Provide instructions for obtaining appropriate license
- Design tools to work with whatever license user has

### Risk 2: Few Convex Models in GAMSLIB
**Impact:** MEDIUM  
**Probability:** LOW

**Mitigation:**
- Research GAMSLIB contents early in Sprint 13
- Expand criteria if needed (include some "nearly convex" models)
- Consider other model sources if GAMSLIB insufficient
- Focus on quality of testing over quantity

### Risk 3: Complex Model Dependencies
**Impact:** MEDIUM  
**Probability:** MEDIUM

**Mitigation:**
- Some models may require data files or includes
- Build infrastructure to handle model dependencies
- Skip models with external dependencies if too complex
- Document any skipped models and reasons

### Risk 4: Solution Comparison Difficulties
**Impact:** MEDIUM  
**Probability:** MEDIUM

**Mitigation:**
- Different solvers may find different optima for non-unique solutions
- Focus on objective value match rather than variable values
- Use appropriate tolerances for comparisons
- Document models with multiple optima

---

## Dependencies

### External Dependencies
- GAMS software installed locally (with valid license)
- PATH solver available
- Internet access for GAMSLIB downloads

### Internal Dependencies
- nlp2mcp core functionality from Epic 1-2
- Convexity detection from Epic 2 (optional, for additional validation)

---

## Future Work (Post-Epic 3)

### Epic 4 Candidates

1. **Extended Model Sources**
   - Test against other optimization libraries (CUTE, Netlib, etc.)
   - User-submitted models from community
   - Industry partner test cases

2. **Automated Regression Testing**
   - Nightly local test runs with notifications
   - Automatic database updates
   - Slack/email alerts for regressions

3. **Model Transformation Preprocessing**
   - Automatic model simplification before parsing
   - Handle common unsupported patterns via preprocessing
   - Macro expansion and include resolution

4. **Performance Optimization**
   - Profile nlp2mcp on large GAMSLIB models
   - Optimize bottlenecks identified by profiling
   - Parallel processing for batch testing

---

## References

### Internal Documents
- `docs/planning/EPIC_2/GOALS.md` - Epic 2 goals (predecessor)
- `docs/GAMS_SUBSET.md` - Supported GAMS syntax
- `docs/research/convexity_detection.md` - Convexity detection research

### External Resources
- GAMS Model Library: https://www.gams.com/latest/gamslib_ml/libhtml/
- GAMS Documentation: https://www.gams.com/latest/docs/
- PATH Solver Manual: https://www.gams.com/latest/docs/S_PATH.html
- GAMS Licensing: https://www.gams.com/products/licensing/

---

## Changelog

- **2025-12-29:** Initial EPIC_3 goals document created

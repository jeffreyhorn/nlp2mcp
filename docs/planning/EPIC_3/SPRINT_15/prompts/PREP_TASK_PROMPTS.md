# Sprint 15 Prep Task Prompts

**Purpose:** Comprehensive prompts for completing Sprint 15 preparation tasks (Tasks 2-10)  
**Created:** January 9, 2026  
**Branch:** `planning/sprint15-prep`

---

## Table of Contents

1. [Task 2: Assess Existing Batch Infrastructure](#task-2-assess-existing-batch-infrastructure)
2. [Task 3: Research Solution Comparison Strategies](#task-3-research-solution-comparison-strategies)
3. [Task 4: Design Comprehensive Error Taxonomy](#task-4-design-comprehensive-error-taxonomy)
4. [Task 5: Validate PATH Solver Integration](#task-5-validate-path-solver-integration)
5. [Task 6: Design Database Schema Extensions](#task-6-design-database-schema-extensions)
6. [Task 7: Define Test Filtering Requirements](#task-7-define-test-filtering-requirements)
7. [Task 8: Research Performance Measurement Approach](#task-8-research-performance-measurement-approach)
8. [Task 9: Research Numerical Tolerance Best Practices](#task-9-research-numerical-tolerance-best-practices)
9. [Task 10: Plan Sprint 15 Detailed Schedule](#task-10-plan-sprint-15-detailed-schedule)

---

## Task 2: Assess Existing Batch Infrastructure

### Prompt

You are working on branch `planning/sprint15-prep`. Complete Sprint 15 Prep Task 2: Assess Existing Batch Infrastructure.

**Objective:** Thoroughly analyze `scripts/gamslib/batch_parse.py` and `scripts/gamslib/batch_translate.py` from Sprint 14 to understand what functionality already exists and what needs to be added/changed for Sprint 15 testing infrastructure.

**Why This Matters:** Sprint 14 delivered batch_parse.py and batch_translate.py that already process models in batch, update database with results, categorize errors, and report progress. Sprint 15's test_parse.py and test_translate.py should reuse or extend this infrastructure, not duplicate it.

**Deliverables:**
1. `docs/planning/EPIC_3/SPRINT_15/prep-tasks/batch_infrastructure_assessment.md` containing:
   - Detailed analysis of batch_parse.py functionality (entry point, CLI args, database integration, error categorization, progress reporting)
   - Detailed analysis of batch_translate.py functionality
   - Strengths and limitations for each script
   - Comparison and reuse recommendations
   - Sprint 15 implementation strategy (extend vs. new scripts)
   - Estimated effort savings from reuse
2. Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 2.1, 2.2

**Steps:**
1. Read and analyze `scripts/gamslib/batch_parse.py` - document key functionality, command-line arguments, database loading/saving, model filtering, parse execution, error handling and categorization, progress reporting
2. Read and analyze `scripts/gamslib/batch_translate.py` - document key functionality, model selection, translation execution, MCP file output, error handling, database updates
3. Check database integration - review schema fields populated by these scripts
4. Test existing scripts (`python scripts/gamslib/batch_parse.py --help`, run on single model)
5. Create comprehensive assessment document at `docs/planning/EPIC_3/SPRINT_15/prep-tasks/batch_infrastructure_assessment.md`
6. Update `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md`:
   - For Unknown 1.1: Add verification result (replace `🔍 INCOMPLETE` with `✅ VERIFIED` or `❌ WRONG` with correction)
   - For Unknown 1.2: Add verification result
   - For Unknown 2.1: Add verification result
   - For Unknown 2.2: Add verification result

**Update PREP_PLAN.md:**
1. Update Task 2 status from `🔵 NOT STARTED` to `✅ COMPLETE`
2. Fill in the "Changes" section with files created/modified
3. Fill in the "Result" section with key findings
4. Check all acceptance criteria boxes

**Update CHANGELOG.md:**
Add entry under `## [Unreleased]` section:
```markdown
### Sprint 15 Prep Task 2: Assess Existing Batch Infrastructure
- Created `docs/planning/EPIC_3/SPRINT_15/prep-tasks/batch_infrastructure_assessment.md`
- Analyzed batch_parse.py and batch_translate.py functionality
- Documented reuse recommendations for Sprint 15
- Verified Unknowns 1.1, 1.2, 2.1, 2.2
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```

**Commit Message:**
```
Complete Sprint 15 Prep Task 2: Assess Existing Batch Infrastructure

- Created batch_infrastructure_assessment.md with full analysis
- Documented batch_parse.py functionality and reuse opportunities
- Documented batch_translate.py functionality and reuse opportunities
- Verified Unknowns 1.1, 1.2, 2.1, 2.2 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 2 status to COMPLETE
- Updated CHANGELOG.md
```

**After Commit:**
1. Push changes: `git push origin planning/sprint15-prep`
2. Create PR: `gh pr create --title "Sprint 15 Prep Task 2: Assess Existing Batch Infrastructure" --body "Completes Task 2 of Sprint 15 prep plan. See docs/planning/EPIC_3/SPRINT_15/prep-tasks/batch_infrastructure_assessment.md for full analysis."`
3. Wait for reviewer comments before proceeding

---

## Task 3: Research Solution Comparison Strategies

### Prompt

You are working on branch `planning/sprint15-prep`. Complete Sprint 15 Prep Task 3: Research Solution Comparison Strategies.

**Objective:** Research and validate strategies for comparing NLP solutions with MCP solutions to ensure the KKT reformulation produces mathematically equivalent results.

**Why This Matters:** Sprint 15's primary goal is to verify that nlp2mcp's KKT reformulation produces correct results. This requires comparing original NLP solutions with MCP solutions, handling numerical tolerance, infeasibility, and multiple optima correctly.

**Deliverables:**
1. `docs/planning/EPIC_3/SPRINT_15/prep-tasks/solution_comparison_research.md` containing:
   - Theoretical foundation (KKT optimality conditions, when NLP and MCP solutions should match)
   - Tolerance selection (recommended default tolerances with justification, relative vs absolute)
   - Status comparison decision tree (handling optimal, infeasible, status mismatches)
   - Multiple optima handling strategy
   - Comparison scope decision (objective only vs. variables vs. duals for Sprint 15)
   - Implementation approach (.lst file parsing vs. GDX vs. Python API)
   - Code reuse opportunities
   - Sprint 15 recommendations (clear and actionable)
2. Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.2, 3.3, 3.4

**Steps:**
1. Review mathematical background - read `docs/concepts/IDEA.md` and `docs/concepts/NLP2MCP_HIGH_LEVEL.md`
2. Research numerical tolerance practices - survey solver tolerances (CONOPT, IPOPT, PATH, CPLEX), relative vs absolute
3. Research infeasibility handling - identify scenarios, design decision tree
4. Research multiple optima handling - when it occurs, comparison strategy
5. Research variable comparison - decide scope for Sprint 15 (objective only recommended)
6. Survey existing tools - check GAMS comparison utilities, existing nlp2mcp validation
7. Create research document at `docs/planning/EPIC_3/SPRINT_15/prep-tasks/solution_comparison_research.md`
8. Update `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md`:
   - Unknown 3.1: Tolerance values verification
   - Unknown 3.2: Infeasibility handling verification
   - Unknown 3.3: Multiple optima handling verification
   - Unknown 3.4: Comparison scope verification

**Update PREP_PLAN.md:**
1. Update Task 3 status from `🔵 NOT STARTED` to `✅ COMPLETE`
2. Fill in the "Changes" section with files created/modified
3. Fill in the "Result" section with key findings
4. Check all acceptance criteria boxes

**Update CHANGELOG.md:**
Add entry under `## [Unreleased]` section:
```markdown
### Sprint 15 Prep Task 3: Research Solution Comparison Strategies
- Created `docs/planning/EPIC_3/SPRINT_15/prep-tasks/solution_comparison_research.md`
- Documented tolerance selection (rtol=1e-6, atol=1e-8 recommended)
- Created status comparison decision tree
- Defined multiple optima handling strategy
- Verified Unknowns 3.1, 3.2, 3.3, 3.4
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```

**Commit Message:**
```
Complete Sprint 15 Prep Task 3: Research Solution Comparison Strategies

- Created solution_comparison_research.md with comprehensive analysis
- Documented theoretical foundation for NLP/MCP comparison
- Recommended tolerance values (rtol=1e-6, atol=1e-8)
- Created status comparison decision tree
- Verified Unknowns 3.1, 3.2, 3.3, 3.4 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 3 status to COMPLETE
- Updated CHANGELOG.md
```

**After Commit:**
1. Push changes: `git push origin planning/sprint15-prep`
2. Create PR: `gh pr create --title "Sprint 15 Prep Task 3: Research Solution Comparison Strategies" --body "Completes Task 3 of Sprint 15 prep plan. See docs/planning/EPIC_3/SPRINT_15/prep-tasks/solution_comparison_research.md for full research."`
3. Wait for reviewer comments before proceeding

---

## Task 4: Design Comprehensive Error Taxonomy

### Prompt

You are working on branch `planning/sprint15-prep`. Complete Sprint 15 Prep Task 4: Design Comprehensive Error Taxonomy.

**Objective:** Design comprehensive error classification taxonomy for all three pipeline stages (parse, translate, solve) to enable systematic analysis of failure modes and targeted improvements.

**Why This Matters:** Sprint 14 had 7 parse error categories with "syntax_error" catching 77% of failures. Sprint 15 needs refined categories to enable targeted improvements, plus comprehensive translation and solve error categories.

**Deliverables:**
1. `docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md` containing:
   - Refined parse error categories (15-20 categories) - lexer, parser, semantic, IR construction errors
   - Comprehensive translation error categories (10-15 categories) - differentiation, min/max, KKT, codegen errors
   - Complete solve error categories (10-12 categories) - PATH status, comparison errors
   - Detection patterns and implementation guidelines for each category
   - Example error messages for each category
   - Migration plan from Sprint 14 categories
   - Database storage format
2. Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.3, 1.4, 2.3, 3.5

**Steps:**
1. Review existing parse error categories - analyze Sprint 14 error distribution, identify refinement opportunities
2. Design refined parse taxonomy - map to parser stages (lexer, parser, semantic, IR)
3. Design translation error taxonomy - cover differentiation, min/max, KKT, codegen stages
4. Design solve error taxonomy - map PATH solver status codes, comparison errors
5. For each category: define description, example error messages, detection patterns
6. Create migration plan from Sprint 14's 7 categories
7. Create taxonomy document at `docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md`
8. Update `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md`:
   - Unknown 1.3: Partial parse success handling verification
   - Unknown 1.4: Model statistics recording verification
   - Unknown 2.3: Translation error categories verification
   - Unknown 3.5: Solve error categories verification

**Update PREP_PLAN.md:**
1. Update Task 4 status from `🔵 NOT STARTED` to `✅ COMPLETE`
2. Fill in the "Changes" section with files created/modified
3. Fill in the "Result" section with key findings
4. Check all acceptance criteria boxes

**Update CHANGELOG.md:**
Add entry under `## [Unreleased]` section:
```markdown
### Sprint 15 Prep Task 4: Design Comprehensive Error Taxonomy
- Created `docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md`
- Designed refined parse error taxonomy (X categories)
- Designed translation error taxonomy (Y categories)
- Designed solve error taxonomy (Z categories)
- Created migration plan from Sprint 14 categories
- Verified Unknowns 1.3, 1.4, 2.3, 3.5
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```

**Commit Message:**
```
Complete Sprint 15 Prep Task 4: Design Comprehensive Error Taxonomy

- Created error_taxonomy.md with 35-45 error categories
- Refined parse errors into lexer/parser/semantic/IR subcategories
- Defined translation errors for diff/minmax/KKT/codegen stages
- Defined solve errors for PATH status and comparison
- Created migration plan from Sprint 14 categories
- Verified Unknowns 1.3, 1.4, 2.3, 3.5 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 4 status to COMPLETE
- Updated CHANGELOG.md
```

**After Commit:**
1. Push changes: `git push origin planning/sprint15-prep`
2. Create PR: `gh pr create --title "Sprint 15 Prep Task 4: Design Comprehensive Error Taxonomy" --body "Completes Task 4 of Sprint 15 prep plan. See docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md for full taxonomy."`
3. Wait for reviewer comments before proceeding

---

## Task 5: Validate PATH Solver Integration

### Prompt

You are working on branch `planning/sprint15-prep`. Complete Sprint 15 Prep Task 5: Validate PATH Solver Integration.

**Objective:** Validate that PATH solver is available, properly configured, and can be invoked from Python scripts for MCP solving.

**Why This Matters:** Sprint 15's solve testing infrastructure depends entirely on PATH solver availability. This is a blocking dependency - if PATH doesn't work, solve testing is blocked.

**Deliverables:**
1. `docs/planning/EPIC_3/SPRINT_15/prep-tasks/path_solver_integration.md` containing:
   - Environment setup (GAMS version, PATH availability, license requirements)
   - Invocation approach (command to solve MCP, options/flags, timeout config)
   - Solution extraction (parsing .lst files for status, objective, variables)
   - Error handling (common scenarios, detection patterns, status code mapping)
   - Python integration examples (subprocess invocation, solution extraction, error handling)
   - Sprint 15 recommendations (recommended approach, timeout values, error handling strategy)
2. Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.6, 3.7

**Steps:**
1. Verify PATH solver availability:
   - Check GAMS installation: `which gams`, `gams --version`
   - List solvers: `gamsinst -a | grep PATH`
   - Check license (run simple MCP solve)
2. Test MCP model generation and solve:
   - Generate MCP from simple model: `python -m nlp2mcp.cli data/gamslib/raw/trnsport.gms -o test_mcp.gms`
   - Solve: `gams test_mcp.gms`
   - Check status in .lst file
3. Test solution extraction:
   - Parse .lst file for SOLVER STATUS, MODEL STATUS, OBJECTIVE VALUE
   - Write Python extraction code samples
   - Test on successful solve, infeasible, iteration limit cases
4. Test error handling:
   - Create intentionally broken MCP (syntax error, infeasible)
   - Verify error detection from .lst file
5. Create integration guide at `docs/planning/EPIC_3/SPRINT_15/prep-tasks/path_solver_integration.md`
6. Update `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md`:
   - Unknown 3.6: PATH solver availability verification
   - Unknown 3.7: .lst file extraction verification

**Update PREP_PLAN.md:**
1. Update Task 5 status from `🔵 NOT STARTED` to `✅ COMPLETE`
2. Fill in the "Changes" section with files created/modified
3. Fill in the "Result" section with key findings
4. Check all acceptance criteria boxes

**Update CHANGELOG.md:**
Add entry under `## [Unreleased]` section:
```markdown
### Sprint 15 Prep Task 5: Validate PATH Solver Integration
- Created `docs/planning/EPIC_3/SPRINT_15/prep-tasks/path_solver_integration.md`
- Confirmed PATH solver availability and license
- Validated MCP solve workflow
- Documented solution extraction from .lst files
- Provided Python integration code samples
- Verified Unknowns 3.6, 3.7
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```

**Commit Message:**
```
Complete Sprint 15 Prep Task 5: Validate PATH Solver Integration

- Created path_solver_integration.md with integration guide
- Confirmed PATH solver available and licensed
- Validated MCP solve workflow with test models
- Documented .lst file parsing for solution extraction
- Provided Python integration code samples
- Verified Unknowns 3.6, 3.7 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 5 status to COMPLETE
- Updated CHANGELOG.md
```

**After Commit:**
1. Push changes: `git push origin planning/sprint15-prep`
2. Create PR: `gh pr create --title "Sprint 15 Prep Task 5: Validate PATH Solver Integration" --body "Completes Task 5 of Sprint 15 prep plan. See docs/planning/EPIC_3/SPRINT_15/prep-tasks/path_solver_integration.md for integration guide."`
3. Wait for reviewer comments before proceeding

---

## Task 6: Design Database Schema Extensions

### Prompt

You are working on branch `planning/sprint15-prep`. Complete Sprint 15 Prep Task 6: Design Database Schema Extensions.

**Objective:** Design extensions to `data/gamslib/schema.json` (v2.0.0) to support solve results, solution comparison, and refined error categorization for Sprint 15.

**Why This Matters:** Sprint 14 delivered schema v2.0.0 with nlp2mcp_parse and nlp2mcp_translate objects. Sprint 15 needs mcp_solve and solution_comparison objects, plus refined error category enums.

**Deliverables:**
1. `docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_v2.1.0_draft.json` - complete draft schema
2. `docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_extensions.md` containing:
   - Overview (version 2.0.0 → 2.1.0, new objects, backward compatibility)
   - mcp_solve object design (all fields, validation rules, examples)
   - solution_comparison object design (all fields, validation rules, examples)
   - Updated error category enums (parse, translate, solve categories from Task 4)
   - Migration plan (Sprint 14 data compatibility)
   - Implementation checklist
3. Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.2, 4.3, 4.4

**Steps:**
1. Design mcp_solve object:
   - Fields: status, solver_status, model_status, objective_value, solve_time_seconds, iterations, error_category, error_message, timestamp, path_version, mcp_file_used
   - Define enums for status codes
   - Define validation rules
2. Design solution_comparison object:
   - Fields: nlp_objective, mcp_objective, objective_match, absolute_difference, relative_difference, tolerance_absolute, tolerance_relative, nlp_status, mcp_status, status_match, comparison_result, notes, timestamp
   - Define comparison_result enum
   - Define validation rules
3. Update error category enums using Task 4 taxonomy (if completed) or propose categories
4. Decide schema versioning (v2.1.0 recommended - backward compatible with optional new objects)
5. Create full schema draft by copying and extending current schema
6. Validate schema syntax with jsonschema
7. Create schema_extensions.md documentation
8. Update `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md`:
   - Unknown 4.1: mcp_solve fields verification
   - Unknown 4.2: solution_comparison fields verification
   - Unknown 4.3: Schema versioning verification
   - Unknown 4.4: Error category enum extensions verification

**Update PREP_PLAN.md:**
1. Update Task 6 status from `🔵 NOT STARTED` to `✅ COMPLETE`
2. Fill in the "Changes" section with files created/modified
3. Fill in the "Result" section with key findings
4. Check all acceptance criteria boxes

**Update CHANGELOG.md:**
Add entry under `## [Unreleased]` section:
```markdown
### Sprint 15 Prep Task 6: Design Database Schema Extensions
- Created `docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_v2.1.0_draft.json`
- Created `docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_extensions.md`
- Designed mcp_solve object with X fields
- Designed solution_comparison object with Y fields
- Updated error category enums
- Confirmed backward compatibility with Sprint 14 data
- Verified Unknowns 4.1, 4.2, 4.3, 4.4
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```

**Commit Message:**
```
Complete Sprint 15 Prep Task 6: Design Database Schema Extensions

- Created schema_v2.1.0_draft.json with mcp_solve and solution_comparison objects
- Created schema_extensions.md documentation
- Designed mcp_solve object (status, objective, timing, errors)
- Designed solution_comparison object (objective match, tolerances, status)
- Updated error category enums for all pipeline stages
- Confirmed v2.1.0 backward compatible with Sprint 14 data
- Verified Unknowns 4.1, 4.2, 4.3, 4.4 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 6 status to COMPLETE
- Updated CHANGELOG.md
```

**After Commit:**
1. Push changes: `git push origin planning/sprint15-prep`
2. Create PR: `gh pr create --title "Sprint 15 Prep Task 6: Design Database Schema Extensions" --body "Completes Task 6 of Sprint 15 prep plan. See docs/planning/EPIC_3/SPRINT_15/prep-tasks/ for schema draft and documentation."`
3. Wait for reviewer comments before proceeding

---

## Task 7: Define Test Filtering Requirements

### Prompt

You are working on branch `planning/sprint15-prep`. Complete Sprint 15 Prep Task 7: Define Test Filtering Requirements.

**Objective:** Define comprehensive filtering requirements for `run_full_test.py` to enable selective testing during development and debugging.

**Why This Matters:** Without filtering, every test run processes all 160+ models, taking minutes even when debugging a single failure. Filtering enables efficient development workflows.

**Deliverables:**
1. `docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md` containing:
   - Overview (purpose of filtering, use cases summary)
   - Use case catalog (development, debugging, incremental testing, stage-specific, combination)
   - Filter API specification (complete command-line arguments with descriptions)
   - Filter combination logic (AND behavior, conflict detection)
   - Implementation guidelines (database query patterns, validation, reporting)
   - 10-15 usage examples with expected behavior
   - Sprint 15 scope (minimum viable filter set, nice-to-have deferrals)
2. Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.1, 5.2, 5.3

**Steps:**
1. Survey existing filtering in batch_parse.py and batch_translate.py
2. Enumerate use cases:
   - Development: test single model, small models, specific type
   - Debugging: re-run failures, specific error category
   - Incremental: skip completed, only untested
   - Stage-specific: only-parse, only-translate, only-solve
   - Combinations: type + status + limit
3. Design filter API:
   - Model selection: --model, --type, --convexity, --limit, --random
   - Status filtering: --parse-success, --parse-failure, --translate-success, etc.
   - Error filtering: --error-category, --parse-error, --translate-error
   - Stage control: --only-parse, --only-translate, --only-solve, --skip-*
   - Convenience: --only-failing, --skip-completed, --quick
4. Define combination logic (AND), conflict detection rules
5. Create requirements document at `docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md`
6. Update `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md`:
   - Unknown 5.1: Essential filter patterns verification
   - Unknown 5.2: Cascading failure handling verification
   - Unknown 5.3: Summary statistics verification

**Update PREP_PLAN.md:**
1. Update Task 7 status from `🔵 NOT STARTED` to `✅ COMPLETE`
2. Fill in the "Changes" section with files created/modified
3. Fill in the "Result" section with key findings
4. Check all acceptance criteria boxes

**Update CHANGELOG.md:**
Add entry under `## [Unreleased]` section:
```markdown
### Sprint 15 Prep Task 7: Define Test Filtering Requirements
- Created `docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md`
- Documented X use cases for test filtering
- Specified Y command-line filter arguments
- Defined filter combination logic and conflict detection
- Provided 10-15 usage examples
- Identified Sprint 15 MVP filter set
- Verified Unknowns 5.1, 5.2, 5.3
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```

**Commit Message:**
```
Complete Sprint 15 Prep Task 7: Define Test Filtering Requirements

- Created test_filtering_requirements.md with comprehensive filter API
- Documented development, debugging, and incremental use cases
- Specified 20+ command-line filter arguments
- Defined AND combination logic and conflict detection
- Provided 10-15 usage examples with expected behavior
- Identified Sprint 15 MVP filter set
- Verified Unknowns 5.1, 5.2, 5.3 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 7 status to COMPLETE
- Updated CHANGELOG.md
```

**After Commit:**
1. Push changes: `git push origin planning/sprint15-prep`
2. Create PR: `gh pr create --title "Sprint 15 Prep Task 7: Define Test Filtering Requirements" --body "Completes Task 7 of Sprint 15 prep plan. See docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md for filter API."`
3. Wait for reviewer comments before proceeding

---

## Task 8: Research Performance Measurement Approach

### Prompt

You are working on branch `planning/sprint15-prep`. Complete Sprint 15 Prep Task 8: Research Performance Measurement Approach.

**Objective:** Research and define approach for accurately measuring parse, translate, and solve times to establish baseline metrics and detect performance regressions.

**Why This Matters:** Sprint 15 needs to establish baseline performance metrics to answer: "How long does parsing take?", "Are there slow models?", "Is performance improving?" Accurate, consistent timing methodology is essential.

**Deliverables:**
1. `docs/planning/EPIC_3/SPRINT_15/prep-tasks/performance_measurement.md` containing:
   - Timing methodology (what to measure for each stage, timer function, handling failures)
   - Statistical analysis approach (mean, median, stddev, percentiles, outlier detection)
   - Baseline documentation format (template for Sprint 15 baseline)
   - Implementation guidelines (code patterns, database storage, reporting)
   - Sprint 15 baseline plan (when to record, what models, how to document)
2. Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 6.1, 6.2

**Steps:**
1. Review existing timing implementation in batch_parse.py and batch_translate.py
2. Research timing best practices:
   - Python timing: time.time() vs time.perf_counter() vs time.process_time()
   - Subprocess timing approaches
   - Statistical considerations (single vs multiple runs, warmup)
3. Design timing methodology:
   - Parse timing: start/end points, what's included/excluded
   - Translate timing: start/end points, what's included/excluded
   - Solve timing: start/end points (GAMS subprocess)
   - Failure handling (still record time)
4. Design statistical analysis:
   - Summary statistics: count, mean, median, stddev, min, max, percentiles
   - Outlier detection (> 2 stddev)
5. Design baseline documentation format (markdown template)
6. Create performance measurement guide at `docs/planning/EPIC_3/SPRINT_15/prep-tasks/performance_measurement.md`
7. Update `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md`:
   - Unknown 6.1: Solve time measurement verification
   - Unknown 6.2: Baseline metrics verification

**Update PREP_PLAN.md:**
1. Update Task 8 status from `🔵 NOT STARTED` to `✅ COMPLETE`
2. Fill in the "Changes" section with files created/modified
3. Fill in the "Result" section with key findings
4. Check all acceptance criteria boxes

**Update CHANGELOG.md:**
Add entry under `## [Unreleased]` section:
```markdown
### Sprint 15 Prep Task 8: Research Performance Measurement Approach
- Created `docs/planning/EPIC_3/SPRINT_15/prep-tasks/performance_measurement.md`
- Defined timing methodology using time.perf_counter()
- Specified statistical analysis approach
- Created baseline documentation format template
- Outlined Sprint 15 baseline plan
- Verified Unknowns 6.1, 6.2
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```

**Commit Message:**
```
Complete Sprint 15 Prep Task 8: Research Performance Measurement Approach

- Created performance_measurement.md with timing methodology
- Selected time.perf_counter() for accurate wall time measurement
- Defined statistical analysis (mean, median, stddev, percentiles)
- Created baseline documentation format template
- Outlined Sprint 15 baseline recording plan
- Verified Unknowns 6.1, 6.2 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 8 status to COMPLETE
- Updated CHANGELOG.md
```

**After Commit:**
1. Push changes: `git push origin planning/sprint15-prep`
2. Create PR: `gh pr create --title "Sprint 15 Prep Task 8: Research Performance Measurement Approach" --body "Completes Task 8 of Sprint 15 prep plan. See docs/planning/EPIC_3/SPRINT_15/prep-tasks/performance_measurement.md for methodology."`
3. Wait for reviewer comments before proceeding

---

## Task 9: Research Numerical Tolerance Best Practices

### Prompt

You are working on branch `planning/sprint15-prep`. Complete Sprint 15 Prep Task 9: Research Numerical Tolerance Best Practices.

**Objective:** Research appropriate numerical tolerance values for comparing NLP and MCP solutions, with justification from optimization literature and solver defaults.

**Why This Matters:** Core validation question: When are two objective values "close enough"? Too loose (1e-3) may miss errors; too tight (1e-12) may cause false positives. Need research-backed recommendations.

**Deliverables:**
1. `docs/planning/EPIC_3/SPRINT_15/prep-tasks/numerical_tolerance_research.md` containing:
   - Background (absolute vs relative vs combined tolerance, precision limits)
   - Solver tolerance survey (CONOPT, IPOPT, PATH, CPLEX defaults)
   - Testing practice survey (CUTEst, NEOS, NumPy/SciPy)
   - GAMSLIB objective value analysis (range of values)
   - Recommendations (default rtol and atol with justification)
   - Configuration approach (environment variables, CLI args)
   - Edge case handling (objective = 0, very large values)
   - Comparison algorithm: `|a - b| <= atol + rtol * |b|`
2. Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.2

**Steps:**
1. Survey GAMS solver tolerances:
   - CONOPT optimality/feasibility tolerance
   - IPOPT tol (default 1e-8)
   - PATH convergence tolerance
   - CPLEX optimality tolerance (default 1e-6)
2. Survey optimization testing practices:
   - CUTEst comparison approach
   - NumPy allclose defaults (rtol=1e-5, atol=1e-8)
   - Academic papers on solver validation
3. Analyze GAMSLIB objective value ranges:
   - Check convexity.objective_value from database
   - Identify min, max, typical range
4. Define tolerance recommendations:
   - Propose defaults (rtol=1e-6, atol=1e-8)
   - Justify from solver defaults and literature
   - Consider LP vs NLP differences
5. Define configuration approach (env vars, CLI args)
6. Document edge cases (objective=0, very large, very small)
7. Create research document at `docs/planning/EPIC_3/SPRINT_15/prep-tasks/numerical_tolerance_research.md`
8. Update `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md`:
   - Unknown 3.1: Tolerance values (update with research findings)
   - Unknown 3.2: Infeasibility handling (update with decision tree)

**Update PREP_PLAN.md:**
1. Update Task 9 status from `🔵 NOT STARTED` to `✅ COMPLETE`
2. Fill in the "Changes" section with files created/modified
3. Fill in the "Result" section with key findings
4. Check all acceptance criteria boxes

**Update CHANGELOG.md:**
Add entry under `## [Unreleased]` section:
```markdown
### Sprint 15 Prep Task 9: Research Numerical Tolerance Best Practices
- Created `docs/planning/EPIC_3/SPRINT_15/prep-tasks/numerical_tolerance_research.md`
- Surveyed solver tolerances (CONOPT, IPOPT, PATH, CPLEX)
- Analyzed GAMSLIB objective value ranges
- Recommended default tolerances: rtol=1e-6, atol=1e-8
- Documented comparison algorithm and edge cases
- Verified Unknowns 3.1, 3.2
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```

**Commit Message:**
```
Complete Sprint 15 Prep Task 9: Research Numerical Tolerance Best Practices

- Created numerical_tolerance_research.md with solver survey
- Documented CONOPT, IPOPT, PATH, CPLEX tolerance defaults
- Analyzed GAMSLIB objective value ranges
- Recommended rtol=1e-6, atol=1e-8 with justification
- Documented combined comparison: |a-b| <= atol + rtol*|b|
- Documented edge case handling
- Verified Unknowns 3.1, 3.2 in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 9 status to COMPLETE
- Updated CHANGELOG.md
```

**After Commit:**
1. Push changes: `git push origin planning/sprint15-prep`
2. Create PR: `gh pr create --title "Sprint 15 Prep Task 9: Research Numerical Tolerance Best Practices" --body "Completes Task 9 of Sprint 15 prep plan. See docs/planning/EPIC_3/SPRINT_15/prep-tasks/numerical_tolerance_research.md for research."`
3. Wait for reviewer comments before proceeding

---

## Task 10: Plan Sprint 15 Detailed Schedule

### Prompt

You are working on branch `planning/sprint15-prep`. Complete Sprint 15 Prep Task 10: Plan Sprint 15 Detailed Schedule.

**Objective:** Create detailed day-by-day plan for Sprint 15 incorporating all research findings from prep tasks and defining specific deliverables for each day.

**Why This Matters:** Sprint 15 has 10 working days to deliver parse, translate, and solve testing infrastructure plus full pipeline runner. Without a detailed plan, risk of scope creep, unclear dependencies, and no checkpoints to track progress.

**Deliverables:**
1. `docs/planning/EPIC_3/SPRINT_15/PLAN.md` containing:
   - Executive Summary (sprint goal, key deliverables, effort estimate, prep task summary)
   - Day-by-Day Plan (Days 1-10 with tasks, deliverables, acceptance criteria, time estimates, dependencies, risks)
   - Checkpoints (5 checkpoints with validation criteria)
   - Deliverables (complete list from PROJECT_PLAN.md)
   - Acceptance Criteria (from PROJECT_PLAN.md)
   - Risk Assessment (risks and mitigations)
   - Dependencies (Sprint 14, prep tasks)
   - Resource Allocation (effort by phase)
   - Appendix (prep task cross-references, unknown resolution status)
2. Updated KNOWN_UNKNOWNS.md with all verification results integrated (summary of all unknown statuses)

**Steps:**
1. Review all prep task outcomes:
   - Read all prep-tasks/*.md documents
   - Extract key decisions (reuse strategy, schema version, tolerances, error categories, filters)
   - Identify any blocking issues
2. Define Sprint 15 phases:
   - Phase 1 (Days 1-2): Foundation - schema update, error taxonomy setup
   - Phase 2 (Days 2-3): Parse Testing
   - Phase 3 (Days 3-4): Translation Testing
   - Phase 4 (Days 5-7): Solve Testing
   - Phase 5 (Days 8-9): Pipeline Integration
   - Phase 6 (Day 10): Baseline and Documentation
3. Create day-by-day plan:
   - For each day: Focus, Tasks (3-5), Deliverables, Acceptance Criteria, Time Estimate, Dependencies, Risks
4. Define checkpoints:
   - Checkpoint 1 (Day 2): Parse testing functional
   - Checkpoint 2 (Day 4): Translation testing functional
   - Checkpoint 3 (Day 7): Solve testing functional
   - Checkpoint 4 (Day 9): Full pipeline operational
   - Checkpoint 5 (Day 10): Baseline recorded, sprint complete
5. Estimate effort and validate (should total 26-33 hours)
6. Identify risks and mitigation strategies
7. Create PLAN.md following Sprint 13/14 format
8. Update KNOWN_UNKNOWNS.md with summary of all unknown resolutions

**Update PREP_PLAN.md:**
1. Update Task 10 status from `🔵 NOT STARTED` to `✅ COMPLETE`
2. Fill in the "Changes" section with files created/modified
3. Fill in the "Result" section with key findings
4. Check all acceptance criteria boxes

**Update CHANGELOG.md:**
Add entry under `## [Unreleased]` section:
```markdown
### Sprint 15 Prep Task 10: Plan Sprint 15 Detailed Schedule
- Created `docs/planning/EPIC_3/SPRINT_15/PLAN.md`
- Defined 10-day detailed schedule with daily tasks and deliverables
- Created 5 checkpoints with validation criteria
- Incorporated all prep task findings
- Validated effort estimate (26-33 hours)
- Documented risks and mitigation strategies
- All prep tasks complete - Sprint 15 ready to begin
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```

**Commit Message:**
```
Complete Sprint 15 Prep Task 10: Plan Sprint 15 Detailed Schedule

- Created PLAN.md with comprehensive 10-day schedule
- Defined daily tasks, deliverables, and acceptance criteria
- Created 5 checkpoints with validation criteria
- Incorporated findings from all prep tasks (2-9)
- Validated effort estimate: 26-33 hours
- Documented risks and mitigations
- Updated KNOWN_UNKNOWNS.md with resolution summary
- Updated PREP_PLAN.md Task 10 status to COMPLETE
- Updated CHANGELOG.md

Sprint 15 prep phase complete. Ready to begin Sprint 15 execution.
```

**After Commit:**
1. Push changes: `git push origin planning/sprint15-prep`
2. Create PR: `gh pr create --title "Sprint 15 Prep Task 10: Plan Sprint 15 Detailed Schedule - PREP COMPLETE" --body "Completes final Task 10 of Sprint 15 prep plan. Creates comprehensive PLAN.md with 10-day schedule. Sprint 15 prep phase is now complete and ready for sprint execution."`
3. Wait for reviewer comments before proceeding

---

## Summary

### Task Execution Order (Recommended)

Based on dependencies:

1. **Task 2** (Batch Infrastructure) - No dependencies, foundational
2. **Task 5** (PATH Solver) - No dependencies, critical validation
3. **Task 3** (Solution Comparison) - Depends on Task 1 (complete)
4. **Task 4** (Error Taxonomy) - Depends on Tasks 1, 2
5. **Task 9** (Tolerance) - Depends on Task 3
6. **Task 7** (Filtering) - Depends on Task 2
7. **Task 8** (Performance) - Depends on Task 2
8. **Task 6** (Schema) - Depends on Tasks 3, 4, 5
9. **Task 10** (Schedule) - Depends on all tasks

### Parallelization Opportunities

- Tasks 2, 5 can run in parallel (both no dependencies)
- Tasks 7, 8 can run in parallel (both depend only on Task 2)
- Tasks 3, 4 can run in parallel after their dependencies complete

### Total Estimated Effort

| Task | Estimated Time |
|------|----------------|
| Task 2 | 2-3h |
| Task 3 | 4-5h |
| Task 4 | 3-4h |
| Task 5 | 2-3h |
| Task 6 | 3-4h |
| Task 7 | 2-3h |
| Task 8 | 2-3h |
| Task 9 | 2-3h |
| Task 10 | 4-5h |
| **Total** | **24-33h** |

---

*Document created: January 9, 2026*  
*Branch: planning/sprint15-prep*

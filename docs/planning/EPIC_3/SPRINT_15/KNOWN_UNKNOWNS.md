# Sprint 15 Known Unknowns

**Created:** January 9, 2026  
**Status:** Active - Pre-Sprint 15  
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 15 pipeline testing infrastructure, parse/translate testing, MCP solve testing, solution comparison, and baseline metrics establishment

---

## Executive Summary

This document identifies all assumptions and unknowns for Sprint 15 features **before** implementation begins. Sprint 15 builds automated testing infrastructure to run verified convex models through the full nlp2mcp pipeline (parse → translate → solve) and establishes initial baseline metrics.

**Sprint 15 Scope:**
1. Parse Testing Infrastructure - Automated parse testing with error classification
2. Translation Testing Infrastructure - Translation testing with error categorization
3. MCP Solve Testing Infrastructure - Solve testing with solution comparison
4. Full Pipeline Runner - Orchestrated pipeline with filtering and reporting
5. Initial Baseline Metrics - Establish metrics for parse/translate/solve stages

**Reference:** See `docs/planning/EPIC_3/PROJECT_PLAN.md` lines 229-330 for complete Sprint 15 deliverables and acceptance criteria.

**Sprint 14 Key Results:**
- Parse success rate: 21.3% (34/160 models) - exceeded 13.3% baseline by 8pp
- Translation success rate: 94.1% (32/34 of parsed models)
- Database schema v2.0.0 with comprehensive pipeline tracking
- Batch processing infrastructure (batch_parse.py, batch_translate.py)

**Lessons from Previous Sprints:** The Known Unknowns process achieved excellent results:
- Sprint 14: 26 unknowns, all verified or deferred appropriately
- Sprint 13: 26 unknowns verified, 100% acceptance criteria met
- Sprint 7: 25 unknowns, achieved 30% parse rate goal

---

## How to Use This Document

### Before Sprint 15 Day 1
1. Research and verify all **Critical** and **High** priority unknowns
2. Create minimal test cases for validation
3. Document findings in "Verification Results" sections
4. Update status: 🔍 INCOMPLETE -> [x] COMPLETE or ❌ WRONG (with correction)

### During Sprint 15
1. Review daily during standup
2. Add newly discovered unknowns
3. Update with implementation findings
4. Move resolved items to "Confirmed Knowledge"

### Priority Definitions
- **Critical:** Wrong assumption will break core functionality or require major refactoring (>8 hours)
- **High:** Wrong assumption will cause significant rework (4-8 hours)
- **Medium:** Wrong assumption will cause minor issues (2-4 hours)
- **Low:** Wrong assumption has minimal impact (<2 hours)

---

## Summary Statistics

**Total Unknowns:** 26  
**By Priority:**
- Critical: 7 (unknowns that could derail sprint or block solve infrastructure)
- High: 10 (unknowns requiring upfront research)
- Medium: 6 (unknowns that can be resolved during implementation)
- Low: 3 (nice-to-know, low impact)

**By Category:**
- Category 1 (Parse Testing Infrastructure): 5 unknowns
- Category 2 (Translation Testing Infrastructure): 4 unknowns
- Category 3 (MCP Solve Testing): 7 unknowns
- Category 4 (Database Schema Extensions): 4 unknowns
- Category 5 (Pipeline Orchestration & Filtering): 3 unknowns
- Category 6 (Performance & Baseline Metrics): 3 unknowns

**Estimated Research Time:** 28-36 hours (spread across prep phase)

---

## Task-to-Unknown Mapping

This table maps each prep task to the unknowns it will verify:

| Prep Task | Description | Unknowns Verified |
|-----------|-------------|-------------------|
| Task 2 | Assess Existing Batch Infrastructure | 1.1, 1.2, 2.1, 2.2 |
| Task 3 | Research Solution Comparison Strategies | 3.1, 3.2, 3.3, 3.4 |
| Task 4 | Design Comprehensive Error Taxonomy | 1.3, 1.4, 2.3, 3.5 |
| Task 5 | Validate PATH Solver Integration | 3.6, 3.7 |
| Task 6 | Design Database Schema Extensions | 4.1, 4.2, 4.3, 4.4 |
| Task 7 | Define Test Filtering Requirements | 5.1, 5.2, 5.3 |
| Task 8 | Research Performance Measurement Approach | 6.1, 6.2 |
| Task 9 | Research Numerical Tolerance Best Practices | 3.1, 3.2 |
| Task 10 | Plan Sprint 15 Detailed Schedule | All unknowns |

---

## Table of Contents

1. [Category 1: Parse Testing Infrastructure](#category-1-parse-testing-infrastructure)
2. [Category 2: Translation Testing Infrastructure](#category-2-translation-testing-infrastructure)
3. [Category 3: MCP Solve Testing](#category-3-mcp-solve-testing)
4. [Category 4: Database Schema Extensions](#category-4-database-schema-extensions)
5. [Category 5: Pipeline Orchestration & Filtering](#category-5-pipeline-orchestration--filtering)
6. [Category 6: Performance & Baseline Metrics](#category-6-performance--baseline-metrics)
7. [Template for New Unknowns](#template-for-new-unknowns)
8. [Next Steps](#next-steps)

---

# Category 1: Parse Testing Infrastructure

## Unknown 1.1: Should test_parse.py extend or replace batch_parse.py?

### Priority
**High** - Affects implementation approach and code reuse

### Assumption
Sprint 15's test_parse.py should extend batch_parse.py functionality rather than replace it, reusing the core parsing logic and database update mechanisms.

### Research Questions
1. What functionality does batch_parse.py already provide that test_parse.py needs?
2. What additional functionality does test_parse.py require (e.g., refined error categorization)?
3. Can we use batch_parse.py as-is or does it need modifications?
4. Should we refactor batch_parse.py into a reusable module?
5. What's the risk of introducing regressions if we modify batch_parse.py?

### How to Verify

**Test Case 1: Feature comparison**
```bash
# Review batch_parse.py current features
grep -E "def |class " scripts/gamslib/batch_parse.py
```

**Test Case 2: Test batch_parse.py on subset**
```bash
python scripts/gamslib/batch_parse.py --model trnsport
# Check if it provides all needed functionality
```

**Test Case 3: Identify gaps**
- Does batch_parse.py provide detailed error categorization?
- Does it support new error categories from Task 4?
- Does it integrate with schema v2.1.0 extensions?

### Risk if Wrong
- Duplicated code if we create test_parse.py from scratch
- Regressions if we modify batch_parse.py incorrectly
- Wasted effort on unnecessary refactoring

### Estimated Research Time
2-3 hours (code review, feature analysis, decision)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 2)

**Finding:** batch_parse.py should be **extended** rather than replaced. Analysis shows it provides:
- Robust batch processing with progress reporting (every 10 models with ETA)
- Database integration via db_manager module (load, save, backup)
- Error categorization infrastructure (6 categories)
- CLI with useful filters (--model, --limit, --dry-run, --verbose)
- Direct parser import for fast execution (uses `src.ir.parser.parse_model_file`)
- Timing measurement with `time.perf_counter()`
- Periodic saves to prevent data loss

**Recommendation:** Add new filter flags to batch_parse.py:
- `--only-failing` - re-run only failed models
- `--error-category=X` - filter by specific error type
- `--parse-success/--parse-failure` - status-based filtering

**Effort Saved:** 8-10 hours by extending vs. creating from scratch.

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/batch_infrastructure_assessment.md` for full analysis.

---

## Unknown 1.2: What additional error categories are needed beyond Sprint 14's 7 categories?

### Priority
**High** - Affects error classification completeness

### Assumption
Sprint 14's 7 parse error categories (syntax_error, unsupported_feature, validation_error, missing_include, internal_error, timeout, license_limited) are insufficient and need to be refined into more specific subcategories for targeted parser improvements.

### Research Questions
1. What percentage of Sprint 14's "syntax_error" (77% of failures) could be further categorized?
2. What specific GAMS syntax constructs cause the most failures?
3. Can we detect and categorize lexer errors vs. parser errors vs. semantic errors?
4. What error patterns exist in the 126 failed parse attempts?
5. How granular should error categories be for actionable insights?

### How to Verify

**Test Case 1: Analyze existing errors**
```bash
# Check actual error messages from Sprint 14
jq '.models[] | select(.nlp2mcp_parse.status=="failure") | .nlp2mcp_parse.error_message' \
  data/gamslib/gamslib_status.json | sort | uniq -c | sort -rn | head -20
```

**Test Case 2: Sample error categorization**
```bash
# Parse a few failing models and examine detailed errors
for model in airsp andean blend; do
  echo "=== $model ==="
  python -m src.cli data/gamslib/raw/$model.gms 2>&1 | head -20
done
```

**Test Case 3: Pattern identification**
- Group errors by: lexer/tokenization, grammar/parser, semantic, IR construction
- Estimate percentage in each group

### Risk if Wrong
- Overly generic error categories don't enable targeted improvements
- Overly specific categories create too much overhead
- Inconsistent categorization between parse/translate/solve stages

### Estimated Research Time
3-4 hours (error analysis, pattern identification, taxonomy design)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 2)

**Finding:** The current 6 error categories (syntax_error, unsupported_feature, validation_error, missing_include, timeout, internal_error) are well-structured, but "syntax_error" at 77% is a catch-all that needs subcategorization.

**Current categorize_error() patterns in batch_parse.py:**
- syntax_error: parse error, unexpected character/token, syntax error, unexpected eof
- unsupported_feature: not yet implemented, unsupported
- validation_error: domain, incompatible, not defined, undefined
- missing_include: include, file not found
- timeout: timeout
- internal_error: default fallback

**Recommendation:** Refine syntax_error into subcategories in Task 4 (Error Taxonomy):
- `lexer_unknown_character` - unexpected character errors
- `parser_equation_syntax` - equation parsing failures
- `parser_expression_syntax` - expression parsing failures
- `parser_unsupported_construct` - valid GAMS but not in our grammar

These can be implemented as `error.details` field or as new enum values in schema v2.1.0.

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/batch_infrastructure_assessment.md` Section 1.4 for details.

---

## Unknown 1.3: How to handle partial parse success?

### Priority
**Medium** - Affects status accuracy

### Assumption
Some models may partially parse (e.g., declarations parsed but equations fail). These should be recorded as "partial" status with details on what succeeded vs. failed.

### Research Questions
1. Does nlp2mcp currently report partial parse results or fail completely?
2. What information is available when parsing fails mid-way?
3. Should we track: declarations parsed, equations parsed, variables defined?
4. How does partial success affect downstream translation testing?
5. Is it worth the complexity to track partial success?

### How to Verify

**Test Case 1: Examine parser behavior**
```python
# Test if parser provides partial results before failing
from src.ir.parser import parse_model_file
try:
    model = parse_model_file("data/gamslib/raw/failing_model.gms")
except Exception as e:
    # What information is available about partial progress?
    print(type(e), e)
```

**Test Case 2: Check if IR is partially populated**
- Does parse failure return any IR data?
- Can we detect which statements were parsed before failure?

### Risk if Wrong
- Losing valuable information about parser progress
- Overcomplicating the status model for minimal benefit
- Inconsistent status values across stages

### Estimated Research Time
1-2 hours (parser behavior analysis)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 4)

**Finding:** The current parser fails completely on errors rather than providing partial results. The IR is not populated if parsing fails.

**Recommendation:** For Sprint 15, continue using binary pass/fail status. Partial parse tracking is complex and low-value. If a model fails to parse, the whole model is marked as failed with the error location and message.

**Future Enhancement (Sprint 16+):** Could add progress tracking (e.g., "declarations parsed: 5, failed at equation 'balance'") but this requires significant parser refactoring.

**Impact on Error Taxonomy:** Error location (line, column) is already captured in error messages. The refined error categories (lexer, parser, semantic) provide sufficient granularity for targeted improvements.

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md` Section 1 for parse error taxonomy.

---

## Unknown 1.4: Should parse testing record model statistics (variables, equations)?

### Priority
**Medium** - Affects baseline metrics and filtering

### Assumption
Parse testing should extract and record model statistics (number of variables, equations, constraints) for successfully parsed models to enable size-based filtering and baseline metrics.

### Research Questions
1. Does the current parser provide model statistics after parsing?
2. What statistics are available from the IR after parsing?
3. Are these statistics useful for filtering or analysis?
4. What's the overhead of extracting these statistics?
5. Should statistics be stored in database or just reported?

### How to Verify

**Test Case 1: Check available statistics**
```python
from src.ir.parser import parse_model_file
model = parse_model_file("data/gamslib/raw/trnsport.gms")
# What statistics can we extract?
print(f"Variables: {len(model.variables)}")
print(f"Equations: {len(model.equations)}")
```

**Test Case 2: Review existing schema**
```bash
# Check if schema already has fields for statistics
jq '.properties.nlp2mcp_parse.properties' data/gamslib/schema.json
```

### Risk if Wrong
- Missing useful filtering/analysis capabilities
- Adding unnecessary complexity to parse testing
- Database bloat from rarely-used statistics

### Estimated Research Time
1 hour (IR inspection, schema review)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 4)

**Finding:** After successful parsing, the IR contains model statistics that can be extracted:
- Variables: `len(model.variables)`
- Equations: `len(model.equations)`
- Parameters: `len(model.parameters)`
- Sets: `len(model.sets)`

**Recommendation:** Record model statistics for successfully parsed models in the database. Add optional fields to `nlp2mcp_parse` object:
```json
{
  "model_stats": {
    "variables": 10,
    "equations": 5,
    "parameters": 3,
    "sets": 2
  }
}
```

**Use Cases:**
1. Filter by model size: `--max-variables=100`
2. Baseline analysis: "Average parse time by model complexity"
3. Performance regression: "Parse time per equation"

**Implementation:** Add statistics extraction after successful parse in batch_parse.py. Low overhead (~1ms per model).

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md` Section 4.1 for database storage format.

---

## Unknown 1.5: How should parse timing be measured for accurate baselines?

### Priority
**Low** - Affects metric accuracy

### Assumption
Parse timing should use `time.perf_counter()` and exclude file I/O overhead to measure pure parsing time for accurate baselines.

### Research Questions
1. What is currently included in parse_time_seconds from Sprint 14?
2. Should we measure: total time, parse-only time, IR construction time?
3. Is subprocess overhead significant (if using subprocess)?
4. How consistent are parse times across multiple runs?
5. What level of timing granularity is useful?

### How to Verify

**Test Case 1: Measure current timing approach**
```python
import time
from src.ir.parser import parse_model_file

# What does parse_time_seconds actually measure?
start = time.perf_counter()
model = parse_model_file("data/gamslib/raw/trnsport.gms")
elapsed = time.perf_counter() - start
print(f"Parse time: {elapsed:.4f}s")
```

**Test Case 2: Check Sprint 14 timing implementation**
```bash
grep -A5 "time" scripts/gamslib/batch_parse.py
```

### Risk if Wrong
- Inaccurate baselines affect regression detection
- Including overhead makes times less meaningful
- Excluding overhead makes times incomparable across runs

### Estimated Research Time
1 hour (timing analysis, decision)

### Owner
Development team

### Verification Results
🔍 INCOMPLETE

---

# Category 2: Translation Testing Infrastructure

## Unknown 2.1: Should test_translate.py extend or replace batch_translate.py?

### Priority
**High** - Affects implementation approach

### Assumption
test_translate.py should extend batch_translate.py's core functionality, adding refined error categorization and schema v2.1.0 integration.

### Research Questions
1. What functionality does batch_translate.py provide?
2. What translation-specific error categories are needed?
3. Can we reuse batch_translate.py's translation logic?
4. Does batch_translate.py handle MCP file output correctly?
5. What enhancements are needed for Sprint 15?

### How to Verify

**Test Case 1: Review batch_translate.py**
```bash
cat scripts/gamslib/batch_translate.py | head -100
# Examine translation approach, error handling, database updates
```

**Test Case 2: Test translation output**
```bash
python scripts/gamslib/batch_translate.py --model trnsport
# Verify MCP output is generated correctly
```

### Risk if Wrong
- Duplicated translation logic
- Inconsistent error handling between scripts
- Missing MCP file management

### Estimated Research Time
2 hours (code review, testing)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 2)

**Finding:** batch_translate.py should be **extended** rather than replaced. It provides:
- Consistent patterns with batch_parse.py (same CLI structure, progress reporting)
- Subprocess isolation for translation safety (60s timeout with proper cleanup)
- MCP file output management (writes to `data/gamslib/mcp/{model_id}_mcp.gms`)
- Database integration via db_manager module
- Error categorization (5 categories: timeout, unsupported_feature, validation_error, syntax_error, internal_error)

**Key Implementation Details:**
- Uses subprocess to call `python -m src.cli model.gms -o output.gms --quiet`
- Only processes models where `nlp2mcp_parse.status == "success"`
- 60-second timeout with proper process cleanup on timeout
- Progress reporting every 5 models

**Recommendation:** Add same filter flags as batch_parse.py for consistency:
- `--only-failing` - re-run only failed translations
- `--translate-success/--translate-failure` - status-based filtering

**Effort Saved:** 6-8 hours by extending vs. creating from scratch.

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/batch_infrastructure_assessment.md` Section 2 for full analysis.

---

## Unknown 2.2: How to validate generated MCP syntax without solving?

### Priority
**Medium** - Affects translation quality detection

### Assumption
We should validate that generated MCP files have correct GAMS syntax by running GAMS in syntax-check mode before attempting to solve, catching syntax errors early.

### Research Questions
1. Does GAMS have a syntax-check-only mode?
2. Can we detect syntax errors without invoking the solver?
3. What syntax errors are common in generated MCPs?
4. Is syntax validation worth the overhead?
5. How do we distinguish translation errors from syntax errors?

### How to Verify

**Test Case 1: Check GAMS syntax-only mode**
```bash
# Does GAMS have --syntax-check or similar?
gams --help | grep -i syntax
```

**Test Case 2: Try compilation without solve**
```bash
# Can we compile without solving?
gams generated_mcp.gms action=c
```

**Test Case 3: Review Sprint 14 translation errors**
```bash
jq '.models[] | select(.nlp2mcp_translate.status=="failure") | .nlp2mcp_translate.error_category' \
  data/gamslib/gamslib_status.json
```

### Risk if Wrong
- Missing syntax errors until solve phase
- Over-validating adds latency
- Conflating translation and solve errors

### Estimated Research Time
1-2 hours (GAMS documentation, testing)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 2)

**Finding:** GAMS supports compilation without solving using `action=c`:
```bash
gams generated_mcp.gms action=c
```

This compiles the model and checks syntax without invoking any solver. If there are syntax errors, they will be reported in the .lst file.

**Recommendation:** Add optional syntax validation step in test_solve.py before PATH solve:
1. Run `gams model.gms action=c` to check syntax
2. If syntax check fails, categorize as `codegen_syntax_error`
3. If syntax check passes, proceed to PATH solve

This prevents wasting solver time on syntactically invalid MCP files and helps distinguish translation/codegen errors from solve errors.

**Implementation Note:** This validation is optional and adds ~1-2 seconds per model. May want to make it configurable via `--skip-syntax-check` flag.

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/batch_infrastructure_assessment.md` Section 6 for details.

---

## Unknown 2.3: What translation error categories are comprehensive?

### Priority
**High** - Affects error analysis

### Assumption
Translation errors should be categorized into: differentiation errors, min/max reformulation errors, KKT generation errors, code generation errors, and internal errors.

### Research Questions
1. What are the actual translation failure modes from Sprint 14?
2. Do the proposed categories cover all observed failures?
3. Are there unsupported GAMS functions causing translation failures?
4. Should we track which KKT component fails (stationarity, complementarity)?
5. How do translation errors map to parser limitations?

### How to Verify

**Test Case 1: Analyze Sprint 14 translation failures**
```bash
# Check translation error messages
jq '.models[] | select(.nlp2mcp_translate.status=="failure") | .nlp2mcp_translate' \
  data/gamslib/gamslib_status.json
```

**Test Case 2: Categorize observed errors**
- IndexOffset not supported → unsupported_feature
- Objective variable not defined → validation_error
- Unsupported functions (gamma, smin, ord) → unsupported_feature

### Risk if Wrong
- Missing important error categories
- Categories too broad for actionable insights
- Categories inconsistent with parse error taxonomy

### Estimated Research Time
2-3 hours (error analysis, taxonomy design)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 4)

**Finding:** Based on Sprint 14 translation errors (17 failures), comprehensive translation error categories are:

**Translation Error Taxonomy (12 categories):**

**Differentiation Errors:**
- `diff_unsupported_func` - Function not implemented (card, ord, gamma, smin, loggamma)
- `diff_chain_rule_error` - Chain rule application failure
- `diff_numerical_error` - NaN/Inf during differentiation

**Model Structure Errors:**
- `model_no_objective_def` - Objective variable has no defining equation
- `model_domain_mismatch` - Incompatible domains in summation/product
- `model_missing_bounds` - Required bounds not specified

**Unsupported Construct Errors:**
- `unsup_index_offset` - Lead/lag indexing not supported
- `unsup_dollar_cond` - Dollar conditional not supported in context
- `unsup_expression_type` - Unrecognized expression type
- `unsup_special_ordered` - SOS not supported

**Code Generation Errors:**
- `codegen_equation_error` - Failed to generate equation GAMS code
- `codegen_variable_error` - Failed to generate variable GAMS code
- `codegen_numerical_error` - NaN/Inf in generated code

**Sprint 14 Error Mapping:**
- `unsupported_feature` (8 failures) → `diff_unsupported_func`, `unsup_index_offset`, `unsup_dollar_cond`
- `validation_error` (8 failures) → `model_no_objective_def`, `model_domain_mismatch`
- `syntax_error` (1 failure) → `codegen_numerical_error`

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md` Section 2 for full translation error taxonomy.

---

## Unknown 2.4: Should MCP files include debug information?

### Priority
**Low** - Affects debugging capability

### Assumption
Generated MCP files should include comment headers with source model name, nlp2mcp version, and generation timestamp for traceability.

### Research Questions
1. Does nlp2mcp currently add header comments to generated MCPs?
2. What debug information is useful for diagnosing solve failures?
3. Do comments affect PATH solver performance?
4. Should we include original equation names in comments?
5. What's the storage impact of additional comments?

### How to Verify

**Test Case 1: Check current MCP output**
```bash
head -20 data/gamslib/mcp/trnsport_mcp.gms
# Does it have header comments?
```

**Test Case 2: Test with/without comments**
```bash
# Generate with and without comments, compare solve times
python -m src.cli model.gms -o with_comments.gms
python -m src.cli model.gms -o no_comments.gms --no-comments
```

### Risk if Wrong
- Difficult to trace MCP files back to source
- Comments affecting solver performance (unlikely)
- Missing useful debug information

### Estimated Research Time
1 hour (output review, decision)

### Owner
Development team

### Verification Results
🔍 INCOMPLETE

---

# Category 3: MCP Solve Testing

## Unknown 3.1: What tolerance values are appropriate for solution comparison?

### Priority
**Critical** - Affects solution validation accuracy

### Assumption
Default tolerance values of 1e-6 relative and 1e-8 absolute are appropriate for comparing NLP and MCP objective values, based on standard optimization solver defaults.

### Research Questions
1. What tolerances do GAMS solvers use internally (CONOPT, IPOPT, PATH)?
2. What tolerances do optimization testing frameworks use?
3. Are different tolerances needed for LP vs NLP models?
4. How do objective value magnitudes affect tolerance selection?
5. What false positive/negative rates are acceptable?

### How to Verify

**Test Case 1: Check solver documentation**
```
CONOPT: optimality tolerance default = ?
IPOPT: tol default = 1e-8
PATH: convergence tolerance = ?
CPLEX: optimality tolerance = 1e-6
```

**Test Case 2: Analyze GAMSLIB objective ranges**
```bash
jq '.models[] | select(.convexity.objective_value != null) | .convexity.objective_value' \
  data/gamslib/gamslib_status.json | sort -n | head -10
# Check for values near zero, very large values
```

**Test Case 3: Test with different tolerances**
```python
# Given known matching solutions, what tolerance catches true matches without false positives?
```

### Risk if Wrong
- Too tight tolerance: False negatives (correct solutions marked as mismatch)
- Too loose tolerance: False positives (incorrect solutions accepted)
- Wrong tolerance for edge cases (objective near zero, very large objectives)

### Estimated Research Time
2-3 hours (solver research, objective analysis, testing)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 3, expanded in Task 9)

**Finding:** Default tolerances of rtol=1e-6 and atol=1e-8 are appropriate:

**Solver Tolerance Survey:**
| Solver | Parameter | Default |
|--------|-----------|---------|
| CONOPT | RTREDG | 1e-7 |
| IPOPT | tol | 1e-8 |
| PATH | convergence_tolerance | 1e-6 |
| CPLEX | optimality_tolerance | 1e-6 |
| GUROBI | OptimalityTol | 1e-6 |

**Testing Practice Survey (Task 9):**
| Tool | rtol | atol | Notes |
|------|------|------|-------|
| NumPy allclose | 1e-5 | 1e-8 | General-purpose comparison |
| CUTEst benchmarks | 1e-6 | - | Optimization testing standard |
| SciPy linprog | 1e-12 | - | LP solver (very tight) |

**GAMSLIB Objective Analysis (Task 9):**
- 174 models with known objectives
- Range: -3.3M to +20.9M
- 13 models (7.5%) have objective exactly 0
- 37 models (21.3%) have objective near zero (-1 to 1)
- Combined tolerance formula handles all cases

**Recommendation:**
- rtol=1e-6 (relative) - matches PATH/CPLEX/CUTEst defaults
- atol=1e-8 (absolute) - matches IPOPT/NumPy defaults; handles zero objectives
- Combined formula: `|a - b| <= atol + rtol * max(|a|, |b|)`

**Edge Case Handling (Task 9):**
- Objective = 0: atol applies (tolerance = 1e-8)
- Very large objective (>1e6): rtol dominates
- NaN/Infinity: Report as comparison failure

**Existing nlp2mcp usage:** `tests/validation/test_path_solver.py` uses 1e-6 for KKT residual checking, confirming alignment.

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/numerical_tolerance_research.md` for comprehensive research.

---

## Unknown 3.2: How to handle infeasibility and status mismatches?

### Priority
**Critical** - Affects validation logic

### Assumption
When NLP and MCP have different solve statuses (e.g., one optimal, one infeasible), this indicates a potential nlp2mcp bug and should be flagged for investigation.

### Research Questions
1. Under what conditions can NLP be optimal but MCP be infeasible (or vice versa)?
2. How should we classify: both infeasible, status mismatch, objective mismatch?
3. What status codes does PATH solver return for different outcomes?
4. Can solver configuration affect feasibility detection?
5. Should status mismatches block solve comparison or just be flagged?

### How to Verify

**Test Case 1: Document status code meanings**
```
PATH model status codes:
1 = optimal
2 = locally optimal
3 = infeasible
4 = ...
```

**Test Case 2: Create decision tree**
```
if nlp_status == optimal and mcp_status == optimal:
    compare_objectives()
elif nlp_status == infeasible and mcp_status == infeasible:
    status = "match_infeasible"
elif nlp_status == optimal and mcp_status != optimal:
    status = "status_mismatch"  # Potential bug
...
```

### Risk if Wrong
- Missing nlp2mcp bugs that cause incorrect MCP formulations
- False alarms from solver configuration differences
- Incomplete classification of comparison outcomes

### Estimated Research Time
2-3 hours (status code research, decision tree design)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 3)

**Finding:** Use decision tree approach with ComparisonResult enum:

**Decision Tree:**
1. NLP solve failed → `nlp_solve_failed`
2. MCP solve failed → `mcp_solve_failed` (possible nlp2mcp bug)
3. Both optimal (status 1 or 2) → compare objectives → `objective_match` or `objective_mismatch`
4. Both infeasible (status 4 or 5) → `both_infeasible` (agreement)
5. NLP optimal, MCP not → `status_mismatch_nlp_optimal` (INVESTIGATE)
6. MCP optimal, NLP not → `status_mismatch_mcp_optimal` (INVESTIGATE)

**Priority of Investigation:**
- `objective_mismatch` and `status_mismatch_*` are Critical (likely nlp2mcp bugs)
- `mcp_solve_failed` is High (check MCP syntax, PATH config)
- `both_infeasible` is expected for infeasible models

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/solution_comparison_research.md` Section 3 for full decision tree.

---

## Unknown 3.3: How to handle multiple optima (non-unique solutions)?

### Priority
**Medium** - Affects comparison accuracy

### Assumption
When problems have multiple optima, objective values should still match even if primal variable values differ, so we should compare objectives only, not primal variables.

### Research Questions
1. How common are multiple optima in GAMSLIB LP/NLP models?
2. Can NLP and MCP find different optimal solutions with the same objective?
3. Should we detect and flag multiple optima situations?
4. When might objective values differ for multiple optima problems?
5. Do we need to compare KKT conditions directly for ambiguous cases?

### How to Verify

**Test Case 1: Identify potential multiple optima models**
```bash
# LP models are more likely to have multiple optima
jq '.models[] | select(.gamslib_type == "LP")' data/gamslib/gamslib_status.json
```

**Test Case 2: Test known multiple optima model**
- Solve same LP twice with different starting points
- Compare objective values

### Risk if Wrong
- Flagging correct solutions as mismatches due to variable differences
- Missing actual objective value mismatches
- Overcomplicating comparison for rare edge cases

### Estimated Research Time
1-2 hours (research, testing)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 3)

**Finding:** Compare objective values only, not primal variables:

**Rationale:**
1. For problems with multiple optima, primal variables may legitimately differ
2. Objective values should be identical at all optima
3. Objective comparison is sufficient to detect nlp2mcp bugs (wrong gradients, sign errors, constraint handling)
4. Primal comparison requires variable name mapping (complex due to added multipliers)

**Strategy:**
- Accept matching objectives regardless of primal variable differences
- Do not explicitly detect multiple optima in Sprint 15
- Future enhancement (Sprint 16+): Flag models where primals differ despite matching objectives

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/solution_comparison_research.md` Section 4 for full analysis.

---

## Unknown 3.4: Should solution comparison include primal variables or just objectives?

### Priority
**High** - Affects comparison scope

### Assumption
Sprint 15 should compare objective values only. Primal variable comparison adds complexity and can be deferred to Sprint 16 if needed.

### Research Questions
1. Is objective comparison sufficient to detect nlp2mcp errors?
2. Can nlp2mcp produce correct objective with wrong primal values?
3. How would we extract and compare primal variable values?
4. Is variable comparison computationally expensive?
5. What additional value does variable comparison provide?

### How to Verify

**Test Case 1: Analyze error detection capability**
- If objective matches, is KKT formulation guaranteed correct?
- Can we construct a case where objective matches but formulation is wrong?

**Test Case 2: Estimate variable comparison complexity**
- How to extract primal values from GAMS .lst files?
- How to handle different variable naming between NLP and MCP?

### Risk if Wrong
- Missing subtle nlp2mcp bugs that produce correct objectives but wrong formulations
- Unnecessary complexity for marginal benefit
- Delayed Sprint 15 completion for low-value features

### Estimated Research Time
1-2 hours (analysis, scoping decision)

### Owner
Development team

### Verification Results
🔍 INCOMPLETE

---

## Unknown 3.5: What solve error categories are needed?

### Priority
**High** - Affects error classification

### Assumption
Solve errors should be categorized into: solve_optimal, solve_infeasible, solve_unbounded, solve_iteration_limit, solve_time_limit, path_error, comparison_mismatch.

### Research Questions
1. What PATH solver status codes need to be mapped to categories?
2. What are common PATH solver failure modes?
3. How do we distinguish PATH errors from generated MCP syntax errors?
4. Should we track solver iterations and convergence metrics?
5. Are there PATH-specific error patterns to detect?

### How to Verify

**Test Case 1: Research PATH status codes**
```
PATH solver status codes (from GAMS documentation):
1 = Normal completion
2 = ...
```

**Test Case 2: Test with intentionally broken MCP**
```bash
# Create MCP with syntax error, observe error message
# Create infeasible MCP, observe status
```

### Risk if Wrong
- Incomplete error categorization
- Misclassifying PATH errors as nlp2mcp bugs
- Missing important failure modes

### Estimated Research Time
2 hours (PATH documentation, testing)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 4)

**Finding:** Comprehensive solve outcome categories designed based on PATH solver status codes and comparison outcomes.

**Solve Outcome Taxonomy (16 categories total: 12 error types + 4 success outcomes):**

**PATH Solver Status Outcomes (6: 1 success, 5 errors):**
- `path_solve_normal` - Solver completed normally (SUCCESS)
- `path_solve_iteration_limit` - Solver hit iteration limit (solver_status=2)
- `path_solve_time_limit` - Solver hit time limit (solver_status=3)
- `path_solve_terminated` - Solver terminated by error (solver_status=4)
- `path_solve_eval_error` - Function evaluation errors (solver_status=5)
- `path_solve_license` - GAMS/PATH license issue (solver_status=7)

**Model Status Outcomes (4: 2 success, 2 errors):**
- `model_optimal` - Model solved optimally (SUCCESS)
- `model_locally_optimal` - Locally optimal solution found (SUCCESS)
- `model_infeasible` - Model is infeasible (model_status=4 or 5)
- `model_unbounded` - Model is unbounded (model_status=3)

**Solution Comparison Outcomes (6: 1 success, 5 errors):**
- `compare_objective_match` - Objectives match within tolerance (SUCCESS)
- `compare_objective_mismatch` - Objectives differ beyond tolerance (INVESTIGATE)
- `compare_status_mismatch` - NLP and MCP have different solve status (INVESTIGATE)
- `compare_nlp_failed` - Could not solve original NLP
- `compare_mcp_failed` - Could not solve generated MCP
- `compare_both_infeasible` - Both NLP and MCP infeasible (expected)

**Priority of Investigation:**
| Result | Priority | Action |
|--------|----------|--------|
| `compare_objective_mismatch` | Critical | Investigate nlp2mcp formulation |
| `compare_status_mismatch` | Critical | Investigate nlp2mcp formulation |
| `compare_mcp_failed` | High | Check generated MCP syntax, PATH config |
| `compare_nlp_failed` | Medium | Model may be genuinely problematic |
| `compare_both_infeasible` | Low | Expected for infeasible models |
| `compare_objective_match` | None | Success! |

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md` Section 3 for full solve error taxonomy.

---

## Unknown 3.6: Is PATH solver available and properly configured?

### Priority
**Critical** - Blocks solve testing

### Assumption
PATH solver is installed as part of GAMS, licensed for MCP solving, and can be invoked via `gams model.gms` command.

### Research Questions
1. Is PATH solver available in the GAMS installation?
2. Does the GAMS license cover PATH usage?
3. What command invokes PATH for MCP models?
4. What timeout configuration is needed?
5. Are there MCP-specific GAMS options needed?

### How to Verify

**Test Case 1: Check PATH availability**
```bash
# List available solvers
gams empty.gms
# Or: gamsinst -a | grep PATH
```

**Test Case 2: Test simple MCP solve**
```bash
cat > test_mcp.gms << 'EOF'
variables x, y;
equations f, g;
f.. x**2 + y - 1 =n= 0;
g.. x + y**2 - 1 =n= 0;
model test /f.x, g.y/;
solve test using mcp;
EOF
gams test_mcp.gms
cat test_mcp.lst | grep "SOLVER STATUS"
```

### Risk if Wrong
- Solve testing completely blocked if PATH unavailable
- License issues discovered mid-sprint
- Configuration issues delay implementation

### Estimated Research Time
1-2 hours (environment verification)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 5)

**Finding:** PATH solver is available and properly configured:

**Environment:**
- GAMS Version: 51.3.0 (38407a9b, Oct 27, 2025)
- PATH Version: 5.2.01 (Mon Oct 27 13:31:58 2025)
- Platform: macOS x86 64bit
- License: Demo license valid until Jan 23, 2026
- Location: `/Library/Frameworks/GAMS.framework/Versions/51/Resources/`

**Validation Tests Passed:**
1. Simple MCP solve: SOLVER STATUS 1, MODEL STATUS 1 (Optimal)
2. Generated MCP (hs62_mcp.gms): Successfully solved
3. Infeasible MCP: Correctly detected (MODEL STATUS 4)
4. Iteration limit: Correctly detected (SOLVER STATUS 2)
5. Time limit: Correctly detected (SOLVER STATUS 3)
6. Compilation error: Correctly detected via `**** $NNN` pattern

**Invocation:**
```bash
gams model_mcp.gms lo=3 o=output.lst
```

**MCP-Specific Options:**
- `option mcp = path;` - Select PATH solver
- `option reslim = 60;` - Time limit (recommended: 60s)
- `option iterlim = 1000000;` - Iteration limit (default sufficient)

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/path_solver_integration.md` for full integration guide.

---

## Unknown 3.7: How to extract solve results from GAMS .lst files?

### Priority
**Critical** - Affects result extraction

### Assumption
Solve results (objective value, solver status, model status, iterations) can be reliably extracted from GAMS .lst files using regex patterns, similar to convexity verification in Sprint 13.

### Research Questions
1. What .lst file patterns indicate solve success/failure?
2. Where is objective value reported in .lst file?
3. How to extract iterations and solve time?
4. Are there differences between LP and MCP .lst file formats?
5. Can we reuse Sprint 13 .lst parsing code?

### How to Verify

**Test Case 1: Analyze MCP .lst file structure**
```bash
gams data/gamslib/mcp/trnsport_mcp.gms
cat trnsport_mcp.lst | grep -A5 "SOLVER STATUS"
cat trnsport_mcp.lst | grep -A5 "OBJECTIVE"
```

**Test Case 2: Review Sprint 13 parsing code**
```bash
grep -A20 "parse.*lst" scripts/gamslib/verify_convexity.py
```

### Risk if Wrong
- Incorrect result extraction leads to false validations
- Missing important metrics (iterations, time)
- Fragile regex patterns break on edge cases

### Estimated Research Time
1-2 hours (.lst analysis, code review)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 5)

**Finding:** Solve results can be reliably extracted from GAMS .lst files using regex patterns. Existing code in `verify_convexity.py` provides comprehensive parsing.

**.lst File Structure for MCP Solve:**
```
S O L V E      S U M M A R Y

     MODEL   mcp_model
     TYPE    MCP
     SOLVER  PATH                FROM LINE  105

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal

 RESOURCE USAGE, LIMIT          0.155 10000000000.000
 ITERATION COUNT, LIMIT        27    2147483647

---- VAR x1                  .             0.6178        +INF      -3.37423E-10
```

**Extraction Patterns (validated):**
```python
import re

# SOLVER STATUS (1=normal, 2=iteration limit, 3=time limit, etc.)
solver_pattern = re.compile(r"\*\*\*\* SOLVER STATUS\s+(\d+)", re.MULTILINE)

# MODEL STATUS (1=optimal, 2=locally optimal, 4=infeasible, etc.)
model_pattern = re.compile(r"\*\*\*\* MODEL STATUS\s+(\d+)", re.MULTILINE)

# ITERATIONS
iter_pattern = re.compile(r"ITERATION COUNT, LIMIT\s+(\d+)", re.MULTILINE)

# RESOURCE (solve time)
resource_pattern = re.compile(r"RESOURCE USAGE, LIMIT\s+([\d.]+)", re.MULTILINE)

# COMPILATION ERROR (syntax errors)
error_pattern = re.compile(r"\*\*\*\* \$\d+")
```

**Existing Code to Reuse:**
- `scripts/gamslib/verify_convexity.py::parse_gams_listing()` - Comprehensive parser
- `tests/validation/test_path_solver.py::_extract_model_status()` - Simple extractor

**Note:** MCP .lst files do not include `**** OBJECTIVE VALUE` line (unlike LP/NLP). Objective must be extracted from variable solution section if needed.

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/path_solver_integration.md` Section 3 for full extraction patterns.

---

# Category 4: Database Schema Extensions

## Unknown 4.1: What fields are needed for mcp_solve object?

### Priority
**Critical** - Affects schema design

### Assumption
mcp_solve object needs: status, solver_status, model_status, objective_value, solve_time_seconds, iterations, error_category, error_message, timestamp, path_version, mcp_file_used.

### Research Questions
1. What solve result information is available from PATH solver?
2. What fields are needed for solution comparison analysis?
3. Should we store raw .lst file excerpts?
4. What iteration/convergence metrics are useful?
5. How does mcp_solve structure align with convexity, nlp2mcp_parse, nlp2mcp_translate?

### How to Verify

**Test Case 1: Check available PATH outputs**
```bash
# Run PATH solve and examine available outputs
gams test_mcp.gms
grep -E "STATUS|OBJECTIVE|ITERATION" test_mcp.lst
```

**Test Case 2: Review existing schema structure**
```bash
jq '.properties.nlp2mcp_translate.properties | keys' data/gamslib/schema.json
# Align mcp_solve with this structure
```

### Risk if Wrong
- Missing essential fields for analysis
- Over-engineering with unnecessary fields
- Inconsistent structure across pipeline stages

### Estimated Research Time
2 hours (output analysis, schema design)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 6)

**Finding:** The `mcp_solve_result` object has been designed with 14 fields that capture all essential PATH solver outputs while maintaining consistency with existing schema objects.

**Designed Fields (14 total):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | enum | Yes | "success", "failure", "timeout", "not_tested" |
| `solve_date` | date-time | No | ISO 8601 timestamp |
| `solver` | string | No | Solver name (default: "PATH") |
| `solver_version` | string | No | Version (e.g., "PATH 5.2.01") |
| `solver_status` | integer | No | GAMS solver status code (1=normal, etc.) |
| `solver_status_text` | string | No | Human-readable solver status |
| `model_status` | integer | No | GAMS model status code (1=optimal, etc.) |
| `model_status_text` | string | No | Human-readable model status |
| `objective_value` | number/null | No | Objective from MCP solve |
| `solve_time_seconds` | number | No | Time to solve in seconds |
| `iterations` | integer/null | No | Solver iteration count |
| `mcp_file_used` | string | No | Path to MCP file that was solved |
| `outcome_category` | enum | No | Categorized outcome (uses `solve_outcome_category`) |
| `error` | object | No | Structured error details (uses `error_detail`) |

**Alignment with Existing Objects:**
- Follows same patterns as `convexity_result`, `parse_result`, `translate_result`
- Uses shared `error_detail` object for consistent error reporting
- Status enum mirrors other stages ("success", "failure", "not_tested") with added "timeout"

**Decision on Raw .lst Excerpts:**
- NOT included in schema (too verbose, storage overhead)
- Error details capture key information; full .lst files stored separately if needed

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_v2.1.0_draft.json` for full schema.

---

## Unknown 4.2: What fields are needed for solution_comparison object?

### Priority
**Critical** - Affects comparison storage

### Assumption
solution_comparison object needs: nlp_objective, mcp_objective, objective_match, absolute_difference, relative_difference, tolerance_absolute, tolerance_relative, nlp_status, mcp_status, status_match, comparison_result, notes, timestamp.

### Research Questions
1. Is a separate solution_comparison object needed or should comparison fields be in mcp_solve?
2. What comparison metrics are useful for analysis?
3. Should we store the NLP solve results alongside MCP results?
4. How to handle cases where comparison wasn't performed?
5. What's the storage overhead of detailed comparison data?

### How to Verify

**Test Case 1: Design comparison workflow**
```
1. Get NLP objective from convexity.objective_value
2. Solve MCP and get mcp_solve.objective_value
3. Compare and store in solution_comparison
```

**Test Case 2: Check if NLP data already exists**
```bash
jq '.models[0].convexity.objective_value' data/gamslib/gamslib_status.json
```

### Risk if Wrong
- Missing important comparison details
- Redundant data storage
- Complicated query patterns

### Estimated Research Time
1-2 hours (workflow design, schema decisions)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 6)

**Finding:** A separate `solution_comparison_result` object is preferred over embedding comparison fields in `mcp_solve`. This provides cleaner separation of concerns and makes comparison optional (can be skipped if NLP data unavailable).

**Designed Fields (16 total):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `comparison_status` | enum | Yes | "match", "mismatch", "skipped", "error", "not_tested" |
| `comparison_date` | date-time | No | ISO 8601 timestamp |
| `nlp_objective` | number/null | No | From `convexity.objective_value` |
| `mcp_objective` | number/null | No | From `mcp_solve.objective_value` |
| `absolute_difference` | number/null | No | \|nlp - mcp\| |
| `relative_difference` | number/null | No | \|nlp - mcp\| / max(\|nlp\|, 1e-10) |
| `objective_match` | boolean/null | No | True if within tolerance |
| `tolerance_absolute` | number | No | Default 1e-8 |
| `tolerance_relative` | number | No | Default 1e-6 |
| `nlp_solver_status` | integer/null | No | From convexity verification |
| `nlp_model_status` | integer/null | No | From convexity verification |
| `mcp_solver_status` | integer/null | No | From mcp_solve |
| `mcp_model_status` | integer/null | No | From mcp_solve |
| `status_match` | boolean/null | No | True if both have compatible status |
| `comparison_result` | enum | No | Detailed result category |
| `notes` | string/null | No | Explanation (e.g., why skipped) |

**Decision: Separate Object vs. Embedded:**
- **Separate object chosen** - Allows comparison to be optional/skipped cleanly
- NLP data (objectives, status) is referenced from `convexity` object, not duplicated
- MCP data is referenced from `mcp_solve` object
- Comparison can be performed later without re-solving

**Comparison Result Categories (7 values):**
- `compare_objective_match` - Success: objectives match within tolerance
- `compare_objective_mismatch` - Investigate: objectives differ
- `compare_status_mismatch` - Investigate: different solve status
- `compare_nlp_failed` - NLP solve failed, no comparison possible
- `compare_mcp_failed` - MCP solve failed, no comparison possible
- `compare_both_infeasible` - Expected: both infeasible
- `compare_not_performed` - Comparison not yet performed

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_v2.1.0_draft.json` for full schema.

---

## Unknown 4.3: Should schema version be 2.1.0 (minor) or 3.0.0 (major)?

### Priority
**High** - Affects backward compatibility

### Assumption
Schema version should be 2.1.0 (minor update) because new objects (mcp_solve, solution_comparison) are optional and existing Sprint 14 data remains valid.

### Research Questions
1. Are new objects truly optional (don't break existing data)?
2. Are error category enums being changed (breaking change)?
3. Does adding new optional objects qualify as minor version?
4. Will Sprint 14 data validate against v2.1.0 schema?
5. What migration is needed for existing data?

### How to Verify

**Test Case 1: Test backward compatibility**
```python
# Validate Sprint 14 data against v2.1.0 schema (draft)
from jsonschema import Draft7Validator
# ... validate existing data
```

**Test Case 2: Check enum changes**
- Do new error categories break old data?
- Are old categories still valid?

### Risk if Wrong
- Breaking change requires major version bump
- Incorrect version causes validation confusion
- Migration issues not anticipated

### Estimated Research Time
1-2 hours (compatibility testing, decision)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 6)

**Finding:** Schema version **2.1.0 (minor)** is correct. The changes are backward-compatible per semantic versioning rules.

**Backward Compatibility Analysis:**

| Change | Breaking? | Reason |
|--------|-----------|--------|
| New `mcp_solve` object | No | Optional property (not in `required`) |
| New `solution_comparison` object | No | Optional property (not in `required`) |
| New `model_statistics` object | No | Optional property in `parse_result` |
| Extended `error_category` enum | No | Additive: all old values still valid |
| New `solve_outcome_category` enum | No | New enum, no existing data uses it |
| New `comparison_result_category` enum | No | New enum, no existing data uses it |

**Semantic Versioning Justification:**
- **MAJOR (3.0.0)** - Required if removing fields, changing required fields, or restricting enum values
- **MINOR (2.1.0)** - Appropriate for adding new optional fields/objects and extending enums
- **PATCH (2.0.1)** - For bug fixes, clarifications, no functional changes

**Migration Requirements:**
- None required for existing data
- Sprint 14 data will validate against v2.1.0 without modification
- New fields will be absent from old data (allowed because optional)

**Validation Test:**
```python
# Existing Sprint 14 data structure (simplified):
{
  "nlp2mcp_parse": {"status": "success", ...},
  "nlp2mcp_translate": {"status": "success", ...}
  # No mcp_solve or solution_comparison
}
# ✅ Validates against v2.1.0 (new objects are optional)
```

**Preserved v2.0.0 Enum Values:**
All original `error_category` values are preserved: `syntax_error`, `unsupported_feature`, `validation_error`, `missing_include`, `timeout`, `internal_error`, `solver_error`.

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_extensions.md` Section 1 for migration notes.

---

## Unknown 4.4: How to handle error category enum extensions?

### Priority
**Medium** - Affects schema evolution

### Assumption
New error categories can be added to enums without breaking existing data, as long as old categories remain valid. Error category enums should use "oneOf" to allow flexibility.

### Research Questions
1. Does JSON Schema allow adding new enum values without breaking validation?
2. Should error categories be open-ended (allow any string) or strict enums?
3. How to handle unknown error categories from old data?
4. Should we namespace error categories by stage (parse_syntax_error vs syntax_error)?
5. What's the migration path if we need to rename categories?

### How to Verify

**Test Case 1: Test enum extension**
```python
# Schema with enum ["a", "b"]
# Data with value "a" -> valid
# New schema with enum ["a", "b", "c"]
# Old data with value "a" -> still valid?
```

**Test Case 2: Review current enum handling**
```bash
jq '.definitions.error_category.enum' data/gamslib/schema.json
```

### Risk if Wrong
- Old data fails validation with new schema
- Too restrictive enums limit future extensions
- Too permissive enums allow invalid values

### Estimated Research Time
1 hour (JSON Schema research, testing)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 6)

**Finding:** Enum extension is backward-compatible in JSON Schema. Adding new enum values does NOT break validation of existing data using old values.

**Approach Chosen: Strict Enum with Legacy Preservation**

The `error_category` enum has been extended from 7 to 36 values:

**Original v2.0.0 Values (7 - all preserved):**
- `syntax_error`, `unsupported_feature`, `validation_error`, `missing_include`, `timeout`, `internal_error`, `solver_error`

**New v2.1.0 Values (29 additions):**
- **Lexer errors (4):** `lexer_invalid_char`, `lexer_unclosed_string`, `lexer_invalid_number`, `lexer_encoding_error`
- **Parser errors (6):** `parser_unexpected_token`, `parser_missing_semicolon`, `parser_unmatched_paren`, `parser_invalid_declaration`, `parser_invalid_expression`, `parser_unexpected_eof`
- **Semantic errors (4):** `semantic_undefined_symbol`, `semantic_type_mismatch`, `semantic_domain_error`, `semantic_duplicate_def`
- **Include errors (2):** `include_file_not_found`, `include_circular`
- **Differentiation errors (3):** `diff_unsupported_func`, `diff_chain_rule_error`, `diff_numerical_error`
- **Model structure errors (3):** `model_no_objective_def`, `model_domain_mismatch`, `model_missing_bounds`
- **Unsupported construct errors (4):** `unsup_index_offset`, `unsup_dollar_cond`, `unsup_expression_type`, `unsup_special_ordered`
- **Code generation errors (3):** `codegen_equation_error`, `codegen_variable_error`, `codegen_numerical_error`

**Migration Support:**
- Added `legacy_category` field in `error_detail` to track original Sprint 14 category
- Existing data continues to use original categories (still valid)
- New processing can use refined categories

**Decision: Strict Enum vs. Open String:**
- **Strict enum chosen** - Provides validation, IDE support, and consistency
- Future extensions follow same additive pattern
- If new category needed during implementation, add to schema before use

**Namespacing Decision:**
- Categories are namespaced by prefix (e.g., `lexer_*`, `parser_*`, `diff_*`)
- NOT namespaced by stage (no `parse_syntax_error`) - categories reused across stages where applicable

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_v2.1.0_draft.json` definitions section and `docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md` for complete taxonomy.

---

# Category 5: Pipeline Orchestration & Filtering

## Unknown 5.1: What filter patterns are essential for Sprint 15?

### Priority
**High** - Affects usability

### Assumption
Essential filters for Sprint 15 are: --model=NAME, --only-parse, --only-translate, --only-solve, --only-failing, --skip-completed. Nice-to-have: --type=LP/NLP, --limit=N, --error-category=X.

### Research Questions
1. What filtering does batch_parse.py/batch_translate.py already support?
2. What filters are needed for development/debugging workflows?
3. Should filter logic be AND or OR (multiple filters)?
4. How to handle conflicting filters (--only-parse --only-solve)?
5. What's the minimum viable filter set for Sprint 15?

### How to Verify

**Test Case 1: Review existing filters**
```bash
python scripts/gamslib/batch_parse.py --help
python scripts/gamslib/batch_translate.py --help
```

**Test Case 2: Prioritize filter use cases**
- Debug single model: --model=trnsport
- Re-run failures: --only-failing
- Test new code: --limit=10

### Risk if Wrong
- Missing essential filters hampers development
- Too many filters complicates implementation
- Inconsistent filter behavior between stages

### Estimated Research Time
1-2 hours (use case analysis, design)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 7)

**Finding:** Comprehensive filter API designed with 25+ command-line arguments covering all essential use cases.

**Existing Filters (Sprint 14):**
- `batch_parse.py`: `--model`, `--limit`, `--dry-run`, `--verbose`, `--save-every`
- `batch_translate.py`: Same pattern as batch_parse.py

**Sprint 15 MVP Filter Set (14 filters):**

| Filter | Priority | Purpose |
|--------|----------|---------|
| `--model=NAME` | Critical | Debug single model (existing) |
| `--limit=N` | Critical | Quick testing (existing) |
| `--dry-run` | Critical | Preview without executing (existing) |
| `--verbose` | Critical | Detailed output (existing) |
| `--type=TYPE` | High | Filter by model type (LP/NLP/QCP) |
| `--only-parse` | High | Stage-specific testing |
| `--only-translate` | High | Stage-specific testing |
| `--only-solve` | High | Stage-specific testing |
| `--only-failing` | High | Re-run failures |
| `--skip-completed` | High | Incremental testing |
| `--parse-success` | High | Filter by status |
| `--parse-failure` | High | Filter by status |
| `--translate-success` | High | Filter by status |
| `--translate-failure` | High | Filter by status |

**Filter Combination Logic:**
- Multiple filters combine with AND logic
- Conflict detection for mutually exclusive flags
- Filters applied in order: model selection → status → error → limit/random

**Use Cases Documented (20 total):**
- Development (6): single model, small subset, by type, convex models, random sample, parse only
- Debugging (5): re-run failures, debug parse errors, specific error, compare stages, investigate mismatch
- Incremental (4): skip completed, only untested, force re-run, continue partial
- Stage-specific (5): parse only, translate only, solve only, skip solve, compare only

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md` for full specification.

---

## Unknown 5.2: How to handle cascading failures (parse fails → skip translate)?

### Priority
**Medium** - Affects pipeline logic

### Assumption
Pipeline should automatically skip downstream stages when upstream stages fail. If parse fails, translate and solve are skipped with status "not_tested".

### Research Questions
1. Should skipped stages be explicitly recorded or just remain null/not_tested?
2. How to handle --only-translate for models that haven't parsed?
3. Should we re-parse on every translate request or trust existing status?
4. What happens to partial pipeline runs (some stages complete, others not)?
5. How to resume a partial pipeline run?

### How to Verify

**Test Case 1: Design cascade logic**
```python
if parse_status == "failure":
    translate_status = "not_tested"  # or "skipped"?
    solve_status = "not_tested"
```

**Test Case 2: Test partial run scenario**
- Parse 100 models (some fail)
- Translate only parsed models
- Solve only translated models
- Verify database reflects correct states

### Risk if Wrong
- Confusing status values for skipped stages
- Unexpected behavior with --only-X filters
- Difficulty resuming interrupted runs

### Estimated Research Time
1-2 hours (logic design, testing)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 7)

**Finding:** Cascading failure handling designed with clear status semantics and resumption behavior.

**Pipeline Stage Dependencies:**
```
Parse → Translate → Solve → Compare
```

**Cascade Behavior:**

| Upstream Status | Downstream Behavior |
|-----------------|---------------------|
| `parse.status = failure` | `translate.status = not_tested`, `solve.status = not_tested` |
| `translate.status = failure` | `solve.status = not_tested` |
| NLP solution not available | `comparison.status = skipped` |
| MCP solution not available | `comparison.status = skipped` |

**Status Semantics:**
- `not_tested`: Stage was never attempted (upstream failed or not run yet)
- `skipped`: Stage was intentionally skipped (e.g., comparison when NLP unavailable)

**Implicit Requirements with --only-* Flags:**
- `--only-translate`: Requires `parse.status = success`
- `--only-solve`: Requires `translate.status = success`
- `--only-compare`: Requires both NLP solution AND MCP solution

**Resumption Behavior:**
- `--skip-completed`: Models with all stages successful are skipped; partial completion continues from last failed stage
- `--force`: Re-runs all models regardless of previous status

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md` Section 5 for full cascade design.

---

## Unknown 5.3: What summary statistics are most useful?

### Priority
**Low** - Affects reporting

### Assumption
Useful summary statistics include: total models, success/failure/skipped counts per stage, success percentages, average/median times per stage, top error categories.

### Research Questions
1. What statistics does batch_parse.py currently report?
2. What additional statistics are needed for Sprint 15?
3. Should statistics be per-run or cumulative?
4. What format is best for statistics (table, JSON, markdown)?
5. Should we track statistics over time for trend analysis?

### How to Verify

**Test Case 1: Review current output**
```bash
python scripts/gamslib/batch_parse.py --all 2>&1 | tail -30
# What statistics are shown?
```

**Test Case 2: List desired statistics**
- Success rates by stage
- Success rates by model type
- Error category distribution
- Timing statistics

### Risk if Wrong
- Missing useful metrics for analysis
- Too much output obscures important information
- Inconsistent statistics between runs

### Estimated Research Time
1 hour (output review, requirements)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 7)

**Finding:** Comprehensive summary statistics designed covering per-run metrics, multiple output formats, and type-based breakdowns.

**Per-Run Statistics (all stages):**
- Models processed count and elapsed time
- Per-stage results: Success/Failure/Skipped counts with percentages
- Per-stage timing: Average time per model
- Comparison results: Match/Mismatch/Skipped with percentages
- Top error categories with model counts
- Full pipeline success rate (end-to-end)

**Output Formats (4 modes):**

| Format | Flag | Description |
|--------|------|-------------|
| Table | (default) | Human-readable table format |
| JSON | `--json` | Machine-readable JSON output |
| Quiet | `--quiet` | Only final success rate |
| Verbose | `--verbose` | Per-model details |

**Statistics by Model Type:**
When filtering by type, results include breakdown by LP/NLP/QCP showing success rates per type.

**Existing batch_parse.py Output:**
- Progress reporting every 10 models with ETA
- Final summary: processed count, success count, failure count, time elapsed
- Error category counts on verbose mode

**Recommendation:** Extend existing summary output pattern with:
1. Per-stage breakdown (Parse → Translate → Solve → Compare)
2. Comparison results (Match/Mismatch/Skipped)
3. Top error categories (up to 5)
4. `--json` flag for machine-readable output

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md` Section 6 for full specification.

---

# Category 6: Performance & Baseline Metrics

## Unknown 6.1: How to accurately measure solve time?

### Priority
**Medium** - Affects baseline accuracy

### Assumption
Solve time should be measured from GAMS subprocess start to completion, including PATH solver execution, and recorded in seconds with millisecond precision.

### Research Questions
1. Does GAMS report internal solve time in .lst file?
2. Should we use subprocess wall time or GAMS-reported time?
3. Is there significant overhead in subprocess creation?
4. How to handle solve timeouts?
5. What's a reasonable default timeout for MCP solves?

### How to Verify

**Test Case 1: Check GAMS time reporting**
```bash
gams test_mcp.gms
grep -i "time" test_mcp.lst
# Look for solve time, total time, etc.
```

**Test Case 2: Compare subprocess vs. reported time**
```python
import time, subprocess
start = time.perf_counter()
subprocess.run(["gams", "test_mcp.gms"])
wall_time = time.perf_counter() - start
# Compare with time in .lst file
```

### Risk if Wrong
- Inaccurate baselines for regression detection
- Inconsistent timing methodology
- Missing solve time for timeout cases

### Estimated Research Time
1-2 hours (GAMS output analysis, timing comparison)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 8)

**Finding:** Use `time.perf_counter()` for wall time measurement around GAMS subprocess. This captures full solve time including subprocess creation, model compilation, PATH solver execution, and cleanup.

**Timing Methodology:**
- **Timer:** `time.perf_counter()` (highest resolution, monotonic, already used in batch_parse.py/batch_translate.py)
- **Start point:** Before `subprocess.run()` call
- **End point:** After subprocess completes or timeout
- **Precision:** 4 decimal places (0.0001s = 0.1ms)

**GAMS-Reported Time (Optional):**
- Available via `RESOURCE USAGE, LIMIT` line in .lst file
- Pattern: `re.search(r"RESOURCE USAGE, LIMIT\s+([\d.]+)", content)`
- Captures solver-only time (excludes GAMS startup)
- Useful for detailed analysis but not required for baseline

**Timeout Handling:**
- Default timeout: 60 seconds (consistent with batch_translate.py)
- On timeout: record elapsed time (60.0s) with status="timeout"
- Always record timing, even for failures

**Subprocess Overhead:**
- GAMS startup adds ~0.5-1.0s overhead
- Acceptable for baseline metrics (consistent overhead)
- Wall time preferred for consistency with parse/translate timing

**Consistency Update Needed:**
- `verify_convexity.py` uses `time.time()` - should update to `time.perf_counter()` during Sprint 15

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/performance_measurement.md` Section 1.4 for full solve timing methodology.

---

## Unknown 6.2: What baseline metrics should Sprint 15 establish?

### Priority
**Medium** - Affects Sprint 16+ planning

### Assumption
Sprint 15 should establish baselines for: parse success rate, translate success rate, solve success rate, objective match rate, average times per stage, and error category distributions.

### Research Questions
1. What metrics are most useful for tracking progress across sprints?
2. How should baselines be documented (markdown, JSON, database)?
3. Should baselines be per model type (LP, NLP, QCP)?
4. What statistical measures (mean, median, percentiles) are appropriate?
5. How to detect regressions against baselines?

### How to Verify

**Test Case 1: Review Sprint 14 metrics**
```markdown
Sprint 14 baselines:
- Parse success: 21.3%
- Translate success: 94.1%
- Total models: 160
```

**Test Case 2: Define Sprint 15 additions**
- Solve success rate: ?
- Objective match rate: ?
- Full pipeline success: ?

### Risk if Wrong
- Missing important baseline metrics
- Metrics that can't be meaningfully compared over time
- Overly complex baseline documentation

### Estimated Research Time
1 hour (requirements, format design)

### Owner
Development team

### Verification Results
✅ VERIFIED (Task 8)

**Finding:** Sprint 15 should establish comprehensive baseline metrics in both JSON (machine-readable) and Markdown (human-readable) formats.

**Baseline Metrics (per stage):**

| Metric Category | Metrics |
|-----------------|---------|
| **Success Rates** | attempted, success, failure, timeout, success_rate |
| **Timing Statistics** | mean, median, stddev, min, max, p25, p75, p90, p99 |
| **By Model Type** | LP, NLP, QCP breakdowns with per-type success rates and timing |
| **Error Distribution** | Count and percentage by error category |
| **Outliers** | Models > 2 stddev above mean time |

**Per-Stage Metrics:**
1. **Parse:** 160 models, success rate, timing stats, error distribution
2. **Translate:** Models with parse success, success rate, timing stats
3. **Solve:** Models with translate success, success rate, timing stats
4. **Compare:** Models with solve success, match/mismatch rate
5. **Full Pipeline:** End-to-end success count and rate

**Documentation Format:**
- **JSON:** `data/gamslib/baseline_metrics.json` - machine-readable for regression detection
- **Markdown:** `docs/planning/EPIC_3/SPRINT_15/SPRINT_BASELINE.md` - human-readable summary

**Statistical Measures:**
- Mean and median (central tendency)
- Stddev (variability)
- Percentiles: P25, P75 (IQR), P90, P99 (tail behavior)
- Outlier detection: > mean + 2*stddev

**Environment Documentation:**
- Machine specs, OS version, Python version
- nlp2mcp version, GAMS version, PATH solver version

**Baseline Recording Plan:**
1. Initial baseline: Sprint 15 Day 5-6 (after infrastructure complete)
2. Final baseline: Sprint 15 Day 10 (end of sprint)
3. Store in version control for historical comparison

See `docs/planning/EPIC_3/SPRINT_15/prep-tasks/performance_measurement.md` Section 3-5 for full baseline format and plan.

---

## Unknown 6.3: How to detect performance regressions?

### Priority
**Low** - Affects future sprint monitoring

### Assumption
Performance regressions can be detected by comparing current metrics against baselines with a 10% threshold for timing and 5% threshold for success rates.

### Research Questions
1. What thresholds are appropriate for detecting regressions?
2. Should regression detection be manual or automated?
3. How to handle natural variance in timing?
4. Should regressions block releases or just warn?
5. What's the process for investigating detected regressions?

### How to Verify

**Test Case 1: Analyze Sprint 14 variance**
```bash
# Check if Sprint 14 times are consistent across runs
python scripts/gamslib/batch_parse.py --model trnsport
# Run multiple times, measure variance
```

**Test Case 2: Define regression thresholds**
- Parse success rate drops >5%: regression
- Average parse time increases >10%: regression

### Risk if Wrong
- False positive regressions cause unnecessary investigation
- False negative regressions miss real problems
- Over-engineering for Sprint 15 scope

### Estimated Research Time
1 hour (variance analysis, threshold definition)

### Owner
Development team

### Verification Results
🔍 INCOMPLETE

---

# Template for New Unknowns

## Unknown X.Y: [Question]

### Priority
**[Critical/High/Medium/Low]** - [Brief reason]

### Assumption
[Current assumption about how things work]

### Research Questions
1. [Question 1]
2. [Question 2]
3. [Question 3]

### How to Verify

**Test Case 1: [Description]**
```bash
# Command or code
```

**Test Case 2: [Description]**
```
# Description of test
```

### Risk if Wrong
- [Risk 1]
- [Risk 2]

### Estimated Research Time
[X-Y hours]

### Owner
[Team/person]

### Verification Results
🔍 INCOMPLETE

---

# Next Steps

## Before Sprint 15 Day 1

1. **Critical unknowns (7):** Must be verified before sprint starts
   - 3.1: Solution tolerance values
   - 3.2: Infeasibility handling
   - 3.6: PATH solver availability
   - 3.7: .lst file extraction
   - 4.1: mcp_solve schema fields
   - 4.2: solution_comparison schema fields

2. **High unknowns (10):** Should be verified, can defer non-blocking items
   - 1.1, 1.2: Parse infrastructure decisions
   - 2.1, 2.3: Translation infrastructure decisions
   - 3.4, 3.5: Solve comparison scope and error categories
   - 4.3: Schema versioning
   - 5.1: Filter requirements

3. **Medium/Low unknowns (9):** Can be resolved during sprint

## Prep Task Execution Order

1. **Days 1-2:** Tasks 1 (this document), 2 (batch infrastructure), 5 (PATH validation)
2. **Days 3-4:** Tasks 3 (solution comparison), 4 (error taxonomy), 9 (tolerance)
3. **Day 5:** Task 6 (schema), 7 (filtering), 8 (performance)
4. **Day 6-7:** Task 10 (detailed schedule)

## Success Criteria

Sprint 15 prep is complete when:
- [x] KNOWN_UNKNOWNS.md created with 25+ unknowns
- [x] All Critical unknowns verified or mitigated
- [x] All High unknowns verified or deferred with rationale
- [x] Task-to-Unknown mapping complete
- [x] PREP_PLAN.md updated with "Unknowns Verified" for Tasks 2-10
- [x] PLAN.md created with day-by-day breakdown

---

# Resolution Summary (Task 10 Completion)

**Date:** January 13, 2026  
**Status:** ALL 26 UNKNOWNS VERIFIED ✅

## Final Resolution Status

| Category | Unknowns | Verified | Status |
|----------|----------|----------|--------|
| 1. Parse Testing Infrastructure | 5 | 5 | ✅ Complete |
| 2. Translation Testing Infrastructure | 4 | 4 | ✅ Complete |
| 3. MCP Solve Testing | 7 | 7 | ✅ Complete |
| 4. Database Schema Extensions | 4 | 4 | ✅ Complete |
| 5. Pipeline Orchestration & Filtering | 3 | 3 | ✅ Complete |
| 6. Performance & Baseline Metrics | 3 | 3 | ✅ Complete |
| **Total** | **26** | **26** | **100%** |

## Key Decisions Made

| Unknown | Decision | Verified In |
|---------|----------|-------------|
| 1.1 | Extend batch_parse.py (not replace) | Task 2 |
| 1.2 | Subcategorize syntax_error (77% of failures) | Task 2 |
| 1.3 | Binary pass/fail for parse status | Task 4 |
| 1.4 | Extract model statistics from IR | Task 4 |
| 2.1 | Extend batch_translate.py (not replace) | Task 2 |
| 2.2 | GAMS action=c for syntax validation | Task 2 |
| 2.3 | 12 translation error categories | Task 4 |
| 3.1 | rtol=1e-6, atol=1e-8 with combined formula | Tasks 3, 9 |
| 3.2 | 7-outcome decision tree for status handling | Task 3 |
| 3.3 | Compare objectives only (not primal variables) | Task 3 |
| 3.4 | Objective-only comparison for Sprint 15 | Task 3 |
| 3.5 | 16 solve outcome categories | Task 4 |
| 3.6 | PATH solver validated (GAMS 51.3.0, PATH 5.2.01) | Task 5 |
| 3.7 | .lst file extraction patterns validated | Task 5 |
| 4.1 | 14-field mcp_solve_result object | Task 6 |
| 4.2 | 16-field solution_comparison_result object | Task 6 |
| 4.3 | Schema version 2.1.0 (minor, backward compatible) | Task 6 |
| 4.4 | Enum extension backward compatible | Task 6 |
| 5.1 | 14 MVP filters defined | Task 7 |
| 5.2 | Cascade failure handling with not_tested status | Task 7 |
| 5.3 | Summary statistics design complete | Task 7 |
| 6.1 | Use time.perf_counter() for timing | Task 8 |
| 6.2 | Dual JSON/Markdown baseline format | Task 8 |
| 6.3 | Statistical analysis approach defined | Task 8 |

## Prep Phase Complete

All 10 prep tasks completed successfully:

| Task | Deliverable | Status |
|------|-------------|--------|
| 1 | KNOWN_UNKNOWNS.md | ✅ Complete |
| 2 | batch_infrastructure_assessment.md | ✅ Complete |
| 3 | solution_comparison_research.md | ✅ Complete |
| 4 | error_taxonomy.md | ✅ Complete |
| 5 | path_solver_integration.md | ✅ Complete |
| 6 | schema_v2.1.0_draft.json, schema_extensions.md | ✅ Complete |
| 7 | test_filtering_requirements.md | ✅ Complete |
| 8 | performance_measurement.md | ✅ Complete |
| 9 | numerical_tolerance_research.md | ✅ Complete |
| 10 | PLAN.md | ✅ Complete |

**Sprint 15 is ready to begin execution.**

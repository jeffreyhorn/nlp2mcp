# Sprint 15 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 15 pipeline testing infrastructure  
**Timeline:** Complete before Sprint 15 Day 1  
**Goal:** Research and validate approaches for automated testing infrastructure to establish baseline metrics

**Key Insight from Sprint 14:** Batch parse achieved 21.3% success rate (+8pp above 13.3% baseline) and translation achieved 94.1% success. Sprint 15 will build comprehensive testing infrastructure to track parse/translate/solve pipeline end-to-end with automated solution validation.

---

## Executive Summary

Sprint 14 delivered the JSON database infrastructure with batch parse/translate scripts. Sprint 15 builds on this foundation to create comprehensive automated testing infrastructure covering the full nlp2mcp pipeline (parse → translate → solve).

### Sprint 15 Goals (from PROJECT_PLAN.md)

**Primary Goal:** Build automated testing infrastructure to run verified convex models through nlp2mcp parse/translate/solve pipeline. Establish initial baseline metrics.

**Key Components:**
1. **Parse Testing Infrastructure** - Automated parse testing with error classification
2. **Translation Testing Infrastructure** - Translation testing with error categorization
3. **MCP Solve Testing Infrastructure** - Solve testing with solution validation
4. **Full Pipeline Runner** - Orchestrated pipeline with filtering and reporting

### Critical Unknowns to Resolve Before Sprint 15

This prep plan identifies 10 essential preparation tasks to research and validate approaches before implementation begins:

1. **Known Unknowns Documentation** - Proactive identification of assumptions and risks
2. **Existing Infrastructure Assessment** - Understand what batch_parse.py/batch_translate.py already provide
3. **Solution Comparison Strategy** - How to reliably compare NLP vs MCP solutions
4. **Error Classification Taxonomy** - Comprehensive error categories for all pipeline stages
5. **PATH Solver Integration** - Validate PATH solver availability and integration approach
6. **Database Schema Extensions** - Design additions for solve results and solution comparison
7. **Test Filtering Requirements** - Identify filter patterns needed for selective testing
8. **Performance Baseline Strategy** - Measurement approach for parse/translate/solve times
9. **Tolerance Configuration Research** - Appropriate tolerances for numerical comparison
10. **Sprint 15 Detailed Schedule** - Day-by-day plan incorporating all research findings

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint 15 Component |
|---|------|----------|-----------|--------------|---------------------|
| 1 | Create Sprint 15 Known Unknowns List | Critical | 3-4h | None | All components |
| 2 | Assess Existing Batch Infrastructure | Critical | 2-3h | None | Parse/translate testing |
| 3 | Research Solution Comparison Strategies | Critical | 4-5h | Task 1 | Solve testing |
| 4 | Design Comprehensive Error Taxonomy | High | 3-4h | Task 1, 2 | Error classification |
| 5 | Validate PATH Solver Integration | Critical | 2-3h | Task 1 | Solve testing |
| 6 | Design Database Schema Extensions | High | 3-4h | Task 3, 4, 5 | All components |
| 7 | Define Test Filtering Requirements | High | 2-3h | Task 2 | Pipeline runner |
| 8 | Research Performance Measurement Approach | Medium | 2-3h | Task 2 | Baseline metrics |
| 9 | Research Numerical Tolerance Best Practices | High | 2-3h | Task 3 | Solution comparison |
| 10 | Plan Sprint 15 Detailed Schedule | Critical | 4-5h | All tasks | Sprint execution |

**Total Estimated Time:** 27-37 hours (~3.5-5 working days)

**Critical Path:** Tasks 1 → 2 → 3 → 5 → 6 → 10

---

## Task 1: Create Sprint 15 Known Unknowns List

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Deadline:** Before Sprint 15 Day 1  
**Owner:** Sprint planning team  
**Dependencies:** None

### Objective

Create comprehensive list of assumptions and unknowns for Sprint 15 to proactively identify risks and research needs before implementation begins.

### Why This Matters

Sprint 15 involves significant new infrastructure (solve testing, solution comparison) with many technical unknowns. Proactive identification prevents mid-sprint blocking issues and emergency research.

From Sprint 4/5 learnings: Known unknowns lists achieved ⭐⭐⭐⭐⭐ rating when used proactively. They prevent late discoveries that cost days of rework.

### Background

**Sprint 15 Scope (from PROJECT_PLAN.md):**
- Parse testing infrastructure with error classification
- Translation testing infrastructure with error categorization  
- MCP solve testing with solution comparison
- Full pipeline orchestration and filtering
- Initial baseline metrics

**Key Technical Challenges:**
1. **Solution Comparison:** How to reliably compare NLP vs MCP solutions (tolerance, infeasibility, multiple optima)
2. **PATH Solver:** Integration approach, error handling, timeout configuration
3. **Error Classification:** Comprehensive taxonomy for parse, translate, and solve errors
4. **Database Extensions:** Schema changes needed for solve results
5. **Performance Measurement:** Accurate timing for parse/translate/solve stages

### What Needs to Be Done

#### Step 1: Review Sprint 15 Goals and Components (30 min)

1. Read PROJECT_PLAN.md lines 229-330 (Sprint 15 section)
2. Identify all deliverables and acceptance criteria
3. List all technical decisions mentioned
4. Note any assumptions made in the plan

```bash
# Review sprint goals
grep -A 100 "Sprint 15" docs/planning/EPIC_3/PROJECT_PLAN.md
```

#### Step 2: Identify Categories of Unknowns (30 min)

Create 5-7 categories based on sprint components:

**Suggested Categories:**
1. **Parse Testing Infrastructure** (test_parse.py)
   - Error classification approach
   - Integration with existing batch_parse.py
   - Database updates
   
2. **Translation Testing Infrastructure** (test_translate.py)
   - Error categorization
   - Integration with existing batch_translate.py
   - MCP file management

3. **MCP Solve Testing** (test_solve.py)
   - PATH solver integration
   - Solution comparison methodology
   - Tolerance configuration
   - Infeasibility handling
   
4. **Database Schema Extensions**
   - Solve results structure
   - Solution comparison fields
   - Performance metrics

5. **Pipeline Orchestration** (run_full_test.py)
   - Filter requirements
   - Error handling across stages
   - Summary generation

6. **Performance and Baseline Metrics**
   - Timing methodology
   - Baseline documentation
   - Statistical analysis

#### Step 3: Document Unknowns with Research Plans (1.5-2 hours)

For each unknown, document:

**Template:**
```markdown
### Unknown X.Y: [Question]

**Category:** [Category name]  
**Priority:** Critical/High/Medium/Low  
**Current Assumption:** [What we're assuming]  
**Why It Matters:** [Impact if assumption is wrong]  
**Verification Method:** [How to verify]  
**Research Required:** [Hours needed]  
**Sprint 15 Impact:** [Which component depends on this]
```

**Example Unknowns to Include:**

**Category 1: Parse Testing**
- Unknown 1.1: Can we reuse batch_parse.py or do we need separate test_parse.py?
- Unknown 1.2: What additional error categories beyond Sprint 14's 7 categories are needed?
- Unknown 1.3: How to handle partial parse success (some declarations parsed, not all)?

**Category 2: Translation Testing**
- Unknown 2.1: Do we need separate test_translate.py or extend batch_translate.py?
- Unknown 2.2: What translation error categories are comprehensive?
- Unknown 2.3: How to validate generated MCP syntax without solving?

**Category 3: Solve Testing**
- Unknown 3.1: Is PATH solver the correct choice for all MCP models?
- Unknown 3.2: What tolerance values are appropriate for solution comparison?
- Unknown 3.3: How to handle models where NLP is infeasible but MCP is feasible?
- Unknown 3.4: How to handle multiple optima (non-unique solutions)?
- Unknown 3.5: What's the appropriate timeout for MCP solves?

**Category 4: Database Schema**
- Unknown 4.1: What fields are needed for solve results (status, time, iterations)?
- Unknown 4.2: How to structure solution comparison data (objective values, tolerances)?
- Unknown 4.3: Should we version the schema (v2.0.0 → v2.1.0 or v3.0.0)?

**Category 5: Pipeline Orchestration**
- Unknown 5.1: What filter patterns are needed (--only-parse, --only-failing, --model=NAME)?
- Unknown 5.2: How to handle cascading failures (parse fails → skip translate)?
- Unknown 5.3: What summary statistics are most useful?

**Category 6: Performance Metrics**
- Unknown 6.1: How to measure accurate timing (subprocess overhead, I/O)?
- Unknown 6.2: What baseline metrics should we record?
- Unknown 6.3: How to detect performance regressions?

#### Step 4: Prioritize and Estimate Research (30 min)

1. Mark Critical unknowns (must resolve before Sprint 15 Day 1)
2. Mark High unknowns (should resolve, but can defer to early sprint)
3. Estimate research time for each unknown
4. Create research task list for remaining prep tasks

#### Step 5: Create Document (30 min)

Create `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md` with:
- Executive summary with unknown counts
- Category-by-category unknowns
- Priority breakdown
- Research time estimates
- Update procedures

### Changes

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify document exists
ls -lh docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md

# Verify structure
grep "^### Unknown" docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md | wc -l
# Should show 20-30 unknowns

# Verify categories
grep "^## Category" docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md
# Should show 5-7 categories

# Verify priorities
grep "^**Priority:**" docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md | sort | uniq -c
# Should show distribution across Critical/High/Medium/Low
```

### Deliverables

- `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md` (comprehensive unknown list)
- 20-30 documented unknowns across 5-7 categories
- Research plan with time estimates
- Prioritization (Critical/High/Medium/Low)

### Acceptance Criteria

- [x] Document created with 20+ unknowns
- [x] All unknowns have priority, assumption, verification method
- [x] Categories align with Sprint 15 components
- [x] Critical unknowns have clear research plans
- [x] Research time estimated (should total 15-25 hours)
- [x] Unknown template defined for updates during sprint

---

## Task 2: Assess Existing Batch Infrastructure

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 2-3 hours  
**Deadline:** Before Sprint 15 Day 1  
**Owner:** Development team  
**Dependencies:** None  
**Unknowns Verified:** 1.1, 1.2, 2.1, 2.2

### Objective

Thoroughly analyze `scripts/gamslib/batch_parse.py` and `scripts/gamslib/batch_translate.py` from Sprint 14 to understand what functionality already exists and what needs to be added/changed for Sprint 15 testing infrastructure.

### Why This Matters

Sprint 14 delivered batch_parse.py and batch_translate.py that already:
- Process models in batch
- Update database with results  
- Categorize errors
- Report progress

Sprint 15's test_parse.py and test_translate.py should **reuse or extend** this infrastructure, not duplicate it. Understanding what exists prevents wasted effort and ensures consistency.

### Background

**Sprint 14 Deliverables (from SPRINT_SUMMARY.md):**
- `batch_parse.py` - Processed 160 models, 34 successful (21.3%), 7 error categories
- `batch_translate.py` - Processed 34 parsed models, 32 successful (94.1%)
- Error categorization: syntax_error (77%), unsupported_feature (14.3%), validation_error (5.6%), missing_include (2.4%), internal_error (0.8%)

**Questions to Answer:**
1. Does batch_parse.py already provide everything needed for "parse testing"?
2. What's missing for Sprint 15 requirements?
3. Can we extend existing scripts or do we need new ones?
4. What command-line options exist?
5. How is database integration implemented?

### What Needs to Be Done

#### Step 1: Read and Analyze batch_parse.py (45-60 min)

1. **Read the full script:**
   ```bash
   cat scripts/gamslib/batch_parse.py
   ```

2. **Document key functionality:**
   - Entry point and command-line arguments
   - Database loading/saving approach
   - Model filtering logic
   - Parse execution (subprocess? direct import?)
   - Error handling and categorization
   - Progress reporting
   - Database update logic
   - Summary generation

3. **Note strengths and limitations:**
   - ✅ What works well
   - ⚠️ What's incomplete
   - 🔄 What needs enhancement

4. **Check for extensibility:**
   - Can we add more error categories?
   - Can we add timing metrics?
   - Can we add model statistics (variables, equations)?

#### Step 2: Read and Analyze batch_translate.py (45-60 min)

1. **Read the full script:**
   ```bash
   cat scripts/gamslib/batch_translate.py
   ```

2. **Document key functionality:**
   - Command-line arguments
   - Model selection (parsed models only?)
   - Translation execution
   - MCP file output location
   - Error handling
   - Database updates
   - Summary generation

3. **Compare with batch_parse.py:**
   - Shared patterns
   - Differences in approach
   - Consistency in error handling

#### Step 3: Check Database Integration (20-30 min)

1. **Review database schema:**
   ```bash
   jq '.models[0] | keys' data/gamslib/gamslib_status.json
   ```

2. **Check what fields are populated:**
   - nlp2mcp_parse object structure
   - nlp2mcp_translate object structure
   - Error message format
   - Timestamp format

3. **Identify schema extensions needed:**
   - Missing fields for Sprint 15 requirements
   - Additional metadata needed

#### Step 4: Test Existing Scripts (20-30 min)

1. **Run batch_parse.py with --help:**
   ```bash
   python scripts/gamslib/batch_parse.py --help
   ```

2. **Run on single model:**
   ```bash
   python scripts/gamslib/batch_parse.py --model trnsport
   ```

3. **Check database update:**
   ```bash
   jq '.models[] | select(.name=="trnsport") | .nlp2mcp_parse' data/gamslib/gamslib_status.json
   ```

4. **Document actual behavior vs. expected**

#### Step 5: Create Assessment Document (30-45 min)

Create `docs/planning/EPIC_3/SPRINT_15/prep-tasks/batch_infrastructure_assessment.md` with:

**Section 1: batch_parse.py Analysis**
- Functionality overview
- Command-line options
- Database integration
- Error categorization
- Strengths
- Limitations
- Extension opportunities

**Section 2: batch_translate.py Analysis**
- Functionality overview
- Command-line options
- Database integration
- Error categorization
- Strengths
- Limitations
- Extension opportunities

**Section 3: Comparison and Recommendations**
- Shared patterns
- Inconsistencies
- Code reuse opportunities
- Recommended approach for Sprint 15:
  - Option A: Extend batch_parse.py/batch_translate.py
  - Option B: Create new test_parse.py/test_translate.py
  - Option C: Hybrid (extend for some features, new for others)

**Section 4: Sprint 15 Implications**
- What can be reused as-is
- What needs enhancement
- What needs to be built from scratch
- Estimated effort savings from reuse

### Changes

- Created `docs/planning/EPIC_3/SPRINT_15/prep-tasks/batch_infrastructure_assessment.md`
- Updated `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.1, 1.2, 2.1, 2.2

### Result

**Key Findings:**
1. **batch_parse.py** provides robust infrastructure: direct parser import, error categorization (6 categories), CLI with --model/--limit/--dry-run, database integration via db_manager, progress reporting with ETA
2. **batch_translate.py** mirrors batch_parse.py patterns: subprocess isolation (60s timeout), MCP output management, consistent CLI
3. **Recommendation:** Extend existing scripts rather than create new ones. Add filter flags (--only-failing, --error-category, --parse-success/failure)
4. **Effort Savings:** 12-16 hours saved by reusing infrastructure vs. building from scratch

**Unknown Verifications:**
- Unknown 1.1: VERIFIED - batch_parse.py should be extended
- Unknown 1.2: VERIFIED - syntax_error (77%) needs subcategorization
- Unknown 2.1: VERIFIED - batch_translate.py should be extended
- Unknown 2.2: VERIFIED - GAMS `action=c` enables syntax validation without solving

### Verification

```bash
# Verify scripts exist
ls -lh scripts/gamslib/batch_parse.py scripts/gamslib/batch_translate.py

# Verify they run
python scripts/gamslib/batch_parse.py --help
python scripts/gamslib/batch_translate.py --help

# Verify assessment document created
ls -lh docs/planning/EPIC_3/SPRINT_15/prep-tasks/batch_infrastructure_assessment.md
```

### Deliverables

- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/batch_infrastructure_assessment.md`
- Detailed analysis of batch_parse.py functionality
- Detailed analysis of batch_translate.py functionality
- Comparison and reuse recommendations
- Sprint 15 implementation strategy
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 2.1, 2.2

### Acceptance Criteria

- [x] batch_parse.py fully documented (functionality, options, integration)
- [x] batch_translate.py fully documented (functionality, options, integration)
- [x] Strengths and limitations identified for each
- [x] Recommendation for Sprint 15 approach (extend vs. new scripts)
- [x] Code reuse opportunities identified
- [x] Effort savings estimated
- [x] Unknowns 1.1, 1.2, 2.1, 2.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: Research Solution Comparison Strategies

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 4-5 hours  
**Deadline:** Before Sprint 15 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Known Unknowns)  
**Unknowns Verified:** 3.1, 3.2, 3.3, 3.4

### Objective

Research and validate strategies for comparing NLP solutions with MCP solutions to ensure the KKT reformulation produces mathematically equivalent results.

### Why This Matters

**Core validation requirement:** Sprint 15's primary goal is to verify that nlp2mcp's KKT reformulation produces correct results. This requires comparing:
- Original NLP solution (from GAMS solve with CONOPT/IPOPT)
- MCP solution (from PATH solver on generated KKT conditions)

**Technical challenges:**
1. **Numerical tolerance:** Floating point comparison requires appropriate tolerances
2. **Infeasibility:** NLP infeasible but MCP feasible (or vice versa) needs handling
3. **Multiple optima:** Non-unique solutions may have different objective values
4. **Solver status:** Different solvers use different status codes
5. **Primal vs. dual:** MCP includes both primal variables and dual multipliers

**Wrong approach = false positives/negatives in validation.**

### Background

**From PROJECT_PLAN.md (Sprint 15):**
- "Compare MCP solution to original NLP solution: Objective value match (within tolerance)"
- "Configurable tolerance (default: 1e-6 relative, 1e-8 absolute)"
- "Solution status (optimal, infeasible, etc.)"

**From Sprint 14 recommendations:**
- "Add MCP solve verification"
- "Implement objective value comparison"

**Open questions:**
- What tolerance values are appropriate?
- How to compare when statuses differ?
- How to handle multiple optima?
- Do we compare primal variables or just objective?
- What about dual multipliers?

### What Needs to Be Done

#### Step 1: Review Mathematical Background (45-60 min)

1. **Read KKT optimality conditions:**
   - Review docs/concepts/IDEA.md
   - Review docs/concepts/NLP2MCP_HIGH_LEVEL.md
   - Understand relationship between NLP optimum and MCP solution

2. **Research complementarity conditions:**
   - What makes a solution optimal for MCP?
   - When do NLP and MCP solutions differ mathematically?

3. **Document theoretical basis:**
   - Under what conditions should solutions match exactly?
   - When might they differ?
   - What does "close enough" mean?

**Output:** Section in research document on theoretical foundation

#### Step 2: Research Numerical Tolerance Practices (45-60 min)

1. **Survey optimization literature:**
   - What tolerances do solvers use internally?
   - What tolerances do testing frameworks use?
   - GAMS documentation on solution comparison

2. **Check solver defaults:**
   - CONOPT tolerance settings
   - IPOPT tolerance settings
   - PATH solver tolerance settings

3. **Research relative vs. absolute tolerance:**
   - When to use relative (large objective values)
   - When to use absolute (objective near zero)
   - Combined approach: `abs(a - b) <= atol + rtol * abs(b)`

4. **Document recommendations:**
   - Default tolerances for nlp2mcp testing
   - Configuration approach (environment variables? command-line args?)
   - Edge cases (objective = 0, very large objectives)

**Output:** Section on tolerance selection with justification

#### Step 3: Research Infeasibility Handling (30-45 min)

1. **Identify infeasibility scenarios:**
   - Both infeasible (models are actually infeasible)
   - NLP feasible, MCP infeasible (KKT reformulation error)
   - NLP infeasible, MCP feasible (KKT reformulation error)
   - Status codes differ but both "solved"

2. **Design decision tree:**
   ```
   if nlp_status == optimal and mcp_status == optimal:
       compare objectives
   elif nlp_status == infeasible and mcp_status == infeasible:
       pass (both agree)
   elif nlp_status == optimal and mcp_status != optimal:
       error (KKT reformulation likely wrong)
   # ... etc
   ```

3. **Document handling for each case**

**Output:** Decision tree for status comparison

#### Step 4: Research Multiple Optima Handling (30-45 min)

1. **Understand when multiple optima occur:**
   - Linear programs with degenerate solutions
   - Non-convex problems (shouldn't occur with verified_convex models)
   - Flat objective regions

2. **Research comparison strategies:**
   - Accept any solution with matching objective?
   - Check KKT conditions directly?
   - Numerical stability checks?

3. **Design handling approach:**
   - What tolerance for objective matching?
   - How to report multiple optima?
   - Should we flag for manual review?

**Output:** Multiple optima handling strategy

#### Step 5: Research Variable Comparison (45-60 min)

1. **Decide what to compare:**
   - Objective value only (easiest)
   - Objective + primal variables (more thorough)
   - Objective + primal + dual (most thorough)

2. **Consider variable mapping:**
   - NLP has variables x, y, z
   - MCP has x, y, z PLUS multipliers lambda_eq, lambda_ineq, etc.
   - How to extract and compare?

3. **Research implementation approaches:**
   - Parse .lst files for solution values?
   - Use GAMS GDX format?
   - Python GAMS API?

4. **Evaluate complexity vs. value:**
   - Is objective comparison sufficient for Sprint 15 baseline?
   - Can variable comparison be deferred to Sprint 16?

**Output:** Scope decision for Sprint 15

#### Step 6: Survey Existing Tools (30-45 min)

1. **Check if GAMS has built-in comparison tools:**
   - GAMS testing framework
   - GAMS solution comparison utilities
   - GDXDiff tool

2. **Check nlp2mcp existing validation:**
   - Do golden tests compare solutions?
   - What approach do they use?
   - Can we reuse that code?

```bash
# Search for solution comparison in tests
grep -r "objective" tests/ | grep -i compare
grep -r "solution" tests/ | grep -i match
```

3. **Document reuse opportunities**

**Output:** Existing tools assessment

#### Step 7: Create Research Document (45-60 min)

Create `docs/planning/EPIC_3/SPRINT_15/prep-tasks/solution_comparison_research.md` with:

**Section 1: Theoretical Foundation**
- KKT optimality conditions
- When NLP and MCP solutions should match
- Mathematical guarantees

**Section 2: Tolerance Selection**
- Recommended default tolerances (relative and absolute)
- Justification from literature and solver defaults
- Configuration approach
- Edge cases

**Section 3: Status Comparison**
- Decision tree for handling different solver statuses
- Infeasibility handling
- Error detection logic

**Section 4: Multiple Optima Handling**
- When it occurs
- Comparison strategy
- Reporting approach

**Section 5: Comparison Scope**
- What to compare (objective, variables, duals)
- Sprint 15 scope recommendation
- Future enhancements (Sprint 16+)

**Section 6: Implementation Approach**
- .lst file parsing vs. GDX vs. Python API
- Code reuse opportunities
- Estimated implementation effort

**Section 7: Recommendations for Sprint 15**
- Proposed comparison algorithm
- Default tolerance values
- Error handling approach
- Testing strategy

### Changes

- Created `docs/planning/EPIC_3/SPRINT_15/prep-tasks/solution_comparison_research.md`
- Updated `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md` with verification results for Unknowns 3.1, 3.2, 3.3, 3.4

### Result

**Key Findings:**
1. **Tolerance Selection:** Combined tolerance formula `|a - b| <= atol + rtol * |b|` with rtol=1e-6 (matches CPLEX), atol=1e-8 (matches numpy). Validated against solver defaults (CONOPT 1e-7, IPOPT 1e-8, PATH 1e-6, CPLEX 1e-6).
2. **Decision Tree for Status Comparison:** 7-outcome decision tree covering optimal/optimal (compare objectives), infeasible/infeasible (both agree), mismatches (flag as errors), and timeouts.
3. **Multiple Optima Strategy:** Compare objectives only, not primal variables. Multiple solutions may have identical objective values but different variable values.
4. **Comparison Scope:** Objectives only for Sprint 15 (sufficient for validation). Variable comparison deferred to Sprint 16+.
5. **Implementation Approach:** Reuse .lst parsing from verify_convexity.py (objective extraction pattern), tolerance utilities from test_path_solver.py.
6. **Code Reuse Identified:** `_check_kkt_residuals()` in test_path_solver.py uses tolerance=1e-6, verify_convexity.py has objective value extraction from .lst files.

**Unknown Verifications:**
- Unknown 3.1: VERIFIED - rtol=1e-6, atol=1e-8 with combined formula
- Unknown 3.2: VERIFIED - 7-outcome decision tree for status handling
- Unknown 3.3: VERIFIED - Compare objectives only for multiple optima
- Unknown 3.4: VERIFIED - Objective-only comparison for Sprint 15

### Verification

```bash
# Verify research document created
ls -lh docs/planning/EPIC_3/SPRINT_15/prep-tasks/solution_comparison_research.md

# Verify it addresses key questions
grep -i "tolerance" docs/planning/EPIC_3/SPRINT_15/prep-tasks/solution_comparison_research.md
grep -i "infeasible" docs/planning/EPIC_3/SPRINT_15/prep-tasks/solution_comparison_research.md
grep -i "multiple optima" docs/planning/EPIC_3/SPRINT_15/prep-tasks/solution_comparison_research.md

# Check for concrete recommendations
grep "Recommendation" docs/planning/EPIC_3/SPRINT_15/prep-tasks/solution_comparison_research.md
```

### Deliverables

- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/solution_comparison_research.md`
- Theoretical foundation for solution comparison
- Recommended tolerance values with justification
- Status comparison decision tree
- Multiple optima handling strategy
- Implementation approach recommendation
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.2, 3.3, 3.4

### Acceptance Criteria

- [x] Theoretical foundation documented
- [x] Tolerance values recommended (relative and absolute)
- [x] Status comparison decision tree complete
- [x] Multiple optima handling defined
- [x] Comparison scope decided (objective only vs. variables vs. duals)
- [x] Implementation approach selected (.lst vs. GDX vs. API)
- [x] Code reuse opportunities identified
- [x] Sprint 15 recommendations clear and actionable
- [x] Unknowns 3.1, 3.2, 3.3, 3.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 4: Design Comprehensive Error Taxonomy

**Status:** ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 3-4 hours  
**Deadline:** Before Sprint 15 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Known Unknowns), Task 2 (Batch Infrastructure)  
**Unknowns Verified:** 1.3, 1.4, 2.3, 3.5

### Objective

Design comprehensive error classification taxonomy for all three pipeline stages (parse, translate, solve) to enable systematic analysis of failure modes and targeted improvements.

### Why This Matters

**Sprint 14 baseline:** 7 parse error categories, translation errors not fully categorized
- syntax_error (77% of failures)
- unsupported_feature (14.3%)
- validation_error (5.6%)
- missing_include (2.4%)
- internal_error (0.8%)
- timeout
- license_limited

**Sprint 15 needs:**
- Refine parse categories for better targeting
- Add comprehensive translation error categories
- Add solve error categories (new)
- Consistent categorization across stages

**Use case:** "We have 97 syntax errors. Which specific syntax patterns are failing most? Can we fix top 3 and get 30% more models parsing?"

### Background

**From Sprint 14 SPRINT_SUMMARY.md:**
- Parse errors: 126 failures categorized into 7 categories
- Translation errors: 2 failures, categories not specified
- Solve errors: Not yet tested

**From PROJECT_PLAN.md Sprint 15:**
- "Categorize parse errors by type: Unsupported syntax (specify which construct), Lexer/tokenization errors, Grammar/parser errors, IR construction errors"
- "Categorize translation errors: Differentiation errors (unsupported operations), Min/max reformulation errors, KKT generation errors, Code generation errors"

### What Needs to Be Done

#### Step 1: Review Existing Parse Error Categories (30-45 min)

1. **Analyze Sprint 14 error distribution:**
   ```bash
   # Check actual error messages from database
   jq '.models[] | select(.nlp2mcp_parse.status=="failure") | .nlp2mcp_parse.error' data/gamslib/gamslib_status.json | sort | uniq -c | sort -rn
   ```

2. **Review batch_parse.py categorization logic:**
   - How are errors currently categorized?
   - What patterns are detected?
   - What's in the "syntax_error" catch-all (77% of failures)?

3. **Identify refinement opportunities:**
   - Can we split syntax_error into subcategories?
   - What specific syntax constructs are failing?
   - Are there patterns in error messages?

**Output:** Analysis of current parse categories

#### Step 2: Design Refined Parse Error Taxonomy (45-60 min)

1. **Review nlp2mcp parser architecture:**
   ```bash
   # Understand parser stages
   ls -la src/parse/
   cat src/parse/README.md  # if it exists
   ```

2. **Map errors to parser stages:**
   - **Lexer errors:** Tokenization failures (unknown characters, invalid tokens)
   - **Parser errors:** Grammar violations (syntax not matching GAMS grammar)
   - **Semantic errors:** Valid syntax but semantic issues (undefined variables, type mismatches)
   - **IR construction errors:** Fails to build intermediate representation

3. **Define subcategories for each stage:**

   **Lexer Errors:**
   - `lexer_unknown_character`
   - `lexer_invalid_number`
   - `lexer_unclosed_string`

   **Parser Errors (syntax):**
   - `parser_equation_syntax`
   - `parser_declaration_syntax`
   - `parser_expression_syntax`
   - `parser_unsupported_construct` (e.g., GAMS features not in our grammar)

   **Semantic Errors:**
   - `semantic_undefined_symbol`
   - `semantic_type_mismatch`
   - `semantic_domain_violation`

   **IR Construction:**
   - `ir_build_failure`
   - `ir_validation_failure`

4. **Map Sprint 14 categories to new taxonomy:**
   - syntax_error → which subcategory?
   - unsupported_feature → parser_unsupported_construct?
   - validation_error → semantic_* or ir_validation_failure?

**Output:** Refined parse error taxonomy

#### Step 3: Design Translation Error Taxonomy (45-60 min)

1. **Review nlp2mcp translation pipeline:**
   ```bash
   ls -la src/
   # Identify translation stages: IR → differentiation → KKT → MCP code
   ```

2. **Define translation error categories:**

   **Differentiation Errors:**
   - `diff_unsupported_function` (e.g., gamma, smin not implemented)
   - `diff_chain_rule_failure`
   - `diff_partial_derivative_failure`

   **Min/Max Reformulation Errors:**
   - `minmax_objective_reformulation_failure`
   - `minmax_constraint_reformulation_failure`
   - `minmax_nested_failure`

   **KKT Generation Errors:**
   - `kkt_stationarity_failure`
   - `kkt_complementarity_failure`
   - `kkt_dual_variable_failure`

   **Code Generation Errors:**
   - `codegen_equation_emission_failure`
   - `codegen_variable_emission_failure`
   - `codegen_syntax_error`

   **Internal Errors:**
   - `translate_internal_error`
   - `translate_timeout`

3. **Check Sprint 14 translation failures:**
   ```bash
   jq '.models[] | select(.nlp2mcp_translate.status=="failure")' data/gamslib/gamslib_status.json
   ```

**Output:** Translation error taxonomy

#### Step 4: Design Solve Error Taxonomy (30-45 min)

1. **Research PATH solver error codes:**
   - Solver status codes (normal completion, iteration limit, etc.)
   - Model status codes (optimal, infeasible, unbounded, etc.)
   - Common failure modes

2. **Define solve error categories:**

   **Solution Status:**
   - `solve_optimal` (not an error, but a category)
   - `solve_locally_optimal`
   - `solve_infeasible`
   - `solve_unbounded`
   - `solve_iteration_limit`
   - `solve_time_limit`

   **Comparison Errors:**
   - `comparison_objective_mismatch` (solutions differ beyond tolerance)
   - `comparison_status_mismatch` (NLP optimal, MCP infeasible)
   - `comparison_nlp_solve_failure` (can't get NLP solution to compare)

   **PATH Solver Errors:**
   - `path_error_execution_failure`
   - `path_error_syntax` (generated MCP has syntax errors)
   - `path_error_numerical` (numerical issues during solve)

   **Internal Errors:**
   - `solve_internal_error`
   - `solve_timeout`

**Output:** Solve error taxonomy

#### Step 5: Create Comprehensive Taxonomy Document (45-60 min)

Create `docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md` with:

**Section 1: Overview**
- Purpose of error taxonomy
- How it will be used
- Relationship to database schema

**Section 2: Parse Error Categories**
- Full taxonomy with descriptions
- Example error messages for each category
- Detection patterns (regex, keywords)
- Sprint 14 mapping

**Section 3: Translation Error Categories**
- Full taxonomy with descriptions
- Example scenarios for each category
- Detection patterns

**Section 4: Solve Error Categories**
- Full taxonomy with descriptions
- PATH solver status code mapping
- Comparison error detection

**Section 5: Implementation Guidelines**
- How to categorize errors in code
- Error message format
- Database storage format
- Reporting format

**Section 6: Migration Plan**
- How to migrate Sprint 14 data to new categories
- Backward compatibility
- Re-categorization script approach

### Changes

- Created `docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md`
- Updated `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.3, 1.4, 2.3, 3.5

### Result

**Key Findings:**
1. **Parse Error Taxonomy (16 categories):** Refined from 6 broad categories into specific subcategories:
   - Lexer errors (4): invalid_char, unclosed_string, invalid_number, encoding_error
   - Parser errors (6): unexpected_token, missing_semicolon, unmatched_paren, invalid_declaration, invalid_expression, unexpected_eof
   - Semantic errors (4): undefined_symbol, type_mismatch, domain_error, duplicate_def
   - Include errors (2): file_not_found, circular
2. **Translation Error Taxonomy (12 categories):** Covers differentiation, model structure, unsupported constructs, and code generation
3. **Solve Outcome Taxonomy (16 categories):** Covers PATH solver status (6), model status (4), and solution comparison (6) - includes 4 success outcomes and 12 error types
4. **Total: 44 outcome categories** across all pipeline stages (40 error types + 4 success outcomes)
5. **Detection Algorithm:** Python functions for automatic categorization based on error message patterns
6. **Migration Plan:** Re-process Sprint 14 error messages with new categorization function, preserve legacy_category field

**Unknown Verifications:**
- Unknown 1.3: VERIFIED - Binary pass/fail status for parse (partial tracking deferred)
- Unknown 1.4: VERIFIED - Model statistics can be extracted from IR after successful parse
- Unknown 2.3: VERIFIED - 12 translation error categories covering all failure modes
- Unknown 3.5: VERIFIED - 16 solve outcome categories (12 error + 4 success) with priority of investigation

### Verification

```bash
# Verify taxonomy document created
ls -lh docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md

# Verify all categories defined
grep "^### " docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md | wc -l
# Should have 20-30 error categories total

# Verify coverage of all stages
grep -i "parse" docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md
grep -i "translate" docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md
grep -i "solve" docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md
```

### Deliverables

- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md`
- Refined parse error categories (15-20 categories)
- Comprehensive translation error categories (10-15 categories)
- Complete solve error categories (10-12 categories)
- Detection patterns and implementation guidelines
- Migration plan from Sprint 14 categories
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.3, 1.4, 2.3, 3.5

### Acceptance Criteria

- [x] Parse error taxonomy refines Sprint 14's 7 categories
- [x] Translation error taxonomy covers all translation stages
- [x] Solve error taxonomy covers PATH solver statuses and comparison
- [x] Each category has description and example
- [x] Detection patterns defined for automatic categorization
- [x] Database storage format specified
- [x] Migration plan for Sprint 14 data created
- [x] Unknowns 1.3, 1.4, 2.3, 3.5 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 5: Validate PATH Solver Integration

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 2-3 hours  
**Deadline:** Before Sprint 15 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Known Unknowns)  
**Unknowns Verified:** 3.6, 3.7

### Objective

Validate that PATH solver is available, properly configured, and can be invoked from Python scripts for MCP solving.

### Why This Matters

Sprint 15's solve testing infrastructure depends entirely on PATH solver availability. We need to verify:
1. PATH solver is installed and accessible
2. License is valid and sufficient
3. Can be invoked via GAMS from Python
4. Error handling works correctly
5. Solution extraction is reliable

**Blocking risk:** If PATH solver integration doesn't work, the entire solve testing component of Sprint 15 is blocked.

### Background

**From Sprint 13:** PATH solver was used for convexity verification via GAMS
- Solve worked for LP/NLP/QCP models
- License validated (demo license sufficient)
- .lst file parsing implemented

**Sprint 15 differences:**
- Running MCP models (not LP/NLP)
- Need to extract solution values
- Need to compare with NLP solution
- Need to handle MCP-specific errors

**Questions:**
- Can PATH solve generated MCP files?
- How to invoke: `gams model.gms` or specific PATH invocation?
- What MCP-specific errors might occur?
- How to extract solution from .lst file?

### What Needs to Be Done

#### Step 1: Verify PATH Solver Availability (15-20 min)

1. **Check GAMS installation:**
   ```bash
   which gams
   gams
   ```

2. **Check PATH solver:**
   ```bash
   # List available solvers
   gamsinst -a
   # Should show PATH in the list
   ```

3. **Check license:**
   ```bash
   # Run a simple MCP model to verify PATH works
   cat > test_path.gms << 'EOF'
   variables x, y;
   equations f, g;
   
   f.. x**2 + y - 1 =n= 0;
   g.. x + y**2 - 1 =n= 0;
   
   model test /f.x, g.y/;
   solve test using mcp;
   EOF
   
   gams test_path.gms
   cat test_path.lst | grep "SOLVER STATUS"
   ```

4. **Document environment:**
   - GAMS version
   - PATH solver version
   - License type and limits

**Output:** Environment validation

#### Step 2: Test MCP Model Generation and Solve (30-45 min)

1. **Generate MCP from a simple model:**
   ```bash
   # Use a model that successfully translated in Sprint 14
   python -m nlp2mcp.cli data/gamslib/raw/trnsport.gms -o test_mcp.gms
   ```

2. **Solve the generated MCP:**
   ```bash
   gams test_mcp.gms
   ```

3. **Check solve status:**
   ```bash
   cat test_mcp.lst | grep "SOLVER STATUS"
   cat test_mcp.lst | grep "MODEL STATUS"
   ```

4. **Verify solution exists:**
   ```bash
   cat test_mcp.lst | grep "OBJECTIVE VALUE"
   ```

5. **Document any issues:**
   - Does it solve?
   - What status codes?
   - Any error messages?

**Output:** MCP solve validation

#### Step 3: Test Solution Extraction (30-45 min)

1. **Parse .lst file for solution:**
   ```bash
   # Extract objective value
   grep "OBJECTIVE VALUE" test_mcp.lst
   
   # Extract variable values (if needed for Sprint 15)
   grep "VARIABLE" test_mcp.lst -A 100
   ```

2. **Write Python extraction code:**
   ```python
   def extract_mcp_solution(lst_file):
       """Extract solution from PATH .lst file."""
       with open(lst_file) as f:
           content = f.read()
       
       # Extract solver status
       # Extract model status
       # Extract objective value
       # Return structured data
       pass
   ```

3. **Test extraction on multiple models:**
   - Successful solve
   - Infeasible solve
   - Iteration limit

**Output:** Solution extraction code

#### Step 4: Test Error Handling (20-30 min)

1. **Create intentionally broken MCP:**
   ```gams
   * Syntax error
   * Unbounded model
   * Infeasible model
   ```

2. **Test each error scenario:**
   - Does GAMS report error correctly?
   - Can we detect from .lst file?
   - What status codes are returned?

3. **Document error detection patterns**

**Output:** Error handling validation

#### Step 5: Create Integration Guide (30-45 min)

Create `docs/planning/EPIC_3/SPRINT_15/prep-tasks/path_solver_integration.md` with:

**Section 1: Environment Setup**
- GAMS version required
- PATH solver availability check
- License requirements

**Section 2: Invocation**
- Command to solve MCP model
- Options/flags needed
- Timeout configuration

**Section 3: Solution Extraction**
- .lst file format
- Parsing patterns for status codes
- Parsing patterns for objective value
- Parsing patterns for variable values (optional)

**Section 4: Error Handling**
- Common error scenarios
- Detection patterns
- Status code mapping

**Section 5: Python Integration**
- Sample code for subprocess invocation
- Sample code for solution extraction
- Sample code for error handling

**Section 6: Sprint 15 Recommendations**
- Recommended invocation approach
- Timeout values
- Error handling strategy

### Changes

- Created `docs/planning/EPIC_3/SPRINT_15/prep-tasks/path_solver_integration.md`
- Updated `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md` with verification results for Unknowns 3.6, 3.7

### Result

**Key Findings:**
1. **Environment Validated:** GAMS 51.3.0 with PATH 5.2.01 installed, demo license valid until Jan 23, 2026
2. **MCP Solve Workflow:** Successfully tested with generated MCP files (hs62_mcp.gms solved with SOLVER STATUS 1, MODEL STATUS 1)
3. **Solution Extraction:** .lst file parsing patterns validated for SOLVER STATUS, MODEL STATUS, ITERATION COUNT, RESOURCE USAGE
4. **Error Handling Tested:** Infeasible (MODEL STATUS 4), iteration limit (SOLVER STATUS 2), time limit (SOLVER STATUS 3), compilation errors all correctly detected
5. **Existing Code Reuse:** `scripts/gamslib/verify_convexity.py::parse_gams_listing()` provides comprehensive .lst parsing
6. **Python Integration:** Subprocess invocation with timeout, error handling, and status extraction code samples provided

**Test Results:**
| Scenario | SOLVER STATUS | MODEL STATUS | Detection |
|----------|---------------|--------------|-----------|
| Optimal | 1 | 1 | ✅ |
| Infeasible | 1 | 4 | ✅ |
| Iteration limit | 2 | 6 | ✅ |
| Time limit | 3 | 6 | ✅ |
| Syntax error | N/A | N/A | ✅ (`**** $NNN` pattern) |

**Unknown Verifications:**
- Unknown 3.6: VERIFIED - PATH solver available with demo license, tested successfully
- Unknown 3.7: VERIFIED - .lst file extraction patterns validated with regex

### Verification

```bash
# Verify PATH solver works
gams --version
gamsinst -a | grep PATH

# Verify integration document created
ls -lh docs/planning/EPIC_3/SPRINT_15/prep-tasks/path_solver_integration.md

# Verify sample code runs
python -c "import subprocess; subprocess.run(['gams', '--help'])"
```

### Deliverables

- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/path_solver_integration.md`
- PATH solver availability confirmed
- MCP solve workflow validated
- Solution extraction code samples
- Error handling patterns documented
- Python integration examples
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.6, 3.7

### Acceptance Criteria

- [x] PATH solver confirmed available and licensed
- [x] MCP model can be solved successfully
- [x] Solution can be extracted from .lst file
- [x] Error scenarios tested and documented
- [x] Python integration code samples provided
- [x] Timeout and error handling recommendations clear
- [x] Unknowns 3.6, 3.7 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 6: Design Database Schema Extensions

**Status:** ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 3-4 hours  
**Deadline:** Before Sprint 15 Day 1  
**Owner:** Development team  
**Dependencies:** Task 3 (Solution Comparison), Task 4 (Error Taxonomy), Task 5 (PATH Solver)  
**Unknowns Verified:** 4.1, 4.2, 4.3, 4.4

### Objective

Design extensions to `data/gamslib/schema.json` (v2.0.0) to support solve results, solution comparison, and refined error categorization for Sprint 15.

### Why This Matters

Sprint 14 delivered schema v2.0.0 with `nlp2mcp_parse` and `nlp2mcp_translate` objects. Sprint 15 needs:
1. **mcp_solve object** - Solve results, PATH solver status, timing
2. **solution_comparison object** - Objective comparison, tolerance, match status
3. **Refined error categories** - New taxonomy from Task 4

**Design decisions:**
- Schema versioning: v2.1.0 (minor) or v3.0.0 (major)?
- Backward compatibility with Sprint 14 data?
- Nested structure depth (avoid going beyond 2 levels per Sprint 14 design)

### Background

**Sprint 14 Schema (from GAMSLIB_DATABASE_SCHEMA.md):**
- Total fields: 56 across nested structure
- Version: 2.0.0 (semantic versioning)
- Pipeline stages: `nlp2mcp_parse`, `nlp2mcp_translate`
- Validation: JSON Schema Draft-07

**Existing structure:**
```json
{
  "name": "trnsport",
  "nlp2mcp_parse": {
    "status": "success",
    "error_category": null,
    "error_message": null,
    "timestamp": "2026-01-15T10:00:00Z",
    "nlp2mcp_version": "0.3.0",
    "parse_time_seconds": 0.45
  },
  "nlp2mcp_translate": {
    "status": "success",
    "error_category": null,
    "error_message": null,
    "timestamp": "2026-01-15T10:00:05Z",
    "nlp2mcp_version": "0.3.0",
    "translate_time_seconds": 0.32,
    "mcp_file": "data/gamslib/mcp/trnsport_mcp.gms"
  }
}
```

**Sprint 15 additions:**
- `mcp_solve` object
- `solution_comparison` object
- Refined `error_category` enums

### What Needs to Be Done

#### Step 1: Design mcp_solve Object (45-60 min)

1. **Identify required fields:**
   - `status`: enum (success, failure, timeout)
   - `solver_status`: int (PATH solver status code)
   - `model_status`: int (PATH model status code)
   - `objective_value`: float | null
   - `solve_time_seconds`: float
   - `iterations`: int | null
   - `error_category`: string | null (from Task 4 taxonomy)
   - `error_message`: string | null
   - `timestamp`: string (ISO 8601)
   - `path_version`: string
   - `mcp_file_used`: string (path to MCP file)

2. **Define enums:**
   ```json
   "status": ["success", "failure", "timeout"]
   "solver_status_code": [1, 2, 3, 4, ...]  // PATH codes
   "model_status_code": [1, 2, 3, 4, ...]   // PATH codes
   ```

3. **Define validation rules:**
   - `objective_value` required if status == success
   - `error_category` required if status == failure
   - `solve_time_seconds` >= 0

4. **Draft JSON Schema fragment**

**Output:** mcp_solve object design

#### Step 2: Design solution_comparison Object (45-60 min)

1. **Identify required fields:**
   - `nlp_objective`: float | null (from original NLP solve)
   - `mcp_objective`: float | null (from MCP solve)
   - `objective_match`: bool (within tolerance)
   - `absolute_difference`: float | null
   - `relative_difference`: float | null
   - `tolerance_absolute`: float (used for comparison)
   - `tolerance_relative`: float (used for comparison)
   - `nlp_status`: string (optimal, infeasible, etc.)
   - `mcp_status`: string (optimal, infeasible, etc.)
   - `status_match`: bool
   - `comparison_result`: enum (exact_match, tolerance_match, mismatch, status_mismatch, comparison_failed)
   - `notes`: string | null (for manual review flags)
   - `timestamp`: string (ISO 8601)

2. **Define enums:**
   ```json
   "comparison_result": [
     "exact_match",
     "tolerance_match",
     "objective_mismatch",
     "status_mismatch",
     "nlp_solve_failed",
     "mcp_solve_failed",
     "comparison_not_performed"
   ]
   ```

3. **Define validation rules:**
   - `nlp_objective` and `mcp_objective` required if comparison_result is match/mismatch
   - `absolute_difference` and `relative_difference` required if comparison performed
   - `tolerance_*` values must be > 0

4. **Draft JSON Schema fragment**

**Output:** solution_comparison object design

#### Step 3: Update Error Category Enums (30-45 min)

1. **Review Task 4 error taxonomy:**
   - Parse error categories (15-20)
   - Translation error categories (10-15)
   - Solve error categories (10-12)

2. **Update schema enums:**
   ```json
   "nlp2mcp_parse": {
     "properties": {
       "error_category": {
         "enum": [
           "lexer_unknown_character",
           "lexer_invalid_number",
           "parser_equation_syntax",
           "parser_unsupported_construct",
           "semantic_undefined_symbol",
           "ir_build_failure",
           ...
         ]
       }
     }
   }
   ```

3. **Ensure backward compatibility:**
   - Old categories still valid?
   - Migration path for Sprint 14 data?

**Output:** Updated error category enums

#### Step 4: Decide Schema Versioning (20-30 min)

1. **Evaluate changes:**
   - Adding new objects (mcp_solve, solution_comparison) = major change?
   - Refining enums (error categories) = minor change?
   - Semantic versioning rules: MAJOR.MINOR.PATCH

2. **Options:**
   - **v2.1.0:** Backward compatible (new objects optional)
   - **v3.0.0:** Breaking change (if error category enums incompatible)

3. **Decide approach:**
   - Recommended: v2.1.0 if we can keep old error categories valid
   - Make new objects optional (not required)
   - Existing Sprint 14 data validates against v2.1.0

4. **Document migration plan:**
   - Do we need to migrate Sprint 14 data?
   - Or can we just update schema version?

**Output:** Versioning decision

#### Step 5: Create Full Schema Draft (45-60 min)

Create `docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_v2.1.0_draft.json`:

1. **Start with Sprint 14 schema.json:**
   ```bash
   cp data/gamslib/schema.json docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_v2.1.0_draft.json
   ```

2. **Add mcp_solve object to properties**

3. **Add solution_comparison object to properties**

4. **Update error_category enums**

5. **Update version to 2.1.0**

6. **Validate syntax:**
   ```python
   import json
   from jsonschema import Draft7Validator
   
   with open('schema_v2.1.0_draft.json') as f:
       schema = json.load(f)
   
   Draft7Validator.check_schema(schema)
   print("Schema valid!")
   ```

**Output:** Draft schema v2.1.0

#### Step 6: Create Schema Extension Document (30-45 min)

Create `docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_extensions.md` with:

**Section 1: Overview**
- Schema version: 2.0.0 → 2.1.0
- New objects added
- Enum updates
- Backward compatibility

**Section 2: mcp_solve Object**
- Field descriptions
- Validation rules
- Example values

**Section 3: solution_comparison Object**
- Field descriptions
- Validation rules
- Example values

**Section 4: Updated Error Categories**
- Parse errors (full list)
- Translation errors (full list)
- Solve errors (full list)

**Section 5: Migration Plan**
- Sprint 14 data compatibility
- Migration script needed? (probably not if backward compatible)

**Section 6: Implementation Checklist**
- schema.json update
- db_manager.py update (validation)
- test_solve.py implementation
- Documentation update

### Changes

- Created `docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_v2.1.0_draft.json`
- Created `docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_extensions.md`
- Updated `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md` with verification results for Unknowns 4.1, 4.2, 4.3, 4.4

### Result

**Key Findings:**
1. **mcp_solve_result object (14 fields):** Designed to capture all PATH solver outputs including status, solver_status, model_status, objective_value, solve_time_seconds, iterations, solver version, and outcome categorization
2. **solution_comparison_result object (16 fields):** Designed as separate object for clean separation of concerns, capturing NLP/MCP objectives, tolerances, differences, status comparison, and detailed result categorization
3. **model_statistics object (4 fields):** New object for tracking variables, equations, parameters, sets extracted from IR after successful parse
4. **error_category enum extended:** From 7 to 36 values, preserving all original Sprint 14 categories while adding 29 refined categories from Task 4 error taxonomy
5. **New enums created:**
   - `solve_outcome_category` (10 values): PATH solver outcomes and model status
   - `comparison_result_category` (7 values): Solution comparison outcomes
6. **Schema version:** v2.1.0 (minor) confirmed as correct - all changes are backward-compatible
7. **Backward compatibility:** Sprint 14 data validates against v2.1.0 without modification (new objects are optional)

**Unknown Verifications:**
- Unknown 4.1: VERIFIED - 14-field mcp_solve_result object designed with all essential PATH solver outputs
- Unknown 4.2: VERIFIED - 16-field solution_comparison_result object designed as separate object for clean separation
- Unknown 4.3: VERIFIED - Schema version 2.1.0 (minor) is correct; all changes are backward-compatible
- Unknown 4.4: VERIFIED - Enum extension is backward-compatible; strict enum with legacy preservation approach chosen

### Verification

```bash
# Verify draft schema created
ls -lh docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_v2.1.0_draft.json

# Verify schema is valid JSON
jq empty docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_v2.1.0_draft.json

# Verify documentation created
ls -lh docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_extensions.md

# Verify version updated
jq '.version' docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_v2.1.0_draft.json
# Should show "2.1.0"

# Verify new objects present
jq '.properties | keys' docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_v2.1.0_draft.json
# Should include "mcp_solve" and "solution_comparison"
```

### Deliverables

- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_v2.1.0_draft.json`
- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/schema_extensions.md`
- mcp_solve object design
- solution_comparison object design
- Updated error category enums
- Versioning decision (v2.1.0)
- Migration plan
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.2, 4.3, 4.4

### Acceptance Criteria

- [x] mcp_solve object fully defined with all fields
- [x] solution_comparison object fully defined with all fields
- [x] Error category enums updated with Task 4 taxonomy
- [x] Schema version decided (2.1.0 or 3.0.0)
- [x] Draft schema validates (JSON Schema Draft-07)
- [x] Backward compatibility with Sprint 14 data ensured
- [x] Migration plan documented
- [x] Documentation complete
- [x] Unknowns 4.1, 4.2, 4.3, 4.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 7: Define Test Filtering Requirements

**Status:** ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 2-3 hours  
**Deadline:** Before Sprint 15 Day 1  
**Owner:** Development team  
**Dependencies:** Task 2 (Batch Infrastructure)  
**Unknowns Verified:** 5.1, 5.2, 5.3

### Objective

Define comprehensive filtering requirements for `run_full_test.py` to enable selective testing during development and debugging.

### Why This Matters

**Use cases for filtering:**
1. **Development:** Test single model while developing new feature
2. **Debugging:** Re-run only failing models
3. **Incremental testing:** Skip already-successful models
4. **Model subset:** Test only LP models, or only small models
5. **Stage-specific:** Run only parse, or only translate, or only solve
6. **Status-based:** Test models with specific error categories

**Without filtering:** Every test run processes all 160+ models, taking minutes even when debugging a single failure.

### Background

**From PROJECT_PLAN.md Sprint 15:**
- "Support filters: `--only-parse`, `--only-translate`, `--only-failing`, `--model=NAME`"

**Sprint 14 batch scripts:**
- batch_parse.py: Has `--model` flag for single model
- batch_translate.py: Similar filtering

**Additional filter needs:**
- By model type (LP, NLP, QCP)
- By convexity status (verified_convex, likely_convex)
- By parse status (success, failure, not_attempted)
- By error category
- By model size (variables, equations)
- Combination of filters (AND/OR logic)

### What Needs to Be Done

#### Step 1: Survey Existing Filtering (30-45 min)

1. **Review batch_parse.py filtering:**
   ```bash
   python scripts/gamslib/batch_parse.py --help
   ```

2. **Review batch_translate.py filtering:**
   ```bash
   python scripts/gamslib/batch_translate.py --help
   ```

3. **Document existing patterns:**
   - Command-line argument names
   - Filter logic implementation
   - Database queries used

4. **Identify reuse opportunities**

**Output:** Existing filter analysis

#### Step 2: Enumerate Use Cases (30-45 min)

1. **Development use cases:**
   - "Test only the model I'm debugging" → `--model=trnsport`
   - "Test only small models first" → `--max-variables=100`
   - "Test only LP models" → `--type=LP`

2. **Debugging use cases:**
   - "Re-run only failures" → `--only-failing`
   - "Test models with specific error" → `--error-category=syntax_error`
   - "Test models that parse but don't translate" → `--parse-success --translate-failure`

3. **Incremental testing use cases:**
   - "Skip already-solved models" → `--skip-completed`
   - "Test only untested models" → `--status=not_attempted`

4. **Stage-specific use cases:**
   - "Run only parse stage" → `--only-parse`
   - "Run only translate stage" → `--only-translate`
   - "Run parse and translate, skip solve" → `--skip-solve`

5. **Combination use cases:**
   - "Test LP models that parse but don't translate" → `--type=LP --parse-success --translate-failure`
   - "Test first 10 failing NLP models" → `--type=NLP --only-failing --limit=10`

**Output:** Use case catalog

#### Step 3: Design Filter API (45-60 min)

1. **Define command-line arguments:**

   **Model Selection:**
   - `--model=NAME` - Single model by name
   - `--type=TYPE` - Filter by type (LP, NLP, QCP)
   - `--convexity=STATUS` - Filter by convexity (verified_convex, likely_convex)
   - `--limit=N` - Limit to first N models
   - `--random=N` - Random sample of N models

   **Status Filtering:**
   - `--parse-success` - Only models that parsed successfully
   - `--parse-failure` - Only models that failed to parse
   - `--translate-success` - Only models that translated successfully
   - `--translate-failure` - Only models that failed to translate
   - `--solve-success` - Only models that solved successfully
   - `--solve-failure` - Only models that failed to solve
   - `--status=not_attempted` - Only untested models

   **Error Filtering:**
   - `--error-category=CATEGORY` - Models with specific error
   - `--parse-error=CATEGORY` - Parse-specific error filter
   - `--translate-error=CATEGORY` - Translate-specific error filter
   - `--solve-error=CATEGORY` - Solve-specific error filter

   **Stage Control:**
   - `--only-parse` - Run only parse stage
   - `--only-translate` - Run only translate stage (implies parse success)
   - `--only-solve` - Run only solve stage (implies translate success)
   - `--skip-parse` - Skip parse stage
   - `--skip-translate` - Skip translate stage
   - `--skip-solve` - Skip solve stage

   **Convenience Flags:**
   - `--only-failing` - Shorthand for parse-failure OR translate-failure OR solve-failure
   - `--skip-completed` - Skip models where all stages succeeded
   - `--quick` - Run first 10 models only

2. **Define filter combination logic:**
   - Multiple filters = AND logic (all must match)
   - Conflicting filters = error (e.g., --parse-success --parse-failure)

3. **Define default behavior:**
   - No filters = run all models through all stages
   - Stage flags override default (--only-parse = parse only)

**Output:** Filter API design

#### Step 4: Design Implementation Approach (30-45 min)

1. **Database query strategy:**
   ```python
   def filter_models(database, args):
       """Apply filters to model list."""
       models = database['models']
       
       # Model selection filters
       if args.model:
           models = [m for m in models if m['name'] == args.model]
       if args.type:
           models = [m for m in models if m['model_type'] == args.type]
       
       # Status filters
       if args.parse_success:
           models = [m for m in models if m['nlp2mcp_parse']['status'] == 'success']
       
       # ... etc
       
       return models
   ```

2. **Validation strategy:**
   - Check for conflicting flags
   - Validate filter values (e.g., valid error categories)
   - Warn if filter results in empty set

3. **Reporting strategy:**
   - Show filter applied: "Running 15 models matching: --type=LP --parse-success"
   - Show skipped count: "Skipped 45 models due to filters"

**Output:** Implementation pseudocode

#### Step 5: Create Filtering Requirements Document (30-45 min)

Create `docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md` with:

**Section 1: Overview**
- Purpose of filtering
- Use cases summary

**Section 2: Use Case Catalog**
- Development use cases
- Debugging use cases
- Incremental testing use cases
- Stage-specific use cases
- Combination use cases

**Section 3: Filter API**
- Complete command-line argument list
- Argument descriptions
- Default behaviors
- Combination logic (AND)
- Conflict detection

**Section 4: Implementation Guidelines**
- Database query patterns
- Validation approach
- Error handling
- Reporting format

**Section 5: Examples**
- 10-15 example filter commands with descriptions
- Expected output for each

**Section 6: Sprint 15 Scope**
- Minimum viable filters for Sprint 15
- Nice-to-have filters (can defer)
- Estimated implementation effort

### Changes

- Created `docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md`
- Updated `docs/planning/EPIC_3/SPRINT_15/KNOWN_UNKNOWNS.md` with verification results for Unknowns 5.1, 5.2, 5.3

### Result

**Key Findings:**
1. **Existing Filters (Sprint 14):** batch_parse.py and batch_translate.py provide `--model`, `--limit`, `--dry-run`, `--verbose`, `--save-every`
2. **Use Cases Documented:** 20 use cases across 5 categories (Development, Debugging, Incremental, Stage-specific, Combination)
3. **Filter API Designed:** 25+ command-line arguments organized into 6 groups (Model Selection, Status, Error, Stage Control, Output, Convenience)
4. **Combination Logic:** AND behavior for multiple filters with conflict detection for mutually exclusive flags
5. **Cascade Handling:** Pipeline stage dependencies (Parse → Translate → Solve → Compare) with `not_tested` vs `skipped` status semantics
6. **Summary Statistics:** Per-run stats, 4 output formats (Table, JSON, Quiet, Verbose), statistics by model type
7. **Sprint 15 MVP Filter Set:** 14 essential filters identified; nice-to-have filters (11) deferred

**Unknown Verifications:**
- Unknown 5.1: VERIFIED - MVP filter set with 14 essential filters for development/debugging workflows
- Unknown 5.2: VERIFIED - Cascading failure handling with `not_tested` status for skipped stages, implicit requirements for `--only-*` flags
- Unknown 5.3: VERIFIED - Summary statistics covering per-stage breakdown, comparison results, error categories, and multiple output formats

### Verification

```bash
# Verify requirements document created
ls -lh docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md

# Verify comprehensive coverage
grep "^###" docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md | wc -l
# Should have 15-25 filter options documented

# Verify examples included
grep "Example:" docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md | wc -l
# Should have 10+ examples
```

### Deliverables

- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/test_filtering_requirements.md`
- Use case catalog (15-20 use cases)
- Filter API specification (20-25 command-line arguments)
- Implementation guidelines
- 10-15 usage examples
- Sprint 15 scope recommendations
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.1, 5.2, 5.3

### Acceptance Criteria

- [x] All use cases from Step 2 documented
- [x] Command-line arguments defined with descriptions
- [x] Filter combination logic specified (AND/OR)
- [x] Conflict detection rules defined
- [x] Implementation approach outlined
- [x] 10+ usage examples provided
- [x] Sprint 15 minimum viable set identified
- [x] Unknowns 5.1, 5.2, 5.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 8: Research Performance Measurement Approach

**Status:** 🔵 NOT STARTED  
**Priority:** Medium  
**Estimated Time:** 2-3 hours  
**Deadline:** Before Sprint 15 Day 1  
**Owner:** Development team  
**Dependencies:** Task 2 (Batch Infrastructure)  
**Unknowns Verified:** 6.1, 6.2

### Objective

Research and define approach for accurately measuring parse, translate, and solve times to establish baseline metrics and detect performance regressions.

### Why This Matters

Sprint 15 needs to establish baseline performance metrics:
- "How long does parsing take on average?"
- "Are there models that take exceptionally long?"
- "Is performance improving over time?"

**Challenges:**
1. **Subprocess overhead:** Time includes Python subprocess creation
2. **I/O overhead:** File reading/writing time
3. **First run vs. subsequent:** OS caching effects
4. **Outliers:** Some models may be much slower

**Need:** Accurate, consistent timing methodology.

### Background

**Sprint 14 timing (from SPRINT_SUMMARY.md):**
- Average parse time: ~3.5s per model (unclear if this includes overhead)
- Average translate time: ~2.5s per model
- Total batch time: ~3 minutes for 160 models

**Questions:**
- Are these times pure parse/translate, or include I/O?
- How were they measured?
- Are they reproducible?

**Sprint 15 needs:**
- Accurate timing for each stage
- Statistical analysis (mean, median, stddev)
- Outlier detection
- Comparison baseline for future sprints

### What Needs to Be Done

#### Step 1: Review Existing Timing Implementation (30-45 min)

1. **Check batch_parse.py timing:**
   ```bash
   grep -A 10 "time" scripts/gamslib/batch_parse.py
   ```

2. **Check batch_translate.py timing:**
   ```bash
   grep -A 10 "time" scripts/gamslib/batch_translate.py
   ```

3. **Understand current approach:**
   - Using `time.time()`? `time.perf_counter()`?
   - What exactly is being timed?
   - Is subprocess overhead included?

4. **Review database storage:**
   ```bash
   jq '.models[0] | {parse_time: .nlp2mcp_parse.parse_time_seconds, translate_time: .nlp2mcp_translate.translate_time_seconds}' data/gamslib/gamslib_status.json
   ```

**Output:** Current timing analysis

#### Step 2: Research Timing Best Practices (30-45 min)

1. **Python timing approaches:**
   - `time.time()` - Wall clock time (affected by system clock adjustments)
   - `time.perf_counter()` - High-resolution performance counter (recommended)
   - `time.process_time()` - CPU time only (excludes I/O waits)

2. **Subprocess timing:**
   - Include subprocess creation overhead? (usually yes)
   - Measure only subprocess execution? (use process_time from subprocess)

3. **Statistical considerations:**
   - Single run vs. multiple runs
   - Handling outliers (median vs. mean)
   - Warmup runs to prime caches

4. **Benchmarking libraries:**
   - `timeit` module (for microbenchmarks)
   - `pytest-benchmark` (for test timing)
   - Custom timing (for batch operations)

**Output:** Best practices summary

#### Step 3: Design Timing Methodology (45-60 min)

1. **Define what to measure:**

   **Parse timing:**
   - Start: Just before nlp2mcp parse invocation
   - End: Just after parse completes (success or failure)
   - Includes: Parse logic, IR construction
   - Excludes: Database loading, file I/O (reading .gms, writing results)

   **Translate timing:**
   - Start: Just before translation begins (after parse success)
   - End: Just after MCP file written
   - Includes: Differentiation, KKT generation, code emission
   - Excludes: Database operations

   **Solve timing:**
   - Start: Just before GAMS invocation
   - End: Just after GAMS completes
   - Includes: GAMS subprocess, PATH solver, file I/O
   - Excludes: Solution extraction from .lst

2. **Choose timing function:**
   - Recommended: `time.perf_counter()` for wall time
   - Record both start and end for precision

3. **Handle failures:**
   - Still record time even if stage fails
   - Distinguish timeout from normal failure

4. **Statistical analysis:**
   - Record individual times in database
   - Calculate summary statistics:
     - Count, mean, median, stddev
     - Min, max
     - 25th, 75th, 95th percentiles
   - Identify outliers (> 2 stddev from mean)

**Output:** Timing methodology specification

#### Step 4: Design Baseline Documentation (30-45 min)

1. **What to record in baseline:**
   - Sprint 15 start date
   - nlp2mcp version
   - Python version
   - Hardware specs (CPU, RAM)
   - Model counts by type
   - Timing statistics for each stage

2. **Baseline document format:**
   ```markdown
   # Sprint 15 Performance Baseline
   
   **Date:** 2026-01-22
   **nlp2mcp version:** 0.3.0
   **Python:** 3.12.0
   **System:** macOS 14.6, M1 Max, 32GB RAM
   
   ## Parse Performance
   - Models tested: 160
   - Success: 34 (21.3%)
   - Mean time: 3.5s
   - Median time: 2.1s
   - 95th percentile: 12.3s
   - Outliers: 5 models > 20s
   
   ## Translate Performance
   ...
   ```

3. **Storage location:**
   - `docs/planning/EPIC_3/SPRINT_15/BASELINE_METRICS.md`
   - Or in database as metadata?

**Output:** Baseline documentation format

#### Step 5: Create Performance Measurement Guide (30-45 min)

Create `docs/planning/EPIC_3/SPRINT_15/prep-tasks/performance_measurement.md` with:

**Section 1: Timing Methodology**
- What to measure for each stage
- Timer function to use (`perf_counter`)
- Handling failures and timeouts

**Section 2: Statistical Analysis**
- Summary statistics to calculate
- Outlier detection approach
- Comparison methodology (vs. previous baseline)

**Section 3: Baseline Documentation**
- What to record
- Document format
- Update procedures

**Section 4: Implementation Guidelines**
- Code patterns for timing
- Database storage format
- Reporting format

**Section 5: Sprint 15 Baseline Plan**
- When to record baseline (Day 1 or after full pipeline complete?)
- What models to include
- How to document

### Changes

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify guide created
ls -lh docs/planning/EPIC_3/SPRINT_15/prep-tasks/performance_measurement.md

# Verify timing methodology defined
grep -i "perf_counter\|timing" docs/planning/EPIC_3/SPRINT_15/prep-tasks/performance_measurement.md

# Verify statistical analysis defined
grep -i "mean\|median\|stddev" docs/planning/EPIC_3/SPRINT_15/prep-tasks/performance_measurement.md
```

### Deliverables

- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/performance_measurement.md`
- Timing methodology specification
- Statistical analysis approach
- Baseline documentation format
- Implementation guidelines
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 6.1, 6.2

### Acceptance Criteria

- [ ] Timing methodology defined for parse, translate, solve
- [ ] Timer function selected (`perf_counter`)
- [ ] Statistical analysis approach specified
- [ ] Outlier detection defined
- [ ] Baseline documentation format created
- [ ] Sprint 15 baseline plan outlined
- [ ] Unknowns 6.1, 6.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 9: Research Numerical Tolerance Best Practices

**Status:** 🔵 NOT STARTED  
**Priority:** High  
**Estimated Time:** 2-3 hours  
**Deadline:** Before Sprint 15 Day 1  
**Owner:** Development team  
**Dependencies:** Task 3 (Solution Comparison)  
**Unknowns Verified:** 3.1, 3.2

### Objective

Research appropriate numerical tolerance values for comparing NLP and MCP solutions, with justification from optimization literature and solver defaults.

### Why This Matters

**Core validation question:** When are two objective values "close enough"?
- Too loose (e.g., 1e-3): May miss real errors
- Too tight (e.g., 1e-12): May flag false positives due to numerical precision

**From PROJECT_PLAN.md:** "Configurable tolerance (default: 1e-6 relative, 1e-8 absolute)"
- Where did these values come from?
- Are they appropriate for GAMSLIB models?
- Should they be different for LP vs. NLP?

### Background

**Numerical comparison approaches:**
1. **Absolute tolerance:** `|a - b| <= atol`
   - Good for values near zero
   - Bad for large values (1000.0 vs. 1000.001 would fail)

2. **Relative tolerance:** `|a - b| / |b| <= rtol`
   - Good for large values
   - Bad for values near zero (division by ~0)

3. **Combined:** `|a - b| <= atol + rtol * |b|`
   - Recommended approach
   - Used by NumPy's `allclose()`, SciPy, etc.

**Questions:**
- What tolerances do GAMS solvers use?
- What do PATH, CONOPT, IPOPT use internally?
- What do other optimization testing frameworks use?

### What Needs to Be Done

#### Step 1: Survey GAMS Solver Tolerances (30-45 min)

1. **Check CONOPT documentation:**
   - Optimality tolerance
   - Feasibility tolerance
   - Documentation location: GAMS docs or CONOPT manual

2. **Check IPOPT documentation:**
   - `tol` option (default: 1e-8)
   - Dual infeasibility tolerance
   - Complementarity tolerance

3. **Check PATH documentation:**
   - Convergence tolerance
   - Complementarity tolerance

4. **Check CPLEX (for LP):**
   - Optimality tolerance (default: 1e-6)
   - Feasibility tolerance (default: 1e-6)

5. **Document defaults:**
   | Solver | Optimality Tolerance | Feasibility Tolerance |
   |--------|---------------------|----------------------|
   | CONOPT | ? | ? |
   | IPOPT | 1e-8 | ? |
   | PATH | ? | ? |
   | CPLEX | 1e-6 | 1e-6 |

**Output:** Solver tolerance survey

#### Step 2: Survey Optimization Testing Practices (30-45 min)

1. **Check CUTEst (optimization test set):**
   - How do they compare solutions?
   - What tolerances are used?

2. **Check NEOS Server (optimization server):**
   - Solution validation approach
   - Tolerances used

3. **Check academic papers:**
   - Search: "optimization solver validation tolerance"
   - Note commonly used values

4. **Check other tools:**
   - NumPy `allclose`: default rtol=1e-5, atol=1e-8
   - SciPy `optimization`: varies by algorithm
   - Julia JuMP testing: what do they use?

**Output:** Testing practice survey

#### Step 3: Analyze GAMSLIB Model Characteristics (30-45 min)

1. **Check objective value ranges in Sprint 13 data:**
   ```bash
   jq '.models[] | select(.convexity_verification.objective != null) | .convexity_verification.objective' data/gamslib/catalog.json | sort -n
   ```

2. **Identify value ranges:**
   - Minimum positive objective (closest to zero)
   - Maximum objective
   - Typical range (median, IQR)

3. **Consider implications:**
   - If objectives range from 0.001 to 1e9, relative tolerance critical
   - If many objectives near zero, absolute tolerance critical

4. **Document model characteristics**

**Output:** GAMSLIB objective value analysis

#### Step 4: Define Tolerance Recommendations (30-45 min)

1. **Propose default values:**

   **For general models:**
   - Relative tolerance: 1e-6 (0.0001% difference)
     - Matches CPLEX default
     - Slightly looser than IPOPT (1e-8)
   - Absolute tolerance: 1e-8
     - Matches NumPy default
     - For objectives near zero

   **For specific model types:**
   - LP models: Could use tighter (1e-8 relative)?
   - NLP models: May need looser (1e-5 relative)?

2. **Justify choices:**
   - Alignment with solver defaults
   - Balance between false positives and false negatives
   - Numerical precision limits (double = ~15-17 decimal digits)

3. **Define configuration approach:**
   - Environment variables: `NLP2MCP_RTOL`, `NLP2MCP_ATOL`
   - Command-line args: `--rtol=1e-6 --atol=1e-8`
   - Config file: `config.toml`

4. **Define edge cases:**
   - Objective = 0 exactly: Use absolute tolerance only
   - Very large objectives (> 1e9): May need looser relative
   - Very small objectives (< 1e-6): May need looser absolute

**Output:** Tolerance recommendations

#### Step 5: Create Tolerance Research Document (30-45 min)

Create `docs/planning/EPIC_3/SPRINT_15/prep-tasks/numerical_tolerance_research.md` with:

**Section 1: Background**
- Absolute vs. relative vs. combined tolerance
- Numerical precision limits
- Why tolerances matter

**Section 2: Solver Tolerance Survey**
- CONOPT, IPOPT, PATH, CPLEX defaults
- Table of solver tolerances
- Industry standard practices

**Section 3: Testing Practice Survey**
- CUTEst, NEOS, academic practices
- NumPy/SciPy defaults
- Other optimization frameworks

**Section 4: GAMSLIB Analysis**
- Objective value range
- Implications for tolerance selection

**Section 5: Recommendations**
- Default tolerance values (rtol=1e-6, atol=1e-8)
- Justification for each
- Configuration approach
- Edge case handling

**Section 6: Implementation Notes**
- Comparison algorithm: `|a - b| <= atol + rtol * |b|`
- Code examples
- Testing approach

### Changes

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify research document created
ls -lh docs/planning/EPIC_3/SPRINT_15/prep-tasks/numerical_tolerance_research.md

# Verify solver survey included
grep -i "CONOPT\|IPOPT\|PATH\|CPLEX" docs/planning/EPIC_3/SPRINT_15/prep-tasks/numerical_tolerance_research.md

# Verify recommendations included
grep -i "recommendation\|rtol\|atol" docs/planning/EPIC_3/SPRINT_15/prep-tasks/numerical_tolerance_research.md
```

### Deliverables

- `docs/planning/EPIC_3/SPRINT_15/prep-tasks/numerical_tolerance_research.md`
- Solver tolerance survey (CONOPT, IPOPT, PATH, CPLEX)
- Testing practice survey
- GAMSLIB objective value analysis
- Tolerance recommendations with justification
- Implementation approach
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.2

### Acceptance Criteria

- [ ] Solver tolerances documented for 4+ solvers
- [ ] Testing practices surveyed (CUTEst, NEOS, NumPy)
- [ ] GAMSLIB objective value range analyzed
- [ ] Default tolerances recommended (rtol, atol)
- [ ] Justification provided for each value
- [ ] Configuration approach defined
- [ ] Edge cases documented
- [ ] Comparison algorithm specified
- [ ] Unknowns 3.1, 3.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 10: Plan Sprint 15 Detailed Schedule

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 4-5 hours  
**Deadline:** Before Sprint 15 Day 1  
**Owner:** Sprint planning team  
**Dependencies:** All tasks (1-9)  
**Unknowns Verified:** All unknowns (integrates findings from Tasks 1-9)

### Objective

Create detailed day-by-day plan for Sprint 15 incorporating all research findings from prep tasks and defining specific deliverables for each day.

### Why This Matters

Sprint 15 has 10 working days to deliver:
- Parse testing infrastructure
- Translation testing infrastructure
- MCP solve testing infrastructure
- Full pipeline runner
- Initial baseline metrics

**Without detailed plan:**
- Risk of scope creep
- Unclear dependencies between components
- No checkpoints to track progress
- Potential bottlenecks not identified

**With detailed plan:**
- Clear daily objectives
- Defined checkpoints
- Risk mitigation strategies
- Effort estimates validated

### Background

**Sprint 15 scope (from PROJECT_PLAN.md):**
- Estimated effort: 26-33 hours (~3-4 hours/day for 10 days)
- 4 major components (parse, translate, solve, pipeline)
- Multiple cross-dependencies

**Prep task findings to incorporate:**
- Task 1: Known unknowns (identify risks)
- Task 2: Batch infrastructure (reuse vs. new)
- Task 3: Solution comparison (approach validated)
- Task 4: Error taxonomy (categories defined)
- Task 5: PATH solver (integration validated)
- Task 6: Database schema (extensions designed)
- Task 7: Test filtering (requirements defined)
- Task 8: Performance measurement (methodology defined)
- Task 9: Numerical tolerance (values selected)

### What Needs to Be Done

#### Step 1: Review All Prep Task Outcomes (30-45 min)

1. **Read all prep task deliverables:**
   - KNOWN_UNKNOWNS.md
   - batch_infrastructure_assessment.md
   - solution_comparison_research.md
   - error_taxonomy.md
   - path_solver_integration.md
   - schema_extensions.md (draft schema)
   - test_filtering_requirements.md
   - performance_measurement.md
   - numerical_tolerance_research.md

2. **Extract key decisions:**
   - Reuse batch scripts or create new?
   - Schema version (2.1.0 or 3.0.0)?
   - Tolerance values (rtol, atol)?
   - Error categories (full list)?
   - Filter flags (MVP set)?

3. **Identify blocking issues:**
   - Any critical unknowns still unresolved?
   - Any dependencies that could cause delays?

**Output:** Key decisions summary

#### Step 2: Define Sprint 15 Phases (45-60 min)

1. **Break into logical phases:**

   **Phase 1: Foundation (Days 1-2)**
   - Update database schema to v2.1.0
   - Extend error taxonomies in code
   - Set up solve infrastructure basics

   **Phase 2: Parse Testing (Days 2-3)**
   - Enhance/create test_parse.py
   - Implement refined error categorization
   - Run initial parse tests

   **Phase 3: Translation Testing (Days 3-4)**
   - Enhance/create test_translate.py
   - Implement translation error categorization
   - Run initial translation tests

   **Phase 4: Solve Testing (Days 5-7)**
   - Implement test_solve.py
   - Implement solution comparison
   - Run initial solve tests

   **Phase 5: Pipeline Integration (Days 8-9)**
   - Implement run_full_test.py
   - Implement filtering
   - Run full pipeline

   **Phase 6: Baseline and Documentation (Day 10)**
   - Record baseline metrics
   - Generate reports
   - Update documentation

2. **Define phase dependencies:**
   - Phase 2 depends on Phase 1 (schema must be updated)
   - Phase 4 depends on Phases 2-3 (models must parse and translate)
   - Phase 5 depends on Phases 2-4 (all components must exist)

**Output:** Phase structure

#### Step 3: Create Day-by-Day Plan (90-120 min)

For each day, define:
- **Focus:** Primary objective
- **Tasks:** Specific implementation tasks (3-5 per day)
- **Deliverables:** Concrete outputs
- **Acceptance Criteria:** How to verify day is complete
- **Time Estimate:** Hours (should total 3-4 hours/day)
- **Dependencies:** What must be done first
- **Risks:** Potential blockers

**Example Day Structure:**

```markdown
### Day 3: Translation Testing Implementation

**Focus:** Create/enhance translation testing script with error categorization

**Tasks:**
1. Implement test_translate.py (or enhance batch_translate.py) (2h)
   - Add error categorization from Task 4 taxonomy
   - Add database update with new schema
   - Add performance timing
2. Test on 5-10 models (30min)
3. Fix issues and refine (1h)
4. Update documentation (30min)

**Deliverables:**
- test_translate.py (functional)
- Updated database with translation error categories
- Translation timing baseline (initial)

**Acceptance Criteria:**
- [ ] Script runs on all parsed models
- [ ] Error categories assigned correctly
- [ ] Database updated with results
- [ ] Performance timing recorded

**Time Estimate:** 4 hours

**Dependencies:**
- Day 2 parse testing complete (need parsed models)
- Schema updated (from Day 1)

**Risks:**
- Translation errors may reveal new categories not in taxonomy
- Performance measurement may need refinement
```

**Create plan for all 10 days following this format.**

#### Step 4: Define Checkpoints (20-30 min)

1. **Identify critical checkpoints:**

   **Checkpoint 1 (End of Day 2):** Parse testing functional
   - Success criteria: Can test all models, categorize errors, update database

   **Checkpoint 2 (End of Day 4):** Translation testing functional
   - Success criteria: Can test all parsed models, categorize errors

   **Checkpoint 3 (End of Day 7):** Solve testing functional
   - Success criteria: Can solve MCPs, compare solutions, detect mismatches

   **Checkpoint 4 (End of Day 9):** Full pipeline operational
   - Success criteria: Can run full pipeline with filtering

   **Checkpoint 5 (End of Day 10):** Baseline recorded, sprint complete
   - Success criteria: All deliverables met, baseline documented

2. **Define checkpoint validation:**
   - What tests to run
   - What metrics to check
   - How to document results

**Output:** Checkpoint plan

#### Step 5: Estimate Effort and Validate Schedule (30-45 min)

1. **Sum effort estimates:**
   - Day 1: 4h
   - Day 2: 4h
   - ... etc
   - Total: Should be 26-33h (from PROJECT_PLAN.md)

2. **Check for overload:**
   - Any day > 5h? (may need to split)
   - Any day < 2h? (may be underestimating)

3. **Validate against PROJECT_PLAN.md estimates:**
   - Parse testing: 8-10h (Days 2-3)
   - Translation testing: 6-8h (Days 3-4)
   - Solve testing: 8-10h (Days 5-7)
   - Pipeline runner: 4-5h (Days 8-9)
   - Documentation: 2-3h (Day 10)

4. **Adjust if needed:**
   - Move tasks between days
   - Add buffer time
   - Defer non-critical features

**Output:** Validated effort estimates

#### Step 6: Identify Risks and Mitigation (30-45 min)

1. **Technical risks:**
   - PATH solver integration issues → Mitigation: Validated in Task 5
   - Solution comparison edge cases → Mitigation: Research in Task 3
   - Performance issues → Mitigation: Methodology in Task 8

2. **Schedule risks:**
   - Error taxonomy incomplete → Mitigation: Can add categories during sprint
   - Solve testing takes longer than estimated → Mitigation: 3-day buffer (Days 5-7)

3. **Dependency risks:**
   - Blocking on earlier phase → Mitigation: Clear checkpoints

4. **Document mitigation strategies**

**Output:** Risk assessment

#### Step 7: Create PLAN.md Document (60-90 min)

Create `docs/planning/EPIC_3/SPRINT_15/PLAN.md` following format of Sprint 13/14 PLAN.md:

**Structure:**
1. Executive Summary
   - Sprint goal
   - Key deliverables
   - Effort estimate
   - Prep task summary

2. Day-by-Day Plan
   - Days 1-10 with full detail (per Step 3 format)

3. Checkpoints
   - 5 checkpoints with validation criteria

4. Deliverables
   - Complete list from PROJECT_PLAN.md

5. Acceptance Criteria
   - From PROJECT_PLAN.md

6. Risk Assessment
   - Risks and mitigations from Step 6

7. Dependencies
   - Sprint 14 deliverables (required)
   - Prep task outputs (required)

8. Resource Allocation
   - Effort by phase

9. Appendix
   - Prep task cross-references
   - Unknown resolution status (from Task 1)

### Changes

To be completed during task execution.

### Result

To be completed during task execution.

### Verification

```bash
# Verify PLAN.md created
ls -lh docs/planning/EPIC_3/SPRINT_15/PLAN.md

# Verify structure
grep "^## " docs/planning/EPIC_3/SPRINT_15/PLAN.md
# Should show sections: Executive Summary, Day-by-Day Plan, Checkpoints, etc.

# Verify all 10 days planned
grep "^### Day" docs/planning/EPIC_3/SPRINT_15/PLAN.md | wc -l
# Should show 10

# Verify checkpoints defined
grep "^#### Checkpoint" docs/planning/EPIC_3/SPRINT_15/PLAN.md | wc -l
# Should show 5

# Verify effort totals
grep -i "total.*hour" docs/planning/EPIC_3/SPRINT_15/PLAN.md
```

### Deliverables

- `docs/planning/EPIC_3/SPRINT_15/PLAN.md` (comprehensive sprint plan)
- Day-by-day breakdown (10 days)
- Checkpoint definitions (5 checkpoints)
- Risk assessment and mitigation
- Effort validation (26-33 hours total)
- Cross-references to all prep tasks
- Updated KNOWN_UNKNOWNS.md with all verification results integrated

### Acceptance Criteria

- [ ] All 10 days planned with tasks, deliverables, acceptance criteria
- [ ] 5 checkpoints defined with validation criteria
- [ ] Effort estimates total 26-33 hours
- [ ] All prep task findings incorporated
- [ ] Risks identified with mitigation strategies
- [ ] Dependencies clearly documented
- [ ] Deliverables match PROJECT_PLAN.md
- [ ] Acceptance criteria match PROJECT_PLAN.md
- [ ] All unknowns verified and updated in KNOWN_UNKNOWNS.md

---

## Summary

### Total Estimated Prep Effort

| Task | Est. Time | Critical Path |
|------|-----------|---------------|
| 1. Known Unknowns | 3-4h | ✅ |
| 2. Batch Infrastructure | 2-3h | ✅ |
| 3. Solution Comparison | 4-5h | ✅ |
| 4. Error Taxonomy | 3-4h | |
| 5. PATH Solver | 2-3h | ✅ |
| 6. Database Schema | 3-4h | ✅ |
| 7. Test Filtering | 2-3h | |
| 8. Performance Measurement | 2-3h | |
| 9. Numerical Tolerance | 2-3h | |
| 10. Detailed Schedule | 4-5h | ✅ |
| **Total** | **27-37h** | **~20h critical** |

### Critical Path

Tasks that must complete before Sprint 15 can begin:
1. Task 1 (Known Unknowns) → Identifies all risks
2. Task 2 (Batch Infrastructure) → Determines reuse strategy
3. Task 3 (Solution Comparison) → Validates core validation approach
4. Task 5 (PATH Solver) → Confirms solve infrastructure viable
5. Task 6 (Database Schema) → Must be designed before implementation
6. Task 10 (Detailed Schedule) → Organizes all findings into executable plan

**Estimated critical path time:** ~20 hours (~2.5 working days)

### Success Criteria

Sprint 15 prep is complete when:
- [ ] All 10 prep tasks completed
- [ ] KNOWN_UNKNOWNS.md created with 20+ unknowns
- [ ] Critical unknowns resolved or mitigated
- [ ] Database schema v2.1.0 drafted and validated
- [ ] Solution comparison strategy validated
- [ ] PATH solver integration confirmed
- [ ] Error taxonomy comprehensive (30-40 categories)
- [ ] PLAN.md created with day-by-day breakdown
- [ ] All prep task deliverables reviewed and approved

### Prep Task Coordination

**Parallelization opportunities:**
- Tasks 2, 4, 5, 7, 8, 9 can run in parallel after Task 1
- Task 3 should inform Task 6 (solution_comparison object design)
- Task 4 should inform Task 6 (error category enums)
- Task 10 depends on all others

**Recommended sequence:**
1. **Week 1, Day 1-2:** Task 1 (Known Unknowns)
2. **Week 1, Day 3-5:** Tasks 2, 5, 7, 8, 9 in parallel
3. **Week 2, Day 1-2:** Tasks 3, 4 in parallel
4. **Week 2, Day 3:** Task 6 (after 3 and 4 complete)
5. **Week 2, Day 4-5:** Task 10 (after all complete)

---

## Appendix A: Cross-References

### PROJECT_PLAN.md
- Sprint 15 Goals: Lines 229-330
- Acceptance Criteria: Lines 310-330
- Estimated Effort: 26-33 hours

### Sprint 14 Deliverables (Dependencies)
- `data/gamslib/gamslib_status.json` (v2.0.0 database)
- `data/gamslib/schema.json` (v2.0.0 schema)
- `scripts/gamslib/batch_parse.py` (parse infrastructure)
- `scripts/gamslib/batch_translate.py` (translate infrastructure)
- `scripts/gamslib/db_manager.py` (database management)
- `docs/infrastructure/GAMSLIB_DATABASE_SCHEMA.md` (schema documentation)

### Sprint 14 Recommendations (Inputs)
- "Address top syntax error patterns" → Task 4 (Error Taxonomy)
- "Add MCP solve verification" → Task 3, 5 (Solution Comparison, PATH Solver)
- "Implement objective value comparison" → Task 3, 9 (Solution Comparison, Tolerance)

### Research Documents
- `docs/concepts/IDEA.md` - KKT transformation concepts
- `docs/concepts/NLP2MCP_HIGH_LEVEL.md` - High-level architecture

### Epic 3 Goals
- `docs/planning/EPIC_3/GOALS.md` - Epic objectives (if exists)
- `docs/planning/EPIC_3/PROJECT_PLAN.md` - Overall epic plan

---

## Appendix B: Prep Task Directory Structure

```
docs/planning/EPIC_3/SPRINT_15/
├── PREP_PLAN.md                    # This document
├── KNOWN_UNKNOWNS.md               # Task 1 output
├── PLAN.md                         # Task 10 output
└── prep-tasks/
    ├── batch_infrastructure_assessment.md      # Task 2
    ├── solution_comparison_research.md         # Task 3
    ├── error_taxonomy.md                       # Task 4
    ├── path_solver_integration.md              # Task 5
    ├── schema_v2.1.0_draft.json               # Task 6 (draft)
    ├── schema_extensions.md                    # Task 6 (docs)
    ├── test_filtering_requirements.md          # Task 7
    ├── performance_measurement.md              # Task 8
    └── numerical_tolerance_research.md         # Task 9
```

---

*Document created: January 2026*  
*Sprint 15 Target Start: After Sprint 14 complete*  
*Estimated Prep Duration: 3.5-5 working days (27-37 hours)*

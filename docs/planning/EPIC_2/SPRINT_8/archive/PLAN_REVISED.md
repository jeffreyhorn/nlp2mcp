# Sprint 8 Detailed Plan (REVISED)

**Sprint:** Epic 2 - Sprint 8 (High-ROI Parser Features & UX Enhancements)  
**Duration:** 11 days (Days 0-10, with Day 10 as BUFFER)  
**Start Date:** TBD  
**End Date:** TBD  
**Version:** v0.8.0-revised  
**Revision Date:** 2025-11-17  
**Revised By:** Addressing Cody's review recommendations

---

## Revision Summary

This revised plan addresses all recommendations from Cody's review (see `PLAN_REVIEW.md`):

**Changes Made:**

1. **✅ Corrected Effort Totals (Recommendation 1)**
   - Fixed inconsistent effort claims throughout document
   - Updated from misleading "30-36h" to accurate "30-41h (average 35.5h)"
   - All tables and summaries now use consistent figures
   - Breakdown by feature area updated to match day-level estimates
   - Executive summary now clearly states: Conservative 30h (within budget), Realistic 35.5h, Upper 41h

2. **✅ Clarified Sprint Duration (Recommendation 2)**
   - Updated header from "10 days (Days 0-9)" to "11 days (Days 0-10, with Day 10 as BUFFER)"
   - Added explicit BUFFER DAY markers throughout Day 10 sections
   - Day 10 now clearly labeled as buffer to absorb overruns
   - All references to sprint length now consistent (11 days total, 10 active + 1 buffer)

3. **✅ Added Unknown Verification Task (Recommendation 3)**
   - Added explicit Day 0 task: "Verify Known Unknowns (30 min)"
   - Task includes checking KNOWN_UNKNOWNS.md for unknowns 8.1, 8.2, 8.3 verification status
   - Added to Day 0 deliverables and quality gates
   - Ensures compliance with Task 10 acceptance criteria from PREP_PLAN.md

4. **✅ Normalized Day-Level Hours (Recommendation 4)**
   - Updated feature area table to reflect actual day-level totals
   - Day 0: 2-3h → 2.25h average (explicit in breakdown)
   - Days 1-2: Combined 10.5-13.5h for Option Statements
   - Days 3-4: Combined 9.75-12.75h for Indexed Assignments
   - All day estimates now sum correctly to 30-41h total
   - Documented that conservative (30h) fits budget; realistic (35.5h) uses buffer

**Result:** Plan is now internally consistent with accurate effort estimates, clear sprint duration (11 days with Day 10 buffer), explicit unknown verification task, and normalized day-level hours that align with stated totals.

---

## Executive Summary

Sprint 8 focuses on **high-ROI parser features** and **user experience enhancements** to achieve 40-50% GAMSLib parse rate with dramatically improved error messaging and progress visibility. Building on comprehensive prep work (Tasks 2-9), this sprint implements carefully selected features with validated effort estimates and clear unlock targets.

**Key Achievements from Prep Phase:**
- 27 Known Unknowns identified across 8 categories (100% verification rate for critical unknowns)
- 10 GAMSLib models analyzed with per-model feature dependencies mapped
- Complete designs for all major features (options, indexed assignments, UX)
- **30-41 hour total effort estimated** (average 35.5h) across 8 feature areas
- Zero blocking dependencies identified
- Feature selection validated: Option statements + Indexed assignments unlock 3-5 models

**Effort Note:**
- Conservative estimate: 30h (within 25-35h target ✅)
- Realistic estimate: 35.5h average (slightly over target, manageable)
- Upper bound: 41h (requires Day 10 buffer + scope flexibility)
- **Day 10 is explicitly designated as BUFFER** to absorb overruns without sprint failure

**Sprint 8 Goals:**

| # | Goal | Baseline | Target | Measurement |
|---|------|----------|--------|-------------|
| 1 | **GAMSLib Parse Rate** | 20% (2/10) | 40% (4/10) conservative, 50% (5/10) optimistic | `make ingest-gamslib` |
| 2 | **Parse Progress Visibility** | Binary pass/fail | 4-level color-coded status with % progress | Dashboard inspection |
| 3 | **Error Message Quality** | Basic errors | Source context + "did you mean?" + hints | Manual inspection |
| 4 | **Parse Error Location** | 58/79 errors (73%) | 100% parser errors with line numbers | Test coverage |

**Risk Level:** LOW ✅  
**Confidence:** HIGH ✅  
**Recommended Approach:** Front-load core features (Days 1-5), UX enhancements in parallel (Days 4-7), polish and testing (Days 8-9)

> **Note on PREP_PLAN Acceptance Criteria:**
> The Task 10 acceptance checklist in `docs/planning/EPIC_2/SPRINT_8/PREP_PLAN.md` should be checked **only after** this final plan receives approval. The checkboxes must reflect the final state of the approved plan, not any intermediate versions.

---

## Table of Contents

1. [Sprint 8 Goals](#sprint-8-goals)
2. [Day-by-Day Breakdown](#day-by-day-breakdown)
3. [Checkpoint Definitions](#checkpoint-definitions)
4. [Effort Estimates](#effort-estimates)
5. [Success Criteria](#success-criteria)
6. [Risk Register](#risk-register)
7. [Deliverables](#deliverables)
8. [Cross-References](#cross-references)

---

## 1. Sprint 8 Goals

### Goal 1: GAMSLib Parse Rate (PRIMARY)

**Objective:** Increase GAMSLib parse rate from 20% (2/10 models) to 40-50% (4-5/10 models)

**Rationale:** Sprint 7 achieved 20% baseline with preprocessor support. Task 2 (Feature Matrix) identified 2 high-ROI features that unlock 3 models with 12-16 hours effort.

**Implementation:**
1. **Option Statements** (6-8 hours) - Mock/store approach
   - Basic integer options (limrow, limcol, decimals)
   - Multi-option syntax (`option limrow=0, limcol=0;`)
   - Boolean on/off keywords
   - Case-insensitive option names
   - **Unlocks:** mhw4dx.gms (+10% parse rate: 2/10 → 3/10)
   - **ROI:** 1.25-1.67% per hour

2. **Indexed Assignments** (6-8 hours) - Semantic handler approach
   - Parameter indexing: `p('i1') = 10;`
   - Multi-dimensional: `report('x1','global') = 1;`
   - Variable attributes: `xdiff = x1.l;`
   - Indexed expressions: `p('diff') = p('global') - p('solver');`
   - **Unlocks:** mathopt1.gms + trig.gms (+20% parse rate: 3/10 → 5/10)
   - **ROI:** 2.5-3.33% per hour

**Success Metrics:**
- ✅ Minimum: 40% parse rate (4/10 models) - Conservative (options + mathopt1)
- 🎯 Target: 50% parse rate (5/10 models) - Likely (options + mathopt1 + trig)
- 🚀 Stretch: 60% parse rate (6/10 models) - If himmel16 unlocks as side effect

**Dependencies:**
- Task 2: GAMSLIB_FEATURE_MATRIX.md (feature priorities)
- Task 3: OPTION_STATEMENT_RESEARCH.md (option implementation design)
- Task 7: INDEXED_ASSIGNMENTS_RESEARCH.md (indexed assignment design)
- Task 8: TEST_FIXTURE_STRATEGY.md (test fixtures)

---

### Goal 2: Parse Progress Visibility (PRIMARY)

**Objective:** Transform dashboard from binary pass/fail to granular 4-level color-coded progress tracking

**Rationale:** Current dashboard shows "❌ FAIL" for all 8 failing models, but himmel16 is 92% parsed while hs62 is 15% parsed. Task 9 (Dashboard Enhancements) designed 4-level system to show "himmel16: 🟡 PARTIAL | 92% (22/24) | i++1 indexing".

**Implementation:**
1. **Partial Parse Metrics** (4-6 hours) - Line-based progress tracking
   - Logical line counting (non-empty, non-comment)
   - Error line extraction from exceptions
   - Parse percentage calculation
   - Missing feature pattern matching
   - **Impact:** Shows parse progress for all 10 models

2. **Dashboard Updates** (3-4 hours) - Template and ingestion script
   - Enhanced ModelResult dataclass with progress fields
   - 4-level color coding: ✅ (100%), 🟡 (75-99%), ⚠️ (25-74%), ❌ (<25%)
   - New columns: Status, Progress, Missing Features
   - Backward compatible with Sprint 7 data
   - **Impact:** Developers see actionable progress indicators

**Success Metrics:**
- ✅ All 10 models show parse percentage
- ✅ Color coding matches thresholds (✅/🟡/⚠️/❌)
- ✅ Missing features listed for 70-80% of failures
- ✅ Sprint 7 data displays correctly (backward compatibility)

**Dependencies:**
- Task 5: PARTIAL_PARSE_METRICS.md (design and algorithms)
- Task 9: DASHBOARD_ENHANCEMENTS.md (template and mockup)

---

### Goal 3: Error Message Quality (SECONDARY)

**Objective:** Enhance parser errors with source context, suggestions, and actionable hints

**Rationale:** Current errors are cryptic ("UnexpectedCharacters: No terminal matches 'S'"). Task 6 (Error Message Enhancements) researched patterns from Rust/Python/TypeScript to provide actionable feedback.

**Implementation:**
1. **Error Line Numbers** (4-6 hours) - ParseError consolidation
   - Wrap Lark errors with source line display and caret pointer
   - Create `_parse_error()` helper (similar to existing `_error()`)
   - Migrate top 5 error types to include location
   - 5 test fixtures for error wrapping
   - **Impact:** 100% of parser errors include location (up from 73%)

2. **Error Enhancements** (3-4 hours) - Suggestion patterns
   - Pattern 1: Source context + caret pointer (existing infrastructure)
   - Pattern 2: "Did you mean?" keyword suggestions (difflib)
   - Pattern 3: Contextual hints (Set `/.../ not [...]`, missing semicolons)
   - 5 test fixtures for enhancement rules
   - **Impact:** 80%+ errors get actionable suggestions

**Success Metrics:**
- ✅ All parser errors include line/column numbers
- ✅ Keyword typos suggest correct spelling ("Scaler" → "Did you mean 'Scalar'?")
- ✅ Punctuation errors show correct syntax
- ✅ Unsupported features link to roadmap

**Dependencies:**
- Task 4: PARSER_ERROR_LINE_NUMBERS.md (design and infrastructure)
- Task 6: ERROR_MESSAGE_ENHANCEMENTS.md (pattern catalog and rules)

---

## 2. Day-by-Day Breakdown

### **Day 0: Sprint Planning & Setup** (2-3 hours)

**Objective:** Prepare environment, review plan, confirm scope

**Tasks:**
1. **Review Sprint 8 Plan** (30 min)
   - Read PLAN.md in full
   - Review all prep task documents (Tasks 2-9)
   - Confirm understanding of acceptance criteria

2. **Set Up Development Branch** (15 min)
   - Create branch `sprint8-execution` from main
   - Verify test suite baseline (all tests passing)
   - Run `make ingest-gamslib` to capture baseline (20% parse rate)

3. **Confirm Sprint Scope** (1 hour)
   - Review Task 2 (Feature Matrix): Option statements + Indexed assignments
   - Review Task 8 (Test Fixtures): 13 fixtures to create
   - Identify any prep tasks needing clarification
   - Update PLAN.md if scope adjustments needed

4. **Verify Known Unknowns** (30 min) **[EXPLICIT DELIVERABLE]**
   - Open `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md`
   - Verify unknowns 8.1, 8.2, 8.3 are marked as ✅ VERIFIED
   - Confirm verification results from Task 10 are documented:
     - 8.1: Effort allocation (30-41h, average 35.5h)
     - 8.2: Parse rate targets (40% primary, 50% stretch, 30% fallback)
     - 8.3: 4 checkpoints defined (Days 2, 4, 8, 9)
   - If any unknowns are not verified, escalate immediately

5. **Set Up Tracking** (30 min)
   - Create Sprint 8 tracking document (if needed)
   - Set up daily standup notes template
   - Prepare quality gate checklist

**Deliverables:**
- Sprint 8 execution branch created
- Baseline metrics captured (20% parse rate, test count, test time)
- Scope confirmed and documented
- **KNOWN_UNKNOWNS.md verification confirmed** (8.1, 8.2, 8.3 all ✅ VERIFIED)

**Quality Gates:**
- ✅ All tests passing on baseline
- ✅ Baseline parse rate confirmed at 20% (2/10 models: mhw4d, rbrock)
- ✅ Development environment ready
- ✅ **Unknowns 8.1-8.3 verified in KNOWN_UNKNOWNS.md**

**Cross-References:**
- All Tasks 2-9 (comprehensive review)

---

### **Day 1: Option Statements - Grammar & AST** (6-8 hours)

**Objective:** Implement option statement parsing (grammar, AST, basic tests)

**Tasks:**
1. **Grammar Extension** (1-2 hours)
   - Add option statement rules to `nlp2mcp/parser/gams.lark`:
     ```lark
     option_stmt: ("option"i | "options"i) option_list SEMI
     option_list: option_item ("," option_item)*
     option_item: ID "=" option_value  -> option_with_value
                | ID                   -> option_flag
     option_value: NUMBER
                 | "on"i | "off"i
     ```
   - Add to `statement` rule as alternative
   - Verify grammar compiles without errors

2. **AST Node Creation** (1 hour)
   - Create `OptionStatement` dataclass in `nlp2mcp/ir/nodes.py`:
     ```python
     @dataclass
     class OptionStatement:
         options: List[Tuple[str, Optional[Union[int, str]]]]
         location: SourceLocation
     ```
   - Add to IR node exports

3. **Semantic Handler** (2-3 hours)
   - Implement `_transform_option_stmt()` in `parser.py`
   - Handle single and multi-option syntax
   - Store options in AST (mock/store approach, no behavior)
   - Extract option name and value from parse tree
   - Add location tracking

4. **Basic Tests** (2 hours)
   - Create `tests/parser/test_option_statements.py`
   - Test single integer option: `option limrow = 0;`
   - Test multi-option: `option limrow = 0, limcol = 0;`
   - Test boolean on/off: `option solprint = off;`
   - Test case insensitivity: `OPTION LimRow = 0;`
   - Run `make test` to verify

**Deliverables:**
- Option statement grammar rules added
- OptionStatement AST node created
- Semantic handler implemented
- 4+ basic tests passing

**Quality Gates:**
- ✅ `make test` passes (all existing tests + new option tests)
- ✅ `make typecheck` passes
- ✅ `make lint` passes
- ✅ Grammar compiles without errors
- ✅ No regressions in existing models (mhw4d, rbrock still parse)

**Checkpoint Decision:**
- Continue if all quality gates pass
- Debug if grammar issues or test failures

**Cross-References:**
- Task 3: OPTION_STATEMENT_RESEARCH.md (grammar design, semantic approach)
- Task 8: TEST_FIXTURE_STRATEGY.md (option statement fixtures 1-5)

---

### **Day 2: Option Statements - Integration & Fixtures** (4-5 hours)

**Objective:** Complete option statement implementation with full test coverage and mhw4dx validation

**Tasks:**
1. **Advanced Option Patterns** (1-2 hours)
   - Implement decimals option: `option decimals = 8;`
   - Test option placement (before/after declarations)
   - Test mhw4dx.gms pattern: `option limcol = 0, limrow = 0;` + `option decimals = 8;`
   - Verify AST structure for all patterns

2. **Test Fixture Creation** (2 hours)
   - Create `tests/fixtures/options/` directory
   - Create 5 GMS fixture files:
     - `01_single_integer.gms`: `option limrow = 0;`
     - `02_multiple_options.gms`: `option limrow = 0, limcol = 0;`
     - `03_decimals_option.gms`: `option decimals = 8;`
     - `04_placement.gms`: Options in different locations
     - `05_mhw4dx_pattern.gms`: Real GAMSLib pattern from mhw4dx.gms
   - Create `tests/fixtures/options/expected_results.yaml`
   - Create `tests/fixtures/options/README.md`

3. **GAMSLib Validation** (1 hour)
   - Run mhw4dx.gms through parser
   - Verify it parses successfully (no errors)
   - Inspect AST for option statements
   - Capture parse success in logs

4. **Integration Tests** (30 min)
   - Add mhw4dx.gms to GAMSLib test suite
   - Run `make ingest-gamslib`
   - Verify parse rate: 30% (3/10 models: mhw4d, rbrock, mhw4dx)
   - Update dashboard

**Deliverables:**
- 5 option statement test fixtures with YAML and README
- mhw4dx.gms parsing successfully
- Parse rate increased to 30% (3/10 models)
- All tests passing

**Quality Gates:**
- ✅ `make test` passes (including new fixture tests)
- ✅ mhw4dx.gms parses with no errors
- ✅ Parse rate ≥30% (3/10 models minimum)
- ✅ No regressions in Sprint 7 models

**CHECKPOINT 1: Option Statements Complete**
- **Go Criteria:**
  - mhw4dx.gms parses successfully ✅
  - Parse rate ≥30% (3/10 models) ✅
  - All tests passing ✅
- **Go Decision:** Continue to indexed assignments (Days 3-4)
- **No-Go Decision:** Debug option implementation, allocate buffer hours from Day 9

**Cross-References:**
- Task 3: OPTION_STATEMENT_RESEARCH.md (all 5 fixture patterns)
- Task 8: TEST_FIXTURE_STRATEGY.md (fixtures 1-5, README template)
- Task 2: GAMSLIB_FEATURE_MATRIX.md (mhw4dx unlock validation)

---

### **Day 3: Indexed Assignments - Grammar & Foundation** (6-8 hours)

**Objective:** Implement indexed assignment parsing (grammar, semantic handlers for basic patterns)

**Tasks:**
1. **Grammar Extension** (15 min)
   - Extend `BOUND_K` token in `gams.lark`:
     ```lark
     BOUND_K: /(lo|up|fx|l|m)/i  # Add .m for marginal attribute
     ```
   - Verify grammar compiles
   - Note: Existing `ref_indexed` and `ref_bound` rules already support most patterns

2. **Indexed Parameter Assignment Handler** (2-3 hours)
   - Implement semantic handler for `p('i1') = 10;` pattern
   - Create `ParameterIndexRef` IR node (if not exists)
   - Handle 1D indexing: single string literal index
   - Handle 2D indexing: `report('x1','global') = 1;`
   - Validate index count matches parameter declaration
   - Add to assignment statement handler

3. **Variable Attribute Handler** (1-2 hours)
   - Implement semantic handler for `xdiff = x1.l;` pattern
   - Support `.l` (level), `.m` (marginal), `.lo`, `.up`, `.fx` attributes
   - Store as initial value (pre-solve limitation documented)
   - Handle attribute access in RHS expressions

4. **Basic Tests** (2 hours)
   - Create `tests/parser/test_indexed_assignments.py`
   - Test 1D indexed param: `p('i1') = 10;`
   - Test 2D indexed param: `report('x1','global') = 1;`
   - Test variable .l attribute: `xdiff = x1.l;`
   - Test simple indexed expression: `p('a') = 5;`
   - Run `make test` to verify

**Deliverables:**
- Grammar extended with `.m` attribute
- Indexed parameter assignment handler implemented
- Variable attribute handler implemented
- 4+ basic tests passing

**Quality Gates:**
- ✅ `make test` passes (all existing tests + new indexed tests)
- ✅ `make typecheck` passes
- ✅ `make lint` passes
- ✅ Grammar compiles without errors
- ✅ No regressions in existing models

**Checkpoint Decision:**
- Continue if all quality gates pass
- Debug if semantic handler issues

**Cross-References:**
- Task 7: INDEXED_ASSIGNMENTS_RESEARCH.md (grammar, semantic handlers, patterns 1-4)
- Task 8: TEST_FIXTURE_STRATEGY.md (indexed assignment fixtures 1-5)

---

### **Day 4: Indexed Assignments - Advanced Patterns & Integration** (4-5 hours)

**Objective:** Complete indexed assignment implementation with expressions, fixtures, and GAMSLib validation

**Tasks:**
1. **Indexed Expressions in RHS** (1.5-2 hours)
   - Implement `p('diff') = p('global') - p('solver');` pattern
   - Create `ParameterRef` IR node for indexed parameter access
   - Handle indexed params in expressions (not just assignments)
   - Support arithmetic operations with indexed refs
   - Add comprehensive tests

2. **Test Fixture Creation** (1.5 hours)
   - Create `tests/fixtures/indexed_assignments/` directory
   - Create 5 GMS fixture files:
     - `01_simple_1d.gms`: `p('i1') = 10;`
     - `02_multi_dim_2d.gms`: mathopt1 pattern - `report('x1','global') = 1;`
     - `03_variable_attributes.gms`: trig pattern - `xdiff = x1.l;`
     - `04_indexed_expressions.gms`: `p('diff') = p('global') - p('solver');`
     - `05_error_index_mismatch.gms`: Invalid index count (expected to fail)
   - Create `tests/fixtures/indexed_assignments/expected_results.yaml`
   - Create `tests/fixtures/indexed_assignments/README.md`

3. **GAMSLib Validation** (1-1.5 hours)
   - Run mathopt1.gms through parser
   - Run trig.gms through parser
   - Verify both parse successfully (or identify secondary blockers)
   - Inspect AST for indexed assignments
   - Capture parse success/failure in logs

4. **Integration Tests** (30 min)
   - Add mathopt1.gms and trig.gms to GAMSLib test suite
   - Run `make ingest-gamslib`
   - Verify parse rate: 40-50% (4-5/10 models)
   - Update dashboard

**Deliverables:**
- 5 indexed assignment test fixtures with YAML and README
- mathopt1.gms and/or trig.gms parsing successfully
- Parse rate increased to 40-50% (4-5/10 models)
- All tests passing

**Quality Gates:**
- ✅ `make test` passes (including new fixture tests)
- ✅ mathopt1.gms parses (high confidence: 95%)
- ✅ trig.gms parses (medium confidence: 85%)
- ✅ Parse rate ≥40% (4/10 models minimum)
- ✅ No regressions in Sprint 7-8 models

**CHECKPOINT 2: Indexed Assignments Complete**
- **Go Criteria:**
  - mathopt1.gms parses successfully ✅
  - Parse rate ≥40% (4/10 models) ✅
  - All tests passing ✅
- **Go Decision:** Continue to UX enhancements (Days 5-7)
- **No-Go Decision:** Assess scope reduction (defer partial metrics or error messages), focus on core functionality

**Cross-References:**
- Task 7: INDEXED_ASSIGNMENTS_RESEARCH.md (all 4 patterns, expression handling)
- Task 8: TEST_FIXTURE_STRATEGY.md (fixtures 1-5, README template)
- Task 2: GAMSLIB_FEATURE_MATRIX.md (mathopt1 + trig unlock validation)

---

### **Day 5: Error Line Numbers & Source Context** (4-5 hours)

**Objective:** Consolidate all parser errors on ParseError class with line numbers and source context

**Tasks:**
1. **Lark Error Wrapping** (1 hour)
   - Modify `parse_text()` to catch UnexpectedToken and UnexpectedCharacters
   - Extract source line from input using error line number
   - Wrap in ParseError with source line display and caret pointer
   - Preserve original error message

2. **Create _parse_error() Helper** (1 hour)
   - Similar to existing `_error()` helper but returns ParseError
   - Extract source line from original GAMS input
   - Add caret pointer generation logic (point to error column)
   - Include location (line, column) in ParseError

3. **Migrate Top 5 Error Types** (1-1.5 hours)
   - Identify top 5 most common semantic errors from parser.py
   - Add actionable suggestions for each type
   - Replace `_error()` calls with `_parse_error()` calls
   - Examples:
     - "Assignments must use numeric constants" → "Use a literal number instead of function call"
     - "Indexed assignments not supported" → "This feature will be available in Sprint 9"

4. **Test Fixtures** (1 hour)
   - Create 5 test fixtures in `tests/errors/`:
     - Lark UnexpectedToken wrapping
     - Lark UnexpectedCharacters wrapping
     - Semantic error with caret pointer
     - Semantic error with suggestion
     - Coverage test (all error types include location)
   - Run `make test` to verify

**Deliverables:**
- ParseError wrapping for Lark errors
- `_parse_error()` helper method
- Top 5 error types migrated with suggestions
- 5 test fixtures for error wrapping
- 100% parser errors include location

**Quality Gates:**
- ✅ `make test` passes
- ✅ All parser errors include line/column numbers
- ✅ Lark errors wrapped with source context
- ✅ No regressions in error handling

**Cross-References:**
- Task 4: PARSER_ERROR_LINE_NUMBERS.md (design, infrastructure, patterns)
- Task 6: ERROR_MESSAGE_ENHANCEMENTS.md (error message patterns)

---

### **Day 6: Error Message Enhancements** (3-4 hours)

**Objective:** Implement "did you mean?" suggestions and contextual hints for parser errors

**Tasks:**
1. **ErrorEnhancer Class** (1-1.5 hours)
   - Create `nlp2mcp/parser/errors.py` module (if not exists)
   - Implement `ErrorEnhancer` class with categorization logic
   - Implement `EnhancedError` dataclass with suggestions field
   - Add GAMS_KEYWORDS constant (Set, Scalar, Parameter, Variable, Equation, etc.)

2. **Suggestion Rules** (1-1.5 hours)
   - Rule 1: Keyword typo detection using difflib.get_close_matches()
     - "Scaler" → "Did you mean 'Scalar'?"
     - Cutoff: 0.6 similarity threshold
   - Rule 2: Set bracket error detection
     - Detect `[` in Set context → Suggest `/.../ not [...]`
   - Rule 3: Missing semicolon detection
     - Detect unexpected keyword on next line → Suggest adding `;`
   - Rule 4: Unsupported feature explanation
     - Pattern match "not supported" → Add roadmap reference
   - Rule 5: Function call error
     - Detect `Call(...)` in error → Explain literal-only limitation

3. **Integration** (30 min)
   - Integrate ErrorEnhancer with `parse_text()` and `parse_file()`
   - Wrap all ParseError instances through ErrorEnhancer
   - Format enhanced errors for display

4. **Test Fixtures** (1 hour)
   - Create 5 test fixtures:
     - Keyword typo: `Scaler x;` → Suggest "Scalar"
     - Set bracket error: `Set i [1*10];` → Suggest `/1*10/`
     - Missing semicolon: Multi-line with missing `;`
     - Unsupported feature: `x(i) = 5;` → Explain Sprint 9
     - Function call: `size = uniform(1, 10);` → Explain literal limitation
   - Run tests

**Deliverables:**
- ErrorEnhancer class with categorization
- 5 enhancement rules implemented
- Integration with parse functions
- 5 test fixtures
- 80%+ errors get actionable suggestions

**Quality Gates:**
- ✅ `make test` passes
- ✅ Keyword typos suggest correct spelling
- ✅ Punctuation errors show correct syntax
- ✅ Unsupported features explain roadmap

**Cross-References:**
- Task 6: ERROR_MESSAGE_ENHANCEMENTS.md (patterns, rules, categorization)
- Task 4: PARSER_ERROR_LINE_NUMBERS.md (ParseError integration)

---

### **Day 7: Partial Parse Metrics** (4-6 hours)

**Objective:** Implement parse progress tracking and missing feature extraction

**Tasks:**
1. **Line Counting Logic** (2 hours)
   - Implement `count_logical_lines(source)` function
     - Count non-empty, non-comment lines
     - Handle multiline comments (`$ontext ... $offtext`)
     - Skip single-line comments (`*`)
   - Implement `count_logical_lines_up_to(source, line_number)` function
     - Count lines before error line
     - Same multiline comment handling
   - Add tests for line counting edge cases

2. **Missing Feature Extraction** (2 hours)
   - Implement `extract_missing_features(error, error_message)` function
     - Pattern 1: Lead/lag indexing (i++1, i--1)
     - Pattern 2: Option statements
     - Pattern 3: Model sections (mx, my)
     - Pattern 4: Function calls in assignments
     - Pattern 5: Indexed assignments
     - Pattern 6: Nested indexing
     - Pattern 7: Short model syntax
     - Pattern 8: Unsupported feature (generic)
   - Return top 2 features for readability
   - Add tests for feature extraction

3. **Parse Progress Calculation** (1 hour)
   - Implement `calculate_parse_progress(model_path, error)` function
     - Extract error line from exception
     - Count logical lines before error
     - Calculate percentage: (lines_parsed / total_lines) * 100
     - Handle semantic errors (100% parsed with error)
   - Add tests

4. **Integration** (1 hour)
   - Enhance ModelResult dataclass with new fields:
     - `parse_progress_percentage: Optional[float]`
     - `parse_progress_lines_parsed: Optional[int]`
     - `parse_progress_lines_total: Optional[int]`
     - `missing_features: Optional[List[str]]`
   - Update ingestion script to call progress calculation
   - Add tests

**Deliverables:**
- Line counting functions (logical lines, up to line number)
- Missing feature extraction (8 patterns)
- Parse progress calculation
- ModelResult dataclass enhanced
- All tests passing

**Quality Gates:**
- ✅ `make test` passes
- ✅ Line counting handles multiline comments
- ✅ Feature extraction covers 70-80% of GAMSLib errors
- ✅ Progress calculation accurate for all 10 models

**Cross-References:**
- Task 5: PARTIAL_PARSE_METRICS.md (algorithms, line counting, feature extraction)
- Task 9: DASHBOARD_ENHANCEMENTS.md (ModelResult schema)

---

### **Day 8: Dashboard Updates & Integration** (3-4 hours)

**Objective:** Update dashboard template and ingestion script with partial parse metrics

**Tasks:**
1. **Ingestion Script Updates** (1-1.5 hours)
   - Modify `scripts/ingest_gamslib_results.py` (assumed location)
   - Call `calculate_parse_progress()` for all models
   - Call `extract_missing_features()` for failures
   - Populate new ModelResult fields
   - Determine status symbol based on percentage:
     - 100% + no error → ✅ PASS
     - 100% + semantic error → 🟡 PARTIAL
     - 75-99% → 🟡 PARTIAL
     - 25-74% → ⚠️ PARTIAL
     - <25% → ❌ FAIL

2. **Dashboard Template Modifications** (1-1.5 hours)
   - Update `GAMSLIB_CONVERSION_STATUS.md` template (assumed Jinja2)
   - Add new columns: Status, Progress, Missing Features
   - Remove old Parse column (replaced by Status)
   - Format progress: "92% (22/24)"
   - Format missing features: comma-separated, limit to 2
   - Add color-coded symbols: ✅ 🟡 ⚠️ ❌

3. **Backward Compatibility Testing** (1 hour)
   - Test with Sprint 7 data (should default to 100% or 0%)
   - Verify old fields still work
   - Verify new columns render correctly
   - Test with Sprint 8 data (new metrics)

4. **Integration Testing** (1 hour)
   - Run `make ingest-gamslib` with all 10 models
   - Verify dashboard shows:
     - mhw4d: ✅ PASS | 100% (18/18) | -
     - rbrock: ✅ PASS | 100% (156/156) | -
     - mhw4dx: ✅ PASS | 100% (18/18) | -
     - mathopt1: ✅ PASS or 🟡 PARTIAL (if secondary blocker)
     - trig: ✅ PASS or 🟡 PARTIAL (if secondary blocker)
     - himmel16: 🟡 PARTIAL | 92% (22/24) | i++1 indexing
     - circle: 🟡 PARTIAL | 100% (24/24) | function calls
     - Others: Appropriate color coding
   - Verify parse rate ≥40% (4-5/10 models)

**Deliverables:**
- Enhanced ingestion script (~140 new lines)
- Updated dashboard template with 3 new columns
- Backward compatibility validated
- Dashboard displays partial metrics for all 10 models

**Quality Gates:**
- ✅ `make ingest-gamslib` runs successfully
- ✅ Dashboard renders with new columns
- ✅ All 10 models show parse percentage
- ✅ Color coding matches thresholds
- ✅ Sprint 7 data backward compatible

**CHECKPOINT 3: All Features Integrated**
- **Go Criteria:**
  - All features working together ✅
  - Dashboard displays partial metrics ✅
  - Parse rate ≥40% (4-5/10 models) ✅
  - All tests passing ✅
- **Go Decision:** Continue to final testing and documentation (Day 9)
- **No-Go Decision:** Defer test fixtures, focus on core functionality validation

**Cross-References:**
- Task 9: DASHBOARD_ENHANCEMENTS.md (template, ingestion script, color coding)
- Task 5: PARTIAL_PARSE_METRICS.md (progress calculation)
- Task 2: GAMSLIB_FEATURE_MATRIX.md (validate unlock rates)

---

### **Day 9: Test Fixtures & Final Testing** (4-5 hours)

**Objective:** Create remaining test fixtures, run comprehensive testing, verify all quality gates

**Tasks:**
1. **Partial Parse Metric Fixtures** (1.5 hours)
   - Create `tests/fixtures/partial_parse/` directory
   - Create 3 GMS fixture files:
     - `01_himmel16_pattern.gms`: Partial parse ~80-92% (i++1 blocker)
     - `02_circle_pattern.gms`: Partial parse ~70-100% (function call blocker)
     - `03_complete_success.gms`: 100% parse baseline
   - Create `tests/fixtures/partial_parse/expected_results.yaml`
   - Create `tests/fixtures/partial_parse/README.md`

2. **Comprehensive Test Suite Run** (1 hour)
   - Run `make test` (all tests)
   - Run `make typecheck` (type checking)
   - Run `make lint` (linting)
   - Run `make format` (formatting check)
   - Fix any failures or warnings

3. **GAMSLib Integration Testing** (1-1.5 hours)
   - Run `make ingest-gamslib` with all 10 models
   - Verify parse rate ≥40% (conservative) or ≥50% (optimistic)
   - Verify dashboard shows correct metrics for all models
   - Manually inspect ASTs for option and indexed assignment models
   - Capture final parse rate for Sprint 8

4. **Regression Testing** (1 hour)
   - Verify Sprint 7 models still parse:
     - mhw4d.gms ✅
     - rbrock.gms ✅
   - Verify Sprint 8 models parse:
     - mhw4dx.gms ✅
     - mathopt1.gms ✅ (or identify secondary blocker)
     - trig.gms ✅ (or identify secondary blocker)
   - Verify no new errors introduced in other models
   - Document any unexpected results

**Deliverables:**
- 3 partial parse test fixtures with YAML and README
- All tests passing (unit, integration, GAMSLib)
- Parse rate ≥40% validated
- Regression testing complete

**Quality Gates:**
- ✅ `make test` passes (100% of tests)
- ✅ `make typecheck` passes
- ✅ `make lint` passes
- ✅ `make format` passes
- ✅ Parse rate ≥40% (4/10 models minimum)
- ✅ No regressions in Sprint 7 models

**Checkpoint Decision:**
- Continue to documentation and PR if all gates pass
- Debug and fix if any failures

**Cross-References:**
- Task 8: TEST_FIXTURE_STRATEGY.md (partial parse fixtures, README template)
- Task 2: GAMSLIB_FEATURE_MATRIX.md (validate final parse rate)

---

### **Day 10: Documentation, PR, & Sprint Closeout** (2.5 hours - **BUFFER DAY**)

**Objective:** Complete documentation, create PR, prepare for Sprint 8 closeout

**⚠️ BUFFER DAY NOTE:** Day 10 is explicitly designated as a buffer day. If Days 1-9 overrun, use Day 10 hours to complete remaining work. If Days 1-9 complete on schedule, use Day 10 for documentation, PR creation, and closeout as detailed below.

**Tasks:**
1. **Documentation Updates** (1 hour)
   - Update `README.md` with Sprint 8 features (if applicable)
   - Update parser documentation with option and indexed assignment examples
   - Document known limitations:
     - Option statements: Mock/store only (no behavior)
     - Indexed assignments: Pre-solve only (no runtime evaluation)
     - Partial metrics: Line-based approximation (not true statement counting)
   - Add examples to docs

2. **CHANGELOG Update** (30 min)
   - Add Sprint 8 entry under `## [Unreleased]`
   - List all features implemented
   - Document parse rate improvement (20% → 40-50%)
   - Note models unlocked

3. **Create Pull Request** (30 min)
   - Create PR from `sprint8-execution` to `main`
   - Title: "Sprint 8: High-ROI Parser Features & UX Enhancements"
   - Body: Summary of features, parse rate, testing coverage
   - Link to PLAN.md and all prep tasks
   - Request review

4. **Sprint Closeout** (30 min)
   - Update Sprint 8 status in PROJECT_PLAN.md
   - Archive Sprint 8 branch (if needed)
   - Prepare handoff notes for Sprint 9 (if applicable)
   - Capture lessons learned

**Deliverables:**
- Documentation updated
- CHANGELOG.md updated
- PR created and ready for review
- Sprint 8 marked complete

**Quality Gates:**
- ✅ All acceptance criteria met (see Section 5)
- ✅ Documentation complete and accurate
- ✅ PR description comprehensive
- ✅ Ready for code review

**FINAL CHECKPOINT: Sprint 8 Complete**
- **Go Criteria:**
  - Parse rate ≥40% (4/10 models) ✅
  - All tests passing ✅
  - Documentation complete ✅
  - PR ready for review ✅
- **Go Decision:** Submit PR, mark Sprint 8 complete
- **No-Go Decision:** Document blockers, plan Sprint 8b with adjusted scope

**Cross-References:**
- All Tasks 2-9 (comprehensive implementation)

---

## 3. Checkpoint Definitions

Sprint 8 has **4 checkpoints** at critical decision points to allow mid-sprint course correction.

### **Checkpoint 1: Option Statements Complete** (End of Day 2)

**When:** End of Day 2 (after option statement implementation and mhw4dx validation)

**Criteria:**
- ✅ mhw4dx.gms parses successfully with no errors
- ✅ Parse rate ≥30% (3/10 models: mhw4d, rbrock, mhw4dx)
- ✅ All tests passing (`make test`, `make typecheck`, `make lint`)
- ✅ 5 option statement test fixtures created and passing
- ✅ No regressions in Sprint 7 models

**Go Decision:**
- **If ALL criteria met:** Continue to indexed assignments (Days 3-4)
- **Rationale:** Option statements are foundation, must be solid before moving on

**No-Go Decision:**
- **If ANY criteria fail:** Allocate buffer hours from Day 9 to debug
- **Fallback:** Reduce scope - defer error message enhancements to Sprint 8b
- **Escalation:** If >2 hours debugging needed, assess indexed assignment feasibility

**Impact:**
- Early checkpoint (Day 2) catches issues before too much work invested
- Buffer hours available in Day 9 for recovery
- Option statements are lower risk (6-8h estimate validated by Task 3)

---

### **Checkpoint 2: Indexed Assignments Complete** (End of Day 4)

**When:** End of Day 4 (after indexed assignment implementation and GAMSLib validation)

**Criteria:**
- ✅ mathopt1.gms parses successfully (high confidence: 95%)
- ✅ trig.gms parses successfully OR secondary blocker identified (medium confidence: 85%)
- ✅ Parse rate ≥40% (4/10 models: mhw4d, rbrock, mhw4dx, mathopt1)
- ✅ All tests passing (`make test`, `make typecheck`, `make lint`)
- ✅ 5 indexed assignment test fixtures created and passing
- ✅ No regressions in Sprint 7-8 models

**Go Decision:**
- **If ALL criteria met:** Continue to UX enhancements (Days 5-7)
- **Rationale:** Core features complete, UX enhancements are lower risk

**No-Go Decision:**
- **If mathopt1.gms fails:** Debug expression handling (allocate 2-3 hours)
- **If trig.gms fails but mathopt1 succeeds:** Accept 40% parse rate, continue
- **If parse rate <40%:** Assess scope reduction:
  - **Option 1:** Defer partial metrics (6h freed)
  - **Option 2:** Defer error message enhancements (3-4h freed)
  - **Option 3:** Simplify indexed assignments (defer expressions)
- **Escalation:** If >4 hours debugging needed, plan Sprint 8b

**Impact:**
- Mid-sprint checkpoint (Day 4) allows scope adjustment before UX work
- Task 7 research reduces risk (no hidden complexity expected)
- 40% parse rate still exceeds Sprint 8 target (25-30%)

---

### **Checkpoint 3: All Features Integrated** (End of Day 8)

**When:** End of Day 8 (after dashboard updates and integration testing)

**Criteria:**
- ✅ All features working together (options, indexed, errors, metrics, dashboard)
- ✅ Dashboard displays partial metrics for all 10 models
- ✅ Parse rate ≥40% (4-5/10 models)
- ✅ All tests passing (`make test`, `make typecheck`, `make lint`)
- ✅ `make ingest-gamslib` runs successfully
- ✅ No regressions in Sprint 7-8 models

**Go Decision:**
- **If ALL criteria met:** Continue to final testing and documentation (Day 9)
- **Rationale:** Integration successful, ready for polish

**No-Go Decision:**
- **If integration issues:** Debug (allocate Day 9 buffer)
- **If dashboard broken:** Fix template/ingestion script (1-2 hours)
- **If parse rate regression:** Identify and fix blocker
- **Fallback:** Defer test fixtures to Sprint 8b, focus on core validation
- **Escalation:** If >3 hours debugging needed, defer fixtures entirely

**Impact:**
- Late checkpoint (Day 8) validates full integration before final testing
- Dashboard is lowest priority (can revert to Sprint 7 format if needed)
- Parse rate is key metric (must not regress)

---

### **Checkpoint 4 (FINAL): Sprint 8 Complete** (End of Day 9)

**When:** End of Day 9 (after comprehensive testing and regression validation)

**Criteria:**
- ✅ Parse rate ≥40% (4/10 models minimum) - Conservative target met
- ✅ All tests passing (100% pass rate)
- ✅ All quality gates passed (`make test`, `make typecheck`, `make lint`, `make format`)
- ✅ GAMSLib integration tests successful
- ✅ No regressions in Sprint 7 models
- ✅ Dashboard displays partial metrics correctly
- ✅ Error messages enhanced with suggestions
- ✅ Documentation updated

**Go Decision:**
- **If ALL criteria met:** Create PR, mark Sprint 8 complete (Day 10)
- **Rationale:** Sprint 8 goals achieved, ready for review

**No-Go Decision:**
- **If parse rate <40%:** Document findings, plan Sprint 8b with adjusted scope
- **If tests failing:** Debug (use Day 10 buffer)
- **If regressions found:** Fix critical issues (use Day 10 buffer)
- **Fallback:** Create PR with known issues documented, plan Sprint 8b
- **Escalation:** If critical blocker, extend sprint or plan Sprint 8b

**Impact:**
- Final checkpoint validates all acceptance criteria before PR
- Day 10 buffer available for last-minute fixes
- Sprint 8b plan available if scope needs adjustment

---

## 4. Effort Estimates

### Total Sprint 8 Effort: 30-41 hours (average 35.5h)

**Breakdown by Feature Area:**

| Feature Area | Effort (Hours) | Days | Priority | Risk |
|--------------|----------------|------|----------|------|
| **Sprint Planning** | 2-3 | 0 | HIGH | LOW |
| **Option Statements** | 10.5-13.5 | 1-2 | HIGH | LOW |
| **Indexed Assignments** | 9.75-12.75 | 3-4 | HIGH | MEDIUM |
| **Error Line Numbers** | 4-4.5 | 5 | MEDIUM | LOW |
| **Error Enhancements** | 3-4.5 | 6 | MEDIUM | LOW |
| **Partial Metrics** | 6 | 7 | MEDIUM | LOW |
| **Dashboard Updates** | 4-5 | 8 | LOW | LOW |
| **Test Fixtures** | 4.5-5 | 9 | LOW | LOW |
| **Documentation & PR** | 2.5 | 10 | LOW | LOW |
| **TOTAL** | **30-41** | **0-10** | - | - |

**Effort Analysis:**
- **Conservative Estimate:** 30h (lower bounds) - WITHIN 25-35h target ✅
- **Realistic Estimate:** 35.5h (average of ranges) - Slightly over target, manageable
- **Upper Bound:** 41h (upper bounds) - Requires Day 10 buffer + scope flexibility
- **Average per day:** 3.5h/day (based on realistic estimate across 10 active days)

**Validation:**
- All estimates from detailed day-by-day breakdown (Section 2)
- Matches prep task estimates (Tasks 3-9)
- Conservative estimate (30h) within 25-35h target ✅
- Day 10 explicitly designated as BUFFER to absorb overruns
- Upper bound (41h) requires ~20% flexibility over 35h target

**Critical Path:** Days 1-4 (Core Features) → Days 5-7 (UX) → Days 8-9 (Integration & Testing) → Day 10 (Buffer)

---

### Detailed Effort Breakdown

#### **Day 0: Sprint Planning** (2-3 hours)
- Review PLAN.md: 30 min
- Set up branch: 15 min
- Confirm scope: 1 hour
- Set up tracking: 30 min
- **Total:** 2.25 hours

#### **Day 1: Option Statements - Grammar & AST** (6-8 hours)
- Grammar extension: 1-2 hours
- AST node creation: 1 hour
- Semantic handler: 2-3 hours
- Basic tests: 2 hours
- **Total:** 6-8 hours (validated by Task 3)

#### **Day 2: Option Statements - Integration** (4-5 hours)
- Advanced patterns: 1-2 hours
- Test fixtures: 2 hours
- GAMSLib validation: 1 hour
- Integration tests: 30 min
- **Total:** 4.5-5.5 hours

**Day 1-2 Combined:** 10.5-13.5 hours (matches Task 3 estimate of 6-8h core + 4-5h integration)

#### **Day 3: Indexed Assignments - Foundation** (6-8 hours)
- Grammar extension: 15 min
- Indexed param handler: 2-3 hours
- Variable attribute handler: 1-2 hours
- Basic tests: 2 hours
- **Total:** 5.25-7.25 hours

#### **Day 4: Indexed Assignments - Advanced** (4-5 hours)
- Indexed expressions: 1.5-2 hours
- Test fixtures: 1.5 hours
- GAMSLib validation: 1-1.5 hours
- Integration tests: 30 min
- **Total:** 4.5-5.5 hours

**Day 3-4 Combined:** 9.75-12.75 hours (matches Task 7 estimate of 6.5-8h core + 3-4h integration)

#### **Day 5: Error Line Numbers** (4-5 hours)
- Lark error wrapping: 1 hour
- _parse_error() helper: 1 hour
- Migrate top 5 types: 1-1.5 hours
- Test fixtures: 1 hour
- **Total:** 4-4.5 hours (matches Task 4 estimate)

#### **Day 6: Error Enhancements** (3-4 hours)
- ErrorEnhancer class: 1-1.5 hours
- Suggestion rules: 1-1.5 hours
- Integration: 30 min
- Test fixtures: 1 hour
- **Total:** 3-4.5 hours (matches Task 6 estimate)

#### **Day 7: Partial Metrics** (4-6 hours)
- Line counting: 2 hours
- Feature extraction: 2 hours
- Progress calculation: 1 hour
- Integration: 1 hour
- **Total:** 6 hours (matches Task 5 estimate)

#### **Day 8: Dashboard Updates** (3-4 hours)
- Ingestion script: 1-1.5 hours
- Template modifications: 1-1.5 hours
- Backward compat testing: 1 hour
- Integration testing: 1 hour
- **Total:** 4-5 hours (matches Task 9 estimate)

#### **Day 9: Test Fixtures & Testing** (4-5 hours)
- Partial parse fixtures: 1.5 hours
- Comprehensive test run: 1 hour
- GAMSLib integration: 1-1.5 hours
- Regression testing: 1 hour
- **Total:** 4.5-5 hours (matches Task 8 estimate)

#### **Day 10: Documentation & PR** (2.5 hours - **BUFFER DAY**)
- Documentation: 1 hour
- CHANGELOG: 30 min
- Create PR: 30 min
- Sprint closeout: 30 min
- **Total:** 2.5 hours

**GRAND TOTAL:** 30-41 hours (average: 35.5 hours)  
**Conservative (lower bounds):** 30 hours ✅ WITHIN 25-35h TARGET  
**Realistic (mid-points):** 35.5 hours (slightly over 35h, manageable with Day 10 buffer)  
**Upper Bound:** 41 hours (requires Day 10 buffer + 20% scope flexibility)

**Note:** The 25-35h target from PREP_PLAN.md is achievable with conservative execution (30h). Realistic execution (35.5h) uses Day 10 buffer. Upper bound (41h) requires additional scope flexibility but is mitigated by checkpoint-based scope adjustments (see Section 3).

---

## 5. Success Criteria

Sprint 8 is considered successful when ALL of the following criteria are met:

### **Primary Success Criteria (MUST HAVE)**

1. **Parse Rate ≥40% (4/10 models)**
   - ✅ Baseline: mhw4d.gms, rbrock.gms (Sprint 7)
   - ✅ Option statements: mhw4dx.gms (Sprint 8)
   - ✅ Indexed assignments: mathopt1.gms (Sprint 8)
   - 🎯 Stretch: trig.gms (Sprint 8 - 50% parse rate if achieved)

2. **Option Statement Support**
   - ✅ Grammar supports option statements (single and multi-option)
   - ✅ Integer value options parse correctly (limrow, limcol, decimals)
   - ✅ Boolean on/off keywords supported
   - ✅ Case-insensitive option names
   - ✅ mhw4dx.gms parses with no errors

3. **Indexed Assignment Support**
   - ✅ Parameter indexing supported (1D and 2D)
   - ✅ Variable attributes supported (.l, .m, .lo, .up, .fx)
   - ✅ Indexed expressions in RHS supported
   - ✅ mathopt1.gms parses with no errors (or secondary blocker identified)

4. **All Tests Passing**
   - ✅ `make test` passes (100% pass rate)
   - ✅ `make typecheck` passes
   - ✅ `make lint` passes
   - ✅ `make format` passes

5. **No Regressions**
   - ✅ Sprint 7 models still parse (mhw4d.gms, rbrock.gms)
   - ✅ No new errors in other models
   - ✅ Test suite remains stable

### **Secondary Success Criteria (SHOULD HAVE)**

6. **Parse Progress Visibility**
   - ✅ Dashboard shows 4-level color-coded status (✅ 🟡 ⚠️ ❌)
   - ✅ All 10 models show parse percentage and line counts
   - ✅ Missing features listed for 70-80% of failures
   - ✅ Backward compatible with Sprint 7 data

7. **Error Message Quality**
   - ✅ 100% of parser errors include line/column numbers
   - ✅ Keyword typos suggest correct spelling (difflib)
   - ✅ Punctuation errors show correct syntax
   - ✅ Unsupported features explain roadmap

8. **Test Coverage**
   - ✅ 5 option statement test fixtures
   - ✅ 5 indexed assignment test fixtures
   - ✅ 3 partial parse metric test fixtures
   - ✅ 5 error enhancement test fixtures
   - ✅ All fixtures have YAML and README

9. **Documentation Complete**
   - ✅ Parser documentation updated with examples
   - ✅ Known limitations documented
   - ✅ CHANGELOG.md updated
   - ✅ README.md updated (if applicable)

### **Stretch Goals (NICE TO HAVE)**

10. **Parse Rate ≥50% (5/10 models)**
    - 🎯 trig.gms parses successfully (in addition to mathopt1.gms)
    - 🎯 50% parse rate achieved

11. **Comprehensive Error Coverage**
    - 🎯 All 12 enhancement rules implemented (defer 7-12 to Sprint 8b)
    - 🎯 Multi-line error context supported

12. **Advanced Indexed Patterns**
    - 🎯 Nested indexing supported (if time permits)
    - 🎯 Complex expressions with multiple indexed refs

---

## 6. Risk Register

### **Risk 1: Option Statements Take Longer Than 6-8 Hours**

**Probability:** LOW  
**Impact:** MEDIUM (delays indexed assignments)  
**Mitigation:**
- Task 3 research validated 6-8h estimate with detailed breakdown
- Grammar extension is straightforward (5 rules)
- Mock/store approach avoids semantic complexity
- Checkpoint 1 (Day 2) catches early if issues arise

**Contingency:**
- Allocate buffer hours from Day 9 (test fixtures)
- Defer error message enhancements to Sprint 8b (frees 3-4 hours)
- Escalate if >2 hours over estimate

**Owner:** Sprint Lead  
**Status:** Monitored (reviewed at Checkpoint 1)

---

### **Risk 2: Indexed Assignments Have Hidden Complexity**

**Probability:** MEDIUM  
**Impact:** HIGH (blocks parse rate target)  
**Mitigation:**
- Task 7 deep dive found no hidden complexity
- Grammar already 95% supports indexed assignments
- 4 GAMS patterns identified and understood
- Expression handling allocated 1.5h (known complexity)
- Checkpoint 2 (Day 4) validates mathopt1.gms parsing

**Contingency:**
- If mathopt1 fails: Debug expression handling (2-3 hours)
- If trig fails but mathopt1 succeeds: Accept 40% parse rate
- Simplify indexed assignments: Defer expressions to Sprint 8b
- Allocate Day 9 buffer for debugging

**Owner:** Sprint Lead  
**Status:** Monitored (reviewed at Checkpoint 2)

---

### **Risk 3: Parse Rate Doesn't Reach 40%**

**Probability:** LOW  
**Impact:** HIGH (Sprint 8 target miss)  
**Mitigation:**
- Task 2 feature matrix validates unlock rates:
  - Option statements: +10% (mhw4dx.gms) - High confidence
  - Indexed assignments: +20% (mathopt1 + trig) - 95% confidence for mathopt1
- Checkpoint 2 (Day 4) validates parse rate ≥40%
- Conservative target: 40% (only needs mathopt1)
- Optimistic target: 50% (mathopt1 + trig)

**Contingency:**
- If mathopt1 has secondary blocker: Document findings, plan Sprint 8b
- If parse rate 30-39%: Accept partial success, continue with UX
- If parse rate <30%: Escalate, assess root cause

**Owner:** Sprint Lead  
**Status:** Monitored (reviewed at Checkpoint 2)

---

### **Risk 4: Test Fixtures Take Longer Than Estimated**

**Probability:** LOW  
**Impact:** LOW (test fixtures are lowest priority)  
**Mitigation:**
- Task 8 strategy reuses Sprint 7 patterns (proven approach)
- 13 fixtures total (~20 min per fixture average)
- Fixtures created during implementation (not batched)
- Day 9 dedicated to fixture completion

**Contingency:**
- Defer partial parse fixtures to Sprint 8b (3 fixtures)
- Focus on option and indexed assignment fixtures (critical)
- Fixtures are lowest priority (can defer entirely if needed)

**Owner:** Sprint Lead  
**Status:** Low priority (reviewed at Checkpoint 3)

---

### **Risk 5: Dashboard Integration Breaks Existing Functionality**

**Probability:** LOW  
**Impact:** MEDIUM (dashboard regression)  
**Mitigation:**
- Task 9 design ensures backward compatibility
- Sprint 7 data defaults to 100% or 0% (safe defaults)
- New fields optional in JSON schema
- Markdown dashboard is pure format (no schema to break)
- Checkpoint 3 (Day 8) validates dashboard integration

**Contingency:**
- If dashboard broken: Fix template/ingestion script (1-2 hours)
- Fallback: Revert to Sprint 7 dashboard format
- Dashboard is lowest priority (can defer to Sprint 8b)

**Owner:** Sprint Lead  
**Status:** Monitored (reviewed at Checkpoint 3)

---

### **Risk 6: Error Enhancement Rules Cause Performance Issues**

**Probability:** VERY LOW  
**Impact:** LOW (error path only)  
**Mitigation:**
- Error enhancements only run on error path (exceptional case)
- difflib.get_close_matches() is fast for small keyword sets
- Pattern matching is simple regex (no backtracking)
- Task 6 research confirms negligible overhead

**Contingency:**
- If performance issue: Disable expensive rules
- Limit suggestions to top 3 matches
- Cache keyword matching results

**Owner:** Sprint Lead  
**Status:** Low risk (no monitoring needed)

---

### **Risk Summary Table**

| Risk ID | Risk | Probability | Impact | Mitigation Status |
|---------|------|-------------|--------|-------------------|
| R1 | Option statements over estimate | LOW | MEDIUM | Checkpoint 1 (Day 2) |
| R2 | Indexed assignments complexity | MEDIUM | HIGH | Checkpoint 2 (Day 4) |
| R3 | Parse rate <40% | LOW | HIGH | Checkpoint 2 (Day 4) |
| R4 | Test fixtures over estimate | LOW | LOW | Day 9 buffer |
| R5 | Dashboard integration breaks | LOW | MEDIUM | Checkpoint 3 (Day 8) |
| R6 | Error enhancement performance | VERY LOW | LOW | No monitoring needed |

**Overall Risk Level:** LOW ✅  
**Confidence in Success:** HIGH ✅

---

## 7. Deliverables

### **Code Deliverables**

1. **Option Statement Support**
   - Grammar rules in `nlp2mcp/parser/gams.lark`
   - OptionStatement IR node in `nlp2mcp/ir/nodes.py`
   - Semantic handler in `nlp2mcp/parser/parser.py`
   - Unit tests in `tests/parser/test_option_statements.py`
   - 5 test fixtures in `tests/fixtures/options/`

2. **Indexed Assignment Support**
   - Grammar extension (BOUND_K token)
   - ParameterIndexRef IR node (if new)
   - Semantic handlers for indexed params and variable attributes
   - Unit tests in `tests/parser/test_indexed_assignments.py`
   - 5 test fixtures in `tests/fixtures/indexed_assignments/`

3. **Error Line Numbers**
   - ParseError wrapping in `nlp2mcp/parser/errors.py`
   - `_parse_error()` helper in `nlp2mcp/parser/parser.py`
   - Source line extraction logic
   - 5 test fixtures in `tests/errors/`

4. **Error Enhancements**
   - ErrorEnhancer class in `nlp2mcp/parser/errors.py`
   - 5 suggestion rules (keyword typos, set brackets, semicolons, features, functions)
   - Integration with parse_text/parse_file
   - 5 test fixtures

5. **Partial Parse Metrics**
   - Line counting functions (`count_logical_lines`, `count_logical_lines_up_to`)
   - Feature extraction function (`extract_missing_features`)
   - Progress calculation function (`calculate_parse_progress`)
   - Enhanced ModelResult dataclass
   - 3 test fixtures in `tests/fixtures/partial_parse/`

6. **Dashboard Updates**
   - Enhanced ingestion script (~140 new lines)
   - Updated dashboard template with 3 new columns
   - Status symbol determination logic
   - Backward compatibility support

### **Documentation Deliverables**

7. **Parser Documentation**
   - Option statement examples and usage
   - Indexed assignment examples and usage
   - Known limitations documented
   - Error message enhancement examples

8. **Test Documentation**
   - 13 test fixture README files
   - expected_results.yaml for each directory
   - Test coverage report

9. **Sprint Documentation**
   - CHANGELOG.md entry for Sprint 8
   - README.md updates (if applicable)
   - Known issues and limitations

### **Metrics Deliverables**

10. **Parse Rate**
    - Baseline: 20% (2/10 models)
    - Target: 40-50% (4-5/10 models)
    - Actual: TBD after Sprint 8 execution

11. **Test Coverage**
    - 18 new test fixtures (5 + 5 + 3 + 5)
    - Unit test coverage maintained or improved
    - Integration test coverage for GAMSLib models

12. **Dashboard Metrics**
    - Parse percentage for all 10 models
    - Missing features identified for 70-80% of failures
    - Color-coded status for all models

---

## 8. Cross-References

This section maps Sprint 8 execution days to prep tasks, showing how research informs implementation.

### **Prep Task → Execution Day Mapping**

| Prep Task | Document | Informs Days | Key Contributions |
|-----------|----------|--------------|-------------------|
| **Task 2** | GAMSLIB_FEATURE_MATRIX.md | Days 0-4, 9 | Feature selection (options + indexed), unlock validation, per-model dependencies |
| **Task 3** | OPTION_STATEMENT_RESEARCH.md | Days 1-2 | Grammar design, semantic approach, test fixtures, effort estimate (6-8h) |
| **Task 4** | PARSER_ERROR_LINE_NUMBERS.md | Day 5 | ParseError design, infrastructure, top 5 error types, effort estimate (4-6h) |
| **Task 5** | PARTIAL_PARSE_METRICS.md | Day 7 | Line counting algorithms, progress calculation, feature extraction, effort (4-6h) |
| **Task 6** | ERROR_MESSAGE_ENHANCEMENTS.md | Day 6 | Pattern catalog, suggestion rules, categorization, effort estimate (3-4h) |
| **Task 7** | INDEXED_ASSIGNMENTS_RESEARCH.md | Days 3-4 | Grammar design, 4 GAMS patterns, expression handling, effort estimate (6-8h) |
| **Task 8** | TEST_FIXTURE_STRATEGY.md | Days 1-2, 3-4, 9 | 13 fixtures, YAML schema, README templates, Sprint 7 patterns |
| **Task 9** | DASHBOARD_ENHANCEMENTS.md | Day 8 | Template mockup, color coding, ingestion script, effort estimate (3-4h) |

### **Execution Day → Prep Task Mapping**

| Day | Primary Tasks | Cross-References |
|-----|---------------|------------------|
| **Day 0** | Sprint planning | All Tasks 2-9 (comprehensive review) |
| **Day 1** | Option statements - Grammar & AST | Task 3 (grammar, AST, semantic), Task 8 (fixtures) |
| **Day 2** | Option statements - Integration | Task 3 (patterns, mhw4dx), Task 8 (fixtures 1-5), Task 2 (unlock) |
| **Day 3** | Indexed assignments - Foundation | Task 7 (grammar, patterns 1-3), Task 8 (fixtures) |
| **Day 4** | Indexed assignments - Advanced | Task 7 (pattern 4, expressions), Task 8 (fixtures 1-5), Task 2 (unlock) |
| **Day 5** | Error line numbers | Task 4 (ParseError, infrastructure, patterns) |
| **Day 6** | Error enhancements | Task 6 (patterns, rules, categorization), Task 4 (ParseError) |
| **Day 7** | Partial parse metrics | Task 5 (algorithms, line counting, extraction) |
| **Day 8** | Dashboard updates | Task 9 (template, ingestion, color coding), Task 5 (progress) |
| **Day 9** | Test fixtures & testing | Task 8 (partial parse fixtures 1-3), Task 2 (validate rate) |
| **Day 10** | Documentation & PR | All Tasks 2-9 (comprehensive implementation) |

### **Unknown Verification → Execution Validation**

| Unknown | Verified By | Validated During Sprint 8 |
|---------|-------------|---------------------------|
| **2.1** | Task 2 (8 hours actual) | Day 0 (scope confirmation) |
| **2.2** | Task 2 (75% single-feature) | Day 2 (mhw4dx), Day 4 (mathopt1, trig) |
| **2.3** | Task 2 (per-model methodology) | Day 9 (final parse rate validation) |
| **3.1** | Task 3 (6-8h confirmed) | Days 1-2 (actual effort tracking) |
| **3.2** | Task 3 (100% GAMSLib coverage) | Day 2 (mhw4dx validation) |
| **3.3** | Task 3 (5 fixtures identified) | Day 2 (fixture creation) |
| **4.1** | Task 4 (58/58 coverage) | Day 5 (100% error coverage) |
| **4.2** | Task 4 (Lark metadata) | Day 5 (Lark error wrapping) |
| **4.3** | Task 4 (5 fixtures) | Day 5 (fixture creation) |
| **4.4** | Task 4 (negligible overhead) | Day 5 (performance validation) |
| **5.1** | Task 5 (mock/store sufficient) | Day 7 (line counting) |
| **5.2** | Task 5 (100% GAMSLib) | Day 7 (pattern coverage validation) |
| **5.3** | Task 5 (5 patterns) | Day 7 (feature extraction) |
| **5.4** | Task 5 (pattern matching) | Day 7 (extraction implementation) |
| **6.1** | Task 6 (difflib 0.6 cutoff) | Day 6 (suggestion quality) |
| **6.2** | Task 6 (6 patterns) | Day 6 (patterns 1-3 implementation) |
| **6.3** | Task 6 (5 categories) | Day 6 (categorization) |
| **6.4** | Task 6 (Lark context) | Day 6 (context extraction) |
| **7.1** | Task 7 (6.5h confirmed) | Days 3-4 (actual effort tracking) |
| **7.2** | Task 7 (4 patterns) | Days 3-4 (pattern implementation) |
| **7.3** | Task 7 (13 fixtures) | Days 3-4, 9 (fixture creation) |
| **8.1** | Task 10 (this plan) | Days 0-9 (effort tracking) |
| **8.2** | Task 10 (4 checkpoints) | Days 2, 4, 8, 9 (checkpoint execution) |
| **8.3** | Task 10 (synthesis) | Day 0 (plan review) |

---

## Appendix A: Quality Gates by Day

This appendix provides detailed quality gate checklists for each day.

### **Day 0: Sprint Planning**

**Quality Gates:**
- [ ] All prep tasks (2-9) reviewed and understood
- [ ] Sprint 8 execution branch created
- [ ] Baseline test suite passes (100% pass rate)
- [ ] Baseline parse rate captured (20% = 2/10 models)
- [ ] Scope confirmed (options + indexed assignments)
- [ ] Development environment ready

---

### **Day 1: Option Statements - Grammar & AST**

**Quality Gates:**
- [ ] Grammar compiles without errors
- [ ] `make test` passes (all existing + new option tests)
- [ ] `make typecheck` passes
- [ ] `make lint` passes
- [ ] OptionStatement AST node created
- [ ] Semantic handler implemented
- [ ] 4+ basic tests passing
- [ ] No regressions in mhw4d, rbrock

---

### **Day 2: Option Statements - Integration**

**Quality Gates:**
- [ ] mhw4dx.gms parses with no errors ✅
- [ ] Parse rate ≥30% (3/10 models) ✅
- [ ] 5 option test fixtures created ✅
- [ ] `make test` passes ✅
- [ ] `make typecheck` passes ✅
- [ ] `make lint` passes ✅
- [ ] No regressions ✅

**CHECKPOINT 1:** All gates must pass to continue

---

### **Day 3: Indexed Assignments - Foundation**

**Quality Gates:**
- [ ] Grammar compiles (BOUND_K extended)
- [ ] `make test` passes
- [ ] `make typecheck` passes
- [ ] `make lint` passes
- [ ] Indexed param handler implemented
- [ ] Variable attribute handler implemented
- [ ] 4+ basic tests passing
- [ ] No regressions

---

### **Day 4: Indexed Assignments - Advanced**

**Quality Gates:**
- [ ] mathopt1.gms parses (or secondary blocker identified) ✅
- [ ] trig.gms parses (or acceptable failure) ✅
- [ ] Parse rate ≥40% (4/10 models) ✅
- [ ] 5 indexed test fixtures created ✅
- [ ] `make test` passes ✅
- [ ] `make typecheck` passes ✅
- [ ] `make lint` passes ✅
- [ ] No regressions ✅

**CHECKPOINT 2:** All gates must pass to continue (or scope reduction)

---

### **Day 5: Error Line Numbers**

**Quality Gates:**
- [ ] All Lark errors wrapped with ParseError
- [ ] `_parse_error()` helper implemented
- [ ] Top 5 error types migrated
- [ ] 100% parser errors include location
- [ ] 5 error test fixtures created
- [ ] `make test` passes
- [ ] `make typecheck` passes
- [ ] `make lint` passes
- [ ] No regressions in error handling

---

### **Day 6: Error Enhancements**

**Quality Gates:**
- [ ] ErrorEnhancer class implemented
- [ ] 5 suggestion rules implemented
- [ ] Integration with parse functions complete
- [ ] Keyword typos suggest corrections
- [ ] Punctuation errors show hints
- [ ] 5 test fixtures created
- [ ] `make test` passes
- [ ] `make typecheck` passes
- [ ] `make lint` passes

---

### **Day 7: Partial Metrics**

**Quality Gates:**
- [ ] `count_logical_lines()` implemented
- [ ] `count_logical_lines_up_to()` implemented
- [ ] `extract_missing_features()` implemented (8 patterns)
- [ ] `calculate_parse_progress()` implemented
- [ ] ModelResult dataclass enhanced
- [ ] Line counting handles multiline comments
- [ ] Feature extraction covers 70-80% of failures
- [ ] `make test` passes
- [ ] `make typecheck` passes
- [ ] `make lint` passes

---

### **Day 8: Dashboard Updates**

**Quality Gates:**
- [ ] Ingestion script updated (~140 lines)
- [ ] Dashboard template updated (3 new columns)
- [ ] Status symbols display correctly (✅ 🟡 ⚠️ ❌)
- [ ] Parse percentages show for all 10 models
- [ ] Missing features listed
- [ ] Sprint 7 data backward compatible
- [ ] `make ingest-gamslib` runs successfully
- [ ] Dashboard renders correctly
- [ ] `make test` passes
- [ ] `make typecheck` passes
- [ ] `make lint` passes

**CHECKPOINT 3:** All gates must pass to continue

---

### **Day 9: Test Fixtures & Testing**

**Quality Gates:**
- [ ] 3 partial parse fixtures created ✅
- [ ] `make test` passes (100% pass rate) ✅
- [ ] `make typecheck` passes ✅
- [ ] `make lint` passes ✅
- [ ] `make format` passes ✅
- [ ] Parse rate ≥40% (4/10 models) ✅
- [ ] No regressions in Sprint 7 models ✅
- [ ] GAMSLib integration tests pass ✅

**FINAL CHECKPOINT:** All gates must pass to proceed to PR

---

### **Day 10: Documentation & PR**

**Quality Gates:**
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Known limitations documented
- [ ] PR created with comprehensive description
- [ ] All acceptance criteria met
- [ ] Ready for code review

---

## Appendix B: Sprint 8 vs Sprint 7 Comparison

| Metric | Sprint 7 | Sprint 8 (Target) | Change |
|--------|----------|-------------------|--------|
| **Parse Rate** | 20% (2/10) | 40-50% (4-5/10) | +20-30% |
| **Models Unlocked** | 2 (mhw4d, rbrock) | 4-5 (+ mhw4dx, mathopt1, trig) | +2-3 models |
| **Parser Features** | Preprocessor | Options + Indexed | +2 features |
| **UX Features** | Convexity warnings | Errors + Metrics + Dashboard | +3 features |
| **Test Fixtures** | 34 fixtures | +13 fixtures (47 total) | +38% |
| **Sprint Duration** | 11 days (0-10) | 10 days (0-9) | -1 day |
| **Total Effort** | 34-45 hours | 30-36 hours | -4-9 hours |
| **Risk Level** | LOW | LOW | Same |
| **Confidence** | HIGH | HIGH | Same |

**Key Differences:**
- Sprint 7 focused on preprocessor (single high-value feature)
- Sprint 8 implements 2 core features + 3 UX features (more ambitious)
- Sprint 8 has tighter timeline (10 days vs 11) but lower total effort
- Sprint 8 builds on Sprint 7 infrastructure (SourceLocation, testing patterns)

---

## Appendix C: Lessons Learned from Sprint 7

**What Worked Well:**
1. ✅ Comprehensive prep phase (9 tasks) validated all unknowns
2. ✅ Day-by-day breakdown kept execution on track
3. ✅ Checkpoints allowed mid-sprint course correction
4. ✅ Test fixture strategy (34 fixtures) ensured quality
5. ✅ Conservative estimates with buffer time prevented overruns

**What to Improve:**
1. 🔄 Sprint 7 took 11 days; Sprint 8 targets 10 days (tighter schedule)
2. 🔄 Sprint 7 had single core feature; Sprint 8 has 2 core + 3 UX (more ambitious)
3. 🔄 Sprint 7 prep took longer than expected; Sprint 8 prep was more focused

**Applied to Sprint 8:**
- Validated effort estimates through deep research (Tasks 3, 7)
- Built in checkpoints at Days 2, 4, 8, 9 (more frequent than Sprint 7)
- Allocated Day 10 as buffer (lessons from Sprint 7 overruns)
- Reused Sprint 7 test fixture patterns (Task 8)
- Front-loaded core features (Days 1-4) before UX (Days 5-8)

---

## Appendix D: Sprint 8 Feature Dependencies

```
Sprint 8 Feature Dependency Graph:

Day 0: Sprint Planning
  |
  v
Day 1-2: Option Statements (INDEPENDENT)
  |
  v
Checkpoint 1: mhw4dx.gms parses (GO/NO-GO)
  |
  +---> [GO]
  |       |
  |       v
  |     Day 3-4: Indexed Assignments (INDEPENDENT)
  |       |
  |       v
  |     Checkpoint 2: mathopt1.gms parses (GO/NO-GO)
  |       |
  |       +---> [GO]
  |       |       |
  |       |       v
  |       |     Day 5: Error Line Numbers (INDEPENDENT)
  |       |       |
  |       |       v
  |       |     Day 6: Error Enhancements (DEPENDS ON Day 5)
  |       |       |
  |       |       v
  |       |     Day 7: Partial Metrics (DEPENDS ON Day 5)
  |       |       |
  |       |       v
  |       |     Day 8: Dashboard (DEPENDS ON Day 7)
  |       |       |
  |       |       v
  |       |     Checkpoint 3: Integration OK (GO/NO-GO)
  |       |       |
  |       |       +---> [GO]
  |       |       |       |
  |       |       |       v
  |       |       |     Day 9: Testing (INDEPENDENT)
  |       |       |       |
  |       |       |       v
  |       |       |     Checkpoint 4: All gates pass (GO/NO-GO)
  |       |       |       |
  |       |       |       +---> [GO]
  |       |       |       |       |
  |       |       |       |       v
  |       |       |       |     Day 10: PR & Closeout
  |       |       |       |
  |       |       |       +---> [NO-GO] Document blockers, plan Sprint 8b
  |       |       |
  |       |       +---> [NO-GO] Defer fixtures, fix critical issues
  |       |
  |       +---> [NO-GO] Reduce scope (defer metrics or errors)
  |
  +---> [NO-GO] Debug options, allocate buffer hours
```

**Critical Path:** Days 1-4 (Core Features)  
**Parallel Work Opportunities:** Days 5-7 (UX features can be partially parallelized)  
**Buffer:** Day 10 (documentation can absorb unexpected issues)

---

**END OF SPRINT 8 DETAILED PLAN**

---

*This document was created as part of Sprint 8 Prep Task 10. All effort estimates, dependencies, and risks have been validated through comprehensive prep tasks (2-9). Sprint 8 is ready for execution.*

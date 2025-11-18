# Sprint 8 Day-by-Day Prompts

This file contains comprehensive prompts for each day of Sprint 8 (Days 0-10). Each prompt is designed to be used when starting work on that specific day.

**Sprint 8 Overview:**
- **Goal:** High-ROI Parser Features & UX Enhancements
- **Parse Rate Target:** 40-50% (conservative: 30%, fallback: 25%)
- **Duration:** 11 days (Days 0-10, with Day 10 as BUFFER)
- **Total Effort:** 30-41 hours (average 35.5h)

---

## Day 0 Prompt: Sprint Planning & Setup

**Branch:** Create a new branch named `sprint8-day0-setup` from `main`

**Objective:** Prepare environment, review plan, confirm scope, and verify all prep work is complete

**Time Estimate:** 2-3 hours

**Prerequisites:**
- Read `/Users/jeff/experiments/nlp2mcp/docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 1-470, complete plan)
- Review `/Users/jeff/experiments/nlp2mcp/docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` (all unknowns verified)
- Review all prep task documents:
  - Task 2: `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` (feature selection)
  - Task 3: `docs/planning/EPIC_2/SPRINT_8/OPTION_STATEMENT_RESEARCH.md` (option statements)
  - Task 4: `docs/planning/EPIC_2/SPRINT_8/PARSER_ERROR_LINE_NUMBERS.md` (error tracking)
  - Task 5: `docs/planning/EPIC_2/SPRINT_8/PARTIAL_PARSE_METRICS.md` (metrics design)
  - Task 6: `docs/planning/EPIC_2/SPRINT_8/ERROR_MESSAGE_ENHANCEMENTS.md` (error patterns)
  - Task 7: `docs/planning/EPIC_2/SPRINT_8/INDEXED_ASSIGNMENTS_RESEARCH.md` (indexed assignments)
  - Task 8: `docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md` (fixtures)
  - Task 9: `docs/planning/EPIC_2/SPRINT_8/DASHBOARD_ENHANCEMENTS.md` (dashboard)

**Tasks to Complete (2.25 hours):**

1. **Review Sprint 8 Plan** (30 min)
   - Read PLAN.md in full (all sections: goals, days, checkpoints, effort, risks)
   - Review acceptance criteria (Section 5: Success Criteria)
   - Understand checkpoint definitions (Section 3: Days 2, 4, 8, 9)
   - Note critical path: Days 1-4 (core features) → Days 5-7 (UX) → Days 8-9 (integration)

2. **Set Up Development Branch** (15 min)
   - Create branch `sprint8-day0-setup` from main
   - Verify test suite baseline: `make test` (all tests must pass)
   - Run `make ingest-gamslib` to capture baseline parse rate (should be 20% = 2/10 models)
   - Document baseline: test count, test time, parse rate

3. **Confirm Sprint Scope** (1 hour)
   - Review Task 2 (GAMSLIB_FEATURE_MATRIX.md): Option statements unlock mhw4dx (+10%), Indexed assignments unlock mathopt1 + trig (+20%)
   - Review Task 8 (TEST_FIXTURE_STRATEGY.md): 13 fixtures total (5 options + 5 indexed + 3 partial)
   - Identify any prep tasks needing clarification
   - Verify feature selection rationale: Options (6-8h) + Indexed (6-8h) = 12-16h parser work
   - Update PLAN.md if any scope adjustments needed

4. **Verify Known Unknowns** (30 min) **[EXPLICIT DELIVERABLE]**
   - Open `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md`
   - Verify unknowns 8.1, 8.2, 8.3 are marked as ✅ VERIFIED:
     - 8.1: Effort allocation (30-41h, average 35.5h) - Check verification results
     - 8.2: Parse rate targets (40% primary, 50% stretch, 30% fallback) - Check scenario analysis
     - 8.3: 4 checkpoints defined (Days 2, 4, 8, 9) - Check checkpoint criteria
   - If any unknowns are NOT verified, escalate immediately (this is blocking)
   - Confirm all Critical and High priority unknowns have verification results

5. **Set Up Tracking** (30 min)
   - Review quality gate checklists (PLAN.md Appendix A)
   - Prepare checkpoint criteria checklists for Days 2, 4, 8, 9
   - Note buffer strategy: Day 10 is designated BUFFER for overruns

**Deliverables:**
- Sprint 8 execution branch created (`sprint8-day0-setup`)
- Baseline metrics captured:
  - Parse rate: 20% (2/10 models: mhw4d, rbrock)
  - Test count: [document actual count]
  - Test time: [document actual time]
- Scope confirmed and documented
- **KNOWN_UNKNOWNS.md verification confirmed** (8.1, 8.2, 8.3 all ✅ VERIFIED)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] All tests passing on baseline
  - [ ] Baseline parse rate confirmed at 20% (2/10 models: mhw4d, rbrock)
  - [ ] Development environment ready
  - [ ] **Unknowns 8.1-8.3 verified in KNOWN_UNKNOWNS.md**
  - [ ] All prep tasks reviewed and understood
- [ ] Mark Day 0 as complete in `docs/planning/EPIC_2/SPRINT_8/PLAN.md`
- [ ] Check off Day 0 in `README.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 8 Day 0: Sprint Planning & Setup" \
                --body "Completes Day 0 tasks from Sprint 8 PLAN.md (lines 127-157)" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 127-157: Day 0 tasks)
- `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` (all unknowns, verification status)
- All Task 2-9 documents (comprehensive review)

---

## Day 1 Prompt: Option Statements - Grammar & AST

**Branch:** Create a new branch named `sprint8-day1-option-statements` from `main`

**Objective:** Implement option statement parsing (grammar, AST, basic tests)

**Time Estimate:** 6-8 hours

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_8/OPTION_STATEMENT_RESEARCH.md` (Task 3) - Grammar design, semantic approach
- Review `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` (unknowns 1.1, 1.2, 1.3 verification results)
- Review `docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md` (Task 8) - Option statement fixtures 1-5
- Review `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 159-188: Day 1 tasks)

**Tasks to Complete (6-8 hours):**

1. **Grammar Extension** (1-2 hours)
   - Open `nlp2mcp/parser/gams.lark`
   - Add option statement rules (see OPTION_STATEMENT_RESEARCH.md Section 3):
     ```lark
     option_stmt: ("option"i | "options"i) option_list SEMI
     option_list: option_item ("," option_item)*
     option_item: ID "=" option_value  -> option_with_value
                | ID                   -> option_flag
     option_value: NUMBER
                 | "on"i | "off"i
     ```
   - Add `option_stmt` to `statement` rule as alternative
   - Verify grammar compiles without errors: `python -c "from lark import Lark; from nlp2mcp.parser.gams import gams_grammar; Lark(gams_grammar)"`

2. **AST Node Creation** (1 hour)
   - Open `nlp2mcp/ir/nodes.py`
   - Create `OptionStatement` dataclass:
     ```python
     @dataclass
     class OptionStatement:
         options: List[Tuple[str, Optional[Union[int, str]]]]  # [(name, value), ...]
         location: SourceLocation
     ```
   - Add to IR node exports in `__init__.py`
   - Add to type hints where needed

3. **Semantic Handler** (2-3 hours)
   - Open `nlp2mcp/parser/parser.py`
   - Implement `_transform_option_stmt()` method
   - Handle single option: `option limrow = 0;`
   - Handle multi-option: `option limrow = 0, limcol = 0;`
   - Extract option name and value from parse tree
   - Store in AST using mock/store approach (no semantic behavior)
   - Add location tracking using `_node_position()` helper
   - Reference: OPTION_STATEMENT_RESEARCH.md Section 4 (semantic handler design)

4. **Basic Tests** (2 hours)
   - Create `tests/parser/test_option_statements.py`
   - Test single integer option: `option limrow = 0;`
   - Test multi-option: `option limrow = 0, limcol = 0;`
   - Test boolean on/off: `option solprint = off;`
   - Test case insensitivity: `OPTION LimRow = 0;`
   - Verify AST structure (OptionStatement with correct options list)
   - Run `make test` to verify all tests pass

**Deliverables:**
- Option statement grammar rules added to `gams.lark`
- `OptionStatement` AST node created in `nodes.py`
- Semantic handler `_transform_option_stmt()` implemented in `parser.py`
- 4+ basic tests passing in `test_option_statements.py`

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `make test` passes (all existing tests + new option tests)
  - [ ] `make typecheck` passes
  - [ ] `make lint` passes
  - [ ] Grammar compiles without errors
  - [ ] No regressions in existing models (mhw4d, rbrock still parse)
  - [ ] OptionStatement AST node exports correctly
- [ ] Mark Day 1 as complete in `docs/planning/EPIC_2/SPRINT_8/PLAN.md`
- [ ] Check off Day 1 in `README.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 8 Day 1: Option Statements - Grammar & AST" \
                --body "Completes Day 1 tasks from Sprint 8 PLAN.md (lines 159-188)" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 159-188: Day 1 tasks)
- `docs/planning/EPIC_2/SPRINT_8/OPTION_STATEMENT_RESEARCH.md` (grammar design, semantic approach)
- `docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md` (option statement fixtures)

---

## Day 2 Prompt: Option Statements - Integration & Fixtures

**Branch:** Create a new branch named `sprint8-day2-option-integration` from `main`

**Objective:** Complete option statement implementation with full test coverage and mhw4dx validation

**Time Estimate:** 4-5 hours

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_8/OPTION_STATEMENT_RESEARCH.md` (Task 3) - All 5 fixture patterns
- Review `docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md` (Task 8) - Fixtures 1-5, README template
- Review `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` (Task 2) - mhw4dx unlock validation
- Review `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 190-227: Day 2 tasks)

**Tasks to Complete (4-5 hours):**

1. **Advanced Option Patterns** (1-2 hours)
   - Implement decimals option: `option decimals = 8;`
   - Test option placement (before/after declarations)
   - Test mhw4dx.gms pattern from OPTION_STATEMENT_RESEARCH.md:
     - `option limcol = 0, limrow = 0;` (line 37)
     - `option decimals = 8;` (line 47)
   - Verify AST structure for all patterns
   - Add tests for edge cases (empty options, syntax errors)

2. **Test Fixture Creation** (2 hours)
   - Create `tests/fixtures/options/` directory
   - Create 5 GMS fixture files (from TEST_FIXTURE_STRATEGY.md):
     - `01_single_integer.gms`: `option limrow = 0;`
     - `02_multiple_options.gms`: `option limrow = 0, limcol = 0;`
     - `03_decimals_option.gms`: `option decimals = 8;`
     - `04_placement.gms`: Options in different locations (before/after declarations)
     - `05_mhw4dx_pattern.gms`: Real GAMSLib pattern from mhw4dx.gms
   - Create `tests/fixtures/options/expected_results.yaml` with expected AST structures
   - Create `tests/fixtures/options/README.md` documenting fixtures and their purpose

3. **GAMSLib Validation** (1 hour)
   - Copy `tests/fixtures/gamslib/mhw4dx.gms` (if not already present)
   - Run mhw4dx.gms through parser: `python -m nlp2mcp.parser parse tests/fixtures/gamslib/mhw4dx.gms`
   - Verify it parses successfully with no errors
   - Inspect AST for option statements (should contain OptionStatement nodes)
   - Capture parse success in logs
   - Document findings

4. **Integration Tests** (30 min)
   - Add mhw4dx.gms to GAMSLib test suite (if not already included)
   - Run `make ingest-gamslib`
   - Verify parse rate: 30% (3/10 models: mhw4d, rbrock, mhw4dx)
   - Update dashboard in `docs/status/GAMSLIB_CONVERSION_STATUS.md`
   - Verify no regressions in existing models

**Deliverables:**
- 5 option statement test fixtures with YAML and README in `tests/fixtures/options/`
- mhw4dx.gms parsing successfully (no errors)
- Parse rate increased to 30% (3/10 models)
- All tests passing (`make test`)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `make test` passes (including new fixture tests)
  - [ ] mhw4dx.gms parses with no errors ✅
  - [ ] Parse rate ≥30% (3/10 models minimum) ✅
  - [ ] No regressions in Sprint 7 models
  - [ ] 5 fixtures created with YAML and README
- [ ] Mark Day 2 as complete in `docs/planning/EPIC_2/SPRINT_8/PLAN.md`
- [ ] Check off Day 2 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] **Check off all Checkpoint 1 criteria in PLAN.md (lines 229-240)**

**CHECKPOINT 1: Option Statements Complete**
- **Go Criteria:**
  - [ ] mhw4dx.gms parses successfully ✅
  - [ ] Parse rate ≥30% (3/10 models) ✅
  - [ ] All tests passing ✅
- **Go Decision:** Continue to indexed assignments (Days 3-4)
- **No-Go Decision:** Debug option implementation, allocate buffer hours from Day 9

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 8 Day 2: Option Statements - Integration & Fixtures" \
                --body "Completes Day 2 tasks from Sprint 8 PLAN.md (lines 190-240). CHECKPOINT 1: Option Statements Complete." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 190-240: Day 2 tasks + Checkpoint 1)
- `docs/planning/EPIC_2/SPRINT_8/OPTION_STATEMENT_RESEARCH.md` (all 5 fixture patterns)
- `docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md` (fixtures 1-5, README template)
- `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` (mhw4dx unlock validation)

---

## Day 3 Prompt: Indexed Assignments - Grammar & Foundation

**Branch:** Create a new branch named `sprint8-day3-indexed-assignments` from `main`

**Objective:** Implement indexed assignment parsing (grammar, semantic handlers for basic patterns)

**Time Estimate:** 5.25-7.25 hours

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_8/INDEXED_ASSIGNMENTS_RESEARCH.md` (Task 7) - Grammar, semantic handlers, patterns 1-4
- Review `docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md` (Task 8) - Indexed assignment fixtures 1-5
- Review `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 244-271: Day 3 tasks)

**Tasks to Complete (5.25-7.25 hours):**

1. **Grammar Extension** (15 min)
   - Open `nlp2mcp/parser/gams.lark`
   - Extend `BOUND_K` token to include `.m` (marginal attribute):
     ```lark
     BOUND_K: /(lo|up|fx|l|m)/i  # Add .m for marginal attribute
     ```
   - Verify grammar compiles without errors
   - Note: Existing `ref_indexed` and `ref_bound` rules already support most patterns (per INDEXED_ASSIGNMENTS_RESEARCH.md Section 3)

2. **Indexed Parameter Assignment Handler** (2-3 hours)
   - Open `nlp2mcp/parser/parser.py`
   - Implement semantic handler for `p('i1') = 10;` pattern
   - Create `ParameterIndexRef` IR node (if not exists) in `nlp2mcp/ir/nodes.py`
   - Handle 1D indexing: single string literal index
   - Handle 2D indexing: `report('x1','global') = 1;`
   - Validate index count matches parameter declaration (optional, can defer)
   - Add to assignment statement handler
   - Reference: INDEXED_ASSIGNMENTS_RESEARCH.md Section 4.1

3. **Variable Attribute Handler** (1-2 hours)
   - Implement semantic handler for `xdiff = x1.l;` pattern
   - Support `.l` (level), `.m` (marginal), `.lo`, `.up`, `.fx` attributes
   - Store as initial value (pre-solve limitation documented)
   - Handle attribute access in RHS expressions
   - Reference: INDEXED_ASSIGNMENTS_RESEARCH.md Section 4.2

4. **Basic Tests** (2 hours)
   - Create `tests/parser/test_indexed_assignments.py`
   - Test 1D indexed param: `p('i1') = 10;`
   - Test 2D indexed param: `report('x1','global') = 1;`
   - Test variable .l attribute: `xdiff = x1.l;`
   - Test simple indexed expression: `p('a') = 5;`
   - Verify AST structure
   - Run `make test` to verify all tests pass

**Deliverables:**
- Grammar extended with `.m` attribute in `BOUND_K` token
- Indexed parameter assignment handler implemented
- Variable attribute handler implemented
- 4+ basic tests passing in `test_indexed_assignments.py`

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `make test` passes (all existing tests + new indexed tests)
  - [ ] `make typecheck` passes
  - [ ] `make lint` passes
  - [ ] Grammar compiles without errors
  - [ ] No regressions in existing models
  - [ ] Indexed parameter handler working
  - [ ] Variable attribute handler working
- [ ] Mark Day 3 as complete in `docs/planning/EPIC_2/SPRINT_8/PLAN.md`
- [ ] Check off Day 3 in `README.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 8 Day 3: Indexed Assignments - Grammar & Foundation" \
                --body "Completes Day 3 tasks from Sprint 8 PLAN.md (lines 244-271)" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 244-271: Day 3 tasks)
- `docs/planning/EPIC_2/SPRINT_8/INDEXED_ASSIGNMENTS_RESEARCH.md` (grammar, semantic handlers, patterns 1-4)
- `docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md` (indexed assignment fixtures 1-5)

---

## Day 4 Prompt: Indexed Assignments - Advanced Patterns & Integration

**Branch:** Create a new branch named `sprint8-day4-indexed-integration` from `main`

**Objective:** Complete indexed assignment implementation with expressions, fixtures, and GAMSLib validation

**Time Estimate:** 4.5-5.5 hours

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_8/INDEXED_ASSIGNMENTS_RESEARCH.md` (Task 7) - All 4 patterns, expression handling
- Review `docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md` (Task 8) - Fixtures 1-5, README template
- Review `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` (Task 2) - mathopt1 + trig unlock validation
- Review `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 273-310: Day 4 tasks)

**Tasks to Complete (4.5-5.5 hours):**

1. **Indexed Expressions in RHS** (1.5-2 hours)
   - Implement `p('diff') = p('global') - p('solver');` pattern
   - Create `ParameterRef` IR node for indexed parameter access (if needed)
   - Handle indexed params in expressions (not just assignments)
   - Support arithmetic operations with indexed refs
   - Add comprehensive tests for expression patterns
   - Reference: INDEXED_ASSIGNMENTS_RESEARCH.md Section 4.3

2. **Test Fixture Creation** (1.5 hours)
   - Create `tests/fixtures/indexed_assignments/` directory
   - Create 5 GMS fixture files (from TEST_FIXTURE_STRATEGY.md):
     - `01_simple_1d.gms`: `p('i1') = 10;`
     - `02_multi_dim_2d.gms`: mathopt1 pattern - `report('x1','global') = 1;`
     - `03_variable_attributes.gms`: trig pattern - `xdiff = x1.l;`
     - `04_indexed_expressions.gms`: `p('diff') = p('global') - p('solver');`
     - `05_error_index_mismatch.gms`: Invalid index count (expected to fail)
   - Create `tests/fixtures/indexed_assignments/expected_results.yaml`
   - Create `tests/fixtures/indexed_assignments/README.md`

3. **GAMSLib Validation** (1-1.5 hours)
   - Run mathopt1.gms through parser: `python -m nlp2mcp.parser parse tests/fixtures/gamslib/mathopt1.gms`
   - Run trig.gms through parser: `python -m nlp2mcp.parser parse tests/fixtures/gamslib/trig.gms`
   - Verify both parse successfully (or identify secondary blockers)
   - Inspect AST for indexed assignments
   - Capture parse success/failure in logs
   - Document any unexpected issues

4. **Integration Tests** (30 min)
   - Add mathopt1.gms and trig.gms to GAMSLib test suite
   - Run `make ingest-gamslib`
   - Verify parse rate: 40-50% (4-5/10 models)
   - Update dashboard in `docs/status/GAMSLIB_CONVERSION_STATUS.md`
   - Verify no regressions

**Deliverables:**
- 5 indexed assignment test fixtures with YAML and README in `tests/fixtures/indexed_assignments/`
- mathopt1.gms and/or trig.gms parsing successfully
- Parse rate increased to 40-50% (4-5/10 models)
- All tests passing (`make test`)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `make test` passes (including new fixture tests)
  - [ ] mathopt1.gms parses (high confidence: 95%) ✅
  - [ ] trig.gms parses (medium confidence: 85%) ✅
  - [ ] Parse rate ≥40% (4/10 models minimum) ✅
  - [ ] No regressions in Sprint 7-8 models
  - [ ] 5 fixtures created with YAML and README
- [ ] Mark Day 4 as complete in `docs/planning/EPIC_2/SPRINT_8/PLAN.md`
- [ ] Check off Day 4 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] **Check off all Checkpoint 2 criteria in PLAN.md (lines 312-322)**

**CHECKPOINT 2: Indexed Assignments Complete**
- **Go Criteria:**
  - [ ] mathopt1.gms parses successfully ✅
  - [ ] Parse rate ≥40% (4/10 models) ✅
  - [ ] All tests passing ✅
- **Go Decision:** Continue to UX enhancements (Days 5-7)
- **No-Go Decision:** Assess scope reduction (defer partial metrics or error messages), focus on core functionality

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 8 Day 4: Indexed Assignments - Advanced Patterns & Integration" \
                --body "Completes Day 4 tasks from Sprint 8 PLAN.md (lines 273-322). CHECKPOINT 2: Indexed Assignments Complete." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 273-322: Day 4 tasks + Checkpoint 2)
- `docs/planning/EPIC_2/SPRINT_8/INDEXED_ASSIGNMENTS_RESEARCH.md` (all 4 patterns, expression handling)
- `docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md` (fixtures 1-5, README template)
- `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` (mathopt1 + trig unlock validation)

---

## Day 5 Prompt: Error Line Numbers & Source Context

**Branch:** Create a new branch named `sprint8-day5-error-line-numbers` from `main`

**Objective:** Consolidate all parser errors on ParseError class with line numbers and source context

**Time Estimate:** 4-4.5 hours

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_8/PARSER_ERROR_LINE_NUMBERS.md` (Task 4) - Design, infrastructure, patterns
- Review `docs/planning/EPIC_2/SPRINT_8/ERROR_MESSAGE_ENHANCEMENTS.md` (Task 6) - Error message patterns
- Review `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 326-354: Day 5 tasks)

**Tasks to Complete (4-4.5 hours):**

1. **Lark Error Wrapping** (1 hour)
   - Open `nlp2mcp/parser/parser.py`
   - Modify `parse_text()` to catch `UnexpectedToken` and `UnexpectedCharacters`
   - Extract source line from input using error line number
   - Wrap in `ParseError` with source line display and caret pointer
   - Preserve original error message
   - Reference: PARSER_ERROR_LINE_NUMBERS.md Section 3.1

2. **Create _parse_error() Helper** (1 hour)
   - Similar to existing `_error()` helper but returns `ParseError`
   - Extract source line from original GAMS input
   - Add caret pointer generation logic (point to error column)
   - Include location (line, column) in `ParseError`
   - Make it easy to use: `raise self._parse_error(node, "message", suggestions=["hint"])`
   - Reference: PARSER_ERROR_LINE_NUMBERS.md Section 3.2

3. **Migrate Top 5 Error Types** (1-1.5 hours)
   - Identify top 5 most common semantic errors from `parser.py`
   - Add actionable suggestions for each type:
     - "Assignments must use numeric constants" → "Use a literal number instead of function call"
     - "Indexed assignments not supported" → "This feature will be available in Sprint 9"
   - Replace `_error()` calls with `_parse_error()` calls
   - Ensure all include source context and suggestions
   - Reference: PARSER_ERROR_LINE_NUMBERS.md Section 4

4. **Test Fixtures** (1 hour)
   - Create 5 test fixtures in `tests/errors/`:
     - Lark UnexpectedToken wrapping
     - Lark UnexpectedCharacters wrapping
     - Semantic error with caret pointer
     - Semantic error with suggestion
     - Coverage test (all error types include location)
   - Verify all errors include line/column numbers
   - Run `make test` to verify

**Deliverables:**
- `ParseError` wrapping for Lark errors in `parse_text()`
- `_parse_error()` helper method in `parser.py`
- Top 5 error types migrated with suggestions
- 5 test fixtures for error wrapping
- 100% parser errors include location

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `make test` passes
  - [ ] All parser errors include line/column numbers ✅
  - [ ] Lark errors wrapped with source context ✅
  - [ ] No regressions in error handling
  - [ ] Top 5 error types have suggestions
- [ ] Mark Day 5 as complete in `docs/planning/EPIC_2/SPRINT_8/PLAN.md`
- [ ] Check off Day 5 in `README.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 8 Day 5: Error Line Numbers & Source Context" \
                --body "Completes Day 5 tasks from Sprint 8 PLAN.md (lines 326-354)" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 326-354: Day 5 tasks)
- `docs/planning/EPIC_2/SPRINT_8/PARSER_ERROR_LINE_NUMBERS.md` (design, infrastructure, patterns)
- `docs/planning/EPIC_2/SPRINT_8/ERROR_MESSAGE_ENHANCEMENTS.md` (error message patterns)

---

## Day 6 Prompt: Error Message Enhancements

**Branch:** Create a new branch named `sprint8-day6-error-enhancements` from `main`

**Objective:** Implement "did you mean?" suggestions and contextual hints for parser errors

**Time Estimate:** 3-4.5 hours

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_8/ERROR_MESSAGE_ENHANCEMENTS.md` (Task 6) - Patterns, rules, categorization
- Review `docs/planning/EPIC_2/SPRINT_8/PARSER_ERROR_LINE_NUMBERS.md` (Task 4) - ParseError integration
- Review `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 358-388: Day 6 tasks)

**Tasks to Complete (3-4.5 hours):**

1. **ErrorEnhancer Class** (1-1.5 hours)
   - Create `nlp2mcp/parser/errors.py` module (if not exists, or add to existing)
   - Implement `ErrorEnhancer` class with categorization logic
   - Implement `EnhancedError` dataclass with suggestions field
   - Add `GAMS_KEYWORDS` constant (Set, Scalar, Parameter, Variable, Equation, Model, Solve, etc.)
   - Reference: ERROR_MESSAGE_ENHANCEMENTS.md Section 3

2. **Suggestion Rules** (1-1.5 hours)
   - Implement 5 enhancement rules:
     - **Rule 1:** Keyword typo detection using `difflib.get_close_matches()`
       - "Scaler" → "Did you mean 'Scalar'?"
       - Cutoff: 0.6 similarity threshold
     - **Rule 2:** Set bracket error detection
       - Detect `[` in Set context → Suggest `/.../ not [...]`
     - **Rule 3:** Missing semicolon detection
       - Detect unexpected keyword on next line → Suggest adding `;`
     - **Rule 4:** Unsupported feature explanation
       - Pattern match "not supported" → Add roadmap reference
     - **Rule 5:** Function call error
       - Detect `Call(...)` in error → Explain literal-only limitation
   - Reference: ERROR_MESSAGE_ENHANCEMENTS.md Section 4

3. **Integration** (30 min)
   - Integrate `ErrorEnhancer` with `parse_text()` and `parse_file()`
   - Wrap all `ParseError` instances through `ErrorEnhancer`
   - Format enhanced errors for display
   - Ensure suggestions appear in error output

4. **Test Fixtures** (1 hour)
   - Create 5 test fixtures:
     - Keyword typo: `Scaler x;` → Suggest "Scalar"
     - Set bracket error: `Set i [1*10];` → Suggest `/1*10/`
     - Missing semicolon: Multi-line with missing `;`
     - Unsupported feature: `x(i) = 5;` → Explain Sprint 9
     - Function call: `size = uniform(1, 10);` → Explain literal limitation
   - Run tests and verify suggestions appear

**Deliverables:**
- `ErrorEnhancer` class with categorization in `errors.py`
- 5 enhancement rules implemented
- Integration with parse functions
- 5 test fixtures
- 80%+ errors get actionable suggestions

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `make test` passes
  - [ ] Keyword typos suggest correct spelling ✅
  - [ ] Punctuation errors show correct syntax ✅
  - [ ] Unsupported features explain roadmap ✅
  - [ ] 5 enhancement rules working
- [ ] Mark Day 6 as complete in `docs/planning/EPIC_2/SPRINT_8/PLAN.md`
- [ ] Check off Day 6 in `README.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 8 Day 6: Error Message Enhancements" \
                --body "Completes Day 6 tasks from Sprint 8 PLAN.md (lines 358-388)" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 358-388: Day 6 tasks)
- `docs/planning/EPIC_2/SPRINT_8/ERROR_MESSAGE_ENHANCEMENTS.md` (patterns, rules, categorization)
- `docs/planning/EPIC_2/SPRINT_8/PARSER_ERROR_LINE_NUMBERS.md` (ParseError integration)

---

## Day 7 Prompt: Partial Parse Metrics

**Branch:** Create a new branch named `sprint8-day7-partial-metrics` from `main`

**Objective:** Implement parse progress tracking and missing feature extraction

**Time Estimate:** 6 hours

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_8/PARTIAL_PARSE_METRICS.md` (Task 5) - Algorithms, line counting, feature extraction
- Review `docs/planning/EPIC_2/SPRINT_8/DASHBOARD_ENHANCEMENTS.md` (Task 9) - ModelResult schema
- Review `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 392-430: Day 7 tasks)

**Tasks to Complete (6 hours):**

1. **Line Counting Logic** (2 hours)
   - Implement `count_logical_lines(source)` function:
     - Count non-empty, non-comment lines
     - Handle multiline comments (`$ontext ... $offtext`)
     - Skip single-line comments (`*`)
   - Implement `count_logical_lines_up_to(source, line_number)` function:
     - Count lines before error line
     - Same multiline comment handling
   - Add tests for line counting edge cases
   - Reference: PARTIAL_PARSE_METRICS.md Section 3.1

2. **Missing Feature Extraction** (2 hours)
   - Implement `extract_missing_features(error, error_message)` function
   - Pattern match for 8 feature types:
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
   - Reference: PARTIAL_PARSE_METRICS.md Section 3.2

3. **Parse Progress Calculation** (1 hour)
   - Implement `calculate_parse_progress(model_path, error)` function:
     - Extract error line from exception
     - Count logical lines before error
     - Calculate percentage: (lines_parsed / total_lines) * 100
     - Handle semantic errors (100% parsed with error)
   - Add tests for progress calculation
   - Reference: PARTIAL_PARSE_METRICS.md Section 3.3

4. **Integration** (1 hour)
   - Enhance `ModelResult` dataclass with new fields:
     - `parse_progress_percentage: Optional[float]`
     - `parse_progress_lines_parsed: Optional[int]`
     - `parse_progress_lines_total: Optional[int]`
     - `missing_features: Optional[List[str]]`
   - Update ingestion script to call progress calculation
   - Add tests for ModelResult integration

**Deliverables:**
- Line counting functions (`count_logical_lines`, `count_logical_lines_up_to`)
- Missing feature extraction (8 patterns)
- Parse progress calculation
- `ModelResult` dataclass enhanced
- All tests passing

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `make test` passes
  - [ ] Line counting handles multiline comments ✅
  - [ ] Feature extraction covers 70-80% of GAMSLib errors ✅
  - [ ] Progress calculation accurate for all 10 models ✅
  - [ ] ModelResult dataclass enhanced
- [ ] Mark Day 7 as complete in `docs/planning/EPIC_2/SPRINT_8/PLAN.md`
- [ ] Check off Day 7 in `README.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 8 Day 7: Partial Parse Metrics" \
                --body "Completes Day 7 tasks from Sprint 8 PLAN.md (lines 392-430)" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 392-430: Day 7 tasks)
- `docs/planning/EPIC_2/SPRINT_8/PARTIAL_PARSE_METRICS.md` (algorithms, line counting, feature extraction)
- `docs/planning/EPIC_2/SPRINT_8/DASHBOARD_ENHANCEMENTS.md` (ModelResult schema)

---

## Day 8 Prompt: Dashboard Updates & Integration

**Branch:** Create a new branch named `sprint8-day8-dashboard` from `main`

**Objective:** Update dashboard template and ingestion script with partial parse metrics

**Time Estimate:** 4-5 hours

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_8/DASHBOARD_ENHANCEMENTS.md` (Task 9) - Template, ingestion script, color coding
- Review `docs/planning/EPIC_2/SPRINT_8/PARTIAL_PARSE_METRICS.md` (Task 5) - Progress calculation
- Review `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` (Task 2) - Validate unlock rates
- Review `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 434-475: Day 8 tasks)

**Tasks to Complete (4-5 hours):**

1. **Ingestion Script Updates** (1-1.5 hours)
   - Modify `scripts/ingest_gamslib_results.py` (or appropriate ingestion script)
   - Call `calculate_parse_progress()` for all models
   - Call `extract_missing_features()` for failures
   - Populate new `ModelResult` fields
   - Determine status symbol based on percentage:
     - 100% + no error → ✅ PASS
     - 100% + semantic error → 🟡 PARTIAL
     - 75-99% → 🟡 PARTIAL
     - 25-74% → ⚠️ PARTIAL
     - <25% → ❌ FAIL
   - Reference: DASHBOARD_ENHANCEMENTS.md Section 3

2. **Dashboard Template Modifications** (1-1.5 hours)
   - Update `GAMSLIB_CONVERSION_STATUS.md` template (or appropriate dashboard file)
   - Add new columns: Status, Progress, Missing Features
   - Remove or update old Parse column (replaced by Status + Progress)
   - Format progress: "92% (22/24)"
   - Format missing features: comma-separated, limit to 2
   - Add color-coded symbols: ✅ 🟡 ⚠️ ❌
   - Reference: DASHBOARD_ENHANCEMENTS.md Section 2

3. **Backward Compatibility Testing** (1 hour)
   - Test with Sprint 7 data (should default to 100% or 0%)
   - Verify old fields still work
   - Verify new columns render correctly
   - Test with Sprint 8 data (new metrics)
   - Ensure no breakage in existing tooling

4. **Integration Testing** (1 hour)
   - Run `make ingest-gamslib` with all 10 models
   - Verify dashboard shows expected metrics:
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

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `make ingest-gamslib` runs successfully ✅
  - [ ] Dashboard renders with new columns ✅
  - [ ] All 10 models show parse percentage ✅
  - [ ] Color coding matches thresholds ✅
  - [ ] Sprint 7 data backward compatible ✅
- [ ] Mark Day 8 as complete in `docs/planning/EPIC_2/SPRINT_8/PLAN.md`
- [ ] Check off Day 8 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] **Check off all Checkpoint 3 criteria in PLAN.md (lines 477-488)**

**CHECKPOINT 3: All Features Integrated**
- **Go Criteria:**
  - [ ] All features working together ✅
  - [ ] Dashboard displays partial metrics ✅
  - [ ] Parse rate ≥40% (4-5/10 models) ✅
  - [ ] All tests passing ✅
- **Go Decision:** Continue to final testing and documentation (Day 9)
- **No-Go Decision:** Defer test fixtures, focus on core functionality validation

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 8 Day 8: Dashboard Updates & Integration" \
                --body "Completes Day 8 tasks from Sprint 8 PLAN.md (lines 434-488). CHECKPOINT 3: All Features Integrated." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 434-488: Day 8 tasks + Checkpoint 3)
- `docs/planning/EPIC_2/SPRINT_8/DASHBOARD_ENHANCEMENTS.md` (template, ingestion script, color coding)
- `docs/planning/EPIC_2/SPRINT_8/PARTIAL_PARSE_METRICS.md` (progress calculation)
- `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` (validate unlock rates)

---

## Day 9 Prompt: Test Fixtures & Final Testing

**Branch:** Create a new branch named `sprint8-day9-testing` from `main`

**Objective:** Create remaining test fixtures, run comprehensive testing, verify all quality gates

**Time Estimate:** 4.5-5 hours

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md` (Task 8) - Partial parse fixtures, README template
- Review `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` (Task 2) - Validate final parse rate
- Review `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 492-527: Day 9 tasks)

**Tasks to Complete (4.5-5 hours):**

1. **Partial Parse Metric Fixtures** (1.5 hours)
   - Create `tests/fixtures/partial_parse/` directory
   - Create 3 GMS fixture files:
     - `01_himmel16_pattern.gms`: Partial parse ~80-92% (i++1 blocker)
     - `02_circle_pattern.gms`: Partial parse ~70-100% (function call blocker)
     - `03_complete_success.gms`: 100% parse baseline
   - Create `tests/fixtures/partial_parse/expected_results.yaml`
   - Create `tests/fixtures/partial_parse/README.md`
   - Reference: TEST_FIXTURE_STRATEGY.md Section 4

2. **Comprehensive Test Suite Run** (1 hour)
   - Run `make test` (all tests)
   - Run `make typecheck` (type checking)
   - Run `make lint` (linting)
   - Run `make format` (formatting check)
   - Fix any failures or warnings
   - Document test results

3. **GAMSLib Integration Testing** (1-1.5 hours)
   - Run `make ingest-gamslib` with all 10 models
   - Verify parse rate ≥40% (conservative) or ≥50% (optimistic)
   - Verify dashboard shows correct metrics for all models
   - Manually inspect ASTs for option and indexed assignment models
   - Capture final parse rate for Sprint 8
   - Document findings

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

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `make test` passes (100% of tests) ✅
  - [ ] `make typecheck` passes ✅
  - [ ] `make lint` passes ✅
  - [ ] `make format` passes ✅
  - [ ] Parse rate ≥40% (4/10 models minimum) ✅
  - [ ] No regressions in Sprint 7 models ✅
- [ ] Mark Day 9 as complete in `docs/planning/EPIC_2/SPRINT_8/PLAN.md`
- [ ] Check off Day 9 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] **Check off all Checkpoint 4 (FINAL) criteria in PLAN.md (lines 529-545)**

**FINAL CHECKPOINT: Sprint 8 Complete**
- **Go Criteria:**
  - [ ] Parse rate ≥40% (4/10 models minimum) ✅
  - [ ] All tests passing (100% pass rate) ✅
  - [ ] All quality gates passed ✅
  - [ ] Documentation updated ✅
- **Go Decision:** Create PR, mark Sprint 8 complete (Day 10)
- **No-Go Decision:** Document blockers, plan Sprint 8b with adjusted scope

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 8 Day 9: Test Fixtures & Final Testing" \
                --body "Completes Day 9 tasks from Sprint 8 PLAN.md (lines 492-545). FINAL CHECKPOINT: Sprint 8 Complete." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 492-545: Day 9 tasks + Final Checkpoint)
- `docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md` (partial parse fixtures, README template)
- `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` (validate final parse rate)

---

## Day 10 Prompt: Documentation, PR, & Sprint Closeout (BUFFER DAY)

**Branch:** Create a new branch named `sprint8-day10-closeout` from `main`

**Objective:** Complete documentation, create PR, prepare for Sprint 8 closeout

**Time Estimate:** 2.5 hours (BUFFER DAY - use for overruns from Days 1-9 if needed)

**⚠️ BUFFER DAY NOTE:** Day 10 is explicitly designated as a buffer day. If Days 1-9 overrun, use Day 10 hours to complete remaining work. If Days 1-9 complete on schedule, use Day 10 for documentation, PR creation, and closeout as detailed below.

**Prerequisites:**
- Review all Days 1-9 work completed
- Verify all checkpoints passed (Days 2, 4, 8, 9)
- Ensure parse rate ≥40% achieved
- Review `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 549-583: Day 10 tasks)

**Tasks to Complete (2.5 hours):**

1. **Documentation Updates** (1 hour)
   - Update `README.md` with Sprint 8 features (if applicable)
   - Update parser documentation with option and indexed assignment examples
   - Document known limitations:
     - Option statements: Mock/store only (no behavior)
     - Indexed assignments: Pre-solve only (no runtime evaluation)
     - Partial metrics: Line-based approximation (not true statement counting)
     - Create `docs/planning/EPIC_2/SPRINT_8/RETROSPECTIVE.md`
        - What went well
        - What could be improved
        - Lessons learned
        - Metrics vs goals
   - Add usage examples to docs

2. **CHANGELOG Update** (30 min)
   - Add Sprint 8 entry under `## [Unreleased]`
   - List all features implemented:
     - Option statements (limrow, limcol, decimals)
     - Indexed assignments (1D, 2D, variable attributes, expressions)
     - Error line numbers (100% coverage)
     - Error message enhancements (5 rules)
     - Partial parse metrics (line counting, feature extraction)
     - Dashboard enhancements (color coding, progress, missing features)
   - Document parse rate improvement (20% → 40-50%)
   - Note models unlocked (mhw4dx, mathopt1, trig)

3. **Create Pull Request** (30 min)
   - Create PR from `sprint8-execution` to `main` (or appropriate branch)
   - Title: "Sprint 8: High-ROI Parser Features & UX Enhancements"
   - Body: Summary of features, parse rate, testing coverage
   - Link to PLAN.md and all prep tasks
   - Request review from team/Copilot

4. **Sprint Closeout** (30 min)
   - Update Sprint 8 status in `docs/planning/EPIC_2/PROJECT_PLAN.md`
   - Archive Sprint 8 branch (if needed)
   - Prepare handoff notes for Sprint 9 (if applicable)
   - Capture lessons learned:
     - What worked well (prep phase, checkpoints, etc.)
     - What to improve (timing, scope, etc.)
     - Recommendations for Sprint 9

**Deliverables:**
- Documentation updated (README, parser docs)
- CHANGELOG.md updated with Sprint 8 entry
- PR created and ready for review
- Sprint retrospective complete
- Sprint 8 marked complete in PROJECT_PLAN.md

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Parse rate ≥40% (4/10 models) ✅
  - [ ] All tests passing ✅
  - [ ] Documentation complete ✅
  - [ ] PR ready for review ✅
  - [ ] All acceptance criteria met (PLAN.md Section 5)
- [ ] Retrospective complete
- [ ] Mark Day 10 as complete in `docs/planning/EPIC_2/SPRINT_8/PLAN.md`
- [ ] Check off Day 10 in `README.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 8 Day 10: Documentation & Sprint Closeout" \
                --body "Completes Day 10 tasks from Sprint 8 PLAN.md (lines 549-583). Sprint 8 is complete." \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (lines 549-583: Day 10 tasks)
- All Tasks 2-9 (comprehensive implementation)

---

## Usage Instructions

**For each day:**

1. **Start of day:**
   - Read the full prompt for that day
   - Review all prerequisite documents listed
   - Create the specified branch from `main`
   - Review tasks and time estimates
   - Prepare development environment

2. **During the day:**
   - Complete tasks in order listed
   - Track progress against time estimates
   - Run quality checks after each significant change
   - Document any blockers or unexpected issues
   - Adjust scope if needed (consult checkpoint criteria)

3. **End of day:**
   - Verify all deliverables complete
   - Run final quality checks:
     - `make typecheck`
     - `make lint`
     - `make format`
     - `make test`
   - Check off completion criteria
   - Update PLAN.md, README.md, and CHANGELOG.md
   - Create PR and request Copilot review
   - Address review comments
   - Merge once approved

4. **Quality checks reminder:**
   - ALWAYS run `make typecheck`, `make lint`, `make format`, `make test` before committing code changes
   - Skip quality checks only for documentation-only commits
   - Never commit code that breaks tests or type checking

5. **Checkpoint days (Days 2, 4, 8, 9):**
   - Complete checkpoint criteria checklist
   - Make Go/No-Go decision based on criteria
   - Document decision and rationale
   - Adjust scope if No-Go (see checkpoint contingency plans)

---

## Notes

- **Each prompt is self-contained:** You should be able to execute a day's work using only that prompt and the referenced documents
- **Prerequisites ensure context:** Always read prerequisite documents before starting work
- **Quality checks ensure code quality:** Never skip quality checks for code commits
- **Completion criteria provide clear "done":** Check all boxes before considering day complete
- **Line number references:** All prompts reference specific line numbers in PLAN.md for detailed task descriptions
- **PR & Review workflow:** Every day ends with a PR for thorough code review before merging
- **Checkpoints enable course correction:** Days 2, 4, 8, 9 have explicit Go/No-Go decisions
- **Buffer strategy:** Day 10 absorbs overruns from Days 1-9 without sprint failure

---

## Sprint 8 Summary

**Parse Rate Targets:**
- Baseline: 20% (2/10 models - Sprint 7)
- Conservative: 30% (3/10 models - option statements only)
- Primary: 40% (4/10 models - options + mathopt1)
- Stretch: 50% (5/10 models - options + mathopt1 + trig)

**Feature Breakdown:**
- **Days 1-2:** Option Statements (6-8h + 4-5h = 10-13h)
- **Days 3-4:** Indexed Assignments (5-7h + 4-6h = 9-13h)
- **Day 5:** Error Line Numbers (4-5h)
- **Day 6:** Error Enhancements (3-5h)
- **Day 7:** Partial Metrics (6h)
- **Day 8:** Dashboard Updates (4-5h)
- **Day 9:** Testing (4-5h)
- **Day 10:** Documentation & PR (2.5h - BUFFER)

**Total Effort:** 30-41 hours (average 35.5h)

**Checkpoints:**
- Checkpoint 1 (Day 2): Option statements complete, mhw4dx parses, 30% parse rate
- Checkpoint 2 (Day 4): Indexed assignments complete, mathopt1 parses, 40% parse rate
- Checkpoint 3 (Day 8): All features integrated, dashboard working
- Checkpoint 4 (Day 9): Final testing complete, ready for PR

**Success:** Sprint 8 is successful when parse rate ≥40% (4/10 models) with all tests passing and quality gates met.

---

**END OF SPRINT 8 DAY-BY-DAY PROMPTS**

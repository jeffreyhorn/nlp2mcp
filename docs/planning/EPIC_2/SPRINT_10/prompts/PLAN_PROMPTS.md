# Sprint 10 Day-by-Day Execution Prompts

This document contains comprehensive, self-contained prompts for executing each day of Sprint 10. Each prompt includes all necessary context, prerequisites, tasks, and completion criteria.

**Sprint 10 Goal:** Increase parse rate from 60% to 90% (6/10 → 9/10 GAMSLIB Tier 1 models)

**Target Models:**
- Day 1: himmel16.gms (90% → 100%)
- Days 2-3: mingamma.gms (65% → 100%)
- Days 4-6: circle.gms (70% → 95%)

**Deferred:** maxmin.gms (to Sprint 11)

---

## Table of Contents

- [Day 1: Variable Bound Index Bug Fix](#day-1-prompt-variable-bound-index-bug-fix)
- [Day 2: Comma-Separated Scalars (Part 1)](#day-2-prompt-comma-separated-scalars-part-1)
- [Day 3: Comma-Separated Scalars (Part 2)](#day-3-prompt-comma-separated-scalars-part-2)
- [Day 4: Function Calls in Assignments (Part 1)](#day-4-prompt-function-calls-in-assignments-part-1)
- [Day 5: Mid-Sprint Checkpoint + Function Calls (Part 2)](#day-5-prompt-mid-sprint-checkpoint--function-calls-part-2)
- [Day 6: Complete Function Calls + Unlock circle.gms](#day-6-prompt-complete-function-calls--unlock-circlegms)
- [Day 7: Integration Testing & Validation](#day-7-prompt-integration-testing--validation)
- [Day 8: Synthetic Test Validation](#day-8-prompt-synthetic-test-validation)
- [Day 9: Final Validation + Buffer](#day-9-prompt-final-validation--buffer)
- [Day 10: Sprint Completion & Retrospective](#day-10-prompt-sprint-completion--retrospective)

---

## Day 1 Prompt: Variable Bound Index Bug Fix

**Branch:** Create a new branch named `sprint10-day1-variable-bound-bug-fix` from `main`

**Objective:** Fix himmel16.gms variable bound index expansion bug to unlock the model (90% → 100% parse rate). This bug in `_expand_variable_indices` incorrectly expands literal indices like `"1"` to ALL domain members instead of treating them as literals.

**Parse Rate Impact:** 60% → 70% (6/10 → 7/10 models)

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/himmel16_analysis.md` - Complete blocker analysis for himmel16.gms
  - Section: "Secondary Blocker: Variable Bound Index Expansion Bug" (lines 400-500)
  - Root cause: `src/ir/parser.py` line 2125 in `_expand_variable_indices` function
  - Bug: Literal indices `"1"` incorrectly expanded to all domain members
- Review `docs/planning/EPIC_2/SPRINT_10/PREP_PLAN.md` - Task 3 (himmel16.gms analysis)
- Review `docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md` - Unknown 10.3.2 (Variable bound semantics)
- Check current himmel16.gms status: `tests/fixtures/gamslib/himmel16.gms` line 63

**Tasks to Complete (3-4 hours):**

**Morning (2 hours):**

1. **Reproduce and Diagnose Bug** (30 min)
   - Run himmel16.gms through parser to confirm failure
   - Verify line 63 fails: `x.up("1") = 100;`
   - Locate root cause in `src/ir/parser.py:2125` (`_expand_variable_indices` function)
   - Understand current behavior: literal `"1"` is being expanded to all domain members
   - Expected behavior: literal `"1"` should remain as-is

2. **Implement Fix** (1 hour)
   - Open `src/ir/parser.py` and navigate to `_expand_variable_indices` function (line ~2125)
   - Add literal index detection logic:
     - Check if `indices[0]` is a quoted string (literal)
     - If literal: return as-is without expansion
     - If variable/set reference: expand to domain members (existing behavior)
   - Code change: approximately 10-15 lines
   - Preserve existing behavior for variable/set indices

3. **Write Test Cases** (30 min)
   - Create new file: `tests/integration/test_variable_bound_literals.py`
   - Test case 1: Literal index - `x.up("1") = 100;` (should work)
   - Test case 2: Variable index - `x.up(i) = 100;` (existing behavior)
   - Test case 3: Mixed indices - `x.up("1", j) = 100;` (literal + variable)
   - Test case 4: Lower bound literal - `x.lo("1") = 0;`
   - Ensure all test patterns pass

**Afternoon (1-2 hours):**

4. **Run Quality Checks** (30 min)
   ```bash
   make typecheck && make lint && make format && make test
   ```
   - All checks must pass before proceeding
   - Fix any issues discovered

5. **Validate himmel16.gms** (30 min)
   - Run himmel16.gms through parser
   - Verify 100% parse success (70/70 lines)
   - Confirm line 63 now parses correctly
   - Check IR generation for variable bounds with literal indices
   - Run: `python scripts/measure_parse_rate.py --verbose`
   - Expected: himmel16.gms shows ✅ PASS

6. **Commit and Review** (30 min - 1 hour)
   - Commit with message: "Fix variable bound index expansion for literal indices"
   - Commit body should list:
     - Bug fixed in src/ir/parser.py:_expand_variable_indices
     - Test coverage added in tests/integration/test_variable_bound_literals.py
     - himmel16.gms now parses at 100% (70/70 lines)
     - Parse rate: 60% → 70% (6/10 → 7/10 models)
   - Self-review for edge cases
   - Update progress tracking

**Deliverables:**
- [ ] Bug fix implemented in `src/ir/parser.py` (_expand_variable_indices function)
- [ ] Test coverage added in `tests/integration/test_variable_bound_literals.py`
- [ ] himmel16.gms parses at 100% (70/70 lines validated)
- [ ] All quality checks pass (typecheck, lint, format, test)
- [ ] **Parse Rate: 60% → 70%** (7/10 models: himmel16 + 6 existing)

**Quality Checks:**
ALWAYS run these commands before committing:
```bash
make typecheck  # Must pass
make lint       # Must pass
make format     # Apply formatting
make test       # All tests must pass
```

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Bug fixed in `_expand_variable_indices` function
  - [ ] Literal indices (e.g., `"1"`) remain as-is
  - [ ] Variable/set indices still expand correctly (no regression)
  - [ ] himmel16.gms parses at 100% (70/70 lines)
  - [ ] Parse rate increased to 70% (7/10 models)
  - [ ] Comprehensive test coverage for literal/variable/mixed indices
  - [ ] All quality checks pass
  - [ ] No regressions in existing models
- [ ] Mark Day 1 as complete in `docs/planning/EPIC_2/SPRINT_10/PLAN.md`
- [ ] Update parse rate in README.md (if tracked)
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_10/CHANGELOG.md` or commit message

**Risks & Mitigation:**
- **Risk:** Fix breaks other variable bound patterns
- **Mitigation:** Comprehensive test suite covers literal/variable/mixed cases
- **Fallback:** Revert if regression detected, debug further on Day 2

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 10 Day 1: Fix Variable Bound Index Bug" \
                --body "Fixes variable bound index expansion bug in himmel16.gms (line 63).

   **Changes:**
   - Fixed _expand_variable_indices to handle literal indices
   - Added test coverage for literal/variable/mixed indices
   - himmel16.gms now parses at 100% (70/70 lines)

   **Parse Rate:** 60% → 70% (7/10 models)

   Completes Day 1 tasks from Sprint 10 PLAN.md" \
                --base main
   ```
2. Request a review (Copilot will auto-review)
3. Wait for review completion
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_10/PLAN.md` (lines 75-133) - Day 1 details
- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/himmel16_analysis.md` - Blocker analysis
- `docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md` - Unknown 10.3.2
- `src/ir/parser.py` (line ~2125) - `_expand_variable_indices` function
- `tests/fixtures/gamslib/himmel16.gms` (line 63) - Test case

---

## Day 2 Prompt: Comma-Separated Scalars (Part 1)

**Branch:** Create a new branch named `sprint10-day2-comma-separated-scalars-p1` from `main`

**Objective:** Implement grammar and semantic handler for comma-separated scalar declarations with optional inline values. This feature is needed to unlock mingamma.gms (lines 30-38).

**Parse Rate Impact:** No change yet (70% maintained), preparation for Day 3

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/mingamma_analysis.md` - Complete blocker analysis
  - Section: "Primary Blocker: Comma-Separated Scalar Declarations" (lines 200-300)
  - Pattern: `Scalar x1opt /1.46/, x1delta, y1opt /0.88/, y2opt;`
- Review `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/comma_separated_research.md` - Research findings
  - Implementation approach for comma-separated scalars
  - Grammar design recommendations
- Review `docs/planning/EPIC_2/SPRINT_10/PREP_PLAN.md` - Task 5 (mingamma.gms analysis), Task 6 (comma-separated research)
- Check current mingamma.gms status: `tests/fixtures/gamslib/mingamma.gms` lines 30-38

**Tasks to Complete (3-4 hours):**

**Morning (2 hours):**

1. **Update GAMS Grammar** (30 min)
   - Open `src/ir/gams_grammar.lark`
   - Locate existing `scalar_decl` rule
   - Add new `scalar_item` rule:
     ```lark
     scalar_item: IDENT ("/" scalar_value "/")?
     scalar_list: scalar_item ("," scalar_item)*
     ```
   - Modify `scalar_decl` to use `scalar_list` instead of single IDENT
   - Test grammar parses: `Scalar x1opt /1.46/, x1delta, y1opt /0.88/;`
   - Verify backward compatibility: single scalars still work

2. **Implement Semantic Handler** (1.5 hours)
   - Open `src/ir/parser.py`
   - Locate `visit_scalar_decl` method
   - Update to handle list of scalar_items:
     - Iterate through list of scalar items
     - For each item: extract name and optional value
     - Create ScalarDef for each scalar
     - Attach values if provided (inline `/value/` syntax)
     - Handle missing values (scalar without `/value/`)
   - Preserve existing behavior for single scalar declarations
   - Ensure backward compatibility

**Afternoon (1-2 hours):**

3. **Write Unit Tests** (1 hour)
   - Create new file: `tests/unit/test_scalar_declarations.py`
   - Test case 1: Single scalar without value - `Scalar x;`
   - Test case 2: Single scalar with value - `Scalar x /5/;`
   - Test case 3: Multiple scalars without values - `Scalar x, y, z;`
   - Test case 4: Multiple scalars all with values - `Scalar x /1/, y /2/;`
   - Test case 5: Mixed (some with, some without) - `Scalar x /1/, y, z /3/;`
   - Test case 6: mingamma.gms pattern - `Scalar x1opt /1.46/, x1delta, y1opt /0.88/, y2opt;`
   - Verify IR structure for each test case

4. **Run Quality Checks** (30 min - 1 hour)
   ```bash
   make typecheck && make lint && make format && make test
   ```
   - All checks must pass
   - Fix any type errors or linting issues

**Deliverables:**
- [ ] Grammar updated in `src/ir/gams_grammar.lark` to support comma-separated scalars
- [ ] Semantic handler in `src/ir/parser.py` processes scalar lists correctly
- [ ] Unit tests in `tests/unit/test_scalar_declarations.py` cover all patterns
- [ ] Quality checks pass (typecheck, lint, format, test)
- [ ] Backward compatibility maintained (single scalars still work)

**Quality Checks:**
ALWAYS run these commands before committing:
```bash
make typecheck  # Must pass
make lint       # Must pass
make format     # Apply formatting
make test       # All tests must pass
```

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Grammar supports comma-separated scalar lists
  - [ ] Grammar supports optional inline values (`/value/` syntax)
  - [ ] Semantic handler creates ScalarDef for each item in list
  - [ ] Values correctly attached when provided
  - [ ] Mixed patterns work (some with values, some without)
  - [ ] Backward compatibility: single scalars still parse
  - [ ] Unit tests cover all patterns
  - [ ] All quality checks pass
- [ ] Mark Day 2 as complete in `docs/planning/EPIC_2/SPRINT_10/PLAN.md`
- [ ] Log progress to commit message

**Risks & Mitigation:**
- **Risk:** Grammar change breaks existing scalar declarations
- **Mitigation:** Test suite includes backward compatibility tests
- **Fallback:** Keep old rule as alternative, add new rule separately
- **Risk:** Inline value parsing conflicts with other declarations
- **Mitigation:** Scalar-specific rule, doesn't affect Variable/Parameter
- **Fallback:** Implement simple comma list first, add values on Day 3

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 10 Day 2: Implement Comma-Separated Scalars (Part 1)" \
                --body "Implements grammar and semantic handler for comma-separated scalar declarations.

   **Changes:**
   - Updated GAMS grammar to support comma-separated scalars with optional inline values
   - Implemented semantic handler to process scalar lists
   - Added comprehensive unit tests for all patterns

   **Progress:** Preparation for unlocking mingamma.gms on Day 3

   Completes Day 2 tasks from Sprint 10 PLAN.md" \
                --base main
   ```
2. Request review and address comments
3. Merge when approved

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_10/PLAN.md` (lines 134-196) - Day 2 details
- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/mingamma_analysis.md` - Blocker analysis
- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/comma_separated_research.md` - Research findings
- `src/ir/gams_grammar.lark` - Grammar file
- `src/ir/parser.py` - Semantic handlers
- `tests/fixtures/gamslib/mingamma.gms` (lines 30-38) - Target pattern

---

## Day 3 Prompt: Comma-Separated Scalars (Part 2)

**Branch:** Create a new branch named `sprint10-day3-comma-separated-scalars-p2` from `main`

**Objective:** Complete comma-separated scalars implementation with integration testing and validation. Unlock mingamma.gms (65% → 100%).

**Parse Rate Impact:** 70% → 80% (7/10 → 8/10 models)

**Prerequisites:**
- Day 2 must be complete and merged
- Comma-separated scalar grammar and semantic handler already implemented
- Review `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/mingamma_analysis.md` - Validation section
- Review `tests/synthetic/comma_separated_scalars.gms` - Synthetic test from Task 9
- Check mingamma.gms: `tests/fixtures/gamslib/mingamma.gms` lines 30-38

**Tasks to Complete (2-3 hours):**

**Morning (1.5 hours):**

1. **Integration Testing** (30 min)
   - Test with real GAMS models
   - Verify existing models still parse correctly:
     - hs62.gms (should still pass)
     - mathopt1.gms (should still pass)
     - rbrock.gms (should still pass)
   - Test edge cases from grammar:
     - Empty comma-separated list (if applicable)
     - Trailing commas (should error or handle gracefully)
     - Very long comma-separated lists

2. **Validate mingamma.gms** (30 min)
   - Run mingamma.gms through parser
   - Verify lines 30-38 parse successfully:
     ```gams
     Scalar x1opt /1.46/, x1delta, y1opt /0.88/, y2opt;
     ```
   - Confirm 100% parse success (63/63 lines)
   - Check IR generation for all 4 scalars:
     - x1opt should have value 1.46
     - x1delta should have no value
     - y1opt should have value 0.88
     - y2opt should have no value
   - Run: `python scripts/measure_parse_rate.py --verbose`
   - Expected: mingamma.gms shows ✅ PASS

3. **Update Synthetic Test** (30 min)
   - Open `tests/synthetic/comma_separated_scalars.gms`
   - Verify test file exists (created in Task 9)
   - If needed, update test file to match implementation
   - Open `tests/synthetic/test_synthetic.py`
   - Update comma_separated_scalars test parameter:
     - Change `should_parse=False` to `should_parse=True`
     - Update sprint number if needed
   - Run synthetic test: `pytest tests/synthetic/test_synthetic.py::test_synthetic_feature[comma_separated_scalars.gms] -v`
   - Verify test passes

**Afternoon (0.5-1.5 hours):**

4. **Final Quality Checks** (30 min)
   ```bash
   make typecheck && make lint && make format && make test
   ```
   - All checks must pass
   - Run full test suite: `pytest tests/ -v`

5. **Commit and Documentation** (30 min - 1 hour)
   - Commit: "Implement comma-separated scalar declarations with inline values"
   - Commit body:
     - Integration tests pass
     - mingamma.gms unlocked (65% → 100%)
     - Synthetic test updated and passing
     - Parse rate: 70% → 80% (8/10 models)
   - Update progress tracking
   - Document feature in implementation notes (if applicable)

**Deliverables:**
- [ ] Full test coverage (unit + integration + synthetic)
- [ ] mingamma.gms parses at 100% (63/63 lines validated)
- [ ] All quality checks pass
- [ ] Feature documented
- [ ] **Parse Rate: 70% → 80%** (8/10 models: himmel16, mingamma, + 6 existing)
- [ ] Synthetic test updated to `should_parse=True`

**Quality Checks:**
ALWAYS run these commands before committing:
```bash
make typecheck  # Must pass
make lint       # Must pass
make format     # Apply formatting
make test       # All tests must pass
```

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Integration tests pass for all existing models (no regressions)
  - [ ] mingamma.gms parses at 100% (63/63 lines)
  - [ ] Lines 30-38 parse correctly with comma-separated scalars
  - [ ] IR correctly generated for all 4 scalars with proper values
  - [ ] Synthetic test passes (`comma_separated_scalars.gms`)
  - [ ] Parse rate increased to 80% (8/10 models)
  - [ ] All quality checks pass
  - [ ] Feature documented
- [ ] Mark Day 3 as complete in `docs/planning/EPIC_2/SPRINT_10/PLAN.md`
- [ ] Update parse rate in README.md
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_10/CHANGELOG.md`

**Milestone Achieved:**
**🎯 80% Parse Rate** (8/10 models: himmel16, mingamma, + 6 existing)

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 10 Day 3: Complete Comma-Separated Scalars + Unlock mingamma.gms" \
                --body "Completes comma-separated scalar implementation and unlocks mingamma.gms.

   **Changes:**
   - Integration testing complete (no regressions)
   - mingamma.gms now parses at 100% (63/63 lines)
   - Synthetic test updated and passing

   **Parse Rate:** 70% → 80% (8/10 models)

   Completes Day 3 tasks from Sprint 10 PLAN.md" \
                --base main
   ```
2. Request review and address comments
3. Merge when approved

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_10/PLAN.md` (lines 197-250) - Day 3 details
- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/mingamma_analysis.md` - Validation criteria
- `tests/fixtures/gamslib/mingamma.gms` (lines 30-38) - Target lines
- `tests/synthetic/comma_separated_scalars.gms` - Synthetic test
- `tests/synthetic/test_synthetic.py` - Test runner

---

## Day 4 Prompt: Function Calls in Assignments (Part 1)

**Branch:** Create a new branch named `sprint10-day4-function-calls-p1` from `main`

**Objective:** Add expressions field to parameters and enable function call storage in assignments. This prepares for unlocking circle.gms on Day 6.

**Parse Rate Impact:** No change yet (80% maintained), preparation for Days 5-6

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md` - Complete blocker analysis
  - Section: "Primary Blocker: Aggregation Function Calls" (lines 300-400)
  - Pattern: `xmin = smin(i, x(i));`
- Read `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/function_call_research.md` - Research findings
  - **CRITICAL:** Infrastructure already exists! (func_call grammar rule, Call AST node)
  - Parse-only approach (no evaluation engine needed)
- Review `docs/planning/EPIC_2/SPRINT_10/PREP_PLAN.md` - Task 2 (circle.gms analysis), Task 7 (function call research)
- Check current state:
  - `src/ir/gams_grammar.lark` line 315 - Verify `func_call` rule exists
  - `src/ir/ast.py` line 170 - Verify `Call` AST node exists
  - `tests/fixtures/gamslib/circle.gms` lines 40-43, 48 - Target patterns

**Tasks to Complete (2-3 hours):**

**Morning (1.5-2 hours):**

1. **Add expressions Field to AST** (30 min)
   - Open `src/ir/ast.py`
   - Locate `ParameterDef` dataclass
   - Add new field:
     ```python
     @dataclass
     class ParameterDef:
         name: str
         domain: Optional[List[str]] = None
         values: Optional[Dict] = None
         expressions: Optional[Dict[str, Expr]] = None  # NEW FIELD
     ```
   - Update `__post_init__` if needed to handle new field
   - Ensure field is optional (backward compatible)

2. **Update Grammar** (15 min, if needed)
   - Open `src/ir/gams_grammar.lark`
   - Verify `func_call` rule exists (should be around line 315) ✅
   - Check FUNCNAME token (should be around line 438) ✅
   - Add missing functions to FUNCNAME if needed:
     - round, mod, ceil (if not already present)
   - Note: Most grammar work already done, just verify

3. **Implement Semantic Handler** (1-1.5 hours)
   - Open `src/ir/parser.py`
   - Locate parameter assignment processing
   - Update to detect function calls in RHS (right-hand side):
     - Check if RHS contains `func_call` node
     - If yes: store as Call AST node in `expressions` field
     - If no: handle normally (existing behavior)
   - **Important:** Do NOT evaluate function calls, just store structure
   - Store mapping: parameter_name → Call expression
   - Preserve existing behavior for simple value assignments

**Afternoon (0.5-1 hour):**

4. **Write Unit Tests** (30 min - 1 hour)
   - Create new file: `tests/unit/test_function_call_assignments.py`
   - Test case 1: Aggregation function
     ```gams
     Parameter x; x = smin(i, a(i));
     ```
   - Test case 2: Mathematical function
     ```gams
     Parameter d; d = sqrt(sqr(x) + sqr(y));
     ```
   - Test case 3: Nested function calls
     ```gams
     Parameter z; z = sqrt(smin(i, sqr(x(i))));
     ```
   - Test case 4: Simple value assignment (no function, ensure backward compatibility)
     ```gams
     Parameter p; p = 5;
     ```
   - Verify `expressions` field populated correctly
   - Verify Call AST node structure

**Deliverables:**
- [ ] `ParameterDef.expressions` field added to `src/ir/ast.py`
- [ ] Semantic handler in `src/ir/parser.py` detects and stores function calls
- [ ] Function calls stored as Call AST nodes (not evaluated)
- [ ] Unit tests pass in `tests/unit/test_function_call_assignments.py`
- [ ] Backward compatibility maintained (simple assignments still work)
- [ ] No evaluation engine (parse-only approach confirmed)

**Quality Checks:**
ALWAYS run these commands before committing:
```bash
make typecheck  # Must pass
make lint       # Must pass
make format     # Apply formatting
make test       # All tests must pass
```

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `expressions` field added to ParameterDef
  - [ ] Field is optional (backward compatible)
  - [ ] Function calls detected in parameter assignments
  - [ ] Call AST nodes created and stored in `expressions` field
  - [ ] No evaluation performed (parse-only)
  - [ ] Unit tests cover aggregation, mathematical, and nested patterns
  - [ ] Backward compatibility: simple assignments still work
  - [ ] All quality checks pass
- [ ] Mark Day 4 as complete in `docs/planning/EPIC_2/SPRINT_10/PLAN.md`
- [ ] Log progress to commit message

**Risks & Mitigation:**
- **Risk:** Breaking existing parameter processing
- **Mitigation:** `expressions` field is optional, backward compatible
- **Fallback:** Make field optional, only populate for function calls

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 10 Day 4: Add Function Call Storage in Assignments (Part 1)" \
                --body "Adds expressions field to ParameterDef and implements function call storage.

   **Changes:**
   - Added expressions field to ParameterDef for storing function call AST nodes
   - Implemented semantic handler to detect and store function calls (parse-only)
   - Added unit tests for aggregation, mathematical, and nested function calls

   **Progress:** Preparation for unlocking circle.gms on Day 6

   Completes Day 4 tasks from Sprint 10 PLAN.md" \
                --base main
   ```
2. Request review and address comments
3. Merge when approved

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_10/PLAN.md` (lines 251-309) - Day 4 details
- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md` - Blocker analysis
- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/function_call_research.md` - **CRITICAL: Read for existing infrastructure**
- `src/ir/ast.py` (line ~170) - Call AST node definition
- `src/ir/gams_grammar.lark` (line ~315) - func_call grammar rule
- `tests/fixtures/gamslib/circle.gms` (lines 40-43, 48) - Target patterns

---

## Day 5 Prompt: Mid-Sprint Checkpoint + Function Calls (Part 2)

**Branch:** Create a new branch named `sprint10-day5-checkpoint-and-function-calls` from `main`

**Objective:** Execute mid-sprint checkpoint to validate progress at Day 5, then complete function call implementation. Expected checkpoint result: 80% parse rate (8/10 models) = ON TRACK.

**Parse Rate Impact:** Maintain 80% at checkpoint, then no change yet (preparation for Day 6)

**Prerequisites:**
- Days 1-4 must be complete and merged
- Review `docs/planning/EPIC_2/SPRINT_10/CHECKPOINT.md` - **FULL checkpoint guide**
  - How to run checkpoint (section: "How to Run")
  - How to interpret results (section: "Interpreting Results")
  - Decision framework (section: "Decision Framework")
  - Contingency plans (section: "Action Options")
- Review `docs/planning/EPIC_2/SPRINT_10/PLAN.md` - Checkpoint section
- Checkpoint infrastructure from Task 11:
  - `scripts/measure_parse_rate.py` - Parse rate measurement script
  - `scripts/sprint10_checkpoint.sh` - Checkpoint validation script

**Tasks to Complete (2-4 hours: 1-2h checkpoint + 1-2h function calls):**

**Morning (1-2 hours): Checkpoint**

1. **Run Checkpoint Script** (15 min)
   ```bash
   ./scripts/sprint10_checkpoint.sh
   ```
   - Script will measure current parse rate
   - Compare to Day 5 target (70% minimum expected)
   - Provide status: ON TRACK or BEHIND SCHEDULE

2. **Analyze Results** (15 min)
   - **Expected Result:**
     ```
     Parse Rate: 8/10 models (80.0%)
     ✅ STATUS: ON TRACK
     ```
   - Passing models: himmel16, mingamma, + 6 existing (8 total)
   - Failing models: circle (function calls not done), maxmin (deferred)
   - Status interpretation: **ON TRACK** (≥ 70% target met, actually at 80%)

3. **Validate Feature Quality** (30 min)
   - Run synthetic tests:
     ```bash
     pytest tests/synthetic/ -v
     ```
   - Verify himmel16 and mingamma features work in isolation:
     - `test_synthetic_feature[i_plusplus_indexing.gms]` should pass (Sprint 9)
     - `test_synthetic_feature[comma_separated_scalars.gms]` should pass (Sprint 10)
   - Check for any regressions in existing models
   - Run full test suite: `make test`

4. **Decision Point** (15 min - 1 hour)

   **Expected Scenario: ON TRACK (80% parse rate)**
   - ✅ Parse rate exceeds Day 5 target (80% vs. 70% minimum)
   - ✅ Continue with function calls implementation (Tasks 5-6)
   - ✅ Stay on schedule for 90% target by Day 6
   - Document checkpoint success in commit message

   **If BEHIND SCHEDULE (<70%, unexpected):**
   - ⚠️ Analyze root cause:
     - Why are implemented features not working?
     - Are there bugs in Day 1-3 implementations?
   - ⚠️ Run synthetic tests to isolate issues
   - ⚠️ Choose mitigation (see CHECKPOINT.md):
     - **Option A:** Debug issues (if quick fix, <2 hours)
     - **Option B:** Defer circle.gms, target 80% instead of 90%
     - **Option C:** Extend schedule, reduce buffer time
   - Document decision and rationale in `docs/planning/EPIC_2/SPRINT_10/SPRINT_LOG.md`

**Afternoon (1-2 hours): Function Calls Completion**

5. **Complete Function Call Tests** (1 hour)
   - Add integration tests for function calls
   - Test with actual circle.gms patterns:
     - Aggregation: `xmin = smin(i, x(i));`
     - Mathematical: `d.l = sqrt(sqr(a.l - xmin) + sqr(b.l - ymin));`
   - Verify function calls detected and stored correctly
   - Test edge cases:
     - Nested function calls
     - Function calls with multiple arguments
     - Mixed parameters (some with functions, some without)

6. **Quality Checks** (30 min - 1 hour)
   ```bash
   make typecheck && make lint && make format && make test
   ```
   - All checks must pass
   - Fix any issues discovered

**Deliverables:**
- [ ] **Checkpoint completed and documented**
- [ ] **Decision made and recorded** (expected: continue as planned)
- [ ] Checkpoint results logged (expected: 80% ON TRACK)
- [ ] Function call tests complete
- [ ] Quality checks pass
- [ ] **Parse Rate validated: 80% (8/10 models)**

**Quality Checks:**
ALWAYS run these commands before committing:
```bash
make typecheck  # Must pass
make lint       # Must pass
make format     # Apply formatting
make test       # All tests must pass
```

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Checkpoint executed successfully
  - [ ] Parse rate measured: 80% (8/10 models) ✅
  - [ ] Status determined: ON TRACK (expected)
  - [ ] Decision documented
  - [ ] Function call tests complete
  - [ ] Integration tests cover circle.gms patterns
  - [ ] All quality checks pass
  - [ ] Synthetic tests for Sprint 9 and Sprint 10 features passing
- [ ] Mark Day 5 as complete in `docs/planning/EPIC_2/SPRINT_10/PLAN.md`
- [ ] Check off Checkpoint criteria in `docs/planning/EPIC_2/SPRINT_10/CHECKPOINT.md` (if applicable)
- [ ] Log checkpoint results to `docs/planning/EPIC_2/SPRINT_10/SPRINT_LOG.md` or commit message

**Checkpoint Decision Matrix:**

| Current Rate | Status | Action |
|--------------|--------|--------|
| ≥ 80% | Ahead of Schedule | Continue as planned, consider stretch goals |
| 70-79% | On Track | Continue as planned |
| 60-69% | Behind Schedule | Analyze and mitigate (see CHECKPOINT.md) |
| < 60% | Significantly Behind | Emergency pivot (likely defer circle.gms) |

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 10 Day 5: Mid-Sprint Checkpoint + Function Calls (Part 2)" \
                --body "Executes Day 5 checkpoint and completes function call implementation.

   **Checkpoint Results:**
   - Parse Rate: 80% (8/10 models)
   - Status: ON TRACK ✅
   - Decision: Continue with function calls implementation

   **Changes:**
   - Completed checkpoint validation
   - Added function call integration tests
   - Verified all Sprint 9 and Sprint 10 features in isolation

   Completes Day 5 tasks from Sprint 10 PLAN.md" \
                --base main
   ```
2. Request review and address comments
3. Merge when approved

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_10/PLAN.md` (lines 310-389) - Day 5 details
- `docs/planning/EPIC_2/SPRINT_10/CHECKPOINT.md` - **FULL checkpoint guide**
- `scripts/sprint10_checkpoint.sh` - Checkpoint script
- `scripts/measure_parse_rate.py` - Parse rate measurement
- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md` - For function call patterns

---

## Day 6 Prompt: Complete Function Calls + Unlock circle.gms

**Branch:** Create a new branch named `sprint10-day6-unlock-circle` from `main`

**Objective:** Finish function calls implementation and unlock circle.gms (70% → 95%). Achieve Sprint 10 goal of 90% parse rate (9/10 models).

**Parse Rate Impact:** 80% → 90% (8/10 → 9/10 models) ✅ **SPRINT GOAL ACHIEVED**

**Prerequisites:**
- Days 1-5 must be complete and merged
- Function call infrastructure already implemented (Days 4-5)
- Review `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md` - Validation section
- Check circle.gms status: `tests/fixtures/gamslib/circle.gms`
  - Lines 40-43: Aggregation functions (smin, smax)
  - Line 48: Mathematical functions (sqrt, sqr)
  - Lines 54-56: Conditional abort (DEFERRED to Sprint 11)

**Tasks to Complete (1-2 hours):**

**Morning (1-2 hours):**

1. **Validate circle.gms** (30 min)
   - Run circle.gms through parser
   - Verify lines 40-43 parse (aggregation functions):
     ```gams
     xmin = smin(i, x(i));
     xmax = smax(i, x(i));
     ymin = smin(i, y(i));
     ymax = smax(i, y(i));
     ```
   - Verify line 48 parses (mathematical functions):
     ```gams
     d.l = sqrt(sqr(a.l - xmin) + sqr(b.l - ymin));
     ```
   - Confirm 95% parse success (53/56 lines)
   - Note: Lines 54-56 (conditional abort with compile-time variables) DEFERRED to Sprint 11
   - Run: `python scripts/measure_parse_rate.py --verbose`
   - Expected: circle.gms shows ✅ PASS (53/56 lines, 95%)

2. **Add/Update Synthetic Tests** (30 min)
   - Verify `tests/synthetic/function_calls_parameters.gms` exists (from Task 9)
   - Verify `tests/synthetic/aggregation_functions.gms` exists (from Task 9)
   - Open `tests/synthetic/test_synthetic.py`
   - Update test parameters for function call tests:
     - Change `should_parse=False` to `should_parse=True`
     - Update sprint numbers if needed
   - Run synthetic tests:
     ```bash
     pytest tests/synthetic/test_synthetic.py::test_synthetic_feature[function_calls_parameters.gms] -v
     pytest tests/synthetic/test_synthetic.py::test_synthetic_feature[aggregation_functions.gms] -v
     ```
   - Verify both tests pass

3. **Final Validation and Commit** (30 min)
   - Run full test suite:
     ```bash
     make test
     ```
   - Verify all 9 target models parse:
     - circle (95%), himmel16 (100%), mingamma (100%)
     - hs62, mathopt1, mhw4d, mhw4dx, rbrock, trig (100%)
   - Run parse rate measurement:
     ```bash
     python scripts/measure_parse_rate.py --verbose
     ```
   - Expected output:
     ```
     Parse Rate: 9/10 models (90.0%) ✅
     
     Passing: circle, himmel16, hs62, mathopt1, mingamma, mhw4d, mhw4dx, rbrock, trig
     Failing: maxmin (deferred to Sprint 11)
     ```
   - Commit: "Implement function calls in parameter assignments (parse-only)"
   - Commit body:
     - Function calls in assignments now supported (parse-only)
     - circle.gms unlocked (70% → 95%, 53/56 lines)
     - Synthetic tests updated and passing
     - Parse rate: 80% → 90% (9/10 models)
     - **SPRINT 10 GOAL ACHIEVED ✅**

**Deliverables:**
- [ ] circle.gms parses at 95% (53/56 lines validated)
- [ ] Lines 40-43 parse (aggregation: smin/smax)
- [ ] Line 48 parses (mathematical: sqrt/sqr)
- [ ] Synthetic tests pass (`function_calls_parameters.gms`, `aggregation_functions.gms`)
- [ ] All quality checks pass
- [ ] **Parse Rate: 80% → 90%** (9/10 models) ✅ **SPRINT GOAL ACHIEVED**

**Quality Checks:**
ALWAYS run these commands before committing:
```bash
make typecheck  # Must pass
make lint       # Must pass
make format     # Apply formatting
make test       # All tests must pass
```

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] circle.gms parses at 95% (53/56 lines)
  - [ ] Aggregation functions work (smin, smax in lines 40-43)
  - [ ] Mathematical functions work (sqrt, sqr in line 48)
  - [ ] Synthetic tests updated to `should_parse=True` and passing
  - [ ] Parse rate increased to 90% (9/10 models)
  - [ ] All quality checks pass
  - [ ] No regressions in existing models
  - [ ] **SPRINT 10 GOAL ACHIEVED: 90% parse rate**
- [ ] Mark Day 6 as complete in `docs/planning/EPIC_2/SPRINT_10/PLAN.md`
- [ ] Update parse rate in README.md to 90%
- [ ] Log milestone achievement to `docs/planning/EPIC_2/SPRINT_10/CHANGELOG.md`

**Milestone Achieved:**
**🎉 SPRINT 10 GOAL: 90% Parse Rate** (9/10 models: circle, himmel16, mingamma, + 6 existing)

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 10 Day 6: Complete Function Calls + Unlock circle.gms" \
                --body "Completes function calls implementation and unlocks circle.gms.

   **Changes:**
   - circle.gms now parses at 95% (53/56 lines)
   - Aggregation functions (smin/smax) working
   - Mathematical functions (sqrt/sqr) working
   - Synthetic tests updated and passing

   **Parse Rate:** 80% → 90% (9/10 models) ✅

   🎉 **SPRINT 10 GOAL ACHIEVED: 90% parse rate**

   Completes Day 6 tasks from Sprint 10 PLAN.md" \
                --base main
   ```
2. Request review and address comments
3. Merge when approved

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_10/PLAN.md` (lines 390-438) - Day 6 details
- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md` - Validation criteria
- `tests/fixtures/gamslib/circle.gms` (lines 40-43, 48) - Target lines
- `tests/synthetic/function_calls_parameters.gms` - Synthetic test
- `tests/synthetic/aggregation_functions.gms` - Synthetic test

---

## Day 7 Prompt: Integration Testing & Validation

**Branch:** Create a new branch named `sprint10-day7-integration-testing` from `main`

**Objective:** Comprehensive testing of all 3 new features (variable bound bug fix, comma-separated scalars, function calls) to ensure no regressions and validate all 9 target models.

**Parse Rate Impact:** Maintain 90% (9/10 models)

**Prerequisites:**
- Days 1-6 must be complete and merged
- Sprint 10 goal achieved (90% parse rate)
- All 3 target models unlocked:
  - himmel16.gms (100%)
  - mingamma.gms (100%)
  - circle.gms (95%)

**Tasks to Complete (2-3 hours):**

**Full Day (2-3 hours):**

1. **Run Full Test Suite** (30 min)
   ```bash
   pytest tests/ -v --cov=src/ir
   ```
   - Verify 100% of tests pass
   - Check code coverage for new code:
     - Variable bound index fix
     - Comma-separated scalars
     - Function calls in assignments
   - Review any warnings or deprecations
   - Target: All tests passing, no regressions

2. **Test All 10 GAMSLIB Tier 1 Models** (30 min)
   ```bash
   python scripts/measure_parse_rate.py --verbose
   ```
   - Expected Results:
     ```
     Testing GAMSLIB Tier 1 models...
     ============================================================
     ✅ PASS  circle.gms      (95%, 53/56 lines)
     ✅ PASS  himmel16.gms    (100%, 70/70 lines)
     ✅ PASS  hs62.gms        (100%)
     ✅ PASS  mathopt1.gms    (100%)
     ❌ FAIL  maxmin.gms      (18%, deferred to Sprint 11)
     ✅ PASS  mhw4d.gms       (100%)
     ✅ PASS  mhw4dx.gms      (100%)
     ✅ PASS  mingamma.gms    (100%, 63/63 lines)
     ✅ PASS  rbrock.gms      (100%)
     ✅ PASS  trig.gms        (100%)
     ============================================================
     Parse Rate: 9/10 models (90.0%) ✅
     ```
   - Verify all 9 target models pass
   - Confirm maxmin.gms still fails (expected, deferred to Sprint 11)

3. **Regression Testing** (30 min - 1 hour)
   - Test existing passing models (6 baseline models):
     - hs62.gms, mathopt1.gms, mhw4d.gms, mhw4dx.gms, rbrock.gms, trig.gms
     - Verify all still parse at 100%
     - Check for any performance degradation
   - Run synthetic tests for Sprint 9 features:
     ```bash
     pytest tests/synthetic/test_synthetic.py::test_synthetic_feature[i_plusplus_indexing.gms] -v
     pytest tests/synthetic/test_synthetic.py::test_synthetic_feature[equation_attributes.gms] -v
     pytest tests/synthetic/test_synthetic.py::test_synthetic_feature[model_sections.gms] -v
     ```
   - Confirm Sprint 9 features still work (i++1, equation attributes, model sections)
   - Verify no performance degradation in parse times

4. **Edge Case Testing** (30 min)
   - Test malformed inputs:
     - Invalid comma-separated syntax
     - Invalid function call syntax
     - Invalid variable bound syntax
   - Test boundary conditions:
     - Empty comma-separated lists
     - Very long function call chains
     - Edge cases in variable bounds
   - Verify error messages are helpful
   - Test parser recovery from errors

5. **Documentation and Commit** (30 min)
   - Update feature documentation (if applicable)
   - Document any known limitations:
     - circle.gms at 95% (lines 54-56 deferred)
     - Function calls are parse-only (no evaluation)
   - Commit: "Integration testing for Sprint 10 features"
   - Commit body:
     - All 9 target models validated
     - No regressions in existing models
     - Sprint 9 features still working
     - Edge cases handled gracefully
     - 90% parse rate confirmed

**Deliverables:**
- [ ] Full test suite passes (100%)
- [ ] All 9 target models parse successfully
- [ ] No regressions in existing models (6 baseline models)
- [ ] Sprint 9 features validated (i++1, equation attributes, model sections)
- [ ] Edge cases handled gracefully
- [ ] Documentation updated
- [ ] **Parse Rate confirmed: 90% (9/10 models)**

**Quality Checks:**
```bash
make typecheck  # Must pass
make lint       # Must pass
make format     # Apply formatting
make test       # All tests must pass (critical for this day)
```

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Full test suite passes (100%, no failures)
  - [ ] All 9 target models parse correctly
  - [ ] No regressions in 6 baseline models
  - [ ] Sprint 9 features still work (i++1, equation attributes, model sections)
  - [ ] Edge cases tested and handled
  - [ ] Error messages are helpful
  - [ ] No performance degradation
  - [ ] Code coverage adequate for new features
  - [ ] Documentation updated with known limitations
- [ ] Mark Day 7 as complete in `docs/planning/EPIC_2/SPRINT_10/PLAN.md`
- [ ] Log validation results to commit message

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 10 Day 7: Integration Testing & Validation" \
                --body "Comprehensive integration testing for all Sprint 10 features.

   **Validation Results:**
   - Full test suite: 100% passing
   - All 9 target models validated
   - No regressions in existing models
   - Sprint 9 features still working
   - Edge cases handled gracefully

   **Parse Rate:** 90% (9/10 models) confirmed ✅

   Completes Day 7 tasks from Sprint 10 PLAN.md" \
                --base main
   ```
2. Request review and address comments
3. Merge when approved

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_10/PLAN.md` (lines 439-503) - Day 7 details
- `scripts/measure_parse_rate.py` - Parse rate measurement
- `tests/synthetic/test_synthetic.py` - Synthetic tests

---

## Day 8 Prompt: Synthetic Test Validation

**Branch:** Create a new branch named `sprint10-day8-synthetic-tests` from `main`

**Objective:** Validate all Sprint 10 features work in isolation using the synthetic test framework. Ensure each feature passes synthetic tests independently of complex model interactions.

**Parse Rate Impact:** Maintain 90% (9/10 models)

**Prerequisites:**
- Days 1-7 must be complete and merged
- Review `docs/planning/EPIC_2/SPRINT_10/PREP_PLAN.md` - Task 9 (Synthetic Test Framework design)
- Review `tests/synthetic/README.md` - Synthetic test framework documentation
- Sprint 10 synthetic tests should exist:
  - `tests/synthetic/comma_separated_scalars.gms` (from Task 9)
  - `tests/synthetic/function_calls_parameters.gms` (from Task 9)
  - `tests/synthetic/aggregation_functions.gms` (from Task 9)

**Tasks to Complete (3-4 hours):**

**Morning (2 hours):**

1. **Run All Synthetic Tests** (30 min)
   ```bash
   pytest tests/synthetic/test_synthetic.py -v
   ```
   - **Expected to PASS:**
     - **Sprint 9:** i_plusplus_indexing.gms, equation_attributes.gms, model_sections.gms
     - **Sprint 10:** comma_separated_scalars.gms, function_calls_parameters.gms, aggregation_functions.gms
     - **Existing:** comma_separated_variables.gms, abort_in_if_blocks.gms
   - **Expected to SKIP:**
     - **Sprint 11+:** nested_function_calls.gms, variable_level_bounds.gms, mixed_variable_bounds.gms, nested_subset_indexing.gms
   - Verify all expected tests pass
   - Document any unexpected failures

2. **Create Additional Synthetic Tests** (1 hour)
   - Create edge case tests for Sprint 10 features:
     - **Variable Bound Literals:**
       - Create `tests/synthetic/variable_bound_literals.gms`
       - Test literal indices: `x.up("1") = 100;`
       - Test mixed indices: `x.up("1", i) = 100;`
     - **Mixed Comma-Separated Scalars:**
       - Update `comma_separated_scalars.gms` if needed
       - Test edge case: all scalars without values
       - Test edge case: all scalars with values
     - **Combined Features:**
       - Create `tests/synthetic/combined_features.gms`
       - Test function call with i++1 indexing
       - Test comma-separated with equation attributes
   - Add tests to `test_synthetic.py` with `should_parse=False` or `True` as appropriate

3. **Verify IR Generation** (30 min)
   - For each passing synthetic test, verify IR structure:
     - Variable bound literals test: Check variable bounds stored correctly
     - Comma-separated scalars test: Check all ScalarDef nodes created
     - Function calls test: Check Call AST nodes in expressions field
   - Use parser directly to inspect IR:
     ```python
     from src.ir.parser import parse_model_file
     result = parse_model_file("tests/synthetic/[test].gms")
     # Inspect result structure
     ```

**Afternoon (1-2 hours):**

4. **Update Synthetic Test Documentation** (30 min)
   - Open `tests/synthetic/README.md`
   - Document new Sprint 10 tests:
     - comma_separated_scalars.gms
     - function_calls_parameters.gms
     - aggregation_functions.gms
     - variable_bound_literals.gms (if created)
   - Update feature coverage matrix:
     - Sprint 9: 3 features (i++1, equation attributes, model sections)
     - Sprint 10: 3 features (variable bound bug, comma-separated, function calls)
   - Document expected pass/skip status for each test

5. **Run Synthetic Tests in Isolation** (30 min)
   - Ensure tests don't depend on each other
   - Run each test independently:
     ```bash
     pytest tests/synthetic/test_synthetic.py::test_synthetic_feature[comma_separated_scalars.gms] -v
     pytest tests/synthetic/test_synthetic.py::test_synthetic_feature[function_calls_parameters.gms] -v
     # etc.
     ```
   - Verify each test can run independently
   - Check test execution time (should be <1s each)
   - Target: All tests run in <10s total

6. **Quality Check and Commit** (30 min - 1 hour)
   ```bash
   make typecheck && make lint && make format && make test
   ```
   - Commit: "Add Sprint 10 synthetic tests and validation"
   - Commit body:
     - All Sprint 10 synthetic tests passing
     - Additional edge case tests added
     - IR generation verified for all features
     - Synthetic test documentation updated
     - All tests run in <1s each

**Deliverables:**
- [ ] All Sprint 10 synthetic tests pass
- [ ] Additional edge case tests added (if applicable)
- [ ] IR generation verified for all features
- [ ] Synthetic test documentation updated in `tests/synthetic/README.md`
- [ ] Tests run independently (<1s each)
- [ ] Feature coverage matrix updated

**Quality Checks:**
```bash
make typecheck  # Must pass
make lint       # Must pass
make format     # Apply formatting
make test       # All tests must pass
```

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] All Sprint 9 synthetic tests still pass
  - [ ] All Sprint 10 synthetic tests pass
  - [ ] Edge case tests added and passing
  - [ ] IR structure verified for each feature
  - [ ] Tests run independently (no dependencies)
  - [ ] Test execution time <1s per test
  - [ ] Documentation updated with Sprint 10 tests
  - [ ] Feature coverage matrix complete
- [ ] Mark Day 8 as complete in `docs/planning/EPIC_2/SPRINT_10/PLAN.md`
- [ ] Log synthetic test results to commit message

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 10 Day 8: Synthetic Test Validation" \
                --body "Validates all Sprint 10 features in isolation using synthetic tests.

   **Validation Results:**
   - All Sprint 9 synthetic tests passing
   - All Sprint 10 synthetic tests passing
   - Additional edge case tests added
   - IR generation verified
   - Documentation updated

   Completes Day 8 tasks from Sprint 10 PLAN.md" \
                --base main
   ```
2. Request review and address comments
3. Merge when approved

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_10/PLAN.md` (lines 504-564) - Day 8 details
- `docs/planning/EPIC_2/SPRINT_10/PREP_PLAN.md` - Task 9 (Synthetic test framework)
- `tests/synthetic/README.md` - Framework documentation
- `tests/synthetic/test_synthetic.py` - Test runner

---

## Day 9 Prompt: Final Validation + Buffer

**Branch:** Create a new branch named `sprint10-day9-final-validation` from `main`

**Objective:** Final comprehensive validation of all Sprint 10 work, bug fixes if needed, and buffer time for any unknowns. Confirm 90% parse rate is stable.

**Parse Rate Impact:** Maintain 90% (9/10 models)

**Prerequisites:**
- Days 1-8 must be complete and merged
- All Sprint 10 features implemented and tested
- Sprint 10 goal achieved (90% parse rate)

**Tasks to Complete (2-4 hours - flexible buffer time):**

**Morning (1-2 hours):**

1. **Run Full Quality Checks** (30 min)
   ```bash
   make typecheck && make lint && make format && make test
   python scripts/measure_parse_rate.py --verbose
   ```
   - Verify 90% parse rate (9/10 models)
   - All quality checks pass
   - No warnings or errors
   - Expected output:
     ```
     Parse Rate: 9/10 models (90.0%) ✅
     
     Passing: circle (95%), himmel16 (100%), mingamma (100%), 
              hs62, mathopt1, mhw4d, mhw4dx, rbrock, trig (all 100%)
     Failing: maxmin (18%, deferred to Sprint 11)
     ```

2. **Manual Testing** (30 min - 1 hour)
   - Test parser with actual GAMS models
   - Try variations of new features:
     - Different comma-separated patterns
     - Different function call patterns
     - Different variable bound patterns
   - Test error recovery:
     - Malformed comma-separated syntax
     - Invalid function calls
     - Invalid variable bounds
   - Verify helpful error messages
   - Document any usability issues

**Afternoon (1-2 hours): Buffer Time**

Use this time based on findings from morning validation:

**Option A: Bug Fixes (if any issues found)**
- Address any bugs discovered in testing
- Fix edge cases that weren't handled
- Improve error messages
- Re-run quality checks after fixes
- Document fixes in commit

**Option B: Code Cleanup (if no issues)**
- Refactor for clarity:
  - Variable bound index function
  - Comma-separated semantic handler
  - Function call detection logic
- Add code comments explaining complex sections
- Improve test coverage:
  - Add more edge case tests
  - Improve test documentation
- Optimize performance (if needed):
  - Profile parser for bottlenecks
  - Optimize hot paths

**Option C: Documentation (if all clean)**
- Write feature documentation:
  - Variable bound literal indices
  - Comma-separated scalar declarations
  - Function calls in assignments (parse-only)
- Add examples to docs:
  - Example GAMS code for each feature
  - Expected IR output
- Update user guides (if applicable)
- Create migration notes (if applicable)

**Option D: Start Sprint 11 Prep (if time permits)**
- Investigate Sprint 11 features:
  - Review maxmin.gms blocker analysis
  - Research nested/subset indexing semantics
  - Prototype approach for nested indexing
- Research additional GAMSLIB models:
  - Test parser on Tier 2 models
  - Identify next blockers
- Update Sprint 11 planning docs

**Deliverables:**
- [ ] Final validation complete
- [ ] Any discovered bugs fixed
- [ ] Code is clean and well-documented
- [ ] All quality checks pass
- [ ] **Parse Rate confirmed: 90% (9/10 models)**
- [ ] Buffer time used productively

**Quality Checks:**
```bash
make typecheck  # Must pass
make lint       # Must pass
make format     # Apply formatting
make test       # All tests must pass
```

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Final validation complete (all checks pass)
  - [ ] 90% parse rate confirmed and stable
  - [ ] Any bugs discovered and fixed
  - [ ] Code is clean and maintainable
  - [ ] Documentation complete
  - [ ] No regressions
  - [ ] Error messages are helpful
- [ ] Mark Day 9 as complete in `docs/planning/EPIC_2/SPRINT_10/PLAN.md`
- [ ] Log final validation results to commit message

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 10 Day 9: Final Validation + [Bug Fixes/Cleanup/Documentation]" \
                --body "Final validation of Sprint 10 features.

   **Validation Results:**
   - Parse rate: 90% (9/10 models) confirmed ✅
   - All quality checks pass
   - [Bug fixes / Code cleanup / Documentation / etc.]

   Completes Day 9 tasks from Sprint 10 PLAN.md" \
                --base main
   ```
2. Request review and address comments
3. Merge when approved

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_10/PLAN.md` (lines 565-624) - Day 9 details
- `scripts/measure_parse_rate.py` - Final parse rate validation

---

## Day 10 Prompt: Sprint Completion & Retrospective

**Branch:** Create a new branch named `sprint10-day10-completion` from `main`

**Objective:** Complete Sprint 10, document results, and prepare retrospective. Celebrate achieving 90% parse rate!

**Parse Rate Impact:** Maintain 90% (9/10 models) - Final confirmed

**Prerequisites:**
- Days 1-9 must be complete and merged
- All Sprint 10 features implemented, tested, and validated
- Sprint 10 goal achieved (90% parse rate)

**Tasks to Complete (1-2 hours):**

**Morning (1-2 hours):**

1. **Final Parse Rate Measurement** (15 min)
   ```bash
   python scripts/measure_parse_rate.py --verbose
   ```
   - Document final results
   - Capture full output for retrospective
   - Expected output:
     ```
     Testing GAMSLIB Tier 1 models...
     ============================================================
     ✅ PASS  circle.gms      (95%, 53/56 lines)
     ✅ PASS  himmel16.gms    (100%, 70/70 lines)
     ✅ PASS  hs62.gms        (100%)
     ✅ PASS  mathopt1.gms    (100%)
     ❌ FAIL  maxmin.gms      (18%, deferred to Sprint 11)
     ✅ PASS  mhw4d.gms       (100%)
     ✅ PASS  mhw4dx.gms      (100%)
     ✅ PASS  mingamma.gms    (100%, 63/63 lines)
     ✅ PASS  rbrock.gms      (100%)
     ✅ PASS  trig.gms        (100%)
     ============================================================
     Parse Rate: 9/10 models (90.0%) ✅
     ```
   - Screenshot or save output for documentation

2. **Update Sprint Documentation** (30 min)
   - Update `docs/planning/EPIC_2/SPRINT_10/PLAN.md`:
     - Mark all 10 days as complete
     - Document final parse rate (90%)
     - Note any deviations from schedule
   - Create/Update `docs/planning/EPIC_2/SPRINT_10/SPRINT_LOG.md`:
     - Document all completed features
     - Record parse rate progression:
       - Day 0: 60% (6/10 models)
       - Day 1: 70% (himmel16 unlocked)
       - Day 3: 80% (mingamma unlocked)
       - Day 6: 90% (circle unlocked) ✅
     - Note checkpoint results (Day 5: 80%, ON TRACK)
     - Document any issues encountered and resolutions

3. **Prepare Retrospective** (30 min - 1 hour)
   - Create `docs/planning/EPIC_2/SPRINT_10/RETROSPECTIVE.md`
   - Document what went well:
     - ✅ Prep phase identified clear blockers
     - ✅ Low-risk features first (de-risked early)
     - ✅ Mid-sprint checkpoint validated progress at Day 5 (80%, ON TRACK)
     - ✅ 90% goal achieved on Day 6 (ahead of Day 10 target)
     - ✅ All 3 features implemented successfully
     - ✅ No major surprises or unexpected blockers
   - Document what could improve:
     - Effort estimates (were they accurate?)
     - Feature interactions (any surprises?)
     - Testing approach (was coverage adequate?)
     - Documentation (was it sufficient?)
   - Action items for Sprint 11:
     - Plan maxmin.gms (nested/subset indexing)
     - Consider additional GAMSLIB models
     - Improve test coverage (if gaps found)
     - Refine estimation process (if estimates were off)
   - Compare to Sprint 10 goals:
     - Goal: 60% → 90% parse rate ✅ ACHIEVED
     - Goal: 3 models unlocked ✅ ACHIEVED
     - Goal: Mid-sprint checkpoint ✅ EXECUTED
     - Goal: No regressions ✅ MAINTAINED

4. **Commit Final Documentation** (15 min)
   - Commit: "Sprint 10 completion: 90% parse rate achieved"
   - Commit body:
     - Final parse rate: 90% (9/10 models)
     - Models unlocked: himmel16 (100%), mingamma (100%), circle (95%)
     - Features implemented: variable bound bug fix, comma-separated scalars, function calls
     - Checkpoint executed on Day 5 (80%, ON TRACK)
     - Sprint 10 goal achieved ✅
   - Tag: `sprint10-complete`
   - Push to remote

**Deliverables:**
- [ ] Final parse rate: **90% (9/10 models)** ✅
- [ ] Sprint documentation complete (`PLAN.md`, `SPRINT_LOG.md`)
- [ ] Retrospective prepared (`RETROSPECTIVE.md`)
- [ ] All commits tagged (`sprint10-complete`)
- [ ] Sprint 10 officially complete

**Completion Criteria:**
- [ ] All Sprint 10 success criteria met:
  - [x] **Parse Rate:** 60% → 90% (TARGET MET ✅)
  - [x] **Models Unlocked:** circle (95%), himmel16 (100%), mingamma (100%)
  - [x] **Features Implemented:**
    - Variable bound index bug fix ✅
    - Comma-separated scalar declarations ✅
    - Function calls in assignments (parse-only) ✅
  - [x] **Quality:** All tests pass, no regressions ✅
  - [x] **Checkpoint:** Day 5 checkpoint executed, validated progress ✅
  - [x] **Synthetic Tests:** All Sprint 10 features validated in isolation ✅
- [ ] Mark Day 10 complete in `docs/planning/EPIC_2/SPRINT_10/PLAN.md`
- [ ] Update README.md with Sprint 10 results
- [ ] Retrospective document created

**Sprint 10 Definition of Done:**
- [x] Parse rate increased from 60% to 90% (6/10 → 9/10 models)
- [x] Three target models unlocked (himmel16, mingamma, circle)
- [x] All implemented features validated in isolation (synthetic tests)
- [x] Mid-sprint checkpoint executed and documented
- [x] All quality checks pass with no regressions
- [x] Comprehensive test coverage for new features
- [x] Code is clean, documented, and maintainable
- [x] Retrospective prepared with lessons learned
- [x] Sprint 11 ready to start (maxmin.gms deferred with plan)

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 10 Day 10: Sprint Completion & Retrospective" \
                --body "Sprint 10 completion documentation and retrospective.

   **Sprint 10 Results:**
   - Final Parse Rate: 90% (9/10 models) ✅
   - Models Unlocked: himmel16 (100%), mingamma (100%), circle (95%)
   - Features: Variable bound bug fix, comma-separated scalars, function calls
   - Checkpoint: Day 5 (80%, ON TRACK)

   🎉 **SPRINT 10 GOAL ACHIEVED**

   Completes Day 10 tasks from Sprint 10 PLAN.md" \
                --base main
   ```
2. Request review and address comments
3. Merge when approved

**Celebration:**
🎉 **Sprint 10 Complete! 90% parse rate achieved!**
- Started: 60% (6/10 models)
- Finished: 90% (9/10 models)
- Models unlocked: 3 (himmel16, mingamma, circle)
- Features implemented: 3 (variable bound bug, comma-separated scalars, function calls)
- Days ahead of schedule: 4 (goal achieved Day 6, not Day 10)

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_10/PLAN.md` (lines 625-690) - Day 10 details
- `docs/planning/EPIC_2/SPRINT_10/SPRINT_LOG.md` - To be created/updated
- `docs/planning/EPIC_2/SPRINT_10/RETROSPECTIVE.md` - To be created

---

## Notes for Execution

### General Guidelines:

1. **Daily Progress Tracking:**
   - Run `python scripts/measure_parse_rate.py --verbose` at end of each day
   - Document parse rate progression
   - Note any deviations from schedule

2. **Quality Checks are Mandatory:**
   - **ALWAYS** run `make typecheck && make lint && make format && make test` before committing
   - **Exception:** Skip if ONLY documentation files (.md, .txt) modified
   - All checks must pass before creating PR

3. **Checkpoint is Critical:**
   - Day 5 checkpoint is **NOT optional**
   - Use decision matrix in CHECKPOINT.md
   - Document checkpoint results in SPRINT_LOG.md

4. **Buffer Time is Real:**
   - Days 9-10 are genuine buffer, not "stretch goals"
   - Use for unexpected issues, not planned work
   - Resist temptation to fill with new features

5. **Defer Decisions are OK:**
   - maxmin.gms deferred is a **SUCCESS**, not a failure
   - 90% (9/10) is excellent progress
   - Quality over quantity

6. **Communication:**
   - Update SPRINT_LOG.md daily (or in commit messages)
   - Document all decisions (especially checkpoint)
   - Prepare retrospective as you go

7. **Testing is Non-Negotiable:**
   - All quality checks must pass before committing
   - Synthetic tests validate features in isolation
   - Regression testing prevents breakage

8. **Risk Awareness:**
   - Monitor risk indicators (time spent, complexity)
   - Activate mitigation early (don't wait for disaster)
   - Checkpoint provides decision point on Day 5

---

**Sprint 10 Ready to Execute!**

Use these prompts day-by-day to systematically execute Sprint 10 and achieve the 90% parse rate goal.

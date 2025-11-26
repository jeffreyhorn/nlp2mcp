# Sprint 11 Day-by-Day Prompts

This file contains comprehensive prompts for each day of Sprint 11 (Days 1-10). Each prompt is designed to be used when starting work on that specific day.

**Sprint Goal:** 100% Tier 1 Parse Rate + Aggressive Simplification (Full) + CI Guardrails  
**Sprint Theme:** "Complete Tier 1 Coverage + Quality Infrastructure"  
**Total Effort:** 45 hours planned + 5 hours buffer = 50 hours total

---

## Day 1 Prompt: Grammar Extension for Nested Indexing

**Branch:** Create a new branch named `sprint11-day1-grammar-nested-indexing` from `main`

**Objective:** Extend GAMS grammar to support nested/subset indexing for maxmin.gms parsing

**Effort:** 6 hours

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_11/maxmin_implementation_plan.md` - Complete research on nested indexing implementation
- Review `docs/planning/EPIC_2/SPRINT_11/KNOWN_UNKNOWNS.md` (Unknown 1.2) - Grammar extension complexity
- Review `docs/planning/EPIC_2/SPRINT_11/PREP_PLAN.md` (Task 2) - maxmin.gms research findings
- Examine `data/gamslib/maxmin.gms` - Target model we need to parse
- Review Lark parser documentation for recursive grammar rules

**Tasks to Complete (6 hours):**

1. **Research current grammar limitations** (30 min)
   - Open and analyze `src/parser/gams.lark`
   - Parse `data/gamslib/maxmin.gms` and document specific syntax patterns that fail
   - Identify which line numbers in maxmin.gms cause parse failures
   - Review Lark documentation for recursive rules and nesting support

2. **Design grammar extension** (1h)
   - Implement **Explicit Subset Syntax** (from Task 2 research)
   - Design `subset_domain` rule: `identifier "(" domain_list ")"`
   - Design modification to `domain_element` to support recursive nesting
   - Document grammar changes with examples:
     ```gams
     Variable x(i);           # Simple domain
     Variable y(i(subset));   # Nested domain
     Variable z(i,j(k));      # Mixed simple + nested
     ```
   - Ensure backward compatibility with existing 9 Tier 1 models

3. **Implement grammar changes** (2h)
   - File: `src/parser/gams.lark`
   - Add new grammar rules:
     ```lark
     domain_element: identifier ("(" domain_list ")")?
     subset_domain: identifier "(" domain_list ")"
     ```
   - Update `domain_list` rule to support recursive parsing
   - Add depth limit to recursive rules (max 5 levels) to prevent infinite loops
   - Test grammar changes incrementally

4. **Create unit tests for new grammar** (1.5h)
   - File: `tests/unit/test_nested_domain_grammar.py` (create new file)
   - Implement 5 synthetic test cases:
     1. Simple nested domain: `x(i(j))`
     2. Multiple nesting levels: `x(i(j(k)))`
     3. Mixed domains: `x(i,j(k))`
     4. Subset filtering: `x(i|condition)`
     5. Multiple subsets: `x(i(j),k(l))`
   - Each test should verify successful parsing to AST
   - Run: `pytest tests/unit/test_nested_domain_grammar.py -v`

5. **Validation and regression testing** (1h)
   - Parse maxmin.gms with new grammar - expect AST generation (may not be semantically valid yet)
   - Verify no regressions on other 9 Tier 1 models:
     - circle.gms, himmel16.gms, hs62.gms, mathopt1.gms
     - mhw4d.gms, mhw4dx.gms, mingamma.gms, rbrock.gms, trig.gms
   - Run full test suite: `make test`
   - Document any unexpected failures

**Deliverables:**
- [ ] Grammar extension implemented in `src/parser/gams.lark`
- [ ] 5 unit tests for nested domain parsing passing
- [ ] maxmin.gms parses to AST (even if semantically incomplete)
- [ ] No regressions in existing 9 Tier 1 models
- [ ] All existing tests still pass

**Quality Checks:**
ALWAYS run these commands before committing code changes:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Grammar accepts nested indexing syntax
  - [ ] maxmin.gms AST generated (even if incomplete)
  - [ ] All 5 synthetic tests pass
  - [ ] All existing tests pass
  - [ ] Quality checks pass (typecheck, lint)
- [ ] Mark Day 1 as complete in `docs/planning/EPIC_2/SPRINT_11/PLAN.md`
- [ ] Check off Day 1 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md`:
  - Add PR entry to Day 1 section
  - Document any grammar design decisions made
  - Note any unexpected challenges
  - Update parse rate table if maxmin.gms parse rate changed
  - See `docs/planning/EPIC_2/SPRINT_11/incremental_documentation_guide.md` for templates

**Early Validation:**
Post-Day 1, verify:
- All 5 synthetic tests parse successfully
- If >2 synthetic tests fail: STOP - Revise grammar design before Day 2

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 11 Day 1: Grammar Extension for Nested Indexing" \
                --body "Completes Day 1 tasks from Sprint 11 PLAN.md

   - Extends GAMS grammar to support nested/subset indexing
   - Adds 5 unit tests for nested domain parsing
   - Enables maxmin.gms to parse to AST
   - No regressions in existing models" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_11/PLAN.md` (lines 270-375)
- `docs/planning/EPIC_2/SPRINT_11/maxmin_implementation_plan.md` (full document)
- `docs/planning/EPIC_2/SPRINT_11/KNOWN_UNKNOWNS.md` (Unknown 1.2)

---

## Day 2 Prompt: Semantic Resolution for Nested Indexing

**Branch:** Create a new branch named `sprint11-day2-semantic-nested-indexing` from `main`

**Objective:** Implement semantic analysis for nested domains to enable maxmin.gms semantic resolution

**Effort:** 6 hours

**Prerequisites:**
- Day 1 must be complete (grammar extension merged)
- Read `docs/planning/EPIC_2/SPRINT_11/maxmin_implementation_plan.md` - Semantic resolution algorithm
- Review `docs/planning/EPIC_2/SPRINT_11/KNOWN_UNKNOWNS.md` (Unknown 1.3) - Eager expansion performance
- Review existing semantic resolution in `src/semantic/resolver.py`
- Understand existing AST nodes in `src/ast/nodes.py`

**Tasks to Complete (6 hours):**

1. **Design AST representation** (1.5h)
   - File: `src/ast/nodes.py`
   - Add new AST node classes:
     ```python
     class DomainElement:
         name: str
         subset: Optional[DomainList] = None
         
     class SimpleDomain(DomainElement):
         # Simple identifier (e.g., i)
         pass
         
     class SubsetDomain(DomainElement):
         # Nested domain (e.g., i(j))
         base: str
         filter: DomainList
     ```
   - Update `VariableDeclaration` class to use new domain nodes
   - Ensure backward compatibility with existing simple domains
   - Add type hints and docstrings

2. **Implement semantic resolution** (2.5h)
   - File: `src/semantic/resolver.py`
   - Add `resolve_nested_domain()` method
   - Implement **Eager expansion algorithm** (from Task 2 research):
     1. Resolve base domain (outer set)
     2. For each element in base, resolve subset (inner set)
     3. Build Cartesian product of valid combinations
     4. Cache result for reuse (avoid redundant computation)
   - Handle symbol table lookups for nested references
   - Validate domain compatibility (type checking)
   - Add error handling for undefined sets and type mismatches

3. **Add unit tests** (1.5h)
   - File: `tests/unit/test_nested_indexing.py` (create new file)
   - Test cases:
     1. Simple nested domain resolution
     2. Multiple nesting levels (2-3 levels)
     3. Subset filtering with conditions
     4. Error case: undefined sets
     5. Error case: type mismatches
     6. Performance test: maxmin.gms resolution time <1ms
   - Run: `pytest tests/unit/test_nested_indexing.py -v`

4. **Integration testing** (30 min)
   - Test maxmin.gms full parse + semantic pipeline
   - Measure parse rate: Expected 80-100%
   - Check semantic errors: Expected 0-2 minor issues
   - Verify AST structure matches expectations
   - Document actual vs. expected results

**Deliverables:**
- [ ] AST nodes for nested domains implemented in `src/ast/nodes.py`
- [ ] Semantic resolution algorithm working in `src/semantic/resolver.py`
- [ ] 6+ unit tests passing
- [ ] maxmin.gms resolves semantically (no errors or only minor expected errors)
- [ ] Performance <1ms for maxmin.gms resolution

**Quality Checks:**
ALWAYS run these commands before committing code changes:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Nested domain resolution works correctly
  - [ ] Symbol table handles nested references
  - [ ] maxmin.gms semantic analysis completes
  - [ ] Performance <1ms for maxmin.gms resolution
  - [ ] Quality checks pass
- [ ] Mark Day 2 as complete in `docs/planning/EPIC_2/SPRINT_11/PLAN.md`
- [ ] Check off Day 2 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md`:
  - Add PR entry to Day 2 section
  - Document semantic resolution algorithm decisions
  - Note any performance optimization needed
  - Update parse rate table if maxmin.gms improved

**Early Validation - Decision Point:**
After integration testing:
- If parse rate <80%: **ACTIVATE BUFFER** - Extend Day 3 to debug, notify stakeholders
- If parse rate ≥80%: Proceed to Day 3 checkpoint as planned

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 11 Day 2: Semantic Resolution for Nested Indexing" \
                --body "Completes Day 2 tasks from Sprint 11 PLAN.md

   - Implements semantic analysis for nested domains
   - Adds AST nodes for nested/simple domains
   - Adds eager expansion algorithm with caching
   - maxmin.gms semantic resolution working" \
                --base main
   ```
2. Request a review from Copilot
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_11/PLAN.md` (lines 376-475)
- `docs/planning/EPIC_2/SPRINT_11/maxmin_implementation_plan.md` (semantic resolution section)
- `docs/planning/EPIC_2/SPRINT_11/KNOWN_UNKNOWNS.md` (Unknown 1.3)

---

## Day 3 Prompt: maxmin.gms Validation + Simplification Pipeline Start (CHECKPOINT)

**Branch:** Create a new branch named `sprint11-day3-checkpoint-tier1-100pct` from `main`

**Objective:** Validate 100% Tier 1 parse rate (Day 3 Checkpoint) and begin simplification infrastructure

**Effort:** 5 hours (3h validation + 2h pipeline infrastructure)

**Prerequisites:**
- Days 1-2 must be complete (nested indexing fully implemented)
- Read `docs/planning/EPIC_2/SPRINT_11/aggressive_simplification_architecture.md` - Full pipeline design
- Review `docs/planning/EPIC_2/SPRINT_11/PLAN.md` Day 3 Checkpoint criteria (lines 147-175)
- Ensure all 10 Tier 1 models are in `data/gamslib/`

**Tasks to Complete (5 hours):**

### Morning (3 hours): maxmin.gms Validation

1. **Run Day 3 checkpoint validation** (1.5h)
   - Run full Tier 1 test suite on all 10 models:
     - circle.gms, himmel16.gms, hs62.gms, mathopt1.gms, maxmin.gms
     - mhw4d.gms, mhw4dx.gms, mingamma.gms, rbrock.gms, trig.gms
   - Measure parse rate for each model
   - **Target:** 10/10 models at 100% parse rate
   - Document any remaining issues in SPRINT_LOG.md
   - Run all synthetic tests from Days 1-2

2. **Integration testing** (1h)
   - Test maxmin.gms end-to-end pipeline:
     - Parse → AST ✓
     - Semantic → Symbol table ✓
     - IR generation (attempt)
     - MCP generation (attempt if IR works)
   - Verify no regressions in other 9 Tier 1 models
   - Run full test suite: `make test`
   - Document any unexpected behavior

3. **Document checkpoint results** (30 min)
   - File: `docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md`
   - Record Day 3 checkpoint results:
     - Parse rate per model (table format)
     - Remaining blockers (if any)
     - Decisions made (defer vs. fix)
     - Buffer usage (if any)
     - Next steps

### Afternoon (2 hours): Simplification Pipeline Infrastructure

4. **Create SimplificationPipeline class** (2h)
   - File: `src/ir/simplification_pipeline.py` (create new file)
   - Implement class structure:
     ```python
     class SimplificationPipeline:
         def __init__(self, max_iterations=5, size_budget=1.5):
             self.passes = []
             self.max_iterations = max_iterations
             self.size_budget = size_budget
             
         def add_pass(self, pass_fn, priority, name):
             # Register transformation pass
             
         def apply(self, expr, metrics=None):
             # Apply all passes with fixpoint iteration
             # Enforce size budget at each step
             # Return simplified expression + metrics
     ```
   - Add size measurement utility: `_expression_size(expr) -> int`
   - Add rollback mechanism for budget violations
   - Create module structure: `src/ir/transformations/` directory
   - Add basic integration tests

**Deliverables:**
- [ ] **Day 3 Checkpoint Complete:** 100% Tier 1 parse rate documented
- [ ] maxmin.gms validation results in SPRINT_LOG.md with parse rate table
- [ ] SimplificationPipeline class implemented
- [ ] Transformation module structure created (`src/ir/transformations/`)
- [ ] Decision made: Proceed to Phase 2 or extend with buffer

**Quality Checks:**
ALWAYS run these commands before committing code changes:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] 10/10 Tier 1 models parse successfully
  - [ ] maxmin.gms at 100% parse rate (or blockers documented)
  - [ ] All tests pass
  - [ ] SimplificationPipeline infrastructure created
  - [ ] Quality checks pass
- [ ] **Check off Day 3 Checkpoint criteria in PLAN.md:**
  - [ ] maxmin.gms parses to 100% ✓
  - [ ] Nested indexing support implemented ✓
  - [ ] 10/10 Tier 1 models at 100% parse rate ✓
  - [ ] All unit tests passing ✓
- [ ] Mark Day 3 as complete in `docs/planning/EPIC_2/SPRINT_11/PLAN.md`
- [ ] Check off Day 3 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md`:
  - Add PR entry to Day 3 section
  - **IMPORTANT:** Update parse rate table with all 10 models
  - Document checkpoint decision
  - Note any buffer usage

**Checkpoint Decision Matrix:**

| Result | Status | Action |
|--------|--------|--------|
| maxmin.gms parses to 100% | ✅ On Track | Proceed to Phase 2 (Day 4) |
| maxmin.gms parses to 80-99% | ⚠️ Acceptable | Document blockers, proceed |
| maxmin.gms parses to <80% | ❌ Behind | **ACTIVATE BUFFER: Extend to Day 4** |

If <80%:
- Use 5h buffer: Extend maxmin work to Day 4
- Defer MEDIUM simplification transforms (save 2h)
- Document decisions in SPRINT_LOG.md

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 11 Day 3: CHECKPOINT - 100% Tier 1 Parse Rate + Pipeline Start" \
                --body "Completes Day 3 tasks and Checkpoint from Sprint 11 PLAN.md

   🎯 DAY 3 CHECKPOINT ACHIEVED:
   - 10/10 Tier 1 models at 100% parse rate
   - maxmin.gms parses successfully
   - Nested indexing support complete
   
   - SimplificationPipeline infrastructure created
   - Ready for Phase 2 (aggressive simplification)" \
                --base main
   ```
2. Request a review from Copilot
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_11/PLAN.md` (lines 476-575, checkpoint lines 147-175)
- `docs/planning/EPIC_2/SPRINT_11/aggressive_simplification_architecture.md`

---

## Day 4 Prompt: Core HIGH Priority Transformations (1-3)

**Branch:** Create a new branch named `sprint11-day4-core-transforms-1-3` from `main`

**Objective:** Implement first 3 HIGH-priority transformations for aggressive simplification

**Effort:** 6 hours (2h per transformation)

**Prerequisites:**
- Day 3 must be complete (SimplificationPipeline infrastructure ready)
- Read `docs/planning/EPIC_2/SPRINT_11/aggressive_simplification_architecture.md` - Section on Transformation Categories
- Review existing simplification in `src/ad/ad_core.py` and `src/ad/term_collection.py`
- Understand transformation priorities: HIGH priority = core term reduction mechanisms

**Tasks to Complete (6 hours):**

1. **Implement common factor extraction (T1.1)** (2h)
   - **Pass 1: Common Factor Extraction** (HIGH priority)
   - File: `src/ir/transformations/factoring.py` (create new file)
   - Algorithm:
     ```python
     def extract_common_factor(expr):
         # Factor: a*x + b*x → (a+b)*x
         # Pattern: Same multiplier across terms
         # Use SymPy factor() with safety checks
     ```
   - Implement helper: `_find_common_factors(terms: list[Expr]) -> list[Expr]`
   - Implement helper: `_get_multiplication_factors(expr: Expr) -> list[Expr]`
   - Safety heuristics:
     - Check size budget (150% max)
     - Detect cancellation opportunities
     - Reject if expansion would exceed budget
   - Unit tests: 10 test cases (basic, nested, edge cases)
   - Test file: `tests/unit/test_factoring.py`

2. **Implement fraction combining (T1.4)** (2h)
   - **Pass 2: Fraction Combining** (HIGH priority)
   - File: `src/ir/transformations/fractions.py` (create new file)
   - Algorithm:
     ```python
     def combine_fractions(expr):
         # Combine: a/c + b/c → (a+b)/c
         # Pattern: Same denominator
         # Use SymPy together() with validation
     ```
   - Safety heuristics:
     - Verify denominator non-zero (symbolic analysis)
     - Check for common denominators
     - Size budget enforcement
   - Unit tests: 10 test cases
   - Test file: `tests/unit/test_fractions.py`

3. **Implement associativity normalization (T2.1)** (2h)
   - **Pass 3: Associativity** (HIGH priority)
   - File: `src/ir/transformations/associativity.py` (create new file)
   - Algorithm:
     ```python
     def normalize_associativity(expr):
         # Left-associate: (a+b)+c → a+(b+c)
         # Enables like-term detection across nesting
         # Consolidate constants: (x * 2) * 3 → x * 6
     ```
   - Handle both addition and multiplication associativity
   - Safety: preserve semantics, check size budget
   - Unit tests: 10 test cases
   - Test file: `tests/unit/test_associativity.py`

**Deliverables:**
- [ ] Common factor extraction implemented (T1.1) in `src/ir/transformations/factoring.py`
- [ ] Fraction combining implemented (T1.4) in `src/ir/transformations/fractions.py`
- [ ] Associativity normalization implemented (T2.1) in `src/ir/transformations/associativity.py`
- [ ] 30+ unit tests passing (10 per transformation)
- [ ] Integration with SimplificationPipeline
- [ ] Size budget enforced for all transformations

**Quality Checks:**
ALWAYS run these commands before committing code changes:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] All 3 transformations work independently
  - [ ] No size explosions (budget enforced)
  - [ ] Unit tests pass
  - [ ] Quality checks pass
- [ ] Mark Day 4 as complete in `docs/planning/EPIC_2/SPRINT_11/PLAN.md`
- [ ] Check off Day 4 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md`:
  - Add PR entry to Day 4 section
  - Document any transformation design decisions
  - Note any challenges with size budget enforcement

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 11 Day 4: Core HIGH Priority Transformations (1-3)" \
                --body "Completes Day 4 tasks from Sprint 11 PLAN.md

   Implements 3 HIGH-priority transformations:
   - T1.1: Common factor extraction
   - T1.4: Fraction combining
   - T2.1: Associativity normalization
   
   - 30+ unit tests passing
   - Size budget enforcement working" \
                --base main
   ```
2. Request a review from Copilot
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_11/PLAN.md` (lines 576-640)
- `docs/planning/EPIC_2/SPRINT_11/aggressive_simplification_architecture.md` (Transformation Categories section)
- `docs/planning/EPIC_2/SPRINT_11/transformation_catalog.md`

---

## Day 5 Prompt: Remaining HIGH Transforms + MEDIUM Priority Start + Checkpoint

**Branch:** Create a new branch named `sprint11-day5-transforms-4-6-medium-start` from `main`

**Objective:** Complete remaining 3 HIGH transformations, start 2 MEDIUM transformations, and validate Day 5 checkpoint

**Effort:** 5 hours (2.5h HIGH + 1.5h MEDIUM + 1h checkpoint)

**Prerequisites:**
- Day 4 must be complete (first 3 HIGH transforms implemented)
- Read `docs/planning/EPIC_2/SPRINT_11/aggressive_simplification_architecture.md` - Transformation priorities
- Review `docs/planning/EPIC_2/SPRINT_11/transformation_catalog.md` - Full transformation details
- Review existing transformations from Day 4

**Tasks to Complete (5 hours):**

### Morning (2.5 hours): Remaining HIGH Priority Transformations

1. **Implement division simplification (T3.1)** (1h)
   - **Pass 4: Division Simplification** (HIGH priority)
   - File: `src/ir/transformations/division.py` (create new file)
   - Algorithm:
     ```python
     def simplify_division(expr):
         # Simplify: (a*b)/a → b (if a ≠ 0)
         # Cancel common factors in numerator/denominator
         # Conservative heuristic (literals + named vars only)
     ```
   - Safety checks:
     - Non-zero detection (symbolic + literal analysis)
     - Size budget enforcement
     - Avoid division by zero risks
   - Unit tests: 10 test cases
   - Test file: `tests/unit/test_division.py`

2. **Implement multi-term factoring (T1.2)** (1h)
   - **Pass 5: Multi-Term Factoring** (HIGH priority)
   - File: `src/ir/transformations/factoring.py` (extend existing)
   - Algorithm:
     ```python
     def multi_term_factoring(expr):
         # Pattern: a*c + a*d + b*c + b*d → (a + b)*(c + d)
         # Group terms by common factors
         # Extract common structure (2+ terms)
     ```
   - Safety checks:
     - Check size budget before applying
     - Only apply if beneficial (net reduction)
     - Avoid creating deeply nested structures
   - Unit tests: 10 test cases

3. **Implement enhanced like-term collection (T2.1 enhancement)** (30 min)
   - **Pass 6: Enhanced Like-Term Collection** (HIGH priority)
   - File: `src/ad/term_collection.py` (enhance existing)
   - Enhance existing `collect_like_terms()` function:
     - Better pattern matching across nested expressions
     - Handle associativity transformations from Pass 3
     - Integration with SimplificationPipeline
   - Unit tests: 5 test cases
   - Test file: `tests/unit/test_like_terms_enhanced.py`

### Afternoon (1.5 hours): MEDIUM Priority Transformations Start

4. **Implement nested product simplification (T2.2)** (45 min)
   - **Pass 7: Nested Product Simplification** (MEDIUM priority)
   - File: `src/ir/transformations/nested_operations.py` (create new file)
   - Pattern: `(a*b)*c → a*b*c` with constant consolidation
   - Flatten nested multiplications
   - Consolidate constants: `(2*x)*3 → 6*x`
   - Unit tests: 8 test cases
   - Test file: `tests/unit/test_nested_operations.py`

5. **Implement power expression consolidation (T2.3)** (45 min)
   - **Pass 8: Power Expression Consolidation** (MEDIUM priority)
   - File: `src/ir/transformations/power_rules.py` (create new file)
   - Patterns:
     - `x^a * x^b → x^(a+b)`
     - `(x^a)^b → x^(a*b)`
     - `x^1 → x`, `x^0 → 1`
   - Safety: check for numeric stability, avoid negative exponents
   - Unit tests: 8 test cases
   - Test file: `tests/unit/test_power_rules.py`

### Late Afternoon (1 hour): Day 5 Checkpoint

6. **Run benchmark validation** (1h)
   - Benchmark on all 10 Tier 1 models:
     - circle, himmel16, hs62, mathopt1, maxmin
     - mhw4d, mhw4dx, mingamma, rbrock, trig
   - Measure derivative term counts:
     - Before simplification (baseline)
     - After simplification (with all 6 HIGH + 2 MEDIUM transforms)
   - Apply all transformations in pipeline with fixpoint iteration
   - Calculate reduction percentage per model
   - **Target:** ≥20% reduction on ≥3 models
   - Document results in SPRINT_LOG.md with table

**Deliverables:**
- [ ] Division simplification implemented (T3.1)
- [ ] Multi-term factoring implemented (T1.2)
- [ ] Enhanced like-term collection (T2.1 enhancement)
- [ ] Nested product simplification implemented (T2.2)
- [ ] Power expression consolidation implemented (T2.3)
- [ ] 51+ new unit tests passing (10+10+5+8+8 from today)
- [ ] **Day 5 Checkpoint Complete:** ≥20% reduction documented
- [ ] Benchmark results in SPRINT_LOG.md

**Quality Checks:**
ALWAYS run these commands before committing code changes:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] All 5 transformations work together (4 today + previous)
  - [ ] No conflicts between passes
  - [ ] ≥20% term reduction on ≥3 models (checkpoint met)
  - [ ] Pipeline fixpoint iteration working
  - [ ] Quality checks pass
- [ ] **Check off Day 5 Checkpoint criteria in PLAN.md:**
  - [ ] 6 HIGH-priority transformations implemented ✓
  - [ ] 2 MEDIUM-priority transformations started ✓
  - [ ] ≥20% term reduction on ≥3 models ✓
  - [ ] No size explosions (budget working) ✓
  - [ ] All tests passing ✓
- [ ] Mark Day 5 as complete in `docs/planning/EPIC_2/SPRINT_11/PLAN.md`
- [ ] Check off Day 5 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md`:
  - Add PR entry to Day 5 section
  - **IMPORTANT:** Add benchmark results table showing term reduction per model
  - Document checkpoint decision
  - Note which transforms were most effective

**Checkpoint Decision Matrix:**

| Result | Status | Action |
|--------|--------|--------|
| ≥20% on ≥3 models | ✅ On Track | Proceed to Day 6 testing |
| ≥15% on ≥3 models | ⚠️ Acceptable | Document findings, proceed |
| <15% on most models | ❌ Behind | **ACTIVATE BUFFER: Use 1h to adjust heuristics** |

If <15%:
- Analyze which transforms are ineffective
- Use 1h buffer to adjust heuristics or add optimization
- Re-validate before proceeding to Phase 4

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 11 Day 5: CHECKPOINT - Remaining HIGH + MEDIUM Start + ≥20% Reduction" \
                --body "Completes Day 5 tasks and Checkpoint from Sprint 11 PLAN.md

   🎯 DAY 5 CHECKPOINT ACHIEVED:
   - 6 HIGH-priority transformations implemented
   - 2 MEDIUM-priority transformations started
   - ≥20% term reduction on ≥3 models
   
   Transformations implemented:
   - T3.1: Division simplification
   - T1.2: Multi-term factoring
   - T2.1: Enhanced like-term collection
   - T2.2: Nested product simplification
   - T2.3: Power expression consolidation
   
   - 51+ unit tests passing" \
                --base main
   ```
2. Request a review from Copilot
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_11/PLAN.md` (lines 640-750)
- `docs/planning/EPIC_2/SPRINT_11/aggressive_simplification_architecture.md`
- `docs/planning/EPIC_2/SPRINT_11/transformation_catalog.md`

---

## Day 6 Prompt: MEDIUM Transforms Finish + Testing + CI Matrix Builds

**Branch:** Create a new branch named `sprint11-day6-medium-finish-ci-matrix` from `main`

**Objective:** Complete MEDIUM transformations, comprehensive testing, and begin CI infrastructure

**Effort:** 4 hours (1.5h MEDIUM transforms + 1h testing + 1.5h CI)

**Prerequisites:**
- Day 5 must be complete (6 HIGH + 2 MEDIUM transforms implemented)
- Read `docs/planning/EPIC_2/SPRINT_11/PLAN.md` Day 6 section
- Review `.github/workflows/gamslib-regression.yml` - Current CI workflow
- Understand GitHub Actions matrix strategy

**Tasks to Complete (4 hours):**

### Morning (1.5 hours): Complete MEDIUM Priority Transformations

1. **Implement trigonometric identities (T2.4)** (45 min)
   - **Pass 9: Trigonometric Identities** (MEDIUM priority)
   - File: `src/ir/transformations/trig_rules.py` (create new file)
   - Patterns:
     - `sin^2(x) + cos^2(x) → 1`
     - `tan(x) → sin(x)/cos(x)`
     - `sec(x) → 1/cos(x)`, `csc(x) → 1/sin(x)`
   - Conservative application (only common identities)
   - Safety: Avoid complex trig expansions that increase size
   - Unit tests: 8 test cases
   - Test file: `tests/unit/test_trig_rules.py`

2. **Implement logarithm rules (T2.5)** (45 min)
   - **Pass 10: Logarithm Simplification** (MEDIUM priority)
   - File: `src/ir/transformations/log_rules.py` (create new file)
   - Patterns:
     - `log(a*b) → log(a) + log(b)`
     - `log(a/b) → log(a) - log(b)`
     - `log(a^n) → n*log(a)`
     - `log(1) → 0`, `log(e) → 1` (if natural log)
   - Safety checks:
     - Check domain (positive arguments only)
     - Avoid introducing invalid log operations
     - Size budget enforcement
   - Unit tests: 8 test cases
   - Test file: `tests/unit/test_log_rules.py`

### Mid-Morning (1 hour): Simplification Validation & Metrics

3. **Add metrics collection** (30 min)
   - File: `src/ir/simplification_pipeline.py` (extend existing)
   - Implement `--simplification-stats` flag
   - Collect per-pass metrics:
     ```python
     class SimplificationMetrics:
         terms_before: int
         terms_after: int
         time_spent_ms: float
         transformations_applied: int
         size_change_pct: float
     ```
   - Basic summary output (text only):
     ```
     Simplification Statistics:
     - Pass 1 (Factoring): 15 terms → 12 terms (20% reduction, 45ms)
     - Pass 2 (Fractions): 12 terms → 10 terms (17% reduction, 38ms)
     ...
     - Total: 15 terms → 8 terms (47% reduction, 230ms)
     ```

4. **Comprehensive validation** (30 min)
   - Run on all 10 Tier 1 models with ALL transformations (6 HIGH + 4 MEDIUM)
   - Verify ≥20% reduction on ≥50% of models (5/10 models)
   - Add finite difference (FD) validation tests:
     - Numerical validation: simplified expression matches original
     - Test edge cases: zero division, empty expressions, single terms
   - Performance check: overhead <10% compared to baseline
   - Document results in table format

### Afternoon (1.5 hours): CI Matrix Builds

5. **Add matrix strategy to GAMSLib workflow** (1.5h)
   - File: `.github/workflows/gamslib-regression.yml`
   - Add matrix strategy for parallelization:
     ```yaml
     strategy:
       matrix:
         model: [circle, himmel16, hs62, mathopt1, maxmin, 
                 mhw4d, mhw4dx, mingamma, rbrock, trig]
       fail-fast: false
     ```
   - Parallelize model testing (reduce 10 min → 2-3 min)
   - Add job consolidation for aggregate results:
     ```yaml
     consolidate-results:
       needs: test-matrix
       runs-on: ubuntu-latest
       steps:
         - name: Aggregate parse rates
         - name: Check overall success
     ```
   - Test on feature branch before merging
   - Measure CI runtime improvement

**Deliverables:**
- [ ] Trigonometric identities implemented (T2.4)
- [ ] Logarithm rules implemented (T2.5)
- [ ] **ALL 10 transformations complete** (6 HIGH + 4 MEDIUM)
- [ ] Metrics collection implemented (`--simplification-stats`)
- [ ] ≥20% reduction on ≥5 models validated
- [ ] FD validation tests passing
- [ ] Matrix build workflow running
- [ ] CI time reduced to 2-3 min

**Quality Checks:**
ALWAYS run these commands before committing code changes:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Simplification metrics accurate
  - [ ] ≥20% reduction on ≥50% models (5/10)
  - [ ] FD validation confirms correctness
  - [ ] Matrix builds parallelize successfully
  - [ ] Quality checks pass
- [ ] Mark Day 6 as complete in `docs/planning/EPIC_2/SPRINT_11/PLAN.md`
- [ ] Check off Day 6 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md`:
  - Add PR entry to Day 6 section
  - Document all 10 transformations completion
  - Add validation results table
  - Note CI time improvement

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 11 Day 6: MEDIUM Transforms Complete + Testing + CI Matrix" \
                --body "Completes Day 6 tasks from Sprint 11 PLAN.md

   🎉 ALL 10 TRANSFORMATIONS COMPLETE:
   - T2.4: Trigonometric identities
   - T2.5: Logarithm simplification
   
   - Metrics collection implemented
   - ≥20% reduction on ≥5 models validated
   - FD validation passing
   - Matrix builds reduce CI time to 2-3 min" \
                --base main
   ```
2. Request a review from Copilot
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_11/PLAN.md` (lines 750-850)
- `docs/planning/EPIC_2/SPRINT_11/aggressive_simplification_architecture.md`
- `.github/workflows/gamslib-regression.yml`

---

## Day 7 Prompt: Performance Baselines + CSE Advanced (T5.2-T5.3) + Checkpoint

**Branch:** Create a new branch named `sprint11-day7-baselines-cse-advanced` from `main`

**Objective:** Complete CI infrastructure with baselines, begin CSE advanced features, validate Day 7 checkpoint

**Effort:** 5 hours (2h baselines + 2h CSE + 1h checkpoint)

**Prerequisites:**
- Day 6 must be complete (matrix builds working)
- Read `docs/planning/EPIC_2/SPRINT_11/PLAN.md` Day 7 section
- Review existing CSE implementation in `src/ir/transformations/cse.py`
- Understand baseline tracking requirements

**Tasks to Complete (5 hours):**

### Morning (2 hours): Baseline Implementation

1. **Create baseline storage** (1h)
   - Create `baselines/` directory structure:
     ```
     baselines/
       performance/
         rolling/         # Latest from main branch
         golden/          # Sprint milestones
       parse_rate/        # Git-tracked parse rate baselines
     ```
   - Create baseline JSON format:
     ```json
     {
       "model": "circle.gms",
       "parse_rate": 1.0,
       "convert_rate": 1.0,
       "parse_time_ms": 45,
       "total_time_ms": 443,
       "commit": "abc1234",
       "timestamp": "2024-01-15T10:30:00Z"
     }
     ```
   - Add `.gitignore` for `rolling/` (not tracked)
   - Add `golden/` to git (milestone snapshots)
   - Add comparison script skeleton: `scripts/compare_performance.py`

2. **Implement performance tracking** (1h)
   - File: `scripts/compare_performance.py` (create new file)
   - Compare current run vs rolling baseline:
     ```python
     def compare_performance(current, baseline):
         delta_parse_time = (current - baseline) / baseline * 100
         if delta_parse_time > 20:
             print("WARNING: 20% slower")
         if delta_parse_time > 50:
             raise Exception("FAILURE: 50% slower")
     ```
   - Calculate deltas per model
   - Apply thresholds:
     - 20% warning (log but pass)
     - 50% failure (fail CI)
   - Basic console output (no PR comment polish yet)
   - Test with synthetic baseline data

### Afternoon (2 hours): CSE Advanced Features (T5.2-T5.3)

3. **Implement nested CSE (T5.2)** (1h)
   - **T5.2: Nested CSE** (CSE with subexpression dependencies)
   - File: `src/ir/transformations/cse_advanced.py` (create new file)
   - Algorithm:
     ```python
     def nested_cse(expr):
         # Handle CSE candidates that depend on other CSE candidates
         # Example: exp(x+y) * sin(x+y) → t1 = x+y; exp(t1) * sin(t1)
         # Build dependency graph of subexpressions
         # Topologically sort to handle nested dependencies
         # Extract in dependency order
     ```
   - Build dependency graph: which CSE candidates contain others
   - Topologically sort CSE candidates
   - Extract in proper order (innermost first)
   - Unit tests: 10 test cases
   - Test file: `tests/unit/test_cse_advanced.py`

4. **Implement multiplicative CSE (T5.3)** (1h)
   - **T5.3: Multiplicative CSE** (common factors across multiplications)
   - File: `src/ir/transformations/cse_advanced.py` (extend)
   - Algorithm:
     ```python
     def multiplicative_cse(expr):
         # Extract common multiplication patterns
         # Example: (a*b)*c + (a*b)*d → t1 = a*b; t1*c + t1*d
         # Identify multiplication patterns across terms
         # Extract common factors as CSE
     ```
   - Integrate with factoring pass (avoid conflicts)
   - Cost-benefit analysis: only extract if beneficial
   - Unit tests: 10 test cases

### Late Afternoon (1 hour): Day 7 Checkpoint

5. **Run CI validation** (1h)
   - Create test PR with dummy change
   - Run full CI workflow
   - Measure runtime: **Target <3 minutes**
   - Verify matrix parallelization working (10 jobs in parallel)
   - Check baseline comparison functional
   - Verify basic reporting shows deltas
   - Document CI performance in SPRINT_LOG.md

**Deliverables:**
- [ ] Baseline storage structure created (`baselines/` directory)
- [ ] Performance comparison script working
- [ ] Nested CSE implemented (T5.2)
- [ ] Multiplicative CSE implemented (T5.3)
- [ ] 20+ unit tests for CSE advanced features
- [ ] **Day 7 Checkpoint Complete:** CI <3 min validated
- [ ] Basic reporting functional

**Quality Checks:**
ALWAYS run these commands before committing code changes:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] CI runtime <3 minutes (70% reduction from 10 min)
  - [ ] Baselines track all 10 models
  - [ ] Comparison script detects regressions
  - [ ] Basic console output shows deltas
  - [ ] Quality checks pass
- [ ] **Check off Day 7 Checkpoint criteria in PLAN.md:**
  - [ ] CI workflow running in <3 minutes ✓
  - [ ] Matrix builds parallelizing 10 models ✓
  - [ ] Performance baselines tracking ✓
  - [ ] Multi-metric thresholds configured (basic) ✓
  - [ ] CSE T5.2 and T5.3 implemented ✓
- [ ] Mark Day 7 as complete in `docs/planning/EPIC_2/SPRINT_11/PLAN.md`
- [ ] Check off Day 7 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md`:
  - Add PR entry to Day 7 section
  - Document CI performance metrics
  - Note checkpoint decision

**Checkpoint Decision Matrix:**

| Result | Status | Action |
|--------|--------|--------|
| CI <3 min | ✅ On Track | Proceed to Phase 5 (Day 8) |
| CI 3-5 min | ⚠️ Acceptable | Document findings, proceed |
| CI >5 min | ❌ Behind | **Reduce to 5 canary models or defer to nightly** |

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 11 Day 7: CHECKPOINT - Performance Baselines + CSE Advanced + CI <3min" \
                --body "Completes Day 7 tasks and Checkpoint from Sprint 11 PLAN.md

   🎯 DAY 7 CHECKPOINT ACHIEVED:
   - CI workflow running in <3 minutes
   - Matrix builds parallelizing 10 models
   - Performance baselines tracking
   
   - Baseline storage structure created
   - Performance comparison script working
   - T5.2: Nested CSE implemented
   - T5.3: Multiplicative CSE implemented
   - 20+ unit tests passing" \
                --base main
   ```
2. Request a review from Copilot
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_11/PLAN.md` (lines 850-1000)
- `docs/planning/EPIC_2/SPRINT_11/transformation_catalog.md` (CSE section)

---

## Day 8 Prompt: CSE Aliasing + Multi-Metric Thresholds + Diagnostics + CI Polish

**Branch:** Create a new branch named `sprint11-day8-cse-aliasing-diagnostics` from `main`

**Objective:** Complete CSE advanced, finalize CI infrastructure, implement diagnostics mode

**Effort:** 5 hours (1h CSE + 1h CI + 2h diagnostics + 1h CI polish)

**Prerequisites:**
- Day 7 must be complete (baselines + CSE T5.2-T5.3 implemented)
- Read `docs/planning/EPIC_2/SPRINT_11/PLAN.md` Day 8 section
- Review diagnostics requirements
- Understand JSON output format requirements

**Tasks to Complete (5 hours):**

### Morning (1 hour): CSE Aliasing Completion

1. **Implement CSE with aliasing (T5.4)** (1h)
   - **T5.4: CSE with Aliasing** (variable substitution awareness)
   - File: `src/ir/transformations/cse_advanced.py` (extend)
   - Algorithm:
     ```python
     def cse_with_aliasing(expr, symbol_table):
         # Track variable substitutions to avoid introducing CSE for aliased expressions
         # Example: If t1 = x+y and later z = x+y, recognize z as alias
         # Don't create new CSE for z, use existing t1
         # Integrate with symbol table for tracking
     ```
   - Track variable substitutions in symbol table
   - Avoid introducing CSE for already-aliased expressions
   - Recognize when an expression is already assigned to a variable
   - Unit tests: 10 test cases
   - Test file: `tests/unit/test_cse_advanced.py` (extend)

### Mid-Morning (1 hour): Multi-Metric Thresholds

2. **Add convert_rate tracking** (45 min)
   - File: `scripts/measure_parse_rate.py` (extend existing)
   - Add `measure_convert_rate()` function:
     ```python
     def measure_convert_rate(models):
         # Track: parse success + IR generation + MCP generation
         # Convert rate = (fully converted models) / (total models)
         pass
     ```
   - Track three stages:
     - Parse success (existing)
     - IR generation success (new)
     - MCP generation success (new)
   - Update baseline format to include both metrics
   - Test on all 10 models

3. **Add multi-metric thresholds** (15 min)
   - File: `.github/workflows/gamslib-regression.yml` (extend)
   - Add threshold checks:
     ```yaml
     - name: Check parse rate
       run: |
         if [ "$PARSE_DELTA" -gt 10 ]; then exit 1; fi
         if [ "$PARSE_DELTA" -gt 5 ]; then echo "WARNING"; fi
     - name: Check convert rate
       run: |
         if [ "$CONVERT_DELTA" -gt 10 ]; then exit 1; fi
     - name: Check performance
       run: |
         if [ "$PERF_DELTA" -gt 50 ]; then exit 1; fi
     ```
   - Thresholds:
     - Parse rate: 5% warn, 10% fail
     - Convert rate: 5% warn, 10% fail
     - Performance: 20% warn, 50% fail
   - Per-model status tracking

### Afternoon (2 hours): Diagnostics (Text + JSON)

4. **Create diagnostics infrastructure with text output** (1h)
   - File: `src/ir/diagnostics.py` (create new file)
   - Track 5 pipeline stages:
     1. Parse (lexer + parser)
     2. Semantic (resolver + symbol table)
     3. Simplification (with pass-level breakdowns)
     4. IR Generation (AST → IR)
     5. MCP Generation (IR → MCP JSON)
   - Use `time.perf_counter()` for high-resolution timing
   - Store metrics in structured format:
     ```python
     @dataclass
     class StageMetrics:
         name: str
         time_ms: float
         memory_mb: Optional[float] = None
         details: Optional[dict] = None
     ```
   - Text table output with box-drawing characters:
     ```
     ┌────────────────────┬──────────┐
     │ Stage              │ Time     │
     ├────────────────────┼──────────┤
     │ Parse              │ 45 ms    │
     │ Semantic           │ 12 ms    │
     │ Simplification     │ 230 ms   │
     │   - Pass 1         │ 45 ms    │
     │   - Pass 2         │ 38 ms    │
     │ IR Generation      │ 67 ms    │
     │ MCP Generation     │ 89 ms    │
     └────────────────────┴──────────┘
     ```
   - Add `--diagnostics` flag to CLI

5. **Add JSON diagnostics output** (1h)
   - File: `src/ir/diagnostics.py` (extend)
   - Add `--diagnostic-json` flag
   - JSON format for automation/dashboards:
     ```json
     {
       "model": "circle.gms",
       "timestamp": "2024-01-15T10:30:00Z",
       "stages": {
         "parse": {
           "time_ms": 45,
           "memory_mb": 12,
           "success": true
         },
         "semantic": {
           "time_ms": 12,
           "memory_mb": 3,
           "success": true
         },
         "simplification": {
           "time_ms": 230,
           "passes": [
             {"name": "factoring", "time_ms": 45, "transforms": 3},
             {"name": "fractions", "time_ms": 38, "transforms": 2}
           ]
         },
         "ir_generation": {"time_ms": 67, "success": true},
         "mcp_generation": {"time_ms": 89, "success": true}
       },
       "total_time_ms": 443
     }
     ```
   - Include all metrics: timing, memory, transformation counts
   - Validate JSON output with schema
   - Test on all 10 models

### Late Afternoon (1 hour): CI Polish

6. **Add PR comment reporting** (1h)
   - File: `.github/workflows/gamslib-regression.yml` (extend)
   - Format PR comments with markdown tables:
     ```markdown
     ## GAMSLib Regression Results
     
     | Model | Parse Rate | Convert Rate | Performance | Status |
     |-------|-----------|--------------|-------------|--------|
     | circle | 100% (✓) | 100% (✓) | +2% (✓) | ✅ PASS |
     | maxmin | 100% (✓) | 95% (⚠️) | +15% (⚠️) | ⚠️ WARN |
     
     **Summary:** 9/10 models passing, 1 warning
     ```
   - Show parse/convert rate changes with delta
   - Show performance regression warnings with percentage
   - Link to detailed logs in workflow artifacts
   - Color coding: ✅ pass, ⚠️ warn, ❌ fail

**Deliverables:**
- [ ] CSE with aliasing implemented (T5.4)
- [ ] **ALL CSE features complete** (T5.1-T5.4)
- [ ] Convert rate tracking implemented
- [ ] Multi-metric thresholds enforced
- [ ] Diagnostics text output with formatting
- [ ] Diagnostics JSON output implemented
- [ ] PR comment reporting working

**Quality Checks:**
ALWAYS run these commands before committing code changes:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Both parse_rate and convert_rate reported
  - [ ] Multi-metric thresholds working
  - [ ] 5 pipeline stages timed
  - [ ] <2% overhead for timing
  - [ ] Text output functional with formatting
  - [ ] JSON output validated
  - [ ] Quality checks pass
- [ ] Mark Day 8 as complete in `docs/planning/EPIC_2/SPRINT_11/PLAN.md`
- [ ] Check off Day 8 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md`:
  - Add PR entry to Day 8 section
  - Document CSE completion
  - Note diagnostics performance overhead

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 11 Day 8: CSE Aliasing + Multi-Metric + Diagnostics + CI Polish" \
                --body "Completes Day 8 tasks from Sprint 11 PLAN.md

   🎉 CSE Advanced Complete:
   - T5.4: CSE with Aliasing implemented
   - All CSE features (T5.1-T5.4) working
   
   🎯 CI Infrastructure Complete:
   - Convert rate tracking
   - Multi-metric thresholds (parse/convert/perf)
   - PR comment reporting
   
   📊 Diagnostics Mode:
   - Text output with formatting
   - JSON output for automation
   - <2% overhead" \
                --base main
   ```
2. Request a review from Copilot
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_11/PLAN.md` (lines 1000-1100)
- `docs/planning/EPIC_2/SPRINT_11/transformation_catalog.md` (CSE section)

---

## Day 9 Prompt: Integration Testing + Buffer Time

**Branch:** Create a new branch named `sprint11-day9-integration-testing` from `main`

**Objective:** Validate all features together and use buffer time for adjustments/enhancements

**Effort:** 3.5 hours (1.5h integration + 2h buffer available)

**Prerequisites:**
- Day 8 must be complete (all features implemented)
- All Sprint 11 features ready for integration testing
- Review complete feature list from PLAN.md

**Tasks to Complete (3.5 hours):**

### Morning (1.5 hours): Integration Testing

1. **Run full integration tests** (1h)
   - Test all Sprint 11 features together:
     - **maxmin.gms parsing:** Verify 100% parse rate maintained
     - **Aggressive simplification:** Test all 10 transformations (6 HIGH + 4 MEDIUM) + CSE
     - **CI guardrails:** Verify matrix builds, baselines, thresholds working
     - **Diagnostics output:** Test both text and JSON formats
   - Verify no feature interactions cause issues:
     - Simplification + CSE interaction
     - Nested indexing + simplification
     - Performance tracking + diagnostics
   - Run full test suite: `make test`
   - Benchmark all features together on all 10 Tier 1 models
   - Measure combined overhead (<5% target)

2. **Document integration results** (30 min)
   - File: `docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md`
   - Record integration test results:
     - Parse rate table (all 10 models)
     - Term reduction table (all 10 models)
     - CI performance (runtime)
     - Diagnostics overhead
   - Note any issues or unexpected interactions
   - Validate all success criteria progress:
     - [ ] 100% Tier 1 parse rate (10/10 models)
     - [ ] ≥20% term reduction on ≥50% models (5/10)
     - [ ] CI <3 minutes
     - [ ] All 10 simplification transformations working
     - [ ] All CSE advanced features working
     - [ ] Diagnostics text + JSON output
   - Prepare for Day 10 final validation

### Afternoon (2 hours): Buffer Time Available

**Buffer Usage Options:**

1. **Priority 1: Address integration issues** (if any found)
   - Fix any bugs discovered in integration testing
   - Resolve feature interaction problems
   - Performance optimization if overhead >5%

2. **Priority 2: Additional test coverage** (if integration passes)
   - Add edge case tests for complex models
   - Test feature interactions explicitly
   - Add performance regression tests

3. **Priority 3: Feature interaction tests** (if time permits)
   - Test simplification with nested indexing
   - Test CSE with complex expressions
   - Test diagnostics with all features enabled

4. **Priority 4: Polish documentation** (if all above complete)
   - Update feature documentation
   - Add usage examples
   - Improve CLI help text

5. **Priority 5: Sprint 12 prep** (if buffer unused)
   - Review deferred items
   - Plan next sprint priorities
   - Document lessons learned

**Deliverables:**
- [ ] Integration tests passing
- [ ] All features validated together
- [ ] No feature interaction issues
- [ ] Integration results documented in SPRINT_LOG.md
- [ ] 2h buffer available for adjustments or enhancements

**Quality Checks:**
For code changes only (documentation updates can skip these):
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] All integration tests pass
  - [ ] Features work together correctly
  - [ ] No unexpected interactions
  - [ ] Quality checks pass (if code changed)
- [ ] Mark Day 9 as complete in `docs/planning/EPIC_2/SPRINT_11/PLAN.md`
- [ ] Check off Day 9 in `README.md`
- [ ] Log progress to `CHANGELOG.md`
- [ ] Log progress to `docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md`:
  - Add Day 9 section
  - Document integration test results
  - Note buffer usage (if any)
  - List any issues found and resolved

**Buffer Usage Check:**

At end of Day 9, assess buffer usage:
- **If buffer unused:** Consider adding polish (formatting, PR comments, additional tests)
- **If buffer used:** Validate recovery successful, document what was fixed
- **If buffer exhausted:** Confirm core goals met, document any deferrals to Sprint 12

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 11 Day 9: Integration Testing + [Buffer Usage Summary]" \
                --body "Completes Day 9 tasks from Sprint 11 PLAN.md

   ✅ Integration Testing Complete:
   - All Sprint 11 features validated together
   - No feature interaction issues
   - Combined overhead <5%
   
   📊 Integration Results:
   - Parse rate: 10/10 models at 100%
   - Term reduction: [X]/10 models at ≥20%
   - CI runtime: [X] minutes
   
   [Add buffer usage details if applicable]" \
                --base main
   ```
2. Request a review from Copilot
3. Address all review comments
4. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_11/PLAN.md` (Day 9 section)
- `docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md` (integration results)

---

## Day 10 Prompt: Final Validation + Retrospective + Buffer

**Branch:** Create a new branch named `sprint11-day10-final-validation` from `main`

**Objective:** Final validation, complete documentation, and Sprint 11 retrospective

**Effort:** 4.5 hours (1.5h validation + 1h retrospective + 2.5h buffer available)

**Prerequisites:**
- Day 9 must be complete (integration testing passed)
- All Sprint 11 features implemented and tested
- SPRINT_LOG.md updated through Day 9

**Tasks to Complete (4.5 hours):**

### Morning (1.5 hours): Final Validation & Documentation

1. **Final validation** (1h)
   - Run full test suite: `make test`
   - Verify all quality checks: `make typecheck lint format`
   - Run benchmark suite on all 10 Tier 1 models
   - Validate all success criteria met:
     - [ ] **100% Tier 1 parse rate (10/10 models)**
     - [ ] **≥20% term reduction on ≥50% models (5/10 models)**
     - [ ] **CI <3 minutes**
     - [ ] **All 10 simplification transformations working**
     - [ ] **All CSE advanced features (T5.2-T5.4) working**
     - [ ] **Diagnostics text + JSON output**
   - Document final metrics in table format
   - Confirm buffer usage and outcomes

2. **Update documentation** (30 min)
   - File: `docs/FEATURES.md`
   - Update with Sprint 11 features:
     ```markdown
     ## Nested Indexing Support (Sprint 11)
     
     - Supports maxmin.gms with nested/subset indexing
     - Grammar extension for subset syntax: `i(j)`, `i(j(k))`
     - Semantic resolution with eager expansion
     - 100% Tier 1 parse rate (10/10 models)
     
     ## Aggressive Simplification (Sprint 11)
     
     ### HIGH Priority Transformations (6)
     - T1.1: Common factor extraction
     - T1.4: Fraction combining
     - T2.1: Associativity normalization
     - T3.1: Division simplification
     - T1.2: Multi-term factoring
     - Enhanced like-term collection
     
     ### MEDIUM Priority Transformations (4)
     - T2.2: Nested product simplification
     - T2.3: Power expression consolidation
     - T2.4: Trigonometric identities
     - T2.5: Logarithm simplification
     
     ### CSE Advanced Features (Sprint 11)
     - T5.2: Nested CSE (subexpression dependencies)
     - T5.3: Multiplicative CSE (common factors)
     - T5.4: CSE with Aliasing (substitution awareness)
     
     ## CI Regression Guardrails (Sprint 11)
     
     - Matrix builds for parallelization (10 models in parallel)
     - Performance baseline tracking (rolling + golden)
     - Multi-metric thresholds (parse/convert/performance)
     - PR comment reporting with markdown tables
     - CI runtime: <3 minutes (70% reduction)
     
     ## Diagnostics Mode (Sprint 11)
     
     - Stage-level timing (5 pipeline stages)
     - Text output with box-drawing formatting
     - JSON output for automation
     - Pass-level breakdowns for simplification
     - <2% overhead
     
     ### Usage:
     ```bash
     # Text output
     nlp2mcp convert model.gms --diagnostics
     
     # JSON output
     nlp2mcp convert model.gms --diagnostic-json > diagnostics.json
     
     # Simplification stats
     nlp2mcp convert model.gms --simplification-stats
     ```
     ```
   - Document configuration options
   - Add CLI flags documentation
   - Update usage examples

### Mid-Morning to Afternoon (1 hour): Sprint Retrospective

3. **Sprint retrospective** (1h)
   - File: `docs/planning/EPIC_2/SPRINT_11/RETROSPECTIVE.md`
   - Create comprehensive retrospective:
     
     **What Went Well:**
     - List successes and smooth implementations
     - Note any ahead-of-schedule work
     - Highlight effective processes
     
     **What Could Improve:**
     - List challenges and blockers
     - Note any behind-schedule work
     - Identify process improvements
     
     **Lessons Learned:**
     - Technical insights from implementation
     - Process insights from sprint execution
     - Risk management lessons
     
     **Action Items for Sprint 12:**
     - Process improvements to implement
     - Technical debt to address
     - Planning adjustments needed
     
     **Effort Analysis:**
     - Compare actual vs planned hours (45h planned)
     - Breakdown by phase and feature
     - Analyze buffer usage effectiveness (5h available)
     - Note any scope changes or adjustments
     
     **Checkpoint Outcomes:**
     - Day 3: 100% Tier 1 parse rate achieved (✅/⚠️/❌)
     - Day 5: ≥20% term reduction achieved (✅/⚠️/❌)
     - Day 7: CI <3 minutes achieved (✅/⚠️/❌)
     
     **Success Metrics:**
     - Parse rate: [X]/10 models at 100%
     - Term reduction: [X]/10 models at ≥20%
     - CI runtime: [X] minutes
     - All transformations: [X]/10 working
     - All CSE features: [X]/4 working

### Afternoon (2.5 hours): Contingency Reserve / Final Buffer

**Allocated for:**

1. **FIRST priority:** Maxmin overruns from Days 1-3 (if checkpoint failed)
2. **SECOND priority:** Simplification bug fixes from Day 5 checkpoint (if <20% reduction)
3. **THIRD priority:** CSE implementation issues from Days 7-8 (if complex bugs found)
4. **FOURTH priority:** CI performance issues from Day 7 checkpoint (if >3 min)
5. **FIFTH priority:** Feature interaction tests (if all above complete)
6. **SIXTH priority:** Additional test coverage, documentation polish, or Sprint 12 prep

**Note:** Combined with Day 9 buffer (2h), total 4.5h buffer available across Days 9-10

**Deliverables:**
- [ ] All success criteria validated
- [ ] `docs/FEATURES.md` updated with all Sprint 11 features
- [ ] Retrospective complete with detailed analysis
- [ ] Buffer usage documented
- [ ] **🎉 Sprint 11 COMPLETE**

**Quality Checks:**
For code changes only (documentation updates can skip these):
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] 100% Tier 1 parse rate achieved (10/10 models)
  - [ ] ≥20% term reduction on ≥50% models (5/10 models)
  - [ ] CI <3 minutes
  - [ ] All tests pass
  - [ ] Documentation complete
  - [ ] Retrospective identifies improvements
- [ ] Mark Day 10 as complete in `docs/planning/EPIC_2/SPRINT_11/PLAN.md`
- [ ] Check off Day 10 in `README.md`
- [ ] Update `CHANGELOG.md` with Sprint 11 summary
- [ ] Final update to `docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md`:
  - Add Day 10 section
  - Mark sprint complete
  - Document final metrics
  - Note total buffer usage across Days 9-10
  - Link to RETROSPECTIVE.md

**Final Success Criteria Validation:**

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Tier 1 Parse Rate | 10/10 (100%) | [X]/10 | ✅/⚠️/❌ |
| Term Reduction | ≥5/10 at ≥20% | [X]/10 | ✅/⚠️/❌ |
| CI Runtime | <3 minutes | [X] min | ✅/⚠️/❌ |
| Transformations | 10/10 working | [X]/10 | ✅/⚠️/❌ |
| CSE Features | 4/4 working | [X]/4 | ✅/⚠️/❌ |
| Diagnostics | Text + JSON | ✅/❌ | ✅/❌ |
| All Tests | Pass | Pass/Fail | ✅/❌ |

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 11 Day 10: Final Validation + Retrospective + Documentation" \
                --body "Completes Sprint 11 Day 10 and FINAL SPRINT VALIDATION

   🎉 SPRINT 11 COMPLETE - Tier 1 Coverage + Quality Infrastructure

   ✅ Final Success Criteria:
   - Parse rate: [X]/10 models at 100%
   - Term reduction: [X]/10 models at ≥20%
   - CI runtime: [X] minutes
   - All 10 transformations working
   - All 4 CSE features working
   - Diagnostics text + JSON output
   
   📚 Documentation Updated:
   - FEATURES.md with all Sprint 11 features
   - RETROSPECTIVE.md with lessons learned
   - SPRINT_LOG.md final update
   
   📊 Buffer Usage:
   - Day 9: [X]h used
   - Day 10: [X]h used
   - Total: [X]/5h used" \
                --base main
   ```
2. Request a review from Copilot
3. Address all review comments
4. Once approved, merge the PR

**Sprint 11 Completion Checklist:**
- [ ] All Day 10 tasks complete
- [ ] All checkpoints passed (Days 3, 5, 7)
- [ ] All success criteria met
- [ ] Documentation updated
- [ ] Retrospective written
- [ ] Buffer usage documented
- [ ] SPRINT_LOG.md finalized
- [ ] Ready for Sprint 12 planning

**🎉 Milestone: SPRINT 11 COMPLETE**

Sprint 11 achieved:
- 100% Tier 1 parse rate coverage (10/10 models including maxmin.gms)
- Aggressive simplification with 10 transformations (6 HIGH + 4 MEDIUM)
- CSE advanced features (T5.2-T5.4)
- CI regression guardrails (<3 min runtime)
- Diagnostics mode (text + JSON)
- Quality infrastructure for future sprints

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_11/PLAN.md` (Day 10 section)
- `docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md` (full sprint log)

---

## Usage Instructions

### How to Use These Prompts

1. **At the start of each day:**
   - Read the corresponding day's prompt in full
   - Create the specified branch from `main`
   - Review all prerequisite documents
   - Follow the task breakdown with time estimates

2. **During development:**
   - Complete tasks in order (unless dependencies allow parallelism)
   - Run quality checks frequently (typecheck, lint, test)
   - Update SPRINT_LOG.md incrementally as you complete tasks
   - Document any deviations or challenges

3. **At checkpoint days (Days 3, 5, 7):**
   - Complete all validation tasks
   - Document checkpoint results in SPRINT_LOG.md
   - Follow checkpoint decision matrix
   - Activate buffer if needed

4. **At day completion:**
   - Verify all deliverables complete
   - Run all quality checks
   - Update documentation (PLAN.md, README.md, CHANGELOG.md, SPRINT_LOG.md)
   - Create pull request with provided template
   - Request Copilot review

5. **Quality checks:**
   - Always run for code changes: `make typecheck lint format test`
   - Can skip for documentation-only commits
   - Never commit code that fails quality checks

6. **Documentation updates:**
   - Update SPRINT_LOG.md after each PR merge (5-10 min)
   - See `docs/planning/EPIC_2/SPRINT_11/incremental_documentation_guide.md` for templates
   - Keep parse rate tables and metrics current

7. **Buffer management:**
   - Days 9-10 have 4.5h total buffer
   - Use for overruns, bug fixes, or enhancements
   - Document buffer usage in SPRINT_LOG.md

### Key Principles

- **Incremental progress:** Complete one task fully before moving to next
- **Quality first:** Never compromise on tests or type safety
- **Documentation:** Keep SPRINT_LOG.md current throughout sprint
- **Checkpoint-driven:** Validate progress at Days 3, 5, 7
- **Buffer awareness:** Know when to activate contingency time

---

**End of Sprint 11 Prompts**


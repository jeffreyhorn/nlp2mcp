# Sprint 11 Preparation Task Prompts

This document contains detailed, copy-paste ready prompts for executing Sprint 11 Prep Tasks 2-12. Each prompt is self-contained with full context, instructions, and quality gates.

---

# Task 2: Research maxmin.gms Nested/Subset Indexing

**Priority:** Critical  
**Estimated Time:** 6 hours  
**Unknowns Verified:** 2.1, 2.2, 2.3, 2.4  
**Dependencies:** Task 1 (Known Unknowns)

## Task Context

### Objective

Research GAMS nested/subset indexing semantics, analyze maxmin.gms blocker in detail, and design implementation approach for achieving 100% Tier 1 parse rate.

### Why This Matters

maxmin.gms is the final GAMSLIB Tier 1 model at 18% parse rate (complexity 9/10). Unlocking this model achieves 100% Tier 1 coverage, completing Epic 2's primary parser goal.

Sprint 10 deferred maxmin.gms due to high complexity and risk. Sprint 11 allocates dedicated research and 8-12 hours implementation time.

### Background

**Current Status:**
- Parse rate: 90% (9/10 models)
- maxmin.gms: 18% parsed (main blocker: nested/subset indexing)
- Complexity: 9/10 (highest of all Tier 1 models)

**From Sprint 10 Retrospective:**
> "Plan maxmin.gms Implementation - Dedicated research phase for nested/subset indexing. Prototype approach before full implementation. Budget: 8-12 hours for complexity 9/10 feature."

**Prior Analysis:**
- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/` may contain maxmin analysis
- Nested indexing involves subset conditions in equation domains
- Example: `Equation balance(i) $(subset(i)).. ...` or similar

### What Needs to Be Done

**1. Analyze maxmin.gms in Detail (2 hours)**
   - Download maxmin.gms from GAMSLIB
   - Identify all instances of nested/subset indexing
   - Document syntax patterns used
   - Identify which lines fail to parse (vs. parse correctly)
   - Create minimal reproducible examples for each pattern

**2. Research GAMS Nested/Subset Indexing Semantics (2 hours)**
   - Read GAMS documentation on subset indexing
   - Research conditional set operations (`$` operator)
   - Understand dynamic vs. static subsets
   - Research nested index scoping rules
   - Find examples in GAMS forums/documentation
   - Document edge cases (empty subsets, complex conditions)

**3. Design AST Representation (1 hour)**
   - How to represent subset conditions in AST?
   - Does `Set` node need `condition` field?
   - How to represent `$` operator in equation domains?
   - How to handle nested indices in `IndexedExpr`?
   - Update AST node definitions if needed

**4. Design Implementation Approach (1 hour)**
   - Grammar changes needed (parser rules for `$` operator)
   - Semantic analyzer changes (subset condition evaluation)
   - IR representation (how `Parameter`/`Equation` store conditions)
   - MCP generation (how subset conditions affect equation instances)
   - Test strategy (unit tests, integration tests, maxmin.gms end-to-end)

**5. Prototype if Time Permits**
   - Create minimal grammar rule for subset syntax
   - Test parsing simple subset examples
   - Validate approach before full implementation

## Deliverables

- Research document with GAMS nested/subset indexing semantics
- Implementation plan with grammar, AST, semantic, IR, MCP changes
- Minimal reproducible test cases for each pattern
- Complexity and risk assessment
- Estimated implementation time (should be 8-12 hours based on research)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.1, 2.2, 2.3, 2.4

## Instructions

### 1. Execute Task Work

1. **Download and analyze maxmin.gms** (2 hours):
   - Get maxmin.gms from GAMSLIB
   - Parse and identify all nested/subset indexing instances
   - Document syntax patterns
   - Create minimal test cases

2. **Research GAMS semantics** (2 hours):
   - Read GAMS documentation on subset indexing and `$` operator
   - Research dynamic vs. static subsets
   - Find example usage in GAMS community
   - Document edge cases

3. **Design AST representation** (1 hour):
   - Define how to represent subset conditions
   - Design AST node changes if needed

4. **Design implementation approach** (1 hour):
   - Document grammar, semantic, IR, and MCP changes
   - Create test strategy
   - Estimate implementation effort (should be 8-12 hours)

5. **Create deliverables**:
   - `docs/research/nested_subset_indexing_research.md`
   - `docs/planning/EPIC_2/SPRINT_11/maxmin_implementation_plan.md`
   - `tests/synthetic/nested_subset_indexing.gms`

### 2. Update KNOWN_UNKNOWNS.md

Update `docs/planning/EPIC_2/SPRINT_11/KNOWN_UNKNOWNS.md` for Unknowns 2.1, 2.2, 2.3, 2.4:

**Unknown 2.1: GAMS Subset Syntax Patterns**
- Change status from 🔍 INCOMPLETE to ✅ VERIFIED or ❌ WRONG
- Add 50-100 lines in "Verification Results" section:
  - **Finding:** Document all subset syntax patterns found in maxmin.gms
  - **Evidence:** Code examples, line numbers, pattern frequency
  - **Decision:** Which patterns to support in Sprint 11
  - **Impact:** Grammar rules needed, implementation complexity

**Unknown 2.2: Nested Index Semantics**
- Change status and add verification results
- **Finding:** How nested indices are resolved and scoped
- **Evidence:** GAMS documentation, test examples
- **Decision:** AST representation approach
- **Impact:** Semantic analyzer complexity

**Unknown 2.3: Subset Condition Evaluation**
- Change status and add verification results
- **Finding:** When and how subset conditions are evaluated (static vs dynamic)
- **Evidence:** GAMS semantics, execution model
- **Decision:** IR representation for conditions
- **Impact:** MCP generation approach

**Unknown 2.4: Implementation Complexity**
- Change status and add verification results
- **Finding:** Confirmed effort estimate (should be 8-12 hours)
- **Evidence:** Grammar changes, AST changes, semantic changes, test requirements
- **Decision:** GO/NO-GO for Sprint 11
- **Impact:** Sprint 11 schedule allocation

### 3. Update PREP_PLAN.md

Update `docs/planning/EPIC_2/SPRINT_11/PREP_PLAN.md`:

1. **Change task status:** `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`

2. **Fill in Changes section:**
```markdown
### Changes

**Files Created:**
- `docs/research/nested_subset_indexing_research.md` (research findings)
- `docs/planning/EPIC_2/SPRINT_11/maxmin_implementation_plan.md` (implementation design)
- `tests/synthetic/nested_subset_indexing.gms` (minimal test case)

**Files Updated:**
- `docs/planning/EPIC_2/SPRINT_11/KNOWN_UNKNOWNS.md` (Unknowns 2.1-2.4 verified)
- `docs/planning/EPIC_2/SPRINT_11/PREP_PLAN.md` (Task 2 status, Changes, Result, acceptance criteria)
```

3. **Fill in Result section** (3-5 paragraphs summarizing findings, decisions, and Sprint 11 impact)

4. **Check off all acceptance criteria** (change `- [ ]` to `- [x]`)

### 4. Update CHANGELOG.md

Add to the top of `## [Unreleased]` section:

```markdown
### Sprint 11: Prep Phase - Task 2: Research maxmin.gms Nested/Subset Indexing - YYYY-MM-DD

**Status:** ✅ COMPLETE

#### Summary

Researched GAMS nested/subset indexing semantics, analyzed maxmin.gms in detail, and designed implementation approach. Confirmed 8-12 hour implementation budget is realistic. Created comprehensive implementation plan with grammar, AST, semantic, IR, and MCP changes documented.

#### Achievements

**maxmin.gms Analysis (2 hours):**
- ✅ Downloaded and analyzed maxmin.gms (108 lines)
- ✅ Identified [N] instances of nested/subset indexing
- ✅ Documented [N] distinct syntax patterns
- ✅ Created minimal reproducible test cases for each pattern

**GAMS Semantics Research (2 hours):**
- ✅ Researched GAMS documentation on subset indexing
- ✅ Documented `$` operator semantics (conditional set operations)
- ✅ Understood dynamic vs. static subsets
- ✅ Identified edge cases (empty subsets, complex conditions, nested levels)

**Implementation Design (2 hours):**
- ✅ Designed AST representation for subset conditions
- ✅ Documented grammar changes (parser rules for `$` operator)
- ✅ Documented semantic analyzer changes (subset condition evaluation)
- ✅ Documented IR representation (how equations store conditions)
- ✅ Documented MCP generation approach (subset filtering)
- ✅ Created test strategy (unit, integration, end-to-end)

#### Deliverables

- `docs/research/nested_subset_indexing_research.md` - Comprehensive research document
- `docs/planning/EPIC_2/SPRINT_11/maxmin_implementation_plan.md` - Implementation plan
- `tests/synthetic/nested_subset_indexing.gms` - Minimal test case
- Updated KNOWN_UNKNOWNS.md (Unknowns 2.1-2.4 verified)

#### Key Findings

**Subset Syntax Patterns:**
[Describe the patterns found in maxmin.gms, e.g., "defdist(low(n,nn)).. ", "mindist1(low).. "]

**GAMS Semantics:**
[Describe how subset indexing works, e.g., "2D subset declaration with assignment, equation domain restriction, shorthand form"]

**Implementation Complexity:**
[Confirm 8-12 hour estimate, break down by component: grammar 3-4h, AST 2-3h, semantic 4-6h, tests 1-2h]

**GO/NO-GO Decision:**
[State whether to implement in Sprint 11 or defer, with rationale]

#### Unknowns Verified

- Unknown 2.1: ✅ VERIFIED - [Summary of subset syntax patterns]
- Unknown 2.2: ✅ VERIFIED - [Summary of nested index semantics]
- Unknown 2.3: ✅ VERIFIED - [Summary of subset condition evaluation]
- Unknown 2.4: ✅ VERIFIED - [Summary of implementation complexity and decision]

#### Impact on Sprint 11

**If GO Decision:**
- Days 1-3 allocated to maxmin.gms implementation
- 100% Tier 1 parse rate achievable (10/10 models)
- Day 3 checkpoint: maxmin.gms passing

**If DEFER Decision:**
- Sprint 11 maintains 90% target (9/10 models)
- maxmin.gms deferred to Sprint 12 with detailed implementation plan
- More time allocated to aggressive simplification features

#### Next Steps

- Task 3: Design Aggressive Simplification Architecture (verify Unknowns 1.2-1.11)
```

### 5. Quality Gates

No code changes in this task, skip quality gates.

### 6. Commit Changes

```bash
git add -A
git commit -m "Complete Sprint 11 Prep Task 2: Research maxmin.gms Nested/Subset Indexing

- Created nested_subset_indexing_research.md with GAMS semantics
- Created maxmin_implementation_plan.md with implementation design
- Created minimal test case: nested_subset_indexing.gms
- Updated KNOWN_UNKNOWNS.md (Unknowns 2.1, 2.2, 2.3, 2.4 verified)
- Updated PREP_PLAN.md (Task 2 complete)
- Updated CHANGELOG.md with research findings and GO/NO-GO decision"
```

### 7. Create Pull Request

```bash
gh pr create \
  --title "Sprint 11 Prep Task 2: Research maxmin.gms Nested/Subset Indexing" \
  --body "## Summary

Researched GAMS nested/subset indexing semantics and created comprehensive implementation plan for maxmin.gms. Confirmed 8-12 hour implementation budget.

## Deliverables

- Research document: nested_subset_indexing_research.md
- Implementation plan: maxmin_implementation_plan.md
- Minimal test case: nested_subset_indexing.gms
- Updated KNOWN_UNKNOWNS.md (Unknowns 2.1-2.4)

## Unknowns Verified

- Unknown 2.1: GAMS subset syntax patterns - [N] patterns documented
- Unknown 2.2: Nested index semantics - AST representation designed
- Unknown 2.3: Subset condition evaluation - IR approach defined
- Unknown 2.4: Implementation complexity - 8-12h estimate confirmed

## GO/NO-GO Decision

[State decision and rationale]

## Changes

- Created: docs/research/nested_subset_indexing_research.md
- Created: docs/planning/EPIC_2/SPRINT_11/maxmin_implementation_plan.md
- Created: tests/synthetic/nested_subset_indexing.gms
- Updated: KNOWN_UNKNOWNS.md, PREP_PLAN.md, CHANGELOG.md

## Impact on Sprint 11

[Describe how this affects Sprint 11 scheduling and goals]

## Checklist

- [x] All deliverables complete
- [x] KNOWN_UNKNOWNS.md updated (4 unknowns verified)
- [x] PREP_PLAN.md updated (status, Changes, Result, acceptance criteria)
- [x] CHANGELOG.md updated
- [x] GO/NO-GO decision documented with clear rationale
- [ ] Awaiting reviewer comments"
```

### 8. Wait for Review

**DO NOT proceed to Task 3 until:**
- Reviewer has approved the PR
- All reviewer comments have been addressed
- PR has been merged to main

---

# Task 3: Design Aggressive Simplification Architecture

**Priority:** Critical  
**Estimated Time:** 5 hours  
**Unknowns Verified:** 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 1.10, 1.11  
**Dependencies:** Task 1 (Known Unknowns)

## Task Context

### Objective

Design comprehensive architecture for aggressive simplification mode implementing distribution/factoring, fraction simplification, nested operations, and division by multiplication as specified in PROJECT_PLAN.md.

### Why This Matters

Aggressive simplification is Sprint 11's primary feature with goal of ≥20% derivative term reduction. Poor architecture risks:
- Correctness bugs (wrong algebraic transformations)
- Expression explosion (>150% size growth without benefit)
- Performance regression (>10% conversion time overhead)
- Maintenance burden (complex transformation interactions)

Upfront design prevents costly refactoring during sprint.

### Background

**From PROJECT_PLAN.md (lines 456-638):**
- 5 transformation categories with 15+ specific patterns
- 8-step transformation pipeline
- Heuristics: size limit (150%), depth limit, cancellation detection
- Validation: FD checks, PATH alignment, performance <10% overhead
- Target: ≥20% term reduction on ≥50% benchmark models

**Existing Simplification:**
- Basic: Constant folding, identity operations (already implemented)
- Advanced: Like-term combination, fraction cancellation (already implemented)
- Aggressive: NEW - factoring, fraction ops, nested ops, division transformations

### What Needs to Be Done

**1. Review Existing Simplification Code (1 hour)**
   - Read `src/ad/simplification.py` (or equivalent)
   - Understand current basic/advanced simplification passes
   - Identify extension points for aggressive transformations
   - Document current architecture (visitor pattern, passes, etc.)

**2. Design Transformation Pipeline (2 hours)**
   - Map 5 transformation categories to code modules
   - Define 8-step pipeline execution order (per PROJECT_PLAN.md line 570)
   - Design data structures for tracking transformations
   - Design metrics collection (`--simplification-stats`)
   - Define heuristic thresholds (size 150%, depth limits)
   - Design cancellation detection algorithm

**3. Design Individual Transformations (1.5 hours)**
   - **Distribution/Factoring:** Common factor detection, multi-term factoring
   - **Fraction Simplification:** Distribution over division, combining fractions, common denominator handling
   - **Nested Operations:** Associativity for constants, division chain simplification
   - **Division by Multiplication:** Constant extraction, variable extraction
   - Define pattern matching approach for each transformation
   - Define applicability conditions (when to apply vs. skip)

**4. Design Validation and Safety (0.5 hour)**
   - Finite difference validation after each transformation
   - Expression size tracking (reject if >150% growth)
   - Depth limit enforcement
   - Rollback mechanism if transformation worsens expression
   - Performance budgeting per transformation type

## Deliverables

- Architecture document with transformation pipeline design
- Transformation catalog with 15+ patterns, applicability conditions, examples
- Data structure designs for tracking transformations and metrics
- Heuristic thresholds documented with rationale
- Validation strategy (FD checks, size limits, performance budgets)
- Extension points in existing code identified
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 1.10, 1.11

## Instructions

### 1. Execute Task Work

1. **Review existing simplification code** (1 hour):
   - Read `src/ad/simplification.py`
   - Document current architecture
   - Identify extension points

2. **Design transformation pipeline** (2 hours):
   - Map 5 categories to modules
   - Define 8-step execution order
   - Design tracking data structures
   - Design metrics collection
   - Define heuristic thresholds

3. **Design individual transformations** (1.5 hours):
   - Document each transformation category
   - Define pattern matching approach
   - Define applicability conditions

4. **Design validation and safety** (0.5 hour):
   - FD validation approach
   - Size tracking and limits
   - Rollback mechanism

5. **Create deliverables**:
   - `docs/planning/EPIC_2/SPRINT_11/aggressive_simplification_architecture.md`
   - `docs/planning/EPIC_2/SPRINT_11/transformation_catalog.md`

### 2. Update KNOWN_UNKNOWNS.md

Update `docs/planning/EPIC_2/SPRINT_11/KNOWN_UNKNOWNS.md` for Unknowns 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 1.10, 1.11:

For each unknown, add verification results with:
- **Finding:** What you discovered about the transformation
- **Evidence:** Design decisions, rationale, examples
- **Decision:** How it will be implemented
- **Impact:** Complexity, risk, effort estimate

Key unknowns to verify:
- **1.2:** Transformation ordering strategy
- **1.3:** Cancellation detection before transformations
- **1.4:** Heuristics for preventing expression explosion
- **1.5:** Associativity handling with mixed operations
- **1.6:** Validation strategy sufficiency
- **1.8:** Nested operations implementation approach
- **1.10:** Division transformation applicability rules
- **1.11:** Performance overhead measurement and limits

### 3. Update PREP_PLAN.md

Update `docs/planning/EPIC_2/SPRINT_11/PREP_PLAN.md`:

1. **Change task status:** `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`

2. **Fill in Changes section:**
```markdown
### Changes

**Files Created:**
- `docs/planning/EPIC_2/SPRINT_11/aggressive_simplification_architecture.md` (architecture design)
- `docs/planning/EPIC_2/SPRINT_11/transformation_catalog.md` (15+ patterns with examples)

**Files Updated:**
- `docs/planning/EPIC_2/SPRINT_11/KNOWN_UNKNOWNS.md` (Unknowns 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 1.10, 1.11 verified)
- `docs/planning/EPIC_2/SPRINT_11/PREP_PLAN.md` (Task 3 complete)
```

3. **Fill in Result section** (3-5 paragraphs)

4. **Check off all acceptance criteria**

### 4. Update CHANGELOG.md

Add entry for Task 3 with achievements, deliverables, key findings, unknowns verified, and Sprint 11 impact.

### 5. Quality Gates

No code changes, skip quality gates.

### 6. Commit Changes

```bash
git add -A
git commit -m "Complete Sprint 11 Prep Task 3: Design Aggressive Simplification Architecture

- Created aggressive_simplification_architecture.md with 8-step pipeline
- Created transformation_catalog.md with 15+ patterns
- Updated KNOWN_UNKNOWNS.md (8 unknowns verified)
- Updated PREP_PLAN.md (Task 3 complete)
- Updated CHANGELOG.md"
```

### 7. Create Pull Request

```bash
gh pr create \
  --title "Sprint 11 Prep Task 3: Design Aggressive Simplification Architecture" \
  --body "## Summary

Designed comprehensive architecture for aggressive simplification with 8-step transformation pipeline, 15+ transformation patterns, and safety mechanisms.

## Deliverables

- Architecture document: aggressive_simplification_architecture.md
- Transformation catalog: transformation_catalog.md (15+ patterns)
- Updated KNOWN_UNKNOWNS.md (8 unknowns verified)

## Key Design Decisions

- 8-step pipeline execution order: [describe]
- Heuristic thresholds: size 150%, depth [N]
- Validation strategy: FD checks + rollback
- Performance budget: <10% overhead

## Unknowns Verified

- Unknown 1.2: Transformation ordering - [decision]
- Unknown 1.3: Cancellation detection - [approach]
- Unknown 1.4: Expression explosion prevention - [heuristics]
- Unknown 1.5: Associativity handling - [strategy]
- Unknown 1.6: Validation strategy - [FD checks sufficient]
- Unknown 1.8: Nested operations - [implementation approach]
- Unknown 1.10: Division transformations - [applicability rules]
- Unknown 1.11: Performance overhead - [measurement approach]

## Changes

- Created: aggressive_simplification_architecture.md
- Created: transformation_catalog.md
- Updated: KNOWN_UNKNOWNS.md, PREP_PLAN.md, CHANGELOG.md

## Impact on Sprint 11

Architecture ready for implementation. Estimated effort: [N] hours for all transformations.

## Checklist

- [x] Architecture covers all 5 transformation categories
- [x] 8-step pipeline designed with execution order justified
- [x] 15+ transformation patterns documented with examples
- [x] Heuristics and safety mechanisms defined
- [x] KNOWN_UNKNOWNS.md updated (8 unknowns verified)
- [x] PREP_PLAN.md updated
- [x] CHANGELOG.md updated
- [ ] Awaiting reviewer comments"
```

### 8. Wait for Review

Wait for PR approval before proceeding to Task 4.

---

# Task 4: Research Common Subexpression Elimination (CSE)

**Priority:** High  
**Estimated Time:** 4 hours  
**Unknowns Verified:** 1.9  
**Dependencies:** Task 3 (Simplification Architecture)

## Task Context

### Objective

Research CSE algorithms, design integration with aggressive simplification, and determine scope for Sprint 11 (opt-in via `--cse` flag vs. automatic).

### Why This Matters

CSE is listed as optional in PROJECT_PLAN.md but can provide significant benefits:
- Reduces redundant computation for expensive functions (exp, log, trig)
- Can reduce derivative terms through shared subexpression handling
- Complements factoring (exposes additional factoring opportunities)

However, CSE has trade-offs:
- Increases variable count (introduces temporaries)
- Complicates code generation (need to emit temporary definitions)
- Only beneficial if subexpression reused ≥2 times

Research needed to determine if Sprint 11 scope or defer to Sprint 12.

### Background

**From PROJECT_PLAN.md:**
- CSE is optional, controlled by flag
- May be deferred to later sprint or made opt-in via `--cse` flag
- Trade-off: Increases variable count; only beneficial if subexpression reused ≥2 times

**Prior Work:**
- No existing CSE implementation
- Simplification currently handles duplicates via like-term combination, not explicit temporaries

### What Needs to Be Done

**1. Research CSE Algorithms (2 hours)**
   - Classic CSE algorithms (hash-based, tree traversal)
   - Cost models (when CSE improves vs. worsens performance)
   - Reuse threshold (≥2, ≥3, cost-based?)
   - Handling of function calls vs. binary ops
   - Integration with existing compiler passes

**2. Survey CSE in Similar Tools (1 hour)**
   - Compiler optimizers (LLVM, GCC)
   - Symbolic math tools (SymPy, Mathematica)
   - Automatic differentiation tools
   - Document best practices and pitfalls

**3. Design Integration Approach (1 hour)**
   - Where in 8-step pipeline does CSE fit? (Step 8 per PROJECT_PLAN.md)
   - How to detect repeated subexpressions? (AST hashing, equality checks)
   - How to generate temporary variable names? (`cse_tmp_1`, etc.)
   - How to emit temporaries in GAMS code? (separate `Variables` block)
   - How to update derivatives after CSE? (chain rule through temporaries)
   - Flag design: `--cse`, `--cse-threshold=N`, `--cse-min-cost=X`?

**4. Scope Decision for Sprint 11**
   - Implement full CSE in Sprint 11? (risky, significant scope)
   - Implement basic CSE (function calls only) in Sprint 11?
   - Defer to Sprint 12 and focus on other transformations?
   - Document recommendation with rationale

## Deliverables

- CSE research document with algorithms, cost models, best practices
- Scope recommendation for Sprint 11 with rationale
- If Sprint 11 scope: Integration design with implementation plan
- If deferred: Justification and Sprint 12 proposal
- Updated KNOWN_UNKNOWNS.md with verification results for Unknown 1.9

## Instructions

### 1. Execute Task Work

1. **Research CSE algorithms** (2 hours)
2. **Survey similar tools** (1 hour)
3. **Design integration** (1 hour)
4. **Make scope decision** with clear rationale
5. **Create deliverables**:
   - `docs/research/cse_research.md`
   - `docs/planning/EPIC_2/SPRINT_11/cse_integration_design.md` (if Sprint 11 scope)

### 2. Update KNOWN_UNKNOWNS.md

Update Unknown 1.9 with:
- **Finding:** CSE algorithm choice, cost model, integration approach
- **Evidence:** Research from LLVM, GCC, SymPy, literature
- **Decision:** Sprint 11 full/basic/deferred with clear rationale
- **Impact:** If deferred, no Sprint 11 impact; if included, add N hours to schedule

### 3. Update PREP_PLAN.md

Update Task 4 status, Changes, Result, and acceptance criteria.

### 4. Update CHANGELOG.md

Add Task 4 entry with CSE research findings and scope decision.

### 5. Quality Gates

No code changes, skip.

### 6. Commit and Create PR

Commit with appropriate message and create PR with scope decision clearly stated.

### 7. Wait for Review

Wait for approval before proceeding to Task 5.

---

# Task 5: Prototype Factoring Algorithms

**Priority:** High  
**Estimated Time:** 5 hours  
**Unknowns Verified:** 1.1, 1.7  
**Dependencies:** Task 3 (Simplification Architecture)

## Task Context

### Objective

Prototype distribution cancellation (`x*y + x*z → x*(y + z)`) and multi-term factoring algorithms to validate approach and identify implementation challenges before Sprint 11.

### Why This Matters

Factoring is the core of aggressive simplification (Category 1 in PROJECT_PLAN.md). Prototyping de-risks Sprint 11 by:
- Validating common factor detection algorithm
- Testing pattern matching approach
- Identifying edge cases (negative factors, fractional coefficients)
- Measuring performance impact
- Confirming ≥20% term reduction is achievable

### Background

**From PROJECT_PLAN.md:**
- Distribution cancellation: `x*y + x*z → x*(y + z)`
- Multi-term factoring: `a*c + a*d + b*c + b*d → (a + b)*(c + d)`
- Reduces multiplication operations, exposes structure

**Example:**
```
Before: grad_x = 2*exp(x)*sin(y) + 2*exp(x)*cos(y)
After:  grad_x = 2*exp(x)*(sin(y) + cos(y))
Operations: 4 multiplications, 1 addition → 2 multiplications, 1 addition (50% reduction)
```

### What Needs to Be Done

**1. Implement Distribution Cancellation Prototype (2 hours)**
   - Create function `factor_common_terms(expr: BinaryOp) -> BinaryOp`
   - Detect common factors in sum terms (AST equality checks)
   - Extract common factor, create factored expression
   - Test on examples from PROJECT_PLAN.md
   - Test edge cases

**2. Implement Multi-Term Factoring Prototype (2 hours)**
   - Create function `factor_multi_terms(expr: BinaryOp) -> BinaryOp`
   - Detect common factors across term pairs
   - Group terms by common factors
   - Recursively apply factoring
   - Test on examples and edge cases

**3. Measure Performance and Effectiveness (1 hour)**
   - Run prototype on benchmark expressions
   - Measure term count reduction (target ≥20%)
   - Measure execution time (should be <1ms per expression)
   - Identify bottlenecks
   - Document findings and recommendations

## Deliverables

- Working prototype for distribution cancellation
- Working prototype for multi-term factoring
- Test suite with examples and edge cases
- Performance measurements (execution time, term count reduction)
- Results document with findings and recommendations
- Updated KNOWN_UNKNOWNS.md for Unknowns 1.1, 1.7

## Instructions

### 1. Execute Task Work

1. **Create prototype directory**: `prototypes/aggressive_simplification/`

2. **Implement distribution cancellation** (2 hours):
   - Create `factoring_prototype.py`
   - Implement `factor_common_terms()` function
   - Test on PROJECT_PLAN.md examples
   - Test edge cases

3. **Implement multi-term factoring** (2 hours):
   - Implement `factor_multi_terms()` function
   - Test on `a*c + a*d + b*c + b*d` example
   - Test edge cases

4. **Create test suite**:
   - Create `test_factoring.py`
   - Test examples from PROJECT_PLAN.md
   - Test edge cases

5. **Measure performance** (1 hour):
   - Run on benchmark expressions
   - Measure term reduction (target ≥20%)
   - Measure execution time (<1ms target)
   - Document findings

6. **Create deliverables**:
   - `prototypes/aggressive_simplification/factoring_prototype.py`
   - `prototypes/aggressive_simplification/test_factoring.py`
   - `docs/planning/EPIC_2/SPRINT_11/factoring_prototype_results.md`

### 2. Update KNOWN_UNKNOWNS.md

Update Unknowns 1.1 and 1.7:

**Unknown 1.1: Common Factor Detection Algorithm**
- **Finding:** Prototype results, AST equality approach works/doesn't work
- **Evidence:** Test results, performance measurements
- **Decision:** Algorithm to use in Sprint 11 implementation
- **Impact:** Complexity estimate for Sprint 11

**Unknown 1.7: Factoring Performance**
- **Finding:** Measured execution time and term reduction
- **Evidence:** Benchmark results, bottleneck analysis
- **Decision:** Performance acceptable for Sprint 11
- **Impact:** No performance concerns or optimizations needed

### 3. Update PREP_PLAN.md

Update Task 5 status, Changes, Result, and acceptance criteria.

### 4. Update CHANGELOG.md

Add Task 5 entry with prototype results and performance findings.

### 5. Quality Gates

**IMPORTANT:** This task involves code. Run quality gates:

```bash
make typecheck && make lint && make format && make test
```

All checks must pass before committing.

### 6. Commit and Create PR

```bash
git add -A
git commit -m "Complete Sprint 11 Prep Task 5: Prototype Factoring Algorithms

- Created factoring_prototype.py with distribution cancellation
- Created factoring_prototype.py with multi-term factoring
- Created test_factoring.py with comprehensive tests
- Created factoring_prototype_results.md with performance analysis
- Achieved [N]% term reduction on test cases
- Execution time: [N]ms per expression
- Updated KNOWN_UNKNOWNS.md (Unknowns 1.1, 1.7 verified)
- Updated PREP_PLAN.md (Task 5 complete)
- Updated CHANGELOG.md"
```

Create PR with prototype results and performance metrics clearly stated.

### 7. Wait for Review

Wait for approval before proceeding to Task 6.

---

# Task 6: Survey CI Regression Frameworks

**Priority:** High  
**Estimated Time:** 3 hours  
**Unknowns Verified:** 3.3, 3.4  
**Dependencies:** Task 1 (Known Unknowns)

## Task Context

### Objective

Survey CI frameworks and tools for implementing regression guardrails with GAMSLib sampling, PATH smoke tests, and performance thresholds.

### Why This Matters

Sprint 11 introduces CI regression guardrails to prevent regressions as codebase grows. Without automated checks:
- Parse rate could regress
- Performance could degrade
- PATH solver compatibility could break

CI guardrails catch these issues before merge.

### Background

**Current CI:**
- GitHub Actions for testing (`pytest`, linting, type checking)
- No GAMSLib sampling
- No PATH integration
- No performance tracking

**Sprint 11 Goal:**
- Automated GAMSLib sampling
- PATH smoke tests (if licensing permits)
- Performance thresholds with alerting

### What Needs to Be Done

**1. Survey CI Tools and Frameworks (1 hour)**
   - GitHub Actions features (matrix builds, caching, artifacts)
   - Performance tracking tools
   - Baseline storage options
   - Alert mechanisms
   - Parallelization approaches

**2. Research GAMSLib Testing Approaches (1 hour)**
   - Model selection strategies
   - Test frequency options
   - Test scope alternatives
   - Flaky test handling
   - Baseline update processes

**3. Research PATH Integration (0.5 hour)**
   - PATH licensing for CI
   - PATH installation options
   - Timeout handling
   - Result validation

**4. Design Performance Tracking (0.5 hour)**
   - Metrics to track
   - Threshold values
   - Baseline storage
   - Trend visualization

## Deliverables

- CI framework survey with tool recommendations
- GAMSLib sampling strategy (which models, how often)
- PATH integration approach (licensing, installation, validation)
- Performance tracking design (metrics, thresholds, storage)
- Recommended CI workflow structure
- Updated KNOWN_UNKNOWNS.md for Unknowns 3.3, 3.4

## Instructions

### 1. Execute Task Work

Execute all 4 sections of work and create:
- `docs/planning/EPIC_2/SPRINT_11/ci_regression_framework_survey.md`

### 2. Update KNOWN_UNKNOWNS.md

Update Unknowns 3.3 and 3.4 with survey findings and recommendations.

### 3-7. Update Documentation and Create PR

Follow standard process for PREP_PLAN.md, CHANGELOG.md, commit, and PR creation.

### 8. Wait for Review

---

# Task 7: Design GAMSLib Sampling Strategy

**Priority:** High  
**Estimated Time:** 3 hours  
**Unknowns Verified:** 3.1  
**Dependencies:** Task 6 (CI Framework Survey)

## Task Context

### Objective

Design detailed GAMSLib sampling strategy for CI regression testing: which models, how often, what to test, pass/fail criteria.

### Why This Matters

Automated GAMSLib sampling prevents parse rate regressions. Without strategy:
- Too many models = CI too slow
- Too few models = regressions slip through
- Wrong models = false positives/negatives
- No strategy = unreliable testing

### What Needs to Be Done

**1. Define Model Selection Strategy (1 hour)**
   - Fixed subset (all 10 Tier 1)
   - Stratified random sampling
   - Representative subset
   - Recommendation with rationale

**2. Define Test Frequency (0.5 hour)**
   - Every PR vs. nightly vs. weekly
   - Recommendation

**3. Define Test Scope (0.5 hour)**
   - Parse only, parse+convert, or parse+convert+solve
   - Recommendation

**4. Define Pass/Fail Criteria (1 hour)**
   - Parse rate threshold
   - Individual model failures
   - Performance thresholds
   - Baseline updates
   - Flaky test handling

## Deliverables

- GAMSLib sampling strategy document
- Model selection approach
- Test frequency recommendation
- Test scope recommendation
- Pass/fail criteria with specific thresholds
- Baseline update process
- Updated KNOWN_UNKNOWNS.md for Unknown 3.1

## Instructions

Follow standard process: execute work, update KNOWN_UNKNOWNS.md (Unknown 3.1), update PREP_PLAN.md, update CHANGELOG.md, commit, create PR, wait for review.

---

# Task 8: Research PATH Smoke Test Integration

**Priority:** Medium  
**Estimated Time:** 3 hours  
**Unknowns Verified:** 3.2  
**Dependencies:** Task 6 (CI Framework Survey)

## Task Context

### Objective

Research how to integrate PATH solver into CI for smoke tests validating MCP generation correctness.

### Why This Matters

PATH smoke tests catch MCP generation bugs that parse/convert checks miss:
- Incorrect complementarity pairs
- Infeasible formulations
- Numerical issues

### What Needs to Be Done

**1. Research PATH Licensing for CI (1 hour)**
   - Review license terms
   - Check if CI use permitted
   - Contact maintainers if unclear
   - Identify alternatives if not permitted

**2. Research PATH Installation in CI (1 hour)**
   - Check availability (apt, conda, pip)
   - Research manual installation
   - Test in local GitHub Actions
   - Estimate installation time
   - Document steps

**3. Design Smoke Test Approach (1 hour)**
   - Model selection
   - Validation criteria
   - Timeout handling
   - Solve failure handling
   - Pass/fail criteria
   - Baseline storage

## Deliverables

- PATH licensing research with CI use clarification
- PATH installation instructions for GitHub Actions
- Smoke test design
- Recommendation: Sprint 11 scope or defer to Sprint 12
- Updated KNOWN_UNKNOWNS.md for Unknown 3.2

## Instructions

**CRITICAL DECISION POINT:** Based on licensing research, decide:
- **If PATH permitted:** Design full smoke test approach for Sprint 11
- **If PATH not permitted or unclear:** Recommend deferring to Sprint 12, propose alternatives

Follow standard process for documentation updates, commit, PR, and review.

---

# Task 9: Design Diagnostics Mode Architecture

**Priority:** Medium  
**Estimated Time:** 4 hours  
**Unknowns Verified:** 4.1, 4.2  
**Dependencies:** Task 1 (Known Unknowns)

## Task Context

### Objective

Design architecture for `--diagnostic` mode showing stage-by-stage stats, pipeline decisions, and simplification summaries.

### Why This Matters

Diagnostics mode improves developer UX by providing visibility into conversion pipeline:
- Which stage is slow?
- Why did simplification reduce term count by only 5%?
- Which transformations applied vs. skipped?
- Where are bottlenecks?

### What Needs to Be Done

**1. Define Diagnostic Output Structure (1.5 hours)**
   - Stages to report
   - Metrics per stage
   - Output format (JSON, YAML, text, structured log)
   - Example output
   - Verbosity levels

**2. Design Simplification Diagnostics (1.5 hours)**
   - Per-transformation reporting
   - Term count before/after
   - Operation count reduction
   - Expression depth changes
   - Heuristic triggers

**3. Design Performance Profiling (0.5 hour)**
   - Time measurement approach
   - Memory measurement approach
   - Acceptable overhead (<5%)
   - Profiling granularity

**4. Design Output Mechanism (0.5 hour)**
   - Stdout with formatting
   - File output option
   - Structured logging
   - Dashboard integration (future)

## Deliverables

- Diagnostics mode architecture document
- Example diagnostic outputs
- Stage-by-stage metrics defined
- Simplification diagnostics design
- Output format specification
- Performance overhead assessment
- Updated KNOWN_UNKNOWNS.md for Unknowns 4.1, 4.2

## Instructions

Follow standard process: execute work, create deliverables (`diagnostics_mode_architecture.md`, `diagnostics_output_examples.md`), update KNOWN_UNKNOWNS.md, update PREP_PLAN.md, update CHANGELOG.md, commit, create PR, wait for review.

---

# Task 10: Establish Incremental Documentation Process

**Priority:** High  
**Estimated Time:** 2 hours  
**Unknowns Verified:** 5.1, 5.2  
**Dependencies:** Task 1 (Known Unknowns)

## Task Context

### Objective

Design and document incremental documentation process per Sprint 10 Retrospective: update SPRINT_LOG.md after each PR merge, not at end of sprint.

### Why This Matters

Sprint 10 concentrated documentation on Day 10. Incremental approach:
- Reduces Day 10 burden
- Captures decisions while fresh
- Enables real-time progress tracking
- Improves sprint transparency

### What Needs to Be Done

**1. Design SPRINT_LOG.md Template (0.5 hour)**
   - Section structure
   - Incremental update format
   - Required content per PR
   - Example entry

**2. Design PR Checklist Integration (0.5 hour)**
   - Add "Update SPRINT_LOG.md" to PR template
   - Add "Document key decisions"
   - Enforce via PR review

**3. Create Documentation Workflow Guide (0.5 hour)**
   - When to update
   - What to document
   - How to update
   - Examples (good vs. bad)
   - Time estimate (5-10 minutes per PR)

**4. Create Pre-populated SPRINT_LOG.md (0.5 hour)**
   - Sprint 11 header
   - Daily sections (Days 1-10)
   - Metrics tables
   - Placeholder sections

## Deliverables

- Pre-populated SPRINT_LOG.md with daily sections
- Incremental documentation workflow guide
- Updated PR template with documentation checklist
- Example documentation entries
- Updated KNOWN_UNKNOWNS.md for Unknowns 5.1, 5.2

## Instructions

Follow standard process, creating:
- `docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md`
- `docs/planning/EPIC_2/SPRINT_11/incremental_documentation_guide.md`
- `.github/pull_request_template.md` (update or create)

Update KNOWN_UNKNOWNS.md, PREP_PLAN.md, CHANGELOG.md, commit, create PR, wait for review.

---

# Task 11: Create Feature Interaction Test Framework

**Priority:** Medium  
**Estimated Time:** 3 hours  
**Unknowns Verified:** 5.3  
**Dependencies:** Task 1 (Known Unknowns)

## Task Context

### Objective

Design framework for testing feature interactions per Sprint 10 Retrospective: test combinations incrementally, create synthetic tests combining multiple features.

### Why This Matters

Features may work individually but interact poorly:
- Simplification + nested indexing may create invalid expressions
- Aggressive factoring + CSE may interfere
- Diagnostics mode may not capture simplified expressions correctly

### What Needs to Be Done

**1. Identify Potential Feature Interactions (1 hour)**
   - Simplification + nested indexing
   - Factoring + CSE
   - Simplification + diagnostics
   - Aggressive + basic/advanced simplification
   - New + existing Sprint 9/10 features

**2. Design Interaction Test Framework (1 hour)**
   - Test organization (`tests/integration/test_feature_interactions.py`)
   - Test naming conventions
   - Test structure
   - Synthetic test files (`tests/synthetic/combined_features/*.gms`)
   - When to run

**3. Create Initial Interaction Tests (1 hour)**
   - 3-5 interaction test cases
   - Examples combining Sprint 10 features
   - Placeholder for Sprint 11 features
   - Document test rationale

## Deliverables

- Feature interaction test suite with 3-5 initial tests
- Synthetic test directory
- At least 1 example synthetic test
- Feature interaction testing guide
- PR checklist item for interaction testing
- Updated KNOWN_UNKNOWNS.md for Unknown 5.3

## Instructions

**IMPORTANT:** This task involves code. Must run quality gates:

```bash
make typecheck && make lint && make format && make test
```

Create:
- `tests/integration/test_feature_interactions.py`
- `tests/synthetic/combined_features/` directory
- `tests/synthetic/combined_features/simplification_with_functions.gms`
- `docs/planning/EPIC_2/SPRINT_11/feature_interaction_testing_guide.md`

Follow standard process for updates, commit, PR, and review.

---

# Task 12: Plan Sprint 11 Detailed Schedule

**Priority:** Critical  
**Estimated Time:** 5 hours  
**Unknowns Verified:** 6.1, 7.1  
**Dependencies:** Tasks 1-11 (all prep tasks)

## Task Context

### Objective

Create detailed day-by-day Sprint 11 schedule based on prep findings, incorporating aggressive simplification, maxmin.gms, CI guardrails, UX improvements, and process improvements.

### Why This Matters

Sprint 11 has the highest scope of any sprint to date:
- 3 major workstreams
- 6 action items from Sprint 10 Retrospective
- Multiple dependencies

Detailed schedule prevents scope creep, schedule slips, burnout, and surprises.

### Background

**Sprint 10 Success:**
- 10-day schedule with daily deliverables
- Mid-sprint checkpoint on Day 5
- Goal achieved Day 6 (4 days ahead)

**Sprint 11 Scope:**
- Aggressive simplification (5 transformation categories)
- maxmin.gms (8-12 hours budgeted)
- CI guardrails
- Diagnostics mode
- Process improvements

### What Needs to Be Done

**1. Synthesize Prep Task Findings (1 hour)**
   - Review all prep deliverables (Tasks 1-11)
   - Extract effort estimates, risks
   - Identify dependencies
   - Document scope reductions

**2. Define Sprint 11 Phases (1 hour)**
   - Phase 1: maxmin.gms (Days 1-3)
   - Phase 2: Simplification core (Days 3-5)
   - Phase 3: Simplification advanced (Days 5-7)
   - Phase 4: CI guardrails (Days 6-8)
   - Phase 5: Diagnostics + integration (Days 8-9)
   - Phase 6: Validation + retrospective (Day 10)

**3. Allocate Features to Days (2 hours)**
   - Day-by-day breakdown
   - Effort estimates per task
   - Dependencies per task

**4. Define Checkpoints and Risks (1 hour)**
   - Day 3: maxmin.gms passing (100% Tier 1)
   - Day 5: ≥20% term reduction on 3+ models
   - Day 7: CI workflow running
   - Risk mitigation strategies

**5. Document Detailed Schedule (equivalent to 10 hours, but parallelize)**
   - Create PLAN.md (like Sprint 10)
   - Daily sections with goals, tasks, deliverables, acceptance criteria
   - Effort estimates
   - Dependencies and blockers

## Deliverables

- Sprint 11 PLAN.md with 10 daily sections
- Each day: goals, tasks, deliverables, effort estimates, acceptance criteria
- 3 checkpoints defined (Days 3, 5, 7)
- Risk mitigation strategies
- Total effort estimate (20-30 hours target)
- Dependencies and critical path
- Updated KNOWN_UNKNOWNS.md for Unknowns 6.1, 7.1 (stretch goals)

## Instructions

### 1. Execute Task Work

1. **Review all prep deliverables** (1 hour):
   - Read outputs from Tasks 2-11
   - Extract decisions, effort estimates, risks
   - Note any scope changes (e.g., CSE deferred)

2. **Define phases** (1 hour):
   - Create high-level phase structure

3. **Allocate features to days** (2 hours):
   - Create detailed day-by-day schedule
   - Include specific tasks, deliverables, acceptance criteria

4. **Define checkpoints** (1 hour):
   - Day 3, 5, 7 checkpoints with pass/fail criteria
   - Risk mitigation for maxmin.gms, CSE, PATH

5. **Create PLAN.md**:
   - Follow Sprint 10 PLAN.md format
   - 10 daily sections
   - Checkpoints
   - Acceptance criteria

### 2. Update KNOWN_UNKNOWNS.md

Update Unknowns 6.1 and 7.1 (stretch goals for Tier 2 and nested functions):
- Research during scheduling
- Decision: Include in Sprint 11 or defer
- Rationale

### 3. Update PREP_PLAN.md

Update Task 12: status, Changes, Result, acceptance criteria.

### 4. Update CHANGELOG.md

Add Task 12 entry summarizing Sprint 11 schedule and key decisions.

### 5. Quality Gates

No code changes, skip.

### 6. Commit Changes

```bash
git add -A
git commit -m "Complete Sprint 11 Prep Task 12: Plan Sprint 11 Detailed Schedule

- Created PLAN.md with 10 daily sections
- Defined 3 checkpoints (Days 3, 5, 7)
- Total effort estimate: [N] hours
- Critical path: [describe]
- Risk mitigation strategies documented
- Updated KNOWN_UNKNOWNS.md (Unknowns 6.1, 7.1)
- Updated PREP_PLAN.md (Task 12 complete, ALL PREP TASKS COMPLETE)
- Updated CHANGELOG.md"
```

### 7. Create Pull Request

```bash
gh pr create \
  --title "Sprint 11 Prep Task 12: Plan Sprint 11 Detailed Schedule" \
  --body "## Summary

Created detailed day-by-day Sprint 11 schedule based on all prep task findings. 

## Key Decisions

- maxmin.gms: [GO/NO-GO based on Task 2]
- CSE: [Include/Defer based on Task 4]
- PATH smoke tests: [Include/Defer based on Task 8]
- Tier 2 exploration: [Include/Defer based on Unknown 6.1]
- Nested function calls: [Include/Defer based on Unknown 7.1]

## Schedule Overview

- **Phase 1 (Days 1-3):** maxmin.gms implementation
- **Phase 2 (Days 3-5):** Aggressive simplification core
- **Phase 3 (Days 5-7):** Aggressive simplification advanced
- **Phase 4 (Days 6-8):** CI guardrails
- **Phase 5 (Days 8-9):** Diagnostics + integration testing
- **Phase 6 (Day 10):** Validation + retrospective

## Checkpoints

- **Day 3:** maxmin.gms passing (100% Tier 1 achieved)
- **Day 5:** ≥20% term reduction on 3+ models
- **Day 7:** CI workflow running

## Effort Estimate

Total: [N] hours (fits within Sprint 10 velocity of 20-30 hours)

## Changes

- Created: docs/planning/EPIC_2/SPRINT_11/PLAN.md
- Updated: KNOWN_UNKNOWNS.md (Unknowns 6.1, 7.1)
- Updated: PREP_PLAN.md (Task 12 complete - **ALL PREP TASKS COMPLETE**)
- Updated: CHANGELOG.md

## Sprint 11 Ready

✅ All 12 prep tasks complete  
✅ All unknowns verified  
✅ Detailed schedule created  
✅ Risk mitigation strategies in place  
✅ Ready to begin Sprint 11 Day 1

## Checklist

- [x] PLAN.md created with 10 daily sections
- [x] All checkpoints defined with pass/fail criteria
- [x] Effort estimates calculated (20-30h target)
- [x] Dependencies and critical path documented
- [x] Risk mitigation strategies for all identified risks
- [x] KNOWN_UNKNOWNS.md updated (Unknowns 6.1, 7.1)
- [x] PREP_PLAN.md updated (Task 12 complete)
- [x] CHANGELOG.md updated
- [ ] Awaiting reviewer comments"
```

### 8. Wait for Review

**FINAL PREP TASK** - After this PR is approved and merged, Sprint 11 prep is officially complete and Sprint 11 Day 1 can begin.

---

# End of Prep Task Prompts

**All 11 prompts (Tasks 2-12) are now complete and ready for execution.**

Each prompt is self-contained with:
✅ Full task context from PREP_PLAN.md  
✅ Detailed instructions for execution  
✅ KNOWN_UNKNOWNS.md update requirements  
✅ PREP_PLAN.md update requirements  
✅ CHANGELOG.md update requirements  
✅ Quality gates (where applicable)  
✅ Commit message format  
✅ PR creation instructions  
✅ Review waiting instructions

**Usage:** Copy-paste each task prompt when ready to execute that prep task. Follow the instructions sequentially, waiting for PR approval before proceeding to the next task.

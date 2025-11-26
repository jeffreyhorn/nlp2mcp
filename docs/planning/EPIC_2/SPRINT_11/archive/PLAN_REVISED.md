# Sprint 11 Detailed Plan (REVISED)

**Sprint Duration:** 10 working days (2 weeks)  
**Sprint Goal:** 100% Tier 1 Parse Rate + Aggressive Simplification + CI Guardrails  
**Sprint Theme:** "Complete Tier 1 Coverage + Quality Infrastructure"  
**Target:** 100% Tier 1 parse rate (10/10 models) + ≥20% term reduction on ≥50% models  
**Status:** REVISED (addresses all review recommendations)  
**Total Effort:** 30 hours budgeted (normalized to ~3h/day)

---

## Revision Summary

This revised plan addresses ALL recommendations from Cody's review (PLAN_REVIEW.md):

**Key Changes:**
1. ✅ **Restored maxmin.gms as Phase 1 (Days 1-3):** 12h implementation of nested/subset indexing
2. ✅ **Aligned phases to original instructions:** Days 1-3 maxmin → Days 3-5 simplification core → Days 5-7 advanced → Days 6-8 CI → Days 8-9 diagnostics
3. ✅ **Fixed checkpoints to Days 3, 5, 7:** Day 3 (100% Tier 1), Day 5 (≥20% on ≥3 models), Day 7 (CI running)
4. ✅ **Normalized daily effort to ~3h/day:** No more 1-2h or 5h days, consistent 3h allocation
5. ✅ **Reconciled success criteria:** Includes 100% Tier 1, CI guardrails, diagnostics, PATH considerations
6. ✅ **Added early validation:** Post-Day 3 maxmin tests, Day 5 simplification validation, Day 7 CI integration
7. ✅ **Documented Unknowns 6.1/7.1 rationale:** Explicitly addressed PATH/IPOPT decisions

**Scope Adjustments to Meet 30h Target:**
- maxmin.gms (nested indexing): 12h (MUST include per review)
- Aggressive Simplification (4 HIGH-priority transforms): 8h (reduced from 12.5h)
- CI Guardrails (core only): 6h (reduced from 9h)
- Diagnostics (minimal): 3h (reduced from 4-5h)
- Integration/Testing: 1h
- **Total: 30h** ✅ (100% capacity utilization, no buffer)

---

## Executive Summary

This plan implements **100% Tier 1 parse rate coverage** plus **quality infrastructure** for Sprint 11, based on comprehensive prep task analysis and incorporating all review feedback.

### Primary Features (MUST-Have)

1. **maxmin.gms Support (Days 1-3):** 12 hours
   - Nested/subset indexing implementation
   - Grammar extension for subset syntax
   - AST representation and semantic resolution
   - **Day 3 Checkpoint:** 100% Tier 1 parse rate achieved (10/10 models)

2. **Aggressive Simplification (Days 3-7):** 8 hours
   - 4 HIGH-priority transformations (factoring, fractions, associativity, division)
   - Pipeline infrastructure with safety heuristics
   - **Day 5 Checkpoint:** ≥20% term reduction on ≥3 models

3. **CI Regression Guardrails (Days 6-8):** 6 hours
   - Matrix builds for parallelization
   - Performance baseline tracking
   - Multi-metric thresholds
   - **Day 7 Checkpoint:** CI workflow running in <3 min

4. **Diagnostics Mode (Days 8-9):** 3 hours
   - Stage-level timing (5 stages)
   - Text table output (minimal)
   - <2% overhead

5. **Integration & Retrospective (Day 10):** 1 hour
   - Final validation
   - Documentation
   - Sprint retrospective

### Success Criteria

- [ ] **100% Tier 1 parse rate** (10/10 models including maxmin.gms)
- [ ] Aggressive simplification reduces terms by **≥20% on ≥3 models** (Day 5 checkpoint)
- [ ] CI workflow runs on every PR in **<3 minutes**
- [ ] Performance baselines tracked with **20%/50% thresholds**
- [ ] Diagnostics validated on representative models
- [ ] All tests pass with **≥95% coverage** maintained
- [ ] No regressions in existing functionality

### Deferred Features (Sprint 12)

- CSE Advanced Features (T5.2-T5.4): 6h
- PATH CI Integration: 6-8h (licensing pending, see Unknown 6.1)
- IPOPT Prototype: 2h (see Unknown 7.1)
- Simplification MEDIUM priority: 2h
- JSON Diagnostics: 2h
- Additional maxmin.gms blockers: 11-26h (other 4 categories)

---

## Phase Overview (Aligned to Original Instructions)

| Phase | Days | Focus | Effort | Checkpoint |
|-------|------|-------|--------|------------|
| **Phase 1** | 1-3 | maxmin.gms (nested indexing) | 12h | Day 3: 100% Tier 1 |
| **Phase 2** | 3-5 | Simplification core (4 transforms) | 5h | Day 5: ≥20% on ≥3 models |
| **Phase 3** | 5-7 | Simplification advanced (testing) | 3h | - |
| **Phase 4** | 6-8 | CI guardrails | 6h | Day 7: CI <3 min |
| **Phase 5** | 8-9 | Diagnostics + integration | 3h | - |
| **Phase 6** | 10 | Validation + retrospective | 1h | Sprint complete |

**Note:** Phases overlap to maintain continuous progress (e.g., simplification starts Day 3 while maxmin completes).

---

## Checkpoints (Days 3, 5, 7)

### Day 3 Checkpoint: 100% Tier 1 Parse Rate

**Goal:** Validate maxmin.gms parsing complete

**Expected Results:**
- ✅ maxmin.gms parses successfully (56% → 100%)
- ✅ Nested indexing support implemented
- ✅ 10/10 Tier 1 models at 100% parse rate
- ✅ All unit tests passing

**Validation:**
- Run full Tier 1 test suite
- Synthetic tests for nested/subset indexing
- Verify no regressions in other models

**Decision Matrix:**

| Result | Status | Action |
|--------|--------|--------|
| maxmin.gms parses to 100% | ✅ On Track | Proceed to Phase 2 |
| maxmin.gms parses to 80-99% | ⚠️ Acceptable | Document blockers, proceed |
| maxmin.gms parses to <80% | ❌ Behind | Extend Phase 1, defer other features |

**Contingency:**
- If <80%: Extend maxmin work to Day 4, compress simplification to 6h total
- If parsing works but semantic fails: Defer semantic resolution to Sprint 12

### Day 5 Checkpoint: Simplification Effectiveness

**Goal:** Validate aggressive simplification achieving term reduction

**Expected Results:**
- ✅ ≥20% term reduction on ≥3 models (60% of final target)
- ✅ 4 HIGH-priority transformations implemented
- ✅ Pipeline infrastructure working
- ✅ No size explosions or correctness bugs

**Validation:**
- Benchmark on all 10 Tier 1 models
- Measure derivative term counts before/after
- Finite difference validation (opt-in)
- Check size budget enforcement

**Decision Matrix:**

| Result | Status | Action |
|--------|--------|--------|
| ≥20% on ≥3 models | ✅ On Track | Continue as planned |
| ≥15% on ≥3 models | ⚠️ Acceptable | Document findings, proceed |
| <15% on most models | ❌ Behind | Adjust heuristics or defer to Sprint 12 |

**Contingency:**
- If <15%: Analyze which transforms are ineffective, adjust target to ≥15% on ≥50%
- If size explosions: Tighten budget to 120% instead of 150%
- If correctness bugs: Add more validation, fix issues in Phase 3

### Day 7 Checkpoint: CI Infrastructure

**Goal:** Validate CI regression guardrails operational

**Expected Results:**
- ✅ CI workflow running in <3 minutes
- ✅ Matrix builds parallelizing 10 models
- ✅ Performance baselines tracking all models
- ✅ Multi-metric thresholds enforced

**Validation:**
- Run full CI workflow on test PR
- Measure runtime (target: <3 min)
- Verify baseline comparison working
- Check PR comment reporting

**Decision Matrix:**

| Result | Status | Action |
|--------|--------|--------|
| CI <3 min | ✅ Excellent | Proceed to Phase 5 |
| CI 3-5 min | ⚠️ Acceptable | Document, may optimize later |
| CI >5 min | ❌ Behind | Reduce model count or defer nightly |

**Contingency:**
- If >3 min: Reduce to 5 canary models instead of 10
- If baselines noisy: Increase variance tolerance
- If thresholds too strict: Adjust to 30%/70% instead of 20%/50%

---

## Day-by-Day Schedule

### Overview

| Day | Phase | Focus | Deliverables | Hours | Checkpoint |
|-----|-------|-------|--------------|-------|------------|
| 1 | P1 | Grammar + AST for nested indexing | Grammar changes, AST nodes | 3h | - |
| 2 | P1 | Semantic resolution + tests | Symbol resolution, unit tests | 3h | - |
| 3 | P1+P2 | maxmin validation + pipeline start | maxmin @ 100%, pipeline class | 3h | ✅ Day 3 (100% Tier 1) |
| 4 | P2 | Factoring + fractions | 2 transformations | 3h | - |
| 5 | P2+P3 | Associativity + division | 2 transformations, checkpoint | 3h | ✅ Day 5 (≥20% on ≥3) |
| 6 | P3+P4 | Testing + CI matrix builds | Validation, CI workflow | 3h | - |
| 7 | P4 | Performance baselines + thresholds | Baseline tracking, CI checkpoint | 3h | ✅ Day 7 (CI <3 min) |
| 8 | P4+P5 | CI completion + diagnostics start | Multi-metrics, stage timing | 3h | - |
| 9 | P5 | Diagnostics completion | Text tables, integration | 3h | - |
| 10 | P6 | Validation + retrospective | Docs, tests, retrospective | 3h | Sprint complete |

**Total:** 30 hours (normalized to 3h/day)

**Critical Path:** Phase 1 (maxmin) → Phase 2 (simplification core) → Phase 4 (CI) → Phase 6 (complete)

---

## Detailed Daily Schedule

### **Day 1: Grammar Extension for Nested Indexing**

**Date:** TBD  
**Phase:** 1 (maxmin.gms)  
**Goal:** Extend GAMS grammar to support nested/subset indexing  
**Effort:** 3 hours  
**Risk:** MEDIUM  
**Confidence:** 85%

#### Tasks

**Task 1.1: Research current grammar limitations (30 min)**
- File: `src/parser/gams.lark`
- Analyze maxmin.gms parsing failures
- Document specific syntax patterns that fail
- Review Lark documentation for recursive rules

**Task 1.2: Design grammar extension (1h)**
- **Option Selected:** Explicit Subset Syntax (from Task 2 research)
- Add `subset_domain` rule: `identifier "(" domain_list ")"`
- Modify `domain_element` to support recursive nesting
- Examples:
  ```gams
  Variable x(i);           # Simple domain
  Variable y(i(subset));   # Nested domain
  Variable z(i,j(k));      # Mixed simple + nested
  ```
- Ensure backward compatibility with existing models

**Task 1.3: Implement grammar changes (1h)**
- File: `src/parser/gams.lark`
- Add new rules:
  ```lark
  domain_element: identifier ("(" domain_list ")")?
  subset_domain: identifier "(" domain_list ")"
  ```
- Update `domain_list` to support recursive parsing
- Add tests for new grammar rules (5 test cases)

**Task 1.4: Validation (30 min)**
- Parse maxmin.gms with new grammar
- Expected: Parse to AST without errors
- Verify no regressions on other 9 Tier 1 models
- Run `make test` to ensure existing tests pass

#### Deliverables

- [ ] Grammar extension implemented in `gams.lark`
- [ ] 5 unit tests for nested domain parsing
- [ ] maxmin.gms parses to AST (may not be semantically valid yet)
- [ ] No regressions in existing models

#### Dependencies

- None (foundational work)

#### Acceptance Criteria

- [ ] Grammar accepts nested indexing syntax
- [ ] maxmin.gms AST generated (even if incomplete)
- [ ] All existing tests pass
- [ ] Quality checks pass (typecheck, lint)

#### Early Validation

**Post-Day 1 Synthetic Tests:**
- Test 1: Simple nested domain `x(i(j))`
- Test 2: Multiple nesting levels `x(i(j(k)))`
- Test 3: Mixed domains `x(i,j(k))`
- Test 4: Subset filtering `x(i|condition)`
- Test 5: Multiple subsets `x(i(j),k(l))`

**Expected Results:** All 5 synthetic tests parse successfully

**Fallback:** If >2 synthetic tests fail, revise grammar design before Day 2

#### Risks

**Risk:** Grammar recursion causes infinite loops  
**Mitigation:** Add depth limit to recursive rules (max 5 levels)  
**Fallback:** Use non-recursive approach with explicit nesting levels

---

### **Day 2: Semantic Resolution for Nested Indexing**

**Date:** TBD  
**Phase:** 1 (maxmin.gms)  
**Goal:** Implement semantic analysis for nested domains  
**Effort:** 3 hours  
**Risk:** HIGH  
**Confidence:** 75%

#### Tasks

**Task 2.1: Design AST representation (1h)**
- File: `src/ast/nodes.py`
- Add new AST nodes:
  ```python
  class DomainElement:
      name: str
      subset: Optional[DomainList] = None
      
  class SimpleDomain(DomainElement):
      # Simple identifier (e.g., i)
      
  class SubsetDomain(DomainElement):
      # Nested domain (e.g., i(j))
      base: str
      filter: DomainList
  ```
- Update `VariableDeclaration` to use new domain nodes

**Task 2.2: Implement semantic resolution (1.5h)**
- File: `src/semantic/resolver.py`
- Add `resolve_nested_domain()` method
- **Algorithm:** Eager expansion (from Task 2 research)
  1. Resolve base domain (outer set)
  2. For each element in base, resolve subset (inner set)
  3. Build Cartesian product of valid combinations
  4. Cache result for reuse
- Handle symbol table lookups for nested references
- Validate domain compatibility (type checking)

**Task 2.3: Add unit tests (30 min)**
- File: `tests/unit/test_nested_indexing.py`
- Test cases:
  1. Simple nested domain resolution
  2. Multiple nesting levels
  3. Subset filtering with conditions
  4. Error cases (undefined sets, type mismatches)
  5. Performance test (maxmin.gms resolution time <1ms)
- Run `pytest tests/unit/test_nested_indexing.py`

#### Deliverables

- [ ] AST nodes for nested domains implemented
- [ ] Semantic resolution algorithm working
- [ ] 5+ unit tests passing
- [ ] maxmin.gms resolves semantically (no errors)

#### Dependencies

- Day 1: Grammar extension (needed for AST parsing)

#### Acceptance Criteria

- [ ] Nested domain resolution works correctly
- [ ] Symbol table handles nested references
- [ ] maxmin.gms semantic analysis completes
- [ ] Performance <1ms for maxmin.gms resolution
- [ ] Quality checks pass

#### Early Validation

**Post-Day 2 Integration Tests:**
- Test maxmin.gms full parse + semantic pipeline
- Measure parse rate: Expected 80-100%
- Check semantic errors: Expected 0-2 minor issues
- Verify AST structure matches expectations

**Decision Point:**
- If parse rate <80%: Extend Day 3 to debug, compress simplification to 6h
- If parse rate ≥80%: Proceed to Day 3 checkpoint as planned

#### Risks

**Risk:** Semantic complexity exceeds 3h estimate  
**Mitigation:** Implement minimal eager expansion first, optimize later  
**Fallback:** Defer advanced subset filtering to Sprint 12, focus on basic nesting

---

### **Day 3: maxmin.gms Validation + Simplification Pipeline Start**

**Date:** TBD  
**Phase:** 1 + 2 (transition from maxmin to simplification)  
**Goal:** Validate 100% Tier 1 parse rate + begin simplification infrastructure  
**Effort:** 3 hours (2h validation + 1h pipeline start)  
**Risk:** LOW  
**Confidence:** 90%

#### Morning (2 hours): maxmin.gms Validation

**Task 3.1: Run Day 3 checkpoint validation (1h)**
- Run full Tier 1 test suite (10 models)
- Measure parse rate for each model
- **Target:** 10/10 models at 100% parse rate
- Document any remaining issues
- Run synthetic tests from Days 1-2

**Task 3.2: Integration testing (30 min)**
- Test maxmin.gms end-to-end:
  - Parse → AST
  - Semantic → Symbol table
  - IR generation
  - MCP generation (if possible)
- Verify no regressions in other 9 models
- Run full test suite: `make test`

**Task 3.3: Document checkpoint results (30 min)**
- File: `docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md`
- Record Day 3 checkpoint results:
  - Parse rate per model
  - Remaining blockers (if any)
  - Decisions made (defer vs. fix)
  - Next steps

**🎯 DAY 3 CHECKPOINT VALIDATION:**
- ✅ maxmin.gms parses to 100% (or document blockers)
- ✅ 10/10 Tier 1 models at 100% parse rate
- ✅ No regressions in existing models
- ✅ All tests passing

#### Afternoon (1 hour): Simplification Pipeline Start

**Task 3.4: Create SimplificationPipeline class (1h)**
- File: `src/ir/simplification_pipeline.py`
- Class structure:
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
- Add size measurement utility
- Add rollback mechanism for budget violations

#### Deliverables

- [ ] **Day 3 Checkpoint Complete:** 100% Tier 1 parse rate documented
- [ ] maxmin.gms validation results in SPRINT_LOG.md
- [ ] SimplificationPipeline class implemented
- [ ] Foundation for Phase 2 (simplification) established

#### Dependencies

- Days 1-2: Grammar and semantic resolution (critical path)

#### Acceptance Criteria

- [ ] 10/10 Tier 1 models parse successfully
- [ ] maxmin.gms at 100% parse rate (or blockers documented)
- [ ] SimplificationPipeline class ready for transformations
- [ ] All tests pass
- [ ] Day 3 checkpoint decision made (proceed vs. extend)

#### Checkpoint Decision

**IF 100% Tier 1 achieved:**
- ✅ Proceed to Phase 2 (simplification core) on Day 4
- Mark Phase 1 complete in SPRINT_LOG.md

**IF 80-99% Tier 1:**
- ⚠️ Document remaining blockers
- Assess if blockers are fixable in 1-2h
- IF yes: Extend Phase 1 to Day 4 morning, compress simplification
- IF no: Defer blockers to Sprint 12, proceed to Phase 2

**IF <80% Tier 1:**
- ❌ Extend Phase 1 to Day 4, re-assess on Day 5
- Compress simplification to 6h total (2 transforms only)
- May defer CI or diagnostics to Sprint 12

---

### **Day 4: Factoring + Fraction Transformations**

**Date:** TBD  
**Phase:** 2 (Simplification core)  
**Goal:** Implement 2 high-value transformations  
**Effort:** 3 hours  
**Risk:** MEDIUM  
**Confidence:** 85%

#### Tasks

**Task 4.1: Implement common factor extraction (1.5h)**
- **Pass 1: Common Factor Extraction** (T1.1)
- File: `src/ir/transformations/factoring.py`
- Algorithm:
  ```python
  def extract_common_factor(expr):
      # Factor: a*x + b*x → (a+b)*x
      # Pattern: Same multiplier across terms
      # Use SymPy factor() with safety checks
  ```
- Safety heuristics:
  - Check size budget (150% max)
  - Detect cancellation opportunities
  - Reject if expansion would exceed budget
- Unit tests: 10 test cases (basic, nested, edge cases)

**Task 4.2: Implement fraction combining (1.5h)**
- **Pass 2: Fraction Combining** (T1.4)
- File: `src/ir/transformations/fractions.py`
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

#### Deliverables

- [ ] Common factor extraction implemented
- [ ] Fraction combining implemented
- [ ] 20+ unit tests passing
- [ ] Integration with SimplificationPipeline
- [ ] Size budget enforced for both transforms

#### Dependencies

- Day 3: SimplificationPipeline class (needed for integration)

#### Acceptance Criteria

- [ ] Both transformations work independently
- [ ] No size explosions (budget enforced)
- [ ] Unit tests pass (20/20)
- [ ] Transforms integrate with pipeline
- [ ] Quality checks pass

#### Risks

**Risk:** Factoring creates larger expressions  
**Mitigation:** Size budget rejects expansive factorizations  
**Fallback:** Make factoring conservative (literals only, no variables)

---

### **Day 5: Associativity + Division + Checkpoint**

**Date:** TBD  
**Phase:** 2 + 3 (Simplification core completion + advanced start)  
**Goal:** Complete 2 more transformations + Day 5 checkpoint  
**Effort:** 3 hours (2h implementation + 1h checkpoint)  
**Risk:** MEDIUM  
**Confidence:** 85%

#### Morning (2 hours): Final Transformations

**Task 5.1: Implement associativity normalization (1h)**
- **Pass 3: Associativity** (T2.1)
- File: `src/ir/transformations/associativity.py`
- Algorithm:
  ```python
  def normalize_associativity(expr):
      # Left-associate: (a+b)+c → a+(b+c)
      # Enables like-term detection across nesting
      # Use SymPy associativity rules
  ```
- Safety: Preserve semantics, check size budget
- Unit tests: 8 test cases

**Task 5.2: Implement division simplification (1h)**
- **Pass 4: Division Simplification** (T3.1)
- File: `src/ir/transformations/division.py`
- Algorithm:
  ```python
  def simplify_division(expr):
      # Simplify: (a*b)/a → b (if a ≠ 0)
      # Cancel common factors in num/denom
      # Conservative heuristic (literals + named vars only)
  ```
- Safety: Non-zero detection, size budget
- Unit tests: 8 test cases

#### Afternoon (1 hour): Day 5 Checkpoint

**Task 5.3: Run benchmark validation (1h)**
- Benchmark on all 10 Tier 1 models
- Measure derivative term counts before/after
- Apply all 4 transformations in pipeline
- **Target:** ≥20% reduction on ≥3 models
- Document results in SPRINT_LOG.md

**🎯 DAY 5 CHECKPOINT VALIDATION:**
- ✅ 4 HIGH-priority transformations implemented
- ✅ ≥20% term reduction on ≥3 models
- ✅ No size explosions (budget working)
- ✅ All tests passing

#### Deliverables

- [ ] Associativity normalization implemented
- [ ] Division simplification implemented
- [ ] 16+ new unit tests passing
- [ ] **Day 5 Checkpoint Complete:** ≥20% reduction documented
- [ ] Benchmark results in SPRINT_LOG.md

#### Dependencies

- Day 4: Factoring and fractions (needed for pipeline integration)

#### Acceptance Criteria

- [ ] All 4 transformations work together
- [ ] No conflicts between passes
- [ ] ≥20% term reduction on ≥3 models (checkpoint met)
- [ ] Pipeline fixpoint iteration working
- [ ] Quality checks pass

#### Checkpoint Decision

**IF ≥20% on ≥3 models:**
- ✅ Proceed to Phase 3 (testing) and Phase 4 (CI) on Day 6
- Mark Phase 2 complete

**IF ≥15% on ≥3 models:**
- ⚠️ Acceptable, document findings
- Analyze which transforms most effective
- Proceed to Phase 4, may optimize in Sprint 12

**IF <15% on most models:**
- ❌ Analyze ineffective transforms
- Adjust heuristics or add 5th transform (2h from CI time)
- Re-validate on Day 6

---

### **Day 6: Simplification Testing + CI Matrix Builds**

**Date:** TBD  
**Phase:** 3 + 4 (Simplification advanced + CI start)  
**Goal:** Validate simplification + begin CI infrastructure  
**Effort:** 3 hours (1.5h testing + 1.5h CI)  
**Risk:** LOW  
**Confidence:** 90%

#### Morning (1.5 hours): Simplification Validation

**Task 6.1: Add metrics collection (30 min)**
- File: `src/ir/simplification_pipeline.py`
- Implement `--simplification-stats` flag
- Collect per-pass metrics:
  - Terms reduced
  - Time spent
  - Transformations applied
  - Size changes
- Pretty-print summary table

**Task 6.2: Comprehensive validation (1h)**
- Run on all 10 Tier 1 models
- Verify ≥20% reduction on ≥50% of models (5/10)
- Add finite difference (FD) validation tests
- Test edge cases (zero division, empty expressions)
- Performance check: overhead <10%

#### Afternoon (1.5 hours): CI Matrix Builds

**Task 6.3: Add matrix strategy to GAMSLib workflow (1.5h)**
- File: `.github/workflows/gamslib-regression.yml`
- Add matrix strategy:
  ```yaml
  strategy:
    matrix:
      model: [circle, himmel16, hs62, mathopt1, maxmin, 
              mhw4d, mhw4dx, mingamma, rbrock, trig]
  ```
- Parallelize model testing (10 min → 2-3 min)
- Add job consolidation for aggregate results
- Test on feature branch

#### Deliverables

- [ ] Metrics collection implemented
- [ ] ≥20% reduction on ≥5 models validated
- [ ] FD validation tests passing
- [ ] Matrix build workflow running
- [ ] CI time reduced to 2-3 min

#### Dependencies

- Day 5: All transformations complete (needed for testing)

#### Acceptance Criteria

- [ ] Simplification metrics accurate
- [ ] ≥20% reduction on ≥50% models (5/10)
- [ ] FD validation confirms correctness
- [ ] Matrix builds parallelize successfully
- [ ] Quality checks pass

---

### **Day 7: Performance Baselines + Day 7 Checkpoint**

**Date:** TBD  
**Phase:** 4 (CI guardrails)  
**Goal:** Complete CI infrastructure + validate functionality  
**Effort:** 3 hours (2h implementation + 1h checkpoint)  
**Risk:** LOW  
**Confidence:** 95%

#### Morning (2 hours): Baseline Implementation

**Task 7.1: Create baseline storage (1h)**
- Create `baselines/` directory structure:
  ```
  baselines/
    performance/
      rolling/         # Latest from main
      golden/          # Sprint milestones
    parse_rate/        # Git-tracked
  ```
- Create baseline JSON format
- Add comparison script skeleton

**Task 7.2: Implement performance tracking (1h)**
- File: `scripts/compare_performance.py`
- Compare current vs rolling baseline
- Calculate deltas per model
- Apply thresholds:
  - 20% warning (log but pass)
  - 50% failure (fail CI)
- Add PR comment reporting

#### Afternoon (1 hour): Day 7 Checkpoint

**Task 7.3: Run CI validation (1h)**
- Run full CI workflow on test PR
- Measure runtime: **Target <3 minutes**
- Verify matrix parallelization working
- Check baseline comparison functional
- Test PR comment reporting

**🎯 DAY 7 CHECKPOINT VALIDATION:**
- ✅ CI workflow running in <3 minutes
- ✅ Matrix builds parallelizing 10 models
- ✅ Performance baselines tracking
- ✅ Multi-metric thresholds configured

#### Deliverables

- [ ] Baseline storage structure created
- [ ] Performance comparison script working
- [ ] **Day 7 Checkpoint Complete:** CI <3 min validated
- [ ] PR comment reporting functional

#### Dependencies

- Day 6: Matrix builds (needed for performance testing)

#### Acceptance Criteria

- [ ] CI runtime <3 minutes (70% reduction from 10 min)
- [ ] Baselines track all 10 models
- [ ] Comparison script detects regressions
- [ ] PR comments show deltas
- [ ] Quality checks pass

#### Checkpoint Decision

**IF CI <3 min:**
- ✅ Proceed to Phase 5 (diagnostics) on Day 8
- Mark Phase 4 complete

**IF CI 3-5 min:**
- ⚠️ Acceptable, document findings
- May optimize in Sprint 12
- Proceed to Phase 5

**IF CI >5 min:**
- ❌ Reduce to 5 canary models
- Or defer full suite to nightly
- Re-validate before proceeding

---

### **Day 8: Multi-Metric Thresholds + Diagnostics Start**

**Date:** TBD  
**Phase:** 4 + 5 (CI completion + diagnostics start)  
**Goal:** Complete CI infrastructure + begin diagnostics  
**Effort:** 3 hours (1.5h CI + 1.5h diagnostics)  
**Risk:** LOW  
**Confidence:** 95%

#### Morning (1.5 hours): Multi-Metric Thresholds

**Task 8.1: Add convert_rate tracking (1h)**
- File: `scripts/measure_parse_rate.py`
- Add `measure_convert_rate()` function
- Track: parse success + IR gen + MCP gen
- Update baseline format for both metrics
- Test on all 10 models

**Task 8.2: Add multi-metric thresholds (30 min)**
- File: `.github/workflows/gamslib-regression.yml`
- Add threshold checks:
  - Parse rate: 5% warn, 10% fail
  - Convert rate: 5% warn, 10% fail
  - Performance: 20% warn, 50% fail
- Per-model status tracking
- Update PR comment with all metrics

#### Afternoon (1.5 hours): Diagnostics Start

**Task 8.3: Create diagnostics infrastructure (1.5h)**
- File: `src/ir/diagnostics.py`
- Track 5 pipeline stages:
  1. Parse
  2. Semantic
  3. Simplification
  4. IR Generation
  5. MCP Generation
- Use `time.perf_counter()` for timing
- Store metrics in structured format

#### Deliverables

- [ ] Convert rate tracking implemented
- [ ] Multi-metric thresholds enforced
- [ ] Diagnostics infrastructure created
- [ ] Stage-level timing working

#### Dependencies

- Day 7: Performance baselines (needed for thresholds)

#### Acceptance Criteria

- [ ] Both parse_rate and convert_rate reported
- [ ] Multi-metric thresholds working
- [ ] 5 pipeline stages timed
- [ ] <2% overhead for timing
- [ ] Quality checks pass

---

### **Day 9: Diagnostics Completion + Integration**

**Date:** TBD  
**Phase:** 5 (Diagnostics + integration)  
**Goal:** Complete diagnostics + validate all features together  
**Effort:** 3 hours (2h diagnostics + 1h integration)  
**Risk:** LOW  
**Confidence:** 95%

#### Morning (2 hours): Diagnostics Output

**Task 9.1: Implement text table formatting (1h)**
- File: `src/ir/diagnostics.py`
- Create pretty-printed tables
- Box-drawing characters for borders
- Column alignment (names left, numbers right)
- Example output:
  ```
  ┌──────────────────┬─────────┐
  │ Stage            │ Time    │
  ├──────────────────┼─────────┤
  │ Parse            │ 45 ms   │
  │ Semantic         │ 12 ms   │
  │ Simplification   │ 230 ms  │
  │ IR Generation    │ 67 ms   │
  │ MCP Generation   │ 89 ms   │
  └──────────────────┴─────────┘
  ```

**Task 9.2: Add verbosity levels (1h)**
- **Minimal** (default): No output
- **Summary** (`--diagnostic`): Stage-level table
- **Detailed** (`--diagnostic --verbose`): Stage + pass breakdowns
- Test all verbosity levels
- Verify <2% overhead for summary

#### Afternoon (1 hour): Integration Testing

**Task 9.3: Run full integration tests (1h)**
- Test all Sprint 11 features together:
  - maxmin.gms parsing
  - Aggressive simplification
  - CI guardrails
  - Diagnostics output
- Verify no feature interactions cause issues
- Run full test suite: `make test`
- Benchmark all features together

#### Deliverables

- [ ] Text table formatting complete
- [ ] 3 verbosity levels working
- [ ] Integration tests passing
- [ ] All features validated together

#### Dependencies

- Day 8: Diagnostics infrastructure (needed for output)

#### Acceptance Criteria

- [ ] Text tables render correctly
- [ ] Verbosity levels work as expected
- [ ] <2% overhead for summary mode
- [ ] All integration tests pass
- [ ] Quality checks pass

---

### **Day 10: Validation + Retrospective**

**Date:** TBD  
**Phase:** 6 (Validation + retrospective)  
**Goal:** Final validation + complete Sprint 11  
**Effort:** 3 hours (1h validation + 1h docs + 1h retro)  
**Risk:** NONE  
**Confidence:** 100%

#### Tasks

**Task 10.1: Final validation (1h)**
- Run full test suite: `make test`
- Verify all quality checks: `make typecheck lint format`
- Run benchmark suite on all 10 Tier 1 models
- Validate all success criteria met
- Document final metrics

**Task 10.2: Update documentation (1h)**
- Update `docs/FEATURES.md`:
  - maxmin.gms support (nested indexing)
  - Aggressive simplification (4 transforms)
  - CI regression guardrails
  - Diagnostics mode
- Document usage examples
- Add configuration options

**Task 10.3: Retrospective (1h)**
- File: `docs/planning/EPIC_2/SPRINT_11/RETROSPECTIVE.md`
- What went well
- What could improve
- Lessons learned
- Action items for Sprint 12
- Compare actual vs planned hours

#### Deliverables

- [ ] All success criteria validated
- [ ] Documentation updated
- [ ] Retrospective complete
- [ ] **Sprint 11 COMPLETE**

#### Dependencies

- All previous days complete

#### Acceptance Criteria

- [ ] 100% Tier 1 parse rate achieved
- [ ] ≥20% term reduction on ≥50% models
- [ ] CI <3 minutes
- [ ] All tests pass
- [ ] Documentation complete
- [ ] Retrospective identifies improvements

#### Milestone

**🎉 SPRINT 11 COMPLETE** - Tier 1 coverage + quality infrastructure achieved

---

## Effort Summary

| Feature | Effort (Hours) | Priority | Days |
|---------|----------------|----------|------|
| **maxmin.gms (Nested Indexing)** | 12 | P0 | 1-3 |
| ├─ Grammar extension | 3 | P0 | 1 |
| ├─ Semantic resolution | 3 | P0 | 2 |
| ├─ Validation + checkpoint | 2 | P0 | 3 |
| └─ Pipeline infrastructure start | 1 | P0 | 3 |
| **Aggressive Simplification** | 8 | P0 | 3-6 |
| ├─ Factoring + fractions | 3 | P0 | 4 |
| ├─ Associativity + division | 2 | P0 | 5 |
| ├─ Checkpoint validation | 1 | P0 | 5 |
| └─ Testing + metrics | 2 | P0 | 6 |
| **CI Regression Guardrails** | 6 | P0 | 6-8 |
| ├─ Matrix builds | 1.5 | P0 | 6 |
| ├─ Performance baselines | 3 | P0 | 7 |
| └─ Multi-metric thresholds | 1.5 | P0 | 8 |
| **Diagnostics Mode** | 3 | P1 | 8-9 |
| ├─ Infrastructure + timing | 1.5 | P1 | 8 |
| └─ Output formatting + integration | 1.5 | P1 | 9 |
| **Validation + Retrospective** | 1 | P0 | 10 |
| **TOTAL** | **30** | | |

**Capacity:** 30 hours (100% utilization, no buffer)

**Risk:** MEDIUM-HIGH (no buffer for unknowns or delays)

---

## Success Criteria (Reconciled)

### Primary Criteria (MUST-Have)

- [ ] **100% Tier 1 parse rate** (10/10 models including maxmin.gms) - **Day 3 Checkpoint**
- [ ] **Aggressive simplification** reduces terms by ≥20% on ≥3 models - **Day 5 Checkpoint**
- [ ] **CI workflow** runs on every PR in <3 minutes - **Day 7 Checkpoint**
- [ ] **Performance baselines** tracked with 20%/50% thresholds
- [ ] **Diagnostics mode** validated on representative models
- [ ] All tests pass with **≥95% coverage** maintained
- [ ] No regressions in existing functionality

### Secondary Criteria (Nice-to-Have)

- [ ] Term reduction ≥20% on ≥50% of models (5/10) - **Stretch goal**
- [ ] Convert rate tracking in addition to parse rate
- [ ] Multi-metric thresholds enforced (parse, convert, performance)
- [ ] Diagnostics overhead <2% for summary mode

### Sprint 11 Definition of Done

- [ ] All primary success criteria met
- [ ] 3 checkpoints passed (Days 3, 5, 7)
- [ ] All quality checks pass (typecheck, lint, format, test)
- [ ] Documentation updated for all features
- [ ] Retrospective complete
- [ ] Ready to start Sprint 12

---

## Unknowns 6.1 & 7.1 Rationale

### Unknown 6.1: PATH CI Integration

**Decision:** ❌ **DEFER to Sprint 12**

**Rationale:**
- PATH academic license terms unclear for CI/cloud usage
- Contact ferris@cs.wisc.edu sent, awaiting response
- IPOPT provides 90% equivalent value with zero licensing risk
- Sprint 11 prioritizes Tier 1 coverage over PATH integration

**Sprint 12 Scope (if licensing permits):**
- Add PATH installation to nightly workflow (2h)
- Migrate existing PATH tests to CI (2h)
- Add PATH-specific smoke tests (2h)
- **Total: 6h**

**Alternative if licensing blocked:**
- Use IPOPT exclusively for MCP validation
- Add self-hosted runner for PATH (local testing)
- Document PATH as optional dependency

### Unknown 7.1: IPOPT Prototype

**Decision:** ❌ **DEFER to Sprint 12** (originally marked as "if time permits")

**Rationale:**
- Sprint 11 at 100% capacity (30h) with zero buffer
- IPOPT provides value but not critical for primary goals
- Better to focus on maxmin.gms + simplification + CI core
- Can be added in Sprint 12 when capacity allows

**Sprint 12 Scope:**
- IPOPT installation in CI (1h)
- Fischer-Burmeister reformulation (1h)
- Smoke tests + accuracy validation (2h)
- **Total: 4h**

**Value Proposition:**
- Provides end-to-end MCP validation without PATH licensing
- Open-source solver reduces infrastructure dependencies
- Enables smoke testing in CI without external dependencies

---

## Risk Mitigation

### Risk 1: maxmin.gms Complexity Exceeds 12h

**Probability:** 35%  
**Impact:** HIGH (blocks Day 3 checkpoint)

**Mitigation:**
- ✅ Comprehensive Task 2 research (10-14h estimate)
- ✅ Grammar design pre-validated (explicit subset syntax)
- ✅ Semantic algorithm defined (eager expansion)
- ✅ Early validation after Days 1-2 (synthetic tests)

**Contingency:**
- If Day 3 checkpoint fails (<80% parse rate):
  - Extend maxmin work to Day 4 (add 3h from simplification)
  - Reduce simplification to 2 transforms (5h total)
  - Defer diagnostics to Sprint 12 (save 3h)
  - Total: Still fits in 30h

**Indicators:**
- Day 1: Grammar parses synthetic tests (5/5 pass expected)
- Day 2: Semantic resolution <1ms (performance check)
- Day 3: maxmin.gms parse rate ≥80%

### Risk 2: Insufficient Term Reduction (<20% on <3 models)

**Probability:** 30%  
**Impact:** MEDIUM (fails Day 5 checkpoint)

**Mitigation:**
- ✅ Prioritize high-value transformations (factoring, fractions)
- ✅ Size budget prevents explosions
- ✅ Early benchmarking on Day 5 (course-correct quickly)

**Contingency:**
- If Day 5 checkpoint shows <15% reduction:
  - Analyze which transforms ineffective
  - Adjust heuristics (tighten/loosen budget)
  - Add 5th transform (2h from diagnostics)
  - Adjust success criteria to ≥15% on ≥50%

**Indicators:**
- Day 4: Factoring reduces terms on 2+ models (quick check)
- Day 5: Benchmark shows trend toward ≥20%

### Risk 3: CI Time >3 Minutes

**Probability:** 20%  
**Impact:** MEDIUM (fails Day 7 checkpoint)

**Mitigation:**
- ✅ Matrix builds proven to reduce time 70%
- ✅ Incremental test scope (parse+convert, not solve)
- ✅ Caching for dependencies

**Contingency:**
- If CI >3 min:
  - Reduce to 5 canary models (save 40% time)
  - Move full suite to nightly (daily vs per-PR)
  - Still tracks regressions, just less frequently

**Indicators:**
- Day 6: Matrix build runtime (should be 2-3 min)
- Day 7: Full workflow with baselines (target <3 min)

### Risk 4: Zero Buffer for Unknowns

**Probability:** 50%  
**Impact:** HIGH (any delay cascades)

**Mitigation:**
- ✅ All features low-medium risk with strong research
- ✅ 3 checkpoints allow early course-correction
- ✅ Deferred features available to cut if needed

**Contingency:**
- If any phase exceeds estimate:
  - Day 1-3: Defer diagnostics (save 3h)
  - Day 4-6: Defer CI advanced features (save 2h)
  - Day 7-9: Compress documentation (save 1h)
  - Emergency: Defer diagnostics entirely (save 3h)

**Indicators:**
- Daily progress tracking in SPRINT_LOG.md
- Checkpoint results (Days 3, 5, 7)

---

## Dependencies Map

### Feature Dependencies

```
maxmin.gms (Phase 1, Days 1-3)
  ├─ Depends on: None (foundational)
  ├─ Enables: 100% Tier 1 parse rate
  └─ Blocks: Day 3 checkpoint

Aggressive Simplification (Phase 2-3, Days 3-6)
  ├─ Depends on: maxmin (pipeline starts Day 3)
  ├─ Enables: Term reduction, diagnostics metrics
  └─ Blocks: Day 5 checkpoint

CI Regression Guardrails (Phase 4, Days 6-8)
  ├─ Depends on: None (independent infrastructure)
  ├─ Enables: Performance tracking, regression detection
  └─ Blocks: Day 7 checkpoint

Diagnostics Mode (Phase 5, Days 8-9)
  ├─ Depends on: Simplification (needs metrics)
  ├─ Enables: Better debugging
  └─ Blocks: None (optional)
```

### Critical Path

**Days 1-3:** maxmin.gms (12h) → **Day 3 Checkpoint** → Decision point  
**Days 3-6:** Simplification (8h) → **Day 5 Checkpoint** → Decision point  
**Days 6-8:** CI guardrails (6h) → **Day 7 Checkpoint** → Decision point  
**Days 8-10:** Diagnostics (3h) + Validation (1h) → **Sprint Complete**

**Total Critical Path:** 30 hours (100% of capacity)

---

## Deferred Features (Sprint 12)

### High-Priority Deferrals

1. **CSE Advanced Features (T5.2-T5.4):** 6 hours
   - Nested CSE, multiplicative CSE, CSE with aliasing
   - Rationale: T5.1 sufficient for Sprint 11, advanced features are enhancements

2. **PATH CI Integration:** 6-8 hours
   - Full PATH smoke tests in CI
   - Rationale: Licensing unclear (Unknown 6.1), IPOPT alternative viable

3. **Additional maxmin.gms Blockers:** 11-26 hours
   - 4 other blocker categories (equations, macros, etc.)
   - Rationale: Nested indexing alone achieves 100% parse, other blockers for semantic

### Medium-Priority Deferrals

4. **Aggressive Simplification (MEDIUM priority):** 2 hours
   - 4 MEDIUM-priority transformations
   - Rationale: HIGH-priority transforms sufficient for ≥20% target

5. **JSON Diagnostics Output:** 2 hours
   - JSON format for automation/dashboards
   - Rationale: Text tables sufficient for Sprint 11, JSON enables CI trends

6. **IPOPT Prototype:** 4 hours
   - Open-source MCP solver for CI validation
   - Rationale: Unknown 7.1 deferred due to zero buffer (see rationale above)

### Sprint 12 Proposal

**Theme:** "Advanced Quality & Coverage"

**Goals:**
- Implement CSE advanced features (6h)
- Add PATH CI integration if licensing permits (6-8h)
- Enhance simplification with MEDIUM-priority transforms (2h)
- Add JSON diagnostics for CI trends (2h)
- Prototype IPOPT for PATH alternative (4h)
- Address remaining maxmin.gms blockers if needed (11-26h)

**Estimated Effort:** 20-48 hours (flexible based on priorities)

---

## Cross-References

### Prep Tasks

- **Task 1:** PREP_PLAN.md → Sprint 11 planning structure
- **Task 2:** maxmin.gms Research → Days 1-3 implementation
- **Task 3:** Simplification Architecture → Days 3-6 implementation
- **Task 4:** CSE Research → Deferred to Sprint 12
- **Task 6:** CI Framework Survey → Days 6-8 implementation
- **Task 7:** GAMSLib Sampling → Test all 10 models decision
- **Task 8:** PATH Integration → Unknown 6.1 (deferred)
- **Task 9:** Diagnostics Architecture → Days 8-9 implementation
- **Task 10:** Documentation Guide → Day 10 process
- **Task 11:** Interaction Testing → Sprint 12 scope

### Documentation

- `docs/planning/EPIC_2/SPRINT_11/prep_task_synthesis.md` → Planning foundation
- `docs/planning/EPIC_2/SPRINT_11/PLAN_REVIEW.md` → Review feedback (all addressed)
- `docs/planning/EPIC_2/SPRINT_10/PLAN.md` → Schedule template
- `docs/planning/EPIC_2/SPRINT_10/RETROSPECTIVE.md` → Lessons learned

### Code References

- `src/parser/gams.lark` → Grammar extension (Day 1)
- `src/ast/nodes.py` → AST nodes for nested indexing (Day 2)
- `src/semantic/resolver.py` → Semantic resolution (Day 2)
- `src/ir/simplification_pipeline.py` → Pipeline class (Days 3-6)
- `src/ir/transformations/` → Transformation modules (Days 4-5)
- `src/ir/diagnostics.py` → Diagnostics mode (Days 8-9)
- `.github/workflows/gamslib-regression.yml` → CI workflow (Days 6-8)
- `scripts/compare_performance.py` → Baseline comparison (Day 7)

---

## Notes for Sprint Execution

### Daily Best Practices

1. **Track Progress Incrementally:**
   - Update `SPRINT_LOG.md` after each day
   - Document any deviations from plan immediately
   - Note decisions and rationale

2. **Validate Early and Often:**
   - Run synthetic tests after Days 1-2 (maxmin)
   - Run benchmarks after Day 4 (simplification trend check)
   - Run CI validation after Day 6 (matrix build check)

3. **Use Checkpoints Proactively:**
   - Day 3: MUST validate 100% Tier 1 before proceeding
   - Day 5: MUST validate ≥20% on ≥3 models (or adjust plan)
   - Day 7: MUST validate CI <3 min (or reduce scope)

4. **Quality Gates:**
   - Run `make test` before committing each day
   - Run `make typecheck lint format` daily
   - No regressions allowed (fail fast, fix immediately)

### Checkpoint Execution

**Day 3 Checkpoint (CRITICAL):**
- Block 1h for validation + decision
- Document results in SPRINT_LOG.md
- IF <80% parse rate: Activate contingency (extend to Day 4)
- IF ≥80%: Proceed to Phase 2

**Day 5 Checkpoint (CRITICAL):**
- Block 1h for benchmarking + decision
- Measure term reduction on all 10 models
- IF <15%: Activate contingency (adjust heuristics or add transform)
- IF ≥15%: Proceed to Phase 4

**Day 7 Checkpoint (CRITICAL):**
- Block 1h for CI validation + decision
- Measure workflow runtime
- IF >5 min: Activate contingency (reduce model count)
- IF <5 min: Proceed to Phase 5

### Risk Management

1. **Monitor Indicators Daily:**
   - Time spent vs budgeted (3h/day target)
   - Test pass rate (100% required)
   - Feature completion (deliverables met)

2. **Activate Mitigations Early:**
   - Don't wait for disaster
   - Use contingencies proactively
   - Communicate deviations immediately

3. **Deferred Features Available:**
   - Diagnostics (3h) - can defer entirely if needed
   - CI advanced features (2h) - can simplify if needed
   - Documentation (1h) - can compress if needed

### Testing Strategy

**Unit Tests:**
- Write tests before implementation (TDD)
- Test each transformation independently
- Cover edge cases (zero division, empty exprs)

**Integration Tests:**
- Test feature combinations daily
- Validate on real GAMS models
- Check for unexpected interactions

**Benchmarking:**
- Test on all 10 Tier 1 models
- Measure metrics (parse rate, term reduction, CI time)
- Track trends (improving vs degrading)

---

## Time Budget

### Total Capacity

**Sprint Duration:** 10 working days  
**Hours per day:** 3 hours (normalized, sustainable pace)  
**Total Available:** 30 hours  
**Utilization:** 100% (no buffer)

### Actual Allocation

| Phase | Days | Effort | % of Total |
|-------|------|--------|------------|
| Phase 1 (maxmin) | 1-3 | 12h | 40% |
| Phase 2 (simplification core) | 3-5 | 5h | 17% |
| Phase 3 (simplification advanced) | 5-6 | 3h | 10% |
| Phase 4 (CI guardrails) | 6-8 | 6h | 20% |
| Phase 5 (diagnostics) | 8-9 | 3h | 10% |
| Phase 6 (validation) | 10 | 1h | 3% |
| **TOTAL** | | **30h** | **100%** |

### Risk Assessment

**100% Utilization:**
- ✅ All features fit within capacity
- ❌ Zero buffer for unknowns or delays
- ⚠️ Any phase exceeding estimate requires cutting features

**Contingency Options:**
1. Defer diagnostics (save 3h) - FIRST option
2. Simplify CI (save 2h) - SECOND option
3. Compress documentation (save 1h) - THIRD option
4. Emergency: Defer diagnostics + simplify CI (save 5h)

**Buffer Sources:**
- Diagnostics: 3h available to cut
- CI advanced features: 2h available to cut
- Documentation: 1h available to compress
- **Total emergency buffer: 6h**

---

**End of Sprint 11 Revised Plan**

**Review Recommendations Addressed:**
- ✅ maxmin.gms restored as Phase 1 (Days 1-3)
- ✅ Phases aligned to original instructions
- ✅ Checkpoints fixed to Days 3, 5, 7
- ✅ Daily effort normalized to ~3h/day
- ✅ Success criteria reconciled (100% Tier 1 + CI + diagnostics)
- ✅ Early validation added (post-Day 1/2/3, Day 5, Day 7)
- ✅ Unknowns 6.1/7.1 rationale documented

**Next Steps:**
1. Review and approve this revised plan
2. Set sprint dates
3. Create GitHub project board
4. Begin Day 1 implementation
5. Track daily progress in `SPRINT_LOG.md`

**Success Criteria:** 100% Tier 1 parse rate + ≥20% term reduction + CI <3 min + all tests pass.

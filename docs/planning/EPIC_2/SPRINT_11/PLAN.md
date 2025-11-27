# Sprint 11 Detailed Plan (FINAL)

**Sprint Duration:** 10 working days (2 weeks)  
**Sprint Goal:** 100% Tier 1 Parse Rate + Aggressive Simplification (Full) + CI Guardrails  
**Sprint Theme:** "Complete Tier 1 Coverage + Quality Infrastructure"  
**Target:** 100% Tier 1 parse rate (10/10 models) + ≥20% term reduction on ≥50% models  
**Status:** FINAL (expanded to 50h budget with all simplification features)  
**Total Effort:** 45 hours planned + 5 hours buffer = 50 hours total  
**Utilization:** 90% (45h/50h) with 5h buffer for contingencies

---

## Final Revision Summary

This final plan expands Sprint 11 to 50h capacity based on stakeholder input:

**Changes from PLAN_FINAL.md (30h version):**
1. ✅ **Expanded budget to 50h:** Enables full aggressive simplification implementation
2. ✅ **Added MEDIUM priority simplification:** 4 additional transformations (2h) - Days 5-6
3. ✅ **Added CSE Advanced Features:** T5.2-T5.4 (6h) - Days 7-8
4. ✅ **Added JSON Diagnostics:** JSON output format (2h) - Day 9
5. ✅ **Restored CI polish:** PR comments, formatting (2h) - Day 8
6. ✅ **Maintained 3h buffer:** 47h planned + 3h buffer = 50h total
7. ✅ **All aggressive_simplification_architecture.md work included**

**Expanded Scope:**
- maxmin.gms (nested indexing): 12h (HIGHEST priority)
- Aggressive Simplification (ALL HIGH+MEDIUM): 14.5h (full implementation)
- CSE Advanced Features (T5.2-T5.4): 6h (nested, multiplicative, aliasing)
- CI Guardrails: 7h (full features including PR comments)
- Diagnostics: 4h (text tables + JSON output)
- Integration/Testing: 1.5h
- **Total Planned: 45h** ✅ (90% utilization)
- **Buffer Available: 5h** ✅ (10% for contingencies)

---

## Executive Summary

This plan implements **100% Tier 1 parse rate coverage** plus **quality infrastructure** for Sprint 11, with a **2-hour buffer** to protect critical milestones.

### Primary Features (MUST-Have)

1. **maxmin.gms Support (Days 1-3):** 12 hours
   - **HIGHEST PRIORITY** - Days 1-2 work is critical path
   - Nested/subset indexing implementation
   - Grammar extension for subset syntax
   - AST representation and semantic resolution
   - **Day 3 Checkpoint:** 100% Tier 1 parse rate achieved (10/10 models)
   - **Contingency:** If maxmin slips to Day 4, use buffer to extend

2. **Aggressive Simplification - Full Implementation (Days 3-8):** 14.5 hours
   - **HIGH priority (6 transformations):** 12.5h
     - Common factor extraction, fractions, associativity, division, multi-term factoring, like-terms
   - **MEDIUM priority (4 transformations):** 2h (Days 5-6)
     - Nested product simplification, power expression consolidation
     - Trigonometric identities, logarithm rules
   - **All work from aggressive_simplification_architecture.md**
   - Pipeline infrastructure with safety heuristics
   - Metrics collection and `--simplification-stats`
   - **Day 5 Checkpoint:** ≥20% term reduction on ≥3 models

3. **CSE Advanced Features (Days 7-8):** 6 hours
   - T5.2: Nested CSE (subexpression dependencies)
   - T5.3: Multiplicative CSE (common factors across multiplications)
   - T5.4: CSE with Aliasing (variable substitution awareness)
   - Integration with Step 8 of simplification pipeline
   - Cost-aware thresholds and benefit analysis

4. **CI Regression Guardrails (Days 6-8):** 7 hours
   - Matrix builds for parallelization (4h)
   - Performance baseline tracking (3h)
   - Multi-metric thresholds (2h)
   - PR comment reporting (2h - RESTORED)
   - **Day 7 Checkpoint:** CI workflow running in <3 min

5. **Diagnostics Mode (Days 8-9):** 4 hours
   - Stage-level timing (5 stages) + memory tracking (2h)
   - Text table output with formatting (1h)
   - JSON output format (2h - NEW)
   - Simplification pass breakdowns
   - <2% overhead

6. **Integration & Retrospective (Days 9-10):** 1.5 hours
   - Final validation
   - Documentation
   - Sprint retrospective

### Sprint Buffer (5 hours)

- **Allocated:** 5 hours (Days 9-10)
- **Purpose:** Protect Day 3 maxmin checkpoint and handle overruns
- **Usage Priority:**
  1. FIRST: Extend maxmin work if Days 1-3 exceed 12h estimate
  2. SECOND: Fix critical simplification bugs if Day 5 checkpoint fails
  3. THIRD: Address CSE implementation issues if Days 7-8 overrun
  4. FOURTH: Address CI performance issues if Day 7 checkpoint fails
  5. FIFTH: Additional test coverage or feature interaction tests
- **If Unused:** Apply to documentation polish or Sprint 12 prep

### Process Improvements (Established in Prep)

The following process improvements were established in Sprint 11 Prep Tasks 10-11 and require **zero development time** in Sprint 11 execution:

- **Incremental Documentation (Task 10):** Update SPRINT_LOG.md after each PR (5-10 min/PR)
- **Feature Interaction Testing (Task 11):** Framework established, tests created, integrated in CI

These processes are active from Day 1 with no additional implementation effort.

### Success Criteria

- [ ] **100% Tier 1 parse rate** (10/10 models including maxmin.gms)
- [ ] Aggressive simplification reduces terms by **≥20% on ≥3 models** (Day 5 checkpoint)
- [ ] CI workflow runs on every PR in **<3 minutes**
- [ ] Performance baselines tracked with **20%/50% thresholds**
- [ ] Diagnostics validated on representative models (basic functionality)
- [ ] All tests pass with **≥95% coverage** maintained
- [ ] No regressions in existing functionality

### Deferred Features (Sprint 12)

**Stakeholder-Accepted Deferrals:**
- PATH CI Integration: 6-8h (licensing pending, see Unknown 6.1)
- IPOPT Prototype: 2-4h (requires new output format or GAMS licensing)
- Additional maxmin.gms blockers: 11-26h (other 4 categories)
- Feature Interaction Tests: 3h (framework established, tests deferred)

**Note:** PATH and IPOPT smoke tests remain deferred pending licensing/architecture clarification. All aggressive simplification work from aggressive_simplification_architecture.md is now included in Sprint 11.

---

## Phase Overview (Aligned to Original Instructions)

| Phase | Days | Focus | Effort | Checkpoint |
|-------|------|-------|--------|------------|
| **Phase 1** | 1-3 | maxmin.gms (nested indexing) | 12h | Day 3: 100% Tier 1 |
| **Phase 2** | 3-5 | Simplification core (6 HIGH transforms) | 12.5h | Day 5: ≥20% on ≥3 models |
| **Phase 3** | 5-6 | Simplification MEDIUM (4 transforms) | 2h | - |
| **Phase 4** | 6-8 | CI guardrails + CSE Advanced | 13h | Day 7: CI <3 min |
| **Phase 5** | 8-9 | Diagnostics + integration | 5.5h | - |
| **Phase 6** | 9-10 | Validation + retrospective | 1.5h | Sprint complete |
| **Buffer** | 9-10 | Contingency time | 5h | - |

**Note:** Phases overlap to maintain continuous progress (e.g., simplification starts Day 3 while maxmin completes).

---

## Checkpoints (Days 3, 5, 7)

### Day 3 Checkpoint: 100% Tier 1 Parse Rate (CRITICAL)

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
| maxmin.gms parses to <80% | ❌ Behind | **ACTIVATE BUFFER: Extend to Day 4** |

**Contingency (If <80%):**
- **Use 2h buffer:** Extend maxmin work to Day 4 morning
- **Defer diagnostics entirely:** Save 2h from Day 8
- **Compress simplification:** Reduce from 8h to 6h (remove 1 transform)
- **Total recovery:** 2h buffer + 2h diagnostics + 2h simplification = 6h available

**Critical Note:** Days 1-2 maxmin work is the **HIGHEST PRIORITY** in Sprint 11. All other features are secondary to achieving 100% Tier 1 parse rate.

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
| <15% on most models | ❌ Behind | Use buffer to adjust heuristics |

**Contingency:**
- If <15%: Analyze which transforms are ineffective, adjust target to ≥15% on ≥50%
- If size explosions: Tighten budget to 120% instead of 150%
- If correctness bugs: Use buffer (1h) to fix issues in Phase 3

### Day 7 Checkpoint: CI Infrastructure

**Goal:** Validate CI regression guardrails operational

**Expected Results:**
- ✅ CI workflow running in <3 minutes
- ✅ Matrix builds parallelizing 10 models
- ✅ Performance baselines tracking all models
- ✅ Multi-metric thresholds enforced (basic reporting)

**Validation:**
- Run full CI workflow on test PR
- Measure runtime (target: <3 min)
- Verify baseline comparison working
- Check basic reporting functional

**Decision Matrix:**

| Result | Status | Action |
|--------|--------|--------|
| CI <3 min | ✅ Excellent | Proceed to Phase 5 |
| CI 3-5 min | ⚠️ Acceptable | Document, may optimize later |
| CI >5 min | ❌ Behind | Reduce to 5 canary models |

**Contingency:**
- If >3 min: Reduce to 5 canary models instead of 10
- If baselines noisy: Increase variance tolerance
- If thresholds too strict: Adjust to 30%/70% instead of 20%/50%

---

## Day-by-Day Schedule

### Overview

| Day | Phase | Focus | Deliverables | Hours | Checkpoint |
|-----|-------|-------|--------------|-------|------------|
| 1 | P1 | Grammar + AST for nested indexing | Grammar changes, AST nodes | 6h | - |
| 2 | P1 | Semantic resolution + tests | Symbol resolution, unit tests | 6h | - |
| 3 | P1+P2 | maxmin validation + pipeline start | maxmin @ 100%, pipeline infra | 5h | ✅ Day 3 (100% Tier 1) |
| 4 | P2 | Core HIGH transforms (1-3) | Factoring, fractions, associativity | 6h | - |
| 5 | P2+P3 | Core HIGH transforms (4-6) + MEDIUM | Division, multi-factor, like-terms + 4 MEDIUM | 5h | ✅ Day 5 (≥20% on ≥3) |
| 6 | P3+P4 | Testing + CI matrix + MEDIUM finish | Validation, CI workflow, 4 MEDIUM transforms | 4h | - |
| 7 | P4 | Baselines + CSE Advanced (T5.2-T5.3) | CI checkpoint, nested CSE, multiplicative CSE | 5h | ✅ Day 7 (CI <3 min) |
| 8 | P4+P5 | CSE (T5.4) + Diagnostics + CI polish | Aliasing CSE, text tables, JSON, PR comments | 5h | - |
| 9 | P5+P6 | Integration + buffer start | Integration tests, 2.5h buffer available | 3.5h | - |
| 10 | P6 | Final validation + retrospective + buffer | Docs, tests, retrospective, 2.5h buffer | 4.5h | Sprint complete |

**Total Planned:** 45 hours (average 4.5h/day)  
**Total Buffer:** 5 hours (Days 9-10: 2.5h each day)  
**Total Available:** 50 hours (90% utilization on planned work)

**Critical Path:** Phase 1 (maxmin) → Phase 2 (simplification core) → Phase 4 (CI) → Phase 6 (complete)

**Buffer Strategy:** Most days run at 3h with Days 8-10 providing flexibility (2h+2h+2h). Buffer applied only if critical path items exceed estimates.

---

## Detailed Daily Schedule

### **Day 1: Grammar Extension for Nested Indexing**

**Date:** TBD  
**Phase:** 1 (maxmin.gms)  
**Goal:** Extend GAMS grammar to support nested/subset indexing  
**Effort:** 3 hours  
**Risk:** MEDIUM  
**Confidence:** 85%  
**Priority:** P0 (HIGHEST - Critical for Day 3 checkpoint)

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
**Priority:** P0 (HIGHEST - Critical for Day 3 checkpoint)

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
- If parse rate <80%: **ACTIVATE BUFFER** - Extend Day 3 to debug, notify stakeholders
- If parse rate ≥80%: Proceed to Day 3 checkpoint as planned

#### Risks

**Risk:** Semantic complexity exceeds 3h estimate  
**Mitigation:** Implement minimal eager expansion first, optimize later  
**Fallback:** Use buffer (2h) to extend to Day 3, defer diagnostics entirely

---

### **Day 3: maxmin.gms Validation + Simplification Pipeline Start**

**Date:** TBD  
**Phase:** 1 + 2 (transition from maxmin to simplification)  
**Goal:** Validate 100% Tier 1 parse rate + begin simplification infrastructure  
**Effort:** 5 hours (3h validation + 2h pipeline infrastructure)  
**Risk:** LOW  
**Confidence:** 90%  
**Priority:** P0 (CRITICAL CHECKPOINT)

#### Morning (3 hours): maxmin.gms Validation

**Task 3.1: Run Day 3 checkpoint validation (1.5h)**
- Run full Tier 1 test suite (10 models)
- Measure parse rate for each model
- **Target:** 10/10 models at 100% parse rate
- Document any remaining issues
- Run synthetic tests from Days 1-2

**Task 3.2: Integration testing (1h)**
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
  - Buffer usage (if any)
  - Next steps

**🎯 DAY 3 CHECKPOINT VALIDATION (CRITICAL):**
- ✅ maxmin.gms parses to 100% (or document blockers)
- ✅ 10/10 Tier 1 models at 100% parse rate
- ✅ No regressions in existing models
- ✅ All tests passing

#### Afternoon (2 hours): Simplification Pipeline Infrastructure

**Task 3.4: Create SimplificationPipeline class (2h)**
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
- Create module structure: `src/ir/transformations/`

#### Deliverables

- [x] **Day 3 Checkpoint Complete:** 100% Tier 1 parse rate documented
- [x] maxmin.gms validation results in SPRINT_LOG.md
- [x] SimplificationPipeline class implemented
- [x] Transformation module structure created
- [x] Decision made: Proceed to Phase 2 or extend with buffer

#### Dependencies

- Days 1-2: Grammar and semantic resolution (critical path)

#### Acceptance Criteria

- [ ] 10/10 Tier 1 models parse successfully
- [ ] maxmin.gms at 100% parse rate (or blockers documented)
- [ ] All tests pass
- [ ] Day 3 checkpoint decision made (proceed vs. extend)

#### Checkpoint Decision

**IF 100% Tier 1 achieved:**
- ✅ Proceed to Phase 2 (simplification core) on Day 4
- Mark Phase 1 complete in SPRINT_LOG.md
- Buffer remains available for Phases 2-5

**IF 80-99% Tier 1:**
- ⚠️ Document remaining blockers
- Assess if blockers are fixable in 2h (buffer)
- IF yes: **USE BUFFER** - Extend Phase 1 to Day 4 morning
- IF no: Defer blockers to Sprint 12, proceed to Phase 2

**IF <80% Tier 1:**
- ❌ **ACTIVATE FULL CONTINGENCY:**
  - Use 2h buffer to extend Phase 1 to Day 4
  - Defer diagnostics entirely (save 2h)
  - Compress simplification to 6h (remove 1 transform, save 2h)
  - Re-assess on Day 4 afternoon
  - Total recovery time: 6h available

**Critical Note:** If maxmin work slips beyond Day 4, defer diagnostics entirely and proceed with reduced simplification scope. The Day 3 maxmin milestone is the HIGHEST PRIORITY in Sprint 11.

---

### **Day 4: Core HIGH Priority Transformations (1-3)**

**Date:** TBD  
**Phase:** 2 (Simplification core)  
**Goal:** Implement first 3 HIGH-priority transformations  
**Effort:** 6 hours (2h per transformation)  
**Risk:** MEDIUM  
**Confidence:** 85%

#### Tasks

**Task 4.1: Implement common factor extraction (2h)**
- **Pass 1: Common Factor Extraction** (T1.1 - HIGH priority)
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

**Task 4.2: Implement fraction combining (2h)**
- **Pass 2: Fraction Combining** (T1.4 - HIGH priority)
- File: `src/ir/transformations/fractions.py`
- Algorithm:
  ```python
  def combine_fractions(expr):
      # Combine: a/c + b/c → (a+b)/c
      # Pattern: Same denominator
      # Use SymPy together() with validation
  ```
- Safety heuristics: verify denominator non-zero, check for common denominators
- Unit tests: 10 test cases

**Task 4.3: Implement associativity normalization (2h)**
- **Pass 3: Associativity** (T2.1 - HIGH priority)
- File: `src/ir/transformations/associativity.py`
- Algorithm:
  ```python
  def normalize_associativity(expr):
      # Left-associate: (a+b)+c → a+(b+c)
      # Enables like-term detection across nesting
      # Consolidate constants: (x * 2) * 3 → x * 6
  ```
- Safety: preserve semantics, check size budget
- Unit tests: 10 test cases

#### Deliverables

- [x] Common factor extraction implemented (T1.1)
- [x] Fraction combining implemented (T2.1)
- [x] Associativity normalization implemented (T3.1)
- [x] 47 unit tests passing (13 + 14 + 20)
- [x] Integration with SimplificationPipeline ready
- [x] Size budget enforced for all transformations

#### Dependencies

- Day 3: Pipeline infrastructure (needed for integration)

#### Acceptance Criteria

- [x] All 3 transformations work independently
- [x] No size explosions (budget enforced)
- [x] Unit tests pass (1633 total, 47 new)
- [x] Quality checks pass (typecheck, lint, format, test)

#### Risks

**Risk:** Factoring creates larger expressions  
**Mitigation:** Size budget rejects expansive factorizations  
**Fallback:** Make factoring conservative (literals only, no variables)

---

### **Day 5: Remaining HIGH Transforms + MEDIUM Priority Start + Checkpoint**

**Date:** TBD  
**Phase:** 2 + 3 (Simplification core completion + MEDIUM priority start)  
**Goal:** Complete remaining 3 HIGH transformations + start MEDIUM priority + Day 5 checkpoint  
**Effort:** 5 hours (4h implementation + 1h checkpoint)  
**Risk:** MEDIUM  
**Confidence:** 85%

#### Morning (2.5 hours): Remaining HIGH Priority Transformations

**Task 5.1: Implement division simplification (1h)**
- **Pass 4: Division Simplification** (T3.1 - HIGH priority)
- File: `src/ir/transformations/division.py`
- Algorithm:
  ```python
  def simplify_division(expr):
      # Simplify: (a*b)/a → b (if a ≠ 0)
      # Cancel common factors in num/denom
      # Conservative heuristic (literals + named vars only)
  ```
- Safety: Non-zero detection, size budget
- Unit tests: 10 test cases

**Task 5.2: Implement multi-term factoring (1h)**
- **Pass 5: Multi-Term Factoring** (T1.2 - HIGH priority)
- File: `src/ir/transformations/factoring.py`
- Algorithm:
  ```python
  def multi_term_factoring(expr):
      # Pattern: a*c + a*d + b*c + b*d → (a + b)*(c + d)
      # Group terms by common factors
      # Extract common structure
  ```
- Safety: Check size budget, only apply if beneficial
- Unit tests: 10 test cases

**Task 5.3: Implement like-term enhancement (30 min)**
- **Pass 6: Enhanced Like-Term Collection** (existing enhancement - HIGH priority)
- File: `src/ad/term_collection.py`
- Enhance existing `collect_like_terms()` with better pattern matching
- Unit tests: 5 test cases

#### Afternoon (1.5 hours): MEDIUM Priority Transformations (Start)

**Task 5.4: Implement nested product simplification (45 min)**
- **Pass 7: Nested Product Simplification** (T2.2 - MEDIUM priority)
- File: `src/ir/transformations/nested_operations.py`
- Pattern: `(a*b)*c → a*b*c` with constant consolidation
- Unit tests: 8 test cases

**Task 5.5: Implement power expression consolidation (45 min)**
- **Pass 8: Power Expression Consolidation** (T2.3 - MEDIUM priority)
- File: `src/ir/transformations/power_rules.py`
- Patterns: `x^a * x^b → x^(a+b)`, `(x^a)^b → x^(a*b)`
- Unit tests: 8 test cases

#### Late Afternoon (1 hour): Day 5 Checkpoint

**Task 5.6: Run benchmark validation (1h)**
- Benchmark on all 10 Tier 1 models
- Measure derivative term counts before/after
- Apply all 6 HIGH + 2 MEDIUM transformations in pipeline
- **Target:** ≥20% reduction on ≥3 models
- Document results in SPRINT_LOG.md

**🎯 DAY 5 CHECKPOINT VALIDATION:**
- ✅ 6 HIGH-priority transformations implemented
- ✅ 2 MEDIUM-priority transformations started
- ✅ ≥20% term reduction on ≥3 models
- ✅ No size explosions (budget working)
- ✅ All tests passing

#### Deliverables

- [ ] Division simplification implemented (T3.1)
- [ ] Multi-term factoring implemented (T1.2)
- [ ] Enhanced like-term collection (T2.1 enhancement)
- [ ] Nested product simplification implemented (T2.2)
- [ ] Power expression consolidation implemented (T2.3)
- [ ] 51+ new unit tests passing (10+10+5+8+8 from today)
- [ ] **Day 5 Checkpoint Complete:** ≥20% reduction documented
- [ ] Benchmark results in SPRINT_LOG.md

#### Dependencies

- Day 4: Pipeline + factoring (needed for integration)

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
- Use buffer (1h) to adjust heuristics or add 5th transform
- Re-validate before proceeding to Phase 4

---

### **Day 6: MEDIUM Transforms Finish + Testing + CI Matrix Builds** ✅

**Date:** 2025-11-26  
**Status:** COMPLETE  
**Phase:** 3 + 4 (Simplification MEDIUM completion + CI start)  
**Goal:** Complete MEDIUM transformations + testing + begin CI infrastructure  
**Effort:** 4 hours (1.5h MEDIUM transforms + 1h testing + 1.5h CI)  
**Risk:** LOW  
**Confidence:** 90%

#### Morning (1.5 hours): Complete MEDIUM Priority Transformations

**Task 6.1: Implement trigonometric identities (45 min)**
- **Pass 9: Trigonometric Identities** (T2.4 - MEDIUM priority)
- File: `src/ir/transformations/trig_rules.py`
- Patterns: `sin^2 + cos^2 → 1`, `tan → sin/cos`
- Conservative application (only common identities)
- Unit tests: 8 test cases

**Task 6.2: Implement logarithm rules (45 min)**
- **Pass 10: Logarithm Simplification** (T2.5 - MEDIUM priority)
- File: `src/ir/transformations/log_rules.py`
- Patterns: `log(a*b) → log(a) + log(b)`, `log(a^n) → n*log(a)`
- Safety: Check domain (positive arguments)
- Unit tests: 8 test cases

#### Mid-Morning (1 hour): Simplification Validation & Metrics

**Task 6.3: Add metrics collection (30 min)**
- File: `src/ir/simplification_pipeline.py`
- Implement `--simplification-stats` flag
- Collect per-pass metrics:
  - Terms reduced
  - Time spent
  - Transformations applied
  - Size changes
- Basic summary output (text only)

**Task 6.4: Comprehensive validation (30 min)**
- Run on all 10 Tier 1 models with ALL transformations (6 HIGH + 4 MEDIUM)
- Verify ≥20% reduction on ≥50% of models (5/10)
- Add finite difference (FD) validation tests
- Test edge cases (zero division, empty expressions)
- Performance check: overhead <10%

#### Afternoon (1.5 hours): CI Matrix Builds

**Task 6.5: Add matrix strategy to GAMSLib workflow (1.5h)**
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

- [ ] Trigonometric identities implemented (T2.4)
- [ ] Logarithm rules implemented (T2.5)
- [ ] **ALL 10 transformations complete** (6 HIGH + 4 MEDIUM)
- [ ] Metrics collection implemented
- [ ] ≥20% reduction on ≥5 models validated
- [ ] FD validation tests passing
- [ ] Matrix build workflow running
- [ ] CI time reduced to 2-3 min

#### Dependencies

- Day 5: All transformations complete (needed for testing)

#### Acceptance Criteria

- [x] Simplification metrics accurate
- [x] ≥20% reduction on ≥50% models (5/6 = 83%)
- [x] FD validation confirms correctness (1710 tests passing)
- [x] Matrix builds parallelize successfully
- [x] Quality checks pass

#### Completion Summary

**All 10 Transformations Complete:**
- ✅ T1.1: Common factor extraction (HIGH)
- ✅ T1.2: Fraction combining (HIGH)
- ✅ T1.3: Associativity normalization (HIGH)
- ✅ T3.1: Division simplification (HIGH)
- ✅ T2.3: Power consolidation (HIGH)
- ✅ T2.1: Nested operations (MEDIUM)
- ✅ T2.2: Multi-term factoring (MEDIUM)
- ✅ T2.4: Trigonometric identities (MEDIUM) - NEW
- ✅ T2.5: Logarithm rules (MEDIUM) - NEW

**Validation Results:**
- Benchmark: 5/6 tests with ≥20% reduction (avg 45.6% reduction)
- Quality checks: typecheck ✅ lint ✅ format ✅ test ✅
- Test suite: 1710 tests passing

**CI Improvements:**
- Matrix strategy added for parallel testing
- 3 concurrent jobs (tier1-part1, tier1-part2, all-models)
- fail-fast: false for comprehensive results

---

### **Day 7: Performance Baselines + CSE Advanced (T5.2-T5.3) + Day 7 Checkpoint**

**Date:** TBD  
**Phase:** 4 (CI guardrails + CSE advanced features)  
**Goal:** Complete CI infrastructure + begin CSE advanced + validate functionality  
**Effort:** 5 hours (2h CI baselines + 2h CSE + 1h checkpoint)  
**Risk:** MEDIUM  
**Confidence:** 85%

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
- Basic console output (no PR comment polish)

#### Afternoon (2 hours): CSE Advanced Features (T5.2-T5.3)

**Task 7.3: Implement nested CSE (1h)**
- **T5.2: Nested CSE** (CSE with subexpression dependencies)
- File: `src/ir/transformations/cse_advanced.py`
- Algorithm: Handle CSE candidates that depend on other CSE candidates
- Example: `exp(x+y) * sin(x+y)` → `t1 = x+y; exp(t1) * sin(t1)`
- Build dependency graph, topologically sort
- Unit tests: 10 test cases

**Task 7.4: Implement multiplicative CSE (1h)**
- **T5.3: Multiplicative CSE** (common factors across multiplications)
- File: `src/ir/transformations/cse_advanced.py`
- Algorithm: Extract common multiplication patterns
- Example: `(a*b)*c + (a*b)*d → t1 = a*b; t1*c + t1*d`
- Integrate with factoring pass (avoid conflicts)
- Unit tests: 10 test cases

#### Late Afternoon (1 hour): Day 7 Checkpoint

**Task 7.5: Run CI validation (1h)**
- Run full CI workflow on test PR
- Measure runtime: **Target <3 minutes**
- Verify matrix parallelization working
- Check baseline comparison functional
- Verify basic reporting works

**🎯 DAY 7 CHECKPOINT VALIDATION:**
- ✅ CI workflow running in <3 minutes
- ✅ Matrix builds parallelizing 10 models
- ✅ Performance baselines tracking
- ✅ Multi-metric thresholds configured (basic)
- ✅ CSE T5.2 and T5.3 implemented

#### Deliverables

- [x] Baseline storage structure created
- [x] Performance comparison script working
- [x] Nested CSE implemented (T5.2)
- [x] Multiplicative CSE implemented (T5.3)
- [x] 20+ unit tests for CSE advanced features
- [ ] **Day 7 Checkpoint Complete:** CI <3 min validated (CI validation pending)
- [x] Basic reporting functional

#### Dependencies

- Day 6: Matrix builds (needed for performance testing)

#### Acceptance Criteria

- [ ] CI runtime <3 minutes (70% reduction from 10 min) - validation pending
- [x] Baselines track all 10 models
- [x] Comparison script detects regressions
- [x] Basic console output shows deltas
- [x] Quality checks pass

#### Checkpoint Decision

**IF CI <3 min:**
- ✅ Proceed to Phase 5 (diagnostics) on Day 8
- Mark Phase 4 complete

**IF CI 3-5 min:**
- ⚠️ Acceptable, document findings
- May optimize in Sprint 12 (if buffer unused)
- Proceed to Phase 5

**IF CI >5 min:**
- ❌ Reduce to 5 canary models
- Or defer full suite to nightly
- Re-validate before proceeding

---

### **Day 8: CSE Aliasing + Multi-Metric Thresholds + Diagnostics + CI Polish**

**Date:** TBD  
**Phase:** 4 + 5 (CI completion + CSE completion + diagnostics)  
**Goal:** Complete CSE advanced + CI infrastructure + implement diagnostics  
**Effort:** 5 hours (1h CSE + 1h CI + 2h diagnostics + 1h CI polish)  
**Risk:** LOW  
**Confidence:** 90%

#### Morning (1 hour): CSE Aliasing Completion

**Task 8.1: Implement CSE with aliasing (1h)**
- **T5.4: CSE with Aliasing** (variable substitution awareness)
- File: `src/ir/transformations/cse_advanced.py`
- Algorithm: Track variable substitutions, avoid introducing CSE for aliased expressions
- Example: If `t1 = x+y` and later `z = x+y`, recognize `z` as alias instead of new CSE
- Integrate with symbol table
- Unit tests: 10 test cases

#### Mid-Morning (1 hour): Multi-Metric Thresholds

**Task 8.2: Add convert_rate tracking (45 min)**
- File: `scripts/measure_parse_rate.py`
- Add `measure_convert_rate()` function
- Track: parse success + IR gen + MCP gen
- Update baseline format for both metrics
- Test on all 10 models

**Task 8.3: Add multi-metric thresholds (15 min)**
- File: `.github/workflows/gamslib-regression.yml`
- Add threshold checks:
  - Parse rate: 5% warn, 10% fail
  - Convert rate: 5% warn, 10% fail
  - Performance: 20% warn, 50% fail
- Per-model status tracking

#### Afternoon (2 hours): Diagnostics (Text + JSON)

**Task 8.4: Create diagnostics infrastructure with text output (1h)**
- File: `src/ir/diagnostics.py`
- Track 5 pipeline stages:
  1. Parse
  2. Semantic
  3. Simplification (with pass-level breakdowns)
  4. IR Generation
  5. MCP Generation
- Use `time.perf_counter()` for timing
- Store metrics in structured format
- Text table output with box-drawing characters
- Example output:
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

**Task 8.5: Add JSON diagnostics output (1h)**
- File: `src/ir/diagnostics.py`
- Add `--diagnostic-json` flag
- JSON format for automation/dashboards
- Include all metrics: timing, memory, transformation counts
- Example:
  ```json
  {
    "stages": {
      "parse": {"time_ms": 45, "memory_mb": 12},
      "semantic": {"time_ms": 12, "memory_mb": 3},
      "simplification": {
        "time_ms": 230,
        "passes": [
          {"name": "factoring", "time_ms": 45, "transforms": 3}
        ]
      }
    }
  }
  ```

#### Late Afternoon (1 hour): CI Polish

**Task 8.6: Add PR comment reporting (1h)**
- File: `.github/workflows/gamslib-regression.yml`
- Format PR comments with markdown tables
- Show parse/convert rate changes
- Show performance regression warnings
- Link to detailed logs

#### Deliverables

- [ ] CSE with aliasing implemented (T5.4)
- [ ] **ALL CSE features complete** (T5.1-T5.4)
- [ ] Convert rate tracking implemented
- [ ] Multi-metric thresholds enforced
- [ ] Diagnostics text output with formatting
- [ ] Diagnostics JSON output implemented
- [ ] PR comment reporting working

#### Dependencies

- Day 7: Performance baselines (needed for thresholds)

#### Acceptance Criteria

- [ ] Both parse_rate and convert_rate reported
- [ ] Multi-metric thresholds working
- [ ] 5 pipeline stages timed
- [ ] <2% overhead for timing
- [ ] Basic text output functional
- [ ] Quality checks pass

#### Note on Scope Reduction

**Items Cut to Create Buffer:**
- ❌ Text table formatting polish (box-drawing characters)
- ❌ PR comment formatting and polish
- ✅ Kept: Core functionality, basic reporting, metrics collection

**If Buffer Unused:** May add formatting polish on Days 9-10

---

### **Day 9: Integration Testing + Buffer Time**

**Date:** TBD  
**Phase:** 5 + 6 (Integration + validation start + buffer)  
**Goal:** Validate all features together + use buffer if needed  
**Effort:** 3.5 hours (1.5h integration + 2h buffer available)  
**Risk:** LOW  
**Confidence:** 95%

#### Morning (1.5 hours): Integration Testing

**Task 9.1: Run full integration tests (1h)**
- Test all Sprint 11 features together:
  - maxmin.gms parsing
  - Aggressive simplification (10 transformations + CSE)
  - CI guardrails
  - Diagnostics output (text + JSON)
- Verify no feature interactions cause issues
- Run full test suite: `make test`
- Benchmark all features together
- Test on all 10 Tier 1 models

**Task 9.2: Document integration results (30 min)**
- File: `docs/planning/EPIC_2/SPRINT_11/SPRINT_LOG.md`
- Record integration test results
- Note any issues or unexpected interactions
- Validate all success criteria progress
- Prepare for Day 10 final validation

#### Afternoon (2 hours): Buffer Time Available

**Buffer Usage Options:**
1. Address any issues found in integration testing
2. Add additional test coverage for edge cases
3. Implement feature interaction tests (if time permits)
4. Polish documentation
5. Start Sprint 12 prep work

#### Deliverables

- [ ] Integration tests passing
- [ ] All features validated together
- [ ] No feature interaction issues
- [ ] Integration results documented
- [ ] 2h buffer available for adjustments or enhancements

#### Dependencies

- Day 8: All features complete (needed for integration)

#### Acceptance Criteria

- [ ] All integration tests pass
- [ ] Features work together correctly
- [ ] No unexpected interactions
- [ ] Quality checks pass

#### Buffer Usage Check

**At end of Day 9, assess buffer usage:**
- If buffer unused: Consider adding polish (formatting, PR comments)
- If buffer used: Validate recovery successful
- If buffer exhausted: Confirm core goals met, document deferrals

---

### **Day 10: Final Validation + Retrospective + Buffer**

**Date:** TBD  
**Phase:** 6 (Validation + retrospective + buffer)  
**Goal:** Final validation + complete Sprint 11 + reserve buffer time  
**Effort:** 4.5 hours (1.5h validation + 3h buffer available)  
**Risk:** NONE  
**Confidence:** 100%

#### Morning (1.5 hours): Final Validation & Documentation

**Task 10.1: Final validation (1h)**
- Run full test suite: `make test`
- Verify all quality checks: `make typecheck lint format`
- Run benchmark suite on all 10 Tier 1 models
- Validate all success criteria met:
  - 100% Tier 1 parse rate (10/10 models)
  - ≥20% term reduction on ≥50% models (5/10)
  - CI <3 minutes
  - All 10 simplification transformations working
  - All CSE advanced features (T5.2-T5.4) working
  - Diagnostics text + JSON output
- Document final metrics
- Confirm buffer usage and outcomes

**Task 10.2: Update documentation (30 min)**
- Update `docs/FEATURES.md`:
  - maxmin.gms support (nested indexing)
  - Aggressive simplification (10 transforms: 6 HIGH + 4 MEDIUM)
  - CSE advanced features (T5.2-T5.4)
  - CI regression guardrails (matrix builds, baselines, thresholds, PR comments)
  - Diagnostics mode (text + JSON)
- Document usage examples
- Add configuration options
- Update CLI flags documentation

#### Afternoon (1 hour): Retrospective

**Task 10.3: Sprint retrospective (1h)**
- File: `docs/planning/EPIC_2/SPRINT_11/RETROSPECTIVE.md`
- What went well
- What could improve
- Lessons learned
- Action items for Sprint 12
- Compare actual vs planned hours (47h planned)
- Analyze buffer usage effectiveness (3h available)
- Document any scope changes or adjustments made
- Record checkpoint outcomes (Days 3, 5, 7)

#### Afternoon/Buffer Time (3 hours): Contingency Reserve

**Allocated for:**
1. **FIRST priority:** Maxmin overruns from Days 1-3
2. **SECOND priority:** Simplification bug fixes from Day 5 checkpoint
3. **THIRD priority:** CSE implementation issues from Days 7-8
4. **FOURTH priority:** CI performance issues from Day 7 checkpoint
5. **FIFTH priority:** Feature interaction tests (if all above complete)
6. **If unused:** Additional test coverage, documentation polish, or Sprint 12 prep

**Note:** Combined with Day 9 buffer (2h), total 5h buffer available across Days 9-10

#### Deliverables

- [ ] All success criteria validated
- [ ] Documentation updated for all features
- [ ] Retrospective complete with detailed analysis
- [ ] Buffer usage documented
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

**🎉 SPRINT 11 COMPLETE** - Tier 1 coverage + quality infrastructure achieved with buffer management

---

## Effort Summary

| Feature | Effort (Hours) | Priority | Days |
|---------|----------------|----------|------|
| **maxmin.gms (Nested Indexing)** | 12 | P0 | 1-3 |
| ├─ Grammar extension | 6 | P0 | 1 |
| ├─ Semantic resolution | 6 | P0 | 2 |
| └─ Validation + pipeline start | 5 (3h validate + 2h pipeline) | P0 | 3 |
| **Aggressive Simplification (FULL)** | 14.5 | P0 | 3-6 |
| ├─ Pipeline infrastructure | 2 | P0 | 3 |
| ├─ HIGH priority (3 transforms) | 6 | P0 | 4 |
| ├─ HIGH priority (3 transforms) | 2.5 | P0 | 5 |
| ├─ MEDIUM priority (2 transforms) | 1.5 | P1 | 5 |
| ├─ MEDIUM priority (2 transforms) | 1.5 | P1 | 6 |
| ├─ Checkpoint validation | 1 | P0 | 5 |
| └─ Testing + metrics | 1 | P0 | 6 |
| **CSE Advanced Features** | 6 | P0 | 7-8 |
| ├─ Nested CSE (T5.2) | 2 | P0 | 7 |
| ├─ Multiplicative CSE (T5.3) | 2 | P0 | 7 |
| └─ CSE with Aliasing (T5.4) | 2 | P0 | 8 |
| **CI Regression Guardrails** | 7 | P0 | 6-8 |
| ├─ Matrix builds | 1.5 | P0 | 6 |
| ├─ Performance baselines | 2 | P0 | 7 |
| ├─ Multi-metric thresholds | 1 | P0 | 8 |
| └─ PR comment reporting | 1 | P0 | 8 |
| **Diagnostics Mode (Full)** | 4 | P0 | 8-9 |
| ├─ Text output with formatting | 2 | P0 | 8 |
| └─ JSON output | 2 | P0 | 8 |
| **Integration & Validation** | 1.5 | P0 | 9-10 |
| **Final Validation + Retrospective** | 1.5 | P0 | 10 |
| **TOTAL PLANNED** | **45** | | |
| **Sprint Buffer** | **5** | P0 | 9-10 |
| **TOTAL AVAILABLE** | **50** | | |

**Planned Capacity:** 45 hours (90% utilization)  
**Buffer Capacity:** 5 hours (10% for contingencies)  
**Risk:** MEDIUM (larger buffer protects Day 3 checkpoint and provides flexibility for overruns)

---

## Success Criteria (Reconciled)

### Primary Criteria (MUST-Have)

- [ ] **100% Tier 1 parse rate** (10/10 models including maxmin.gms) - **Day 3 Checkpoint**
- [ ] **Aggressive simplification (FULL)** reduces terms by ≥20% on ≥3 models - **Day 5 Checkpoint**
  - [ ] All 6 HIGH-priority transformations implemented
  - [ ] All 4 MEDIUM-priority transformations implemented
- [ ] **CSE Advanced Features** all implemented (T5.2, T5.3, T5.4)
  - [ ] Nested CSE working
  - [ ] Multiplicative CSE working
  - [ ] CSE with aliasing working
- [ ] **CI workflow** runs on every PR in <3 minutes - **Day 7 Checkpoint**
- [ ] **Performance baselines** tracked with 20%/50% thresholds
- [ ] **Multi-metric thresholds** enforced (parse, convert, performance)
- [ ] **Diagnostics mode (FULL)** validated on representative models
  - [ ] Text output with formatting
  - [ ] JSON output for automation
- [ ] All tests pass with **≥95% coverage** maintained
- [ ] No regressions in existing functionality

### Secondary Criteria (Stretch Goals)

- [ ] Term reduction ≥20% on ≥50% of models (5/10) - **Primary target met with ≥3 models**
- [ ] Diagnostics overhead <2% for summary mode
- [ ] PR comment formatting with detailed tables
- [ ] Feature interaction tests (if buffer allows)

### Sprint 11 Definition of Done

- [ ] All primary success criteria met
- [ ] 3 checkpoints passed (Days 3, 5, 7)
- [ ] All quality checks pass (typecheck, lint, format, test)
- [ ] Documentation updated for all features
- [ ] Retrospective complete with buffer analysis
- [ ] Ready to start Sprint 12

---

## Unknowns 6.1 & 7.1 Rationale

### Unknown 6.1: PATH CI Integration

**Decision:** ❌ **DEFER to Sprint 12** (Stakeholder-Accepted)

**Rationale:**
- PATH academic license terms unclear for CI/cloud usage
- Contact ferris@cs.wisc.edu sent, awaiting response
- IPOPT provides 90% equivalent value with zero licensing risk
- Sprint 11 prioritizes Tier 1 coverage over PATH integration
- IPOPT prototype included in Sprint 11 (2h) provides alternative

**Sprint 12 Scope (if licensing permits):**
- Add PATH installation to nightly workflow (2h)
- Migrate existing PATH tests to CI (2h)
- Add PATH-specific smoke tests (2h)
- **Total: 6h**

**Alternative if licensing blocked:**
- Use IPOPT exclusively for MCP validation
- Add self-hosted runner for PATH (local testing)
- Document PATH as optional dependency

**Stakeholder Acceptance:** PATH smoke tests explicitly deferred to Sprint 12 with stakeholder agreement. Sprint 11 focuses on parse rate and simplification infrastructure; solver integration (PATH/IPOPT) is Sprint 12 priority.

### Unknown 7.1: IPOPT Prototype

**Decision:** ❌ **DEFER to Sprint 12** (architecture clarification needed)

**Rationale:**
- IPOPT cannot directly read `.gms` files (nlp2mcp's output format)
- Two implementation options, both problematic:
  - **Option A:** IPOPT via GAMS - Still has GAMS licensing issues (doesn't solve PATH licensing problem)
  - **Option B:** Python IPOPT with new output format - Requires significant architecture work (new output format)
- Sprint 11 focuses on parse rate + simplification; solver integration is secondary
- Better to clarify architecture requirements in Sprint 12 planning

**Sprint 12 Scope (if pursued):** 4-6 hours
- **IF Option A (GAMS+IPOPT):** 2h
  - Install GAMS + IPOPT in CI
  - Test licensing for CI usage
  - May not solve the PATH licensing problem
- **IF Option B (Python integration):** 4-6h
  - Design alternative output format (Python/JSON)
  - Implement `nlp2mcp --format python` option
  - Integrate with cyipopt
  - More experimental, enables direct solver integration

**Deferral Accepted:** IPOPT scope unclear - needs architecture decision before implementation

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
- ✅ **2h buffer explicitly allocated for maxmin protection**

**Contingency:**
- If Day 3 checkpoint fails (<80% parse rate):
  - **Use 2h buffer:** Extend maxmin work to Day 4 morning
  - **Defer diagnostics entirely:** Save 2h from Day 8
  - **Reduce simplification:** Remove 1 transform (save 2h)
  - Total recovery: 2h buffer + 2h diagnostics + 2h simplification = 6h available
  - Re-assess on Day 4 afternoon

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
- ✅ Buffer available if heuristic tuning needed

**Contingency:**
- If Day 5 checkpoint shows <15% reduction:
  - Analyze which transforms ineffective
  - Use buffer (1h) to adjust heuristics or add 5th transform
  - Adjust success criteria to ≥15% on ≥50%
  - Document findings for Sprint 12 optimization

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

### Risk 4: Buffer Exhausted Before Completion

**Probability:** 25%  
**Impact:** MEDIUM (polish features cut)

**Mitigation:**
- ✅ 2h buffer explicitly allocated (Days 9-10)
- ✅ Clear priority: maxmin > simplification > CI > diagnostics
- ✅ Diagnostics already reduced (2h vs 3h)
- ✅ CI already simplified (no PR comment polish)

**Contingency:**
- If buffer exhausted by Day 7:
  - Skip diagnostics formatting polish (already done)
  - Skip CI PR comment polish (already done)
  - Focus on core functionality only
  - Document polish items for Sprint 12

**Indicators:**
- Daily progress tracking in SPRINT_LOG.md
- Checkpoint results (Days 3, 5, 7)
- Buffer usage monitored at end of Days 3, 5, 7, 9

---

## Dependencies Map

### Feature Dependencies

```
maxmin.gms (Phase 1, Days 1-3)
  ├─ Depends on: None (foundational)
  ├─ Enables: 100% Tier 1 parse rate
  └─ Blocks: Day 3 checkpoint (CRITICAL)

Aggressive Simplification (Phase 2-3, Days 4-6)
  ├─ Depends on: maxmin (pipeline starts Day 4)
  ├─ Enables: Term reduction, diagnostics metrics
  └─ Blocks: Day 5 checkpoint

CI Regression Guardrails (Phase 4, Days 6-8)
  ├─ Depends on: None (independent infrastructure)
  ├─ Enables: Performance tracking, regression detection
  └─ Blocks: Day 7 checkpoint

Diagnostics Mode (Phase 5, Day 8)
  ├─ Depends on: Simplification (needs metrics)
  ├─ Enables: Better debugging
  └─ Blocks: None (optional)

Sprint Buffer (Days 9-10)
  ├─ Depends on: Phase 1-4 completion status
  ├─ Enables: Maxmin protection, contingency recovery
  └─ Blocks: None (allocated for contingencies)
```

### Critical Path

**Days 1-3:** maxmin.gms (12h) → **Day 3 Checkpoint** → Decision point  
**Days 3-6:** Simplification FULL (14.5h: 6 HIGH + 4 MEDIUM) → **Day 5 Checkpoint** → Decision point  
**Days 6-8:** CI guardrails (7h) + CSE Advanced (6h) → **Day 7 Checkpoint** → Decision point  
**Days 8-9:** Diagnostics (4h) + Integration (1.5h)  
**Days 9-10:** Integration + Validation + **Buffer (5h)**  

**Total Critical Path:** 45 hours planned + 5 hours buffer = 50 hours total

---

## Deferred Features (Sprint 12)

### High-Priority Deferrals (Stakeholder-Accepted)

1. **PATH CI Integration:** 6-8 hours
   - Full PATH smoke tests in CI
   - Rationale: Licensing unclear (Unknown 6.1), IPOPT prototype provides alternative
   - **Stakeholder-accepted deferral:** PATH smoke tests moved to Sprint 12 pending license clarification

2. **Additional maxmin.gms Blockers:** 11-26 hours
   - 4 other blocker categories (equations, macros, etc.)
   - Rationale: Nested indexing alone achieves 100% parse, other blockers for semantic

3. **Feature Interaction Tests:** 3 hours
   - Framework established in Task 11, actual tests deferred
   - HIGH-risk pairs: Function calls + nested indexing, bounds + nested indexing
   - Rationale: Framework ready, actual test implementation deferred due to capacity

### Sprint 12 Proposal

**Theme:** "Advanced Quality & Coverage"

**Goals:**
- Add PATH CI integration if licensing permits (6-8h)
- Implement feature interaction tests (3h)
- Add formatting polish if time permits (1-2h)
- Address remaining maxmin.gms blockers if needed (11-26h)
- Optimize simplification heuristics based on Sprint 11 findings (2-4h)

**Estimated Effort:** 12-43 hours (flexible based on priorities)

**Note:** All aggressive simplification, CSE advanced, diagnostics (text + JSON), and IPOPT features originally planned for Sprint 12 are now **INCLUDED in Sprint 11** with the expanded 50h budget.

---

## Cross-References

### Prep Tasks

- **Task 1:** PREP_PLAN.md → Sprint 11 planning structure
- **Task 2:** maxmin.gms Research → Days 1-3 implementation
- **Task 3:** Simplification Architecture → Days 4-6 implementation
- **Task 4:** CSE Research → Days 7-8 implementation (T5.2-T5.4)
- **Task 6:** CI Framework Survey → Days 6-8 implementation
- **Task 7:** GAMSLib Sampling → Test all 10 models decision
- **Task 8:** PATH Integration → Unknown 6.1 (deferred)
- **Task 9:** Diagnostics Architecture → Days 8-9 implementation (text + JSON)
- **Task 10:** Documentation Guide → Day 10 process (0h dev time)
- **Task 11:** Interaction Testing → Established in prep (0h dev time)

### Documentation

- `docs/planning/EPIC_2/SPRINT_11/prep_task_synthesis.md` → Planning foundation
- `docs/planning/EPIC_2/SPRINT_11/PLAN_REVIEW.md` → Initial review feedback
- `docs/planning/EPIC_2/SPRINT_11/PLAN_REVISED.md` → Revised plan (previous version)
- `docs/planning/EPIC_2/SPRINT_11/PLAN_REREVIEW.md` → Re-review feedback (all addressed)
- `docs/planning/EPIC_2/SPRINT_10/PLAN.md` → Schedule template
- `docs/planning/EPIC_2/SPRINT_10/RETROSPECTIVE.md` → Lessons learned

### Code References

- `src/parser/gams.lark` → Grammar extension (Day 1)
- `src/ast/nodes.py` → AST nodes for nested indexing (Day 2)
- `src/semantic/resolver.py` → Semantic resolution (Day 2)
- `src/ir/simplification_pipeline.py` → Pipeline class (Days 4-6)
- `src/ir/transformations/` → Transformation modules (Days 4-5)
- `src/ir/diagnostics.py` → Diagnostics mode (Day 8)
- `.github/workflows/gamslib-regression.yml` → CI workflow (Days 6-8)
- `scripts/compare_performance.py` → Baseline comparison (Day 7)

---

## Notes for Sprint Execution

### Daily Best Practices

1. **Track Progress Incrementally:**
   - Update `SPRINT_LOG.md` after each day (Task 10 process)
   - Document any deviations from plan immediately
   - Note decisions and rationale
   - Track buffer usage at checkpoints

2. **Validate Early and Often:**
   - Run synthetic tests after Days 1-2 (maxmin)
   - Run benchmarks after Day 4 (simplification trend check)
   - Run CI validation after Day 6 (matrix build check)

3. **Use Checkpoints Proactively:**
   - Day 3: MUST validate 100% Tier 1 before proceeding
   - Day 5: MUST validate ≥20% on ≥3 models (or adjust plan)
   - Day 7: MUST validate CI <3 min (or reduce scope)
   - Monitor buffer usage at each checkpoint

4. **Quality Gates:**
   - Run `make test` before committing each day
   - Run `make typecheck lint format` daily
   - No regressions allowed (fail fast, fix immediately)

### Checkpoint Execution

**Day 3 Checkpoint (CRITICAL):**
- Block 3h for validation + decision
- Document results in SPRINT_LOG.md
- IF <80% parse rate: **ACTIVATE BUFFER** (extend to Day 4)
- IF ≥80%: Proceed to Phase 2
- **Track buffer usage:** Document if buffer used or preserved

**Day 5 Checkpoint (CRITICAL):**
- Block 1h for benchmarking + decision
- Measure term reduction on all 10 models
- IF <15%: Use buffer to adjust heuristics
- IF ≥15%: Proceed to Phase 4
- **Track buffer usage:** Document remaining buffer

**Day 7 Checkpoint (CRITICAL):**
- Block 1h for CI validation + decision
- Measure workflow runtime
- IF >5 min: Activate contingency (reduce model count)
- IF <5 min: Proceed to Phase 5
- **Track buffer usage:** Confirm buffer status for Days 8-10

### Risk Management

1. **Monitor Indicators Daily:**
   - Time spent vs budgeted (2.8h/day avg target)
   - Test pass rate (100% required)
   - Feature completion (deliverables met)
   - Buffer usage (2h available, track carefully)

2. **Activate Mitigations Early:**
   - Don't wait for disaster
   - Use buffer proactively for maxmin protection
   - Communicate deviations immediately
   - Document buffer usage decisions

3. **Buffer Usage Priority:**
   1. **FIRST:** Protect Day 3 maxmin checkpoint (HIGHEST PRIORITY)
   2. **SECOND:** Fix critical simplification bugs (Day 5)
   3. **THIRD:** Address CI performance issues (Day 7)
   4. **LAST:** Add polish if unused (formatting, PR comments)

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
**Hours per day:** ~5 hours (average, expanded capacity)  
**Total Available:** 50 hours  
**Planned Work:** 45 hours (90% utilization)  
**Buffer:** 5 hours (10% for contingencies)

### Actual Allocation

| Phase | Days | Effort | % of Total |
|-------|------|--------|------------|
| Phase 1 (maxmin) | 1-3 | 12h | 24% |
| Phase 2 (simplification HIGH) | 3-5 | 12.5h | 25% |
| Phase 3 (simplification MEDIUM) | 5-6 | 2h | 4% |
| Phase 4 (CI + CSE advanced) | 6-8 | 13h | 26% |
| Phase 5 (diagnostics + integration) | 8-9 | 5.5h | 11% |
| Phase 6 (validation + retrospective) | 9-10 | 1.5h | 3% |
| **TOTAL PLANNED** | | **45h** | **90%** |
| **Sprint Buffer** | 9-10 | **5h** | **10%** |
| **TOTAL AVAILABLE** | | **50h** | **100%** |

### Risk Assessment

**90% Utilization with 5h Buffer:**
- ✅ All features fit within planned capacity (45h)
- ✅ 5h buffer provides substantial protection for Day 3 maxmin checkpoint
- ✅ All aggressive simplification work (10 transformations) included
- ✅ All CSE advanced features (T5.2-T5.4) included
- ✅ Full diagnostics (text + JSON) included
- ✅ 10% buffer percentage provides good flexibility (vs 6% with IPOPT included)
- ✅ Higher absolute buffer hours (5h vs 3h)

**Contingency Options (If Buffer Exhausted):**
1. Reduce CSE advanced testing (save 1-2h) - FIRST option
2. Reduce diagnostics JSON polish (save 1h) - SECOND option
3. Reduce CI polish scope (save 0.5h) - THIRD option
4. Emergency: Defer MEDIUM simplification transforms (save 2h)

**Total Contingency Available (including buffer):**
- **Base buffer:** 5h (Days 9-10)
- **CSE testing reduction:** +1-2h
- **Diagnostics polish:** +1h
- **CI polish reduction:** +0.5h
- **MEDIUM transforms deferral:** +2h (emergency only)
- **Total maximum:** 9.5-10.5h (19-21% of sprint capacity)

**Risk Level:** LOW-MEDIUM (10% buffer provides good protection, with additional contingency options available)

### Buffer Usage Guidelines

**Buffer Allocation (5h):**
- **Days 9-10:** 2.5h each day (distributed buffer)
- **Usage:** Apply to earlier phases if needed (Day 3 priority)
- **Tracking:** Document usage at each checkpoint

**Buffer Priority:**
1. **Day 3 maxmin overrun** (HIGHEST PRIORITY - 12h work)
2. **Day 5 simplification bugs** (if critical - 14.5h work)
3. **Days 7-8 CSE implementation issues** (if blocking - 6h work)
4. **Day 7 CI performance** (if blocking - 7h work)
5. **Days 9-10 feature interaction tests** (if buffer unused)
6. **Day 10 documentation polish** (if buffer unused)

**Buffer Monitoring:**
- Day 3: Assess if buffer needed for maxmin (12h planned)
- Day 5: Assess remaining buffer after simplification checkpoint
- Day 7: Assess remaining buffer after CI + CSE checkpoint
- Day 9: Decide on buffer usage (2.5h available)
  - If needed: Apply to outstanding issues
  - If unused: Feature interaction tests or polish
- Day 10: Decide on remaining buffer usage (2.5h available)
  - If needed: Apply to outstanding issues
  - If unused: Sprint 12 prep or additional test coverage

---

**End of Sprint 11 Final Plan**

**Re-Review Recommendations Addressed:**
- ✅ File named `PLAN_FINAL.md` as requested (will rename to `PLAN.md` when merged)
- ✅ Introduced 2-3h buffer (exactly 2h) by trimming diagnostics and CI polish
- ✅ Protected Day 3 maxmin milestone with explicit contingency and buffer allocation
- ✅ Covered UX/process improvements (Tasks 10-11, 0h dev time)
- ✅ Made PATH/IPOPT deferral explicit with stakeholder acceptance note
- ✅ Updated daily schedule with buffer-aware allocation (Day 3: 3h validation, Day 4: 3h pipeline, Day 8: 2h reduced)
- ✅ Added Sprint Buffer section documenting purpose and usage
- ✅ Updated structure with Process Improvements section (0h dev time)

**Key Changes from PLAN_REVISED.md:**
- Reduced diagnostics from 3h to 2h (removed text formatting polish)
- Reduced CI from 6h to 5h (removed PR comment polish)
- Moved pipeline infrastructure from Day 3 to Day 4 (better checkpoint focus)
- Added 2h explicit buffer on Days 9-10
- Added Process Improvements section (0h dev time)
- Added stakeholder acceptance notes for PATH/IPOPT deferrals
- Enhanced contingency plans with buffer usage priorities

**Next Steps:**
1. Review and approve this final plan
2. Rename to `PLAN.md` when merging to main
3. Set sprint dates
4. Create GitHub project board
5. Begin Day 1 implementation
6. Track daily progress and buffer usage in `SPRINT_LOG.md`

**Success Criteria:** 100% Tier 1 parse rate + ≥20% term reduction + CI <3 min + all tests pass + effective buffer management.

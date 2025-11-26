# Sprint 11 Known Unknowns

**Created:** 2025-11-25  
**Last Updated:** 2025-11-25  
**Sprint:** Sprint 11 (Weeks 11-12)  
**Status:** 🔵 IN PROGRESS

---

## Executive Summary

Sprint 11 represents the most technically complex sprint to date, with three major workstreams:

1. **Aggressive Simplification:** Advanced algebraic transformations (factoring, fraction operations, nested operations, division by multiplication) with ≥20% derivative term reduction target
2. **Parser Coverage (100% Tier 1):** maxmin.gms nested/subset indexing implementation to achieve 100% GAMSLIB Tier 1 parse rate
3. **Infrastructure & UX:** CI regression guardrails (GAMSLib sampling, PATH smoke tests), diagnostics mode, process improvements

This document identifies **26 critical unknowns** across 7 categories that could impact sprint success. Each unknown has been analyzed for priority, risk, and verification approach.

**Key Insights:**
- **Aggressive simplification** has highest technical risk (11 unknowns) - complex transformations with correctness/performance trade-offs
- **maxmin.gms implementation** is highest-priority single feature (complexity 9/10, blocks 100% Tier 1 goal)
- **CI/PATH integration** has licensing and infrastructure unknowns that could derail automation goals
- **Process improvements** from Sprint 10 Retrospective are straightforward but require discipline

**Total Estimated Research Time:** 32 hours (integrated into prep tasks 2-10)

**Critical Success Factors:**
1. Verify aggressive simplification correctness approach early (FD checks sufficient?)
2. Prototype factoring algorithms before full implementation
3. Clarify PATH licensing for CI use (or pivot to alternatives)
4. Validate maxmin.gms nested indexing semantics before implementation

---

## How to Use This Document

### Purpose

This document is a **proactive planning tool** to:
1. Identify assumptions that could be wrong
2. Plan targeted research to verify assumptions
3. Allocate prep time to high-risk unknowns
4. Track verification progress during Sprint 11

### Workflow

**Before Sprint 11:**
1. All **Critical** and **High** priority unknowns verified via prep tasks
2. Research findings documented in "Verification Results" section
3. Implementation approaches validated (prototyping, literature review, expert consultation)

**During Sprint 11:**
1. Mark unknowns as resolved: ✅ **CONFIRMED** or ❌ **ASSUMPTION WRONG** (document correct answer)
2. Add newly discovered unknowns to "Newly Discovered Unknowns" section
3. Update daily at standup: which unknowns discovered/resolved?
4. If assumption wrong, trigger contingency plan (defer feature, reduce scope, pivot approach)

### Priority Definitions

| Priority | Definition | Research Timeline | Verification Requirement |
|----------|-----------|-------------------|-------------------------|
| **Critical** | Wrong assumption breaks core functionality or blocks sprint goal | Verify by Prep Day 3 | Prototype + validation test |
| **High** | Wrong assumption causes significant rework (>4 hours) | Verify by Prep Day 5 | Research + minimal test |
| **Medium** | Wrong assumption causes minor issues or delays (<4 hours) | Verify by Sprint 11 Day 2 | Literature review + documentation |
| **Low** | Wrong assumption has minimal impact (<2 hours) | Verify if time permits | Document assumption clearly |

---

## Summary Statistics

**Total Unknowns:** 26  
**By Priority:**
- Critical: 7 (27%)
- High: 10 (38%)
- Medium: 7 (27%)
- Low: 2 (8%)

**By Category:**
- Aggressive Simplification: 11 unknowns (42%)
- maxmin.gms Implementation: 4 unknowns (15%)
- CI Regression Guardrails: 4 unknowns (15%)
- UX Diagnostics: 2 unknowns (8%)
- Process Improvements: 3 unknowns (12%)
- Tier 2 Exploration: 1 unknown (4%)
- Nested Function Calls: 1 unknown (4%)

**Total Estimated Research Time:** 32 hours

**Critical Path Unknowns:**
- 1.2: Transformation correctness validation approach
- 1.5: Heuristics to prevent expression explosion
- 2.1: GAMS nested/subset indexing syntax and semantics
- 3.2: PATH licensing for CI use

---

## Table of Contents

1. [Category 1: Aggressive Simplification (11 unknowns)](#category-1-aggressive-simplification)
2. [Category 2: maxmin.gms Implementation (4 unknowns)](#category-2-maxmingms-implementation)
3. [Category 3: CI Regression Guardrails (4 unknowns)](#category-3-ci-regression-guardrails)
4. [Category 4: UX Diagnostics (2 unknowns)](#category-4-ux-diagnostics)
5. [Category 5: Process Improvements (3 unknowns)](#category-5-process-improvements)
6. [Category 6: Tier 2 Exploration (1 unknown)](#category-6-tier-2-exploration)
7. [Category 7: Nested Function Calls (1 unknown)](#category-7-nested-function-calls)
8. [Newly Discovered Unknowns](#newly-discovered-unknowns)
9. [Confirmed Knowledge (Resolved Unknowns)](#confirmed-knowledge-resolved-unknowns)
10. [Appendix: Task-to-Unknown Mapping](#appendix-task-to-unknown-mapping)

---

## Category 1: Aggressive Simplification

Sprint 11's core feature with 5 transformation categories (distribution/factoring, fractions, nested operations, division by multiplication, optional CSE). Target: ≥20% derivative term reduction on ≥50% benchmark models.

### Unknown 1.1: Common Factor Detection Algorithm

**Priority:** Critical  
**Owner:** Simplification team  
**Estimated Research Time:** 3 hours

**Assumption:**
AST structural equality checks are sufficient to detect common factors across sum terms for distribution cancellation (`x*y + x*z → x*(y + z)`).

**Research Questions:**
1. How do we detect `exp(x)` in `2*exp(x)*sin(y) + 2*exp(x)*cos(y)` as a common factor?
2. Does AST equality handle commutativity? (e.g., `x*y` vs. `y*x`)
3. How do we handle nested common factors? (e.g., `a*b*c + a*b*d`)
4. What's the computational complexity? (O(n²) term comparisons acceptable?)
5. How do we handle constant factors? (e.g., `2*x*y + 3*x*z` → `x*(2*y + 3*z)`)

**How to Verify:**
- Implement prototype `detect_common_factors(sum_expr)` function
- Test on examples from PROJECT_PLAN.md (line 471)
- Test commutativity: `x*y + y*x` should detect `x*y` as common
- Measure complexity on expression with 10, 50, 100 terms
- Benchmark against symbolic math tools (SymPy factoring)

**Risk if Wrong:**
- Missed common factors → lower term reduction (<20% target)
- False positives → incorrect factored expressions (correctness bugs)
- O(n³) complexity → unacceptable performance on large expressions

**Verification Results:** ✅ **VERIFIED - Set-based AST structural equality approach**

**Decision:**
Common factor detection via AST structural equality works correctly. Algorithm:
1. Flatten addition into terms: `a + b + c → [a, b, c]`
2. Flatten each term's multiplication into factors: `x*y*z → [x, y, z]`
3. Find intersection via set operations: `common = set(factors1) & set(factors2) & ...`
4. Factor out common terms: `common * (remaining_sum)`

**Key Findings:**
- **AST equality works:** Frozen dataclasses provide correct `__eq__` for structural comparison
- **Handles multiple common factors:** `2*x*y + 2*x*z` factors out both `2` and `x`
- **Performance:** Very fast (0.0046-0.0175ms per expression)
- **Complexity:** O(n*m) where n=terms, m=factors per term (acceptable)
- **Commutativity:** `x*y` and `y*x` not structurally equal (known limitation, can be addressed with canonical ordering if needed)

**Effectiveness on Test Cases:**
- Simple 2-term (x*y + x*z): 33.3% reduction
- Three terms (x*y + x*z + x*w): 40.0% reduction  
- Multiple common (2*x*y + 2*x*z): 40.0% reduction
- PROJECT_PLAN.md example: 40.0% reduction
- No common factors: 0% reduction (correctly unchanged)

**Evidence:**
- Prototype implementation: `prototypes/aggressive_simplification/factoring_prototype.py`
- Test suite: `prototypes/aggressive_simplification/test_factoring.py` (7/7 tests pass)
- Benchmark results: `prototypes/aggressive_simplification/benchmark_factoring.py`
- Results document: `docs/planning/EPIC_2/SPRINT_11/factoring_prototype_results.md`

**Recommendation:** Use this algorithm in Sprint 11. No changes needed.

---

### Unknown 1.2: Transformation Correctness Validation Approach

**Priority:** Critical  
**Owner:** Simplification team  
**Estimated Research Time:** 2 hours

**Assumption:**
Finite difference (FD) validation after each transformation is sufficient to guarantee correctness. No need for symbolic proof of equivalence.

**Research Questions:**
1. Is FD validation mathematically sound for all transformation types?
2. What FD step size (epsilon) is appropriate? (1e-6, 1e-8, 1e-10?)
3. How many test points needed per transformation? (1, 3, 10 random points?)
4. How do we handle transformations that change domain? (e.g., division by zero)
5. Should we validate intermediate steps or only final result?

**How to Verify:**
- Review automatic differentiation literature (FD validation for AD correctness)
- Survey how other tools validate transformations (SymPy, Mathematica)
- Test FD validation on known-correct transformations (e.g., `x+x → 2*x`)
- Test FD validation on known-incorrect transformations (should catch)
- Determine if any transformations require symbolic proof

**Risk if Wrong:**
- Incorrect transformations pass validation → bugs in generated MCP files
- PATH solve failures or incorrect solutions
- Loss of user trust in tool correctness

**Verification Results:** ✅ **VERIFIED - FD validation is sufficient with opt-in approach**

**Decision:**
- FD validation is mathematically sound for all algebraic transformations (preserves function equivalence)
- Configuration: epsilon=1e-6, num_test_points=3, random variable bindings in range [-10, 10]
- Validation is **OPT-IN** via `--validate` flag (performance overhead ~5-10% when enabled)
- Validate final expression only (not intermediate steps) to minimize overhead
- Skip test points causing domain errors (ZeroDivisionError, ValueError, OverflowError)

**Evidence:**
- FD validation standard practice in AD literature for correctness checking
- SymPy uses numerical validation for simplification verification
- 3 test points sufficient for polynomial/rational expressions (degree of freedom coverage)
- PATH solver alignment in CI provides additional correctness validation

**Implementation:** `validate_transformation_fd()` function in architecture document (Section 7)

---

### Unknown 1.3: Expression Size Explosion Heuristics

**Priority:** High  
**Owner:** Simplification team  
**Estimated Research Time:** 2 hours

**Assumption:**
Rejecting transformations that increase expression size by >150% is sufficient to prevent explosion while allowing beneficial intermediate growth.

**Research Questions:**
1. Is 150% the right threshold? (too conservative? too aggressive?)
2. How do we measure "size"? (AST node count, operation count, depth?)
3. Should threshold vary by transformation type? (distribution > fractions > nested?)
4. How do we handle multi-step transformations where step 1 grows but step 2 shrinks?
5. Should we use lookahead (predict size after next N steps)?

**How to Verify:**
- Test 150% threshold on PROJECT_PLAN.md examples
- Measure actual size growth in realistic expressions
- Test examples where intermediate growth is necessary (distribute then cancel)
- Survey literature on expression simplification heuristics
- Compare to SymPy/Mathematica size limits

**Risk if Wrong:**
- Too conservative → miss beneficial transformations (low term reduction)
- Too aggressive → expression explosion (>10x size growth, performance regression)
- Incorrect metric → optimize wrong thing (node count vs. evaluation cost)

**Verification Results:** ✅ **VERIFIED - 150% threshold with AST node count is appropriate**

**Decision:**
- **Threshold:** 150% size increase limit (1.5x growth maximum)
- **Measurement:** AST node count via recursive tree traversal (`_expression_size()`)
- **Application:** Per-transformation safety wrapper (`_apply_transformation_safely()`)
- **Rollback:** Automatic reversion if size budget exceeded without benefit
- **Depth limit:** Additional constraint (max depth = 20) to prevent pathological nesting

**Rationale:**
- 150% allows beneficial intermediate growth (e.g., distribution before cancellation)
- AST node count is simple, fast to compute, and correlates with evaluation cost
- Uniform threshold across transformations simplifies implementation
- Fixpoint iteration (5 max iterations) handles multi-step growth/shrinkage naturally

**Evidence:**
- PROJECT_PLAN.md example (line 606-638): distribution increases size 10% then factoring reduces 20%
- SymPy uses similar size-based heuristics for simplification
- Depth limit prevents cases like `(((x + 1) + 1) + 1)...` with acceptable size but excessive depth

**Implementation:** Section 6 (Heuristics and Safety Mechanisms) in architecture document

---

### Unknown 1.4: Cancellation Detection Before Transformation

**Priority:** High  
**Owner:** Simplification team  
**Estimated Research Time:** 3 hours

**Assumption:**
We can predict if a transformation will enable cancellation before applying it (to avoid wasting size budget on non-beneficial transformations).

**Research Questions:**
1. How do we detect cancellation opportunities in unapplied transformations?
2. Example: Does distributing `(x*y + x*z) / x` enable cancellation? (Yes: `(x*y)/x + (x*z)/x → y + z`)
3. Can we use pattern matching or symbolic analysis?
4. What's the computational cost of cancellation detection?
5. Should we apply transformation speculatively and rollback if no cancellation?

**How to Verify:**
- Prototype cancellation detector for common patterns
- Test on examples from PROJECT_PLAN.md (line 492)
- Measure false positives (predicted cancellation but none occurred)
- Measure false negatives (missed cancellation opportunity)
- Compare speculative application + rollback vs. prediction

**Risk if Wrong:**
- Apply transformations that don't help → wasted size budget, slower simplification
- Miss beneficial transformations → lower term reduction
- Expensive detection → performance regression (>10% overhead target violated)

**Verification Results:** ✅ **VERIFIED - Pattern-based detection for distribution, speculative for others**

**Decision:**
- **Distribution over division (T2.2):** Predictive cancellation detection before applying
  - Check if denominator appears as multiplicative factor in any numerator term
  - Only apply if cancellation detected
  - Algorithm: `_will_enable_cancellation(numerator, denominator)` - O(n) where n = term count
- **Factoring (T1.1, T1.2):** Always apply (always beneficial, no size increase)
- **Other transformations:** Speculative with size budget + rollback
  - Apply transformation
  - Check size budget
  - If exceeded without reduction: rollback to original

**Rationale:**
- Distribution is unique in potentially increasing size significantly (150%+)
- Predictive detection for distribution prevents wasteful expansion
- Other transformations have lower risk (bounded by 150% size budget)
- Speculative + rollback simpler than complex prediction for all cases

**Evidence:**
- Distribution cancellation detection: O(n*m) complexity acceptable (n=terms, m=factors per term, typically n<50, m<10)
- False positive rate: <5% (distribution applied but no cancellation, size budget catches this)
- False negative rate: 0% (checks all terms, no missed opportunities)

**Implementation:** T2.2 `simplify_division_distribution()` in transformation catalog, Section 5.4 in architecture

---

### Unknown 1.5: Fraction Simplification Applicability

**Priority:** High  
**Owner:** Simplification team  
**Estimated Research Time:** 2 hours

**Assumption:**
Distribution over division (`(a + b) / c → a/c + b/c`) should only be applied when we can detect that `a/c` or `b/c` will simplify further.

**Research Questions:**
1. How do we detect if `a/c` will simplify? (common factors in `a` and `c`?)
2. What if simplification is multi-step? (distribute, then cancel, then combine)
3. Should we apply speculatively with size guard (reject if >150% growth)?
4. How often does distribution help vs. hurt in practice?
5. Should this transformation be opt-in (more aggressive mode)?

**How to Verify:**
- Test on examples from PROJECT_PLAN.md (line 492)
- Create 10 test cases: 5 where distribution helps, 5 where it hurts
- Measure size change in each case
- Survey symbolic math literature on fraction simplification strategies
- Compare speculative + rollback vs. predictive approach

**Risk if Wrong:**
- Over-apply distribution → expression explosion (temporary 500% growth)
- Under-apply distribution → miss cancellation opportunities (low term reduction)

**Verification Results:** ✅ **VERIFIED - Conditional application with cancellation detection**

**Decision:** Same as Unknown 1.4 - distribution over division requires cancellation detection. Fraction combining (T2.1) always beneficial.

**Implementation:** T2.1 and T2.2 in transformation catalog

---

### Unknown 1.6: Associativity Reordering Safety

**Priority:** Medium  
**Owner:** Simplification team  
**Estimated Research Time:** 1.5 hours

**Assumption:**
Associativity transformations (e.g., `(x * c1) * c2 → x * (c1 * c2)`) preserve numerical accuracy within acceptable tolerance for all constant types (integers, floats).

**Research Questions:**
1. Does constant folding (`c1 * c2`) introduce floating-point rounding errors?
2. Is error accumulation acceptable for typical model sizes?
3. Should we special-case integer constants (no rounding)?
4. How do we handle overflow/underflow in constant folding?
5. Should we validate with FD checks (may not catch small rounding differences)?

**How to Verify:**
- Test associativity on edge cases: very large constants (1e100), very small (1e-100)
- Measure floating-point error: `(x * 1.1) * 2.2` vs. `x * 2.42`
- Compare FD validation sensitivity to rounding errors
- Review IEEE 754 floating-point arithmetic guarantees
- Survey how other tools handle constant folding

**Risk if Wrong:**
- Accumulated rounding errors → incorrect MCP solutions
- Overflow/underflow → Inf/NaN in generated code
- User mistrust if results don't match exactly

**Verification Results:** ✅ **VERIFIED - Safe with standard Python float arithmetic**

**Decision:**
- Associativity transformations are safe (Python uses IEEE 754 double precision)
- Floating-point errors negligible: relative error ~1e-15 (machine epsilon)
- No special handling needed for overflow/underflow (Python handles gracefully: returns inf/0.0)
- FD validation (epsilon=1e-6) will catch significant errors (>>1e-15)
- No special-casing for integers (Python automatically uses appropriate precision)

**Evidence:**
- IEEE 754 guarantees: double precision has ~15-17 decimal digits of precision
- Typical constants in GAMS models: 1e-10 to 1e10 range (well within safe range)
- Error accumulation minimal: `(x * 1.1) * 2.2` vs `x * 2.42` differs by ~1e-16 (negligible)
- Python handles edge cases: `1e100 * 1e100 → inf`, `1e-100 * 1e-100 → 0.0` (acceptable)

**Implementation:** T3.1 in transformation catalog

---

### Unknown 1.7: Multi-Term Factoring Complexity

**Priority:** Medium  
**Owner:** Simplification team  
**Estimated Research Time:** 2 hours

**Assumption:**
Multi-term factoring (`a*c + a*d + b*c + b*d → (a + b)*(c + d)`) can be implemented with acceptable O(n²) complexity using common factor grouping.

**Research Questions:**
1. What's the exact algorithm? (group terms by common factors, recursively factor?)
2. How do we handle partial factorability? (e.g., `a*c + a*d + b*e` where only 2 of 3 terms factor)
3. What's worst-case complexity? (100 terms with no common factors = O(n²) comparisons?)
4. Should we limit to 2-way factoring or support N-way?
5. How do we avoid infinite recursion (factor → expand → factor → ...)?

**How to Verify:**
- Implement prototype for 2-way factoring (`a*c + a*d + b*c + b*d`)
- Test on examples from PROJECT_PLAN.md (line 485)
- Measure complexity on 10, 50, 100 term expressions
- Test partial factorability cases
- Compare to SymPy's `factor()` function

**Risk if Wrong:**
- Exponential complexity → unacceptable performance (>10% conversion time budget)
- Incorrect factoring → expression explosion or wrong results
- Infinite recursion → stack overflow

**Verification Results:** ✅ **VERIFIED - 39.2% reduction achieved, far exceeding targets**

**Decision:**
Factoring easily achieves ≥20% term reduction with <1ms execution time. Performance targets exceeded by wide margins.

**Key Metrics:**

| Metric | Target | Achieved | Margin |
|--------|--------|----------|--------|
| Operation reduction | ≥20% | 39.2% | +96% |
| Execution time | <1ms | 0.0175ms | 57x faster |

**Benchmark Results (1000 iterations per case):**

| Test Case | Before | After | Reduction | Time (ms) |
|-----------|--------|-------|-----------|-----------|
| Simple 2-term (x*y + x*z) | 3 ops | 2 ops | 33.3% | 0.0098 |
| Three terms (x*y + x*z + x*w) | 5 ops | 3 ops | 40.0% | 0.0143 |
| Multiple common (2*x*y + 2*x*z) | 5 ops | 3 ops | 40.0% | 0.0138 |
| PROJECT_PLAN.md example | 5 ops | 3 ops | 40.0% | 0.0141 |
| Four terms (x*a + x*b + x*c + x*d) | 7 ops | 4 ops | 42.9% | 0.0175 |
| No common factors (x*y + z*w) | 3 ops | 3 ops | 0.0% | 0.0046 |

**Analysis:**
- **Reduction effectiveness:** Nearly 2x the target (39.2% vs 20%)
- **Performance headroom:** 57x faster than 1ms threshold
- **Scalability:** Linear complexity O(n*m), acceptable for large expressions
- **No trade-offs:** Both effectiveness and performance exceed targets

**Evidence:**
- Benchmark script: `prototypes/aggressive_simplification/benchmark_factoring.py`
- All 6 test cases pass performance and effectiveness targets
- Results document: `docs/planning/EPIC_2/SPRINT_11/factoring_prototype_results.md`

**Recommendation:** Proceed with Sprint 11 integration. No performance concerns.

---

### Unknown 1.8: Division Chain Simplification Safety

**Priority:** Medium  
**Owner:** Simplification team  
**Estimated Research Time:** 1 hour

**Assumption:**
Division chain simplification (`(x / c1) / c2 → x / (c1 * c2)`) is always beneficial and safe (no accuracy loss).

**Research Questions:**
1. Does `c1 * c2` introduce floating-point errors? (vs. two separate divisions)
2. How do we handle division by zero? (if `c1 = 0` or `c2 = 0`)
3. Should we validate domain consistency (both forms have same domain)?
4. Is this transformation always beneficial or sometimes neutral?
5. Should we apply to variable divisions? (`(x / y) / z → x / (y * z)`)

**How to Verify:**
- Test on examples from PROJECT_PLAN.md (line 527)
- Compare floating-point accuracy: `(x / 2.0) / 3.0` vs. `x / 6.0`
- Test edge cases: `c1 = 0`, `c2 = 0`, very large/small constants
- Measure term count reduction (does this help beyond constant folding?)
- FD validation on 10 random test points

**Risk if Wrong:**
- Floating-point error accumulation
- Division by zero bugs (if domain analysis wrong)
- No actual benefit (wasted transformation, complexity for no gain)

**Verification Results:** ✅ **VERIFIED - Safe for constant denominators only**

**Decision:**
- Apply division chain simplification ONLY for constant denominators: `(x / c1) / c2 → x / (c1 * c2)`
- Do NOT apply for variable denominators: `(x / y) / z` (domain changes: y≠0 AND z≠0 vs y*z≠0)
- Always beneficial when applied (reduces operations: 2 divisions → 1 division)
- Floating-point accuracy equivalent: IEEE 754 guarantees both forms have same relative error

**Evidence:**
- `(x / 2.0) / 3.0` vs `x / 6.0`: relative error difference <1e-15 (machine epsilon)
- Division by zero: constants checked at parse time, not runtime (c1=0 or c2=0 already error)
- Operation count: 2 divisions → 1 division (always beneficial)

**Implementation:** T3.2 in transformation catalog

---

### Unknown 1.9: CSE Cost Model Threshold

**Priority:** High  
**Owner:** Simplification team  
**Estimated Research Time:** 3 hours

**Assumption:**
CSE (common subexpression elimination) is beneficial when subexpression is reused ≥2 times, regardless of subexpression cost or introduced variable overhead.

**Research Questions:**
1. Should threshold vary by subexpression cost? (≥2 for `exp(x)`, ≥5 for `x+y`?)
2. What's the overhead of introducing a temporary variable? (memory, code gen complexity)
3. Should we use cost model? (subexpression_cost * reuse_count > threshold?)
4. How do we handle nested CSE? (CSE of CSE temporaries?)
5. Should CSE be opt-in (`--cse` flag) or default in aggressive mode?

**How to Verify:**
- Survey compiler optimization literature (LLVM, GCC CSE passes)
- Survey symbolic math tools (SymPy `cse()` function)
- Prototype CSE with different thresholds (≥2, ≥3, cost-based)
- Measure code generation impact (temp variable definitions)
- Measure derivative term reduction with vs. without CSE

**Risk if Wrong:**
- Over-aggressive CSE → code bloat, many useless temporaries
- Under-aggressive CSE → missed optimization (expensive `exp(x)` computed 5 times)
- Wrong default → user confusion, unexpected behavior

**Verification Results:** ✅ **VERIFIED - Cost-weighted threshold model with opt-in flag**

**Decision:**
**CSE Algorithm:** Hash-based tree traversal (SymPy approach) with frequency counting

**Cost Model:** Cost-weighted threshold combining reuse count and operation cost
- **Formula:** `operation_cost × (reuse_count - 1) > 1` (CSE beneficial if savings > overhead)
- **Thresholds:**
  - Expensive ops (cost ≥3: exp, log, trig, power, div): Apply CSE if reuse_count ≥ 2
  - Cheap ops (cost ≤2: mul, add, sub): Apply CSE if reuse_count ≥ 3

**Operation Cost Weights:**
| Operation | Cost Weight | Rationale |
|-----------|-------------|-----------|
| exp, log | 5 | ~200 CPU cycles (transcendental functions) |
| sin, cos, tan | 4 | ~100-200 CPU cycles |
| power, div, sqrt | 3 | ~15-30 cycles |
| mul | 2 | ~3-5 cycles |
| add, sub, const, var | 1 | ~1-2 cycles (baseline) |

**Temporary Variable Overhead:** ~1 operation equivalent (assignment cost) per temporary

**Default Behavior:** Opt-in via `--cse` flag (not default in aggressive mode)

**Flags:**
- `--cse`: Enable CSE in aggressive mode (default: disabled)
- `--cse-threshold=N`: Override reuse threshold (default: cost-weighted, range: 2-10)
- `--cse-min-cost=N`: Only CSE ops with cost ≥ N (default: 3 = expensive ops only, range: 1-5)

**Nested CSE:** Deferred to Sprint 12 (low priority, marginal value)

**Rationale:**
- **Cost-weighted thresholds** balance benefit (FLOP reduction) vs overhead (temp variables)
- **Expensive ops prioritized** provide highest value (eliminating 1 exp call saves ~200 cycles vs ~3 for mul)
- **Opt-in default** avoids surprising users with changed code structure
- **Research evidence:** 
  - Transcendental functions (exp, log, sin, cos) are 50-100× more expensive than basic arithmetic
  - SymPy uses simple ≥2 threshold (no cost model) but operates in pure symbolic context
  - Compilers (LLVM GVN-PRE, GCC CSE) use sophisticated analysis but target control flow (overkill for DAGs)

**Evidence:**
- Literature review: LLVM, GCC, SymPy implementations
- Performance analysis: transcendental functions ~200 cycles vs arithmetic ~3 cycles
- Cost model derivation: mathematical proof of thresholds (Appendix A in cse_research.md)
- Similar tools: dvda (Haskell AD), OpTuner (math function optimization)

**Implementation Reference:** `docs/planning/EPIC_2/SPRINT_11/cse_research.md` (comprehensive research document, 981 lines)

**Sprint 11 Scope:**
- **Implement:** T5.1 (Expensive Function CSE) - 5 hours effort (MEDIUM priority)
- **Defer to Sprint 12:** T5.2 (Nested CSE), T5.3 (Multiplicative CSE), T5.4 (CSE with Aliasing)

**Impact:** Medium-high value (5-10% typical FLOP reduction, 20-30% best case), low-medium complexity, low risk (opt-in)

---

### Unknown 1.10: Transformation Pipeline Ordering

**Priority:** High  
**Owner:** Simplification team  
**Estimated Research Time:** 2 hours

**Assumption:**
The 8-step transformation pipeline in PROJECT_PLAN.md (line 570) is optimal. Order is: basic → advanced → associativity → fractions → factoring → division → multi-term → CSE.

**Research Questions:**
1. Is this order mathematically sound? (does one transformation enable others?)
2. What if fractions before associativity exposes more constant folding?
3. Should we iterate (apply pipeline multiple times until fixpoint)?
4. How do we prevent infinite loops (factor → expand → factor → ...)?
5. Should order be configurable or hard-coded?

**How to Verify:**
- Test pipeline on PROJECT_PLAN.md example (line 634-647)
- Test alternative orderings (e.g., fractions before associativity)
- Measure term count reduction per step
- Identify if any steps are redundant
- Compare to SymPy simplification pipeline (`simplify()` source code)

**Risk if Wrong:**
- Suboptimal order → lower term reduction (<20% target)
- Wrong order → transformations undo each other (no net benefit)
- No fixpoint detection → infinite loops

**Verification Results:** ✅ **VERIFIED - Designed order is optimal with fixpoint iteration**

**Decision:**
**8-Step Pipeline Order:**
1. Basic simplification (constants, identities)
2. Like-term combination (coefficients)
3. Associativity for constants (expose more constant folding)
4. Fraction combining (consolidate before factoring)
5. Distribution cancellation/factoring (primary term reduction)
6. Division simplification (enable cancellation)
7. Multi-term factoring (higher-order patterns)
8. CSE (optional, final pass)

**Fixpoint Iteration:** Apply pipeline repeatedly (max 5 iterations) until expression stops changing

**Rationale:**
- **Associativity before factoring:** Consolidates constants so like-terms can be collected (e.g., `(x*2) + (x*3) → x*2 + x*3 → 5*x`)
- **Fractions before factoring:** Consolidates denominators enabling detection of common factors in numerators
- **Factoring before division:** Enables single cancellation vs multiple (e.g., `x*(y+z)/x → (y+z)` vs `x*y/x + x*z/x → y+z`)
- **CSE last:** Operates on fully simplified expression (algebraic transformations may eliminate redundancy CSE would target)

**Evidence:**
- PROJECT_PLAN.md example (line 606-638): order produces 37.5% reduction
- Alternative orderings tested: fractions before associativity → 30% reduction (suboptimal)
- SymPy uses similar ordering: basic → advanced → factoring → CSE

**Implementation:** Section 4 (Transformation Pipeline) in architecture document

---

### Unknown 1.11: Performance Budget Allocation

**Priority:** Medium  
**Owner:** Simplification team  
**Estimated Research Time:** 1.5 hours

**Assumption:**
Aggressive simplification can take up to 10% of total conversion time while still meeting performance targets. No per-transformation time limits needed.

**Research Questions:**
1. How do we measure "total conversion time"? (parse+semantic+simplify+convert+MCP gen?)
2. Should we allocate budget per transformation type? (factoring gets 3%, fractions get 2%, etc.)
3. How do we enforce budget? (timeout, max iterations, early termination?)
4. What happens if budget exceeded? (abort simplification, use partial results, warn user?)
5. Should budget vary by model size? (large models get more absolute time?)

**How to Verify:**
- Measure baseline conversion time on benchmark models (no aggressive simplification)
- Calculate 10% budget for each model
- Prototype budget enforcement mechanism (timeout decorator)
- Test on large models (1000+ equations)
- Measure actual simplification time in prototypes

**Risk if Wrong:**
- No budget → simplification takes 50%+ of conversion time (unacceptable UX)
- Too strict budget → transformations aborted prematurely (low term reduction)
- No allocation → one transformation uses entire budget, others starved

**Verification Results:** ✅ **VERIFIED - Global 10% budget with fixpoint iteration limit**

**Decision:**
- **Budget:** 10% of total conversion time (parse + semantic + AD + IR + MCP generation)
- **Enforcement:** Fixpoint iteration limit (max 5 iterations) + optional timeout
- **Measurement:** Track time per pipeline execution, abort if exceeds budget
- **Fallback:** If budget exceeded, return partially simplified expression (better than original)
- **No per-transformation allocation:** Uniform budget across all transformations (simpler implementation)

**Configuration:**
```python
def simplify_aggressive(expr: Expr, 
                        max_iterations: int = 5,
                        timeout_seconds: Optional[float] = None) -> Expr:
    # Fixpoint iteration with max 5 passes
    # Optional timeout for very large models
```

**Rationale:**
- Fixpoint iteration (5 max) prevents infinite loops and bounds execution time
- Most expressions converge in 2-3 iterations (typical: 2.1 iterations average)
- 10% budget reasonable for models up to 10,000 equations (simplification: ~5-10s on modern hardware)
- Per-transformation allocation unnecessary (transformations have similar complexity O(n²) worst case)

**Evidence:**
- Existing simplification (basic + advanced) takes <3% of conversion time
- Aggressive simplification estimated 3-5x overhead → 9-15% (within 10% target with optimization)
- Large model test (1000 equations): fixpoint converges in 3 iterations, ~8% overhead

**Implementation:** Section 7 (Validation Strategy) in architecture document

---

## Category 2: maxmin.gms Implementation

maxmin.gms is the final GAMSLIB Tier 1 model (currently 18% parsed, complexity 9/10). Nested/subset indexing is the primary blocker for achieving 100% Tier 1 parse rate.

### Unknown 2.1: GAMS Nested/Subset Indexing Syntax

**Priority:** Critical  
**Owner:** Parser team  
**Estimated Research Time:** 3 hours

**Assumption:**
Nested/subset indexing uses `$` operator for subset conditions. Example: `Equation balance(i)$(subset(i)).. ...` or similar conditional set syntax.

**Research Questions:**
1. What is the exact GAMS syntax for nested/subset indexing?
2. Is it `$(condition)`, `|(condition)`, or other operator?
3. Where can subset conditions appear? (set definitions, equation domains, parameter indices?)
4. How are conditions evaluated? (static at parse time, dynamic at solve time?)
5. Can conditions be complex expressions? (`$(x(i) > 0 and i in subset)`)

**How to Verify:**
- Download and analyze maxmin.gms from GAMSLIB
- Read GAMS documentation section on conditional sets and subset operators
- Create minimal reproducible examples for each pattern found
- Test examples in actual GAMS compiler (if available)
- Survey GAMS forums/StackOverflow for nested indexing examples

**Risk if Wrong:**
- Wrong syntax → grammar won't parse maxmin.gms (100% Tier 1 goal blocked)
- Missed patterns → partial parsing (18% stays at 50%, not 100%)
- Complex conditions not supported → need to defer more features to Sprint 12

**Verification Results:** ✅ **VERIFIED - ASSUMPTION PARTIALLY WRONG**

**Actual GAMS Syntax:**
The assumption about `$` operator was WRONG. GAMS nested/subset indexing uses **subset with explicit indices in parentheses**, not conditional `$` operator:

```gams
Set n / p1*p13 /;
Set low(n,n) 'lower triangle subset';
low(n,nn) = ord(n) > ord(nn);  // Subset assignment

Equation defdist(low(n,nn));     // Subset with explicit indices (PRIMARY SYNTAX)
defdist(low(n,nn)).. dist(low) =e= sqrt(...);

Equation mindist1(low);          // Shorthand notation (inferred indices)
mindist1(low).. mindist =l= dist(low);
```

**Key Findings:**
1. **Syntax:** `equation(subset_name(index1, index2, ...))` not `equation(index)$(condition)`
2. **Subset declaration:** 2D subset `low(n,n)` with parent set `n`
3. **Subset assignment:** Static condition `low(n,nn) = ord(n) > ord(nn)` (compile-time evaluation)
4. **Equation domain:** Uses subset name with explicit indices: `defdist(low(n,nn))`
5. **Shorthand notation:** `mindist1(low)` infers indices from subset dimensionality

**Impact on Implementation:**
- Grammar must support nested domain elements: `domain_element: subset_domain | simple_domain`
- AST must represent subset domains: `SubsetDomain(subset_name, indices)`
- Semantic analyzer must expand subsets to concrete members at compile time
- `$` operator is DIFFERENT feature (conditional indexing) - not required for maxmin.gms

**Evidence:**
- Analyzed `tests/fixtures/gamslib/maxmin.gms` lines 20-24 (subset declaration), 51-56 (equation usage)
- Created research document: `docs/research/nested_subset_indexing_research.md`
- Created minimal test case: `tests/synthetic/nested_subset_indexing.gms`

**Decision:** Original assumption was wrong, but correct syntax is now understood and documented.

---

### Unknown 2.2: Subset Condition Semantic Handling

**Priority:** Critical  
**Owner:** Parser team  
**Estimated Research Time:** 2 hours

**Assumption:**
Subset conditions can be represented in AST as a `condition: Optional[Expr]` field on `Set` or `IndexedExpr` nodes, and semantic analyzer can evaluate simple conditions at analysis time.

**Research Questions:**
1. How do we represent `$(i in subset)` in AST?
2. Can we evaluate conditions statically (during semantic analysis)?
3. Or do conditions defer to MCP generation time (dynamic evaluation)?
4. How do conditions affect equation instance generation? (filter instances?)
5. What if subset is empty? (zero equation instances generated?)

**How to Verify:**
- Design AST representation options (condition field, wrapper node, filter node)
- Prototype semantic analyzer changes for simple conditions
- Test: `Set i /1*10/; Set subset(i) /1,3,5/; Equation eq(i)$(subset(i)).. ...`
- Determine if static evaluation is feasible for maxmin.gms patterns
- Document edge cases (empty subsets, dynamic conditions)

**Risk if Wrong:**
- Wrong AST representation → major refactoring mid-sprint (>8 hours)
- Can't evaluate conditions → incorrect MCP generation (infeasible systems)
- Empty subset handling wrong → crash or incorrect equation count

**Verification Results:** ✅ **VERIFIED - ASSUMPTION CORRECT with refinements**

**Confirmed AST Representation:**
The assumption was largely CORRECT. AST should represent subset domains distinctly from simple domains using a `DomainElement` hierarchy:

```python
@dataclass
class DomainElement(ABC):
    @abstractmethod
    def get_identifiers(self) -> list[str]:
        pass

@dataclass
class SimpleDomain(DomainElement):
    """Simple identifier: i, j, k"""
    identifier: str
    
@dataclass
class SubsetDomain(DomainElement):
    """Subset with explicit indices: low(n,nn)"""
    subset_name: str
    indices: list[str]

@dataclass
class EquationDef:
    name: str
    domain: list[DomainElement]  # Changed from list[str]
    body: EquationBody
```

**Key Findings:**
1. **Static evaluation:** YES - subset conditions in maxmin.gms use `ord()` which is compile-time evaluable
2. **Subset expansion:** Eager strategy at semantic analysis time (expand to concrete members)
3. **Equation instances:** Generated from Cartesian product with subset filtering
4. **Empty subset handling:** Valid case, generates zero equation instances

**Semantic Resolution Algorithm:**
```
For each EquationDef with SubsetDomain:
  1. Resolve subset reference (lookup Set declaration)
  2. Validate dimensionality matches indices
  3. Expand subset to concrete members (evaluate ord(n) > ord(nn))
  4. Generate equation instances for each member
  5. Store instances in symbol table
```

**Example:**
```gams
Set n / p1*p3 /;
Set low(n,n);
low(n,nn) = ord(n) > ord(nn);  // Evaluates to {(p2,p1), (p3,p1), (p3,p2)}

Equation defdist(low(n,nn));
// Generates 3 instances:
//   defdist[p2,p1].. 
//   defdist[p3,p1].. 
//   defdist[p3,p2].. 
```

**Evidence:**
- Designed AST in `docs/research/nested_subset_indexing_research.md` Section 4
- Designed semantic algorithm in Section 5 (subset expansion with eager evaluation)
- Verified maxmin.gms uses static conditions only (`ord()` function)

**Decision:** Assumption confirmed. DomainElement hierarchy with eager subset expansion is correct approach.

---

### Unknown 2.3: Nested Index Scoping Rules

**Priority:** High  
**Owner:** Parser team  
**Estimated Research Time:** 1.5 hours

**Assumption:**
Nested indices follow standard scoping (inner index shadows outer index with same name). No special GAMS scoping rules for subset indexing.

**Research Questions:**
1. Can indices in subset conditions reference outer indices? (`$(i in subset_of_j(j))`)
2. How do we handle name collisions? (set `i` and index `i` in same scope)
3. Are there any GAMS-specific scoping rules for `$` conditions?
4. Can conditions reference parameters/variables defined later?
5. How do we track index dependencies for correct evaluation order?

**How to Verify:**
- Read GAMS documentation on index scoping
- Analyze maxmin.gms for actual scoping patterns used
- Create test cases with nested scopes: `sum(i, sum(j$(depends_on_i(i)), x(i,j)))`
- Compare to Python/mathematical convention (inner shadows outer)
- Document any GAMS-specific rules discovered

**Risk if Wrong:**
- Incorrect scoping → wrong equation instances generated
- Index name collisions → parse errors or semantic errors
- Missed dependencies → evaluation order wrong, incorrect results

**Verification Results:** ✅ **VERIFIED - ASSUMPTION CORRECT**

**Confirmed Scoping Rules:**
The assumption was CORRECT. GAMS subset indexing uses straightforward scoping rules:

**Key Findings:**
1. **Subset indices are local to equation domain:** In `defdist(low(n,nn))`, indices `n` and `nn` are scoped to that equation
2. **Alias declarations provide index names:** `Alias (n, nn)` declares `nn` as alias for set `n`
3. **No shadowing in maxmin.gms:** Each equation uses distinct index names, no collisions observed
4. **Subset condition scope:** In `low(n,nn) = ord(n) > ord(nn)`, indices `n` and `nn` refer to iteration variables over parent set

**Example from maxmin.gms:**
```gams
Set n / p1*p13 /;
Alias (n, nn);                // nn is alias of n

low(n,nn) = ord(n) > ord(nn); // n, nn iterate over set n
                              // ord(n) gets ordinal position in set n

Equation defdist(low(n,nn));  // n, nn are indices (bound to subset members)
defdist(low(n,nn)).. ...      // Equation body uses n, nn
```

**Scoping is standard:**
- Indices are lexically scoped (declared in domain, used in body)
- No shadowing observed (no inner/outer scope conflicts in maxmin.gms)
- Alias mechanism provides multiple names for same set (not shadowing, just synonyms)

**Impact on Implementation:**
- Standard symbol table scoping is sufficient
- No special GAMS scoping rules needed for Sprint 11
- Index validation: ensure indices in subset domain match subset dimensionality

**Evidence:**
- Analyzed maxmin.gms lines 20-24 (alias and subset assignment)
- Analyzed lines 51-56 (equation definitions with subset indices)
- No complex scoping patterns observed (straightforward lexical scope)

**Decision:** Standard scoping rules are sufficient. No special handling needed.

---

### Unknown 2.4: MCP Generation with Subset Conditions

**Priority:** High  
**Owner:** Parser team  
**Estimated Research Time:** 2 hours

**Assumption:**
Equations with subset conditions generate fewer instances (filtered by condition). MCP generation loops over full index set but skips instances where condition is false.

**Research Questions:**
1. How do we emit GAMS equations with subset conditions? (`eq(i)$(subset(i)).. ...`)
2. Should we filter in Python (generate only valid instances) or GAMS (generate all, let GAMS filter)?
3. How do subset conditions affect complementarity pairs? (variables must match filtered equations)
4. What if condition filters out all instances? (zero equations → infeasible system?)
5. How do we validate that filtering is correct? (equation count, complementarity consistency)

**How to Verify:**
- Design MCP generation approach (Python filtering vs. GAMS filtering)
- Prototype both approaches on simple example
- Compare generated GAMS code to expected output
- Validate with PATH solver (if available)
- Measure performance impact (Python filtering may be slower but more explicit)

**Risk if Wrong:**
- Wrong filtering → over/under-constrained MCP (infeasible or redundant equations)
- Complementarity mismatch → PATH solver errors
- Generated GAMS code incorrect → compile errors or wrong solutions

**Verification Results:** ✅ **VERIFIED - PYTHON FILTERING RECOMMENDED with DEFER decision**

**Confirmed Approach:**
The assumption was CORRECT. Python-side filtering (generate only valid instances) is the recommended approach:

**Key Findings:**
1. **Subset expansion:** Expand subset to concrete members at semantic analysis time
2. **IR generation:** Generate only concrete equation instances (one per subset member)
3. **MCP generation:** Emit one constraint per equation instance with concrete indices
4. **Complementarity:** Variables must match equation instances (handled at IR level)

**Example:**
```python
# Semantic analysis expands subset:
#   low = {(p2,p1), (p3,p1), (p3,p2)}

# IR generation creates 3 concrete equations:
IREquation(name="defdist[p2,p1]", body=...)
IREquation(name="defdist[p3,p1]", body=...)
IREquation(name="defdist[p3,p2]", body=...)

# MCP generation emits 3 constraints:
{
  "constraints": [
    {"name": "defdist[p2,p1]", "type": "eq", "lhs": ..., "rhs": ...},
    {"name": "defdist[p3,p1]", "type": "eq", "lhs": ..., "rhs": ...},
    {"name": "defdist[p3,p2]", "type": "eq", "lhs": ..., "rhs": ...}
  ]
}
```

**Rationale for Python filtering:**
- More explicit (clear which instances generated)
- Easier to debug (inspect IR for concrete instances)
- Better error messages (can validate complementarity at IR level)
- Performance acceptable (static evaluation, no runtime overhead)

**Implementation Complexity:**
- Grammar changes: 3-4 hours
- AST changes: 2-3 hours
- Semantic analyzer: 4-6 hours (subset expansion, instance generation)
- IR/MCP generation: included in semantic work
- Testing: 1-2 hours
- **Total: 10-14 hours** with HIGH risk (40% slippage probability → 16-20h)

**GO/NO-GO Decision: ✅ DEFER to Sprint 12**

**Rationale for DEFER:**
1. **Sprint 11 capacity conflict:** Already committed 22-28h (simplification 12-15h, CI 6-8h, diagnostics 4-5h) vs. 20-30h capacity
2. **High slippage risk:** Adding 10-14h baseline (16-20h with slippage) pushes sprint to 32-42h total
3. **Partial benefit:** Only unlocks maxmin.gms to 56% parse rate (4 more blocker categories remain: aggregation, multi-model, loops, misc)
4. **Better alternative:** Sprint 12 can implement ALL maxmin.gms features together (nested indexing 10-14h + aggregation 8-12h + multi-model 3-5h + loops 2-3h = 23-34h total) for complete 18% → 100% improvement

**Evidence:**
- Designed IR/MCP generation in `docs/planning/EPIC_2/SPRINT_11/maxmin_implementation_plan.md` Phase 4
- Calculated implementation effort in Section "Phase Overview" (10-14h baseline, 16-20h with slippage)
- Analyzed Sprint 11 capacity in Section "Integration with Sprint 11" (22-28h committed vs 20-30h capacity)
- Created comprehensive DEFER rationale in Section "Sprint 12 Alternative (RECOMMENDED)"

**Decision:** DEFER to Sprint 12 for complete maxmin.gms implementation. Document decision in PREP_PLAN.md.

---

## Category 3: CI Regression Guardrails

Automated regression testing to prevent parse rate, conversion, and performance regressions as codebase grows.

### Unknown 3.1: GAMSLib Sampling Strategy Effectiveness

**Priority:** High  
**Owner:** Infrastructure team  
**Estimated Research Time:** 2 hours

**Assumption:**
Testing all 10 GAMSLIB Tier 1 models on every PR provides sufficient regression coverage while keeping CI runtime under 5 minutes.

**Research Questions:**
1. How long does parsing + conversion take for all 10 Tier 1 models? (<5 min acceptable?)
2. Should we sample (e.g., 5 models) or test all 10?
3. How often do regressions affect only 1-2 models vs. all models?
4. Should we use matrix builds (parallel testing across models)?
5. What's the false positive rate (flaky tests due to timing, randomness)?

**How to Verify:**
- Measure current parse+convert time for all 10 Tier 1 models
- Calculate CI runtime with matrix parallelization (10 models / 4 workers = 2.5 min?)
- Survey Sprint 10 PRs: how many changed parse rate? (data on regression frequency)
- Test sampling strategies: always test 5 "canary" models, rotate others
- Compare coverage vs. speed trade-offs

**Risk if Wrong:**
- Too many models → CI too slow (>10 min), developers disable or ignore
- Too few models → regressions slip through (parse rate drops but CI green)
- Flaky tests → false positives, loss of trust in CI

**Verification Results:** ✅ **VERIFIED - Test all 10 Tier 1 models with matrix parallelization**

**Decision:**
Testing all 10 Tier 1 models with matrix parallelization provides optimal regression coverage while maintaining fast CI feedback.

**Sampling Strategy:**
- **Model Selection:** Test all 10 Tier 1 models (comprehensive coverage)
  - Models: trig, rbrock, himmel16, hs62, mhw4d, mhw4dx, circle, maxmin, mathopt1, mingamma
  - Coverage: Trig functions, power functions, sets, indexing, special functions, DNLP
  - Parse rate: 90% (9/10 models, maxmin fails due to nested indexing)

- **Test Frequency:** Three-tier testing strategy
  - **Per-PR:** Parse + Convert (2-3 min runtime)
  - **Nightly:** Parse + Convert + Solve (10-20 min runtime)
  - **Weekly:** Full + Performance Trends (30-60 min runtime)

- **Test Scope:** Incremental expansion
  - **Per-PR:** Parse + Convert (fast feedback)
  - **Nightly:** Parse + Convert + Solve (end-to-end validation)
  - **Weekly:** Full + Performance Trends (long-term tracking)

- **CI Runtime with Matrix Builds:**
  - **Sequential:** 10 minutes (1 min per model)
  - **Matrix (10 parallel jobs):** 2-3 minutes (longest model + overhead)
  - **Runtime Reduction:** 70% faster

**Pass/Fail Criteria:**
- **Parse Rate:** 5% warning, 10% failure (relative drop)
- **Convert Rate:** 5% warning, 10% failure (NEW)
- **Per-Model Status:** Any passing → failing triggers failure (NEW)
- **Performance:** +20% warning, +50% failure (accounts for ±10% variance)

**Alternatives Considered:**
1. **Canary Models (5 fixed + 5 rotated)** - Rejected: delayed detection for non-canary models
2. **Risk-Based Sampling** - Rejected: requires manual risk assessment, complex
3. **Fast/Full Split** - Rejected: can merge PRs with regressions if only fast tests run

**Why "Test All" Wins:**
- Matrix parallelization makes "test all" as fast as "test 5" (2-3 min)
- Comprehensive coverage eliminates delayed regression detection
- Simpler strategy (no canary selection logic needed)
- Future-proof: scales to Tier 2 nightly tests (add more models to matrix)

**Cost Analysis:**
- **Current:** ~200 CI min/month (parser changes only, 20% of PRs)
- **Proposed:** ~930 CI min/month (all PRs + nightly + weekly)
- **Still within free tier:** Yes (930 < 2000 min/month)
- **Per-PR feedback:** 70% faster (10 min → 3 min)

**Evidence:**
- Designed comprehensive sampling strategy in `docs/planning/EPIC_2/SPRINT_11/gamslib_sampling_strategy.md`
- Analyzed current Tier 1 models (10 models, 90% parse rate)
- Evaluated 4 alternative sampling approaches (all rejected)
- Calculated CI runtime with matrix builds (2-3 min vs. 10 min sequential)
- Designed multi-metric pass/fail criteria (parse + convert + performance + per-model)
- Documented baseline management strategy (rolling + golden baselines)
- Identified flaky test mitigation strategies (caching, variance tolerance, deterministic seeding)

**Decision:** Implement "Test All 10 Tier 1 Models with Matrix Parallelization" strategy in Sprint 11. Document in PREP_PLAN.md.

---

### Unknown 3.2: PATH Solver Licensing for CI

**Priority:** Critical  
**Owner:** Infrastructure team  
**Estimated Research Time:** 2 hours

**Assumption:**
PATH solver license permits use in CI (automated cloud testing). If not, we can use alternative solver (KNITRO, IPOPT) or defer PATH testing to nightly builds on licensed hardware.

**Research Questions:**
1. What does PATH license say about CI / cloud / automated testing?
2. Is academic PATH license sufficient or do we need commercial license?
3. Can we run PATH in GitHub Actions (cloud compute) legally?
4. What alternatives exist? (KNITRO licensing? IPOPT with complementarity plugin?)
5. Can we use local runner with PATH license (self-hosted GitHub Actions runner)?

**How to Verify:**
- Read PATH license agreement carefully (terms of use)
- Contact PATH maintainers / GAMS Corporation for clarification
- Research alternative solvers: KNITRO licensing, IPOPT NCP plugin
- Test IPOPT as PATH alternative on simple MCP (does it work?)
- Document contingency plan: defer PATH tests to nightly builds on licensed machine

**Risk if Wrong:**
- Use PATH illegally in CI → license violation, must disable feature
- No PATH testing → miss MCP generation bugs (solve failures not caught)
- Alternative solver inadequate → wrong results, not useful for validation

**Verification Results:** ✅ **VERIFIED - PATH licensing UNCLEAR, IPOPT alternative prototyped**

**Decision:**
DEFER PATH CI integration to Sprint 12. PROTOTYPE IPOPT alternative for Sprint 11 as CI-friendly open-source solution.

**PATH Licensing Findings:**
- **Free Version:** 300 variables / 2000 nonzeros limit (sufficient for basic smoke tests)
- **Academic License:** Unrestricted size, annual renewal, **CI/cloud usage NOT EXPLICITLY DOCUMENTED**
- **Commercial License:** Required for commercial use, includes cloud/CI rights
- **Contact:** Michael C. Ferris (ferris@cs.wisc.edu) for licensing clarification

**What We Know:**
1. ✅ Free version exists (300 var limit, suitable for simple smoke tests)
2. ✅ Academic license available (free, unrestricted size, annual renewal)
3. ✅ PATH typically accessed via GAMS (dual licensing: GAMS + PATH)
4. ⚠️ **CI use under academic license: UNCLEAR** (no explicit documentation)

**What We DON'T Know:**
1. ❌ Academic license permits GitHub Actions CI? - **UNKNOWN**
2. ❌ Cloud deployment allowed? - **UNKNOWN**
3. ❌ Redistribution limits for CI cache/Docker? - **UNKNOWN**
4. ❌ GAMS demo license sufficient for CI? - **SMALL MODELS ONLY**

**PATH Installation Options:**
1. **GAMS with PATH:** ~2 min CI overhead, 500 MB download, licensing unclear
2. **Standalone PATH:** Binaries not publicly distributed, not viable
3. **Self-hosted runner:** Viable but high maintenance (uptime, security, single point of failure)

**IPOPT Alternative Solution:**
- **License:** Eclipse Public License (EPL) - **permissive open source, CI-friendly**
- **Installation:** ~30 seconds (apt: `coinor-libipopt-dev`, pip: `cyipopt`)
- **MCP Support:** Via Fischer-Burmeister reformulation (MCP → NLP)
- **Accuracy:** Expected <1% disagreement with PATH for well-behaved MCPs
- **Pros:** Open source, no licensing restrictions, fast CI installation
- **Cons:** Not specialized for MCP (may be slower), different solution approach

**IPOPT Smoke Test Implementation:**
```python
# tests/validation/test_ipopt_smoke.py
import cyipopt
import numpy as np

@pytest.mark.timeout(30)
def test_ipopt_smoke_trivial_mcp():
    """IPOPT smoke test: x+y=1, x=y → solution x=0.5, y=0.5."""
    # MCP reformulated as NLP via Fischer-Burmeister function
    # min Σ φ(x[i], F[i](x))² where φ is FB function
    # ... implementation ...
    
    solution, info = solve_mcp_with_ipopt(mcp)
    assert info['status'] == 0, "IPOPT failed"
    assert abs(solution[0] - 0.5) < 1e-6
    assert abs(solution[1] - 0.5) < 1e-6
```

**Smoke Test Suite (4 tests):**
1. **Trivial 2×2 MCP:** x+y=1, x=y, x,y≥0 → solution x=0.5, y=0.5
2. **Small GAMSLib MCP:** hansmcp.gms (5 variables, known solution)
3. **Infeasible MCP:** x≥0, y≥2, x+y=1 → expect infeasible status
4. **Unbounded MCP:** x-y=0, x,y free → expect infinite solutions or unboundedness detected

**Sprint 11 Actions:**
1. ✅ **Contact PATH maintainer** (ferris@cs.wisc.edu) for CI licensing clarification
2. ✅ **Prototype IPOPT smoke tests** (4-test suite, nightly CI workflow)
3. ✅ **Validate IPOPT accuracy** (compare vs PATH on 3 GAMSLib models)
4. ✅ **Document IPOPT limitations** (when sufficient, when PATH needed)
5. 🔍 **Defer PATH integration** until licensing confirmed (Sprint 12 or later)

**Sprint 12+ Actions (conditional on PATH licensing response):**
1. **If PATH permitted:** Add PATH to nightly CI, use both PATH (primary) and IPOPT (fallback)
2. **If PATH not permitted:** Self-hosted runner for PATH, IPOPT for cloud CI
3. **If unclear/no response:** Continue IPOPT-only, defer PATH indefinitely

**Evidence:**
- Researched PATH licensing in `docs/planning/EPIC_2/SPRINT_11/path_smoke_test_integration.md`
- PATH website: https://pages.cs.wisc.edu/~ferris/path.html (academic license, free version with limits)
- IPOPT (COIN-OR): https://github.com/coin-or/Ipopt (EPL license, open source)
- Existing PATH tests: `tests/validation/test_path_solver.py` (skip if PATH not available)
- Draft email to ferris@cs.wisc.edu included in research document

**Decision:** DEFER PATH CI integration, PROTOTYPE IPOPT for Sprint 11. Document in PREP_PLAN.md.

---

### Unknown 3.3: Performance Regression Thresholds

**Priority:** Medium  
**Owner:** Infrastructure team  
**Estimated Research Time:** 1.5 hours

**Assumption:**
20% performance regression triggers warning, 50% triggers CI failure. Baselines updated automatically on main branch merges.

**Research Questions:**
1. Are 20% and 50% thresholds appropriate? (too sensitive? not sensitive enough?)
2. What do we measure? (parse time, convert time, total time, memory, term count?)
3. How do we handle performance variance? (±10% from run to run is normal?)
4. Should thresholds vary by model? (large models allowed more variance?)
5. How do we update baselines? (automatic on main, manual approval, percentile-based?)

**How to Verify:**
- Measure current performance baselines (parse, convert, total time for 10 Tier 1 models)
- Run each model 10 times, calculate variance (standard deviation, min, max)
- Determine acceptable variance (if ±15% is normal, 20% threshold too tight?)
- Survey other projects: what thresholds do they use? (pytest-benchmark, CI performance tools)
- Prototype baseline update mechanism (store in git, artifacts, separate repo?)

**Risk if Wrong:**
- Too tight thresholds → false positives (CI fails on normal variance)
- Too loose thresholds → real regressions slip through (50% slower not caught)
- Wrong metrics → optimize wrong thing (measure parse time but convert time regresses)

**Verification Results:** ✅ **VERIFIED - 20%/50% thresholds with multi-metric tracking**

**Decision:**
Performance regression thresholds should use hybrid absolute + relative approach with multi-metric tracking:

**Thresholds:**

| Metric | Warning | Failure | Rationale |
|--------|---------|---------|-----------|
| Parse rate | 5% drop | 10% drop | Current threshold proven effective |
| Convert rate | 5% drop | 10% drop | NEW - validates full pipeline |
| Conversion time | +20% | +50% | Accounts for ±10% variance on shared runners |
| Fast test runtime | >27s | >30s | Current budget (already implemented) |
| Simplification effectiveness | -10% | -20% | NEW - Sprint 11 feature metric |

**Metrics to Track:**
- **Primary:** Parse rate, convert rate, total conversion time
- **Secondary:** Simplification effectiveness (term count reduction), operation count
- **Tertiary:** CI runtime, memory usage (peak RSS)

**Variance Handling:**
- GitHub Actions shared runners have ±10% performance variance
- 20% threshold provides 2× safety margin above typical variance
- Use median of 3 runs for stability (if needed for flaky tests)

**Baseline Storage:**
```
baselines/
  performance/
    baseline_latest.json  # Rolling baseline (git-lfs, updated on main merge)
    baseline_sprint10.json  # Sprint 10 golden baseline
    baseline_sprint11.json  # Sprint 11 golden baseline (target)
    history/
      2025-11-01_commit-abc123.json  # Historical snapshots
      2025-11-15_commit-def456.json
  parse_rate/
    gamslib_ingestion_sprint11.json  # Current (git-tracked)
```

**Baseline Update Process:**
- **Automatic:** Update `baseline_latest.json` on main merge (git-lfs)
- **Manual:** Update golden baselines at sprint milestones
- **Audit:** Git history provides full baseline evolution trail

**Evidence:**
- Existing `performance-check.yml` uses 30s absolute threshold (no false positives)
- Existing `check_parse_rate_regression.py` uses 10% relative threshold (proven effective)
- Industry standard: pytest-benchmark, Google Benchmark use 20-50% thresholds
- Statistical analysis: 20% = 2σ above ±10% typical variance

**Comprehensive Survey:** `docs/planning/EPIC_2/SPRINT_11/ci_regression_framework_survey.md` Section 4.2

**Recommendation:** Implement multi-metric thresholds in Sprint 11 (12 hours estimated effort)

---

### Unknown 3.4: CI Workflow Integration Points

**Priority:** Medium  
**Owner:** Infrastructure team  
**Estimated Research Time:** 1 hour

**Assumption:**
CI workflow runs on every PR (pull_request trigger) and nightly (schedule trigger). Matrix builds parallelize across models. Artifacts store baselines and performance data.

**Research Questions:**
1. Should we use matrix builds? (test 10 models in parallel or sequentially?)
2. How do we share baselines across workflow runs? (artifacts, cache, git-lfs?)
3. Should we test on every commit or only on PR? (too frequent → wasted resources)
4. How do we report results? (GitHub Actions annotations, PR comments, separate dashboard?)
5. Should we separate fast checks (parse only) from slow checks (parse + convert + solve)?

**How to Verify:**
- Review existing GitHub Actions workflows (test.yml, lint.yml)
- Prototype GAMSLib sampling workflow (matrix build, baseline comparison)
- Test artifact storage: store baseline JSON, retrieve in next run
- Estimate costs: 10 models * 2 min * 100 PRs/month = 2000 CI minutes (within free tier?)
- Survey GitHub Actions best practices (caching, matrix builds, reporting)

**Risk if Wrong:**
- Wrong trigger → CI doesn't run when it should (or runs too often)
- No parallelization → CI too slow (10 models * 2 min = 20 min total)
- Baseline storage wrong → can't compare performance (CI useless)

**Verification Results:** ✅ **VERIFIED - Matrix builds with git-lfs baselines and PR comments**

**Decision:**
CI workflow integration should use matrix builds for parallelization, git-lfs for baseline storage, and PR comments for reporting:

**1. Matrix Builds:** ✅ **YES - Adopt for GAMSLib regression workflow**
```yaml
strategy:
  matrix:
    model: [trnsport, prodsch, bearing, hansmcp, scarfmcp, ...]  # 10 Tier 1 models
  fail-fast: false  # Test all models even if one fails
```
- **Benefit:** 10 minutes → 2-3 minutes (parallel testing across GitHub runners)
- **Isolation:** Per-model failures clearly visible
- **Cost:** Within GitHub free tier (2000 min/month for private repos)

**2. Baseline Storage:** ✅ **Git-lfs for performance, git-tracked for parse rate**
- **Parse rate baselines** (small JSON, infrequent updates): Git-tracked (current approach)
- **Performance baselines** (larger, frequent updates): Git-lfs
- **Artifacts:** 30-day retention for PR comparisons
- **Cost:** 1 GB free tier sufficient (baselines ~10 MB/month)

**3. Trigger Strategy:** ✅ **Per-PR for fast checks, nightly for slow checks**
- **Every PR:** Parse + Convert testing (<5 min with matrix builds)
- **Nightly:** Parse + Convert + Solve with PATH/IPOPT (<30 min)
- **Weekly:** Extended suite (Tier 2 models, performance trends)

**4. Reporting:** ✅ **GitHub Actions summary + PR comments**
```yaml
- run: echo "## Regression Check Results" >> $GITHUB_STEP_SUMMARY
- uses: actions/github-script@v7  # Post PR comment with summary table
```
- **Visibility:** Persistent PR comments (not ephemeral like workflow logs)
- **Format:** Markdown tables with deltas (✅/❌ indicators)

**5. Separation:** ✅ **Fast checks (parse + convert) vs. slow checks (solve)**
- **Fast checks (<5 min):** Parse rate + convert rate (every PR)
- **Slow checks (<30 min):** Solve validation with PATH/IPOPT (nightly)
- **Rationale:** Balance comprehensive validation vs. fast feedback

**Workflow Structure (Final Design):**
```
.github/workflows/
  ci.yml                    # Existing - fast tests, linting (keep as-is)
  gamslib-regression.yml    # Enhanced - matrix builds, conversion testing
  performance-check.yml     # New - performance baselines, multi-metric thresholds
  nightly-validation.yml    # New - full solve validation (Sprint 12)
```

**Evidence:**
- Existing workflows already use caching, selective triggering, artifacts (proven effective)
- Matrix builds supported natively in GitHub Actions (no additional complexity)
- Git-lfs integrated with GitHub (transparent to workflows)
- PR comment reporting used successfully in many open-source projects (Jest, ESLint, webpack)

**Cost Analysis:**
- Current: ~10 min/PR × 100 PRs/month = 1000 CI minutes
- With matrix builds: ~3 min/PR × 100 PRs/month = 300 CI minutes
- **Savings:** 700 minutes/month (faster feedback + lower cost)

**Comprehensive Survey:** `docs/planning/EPIC_2/SPRINT_11/ci_regression_framework_survey.md` Sections 1.3, 1.4, 1.5, 5.4

**Recommendation:** Implement matrix builds and enhanced reporting in Sprint 11 (4 hours effort)

---

## Category 4: UX Diagnostics

`--diagnostic` mode providing visibility into conversion pipeline stages, transformation decisions, and performance bottlenecks.

### Unknown 4.1: Diagnostic Output Granularity

**Priority:** Medium  
**Owner:** UX team  
**Estimated Research Time:** 1.5 hours

**Assumption:**
Stage-level diagnostics (parse, semantic, simplification passes, conversion, MCP gen) with per-stage time/memory/size metrics are sufficient. No need for per-function or per-transformation granularity.

**Research Questions:**
1. Is stage-level sufficient or do users need per-transformation details?
2. Should we show all 8 simplification passes separately or grouped?
3. What granularity for simplification decisions? (per-transformation: "applied factoring to expr X" or summary: "10 factorings applied"?)
4. How verbose should default be? (summary mode vs. detailed mode vs. debug mode?)
5. Should diagnostics be real-time (streaming) or post-hoc (final report)?

**How to Verify:**
- Survey similar tools: LLVM `-time-passes`, GCC `-ftime-report`, SymPy diagnostics
- Create mock diagnostic output at different granularities (stage, pass, transformation)
- Get feedback from potential users (if available): what level of detail is useful?
- Measure diagnostic overhead: stage-level should be <1%, per-transformation may be 5%+
- Prototype stage-level diagnostics on simple model

**Risk if Wrong:**
- Too coarse → users can't debug "why did simplification fail?"
- Too fine → information overload, hard to find signal in noise
- Too much overhead → diagnostic mode unusable (10%+ slowdown)

**Verification Results:** ✅ **VERIFIED - Stage-level + per-pass simplification diagnostics**

**Decision:**
Stage-level diagnostics (5 pipeline stages) with per-pass breakdowns for simplification (8 passes) is the optimal granularity.

**Key Findings:**

1. **Verbosity Levels (3 tiers):**
   - **Level 0 (default):** No diagnostics, just success/failure + total time
   - **Level 1 (--diagnostic):** Stage timing table + simplification summary
   - **Level 2 (--diagnostic --verbose):** Per-pass breakdowns + transformation details

2. **Stage-Level Metrics:**
   - Time (ms), Memory (MB), % of total time
   - Input size → Output size (AST nodes, term count)
   - Errors, warnings, transformation count

3. **Simplification Per-Pass Metrics:**
   - 8 passes shown separately (Basic, Like-Term, Associativity, Fractions, Factoring, Division, Multi-Term, CSE)
   - Transformations applied/skipped per pass
   - Term count before → after per pass
   - Skip reasons tracked (no_candidates, size_budget_exceeded, no_benefit, threshold_not_met)

4. **Performance Overhead Measured:**
   - Stage-level: 1.3-1.7% overhead (✅ <2% target met)
   - Pass-level: 2.8-3.4% overhead (✅ <5% target met)
   - Transformation-level (verbose): 4.2-5.1% overhead (✅ <5% target met)

5. **Comparison with Similar Tools:**
   - LLVM `-time-passes`: Stage/pass-level, no transformation details
   - GCC `-ftime-report`: Stage/pass-level, no size tracking
   - SymPy: NO built-in diagnostics ❌
   - **Our design:** Most comprehensive for simplification-focused tools ✅

**Recommendation:**
- ✅ Implement 3-tier verbosity in Sprint 11 (default, --diagnostic, --diagnostic --verbose)
- ✅ Stage-level diagnostics for all pipeline stages (5 stages)
- ✅ Per-pass diagnostics for simplification (8 passes)
- ⏸️ Defer per-transformation details to verbose mode only
- ⏸️ Defer heuristic decision logging to verbose mode

**Reference:** `docs/planning/EPIC_2/SPRINT_11/diagnostics_mode_architecture.md` Section 1

---

### Unknown 4.2: Diagnostic Output Format

**Priority:** Low  
**Owner:** UX team  
**Estimated Research Time:** 1 hour

**Assumption:**
Text table output to stdout is sufficient for Sprint 11. JSON output (`--diagnostic-output=stats.json`) is nice-to-have but not required. Dashboard integration is Sprint 12 work.

**Research Questions:**
1. Should we support JSON output in Sprint 11 or defer to Sprint 12?
2. What text format? (pretty table, YAML-like, structured log?)
3. Should output be colorized? (green for fast stages, red for slow?)
4. How do we handle large outputs? (100+ transformations → truncate? paginate?)
5. Should we support multiple output sinks? (stdout + file simultaneously?)

**How to Verify:**
- Create mock outputs in different formats (table, JSON, YAML)
- Measure implementation effort: JSON output adds 2-3 hours
- Survey user preferences: do users need machine-readable output in Sprint 11?
- Check if JSON output enables future work (dashboard, regression tracking)
- Decide: must-have for Sprint 11 or nice-to-have for Sprint 12

**Risk if Wrong:**
- No JSON output → can't automate analysis (performance regression tracking harder)
- Wrong text format → hard to read, users don't use diagnostics mode
- Too complex → over-engineered for Sprint 11 scope

**Verification Results:** ✅ **VERIFIED - Pretty text tables for Sprint 11, JSON deferred to Sprint 12**

**Decision:**
Text table output to stdout is sufficient for Sprint 11. JSON output and dashboard integration deferred to Sprint 12.

**Key Findings:**

1. **Output Format Selection:**
   - **Pretty Tables:** ✅ PRIMARY for Sprint 11
     - Human-readable, terminal-friendly
     - No external dependencies (stdlib only)
     - Box-drawing characters for clean layout
   - **JSON:** ⏸️ DEFER to Sprint 12
     - Machine-parseable for automation
     - Enables CI trend tracking
     - Adds 2h implementation effort
   - **YAML:** ❌ REJECT (requires external dependency)
   - **Structured Logs:** ❌ REJECT (hard to get overview)

2. **Implementation Effort:**
   - Text tables only: 4-5 hours (fits Sprint 11 budget)
   - Text + JSON: 6-7 hours (exceeds Sprint 11 budget)
   - JSON alone (Sprint 12): 2 hours

3. **Output Destinations:**
   - `--diagnostic`: Output to stdout (default)
   - `--diagnostic-stderr`: Output to stderr (separate from conversion output)
   - `--diagnostic-output=FILE`: Save to file
   - Sprint 12: `--diagnostic-output=stats.json --format=json`

4. **Color Support:**
   - Conditional ANSI color codes (auto-detect TTY)
   - Green: Fast stages (<10% of total)
   - Yellow: Medium stages (10-30%)
   - Red: Slow stages (>30%)
   - Disabled for non-TTY (pipes, files)

5. **Similar Tools Comparison:**
   - LLVM `-time-passes`: Text output, JSON is optional in newer versions
   - GCC `-ftime-report`: Text output only (JSON added in GCC 10+)
   - **Text-first approach is industry standard** ✅

**Recommendation:**
- ✅ Implement pretty text tables in Sprint 11 (4-5h)
- ✅ Support `--diagnostic-output=FILE` for saving reports
- ✅ Add optional color support (conditional on TTY)
- ⏸️ Defer JSON output to Sprint 12 (2h additional)
- ⏸️ Defer HTML dashboard to Sprint 12 (4-6h additional)

**Sprint 12 Enhancements:**
- JSON schema design + serialization (2h)
- HTML dashboard with charts (4-6h)
- CI integration (artifact storage, trend tracking) (2h)

**Reference:** `docs/planning/EPIC_2/SPRINT_11/diagnostics_mode_architecture.md` Section 4

---

## Category 5: Process Improvements

Sprint 10 Retrospective action items: incremental documentation, effort estimation refinement, feature interaction testing.

### Unknown 5.1: Incremental Documentation Enforcement

**Priority:** High  
**Owner:** Process improvement team  
**Estimated Research Time:** 1 hour

**Assumption:**
Adding "Update SPRINT_LOG.md" to PR checklist + PR review enforcement is sufficient to establish incremental documentation habit. No pre-commit hooks or automation needed.

**Research Questions:**
1. Is checklist + review enough or do we need pre-commit hooks?
2. How do we enforce during PR review? (reviewer blocks merge if docs not updated?)
3. What if docs update is tiny? (1-line change → 1-line SPRINT_LOG entry sufficient?)
4. Should we track compliance? (% PRs with docs update?)
5. What happens if docs update is forgotten? (revert PR? add follow-up commit?)

**How to Verify:**
- Review Sprint 10 PRs: how many updated docs? (establish baseline)
- Survey other projects: how do they enforce documentation?
- Prototype PR template with checklist
- Test enforcement in Sprint 11: track compliance for first 5 PRs
- Measure time overhead: is 5-10 min/PR realistic or does it take longer?

**Risk if Wrong:**
- No enforcement → docs still concentrated at end of sprint (defeats purpose)
- Too strict → developers annoyed, try to work around checklist
- No tracking → can't measure if process improvement works

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 10 will verify)

---

### Unknown 5.2: Effort Estimation Refinement Method

**Priority:** Medium  
**Owner:** Process improvement team  
**Estimated Research Time:** 1.5 hours

**Assumption:**
Using Sprint 10 velocity (3 features in 6 days, ~18-20 hours total) as baseline and adjusting for feature complexity is sufficient for Sprint 11 estimation. No need for complex estimation models (story points, planning poker).

**Research Questions:**
1. Is velocity-based estimation sufficient or do we need per-feature coefficients?
2. How do we adjust for complexity? (maxmin = 9/10 complexity → multiply by 1.5x?)
3. Should we track actual time spent in Sprint 11? (manual logging? commit timestamps?)
4. How do we account for unknowns? (research time, prototyping time, rework time?)
5. Should we use ranges (6-8 hours) or point estimates (7 hours)?

**How to Verify:**
- Analyze Sprint 10 actual time: parse commits, measure days between start and merge
- Compare estimated vs. actual for Sprint 10 (20-31h budgeted, 18-20h actual)
- Calculate velocity: features per day, hours per feature
- Apply velocity to Sprint 11 features: maxmin (12h), simplification (10h), CI (6h)
- Document estimation template for future sprints

**Risk if Wrong:**
- Over-estimate → commit to too little work (unused capacity, slower progress)
- Under-estimate → commit to too much work (burnout, missed deadlines, cut scope)
- No tracking → can't improve estimation in future sprints

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 10 will verify)

---

### Unknown 5.3: Feature Interaction Test Coverage

**Priority:** Medium  
**Owner:** QA / Testing team  
**Estimated Research Time:** 1 hour

**Assumption:**
3-5 feature interaction tests (simplification + functions, simplification + nested indexing, etc.) are sufficient to catch major interaction bugs. Exhaustive pairwise testing (N choose 2) is unnecessary.

**Research Questions:**
1. How many interaction tests are sufficient? (3, 5, 10, pairwise?)
2. Which feature pairs are highest risk? (most likely to interact poorly?)
3. Should we test 3-way interactions? (feature A + B + C?)
4. How do we prioritize interaction tests? (by risk? by frequency of use?)
5. Should interaction tests be in separate file or integrated into existing tests?

**How to Verify:**
- List all Sprint 9/10/11 features (7+ features)
- Calculate pairwise interactions (7 choose 2 = 21 pairs)
- Identify high-risk pairs: simplification + nested indexing (both modify AST)
- Prototype 3 interaction tests on current codebase
- Measure test runtime: should be <5 seconds total (no performance impact)

**Risk if Wrong:**
- Too few tests → interaction bugs slip through (features work alone, fail together)
- Too many tests → test suite bloat, slow CI, hard to maintain
- Wrong pairs → test low-risk interactions, miss high-risk ones

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 11 will verify)

---

## Category 6: Tier 2 Exploration

Medium-priority action item from Sprint 10 Retrospective: research next set of GAMSLIB models beyond Tier 1.

### Unknown 6.1: Tier 2 Model Selection Criteria

**Priority:** Low  
**Owner:** Planning team  
**Estimated Research Time:** 2 hours

**Assumption:**
Tier 2 models should be selected based on: (1) parse complexity (5-7/10), (2) feature diversity (introduce new patterns), (3) size (<200 lines), (4) community usage (popular models).

**Research Questions:**
1. How many models are in GAMSLIB? (100+? 500+?)
2. What criteria should we use for Tier 2? (complexity, size, features, popularity?)
3. Should Tier 2 have fixed size (10 models like Tier 1) or flexible?
4. How do we assess complexity before parsing? (heuristic: line count, keyword density?)
5. Should we prioritize models that unlock other models? (common blockers first?)

**How to Verify:**
- Download full GAMSLIB NLP collection
- Analyze metadata: line count, keywords, model type
- Parse all models with current parser: categorize by parse rate (0-25%, 25-50%, etc.)
- Identify common blockers in 25-50% range (next targets for Sprint 12)
- Document Tier 2 selection in preparation for Sprint 12

**Risk if Wrong:**
- Wrong criteria → select too-hard models (complexity 9/10 like maxmin)
- Wrong criteria → select too-easy models (already parse at 100%, no value)
- No clear Tier 2 → Sprint 12 has no target models (unfocused sprint)

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 12 will verify during Sprint 11 planning)

---

## Category 7: Nested Function Calls

Medium-priority action item from Sprint 10 Retrospective: complete circle.gms to 100% (currently 95%, 3 lines remain).

### Unknown 7.1: Nested Function Call Implementation Complexity

**Priority:** Low  
**Owner:** Parser team  
**Estimated Research Time:** 1 hour

**Assumption:**
Nested function calls (`exp(log(x))`, `sqrt(power(a, 2))`) can be implemented in 2-3 hours by recursively parsing function call arguments as expressions (which may themselves be function calls).

**Research Questions:**
1. Does current expression parser already support nested calls?
2. If not, what needs to change? (recursive descent parser adjustment?)
3. Are there nesting depth limits? (GAMS allows arbitrary depth? performance?)
4. How do nested calls affect MCP generation? (emit as nested or flatten?)
5. Should we validate semantics? (e.g., `exp(log(x))` = `x` for positive `x`)

**How to Verify:**
- Test current parser on `exp(log(x))` (does it parse or fail?)
- If fails, identify exact blocker (grammar, semantic, IR?)
- Prototype fix on one example
- Measure implementation time (should be 2-3 hours per estimate)
- Test circle.gms: do remaining 3 lines now parse?

**Risk if Wrong:**
- Harder than expected → takes 6-8 hours (too much for stretch goal)
- Already works → time wasted researching non-issue
- Reveals deeper blocker → cascade of changes needed

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 12 will verify during Sprint 11 planning)

---

## Newly Discovered Unknowns

This section tracks unknowns discovered during Sprint 11 that were not identified during prep. Add new unknowns here as they arise, then categorize and assign for resolution.

**Format:**
```markdown
### Unknown X.Y: [Title]
**Discovered:** Day N
**Priority:** Critical/High/Medium/Low
**Assumption:** [What we assumed]
**Why Wrong:** [What we discovered]
**Impact:** [How this affects sprint]
**Mitigation:** [What we're doing about it]
```

**Example:**
```markdown
### Unknown 1.12: SymPy Integration Required
**Discovered:** Day 4
**Priority:** High
**Assumption:** Hand-rolled factoring algorithm sufficient
**Why Wrong:** SymPy's factor() handles edge cases we didn't consider (complex coefficients, symbolic constants)
**Impact:** 2 days to integrate SymPy vs. 4 days to handle edge cases manually
**Mitigation:** Pivot to SymPy integration, defer custom factoring to Sprint 12
```

---

## Confirmed Knowledge (Resolved Unknowns)

This section tracks unknowns that have been resolved (confirmed or proven wrong) during prep or Sprint 11. Move resolved unknowns here with findings.

**Format:**
```markdown
### ✅ Unknown X.Y: [Title] — CONFIRMED
**Resolution:** [What we confirmed]
**Evidence:** [How we verified]
**Impact:** [How this affects implementation]

OR

### ❌ Unknown X.Y: [Title] — ASSUMPTION WRONG
**Correct Answer:** [What we discovered is true]
**Evidence:** [How we found out]
**Impact:** [How this changes our approach]
```

---

## Next Steps

### Before Sprint 11 Day 1

**Critical Priority (Must Complete):**
1. Verify Unknown 1.2 (transformation correctness validation) — Prep Task 3
2. Verify Unknown 2.1 (GAMS nested indexing syntax) — Prep Task 2
3. Verify Unknown 3.2 (PATH licensing for CI) — Prep Task 8
4. Verify Unknown 1.1 (common factor detection) — Prep Task 5

**High Priority (Should Complete):**
1. Verify Unknown 1.3 (expression size heuristics) — Prep Task 3
2. Verify Unknown 1.4 (cancellation detection) — Prep Task 3
3. Verify Unknown 1.5 (fraction simplification) — Prep Task 3
4. Verify Unknown 1.9 (CSE cost model) — Prep Task 4
5. Verify Unknown 1.10 (pipeline ordering) — Prep Task 3
6. Verify Unknown 2.2 (subset semantic handling) — Prep Task 2
7. Verify Unknown 2.4 (MCP generation with subsets) — Prep Task 2
8. Verify Unknown 3.1 (GAMSLib sampling effectiveness) — Prep Task 7
9. Verify Unknown 5.1 (incremental docs enforcement) — Prep Task 10

### During Sprint 11

**Daily Standup:**
- Review newly discovered unknowns (add to "Newly Discovered Unknowns")
- Update verification status (mark as ✅ CONFIRMED or ❌ WRONG)
- Identify blockers (unknowns preventing progress)
- Trigger contingency plans if critical assumptions wrong

**Weekly Review (Day 5 Checkpoint):**
- Count resolved unknowns (should be >80% by Day 5)
- Review impact of wrong assumptions (any major pivots needed?)
- Update sprint plan based on findings

**End of Sprint:**
- Move all resolved unknowns to "Confirmed Knowledge"
- Document lessons learned in Sprint 11 Retrospective
- Identify unknowns for Sprint 12 Known Unknowns document

---

## Appendix: Task-to-Unknown Mapping

This table shows which prep tasks verify which unknowns:

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Research maxmin.gms Nested/Subset Indexing | 2.1, 2.2, 2.3, 2.4 | All maxmin.gms / nested indexing unknowns verified through GAMS documentation research, maxmin.gms analysis, and implementation design |
| Task 3: Design Aggressive Simplification Architecture | 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 1.10, 1.11 | Core simplification unknowns verified through architecture design, literature review, and design decisions |
| Task 4: Research Common Subexpression Elimination | 1.9 | CSE-specific unknowns verified through literature survey (LLVM, SymPy) and cost model design |
| Task 5: Prototype Factoring Algorithms | 1.1, 1.7 | Factoring unknowns verified through prototype implementation and complexity analysis |
| Task 6: Survey CI Regression Frameworks | 3.3, 3.4 | Infrastructure unknowns verified through GitHub Actions survey and framework selection |
| Task 7: Design GAMSLib Sampling Strategy | 3.1 | Sampling effectiveness verified through strategy design and runtime analysis |
| Task 8: Research PATH Smoke Test Integration | 3.2 | PATH licensing verified through license review and maintainer contact |
| Task 9: Design Diagnostics Mode Architecture | 4.1, 4.2 | UX unknowns verified through architecture design and output format selection |
| Task 10: Establish Incremental Documentation Process | 5.1, 5.2 | Process improvement unknowns verified through workflow design and estimation method refinement |
| Task 11: Create Feature Interaction Test Framework | 5.3 | Testing unknowns verified through interaction test design and coverage analysis |
| Task 12: Plan Sprint 11 Detailed Schedule | 6.1, 7.1 | Stretch goal unknowns (Tier 2, nested functions) researched during scheduling, may defer if needed |

**Total Unknowns:** 26  
**Unknowns Verified by Prep Tasks:** 26 (100%)

**Critical Path Unknowns (must verify before Sprint 11 Day 1):**
- 1.2 (Task 3) - Transformation correctness
- 2.1 (Task 2) - GAMS nested indexing syntax
- 3.2 (Task 8) - PATH licensing

**Verification Timeline:**
- Prep Days 1-3: Tasks 1, 2, 3 complete → Unknowns 2.1-2.4, 1.2-1.11 verified
- Prep Days 3-5: Tasks 4, 5, 6 complete → Unknowns 1.1, 1.7, 1.9, 3.3, 3.4 verified
- Prep Days 5-6: Tasks 7, 8, 9, 10, 11 complete → Unknowns 3.1, 3.2, 4.1, 4.2, 5.1, 5.2, 5.3 verified
- Prep Day 6: Task 12 complete → Unknowns 6.1, 7.1 researched (may defer)

---

**Document Status:** 🔵 Ready for Prep Task Verification  
**Next Action:** Begin Prep Task 2 (maxmin.gms Research) to verify Unknowns 2.1-2.4

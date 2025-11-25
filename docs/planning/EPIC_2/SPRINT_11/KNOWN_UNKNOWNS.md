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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 5 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 3 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 3 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 3 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 3 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 3 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 5 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 3 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 4 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 3 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 3 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 2 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 2 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 2 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 2 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 7 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 8 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 6 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 6, 7 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 9 will verify)

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

**Verification Results:** 🔍 Status: INCOMPLETE (Prep Task 9 will verify)

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

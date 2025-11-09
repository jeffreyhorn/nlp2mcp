# EPIC 2 Goals: Advanced Features & Real-World Validation

**Timeline:** 10 weeks (5 sprints of 2 weeks each)  
**Target Release:** v1.0.0  
**Status:** Planning Phase

## Overview

Epic 2 builds upon the production-ready foundation established in Epic 1 (v0.5.0-beta) to add advanced features, improve robustness with real-world models, and enhance user experience. The focus shifts from core functionality to handling edge cases, validating against industry-standard benchmarks, and providing more sophisticated analysis capabilities.

## Strategic Themes

1. **Real-World Validation** - Test against GAMS Model Library NLP examples
2. **Parser Completeness** - Support additional GAMS syntax needed for library models
3. **Advanced Analysis** - Convexity detection, aggressive simplification, performance benchmarking
4. **Bug Fixes** - Address known issues from Epic 1 follow-ons
5. **User Experience** - Better error messages, diagnostics, and documentation

---

## Goal Categories

### 1. Convexity Detection & Warnings

**Priority:** HIGH  
**Estimated Effort:** 1 sprint (2 weeks)  
**Reference:** `docs/research/convexity_detection.md`

#### Motivation
Users may unknowingly attempt to convert non-convex NLP models to MCP, resulting in unsolvable problems or PATH solver failures. Providing convexity warnings will prevent frustration and misuse of the tool.

#### Objectives

- **1.1 Heuristic Convexity Checker** (Quick Pattern Matching)
  - Detect non-convex indicators:
    - Nonlinear equality constraints (`sin(x) + cos(y) = 0`)
    - Trigonometric functions (`sin`, `cos`, `tan`)
    - Bilinear terms (`x*y` where both are variables)
    - Variable quotients (`x/y`)
    - Odd powers (`x^3`, `x^5`)
  - Emit warnings but allow conversion to continue
  - Provide educational messages about KKT sufficiency conditions

- **1.2 AST-Based Convexity Classification** (Optional `--analyze-convexity`)
  - Implement convexity class tracking (`CONSTANT`, `AFFINE`, `CONVEX`, `CONCAVE`, `UNKNOWN`)
  - Use composition rules to classify expressions
  - Generate detailed convexity report
  - Suggest reformulations when possible

- **1.3 CLI Integration**
  - Add automatic warnings after parsing (always enabled)
  - Add `--strict-convexity` flag to fail on non-convexity
  - Add `--analyze-convexity` flag for detailed analysis
  - Update documentation with convexity guidance

#### Success Criteria
- Warns on all non-convex test cases (e.g., circular constraints, trig equalities)
- Does NOT warn on convex examples (linear programs, convex QPs)
- Clear, actionable error messages
- Documentation explains when to use NLP vs MCP approaches

---

### 2. Fix Known Bugs from Epic 1

**Priority:** HIGH  
**Estimated Effort:** 1 sprint (2 weeks)  
**Reference:** `docs/planning/EPIC_1/SPRINT_5/follow-ons/*.md`

#### 2.1 Maximize Bound Multiplier Sign Bug

**Reference:** `MAXIMIZE_BOUND_MULTIPLIER_BUG.md`

**Problem:** When using `maximize` objective, bound multipliers in stationarity equations have incorrect signs, causing PATH solver failures.

**Root Cause:** Stationarity equation generation doesn't account for maximize vs minimize objective sense.

**Fix Plan:**
1. Store objective sense in `KKTSystem` or `ModelIR`
2. Adjust bound multiplier signs based on objective sense:
   - For maximize: flip bound multiplier signs
   - For minimize: keep current implementation
3. Add test cases for maximize with various bound configurations
4. Verify minimize cases still pass after fix

**Success Criteria:**
- `test2_maximize_max.gms` finds correct solution (x=10, y=20, z=20)
- All existing minimize tests continue to pass
- Simple maximize without min/max works correctly

#### 2.2 Nested Min/Max Support

**Reference:** `NESTED_MINMAX_REQUIREMENTS.md`

**Problem:** Nested min/max like `min(x, min(y, z))` or `max(min(x, y), z)` cause "function not supported" errors during differentiation.

**Solution Approaches:**

**Option A: Flattening (Simpler)**
- Flatten same-operation nesting: `min(x, min(y, z))` → `min(x, y, z)`
- Handles 80% of real-world cases
- Cleaner MCP output with fewer auxiliary variables
- 4-6 hours implementation effort

**Option B: Multi-Pass Reformulation (Comprehensive)**
- Bottom-up reformulation: innermost calls first
- Substitute auxiliary variables in parent expressions
- Handles mixed operations: `min(x, max(y, z))`
- 10-15 hours implementation effort

**Recommendation:** Start with Option A (flattening), add Option B if needed based on user demand.

**Success Criteria:**
- `test5_nested_minmax.gms` generates valid MCP
- PATH solver finds correct solution (x=1, y=2, z=3, w=1)
- No "function not supported" errors
- Existing non-nested tests still pass

---

### 3. GAMSLib NLP Model Validation

**Priority:** HIGH  
**Estimated Effort:** 2 sprints (4 weeks)

#### Motivation
Validate nlp2mcp against real-world GAMS models from the official GAMS Model Library. This will:
- Identify missing GAMS syntax features
- Reveal edge cases not covered by current tests
- Provide realistic performance benchmarks
- Build confidence in production readiness

#### 3.1 Model Download & Organization

**Objectives:**
- Create automated script to download NLP models from GAMS library
- URL: `https://www.gams.com/latest/gamslib_ml/libhtml/`
- Target models (initial set):
  - `trig.gms` - Simple trigonometric example
  - `trigx.gms` - Trigonometric mathematical problem
  - `mhw4dx.gms` - Nonlinear test problem
  - `cclinpts.gms` - Power utility function linearization
  - `minsurf.gms` - Minimal surface computation (COPS 2.0)
  - Additional models based on parser capability
  
**Implementation:**
```bash
# Download script
scripts/download_gamslib_nlp.sh

# Organization
tests/fixtures/gamslib/
  ├── README.md (model descriptions, expected results)
  ├── trig.gms
  ├── trigx.gms
  ├── mhw4dx.gms
  └── ...
```

#### 3.2 Parser Enhancement Plan

**Strategy:** Iteratively enhance parser to support GAMSLib models

**Phase 1: Analyze Missing Features**
1. Run nlp2mcp on downloaded models
2. Collect all parse errors
3. Categorize by GAMS language feature
4. Prioritize by frequency and importance

**Phase 2: Implement Missing Features**

Common features likely needed:
- **Variable initialization** (`.l` attribute: `x.l = 5`)
- **Solver options** (`Option NLP = conopt`)
- **Display statements** (`Display x.l, obj.l`)
- **Equation attributes** (`.m` for marginals, `.l` for levels)
- **Assignment statements** (`parameter_name = expression;`)
- **Multi-dimensional sets** (`Set ij(i,j)` - subsets)
- **Conditional expressions** (`$(condition)` - dollar condition operator)
- **Acronyms** (`Acronym Inf;` for infinity representation)
- **Put statements** (file output - may skip)
- **Option statements** (`Option limrow=0, limcol=0` - output control)

**Phase 3: Implement Iteratively**

For each feature:
1. Analyze GAMS syntax from failing model
2. Extend grammar in `src/gams/grammar.lark`
3. Update parser in `src/ir/parser.py`
4. Add to IR if needed (or skip if non-semantic)
5. Add unit tests
6. Verify model now parses
7. Check if conversion succeeds

#### 3.3 Conversion Success Tracking

**Goal:** Track how many GAMSLib models successfully convert

**Metrics:**
- Parse success rate (models that parse without error)
- Conversion success rate (models that generate valid MCP)
- Solver success rate (MCPs that PATH can solve)

**Dashboard:** `tests/fixtures/gamslib/CONVERSION_STATUS.md`

```markdown
# GAMSLib NLP Conversion Status

| Model | Parse | Convert | Solve | Notes |
|-------|-------|---------|-------|-------|
| trig | OK | OK | OK | Simple trig functions |
| trigx | OK | FAIL | - | Unsupported: nested trig |
| mhw4dx | OK | OK | FAIL | Non-convex, as expected |
| ...
```

#### 3.4 Performance Benchmarking

**Goal:** Compare NLP solving time vs MCP solving time

**Approach:**
1. Solve original NLP with CONOPT or IPOPT
2. Convert to MCP and solve with PATH
3. Record solve times, iterations, objective values
4. Document cases where MCP is faster/slower

**Benchmark Report:** `docs/benchmarks/GAMSLIB_PERFORMANCE.md`

```markdown
# GAMSLib Performance Comparison

| Model | NLP Solver | NLP Time | MCP Solver | MCP Time | Speedup | Notes |
|-------|------------|----------|------------|----------|---------|-------|
| trig | CONOPT | 0.12s | PATH | 0.08s | 1.5x | Simple convex |
| ...
```

**Use Cases:**
- Identify when MCP reformulation is beneficial
- Validate correctness (objective values should match)
- Document performance characteristics

---

### 4. Aggressive Algebraic Simplification

**Priority:** MEDIUM  
**Estimated Effort:** 1 sprint (2 weeks)

#### Motivation
Current `--simplification advanced` mode performs good simplifications, but there's room for more aggressive algebraic optimizations that could significantly reduce MCP complexity.

#### Objectives

**4.1 Implement `--simplification aggressive` Mode**

New simplification rules beyond `advanced`:

**Algebraic Identities:**
- Trigonometric: `sin^2(x) + cos^2(x) → 1`
- Logarithmic: `log(a) + log(b) → log(a*b)`
- Exponential: `exp(a) * exp(b) → exp(a+b)`
- Power laws: `x^a * x^b → x^(a+b)`, `(x^a)^b → x^(a*b)`

**Advanced Factoring:**
- Common subexpression elimination across terms
- Factor out common multipliers: `2*x*y + 4*x*z → 2*x*(y + 2*z)`
- Distribute and combine: `x*(a+b) + x*(c+d) → x*(a+b+c+d)`

**Rational Simplification:**
- Simplify fractions: `(2*x) / (4*y) → x / (2*y)`
- Combine fractions: `x/y + z/y → (x+z)/y`
- Cancel common factors: `(x*y) / (x*z) → y/z` (if x ≠ 0)

**Strength Reduction:**
- Replace expensive operations: `x^2 → x*x` (debatable)
- Replace `sqrt(x) → x^0.5` or vice versa depending on solver preference
- Simplify integer powers: `x^4 → sqr(sqr(x))` if beneficial

**Symbolic Evaluation:**
- Evaluate constant expressions more aggressively
- Fold parameter references if values are known
- Simplify `sum(i, constant)` → `constant * card(i)` (if cardinality known)

**4.2 Common Subexpression Elimination (CSE)**

Detect repeated subexpressions across multiple equations:

```gams
eq1.. y1 =e= exp(x1 + x2) + 2*x1;
eq2.. y2 =e= exp(x1 + x2) + 3*x2;
```

Introduce auxiliary variable:
```gams
aux_exp =e= exp(x1 + x2);
eq1.. y1 =e= aux_exp + 2*x1;
eq2.. y2 =e= aux_exp + 3*x2;
```

**Benefits:**
- Reduces redundant computation in gradients/Jacobians
- Can significantly reduce derivative complexity
- May improve solver performance

**Challenges:**
- Changes problem structure (adds variables/equations)
- Need heuristics to decide when CSE is beneficial
- Must not break existing functionality

**4.3 CLI Integration**

```bash
# Use aggressive simplification
nlp2mcp model.gms --simplification aggressive

# With CSE
nlp2mcp model.gms --simplification aggressive --cse

# Show simplification statistics
nlp2mcp model.gms --simplification aggressive --show-simplification-stats
```

**4.4 Testing & Validation**

- Finite-difference validation must pass (correctness check)
- Compare simplified vs non-simplified derivative complexity
- Measure impact on PATH solver performance
- Document when aggressive mode is recommended

#### Success Criteria
- All existing tests pass with `--simplification aggressive`
- Demonstrable reduction in derivative term counts (e.g., 20-30% fewer terms)
- Performance improvement on at least 50% of test cases
- No correctness regressions (finite-difference validation)

---

### 5. Enhanced User Experience

**Priority:** MEDIUM  
**Estimated Effort:** Ongoing throughout Epic 2

#### 5.1 Better Error Messages

**Current Issues:**
- Generic "Parse error" messages
- No line numbers for some errors
- Cryptic messages for unsupported features

**Improvements:**
- Always include line/column numbers
- Provide helpful suggestions: "Did you mean X?"
- Link to documentation for unsupported features
- Show context around error location

**Example:**
```
Before:
  Error: Unsupported equation type

After:
  Error: Unsupported equation type '=n=' (line 15, column 20)
  
  15 | constraint.. x + y =n= 0;
                            ^^^
  
  nlp2mcp currently only supports:
    =e= (equality)
    =l= (less than or equal)
    =g= (greater than or equal)
  
  See: docs/GAMS_SUBSET.md for full list of supported features
```

#### 5.2 Progress Indicators

For large models, show progress during long operations:

```bash
$ nlp2mcp large_model.gms -o output.gms

Parsing model...                     [====] 100% (1.2s)
Normalizing constraints...           [====] 100% (0.3s)
Computing gradients...               [====] 100% (2.5s)
Computing Jacobians...               [====] 100% (5.7s)
  Equality constraints:   50/50
  Inequality constraints: 120/120
Assembling KKT system...             [====] 100% (0.8s)
Generating GAMS MCP code...          [====] 100% (1.1s)

MCP model generated successfully!
  Variables: 250
  Equations: 420
  Nonzeros:  1,850
  Output: output.gms
```

#### 5.3 Model Statistics Dashboard

Add `--stats-detailed` flag for comprehensive model analysis:

```bash
$ nlp2mcp model.gms --stats-detailed

=== MODEL STATISTICS ===

Input Model:
  Variables:       50 (30 continuous, 15 positive, 5 bounded)
  Equations:       35 (10 equality, 25 inequality)
  Parameters:      12
  Sets:            3
  Model type:      NLP (minimize)
  Nonlinear:       Yes (trig functions, powers)

Derivatives:
  Objective gradient:   50 nonzeros (sparse: 60%)
  Jacobian (equality):  150 nonzeros (sparse: 70%)
  Jacobian (inequality): 380 nonzeros (sparse: 65%)

KKT System:
  Total variables:  115 (50 original + 35 multipliers + 30 bound multipliers)
  Total equations:  85 (50 stationarity + 35 original constraints)
  Complementarity:  65 pairs
  MCP nonzeros:     890

Convexity Analysis:
  Objective:        UNKNOWN (contains trig functions)
  Constraints:      2 nonlinear equalities detected (likely non-convex)
  Recommendation:   Review convexity before solving
```

#### 5.4 Diagnostic Mode

Add `--diagnostic` flag that shows internal state at each pipeline stage:

```bash
$ nlp2mcp model.gms --diagnostic

=== STAGE 1: PARSING ===
Detected constructs:
  - 3 Sets: i, j, k
  - 12 Parameters: cost, demand, capacity, ...
  - 50 Variables: x(i,j), y(i), z(k), obj
  - 35 Equations: balance(i), capacity(j), ...
  - Min/max calls: 2 detected
  - Special functions: sin, cos, exp

=== STAGE 2: NORMALIZATION ===
Converted equations to standard form:
  - 10 equality constraints (g(x) = 0)
  - 25 inequality constraints (g(x) <= 0)

=== STAGE 3: MIN/MAX REFORMULATION ===
Reformulating 2 min/max calls:
  1. min(x(1), x(2)) in equation eq1 → 2 complementarity constraints
  2. max(y(1), y(2)) in equation eq5 → 2 complementarity constraints
Added 2 auxiliary variables, 4 multipliers

=== STAGE 4: DIFFERENTIATION ===
Computing gradients... (50 variables, 1 objective)
Computing Jacobians... (35 constraints, 50 variables)
Simplification mode: advanced

=== STAGE 5: KKT ASSEMBLY ===
Creating stationarity equations for 50 variables...
Adding 35 constraint multipliers...
Adding 30 bound multipliers...

=== STAGE 6: CODE GENERATION ===
Generating GAMS MCP code...
```

---

### 6. Documentation Enhancements

**Priority:** MEDIUM  
**Estimated Effort:** Ongoing throughout Epic 2

#### 6.1 Advanced User Guide

Create `docs/ADVANCED_USAGE.md`:
- When to use nlp2mcp vs direct NLP solvers
- Convexity requirements and detection
- Performance tuning recommendations
- Scaling and preconditioning strategies
- Troubleshooting common issues
- Interpreting PATH solver output

#### 6.2 GAMSLib Examples Documentation

Create `docs/GAMSLIB_EXAMPLES.md`:
- How to run GAMSLib benchmarks
- Expected conversion success rates
- Performance comparison methodology
- Known limitations with specific models

#### 6.3 API Reference Enhancement

Expand `docs/api/` with:
- Detailed function signatures and types
- Usage examples for each module
- Integration examples (using nlp2mcp as library)
- Custom simplification rules
- Extending the parser

#### 6.4 Video Tutorials

Create short video walkthroughs:
1. "Getting Started with nlp2mcp" (5 min)
2. "Understanding Convexity Warnings" (10 min)
3. "Performance Tuning" (8 min)
4. "Extending the Parser" (12 min)

---

### 7. Quality & Robustness

**Priority:** HIGH (Continuous)  
**Estimated Effort:** Ongoing throughout Epic 2

#### 7.1 Test Coverage Goals

**Target:** Maintain >90% coverage

- Add tests for all new features
- Expand edge case coverage
- Add regression tests for fixed bugs
- Improve integration test coverage

#### 7.2 Performance Testing

**Objectives:**
- Establish performance benchmarks for common model sizes
- Track performance regressions in CI/CD
- Optimize hot paths identified by profiling
- Document performance characteristics

**Benchmark Models:**
- Small: <10 variables, <20 equations
- Medium: 10-100 variables, 20-200 equations
- Large: 100-1000 variables, 200-2000 equations
- Extra Large: >1000 variables, >2000 equations

**Metrics:**
- Parse time
- Differentiation time
- KKT assembly time
- Total conversion time
- Memory usage

#### 7.3 Continuous Integration Enhancements

- Add GAMSLib conversion tests to CI
- Add performance regression detection
- Add memory leak detection
- Add coverage reporting to PR checks

---

## Sprint Breakdown (Tentative)

### Sprint 6 (Weeks 1-2): Convexity Detection & Maximize Bug
- Implement heuristic convexity checker
- Fix maximize bound multiplier sign bug
- CLI integration for convexity warnings
- Add tests and documentation

**Deliverable:** v0.6.0 with convexity warnings and maximize fix

### Sprint 7 (Weeks 3-4): GAMSLib Integration Part 1
- Download and organize GAMSLib NLP models
- Analyze missing parser features
- Implement top priority parser enhancements
- Initial conversion success tracking

**Deliverable:** v0.7.0 with expanded parser support

### Sprint 8 (Weeks 5-6): GAMSLib Integration Part 2
- Continue parser enhancements based on model needs
- Implement nested min/max support (flattening approach)
- Performance benchmarking infrastructure
- Track conversion success metrics

**Deliverable:** v0.8.0 with nested min/max and more GAMSLib support

### Sprint 9 (Weeks 7-8): Aggressive Simplification
- Implement `--simplification aggressive` mode
- Add advanced algebraic identities
- Common subexpression elimination (CSE)
- Performance validation and tuning

**Deliverable:** v0.9.0 with aggressive simplification

### Sprint 10 (Weeks 9-10): UX Polish & v1.0 Release
- Enhanced error messages and diagnostics
- Progress indicators for large models
- Documentation enhancements
- Final testing and bug fixes
- Release v1.0.0

**Deliverable:** v1.0.0 - Production-ready with comprehensive GAMSLib support

---

## Success Metrics

### Quantitative
- **Parser Coverage:** Support 80%+ of GAMSLib NLP models
- **Conversion Success:** 60%+ of parseable models convert to valid MCP
- **Test Coverage:** >90% code coverage maintained
- **Performance:** <2x overhead vs Epic 1 for equivalent models
- **User Satisfaction:** Positive feedback on convexity warnings and error messages

### Qualitative
- **Production Ready:** Trusted for real-world optimization workflows
- **Well Documented:** Users can self-serve for common tasks
- **Extensible:** Clear path for adding new GAMS features
- **Robust:** Handles edge cases gracefully with helpful messages

---

## Risks & Mitigation

### Risk 1: GAMSLib Models Too Complex
**Impact:** HIGH  
**Probability:** MEDIUM

**Mitigation:**
- Start with simpler models from library
- Incrementally add parser features
- Document unsupported features clearly
- Provide workarounds when possible

### Risk 2: Performance Regressions
**Impact:** MEDIUM  
**Probability:** MEDIUM

**Mitigation:**
- Establish baseline benchmarks early
- Add performance tests to CI
- Profile before optimizing
- Make aggressive simplification optional

### Risk 3: Aggressive Simplification Correctness
**Impact:** HIGH  
**Probability:** LOW

**Mitigation:**
- Extensive finite-difference validation
- Conservative rules initially
- Make it opt-in (`--simplification aggressive`)
- Comprehensive test suite

### Risk 4: Scope Creep
**Impact:** MEDIUM  
**Probability:** HIGH

**Mitigation:**
- Strict sprint planning
- Defer low-priority features
- Focus on GAMSLib validation as north star
- Regular checkpoint reviews

---

## Future Work (Post-Epic 2)

### Epic 3 Candidates

1. **Advanced Solver Integration**
   - Direct PATH solver integration (no intermediate .gms file)
   - Support for other MCP solvers (MILES, NLPEC)
   - Warm-start support from previous solutions

2. **Parallel Processing**
   - Parallelize gradient/Jacobian computation
   - Multi-threaded simplification
   - Batch processing of multiple models

3. **Web Interface**
   - Browser-based model editor
   - Visual KKT system inspector
   - Interactive convexity analysis

4. **Advanced Reformulations**
   - Automatic convexification hints
   - Piecewise linear approximations
   - Complementarity detection in general NLPs

5. **GAMS Studio Integration**
   - Plugin for GAMS IDE
   - Integrated debugging
   - Visual diff of NLP vs MCP

---

## References

### Internal Documents
- `docs/research/convexity_detection.md` - Convexity detection research
- `docs/planning/EPIC_1/SPRINT_5/follow-ons/MAXIMIZE_BOUND_MULTIPLIER_BUG.md` - Maximize bug analysis
- `docs/planning/EPIC_1/SPRINT_5/follow-ons/NESTED_MINMAX_REQUIREMENTS.md` - Nested min/max requirements
- `docs/planning/EPIC_1/SUMMARY.md` - Epic 1 feature overview

### External Resources
- GAMS Model Library: https://www.gams.com/latest/gamslib_ml/libhtml/
- GAMS Documentation: https://www.gams.com/latest/docs/
- PATH Solver Manual: https://www.gams.com/latest/docs/S_PATH.html
- Convex Optimization (Boyd & Vandenberghe): https://web.stanford.edu/~boyd/cvxbook/

---

## Changelog

- **2025-11-09:** Initial EPIC_2 goals document created

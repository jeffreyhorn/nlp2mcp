# nlp2mcp Limitations

**Version:** Sprint 5  
**Last Updated:** November 7, 2025  
**Status:** Production Hardening Complete

---

## Overview

This document describes the known limitations, constraints, and edge case behavior of nlp2mcp. Understanding these limitations helps users set appropriate expectations and design models that convert successfully.

**Quick Summary:**
- ✅ Handles models up to 1000+ variables efficiently
- ✅ Supports all standard NLP constructs (nonlinear objectives, constraints, bounds)
- ✅ Comprehensive error recovery with helpful messages
- ⚠️ Requires convex NLP problems for reliable KKT transformation
- ⚠️ Some GAMS features not supported (see below)

---

## Table of Contents

1. [Model Requirements](#model-requirements)
2. [Supported GAMS Features](#supported-gams-features)
3. [Unsupported GAMS Features](#unsupported-gams-features)
4. [Performance Limits](#performance-limits)
5. [Numerical Considerations](#numerical-considerations)
6. [Edge Cases and Degeneracies](#edge-cases-and-degeneracies)
7. [Error Handling](#error-handling)
8. [Workarounds and Best Practices](#workarounds-and-best-practices)

---

## Model Requirements

### Required for Successful Conversion

nlp2mcp expects well-formed GAMS NLP models with:

1. **Single Objective Function**
   - Model must have exactly one objective variable
   - Objective must be defined by an equation (e.g., `obj_def.. z =e= <expression>`)
   - Objective sense: `minimizing` or `maximizing`

2. **Valid Variable Declarations**
   - All variables used in equations must be declared in `Variables` block
   - Variable types supported: `Variables`, `Positive Variables`, `Binary Variables`, `Integer Variables`
   - Note: Integer and binary variables treated as continuous in MCP formulation

3. **Valid Equation Declarations**
   - Equations must use GAMS equation syntax: `eq_name.. lhs =e=/=l=/=g= rhs`
   - Supported relations: `=e=` (equality), `=l=` (≤), `=g=` (≥)

4. **Model Solve Statement**
   - Must include: `Solve <modelname> using NLP minimizing/maximizing <objvar>`
   - NLP solver type required (nlp2mcp converts NLP → MCP)

### Convexity Requirement

⚠️ **Important:** nlp2mcp uses KKT conditions for NLP → MCP transformation.

**KKT conditions assume convexity:**
- For minimization: objective and inequality constraints should be convex
- For maximization: objective should be concave, inequalities convex
- Non-convex problems may produce:
  - Infeasible MCP systems (PATH Model Status 5)
  - Incorrect solutions
  - Local optima instead of global optima

**Recommendation:** Verify problem convexity before conversion. If unsure, test with small instances first.

---

## Supported GAMS Features

### ✅ Fully Supported

**Arithmetic Operations:**
- Basic: `+`, `-`, `*`, `/`, `**` (power)
- Unary: `-x`, `+x`

**Mathematical Functions:**
- Exponential/Logarithmic: `exp(x)`, `log(x)` (natural log)
- Power: `power(x, n)`, `sqr(x)`, `sqrt(x)`
- Trigonometric: `sin(x)`, `cos(x)`, `tan(x)`

**Indexing and Sets:**
- Sets with explicit members: `Set i /i1, i2, i3/`
- Indexed variables: `x(i, j)`
- Indexed equations: `eq(i).. <expression>`
- Indexed parameters: `p(i, j)`
- Sum expressions: `sum(i, x(i))`
- Aliased sets: `Alias(i, j)`

**Constraints:**
- Equality constraints: `eq.. lhs =e= rhs`
- Inequality constraints: `ineq.. lhs =l= rhs` or `lhs =g= rhs`
- Variable bounds: `x.lo`, `x.up`, `x.fx`
- Parametric bounds: `x.lo(i) = p(i)`

**Variable Types:**
- Free variables: `Variables x`
- Positive variables: `Positive Variables x` (automatic `x.lo = 0`)
- Binary variables: `Binary Variables x` (treated as continuous in MCP)
- Integer variables: `Integer Variables x` (treated as continuous in MCP)

---

## Unsupported GAMS Features

### ❌ Not Supported (Will Cause Errors or Unexpected Behavior)

**Advanced GAMS Functions:**
- `min(x, y, z)` / `max(x, y, z)` - **Partially supported** (see note below)
- `abs(x)` - **Partially supported** (reformulated using complementarity)
- Conditional expressions: `$(condition)`
- Special functions: `sign`, `mod`, `div`, `ceil`, `floor`
- String operations

**Min/Max Functions:**
- ✅ Supported when min/max defines objective variable (Strategy 1 reformulation)
- ❌ Not supported in general constraint expressions
- See `docs/research/minmax_objective_reformulation.md` for details

**Advanced Indexing:**
- Conditional sums: `sum(i$condition, x(i))`
- Lag/lead operators: `x(i-1)`, `x(i+1)`
- Ord/card functions

**Data Structures:**
- Tables (use `Parameter` blocks instead)
- Multi-dimensional parameters with sparse data
- External data files (`$include`, `$gdxin`)

**Control Flow:**
- Loops: `loop`, `while`, `repeat`
- Conditional statements: `if-then-else`
- Macros and compile-time functions

**Solver Options:**
- Solver-specific options embedded in model (use separate `.opt` files instead)
- Solution report customization

**Other:**
- Multiple objective functions
- Multi-stage optimization
- Stochastic programming constructs
- Complementarity conditions in NLP (nlp2mcp generates these, doesn't parse them)

---

## Performance Limits

### Tested and Validated

Based on Sprint 5 Day 5 performance benchmarking:

| Model Size | Conversion Time | Memory Usage | Status |
|------------|----------------|--------------|--------|
| 250 variables | 4.2s | <100 MB | ✅ Excellent |
| 500 variables | 10.7s | 60 MB | ✅ Excellent |
| 1000 variables | 42.6s | ~150 MB (est) | ✅ Good |

**Performance Characteristics:**
- Time complexity: O(n²) for Jacobian computation (expected)
- Memory complexity: O(n) for sparse storage
- Bottleneck: Symbolic differentiation and simplification (80% of time)

### Recommended Limits

**Small Models** (≤100 variables):
- Conversion time: <5 seconds
- Memory: <50 MB
- Use case: Rapid prototyping, testing

**Medium Models** (100-500 variables):
- Conversion time: <30 seconds
- Memory: <100 MB
- Use case: Typical optimization problems

**Large Models** (500-1000 variables):
- Conversion time: <2 minutes
- Memory: <200 MB
- Use case: Production optimization, large-scale planning

**Very Large Models** (>1000 variables):
- Conversion time: 2-10 minutes (estimated)
- Memory: 200-500 MB (estimated)
- Status: Not extensively tested
- Recommendation: Test on smaller instances first

### Dimensional Limits

**Variables and Equations:**
- Maximum tested: 1000 variables, 1000 equations
- Theoretical limit: System memory (Python dict-based storage scales linearly)
- Practical limit: ~2000 variables before conversion time exceeds 10 minutes

**Indexing:**
- Maximum set size: Limited by Python memory
- Maximum nesting depth: 50+ levels (tested)
- Maximum indices per variable: No hard limit (tested up to 3 dimensions)

**Expressions:**
- Maximum expression nesting: 50+ levels (tested)
- Maximum terms in sum: Limited by Python memory
- Identifier length: 240+ characters (tested)

---

## Numerical Considerations

### NaN and Inf Detection

nlp2mcp validates for numerical issues at multiple pipeline stages (Sprint 5 Day 4):

**Validated:**
- Parameter values (after parsing)
- Expression evaluation (during differentiation)
- Jacobian entries (before KKT assembly)

**Detected Issues:**
- NaN (Not a Number) in parameters, expressions, or derivatives
- Inf (Infinity) in parameters, expressions, or derivatives
- Division by zero
- Invalid operations: `log(0)`, `sqrt(-1)`, `log(negative)`

**Error Messages:**
All numerical errors include:
- Location (parameter name, equation, variable)
- Actual value (NaN, +Inf, -Inf)
- Actionable suggestions for fixing

### Numerical Stability

**Potential Issues:**
- Very large parameter values (>1e10) may cause scaling issues
- Very small parameter values (<1e-10) may underflow
- Ill-conditioned Jacobians may fail in PATH solver

**Recommendations:**
- Scale variables and parameters to similar magnitudes (0.1 - 100)
- Avoid extreme bounds (e.g., `x.lo = -1e20`)
- Use PATH solver options for ill-conditioned problems (see PATH_SOLVER.md)

---

## Edge Cases and Degeneracies

nlp2mcp handles many edge cases gracefully (Sprint 5 Day 6 - 29 tests):

### ✅ Supported Edge Cases

**Constraint Configurations:**
- Only equality constraints (no inequalities)
- Only inequality constraints (no equalities)
- Only variable bounds (no explicit constraints)
- No constraints (unconstrained optimization)

**Bounds:**
- All finite bounds
- All infinite bounds (unbounded variables)
- Mixed finite/infinite bounds
- Fixed variables (`x.fx = value`)
- Duplicate bound declarations

**Indexing:**
- Scalar variables only (no indexed variables)
- Single-indexed variables
- Multi-indexed variables (2+ dimensions)
- Sparse indexing (not all combinations defined)
- Aliased sets

**Expressions:**
- Constant expressions (zero derivatives)
- Linear-only expressions
- Quadratic expressions
- Highly nonlinear expressions
- Very long expressions (50+ terms)

**Sparsity:**
- Dense Jacobians (all derivatives nonzero)
- Sparse Jacobians (many zero derivatives)
- Block-diagonal Jacobians
- Single variable per constraint

**Special Structures:**
- Single variable models
- Single constraint models
- Large models (1000+ variables)
- Empty set indexing
- Objective-only models (no constraints)

### ⚠️ Degenerate Cases

**May Cause Issues:**
- Constant equations (e.g., `5 = 5`) - Detected and reported as ModelError
- Circular variable definitions (e.g., `x = y; y = x`) - Detected and reported
- Undefined variables referenced in equations - Detected and reported
- Missing objective - Detected and reported

All degeneracies are caught during validation (Day 4) with helpful error messages.

---

## Error Handling

nlp2mcp provides comprehensive error recovery (Sprint 5 Day 4):

### Error Categories

**1. UserError - Modeling Mistakes**
- Missing objective
- Undefined variables
- Circular definitions
- Constant equations

**2. NumericalError - Invalid Values**
- NaN in parameters
- Inf in expressions
- Invalid bounds (lower > upper)

**3. ModelError - Structural Issues**
- Invalid equation syntax
- Unsupported constructs
- Malformed GAMS code

### Error Message Quality

All errors include:
- ✅ Clear description of the problem
- ✅ Location context (file, line, variable, equation)
- ✅ Actual values (for numerical errors)
- ✅ Actionable suggestions with examples
- ✅ Links to documentation (where applicable)

**Example:**
```
Numerical error in parameter 'demand[region1]': Invalid value (value is NaN)

Suggestion:
Check your GAMS model or data file for:
  - Uninitialized parameters
  - Division by zero in parameter calculations
  - Invalid mathematical operations
  - Correct definition of parameter 'demand'
```

---

## Workarounds and Best Practices

### Common Issues and Solutions

**Issue: Model fails with "No objective defined"**
- **Cause:** Objective variable not defined by an equation
- **Solution:** Add equation defining objective, e.g., `obj_def.. z =e= sum(i, x(i))`

**Issue: Conversion very slow (>5 minutes)**
- **Cause:** Very large model or complex expressions
- **Solution:**
  - Simplify expressions algebraically before conversion
  - Reduce model size if possible
  - Check for unnecessary complexity (e.g., deeply nested sums)

**Issue: PATH solver reports Model Status 5 (Locally Infeasible)**
- **Cause:** Non-convex problem or infeasible KKT system
- **Solution:**
  - Verify problem convexity
  - Check initial point feasibility
  - Try different PATH solver options (see PATH_SOLVER.md)
  - If problem is non-convex, nlp2mcp may not be suitable

**Issue: NaN in output**
- **Cause:** Numerical issues in input data or expressions
- **Solution:**
  - Check parameter values for NaN/Inf
  - Avoid operations that produce NaN (log of negative, sqrt of negative)
  - Add bounds to prevent invalid domain (e.g., `x.lo = 0.0001` before `log(x)`)

**Issue: Min/max function not supported**
- **Cause:** Min/max in constraint (not objective-defining)
- **Solution:**
  - Reformulate using auxiliary variables and constraints
  - Example: `z = min(x, y)` → `z <= x; z <= y; z >= 0` (if minimizing z)
  - See `docs/research/minmax_objective_reformulation.md`

### Best Practices

**Model Design:**
1. **Start small:** Test on reduced model first (10-100 variables)
2. **Verify convexity:** Check mathematical properties before conversion
3. **Use scaling:** Keep variables and parameters in range [0.1, 100]
4. **Provide good initial points:** Set `.l` values for faster PATH convergence
5. **Avoid deep nesting:** Simplify expressions algebraically when possible

**Debugging:**
1. **Enable verbose mode:** Use `-v` or `-vv` flag to see pipeline stages
2. **Check intermediate output:** Review generated MCP for correctness
3. **Validate manually:** For critical models, verify KKT conditions by hand
4. **Use validation:** Let Day 4 validation catch issues early

**Performance:**
1. **Profile first:** Use Day 5 profiling if conversion is slow
2. **Simplify expressions:** Algebraic simplification before GAMS code
3. **Sparse structures:** Take advantage of block-diagonal or sparse patterns
4. **Batch processing:** Convert multiple models in parallel (separate processes)

---

## Known Issues and Future Work

### Planned Improvements

**Short-term (Sprint 6):**
- Extended min/max support (constraints, not just objective)
- Additional mathematical functions (abs, sign, etc.)
- Performance optimizations for >2K variable models

**Long-term:**
- Integer variable handling (MPEC reformulation)
- Conditional expressions support
- Automatic convexity detection
- Multi-objective optimization

### Reporting Issues

If you encounter:
- ❌ Crashes or unexpected errors
- ❌ Incorrect MCP formulations
- ❌ Missing features critical for your use case
- ❌ Documentation gaps

Please report at: https://github.com/your-repo/nlp2mcp/issues

Include:
- Minimal GAMS model reproducing the issue
- nlp2mcp version
- Error message (full traceback)
- Expected vs actual behavior

---

## Summary

**nlp2mcp is production-ready for:**
- ✅ Convex NLP problems
- ✅ Models up to 1000+ variables
- ✅ Standard GAMS NLP constructs
- ✅ Production optimization workflows

**Use with caution for:**
- ⚠️ Non-convex problems (may fail or produce incorrect results)
- ⚠️ Very large models (>2K variables, not extensively tested)
- ⚠️ Models using unsupported GAMS features

**Not suitable for:**
- ❌ Integer programming (MILP, MINLP)
- ❌ Stochastic programming
- ❌ Models requiring unsupported functions (general min/max in constraints)

For questions or support, see:
- `USER_GUIDE.md` - Usage instructions and examples
- `docs/PATH_SOLVER.md` - PATH solver configuration
- `docs/testing/EDGE_CASE_MATRIX.md` - Detailed edge case documentation

---

**Document Version:** Sprint 5 Day 6  
**Validated:** November 7, 2025  
**Next Review:** Sprint 6 or upon major feature addition

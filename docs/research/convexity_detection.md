# Convexity Detection for GAMS Models

**Date:** 2025-11-03  
**Status:** Research / Future Enhancement  
**Target:** Next Sprint  

## Motivation

The investigation into PATH solver failures (Issue #107) revealed that the tool was attempting to convert non-convex optimization problems to MCP format. For non-convex problems:

- KKT conditions are **necessary but NOT sufficient** for optimality
- MCP reformulation **may not be solvable**
- Solver failures are **expected behavior**, not bugs

To prevent users from attempting to convert unsuitable problems, we need a mechanism to detect when a GAMS model describes a non-convex program.

## Problem Statement

**Goal:** Determine whether a GAMS NLP model describes a convex optimization problem before generating the MCP reformulation.

**Challenge:** Checking convexity is mathematically complex and can be undecidable in the general case.

## Background: What Makes a Problem Convex?

A constrained optimization problem is convex if:

1. **Objective function** is convex (for minimization) or concave (for maximization)
2. **Feasible set** is convex, which requires:
   - All inequality constraints `g(x) ≤ 0` have convex `g(x)`
   - All equality constraints `h(x) = 0` are **affine** (linear)

**Key Insight:** Nonlinear equality constraints almost always result in non-convex feasible sets.

### Examples

**Convex:**
```gams
* Linear program
objective.. obj =e= 2*x + 3*y;
constraint1.. x + y =l= 5;          * Linear inequality
constraint2.. x =e= 2*y + 1;        * Affine equality
x.lo = 0; y.lo = 0;
```

**Convex:**
```gams
* Convex quadratic program
objective.. obj =e= x**2 + y**2;    * Convex objective
constraint1.. x + y =l= 5;          * Linear inequality
x.lo = 0; y.lo = 0;
```

**Non-Convex:**
```gams
* Nonlinear equality constraint
objective.. obj =e= x + y;
constraint1.. sin(x) + cos(y) =e= 0;  * Nonlinear equality → non-convex!
```

**Non-Convex:**
```gams
* Circle constraint
objective.. obj =e= x + y;
constraint1.. x**2 + y**2 =e= 4;  * Circle is non-convex set!
```

## Approaches to Convexity Detection

### Approach 1: Heuristic Pattern Matching ⭐ RECOMMENDED

**Complexity:** Low  
**Accuracy:** Conservative (may reject some convex problems, but won't accept non-convex ones)  
**Speed:** Very Fast  

Detect common patterns that indicate non-convexity:

**Non-convex indicators:**
- ❌ Nonlinear equality constraints (except affine)
- ❌ Trigonometric functions: `sin()`, `cos()`, `tan()`
- ❌ Odd power operations: `x^3`, `x^5`, etc.
- ❌ Negative power operations: `x^(-1)`, `x^(-2)`, etc.
- ❌ Products of variables: `x*y` (bilinear terms)
- ❌ Quotients of variables: `x/y` (fractional terms)
- ❌ Non-monotone functions in equality constraints

**Convex patterns (allowed):**
- ✅ Linear constraints
- ✅ Affine equality constraints: `2*x + 3*y = 5`
- ✅ Quadratic terms: `x^2`, `x^2 + y^2` (with all positive coefficients)
- ✅ Bounds on variables

**Implementation:**
```python
def quick_convexity_check(model_ir: ModelIR) -> list[str]:
    """
    Fast heuristic check for obvious non-convexity.
    Returns list of warnings.
    """
    warnings = []
    
    # Rule 1: Check for nonlinear equality constraints
    for eq_name, eq in model_ir.equations.items():
        if eq.relation == Rel.EQ:
            lhs, rhs = eq.lhs_rhs
            expr = Binary("-", lhs, rhs)
            
            # Check if affine (linear)
            if not is_affine(expr):
                warnings.append(
                    f"⚠️ Equation '{eq_name}' is a nonlinear equality constraint.\n"
                    f"   Nonlinear equalities typically define non-convex feasible sets.\n"
                    f"   Example: x² + y² = 4 defines a circle (non-convex).\n"
                    f"   KKT-based MCP reformulation may not be solvable."
                )
    
    # Rule 2: Check for non-convex functions
    all_exprs = [model_ir.objective.expr]
    for eq in model_ir.equations.values():
        all_exprs.extend(eq.lhs_rhs)
    
    for expr in all_exprs:
        # Check for trigonometric functions
        trig_funcs = find_functions(expr, ["sin", "cos", "tan"])
        if trig_funcs:
            warnings.append(
                f"⚠️ Found trigonometric functions: {trig_funcs}\n"
                f"   Trigonometric functions are neither convex nor concave.\n"
                f"   The problem is likely non-convex."
            )
        
        # Check for bilinear terms (x*y where both are variables)
        bilinear = find_bilinear_terms(expr)
        if bilinear:
            warnings.append(
                f"⚠️ Found bilinear terms (products of variables): {bilinear}\n"
                f"   Bilinear terms are non-convex.\n"
                f"   The problem is likely non-convex."
            )
        
        # Check for variable quotients (x/y)
        quotients = find_variable_quotients(expr)
        if quotients:
            warnings.append(
                f"⚠️ Found variable quotients: {quotients}\n"
                f"   Ratios of variables are generally non-convex.\n"
                f"   The problem is likely non-convex."
            )
    
    return warnings

def is_affine(expr: Expr) -> bool:
    """Check if expression is affine (linear)."""
    match expr:
        case Const(_):
            return True
        case VarRef(_):
            return True
        case ParamRef(_):
            return True
        case Binary(op, left, right) if op in ("+", "-"):
            return is_affine(left) and is_affine(right)
        case Binary("*", left, right):
            # Affine if one side is constant
            return (is_constant(left) and is_affine(right)) or \
                   (is_affine(left) and is_constant(right))
        case Binary("/", left, right):
            # Affine if numerator is affine and denominator is constant
            return is_affine(left) and is_constant(right)
        case Unary(_, operand):
            return is_affine(operand)
        case _:
            return False

def is_constant(expr: Expr) -> bool:
    """Check if expression contains no variables."""
    match expr:
        case Const(_):
            return True
        case ParamRef(_):
            return True  # Parameters are constants w.r.t. variables
        case VarRef(_):
            return False
        case Binary(_, left, right):
            return is_constant(left) and is_constant(right)
        case Unary(_, operand):
            return is_constant(operand)
        case _:
            return False
```

**Advantages:**
- ✅ Very fast (no complex computation)
- ✅ Easy to understand and maintain
- ✅ Conservative (won't incorrectly accept non-convex problems)
- ✅ Provides helpful error messages
- ✅ Catches the most common non-convex patterns

**Disadvantages:**
- ⚠️ May reject some convex problems (false negatives)
- ⚠️ Cannot verify positive semi-definiteness of quadratic forms
- ⚠️ Cannot handle complex compositions of convex functions

---

### Approach 2: AST-Based Convexity Classification

**Complexity:** Medium  
**Accuracy:** Better than heuristics, but still conservative  
**Speed:** Fast  

Walk the AST and classify each expression using composition rules.

**Implementation Sketch:**
```python
from enum import Enum

class ConvexityClass(Enum):
    CONSTANT = "constant"
    AFFINE = "affine"
    CONVEX = "convex"
    CONCAVE = "concave"
    UNKNOWN = "unknown"

def get_convexity_class(expr: Expr) -> ConvexityClass:
    """Determine convexity class using composition rules."""
    
    match expr:
        case Const(_):
            return ConvexityClass.CONSTANT
        
        case VarRef(_):
            return ConvexityClass.AFFINE
        
        case ParamRef(_):
            return ConvexityClass.CONSTANT
        
        case Binary("+", left, right):
            left_class = get_convexity_class(left)
            right_class = get_convexity_class(right)
            # Convex + Convex = Convex
            # Concave + Concave = Concave
            # Affine + X = X
            return combine_addition(left_class, right_class)
        
        case Binary("-", left, right):
            left_class = get_convexity_class(left)
            right_class = get_convexity_class(right)
            # Convex - Concave = Convex
            # Concave - Convex = Concave
            return combine_subtraction(left_class, right_class)
        
        case Binary("*", left, right):
            left_class = get_convexity_class(left)
            right_class = get_convexity_class(right)
            
            if left_class == ConvexityClass.CONSTANT:
                # Positive constant * Convex = Convex
                # Negative constant * Convex = Concave
                # Need to check sign of constant
                if is_positive_constant(left):
                    return right_class
                elif is_negative_constant(left):
                    return flip_convexity(right_class)
            
            if right_class == ConvexityClass.CONSTANT:
                if is_positive_constant(right):
                    return left_class
                elif is_negative_constant(right):
                    return flip_convexity(left_class)
            
            # Variable * Variable = UNKNOWN (bilinear, non-convex)
            return ConvexityClass.UNKNOWN
        
        case Binary("^", base, Const(exp)):
            base_class = get_convexity_class(base)
            
            if exp == 1:
                return base_class
            elif exp == 2 and base_class == ConvexityClass.AFFINE:
                return ConvexityClass.CONVEX  # x^2 is convex
            elif exp > 0 and exp == int(exp) and exp % 2 == 0:
                # Even positive integer powers of affine = convex
                if base_class == ConvexityClass.AFFINE:
                    return ConvexityClass.CONVEX
            
            return ConvexityClass.UNKNOWN
        
        case Call("exp", (arg,)):
            arg_class = get_convexity_class(arg)
            if arg_class in (ConvexityClass.AFFINE, ConvexityClass.CONVEX):
                return ConvexityClass.CONVEX  # exp is convex and increasing
            return ConvexityClass.UNKNOWN
        
        case Call("log", (arg,)):
            arg_class = get_convexity_class(arg)
            if arg_class == ConvexityClass.AFFINE:
                return ConvexityClass.CONCAVE  # log is concave
            return ConvexityClass.UNKNOWN
        
        case Call("sqrt", (arg,)):
            arg_class = get_convexity_class(arg)
            if arg_class == ConvexityClass.AFFINE:
                return ConvexityClass.CONCAVE  # sqrt is concave
            return ConvexityClass.UNKNOWN
        
        case Call(func, _) if func in ("sin", "cos", "tan"):
            return ConvexityClass.UNKNOWN  # Non-convex
        
        case _:
            return ConvexityClass.UNKNOWN

def check_problem_convexity(model_ir: ModelIR) -> tuple[bool, list[str]]:
    """Check if entire problem is convex."""
    warnings = []
    
    # Check objective
    obj_class = get_convexity_class(model_ir.objective.expr)
    
    if model_ir.objective.sense == ObjSense.MINIMIZE:
        if obj_class not in (ConvexityClass.CONSTANT, ConvexityClass.AFFINE, 
                              ConvexityClass.CONVEX):
            warnings.append(
                f"Minimization objective is not convex (class: {obj_class.value})"
            )
    else:  # MAXIMIZE
        if obj_class not in (ConvexityClass.CONSTANT, ConvexityClass.AFFINE,
                              ConvexityClass.CONCAVE):
            warnings.append(
                f"Maximization objective is not concave (class: {obj_class.value})"
            )
    
    # Check constraints
    for eq_name, eq in model_ir.equations.items():
        lhs, rhs = eq.lhs_rhs
        
        if eq.relation == Rel.EQ:
            # Equality must be affine
            expr_class = get_convexity_class(Binary("-", lhs, rhs))
            if expr_class not in (ConvexityClass.CONSTANT, ConvexityClass.AFFINE):
                warnings.append(
                    f"Equality constraint '{eq_name}' is not affine "
                    f"(class: {expr_class.value})"
                )
        
        elif eq.relation == Rel.LE:
            # g(x) <= 0 requires convex g
            expr_class = get_convexity_class(Binary("-", lhs, rhs))
            if expr_class not in (ConvexityClass.CONSTANT, ConvexityClass.AFFINE,
                                  ConvexityClass.CONVEX):
                warnings.append(
                    f"Inequality constraint '{eq_name}' (<= 0) is not convex "
                    f"(class: {expr_class.value})"
                )
        
        elif eq.relation == Rel.GE:
            # g(x) >= 0 ⟺ -g(x) <= 0 requires -g convex ⟺ g concave
            expr_class = get_convexity_class(Binary("-", lhs, rhs))
            if expr_class not in (ConvexityClass.CONSTANT, ConvexityClass.AFFINE,
                                  ConvexityClass.CONCAVE):
                warnings.append(
                    f"Inequality constraint '{eq_name}' (>= 0) is not concave "
                    f"(class: {expr_class.value})"
                )
    
    is_convex = len(warnings) == 0
    return is_convex, warnings
```

**Advantages:**
- ✅ More accurate than simple pattern matching
- ✅ Uses formal composition rules
- ✅ Can handle some function compositions
- ✅ Still relatively fast

**Disadvantages:**
- ⚠️ More complex to implement and maintain
- ⚠️ Cannot determine sign of constants symbolically (need evaluation)
- ⚠️ Cannot verify PSD of quadratic forms with cross terms (x*y coefficients)
- ⚠️ Still conservative for complex compositions

---

### Approach 3: Symbolic Hessian Analysis

**Complexity:** High  
**Accuracy:** High (but still incomplete for general case)  
**Speed:** Slow (requires symbolic computation)  

Compute the Hessian symbolically and check positive semi-definiteness.

**Challenges:**
- Computing symbolic Hessian is expensive
- Checking PSD symbolically is very hard (often undecidable)
- Would need symbolic linear algebra library
- Scalability issues for large problems

**Not recommended** due to complexity and limited practical benefit over Approach 2.

---

### Approach 4: Disciplined Convex Programming (DCP)

**Complexity:** High  
**Accuracy:** Very High  
**Speed:** Medium  

Implement full DCP rules similar to CVX/CVXPY.

**Example Library:** Use rules from [CVXPY](https://www.cvxpy.org/tutorial/dcp/index.html)

**Advantages:**
- ✅ Very rigorous
- ✅ Well-studied methodology
- ✅ Can handle complex compositions

**Disadvantages:**
- ⚠️ Very complex to implement completely
- ⚠️ Would essentially be reimplementing CVXPY's verification
- ⚠️ Overkill for our use case

**Not recommended** - too much complexity for marginal benefit.

---

## Recommendation: Hybrid Approach

**Implement a two-tier system:**

### Tier 1: Quick Heuristic Check (Always Enabled)

Use **Approach 1** as the default:
- Fast pattern matching for common non-convex indicators
- Run automatically on every model
- Emit warnings but allow user to continue
- Focus on the most important checks:
  1. Nonlinear equality constraints
  2. Trigonometric functions
  3. Bilinear terms
  4. Variable quotients

### Tier 2: Detailed Analysis (Optional Flag)

Use **Approach 2** with a CLI flag:
- AST-based convexity classification
- Run only when user requests: `--check-convexity`
- Provides more detailed report
- Can be used to verify convexity before committing to MCP generation

## Integration into nlp2mcp

### Phase 1: Warnings (Next Sprint)

**Goal:** Warn users about potential non-convexity without blocking them.

**Implementation:**

1. Add quick convexity check in `src/convexity/checker.py`:
   ```python
   def quick_convexity_check(model_ir: ModelIR) -> list[str]:
       """Fast heuristic check for obvious non-convexity."""
       # Implementation from Approach 1
   ```

2. Integrate into CLI after parsing:
   ```python
   # In src/cli.py, after parse_model_file()
   model = parse_model_file(input_file)
   
   # Quick convexity check
   warnings = quick_convexity_check(model)
   if warnings:
       click.echo("\n⚠️  CONVEXITY WARNING", err=True)
       click.echo("=" * 60, err=True)
       for warning in warnings:
           click.echo(f"\n{warning}", err=True)
       click.echo(
           "\nFor non-convex problems:\n"
           "• KKT conditions are necessary but NOT sufficient for optimality\n"
           "• MCP reformulation may not be solvable\n"
           "• PATH solver may fail (this is expected behavior)\n"
           "\nConsider using a standard NLP solver (CONOPT, IPOPT) instead.\n",
           err=True
       )
       click.echo("=" * 60, err=True)
   ```

3. Add tests in `tests/unit/convexity/test_checker.py`:
   ```python
   def test_detects_nonlinear_equality():
       """Should detect sin(x) + cos(y) = 0 as non-convex."""
       
   def test_detects_circle_constraint():
       """Should detect x^2 + y^2 = 4 as non-convex."""
       
   def test_allows_linear_program():
       """Should not warn on simple linear program."""
       
   def test_allows_convex_qp():
       """Should not warn on x^2 + y^2 objective."""
   ```

### Phase 2: Strict Mode (Future)

**Goal:** Add flag to fail on non-convexity.

```python
@click.option(
    "--strict-convexity",
    is_flag=True,
    default=False,
    help="Fail if problem appears to be non-convex"
)
def main(..., strict_convexity):
    ...
    warnings = quick_convexity_check(model)
    if warnings and strict_convexity:
        click.echo("ERROR: Non-convex problem detected.", err=True)
        for warning in warnings:
            click.echo(f"\n{warning}", err=True)
        sys.exit(1)
```

### Phase 3: Detailed Analysis (Future)

**Goal:** Add optional detailed convexity analysis.

```python
@click.option(
    "--analyze-convexity",
    is_flag=True,
    default=False,
    help="Perform detailed convexity analysis and show report"
)
def main(..., analyze_convexity):
    ...
    if analyze_convexity:
        report = detailed_convexity_analysis(model)
        click.echo(report.format())
```

## Implementation Plan for Next Sprint

### Sprint Tasks

1. **Create convexity checking module** (`src/convexity/`)
   - `checker.py` - Main convexity checking logic
   - `patterns.py` - Pattern detection helpers
   - `utils.py` - AST traversal utilities

2. **Implement Tier 1 (Quick Check)**
   - `quick_convexity_check()` function
   - Helper: `is_affine()`
   - Helper: `find_bilinear_terms()`
   - Helper: `find_variable_quotients()`
   - Helper: `find_functions()`

3. **Integrate into CLI**
   - Add warning messages after parsing
   - Format warnings nicely
   - Provide guidance on what to do

4. **Add tests**
   - Unit tests for pattern detection
   - Integration tests with example models
   - Test warning messages

5. **Update documentation**
   - Add "Limitations" section to README
   - Document when nlp2mcp should/shouldn't be used
   - Add examples of convex vs. non-convex problems

### Estimated Effort

- **Development:** 1-2 days
- **Testing:** 0.5 days
- **Documentation:** 0.5 days
- **Total:** 2-3 days

### Success Criteria

- ✅ Tool warns on `bounds_nlp.gms` (sin/cos equality)
- ✅ Tool warns on `nonlinear_mix.gms` (circle constraint)
- ✅ Tool does NOT warn on convex examples (simple_nlp, etc.)
- ✅ Warning messages are clear and actionable
- ✅ All tests pass

## Future Enhancements

### After Initial Implementation

1. **Expand pattern library**
   - Add more non-convex patterns
   - Handle more function compositions
   - Detect specific non-convex structures

2. **Implement Tier 2 (AST-based)**
   - Add ConvexityClass enum
   - Implement composition rules
   - Add `--analyze-convexity` flag

3. **Quadratic form analysis**
   - Extract quadratic forms from expressions
   - Check if Q matrix is positive semi-definite
   - Verify convexity of QPs

4. **Interactive mode**
   - Prompt user when non-convexity detected
   - Offer to continue anyway
   - Suggest reformulations

5. **GAMS integration**
   - Use GAMS's convexity diagnostics if available
   - Parse GAMS solver output for convexity info

## References

### Academic Papers
- Boyd, S., & Vandenberghe, L. (2004). *Convex Optimization*. Cambridge University Press.
- Grant, M., & Boyd, S. (2008). "Graph implementations for nonsmooth convex programs." *Recent Advances in Learning and Control*.

### Software Tools
- [CVXPY](https://www.cvxpy.org/) - Disciplined Convex Programming in Python
- [CVX](http://cvxr.com/cvx/) - MATLAB software for disciplined convex programming
- [Convex.jl](https://github.com/jump-dev/Convex.jl) - Julia library for DCP

### GAMS Documentation
- GAMS User's Guide - Model Types and Attributes
- GAMS Solver Manuals - Convexity requirements

## Related Issues

- #107 - PATH Solver Fails on Non-Convex Models (investigation completed)
- Future: Add convexity warnings to user interface

## Notes

- This is a **heuristic** approach - we cannot detect all non-convex problems
- The goal is to catch **common mistakes**, not to provide a complete convexity oracle
- Users should still understand their problem's mathematical properties
- When in doubt, test with multiple solvers and check KKT conditions manually

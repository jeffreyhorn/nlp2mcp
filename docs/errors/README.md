# nlp2mcp Error Reference

This document describes all errors and warnings you may encounter when using nlp2mcp.

## Quick Index

**Errors (Blocking):**
- [E001: Undefined Variable](#e001-undefined-variable)
- [E002: Undefined Equation](#e002-undefined-equation)
- [E003: Type Mismatch](#e003-type-mismatch)
- [E101: Syntax Error](#e101-syntax-error)

**Warnings (Non-Blocking):**
- [W301: Nonlinear Equality](#w301-nonlinear-equality)
- [W302: Trigonometric Function](#w302-trigonometric-function)
- [W303: Bilinear Term](#w303-bilinear-term)
- [W304: Division/Quotient](#w304-division-quotient)
- [W305: Odd-Power Polynomial](#w305-odd-power-polynomial)

---

## Error Code Format

Error codes follow the format: **{Level}{Category}{Number}**

**Levels:**
- `E` = Error (blocking, prevents conversion)
- `W` = Warning (non-blocking, user should review)
- `I` = Info (non-blocking, informational only)

**Categories:**
- `0xx` = Syntax/Validation errors
- `1xx` = Parser/Semantic errors
- `2xx` = Solver errors
- `3xx` = Convexity warnings
- `9xx` = Internal errors

---

## E001: Undefined Variable

**Level:** Error  
**Category:** Validation

### Description

A variable is referenced in an equation or expression but has not been declared in the `Variables` section of the GAMS model.

### Common Causes

1. Typo in variable name
2. Forgot to add variable to `Variables` declaration
3. Variable was declared in different scope (e.g., inside a `$if` block)

### How to Fix

**Quick Fix:**
Add the missing variable to the `Variables` declaration at the top of your model.

**Step-by-Step:**
1. Locate the `Variables` section in your GAMS file
2. Add the undefined variable to the list
3. Ensure the variable name matches exactly (case-sensitive)

### Example

**GAMS Code (Error):**
```gams
Variables x, y;
Equations eq1;
eq1.. x + y + z =e= 10;  # z is not declared
```

**Error Message:**
```
Error E001: Undefined variable 'z' (line 3, column 15)

   3 | eq1.. x + y + z =e= 10;
                     ^

Variable 'z' is used but not declared in the Variables section.

Action: Add 'z' to the Variables declaration.
See: https://github.com/jeffreyhorn/nlp2mcp/blob/main/docs/errors/README.md#e001-undefined-variable
```

**Fixed Code:**
```gams
Variables x, y, z;  # Added z here
Equations eq1;
eq1.. x + y + z =e= 10;
```

### Related

- [E002: Undefined Equation](#e002-undefined-equation)

---

## E002: Undefined Equation

**Level:** Error  
**Category:** Validation

### Description

An equation is referenced (e.g., in a `Model` statement) but has not been declared in the `Equations` section.

### Common Causes

1. Typo in equation name
2. Forgot to add equation to `Equations` declaration
3. Equation declaration in wrong order

### How to Fix

**Quick Fix:**
Add the missing equation to the `Equations` declaration before it is referenced.

**Step-by-Step:**
1. Locate the `Equations` section
2. Add the undefined equation name
3. Define the equation with `..` syntax
4. Reference it in the `Model` statement

### Example

**GAMS Code (Error):**
```gams
Equations balance;
balance.. x + y =e= 10;

Model m /balance, cost/;  # cost is not declared
```

**Error Message:**
```
Error E002: Undefined equation 'cost' (line 4, column 19)

   4 | Model m /balance, cost/;
                         ^^^^

Equation 'cost' is referenced but not declared in the Equations section.

Action: Add 'cost' to the Equations declaration and define it.
See: https://github.com/jeffreyhorn/nlp2mcp/blob/main/docs/errors/README.md#e002-undefined-equation
```

**Fixed Code:**
```gams
Equations balance, cost;
balance.. x + y =e= 10;
cost.. 2*x + 3*y =e= obj;  # Added equation definition

Model m /balance, cost/;
```

---

## E003: Type Mismatch

**Level:** Error  
**Category:** Validation

### Description

An operation is attempted between incompatible types (e.g., adding a scalar to a set, using a parameter where a variable is expected).

### Common Causes

1. Using a parameter in place of a variable
2. Indexing mismatch (scalar used where indexed variable expected)
3. Set operations on non-set types

### How to Fix

**Quick Fix:**
Ensure all operands in expressions have compatible types.

**Step-by-Step:**
1. Check the declared type of each symbol
2. Verify index sets match for indexed operations
3. Convert types if necessary (e.g., parameter to variable)

### Example

**GAMS Code (Error):**
```gams
Parameter p /5/;
Variables x;
Equations eq1;
eq1.. p + x =e= 10;  # p is a parameter, not a variable
```

**Error Message:**
```
Error E003: Type mismatch (line 4, column 7)

   4 | eq1.. p + x =e= 10;
             ^

Cannot use parameter 'p' in equation expression. Only variables allowed.

Action: If 'p' should vary, declare it as a Variable instead of Parameter.
See: https://github.com/jeffreyhorn/nlp2mcp/blob/main/docs/errors/README.md#e003-type-mismatch
```

**Note:** This is actually a design choice in GAMS - parameters in equations are allowed and treated as constants. This error might not occur in standard GAMS but could be a validation rule in nlp2mcp.

---

## E101: Syntax Error

**Level:** Error  
**Category:** Parser

### Description

The GAMS code contains invalid syntax that cannot be parsed. This is a general syntax error that doesn't fit into more specific categories.

### Common Causes

1. Missing semicolons
2. Unmatched parentheses or brackets
3. Invalid keywords or operators
4. Unexpected tokens

### How to Fix

**Quick Fix:**
Review the indicated line and fix the syntax according to GAMS language rules.

**Step-by-Step:**
1. Check for missing semicolons at end of statements
2. Verify all parentheses/brackets are balanced
3. Ensure keywords are spelled correctly
4. Check operator syntax

### Example

**GAMS Code (Error):**
```gams
Variables x, y;
Equations eq1;
eq1.. x +  =e= 10;  # Missing operand after +
```

**Error Message:**
```
Error E101: Syntax error (line 3, column 12)

   3 | eq1.. x +  =e= 10;
                  ^

Unexpected token '='. Expected expression after '+' operator.

Action: Add the missing operand or remove the extra '+' operator.
See: https://github.com/jeffreyhorn/nlp2mcp/blob/main/docs/errors/README.md#e101-syntax-error
```

**Fixed Code:**
```gams
Variables x, y;
Equations eq1;
eq1.. x + y =e= 10;  # Added missing operand 'y'
```

---

## W301: Nonlinear Equality

**Level:** Warning  
**Category:** Convexity

### Description

The equation contains a nonlinear expression with an equality constraint (`=e=`), which may define a nonconvex feasible region. This can cause PATH solver to fail or return incorrect solutions.

### Common Causes

1. Circle/sphere constraints: `x^2 + y^2 = 4`
2. Hyperbola constraints: `x * y = 1`
3. Exponential equalities: `exp(x) = 5`
4. Product equalities: `x * y = constant`

### Why This Matters

Nonconvex feasible regions can have:
- Multiple local optima
- Disconnected feasible regions
- Solver convergence failures

PATH solver is designed for convex problems and may fail on nonconvex ones.

### How to Fix

**Option 1: Replace with inequality (if feasible region allows)**
```gams
# Instead of:
circle.. sqr(x) + sqr(y) =e= 4;

# Use:
circle_ub.. sqr(x) + sqr(y) =l= 4;  # Points inside or on circle
```

**Option 2: Accept the warning if this is intentional**
PATH may still solve the problem, especially if:
- The feasible region is locally convex near the solution
- You have a good starting point
- The problem is small

**Option 3: Use a global solver (not PATH)**
If convexity is critical, consider using a global optimization solver instead of PATH.

### Example

**GAMS Code (Warning):**
```gams
Variables x, y;
Equations circle;
circle.. sqr(x) + sqr(y) =e= 4;  # Nonlinear equality
```

**Warning Message:**
```
Warning W301: Nonlinear equality may be nonconvex (line 3, column 10)

   3 | circle.. sqr(x) + sqr(y) =e= 4;
              ^~~~~~~~~~~~~~~~~~~~~^

Equation 'circle' has nonlinear equality constraint, which defines a potentially
nonconvex feasible region (circle boundary). PATH solver may fail.

Action: Consider replacing with inequality (=l= or =g=) if feasible region allows.
See: https://github.com/jeffreyhorn/nlp2mcp/blob/main/docs/errors/README.md#w301-nonlinear-equality
```

**Alternative (if feasible):**
```gams
Variables x, y;
Equations circle_ub;
circle_ub.. sqr(x) + sqr(y) =l= 4;  # Interior + boundary (convex)
```

### Related

- [W303: Bilinear Term](#w303-bilinear-term)

---

## W302: Trigonometric Function

**Level:** Warning  
**Category:** Convexity

### Description

The equation contains trigonometric functions (sin, cos, tan), which are generally nonconvex and can cause solver issues.

### Common Causes

1. Periodic constraints
2. Angular calculations
3. Wave equations
4. Oscillatory systems

### Why This Matters

Trigonometric functions are nonconvex:
- Multiple local minima/maxima
- Periodic behavior complicates optimization
- Gradient-based solvers may get stuck in local optima

### How to Fix

**Option 1: Linearize if possible**
For small angles, use linear approximations:
- `sin(x) ≈ x` for small x
- `cos(x) ≈ 1 - x²/2` for small x

**Option 2: Restrict domain**
If angle range is limited, convexity may hold locally.

**Option 3: Use global solver**
Accept nonconvexity and use a solver designed for it.

### Example

**GAMS Code (Warning):**
```gams
Variables theta, x, y;
Equations transform;
transform.. x =e= sin(theta) + y;  # Nonconvex trig function
```

**Warning Message:**
```
Warning W302: Trigonometric function may be nonconvex (line 3, column 18)

   3 | transform.. x =e= sin(theta) + y;
                          ^^^

Function 'sin' is nonconvex. Solver may struggle with multiple local optima.

Action: Consider linearization for small angles or use global solver.
See: https://github.com/jeffreyhorn/nlp2mcp/blob/main/docs/errors/README.md#w302-trigonometric-function
```

---

## W303: Bilinear Term

**Level:** Warning  
**Category:** Convexity

### Description

The equation contains a product of two variables (bilinear term), which is nonconvex and can cause solver issues.

### Common Causes

1. Product of two variables: `x * y`
2. Quotient reformulated as product: `z = 1/(x*y)` → `x*y*z = 1`
3. Multiplicative utility functions
4. Flow-pressure relationships

### Why This Matters

Bilinear terms `x * y` are:
- Nonconvex (saddle-shaped)
- Source of multiple local optima
- Difficult for local solvers like PATH

### How to Fix

**Option 1: McCormick relaxation (if bounds known)**
If variables have finite bounds, replace bilinear term with McCormick envelopes.

**Option 2: Fix one variable**
If one variable can be fixed or parameterized, problem becomes convex.

**Option 3: Accept nonconvexity**
Use good starting point and hope PATH converges.

### Example

**GAMS Code (Warning):**
```gams
Variables x, y, z;
Equations prod;
prod.. z =e= x * y;  # Bilinear term
```

**Warning Message:**
```
Warning W303: Bilinear term may be nonconvex (line 3, column 14)

   3 | prod.. z =e= x * y;
                    ^^^^^

Product of variables 'x' and 'y' creates nonconvex bilinear term.

Action: If variables have bounds, consider McCormick relaxation. Otherwise, use global solver.
See: https://github.com/jeffreyhorn/nlp2mcp/blob/main/docs/errors/README.md#w303-bilinear-term
```

---

## W304: Division/Quotient

**Level:** Warning  
**Category:** Convexity

### Description

The equation contains division of expressions, which is generally nonconvex unless the numerator is affine and denominator is constant.

### Common Causes

1. Ratio constraints: `x / y`
2. Efficiency metrics: `output / input`
3. Normalized values: `value / total`
4. Reciprocals: `1 / x`

### Why This Matters

Division creates nonconvexity:
- `x / y` is nonconvex in general
- Singularities when denominator → 0
- Multiple local optima possible

### How to Fix

**Option 1: Reformulate with multiplication**
```gams
# Instead of: z = x / y
# Use: z * y = x (if y > 0 known)
```

**Option 2: Use bounds to ensure denominator > 0**
Add explicit lower bound on denominator.

**Option 3: Accept nonconvexity**
Ensure good starting point where denominator is non-zero.

### Example

**GAMS Code (Warning):**
```gams
Variables x, y, ratio;
Equations efficiency;
efficiency.. ratio =e= x / y;  # Division (nonconvex)
```

**Warning Message:**
```
Warning W304: Division/quotient may be nonconvex (line 3, column 28)

   3 | efficiency.. ratio =e= x / y;
                                ^^^^^

Division 'x / y' is nonconvex. Also risk of division by zero if y = 0.

Action: Reformulate as multiplication (ratio * y = x) if y > 0, or add bounds.
See: https://github.com/jeffreyhorn/nlp2mcp/blob/main/docs/errors/README.md#w304-division-quotient
```

**Better formulation:**
```gams
Variables x, y, ratio;
y.lo = 0.01;  # Ensure y > 0
Equations efficiency;
efficiency.. ratio * y =e= x;  # Avoid explicit division
```

---

## W305: Odd-Power Polynomial

**Level:** Warning  
**Category:** Convexity

### Description

The equation contains an odd power of a variable (e.g., `x^3`, `x^5`), which is nonconvex.

### Common Causes

1. Cubic terms: `x^3`
2. Higher odd powers: `x^5`, `x^7`
3. Polynomial constraints

### Why This Matters

Odd powers are nonconvex:
- `x^3` has inflection point at x=0
- Not jointly convex with other variables
- Can create multiple local optima

### How to Fix

**Option 1: Replace with even power if possible**
`x^2` and `x^4` are convex (for x ≥ 0).

**Option 2: Add domain restrictions**
Restrict to region where function is locally convex.

**Option 3: Accept nonconvexity**
Use solver with good starting point.

### Example

**GAMS Code (Warning):**
```gams
Variables x, y;
Equations cubic;
cubic.. y =e= power(x, 3);  # Cubic term (nonconvex)
```

**Warning Message:**
```
Warning W305: Odd-power polynomial may be nonconvex (line 3, column 15)

   3 | cubic.. y =e= power(x, 3);
                     ^^^^^^^^^^^^

Odd power 'x^3' is nonconvex. Solver may struggle.

Action: If possible, reformulate with even powers or restrict domain.
See: https://github.com/jeffreyhorn/nlp2mcp/blob/main/docs/errors/README.md#w305-odd-power-polynomial
```

---

## Getting Help

If you encounter an error not documented here:

1. **Check the GAMS documentation** - Many errors are related to standard GAMS syntax
2. **Review the error message** - The error message includes specific guidance
3. **File an issue** - If you believe this is a bug in nlp2mcp, file an issue on GitHub with:
   - Error message
   - Minimal GAMS code that reproduces the error
   - Expected behavior

## Contributing

Found an error that should be documented? Please submit a pull request with:
1. Error code and description
2. Example that triggers the error
3. Suggested fix with before/after code samples

---

**Last Updated:** Sprint 6 Day 7  
**Version:** 0.3.0

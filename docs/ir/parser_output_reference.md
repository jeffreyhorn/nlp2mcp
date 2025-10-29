# Parser Output Reference

**Purpose:** Document how the parser represents every GAMS construct as AST nodes to prevent implementation confusion.

**Created:** 2025-10-29  
**Last Updated:** 2025-10-29  
**Related:** Sprint 3 Prep Plan Task 2, [System Architecture](../architecture/SYSTEM_ARCHITECTURE.md)

**Why This Exists:** Issue #25 occurred because developers assumed `x^2` was parsed as `Call("power", ...)` when it's actually `Binary("^", ...)`. This reference prevents such assumptions.

---

## Quick Reference Card

**Most Common Operations:**

| GAMS | AST | Note |
|------|-----|------|
| `x + y` | `Binary("+", ...)` | Addition |
| `x * y` | `Binary("*", ...)` | Multiplication |
| `x / y` | `Binary("/", ...)` | Division |
| `x ^ 2` | `Binary("^", ...)` | ⚠️ **Power is Binary, NOT Call!** |
| `exp(x)` | `Call("exp", ...)` | Function call |
| `sum(i, x(i))` | `Sum(...)` | Aggregation |
| `x` | `VarRef("x", ())` | Scalar variable (empty tuple) |
| `x(i)` | `VarRef("x", ("i",))` | Indexed variable (tuple!) |
| `3.14` | `Const(3.14)` | Numeric constant |

---

## Table of Contents

1. [Binary Operators](#binary-operators)
2. [Unary Operators](#unary-operators)
3. [Function Calls](#function-calls)
4. [Variable References](#variable-references)
5. [Parameter References](#parameter-references)
6. [Constants](#constants)
7. [Aggregations (Sum)](#aggregations-sum)
8. [Equation Relations](#equation-relations)
9. [Common Pitfalls](#common-pitfalls)
10. [Real Examples](#real-examples)

---

## Binary Operators

All binary operations are represented as `Binary(op, left, right)` nodes.

**AST Definition:**
```python
@dataclass(frozen=True)
class Binary(Expr):
    op: str  # Operator: "+", "-", "*", "/", "^"
    left: Expr
    right: Expr
```

### Supported Operators

| GAMS Syntax | AST Representation | Op String | Description |
|-------------|-------------------|-----------|-------------|
| `x + y` | `Binary("+", VarRef("x"), VarRef("y"))` | `"+"` | Addition |
| `x - y` | `Binary("-", VarRef("x"), VarRef("y"))` | `"-"` | Subtraction |
| `x * y` | `Binary("*", VarRef("x"), VarRef("y"))` | `"*"` | Multiplication |
| `x / y` | `Binary("/", VarRef("x"), VarRef("y"))` | `"/"` | Division |
| `x ^ 2` | `Binary("^", VarRef("x"), Const(2.0))` | `"^"` | **Power** |
| `x ^ y` | `Binary("^", VarRef("x"), VarRef("y"))` | `"^"` | **Power (variable exponent)** |

### Critical: Power Operator (Issue #25)

**⚠️ IMPORTANT:** The power operator `^` is parsed as `Binary("^", ...)`, NOT as `Call("power", ...)`.

```python
# GAMS: x ^ 2
# Parser produces:
Binary("^", VarRef("x"), Const(2.0))

# NOT:
Call("power", (VarRef("x"), Const(2.0)))  # ❌ Wrong!
```

**What AD Does:**
The differentiation engine internally converts `Binary("^", ...)` to `Call("power", ...)` for processing, but at parse time it's always `Binary`.

**Example from `nonlinear_mix.gms`:**
```gams
poly_balance.. x ^ 2 + y ^ 2 =e= 4;
```

Parses to:
```python
EquationDef(
    name="poly_balance",
    expression=Binary("-",
        Binary("+",
            Binary("^", VarRef("x"), Const(2.0)),  # x^2
            Binary("^", VarRef("y"), Const(2.0))   # y^2
        ),
        Const(4.0)
    )
)
```

### Operator Precedence

Parser respects standard mathematical precedence:
1. Exponentiation (`^`) - highest
2. Multiplication (`*`) and Division (`/`)
3. Addition (`+`) and Subtraction (`-`) - lowest

**Example:**
```gams
x + y * z ^ 2
```

Parses to:
```python
Binary("+",
    VarRef("x"),
    Binary("*",
        VarRef("y"),
        Binary("^", VarRef("z"), Const(2.0))
    )
)
```

---

## Unary Operators

Unary operations are represented as `Unary(op, child)` nodes.

**AST Definition:**
```python
@dataclass(frozen=True)
class Unary(Expr):
    op: str  # "+", "-"
    child: Expr
```

### Supported Operators

| GAMS Syntax | AST Representation | Op String | Description |
|-------------|-------------------|-----------|-------------|
| `-x` | `Unary("-", VarRef("x"))` | `"-"` | Negation |
| `+x` | `Unary("+", VarRef("x"))` | `"+"` | Explicit positive |

**Example:**
```gams
-x * 2
```

Parses to:
```python
Binary("*",
    Unary("-", VarRef("x")),
    Const(2.0)
)
```

---

## Function Calls

All function calls are represented as `Call(func_name, args)` nodes.

**AST Definition:**
```python
@dataclass(frozen=True)
class Call(Expr):
    func: str  # Function name
    args: tuple[Expr, ...]  # Arguments as tuple
```

### Supported Functions

| GAMS Syntax | AST Representation | Function | Description |
|-------------|-------------------|----------|-------------|
| `exp(x)` | `Call("exp", (VarRef("x"),))` | `"exp"` | Exponential e^x |
| `log(x)` | `Call("log", (VarRef("x"),))` | `"log"` | Natural logarithm |
| `sqrt(x)` | `Call("sqrt", (VarRef("x"),))` | `"sqrt"` | Square root |
| `sin(x)` | `Call("sin", (VarRef("x"),))` | `"sin"` | Sine |
| `cos(x)` | `Call("cos", (VarRef("x"),))` | `"cos"` | Cosine |
| `tan(x)` | `Call("tan", (VarRef("x"),))` | `"tan"` | Tangent |

**Note on Arguments:**
- Arguments are always a tuple, even for single-argument functions
- `Call("exp", (VarRef("x"),))` - note the comma making it a tuple

**Example from `nonlinear_mix.gms`:**
```gams
trig_balance.. sin(x) + cos(y) =e= 0;
```

Parses to:
```python
EquationDef(
    name="trig_balance",
    expression=Binary("-",
        Binary("+",
            Call("sin", (VarRef("x"),)),
            Call("cos", (VarRef("y"),))
        ),
        Const(0.0)
    )
)
```

### Power Function vs Power Operator

**GAMS allows both syntaxes:**
- `x ** y` or `x ^ y` → `Binary("^", ...)` 
- `power(x, y)` → `Call("power", (...))`

**At parse time these are different**, but AD converts both to the same internal representation.

---

## Variable References

Variable references are represented as `VarRef(name, indices)` nodes.

**AST Definition:**
```python
@dataclass(frozen=True)
class VarRef(Expr):
    name: str
    indices: tuple[str, ...] = ()  # Empty tuple for scalar
```

### Variable Indexing Patterns

| GAMS Syntax | AST Representation | Indices | Notes |
|-------------|-------------------|---------|-------|
| `x` | `VarRef("x", ())` | `()` | Scalar variable - **empty tuple** |
| `x(i)` | `VarRef("x", ("i",))` | `("i",)` | Single index - **tuple with comma** |
| `x(i, j)` | `VarRef("x", ("i", "j"))` | `("i", "j")` | Two indices |
| `supply(i)` | `VarRef("supply", ("i",))` | `("i",)` | Named variable with index |

### Critical: Index Tuples

**⚠️ IMPORTANT:** Indices are ALWAYS tuples, even for scalar variables or single indices.

```python
# ✅ CORRECT:
VarRef("x", ())           # Scalar: empty tuple
VarRef("x", ("i",))       # Single index: tuple with comma
VarRef("x", ("i", "j"))   # Two indices: tuple

# ❌ WRONG:
VarRef("x")               # Missing indices argument
VarRef("x", None)         # None instead of tuple
VarRef("x", "i")          # String instead of tuple
VarRef("x", ["i"])        # List instead of tuple
```

### Symbolic vs Concrete Indices

**At parse time:** Indices are symbolic (set element variables)
```python
VarRef("x", ("i",))  # "i" is a symbolic index (iterates over set)
```

**After normalization/instantiation:** Indices become concrete
```python
VarRef("x", ("i1",))  # "i1" is a specific set member
VarRef("x", ("i2",))  # "i2" is another specific set member
```

**Example from `simple_nlp.gms`:**
```gams
balance(i).. x(i) =g= 0 ;
```

Parses to:
```python
EquationDef(
    name="balance",
    domain=("i",),  # Equation indexed over i
    expression=Binary("-",
        VarRef("x", ("i",)),  # Variable x(i) with symbolic index
        Const(0.0)
    )
)
```

---

## Parameter References

Parameter references are represented as `ParamRef(name, indices)` nodes.

**AST Definition:**
```python
@dataclass(frozen=True)
class ParamRef(Expr):
    name: str
    indices: tuple[str, ...] = ()  # Empty tuple for scalar
```

### Parameter Indexing Patterns

| GAMS Syntax | AST Representation | Indices | Notes |
|-------------|-------------------|---------|-------|
| `c` | `ParamRef("c", ())` | `()` | Scalar parameter |
| `a(i)` | `ParamRef("a", ("i",))` | `("i",)` | Indexed parameter |
| `demand(i)` | `ParamRef("demand", ("i",))` | `("i",)` | Named parameter |

**Same indexing rules as VarRef:**
- Always tuples
- Empty tuple for scalar
- Comma for single-element tuple

**Example from `simple_nlp.gms`:**
```gams
objective.. obj =e= sum(i, a(i) * x(i));
```

Inside the sum:
```python
Binary("*",
    ParamRef("a", ("i",)),  # Parameter a(i)
    VarRef("x", ("i",))     # Variable x(i)
)
```

---

## Constants

Numeric constants are represented as `Const(value)` nodes.

**AST Definition:**
```python
@dataclass(frozen=True)
class Const(Expr):
    value: float
```

### Constant Patterns

| GAMS Syntax | AST Representation | Notes |
|-------------|-------------------|-------|
| `3.14` | `Const(3.14)` | Floating point |
| `2` | `Const(2.0)` | Integer converted to float |
| `0` | `Const(0.0)` | Zero |
| `-5` | `Unary("-", Const(5.0))` | Negative (as unary) |

**Note:** All numeric values are stored as `float`, even if written as integers in GAMS.

---

## Aggregations (Sum)

Sum operations are represented as `Sum(index_sets, body)` nodes.

**AST Definition:**
```python
@dataclass(frozen=True)
class Sum(Expr):
    index_sets: tuple[str, ...]  # Set names to sum over
    body: Expr  # Expression to sum
```

### Sum Patterns

| GAMS Syntax | AST Representation | Index Sets | Notes |
|-------------|-------------------|------------|-------|
| `sum(i, x(i))` | `Sum(("I",), VarRef("x", ("i",)))` | `("I",)` | Single index |
| `sum((i,j), x(i,j))` | `Sum(("I","J"), VarRef("x", ("i","j")))` | `("I","J")` | Multiple indices |

**Example from `simple_nlp.gms`:**
```gams
objective.. obj =e= sum(i, a(i) * x(i));
```

Parses to:
```python
EquationDef(
    name="objective",
    expression=Binary("-",
        VarRef("obj"),
        Sum(
            ("I",),  # Set name (uppercase)
            Binary("*",
                ParamRef("a", ("i",)),  # Index variable (lowercase)
                VarRef("x", ("i",))
            )
        )
    )
)
```

**Important Notes:**
- `index_sets` contains the SET NAME (e.g., `"I"`)
- The index variable in the body uses lowercase (e.g., `"i"`)
- Set name mapping happens during parsing (lowercase `i` → uppercase `I`)

### Index-Aware Differentiation

**Differentiation Note (Sprint 2 Day 7.5):**

When differentiating `sum(i, f(i))` with respect to `x(i1)`:
- Only the term where `i=i1` contributes
- Result is NOT `sum(i, df(i)/dx(i1))` but rather `df(i1)/dx(i1)`

```python
# d/dx(i1) sum(i, x(i)^2)
# Result: 2*x(i1)  (only i1 term contributes)
# NOT: sum(i, 2*x(i))  (wrong - over-generalized)
```

---

## Equation Relations

Equations have relations that indicate the constraint type.

**Equation Definition:**
```python
@dataclass
class EquationDef:
    name: str
    domain: tuple[str, ...]
    relation: str  # "=e=", "=l=", "=g="
    expression: Expr  # Normalized to lhs - rhs
```

### Relation Types

| GAMS Relation | Relation String | Meaning | Normalized Form |
|---------------|----------------|---------|-----------------|
| `=e=` | `"=e="` | Equality | `lhs - rhs = 0` |
| `=l=` | `"=l="` | Less than or equal | `lhs - rhs ≤ 0` |
| `=g=` | `"=g="` | Greater than or equal | `-(lhs - rhs) ≤ 0` or `rhs - lhs ≤ 0` |

**Normalization (Sprint 1):**

All equations are normalized to standard form during processing:
- `=e=` relations: `lhs - rhs = 0`
- `=l=` relations: `lhs - rhs ≤ 0` 
- `=g=` relations: converted to `≤ 0` form

**Example:**
```gams
balance(i).. x(i) =g= 0;
```

Parses to:
```python
EquationDef(
    name="balance",
    domain=("i",),
    relation="=g=",
    expression=Binary("-", VarRef("x", ("i",)), Const(0.0))
)
```

After normalization, becomes: `-(x(i) - 0) ≤ 0` or stored appropriately in `inequalities`.

---

## Common Pitfalls

### Pitfall 1: Power Operator Confusion (Issue #25)

**❌ WRONG ASSUMPTION:**
```python
# Assuming x^2 parses to:
Call("power", (VarRef("x"), Const(2.0)))
```

**✅ ACTUAL PARSE OUTPUT:**
```python
# x^2 actually parses to:
Binary("^", VarRef("x"), Const(2.0))
```

**Why This Matters:**
- If you check for `Call("power", ...)` you'll miss `Binary("^", ...)`
- AD engine handles this by converting `Binary("^", ...)` to `Call("power", ...)` internally
- At parse time, they are DIFFERENT

**Lesson from Issue #25:**
Differentiation code had `_diff_power()` for `Call` but no handler for `Binary("^")`. Tests using `x^2` failed until `Binary("^")` support was added.

### Pitfall 2: Index Tuple Syntax

**❌ WRONG:**
```python
VarRef("x", "i")      # String instead of tuple
VarRef("x")           # Missing indices
VarRef("x", None)     # None instead of empty tuple
```

**✅ CORRECT:**
```python
VarRef("x", ())       # Scalar: empty tuple
VarRef("x", ("i",))   # Single index: tuple with comma
VarRef("x", ("i", "j"))  # Multiple indices
```

**Why This Matters:**
- Type checkers will catch missing tuples
- String indices will cause runtime errors
- Empty tuple vs None distinction is critical

### Pitfall 3: Bounds Location (Issue #24)

**Context:** This isn't about parser output per se, but about where bounds end up after normalization.

**❌ WRONG:**
```python
# Looking for bounds in equations dict
bound_def = model_ir.equations["x_lo"]  # KeyError!
```

**✅ CORRECT:**
```python
# Bounds are in normalized_bounds
bound_def = model_ir.normalized_bounds["x_lo"]
```

**Parser Output for Bounds:**
```gams
x.lo = 0;
x.up = 100;
```

These become entries in `normalized_bounds` dict with keys `"x_lo"` and `"x_up"`, NOT in the `equations` dict.

### Pitfall 4: Function Call Argument Tuples

**❌ WRONG:**
```python
Call("exp", VarRef("x"))  # Missing tuple around args
```

**✅ CORRECT:**
```python
Call("exp", (VarRef("x"),))  # Args are a tuple
```

**Why:** Function arguments are ALWAYS a tuple in the AST, even for single arguments.

### Pitfall 5: Set Names vs Index Variables

In sum expressions:
- `index_sets` uses SET NAMES (uppercase): `"I"`, `"J"`
- Body uses INDEX VARIABLES (lowercase): `"i"`, `"j"`

**Example:**
```python
Sum(
    ("I",),  # ← Set name (uppercase)
    VarRef("x", ("i",))  # ← Index variable (lowercase)
)
```

Don't confuse the two!

---

## Real Examples

### Example 1: Scalar NLP with Power and Trig (nonlinear_mix.gms)

**GAMS:**
```gams
poly_balance.. x ^ 2 + y ^ 2 =e= 4;
trig_balance.. sin(x) + cos(y) =e= 0;
```

**Parsed AST:**

**poly_balance:**
```python
EquationDef(
    name="poly_balance",
    domain=(),
    relation="=e=",
    expression=Binary("-",
        Binary("+",
            Binary("^", VarRef("x", ()), Const(2.0)),  # x^2 is Binary!
            Binary("^", VarRef("y", ()), Const(2.0))   # y^2 is Binary!
        ),
        Const(4.0)
    )
)
```

**trig_balance:**
```python
EquationDef(
    name="trig_balance",
    domain=(),
    relation="=e=",
    expression=Binary("-",
        Binary("+",
            Call("sin", (VarRef("x", ()),)),  # sin(x) is Call
            Call("cos", (VarRef("y", ()),))   # cos(y) is Call
        ),
        Const(0.0)
    )
)
```

### Example 2: Indexed Variables with Sum (simple_nlp.gms)

**GAMS:**
```gams
objective.. obj =e= sum(i, a(i) * x(i));
balance(i).. x(i) =g= 0;
```

**Parsed AST:**

**objective:**
```python
EquationDef(
    name="objective",
    domain=(),  # Not indexed
    relation="=e=",
    expression=Binary("-",
        VarRef("obj", ()),
        Sum(
            ("I",),  # Set name
            Binary("*",
                ParamRef("a", ("i",)),  # a(i)
                VarRef("x", ("i",))     # x(i)
            )
        )
    )
)
```

**balance:**
```python
EquationDef(
    name="balance",
    domain=("i",),  # Indexed over i
    relation="=g=",
    expression=Binary("-",
        VarRef("x", ("i",)),  # x(i) with symbolic index
        Const(0.0)
    )
)
```

### Example 3: Parameter Usage (indexed_balance.gms)

**GAMS:**
```gams
balance(i).. supply(i) =e= demand(i);
```

**Parsed AST:**
```python
EquationDef(
    name="balance",
    domain=("i",),
    relation="=e=",
    expression=Binary("-",
        VarRef("supply", ("i",)),
        ParamRef("demand", ("i",))  # Parameter reference
    )
)
```

---

## AST Node Type Summary

### Expression Types Hierarchy

```
Expr (base class)
├── Const(value: float)
├── VarRef(name: str, indices: tuple[str, ...])
├── ParamRef(name: str, indices: tuple[str, ...])
├── Binary(op: str, left: Expr, right: Expr)
├── Unary(op: str, child: Expr)
├── Call(func: str, args: tuple[Expr, ...])
└── Sum(index_sets: tuple[str, ...], body: Expr)
```

### Quick Type Check

To identify what you're dealing with:

```python
from src.ir.ast import *

if isinstance(expr, Binary):
    if expr.op == "^":
        # This is x^y power operation
        pass
elif isinstance(expr, Call):
    if expr.func == "power":
        # This is power(x,y) function call
        pass
elif isinstance(expr, VarRef):
    if expr.indices == ():
        # Scalar variable
        pass
    else:
        # Indexed variable
        pass
```

---

## Testing Parser Output

To verify parser output for any GAMS file:

```python
from src.ir.parser import parse_model_file

model = parse_model_file("examples/your_file.gms")

# Print all equations
for eq_name, eq_def in model.equations.items():
    print(f"\n{eq_name}:")
    print(f"  Domain: {eq_def.domain}")
    print(f"  Relation: {eq_def.relation}")
    print(f"  Expression: {eq_def.expression}")
```

For specific expression inspection:
```python
expr = model.equations["poly_balance"].expression
print(type(expr))  # Binary
print(expr.op)     # "-"
print(type(expr.left))  # Binary (the x^2 + y^2 part)
```

---

## See Also

- [System Architecture](../architecture/SYSTEM_ARCHITECTURE.md) - Complete system overview
- [Data Structures Reference](../architecture/DATA_STRUCTURES.md) - Detailed field documentation
- [Sprint 2 Retrospective](../planning/SPRINT_2/RETROSPECTIVE.md) - Issue #25 analysis
- Source: `src/ir/ast.py` - AST node definitions
- Source: `src/ir/parser.py` - Parser implementation

---

## Version History

- **2025-10-29**: Initial version (Sprint 3 Prep Task 2)
  - Complete operator reference
  - Issue #25 power operator documentation
  - Real examples from test files
  - Common pitfalls section

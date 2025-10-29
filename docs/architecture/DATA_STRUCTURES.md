# Data Structures Reference

**Purpose:** Document all key IR types, their fields, invariants, and contracts.

**Created:** 2025-10-29  
**Last Updated:** 2025-10-29  
**Related:** [System Architecture](SYSTEM_ARCHITECTURE.md)

---

## Table of Contents

1. [Sprint 1 Data Structures](#sprint-1-data-structures)
2. [Sprint 2 Data Structures](#sprint-2-data-structures)
3. [AST Expression Types](#ast-expression-types)
4. [Symbol Definitions](#symbol-definitions)
5. [Data Flow Examples](#data-flow-examples)

---

## Sprint 1 Data Structures

### ModelIR

**Location:** `src/ir/model_ir.py`

**Created By:** `normalize_model()` in `src/ir/normalize.py`

**Consumed By:**
- `compute_objective_gradient()` in `src/ad/gradient.py`
- `compute_constraint_jacobian()` in `src/ad/constraint_jacobian.py`
- `build_index_mapping()` in `src/ad/index_mapping.py`

**Purpose:** Central data structure containing the complete model representation after normalization.

**Fields:**

```python
@dataclass
class ModelIR:
    # Symbol tables
    sets: dict[str, SetDef] = field(default_factory=dict)
    aliases: dict[str, AliasDef] = field(default_factory=dict)
    params: dict[str, ParameterDef] = field(default_factory=dict)
    variables: dict[str, VariableDef] = field(default_factory=dict)
    
    # Equations
    equations: dict[str, EquationDef] = field(default_factory=dict)
    
    # Solve information
    declared_model: str | None = None
    model_equations: list[str] = field(default_factory=list)
    model_uses_all: bool = False
    model_name: str | None = None
    objective: ObjectiveIR | None = None
    
    # Normalized constraint categorization
    equalities: list[str] = field(default_factory=list)
    inequalities: list[str] = field(default_factory=list)
    normalized_bounds: dict[str, NormalizedEquation] = field(default_factory=dict)
```

**Critical Invariants:**

1. **Bounds Storage (Issue #24):**
   - If `name` in `inequalities`, then either:
     - `name` in `equations` (regular inequality constraint), OR
     - `name` in `normalized_bounds` (bound constraint)
   - Bound names follow pattern: `"{var}_lo"` or `"{var}_up"`
   - Bounds are NEVER in `equations` dict
   - Bound names ARE in `inequalities` list

2. **Equation Categorization:**
   - Every equation name is in either `equalities` OR `inequalities`
   - No equation appears in both lists
   - Equalities correspond to `=e=` relations
   - Inequalities correspond to `=l=` or `=g=` relations (normalized to ≤ 0)

3. **Objective:**
   - `objective` is None before Solve statement is parsed
   - After parsing, `objective.sense` is either MIN or MAX
   - `objective.objvar` is the objective variable name
   - `objective.expr` may be None (defined by equation) or Expr (explicit)

**Example:**

```python
# For model with:
# - Variables: x, y(i) where i in {i1, i2}
# - Constraints: c1: x + sum(i, y(i)) =e= 10
#                c2: x - 5 =l= 0
# - Bounds: x.lo = 0, x.up = 100

model_ir = ModelIR(
    variables={
        "x": VariableDef(name="x", domain=(), ...),
        "y": VariableDef(name="y", domain=("I",), ...),
    },
    equations={
        "c1": EquationDef(name="c1", relation="=e=", ...),
        "c2": EquationDef(name="c2", relation="=l=", ...),
    },
    equalities=["c1"],
    inequalities=["c2", "x_lo", "x_up"],  # Includes bounds!
    normalized_bounds={
        "x_lo": NormalizedEquation(...),  # x >= 0
        "x_up": NormalizedEquation(...),  # x <= 100
    },
)
```

---

### ObjectiveIR

**Location:** `src/ir/model_ir.py`

**Purpose:** Represents the objective function from the Solve statement.

**Fields:**

```python
@dataclass
class ObjectiveIR:
    sense: ObjSense  # MIN or MAX
    objvar: str  # Name of objective variable/symbol
    expr: Expr | None = None  # Explicit expression (if given)
```

**Usage Patterns:**

```python
# Case 1: Explicit expression
# GAMS: Solve mymodel using NLP minimizing (x^2 + y^2);
objective = ObjectiveIR(
    sense=ObjSense.MIN,
    objvar="anonymous_obj",
    expr=Binary("+", Binary("^", VarRef("x"), Const(2)), ...)
)

# Case 2: Variable defined by equation
# GAMS: obj_eq.. obj =e= x^2 + y^2;
#       Solve mymodel using NLP minimizing obj;
objective = ObjectiveIR(
    sense=ObjSense.MIN,
    objvar="obj",
    expr=None  # Must find defining equation
)
```

---

### EquationDef

**Location:** `src/ir/symbols.py`

**Purpose:** Defines a single equation (constraint or objective definition).

**Fields:**

```python
@dataclass
class EquationDef:
    name: str
    domain: tuple[str, ...]  # Index set names
    relation: str  # "=e=", "=l=", "=g="
    expression: Expr  # Normalized to lhs - rhs form
```

**Normalization:**

Original GAMS equation:
```gams
con(i).. x(i) + y(i) =l= bound(i);
```

After normalization:
```python
EquationDef(
    name="con",
    domain=("i",),
    relation="=l=",
    expression=Binary(
        "-",
        Binary("+", VarRef("x", ("i",)), VarRef("y", ("i",))),
        ParamRef("bound", ("i",))
    )
)
```

Interpretation: `(x(i) + y(i)) - bound(i) ≤ 0`

---

### VariableDef

**Location:** `src/ir/symbols.py`

**Purpose:** Defines a decision variable.

**Fields:**

```python
@dataclass
class VariableDef:
    name: str
    domain: tuple[str, ...]  # Index set names
    var_type: str  # "free", "positive", "negative", "binary", "integer"
    # Bounds stored separately in normalized_bounds during normalization
```

**Examples:**

```python
# Scalar variable
VariableDef(name="x", domain=(), var_type="free")

# Indexed variable
VariableDef(name="y", domain=("I", "J"), var_type="positive")
```

---

### SetDef

**Location:** `src/ir/symbols.py`

**Purpose:** Defines an index set.

**Fields:**

```python
@dataclass
class SetDef:
    name: str
    elements: list[str] | None  # Concrete elements or None if abstract
```

**Examples:**

```python
# Concrete set
SetDef(name="I", elements=["i1", "i2", "i3"])

# Abstract set (size unknown at parse time)
SetDef(name="J", elements=None)
```

---

## Sprint 2 Data Structures

### IndexMapping

**Location:** `src/ad/index_mapping.py`

**Created By:** `build_index_mapping()` in `src/ad/index_mapping.py`

**Consumed By:**
- `compute_objective_gradient()` in `src/ad/gradient.py`
- `compute_constraint_jacobian()` in `src/ad/constraint_jacobian.py`
- `GradientVector` and `JacobianStructure` for lookups

**Purpose:** Maps variable/equation instances to matrix column/row indices.

**Fields:**

```python
@dataclass
class IndexMapping:
    # Variable instances (columns)
    instances: list[tuple[str, tuple[str, ...]]]  # [(var_name, indices), ...]
    var_to_col: dict[tuple[str, tuple[str, ...]], int]
    col_to_var: dict[int, tuple[str, tuple[str, ...]]]
    
    # Equation instances (rows)
    eq_instances: list[tuple[str, tuple[str, ...]]]  # [(eq_name, indices), ...]
    eq_to_row: dict[tuple[str, tuple[str, ...]], int]
    row_to_eq: dict[int, tuple[str, tuple[str, ...]]]
```

**Example:**

```python
# For variables: x (scalar), y(i) where i in {i1, i2}
mapping = IndexMapping(
    instances=[
        ("x", ()),
        ("y", ("i1",)),
        ("y", ("i2",)),
    ],
    var_to_col={
        ("x", ()): 0,
        ("y", ("i1",)): 1,
        ("y", ("i2",)): 2,
    },
    col_to_var={
        0: ("x", ()),
        1: ("y", ("i1",)),
        2: ("y", ("i2",)),
    },
    # ... similar for equations
)
```

**Usage:**

```python
# Get column ID for y(i1)
col_id = mapping.var_to_col[("y", ("i1",))]  # Returns 1

# Get variable name for column 2
var_name, indices = mapping.col_to_var[2]  # Returns ("y", ("i2",))
```

---

### GradientVector

**Location:** `src/ad/jacobian.py`

**Created By:** `compute_objective_gradient()` in `src/ad/gradient.py`

**Consumed By:** KKT assembler (Sprint 3)

**Purpose:** Stores sparse gradient ∇f of objective function.

**Fields:**

```python
@dataclass
class GradientVector:
    num_cols: int  # ✅ Total number of variables
    values: dict[int, Expr]  # col_id → derivative expression (AST)
    mapping: IndexMapping  # For variable instance lookups
```

**API Contract (Issue #22):**

```python
# ✅ CORRECT
gradient.num_cols  # Number of variable columns

# ❌ WRONG - Does not exist!
gradient.mapping.num_vars
```

**Example:**

```python
# For objective f = x^2 + sum(i, y(i)^2)
# Variables: x, y(i1), y(i2)

gradient = GradientVector(
    num_cols=3,
    values={
        0: Binary("*", Const(2.0), VarRef("x", ())),  # ∂f/∂x = 2*x
        1: Binary("*", Const(2.0), VarRef("y", ("i1",))),  # ∂f/∂y(i1) = 2*y(i1)
        2: Binary("*", Const(2.0), VarRef("y", ("i2",))),  # ∂f/∂y(i2) = 2*y(i2)
    },
    mapping=IndexMapping(...)
)
```

**Sparsity:**

Only nonzero derivatives are stored in `values` dict. If `col_id` not in `values`, derivative is implicitly zero.

---

### JacobianStructure

**Location:** `src/ad/jacobian.py`

**Created By:** `compute_constraint_jacobian()` in `src/ad/constraint_jacobian.py`

**Consumed By:** KKT assembler (Sprint 3)

**Purpose:** Stores sparse Jacobian matrix J where J[i,j] = ∂constraint_i/∂x_j.

**Fields:**

```python
@dataclass
class JacobianStructure:
    num_rows: int  # Number of constraints
    num_cols: int  # Number of variables
    entries: dict[int, dict[int, Expr]]  # row → col → derivative AST
    index_mapping: IndexMapping | None  # For lookups
```

**Access Methods:**

```python
class JacobianStructure:
    def get_derivative(self, row_id: int, col_id: int) -> Expr | None:
        """Get derivative at (row, col). Returns None if zero."""
        
    def get_derivative_by_names(
        self, eq_name: str, eq_indices: tuple,
        var_name: str, var_indices: tuple
    ) -> Expr | None:
        """Get derivative using names (requires index_mapping)."""
        
    def get_row(self, row_id: int) -> dict[int, Expr]:
        """Get all nonzero entries in a row."""
        
    def get_col(self, col_id: int) -> dict[int, Expr]:
        """Get all nonzero entries in a column."""
```

**Example:**

```python
# For constraints:
# h1: x + y(i1) = 0
# h2: x + y(i2) = 0
# Variables: x, y(i1), y(i2)

J_h = JacobianStructure(
    num_rows=2,
    num_cols=3,
    entries={
        0: {  # h1 row
            0: Const(1.0),  # ∂h1/∂x = 1
            1: Const(1.0),  # ∂h1/∂y(i1) = 1
            # col 2 not present → ∂h1/∂y(i2) = 0
        },
        1: {  # h2 row
            0: Const(1.0),  # ∂h2/∂x = 1
            2: Const(1.0),  # ∂h2/∂y(i2) = 1
            # col 1 not present → ∂h2/∂y(i1) = 0
        },
    },
    index_mapping=IndexMapping(...)
)
```

**Sparsity Pattern:**

```
     x   y(i1) y(i2)
h1 [ 1    1     0   ]
h2 [ 1    0     1   ]
```

Only nonzero entries are stored.

---

## AST Expression Types

**Location:** `src/ir/ast.py`

**Purpose:** Abstract syntax tree nodes for mathematical expressions.

### Base Class

```python
class Expr:
    """Base class for all expression nodes."""
    
    def children(self) -> Iterable[Expr]:
        """Return child expressions for tree traversal."""
        return []
    
    def pretty(self) -> str:
        """Debug-friendly rendering."""
        return repr(self)
```

### Const

```python
@dataclass(frozen=True)
class Const(Expr):
    value: float
```

**Examples:**

```python
Const(3.14)  # Numeric constant
Const(0.0)   # Zero
Const(1.0)   # Derivative of x w.r.t. x
```

### VarRef

```python
@dataclass(frozen=True)
class VarRef(Expr):
    """Reference to a variable."""
    name: str
    indices: tuple[str, ...] = ()  # Empty tuple for scalar
```

**Examples:**

```python
VarRef("x", ())  # Scalar variable x
VarRef("y", ("i",))  # Indexed variable y(i) - symbolic
VarRef("y", ("i1",))  # Indexed variable y(i1) - concrete
VarRef("z", ("i", "j"))  # Two-dimensional z(i,j)
```

**Important:** 
- Scalar variables have empty tuple `()`
- Single index is tuple `("i",)` not string `"i"`
- See Issue #25 for indexing pitfalls

### ParamRef

```python
@dataclass(frozen=True)
class ParamRef(Expr):
    """Reference to a parameter."""
    name: str
    indices: tuple[str, ...] = ()
```

**Examples:**

```python
ParamRef("c", ())  # Scalar parameter c
ParamRef("bound", ("i",))  # Indexed parameter bound(i)
```

### Binary

```python
@dataclass(frozen=True)
class Binary(Expr):
    op: str  # Operator: "+", "-", "*", "/", "^"
    left: Expr
    right: Expr
    
    def children(self) -> Iterable[Expr]:
        yield self.left
        yield self.right
```

**Operators:**

| Operator | Description | Example |
|----------|-------------|---------|
| `"+"` | Addition | `Binary("+", VarRef("x"), Const(5))` → x + 5 |
| `"-"` | Subtraction | `Binary("-", VarRef("x"), VarRef("y"))` → x - y |
| `"*"` | Multiplication | `Binary("*", Const(2), VarRef("x"))` → 2*x |
| `"/"` | Division | `Binary("/", VarRef("x"), VarRef("y"))` → x/y |
| `"^"` | Power | `Binary("^", VarRef("x"), Const(2))` → x^2 |

**Issue #25 Note:**

Power operator `^` is represented as `Binary("^", ...)`, NOT as `Call("power", ...)`.
The AD engine converts `Binary("^", ...)` to `Call("power", ...)` internally.

### Unary

```python
@dataclass(frozen=True)
class Unary(Expr):
    op: str  # Operator: "+", "-"
    child: Expr
    
    def children(self) -> Iterable[Expr]:
        yield self.child
```

**Examples:**

```python
Unary("-", VarRef("x"))  # -x (negation)
Unary("+", VarRef("x"))  # +x (explicit positive)
```

### Call

```python
@dataclass(frozen=True)
class Call(Expr):
    func: str  # Function name
    args: tuple[Expr, ...]  # Arguments
    
    def children(self) -> Iterable[Expr]:
        return self.args
```

**Functions:**

| Function | Description | Example |
|----------|-------------|---------|
| `"exp"` | Exponential | `Call("exp", (VarRef("x"),))` → exp(x) |
| `"log"` | Natural log | `Call("log", (VarRef("x"),))` → log(x) |
| `"sqrt"` | Square root | `Call("sqrt", (VarRef("x"),))` → sqrt(x) |
| `"sin"` | Sine | `Call("sin", (VarRef("x"),))` → sin(x) |
| `"cos"` | Cosine | `Call("cos", (VarRef("x"),))` → cos(x) |
| `"power"` | Power (internal) | `Call("power", (VarRef("x"), Const(2)))` → x^2 |

**Note:** `power` is primarily used internally after converting from `Binary("^", ...)`.

### Sum

```python
@dataclass(frozen=True)
class Sum(Expr):
    """Summation over index sets."""
    index_sets: tuple[str, ...]  # Set names
    body: Expr  # Expression to sum
    
    def children(self) -> Iterable[Expr]:
        yield self.body
```

**Examples:**

```python
# sum(i, x(i))
Sum(
    index_sets=("I",),
    body=VarRef("x", ("i",))
)

# sum((i,j), x(i,j) * y(i,j))
Sum(
    index_sets=("I", "J"),
    body=Binary("*", VarRef("x", ("i", "j")), VarRef("y", ("i", "j")))
)
```

**Differentiation:**

```python
# d/dx(i1) sum(i, f(i))
# Only the i=i1 term contributes (index-aware, Sprint 2 Day 7.5)
```

---

## Symbol Definitions

### SetDef

**Location:** `src/ir/symbols.py`

```python
@dataclass
class SetDef:
    name: str
    elements: list[str] | None  # Concrete elements or None
```

### AliasDef

**Location:** `src/ir/symbols.py`

```python
@dataclass
class AliasDef:
    name: str
    parent_set: str  # Name of set this is an alias for
```

### ParameterDef

**Location:** `src/ir/symbols.py`

```python
@dataclass
class ParameterDef:
    name: str
    domain: tuple[str, ...]  # Index set names
    # Values typically loaded from data, not stored in IR
```

---

## Data Flow Examples

### Example 1: Scalar NLP

**GAMS Input:**

```gams
Variables x, y, obj;
Equations obj_eq, con1;

obj_eq.. obj =e= x^2 + y^2;
con1.. x + y =l= 10;

x.lo = 0; x.up = 100;
y.lo = 0;

Solve mymodel using NLP minimizing obj;
```

**ModelIR After Normalization:**

```python
ModelIR(
    variables={
        "x": VariableDef("x", (), "free"),
        "y": VariableDef("y", (), "free"),
        "obj": VariableDef("obj", (), "free"),
    },
    equations={
        "obj_eq": EquationDef(
            name="obj_eq",
            domain=(),
            relation="=e=",
            expression=Binary("-",
                VarRef("obj"),
                Binary("+",
                    Binary("^", VarRef("x"), Const(2)),
                    Binary("^", VarRef("y"), Const(2))
                )
            )
        ),
        "con1": EquationDef(
            name="con1",
            domain=(),
            relation="=l=",
            expression=Binary("-",
                Binary("+", VarRef("x"), VarRef("y")),
                Const(10)
            )
        ),
    },
    equalities=["obj_eq"],
    inequalities=["con1", "x_lo", "x_up", "y_lo"],
    normalized_bounds={
        "x_lo": NormalizedEquation(...),  # x >= 0
        "x_up": NormalizedEquation(...),  # x <= 100
        "y_lo": NormalizedEquation(...),  # y >= 0
    },
    objective=ObjectiveIR(
        sense=ObjSense.MIN,
        objvar="obj",
        expr=None  # Defined by obj_eq
    ),
)
```

**IndexMapping:**

```python
IndexMapping(
    instances=[
        ("x", ()),
        ("y", ()),
        ("obj", ()),
    ],
    var_to_col={
        ("x", ()): 0,
        ("y", ()): 1,
        ("obj", ()): 2,
    },
    eq_instances=[
        ("obj_eq", ()),
        ("con1", ()),
        ("x_lo", ()),
        ("x_up", ()),
        ("y_lo", ()),
    ],
    eq_to_row={
        ("obj_eq", ()): 0,
        ("con1", ()): 1,
        ("x_lo", ()): 2,
        ("x_up", ()): 3,
        ("y_lo", ()): 4,
    },
)
```

**GradientVector:**

```python
# Objective: obj = x^2 + y^2
# ∇f = [∂obj/∂x, ∂obj/∂y, ∂obj/∂obj]

GradientVector(
    num_cols=3,
    values={
        0: Binary("*", Const(2.0), VarRef("x")),  # ∂f/∂x = 2*x
        1: Binary("*", Const(2.0), VarRef("y")),  # ∂f/∂y = 2*y
        2: Const(-1.0),  # ∂f/∂obj = -1 (from obj - (x^2+y^2) = 0)
    },
    mapping=IndexMapping(...)
)
```

**JacobianStructure (J_h for equalities):**

```python
# Equality: obj - (x^2 + y^2) = 0

J_h = JacobianStructure(
    num_rows=1,
    num_cols=3,
    entries={
        0: {  # obj_eq row
            0: Binary("*", Const(-2.0), VarRef("x")),  # ∂h/∂x = -2*x
            1: Binary("*", Const(-2.0), VarRef("y")),  # ∂h/∂y = -2*y
            2: Const(1.0),  # ∂h/∂obj = 1
        },
    },
)
```

**JacobianStructure (J_g for inequalities):**

```python
# Inequalities:
# con1: x + y - 10 <= 0
# x_lo: -(x - 0) <= 0  →  -x <= 0
# x_up: x - 100 <= 0
# y_lo: -(y - 0) <= 0  →  -y <= 0

J_g = JacobianStructure(
    num_rows=4,
    num_cols=3,
    entries={
        0: {0: Const(1.0), 1: Const(1.0)},  # ∂con1/∂x=1, ∂con1/∂y=1
        1: {0: Const(-1.0)},  # ∂(x_lo)/∂x = -1
        2: {0: Const(1.0)},   # ∂(x_up)/∂x = 1
        3: {1: Const(-1.0)},  # ∂(y_lo)/∂y = -1
    },
)
```

---

### Example 2: Indexed Variables

**GAMS Input:**

```gams
Set I /i1, i2/;
Parameter bound(i) /i1 5, i2 10/;
Variables x(i), obj;
Equations obj_eq, con(i);

obj_eq.. obj =e= sum(i, x(i)^2);
con(i).. x(i) =l= bound(i);

Solve mymodel using NLP minimizing obj;
```

**ModelIR After Normalization:**

```python
ModelIR(
    sets={
        "I": SetDef("I", ["i1", "i2"]),
    },
    variables={
        "x": VariableDef("x", ("I",), "free"),
        "obj": VariableDef("obj", (), "free"),
    },
    equations={
        "obj_eq": EquationDef(
            name="obj_eq",
            domain=(),
            relation="=e=",
            expression=Binary("-",
                VarRef("obj"),
                Sum(("I",), Binary("^", VarRef("x", ("i",)), Const(2)))
            )
        ),
        "con": EquationDef(
            name="con",
            domain=("I",),
            relation="=l=",
            expression=Binary("-",
                VarRef("x", ("i",)),
                ParamRef("bound", ("i",))
            )
        ),
    },
    equalities=["obj_eq"],
    inequalities=["con"],  # 2 instances: con(i1), con(i2)
    params={
        "bound": ParameterDef("bound", ("I",)),
    },
)
```

**IndexMapping:**

```python
IndexMapping(
    instances=[
        ("x", ("i1",)),
        ("x", ("i2",)),
        ("obj", ()),
    ],
    var_to_col={
        ("x", ("i1",)): 0,
        ("x", ("i2",)): 1,
        ("obj", ()): 2,
    },
    eq_instances=[
        ("obj_eq", ()),
        ("con", ("i1",)),
        ("con", ("i2",)),
    ],
    eq_to_row={
        ("obj_eq", ()): 0,
        ("con", ("i1",)): 1,
        ("con", ("i2",)): 2,
    },
)
```

**GradientVector (Index-Aware):**

```python
# Objective: obj = sum(i, x(i)^2) = x(i1)^2 + x(i2)^2
# With index-aware differentiation:
# ∂f/∂x(i1) = 2*x(i1)  (only i1 term contributes)
# ∂f/∂x(i2) = 2*x(i2)  (only i2 term contributes)
# ∂f/∂obj = -1

GradientVector(
    num_cols=3,
    values={
        0: Binary("*", Const(2.0), VarRef("x", ("i1",))),  # ∂f/∂x(i1)
        1: Binary("*", Const(2.0), VarRef("x", ("i2",))),  # ∂f/∂x(i2)
        2: Const(-1.0),  # ∂f/∂obj
    },
)
```

**Without index-aware differentiation (incorrect):**

```python
# WRONG: Old behavior before Sprint 2 Day 7.5
GradientVector(
    values={
        0: Sum(("I",), Binary("*", Const(2.0), VarRef("x", ("i",)))),  # Wrong!
        1: Sum(("I",), Binary("*", Const(2.0), VarRef("x", ("i",)))),  # Wrong!
        # Same derivative for both instances - incorrect!
    },
)
```

---

## Invariants Summary

### ModelIR Invariants

1. **Bounds separated from equations**
   - Bounds in `normalized_bounds`, not `equations`
   - Bound names in `inequalities` list
   - Bound names match pattern: `{var}_lo`, `{var}_up`

2. **Constraint categorization complete**
   - Every equation in either `equalities` or `inequalities`
   - No equation in both lists
   - Equalities ↔ =e= relations
   - Inequalities ↔ =l=/=g= relations (normalized)

3. **Objective consistency**
   - If `objective.expr` is None, defining equation must exist
   - If `objective.expr` is not None, it's the objective expression

### IndexMapping Invariants

1. **Bidirectional consistency**
   - `var_to_col[v] = c` ↔ `col_to_var[c] = v`
   - `eq_to_row[e] = r` ↔ `row_to_eq[r] = e`

2. **Instance enumeration complete**
   - Every variable instance in `instances`
   - Every equation instance in `eq_instances`
   - Ordering is deterministic (sorted)

### Jacobian Invariants

1. **Dimension consistency**
   - `num_cols` = number of variable instances
   - `num_rows` = number of constraint instances
   - All row IDs in range [0, num_rows)
   - All col IDs in range [0, num_cols)

2. **Sparsity**
   - Only nonzero entries stored
   - Missing entry implies zero derivative

---

## See Also

- [System Architecture](SYSTEM_ARCHITECTURE.md) - Complete data flow diagram
- [Sprint 2 Retrospective](../planning/SPRINT_2/RETROSPECTIVE.md) - Lessons learned
- [Sprint 3 Prep Plan](../planning/SPRINT_3/PREP_PLAN.md) - Process improvements

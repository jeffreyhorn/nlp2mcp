# Data Structures Reference

**Purpose:** Document all key IR types, their fields, invariants, and contracts.

**Created:** 2025-10-29  
**Last Updated:** 2025-10-30  
**Related:** [System Architecture](SYSTEM_ARCHITECTURE.md)

---

## Table of Contents

1. [Sprint 1 Data Structures](#sprint-1-data-structures)
2. [Sprint 2 Data Structures](#sprint-2-data-structures)
3. [Sprint 3 Data Structures](#sprint-3-data-structures)
4. [AST Expression Types](#ast-expression-types)
5. [Symbol Definitions](#symbol-definitions)
6. [Data Flow Examples](#data-flow-examples)

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
    entries: dict[int, Expr]  # col_id → derivative expression (AST)
    index_mapping: IndexMapping  # For variable instance lookups
    
    # Access methods
    def get_derivative(self, col_id: int) -> Expr | None:
        """Get derivative at col_id. Returns None if zero."""
    
    def get_derivative_by_name(self, var_name: str, indices: tuple) -> Expr | None:
        """Get derivative using variable name and indices."""
```

**API Contract (Validated by tests/integration/test_api_contracts.py):**

```python
# ✅ CORRECT - All these exist
gradient.num_cols  # Number of variable columns
gradient.entries  # Sparse derivatives dict (col_id → Expr)
gradient.index_mapping  # IndexMapping with num_vars, var_to_col, col_to_var

# Consistency guarantee (Issue #22 regression test)
assert gradient.num_cols == gradient.index_mapping.num_vars
```

**Example:**

```python
# For objective f = x^2 + sum(i, y(i)^2)
# Variables: x, y(i1), y(i2)

gradient = GradientVector(
    num_cols=3,
    entries={
        0: Binary("*", Const(2.0), VarRef("x", ())),  # ∂f/∂x = 2*x
        1: Binary("*", Const(2.0), VarRef("y", ("i1",))),  # ∂f/∂y(i1) = 2*y(i1)
        2: Binary("*", Const(2.0), VarRef("y", ("i2",))),  # ∂f/∂y(i2) = 2*y(i2)
    },
    index_mapping=IndexMapping(...)
)
```

**Sparsity:**

Only nonzero derivatives are stored in `entries` dict. If `col_id` not in `entries`, derivative is implicitly zero.

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

## Sprint 3 Data Structures

### KKTSystem

**Location:** `src/kkt/kkt_system.py`

**Created By:** `assemble_kkt_system()` in `src/kkt/kkt_system.py`

**Consumed By:** `write_kkt_gams()` in `src/codegen/kkt_writer.py`

**Purpose:** Complete representation of the Karush-Kuhn-Tucker (KKT) optimality conditions for an NLP problem. The KKT system transforms the original constrained optimization problem into a system of equations and complementarity conditions that characterize optimal solutions.

**Fields:**

```python
@dataclass
class KKTSystem:
    # Original model data
    model_ir: ModelIR
    gradient: GradientVector  # ∇f
    J_eq: JacobianStructure   # Jacobian of equality constraints
    J_ineq: JacobianStructure # Jacobian of inequality constraints
    
    # Lagrange multipliers for each constraint type
    multipliers_eq: dict[str, MultiplierDef] = field(default_factory=dict)
    multipliers_ineq: dict[str, MultiplierDef] = field(default_factory=dict)
    multipliers_bounds_lo: dict[tuple, MultiplierDef] = field(default_factory=dict)
    multipliers_bounds_up: dict[tuple, MultiplierDef] = field(default_factory=dict)
    
    # KKT conditions
    stationarity: dict[str, EquationDef] = field(default_factory=dict)
    complementarity_ineq: dict[str, ComplementarityPair] = field(default_factory=dict)
    complementarity_bounds_lo: dict[tuple, ComplementarityPair] = field(default_factory=dict)
    complementarity_bounds_up: dict[tuple, ComplementarityPair] = field(default_factory=dict)
    
    # Exclusions and diagnostics
    skipped_infinite_bounds: list[tuple[str, tuple, str]] = field(default_factory=list)
    duplicate_bounds_excluded: list[str] = field(default_factory=list)
```

**KKT System Components:**

1. **Stationarity Equations** (`stationarity`):
   - One equation per primal variable x(i)
   - Form: `∇f + J_eq^T·ν + J_ineq^T·λ + bound_multipliers = 0`
   - Keys: variable instance strings like `"x.i1"` or `"y"` for scalar
   - Stored as `EquationDef` objects

2. **Multiplier Definitions**:
   - `multipliers_eq`: For equality constraints (ν)
   - `multipliers_ineq`: For inequality constraints (λ) 
   - `multipliers_bounds_lo`: For lower bounds (π_lo)
   - `multipliers_bounds_up`: For upper bounds (π_up)

3. **Complementarity Conditions**:
   - `complementarity_ineq`: For inequalities: `g(x) ⊥ λ` (either g=0 or λ=0)
   - `complementarity_bounds_lo`: For lower bounds: `(x - x_lo) ⊥ π_lo`
   - `complementarity_bounds_up`: For upper bounds: `(x_up - x) ⊥ π_up`
   - Stored as `ComplementarityPair` objects

4. **Diagnostics**:
   - `skipped_infinite_bounds`: Bounds with ±INF values (no multiplier needed)
   - `duplicate_bounds_excluded`: Variables appearing in both bounds and constraints

**Example:**

```python
# For problem: minimize x^2 + y^2
#              subject to: x + y = 1
#                         x >= 0

kkt_system = KKTSystem(
    model_ir=ModelIR(...),
    gradient=GradientVector(...),  # [2*x, 2*y]
    J_eq=JacobianStructure(...),   # [[1, 1]] for x+y=1
    J_ineq=JacobianStructure(...), # [[-1, 0]] for -x<=0
    
    multipliers_eq={
        "con_eq": MultiplierDef(
            name="nu_con_eq",
            domain=(),
            kind="eq",
            associated_constraint="con_eq"
        ),
    },
    
    multipliers_bounds_lo={
        ("x", ()): MultiplierDef(
            name="pi_lo_x",
            domain=(),
            kind="bound_lo",
            associated_constraint="x_lo"
        ),
    },
    
    stationarity={
        "x": EquationDef(  # ∇_x L = 2*x + nu_con_eq - pi_lo_x = 0
            name="stat_x",
            domain=(),
            relation="=e=",
            expression=...
        ),
        "y": EquationDef(  # ∇_y L = 2*y + nu_con_eq = 0
            name="stat_y",
            domain=(),
            relation="=e=",
            expression=...
        ),
    },
    
    complementarity_bounds_lo={
        ("x", ()): ComplementarityPair(
            equation=EquationDef(...),  # x >= 0
            variable="pi_lo_x",
            variable_indices=()
        ),
    },
)
```

---

### MultiplierDef

**Location:** `src/kkt/kkt_system.py`

**Purpose:** Defines a Lagrange multiplier variable for a constraint in the KKT system.

**Fields:**

```python
@dataclass
class MultiplierDef:
    name: str  # Multiplier variable name (e.g., "nu_con1", "lambda_ineq_i1", "pi_lo_x")
    domain: tuple[str, ...] = ()  # Index sets (empty for scalar)
    kind: Literal["eq", "ineq", "bound_lo", "bound_up"] = "eq"
    associated_constraint: str = ""  # Name of the constraint this multiplies
```

**Naming Conventions:**

- Equality multipliers (ν): `nu_{constraint_name}`
- Inequality multipliers (λ): `lambda_{constraint_name}`
- Lower bound multipliers (π_lo): `pi_lo_{var_name}`
- Upper bound multipliers (π_up): `pi_up_{var_name}`

**Examples:**

```python
# Equality constraint multiplier
MultiplierDef(
    name="nu_obj_eq",
    domain=(),
    kind="eq",
    associated_constraint="obj_eq"
)

# Indexed inequality constraint multiplier
MultiplierDef(
    name="lambda_con",
    domain=("I",),
    kind="ineq",
    associated_constraint="con"
)

# Lower bound multiplier
MultiplierDef(
    name="pi_lo_x",
    domain=(),
    kind="bound_lo",
    associated_constraint="x_lo"
)
```

---

### ComplementarityPair

**Location:** `src/kkt/kkt_system.py`

**Purpose:** Represents a complementarity condition `F(x) ⊥ variable` where either F=0 or variable=0 (or both) at optimality.

**Fields:**

```python
@dataclass
class ComplementarityPair:
    equation: EquationDef  # The constraint/bound equation F(x)
    variable: str          # The multiplier variable name
    variable_indices: tuple[str, ...] = ()  # Indices if variable is indexed
```

**Complementarity Types:**

1. **Inequality complementarity**: `g(x) ≤ 0 ⊥ λ ≥ 0`
   - Either constraint is slack (g < 0, λ = 0) or binding (g = 0, λ > 0)

2. **Lower bound complementarity**: `x - x_lo ≥ 0 ⊥ π_lo ≥ 0`
   - Either bound is slack (x > x_lo, π_lo = 0) or binding (x = x_lo, π_lo > 0)

3. **Upper bound complementarity**: `x_up - x ≥ 0 ⊥ π_up ≥ 0`
   - Either bound is slack (x < x_up, π_up = 0) or binding (x = x_up, π_up > 0)

**Examples:**

```python
# Inequality complementarity: g(x) ≤ 0 ⊥ λ ≥ 0
ComplementarityPair(
    equation=EquationDef(
        name="con1_compl",
        domain=(),
        relation="=l=",
        expression=Binary("-", VarRef("x"), Const(10))  # x - 10 ≤ 0
    ),
    variable="lambda_con1",
    variable_indices=()
)

# Lower bound complementarity: x(i) ≥ 0 ⊥ π_lo_x(i) ≥ 0
ComplementarityPair(
    equation=EquationDef(
        name="x_lo_i1_compl",
        domain=(),
        relation="=g=",
        expression=VarRef("x", ("i1",))  # x(i1) ≥ 0
    ),
    variable="pi_lo_x",
    variable_indices=("i1",)
)
```

**GAMS MCP Format:**

These pairs are written to GAMS as:
```gams
equation_name .. expression =N= 0;
Model mymodel_mcp / equation_name.variable_name /;
```

---

### BoundDef

**Location:** `src/kkt/partition.py`

**Purpose:** Represents a variable bound during constraint partitioning.

**Fields:**

```python
@dataclass
class BoundDef:
    kind: str  # 'lo' (lower), 'up' (upper), 'fx' (fixed)
    value: float  # Bound value
    domain: tuple[str, ...] = ()  # Index sets (empty for scalar)
```

**Examples:**

```python
# Scalar lower bound: x.lo = 0
BoundDef(kind='lo', value=0.0, domain=())

# Indexed upper bound: y(i).up = 100
BoundDef(kind='up', value=100.0, domain=('I',))

# Fixed bound: z.fx = 5
BoundDef(kind='fx', value=5.0, domain=())
```

**Usage in Partitioning:**

Fixed bounds (`kind='fx'`) generate both lower and upper bound constraints, while `'lo'` and `'up'` generate single-sided constraints.

---

### PartitionResult

**Location:** `src/kkt/partition.py`

**Created By:** `partition_constraints()` in `src/kkt/partition.py`

**Consumed By:** `assemble_kkt_system()` in `src/kkt/kkt_system.py`

**Purpose:** Result of categorizing constraints into equalities, inequalities, and variable bounds.

**Fields:**

```python
@dataclass
class PartitionResult:
    equalities: list[str] = field(default_factory=list)
    inequalities: list[str] = field(default_factory=list)
    
    # Key: (var_name, indices_tuple), Value: BoundDef
    bounds_lo: dict[tuple[str, tuple], BoundDef] = field(default_factory=dict)
    bounds_up: dict[tuple[str, tuple], BoundDef] = field(default_factory=dict)
    bounds_fx: dict[tuple[str, tuple], BoundDef] = field(default_factory=dict)
    
    # Diagnostics
    skipped_infinite: list[tuple[str, tuple, str]] = field(default_factory=list)
    duplicate_excluded: list[str] = field(default_factory=list)
```

**Partitioning Rules:**

1. **Equalities**: Constraints with `relation="=e="`
2. **Inequalities**: Constraints with `relation="=l="` or `"=g="` (not bounds)
3. **Bounds**: Constraints of form `x ≤ c`, `x ≥ c`, or bounds from ModelIR.normalized_bounds
4. **Infinite Bounds**: Skipped (±INF), recorded in `skipped_infinite`
5. **Duplicates**: Variables appearing in both explicit bounds and constraints, recorded in `duplicate_excluded`

**Example:**

```python
# For model with:
# - Equality: obj =e= x^2 + y^2
# - Inequality: x + y =l= 10
# - Bounds: x.lo=0, x.up=100, y.lo=0

partition = PartitionResult(
    equalities=["obj_eq"],
    inequalities=["con1"],
    bounds_lo={
        ("x", ()): BoundDef(kind='lo', value=0.0, domain=()),
        ("y", ()): BoundDef(kind='lo', value=0.0, domain=()),
    },
    bounds_up={
        ("x", ()): BoundDef(kind='up', value=100.0, domain=()),
    },
    bounds_fx={},
    skipped_infinite=[],
    duplicate_excluded=[],
)
```

---

### ObjectiveInfo

**Location:** `src/kkt/objective.py`

**Created By:** `find_objective_info()` in `src/kkt/objective.py`

**Consumed By:** `compute_objective_gradient()` in `src/ad/gradient.py` (via KKT assembly)

**Purpose:** Metadata about the objective variable and its defining equation.

**Fields:**

```python
@dataclass
class ObjectiveInfo:
    objvar: str  # Name of objective variable
    objvar_indices: tuple[str, ...] = ()  # Indices (empty for scalar)
    defining_equation: str = ""  # Name of equation defining objvar
    needs_stationarity: bool = False  # Whether stationarity eq needed for objvar
```

**Two Patterns:**

1. **Objective defined by equation** (most common in GAMS):
   ```gams
   obj_eq.. obj =e= x^2 + y^2;
   Solve mymodel using NLP minimizing obj;
   ```
   ```python
   ObjectiveInfo(
       objvar="obj",
       objvar_indices=(),
       defining_equation="obj_eq",
       needs_stationarity=True  # Need stationarity eq for obj
   )
   ```

2. **Inline objective expression** (less common):
   ```gams
   Solve mymodel using NLP minimizing (x^2 + y^2);
   ```
   ```python
   ObjectiveInfo(
       objvar="anonymous_obj",
       objvar_indices=(),
       defining_equation="",
       needs_stationarity=False  # No separate variable
   )
   ```

**Stationarity Decision:**

If objective variable appears in the defining equation (e.g., `obj =e= x^2 + y^2`), then it needs its own stationarity equation in the KKT system. The coefficient from ∂f/∂obj appears in this equation.

---

### MultiplierRef (AST Node)

**Location:** `src/ir/ast.py`

**Purpose:** AST node representing a reference to a KKT multiplier variable (ν, λ, π) in stationarity equations.

**Fields:**

```python
@dataclass(frozen=True)
class MultiplierRef(Expr):
    """Reference to a KKT multiplier variable."""
    name: str  # Multiplier name (e.g., "nu_obj_eq", "lambda_con1")
    indices: tuple[str, ...] = ()  # Empty for scalar, filled for indexed
```

**Usage:**

MultiplierRef nodes appear in stationarity equation expressions to represent Lagrange multiplier terms. They are created during KKT assembly when building the Lagrangian gradient.

**Examples:**

```python
# Scalar multiplier: nu_obj_eq
MultiplierRef("nu_obj_eq", ())

# Indexed multiplier: lambda_con(i1)
MultiplierRef("lambda_con", ("i1",))

# In stationarity equation: 2*x + nu_obj_eq + lambda_con1 = 0
Binary(
    "+",
    Binary("+",
        Binary("*", Const(2.0), VarRef("x")),
        MultiplierRef("nu_obj_eq", ())
    ),
    MultiplierRef("lambda_con1", ())
)
```

**Differentiation:**

MultiplierRef nodes are treated as constants during automatic differentiation (derivative is zero). They represent dual variables, not primal decision variables.

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

### Example 3: KKT System Assembly (Sprint 3)

**GAMS Input:**

```gams
Variables x, y, obj;
Equations obj_eq, con_ineq;

obj_eq.. obj =e= x^2 + y^2;
con_ineq.. x + y =l= 10;

x.lo = 0;
y.lo = 0;

Solve mymodel using NLP minimizing obj;
```

**After Sprint 1 (ModelIR):**

```python
ModelIR(
    variables={"x": ..., "y": ..., "obj": ...},
    equations={"obj_eq": ..., "con_ineq": ...},
    equalities=["obj_eq"],
    inequalities=["con_ineq", "x_lo", "y_lo"],
    normalized_bounds={
        "x_lo": NormalizedEquation(...),
        "y_lo": NormalizedEquation(...),
    },
    objective=ObjectiveIR(sense=ObjSense.MIN, objvar="obj", expr=None),
)
```

**After Sprint 2 (AD):**

```python
# Gradient: ∇f = [∂obj/∂x, ∂obj/∂y, ∂obj/∂obj]
gradient = GradientVector(
    num_cols=3,
    entries={
        0: Binary("*", Const(-2.0), VarRef("x")),  # ∂obj_eq/∂x (from obj - expr = 0)
        1: Binary("*", Const(-2.0), VarRef("y")),  # ∂obj_eq/∂y
        2: Const(1.0),  # ∂obj_eq/∂obj = 1
    },
)

# Jacobian of equality: obj - (x^2 + y^2) = 0
J_eq = JacobianStructure(
    num_rows=1,
    num_cols=3,
    entries={
        0: {  # obj_eq row
            0: Binary("*", Const(-2.0), VarRef("x")),
            1: Binary("*", Const(-2.0), VarRef("y")),
            2: Const(1.0),
        },
    },
)

# Jacobian of inequality: x + y - 10 <= 0, -x <= 0, -y <= 0
J_ineq = JacobianStructure(
    num_rows=3,
    num_cols=3,
    entries={
        0: {0: Const(1.0), 1: Const(1.0)},  # ∂con_ineq/∂x=1, ∂con_ineq/∂y=1
        1: {0: Const(-1.0)},  # ∂x_lo/∂x = -1
        2: {1: Const(-1.0)},  # ∂y_lo/∂y = -1
    },
)
```

**After Sprint 3 (KKT System):**

```python
kkt_system = KKTSystem(
    model_ir=ModelIR(...),
    gradient=gradient,
    J_eq=J_eq,
    J_ineq=J_ineq,
    
    # Lagrange multipliers
    multipliers_eq={
        "obj_eq": MultiplierDef(
            name="nu_obj_eq",
            domain=(),
            kind="eq",
            associated_constraint="obj_eq"
        ),
    },
    multipliers_ineq={
        "con_ineq": MultiplierDef(
            name="lambda_con_ineq",
            domain=(),
            kind="ineq",
            associated_constraint="con_ineq"
        ),
    },
    multipliers_bounds_lo={
        ("x", ()): MultiplierDef(
            name="pi_lo_x",
            domain=(),
            kind="bound_lo",
            associated_constraint="x_lo"
        ),
        ("y", ()): MultiplierDef(
            name="pi_lo_y",
            domain=(),
            kind="bound_lo",
            associated_constraint="y_lo"
        ),
    },
    
    # Stationarity equations: ∇f + J_eq^T·ν + J_ineq^T·λ = 0
    stationarity={
        "x": EquationDef(
            name="stat_x",
            domain=(),
            relation="=e=",
            # -2*x + (-2*x)*nu_obj_eq + 1*lambda_con_ineq - 1*pi_lo_x = 0
            expression=Binary("+",
                Binary("+",
                    Binary("*", Const(-2.0), VarRef("x")),
                    Binary("*",
                        Binary("*", Const(-2.0), VarRef("x")),
                        MultiplierRef("nu_obj_eq", ())
                    )
                ),
                Binary("-",
                    MultiplierRef("lambda_con_ineq", ()),
                    MultiplierRef("pi_lo_x", ())
                )
            )
        ),
        "y": EquationDef(
            name="stat_y",
            domain=(),
            relation="=e=",
            # -2*y + (-2*y)*nu_obj_eq + 1*lambda_con_ineq - 1*pi_lo_y = 0
            expression=...
        ),
        "obj": EquationDef(
            name="stat_obj",
            domain=(),
            relation="=e=",
            # 1 + 1*nu_obj_eq = 0  →  nu_obj_eq = -1
            expression=Binary("+",
                Const(1.0),
                MultiplierRef("nu_obj_eq", ())
            )
        ),
    },
    
    # Complementarity conditions
    complementarity_ineq={
        "con_ineq": ComplementarityPair(
            equation=EquationDef(
                name="con_ineq_compl",
                domain=(),
                relation="=l=",
                expression=Binary("-",
                    Binary("+", VarRef("x"), VarRef("y")),
                    Const(10.0)
                )  # x + y - 10 <= 0
            ),
            variable="lambda_con_ineq",
            variable_indices=()
        ),
    },
    complementarity_bounds_lo={
        ("x", ()): ComplementarityPair(
            equation=EquationDef(
                name="x_lo_compl",
                domain=(),
                relation="=g=",
                expression=VarRef("x")  # x >= 0
            ),
            variable="pi_lo_x",
            variable_indices=()
        ),
        ("y", ()): ComplementarityPair(
            equation=EquationDef(
                name="y_lo_compl",
                domain=(),
                relation="=g=",
                expression=VarRef("y")  # y >= 0
            ),
            variable="pi_lo_y",
            variable_indices=()
        ),
    },
)
```

**GAMS MCP Output:**

```gams
Variables nu_obj_eq, lambda_con_ineq, pi_lo_x, pi_lo_y;

Equations stat_x, stat_y, stat_obj;
Equations con_ineq_compl, x_lo_compl, y_lo_compl;

stat_x.. -2*x + (-2*x)*nu_obj_eq + lambda_con_ineq - pi_lo_x =E= 0;
stat_y.. -2*y + (-2*y)*nu_obj_eq + lambda_con_ineq - pi_lo_y =E= 0;
stat_obj.. 1 + nu_obj_eq =E= 0;

con_ineq_compl.. x + y - 10 =N= 0;
x_lo_compl.. x =N= 0;
y_lo_compl.. y =N= 0;

Model mymodel_mcp / stat_x.x, stat_y.y, stat_obj.obj,
                    con_ineq_compl.lambda_con_ineq,
                    x_lo_compl.pi_lo_x,
                    y_lo_compl.pi_lo_y /;
```

**Data Flow Summary:**

```
GAMS Source
    ↓
ModelIR (Sprint 1)
    ↓
GradientVector + JacobianStructure (Sprint 2)
    ↓
KKTSystem (Sprint 3)
    ↓
GAMS MCP Output (Sprint 3)
```

---

## See Also

- [System Architecture](SYSTEM_ARCHITECTURE.md) - Complete data flow diagram
- [Sprint 2 Retrospective](../planning/SPRINT_2/RETROSPECTIVE.md) - Lessons learned
- [Sprint 3 Prep Plan](../planning/SPRINT_3/PREP_PLAN.md) - Process improvements

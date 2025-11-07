"""
Min/Max Reformulation for MCP.

This module implements the epigraph reformulation of non-smooth min/max functions
into smooth complementarity conditions suitable for MCP solvers like PATH.

Design Overview
===============

The min(x, y, ...) and max(x, y, ...) functions are non-smooth (non-differentiable)
at points where arguments are equal. To handle them in NLP→MCP conversion, we use
the standard epigraph reformulation approach.

Min Reformulation (Epigraph Form)
----------------------------------

Original constraint:
    z = min(x₁, x₂, ..., xₙ)

Reformulated as MCP:
    Variables:
        z_min (auxiliary variable replacing z)
        λ₁, λ₂, ..., λₙ (multipliers, all >= 0)

    Complementarity conditions:
        (x₁ - z_min) ⊥ λ₁  i.e.,  x₁ - z_min >= 0, λ₁ >= 0, (x₁ - z_min) · λ₁ = 0
        (x₂ - z_min) ⊥ λ₂  i.e.,  x₂ - z_min >= 0, λ₂ >= 0, (x₂ - z_min) · λ₂ = 0
        ...
        (xₙ - z_min) ⊥ λₙ  i.e.,  xₙ - z_min >= 0, λₙ >= 0, (xₙ - z_min) · λₙ = 0

    Stationarity for z_min:
        ∂L/∂z_min = ∂f/∂z_min - Σᵢ λᵢ = 0

Why this works:
    - At the solution, z_min equals the minimum of all arguments
    - For the active argument (say x₁ = z_min), we have x₁ - z_min = 0, so λ₁ can be > 0
    - For inactive arguments (xᵢ > z_min), we have xᵢ - z_min > 0, so λᵢ = 0
    - The stationarity condition ensures Σλᵢ = ∂f/∂z_min (for minimization, this equals 1)

Example:
    Original NLP:
        minimize  z
        s.t.      z = min(x, y)
                  x >= 1, y >= 2

    Optimal solution: z* = 1 (since x can be 1, y can be 2)

    Reformulated MCP:
        Variables: x, y, z_min, λ_x, λ_y

        Equations:
            stat_x:     ∂f/∂x + ... = 0        (stationarity for x)
            stat_y:     ∂f/∂y + ... = 0        (stationarity for y)
            stat_z:     ∂f/∂z_min - λ_x - λ_y = 0

        Complementarity pairs:
            (x - z_min) ⊥ λ_x  (λ_x >= 0)
            (y - z_min) ⊥ λ_y  (λ_y >= 0)

        Model mcp / stat_x.x, stat_y.y, stat_z.z_min,
                    (x - z_min).λ_x, (y - z_min).λ_y /;

    At solution: x=1, y=2, z_min=1, λ_x > 0 (active), λ_y = 0 (slack)

Max Reformulation (Dual Epigraph)
----------------------------------

Original constraint:
    w = max(x₁, x₂, ..., xₙ)

Reformulated as MCP:
    Variables:
        w_max (auxiliary variable replacing w)
        μ₁, μ₂, ..., μₙ (multipliers, all >= 0)

    Complementarity conditions:
        (w_max - x₁) ⊥ μ₁  i.e.,  w_max - x₁ >= 0, μ₁ >= 0, (w_max - x₁) · μ₁ = 0
        (w_max - x₂) ⊥ μ₂  i.e.,  w_max - x₂ >= 0, μ₂ >= 0, (w_max - x₂) · μ₂ = 0
        ...
        (w_max - xₙ) ⊥ μₙ  i.e.,  w_max - xₙ >= 0, μₙ >= 0, (w_max - xₙ) · μₙ = 0

    Stationarity for w_max:
        ∂L/∂w_max = ∂f/∂w_max + Σᵢ μᵢ = 0

Note the sign difference:
    - Min: constraints are (xᵢ - z) >= 0, stationarity has -Σλᵢ
    - Max: constraints are (w - xᵢ) >= 0, stationarity has +Σμᵢ

Alternative: max via min transformation
    max(x, y) = -min(-x, -y)

    While mathematically correct, direct implementation is preferred:
    - Clearer MCP structure (fewer negations)
    - Simpler derivative computation
    - Better numerical properties (no double negation)

Multi-Argument Handling
------------------------

Both min and max naturally extend to n arguments:
    - min(x₁, ..., xₙ) creates n complementarity pairs
    - max(x₁, ..., xₙ) creates n complementarity pairs
    - Scales linearly: n arguments → n+1 variables, n+1 equations

Nested Functions (Flattening)
------------------------------

Nested calls should be flattened before reformulation:

    Original:
        z = min(min(x, y), w)

    Flattened:
        z = min(x, y, w)

    Why flatten:
        - Fewer auxiliary variables (1 instead of 2)
        - Simpler MCP structure
        - Mathematically equivalent
        - Better numerical properties

    Flattening algorithm:
        def flatten_min(expr):
            if not is_min_call(expr):
                return [expr]
            args = []
            for arg in expr.args:
                if is_min_call(arg):
                    args.extend(flatten_min(arg))  # Recursive
                else:
                    args.append(arg)
            return args

Constants in Min/Max
--------------------

Constants are treated identically to variables:
    min(x, 5, y)  →  Creates 3 constraints: x-z>=0, 5-z>=0, y-z>=0

    No special handling needed. The constant becomes an inactive constraint
    if it's larger than the minimum.

Edge Cases
----------

1. Single argument: min(x) = x, max(x) = x
   - Detection recommended: if len(args) == 1, return arg directly
   - Avoids unnecessary auxiliary variables

2. Zero arguments: min() or max()
   - Should be flagged as semantic error
   - Not mathematically meaningful

3. Duplicate arguments: min(x, x)
   - Valid but redundant
   - Creates duplicate constraints (both will have same slack)
   - Could optimize by detecting duplicates

Implementation Strategy (Day 3 - Infrastructure)
-------------------------------------------------

Day 3 focuses on infrastructure and detection, not full reformulation:

1. AST Detection:
   - Traverse equation expressions
   - Identify Call nodes with func_name in {'min', 'max'}
   - Extract arguments and context

2. Auxiliary Variable Naming:
   - Scheme: aux_{min|max}_{context}_{counter}
   - Context: equation name or unique identifier
   - Counter: for multiple min/max in same equation
   - Collision detection with user variables

3. Flattening:
   - Recursive traversal of min/max arguments
   - Collect all leaf arguments
   - Preserve non-min/max expressions

4. Design Validation:
   - Unit tests for detection
   - Unit tests for naming scheme
   - Unit tests for flattening algorithm
   - No actual MCP generation yet (Day 4)

Day 4 will implement:
- Actual reformulation (creating constraints)
- Integration with KKT assembly
- Derivative computation for auxiliary variables
- MCP emission with complementarity pairs

References
----------
- Ferris & Pang (1997): Engineering and Economic Applications of Complementarity Problems
- Ralph & Wright (2004): Some Properties of Regularization and Penalization Schemes
- Luo, Pang & Ralph (1996): Mathematical Programs with Equilibrium Constraints
- GAMS Documentation: MCP Model Type, PATH Solver
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..ir.ast import Call, Const, Expr

if TYPE_CHECKING:
    from ..ir.ast import VarRef
    from ..ir.model_ir import ModelIR
    from ..ir.symbols import EquationDef

# Constraint naming constants for min/max reformulation
# These prefixes are used to identify constraint types in complementarity and stationarity builders
MINMAX_MIN_CONSTRAINT_PREFIX = "minmax_min_"
MINMAX_MAX_CONSTRAINT_PREFIX = "minmax_max_"


@dataclass
class MinMaxCall:
    """
    Represents a detected min() or max() function call in an expression.

    Attributes:
        func_type: Either 'min' or 'max'
        args: List of argument expressions (already flattened if nested)
        context: Identifier for where this call appears (e.g., equation name)
        index: Integer to distinguish multiple calls in same context
    """

    func_type: str  # 'min' or 'max'
    args: list[Expr]
    context: str  # e.g., "eq_balance_i1"
    index: int = 0  # for multiple min/max in same equation


@dataclass
class AuxiliaryVariableManager:
    """
    Manages naming and collision detection for auxiliary variables.

    Strategy:
        - Auxiliary variables named: aux_{min|max}_{context}_{index}
        - Context is equation name or unique identifier
        - Index increments for multiple min/max in same equation
        - Collision detection checks against user-declared variables

    Example names:
        - aux_min_objdef_0      (first min in objective equation)
        - aux_max_balance_1     (second max in balance equation)
        - aux_min_eq_cost_i1_0  (min in indexed equation instance)

    Attributes:
        user_variables: Set of user-declared variable names to check for collisions
        generated_names: Counter mapping (func_type, context) pairs to next available index
    """

    user_variables: set[str] = field(default_factory=set)
    generated_names: dict[tuple[str, str], int] = field(
        default_factory=dict
    )  # (func_type, context) -> counter

    def generate_name(self, func_type: str, context: str) -> str:
        """
        Generate a unique auxiliary variable name.

        Args:
            func_type: Either 'min' or 'max'
            context: Context identifier (equation name, etc.)

        Returns:
            Unique variable name: aux_{min|max}_{context}_{index}

        Raises:
            ValueError: If generated name collides with user variable
        """
        if func_type not in ("min", "max"):
            raise ValueError(f"func_type must be 'min' or 'max', got: {func_type}")

        # Get next index for this (func_type, context) pair
        # This ensures min and max have separate counters
        key = (func_type, context)
        index = self.generated_names.get(key, 0)
        self.generated_names[key] = index + 1

        # Generate name
        name = f"aux_{func_type}_{context}_{index}"

        # Check for collision with user variables
        if name in self.user_variables:
            raise ValueError(
                f"Generated auxiliary variable name '{name}' collides with user variable. "
                f"Please rename your variable or choose a different equation name."
            )

        return name

    def register_user_variables(self, var_names: set[str]) -> None:
        """Register user-declared variable names for collision detection."""
        self.user_variables.update(var_names)


def is_min_or_max_call(expr: Expr) -> bool:
    """Check if expression is a min() or max() function call."""
    return isinstance(expr, Call) and expr.func.lower() in ("min", "max")


def flatten_min_max_args(expr: Call) -> list[Expr]:
    """
    Flatten nested min/max calls into a single argument list.

    Example:
        min(min(x, y), z)  →  [x, y, z]
        max(a, max(b, c))  →  [a, b, c]
        min(x, y+2)        →  [x, y+2]  (non-min preserved)

    Args:
        expr: A Call expression with func_name in {'min', 'max'}

    Returns:
        Flattened list of argument expressions
    """
    if not isinstance(expr, Call):
        return [expr]

    func_type = expr.func.lower()
    if func_type not in ("min", "max"):
        return [expr]

    # Recursively flatten arguments
    flattened = []
    for arg in expr.args:
        if isinstance(arg, Call) and arg.func.lower() == func_type:
            # Same function type: flatten recursively
            flattened.extend(flatten_min_max_args(arg))
        else:
            # Different type or non-Call: keep as-is
            flattened.append(arg)

    return flattened


def detect_min_max_calls(expr: Expr, context: str) -> list[MinMaxCall]:
    """
    Detect all min/max calls in an expression and return flattened representations.

    This is the main entry point for Day 3 infrastructure.

    Args:
        expr: Expression AST to search
        context: Context identifier (equation name, etc.)

    Returns:
        List of MinMaxCall objects with flattened arguments

    Example:
        expr = Call('min', [VarRef('x'), VarRef('y')])
        calls = detect_min_max_calls(expr, 'objdef')
        # Returns: [MinMaxCall('min', [VarRef('x'), VarRef('y')], 'objdef', 0)]
    """
    detected = []
    index_counter = 0

    def traverse(node: Expr) -> None:
        nonlocal index_counter
        if isinstance(node, Call) and node.func.lower() in ("min", "max"):
            # Found a min/max call
            func_type = node.func.lower()
            flattened_args = flatten_min_max_args(node)

            detected.append(
                MinMaxCall(
                    func_type=func_type,
                    args=flattened_args,
                    context=context,
                    index=index_counter,
                )
            )
            index_counter += 1

            # Continue traversing into flattened args to find different-type nested calls
            # (e.g., max inside min or min inside max)
            for arg in flattened_args:
                traverse(arg)
            return

        # Traverse child expressions based on type
        if isinstance(node, Call):
            for arg in node.args:
                traverse(arg)
        elif hasattr(node, "__dict__"):
            # Generic traversal for other expression types
            for value in node.__dict__.values():
                if isinstance(value, Expr):
                    traverse(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, Expr):
                            traverse(item)

    traverse(expr)
    return detected


# =============================================================================
# Day 4: Actual Reformulation Implementation
# =============================================================================


@dataclass
class ReformulationResult:
    """
    Result of reformulating a single min/max call.

    Contains all the auxiliary variables, multipliers, and constraints
    needed to replace the non-smooth min/max with complementarity conditions.

    Attributes:
        aux_var_name: Name of auxiliary variable (e.g., "aux_min_objdef_0")
        multiplier_names: Names of multiplier variables (one per argument)
        constraints: List of (constraint_name, EquationDef) for complementarity
        replacement_expr: Expression to use in place of original min/max call
        original_lhs_var: If this min/max defined a variable, which one (for Strategy 1)
        context: Equation name where this min/max appeared
    """

    aux_var_name: str
    multiplier_names: list[str]
    constraints: list[tuple[str, EquationDef]]
    replacement_expr: VarRef
    original_lhs_var: str | None = None
    context: str = ""


def reformulate_min(min_call: MinMaxCall, aux_mgr: AuxiliaryVariableManager) -> ReformulationResult:
    """
    Reformulate min(x₁, x₂, ..., xₙ) into MCP complementarity form.

    Creates:
        - Auxiliary variable z_min
        - n multiplier variables λ₁, λ₂, ..., λₙ (all >= 0)
        - n complementarity constraints: (xᵢ - z_min) ⊥ λᵢ

    Mathematical formulation:
        For each argument xᵢ:
            xᵢ - z_min >= 0  (with multiplier λᵢ >= 0)
            Complementarity: (xᵢ - z_min) · λᵢ = 0

    At solution:
        - z_min = min(x₁, ..., xₙ)
        - For active argument (xⱼ = z_min): λⱼ can be > 0
        - For inactive arguments (xᵢ > z_min): λᵢ = 0

    Args:
        min_call: MinMaxCall object with func_type='min'
        aux_mgr: Manager for generating unique variable names

    Returns:
        ReformulationResult with all components for MCP system

    Example:
        Input: min(x, y) in equation "objdef"
        Output:
            aux_var_name: "aux_min_objdef_0"
            multiplier_names: ["lambda_min_objdef_0_arg0", "lambda_min_objdef_0_arg1"]
            constraints: [
                ("comp_min_objdef_0_arg0", x - aux_min_objdef_0 >= 0),
                ("comp_min_objdef_0_arg1", y - aux_min_objdef_0 >= 0)
            ]
            replacement_expr: VarRef("aux_min_objdef_0")
    """
    from ..ir.ast import Binary, VarRef
    from ..ir.symbols import EquationDef, Rel

    if min_call.func_type != "min":
        raise ValueError(f"Expected func_type='min', got '{min_call.func_type}'")

    if not min_call.args:
        raise ValueError("min() call must have at least one argument")

    # Generate auxiliary variable name
    aux_var_name = aux_mgr.generate_name("min", min_call.context)

    # Generate multiplier names (one per argument)
    # Use standard KKT naming: base constraint name is "minmax_min_*"
    # The complementarity.py will create equations named "comp_<constraint_name>"
    # and multipliers named "lam_<constraint_name>", so the final names will be
    # "comp_minmax_min_*" for equations and "lam_minmax_min_*" for multipliers.
    multiplier_names = []
    for i in range(len(min_call.args)):
        constraint_name = (
            f"{MINMAX_MIN_CONSTRAINT_PREFIX}{min_call.context}_{min_call.index}_arg{i}"
        )
        # The multiplier will be named lam_<constraint> by KKT assembly
        mult_name = f"lam_{constraint_name}"
        multiplier_names.append(mult_name)

    # Create complementarity constraints: xᵢ - z_min >= 0
    constraints = []
    aux_var_ref = VarRef(aux_var_name, ())

    for i, arg_expr in enumerate(min_call.args):
        # Constraint: For min(x,y), we want x >= aux_min and y >= aux_min
        # Create: aux_min - arg <= 0 (meaning aux_min <= arg)
        # Complementarity negates: -(aux_min - arg) >= 0, i.e., arg - aux_min >= 0 ✓
        # Jacobian computes: ∂(aux_min - arg)/∂aux_min = +1
        # Stationarity subtracts the Jacobian term for negated constraints (correct sign!)
        constraint_name = (
            f"{MINMAX_MIN_CONSTRAINT_PREFIX}{min_call.context}_{min_call.index}_arg{i}"
        )

        lhs = Binary("-", aux_var_ref, arg_expr)  # aux_min - arg
        rhs = Const(0.0)

        constraint = EquationDef(
            name=constraint_name,
            domain=(),  # Scalar for now; indexed handling in future
            relation=Rel.LE,  # <= 0
            lhs_rhs=(lhs, rhs),
        )

        constraints.append((constraint_name, constraint))

    return ReformulationResult(
        aux_var_name=aux_var_name,
        multiplier_names=multiplier_names,
        constraints=constraints,
        replacement_expr=aux_var_ref,
        original_lhs_var=None,  # Will be set by reformulate_model
        context=min_call.context,
    )


def reformulate_max(max_call: MinMaxCall, aux_mgr: AuxiliaryVariableManager) -> ReformulationResult:
    """
    Reformulate max(x₁, x₂, ..., xₙ) into MCP complementarity form.

    Creates:
        - Auxiliary variable w_max
        - n multiplier variables μ₁, μ₂, ..., μₙ (all >= 0)
        - n complementarity constraints: (w_max - xᵢ) ⊥ μᵢ

    Mathematical formulation:
        For each argument xᵢ:
            w_max - xᵢ >= 0  (with multiplier μᵢ >= 0)
            Complementarity: (w_max - xᵢ) · μᵢ = 0

    At solution:
        - w_max = max(x₁, ..., xₙ)
        - For active argument (xⱼ = w_max): μⱼ can be > 0
        - For inactive arguments (xᵢ < w_max): μᵢ = 0

    Note: This is symmetric to min but with reversed inequality direction.
          Constraints are (w_max - xᵢ) >= 0 instead of (xᵢ - z_min) >= 0.

    Args:
        max_call: MinMaxCall object with func_type='max'
        aux_mgr: Manager for generating unique variable names

    Returns:
        ReformulationResult with all components for MCP system

    Example:
        Input: max(x, y) in equation "balance"
        Output:
            aux_var_name: "aux_max_balance_0"
            multiplier_names: ["mu_max_balance_0_arg0", "mu_max_balance_0_arg1"]
            constraints: [
                ("comp_max_balance_0_arg0", aux_max_balance_0 - x >= 0),
                ("comp_max_balance_0_arg1", aux_max_balance_0 - y >= 0)
            ]
            replacement_expr: VarRef("aux_max_balance_0")
    """
    from ..ir.ast import Binary, VarRef
    from ..ir.symbols import EquationDef, Rel

    if max_call.func_type != "max":
        raise ValueError(f"Expected func_type='max', got '{max_call.func_type}'")

    if not max_call.args:
        raise ValueError("max() call must have at least one argument")

    # Generate auxiliary variable name
    aux_var_name = aux_mgr.generate_name("max", max_call.context)

    # Generate multiplier names (one per argument)
    # Use standard KKT naming: base constraint name is "minmax_max_*"
    # The complementarity.py will create equations named "comp_minmax_max_*"
    # and multipliers named "lam_minmax_max_*", so we need to match that
    # TODO: Extract constraint naming logic into a helper function to reduce duplication
    # between reformulate_min() and reformulate_max()
    multiplier_names = []
    for i in range(len(max_call.args)):
        constraint_name = (
            f"{MINMAX_MAX_CONSTRAINT_PREFIX}{max_call.context}_{max_call.index}_arg{i}"
        )
        # The multiplier will be named lam_<constraint> by KKT assembly
        mult_name = f"lam_{constraint_name}"
        multiplier_names.append(mult_name)

    # Create complementarity constraints: w_max - xᵢ >= 0
    constraints = []
    aux_var_ref = VarRef(aux_var_name, ())

    for i, arg_expr in enumerate(max_call.args):
        # Constraint: arg - aux_var <= 0  (equivalent to aux_var >= arg)
        # KKT system expects inequalities in form g(x) <= 0
        # Note: Don't use "comp_" prefix as complementarity.py adds it
        constraint_name = (
            f"{MINMAX_MAX_CONSTRAINT_PREFIX}{max_call.context}_{max_call.index}_arg{i}"
        )

        # LHS: arg - aux_var  (so constraint is arg - aux_var <= 0, i.e., aux_var >= arg)
        # RHS: 0

        lhs = Binary("-", arg_expr, aux_var_ref)
        rhs = Const(0.0)

        constraint = EquationDef(
            name=constraint_name,
            domain=(),  # Scalar for now; indexed handling in future
            relation=Rel.LE,  # <= 0
            lhs_rhs=(lhs, rhs),
        )

        constraints.append((constraint_name, constraint))

    return ReformulationResult(
        aux_var_name=aux_var_name,
        multiplier_names=multiplier_names,
        constraints=constraints,
        replacement_expr=aux_var_ref,
        original_lhs_var=None,  # Will be set by reformulate_model
        context=max_call.context,
    )


def apply_strategy1_objective_substitution(
    model: ModelIR, reformulation_results: list[ReformulationResult]
) -> None:
    """Apply Strategy 1: Direct Objective Substitution.

    For min/max calls that define variables in the objective chain,
    substitute intermediate variables with auxiliary variables directly
    in the equations.

    Transformation:
        minimize obj where obj = z and z = aux_min
        →
        minimize obj where obj = aux_min (z bypassed)

    Note: The objective variable (obj) remains unchanged in model.objective.
    This ensures KKT assembly correctly identifies which variable to skip.

    This resolves the KKT infeasibility that occurs with objective-defining
    min/max equations by eliminating intermediate variables from the chain.

    Args:
        model: The model to modify (modified in-place)
        reformulation_results: Results from min/max reformulation
    """
    from ..ir.ast import VarRef
    from ..ir.minmax_detection import trace_objective_chain
    from ..ir.model_ir import ObjectiveIR
    from ..ir.symbols import EquationDef

    if not model.objective:
        return

    # Detect objective chain
    obj_chain = trace_objective_chain(model)

    # Find reformulation results for variables in objective chain
    for result in reformulation_results:
        if result.original_lhs_var and result.original_lhs_var in obj_chain:
            # This aux variable should become the objective
            new_objvar = result.aux_var_name

            # DO NOT change model.objective.objvar - keep it as the original
            # objective variable (e.g., 'obj'). This ensures the KKT assembly
            # correctly skips only the true objective variable.

            # Step 1: Update objective expression
            # The objective now depends on aux_min instead of the intermediate variable.
            # This ensures the gradient ∂obj/∂(intermediate) = 0.
            # Keep objvar the same so KKT assembly still skips it correctly.
            model.objective = ObjectiveIR(
                sense=model.objective.sense,
                objvar=model.objective.objvar,  # Keep same (e.g., 'obj')
                expr=VarRef(new_objvar, ()),  # Change to aux_min
            )

            # Mark that Strategy 1 was applied
            # This tells KKT assembly to create multiplier for objdef equation
            model.strategy1_applied = True

            # Step 2: Find and update objective-defining equations
            # Replace intermediate variable references with auxiliary variable
            # Example: obj = z becomes obj = aux_min
            intermediate_var = result.original_lhs_var

            for eq_name, eq_def in model.equations.items():
                lhs, rhs = eq_def.lhs_rhs
                # Check if RHS references the intermediate variable
                if isinstance(rhs, VarRef) and rhs.name == intermediate_var:
                    # Update RHS to reference auxiliary variable instead
                    model.equations[eq_name] = EquationDef(
                        name=eq_def.name,
                        domain=eq_def.domain,
                        relation=eq_def.relation,
                        lhs_rhs=(lhs, VarRef(new_objvar, ())),
                    )

            # Only apply Strategy 1 once (first match in objective chain)
            # This is correct behavior: in a chain like obj = z where z = min(...),
            # we only need to substitute the first min/max encountered. Multiple matches
            # should not occur in a properly-formed objective chain with a single terminal
            # min/max operation, so we break after the first match to avoid redundant updates.
            break


def reformulate_model(model: ModelIR) -> None:
    """
    Reformulate all min/max calls in a model into MCP complementarity form.

    This is the main entry point for min/max reformulation (Day 4).

    Process:
        1. Scan all equations for min/max calls
        2. For each call, generate auxiliary variables and constraints
        3. Replace min/max calls with auxiliary variable references
        4. Add auxiliary variables and multipliers to model
        5. Add complementarity constraints to model

    The reformulation happens in-place, modifying the model's variables
    and equations dictionaries.

    Integration Point (from Unknown 6.4):
        This function should be called in cli.py AFTER normalize_model()
        and BEFORE compute_objective_gradient(). This ensures:
        - Auxiliary variables are added to model.variables
        - Auxiliary constraints are added to model.equations
        - IndexMapping will include them automatically during derivative computation

    Args:
        model: ModelIR to reformulate (modified in-place)

    Side Effects:
        - Adds auxiliary variables to model.variables
        - Adds multiplier variables to model.variables
        - Adds complementarity constraints to model.equations
        - Modifies equation expressions to replace min/max with aux vars

    Example:
        Before:
            equations = {"objdef": obj =e= min(x, y)}
            variables = {"x": ..., "y": ..., "obj": ...}

        After:
            equations = {
                "objdef": obj =e= aux_min_objdef_0,
                "comp_min_objdef_0_arg0": x - aux_min_objdef_0 =g= 0,
                "comp_min_objdef_0_arg1": y - aux_min_objdef_0 =g= 0
            }
            variables = {
                "x": ..., "y": ..., "obj": ...,
                "aux_min_objdef_0": VariableDef(...),
                "lambda_min_objdef_0_arg0": VariableDef(kind=POSITIVE, ...),
                "lambda_min_objdef_0_arg1": VariableDef(kind=POSITIVE, ...)
            }
    """
    from ..ir.symbols import EquationDef, VariableDef, VarKind

    # Initialize auxiliary variable manager
    aux_mgr = AuxiliaryVariableManager()
    aux_mgr.register_user_variables(set(model.variables.keys()))

    # Track all reformulations to apply
    reformulations: list[tuple[str, MinMaxCall, ReformulationResult]] = []
    all_results: list[ReformulationResult] = []  # For Strategy 1

    # Scan all equations for min/max calls
    for eq_name, eq_def in model.equations.items():
        lhs, rhs = eq_def.lhs_rhs

        # Check both sides for min/max calls
        for expr in [lhs, rhs]:
            min_max_calls = detect_min_max_calls(expr, eq_name)

            for call in min_max_calls:
                # Reformulate based on type
                if call.func_type == "min":
                    result = reformulate_min(call, aux_mgr)
                elif call.func_type == "max":
                    result = reformulate_max(call, aux_mgr)
                else:
                    raise ValueError(f"Unknown func_type: {call.func_type}")

                # Track which variable was defined (for Strategy 1)
                from ..ir.ast import VarRef

                if isinstance(lhs, VarRef):
                    result.original_lhs_var = lhs.name

                # Store for later use
                reformulations.append((eq_name, call, result))
                all_results.append(result)

    # Apply reformulations
    for eq_name, min_max_call, result in reformulations:
        # 1. Add auxiliary variable to model
        aux_var = VariableDef(
            name=result.aux_var_name,
            domain=(),
            kind=VarKind.CONTINUOUS,
            lo=None,  # Unbounded
            up=None,
        )
        model.add_var(aux_var)

        # 2. Track complementarity multipliers (do NOT add as primal variables!)
        # These multipliers will be paired with constraints in the MCP model.
        # They should NOT have stationarity equations generated for them.
        # The MCP emitter will declare them in the Positive Variables section
        # and pair them with their constraints in the Model declaration.
        for i, mult_name in enumerate(result.multiplier_names):
            constraint_name = result.constraints[i][0]
            model.complementarity_multipliers[mult_name] = constraint_name

        # 3. Add complementarity constraints to model
        # Add both to equations dict and inequalities list so they get processed by KKT
        for constraint_name, constraint_def in result.constraints:
            model.add_equation(constraint_def)
            # Also add to inequalities list so they get included in KKT assembly
            model.inequalities.append(constraint_name)

        # 4. Replace min/max call with auxiliary variable in original equation
        eq_def = model.equations[eq_name]
        lhs, rhs = eq_def.lhs_rhs

        # Replace min/max calls with aux var reference
        new_lhs = _replace_min_max_call(lhs, min_max_call, result.replacement_expr)
        new_rhs = _replace_min_max_call(rhs, min_max_call, result.replacement_expr)

        # Update equation with new expressions
        model.equations[eq_name] = EquationDef(
            name=eq_def.name,
            domain=eq_def.domain,
            relation=eq_def.relation,
            lhs_rhs=(new_lhs, new_rhs),
        )

    # Apply Strategy 1 for objective-defining cases
    apply_strategy1_objective_substitution(model, all_results)


def _replace_min_max_call(expr: Expr, call: MinMaxCall, replacement: Expr) -> Expr:
    """
    Recursively replace a min/max call with a replacement expression.

    This traverses the expression tree and replaces the matching Call node
    with the replacement expression (typically a VarRef to auxiliary variable).

    Args:
        expr: Expression to search and modify
        call: MinMaxCall object describing what to replace
        replacement: Expression to use instead (e.g., VarRef to aux var)

    Returns:
        New expression with replacements made
    """
    from ..ir.ast import Binary, Sum, Unary
    from ..ir.ast import Call as ASTCall

    # Check if this expression is the call we're looking for
    if isinstance(expr, ASTCall):
        if expr.func.lower() == call.func_type:
            # Check if arguments match (simple equality check)
            # For exact matching, we'd need to compare ASTs deeply
            # For now, assume first match is correct (single min/max per equation)
            if len(expr.args) == len(call.args):
                return replacement

    # Recursively replace in children
    if isinstance(expr, Binary):
        new_left = _replace_min_max_call(expr.left, call, replacement)
        new_right = _replace_min_max_call(expr.right, call, replacement)
        return Binary(expr.op, new_left, new_right)

    elif isinstance(expr, Unary):
        new_child = _replace_min_max_call(expr.child, call, replacement)
        return Unary(expr.op, new_child)

    elif isinstance(expr, ASTCall):
        new_args = tuple(_replace_min_max_call(arg, call, replacement) for arg in expr.args)
        return ASTCall(expr.func, new_args)

    elif isinstance(expr, Sum):
        new_body = _replace_min_max_call(expr.body, call, replacement)
        return Sum(expr.index_sets, new_body)

    # Base case: no replacement needed (Const, VarRef, ParamRef, etc.)
    return expr

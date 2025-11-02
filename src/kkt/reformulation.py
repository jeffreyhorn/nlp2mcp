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

from ..ir.ast import Call, Expr


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

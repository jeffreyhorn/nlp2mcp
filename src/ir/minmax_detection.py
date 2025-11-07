"""Detection of min/max in objective-defining equations.

This module provides functionality to detect when min() or max() functions
appear in equations that define the objective variable. This is critical for
proper KKT assembly because such cases require special handling to include
auxiliary constraint multipliers in the stationarity equations.

Background:
-----------
When min/max defines the objective variable (directly or through a chain),
the standard epigraph reformulation creates auxiliary equality constraints
(e.g., z = aux_min). These constraints MUST have multipliers in the KKT
system, or the system becomes mathematically infeasible.

Example:
    minimize obj
    s.t. obj = z
         z = min(x, y)

This requires detecting that min(x,y) defines z, which defines obj.

See: docs/research/minmax_objective_reformulation.md
     docs/design/minmax_kkt_fix_design.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.ir.ast import Call, Expr, VarRef

if TYPE_CHECKING:
    from src.ir.model_ir import ModelIR
    from src.ir.symbols import EquationDef


def detects_objective_minmax(model_ir: ModelIR) -> bool:
    """Detect if min/max appears in equations that define the objective variable.

    This function traces the dependency chain from the objective variable
    through defining equations to check if any contain min() or max() calls.

    Detection algorithm:
        1. Start with objective variable (from model_ir.objective.objvar)
        2. Find the equation that defines it (e.g., obj = z)
        3. Extract variables on the RHS of that equation
        4. For each RHS variable, recursively check if its defining equation contains min/max
        5. Handle chains: obj = z, z = w, w = min(x,y)
        6. Handle cycles by tracking visited equations

    Args:
        model_ir: Model IR to analyze

    Returns:
        True if min/max defines the objective variable (directly or through chain)
        False otherwise

    Example:
        >>> # Case 1: Direct min/max in objective equation
        >>> # obj = min(x, y)
        >>> detects_objective_minmax(model)  # True
        >>>
        >>> # Case 2: Chained through intermediate variable
        >>> # obj = z, z = min(x, y)
        >>> detects_objective_minmax(model)  # True
        >>>
        >>> # Case 3: Min/max in constraint, not objective
        >>> # obj = x + y, g = min(a, b)
        >>> detects_objective_minmax(model)  # False
    """
    if model_ir.objective is None:
        return False

    objvar = model_ir.objective.objvar

    # Build variable -> equation mapping
    definitions = _build_variable_definitions(model_ir)

    # Trace from objvar through defining equations
    visited_vars = set()
    visited_eqs = set()
    to_check = [objvar]

    while to_check:
        var = to_check.pop()

        # Avoid infinite loops on circular definitions
        if var in visited_vars:
            continue
        visited_vars.add(var)

        # Find equation defining this variable
        if var not in definitions:
            continue

        eq_name = definitions[var]

        # Avoid visiting same equation twice
        if eq_name in visited_eqs:
            continue
        visited_eqs.add(eq_name)

        eq_def = model_ir.equations[eq_name]

        # Check if equation contains min/max - THIS IS THE KEY CHECK
        if _contains_minmax(eq_def):
            return True

        # Extract variables from RHS to continue tracing
        # The variable is defined by this equation, so we trace dependencies
        lhs, rhs = eq_def.lhs_rhs

        # Standard case: var = expression, so trace variables in expression
        # For example: obj = z means we should check what defines z
        if isinstance(lhs, VarRef) and lhs.name == var:
            # var = RHS, so trace variables in RHS
            rhs_vars = _extract_variables(rhs)
            to_check.extend(rhs_vars)
        elif isinstance(rhs, VarRef) and rhs.name == var:
            # expression = var (less common), so trace variables in LHS
            lhs_vars = _extract_variables(lhs)
            to_check.extend(lhs_vars)
        else:
            # Safety: if var appears in a more complex way, trace both sides
            # This shouldn't normally happen for defining equations
            rhs_vars = _extract_variables(rhs)
            lhs_vars = _extract_variables(lhs)
            to_check.extend(rhs_vars)
            to_check.extend(lhs_vars)

    return False


def _build_variable_definitions(model_ir: ModelIR) -> dict[str, str]:
    """Map each variable to the equation that defines it (if any).

    A variable is "defined" by an equation if it appears alone on the LEFT side
    of an equality equation. This is the standard definition pattern: var = expr.

    Args:
        model_ir: Model IR

    Returns:
        Dictionary mapping variable name -> equation name

    Example:
        >>> # Given equations:
        >>> # obj_eq: obj =e= z
        >>> # min_eq: z =e= min(x, y)
        >>> defs = _build_variable_definitions(model)
        >>> defs["obj"]  # "obj_eq"
        >>> defs["z"]    # "min_eq" (z is defined here, not in obj_eq)
    """
    definitions = {}

    for eq_name, eq_def in model_ir.equations.items():
        lhs, rhs = eq_def.lhs_rhs

        # A variable is "defined" if it appears alone on the LHS
        # This is the standard pattern: z = min(x, y)
        if isinstance(lhs, VarRef):
            var_name = lhs.name
            # Record LHS definitions with priority (don't override)
            if var_name not in definitions:
                definitions[var_name] = eq_name

    return definitions


def _contains_minmax(eq_def: EquationDef) -> bool:
    """Check if equation contains min() or max() calls.

    Args:
        eq_def: Equation definition to check

    Returns:
        True if equation contains min or max calls

    Example:
        >>> # z =e= min(x, y)
        >>> _contains_minmax(eq)  # True
        >>>
        >>> # z =e= x + y
        >>> _contains_minmax(eq)  # False
    """
    lhs, rhs = eq_def.lhs_rhs

    for expr in [lhs, rhs]:
        if _expr_contains_minmax(expr):
            return True

    return False


def _expr_contains_minmax(expr: Expr) -> bool:
    """Recursively check if an expression contains a min() or max() call.

    This is a pure IR-layer implementation that doesn't depend on the KKT layer,
    avoiding circular dependencies.

    Args:
        expr: Expression to check

    Returns:
        True if the expression or any sub-expression contains min/max

    Examples:
        >>> from src.ir.ast import Call, VarRef, Const
        >>> # min(x, y)
        >>> expr = Call("min", (VarRef("x"), VarRef("y")))
        >>> _expr_contains_minmax(expr)  # True
        >>>
        >>> # x + y
        >>> expr = BinOp("+", VarRef("x"), VarRef("y"))
        >>> _expr_contains_minmax(expr)  # False
    """
    from src.ir.ast import Call

    # Direct min/max call
    if isinstance(expr, Call) and expr.func in {"min", "max"}:
        return True

    # Recursively check all child expressions
    for child in expr.children():
        if _expr_contains_minmax(child):
            return True

    return False


def trace_objective_chain(model_ir: ModelIR) -> set[str]:
    """Trace all variables involved in defining the objective.

    Returns set of variable names that are part of the objective-defining chain.
    This is used by Strategy 1 to identify which min/max calls need special handling.

    Args:
        model_ir: Model IR to analyze

    Returns:
        Set of variable names in the objective-defining chain

    Example:
        >>> # minimize obj where obj = z and z = x + y
        >>> trace_objective_chain(model_ir)  # {'obj', 'z'}
        >>>
        >>> # minimize obj where obj = min(x, y) directly
        >>> trace_objective_chain(model_ir)  # {'obj'}
    """
    if not model_ir.objective:
        return set()

    obj_var = model_ir.objective.objvar
    chain = {obj_var}

    # Build reverse dependency map: var -> equations that define it
    definitions = _build_variable_definitions(model_ir)

    # BFS to find all variables in the chain
    to_visit = [obj_var]
    visited = set()

    while to_visit:
        var = to_visit.pop(0)
        if var in visited:
            continue
        visited.add(var)

        # Find equation that defines this variable
        if var in definitions:
            eq_name = definitions[var]
            eq_def = model_ir.equations[eq_name]

            # Extract all variables from the RHS (what defines this var)
            _, rhs = eq_def.lhs_rhs
            rhs_vars = _extract_variables(rhs)

            for rhs_var in rhs_vars:
                if rhs_var not in visited:
                    chain.add(rhs_var)
                    to_visit.append(rhs_var)

    return chain


def detect_minmax_in_objective_chain(model_ir: ModelIR) -> list[tuple[str, str, str]]:
    """Detect min/max calls in objective-defining equations.

    Returns list of (equation_name, var_name, func_type) tuples where:
    - equation_name: The equation containing min/max
    - var_name: The objective-chain variable being defined
    - func_type: 'min' or 'max'

    This is used by Strategy 1 to identify which min/max calls need
    objective substitution treatment.

    Args:
        model_ir: Model IR to analyze

    Returns:
        List of (equation_name, var_name, func_type) tuples

    Example:
        >>> # minimize obj where obj = z and z = min(x, y)
        >>> detect_minmax_in_objective_chain(model_ir)
        [('eq_z', 'z', 'min')]
        >>>
        >>> # minimize obj where obj = min(x, y) directly
        >>> detect_minmax_in_objective_chain(model_ir)
        [('objdef', 'obj', 'min')]
    """
    obj_chain = trace_objective_chain(model_ir)
    results = []

    for eq_name, eq_def in model_ir.equations.items():
        # Check if LHS is a simple variable in the objective chain
        lhs, rhs = eq_def.lhs_rhs
        if isinstance(lhs, VarRef) and lhs.name in obj_chain:
            # Check if RHS contains min/max
            if _contains_minmax(eq_def):
                # Determine which function type (min or max)
                func_type = _get_minmax_type(rhs)
                if func_type:
                    results.append((eq_name, lhs.name, func_type))

    return results


def _get_minmax_type(expr: Expr) -> str | None:
    """Get the min/max function type from an expression.

    Returns 'min', 'max', or None if no min/max found.
    For nested cases, returns the outermost min/max.

    Args:
        expr: Expression to check

    Returns:
        'min', 'max', or None
    """
    if isinstance(expr, Call) and expr.func in {"min", "max"}:
        return expr.func

    # Check children
    for child in expr.children():
        result = _get_minmax_type(child)
        if result:
            return result

    return None


def _extract_variables(expr: Expr) -> list[str]:
    """Extract all variable names from an expression.

    This recursively traverses the expression AST and collects all
    VarRef nodes, returning their variable names.

    Args:
        expr: Expression to analyze

    Returns:
        List of variable names (may contain duplicates)

    Example:
        >>> # expr = x + y * z
        >>> _extract_variables(expr)  # ["x", "y", "z"]
        >>>
        >>> # expr = min(x, y)
        >>> _extract_variables(expr)  # ["x", "y"]
    """
    vars_found = []

    def traverse(node: Expr) -> None:
        """Recursively traverse expression tree."""
        if isinstance(node, VarRef):
            vars_found.append(node.name)
        elif isinstance(node, Call):
            # Traverse function arguments
            for arg in node.args:
                traverse(arg)
        elif hasattr(node, "__dict__"):
            # Generic traversal for other expression types
            for value in node.__dict__.values():
                if isinstance(value, Expr):
                    traverse(value)
                elif isinstance(value, (list, tuple)):
                    for item in value:
                        if isinstance(item, Expr):
                            traverse(item)

    traverse(expr)
    return vars_found

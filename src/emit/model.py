"""GAMS Model MCP emission.

This module generates the Model MCP declaration with complementarity pairs.
"""

from src.ir.model_ir import ModelIR
from src.kkt.kkt_system import KKTSystem
from src.kkt.naming import create_eq_multiplier_name
from src.kkt.objective import ObjectiveInfo, extract_objective_info


def _extract_variable_name_from_stationarity(suffix: str, model_ir: ModelIR) -> str:
    """Extract the actual variable name from a stationarity equation suffix.

    Stationarity equations are named:
    - stat_x for scalar variables or indexed variables with uniform bounds
    - stat_x_i1 for per-instance equations (non-uniform bounds)

    This function finds the actual variable name by checking which model variable
    matches the prefix of the suffix.

    Args:
        suffix: The part after "stat_" (e.g., "x", "x_i1", "flow_node1")
        model_ir: Model IR containing variable definitions

    Returns:
        The actual variable name from the model

    Examples:
        >>> _extract_variable_name_from_stationarity("x", model_ir)  # has var "x"
        "x"
        >>> _extract_variable_name_from_stationarity("x_i1", model_ir)  # has var "x"
        "x"
        >>> _extract_variable_name_from_stationarity("flow_node1", model_ir)  # has var "flow"
        "flow"
    """
    # First, try exact match (most common case for indexed/scalar equations)
    if suffix in model_ir.variables:
        return suffix

    # For per-instance equations, the suffix is var_name + "_" + sanitized_indices
    # Find the longest variable name that is a prefix of the suffix
    # This handles cases like "x_i1" -> "x" and "flow_node1" -> "flow"
    best_match = ""
    for var_name in model_ir.variables:
        # Check if suffix starts with var_name followed by underscore
        if suffix.startswith(var_name + "_") and len(var_name) > len(best_match):
            best_match = var_name
        # Also check exact prefix match for edge cases
        elif suffix.startswith(var_name) and len(var_name) > len(best_match):
            # Only accept if the next char is underscore or end of string
            remaining = suffix[len(var_name) :]
            if remaining == "" or remaining.startswith("_"):
                best_match = var_name

    return best_match if best_match else suffix


def _should_pair_with_objvar(
    eq_name: str, obj_info: ObjectiveInfo, strategy1_applied: bool
) -> bool:
    """Determine if an equality equation should be paired with objvar.

    In standard NLP->MCP transformation, the objective-defining equation is paired
    with the objective variable rather than a multiplier. However, after Strategy 1
    is applied (when min/max appears in the objective), the objective-defining equation
    should be paired with a multiplier like any other equality.

    Args:
        eq_name: Name of the equation to check
        obj_info: Objective information including defining equation name
        strategy1_applied: Whether Strategy 1 reformulation was applied

    Returns:
        True if equation should be paired with objvar, False if with multiplier
    """
    return eq_name == obj_info.defining_equation and not strategy1_applied


def emit_model_mcp(kkt: KKTSystem, model_name: str = "mcp_model") -> str:
    """Emit Model MCP declaration with complementarity pairs.

    The Model MCP block lists all equation-variable pairs that form the
    complementarity problem. The pairing rules are:

    1. Stationarity equations paired with primal variables (except objvar)
       - stat_x.x
       - stat_y.y

    2. Inequality complementarity equations paired with multipliers
       - comp_g1.lam_g1

    3. Equality equations paired with free multipliers
       - eq_h1.nu_h1

    4. Objective defining equation paired with objvar (not a multiplier)
       - eq_objdef.obj

    5. Bound complementarity equations paired with bound multipliers
       - bound_lo_x.piL_x
       - bound_up_x.piU_x

    Args:
        kkt: The KKT system containing all equations and variables
        model_name: Name for the GAMS model (default: "mcp_model")

    Returns:
        GAMS Model MCP declaration string

    Example:
        ```gams
        Model mcp_model /
            stat_x.x,
            stat_y.y,
            comp_g1.lam_g1,
            eq_h1.nu_h1,
            eq_objdef.obj,
            bound_lo_x.piL_x,
            bound_up_y.piU_y
        /;
        ```
    """
    pairs = []

    # Extract objective info to handle objvar specially
    obj_info = extract_objective_info(kkt.model_ir)

    # 1. Stationarity equations paired with primal variables
    if kkt.stationarity:
        pairs.append("    * Stationarity conditions")
        for eq_name in sorted(kkt.stationarity.keys()):
            # Extract variable name from stationarity equation name
            # stat_x -> x (scalar or indexed)
            # stat_x_i1 -> x (per-instance for non-uniform bounds)
            if eq_name.startswith("stat_"):
                # Extract base variable name by finding it in the model's variables
                # For per-instance equations (stat_x_i1), we need to find the actual
                # variable name (x) not the full suffix (x_i1)
                suffix = eq_name[5:]  # Remove "stat_" prefix
                var_name = _extract_variable_name_from_stationarity(suffix, kkt.model_ir)

                # Skip objective variable UNLESS Strategy 1 was applied
                # or the objective is a simple variable that needs stationarity
                # (Issue #624: must be consistent with build_stationarity_equations)
                skip_objvar = not kkt.model_ir.strategy1_applied and not obj_info.needs_stationarity
                if var_name and (not skip_objvar or var_name != obj_info.objvar):
                    # GAMS MCP syntax: indexed equations listed without indices
                    # stat_x.x (not stat_x(i).x(i)) - indexing is implicit
                    # For per-instance stationarity (stat_x_i1.x), we pair scalar
                    # equation with indexed variable - GAMS handles the element selection
                    pairs.append(f"    {eq_name}.{var_name}")

    # 2. Inequality complementarities (includes min/max complementarity)
    # Skip pairs whose multiplier was simplified away from stationarity equations
    ref_mults = kkt.referenced_multipliers
    if kkt.complementarity_ineq:
        pairs.append("")
        pairs.append("    * Inequality complementarities")
        for _eq_name, comp_pair in sorted(kkt.complementarity_ineq.items()):
            if ref_mults is not None and comp_pair.variable not in ref_mults:
                continue
            eq_def = comp_pair.equation
            var_name = comp_pair.variable
            # GAMS MCP syntax: list without indices - indexing is implicit
            pairs.append(f"    {eq_def.name}.{var_name}")

    # 3. Equality constraints paired with free multipliers or objvar
    # Iterate through all equalities to ensure objective equation is included
    if kkt.model_ir.equalities:
        pairs.append("")
        pairs.append("    * Equality constraints")
        for eq_name in sorted(kkt.model_ir.equalities):
            # Check if this is the objective defining equation that should be paired with objvar
            # Note: The multiplier for objdef is created in build_complementarity_pairs()
            # for all equality constraints, so it's guaranteed to exist.
            if _should_pair_with_objvar(eq_name, obj_info, kkt.model_ir.strategy1_applied):
                # Pair with objvar, not a multiplier (standard NLP->MCP)
                # GAMS MCP syntax: list without indices - indexing is implicit
                pairs.append(f"    {eq_name}.{obj_info.objvar}")
            else:
                # Regular equality: pair with multiplier
                # (or objdef after Strategy 1)
                # Find the multiplier name for this equation
                mult_name = create_eq_multiplier_name(eq_name)
                # Skip if multiplier was simplified away
                if ref_mults is not None and mult_name not in ref_mults:
                    continue
                # GAMS MCP syntax: list without indices - indexing is implicit
                pairs.append(f"    {eq_name}.{mult_name}")

    # 4. Lower bound complementarities
    # For uniform bounds: indexed equation paired with indexed multiplier
    #   comp_lo_x.piL_x (GAMS matches indices automatically)
    # For non-uniform bounds: scalar equation paired with scalar multiplier
    #   comp_lo_x_i1.piL_x_i1 (both are scalar, no indices needed)
    if kkt.complementarity_bounds_lo:
        pairs.append("")
        pairs.append("    * Lower bound complementarities")
        for _key, comp_pair in sorted(kkt.complementarity_bounds_lo.items()):
            if ref_mults is not None and comp_pair.variable not in ref_mults:
                continue
            eq_def = comp_pair.equation
            var_name = comp_pair.variable
            # Both uniform (indexed) and non-uniform (scalar) cases use simple pairing
            # GAMS handles domain matching for indexed cases
            pairs.append(f"    {eq_def.name}.{var_name}")

    # 5. Upper bound complementarities
    # Same approach as lower bounds
    if kkt.complementarity_bounds_up:
        pairs.append("")
        pairs.append("    * Upper bound complementarities")
        for _key, comp_pair in sorted(kkt.complementarity_bounds_up.items()):
            if ref_mults is not None and comp_pair.variable not in ref_mults:
                continue
            eq_def = comp_pair.equation
            var_name = comp_pair.variable
            # Both uniform (indexed) and non-uniform (scalar) cases use simple pairing
            pairs.append(f"    {eq_def.name}.{var_name}")

    # Build the model declaration
    # GAMS does not allow comments inside the Model / ... / block
    # Filter out comment lines and empty lines, keeping only actual pairs
    actual_pairs = []
    for pair in pairs:
        stripped = pair.strip()
        # Keep only non-empty, non-comment lines
        if stripped and not stripped.startswith("*"):
            # Append the original (indented) line to preserve GAMS formatting
            # Do NOT use 'stripped' here - GAMS formatting conventions expect
            # consistent indentation for readability within model blocks
            actual_pairs.append(pair)

    # Build the model declaration with commas
    lines = [f"Model {model_name} /"]

    for i, pair in enumerate(actual_pairs):
        # Add comma to all pairs except the last one
        if i < len(actual_pairs) - 1:
            lines.append(pair + ",")
        else:
            lines.append(pair)

    lines.append("/;")

    return "\n".join(lines)


def emit_solve(model_name: str = "mcp_model") -> str:
    """Emit Solve statement for MCP model.

    Args:
        model_name: Name of the GAMS model (default: "mcp_model")

    Returns:
        GAMS Solve statement

    Example:
        ```gams
        Solve mcp_model using MCP;
        ```
    """
    return f"Solve {model_name} using MCP;"

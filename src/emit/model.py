"""GAMS Model MCP emission.

This module generates the Model MCP declaration with complementarity pairs.
"""

from src.kkt.kkt_system import KKTSystem
from src.kkt.naming import create_eq_multiplier_name
from src.kkt.objective import ObjectiveInfo, extract_objective_info


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
            if eq_name.startswith("stat_"):
                # Extract base variable name
                var_name = eq_name[5:]  # Remove "stat_" prefix

                # Skip objective variable UNLESS Strategy 1 was applied
                skip_objvar = not kkt.model_ir.strategy1_applied
                if var_name and (not skip_objvar or var_name != obj_info.objvar):
                    # GAMS MCP syntax: indexed equations listed without indices
                    # stat_x.x (not stat_x(i).x(i)) - indexing is implicit
                    pairs.append(f"    {eq_name}.{var_name}")

    # 2. Inequality complementarities (includes min/max complementarity)
    if kkt.complementarity_ineq:
        pairs.append("")
        pairs.append("    * Inequality complementarities")
        for _eq_name, comp_pair in sorted(kkt.complementarity_ineq.items()):
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
                # GAMS MCP syntax: list without indices - indexing is implicit
                pairs.append(f"    {eq_name}.{mult_name}")

    # 4. Lower bound complementarities
    if kkt.complementarity_bounds_lo:
        pairs.append("")
        pairs.append("    * Lower bound complementarities")
        for _key, comp_pair in sorted(kkt.complementarity_bounds_lo.items()):
            eq_def = comp_pair.equation
            var_name = comp_pair.variable
            # GAMS MCP syntax: list without indices - indexing is implicit
            pairs.append(f"    {eq_def.name}.{var_name}")

    # 5. Upper bound complementarities
    if kkt.complementarity_bounds_up:
        pairs.append("")
        pairs.append("    * Upper bound complementarities")
        for _key, comp_pair in sorted(kkt.complementarity_bounds_up.items()):
            eq_def = comp_pair.equation
            var_name = comp_pair.variable
            # GAMS MCP syntax: list without indices - indexing is implicit
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

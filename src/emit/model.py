"""GAMS Model MCP emission.

This module generates the Model MCP declaration with complementarity pairs.
"""

from src.kkt.kkt_system import KKTSystem
from src.kkt.objective import extract_objective_info


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
            * Stationarity conditions
            stat_x.x
            stat_y.y

            * Inequality complementarities
            comp_g1.lam_g1

            * Equality constraints
            eq_h1.nu_h1
            eq_objdef.obj

            * Bound complementarities
            bound_lo_x.piL_x
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
        for eq_name, eq_def in sorted(kkt.stationarity.items()):
            # Extract variable name from stationarity equation name
            # stat_x -> x, stat_x_i1 -> x(i1)
            if eq_name.startswith("stat_"):
                var_part = eq_name[5:]  # Remove "stat_" prefix

                # Handle indexed variables: stat_x_i1 -> x.x(i1)
                # This is tricky - we need to extract the base variable name
                # For now, use the equation domain to reconstruct indices
                if eq_def.domain:
                    # Extract base variable name (everything before first index)
                    # This assumes naming like stat_x_i1 where x is var, i1 is index
                    # We'll need the actual variable name from the equation
                    # For simplicity, extract from first VarRef in equation
                    var_name = _extract_var_name_from_stat_eq(eq_def, kkt)
                    if var_name and var_name != obj_info.objvar:
                        indices_str = ",".join(eq_def.domain)
                        pairs.append(f"    {eq_name}.{var_name}({indices_str})")
                else:
                    # Scalar variable
                    var_name = var_part
                    if var_name != obj_info.objvar:
                        pairs.append(f"    {eq_name}.{var_name}")

    # 2. Inequality complementarities
    if kkt.complementarity_ineq:
        pairs.append("")
        pairs.append("    * Inequality complementarities")
        for _eq_name, comp_pair in sorted(kkt.complementarity_ineq.items()):
            eq_def = comp_pair.equation
            var_name = comp_pair.variable
            if comp_pair.variable_indices:
                indices_str = ",".join(comp_pair.variable_indices)
                pairs.append(f"    {eq_def.name}.{var_name}({indices_str})")
            else:
                pairs.append(f"    {eq_def.name}.{var_name}")

    # 3. Equality constraints paired with free multipliers
    # Include objective defining equation here
    if kkt.multipliers_eq:
        pairs.append("")
        pairs.append("    * Equality constraints")
        for mult_name, mult_def in sorted(kkt.multipliers_eq.items()):
            # Find the corresponding equation name
            eq_name = mult_def.associated_constraint

            # Check if this is the objective defining equation
            if eq_name == obj_info.defining_equation:
                # Pair with objvar, not the multiplier
                if mult_def.domain:
                    indices_str = ",".join(mult_def.domain)
                    pairs.append(f"    {eq_name}.{obj_info.objvar}({indices_str})")
                else:
                    pairs.append(f"    {eq_name}.{obj_info.objvar}")
            else:
                # Regular equality: pair with multiplier
                if mult_def.domain:
                    indices_str = ",".join(mult_def.domain)
                    pairs.append(f"    {eq_name}.{mult_name}({indices_str})")
                else:
                    pairs.append(f"    {eq_name}.{mult_name}")

    # 4. Lower bound complementarities
    if kkt.complementarity_bounds_lo:
        pairs.append("")
        pairs.append("    * Lower bound complementarities")
        for _key, comp_pair in sorted(kkt.complementarity_bounds_lo.items()):
            eq_def = comp_pair.equation
            var_name = comp_pair.variable
            if comp_pair.variable_indices:
                indices_str = ",".join(comp_pair.variable_indices)
                pairs.append(f"    {eq_def.name}.{var_name}({indices_str})")
            else:
                pairs.append(f"    {eq_def.name}.{var_name}")

    # 5. Upper bound complementarities
    if kkt.complementarity_bounds_up:
        pairs.append("")
        pairs.append("    * Upper bound complementarities")
        for _key, comp_pair in sorted(kkt.complementarity_bounds_up.items()):
            eq_def = comp_pair.equation
            var_name = comp_pair.variable
            if comp_pair.variable_indices:
                indices_str = ",".join(comp_pair.variable_indices)
                pairs.append(f"    {eq_def.name}.{var_name}({indices_str})")
            else:
                pairs.append(f"    {eq_def.name}.{var_name}")

    # Build the model declaration
    # Need to add commas between pairs (but not after comments or empty lines)
    lines = [f"Model {model_name} /"]

    # Process pairs to add commas
    for i, pair in enumerate(pairs):
        # Skip adding comma for comment lines, empty lines, and last item
        if pair.strip() and not pair.strip().startswith("*"):
            # This is an actual equation-variable pair
            # Check if there's a next non-comment, non-empty line
            needs_comma = False
            for j in range(i + 1, len(pairs)):
                next_line = pairs[j].strip()
                if next_line and not next_line.startswith("*"):
                    # Found another pair after this one
                    needs_comma = True
                    break

            if needs_comma:
                lines.append(pair + ",")
            else:
                lines.append(pair)
        else:
            # Comment or empty line - no comma
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


def _extract_var_name_from_stat_eq(eq_def, kkt: KKTSystem) -> str | None:
    """Extract the variable name from a stationarity equation.

    Stationarity equations are of the form:
        ∇f/∂x + ... = 0

    We need to extract 'x' from the equation structure.

    For now, we'll use a heuristic: the stationarity equation name
    is stat_<varname> or stat_<varname>_<indices>.

    Args:
        eq_def: The stationarity equation definition
        kkt: The KKT system

    Returns:
        Variable name, or None if not found
    """
    # Extract from equation name: stat_x or stat_x_i1
    eq_name = eq_def.name
    if not eq_name.startswith("stat_"):
        return None

    var_part = eq_name[5:]  # Remove "stat_" prefix

    # First check for exact match (scalar variable)
    if var_part in kkt.model_ir.variables:
        return var_part

    # For indexed variables: stat_x_i1 -> x
    # Sort variable names by descending length to match longest first
    # This prevents prefix issues (e.g., 'x' matching when looking for 'xy')
    for var_name in sorted(kkt.model_ir.variables, key=len, reverse=True):
        # Check for exact match
        if var_part == var_name:
            return var_name
        # Check for delimiter (underscore) after variable name
        # This ensures we match 'xy' in 'stat_xy_i1', not 'x'
        if var_part.startswith(var_name + "_"):
            return var_name

    return None

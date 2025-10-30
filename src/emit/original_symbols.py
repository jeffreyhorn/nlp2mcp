"""Emission of original model symbols (Sets, Aliases, Parameters).

This module emits GAMS declarations for the original model symbols using
actual IR fields (Finding #3 from final review).

Key principles:
- Use SetDef.members (not .elements)
- Use ParameterDef.domain and .values (not invented fields)
- Use AliasDef.target and .universe
- Scalars have empty domain () and values[()] = value
- Multi-dimensional parameter keys formatted as GAMS syntax: ("i1", "j2") → "i1.j2"
"""

from src.ir.model_ir import ModelIR


def emit_original_sets(model_ir: ModelIR) -> str:
    """Emit Sets block from original model.

    Uses SetDef.members (Finding #3: actual IR field).

    Args:
        model_ir: Model IR containing set definitions

    Returns:
        GAMS Sets block as string

    Example output:
        Sets
            i /i1, i2, i3/
            j /j1, j2/
        ;
    """
    if not model_ir.sets:
        return ""

    lines: list[str] = ["Sets"]
    for set_name, set_def in model_ir.sets.items():
        # Use SetDef.members (Finding #3)
        # Members are stored as a list of strings in SetDef
        if set_def.members:
            members = ", ".join(set_def.members)
            lines.append(f"    {set_name} /{members}/")
        else:
            # Empty set or universe
            lines.append(f"    {set_name}")
    lines.append(";")

    return "\n".join(lines)


def emit_original_aliases(model_ir: ModelIR) -> str:
    """Emit Alias declarations.

    Uses AliasDef.target and .universe (Finding #3: actual IR fields).

    Args:
        model_ir: Model IR containing alias definitions

    Returns:
        GAMS Alias declarations as string

    Example output:
        Alias(i, ip);
        Alias(j, jp);
    """
    if not model_ir.aliases:
        return ""

    lines = []
    for alias_name, alias_def in model_ir.aliases.items():
        # Use AliasDef.target (Finding #3)
        lines.append(f"Alias({alias_def.target}, {alias_name});")

    return "\n".join(lines)


def emit_original_parameters(model_ir: ModelIR) -> str:
    """Emit Parameters and Scalars with their data.

    Uses ParameterDef.domain and .values (Finding #3: actual IR fields).
    Scalars have empty domain () and values[()] = value.
    Multi-dimensional keys formatted as GAMS syntax: ("i1", "j2") → "i1.j2".

    Args:
        model_ir: Model IR containing parameter definitions

    Returns:
        GAMS Parameters and Scalars blocks as string

    Example output:
        Parameters
            c(i,j) /i1.j1 2.5, i1.j2 3.0, i2.j1 1.8/
            demand(j) /j1 100, j2 150/
        ;

        Scalars
            discount /0.95/
        ;
    """
    if not model_ir.params:
        return ""

    # Separate scalars (empty domain) from parameters
    scalars = {}
    parameters = {}

    for param_name, param_def in model_ir.params.items():
        # Use ParameterDef.domain to detect scalars (Finding #3)
        if len(param_def.domain) == 0:
            scalars[param_name] = param_def
        else:
            parameters[param_name] = param_def

    lines = []

    # Emit Parameters
    if parameters:
        lines.append("Parameters")
        for param_name, param_def in parameters.items():
            # Use ParameterDef.values (Finding #3)
            # Format tuple keys as GAMS syntax: ("i1", "j2") → "i1.j2"
            if param_def.values:
                data_parts = []
                for key_tuple, value in param_def.values.items():
                    # Convert tuple to GAMS index syntax (Finding #3)
                    key_str = ".".join(key_tuple)
                    data_parts.append(f"{key_str} {value}")

                data_str = ", ".join(data_parts)
                domain_str = ",".join(param_def.domain)
                lines.append(f"    {param_name}({domain_str}) /{data_str}/")
            else:
                # Parameter declared but no data
                domain_str = ",".join(param_def.domain)
                lines.append(f"    {param_name}({domain_str})")
        lines.append(";")

    # Emit Scalars
    if scalars:
        if lines:  # Add blank line if parameters were emitted
            lines.append("")
        lines.append("Scalars")
        for scalar_name, scalar_def in scalars.items():
            # Scalars have values[()] = value (Finding #3)
            value = scalar_def.values.get((), 0.0)
            lines.append(f"    {scalar_name} /{value}/")
        lines.append(";")

    return "\n".join(lines)

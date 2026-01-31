"""Emission of original model symbols (Sets, Aliases, Parameters).

This module emits GAMS declarations for the original model symbols using
actual IR fields (Finding #3 from final review).

Key principles:
- Use SetDef.members (not .elements)
- Use ParameterDef.domain and .values (not invented fields)
- Use AliasDef.target and .universe
- Scalars have empty domain () and values[()] = value
- Multi-dimensional parameter keys formatted as GAMS syntax: ("i1", "j2") → "i1.j2"
- Emit computed parameter assignments as GAMS statements (Sprint 17 Day 4)
"""

import re

from src.emit.expr_to_gams import expr_to_gams
from src.ir.constants import PREDEFINED_GAMS_CONSTANTS
from src.ir.model_ir import ModelIR

# Regex pattern for valid GAMS set element identifiers
# Allows: letters, digits, underscores, hyphens, dots (for tuples like a.b), plus signs
# Must start with letter or digit
# Note: Dots are allowed because they represent tuple notation in GAMS (e.g., upper.egypt).
# Plus signs are allowed because GAMS uses them in composite names (e.g., food+agr, pulp+paper).
# These characters cannot break out of the /.../ block - that requires / or ; which are blocked.
_VALID_SET_ELEMENT_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_\-\.+]*$")


def _sanitize_set_element(element: str) -> str:
    """Sanitize a set element name for safe GAMS emission.

    Validates that the element contains only safe characters to prevent
    DSL injection attacks. Elements that could break out of the /.../ block
    or inject GAMS statements are rejected.

    Args:
        element: Set element identifier

    Returns:
        The element if valid, or a safely quoted version

    Raises:
        ValueError: If the element contains characters that cannot be safely emitted
    """
    # Check for obviously dangerous characters that could break GAMS syntax
    # These characters could allow escaping the /.../ block or injecting statements
    dangerous_chars = {"/", ";", "*", "$", '"', "'", "(", ")", "[", "]", "=", "<", ">"}

    if any(c in element for c in dangerous_chars):
        raise ValueError(
            f"Set element '{element}' contains unsafe characters that could cause "
            f"GAMS injection. Dangerous characters: {dangerous_chars & set(element)}"
        )

    # Validate against safe pattern
    if not _VALID_SET_ELEMENT_PATTERN.match(element):
        raise ValueError(
            f"Set element '{element}' contains invalid characters. "
            f"Set elements must start with a letter or digit and contain only "
            f"letters, digits, underscores, hyphens, dots, and plus signs."
        )

    return element


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
        # Sanitize each member to prevent DSL injection attacks
        if set_def.members:
            sanitized_members = [_sanitize_set_element(m) for m in set_def.members]
            members = ", ".join(sanitized_members)
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

    # Emit Scalars (skip predefined GAMS constants and description-only entries)
    if scalars:
        # Filter out predefined constants and description-only entries
        # Description-only entries occur when the parser stores description strings
        # as scalar names (e.g., 'loss equation constant' instead of a proper identifier).
        # These contain spaces, quotes, or other invalid identifier characters.
        def is_valid_scalar_name(name: str) -> bool:
            """Check if scalar name is a valid GAMS identifier.

            Valid GAMS identifiers:
            - Start with a letter or underscore
            - Contain only letters, digits, and underscores
            Additionally, reject any whitespace, newlines, or GAMS delimiters.
            """
            if not name:
                return False
            # Reject any whitespace (including spaces, tabs, newlines) or quote characters
            if re.search(r"\s", name) or "'" in name or '"' in name:
                return False
            # Explicitly reject GAMS delimiters that could break syntax blocks
            if "/" in name or ";" in name:
                return False
            # Full-pattern check: first char letter or underscore, rest letters/digits/underscores
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                return False
            return True

        user_scalars = {
            name: param_def
            for name, param_def in scalars.items()
            if name not in PREDEFINED_GAMS_CONSTANTS and is_valid_scalar_name(name)
        }
        if user_scalars:
            if lines:  # Add blank line if parameters were emitted
                lines.append("")
            lines.append("Scalars")
            for scalar_name, scalar_def in user_scalars.items():
                # Scalars have values[()] = value (Finding #3)
                value = scalar_def.values.get((), 0.0)
                lines.append(f"    {scalar_name} /{value}/")
            lines.append(";")

    return "\n".join(lines)


def emit_computed_parameter_assignments(model_ir: ModelIR) -> str:
    """Emit computed parameter assignment statements.

    Sprint 17 Day 4: Emit expressions stored in ParameterDef.expressions as
    GAMS assignment statements. These are computed parameters like:
        c(i,j) = f*d(i,j)/1000;
        gplus(c) = gibbs(c) + log(750*.07031);

    Args:
        model_ir: Model IR containing parameter definitions with expressions

    Returns:
        GAMS assignment statements as string

    Example output:
        c(i,j) = f * d(i,j) / 1000;
        gplus(c) = gibbs(c) + log(750 * 0.07031);
    """
    lines: list[str] = []

    for param_name, param_def in model_ir.params.items():
        # Skip predefined constants
        if param_name in PREDEFINED_GAMS_CONSTANTS:
            continue

        # Check if this parameter has expressions (computed values)
        if not param_def.expressions:
            continue

        # Emit each expression assignment
        for key_tuple, expr in param_def.expressions.items():
            # Convert expression to GAMS syntax
            expr_str = expr_to_gams(expr)

            # Format the LHS with indices
            if key_tuple:
                # Indexed parameter: c(i,j) = expr
                index_str = ",".join(key_tuple)
                lines.append(f"{param_name}({index_str}) = {expr_str};")
            else:
                # Scalar parameter: f = expr
                lines.append(f"{param_name} = {expr_str};")

    return "\n".join(lines)

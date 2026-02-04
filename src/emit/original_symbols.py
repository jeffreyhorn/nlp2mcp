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
from src.ir.symbols import SetDef

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


def _format_set_declaration(set_name: str, set_def: "SetDef") -> str:
    """Format a single set declaration line.

    Args:
        set_name: Name of the set
        set_def: SetDef object with members and domain

    Returns:
        Formatted set declaration line (without leading spaces)
    """
    # Format set declaration with optional domain (subset relationship)
    # E.g., cg(genchar) for subset cg of genchar
    if set_def.domain:
        domain_str = ",".join(set_def.domain)
        set_decl = f"{set_name}({domain_str})"
    else:
        set_decl = set_name

    # Use SetDef.members
    # Members are stored as a list of strings in SetDef
    # Sanitize each member to prevent DSL injection attacks
    if set_def.members:
        sanitized_members = [_sanitize_set_element(m) for m in set_def.members]
        members = ", ".join(sanitized_members)
        return f"{set_decl} /{members}/"
    else:
        # Empty set or universe (or subset with inherited members)
        return set_decl


def _compute_set_alias_phases(
    model_ir: ModelIR,
) -> tuple[set[str], set[str], set[str]]:
    """Compute emission phases for sets based on dependencies.

    This function partitions sets into phases to ensure correct declaration order.
    A set must be declared before it can be referenced.

    Emission order:
    1. Phase 1 sets: Sets with no alias dependencies (directly or transitively)
    2. Phase 1 aliases: Aliases targeting phase 1 sets
    3. Phase 2 sets: Sets depending on phase 1 aliases (directly or transitively)
    4. Phase 2 aliases: Aliases targeting phase 2 sets
    5. Phase 3 sets: Sets depending on phase 2 aliases (directly or transitively)
    6. Phase 3 aliases: Aliases targeting phase 3 sets

    Args:
        model_ir: Model IR containing set and alias definitions

    Returns:
        Tuple of (phase1_sets, phase2_sets, phase3_sets) as lowercase name sets.
    """
    if not model_ir.sets:
        return set(), set(), set()

    # Get all alias names and build alias target map (lowercase for case-insensitive comparison)
    alias_names_lower = (
        {name.lower() for name in model_ir.aliases.keys()} if model_ir.aliases else set()
    )
    # Map: alias_name (lower) -> target_set_name (lower)
    alias_targets: dict[str, str] = {}
    if model_ir.aliases:
        for alias_name, alias_def in model_ir.aliases.items():
            alias_targets[alias_name.lower()] = alias_def.target.lower()

    # Build a map of set name (lowercase) -> domain indices (lowercase)
    set_domains: dict[str, set[str]] = {}
    for set_name, set_def in model_ir.sets.items():
        set_domains[set_name.lower()] = {idx.lower() for idx in set_def.domain}

    all_set_names = set(set_domains.keys())

    # First, identify sets that directly depend on aliases
    sets_with_alias_deps: set[str] = set()
    for set_name_lower, domain_indices in set_domains.items():
        if domain_indices & alias_names_lower:
            sets_with_alias_deps.add(set_name_lower)

    # Compute transitive closure: sets depending on alias-dependent sets are also alias-dependent
    changed = True
    while changed:
        changed = False
        for set_name_lower, domain_indices in set_domains.items():
            if set_name_lower not in sets_with_alias_deps:
                # Check if depends on any alias-dependent set
                if domain_indices & sets_with_alias_deps:
                    sets_with_alias_deps.add(set_name_lower)
                    changed = True

    # Phase 1: Sets with no alias dependencies (directly or transitively)
    phase1_sets = all_set_names - sets_with_alias_deps

    # Phase 1 aliases: Aliases targeting phase 1 sets
    phase1_alias_names: set[str] = set()
    for alias_name_lower, target_lower in alias_targets.items():
        if target_lower in phase1_sets:
            phase1_alias_names.add(alias_name_lower)

    # Phase 2 sets: Sets depending on phase 1 aliases (directly or transitively through other phase 2 sets)
    phase2_sets: set[str] = set()
    for set_name_lower, domain_indices in set_domains.items():
        if set_name_lower in phase1_sets:
            continue
        # Check if depends on any phase 1 alias
        if domain_indices & phase1_alias_names:
            phase2_sets.add(set_name_lower)

    # Compute transitive closure for phase 2
    changed = True
    while changed:
        changed = False
        for set_name_lower, domain_indices in set_domains.items():
            if set_name_lower in phase1_sets or set_name_lower in phase2_sets:
                continue
            # Check if depends on any phase 2 set
            if domain_indices & phase2_sets:
                phase2_sets.add(set_name_lower)
                changed = True

    # Phase 3 sets: Everything else (depends on phase 2 aliases)
    phase3_sets = all_set_names - phase1_sets - phase2_sets

    return phase1_sets, phase2_sets, phase3_sets


def emit_original_sets(model_ir: ModelIR) -> tuple[str, str, str]:
    """Emit Sets blocks from original model, split by alias dependencies.

    Uses SetDef.members and SetDef.domain (Finding #3: actual IR fields).
    Sprint 17 Day 5: Now preserves subset relationships by emitting domain.
    Sprint 17 Day 10: Splits sets into three phases to handle complex alias
    dependencies (GitHub Issue #621).

    Emission order ensures all dependencies are declared before use:
    1. Phase 1 sets: Sets with no alias dependencies
    2. Phase 1 aliases (emitted by emit_original_aliases)
    3. Phase 2 sets: Sets depending on phase 1 aliases
    4. Phase 2 aliases (emitted by emit_original_aliases)
    5. Phase 3 sets: Sets depending on phase 2 aliases

    Args:
        model_ir: Model IR containing set definitions

    Returns:
        Tuple of (phase1_sets, phase2_sets, phase3_sets) as GAMS code strings.

    Example output for phase1_sets:
        Sets
            i /i1, i2, i3/
        ;

    Example output for phase2_sets:
        Sets
            ij(i,j)
        ;
    """
    if not model_ir.sets:
        return "", "", ""

    # Compute which sets go in each phase
    phase1_names, phase2_names, phase3_names = _compute_set_alias_phases(model_ir)

    # Partition sets into lists preserving original order
    phase1_sets: list[tuple[str, SetDef]] = []
    phase2_sets: list[tuple[str, SetDef]] = []
    phase3_sets: list[tuple[str, SetDef]] = []

    for set_name, set_def in model_ir.sets.items():
        set_name_lower = set_name.lower()
        if set_name_lower in phase1_names:
            phase1_sets.append((set_name, set_def))
        elif set_name_lower in phase2_names:
            phase2_sets.append((set_name, set_def))
        else:
            phase3_sets.append((set_name, set_def))

    def build_sets_block(sets_list: list[tuple[str, SetDef]]) -> str:
        if not sets_list:
            return ""
        lines: list[str] = ["Sets"]
        for set_name, set_def in sets_list:
            lines.append(f"    {_format_set_declaration(set_name, set_def)}")
        lines.append(";")
        return "\n".join(lines)

    return (
        build_sets_block(phase1_sets),
        build_sets_block(phase2_sets),
        build_sets_block(phase3_sets),
    )


def emit_original_aliases(model_ir: ModelIR) -> tuple[str, str, str]:
    """Emit Alias declarations, split by target set dependencies.

    Uses AliasDef.target and .universe (Finding #3: actual IR fields).

    Sprint 17 Day 10: Splits aliases into three groups matching the set phases:
    - Phase 1 aliases: Target is a phase 1 set (emitted after phase 1 sets)
    - Phase 2 aliases: Target is a phase 2 set (emitted after phase 2 sets)
    - Phase 3 aliases: Target is a phase 3 set (emitted after phase 3 sets)

    Args:
        model_ir: Model IR containing alias definitions

    Returns:
        Tuple of (phase1_aliases, phase2_aliases, phase3_aliases) as GAMS code strings.
        Phase 1 aliases target sets in phase 1 (no alias dependencies).
        Phase 2 aliases target sets in phase 2 (depend on phase 1 aliases).
        Phase 3 aliases target sets in phase 3 (depend on phase 2 aliases).

    Example output:
        Alias(i, ip);
        Alias(j, jp);
    """
    if not model_ir.aliases:
        return "", "", ""

    # Get set names for each phase
    phase1_set_names, phase2_set_names, phase3_set_names = _compute_set_alias_phases(model_ir)

    phase1_aliases: list[str] = []
    phase2_aliases: list[str] = []
    phase3_aliases: list[str] = []

    for alias_name, alias_def in model_ir.aliases.items():
        alias_line = f"Alias({alias_def.target}, {alias_name});"
        target_lower = alias_def.target.lower()
        # Check which phase the alias target belongs to
        if target_lower in phase3_set_names:
            phase3_aliases.append(alias_line)
        elif target_lower in phase2_set_names:
            phase2_aliases.append(alias_line)
        else:
            phase1_aliases.append(alias_line)

    phase1_code = "\n".join(phase1_aliases) if phase1_aliases else ""
    phase2_code = "\n".join(phase2_aliases) if phase2_aliases else ""
    phase3_code = "\n".join(phase3_aliases) if phase3_aliases else ""

    return phase1_code, phase2_code, phase3_code


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

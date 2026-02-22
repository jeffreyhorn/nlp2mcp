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

import logging
import re

from src.emit.expr_to_gams import expr_to_gams
from src.ir.ast import Call, Expr, MultiplierRef, ParamRef, VarRef
from src.ir.constants import GAMS_RESERVED_CONSTANTS, PREDEFINED_GAMS_CONSTANTS
from src.ir.model_ir import ModelIR
from src.ir.symbols import SetDef

logger = logging.getLogger(__name__)

# GAMS functions that produce stochastic (non-deterministic) output.
# When these appear in parameter assignments within MCP files, the model
# becomes non-deterministic — each solve produces different data, making
# the KKT conditions inconsistent.
STOCHASTIC_FUNCTIONS: frozenset[str] = frozenset(
    {
        "uniform",
        "normal",
        "uniformint",
        "triangular",
        "binomial",
        "beta",
        "gamma",
        "lognormal",
        "negbinomial",
        "poisson",
        "rand",
        "randsign",
        "heaprandom",
    }
)


def _expr_contains_stochastic(expr: Expr) -> bool:
    """Return True if *expr* contains a call to a stochastic function."""
    if isinstance(expr, Call) and expr.func.lower() in STOCHASTIC_FUNCTIONS:
        return True
    return any(_expr_contains_stochastic(c) for c in expr.children())


def has_stochastic_parameters(model_ir: ModelIR) -> bool:
    """Return True if any computed parameter contains a stochastic function call."""
    for param_name, param_def in model_ir.params.items():
        if param_name in PREDEFINED_GAMS_CONSTANTS:
            continue
        for _key, expr in param_def.expressions:
            if _expr_contains_stochastic(expr):
                return True
    return False


# Regex pattern for valid GAMS set element identifiers
# Allows: letters, digits, underscores, hyphens, dots (for tuples like a.b), plus signs
# Must start with letter or digit
# Note: Dots are allowed because they represent tuple notation in GAMS (e.g., upper.egypt).
# Plus signs are allowed because GAMS uses them in composite names (e.g., food+agr, pulp+paper).
# These characters cannot break out of the /.../ block - that requires / or ; which are blocked.
_VALID_SET_ELEMENT_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_\-\.+]*$")

# Valid unescaped GAMS symbol identifier: starts with letter/underscore, contains only
# letters, digits, and underscores. Dots are allowed as they represent tuple notation.
_VALID_UNESCAPED_SYMBOL_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$")


def _needs_quoting(element: str) -> bool:
    """Determine if a set element or symbol name needs quoting in GAMS.

    A symbol needs quoting if it doesn't match the valid unescaped GAMS identifier
    pattern: must start with a letter or underscore, and contain only letters,
    digits, and underscores (dots are allowed for tuple notation like x.i).

    This catches:
    - Names starting with a digit (e.g., '20foo')
    - Names containing '+' or '-' (interpreted as operators)
    - Names containing whitespace
    - Names containing other special characters (e.g., '%', '@')

    Args:
        element: Set element or symbol identifier

    Returns:
        True if the element/name needs quoting, False otherwise
    """
    # Empty strings don't need quoting (shouldn't happen, but be safe)
    if not element:
        return False
    # Quote anything that doesn't match the valid unescaped identifier pattern
    return not _VALID_UNESCAPED_SYMBOL_PATTERN.match(element)


def _quote_symbol(name: str) -> str:
    """Quote a symbol name if it contains special characters.

    Issue #665: Symbol names (sets, parameters, variables, aliases) containing
    special characters like '-' or '+' must be quoted in emitted GAMS to avoid
    syntax errors. The parser strips quotes from escaped identifiers, so the
    emitter must re-quote them for valid GAMS output.

    Also validates that symbol names don't contain dangerous characters that
    could break GAMS syntax or enable injection attacks.

    Args:
        name: Symbol name to potentially quote

    Returns:
        The name quoted if necessary, otherwise unchanged

    Raises:
        ValueError: If the name contains characters that cannot be safely emitted
    """
    # Validate: reject characters that could break GAMS syntax or enable injection
    # Single quotes would break our quoting, semicolons/slashes could inject statements
    dangerous_chars = {"'", '"', ";", "/", "\n", "\r", "\t"}
    if any(c in name for c in dangerous_chars):
        raise ValueError(
            f"Symbol name '{name}' contains unsafe characters that could cause "
            f"GAMS injection. Dangerous characters: {dangerous_chars & set(name)}"
        )

    # Special case: wildcard '*' should never be quoted
    if name == "*":
        return name
    return f"'{name}'" if _needs_quoting(name) else name


def _sanitize_set_element(element: str) -> str:
    """Sanitize a set element name for safe GAMS emission.

    Validates that the element contains only safe characters to prevent
    DSL injection attacks. Elements that could break out of the /.../ block
    or inject GAMS statements are rejected. Elements with special characters
    (like + or -) are quoted for correct GAMS parsing.

    Handles pre-quoted elements from the parser: if the element is already
    wrapped in single quotes, it's validated and returned as-is. Quoted
    elements may contain spaces (e.g., 'SAE 10' from bearing.gms).

    Args:
        element: Set element identifier (may or may not be pre-quoted)

    Returns:
        The element (quoted if necessary) if valid

    Raises:
        ValueError: If the element contains characters that cannot be safely emitted
    """
    # Strip surrounding whitespace that may come from table row labels
    element = element.strip()

    # Normalize doubled single quotes to single quotes
    # The parser sometimes produces ''label'' instead of 'label'
    # (e.g., ''SAE 10'', ''max-stock'' from bearing/robert models)
    if len(element) >= 4 and element.startswith("''") and element.endswith("''"):
        element = "'" + element[2:-2] + "'"

    # Handle pre-quoted elements from the parser
    # If element is already wrapped in single quotes, strip them for validation
    # and return with quotes preserved
    is_prequoted = len(element) >= 2 and element.startswith("'") and element.endswith("'")
    if is_prequoted:
        inner = element[1:-1]
        # Validate the inner content (should not have additional quotes, control chars, or dangerous chars)
        # Note: spaces are allowed in quoted GAMS labels (e.g., 'SAE 10')
        control_chars_inner = {"\n", "\r", "\t"}
        if any(c in inner for c in control_chars_inner):
            raise ValueError(
                f"Set element '{element}' contains control characters that could break GAMS syntax. "
                f"Disallowed control characters: {control_chars_inner & set(inner)}"
            )
        dangerous_chars_inner = {"/", ";", "*", "$", '"', "'", "(", ")", "[", "]", "=", "<", ">"}
        if any(c in inner for c in dangerous_chars_inner):
            raise ValueError(
                f"Set element '{element}' contains unsafe characters that could cause "
                f"GAMS injection. Dangerous characters: {dangerous_chars_inner & set(inner)}"
            )
        # For quoted elements, we allow spaces and other characters that GAMS permits
        # in quoted labels. Only check for truly dangerous injection characters and control chars above.
        # Return as-is (already quoted)
        return element

    # Check for obviously dangerous characters that could break GAMS syntax
    # These characters could allow escaping the /.../ block or injecting statements
    dangerous_chars = {"/", ";", "*", "$", '"', "'", "(", ")", "[", "]", "=", "<", ">"}

    if any(c in element for c in dangerous_chars):
        raise ValueError(
            f"Set element '{element}' contains unsafe characters that could cause "
            f"GAMS injection. Dangerous characters: {dangerous_chars & set(element)}"
        )

    # Check if element needs quoting (spaces, +, -)
    # Elements with spaces (e.g., 'SAE 10' stripped to 'SAE 10') need re-quoting
    if _needs_quoting(element):
        # Validate that the element is safe to quote (no dangerous chars)
        # Note: we already checked dangerous_chars above
        # For quoted elements, we only need to ensure no control chars
        control_chars = {"\n", "\r", "\t"}
        if any(c in element for c in control_chars):
            raise ValueError(
                f"Set element '{element}' contains control characters that could break GAMS syntax."
            )
        return f"'{element}'"

    # Validate against safe pattern for unquoted elements
    if not _VALID_SET_ELEMENT_PATTERN.match(element):
        raise ValueError(
            f"Set element '{element}' contains invalid characters. "
            f"Set elements must start with a letter or digit and contain only "
            f"letters, digits, underscores, hyphens, dots, and plus signs."
        )

    # Sprint 19 Day 2: GAMS reserved constants (inf, na, eps, etc.) must be quoted
    # when used as set elements, otherwise GAMS interprets them as special values.
    if element.lower() in GAMS_RESERVED_CONSTANTS:
        return f"'{element}'"

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
    # Quote symbol names that contain special characters (Issue #665)
    quoted_name = _quote_symbol(set_name)
    if set_def.domain:
        quoted_domain = [_quote_symbol(d) for d in set_def.domain]
        domain_str = ",".join(quoted_domain)
        set_decl = f"{quoted_name}({domain_str})"
    else:
        set_decl = quoted_name

    # Use SetDef.members
    # Members are stored as a list of strings in SetDef
    # Sanitize each member to prevent DSL injection attacks
    # For multi-dimensional sets (domain has multiple elements), members are stored
    # as dot-separated tuples (e.g., "c-cracker.ho-low-s"). We need to split on '.'
    # and sanitize each component separately to avoid quoting the entire tuple.
    if set_def.members:
        domain_arity = len(set_def.domain) if set_def.domain else 1
        if domain_arity > 1:
            # Multi-dimensional set: split members and sanitize each component
            sanitized_members = []
            for m in set_def.members:
                components = m.split(".")
                # Handle case where number of components doesn't match domain arity
                # (shouldn't happen, but be defensive)
                if len(components) == domain_arity:
                    sanitized_components = [_sanitize_set_element(c) for c in components]
                    sanitized_members.append(".".join(sanitized_components))
                else:
                    # Fallback: sanitize as single element
                    sanitized_members.append(_sanitize_set_element(m))
        else:
            # Single-dimensional set: sanitize directly
            sanitized_members = [_sanitize_set_element(m) for m in set_def.members]
        members = ", ".join(sanitized_members)
        return f"{set_decl} /{members}/"
    else:
        # Empty set or universe (or subset with inherited members)
        return set_decl


def _compute_set_alias_phases(
    model_ir: ModelIR,
) -> tuple[dict[str, int], dict[str, int]]:
    """Compute emission phases for sets and aliases based on dependencies.

    This function assigns phases to sets and aliases to ensure correct declaration
    order. A set must be declared before it can be referenced. Uses an iterative,
    dependency-aware algorithm that assigns phases based on actual dependencies.

    Emission order for each phase p:
    1. Phase p sets
    2. Phase p aliases (targeting phase p sets)

    The algorithm iteratively assigns phases such that:
    - An alias can be assigned to phase p if its target set is in a phase <= p.
    - A set can be assigned to phase p if all its domain indices refer only to
      sets/aliases already assigned to phases < p (for aliases) or <= p (for sets).

    Args:
        model_ir: Model IR containing set and alias definitions

    Returns:
        Tuple of (set_phases, alias_phases) as dicts mapping lowercase names to phase numbers.
    """
    if not model_ir.sets:
        return {}, {}

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
    alias_names_lower = set(alias_targets.keys())

    # Validate that all alias targets refer to existing sets or other aliases.
    # Without this check, an alias targeting a non-existent symbol would remain
    # unassigned and trigger a misleading "Circular dependency" error.
    all_known_symbols = all_set_names | alias_names_lower
    for alias_name_lower, target_lower in alias_targets.items():
        if target_lower not in all_known_symbols:
            raise ValueError(
                f"Alias '{alias_name_lower}' targets non-existent symbol '{target_lower}'. "
                f"Expected a set or another alias."
            )

    # Phase 1 sets: Sets with no alias dependencies (directly or transitively)
    # First, identify sets that directly depend on aliases
    sets_with_alias_deps: set[str] = set()
    for set_name_lower, domain_indices in set_domains.items():
        if domain_indices & alias_names_lower:
            sets_with_alias_deps.add(set_name_lower)

    # Compute transitive closure: sets depending on alias-dependent sets
    changed = True
    while changed:
        changed = False
        for set_name_lower, domain_indices in set_domains.items():
            if set_name_lower not in sets_with_alias_deps:
                if domain_indices & sets_with_alias_deps:
                    sets_with_alias_deps.add(set_name_lower)
                    changed = True

    phase1_sets = all_set_names - sets_with_alias_deps

    # Initialize phase tracking for iterative assignment
    set_phases: dict[str, int] = dict.fromkeys(phase1_sets, 1)
    alias_phases: dict[str, int] = {}

    # Phase 1 aliases: aliases targeting phase 1 sets
    for alias_name_lower, target_lower in alias_targets.items():
        if target_lower in phase1_sets:
            alias_phases[alias_name_lower] = 1

    unassigned_sets = all_set_names - phase1_sets
    unassigned_aliases = alias_names_lower - set(alias_phases.keys())

    # Iterative, dependency-aware phase assignment
    # Upper bound: each symbol can require at most one additional phase
    max_phases = len(all_set_names) + len(alias_names_lower) + 1
    phase = 2
    while (unassigned_sets or unassigned_aliases) and phase <= max_phases:
        progressed = True
        while progressed:
            progressed = False

            # Assign aliases whose target is already in a phase <= current phase.
            # The target may be a set OR another alias (alias chains).
            for alias_name_lower in list(unassigned_aliases):
                target_lower = alias_targets[alias_name_lower]
                target_phase = set_phases.get(target_lower)
                if target_phase is None:
                    # Target might be another alias (alias chain)
                    target_phase = alias_phases.get(target_lower)
                if target_phase is not None and target_phase <= phase:
                    alias_phases[alias_name_lower] = phase
                    unassigned_aliases.remove(alias_name_lower)
                    progressed = True

            # Assign sets whose domain indices only reference resolved deps
            for set_name_lower in list(unassigned_sets):
                domain_indices = set_domains.get(set_name_lower, set())

                def _index_resolved(idx: str, current_phase: int = phase) -> bool:
                    # Resolution order: check sets first, then aliases.
                    # GAMS enforces that set and alias names are unique within a
                    # model, so an index cannot match both set_phases and
                    # alias_targets simultaneously.
                    if idx in set_phases:
                        return set_phases[idx] <= current_phase
                    # If index is an alias, it must be in a STRICTLY EARLIER phase
                    # because aliases in phase p are emitted AFTER phase p sets,
                    # so sets depending on phase p aliases must be in phase p+1 or later
                    if idx in alias_targets:
                        alias_phase = alias_phases.get(idx)
                        return alias_phase is not None and alias_phase < current_phase
                    # Unrecognized indices are conservatively treated as resolved
                    # (they may be predefined GAMS sets or external references)
                    return True

                if all(_index_resolved(idx) for idx in domain_indices):
                    set_phases[set_name_lower] = phase
                    unassigned_sets.remove(set_name_lower)
                    progressed = True

        phase += 1

    # If any symbols remain unassigned, there's a circular dependency
    if unassigned_sets or unassigned_aliases:
        raise ValueError(
            f"Circular dependency detected in sets/aliases; "
            f"cannot safely order GAMS emission. "
            f"Unassigned sets: {unassigned_sets}, aliases: {unassigned_aliases}"
        )

    return set_phases, alias_phases


def emit_original_sets(
    model_ir: ModelIR,
    precomputed_phases: tuple[dict[str, int], dict[str, int]] | None = None,
) -> list[str]:
    """Emit Sets blocks from original model, split by alias dependencies.

    Uses SetDef.members and SetDef.domain (Finding #3: actual IR fields).
    Sprint 17 Day 5: Now preserves subset relationships by emitting domain.
    Sprint 17 Day 10: Splits sets into phases to handle complex alias
    dependencies (GitHub Issue #621). Supports N phases dynamically.

    Emission order ensures all dependencies are declared before use:
    - Phase 1 sets: Sets with no alias dependencies
    - Phase 1 aliases (emitted by emit_original_aliases)
    - Phase 2 sets: Sets depending on phase 1 aliases
    - Phase 2 aliases (emitted by emit_original_aliases)
    - ... continues for all phases as needed

    Args:
        model_ir: Model IR containing set definitions
        precomputed_phases: Optional pre-computed (set_phases, alias_phases) tuple
            from _compute_set_alias_phases to avoid redundant computation.

    Returns:
        List of GAMS code strings, one per phase, indexed from 0.
        Index 0 = phase 1 sets, index 1 = phase 2 sets, etc.

    Example output for phase 1:
        Sets
            i /i1, i2, i3/
        ;
    """
    if not model_ir.sets:
        return []

    # Compute which sets go in each phase (or use pre-computed result)
    if precomputed_phases is not None:
        set_phases, _ = precomputed_phases
    else:
        set_phases, _ = _compute_set_alias_phases(model_ir)

    if not set_phases:
        return []

    # Determine number of phases (set_phases is guaranteed non-empty by early return above)
    max_phase = max(set_phases.values())

    # Partition sets into lists by phase, preserving original order
    phase_sets: list[list[tuple[str, SetDef]]] = [[] for _ in range(max_phase)]

    for set_name, set_def in model_ir.sets.items():
        set_name_lower = set_name.lower()
        phase = set_phases.get(set_name_lower, 1)
        phase_sets[phase - 1].append((set_name, set_def))

    def build_sets_block(sets_list: list[tuple[str, SetDef]]) -> str:
        if not sets_list:
            return ""
        lines: list[str] = ["Sets"]
        for set_name, set_def in sets_list:
            lines.append(f"    {_format_set_declaration(set_name, set_def)}")
        lines.append(";")
        return "\n".join(lines)

    return [build_sets_block(sets_list) for sets_list in phase_sets]


def emit_original_aliases(
    model_ir: ModelIR,
    precomputed_phases: tuple[dict[str, int], dict[str, int]] | None = None,
) -> list[str]:
    """Emit Alias declarations, split by target set dependencies.

    Uses AliasDef.target and .universe (Finding #3: actual IR fields).

    Sprint 17 Day 10: Splits aliases into phases matching the set phases:
    - Phase p aliases: Aliases targeting phase p sets (emitted after phase p sets)

    Args:
        model_ir: Model IR containing alias definitions
        precomputed_phases: Optional pre-computed (set_phases, alias_phases) tuple
            from _compute_set_alias_phases to avoid redundant computation.

    Returns:
        List of GAMS code strings, one per phase, indexed from 0.
        Index 0 = phase 1 aliases, index 1 = phase 2 aliases, etc.

    Example output:
        Alias(i, ip);
        Alias(j, jp);
    """
    if not model_ir.aliases:
        return []

    # Get phase assignments (or use pre-computed result)
    if precomputed_phases is not None:
        set_phases, alias_phases = precomputed_phases
    else:
        set_phases, alias_phases = _compute_set_alias_phases(model_ir)

    if not alias_phases:
        return []

    # Determine number of phases (use set_phases to include all phases)
    max_phase = max(
        max(set_phases.values()) if set_phases else 0,
        max(alias_phases.values()) if alias_phases else 0,
    )

    # Partition aliases into lists by phase
    phase_aliases: list[list[str]] = [[] for _ in range(max_phase)]

    for alias_name, alias_def in model_ir.aliases.items():
        # Quote symbol names that contain special characters (Issue #665)
        alias_line = f"Alias({_quote_symbol(alias_def.target)}, {_quote_symbol(alias_name)});"
        alias_name_lower = alias_name.lower()
        phase = alias_phases.get(alias_name_lower, 1)
        phase_aliases[phase - 1].append(alias_line)

    return ["\n".join(aliases) if aliases else "" for aliases in phase_aliases]


def _expand_table_key(key_tuple: tuple[str, ...], domain_size: int) -> tuple[str, ...] | None:
    """Expand a table data key to match the expected domain size.

    Table parser stores data as 2-tuples (row_header, col_header) where row_header
    may be a dotted string representing multiple dimensions (e.g., 'low.a.distr').
    This function expands such keys to match the full domain size.

    For example:
        key_tuple = ('low.a.distr', 'light-ind')
        domain_size = 4
        -> ('low', 'a', 'distr', 'light-ind')

    Args:
        key_tuple: Original key tuple from parameter values
        domain_size: Expected number of dimensions from domain

    Returns:
        Expanded key tuple matching domain_size, or None if the key cannot be
        expanded to match (indicating an invalid/malformed entry that should be skipped)
    """
    # If the key already has the correct arity, return it as-is.
    if len(key_tuple) == domain_size:
        return key_tuple
    # Keys with more elements than the domain size are malformed.
    if len(key_tuple) > domain_size:
        return None

    # Need to expand: split dotted elements until we reach domain_size
    expanded: list[str] = []
    for element in key_tuple:
        if len(expanded) < domain_size and "." in element:
            # Split this element on dots
            parts = element.split(".")
            expanded.extend(parts)
        else:
            expanded.append(element)

    # If we don't have exactly domain_size elements, this entry is malformed
    # (e.g., zero-fill entries from parser that don't have proper row labels)
    if len(expanded) != domain_size:
        return None

    return tuple(expanded)


def emit_original_parameters(model_ir: ModelIR) -> str:
    """Emit Parameters and Scalars with their data.

    Uses ParameterDef.domain and .values (Finding #3: actual IR fields).
    Scalars have empty domain () and values[()] = value.
    Multi-dimensional keys formatted as GAMS syntax: ("i1", "j2") → "i1.j2".

    Wildcard domains (*) are preserved as-is in the declaration. This matches
    the original GAMS behavior and allows any set to be used for indexing.
    (Issue #679: replacing wildcards with named sets caused E171 domain violations
    when the original code used subset indexing.)

    Args:
        model_ir: Model IR containing parameter definitions

    Returns:
        GAMS Parameters and Scalars blocks as string

    Example output:
        Parameters
            c(i,j) /i1.j1 2.5, i1.j2 3.0, i2.j1 1.8/
            dat(i,*) /1.y 127.0, 1.x -5.0/
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
            # Issue #675: Skip parameters declared without domain but used with indices.
            # These are "dynamically typed" report parameters like:
            #   Parameter report;
            #   report('x1','global') = 1;
            #   report('x1','solver') = x1.l;
            # GAMS allows this but emitting as scalar causes Error 148 (dimension mismatch).
            # Check if values or expressions have indexed keys (non-empty tuples).
            has_indexed_values = any(len(k) > 0 for k in param_def.values.keys())
            has_indexed_exprs = param_def.expressions and any(
                len(k) > 0 for k, _expr in param_def.expressions
            )
            if has_indexed_values or has_indexed_exprs:
                # Skip this parameter entirely - it's a report parameter that can't be
                # properly emitted without proper domain declaration.
                # Warn in case the parameter is actually needed for optimization.
                logger.warning(
                    "Skipping parameter '%s': declared without domain but used with "
                    "indexed values/expressions. If this parameter is used in the "
                    "optimization model (not just post-solve reporting), the generated "
                    "MCP will be invalid.",
                    param_name,
                )
                continue
            scalars[param_name] = param_def
        else:
            parameters[param_name] = param_def

    lines = []

    # Issue #679: Keep wildcard domains as '*' instead of replacing with named sets
    # Rationale: When the original GAMS code declares a parameter with wildcard domain
    # like `Table compdat(*,alloy)`, it may index the parameter using different sets:
    #   - compdat(elem,alloy) where elem = {lead, zinc, tin}
    #   - compdat("price",alloy) for a specific element
    # If we replace '*' with a generated set wc_compdat_d1 = {lead, zinc, tin, price},
    # then indexing via `elem` causes E171 "Domain violation for set" because GAMS
    # requires the indexing set to be compatible with (subset of or equal to) the
    # declared domain set.
    # Solution: Keep wildcards as '*' in the domain declaration, which allows any
    # set or element to be used for indexing, matching the original GAMS behavior.

    # Emit Parameters
    if parameters:
        lines.append("Parameters")
        for param_name, param_def in parameters.items():
            domain = list(param_def.domain)

            # Use ParameterDef.values (Finding #3)
            # Format tuple keys as GAMS syntax: ("i1", "j2") → "i1.j2"
            if param_def.values:
                domain_size = len(domain)
                data_parts = []
                for key_tuple, value in param_def.values.items():
                    # Expand key to match domain size (handles table data with dotted row headers)
                    expanded_key = _expand_table_key(key_tuple, domain_size)

                    # Skip malformed entries (e.g., zero-fill entries with wrong dimensions)
                    if expanded_key is None:
                        continue

                    # Convert tuple to GAMS index syntax (Finding #3)
                    # Apply quoting/sanitization to each element for consistent handling
                    # This ensures parameter data keys match set element quoting
                    sanitized_keys = [_sanitize_set_element(k) for k in expanded_key]
                    key_str = ".".join(sanitized_keys)
                    data_parts.append(f"{key_str} {value}")

                # Quote symbol names that contain special characters (Issue #665)
                quoted_domain = [_quote_symbol(d) for d in domain]
                domain_str = ",".join(quoted_domain)
                if data_parts:
                    # Emit parameter with data
                    data_str = ", ".join(data_parts)
                    lines.append(f"    {_quote_symbol(param_name)}({domain_str}) /{data_str}/")
                else:
                    # All data entries were filtered out as malformed - emit declaration only
                    lines.append(f"    {_quote_symbol(param_name)}({domain_str})")
            else:
                # Parameter declared but no data - must have domain since
                # parameters dict only contains entries with non-empty domain
                # (PR #658 review: removed scalar-with-indexed-expressions promotion)
                quoted_domain = [_quote_symbol(d) for d in domain]
                domain_str = ",".join(quoted_domain)
                lines.append(f"    {_quote_symbol(param_name)}({domain_str})")
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


def _expr_references_param(expr: Expr, param_name: str) -> bool:
    """Check if an expression tree contains a ParamRef to the given parameter.

    Issue #738: Used to detect self-referencing parameter assignments like
    ``deltaq(sc) = deltaq(sc) / (1 + deltaq(sc))`` where the RHS references the
    parameter being assigned.

    Args:
        expr: Expression tree to search
        param_name: Parameter name to look for (case-insensitive)

    Returns:
        True if the expression contains a ParamRef with the given name
    """
    if isinstance(expr, ParamRef) and expr.name.lower() == param_name.lower():
        return True
    return any(_expr_references_param(child, param_name) for child in expr.children())


def _expr_contains_varref_attribute(expr: Expr) -> bool:
    """Check whether an expression tree contains a VarRef with an attribute.

    Used to detect `.l`-referencing calibration assignments (e.g., ``x.l(i)``)
    that must be emitted after the Variables declaration in GAMS.
    """
    if isinstance(expr, VarRef) and expr.attribute:
        return True
    # Explicitly traverse index expressions on reference-like nodes.
    # VarRef/ParamRef/MultiplierRef.children() do not yield indices,
    # so an attributed VarRef inside an IndexOffset would be missed.
    if isinstance(expr, (VarRef, ParamRef, MultiplierRef)):
        for idx in expr.indices:
            if isinstance(idx, Expr) and _expr_contains_varref_attribute(idx):
                return True
    return any(_expr_contains_varref_attribute(child) for child in expr.children())


def _collect_param_refs(expr: Expr) -> set[str]:
    """Collect all ParamRef names referenced in an expression tree."""
    refs: set[str] = set()
    if isinstance(expr, ParamRef):
        refs.add(expr.name.lower())
    for child in expr.children():
        refs.update(_collect_param_refs(child))
    if isinstance(expr, (VarRef, ParamRef, MultiplierRef)):
        for idx in expr.indices:
            if isinstance(idx, Expr):
                refs.update(_collect_param_refs(idx))
    return refs


def emit_computed_parameter_assignments(model_ir: ModelIR, *, varref_filter: str = "all") -> str:
    """Emit computed parameter assignment statements.

    Sprint 17 Day 4: Emit expressions stored in ParameterDef.expressions as
    GAMS assignment statements. These are computed parameters like:
        c(i,j) = f*d(i,j)/1000;
        gplus(c) = gibbs(c) + log(750*.07031);

    Args:
        model_ir: Model IR containing parameter definitions with expressions
        varref_filter: Controls which expressions are emitted based on whether
            they contain attributed VarRef nodes (e.g., ``x.l(i)``):
            - ``"all"``: Emit all expressions (default, backward compatible)
            - ``"no_varref_attr"``: Skip expressions containing VarRef with attribute
            - ``"only_varref_attr"``: Only emit expressions containing VarRef with attribute

    Returns:
        GAMS assignment statements as string

    Example output:
        c(i,j) = f * d(i,j) / 1000;
        gplus(c) = gibbs(c) + log(750 * 0.07031);
    """
    _VALID_VARREF_FILTERS = {"all", "no_varref_attr", "only_varref_attr"}
    if varref_filter not in _VALID_VARREF_FILTERS:
        raise ValueError(
            f"Invalid varref_filter={varref_filter!r}. "
            f"Allowed values: {sorted(_VALID_VARREF_FILTERS)}"
        )

    lines: list[str] = []

    # PR #658 review: Precompute declared sets (lowercase) once for efficient lookup
    # This avoids recomputing the lowercase set inside the inner loop
    declared_sets_lower = {s.lower() for s in model_ir.sets.keys()} | {
        s.lower() for s in model_ir.aliases.keys()
    }

    # Issue #763: Compute transitive closure of calibration parameters.
    # A parameter that references .l values (VarRef with attribute) is a
    # "calibration" parameter.  A parameter that transitively depends on a
    # calibration parameter (e.g., rva = cva / cli, where cva and cli use .l)
    # must also be emitted in the calibration section to avoid division-by-zero
    # from uninitialized dependencies.
    calibration_params: set[str] = set()
    param_deps: dict[str, set[str]] = {}
    if varref_filter in ("no_varref_attr", "only_varref_attr"):
        for pname, pdef in model_ir.params.items():
            if not pdef.expressions:
                continue
            pname_lower = pname.lower()
            if any(_expr_contains_varref_attribute(ex) for _, ex in pdef.expressions):
                calibration_params.add(pname_lower)
            refs: set[str] = set()
            for _, ex in pdef.expressions:
                refs.update(_collect_param_refs(ex))
            if refs:
                param_deps[pname_lower] = refs
        # Propagate calibration flag through transitive dependencies
        changed = True
        while changed:
            changed = False
            for pname_lower, deps in param_deps.items():
                if pname_lower not in calibration_params and deps & calibration_params:
                    calibration_params.add(pname_lower)
                    changed = True

    # Issue #763: When emitting calibration parameters, topologically sort them
    # so dependencies are emitted first (e.g., cva and cli before rva = cva/cli).
    param_order: list[str]
    if varref_filter == "only_varref_attr":
        eligible: list[str] = []
        for pname, pdef in model_ir.params.items():
            if pname in PREDEFINED_GAMS_CONSTANTS or not pdef.expressions:
                continue
            if not pdef.domain:
                if any(len(k) > 0 for k, _ in pdef.expressions):
                    continue
            if pname.lower() in calibration_params:
                eligible.append(pname)
        # Kahn's algorithm for topological sort
        eligible_lower = {p.lower() for p in eligible}
        in_degree: dict[str, int] = dict.fromkeys(eligible, 0)
        for pname in eligible:
            deps = param_deps.get(pname.lower(), set())
            for dep in deps:
                if dep in eligible_lower:
                    in_degree[pname] += 1
        queue = [p for p in eligible if in_degree[p] == 0]
        sorted_params: list[str] = []
        while queue:
            node = queue.pop(0)
            sorted_params.append(node)
            node_lower = node.lower()
            for pname in eligible:
                if pname in sorted_params:
                    continue
                deps = param_deps.get(pname.lower(), set())
                if node_lower in deps:
                    in_degree[pname] -= 1
                    if in_degree[pname] == 0:
                        queue.append(pname)
        for pname in eligible:
            if pname not in sorted_params:
                sorted_params.append(pname)
        param_order = sorted_params
    else:
        param_order = list(model_ir.params.keys())

    for param_name in param_order:
        param_def = model_ir.params[param_name]
        # Skip predefined constants
        if param_name in PREDEFINED_GAMS_CONSTANTS:
            continue

        # Check if this parameter has expressions (computed values)
        if not param_def.expressions:
            continue

        # Sprint 18 Day 2: Skip parameters with no declared domain but have INDEXED
        # expressions. These are typically post-solve report parameters like:
        #   Parameter report;
        #   report('x1','global') = 1;
        #   report('x1','solver') = x1.l;  (references solution values)
        #   report('x1','diff') = report('x1','global') - report('x1','solver');
        #
        # GAMS allows declaring parameters without domains and using them with any
        # indices, but emitting them to MCP causes errors:
        # - Error 116: Label is unknown (the indices aren't declared sets)
        # - Error 148: Dimension mismatch (scalar declared but used with indices)
        #
        # Issue #675: Even if some values exist (e.g., report('x1','global') = 1),
        # the expressions may reference other indexed assignments that depend on
        # solution values (.l) which aren't available until after solving.
        # Skip ALL indexed expressions for domain-less parameters.
        if not param_def.domain:
            # Check if any expression has indexed keys (not scalar)
            has_indexed_exprs = any(len(key) > 0 for key, _expr in param_def.expressions)
            if has_indexed_exprs:
                continue

        # Issue #763: Use the transitive calibration set to determine which pass
        # this parameter belongs to.
        is_calibration = (
            param_name.lower() in calibration_params if varref_filter != "all" else False
        )
        if varref_filter == "no_varref_attr" and is_calibration:
            continue
        if varref_filter == "only_varref_attr" and not is_calibration:
            continue

        # Emit each expression assignment (list preserves sequential ordering)
        # Track whether we've emitted any expression for this parameter so far,
        # used to detect self-referencing expressions that lack prior assignments.
        has_prior_assignment = bool(param_def.values)
        seen_assignment_lines: set[str] = set()  # Issue #768: deduplicate repeated assignments
        for key_tuple, expr in param_def.expressions:
            # Issue #738: Skip self-referencing expressions when the parameter has no
            # prior values or prior emitted expressions. This occurs when the parser
            # drops the initial .l-based assignment but keeps the self-referencing
            # follow-up. If a prior expression was already emitted (or static values
            # exist), the self-reference is valid.
            if _expr_references_param(expr, param_name) and not has_prior_assignment:
                logger.info(
                    "Skipping self-referencing expression for parameter '%s' "
                    "(no prior values — likely depends on dropped .l calibration)",
                    param_name,
                )
                continue

            # Convert expression to GAMS syntax
            # PR #658 review: Derive domain_vars from model context (declared sets/aliases)
            # rather than trusting raw key strings. This prevents unquoted element literals
            # like "cod", "apr", "land" from being misclassified as domain variables.
            domain_vars = frozenset(
                idx
                for idx in key_tuple
                if not idx.startswith('"')
                and not idx.startswith("'")
                and idx.lower() in declared_sets_lower
            )
            expr_str = expr_to_gams(expr, domain_vars=domain_vars)

            # Format the LHS with indices
            # Quote symbol names that contain special characters (Issue #665)
            if key_tuple:
                # Indexed parameter: c(i,j) = expr
                # key_tuple indices are already normalized:
                # - Domain variables: unquoted (e.g., i, j)
                # - Element literals: quoted strings (e.g., "route-1", "revenue")
                # Emit indices as-is to avoid double-quoting element literals.
                index_str = ",".join(key_tuple)
                assignment_line = f"{_quote_symbol(param_name)}({index_str}) = {expr_str};"
            else:
                # Scalar parameter: f = expr
                assignment_line = f"{_quote_symbol(param_name)} = {expr_str};"
            # Issue #768: Skip duplicate assignments (e.g., scalar reassignments
            # collected once per equation pass during KKT construction).
            if assignment_line not in seen_assignment_lines:
                seen_assignment_lines.add(assignment_line)
                lines.append(assignment_line)
            has_prior_assignment = True

    return "\n".join(lines)


def emit_set_assignments(model_ir: ModelIR) -> str:
    """Emit dynamic set assignment statements.

    Sprint 18 Day 3: Emit SetAssignment objects stored in model_ir.set_assignments
    as GAMS assignment statements. These are dynamic subset initializations like:
        ku(k) = yes$(ord(k) < card(k));
        ki(k) = yes$(ord(k) = 1);
        kt(k) = not ku(k);
        low(n,nn) = ord(n) > ord(nn);

    Args:
        model_ir: Model IR containing set assignment definitions

    Returns:
        GAMS assignment statements as string

    Example output:
        ku(k) = yes$(ord(k) < card(k));
        low(n,nn) = ord(n) > ord(nn);
    """
    if not model_ir.set_assignments:
        return ""

    lines: list[str] = []

    for set_assignment in model_ir.set_assignments:
        # Convert expression to GAMS syntax
        # Pass indices as domain_vars so they're recognized as domain variables
        domain_vars = frozenset(set_assignment.indices)
        expr_str = expr_to_gams(set_assignment.expr, domain_vars=domain_vars)

        # Format the LHS with indices
        # Quote symbol names that contain special characters (Issue #665)
        if set_assignment.indices:
            # Emit indices as-is: they may be domain variables or already-normalized
            # literals (e.g., "route-1"). Only quote the set_name as a symbol name.
            index_str = ",".join(set_assignment.indices)
            lines.append(f"{_quote_symbol(set_assignment.set_name)}({index_str}) = {expr_str};")
        else:
            # Scalar set assignment (rare but possible)
            lines.append(f"{_quote_symbol(set_assignment.set_name)} = {expr_str};")

    return "\n".join(lines)

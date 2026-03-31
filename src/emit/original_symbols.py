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
import math
import re
from collections import deque

from src.emit.expr_to_gams import (
    _format_mixed_indices,
    expr_to_gams,
    resolve_index_conflicts,
)
from src.ir.ast import (
    Binary,
    Call,
    Const,
    DollarConditional,
    Expr,
    IndexOffset,
    LhsConditionalAssign,
    MultiplierRef,
    ParamRef,
    Prod,
    SetMembershipTest,
    Sum,
    SymbolRef,
    Unary,
    VarRef,
)
from src.ir.constants import GAMS_RESERVED_CONSTANTS, PREDEFINED_GAMS_CONSTANTS
from src.ir.model_ir import ModelIR
from src.ir.symbols import ParameterDef, SetDef

logger = logging.getLogger(__name__)


def _format_param_value(value: float | str) -> str:
    """Format a parameter/scalar value for GAMS data syntax.

    Handles IEEE special values:
    - +Inf → 'inf' (GAMS native)
    - -Inf → '-inf' (GAMS native)
    - NaN → 'na' (GAMS native for Not Available)

    Also handles acronym values stored as strings.
    """
    # Issue #877: Acronym values stored as strings are emitted as-is
    if isinstance(value, str):
        return value
    if isinstance(value, float):
        if math.isinf(value):
            return "inf" if value > 0 else "-inf"
        if math.isnan(value):
            return "na"
    if isinstance(value, (int, float)) and value == int(value):
        return str(int(value))
    return str(value)


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


def _quote_assignment_index(
    idx: str,
    sets_lower: set[str],
    domain_lower: frozenset[str] | None = None,
) -> str:
    """Quote an index element for executable assignment LHS if needed.

    Issues #874, #886, #912, #916: In GAMS executable assignments like
    ``p(i,'3') = 0``, indices must be quoted when they are:
    - numeric-looking (``'3'`` not ``3``)
    - containing operators like ``-`` or ``+`` (``'period-1'`` not ``period-1``)
    - literal element names that collide with declared set names

    Already-quoted indices are returned as-is.  Domain variables (set/alias
    names that are part of the parameter's declared domain) are never quoted.

    Args:
        idx: The index element string
        sets_lower: All declared set/alias names (lowercase)
        domain_lower: The parameter's declared domain set names (lowercase).
            When provided, only indices matching domain sets are treated as
            domain variables.  When ``None``, falls back to checking all
            ``sets_lower`` (backward-compatible).
    """
    # Already quoted
    if (idx.startswith('"') and idx.endswith('"')) or (idx.startswith("'") and idx.endswith("'")):
        return idx
    # Wildcard '*' should never be quoted (universal set reference)
    if idx == "*":
        return idx
    # Domain variable check: if domain_lower is provided, only treat indices
    # matching the parameter's own domain as domain variables.  Otherwise,
    # fall back to checking all declared sets (backward-compatible).
    check_set = domain_lower if domain_lower is not None else sets_lower
    if idx.lower() in check_set:
        return _quote_symbol(idx)
    # Issue #912: When domain context is provided (values path where quotes
    # were stripped at parse time), any index that is NOT a domain variable
    # AND NOT a declared set/alias name is a literal element value.
    # Quote it to prevent GAMS from interpreting it incorrectly.
    # Indices that ARE declared set/alias names stay bare — they may be
    # cross-domain references (e.g., yw(t,at,s,cl) where t is a subset
    # of the declared domain set te).
    if domain_lower is not None and idx.lower() not in sets_lower:
        return f"'{idx}'"
    # Issue #886/#916: Elements with operators (-,+) or other special chars
    # must be quoted so GAMS doesn't interpret them as arithmetic
    if _needs_quoting(idx):
        return f"'{idx}'"
    return idx


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

    # Normalize double-quoted elements to single-quoted
    # GAMS allows both "sc-mill" and 'sc-mill' as quoted labels.
    # The parser/IR may store elements with double quotes (e.g., from
    # variable bound assignments like xca.up(g,"sc-mill")).
    if len(element) >= 2 and element.startswith('"') and element.endswith('"'):
        element = "'" + element[1:-1] + "'"

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

    # GUSS dict sets use three-component dot-separated elements where the
    # last component may be an empty quoted string (e.g., rapscenarios.scenario.'').
    # The parser stores this as a trailing dot: "rapscenarios.scenario."
    # Restore the empty component so GAMS interprets it as a 3-tuple, not a
    # quoted single label.  (Issue #910)
    if element.endswith("."):
        return element + "''"

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


def _is_referenced_in_loops(param_name: str, model_ir: ModelIR) -> bool:
    """Check if a parameter is referenced in any loop statement body.

    Issue #1182: Parameters assigned inside loops (e.g., kdem(k) = uniform(...))
    need to be declared even if they have no static values/expressions.
    """
    from lark import Token, Tree

    pname_lower = param_name.lower()

    def _check_tree(node: Tree | Token) -> bool:
        if isinstance(node, Token):
            if node.type == "ID" and str(node).lower() == pname_lower:
                return True
            return False
        if isinstance(node, Tree):
            return any(_check_tree(c) for c in node.children)
        return False

    for loop_stmt in model_ir.loop_statements:
        if hasattr(loop_stmt, "body_stmts"):
            for stmt in loop_stmt.body_stmts:
                if isinstance(stmt, (Tree, Token)) and _check_tree(stmt):
                    return True
    return False


def emit_original_parameters(
    model_ir: ModelIR,
    param_domain_widenings: dict[str, tuple[str, ...]] | None = None,
    model_relevant_params: set[str] | None = None,
) -> str:
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

    # Issue #860: Build set/alias lookup for detecting subset-qualified values.
    # When a value key element is a set/alias name (not an element literal),
    # it's a subset-qualified assignment like gamma(in) = 0 and must be emitted
    # as an executable statement, not inline data. These are handled separately
    # by emit_subset_value_assignments().
    sets_and_aliases_lower = {s.lower() for s in model_ir.sets.keys()} | {
        s.lower() for s in model_ir.aliases.keys()
    }

    # Emit Parameters
    if parameters:
        lines.append("Parameters")
        for param_name, param_def in parameters.items():
            # Issue #1164/#1175: Use widened domain if parameter needs it
            if param_domain_widenings and param_name.lower() in param_domain_widenings:
                domain = list(param_domain_widenings[param_name.lower()])
            else:
                domain = list(param_def.domain)

            # Use ParameterDef.values (Finding #3)
            # Format tuple keys as GAMS syntax: ("i1", "j2") → "i1.j2"
            if param_def.values:
                domain_size = len(domain)
                # Issue #913: Use dict for last-write-wins deduplication.
                # Table data and computed assignments may create entries with
                # different key representations (e.g., ('upper.fuel-oil', 'sulfur')
                # vs ('upper', 'fuel-oil', 'sulfur')) that expand to the same
                # normalized key. The dict ensures only the last value is emitted.
                data_by_key: dict[str, str] = {}
                for key_tuple, value in param_def.values.items():
                    # Expand key to match domain size (handles table data with dotted row headers)
                    expanded_key = _expand_table_key(key_tuple, domain_size)

                    # Skip malformed entries (e.g., zero-fill entries with wrong dimensions)
                    if expanded_key is None:
                        continue

                    # Issue #860: Skip subset-qualified values from inline data.
                    # These are emitted as executable assignments by
                    # emit_subset_value_assignments() after set assignments.
                    if any(k.lower() in sets_and_aliases_lower for k in expanded_key):
                        continue

                    # Issue #967: Skip zero-valued entries to preserve GAMS sparse
                    # semantics. Unassigned parameters default to zero in GAMS but are
                    # skipped during division (sparse evaluation). Explicit zeros break
                    # this, causing division-by-zero runtime errors.
                    if isinstance(value, (int, float)) and value == 0:
                        continue

                    # Convert tuple to GAMS index syntax (Finding #3)
                    # Apply quoting/sanitization to each element for consistent handling
                    # This ensures parameter data keys match set element quoting
                    sanitized_keys = [_sanitize_set_element(k) for k in expanded_key]
                    key_str = ".".join(sanitized_keys)
                    data_by_key[key_str] = f"{key_str} {_format_param_value(value)}"

                # Quote symbol names that contain special characters (Issue #665)
                quoted_domain = [_quote_symbol(d) for d in domain]
                domain_str = ",".join(quoted_domain)
                data_parts = list(data_by_key.values())
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
                # Issue #917: Skip parameters with no values AND no expressions,
                # UNLESS they're referenced in model equations or loop
                # statements (Issue #1182). Loop-initialized reporting
                # parameters are skipped, but parameters used in equations
                # or pre-solve loops must be declared.
                if not param_def.expressions:
                    is_model_relevant = (
                        model_relevant_params is not None
                        and param_name.lower() in model_relevant_params
                    )
                    is_loop_referenced = _is_referenced_in_loops(param_name, model_ir)
                    if not is_model_relevant and not is_loop_referenced:
                        continue
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
            if name not in PREDEFINED_GAMS_CONSTANTS
            and is_valid_scalar_name(name)
            and name.lower() not in model_ir.acronyms  # Issue #877: skip acronyms
        }
        if user_scalars:
            if lines:  # Add blank line if parameters were emitted
                lines.append("")
            lines.append("Scalars")
            for scalar_name, scalar_def in user_scalars.items():
                # Scalars have values[()] = value (Finding #3)
                value = scalar_def.values.get((), 0.0)
                lines.append(f"    {scalar_name} /{_format_param_value(value)}/")
            lines.append(";")

    return "\n".join(lines)


def collect_missing_param_labels(model_ir: ModelIR) -> set[str]:
    """Collect first-dimension labels lost by zero-filtering in parameter data.

    Issue #1007: When multi-dimensional parameters have rows where ALL values
    are zero, the zero-filtering from Issue #967 eliminates those rows entirely.
    This drops the label from the emitted parameter data, causing GAMS $116
    errors when the label is later referenced via string-indexed lookups like
    ``zz("depr",i)``.

    Returns the set of missing labels that need UEL registration via a
    synthetic Set declaration.
    """
    sets_and_aliases_lower = {s.lower() for s in model_ir.sets.keys()} | {
        s.lower() for s in model_ir.aliases.keys()
    }
    missing: set[str] = set()

    for param_def in model_ir.params.values():
        domain = list(param_def.domain)
        if not param_def.values or len(domain) < 2:
            continue
        # Only track labels for parameters with a universe (*) first dimension.
        # Named set domains (e.g., i, j) already have their elements registered
        # via the set declaration, so zero-filtered rows aren't truly lost.
        if domain[0] != "*":
            continue

        domain_size = len(domain)
        all_first_labels: set[str] = set()
        emitted_first_labels: set[str] = set()

        for key_tuple, value in param_def.values.items():
            expanded_key = _expand_table_key(key_tuple, domain_size)
            if expanded_key is None:
                continue
            if any(k.lower() in sets_and_aliases_lower for k in expanded_key):
                continue

            first_label = expanded_key[0]
            all_first_labels.add(first_label)

            if isinstance(value, (int, float)) and value == 0:
                continue
            emitted_first_labels.add(first_label)

        missing.update(all_first_labels - emitted_first_labels)

    return missing


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
    """Collect all ParamRef names from an expression tree and its index expressions."""
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


def _topological_sort_params(eligible: list[str], param_deps: dict[str, set[str]]) -> list[str]:
    """Topologically sort parameters so dependencies are emitted first.

    Uses Kahn's algorithm. Parameters with no dependencies come first.
    Params not reachable (e.g., cycles) are appended at the end.
    """
    eligible_lower = {p.lower() for p in eligible}
    in_degree: dict[str, int] = dict.fromkeys(eligible, 0)
    # Build reverse dependency graph: dep -> list of params that depend on it.
    dependents: dict[str, list[str]] = {}
    for pname in eligible:
        deps = param_deps.get(pname.lower(), set())
        for dep in deps:
            if dep in eligible_lower:
                in_degree[pname] += 1
                dependents.setdefault(dep, []).append(pname)
    queue = deque(p for p in eligible if in_degree[p] == 0)
    sorted_params: list[str] = []
    while queue:
        node = queue.popleft()
        sorted_params.append(node)
        node_lower = node.lower()
        for pname in dependents.get(node_lower, ()):
            in_degree[pname] -= 1
            if in_degree[pname] == 0:
                queue.append(pname)
    for pname in eligible:
        if pname not in sorted_params:
            sorted_params.append(pname)
    return sorted_params


# Issue #878: Statement-level topological sort type
_StmtTuple = tuple[
    str, tuple[str | IndexOffset, ...], Expr, int
]  # (param_name, key, expr, orig_idx)


def _topological_sort_statements(
    stmts: list[_StmtTuple],
    params_with_static_values: set[str],
) -> list[_StmtTuple]:
    """Topologically sort individual assignment statements by read/write deps.

    Issue #878: Parameter-level sorting can't handle cases where the same
    parameter has assignments that both precede and depend on other parameters
    (e.g., SAM is first loaded from data, then rewritten from T1).  This
    function sorts at the individual statement level.

    A statement is "ready" when all parameters it reads have either:
    - Been written by a prior statement in the sorted order, OR
    - Have static values (from table data / initial values), OR
    - Are the same parameter being written (self-reference)

    Args:
        stmts: List of (param_name, key_tuple, expr, original_index) tuples
        params_with_static_values: Set of lowercase param names that have
            static .values data (considered already "defined")

    Returns:
        Topologically sorted list of statement tuples
    """
    if len(stmts) <= 1:
        return stmts

    # Collect read dependencies for each statement (excluding self-reads).
    # Also traverse IndexOffset.offset expressions in LHS key_tuple, since
    # offsets like p(t+shift(i)) reference parameters that must be defined first.
    stmt_reads: list[set[str]] = []
    for param_name, key, expr, _idx in stmts:
        refs = _collect_param_refs(expr)
        for idx in key:
            if isinstance(idx, IndexOffset) and isinstance(idx.offset, Expr):
                refs.update(_collect_param_refs(idx.offset))
        refs.discard(param_name.lower())
        stmt_reads.append(refs)

    # Set of param names written by ANY statement in our list
    writable = {s[0].lower() for s in stmts}

    # Split each param's statements into "phases" at dependency boundaries.
    # A new phase starts when a statement introduces a new external dep that
    # previous stmts in the same param didn't have.  This allows, e.g.,
    # SAM's early self-contained totals to emit separately from SAM's later
    # T1-dependent totals.  Within a phase, original order is preserved.
    # Each phase is a scheduling unit: (phase_key, [stmt_indices], deps).
    from collections import defaultdict

    param_chains: dict[str, list[int]] = defaultdict(list)
    for i, (param_name, _key, _expr, _idx) in enumerate(stmts):
        param_chains[param_name.lower()].append(i)

    # phase_key = "param:N" where N is the phase number for that param
    phases: list[tuple[str, str, list[int], set[str]]] = []  # (key, param, indices, deps)
    last_phase_key: dict[str, str] = {}  # param -> key of its last phase

    for pname_low, chain in param_chains.items():
        # cum_deps tracks all external dependencies seen so far across all
        # phases of this parameter.  It is updated AFTER the new-dependency
        # check so that the check compares the current statement's reads
        # against dependencies accumulated from *previous* statements only.
        cum_deps: set[str] = set()
        phase_indices: list[int] = []
        phase_num = 0
        for i in chain:
            new_deps = (stmt_reads[i] & writable) - cum_deps
            if new_deps and phase_indices:
                # New dependency boundary — close current phase
                pkey = f"{pname_low}:{phase_num}"
                phases.append((pkey, pname_low, list(phase_indices), set(cum_deps)))
                last_phase_key[pname_low] = pkey
                phase_num += 1
                phase_indices = []
            cum_deps |= stmt_reads[i]
            phase_indices.append(i)
        if phase_indices:
            pkey = f"{pname_low}:{phase_num}"
            phases.append((pkey, pname_low, list(phase_indices), set(cum_deps)))
            last_phase_key[pname_low] = pkey

    # Kahn's-style sort at the phase level.
    # A phase is ready when its deps are satisfied AND all prior phases of
    # the same param have been emitted (preserves within-param order).
    # Treat all params_with_static_values as already defined, even if they also
    # have expressions, so that reads of their static .values do not block phases.
    defined = set(params_with_static_values)
    emitted_phases: set[str] = set()
    remaining = list(range(len(phases)))
    sorted_stmts: list[_StmtTuple] = []

    # Build predecessor map: phase N of param P requires phase N-1 of param P
    phase_predecessor: dict[str, str | None] = {}
    param_phase_list: dict[str, list[str]] = defaultdict(list)
    for pkey, pname_low, _indices, _deps in phases:
        param_phase_list[pname_low].append(pkey)
    for _pname_low, pkeys in param_phase_list.items():
        phase_predecessor[pkeys[0]] = None
        for j in range(1, len(pkeys)):
            phase_predecessor[pkeys[j]] = pkeys[j - 1]

    max_iterations = len(phases) + 1
    for _ in range(max_iterations):
        if not remaining:
            break
        ready: list[int] = []
        still_blocked: list[int] = []
        for pi in remaining:
            pkey, pname_low, _indices, deps = phases[pi]
            # Check predecessor emitted
            pred = phase_predecessor[pkey]
            if pred is not None and pred not in emitted_phases:
                still_blocked.append(pi)
                continue
            unmet = (deps - defined) & writable
            if not unmet:
                ready.append(pi)
            else:
                still_blocked.append(pi)
        if not ready:
            # Cycle — break with static values, but only for a parameter's
            # first phase (phase 0) to avoid emitting later phases out of
            # order before their predecessors have been emitted.
            cycle_broken = False
            for pi in still_blocked:
                pkey, pname_low, _indices, _deps = phases[pi]
                if pname_low in params_with_static_values and phase_predecessor.get(pkey) is None:
                    defined.add(pname_low)
                    cycle_broken = True
            if cycle_broken:
                remaining = still_blocked
                continue
            # Truly unresolvable — emit remaining in original order
            all_remaining: list[int] = []
            for pi in still_blocked:
                all_remaining.extend(phases[pi][2])
            all_remaining.sort()
            for i in all_remaining:
                sorted_stmts.append(stmts[i])
            break
        # Sort ready phases by their first stmt's original index
        ready.sort(key=lambda pi: phases[pi][2][0])
        for pi in ready:
            pkey, pname_low, indices, _deps = phases[pi]
            for i in indices:
                sorted_stmts.append(stmts[i])
            emitted_phases.add(pkey)
            # Mark param as defined once its LAST phase is emitted
            if pkey == last_phase_key[pname_low]:
                defined.add(pname_low)
        remaining = still_blocked

    return sorted_stmts


def emit_computed_parameter_assignments(
    model_ir: ModelIR,
    *,
    varref_filter: str = "all",
    only_params: set[str] | None = None,
    exclude_params: set[str] | None = None,
) -> str:
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
        only_params: If provided, only emit params whose lowercase name is in this set.
        exclude_params: If provided, skip params whose lowercase name is in this set.

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
            # Check RHS expressions and IndexOffset.offset in LHS keys
            # for VarRef with attribute (calibration detection).
            all_exprs = [ex for _, ex in pdef.expressions]
            for key, _ in pdef.expressions:
                for idx in key:
                    if isinstance(idx, IndexOffset) and isinstance(idx.offset, Expr):
                        all_exprs.append(idx.offset)
            if any(_expr_contains_varref_attribute(ex) for ex in all_exprs):
                calibration_params.add(pname_lower)
            refs: set[str] = set()
            for ex in all_exprs:
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

    # Issue #763 / #860: Topologically sort computed parameter assignments so
    # dependencies are emitted first. Applied to both calibration and regular passes.
    param_order: list[str]
    if varref_filter == "only_varref_attr":
        eligible: list[str] = []
        for pname, pdef in model_ir.params.items():
            if (pname in PREDEFINED_GAMS_CONSTANTS and not pdef.domain) or not pdef.expressions:
                continue
            if not pdef.domain:
                if any(len(k) > 0 for k, _ in pdef.expressions):
                    continue
            if pname.lower() in calibration_params:
                eligible.append(pname)
        param_order = _topological_sort_params(eligible, param_deps)
    elif varref_filter == "no_varref_attr":
        # Issue #860: Topologically sort regular (non-calibration) parameters too.
        eligible = []
        for pname, pdef in model_ir.params.items():
            if (pname in PREDEFINED_GAMS_CONSTANTS and not pdef.domain) or not pdef.expressions:
                continue
            if not pdef.domain:
                if any(len(k) > 0 for k, _ in pdef.expressions):
                    continue
            if pname.lower() not in calibration_params:
                eligible.append(pname)
        param_order = _topological_sort_params(eligible, param_deps)
    else:
        param_order = list(model_ir.params.keys())

    # Issue #878: Collect all eligible statements first, then topologically sort
    # at the statement level so that dependencies are emitted before consumers.
    collected_stmts: list[_StmtTuple] = []
    params_with_static: set[str] = set()  # params that have .values (table data etc.)
    stmt_idx = 0
    for param_name in param_order:
        param_def = model_ir.params.get(param_name)
        if param_def is None:
            continue
        # Skip predefined constants — but only if the parameter has no domain.
        # Issue #914: Models may declare indexed parameters whose name collides
        # with a built-in constant (e.g., pi(s,i,sp,j,spp) in markov).
        if param_name in PREDEFINED_GAMS_CONSTANTS and not param_def.domain:
            continue

        # Issue #860: Apply only_params / exclude_params filters
        if only_params is not None and param_name.lower() not in only_params:
            continue
        if exclude_params is not None and param_name.lower() in exclude_params:
            continue

        # Check if this parameter has expressions (computed values)
        if not param_def.expressions:
            continue

        # Sprint 18 Day 2: Skip parameters with no declared domain but have INDEXED
        # expressions. These are typically post-solve report parameters.
        if not param_def.domain:
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

        if param_def.values:
            params_with_static.add(param_name.lower())

        # Issue #738: Track self-referencing expressions with no prior assignment.
        # Skipped statements are excluded from collected_stmts entirely so they
        # don't introduce spurious dependencies in the topological sort.
        has_prior_assignment = bool(param_def.values)
        for key_tuple, expr in param_def.expressions:
            is_self_ref = _expr_references_param(expr, param_name)
            if is_self_ref and not has_prior_assignment:
                logger.info(
                    "Skipping self-referencing expression for parameter '%s' "
                    "(no prior values — likely depends on dropped .l calibration)",
                    param_name,
                )
                stmt_idx += 1
                continue
            has_prior_assignment = True
            collected_stmts.append((param_name, key_tuple, expr, stmt_idx))
            stmt_idx += 1

    # Issue #878: Topologically sort collected statements
    sorted_stmts = _topological_sort_statements(collected_stmts, params_with_static)

    # Emit sorted statements
    # Subcategory E: Build set of all declared set/alias names (canonical lowercase)
    # so that set references like SAM("TRF",J) emit J bare (not "J").

    # Subcategory G: Pre-resolve all parameter assignment expressions to collect
    # the full set of generated alias names (including i__2, i__3, etc. for deeply
    # nested scopes). Emit Alias declarations up front before any assignments.
    all_param_aliases: dict[str, list[str]] = {}
    resolved_exprs: list[_StmtTuple] = []
    for param_name, key_tuple, expr, _orig_idx in sorted_stmts:
        param_domain = tuple(
            idx if isinstance(idx, str) else idx.base
            for idx in key_tuple
            if isinstance(idx, str) or isinstance(idx, IndexOffset)
        )
        resolved_expr, expr_aliases = resolve_index_conflicts(expr, param_domain)
        for base, alias_list in expr_aliases.items():
            existing = all_param_aliases.setdefault(base, [])
            for a in alias_list:
                if a not in existing:
                    existing.append(a)
        resolved_exprs.append((param_name, key_tuple, resolved_expr, _orig_idx))

    if all_param_aliases:
        for base in sorted(all_param_aliases.keys()):
            for alias_name in all_param_aliases[base]:
                lines.append(f"Alias({_quote_symbol(base)}, {_quote_symbol(alias_name)});")

    seen_assignment_lines: set[str] = set()
    for param_name, key_tuple, expr, _orig_idx in resolved_exprs:
        # Convert expression to GAMS syntax
        # domain_vars includes: LHS key_tuple indices + all declared set/alias names
        # (Subcategory E: so RHS set references like J are emitted bare)
        lhs_domain: frozenset[str] = frozenset(
            idx if isinstance(idx, str) else idx.base
            for idx in key_tuple
            if (
                isinstance(idx, str)
                and not idx.startswith('"')
                and not idx.startswith("'")
                and idx.lower() in declared_sets_lower
            )
            or (isinstance(idx, IndexOffset) and idx.base.lower() in declared_sets_lower)
        )
        domain_vars = lhs_domain | frozenset(declared_sets_lower)

        # Issue #1015: LhsConditionalAssign wraps a LHS-conditional assignment
        # p(i)$cond = rhs — emit condition on the LHS, not the RHS.
        lhs_cond_str = ""
        if isinstance(expr, LhsConditionalAssign):
            lhs_cond_str = "$(" + expr_to_gams(expr.condition, domain_vars=domain_vars) + ")"
            expr_str = expr_to_gams(expr.rhs, domain_vars=domain_vars)
        else:
            expr_str = expr_to_gams(expr, domain_vars=domain_vars)

        # Format the LHS with indices
        # Issue #949: Pass param's declared domain so set-over expanded
        # element labels (e.g., slope0 from nseg(g(s))) get quoted.
        param_def = model_ir.params.get(param_name)
        param_domain_lower: frozenset[str] | None = None
        if param_def and param_def.domain:
            param_domain_lower = frozenset(d.lower() for d in param_def.domain)
        if key_tuple:
            quoted_keys = [
                (
                    idx.to_gams_string()
                    if isinstance(idx, IndexOffset)
                    else _quote_assignment_index(
                        idx, declared_sets_lower, domain_lower=param_domain_lower
                    )
                )
                for idx in key_tuple
            ]
            index_str = ",".join(quoted_keys)
            assignment_line = (
                f"{_quote_symbol(param_name)}({index_str}){lhs_cond_str} = {expr_str};"
            )
        else:
            assignment_line = f"{_quote_symbol(param_name)}{lhs_cond_str} = {expr_str};"
        # Issue #768: Skip duplicate assignments
        if assignment_line not in seen_assignment_lines:
            seen_assignment_lines.add(assignment_line)
            lines.append(assignment_line)

    return "\n".join(lines)


def emit_interleaved_params_and_sets(
    model_ir: ModelIR,
    *,
    varref_filter: str = "no_varref_attr",
) -> tuple[str, set[str], set[int]]:
    """Emit an interleaved stream of computed params and set assignments.

    Issue #881: When set assignments and computed parameters have circular
    dependency chains (e.g., T0 → red → redsam → T1 → Abar1 → nonzero),
    they must be emitted in an interleaved order.

    This function identifies all params involved in such chains, collects
    their expressions alongside set assignment statements, and uses the
    existing statement-level topological sort to emit everything in the
    correct dependency order.

    Args:
        model_ir: Model IR containing params and set assignments
        varref_filter: Passed through for calibration filtering

    Returns:
        Tuple of:
        - GAMS code string (empty if no interleaving needed)
        - Set of lowercase param names emitted (for exclusion from later passes)
        - Set of set assignment indices emitted (for exclusion from later passes)
    """
    if not model_ir.set_assignments:
        return "", set(), set()

    dynamic_set_names = {sa.set_name.lower() for sa in model_ir.set_assignments}

    # Identify set-blocked params: have LHS conditions on dynamic sets
    set_blocked_params: set[str] = set()
    for pname, pdef in model_ir.params.items():
        if pdef.expressions:
            for _, ex in pdef.expressions:
                if isinstance(ex, LhsConditionalAssign):
                    cond_sets = _collect_set_membership_names(ex.condition)
                    if cond_sets & dynamic_set_names:
                        set_blocked_params.add(pname.lower())
                        break

    # Issue #1041: Also detect "index-blocked" params — params that are
    # (a) referenced by set assignments and (b) have expression keys using
    # dynamic set names (or their aliases).  These create a three-way dependency:
    #   set_assignment(ii) → param(ii,jj) → set_assignment(NONZERO)
    # requiring interleaving even when no LHS-condition-blocked params exist.
    # Build expanded set including aliases of dynamic sets.
    # Resolve alias chains transitively (e.g., kk -> jj -> ii where ii is dynamic).
    def _resolve_alias_chain(name: str) -> str:
        """Walk alias chain to canonical (non-alias) target."""
        seen: set[str] = set()
        current = name
        while current not in seen:
            seen.add(current)
            adef = model_ir.aliases.get(current)
            if adef is None:
                break
            target = adef.target.lower()
            if target == current:
                break
            current = target
        return current

    dynamic_set_names_expanded = set(dynamic_set_names)
    for aname in model_ir.aliases:
        canonical = _resolve_alias_chain(aname.lower())
        if canonical in dynamic_set_names:
            dynamic_set_names_expanded.add(aname.lower())

    all_computed_quick: set[str] = {
        p.lower() for p, pd in model_ir.params.items() if pd.expressions
    }
    sa_param_deps: set[str] = set()
    for sa in model_ir.set_assignments:
        sa_param_deps.update(_collect_param_refs(sa.expr) & all_computed_quick)
    index_blocked_params: set[str] = set()
    for pname in sa_param_deps:
        p_def = model_ir.params.get(pname)
        if p_def and p_def.expressions:
            for key_tuple, _expr in p_def.expressions:
                for idx in key_tuple:
                    if isinstance(idx, str):
                        idx_base = idx.lower()
                    elif isinstance(idx, IndexOffset):
                        idx_base = idx.base.lower()
                    else:
                        continue
                    if idx_base in dynamic_set_names_expanded:
                        index_blocked_params.add(pname)
                        break
                if pname in index_blocked_params:
                    break

    if not set_blocked_params and not index_blocked_params:
        # No params depend on dynamic sets — no interleaving needed.
        # Fall back to the simple early-params approach.
        return "", set(), set()

    # Identify all params that need to be part of the interleaved section.
    # Start with set-blocked params, then add:
    # - Params that set assignments directly depend on
    # - Transitive deps of set-blocked params (upstream)
    # - Params between set assignment deps and set-blocked params (downstream)
    all_computed: set[str] = set()
    param_deps_all: dict[str, set[str]] = {}  # union of all expr deps
    for pname, pdef in model_ir.params.items():
        if pdef.expressions:
            pname_lower = pname.lower()
            all_computed.add(pname_lower)
            refs: set[str] = set()
            for _, ex in pdef.expressions:
                refs.update(_collect_param_refs(ex))
            if refs:
                param_deps_all[pname_lower] = refs

    # Params directly needed by set assignments
    sa_direct_deps: set[str] = set()
    for sa in model_ir.set_assignments:
        sa_direct_deps.update(_collect_param_refs(sa.expr) & all_computed)

    # Build the involved set: everything between sa deps and set-blocked/index-blocked params
    involved: set[str] = set(set_blocked_params) | index_blocked_params | sa_direct_deps

    # Expand upstream: if an involved param depends on another computed param,
    # that param is also involved.
    frontier = set(involved)
    while frontier:
        next_f: set[str] = set()
        for p in frontier:
            for dep in param_deps_all.get(p, set()):
                if dep in all_computed and dep not in involved:
                    involved.add(dep)
                    next_f.add(dep)
        frontier = next_f

    # Also expand downstream: if a non-involved param depends on an involved
    # param AND depends on a set-blocked param transitively, include it.
    # (E.g., T1 depends on both T0 and redsam)
    changed = True
    while changed:
        changed = False
        for pname in all_computed:
            if pname in involved:
                continue
            deps = param_deps_all.get(pname, set())
            if deps & involved:
                # Check if this param also transitively reaches a blocked param
                visited: set[str] = set()
                to_visit = list(deps & all_computed)
                all_blocked = set_blocked_params | index_blocked_params
                reaches_blocked = False
                while to_visit:
                    d = to_visit.pop()
                    if d in visited:
                        continue
                    visited.add(d)
                    if d in all_blocked:
                        reaches_blocked = True
                        break
                    to_visit.extend(param_deps_all.get(d, set()) & all_computed - visited)
                if reaches_blocked:
                    involved.add(pname)
                    changed = True

    # Post-filter: remove params whose expression keys use dynamic set names
    # as running indices (e.g., beta(cn)) — UNLESS they are needed for the
    # index-blocked interleaving chain (Issue #1041: index-blocked params and
    # their transitive dependencies must stay so the topological sort places
    # them after their set dependencies but before dependent set assignments).
    keep_for_interleave: set[str] = set(index_blocked_params)
    _frontier = set(index_blocked_params)
    while _frontier:
        _next: set[str] = set()
        for p in _frontier:
            for dep in param_deps_all.get(p, set()):
                if dep in involved and dep not in keep_for_interleave:
                    keep_for_interleave.add(dep)
                    _next.add(dep)
        _frontier = _next

    disqualified: set[str] = set()
    for pname in involved:
        if pname in keep_for_interleave:
            continue  # Keep — needed for index-blocked interleaving chain
        p_def2: ParameterDef | None = model_ir.params.get(pname)
        if p_def2 and p_def2.expressions:
            for key_tuple, _expr in p_def2.expressions:
                for idx in key_tuple:
                    idx_str = idx.lower() if isinstance(idx, str) else ""
                    if idx_str in dynamic_set_names:
                        disqualified.add(pname)
                        break
                if pname in disqualified:
                    break
    involved -= disqualified

    if not involved:
        return "", set(), set()

    # Now build a unified stream of statements:
    # - Param expressions from involved params
    # - Set assignment "statements" (with special sentinel names)

    # Use the existing statement-level sort infrastructure.
    # Set assignments become pseudo-statements with a special param name
    # like "__set_red__".  Their "reads" are the params they reference.
    # Set-blocked params have "reads" that include the set pseudo-params.

    # Collect all involved param expressions
    declared_sets_lower = {s.lower() for s in model_ir.sets.keys()} | {
        s.lower() for s in model_ir.aliases.keys()
    }

    # Calibration detection (same logic as emit_computed_parameter_assignments)
    calibration_params: set[str] = set()
    if varref_filter in ("no_varref_attr", "only_varref_attr"):
        for pname, pdef in model_ir.params.items():
            if not pdef.expressions:
                continue
            all_exprs = [ex for _, ex in pdef.expressions]
            for key, _ in pdef.expressions:
                for idx in key:
                    if isinstance(idx, IndexOffset) and isinstance(idx.offset, Expr):
                        all_exprs.append(idx.offset)
            if any(_expr_contains_varref_attribute(ex) for ex in all_exprs):
                calibration_params.add(pname.lower())
        # Propagate calibration transitively
        changed = True
        while changed:
            changed = False
            for pname_lower, deps in param_deps_all.items():
                if pname_lower not in calibration_params and deps & calibration_params:
                    calibration_params.add(pname_lower)
                    changed = True

    # Build the combined statement list
    # Each item: (pseudo_name, key_tuple, expr, orig_idx, item_type)
    # item_type: "param" or "set"
    combined: list[tuple[str, tuple, Expr | None, int, str, int | None]] = []
    # (name, key, expr, idx, type, sa_idx_or_None)
    params_with_static: set[str] = set()
    stmt_idx = 0

    for param_name in sorted(involved):
        param_def = model_ir.params.get(param_name)
        if param_def is None:
            continue
        if param_name in PREDEFINED_GAMS_CONSTANTS and not param_def.domain:
            continue
        # Filter calibration params in no_varref_attr mode
        if varref_filter == "no_varref_attr" and param_name.lower() in calibration_params:
            continue
        if not param_def.expressions:
            continue
        if not param_def.domain:
            if any(len(k) > 0 for k, _ in param_def.expressions):
                continue
        if param_def.values:
            params_with_static.add(param_name.lower())

        # Map to original casing for emission (involved contains lowercase names)
        original_name = model_ir.params.get_original_name(param_name)

        has_prior = bool(param_def.values)
        for key_tuple, expr in param_def.expressions:
            is_self = _expr_references_param(expr, param_name)
            if is_self and not has_prior:
                stmt_idx += 1
                continue
            has_prior = True
            combined.append((original_name, key_tuple, expr, stmt_idx, "param", None))
            stmt_idx += 1

    # Issue #1007: Compute deferred sets (direct + transitive), matching
    # emit_set_assignments() logic.  E.g., it(i) = yes$(e.l(i)) is direct;
    # inn(i) = not it(i) is transitive.
    deferred_sets: set[str] = set()
    set_deps: dict[str, set[str]] = {}
    for sa in model_ir.set_assignments:
        sa_lower = sa.set_name.lower()
        if _expr_contains_varref_attribute(sa.expr):
            deferred_sets.add(sa_lower)
        set_deps[sa_lower] = _collect_set_membership_names(sa.expr)
    changed = True
    while changed:
        changed = False
        for sa_lower, deps in set_deps.items():
            if sa_lower not in deferred_sets and deps & deferred_sets:
                deferred_sets.add(sa_lower)
                changed = True

    # Add set assignments as pseudo-statements
    for i, sa in enumerate(model_ir.set_assignments):
        # Skip deferred (varref) set assignments (direct + transitive)
        if sa.set_name.lower() in deferred_sets:
            continue
        pseudo_name = f"__set_{sa.set_name.lower()}__"
        combined.append((pseudo_name, (), None, stmt_idx, "set", i))
        stmt_idx += 1

    if not combined:
        return "", set(), set()

    # Build read deps for each statement
    stmt_reads: list[set[str]] = []
    for name, key, expr, _idx, item_type, sa_idx in combined:
        if item_type == "param":
            assert expr is not None  # param items always have an expression
            refs = _collect_param_refs(expr)
            for idx_val in key:
                if isinstance(idx_val, IndexOffset) and isinstance(idx_val.offset, Expr):
                    refs.update(_collect_param_refs(idx_val.offset))
            refs.discard(name.lower())
            # If this expression has a LHS condition on a dynamic set,
            # add the set pseudo-name as a dependency.
            if isinstance(expr, LhsConditionalAssign):
                cond_sets = _collect_set_membership_names(expr.condition)
                for sn in cond_sets & dynamic_set_names:
                    refs.add(f"__set_{sn}__")
            # Issue #1041: If expression keys use dynamic set names (or aliases)
            # as indices (e.g., Abar0(ii,jj)), those sets must be populated first.
            # Also handle IndexOffset indices (e.g., t+1) by checking idx.base.
            for idx_val in key:
                if isinstance(idx_val, str):
                    idx_base = idx_val.lower()
                elif isinstance(idx_val, IndexOffset):
                    idx_base = idx_val.base.lower()
                else:
                    continue
                if idx_base in dynamic_set_names:
                    refs.add(f"__set_{idx_base}__")
                elif idx_base in dynamic_set_names_expanded:
                    # Alias (possibly chained) of a dynamic set — resolve
                    # transitively to the canonical dynamic set target.
                    canonical_target = _resolve_alias_chain(idx_base)
                    if canonical_target in dynamic_set_names:
                        refs.add(f"__set_{canonical_target}__")
            stmt_reads.append(refs)
        else:
            # Set assignment — reads the params it references AND
            # any dynamic sets it depends on (set→set ordering).
            assert sa_idx is not None  # set items always have an index
            sa = model_ir.set_assignments[sa_idx]
            refs = _collect_param_refs(sa.expr) - {name.lower()}
            # Add pseudo-deps for referenced dynamic sets (e.g., kt = not ku)
            for sn in _collect_set_membership_names(sa.expr) & dynamic_set_names:
                refs.add(f"__set_{sn}__")
            stmt_reads.append(refs)

    # Set of all "writable" names (param names + set pseudo-names)
    writable = {c[0].lower() for c in combined}

    # Build the phase structure (same as _topological_sort_statements)
    from collections import defaultdict

    param_chains: dict[str, list[int]] = defaultdict(list)
    for i, (name, _key, _expr_or_none, _idx, _type, _sa) in enumerate(combined):
        param_chains[name.lower()].append(i)

    phases: list[tuple[str, str, list[int], set[str]]] = []
    last_phase_key: dict[str, str] = {}

    for pname_low, chain in param_chains.items():
        cum_deps: set[str] = set()
        phase_indices: list[int] = []
        phase_num = 0
        for i in chain:
            new_deps = (stmt_reads[i] & writable) - cum_deps
            if new_deps and phase_indices:
                pkey = f"{pname_low}:{phase_num}"
                phases.append((pkey, pname_low, list(phase_indices), set(cum_deps)))
                last_phase_key[pname_low] = pkey
                phase_num += 1
                phase_indices = []
            cum_deps |= stmt_reads[i]
            phase_indices.append(i)
        if phase_indices:
            pkey = f"{pname_low}:{phase_num}"
            phases.append((pkey, pname_low, list(phase_indices), set(cum_deps)))
            last_phase_key[pname_low] = pkey

    # Kahn's-style phase sort
    # Issue #881: Don't pre-define set-blocked params (those with LHS conditions
    # on dynamic sets) even if they have static values.  Their computed expressions
    # override the static defaults and must be ordered correctly.
    # Issue #1041: Also exclude index-blocked params and their deps — these
    # must be ordered after their dynamic set dependencies.
    set_blocked_lower = {p.lower() for p in set_blocked_params}
    involved_lower = {p.lower() for p in involved}
    defined = params_with_static - set_blocked_lower - involved_lower
    emitted_phases: set[str] = set()
    remaining = list(range(len(phases)))
    sorted_items: list[tuple[str, tuple, Expr | None, int, str, int | None]] = []

    phase_predecessor: dict[str, str | None] = {}
    param_phase_list: dict[str, list[str]] = defaultdict(list)
    for pkey, pname_low, _indices, _deps in phases:
        param_phase_list[pname_low].append(pkey)
    for _pname_low, pkeys in param_phase_list.items():
        phase_predecessor[pkeys[0]] = None
        for j in range(1, len(pkeys)):
            phase_predecessor[pkeys[j]] = pkeys[j - 1]

    max_iterations = len(phases) + 1
    for _ in range(max_iterations):
        if not remaining:
            break
        ready: list[int] = []
        still_blocked: list[int] = []
        for pi in remaining:
            pkey, pname_low, _indices, deps = phases[pi]
            pred = phase_predecessor[pkey]
            if pred is not None and pred not in emitted_phases:
                still_blocked.append(pi)
                continue
            unmet = (deps - defined) & writable
            if not unmet:
                ready.append(pi)
            else:
                still_blocked.append(pi)
        if not ready:
            # Cycle — try breaking with static values
            cycle_broken = False
            for pi in still_blocked:
                pkey, pname_low, _indices, _deps = phases[pi]
                if pname_low in params_with_static and phase_predecessor.get(pkey) is None:
                    defined.add(pname_low)
                    cycle_broken = True
            if cycle_broken:
                remaining = still_blocked
                continue
            # Emit remaining in original order
            all_remaining: list[int] = []
            for pi in still_blocked:
                all_remaining.extend(phases[pi][2])
            all_remaining.sort()
            for i in all_remaining:
                sorted_items.append(combined[i])
            break
        ready.sort(key=lambda pi: phases[pi][2][0])
        for pi in ready:
            pkey, pname_low, indices, _deps = phases[pi]
            for i in indices:
                sorted_items.append(combined[i])
            emitted_phases.add(pkey)
            if pkey == last_phase_key[pname_low]:
                defined.add(pname_low)
        remaining = still_blocked

    # Emit sorted items as GAMS code
    lines: list[str] = []
    emitted_param_names: set[str] = set()
    emitted_sa_indices: set[int] = set()

    # Pre-resolve expressions for alias collection (and cache for reuse)
    all_aliases: dict[str, list[str]] = {}
    resolved_exprs: dict[int, Expr] = {}  # sorted_items index → resolved expr
    for si_idx, (_name, key, expr, _idx, item_type, _sa) in enumerate(sorted_items):
        if item_type != "param" or expr is None:
            continue
        param_domain = tuple(
            idx if isinstance(idx, str) else idx.base
            for idx in key
            if isinstance(idx, str) or isinstance(idx, IndexOffset)
        )
        resolved, expr_aliases = resolve_index_conflicts(expr, param_domain)
        resolved_exprs[si_idx] = resolved
        for base, alias_list in expr_aliases.items():
            existing = all_aliases.setdefault(base, [])
            for a in alias_list:
                if a not in existing:
                    existing.append(a)

    if all_aliases:
        for base in sorted(all_aliases.keys()):
            for alias_name in all_aliases[base]:
                lines.append(f"Alias({_quote_symbol(base)}, {_quote_symbol(alias_name)});")

    seen: set[str] = set()
    for si_idx, (name, key, expr, _idx, item_type, sa_idx) in enumerate(sorted_items):
        if item_type == "set":
            # Emit set assignment
            assert sa_idx is not None
            sa = model_ir.set_assignments[sa_idx]
            restored_expr = _restore_yes_keyword(sa.expr)
            domain_vars = frozenset(idx for idx in sa.indices if isinstance(idx, str))
            expr_str = expr_to_gams(restored_expr, domain_vars=domain_vars)
            if sa.indices:
                index_str = _format_mixed_indices(sa.indices, domain_vars)
                line = f"{_quote_symbol(sa.set_name)}({index_str}) = {expr_str};"
            else:
                line = f"{_quote_symbol(sa.set_name)} = {expr_str};"
            if line not in seen:
                seen.add(line)
                lines.append(line)
            emitted_sa_indices.add(sa_idx)
        else:
            # Emit param expression
            assert expr is not None
            emitted_param_names.add(name.lower())
            resolved_expr = resolved_exprs[si_idx]

            lhs_domain: frozenset[str] = frozenset(
                idx if isinstance(idx, str) else idx.base
                for idx in key
                if (
                    isinstance(idx, str)
                    and not idx.startswith('"')
                    and not idx.startswith("'")
                    and idx.lower() in declared_sets_lower
                )
                or (isinstance(idx, IndexOffset) and idx.base.lower() in declared_sets_lower)
            )
            domain_vars = lhs_domain | frozenset(declared_sets_lower)

            lhs_cond_str = ""
            if isinstance(resolved_expr, LhsConditionalAssign):
                lhs_cond_str = (
                    "$(" + expr_to_gams(resolved_expr.condition, domain_vars=domain_vars) + ")"
                )
                expr_str = expr_to_gams(resolved_expr.rhs, domain_vars=domain_vars)
            else:
                expr_str = expr_to_gams(resolved_expr, domain_vars=domain_vars)

            # Issue #949: Pass param's declared domain for element quoting
            interleaved_pdef = model_ir.params.get(name)
            interleaved_domain_lower: frozenset[str] | None = None
            if interleaved_pdef and interleaved_pdef.domain:
                interleaved_domain_lower = frozenset(d.lower() for d in interleaved_pdef.domain)
            if key:
                quoted_keys = [
                    (
                        idx.to_gams_string()
                        if isinstance(idx, IndexOffset)
                        else _quote_assignment_index(
                            idx, declared_sets_lower, domain_lower=interleaved_domain_lower
                        )
                    )
                    for idx in key
                ]
                index_str = ",".join(quoted_keys)
                line = f"{_quote_symbol(name)}({index_str}){lhs_cond_str} = {expr_str};"
            else:
                line = f"{_quote_symbol(name)}{lhs_cond_str} = {expr_str};"

            if line not in seen:
                seen.add(line)
                lines.append(line)

    return "\n".join(lines), emitted_param_names, emitted_sa_indices


def compute_set_assignment_param_deps(model_ir: ModelIR) -> set[str]:
    """Compute the set of parameter names (lowercase) referenced by set assignments.

    Issue #860: Set assignments like ``it(i) = 1$m0(i)`` reference computed
    parameters (``m0``).  These parameters must be emitted BEFORE set assignments
    even though computed parameters normally come after.  This function identifies
    the transitive closure of parameters needed by set assignments.

    Note: This function is used as a fallback when
    ``emit_interleaved_params_and_sets`` returns empty (no set-blocked params).
    The interleaved emitter handles the complex case (Issue #881) where params
    have LHS conditions on dynamic sets.
    """
    if not model_ir.set_assignments:
        return set()

    # Direct parameter references in set assignment expressions
    direct_deps: set[str] = set()
    for sa in model_ir.set_assignments:
        direct_deps.update(_collect_param_refs(sa.expr))

    # Build dependency graph for all computed params
    param_deps: dict[str, set[str]] = {}
    for pname, pdef in model_ir.params.items():
        if pdef.expressions:
            refs: set[str] = set()
            for _, ex in pdef.expressions:
                refs.update(_collect_param_refs(ex))
            if refs:
                param_deps[pname.lower()] = refs

    # Transitive closure: if set assignments need param A, and param A needs
    # param B, then param B must also be emitted early.
    needed: set[str] = set()
    all_param_keys_lower = {p.lower() for p in model_ir.params.keys()}
    frontier = direct_deps & all_param_keys_lower
    while frontier:
        needed.update(frontier)
        next_frontier: set[str] = set()
        for p in frontier:
            for dep in param_deps.get(p, set()):
                if dep not in needed and dep in all_param_keys_lower:
                    next_frontier.add(dep)
        frontier = next_frontier

    # Post-filter: remove params whose LHS expression keys reference dynamic
    # set names.  These params MUST go AFTER set assignments because their
    # indices (e.g., "cn" in beta(cn)) are populated by set assignments.
    dynamic_set_names = {sa.set_name.lower() for sa in model_ir.set_assignments}
    if dynamic_set_names:
        disqualified: set[str] = set()
        for pname in needed:
            p_def: ParameterDef | None = model_ir.params.get(pname)
            if p_def and p_def.expressions:
                for key_tuple, _expr in p_def.expressions:
                    for idx in key_tuple:
                        idx_str = idx.lower() if isinstance(idx, str) else ""
                        if idx_str in dynamic_set_names:
                            disqualified.add(pname)
                            break
                    if pname in disqualified:
                        break
        if disqualified:
            logger.info(
                "Excluding dynamic-set-dependent params from early emission: %s",
                sorted(disqualified),
            )
        needed -= disqualified

    return needed


def _restore_yes_keyword(expr: Expr) -> Expr:
    """Replace Const(1.0) with SymbolRef('yes') in set assignment expressions.

    Issue #861: The parser converts GAMS ``yes`` to ``Const(1.0)`` during parsing.
    For set assignments, ``yes`` must be preserved because GAMS distinguishes between
    set membership (``yes$cond``) and numeric value (``1$cond``).  This function
    restores the ``yes`` keyword at positions where it was originally used:
    - ``DollarConditional(Const(1.0), cond)`` → ``DollarConditional(SymbolRef('yes'), cond)``
    - ``Binary(-, Const(1.0), rhs)`` → ``Binary(-, SymbolRef('yes'), rhs)``

    The transformation is applied recursively so that nested expressions such as
    ``Binary(+, DollarConditional(Const(1.0), cond1), DollarConditional(Const(1.0), cond2))``
    or expressions inside function calls are also handled.
    """
    yes = SymbolRef("yes")

    def transform(e: Expr) -> Expr:
        if isinstance(e, DollarConditional):
            value_expr = transform(e.value_expr)
            condition = transform(e.condition)
            if isinstance(value_expr, Const) and value_expr.value == 1.0:
                value_expr = yes
            return DollarConditional(value_expr, condition)

        if isinstance(e, Binary):
            left = transform(e.left)
            right = transform(e.right)
            if e.op == "-" and isinstance(left, Const) and left.value == 1.0:
                left = yes
            return Binary(e.op, left, right)

        if isinstance(e, Call):
            new_args = tuple(transform(arg) for arg in e.args)
            if all(a1 is a2 for a1, a2 in zip(new_args, e.args, strict=True)):
                return e
            return Call(e.func, new_args)

        if isinstance(e, Unary):
            child = transform(e.child)
            if child is e.child:
                return e
            return Unary(e.op, child)

        if isinstance(e, Sum):
            body = transform(e.body)
            cond = transform(e.condition) if e.condition is not None else None
            if body is e.body and cond is e.condition:
                return e
            return Sum(e.index_sets, body, cond)

        if isinstance(e, Prod):
            body = transform(e.body)
            cond = transform(e.condition) if e.condition is not None else None
            if body is e.body and cond is e.condition:
                return e
            return Prod(e.index_sets, body, cond)

        return e

    return transform(expr)


def _collect_set_membership_names(expr: Expr) -> set[str]:
    """Collect all SetMembershipTest set names from an expression tree.

    This walks both the standard ``children()`` interface and index
    expressions on reference nodes (VarRef/ParamRef/MultiplierRef),
    because those are not exposed via ``children()``.  ``IndexOffset``
    indices are ``Expr`` subclasses, so they are handled by the same
    recursive call (``IndexOffset.children()`` yields the offset).
    """
    names: set[str] = set()

    if isinstance(expr, SetMembershipTest):
        names.add(expr.set_name.lower())

    # Recurse into normal children first.
    for child in expr.children():
        names.update(_collect_set_membership_names(child))

    # Explicitly traverse reference indices that are not part of the
    # generic children() interface.  IndexOffset is an Expr subclass,
    # so the isinstance(idx, Expr) check covers it — its children()
    # yields the offset expression for further traversal.
    if isinstance(expr, (VarRef, ParamRef, MultiplierRef)):
        for idx in getattr(expr, "indices", None) or []:
            if isinstance(idx, Expr):
                names.update(_collect_set_membership_names(idx))

    return names


def emit_set_assignments(
    model_ir: ModelIR,
    *,
    varref_filter: str = "all",
    only_indices: list[int] | None = None,
) -> str:
    """Emit dynamic set assignment statements.

    Sprint 18 Day 3: Emit SetAssignment objects stored in model_ir.set_assignments
    as GAMS assignment statements. These are dynamic subset initializations like:
        ku(k) = yes$(ord(k) < card(k));
        ki(k) = yes$(ord(k) = 1);
        kt(k) = not ku(k);
        low(n,nn) = ord(n) > ord(nn);

    Args:
        model_ir: Model IR containing set assignment definitions
        varref_filter: Controls which assignments are emitted based on whether
            they contain attributed VarRef nodes (e.g., ``e.l(i)``), directly
            or transitively through set dependencies:
            - ``"all"``: Emit all assignments (default, backward compatible)
            - ``"no_varref_attr"``: Skip assignments that need deferral
            - ``"only_varref_attr"``: Only emit assignments that need deferral
        only_indices: If not None, only emit set assignments whose index in
            ``model_ir.set_assignments`` is in this list. ``None`` (default)
            emits all assignments; an empty list emits nothing.

    Returns:
        GAMS assignment statements as string

    Example output:
        ku(k) = yes$(ord(k) < card(k));
        low(n,nn) = ord(n) > ord(nn);
    """
    _VALID_VARREF_FILTERS = {"all", "no_varref_attr", "only_varref_attr"}
    if varref_filter not in _VALID_VARREF_FILTERS:
        raise ValueError(
            f"Invalid varref_filter={varref_filter!r}. "
            f"Allowed values: {sorted(_VALID_VARREF_FILTERS)}"
        )

    if not model_ir.set_assignments:
        return ""

    # Issue #1007: Compute which set assignments need deferral (directly
    # contain VarRef attributes, or transitively depend on deferred sets).
    # E.g., it(i) = yes$(e.l(i)) is direct; in(i) = not it(i) is transitive.
    deferred_sets: set[str] = set()
    if varref_filter != "all":
        # Pass 1: identify directly deferred set assignments
        set_deps: dict[str, set[str]] = {}
        for sa in model_ir.set_assignments:
            sa_lower = sa.set_name.lower()
            if _expr_contains_varref_attribute(sa.expr):
                deferred_sets.add(sa_lower)
            set_deps[sa_lower] = _collect_set_membership_names(sa.expr)
        # Pass 2: propagate deferral through transitive dependencies
        changed = True
        while changed:
            changed = False
            for sa_lower, deps in set_deps.items():
                if sa_lower not in deferred_sets and deps & deferred_sets:
                    deferred_sets.add(sa_lower)
                    changed = True

    lines: list[str] = []
    only_indices_set = set(only_indices) if only_indices is not None else None

    for sa_idx, set_assignment in enumerate(model_ir.set_assignments):
        # Issue #881: If only_indices specified, skip set assignments not in the list.
        if only_indices_set is not None and sa_idx not in only_indices_set:
            continue

        # Issue #1007: Filter set assignments based on deferral status.
        if varref_filter != "all":
            is_deferred = set_assignment.set_name.lower() in deferred_sets
            if varref_filter == "no_varref_attr" and is_deferred:
                continue
            if varref_filter == "only_varref_attr" and not is_deferred:
                continue

        # Issue #861: Restore 'yes' keyword for set membership assignments.
        # The parser converts yes → Const(1.0), but GAMS requires 'yes' for
        # set assignment expressions to avoid type mismatch errors.
        restored_expr = _restore_yes_keyword(set_assignment.expr)

        # Convert expression to GAMS syntax
        # Pass indices as domain_vars so they're recognized as domain variables
        # Issue #976: Only include string indices in domain_vars (not IndexOffset)
        domain_vars = frozenset(idx for idx in set_assignment.indices if isinstance(idx, str))
        expr_str = expr_to_gams(restored_expr, domain_vars=domain_vars)

        # Format the LHS with indices
        # Quote symbol names that contain special characters (Issue #665)
        if set_assignment.indices:
            # Issue #976: Use _format_mixed_indices to handle IndexOffset objects
            index_str = _format_mixed_indices(set_assignment.indices, domain_vars)
            lines.append(f"{_quote_symbol(set_assignment.set_name)}({index_str}) = {expr_str};")
        else:
            # Scalar set assignment (rare but possible)
            lines.append(f"{_quote_symbol(set_assignment.set_name)} = {expr_str};")

    return "\n".join(lines)


def emit_subset_value_assignments(
    model_ir: ModelIR,
    *,
    exclude_params: set[str] | None = None,
) -> str:
    """Emit parameter values that use subset-qualified indices as executable assignments.

    Issue #860: When a parameter's inline data contains keys that are set/alias
    names (not element literals), those entries must be emitted as executable
    assignment statements (e.g., ``gamma(in) = 0;``) rather than inline data
    (which GAMS would misinterpret as ``gamma(i) /in 0/``).

    Must be called AFTER set assignments so dynamic subsets are populated.

    Args:
        model_ir: Model IR
        exclude_params: Optional set of lowercase param names to skip (Issue #881).
    """
    sets_and_aliases_lower = {s.lower() for s in model_ir.sets.keys()} | {
        s.lower() for s in model_ir.aliases.keys()
    }
    assignments: list[str] = []

    for param_name, param_def in model_ir.params.items():
        # Issue #881: Skip params handled by interleaved emission
        if exclude_params and param_name.lower() in exclude_params:
            continue
        if not param_def.values or not param_def.domain:
            continue
        domain_size = len(param_def.domain)
        for key_tuple, value in param_def.values.items():
            expanded_key = _expand_table_key(key_tuple, domain_size)
            if expanded_key is None:
                continue
            is_set_flags = tuple(k.lower() in sets_and_aliases_lower for k in expanded_key)
            if not any(is_set_flags):
                continue
            if any(is_set_flags) and not all(is_set_flags):
                logger.debug(
                    "emit_subset_value_assignments: mixed subset/literal key for %s: %r",
                    param_name,
                    expanded_key,
                )
            # Issue #874/#886/#912: Quote indices appropriately.
            # When ALL elements are set names, this is a pure subset-over
            # assignment (e.g., gamma(in) = 0) — keep set names unquoted.
            # When the key is MIXED (some set names, some not), the set-name
            # elements are likely literal collisions (e.g., cases(c1, m) = 10
            # where 'm' is both an element and a set) — quote everything
            # that isn't a domain variable.
            if all(is_set_flags):
                # Pure subset reference — keep set names bare
                quoted_keys = [
                    _quote_assignment_index(k, sets_and_aliases_lower) for k in expanded_key
                ]
            else:
                # Mixed: some elements are set/alias names, others are literals.
                # Use per-position is_set_flags to decide quoting:
                # - is_set=True  → legitimate subset reference, keep bare
                # - is_set=False → literal UEL (possibly colliding with a set
                #   name, e.g., cases(c1,m) where 'm' is both element and set),
                #   force-quote to prevent $170 domain violations.
                quoted_keys = []
                for k, is_set in zip(expanded_key, is_set_flags, strict=True):
                    if is_set:
                        # Legitimate set reference — keep bare (quote only if
                        # the name contains special chars like '-')
                        quoted_keys.append(_quote_assignment_index(k, sets_and_aliases_lower))
                    else:
                        # Literal element — force-quote even if it collides
                        # with a declared set name
                        if (k.startswith('"') and k.endswith('"')) or (
                            k.startswith("'") and k.endswith("'")
                        ):
                            quoted_keys.append(k)
                        else:
                            quoted_keys.append(f"'{k}'")
            index_str = ",".join(quoted_keys)
            assignments.append(
                f"{_quote_symbol(param_name)}({index_str}) = {_format_param_value(value)};"
            )

    return "\n".join(assignments)


def _loop_tree_to_gams(node: object) -> str:
    """Reconstruct GAMS text from a Lark parse tree node.

    Issue #1025: Faithfully converts raw Lark Tree objects back to GAMS
    syntax for loop statement re-emission. Handles the tree node types
    that appear in loop bodies (assign, conditional_assign_general, etc.)
    and loop headers (id_list, index_list, conditions).

    Args:
        node: Lark Token or Tree object

    Returns:
        GAMS text representation
    """
    # Import here to avoid circular dependency — lark is only needed at emit time
    from lark import Token, Tree

    if isinstance(node, Token):
        return str(node)
    if not isinstance(node, Tree):
        return str(node)

    data = str(node.data)

    if data == "id_list":
        return ",".join(_loop_tree_to_gams(c) for c in node.children)
    if data in ("index_list", "arg_list"):
        return ",".join(_loop_tree_to_gams(c) for c in node.children)
    if data == "index_simple":
        # index_simple: ID lag_lead_suffix?
        base = _loop_tree_to_gams(node.children[0])
        if len(node.children) > 1:
            suffix = _loop_tree_to_gams(node.children[1])
            return f"{base}{suffix}"
        return base
    if data in ("circular_lead", "circular_lag", "linear_lead", "linear_lag"):
        # e.g. ++1, --2, +1, -1  — operator token followed by offset
        return "".join(_loop_tree_to_gams(c) for c in node.children)
    if data == "index_subset":
        # index_subset: ID "(" index_list ")" lag_lead_suffix?  e.g. low(n,nn)
        name = _loop_tree_to_gams(node.children[0])
        idx = _loop_tree_to_gams(node.children[1])
        base = f"{name}({idx})"
        if len(node.children) > 2:
            suffix = _loop_tree_to_gams(node.children[2])
            return f"{base}{suffix}"
        return base
    if data == "offset_paren":
        # offset_paren: "(" expr ")"  e.g. (ord(n)-1)
        return f"({_loop_tree_to_gams(node.children[0])})"
    if data == "symbol_indexed":
        name = _loop_tree_to_gams(node.children[0])
        idx = _loop_tree_to_gams(node.children[1])
        return f"{name}({idx})"
    if data in ("symbol_plain", "lvalue", "number", "funccall"):
        return _loop_tree_to_gams(node.children[0])
    if data == "func_call":
        name = _loop_tree_to_gams(node.children[0])
        if len(node.children) > 1:
            args = _loop_tree_to_gams(node.children[1])
            return f"{name}({args})"
        return f"{name}()"
    if data in ("binop", "unaryop"):
        return " ".join(_loop_tree_to_gams(c) for c in node.children)
    if data == "condition":
        # condition: DOLLAR (paren|bracket|cond_bound|ref_indexed|NUMBER|ID)
        # For $(expr) form, Lark discards anonymous parens — detect expr child
        # and wrap it to preserve the original grouping.
        children = [c for c in node.children if isinstance(c, (Tree, Token))]
        parts: list[str] = []
        for c in children:
            if isinstance(c, Tree) and c.data == "expr":
                parts.append(f"({_loop_tree_to_gams(c)})")
            else:
                parts.append(_loop_tree_to_gams(c))
        return "".join(parts)
    if data == "bound_indexed":
        # cond_bound: ID "." BOUND_K "(" index_list ")" -> bound_indexed
        # e.g. x.l(i,j)
        name = _loop_tree_to_gams(node.children[0])
        attr = _loop_tree_to_gams(node.children[1])
        idx = _loop_tree_to_gams(node.children[2])
        return f"{name}.{attr}({idx})"
    if data == "bound_scalar":
        # cond_bound: ID "." BOUND_K -> bound_scalar
        # e.g. x.l
        name = _loop_tree_to_gams(node.children[0])
        attr = _loop_tree_to_gams(node.children[1])
        return f"{name}.{attr}"
    if data in ("set_attr", "attr_access"):
        # set_attr: ID "." SET_ATTR_K  e.g. i.ord
        # attr_access: ID "." ID  e.g. x.val
        return ".".join(_loop_tree_to_gams(c) for c in node.children)
    if data == "attr_access_indexed":
        # ref_bound: ID "." ID "(" index_list ")" -> attr_access_indexed
        # e.g. x.val(i)
        name = _loop_tree_to_gams(node.children[0])
        attr = _loop_tree_to_gams(node.children[1])
        idx = _loop_tree_to_gams(node.children[2])
        return f"{name}.{attr}({idx})"
    if data == "assign":
        # assign: lvalue "=" expr ";"
        return " ".join(_loop_tree_to_gams(c) for c in node.children)
    if data == "conditional_assign_general":
        # conditional_assign_general: lvalue condition "=" expr ";"
        lhs = _loop_tree_to_gams(node.children[0])
        cond = _loop_tree_to_gams(node.children[1])
        rest = " ".join(_loop_tree_to_gams(c) for c in node.children[2:])
        return f"{lhs}{cond} {rest}"
    if data == "loop_body":
        stmts = [_loop_tree_to_gams(c) for c in node.children if isinstance(c, Tree)]
        return "\n".join(f"   {s}" for s in stmts)
    if data == "paren":
        inner = " ".join(_loop_tree_to_gams(c) for c in node.children if isinstance(c, Tree))
        return f"({inner})"
    # sum(domain, expr), prod(domain, expr), smax(domain, expr), smin(domain, expr)
    if data in ("sum", "prod", "smax", "smin"):
        # Skip leading keyword token (SUM_K, PROD_K, etc.) if present
        tree_children = [c for c in node.children if isinstance(c, Tree)]
        if len(tree_children) >= 2:
            domain = _loop_tree_to_gams(tree_children[0])
            body = _loop_tree_to_gams(tree_children[1])
        else:
            domain = _loop_tree_to_gams(node.children[0])
            body = _loop_tree_to_gams(node.children[1])
        return f"{data}({domain}, {body})"
    # sum_domain variants: index_spec, tuple_domain, tuple_domain_cond
    if data == "sum_domain":
        return _loop_tree_to_gams(node.children[0])
    if data == "index_spec":
        # index_spec: index_list [DOLLAR condition]
        # Emit as "i$(cond)" or just "i" if no condition
        idx_parts: list[Tree] = [c for c in node.children if isinstance(c, Tree)]
        idx = _loop_tree_to_gams(idx_parts[0])
        if len(idx_parts) >= 2:
            cond = _loop_tree_to_gams(idx_parts[1])
            return f"{idx}$({cond})"
        return idx
    if data == "tuple_domain":
        return f"({_loop_tree_to_gams(node.children[0])})"
    if data == "tuple_domain_cond":
        # Grammar: "(" index_spec ")" DOLLAR expr -> tuple_domain_cond
        # children[0] = index_spec, children[1] = DOLLAR token, children[2] = expr
        idx = _loop_tree_to_gams(node.children[0])
        cond = _loop_tree_to_gams(node.children[2])
        return f"({idx})$({cond})"
    # dollar_cond: term $ term
    if data == "dollar_cond":
        lhs = _loop_tree_to_gams(node.children[0])
        rhs = _loop_tree_to_gams(node.children[1])
        return f"{lhs}${rhs}"
    # dollar_cond_paren: term $ (expr) or term $ [expr]
    if data == "dollar_cond_paren":
        lhs = _loop_tree_to_gams(node.children[0])
        rhs = _loop_tree_to_gams(node.children[1])
        return f"{lhs}$({rhs})"
    # bracket_expr: [ expr ]
    if data == "bracket_expr":
        return f"[{_loop_tree_to_gams(node.children[0])}]"
    # brace_expr: { expr }
    if data == "brace_expr":
        return f"{{{_loop_tree_to_gams(node.children[0])}}}"
    # yes$cond, no$cond
    if data == "yes_cond":
        return f"yes{_loop_tree_to_gams(node.children[0])}"
    if data == "no_cond":
        return f"no{_loop_tree_to_gams(node.children[0])}"
    # bare yes/no values (YES_K/NO_K without condition)
    if data == "yes_value":
        return "yes"
    if data == "no_value":
        return "no"
    # compile_const: compile_time_const -> %name%
    if data == "compile_const":
        inner = _loop_tree_to_gams(node.children[0])
        return f"%{inner}%"
    if data == "compile_const_path":
        return ".".join(_loop_tree_to_gams(c) for c in node.children)
    if data.startswith("loop_stmt"):
        return _emit_loop_node(node)

    # Fallback: join all children with spaces
    return " ".join(_loop_tree_to_gams(c) for c in node.children)


def _emit_loop_node(node: object) -> str:
    """Emit a complete loop statement from its Lark Tree node.

    Handles all loop variants: simple, paren, filtered, paren_filtered,
    indexed, indexed_filtered.
    """
    from lark import Token, Tree

    if not isinstance(node, Tree):
        return ""

    # Collect parts from the parse tree, handling all loop variants:
    #   loop_stmt:                 id_list, loop_body
    #   loop_stmt_paren:           id_list, loop_body  (anon parens discarded)
    #   loop_stmt_filtered:        ID, DOLLAR, expr|ID[,index_list], loop_body
    #   loop_stmt_paren_filtered:  id_list, DOLLAR, expr|ID[,index_list], loop_body
    #   loop_stmt_indexed:         ID, id_list, loop_body
    #   loop_stmt_indexed_filtered: ID, id_list, DOLLAR, expr, loop_body
    id_list_parts: list[str] = []
    leading_id: str | None = None  # Leading ID token (for filtered/indexed)
    filter_dollar = False
    filter_id: str | None = None
    filter_idx: str | None = None
    filter_expr: str | None = None  # expr after $ (for filtered variants)
    body: str | None = None

    for child in node.children:
        if isinstance(child, Token):
            if child.type == "DOLLAR":
                filter_dollar = True
            elif child.type == "ID":
                if not filter_dollar and leading_id is None:
                    # Before $: loop index or set name
                    leading_id = str(child)
                elif filter_dollar and filter_id is None:
                    # After $: filter identifier
                    filter_id = str(child)
        elif isinstance(child, Tree):
            if child.data == "id_list":
                id_list_parts.append(_loop_tree_to_gams(child))
            elif child.data == "index_list" and filter_dollar:
                filter_idx = _loop_tree_to_gams(child)
            elif child.data in ("expr", "condition") and filter_dollar:
                filter_expr = _loop_tree_to_gams(child)
            elif child.data == "loop_body":
                body = _loop_tree_to_gams(child)

    loop_kind = str(node.data)

    # Build header depending on loop variant
    if "indexed" in loop_kind:
        # loop_stmt_indexed: loop(setname(i,j), ...)
        indices = ",".join(id_list_parts)
        if leading_id:
            header = f"{leading_id}({indices})" if indices else leading_id
        else:
            header = f"({indices})" if indices else "()"
    else:
        # Non-indexed variants:
        #   loop_stmt:                 id_list, loop_body           -> no extra parens
        #   loop_stmt_paren:           id_list, loop_body           -> (id_list)
        #   loop_stmt_filtered:        ID, DOLLAR, ..., loop_body   -> leading_id only
        #   loop_stmt_paren_filtered:  id_list, DOLLAR, ..., body   -> (id_list)$...
        is_paren_variant = loop_kind in ("loop_stmt_paren", "loop_stmt_paren_filtered")
        if id_list_parts:
            core = ",".join(id_list_parts)
            header = f"({core})" if is_paren_variant else core
        elif leading_id:
            # loop_stmt_filtered with single ID: loop(i$..., ...)
            header = leading_id
        else:
            # Fallback for empty id_list
            header = "()" if is_paren_variant else ""

    # Apply filter
    if filter_expr:
        header = f"{header}$({filter_expr})"
    elif filter_id and filter_idx:
        header += f"${filter_id}({filter_idx})"
    elif filter_id:
        header += f"${filter_id}"

    if body:
        return f"loop({header},\n{body}\n);"
    return f"loop({header});"


def _loop_contains_solve(loop_stmt: object) -> bool:
    """Check if a loop body contains a solve statement.

    Loops with solve statements are iterative solve procedures from the
    original model and should NOT be re-emitted in the MCP output.
    """
    from lark import Tree

    from src.ir.symbols import LoopStatement

    if not isinstance(loop_stmt, LoopStatement):
        return False

    def _has_solve(stmts: list[object]) -> bool:
        for stmt in stmts:
            if isinstance(stmt, Tree):
                if "solve" in str(stmt.data):
                    return True
                # Recurse into nested structures
                if _has_solve(list(stmt.children)):
                    return True
        return False

    return _has_solve(loop_stmt.body_stmts)


def _loop_body_only_param_assigns(loop_stmt: object, param_names: set[str]) -> bool:
    """Check if a loop body consists solely of parameter assignments.

    Returns True only when every statement in the loop body is an ``assign``
    or ``conditional_assign_general`` whose LHS target is a known parameter.
    Loops containing display/execute/put/option/variable-attribute
    assignments or any other procedural statements are rejected.
    """
    from lark import Token, Tree

    from src.ir.symbols import LoopStatement

    if not isinstance(loop_stmt, LoopStatement):
        return False

    _ASSIGN_TYPES = {"assign", "conditional_assign_general"}

    def _lhs_name(stmt: Tree) -> str | None:
        """Extract the plain symbol name from the LHS of an assignment."""
        if not stmt.children:
            return None
        lhs = stmt.children[0]
        # Walk down lvalue → symbol_indexed → symbol_plain → ID
        #              or lvalue → symbol_plain → ID
        while isinstance(lhs, Tree) and lhs.data in ("lvalue", "symbol_indexed", "symbol_plain"):
            lhs = lhs.children[0]
        if isinstance(lhs, Token) and lhs.type == "ID":
            return str(lhs).lower()
        return None

    for stmt in loop_stmt.body_stmts:
        if not isinstance(stmt, Tree):
            return False
        if str(stmt.data) not in _ASSIGN_TYPES:
            return False
        name = _lhs_name(stmt)
        if name is None or name not in param_names:
            return False

    return True


def _loop_body_only_var_level_assigns(loop_stmt: object, var_names: set[str]) -> bool:
    """Check if a loop body consists solely of variable ``.l`` assignments.

    Returns True only when every statement in the loop body is an ``assign``
    or ``conditional_assign_general`` whose LHS is a variable ``.l`` attribute
    (e.g., ``r.l(t) = r.l(t-1) - d.l(t)``).

    Issue #1088: Loop-based ``.l`` initialization is sequential and
    order-dependent; it must be emitted as a loop rather than expanded
    into individual element assignments.
    """
    from lark import Token, Tree

    from src.ir.symbols import LoopStatement

    if not isinstance(loop_stmt, LoopStatement):
        return False

    _ASSIGN_TYPES = {"assign", "conditional_assign_general"}

    def _is_var_level_lhs(stmt: Tree) -> bool:
        """Check if LHS is a variable .l attribute (bound_indexed or bound_scalar)."""
        if not stmt.children:
            return False
        lhs = stmt.children[0]
        # Walk through lvalue wrapper
        while isinstance(lhs, Tree) and lhs.data == "lvalue":
            lhs = lhs.children[0]
        if not isinstance(lhs, Tree):
            return False
        if lhs.data not in ("bound_indexed", "bound_scalar"):
            return False
        # bound_indexed: ID "." BOUND_K "(" index_list ")"
        # bound_scalar: ID "." BOUND_K
        # children[0] = ID (variable name), children[1] = BOUND_K (l/lo/up/fx)
        if len(lhs.children) < 2:
            return False
        var_name = lhs.children[0]
        bound_kind = lhs.children[1]
        if not isinstance(var_name, Token) or not isinstance(bound_kind, Token):
            return False
        return str(var_name).lower() in var_names and str(bound_kind).lower() == "l"

    for stmt in loop_stmt.body_stmts:
        if not isinstance(stmt, Tree):
            return False
        if str(stmt.data) not in _ASSIGN_TYPES:
            return False
        if not _is_var_level_lhs(stmt):
            return False

    return True


def emit_loop_statements(model_ir: ModelIR) -> str:
    """Emit loop statements that contain only parameter assignments.

    Issue #1025: Loop bodies may contain parameter assignments that are not
    captured in ParameterDef.values/expressions. This function re-emits
    only those loop statements whose bodies consist exclusively of
    assignments to known parameters (e.g., wbar3, vbar3, sigmay3).

    Loops are skipped when they:
    - contain solve statements (iterative solve procedures)
    - are while statements (iterative procedures)
    - contain non-assignment statements (display, execute, put, etc.)
    - assign to variables or other non-parameter symbols

    Args:
        model_ir: Model IR with loop_statements

    Returns:
        GAMS loop statement code, or empty string if no qualifying loops
    """
    if not model_ir.loop_statements:
        return ""

    param_names = {name.lower() for name in model_ir.params}

    lines: list[str] = []
    for loop_stmt in model_ir.loop_statements:
        if loop_stmt.raw_node is None:
            continue
        # Skip while_stmt nodes — they are iterative procedures, not parameter init
        if getattr(loop_stmt.raw_node, "data", None) == "while_stmt":
            continue
        if _loop_contains_solve(loop_stmt):
            continue
        if not _loop_body_only_param_assigns(loop_stmt, param_names):
            continue
        lines.append(_loop_tree_to_gams(loop_stmt.raw_node))

    return "\n\n".join(lines)


def emit_pre_solve_param_assignments(model_ir: ModelIR) -> str:
    """Emit parameter assignments from before the first solve in solve-containing loops.

    Issue #1101/#1102: Multi-solve loops like ``loop(t, p(i) = pt(i,t); solve ...;)``
    contain pre-solve parameter assignments that are needed for the MCP output.
    The loop itself is skipped (it contains a solve), but the pre-solve
    parameter assignments must be emitted with the loop index substituted
    by the first element of its set.

    Args:
        model_ir: Model IR with loop_statements and sets

    Returns:
        GAMS assignment statements, or empty string if none found
    """
    from lark import Token, Tree

    from src.ir.symbols import LoopStatement

    if not model_ir.loop_statements:
        return ""

    param_names = {name.lower() for name in model_ir.params}
    _ASSIGN_TYPES = {"assign", "conditional_assign_general"}

    def _lhs_name(stmt: Tree) -> str | None:
        if not stmt.children:
            return None
        lhs = stmt.children[0]
        while isinstance(lhs, Tree) and lhs.data in ("lvalue", "symbol_indexed", "symbol_plain"):
            lhs = lhs.children[0]
        if isinstance(lhs, Token) and lhs.type == "ID":
            return str(lhs).lower()
        return None

    def _tree_to_gams_subst(node: object, subst: dict[str, str]) -> str:
        """Like _loop_tree_to_gams but substitutes loop index tokens."""
        if isinstance(node, Token):
            if node.type == "ID" and str(node).lower() in subst:
                return subst[str(node).lower()]
            return str(node)
        if not isinstance(node, Tree):
            return str(node)
        data = str(node.data)
        if data == "index_simple":
            base = node.children[0]
            if isinstance(base, Token) and base.type == "ID" and str(base).lower() in subst:
                val = subst[str(base).lower()]
                if len(node.children) > 1:
                    suffix = _tree_to_gams_subst(node.children[1], subst)
                    return f"{val}{suffix}"
                return val
        # Fall through to _loop_tree_to_gams for all other cases,
        # but we need recursion with substitution — re-dispatch children.
        return _loop_tree_to_gams_subst_dispatch(node, subst)

    def _loop_tree_to_gams_subst_dispatch(node: Tree, subst: dict[str, str]) -> str:
        """Dispatch to _loop_tree_to_gams logic but with token substitution."""
        data = str(node.data)
        if data == "id_list":
            return ",".join(_tree_to_gams_subst(c, subst) for c in node.children)
        if data in ("index_list", "arg_list"):
            return ",".join(_tree_to_gams_subst(c, subst) for c in node.children)
        if data == "index_simple":
            base = _tree_to_gams_subst(node.children[0], subst)
            if len(node.children) > 1:
                suffix = _tree_to_gams_subst(node.children[1], subst)
                return f"{base}{suffix}"
            return base
        if data in ("circular_lead", "circular_lag", "linear_lead", "linear_lag"):
            return "".join(_tree_to_gams_subst(c, subst) for c in node.children)
        if data == "index_subset":
            name = _tree_to_gams_subst(node.children[0], subst)
            idx = _tree_to_gams_subst(node.children[1], subst)
            base = f"{name}({idx})"
            if len(node.children) > 2:
                suffix = _tree_to_gams_subst(node.children[2], subst)
                return f"{base}{suffix}"
            return base
        if data == "offset_paren":
            return f"({_tree_to_gams_subst(node.children[0], subst)})"
        if data == "symbol_indexed":
            name = _tree_to_gams_subst(node.children[0], subst)
            idx = _tree_to_gams_subst(node.children[1], subst)
            return f"{name}({idx})"
        if data in ("symbol_plain", "lvalue", "number", "funccall"):
            return _tree_to_gams_subst(node.children[0], subst)
        if data == "func_call":
            name = _tree_to_gams_subst(node.children[0], subst)
            if len(node.children) > 1:
                args = _tree_to_gams_subst(node.children[1], subst)
                return f"{name}({args})"
            return f"{name}()"
        if data in ("binop", "unaryop"):
            return " ".join(_tree_to_gams_subst(c, subst) for c in node.children)
        if data == "condition":
            children = [c for c in node.children if isinstance(c, (Tree, Token))]
            parts: list[str] = []
            for c in children:
                if isinstance(c, Tree) and c.data == "expr":
                    parts.append(f"({_tree_to_gams_subst(c, subst)})")
                else:
                    parts.append(_tree_to_gams_subst(c, subst))
            return "".join(parts)
        if data == "assign":
            return " ".join(_tree_to_gams_subst(c, subst) for c in node.children)
        if data == "conditional_assign_general":
            lhs = _tree_to_gams_subst(node.children[0], subst)
            cond = _tree_to_gams_subst(node.children[1], subst)
            rest = " ".join(_tree_to_gams_subst(c, subst) for c in node.children[2:])
            return f"{lhs}{cond} {rest}"
        if data == "expr":
            return " ".join(_tree_to_gams_subst(c, subst) for c in node.children)
        # Fallback: join children
        return " ".join(_tree_to_gams_subst(c, subst) for c in node.children)

    assign_lines: list[str] = []
    emitted_params: set[str] = set()
    for loop_stmt in model_ir.loop_statements:
        if not isinstance(loop_stmt, LoopStatement):
            continue
        if not _loop_contains_solve(loop_stmt):
            continue
        if not loop_stmt.indices:
            continue

        # Build substitution: each loop index -> first element of its set
        subst: dict[str, str] = {}
        for idx_name in loop_stmt.indices:
            idx_lower = idx_name.lower()
            sdef = model_ir.sets.get(idx_lower)
            if sdef and sdef.members:
                first_elem = sdef.members[0]
                subst[idx_lower] = f"'{first_elem}'"

        if not subst:
            continue

        # Extract pre-solve param assignments
        for stmt in loop_stmt.body_stmts:
            if not isinstance(stmt, Tree):
                break
            if "solve" in str(stmt.data):
                break
            if str(stmt.data) not in _ASSIGN_TYPES:
                continue
            name = _lhs_name(stmt)
            if name is None or name not in param_names:
                continue
            # Emit this assignment with loop index substituted
            gams_text = _tree_to_gams_subst(stmt, subst)
            assign_lines.append(gams_text)
            emitted_params.add(name)

    if not assign_lines:
        return ""

    # Emit declarations for params that were skipped by Issue #917 logic
    # (no values, no expressions — only assigned inside solve loops)
    decl_lines: list[str] = []
    for pname in sorted(emitted_params):
        pdef = model_ir.params.get(pname)
        if pdef and not pdef.values and not pdef.expressions and pdef.domain:
            domain_str = ",".join(pdef.domain)
            decl_lines.append(f"Parameter {pname}({domain_str});")

    return "\n".join(decl_lines + assign_lines)


def get_var_level_loop_varnames(model_ir: ModelIR) -> set[str]:
    """Return lowercase variable names whose ``.l`` is assigned inside loops.

    Issue #1088: Variables initialized by loop-based ``.l`` assignments
    should not receive default POSITIVE initialization (e.g., ``r.l(t) = 1``)
    because the loop provides the correct sequential values.
    """
    from lark import Token, Tree

    from src.ir.symbols import LoopStatement

    if not model_ir.loop_statements:
        return set()

    var_names = {name.lower() for name in model_ir.variables}
    result: set[str] = set()

    for loop_stmt in model_ir.loop_statements:
        if not isinstance(loop_stmt, LoopStatement):
            continue
        if loop_stmt.raw_node is None:
            continue
        if getattr(loop_stmt.raw_node, "data", None) == "while_stmt":
            continue
        if _loop_contains_solve(loop_stmt):
            continue
        if not _loop_body_only_var_level_assigns(loop_stmt, var_names):
            continue
        # Extract variable names from each .l assignment LHS
        for stmt in loop_stmt.body_stmts:
            if not isinstance(stmt, Tree):
                continue
            lhs = stmt.children[0] if stmt.children else None
            while isinstance(lhs, Tree) and lhs.data == "lvalue":
                lhs = lhs.children[0]
            if isinstance(lhs, Tree) and lhs.data in ("bound_indexed", "bound_scalar"):
                if len(lhs.children) >= 2 and isinstance(lhs.children[0], Token):
                    vn = str(lhs.children[0]).lower()
                    if vn in var_names:
                        result.add(vn)

    return result


def emit_var_level_loop_statements(model_ir: ModelIR) -> str:
    """Emit loop statements that contain variable ``.l`` assignments.

    Issue #1088: Some models initialize variable levels sequentially via
    loops (e.g., ``loop(t$to(t), r.l(t) = r.l(t-1) - d.l(t))``).
    These must be emitted as loops rather than expanded into individual
    assignments because they are order-dependent.

    This function should be called AFTER regular ``.l`` initialization
    so that non-loop ``.l`` values are available for the loop body.

    Args:
        model_ir: Model IR with loop_statements

    Returns:
        GAMS loop statement code, or empty string if no qualifying loops
    """
    if not model_ir.loop_statements:
        return ""

    var_names = {name.lower() for name in model_ir.variables}

    lines: list[str] = []
    for loop_stmt in model_ir.loop_statements:
        if loop_stmt.raw_node is None:
            continue
        if getattr(loop_stmt.raw_node, "data", None) == "while_stmt":
            continue
        if _loop_contains_solve(loop_stmt):
            continue
        if not _loop_body_only_var_level_assigns(loop_stmt, var_names):
            continue
        lines.append(_loop_tree_to_gams(loop_stmt.raw_node))

    return "\n\n".join(lines)

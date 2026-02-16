"""GAMS code generation templates for KKT systems.

This module provides template functions for emitting GAMS code from KKT systems,
with variable kind preservation (Finding #4 from final review).
"""

from src.ir.model_ir import ModelIR
from src.ir.symbols import VarKind
from src.kkt.kkt_system import KKTSystem


def _build_dynamic_subset_map(model_ir: ModelIR) -> dict[str, str]:
    """Build a mapping from dynamically assigned subset names to their parent sets.

    Issue #739: GAMS forbids dynamically assigned sets (populated via assignment
    statements like ``im(i) = yes$dat("cons-imp",i)``) from being used as
    declaration domains for variables and equations. This function identifies
    such sets so the emitter can replace them with their parent sets in
    declarations.

    A set qualifies as a dynamic subset if:
    1. It appears in ``model_ir.set_assignments`` (has a runtime assignment), AND
    2. It has no static members (``SetDef.members`` is empty), AND
    3. It has a single-element domain (subset of exactly one parent set)

    Args:
        model_ir: Model IR containing set definitions and assignments

    Returns:
        Dict mapping lowercase dynamic subset name to parent set name
        (e.g., ``{"im": "i", "ie": "i"}``)
    """
    dynamic_set_names = {sa.set_name.lower() for sa in model_ir.set_assignments}
    result: dict[str, str] = {}
    for set_name, set_def in model_ir.sets.items():
        name_lower = set_name.lower()
        if name_lower in dynamic_set_names and not set_def.members and len(set_def.domain) == 1:
            result[name_lower] = set_def.domain[0]
    return result


def _remap_domain(domain: tuple[str, ...], dynamic_map: dict[str, str]) -> tuple[str, ...]:
    """Replace dynamic subset names in a domain tuple with their parent sets.

    Args:
        domain: Original domain tuple (e.g., ``("im",)``)
        dynamic_map: Mapping from dynamic subset name (lowercase) to parent set

    Returns:
        Remapped domain tuple (e.g., ``("i",)``)
    """
    return tuple(dynamic_map.get(d.lower(), d) for d in domain)


def emit_variables(kkt: KKTSystem) -> str:
    """Emit Variables blocks grouped by VariableDef.kind.

    **CRITICAL (Finding #4)**: Preserves variable kinds from source model.
    Primal variables grouped by their kind (Positive/Binary/Integer/etc.).
    Multipliers added to appropriate groups:
    - Free multipliers (ν for equalities) → CONTINUOUS
    - Positive multipliers (λ, π^L, π^U) → POSITIVE

    Args:
        kkt: KKT system containing variables and multipliers

    Returns:
        GAMS Variables blocks as string

    Example output:
        Variables
            obj           "Objective variable"
            nu_balance    "Multiplier for balance equation"
        ;

        Positive Variables
            x
            lam_g1        "Multiplier for inequality g1"
            piL_x         "Multiplier for lower bound on x"
            piU_x         "Multiplier for upper bound on x"
        ;

        Binary Variables
            y             "Binary decision variable"
        ;
    """
    # Issue #739: Build dynamic subset → parent set mapping for declarations
    dynamic_map = _build_dynamic_subset_map(kkt.model_ir)

    # Group variables by kind (Finding #4)
    var_groups: dict[VarKind, list[tuple[str, tuple[str, ...]]]] = {
        VarKind.CONTINUOUS: [],
        VarKind.POSITIVE: [],
        VarKind.NEGATIVE: [],
        VarKind.BINARY: [],
        VarKind.INTEGER: [],
    }

    # Group primal variables by kind
    for var_name, var_def in kkt.model_ir.variables.items():
        var_groups[var_def.kind].append((var_name, var_def.domain))

    # Add multipliers to appropriate groups
    # Free multipliers (ν for equalities) → CONTINUOUS
    for mult_name, mult_def in kkt.multipliers_eq.items():
        var_groups[VarKind.CONTINUOUS].append((mult_name, mult_def.domain))

    # Positive multipliers (λ, π^L, π^U) → POSITIVE
    for mult_name, mult_def in kkt.multipliers_ineq.items():
        var_groups[VarKind.POSITIVE].append((mult_name, mult_def.domain))

    # Bound multipliers use tuple keys (var_name, indices)
    # Deduplicate by collecting unique (name, domain) pairs to avoid
    # emitting the same indexed variable declaration multiple times
    seen_bound_multipliers: set[tuple[str, tuple[str, ...]]] = set()

    for (_var_name, _indices), mult_def in kkt.multipliers_bounds_lo.items():
        key = (mult_def.name, mult_def.domain)
        if key not in seen_bound_multipliers:
            seen_bound_multipliers.add(key)
            var_groups[VarKind.POSITIVE].append(key)

    for (_var_name, _indices), mult_def in kkt.multipliers_bounds_up.items():
        key = (mult_def.name, mult_def.domain)
        if key not in seen_bound_multipliers:
            seen_bound_multipliers.add(key)
            var_groups[VarKind.POSITIVE].append(key)

    # Note: Min/max complementarity multipliers are added automatically as part of
    # kkt.multipliers_ineq (they're regular inequality multipliers)

    # Emit blocks
    lines: list[str] = []

    kind_to_block = {
        VarKind.CONTINUOUS: "Variables",
        VarKind.POSITIVE: "Positive Variables",
        VarKind.NEGATIVE: "Negative Variables",
        VarKind.BINARY: "Binary Variables",
        VarKind.INTEGER: "Integer Variables",
    }

    for kind, block_name in kind_to_block.items():
        if var_groups[kind]:
            if lines:  # Add blank line between blocks
                lines.append("")
            lines.append(block_name)
            for var_name, domain in var_groups[kind]:
                if domain:
                    # Issue #739: Replace dynamic subsets with parent sets in declarations
                    decl_domain = _remap_domain(domain, dynamic_map)
                    domain_indices = ",".join(decl_domain)
                    lines.append(f"    {var_name}({domain_indices})")
                else:
                    lines.append(f"    {var_name}")
            lines.append(";")

    return "\n".join(lines)


def emit_kkt_sets(kkt: KKTSystem) -> str:
    """Emit Sets block for KKT system indexing.

    Extracts unique index sets from multiplier and equation domains.

    Args:
        kkt: KKT system

    Returns:
        GAMS Sets block for KKT indices

    Example output:
        Sets
            eq_rows   /balance, flow/
            ineq_rows /capacity, demand/
        ;
    """
    # For now, return empty as this is typically handled by original model sets
    # This placeholder will be expanded in future if needed
    return ""


def emit_equations(kkt: KKTSystem) -> str:
    """Emit Equations block declarations.

    Declares all equation names (stationarity, complementarity, equality).
    For indexed equations, includes domain in declaration.

    Args:
        kkt: KKT system

    Returns:
        GAMS Equations block

    Example output:
        Equations
            stat_x
            stat_y
            comp_g1
            comp_balance(i)
            comp_lo_x
            eq_balance(i)
        ;
    """
    # Issue #739: Build dynamic subset → parent set mapping for declarations
    dynamic_map = _build_dynamic_subset_map(kkt.model_ir)

    def _decl_domain_str(domain: tuple[str, ...]) -> str:
        """Format a domain tuple for declaration, remapping dynamic subsets."""
        remapped = _remap_domain(domain, dynamic_map)
        return ",".join(remapped)

    lines = ["Equations"]

    # Stationarity equations
    for eq_name, eq_def in sorted(kkt.stationarity.items()):
        # Include domain if present
        if eq_def.domain:
            lines.append(f"    {eq_name}({_decl_domain_str(eq_def.domain)})")
        else:
            lines.append(f"    {eq_name}")

    # Inequality complementarity equations (includes min/max complementarity)
    for eq_name in sorted(kkt.complementarity_ineq.keys()):
        comp_pair = kkt.complementarity_ineq[eq_name]
        eq_def = comp_pair.equation
        # Include domain if present
        if eq_def.domain:
            lines.append(f"    {eq_def.name}({_decl_domain_str(eq_def.domain)})")
        else:
            lines.append(f"    {eq_def.name}")

    # Bound complementarity equations
    for key in sorted(kkt.complementarity_bounds_lo.keys()):
        comp_pair = kkt.complementarity_bounds_lo[key]
        eq_def = comp_pair.equation
        # Include domain if present
        if eq_def.domain:
            lines.append(f"    {eq_def.name}({_decl_domain_str(eq_def.domain)})")
        else:
            lines.append(f"    {eq_def.name}")

    for key in sorted(kkt.complementarity_bounds_up.keys()):
        comp_pair = kkt.complementarity_bounds_up[key]
        eq_def = comp_pair.equation
        # Include domain if present
        if eq_def.domain:
            lines.append(f"    {eq_def.name}({_decl_domain_str(eq_def.domain)})")
        else:
            lines.append(f"    {eq_def.name}")

    # Original equality equations (declared here, also used in Model MCP section)
    # Note: Equalities can be in either equations dict or normalized_bounds dict
    from ..ir.normalize import NormalizedEquation
    from ..ir.symbols import EquationDef

    for eq_name in sorted(kkt.model_ir.equalities):
        # Check both equations dict and normalized_bounds dict
        # Fixed variables (.fx) create equalities stored in normalized_bounds
        eq_domain: tuple[str, ...]
        if eq_name in kkt.model_ir.equations:
            eq_or_norm: EquationDef = kkt.model_ir.equations[eq_name]
            eq_domain = eq_or_norm.domain
        elif eq_name in kkt.model_ir.normalized_bounds:
            eq_or_norm_2: NormalizedEquation = kkt.model_ir.normalized_bounds[eq_name]
            # NormalizedEquation uses 'domain_sets' instead of 'domain'
            eq_domain = eq_or_norm_2.domain_sets
        else:
            raise ValueError(
                f"Equation '{eq_name}' is in equalities list but not found in "
                f"equations dict or normalized_bounds dict. "
                f"This indicates a data inconsistency in the ModelIR."
            )

        # Check if it has domain (indexed)
        if eq_domain:
            lines.append(f"    {eq_name}({_decl_domain_str(eq_domain)})")
        else:
            lines.append(f"    {eq_name}")

    lines.append(";")

    return "\n".join(lines)


def emit_equation_definitions(kkt: KKTSystem) -> tuple[str, set[str]]:
    """Emit equation definitions (eq_name.. lhs =E= rhs;).

    Delegates to src.emit.equations for the actual implementation.

    Handles index aliasing to avoid GAMS Error 125 ("Set is under control already")
    when an equation's domain index is reused in a nested sum expression.

    Args:
        kkt: KKT system

    Returns:
        Tuple of (GAMS equation definitions string, set of indices needing aliases)

    Note:
        The return type is `tuple[str, set[str]]` to support index aliasing.
        Callers must unpack the tuple:
        `equations_str, aliases = emit_equation_definitions(kkt)`
    """
    from src.emit.equations import emit_equation_definitions as _emit_eq_defs

    return _emit_eq_defs(kkt)


def emit_model(kkt: KKTSystem) -> str:
    """Emit Model MCP block with complementarity pairs.

    This is a placeholder for Day 6 implementation.

    Args:
        kkt: KKT system

    Returns:
        Empty string (to be implemented Day 6)
    """
    # Day 6: Will implement Model MCP syntax
    return ""


def emit_solve(kkt: KKTSystem) -> str:
    """Emit Solve statement.

    This is a placeholder for Day 6 implementation.

    Args:
        kkt: KKT system

    Returns:
        Empty string (to be implemented Day 6)
    """
    # Day 6: Will implement Solve statement
    return ""

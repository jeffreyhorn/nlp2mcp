"""AST to GAMS expression converter.

This module converts IR expression AST nodes to GAMS syntax strings.
Handles operator precedence, function calls, and all AST node types including MultiplierRef.

Also handles index aliasing for sum expressions to avoid GAMS Error 125
("Set is under control already") when an equation's domain index is reused
in a nested sum.
"""

import math

from src.ir.ast import (
    Binary,
    Call,
    Const,
    DollarConditional,
    EquationRef,
    Expr,
    IndexOffset,
    LhsConditionalAssign,
    ModelAttrRef,
    MultiplierRef,
    ParamRef,
    Prod,
    SetAttrRef,
    SetMembershipTest,
    Sum,
    SymbolRef,
    Unary,
    VarRef,
)
from src.ir.constants import GAMS_RESERVED_CONSTANTS

# Operator precedence levels (higher = tighter binding)
PRECEDENCE = {
    "or": 1,
    "and": 2,
    "=": 3,
    "==": 3,  # IR alias for "=" — mapped to "=" at emission
    "<>": 3,
    "!=": 3,  # IR alias for "<>" — mapped to "<>" at emission
    "<": 3,
    ">": 3,
    "<=": 3,
    ">=": 3,
    "+": 4,
    "-": 4,
    "*": 5,
    "/": 5,
    "^": 6,  # Power operator (highest precedence)
    "**": 6,  # Alternative power operator syntax (same precedence as ^)
}


def _format_numeric(value: int | float) -> str:
    """Format numeric value for GAMS, avoiding unnecessary decimals.

    Handles special IEEE values:
    - +Inf → 'inf' (GAMS native syntax)
    - -Inf → '-inf' (parentheses, when needed, are added by expression handlers)
    - NaN → 'na' (GAMS native syntax for Not Available)

    Args:
        value: Numeric value to format

    Returns:
        Formatted string representation

    Examples:
        >>> _format_numeric(3.0)
        '3'
        >>> _format_numeric(3.14)
        '3.14'
        >>> _format_numeric(5)
        '5'
        >>> _format_numeric(float('inf'))
        'inf'
        >>> _format_numeric(float('-inf'))
        '-inf'
    """
    if isinstance(value, float):
        if math.isinf(value):
            return "inf" if value > 0 else "-inf"
        if math.isnan(value):
            return "na"
    if isinstance(value, (int, float)) and value == int(value):
        return str(int(value))
    return str(value)


def _is_index_offset_syntax(s: str, domain_vars: frozenset[str] | None = None) -> bool:
    """Check if a string looks like GAMS IndexOffset syntax (i++1, i--2, i+1, i-3, i+j).

    These patterns are already valid GAMS index expressions and should NOT be quoted.
    Must be careful not to match element labels like "route-1", "item-2", or "food+agr".

    GAMS allows both + and - in element labels (e.g., food+agr, light-ind from chenery.gms),
    so we use conservative heuristics:
    - Circular operators (++, --) are unambiguous IndexOffset syntax
    - Numeric offsets (i+1, tt+1, i-1) are unambiguous IndexOffset syntax
    - Symbolic offsets with single-letter base (i+j, t-k) are treated as IndexOffset
    - Symbolic offsets with multi-letter base require domain_vars context to disambiguate

    Args:
        s: String to check
        domain_vars: Optional set of known domain variable names. When provided,
                     multi-letter expressions like "tt-1" or "tt+j" are recognized
                     as IndexOffset if "tt" is in domain_vars.

    Returns:
        True if the string matches IndexOffset GAMS syntax patterns

    Examples:
        >>> _is_index_offset_syntax("i++1")
        True
        >>> _is_index_offset_syntax("t--10")
        True
        >>> _is_index_offset_syntax("i+j")
        True
        >>> _is_index_offset_syntax("i-3")
        True
        >>> _is_index_offset_syntax("i+shift")
        True
        >>> _is_index_offset_syntax("t-offset1")
        True
        >>> _is_index_offset_syntax("i++shift_1")
        True
        >>> _is_index_offset_syntax("t--lag_2")
        True
        >>> _is_index_offset_syntax("tt+1")
        True
        >>> _is_index_offset_syntax("tt-1", frozenset(["tt"]))
        True
        >>> _is_index_offset_syntax("tt+j", frozenset(["tt"]))
        True
        >>> _is_index_offset_syntax("i1")
        False
        >>> _is_index_offset_syntax("H2O")
        False
        >>> _is_index_offset_syntax("route-1")
        False
        >>> _is_index_offset_syntax("item-2")
        False
        >>> _is_index_offset_syntax("food+agr")  # Element label, not IndexOffset
        False
    """
    import re

    if domain_vars is None:
        domain_vars = frozenset()

    # Circular operators (++ and --) are unambiguous IndexOffset syntax
    # Pattern: identifier base ++ or -- followed by either:
    #   - a numeric offset (e.g., i++1, t--10, tt++1), or
    #   - an identifier offset (e.g., i++shift, tt++shift_1)
    # Sprint 18 Day 3: Extended to support multi-letter bases like 'tt', 'np'
    # Circular syntax is unambiguous since ++ and -- aren't valid in element labels
    circular_pattern = r"^[A-Za-z_][A-Za-z0-9_]*(\+\+|--)([0-9]+|[A-Za-z_][A-Za-z0-9_]*)$"
    if re.match(circular_pattern, s):
        return True

    # Linear lead with + and numeric offset is unambiguous (i+1, tt+1)
    # Sprint 18 Day 3: Extended to support multi-letter bases (tt+1, np+1)
    linear_lead_numeric = r"^[A-Za-z_][A-Za-z0-9_]*\+[0-9]+$"  # i+1, tt+1
    if re.match(linear_lead_numeric, s):
        return True

    # Linear lead with symbolic offset is AMBIGUOUS: "i+j" vs "food+agr"
    # GAMS allows + in element labels (e.g., food+agr, pulp+paper from chenery.gms)
    # For single-letter bases, always match as IndexOffset (i+j, t+k)
    linear_lead_symbolic_single = r"^[a-zA-Z]\+[A-Za-z_][A-Za-z0-9_]*$"  # i+j, t+k
    if re.match(linear_lead_symbolic_single, s):
        return True

    # For multi-letter bases with +, check if base is a known domain variable
    # If "tt" is in domain_vars, then "tt+j" is IndexOffset, not element label
    multi_lead_symbolic = r"^([A-Za-z_][A-Za-z0-9_]*)\+[A-Za-z_][A-Za-z0-9_]*$"
    match = re.match(multi_lead_symbolic, s)
    if match and match.group(1) in domain_vars:
        return True

    # Linear lag with - is AMBIGUOUS: "route-1" vs "tt-1"
    # For single-letter bases, always match as IndexOffset
    linear_lag_numeric = r"^[a-zA-Z]-[0-9]+$"  # i-1, t-3 (single letter only)
    if re.match(linear_lag_numeric, s):
        return True

    linear_lag_symbolic = r"^[a-zA-Z]-[A-Za-z_][A-Za-z0-9_]*$"  # i-j, t-k (single letter only)
    if re.match(linear_lag_symbolic, s):
        return True

    # PR #658: For multi-letter bases, check if base is a known domain variable
    # If "tt" is in domain_vars, then "tt-1" is IndexOffset, not "tt minus one" label
    multi_lag_pattern = r"^([A-Za-z_][A-Za-z0-9_]*)-([0-9]+|[A-Za-z_][A-Za-z0-9_]*)$"
    match = re.match(multi_lag_pattern, s)
    if match and match.group(1) in domain_vars:
        return True

    return False


def _format_mixed_indices(
    indices: tuple[str | IndexOffset, ...], domain_vars: frozenset[str] | None = None
) -> str:
    """Format a tuple of mixed indices (strings and IndexOffset) for GAMS syntax.

    This function handles both string indices (which need quoting logic) and
    IndexOffset objects (which are emitted directly without quoting).

    Sprint 18 Day 3: Fixes P2 issue where IndexOffset expressions like tt+1 were
    being quoted as "tt+1" because they passed through _quote_indices as strings.
    By keeping IndexOffset objects separate, we preserve the semantic information
    that these are lag/lead expressions, not hyphenated element labels.

    Args:
        indices: Tuple of string indices or IndexOffset objects
        domain_vars: Set of known domain variable names (not quoted)

    Returns:
        Comma-separated string of formatted indices

    Examples:
        >>> _format_mixed_indices(("r", IndexOffset("tt", Const(1), False)))
        'r,tt+1'
        >>> _format_mixed_indices(("i", "j"), frozenset(["i", "j"]))
        'i,j'
        >>> _format_mixed_indices(("route-1",))  # Element label
        '"route-1"'
    """
    if domain_vars is None:
        domain_vars = frozenset()

    result: list[str] = []
    string_indices: list[str] = []

    for idx in indices:
        if isinstance(idx, IndexOffset):
            # Flush any accumulated string indices first
            if string_indices:
                result.extend(_quote_indices(tuple(string_indices), domain_vars))
                string_indices = []
            # IndexOffset objects are emitted directly - never quoted
            result.append(idx.to_gams_string())
        else:
            # Accumulate string indices for batch processing
            string_indices.append(idx)

    # Flush remaining string indices
    if string_indices:
        result.extend(_quote_indices(tuple(string_indices), domain_vars))

    return ",".join(result)


def _quote_indices(
    indices: tuple[str, ...], domain_vars: frozenset[str] | None = None
) -> list[str]:
    """Quote element labels in index tuples for GAMS syntax.

    This function uses context and heuristics to distinguish between domain variables
    (set indices like 'i', 'j', 'nodes') and element labels (specific values like 'i1', 'H2').

    Args:
        indices: Tuple of index identifiers
        domain_vars: Optional set of identifiers that are known domain variables
                     (e.g., from enclosing sum expressions). These are never quoted.

    Heuristic (when domain_vars context is not available):
    - Indices in domain_vars are domain variables → unquoted
    - IndexOffset syntax (i++1, i--2, i+1, i-3, i+j) are valid GAMS expressions → unquoted
    - Single/two-char lowercase identifiers (i, j, ii, np) are likely domain variables → unquoted
    - Indices that arrive already quoted (e.g., "demand") are element labels → quoted
    - Multi-char lowercase identifiers (cod, land, apr) are likely element labels → quoted
    - Names with digits or uppercase are element labels → quoted

    This addresses GAMS compilation errors from inconsistent quoting (Error 120, 171, 340)
    while preserving correct behavior for indexed equations.

    Returns:
        List of appropriately quoted/unquoted indices

    Examples:
        >>> _quote_indices(("i",))
        ['i']
        >>> _quote_indices(("i1",))
        ['"i1"']
        >>> _quote_indices(("i", "j"))
        ['i', 'j']
        >>> _quote_indices(("crep",), frozenset(["crep"]))  # crep in domain context
        ['crep']
        >>> _quote_indices(("cod",))  # cod without domain context
        ['"cod"']
        >>> _quote_indices(('"demand"',))
        ['"demand"']
        >>> _quote_indices(("i++1",))
        ['i++1']
    """
    if domain_vars is None:
        domain_vars = frozenset()
    # Subcategory E: Precompute lowercase set for case-insensitive matching
    # (GAMS is case-insensitive: set 'j' can be referenced as 'J')
    domain_vars_lower = frozenset(dv.lower() for dv in domain_vars)
    result = []
    for idx in indices:
        # Strip ALL layers of quotes to handle double-quoted indices like ""cost""
        # This can happen when indices pass through multiple transformations
        was_quoted = False
        idx_clean = idx
        while True:
            if idx_clean.startswith('"') and idx_clean.endswith('"') and len(idx_clean) >= 2:
                idx_clean = idx_clean[1:-1]
                was_quoted = True
            elif idx_clean.startswith("'") and idx_clean.endswith("'") and len(idx_clean) >= 2:
                idx_clean = idx_clean[1:-1]
                was_quoted = True
            else:
                break

        # If it was quoted, it's an element label - always quote it (single layer)
        if was_quoted:
            result.append(f'"{idx_clean}"')
        # Sprint 19 Day 2: GAMS reserved constants (inf, na, eps, etc.) must always be quoted
        # when used as set element indices, even in domain_vars context.
        elif idx_clean.lower() in GAMS_RESERVED_CONSTANTS:
            result.append(f'"{idx_clean}"')
        # Sprint 18 Day 2: If index is in domain_vars context, it's a domain variable - don't quote
        # Subcategory E: Use case-insensitive matching because GAMS is case-insensitive
        # (e.g., set declared as 'j' but referenced as 'J' in SAM("TRF",J))
        elif idx_clean in domain_vars or idx_clean.lower() in domain_vars_lower:
            result.append(idx_clean)
        # IndexOffset syntax (i++1, i--2, i+1, i-3, i+j) is valid GAMS - don't quote
        # PR #658: Pass domain_vars to support multi-letter lag detection (tt-1)
        elif _is_index_offset_syntax(idx_clean, domain_vars):
            result.append(idx_clean)
        # Sprint 18 Day 2: Refined heuristic for domain variables vs element literals
        # Only single/two-character lowercase identifiers are treated as domain variables.
        # Multi-character all-lowercase identifiers (like 'cod', 'land', 'apr', 'water')
        # are likely element literals and should be quoted.
        # This fixes GAMS Error 120/340 where element labels are misinterpreted as set names.
        elif len(idx_clean) == 1 and idx_clean.isalpha() and idx_clean.islower():
            # Single lowercase letter like 'i', 'j', 'k', 'c', 't' - domain variable
            result.append(idx_clean)
        elif idx_clean.replace("_", "").isalpha() and idx_clean.islower() and len(idx_clean) <= 2:
            # Two-letter lowercase identifiers like 'ii', 'jj', 'np', 'nn' - likely domain variables
            result.append(idx_clean)
        else:
            # Everything else is an element label, quote it for consistency
            # This includes multi-character lowercase names like 'cod', 'land', 'apr', 'water'
            result.append(f'"{idx_clean}"')
    return result


def _needs_parens(parent_op: str | None, child_op: str | None, is_right: bool = False) -> bool:
    """Determine if child expression needs parentheses.

    Args:
        parent_op: Operator of parent expression (None if no parent)
        child_op: Operator of child expression (None if not a binary op)
        is_right: Whether child is the right operand of parent

    Returns:
        True if parentheses are needed
    """
    if parent_op is None or child_op is None:
        return False

    parent_prec = PRECEDENCE.get(parent_op, 0)
    child_prec = PRECEDENCE.get(child_op, 0)

    # Lower precedence always needs parens
    if child_prec < parent_prec:
        return True

    # Equal precedence on right side needs parens for non-associative ops
    # e.g., a - (b - c) vs a - b - c
    if child_prec == parent_prec and is_right:
        # Subtraction and division are left-associative
        if parent_op in ("-", "/"):
            return True

    # Power is non-associative in GAMS — both (a^b)^c and a^(b^c) must
    # parenthesize the nested child regardless of side.
    if parent_op in ("^", "**") and child_op in ("^", "**"):
        return True

    return False


def expr_to_gams(
    expr: Expr,
    parent_op: str | None = None,
    is_right: bool = False,
    domain_vars: frozenset[str] | None = None,
) -> str:
    """Convert an AST expression to GAMS syntax.

    Args:
        expr: Expression AST node
        parent_op: Operator of parent expression (for precedence handling)
        is_right: Whether this is the right operand of parent
        domain_vars: Set of identifiers that are currently in scope as domain variables
                     (from enclosing sum expressions or equation domain). These are not quoted.

    Returns:
        GAMS expression string

    Examples:
        >>> expr_to_gams(Const(3.14))
        '3.14'
        >>> expr_to_gams(VarRef("x", ("i",)))
        'x(i)'
        >>> expr_to_gams(Binary("+", Const(1), Const(2)))
        '1 + 2'
        >>> expr_to_gams(Binary("^", VarRef("x", ()), Const(2)))
        'sqr(x)'
    """
    if domain_vars is None:
        domain_vars = frozenset()
    match expr:
        case Const(value):
            return _format_numeric(value)

        case SymbolRef(name):
            return name

        case VarRef() as var_ref:
            # Issue #741: Support variable attribute access (e.g., x.l, v.m)
            attr_suffix = f".{var_ref.attribute}" if var_ref.attribute else ""
            if var_ref.indices:
                indices_str = _format_mixed_indices(var_ref.indices, domain_vars)
                return f"{var_ref.name}{attr_suffix}({indices_str})"
            return f"{var_ref.name}{attr_suffix}"

        case ParamRef() as param_ref:
            if param_ref.indices:
                indices_str = _format_mixed_indices(param_ref.indices, domain_vars)
                return f"{param_ref.name}({indices_str})"
            return param_ref.name

        case MultiplierRef() as mult_ref:
            if mult_ref.indices:
                indices_str = _format_mixed_indices(mult_ref.indices, domain_vars)
                return f"{mult_ref.name}({indices_str})"
            return mult_ref.name

        case EquationRef() as eq_ref:
            # Equation attribute access: eq.m, eq.l('1'), etc.
            if eq_ref.indices:
                indices_str = _format_mixed_indices(eq_ref.indices, domain_vars)
                return f"{eq_ref.name}.{eq_ref.attribute}({indices_str})"
            return f"{eq_ref.name}.{eq_ref.attribute}"

        case SetAttrRef() as sa_ref:
            # Set attribute access: ss.off, ss.pos, etc.
            return f"{sa_ref.name}.{sa_ref.attribute}"

        case ModelAttrRef() as ma_ref:
            # Model attribute access: m.modelStat, m.solveStat, etc.
            # After MCP transformation the original model may not exist;
            # emit as mcp_model attribute reference.
            return f"mcp_model.{ma_ref.attribute}"

        case Unary(op, child):
            child_str = expr_to_gams(child, parent_op=op, domain_vars=domain_vars)
            # GAMS unary operators: +, -, not
            # For unary minus, ALWAYS convert to multiplication form to avoid GAMS Error 445
            # ("More than one operator in a row"). This happens when unary minus follows
            # other operators like ".." (equation definition), "+", "-", etc.
            # Solution: -(expr) becomes ((-1) * (expr)) which GAMS parses correctly.
            if op == "-":
                # Wrap child in parentheses if it's a complex expression (Binary or Call)
                # or a negative constant (to avoid ((-1) * -5) which has two operators in a row)
                # Simple cases like -x become (-1) * x, complex like -(a+b) become (-1) * (a+b)
                is_negative_const = isinstance(child, Const) and child.value < 0
                if isinstance(child, (Binary, Call)) or is_negative_const:
                    return f"((-1) * ({child_str}))"
                else:
                    return f"((-1) * {child_str})"
            # Sprint 18 Day 3: Handle 'not' operator with required space
            # Issue #730: Always parenthesize 'not' expressions to avoid GAMS Error 445
            # ("More than one operator in a row") when 'not' follows another operator,
            # e.g., ((-1) * not sa(i)) must become ((-1) * (not sa(i))).
            if op == "not":
                return f"(not {child_str})"
            # Unary plus can be passed through directly
            return f"{op}{child_str}"

        case Binary(op, left, right):
            # Convert power operator to GAMS syntax
            # Handle both ^ and ** (term collection may generate **)
            if op in ("^", "**"):
                # Use sqr() for x**2 — GAMS rPower rejects negative bases
                # (e.g. (-1)**2 raises FUNC DOMAIN) but sqr() handles them (#982).
                if isinstance(right, Const) and right.value == 2.0:
                    left_str = expr_to_gams(
                        left, parent_op=None, is_right=False, domain_vars=domain_vars
                    )
                    result = f"sqr({left_str})"
                    needs_parens = _needs_parens(parent_op, "**", is_right)
                    return f"({result})" if needs_parens else result

                # GAMS uses ** for exponentiation
                left_str = expr_to_gams(left, parent_op=op, is_right=False, domain_vars=domain_vars)
                right_str = expr_to_gams(
                    right, parent_op=op, is_right=True, domain_vars=domain_vars
                )

                # Subcategory D: GAMS Error $445 ("more than one operator in a row")
                # when the exponent is negative, e.g., x ** -0.9904. GAMS requires
                # parentheses: x ** (-0.9904). Wrap the exponent in parens if it
                # starts with a bare minus sign (not already parenthesized).
                if right_str.startswith("-"):
                    right_str = f"({right_str})"

                # Determine if we need parentheses for the whole expression
                needs_parens = _needs_parens(parent_op, op, is_right)
                result = f"{left_str} ** {right_str}"
                return f"({result})" if needs_parens else result

            # Special handling for subtraction of negative constants
            # Convert "x - (-5)" to "x + 5" to avoid double operators
            if op == "-" and isinstance(right, Const) and right.value < 0:
                left_str = expr_to_gams(
                    left, parent_op="+", is_right=False, domain_vars=domain_vars
                )
                # Negate the negative value to get positive
                right_val = -right.value
                right_str = _format_numeric(right_val)
                # Use addition instead
                needs_parens = _needs_parens(parent_op, "+", is_right)
                result = f"{left_str} + {right_str}"
                return f"({result})" if needs_parens else result

            # Other binary operators
            left_str = expr_to_gams(left, parent_op=op, is_right=False, domain_vars=domain_vars)
            right_str = expr_to_gams(right, parent_op=op, is_right=True, domain_vars=domain_vars)

            # Special handling: wrap negative constants in parentheses to avoid GAMS Error 445
            # ("More than one operator in a row").
            #
            # For multiplication/division, GAMS cannot parse negative constants without parens:
            # - Left operand: "a + -1 * b" is invalid → becomes "a + (-1) * b"
            # - Right operand: "y * -1" is invalid → becomes "y * (-1)"
            #
            # Other operators like exponentiation (**) don't currently need this fix.
            if op in ("*", "/") and isinstance(left, Const) and left.value < 0:
                left_str = f"({left_str})"
            if op in ("*", "/") and isinstance(right, Const) and right.value < 0:
                right_str = f"({right_str})"

            # Issue #1003: Map Python/IR comparison operators to GAMS equivalents.
            # GAMS uses = (not ==) for equality and <> (not !=) for inequality.
            gams_op = {"==": "=", "!=": "<>"}.get(op, op)

            # Determine if we need parentheses
            needs_parens = _needs_parens(parent_op, op, is_right)
            result = f"{left_str} {gams_op} {right_str}"
            return f"({result})" if needs_parens else result

        case Sum(index_sets, body, condition):
            # GAMS: sum(i$cond, body) or sum((i,j), body)
            extended_domain_vars = domain_vars | frozenset(index_sets)
            body_str = expr_to_gams(body, domain_vars=extended_domain_vars)
            domain_str = _agg_domain_str(index_sets, condition, extended_domain_vars)
            return f"sum({domain_str}, {body_str})"

        case Prod(index_sets, body, condition):
            # GAMS: prod(i$cond, body) or prod((i,j), body) — Issue #709
            extended_domain_vars = domain_vars | frozenset(index_sets)
            body_str = expr_to_gams(body, domain_vars=extended_domain_vars)
            domain_str = _agg_domain_str(index_sets, condition, extended_domain_vars)
            return f"prod({domain_str}, {body_str})"

        case Call(func, args):
            # Function calls: exp(x), log(x), sqrt(x), etc.

            # Issue #1056: smax/smin with multi-index domains need tuple
            # parentheses: smax((i,kp), fx(i,kp)) not smax(i, kp, fx(i,kp)).
            # The parser stores args as [SymbolRef(idx)..., optional_cond, body].
            if func in ("smax", "smin") and len(args) >= 2:
                # Collect leading SymbolRef args as domain indices
                domain_indices: list[str] = []
                for arg in args:
                    if isinstance(arg, SymbolRef):
                        domain_indices.append(arg.name)
                    else:
                        break
                if domain_indices:
                    remaining = args[len(domain_indices) :]
                    extended_domain_vars = domain_vars | frozenset(domain_indices)
                    # Last remaining arg is the body; anything before it is a condition
                    body_str = expr_to_gams(remaining[-1], domain_vars=extended_domain_vars)
                    if len(domain_indices) == 1:
                        idx_str = domain_indices[0]
                    else:
                        idx_str = "(" + ",".join(domain_indices) + ")"
                    if len(remaining) > 1:
                        # There's a condition expression before the body
                        cond_str = expr_to_gams(remaining[0], domain_vars=extended_domain_vars)
                        return f"{func}({idx_str}$({cond_str}), {body_str})"
                    return f"{func}({idx_str}, {body_str})"

            # Issue #724: In this emitter, GAMS power(base, exp) is only used when the exponent is an integer.
            # Issue #904: AD can produce non-integer Const exponents (e.g.,
            # d/dx[x^0.5] = 0.5 * power(x, -0.5)). Use ** for non-integer
            # Const exponents and ParamRef exponents (may be non-integer
            # at runtime). Only keep power() for integer Const exponents.
            if func == "power" and len(args) == 2:
                exponent = args[1]
                use_infix = not isinstance(exponent, Const)
                if isinstance(exponent, Const):
                    value = exponent.value
                    if isinstance(value, float):
                        # Avoid int() on non-finite floats (inf, nan); treat as requiring infix.
                        if (not math.isfinite(value)) or (not value.is_integer()):
                            use_infix = True
                    else:
                        if value != int(value):
                            use_infix = True
                if use_infix:
                    base_str = expr_to_gams(
                        args[0], parent_op="**", is_right=False, domain_vars=domain_vars
                    )
                    exp_str = expr_to_gams(
                        args[1], parent_op="**", is_right=True, domain_vars=domain_vars
                    )
                    # Wrap negative exponents in parens (GAMS Error $445)
                    if exp_str.startswith("-"):
                        exp_str = f"({exp_str})"
                    result = f"{base_str} ** {exp_str}"
                    if _needs_parens(parent_op, "**", is_right):
                        return f"({result})"
                    return result
            args_str = ", ".join(expr_to_gams(arg, domain_vars=domain_vars) for arg in args)
            return f"{func}({args_str})"

        case DollarConditional(value_expr, condition):
            # Dollar conditional: value_expr$condition
            # Evaluates to value_expr if condition is non-zero, otherwise 0
            value_str = expr_to_gams(value_expr, domain_vars=domain_vars)
            condition_str = expr_to_gams(condition, domain_vars=domain_vars)
            # Parenthesize value if it's a complex expression to avoid precedence issues
            if isinstance(value_expr, (Binary, Unary, DollarConditional)):
                value_str = f"({value_str})"
            # Issue #1003: Always parenthesize the dollar condition.
            # GAMS requires $(cond) when the condition is a function-like
            # expression such as a SetMembershipTest (e.g., $t(tl) must be
            # $(t(tl))). Since $(...) is always valid GAMS syntax, always
            # wrapping is safe and avoids ambiguity for all condition types.
            condition_str = f"({condition_str})"
            return f"{value_str}${condition_str}"

        case SetMembershipTest(set_name, indices):
            # Set membership test: set_name(indices)
            # In GAMS conditional context, tests if index combination is in set
            if indices:
                indices_str = ",".join(
                    expr_to_gams(idx, domain_vars=domain_vars) for idx in indices
                )
                return f"{set_name}({indices_str})"
            return set_name

        case LhsConditionalAssign(rhs=rhs_expr):
            # LhsConditionalAssign in expression context: emit only the RHS.
            # The LHS condition is handled at the assignment/statement level
            # (e.g., in emit_gams.py bound emission or original_symbols.py).
            # When this node reaches expr_to_gams() directly (e.g., via KKT
            # equation expressions), only the value matters, not the condition.
            return expr_to_gams(
                rhs_expr, parent_op=parent_op, is_right=is_right, domain_vars=domain_vars
            )

        case _:
            # Fallback for unknown node types
            raise ValueError(f"Unknown expression type: {type(expr).__name__}")


def _agg_domain_str(
    index_sets: tuple[str, ...],
    condition: Expr | None,
    domain_vars: frozenset[str],
) -> str:
    """Format the domain part of sum/prod: 'i', '(i,j)', 'i$cond', '(i,j)$cond'."""
    if len(index_sets) == 1:
        idx_str = index_sets[0]
    else:
        idx_str = "(" + ",".join(index_sets) + ")"
    if condition is not None:
        cond_str = expr_to_gams(condition, domain_vars=domain_vars)
        return f"{idx_str}$({cond_str})"
    return idx_str


def _make_alias_name(index: str, taken: set[str] | frozenset[str] | None = None) -> str:
    """Create an alias name for an index to avoid conflicts.

    Uses double underscore suffix to create unique alias names that are
    unlikely to conflict with user-defined sets. When the first-choice alias
    is already taken (e.g., in nested scopes), appends increasing numeric
    suffixes to guarantee uniqueness.

    Args:
        index: Original index name (canonical lowercase)
        taken: Set of lowercase names already bound in current scope.
            When provided, the alias is guaranteed not to collide.

    Returns:
        Aliased index name

    Examples:
        >>> _make_alias_name("i")
        'i__'
        >>> _make_alias_name("i", frozenset({"i__"}))
        'i__2'
    """
    candidate = f"{index}__"
    if taken is None or candidate.lower() not in taken:
        return candidate
    # First choice taken — append increasing numeric suffixes
    n = 2
    while True:
        candidate = f"{index}__{n}"
        if candidate.lower() not in taken:
            return candidate
        n += 1


def collect_index_aliases(expr: Expr, equation_domain: tuple[str, ...]) -> set[str]:
    """Collect all indices that need aliases due to conflicts.

    Detects two conflict patterns:
    1. Sum/Prod index collides with equation domain (case-insensitive)
    2. Inner Sum/Prod index collides with outer Sum/Prod index (nested reuse)

    Args:
        expr: Expression to analyze
        equation_domain: Tuple of index names used in the equation's domain

    Returns:
        Set of canonical lowercase index names that need aliases
    """
    # Use case-insensitive comparison (GAMS is case-insensitive for identifiers)
    domain_set_lower = {d.lower() for d in equation_domain}
    aliases_needed: set[str] = set()

    def _collect(e: Expr, bound: frozenset[str]) -> None:
        match e:
            case Sum(index_sets, body, condition) | Prod(index_sets, body, condition):
                # Check for conflicts with equation domain or outer bound indices
                for idx in index_sets:
                    idx_lower = idx.lower()
                    if idx_lower in domain_set_lower or idx_lower in bound:
                        aliases_needed.add(idx_lower)
                # Recurse with expanded bound set
                new_bound = bound | frozenset(idx.lower() for idx in index_sets)
                if condition is not None:
                    _collect(condition, new_bound)
                _collect(body, new_bound)

            case Binary(_, left, right):
                _collect(left, bound)
                _collect(right, bound)

            case Unary(_, child):
                _collect(child, bound)

            case Call(_, args):
                for arg in args:
                    _collect(arg, bound)

            case DollarConditional(value_expr, condition):
                _collect(value_expr, bound)
                _collect(condition, bound)

            case SetMembershipTest() as smt:
                for smt_idx in smt.indices:
                    _collect(smt_idx, bound)

            case LhsConditionalAssign(rhs, condition):
                _collect(rhs, bound)
                _collect(condition, bound)

            case (
                VarRef()
                | ParamRef()
                | MultiplierRef()
                | EquationRef()
                | Const()
                | SymbolRef()
                | SetAttrRef()
                | ModelAttrRef()
            ):
                pass

            case _:
                pass

    _collect(expr, frozenset())
    return aliases_needed


def resolve_index_conflicts(
    expr: Expr, equation_domain: tuple[str, ...]
) -> tuple[Expr, dict[str, list[str]]]:
    """Resolve index conflicts by replacing conflicting sum indices with aliases.

    Handles two conflict patterns:
    1. Sum/Prod index collides with equation domain (case-insensitive)
    2. Inner Sum/Prod index collides with outer Sum/Prod index (nested reuse)

    Args:
        expr: Expression to transform
        equation_domain: Tuple of index names used in the equation's domain

    Returns:
        Tuple of (new expression with conflicts resolved, dict mapping canonical
        lowercase base index names to lists of alias names generated for them).
        For example: {"i": ["i__", "i__2"]} when ``i`` is aliased at two nesting
        levels.
    """
    # Use case-insensitive comparison for conflict detection
    domain_set_lower = {d.lower() for d in equation_domain}
    # Accumulate all generated aliases: base_lower -> [alias1, alias2, ...]
    generated_aliases: dict[str, list[str]] = {}

    def _resolve(e: Expr, active_aliases: dict[str, str], bound_lower: frozenset[str]) -> Expr:
        """Recursively resolve conflicts, tracking active alias substitutions."""
        match e:
            case Sum(index_sets, body, condition) | Prod(index_sets, body, condition):
                # Check which indices conflict and need aliasing
                agg_indices: list[str] = []
                new_aliases = dict(active_aliases)  # Copy current aliases

                for idx in index_sets:
                    idx_lower = idx.lower()
                    if idx_lower in domain_set_lower or idx_lower in bound_lower:
                        # This index conflicts - use alias (canonicalized to lowercase).
                        # Pass current bound + domain as 'taken' so nested scopes
                        # get unique aliases (e.g., i__ then i__2).
                        taken = (
                            domain_set_lower
                            | bound_lower
                            | frozenset(a.lower() for a in agg_indices)
                        )
                        alias = _make_alias_name(idx_lower, taken)
                        agg_indices.append(alias)
                        # Track alias under lowercase key for case-insensitive substitution
                        new_aliases[idx_lower] = alias
                        # Record the generated alias for Alias declaration emission
                        generated_aliases.setdefault(idx_lower, []).append(alias)
                    else:
                        agg_indices.append(idx)

                # Recurse with expanded bound set based on emitted agg_indices
                # (not original index_sets) so nested sums see alias names too
                new_bound = bound_lower | frozenset(idx.lower() for idx in agg_indices)
                new_condition = (
                    _resolve(condition, new_aliases, new_bound) if condition is not None else None
                )
                new_body = _resolve(body, new_aliases, new_bound)
                agg_class = type(e)  # Sum or Prod
                return agg_class(tuple(agg_indices), new_body, new_condition)

            case Binary(op, left, right):
                new_left = _resolve(left, active_aliases, bound_lower)
                new_right = _resolve(right, active_aliases, bound_lower)
                return Binary(op, new_left, new_right)

            case Unary(op, child):
                new_child = _resolve(child, active_aliases, bound_lower)
                return Unary(op, new_child)

            case Call(func, args):
                new_args = tuple(_resolve(arg, active_aliases, bound_lower) for arg in args)
                return Call(func, new_args)

            case DollarConditional(value_expr, condition):
                new_value = _resolve(value_expr, active_aliases, bound_lower)
                new_condition = _resolve(condition, active_aliases, bound_lower)
                return DollarConditional(new_value, new_condition)

            case SetMembershipTest(set_name, indices):
                new_indices = tuple(_resolve(idx, active_aliases, bound_lower) for idx in indices)
                return SetMembershipTest(set_name, new_indices)

            case LhsConditionalAssign(rhs, condition):
                new_rhs = _resolve(rhs, active_aliases, bound_lower)
                new_cond = _resolve(condition, active_aliases, bound_lower)
                return LhsConditionalAssign(rhs=new_rhs, condition=new_cond)

            case VarRef() as var_ref:
                if var_ref.indices and active_aliases:
                    var_indices: tuple[str | IndexOffset, ...] = tuple(
                        active_aliases.get(idx.lower(), idx) if isinstance(idx, str) else idx
                        for idx in var_ref.indices
                    )
                    if var_indices != var_ref.indices:
                        return VarRef(var_ref.name, var_indices)
                return var_ref

            case ParamRef() as param_ref:
                if param_ref.indices and active_aliases:
                    param_indices: tuple[str | IndexOffset, ...] = tuple(
                        active_aliases.get(idx.lower(), idx) if isinstance(idx, str) else idx
                        for idx in param_ref.indices
                    )
                    if param_indices != param_ref.indices:
                        return ParamRef(param_ref.name, param_indices)
                return param_ref

            case MultiplierRef() as mult_ref:
                if mult_ref.indices and active_aliases:
                    mult_indices: tuple[str | IndexOffset, ...] = tuple(
                        active_aliases.get(idx.lower(), idx) if isinstance(idx, str) else idx
                        for idx in mult_ref.indices
                    )
                    if mult_indices != mult_ref.indices:
                        return MultiplierRef(mult_ref.name, mult_indices)
                return mult_ref

            case EquationRef() as eq_ref:
                if eq_ref.indices and active_aliases:
                    eq_indices: tuple[str | IndexOffset, ...] = tuple(
                        active_aliases.get(idx.lower(), idx) if isinstance(idx, str) else idx
                        for idx in eq_ref.indices
                    )
                    if eq_indices != eq_ref.indices:
                        return EquationRef(eq_ref.name, eq_indices, eq_ref.attribute)
                return eq_ref

            case SymbolRef(name) if active_aliases and name.lower() in active_aliases:
                return SymbolRef(active_aliases[name.lower()])

            case Const() | SymbolRef() | SetAttrRef() | ModelAttrRef():
                return e

            case _:
                return e

    resolved = _resolve(expr, {}, frozenset())
    return resolved, generated_aliases

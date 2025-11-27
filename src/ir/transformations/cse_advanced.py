"""Advanced Common Subexpression Elimination (CSE) transformations.

This module implements T5.2 (Nested CSE) and T5.3 (Multiplicative CSE)
for aggressive simplification mode.

Patterns:
- T5.2: Nested CSE - Replace repeated complex subexpressions
- T5.3: Multiplicative CSE - Replace repeated multiplication patterns

Example:
    # T5.2: Nested CSE
    (x*y + z)^2 + 3*(x*y + z) + sin(x*y + z) → t1 = x*y + z; t1^2 + 3*t1 + sin(t1)

    # T5.3: Multiplicative CSE
    x*y*a + x*y*b + x*y*c → t1 = x*y; t1*a + t1*b + t1*c

Priority: LOW (optional CSE features, high reuse threshold required)

Note: CSE transformations create temporary variables, which changes the
expression structure significantly. They should only be applied when:
1. The subexpression appears many times (≥3 for nested, ≥4 for multiplicative)
2. Cost savings justify the overhead
3. All algebraic simplifications have been exhausted
"""

from collections import defaultdict

from src.ir.ast import Binary, Call, Const, Expr, SymbolRef, VarRef


def nested_cse(expr: Expr, min_occurrences: int = 3) -> tuple[Expr, dict[str, Expr]]:
    """Apply nested CSE - extract repeated complex subexpressions.

    Algorithm:
    1. Traverse expression tree to collect all subexpressions with counts
    2. Build dependency graph (which subexpressions contain others)
    3. Topologically sort candidates by dependency order
    4. Extract candidates with occurrence count ≥ threshold
    5. Replace occurrences with temporary variable references

    Args:
        expr: Expression to transform
        min_occurrences: Minimum occurrences required for CSE (default: 3)

    Returns:
        Tuple of (transformed expression, dict mapping temp names to definitions)

    Example:
        >>> # (x+y)^2 + 3*(x+y) + sin(x+y)
        >>> x, y = SymbolRef("x"), SymbolRef("y")
        >>> xy = Binary("+", x, y)
        >>> expr = Binary("+", Binary("+", Binary("**", xy, Const(2)),
        ...                            Binary("*", Const(3), xy)),
        ...               Call("sin", (xy,)))
        >>> result, temps = nested_cse(expr, min_occurrences=3)
        >>> # result references t1, temps = {"t1": x+y}
    """
    # Step 1: Collect subexpressions with counts
    subexpr_counts: dict[str, tuple[Expr, int]] = {}
    _collect_subexpressions(expr, subexpr_counts)

    # Step 2 & 3: Filter candidates and build dependency graph
    candidates = {
        key: (subexpr, count)
        for key, (subexpr, count) in subexpr_counts.items()
        if count >= min_occurrences and _is_cse_candidate(subexpr)
    }

    if not candidates:
        return expr, {}

    # Step 4: Sort candidates by dependency (innermost first)
    sorted_candidates = _topological_sort_candidates(candidates)

    # Step 5: Generate temporary variables and replace
    temps: dict[str, Expr] = {}
    result_expr = expr

    for i, (_key, (subexpr, _count)) in enumerate(sorted_candidates):
        temp_name = f"t{i + 1}"
        temp_ref = SymbolRef(temp_name)

        # Store the definition
        temps[temp_name] = subexpr

        # Replace all occurrences in result expression
        result_expr = _replace_subexpression(result_expr, subexpr, temp_ref)

        # Also update temp definitions to use previously extracted temps
        # Only iterate over temps that existed before this iteration
        existing_temp_names = list(temps.keys())[:-1]  # Exclude the just-added temp
        for existing_temp_name in existing_temp_names:
            temps[existing_temp_name] = _replace_subexpression(
                temps[existing_temp_name], subexpr, temp_ref
            )

    return result_expr, temps


def multiplicative_cse(expr: Expr, min_occurrences: int = 4) -> tuple[Expr, dict[str, Expr]]:
    """Apply multiplicative CSE - extract repeated multiplication patterns.

    Algorithm:
    1. Traverse expression tree to collect multiplication subexpressions
    2. Count occurrences of each multiplication pattern
    3. Calculate cost savings for each candidate
    4. Extract candidates with positive cost savings

    Note: Factoring (T1.2) often produces better results than CSE for
    multiplication patterns. This transformation only applies when factoring
    is not applicable.

    Args:
        expr: Expression to transform
        min_occurrences: Minimum occurrences required for CSE (default: 4)

    Returns:
        Tuple of (transformed expression, dict mapping temp names to definitions)

    Example:
        >>> # x*y*a + x*y*b + x*y*c + x*y*d
        >>> x, y = SymbolRef("x"), SymbolRef("y")
        >>> a, b, c, d = SymbolRef("a"), SymbolRef("b"), SymbolRef("c"), SymbolRef("d")
        >>> # Build x*y*a + x*y*b + x*y*c + x*y*d expression...
        >>> result, temps = multiplicative_cse(expr, min_occurrences=4)
        >>> # result uses m1 for x*y, temps = {"m1": x*y}
    """
    # Step 1: Collect multiplication subexpressions with counts
    mult_counts: dict[str, tuple[Expr, int]] = {}
    _collect_multiplicative_subexpressions(expr, mult_counts)

    # Step 2: Filter candidates by occurrence threshold and cost savings
    candidates = []
    for key, (subexpr, count) in mult_counts.items():
        if count >= min_occurrences:
            # Cost model: multiplication = 2, assignment = 1
            # Savings = (cost * reuse_count) - cost - 1
            cost = 2
            savings = (cost * count) - cost - 1
            if savings > 0:
                candidates.append((key, subexpr, count, savings))

    if not candidates:
        return expr, {}

    # Sort by savings (highest first)
    candidates.sort(key=lambda x: x[3], reverse=True)

    # Step 3: Generate temporary variables and replace
    temps: dict[str, Expr] = {}
    result_expr = expr

    for i, (_key, subexpr, _count, _savings) in enumerate(candidates):
        temp_name = f"m{i + 1}"  # Use 'm' prefix for multiplicative temps
        temp_ref = SymbolRef(temp_name)

        # Store the definition
        temps[temp_name] = subexpr

        # Replace all occurrences
        result_expr = _replace_subexpression(result_expr, subexpr, temp_ref)

    return result_expr, temps


def _collect_subexpressions(expr: Expr, counts: dict[str, tuple[Expr, int]]) -> None:
    """Collect all subexpressions with occurrence counts.

    Args:
        expr: Expression to traverse
        counts: Dictionary to populate with {expr_key: (expr, count)}
    """
    # Generate a key for this expression
    key = _expression_key(expr)

    # Update count
    if key in counts:
        counts[key] = (expr, counts[key][1] + 1)
    else:
        counts[key] = (expr, 1)

    # Recursively collect from subexpressions
    if isinstance(expr, Binary):
        _collect_subexpressions(expr.left, counts)
        _collect_subexpressions(expr.right, counts)
    elif isinstance(expr, Call):
        for arg in expr.args:
            _collect_subexpressions(arg, counts)


def _collect_multiplicative_subexpressions(expr: Expr, counts: dict[str, tuple[Expr, int]]) -> None:
    """Collect only multiplication subexpressions with occurrence counts.

    Args:
        expr: Expression to traverse
        counts: Dictionary to populate with {expr_key: (expr, count)}
    """
    # Only count multiplication expressions
    if isinstance(expr, Binary) and expr.op == "*":
        key = _expression_key(expr)
        if key in counts:
            counts[key] = (expr, counts[key][1] + 1)
        else:
            counts[key] = (expr, 1)

    # Recursively traverse
    if isinstance(expr, Binary):
        _collect_multiplicative_subexpressions(expr.left, counts)
        _collect_multiplicative_subexpressions(expr.right, counts)
    elif isinstance(expr, Call):
        for arg in expr.args:
            _collect_multiplicative_subexpressions(arg, counts)


def _expression_key(expr: Expr) -> str:
    """Generate a unique string key for an expression.

    Uses structural representation to identify identical subexpressions.

    Args:
        expr: Expression to generate key for

    Returns:
        Unique string key
    """
    if isinstance(expr, Const):
        return f"Const({expr.value})"
    elif isinstance(expr, SymbolRef):
        return f"SymbolRef({expr.name})"
    elif isinstance(expr, VarRef):
        return f"VarRef({expr.name})"
    elif isinstance(expr, Binary):
        left_key = _expression_key(expr.left)
        right_key = _expression_key(expr.right)
        return f"Binary({expr.op},{left_key},{right_key})"
    elif isinstance(expr, Call):
        args_keys = ",".join(_expression_key(arg) for arg in expr.args)
        return f"Call({expr.func},{args_keys})"
    else:
        return f"{type(expr).__name__}({id(expr)})"


def _is_cse_candidate(expr: Expr) -> bool:
    """Check if expression is a valid CSE candidate.

    Candidates must be:
    - Not a simple constant or variable (too cheap to extract)
    - Composite expressions (Binary, Call)

    Args:
        expr: Expression to check

    Returns:
        True if valid CSE candidate
    """
    # Exclude simple constants and variables
    if isinstance(expr, (Const, SymbolRef, VarRef)):
        return False

    # Only consider composite expressions
    return isinstance(expr, (Binary, Call))


def _topological_sort_candidates(
    candidates: dict[str, tuple[Expr, int]],
) -> list[tuple[str, tuple[Expr, int]]]:
    """Sort CSE candidates by dependency order (innermost first).

    Ensures that nested subexpressions are extracted before their containers.

    Args:
        candidates: Dictionary of {key: (expr, count)}

    Returns:
        List of (key, (expr, count)) tuples sorted by dependencies
    """
    # Build dependency graph: expr -> [exprs that contain it]
    dependencies: dict[str, list[str]] = defaultdict(list)

    for key, (expr, _count) in candidates.items():
        # Find which other candidates contain this expression
        for other_key, (other_expr, _other_count) in candidates.items():
            if key != other_key and _contains_subexpression(other_expr, expr):
                dependencies[key].append(other_key)

    # Topological sort using DFS
    visited: set[str] = set()
    result: list[tuple[str, tuple[Expr, int]]] = []

    def visit(key: str) -> None:
        if key in visited:
            return
        visited.add(key)

        # Visit dependents first (expressions that contain this one)
        for dependent in dependencies.get(key, []):
            visit(dependent)

        result.append((key, candidates[key]))

    for key in candidates:
        visit(key)

    return result


def _contains_subexpression(container: Expr, target: Expr) -> bool:
    """Check if container expression contains target as a subexpression.

    Note: Returns True if container and target are the same expression.
    This is intentional for the topological sort algorithm, which uses this
    function to detect dependencies between CSE candidates. An expression
    containing itself creates a self-loop that gets handled correctly by
    the topological sort.

    Args:
        container: Expression to search in
        target: Expression to search for

    Returns:
        True if target is found as a subexpression of container (including if they're the same)
    """
    if _expression_key(container) == _expression_key(target):
        return True

    if isinstance(container, Binary):
        return _contains_subexpression(container.left, target) or _contains_subexpression(
            container.right, target
        )
    elif isinstance(container, Call):
        return any(_contains_subexpression(arg, target) for arg in container.args)

    return False


def _replace_subexpression(expr: Expr, target: Expr, replacement: Expr) -> Expr:
    """Replace all occurrences of target subexpression with replacement.

    Args:
        expr: Expression to transform
        target: Subexpression to replace
        replacement: Expression to replace with

    Returns:
        Transformed expression
    """
    # Check if this expression matches the target
    if _expression_key(expr) == _expression_key(target):
        return replacement

    # Recursively replace in subexpressions
    if isinstance(expr, Binary):
        new_left = _replace_subexpression(expr.left, target, replacement)
        new_right = _replace_subexpression(expr.right, target, replacement)
        if new_left != expr.left or new_right != expr.right:
            return Binary(expr.op, new_left, new_right)
    elif isinstance(expr, Call):
        new_args = tuple(_replace_subexpression(arg, target, replacement) for arg in expr.args)
        if any(new_arg != old_arg for new_arg, old_arg in zip(new_args, expr.args, strict=True)):
            return Call(expr.func, new_args)

    return expr

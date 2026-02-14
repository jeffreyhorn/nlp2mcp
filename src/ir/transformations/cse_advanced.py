"""Advanced Common Subexpression Elimination (CSE) transformations.

This module implements T5.2 (Nested CSE), T5.3 (Multiplicative CSE), and
T5.4 (CSE with Aliasing) for aggressive simplification mode.

Patterns:
- T5.2: Nested CSE - Replace repeated complex subexpressions
- T5.3: Multiplicative CSE - Replace repeated multiplication patterns
- T5.4: CSE with Aliasing - Avoid creating CSE for already-aliased expressions

Example:
    # T5.2: Nested CSE
    (x*y + z)^2 + 3*(x*y + z) + sin(x*y + z) → t1 = x*y + z; t1^2 + 3*t1 + sin(t1)

    # T5.3: Multiplicative CSE
    x*y*a + x*y*b + x*y*c → m1 = x*y; m1*a + m1*b + m1*c

    # T5.4: CSE with Aliasing
    Given: t1 = x+y, later: z = x+y → Recognize z as alias, reuse t1

Priority: LOW (optional CSE features, high reuse threshold required)

Note: CSE transformations create temporary variables, which changes the
expression structure significantly. They should only be applied when:
1. The subexpression appears many times (≥3 for nested, ≥4 for multiplicative)
2. Cost savings justify the overhead
3. All algebraic simplifications have been exhausted
"""

from collections import defaultdict

from src.ir.ast import Binary, Call, Const, Expr, Prod, Sum, SymbolRef, Unary, VarRef


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
    elif isinstance(expr, Unary):
        _collect_subexpressions(expr.child, counts)
    elif isinstance(expr, (Sum, Prod)):
        if expr.condition is not None:
            _collect_subexpressions(expr.condition, counts)
        _collect_subexpressions(expr.body, counts)


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
    elif isinstance(expr, Unary):
        _collect_multiplicative_subexpressions(expr.child, counts)
    elif isinstance(expr, (Sum, Prod)):
        if expr.condition is not None:
            _collect_multiplicative_subexpressions(expr.condition, counts)
        _collect_multiplicative_subexpressions(expr.body, counts)


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
        return f"VarRef({expr.name},{repr(expr.indices)})"
    elif isinstance(expr, Binary):
        left_key = _expression_key(expr.left)
        right_key = _expression_key(expr.right)
        return f"Binary({expr.op},{left_key},{right_key})"
    elif isinstance(expr, Call):
        args_keys = ",".join(_expression_key(arg) for arg in expr.args)
        return f"Call({expr.func},{args_keys})"
    elif isinstance(expr, Unary):
        child_key = _expression_key(expr.child)
        return f"Unary({expr.op},{child_key})"
    elif isinstance(expr, Sum):
        body_key = _expression_key(expr.body)
        cond_key = _expression_key(expr.condition) if expr.condition is not None else "None"
        return f"Sum({expr.index_sets},{body_key},{cond_key})"
    elif isinstance(expr, Prod):
        body_key = _expression_key(expr.body)
        cond_key = _expression_key(expr.condition) if expr.condition is not None else "None"
        return f"Prod({expr.index_sets},{body_key},{cond_key})"
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
    elif isinstance(container, Unary):
        return _contains_subexpression(container.child, target)
    elif isinstance(container, (Sum, Prod)):
        if container.condition is not None and _contains_subexpression(container.condition, target):
            return True
        return _contains_subexpression(container.body, target)

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
    elif isinstance(expr, Unary):
        new_child = _replace_subexpression(expr.child, target, replacement)
        if new_child != expr.child:
            return Unary(expr.op, new_child)
    elif isinstance(expr, (Sum, Prod)):
        new_body = _replace_subexpression(expr.body, target, replacement)
        new_cond = (
            _replace_subexpression(expr.condition, target, replacement)
            if expr.condition is not None
            else None
        )
        if new_body != expr.body or new_cond != expr.condition:
            return type(expr)(expr.index_sets, new_body, new_cond)

    return expr


def cse_with_aliasing(
    expr: Expr,
    symbol_table: dict[str, Expr] | None = None,
    min_occurrences: int = 3,
) -> tuple[Expr, dict[str, Expr]]:
    """Apply CSE with aliasing awareness - avoid creating CSE for already-aliased expressions.

    This transformation extends nested CSE by tracking variable substitutions in a symbol
    table. If an expression is already assigned to a variable (either from a previous CSE
    pass or from user-defined variables), this function recognizes the alias and reuses
    the existing variable instead of creating a new temporary.

    Algorithm:
    1. Start with existing symbol table (mapping variable names to their expressions)
    2. Collect subexpressions and check if any match existing variables
    3. For matched expressions, use existing variable instead of creating new temp
    4. For unmatched expressions, apply standard nested CSE
    5. Update symbol table with new temporary variables

    Args:
        expr: Expression to transform
        symbol_table: Optional dict mapping variable names to their expressions.
                     If None, starts with empty symbol table.
        min_occurrences: Minimum occurrences required for CSE (default: 3)

    Returns:
        Tuple of (transformed expression, dict mapping temp names to definitions)

    Example:
        >>> # Given existing: t1 = x+y
        >>> # Expression: (x+y)^2 + 3*(x+y) + (a+b) + (a+b) + (a+b)
        >>> x, y, a, b = SymbolRef("x"), SymbolRef("y"), SymbolRef("a"), SymbolRef("b")
        >>> xy = Binary("+", x, y)
        >>> ab = Binary("+", a, b)
        >>> symbol_table = {"t1": xy}  # t1 already assigned to x+y
        >>> expr = Binary("+", Binary("**", xy, Const(2)),
        ...               Binary("+", Binary("+", ab, ab), ab))
        >>> result, temps = cse_with_aliasing(expr, symbol_table, min_occurrences=3)
        >>> # result uses t1 for x+y (existing), creates new temp for a+b
        >>> # temps only contains new temporaries (not t1)
    """
    if symbol_table is None:
        symbol_table = {}

    # Step 1: Collect subexpressions with counts
    subexpr_counts: dict[str, tuple[Expr, int]] = {}
    _collect_subexpressions(expr, subexpr_counts)

    # Step 2: Build reverse mapping: expression key -> existing variable name
    # If multiple variables map to same expression, pick lexicographically smallest for determinism
    expr_to_var: dict[str, str] = {}
    for var_name, var_expr in symbol_table.items():
        expr_key = _expression_key(var_expr)
        if expr_key not in expr_to_var or var_name < expr_to_var[expr_key]:
            expr_to_var[expr_key] = var_name

    # Step 3: Filter candidates and separate into aliased vs new
    aliased_candidates: dict[str, str] = {}  # expr_key -> existing var name
    new_candidates: dict[str, tuple[Expr, int]] = {}  # expr_key -> (expr, count)

    for key, (subexpr, count) in subexpr_counts.items():
        if count >= min_occurrences and _is_cse_candidate(subexpr):
            if key in expr_to_var:
                # This expression is already assigned to a variable
                aliased_candidates[key] = expr_to_var[key]
            else:
                # This is a new candidate for CSE
                new_candidates[key] = (subexpr, count)

    # Step 4: Replace aliased expressions with existing variables first
    result_expr = expr
    for expr_key, var_name in aliased_candidates.items():
        # Find the original expression from subexpr_counts
        subexpr = subexpr_counts[expr_key][0]
        var_ref = SymbolRef(var_name)
        result_expr = _replace_subexpression(result_expr, subexpr, var_ref)

    # Step 5: Apply standard nested CSE to remaining candidates
    if not new_candidates:
        return result_expr, {}

    # Sort new candidates by dependency (innermost first)
    sorted_new_candidates = _topological_sort_candidates(new_candidates)

    # Step 6: Generate temporary variables and replace
    temps: dict[str, Expr] = {}

    for i, (_key, (subexpr, _count)) in enumerate(sorted_new_candidates):
        temp_name = f"a{i + 1}"  # Use 'a' prefix for aliasing-aware temps
        temp_ref = SymbolRef(temp_name)

        # Store the definition
        temps[temp_name] = subexpr

        # Also replace aliased expressions in the temp definition
        for expr_key, var_name in aliased_candidates.items():
            aliased_subexpr = subexpr_counts[expr_key][0]
            var_ref = SymbolRef(var_name)
            temps[temp_name] = _replace_subexpression(temps[temp_name], aliased_subexpr, var_ref)

        # Replace all occurrences in result expression
        result_expr = _replace_subexpression(result_expr, subexpr, temp_ref)

        # Also update temp definitions to use previously extracted temps
        existing_temp_names = list(temps.keys())[:-1]
        for existing_temp_name in existing_temp_names:
            temps[existing_temp_name] = _replace_subexpression(
                temps[existing_temp_name], subexpr, temp_ref
            )

    return result_expr, temps

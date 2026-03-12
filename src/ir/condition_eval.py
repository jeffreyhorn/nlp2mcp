"""
Condition evaluation for GAMS conditional equations ($ operator).

Evaluates condition expressions with concrete index values to determine
which equation instances should be generated.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .ast import Binary, Call, Const, Expr, ParamRef, SymbolRef, Unary, VarRef

if TYPE_CHECKING:
    from .model_ir import ModelIR


class ConditionEvaluationError(Exception):
    """Raised when a condition cannot be evaluated."""

    pass


def evaluate_condition(
    condition: Expr,
    domain_sets: tuple[str, ...],
    index_values: tuple[str, ...],
    model_ir: ModelIR,
) -> bool:
    """
    Evaluate a condition expression with concrete index values.

    Args:
        condition: Condition expression AST (from $ operator)
        domain_sets: Domain set names (e.g., ("i", "j"))
        index_values: Concrete index values (e.g., ("i1", "j2"))
        model_ir: Model IR for parameter and set lookups

    Returns:
        True if condition is satisfied, False otherwise

    Examples:
        >>> # Condition: $(ord(i) > 2)
        >>> # For index value "i3": ord("i3") = 3, so 3 > 2 = True
        >>> evaluate_condition(condition, ("i",), ("i3",), model_ir)
        True

        >>> # Condition: $(demand(i) > 0)
        >>> # For index value "i1": demand("i1") = 10, so 10 > 0 = True
        >>> evaluate_condition(condition, ("i",), ("i1",), model_ir)
        True

        >>> # Condition: $(i <> j)
        >>> # For index values ("i1", "i2"): "i1" <> "i2" = True
        >>> evaluate_condition(condition, ("i", "j"), ("i1", "i2"), model_ir)
        True
    """
    # Create index substitution map
    index_map = dict(zip(domain_sets, index_values, strict=True))

    # Evaluate the expression
    try:
        result = _eval_expr(condition, index_map, model_ir)
        # Convert to boolean
        return bool(result) and result != 0
    except Exception as e:
        raise ConditionEvaluationError(
            f"Failed to evaluate condition {condition} with indices {index_values}: {e}"
        ) from e


def _eval_expr(expr: Expr, index_map: dict[str, str], model_ir: ModelIR) -> float | str:
    """
    Recursively evaluate an expression with index substitution.

    Returns:
        Numeric value or string (for set element comparisons)
    """
    if isinstance(expr, Const):
        return expr.value

    if isinstance(expr, SymbolRef):
        # Could be an index reference (e.g., "i" in condition)
        if expr.name in index_map:
            return index_map[expr.name]
        # Issue #877: Acronyms are symbolic constants — return the name
        # as a string so comparisons like pdata(i,t,j,"type") = call work
        if expr.name.lower() in model_ir.acronyms:
            return expr.name.lower()
        # Could be a scalar parameter
        if expr.name in model_ir.params:
            param = model_ir.params[expr.name]
            if not param.domain:  # scalar parameter
                return param.values.get((), 0.0)
        raise ConditionEvaluationError(f"Unknown symbol '{expr.name}' in condition")

    if isinstance(expr, (VarRef, ParamRef)):
        # Issue #877: Acronym references (no indices) return the name as string
        if (
            isinstance(expr, ParamRef)
            and not expr.indices
            and expr.name.lower() in model_ir.acronyms
        ):
            return expr.name.lower()
        # Parameter reference with indices (or variable reference in condition)
        param_name = expr.name
        if param_name not in model_ir.params:
            # For VarRef in conditions, it might be checking variable bounds, but that's uncommon
            # For now, just raise an error
            raise ConditionEvaluationError(f"Unknown parameter '{param_name}' in condition")

        param = model_ir.params[param_name]

        # Substitute indices - only string indices supported, IndexOffset raises error
        concrete_indices_list = []
        for idx in expr.indices:
            if isinstance(idx, str):
                concrete_indices_list.append(index_map.get(idx, idx))
            else:
                # IndexOffset not yet supported in condition evaluation
                raise ConditionEvaluationError(f"IndexOffset not supported in conditions: {idx}")
        concrete_indices: tuple[str, ...] = tuple(concrete_indices_list)

        # Look up parameter value
        if concrete_indices in param.values:
            return param.values[concrete_indices]
        # Issue #1057: If the parameter has expression-based values, try to
        # evaluate the expression recursively. E.g., tm(t) = td("target",t)
        # can be resolved if td has static values.
        if param.expressions:
            for expr_domain, expr_body in param.expressions:
                if len(expr_domain) != len(concrete_indices):
                    continue
                # Only handle simple string domains (skip IndexOffset)
                if not all(isinstance(d, str) for d in expr_domain):
                    continue
                # Build index map from expression domain to concrete values
                expr_index_map: dict[str, str] = dict(
                    zip(expr_domain, concrete_indices, strict=True)  # type: ignore[arg-type]
                )
                try:
                    return _eval_expr(expr_body, expr_index_map, model_ir)
                except ConditionEvaluationError:
                    pass  # Try next expression or fall through to error
            raise ConditionEvaluationError(
                f"Parameter '{param_name}' has expression-based values that "
                f"cannot be evaluated statically for indices {concrete_indices}"
            )
        # Default to 0 for parameters with no values and no expressions
        return 0.0

    if isinstance(expr, Binary):
        left = _eval_expr(expr.left, index_map, model_ir)
        right = _eval_expr(expr.right, index_map, model_ir)

        # Comparison operators (work with both float and str for set comparisons)
        if expr.op == ">":
            return 1.0 if left > right else 0.0  # type: ignore[operator]
        if expr.op == "<":
            return 1.0 if left < right else 0.0  # type: ignore[operator]
        if expr.op == ">=":
            return 1.0 if left >= right else 0.0  # type: ignore[operator]
        if expr.op == "<=":
            return 1.0 if left <= right else 0.0  # type: ignore[operator]
        if expr.op in ("==", "="):
            return 1.0 if left == right else 0.0
        if expr.op == "<>":
            return 1.0 if left != right else 0.0

        # Logical operators
        if expr.op.lower() == "and":
            return 1.0 if (left and right) else 0.0
        if expr.op.lower() == "or":
            return 1.0 if (left or right) else 0.0

        # Arithmetic operators - ensure numeric types.
        # Acronym string values are only valid in comparisons, not arithmetic.
        def _check_numeric(op: str, lhs: float | str, rhs: float | str) -> tuple[float, float]:
            if isinstance(lhs, str) or isinstance(rhs, str):
                acronym_side = lhs if isinstance(lhs, str) else rhs
                raise ConditionEvaluationError(
                    f"Acronym '{acronym_side}' cannot be used in arithmetic "
                    f"({op}); acronyms are only valid in comparisons"
                )
            return lhs, rhs

        if expr.op == "+":
            nl, nr = _check_numeric("+", left, right)
            return nl + nr
        if expr.op == "-":
            nl, nr = _check_numeric("-", left, right)
            return nl - nr
        if expr.op == "*":
            nl, nr = _check_numeric("*", left, right)
            return nl * nr
        if expr.op == "/":
            nl, nr = _check_numeric("/", left, right)
            return nl / nr if nr != 0 else 0.0

        raise ConditionEvaluationError(f"Unsupported binary operator '{expr.op}' in condition")

    if isinstance(expr, Unary):
        operand_val = _eval_expr(expr.child, index_map, model_ir)
        if expr.op.lower() == "not":
            return 1.0 if not operand_val else 0.0
        if expr.op == "-":
            if isinstance(operand_val, (int, float)):
                return -operand_val
            raise ConditionEvaluationError("Unary - requires numeric operand")
        raise ConditionEvaluationError(f"Unsupported unary operator '{expr.op}' in condition")

    if isinstance(expr, Call):
        func_name = expr.func.lower()

        # ord(i) - returns ordinal position of set element (1-based)
        if func_name == "ord":
            if len(expr.args) != 1:
                raise ConditionEvaluationError(f"ord() expects 1 argument, got {len(expr.args)}")

            # Get the index reference
            arg = expr.args[0]
            if isinstance(arg, SymbolRef) and arg.name in index_map:
                element = index_map[arg.name]
                set_name = arg.name
                # Get set members to determine ordinal
                if set_name in model_ir.sets:
                    members = model_ir.sets[set_name].members
                    if element in members:
                        return float(members.index(element) + 1)  # 1-based
                # Check aliases
                if set_name in model_ir.aliases:
                    target = model_ir.aliases[set_name].target
                    if target in model_ir.sets:
                        members = model_ir.sets[target].members
                        if element in members:
                            return float(members.index(element) + 1)  # 1-based
                raise ConditionEvaluationError(f"Could not find ordinal for element '{element}'")
            raise ConditionEvaluationError("ord() argument must be an index reference")

        # card(set) - returns cardinality of set
        if func_name == "card":
            if len(expr.args) != 1:
                raise ConditionEvaluationError(f"card() expects 1 argument, got {len(expr.args)}")
            arg = expr.args[0]
            if isinstance(arg, SymbolRef):
                set_name = arg.name
                if set_name in model_ir.sets:
                    return float(len(model_ir.sets[set_name].members))
                if set_name in model_ir.aliases:
                    target = model_ir.aliases[set_name].target
                    if target in model_ir.sets:
                        return float(len(model_ir.sets[target].members))
            raise ConditionEvaluationError("card() argument must be a set reference")

        raise ConditionEvaluationError(f"Unsupported function '{func_name}' in condition")

    raise ConditionEvaluationError(
        f"Unsupported expression type {type(expr).__name__} in condition"
    )

"""
Symbolic Automatic Differentiation Core

This module implements symbolic differentiation (AST → AST transformations)
for computing derivatives of GAMS NLP expressions.

Design Philosophy:
-----------------
We use symbolic differentiation rather than adjoint-style reverse-mode AD because:

1. **Transparency**: Derivative expressions remain as AST nodes that can be
   inspected, simplified, and manipulated before evaluation.

2. **Flexibility**: We can generate GAMS code directly from derivative ASTs
   without needing to evaluate them numerically first.

3. **Simplicity**: For our use case (generating KKT conditions), we need
   symbolic Jacobian entries, not just numerical values.

4. **Debugging**: Symbolic derivatives can be pretty-printed and verified
   against mathematical expectations before any numerical evaluation.

The trade-off is that symbolic differentiation can produce larger expression
trees than strictly necessary, but this is acceptable for our problem sizes
and allows for better debugging and code generation.

Approach:
--------
- differentiate(expr, wrt_var) → new AST representing d(expr)/d(wrt_var)
- Each AST node type has a differentiation rule
- Chain rule applied recursively through expression tree
- Result is always a new AST (never modifies input)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .term_collection import (
    collect_like_terms,
    simplify_multiplicative_cancellation,
    simplify_power_rules,
)

if TYPE_CHECKING:
    from ..config import Config
    from ..ir.ast import Expr


def differentiate(expr: Expr, wrt_var: str) -> Expr:
    """
    Compute the symbolic derivative of an expression with respect to a variable.

    Args:
        expr: The expression to differentiate (AST node)
        wrt_var: The variable name to differentiate with respect to
                 (e.g., "x" for scalar, or base name for indexed vars)

    Returns:
        A new AST representing the derivative d(expr)/d(wrt_var)

    Examples:
        >>> from src.ir.ast import Const, VarRef
        >>> differentiate(Const(5.0), "x")  # d(5)/dx = 0
        Const(0.0)
        >>> differentiate(VarRef("x"), "x")  # dx/dx = 1
        Const(1.0)
        >>> differentiate(VarRef("y"), "x")  # dy/dx = 0
        Const(0.0)

    Note:
        This is the main entry point for symbolic differentiation.
        Expressions are first flattened (nested min/max operations)
        before differentiation for optimal performance.
        Specific derivative rules are delegated to derivative_rules module.
    """
    from . import derivative_rules
    from .minmax_flattener import flatten_all_minmax

    # Flatten nested min/max operations before differentiation
    # This reduces auxiliary variables and improves efficiency
    flattened_expr = flatten_all_minmax(expr)

    return derivative_rules.differentiate_expr(flattened_expr, wrt_var)


def simplify(expr: Expr) -> Expr:
    """
    Simplify a symbolic expression using algebraic simplification rules.

    This function recursively simplifies expressions by applying these rules:

    **Priority 1 (Basic Algebraic Simplifications):**
        - Constant folding: Const(2) + Const(3) → Const(5)
        - Zero elimination: x + 0 → x, 0 + x → x, x * 0 → 0, 0 * x → 0
        - Identity elimination: x * 1 → x, 1 * x → x
        - Zero subtraction: x - 0 → x
        - Division by one: x / 1 → x
        - Double negation: -(-x) → x
        - Power simplification: x ** 0 → 1, x ** 1 → x

    **Priority 2 (Structural Simplifications):**
        - Additive inverse: x + (-y) → x - y
        - Nested simplification: Recursively simplifies subexpressions

    Args:
        expr: The expression to simplify (AST node)

    Returns:
        A simplified version of the expression (new AST node)

    Examples:
        >>> from src.ir.ast import Const, VarRef, Binary, Unary
        >>> simplify(Binary("+", VarRef("x", ()), Const(0)))
        VarRef("x", ())
        >>> simplify(Binary("*", Const(2), Const(3)))
        Const(6)
        >>> simplify(Binary("*", VarRef("x", ()), Const(0)))
        Const(0)
        >>> simplify(Unary("-", Unary("-", VarRef("x", ()))))
        VarRef("x", ())

    Note:
        Simplification is applied recursively bottom-up through the expression tree.
        The function is safe to call multiple times (idempotent for fully simplified expressions).
    """
    from ..ir.ast import Binary, Call, Const, MultiplierRef, ParamRef, Sum, SymbolRef, Unary, VarRef

    match expr:
        # Base cases: already simple
        case Const(_) | VarRef(_, _) | ParamRef(_, _) | MultiplierRef(_, _) | SymbolRef(_):
            return expr

        # Unary operations
        case Unary(op, child):
            simplified_child = simplify(child)

            # Double negation: -(-x) → x
            if op == "-" and isinstance(simplified_child, Unary) and simplified_child.op == "-":
                return simplified_child.child

            # Unary plus: +x → x
            if op == "+":
                return simplified_child

            # Constant unary: -(5) → -5
            if isinstance(simplified_child, Const):
                if op == "-":
                    return Const(-simplified_child.value)
                if op == "+":
                    return simplified_child

            return Unary(op, simplified_child)

        # Binary operations
        case Binary(op, left, right):
            # First, recursively simplify children
            simplified_left = simplify(left)
            simplified_right = simplify(right)

            # Constant folding: operate on two constants
            if isinstance(simplified_left, Const) and isinstance(simplified_right, Const):
                left_val = simplified_left.value
                right_val = simplified_right.value
                match op:
                    case "+":
                        return Const(left_val + right_val)
                    case "-":
                        return Const(left_val - right_val)
                    case "*":
                        return Const(left_val * right_val)
                    case "/":
                        # Avoid division by zero
                        if right_val != 0:
                            return Const(left_val / right_val)
                        else:
                            # Division by zero: return unsimplified expression
                            return Binary(op, simplified_left, simplified_right)
                    case "^":
                        # Special case: 0 ** 0 is mathematically indeterminate
                        # Don't simplify even though Python evaluates to 1
                        if left_val == 0 and right_val == 0:
                            return Binary("^", simplified_left, simplified_right)
                        # Handle edge cases: negative base with fractional exponent, 0**negative, overflow
                        try:
                            return Const(left_val**right_val)
                        except (ValueError, ZeroDivisionError, OverflowError):
                            # Fall back to unsimplified expression if invalid operation
                            return Binary("^", simplified_left, simplified_right)

            # Addition simplifications
            if op == "+":
                # x + 0 → x
                if isinstance(simplified_right, Const) and simplified_right.value == 0:
                    return simplified_left
                # 0 + x → x
                if isinstance(simplified_left, Const) and simplified_left.value == 0:
                    return simplified_right
                # x + (-y) → x - y
                if isinstance(simplified_right, Unary) and simplified_right.op == "-":
                    return Binary("-", simplified_left, simplified_right.child)

            # Subtraction simplifications
            if op == "-":
                # x - 0 → x
                if isinstance(simplified_right, Const) and simplified_right.value == 0:
                    return simplified_left
                # 0 - x → -x
                # Recursive call needed to handle double negation: 0 - (-x) → -(-x) → x
                if isinstance(simplified_left, Const) and simplified_left.value == 0:
                    return simplify(Unary("-", simplified_right))
                # x - x → 0 (only if same variable reference with same indices)
                if simplified_left == simplified_right:
                    return Const(0)

            # Multiplication simplifications
            if op == "*":
                # x * 0 → 0
                if isinstance(simplified_right, Const) and simplified_right.value == 0:
                    return Const(0)
                # 0 * x → 0
                if isinstance(simplified_left, Const) and simplified_left.value == 0:
                    return Const(0)
                # x * 1 → x
                if isinstance(simplified_right, Const) and simplified_right.value == 1:
                    return simplified_left
                # 1 * x → x
                if isinstance(simplified_left, Const) and simplified_left.value == 1:
                    return simplified_right

            # Division simplifications
            if op == "/":
                # x / 1 → x
                if isinstance(simplified_right, Const) and simplified_right.value == 1:
                    return simplified_left
                # 0 / x → 0 (note: if x == 0 at runtime, both 0/0 and 0 are invalid/indeterminate)
                if isinstance(simplified_left, Const) and simplified_left.value == 0:
                    return Const(0)
                # x / x → 1 (only if same variable reference)
                if simplified_left == simplified_right:
                    return Const(1)

            # Power simplifications
            if op == "^":
                # x ** 0 → 1 (but NOT for 0 ** 0, which is indeterminate)
                if (
                    isinstance(simplified_right, Const)
                    and simplified_right.value == 0
                    and not (isinstance(simplified_left, Const) and simplified_left.value == 0)
                ):
                    return Const(1)
                # x ** 1 → x
                if isinstance(simplified_right, Const) and simplified_right.value == 1:
                    return simplified_left
                # 0 ** x → 0 (only if x is constant and x > 0)
                # Invalid for x ≤ 0: 0**(-1) = 1/0, 0**0 is indeterminate
                if (
                    isinstance(simplified_left, Const)
                    and simplified_left.value == 0
                    and isinstance(simplified_right, Const)
                    and simplified_right.value > 0
                ):
                    return Const(0)
                # 1 ** x → 1
                if isinstance(simplified_left, Const) and simplified_left.value == 1:
                    return Const(1)

            return Binary(op, simplified_left, simplified_right)

        # Function calls: recursively simplify arguments
        case Call(func, args):
            simplified_args = tuple(simplify(arg) for arg in args)
            return Call(func, simplified_args)

        # Sum: recursively simplify body
        case Sum(index_sets, body):
            simplified_body = simplify(body)
            return Sum(index_sets, simplified_body)

        case _:
            # Unknown expression type - return as-is
            return expr


def simplify_advanced(expr: Expr) -> Expr:
    """
    Apply advanced simplification including term collection.

    This function extends basic simplification with:
    - Constant collection: 1 + x + 1 → x + 2
    - Like-term collection: x + y + x + y → 2*x + 2*y

    The function applies simplification in two passes:
    1. Basic simplification (existing rules)
    2. Advanced term collection (for additions)

    Args:
        expr: The expression to simplify

    Returns:
        A simplified version of the expression

    Examples:
        >>> from src.ir.ast import Const, VarRef, Binary
        >>> expr = Binary("+", Binary("+", Const(1), VarRef("x", ())), Const(1))
        >>> result = simplify_advanced(expr)
        >>> # Result: Binary("+", VarRef("x", ()), Const(2)) or Const(2) + VarRef("x")
    """
    from ..ir.ast import Binary, Call, Sum, Unary

    # Step 1: Apply basic simplification rules
    basic_simplified = simplify(expr)

    # Step 2: Apply term collection (only for additions)
    # Recursively process children first, then apply to this node
    match basic_simplified:
        case Binary("+", left, right):
            # Recursively simplify children with advanced rules
            simplified_left = simplify_advanced(left)
            simplified_right = simplify_advanced(right)
            reconstructed = Binary("+", simplified_left, simplified_right)

            # Apply term collection to this level
            collected = collect_like_terms(reconstructed)

            # If collection made progress, simplify again (may enable more basic rules)
            if collected != reconstructed:
                return simplify(collected)
            return collected

        case Binary("/", left, right):
            # Division: recursively simplify, then try multiplicative cancellation and power rules
            simplified_left = simplify_advanced(left)
            simplified_right = simplify_advanced(right)
            reconstructed = Binary("/", simplified_left, simplified_right)

            # Apply multiplicative cancellation: (c * x) / c → x
            cancelled = simplify_multiplicative_cancellation(reconstructed)

            # Apply power rules: x^a / x^b → x^(a-b)
            power_simplified = simplify_power_rules(cancelled)

            # If any transformation made progress, simplify again
            if power_simplified != reconstructed:
                return simplify(power_simplified)
            return power_simplified

        case Binary("*", left, right):
            # Multiplication: recursively simplify, then try power rules
            simplified_left = simplify_advanced(left)
            simplified_right = simplify_advanced(right)
            reconstructed = Binary("*", simplified_left, simplified_right)

            # Apply power rules: x^a * x^b → x^(a+b), x * x → x^2
            power_simplified = simplify_power_rules(reconstructed)

            # If power rules made progress, simplify again
            if power_simplified != reconstructed:
                return simplify(power_simplified)
            return power_simplified

        case Binary("**", left, right):
            # Power: recursively simplify, then try nested power rules
            simplified_left = simplify_advanced(left)
            simplified_right = simplify_advanced(right)
            reconstructed = Binary("**", simplified_left, simplified_right)

            # Apply power rules: (x^a)^b → x^(a*b)
            power_simplified = simplify_power_rules(reconstructed)

            # If power rules made progress, simplify again
            if power_simplified != reconstructed:
                return simplify(power_simplified)
            return power_simplified

        case Binary(op, left, right):
            # Recursively process children for other binary operations
            simplified_left = simplify_advanced(left)
            simplified_right = simplify_advanced(right)
            if simplified_left != left or simplified_right != right:
                # Children changed, rebuild and simplify
                return simplify(Binary(op, simplified_left, simplified_right))
            return basic_simplified

        case Unary(op, child):
            # Recursively process child
            simplified_child = simplify_advanced(child)
            if simplified_child != child:
                return simplify(Unary(op, simplified_child))
            return basic_simplified

        case Call(func, args):
            # Recursively process arguments
            simplified_args = tuple(simplify_advanced(arg) for arg in args)
            if simplified_args != args:
                return Call(func, simplified_args)
            return basic_simplified

        case Sum(index_sets, body):
            # Recursively process body
            simplified_body = simplify_advanced(body)
            if simplified_body != body:
                return Sum(index_sets, simplified_body)
            return basic_simplified

        case _:
            # Leaf nodes or unknown types - already simplified
            return basic_simplified


def get_simplification_mode(config: Config | None) -> str:
    """
    Get the simplification mode from config, with a sensible default.

    Args:
        config: Configuration object (may be None)

    Returns:
        Simplification mode string: "none", "basic", or "advanced"
    """
    if config:
        return config.simplification
    else:
        # Default to advanced simplification if no config provided
        return "advanced"


def apply_simplification(expr: Expr, mode: str) -> Expr:
    """
    Apply simplification based on the specified mode.

    Args:
        expr: Expression to simplify
        mode: Simplification mode - "none", "basic", or "advanced"

    Returns:
        Simplified expression (or original if mode is "none")

    Raises:
        ValueError: If mode is not one of "none", "basic", "advanced"
    """
    if mode == "none":
        return expr
    elif mode == "basic":
        return simplify(expr)
    elif mode == "advanced":
        return simplify_advanced(expr)
    else:
        raise ValueError(
            f"Invalid simplification mode: {mode}. Must be 'none', 'basic', or 'advanced'"
        )

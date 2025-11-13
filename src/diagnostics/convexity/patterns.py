"""
Concrete implementations of convexity pattern matchers.

This module implements 5 core patterns from Sprint 6 Prep Task 2 POC:
1. Nonlinear Equality Detection
2. Trigonometric Function Detection
3. Bilinear Term Detection
4. Division/Quotient Detection
5. Odd-Power Polynomial Detection

Each pattern matcher is a conservative heuristic designed to detect
common non-convex structures while avoiding false positives.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.ir.ast import Binary, Call, Const, Expr, VarRef
from src.ir.symbols import Rel

from .pattern_matcher import (
    ConvexityWarning,
    PatternMatcher,
    find_matching_nodes,
    has_variable,
    is_affine,
)

if TYPE_CHECKING:
    from src.ir.model_ir import ModelIR


class NonlinearEqualityPattern(PatternMatcher):
    """
    Detect nonlinear equality constraints.

    Mathematical Basis:
    ------------------
    Nonlinear equality constraints h(x) = 0 typically define non-convex
    feasible sets, even if h itself might be convex.

    Example: x² + y² = 4 defines a circle (non-convex set), whereas
    x² + y² ≤ 4 defines a disk (convex set).

    Implementation:
    --------------
    - Check all equations with Rel.EQ (equality relation)
    - Skip objective definition equations (e.g., obj =e= f(x))
    - Use is_affine() to verify linearity
    - Report non-affine equalities as warnings

    Validated: POC Task 2, 100% accuracy on test fixtures
    """

    @property
    def pattern_name(self) -> str:
        return "nonlinear_equality"

    def detect(self, model_ir: ModelIR) -> list[ConvexityWarning]:
        warnings = []

        # Get objective variable name to skip its definition equation
        obj_var = model_ir.objective.objvar if model_ir.objective else None

        for eq_name, eq in model_ir.equations.items():
            if eq.relation == Rel.EQ:
                lhs, rhs = eq.lhs_rhs

                # Skip objective definition equations (e.g., obj =e= 2*x + 3*y)
                # These are identified by checking if LHS is just the objective variable
                if obj_var and isinstance(lhs, VarRef):
                    # Check if LHS matches objective variable name
                    if lhs.name == obj_var:
                        continue

                # Compute difference: lhs - rhs
                # An equality lhs = rhs is equivalent to lhs - rhs = 0
                difference = Binary("-", lhs, rhs)

                # Check if the equality constraint is affine
                if not is_affine(difference):
                    warnings.append(
                        ConvexityWarning(
                            equation=eq_name,
                            pattern=self.pattern_name,
                            message="Nonlinear equality constraint detected (may be non-convex)",
                            details=None,
                            error_code="W301",
                        )
                    )

        return warnings


class TrigonometricPattern(PatternMatcher):
    """
    Detect trigonometric functions in objectives and constraints.

    Mathematical Basis:
    ------------------
    Trigonometric functions (sin, cos, tan, etc.) are neither globally
    convex nor concave, making them strong indicators of non-convexity.

    Implementation:
    --------------
    - Recursively traverse AST for Call nodes
    - Detect: sin, cos, tan, arcsin, arccos, arctan
    - Check both objectives and all constraint expressions

    Validated: POC Task 2, 100% accuracy on test fixtures
    """

    TRIG_FUNCTIONS = {"sin", "cos", "tan", "arcsin", "arccos", "arctan"}

    @property
    def pattern_name(self) -> str:
        return "trigonometric_function"

    def detect(self, model_ir: ModelIR) -> list[ConvexityWarning]:
        warnings = []

        # Check objective function
        if model_ir.objective and model_ir.objective.expr:
            trig_calls = self._find_trig_functions(model_ir.objective.expr)
            if trig_calls:
                warnings.append(
                    ConvexityWarning(
                        equation="objective",
                        pattern=self.pattern_name,
                        message="Trigonometric function in objective",
                        details=", ".join(trig_calls),
                        error_code="W302",
                    )
                )

        # Check all constraints
        for eq_name, eq in model_ir.equations.items():
            lhs, rhs = eq.lhs_rhs
            # Check both sides of the equation
            difference = Binary("-", lhs, rhs)
            trig_calls = self._find_trig_functions(difference)
            if trig_calls:
                warnings.append(
                    ConvexityWarning(
                        equation=eq_name,
                        pattern=self.pattern_name,
                        message="Trigonometric function in constraint",
                        details=", ".join(trig_calls),
                        error_code="W302",
                    )
                )

        return warnings

    def _find_trig_functions(self, expr: Expr) -> list[str]:
        """Find all trigonometric function calls in expression."""
        trig_calls = []

        def is_trig_call(e: Expr) -> bool:
            return isinstance(e, Call) and e.func in self.TRIG_FUNCTIONS

        matches = find_matching_nodes(expr, is_trig_call)
        for match in matches:
            if isinstance(match, Call):
                trig_calls.append(f"{match.func}(...)")

        return trig_calls


class BilinearTermPattern(PatternMatcher):
    """
    Detect bilinear terms (products of two variables).

    Mathematical Basis:
    ------------------
    Bilinear terms x*y where both x and y are decision variables are
    typically non-convex (they form saddle-shaped surfaces).

    Implementation:
    --------------
    - Find Binary("*", left, right) nodes
    - Use has_variable() to check if both operands contain variables
    - Report all variable × variable products

    Note: Constant × variable is allowed (linear), we only flag
    variable × variable.

    Validated: POC Task 2, 100% accuracy on test fixtures
    """

    @property
    def pattern_name(self) -> str:
        return "bilinear_term"

    def detect(self, model_ir: ModelIR) -> list[ConvexityWarning]:
        warnings = []

        # Check objective
        if model_ir.objective and model_ir.objective.expr:
            bilinear_terms = self._find_bilinear_terms(model_ir.objective.expr)
            if bilinear_terms:
                warnings.append(
                    ConvexityWarning(
                        equation="objective",
                        pattern=self.pattern_name,
                        message="Bilinear term in objective (variable * variable)",
                        details=f"{len(bilinear_terms)} term(s) found",
                        error_code="W303",
                    )
                )

        # Check all constraints
        for eq_name, eq in model_ir.equations.items():
            lhs, rhs = eq.lhs_rhs
            difference = Binary("-", lhs, rhs)
            bilinear_terms = self._find_bilinear_terms(difference)
            if bilinear_terms:
                warnings.append(
                    ConvexityWarning(
                        equation=eq_name,
                        pattern=self.pattern_name,
                        message="Bilinear term in constraint (variable * variable)",
                        details=f"{len(bilinear_terms)} term(s) found",
                        error_code="W303",
                    )
                )

        return warnings

    def _find_bilinear_terms(self, expr: Expr) -> list[Expr]:
        """Find bilinear terms (products of two variables)."""

        def is_bilinear_multiplication(e: Expr) -> bool:
            if isinstance(e, Binary) and e.op == "*":
                return has_variable(e.left) and has_variable(e.right)
            return False

        return find_matching_nodes(expr, is_bilinear_multiplication)


class QuotientPattern(PatternMatcher):
    """
    Detect quotients where the denominator contains variables.

    Mathematical Basis:
    ------------------
    Rational functions x/y with variable denominators are typically
    non-convex and may cause numerical issues (division by zero).

    Implementation:
    --------------
    - Find Binary("/", left, right) nodes
    - Check if denominator (right) contains variables
    - Report all variable/variable divisions

    Note: Constant/variable and variable/constant may be convex in
    some cases, but variable/variable is almost always non-convex.

    Validated: POC Task 2, 100% accuracy on test fixtures
    """

    @property
    def pattern_name(self) -> str:
        return "variable_quotient"

    def detect(self, model_ir: ModelIR) -> list[ConvexityWarning]:
        warnings = []

        # Check objective
        if model_ir.objective and model_ir.objective.expr:
            quotients = self._find_variable_quotients(model_ir.objective.expr)
            if quotients:
                warnings.append(
                    ConvexityWarning(
                        equation="objective",
                        pattern=self.pattern_name,
                        message="Division by variable in objective",
                        details=f"{len(quotients)} quotient(s) found",
                        error_code="W304",
                    )
                )

        # Check all constraints
        for eq_name, eq in model_ir.equations.items():
            lhs, rhs = eq.lhs_rhs
            difference = Binary("-", lhs, rhs)
            quotients = self._find_variable_quotients(difference)
            if quotients:
                warnings.append(
                    ConvexityWarning(
                        equation=eq_name,
                        pattern=self.pattern_name,
                        message="Division by variable in constraint",
                        details=f"{len(quotients)} quotient(s) found",
                        error_code="W304",
                    )
                )

        return warnings

    def _find_variable_quotients(self, expr: Expr) -> list[Expr]:
        """Find quotients where denominator contains variables."""

        def is_variable_quotient(e: Expr) -> bool:
            if isinstance(e, Binary) and e.op == "/":
                return has_variable(e.right)
            return False

        return find_matching_nodes(expr, is_variable_quotient)


class OddPowerPattern(PatternMatcher):
    """
    Detect odd integer powers of variables (x³, x⁵, etc.).

    Mathematical Basis:
    ------------------
    Odd powers x³, x⁵, x⁷, ... are neither globally convex nor concave.
    Even powers like x², x⁴ can be convex, but odd powers indicate
    non-convexity.

    Implementation:
    --------------
    - Find power operations: Binary("**", base, exp) or Binary("^", base, exp)
    - Also check Call("power", (base, exp))
    - Verify exponent is odd integer (3, 5, 7, ...) excluding 1
    - Only report when base contains variables

    Note: x¹ = x is linear (allowed), x² may be convex (allowed),
    x³ is non-convex (flagged).

    Validated: POC Task 2, 100% accuracy on test fixtures
    """

    @property
    def pattern_name(self) -> str:
        return "odd_power"

    def detect(self, model_ir: ModelIR) -> list[ConvexityWarning]:
        warnings = []

        # Check objective
        if model_ir.objective and model_ir.objective.expr:
            odd_powers = self._find_odd_powers(model_ir.objective.expr)
            if odd_powers:
                warnings.append(
                    ConvexityWarning(
                        equation="objective",
                        pattern=self.pattern_name,
                        message="Odd power of variable in objective",
                        details=f"{len(odd_powers)} term(s) found",
                        error_code="W305",
                    )
                )

        # Check all constraints
        for eq_name, eq in model_ir.equations.items():
            lhs, rhs = eq.lhs_rhs
            difference = Binary("-", lhs, rhs)
            odd_powers = self._find_odd_powers(difference)
            if odd_powers:
                warnings.append(
                    ConvexityWarning(
                        equation=eq_name,
                        pattern=self.pattern_name,
                        message="Odd power of variable in constraint",
                        details=f"{len(odd_powers)} term(s) found",
                        error_code="W305",
                    )
                )

        return warnings

    def _find_odd_powers(self, expr: Expr) -> list[Expr]:
        """Find odd integer powers of variables (x^3, x^5, etc.)."""

        def is_odd_power(e: Expr) -> bool:
            # Check binary operators ** and ^
            if isinstance(e, Binary) and e.op in ("**", "^"):
                if isinstance(e.right, Const) and has_variable(e.left):
                    exp = e.right.value
                    # Check if exponent is odd integer, excluding 1 and -1
                    # Note: x^-1 (1/x) is already handled by QuotientPattern
                    if isinstance(exp, int) or (isinstance(exp, float) and exp.is_integer()):
                        int_exp = int(exp)
                        if int_exp % 2 == 1 and int_exp != 1 and int_exp != -1:
                            return True

            # Check power() function call
            if isinstance(e, Call) and e.func == "power" and len(e.args) == 2:
                base, exp_expr = e.args
                if isinstance(exp_expr, Const) and has_variable(base):
                    exp = exp_expr.value
                    if isinstance(exp, int) or (isinstance(exp, float) and exp.is_integer()):
                        int_exp = int(exp)
                        if int_exp % 2 == 1 and int_exp != 1 and int_exp != -1:
                            return True

            return False

        return find_matching_nodes(expr, is_odd_power)

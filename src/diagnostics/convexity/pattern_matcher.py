"""
Pattern matcher infrastructure for convexity detection.

This module provides the base classes and utilities for implementing
heuristic pattern matchers that detect common non-convex structures
in optimization models.

Design:
-------
- PatternMatcher: Abstract base class for all pattern detectors
- ConvexityWarning: Data structure for warnings
- AST traversal utilities for pattern matching

Implementation follows POC from scripts/poc_convexity_patterns.py
(validated Sprint 6 Prep Task 2).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.ir.ast import Binary, Call, Const, Expr, ParamRef, Sum, Unary, VarRef

if TYPE_CHECKING:
    from src.ir.model_ir import ModelIR


@dataclass
class ConvexityWarning:
    """
    A convexity warning detected in the model.

    Attributes:
        equation: Name of the equation where pattern was found
        pattern: Name of the pattern (e.g., "nonlinear_equality", "trig_function")
        message: Human-readable description of the issue
        details: Optional additional details (e.g., "sin(...)", "x*y")
        error_code: Error code for documentation linking (e.g., "W301")
    """

    equation: str
    pattern: str
    message: str
    details: str | None = None
    error_code: str | None = None

    def __str__(self) -> str:
        """Format warning for display."""
        prefix = f"[{self.error_code}] " if self.error_code else ""
        base = f"{prefix}[{self.pattern}] {self.equation}: {self.message}"
        if self.details:
            return f"{base} ({self.details})"
        return base


class PatternMatcher(ABC):
    """
    Abstract base class for convexity pattern matchers.

    Each pattern matcher implements the `detect()` method which analyzes
    a ModelIR and returns a list of ConvexityWarning objects.

    Pattern matchers are designed to be conservative: they may produce
    false negatives (miss non-convex patterns) but MUST NOT produce
    false positives (flag convex models as non-convex).
    """

    @property
    @abstractmethod
    def pattern_name(self) -> str:
        """Return the name of this pattern (e.g., 'nonlinear_equality')."""
        pass

    @abstractmethod
    def detect(self, model_ir: ModelIR) -> list[ConvexityWarning]:
        """
        Detect instances of this pattern in the model.

        Args:
            model_ir: The model to analyze

        Returns:
            List of warnings found (empty if no issues detected)
        """
        pass


# ===== AST Utility Functions =====


def is_constant(expr: Expr) -> bool:
    """
    Check if expression contains no variables (only constants/parameters).

    Args:
        expr: Expression to check

    Returns:
        True if expression is constant w.r.t. variables
    """
    match expr:
        case Const(_):
            return True
        case ParamRef(_):
            return True  # Parameters are constants w.r.t. variables
        case VarRef(_):
            return False
        case Binary(_, left, right):
            return is_constant(left) and is_constant(right)
        case Unary(_, operand):
            return is_constant(operand)
        case Call(_, args):
            return all(is_constant(arg) for arg in args)
        case Sum(_, body):
            return is_constant(body)
        case _:
            return False


def is_affine(expr: Expr) -> bool:
    """
    Check if expression is affine (linear in variables).

    An expression is affine if it can be written as a₀ + a₁x₁ + a₂x₂ + ...
    where aᵢ are constants (possibly parameters).

    Args:
        expr: Expression to check

    Returns:
        True if expression is affine in decision variables
    """
    match expr:
        case Const(_) | ParamRef(_):
            return True
        case VarRef(_):
            return True
        case Binary(op, left, right) if op in ("+", "-"):
            return is_affine(left) and is_affine(right)
        case Binary("*", left, right):
            # Affine if one side is constant and other is affine
            return (is_constant(left) and is_affine(right)) or (
                is_affine(left) and is_constant(right)
            )
        case Binary("/", left, right):
            # Affine if numerator is affine and denominator is constant
            return is_affine(left) and is_constant(right)
        case Unary("-", operand):
            return is_affine(operand)
        case Unary("+", operand):
            return is_affine(operand)
        case Sum(_, body):
            return is_affine(body)
        case _:
            return False


def has_variable(expr: Expr) -> bool:
    """
    Check if expression contains any decision variables.

    Args:
        expr: Expression to check

    Returns:
        True if expression contains at least one VarRef
    """
    match expr:
        case VarRef(_):
            return True
        case Binary(_, left, right):
            return has_variable(left) or has_variable(right)
        case Unary(_, operand):
            return has_variable(operand)
        case Call(_, args):
            return any(has_variable(arg) for arg in args)
        case Sum(_, body):
            return has_variable(body)
        case _:
            return False


def find_matching_nodes(
    expr: Expr,
    predicate: Callable[[Expr], bool],
) -> list[Expr]:
    """
    Find all AST nodes matching a predicate.

    Args:
        expr: Expression to traverse
        predicate: Function that returns True for matching nodes

    Returns:
        List of matching expression nodes
    """
    matches = []

    def traverse(e: Expr) -> None:
        if predicate(e):
            matches.append(e)

        match e:
            case Binary(_, left, right):
                traverse(left)
                traverse(right)
            case Unary(_, operand):
                traverse(operand)
            case Call(_, args):
                for arg in args:
                    traverse(arg)
            case Sum(_, body):
                traverse(body)
            case _:
                pass

    traverse(expr)
    return matches

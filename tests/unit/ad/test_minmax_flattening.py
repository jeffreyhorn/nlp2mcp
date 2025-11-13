"""
Tests for Nested Min/Max Flattening (Sprint 6 Day 2)

Test Coverage:
-------------
1. Detection of SAME_TYPE_NESTING (min(min(...)), max(max(...)))
2. Detection of MIXED_NESTING (min(max(...)), max(min(...)))
3. Detection of NO_NESTING (flat structures)
4. Flattening of simple nested structures
5. Flattening of deeply nested structures
6. Preservation of mixed nesting (should NOT flatten)
7. Nesting depth and argument count analysis
8. Integration with full AST visitor
9. Edge cases: empty args, single arg, multiple levels
10. Preservation of non-min/max expressions
"""

import pytest

from src.ad.minmax_flattener import (
    NestingType,
    analyze_nesting,
    detect_minmax_nesting,
    flatten_all_minmax,
    flatten_minmax,
)
from src.ir.ast import Binary, Call, Const, VarRef

pytestmark = pytest.mark.unit


# ===== Detection Tests =====


@pytest.mark.unit
class TestNestingDetection:
    """Test detection of min/max nesting patterns."""

    def test_detects_nested_min(self):
        """Should detect min(min(x,y),z) as SAME_TYPE_NESTING."""
        expr = Call(
            "min",
            (Call("min", (VarRef("x"), VarRef("y"))), VarRef("z")),
        )

        nesting_type = detect_minmax_nesting(expr)
        assert nesting_type == NestingType.SAME_TYPE_NESTING

    def test_detects_nested_max(self):
        """Should detect max(max(x,y),z) as SAME_TYPE_NESTING."""
        expr = Call(
            "max",
            (Call("max", (VarRef("x"), VarRef("y"))), VarRef("z")),
        )

        nesting_type = detect_minmax_nesting(expr)
        assert nesting_type == NestingType.SAME_TYPE_NESTING

    def test_detects_mixed_nesting_min_max(self):
        """Should detect min(max(x,y),z) as MIXED_NESTING."""
        expr = Call(
            "min",
            (Call("max", (VarRef("x"), VarRef("y"))), VarRef("z")),
        )

        nesting_type = detect_minmax_nesting(expr)
        assert nesting_type == NestingType.MIXED_NESTING

    def test_detects_mixed_nesting_max_min(self):
        """Should detect max(min(x,y),z) as MIXED_NESTING."""
        expr = Call(
            "max",
            (Call("min", (VarRef("x"), VarRef("y"))), VarRef("z")),
        )

        nesting_type = detect_minmax_nesting(expr)
        assert nesting_type == NestingType.MIXED_NESTING

    def test_detects_no_nesting_flat_min(self):
        """Should detect min(x,y,z) as NO_NESTING."""
        expr = Call("min", (VarRef("x"), VarRef("y"), VarRef("z")))

        nesting_type = detect_minmax_nesting(expr)
        assert nesting_type == NestingType.NO_NESTING

    def test_detects_no_nesting_non_minmax(self):
        """Should detect exp(x) as NO_NESTING."""
        expr = Call("exp", (VarRef("x"),))

        nesting_type = detect_minmax_nesting(expr)
        assert nesting_type == NestingType.NO_NESTING

    def test_detects_no_nesting_const(self):
        """Should detect Const(5) as NO_NESTING."""
        expr = Const(5.0)

        nesting_type = detect_minmax_nesting(expr)
        assert nesting_type == NestingType.NO_NESTING

    def test_detects_deep_nesting(self):
        """Should detect min(min(min(x,y),z),w) as SAME_TYPE_NESTING."""
        expr = Call(
            "min",
            (
                Call(
                    "min",
                    (Call("min", (VarRef("x"), VarRef("y"))), VarRef("z")),
                ),
                VarRef("w"),
            ),
        )

        nesting_type = detect_minmax_nesting(expr)
        assert nesting_type == NestingType.SAME_TYPE_NESTING

    def test_detects_multiple_nested_args(self):
        """Should detect min(min(x,y), min(z,w)) as SAME_TYPE_NESTING."""
        expr = Call(
            "min",
            (
                Call("min", (VarRef("x"), VarRef("y"))),
                Call("min", (VarRef("z"), VarRef("w"))),
            ),
        )

        nesting_type = detect_minmax_nesting(expr)
        assert nesting_type == NestingType.SAME_TYPE_NESTING


# ===== Analysis Tests =====


@pytest.mark.unit
class TestNestingAnalysis:
    """Test detailed nesting analysis (depth, arg count)."""

    def test_analyzes_simple_nesting(self):
        """Should compute depth=2, total_args=3 for min(min(x,y),z)."""
        expr = Call(
            "min",
            (Call("min", (VarRef("x"), VarRef("y"))), VarRef("z")),
        )

        info = analyze_nesting(expr)
        assert info.nesting_type == NestingType.SAME_TYPE_NESTING
        assert info.outer_func == "min"
        assert info.depth == 2
        assert info.total_args == 3

    def test_analyzes_deep_nesting(self):
        """Should compute depth=3, total_args=4 for min(min(min(x,y),z),w)."""
        expr = Call(
            "min",
            (
                Call(
                    "min",
                    (Call("min", (VarRef("x"), VarRef("y"))), VarRef("z")),
                ),
                VarRef("w"),
            ),
        )

        info = analyze_nesting(expr)
        assert info.nesting_type == NestingType.SAME_TYPE_NESTING
        assert info.outer_func == "min"
        assert info.depth == 3
        assert info.total_args == 4

    def test_analyzes_flat_structure(self):
        """Should compute depth=1, total_args=3 for min(x,y,z)."""
        expr = Call("min", (VarRef("x"), VarRef("y"), VarRef("z")))

        info = analyze_nesting(expr)
        assert info.nesting_type == NestingType.NO_NESTING
        assert info.outer_func == "min"
        assert info.depth == 1
        assert info.total_args == 3

    def test_analyzes_mixed_nesting(self):
        """Should return depth=-1 for mixed nesting."""
        expr = Call(
            "min",
            (Call("max", (VarRef("x"), VarRef("y"))), VarRef("z")),
        )

        info = analyze_nesting(expr)
        assert info.nesting_type == NestingType.MIXED_NESTING
        assert info.outer_func == "min"
        assert info.depth == -1
        assert info.total_args == -1

    def test_analyzes_multiple_branches(self):
        """Should compute correct depth for min(min(x,y), min(z,w))."""
        expr = Call(
            "min",
            (
                Call("min", (VarRef("x"), VarRef("y"))),
                Call("min", (VarRef("z"), VarRef("w"))),
            ),
        )

        info = analyze_nesting(expr)
        assert info.nesting_type == NestingType.SAME_TYPE_NESTING
        assert info.outer_func == "min"
        assert info.depth == 2  # Max depth across branches
        assert info.total_args == 4  # All leaf args


# ===== Flattening Tests =====


@pytest.mark.unit
class TestMinMaxFlattening:
    """Test flattening transformation."""

    def test_flattens_simple_min(self):
        """Should flatten min(min(x,y),z) to min(x,y,z)."""
        nested = Call(
            "min",
            (Call("min", (VarRef("x"), VarRef("y"))), VarRef("z")),
        )

        flat = flatten_minmax(nested)

        assert isinstance(flat, Call)
        assert flat.func == "min"
        assert len(flat.args) == 3
        assert all(isinstance(arg, VarRef) for arg in flat.args)

    def test_flattens_simple_max(self):
        """Should flatten max(max(a,b),c) to max(a,b,c)."""
        nested = Call(
            "max",
            (Call("max", (VarRef("a"), VarRef("b"))), VarRef("c")),
        )

        flat = flatten_minmax(nested)

        assert isinstance(flat, Call)
        assert flat.func == "max"
        assert len(flat.args) == 3

    def test_flattens_deep_nesting(self):
        """Should flatten min(min(min(w,x),y),z) to min(w,x,y,z)."""
        deep_nested = Call(
            "min",
            (
                Call(
                    "min",
                    (Call("min", (VarRef("w"), VarRef("x"))), VarRef("y")),
                ),
                VarRef("z"),
            ),
        )

        flat = flatten_minmax(deep_nested)

        assert isinstance(flat, Call)
        assert flat.func == "min"
        assert len(flat.args) == 4

    def test_preserves_mixed_nesting(self):
        """Should NOT flatten min(max(x,y),z) - returns unchanged."""
        mixed = Call(
            "min",
            (Call("max", (VarRef("x"), VarRef("y"))), VarRef("z")),
        )

        result = flatten_minmax(mixed)

        # Should be unchanged - still nested
        assert isinstance(result, Call)
        assert result.func == "min"
        assert len(result.args) == 2  # Still has inner Call + z
        assert isinstance(result.args[0], Call)

    def test_preserves_flat_structure(self):
        """Should preserve min(x,y,z) as-is."""
        flat = Call("min", (VarRef("x"), VarRef("y"), VarRef("z")))

        result = flatten_minmax(flat)

        assert isinstance(result, Call)
        assert result.func == "min"
        assert len(result.args) == 3

    def test_preserves_non_minmax(self):
        """Should preserve exp(x) unchanged."""
        expr = Call("exp", (VarRef("x"),))

        result = flatten_minmax(expr)

        assert isinstance(result, Call)
        assert result.func == "exp"
        assert len(result.args) == 1

    def test_flattens_multiple_branches(self):
        """Should flatten min(min(x,y), min(z,w)) to min(x,y,z,w)."""
        expr = Call(
            "min",
            (
                Call("min", (VarRef("x"), VarRef("y"))),
                Call("min", (VarRef("z"), VarRef("w"))),
            ),
        )

        flat = flatten_minmax(expr)

        assert isinstance(flat, Call)
        assert flat.func == "min"
        assert len(flat.args) == 4


# ===== Full Visitor Tests =====


@pytest.mark.unit
class TestFullVisitor:
    """Test complete AST visitor with flatten_all_minmax."""

    def test_flattens_top_level_min(self):
        """Should flatten top-level min(min(x,y),z)."""
        expr = Call(
            "min",
            (Call("min", (VarRef("x"), VarRef("y"))), VarRef("z")),
        )

        result = flatten_all_minmax(expr)

        assert isinstance(result, Call)
        assert result.func == "min"
        assert len(result.args) == 3

    def test_flattens_nested_in_binary(self):
        """Should flatten min inside binary operation: min(min(x,y),z) + w."""
        expr = Binary(
            "+",
            Call("min", (Call("min", (VarRef("x"), VarRef("y"))), VarRef("z"))),
            VarRef("w"),
        )

        result = flatten_all_minmax(expr)

        assert isinstance(result, Binary)
        assert result.op == "+"
        # Left side should be flattened
        assert isinstance(result.left, Call)
        assert result.left.func == "min"
        assert len(result.left.args) == 3

    def test_flattens_multiple_min_max_in_expr(self):
        """Should flatten both min and max in: min(min(x,y),z) + max(max(a,b),c)."""
        expr = Binary(
            "+",
            Call("min", (Call("min", (VarRef("x"), VarRef("y"))), VarRef("z"))),
            Call("max", (Call("max", (VarRef("a"), VarRef("b"))), VarRef("c"))),
        )

        result = flatten_all_minmax(expr)

        assert isinstance(result, Binary)
        # Both sides should be flattened
        assert isinstance(result.left, Call)
        assert result.left.func == "min"
        assert len(result.left.args) == 3

        assert isinstance(result.right, Call)
        assert result.right.func == "max"
        assert len(result.right.args) == 3

    def test_preserves_mixed_nesting_in_complex_expr(self):
        """Should NOT flatten mixed nesting even in complex expressions."""
        expr = Binary(
            "+",
            Call("min", (Call("max", (VarRef("x"), VarRef("y"))), VarRef("z"))),
            VarRef("w"),
        )

        result = flatten_all_minmax(expr)

        assert isinstance(result, Binary)
        # Left side should still be nested (mixed nesting)
        assert isinstance(result.left, Call)
        assert result.left.func == "min"
        assert len(result.left.args) == 2  # Still has inner Call

    def test_handles_const_nodes(self):
        """Should handle Const nodes without modification."""
        expr = Const(5.0)

        result = flatten_all_minmax(expr)

        assert isinstance(result, Const)
        assert result.value == 5.0

    def test_handles_varref_nodes(self):
        """Should handle VarRef nodes without modification."""
        expr = VarRef("x")

        result = flatten_all_minmax(expr)

        assert isinstance(result, VarRef)
        assert result.name == "x"


# ===== Edge Case Tests =====


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and corner scenarios."""

    def test_single_arg_min(self):
        """Should handle min(x) as NO_NESTING."""
        expr = Call("min", (VarRef("x"),))

        nesting_type = detect_minmax_nesting(expr)
        assert nesting_type == NestingType.NO_NESTING

        # Flattening should preserve it
        result = flatten_minmax(expr)
        assert isinstance(result, Call)
        assert result.func == "min"
        assert len(result.args) == 1

    def test_nested_with_constants(self):
        """Should flatten min(min(5,x),y) to min(5,x,y)."""
        expr = Call(
            "min",
            (Call("min", (Const(5.0), VarRef("x"))), VarRef("y")),
        )

        result = flatten_minmax(expr)

        assert isinstance(result, Call)
        assert result.func == "min"
        assert len(result.args) == 3
        assert isinstance(result.args[0], Const)

    def test_asymmetric_nesting(self):
        """Should flatten min(x, min(y,z)) where nesting is in second arg."""
        expr = Call(
            "min",
            (VarRef("x"), Call("min", (VarRef("y"), VarRef("z")))),
        )

        result = flatten_minmax(expr)

        assert isinstance(result, Call)
        assert result.func == "min"
        assert len(result.args) == 3

    def test_very_deep_nesting(self):
        """Should handle 5-level nesting."""
        # min(min(min(min(min(a,b),c),d),e),f)
        expr = Call(
            "min",
            (
                Call(
                    "min",
                    (
                        Call(
                            "min",
                            (
                                Call(
                                    "min",
                                    (
                                        Call(
                                            "min",
                                            (VarRef("a"), VarRef("b")),
                                        ),
                                        VarRef("c"),
                                    ),
                                ),
                                VarRef("d"),
                            ),
                        ),
                        VarRef("e"),
                    ),
                ),
                VarRef("f"),
            ),
        )

        result = flatten_minmax(expr)

        assert isinstance(result, Call)
        assert result.func == "min"
        assert len(result.args) == 6  # All args collected

    def test_preserves_arg_order(self):
        """Should preserve argument order when flattening."""
        expr = Call(
            "min",
            (Call("min", (VarRef("x"), VarRef("y"))), VarRef("z")),
        )

        result = flatten_minmax(expr)

        assert isinstance(result, Call)
        # Order should be: x, y, z
        assert result.args[0].name == "x"
        assert result.args[1].name == "y"
        assert result.args[2].name == "z"


# ===== Integration Tests =====


@pytest.mark.unit
class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    def test_nested_min_in_objective(self):
        """Simulates objective function with nested min."""
        # Objective: minimize x^2 + min(min(y,z),w)
        objective = Binary(
            "+",
            Binary("^", VarRef("x"), Const(2.0)),
            Call("min", (Call("min", (VarRef("y"), VarRef("z"))), VarRef("w"))),
        )

        result = flatten_all_minmax(objective)

        # Structure should be preserved, min should be flattened
        assert isinstance(result, Binary)
        assert result.op == "+"
        # Right side should have flattened min
        assert isinstance(result.right, Call)
        assert result.right.func == "min"
        assert len(result.right.args) == 3

    def test_nested_max_in_constraint(self):
        """Simulates constraint with nested max."""
        # Constraint: max(max(x,y),z) <= 10
        constraint = Binary(
            "<=",
            Call("max", (Call("max", (VarRef("x"), VarRef("y"))), VarRef("z"))),
            Const(10.0),
        )

        result = flatten_all_minmax(constraint)

        # Left side should be flattened
        assert isinstance(result, Binary)
        assert result.op == "<="
        assert isinstance(result.left, Call)
        assert result.left.func == "max"
        assert len(result.left.args) == 3

    def test_complex_nested_expression(self):
        """Tests deeply nested expression with multiple operations."""
        # Expression: min(x, max(y, min(z, w)))
        # Should only flatten the inner min(z,w) because max(y, min(...)) is flat
        # The outer min(x, max(...)) is also flat
        expr = Call(
            "min",
            (
                VarRef("x"),
                Call(
                    "max",
                    (VarRef("y"), Call("min", (VarRef("z"), VarRef("w")))),
                ),
            ),
        )

        result = flatten_all_minmax(expr)

        # Outer min should remain (it's flat)
        # Inner max should remain (it's flat)
        # Innermost min should remain (already flat)
        assert isinstance(result, Call)
        assert result.func == "min"
        assert len(result.args) == 2  # x and max(...)

    def test_no_modification_when_no_nesting(self):
        """Should return identical structure when no nesting exists."""
        expr = Binary(
            "+",
            Call("min", (VarRef("x"), VarRef("y"))),
            Call("max", (VarRef("z"), VarRef("w"))),
        )

        result = flatten_all_minmax(expr)

        # Should be structurally identical (new objects, same structure)
        assert isinstance(result, Binary)
        assert result.op == "+"
        assert isinstance(result.left, Call)
        assert result.left.func == "min"
        assert len(result.left.args) == 2
        assert isinstance(result.right, Call)
        assert result.right.func == "max"
        assert len(result.right.args) == 2

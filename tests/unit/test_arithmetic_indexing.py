"""Unit tests for arithmetic indexing (i++1, i--1, i+j) - Sprint 9 Day 3.

Tests focus on equation definitions and bounds, which are the primary use cases
for lead/lag indexing in GAMS (parameter assignments don't support IndexOffset).
"""

import pytest

from src.ir.parser import parse_model_text
from src.utils.errors import ParseError


class TestBasicArithmeticIndexing:
    """Test basic arithmetic indexing patterns in equations."""

    def test_circular_lead_constant(self):
        """Test circular lead with constant offset (i++1)."""
        source = """
Set i /1*5/;
Variable x(i);
Variable y(i);
Equation eq(i);
eq(i).. y(i) =e= x(i++1);
"""
        model = parse_model_text(source)
        assert model is not None
        assert "eq" in model.equations

    def test_circular_lag_constant(self):
        """Test circular lag with constant offset (i--2)."""
        source = """
Set i /1*5/;
Variable x(i);
Variable y(i);
Equation eq(i);
eq(i).. y(i) =e= x(i--2);
"""
        model = parse_model_text(source)
        assert model is not None
        assert "eq" in model.equations

    def test_linear_lead_constant(self):
        """Test linear lead with constant offset (i+1)."""
        source = """
Set i /1*5/;
Variable x(i);
Variable y(i);
Equation eq(i);
eq(i).. y(i) =e= x(i+1);
"""
        model = parse_model_text(source)
        assert model is not None
        assert "eq" in model.equations

    def test_linear_lag_constant(self):
        """Test linear lag with constant offset (i-3)."""
        source = """
Set i /1*5/;
Variable x(i);
Variable y(i);
Equation eq(i);
eq(i).. y(i) =e= x(i-3);
"""
        model = parse_model_text(source)
        assert model is not None
        assert "eq" in model.equations

    def test_variable_offset_lead(self):
        """Test lead with variable offset (i+j)."""
        source = """
Set i /1*5/;
Set j /1*3/;
Variable x(i);
Variable y(i,j);
Equation eq(i,j);
eq(i,j).. y(i,j) =e= x(i+j);
"""
        model = parse_model_text(source)
        assert model is not None
        assert "eq" in model.equations

    def test_variable_offset_circular_lag(self):
        """Test circular lag with variable offset (i--j)."""
        source = """
Set i /1*5/;
Set j /1*3/;
Variable x(i);
Variable y(i,j);
Equation eq(i,j);
eq(i,j).. y(i,j) =e= x(i--j);
"""
        model = parse_model_text(source)
        assert model is not None
        assert "eq" in model.equations

    def test_variable_offset_linear_lag(self):
        """Test linear lag with variable offset (i-j)."""
        source = """
Set i /1*5/;
Set j /1*3/;
Variable x(i);
Variable y(i,j);
Equation eq(i,j);
eq(i,j).. y(i,j) =e= x(i-j);
"""
        model = parse_model_text(source)
        assert model is not None
        assert "eq" in model.equations


class TestEdgeCaseIndexing:
    """Test edge cases and boundary conditions."""

    def test_zero_offset(self):
        """Test zero offset (i++0 should equal i)."""
        source = """
Set i /1*5/;
Variable x(i);
Variable y(i);
Equation eq(i);
eq(i).. y(i) =e= x(i++0);
"""
        model = parse_model_text(source)
        assert model is not None

    def test_large_offset(self):
        """Test large offset values (i++10, i--100)."""
        source = """
Set i /1*200/;
Variable x(i);
Variable y(i);
Variable z(i);
Equation eq1(i);
Equation eq2(i);
eq1(i).. y(i) =e= x(i++10);
eq2(i).. z(i) =e= x(i--100);
"""
        model = parse_model_text(source)
        assert model is not None

    def test_two_element_set(self):
        """Test indexing on two-element set (minimal wrap-around)."""
        source = """
Set i /1*2/;
Variable x(i);
Variable y(i);
Equation eq(i);
eq(i).. y(i) =e= x(i++1);
"""
        model = parse_model_text(source)
        assert model is not None


class TestMultiDimensionalIndexing:
    """Test multi-dimensional indexing with lead/lag."""

    def test_two_dimensional_both_lead(self):
        """Test 2D indexing with both indices having lead (x(i++1, j++1))."""
        source = """
Set i /1*5/;
Set j /1*5/;
Variable x(i,j);
Variable y(i,j);
Equation eq(i,j);
eq(i,j).. y(i,j) =e= x(i++1, j++1);
"""
        model = parse_model_text(source)
        assert model is not None

    def test_two_dimensional_mixed_lead_lag(self):
        """Test 2D indexing with lead and lag (x(i++1, j--2))."""
        source = """
Set i /1*5/;
Set j /1*5/;
Variable x(i,j);
Variable y(i,j);
Equation eq(i,j);
eq(i,j).. y(i,j) =e= x(i++1, j--2);
"""
        model = parse_model_text(source)
        assert model is not None

    def test_three_dimensional_all_lead(self):
        """Test 3D indexing with all lead offsets."""
        source = """
Set i /1*3/;
Set j /1*3/;
Set k /1*3/;
Variable x(i,j,k);
Variable y(i,j,k);
Equation eq(i,j,k);
eq(i,j,k).. y(i,j,k) =e= x(i++1, j++1, k++1);
"""
        model = parse_model_text(source)
        assert model is not None

    def test_mixed_plain_and_offset_indices(self):
        """Test mixing plain indices with offset indices (x(i, j++1, k))."""
        source = """
Set i /1*3/;
Set j /1*3/;
Set k /1*3/;
Variable x(i,j,k);
Variable y(i,j,k);
Equation eq(i,j,k);
eq(i,j,k).. y(i,j,k) =e= x(i, j++1, k);
"""
        model = parse_model_text(source)
        assert model is not None


class TestEquationIndexing:
    """Test arithmetic indexing in equation definitions."""

    def test_equation_with_circular_lead(self):
        """Test equation with circular lead indexing."""
        source = """
Set i /1*5/;
Variable x(i);
Variable y(i);
Equation eq(i);
eq(i).. y(i) =e= x(i++1);
"""
        model = parse_model_text(source)
        assert model is not None
        assert "eq" in model.equations

    def test_equation_with_multiple_offsets(self):
        """Test equation with multiple different offsets."""
        source = """
Set i /1*5/;
Variable x(i);
Variable y(i);
Equation eq(i);
eq(i).. y(i) =e= x(i++1) + x(i--1) + x(i+2);
"""
        model = parse_model_text(source)
        assert model is not None
        assert "eq" in model.equations

    def test_equation_with_variable_offset(self):
        """Test equation with variable offset (i+j)."""
        source = """
Set i /1*5/;
Set j /1*3/;
Variable x(i);
Variable y(i,j);
Equation eq(i,j);
eq(i,j).. y(i,j) =e= x(i+j);
"""
        model = parse_model_text(source)
        assert model is not None
        assert "eq" in model.equations


class TestBoundIndexing:
    """Test arithmetic indexing in variable bounds."""

    def test_lower_bound_with_lead(self):
        """Test lower bound with lead indexing (x.lo(i++1))."""
        source = """
Set i /1*5/;
Variable x(i);
x.lo(i++1) = 10;
"""
        model = parse_model_text(source)
        assert model is not None
        assert "x" in model.variables

    def test_upper_bound_with_lag(self):
        """Test upper bound with lag indexing (x.up(i--2))."""
        source = """
Set i /1*5/;
Variable x(i);
x.up(i--2) = 100;
"""
        model = parse_model_text(source)
        assert model is not None
        assert "x" in model.variables

    def test_fixed_bound_with_variable_offset(self):
        """Test fixed bound with variable offset (x.fx(i+j, j))."""
        source = """
Set i /1*5/;
Set j /1*3/;
Variable x(i,j);
x.fx(i+j, j) = 50;
"""
        model = parse_model_text(source)
        assert model is not None
        assert "x" in model.variables


class TestComplexExpressions:
    """Test arithmetic indexing in complex expressions."""

    def test_multiple_references_same_variable(self):
        """Test multiple references with different offsets."""
        source = """
Set i /1*5/;
Variable x(i);
Variable y(i);
Equation eq(i);
eq(i).. y(i) =e= x(i++1) + x(i--1) + x(i+2) - x(i-2);
"""
        model = parse_model_text(source)
        assert model is not None

    def test_arithmetic_with_offset_indices(self):
        """Test arithmetic operations with offset indices."""
        source = """
Set i /1*5/;
Variable x(i);
Variable y(i);
Equation eq(i);
eq(i).. y(i) =e= 2 * x(i++1) + 3 * x(i--1);
"""
        model = parse_model_text(source)
        assert model is not None

    def test_function_call_with_offset(self):
        """Test function call with offset indexing."""
        source = """
Set i /1*5/;
Variable x(i);
Variable y(i);
Equation eq(i);
eq(i).. y(i) =e= sqrt(x(i++1));
"""
        model = parse_model_text(source)
        assert model is not None


class TestRealWorldPatterns:
    """Test patterns from actual GAMSLib models (himmel16.gms style)."""

    def test_himmel16_pattern(self):
        """Test pattern from himmel16.gms (i++1 in constraints)."""
        source = """
Set i /1*6/;
Variable x(i);
Variable y(i);
Equation eq1(i);
Equation eq2;
eq1(i).. 2*x(i) - x(i++1) =l= 0;
eq2.. sum(i, x(i)) =e= 1;
"""
        model = parse_model_text(source)
        assert model is not None
        assert "eq1" in model.equations
        assert "eq2" in model.equations

    def test_inventory_balance_pattern(self):
        """Test inventory balance pattern (stock(t) transitions)."""
        source = """
Set t /1*12/;
Variable stock(t);
Variable inflow(t);
Variable outflow(t);
Equation balance(t);
balance(t).. stock(t++1) =e= stock(t) + inflow(t) - outflow(t);
"""
        model = parse_model_text(source)
        assert model is not None


class TestErrorHandling:
    """Test error handling for invalid indexing patterns."""

    def test_parameter_assignment_with_lead_lag_rejected(self):
        """Test that lead/lag in parameter assignments is rejected."""
        source = """
Set i /1*5/;
Parameter x(i);
x(i++1) = 10;
"""
        # Parameter assignments don't support lead/lag offsets
        with pytest.raises(Exception):  # Should raise ParserSemanticError
            parse_model_text(source)


class TestBackwardCompatibility:
    """Test that plain indexing still works (backward compatibility)."""

    def test_plain_single_index(self):
        """Test plain single index (i) still works."""
        source = """
Set i /1*5/;
Variable x(i);
Variable y(i);
Equation eq(i);
eq(i).. y(i) =e= x(i);
"""
        model = parse_model_text(source)
        assert model is not None

    def test_plain_multi_index(self):
        """Test plain multi-index (i,j,k) still works."""
        source = """
Set i /1*3/;
Set j /1*3/;
Set k /1*3/;
Variable x(i,j,k);
Variable y(i,j,k);
Equation eq(i,j,k);
eq(i,j,k).. y(i,j,k) =e= x(i, j, k);
"""
        model = parse_model_text(source)
        assert model is not None

    def test_mixed_plain_and_offset(self):
        """Test mixing plain indices with offset indices."""
        source = """
Set i /1*5/;
Set j /1*5/;
Variable x(i,j);
Variable y(i,j);
Equation eq(i,j);
eq(i, j).. y(i, j) =e= x(i++1, j);
"""
        model = parse_model_text(source)
        assert model is not None

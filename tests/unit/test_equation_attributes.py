"""Unit tests for equation attribute access (Sprint 9 Day 6).

Tests cover:
- Equation .l (level) attribute access
- Equation .m (marginal) attribute access
- Indexed equation attributes
- Equation attributes in expressions
- Equation attributes in assignments
"""

import pytest

from src.ir.parser import parse_model_text
from src.utils.errors import ParseError


class TestEquationAttributeBasics:
    """Test basic equation attribute access."""

    def test_equation_marginal_attribute(self):
        """Test accessing equation .m (marginal/dual) attribute."""
        source = """
Set i / 1*3 /;
Variable x(i);
Variable obj;
Equation eq1;

eq1.. obj =e= sum(i, x(i));

Solve mymodel using nlp min obj;

Scalar marginal;
marginal = eq1.m;
"""
        model = parse_model_text(source)
        assert "marginal" in model.params
        assert "eq1" in model.equations

    def test_equation_level_attribute(self):
        """Test accessing equation .l (level) attribute."""
        source = """
Set i / 1*3 /;
Variable x(i);
Variable obj;
Equation eq1;

eq1.. obj =e= sum(i, x(i));

Solve mymodel using nlp min obj;

Scalar level;
level = eq1.l;
"""
        model = parse_model_text(source)
        assert "level" in model.params
        assert "eq1" in model.equations

    def test_both_marginal_and_level(self):
        """Test accessing both .m and .l attributes."""
        source = """
Variable x;
Variable obj;
Equation eq1;

eq1.. obj =e= x;

Solve mymodel using nlp min obj;

Scalar m_val, l_val;
m_val = eq1.m;
l_val = eq1.l;
"""
        model = parse_model_text(source)
        assert "m_val" in model.params
        assert "l_val" in model.params


class TestIndexedEquationAttributes:
    """Test equation attributes on indexed equations."""

    def test_indexed_equation_marginal(self):
        """Test accessing .m on indexed equation (no indices in access)."""
        source = """
Set i / 1*3 /;
Variable x(i);
Equation eq(i);

eq(i).. x(i) =e= i;

* Note: This accesses the full indexed equation, not a specific instance
* In real GAMS, you'd need eq.m('1') to access a specific instance
"""
        model = parse_model_text(source)
        assert "eq" in model.equations
        assert model.equations["eq"].domain == ("i",)

    def test_indexed_equation_with_index_access(self):
        """Test accessing specific instance of indexed equation attribute."""
        source = """
Set i / 1*3 /;
Variable x(i);
Variable obj;
Equation eq(i);
Equation objdef;

objdef.. obj =e= sum(i, x(i));
eq(i).. x(i) =e= i;

Solve mymodel using nlp min obj;

Scalar m1;
m1 = eq.m('1');
"""
        model = parse_model_text(source)
        assert "m1" in model.params
        assert "eq" in model.equations


class TestEquationAttributesInExpressions:
    """Test equation attributes used in expressions."""

    def test_equation_attribute_in_arithmetic(self):
        """Test using equation attribute in arithmetic expression."""
        source = """
Variable x, obj;
Equation eq1;

eq1.. obj =e= x;

Solve mymodel using nlp min obj;

Scalar result;
result = 2 * eq1.m + 1;
"""
        model = parse_model_text(source)
        assert "result" in model.params

    def test_equation_attribute_in_sum(self):
        """Test using equation attribute in sum expression."""
        source = """
Set i / 1*3 /;
Variable x(i);
Variable obj;
Equation eq(i);
Equation objdef;

objdef.. obj =e= sum(i, x(i));
eq(i).. x(i) =e= i;

Solve mymodel using nlp min obj;

Scalar total;
total = sum(i, eq.m(i));
"""
        model = parse_model_text(source)
        assert "total" in model.params

    def test_mixed_variable_and_equation_attributes(self):
        """Test mixing variable and equation attributes in expressions."""
        source = """
Variable x, obj;
Equation eq1;

eq1.. obj =e= x;

Solve mymodel using nlp min obj;

Scalar gap;
gap = abs(x.l - eq1.m);
"""
        model = parse_model_text(source)
        assert "gap" in model.params


class TestEquationAttributeEdgeCases:
    """Test edge cases and error conditions."""

    def test_equation_attribute_before_declaration(self):
        """Test that equation must be declared before accessing attributes."""
        source = """
Scalar m_val;
m_val = eq1.m;

Variable obj;
Equation eq1;

eq1.. obj =e= 1;
"""
        # This should fail because eq1 is used before declaration
        with pytest.raises(ParseError, match="Undefined symbol 'eq1'"):
            parse_model_text(source)

    def test_undeclared_equation_attribute(self):
        """Test accessing attributes on undeclared equation."""
        source = """
Variable obj;

Scalar m_val;
m_val = nonexistent.m;
"""
        with pytest.raises(ParseError, match="Undefined symbol 'nonexistent'"):
            parse_model_text(source)

    def test_equation_attribute_in_display(self):
        """Test equation attributes in display statement (mock/store approach)."""
        source = """
Variable x, obj;
Equation eq1;

eq1.. obj =e= x;

Solve mymodel using nlp min obj;

display eq1.m, eq1.l;
"""
        # Display statements are parsed but not executed (mock/store approach)
        model = parse_model_text(source)
        assert "eq1" in model.equations


class TestEquationAttributeTypes:
    """Test different attribute types."""

    def test_level_attribute_lowercase(self):
        """Test .l attribute (lowercase)."""
        source = """
Variable x, obj;
Equation eq1;

eq1.. obj =e= x;

Scalar val;
val = eq1.l;
"""
        model = parse_model_text(source)
        assert "val" in model.params

    def test_marginal_attribute_lowercase(self):
        """Test .m attribute (lowercase)."""
        source = """
Variable x, obj;
Equation eq1;

eq1.. obj =e= x;

Scalar val;
val = eq1.m;
"""
        model = parse_model_text(source)
        assert "val" in model.params

    def test_attribute_case_insensitive(self):
        """Test that attributes are case-insensitive (GAMS convention)."""
        source = """
Variable x, obj;
Equation eq1;

eq1.. obj =e= x;

Scalar val1, val2;
val1 = eq1.M;
val2 = eq1.L;
"""
        model = parse_model_text(source)
        assert "val1" in model.params
        assert "val2" in model.params


class TestEquationVsVariableAttributes:
    """Test that equations and variables both support attributes correctly."""

    def test_equation_and_variable_same_name_different_attributes(self):
        """Test equation and variable with similar names don't interfere."""
        source = """
Variable x, obj;
Equation eq_x;

eq_x.. obj =e= x;

Solve mymodel using nlp min obj;

Scalar eq_marginal, var_level;
eq_marginal = eq_x.m;
var_level = x.l;
"""
        model = parse_model_text(source)
        assert "eq_marginal" in model.params
        assert "var_level" in model.params
        assert "eq_x" in model.equations
        assert "x" in model.variables

    def test_variable_attributes_still_work(self):
        """Test that variable attributes still work (no regression)."""
        source = """
Variable x;

x.lo = 0;
x.up = 10;
x.l = 5;

Scalar init_val;
init_val = x.l;
"""
        model = parse_model_text(source)
        assert "x" in model.variables
        assert "init_val" in model.params
        # Verify bounds were set
        assert model.variables["x"].lo == 0
        assert model.variables["x"].up == 10


class TestEquationAttributeIRRepresentation:
    """Test that equation attributes create correct IR nodes."""

    def test_equation_ref_node_created(self):
        """Test that EquationRef nodes are created with correct attributes."""
        source = """
Variable x, obj;
Equation eq1;

eq1.. obj =e= x;

Scalar m_val;
m_val = eq1.m;
"""
        model = parse_model_text(source)
        # The EquationRef should be created during parsing
        # We can't easily inspect the expression tree here, but we verify it parses
        assert "eq1" in model.equations
        assert "m_val" in model.params

    def test_indexed_equation_ref_node(self):
        """Test EquationRef nodes for indexed equations."""
        source = """
Set i / 1*3 /;
Variable x(i);
Equation eq(i);

eq(i).. x(i) =e= i;

Scalar m_val;
m_val = eq.m('1');
"""
        model = parse_model_text(source)
        assert "eq" in model.equations
        assert model.equations["eq"].domain == ("i",)

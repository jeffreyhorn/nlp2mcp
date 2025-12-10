"""Tests for loop statement conditional filter parsing (Issue #449).

GAMS allows filtering the iteration domain in loop statements using the $
operator: loop(i$(condition), ...). This was blocking gasoil.gms at line 111.
"""

from src.ir.parser import parse_text


class TestLoopConditionalFilterBasic:
    """Test basic loop conditional filter parsing."""

    def test_loop_filtered_simple(self):
        """Test loop with simple conditional filter."""
        code = """
Set i / i1*i5 /;
Parameter x(i);
loop(i$(ord(i)>1), x(i) = ord(i));
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_filtered_ord_condition(self):
        """Test loop with ord() in condition - the gasoil.gms pattern."""
        code = """
Set nc / nc1*nc4 /;
Parameter fact(nc);
fact('nc1') = 1;
loop(nc$(ord(nc)>1), fact(nc) = fact(nc-1)*ord(nc));
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_filtered_equality(self):
        """Test loop with equality condition."""
        code = """
Set i / i1*i5 /;
Parameter x(i);
loop(i$(ord(i)=3), x(i) = 100);
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_filtered_less_than(self):
        """Test loop with less than condition."""
        code = """
Set i / i1*i10 /;
Parameter x(i);
loop(i$(ord(i)<5), x(i) = ord(i));
"""
        tree = parse_text(code)
        assert tree is not None


class TestLoopConditionalFilterComplex:
    """Test complex conditional filter expressions."""

    def test_loop_filtered_and_condition(self):
        """Test loop with AND in condition."""
        code = """
Set i / i1*i10 /;
Parameter x(i);
loop(i$(ord(i)>2 and ord(i)<8), x(i) = ord(i));
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_filtered_or_condition(self):
        """Test loop with OR in condition."""
        code = """
Set i / i1*i10 /;
Parameter x(i);
loop(i$(ord(i)=1 or ord(i)=10), x(i) = 999);
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_filtered_parameter_condition(self):
        """Test loop with parameter in condition."""
        code = """
Set i / i1*i5 /;
Parameter a(i) / i1 1, i2 0, i3 1, i4 0, i5 1 /;
Parameter x(i);
loop(i$(a(i)>0), x(i) = ord(i));
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_filtered_arithmetic_condition(self):
        """Test loop with arithmetic in condition."""
        code = """
Set i / i1*i10 /;
Parameter x(i);
loop(i$(ord(i)*2 > 5), x(i) = ord(i));
"""
        tree = parse_text(code)
        assert tree is not None


class TestLoopConditionalFilterMultiIndex:
    """Test multi-index loop with conditional filter."""

    def test_loop_paren_filtered(self):
        """Test multi-index loop with conditional filter."""
        code = """
Set i / i1*i3 /;
Set j / j1*j3 /;
Parameter x(i,j);
loop((i,j)$(ord(i)=ord(j)), x(i,j) = 1);
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_paren_filtered_complex(self):
        """Test multi-index loop with complex condition."""
        code = """
Set i / i1*i5 /;
Set j / j1*j5 /;
Parameter x(i,j);
loop((i,j)$(ord(i)<ord(j)), x(i,j) = ord(i) + ord(j));
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_paren_filtered_three_indices(self):
        """Test three-index loop with conditional filter."""
        code = """
Set i / i1*i3 /;
Set j / j1*j3 /;
Set k / k1*k3 /;
Parameter x(i,j,k);
loop((i,j,k)$(ord(i)+ord(j)+ord(k) < 6), x(i,j,k) = 1);
"""
        tree = parse_text(code)
        assert tree is not None


class TestLoopConditionalFilterMultipleStatements:
    """Test loop conditional filter with multiple statements."""

    def test_loop_filtered_multiple_assignments(self):
        """Test filtered loop with multiple assignment statements."""
        code = """
Set i / i1*i5 /;
Parameter x(i), y(i);
loop(i$(ord(i)>1), x(i) = ord(i); y(i) = ord(i)*2;);
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_filtered_with_display(self):
        """Test filtered loop with display statement (no trailing semi)."""
        code = """
Set i / i1*i5 /;
Parameter x(i);
loop(i$(ord(i)>1), x(i) = ord(i); display x);
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_filtered_final_with_semi(self):
        """Test filtered loop where final statement has optional semicolon."""
        code = """
Set i / i1*i5 /;
Parameter x(i);
loop(i$(ord(i)>1), x(i) = ord(i););
"""
        tree = parse_text(code)
        assert tree is not None


class TestLoopConditionalFilterCaseInsensitive:
    """Test that LOOP keyword is case-insensitive."""

    def test_loop_lowercase_filtered(self):
        """Test lowercase loop with filter."""
        code = """
Set i / i1*i5 /;
Parameter x(i);
loop(i$(ord(i)>1), x(i) = ord(i));
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_uppercase_filtered(self):
        """Test uppercase LOOP with filter."""
        code = """
Set i / i1*i5 /;
Parameter x(i);
LOOP(i$(ord(i)>1), x(i) = ord(i));
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_mixedcase_filtered(self):
        """Test mixed case Loop with filter."""
        code = """
Set i / i1*i5 /;
Parameter x(i);
Loop(i$(ord(i)>1), x(i) = ord(i));
"""
        tree = parse_text(code)
        assert tree is not None

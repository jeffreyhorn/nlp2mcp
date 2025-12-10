"""Tests for loop over indexed/mapped set parsing (Issue #450).

GAMS allows loop(setname(i,j), ...) to iterate over a multi-dimensional set,
binding the index variables during iteration. This was blocking gasoil.gms.
"""

from src.ir.parser import parse_text


class TestLoopIndexedSetBasic:
    """Test basic loop over indexed set parsing."""

    def test_loop_indexed_set_2d(self):
        """Test loop over 2D indexed set."""
        code = """
Set i / i1*i3 /;
Set j / j1*j3 /;
Set map(i,j);
Parameter x(i,j);
loop(map(i,j), x(i,j) = 1);
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_indexed_set_3d(self):
        """Test loop over 3D indexed set."""
        code = """
Set i / i1*i3 /;
Set j / j1*j3 /;
Set k / k1*k3 /;
Set map(i,j,k);
Parameter x(i,j,k);
loop(map(i,j,k), x(i,j,k) = 1);
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_indexed_set_gasoil_pattern(self):
        """Test the exact gasoil.gms/copspart.inc pattern."""
        code = """
Set nm / nm1*nm3 /;
Set i / i1*i5 /;
Set mapitau(nm,i);
Set nh / nh1*nh5 /;
Set s / s1*s3 /;
Variable v(nh,s), z(nm,s);
Parameter itau(nm);
loop(mapitau(nm,i), v.l[nh,s] = 1);
"""
        tree = parse_text(code)
        assert tree is not None


class TestLoopIndexedSetFiltered:
    """Test loop over indexed set with conditional filter."""

    def test_loop_indexed_set_filtered(self):
        """Test loop over indexed set with filter."""
        code = """
Set i / i1*i5 /;
Set j / j1*j5 /;
Set map(i,j);
Parameter x(i,j);
loop(map(i,j)$(ord(i)>1), x(i,j) = ord(i));
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_indexed_set_filtered_complex(self):
        """Test loop over indexed set with complex filter."""
        code = """
Set i / i1*i5 /;
Set j / j1*j5 /;
Set map(i,j);
Parameter x(i,j);
loop(map(i,j)$(ord(i)<ord(j)), x(i,j) = ord(i) + ord(j));
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_indexed_set_filtered_and(self):
        """Test loop over indexed set with AND condition."""
        code = """
Set i / i1*i5 /;
Set j / j1*j5 /;
Set map(i,j);
Parameter x(i,j);
loop(map(i,j)$(ord(i)>1 and ord(j)>1), x(i,j) = 1);
"""
        tree = parse_text(code)
        assert tree is not None


class TestLoopIndexedSetBody:
    """Test loop over indexed set with various body statements."""

    def test_loop_indexed_set_with_assignment(self):
        """Test indexed set loop with simple assignment."""
        code = """
Set i / i1*i3 /;
Set j / j1*j3 /;
Set map(i,j);
Parameter x(i,j);
loop(map(i,j), x(i,j) = ord(i) * ord(j));
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_indexed_set_with_conditional_assignment(self):
        """Test indexed set loop with conditional assignment in body."""
        code = """
Set i / i1*i3 /;
Set j / j1*j3 /;
Set k / k1*k3 /;
Set map(i,j);
Parameter x(i,j,k);
loop(map(i,j), x(i,j,k)$(ord(k)>1) = 1);
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_indexed_set_multiple_statements(self):
        """Test indexed set loop with multiple statements."""
        code = """
Set i / i1*i3 /;
Set j / j1*j3 /;
Set map(i,j);
Parameter x(i,j), y(i,j);
loop(map(i,j), x(i,j) = ord(i); y(i,j) = ord(j););
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_indexed_set_level_attribute(self):
        """Test indexed set loop with level attribute access."""
        code = """
Set i / i1*i3 /;
Set j / j1*j3 /;
Set map(i,j);
Variable v(i,j);
loop(map(i,j), v.l(i,j) = 1);
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_indexed_set_bracket_notation(self):
        """Test indexed set loop with bracket notation."""
        code = """
Set i / i1*i3 /;
Set j / j1*j3 /;
Set map(i,j);
Variable v(i,j);
loop(map(i,j), v.l[i,j] = 1);
"""
        tree = parse_text(code)
        assert tree is not None


class TestLoopIndexedSetCaseInsensitive:
    """Test case insensitivity of LOOP keyword with indexed sets."""

    def test_loop_lowercase_indexed(self):
        """Test lowercase loop with indexed set."""
        code = """
Set i / i1*i3 /;
Set j / j1*j3 /;
Set map(i,j);
Parameter x(i,j);
loop(map(i,j), x(i,j) = 1);
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_uppercase_indexed(self):
        """Test uppercase LOOP with indexed set."""
        code = """
Set i / i1*i3 /;
Set j / j1*j3 /;
Set map(i,j);
Parameter x(i,j);
LOOP(map(i,j), x(i,j) = 1);
"""
        tree = parse_text(code)
        assert tree is not None

    def test_loop_mixedcase_indexed(self):
        """Test mixed case Loop with indexed set."""
        code = """
Set i / i1*i3 /;
Set j / j1*j3 /;
Set map(i,j);
Parameter x(i,j);
Loop(map(i,j), x(i,j) = 1);
"""
        tree = parse_text(code)
        assert tree is not None

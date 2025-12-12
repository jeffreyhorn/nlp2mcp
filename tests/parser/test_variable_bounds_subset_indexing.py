"""Tests for variable bounds with subset indexing (Sprint 12 - Issue #455).

When a variable is defined with multiple indices (e.g., f(a,i,j)) and bounds
are set using a subset that maps to those indices (e.g., f.lo(aij(as,i,j))),
the parser should correctly accept the bounds.
"""

from src.ir.parser import parse_model_text


class TestSubsetIndexingBasic:
    """Test basic variable bounds with subset indexing."""

    def test_bounds_with_subset_indexing_3d(self):
        """Test 3D variable bounds with subset indexing: f.lo(aij(as,i,j)) = 0;"""
        source = """
Set i / 1*3 /, j / 1*3 /;
Set a / a1, a2 /;
Set aij(a,i,j);
Set as(a) / a1 /;
Variable f(a,i,j);
f.lo(aij(as,i,j)) = 0;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_bounds_with_subset_indexing_2d(self):
        """Test 2D variable bounds with subset indexing: x.up(low(n,nn)) = 10;"""
        source = """
Set n / n1*n5 /, nn / n1*n5 /;
Set low(n,nn);
Variable x(n,nn);
x.up(low(n,nn)) = 10;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_bounds_with_simple_subset_full_indices(self):
        """Test bounds with simple subset using all indices: f.lo(aij(a,i,j)) = 0;"""
        source = """
Set i / 1*3 /, j / 1*3 /;
Set a / a1, a2 /;
Set aij(a,i,j);
Variable f(a,i,j);
f.lo(aij(a,i,j)) = 0;
"""
        model = parse_model_text(source)
        assert model is not None


class TestSubsetIndexingBoundTypes:
    """Test different bound types with subset indexing."""

    def test_lower_bound_with_subset(self):
        """Test lower bound with subset indexing."""
        source = """
Set i / 1*3 /, j / 1*3 /;
Set ij(i,j);
Variable x(i,j);
x.lo(ij(i,j)) = 0;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_upper_bound_with_subset(self):
        """Test upper bound with subset indexing."""
        source = """
Set i / 1*3 /, j / 1*3 /;
Set ij(i,j);
Variable x(i,j);
x.up(ij(i,j)) = 100;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_fixed_bound_with_subset(self):
        """Test fixed bound with subset indexing."""
        source = """
Set i / 1*3 /, j / 1*3 /;
Set ij(i,j);
Variable x(i,j);
x.fx(ij(i,j)) = 5;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_level_with_subset(self):
        """Test level (initial value) with subset indexing."""
        source = """
Set i / 1*3 /, j / 1*3 /;
Set ij(i,j);
Variable x(i,j);
x.l(ij(i,j)) = 1;
"""
        model = parse_model_text(source)
        assert model is not None


class TestSubsetIndexingWithFiltering:
    """Test subset indexing with additional filtering."""

    def test_subset_with_filtered_first_index(self):
        """Test subset with filtered first index: f.lo(aij(as,i,j))."""
        source = """
Set a / a1, a2 /;
Set i / 1*3 /;
Set j / 1*3 /;
Set as(a) / a1 /;
Set aij(a,i,j);
Variable f(a,i,j);
f.lo(aij(as,i,j)) = 0;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_subset_with_filtered_middle_index(self):
        """Test subset with filtered middle index."""
        source = """
Set a / a1, a2 /;
Set i / 1*3 /;
Set is(i) / 1, 2 /;
Set j / 1*3 /;
Set aij(a,i,j);
Variable f(a,i,j);
f.lo(aij(a,is,j)) = 0;
"""
        model = parse_model_text(source)
        assert model is not None


class TestSubsetIndexingGastransPattern:
    """Test patterns from gastrans.gms (the model that was blocking)."""

    def test_gastrans_flow_bounds_pattern(self):
        """Test the exact pattern from gastrans.gms: f.lo(aij(as,i,j)) = 0;"""
        source = """
Set a / active, passive /;
Set i / node1*node5 /;
Set j / node1*node5 /;
Set as(a) / active /;
Set aij(a,i,j) "arc subset";
Variable f(a,i,j) "arc flow";
f.lo(aij(as,i,j)) = 0;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_gastrans_with_multiple_bounds(self):
        """Test multiple bounds with subset indexing."""
        source = """
Set a / active, passive /;
Set i / node1*node5 /;
Set j / node1*node5 /;
Set as(a) / active /;
Set ap(a) / passive /;
Set aij(a,i,j) "arc subset";
Variable f(a,i,j) "arc flow";
f.lo(aij(as,i,j)) = 0;
f.up(aij(ap,i,j)) = 100;
"""
        model = parse_model_text(source)
        assert model is not None


class TestSubsetIndexingEdgeCases:
    """Test edge cases for subset indexing."""

    def test_single_index_subset(self):
        """Test 1D variable with subset indexing."""
        source = """
Set i / 1*5 /;
Set is(i) / 1, 3, 5 /;
Variable x(i);
x.lo(is(i)) = 0;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_four_dimensional_subset(self):
        """Test 4D variable with subset indexing."""
        source = """
Set a / a1, a2 /;
Set b / b1, b2 /;
Set c / c1, c2 /;
Set d / d1, d2 /;
Set abcd(a,b,c,d);
Variable w(a,b,c,d);
w.lo(abcd(a,b,c,d)) = 0;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_mixed_regular_and_subset_bounds(self):
        """Test mixing regular bounds with subset-indexed bounds."""
        source = """
Set i / 1*3 /;
Set j / 1*3 /;
Set ij(i,j);
Variable x(i,j);
x.lo(i,j) = 0;
x.up(ij(i,j)) = 10;
"""
        model = parse_model_text(source)
        assert model is not None


class TestSubsetIndexCaseInsensitive:
    """Test case insensitivity of subset indexing."""

    def test_uppercase_bound_modifier(self):
        """Test uppercase bound modifier with subset indexing."""
        source = """
Set i / 1*3 /, j / 1*3 /;
Set ij(i,j);
Variable x(i,j);
x.LO(ij(i,j)) = 0;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_mixedcase_bound_modifier(self):
        """Test mixed case bound modifier with subset indexing."""
        source = """
Set i / 1*3 /, j / 1*3 /;
Set ij(i,j);
Variable x(i,j);
x.Lo(ij(i,j)) = 0;
"""
        model = parse_model_text(source)
        assert model is not None


class TestSubsetIndexingErrorCases:
    """Test error handling for invalid subset indexing."""

    def test_subset_index_count_mismatch_too_few(self):
        """Test error when subset provides fewer indices than variable domain.

        f(a,i,j) expects 3 indices but aij(i) provides only 1.
        """
        import pytest

        from src.ir.parser import ParserSemanticError

        source = """
Set a / a1, a2 /;
Set i / 1*3 /;
Set j / 1*3 /;
Set aij(i);
Variable f(a,i,j);
f.lo(aij(i)) = 0;
"""
        with pytest.raises(ParserSemanticError, match=r"expect.*3.*indices.*provided 1"):
            parse_model_text(source)

    def test_subset_index_count_mismatch_too_many(self):
        """Test error when subset provides more indices than variable domain.

        x(i) expects 1 index but ij(i,j) provides 2.
        """
        import pytest

        from src.ir.parser import ParserSemanticError

        source = """
Set i / 1*3 /;
Set j / 1*3 /;
Set ij(i,j);
Variable x(i);
x.lo(ij(i,j)) = 0;
"""
        with pytest.raises(ParserSemanticError, match=r"expect.*1.*index.*provided 2"):
            parse_model_text(source)

    def test_subset_index_count_mismatch_3d_to_2d(self):
        """Test error when 3D subset used for 2D variable.

        x(i,j) expects 2 indices but aij(a,i,j) provides 3.
        """
        import pytest

        from src.ir.parser import ParserSemanticError

        source = """
Set a / a1, a2 /;
Set i / 1*3 /;
Set j / 1*3 /;
Set aij(a,i,j);
Variable x(i,j);
x.lo(aij(a,i,j)) = 0;
"""
        with pytest.raises(ParserSemanticError, match=r"expect.*2.*indices.*provided 3"):
            parse_model_text(source)

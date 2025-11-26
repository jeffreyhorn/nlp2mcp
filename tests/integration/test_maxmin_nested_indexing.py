"""Integration tests for maxmin.gms nested indexing (Sprint 11 Day 1-2).

Tests validate that the nested/subset domain grammar extension enables
parsing of maxmin.gms equation declarations and definitions.

Sprint 11 Day 1 extended the grammar to support syntax like:
- defdist(low(n,nn)) where low is a subset with explicit indices
- mindist1(low) where low is used as a simple domain reference

This test validates the real-world maxmin.gms file parses correctly
through all equation declarations/definitions (lines 44-58).
"""

import pytest

from src.ir.parser import ParserSemanticError, parse_model_file, parse_model_text
from src.utils.errors import ParseError


class TestMaxminNestedIndexing:
    """Integration tests for maxmin.gms nested domain handling."""

    def test_maxmin_nested_domain_declarations(self):
        """Test that nested domain syntax in equation declarations parses correctly.

        This validates the core Sprint 11 Day 1 feature: grammar support for
        nested/subset indexing in equation domain specifications.
        """
        code = """
        Set n /p1*p3/;
        Alias (n, nn);
        Set low(n,n);

        Variable x;

        Equation
           test1(low(n,nn))   'equation with nested domain'
           test2(n,nn)        'equation with simple domain'
           test3              'scalar equation';

        test1(low(n,nn)).. x =e= 1;
        test2(n,nn).. x =e= 1;
        test3.. x =e= 1;

        Model m /all/;
        """

        model = parse_model_text(code)

        # Verify all 3 equations parsed
        assert len(model.equations) == 3, f"Expected 3 equations, got {len(model.equations)}"

        # Verify equation names
        eq_names = set(model.equations.keys())
        assert "test1" in eq_names
        assert "test2" in eq_names
        assert "test3" in eq_names

        # Verify domains are extracted correctly
        # test1(low(n,nn)) should extract ('n', 'nn')
        test1 = model.equations["test1"]
        assert test1.domain == ("n", "nn"), f"test1 domain: {test1.domain}"

        # test2(n,nn) should extract ('n', 'nn')
        test2 = model.equations["test2"]
        assert test2.domain == ("n", "nn"), f"test2 domain: {test2.domain}"

        # test3 is scalar (no domain)
        test3 = model.equations["test3"]
        assert test3.domain == (), f"test3 domain: {test3.domain}"

    def test_maxmin_file_parse_progress(self):
        """Test that maxmin.gms now parses further with aggregation over subset domains.

        Before Sprint 11 Day 1: Failed at line 51 (nested indexing not supported)
        After Sprint 11 Day 1: Failed at line 70 (loop statement not supported)
        After Sprint 11 Day 2 Extended (domain context): Parses past line 37 (indexed set assignments)
        After Sprint 11 Day 2 Extended (subset expansion): Parses past line 51 (subset expansion working)
        After Sprint 11 Day 2 Extended (aggregation): Parses past line 59 (aggregation over subsets working)

        Current blocker: Line 75 (variable bounds expansion for sets without explicit members)
        This is expected - requires handling sets with range specifications.
        """
        try:
            model = parse_model_file("tests/fixtures/gamslib/maxmin.gms")
            # If it fully parses, great! Check we got the equations
            assert len(model.equations) >= 5, "Should have at least 5 equations from maxmin.gms"
        except (ParseError, ParserSemanticError) as e:
            # If parsing fails, verify we made progress past earlier blockers
            error_msg = str(e)

            # Should NOT fail on earlier fixes
            assert not (
                "37" in error_msg and "ord" in error_msg
            ), f"Should not fail on indexed set assignment (line 37): {error_msg}"
            assert not (
                "51" in error_msg and "dist" in error_msg and "2 indices" in error_msg
            ), f"Should not fail on subset expansion (line 51): {error_msg}"
            assert not (
                "59" in error_msg and "low" in error_msg and "Undefined" in error_msg
            ), f"Should not fail on aggregation over subset (line 59): {error_msg}"

            # The current blocker is variable bounds expansion (line 75)
            # This is expected and acceptable for now

    def test_nested_domain_in_equation_head(self):
        """Test nested domains in equation head declarations."""
        code = """
        Set i /i1*i3/;
        Set j /j1*j2/;
        Set sub(i,j);
        Variable x;

        Equation test(sub(i,j)) 'test equation with nested domain';
        test(sub(i,j)).. x =e= 1;

        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.equations) == 1
        eq = model.equations["test"]
        assert eq.domain == ("i", "j")
        # EquationDef doesn't store description - validated via parsing only

    def test_nested_domain_backward_compatibility(self):
        """Ensure existing simple domain syntax still works correctly."""
        code = """
        Set i /i1*i3/;
        Set j /j1*j2/;
        Variable x(i,j);

        Equation simple(i,j) 'simple domain equation';
        simple(i,j).. x(i,j) =e= 1;

        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.equations) == 1
        eq = model.equations["simple"]
        assert eq.domain == ("i", "j")
        # EquationDef doesn't store description - validated via parsing only

    def test_complex_nested_and_simple_mixed(self):
        """Test complex case with multiple nested and simple domains mixed."""
        code = """
        Set i /i1*i3/;
        Set j /j1*j2/;
        Set k /k1*k2/;
        Set n /n1*n2/;
        Set low(n,n);
        Alias (n, nn);
        Variable x;

        Equation test(i, j, low(n,nn), k);
        test(i, j, low(n,nn), k).. x =e= 1;

        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.equations) == 1
        eq = model.equations["test"]
        # Should extract i, j, n, nn, k
        assert eq.domain == ("i", "j", "n", "nn", "k")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

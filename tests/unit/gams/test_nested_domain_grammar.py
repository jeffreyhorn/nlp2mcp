"""Unit tests for nested/subset domain grammar (Sprint 11 Day 1).

Tests the grammar extension that supports nested indexing like:
- Simple: supply(i)
- Nested: defdist(low(n,nn))
- Mixed: foo(i, low(n,nn), k)

Note: The grammar supports one level of nesting (subset with indices),
which is sufficient for maxmin.gms and similar models.
"""

import pytest

from src.ir.parser import parse_model_text


class TestNestedDomainGrammar:
    """Test nested/subset indexing in equation declarations and definitions."""

    def test_simple_nested_domain(self):
        """Test case 1: Simple nested domain defdist(subset(i,j))"""
        code = """
        Set i /i1*i3/;
        Set j /j1*j2/;
        Set subset(i,j);
        Variable x;
        Equation test(subset(i,j));
        test(subset(i,j)).. x =e= 1;
        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.equations) == 1
        eq = model.equations["test"]
        assert eq.name == "test"
        # Domain should extract 'i', 'j' from subset(i,j)
        assert eq.domain == ("i", "j")

    def test_mixed_simple_and_nested_domains(self):
        """Test case 2: Mixed simple and nested domains test(i,low(n,nn))"""
        code = """
        Set i /i1*i3/;
        Set n /n1*n2/;
        Set low(n,n);
        Alias (n, nn);
        Variable x;
        Equation test(i, low(n,nn));
        test(i, low(n,nn)).. x =e= 1;
        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.equations) == 1
        eq = model.equations[list(model.equations.keys())[0]]
        assert eq.name == "test"
        # Domain should extract 'i', 'n', 'nn' from i, low(n,nn)
        assert eq.domain == ("i", "n", "nn")

    def test_subset_with_single_index(self):
        """Test case 3: Subset with single index active(i)"""
        code = """
        Set i /i1*i3/;
        Set active(i);
        Variable x;
        Equation test(active(i));
        test(active(i)).. x =e= 1;
        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.equations) == 1
        eq = model.equations[list(model.equations.keys())[0]]
        assert eq.name == "test"
        # Domain should extract 'i' from active(i)
        assert eq.domain == ("i",)

    def test_subset_with_two_indices(self):
        """Test case 4: Subset with two indices low(n,nn)"""
        code = """
        Set n /p1*p3/;
        Set low(n,n);
        Alias (n, nn);
        Variable dist(n,n);
        Equation defdist(low(n,nn));
        defdist(low(n,nn)).. dist(n,nn) =e= 1;
        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.equations) == 1
        eq = model.equations[list(model.equations.keys())[0]]
        assert eq.name == "defdist"
        # Domain should extract 'n', 'nn' from low(n,nn)
        assert eq.domain == ("n", "nn")

    def test_multiple_nested_domains(self):
        """Test case 5: Multiple nested domains test(subset1(i,j), subset2(k,l))"""
        code = """
        Set i /i1*i3/;
        Set j /j1*j2/;
        Set k /k1*k2/;
        Set l /l1*l2/;
        Set subset1(i,j);
        Set subset2(k,l);
        Variable x;
        Equation test(subset1(i,j), subset2(k,l));
        test(subset1(i,j), subset2(k,l)).. x =e= 1;
        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.equations) == 1
        eq = model.equations[list(model.equations.keys())[0]]
        assert eq.name == "test"
        # Domain should extract 'i', 'j', 'k', 'l' from subset1(i,j), subset2(k,l)
        assert eq.domain == ("i", "j", "k", "l")

    def test_backward_compatibility_simple_domain(self):
        """Test backward compatibility: simple domains still work"""
        code = """
        Set i /i1*i3/;
        Variable x(i);
        Equation test(i);
        test(i).. x(i) =e= 1;
        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.equations) == 1
        eq = model.equations[list(model.equations.keys())[0]]
        assert eq.name == "test"
        assert eq.domain == ("i",)

    def test_backward_compatibility_multi_domain(self):
        """Test backward compatibility: multiple simple domains"""
        code = """
        Set i /i1*i3/;
        Set j /j1*j2/;
        Variable x(i,j);
        Equation test(i,j);
        test(i,j).. x(i,j) =e= 1;
        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.equations) == 1
        eq = model.equations[list(model.equations.keys())[0]]
        assert eq.name == "test"
        assert eq.domain == ("i", "j")

    def test_maxmin_defdist_equation(self):
        """Test real-world case from maxmin.gms: defdist(low(n,nn))"""
        code = """
        Set n /p1*p3/;
        Set low(n,n);
        Alias (n, nn);
        Variable dist(n,n);
        Equation defdist(low(n,nn));
        defdist(low(n,nn)).. dist(n,nn) =e= 1;
        Model test /all/;
        """
        model = parse_model_text(code)
        assert len(model.equations) == 1
        eq = model.equations[list(model.equations.keys())[0]]
        assert eq.name == "defdist"
        assert eq.domain == ("n", "nn")

    def test_nested_in_declaration_and_definition(self):
        """Test nested domain appears in both declaration and definition"""
        code = """
        Set n /p1*p3/;
        Set low(n,n);
        Alias (n, nn);
        Variable x;
        Equation test(low(n,nn));
        test(low(n,nn)).. x =e= 1;
        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.equations) == 1
        eq = model.equations[list(model.equations.keys())[0]]
        assert eq.name == "test"
        assert eq.domain == ("n", "nn")

    def test_complex_mixed_domains(self):
        """Test complex case with 3 simple + 1 nested domain"""
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
        eq = model.equations[list(model.equations.keys())[0]]
        assert eq.name == "test"
        # Domain should extract i, j, n, nn, k
        assert eq.domain == ("i", "j", "n", "nn", "k")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

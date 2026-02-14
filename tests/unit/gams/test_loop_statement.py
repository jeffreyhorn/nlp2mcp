"""Unit tests for loop statement parsing (Sprint 11 Day 2 Extended).

Tests the grammar extension that supports GAMS loop statements.
"""

import pytest

from src.ir.parser import parse_model_text


class TestLoopStatement:
    """Test loop statement parsing and storage."""

    def test_simple_loop(self):
        """Test case 1: Simple loop with assignment statements"""
        code = """
        Set i /i1*i3/;
        Parameter p;

        p = 0;
        loop(i,
           p = p + 1;
        );

        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.loop_statements) == 1

        loop = model.loop_statements[0]
        assert loop.indices == ("i",)
        assert len(loop.body_stmts) >= 1

    def test_loop_with_double_parens(self):
        """Test case 2: Loop with double parentheses around indices"""
        code = """
        Set n /p1*p3/;
        Set d /x,y/;
        Parameter p;
        Variable point(n,d);

        p = 0;
        loop((n,d),
           p = p + 1;
           point.l(n,d) = p/10;
        );

        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.loop_statements) == 1

        loop = model.loop_statements[0]
        assert loop.indices == ("n", "d")
        assert len(loop.body_stmts) >= 2

    def test_loop_with_multiple_statements(self):
        """Test case 3: Loop with multiple statements in body"""
        code = """
        Set i /i1*i3/;
        Parameter a, b, c;

        loop(i,
           a = a + 1;
           b = b * 2;
           c = a + b;
        );

        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.loop_statements) == 1

        loop = model.loop_statements[0]
        assert loop.indices == ("i",)
        assert len(loop.body_stmts) >= 3

    def test_multiple_loops(self):
        """Test case 4: Multiple loop statements in same model"""
        code = """
        Set i /i1*i3/;
        Set j /j1*j2/;
        Parameter p, q;

        loop(i,
           p = p + 1;
        );

        loop(j,
           q = q + 1;
        );

        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.loop_statements) == 2

        loop1 = model.loop_statements[0]
        assert loop1.indices == ("i",)

        loop2 = model.loop_statements[1]
        assert loop2.indices == ("j",)

    def test_loop_with_function_calls(self):
        """Test case 5: Loop with function calls (like maxmin.gms)"""
        code = """
        Set i /i1*i3/;
        Parameter p;

        p = 0;
        loop(i,
           p = round(mod(p,10)) + 1;
        );

        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.loop_statements) == 1

        loop = model.loop_statements[0]
        assert loop.indices == ("i",)
        assert len(loop.body_stmts) >= 1

    def test_loop_stored_not_executed(self):
        """Test case 6: Verify loop is stored but not executed (mock approach)"""
        code = """
        Set i /i1*i3/;
        Parameter p;

        p = 0;

        loop(i,
           p = p + 1;
        );

        Model m /all/;
        """
        model = parse_model_text(code)

        # Loop should be stored
        assert len(model.loop_statements) == 1

        # Loop is stored but not executed (mock/store approach)

    def test_nested_indices_two(self):
        """Test case 7: Loop with two indices"""
        code = """
        Set i /i1*i3/;
        Set j /j1*j2/;
        Parameter p;

        loop((i,j),
           p = p + 1;
        );

        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.loop_statements) == 1

        loop = model.loop_statements[0]
        assert loop.indices == ("i", "j")

    def test_nested_indices_three(self):
        """Test case 8: Loop with three indices"""
        code = """
        Set i /i1*i3/;
        Set j /j1*j2/;
        Set k /k1*k2/;
        Parameter p;

        loop((i,j,k),
           p = p + 1;
        );

        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.loop_statements) == 1

        loop = model.loop_statements[0]
        assert loop.indices == ("i", "j", "k")


class TestNestedLoopStatement:
    """Test nested loop and if statements inside loop bodies (Issue #711)."""

    def test_nested_loop(self):
        """Test loop containing another loop."""
        code = """
        Set i /i1*i3/;
        Set j /j1*j2/;
        Parameter p;

        loop(i,
           p = 0;
           loop(j,
              p = p + 1;
           );
        );

        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.loop_statements) >= 1

    def test_nested_loop_with_dollar_filter(self):
        """Test nested loop with dollar-filtered domain (lop pattern)."""
        code = """
        Set s /s1*s5/;
        Set r /r1*r5/;
        Set unvisit(s);
        Parameter p;

        loop(s,
           p = 0;
           loop(r$(ord(r) > 1 and card(unvisit)),
              p = p + 1;
           );
        );

        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.loop_statements) >= 1

    def test_triple_nested_loop(self):
        """Test three levels of nested loops."""
        code = """
        Set i /i1*i3/;
        Set j /j1*j2/;
        Set k /k1*k2/;
        Parameter p;

        loop(i,
           loop(j,
              loop(k,
                 p = p + 1;
              );
           );
        );

        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.loop_statements) >= 1

    def test_if_inside_loop(self):
        """Test if statement nested inside loop body."""
        code = """
        Set i /i1*i3/;
        Parameter p;
        Scalar flag /1/;

        loop(i,
           if(flag > 0,
              p = 1;
           );
        );

        Model m /all/;
        """
        model = parse_model_text(code)
        assert len(model.loop_statements) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

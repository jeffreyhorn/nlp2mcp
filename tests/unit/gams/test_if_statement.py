"""Unit tests for if statement parsing — final statement without semicolon.

Sprint 20 Day 7: The if_stmt grammar was changed to use exec_stmt* exec_stmt_final
(matching loop_body pattern), allowing the last statement before ) to omit its
trailing semicolon.  These tests verify that pattern for if, elseif, and else.
"""

import pytest

from src.ir.parser import parse_model_text

pytestmark = pytest.mark.unit


class TestIfStmtNoTrailingSemicolon:
    """Test if_stmt with final statement lacking a trailing semicolon."""

    def test_if_no_semicolon_before_close(self):
        """if(cond, x = 1) — no semicolon before closing paren."""
        source = """
        Parameter x;
        x = 0;
        if(1 > 0, x = 1);
        Variables obj;
        Equations defobj;
        defobj.. obj =e= x;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert len(ir.conditional_statements) == 1

    def test_if_with_semicolon_still_works(self):
        """if(cond, x = 1;) — semicolon before closing paren still works."""
        source = """
        Parameter x;
        x = 0;
        if(1 > 0, x = 1;);
        Variables obj;
        Equations defobj;
        defobj.. obj =e= x;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert len(ir.conditional_statements) == 1

    def test_elseif_no_semicolon(self):
        """elseif branch final statement without semicolon."""
        source = """
        Parameter x;
        x = 0;
        if(1 > 2, x = 1
        elseif 2 > 1, x = 2);
        Variables obj;
        Equations defobj;
        defobj.. obj =e= x;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert len(ir.conditional_statements) == 1

    def test_else_no_semicolon(self):
        """else branch final statement without semicolon."""
        source = """
        Parameter x;
        x = 0;
        if(1 > 2, x = 1
        else x = 3);
        Variables obj;
        Equations defobj;
        defobj.. obj =e= x;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert len(ir.conditional_statements) == 1

    def test_if_elseif_else_all_no_semicolons(self):
        """All branches omit trailing semicolons."""
        source = """
        Parameter x;
        x = 0;
        if(1 > 3, x = 1
        elseif 2 > 3, x = 2
        else x = 3);
        Variables obj;
        Equations defobj;
        defobj.. obj =e= x;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert len(ir.conditional_statements) == 1

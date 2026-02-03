"""Unit tests for Sprint 17 Day 7 grammar additions.

Tests for:
- Square bracket conditionals ($[cond] in addition to $(cond))
- Solve keyword variants (minimize/maximize without -ing suffix)
"""

from src.ir.parser import parse_model_text, parse_text


class TestSquareBracketConditionals:
    """Tests for $[condition] syntax support."""

    def test_assignment_with_square_bracket_conditional(self):
        """Parameter assignment with $[cond] syntax."""
        code = """
        Set i / 1*5 /;
        Parameter x(i);
        x(i)$[ord(i) > 2] = 1;
        """
        # Should parse without error
        parse_text(code)

    def test_equation_with_square_bracket_conditional(self):
        """Equation definition with $[cond] syntax."""
        code = """
        Set n / n1*n5 /;
        Variable x(n);
        Equation ldef(n);
        ldef(n)$[ord(n) > 1].. x(n) =e= 1;
        Model m / all /;
        """
        model = parse_model_text(code)
        assert "ldef" in model.equations

    def test_sum_with_square_bracket_conditional(self):
        """Sum expression with $[cond] in index spec - using parameter context."""
        code = """
        Set n / n1*n5 /;
        Alias (n, np);
        Parameter m(n), result(n);
        result(n) = sum(np$[ord(np) > ord(n)], m(np));
        """
        # Should parse without error - using parameter assignment context
        # where n is already in the domain
        parse_text(code)

    def test_prod_with_square_bracket_conditional(self):
        """Prod expression with $[cond] in index spec - using parameter context."""
        code = """
        Set i / 1*5 /;
        Alias (i, ip);
        Parameter a(i), result(i);
        result(i) = prod(ip$[ord(ip) > ord(i)], a(ip));
        """
        # Should parse without error
        parse_text(code)

    def test_expression_with_square_bracket_dollar_cond(self):
        """Expression with $[cond] inside."""
        code = """
        Set i / 1*5 /;
        Parameter x(i), y(i);
        Variable z;
        Equation def;
        def.. z =e= sum(i, x(i)$[y(i) > 0]);
        Model test / all /;
        """
        model = parse_model_text(code)
        assert "def" in model.equations

    def test_loop_with_square_bracket_filter(self):
        """Loop statement with $[cond] filter."""
        code = """
        Set i / 1*5 /;
        Parameter x(i);
        loop(i$[ord(i) > 2], x(i) = 1;);
        """
        parse_text(code)

    def test_abort_with_square_bracket_condition(self):
        """Abort statement with $[cond] syntax."""
        code = """
        Parameter x;
        x = 0.5;
        abort$[abs(x - 1) > 1e-8] 'Error in value';
        """
        parse_text(code)


class TestSolveKeywordVariants:
    """Tests for solve direction keyword variants."""

    def test_solve_with_maximize(self):
        """Solve with 'maximize' (without -ing)."""
        code = """
        Variable x, obj;
        Equation e;
        e.. obj =e= x;
        Model m / all /;
        solve m maximize obj using nlp;
        """
        model = parse_model_text(code)
        assert model.objective.objvar == "obj"

    def test_solve_with_minimize(self):
        """Solve with 'minimize' (without -ing)."""
        code = """
        Variable x, obj;
        Equation e;
        e.. obj =e= x;
        Model m / all /;
        solve m minimize obj using nlp;
        """
        model = parse_model_text(code)
        assert model.objective.objvar == "obj"

    def test_solve_with_maximizing(self):
        """Solve with 'maximizing' (standard form) still works."""
        code = """
        Variable x, obj;
        Equation e;
        e.. obj =e= x;
        Model m / all /;
        solve m maximizing obj using nlp;
        """
        model = parse_model_text(code)
        assert model.objective.objvar == "obj"

    def test_solve_with_minimizing(self):
        """Solve with 'minimizing' (standard form) still works."""
        code = """
        Variable x, obj;
        Equation e;
        e.. obj =e= x;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        model = parse_model_text(code)
        assert model.objective.objvar == "obj"

    def test_solve_using_lp_maximize(self):
        """Solve with 'using lp maximize' order."""
        code = """
        Variable x, obj;
        Equation e;
        e.. obj =e= x;
        Model m / all /;
        solve m using lp maximize obj;
        """
        model = parse_model_text(code)
        assert model.objective.objvar == "obj"

    def test_solve_using_nlp_minimize(self):
        """Solve with 'using nlp minimize' order."""
        code = """
        Variable x, obj;
        Equation e;
        e.. obj =e= x;
        Model m / all /;
        solve m using nlp minimize obj;
        """
        model = parse_model_text(code)
        assert model.objective.objvar == "obj"

    def test_solve_with_min_shorthand(self):
        """Solve with 'min' shorthand still works."""
        code = """
        Variable x, obj;
        Equation e;
        e.. obj =e= x;
        Model m / all /;
        solve m min obj using nlp;
        """
        model = parse_model_text(code)
        assert model.objective.objvar == "obj"

    def test_solve_with_max_shorthand(self):
        """Solve with 'max' shorthand still works."""
        code = """
        Variable x, obj;
        Equation e;
        e.. obj =e= x;
        Model m / all /;
        solve m max obj using nlp;
        """
        model = parse_model_text(code)
        assert model.objective.objvar == "obj"


class TestCombinedPatterns:
    """Tests combining multiple new features."""

    def test_equation_with_bracket_cond_and_solve_maximize(self):
        """Equation with $[cond] and solve with maximize."""
        code = """
        Set i / 1*5 /;
        Variable x(i), obj;
        Equation def, objdef(i);
        def.. obj =e= sum(i, x(i));
        objdef(i)$[ord(i) > 1].. x(i) =e= ord(i);
        Model m / all /;
        solve m maximize obj using nlp;
        """
        model = parse_model_text(code)
        assert "objdef" in model.equations
        assert model.objective.objvar == "obj"

"""Unit tests for model section declarations (Sprint 9 Day 5).

Tests cover:
- Model / all / syntax
- Model / eq1, eq2 / syntax with equation lists
- Model name; syntax (declaration only)
- Multi-model declarations (Model m1 / ... / m2 / ... /;)
"""

import pytest

from src.ir.parser import parse_model_text
from src.utils.errors import ParseError


class TestModelAll:
    """Test Model / all / syntax."""

    def test_model_all_basic(self):
        """Test basic Model / all / declaration."""
        source = """
Set i / 1*3 /;
Variable x(i);
Equation eq1(i);

eq1(i).. x(i) =e= 1;

Model mymodel / all /;
"""
        model = parse_model_text(source)
        assert model.declared_model == "mymodel"
        assert model.model_uses_all is True
        assert model.model_equations == []

    def test_model_all_case_insensitive(self):
        """Test Model / ALL / is case-insensitive."""
        source = """
Set i / 1*3 /;
Variable x(i);
Equation eq1(i);

eq1(i).. x(i) =e= 1;

Model mymodel / ALL /;
"""
        model = parse_model_text(source)
        assert model.declared_model == "mymodel"
        assert model.model_uses_all is True

    def test_models_keyword(self):
        """Test Models (plural) keyword works."""
        source = """
Set i / 1*3 /;
Variable x(i);
Equation eq1(i);

eq1(i).. x(i) =e= 1;

Models mymodel / all /;
"""
        model = parse_model_text(source)
        assert model.declared_model == "mymodel"
        assert model.model_uses_all is True


class TestModelWithList:
    """Test Model / eq1, eq2 / syntax with equation lists."""

    def test_model_single_equation(self):
        """Test model with single equation."""
        source = """
Set i / 1*3 /;
Variable x(i);
Equation eq1;

eq1.. x('1') =e= 1;

Model mymodel / eq1 /;
"""
        model = parse_model_text(source)
        assert model.declared_model == "mymodel"
        assert model.model_uses_all is False
        assert model.model_equations == ["eq1"]

    def test_model_multiple_equations(self):
        """Test model with multiple equations."""
        source = """
Set i / 1*3 /;
Variable x(i);
Variable obj;
Equation eq1, eq2, objdef;

eq1.. x('1') =e= 1;
eq2.. x('2') =e= 2;
objdef.. obj =e= sum(i, x(i));

Model mymodel / eq1, eq2, objdef /;
"""
        model = parse_model_text(source)
        assert model.declared_model == "mymodel"
        assert model.model_uses_all is False
        assert model.model_equations == ["eq1", "eq2", "objdef"]

    def test_model_equations_not_all_defined(self):
        """Test model can reference equations that are declared but not defined yet."""
        source = """
Set i / 1*3 /;
Variable x(i);
Equation eq1, eq2, eq3;

eq1.. x('1') =e= 1;
eq2.. x('2') =e= 2;

Model mymodel / eq1, eq2, eq3 /;

eq3.. x('3') =e= 3;
"""
        model = parse_model_text(source)
        assert model.declared_model == "mymodel"
        assert model.model_equations == ["eq1", "eq2", "eq3"]

    def test_model_whitespace_separated_equations(self):
        """Test model with whitespace-separated equation list (Issue #710).

        GAMS allows equation names in model lists to be separated by
        whitespace (newlines) without commas.
        """
        source = """
Set i / 1*3 /;
Variable x(i);
Variable obj;
Equation eq1, eq2, eq3, objdef;

eq1.. x('1') =e= 1;
eq2.. x('2') =e= 2;
eq3.. x('3') =e= 3;
objdef.. obj =e= sum(i, x(i));

Model mymodel / eq1, eq2
                eq3
                objdef /;
"""
        model = parse_model_text(source)
        assert model.declared_model == "mymodel"
        assert model.model_uses_all is False
        assert model.model_equations == ["eq1", "eq2", "eq3", "objdef"]


class TestModelDeclaration:
    """Test Model name; syntax (declaration only)."""

    def test_model_declaration_only(self):
        """Test model declaration without equations."""
        source = """
Set i / 1*3 /;
Variable x(i);
Equation eq1(i);

eq1(i).. x(i) =e= 1;

Model mymodel;
"""
        model = parse_model_text(source)
        assert model.declared_model == "mymodel"
        assert model.model_uses_all is False
        assert model.model_equations == []

    def test_model_declaration_before_equations(self):
        """Test model declaration can come before equation definitions."""
        source = """
Set i / 1*3 /;
Variable x(i);
Equation eq1(i);

Model mymodel;

eq1(i).. x(i) =e= 1;
"""
        model = parse_model_text(source)
        assert model.declared_model == "mymodel"


class TestMultiModelDeclaration:
    """Test multi-model declarations (Sprint 9 Day 5 feature)."""

    def test_multi_model_basic(self):
        """Test basic multi-model declaration (hs62.gms pattern)."""
        source = """
Set i / 1*3 /;
Variable x(i);
Variable obj;
Equation eq1, eq2, objdef;

objdef.. obj =e= sum(i, x(i));
eq1.. x('1') =e= 1;
eq2.. x('2') =e= 2;

Model
   m  / objdef, eq1  /
   mx / objdef, eq2 /;
"""
        model = parse_model_text(source)
        # Only first model is stored in IR (current limitation)
        assert model.declared_model == "m"
        assert model.model_uses_all is False
        assert model.model_equations == ["objdef", "eq1"]

    def test_multi_model_with_all(self):
        """Test multi-model with one using / all /."""
        source = """
Set i / 1*3 /;
Variable x(i);
Variable obj;
Equation eq1, eq2, objdef;

objdef.. obj =e= sum(i, x(i));
eq1.. x('1') =e= 1;
eq2.. x('2') =e= 2;

Model
   m  / all /
   mx / objdef, eq2 /;
"""
        model = parse_model_text(source)
        assert model.declared_model == "m"
        assert model.model_uses_all is True
        assert model.model_equations == []

    def test_multi_model_three_models(self):
        """Test multi-model declaration with three models."""
        source = """
Set i / 1*3 /;
Variable x(i);
Variable obj;
Equation eq1, eq2, eq3, objdef;

objdef.. obj =e= sum(i, x(i));
eq1.. x('1') =e= 1;
eq2.. x('2') =e= 2;
eq3.. x('3') =e= 3;

Model
   m1 / objdef, eq1 /
   m2 / objdef, eq2 /
   m3 / objdef, eq3 /;
"""
        model = parse_model_text(source)
        # Only first model is stored
        assert model.declared_model == "m1"
        assert model.model_equations == ["objdef", "eq1"]


class TestModelWithSolve:
    """Test model declarations with solve statements."""

    def test_model_and_solve(self):
        """Test model declaration followed by solve."""
        source = """
Set i / 1*3 /;
Variable x(i);
Variable obj;
Equation eq1, objdef;

eq1.. x('1') =e= 1;
objdef.. obj =e= sum(i, x(i));

Model mymodel / all /;

Solve mymodel using nlp min obj;
"""
        model = parse_model_text(source)
        assert model.declared_model == "mymodel"
        assert model.model_name == "mymodel"  # Set by solve statement
        assert model.objective is not None
        assert model.objective.objvar == "obj"

    def test_solve_references_multi_model(self):
        """Test solve can reference model from multi-model declaration."""
        source = """
Set i / 1*3 /;
Variable x(i);
Variable obj;
Equation eq1, eq2, objdef;

objdef.. obj =e= sum(i, x(i));
eq1.. x('1') =e= 1;
eq2.. x('2') =e= 2;

Model
   m  / objdef, eq1  /
   mx / objdef, eq2 /;

Solve m using nlp min obj;
"""
        model = parse_model_text(source)
        assert model.declared_model == "m"
        assert model.model_name == "m"


class TestModelEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_equation_list(self):
        """Test model with empty equation list."""
        source = """
Set i / 1*3 /;
Variable x(i);

Model mymodel / /;
"""
        # This should fail to parse - empty equation list is invalid
        with pytest.raises(ParseError):
            parse_model_text(source)

    def test_model_name_can_differ_from_solve(self):
        """Test declared model name can differ from solve statement."""
        source = """
Set i / 1*3 /;
Variable x(i);
Variable obj;
Equation eq1, objdef;

eq1.. x('1') =e= 1;
objdef.. obj =e= sum(i, x(i));

Model declared_name / all /;

Solve different_name using nlp min obj;
"""
        model = parse_model_text(source)
        # declared_model comes from Model statement
        assert model.declared_model == "declared_name"
        # model_name comes from Solve statement
        assert model.model_name == "different_name"

    def test_multiple_model_statements(self):
        """Test multiple separate Model statements (not multi-model)."""
        source = """
Set i / 1*3 /;
Variable x(i);
Variable obj;
Equation eq1, eq2, objdef;

objdef.. obj =e= sum(i, x(i));
eq1.. x('1') =e= 1;
eq2.. x('2') =e= 2;

Model m1 / eq1 /;
Model m2 / eq2 /;
"""
        model = parse_model_text(source)
        # declared_model property returns the first model name
        assert model.declared_model == "m1"
        # Issue #729: all model names are tracked
        assert "m1" in model.declared_models
        assert "m2" in model.declared_models


class TestModelCaseSensitivity:
    """Test case sensitivity in model declarations."""

    def test_model_keyword_case_insensitive(self):
        """Test Model/model/MODEL keywords are case-insensitive."""
        for keyword in ["Model", "model", "MODEL", "MoDeL"]:
            source = f"""
Set i / 1*3 /;
Variable x(i);
Equation eq1(i);

eq1(i).. x(i) =e= 1;

{keyword} mymodel / all /;
"""
            model = parse_model_text(source)
            assert model.declared_model == "mymodel"

    def test_all_keyword_case_insensitive(self):
        """Test all/ALL/All keywords are case-insensitive."""
        for all_kw in ["all", "ALL", "All", "aLl"]:
            source = f"""
Set i / 1*3 /;
Variable x(i);
Equation eq1(i);

eq1(i).. x(i) =e= 1;

Model mymodel / {all_kw} /;
"""
            model = parse_model_text(source)
            assert model.model_uses_all is True

    def test_model_name_case_insensitive(self):
        """Test model names are case-insensitive (Issue #729, consistent with GAMS)."""
        source = """
Set i / 1*3 /;
Variable x(i);
Equation eq1(i);

eq1(i).. x(i) =e= 1;

Model MyModel / all /;
"""
        model = parse_model_text(source)
        assert model.declared_model == "mymodel"
        # Model names stored lowercase (GAMS is case-insensitive)
        assert "mymodel" in model.declared_models


class TestMultiModelAttributeAccess:
    """Issue #729: attribute assignments on non-first models must not error."""

    def test_attr_on_second_model(self):
        """ilp.optCr = 0 must parse when ilp is not the first Model."""
        gams = """
Set i / a, b /;
Variable x(i);
Variable obj;
Equation eq1(i);
Equation eq2(i);
Equation objdef;
objdef.. obj =e= sum(i, x(i));
eq1(i).. x(i) =g= 0;
eq2(i).. x(i) =l= 10;

Model sp / eq1 /;
Model ilp / eq2 /;

ilp.optCr  = 0;
ilp.resLim = 100;
"""
        model = parse_model_text(source=gams)
        assert "sp" in model.declared_models
        assert "ilp" in model.declared_models

    def test_attr_case_insensitive_model(self):
        """Model declared as ILP, accessed as ilp."""
        gams = """
Set i / a, b /;
Variable x(i);
Variable obj;
Equation eq1(i);
Equation objdef;
objdef.. obj =e= sum(i, x(i));
eq1(i).. x(i) =g= 0;

Model sp / eq1 /;
Model ILP / objdef /;

ilp.optCr = 0;
"""
        model = parse_model_text(source=gams)
        assert "ilp" in model.declared_models

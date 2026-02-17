"""Tests for mixed-case variable name handling in AD differentiation.

Issue #672: CaseInsensitiveDict.keys() returns lowercase, but VarRef nodes previously
stored original-case names from GAMS source. This caused _diff_varref() to return
Const(0.0) for mixed-case variables because the case-sensitive comparison failed.

Fix: VarRef names are normalized to lowercase at parse time in src/ir/parser.py.
These tests verify that differentiation works correctly for mixed-case variable names.
"""

import pytest

from src.ad import evaluate
from src.ad.derivative_rules import differentiate_expr
from src.ir.ast import Binary, Const, VarRef

pytestmark = pytest.mark.unit


def _eval(expr) -> float:
    """Evaluate a constant expression (no free variables) to a float."""
    return evaluate(expr, {})


class TestMixedCaseDifferentiation:
    """Test that AD correctly handles mixed-case variable names after normalization."""

    def test_lowercase_varref_differentiates_correctly(self):
        """d/dx(x) = 1 when VarRef name is lowercase (baseline)."""
        expr = VarRef("x")
        result = differentiate_expr(expr, "x")
        assert isinstance(result, Const)
        assert result.value == 1.0

    def test_lowercase_varref_wrong_var_is_zero(self):
        """d/dx(y) = 0 when names differ."""
        expr = VarRef("y")
        result = differentiate_expr(expr, "x")
        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_mixed_case_varref_after_normalization(self):
        """VarRef with lowercased name matches lowercase wrt_var correctly.

        After the Issue #672 fix, parser produces lowercase VarRef names.
        VarRef('acidfeed') differentiates w.r.t. 'acidfeed' should give 1.
        """
        expr = VarRef("acidfeed")
        result = differentiate_expr(expr, "acidfeed")
        assert isinstance(result, Const)
        assert result.value == 1.0

    def test_uppercase_source_name_mismatch_documents_bug(self):
        """Documents the pre-fix broken behavior that motivated the parser fix.

        If a VarRef('AcidFeed') is compared to 'acidfeed' (CaseInsensitiveDict key),
        the case-sensitive comparison returns 0 -- the bug this fix addresses.
        """
        expr = VarRef("AcidFeed")  # old behavior: mixed case preserved
        result = differentiate_expr(expr, "acidfeed")  # lowercase key from CaseInsensitiveDict
        # This IS the old broken behavior: returns 0 due to case mismatch.
        # Documents WHY the parser-level fix is necessary.
        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_product_rule_with_lowercase_vars(self):
        """d/dx(x * y) is non-zero when both vars are lowercase (post-fix behavior)."""
        x = VarRef("x")
        y = VarRef("y")
        expr = Binary("*", x, y)
        result = differentiate_expr(expr, "x")
        # The result may be a VarRef(y) or unsimplified form -- just not zero
        assert not (isinstance(result, Const) and result.value == 0.0)

    def test_sum_of_lowercase_vars(self):
        """d/dx(x + y) = 1 when x and y are lowercase VarRefs."""
        x = VarRef("x")
        y = VarRef("y")
        expr = Binary("+", x, y)
        result = differentiate_expr(expr, "x")
        # May return Binary(+, Const(1.0), Const(0.0)) -- evaluate it
        assert _eval(result) == 1.0

    def test_indexed_lowercase_varref_matches(self):
        """d/dx(i)(x(i)) = 1 with lowercase name and matching index."""
        expr = VarRef("x", ("i",))
        result = differentiate_expr(expr, "x", ("i",))
        assert isinstance(result, Const)
        assert result.value == 1.0

    def test_indexed_lowercase_varref_no_match_different_index(self):
        """d/dx(j)(x(i)) = 0 -- different index, should be zero."""
        expr = VarRef("x", ("i",))
        result = differentiate_expr(expr, "x", ("j",))
        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_bearing_style_variable_names(self):
        """Variables like 'load' and 'ecc' (bearing model) differentiate correctly."""
        load = VarRef("load")
        ecc = VarRef("ecc")
        expr = Binary("*", load, ecc)
        d_load = differentiate_expr(expr, "load")
        d_ecc = differentiate_expr(expr, "ecc")
        # Results should be non-zero (the other variable)
        assert not (isinstance(d_load, Const) and d_load.value == 0.0)
        assert not (isinstance(d_ecc, Const) and d_ecc.value == 0.0)

    def test_alkyl_style_variable_names(self):
        """Variables like 'AcidFeed' normalized to 'acidfeed' differentiate correctly."""
        # Post-fix: parser produces 'acidfeed' not 'AcidFeed'
        acidfeed = VarRef("acidfeed")
        expr = Binary("+", acidfeed, Const(1.0))
        result = differentiate_expr(expr, "acidfeed")
        # May return Binary(+, Const(1.0), Const(0.0)) -- evaluate it
        assert _eval(result) == 1.0


class TestParserVarRefNormalization:
    """Integration tests verifying the parser produces lowercase VarRef names."""

    def test_mixed_case_variable_produces_lowercase_varref(self):
        """Parse a model with mixed-case variable name -- VarRef should be lowercase."""
        from src.ir.parser import parse_model_text

        source = """
Variable AcidFeed, obj;
Equation eq1;
eq1.. obj =e= AcidFeed * 2;
Model m / all /;
Solve m using nlp minimizing obj;
"""
        model = parse_model_text(source)
        eq = model.equations["eq1"]
        lhs, rhs = eq.lhs_rhs
        for expr in (lhs, rhs):
            for name in _collect_varref_names(expr):
                assert name == name.lower(), f"VarRef name '{name}' is not lowercase"

    def test_lowercase_variable_stays_lowercase(self):
        """Parse a model with all-lowercase variable names -- VarRef should be lowercase."""
        from src.ir.parser import parse_model_text

        source = """
Variable x, obj;
Equation eq1;
eq1.. obj =e= x * 3;
Model m / all /;
Solve m using nlp minimizing obj;
"""
        model = parse_model_text(source)
        eq = model.equations["eq1"]
        lhs, rhs = eq.lhs_rhs
        for expr in (lhs, rhs):
            for name in _collect_varref_names(expr):
                assert name == name.lower(), f"VarRef name '{name}' is not lowercase"

    def test_uppercase_variable_normalized_to_lowercase(self):
        """Parse a model with ALL-CAPS variable -- VarRef should be lowercase."""
        from src.ir.parser import parse_model_text

        source = """
Variable BIGVAR, obj;
Equation eq1;
eq1.. obj =e= BIGVAR + 1;
Model m / all /;
Solve m using nlp minimizing obj;
"""
        model = parse_model_text(source)
        eq = model.equations["eq1"]
        lhs, rhs = eq.lhs_rhs
        for expr in (lhs, rhs):
            for name in _collect_varref_names(expr):
                assert name == name.lower(), f"VarRef name '{name}' is not lowercase"


def _collect_varref_names(expr) -> list[str]:
    """Recursively collect all VarRef names from an expression tree."""
    names = []
    if isinstance(expr, VarRef):
        names.append(expr.name)
    for child in expr.children():
        names.extend(_collect_varref_names(child))
    return names

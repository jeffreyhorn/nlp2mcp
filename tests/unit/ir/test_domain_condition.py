"""Tests for domain condition extraction from nested equation domains.

Issue #1112: When an equation is defined with a restricted domain like
`eq(low(n,nn))..`, the parser extracts `low(n,nn)` as a SetMembershipTest
condition on the equation so the emitter can generate a `$(low(n,nn))` guard.
The condition cannot be evaluated at compile time by condition_eval, but
enumerate_equation_instances() handles this gracefully (warns once per equation,
includes all instances).
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.ir.ast import SetMembershipTest, SymbolRef
from src.ir.condition_eval import ConditionEvaluationError, evaluate_condition
from src.ir.parser import parse_model_text
from src.ir.symbols import AliasDef, SetDef


@pytest.mark.unit
class TestDomainConditionExtraction:
    """Test that nested domain elements generate equation conditions."""

    def test_nested_domain_creates_condition(self):
        """eq(low(n,nn)).. creates a SetMembershipTest condition on 'low(n,nn)'."""
        gams = """
Set n / a, b, c /;
Set low(n,n);
Alias(n, nn);
low(n,nn) = ord(n) > ord(nn);
Variable x;
Equation eq1(n,nn);
eq1(low(n,nn)).. x =e= 0;
Solve dummy using NLP minimizing x;
"""
        ir = parse_model_text(gams)
        eq = ir.equations.get("eq1")
        assert eq is not None
        assert eq.domain == ("n", "nn")
        assert eq.condition is not None
        assert "SetMembershipTest" in repr(eq.condition)
        assert "low" in repr(eq.condition)

    def test_simple_domain_no_condition(self):
        """eq(i,j).. does NOT create a condition."""
        gams = """
Set i / a, b /;
Set j / x, y /;
Variable z;
Equation eq1(i,j);
eq1(i,j).. z =e= 0;
Solve dummy using NLP minimizing z;
"""
        ir = parse_model_text(gams)
        eq = ir.equations.get("eq1")
        assert eq is not None
        assert eq.domain == ("i", "j")
        assert eq.condition is None

    def test_nested_domain_with_explicit_condition(self):
        """eq(low(n,nn))$active(n).. combines SetMembershipTest and explicit condition."""
        gams = """
Set n / a, b, c /;
Set low(n,n);
Set active(n) / a, b /;
Alias(n, nn);
low(n,nn) = ord(n) > ord(nn);
Parameter p(n);
Variable x;
Equation eq1(n,nn);
eq1(low(n,nn))$(active(n)).. x =e= 0;
Solve dummy using NLP minimizing x;
"""
        ir = parse_model_text(gams)
        eq = ir.equations.get("eq1")
        assert eq is not None
        assert eq.condition is not None
        # Should be Binary("and", SetMembershipTest("low", ...), ...)
        assert "low" in repr(eq.condition)
        assert "active" in repr(eq.condition)


def _make_model_ir(sets=None, aliases=None):
    """Create a minimal mock ModelIR for condition evaluation tests."""
    ir = MagicMock()
    ir.sets = sets or {}
    ir.aliases = aliases or {}
    ir.parameters = {}
    return ir


@pytest.mark.unit
class TestSetMembershipTestEvaluation:
    """Test evaluate_condition() with SetMembershipTest expressions."""

    def test_member_found_returns_true(self):
        """Element that is in the set returns True."""
        model_ir = _make_model_ir(sets={"cf": SetDef(name="cf", members=["coal", "gas", "oil"])})
        cond = SetMembershipTest(set_name="cf", indices=(SymbolRef("c"),))
        result = evaluate_condition(
            cond, domain_sets=("c",), index_values=("coal",), model_ir=model_ir
        )
        assert result is True

    def test_member_not_found_returns_false(self):
        """Element not in the set returns False."""
        model_ir = _make_model_ir(sets={"cf": SetDef(name="cf", members=["coal", "gas", "oil"])})
        cond = SetMembershipTest(set_name="cf", indices=(SymbolRef("c"),))
        result = evaluate_condition(
            cond, domain_sets=("c",), index_values=("nuclear",), model_ir=model_ir
        )
        assert result is False

    def test_alias_resolved_to_target_set(self):
        """SetMembershipTest on an alias resolves to the target set."""
        model_ir = _make_model_ir(
            sets={"t": SetDef(name="t", members=["1990", "1995", "2000"])},
            aliases={"tt": AliasDef(name="tt", target="t")},
        )
        cond = SetMembershipTest(set_name="tt", indices=(SymbolRef("i"),))
        result = evaluate_condition(
            cond, domain_sets=("i",), index_values=("1995",), model_ir=model_ir
        )
        assert result is True

    def test_dynamic_subset_raises_error(self):
        """Set with domain but no members raises ConditionEvaluationError."""
        model_ir = _make_model_ir(sets={"low": SetDef(name="low", members=[], domain=("n",))})
        cond = SetMembershipTest(set_name="low", indices=(SymbolRef("n"),))
        with pytest.raises(ConditionEvaluationError, match="cannot be evaluated"):
            evaluate_condition(cond, domain_sets=("n",), index_values=("a",), model_ir=model_ir)

    def test_empty_set_no_domain_returns_false(self):
        """Genuinely empty set (no domain) returns False."""
        model_ir = _make_model_ir(sets={"empty": SetDef(name="empty", members=[])})
        cond = SetMembershipTest(set_name="empty", indices=(SymbolRef("i"),))
        result = evaluate_condition(
            cond, domain_sets=("i",), index_values=("x",), model_ir=model_ir
        )
        assert result is False

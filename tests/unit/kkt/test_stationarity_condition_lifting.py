"""Tests for existential lifting in _find_variable_access_condition().

Issue #1005: When a stationarity equation condition contains free indices
not in the variable's domain, they should be lifted into an existential
check sum(extra, 1$cond) instead of being rejected.
"""

from __future__ import annotations

import pytest

from src.ir.ast import (
    Const,
    DollarConditional,
    ParamRef,
    Sum,
    VarRef,
)
from src.ir.model_ir import ModelIR
from src.ir.symbols import EquationDef, Rel, SetDef, VariableDef
from src.kkt.stationarity import _find_variable_access_condition
from src.utils.case_insensitive_dict import CaseInsensitiveDict


def _make_model_ir(sets, equations, variables, params=None, aliases=None):
    """Create a minimal ModelIR for testing."""
    s = CaseInsensitiveDict()
    for name, sd in sets.items():
        s[name] = sd
    e = CaseInsensitiveDict()
    for name, ed in equations.items():
        e[name] = ed
    v = CaseInsensitiveDict()
    for name, vd in variables.items():
        v[name] = vd
    p = CaseInsensitiveDict()
    if params:
        for name, pd in params.items():
            p[name] = pd
    a = CaseInsensitiveDict()
    if aliases:
        for name, ad in aliases.items():
            a[name] = ad
    return ModelIR(sets=s, equations=e, variables=v, params=p, aliases=a)


@pytest.mark.unit
class TestAccessConditionLifting:
    """Tests for existential lifting of uncontrolled indices in conditions."""

    def test_paramref_condition_with_extra_index_is_lifted(self):
        """Issue #1005: ParamRef condition ts(t,tf) with extra index t is
        lifted to sum(t, 1$ts(t,tf)) when variable domain is (m, tf)."""
        from src.ir.symbols import ParameterDef

        model_ir = _make_model_ir(
            sets={
                "m": SetDef(name="m", members=["m1"]),
                "tf": SetDef(name="tf", members=["1980", "1985"]),
                "t": SetDef(name="t", members=["1980"], domain=("tf",)),
            },
            params={
                "ts": ParameterDef(name="ts", domain=("tf", "tf")),
            },
            variables={
                "h": VariableDef(name="h", domain=("m", "tf")),
            },
            equations={
                # cpu(m,t).. sum(p, ...) =l= sum(tf$ts(t,tf), h(m,tf))
                "cpu": EquationDef(
                    name="cpu",
                    domain=("m", "t"),
                    relation=Rel.LE,
                    lhs_rhs=(
                        Const(0),
                        Sum(
                            index_sets=("tf",),
                            condition=ParamRef("ts", ("t", "tf")),
                            body=VarRef("h", ("m", "tf")),
                        ),
                    ),
                ),
            },
        )

        result = _find_variable_access_condition("h", ("m", "tf"), model_ir)

        # Should be lifted: sum(t, 1$ts(t,tf))
        assert result is not None
        assert isinstance(result, Sum)
        assert result.index_sets == ("t",)
        assert isinstance(result.body, DollarConditional)
        assert isinstance(result.body.condition, ParamRef)
        assert result.body.condition.name == "ts"

    def test_condition_within_domain_not_lifted(self):
        """Condition whose free indices are all within domain should pass
        through unchanged (no Sum wrapping)."""
        from src.ir.symbols import ParameterDef

        model_ir = _make_model_ir(
            sets={
                "m": SetDef(name="m", members=["m1"]),
                "tf": SetDef(name="tf", members=["1980", "1985"]),
            },
            params={
                "active": ParameterDef(name="active", domain=("tf",)),
            },
            variables={
                "h": VariableDef(name="h", domain=("m", "tf")),
            },
            equations={
                "eq1": EquationDef(
                    name="eq1",
                    domain=("m", "tf"),
                    relation=Rel.EQ,
                    lhs_rhs=(
                        Const(0),
                        Sum(
                            index_sets=("tf",),
                            condition=ParamRef("active", ("tf",)),
                            body=VarRef("h", ("m", "tf")),
                        ),
                    ),
                ),
            },
        )

        result = _find_variable_access_condition("h", ("m", "tf"), model_ir)

        # active(tf) has no extra indices — should NOT be wrapped in Sum
        assert result is not None
        assert isinstance(result, ParamRef)
        assert result.name == "active"

    def test_case_insensitive_domain_matching(self):
        """Extra index detection should be case-insensitive: domain ('M','TF')
        should match free indices {'m','tf'} without false positives."""
        from src.ir.symbols import ParameterDef

        model_ir = _make_model_ir(
            sets={
                "M": SetDef(name="M", members=["m1"]),
                "TF": SetDef(name="TF", members=["1980", "1985"]),
            },
            params={
                "active": ParameterDef(name="active", domain=("TF",)),
            },
            variables={
                "h": VariableDef(name="h", domain=("M", "TF")),
            },
            equations={
                "eq1": EquationDef(
                    name="eq1",
                    domain=("M", "TF"),
                    relation=Rel.EQ,
                    lhs_rhs=(
                        Const(0),
                        Sum(
                            index_sets=("TF",),
                            condition=ParamRef("active", ("TF",)),
                            body=VarRef("h", ("M", "TF")),
                        ),
                    ),
                ),
            },
        )

        result = _find_variable_access_condition("h", ("M", "TF"), model_ir)

        # free_indices returns lowercase, domain is uppercase — should still match
        assert result is not None
        assert isinstance(result, ParamRef)
        assert result.name == "active"

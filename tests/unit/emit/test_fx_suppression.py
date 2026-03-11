"""Unit tests for _fx_ equation suppression in emit_gams_mcp().

When a variable has a conditioned stationarity equation AND per-element
_fx_ equations (from fx_map), the _fx_ equations for indices outside the
active domain must be suppressed to avoid GAMS "unmatched equation" errors.
"""

import pytest

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.emit.emit_gams import _compute_suppressed_fx_equations, _fx_eq_name, emit_gams_mcp
from src.ir.ast import Binary, SetMembershipTest, SymbolRef
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import ObjSense, SetDef, VariableDef, VarKind
from src.kkt.kkt_system import KKTSystem, MultiplierDef


def _make_kkt(model, vars_list, manual_index_mapping):
    """Helper to build a minimal KKTSystem for testing."""
    index_mapping = manual_index_mapping(vars_list)
    n = len(vars_list)
    gradient = GradientVector(num_cols=n, index_mapping=index_mapping)
    J_eq = JacobianStructure(num_rows=0, num_cols=n, index_mapping=index_mapping)
    J_ineq = JacobianStructure(num_rows=0, num_cols=n, index_mapping=index_mapping)
    return KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)


@pytest.mark.unit
class TestFxEqName:
    """Tests for _fx_eq_name helper."""

    def test_scalar(self):
        assert _fx_eq_name("a", ()) == "a_fx"

    def test_single_index(self):
        assert _fx_eq_name("a", ("0",)) == "a_fx_0"

    def test_multi_index(self):
        assert _fx_eq_name("x", ("r1", "c1")) == "x_fx_r1_c1"

    def test_special_char_index(self):
        """Indices with special characters get sanitized + hash suffix."""
        name = _fx_eq_name("a", ("q-1",))
        assert name.startswith("a_fx_q_1_")
        assert len(name) > len("a_fx_q_1_")  # has hash suffix


@pytest.mark.unit
class TestComputeSuppressedFxEquations:
    """Tests for _compute_suppressed_fx_equations."""

    def test_basic_suppression(self, manual_index_mapping):
        """fx_map entry outside stationarity condition is suppressed."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)

        # tl = {0, 1, 2}, t(tl) = {1, 2} — "0" is outside t
        model.sets["tl"] = SetDef(name="tl", members=["0", "1", "2"])
        model.sets["t"] = SetDef(name="t", members=["1", "2"])

        a = VariableDef(name="a", domain=("tl",), kind=VarKind.CONTINUOUS)
        a.fx_map[("0",)] = 1000.0  # a.fx("0") = 1000 — "0" not in t
        model.variables["a"] = a

        kkt = _make_kkt(model, [("obj", ()), ("a", ("0",)), ("a", ("1",))], manual_index_mapping)
        kkt.stationarity_conditions["a"] = SetMembershipTest("t", (SymbolRef("tl"),))

        suppressed = _compute_suppressed_fx_equations(kkt)
        assert suppressed == {"a_fx_0"}

    def test_no_suppression_when_index_is_active(self, manual_index_mapping):
        """fx_map entry within stationarity condition is NOT suppressed."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)

        model.sets["tl"] = SetDef(name="tl", members=["0", "1", "2"])
        model.sets["t"] = SetDef(name="t", members=["0", "1", "2"])

        a = VariableDef(name="a", domain=("tl",), kind=VarKind.CONTINUOUS)
        a.fx_map[("0",)] = 1000.0  # "0" IS in t
        model.variables["a"] = a

        kkt = _make_kkt(model, [("obj", ()), ("a", ("0",))], manual_index_mapping)
        kkt.stationarity_conditions["a"] = SetMembershipTest("t", (SymbolRef("tl"),))

        suppressed = _compute_suppressed_fx_equations(kkt)
        assert suppressed == set()

    def test_no_suppression_without_stationarity_condition(self, manual_index_mapping):
        """fx_map with no stationarity condition produces no suppression."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)

        model.sets["i"] = SetDef(name="i", members=["a", "b"])

        x = VariableDef(name="x", domain=("i",), kind=VarKind.CONTINUOUS)
        x.fx_map[("a",)] = 5.0
        model.variables["x"] = x

        kkt = _make_kkt(model, [("obj", ()), ("x", ("a",))], manual_index_mapping)
        # No stationarity_conditions set

        suppressed = _compute_suppressed_fx_equations(kkt)
        assert suppressed == set()

    def test_multiple_vars_suppressed(self, manual_index_mapping):
        """Multiple variables with inactive fx_map entries are all suppressed."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)

        model.sets["tl"] = SetDef(name="tl", members=["0", "1", "2", "3"])
        model.sets["t"] = SetDef(name="t", members=["1", "2", "3"])

        a = VariableDef(name="a", domain=("tl",), kind=VarKind.CONTINUOUS)
        a.fx_map[("0",)] = 1000.0
        model.variables["a"] = a

        m = VariableDef(name="m", domain=("tl",), kind=VarKind.CONTINUOUS)
        m.fx_map[("0",)] = 100.0
        model.variables["m"] = m

        kkt = _make_kkt(
            model,
            [("obj", ()), ("a", ("0",)), ("a", ("1",)), ("m", ("0",)), ("m", ("1",))],
            manual_index_mapping,
        )
        kkt.stationarity_conditions["a"] = SetMembershipTest("t", (SymbolRef("tl"),))
        kkt.stationarity_conditions["m"] = SetMembershipTest("t", (SymbolRef("tl"),))

        suppressed = _compute_suppressed_fx_equations(kkt)
        assert suppressed == {"a_fx_0", "m_fx_0"}

    def test_multidim_domain_condition_on_first_index(self, manual_index_mapping):
        """Variable with 2-D domain and condition on first index only should not over-suppress."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)

        # Two-dimensional domain: (ku, k), with stationarity condition only on ku via subset t.
        model.sets["ku"] = SetDef(name="ku", members=["0", "1"])
        model.sets["k"] = SetDef(name="k", members=["0", "1"])
        model.sets["t"] = SetDef(name="t", members=["1"])

        x = VariableDef(name="x", domain=("ku", "k"), kind=VarKind.CONTINUOUS)
        # Fix x('0','0') outside the active subset on ku, and x('1','0') inside.
        idx_out = ("0", "0")
        idx_in = ("1", "0")
        x.fx_map[idx_out] = 10.0
        x.fx_map[idx_in] = 20.0
        model.variables["x"] = x

        kkt = _make_kkt(
            model,
            [
                ("obj", ()),
                ("x", ("0", "0")),
                ("x", ("0", "1")),
                ("x", ("1", "0")),
                ("x", ("1", "1")),
            ],
            manual_index_mapping,
        )
        # Stationarity is active only where ku is in t; k index is unconstrained.
        kkt.stationarity_conditions["x"] = SetMembershipTest("t", (SymbolRef("ku"),))

        suppressed = _compute_suppressed_fx_equations(kkt)
        # Only the fx for the index with ku='0' (not in t) should be suppressed.
        expected_suppressed = {_fx_eq_name("x", idx_out)}
        assert suppressed == expected_suppressed

    def test_multidim_membership_test_with_tuple_members(self, manual_index_mapping):
        """2-D SetMembershipTest with dot-joined tuple members suppresses correctly."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)

        # Variable x(w, t) with a 2-D membership condition td(w, t).
        # td members are dot-joined tuples: "w1.t1", "w1.t2" — so (w1,t1) and (w1,t2) are active.
        model.sets["w"] = SetDef(name="w", members=["w1", "w2"])
        model.sets["t"] = SetDef(name="t", members=["t1", "t2"])
        model.sets["td"] = SetDef(name="td", members=["w1.t1", "w1.t2"])

        x = VariableDef(name="x", domain=("w", "t"), kind=VarKind.CONTINUOUS)
        idx_active = ("w1", "t1")  # in td
        idx_inactive = ("w2", "t1")  # (w2,t1) not in td
        x.fx_map[idx_active] = 5.0
        x.fx_map[idx_inactive] = 10.0
        model.variables["x"] = x

        kkt = _make_kkt(
            model,
            [
                ("obj", ()),
                ("x", ("w1", "t1")),
                ("x", ("w1", "t2")),
                ("x", ("w2", "t1")),
                ("x", ("w2", "t2")),
            ],
            manual_index_mapping,
        )
        # 2-D membership condition: td(w, t)
        kkt.stationarity_conditions["x"] = SetMembershipTest("td", (SymbolRef("w"), SymbolRef("t")))

        suppressed = _compute_suppressed_fx_equations(kkt)
        # (w2, t1) is not in td — suppressed
        assert _fx_eq_name("x", idx_inactive) in suppressed
        # (w1, t1) is in td — not suppressed
        assert _fx_eq_name("x", idx_active) not in suppressed

    def test_multidim_membership_sparse_set(self, manual_index_mapping):
        """Sparse 2-D set: (w2,t1) absent even though w2 and t1 appear in other tuples."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)

        # td = {w1.t1, w2.t2} — sparse: w2 appears (in w2.t2) and t1 appears
        # (in w1.t1) but (w2,t1) is NOT a member.
        model.sets["w"] = SetDef(name="w", members=["w1", "w2"])
        model.sets["t"] = SetDef(name="t", members=["t1", "t2"])
        model.sets["td"] = SetDef(name="td", members=["w1.t1", "w2.t2"])

        x = VariableDef(name="x", domain=("w", "t"), kind=VarKind.CONTINUOUS)
        idx_in_td = ("w1", "t1")  # in td
        idx_not_in_td = ("w2", "t1")  # NOT in td despite w2 and t1 appearing separately
        x.fx_map[idx_in_td] = 5.0
        x.fx_map[idx_not_in_td] = 10.0
        model.variables["x"] = x

        kkt = _make_kkt(
            model,
            [
                ("obj", ()),
                ("x", ("w1", "t1")),
                ("x", ("w1", "t2")),
                ("x", ("w2", "t1")),
                ("x", ("w2", "t2")),
            ],
            manual_index_mapping,
        )
        kkt.stationarity_conditions["x"] = SetMembershipTest("td", (SymbolRef("w"), SymbolRef("t")))

        suppressed = _compute_suppressed_fx_equations(kkt)
        # (w2, t1) is NOT in td — must be suppressed (full-tuple check)
        assert _fx_eq_name("x", idx_not_in_td) in suppressed
        # (w1, t1) IS in td — must not be suppressed
        assert _fx_eq_name("x", idx_in_td) not in suppressed

    def test_disjunctive_condition_bails_out(self, manual_index_mapping):
        """Binary('or', ...) condition should bail out — no suppression."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)

        model.sets["tl"] = SetDef(name="tl", members=["0", "1", "2"])
        model.sets["t"] = SetDef(name="t", members=["1", "2"])
        model.sets["tt"] = SetDef(name="tt", members=["0", "1"])

        a = VariableDef(name="a", domain=("tl",), kind=VarKind.CONTINUOUS)
        a.fx_map[("0",)] = 1000.0  # "0" is not in t, but IS in tt
        model.variables["a"] = a

        kkt = _make_kkt(model, [("obj", ()), ("a", ("0",)), ("a", ("1",))], manual_index_mapping)
        # Disjunctive condition: t(tl) or tt(tl) — suppression is unsound here
        kkt.stationarity_conditions["a"] = Binary(
            "or",
            SetMembershipTest("t", (SymbolRef("tl"),)),
            SetMembershipTest("tt", (SymbolRef("tl"),)),
        )

        suppressed = _compute_suppressed_fx_equations(kkt)
        # Must return empty — can't safely suppress under disjunction
        assert suppressed == set()


@pytest.mark.unit
class TestSuppressedFxInEmission:
    """Tests that suppressed _fx_ equations are filtered from emitted output."""

    def test_suppressed_fx_not_in_model_statement(self, manual_index_mapping):
        """Suppressed _fx_ equations must not appear in the MCP model statement."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)

        model.sets["tl"] = SetDef(name="tl", members=["0", "1"])
        model.sets["t"] = SetDef(name="t", members=["1"])

        a = VariableDef(name="a", domain=("tl",), kind=VarKind.CONTINUOUS)
        a.fx_map[("0",)] = 1000.0
        model.variables["a"] = a

        # Register the _fx_ equation as an equality
        from src.ir.ast import Binary, Const, VarRef
        from src.ir.symbols import EquationDef, Rel

        fx_eq = EquationDef(
            name="a_fx_0",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(Binary("-", VarRef("a", indices=("0",)), Const(1000.0)), Const(0.0)),
        )
        model.equations["a_fx_0"] = fx_eq
        model.equalities.append("a_fx_0")

        kkt = _make_kkt(
            model,
            [("obj", ()), ("a", ("0",)), ("a", ("1",))],
            manual_index_mapping,
        )
        kkt.stationarity_conditions["a"] = SetMembershipTest("t", (SymbolRef("tl"),))
        # Register the equality multiplier so it is declared in the Variables section.
        kkt.multipliers_eq["a_fx_0"] = MultiplierDef(
            name="nu_a_fx_0", domain=(), kind="eq", associated_constraint="a_fx_0"
        )

        result = emit_gams_mcp(kkt)

        # The suppressed equation should NOT appear in the model statement
        assert "a_fx_0.nu_a_fx_0" not in result
        # But the correct .fx value should be re-emitted
        assert "a.fx('0') = 1000;" in result
        # And the multiplier should be fixed to 0
        assert "nu_a_fx_0.fx = 0;" in result

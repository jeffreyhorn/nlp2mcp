"""Full end-to-end KKT system assembly tests."""

import pytest

from src.ad.gradient import GradientVector
from src.ad.index_mapping import IndexMapping
from src.ad.jacobian import JacobianStructure
from src.ir.ast import Binary, Const, VarRef
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import EquationDef, ObjSense, Rel, VariableDef
from src.kkt.assemble import assemble_kkt_system


def _manual_index_mapping(
    vars: list[tuple[str, tuple]], eqs: list[tuple[str, tuple]] = None
) -> IndexMapping:
    """Helper to manually create IndexMapping for tests."""
    mapping = IndexMapping()

    for col_id, (var_name, indices) in enumerate(vars):
        mapping.var_to_col[(var_name, indices)] = col_id
        mapping.col_to_var[col_id] = (var_name, indices)
    mapping.num_vars = len(vars)

    if eqs:
        for row_id, (eq_name, indices) in enumerate(eqs):
            mapping.eq_to_row[(eq_name, indices)] = row_id
            mapping.row_to_eq[row_id] = (eq_name, indices)
        mapping.num_eqs = len(eqs)

    return mapping


@pytest.mark.integration
class TestKKTFullAssembly:
    """Test full KKT system assembly."""

    def test_simple_nlp_full_assembly(self):
        """Test complete KKT assembly for simple NLP.

        Problem:
            min x^2 + y^2
            s.t. x + y = 1

        KKT components:
            - 2 stationarity equations (x, y; not obj)
            - 1 equality equation (x + y = 1)
            - 1 equality multiplier (ν)
            - No inequalities, no bounds
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        # obj =E= x^2 + y^2
        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("obj", ()),
                Binary(
                    "+",
                    Binary("^", VarRef("x", ()), Const(2.0)),
                    Binary("^", VarRef("y", ()), Const(2.0)),
                ),
            ),
        )

        # x + y =E= 1
        model.equations["balance"] = EquationDef(
            name="balance",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(Binary("+", VarRef("x", ()), VarRef("y", ())), Const(1.0)),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=())
        model.variables["y"] = VariableDef(name="y", domain=())

        model.equalities = ["objdef", "balance"]

        # Set up derivatives
        index_mapping = _manual_index_mapping(
            [("obj", ()), ("x", ()), ("y", ())], [("objdef", ()), ("balance", ())]
        )

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Binary("*", Const(2.0), VarRef("x", ())))  # 2x
        gradient.set_derivative(2, Binary("*", Const(2.0), VarRef("y", ())))  # 2y

        J_eq = JacobianStructure(num_rows=2, num_cols=3, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))  # ∂objdef/∂obj
        J_eq.set_derivative(1, 1, Const(1.0))  # ∂balance/∂x
        J_eq.set_derivative(1, 2, Const(1.0))  # ∂balance/∂y

        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        # Assemble full KKT system
        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

        # Verify counts
        assert len(kkt.stationarity) == 2  # x and y (not obj)
        assert "stat_x" in kkt.stationarity
        assert "stat_y" in kkt.stationarity
        assert "stat_obj" not in kkt.stationarity

        assert len(kkt.multipliers_eq) == 2  # objdef and balance
        assert len(kkt.multipliers_ineq) == 0
        assert len(kkt.multipliers_bounds_lo) == 0
        assert len(kkt.multipliers_bounds_up) == 0

        assert len(kkt.complementarity_ineq) == 0
        assert len(kkt.complementarity_bounds_lo) == 0
        assert len(kkt.complementarity_bounds_up) == 0

    def test_nlp_with_bounds_assembly(self):
        """Test KKT assembly with variable bounds.

        Problem:
            min x^2
            s.t. x ≥ 1, x ≤ 10

        KKT components:
            - 1 stationarity equation (x; not obj)
            - 2 bound complementarity pairs (lower and upper)
            - 2 bound multipliers (π^L, π^U)
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), Binary("^", VarRef("x", ()), Const(2.0))),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=(), lo=1.0, up=10.0)

        model.equalities = ["objdef"]

        # Set up derivatives
        index_mapping = _manual_index_mapping([("obj", ()), ("x", ())], [("objdef", ())])

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Binary("*", Const(2.0), VarRef("x", ())))

        J_eq = JacobianStructure(num_rows=1, num_cols=2, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))

        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        # Assemble KKT
        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

        # Verify
        assert len(kkt.stationarity) == 1
        assert "stat_x" in kkt.stationarity

        assert len(kkt.multipliers_bounds_lo) == 1
        assert ("x", ()) in kkt.multipliers_bounds_lo

        assert len(kkt.multipliers_bounds_up) == 1
        assert ("x", ()) in kkt.multipliers_bounds_up

        assert len(kkt.complementarity_bounds_lo) == 1
        assert ("x", ()) in kkt.complementarity_bounds_lo

        assert len(kkt.complementarity_bounds_up) == 1
        assert ("x", ()) in kkt.complementarity_bounds_up

    def test_nlp_with_inequality_assembly(self):
        """Test KKT assembly with inequality constraints.

        Problem:
            min x^2 + y^2
            s.t. x + y ≤ 10

        KKT components:
            - 2 stationarity equations
            - 1 inequality complementarity pair
            - 1 inequality multiplier (λ)
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ())),
        )

        model.equations["capacity"] = EquationDef(
            name="capacity",
            domain=(),
            relation=Rel.LE,
            lhs_rhs=(Binary("+", VarRef("x", ()), VarRef("y", ())), Const(10.0)),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=())
        model.variables["y"] = VariableDef(name="y", domain=())

        model.equalities = ["objdef"]
        model.inequalities = ["capacity"]

        # Set up derivatives
        index_mapping = _manual_index_mapping(
            [("obj", ()), ("x", ()), ("y", ())], [("objdef", ()), ("capacity", ())]
        )

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(1.0))
        gradient.set_derivative(2, Const(0.0))

        J_eq = JacobianStructure(num_rows=1, num_cols=3, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))

        J_ineq = JacobianStructure(num_rows=1, num_cols=3, index_mapping=index_mapping)
        J_ineq.set_derivative(0, 1, Const(1.0))
        J_ineq.set_derivative(0, 2, Const(1.0))

        # Assemble KKT
        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

        # Verify
        assert len(kkt.stationarity) == 2  # x, y
        assert len(kkt.multipliers_ineq) == 1
        assert len(kkt.complementarity_ineq) == 1
        assert "capacity" in kkt.complementarity_ineq

    def test_indexed_bounds_assembly(self):
        """Test KKT assembly with indexed variable bounds.

        Problem:
            min sum(i, x(i)^2)
            s.t. x(i) ≥ 0 for specific instances

        KKT components:
            - Per-instance stationarity equations
            - Per-instance bound multipliers
            - Per-instance complementarity pairs
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ("i",))),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(
            name="x", domain=("i",), lo_map={("i1",): 0.0, ("i2",): 1.0}
        )

        model.equalities = ["objdef"]
        model.sets["i"] = ["i1", "i2"]

        # Set up derivatives
        index_mapping = _manual_index_mapping(
            [("obj", ()), ("x", ("i1",)), ("x", ("i2",))], [("objdef", ())]
        )

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(2.0))
        gradient.set_derivative(2, Const(2.0))

        J_eq = JacobianStructure(num_rows=1, num_cols=3, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))

        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        # Assemble KKT
        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

        # Verify indexed bounds
        assert len(kkt.stationarity) == 2  # x(i1), x(i2)
        assert "stat_x_i1" in kkt.stationarity
        assert "stat_x_i2" in kkt.stationarity

        assert len(kkt.multipliers_bounds_lo) == 2
        assert ("x", ("i1",)) in kkt.multipliers_bounds_lo
        assert ("x", ("i2",)) in kkt.multipliers_bounds_lo

        assert len(kkt.complementarity_bounds_lo) == 2
        assert ("x", ("i1",)) in kkt.complementarity_bounds_lo
        assert ("x", ("i2",)) in kkt.complementarity_bounds_lo

    def test_infinite_bounds_filtered(self):
        """Test that infinite bounds are filtered out.

        Variables with ±INF bounds should not have multipliers or complementarity.
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ())),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=(), lo=float("-inf"), up=float("inf"))

        model.equalities = ["objdef"]

        # Set up derivatives
        index_mapping = _manual_index_mapping([("obj", ()), ("x", ())], [("objdef", ())])

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(1.0))

        J_eq = JacobianStructure(num_rows=1, num_cols=2, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))

        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        # Assemble KKT
        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

        # Verify no bound multipliers for infinite bounds
        assert len(kkt.multipliers_bounds_lo) == 0
        assert len(kkt.multipliers_bounds_up) == 0
        assert len(kkt.complementarity_bounds_lo) == 0
        assert len(kkt.complementarity_bounds_up) == 0

        # But should have stationarity
        assert len(kkt.stationarity) == 1
        assert "stat_x" in kkt.stationarity

        # Should have logged skipped bounds
        assert len(kkt.skipped_infinite_bounds) == 2  # lo and up

    def test_objective_defining_equation_included(self):
        """Test that objective defining equation is included in the system."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ())),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=())

        model.equalities = ["objdef"]

        # Set up derivatives
        index_mapping = _manual_index_mapping([("obj", ()), ("x", ())], [("objdef", ())])

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(1.0))

        J_eq = JacobianStructure(num_rows=1, num_cols=2, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))

        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        # Assemble KKT
        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

        # Objective defining equation should be in equalities
        # (This is built by complementarity builder)
        comp_ineq, comp_lo, comp_up, eq_eqs = (
            kkt.complementarity_ineq,
            kkt.complementarity_bounds_lo,
            kkt.complementarity_bounds_up,
            {},
        )

        # Note: equality_eqs are built in complementarity but not stored directly
        # We verify objdef has a multiplier
        assert "nu_objdef" in kkt.multipliers_eq

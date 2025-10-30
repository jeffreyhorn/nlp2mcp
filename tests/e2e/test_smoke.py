"""Early integration smoke tests for complete pipeline.

These tests verify that the full pipeline (Parse → Normalize → AD → KKT)
works end-to-end for key scenarios.
"""

import pytest

from src.ad.gradient import GradientVector
from src.ad.index_mapping import IndexMapping
from src.ad.jacobian import JacobianStructure
from src.ir.ast import Binary, Const, VarRef
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import EquationDef, ObjSense, Rel, VariableDef
from src.kkt.kkt_system import KKTSystem, MultiplierDef
from src.kkt.objective import extract_objective_info
from src.kkt.partition import partition_constraints
from src.kkt.stationarity import build_stationarity_equations


def _manual_index_mapping(vars: list[tuple[str, tuple]], eqs: list[tuple[str, tuple]] = None):
    """Helper to manually create IndexMapping for tests."""
    from src.ad.index_mapping import IndexMapping

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


@pytest.mark.e2e
class TestMinimalPipeline:
    """Smoke tests for minimal pipeline components."""

    def test_minimal_scalar_nlp_pipeline(self):
        """Test basic pipeline: model setup → derivatives → KKT.

        Problem:
            min x^2
        """
        # Build model
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), Binary("^", VarRef("x", ()), Const(2.0))),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=())

        model.equalities = ["objdef"]

        # Set up derivatives
        index_mapping = _manual_index_mapping([("obj", ()), ("x", ())])

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(1, Binary("*", Const(2.0), VarRef("x", ())))

        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        # Build KKT system
        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        # Extract objective info
        obj_info = extract_objective_info(model)
        assert obj_info.objvar == "obj"
        assert obj_info.defining_equation == "objdef"

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        # Verify
        assert len(stationarity) == 1
        assert "stat_x" in stationarity

    def test_indexed_nlp_pipeline(self):
        """Test pipeline with indexed variables.

        Problem:
            min sum(i, x(i)^2)
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
        model.variables["x"] = VariableDef(name="x", domain=("i",))

        model.equalities = ["objdef"]
        model.sets["i"] = ["i1", "i2"]

        # Set up derivatives
        index_mapping = _manual_index_mapping([("obj", ()), ("x", ("i1",)), ("x", ("i2",))])

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(1, Const(2.0))
        gradient.set_derivative(2, Const(2.0))

        J_eq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        # Build KKT system
        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        # Verify
        assert len(stationarity) == 2
        assert "stat_x_i1" in stationarity
        assert "stat_x_i2" in stationarity

    def test_bounds_handling_pipeline(self):
        """Test pipeline with bounds (regression test for issue #24).

        Problem:
            min x^2
            s.t. x ≥ 1
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
        model.variables["x"] = VariableDef(name="x", domain=(), lo=1.0)

        model.equalities = ["objdef"]

        # Partition constraints
        partition_result = partition_constraints(model)

        # Verify bounds detected
        assert ("x", ()) in partition_result.bounds_lo
        assert partition_result.bounds_lo[("x", ())].value == 1.0

        # Set up KKT system
        index_mapping = _manual_index_mapping([("obj", ()), ("x", ())])

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(1, Binary("*", Const(2.0), VarRef("x", ())))

        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        # Add bound multiplier
        kkt.multipliers_bounds_lo[("x", ())] = MultiplierDef(
            name="piL_x", domain=(), kind="bound_lo", associated_constraint="x"
        )

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        # Verify stationarity includes π^L term
        assert len(stationarity) == 1
        assert "stat_x" in stationarity


@pytest.mark.e2e
class TestKKTAssemblerSmoke:
    """Smoke tests specifically for KKT assembler."""

    def test_kkt_assembler_smoke(self):
        """Basic KKT assembly smoke test.

        Verifies that all KKT components can be assembled:
        - Objective info extraction
        - Constraint partitioning
        - Stationarity building
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), Binary("+", VarRef("x", ()), VarRef("y", ()))),
        )

        model.equations["constraint"] = EquationDef(
            name="constraint",
            domain=(),
            relation=Rel.LE,
            lhs_rhs=(Binary("+", VarRef("x", ()), VarRef("y", ())), Const(10.0)),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=(), lo=0.0)
        model.variables["y"] = VariableDef(name="y", domain=(), lo=0.0, up=5.0)

        model.equalities = ["objdef"]
        model.inequalities = ["constraint"]

        # Step 1: Extract objective info
        obj_info = extract_objective_info(model)
        assert obj_info.objvar == "obj"
        assert obj_info.defining_equation == "objdef"

        # Step 2: Partition constraints
        partition_result = partition_constraints(model)
        assert "objdef" in partition_result.equalities
        assert "constraint" in partition_result.inequalities
        assert ("x", ()) in partition_result.bounds_lo
        assert ("y", ()) in partition_result.bounds_lo
        assert ("y", ()) in partition_result.bounds_up

        # Step 3: Set up derivatives
        index_mapping = _manual_index_mapping(
            [("obj", ()), ("x", ()), ("y", ())], [("constraint", ())]
        )

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(1, Const(1.0))
        gradient.set_derivative(2, Const(1.0))

        J_eq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        J_ineq = JacobianStructure(num_rows=1, num_cols=3, index_mapping=index_mapping)
        J_ineq.set_derivative(0, 1, Const(1.0))
        J_ineq.set_derivative(0, 2, Const(1.0))

        # Step 4: Build KKT system
        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        kkt.multipliers_ineq["lam_constraint"] = MultiplierDef(
            name="lam_constraint", domain=(), kind="ineq", associated_constraint="constraint"
        )
        kkt.multipliers_bounds_lo[("x", ())] = MultiplierDef(
            name="piL_x", domain=(), kind="bound_lo", associated_constraint="x"
        )
        kkt.multipliers_bounds_lo[("y", ())] = MultiplierDef(
            name="piL_y", domain=(), kind="bound_lo", associated_constraint="y"
        )
        kkt.multipliers_bounds_up[("y", ())] = MultiplierDef(
            name="piU_y", domain=(), kind="bound_up", associated_constraint="y"
        )

        # Step 5: Build stationarity
        stationarity = build_stationarity_equations(kkt)

        # Verify
        assert len(stationarity) == 2  # x and y, not obj
        assert "stat_x" in stationarity
        assert "stat_y" in stationarity

    def test_indexed_bounds_handling(self):
        """Test KKT assembly with indexed bounds.

        Verifies that indexed bounds are correctly handled in:
        - Partitioning (via lo_map/up_map)
        - Multiplier generation
        - Stationarity building
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
            name="x",
            domain=("i",),
            lo_map={("i1",): 0.0, ("i2",): 1.0},
        )

        model.equalities = ["objdef"]
        model.sets["i"] = ["i1", "i2"]

        # Partition constraints
        partition_result = partition_constraints(model)

        # Verify indexed bounds detected
        assert ("x", ("i1",)) in partition_result.bounds_lo
        assert ("x", ("i2",)) in partition_result.bounds_lo
        assert partition_result.bounds_lo[("x", ("i1",))].value == 0.0
        assert partition_result.bounds_lo[("x", ("i2",))].value == 1.0

        # Set up KKT system
        index_mapping = _manual_index_mapping([("obj", ()), ("x", ("i1",)), ("x", ("i2",))])

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(1, Const(1.0))
        gradient.set_derivative(2, Const(1.0))

        J_eq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        # Add indexed bound multipliers
        kkt.multipliers_bounds_lo[("x", ("i1",))] = MultiplierDef(
            name="piL_x", domain=("i",), kind="bound_lo", associated_constraint="x"
        )
        kkt.multipliers_bounds_lo[("x", ("i2",))] = MultiplierDef(
            name="piL_x", domain=("i",), kind="bound_lo", associated_constraint="x"
        )

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        # Verify
        assert len(stationarity) == 2
        assert "stat_x_i1" in stationarity
        assert "stat_x_i2" in stationarity

    def test_objective_variable_handling(self):
        """Test that objective variable is correctly handled in KKT assembly.

        Verifies:
        - Objective variable detected
        - No stationarity equation for objective variable
        - Objective defining equation identified
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="cost")

        model.equations["costdef"] = EquationDef(
            name="costdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("cost", ()),
                Binary("*", Const(2.0), VarRef("x", ())),
            ),
        )

        model.variables["cost"] = VariableDef(name="cost", domain=())
        model.variables["x"] = VariableDef(name="x", domain=())

        model.equalities = ["costdef"]

        # Extract objective info
        obj_info = extract_objective_info(model)
        assert obj_info.objvar == "cost"
        assert obj_info.defining_equation == "costdef"
        assert obj_info.needs_stationarity is False

        # Set up KKT system
        index_mapping = _manual_index_mapping([("cost", ()), ("x", ())])

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(2.0))

        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        # Verify: only x has stationarity, not cost
        assert len(stationarity) == 1
        assert "stat_x" in stationarity
        assert "stat_cost" not in stationarity

"""Integration tests for stationarity equation builder."""

import pytest

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.ir.ast import Binary, Call, Const, Expr, ParamRef, Sum, Unary, VarRef
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import EquationDef, ObjSense, Rel, VariableDef
from src.kkt.kkt_system import KKTSystem, MultiplierDef
from src.kkt.stationarity import build_stationarity_equations


@pytest.mark.integration
class TestStationarityScalar:
    """Test stationarity for scalar NLP problems."""

    def test_scalar_nlp_basic_structure(self, manual_index_mapping):
        """Test basic stationarity structure for scalar problem.

        Problem:
            min x^2
            s.t. x ≥ 1

        KKT stationarity: 2x - π^L = 0
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        # obj =E= x^2
        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("obj", ()),
                Binary("^", VarRef("x", ()), Const(2.0)),
            ),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=(), lo=1.0)

        model.equalities = ["objdef"]

        # Set up KKT system
        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))  # ∂obj/∂obj = 1
        gradient.set_derivative(1, Binary("*", Const(2.0), VarRef("x", ())))  # ∂obj/∂x = 2x

        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        # Add lower bound multiplier
        kkt.multipliers_bounds_lo[("x", ())] = MultiplierDef(
            name="piL_x", domain=(), kind="bound_lo", associated_constraint="x"
        )

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        # Should have one stationarity equation (for x, not obj)
        assert len(stationarity) == 1
        assert "stat_x" in stationarity

        stat_eq = stationarity["stat_x"]
        assert stat_eq.relation == Rel.EQ
        assert isinstance(stat_eq.lhs_rhs[1], Const)
        assert stat_eq.lhs_rhs[1].value == 0.0

    def test_scalar_nlp_with_equality_constraint(self, manual_index_mapping):
        """Test stationarity with equality constraint.

        Problem:
            min (x - 3)^2 + (y - 2)^2
            s.t. x + y = 5

        KKT stationarity:
            2(x - 3) + ν = 0
            2(y - 2) + ν = 0
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ())),
        )

        model.equations["balance"] = EquationDef(
            name="balance",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                Binary("+", VarRef("x", ()), VarRef("y", ())),
                Const(5.0),
            ),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=())
        model.variables["y"] = VariableDef(name="y", domain=())

        model.equalities = ["objdef", "balance"]

        # Set up KKT system
        index_mapping = manual_index_mapping(
            [("obj", ()), ("x", ()), ("y", ())], [("objdef", ()), ("balance", ())]
        )

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(
            1, Binary("*", Const(2.0), Binary("-", VarRef("x", ()), Const(3.0)))
        )
        gradient.set_derivative(
            2, Binary("*", Const(2.0), Binary("-", VarRef("y", ()), Const(2.0)))
        )

        J_eq = JacobianStructure(num_rows=2, num_cols=3, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))  # ∂objdef/∂obj
        J_eq.set_derivative(1, 1, Const(1.0))  # ∂balance/∂x
        J_eq.set_derivative(1, 2, Const(1.0))  # ∂balance/∂y

        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        # Add equality multiplier
        kkt.multipliers_eq["nu_balance"] = MultiplierDef(
            name="nu_balance", domain=(), kind="eq", associated_constraint="balance"
        )

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        # Should have two stationarity equations (x and y, not obj)
        assert len(stationarity) == 2
        assert "stat_x" in stationarity
        assert "stat_y" in stationarity

    def test_scalar_nlp_with_inequality_constraint(self, manual_index_mapping):
        """Test stationarity with inequality constraint.

        Problem:
            min x^2
            s.t. x ≤ 10

        KKT stationarity: 2x + λ = 0
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), Binary("^", VarRef("x", ()), Const(2.0))),
        )

        model.equations["capacity"] = EquationDef(
            name="capacity",
            domain=(),
            relation=Rel.LE,
            lhs_rhs=(VarRef("x", ()), Const(10.0)),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=())

        model.equalities = ["objdef"]
        model.inequalities = ["capacity"]

        # Set up KKT system
        index_mapping = manual_index_mapping(
            [("obj", ()), ("x", ())], [("objdef", ()), ("capacity", ())]
        )

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Binary("*", Const(2.0), VarRef("x", ())))

        J_eq = JacobianStructure(num_rows=1, num_cols=2, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))

        J_ineq = JacobianStructure(num_rows=1, num_cols=2, index_mapping=index_mapping)
        J_ineq.set_derivative(0, 1, Const(1.0))  # ∂capacity/∂x

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        kkt.multipliers_ineq["lam_capacity"] = MultiplierDef(
            name="lam_capacity", domain=(), kind="ineq", associated_constraint="capacity"
        )

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        assert len(stationarity) == 1
        assert "stat_x" in stationarity


@pytest.mark.integration
class TestStationarityIndexed:
    """Test stationarity for indexed NLP problems."""

    def test_indexed_variable_stationarity(self, manual_index_mapping):
        """Test stationarity for indexed variables.

        Problem:
            min sum(i, x(i)^2)
            s.t. sum(i, x(i)) = 10

        Each x(i) should have its own stationarity equation.
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ("i",))),
        )

        model.equations["balance"] = EquationDef(
            name="balance",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("x", ("i",)), Const(10.0)),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=("i",))

        model.equalities = ["objdef", "balance"]

        model.sets["i"] = ["i1", "i2", "i3"]

        # Set up KKT system
        index_mapping = manual_index_mapping(
            [("obj", ()), ("x", ("i1",)), ("x", ("i2",)), ("x", ("i3",))],
            [("objdef", ()), ("balance", ())],
        )

        gradient = GradientVector(num_cols=4, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Binary("*", Const(2.0), VarRef("x", ("i1",))))
        gradient.set_derivative(2, Binary("*", Const(2.0), VarRef("x", ("i2",))))
        gradient.set_derivative(3, Binary("*", Const(2.0), VarRef("x", ("i3",))))

        J_eq = JacobianStructure(num_rows=2, num_cols=4, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))
        J_eq.set_derivative(1, 1, Const(1.0))
        J_eq.set_derivative(1, 2, Const(1.0))
        J_eq.set_derivative(1, 3, Const(1.0))

        J_ineq = JacobianStructure(num_rows=0, num_cols=4, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        kkt.multipliers_eq["nu_balance"] = MultiplierDef(
            name="nu_balance", domain=(), kind="eq", associated_constraint="balance"
        )

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        # Should have one indexed stationarity equation stat_x(i)
        assert len(stationarity) == 1
        assert "stat_x" in stationarity
        assert stationarity["stat_x"].domain == ("i",)

    def test_indexed_bounds_stationarity_uniform(self, manual_index_mapping):
        """Test stationarity with uniform indexed bounds.

        When all x(i) have the same bound value (uniform bounds), a single
        indexed stationarity equation stat_x(i) is generated with the indexed
        π^L term.
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

        # Set up KKT system
        index_mapping = manual_index_mapping([("obj", ()), ("x", ("i1",)), ("x", ("i2",))])

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(1.0))
        gradient.set_derivative(2, Const(1.0))

        J_eq = JacobianStructure(num_rows=1, num_cols=3, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))

        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        # Add UNIFORM indexed bound multiplier (stored under empty indices key)
        # This represents x(i) >= 0 for all i (same bound value)
        kkt.multipliers_bounds_lo[("x", ())] = MultiplierDef(
            name="piL_x", domain=("i",), kind="bound_lo", associated_constraint="x"
        )

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        # Should have one indexed stationarity equation stat_x(i)
        assert len(stationarity) == 1
        assert "stat_x" in stationarity
        assert stationarity["stat_x"].domain == ("i",)

        # Verify bound multiplier is included in stationarity expression
        stat_str = str(stationarity["stat_x"].lhs_rhs[0])
        assert "piL_x" in stat_str, "Bound multiplier missing from stationarity"

    def test_indexed_bounds_stationarity_nonuniform(self, manual_index_mapping):
        """Test stationarity with non-uniform indexed bounds.

        When x(i) has different bound values per element (non-uniform bounds),
        per-instance stationarity equations are generated to ensure bound
        multipliers are properly included.
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

        # Set up KKT system
        index_mapping = manual_index_mapping([("obj", ()), ("x", ("i1",)), ("x", ("i2",))])

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(1.0))
        gradient.set_derivative(2, Const(1.0))

        J_eq = JacobianStructure(num_rows=1, num_cols=3, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))

        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        # Add NON-UNIFORM per-instance bound multipliers (different values)
        # This represents x("i1") >= 0, x("i2") >= 1
        kkt.multipliers_bounds_lo[("x", ("i1",))] = MultiplierDef(
            name="piL_x_i1", domain=(), kind="bound_lo", associated_constraint="x"
        )
        kkt.multipliers_bounds_lo[("x", ("i2",))] = MultiplierDef(
            name="piL_x_i2", domain=(), kind="bound_lo", associated_constraint="x"
        )

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        # Should have per-instance stationarity equations
        assert len(stationarity) == 2
        assert "stat_x_i1" in stationarity
        assert "stat_x_i2" in stationarity
        assert stationarity["stat_x_i1"].domain == ()
        assert stationarity["stat_x_i2"].domain == ()

        # Verify bound multipliers are included in stationarity expressions
        stat_i1_str = str(stationarity["stat_x_i1"].lhs_rhs[0])
        stat_i2_str = str(stationarity["stat_x_i2"].lhs_rhs[0])
        assert "piL_x_i1" in stat_i1_str, "Bound multiplier missing from stat_x_i1"
        assert "piL_x_i2" in stat_i2_str, "Bound multiplier missing from stat_x_i2"


@pytest.mark.integration
class TestStationarityBounds:
    """Test stationarity with various bound configurations."""

    def test_no_pi_term_for_infinite_lower_bound(self, manual_index_mapping):
        """Variables with -INF lower bound should not have π^L term."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ())),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=(), lo=float("-inf"))

        model.equalities = ["objdef"]

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(1.0))

        J_eq = JacobianStructure(num_rows=1, num_cols=2, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))

        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        # No bound multipliers for infinite bounds

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        assert len(stationarity) == 1
        assert "stat_x" in stationarity

    def test_no_pi_term_for_infinite_upper_bound(self, manual_index_mapping):
        """Variables with +INF upper bound should not have π^U term."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ())),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=(), up=float("inf"))

        model.equalities = ["objdef"]

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(1.0))

        J_eq = JacobianStructure(num_rows=1, num_cols=2, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))

        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        assert len(stationarity) == 1
        assert "stat_x" in stationarity

    def test_both_bounds_present(self, manual_index_mapping):
        """Variable with both finite bounds should have both π^L and π^U terms."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ())),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=(), lo=0.0, up=10.0)

        model.equalities = ["objdef"]

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(1.0))

        J_eq = JacobianStructure(num_rows=1, num_cols=2, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))

        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        kkt.multipliers_bounds_lo[("x", ())] = MultiplierDef(
            name="piL_x", domain=(), kind="bound_lo", associated_constraint="x"
        )
        kkt.multipliers_bounds_up[("x", ())] = MultiplierDef(
            name="piU_x", domain=(), kind="bound_up", associated_constraint="x"
        )

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        assert len(stationarity) == 1
        assert "stat_x" in stationarity


@pytest.mark.integration
class TestStationarityObjectiveVariable:
    """Test that objective variable is skipped in stationarity."""

    def test_objective_variable_skipped(self, manual_index_mapping):
        """Objective variable should not have a stationarity equation."""
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

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Binary("*", Const(2.0), VarRef("x", ())))

        J_eq = JacobianStructure(num_rows=1, num_cols=2, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))

        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        # Only x should have stationarity, not obj
        assert len(stationarity) == 1
        assert "stat_x" in stationarity
        assert "stat_obj" not in stationarity

    def test_objective_defining_equation_skipped_in_jacobian_terms(self, manual_index_mapping):
        """Objective defining equation should not contribute to stationarity."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ())),
        )

        model.equations["constraint"] = EquationDef(
            name="constraint",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("x", ()), Const(5.0)),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=())

        model.equalities = ["objdef", "constraint"]

        index_mapping = manual_index_mapping(
            [("obj", ()), ("x", ())], [("objdef", ()), ("constraint", ())]
        )

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(1.0))

        J_eq = JacobianStructure(num_rows=2, num_cols=2, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))  # ∂objdef/∂obj
        J_eq.set_derivative(0, 1, Const(1.0))  # ∂objdef/∂x
        J_eq.set_derivative(1, 1, Const(1.0))  # ∂constraint/∂x

        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        kkt.multipliers_eq["nu_objdef"] = MultiplierDef(
            name="nu_objdef", domain=(), kind="eq", associated_constraint="objdef"
        )
        kkt.multipliers_eq["nu_constraint"] = MultiplierDef(
            name="nu_constraint", domain=(), kind="eq", associated_constraint="constraint"
        )

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        # Only x should have stationarity
        assert len(stationarity) == 1
        assert "stat_x" in stationarity


@pytest.mark.integration
class TestStationarityIndexDisambiguation:
    """Test correct index disambiguation when elements belong to multiple sets.

    GitHub Issue #572: KKT Incorrect Index References
    When an element (e.g., 'H') belongs to multiple sets (e.g., both 'i' and 'c'),
    the stationarity builder must use the parameter's declared domain to determine
    the correct index mapping, not just the element-to-set mapping.
    """

    def test_parameter_domain_disambiguation(self, manual_index_mapping):
        """Test that parameter domain is used to disambiguate index references.

        Simulates the chem model case where:
        - Element 'H' belongs to both set 'i' and set 'c'
        - Parameter a(i,c) should become a(i,c), not a(c,c)

        When generating stationarity for x(c), the Jacobian term contains a('H','c')
        (where 'H' was substituted for the element). Without disambiguation, both
        indices would map to 'c'. With proper disambiguation using a's declared
        domain (i,c), the first index maps to 'i' and second to 'c'.
        """
        from src.ir.symbols import ParameterDef, SetDef

        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        # Sets where 'H' belongs to both 'i' and 'c'
        model.sets["i"] = SetDef(name="i", members=["H", "N", "O"])
        model.sets["c"] = SetDef(name="c", members=["H", "N", "O"])

        # Parameter a(i,c) - the domain is crucial for disambiguation
        model.params["a"] = ParameterDef(name="a", domain=("i", "c"))

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ("c",))),
        )

        # Constraint cdef(i) that references a(i,c) and x(c)
        model.equations["cdef"] = EquationDef(
            name="cdef",
            domain=("i",),
            relation=Rel.EQ,
            lhs_rhs=(
                Binary("*", ParamRef("a", ("i", "c")), VarRef("x", ("c",))),
                Const(1.0),
            ),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=("c",))

        model.equalities = ["objdef", "cdef"]

        # Set up KKT system with instances for x(c) where c in {H, N, O}
        index_mapping = manual_index_mapping(
            [("obj", ()), ("x", ("H",)), ("x", ("N",)), ("x", ("O",))],
            [("objdef", ()), ("cdef", ("H",)), ("cdef", ("N",)), ("cdef", ("O",))],
        )

        gradient = GradientVector(num_cols=4, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        # Gradient for x(H), x(N), x(O) - simple for this test
        gradient.set_derivative(1, Const(1.0))
        gradient.set_derivative(2, Const(1.0))
        gradient.set_derivative(3, Const(1.0))

        J_eq = JacobianStructure(num_rows=4, num_cols=4, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))  # ∂objdef/∂obj

        # Jacobian entries for cdef(i) w.r.t. x(c)
        # When i=H and c=H: ∂cdef(H)/∂x(H) = a('H', 'H')
        # The key test: this should become a(i,c), not a(c,c)
        J_eq.set_derivative(1, 1, ParamRef("a", ("H", "H")))  # cdef(H) w.r.t. x(H)
        J_eq.set_derivative(2, 2, ParamRef("a", ("N", "N")))  # cdef(N) w.r.t. x(N)
        J_eq.set_derivative(3, 3, ParamRef("a", ("O", "O")))  # cdef(O) w.r.t. x(O)

        J_ineq = JacobianStructure(num_rows=0, num_cols=4, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        kkt.multipliers_eq["nu_cdef"] = MultiplierDef(
            name="nu_cdef", domain=("i",), kind="eq", associated_constraint="cdef"
        )

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        assert "stat_x" in stationarity
        stat_eq = stationarity["stat_x"]

        # The stationarity equation for x(c) should reference a(i,c), not a(c,c)
        # We check by examining the AST for ParamRef nodes
        def find_param_refs(expr: Expr) -> list[ParamRef]:
            """Recursively find all ParamRef nodes in expression."""
            refs = []
            match expr:
                case ParamRef():
                    refs.append(expr)
                case Binary(_, left, right):
                    refs.extend(find_param_refs(left))
                    refs.extend(find_param_refs(right))
                case Unary(_, child):
                    refs.extend(find_param_refs(child))
                case Call(_, args):
                    for arg in args:
                        refs.extend(find_param_refs(arg))
                case Sum(_, body):
                    refs.extend(find_param_refs(body))
            return refs

        lhs = stat_eq.lhs_rhs[0]
        param_refs = find_param_refs(lhs)

        # Find references to parameter 'a'
        a_refs = [ref for ref in param_refs if ref.name == "a"]
        assert len(a_refs) > 0, "Expected parameter 'a' in stationarity equation"

        # Check that a(i,c) is used, not a(c,c)
        for ref in a_refs:
            indices = ref.indices_as_strings()
            assert indices == (
                "i",
                "c",
            ), f"Expected a(i,c) but got a{indices}. Parameter domain disambiguation failed."

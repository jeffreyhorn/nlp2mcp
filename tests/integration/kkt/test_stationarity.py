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

    def test_cross_domain_summation_partial_overlap(self, manual_index_mapping):
        """Test stationarity with partial domain overlap (trussm pattern).

        GitHub Issue #594: Cross-domain summation in constraints.

        When a constraint sums over a variable using different index sets:
        - Variable s(i,k) has domain ('i', 'k')
        - Constraint stiffness(j,k) has domain ('j', 'k')
        - Equation: sum(i, s(i,k)*b(j,i)) =E= f(j,k)

        The domains partially overlap (share 'k') but each has unique indices
        ('i' in variable, 'j' in constraint). The stationarity term should
        sum over the extra multiplier indices:
            sum(j, derivative * nu_stiffness(j,k))
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.sets["i"] = ["i1", "i2"]  # bars
        model.sets["j"] = ["j1", "j2"]  # nodes
        model.sets["k"] = ["k1"]  # load scenarios (single for simplicity)

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), Const(0.0)),
        )

        # stiffness(j,k).. sum(i, s(i,k)*b(j,i)) =E= f(j,k)
        model.equations["stiffness"] = EquationDef(
            name="stiffness",
            domain=("j", "k"),
            relation=Rel.EQ,
            lhs_rhs=(
                Sum(("i",), Binary("*", VarRef("s", ("i", "k")), ParamRef("b", ("j", "i")))),
                ParamRef("f", ("j", "k")),
            ),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["s"] = VariableDef(name="s", domain=("i", "k"))

        model.equalities = ["objdef", "stiffness"]

        # Set up KKT system with s(i,k) instances
        index_mapping = manual_index_mapping(
            [("obj", ()), ("s", ("i1", "k1")), ("s", ("i2", "k1"))],
            [
                ("objdef", ()),
                ("stiffness", ("j1", "k1")),
                ("stiffness", ("j2", "k1")),
            ],
        )

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(0.0))  # ∂obj/∂s(i1,k1) = 0
        gradient.set_derivative(2, Const(0.0))  # ∂obj/∂s(i2,k1) = 0

        J_eq = JacobianStructure(num_rows=3, num_cols=3, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))  # ∂objdef/∂obj
        # ∂stiffness(j1,k1)/∂s(i1,k1) = b(j1,i1)
        J_eq.set_derivative(1, 1, ParamRef("b", ("j1", "i1")))
        # ∂stiffness(j1,k1)/∂s(i2,k1) = b(j1,i2)
        J_eq.set_derivative(1, 2, ParamRef("b", ("j1", "i2")))
        # ∂stiffness(j2,k1)/∂s(i1,k1) = b(j2,i1)
        J_eq.set_derivative(2, 1, ParamRef("b", ("j2", "i1")))
        # ∂stiffness(j2,k1)/∂s(i2,k1) = b(j2,i2)
        J_eq.set_derivative(2, 2, ParamRef("b", ("j2", "i2")))

        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        # Add equality multiplier for stiffness(j,k)
        kkt.multipliers_eq["nu_stiffness"] = MultiplierDef(
            name="nu_stiffness", domain=("j", "k"), kind="eq", associated_constraint="stiffness"
        )

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        # Should have one indexed stationarity equation stat_s(i,k)
        assert "stat_s" in stationarity
        stat_eq = stationarity["stat_s"]
        assert stat_eq.domain == ("i", "k")

        # The stationarity expression should contain Sum(('j',), ...)
        # because we sum over the extra multiplier index 'j'
        lhs = stat_eq.lhs_rhs[0]

        def contains_sum_over_j(expr: Expr) -> bool:
            """Check if expression contains Sum with index 'j'."""
            match expr:
                case Sum(index_sets, body):
                    if "j" in index_sets:
                        return True
                    return contains_sum_over_j(body)
                case Binary(_, left, right):
                    return contains_sum_over_j(left) or contains_sum_over_j(right)
                case Unary(_, child):
                    return contains_sum_over_j(child)
                case _:
                    return False

        assert contains_sum_over_j(
            lhs
        ), f"Expected stationarity to contain sum over 'j' for cross-domain summation. Got: {lhs}"


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

    def test_multi_index_constraint_same_set(self, manual_index_mapping):
        """Test constraint with multiple indices from the same set (Issue #649).

        Simulates the himmel16 model case where constraint maxdist(i,j) has both
        indices from the same underlying set. The Jacobian derivative x(1) - x(2)
        should become x(i) - x(j), not x(i) - x(i).

        This tests the constraint-specific element-to-set mapping that maps elements
        to their position in the constraint domain, not just to the variable domain.
        """
        from src.ir.symbols import SetDef

        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        # Set with elements "1", "2", "3" (like himmel16's point indices)
        model.sets["i"] = SetDef(name="i", members=["1", "2", "3"])
        # Alias j for i (like himmel16's Alias(i,j))
        model.aliases["j"] = "i"

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ("i",))),
        )

        # Constraint maxdist(i,j) similar to himmel16:
        # maxdist(i,j).. sqr(x(i) - x(j)) =l= 1
        model.equations["maxdist"] = EquationDef(
            name="maxdist",
            domain=("i", "j"),
            relation=Rel.LE,
            lhs_rhs=(
                Call("sqr", (Binary("-", VarRef("x", ("i",)), VarRef("x", ("j",))),)),
                Const(1.0),
            ),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=("i",))

        model.equalities = ["objdef"]
        model.inequalities = ["maxdist"]

        # Set up index mapping with instances for x(i) and maxdist(i,j)
        # x(1), x(2), x(3) and maxdist(1,2), maxdist(1,3), maxdist(2,3)
        index_mapping = manual_index_mapping(
            [("obj", ()), ("x", ("1",)), ("x", ("2",)), ("x", ("3",))],
            [("objdef", ())],  # Only equality constraint for J_eq
        )

        # Create separate index mapping for inequalities
        ineq_index_mapping = manual_index_mapping(
            [("obj", ()), ("x", ("1",)), ("x", ("2",)), ("x", ("3",))],
            [("maxdist", ("1", "2")), ("maxdist", ("1", "3")), ("maxdist", ("2", "3"))],
        )

        gradient = GradientVector(num_cols=4, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))  # ∂obj/∂obj
        gradient.set_derivative(1, Const(1.0))  # ∂obj/∂x(1)
        gradient.set_derivative(2, Const(1.0))  # ∂obj/∂x(2)
        gradient.set_derivative(3, Const(1.0))  # ∂obj/∂x(3)

        J_eq = JacobianStructure(num_rows=1, num_cols=4, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))  # ∂objdef/∂obj

        # J_ineq: derivatives of maxdist(i,j) w.r.t. x(k)
        # d(sqr(x(1)-x(2)))/dx(1) = 2*(x(1)-x(2))
        # d(sqr(x(1)-x(2)))/dx(2) = -2*(x(1)-x(2)) = 2*(x(2)-x(1))
        J_ineq = JacobianStructure(num_rows=3, num_cols=4, index_mapping=ineq_index_mapping)
        # maxdist(1,2) row 0: derivatives w.r.t. x(1) and x(2)
        J_ineq.set_derivative(
            0, 1, Binary("*", Const(2.0), Binary("-", VarRef("x", ("1",)), VarRef("x", ("2",))))
        )
        J_ineq.set_derivative(
            0, 2, Binary("*", Const(2.0), Binary("-", VarRef("x", ("2",)), VarRef("x", ("1",))))
        )
        # maxdist(1,3) row 1
        J_ineq.set_derivative(
            1, 1, Binary("*", Const(2.0), Binary("-", VarRef("x", ("1",)), VarRef("x", ("3",))))
        )
        J_ineq.set_derivative(
            1, 3, Binary("*", Const(2.0), Binary("-", VarRef("x", ("3",)), VarRef("x", ("1",))))
        )
        # maxdist(2,3) row 2
        J_ineq.set_derivative(
            2, 2, Binary("*", Const(2.0), Binary("-", VarRef("x", ("2",)), VarRef("x", ("3",))))
        )
        J_ineq.set_derivative(
            2, 3, Binary("*", Const(2.0), Binary("-", VarRef("x", ("3",)), VarRef("x", ("2",))))
        )

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        kkt.multipliers_ineq["lam_maxdist"] = MultiplierDef(
            name="lam_maxdist",
            domain=("i", "j"),
            kind="ineq",
            associated_constraint="maxdist",
        )

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        assert "stat_x" in stationarity
        stat_eq = stationarity["stat_x"]

        # Find all VarRefs to x in the stationarity equation
        def find_var_refs(expr: Expr, var_name: str) -> list[VarRef]:
            """Recursively find all VarRef nodes for a specific variable."""
            refs = []
            match expr:
                case VarRef() if expr.name == var_name:
                    refs.append(expr)
                case Binary(_, left, right):
                    refs.extend(find_var_refs(left, var_name))
                    refs.extend(find_var_refs(right, var_name))
                case Unary(_, child):
                    refs.extend(find_var_refs(child, var_name))
                case Call(_, args):
                    for arg in args:
                        refs.extend(find_var_refs(arg, var_name))
                case Sum(_, body):
                    refs.extend(find_var_refs(body, var_name))
            return refs

        lhs = stat_eq.lhs_rhs[0]
        x_refs = find_var_refs(lhs, "x")

        # Check that we have VarRefs to both x(i) and x(j), not just x(i)
        indices_found = {ref.indices_as_strings() for ref in x_refs}

        # The stationarity equation should contain x(i) - x(j) terms
        # from the Jacobian transpose, so we expect both ("i",) and ("j",)
        assert ("i",) in indices_found, f"Expected x(i) in stationarity, found {indices_found}"
        assert ("j",) in indices_found, (
            f"Expected x(j) in stationarity (not x(i)-x(i)), found {indices_found}. "
            "Issue #649: constraint-specific element mapping may be broken."
        )


@pytest.mark.integration
class TestStationaritySubsetSupersetIndex:
    """Test correct index substitution when variable domain is a subset of parameter domain.

    GitHub Issue #620: Stationarity equation uses uncontrolled index variable.
    When a variable x(i) has domain i(s) (subset of s), and a parameter mu(s)
    is referenced in the stationarity equation stat_x(i), the index 's' must be
    replaced with 'i' to avoid GAMS Error 149 "Set is not under control".
    """

    def test_superset_index_replaced_with_subset(self, manual_index_mapping):
        """Test that mu(s) becomes mu(i) in stat_x(i) when i is a subset of s.

        Simulates the meanvar model case:
        - Set s: {cn, fr, gr, jp, sw, uk, us, wr}
        - Set i(s): {cn, fr, gr, jp, sw, uk, us} (subset of s)
        - Parameter mu(s): expected returns defined over superset
        - Variable x(i): portfolio fractions defined over subset
        - Constraint mbal.. m =e= sum(i, mu(i)*x(i))

        The stationarity for x(i) includes terms from mbal with mu(s).
        The fix must replace mu(s) → mu(i) since i ⊆ s.
        """
        from src.ir.symbols import ParameterDef, SetDef

        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        # Sets: s is superset, i(s) is subset
        model.sets["s"] = SetDef(name="s", members=["cn", "fr", "us"])
        model.sets["i"] = SetDef(name="i", members=["cn", "fr"], domain=("s",))

        # Parameter mu(s) defined over superset
        model.params["mu"] = ParameterDef(
            name="mu",
            domain=("s",),
            values={("cn",): 0.1287, ("fr",): 0.1096, ("us",): 0.062},
        )

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ("i",))),
        )

        # mbal.. m =e= sum(i, mu(i)*x(i))
        model.equations["mbal"] = EquationDef(
            name="mbal",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("m", ()),
                Sum(("i",), Binary("*", ParamRef("mu", ("i",)), VarRef("x", ("i",)))),
            ),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["m"] = VariableDef(name="m", domain=())
        model.variables["x"] = VariableDef(name="x", domain=("i",))

        model.equalities = ["objdef", "mbal"]

        # Set up KKT system
        index_mapping = manual_index_mapping(
            [("obj", ()), ("m", ()), ("x", ("cn",)), ("x", ("fr",))],
            [("objdef", ()), ("mbal", ())],
        )

        gradient = GradientVector(num_cols=4, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))  # ∂obj/∂obj
        gradient.set_derivative(1, Const(0.0))  # ∂obj/∂m
        gradient.set_derivative(2, Const(0.0))  # ∂obj/∂x(cn)
        gradient.set_derivative(3, Const(0.0))  # ∂obj/∂x(fr)

        J_eq = JacobianStructure(num_rows=2, num_cols=4, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))  # ∂objdef/∂obj
        # ∂mbal/∂x(cn) = mu("cn") - uses element label from the superset s
        J_eq.set_derivative(1, 2, ParamRef("mu", ("cn",)))
        # ∂mbal/∂x(fr) = mu("fr")
        J_eq.set_derivative(1, 3, ParamRef("mu", ("fr",)))

        J_ineq = JacobianStructure(num_rows=0, num_cols=4, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        kkt.multipliers_eq["nu_mbal"] = MultiplierDef(
            name="nu_mbal", domain=(), kind="eq", associated_constraint="mbal"
        )

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        assert "stat_x" in stationarity
        stat_eq = stationarity["stat_x"]
        assert stat_eq.domain == ("i",)

        # Find all ParamRef nodes in the stationarity expression
        def find_param_refs(expr: Expr) -> list[ParamRef]:
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

        # Find references to parameter 'mu'
        mu_refs = [ref for ref in param_refs if ref.name == "mu"]
        assert len(mu_refs) > 0, "Expected parameter 'mu' in stationarity equation"

        # All mu references should use 'i' (subset), not 's' (superset)
        for ref in mu_refs:
            indices = ref.indices_as_strings()
            assert indices == ("i",), (
                f"Expected mu(i) but got mu{indices}. "
                "Superset index 's' was not replaced with subset index 'i'. "
                "This causes GAMS Error 149."
            )

    def test_non_subset_set_preserved(self, manual_index_mapping):
        """Test that set names that are NOT supersets of the equation domain are preserved.

        When a parameter uses a set that has no subset relationship with the
        equation domain, the index should remain unchanged.
        """
        from src.ir.symbols import ParameterDef, SetDef

        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        # Sets: i and k are independent (no subset relationship)
        model.sets["i"] = SetDef(name="i", members=["i1", "i2"])
        model.sets["k"] = SetDef(name="k", members=["k1", "k2"])

        # Parameter p(k) defined over independent set k
        model.params["p"] = ParameterDef(
            name="p", domain=("k",), values={("k1",): 1.0, ("k2",): 2.0}
        )

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ("i",))),
        )

        # constraint.. sum(i, p(k)*x(i)) would be unusual but tests preservation
        model.equations["con"] = EquationDef(
            name="con",
            domain=("k",),
            relation=Rel.EQ,
            lhs_rhs=(
                Sum(("i",), Binary("*", ParamRef("p", ("k",)), VarRef("x", ("i",)))),
                Const(1.0),
            ),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=("i",))

        model.equalities = ["objdef", "con"]

        index_mapping = manual_index_mapping(
            [("obj", ()), ("x", ("i1",)), ("x", ("i2",))],
            [("objdef", ()), ("con", ("k1",)), ("con", ("k2",))],
        )

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(0.0))
        gradient.set_derivative(2, Const(0.0))

        J_eq = JacobianStructure(num_rows=3, num_cols=3, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))
        # ∂con(k1)/∂x(i1) = p("k1")
        J_eq.set_derivative(1, 1, ParamRef("p", ("k1",)))
        J_eq.set_derivative(1, 2, ParamRef("p", ("k1",)))
        J_eq.set_derivative(2, 1, ParamRef("p", ("k2",)))
        J_eq.set_derivative(2, 2, ParamRef("p", ("k2",)))

        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        kkt.multipliers_eq["nu_con"] = MultiplierDef(
            name="nu_con", domain=("k",), kind="eq", associated_constraint="con"
        )

        stationarity = build_stationarity_equations(kkt)

        assert "stat_x" in stationarity

        def find_param_refs(expr: Expr) -> list[ParamRef]:
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

        lhs = stationarity["stat_x"].lhs_rhs[0]
        p_refs = [ref for ref in find_param_refs(lhs) if ref.name == "p"]

        # p(k) should remain p(k), not be changed to p(i)
        for ref in p_refs:
            indices = ref.indices_as_strings()
            assert "k" in indices, (
                f"Expected p(k) to be preserved but got p{indices}. "
                "Non-subset set 'k' should not be replaced."
            )


@pytest.mark.integration
class TestStationaritySubsetVariableDomain:
    """Test correct index handling when variable is defined over a subset.

    GitHub Issue #666: KKT generation domain mismatch when variable domain
    differs from equation domain.

    When a variable like h(t) is defined over a subset t(i), and it appears
    in the stationarity equation stat_e(i) (where e is defined over superset i),
    the variable reference must preserve h(t), not become h(i).
    """

    def test_subset_variable_preserved_in_stationarity(self, manual_index_mapping):
        """Test that h(t) stays h(t) in stat_e(i) when t is a subset of i.

        Simulates the chenery model case:
        - Set i: {light-ind, food+agr, heavy-ind, services} (all sectors)
        - Set t(i): {light-ind, food+agr, heavy-ind} (tradables, subset of i)
        - Variable e(i): exports defined over all sectors
        - Variable h(t): foreign exchange value, defined only over tradables
        - Constraint tb: sum(t, g(t)*m(t) - h(t)*e(t)) =l= dbar

        The stationarity for e(i) includes derivative term h(t).
        This must remain h(t), not become h(i) which would cause GAMS Error 170.
        """
        from src.ir.symbols import SetDef

        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        # Sets: i is superset, t(i) is subset (tradables)
        model.sets["i"] = SetDef(
            name="i", members=["light-ind", "food+agr", "heavy-ind", "services"]
        )
        model.sets["t"] = SetDef(
            name="t", members=["light-ind", "food+agr", "heavy-ind"], domain=("i",)
        )

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("e", ("i",))),
        )

        # tb.. sum(t, h(t)*e(t)) =l= dbar (simplified - just h(t)*e(t) term)
        model.equations["tb"] = EquationDef(
            name="tb",
            domain=(),
            relation=Rel.LE,
            lhs_rhs=(
                Sum(("t",), Binary("*", VarRef("h", ("t",)), VarRef("e", ("t",)))),
                Const(0.0),
            ),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["e"] = VariableDef(name="e", domain=("i",))  # superset domain
        model.variables["h"] = VariableDef(name="h", domain=("t",))  # subset domain

        model.equalities = ["objdef"]
        model.inequalities = ["tb"]

        # Set up KKT system with e(i) instances (4 elements)
        index_mapping = manual_index_mapping(
            [
                ("obj", ()),
                ("e", ("light-ind",)),
                ("e", ("food+agr",)),
                ("e", ("heavy-ind",)),
                ("e", ("services",)),
                ("h", ("light-ind",)),
                ("h", ("food+agr",)),
                ("h", ("heavy-ind",)),
            ],
            [("objdef", ())],
        )

        # Separate mapping for inequalities
        ineq_index_mapping = manual_index_mapping(
            [
                ("obj", ()),
                ("e", ("light-ind",)),
                ("e", ("food+agr",)),
                ("e", ("heavy-ind",)),
                ("e", ("services",)),
                ("h", ("light-ind",)),
                ("h", ("food+agr",)),
                ("h", ("heavy-ind",)),
            ],
            [("tb", ())],
        )

        gradient = GradientVector(num_cols=8, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))  # ∂obj/∂obj
        # Gradient for e instances - simplified
        for col in range(1, 5):
            gradient.set_derivative(col, Const(0.0))
        # Gradient for h instances
        for col in range(5, 8):
            gradient.set_derivative(col, Const(0.0))

        J_eq = JacobianStructure(num_rows=1, num_cols=8, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))  # ∂objdef/∂obj

        # J_ineq: ∂tb/∂e(t) = h(t) for tradables only
        # tb = sum(t, h(t)*e(t)), so ∂tb/∂e(light-ind) = h(light-ind)
        J_ineq = JacobianStructure(num_rows=1, num_cols=8, index_mapping=ineq_index_mapping)
        # Derivatives w.r.t. e (cols 1-4), but only tradables contribute
        J_ineq.set_derivative(0, 1, VarRef("h", ("light-ind",)))  # ∂tb/∂e(light-ind)
        J_ineq.set_derivative(0, 2, VarRef("h", ("food+agr",)))  # ∂tb/∂e(food+agr)
        J_ineq.set_derivative(0, 3, VarRef("h", ("heavy-ind",)))  # ∂tb/∂e(heavy-ind)
        # e(services) doesn't appear in tb, no derivative

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        kkt.multipliers_ineq["lam_tb"] = MultiplierDef(
            name="lam_tb", domain=(), kind="ineq", associated_constraint="tb"
        )

        # Build stationarity
        stationarity = build_stationarity_equations(kkt)

        assert "stat_e" in stationarity
        stat_eq = stationarity["stat_e"]
        assert stat_eq.domain == ("i",)  # Stationarity indexed over superset

        # Find all VarRefs to h in the stationarity equation
        def find_var_refs(expr: Expr, var_name: str) -> list[VarRef]:
            """Recursively find all VarRef nodes for a specific variable."""
            refs = []
            match expr:
                case VarRef() if expr.name == var_name:
                    refs.append(expr)
                case Binary(_, left, right):
                    refs.extend(find_var_refs(left, var_name))
                    refs.extend(find_var_refs(right, var_name))
                case Unary(_, child):
                    refs.extend(find_var_refs(child, var_name))
                case Call(_, args):
                    for arg in args:
                        refs.extend(find_var_refs(arg, var_name))
                case Sum(_, body):
                    refs.extend(find_var_refs(body, var_name))
            return refs

        lhs = stat_eq.lhs_rhs[0]
        h_refs = find_var_refs(lhs, "h")

        # All h references must use 't' (subset), not 'i' (superset)
        # This is the key assertion for Issue #666
        # Note: h(i) is NOT acceptable because h is only defined over subset t.
        # Using h(i) would cause GAMS Error 170 (domain violation) for elements
        # like 'services' that are in i but not in t. The index t is controlled
        # via the original sum(t, ...) in the constraint tb.
        for ref in h_refs:
            indices = ref.indices_as_strings()
            assert indices == ("t",), (
                f"Expected h(t) but got h{indices}. "
                "Issue #666: Variable h is defined over subset t, so h(i) would cause "
                "GAMS Error 170 for elements not in t. Must preserve h(t)."
            )

    def test_superset_variable_uses_equation_domain(self, manual_index_mapping):
        """Test that e(i) uses i in stat_e(i) - normal case for superset variables."""
        from src.ir.symbols import SetDef

        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.sets["i"] = SetDef(name="i", members=["a", "b"])

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ("i",))),
        )

        model.equations["con"] = EquationDef(
            name="con",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(Sum(("i",), VarRef("x", ("i",))), Const(1.0)),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=("i",))

        model.equalities = ["objdef", "con"]

        index_mapping = manual_index_mapping(
            [("obj", ()), ("x", ("a",)), ("x", ("b",))],
            [("objdef", ()), ("con", ())],
        )

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(0.0))
        gradient.set_derivative(2, Const(0.0))

        J_eq = JacobianStructure(num_rows=2, num_cols=3, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))
        J_eq.set_derivative(1, 1, Const(1.0))  # ∂con/∂x(a)
        J_eq.set_derivative(1, 2, Const(1.0))  # ∂con/∂x(b)

        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        kkt.multipliers_eq["nu_con"] = MultiplierDef(
            name="nu_con", domain=(), kind="eq", associated_constraint="con"
        )

        stationarity = build_stationarity_equations(kkt)

        assert "stat_x" in stationarity
        assert stationarity["stat_x"].domain == ("i",)

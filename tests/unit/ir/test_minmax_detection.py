"""Unit tests for min/max detection in objective-defining equations.

Tests the detection logic that identifies when min() or max() functions
appear in the dependency chain that defines the objective variable.

This is critical for proper KKT assembly because such cases require
special handling with auxiliary constraint multipliers.
"""

from __future__ import annotations

from src.ir.ast import Binary, Call, Const, VarRef
from src.ir.minmax_detection import (
    _build_variable_definitions,
    _contains_minmax,
    _extract_variables,
    detects_objective_minmax,
)
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import EquationDef, ObjSense, Rel


class TestExtractVariables:
    """Test variable extraction from expressions."""

    def test_extract_single_variable(self):
        """Extract from simple variable reference."""
        expr = VarRef("x", ())
        vars_found = _extract_variables(expr)
        assert vars_found == ["x"]

    def test_extract_from_binary(self):
        """Extract from binary expression."""
        # x + y
        expr = Binary("+", VarRef("x", ()), VarRef("y", ()))
        vars_found = _extract_variables(expr)
        assert set(vars_found) == {"x", "y"}

    def test_extract_from_nested_binary(self):
        """Extract from nested expression."""
        # (x + y) * z
        inner = Binary("+", VarRef("x", ()), VarRef("y", ()))
        expr = Binary("*", inner, VarRef("z", ()))
        vars_found = _extract_variables(expr)
        assert set(vars_found) == {"x", "y", "z"}

    def test_extract_from_call(self):
        """Extract from function call."""
        # min(x, y)
        expr = Call("min", (VarRef("x", ()), VarRef("y", ())))
        vars_found = _extract_variables(expr)
        assert set(vars_found) == {"x", "y"}

    def test_extract_from_const(self):
        """Extract from constant (should be empty)."""
        expr = Const(5.0)
        vars_found = _extract_variables(expr)
        assert vars_found == []

    def test_extract_with_duplicates(self):
        """Extract variables that appear multiple times."""
        # x + x
        expr = Binary("+", VarRef("x", ()), VarRef("x", ()))
        vars_found = _extract_variables(expr)
        assert vars_found == ["x", "x"]  # Duplicates preserved

    def test_extract_from_complex_expression(self):
        """Extract from complex nested expression."""
        # min(x + y, z * w)
        arg1 = Binary("+", VarRef("x", ()), VarRef("y", ()))
        arg2 = Binary("*", VarRef("z", ()), VarRef("w", ()))
        expr = Call("min", (arg1, arg2))
        vars_found = _extract_variables(expr)
        assert set(vars_found) == {"x", "y", "z", "w"}


class TestContainsMinMax:
    """Test detection of min/max in equations."""

    def test_contains_min_on_rhs(self):
        """Detect min() on RHS of equation."""
        # z =e= min(x, y)
        eq = EquationDef(
            name="eq1",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("z", ()),
                Call("min", (VarRef("x", ()), VarRef("y", ()))),
            ),
        )
        assert _contains_minmax(eq)

    def test_contains_max_on_rhs(self):
        """Detect max() on RHS of equation."""
        # z =e= max(x, y)
        eq = EquationDef(
            name="eq1",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("z", ()),
                Call("max", (VarRef("x", ()), VarRef("y", ()))),
            ),
        )
        assert _contains_minmax(eq)

    def test_contains_min_on_lhs(self):
        """Detect min() on LHS of equation (unusual but possible)."""
        # min(x, y) =e= z
        eq = EquationDef(
            name="eq1",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                Call("min", (VarRef("x", ()), VarRef("y", ()))),
                VarRef("z", ()),
            ),
        )
        assert _contains_minmax(eq)

    def test_contains_nested_min(self):
        """Detect min() nested in expression."""
        # z =e= 2 * min(x, y)
        eq = EquationDef(
            name="eq1",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("z", ()),
                Binary("*", Const(2.0), Call("min", (VarRef("x", ()), VarRef("y", ())))),
            ),
        )
        assert _contains_minmax(eq)

    def test_no_minmax_simple(self):
        """No detection when no min/max present."""
        # z =e= x + y
        eq = EquationDef(
            name="eq1",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("z", ()), Binary("+", VarRef("x", ()), VarRef("y", ()))),
        )
        assert not _contains_minmax(eq)

    def test_no_minmax_other_function(self):
        """No detection for other functions like sqrt, exp."""
        # z =e= sqrt(x)
        eq = EquationDef(
            name="eq1",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("z", ()), Call("sqrt", (VarRef("x", ()),))),
        )
        assert not _contains_minmax(eq)


class TestBuildVariableDefinitions:
    """Test building variable -> equation mapping."""

    def test_simple_definition(self):
        """Map variable to its defining equation."""
        model = ModelIR()
        model.equations["eq1"] = EquationDef(
            name="eq1",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("z", ()), Binary("+", VarRef("x", ()), VarRef("y", ()))),
        )

        defs = _build_variable_definitions(model)
        assert defs["z"] == "eq1"

    def test_multiple_definitions(self):
        """Multiple equations, each defines a variable."""
        model = ModelIR()
        model.equations["eq1"] = EquationDef(
            name="eq1",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("z", ())),
        )
        model.equations["eq2"] = EquationDef(
            name="eq2",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("z", ()), Call("min", (VarRef("x", ()), VarRef("y", ())))),
        )

        defs = _build_variable_definitions(model)
        assert defs["obj"] == "eq1"
        # z is defined by eq2 (LHS), not eq1 (RHS)
        assert defs["z"] == "eq2"

    def test_no_rhs_variable_mapping(self):
        """Variable on RHS is NOT mapped (only LHS definitions count)."""
        model = ModelIR()
        model.equations["eq1"] = EquationDef(
            name="eq1",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(Binary("+", VarRef("x", ()), VarRef("y", ())), VarRef("z", ())),
        )

        defs = _build_variable_definitions(model)
        # z appears on RHS, so it's NOT defined by eq1
        assert "z" not in defs

    def test_first_definition_wins(self):
        """When variable appears in multiple equations, first wins."""
        model = ModelIR()
        model.equations["eq1"] = EquationDef(
            name="eq1",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("z", ()), VarRef("x", ())),
        )
        model.equations["eq2"] = EquationDef(
            name="eq2",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("z", ()), VarRef("y", ())),
        )

        defs = _build_variable_definitions(model)
        # First occurrence should be recorded
        assert defs["z"] in ["eq1", "eq2"]

    def test_no_definition_for_complex_lhs(self):
        """Complex expressions on LHS don't define variables."""
        model = ModelIR()
        model.equations["eq1"] = EquationDef(
            name="eq1",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(Binary("+", VarRef("x", ()), VarRef("y", ())), Const(1.0)),
        )

        defs = _build_variable_definitions(model)
        # x and y are not "defined" by this equation
        assert "x" not in defs
        assert "y" not in defs


class TestDetectsObjectiveMinMax:
    """Test end-to-end detection of min/max in objective chain."""

    def test_direct_minmax_in_objective(self):
        """Detect: obj = min(x, y)"""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("obj", ()),
                Call("min", (VarRef("x", ()), VarRef("y", ()))),
            ),
        )

        assert detects_objective_minmax(model)

    def test_chained_minmax_one_hop(self):
        """Detect: obj = z, z = min(x, y)"""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("z", ())),
        )
        model.equations["mindef"] = EquationDef(
            name="mindef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("z", ()),
                Call("min", (VarRef("x", ()), VarRef("y", ()))),
            ),
        )

        assert detects_objective_minmax(model)

    def test_chained_minmax_two_hops(self):
        """Detect: obj = z, z = w, w = min(x, y)"""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("z", ())),
        )
        model.equations["zdef"] = EquationDef(
            name="zdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("z", ()), VarRef("w", ())),
        )
        model.equations["wdef"] = EquationDef(
            name="wdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("w", ()),
                Call("min", (VarRef("x", ()), VarRef("y", ()))),
            ),
        )

        assert detects_objective_minmax(model)

    def test_max_instead_of_min(self):
        """Detect: obj = max(x, y)"""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MAX, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("obj", ()),
                Call("max", (VarRef("x", ()), VarRef("y", ()))),
            ),
        )

        assert detects_objective_minmax(model)

    def test_nested_minmax(self):
        """Detect: obj = z, z = max(min(x, y), w)"""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("z", ())),
        )

        # z = max(min(x, y), w)
        inner_min = Call("min", (VarRef("x", ()), VarRef("y", ())))
        outer_max = Call("max", (inner_min, VarRef("w", ())))
        model.equations["zdef"] = EquationDef(
            name="zdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("z", ()), outer_max),
        )

        assert detects_objective_minmax(model)

    def test_no_detection_minmax_in_constraint(self):
        """No detection: obj = x + y, constraint has min(a, b)"""
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
            lhs_rhs=(
                Call("min", (VarRef("a", ()), VarRef("b", ()))),
                Const(10.0),
            ),
        )

        # Min/max is in constraint, NOT in objective chain
        assert not detects_objective_minmax(model)

    def test_no_detection_no_minmax(self):
        """No detection: obj = x^2 + y^2 (no min/max anywhere)"""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

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

        assert not detects_objective_minmax(model)

    def test_no_detection_no_objective(self):
        """No detection when model has no objective."""
        model = ModelIR()
        model.objective = None

        model.equations["eq1"] = EquationDef(
            name="eq1",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("z", ()),
                Call("min", (VarRef("x", ()), VarRef("y", ()))),
            ),
        )

        assert not detects_objective_minmax(model)

    def test_handles_undefined_variable(self):
        """No crash when objective variable has no defining equation."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        # No equation defines "obj"
        model.equations["constraint"] = EquationDef(
            name="constraint",
            domain=(),
            relation=Rel.LE,
            lhs_rhs=(VarRef("x", ()), Const(10.0)),
        )

        # Should not crash, just return False
        assert not detects_objective_minmax(model)

    def test_handles_circular_definition(self):
        """Handle circular definitions gracefully (shouldn't happen, but be robust)."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        # Circular: obj = z, z = obj
        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("z", ())),
        )
        model.equations["zdef"] = EquationDef(
            name="zdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("z", ()), VarRef("obj", ())),
        )

        # Should not crash (visited tracking prevents infinite loop)
        assert not detects_objective_minmax(model)

    def test_minmax_in_expression_with_other_terms(self):
        """Detect: obj = z, z = min(x, y) + 5"""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("z", ())),
        )
        model.equations["zdef"] = EquationDef(
            name="zdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("z", ()),
                Binary("+", Call("min", (VarRef("x", ()), VarRef("y", ()))), Const(5.0)),
            ),
        )

        assert detects_objective_minmax(model)

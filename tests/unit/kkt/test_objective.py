"""Unit tests for objective variable detection."""

import pytest

from src.ir.ast import Binary, Const, SymbolRef, VarRef
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import EquationDef, ObjSense, Rel, VariableDef
from src.kkt.objective import extract_objective_info


@pytest.mark.unit
class TestExtractObjectiveInfo:
    """Tests for extract_objective_info function."""

    def test_no_objective_raises(self):
        """Model without objective should raise ValueError."""
        model = ModelIR()

        with pytest.raises(ValueError, match="Model has no objective"):
            extract_objective_info(model)

    def test_objective_on_lhs(self):
        """Objective variable on LHS of defining equation."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        # obj =E= x + y
        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("obj", ()),
                Binary("+", VarRef("x", ()), VarRef("y", ())),
            ),
        )

        result = extract_objective_info(model)

        assert result.objvar == "obj"
        assert result.defining_equation == "objdef"
        assert result.needs_stationarity is False

    def test_objective_on_rhs(self):
        """Objective variable on RHS of defining equation."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MAX, objvar="z")

        # x + y =E= z
        model.equations["zdef"] = EquationDef(
            name="zdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                Binary("+", VarRef("x", ()), VarRef("y", ())),
                VarRef("z", ()),
            ),
        )

        result = extract_objective_info(model)

        assert result.objvar == "z"
        assert result.defining_equation == "zdef"

    def test_no_defining_equation_raises(self):
        """Model without defining equation should raise ValueError."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        # No equations defined

        with pytest.raises(ValueError, match="Could not find defining equation"):
            extract_objective_info(model)

    def test_wrong_equation_not_matched(self):
        """Equation that doesn't define objective should not match."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        # balance.. x + y =E= 0  (doesn't define obj)
        model.equations["balance"] = EquationDef(
            name="balance",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                Binary("+", VarRef("x", ()), VarRef("y", ())),
                Const(0.0),
            ),
        )

        with pytest.raises(ValueError, match="Could not find defining equation"):
            extract_objective_info(model)

    def test_multiple_equations_finds_correct_one(self):
        """Should find the correct defining equation among multiple."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="cost")

        # balance.. x + y =E= 10
        model.equations["balance"] = EquationDef(
            name="balance",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                Binary("+", VarRef("x", ()), VarRef("y", ())),
                Const(10.0),
            ),
        )

        # costdef.. cost =E= 2*x + 3*y
        model.equations["costdef"] = EquationDef(
            name="costdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("cost", ()),
                Binary(
                    "+",
                    Binary("*", Const(2.0), VarRef("x", ())),
                    Binary("*", Const(3.0), VarRef("y", ())),
                ),
            ),
        )

        result = extract_objective_info(model)

        assert result.objvar == "cost"
        assert result.defining_equation == "costdef"

    def test_objvar_indices_empty(self):
        """Objective variable indices should be empty tuple."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ())),
        )

        result = extract_objective_info(model)

        assert result.objvar_indices == ()

    def test_needs_stationarity_is_false(self):
        """For standard NLP->MCP, objvar should not need stationarity."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ())),
        )

        result = extract_objective_info(model)

        assert result.needs_stationarity is False

    def test_case_insensitive_objvar_lhs(self):
        """GAMS is case-insensitive - 'f' should match equation with 'F'.

        This pattern appears in models like alkyl (objvar='f', equation LHS='F').
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="f")  # lowercase

        # F =E= x^2 (uppercase in equation using SymbolRef)
        model.equations["obj_def"] = EquationDef(
            name="obj_def",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                SymbolRef("F"),  # uppercase
                Binary("*", VarRef("x", ()), VarRef("x", ())),
            ),
        )

        result = extract_objective_info(model)

        assert result.objvar == "f"
        assert result.defining_equation == "obj_def"

    def test_case_insensitive_objvar_rhs(self):
        """GAMS is case-insensitive - should also work when objvar is on RHS."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")  # lowercase

        # x^2 =E= OBJ (uppercase in equation)
        model.equations["obj_def"] = EquationDef(
            name="obj_def",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                Binary("*", VarRef("x", ()), VarRef("x", ())),
                SymbolRef("OBJ"),  # uppercase
            ),
        )

        result = extract_objective_info(model)

        assert result.objvar == "obj"
        assert result.defining_equation == "obj_def"

    def test_simple_variable_objective(self):
        """Objective that is just a variable with no defining equation.

        This handles 'minimize r' where r is a free variable with no equation
        defining it. Common in models like circle, cpack.
        """
        model = ModelIR()
        model.add_var(VariableDef("r", ()))
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="r")
        # No equations defining r

        result = extract_objective_info(model)

        assert result.objvar == "r"
        assert result.defining_equation == ""  # No defining equation
        assert result.needs_stationarity is True  # Stationarity needed for simple var

    def test_simple_variable_objective_case_insensitive(self):
        """Simple variable objective with case mismatch.

        Handles 'minimize RADIUS' when variable is declared as 'radius'.
        """
        model = ModelIR()
        model.add_var(VariableDef("radius", ()))  # lowercase
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="RADIUS")  # uppercase

        result = extract_objective_info(model)

        assert result.objvar == "RADIUS"  # Preserves original objvar case
        assert result.defining_equation == ""
        assert result.needs_stationarity is True

    def test_objvar_not_variable_raises_error(self):
        """Error when objvar is neither defined by equation nor a variable."""
        model = ModelIR()
        model.add_var(VariableDef("x", ()))  # Different variable
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        # obj is not defined by equation and not a declared variable

        with pytest.raises(ValueError, match="Could not find defining equation"):
            extract_objective_info(model)

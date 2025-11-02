"""Unit tests for min/max reformulation infrastructure."""

from __future__ import annotations

import pytest

from src.ir.ast import Binary, Call, Const, VarRef
from src.ir.symbols import Rel
from src.kkt.reformulation import (
    AuxiliaryVariableManager,
    MinMaxCall,
    detect_min_max_calls,
    flatten_min_max_args,
    is_min_or_max_call,
)


class TestMinMaxDetection:
    """Test detection of min/max function calls."""

    def test_is_min_call(self):
        """Test detection of min() calls."""
        expr = Call("min", (VarRef("x"), VarRef("y")))
        assert is_min_or_max_call(expr)

    def test_is_max_call(self):
        """Test detection of max() calls."""
        expr = Call("max", (VarRef("x"), VarRef("y")))
        assert is_min_or_max_call(expr)

    def test_is_min_case_insensitive(self):
        """Test case-insensitive detection."""
        expr_lower = Call("min", (VarRef("x"),))
        expr_upper = Call("MIN", (VarRef("x"),))
        expr_mixed = Call("Min", (VarRef("x"),))

        assert is_min_or_max_call(expr_lower)
        assert is_min_or_max_call(expr_upper)
        assert is_min_or_max_call(expr_mixed)

    def test_not_min_or_max(self):
        """Test that other functions are not detected."""
        expr_exp = Call("exp", (VarRef("x"),))
        expr_sqrt = Call("sqrt", (VarRef("x"),))
        expr_var = VarRef("x")

        assert not is_min_or_max_call(expr_exp)
        assert not is_min_or_max_call(expr_sqrt)
        assert not is_min_or_max_call(expr_var)

    def test_detect_simple_min(self):
        """Test detection of simple min(x, y)."""
        expr = Call("min", (VarRef("x"), VarRef("y")))
        calls = detect_min_max_calls(expr, "objdef")

        assert len(calls) == 1
        assert calls[0].func_type == "min"
        assert len(calls[0].args) == 2
        assert calls[0].context == "objdef"
        assert calls[0].index == 0

    def test_detect_simple_max(self):
        """Test detection of simple max(x, y)."""
        expr = Call("max", (VarRef("x"), VarRef("y")))
        calls = detect_min_max_calls(expr, "constraint1")

        assert len(calls) == 1
        assert calls[0].func_type == "max"
        assert len(calls[0].args) == 2

    def test_detect_multiple_min_max(self):
        """Test detection of multiple min/max in same expression."""
        # min(x, y) + max(a, b)
        expr = Binary(
            "+",
            Call("min", (VarRef("x"), VarRef("y"))),
            Call("max", (VarRef("a"), VarRef("b"))),
        )
        calls = detect_min_max_calls(expr, "eq1")

        assert len(calls) == 2
        assert calls[0].func_type == "min"
        assert calls[0].index == 0
        assert calls[1].func_type == "max"
        assert calls[1].index == 1

    def test_detect_no_min_max(self):
        """Test that expressions without min/max return empty list."""
        expr = Binary("+", VarRef("x"), Const(5.0))
        calls = detect_min_max_calls(expr, "eq1")

        assert len(calls) == 0


class TestFlattening:
    """Test flattening of nested min/max calls."""

    def test_flatten_simple_min(self):
        """Test that simple min is not changed."""
        expr = Call("min", (VarRef("x"), VarRef("y")))
        flattened = flatten_min_max_args(expr)

        assert len(flattened) == 2
        assert isinstance(flattened[0], VarRef)
        assert isinstance(flattened[1], VarRef)

    def test_flatten_nested_min(self):
        """Test flattening nested min(min(x, y), z)."""
        inner = Call("min", (VarRef("x"), VarRef("y")))
        outer = Call("min", (inner, VarRef("z")))
        flattened = flatten_min_max_args(outer)

        assert len(flattened) == 3
        # Should have x, y, z as separate arguments
        assert all(isinstance(arg, VarRef) for arg in flattened)

    def test_flatten_deeply_nested_min(self):
        """Test flattening min(min(min(a, b), c), d)."""
        inner1 = Call("min", (VarRef("a"), VarRef("b")))
        inner2 = Call("min", (inner1, VarRef("c")))
        outer = Call("min", (inner2, VarRef("d")))
        flattened = flatten_min_max_args(outer)

        assert len(flattened) == 4

    def test_flatten_mixed_max(self):
        """Test that max(max(x, y), z) flattens correctly."""
        inner = Call("max", (VarRef("x"), VarRef("y")))
        outer = Call("max", (inner, VarRef("z")))
        flattened = flatten_min_max_args(outer)

        assert len(flattened) == 3

    def test_flatten_preserves_non_min_max(self):
        """Test that non-min/max expressions in arguments are preserved."""
        # min(x + 2, sqrt(y), z)
        expr = Call(
            "min",
            (
                Binary("+", VarRef("x"), Const(2.0)),
                Call("sqrt", (VarRef("y"),)),
                VarRef("z"),
            ),
        )
        flattened = flatten_min_max_args(expr)

        assert len(flattened) == 3
        assert isinstance(flattened[0], Binary)  # x + 2 preserved
        assert isinstance(flattened[1], Call)  # sqrt(y) preserved
        assert isinstance(flattened[2], VarRef)  # z

    def test_flatten_does_not_mix_min_max(self):
        """Test that min(max(x, y), z) does NOT flatten max."""
        # min and max are different functions, should not flatten across them
        inner_max = Call("max", (VarRef("x"), VarRef("y")))
        outer_min = Call("min", (inner_max, VarRef("z")))
        flattened = flatten_min_max_args(outer_min)

        assert len(flattened) == 2
        # First arg should still be max call, not flattened
        assert isinstance(flattened[0], Call)
        assert flattened[0].func == "max"
        assert isinstance(flattened[1], VarRef)

    def test_flatten_multiple_nested_levels(self):
        """Test min(min(a, min(b, c)), d)."""
        inner2 = Call("min", (VarRef("b"), VarRef("c")))
        inner1 = Call("min", (VarRef("a"), inner2))
        outer = Call("min", (inner1, VarRef("d")))
        flattened = flatten_min_max_args(outer)

        assert len(flattened) == 4


class TestAuxiliaryVariableNaming:
    """Test auxiliary variable name generation."""

    def test_generate_min_name(self):
        """Test name generation for min auxiliary variable."""
        manager = AuxiliaryVariableManager()
        name = manager.generate_name("min", "objdef")

        assert name == "aux_min_objdef_0"

    def test_generate_max_name(self):
        """Test name generation for max auxiliary variable."""
        manager = AuxiliaryVariableManager()
        name = manager.generate_name("max", "constraint1")

        assert name == "aux_max_constraint1_0"

    def test_generate_multiple_names_same_context(self):
        """Test that multiple calls in same context get different indices."""
        manager = AuxiliaryVariableManager()
        name1 = manager.generate_name("min", "eq1")
        name2 = manager.generate_name("min", "eq1")
        name3 = manager.generate_name("max", "eq1")

        assert name1 == "aux_min_eq1_0"
        assert name2 == "aux_min_eq1_1"
        assert name3 == "aux_max_eq1_0"  # max has separate counter

    def test_generate_names_different_contexts(self):
        """Test that different contexts have independent counters."""
        manager = AuxiliaryVariableManager()
        name1 = manager.generate_name("min", "eq1")
        name2 = manager.generate_name("min", "eq2")

        assert name1 == "aux_min_eq1_0"
        assert name2 == "aux_min_eq2_0"

    def test_collision_detection(self):
        """Test that collision with user variables raises error."""
        manager = AuxiliaryVariableManager()
        manager.register_user_variables({"aux_min_objdef_0"})

        with pytest.raises(ValueError, match="collides with user variable"):
            manager.generate_name("min", "objdef")

    def test_no_collision_with_different_name(self):
        """Test that no collision occurs with different names."""
        manager = AuxiliaryVariableManager()
        manager.register_user_variables({"aux_min_objdef_1"})

        # Should not raise
        name = manager.generate_name("min", "objdef")
        assert name == "aux_min_objdef_0"

    def test_invalid_func_type(self):
        """Test that invalid func_type raises error."""
        manager = AuxiliaryVariableManager()

        with pytest.raises(ValueError, match="must be 'min' or 'max'"):
            manager.generate_name("median", "eq1")

    def test_register_multiple_user_variables(self):
        """Test registering multiple user variables at once."""
        manager = AuxiliaryVariableManager()
        manager.register_user_variables({"x", "y", "z"})
        manager.register_user_variables({"a", "b"})

        assert manager.user_variables == {"x", "y", "z", "a", "b"}


class TestDetectWithFlattening:
    """Test that detection properly integrates with flattening."""

    def test_detect_flattens_nested_min(self):
        """Test that detected calls have flattened arguments."""
        # min(min(x, y), z)
        inner = Call("min", (VarRef("x"), VarRef("y")))
        outer = Call("min", (inner, VarRef("z")))
        calls = detect_min_max_calls(outer, "eq1")

        assert len(calls) == 1
        assert calls[0].func_type == "min"
        # Arguments should be flattened to [x, y, z]
        assert len(calls[0].args) == 3

    def test_detect_does_not_double_count_nested(self):
        """Test that nested min/max are not counted multiple times."""
        # min(min(x, y), z) should be detected as ONE min call with 3 args
        # not as TWO separate min calls
        inner = Call("min", (VarRef("x"), VarRef("y")))
        outer = Call("min", (inner, VarRef("z")))
        calls = detect_min_max_calls(outer, "eq1")

        assert len(calls) == 1  # Only one call detected

    def test_detect_preserves_mixed_functions(self):
        """Test that min(max(x, y), z) keeps max as argument."""
        inner_max = Call("max", (VarRef("x"), VarRef("y")))
        outer_min = Call("min", (inner_max, VarRef("z")))
        calls = detect_min_max_calls(outer_min, "eq1")

        assert len(calls) == 2  # Both min and max detected
        # First should be max with 2 args
        max_call = [c for c in calls if c.func_type == "max"][0]
        assert len(max_call.args) == 2
        # Second should be min with 2 args (max call + z)
        min_call = [c for c in calls if c.func_type == "min"][0]
        assert len(min_call.args) == 2


class TestMinMaxCallDataclass:
    """Test MinMaxCall dataclass."""

    def test_create_min_call(self):
        """Test creating MinMaxCall instance."""
        call = MinMaxCall(
            func_type="min", args=[VarRef("x"), VarRef("y")], context="objdef", index=0
        )

        assert call.func_type == "min"
        assert len(call.args) == 2
        assert call.context == "objdef"
        assert call.index == 0

    def test_default_index(self):
        """Test that index defaults to 0."""
        call = MinMaxCall(func_type="max", args=[VarRef("x")], context="eq1")

        assert call.index == 0

    def test_multiple_args(self):
        """Test MinMaxCall with multiple arguments."""
        args = [VarRef("x"), VarRef("y"), VarRef("z"), Const(5.0)]
        call = MinMaxCall(func_type="min", args=args, context="eq1", index=2)

        assert len(call.args) == 4
        assert call.index == 2


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    def test_objective_with_min(self):
        """Test detecting min in objective function: obj = min(x, y)."""
        expr = Call("min", (VarRef("x"), VarRef("y")))
        calls = detect_min_max_calls(expr, "objdef")

        assert len(calls) == 1
        assert calls[0].func_type == "min"
        assert calls[0].context == "objdef"

        # Generate auxiliary name
        manager = AuxiliaryVariableManager()
        manager.register_user_variables({"x", "y", "obj"})
        aux_name = manager.generate_name("min", "objdef")

        assert aux_name == "aux_min_objdef_0"

    def test_constraint_with_nested_max(self):
        """Test constraint with nested max: c = max(max(a, b), c)."""
        inner = Call("max", (VarRef("a"), VarRef("b")))
        outer = Call("max", (inner, VarRef("c")))
        calls = detect_min_max_calls(outer, "constraint_balance")

        assert len(calls) == 1
        assert calls[0].func_type == "max"
        # Should be flattened to 3 args
        assert len(calls[0].args) == 3

    def test_complex_expression_with_min_max(self):
        """Test complex expression: x + min(y, z) * max(a, b)."""
        min_expr = Call("min", (VarRef("y"), VarRef("z")))
        max_expr = Call("max", (VarRef("a"), VarRef("b")))
        product = Binary("*", min_expr, max_expr)
        expr = Binary("+", VarRef("x"), product)

        calls = detect_min_max_calls(expr, "eq_complex")

        assert len(calls) == 2
        # Should have both min and max
        func_types = {c.func_type for c in calls}
        assert func_types == {"min", "max"}

    def test_indexed_equation_naming(self):
        """Test naming scheme for indexed equations."""
        expr = Call("min", (VarRef("x", ("i1",)), VarRef("y", ("i1",))))
        _ = detect_min_max_calls(expr, "eq_balance_i1")

        manager = AuxiliaryVariableManager()
        aux_name = manager.generate_name("min", "eq_balance_i1")

        assert aux_name == "aux_min_eq_balance_i1_0"


# =============================================================================
# Day 4: Reformulation Implementation Tests
# =============================================================================


class TestReformulatMin:
    """Test reformulate_min() function."""

    def test_reformulate_simple_min_two_args(self):
        """Test reformulating min(x, y)."""
        from src.kkt.reformulation import reformulate_min

        min_call = MinMaxCall(
            func_type="min",
            args=[VarRef("x", ()), VarRef("y", ())],
            context="objdef",
            index=0,
        )

        manager = AuxiliaryVariableManager()
        result = reformulate_min(min_call, manager)

        # Check auxiliary variable name
        assert result.aux_var_name == "aux_min_objdef_0"

        # Check multiplier names (one per argument)
        assert len(result.multiplier_names) == 2
        assert result.multiplier_names[0] == "lambda_min_objdef_0_arg0"
        assert result.multiplier_names[1] == "lambda_min_objdef_0_arg1"

        # Check constraints (one per argument)
        assert len(result.constraints) == 2

        # First constraint: x - aux_min >= 0
        name0, eq0 = result.constraints[0]
        assert name0 == "comp_min_objdef_0_arg0"
        assert eq0.relation == Rel.GE

        # Second constraint: y - aux_min >= 0
        name1, eq1 = result.constraints[1]
        assert name1 == "comp_min_objdef_0_arg1"
        assert eq1.relation == Rel.GE

        # Check replacement expression
        assert isinstance(result.replacement_expr, VarRef)
        assert result.replacement_expr.name == "aux_min_objdef_0"

    def test_reformulate_min_three_args(self):
        """Test reformulating min(a, b, c)."""
        from src.kkt.reformulation import reformulate_min

        min_call = MinMaxCall(
            func_type="min",
            args=[VarRef("a", ()), VarRef("b", ()), VarRef("c", ())],
            context="balance",
            index=0,
        )

        manager = AuxiliaryVariableManager()
        result = reformulate_min(min_call, manager)

        # Should have 3 multipliers and 3 constraints
        assert len(result.multiplier_names) == 3
        assert len(result.constraints) == 3

        assert result.multiplier_names[0] == "lambda_min_balance_0_arg0"
        assert result.multiplier_names[1] == "lambda_min_balance_0_arg1"
        assert result.multiplier_names[2] == "lambda_min_balance_0_arg2"

    def test_reformulate_min_wrong_func_type(self):
        """Test that reformulate_min rejects max calls."""
        from src.kkt.reformulation import reformulate_min

        max_call = MinMaxCall(func_type="max", args=[VarRef("x", ())], context="eq1", index=0)

        manager = AuxiliaryVariableManager()
        with pytest.raises(ValueError, match="Expected func_type='min'"):
            reformulate_min(max_call, manager)

    def test_reformulate_min_empty_args(self):
        """Test that empty arguments raise error."""
        from src.kkt.reformulation import reformulate_min

        min_call = MinMaxCall(func_type="min", args=[], context="eq1", index=0)

        manager = AuxiliaryVariableManager()
        with pytest.raises(ValueError, match="must have at least one argument"):
            reformulate_min(min_call, manager)

    def test_reformulate_min_with_expressions(self):
        """Test reformulating min with complex expressions as arguments."""
        from src.kkt.reformulation import reformulate_min

        # min(x + 2, y * 3)
        arg1 = Binary("+", VarRef("x", ()), Const(2.0))
        arg2 = Binary("*", VarRef("y", ()), Const(3.0))

        min_call = MinMaxCall(func_type="min", args=[arg1, arg2], context="objdef", index=0)

        manager = AuxiliaryVariableManager()
        result = reformulate_min(min_call, manager)

        # Should still work with complex expressions
        assert len(result.constraints) == 2
        assert result.aux_var_name == "aux_min_objdef_0"


class TestReformulatMax:
    """Test reformulate_max() function."""

    def test_reformulate_simple_max_two_args(self):
        """Test reformulating max(x, y)."""
        from src.kkt.reformulation import reformulate_max

        max_call = MinMaxCall(
            func_type="max",
            args=[VarRef("x", ()), VarRef("y", ())],
            context="constraint1",
            index=0,
        )

        manager = AuxiliaryVariableManager()
        result = reformulate_max(max_call, manager)

        # Check auxiliary variable name
        assert result.aux_var_name == "aux_max_constraint1_0"

        # Check multiplier names (using mu instead of lambda)
        assert len(result.multiplier_names) == 2
        assert result.multiplier_names[0] == "mu_max_constraint1_0_arg0"
        assert result.multiplier_names[1] == "mu_max_constraint1_0_arg1"

        # Check constraints (one per argument)
        assert len(result.constraints) == 2

        # Constraints should be: aux_max - x >= 0, aux_max - y >= 0
        name0, eq0 = result.constraints[0]
        assert name0 == "comp_max_constraint1_0_arg0"
        assert eq0.relation == Rel.GE

        # Check replacement expression
        assert isinstance(result.replacement_expr, VarRef)
        assert result.replacement_expr.name == "aux_max_constraint1_0"

    def test_reformulate_max_three_args(self):
        """Test reformulating max(a, b, c)."""
        from src.kkt.reformulation import reformulate_max

        max_call = MinMaxCall(
            func_type="max",
            args=[VarRef("a", ()), VarRef("b", ()), VarRef("c", ())],
            context="balance",
            index=1,
        )

        manager = AuxiliaryVariableManager()
        result = reformulate_max(max_call, manager)

        # Should have 3 multipliers and 3 constraints
        assert len(result.multiplier_names) == 3
        assert len(result.constraints) == 3

    def test_reformulate_max_wrong_func_type(self):
        """Test that reformulate_max rejects min calls."""
        from src.kkt.reformulation import reformulate_max

        min_call = MinMaxCall(func_type="min", args=[VarRef("x", ())], context="eq1", index=0)

        manager = AuxiliaryVariableManager()
        with pytest.raises(ValueError, match="Expected func_type='max'"):
            reformulate_max(min_call, manager)

    def test_reformulate_max_empty_args(self):
        """Test that empty arguments raise error."""
        from src.kkt.reformulation import reformulate_max

        max_call = MinMaxCall(func_type="max", args=[], context="eq1", index=0)

        manager = AuxiliaryVariableManager()
        with pytest.raises(ValueError, match="must have at least one argument"):
            reformulate_max(max_call, manager)


class TestReformulateModel:
    """Test reformulate_model() function - end-to-end reformulation."""

    def test_reformulate_model_no_min_max(self):
        """Test that model without min/max is unchanged."""
        from src.ir.model_ir import ModelIR
        from src.ir.symbols import EquationDef, Rel, VariableDef, VarKind
        from src.kkt.reformulation import reformulate_model

        model = ModelIR()

        # Add simple variables
        model.add_var(VariableDef("x", (), VarKind.CONTINUOUS))
        model.add_var(VariableDef("y", (), VarKind.CONTINUOUS))

        # Add simple equation: x + y = 10
        eq = EquationDef(
            name="balance",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(Binary("+", VarRef("x", ()), VarRef("y", ())), Const(10.0)),
        )
        model.add_equation(eq)

        vars_before = len(model.variables)
        eqs_before = len(model.equations)

        # Reformulate (should do nothing)
        reformulate_model(model)

        # No change
        assert len(model.variables) == vars_before
        assert len(model.equations) == eqs_before

    def test_reformulate_model_simple_min(self):
        """Test reformulating model with simple min(x, y)."""
        from src.ir.model_ir import ModelIR
        from src.ir.symbols import EquationDef, Rel, VariableDef, VarKind
        from src.kkt.reformulation import reformulate_model

        model = ModelIR()

        # Add variables
        model.add_var(VariableDef("x", (), VarKind.CONTINUOUS))
        model.add_var(VariableDef("y", (), VarKind.CONTINUOUS))
        model.add_var(VariableDef("z", (), VarKind.CONTINUOUS))

        # Add equation: z = min(x, y)
        eq = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("z", ()), Call("min", (VarRef("x", ()), VarRef("y", ())))),
        )
        model.add_equation(eq)

        # Reformulate
        reformulate_model(model)

        # Should add:
        # - 1 auxiliary variable (aux_min_objdef_0)
        # - 2 multipliers (lambda_min_objdef_0_arg0, lambda_min_objdef_0_arg1)
        # - 2 complementarity constraints
        assert len(model.variables) == 3 + 1 + 2  # Original + aux + 2 multipliers
        assert len(model.equations) == 1 + 2  # Original + 2 constraints

        # Check auxiliary variable exists
        assert "aux_min_objdef_0" in model.variables
        assert model.variables["aux_min_objdef_0"].kind == VarKind.CONTINUOUS

        # Check multipliers exist and are positive
        assert "lambda_min_objdef_0_arg0" in model.variables
        assert "lambda_min_objdef_0_arg1" in model.variables
        assert model.variables["lambda_min_objdef_0_arg0"].kind == VarKind.POSITIVE
        assert model.variables["lambda_min_objdef_0_arg1"].kind == VarKind.POSITIVE

        # Check complementarity constraints exist
        assert "comp_min_objdef_0_arg0" in model.equations
        assert "comp_min_objdef_0_arg1" in model.equations

        # Check original equation was modified (min replaced with aux var)
        modified_eq = model.equations["objdef"]
        _, rhs = modified_eq.lhs_rhs
        assert isinstance(rhs, VarRef)
        assert rhs.name == "aux_min_objdef_0"

    def test_reformulate_model_simple_max(self):
        """Test reformulating model with simple max(x, y)."""
        from src.ir.model_ir import ModelIR
        from src.ir.symbols import EquationDef, Rel, VariableDef, VarKind
        from src.kkt.reformulation import reformulate_model

        model = ModelIR()

        # Add variables
        model.add_var(VariableDef("x", (), VarKind.CONTINUOUS))
        model.add_var(VariableDef("y", (), VarKind.CONTINUOUS))
        model.add_var(VariableDef("w", (), VarKind.CONTINUOUS))

        # Add equation: w = max(x, y)
        eq = EquationDef(
            name="maxdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("w", ()), Call("max", (VarRef("x", ()), VarRef("y", ())))),
        )
        model.add_equation(eq)

        # Reformulate
        reformulate_model(model)

        # Should add auxiliary variable and multipliers
        assert "aux_max_maxdef_0" in model.variables
        assert "mu_max_maxdef_0_arg0" in model.variables
        assert "mu_max_maxdef_0_arg1" in model.variables

        # Check complementarity constraints
        assert "comp_max_maxdef_0_arg0" in model.equations
        assert "comp_max_maxdef_0_arg1" in model.equations

    def test_reformulate_model_multiple_min_max(self):
        """Test reformulating model with both min and max."""
        from src.ir.model_ir import ModelIR
        from src.ir.symbols import EquationDef, Rel, VariableDef, VarKind
        from src.kkt.reformulation import reformulate_model

        model = ModelIR()

        # Add variables
        model.add_var(VariableDef("x", (), VarKind.CONTINUOUS))
        model.add_var(VariableDef("y", (), VarKind.CONTINUOUS))
        model.add_var(VariableDef("z", (), VarKind.CONTINUOUS))

        # Equation 1: z = min(x, y)
        eq1 = EquationDef(
            name="eq1",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("z", ()), Call("min", (VarRef("x", ()), VarRef("y", ())))),
        )
        model.add_equation(eq1)

        # Equation 2: z = max(x, y)
        eq2 = EquationDef(
            name="eq2",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("z", ()), Call("max", (VarRef("x", ()), VarRef("y", ())))),
        )
        model.add_equation(eq2)

        # Reformulate
        reformulate_model(model)

        # Should have both min and max auxiliaries
        assert "aux_min_eq1_0" in model.variables
        assert "aux_max_eq2_0" in model.variables

        # Each should have 2 multipliers
        assert "lambda_min_eq1_0_arg0" in model.variables
        assert "lambda_min_eq1_0_arg1" in model.variables
        assert "mu_max_eq2_0_arg0" in model.variables
        assert "mu_max_eq2_0_arg1" in model.variables

        # Should have 4 complementarity constraints (2 for each)
        assert "comp_min_eq1_0_arg0" in model.equations
        assert "comp_min_eq1_0_arg1" in model.equations
        assert "comp_max_eq2_0_arg0" in model.equations
        assert "comp_max_eq2_0_arg1" in model.equations

    def test_reformulate_model_three_args(self):
        """Test reformulating min with three arguments."""
        from src.ir.model_ir import ModelIR
        from src.ir.symbols import EquationDef, Rel, VariableDef, VarKind
        from src.kkt.reformulation import reformulate_model

        model = ModelIR()

        # Add variables
        for var_name in ["a", "b", "c", "result"]:
            model.add_var(VariableDef(var_name, (), VarKind.CONTINUOUS))

        # Equation: result = min(a, b, c)
        eq = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("result", ()),
                Call("min", (VarRef("a", ()), VarRef("b", ()), VarRef("c", ()))),
            ),
        )
        model.add_equation(eq)

        # Reformulate
        reformulate_model(model)

        # Should have 3 multipliers and 3 constraints
        assert "lambda_min_objdef_0_arg0" in model.variables
        assert "lambda_min_objdef_0_arg1" in model.variables
        assert "lambda_min_objdef_0_arg2" in model.variables

        assert "comp_min_objdef_0_arg0" in model.equations
        assert "comp_min_objdef_0_arg1" in model.equations
        assert "comp_min_objdef_0_arg2" in model.equations


class TestAcceptanceCriteria:
    """Test Day 4 acceptance criteria."""

    def test_min_two_args_generates_two_constraints(self):
        """AC: min(x, y) generates 2 auxiliary constraints with multipliers."""
        from src.ir.model_ir import ModelIR
        from src.ir.symbols import EquationDef, Rel, VariableDef, VarKind
        from src.kkt.reformulation import reformulate_model

        model = ModelIR()
        model.add_var(VariableDef("x", (), VarKind.CONTINUOUS))
        model.add_var(VariableDef("y", (), VarKind.CONTINUOUS))
        model.add_var(VariableDef("obj", (), VarKind.CONTINUOUS))

        eq = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), Call("min", (VarRef("x", ()), VarRef("y", ())))),
        )
        model.add_equation(eq)

        reformulate_model(model)

        # Should have exactly 2 complementarity constraints
        comp_constraints = [name for name in model.equations if name.startswith("comp_min")]
        assert len(comp_constraints) == 2

        # Should have exactly 2 multipliers
        multipliers = [
            name
            for name in model.variables
            if name.startswith("lambda_min") or name.startswith("mu_")
        ]
        assert len(multipliers) == 2

    def test_max_two_args_generates_two_constraints_opposite_direction(self):
        """AC: max(x, y) generates 2 auxiliary constraints (opposite direction)."""
        from src.ir.model_ir import ModelIR
        from src.ir.symbols import EquationDef, Rel, VariableDef, VarKind
        from src.kkt.reformulation import reformulate_model

        model = ModelIR()
        model.add_var(VariableDef("x", (), VarKind.CONTINUOUS))
        model.add_var(VariableDef("y", (), VarKind.CONTINUOUS))
        model.add_var(VariableDef("obj", (), VarKind.CONTINUOUS))

        eq = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), Call("max", (VarRef("x", ()), VarRef("y", ())))),
        )
        model.add_equation(eq)

        reformulate_model(model)

        # Should have exactly 2 complementarity constraints
        comp_constraints = [name for name in model.equations if name.startswith("comp_max")]
        assert len(comp_constraints) == 2

        # Constraints should be aux_max - x >= 0, aux_max - y >= 0 (opposite of min)
        for constraint_name in comp_constraints:
            constraint = model.equations[constraint_name]
            assert constraint.relation == Rel.GE

    def test_multi_arg_min_generates_n_constraints(self):
        """AC: Multi-argument min(a, b, c) generates 3 constraints."""
        from src.ir.model_ir import ModelIR
        from src.ir.symbols import EquationDef, Rel, VariableDef, VarKind
        from src.kkt.reformulation import reformulate_model

        model = ModelIR()
        for var_name in ["a", "b", "c", "result"]:
            model.add_var(VariableDef(var_name, (), VarKind.CONTINUOUS))

        eq = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("result", ()),
                Call("min", (VarRef("a", ()), VarRef("b", ()), VarRef("c", ()))),
            ),
        )
        model.add_equation(eq)

        reformulate_model(model)

        # Should have exactly 3 complementarity constraints
        comp_constraints = [name for name in model.equations if name.startswith("comp_min")]
        assert len(comp_constraints) == 3

        # Should have exactly 3 multipliers
        multipliers = [name for name in model.variables if name.startswith("lambda_min")]
        assert len(multipliers) == 3

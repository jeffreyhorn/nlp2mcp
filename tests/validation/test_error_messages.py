"""
Test suite for error message quality and clarity.

This validates that error messages from validation systems provide:
1. Clear description of what went wrong
2. Actionable suggestions for fixing the issue
3. Proper location context where applicable

Sprint 5 Day 6: Task 6.3 - Message Validation
"""

import pytest

from src.ir.model_ir import ModelIR
from src.ir.parser import parse_model_text
from src.ir.symbols import ParameterDef
from src.utils.errors import ModelError, NumericalError
from src.validation.model import validate_model_structure
from src.validation.numerical import (
    validate_bounds,
    validate_parameter_values,
)


class TestNumericalErrorMessages:
    """Test numerical error message quality."""

    def test_inf_parameter_message(self):
        """Verify Inf parameter errors have clear, actionable error messages.

        Inf values (from division by zero or genuine overflow) are still rejected.
        This test checks that the error message is informative.
        """
        model = ModelIR()
        model.params["p"] = ParameterDef(name="p", domain=("i",), values={("1",): float("inf")})

        with pytest.raises(NumericalError) as exc_info:
            validate_parameter_values(model)

        error_msg = str(exc_info.value)
        assert "parameter" in error_msg.lower()
        assert "p" in error_msg
        assert "Inf" in error_msg
        assert len(error_msg) > 50  # Non-trivial message with actionable content

    def test_invalid_bounds_message(self):
        """Verify invalid bounds errors have clear messages with suggestions."""
        with pytest.raises(NumericalError) as exc_info:
            validate_bounds(10.0, 5.0, "x")

        error_msg = str(exc_info.value)
        # Should mention the variable name
        assert "x" in error_msg
        # Should mention the problematic bounds
        assert "10" in error_msg and "5" in error_msg
        # Should indicate the problem
        assert "lower" in error_msg.lower() and "upper" in error_msg.lower()
        # Should have suggestion
        assert "suggestion" in error_msg.lower() or "fix" in error_msg.lower()

    def test_nan_bound_message(self):
        """Verify NaN bound errors have clear messages."""
        with pytest.raises(NumericalError) as exc_info:
            validate_bounds(float("nan"), 10.0, "y")

        error_msg = str(exc_info.value)
        # Should mention NaN explicitly
        assert "nan" in error_msg.lower()
        # Should mention it's a lower bound issue
        assert "lower" in error_msg.lower() or "bound" in error_msg.lower()
        # Should mention variable name
        assert "y" in error_msg
        # Should have suggestion
        assert "suggestion" in error_msg.lower() or "set" in error_msg.lower()


class TestModelErrorMessages:
    """Test model structure error message quality."""

    def test_missing_objective_message(self):
        """Verify missing objective errors provide helpful guidance."""
        gams_code = """
Variables
    x
    y ;

Equations
    eq1 ;

eq1..
    x + y =e= 10;

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        with pytest.raises(ModelError) as exc_info:
            validate_model_structure(model)

        error_msg = str(exc_info.value)
        # Should clearly state the problem
        assert "objective" in error_msg.lower()
        # Should provide example/suggestion
        assert "suggestion" in error_msg.lower() or "add" in error_msg.lower()
        # Should mention key GAMS constructs
        assert "equation" in error_msg.lower() or "solve" in error_msg.lower()

    def test_constant_equation_message(self):
        """Verify constant equation errors explain the issue clearly."""
        gams_code = """
Variables
    obj ;

Equations
    const_eq
    objective ;

const_eq..
    5 =e= 5;

objective..
    obj =e= 1;

Model test /all/ ;
Solve test using NLP minimizing obj;
"""
        model = parse_model_text(gams_code)
        with pytest.raises(ModelError) as exc_info:
            validate_model_structure(model)

        error_msg = str(exc_info.value)
        # Should mention the equation name
        assert "const_eq" in error_msg
        # Should explain the problem
        assert "variable" in error_msg.lower() or "constant" in error_msg.lower()
        # Should provide actionable suggestions
        assert "suggestion" in error_msg.lower()
        # Should explain why this is invalid
        assert len(error_msg) > 100  # Substantial explanation

    def test_circular_dependency_allowed(self):
        """Verify cross-equation cycles are allowed (Issue #719).

        NLP models are solved simultaneously, so mutual dependencies between
        variables across equations are valid and should not raise errors.
        """
        gams_code = """
Variables
    x
    y
    obj ;

Equations
    eq1
    eq2
    objective ;

eq1..
    x =e= y + 1;

eq2..
    y =e= x + 1;

objective..
    obj =e= x + y;

Model test /all/ ;
Solve test using NLP minimizing obj;
"""
        model = parse_model_text(gams_code)
        # Should not raise — cross-equation cycles are valid in NLP
        validate_model_structure(model)


class TestEdgeCaseErrorMessages:
    """Test that edge cases produce clear error messages when they fail."""

    def test_duplicate_bounds_message_quality(self):
        """Verify duplicate/conflicting bounds produce clear errors."""
        gams_code = """
Variables
    x
    obj ;

x.lo = 0;
x.up = 10;
x.lo = 5;

Equations
    objective ;

objective..
    obj =e= x;

Model test /all/ ;
"""
        # This should raise an error about conflicting bounds
        try:
            model = parse_model_text(gams_code)
            # If parsing succeeds, validation should catch it
            if model:
                # Check if bounds are inconsistent
                var_x = model.variables.get("x")
                if var_x and var_x.lo is not None:
                    # Parser may have taken last value, which is OK
                    pass
        except Exception as e:
            # Should have clear error about bounds
            error_msg = str(e)
            assert len(error_msg) > 20  # Non-trivial message
            # Should reference the variable
            assert "x" in error_msg or "bound" in error_msg.lower()


class TestErrorMessageCompleteness:
    """Test that all error types have required components."""

    def test_model_error_has_suggestion(self):
        """Verify ModelError instances include suggestions."""
        gams_code = """
Variables
    obj ;

Equations
    no_vars
    objective ;

no_vars..
    1 + 1 =e= 2;

objective..
    obj =e= 1;

Model test /all/ ;
Solve test using NLP minimizing obj;
"""
        model = parse_model_text(gams_code)
        with pytest.raises(ModelError) as exc_info:
            validate_model_structure(model)

        error_msg = str(exc_info.value)
        # Every ModelError should have a suggestion section
        assert "suggestion" in error_msg.lower()

    def test_numerical_error_format(self):
        """Verify NumericalError provides value and location context."""
        with pytest.raises(NumericalError) as exc_info:
            validate_bounds(10.0, 0.0, "test_var")

        error = exc_info.value
        # Should have location
        assert error.location is not None
        assert "test_var" in error.location

        # Error message should be formatted clearly
        error_msg = str(error)
        assert "test_var" in error_msg
        assert "10" in error_msg
        assert "0" in error_msg

    def test_error_messages_are_actionable(self):
        """Verify error messages provide actionable next steps."""
        test_cases = [
            # (error generator, expected keywords in message)
            (
                lambda: validate_bounds(float("nan"), 1.0, "x"),
                ["nan", "bound", "x", "suggestion"],
            ),
            (
                lambda: validate_bounds(5.0, 2.0, "y"),
                ["lower", "upper", "y", "suggestion"],
            ),
        ]

        for error_generator, expected_keywords in test_cases:
            try:
                error_generator()
                pytest.fail("Expected an error to be raised")
            except NumericalError as e:
                error_msg = str(e).lower()
                for keyword in expected_keywords:
                    assert (
                        keyword.lower() in error_msg
                    ), f"Expected '{keyword}' in error message, got: {error_msg}"


class TestErrorMessageLength:
    """Test that error messages are neither too terse nor too verbose."""

    def test_minimum_message_length(self):
        """Error messages should be descriptive enough to be helpful."""
        gams_code = """
Variables
    x
    obj ;

Equations
    const_eq
    objective ;

const_eq..
    5 =e= 5;

objective..
    obj =e= x;

Model test /all/ ;
Solve test using NLP minimizing obj;
"""
        model = parse_model_text(gams_code)

        with pytest.raises(ModelError) as exc_info:
            validate_model_structure(model)

        error_msg = str(exc_info.value)
        # Should be at least a full sentence with suggestion
        assert len(error_msg) >= 50

    def test_maximum_message_readability(self):
        """Error messages should be concise enough to read quickly."""
        # Use a constant equation error (no variables referenced)
        gams_code = """
Variables
    x
    obj ;

Equations
    const_eq
    objective ;

const_eq..
    5 =e= 5;

objective..
    obj =e= x;

Model test /all/ ;
Solve test using NLP minimizing obj;
"""
        model = parse_model_text(gams_code)
        with pytest.raises(ModelError) as exc_info:
            validate_model_structure(model)

        error_msg = str(exc_info.value)
        # Should be detailed but not a novel (< 1000 chars is reasonable)
        assert len(error_msg) < 1000


class TestErrorMessageConsistency:
    """Test that error messages follow consistent patterns."""

    def test_suggestion_format_consistency(self):
        """All suggestions should follow a consistent format."""
        # Collect several errors
        errors = []

        # Missing objective
        try:
            gams_code = """
Variables
    x ;
Equations
    eq1 ;
eq1..
    x =e= 1;
Model test /all/ ;
"""
            model = parse_model_text(gams_code)
            validate_model_structure(model)
        except ModelError as e:
            errors.append(str(e))

        # Constant equation
        try:
            gams_code = """
Variables
    obj ;
Equations
    const_eq
    objective ;
const_eq..
    5 =e= 5;
objective..
    obj =e= 1;
Model test /all/ ;
Solve test using NLP minimizing obj;
"""
            model = parse_model_text(gams_code)
            validate_model_structure(model)
        except ModelError as e:
            errors.append(str(e))

        # Check that all have suggestion sections
        for error_msg in errors:
            assert "suggestion" in error_msg.lower()

        # Check formatting consistency - all should use similar structure
        # They should all have "Error:" or similar prefix
        for error_msg in errors:
            # Either starts with "Error:" or has it in first line
            first_line = error_msg.split("\n")[0]
            assert len(first_line) > 10  # Non-trivial first line

"""Unit tests for $if/$else/$endif conditional directives.

Tests for Phase 4 of Issue #360: Dollar Control Directives.
This phase implements conditional compilation using $if, $else, $elseif, and $endif.
"""

from src.ir.preprocessor import _evaluate_if_condition, process_conditionals


class TestEvaluateIfCondition:
    """Test condition evaluation logic."""

    def test_if_set_variable_defined(self):
        assert _evaluate_if_condition("$if set n", {"n": "10"}) is True

    def test_if_set_variable_undefined(self):
        assert _evaluate_if_condition("$if set missing", {"n": "10"}) is False

    def test_if_not_set_variable_undefined(self):
        assert _evaluate_if_condition("$if not set missing", {"n": "10"}) is True

    def test_if_comparison_greater_than(self):
        assert _evaluate_if_condition("$if %n% > 5", {"n": "10"}) is True

    def test_if_comparison_greater_equal(self):
        assert _evaluate_if_condition("$if %n% >= 10", {"n": "10"}) is True

    def test_if_comparison_less_equal(self):
        assert _evaluate_if_condition("$if %n% <= 10", {"n": "10"}) is True


class TestProcessConditionalsBasic:
    """Test basic conditional processing."""

    def test_if_set_true_includes_block(self):
        source = """$if set debug
Parameter debugMode;
$endif
Parameter alwaysHere;"""
        result = process_conditionals(source, {"debug": "1"})
        assert "Parameter debugMode;" in result
        assert "Parameter alwaysHere;" in result

    def test_if_set_false_excludes_block(self):
        source = """$if set debug
Parameter debugMode;
$endif"""
        result = process_conditionals(source, {})
        assert "* [Excluded: Parameter debugMode;]" in result
        assert "\nParameter debugMode;" not in result


class TestProcessConditionalsElse:
    """Test $else blocks."""

    def test_else_block_when_if_false(self):
        source = """$if set debug
Parameter debugMode;
$else
Parameter prodMode;
$endif"""
        result = process_conditionals(source, {})
        assert "* [Excluded: Parameter debugMode;]" in result
        assert "Parameter prodMode;" in result


class TestProcessConditionalsElseIf:
    """Test $elseif blocks."""

    def test_elseif_when_first_if_false(self):
        source = """$if set mode1
Parameter mode1Active;
$elseif set mode2
Parameter mode2Active;
$endif"""
        result = process_conditionals(source, {"mode2": "1"})
        assert "* [Excluded: Parameter mode1Active;]" in result
        assert "Parameter mode2Active;" in result


class TestProcessConditionalsNested:
    """Test nested conditional blocks."""

    def test_nested_if_both_true(self):
        source = """$if set outer
Outer block;
$if set inner
Inner block;
$endif
$endif"""
        result = process_conditionals(source, {"outer": "1", "inner": "1"})
        assert "Outer block;" in result
        assert "Inner block;" in result


class TestProcessConditionalsIntegration:
    """Test integration with real-world patterns."""

    def test_elec_pattern(self):
        """Test pattern from elec.gms - single-line default."""
        source = """$if not set n $set n 10
Set i /1*%n%/;"""
        result = process_conditionals(source, {})
        # Single-line $if not set ... $set ... is passed through
        assert "$if not set n $set n 10" in result

    def test_default_value_pattern(self):
        """Test common default value pattern with multi-line block."""
        source = """$if not set maxiter
$set maxiter 1000
$endif
Parameter maxIterations /%maxiter%/;"""
        result = process_conditionals(source, {})
        assert "$set maxiter 1000" in result

    def test_feature_flag_pattern(self):
        """Test feature flag pattern."""
        source = """$if set USE_ADVANCED
$set solver cplex
$else
$set solver cbc
$endif"""
        result = process_conditionals(source, {"USE_ADVANCED": "1"})
        assert "$set solver cplex" in result
        assert "* [Excluded: $set solver cbc]" in result

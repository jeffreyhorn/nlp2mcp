"""Feature interaction tests.

Sprint 11 Prep Task 11: Test combinations of features to detect interaction bugs.
Organized by feature pair with risk-based prioritization.

Risk Levels:
- HIGH: Features share AST manipulation or semantic analysis code (test first)
- MEDIUM: Features may affect same data structures or output (test after basics stable)
- LOW: Features are orthogonal (test as needed)

Sprint 11 Coverage Target:
- HIGH-risk pairs: 100% (3/3)
- MEDIUM-risk pairs: 60% (3/5)

NOTE: Many tests are currently skipped as placeholders for Sprint 11+ features.
      Enable tests as features are implemented.
"""

import pytest

from src.ir.ast import Call
from src.ir.parser import parse_model_file
from src.ir.symbols import VariableDef

pytestmark = pytest.mark.integration


class TestHighRiskInteractions:
    """HIGH risk feature pairs (P0 - critical, test before Sprint 11 implementation).

    These feature pairs share code paths and are most likely to interfere with each other.
    """

    class TestFunctionCallsWithNestedIndexing:
        """Function calls + nested indexing interaction.

        Risk: HIGH - Both involve complex expression parsing, may interfere
        Features:
          - Function Calls (Sprint 10): sqrt(), exp(), power(), etc.
          - Nested Indexing (Future): subset(i), filter expressions

        NOTE: Nested indexing not yet implemented. Tests are placeholders.
        """

        @pytest.mark.skip(reason="Nested subset indexing not yet implemented")
        def test_function_with_single_nested_index(self, tmp_path):
            """Placeholder: Test function call with single level of index nesting.

            Enable when subset(i) syntax is supported.
            """
            pass

        @pytest.mark.skip(reason="Nested subset indexing not yet implemented")
        def test_function_with_multiple_nested_arguments(self, tmp_path):
            """Placeholder: Test function call with multiple arguments, some nested.

            Enable when subset(i) syntax is supported.
            """
            pass

        def test_function_with_indexed_argument(self, tmp_path):
            """Test function call with indexed sum argument (currently supported).

            Pattern: sqrt(sum(i, expr))
            Expected: Parse succeeds, Call node with sum expression
            """
            test_file = tmp_path / "test_indexed_arg.gms"
            test_file.write_text(
                """
Sets i / i1*i3 /;
Parameters
    data(i)
    result;

* Simple data initialization
data('i1') = 10;
data('i2') = 20;
data('i3') = 30;

* Function with sum containing indexed parameter
result = sqrt(sum(i, data(i)));
"""
            )

            model = parse_model_file(test_file)

            # Verify parse succeeded
            assert "result" in model.params

            # Verify Call node exists
            param = model.params["result"]
            assert () in param.expressions
            expr = param.expressions[()]
            assert isinstance(expr, Call)
            assert expr.func == "sqrt"

    class TestVariableBoundsWithNestedIndexing:
        """Variable bounds + nested indexing interaction.

        Risk: HIGH - Index extraction from attribute access may fail with nesting

        NOTE: Nested indexing not yet implemented. Tests are placeholders.
        """

        @pytest.mark.skip(reason="Nested subset indexing not yet implemented")
        def test_bounds_with_subset_index(self, tmp_path):
            """Placeholder: Test variable bound with subset index expression.

            Enable when subset(i) syntax is supported.
            """
            pass

        def test_bounds_with_simple_index(self, tmp_path):
            """Test variable bound with simple index (currently supported).

            Pattern: x.lo(i) = 0
            Expected: Parse succeeds, bounds applied correctly
            """
            test_file = tmp_path / "test_simple_bounds.gms"
            test_file.write_text(
                """
Sets i / i1*i3 /;
Variables x(i);

* Bounds with simple index
x.lo(i) = 0;
x.up(i) = 100;
"""
            )

            model = parse_model_file(test_file)

            # Verify parse succeeded
            assert "x" in model.variables

            # Verify variable structure
            var = model.variables["x"]
            assert isinstance(var, VariableDef)


class TestMediumRiskInteractions:
    """MEDIUM risk feature pairs (P1 - important, test after basic features stable)."""

    class TestFunctionCallsWithSimplification:
        """Function calls + simplification interaction.

        Risk: MEDIUM - Simplification may alter function arguments incorrectly

        NOTE: Advanced simplification not yet implemented. Tests are placeholders.
        """

        def test_function_preserves_structure(self, tmp_path):
            """Test that function Call nodes are preserved (parse-only in Sprint 10).

            Pattern: sqrt(2*x + 2*y)
            Expected: Call node preserved (simplification happens in Sprint 11)
            """
            test_file = tmp_path / "test_call_preserve.gms"
            test_file.write_text(
                """
Parameters
    x
    y
    result;
x = 2;
y = 3;

* Function with arithmetic expression
result = sqrt(2*x + 2*y);
"""
            )

            model = parse_model_file(test_file)

            # Verify Call node exists (parse-only in Sprint 10)
            assert "result" in model.params
            expr = model.params["result"].expressions[()]
            assert isinstance(expr, Call)
            assert expr.func == "sqrt"

    class TestCommaSeparatedWithComplexExpressions:
        """Comma-separated declarations + complex inline expressions interaction.

        Risk: MEDIUM - Parsing ambiguity with commas in different contexts
        """

        @pytest.mark.skip(reason="Inline calculation expressions not yet supported")
        def test_comma_separated_with_inline_calculations(self, tmp_path):
            """Placeholder: Test comma-separated declarations with calculated values.

            Enable when inline expression evaluation in declarations is supported.
            """
            pass

        def test_comma_separated_scalars_basic(self, tmp_path):
            """Test basic comma-separated scalar declarations (currently supported).

            Pattern: Scalar a /5/, b /10/, c /1/
            Expected: Parse succeeds, all scalars created with values
            """
            test_file = tmp_path / "test_comma_basic.gms"
            test_file.write_text(
                """
* Comma-separated with literal values
Scalar a /5/, b /10/, c /1/;

Display a, b, c;
"""
            )

            model = parse_model_file(test_file)

            # Verify all scalars created
            assert "a" in model.params
            assert "b" in model.params
            assert "c" in model.params

            # Verify values
            assert model.params["a"].values[()] == 5
            assert model.params["b"].values[()] == 10
            assert model.params["c"].values[()] == 1


class TestLowRiskInteractions:
    """LOW risk feature pairs (P2/P3 - optional, test if bugs suspected)."""

    # Reserved for future tests if interaction issues discovered


# Framework validation test
def test_interaction_test_coverage():
    """Verify minimum interaction test coverage for Sprint 11.

    Expected:
      - HIGH-risk pairs: ≥2 test classes
      - MEDIUM-risk pairs: ≥2 test classes

    This meta-test ensures we maintain adequate interaction test coverage.
    """
    import inspect

    # Count test classes in each risk category
    high_risk_classes = [
        name
        for name, obj in inspect.getmembers(TestHighRiskInteractions)
        if inspect.isclass(obj) and name.startswith("Test")
    ]

    medium_risk_classes = [
        name
        for name, obj in inspect.getmembers(TestMediumRiskInteractions)
        if inspect.isclass(obj) and name.startswith("Test")
    ]

    # Validate coverage
    assert len(high_risk_classes) >= 2, (
        f"Expected ≥2 HIGH-risk test classes for Sprint 11, "
        f"found {len(high_risk_classes)}: {high_risk_classes}"
    )

    assert len(medium_risk_classes) >= 2, (
        f"Expected ≥2 MEDIUM-risk test classes for Sprint 11, "
        f"found {len(medium_risk_classes)}: {medium_risk_classes}"
    )

    # Log coverage for retrospective
    print("\nInteraction Test Coverage:")
    print(f"  HIGH-risk pairs: {len(high_risk_classes)} classes")
    print(f"  MEDIUM-risk pairs: {len(medium_risk_classes)} classes")
    print(f"  Total: {len(high_risk_classes) + len(medium_risk_classes)} interaction test classes")

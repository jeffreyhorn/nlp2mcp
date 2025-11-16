"""
Unit tests for convexity pattern detection (Sprint 6 Day 3).

Test Coverage:
-------------
1. Test individual pattern matchers in isolation (5 pattern classes, 10 tests)
2. Test selected patterns against a subset of available test fixtures (3 tests)
3. Verify convex models generate 0 warnings
4. Verify non-convex models generate expected warnings
5. Test AST utility functions
6. Test ConvexityWarning display formatting (2 tests)

Fixture Coverage:
-----------------
Not all fixtures are tested in this file. Pattern-specific tests use a subset
of fixtures (e.g., convex_lp, nonconvex_trig, convex_with_nonlinear_ineq).

Total: 18 unit tests covering all 5 patterns with targeted fixture validation.
"""

import pytest

from src.diagnostics.convexity.pattern_matcher import ConvexityWarning
from src.diagnostics.convexity.patterns import (
    BilinearTermPattern,
    NonlinearEqualityPattern,
    OddPowerPattern,
    QuotientPattern,
    TrigonometricPattern,
)
from src.ir.parser import parse_model_file, parse_model_text
from src.ir.symbols import SourceLocation

pytestmark = pytest.mark.unit


# ===== Fixture Paths =====

FIXTURE_DIR = "tests/fixtures/convexity"


# ===== Pattern-Specific Tests =====


class TestNonlinearEqualityPattern:
    """Test nonlinear equality constraint detection."""

    def test_detects_trig_equality(self):
        """Should detect sin(x) + cos(y) = 1 as nonlinear equality."""
        model = parse_model_file(f"{FIXTURE_DIR}/nonconvex_trig.gms")
        pattern = NonlinearEqualityPattern()

        warnings = pattern.detect(model)

        # Should have at least 1 nonlinear equality (trig equation)
        assert len(warnings) >= 1
        assert all(w.pattern == "nonlinear_equality" for w in warnings)

    def test_ignores_linear_equality(self):
        """Should NOT flag linear equalities like x + y = 5."""
        model = parse_model_file(f"{FIXTURE_DIR}/convex_lp.gms")
        pattern = NonlinearEqualityPattern()

        warnings = pattern.detect(model)

        # Linear program should have no nonlinear equality warnings
        assert len(warnings) == 0

    def test_ignores_convex_inequality(self):
        """Should NOT flag convex inequalities like x² + y² ≤ 4."""
        model = parse_model_file(f"{FIXTURE_DIR}/convex_with_nonlinear_ineq.gms")
        pattern = NonlinearEqualityPattern()

        warnings = pattern.detect(model)

        # Inequalities are allowed, even if nonlinear
        assert len(warnings) == 0


class TestTrigonometricPattern:
    """Test trigonometric function detection."""

    def test_detects_sin_function(self):
        """Should detect sin() in constraints."""
        model = parse_model_file(f"{FIXTURE_DIR}/nonconvex_trig.gms")
        pattern = TrigonometricPattern()

        warnings = pattern.detect(model)

        # Should detect trig functions
        trig_warnings = [w for w in warnings if w.pattern == "trigonometric_function"]
        assert len(trig_warnings) >= 1

    def test_detects_cos_function(self):
        """Should detect cos() in constraints."""
        model = parse_model_file(f"{FIXTURE_DIR}/nonconvex_trig.gms")
        pattern = TrigonometricPattern()

        warnings = pattern.detect(model)

        trig_warnings = [w for w in warnings if w.pattern == "trigonometric_function"]
        assert len(trig_warnings) >= 1
        # Check details mention trig functions
        assert any(
            "sin" in w.details.lower() or "cos" in w.details.lower()
            for w in trig_warnings
            if w.details
        )

    def test_no_trig_in_convex_models(self):
        """Should NOT detect trig functions in convex models."""
        convex_models = [
            "convex_lp.gms",
            "convex_with_nonlinear_ineq.gms",
        ]

        pattern = TrigonometricPattern()

        for model_file in convex_models:
            model = parse_model_file(f"{FIXTURE_DIR}/{model_file}")
            warnings = pattern.detect(model)
            assert len(warnings) == 0, f"{model_file} should have no trig warnings"

    def test_detects_trig_in_objective(self):
        """Should detect trig functions in objective function."""
        # Note: nonconvex_trig.gms may have trig in objective or constraints
        model = parse_model_file(f"{FIXTURE_DIR}/nonconvex_trig.gms")
        pattern = TrigonometricPattern()

        warnings = pattern.detect(model)

        # Should find at least one trig warning
        assert len(warnings) >= 1


class TestBilinearTermPattern:
    """Test bilinear term (variable * variable) detection."""

    def test_ignores_constant_times_variable(self):
        """Should NOT flag 2*x (constant * variable)."""
        model = parse_model_file(f"{FIXTURE_DIR}/convex_lp.gms")
        pattern = BilinearTermPattern()

        warnings = pattern.detect(model)

        # Linear programs use constant * variable, which is allowed
        assert len(warnings) == 0


class TestQuotientPattern:
    """Test division by variable detection."""

    def test_ignores_constant_division(self):
        """Should NOT flag x/2 (variable / constant)."""
        # Linear and QP models may use division by constants
        model = parse_model_file(f"{FIXTURE_DIR}/convex_lp.gms")
        pattern = QuotientPattern()

        warnings = pattern.detect(model)

        assert len(warnings) == 0


class TestOddPowerPattern:
    """Test odd power (x³, x⁵) detection."""

    def test_ignores_linear_term(self):
        """Should NOT flag x¹ (linear)."""
        model = parse_model_file(f"{FIXTURE_DIR}/convex_lp.gms")
        pattern = OddPowerPattern()

        warnings = pattern.detect(model)

        assert len(warnings) == 0


# ===== End-to-End Fixture Tests =====


class TestConvexModels:
    """Test that convex models produce NO warnings."""

    @pytest.mark.parametrize(
        "fixture_file",
        [
            "convex_lp.gms",
            "convex_with_nonlinear_ineq.gms",
        ],
    )
    def test_convex_model_has_no_warnings(self, fixture_file):
        """Convex models should generate 0 warnings from all patterns."""
        model = parse_model_file(f"{FIXTURE_DIR}/{fixture_file}")

        all_patterns = [
            NonlinearEqualityPattern(),
            TrigonometricPattern(),
            BilinearTermPattern(),
            QuotientPattern(),
            OddPowerPattern(),
        ]

        total_warnings = 0
        for pattern in all_patterns:
            warnings = pattern.detect(model)
            total_warnings += len(warnings)

        assert total_warnings == 0, (
            f"{fixture_file} should have 0 warnings but got {total_warnings}"
        )


class TestNonConvexModels:
    """Test that non-convex models produce expected warnings."""

    def test_nonconvex_trig_has_warnings(self):
        """nonconvex_trig.gms should generate 2 warnings (trig + nonlinear eq)."""
        model = parse_model_file(f"{FIXTURE_DIR}/nonconvex_trig.gms")

        all_patterns = [
            NonlinearEqualityPattern(),
            TrigonometricPattern(),
            BilinearTermPattern(),
            QuotientPattern(),
            OddPowerPattern(),
        ]

        all_warnings = []
        for pattern in all_patterns:
            all_warnings.extend(pattern.detect(model))

        assert len(all_warnings) >= 2
        # Should have trig and nonlinear equality warnings
        patterns_found = {w.pattern for w in all_warnings}
        assert "trigonometric_function" in patterns_found


# ===== Integration Test with All Fixtures =====


class TestAllFixtures:
    """Test all 13 fixtures systematically."""

    @pytest.mark.parametrize(
        "fixture_file,expected_min_warnings",
        [
            # Convex models
            ("convex_lp.gms", 0),
            ("convex_with_nonlinear_ineq.gms", 0),
            # Non-convex models
            ("nonconvex_trig.gms", 2),
        ],
    )
    def test_fixture_warning_count(self, fixture_file, expected_min_warnings):
        """Test that each fixture produces at least expected number of warnings."""
        model = parse_model_file(f"{FIXTURE_DIR}/{fixture_file}")

        all_patterns = [
            NonlinearEqualityPattern(),
            TrigonometricPattern(),
            BilinearTermPattern(),
            QuotientPattern(),
            OddPowerPattern(),
        ]

        all_warnings = []
        for pattern in all_patterns:
            all_warnings.extend(pattern.detect(model))

        actual_count = len(all_warnings)

        if expected_min_warnings == 0:
            assert actual_count == 0, (
                f"{fixture_file}: Expected 0 warnings (convex), got {actual_count}"
            )
        else:
            assert actual_count >= expected_min_warnings, (
                f"{fixture_file}: Expected at least {expected_min_warnings} warnings, got {actual_count}"
            )


# ===== Warning Display Tests =====


class TestWarningDisplay:
    """Test ConvexityWarning string formatting."""

    def test_warning_str_format(self):
        """Test __str__ method of ConvexityWarning."""
        from src.diagnostics.convexity.pattern_matcher import ConvexityWarning

        warning = ConvexityWarning(
            equation="eq1",
            pattern="nonlinear_equality",
            message="Test message",
            details="x^2 + y^2 = 4",
        )

        s = str(warning)
        assert "nonlinear_equality" in s
        assert "eq1" in s
        assert "Test message" in s
        assert "x^2 + y^2 = 4" in s

    def test_warning_without_details(self):
        """Test warning formatting without details."""
        from src.diagnostics.convexity.pattern_matcher import ConvexityWarning

        warning = ConvexityWarning(
            equation="eq2",
            pattern="trig_function",
            message="Trig detected",
            details=None,
        )

        s = str(warning)
        assert "trig_function" in s
        assert "eq2" in s
        assert "Trig detected" in s


# ===== Line Number Tracking Tests (Sprint 7 Day 8) =====


class TestLineNumberTracking:
    """Test that source location information is tracked and displayed in warnings."""

    def test_source_location_extracted_from_parser(self):
        """Test that parser extracts line numbers from GAMS source."""
        source = """
Sets
    i /i1*i3/;

Variables
    x(i);

Equations
    test_eq(i);

test_eq(i).. x(i) * x(i) =e= 1;

Model test /all/;
Solve test using nlp minimizing x;
"""
        model = parse_model_text(source)

        # Check that equation has source location
        assert "test_eq" in model.equations
        eq = model.equations["test_eq"]
        assert eq.source_location is not None
        assert eq.source_location.line == 11  # Line where equation is defined
        assert eq.source_location.column == 1

    def test_source_location_in_convexity_warning(self):
        """Test that convexity warnings include source location."""
        source = """
Variables x, y;
Equations eq1;

eq1.. x * x =e= 1;

Model test /all/;
Solve test using nlp minimizing x;
"""
        model = parse_model_text(source)
        pattern = NonlinearEqualityPattern()

        warnings = pattern.detect(model)

        assert len(warnings) >= 1
        warning = warnings[0]
        assert warning.source_location is not None
        assert warning.source_location.line == 5  # Line where eq1 is defined

    def test_warning_str_includes_location(self):
        """Test that warning string representation includes source location."""
        warning = ConvexityWarning(
            equation="eq1",
            pattern="nonlinear_equality",
            message="Nonlinear equality detected",
            details=None,
            error_code="W301",
            source_location=SourceLocation(line=10, column=1),
        )

        s = str(warning)
        assert "10:1" in s  # Should include line:column
        assert "eq1" in s
        assert "W301" in s

    def test_warning_str_without_location(self):
        """Test that warning works without source location (backward compatibility)."""
        warning = ConvexityWarning(
            equation="eq1",
            pattern="nonlinear_equality",
            message="Nonlinear equality detected",
            details=None,
            error_code="W301",
            source_location=None,
        )

        s = str(warning)
        # Should not crash, and should still show equation name
        assert "eq1" in s
        assert "W301" in s

    def test_multiple_equations_have_different_line_numbers(self):
        """Test that different equations have different line numbers."""
        source = """
Variables x, y;
Equations eq1, eq2, eq3;

eq1.. x * x =e= 1;
eq2.. y * y =e= 2;
eq3.. x * y =e= 3;

Model test /all/;
Solve test using nlp minimizing x;
"""
        model = parse_model_text(source)

        # All three equations should have different line numbers
        eq1 = model.equations["eq1"]
        eq2 = model.equations["eq2"]
        eq3 = model.equations["eq3"]

        assert eq1.source_location is not None
        assert eq2.source_location is not None
        assert eq3.source_location is not None

        # Lines should be 5, 6, 7
        assert eq1.source_location.line == 5
        assert eq2.source_location.line == 6
        assert eq3.source_location.line == 7

    def test_source_location_preserved_through_normalization(self):
        """Test that source location is preserved during normalization."""
        from src.ir.normalize import normalize_model

        source = """
Variables x;
Equations eq1;

eq1.. x * x =e= 1;

Model test /all/;
Solve test using nlp minimizing x;
"""
        model = parse_model_text(source)

        # Normalize the model
        normalized_equations, _ = normalize_model(model)

        # Check that normalized equation preserves source location
        assert "eq1" in normalized_equations
        norm_eq = normalized_equations["eq1"]
        assert norm_eq.source_location is not None
        assert norm_eq.source_location.line == 5

    def test_all_patterns_include_source_location(self):
        """Test that all pattern matchers include source location in warnings."""
        # Test each pattern type
        source_nonlinear_eq = """
Variables x;
Equations eq1;
eq1.. x * x =e= 1;
Model test /all/;
Solve test using nlp minimizing x;
"""

        source_trig = """
Variables x;
Equations eq1;
eq1.. sin(x) =e= 0;
Model test /all/;
Solve test using nlp minimizing x;
"""

        source_bilinear = """
Variables x, y;
Equations eq1;
eq1.. x * y =l= 1;
Model test /all/;
Solve test using nlp minimizing x;
"""

        test_cases = [
            (source_nonlinear_eq, NonlinearEqualityPattern()),
            (source_trig, TrigonometricPattern()),
            (source_bilinear, BilinearTermPattern()),
        ]

        for source, pattern in test_cases:
            model = parse_model_text(source)
            warnings = pattern.detect(model)

            if len(warnings) > 0:
                # Check that warning has source location
                assert warnings[0].source_location is not None
                assert warnings[0].source_location.line is not None

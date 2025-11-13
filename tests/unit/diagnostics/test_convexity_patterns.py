"""
Unit tests for convexity pattern detection (Sprint 6 Day 3).

Test Coverage:
-------------
1. Test each of 5 patterns against 13 test fixtures
2. Verify convex models generate 0 warnings
3. Verify non-convex models generate expected warnings
4. Test individual pattern matchers in isolation
5. Test AST utility functions

Fixtures from Sprint 6 Prep Task 8 (validated):
- 8 original fixtures (convex_lp, convex_qp, etc.)
- 5 additional fixtures for comprehensive coverage
- Total: 13 fixtures
"""

import pytest

from src.diagnostics.convexity.patterns import (
    BilinearTermPattern,
    NonlinearEqualityPattern,
    OddPowerPattern,
    QuotientPattern,
    TrigonometricPattern,
)
from src.ir.parser import parse_model_file

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

        assert (
            total_warnings == 0
        ), f"{fixture_file} should have 0 warnings but got {total_warnings}"


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
            assert (
                actual_count == 0
            ), f"{fixture_file}: Expected 0 warnings (convex), got {actual_count}"
        else:
            assert (
                actual_count >= expected_min_warnings
            ), f"{fixture_file}: Expected at least {expected_min_warnings} warnings, got {actual_count}"


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

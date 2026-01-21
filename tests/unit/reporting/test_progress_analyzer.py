"""Unit tests for the progress analyzer module."""

from __future__ import annotations

from src.reporting.analyzers.progress_analyzer import (
    ErrorChange,
    ProgressAnalyzer,
    RateDelta,
    Regression,
)
from src.reporting.data_loader import (
    BaselineMetrics,
    ComparisonMetrics,
    Environment,
    FullPipelineMetrics,
    StageMetrics,
)


def create_baseline(
    sprint: str,
    baseline_date: str,
    parse_success: int = 34,
    parse_failure: int = 126,
    parse_rate: float = 0.2125,
    translate_success: int = 17,
    translate_failure: int = 17,
    translate_rate: float = 0.5,
    solve_success: int = 3,
    solve_failure: int = 14,
    solve_rate: float = 0.1765,
    pipeline_success: int = 1,
    pipeline_rate: float = 0.0063,
    parse_errors: dict[str, int] | None = None,
    translate_errors: dict[str, int] | None = None,
    solve_errors: dict[str, int] | None = None,
) -> BaselineMetrics:
    """Create a test baseline with configurable values."""
    if parse_errors is None:
        parse_errors = {"lexer_invalid_char": 109, "internal_error": 17}
    if translate_errors is None:
        translate_errors = {"model_no_objective_def": 5, "diff_unsupported_func": 5}
    if solve_errors is None:
        solve_errors = {"path_syntax_error": 14}

    return BaselineMetrics(
        schema_version="1.0.0",
        baseline_date=baseline_date,
        sprint=sprint,
        environment=Environment(
            nlp2mcp_version="0.1.0",
            python_version="3.12.8",
            gams_version="51.3.0",
            path_solver_version="5.2.01",
            platform="Darwin",
            platform_version="24.6.0",
        ),
        total_models=160,
        model_types={"NLP": 94, "LP": 57, "QCP": 9},
        parse=StageMetrics(
            attempted=160,
            success=parse_success,
            failure=parse_failure,
            success_rate=parse_rate,
            cascade_skip=0,
            timing=None,
            by_type={},
            error_breakdown=parse_errors,
        ),
        translate=StageMetrics(
            attempted=parse_success,
            success=translate_success,
            failure=translate_failure,
            success_rate=translate_rate,
            cascade_skip=160 - parse_success,
            timing=None,
            by_type={},
            error_breakdown=translate_errors,
        ),
        solve=StageMetrics(
            attempted=translate_success,
            success=solve_success,
            failure=solve_failure,
            success_rate=solve_rate,
            cascade_skip=160 - translate_success,
            timing=None,
            by_type={},
            error_breakdown=solve_errors,
        ),
        comparison=ComparisonMetrics(
            attempted=solve_success,
            match=pipeline_success,
            mismatch=solve_success - pipeline_success,
            skipped=0,
            cascade_skip=160 - solve_success,
            match_rate=0.3333,
        ),
        full_pipeline=FullPipelineMetrics(
            success=pipeline_success,
            total=160,
            success_rate=pipeline_rate,
            successful_models=["hs62"] if pipeline_success >= 1 else [],
        ),
        notes=[],
    )


class TestProgressAnalyzerWithoutPrevious:
    """Tests for ProgressAnalyzer without previous snapshot."""

    def test_has_previous_false(self) -> None:
        """Test that has_previous returns False when no previous."""
        current = create_baseline("Sprint 15", "2026-01-15")
        analyzer = ProgressAnalyzer(current, previous=None)

        assert analyzer.has_previous() is False

    def test_get_rate_deltas_none(self) -> None:
        """Test that get_rate_deltas returns None without previous."""
        current = create_baseline("Sprint 15", "2026-01-15")
        analyzer = ProgressAnalyzer(current, previous=None)

        assert analyzer.get_rate_deltas() is None

    def test_get_error_changes_empty(self) -> None:
        """Test that get_error_changes returns empty list without previous."""
        current = create_baseline("Sprint 15", "2026-01-15")
        analyzer = ProgressAnalyzer(current, previous=None)

        assert analyzer.get_error_changes() == []

    def test_detect_regressions_empty(self) -> None:
        """Test that detect_regressions returns empty list without previous."""
        current = create_baseline("Sprint 15", "2026-01-15")
        analyzer = ProgressAnalyzer(current, previous=None)

        assert analyzer.detect_regressions() == []

    def test_get_comparison_summary_none(self) -> None:
        """Test that get_comparison_summary returns None without previous."""
        current = create_baseline("Sprint 15", "2026-01-15")
        analyzer = ProgressAnalyzer(current, previous=None)

        assert analyzer.get_comparison_summary() is None


class TestProgressAnalyzerWithPrevious:
    """Tests for ProgressAnalyzer with previous snapshot."""

    def test_has_previous_true(self) -> None:
        """Test that has_previous returns True when previous exists."""
        current = create_baseline("Sprint 16", "2026-01-20")
        previous = create_baseline("Sprint 15", "2026-01-15")
        analyzer = ProgressAnalyzer(current, previous=previous)

        assert analyzer.has_previous() is True

    def test_get_rate_deltas_improvement(self) -> None:
        """Test rate deltas for improvement scenario."""
        previous = create_baseline(
            "Sprint 15",
            "2026-01-15",
            parse_success=34,
            parse_rate=0.2125,
        )
        current = create_baseline(
            "Sprint 16",
            "2026-01-20",
            parse_success=50,
            parse_rate=0.3125,
        )
        analyzer = ProgressAnalyzer(current, previous=previous)

        deltas = analyzer.get_rate_deltas()

        assert deltas is not None
        assert deltas.parse.previous_rate == 0.2125
        assert deltas.parse.current_rate == 0.3125
        assert deltas.parse.delta == 0.1  # 0.3125 - 0.2125
        assert deltas.parse.trend == "improved"
        assert deltas.parse.delta_count == 16  # 50 - 34

    def test_get_rate_deltas_regression(self) -> None:
        """Test rate deltas for regression scenario."""
        previous = create_baseline(
            "Sprint 15",
            "2026-01-15",
            parse_success=50,
            parse_rate=0.3125,
        )
        current = create_baseline(
            "Sprint 16",
            "2026-01-20",
            parse_success=34,
            parse_rate=0.2125,
        )
        analyzer = ProgressAnalyzer(current, previous=previous)

        deltas = analyzer.get_rate_deltas()

        assert deltas is not None
        assert deltas.parse.trend == "regressed"
        assert deltas.parse.delta < 0

    def test_get_rate_deltas_unchanged(self) -> None:
        """Test rate deltas for unchanged scenario."""
        previous = create_baseline(
            "Sprint 15",
            "2026-01-15",
            parse_success=34,
            parse_rate=0.2125,
        )
        current = create_baseline(
            "Sprint 16",
            "2026-01-20",
            parse_success=34,
            parse_rate=0.2125,
        )
        analyzer = ProgressAnalyzer(current, previous=previous)

        deltas = analyzer.get_rate_deltas()

        assert deltas is not None
        assert deltas.parse.trend == "unchanged"

    def test_get_error_changes(self) -> None:
        """Test error category changes detection."""
        previous = create_baseline(
            "Sprint 15",
            "2026-01-15",
            parse_errors={"lexer_invalid_char": 109, "internal_error": 17},
        )
        current = create_baseline(
            "Sprint 16",
            "2026-01-20",
            parse_errors={"lexer_invalid_char": 50, "internal_error": 10},
        )
        analyzer = ProgressAnalyzer(current, previous=previous)

        changes = analyzer.get_error_changes()

        # Find lexer_invalid_char change
        lexer_change = next(c for c in changes if c.category == "lexer_invalid_char")
        assert lexer_change.previous_count == 109
        assert lexer_change.current_count == 50
        assert lexer_change.delta == -59
        assert lexer_change.trend == "improved"

    def test_get_error_changes_new_category(self) -> None:
        """Test error changes when new category appears."""
        previous = create_baseline(
            "Sprint 15",
            "2026-01-15",
            parse_errors={"lexer_invalid_char": 100},
        )
        current = create_baseline(
            "Sprint 16",
            "2026-01-20",
            parse_errors={"lexer_invalid_char": 80, "new_error": 20},
        )
        analyzer = ProgressAnalyzer(current, previous=previous)

        changes = analyzer.get_error_changes()

        new_error_change = next(c for c in changes if c.category == "new_error")
        assert new_error_change.previous_count == 0
        assert new_error_change.current_count == 20
        assert new_error_change.delta == 20
        assert new_error_change.trend == "regressed"

    def test_detect_regressions_rate(self) -> None:
        """Test regression detection for rate decrease."""
        previous = create_baseline(
            "Sprint 15",
            "2026-01-15",
            parse_rate=0.30,
        )
        current = create_baseline(
            "Sprint 16",
            "2026-01-20",
            parse_rate=0.25,  # 5% decrease > 2% threshold
        )
        analyzer = ProgressAnalyzer(current, previous=previous)

        regressions = analyzer.detect_regressions()

        assert len(regressions) >= 1
        rate_regression = next(r for r in regressions if r.regression_type == "rate")
        assert rate_regression.stage == "parse"
        assert rate_regression.severity == "warning"

    def test_detect_regressions_error_increase(self) -> None:
        """Test regression detection for error count increase."""
        previous = create_baseline(
            "Sprint 15",
            "2026-01-15",
            parse_errors={"lexer_invalid_char": 100},
        )
        current = create_baseline(
            "Sprint 16",
            "2026-01-20",
            parse_errors={"lexer_invalid_char": 110},  # 10 increase > 5 threshold
        )
        analyzer = ProgressAnalyzer(current, previous=previous)

        regressions = analyzer.detect_regressions()

        error_regression = next(
            (r for r in regressions if r.regression_type == "error_increase"), None
        )
        assert error_regression is not None
        assert error_regression.stage == "parse"
        assert "lexer_invalid_char" in error_regression.description

    def test_detect_no_regressions(self) -> None:
        """Test no regressions for improvement scenario."""
        previous = create_baseline(
            "Sprint 15",
            "2026-01-15",
            parse_rate=0.20,
            parse_errors={"lexer_invalid_char": 100},
        )
        current = create_baseline(
            "Sprint 16",
            "2026-01-20",
            parse_rate=0.30,  # Improvement
            parse_errors={"lexer_invalid_char": 50},  # Decrease
        )
        analyzer = ProgressAnalyzer(current, previous=previous)

        regressions = analyzer.detect_regressions()

        assert len(regressions) == 0

    def test_get_comparison_summary(self) -> None:
        """Test getting complete comparison summary."""
        previous = create_baseline("Sprint 15", "2026-01-15")
        current = create_baseline("Sprint 16", "2026-01-20")
        analyzer = ProgressAnalyzer(current, previous=previous)

        summary = analyzer.get_comparison_summary()

        assert summary is not None
        assert summary.previous_sprint == "Sprint 15"
        assert summary.current_sprint == "Sprint 16"
        assert summary.previous_date == "2026-01-15"
        assert summary.current_date == "2026-01-20"
        assert summary.rate_deltas is not None
        assert isinstance(summary.error_changes, list)
        assert isinstance(summary.regressions, list)
        assert isinstance(summary.has_regressions, bool)


class TestRateDelta:
    """Tests for RateDelta dataclass."""

    def test_rate_delta_fields(self) -> None:
        """Test RateDelta fields are accessible."""
        delta = RateDelta(
            stage="parse",
            previous_rate=0.20,
            current_rate=0.30,
            delta=0.10,
            previous_count=32,
            current_count=48,
            delta_count=16,
            trend="improved",
        )

        assert delta.stage == "parse"
        assert delta.previous_rate == 0.20
        assert delta.current_rate == 0.30
        assert delta.delta == 0.10
        assert delta.trend == "improved"


class TestErrorChange:
    """Tests for ErrorChange dataclass."""

    def test_error_change_fields(self) -> None:
        """Test ErrorChange fields are accessible."""
        change = ErrorChange(
            category="lexer_invalid_char",
            stage="parse",
            previous_count=100,
            current_count=50,
            delta=-50,
            trend="improved",
        )

        assert change.category == "lexer_invalid_char"
        assert change.delta == -50
        assert change.trend == "improved"


class TestRegression:
    """Tests for Regression dataclass."""

    def test_regression_fields(self) -> None:
        """Test Regression fields are accessible."""
        regression = Regression(
            regression_type="rate",
            stage="parse",
            description="Parse rate decreased from 30% to 25%",
            previous_value=0.30,
            current_value=0.25,
            delta=-0.05,
            severity="warning",
        )

        assert regression.regression_type == "rate"
        assert regression.severity == "warning"

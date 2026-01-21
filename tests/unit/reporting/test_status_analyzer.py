"""Unit tests for the status analyzer module."""

from __future__ import annotations

from src.reporting.analyzers.status_analyzer import StatusAnalyzer, StatusSummary
from src.reporting.data_loader import (
    BaselineMetrics,
    ComparisonMetrics,
    Environment,
    FullPipelineMetrics,
    StageMetrics,
    TypeBreakdown,
)


def create_test_baseline() -> BaselineMetrics:
    """Create a test baseline metrics object with known values."""
    return BaselineMetrics(
        schema_version="1.0.0",
        baseline_date="2026-01-15",
        sprint="Sprint 15",
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
            success=34,
            failure=126,
            success_rate=0.2125,
            cascade_skip=0,
            timing=None,
            by_type={
                "NLP": TypeBreakdown(attempted=94, success=26, success_rate=0.2766),
                "LP": TypeBreakdown(attempted=57, success=5, success_rate=0.0877),
                "QCP": TypeBreakdown(attempted=9, success=3, success_rate=0.3333),
            },
            error_breakdown={"lexer_invalid_char": 109, "internal_error": 17},
        ),
        translate=StageMetrics(
            attempted=34,
            success=17,
            failure=17,
            success_rate=0.5,
            cascade_skip=126,
            timing=None,
            by_type={
                "NLP": TypeBreakdown(attempted=26, success=14, success_rate=0.5385),
                "LP": TypeBreakdown(attempted=5, success=2, success_rate=0.4),
                "QCP": TypeBreakdown(attempted=3, success=1, success_rate=0.3333),
            },
            error_breakdown={"model_no_objective_def": 5, "diff_unsupported_func": 5},
        ),
        solve=StageMetrics(
            attempted=17,
            success=3,
            failure=14,
            success_rate=0.1765,
            cascade_skip=143,
            timing=None,
            by_type={
                "NLP": TypeBreakdown(attempted=14, success=2, success_rate=0.1429),
                "LP": TypeBreakdown(attempted=2, success=1, success_rate=0.5),
                "QCP": TypeBreakdown(attempted=1, success=0, success_rate=0.0),
            },
            error_breakdown={"path_syntax_error": 14},
        ),
        comparison=ComparisonMetrics(
            attempted=3,
            match=1,
            mismatch=2,
            skipped=0,
            cascade_skip=157,
            match_rate=0.3333,
        ),
        full_pipeline=FullPipelineMetrics(
            success=1,
            total=160,
            success_rate=0.0063,
            successful_models=["hs62"],
        ),
        notes=["Test baseline"],
    )


class TestStatusAnalyzer:
    """Tests for StatusAnalyzer class."""

    def test_get_parse_rate(self) -> None:
        """Test getting parse success rate."""
        baseline = create_test_baseline()
        analyzer = StatusAnalyzer(baseline)

        assert analyzer.get_parse_rate() == 0.2125

    def test_get_translate_rate(self) -> None:
        """Test getting translate success rate."""
        baseline = create_test_baseline()
        analyzer = StatusAnalyzer(baseline)

        assert analyzer.get_translate_rate() == 0.5

    def test_get_solve_rate(self) -> None:
        """Test getting solve success rate."""
        baseline = create_test_baseline()
        analyzer = StatusAnalyzer(baseline)

        assert analyzer.get_solve_rate() == 0.1765

    def test_get_pipeline_rate(self) -> None:
        """Test getting full pipeline success rate."""
        baseline = create_test_baseline()
        analyzer = StatusAnalyzer(baseline)

        assert analyzer.get_pipeline_rate() == 0.0063

    def test_get_summary(self) -> None:
        """Test getting complete status summary."""
        baseline = create_test_baseline()
        analyzer = StatusAnalyzer(baseline)

        summary = analyzer.get_summary()

        # Check rates
        assert summary.parse_rate == 0.2125
        assert summary.translate_rate == 0.5
        assert summary.solve_rate == 0.1765
        assert summary.pipeline_rate == 0.0063

        # Check counts
        assert summary.total_models == 160
        assert summary.parse_success == 34
        assert summary.parse_failure == 126
        assert summary.translate_success == 17
        assert summary.translate_failure == 17
        assert summary.translate_skipped == 126
        assert summary.solve_success == 3
        assert summary.solve_failure == 14
        assert summary.solve_skipped == 143
        assert summary.pipeline_success == 1

        # Check metadata
        assert summary.baseline_date == "2026-01-15"
        assert summary.sprint == "Sprint 15"

    def test_get_model_type_breakdown(self) -> None:
        """Test getting success rates broken down by model type."""
        baseline = create_test_baseline()
        analyzer = StatusAnalyzer(baseline)

        breakdown = analyzer.get_model_type_breakdown()

        # Check NLP breakdown
        assert "NLP" in breakdown
        assert breakdown["NLP"]["parse"] == 0.2766
        assert breakdown["NLP"]["translate"] == 0.5385
        assert breakdown["NLP"]["solve"] == 0.1429

        # Check LP breakdown
        assert "LP" in breakdown
        assert breakdown["LP"]["parse"] == 0.0877
        assert breakdown["LP"]["translate"] == 0.4
        assert breakdown["LP"]["solve"] == 0.5

        # Check QCP breakdown
        assert "QCP" in breakdown
        assert breakdown["QCP"]["parse"] == 0.3333
        assert breakdown["QCP"]["translate"] == 0.3333
        assert breakdown["QCP"]["solve"] == 0.0

    def test_get_error_breakdown(self) -> None:
        """Test getting error counts by category."""
        baseline = create_test_baseline()
        analyzer = StatusAnalyzer(baseline)

        errors = analyzer.get_error_breakdown()

        # Check parse errors
        assert "parse" in errors
        assert errors["parse"]["lexer_invalid_char"] == 109
        assert errors["parse"]["internal_error"] == 17

        # Check translate errors
        assert "translate" in errors
        assert errors["translate"]["model_no_objective_def"] == 5
        assert errors["translate"]["diff_unsupported_func"] == 5

        # Check solve errors
        assert "solve" in errors
        assert errors["solve"]["path_syntax_error"] == 14


class TestStatusSummary:
    """Tests for StatusSummary dataclass."""

    def test_format_rates_default_precision(self) -> None:
        """Test formatting rates as percentages with default precision."""
        summary = StatusSummary(
            parse_rate=0.2125,
            translate_rate=0.5,
            solve_rate=0.1765,
            pipeline_rate=0.0063,
            total_models=160,
            parse_success=34,
            parse_failure=126,
            translate_success=17,
            translate_failure=17,
            translate_skipped=126,
            solve_success=3,
            solve_failure=14,
            solve_skipped=143,
            pipeline_success=1,
            baseline_date="2026-01-15",
            sprint="Sprint 15",
        )

        formatted = summary.format_rates()

        assert formatted["parse_rate"] == "21.25%"
        assert formatted["translate_rate"] == "50.00%"
        assert formatted["solve_rate"] == "17.65%"
        assert formatted["pipeline_rate"] == "0.63%"

    def test_format_rates_custom_precision(self) -> None:
        """Test formatting rates with custom precision."""
        summary = StatusSummary(
            parse_rate=0.2125,
            translate_rate=0.5,
            solve_rate=0.1765,
            pipeline_rate=0.0063,
            total_models=160,
            parse_success=34,
            parse_failure=126,
            translate_success=17,
            translate_failure=17,
            translate_skipped=126,
            solve_success=3,
            solve_failure=14,
            solve_skipped=143,
            pipeline_success=1,
            baseline_date="2026-01-15",
            sprint="Sprint 15",
        )

        formatted = summary.format_rates(precision=1)

        assert formatted["parse_rate"] == "21.2%"
        assert formatted["translate_rate"] == "50.0%"
        assert formatted["solve_rate"] == "17.6%"
        assert formatted["pipeline_rate"] == "0.6%"

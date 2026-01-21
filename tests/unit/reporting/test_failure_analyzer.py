"""Unit tests for the failure analyzer module."""

from __future__ import annotations

from src.reporting.analyzers.failure_analyzer import (
    DEFAULT_EFFORT_HOURS,
    NON_FIXABLE_CATEGORIES,
    FailureAnalyzer,
)
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
            error_breakdown={
                "model_no_objective_def": 5,
                "diff_unsupported_func": 5,
                "unsup_index_offset": 3,
                "model_domain_mismatch": 2,
                "unsup_dollar_cond": 1,
                "codegen_numerical_error": 1,
            },
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


class TestFailureAnalyzer:
    """Tests for FailureAnalyzer class."""

    def test_get_parse_failures(self) -> None:
        """Test getting parse failures by category."""
        baseline = create_test_baseline()
        analyzer = FailureAnalyzer(baseline)

        failures = analyzer.get_parse_failures()

        assert failures["lexer_invalid_char"] == 109
        assert failures["internal_error"] == 17
        assert len(failures) == 2

    def test_get_translate_failures(self) -> None:
        """Test getting translation failures by category."""
        baseline = create_test_baseline()
        analyzer = FailureAnalyzer(baseline)

        failures = analyzer.get_translate_failures()

        assert failures["model_no_objective_def"] == 5
        assert failures["diff_unsupported_func"] == 5
        assert len(failures) == 6

    def test_get_solve_failures(self) -> None:
        """Test getting solve failures by category."""
        baseline = create_test_baseline()
        analyzer = FailureAnalyzer(baseline)

        failures = analyzer.get_solve_failures()

        assert failures["path_syntax_error"] == 14
        assert len(failures) == 1

    def test_calculate_priority_score(self) -> None:
        """Test priority score calculation."""
        baseline = create_test_baseline()
        analyzer = FailureAnalyzer(baseline)

        # Priority Score = Models / Effort
        # lexer_invalid_char: 109 models, 8 hours effort = 13.625 -> 13.62
        score = analyzer.calculate_priority_score("lexer_invalid_char", 109)
        assert score == 13.62

        # path_syntax_error: 14 models, 6 hours effort = 2.33
        score = analyzer.calculate_priority_score("path_syntax_error", 14)
        assert score == 2.33

    def test_calculate_priority_score_non_fixable(self) -> None:
        """Test that non-fixable categories return 0.0."""
        baseline = create_test_baseline()
        analyzer = FailureAnalyzer(baseline)

        for category in NON_FIXABLE_CATEGORIES:
            score = analyzer.calculate_priority_score(category, 100)
            assert score == 0.0

    def test_get_error_categories_parse(self) -> None:
        """Test getting detailed error categories for parse stage."""
        baseline = create_test_baseline()
        analyzer = FailureAnalyzer(baseline)

        categories = analyzer.get_error_categories("parse")

        assert len(categories) == 2
        # Should be sorted by count descending
        assert categories[0].name == "lexer_invalid_char"
        assert categories[0].count == 109
        assert categories[0].stage == "parse"
        assert categories[0].fixable is True
        assert categories[0].effort_hours == 8.0
        assert categories[0].priority_score == 13.62

    def test_get_error_categories_translate(self) -> None:
        """Test getting detailed error categories for translate stage."""
        baseline = create_test_baseline()
        analyzer = FailureAnalyzer(baseline)

        categories = analyzer.get_error_categories("translate")

        assert len(categories) == 6
        # Check first category (highest count)
        top_category = categories[0]
        assert top_category.count >= categories[-1].count

    def test_get_error_categories_solve(self) -> None:
        """Test getting detailed error categories for solve stage."""
        baseline = create_test_baseline()
        analyzer = FailureAnalyzer(baseline)

        categories = analyzer.get_error_categories("solve")

        assert len(categories) == 1
        assert categories[0].name == "path_syntax_error"
        assert categories[0].count == 14

    def test_get_prioritized_improvements(self) -> None:
        """Test getting prioritized improvement list."""
        baseline = create_test_baseline()
        analyzer = FailureAnalyzer(baseline)

        improvements = analyzer.get_prioritized_improvements()

        # Should have items from all stages
        assert len(improvements) > 0

        # Check ranking
        assert improvements[0].rank == 1
        assert improvements[1].rank == 2

        # Should be sorted by priority score descending
        for i in range(len(improvements) - 1):
            assert improvements[i].priority_score >= improvements[i + 1].priority_score

        # Top item should be lexer_invalid_char (highest score)
        assert improvements[0].error_category == "lexer_invalid_char"

    def test_get_summary(self) -> None:
        """Test getting failure summary."""
        baseline = create_test_baseline()
        analyzer = FailureAnalyzer(baseline)

        summary = analyzer.get_summary()

        assert summary.total_models == 160
        assert summary.parse_failures == 126
        assert summary.translate_failures == 17
        assert summary.solve_failures == 14
        assert summary.total_failures == 126 + 17 + 14
        assert summary.dominant_stage == "parse"
        assert summary.dominant_error == "lexer_invalid_char"
        # 2 parse + 6 translate + 1 solve = 9 unique error types
        assert summary.unique_error_types == 9


class TestDefaultEffortHours:
    """Tests for effort hour constants."""

    def test_all_common_categories_have_effort(self) -> None:
        """Test that common error categories have effort hours defined."""
        common_categories = [
            "lexer_invalid_char",
            "internal_error",
            "path_syntax_error",
            "model_no_objective_def",
            "diff_unsupported_func",
        ]
        for category in common_categories:
            assert category in DEFAULT_EFFORT_HOURS
            assert DEFAULT_EFFORT_HOURS[category] > 0


class TestNonFixableCategories:
    """Tests for non-fixable category constants."""

    def test_license_errors_not_fixable(self) -> None:
        """Test that license errors are marked as non-fixable."""
        assert "path_solve_license" in NON_FIXABLE_CATEGORIES

    def test_success_outcomes_not_fixable(self) -> None:
        """Test that success outcomes are marked as non-fixable."""
        assert "model_optimal" in NON_FIXABLE_CATEGORIES
        assert "model_locally_optimal" in NON_FIXABLE_CATEGORIES

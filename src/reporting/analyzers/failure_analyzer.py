"""
Failure analyzer for pipeline error analysis.

Provides error breakdown by category, priority scores, and improvement recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.reporting.data_loader import BaselineMetrics

# Default effort hours for error categories (from FAILURE_REPORT_SCHEMA.md)
DEFAULT_EFFORT_HOURS: dict[str, float] = {
    # Parse errors
    "lexer_invalid_char": 8.0,
    "lexer_unclosed_string": 2.0,
    "lexer_invalid_number": 2.0,
    "lexer_encoding_error": 2.0,
    "parser_unexpected_token": 4.0,
    "parser_missing_semicolon": 2.0,
    "parser_unmatched_paren": 2.0,
    "parser_invalid_declaration": 4.0,
    "parser_invalid_expression": 4.0,
    "parser_unexpected_eof": 3.0,
    "semantic_undefined_symbol": 4.0,
    "semantic_type_mismatch": 4.0,
    "semantic_domain_error": 6.0,
    "semantic_duplicate_def": 2.0,
    "include_file_not_found": 1.0,
    "include_circular": 2.0,
    "validation_circular_dep": 4.0,
    "internal_error": 12.0,
    # Translation errors
    "diff_unsupported_func": 6.0,
    "diff_chain_rule_error": 8.0,
    "diff_numerical_error": 4.0,
    "model_no_objective_def": 1.0,
    "model_domain_mismatch": 6.0,
    "model_missing_bounds": 4.0,
    "unsup_index_offset": 8.0,
    "unsup_dollar_cond": 6.0,
    "unsup_expression_type": 6.0,
    "unsup_special_ordered": 8.0,
    "codegen_equation_error": 4.0,
    "codegen_variable_error": 4.0,
    "codegen_numerical_error": 4.0,
    # Solve errors
    "path_syntax_error": 6.0,
    "path_solve_iteration_limit": 2.0,
    "path_solve_time_limit": 2.0,
    "path_solve_terminated": 4.0,
    "path_solve_eval_error": 6.0,
    "path_solve_license": 0.0,  # Not fixable
    "model_optimal": 0.0,  # Not an error
    "model_locally_optimal": 0.0,  # Not an error
    "model_infeasible": 4.0,
    "model_unbounded": 4.0,
}

# Categories that are not fixable in nlp2mcp
NON_FIXABLE_CATEGORIES: set[str] = {
    "path_solve_license",
    "model_optimal",
    "model_locally_optimal",
    "path_solve_normal",
    "timeout",
}


@dataclass
class ErrorCategory:
    """Details for a single error category."""

    name: str
    count: int
    percentage: float
    percentage_of_total: float
    stage: str
    effort_hours: float
    fixable: bool
    priority_score: float
    affected_models: list[str] = field(default_factory=list)


@dataclass
class ImprovementItem:
    """A prioritized improvement recommendation."""

    rank: int
    error_category: str
    stage: str
    models_affected: int
    effort_hours: float
    priority_score: float
    fixable: bool


@dataclass
class FailureSummary:
    """Summary of all failures across pipeline stages."""

    total_models: int
    total_failures: int
    parse_failures: int
    translate_failures: int
    solve_failures: int
    unique_error_types: int
    dominant_stage: str
    dominant_error: str


class FailureAnalyzer:
    """
    Analyzer for pipeline failure patterns.

    Groups errors by category, calculates priority scores, and generates
    improvement recommendations based on impact and effort.
    """

    def __init__(self, baseline: BaselineMetrics) -> None:
        """
        Initialize the failure analyzer.

        Args:
            baseline: Loaded baseline metrics
        """
        self._baseline = baseline

    def get_parse_failures(self) -> dict[str, int]:
        """
        Get parse failures grouped by error category.

        Returns:
            Dictionary mapping error category to count
        """
        return dict(self._baseline.parse.error_breakdown)

    def get_translate_failures(self) -> dict[str, int]:
        """
        Get translation failures grouped by error category.

        Returns:
            Dictionary mapping error category to count
        """
        return dict(self._baseline.translate.error_breakdown)

    def get_solve_failures(self) -> dict[str, int]:
        """
        Get solve failures grouped by error category.

        Returns:
            Dictionary mapping error category to count
        """
        return dict(self._baseline.solve.error_breakdown)

    def calculate_priority_score(self, category: str, models_affected: int) -> float:
        """
        Calculate priority score for an error category.

        Priority Score = Models Affected / Effort Hours
        Non-fixable errors return 0.0.

        Args:
            category: Error category name
            models_affected: Number of models affected by this error

        Returns:
            Priority score (higher = higher priority), 0.0 for non-fixable
        """
        if category in NON_FIXABLE_CATEGORIES:
            return 0.0

        effort_hours = DEFAULT_EFFORT_HOURS.get(category, 4.0)
        if effort_hours <= 0:
            return 0.0

        return round(models_affected / effort_hours, 2)

    def get_error_categories(self, stage: str) -> list[ErrorCategory]:
        """
        Get detailed error category information for a stage.

        Args:
            stage: Pipeline stage ('parse', 'translate', or 'solve')

        Returns:
            List of ErrorCategory objects sorted by count descending
        """
        if stage == "parse":
            error_breakdown = self._baseline.parse.error_breakdown
            stage_failures = self._baseline.parse.failure
        elif stage == "translate":
            error_breakdown = self._baseline.translate.error_breakdown
            stage_failures = self._baseline.translate.failure
        elif stage == "solve":
            error_breakdown = self._baseline.solve.error_breakdown
            stage_failures = self._baseline.solve.failure
        else:
            return []

        total_models = self._baseline.total_models
        categories = []

        for name, count in error_breakdown.items():
            percentage = (count / stage_failures * 100) if stage_failures > 0 else 0.0
            percentage_of_total = (count / total_models * 100) if total_models > 0 else 0.0
            effort_hours = DEFAULT_EFFORT_HOURS.get(name, 4.0)
            fixable = name not in NON_FIXABLE_CATEGORIES
            priority_score = self.calculate_priority_score(name, count)

            categories.append(
                ErrorCategory(
                    name=name,
                    count=count,
                    percentage=percentage,
                    percentage_of_total=percentage_of_total,
                    stage=stage,
                    effort_hours=effort_hours,
                    fixable=fixable,
                    priority_score=priority_score,
                )
            )

        # Sort by count descending
        categories.sort(key=lambda x: x.count, reverse=True)
        return categories

    def get_prioritized_improvements(self) -> list[ImprovementItem]:
        """
        Get improvement recommendations sorted by priority score.

        Returns:
            List of ImprovementItem objects sorted by priority score descending
        """
        improvements: list[ImprovementItem] = []

        # Collect from all stages
        for stage in ["parse", "translate", "solve"]:
            categories = self.get_error_categories(stage)
            for cat in categories:
                improvements.append(
                    ImprovementItem(
                        rank=0,  # Will be set after sorting
                        error_category=cat.name,
                        stage=stage,
                        models_affected=cat.count,
                        effort_hours=cat.effort_hours,
                        priority_score=cat.priority_score,
                        fixable=cat.fixable,
                    )
                )

        # Sort by priority score descending
        improvements.sort(key=lambda x: x.priority_score, reverse=True)

        # Assign ranks
        for i, item in enumerate(improvements, 1):
            item.rank = i

        return improvements

    def get_summary(self) -> FailureSummary:
        """
        Get a summary of all failures.

        Returns:
            FailureSummary with aggregate statistics
        """
        parse_failures = self._baseline.parse.failure
        translate_failures = self._baseline.translate.failure
        solve_failures = self._baseline.solve.failure
        total_failures = parse_failures + translate_failures + solve_failures

        # Count unique error types
        all_errors: set[str] = set()
        all_errors.update(self._baseline.parse.error_breakdown.keys())
        all_errors.update(self._baseline.translate.error_breakdown.keys())
        all_errors.update(self._baseline.solve.error_breakdown.keys())

        # Determine dominant stage
        stage_failures = {
            "parse": parse_failures,
            "translate": translate_failures,
            "solve": solve_failures,
        }
        dominant_stage = max(stage_failures, key=stage_failures.get)  # type: ignore[arg-type]

        # Determine dominant error (most frequent across all stages)
        all_error_counts: dict[str, int] = {}
        for errors in [
            self._baseline.parse.error_breakdown,
            self._baseline.translate.error_breakdown,
            self._baseline.solve.error_breakdown,
        ]:
            for name, count in errors.items():
                all_error_counts[name] = all_error_counts.get(name, 0) + count

        dominant_error = (
            max(all_error_counts, key=lambda k: all_error_counts[k]) if all_error_counts else "none"
        )

        return FailureSummary(
            total_models=self._baseline.total_models,
            total_failures=total_failures,
            parse_failures=parse_failures,
            translate_failures=translate_failures,
            solve_failures=solve_failures,
            unique_error_types=len(all_errors),
            dominant_stage=dominant_stage,
            dominant_error=dominant_error,
        )

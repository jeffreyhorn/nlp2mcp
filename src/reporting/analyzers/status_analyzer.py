"""
Status analyzer for pipeline metrics.

Provides overall success rates and summary statistics from baseline metrics.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.reporting.data_loader import BaselineMetrics


@dataclass
class StatusSummary:
    """Summary of pipeline status metrics."""

    # Overall rates
    parse_rate: float
    translate_rate: float
    solve_rate: float
    pipeline_rate: float

    # Counts
    total_models: int
    parse_success: int
    parse_failure: int
    translate_success: int
    translate_failure: int
    translate_skipped: int
    solve_success: int
    solve_failure: int
    solve_skipped: int
    pipeline_success: int

    # Metadata
    baseline_date: str
    sprint: str

    def format_rates(self, precision: int = 2) -> dict[str, str]:
        """Format rates as percentage strings.

        Args:
            precision: Number of decimal places

        Returns:
            Dictionary with formatted rate strings
        """
        return {
            "parse_rate": f"{self.parse_rate * 100:.{precision}f}%",
            "translate_rate": f"{self.translate_rate * 100:.{precision}f}%",
            "solve_rate": f"{self.solve_rate * 100:.{precision}f}%",
            "pipeline_rate": f"{self.pipeline_rate * 100:.{precision}f}%",
        }


class StatusAnalyzer:
    """
    Analyzer for overall pipeline status metrics.

    Extracts success rates and summary statistics from baseline metrics.
    """

    def __init__(self, baseline: BaselineMetrics) -> None:
        """
        Initialize the status analyzer.

        Args:
            baseline: Loaded baseline metrics
        """
        self._baseline = baseline

    def get_parse_rate(self) -> float:
        """
        Get the parse success rate.

        Returns:
            Parse success rate as a decimal (0.0 to 1.0)
        """
        return self._baseline.parse.success_rate

    def get_translate_rate(self) -> float:
        """
        Get the translation success rate (of parsed models).

        Returns:
            Translation success rate as a decimal (0.0 to 1.0)
        """
        return self._baseline.translate.success_rate

    def get_solve_rate(self) -> float:
        """
        Get the solve success rate (of translated models).

        Returns:
            Solve success rate as a decimal (0.0 to 1.0)
        """
        return self._baseline.solve.success_rate

    def get_pipeline_rate(self) -> float:
        """
        Get the full pipeline success rate.

        Returns:
            Full pipeline success rate as a decimal (0.0 to 1.0)
        """
        return self._baseline.full_pipeline.success_rate

    def get_summary(self) -> StatusSummary:
        """
        Get a complete summary of pipeline status.

        Returns:
            StatusSummary with all rates and counts
        """
        return StatusSummary(
            # Rates
            parse_rate=self.get_parse_rate(),
            translate_rate=self.get_translate_rate(),
            solve_rate=self.get_solve_rate(),
            pipeline_rate=self.get_pipeline_rate(),
            # Counts
            total_models=self._baseline.total_models,
            parse_success=self._baseline.parse.success,
            parse_failure=self._baseline.parse.failure,
            translate_success=self._baseline.translate.success,
            translate_failure=self._baseline.translate.failure,
            translate_skipped=self._baseline.translate.cascade_skip,
            solve_success=self._baseline.solve.success,
            solve_failure=self._baseline.solve.failure,
            solve_skipped=self._baseline.solve.cascade_skip,
            pipeline_success=self._baseline.full_pipeline.success,
            # Metadata
            baseline_date=self._baseline.baseline_date,
            sprint=self._baseline.sprint,
        )

    def get_model_type_breakdown(self) -> dict[str, dict[str, float]]:
        """
        Get success rates broken down by model type.

        Returns:
            Dictionary mapping model type to stage success rates
        """
        breakdown: dict[str, dict[str, float]] = {}

        for model_type in self._baseline.model_types:
            breakdown[model_type] = {
                "parse": (
                    self._baseline.parse.by_type[model_type].success_rate
                    if model_type in self._baseline.parse.by_type
                    else 0.0
                ),
                "translate": (
                    self._baseline.translate.by_type[model_type].success_rate
                    if model_type in self._baseline.translate.by_type
                    else 0.0
                ),
                "solve": (
                    self._baseline.solve.by_type[model_type].success_rate
                    if model_type in self._baseline.solve.by_type
                    else 0.0
                ),
            }

        return breakdown

    def get_error_breakdown(self) -> dict[str, dict[str, int]]:
        """
        Get error counts by category for each stage.

        Returns:
            Dictionary mapping stage to error category counts
        """
        return {
            "parse": self._baseline.parse.error_breakdown,
            "translate": self._baseline.translate.error_breakdown,
            "solve": self._baseline.solve.error_breakdown,
        }

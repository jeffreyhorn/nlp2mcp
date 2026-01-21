"""
Progress analyzer for sprint-over-sprint comparison.

Provides rate deltas, model changes, and regression detection.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.reporting.data_loader import BaselineMetrics

# Threshold configuration for regression detection
REGRESSION_THRESHOLDS = {
    # Rate-based thresholds (absolute change)
    "parse_rate": 0.02,  # 2% regression triggers alert
    "translate_rate": 0.02,
    "solve_rate": 0.02,
    "full_pipeline_rate": 0.01,  # More sensitive for full pipeline
    # Error category thresholds
    "error_increase_threshold": 5,  # Flag if any error category increases by >5
}


@dataclass
class RateDelta:
    """Change in a success rate between two snapshots."""

    stage: str
    previous_rate: float
    current_rate: float
    delta: float
    previous_count: int
    current_count: int
    delta_count: int
    trend: str  # 'improved', 'regressed', or 'unchanged'


@dataclass
class RateDeltas:
    """All rate deltas between two snapshots."""

    parse: RateDelta
    translate: RateDelta
    solve: RateDelta
    full_pipeline: RateDelta


@dataclass
class Regression:
    """A detected regression."""

    regression_type: str  # 'rate' or 'error_increase'
    stage: str
    description: str
    previous_value: float | int
    current_value: float | int
    delta: float | int
    severity: str  # 'warning' or 'critical'


@dataclass
class ErrorChange:
    """Change in an error category count."""

    category: str
    stage: str
    previous_count: int
    current_count: int
    delta: int
    trend: str  # 'improved', 'regressed', or 'unchanged'


@dataclass
class ComparisonSummary:
    """Complete comparison between two snapshots."""

    previous_sprint: str
    current_sprint: str
    previous_date: str
    current_date: str
    rate_deltas: RateDeltas
    error_changes: list[ErrorChange]
    regressions: list[Regression]
    has_regressions: bool


def _compute_trend(current: float, previous: float, threshold: float = 0.001) -> str:
    """Compute trend based on delta."""
    delta = current - previous
    if delta > threshold:
        return "improved"
    elif delta < -threshold:
        return "regressed"
    else:
        return "unchanged"


class ProgressAnalyzer:
    """
    Analyzer for comparing pipeline metrics across sprints.

    Computes rate deltas, detects regressions, and tracks error changes.
    """

    def __init__(
        self,
        current: BaselineMetrics,
        previous: BaselineMetrics | None = None,
    ) -> None:
        """
        Initialize the progress analyzer.

        Args:
            current: Current baseline metrics
            previous: Previous baseline metrics for comparison (optional)
        """
        self._current = current
        self._previous = previous

    def has_previous(self) -> bool:
        """Check if previous metrics are available for comparison."""
        return self._previous is not None

    def get_rate_deltas(self) -> RateDeltas | None:
        """
        Get rate changes between current and previous snapshots.

        Returns:
            RateDeltas object or None if no previous snapshot
        """
        if self._previous is None:
            return None

        return RateDeltas(
            parse=self._compute_rate_delta("parse"),
            translate=self._compute_rate_delta("translate"),
            solve=self._compute_rate_delta("solve"),
            full_pipeline=self._compute_pipeline_delta(),
        )

    def _compute_rate_delta(self, stage: str) -> RateDelta:
        """Compute rate delta for a stage."""
        if self._previous is None:
            raise ValueError("No previous metrics available")

        current_stage = getattr(self._current, stage)
        previous_stage = getattr(self._previous, stage)

        current_rate = current_stage.success_rate
        previous_rate = previous_stage.success_rate
        delta = current_rate - previous_rate

        return RateDelta(
            stage=stage,
            previous_rate=previous_rate,
            current_rate=current_rate,
            delta=delta,
            previous_count=previous_stage.success,
            current_count=current_stage.success,
            delta_count=current_stage.success - previous_stage.success,
            trend=_compute_trend(current_rate, previous_rate),
        )

    def _compute_pipeline_delta(self) -> RateDelta:
        """Compute rate delta for full pipeline."""
        if self._previous is None:
            raise ValueError("No previous metrics available")

        current_rate = self._current.full_pipeline.success_rate
        previous_rate = self._previous.full_pipeline.success_rate
        delta = current_rate - previous_rate

        return RateDelta(
            stage="full_pipeline",
            previous_rate=previous_rate,
            current_rate=current_rate,
            delta=delta,
            previous_count=self._previous.full_pipeline.success,
            current_count=self._current.full_pipeline.success,
            delta_count=(
                self._current.full_pipeline.success - self._previous.full_pipeline.success
            ),
            trend=_compute_trend(current_rate, previous_rate),
        )

    def get_error_changes(self) -> list[ErrorChange]:
        """
        Get changes in error category counts.

        Returns:
            List of ErrorChange objects for all categories
        """
        if self._previous is None:
            return []

        changes: list[ErrorChange] = []

        for stage in ["parse", "translate", "solve"]:
            current_errors = getattr(self._current, stage).error_breakdown
            previous_errors = getattr(self._previous, stage).error_breakdown

            # Get all error categories from both snapshots
            all_categories = set(current_errors.keys()) | set(previous_errors.keys())

            for category in all_categories:
                current_count = current_errors.get(category, 0)
                previous_count = previous_errors.get(category, 0)
                delta = current_count - previous_count

                # Determine trend (note: for errors, decrease is improvement)
                if delta < 0:
                    trend = "improved"
                elif delta > 0:
                    trend = "regressed"
                else:
                    trend = "unchanged"

                changes.append(
                    ErrorChange(
                        category=category,
                        stage=stage,
                        previous_count=previous_count,
                        current_count=current_count,
                        delta=delta,
                        trend=trend,
                    )
                )

        # Sort by absolute delta descending
        changes.sort(key=lambda x: abs(x.delta), reverse=True)
        return changes

    def detect_regressions(self) -> list[Regression]:
        """
        Detect regressions between current and previous snapshots.

        Checks for:
        - Rate decreases beyond threshold
        - Error category count increases beyond threshold

        Returns:
            List of Regression objects
        """
        if self._previous is None:
            return []

        regressions: list[Regression] = []

        # Check rate regressions
        rate_deltas = self.get_rate_deltas()
        if rate_deltas:
            for delta in [
                rate_deltas.parse,
                rate_deltas.translate,
                rate_deltas.solve,
                rate_deltas.full_pipeline,
            ]:
                threshold_key = f"{delta.stage}_rate"
                threshold = REGRESSION_THRESHOLDS.get(threshold_key, 0.02)

                # Check if rate decreased beyond threshold
                if delta.delta < -threshold:
                    severity = "critical" if delta.stage == "full_pipeline" else "warning"
                    regressions.append(
                        Regression(
                            regression_type="rate",
                            stage=delta.stage,
                            description=(
                                f"{delta.stage} rate decreased from "
                                f"{delta.previous_rate * 100:.1f}% to {delta.current_rate * 100:.1f}%"
                            ),
                            previous_value=delta.previous_rate,
                            current_value=delta.current_rate,
                            delta=delta.delta,
                            severity=severity,
                        )
                    )

        # Check error category increases
        error_threshold = REGRESSION_THRESHOLDS.get("error_increase_threshold", 5)
        error_changes = self.get_error_changes()

        for change in error_changes:
            if change.delta > error_threshold:
                regressions.append(
                    Regression(
                        regression_type="error_increase",
                        stage=change.stage,
                        description=(
                            f"{change.category} increased from "
                            f"{change.previous_count} to {change.current_count}"
                        ),
                        previous_value=change.previous_count,
                        current_value=change.current_count,
                        delta=change.delta,
                        severity="warning",
                    )
                )

        return regressions

    def get_comparison_summary(self) -> ComparisonSummary | None:
        """
        Get a complete comparison summary.

        Returns:
            ComparisonSummary object or None if no previous snapshot
        """
        if self._previous is None:
            return None

        rate_deltas = self.get_rate_deltas()
        if rate_deltas is None:
            return None

        regressions = self.detect_regressions()

        return ComparisonSummary(
            previous_sprint=self._previous.sprint,
            current_sprint=self._current.sprint,
            previous_date=self._previous.baseline_date,
            current_date=self._current.baseline_date,
            rate_deltas=rate_deltas,
            error_changes=self.get_error_changes(),
            regressions=regressions,
            has_regressions=len(regressions) > 0,
        )

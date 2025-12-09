"""Diagnostics infrastructure for GAMS-to-MCP pipeline.

This module provides diagnostic tracking for the 5-stage compilation pipeline:
1. Parse: GAMS source → Parse tree
2. Semantic Analysis: Parse tree → Validated IR
3. Simplification: IR transformations and optimizations
4. IR Generation: Final IR model construction
5. MCP Generation: IR → MCP GAMS output

Sprint 11 Day 8: Text and JSON output modes for performance analysis.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Stage(Enum):
    """Pipeline stages for diagnostic tracking."""

    PARSE = "Parse"
    SEMANTIC = "Semantic Analysis"
    SIMPLIFICATION = "Simplification"
    IR_GENERATION = "IR Generation"
    MCP_GENERATION = "MCP Generation"


@dataclass
class StageMetrics:
    """Metrics for a single pipeline stage."""

    stage: Stage
    duration_ms: float = 0.0
    success: bool = False
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiagnosticReport:
    """Complete diagnostic report for pipeline execution."""

    model_name: str
    stages: dict[Stage, StageMetrics] = field(default_factory=dict)

    @property
    def total_duration_ms(self) -> float:
        """Calculate total duration from all stages."""
        return sum(m.duration_ms for m in self.stages.values())

    @property
    def overall_success(self) -> bool:
        """Check if all stages succeeded."""
        # If there are no stages, consider as False (no success)
        return bool(self.stages) and all(m.success for m in self.stages.values())

    def add_stage(self, metrics: StageMetrics) -> None:
        """Add stage metrics to the report."""
        self.stages[metrics.stage] = metrics

    def to_text(self) -> str:
        """Format report as human-readable text table.

        Returns:
            Formatted text table with stage timings and status
        """
        lines = []
        lines.append(f"Diagnostic Report: {self.model_name}")
        lines.append("=" * 70)
        lines.append("")

        # Header
        lines.append(f"{'Stage':<25} {'Duration':<12} {'Status':<10} {'Details'}")
        lines.append("-" * 70)

        # Stage rows
        for stage in Stage:
            if stage in self.stages:
                metrics = self.stages[stage]
                duration_str = f"{metrics.duration_ms:.2f} ms"
                status = "✓ SUCCESS" if metrics.success else "✗ FAILED"

                # Build details string
                details_parts = []
                if metrics.error:
                    details_parts.append(f"Error: {metrics.error}")
                if metrics.details:
                    for key, value in metrics.details.items():
                        details_parts.append(f"{key}={value}")
                details_str = ", ".join(details_parts) if details_parts else "-"

                lines.append(f"{stage.value:<25} {duration_str:<12} {status:<10} {details_str}")
            else:
                lines.append(f"{stage.value:<25} {'N/A':<12} {'SKIPPED':<10} -")

        # Summary
        lines.append("-" * 70)
        total_str = f"{self.total_duration_ms:.2f} ms"
        overall_status = "✓ SUCCESS" if self.overall_success else "✗ FAILED"
        lines.append(f"{'TOTAL':<25} {total_str:<12} {overall_status}")
        lines.append("")

        return "\n".join(lines)

    def to_json(self) -> dict[str, Any]:
        """Format report as JSON-serializable dictionary (legacy format).

        Returns:
            Dictionary with all diagnostic data
        """
        return {
            "model_name": self.model_name,
            "total_duration_ms": self.total_duration_ms,
            "overall_success": self.overall_success,
            "stages": {
                stage.value: {
                    "duration_ms": metrics.duration_ms,
                    "success": metrics.success,
                    "error": metrics.error,
                    "details": metrics.details,
                }
                for stage, metrics in self.stages.items()
            },
        }

    def to_json_v1(self) -> dict[str, Any]:
        """Format report as JSON with schema v1.0.0.

        Returns:
            Dictionary conforming to diagnostics schema v1.0.0
        """
        from datetime import UTC, datetime

        return {
            "schema_version": "1.0.0",
            "generated_at": datetime.now(UTC).isoformat(),
            "model_name": self.model_name,
            "total_duration_ms": self.total_duration_ms,
            "overall_success": self.overall_success,
            "stages": {
                stage.value: {
                    "duration_ms": metrics.duration_ms,
                    "success": metrics.success,
                    "error": metrics.error,
                    "details": metrics.details,
                }
                for stage, metrics in self.stages.items()
            },
            "summary": self._build_summary(),
        }

    def _build_summary(self) -> dict[str, Any]:
        """Build summary object from stages.

        Returns:
            Summary statistics for the diagnostic report
        """
        all_stages = list(Stage)
        completed = len(self.stages)
        failed = sum(1 for m in self.stages.values() if not m.success)
        skipped = len(all_stages) - completed

        # Helper to get duration or 0 if stage not present
        def get_duration(stage: Stage) -> float:
            if stage in self.stages:
                return self.stages[stage].duration_ms
            return 0.0

        return {
            "stages_completed": completed,
            "stages_failed": failed,
            "stages_skipped": skipped,
            "parse_duration_ms": get_duration(Stage.PARSE),
            "semantic_duration_ms": get_duration(Stage.SEMANTIC),
            "simplification_duration_ms": get_duration(Stage.SIMPLIFICATION),
            "ir_generation_duration_ms": get_duration(Stage.IR_GENERATION),
            "mcp_generation_duration_ms": get_duration(Stage.MCP_GENERATION),
        }


class DiagnosticContext:
    """Context manager for tracking stage execution with timing.

    Example:
        >>> report = DiagnosticReport(model_name="example.gms")
        >>> with DiagnosticContext(report, Stage.PARSE) as ctx:
        ...     # Parse operations here
        ...     ctx.add_detail("lines", 150)
        >>> print(report.to_text())
    """

    def __init__(self, report: DiagnosticReport, stage: Stage):
        """Initialize diagnostic context.

        Args:
            report: DiagnosticReport to update
            stage: Pipeline stage being tracked
        """
        self.report = report
        self.stage = stage
        self.metrics = StageMetrics(stage=stage)
        self.start_time: float = 0.0

    def add_detail(self, key: str, value: Any) -> None:
        """Add detail to stage metrics.

        Args:
            key: Detail name
            value: Detail value
        """
        self.metrics.details[key] = value

    def __enter__(self) -> "DiagnosticContext":
        """Start timing the stage."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Stop timing and record results.

        Args:
            exc_type: Exception type if raised
            exc_val: Exception value if raised
            exc_tb: Exception traceback if raised
        """
        end_time = time.perf_counter()
        self.metrics.duration_ms = (end_time - self.start_time) * 1000

        if exc_type is None:
            # Success
            self.metrics.success = True
        else:
            # Failure
            self.metrics.success = False
            self.metrics.error = str(exc_val)

        self.report.add_stage(self.metrics)


def create_report(model_name: str) -> DiagnosticReport:
    """Create a new diagnostic report for a model.

    Args:
        model_name: Name of the model being processed

    Returns:
        New DiagnosticReport instance
    """
    return DiagnosticReport(model_name=model_name)

"""
Markdown renderer for report generation.

Renders Jinja2 templates to markdown files with tabulate for table generation.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from tabulate import tabulate

from src.reporting.analyzers.failure_analyzer import (
    ErrorCategory,
    FailureAnalyzer,
    FailureSummary,
    ImprovementItem,
)
from src.reporting.analyzers.progress_analyzer import ComparisonSummary
from src.reporting.analyzers.status_analyzer import StatusSummary
from src.reporting.data_loader import BaselineMetrics, TimingStats


class RenderError(Exception):
    """Exception raised when rendering fails."""


class MarkdownRenderer:
    """
    Renderer for Markdown report generation using Jinja2 templates.

    Uses Jinja2 templates and tabulate for table generation to produce
    GitHub-flavored Markdown reports.
    """

    def __init__(self, template_dir: Path | None = None) -> None:
        """
        Initialize the Markdown renderer.

        Args:
            template_dir: Path to template directory. If None, uses the default
                templates directory in the reporting module.
        """
        if template_dir is None:
            template_dir = Path(__file__).parent.parent / "templates"

        if not template_dir.exists():
            raise RenderError(f"Template directory not found: {template_dir}")

        self._template_dir = template_dir
        self._env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _format_timing_table(self, timing: TimingStats) -> str:
        """Format timing statistics as a markdown table."""
        headers = ["Metric", "Value"]
        data = [
            ["Mean", f"{timing.mean_ms:.1f} ms"],
            ["Median", f"{timing.median_ms:.1f} ms"],
            ["P90", f"{timing.p90_ms:.1f} ms"],
            ["P99", f"{timing.p99_ms:.1f} ms"],
            ["Min", f"{timing.min_ms:.1f} ms"],
            ["Max", f"{timing.max_ms:.1f} ms"],
        ]
        return tabulate(data, headers=headers, tablefmt="github")

    def _format_stage_table(self, baseline: BaselineMetrics, summary: StatusSummary) -> str:
        """Format pipeline stage summary as a markdown table."""
        headers = ["Stage", "Attempted", "Success", "Failure", "Success Rate"]
        data = [
            [
                "Parse",
                baseline.parse.attempted,
                summary.parse_success,
                summary.parse_failure,
                f"{summary.parse_rate * 100:.1f}%",
            ],
            [
                "Translate",
                baseline.translate.attempted,
                summary.translate_success,
                summary.translate_failure,
                f"{summary.translate_rate * 100:.1f}%",
            ],
            [
                "Solve",
                baseline.solve.attempted,
                summary.solve_success,
                summary.solve_failure,
                f"{summary.solve_rate * 100:.1f}%",
            ],
            [
                "**Full Pipeline**",
                f"**{baseline.total_models}**",
                f"**{summary.pipeline_success}**",
                f"**{baseline.total_models - summary.pipeline_success}**",
                f"**{summary.pipeline_rate * 100:.1f}%**",
            ],
        ]
        return tabulate(data, headers=headers, tablefmt="github")

    def _format_type_table(self, baseline: BaselineMetrics) -> str:
        """Format success by model type as a markdown table."""
        headers = ["Type", "Count", "Parse Rate", "Translate Rate", "Solve Rate"]
        data = []

        for model_type, count in baseline.model_types.items():
            parse_rate = (
                baseline.parse.by_type[model_type].success_rate
                if model_type in baseline.parse.by_type
                else 0.0
            )
            translate_rate = (
                baseline.translate.by_type[model_type].success_rate
                if model_type in baseline.translate.by_type
                else 0.0
            )
            solve_rate = (
                baseline.solve.by_type[model_type].success_rate
                if model_type in baseline.solve.by_type
                else 0.0
            )
            data.append(
                [
                    model_type,
                    count,
                    f"{parse_rate * 100:.1f}%",
                    f"{translate_rate * 100:.1f}%",
                    f"{solve_rate * 100:.1f}%",
                ]
            )

        return tabulate(data, headers=headers, tablefmt="github")

    def _format_blocker_table(self, errors: list[ErrorCategory], max_items: int = 5) -> str:
        """Format top blockers as a markdown table."""
        headers = ["Rank", "Error Category", "Count", "Stage", "Priority Score"]
        data = []

        # Sort by count descending across all stages
        sorted_errors = sorted(errors, key=lambda x: x.count, reverse=True)

        for i, error in enumerate(sorted_errors[:max_items], 1):
            data.append(
                [
                    i,
                    f"`{error.name}`",
                    error.count,
                    error.stage,
                    f"{error.priority_score:.2f}",
                ]
            )

        return tabulate(data, headers=headers, tablefmt="github")

    def _format_error_table(self, errors: list[ErrorCategory]) -> str:
        """Format error breakdown as a markdown table."""
        headers = ["Category", "Count", "% of Failures", "Fixable", "Priority"]
        data = []

        for error in errors:
            data.append(
                [
                    f"`{error.name}`",
                    error.count,
                    f"{error.percentage:.1f}%",
                    "Yes" if error.fixable else "No",
                    f"{error.priority_score:.2f}",
                ]
            )

        return tabulate(data, headers=headers, tablefmt="github")

    def _format_roadmap_table(
        self, improvements: list[ImprovementItem], max_items: int = 10
    ) -> str:
        """Format improvement roadmap as a markdown table."""
        headers = ["Priority", "Error Category", "Stage", "Models", "Effort", "Score"]
        data = []

        for item in improvements[:max_items]:
            if item.priority_score > 0:  # Only show fixable items
                data.append(
                    [
                        item.rank,
                        f"`{item.error_category}`",
                        item.stage,
                        item.models_affected,
                        f"{item.effort_hours}h",
                        f"{item.priority_score:.2f}",
                    ]
                )

        return tabulate(data, headers=headers, tablefmt="github")

    def _format_stage_overview_table(
        self, summary: FailureSummary, baseline: BaselineMetrics
    ) -> str:
        """Format stage overview table for failure report."""
        headers = ["Stage", "Failures", "% of Total Models", "Top Error"]

        # Get top error for each stage
        parse_errors = baseline.parse.error_breakdown
        translate_errors = baseline.translate.error_breakdown
        solve_errors = baseline.solve.error_breakdown

        parse_top = max(parse_errors, key=lambda k: parse_errors[k]) if parse_errors else "N/A"
        translate_top = (
            max(translate_errors, key=lambda k: translate_errors[k]) if translate_errors else "N/A"
        )
        solve_top = max(solve_errors, key=lambda k: solve_errors[k]) if solve_errors else "N/A"

        data = [
            [
                "Parse",
                summary.parse_failures,
                f"{summary.parse_failures / summary.total_models * 100:.1f}%",
                f"`{parse_top}`",
            ],
            [
                "Translate",
                summary.translate_failures,
                f"{summary.translate_failures / summary.total_models * 100:.1f}%",
                f"`{translate_top}`",
            ],
            [
                "Solve",
                summary.solve_failures,
                f"{summary.solve_failures / summary.total_models * 100:.1f}%",
                f"`{solve_top}`",
            ],
        ]
        return tabulate(data, headers=headers, tablefmt="github")

    def _format_progress_table(self, comparison: ComparisonSummary) -> str:
        """Format progress comparison table."""
        headers = ["Metric", "Previous", "Current", "Change", "Trend"]
        data = []

        deltas = comparison.rate_deltas

        def trend_icon(delta: float) -> str:
            if delta > 0.001:
                return "✅"
            elif delta < -0.001:
                return "⚠️"
            return "➡️"

        for name, rate_delta in [
            ("Parse Rate", deltas.parse),
            ("Translate Rate", deltas.translate),
            ("Solve Rate", deltas.solve),
            ("Pipeline Rate", deltas.full_pipeline),
        ]:
            data.append(
                [
                    name,
                    f"{rate_delta.previous_rate * 100:.1f}%",
                    f"{rate_delta.current_rate * 100:.1f}%",
                    f"{rate_delta.delta * 100:+.1f}%",
                    trend_icon(rate_delta.delta),
                ]
            )

        return tabulate(data, headers=headers, tablefmt="github")

    def _generate_executive_summary(self, summary: StatusSummary, baseline: BaselineMetrics) -> str:
        """Generate executive summary text."""
        lines = []
        lines.append(
            f"The nlp2mcp pipeline was tested against **{summary.total_models}** "
            f"GAMSLIB models on **{summary.baseline_date}** ({summary.sprint})."
        )
        lines.append("")
        lines.append(
            f"- **Full Pipeline Success:** {summary.pipeline_success} models "
            f"({summary.pipeline_rate * 100:.1f}%)"
        )
        lines.append(
            f"- **Parse Success:** {summary.parse_success}/{summary.total_models} "
            f"({summary.parse_rate * 100:.1f}%)"
        )
        lines.append(
            f"- **Translate Success:** {summary.translate_success}/"
            f"{baseline.translate.attempted} ({summary.translate_rate * 100:.1f}%)"
        )
        lines.append(
            f"- **Solve Success:** {summary.solve_success}/"
            f"{baseline.solve.attempted} ({summary.solve_rate * 100:.1f}%)"
        )

        # Identify bottleneck
        stage_rates = {
            "parse": summary.parse_rate,
            "translate": summary.translate_rate,
            "solve": summary.solve_rate,
        }
        bottleneck = min(stage_rates, key=stage_rates.get)  # type: ignore[arg-type]
        lines.append("")
        lines.append(
            f"**Key Bottleneck:** {bottleneck.capitalize()} stage "
            f"({stage_rates[bottleneck] * 100:.1f}% success rate)"
        )

        return "\n".join(lines)

    def render_status_report(
        self,
        baseline: BaselineMetrics,
        summary: StatusSummary,
        comparison: ComparisonSummary | None = None,
        data_source: str = "baseline_metrics.json",
    ) -> str:
        """
        Render a status report to markdown.

        Args:
            baseline: Loaded baseline metrics
            summary: Status summary from StatusAnalyzer
            comparison: Optional comparison summary from ProgressAnalyzer
            data_source: Name of the data source file

        Returns:
            Rendered markdown string

        Raises:
            RenderError: If template is not found or rendering fails
        """
        try:
            template = self._env.get_template("status_report.md.j2")
        except TemplateNotFound as e:
            raise RenderError(f"Status report template not found: {e}") from e

        # Collect all errors for blocker table

        failure_analyzer = FailureAnalyzer(baseline)
        all_errors: list[ErrorCategory] = []
        for stage in ["parse", "translate", "solve"]:
            all_errors.extend(failure_analyzer.get_error_categories(stage))

        # Prepare context
        context: dict[str, Any] = {
            "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "environment": baseline.environment,
            "data_source": data_source,
            "executive_summary": self._generate_executive_summary(summary, baseline),
            "stage_table": self._format_stage_table(baseline, summary),
            "type_table": self._format_type_table(baseline),
            "blocker_table": self._format_blocker_table(all_errors),
            "successful_models": baseline.full_pipeline.successful_models,
            "parse_timing": baseline.parse.timing,
            "translate_timing": baseline.translate.timing,
            "solve_timing": baseline.solve.timing,
            "parse_timing_table": (
                self._format_timing_table(baseline.parse.timing) if baseline.parse.timing else None
            ),
            "translate_timing_table": (
                self._format_timing_table(baseline.translate.timing)
                if baseline.translate.timing
                else None
            ),
            "solve_timing_table": (
                self._format_timing_table(baseline.solve.timing) if baseline.solve.timing else None
            ),
            "comparison": None,
        }

        if comparison:
            context["comparison"] = {
                "previous_sprint": comparison.previous_sprint or "Previous",
                "current_sprint": comparison.current_sprint or "Current",
                "has_regressions": len(comparison.regressions) > 0,
                "regressions": [
                    {"stage": r.stage, "description": r.description} for r in comparison.regressions
                ],
            }
            context["progress_table"] = self._format_progress_table(comparison)

        try:
            return template.render(**context)
        except Exception as e:
            raise RenderError(f"Failed to render status report: {e}") from e

    def render_failure_report(
        self,
        baseline: BaselineMetrics,
        failure_summary: FailureSummary,
        parse_errors: list[ErrorCategory],
        translate_errors: list[ErrorCategory],
        solve_errors: list[ErrorCategory],
        improvements: list[ImprovementItem],
        comparison: ComparisonSummary | None = None,
        data_source: str = "baseline_metrics.json",
    ) -> str:
        """
        Render a failure analysis report to markdown.

        Args:
            baseline: Loaded baseline metrics
            failure_summary: Failure summary from FailureAnalyzer
            parse_errors: Parse error categories
            translate_errors: Translate error categories
            solve_errors: Solve error categories
            improvements: Prioritized improvement items
            comparison: Optional comparison summary from ProgressAnalyzer
            data_source: Name of the data source file

        Returns:
            Rendered markdown string

        Raises:
            RenderError: If template is not found or rendering fails
        """
        try:
            template = self._env.get_template("failure_report.md.j2")
        except TemplateNotFound as e:
            raise RenderError(f"Failure report template not found: {e}") from e

        # Calculate failure rates
        parse_failure_rate = (
            baseline.parse.failure / baseline.parse.attempted
            if baseline.parse.attempted > 0
            else 0.0
        )
        translate_failure_rate = (
            baseline.translate.failure / baseline.translate.attempted
            if baseline.translate.attempted > 0
            else 0.0
        )
        solve_failure_rate = (
            baseline.solve.failure / baseline.solve.attempted
            if baseline.solve.attempted > 0
            else 0.0
        )

        # Prepare context
        context: dict[str, Any] = {
            "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "environment": baseline.environment,
            "data_source": data_source,
            "summary": failure_summary,
            "stage_overview_table": self._format_stage_overview_table(failure_summary, baseline),
            "parse_failures": baseline.parse.failure,
            "parse_failure_rate": parse_failure_rate,
            "parse_error_table": self._format_error_table(parse_errors),
            "parse_errors": parse_errors,
            "translate_failures": baseline.translate.failure,
            "translate_failure_rate": translate_failure_rate,
            "translate_error_table": self._format_error_table(translate_errors),
            "translate_errors": translate_errors,
            "solve_failures": baseline.solve.failure,
            "solve_failure_rate": solve_failure_rate,
            "solve_error_table": self._format_error_table(solve_errors),
            "solve_errors": solve_errors,
            "roadmap_table": self._format_roadmap_table(improvements),
            "comparison": None,
        }

        if comparison:
            context["comparison"] = {
                "previous_sprint": comparison.previous_sprint or "Previous",
                "current_sprint": comparison.current_sprint or "Current",
                "has_regressions": len(comparison.regressions) > 0,
                "regressions": [
                    {"stage": r.stage, "description": r.description} for r in comparison.regressions
                ],
            }
            context["progress_table"] = self._format_progress_table(comparison)

            # Format error changes table
            headers = ["Category", "Previous", "Current", "Change"]
            data = []
            for change in comparison.error_changes[:10]:
                data.append(
                    [
                        f"`{change.category}`",
                        change.previous_count,
                        change.current_count,
                        f"{change.delta:+d}",
                    ]
                )
            context["error_changes_table"] = tabulate(data, headers=headers, tablefmt="github")

        try:
            return template.render(**context)
        except Exception as e:
            raise RenderError(f"Failed to render failure report: {e}") from e

    def render_to_file(self, content: str, output_path: Path | str) -> None:
        """
        Write rendered content to a file.

        Args:
            content: Rendered markdown content
            output_path: Path to output file

        Raises:
            RenderError: If writing fails
        """
        output_path = Path(output_path)

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")
        except OSError as e:
            raise RenderError(f"Failed to write report to {output_path}: {e}") from e

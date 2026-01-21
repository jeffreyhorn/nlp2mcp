"""
Integration tests for the report generation CLI.

Tests end-to-end report generation using actual baseline_metrics.json data.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.reporting.analyzers.failure_analyzer import FailureAnalyzer
from src.reporting.analyzers.status_analyzer import StatusAnalyzer
from src.reporting.data_loader import load_baseline_metrics
from src.reporting.generate_report import main
from src.reporting.renderers.markdown_renderer import MarkdownRenderer

# Path to actual baseline metrics
BASELINE_PATH = Path("data/gamslib/baseline_metrics.json")


class TestCLIStatusReport:
    """Test CLI status report generation."""

    @pytest.fixture
    def output_dir(self, tmp_path: Path) -> Path:
        """Create a temporary output directory."""
        return tmp_path / "reports"

    def test_generate_status_report(self, output_dir: Path) -> None:
        """Test generating a status report."""
        if not BASELINE_PATH.exists():
            pytest.skip("Baseline metrics file not found")

        result = main(
            [
                "--type=status",
                f"--output={output_dir}",
                f"--baseline={BASELINE_PATH}",
            ]
        )

        assert result == 0
        status_file = output_dir / "GAMSLIB_STATUS.md"
        assert status_file.exists()

        content = status_file.read_text()
        assert "# GAMSLIB Pipeline Status Report" in content
        assert "Executive Summary" in content
        assert "Pipeline Stage Summary" in content
        assert "Parse" in content
        assert "Translate" in content
        assert "Solve" in content

    def test_status_report_contains_metrics(self, output_dir: Path) -> None:
        """Test that status report contains expected metrics."""
        if not BASELINE_PATH.exists():
            pytest.skip("Baseline metrics file not found")

        result = main(
            [
                "--type=status",
                f"--output={output_dir}",
                f"--baseline={BASELINE_PATH}",
            ]
        )

        assert result == 0
        content = (output_dir / "GAMSLIB_STATUS.md").read_text()

        # Check for percentage patterns (21.3%, etc.)
        assert "%" in content
        # Check for model count
        assert "160" in content or "models" in content.lower()

    def test_dry_run_does_not_create_file(self, output_dir: Path) -> None:
        """Test that dry run doesn't create files."""
        if not BASELINE_PATH.exists():
            pytest.skip("Baseline metrics file not found")

        result = main(
            [
                "--type=status",
                f"--output={output_dir}",
                f"--baseline={BASELINE_PATH}",
                "--dry-run",
            ]
        )

        assert result == 0
        status_file = output_dir / "GAMSLIB_STATUS.md"
        assert not status_file.exists()


class TestCLIFailureReport:
    """Test CLI failure report generation."""

    @pytest.fixture
    def output_dir(self, tmp_path: Path) -> Path:
        """Create a temporary output directory."""
        return tmp_path / "reports"

    def test_generate_failure_report(self, output_dir: Path) -> None:
        """Test generating a failure analysis report."""
        if not BASELINE_PATH.exists():
            pytest.skip("Baseline metrics file not found")

        result = main(
            [
                "--type=failure",
                f"--output={output_dir}",
                f"--baseline={BASELINE_PATH}",
            ]
        )

        assert result == 0
        failure_file = output_dir / "FAILURE_ANALYSIS.md"
        assert failure_file.exists()

        content = failure_file.read_text()
        assert "# GAMSLIB Failure Analysis Report" in content
        assert "Executive Summary" in content
        assert "Parse Failures" in content
        assert "Translation Failures" in content
        assert "Solve Failures" in content
        assert "Improvement Roadmap" in content

    def test_failure_report_contains_error_categories(self, output_dir: Path) -> None:
        """Test that failure report contains error categories."""
        if not BASELINE_PATH.exists():
            pytest.skip("Baseline metrics file not found")

        result = main(
            [
                "--type=failure",
                f"--output={output_dir}",
                f"--baseline={BASELINE_PATH}",
            ]
        )

        assert result == 0
        content = (output_dir / "FAILURE_ANALYSIS.md").read_text()

        # Check for error category patterns
        assert "lexer_invalid_char" in content or "Error Breakdown" in content
        assert "Priority Score" in content or "priority" in content.lower()


class TestCLIAllReports:
    """Test CLI generation of all reports."""

    @pytest.fixture
    def output_dir(self, tmp_path: Path) -> Path:
        """Create a temporary output directory."""
        return tmp_path / "reports"

    def test_generate_all_reports(self, output_dir: Path) -> None:
        """Test generating all reports at once."""
        if not BASELINE_PATH.exists():
            pytest.skip("Baseline metrics file not found")

        result = main(
            [
                "--type=all",
                f"--output={output_dir}",
                f"--baseline={BASELINE_PATH}",
            ]
        )

        assert result == 0

        status_file = output_dir / "GAMSLIB_STATUS.md"
        failure_file = output_dir / "FAILURE_ANALYSIS.md"

        assert status_file.exists()
        assert failure_file.exists()

    def test_verbose_output(self, output_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """Test verbose output mode."""
        if not BASELINE_PATH.exists():
            pytest.skip("Baseline metrics file not found")

        result = main(
            [
                "--type=status",
                f"--output={output_dir}",
                f"--baseline={BASELINE_PATH}",
                "--verbose",
            ]
        )

        assert result == 0
        captured = capsys.readouterr()
        assert "Loading baseline metrics" in captured.out or "Rendering" in captured.out


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_missing_baseline_file(self, tmp_path: Path) -> None:
        """Test error when baseline file doesn't exist."""
        result = main(
            [
                "--type=status",
                f"--output={tmp_path}",
                "--baseline=nonexistent.json",
            ]
        )

        assert result == 1

    def test_invalid_report_type(self) -> None:
        """Test error for invalid report type (handled by argparse)."""
        with pytest.raises(SystemExit):
            main(["--type=invalid"])


class TestMarkdownRendererIntegration:
    """Test MarkdownRenderer with actual data."""

    def test_render_status_report_with_actual_data(self) -> None:
        """Test rendering status report with actual baseline data."""
        if not BASELINE_PATH.exists():
            pytest.skip("Baseline metrics file not found")

        baseline = load_baseline_metrics(BASELINE_PATH)
        analyzer = StatusAnalyzer(baseline)
        summary = analyzer.get_summary()

        renderer = MarkdownRenderer()
        content = renderer.render_status_report(baseline, summary)

        assert "# GAMSLIB Pipeline Status Report" in content
        assert f"{summary.parse_rate * 100:.1f}%" in content
        assert "Executive Summary" in content

    def test_render_failure_report_with_actual_data(self) -> None:
        """Test rendering failure report with actual baseline data."""
        if not BASELINE_PATH.exists():
            pytest.skip("Baseline metrics file not found")

        baseline = load_baseline_metrics(BASELINE_PATH)
        analyzer = FailureAnalyzer(baseline)

        failure_summary = analyzer.get_summary()
        parse_errors = analyzer.get_error_categories("parse")
        translate_errors = analyzer.get_error_categories("translate")
        solve_errors = analyzer.get_error_categories("solve")
        improvements = analyzer.get_prioritized_improvements()

        renderer = MarkdownRenderer()
        content = renderer.render_failure_report(
            baseline=baseline,
            failure_summary=failure_summary,
            parse_errors=parse_errors,
            translate_errors=translate_errors,
            solve_errors=solve_errors,
            improvements=improvements,
        )

        assert "# GAMSLIB Failure Analysis Report" in content
        assert "Executive Summary" in content
        assert "Improvement Roadmap" in content


class TestReportAccuracy:
    """Test that reports contain accurate data."""

    def test_status_report_metrics_match_baseline(self, tmp_path: Path) -> None:
        """Test that status report metrics match baseline_metrics.json."""
        if not BASELINE_PATH.exists():
            pytest.skip("Baseline metrics file not found")

        baseline = load_baseline_metrics(BASELINE_PATH)

        # Generate report
        result = main(
            [
                "--type=status",
                f"--output={tmp_path}",
                f"--baseline={BASELINE_PATH}",
            ]
        )
        assert result == 0

        content = (tmp_path / "GAMSLIB_STATUS.md").read_text()

        # Verify parse rate is in report
        expected_parse_rate = f"{baseline.parse.success_rate * 100:.1f}%"
        assert (
            expected_parse_rate in content
        ), f"Expected parse rate {expected_parse_rate} not found"

        # Verify total models
        assert str(baseline.total_models) in content

    def test_failure_report_error_counts_match_baseline(self, tmp_path: Path) -> None:
        """Test that failure report error counts match baseline."""
        if not BASELINE_PATH.exists():
            pytest.skip("Baseline metrics file not found")

        baseline = load_baseline_metrics(BASELINE_PATH)

        # Generate report
        result = main(
            [
                "--type=failure",
                f"--output={tmp_path}",
                f"--baseline={BASELINE_PATH}",
            ]
        )
        assert result == 0

        content = (tmp_path / "FAILURE_ANALYSIS.md").read_text()

        # Verify parse failure count
        assert str(baseline.parse.failure) in content

        # Verify total models
        assert str(baseline.total_models) in content

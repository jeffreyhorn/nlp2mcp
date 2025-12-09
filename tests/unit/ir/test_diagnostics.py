"""Tests for pipeline diagnostics infrastructure.

Sprint 12 Day 7: Tests for JSON diagnostics schema v1.0.0.
"""

import json
from datetime import datetime

import pytest

from src.ir.diagnostics import (
    DiagnosticContext,
    Stage,
    StageMetrics,
    create_report,
)


class TestDiagnosticReport:
    """Tests for DiagnosticReport class."""

    def test_create_report(self):
        """Test creating a new diagnostic report."""
        report = create_report("test.gms")
        assert report.model_name == "test.gms"
        assert len(report.stages) == 0
        assert report.total_duration_ms == 0.0
        assert report.overall_success is False  # No stages = not successful

    def test_add_stage(self):
        """Test adding stage metrics to report."""
        report = create_report("test.gms")
        metrics = StageMetrics(
            stage=Stage.PARSE,
            duration_ms=10.5,
            success=True,
            details={"lines": 100},
        )
        report.add_stage(metrics)

        assert Stage.PARSE in report.stages
        assert report.stages[Stage.PARSE].duration_ms == 10.5
        assert report.stages[Stage.PARSE].success is True

    def test_total_duration(self):
        """Test total duration calculation."""
        report = create_report("test.gms")
        report.add_stage(StageMetrics(stage=Stage.PARSE, duration_ms=10.0, success=True))
        report.add_stage(StageMetrics(stage=Stage.SEMANTIC, duration_ms=5.0, success=True))

        assert report.total_duration_ms == 15.0

    def test_overall_success_all_passed(self):
        """Test overall success when all stages pass."""
        report = create_report("test.gms")
        report.add_stage(StageMetrics(stage=Stage.PARSE, duration_ms=10.0, success=True))
        report.add_stage(StageMetrics(stage=Stage.SEMANTIC, duration_ms=5.0, success=True))

        assert report.overall_success is True

    def test_overall_success_one_failed(self):
        """Test overall success when one stage fails."""
        report = create_report("test.gms")
        report.add_stage(StageMetrics(stage=Stage.PARSE, duration_ms=10.0, success=True))
        report.add_stage(StageMetrics(stage=Stage.SEMANTIC, duration_ms=5.0, success=False))

        assert report.overall_success is False


class TestJsonV1Schema:
    """Tests for JSON schema v1.0.0 output."""

    def test_schema_version(self):
        """Test schema version is present and correct."""
        report = create_report("test.gms")
        report.add_stage(StageMetrics(stage=Stage.PARSE, duration_ms=10.0, success=True))

        json_output = report.to_json_v1()

        assert json_output["schema_version"] == "1.0.0"

    def test_generated_at_format(self):
        """Test generated_at is valid ISO 8601 timestamp."""
        report = create_report("test.gms")
        report.add_stage(StageMetrics(stage=Stage.PARSE, duration_ms=10.0, success=True))

        json_output = report.to_json_v1()

        # Should be parseable as ISO format
        timestamp = json_output["generated_at"]
        parsed = datetime.fromisoformat(timestamp)
        assert parsed is not None

    def test_model_name(self):
        """Test model name is included."""
        report = create_report("example.gms")
        report.add_stage(StageMetrics(stage=Stage.PARSE, duration_ms=10.0, success=True))

        json_output = report.to_json_v1()

        assert json_output["model_name"] == "example.gms"

    def test_stages_structure(self):
        """Test stages are properly structured."""
        report = create_report("test.gms")
        report.add_stage(
            StageMetrics(
                stage=Stage.PARSE,
                duration_ms=10.5,
                success=True,
                error=None,
                details={"lines": 100, "tokens": 500},
            )
        )

        json_output = report.to_json_v1()

        assert "Parse" in json_output["stages"]
        parse_stage = json_output["stages"]["Parse"]
        assert parse_stage["duration_ms"] == 10.5
        assert parse_stage["success"] is True
        assert parse_stage["error"] is None
        assert parse_stage["details"]["lines"] == 100
        assert parse_stage["details"]["tokens"] == 500

    def test_stages_with_error(self):
        """Test stage with error message."""
        report = create_report("test.gms")
        report.add_stage(
            StageMetrics(
                stage=Stage.PARSE,
                duration_ms=5.0,
                success=False,
                error="Syntax error at line 42",
            )
        )

        json_output = report.to_json_v1()

        parse_stage = json_output["stages"]["Parse"]
        assert parse_stage["success"] is False
        assert parse_stage["error"] == "Syntax error at line 42"

    def test_summary_structure(self):
        """Test summary object structure."""
        report = create_report("test.gms")
        report.add_stage(StageMetrics(stage=Stage.PARSE, duration_ms=10.0, success=True))
        report.add_stage(StageMetrics(stage=Stage.SEMANTIC, duration_ms=5.0, success=True))
        report.add_stage(StageMetrics(stage=Stage.SIMPLIFICATION, duration_ms=8.0, success=False))

        json_output = report.to_json_v1()

        summary = json_output["summary"]
        assert summary["stages_completed"] == 3
        assert summary["stages_failed"] == 1
        assert summary["stages_skipped"] == 2  # IR_GENERATION and MCP_GENERATION
        assert summary["parse_duration_ms"] == 10.0
        assert summary["semantic_duration_ms"] == 5.0
        assert summary["simplification_duration_ms"] == 8.0
        assert summary["ir_generation_duration_ms"] == 0.0
        assert summary["mcp_generation_duration_ms"] == 0.0

    def test_json_serializable(self):
        """Test output is valid JSON."""
        report = create_report("test.gms")
        report.add_stage(
            StageMetrics(
                stage=Stage.PARSE,
                duration_ms=10.5,
                success=True,
                details={"lines": 100},
            )
        )

        json_output = report.to_json_v1()

        # Should not raise
        json_str = json.dumps(json_output)
        assert isinstance(json_str, str)

        # Should round-trip
        parsed = json.loads(json_str)
        assert parsed["schema_version"] == "1.0.0"

    def test_all_stages_success(self):
        """Test with all 5 stages successfully completing."""
        report = create_report("complete.gms")
        report.add_stage(StageMetrics(stage=Stage.PARSE, duration_ms=10.0, success=True))
        report.add_stage(StageMetrics(stage=Stage.SEMANTIC, duration_ms=5.0, success=True))
        report.add_stage(StageMetrics(stage=Stage.SIMPLIFICATION, duration_ms=8.0, success=True))
        report.add_stage(StageMetrics(stage=Stage.IR_GENERATION, duration_ms=12.0, success=True))
        report.add_stage(StageMetrics(stage=Stage.MCP_GENERATION, duration_ms=3.0, success=True))

        json_output = report.to_json_v1()

        assert json_output["overall_success"] is True
        assert json_output["total_duration_ms"] == 38.0
        assert json_output["summary"]["stages_completed"] == 5
        assert json_output["summary"]["stages_failed"] == 0
        assert json_output["summary"]["stages_skipped"] == 0


class TestDiagnosticContext:
    """Tests for DiagnosticContext context manager."""

    def test_timing(self):
        """Test that context manager captures timing."""
        report = create_report("test.gms")

        with DiagnosticContext(report, Stage.PARSE) as ctx:
            # Simulate some work
            total = sum(range(1000))
            ctx.add_detail("result", total)

        assert Stage.PARSE in report.stages
        assert report.stages[Stage.PARSE].duration_ms > 0
        assert report.stages[Stage.PARSE].success is True

    def test_add_detail(self):
        """Test adding details during context."""
        report = create_report("test.gms")

        with DiagnosticContext(report, Stage.PARSE) as ctx:
            ctx.add_detail("lines", 100)
            ctx.add_detail("tokens", 500)

        assert report.stages[Stage.PARSE].details["lines"] == 100
        assert report.stages[Stage.PARSE].details["tokens"] == 500

    def test_exception_handling(self):
        """Test that exceptions are captured but not suppressed."""
        report = create_report("test.gms")

        with pytest.raises(ValueError, match="Test error"):
            with DiagnosticContext(report, Stage.PARSE):
                raise ValueError("Test error")

        assert Stage.PARSE in report.stages
        assert report.stages[Stage.PARSE].success is False
        assert report.stages[Stage.PARSE].error == "Test error"


class TestTextOutput:
    """Tests for text output format."""

    def test_text_output_structure(self):
        """Test text output has expected structure."""
        report = create_report("test.gms")
        report.add_stage(StageMetrics(stage=Stage.PARSE, duration_ms=10.0, success=True))

        text = report.to_text()

        assert "Diagnostic Report: test.gms" in text
        assert "Parse" in text
        assert "SUCCESS" in text

    def test_text_output_failed_stage(self):
        """Test text output shows failures."""
        report = create_report("test.gms")
        report.add_stage(
            StageMetrics(
                stage=Stage.PARSE,
                duration_ms=5.0,
                success=False,
                error="Syntax error",
            )
        )

        text = report.to_text()

        assert "FAILED" in text
        assert "Syntax error" in text

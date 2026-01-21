"""Unit tests for the data loader module."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from src.reporting.data_loader import (
    ComparisonMetrics,
    DataLoadError,
    Environment,
    FullPipelineMetrics,
    StageMetrics,
    TimingStats,
    TypeBreakdown,
    load_baseline_metrics,
    load_gamslib_status,
)


class TestTimingStats:
    """Tests for TimingStats dataclass."""

    def test_from_dict_complete(self) -> None:
        """Test creating TimingStats from complete dictionary."""
        data = {
            "scope": "successful_models",
            "count": 34,
            "mean_ms": 141.5,
            "median_ms": 125.8,
            "stddev_ms": 89.4,
            "min_ms": 15.0,
            "max_ms": 421.4,
            "p90_ms": 248.9,
            "p99_ms": 421.4,
        }
        stats = TimingStats.from_dict(data)

        assert stats.scope == "successful_models"
        assert stats.count == 34
        assert stats.mean_ms == 141.5
        assert stats.median_ms == 125.8
        assert stats.stddev_ms == 89.4
        assert stats.min_ms == 15.0
        assert stats.max_ms == 421.4
        assert stats.p90_ms == 248.9
        assert stats.p99_ms == 421.4

    def test_from_dict_empty(self) -> None:
        """Test creating TimingStats from empty dictionary uses defaults."""
        stats = TimingStats.from_dict({})

        assert stats.scope == "unknown"
        assert stats.count == 0
        assert stats.mean_ms == 0.0


class TestTypeBreakdown:
    """Tests for TypeBreakdown dataclass."""

    def test_from_dict_complete(self) -> None:
        """Test creating TypeBreakdown from complete dictionary."""
        data = {"attempted": 94, "success": 26, "success_rate": 0.2766}
        breakdown = TypeBreakdown.from_dict(data)

        assert breakdown.attempted == 94
        assert breakdown.success == 26
        assert breakdown.success_rate == 0.2766

    def test_from_dict_empty(self) -> None:
        """Test creating TypeBreakdown from empty dictionary uses defaults."""
        breakdown = TypeBreakdown.from_dict({})

        assert breakdown.attempted == 0
        assert breakdown.success == 0
        assert breakdown.success_rate == 0.0


class TestStageMetrics:
    """Tests for StageMetrics dataclass."""

    def test_from_dict_with_timing_and_types(self) -> None:
        """Test creating StageMetrics with timing and type breakdown."""
        data = {
            "attempted": 160,
            "success": 34,
            "failure": 126,
            "success_rate": 0.2125,
            "cascade_skip": 0,
            "timing": {
                "scope": "successful_models",
                "count": 34,
                "mean_ms": 141.5,
                "median_ms": 125.8,
                "stddev_ms": 89.4,
                "min_ms": 15.0,
                "max_ms": 421.4,
                "p90_ms": 248.9,
                "p99_ms": 421.4,
            },
            "by_type": {
                "NLP": {"attempted": 94, "success": 26, "success_rate": 0.2766},
                "LP": {"attempted": 57, "success": 5, "success_rate": 0.0877},
            },
            "error_breakdown": {"lexer_invalid_char": 109, "internal_error": 17},
        }
        metrics = StageMetrics.from_dict(data)

        assert metrics.attempted == 160
        assert metrics.success == 34
        assert metrics.failure == 126
        assert metrics.success_rate == 0.2125
        assert metrics.timing is not None
        assert metrics.timing.count == 34
        assert len(metrics.by_type) == 2
        assert metrics.by_type["NLP"].success == 26
        assert metrics.error_breakdown["lexer_invalid_char"] == 109

    def test_from_dict_minimal(self) -> None:
        """Test creating StageMetrics from minimal dictionary."""
        metrics = StageMetrics.from_dict({})

        assert metrics.attempted == 0
        assert metrics.timing is None
        assert metrics.by_type == {}
        assert metrics.error_breakdown == {}


class TestComparisonMetrics:
    """Tests for ComparisonMetrics dataclass."""

    def test_from_dict_complete(self) -> None:
        """Test creating ComparisonMetrics from complete dictionary."""
        data = {
            "attempted": 3,
            "match": 1,
            "mismatch": 2,
            "skipped": 0,
            "cascade_skip": 157,
            "match_rate": 0.3333,
        }
        metrics = ComparisonMetrics.from_dict(data)

        assert metrics.attempted == 3
        assert metrics.match == 1
        assert metrics.mismatch == 2
        assert metrics.skipped == 0
        assert metrics.cascade_skip == 157
        assert metrics.match_rate == 0.3333


class TestFullPipelineMetrics:
    """Tests for FullPipelineMetrics dataclass."""

    def test_from_dict_complete(self) -> None:
        """Test creating FullPipelineMetrics from complete dictionary."""
        data = {
            "success": 1,
            "total": 160,
            "success_rate": 0.0063,
            "successful_models": ["hs62"],
        }
        metrics = FullPipelineMetrics.from_dict(data)

        assert metrics.success == 1
        assert metrics.total == 160
        assert metrics.success_rate == 0.0063
        assert metrics.successful_models == ["hs62"]

    def test_from_dict_empty_models(self) -> None:
        """Test creating FullPipelineMetrics with no successful models."""
        metrics = FullPipelineMetrics.from_dict({"success": 0, "total": 10})

        assert metrics.successful_models == []


class TestEnvironment:
    """Tests for Environment dataclass."""

    def test_from_dict_complete(self) -> None:
        """Test creating Environment from complete dictionary."""
        data = {
            "nlp2mcp_version": "0.1.0",
            "python_version": "3.12.8",
            "gams_version": "51.3.0",
            "path_solver_version": "5.2.01",
            "platform": "Darwin",
            "platform_version": "24.6.0",
        }
        env = Environment.from_dict(data)

        assert env.nlp2mcp_version == "0.1.0"
        assert env.python_version == "3.12.8"
        assert env.gams_version == "51.3.0"

    def test_from_dict_empty(self) -> None:
        """Test creating Environment from empty dictionary uses defaults."""
        env = Environment.from_dict({})

        assert env.nlp2mcp_version == "unknown"
        assert env.python_version == "unknown"


class TestLoadBaselineMetrics:
    """Tests for load_baseline_metrics function."""

    def test_load_valid_file(self) -> None:
        """Test loading a valid baseline_metrics.json file."""
        data = {
            "schema_version": "1.0.0",
            "baseline_date": "2026-01-15",
            "sprint": "Sprint 15",
            "environment": {
                "nlp2mcp_version": "0.1.0",
                "python_version": "3.12.8",
                "gams_version": "51.3.0",
                "path_solver_version": "5.2.01",
                "platform": "Darwin",
                "platform_version": "24.6.0",
            },
            "total_models": 160,
            "model_types": {"NLP": 94, "LP": 57, "QCP": 9},
            "parse": {
                "attempted": 160,
                "success": 34,
                "failure": 126,
                "success_rate": 0.2125,
            },
            "translate": {
                "attempted": 34,
                "success": 17,
                "failure": 17,
                "cascade_skip": 126,
                "success_rate": 0.5,
            },
            "solve": {
                "attempted": 17,
                "success": 3,
                "failure": 14,
                "cascade_skip": 143,
                "success_rate": 0.1765,
            },
            "comparison": {
                "attempted": 3,
                "match": 1,
                "mismatch": 2,
                "skipped": 0,
                "cascade_skip": 157,
                "match_rate": 0.3333,
            },
            "full_pipeline": {
                "success": 1,
                "total": 160,
                "success_rate": 0.0063,
                "successful_models": ["hs62"],
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = Path(f.name)

        try:
            metrics = load_baseline_metrics(temp_path)

            assert metrics.schema_version == "1.0.0"
            assert metrics.baseline_date == "2026-01-15"
            assert metrics.sprint == "Sprint 15"
            assert metrics.total_models == 160
            assert metrics.parse.success_rate == 0.2125
            assert metrics.translate.success_rate == 0.5
            assert metrics.solve.success_rate == 0.1765
            assert metrics.full_pipeline.success == 1
        finally:
            temp_path.unlink()

    def test_load_missing_file(self) -> None:
        """Test that loading a missing file raises DataLoadError."""
        with pytest.raises(DataLoadError, match="Baseline metrics file not found"):
            load_baseline_metrics("/nonexistent/path/baseline_metrics.json")

    def test_load_invalid_json(self) -> None:
        """Test that loading invalid JSON raises DataLoadError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            temp_path = Path(f.name)

        try:
            with pytest.raises(DataLoadError, match="Invalid JSON"):
                load_baseline_metrics(temp_path)
        finally:
            temp_path.unlink()

    def test_load_missing_required_fields(self) -> None:
        """Test that loading file with missing required fields raises DataLoadError."""
        data = {
            "schema_version": "1.0.0",
            # Missing baseline_date, parse, translate, solve
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(DataLoadError, match="Missing required fields"):
                load_baseline_metrics(temp_path)
        finally:
            temp_path.unlink()

    def test_load_actual_baseline_file(self) -> None:
        """Test loading the actual baseline_metrics.json file."""
        baseline_path = Path("data/gamslib/baseline_metrics.json")
        if not baseline_path.exists():
            pytest.skip("baseline_metrics.json not found")

        metrics = load_baseline_metrics(baseline_path)

        assert metrics.schema_version == "1.0.0"
        assert metrics.total_models == 160
        assert metrics.parse.success == 34
        assert metrics.translate.success == 17
        assert metrics.solve.success == 3
        assert metrics.full_pipeline.success == 1


class TestLoadGamslibStatus:
    """Tests for load_gamslib_status function."""

    def test_load_valid_file(self) -> None:
        """Test loading a valid gamslib_status.json file."""
        data = {
            "schema_version": "2.1.0",
            "total_models": 1,
            "models": [
                {
                    "model_id": "hs62",
                    "model_name": "Test Model",
                    "gamslib_type": "NLP",
                    "parse_status": "success",
                    "translate_status": "success",
                    "solve_status": "success",
                }
            ],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = Path(f.name)

        try:
            status = load_gamslib_status(temp_path)

            assert "models" in status
            assert len(status["models"]) == 1
            assert status["models"][0]["model_id"] == "hs62"
            assert status["models"][0]["parse_status"] == "success"
        finally:
            temp_path.unlink()

    def test_load_missing_file(self) -> None:
        """Test that loading a missing file raises DataLoadError."""
        with pytest.raises(DataLoadError, match="GAMSLIB status file not found"):
            load_gamslib_status("/nonexistent/path/gamslib_status.json")

    def test_load_missing_models_field(self) -> None:
        """Test that loading file without 'models' field raises DataLoadError."""
        data = {"version": "1.0.0"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(DataLoadError, match="Missing 'models' field"):
                load_gamslib_status(temp_path)
        finally:
            temp_path.unlink()

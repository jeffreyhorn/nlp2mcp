"""
Data loader for pipeline metrics and results.

Loads and validates baseline_metrics.json and pipeline results data,
providing typed data classes for type safety.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class DataLoadError(Exception):
    """Exception raised when data loading fails."""


@dataclass
class TimingStats:
    """Timing statistics for a pipeline stage."""

    scope: str
    count: int
    mean_ms: float
    median_ms: float
    stddev_ms: float
    min_ms: float
    max_ms: float
    p90_ms: float
    p99_ms: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TimingStats:
        """Create TimingStats from a dictionary."""
        return cls(
            scope=data.get("scope", "unknown"),
            count=data.get("count", 0),
            mean_ms=data.get("mean_ms", 0.0),
            median_ms=data.get("median_ms", 0.0),
            stddev_ms=data.get("stddev_ms", 0.0),
            min_ms=data.get("min_ms", 0.0),
            max_ms=data.get("max_ms", 0.0),
            p90_ms=data.get("p90_ms", 0.0),
            p99_ms=data.get("p99_ms", 0.0),
        )


@dataclass
class TypeBreakdown:
    """Breakdown of metrics by model type (NLP, LP, QCP)."""

    attempted: int
    success: int
    success_rate: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TypeBreakdown:
        """Create TypeBreakdown from a dictionary."""
        return cls(
            attempted=data.get("attempted", 0),
            success=data.get("success", 0),
            success_rate=data.get("success_rate", 0.0),
        )


@dataclass
class StageMetrics:
    """Metrics for a single pipeline stage (parse, translate, solve)."""

    attempted: int
    success: int
    failure: int
    success_rate: float
    cascade_skip: int = 0
    timing: TimingStats | None = None
    by_type: dict[str, TypeBreakdown] = field(default_factory=dict)
    error_breakdown: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StageMetrics:
        """Create StageMetrics from a dictionary."""
        timing = None
        if "timing" in data:
            timing = TimingStats.from_dict(data["timing"])

        by_type = {}
        if "by_type" in data:
            for type_name, type_data in data["by_type"].items():
                by_type[type_name] = TypeBreakdown.from_dict(type_data)

        return cls(
            attempted=data.get("attempted", 0),
            success=data.get("success", 0),
            failure=data.get("failure", 0),
            success_rate=data.get("success_rate", 0.0),
            cascade_skip=data.get("cascade_skip", 0),
            timing=timing,
            by_type=by_type,
            error_breakdown=data.get("error_breakdown", {}),
        )


@dataclass
class ComparisonMetrics:
    """Metrics for solution comparison stage."""

    attempted: int
    match: int
    mismatch: int
    skipped: int
    cascade_skip: int
    match_rate: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ComparisonMetrics:
        """Create ComparisonMetrics from a dictionary."""
        return cls(
            attempted=data.get("attempted", 0),
            match=data.get("match", 0),
            mismatch=data.get("mismatch", 0),
            skipped=data.get("skipped", 0),
            cascade_skip=data.get("cascade_skip", 0),
            match_rate=data.get("match_rate", 0.0),
        )


@dataclass
class FullPipelineMetrics:
    """Metrics for full pipeline success."""

    success: int
    total: int
    success_rate: float
    successful_models: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FullPipelineMetrics:
        """Create FullPipelineMetrics from a dictionary."""
        return cls(
            success=data.get("success", 0),
            total=data.get("total", 0),
            success_rate=data.get("success_rate", 0.0),
            successful_models=data.get("successful_models", []),
        )


@dataclass
class Environment:
    """Environment information for the baseline."""

    nlp2mcp_version: str
    python_version: str
    gams_version: str
    path_solver_version: str
    platform: str
    platform_version: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Environment:
        """Create Environment from a dictionary."""
        return cls(
            nlp2mcp_version=data.get("nlp2mcp_version", "unknown"),
            python_version=data.get("python_version", "unknown"),
            gams_version=data.get("gams_version", "unknown"),
            path_solver_version=data.get("path_solver_version", "unknown"),
            platform=data.get("platform", "unknown"),
            platform_version=data.get("platform_version", "unknown"),
        )


@dataclass
class BaselineMetrics:
    """Complete baseline metrics from baseline_metrics.json."""

    schema_version: str
    baseline_date: str
    sprint: str
    environment: Environment
    total_models: int
    model_types: dict[str, int]
    parse: StageMetrics
    translate: StageMetrics
    solve: StageMetrics
    comparison: ComparisonMetrics
    full_pipeline: FullPipelineMetrics
    notes: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaselineMetrics:
        """Create BaselineMetrics from a dictionary."""
        return cls(
            schema_version=data.get("schema_version", "unknown"),
            baseline_date=data.get("baseline_date", "unknown"),
            sprint=data.get("sprint", "unknown"),
            environment=Environment.from_dict(data.get("environment", {})),
            total_models=data.get("total_models", 0),
            model_types=data.get("model_types", {}),
            parse=StageMetrics.from_dict(data.get("parse", {})),
            translate=StageMetrics.from_dict(data.get("translate", {})),
            solve=StageMetrics.from_dict(data.get("solve", {})),
            comparison=ComparisonMetrics.from_dict(data.get("comparison", {})),
            full_pipeline=FullPipelineMetrics.from_dict(data.get("full_pipeline", {})),
            notes=data.get("notes", []),
        )


def load_baseline_metrics(path: Path | str) -> BaselineMetrics:
    """
    Load baseline metrics from a JSON file.

    Args:
        path: Path to the baseline_metrics.json file

    Returns:
        BaselineMetrics object with all metrics

    Raises:
        DataLoadError: If the file doesn't exist, is invalid JSON,
            or is missing required fields
    """
    path = Path(path)

    if not path.exists():
        raise DataLoadError(f"Baseline metrics file not found: {path}")

    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise DataLoadError(f"Invalid JSON in baseline metrics file: {e}") from e

    # Validate required fields
    required_fields = [
        "schema_version",
        "baseline_date",
        "parse",
        "translate",
        "solve",
    ]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise DataLoadError(f"Missing required fields in baseline metrics: {missing_fields}")

    return BaselineMetrics.from_dict(data)


def load_gamslib_status(path: Path | str) -> dict[str, Any]:
    """
    Load GAMSLIB status database with per-model results.

    Args:
        path: Path to the gamslib_status.json file

    Returns:
        Dictionary with models data

    Raises:
        DataLoadError: If the file doesn't exist or is invalid JSON
    """
    path = Path(path)

    if not path.exists():
        raise DataLoadError(f"GAMSLIB status file not found: {path}")

    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise DataLoadError(f"Invalid JSON in GAMSLIB status file: {e}") from e

    # Validate basic structure
    if "models" not in data:
        raise DataLoadError("Missing 'models' field in GAMSLIB status file")

    return data

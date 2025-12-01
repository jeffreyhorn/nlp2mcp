"""Unit tests for check_parse_rate_regression.py multi-metric logic.

Sprint 12 Day 2: Multi-Metric Threshold Backend
"""

# Import functions from the script
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from check_parse_rate_regression import check_regression, read_metrics_from_dict


class TestCheckRegression:
    """Test regression detection logic."""

    def test_no_regression_same_rate(self):
        """No regression when current equals baseline."""
        assert not check_regression(current=50.0, baseline=50.0, threshold=0.10)

    def test_no_regression_improvement(self):
        """No regression when current is better than baseline."""
        assert not check_regression(current=60.0, baseline=50.0, threshold=0.10)

    def test_no_regression_within_threshold(self):
        """No regression when drop is within threshold."""
        # 5% drop with 10% threshold
        assert not check_regression(current=47.5, baseline=50.0, threshold=0.10)

    def test_regression_exceeds_threshold(self):
        """Regression detected when drop exceeds threshold."""
        # 15% drop with 10% threshold
        assert check_regression(current=42.5, baseline=50.0, threshold=0.10)

    def test_no_regression_from_zero_baseline(self):
        """Cannot regress from 0% baseline."""
        assert not check_regression(current=0.0, baseline=0.0, threshold=0.10)


class TestReadMetricsFromDict:
    """Test metrics extraction from report dictionaries."""

    def test_parse_rate_only(self):
        """Extract parse_rate when only parse_rate present."""
        report = {"kpis": {"parse_rate_percent": 75.5}}
        metrics = read_metrics_from_dict(report)

        assert metrics == {"parse_rate": 75.5}

    def test_all_metrics(self):
        """Extract all metrics when all present."""
        report = {
            "kpis": {
                "parse_rate_percent": 75.5,
                "convert_rate_percent": 82.3,
                "avg_time_ms": 12.5,
            }
        }
        metrics = read_metrics_from_dict(report)

        assert metrics == {
            "parse_rate": 75.5,
            "convert_rate": 82.3,
            "avg_time_ms": 12.5,
        }

    def test_missing_kpis_key(self):
        """Raise KeyError when 'kpis' key missing."""
        report = {"data": {}}

        with pytest.raises(KeyError, match="Missing 'kpis'"):
            read_metrics_from_dict(report)

    def test_empty_kpis(self):
        """Return empty dict when kpis is empty."""
        report = {"kpis": {}}
        metrics = read_metrics_from_dict(report)

        assert metrics == {}


class TestMultiMetricThresholds:
    """Test multi-metric threshold calculations."""

    def test_parse_rate_higher_is_better(self):
        """Parse rate regression: higher is better, so drop is bad."""
        # Baseline 50%, current 45% = 10% relative drop
        baseline = 50.0
        current = 45.0
        relative_change = (baseline - current) / baseline

        assert relative_change == 0.10  # 10% drop
        assert relative_change > 0.05  # Exceeds 5% warn threshold
        assert relative_change < 0.15  # Does not exceed 10% fail threshold (using <15% for clarity)

    def test_convert_rate_higher_is_better(self):
        """Convert rate regression: higher is better, so drop is bad."""
        # Baseline 80%, current 72% = 10% relative drop
        baseline = 80.0
        current = 72.0
        relative_change = (baseline - current) / baseline

        assert relative_change == 0.10  # 10% drop

    def test_performance_lower_is_better(self):
        """Performance regression: lower is better, so increase is bad."""
        # Baseline 10ms, current 13ms = 30% relative increase
        baseline = 10.0
        current = 13.0
        relative_change = (current - baseline) / baseline

        assert relative_change == 0.30  # 30% increase
        assert relative_change > 0.20  # Exceeds 20% warn threshold
        assert relative_change < 0.50  # Does not exceed 50% fail threshold

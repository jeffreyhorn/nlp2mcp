"""Unit tests for test_solve.py MCP solve functionality."""

from __future__ import annotations

import argparse

# Add project root to path
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gamslib.error_taxonomy import PATH_SYNTAX_ERROR  # noqa: E402
from scripts.gamslib.test_solve import (  # noqa: E402
    apply_filters,
    categorize_solve_outcome,
    extract_objective_from_variables,
    extract_path_version,
    get_translated_models,
    parse_gams_listing,
    solve_mcp,
    update_model_solve_result,
)


class TestParseGamsListing:
    """Tests for parse_gams_listing function."""

    def test_parse_successful_solve(self):
        """Test parsing a successful MCP solve."""
        lst_content = """
S O L V E      S U M M A R Y

     MODEL   mcp_model
     TYPE    MCP
     SOLVER  PATH                FROM LINE  105

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal

 RESOURCE USAGE, LIMIT          0.155 10000000000.000
 ITERATION COUNT, LIMIT        27    2147483647
"""
        result = parse_gams_listing(lst_content)

        assert result["solver_status"] == 1
        assert result["model_status"] == 1
        assert result["iterations"] == 27
        assert result["resource_usage"] == 0.155
        assert result["has_solve_summary"] is True
        assert result["error_type"] is None

    def test_parse_infeasible_solve(self):
        """Test parsing an infeasible MCP solve."""
        lst_content = """
S O L V E      S U M M A R Y

     MODEL   mcp_model
     TYPE    MCP
     SOLVER  PATH                FROM LINE  105

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      4 Infeasible

 RESOURCE USAGE, LIMIT          0.100 10000000000.000
 ITERATION COUNT, LIMIT        10    2147483647
"""
        result = parse_gams_listing(lst_content)

        assert result["solver_status"] == 1
        assert result["model_status"] == 4
        assert result["has_solve_summary"] is True

    def test_parse_compilation_error(self):
        """Test parsing a compilation error."""
        lst_content = """
**** $409 Unrecognizable item - skipped
**** 1 ERROR(S)   0 WARNING(S)
"""
        result = parse_gams_listing(lst_content)

        assert result["error_type"] == "compilation_error"
        assert result["solver_status"] is None
        assert result["model_status"] is None

    def test_parse_license_limit(self):
        """Test parsing a license limit error."""
        lst_content = """
S O L V E      S U M M A R Y

The model exceeds the demo license limits.
"""
        result = parse_gams_listing(lst_content)

        assert result["error_type"] == "license_limit"

    def test_parse_with_objective_value(self):
        """Test parsing with explicit objective value."""
        lst_content = """
S O L V E      S U M M A R Y

     MODEL   nlp_model
     TYPE    NLP
     SOLVER  CONOPT              FROM LINE  50

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal
**** OBJECTIVE VALUE             -26272.5145

 RESOURCE USAGE, LIMIT          0.200 10000000000.000
 ITERATION COUNT, LIMIT        50    2147483647
"""
        result = parse_gams_listing(lst_content)

        assert result["solver_status"] == 1
        assert result["model_status"] == 1
        assert result["objective_value"] == pytest.approx(-26272.5145)

    def test_parse_no_solve_summary(self):
        """Test parsing file without solve summary."""
        lst_content = """
GAMS 51.3.0 38407a9b DEX-DEG x86 64bit/macOS

$title Test Model

* Just declarations, no solve
"""
        result = parse_gams_listing(lst_content)

        assert result["error_type"] == "no_solve_summary"
        assert result["has_solve_summary"] is False


class TestExtractObjectiveFromVariables:
    """Tests for extract_objective_from_variables function."""

    def test_extract_scalar_obj(self):
        """Test extracting objective from scalar obj variable."""
        lst_content = """
---- VAR obj               -INF       -26272.5145        +INF             .
"""
        result = extract_objective_from_variables(lst_content)
        assert result == pytest.approx(-26272.5145)

    def test_extract_z_variable(self):
        """Test extracting objective from z variable."""
        lst_content = """
---- VAR z                 -INF           123.456        +INF             .
"""
        result = extract_objective_from_variables(lst_content)
        assert result == pytest.approx(123.456)

    def test_extract_zero_objective(self):
        """Test extracting zero objective (shown as .)."""
        lst_content = """
---- VAR obj               -INF             .            +INF             .
"""
        result = extract_objective_from_variables(lst_content)
        assert result == 0.0

    def test_no_objective_found(self):
        """Test when no objective variable found."""
        lst_content = """
---- VAR x                   0.0            1.0          10.0             .
"""
        result = extract_objective_from_variables(lst_content)
        assert result is None


class TestExtractPathVersion:
    """Tests for extract_path_version function."""

    def test_extract_version_standard_format(self):
        """Test extracting PATH version from standard .lst format."""
        lst_content = """
PATH Version: 5.2.01 (Mon Oct 27 13:31:58 2025)
Authors: Todd Munson, Steven Dirkse, Youngdae Kim, and Michael Ferris
"""
        result = extract_path_version(lst_content)
        assert result == "5.2.01"

    def test_extract_version_two_part(self):
        """Test extracting PATH version with two-part version number."""
        lst_content = """
PATH Version: 5.2 (Some date)
"""
        result = extract_path_version(lst_content)
        assert result == "5.2"

    def test_no_version_found(self):
        """Test when no PATH version found in .lst file."""
        lst_content = """
S O L V E      S U M M A R Y

**** SOLVER STATUS     1 Normal Completion
"""
        result = extract_path_version(lst_content)
        assert result is None

    def test_version_with_extra_whitespace(self):
        """Test extracting version with extra whitespace."""
        lst_content = """
PATH  Version:   5.2.01   (date info)
"""
        result = extract_path_version(lst_content)
        assert result == "5.2.01"


class TestCategorizeSolveOutcome:
    """Tests for categorize_solve_outcome function."""

    def test_optimal_solve(self):
        """Test categorization of optimal solve."""
        result = categorize_solve_outcome(1, 1, None)
        assert result == "model_optimal"

    def test_locally_optimal_solve(self):
        """Test categorization of locally optimal solve."""
        result = categorize_solve_outcome(1, 2, None)
        assert result == "model_locally_optimal"

    def test_infeasible_solve(self):
        """Test categorization of infeasible solve."""
        result = categorize_solve_outcome(1, 4, None)
        assert result == "model_infeasible"

    def test_unbounded_solve(self):
        """Test categorization of unbounded solve."""
        result = categorize_solve_outcome(1, 3, None)
        assert result == "model_unbounded"

    def test_iteration_limit(self):
        """Test categorization of iteration limit."""
        result = categorize_solve_outcome(2, 6, None)
        assert result == "path_solve_iteration_limit"

    def test_time_limit(self):
        """Test categorization of time limit."""
        result = categorize_solve_outcome(3, 6, None)
        assert result == "path_solve_time_limit"

    def test_evaluation_error(self):
        """Test categorization of evaluation error."""
        result = categorize_solve_outcome(5, None, None)
        assert result == "path_solve_eval_error"

    def test_license_error(self):
        """Test categorization of license error."""
        result = categorize_solve_outcome(7, None, None)
        assert result == "path_solve_license"

    def test_compilation_error(self):
        """Test categorization of compilation error."""
        result = categorize_solve_outcome(None, None, "compilation_error")
        assert result == PATH_SYNTAX_ERROR

    def test_license_limit_error_type(self):
        """Test categorization of license limit from error type."""
        result = categorize_solve_outcome(None, None, "license_limit")
        assert result == "path_solve_license"

    def test_terminated_solver(self):
        """Test categorization of terminated solver."""
        result = categorize_solve_outcome(4, None, None)
        assert result == "path_solve_terminated"


class TestGetTranslatedModels:
    """Tests for get_translated_models function."""

    def test_get_translated_models(self):
        """Test getting translated models."""
        db = {
            "models": [
                {"model_id": "a", "nlp2mcp_translate": {"status": "success"}},
                {"model_id": "b", "nlp2mcp_translate": {"status": "failure"}},
                {"model_id": "c", "nlp2mcp_translate": {"status": "success"}},
                {"model_id": "d"},  # No translate result
            ]
        }
        result = get_translated_models(db)
        assert len(result) == 2
        assert result[0]["model_id"] == "a"
        assert result[1]["model_id"] == "c"

    def test_get_no_translated_models(self):
        """Test when no models translated."""
        db = {
            "models": [
                {"model_id": "a", "nlp2mcp_translate": {"status": "failure"}},
                {"model_id": "b"},
            ]
        }
        result = get_translated_models(db)
        assert len(result) == 0

    def test_get_empty_database(self):
        """Test with empty database."""
        db = {"models": []}
        result = get_translated_models(db)
        assert len(result) == 0


class TestApplyFilters:
    """Tests for apply_filters function."""

    def _make_args(
        self,
        model: str | None = None,
        model_type: str | None = None,
        translate_success: bool = False,
        limit: int | None = None,
    ) -> argparse.Namespace:
        """Create args namespace for testing."""
        return argparse.Namespace(
            model=model,
            model_type=model_type,
            translate_success=translate_success,
            limit=limit,
        )

    def test_no_filters_returns_all(self):
        """Test that no filters returns all models."""
        models = [
            {"model_id": "a"},
            {"model_id": "b"},
            {"model_id": "c"},
        ]
        args = self._make_args()
        result = apply_filters(models, args)
        assert len(result) == 3

    def test_model_filter(self):
        """Test filtering by specific model."""
        models = [
            {"model_id": "a"},
            {"model_id": "b"},
            {"model_id": "c"},
        ]
        args = self._make_args(model="b")
        result = apply_filters(models, args)
        assert len(result) == 1
        assert result[0]["model_id"] == "b"

    def test_model_type_filter(self):
        """Test filtering by model type."""
        models = [
            {"model_id": "a", "type": "NLP"},
            {"model_id": "b", "type": "LP"},
            {"model_id": "c", "type": "NLP"},
        ]
        args = self._make_args(model_type="NLP")
        result = apply_filters(models, args)
        assert len(result) == 2
        assert all(m["type"] == "NLP" for m in result)

    def test_translate_success_filter(self):
        """Test filtering by translate success."""
        models = [
            {"model_id": "a", "nlp2mcp_translate": {"status": "success"}},
            {"model_id": "b", "nlp2mcp_translate": {"status": "failure"}},
            {"model_id": "c", "nlp2mcp_translate": {"status": "success"}},
        ]
        args = self._make_args(translate_success=True)
        result = apply_filters(models, args)
        assert len(result) == 2

    def test_limit_filter(self):
        """Test limit filter."""
        models = [{"model_id": f"m{i}"} for i in range(10)]
        args = self._make_args(limit=3)
        result = apply_filters(models, args)
        assert len(result) == 3


class TestUpdateModelSolveResult:
    """Tests for update_model_solve_result function."""

    def test_update_successful_solve(self):
        """Test updating model with successful solve result."""
        model: dict[str, Any] = {"model_id": "test"}
        solve_result = {
            "status": "success",
            "solver_version": "5.2.01",
            "solver_status": 1,
            "solver_status_text": "Normal Completion",
            "model_status": 1,
            "model_status_text": "Optimal",
            "objective_value": 123.456,
            "solve_time_seconds": 0.5,
            "iterations": 27,
            "outcome_category": "model_optimal",
        }

        update_model_solve_result(model, solve_result)

        assert "mcp_solve" in model
        assert model["mcp_solve"]["status"] == "success"
        assert model["mcp_solve"]["solver_version"] == "5.2.01"
        assert model["mcp_solve"]["solver_status"] == 1
        assert model["mcp_solve"]["model_status"] == 1
        assert model["mcp_solve"]["objective_value"] == 123.456
        assert model["mcp_solve"]["solver"] == "PATH"
        assert "error" not in model["mcp_solve"]

    def test_update_failed_solve(self):
        """Test updating model with failed solve result."""
        model: dict[str, Any] = {"model_id": "test"}
        solve_result = {
            "status": "failure",
            "solver_status": 3,
            "solver_status_text": "Resource Interrupt",
            "model_status": None,
            "model_status_text": None,
            "objective_value": None,
            "solve_time_seconds": 60.0,
            "iterations": None,
            "outcome_category": "path_solve_time_limit",
            "error": "Timeout after 60 seconds",
        }

        update_model_solve_result(model, solve_result)

        assert model["mcp_solve"]["status"] == "failure"
        assert model["mcp_solve"]["error"] == {
            "category": "path_solve_time_limit",
            "message": "Timeout after 60 seconds",
        }


class TestSolveMcp:
    """Tests for solve_mcp function."""

    @patch("scripts.gamslib.test_solve.Path.exists")
    @patch("shutil.which")
    def test_gams_not_found(self, mock_which, mock_exists):
        """Test when GAMS executable not found."""
        mock_which.return_value = None
        mock_exists.return_value = False  # No fallback GAMS paths exist

        result = solve_mcp(Path("/nonexistent/model.gms"))

        assert result["status"] == "failure"
        assert "GAMS executable not found" in result["error"]
        assert result["outcome_category"] == "path_solve_terminated"

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_successful_solve(self, mock_which, mock_run):
        """Test successful solve with mocked subprocess."""
        mock_which.return_value = "/usr/bin/gams"

        # Create a mock .lst file content
        lst_content = """
S O L V E      S U M M A R Y

     MODEL   mcp_model
     TYPE    MCP
     SOLVER  PATH                FROM LINE  105

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal

 RESOURCE USAGE, LIMIT          0.155 10000000000.000
 ITERATION COUNT, LIMIT        27    2147483647
"""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        # Mock the temp directory and file reading
        with patch("tempfile.TemporaryDirectory") as mock_tmpdir:
            mock_tmpdir.return_value.__enter__.return_value = "/tmp/test"
            with patch.object(Path, "exists", return_value=True):
                with patch.object(Path, "read_text", return_value=lst_content):
                    result = solve_mcp(Path("/test/model.gms"))

        assert result["status"] == "success"
        assert result["solver_status"] == 1
        assert result["model_status"] == 1
        assert result["outcome_category"] == "model_optimal"

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_solve_timeout(self, mock_which, mock_run):
        """Test solve timeout handling."""
        import subprocess

        mock_which.return_value = "/usr/bin/gams"
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="gams", timeout=60)

        result = solve_mcp(Path("/test/model.gms"), timeout=60)

        assert result["status"] == "failure"
        assert result["solver_status"] == 3
        assert result["outcome_category"] == "path_solve_time_limit"
        assert "Timeout" in result["error"]

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_no_lst_file_generated(self, mock_which, mock_run):
        """Test when no .lst file is generated."""
        mock_which.return_value = "/usr/bin/gams"
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")

        with patch("tempfile.TemporaryDirectory") as mock_tmpdir:
            mock_tmpdir.return_value.__enter__.return_value = "/tmp/test"
            with patch.object(Path, "exists", return_value=False):
                result = solve_mcp(Path("/test/model.gms"))

        assert result["status"] == "failure"
        assert "No .lst file generated" in result["error"]

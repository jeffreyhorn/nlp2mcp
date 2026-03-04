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
    COMPARE_BOTH_INFEASIBLE,
    COMPARE_MCP_FAILED,
    COMPARE_NLP_FAILED,
    COMPARE_NOT_PERFORMED,
    COMPARE_OBJECTIVE_MATCH,
    COMPARE_OBJECTIVE_MISMATCH,
    COMPARE_STATUS_MISMATCH,
    DEFAULT_ATOL,
    DEFAULT_RTOL,
    apply_filters,
    categorize_solve_outcome,
    compare_solutions,
    compare_variable_values,
    extract_equation_marginals,
    extract_objective_from_variables,
    extract_path_version,
    extract_variable_values,
    get_translated_models,
    objectives_match,
    parse_gams_listing,
    solve_mcp,
    update_model_solve_result,
    values_close,
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

    def test_extract_profit_variable(self):
        """Test extracting objective from profit variable."""
        lst_content = """
---- VAR profit            -INF        18666.667        +INF             .
"""
        result = extract_objective_from_variables(lst_content)
        assert result == pytest.approx(18666.667)

    def test_extract_cost_variable(self):
        """Test extracting objective from cost variable."""
        lst_content = """
---- VAR cost              -INF          500.123        +INF             .
"""
        result = extract_objective_from_variables(lst_content)
        assert result == pytest.approx(500.123)

    def test_no_objective_found(self):
        """Test when no objective variable found."""
        lst_content = """
---- VAR x                   0.0            1.0          10.0             .
"""
        result = extract_objective_from_variables(lst_content)
        assert result is None

    def test_sentinel_nlp2mcp_obj_val(self):
        """Test that the nlp2mcp sentinel scalar is preferred over heuristic names."""
        lst_content = """
----    185 PARAMETER nlp2mcp_obj_val          =     4500.000
"""
        result = extract_objective_from_variables(lst_content)
        assert result == pytest.approx(4500.0)

    def test_sentinel_takes_priority_over_heuristic(self):
        """Sentinel match wins even when a heuristic name is also present."""
        lst_content = """
---- VAR obj               -INF         100.000        +INF             .
----    185 PARAMETER nlp2mcp_obj_val          =     4500.000
"""
        result = extract_objective_from_variables(lst_content)
        assert result == pytest.approx(4500.0)

    def test_sentinel_last_occurrence_used(self):
        """With multiple solve runs in one .lst, the last sentinel value is used."""
        lst_content = """
----    100 PARAMETER nlp2mcp_obj_val          =     1000.000
----    200 PARAMETER nlp2mcp_obj_val          =     4500.000
"""
        result = extract_objective_from_variables(lst_content)
        assert result == pytest.approx(4500.0)


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


class TestObjectivesMatch:
    """Tests for objectives_match tolerance comparison function."""

    def test_exact_match(self):
        """Test exact match returns True."""
        match, reason = objectives_match(100.0, 100.0)
        assert match is True
        assert "Match" in reason

    def test_within_relative_tolerance(self):
        """Test values within relative tolerance match."""
        # For large values, rtol=1e-6 allows diff of ~1 for obj=1e6
        # 1000000.0 vs 1000000.5 -> diff=0.5, tol = 1e-8 + 1e-6 * 1e6 = 1.00001
        match, reason = objectives_match(1000000.0, 1000000.5)
        assert match is True

    def test_outside_relative_tolerance(self):
        """Test values outside relative tolerance don't match."""
        # 1000.0 vs 1010.0 -> diff=10.0, tol = 1e-8 + 2e-3 * 1010 = 2.02
        match, reason = objectives_match(1000.0, 1010.0)
        assert match is False
        assert "Mismatch" in reason

    def test_zero_objective_within_atol(self):
        """Test zero objective with value within atol matches."""
        # 0 vs 1e-9 -> diff=1e-9, tol = 1e-8 + 1e-6 * 1e-9 ≈ 1e-8
        match, reason = objectives_match(0.0, 1e-9)
        assert match is True

    def test_zero_objective_outside_atol(self):
        """Test zero objective with value outside atol doesn't match."""
        # 0 vs 1e-7 -> diff=1e-7, tol = 1e-8 + 1e-6 * 1e-7 ≈ 1e-8
        match, reason = objectives_match(0.0, 1e-7)
        assert match is False

    def test_negative_objectives_match(self):
        """Test negative objectives that match within tolerance."""
        # -1000.0 vs -1000.0005 -> diff=0.0005, tol = 1e-8 + 1e-6 * 1000.0005 ≈ 0.001
        match, reason = objectives_match(-1000.0, -1000.0005)
        assert match is True

    def test_negative_objectives_mismatch(self):
        """Test negative objectives that don't match."""
        # -1000.0 vs -1010.0 -> diff=10.0, tol = 1e-8 + 2e-3 * 1010 = 2.02
        match, reason = objectives_match(-1000.0, -1010.0)
        assert match is False

    def test_nan_handling(self):
        """Test NaN values return False with appropriate message."""
        match, reason = objectives_match(float("nan"), 100.0)
        assert match is False
        assert "NaN" in reason

        match, reason = objectives_match(100.0, float("nan"))
        assert match is False
        assert "NaN" in reason

    def test_infinity_handling(self):
        """Test Infinity values return False."""
        match, reason = objectives_match(float("inf"), 100.0)
        assert match is False
        assert "Infinity" in reason

        match, reason = objectives_match(100.0, float("-inf"))
        assert match is False

    def test_both_positive_infinity_match(self):
        """Test both positive infinity values match."""
        match, reason = objectives_match(float("inf"), float("inf"))
        assert match is True
        assert "infinite" in reason.lower()

    def test_both_negative_infinity_match(self):
        """Test both negative infinity values match."""
        match, reason = objectives_match(float("-inf"), float("-inf"))
        assert match is True

    def test_opposite_infinity_mismatch(self):
        """Test opposite infinity values don't match."""
        match, reason = objectives_match(float("inf"), float("-inf"))
        assert match is False

    def test_custom_tolerances(self):
        """Test with custom tolerance values."""
        # With rtol=1e-3, 1000.0 vs 1001.0 should match (diff=1, tol=1.001)
        match, reason = objectives_match(1000.0, 1001.0, rtol=1e-3, atol=1e-8)
        assert match is True

        # With very tight tolerance, should not match
        match, reason = objectives_match(100.0, 100.001, rtol=1e-10, atol=1e-10)
        assert match is False

    def test_very_small_values(self):
        """Test comparison of very small non-zero values."""
        # Both near zero - should match if within atol
        match, reason = objectives_match(1e-10, -1e-10)
        assert match is True  # diff=2e-10 < atol=1e-8

    def test_default_tolerance_values(self):
        """Test that default tolerance values are as expected."""
        assert DEFAULT_RTOL == 2e-3
        assert DEFAULT_ATOL == 1e-8


class TestCompareSolutions:
    """Tests for compare_solutions decision tree function."""

    def _make_model(
        self,
        nlp_solver_status: int | None = 1,
        nlp_model_status: int | None = 1,
        nlp_objective: float | None = 100.0,
        nlp_convexity_status: str = "verified_convex",
        mcp_solver_status: int | None = 1,
        mcp_model_status: int | None = 1,
        mcp_objective: float | None = 100.0,
        mcp_solve_status: str = "success",
    ) -> dict[str, Any]:
        """Create a model dict for testing."""
        model: dict[str, Any] = {"model_id": "test"}

        if nlp_convexity_status:
            model["convexity"] = {
                "status": nlp_convexity_status,
                "solver_status": nlp_solver_status,
                "model_status": nlp_model_status,
                "objective_value": nlp_objective,
            }

        if mcp_solve_status:
            model["mcp_solve"] = {
                "status": mcp_solve_status,
                "solver_status": mcp_solver_status,
                "model_status": mcp_model_status,
                "objective_value": mcp_objective,
            }

        return model

    def test_objective_match(self):
        """Test Case 1: Both optimal, objectives match."""
        model = self._make_model(
            nlp_objective=225.1946,
            mcp_objective=225.1946,
        )
        result = compare_solutions(model)

        assert result["comparison_status"] == "match"
        assert result["comparison_result"] == COMPARE_OBJECTIVE_MATCH
        assert result["objective_match"] is True
        assert result["status_match"] is True
        assert result["nlp_objective"] == 225.1946
        assert result["mcp_objective"] == 225.1946
        assert result["absolute_difference"] == 0.0

    def test_objective_mismatch(self):
        """Test Case 2: Both optimal, objectives differ."""
        model = self._make_model(
            nlp_objective=100.0,
            mcp_objective=200.0,  # Large difference
        )
        result = compare_solutions(model)

        assert result["comparison_status"] == "mismatch"
        assert result["comparison_result"] == COMPARE_OBJECTIVE_MISMATCH
        assert result["objective_match"] is False
        assert result["status_match"] is True
        assert result["absolute_difference"] == 100.0

    def test_both_infeasible(self):
        """Test Case 3: Both NLP and MCP are infeasible."""
        model = self._make_model(
            nlp_model_status=4,  # Infeasible
            nlp_objective=None,
            mcp_model_status=4,  # Infeasible
            mcp_objective=None,
        )
        result = compare_solutions(model)

        assert result["comparison_status"] == "match"
        assert result["comparison_result"] == COMPARE_BOTH_INFEASIBLE
        assert result["status_match"] is True

    def test_status_mismatch_nlp_optimal(self):
        """Test Case 4: NLP optimal but MCP not optimal."""
        model = self._make_model(
            nlp_solver_status=1,
            nlp_model_status=1,  # Optimal
            nlp_objective=100.0,
            mcp_solver_status=1,
            mcp_model_status=4,  # Infeasible
            mcp_objective=None,
        )
        result = compare_solutions(model)

        assert result["comparison_status"] == "mismatch"
        assert result["comparison_result"] == COMPARE_STATUS_MISMATCH
        assert result["status_match"] is False
        assert "NLP optimal" in result["notes"]

    def test_status_mismatch_mcp_optimal(self):
        """Test Case 5: MCP optimal but NLP not optimal."""
        model = self._make_model(
            nlp_solver_status=1,
            nlp_model_status=4,  # Infeasible
            nlp_objective=None,
            mcp_solver_status=1,
            mcp_model_status=1,  # Optimal
            mcp_objective=100.0,
        )
        result = compare_solutions(model)

        assert result["comparison_status"] == "mismatch"
        assert result["comparison_result"] == COMPARE_STATUS_MISMATCH
        assert result["status_match"] is False
        assert "MCP optimal" in result["notes"]

    def test_nlp_solve_failed_no_convexity(self):
        """Test Case 6: NLP solve failed (no convexity data)."""
        model: dict[str, Any] = {
            "model_id": "test",
            "mcp_solve": {
                "status": "success",
                "solver_status": 1,
                "model_status": 1,
                "objective_value": 100.0,
            },
        }
        result = compare_solutions(model)

        assert result["comparison_status"] == "skipped"
        assert result["comparison_result"] == COMPARE_NLP_FAILED

    def test_nlp_solve_failed_error_status(self):
        """Test Case 6: NLP convexity status is error."""
        model = self._make_model(nlp_convexity_status="error")
        result = compare_solutions(model)

        assert result["comparison_status"] == "skipped"
        assert result["comparison_result"] == COMPARE_NLP_FAILED

    def test_mcp_solve_failed(self):
        """Test Case 7: MCP solve failed."""
        model = self._make_model(mcp_solve_status="failure")
        result = compare_solutions(model)

        assert result["comparison_status"] == "skipped"
        assert result["comparison_result"] == COMPARE_MCP_FAILED

    def test_mcp_solve_missing(self):
        """Test when mcp_solve is missing."""
        model: dict[str, Any] = {
            "model_id": "test",
            "convexity": {
                "status": "verified_convex",
                "solver_status": 1,
                "model_status": 1,
                "objective_value": 100.0,
            },
        }
        result = compare_solutions(model)

        assert result["comparison_status"] == "skipped"
        assert result["comparison_result"] == COMPARE_MCP_FAILED

    def test_nlp_objective_missing(self):
        """Test when NLP objective is None but solve succeeded."""
        model = self._make_model(nlp_objective=None)
        result = compare_solutions(model)

        assert result["comparison_status"] == "error"
        assert result["comparison_result"] == COMPARE_NOT_PERFORMED
        assert "NLP objective value not available" in result["notes"]

    def test_mcp_objective_missing(self):
        """Test when MCP objective is None but solve succeeded."""
        model = self._make_model(mcp_objective=None)
        result = compare_solutions(model)

        assert result["comparison_status"] == "error"
        assert result["comparison_result"] == COMPARE_NOT_PERFORMED
        assert "MCP objective value not available" in result["notes"]

    def test_custom_tolerances(self):
        """Test comparison with custom tolerances."""
        model = self._make_model(
            nlp_objective=1000.0,
            mcp_objective=1001.0,
        )

        # With tight default tolerance, should mismatch
        result_tight = compare_solutions(model, rtol=1e-6, atol=1e-8)
        assert result_tight["comparison_result"] == COMPARE_OBJECTIVE_MISMATCH

        # With looser tolerance, should match
        result_loose = compare_solutions(model, rtol=1e-2, atol=1e-8)
        assert result_loose["comparison_result"] == COMPARE_OBJECTIVE_MATCH

    def test_tolerance_values_stored(self):
        """Test that tolerance values are stored in result."""
        model = self._make_model()
        result = compare_solutions(model, rtol=1e-5, atol=1e-7)

        assert result["tolerance_relative"] == 1e-5
        assert result["tolerance_absolute"] == 1e-7

    def test_comparison_date_set(self):
        """Test that comparison_date is set."""
        model = self._make_model()
        result = compare_solutions(model)

        assert result["comparison_date"] is not None
        assert "T" in result["comparison_date"]  # ISO format

    def test_locally_optimal_treated_as_optimal(self):
        """Test that locally optimal (status 2) is treated as optimal."""
        model = self._make_model(
            nlp_model_status=2,  # Locally optimal
            mcp_model_status=2,  # Locally optimal
        )
        result = compare_solutions(model)

        assert result["comparison_status"] == "match"
        assert result["comparison_result"] == COMPARE_OBJECTIVE_MATCH
        assert result["status_match"] is True

    def test_relative_difference_calculated(self):
        """Test that relative difference is calculated correctly."""
        model = self._make_model(
            nlp_objective=1000.0,
            mcp_objective=1010.0,
        )
        result = compare_solutions(model)

        assert result["absolute_difference"] == 10.0
        # relative = 10 / max(1000, 1010, 1e-10) = 10/1010 ≈ 0.0099
        assert result["relative_difference"] == pytest.approx(10.0 / 1010.0)


class TestValuesClose:
    """Tests for values_close combined tolerance function."""

    def test_exact_match(self):
        """Identical values are close."""
        assert values_close(1.0, 1.0) is True

    def test_within_tolerance(self):
        """Values within combined tolerance are close."""
        # diff=0.001, tol = 1e-8 + 2e-3 * 100 = 0.2
        assert values_close(100.0, 100.001) is True

    def test_outside_tolerance(self):
        """Values outside combined tolerance are not close."""
        # diff=10, tol = 1e-8 + 2e-3 * 110 = 0.22
        assert values_close(100.0, 110.0) is False

    def test_nan_not_close(self):
        """NaN is never close to anything."""
        assert values_close(float("nan"), 1.0) is False
        assert values_close(1.0, float("nan")) is False

    def test_inf_same_sign_close(self):
        """Matching infinities are close."""
        assert values_close(float("inf"), float("inf")) is True
        assert values_close(float("-inf"), float("-inf")) is True

    def test_inf_opposite_not_close(self):
        """Opposite infinities are not close."""
        assert values_close(float("inf"), float("-inf")) is False

    def test_zero_within_atol(self):
        """Zero vs small value within atol."""
        assert values_close(0.0, 1e-9) is True

    def test_zero_outside_atol(self):
        """Zero vs value outside atol."""
        assert values_close(0.0, 1e-7) is False


class TestExtractVariableValues:
    """Tests for extract_variable_values .lst parser."""

    def test_scalar_variables(self):
        """Parse scalar variables from .lst content."""
        lst = """
---- VAR a                 -INF            5.6833        +INF             .
---- VAR b                 -INF            4.3702        +INF             .
---- VAR r                 -INF            4.0707        +INF             .
"""
        result = extract_variable_values(lst)
        assert result["a"] == {"": pytest.approx(5.6833)}
        assert result["b"] == {"": pytest.approx(4.3702)}
        assert result["r"] == {"": pytest.approx(4.0707)}

    def test_indexed_variable(self):
        """Parse indexed variable with multiple indices."""
        lst = """
---- VAR lam_e

           LOWER          LEVEL          UPPER         MARGINAL

p1           .              .            +INF           15.0895
p2           .            3.500          +INF           -0.0007
p3           .            2.100          +INF            6.4263
"""
        result = extract_variable_values(lst)
        assert "lam_e" in result
        assert result["lam_e"]["p1"] == pytest.approx(0.0)
        assert result["lam_e"]["p2"] == pytest.approx(3.5)
        assert result["lam_e"]["p3"] == pytest.approx(2.1)

    def test_mixed_scalar_and_indexed(self):
        """Parse file with both scalar and indexed variables."""
        lst = """
---- VAR obj               -INF         100.000        +INF             .

---- VAR x

           LOWER          LEVEL          UPPER         MARGINAL

i1           .            1.000          +INF             .
i2           .            2.000          +INF             .
"""
        result = extract_variable_values(lst)
        assert result["obj"] == {"": pytest.approx(100.0)}
        assert result["x"]["i1"] == pytest.approx(1.0)
        assert result["x"]["i2"] == pytest.approx(2.0)

    def test_dot_value_is_zero(self):
        """GAMS '.' represents zero."""
        lst = """
---- VAR z                 -INF             .            +INF             .
"""
        result = extract_variable_values(lst)
        assert result["z"] == {"": 0.0}

    def test_eps_value_is_zero(self):
        """GAMS 'EPS' represents machine epsilon, treated as zero."""
        lst = """
---- VAR w                 -INF           EPS            +INF             .
"""
        result = extract_variable_values(lst)
        assert result["w"] == {"": 0.0}

    def test_undf_value_skipped(self):
        """GAMS 'UNDF' (undefined) is skipped — variable not included."""
        lst = """
---- VAR u                 -INF          UNDF            +INF             .
"""
        result = extract_variable_values(lst)
        assert "u" not in result

    def test_indexed_eps_value(self):
        """EPS in indexed variable data row is treated as zero."""
        lst = """
---- VAR y

           LOWER          LEVEL          UPPER         MARGINAL

i1           .            EPS            +INF             .
i2           .            5.000          +INF             .
"""
        result = extract_variable_values(lst)
        assert result["y"]["i1"] == 0.0
        assert result["y"]["i2"] == pytest.approx(5.0)

    def test_empty_lst(self):
        """Empty .lst returns empty dict."""
        assert extract_variable_values("") == {}


class TestExtractEquationMarginals:
    """Tests for extract_equation_marginals .lst parser."""

    def test_scalar_equations(self):
        """Parse scalar equation marginals."""
        lst = """
---- EQU stat_a              .              .              .             5.6833
---- EQU stat_b              .              .              .             4.3702
"""
        result = extract_equation_marginals(lst)
        assert result["stat_a"] == {"": pytest.approx(5.6833)}
        assert result["stat_b"] == {"": pytest.approx(4.3702)}

    def test_indexed_equation(self):
        """Parse indexed equation marginals."""
        lst = """
---- EQU comp_e

           LOWER          LEVEL          UPPER         MARGINAL

p1           .            15.0895        +INF             .
p2           .            -0.0007        +INF           1.234
p3           .             6.4263        +INF             .
"""
        result = extract_equation_marginals(lst)
        assert "comp_e" in result
        assert result["comp_e"]["p1"] == pytest.approx(0.0)
        assert result["comp_e"]["p2"] == pytest.approx(1.234)
        assert result["comp_e"]["p3"] == pytest.approx(0.0)

    def test_eps_marginal(self):
        """EPS in equation marginal is treated as zero."""
        lst = """
---- EQU eq_a              .              .              .           EPS
"""
        result = extract_equation_marginals(lst)
        assert result["eq_a"] == {"": 0.0}

    def test_undf_marginal_skipped(self):
        """UNDF in equation marginal skips the equation."""
        lst = """
---- EQU eq_b              .              .              .          UNDF
"""
        result = extract_equation_marginals(lst)
        assert "eq_b" not in result


class TestCompareVariableValues:
    """Tests for compare_variable_values comparison function."""

    def test_matching_variables(self):
        """Variables that match within tolerance."""
        nlp = {"x": {"": 100.0}, "y": {"i1": 1.0, "i2": 2.0}}
        mcp = {"x": {"": 100.0}, "y": {"i1": 1.0, "i2": 2.0}}
        result = compare_variable_values(nlp, mcp)

        assert result["variables_compared"] == 2
        assert result["variables_matched"] == 2
        assert result["variables_diverged"] == 0
        assert result["max_abs_diff"] == 0.0

    def test_diverged_variable(self):
        """Variable that diverges beyond tolerance."""
        nlp = {"x": {"": 100.0}, "y": {"": 200.0}}
        mcp = {"x": {"": 100.0}, "y": {"": 300.0}}
        result = compare_variable_values(nlp, mcp)

        assert result["variables_compared"] == 2
        assert result["variables_matched"] == 1
        assert result["variables_diverged"] == 1
        assert result["max_abs_diff"] == pytest.approx(100.0)
        assert result["worst_variable"] == "y"

    def test_partial_overlap(self):
        """Only common variables and indices are compared."""
        nlp = {"x": {"": 1.0}, "unique_nlp": {"": 5.0}}
        mcp = {"x": {"": 1.0}, "unique_mcp": {"": 5.0}}
        result = compare_variable_values(nlp, mcp)

        assert result["variables_compared"] == 1  # only x in common
        assert result["variables_matched"] == 1

    def test_per_variable_sorted_by_diff(self):
        """Per-variable list is sorted by max abs diff descending."""
        nlp = {"a": {"": 100.0}, "b": {"": 100.0}, "c": {"": 100.0}}
        mcp = {"a": {"": 100.0}, "b": {"": 200.0}, "c": {"": 150.0}}
        result = compare_variable_values(nlp, mcp)

        assert result["per_variable"][0]["name"] == "b"  # diff=100
        assert result["per_variable"][1]["name"] == "c"  # diff=50

    def test_infinity_mismatch(self):
        """Infinity mismatch sets worst_variable and increments diverged."""
        nlp = {"x": {"": float("inf")}}
        mcp = {"x": {"": 1.0}}
        result = compare_variable_values(nlp, mcp)

        assert result["variables_compared"] == 1
        assert result["variables_diverged"] == 1
        assert result["worst_variable"] == "x"

    def test_empty_inputs(self):
        """Empty inputs produce zero-count result."""
        result = compare_variable_values({}, {})
        assert result["variables_compared"] == 0
        assert result["variables_matched"] == 0

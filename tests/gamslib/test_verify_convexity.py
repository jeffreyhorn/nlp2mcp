"""Tests for GAMSLIB convexity verification script."""

import sys
from pathlib import Path

# Add project root to path so we can import from scripts/
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gamslib.verify_convexity import (
    MODEL_STATUS_DESCRIPTIONS,
    SOLVER_STATUS_DESCRIPTIONS,
    ConvexityStatus,
    VerificationResult,
    classify_result,
    parse_gams_listing,
)


class TestStatusDescriptions:
    """Tests for status description dictionaries."""

    def test_model_status_descriptions_complete(self) -> None:
        """Test that all model status codes 1-19 are documented."""
        for status in range(1, 20):
            assert status in MODEL_STATUS_DESCRIPTIONS
            assert len(MODEL_STATUS_DESCRIPTIONS[status]) > 0

    def test_solver_status_descriptions_complete(self) -> None:
        """Test that all solver status codes 1-13 are documented."""
        for status in range(1, 14):
            assert status in SOLVER_STATUS_DESCRIPTIONS
            assert len(SOLVER_STATUS_DESCRIPTIONS[status]) > 0

    def test_key_model_statuses(self) -> None:
        """Test key model status descriptions are correct."""
        assert MODEL_STATUS_DESCRIPTIONS[1] == "Optimal"
        assert MODEL_STATUS_DESCRIPTIONS[2] == "Locally Optimal"
        assert MODEL_STATUS_DESCRIPTIONS[3] == "Unbounded"
        assert MODEL_STATUS_DESCRIPTIONS[4] == "Infeasible"

    def test_key_solver_statuses(self) -> None:
        """Test key solver status descriptions are correct."""
        assert SOLVER_STATUS_DESCRIPTIONS[1] == "Normal Completion"
        assert SOLVER_STATUS_DESCRIPTIONS[7] == "Licensing Problem"


class TestParseGamsListing:
    """Tests for parse_gams_listing function."""

    def test_parse_successful_solve(self) -> None:
        """Test parsing a successful solve output."""
        lst_content = """
GAMS Output

               S O L V E      S U M M A R Y

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal
**** OBJECTIVE VALUE             153.675000

"""
        result = parse_gams_listing(lst_content)
        assert result["has_solve_summary"] is True
        assert result["solver_status"] == 1
        assert result["model_status"] == 1
        assert result["objective_value"] == 153.675
        assert result["error_type"] is None

    def test_parse_no_solve_summary(self) -> None:
        """Test parsing output without solve summary."""
        lst_content = """
GAMS Output
Some model compilation output
"""
        result = parse_gams_listing(lst_content)
        assert result["has_solve_summary"] is False
        assert result["solver_status"] is None
        assert result["model_status"] is None

    def test_parse_compilation_error(self) -> None:
        """Test detecting compilation errors."""
        lst_content = """
GAMS Output
**** $141
**** Syntax error in set definition
"""
        result = parse_gams_listing(lst_content)
        assert result["error_type"] == "compilation_error"
        assert result["has_solve_summary"] is False

    def test_parse_missing_file(self) -> None:
        """Test detecting missing include files."""
        lst_content = """
GAMS Output
*** Error: File 'data.inc' could not be opened
"""
        result = parse_gams_listing(lst_content)
        assert result["error_type"] == "missing_file"
        assert result["has_solve_summary"] is False

    def test_parse_execution_error(self) -> None:
        """Test detecting execution errors."""
        lst_content = """
GAMS Output
*** Execution error: Division by zero
"""
        result = parse_gams_listing(lst_content)
        assert result["error_type"] == "execution_error"
        assert result["has_solve_summary"] is False

    def test_parse_no_solve_statement(self) -> None:
        """Test detecting models without solve statement."""
        lst_content = """
GAMS Output
Model compiled successfully
Parameter definitions only
"""
        result = parse_gams_listing(lst_content)
        assert result["error_type"] == "no_solve_statement"
        assert result["has_solve_summary"] is False

    def test_parse_with_solve_keyword_but_no_summary(self) -> None:
        """Test model that has solve but didn't produce summary."""
        lst_content = """
GAMS Output
solve model using lp;
*** Error occurred before solve
"""
        result = parse_gams_listing(lst_content)
        # Has solve keyword, so not "no_solve_statement"
        assert result["error_type"] == "execution_error"

    def test_parse_multiple_solves_uses_last(self) -> None:
        """Test that multiple solves use the last result."""
        lst_content = """
               S O L V E      S U M M A R Y

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal
**** OBJECTIVE VALUE             100.0

               S O L V E      S U M M A R Y

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      2 Locally Optimal
**** OBJECTIVE VALUE             200.0

"""
        result = parse_gams_listing(lst_content)
        assert result["model_status"] == 2
        assert result["objective_value"] == 200.0

    def test_parse_scientific_notation(self) -> None:
        """Test parsing objective value in scientific notation."""
        lst_content = """
               S O L V E      S U M M A R Y

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal
**** OBJECTIVE VALUE             1.234e+05

"""
        result = parse_gams_listing(lst_content)
        assert result["objective_value"] == 123400.0

    def test_parse_negative_objective(self) -> None:
        """Test parsing negative objective value."""
        lst_content = """
               S O L V E      S U M M A R Y

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal
**** OBJECTIVE VALUE             -42.5

"""
        result = parse_gams_listing(lst_content)
        assert result["objective_value"] == -42.5


class TestClassifyResult:
    """Tests for classify_result function."""

    def test_lp_optimal_is_verified_convex(self) -> None:
        """Test that LP with optimal status is verified convex."""
        result = classify_result(
            model_id="trnsport",
            model_path="/path/to/trnsport.gms",
            model_type="LP",
            solver_status=1,
            model_status=1,
            objective_value=153.675,
            solve_time=0.5,
        )
        assert result.convexity_status == ConvexityStatus.VERIFIED_CONVEX.value
        assert result.error_message is None

    def test_nlp_optimal_is_likely_convex(self) -> None:
        """Test that NLP with optimal status is likely convex."""
        result = classify_result(
            model_id="circle",
            model_path="/path/to/circle.gms",
            model_type="NLP",
            solver_status=1,
            model_status=1,
            objective_value=10.0,
            solve_time=0.3,
        )
        assert result.convexity_status == ConvexityStatus.LIKELY_CONVEX.value

    def test_nlp_locally_optimal_is_likely_convex(self) -> None:
        """Test that NLP with locally optimal status is likely convex."""
        result = classify_result(
            model_id="nlp_model",
            model_path="/path/to/model.gms",
            model_type="NLP",
            solver_status=1,
            model_status=2,  # Locally Optimal
            objective_value=10.0,
            solve_time=0.3,
        )
        assert result.convexity_status == ConvexityStatus.LIKELY_CONVEX.value

    def test_qcp_optimal_is_likely_convex(self) -> None:
        """Test that QCP with optimal status is likely convex."""
        result = classify_result(
            model_id="qcp_model",
            model_path="/path/to/model.gms",
            model_type="QCP",
            solver_status=1,
            model_status=1,
            objective_value=10.0,
            solve_time=0.3,
        )
        assert result.convexity_status == ConvexityStatus.LIKELY_CONVEX.value

    def test_infeasible_is_excluded(self) -> None:
        """Test that infeasible model is excluded."""
        result = classify_result(
            model_id="infeas",
            model_path="/path/to/infeas.gms",
            model_type="LP",
            solver_status=1,
            model_status=4,  # Infeasible
            objective_value=None,
            solve_time=0.1,
        )
        assert result.convexity_status == ConvexityStatus.EXCLUDED.value
        assert "Infeasible" in result.error_message

    def test_unbounded_is_excluded(self) -> None:
        """Test that unbounded model is excluded."""
        result = classify_result(
            model_id="unbnd",
            model_path="/path/to/unbnd.gms",
            model_type="LP",
            solver_status=1,
            model_status=3,  # Unbounded
            objective_value=None,
            solve_time=0.1,
        )
        assert result.convexity_status == ConvexityStatus.EXCLUDED.value
        assert "Unbounded" in result.error_message

    def test_solver_failure_is_error(self) -> None:
        """Test that solver failure is classified as error."""
        result = classify_result(
            model_id="fail",
            model_path="/path/to/fail.gms",
            model_type="LP",
            solver_status=7,  # Licensing Problem
            model_status=None,
            objective_value=None,
            solve_time=0.1,
        )
        assert result.convexity_status == ConvexityStatus.ERROR.value
        assert "Licensing Problem" in result.error_message

    def test_solver_none_is_error(self) -> None:
        """Test that None solver status is classified as error."""
        result = classify_result(
            model_id="fail",
            model_path="/path/to/fail.gms",
            model_type="LP",
            solver_status=None,
            model_status=None,
            objective_value=None,
            solve_time=0.1,
        )
        assert result.convexity_status == ConvexityStatus.ERROR.value

    def test_model_status_none_is_error(self) -> None:
        """Test that None model status with good solver is error."""
        result = classify_result(
            model_id="fail",
            model_path="/path/to/fail.gms",
            model_type="LP",
            solver_status=1,
            model_status=None,
            objective_value=None,
            solve_time=0.1,
        )
        assert result.convexity_status == ConvexityStatus.ERROR.value
        assert "No model status" in result.error_message

    def test_licensing_error_status(self) -> None:
        """Test that licensing error model status is classified as error."""
        result = classify_result(
            model_id="big_model",
            model_path="/path/to/big_model.gms",
            model_type="LP",
            solver_status=1,
            model_status=11,  # Licensing Problem
            objective_value=None,
            solve_time=0.1,
        )
        assert result.convexity_status == ConvexityStatus.ERROR.value
        assert "Licensing Problem" in result.error_message

    def test_error_includes_descriptive_message(self) -> None:
        """Test that error messages include descriptive status text."""
        result = classify_result(
            model_id="fail",
            model_path="/path/to/fail.gms",
            model_type="LP",
            solver_status=3,  # Resource Interrupt
            model_status=None,
            objective_value=None,
            solve_time=60.0,
        )
        assert result.convexity_status == ConvexityStatus.ERROR.value
        assert "Resource Interrupt" in result.error_message


class TestVerificationResult:
    """Tests for VerificationResult dataclass."""

    def test_to_dict(self) -> None:
        """Test serializing VerificationResult to dictionary."""
        result = VerificationResult(
            model_id="trnsport",
            model_path="/path/to/trnsport.gms",
            convexity_status=ConvexityStatus.VERIFIED_CONVEX.value,
            solver_status=1,
            model_status=1,
            objective_value=153.675,
            solve_time_seconds=0.5,
            timed_out=False,
            error_message=None,
        )
        d = result.to_dict()
        assert d["model_id"] == "trnsport"
        assert d["convexity_status"] == "verified_convex"
        assert d["objective_value"] == 153.675
        assert d["timed_out"] is False

    def test_error_result_to_dict(self) -> None:
        """Test serializing error result to dictionary."""
        result = VerificationResult(
            model_id="fail",
            model_path="/path/to/fail.gms",
            convexity_status=ConvexityStatus.ERROR.value,
            solver_status=None,
            model_status=None,
            objective_value=None,
            solve_time_seconds=60.0,
            timed_out=True,
            error_message="Timeout after 60 seconds",
        )
        d = result.to_dict()
        assert d["convexity_status"] == "error"
        assert d["timed_out"] is True
        assert d["error_message"] == "Timeout after 60 seconds"

"""Tests for GAMSLIB batch translate script."""

import argparse
import io
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path so we can import from scripts/
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gamslib.batch_translate import (  # noqa: E402
    get_parsed_models,
    print_summary,
    run_batch_translate,
    translate_single_model,
)
from scripts.gamslib.error_taxonomy import categorize_translate_error  # noqa: E402


class TestCategorizeTranslateError:
    """Tests for categorize_translate_error function (Sprint 15 taxonomy)."""

    def test_timeout_error(self) -> None:
        """Test timeout is categorized correctly."""
        error = "Translation timeout after 60 seconds"
        category = categorize_translate_error(error)
        assert category == "timeout"

    def test_diff_unsupported_func(self) -> None:
        """Test differentiation not implemented is categorized correctly."""
        error = "Differentiation not yet implemented for function 'gamma'"
        category = categorize_translate_error(error)
        assert category == "diff_unsupported_func"

    def test_unsup_index_offset(self) -> None:
        """Test 'IndexOffset not yet supported' is categorized correctly."""
        error = "IndexOffset not yet supported in this context"
        category = categorize_translate_error(error)
        assert category == "unsup_index_offset"

    def test_model_no_objective_def(self) -> None:
        """Test objective not defined by equation is categorized correctly."""
        error = "Objective variable 'z' is not defined by any equation"
        category = categorize_translate_error(error)
        assert category == "model_no_objective_def"

    def test_model_domain_mismatch(self) -> None:
        """Test incompatible domains is categorized correctly."""
        error = "Incompatible domains for variable indexing"
        category = categorize_translate_error(error)
        assert category == "model_domain_mismatch"

    def test_internal_error_unknown(self) -> None:
        """Test unknown error falls back to internal_error."""
        error = "Some unknown translation error"
        category = categorize_translate_error(error)
        assert category == "internal_error"

    def test_diff_chain_rule_error(self) -> None:
        """Test chain rule errors are categorized correctly."""
        error = "Error applying chain rule in derivative"
        category = categorize_translate_error(error)
        assert category == "diff_chain_rule_error"

    def test_model_missing_bounds(self) -> None:
        """Test model missing bounds errors are categorized correctly."""
        error = "Variable has missing bounds specification"
        category = categorize_translate_error(error)
        assert category == "model_missing_bounds"

    def test_unsupported_dollar_cond(self) -> None:
        """Test unsupported dollar conditional errors are categorized correctly."""
        error = "DollarConditional expressions not supported"
        category = categorize_translate_error(error)
        assert category == "unsup_dollar_cond"

    def test_case_insensitive_matching(self) -> None:
        """Test error categorization is case-insensitive."""
        error = "TIMEOUT exceeded"
        category = categorize_translate_error(error)
        assert category == "timeout"


class TestGetParsedModels:
    """Tests for get_parsed_models function."""

    def test_get_successfully_parsed_models(self) -> None:
        """Test getting models with parse status success."""
        database = {
            "models": [
                {"model_id": "model1", "nlp2mcp_parse": {"status": "success"}},
                {"model_id": "model2", "nlp2mcp_parse": {"status": "failure"}},
                {"model_id": "model3", "nlp2mcp_parse": {"status": "success"}},
            ]
        }
        parsed = get_parsed_models(database)
        assert len(parsed) == 2
        assert parsed[0]["model_id"] == "model1"
        assert parsed[1]["model_id"] == "model3"

    def test_get_no_parsed_models(self) -> None:
        """Test when no models have been successfully parsed."""
        database = {
            "models": [
                {"model_id": "model1", "nlp2mcp_parse": {"status": "failure"}},
                {"model_id": "model2"},  # No parse status
            ]
        }
        parsed = get_parsed_models(database)
        assert len(parsed) == 0

    def test_get_empty_database(self) -> None:
        """Test with empty database."""
        database = {"models": []}
        parsed = get_parsed_models(database)
        assert len(parsed) == 0

    def test_get_missing_parse_field(self) -> None:
        """Test models without nlp2mcp_parse field are excluded."""
        database = {
            "models": [
                {"model_id": "model1"},
                {"model_id": "model2", "nlp2mcp_parse": {"status": "success"}},
            ]
        }
        parsed = get_parsed_models(database)
        assert len(parsed) == 1
        assert parsed[0]["model_id"] == "model2"


class TestTranslateSingleModel:
    """Tests for translate_single_model function."""

    def test_successful_translation(self, tmp_path: Path) -> None:
        """Test successful model translation."""
        model_file = tmp_path / "test_model.gms"
        model_file.write_text("* Test model")
        output_file = tmp_path / "output" / "test_model_mcp.gms"

        mock_proc = MagicMock()
        mock_proc.communicate.return_value = ("", "")
        mock_proc.returncode = 0

        with patch("scripts.gamslib.batch_translate.subprocess.Popen", return_value=mock_proc):
            with patch("scripts.gamslib.batch_translate.PROJECT_ROOT", tmp_path):
                result = translate_single_model(model_file, output_file)

        assert result["status"] == "success"
        assert "translate_time_seconds" in result
        assert result["translate_time_seconds"] >= 0

    def test_translation_failure(self, tmp_path: Path) -> None:
        """Test translation failure with differentiation error."""
        model_file = tmp_path / "bad_model.gms"
        model_file.write_text("* Bad model")
        output_file = tmp_path / "output" / "bad_model_mcp.gms"

        mock_proc = MagicMock()
        mock_proc.communicate.return_value = (
            "",
            "Error: Differentiation not yet implemented for function 'gamma'",
        )
        mock_proc.returncode = 1

        with patch("scripts.gamslib.batch_translate.subprocess.Popen", return_value=mock_proc):
            result = translate_single_model(model_file, output_file)

        assert result["status"] == "failure"
        assert result["error"]["category"] == "diff_unsupported_func"
        assert "Differentiation" in result["error"]["message"]

    def test_translation_timeout(self, tmp_path: Path) -> None:
        """Test translation timeout handling."""
        model_file = tmp_path / "slow_model.gms"
        model_file.write_text("* Slow model")
        output_file = tmp_path / "output" / "slow_model_mcp.gms"

        mock_proc = MagicMock()
        mock_proc.communicate.side_effect = [
            subprocess.TimeoutExpired(cmd="test", timeout=60),
            ("", ""),  # Second call after kill
        ]
        mock_proc.kill = MagicMock()

        with patch("scripts.gamslib.batch_translate.subprocess.Popen", return_value=mock_proc):
            result = translate_single_model(model_file, output_file)

        assert result["status"] == "failure"
        assert result["error"]["category"] == "timeout"
        mock_proc.kill.assert_called_once()

    def test_translation_creates_output_directory(self, tmp_path: Path) -> None:
        """Test that output directory is created if it doesn't exist."""
        model_file = tmp_path / "test_model.gms"
        model_file.write_text("* Test model")
        output_file = tmp_path / "nested" / "output" / "test_model_mcp.gms"

        mock_proc = MagicMock()
        mock_proc.communicate.return_value = ("", "")
        mock_proc.returncode = 0

        with patch("scripts.gamslib.batch_translate.subprocess.Popen", return_value=mock_proc):
            translate_single_model(model_file, output_file)

        assert output_file.parent.exists()


class TestRunBatchTranslate:
    """Tests for run_batch_translate function."""

    def _make_args(
        self,
        dry_run: bool = False,
        limit: int | None = None,
        model: str | None = None,
        verbose: bool = False,
        save_every: int = 5,
    ) -> argparse.Namespace:
        """Create argparse.Namespace with default values."""
        return argparse.Namespace(
            dry_run=dry_run,
            limit=limit,
            model=model,
            verbose=verbose,
            save_every=save_every,
        )

    def test_dry_run_does_not_translate(self, tmp_path: Path) -> None:
        """Test dry run mode doesn't actually translate."""
        database = {
            "models": [
                {"model_id": "model1", "nlp2mcp_parse": {"status": "success"}},
            ]
        }
        model_file = tmp_path / "model1.gms"
        model_file.write_text("* Test model")

        with patch("scripts.gamslib.batch_translate.load_database", return_value=database):
            with patch("scripts.gamslib.batch_translate.save_database") as mock_save:
                with patch("scripts.gamslib.batch_translate.RAW_MODELS_DIR", tmp_path):
                    with patch("scripts.gamslib.batch_translate.subprocess.Popen") as mock_popen:
                        args = self._make_args(dry_run=True)
                        stats = run_batch_translate(args)

        mock_save.assert_not_called()
        mock_popen.assert_not_called()
        assert stats["processed"] == 1

    def test_limit_restricts_models_processed(self, tmp_path: Path) -> None:
        """Test limit argument restricts number of models processed."""
        database = {
            "models": [
                {"model_id": f"model{i}", "nlp2mcp_parse": {"status": "success"}} for i in range(10)
            ]
        }

        with patch("scripts.gamslib.batch_translate.load_database", return_value=database):
            with patch("scripts.gamslib.batch_translate.save_database"):
                with patch("scripts.gamslib.batch_translate.create_backup", return_value=None):
                    with patch("scripts.gamslib.batch_translate.RAW_MODELS_DIR", tmp_path):
                        args = self._make_args(dry_run=True, limit=3)
                        stats = run_batch_translate(args)

        assert stats["total"] == 3

    def test_single_model_filter(self, tmp_path: Path) -> None:
        """Test processing a single specific model."""
        database = {
            "models": [
                {"model_id": "model1", "nlp2mcp_parse": {"status": "success"}},
                {"model_id": "target_model", "nlp2mcp_parse": {"status": "success"}},
                {"model_id": "model3", "nlp2mcp_parse": {"status": "success"}},
            ]
        }
        model_file = tmp_path / "target_model.gms"
        model_file.write_text("* Target model")

        with patch("scripts.gamslib.batch_translate.load_database", return_value=database):
            with patch("scripts.gamslib.batch_translate.save_database"):
                with patch("scripts.gamslib.batch_translate.create_backup", return_value=None):
                    with patch("scripts.gamslib.batch_translate.RAW_MODELS_DIR", tmp_path):
                        args = self._make_args(dry_run=True, model="target_model")
                        stats = run_batch_translate(args)

        assert stats["total"] == 1

    def test_model_not_found_returns_error(self) -> None:
        """Test error when specified model is not found."""
        database = {
            "models": [
                {"model_id": "model1", "nlp2mcp_parse": {"status": "success"}},
            ]
        }

        with patch("scripts.gamslib.batch_translate.load_database", return_value=database):
            args = self._make_args(model="nonexistent_model")
            stats = run_batch_translate(args)

        assert "error" in stats
        assert "not found" in stats["error"].lower()

    def test_skips_missing_model_files(self, tmp_path: Path) -> None:
        """Test that missing model files are skipped."""
        database = {
            "models": [
                {"model_id": "missing_model", "nlp2mcp_parse": {"status": "success"}},
            ]
        }

        with patch("scripts.gamslib.batch_translate.load_database", return_value=database):
            with patch("scripts.gamslib.batch_translate.save_database"):
                with patch("scripts.gamslib.batch_translate.create_backup", return_value=None):
                    with patch("scripts.gamslib.batch_translate.RAW_MODELS_DIR", tmp_path):
                        args = self._make_args()
                        stats = run_batch_translate(args)

        assert stats["skipped"] == 1
        assert stats["processed"] == 0

    def test_successful_translation_updates_database(self, tmp_path: Path) -> None:
        """Test successful translation updates database with results."""
        database = {
            "models": [
                {"model_id": "good_model", "nlp2mcp_parse": {"status": "success"}},
            ]
        }
        model_file = tmp_path / "good_model.gms"
        model_file.write_text("* Good model")

        mock_proc = MagicMock()
        mock_proc.communicate.return_value = ("", "")
        mock_proc.returncode = 0

        with patch("scripts.gamslib.batch_translate.load_database", return_value=database):
            with patch("scripts.gamslib.batch_translate.save_database"):
                with patch("scripts.gamslib.batch_translate.create_backup", return_value=None):
                    with patch("scripts.gamslib.batch_translate.RAW_MODELS_DIR", tmp_path):
                        with patch(
                            "scripts.gamslib.batch_translate.subprocess.Popen",
                            return_value=mock_proc,
                        ):
                            args = self._make_args()
                            stats = run_batch_translate(args)

        assert stats["success"] == 1
        assert stats["failure"] == 0
        assert "nlp2mcp_translate" in database["models"][0]
        assert database["models"][0]["nlp2mcp_translate"]["status"] == "success"

    def test_failed_translation_updates_database_with_error(self, tmp_path: Path) -> None:
        """Test failed translation updates database with error information."""
        database = {
            "models": [
                {"model_id": "bad_model", "nlp2mcp_parse": {"status": "success"}},
            ]
        }
        model_file = tmp_path / "bad_model.gms"
        model_file.write_text("* Bad model")

        mock_proc = MagicMock()
        mock_proc.communicate.return_value = ("", "Error: unsupported feature")
        mock_proc.returncode = 1

        with patch("scripts.gamslib.batch_translate.load_database", return_value=database):
            with patch("scripts.gamslib.batch_translate.save_database"):
                with patch("scripts.gamslib.batch_translate.create_backup", return_value=None):
                    with patch("scripts.gamslib.batch_translate.RAW_MODELS_DIR", tmp_path):
                        with patch(
                            "scripts.gamslib.batch_translate.subprocess.Popen",
                            return_value=mock_proc,
                        ):
                            args = self._make_args()
                            stats = run_batch_translate(args)

        assert stats["success"] == 0
        assert stats["failure"] == 1
        assert "nlp2mcp_translate" in database["models"][0]
        assert database["models"][0]["nlp2mcp_translate"]["status"] == "failure"


class TestPrintSummary:
    """Tests for print_summary function."""

    def test_prints_basic_stats(self) -> None:
        """Test basic statistics are printed."""
        stats = {
            "total": 10,
            "processed": 8,
            "success": 6,
            "failure": 2,
            "skipped": 2,
            "success_rate": 75.0,
            "total_time": 10.5,
            "successful_models": [],
        }

        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            print_summary(stats)

        output = captured_output.getvalue()
        assert "8/10" in output
        assert "Success: 6" in output
        assert "75.0%" in output
        assert "Failure: 2" in output
        assert "Skipped: 2" in output
        assert "10.5s" in output

    def test_prints_successful_models(self) -> None:
        """Test successful model list is printed."""
        stats = {
            "total": 3,
            "processed": 3,
            "success": 2,
            "failure": 1,
            "skipped": 0,
            "success_rate": 66.7,
            "total_time": 5.0,
            "successful_models": ["model_a", "model_b"],
        }

        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            print_summary(stats)

        output = captured_output.getvalue()
        assert "Successful translations (2)" in output
        assert "model_a" in output
        assert "model_b" in output

    def test_handles_zero_processed(self) -> None:
        """Test handles zero processed models gracefully."""
        stats = {
            "total": 5,
            "processed": 0,
            "success": 0,
            "failure": 0,
            "skipped": 5,
            "success_rate": 0,
            "total_time": 0.1,
            "successful_models": [],
        }

        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            print_summary(stats)

        output = captured_output.getvalue()
        assert "0/5" in output
        assert "Skipped: 5" in output

    def test_prints_average_time_per_model(self) -> None:
        """Test average time per model is printed."""
        stats = {
            "total": 4,
            "processed": 4,
            "success": 4,
            "failure": 0,
            "skipped": 0,
            "success_rate": 100.0,
            "total_time": 8.0,
            "successful_models": ["m1", "m2", "m3", "m4"],
        }

        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            print_summary(stats)

        output = captured_output.getvalue()
        assert "2.00s" in output  # 8.0 / 4 = 2.0

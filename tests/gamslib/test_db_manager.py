"""Unit tests for db_manager.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gamslib.db_manager import (  # noqa: E402
    create_backup,
    list_backups,
    load_database,
    prune_backups,
    save_database,
    validate_database,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_database() -> dict:
    """Create a sample valid database."""
    return {
        "schema_version": "2.0.0",
        "created_date": "2026-01-01T00:00:00Z",
        "updated_date": "2026-01-01T00:00:00Z",
        "total_models": 2,
        "models": [
            {
                "model_id": "trnsport",
                "model_name": "A Transportation Problem",
                "gamslib_type": "LP",
                "convexity": {
                    "status": "verified_convex",
                    "solver_status": 1,
                    "model_status": 1,
                },
            },
            {
                "model_id": "circle",
                "model_name": "Circle Enclosing Points",
                "gamslib_type": "NLP",
                "convexity": {
                    "status": "likely_convex",
                    "solver_status": 1,
                    "model_status": 2,
                },
            },
        ],
    }


@pytest.fixture
def sample_schema() -> dict:
    """Load the actual schema for testing."""
    schema_path = PROJECT_ROOT / "data" / "gamslib" / "schema.json"
    with open(schema_path) as f:
        return json.load(f)


@pytest.fixture
def temp_database(tmp_path: Path, sample_database: dict) -> Path:
    """Create a temporary database file."""
    db_path = tmp_path / "gamslib_status.json"
    with open(db_path, "w") as f:
        json.dump(sample_database, f, indent=2)
    return db_path


@pytest.fixture
def temp_backup_dir(tmp_path: Path) -> Path:
    """Create a temporary backup directory."""
    backup_dir = tmp_path / "archive"
    backup_dir.mkdir()
    return backup_dir


# =============================================================================
# Test load_database
# =============================================================================


class TestLoadDatabase:
    """Tests for load_database function."""

    def test_load_valid_database(self, temp_database: Path) -> None:
        """Test loading a valid database file."""
        data = load_database(temp_database)
        assert data["schema_version"] == "2.0.0"
        assert len(data["models"]) == 2

    def test_load_nonexistent_database(self, tmp_path: Path) -> None:
        """Test loading a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_database(tmp_path / "nonexistent.json")

    def test_load_invalid_json(self, tmp_path: Path) -> None:
        """Test loading invalid JSON raises JSONDecodeError."""
        invalid_path = tmp_path / "invalid.json"
        invalid_path.write_text("not valid json {")
        with pytest.raises(json.JSONDecodeError):
            load_database(invalid_path)


# =============================================================================
# Test save_database
# =============================================================================


class TestSaveDatabase:
    """Tests for save_database function."""

    def test_save_database(self, tmp_path: Path, sample_database: dict) -> None:
        """Test saving a database creates valid JSON file."""
        db_path = tmp_path / "output.json"
        save_database(sample_database, db_path)

        assert db_path.exists()
        with open(db_path) as f:
            loaded = json.load(f)
        assert loaded["schema_version"] == "2.0.0"
        assert len(loaded["models"]) == 2

    def test_save_database_creates_directory(self, tmp_path: Path, sample_database: dict) -> None:
        """Test save creates parent directory if needed."""
        db_path = tmp_path / "subdir" / "output.json"
        save_database(sample_database, db_path)
        assert db_path.exists()

    def test_save_database_atomic_write(self, tmp_path: Path, sample_database: dict) -> None:
        """Test save uses atomic write (no temp file left behind)."""
        db_path = tmp_path / "output.json"
        save_database(sample_database, db_path)

        # Check no temp file left
        temp_path = db_path.with_suffix(".json.tmp")
        assert not temp_path.exists()


# =============================================================================
# Test validate_database
# =============================================================================


class TestValidateDatabase:
    """Tests for validate_database function."""

    def test_valid_database(self, sample_database: dict, sample_schema: dict) -> None:
        errors = validate_database(sample_database, sample_schema)
        assert len(errors) == 0

    def test_invalid_model_type(self, sample_schema: dict) -> None:
        """Test validation fails for invalid model type."""
        invalid_db = {
            "schema_version": "2.0.0",
            "models": [
                {
                    "model_id": "test",
                    "model_name": "Test Model",
                    "gamslib_type": "INVALID",  # Invalid type
                }
            ],
        }
        errors = validate_database(invalid_db, sample_schema)
        assert len(errors) > 0
        assert any("INVALID" in e["message"] for e in errors)

    def test_missing_required_field(self, sample_schema: dict) -> None:
        """Test validation fails for missing required field."""
        invalid_db = {
            "schema_version": "2.0.0",
            "models": [
                {
                    "model_id": "test",
                    # Missing model_name and gamslib_type
                }
            ],
        }
        errors = validate_database(invalid_db, sample_schema)
        assert len(errors) > 0

    def test_invalid_convexity_status(self, sample_schema: dict) -> None:
        """Test validation fails for invalid convexity status."""
        invalid_db = {
            "schema_version": "2.0.0",
            "models": [
                {
                    "model_id": "test",
                    "model_name": "Test Model",
                    "gamslib_type": "LP",
                    "convexity": {
                        "status": "invalid_status",  # Invalid
                    },
                }
            ],
        }
        errors = validate_database(invalid_db, sample_schema)
        assert len(errors) > 0


# =============================================================================
# Test backup functions
# =============================================================================


class TestBackupFunctions:
    """Tests for backup-related functions."""

    def test_create_backup(self, temp_database: Path, tmp_path: Path) -> None:
        """Test creating a backup."""
        backup_dir = tmp_path / "archive"

        with patch("scripts.gamslib.db_manager.BACKUP_DIR", backup_dir):
            backup_path = create_backup(temp_database)

        assert backup_path is not None
        assert backup_path.exists()
        assert "gamslib_status.json" in backup_path.name

    def test_create_backup_nonexistent_source(self, tmp_path: Path) -> None:
        """Test backup returns None for nonexistent source."""
        backup_path = create_backup(tmp_path / "nonexistent.json")
        assert backup_path is None

    def test_list_backups(self, tmp_path: Path) -> None:
        """Test listing backups."""
        backup_dir = tmp_path / "archive"
        backup_dir.mkdir()

        # Create some backup files
        (backup_dir / "20260101_100000_gamslib_status.json").write_text("{}")
        (backup_dir / "20260101_110000_gamslib_status.json").write_text("{}")

        with patch("scripts.gamslib.db_manager.BACKUP_DIR", backup_dir):
            backups = list_backups()

        assert len(backups) == 2

    def test_prune_backups(self, tmp_path: Path) -> None:
        """Test pruning old backups."""
        backup_dir = tmp_path / "archive"
        backup_dir.mkdir()

        # Create 15 backup files
        for i in range(15):
            (backup_dir / f"2026010{i:02d}_100000_gamslib_status.json").write_text("{}")

        with patch("scripts.gamslib.db_manager.BACKUP_DIR", backup_dir):
            pruned = prune_backups(keep_count=10)

        assert pruned == 5
        remaining = list(backup_dir.glob("*_gamslib_status.json"))
        assert len(remaining) == 10


# =============================================================================
# Test CLI commands via subprocess
# =============================================================================


class TestCLICommands:
    """Integration tests for CLI commands."""

    def test_validate_command(self) -> None:
        """Test validate command runs successfully."""
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "gamslib" / "db_manager.py"),
                "validate",
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0
        assert "Validation PASSED" in result.stdout

    def test_list_command(self) -> None:
        """Test list command runs successfully."""
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "gamslib" / "db_manager.py"),
                "list",
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0
        assert "219 models" in result.stdout

    def test_list_command_json_format(self) -> None:
        """Test list command with JSON format."""
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "gamslib" / "db_manager.py"),
                "list",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "total" in data
        assert "models" in data

    def test_list_command_count_format(self) -> None:
        """Test list command with count format."""
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "gamslib" / "db_manager.py"),
                "list",
                "--format",
                "count",
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0
        assert result.stdout.strip() == "219"

    def test_init_requires_force(self) -> None:
        """Test init command requires --force when database exists."""
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "gamslib" / "db_manager.py"),
                "init",
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 1
        assert "Use --force" in result.stderr

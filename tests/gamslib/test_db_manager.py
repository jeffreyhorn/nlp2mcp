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
    _NOT_FOUND,
    create_backup,
    find_model,
    get_nested_value,
    list_backups,
    load_database,
    parse_value,
    prune_backups,
    save_database,
    set_nested_value,
    validate_database,
    validate_model_entry,
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


# Check if jsonschema is available for conditional skipping
try:
    import jsonschema  # noqa: F401

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
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

        # Create 15 backup files with valid consecutive dates (2026-01-01 to 2026-01-15)
        for day in range(1, 16):
            (backup_dir / f"202601{day:02d}_100000_gamslib_status.json").write_text("{}")

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

    @pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
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

    def test_get_command(self) -> None:
        """Test get command returns model details."""
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "gamslib" / "db_manager.py"),
                "get",
                "trnsport",
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0
        assert "trnsport" in result.stdout
        assert "Transportation" in result.stdout

    def test_get_command_json_format(self) -> None:
        """Test get command with JSON format."""
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "gamslib" / "db_manager.py"),
                "get",
                "trnsport",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["model_id"] == "trnsport"
        assert data["gamslib_type"] == "LP"

    def test_get_command_field(self) -> None:
        """Test get command with --field option."""
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "gamslib" / "db_manager.py"),
                "get",
                "trnsport",
                "--field",
                "convexity.status",
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0
        assert "verified_convex" in result.stdout

    def test_get_command_not_found(self) -> None:
        """Test get command with invalid model_id."""
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "gamslib" / "db_manager.py"),
                "get",
                "nonexistent_model",
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 1
        assert "not found" in result.stderr.lower()


# =============================================================================
# Test get/update helper functions
# =============================================================================


class TestFindModel:
    """Tests for find_model function."""

    def test_find_existing_model(self, sample_database: dict) -> None:
        """Test finding an existing model."""
        model = find_model(sample_database, "trnsport")
        assert model is not None
        assert model["model_id"] == "trnsport"

    def test_find_nonexistent_model(self, sample_database: dict) -> None:
        """Test finding a nonexistent model returns None."""
        model = find_model(sample_database, "nonexistent")
        assert model is None


class TestGetNestedValue:
    """Tests for get_nested_value function."""

    def test_get_top_level_field(self, sample_database: dict) -> None:
        """Test getting a top-level field."""
        model = sample_database["models"][0]
        value = get_nested_value(model, "model_id")
        assert value == "trnsport"

    def test_get_nested_field(self, sample_database: dict) -> None:
        """Test getting a nested field with dot notation."""
        model = sample_database["models"][0]
        value = get_nested_value(model, "convexity.status")
        assert value == "verified_convex"

    def test_get_deeply_nested_field(self) -> None:
        """Test getting a deeply nested field."""
        data = {"a": {"b": {"c": "deep_value"}}}
        value = get_nested_value(data, "a.b.c")
        assert value == "deep_value"

    def test_get_nonexistent_field(self, sample_database: dict) -> None:
        """Test getting a nonexistent field returns _NOT_FOUND sentinel."""
        model = sample_database["models"][0]
        value = get_nested_value(model, "nonexistent.field")
        assert value is _NOT_FOUND


class TestSetNestedValue:
    """Tests for set_nested_value function."""

    def test_set_top_level_field(self) -> None:
        """Test setting a top-level field."""
        data: dict = {"existing": "value"}
        set_nested_value(data, "new_field", "new_value")
        assert data["new_field"] == "new_value"

    def test_set_nested_field_existing_path(self) -> None:
        """Test setting a nested field in existing structure."""
        data: dict = {"convexity": {"status": "old_status"}}
        set_nested_value(data, "convexity.status", "new_status")
        assert data["convexity"]["status"] == "new_status"

    def test_set_nested_field_creates_path(self) -> None:
        """Test setting a nested field creates intermediate dicts."""
        data: dict = {}
        set_nested_value(data, "nlp2mcp_parse.status", "success")
        assert data["nlp2mcp_parse"]["status"] == "success"

    def test_set_deeply_nested_field(self) -> None:
        """Test setting a deeply nested field."""
        data: dict = {}
        set_nested_value(data, "a.b.c.d", "deep_value")
        assert data["a"]["b"]["c"]["d"] == "deep_value"


class TestParseValue:
    """Tests for parse_value function."""

    def test_parse_string(self) -> None:
        """Test parsing a regular string."""
        assert parse_value("hello") == "hello"

    def test_parse_integer(self) -> None:
        """Test parsing an integer."""
        assert parse_value("42") == 42

    def test_parse_float(self) -> None:
        """Test parsing a float."""
        assert parse_value("3.14") == 3.14

    def test_parse_boolean_true(self) -> None:
        """Test parsing boolean true."""
        assert parse_value("true") is True

    def test_parse_boolean_false(self) -> None:
        """Test parsing boolean false."""
        assert parse_value("false") is False

    def test_parse_null(self) -> None:
        """Test parsing null."""
        assert parse_value("null") is None

    def test_parse_json_array(self) -> None:
        """Test parsing a JSON array."""
        assert parse_value('["a", "b"]') == ["a", "b"]

    def test_parse_json_object(self) -> None:
        """Test parsing a JSON object."""
        assert parse_value('{"key": "value"}') == {"key": "value"}


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
class TestValidateModelEntry:
    """Tests for validate_model_entry function."""

    def test_valid_model_entry(self, sample_database: dict, sample_schema: dict) -> None:
        """Test validating a valid model entry."""
        model = sample_database["models"][0]
        errors = validate_model_entry(model, sample_schema)
        assert len(errors) == 0

    def test_invalid_convexity_status(self, sample_schema: dict) -> None:
        """Test validation fails for invalid convexity status."""
        invalid_model = {
            "model_id": "test",
            "model_name": "Test Model",
            "gamslib_type": "LP",
            "convexity": {
                "status": "invalid_status",
            },
        }
        errors = validate_model_entry(invalid_model, sample_schema)
        assert len(errors) > 0
        assert any("invalid_status" in e["message"] for e in errors)

    def test_invalid_parse_status(self, sample_schema: dict) -> None:
        """Test validation fails for invalid parse status."""
        invalid_model = {
            "model_id": "test",
            "model_name": "Test Model",
            "gamslib_type": "LP",
            "nlp2mcp_parse": {
                "status": "bad_status",
            },
        }
        errors = validate_model_entry(invalid_model, sample_schema)
        assert len(errors) > 0

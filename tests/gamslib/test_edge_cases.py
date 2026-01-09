"""Additional edge case tests for GAMSLIB database operations."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gamslib.db_manager import (  # noqa: E402
    get_nested_value,
    parse_value,
    set_nested_value,
    validate_database,
)

# =============================================================================
# Edge Cases for get_nested_value
# =============================================================================


class TestGetNestedValueEdgeCases:
    """Edge case tests for get_nested_value."""

    def test_get_from_empty_dict(self) -> None:
        """Test getting value from empty dict."""
        from scripts.gamslib.db_manager import _NOT_FOUND

        result = get_nested_value({}, "field")
        assert result is _NOT_FOUND

    def test_get_with_none_value(self) -> None:
        """Test getting field that has None value."""
        data = {"field": None}
        result = get_nested_value(data, "field")
        assert result is None

    def test_get_with_empty_string_value(self) -> None:
        """Test getting field with empty string."""
        data = {"field": ""}
        result = get_nested_value(data, "field")
        assert result == ""

    def test_get_with_zero_value(self) -> None:
        """Test getting field with zero value."""
        data = {"field": 0}
        result = get_nested_value(data, "field")
        assert result == 0

    def test_get_nested_none_in_path(self) -> None:
        """Test getting nested field when intermediate value is None."""
        from scripts.gamslib.db_manager import _NOT_FOUND

        data = {"a": None}
        result = get_nested_value(data, "a.b")
        assert result is _NOT_FOUND

    def test_get_nested_list_in_path(self) -> None:
        """Test getting nested field when intermediate value is a list."""
        from scripts.gamslib.db_manager import _NOT_FOUND

        data = {"a": [1, 2, 3]}
        result = get_nested_value(data, "a.b")
        assert result is _NOT_FOUND


# =============================================================================
# Edge Cases for set_nested_value
# =============================================================================


class TestSetNestedValueEdgeCases:
    """Edge case tests for set_nested_value."""

    def test_set_overwrites_none(self) -> None:
        """Test setting value overwrites None."""
        data: dict = {"field": None}
        set_nested_value(data, "field", "value")
        assert data["field"] == "value"

    def test_set_overwrites_non_dict_with_dict(self) -> None:
        """Test setting nested value overwrites non-dict intermediate."""
        data: dict = {"a": "not_a_dict"}
        set_nested_value(data, "a.b", "value")
        assert isinstance(data["a"], dict)
        assert data["a"]["b"] == "value"

    def test_set_empty_string_value(self) -> None:
        """Test setting empty string value."""
        data: dict = {}
        set_nested_value(data, "field", "")
        assert data["field"] == ""

    def test_set_zero_value(self) -> None:
        """Test setting zero value."""
        data: dict = {}
        set_nested_value(data, "field", 0)
        assert data["field"] == 0

    def test_set_none_value(self) -> None:
        """Test setting None value."""
        data: dict = {}
        set_nested_value(data, "field", None)
        assert data["field"] is None

    def test_set_list_value(self) -> None:
        """Test setting list value."""
        data: dict = {}
        set_nested_value(data, "field", [1, 2, 3])
        assert data["field"] == [1, 2, 3]

    def test_set_dict_value(self) -> None:
        """Test setting dict value."""
        data: dict = {}
        set_nested_value(data, "field", {"key": "value"})
        assert data["field"] == {"key": "value"}


# =============================================================================
# Edge Cases for parse_value
# =============================================================================


class TestParseValueEdgeCases:
    """Edge case tests for parse_value."""

    def test_parse_empty_string(self) -> None:
        """Test parsing empty string."""
        assert parse_value("") == ""

    def test_parse_whitespace(self) -> None:
        """Test parsing whitespace."""
        assert parse_value("   ") == "   "

    def test_parse_negative_integer(self) -> None:
        """Test parsing negative integer."""
        assert parse_value("-42") == -42

    def test_parse_negative_float(self) -> None:
        """Test parsing negative float."""
        assert parse_value("-3.14") == -3.14

    def test_parse_scientific_notation(self) -> None:
        """Test parsing scientific notation."""
        assert parse_value("1e-6") == 1e-6
        assert parse_value("1.5e10") == 1.5e10

    def test_parse_string_that_looks_like_number(self) -> None:
        """Test parsing string with extra characters."""
        assert parse_value("42x") == "42x"
        assert parse_value("3.14pi") == "3.14pi"

    def test_parse_empty_array(self) -> None:
        """Test parsing empty array."""
        assert parse_value("[]") == []

    def test_parse_empty_object(self) -> None:
        """Test parsing empty object."""
        assert parse_value("{}") == {}

    def test_parse_nested_json(self) -> None:
        """Test parsing nested JSON structures."""
        assert parse_value('{"a": {"b": [1, 2, 3]}}') == {"a": {"b": [1, 2, 3]}}

    def test_parse_true_uppercase(self) -> None:
        """Test parsing True (uppercase) as string."""
        assert parse_value("True") == "True"  # Not JSON, returns as string

    def test_parse_false_uppercase(self) -> None:
        """Test parsing False (uppercase) as string."""
        assert parse_value("False") == "False"  # Not JSON, returns as string

    def test_parse_null_uppercase(self) -> None:
        """Test parsing Null (uppercase) as string."""
        assert parse_value("Null") == "Null"  # Not JSON, returns as string


# =============================================================================
# Edge Cases for Database Validation
# =============================================================================


HAS_JSONSCHEMA = importlib.util.find_spec("jsonschema") is not None


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
class TestValidationEdgeCases:
    """Edge case tests for database validation."""

    @pytest.fixture
    def sample_schema(self) -> dict:
        """Load the actual schema."""
        schema_path = PROJECT_ROOT / "data" / "gamslib" / "schema.json"
        with open(schema_path) as f:
            return json.load(f)

    def test_validate_empty_models_array(self, sample_schema: dict) -> None:
        """Test validation with empty models array."""
        db = {
            "schema_version": "2.0.0",
            "created_date": "2026-01-01T00:00:00Z",
            "updated_date": "2026-01-01T00:00:00Z",
            "total_models": 0,
            "models": [],
        }
        errors = validate_database(db, sample_schema)
        assert len(errors) == 0

    def test_validate_model_with_minimal_fields(self, sample_schema: dict) -> None:
        """Test validation with only required fields."""
        db = {
            "schema_version": "2.0.0",
            "models": [
                {
                    "model_id": "test",
                    "model_name": "Test",
                    "gamslib_type": "LP",
                }
            ],
        }
        errors = validate_database(db, sample_schema)
        assert len(errors) == 0

    def test_validate_model_with_all_optional_fields_empty(self, sample_schema: dict) -> None:
        """Test validation with optional fields as empty strings/arrays."""
        db = {
            "schema_version": "2.0.0",
            "models": [
                {
                    "model_id": "test",
                    "model_name": "Test",
                    "gamslib_type": "LP",
                    "description": "",
                    "keywords": [],
                    "notes": "",
                }
            ],
        }
        errors = validate_database(db, sample_schema)
        assert len(errors) == 0

    def test_validate_negative_parse_time(self, sample_schema: dict) -> None:
        """Test validation rejects negative parse time."""
        db = {
            "schema_version": "2.0.0",
            "models": [
                {
                    "model_id": "test",
                    "model_name": "Test",
                    "gamslib_type": "LP",
                    "nlp2mcp_parse": {
                        "status": "success",
                        "parse_time_seconds": -1.0,  # Invalid
                    },
                }
            ],
        }
        errors = validate_database(db, sample_schema)
        assert len(errors) > 0

    def test_validate_zero_parse_time(self, sample_schema: dict) -> None:
        """Test validation allows zero parse time."""
        db = {
            "schema_version": "2.0.0",
            "models": [
                {
                    "model_id": "test",
                    "model_name": "Test",
                    "gamslib_type": "LP",
                    "nlp2mcp_parse": {
                        "status": "success",
                        "parse_time_seconds": 0.0,
                    },
                }
            ],
        }
        errors = validate_database(db, sample_schema)
        assert len(errors) == 0

    def test_validate_error_category_values(self, sample_schema: dict) -> None:
        """Test validation of error category enum values."""
        # Valid error categories
        valid_categories = [
            "syntax_error",
            "unsupported_feature",
            "missing_include",
            "timeout",
            "validation_error",
            "internal_error",
        ]

        for category in valid_categories:
            db = {
                "schema_version": "2.0.0",
                "models": [
                    {
                        "model_id": "test",
                        "model_name": "Test",
                        "gamslib_type": "LP",
                        "nlp2mcp_parse": {
                            "status": "failure",
                            "parse_date": "2026-01-01T00:00:00Z",
                            "error": {
                                "category": category,
                                "message": "test error",
                            },
                        },
                    }
                ],
            }
            errors = validate_database(db, sample_schema)
            assert len(errors) == 0, f"Category '{category}' should be valid"

        # Invalid error category
        db = {
            "schema_version": "2.0.0",
            "models": [
                {
                    "model_id": "test",
                    "model_name": "Test",
                    "gamslib_type": "LP",
                    "nlp2mcp_parse": {
                        "status": "failure",
                        "parse_date": "2026-01-01T00:00:00Z",
                        "error": {
                            "category": "invalid_category",
                            "message": "test error",
                        },
                    },
                }
            ],
        }
        errors = validate_database(db, sample_schema)
        assert len(errors) > 0


# =============================================================================
# Edge Cases for CLI Limit Parameter
# =============================================================================


class TestCLILimitEdgeCases:
    """Edge case tests for CLI limit parameter."""

    def test_list_with_zero_limit(self) -> None:
        """Test list command with limit=0 (should show all)."""
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "gamslib" / "db_manager.py"),
                "list",
                "--limit",
                "0",
                "--format",
                "count",
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0
        count = int(result.stdout.strip())
        assert count == 219  # All models

    def test_list_with_negative_limit(self) -> None:
        """Test list command with negative limit (should error)."""
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "gamslib" / "db_manager.py"),
                "list",
                "--limit",
                "-1",
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 1
        assert "Invalid limit" in result.stderr

    def test_list_with_limit_exceeding_total(self) -> None:
        """Test list command with limit > total models."""
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "gamslib" / "db_manager.py"),
                "list",
                "--limit",
                "1000",
                "--format",
                "count",
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0
        count = int(result.stdout.strip())
        assert count == 219  # Only 219 models exist

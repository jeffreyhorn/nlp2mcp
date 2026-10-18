"""Schema 3.1.0: ``license_edition`` (both result types) and ``convexity.gams_version``.

Sprint 40 P1 (``SCHEMA_3_1_0_DESIGN.md`` §8, §10, T8). The contract is ADDITIVE
and does not loosen: both result types keep ``additionalProperties: false``, and
the edition enum has no ``"unknown"``, because ``null`` already means unrecorded.

The positive control validates the same row against the 3.0.0 schema as
committed at ``SCHEMA_3_0_0_REF`` (read with ``git show``, never a stash). There
the new fields must FAIL; under 3.1.0 they must PASS. Without that, a test that
only checks "3.1.0 accepts the fields" would also pass if the schema accepted
everything.
"""

from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema", reason="optional; the validator no-ops without it")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = PROJECT_ROOT / "data" / "gamslib" / "schema.json"
#: The last commit whose schema.json is 3.0.0 (Sprint 40 Day 0's base).
SCHEMA_3_0_0_REF = "cd5c6b7e"


def _schema_3_1_0() -> dict:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def _schema_3_0_0() -> dict:
    try:
        text = subprocess.run(
            ["git", "show", f"{SCHEMA_3_0_0_REF}:data/gamslib/schema.json"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip(f"git history for {SCHEMA_3_0_0_REF} is not available (shallow clone?)")
    schema = json.loads(text)
    assert "(v3.0.0)" in schema["description"], "the control must be the 3.0.0 schema"
    return schema


def _model(**mcp_and_convexity: dict) -> dict:
    """A minimal valid model entry carrying the given stage objects."""
    entry = {
        "model_id": "abel",
        "model_name": "Linear Quadratic Control Problem",
        "gamslib_type": "NLP",
    }
    entry.update(mcp_and_convexity)
    return entry


def _errors(schema: dict, model: dict) -> list[str]:
    validator = jsonschema.Draft7Validator(
        {**schema["definitions"]["model_entry"], "definitions": schema["definitions"]}
    )
    return [e.message for e in validator.iter_errors(model)]


MCP = {"status": "success", "license_edition": "licensed"}
CONV = {"status": "verified_convex", "license_edition": "licensed", "gams_version": "54.2.1"}


def test_the_minimal_entry_is_valid_under_both_schemas() -> None:
    """Guard for the controls below: the base row is valid, so any failure is the new field."""
    base = _model(mcp_solve={"status": "success"}, convexity={"status": "verified_convex"})
    assert _errors(_schema_3_0_0(), base) == []
    assert _errors(_schema_3_1_0(), base) == []


def test_positive_control_the_new_fields_FAIL_the_3_0_0_schema() -> None:
    errs = _errors(_schema_3_0_0(), _model(mcp_solve=MCP, convexity=CONV))
    assert any("'license_edition' was unexpected" in e for e in errs), errs
    assert any("gams_version" in e and "unexpected" in e for e in errs), errs


@pytest.mark.parametrize("edition", ["licensed", "demo", None])
def test_both_types_accept_each_edition(edition: str | None) -> None:
    model = _model(
        mcp_solve={"status": "success", "license_edition": edition},
        convexity={"status": "verified_convex", "license_edition": edition, "gams_version": None},
    )
    assert _errors(_schema_3_1_0(), model) == []


@pytest.mark.parametrize("stage", ["mcp_solve", "convexity"])
def test_unknown_is_not_an_edition(stage: str) -> None:
    """``null`` already means unrecorded; a third word would invite guessing."""
    model = _model(mcp_solve=dict(MCP), convexity=dict(CONV))
    model[stage]["license_edition"] = "unknown"
    assert any("is not one of" in e for e in _errors(_schema_3_1_0(), model))


@pytest.mark.parametrize("stage", ["mcp_solve", "convexity"])
def test_an_unknown_key_is_still_rejected(stage: str) -> None:
    """The bump is additive: it must not loosen ``additionalProperties: false``."""
    model = _model(mcp_solve=dict(MCP), convexity=dict(CONV))
    model[stage]["licence_edition"] = "licensed"  # the misspelling is the point
    assert any("'licence_edition' was unexpected" in e for e in _errors(_schema_3_1_0(), model))


def test_the_top_level_accepts_the_v3_1_0_summary_and_still_rejects_an_unknown_key() -> None:
    db = json.loads((PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json").read_text())
    db = copy.deepcopy(db)
    db["models"] = db["models"][:1]
    db["_migration_summary_v3_1_0"] = {"to_version": "3.1.0", "added": {}}
    validator = jsonschema.Draft7Validator(_schema_3_1_0())
    top = [e.message for e in validator.iter_errors(db) if not e.absolute_path]
    assert not any("_migration_summary_v3_1_0" in m for m in top), top
    db["_bogus_block"] = {}
    top = [e.message for e in validator.iter_errors(db) if not e.absolute_path]
    assert any("'_bogus_block' was unexpected" in m for m in top), top


def test_the_description_carries_the_canonical_version() -> None:
    """``test_db_manager`` reads the canonical version from this string."""
    assert "(v3.1.0)" in _schema_3_1_0()["description"]

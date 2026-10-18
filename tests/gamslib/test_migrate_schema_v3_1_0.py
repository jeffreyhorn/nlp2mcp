"""Sprint 40 P1: the 3.0.0 -> 3.1.0 migration (``SCHEMA_3_1_0_DESIGN.md`` §7, T5).

The migration is additive, so its two dangerous failures are quiet ones:
OVERWRITING a value a 3.1.0 writer already recorded, and GUESSING an edition
for a pre-license row. Both are asserted. ``null`` means unrecorded, and a
pre-license row's edition is unknown, not ``"demo"``.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

_SPEC = importlib.util.spec_from_file_location(
    "migrate_schema_v3_1_0",
    PROJECT_ROOT / "scripts" / "gamslib" / "migrate_schema_v3.1.0.py",
)
assert _SPEC and _SPEC.loader
mig = importlib.util.module_from_spec(_SPEC)
_prev = sys.modules.get("migrate_schema_v3_1_0")
sys.modules["migrate_schema_v3_1_0"] = mig
try:
    _SPEC.loader.exec_module(mig)
finally:
    if _prev is None:
        sys.modules.pop("migrate_schema_v3_1_0", None)
    else:
        sys.modules["migrate_schema_v3_1_0"] = _prev

pytestmark = pytest.mark.unit

#: The last commit whose DB is 3.0.0 (Sprint 40 Day 0's base).
DB_3_0_0_REF = "cd5c6b7e"


def _db() -> dict:
    return {
        "schema_version": "3.0.0",
        "updated_date": "2026-09-14T00:00:00+00:00",
        "total_models": 3,
        "models": [
            {
                "model_id": "a",
                "mcp_solve": {"status": "success"},
                "convexity": {"status": "likely_convex"},
            },
            {"model_id": "b", "convexity": {"status": "non_convex"}},  # no mcp_solve
            {
                "model_id": "c",
                # Already recorded by a 3.1.0 writer: must survive untouched.
                "mcp_solve": {"status": "success", "license_edition": "licensed"},
                "convexity": {
                    "status": "verified_convex",
                    "license_edition": "licensed",
                    "gams_version": "54.2.1",
                },
            },
        ],
    }


def test_add_fields_adds_None_only_where_absent_and_never_overwrites() -> None:
    db = _db()
    added = mig.add_fields(db)
    a, b, c = db["models"]
    assert a["mcp_solve"]["license_edition"] is None, "unrecorded, never 'demo'"
    assert a["convexity"] == {
        "status": "likely_convex",
        "license_edition": None,
        "gams_version": None,
    }
    assert "mcp_solve" not in b, "the migration must not CREATE a stage object"
    assert c["mcp_solve"]["license_edition"] == "licensed", "an existing value is never overwritten"
    assert c["convexity"]["gams_version"] == "54.2.1"
    assert added == {
        "mcp_solve.license_edition": 1,
        "convexity.license_edition": 2,
        "convexity.gams_version": 2,
    }
    assert "solver" not in a["convexity"], "non-nullable; absent until a real value exists"


def test_add_fields_appends_keys_so_existing_order_is_stable() -> None:
    db = _db()
    before = list(db["models"][0]["mcp_solve"].keys())
    mig.add_fields(db)
    assert list(db["models"][0]["mcp_solve"].keys()) == before + ["license_edition"]


def test_a_real_run_bumps_stamps_and_summarises(tmp_path, monkeypatch) -> None:
    db = tmp_path / "db.json"
    db.write_text(json.dumps(_db()))
    monkeypatch.setattr(mig, "validate", lambda _d: [])
    assert mig.main(["--database", str(db), "--no-backup"]) == 0
    out = json.loads(db.read_text())
    assert out["schema_version"] == "3.1.0"
    assert out["updated_date"] != "2026-09-14T00:00:00+00:00", "provenance must move"
    assert out["_migration_summary_v3_1_0"] == {
        "to_version": "3.1.0",
        "added": {
            "mcp_solve.license_edition": 1,
            "convexity.license_edition": 2,
            "convexity.gams_version": 2,
        },
    }


@pytest.mark.parametrize("version", ["3.1.0", "2.2.1", "unknown"])
def test_it_refuses_any_start_but_3_0_0(tmp_path, version: str) -> None:
    """Including a SECOND run: it would add nothing and still bump the version."""
    db = tmp_path / "db.json"
    d = _db()
    d["schema_version"] = version
    before = json.dumps(d)
    db.write_text(before)
    assert mig.main(["--database", str(db), "--no-backup"]) == 1
    assert db.read_text() == before


def test_dry_run_writes_nothing(tmp_path, monkeypatch) -> None:
    db = tmp_path / "db.json"
    before = json.dumps(_db())
    db.write_text(before)
    monkeypatch.setattr(mig, "validate", lambda _d: [])
    assert mig.main(["--database", str(db), "--dry-run"]) == 0
    assert db.read_text() == before


def test_it_refuses_to_write_an_invalid_result(tmp_path, monkeypatch) -> None:
    db = tmp_path / "db.json"
    before = json.dumps(_db())
    db.write_text(before)
    monkeypatch.setattr(mig, "validate", lambda _d: ["models/0: bad"])
    assert mig.main(["--database", str(db), "--no-backup"]) == 1
    assert db.read_text() == before


def test_the_committed_3_0_0_db_migrates_to_a_valid_db_identical_but_for_the_new_keys(
    tmp_path,
) -> None:
    """Against the REAL ``schema.json`` and the REAL 3.0.0 DB (read with ``git show``):
    the output validates, and removing the migration's own keys gives back the
    input exactly. That is the claim the migration's diff makes."""
    pytest.importorskip("jsonschema", reason="optional; the validator no-ops without it")
    try:
        text = subprocess.run(
            ["git", "show", f"{DB_3_0_0_REF}:data/gamslib/gamslib_status.json"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip(f"git history for {DB_3_0_0_REF} is not available (shallow clone?)")
    src = json.loads(text)
    assert src["schema_version"] == "3.0.0"
    db = tmp_path / "db.json"
    db.write_text(text)

    assert mig.main(["--database", str(db), "--no-backup"]) == 0
    assert mig.main(["--database", str(db), "--validate"]) == 0

    out = json.loads(db.read_text())
    assert out["_migration_summary_v3_1_0"]["added"] == {
        "mcp_solve.license_edition": sum(
            isinstance(m.get("mcp_solve"), dict) for m in src["models"]
        ),
        "convexity.license_edition": sum(
            isinstance(m.get("convexity"), dict) for m in src["models"]
        ),
        "convexity.gams_version": sum(isinstance(m.get("convexity"), dict) for m in src["models"]),
    }
    stripped = copy.deepcopy(out)
    for m in stripped["models"]:
        for stage, field in mig.ADDED_FIELDS:
            if isinstance(m.get(stage), dict):
                assert m[stage].pop(field) is None, "every added value is null"
    for key in ("schema_version", "updated_date", "_migration_summary_v3_1_0"):
        stripped.pop(key)
        src.pop(key, None)
    assert stripped == src


def test_the_committed_db_carries_the_fields_on_every_stage_object() -> None:
    """The §2 invariant, on the REAL committed DB: after migration and after any
    pipeline run, every ``mcp_solve`` and ``convexity`` object carries
    ``license_edition`` (present, possibly null), and every ``convexity`` carries
    ``gams_version``. A writer that drops the key is caught here, against real
    data, not only by its unit test."""
    db = json.loads((PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json").read_text())
    assert db["schema_version"] == "3.1.0"
    missing = [
        f"{m['model_id']}.{stage}.{field}"
        for m in db["models"]
        for stage, field in mig.ADDED_FIELDS
        if isinstance(m.get(stage), dict) and field not in m[stage]
    ]
    assert missing == []
    editions = {
        m[stage]["license_edition"]
        for m in db["models"]
        for stage in ("mcp_solve", "convexity")
        if isinstance(m.get(stage), dict)
    }
    assert editions <= {"licensed", "demo", None}

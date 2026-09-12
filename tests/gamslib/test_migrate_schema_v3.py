"""Sprint 39 P7 — the 2.2.1 → 3.0.0 migration.

⚠ THIS FILE EXISTS BECAUSE A DESTRUCTIVE MIGRATION HAD NO TESTS (PR #1740
review). Nothing called `rename_field` or `main`, so a regression in the key
conversion, the row count, the version/date update, or the validate-before-write
refusal would all have stayed green — on a script whose failure mode is a
silently mangled results database.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

_SPEC = importlib.util.spec_from_file_location(
    "migrate_schema_v3",
    PROJECT_ROOT / "scripts" / "gamslib" / "migrate_schema_v3.0.0.py",
)
assert _SPEC and _SPEC.loader
mig = importlib.util.module_from_spec(_SPEC)
_prev = sys.modules.get("migrate_schema_v3")
sys.modules["migrate_schema_v3"] = mig
try:
    _SPEC.loader.exec_module(mig)
finally:
    if _prev is None:
        sys.modules.pop("migrate_schema_v3", None)
    else:
        sys.modules["migrate_schema_v3"] = _prev

pytestmark = pytest.mark.unit


def _db(n_with_key: int = 2, n_without: int = 1) -> dict:
    models = [
        {
            "model_id": f"m{i}",
            "mcp_solve": {"status": "success", "mcp_file_used": f"data/gamslib/mcp/m{i}.gms"},
        }
        for i in range(n_with_key)
    ]
    models += [{"model_id": f"n{i}", "mcp_solve": {"status": "failure"}} for i in range(n_without)]
    return {
        "schema_version": "2.2.1",
        "updated_date": "2026-05-14T00:00:00+00:00",
        "total_models": len(models),
        "models": models,
    }


def test_rename_field_moves_only_rows_that_carry_the_key():
    db = _db(n_with_key=2, n_without=1)
    assert mig.rename_field(db) == 2
    assert [
        ("mcp_file_used" in m["mcp_solve"], "mcp_file_generated" in m["mcp_solve"])
        for m in db["models"]
    ] == [(False, True), (False, True), (False, False)]


def test_rename_field_preserves_the_value_and_other_keys():
    db = _db(n_with_key=1, n_without=0)
    mig.rename_field(db)
    solve = db["models"][0]["mcp_solve"]
    assert solve["mcp_file_generated"] == "data/gamslib/mcp/m0.gms"
    assert solve["status"] == "success", "unrelated keys must survive"


def test_a_migration_refuses_to_run_twice(tmp_path, monkeypatch, capsys):
    """⚠ Running twice would rename nothing and still bump the version."""
    db = tmp_path / "db.json"
    d = _db()
    d["schema_version"] = "3.0.0"
    db.write_text(json.dumps(d))
    assert mig.main(["--database", str(db), "--dry-run"]) == 1


def test_dry_run_validates_and_writes_nothing(tmp_path, monkeypatch):
    db = tmp_path / "db.json"
    before = json.dumps(_db())
    db.write_text(before)
    monkeypatch.setattr(mig, "validate", lambda _d: [])
    assert mig.main(["--database", str(db), "--dry-run"]) == 0
    assert db.read_text() == before, "--dry-run must not write"


def test_a_real_run_renames_bumps_and_stamps_the_date(tmp_path, monkeypatch):
    db = tmp_path / "db.json"
    db.write_text(json.dumps(_db(n_with_key=2)))
    monkeypatch.setattr(mig, "validate", lambda _d: [])
    assert mig.main(["--database", str(db), "--no-backup"]) == 0

    out = json.loads(db.read_text())
    assert out["schema_version"] == "3.0.0"
    assert out["updated_date"] != "2026-05-14T00:00:00+00:00", "provenance must move"
    assert out["_migration_summary_v3_0_0"]["renamed"]["rows"] == 2
    assert all("mcp_file_used" not in m["mcp_solve"] for m in out["models"])


def test_it_REFUSES_TO_WRITE_when_the_result_would_be_invalid(tmp_path, monkeypatch):
    """⚠ The fail-closed property, which is the point of restoring --validate.

    v2.2.0 and v2.2.1 dropped the flag v2.1.0 had; a migration that cannot check
    its own output is the wrong tool for a breaking change.
    """
    db = tmp_path / "db.json"
    before = json.dumps(_db())
    db.write_text(before)
    monkeypatch.setattr(mig, "validate", lambda _d: [{"path": "x", "message": "boom"}])
    assert mig.main(["--database", str(db), "--no-backup"]) == 1
    assert db.read_text() == before, "an invalid migration must leave the file untouched"


def test_validate_FAILS_CLOSED_without_jsonschema(monkeypatch):
    """Absent the optional library, validation must report rather than pass."""
    import builtins

    real = builtins.__import__

    def blocked(name, *a, **k):
        if name.split(".")[0] == "jsonschema":
            raise ImportError("blocked")
        return real(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", blocked)
    errors = mig.validate(_db())
    assert len(errors) == 1
    assert "jsonschema" in errors[0].lower()


def test_the_writer_does_not_re_encode_unicode(tmp_path, monkeypatch):
    """⚠ `ensure_ascii=False` rewrote unrelated escaped text (PR #1740 review).

    A migration's diff is its evidence; anything in it the migration did not
    intend is noise a reviewer has to disprove.
    """
    db = tmp_path / "db.json"
    d = _db(n_with_key=1, n_without=0)
    d["models"][0]["notes"] = "em—dash and arrow→here"
    db.write_text(json.dumps(d))
    monkeypatch.setattr(mig, "validate", lambda _d: [])
    assert mig.main(["--database", str(db), "--no-backup"]) == 0
    raw = db.read_text()
    assert "\\u2014" in raw and "\\u2192" in raw, "escapes must survive untouched"

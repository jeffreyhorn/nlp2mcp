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


def _block_jsonschema(monkeypatch):
    import builtins

    real = builtins.__import__

    def blocked(name, *a, **k):
        if name.split(".")[0] == "jsonschema":
            raise ImportError("blocked")
        return real(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", blocked)


def test_validate_returns_None_when_it_CANNOT_RUN(monkeypatch):
    """⚠ `None` (could not check) and `[]` (checked, clean) are different.

    An earlier revision returned a synthetic error for the missing library,
    which made the two indistinguishable (PR #1740 review).
    """
    _block_jsonschema(monkeypatch)
    assert mig.validate(_db()) is None


def test_the_DEFAULT_migration_still_runs_without_jsonschema(tmp_path, monkeypatch, caplog):
    """⚠ Refusing here made the documented command unrunnable.

    `jsonschema` is deliberately optional and undeclared, so treating its
    absence as a validation failure blocked the migration on any machine
    lacking it — a worse outcome than an unvalidated run, because the operator
    cannot migrate at all.
    """
    db = tmp_path / "db.json"
    db.write_text(json.dumps(_db(n_with_key=2)))
    _block_jsonschema(monkeypatch)

    assert mig.main(["--database", str(db), "--no-backup"]) == 0
    out = json.loads(db.read_text())
    assert out["schema_version"] == "3.0.0"
    assert all("mcp_file_used" not in m["mcp_solve"] for m in out["models"])
    assert any(
        "NOT validated" in r.getMessage() for r in caplog.records
    ), "the operator must be warned that the run was unvalidated"


def test_an_EXPLICIT_validate_still_fails_when_it_cannot_run(tmp_path, monkeypatch):
    """Asked for validation and cannot deliver it → error, not a silent pass."""
    db = tmp_path / "db.json"
    before = json.dumps(_db())
    db.write_text(before)
    _block_jsonschema(monkeypatch)

    assert mig.main(["--database", str(db), "--no-backup", "--validate"]) == 1
    assert db.read_text() == before, "and it must not have written an unvalidated result"


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


def test_a_real_migration_validates_against_the_ACTUAL_schema(tmp_path):
    """⚠ Every other success test stubs `validate` (PR #1740 review).

    That means none of them exercised the validate-before-write path against
    the real `schema.json` — so a future mismatch between what the migration
    writes and what the contract permits could still produce an invalid
    database while this suite stayed green. Which is not hypothetical: the
    migration's own `_migration_summary_v3_0_0` block was rejected on first
    run, because the schema root is `additionalProperties: false`.
    """
    pytest.importorskip("jsonschema", reason="optional; the validator no-ops without it")

    src = json.loads((PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json").read_text())
    # Rewind the committed database to the pre-migration shape.
    src["schema_version"] = "2.2.1"
    src.pop("_migration_summary_v3_0_0", None)
    for m in src["models"]:
        solve = m.get("mcp_solve")
        if isinstance(solve, dict) and "mcp_file_generated" in solve:
            solve["mcp_file_used"] = solve.pop("mcp_file_generated")

    db = tmp_path / "db.json"
    db.write_text(json.dumps(src))

    assert (
        mig.main(["--database", str(db), "--no-backup"]) == 0
    ), "the real validator must accept what the migration writes"
    out = json.loads(db.read_text())
    assert out["schema_version"] == "3.0.0"
    assert mig.main(["--database", str(db), "--validate"]) == 0

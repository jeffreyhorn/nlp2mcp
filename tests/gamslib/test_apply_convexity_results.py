"""W10, ``apply_convexity_results.py``: verifier results -> DB, with the corpus hold.

Sprint 40 P1/P3 (``SCHEMA_3_1_0_DESIGN.md`` §6, test T9's W10 part). A convexity
write is a corpus write (the candidate corpus is derived from
``convexity.status``), so the central properties are refusals:

* a model entering the convex set without ``--admit`` is refused;
* an ``--admit`` not recorded in ``corpus_admissions.json`` is refused, or the
  continuity denominator would grow silently anyway;
* MINLP/MIP and unknown ids are refused;
* a result without its own ``verification_date`` is refused, not back-dated.

Every test runs on a COPY of the committed DB in ``tmp_path``.
"""

from __future__ import annotations

import copy
import json
import logging
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gamslib import apply_convexity_results as w10  # noqa: E402
from scripts.sprint_audit.check_mcp_solve_attribution import (  # noqa: E402
    _validate_against_schema,
)

DB_PATH = PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json"


def _result(mid: str = "torsion", **over: object) -> dict:
    """A verifier result shaped exactly like ``VerificationResult.to_dict()``."""
    r = {
        "model_id": mid,
        "model_path": f"/x/{mid}.gms",
        "convexity_status": "likely_convex",
        "solver_status": 1,
        "model_status": 2,
        "objective_value": -0.4175,
        "solve_time_seconds": 0.67,
        "timed_out": False,
        "error_message": None,
        "license_edition": "licensed",
        "gams_version": "54.2.1",
        "solver": "CONOPT",
        "verification_date": "2026-10-19T23:17:14Z",
    }
    r.update(over)
    return r


def _run(tmp_path: Path, results: list[dict], admit=(), recorded=(), extra=()) -> tuple[int, dict]:
    db = tmp_path / "db.json"
    db.write_text(DB_PATH.read_text())
    inp = tmp_path / "in.json"
    inp.write_text(json.dumps({"verification_date": "2026-10-19T23:20:00Z", "results": results}))
    adm = tmp_path / "adm.json"
    adm.write_text(json.dumps({"admissions": [{"model_id": m} for m in recorded]}))
    argv = ["--input", str(inp), "--db", str(db), "--admissions", str(adm), "--no-backup", *extra]
    if admit:
        argv += ["--admit", *admit]
    rc = w10.main(argv)
    return rc, json.loads(db.read_text())


def _row(db: dict, mid: str) -> dict:
    return next(m for m in db["models"] if m["model_id"] == mid)


# --------------------------------------------------------------- the hold


def test_entering_the_corpus_without_admit_is_refused_and_nothing_is_written(tmp_path) -> None:
    """RECORDED in corpus_admissions.json but NOT --admit-ted: only the hold can
    refuse it. (Without the record, the record check would refuse it first, and
    a first version of this test passed with the hold removed.)"""
    before = DB_PATH.read_text()
    rc, db = _run(tmp_path, [_result()], recorded=["torsion"])
    assert rc == 1
    assert json.dumps(db, indent=2) + "\n" == before or db == json.loads(before)


def test_an_admit_not_recorded_in_corpus_admissions_is_refused(tmp_path) -> None:
    rc, db = _run(tmp_path, [_result()], admit=["torsion"])
    assert rc == 1
    assert _row(db, "torsion")["convexity"]["status"] == "error", "unchanged"


def test_admitted_and_recorded_applies(tmp_path) -> None:
    rc, db = _run(tmp_path, [_result()], admit=["torsion"], recorded=["torsion"])
    assert rc == 0
    assert _row(db, "torsion")["convexity"]["status"] == "likely_convex"


def test_an_unused_admit_is_refused(tmp_path) -> None:
    """--admit is an owner decision; one that admits nothing is a mistake, not a no-op."""
    rc, _ = _run(
        tmp_path, [_result()], admit=["torsion", "trnsport"], recorded=["torsion", "trnsport"]
    )
    assert rc == 1


def test_a_model_leaving_the_corpus_is_applied_and_reported(tmp_path, caplog) -> None:
    caplog.set_level(logging.INFO)
    rc, db = _run(tmp_path, [_result("trnsport", convexity_status="non_convex", solver="CPLEX")])
    assert rc == 0
    assert _row(db, "trnsport")["convexity"]["status"] == "non_convex"
    assert "leaving" in caplog.text and "trnsport" in caplog.text


# ---------------------------------------------------------- scope refusals


def test_mip_and_unknown_ids_are_refused() -> None:
    """Asserted on the planner's own refusal message, with `andean` admitted AND
    recorded, so only the type guard can refuse it. (A first version ran it
    un-admitted, where the hold refused it and the type guard was never reached.)"""
    db = json.loads(DB_PATH.read_text())
    with pytest.raises(w10.Refusal, match="andean: type 'MIP' is out of scope"):
        w10.plan(
            db,
            [_result("andean", convexity_status="verified_convex")],
            frozenset({"andean"}),
            frozenset({"andean"}),
        )
    with pytest.raises(w10.Refusal, match="'no_such_model': not a model in the DB"):
        w10.plan(db, [_result("no_such_model")], frozenset(), frozenset())


def test_a_result_without_its_own_verification_date_is_refused() -> None:
    """Asserted on the refusal itself. A null date would ALSO fail schema
    validation, so an exit code alone cannot tell which guard fired. A first
    version checked only rc and passed with this refusal removed."""
    with pytest.raises(w10.Refusal, match="no per-result verification_date"):
        w10.convexity_from_result(_result(verification_date=None))
    db = json.loads(DB_PATH.read_text())
    with pytest.raises(w10.Refusal, match="no per-result verification_date"):
        w10.plan(
            db, [_result(verification_date=None)], frozenset({"torsion"}), frozenset({"torsion"})
        )


# ---------------------------------------------------- mapping and validity


def test_the_mapping_omits_non_nullable_None_and_always_writes_provenance(tmp_path) -> None:
    rc, db = _run(tmp_path, [_result()], admit=["torsion"], recorded=["torsion"])
    assert rc == 0
    conv = _row(db, "torsion")["convexity"]
    assert (
        "error" not in conv
    ), "a successful result (error_message None) must NOT write error: null"
    assert conv["verification_date"] == "2026-10-19T23:17:14Z", "verbatim, never the envelope's"
    assert (conv["license_edition"], conv["gams_version"], conv["solver"]) == (
        "licensed",
        "54.2.1",
        "CONOPT",
    )
    refused_listing = _result(
        "airsp",
        convexity_status="error",
        solver=None,
        solver_status=None,
        model_status=None,
        objective_value=None,
        error_message="Model exceeds demo license limits",
        license_edition="demo",
    )
    rc, db = _run(tmp_path, [refused_listing])
    conv = _row(db, "airsp")["convexity"]
    assert rc == 0
    assert not {"solver", "solver_status", "model_status", "objective_value"} & set(conv)
    assert conv["error"] == "Model exceeds demo license limits"
    assert conv["license_edition"] == "demo" and "gams_version" in conv


def test_convexity_is_replaced_not_merged(tmp_path) -> None:
    """The old row carries the demo-era `error`; a merge would keep it under the
    new run's provenance."""
    assert "error" in _row(json.loads(DB_PATH.read_text()), "torsion")["convexity"]
    rc, db = _run(tmp_path, [_result()], admit=["torsion"], recorded=["torsion"])
    assert rc == 0
    assert "error" not in _row(db, "torsion")["convexity"]


def test_the_output_validates_including_RFC3339_dates(tmp_path) -> None:
    pytest.importorskip("jsonschema", reason="optional; the validator no-ops without it")
    rc, db = _run(
        tmp_path, [_result()], admit=["torsion"], recorded=["torsion"], extra=["--validate"]
    )
    assert rc == 0
    assert _validate_against_schema(db, tmp_path / "db.json") is None
    assert db["updated_date"] != json.loads(DB_PATH.read_text())["updated_date"]


def test_dry_run_writes_nothing(tmp_path) -> None:
    rc, db = _run(
        tmp_path, [_result()], admit=["torsion"], recorded=["torsion"], extra=["--dry-run"]
    )
    assert rc == 0
    assert db == json.loads(DB_PATH.read_text())


def test_plan_reports_every_problem_at_once() -> None:
    """One run names every offending model, not just the first."""
    db = json.loads(DB_PATH.read_text())
    results = [
        _result("torsion"),
        _result("airsp", convexity_status="verified_convex"),
        _result("andean"),
    ]
    with pytest.raises(w10.Refusal) as exc:
        w10.plan(copy.deepcopy(db), results, frozenset(), frozenset())
    msg = str(exc.value)
    assert "torsion" in msg and "airsp" in msg and "andean" in msg

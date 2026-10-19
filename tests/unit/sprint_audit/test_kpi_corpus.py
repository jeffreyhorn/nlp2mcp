"""``kpi_block.py --corpus continuity|current`` (Sprint 40 P1, owner Decision 2 = A).

Admission is by rule, so the 142 denominator would otherwise grow silently with
the first licensed convexity run (Prep Task 6: 142 -> 143 on a scratch DB). Both
denominators must derive mechanically from one function, and ``continuity`` must
stay the 142 series however many models are admitted.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "sprint_audit"))
from kpi_block import compute_kpis, load_admissions  # noqa: E402

sys.path.pop(0)

DB = json.loads((PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json").read_text())


def test_continuity_equals_current_on_todays_db() -> None:
    """No admissions yet, so the two corpora are the same 142 (Decision 2's own test)."""
    admitted = load_admissions()
    assert admitted == frozenset()
    current, continuity = compute_kpis(DB), compute_kpis(DB, exclude=admitted)
    assert current == continuity
    assert current["candidates"] == 142


def _admit_one(db: dict) -> tuple[dict, str]:
    """A scratch DB where one non-convex, in-scope model is newly classified convex."""
    db = copy.deepcopy(db)
    model = next(
        m
        for m in db["models"]
        if (m.get("convexity") or {}).get("status") not in ("verified_convex", "likely_convex")
        and m.get("gamslib_type") in ("LP", "NLP", "QCP")
    )
    model["convexity"]["status"] = "likely_convex"
    return db, model["model_id"]


def test_an_admitted_model_grows_current_but_not_continuity() -> None:
    db, mid = _admit_one(DB)
    current = compute_kpis(db)
    continuity = compute_kpis(db, exclude=frozenset({mid}))
    assert current["candidates"] == 143, "the silent growth this guards against"
    assert continuity == compute_kpis(DB), "continuity is the unchanged 142 series"
    assert current["all_219_match"] == continuity["all_219_match"], "never corpus-scoped"


def test_an_absent_admissions_file_means_none(tmp_path: Path) -> None:
    assert load_admissions(tmp_path / "nope.json") == frozenset()


@pytest.mark.parametrize(
    "payload",
    [{}, {"admissions": {}}, {"admissions": [{"model": "x"}]}, {"admissions": [{"model_id": ""}]}],
)
def test_a_malformed_admissions_file_raises(tmp_path: Path, payload: dict) -> None:
    """Treating a broken file as empty would make continuity == current while
    claiming otherwise."""
    f = tmp_path / "a.json"
    f.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        load_admissions(f)


def _cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts/sprint_audit/kpi_block.py"), *args],
        capture_output=True,
        text=True,
    )


def test_the_cli_reports_both_corpora_through_an_admissions_file(tmp_path: Path) -> None:
    db, mid = _admit_one(DB)
    dbf, adm = tmp_path / "db.json", tmp_path / "adm.json"
    dbf.write_text(json.dumps(db))
    adm.write_text(json.dumps({"admissions": [{"model_id": mid}]}))
    cur = json.loads(_cli("--json", "--db", str(dbf), "--admissions", str(adm)).stdout)
    con = json.loads(
        _cli("--json", "--db", str(dbf), "--admissions", str(adm), "--corpus", "continuity").stdout
    )
    assert (cur["corpus"], cur["candidates"], cur["admitted"]) == ("current", 143, 1)
    assert (con["corpus"], con["candidates"], con["admitted"]) == ("continuity", 142, 1)
    line = _cli(
        "--format", "line", "--db", str(dbf), "--admissions", str(adm), "--corpus", "continuity"
    )
    assert "corpus continuity (142 candidates, 1 admitted)" in line.stdout


def test_a_malformed_admissions_file_fails_the_cli(tmp_path: Path) -> None:
    adm = tmp_path / "adm.json"
    adm.write_text("{not json")
    assert _cli("--json", "--admissions", str(adm)).returncode == 2


def test_the_kpi_corpus_and_the_pipeline_run_set_differ_by_exactly_two_named_models() -> None:
    """Prep Task 6 side finding, pinned BY IDENTITY: `kpi_block` (142) keeps the two
    convex multi-solve drivers that `batch_parse` skips (140). A count would pass
    if one of them were swapped for a third model; the set does not."""
    sys.path.insert(0, str(PROJECT_ROOT))
    try:
        from scripts.gamslib.batch_parse import get_candidate_models
    finally:
        sys.path.pop(0)
    kpi_ids = {
        m["model_id"]
        for m in DB["models"]
        if (m.get("convexity") or {}).get("status") in ("verified_convex", "likely_convex")
    }
    run_ids = {m["model_id"] for m in get_candidate_models(DB)}
    assert kpi_ids - run_ids == {"danwolfe", "decomp"}
    assert run_ids <= kpi_ids
    for mid in ("danwolfe", "decomp"):
        row = next(m for m in DB["models"] if m["model_id"] == mid)
        assert row["pipeline_status"]["reason"] == "multi_solve_driver_out_of_scope"

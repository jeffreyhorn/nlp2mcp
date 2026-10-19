"""``kpi_block.py --corpus continuity|current`` (Sprint 40 P1, owner Decision 2 = A).

Admission is by rule, so the candidate denominator would otherwise grow silently
with the first licensed convexity run (Prep Task 6: 142 -> 143 on a scratch DB).
Both denominators must derive mechanically from one function, and ``continuity``
must stay the base series however many models are admitted. The base is **140**
since the owner's Sprint 40 re-base (2026-10-19): the corpus rule is convex AND
not ``pipeline_status: skipped``, applied identically by all three readers.
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
    """No admissions yet, so the two corpora are the same 140 (Decision 2's own test)."""
    admitted = load_admissions()
    assert admitted == frozenset()
    current, continuity = compute_kpis(DB), compute_kpis(DB, exclude=admitted)
    assert current == continuity
    assert current["candidates"] == 140


def _admit_one(db: dict) -> tuple[dict, str]:
    """A scratch DB where one non-convex, in-scope model is newly classified convex."""
    db = copy.deepcopy(db)
    model = next(
        m
        for m in db["models"]
        if (m.get("convexity") or {}).get("status") not in ("verified_convex", "likely_convex")
        and m.get("gamslib_type") in ("LP", "NLP", "QCP")
        and (m.get("pipeline_status") or {}).get("status") != "skipped"
    )
    model["convexity"]["status"] = "likely_convex"
    return db, model["model_id"]


def test_an_admitted_model_grows_current_but_not_continuity() -> None:
    db, mid = _admit_one(DB)
    current = compute_kpis(db)
    continuity = compute_kpis(db, exclude=frozenset({mid}))
    assert current["candidates"] == 141, "the silent growth this guards against"
    assert continuity == compute_kpis(DB), "continuity is the unchanged 140 series"
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
    assert (cur["corpus"], cur["candidates"], cur["admitted"]) == ("current", 141, 1)
    assert (con["corpus"], con["candidates"], con["admitted"]) == ("continuity", 140, 1)
    line = _cli(
        "--format", "line", "--db", str(dbf), "--admissions", str(adm), "--corpus", "continuity"
    )
    assert "corpus continuity (140 candidates, 1 admitted)" in line.stdout


def test_a_malformed_admissions_file_fails_the_cli(tmp_path: Path) -> None:
    adm = tmp_path / "adm.json"
    adm.write_text("{not json")
    assert _cli("--json", "--admissions", str(adm)).returncode == 2


def test_all_three_corpus_readers_select_the_same_140_models() -> None:
    """Owner decision, Sprint 40 (2026-10-19): re-based 142 -> 140. `kpi_block`,
    `batch_parse` and `run_full_test` each select the corpus, and before the
    re-base they disagreed (142 / 140 / 142). Pinned as one IDENTICAL set, not a
    count, so a swap cannot pass, and the two out-of-scope multi-solve drivers
    are named so their exclusion is explicit."""
    sys.path.insert(0, str(PROJECT_ROOT))
    try:
        from scripts.gamslib.batch_parse import get_candidate_models as bp_candidates
        from scripts.gamslib.run_full_test import get_candidate_models as rft_candidates
    finally:
        sys.path.pop(0)
    sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "sprint_audit"))
    try:
        import kpi_block
    finally:
        sys.path.pop(0)
    kpi_ids = {
        m["model_id"]
        for m in DB["models"]
        if (m.get("convexity") or {}).get("status") in kpi_block.CONVEX_STATUSES
        and (m.get("pipeline_status") or {}).get("status") != "skipped"
    }
    assert compute_kpis(DB)["candidates"] == len(kpi_ids) == 140
    assert {m["model_id"] for m in bp_candidates(DB)} == kpi_ids
    assert {m["model_id"] for m in rft_candidates(DB)} == kpi_ids
    for mid in ("danwolfe", "decomp"):
        row = next(m for m in DB["models"] if m["model_id"] == mid)
        assert row["pipeline_status"]["reason"] == "multi_solve_driver_out_of_scope"
        assert (
            row["convexity"]["status"] == "verified_convex"
        ), "excluded by the skip, not by convexity"
        assert mid not in kpi_ids


def test_the_current_corpus_line_passes_the_doc_figure_checker_after_an_admission(tmp_path) -> None:
    """PR #1762 review: a BARE figure is checked against continuity, so once a model
    is admitted a correct `--corpus current` line must carry `N/D` to be matched to
    its own corpus. Both lines, rendered from one admitted scratch DB, must pass."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "cdf_for_kpi", PROJECT_ROOT / "scripts" / "sprint_audit" / "check_doc_figures.py"
    )
    assert spec and spec.loader
    cdf = importlib.util.module_from_spec(spec)
    # Registered BEFORE exec: the module defines dataclasses, which resolve their
    # own module through sys.modules.
    sys.modules["cdf_for_kpi"] = cdf
    try:
        spec.loader.exec_module(cdf)
    except BaseException:
        sys.modules.pop("cdf_for_kpi", None)
        raise

    db, mid = _admit_one(DB)
    # Make the admitted model ADD to the numerators, so the corpora really differ.
    row = next(m for m in db["models"] if m["model_id"] == mid)
    row["nlp2mcp_parse"] = {"status": "success"}
    row["nlp2mcp_translate"] = {"status": "success"}
    row["mcp_solve"] = {"status": "success", "outcome_category": "model_optimal"}
    row["solution_comparison"] = {"comparison_status": "match"}
    blocks = {"continuity": compute_kpis(db, exclude=frozenset({mid})), "current": compute_kpis(db)}
    assert blocks["current"]["match"] == blocks["continuity"]["match"] + 1

    truths: dict = {"Match": blocks["continuity"]["match"], "Solve": blocks["continuity"]["solve"],
                    "Translate": blocks["continuity"]["translate"]}  # fmt: skip
    key = {"Match": "match", "Translate": "translate", "Solve": "solve"}
    for fact, den in cdf._DENOMINATOR_OF.items():
        for corpus, k in blocks.items():
            truths[f"{fact}|{corpus}"] = k[key[fact]]
            truths[f"{fact}|{corpus}|den"] = k[den]

    sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "sprint_audit"))
    try:
        from kpi_block import _render_line
    finally:
        sys.path.pop(0)
    for corpus, k in blocks.items():
        line = _render_line({**k, "corpus": corpus, "admitted": 1}, "abc1234", dirty=False)
        findings, reason = cdf.scan_line(Path("x.md"), 1, line, truths)
        assert reason is None and findings == [], (corpus, line, findings)

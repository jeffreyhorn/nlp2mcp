"""Schema 3.1.0 provenance: the parser and every writer of ``license_edition``.

Sprint 40 P1 (``SCHEMA_3_1_0_DESIGN.md`` §3–§5, tests T1–T4 and the W7–W9 part
of T9). Two failure modes matter:

* a FIXED-KEY-LIST writer that does not name the field drops it silently. That
  is how ``mcp_attribution`` was lost in Sprint 39, so W2 and W3 are asserted
  directly;
* a writer that GUESSES. ``None`` means unrecorded, so every path that never
  classified a listing must write ``None``, never ``"demo"``.

LICENSE HYGIENE: every listing here is SYNTHETIC. The licensed ``USER:`` line is
a made-up licensee, and the demo line stops before its license-ID tail. Never
paste a real listing header into this file.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gamslib.test_solve import (  # noqa: E402
    extract_gams_version,
    extract_license_edition,
    extract_solver_name,
    solve_mcp,
    update_model_solve_result,
)

HEADER = "GAMS 54.2.1  abcdef12 Jul 13, 2026          DEX-DEG x86 64bit/macOS - 10/18/26 12:00:00 Page 1\n"
LICENSED_USER = "USER: Example Licensee                                  G000000:0000AB-GEN\n"
DEMO_USER = "USER: GAMS Demo, for EULA and demo limitations see\n"
REFUSAL = "**** The model exceeds the demo license limits for nonlinear models of more than 1000 rows or columns\n"


def summary(solver: str, line: int = 3) -> str:
    return (
        "               S O L V E      S U M M A R Y\n\n"
        "     MODEL   m                   OBJECTIVE  z\n"
        "     TYPE    NLP                 DIRECTION  MINIMIZE\n"
        f"     SOLVER  {solver:<18}  FROM LINE  {line}\n\n"
        "**** SOLVER STATUS     1 Normal Completion\n"
        "**** MODEL STATUS      2 Locally Optimal\n"
    )


LICENSED_LST = HEADER + LICENSED_USER + summary("CONOPT")
DEMO_SMALL_LST = HEADER + DEMO_USER + summary("CONOPT")
DEMO_REFUSED_LST = HEADER + REFUSAL


# --------------------------------------------------------------------- T1: parser


class TestExtractLicenseEdition:
    def test_licensed_user_line(self) -> None:
        assert extract_license_edition(LICENSED_LST) == "licensed"

    def test_demo_user_line(self) -> None:
        assert extract_license_edition(DEMO_SMALL_LST) == "demo"

    def test_refused_listing_is_demo_although_it_has_no_user_line(self) -> None:
        assert "USER:" not in DEMO_REFUSED_LST
        assert extract_license_edition(DEMO_REFUSED_LST) == "demo"

    def test_neither_marker_is_None_never_demo(self) -> None:
        assert extract_license_edition(HEADER + summary("PATH")) is None
        assert extract_license_edition("") is None

    def test_demo_wins_when_both_markers_appear(self) -> None:
        """Order: the demo patterns are tested first."""
        assert extract_license_edition(HEADER + LICENSED_USER + REFUSAL) == "demo"

    def test_the_licensee_is_never_returned(self) -> None:
        out = extract_license_edition(LICENSED_LST)
        assert out == "licensed" and "Example" not in str(out)

    def test_markers_must_start_a_line(self) -> None:
        """Prefix-matched at line start: a quoted marker mid-line is not a listing header."""
        quoted = HEADER + "* comment mentioning USER: GAMS Demo, inside a model\n"
        assert extract_license_edition(quoted) is None


class TestExtractSolverName:
    def test_solver_from_summary(self) -> None:
        assert extract_solver_name(LICENSED_LST) == "CONOPT"
        assert extract_solver_name(HEADER + summary("PATH")) == "PATH"

    def test_refused_listing_has_no_solver(self) -> None:
        assert extract_solver_name(DEMO_REFUSED_LST) is None

    def test_last_solve_wins(self) -> None:
        assert extract_solver_name(HEADER + summary("CPLEX", 3) + summary("CONOPT", 9)) == "CONOPT"

    def test_version_is_read_from_a_refused_listing_too(self) -> None:
        assert extract_gams_version(DEMO_REFUSED_LST) == "54.2.1"


# --------------------------------------------------------- T2: solve_mcp (W1)


class TestSolveMcpCarriesTheEdition:
    @patch("subprocess.run")
    @patch("shutil.which", return_value="/usr/bin/gams")
    def test_a_classified_listing_sets_the_edition(self, _which, mock_run) -> None:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        lst = HEADER + LICENSED_USER + summary("PATH", 105)
        with patch("tempfile.TemporaryDirectory") as tmp:
            tmp.return_value.__enter__.return_value = "/tmp/t"
            with patch.object(Path, "exists", return_value=True):
                with patch.object(Path, "read_text", return_value=lst):
                    result = solve_mcp(Path("/test/model.gms"))
        assert result["license_edition"] == "licensed"

    @patch("shutil.which", return_value=None)
    @patch.object(Path, "exists", return_value=False)
    def test_no_gams_is_None(self, _exists, _which) -> None:
        result = solve_mcp(Path("/nonexistent/model.gms"))
        assert "license_edition" in result and result["license_edition"] is None

    @patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="gams", timeout=1))
    @patch("shutil.which", return_value="/usr/bin/gams")
    def test_timeout_is_None(self, _which, _run) -> None:
        result = solve_mcp(Path("/test/model.gms"), timeout=1)
        assert "license_edition" in result and result["license_edition"] is None

    @patch("subprocess.run")
    @patch("shutil.which", return_value="/usr/bin/gams")
    def test_no_listing_is_None(self, _which, mock_run) -> None:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")
        with patch("tempfile.TemporaryDirectory") as tmp:
            tmp.return_value.__enter__.return_value = "/tmp/t"
            with patch.object(Path, "exists", return_value=False):
                result = solve_mcp(Path("/test/model.gms"))
        assert "license_edition" in result and result["license_edition"] is None


# ------------------------------------- T3: update_model_solve_result (W2)


def _solve_result(**extra: object) -> dict:
    base = {
        "status": "success",
        "solver_status": 1,
        "solver_status_text": "Normal Completion",
        "model_status": 1,
        "model_status_text": "Optimal",
        "objective_value": 1.0,
        "solve_time_seconds": 0.1,
        "iterations": 1,
        "outcome_category": "model_optimal",
    }
    base.update(extra)
    return base


@pytest.mark.parametrize("edition", ["licensed", "demo", None])
def test_update_model_solve_result_persists_the_edition(edition: str | None) -> None:
    """W2 is a fixed-key-list writer: a field it does not NAME vanishes."""
    model: dict = {"model_id": "m"}
    update_model_solve_result(model, _solve_result(license_edition=edition))
    assert "license_edition" in model["mcp_solve"]
    assert model["mcp_solve"]["license_edition"] == edition


def test_update_model_solve_result_writes_None_for_a_legacy_result() -> None:
    """A result from older code carries no edition: recorded as unknown, not dropped."""
    model: dict = {"model_id": "m"}
    update_model_solve_result(model, _solve_result())
    assert model["mcp_solve"]["license_edition"] is None


# ------------------------------------------------ T4: run_full_test (W3–W5)


def _run_stage(model: dict, solve_result: dict) -> None:
    import scripts.gamslib.run_full_test as rft

    orig = rft.get_solve_function
    rft.get_solve_function = lambda: (lambda _path, timeout=120: dict(solve_result))
    try:
        rft.run_solve_stage(
            model, Path("unused.gms"), argparse.Namespace(verbose=False), rft._new_stats(1)
        )
    finally:
        rft.get_solve_function = orig


@pytest.mark.parametrize("edition", ["licensed", "demo", None])
def test_run_solve_stage_persists_the_edition(edition: str | None) -> None:
    model: dict = {"model_id": "m"}
    _run_stage(model, _solve_result(license_edition=edition))
    assert "license_edition" in model["mcp_solve"]
    assert model["mcp_solve"]["license_edition"] == edition


@pytest.mark.parametrize("failed_stage", ["parse", "translate"])
def test_cascade_rows_record_None(failed_stage: str) -> None:
    """W4: no GAMS ran for a cascade skip, so the edition is unrecorded (§2 invariant)."""
    from scripts.gamslib.run_full_test import _new_stats, mark_cascade_not_tested

    model: dict = {"model_id": "m"}
    mark_cascade_not_tested(model, failed_stage, _new_stats(1))
    assert model["mcp_solve"]["status"] == "not_tested"
    assert "license_edition" in model["mcp_solve"]
    assert model["mcp_solve"]["license_edition"] is None


def test_the_presolve_restore_keeps_the_cold_runs_edition() -> None:
    """W5 needs no change, and this shows why. It reproduces the retry's steps
    around the REAL ``run_solve_stage``: copy the cold record
    (``run_full_test.py`` ``original_mcp_solve = model["mcp_solve"].copy()``),
    let the retry overwrite it, then restore the copy on a failed retry. Each
    record keeps the edition of the run that produced it."""
    model: dict = {"model_id": "m"}
    _run_stage(model, _solve_result(license_edition="licensed"))
    original = model["mcp_solve"].copy()
    _run_stage(model, _solve_result(status="failure", license_edition="demo"))
    assert model["mcp_solve"]["license_edition"] == "demo"
    model["mcp_solve"] = original
    assert model["mcp_solve"]["license_edition"] == "licensed"

    src = (PROJECT_ROOT / "scripts" / "gamslib" / "run_full_test.py").read_text()
    assert 'original_mcp_solve = model["mcp_solve"].copy()' in src
    assert 'model["mcp_solve"] = original_mcp_solve' in src


# ------------------------------------------- T9 (part): verify_convexity W7–W9

UTC_STAMP = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")


def _verify(lst: str | None, *, returncode: int = 0, raise_: Exception | None = None):
    """Run ``verify_model`` against a mocked GAMS whose listing is ``lst``."""
    from scripts.gamslib import verify_convexity as vc

    def fake_run(cmd, **kw):
        if raise_ is not None:
            raise raise_
        out = next(a[2:] for a in cmd if a.startswith("o="))
        if lst is not None:
            Path(out).write_text(lst)
        return MagicMock(returncode=returncode, stdout="", stderr="")

    with patch.object(vc.subprocess, "run", side_effect=fake_run):
        return vc.verify_model("m", Path("/x/m.gms"), "NLP", timeout_seconds=5)


def test_verify_model_records_provenance_from_its_own_listing() -> None:
    r = _verify(HEADER + LICENSED_USER + summary("CONOPT"))
    assert (r.license_edition, r.gams_version, r.solver) == ("licensed", "54.2.1", "CONOPT")
    assert UTC_STAMP.match(r.verification_date or "")
    d = r.to_dict()
    assert {"license_edition", "gams_version", "solver", "verification_date"} <= set(d)


def test_the_demo_refusal_records_demo_and_version_but_no_solver() -> None:
    r = _verify(DEMO_REFUSED_LST)
    assert r.error_message == "Model exceeds demo license limits"
    assert (r.license_edition, r.gams_version, r.solver) == ("demo", "54.2.1", None)
    assert UTC_STAMP.match(r.verification_date or "")


@pytest.mark.parametrize(
    "kind",
    ["excluded", "no_gams", "timeout", "compile_error", "no_listing"],
)
def test_returns_before_any_listing_carry_None_but_a_date(kind: str) -> None:
    from scripts.gamslib import verify_convexity as vc

    if kind == "excluded":
        r = vc.verify_model("m", Path("/x/m.gms"), "MIP")
    elif kind == "no_gams":
        r = _verify(None, raise_=FileNotFoundError())
    elif kind == "timeout":
        r = _verify(None, raise_=subprocess.TimeoutExpired(cmd="gams", timeout=5))
    elif kind == "compile_error":
        r = _verify(LICENSED_LST, returncode=2)
    else:
        r = _verify(None)
    assert (r.license_edition, r.gams_version, r.solver) == (None, None, None), kind
    assert UTC_STAMP.match(r.verification_date or ""), kind


def test_update_catalog_entry_writes_and_clears_the_flat_fields() -> None:
    """W8: present-or-delete, so a re-run without a listing leaves no stale provenance."""
    from scripts.gamslib import verify_convexity as vc

    entry: dict = {}
    vc.update_catalog_entry(entry, _verify(HEADER + LICENSED_USER + summary("CONOPT")))
    assert (entry["license_edition"], entry["gams_version"], entry["convexity_solver"]) == (
        "licensed",
        "54.2.1",
        "CONOPT",
    )
    vc.update_catalog_entry(entry, _verify(None, raise_=FileNotFoundError()))
    assert not {"license_edition", "gams_version", "convexity_solver"} & set(entry)


def test_migrate_catalog_copies_the_fields_only_when_present() -> None:
    """W7: absent stays absent (not "demo"); the v3.1.0 migration supplies the null."""
    from scripts.gamslib.migrate_catalog import transform_entry

    base = {"model_id": "m", "model_name": "M", "gamslib_type": "NLP"}
    with_prov = {
        **base,
        "convexity_status": "likely_convex",
        "license_edition": "licensed",
        "gams_version": "54.2.1",
        "convexity_solver": "CONOPT",
    }
    conv = transform_entry(with_prov, "2026-10-18T00:00:00Z")["convexity"]
    assert (conv["license_edition"], conv["gams_version"], conv["solver"]) == (
        "licensed",
        "54.2.1",
        "CONOPT",
    )
    bare = transform_entry({**base, "convexity_status": "likely_convex"}, "2026-10-18T00:00:00Z")
    assert not {"license_edition", "gams_version", "solver"} & set(bare["convexity"])

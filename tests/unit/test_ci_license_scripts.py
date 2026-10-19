"""The CI side of the license unlock (Sprint 40 P1, ``CI_LICENSE_DESIGN.md`` §3, §6).

Three scripts, one shared rule: a CI log is PUBLISHED, so nothing from a GAMS
listing's header may reach it. Each test drives a script against a mocked GAMS
that writes a SYNTHETIC listing, and asserts both the behaviour and that the
made-up licensee line never appears in what the script prints or writes.

LICENSE HYGIENE: every listing here is synthetic. Never paste a real header.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import scripts.ci.gams_edition as ge  # noqa: E402
import scripts.ci.run_licensed_solves as rls  # noqa: E402
import scripts.ci.run_pr19_solves as pr19  # noqa: E402

LICENSEE = "USER: Example Licensee                                  G000000:0000AB-GEN"
HEADER = "GAMS 54.2.1  abcdef12 Jul 13, 2026          DEX-DEG x86 64bit/macOS\n"
SOLVED = "**** SOLVER STATUS     1 Normal Completion\n**** MODEL STATUS      1 Optimal\n"
REFUSAL = (
    "**** The model exceeds the demo license limits for nonlinear models of more than 1000 rows\n"
)


def _gams_writing(listing: str):
    """A fake ``subprocess.run`` that writes ``listing`` to the ``o=`` path."""

    def run(cmd, **kw):
        out = next(a[2:] for a in cmd if a.startswith("o="))
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(listing)
        return MagicMock(returncode=0, stdout=LICENSEE, stderr=LICENSEE)

    return run


# ------------------------------------------------- run_pr19_solves: refusal


def test_pr19_reports_a_demo_refusal_as_skipped_not_as_an_emit_failure(tmp_path, capsys) -> None:
    mcp = tmp_path / "data" / "gamslib" / "mcp" / "egypt_mcp.gms"
    mcp.parent.mkdir(parents=True)
    mcp.write_text("* golden\n")
    with patch.object(pr19.subprocess, "run", side_effect=_gams_writing(HEADER + REFUSAL)):
        r = pr19._solve_one("egypt", tmp_path, tmp_path / "scratch", 30)
    assert r["skipped"] == "over the demo ceiling"
    assert r["passed"] is False, "the HARD tier must still fail if a canary outgrows the demo"
    assert "demo ceiling" in r["model_status"]


def test_pr19_leaves_an_ordinary_solve_alone(tmp_path) -> None:
    mcp = tmp_path / "data" / "gamslib" / "mcp" / "trnsport_mcp.gms"
    mcp.parent.mkdir(parents=True)
    mcp.write_text("* golden\n")
    with patch.object(pr19.subprocess, "run", side_effect=_gams_writing(HEADER + SOLVED)):
        r = pr19._solve_one("trnsport", tmp_path, tmp_path / "scratch", 30)
    assert "skipped" not in r
    assert r["passed"] is True


# ----------------------------------------------------- gams_edition: output


@pytest.mark.parametrize(
    "listing, edition, rc",
    [
        (HEADER + LICENSEE + "\n" + SOLVED, "licensed", 0),
        (HEADER + "USER: GAMS Demo, for EULA and demo limitations see\n" + SOLVED, "demo", 0),
        (HEADER + REFUSAL, "demo", 0),
    ],
)
def test_gams_edition_prints_the_verdict_and_never_the_header(listing, edition, rc, capsys) -> None:
    with patch.object(ge.subprocess, "run", side_effect=_gams_writing(listing)):
        assert ge.main(["--gams", "gams"]) == rc
    out = capsys.readouterr().out
    assert f"edition={edition}" in out
    assert "USER:" not in out and "Licensee" not in out, "nothing from the header may print"


def test_gams_edition_require_mismatch_is_rc_1(capsys) -> None:
    with patch.object(ge.subprocess, "run", side_effect=_gams_writing(HEADER + REFUSAL)):
        assert ge.main(["--require", "licensed"]) == 1
    assert "expected edition=licensed, got edition=demo" in capsys.readouterr().out


def test_gams_edition_unclassifiable_is_rc_2(capsys) -> None:
    with patch.object(ge.subprocess, "run", side_effect=FileNotFoundError()):
        assert ge.main([]) == 2
    assert "edition=unknown" in capsys.readouterr().out


# ------------------------------------------------ run_licensed_solves


def test_the_target_list_is_the_eleven_mcp_gated_models_by_identity() -> None:
    """Pinned by identity (a count would pass a swap): the S39-close cohort."""
    ids = rls.read_targets(PROJECT_ROOT / ".github" / "licensed-solve-targets.txt")
    assert set(ids) == {
        "egypt", "ferts", "glider", "robot", "shale", "sroute",
        "srpchase", "tabora", "tfordy", "tricp", "turkey",
    }  # fmt: skip
    assert len(ids) == len(set(ids))
    for mid in ids:
        assert (PROJECT_ROOT / "data" / "gamslib" / "mcp" / f"{mid}_mcp.gms").is_file(), mid


def test_read_targets_rejects_a_path_like_id(tmp_path) -> None:
    f = tmp_path / "t.txt"
    f.write_text("egypt\n../etc/passwd\n")
    with pytest.raises(ValueError):
        rls.read_targets(f)


def _licensed_run(tmp_path, listing: str, capsys) -> tuple[int, str, str]:
    targets = tmp_path / "t.txt"
    targets.write_text("trnsport\n")
    summary = tmp_path / "summary.json"
    with (
        patch.object(rls, "PROJECT_ROOT", tmp_path),
        patch.object(rls.subprocess, "run", side_effect=_gams_writing(listing)),
    ):
        mcp = tmp_path / "data" / "gamslib" / "mcp" / "trnsport_mcp.gms"
        mcp.parent.mkdir(parents=True, exist_ok=True)
        mcp.write_text("* golden\n")
        rc = rls.main(
            ["--targets", str(targets), "--out", str(tmp_path / "out"), "--summary", str(summary)]
        )
    return rc, capsys.readouterr().out, summary.read_text()


def test_licensed_solves_pass_under_the_licensed_edition(tmp_path, capsys) -> None:
    rc, out, summary = _licensed_run(tmp_path, HEADER + LICENSEE + "\n" + SOLVED, capsys)
    assert rc == 0
    assert json.loads(summary)["results"][0]["edition"] == "licensed"
    for text in (out, summary):
        assert "USER:" not in text and "Licensee" not in text


def test_licensed_solves_FAIL_when_the_run_was_the_demo(tmp_path, capsys) -> None:
    """A measurement made on the demo is meaningless: the job must fail, not report it."""
    rc, out, _ = _licensed_run(tmp_path, HEADER + REFUSAL, capsys)
    assert rc == 1
    assert "not run under the licensed edition: trnsport" in out


# ------------------------------------- stale listings (PR #1762 review)


def test_licensed_solves_never_classify_a_stale_listing(tmp_path, capsys) -> None:
    """A reused --out holds the PREVIOUS licensed listing. If GAMS then fails to
    start, the stale file must not be read as this run's result."""
    targets = tmp_path / "t.txt"
    targets.write_text("trnsport\n")
    stale = tmp_path / "out" / "trnsport" / "trnsport_mcp.lst"
    stale.parent.mkdir(parents=True)
    stale.write_text(HEADER + LICENSEE + "\n" + SOLVED)
    mcp = tmp_path / "data" / "gamslib" / "mcp" / "trnsport_mcp.gms"
    mcp.parent.mkdir(parents=True)
    mcp.write_text("* golden\n")
    with (
        patch.object(rls, "PROJECT_ROOT", tmp_path),
        patch.object(rls.subprocess, "run", side_effect=FileNotFoundError()),
    ):
        rc = rls.main(
            [
                "--targets",
                str(targets),
                "--out",
                str(tmp_path / "out"),
                "--summary",
                str(tmp_path / "s.json"),
            ]
        )
    assert rc == 1, "a run that produced no listing is not a licensed run"
    assert json.loads((tmp_path / "s.json").read_text())["results"][0]["edition"] == "unknown"


def test_pr19_never_reads_a_stale_refusal(tmp_path) -> None:
    """Same defect in run_pr19_solves.py: a persisted --scratch-base must not make a
    GAMS that never ran look like a demo refusal."""
    mcp = tmp_path / "data" / "gamslib" / "mcp" / "egypt_mcp.gms"
    mcp.parent.mkdir(parents=True)
    mcp.write_text("* golden\n")
    stale = tmp_path / "scratch" / "egypt" / "egypt_mcp.lst"
    stale.parent.mkdir(parents=True)
    stale.write_text(HEADER + REFUSAL)
    # GAMS RUNS but writes no listing. (A missing executable returns before the
    # listing is read, so it cannot exercise this; the first version of this
    # test used it and stayed green with the fix reverted.)
    with patch.object(pr19.subprocess, "run", return_value=MagicMock(returncode=3)):
        r = pr19._solve_one("egypt", tmp_path, tmp_path / "scratch", 30)
    assert "skipped" not in r, "a stale refusal must not be reported as this run's"
    assert r["model_status"] == "n/a (no lst)"

"""Sprint 39 P7 — `solve_mcp` must carry the attribution VERDICT, not a guess.

⚠ THIS FILE EXISTS BECAUSE THE GATE'S OWN WIRING WAS UNTESTED (PR #1740 review).
`run_full_test.py`'s presolve-retry gate depends entirely on `solve_mcp`
returning `mcp_attribution`, but the end-to-end tests stub the solver and
compute that value themselves — so the parser/filter here could be removed or
miswired and the suite would stay green while every real retry silently
defaulted to unattributed.

⚠ AND ATTRIBUTION IS NOT SUCCESS. An earlier revision gated on
``any(s.model_status is not None)`` — *is the status ours* — which is **True for
an aborted MCP**: GAMS prints ``MODEL STATUS 1`` above the
``**** SOLVE ... ABORTED`` line, so `parse_gams_listing` reports 1/1 and the
retry would have been recorded `model_optimal_presolve`. The verdict folds in
the abort and solver-status checks that a presence test cannot see.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.gamslib import test_solve as ts

#: Our emitted MCP solved, and only ours is present. The cold-emit shape.
OURS_SOLVED = """
               S O L V E      S U M M A R Y

     MODEL   mcp_model           OBJECTIVE  dummy
     TYPE    MCP                 DIRECTION  MINIMIZE
     SOLVER  PATH                FROM LINE  240

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal
**** OBJECTIVE VALUE                0.0000
"""

#: `weapons`: the embedded source solved, our MCP aborted without a summary.
EMBEDDED_ONLY = """
               S O L V E      S U M M A R Y

     MODEL   war                 OBJECTIVE  tetd
     TYPE    NLP                 DIRECTION  MAXIMIZE
     SOLVER  CONOPT              FROM LINE  138

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      2 Locally Optimal
**** OBJECTIVE VALUE             1735.5696

**** SOLVE from line 238 ABORTED, EXECERROR = 1
"""

#: ⚠ OUR model, OUR status — and explicitly ABORTED. The shape a status-presence
#: test cannot distinguish from a real solve.
OURS_ABORTED = """
               S O L V E      S U M M A R Y

     MODEL   mcp_model
     TYPE    MCP
     SOLVER  PATH                FROM LINE  1124

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal

**** SOLVE from line 1124 ABORTED, EXECERROR = 1
"""


@pytest.fixture
def run_with_listing(monkeypatch):
    """Drive the real `solve_mcp` over a supplied listing, without GAMS."""

    def _run(listing: str):
        # `solve_mcp` locates GAMS via `shutil.which` (it has no `find_gams`),
        # so stub that rather than a name the module does not export.
        monkeypatch.setattr(ts.shutil, "which", lambda _n: "/nonexistent/gams")

        def fake_subprocess_run(cmd, *a, **k):
            # `o=<path>` is where solve_mcp told GAMS to write the listing.
            out = next(c.split("=", 1)[1] for c in cmd if str(c).startswith("o="))
            Path(out).write_text(listing)

            class R:
                returncode = 0
                stdout = ""
                stderr = ""

            return R()

        monkeypatch.setattr(ts.subprocess, "run", fake_subprocess_run)
        return ts.solve_mcp(Path("weapons_mcp_presolve.gms"), timeout=5)

    return _run


@pytest.mark.unit
def test_our_own_solved_mcp_is_MCP_SOLVED(run_with_listing):
    result = run_with_listing(OURS_SOLVED)
    assert result["mcp_attribution"] == "MCP-SOLVED"
    assert result["status"] == "success"


@pytest.mark.unit
def test_an_embedded_only_listing_is_not_MCP_SOLVED(run_with_listing):
    """The `weapons` defect, through the real `solve_mcp`.

    ⚠ Note `status` is still "success" and `model_status` is still 2: the global
    scan cannot tell whose status it read. That is precisely why the gate must
    consult the verdict rather than the status.
    """
    result = run_with_listing(EMBEDDED_ONLY)
    assert result["mcp_attribution"] == "EMBEDDED-ONLY"
    assert result["mcp_produced_own_status"] is False
    assert result["status"] == "success", "the scan is fooled — the verdict is not"
    assert result["model_status"] == 2


@pytest.mark.unit
def test_an_ABORTED_mcp_of_ours_is_not_MCP_SOLVED(run_with_listing):
    """⚠ The hole an earlier revision of this gate had.

    Attribution SUCCEEDS here — the status genuinely is ours — so a
    `mcp_produced_own_status` gate passes. But the solve aborted, so there is no
    usable answer, and `run_pipeline` would have recorded
    `model_optimal_presolve` for it.
    """
    result = run_with_listing(OURS_ABORTED)
    assert result["mcp_produced_own_status"] is True, "the status IS ours…"
    assert result["mcp_attribution"] == "MCP-FAILED", "…but the solve aborted"
    # And the distinction is not academic: the naive predicate says "record it".
    assert result["mcp_attribution"] != "MCP-SOLVED"


@pytest.mark.unit
def test_the_verdict_is_computed_HERE_and_not_by_a_caller(run_with_listing):
    """Scope guard: the field must be present on every successful solve.

    The end-to-end gate tests stub the solver and supply this value themselves,
    so without this file nothing checks that production computes it at all.
    """
    for listing in (OURS_SOLVED, EMBEDDED_ONLY, OURS_ABORTED):
        result = run_with_listing(listing)
        assert "mcp_attribution" in result
        assert result["mcp_attribution"] in {
            "MCP-SOLVED",
            "MCP-FAILED",
            "MCP-NO-STATUS",
            "EMBEDDED-ONLY",
            "NO-SOLVE",
            "ERROR",
        }

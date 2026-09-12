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

    def _run(listing: str, model_name: str = "mcp_model"):
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
        # `solve_mcp` reads the emitted model's NAME out of this file.
        monkeypatch.setattr(ts, "_emitted_model_name", lambda _p: model_name)
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
    # ⚠ The RAW SCAN is still fooled — `model_status` is the source's 2 — but
    # `status` is no longer, because the verdict contradicts it (PR #1740
    # review). An earlier revision asserted `status == "success"` here and
    # called it "the scan is fooled, the verdict is not": true of the parse,
    # and it left every consumer of `status` inheriting the false success.
    assert result["model_status"] == 2, "the raw scan still reads the source's status"
    assert result["status"] == "failure", "…but the public result no longer claims success"


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
    # ⚠ The PUBLIC contract too (PR #1740 review): GAMS prints MODEL STATUS 1
    # above the abort line, so the raw scan yields 1/1 and `is_success` was true
    # — every consumer of `status`, including the solve counts and the persisted
    # DB record, would have booked an aborted solve as a success.
    assert result["model_status"] == 1, "the raw scan reads the stale status"
    assert result["status"] == "failure", "…and the public result refuses it"


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


#: The same healthy solve, emitted under a CUSTOM model name via `--model-name`.
OURS_SOLVED_CUSTOM_NAME = OURS_SOLVED.replace("mcp_model", "my_model")


@pytest.mark.unit
def test_a_CUSTOM_emitted_model_name_is_still_ours(run_with_listing):
    """⚠ `mcp_model` is the CLI's DEFAULT, not a guarantee (PR #1740 review).

    `SolveSummary.is_emitted_mcp` compares against the module constant, so
    before the name was threaded through, `nlp2mcp --model-name my_model` made
    every valid MCP summary `EMBEDDED-ONLY` — turning correct results
    inconclusive and, worse, doing it silently.
    """
    result = run_with_listing(OURS_SOLVED_CUSTOM_NAME, model_name="my_model")
    assert result["mcp_attribution"] == "MCP-SOLVED"
    assert result["mcp_completed_own_solve"] is True


@pytest.mark.unit
def test_a_custom_name_does_NOT_swallow_the_raw_source_solve(run_with_listing):
    """The raw source keeps its own identity — only the emitted name is mapped.

    Relabelling must not be a blanket rewrite: `weapons`' embedded `war` solve
    has to stay distinguishable, or the fix would recreate the very confusion it
    removes.
    """
    listing = EMBEDDED_ONLY.replace("mcp_model", "my_model")
    result = run_with_listing(listing, model_name="my_model")
    assert result["mcp_attribution"] == "EMBEDDED-ONLY"


@pytest.mark.unit
def test_a_COMPLETED_infeasible_mcp_is_failed_but_COMPLETED(run_with_listing):
    """⚠ The distinction the convexity infeasible path depends on.

    A normally-completed MCP reporting model status 4 is `MCP-FAILED` — the
    verdict reserves `MCP-SOLVED` for a usable answer — but it DID run and
    report that status itself, unlike an abort.
    """
    infeasible = OURS_SOLVED.replace(
        "**** MODEL STATUS      1 Optimal", "**** MODEL STATUS      4 Infeasible"
    )
    result = run_with_listing(infeasible)
    assert result["mcp_attribution"] == "MCP-FAILED"
    assert result["mcp_completed_own_solve"] is True, "it completed; it just failed"

    aborted = run_with_listing(OURS_ABORTED)
    assert aborted["mcp_attribution"] == "MCP-FAILED", "same verdict…"
    assert aborted["mcp_completed_own_solve"] is False, "…different meaning"


@pytest.mark.unit
def test_the_emitted_name_parser_reads_a_REAL_file(tmp_path):
    """⚠ The custom-name tests above STUB `_emitted_model_name` (PR #1740 review).

    That makes them tests of the relabelling, not of the parsing — they would
    pass even if `_SOLVE_MCP_STMT` could not read a `Solve ... using MCP;`
    statement at all. This exercises the helper against real file content.
    """
    f = tmp_path / "x_mcp.gms"
    f.write_text(
        "Variables x;\nEquations e;\n\nModel my_model / all /;\nSolve my_model using MCP;\n"
    )
    assert ts._emitted_model_name(f) == "my_model"

    # Case is preserved as written — the relabelling is what normalises it.
    f.write_text("Solve MCP_MODEL using MCP;\n")
    assert ts._emitted_model_name(f) == "MCP_MODEL"

    # Real emitted goldens parse.
    golden = Path("data/gamslib/mcp/aircraft_mcp.gms")
    if golden.exists():
        assert ts._emitted_model_name(golden) == "mcp_model"

    # Unreadable or unmatched leaves the constant in force (previous behaviour).
    assert ts._emitted_model_name(tmp_path / "absent.gms") is None
    f.write_text("* no solve statement here\n")
    assert ts._emitted_model_name(f) is None


@pytest.mark.unit
def test_a_CASE_ONLY_model_name_override_is_still_ours(run_with_listing):
    """⚠ The guard must be at least as strict as the consumer it protects.

    `--model-name MCP_MODEL` differs from `mcp_model` only in case. An earlier
    revision skipped relabelling when the names matched case-INSENSITIVELY,
    while `is_emitted_mcp` compares case-SENSITIVELY — so the summary kept
    `MCP_MODEL`, failed `== "mcp_model"`, and a healthy solve was reported
    EMBEDDED-ONLY.
    """
    listing = OURS_SOLVED.replace("mcp_model", "MCP_MODEL")
    result = run_with_listing(listing, model_name="MCP_MODEL")
    assert result["mcp_attribution"] == "MCP-SOLVED"


@pytest.mark.unit
def test_an_INDETERMINATE_verdict_does_NOT_flip_success(run_with_listing):
    """⚠⚠ The safety property behind gating on positive contradiction only.

    `NO-SOLVE` / `MCP-NO-STATUS` / `ERROR` mean *nothing could be attributed* —
    and that is also where a summary the parser failed to recognise would land.
    Treating them as contradictions would turn a parsing change into a
    corpus-wide flip of genuine successes to failures, which is why the gate
    lists `EMBEDDED-ONLY` and `MCP-FAILED` explicitly rather than testing
    `!= "MCP-SOLVED"`.

    ⚠ The fixture must reach the ATTRIBUTION layer to test it. A first draft
    used a listing with no `S O L V E   S U M M A R Y` header at all, which
    `parse_gams_listing` rejects outright — so it failed for a parse reason and
    proved nothing about the verdict. This one has a valid summary that our
    parser attributes to `mcp_model` but which carries NO status lines, with the
    statuses stranded above it: global scan reads 1/1, attribution reads
    nothing.
    """
    unattributable = """
**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal
**** OBJECTIVE VALUE                0.0000

               S O L V E      S U M M A R Y

     MODEL   mcp_model
     TYPE    MCP
     SOLVER  PATH                FROM LINE  240
"""
    result = run_with_listing(unattributable)
    assert result["mcp_attribution"] in {"NO-SOLVE", "MCP-NO-STATUS"}
    assert result["status"] == "success", (
        "an unattributable listing must not be downgraded — otherwise a parser "
        "gap silently fails the whole corpus"
    )


@pytest.mark.unit
def test_a_rejected_row_does_not_keep_a_SUCCESS_category(run_with_listing):
    """⚠ A failure row must not assert an optimal outcome (PR #1740 review).

    `categorize_solve_outcome` derives from the same borrowed/stale scalars as
    `status`, so refusing the status alone left `outcome_category:
    "model_optimal"` on a `status: "failure"` row — which `run_solve_stage`
    copies into `error.category`. That is schema-VALID (both are members of
    `error_category`) and still a contradiction: no such row exists anywhere in
    the corpus.

    ⚠⚠ `path_solve_terminated` is a KPI Sprint 39 requires to stay at 0. This
    mapping is inert today — no corpus row is attribution-rejected — so the
    figure does not move. If it ever fires it is a model genuinely aborting that
    was previously recorded optimal: a correction, not a regression.
    """
    for listing in (EMBEDDED_ONLY, OURS_ABORTED):
        result = run_with_listing(listing)
        assert result["status"] == "failure"
        assert result["outcome_category"] == "path_solve_terminated", result["outcome_category"]

    # The negative control: a genuine solve keeps its real category.
    ok = run_with_listing(OURS_SOLVED)
    assert ok["status"] == "success"
    assert ok["outcome_category"] != "path_solve_terminated"


@pytest.mark.unit
def test_an_indeterminate_row_keeps_its_category(run_with_listing):
    """The safety property again: no verdict, no re-categorisation."""
    unattributable = """
**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal

               S O L V E      S U M M A R Y

     MODEL   mcp_model
     TYPE    MCP
     SOLVER  PATH                FROM LINE  240
"""
    result = run_with_listing(unattributable)
    assert result["status"] == "success"
    assert result["outcome_category"] != "path_solve_terminated"

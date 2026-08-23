"""A `MODEL STATUS` belongs to the solve above it, not to the listing.

Sprint 38 Day 10. A ``--nlp-presolve`` emit runs the original model inside the
generated file before solving the MCP, so its listing contains **two or more**
solve summaries. If the MCP solve aborts, the listing still holds the embedded
NLP's ``MODEL STATUS`` — and anything that searches the listing globally will
report that status as the MCP's.

`weapons` is the real instance: its listing has exactly ONE summary (the NLP's,
MS-2 @ 1735.5696), the MCP aborted with ``EXECERROR = 1``, and the DB recorded
``model_optimal_presolve`` + match at 1735.5696.

**The fixtures below are verbatim excerpts of real GAMS 54.2.1 listings**, not
hand-written approximations of what a listing looks like. A parser test built
from an idealised fixture proves only that the parser matches the author's
mental model of the format.
"""

import pytest

from scripts.sprint_audit.check_mcp_solve_attribution import (
    Attribution,
    parse_solve_summaries,
)

#: Verbatim from `weapons`'s listing — the ONLY solve summary it contains,
#: followed by the MCP abort that produced no summary of its own.
_WEAPONS = """
               S O L V E      S U M M A R Y

     MODEL   war                 OBJECTIVE  tetd
     TYPE    NLP                 DIRECTION  MAXIMIZE
     SOLVER  CONOPT              FROM LINE  138

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      2 Locally Optimal
**** OBJECTIVE VALUE             1735.5696

 RESOURCE USAGE, LIMIT          0.071       300.000
 ITERATION COUNT, LIMIT        11    2147483647

**** MCP pair comp_minw.lam_minw has unmatched equation
**** SOLVE from line 238 ABORTED, EXECERROR = 1
**** USER ERROR(S) ENCOUNTERED
"""

#: Verbatim from `twocge`'s listing — the raw model solves twice, then the MCP.
_TWOCGE = """
               S O L V E      S U M M A R Y

     MODEL   twocge              OBJECTIVE  SW
     TYPE    NLP                 DIRECTION  MAXIMIZE
     SOLVER  CONOPT              FROM LINE  634

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      2 Locally Optimal
**** OBJECTIVE VALUE               55.5085


               S O L V E      S U M M A R Y

     MODEL   twocge              OBJECTIVE  SW
     TYPE    NLP                 DIRECTION  MAXIMIZE
     SOLVER  CONOPT              FROM LINE  641

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      2 Locally Optimal
**** OBJECTIVE VALUE               56.7778


               S O L V E      S U M M A R Y

     MODEL   mcp_model
     TYPE    MCP
     SOLVER  PATH                FROM LINE  1124

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal
"""


@pytest.mark.unit
def test_weapons_listing_is_NLP_ONLY_despite_holding_a_model_status():
    """The discriminating case: a status is present, but not the MCP's.

    Any check that greps the listing for ``MODEL STATUS`` calls this MCP-SOLVED.
    """
    summaries = parse_solve_summaries(_WEAPONS)
    attribution = Attribution("weapons", summaries=summaries)

    assert len(summaries) == 1, f"weapons has exactly one solve summary, got {summaries}"
    assert summaries[0].type == "NLP"
    assert summaries[0].model_status == 2, "the status present is the embedded NLP's"

    assert attribution.mcp_summaries == [], "there is no MCP-typed solve at all"
    assert not attribution.mcp_produced_status
    assert attribution.verdict == "NLP-ONLY"


@pytest.mark.unit
def test_twocge_listing_attributes_the_MCP_status_to_the_MCP():
    """Three solves; only the third is ours, and only its status counts."""
    summaries = parse_solve_summaries(_TWOCGE)
    attribution = Attribution("twocge", summaries=summaries)

    assert [s.type for s in summaries] == ["NLP", "NLP", "MCP"]
    assert [s.model for s in summaries] == ["twocge", "twocge", "mcp_model"]

    (mcp,) = attribution.mcp_summaries
    assert mcp.solver == "PATH"
    assert mcp.model_status == 1
    assert attribution.verdict == "MCP-SOLVED"


@pytest.mark.unit
def test_the_LAST_status_in_a_listing_is_not_the_MCPs():
    """Pin the defect this exists to catch, on both fixtures at once.

    `parse_gams_listing` takes the last ``MODEL STATUS`` in the file. On twocge
    that happens to be right; on weapons it silently yields the NLP's MS-2. The
    two fixtures therefore disagree about whether "last" is a safe rule — which
    is precisely why attribution has to be positional.
    """
    weapons_last = parse_solve_summaries(_WEAPONS)[-1]
    twocge_last = parse_solve_summaries(_TWOCGE)[-1]

    assert twocge_last.is_mcp, "on twocge the last solve IS the MCP — the rule looks fine"
    assert not weapons_last.is_mcp, (
        "on weapons the last solve is the embedded NLP, so 'take the last MODEL "
        "STATUS' reports an NLP status as the MCP's"
    )


@pytest.mark.unit
def test_a_summary_without_a_status_does_not_count_as_solved():
    """An MCP summary that reported no status must not read as MCP-SOLVED.

    GAMS emits the header during model generation; a solver that dies before
    reporting leaves the block statusless.
    """
    truncated = """
               S O L V E      S U M M A R Y

     MODEL   mcp_model
     TYPE    MCP
     SOLVER  PATH                FROM LINE  1124

"""
    attribution = Attribution("truncated", summaries=parse_solve_summaries(truncated))

    assert len(attribution.mcp_summaries) == 1, "the MCP block is present..."
    assert attribution.mcp_summaries[0].model_status is None, "...but reported no status"
    assert not attribution.mcp_produced_status
    assert attribution.verdict == "NLP-ONLY"


@pytest.mark.unit
def test_a_raw_models_OWN_mcp_solve_is_not_ours():
    """`TYPE MCP` alone is not enough — two raw sources solve an MCP themselves.

    `cesam.gms` and `spatequ.gms` contain their own `using MCP` solve, and a
    presolve emit `$include`s the raw source. Reading that summary as ours would
    reinstate the very bug this script exists to catch, one level up.
    """
    foreign = """
               S O L V E      S U M M A R Y

     MODEL   spatequ             OBJECTIVE
     TYPE    MCP
     SOLVER  PATH                FROM LINE  95

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal
"""
    attribution = Attribution("spatequ-like", summaries=parse_solve_summaries(foreign))

    (summary,) = attribution.summaries
    assert summary.is_mcp, "it IS an MCP solve..."
    assert not summary.is_emitted_mcp, "...but it is the raw model's, not ours"

    assert attribution.mcp_summaries == [], "so it must not count toward our MCP"
    assert len(attribution.foreign_mcp_summaries) == 1, "and it must be surfaced, not dropped"
    assert not attribution.mcp_produced_status
    assert attribution.verdict == "NLP-ONLY"


@pytest.mark.unit
def test_empty_listing_is_NO_SOLVE_not_NLP_ONLY():
    """No solve at all is a distinct outcome from 'the NLP solved, the MCP did not'."""
    attribution = Attribution("empty", summaries=parse_solve_summaries("no solves here"))

    assert attribution.summaries == []
    assert attribution.verdict == "NO-SOLVE"

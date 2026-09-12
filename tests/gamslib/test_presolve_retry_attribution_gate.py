"""Sprint 39 P7 / Remedy A — a retry may be recorded only if the status is OURS.

The defect (`weapons`, Sprint 38 Day 9): ``parse_gams_listing`` takes the LAST
match of each pattern across the WHOLE listing, with no notion of which model
produced it. A ``--nlp-presolve`` listing holds the embedded source solve *and*
our MCP solve, so when our MCP aborts before reporting, the source's
``MODEL STATUS`` is read back as ours. The row then records
``model_optimal_presolve`` + match for a solve that never happened — and because
the warm start already put the NLP's answer in the variables, the objective
"matches" itself.

⚠ **The gate is on the BRANCH, not on one write.** ``run_full_test.py``'s retry
branch makes three writes (``presolve_required``, ``mcp_file_used`` /
``mcp_file_generated``, ``outcome_category``); gating a single one would leave
the others asserting a presolve success.

⚠ **Not keyed on ``EXECERROR``**, which conflates MCP-side and NLP-side aborts —
the mistake that first reported `weapons` against the wrong half of its listing.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from scripts.gamslib.run_full_test import run_pipeline

#: Verbatim from `weapons`'s listing: the ONLY solve summary it contains is the
#: embedded NLP's, followed by the MCP abort that produced no summary at all.
#: Note the abort is reported at line 238 while the summary is FROM LINE 138 —
#: attribution must be positional, not by proximity.
WEAPONS_SHAPED = """
               S O L V E      S U M M A R Y

     MODEL   war                 OBJECTIVE  tetd
     TYPE    NLP                 DIRECTION  MAXIMIZE
     SOLVER  CONOPT              FROM LINE  138

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      2 Locally Optimal
**** OBJECTIVE VALUE             1735.5696

 RESOURCE USAGE, LIMIT          0.071       300.000
 ITERATION COUNT, LIMIT        11    2147483647

**** SOLVE from line 238 ABORTED, EXECERROR = 1
**** USER ERROR(S) ENCOUNTERED
"""

#: The negative control: the same listing PLUS our MCP reporting its own status.
#: Without this, a gate that rejects everything would pass every other test here.
#:
#: ⚠ `FROM LINE 240`, NOT 238. The base listing ends with
#: `**** SOLVE from line 238 ABORTED`, and attribution is by FROM LINE — so an
#: MCP summary claiming line 238 IS the aborted solve. The first draft used 238
#: and the strengthened gate correctly refused it, which is the fixture being
#: wrong rather than the gate (PR #1740 review). A negative control has to be a
#: genuinely healthy listing or it proves nothing.
WEAPONS_SHAPED_PLUS_OUR_MCP = WEAPONS_SHAPED + """
               S O L V E      S U M M A R Y

     MODEL   mcp_model           OBJECTIVE  dummy
     TYPE    MCP                 DIRECTION  MINIMIZE
     SOLVER  PATH                FROM LINE  240

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal
**** OBJECTIVE VALUE                0.0000
"""


#: ⚠ OUR model, OUR status — and explicitly ABORTED. GAMS prints MODEL STATUS 1
#: above the abort line, so `parse_gams_listing` reports 1/1 and a
#: status-presence gate waves it through (PR #1740 review).
OURS_ABORTED = """
               S O L V E      S U M M A R Y

     MODEL   mcp_model
     TYPE    MCP
     SOLVER  PATH                FROM LINE  1124

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal

**** SOLVE from line 1124 ABORTED, EXECERROR = 1
"""


#: ⚠ An INDETERMINATE listing: statuses parse (1/1) but belong to no summary our
#: parser attributes, so the verdict is `MCP-NO-STATUS`/`NO-SOLVE`. This is the
#: only shape that still reaches the rejection arm with `status == "success"`,
#: because a contradicting verdict now downgrades the status itself.
UNATTRIBUTABLE = """
**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal
**** OBJECTIVE VALUE             1735.5696

               S O L V E      S U M M A R Y

     MODEL   mcp_model
     TYPE    MCP
     SOLVER  PATH                FROM LINE  240
"""


# --------------------------------------------------------------- the primitive


@pytest.mark.unit
def test_the_raw_listing_scan_IS_fooled_but_attribution_is_not():
    """Fail-before, at the defect itself rather than at the guard.

    ``parse_gams_listing`` reports MODEL STATUS 2 for a listing in which OUR
    model reported nothing. Asserting that first is what stops the guard from
    later being read as redundant.
    """
    from scripts.gamslib.test_solve import parse_gams_listing
    from scripts.sprint_audit.check_mcp_solve_attribution import parse_solve_summaries

    parsed = parse_gams_listing(WEAPONS_SHAPED)
    assert parsed["model_status"] == 2, "the global scan reads the source's status"
    assert parsed["objective_value"] == pytest.approx(1735.5696)

    ours = [s for s in parse_solve_summaries(WEAPONS_SHAPED) if s.is_emitted_mcp]
    assert ours == [], "…while no summary in that listing belongs to mcp_model"


@pytest.mark.unit
def test_attribution_is_true_only_when_our_model_reported():
    from scripts.sprint_audit.check_mcp_solve_attribution import parse_solve_summaries

    def attributed(lst: str) -> bool:
        return any(
            s.model_status is not None for s in parse_solve_summaries(lst) if s.is_emitted_mcp
        )

    assert attributed(WEAPONS_SHAPED) is False
    assert attributed(WEAPONS_SHAPED_PLUS_OUR_MCP) is True


# ------------------------------------------------------- the record-writing path


def _args(**over):
    base = {
        "only_parse": False,
        "only_translate": False,
        "only_solve": False,
        "only_compare": False,
        "verbose": False,
        "no_presolve_retry": False,
        "skip_convexity": True,
    }
    base.update(over)
    return argparse.Namespace(**base)


def _stats():
    """The REAL initialiser, not a hand-listed subset.

    A local dict drifts: the first draft of this file omitted
    ``compare_skipped`` and three tests died on a ``KeyError`` that had nothing
    to do with the property under test. Worse, a hand-listed dict would silently
    stop covering any counter added later.
    """
    from scripts.gamslib.run_full_test import _new_stats

    return _new_stats(total=1)


def _drive(monkeypatch, tmp_path, retry_listing: str):
    """Run the retry branch with a cold spurious-KKT solve and a given retry listing.

    Returns (model, stats). The cold solve reports MS-1 at an objective that
    mismatches the NLP reference, which is what triggers the retry — `weapons`'
    own shape.
    """
    import scripts.gamslib.run_full_test as rft
    from scripts.gamslib.test_solve import parse_gams_listing
    from scripts.sprint_audit.check_mcp_solve_attribution import (
        Attribution,
        parse_solve_summaries,
    )

    # ⚠ PROJECT_ROOT is redirected so this runs WITHOUT `data/gamslib/raw/`.
    # `run_pipeline` returns at :816 when the raw source is missing, and CI does
    # not ship `raw/` — so the first version of this file passed locally and
    # failed in CI with `KeyError: 'mcp_solve'`, the solve stage never reached.
    #
    # The repo convention for raw-dependent tests is `pytest.skip()`, and that
    # is the WRONG answer here: these three are the gate's only end-to-end
    # coverage, and skipping them in CI means the regression they exist to catch
    # would land unchallenged. Nothing in them needs the real `weapons` source —
    # translate and solve are both stubbed — so the fixture supplies a stand-in
    # instead of opting out.
    root = tmp_path / "root"
    (root / "data" / "gamslib" / "raw").mkdir(parents=True)
    (root / "data" / "gamslib" / "mcp").mkdir(parents=True)
    (root / "data" / "gamslib" / "raw" / "weapons.gms").write_text("* stand-in source\n")
    monkeypatch.setattr(rft, "PROJECT_ROOT", root)

    mcp = root / "data" / "gamslib" / "mcp" / "weapons_mcp.gms"
    mcp.write_text("* cold emit\n")

    calls = {"n": 0}

    def fake_solve(path: Path, timeout: int = 120):
        calls["n"] += 1
        if calls["n"] == 1:  # cold: succeeds at the WRONG objective
            return {
                "status": "success",
                "solver_status": 1,
                "model_status": 1,
                "objective_value": 1700.397,
                "outcome_category": "model_optimal",
                "solve_time_seconds": 0.1,
                "iterations": 1,
                "mcp_attribution": "MCP-SOLVED",
            }
        parsed = parse_gams_listing(retry_listing)  # the real parser
        _verdict = Attribution(
            model_id="weapons", summaries=parse_solve_summaries(retry_listing)
        ).verdict
        # ⚠ Mirror production's `is_success`, which now refuses to claim success
        # when the verdict contradicts it. Leaving this hardcoded "success" made
        # the fake diverge from `solve_mcp` and the tests exercise a path that no
        # longer exists (PR #1740 review).
        _status = (
            "success"
            if (
                parsed["solver_status"] == 1
                and parsed["model_status"] in (1, 2)
                and _verdict not in ("EMBEDDED-ONLY", "MCP-FAILED")
            )
            else "failure"
        )
        return {
            "status": _status,
            "solver_status": parsed["solver_status"],
            "model_status": parsed["model_status"],
            "objective_value": parsed["objective_value"],
            "outcome_category": "model_optimal",
            "solve_time_seconds": 0.1,
            "iterations": 1,
            # ⚠ PRODUCTION semantics, not a local re-derivation. An earlier
            # version computed `any(s.model_status is not None)` here, which
            # (a) duplicated logic the gate no longer uses and (b) could not have
            # caught the aborted-MCP hole, because that predicate is True for an
            # aborted solve (PR #1740 review).
            "mcp_attribution": _verdict,
        }

    monkeypatch.setattr(rft, "get_solve_function", lambda: fake_solve)
    monkeypatch.setattr(
        rft,
        "get_translate_function",
        lambda: (lambda src, out, nlp_presolve=False: {"status": "success"}),
    )
    monkeypatch.setattr(rft, "get_compare_function", lambda: (lambda *a, **k: {}))
    monkeypatch.setattr(rft, "_run_convexity_check", lambda *a, **k: None)

    # ⚠ The retry trigger reads `model["convexity"]`, NOT `nlp_solve` — the
    # reference objective for the spurious-KKT test comes from the convexity
    # probe (`_cold_objective_mismatches_nlp`, run_full_test.py:146-150). A
    # first draft here put it under `nlp_solve` and the retry silently never
    # fired, so both record-path tests passed vacuously against a branch that
    # was never entered.
    model = {
        "model_id": "weapons",
        "convexity": {
            "solver_status": 1,
            "model_status": 2,
            "objective_value": 1735.5696,  # the NLP reference
        },
        "nlp2mcp_translate": {"status": "success", "output_file": str(mcp)},
    }
    stats = _stats()
    run_pipeline(model, {"models": [model]}, _args(only_solve=True), stats)
    return model, stats


@pytest.mark.unit
def test_an_unattributed_retry_is_NOT_recorded_as_a_presolve_match(monkeypatch, tmp_path):
    """§7 assertion 2 — the property the whole remedy exists to enforce."""
    model, stats = _drive(monkeypatch, tmp_path, WEAPONS_SHAPED)

    solve = model["mcp_solve"]
    assert solve["outcome_category"] != "model_optimal_presolve"
    assert solve.get("presolve_required") is not True
    # The COLD record is what survives — the remedy invents no category.
    assert solve["outcome_category"] == "model_optimal"
    assert solve["objective_value"] == pytest.approx(1700.397)
    assert stats["presolve_retry_rejected"] == 1
    assert stats["presolve_retry_success"] == 0


@pytest.mark.unit
def test_an_ATTRIBUTED_retry_is_still_recorded_normally(monkeypatch, tmp_path):
    """§7 assertion 3, the negative control.

    Without this, a gate that rejected every retry would pass the test above.
    """
    model, stats = _drive(monkeypatch, tmp_path, WEAPONS_SHAPED_PLUS_OUR_MCP)

    assert model["mcp_solve"]["outcome_category"] == "model_optimal_presolve"
    assert model["mcp_solve"]["presolve_required"] is True
    assert stats["presolve_retry_success"] == 1
    assert stats["presolve_retry_rejected"] == 0


@pytest.mark.unit
def test_the_unattributed_path_undoes_the_RIGHT_counter(monkeypatch, tmp_path):
    """⚠ The two ways into the restore branch need different bookkeeping.

    A failed retry increments ``solve_failure`` and pushes an error; a retry that
    reports success incremented ``solve_success`` and pushed nothing. Undoing the
    failure path for the second would double-count and — worse — pop the COLD
    error off ``solve_errors``.

    ⚠ USES THE INDETERMINATE FIXTURE, NOT ``WEAPONS_SHAPED`` (PR #1740 review).
    Once `solve_mcp` began downgrading a CONTRADICTED status to ``failure``,
    `WEAPONS_SHAPED` started arriving at the *failure* rollback — so this test
    silently stopped exercising the ``solve_success`` branch it names, while
    still passing. An indeterminate verdict is now the only way to reach the
    rejection arm with a successful scalar status.
    """
    _, stats = _drive(monkeypatch, tmp_path, UNATTRIBUTABLE)

    # cold success (+1) then the retry's success undone (-1) == one net success
    assert stats["solve_success"] == 1
    assert stats["solve_failure"] == 0
    assert stats["solve_errors"] == [], "no cold error existed to pop"


@pytest.mark.unit
def test_an_ABORTED_retry_of_OUR_OWN_model_is_NOT_recorded(monkeypatch, tmp_path):
    """⚠ The hole an earlier revision of this gate had (PR #1740 review).

    Attribution SUCCEEDS here — the status genuinely is ours — so the original
    `mcp_produced_own_status` predicate was True, `parse_gams_listing` returned
    1/1, and the retry would have been recorded `model_optimal_presolve` for a
    solve GAMS reported ABORTED.

    A different door into the same defect as `weapons`: there the status
    belonged to someone else; here it belongs to us and still means nothing.
    """
    model, stats = _drive(monkeypatch, tmp_path, OURS_ABORTED)

    assert model["mcp_solve"]["outcome_category"] != "model_optimal_presolve"
    assert model["mcp_solve"]["outcome_category"] == "model_optimal"
    assert stats["presolve_retry_success"] == 0
    assert stats["presolve_retry_rejected"] == 1


# ------------------------------------------------------------- the run summary


@pytest.mark.unit
def test_the_summary_REPORTS_rejected_retries(capsys):
    """⚠ The human-facing formatter must not contradict the JSON (PR #1740 review).

    `generate_summary` reports `rejected`, but `print_summary` printed only
    `success/attempted recovered from STATUS 5` — so a run whose retry the
    attribution gate refused showed **"0/1 recovered"**, hiding the finding
    entirely. A gate whose result is invisible in the output people actually
    read is a gate nobody will act on.

    ⚠ And "STATUS 5" named one of TWO triggers. The retry also fires on a
    spurious-KKT objective mismatch, which is `weapons`' case — so the one run
    that exercises the gate was also the one the wording described wrongly.
    """
    from scripts.gamslib.run_full_test import print_summary

    stats = _stats()
    # ⚠ `solve_success`/`solve_failure` must be non-zero: `generate_summary`
    # gates the whole solve block on `solve_total > 0`, so a fixture with only
    # retry counters renders nothing and the assertions below would pass or fail
    # for the wrong reason.
    stats.update(
        processed=1,
        solve_success=1,
        presolve_retry_attempted=1,
        presolve_retry_success=0,
        presolve_retry_rejected=1,
    )
    print_summary(stats, _args())
    out = capsys.readouterr().out

    assert "REJECTED" in out, out
    assert "0/1 recovered" in out
    assert "STATUS 5" not in out, "the trigger is not always STATUS 5"


@pytest.mark.unit
def test_the_summary_distinguishes_rejected_from_FAILED(capsys):
    """`attempted - success - rejected` is a genuine failure, and reads as one."""
    from scripts.gamslib.run_full_test import print_summary

    stats = _stats()
    stats.update(
        processed=3,
        solve_success=2,
        solve_failure=1,
        presolve_retry_attempted=3,
        presolve_retry_success=1,
        presolve_retry_rejected=1,
    )
    print_summary(stats, _args())
    out = capsys.readouterr().out
    assert "1/3 recovered" in out
    assert "1 REJECTED (no usable answer from our MCP)" in out
    assert "1 failed" in out

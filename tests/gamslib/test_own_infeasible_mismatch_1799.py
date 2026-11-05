"""Sprint 40 P9a (#1799): an MCP that PROVES infeasibility against an optimal NLP
is reported as ``mismatch``, not ``not_tested``.

Two sites must agree, and both read ``test_solve.is_completed_own_infeasible``:

* ``compare_solutions``' Case-6 exemption (no longer scoped to ``nlp_infeasible``);
* ``run_full_test.py``'s post-solve cascade, which otherwise marks the row
  ``not_tested`` before the compare stage runs. **This is the load-bearing
  site**: widening Case 6 alone leaves the DB byte-identical (``ISSUE_1799``).
"""

from __future__ import annotations

import argparse

import pytest

import scripts.gamslib.run_full_test as rft
from scripts.gamslib.test_solve import compare_solutions, is_completed_own_infeasible

pytestmark = pytest.mark.unit

_OWN_INFEASIBLE = {
    "status": "failure",
    "solver_status": 1,
    "model_status": 5,
    "objective_value": 113.772,
    "outcome_category": "model_infeasible",
    "mcp_attribution": "MCP-FAILED",
    "mcp_completed_own_solve": True,
}


def _model(nlp_model_status: int = 1, **mcp) -> dict:
    return {
        "model_id": "m",
        "convexity": {
            "status": "verified_convex",
            "solver_status": 1,
            "model_status": nlp_model_status,
            "objective_value": 102.0362 if nlp_model_status in (1, 2) else None,
        },
        "mcp_solve": {**_OWN_INFEASIBLE, **mcp},
    }


# ------------------------------------------------------------- the predicate


def test_the_predicate_admits_exactly_a_COMPLETED_OWN_infeasible_solve():
    assert is_completed_own_infeasible(dict(_OWN_INFEASIBLE))
    for ms in (4, 5, 6, 19):
        assert is_completed_own_infeasible({**_OWN_INFEASIBLE, "model_status": ms})


@pytest.mark.parametrize(
    "override",
    [
        {"model_status": 13},  # an error status, not infeasibility
        {"model_status": 1, "status": "success"},  # solved: not this predicate's case
        {"solver_status": 3},  # the solver did not complete normally
        {"mcp_attribution": "EMBEDDED-ONLY"},  # not our model's answer
        {"mcp_completed_own_solve": False},  # ours, but never finished
    ],
    ids=["error_status", "optimal", "abnormal_solver", "not_ours", "uncompleted"],
)
def test_the_predicate_refuses_everything_else(override):
    assert not is_completed_own_infeasible({**_OWN_INFEASIBLE, **override})


def test_the_predicate_refuses_a_missing_row():
    assert not is_completed_own_infeasible(None)
    assert not is_completed_own_infeasible({})


# ----------------------------------------------------------- site 1: Case 6


def test_an_OPTIMAL_NLP_against_our_proved_infeasible_MCP_is_a_MISMATCH():
    out = compare_solutions(_model(nlp_model_status=1))
    assert (out["comparison_status"], out["comparison_result"]) == (
        "mismatch",
        "compare_status_mismatch",
    )


def test_an_INFEASIBLE_NLP_against_it_is_still_a_MATCH():
    """Case 3 is unchanged by the widening."""
    assert compare_solutions(_model(nlp_model_status=5))["comparison_status"] == "match"


def test_a_failed_row_that_is_NOT_our_answer_is_still_SKIPPED():
    out = compare_solutions(_model(mcp_attribution="EMBEDDED-ONLY"))
    assert out["comparison_status"] == "skipped"
    out = compare_solutions(_model(model_status=13))
    assert out["comparison_status"] == "skipped"


# ------------------------------------------------- site 2: the pipeline cascade


def _drive(monkeypatch, tmp_path, solve_result: dict) -> dict:
    """``run_pipeline`` with a stubbed solve and the REAL compare function."""
    root = tmp_path / "root"
    (root / "data" / "gamslib" / "raw").mkdir(parents=True)
    (root / "data" / "gamslib" / "mcp").mkdir(parents=True)
    (root / "data" / "gamslib" / "raw" / "m.gms").write_text("* stand-in source\n")
    mcp = root / "data" / "gamslib" / "mcp" / "m_mcp.gms"
    mcp.write_text("* emit\n")
    monkeypatch.setattr(rft, "PROJECT_ROOT", root)
    monkeypatch.setattr(rft, "get_solve_function", lambda: (lambda *a, **k: dict(solve_result)))
    monkeypatch.setattr(rft, "_run_convexity_check", lambda *a, **k: None)

    model = {
        "model_id": "m",
        "convexity": {
            "status": "verified_convex",
            "solver_status": 1,
            "model_status": 1,
            "objective_value": 102.0362,
        },
        "nlp2mcp_translate": {"status": "success", "output_file": str(mcp)},
    }
    args = argparse.Namespace(
        only_parse=False,
        only_translate=False,
        only_solve=True,
        only_compare=False,
        verbose=False,
        no_presolve_retry=True,
        skip_convexity=True,
    )
    rft.run_pipeline(model, {"models": [model]}, args, rft._new_stats(total=1))
    return model


def test_the_pipeline_lets_a_COMPLETED_OWN_infeasible_solve_reach_COMPARE(monkeypatch, tmp_path):
    model = _drive(monkeypatch, tmp_path, {**_OWN_INFEASIBLE, "solve_time_seconds": 0.1})
    assert model["solution_comparison"]["comparison_status"] == "mismatch"
    assert model["solution_comparison"]["comparison_result"] == "compare_status_mismatch"


@pytest.mark.parametrize(
    "override",
    [{"mcp_attribution": "EMBEDDED-ONLY"}, {"model_status": 13}, {"solver_status": 3}],
    ids=["not_ours", "error_status", "abnormal_solver"],
)
def test_every_OTHER_failed_solve_still_cascades_to_NOT_TESTED(monkeypatch, tmp_path, override):
    model = _drive(
        monkeypatch, tmp_path, {**_OWN_INFEASIBLE, "solve_time_seconds": 0.1, **override}
    )
    assert model["solution_comparison"]["comparison_status"] == "not_tested"

"""Unit tests for the Priority-8 ``--resolve-changed`` checkpoint re-solve helpers.

Covers the pure logic (path→id mapping, bucket extraction, severity ordering,
and the GO/NO-GO move classifier) — the load-bearing pieces of the checkpoint
that catch the #1462-class regression (byte-stable golden, broken solve).
"""

from __future__ import annotations

from scripts.gamslib.run_full_test import (
    _bucket_severity,
    _checkpoint_verdict,
    _classify_bucket_move,
    _extract_bucket,
    _model_id_from_golden_path,
)


class TestModelIdFromGoldenPath:
    def test_cold_golden(self):
        assert _model_id_from_golden_path("data/gamslib/mcp/maxmin_mcp.gms") == "maxmin"

    def test_presolve_golden_prefers_longer_suffix(self):
        # Must strip `_mcp_presolve.gms`, not leave a spurious `_presolve`.
        assert _model_id_from_golden_path("data/gamslib/mcp/rocket_mcp_presolve.gms") == "rocket"

    def test_bare_filename(self):
        assert _model_id_from_golden_path("cclinpts_mcp.gms") == "cclinpts"

    def test_underscored_model_id_preserved(self):
        assert _model_id_from_golden_path("data/gamslib/mcp/two_cge_mcp.gms") == "two_cge"

    def test_non_golden_returns_none(self):
        assert _model_id_from_golden_path("src/emit/emit_gams.py") is None
        assert _model_id_from_golden_path("data/gamslib/raw/maxmin.gms") is None
        assert _model_id_from_golden_path("README.md") is None


class TestExtractBucket:
    def test_full_record(self):
        model = {
            "mcp_solve": {"outcome_category": "model_optimal_presolve"},
            "solution_comparison": {"comparison_status": "match"},
        }
        assert _extract_bucket(model) == {
            "outcome_category": "model_optimal_presolve",
            "comparison_status": "match",
        }

    def test_missing_subdicts_are_none(self):
        assert _extract_bucket({}) == {
            "outcome_category": None,
            "comparison_status": None,
        }

    def test_null_subdicts_do_not_crash(self):
        # The DB stores JSON null for un-run stages.
        assert _extract_bucket({"mcp_solve": None, "solution_comparison": None}) == {
            "outcome_category": None,
            "comparison_status": None,
        }


class TestBucketSeverity:
    def test_match_optimal_is_healthiest(self):
        best = {"outcome_category": "model_optimal", "comparison_status": "match"}
        assert _bucket_severity(best) == 22

    def test_compare_dominates_outcome(self):
        # A mismatch that solved optimally is still below any match.
        matched = {"outcome_category": "model_infeasible", "comparison_status": "match"}
        mismatched = {
            "outcome_category": "model_optimal",
            "comparison_status": "mismatch",
        }
        assert _bucket_severity(matched) > _bucket_severity(mismatched)

    def test_presolve_and_cold_optimal_rank_equal(self):
        cold = {"outcome_category": "model_optimal", "comparison_status": "match"}
        presolve = {
            "outcome_category": "model_optimal_presolve",
            "comparison_status": "match",
        }
        assert _bucket_severity(cold) == _bucket_severity(presolve)

    def test_failure_is_zero_ish(self):
        failed = {"outcome_category": "path_syntax_error", "comparison_status": None}
        assert _bucket_severity(failed) == 0


class TestClassifyBucketMove:
    MATCH_OPT = {"outcome_category": "model_optimal", "comparison_status": "match"}
    MATCH_PRESOLVE = {
        "outcome_category": "model_optimal_presolve",
        "comparison_status": "match",
    }
    MISMATCH = {"outcome_category": "model_optimal", "comparison_status": "mismatch"}
    INFEASIBLE = {"outcome_category": "model_infeasible", "comparison_status": None}

    def test_identical_is_same(self):
        assert _classify_bucket_move(self.MATCH_OPT, dict(self.MATCH_OPT)) == "same"

    def test_match_to_mismatch_is_backward(self):
        # The core regression the checkpoint must catch.
        assert _classify_bucket_move(self.MATCH_OPT, self.MISMATCH) == "backward"

    def test_match_to_infeasible_is_backward(self):
        # The #1462 rocket class: a byte-stable golden whose solve broke.
        assert _classify_bucket_move(self.MATCH_OPT, self.INFEASIBLE) == "backward"

    def test_mismatch_to_match_is_forward(self):
        assert _classify_bucket_move(self.MISMATCH, self.MATCH_OPT) == "forward"

    def test_infeasible_to_match_is_forward(self):
        assert _classify_bucket_move(self.INFEASIBLE, self.MATCH_OPT) == "forward"

    def test_cold_to_presolve_match_is_shift_not_regression(self):
        # maxmin's Day-3 path shift (cold match -> presolve match): equal severity,
        # different label -> benign shift, NOT a NO-GO.
        assert _classify_bucket_move(self.MATCH_OPT, self.MATCH_PRESOLVE) == "shift"

    def test_shift_is_not_backward(self):
        # A same-severity relabel must never be a NO-GO.
        assert _classify_bucket_move(self.MATCH_PRESOLVE, self.MATCH_OPT) != "backward"


class TestCheckpointVerdict:
    def test_all_same_is_go(self):
        rows = [{"model": "a", "move": "same"}, {"model": "b", "move": "shift"}]
        assert _checkpoint_verdict(rows) == ("GO", [])

    def test_forward_is_go(self):
        rows = [{"model": "a", "move": "forward"}]
        assert _checkpoint_verdict(rows) == ("GO", [])

    def test_backward_is_nogo(self):
        rows = [{"model": "a", "move": "same"}, {"model": "b", "move": "backward"}]
        assert _checkpoint_verdict(rows) == ("NO-GO", ["b"])

    def test_missing_is_nogo(self):
        # A changed golden with no DB entry (added/renamed model) must block —
        # a missing entry can mask a problem, so it cannot pass the gate.
        rows = [{"model": "a", "move": "same"}, {"model": "gone", "move": "missing"}]
        assert _checkpoint_verdict(rows) == ("NO-GO", ["gone"])

    def test_backward_and_missing_both_reported(self):
        rows = [
            {"model": "a", "move": "backward"},
            {"model": "b", "move": "missing"},
            {"model": "c", "move": "same"},
        ]
        verdict, blocking = _checkpoint_verdict(rows)
        assert verdict == "NO-GO"
        assert blocking == ["a", "b"]

    def test_empty_is_go(self):
        assert _checkpoint_verdict([]) == ("GO", [])

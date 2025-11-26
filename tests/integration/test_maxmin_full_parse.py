"""Integration test for maxmin.gms parse progress (Sprint 11 Day 2 Extended).

Tests maxmin.gms parsing after subset indexing, indexed set assignments, subset expansion, and aggregation.

Note: Line 59 blocker (aggregation over subsets) has been resolved!
New blocker at line 75: variable bounds expansion for sets without explicit members.
"""

import pytest

from src.ir.parser import parse_model_file


def test_maxmin_parse_progress():
    """Test that maxmin.gms parses past line 59 with aggregation over subset domains.

    Progress tracking:
    - Before Sprint 11 Day 1: Line 51 (47% parse rate) - nested indexing blocker
    - After Sprint 11 Day 1: Line 70 (65% parse rate) - loop statement blocker
    - After Sprint 11 Day 2 loop: Line 78 (72% parse rate) - subset indexing in grammar
    - After Sprint 11 Day 2 Extended (grammar): Line 37 - indexed set assignment blocker
    - After Sprint 11 Day 2 Extended (domain context): Line 51 - subset expansion blocker
    - After Sprint 11 Day 2 Extended (subset expansion): Line 59 (~55% parse rate) - aggregation subset blocker
    - After Sprint 11 Day 2 Extended (aggregation): Line 75 (~69% parse rate) - bounds expansion blocker

    Line 37 fix: Added domain context for indexed assignments
    - low(n,nn) = ord(n) > ord(nn) now parses successfully
    - Indices from lvalue are available as free domain in expression

    Line 51 fix: Added subset reference expansion in indices
    - dist(low) where low is low(n,n) now expands to dist(n,n)
    - Only expands multi-dimensional sets whose members are other sets

    Line 59 fix: Added subset domain support in aggregation functions
    - smin(low(n,nn), expr) now recognized as aggregation over subset domain
    - Indices n,nn are available in aggregated expression

    New blocker at line 75 is variable bounds expansion:
    - point.lo(n,d) = 0 where n is /p1*p13/ (no explicit members yet)
    - Requires handling sets with range specifications

    Achievements:
    - Line 78: Subset indexing in lvalues (dist.l(low(n,nn)))
    - Line 87: Option statements in if/loop blocks
    - Line 106: DNLP and other solver types
    - Line 37: Indexed set assignments with domain context
    - Line 51: Subset reference expansion in variable indices
    - Line 59: Aggregation over subset domains
    """
    try:
        model = parse_model_file("tests/fixtures/gamslib/maxmin.gms")

        # If we got here, maxmin.gms parsed completely!
        # This would be a HUGE achievement - verify all components
        assert model is not None
        assert len(model.sets) >= 2
        assert len(model.params) >= 1
        assert len(model.variables) >= 2
        assert len(model.equations) >= 5
        assert len(model.loop_statements) == 1

        print("✅ AMAZING: maxmin.gms parsed 100%!")

    except Exception as e:
        # Now expected to fail at line 51 (subset reference as index)
        error_msg = str(e)

        # Should NOT fail on earlier blockers (lines 37, 51, 59, 78, 87, 106)
        assert not (
            "37" in error_msg and "ord" in error_msg
        ), f"Should not fail on indexed set assignment (line 37): {error_msg}"
        assert not (
            "51" in error_msg and "dist" in error_msg and "2 indices" in error_msg
        ), f"Should not fail on subset expansion (line 51): {error_msg}"
        assert not (
            "59" in error_msg and "low" in error_msg and "Undefined" in error_msg
        ), f"Should not fail on aggregation over subset (line 59): {error_msg}"
        assert (
            "subset indexing" not in error_msg.lower()
        ), f"Should not fail on subset indexing grammar (line 78): {error_msg}"
        assert not (
            "option" in error_msg.lower() and "87" in error_msg
        ), f"Should not fail on option in exec (line 87): {error_msg}"
        assert (
            "dnlp" not in error_msg.lower()
        ), f"Should not fail on DNLP solver (line 106): {error_msg}"

        # Should fail at line 75 (variable bounds expansion)
        assert (
            "75" in error_msg or "line 7" in error_msg
        ), f"Expected to fail at line 75 (bounds expansion blocker), but got: {error_msg}"

        print("✅ Sprint 11 Day 2 Extended Aggregation Complete:")
        print("   Aggregation over subset domains now supported (line 59 ✓)")
        print("   Blocker moved: line 59 → line 75")
        print("   Line 75: Variable bounds expansion for sets without explicit members")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

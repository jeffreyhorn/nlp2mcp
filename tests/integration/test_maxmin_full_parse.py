"""Integration test for maxmin.gms parse progress (Sprint 11 Day 2 Extended).

Tests maxmin.gms parsing after subset indexing, indexed set assignments, and subset expansion.

Note: Line 51 blocker (subset expansion) has been resolved!
New blocker at line 59: subset references in aggregation functions (smin(low(n,nn), ...)).
"""

import pytest

from src.ir.parser import parse_model_file


def test_maxmin_parse_progress():
    """Test that maxmin.gms parses past line 51 with subset expansion support.

    Progress tracking:
    - Before Sprint 11 Day 1: Line 51 (47% parse rate) - nested indexing blocker
    - After Sprint 11 Day 1: Line 70 (65% parse rate) - loop statement blocker
    - After Sprint 11 Day 2 loop: Line 78 (72% parse rate) - subset indexing in grammar
    - After Sprint 11 Day 2 Extended (grammar): Line 37 - indexed set assignment blocker
    - After Sprint 11 Day 2 Extended (domain context): Line 51 - subset expansion blocker
    - After Sprint 11 Day 2 Extended (subset expansion): Line 59 (~55% parse rate) - aggregation subset blocker

    Line 37 fix: Added domain context for indexed assignments
    - low(n,nn) = ord(n) > ord(nn) now parses successfully
    - Indices from lvalue are available as free domain in expression

    Line 51 fix: Added subset reference expansion in indices
    - dist(low) where low is low(n,n) now expands to dist(n,n)
    - Only expands multi-dimensional sets whose members are other sets

    New blocker at line 59 is aggregation with subset domain:
    - smin(low(n,nn), expr) - using subset as aggregation domain
    - Requires special handling in aggregation functions

    Achievements:
    - Line 78: Subset indexing in lvalues (dist.l(low(n,nn)))
    - Line 87: Option statements in if/loop blocks
    - Line 106: DNLP and other solver types
    - Line 37: Indexed set assignments with domain context
    - Line 51: Subset reference expansion in variable indices
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

        # Should NOT fail on earlier blockers (lines 37, 51, 78, 87, 106)
        assert not ("37" in error_msg and "ord" in error_msg), (
            f"Should not fail on indexed set assignment (line 37): {error_msg}"
        )
        assert not ("51" in error_msg and "dist" in error_msg and "2 indices" in error_msg), (
            f"Should not fail on subset expansion (line 51): {error_msg}"
        )
        assert "subset indexing" not in error_msg.lower(), (
            f"Should not fail on subset indexing grammar (line 78): {error_msg}"
        )
        assert not ("option" in error_msg.lower() and "87" in error_msg), (
            f"Should not fail on option in exec (line 87): {error_msg}"
        )
        assert "dnlp" not in error_msg.lower(), (
            f"Should not fail on DNLP solver (line 106): {error_msg}"
        )

        # Should fail at line 59 (aggregation with subset domain)
        assert "59" in error_msg or "line 5" in error_msg, (
            f"Expected to fail at line 59 (aggregation subset blocker), but got: {error_msg}"
        )

        print("✅ Sprint 11 Day 2 Extended Subset Expansion Complete:")
        print("   Subset expansion now supported (line 51 ✓)")
        print("   Blocker moved: line 51 → line 59")
        print("   Line 59: Aggregation over subset domains (smin(low(n,nn), ...))")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

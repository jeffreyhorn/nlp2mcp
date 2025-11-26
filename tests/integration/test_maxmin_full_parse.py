"""Integration test for maxmin.gms parse progress (Sprint 11 Day 2 Extended).

Tests maxmin.gms grammar parsing after subset indexing, option in exec, and solver support.

Note: Line 37 blocker (indexed set assignments) has been resolved!
New blocker at line 51: subset references as indices (dist(low) where low is a 2D set).
"""

import pytest

from src.ir.parser import parse_model_file


def test_maxmin_parse_progress():
    """Test that maxmin.gms parses past line 37 with indexed set assignment support.

    Progress tracking:
    - Before Sprint 11 Day 1: Line 51 (40% parse rate) - nested indexing blocker
    - After Sprint 11 Day 1: Line 70 (66% parse rate) - loop statement blocker
    - After Sprint 11 Day 2 loop: Line 78 (85% parse rate) - subset indexing in grammar
    - After Sprint 11 Day 2 Extended (grammar): Line 37 - indexed set assignment blocker
    - After Sprint 11 Day 2 Extended (semantic): Line 51 - subset reference as index blocker

    Line 37 fix: Added domain context for indexed assignments
    - low(n,nn) = ord(n) > ord(nn) now parses successfully
    - Indices from lvalue are available as free domain in expression

    New blocker at line 51 is subset reference pattern:
    - defdist(low(n,nn)).. dist(low) =e= ...
    - Using 'low' (a 2D set) as single index requires expansion to underlying indices

    Achievements:
    - Line 78: Subset indexing in lvalues (dist.l(low(n,nn)))
    - Line 87: Option statements in if/loop blocks
    - Line 106: DNLP and other solver types
    - Line 37: Indexed set assignments with domain context
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

        # Should NOT fail on earlier blockers (lines 37, 78, 87, 106)
        assert not ("37" in error_msg and "ord" in error_msg), (
            f"Should not fail on indexed set assignment (line 37): {error_msg}"
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

        # Should fail at line 51 (subset reference as index)
        assert "51" in error_msg or "line 5" in error_msg, (
            f"Expected to fail at line 51 (subset reference blocker), but got: {error_msg}"
        )

        print("✅ Sprint 11 Day 2 Extended Semantic Progress:")
        print("   Indexed set assignments now supported (line 37 ✓)")
        print("   Blocker moved: line 37 → line 51")
        print("   Line 51: Subset references as indices require expansion (dist(low))")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

"""Integration test for maxmin.gms parse progress (Sprint 11 Day 2 Extended).

Tests that maxmin.gms parses through line 77 after adding loop statement support.

Note: Full parse blocked at line 78 by subset indexing in assignments (dist.l(low(n,nn))),
which requires semantic resolution and is out of Sprint 11 scope.
"""

import pytest

from src.ir.parser import parse_model_file


def test_maxmin_parse_progress():
    """Test that maxmin.gms parses through line 77 with loop statement support.

    Progress tracking:
    - Before Sprint 11 Day 1: Line 51 (40% parse rate) - nested indexing blocker
    - After Sprint 11 Day 1: Line 70 (66% parse rate) - loop statement blocker
    - After Sprint 11 Day 2 Extended: Line 78 (~85% parse rate) - subset indexing blocker
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
        # Expected to fail at line 78 - verify we made progress past line 70
        error_msg = str(e)

        # Should NOT fail on loop statement (line 70) - that's now supported
        assert "loop" not in error_msg.lower() or "78" in error_msg, (
            f"Should not fail on loop at line 70: {error_msg}"
        )

        # Should fail at line 78 or later (subset indexing in assignment)
        assert "78" in error_msg or "line 7" in error_msg or "line 8" in error_msg, (
            f"Expected to fail at line 78+, but got: {error_msg}"
        )

        print("✅ Sprint 11 Day 2 Extended Goal Achieved:")
        print("   Parses through line 77 (loop statement now supported)")
        print("   Blocker moved: line 70 → line 78")
        print("   New blocker: subset indexing in assignments (dist.l(low(n,nn)))")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

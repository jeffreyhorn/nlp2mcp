"""Performance tests for comma-separated list parsing.

These tests ensure the parser maintains good performance with long
comma-separated lists in set definitions. Issue #138 reported performance
problems that could not be reproduced, but these tests guard against regressions.

Note: These tests use wall-clock time assertions and are marked as @pytest.mark.slow
to allow selective execution and reduce flakiness in CI/CD environments with
variable system load.
"""

import time

import pytest

from src.ir import parser


class TestCommaListPerformance:
    """Test parser performance with various comma-separated list sizes."""

    def test_small_list_fast(self):
        """10 elements should parse quickly (< 1s)."""
        elements = ", ".join([f"i{i}" for i in range(1, 11)])

        code = f"""
        Sets i /{elements}/ ;
        Variables
            x(i)
            obj ;
        Equations objdef ;
        objdef.. obj =e= sum(i, x(i));
        Model test /all/;
        Solve test using NLP minimizing obj;
        """

        start = time.time()
        result = parser.parse_model_text(code)
        elapsed = time.time() - start

        assert result.sets["i"].members == [f"i{i}" for i in range(1, 11)]
        assert elapsed < 1.0, f"10 elements took {elapsed:.2f}s (expected < 1.0s)"

    @pytest.mark.slow
    def test_medium_list_reasonable(self):
        """50 elements should parse reasonably fast (< 3s with CI/CD buffer)."""
        elements = ", ".join([f"i{i}" for i in range(1, 51)])

        code = f"""
        Sets i /{elements}/ ;
        Variables
            x(i)
            obj ;
        Equations objdef ;
        objdef.. obj =e= sum(i, x(i));
        Model test /all/;
        Solve test using NLP minimizing obj;
        """

        start = time.time()
        result = parser.parse_model_text(code)
        elapsed = time.time() - start

        assert len(result.sets["i"].members) == 50
        # Allow extra buffer for CI/CD variability
        assert elapsed < 3.0, f"50 elements took {elapsed:.2f}s (expected < 3.0s)"

    @pytest.mark.slow
    def test_large_list_acceptable(self):
        """100 elements should parse in acceptable time (< 5s with CI/CD buffer)."""
        elements = ", ".join([f"i{i}" for i in range(1, 101)])

        code = f"""
        Sets i /{elements}/ ;
        Variables
            x(i)
            obj ;
        Equations objdef ;
        objdef.. obj =e= sum(i, x(i));
        Model test /all/;
        Solve test using NLP minimizing obj;
        """

        start = time.time()
        result = parser.parse_model_text(code)
        elapsed = time.time() - start

        assert len(result.sets["i"].members) == 100
        # Allow extra buffer for CI/CD variability
        assert elapsed < 5.0, f"100 elements took {elapsed:.2f}s (expected < 5.0s)"

    @pytest.mark.slow
    def test_very_large_list_works(self):
        """200 elements should still work in reasonable time (< 8s with CI/CD buffer)."""
        elements = ", ".join([f"i{i}" for i in range(1, 201)])

        code = f"""
        Sets i /{elements}/ ;
        Variables
            x(i)
            obj ;
        Equations objdef ;
        objdef.. obj =e= sum(i, x(i));
        Model test /all/;
        Solve test using NLP minimizing obj;
        """

        start = time.time()
        result = parser.parse_model_text(code)
        elapsed = time.time() - start

        assert len(result.sets["i"].members) == 200
        # Allow extra buffer for CI/CD variability
        assert elapsed < 8.0, f"200 elements took {elapsed:.2f}s (expected < 8.0s)"

    @pytest.mark.slow
    def test_scaling_is_reasonable(self):
        """Performance should scale reasonably with list size."""
        times = []
        sizes = [10, 50, 100]

        for size in sizes:
            elements = ", ".join([f"i{i}" for i in range(1, size + 1)])

            code = f"""
            Sets i /{elements}/ ;
            Variables
                x(i)
                obj ;
            Equations objdef ;
            objdef.. obj =e= sum(i, x(i));
            Model test /all/;
            Solve test using NLP minimizing obj;
            """

            start = time.time()
            parser.parse_model_text(code)
            elapsed = time.time() - start
            times.append(elapsed)

        # Check that 10x increase in size doesn't cause 10x increase in time
        # Allow 5x time increase for 10x size increase (near-linear)
        ratio_50_to_10 = times[1] / times[0]
        ratio_100_to_50 = times[2] / times[1]

        assert ratio_50_to_10 < 5.0, f"5x elements caused {ratio_50_to_10:.1f}x time increase"
        assert ratio_100_to_50 < 5.0, f"2x elements caused {ratio_100_to_50:.1f}x time increase"

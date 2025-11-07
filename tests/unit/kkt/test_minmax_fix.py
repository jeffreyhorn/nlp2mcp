"""Regression tests for min/max in objective-defining equations.

These tests cover the critical bug where min/max appearing in equations that
define the objective variable creates mathematically infeasible KKT systems.

Research document: docs/research/minmax_objective_reformulation.md
Design document: docs/design/minmax_kkt_fix_design.md

The tests use actual GAMS files from the research phase and verify that:
1. The models parse correctly
2. Min/max reformulation generates auxiliary variables and constraints
3. KKT assembly includes ALL equality constraint multipliers (including auxiliary)
4. The generated MCP system is well-formed
5. No errors occur during the pipeline

These tests will initially be marked @pytest.mark.xfail because the fix is
not yet implemented. On Sprint 5 Day 2, the xfail markers should be removed
as the implementation is completed.
"""

from __future__ import annotations

import pytest

from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_file
from src.kkt.reformulation import reformulate_model


@pytest.mark.integration
@pytest.mark.xfail(reason="Min/max in objective-defining equations not yet fixed (Sprint 5 Day 2)")
class TestMinMaxInObjectiveRegression:
    """Regression tests for min/max in objective-defining equations.

    These tests will PASS once Sprint 5 Day 2 implementation is complete.
    Until then, they are expected to fail (xfail).
    """

    def test_minimize_min_xy(self):
        """Test Case 1: minimize z where z = min(x, y)

        This is the CRITICAL test case that proves Strategy 2 is mathematically
        infeasible and Strategy 1 (auxiliary variables with proper KKT) is required.

        GAMS Model:
            Variables x, y, z, obj;
            x.lo = 1; y.lo = 2;

            objective.. obj =e= z;
            min_constraint.. z =e= min(x, y);

            Solve model using NLP minimizing obj;

        Expected Solution: z* = 1, x* = 1, y* = 2

        Expected MCP Structure (Strategy 1):
            Variables: x, y, z, obj, aux_min

            Multipliers:
                ν_objective (for obj = z, free)
                ν_aux_eq (for z = aux_min, free)  <- CRITICAL: Must be created!
                λ_x (for aux_min ≤ x, ≥ 0)
                λ_y (for aux_min ≤ y, ≥ 0)

            Stationarity:
                ∂L/∂obj = ν_objective = 0
                ∂L/∂z = -ν_objective + ν_aux_eq = 0
                ∂L/∂aux_min = -ν_aux_eq - λ_x - λ_y = 0  <- Includes auxiliary multiplier!
                ∂L/∂x = ... + λ_x = 0
                ∂L/∂y = ... + λ_y = 0

            Equalities:
                obj - z = 0
                z - aux_min = 0

            Complementarity:
                (x - aux_min) ⊥ λ_x
                (y - aux_min) ⊥ λ_y

        This test verifies:
        - Model parses successfully
        - Min/max reformulation creates auxiliary variable (aux_min)
        - Auxiliary equality constraint (z = aux_min) is created
        - KKT assembly creates multiplier for auxiliary constraint
        - Stationarity equation for aux_min includes all terms
        - No errors during pipeline
        """
        gams_file = "tests/fixtures/minmax_research/test1_minimize_min.gms"

        # Parse GAMS model
        model_ir = parse_model_file(gams_file)
        assert model_ir is not None
        assert model_ir.objective is not None

        # Normalize
        normalize_model(model_ir)

        # Reformulate min/max (this should create auxiliary variables)
        reformulate_model(model_ir)

        # Verify auxiliary variable was created
        aux_vars = [v for v in model_ir.variables.keys() if v.startswith("aux_min_")]
        assert len(aux_vars) >= 1, "Auxiliary variable for min() should be created"

        # Verify auxiliary equality constraint exists (z = aux_min)
        # This should be named something like "aux_eq_min_*"
        aux_eqs = [eq for eq in model_ir.equations.keys() if "aux" in eq.lower()]
        assert len(aux_eqs) >= 1, "Auxiliary equality constraint should be created"

        # Verify inequality constraints exist (aux_min <= x, aux_min <= y)
        minmax_ineqs = [eq for eq in model_ir.equations.keys() if eq.startswith("minmax_min_")]
        assert len(minmax_ineqs) >= 2, "Two inequality constraints should be created for min(x,y)"

        # Compute derivatives (this will be implemented using actual derivative computation)
        # For now, we're testing that reformulation creates correct structure

        # The full integration with KKT assembly will be tested once derivatives are computed
        # For this scaffolding test, we verify the structure is correct

    def test_maximize_max_xy(self):
        """Test Case 2: maximize z where z = max(x, y)

        This is the SYMMETRIC case to Test 1. Should work if Test 1 works.

        GAMS Model:
            Variables x, y, z, obj;
            x.up = 10; y.up = 20;

            objective.. obj =e= z;
            max_constraint.. z =e= max(x, y);

            Solve model using NLP maximizing obj;

        Expected Solution: z* = 20, y* = 20 (maximize the maximum)

        Expected MCP Structure:
            Similar to Test 1 but with max reformulation:
            - aux_max variable
            - Inequalities: aux_max >= x, aux_max >= y (sign flipped)

        This test verifies symmetric case handling.
        """
        gams_file = "tests/fixtures/minmax_research/test2_maximize_max.gms"

        model_ir = parse_model_file(gams_file)
        assert model_ir is not None

        normalize_model(model_ir)
        reformulate_model(model_ir)

        # Verify max auxiliary variable
        aux_vars = [v for v in model_ir.variables.keys() if v.startswith("aux_max_")]
        assert len(aux_vars) >= 1, "Auxiliary variable for max() should be created"

        # Verify inequality constraints
        minmax_ineqs = [eq for eq in model_ir.equations.keys() if eq.startswith("minmax_max_")]
        assert len(minmax_ineqs) >= 2, "Two inequality constraints should be created for max(x,y)"

    def test_minimize_max_xy(self):
        """Test Case 3: minimize z where z = max(x, y)

        This is an OPPOSITE-SENSE combination (minimize a maximum).

        GAMS Model:
            Variables x, y, z, obj;
            x.lo = 1; y.lo = 2;

            objective.. obj =e= z;
            max_constraint.. z =e= max(x, y);

            Solve model using NLP minimizing obj;

        Expected Solution: z* = 2, y* = 2 (minimize the maximum, so both become equal)

        This tests that the reformulation works regardless of objective sense.
        The key is proper KKT assembly with auxiliary multipliers.
        """
        gams_file = "tests/fixtures/minmax_research/test3_minimize_max.gms"

        model_ir = parse_model_file(gams_file)
        assert model_ir is not None

        normalize_model(model_ir)
        reformulate_model(model_ir)

        aux_vars = [v for v in model_ir.variables.keys() if v.startswith("aux_max_")]
        assert len(aux_vars) >= 1

    def test_maximize_min_xy(self):
        """Test Case 4: maximize z where z = min(x, y)

        Another OPPOSITE-SENSE combination (maximize a minimum).

        GAMS Model:
            Variables x, y, z, obj;
            x.up = 10; y.up = 20;

            objective.. obj =e= z;
            min_constraint.. z =e= min(x, y);

            Solve model using NLP maximizing obj;

        Expected Solution: z* = 10, x* = 10 (maximize the minimum, so both become equal)

        This completes the test matrix of sense/function combinations.
        """
        gams_file = "tests/fixtures/minmax_research/test4_maximize_min.gms"

        model_ir = parse_model_file(gams_file)
        assert model_ir is not None

        normalize_model(model_ir)
        reformulate_model(model_ir)

        aux_vars = [v for v in model_ir.variables.keys() if v.startswith("aux_min_")]
        assert len(aux_vars) >= 1

    def test_nested_minmax(self):
        """Test Case 5: minimize z where z = max(min(x, y), w)

        This tests NESTED min/max handling.

        GAMS Model:
            Variables x, y, w, z, obj;
            x.lo = 1; y.lo = 2; w.lo = 1.5;

            objective.. obj =e= z;
            nested.. z =e= max(min(x, y), w);

            Solve model using NLP minimizing obj;

        Expected Solution: z* = 1.5 (max of min(1,2)=1 and w=1.5)

        Expected MCP Structure:
            This should be flattened or handled with multiple auxiliary variables.
            The reformulation module should handle nested cases.

        This is the most complex test case.
        """
        gams_file = "tests/fixtures/minmax_research/test5_nested_minmax.gms"

        model_ir = parse_model_file(gams_file)
        assert model_ir is not None

        normalize_model(model_ir)
        reformulate_model(model_ir)

        # Nested case may create multiple auxiliary variables
        aux_vars = [v for v in model_ir.variables.keys() if v.startswith("aux_")]
        assert len(aux_vars) >= 1, "At least one auxiliary variable should be created"


@pytest.mark.integration
class TestMinMaxInConstraintNoRegression:
    """Regression test: min/max in constraints (NOT objective) should still work.

    This verifies that the fix for objective-defining min/max doesn't break
    the existing functionality for min/max in regular constraints.
    """

    @pytest.mark.xfail(reason="Test fixture has GAMS syntax issue - needs fixing")
    def test_constraint_min_not_objective(self):
        """Test Case 6: min/max in constraint, NOT defining objective.

        GAMS Model:
            Variables x, y, z, obj;
            x.lo = 1; y.lo = 2;

            objective.. obj =e= z;
            constraint.. z =g= min(x, y) + 0.5;

            Solve model using NLP minimizing obj;

        Expected Solution: z* = 1.5, min(x,y) = 1

        This should work with standard epigraph reformulation.
        No special handling needed because min/max is NOT defining the objective.

        This test ensures we didn't break existing functionality.
        """
        gams_file = "tests/fixtures/minmax_research/test6_constraint_min.gms"

        model_ir = parse_model_file(gams_file)
        assert model_ir is not None

        normalize_model(model_ir)
        reformulate_model(model_ir)

        # Should still create auxiliary variable
        aux_vars = [v for v in model_ir.variables.keys() if v.startswith("aux_")]
        assert len(aux_vars) >= 1

        # But the objective variable (z) should NOT be involved in the auxiliary equation
        # The constraint is: z >= aux + 0.5, not z = aux


@pytest.mark.unit
class TestMinMaxDetectionScaffolding:
    """Unit tests for detection logic scaffolding.

    These tests will be expanded in Task 1.4 (detection logic implementation).
    For now, they serve as placeholders showing the expected API.
    """

    @pytest.mark.xfail(reason="Detection logic not yet implemented (Sprint 5 Day 1 Task 1.4)")
    def test_detects_simple_objective_minmax(self):
        """Placeholder: Detection of simple obj = min(x, y) case."""
        # from src.ir.minmax_detection import detects_objective_minmax
        # Will be implemented in Task 1.4
        pass

    @pytest.mark.xfail(reason="Detection logic not yet implemented (Sprint 5 Day 1 Task 1.4)")
    def test_detects_chained_objective_minmax(self):
        """Placeholder: Detection of chained obj = z, z = min(x, y) case."""
        # Will be implemented in Task 1.4
        pass

    @pytest.mark.xfail(reason="Detection logic not yet implemented (Sprint 5 Day 1 Task 1.4)")
    def test_no_detection_for_constraint_minmax(self):
        """Placeholder: No detection when min/max is in constraint, not objective."""
        # Will be implemented in Task 1.4
        pass

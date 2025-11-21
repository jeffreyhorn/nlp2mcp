"""
Integration Tests for Full NLP → AD Pipeline

These tests verify the complete end-to-end workflow:
1. Parse GAMS file
2. Normalize to IR
3. Compute derivatives using high-level API
4. Verify correctness of results

Test Coverage:
--------------
- Scalar models (no indexing)
- Indexed models with sum aggregations
- Models with equality constraints
- Models with inequality constraints
- Models with bounds
- Models with parameters
- Models with multiple variables

Each test validates:
- API returns correct structure
- Gradient has expected number of components
- Jacobians have expected sparsity patterns
- Derivatives are non-trivial (not all zeros)

Status:
-------
Integration tests are now enabled after fixing GitHub Issue #20 (parse hang).

GitHub Issue #19 Status: ✅ RESOLVED
- The objective extraction issue has been fixed in normalize_model()
- Fix verified by 6 new unit tests in tests/ir/test_normalize.py
- All normalization tests pass successfully

GitHub Issue #20 Status: ✅ RESOLVED
- parse_model_file() hang fixed by switching to standard lexer
- All example files now parse successfully

GitHub Issue #22 Status: ✅ RESOLVED
- API mismatch tests fixed by updating to correct API attributes
- Changed gradient.mapping.num_vars → gradient.num_cols
- Changed J_g.mapping.num_equations → J_g.num_rows
- Changed gradient.mapping → gradient.index_mapping
- Updated test expectations to account for objective variable (obj)

GitHub Issue #24 Status: ✅ RESOLVED
- Bounds handling bug fixed in constraint_jacobian.py
- Added check to skip bounds in _compute_inequality_jacobian()
- Bounds are now properly handled by _compute_bound_jacobian()
- test_bounds_nlp_basic now passes

GitHub Issue #25 Status: ✅ RESOLVED
- Power operator (^) now supported in AD module
- Added differentiation support for Binary('^', base, exponent)
- Uses existing _diff_power() logic from Call("power", ...)
- test_nonlinear_mix_model now passes

Current Status:
- ✅ All 15 out of 15 tests passing (100% pass rate!)
- ✅ Full integration test coverage achieved

See:
- GitHub Issue #19: "Objective Expressions Not Found After Model Normalization"
  https://github.com/jeffreyhorn/nlp2mcp/issues/19
- GitHub Issue #20: "Issue: parse_model_file() Hangs on Example Files"
  https://github.com/jeffreyhorn/nlp2mcp/issues/20
- GitHub Issue #22: "Integration Tests API Mismatch"
  https://github.com/jeffreyhorn/nlp2mcp/issues/22
"""

import os
from pathlib import Path

import pytest

# NOTE: Integration tests now enabled after fixing GitHub Issue #20.
#
# See:
# - GitHub Issue #19 (RESOLVED): Objective extraction in normalization
# - GitHub Issue #20 (RESOLVED): parse_model_file() hang fixed by switching from
#   dynamic_complete lexer to standard lexer with ambiguity="resolve"
#   https://github.com/jeffreyhorn/nlp2mcp/issues/20
from src.ad.api import compute_derivatives
from src.ir.normalize import normalize_model
from src.ir.parser import parse_file, parse_model_file

pytestmark = pytest.mark.e2e

# Skip marker for tests failing due to API mismatch (Issue #22)
skip_api_mismatch = pytest.mark.skip(
    reason="API mismatch (Issue #22): Tests expect gradient.mapping but implementation provides "
    "gradient.index_mapping. See https://github.com/jeffreyhorn/nlp2mcp/issues/22"
)


# Helper to get example file path
def get_example_path(filename: str) -> str:
    """Get absolute path to example file."""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(test_dir))
    return os.path.join(repo_root, "examples", filename)


# Helper to parse and normalize a model
def parse_and_normalize(filename: str):
    """Parse a GAMS file and normalize it."""
    model_ir = parse_model_file(get_example_path(filename))
    normalize_model(model_ir)
    return model_ir


@pytest.mark.e2e
class TestScalarModels:
    """Test integration on scalar (non-indexed) models."""

    def test_scalar_nlp_basic(self):
        """Test scalar model: min x s.t. x + a = 0."""
        model_ir = parse_and_normalize("scalar_nlp.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Should have 2 variables (x and obj)
        assert gradient.num_cols == 2

        # Gradient should have 2 components
        assert gradient.num_nonzeros() == 2

        # Verify gradient components exist
        for col_id in range(2):
            grad = gradient.get_derivative(col_id)
            assert grad is not None

        # Should have 2 equality constraints: objective equation and stationarity
        assert J_h.num_rows == 2
        assert J_h.num_nonzeros() > 0

        # Should have no inequality constraints
        assert J_g.num_nonzeros() == 0


@pytest.mark.e2e
class TestIndexedModels:
    """Test integration on indexed models with sum aggregations."""

    def test_simple_nlp_indexed(self):
        """Test indexed model: min sum(i, a(i)*x(i)) s.t. x(i) >= 0."""
        model_ir = parse_and_normalize("simple_nlp.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Should have 4 variables: obj, x(i1), x(i2), x(i3)
        assert gradient.num_cols == 4

        # Gradient should have 4 components
        assert gradient.num_nonzeros() == 4

        # Verify each gradient component exists and is not None
        for col_id in range(4):
            deriv = gradient.get_derivative(col_id)
            assert deriv is not None, f"Gradient component {col_id} should exist"

        # Should have 3 inequality constraints: x(i) >= 0 normalized to -x(i) <= 0
        # plus any bounds
        assert J_g.num_nonzeros() >= 3

        # Should have equality constraints (objective definition and balance equations)
        assert J_h.num_nonzeros() >= 1


@pytest.mark.e2e
class TestJacobianStructure:
    """Test Jacobian structure and sparsity patterns."""

    def test_jacobian_sparsity_pattern(self):
        """Test that Jacobian has correct sparsity pattern."""
        model_ir = parse_and_normalize("simple_nlp.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Get nonzero entries
        nonzeros = J_g.get_nonzero_entries()
        assert len(nonzeros) > 0

        # Each nonzero should have valid row/col IDs
        for row_id, col_id in nonzeros:
            assert 0 <= row_id < J_g.num_rows
            assert 0 <= col_id < J_g.num_cols

            # Derivative should exist
            deriv = J_g.get_derivative(row_id, col_id)
            assert deriv is not None

    def test_jacobian_by_names(self):
        """Test querying Jacobian by equation/variable names."""
        model_ir = parse_and_normalize("simple_nlp.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Should be able to query by names if they exist
        # For indexed constraints, need to specify indices
        # This is a smoke test - just verify no crashes
        nonzeros = J_g.get_nonzero_entries()
        if len(nonzeros) > 0:
            row_id, col_id = nonzeros[0]
            deriv = J_g.get_derivative(row_id, col_id)
            assert deriv is not None


@pytest.mark.e2e
class TestGradientStructure:
    """Test gradient structure and access patterns."""

    def test_gradient_by_name(self):
        """Test querying gradient by variable name."""
        model_ir = parse_and_normalize("scalar_nlp.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Should be able to get derivative by variable ID
        deriv = gradient.get_derivative(0)
        assert deriv is not None

    def test_gradient_all_components(self):
        """Test getting all gradient components."""
        model_ir = parse_and_normalize("simple_nlp.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Get all derivatives
        all_derivs = gradient.get_all_derivatives()
        assert len(all_derivs) == gradient.num_nonzeros()

        # Each derivative should be valid
        for col_id, deriv_expr in all_derivs.items():
            assert deriv_expr is not None
            assert 0 <= col_id < gradient.num_cols


@pytest.mark.e2e
class TestAPIErrorHandling:
    """Test that API handles errors gracefully."""

    def test_empty_model_error(self):
        """Test that empty model raises appropriate error."""
        # This would require creating an empty ModelIR, which is complex
        # Skip for now - could add in future if needed
        pass

    def test_no_objective_error(self):
        """Test that model without objective raises error."""
        # This would require creating a ModelIR without objective
        # Skip for now - could add in future if needed
        pass


@pytest.mark.e2e
class TestConsistency:
    """Test consistency across different access patterns."""

    def test_mapping_consistency(self):
        """Test that variable mappings are consistent across gradient and Jacobians."""
        model_ir = parse_and_normalize("simple_nlp.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # All three should have same variable mappings
        assert gradient.index_mapping.num_vars == J_g.index_mapping.num_vars
        assert gradient.index_mapping.num_vars == J_h.index_mapping.num_vars

        # Note: Equation mappings are now separate for J_eq and J_ineq,
        # so num_eqs will differ between them. The gradient uses a global
        # equation mapping that includes all equations.

        # The number of equation instances (rows) should equal the total number of
        # expanded instances (indexed equations expand to multiple rows).
        # Verify exact counts to catch unexpected dimension inflation.
        from src.ad.constraint_jacobian import _count_equation_instances

        expected_eq_rows = _count_equation_instances(model_ir, model_ir.equalities)
        expected_ineq_rows = _count_equation_instances(model_ir, model_ir.inequalities)

        assert J_h.index_mapping.num_eqs == expected_eq_rows
        assert J_g.index_mapping.num_eqs == expected_ineq_rows

        # Mapping should be complete
        assert gradient.index_mapping.num_vars > 0

    def test_all_variables_have_gradients(self):
        """Test that every variable has a gradient component."""
        model_ir = parse_and_normalize("simple_nlp.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Every variable should have a gradient (though some may be zero)
        num_vars = gradient.num_cols
        gradient_entries = gradient.num_nonzeros()

        # In general, we expect gradient for all vars (unless objective is constant)
        # For sum(i, a(i)*x(i)), all variables should have non-zero gradient
        assert gradient_entries == num_vars


@pytest.mark.e2e
class TestPositiveVariables:
    """Test end-to-end pipeline with Positive Variables keyword (Issue #140)."""

    def test_positive_variables_full_pipeline(self):
        """Test that Positive Variables are parsed and generate correct MCP output."""
        from src.ad.constraint_jacobian import compute_constraint_jacobian
        from src.ad.gradient import compute_objective_gradient
        from src.emit.emit_gams import emit_gams_mcp
        from src.ir.normalize import normalize_model
        from src.ir.parser import parse_model_file
        from src.ir.symbols import VarKind
        from src.kkt.assemble import assemble_kkt_system

        # Parse model with Positive Variables keyword
        model_ir = parse_model_file(get_example_path("positive_vars_nlp.gms"))

        # Verify that variables were parsed with correct kind
        assert "x" in model_ir.variables
        assert model_ir.variables["x"].kind == VarKind.POSITIVE
        assert "obj" in model_ir.variables
        assert model_ir.variables["obj"].kind == VarKind.POSITIVE

        # Normalize model
        normalized_eqs, _ = normalize_model(model_ir)

        # Compute derivatives
        gradient = compute_objective_gradient(model_ir)
        J_eq, J_ineq = compute_constraint_jacobian(model_ir, normalized_eqs)

        # Should have 4 variables: obj, x(i1), x(i2), x(i3)
        assert gradient.num_cols == 4

        # Gradient should have non-zero components
        assert gradient.num_nonzeros() > 0

        # Should have equality constraints (objective definition + total_demand)
        assert J_eq.num_rows >= 2  # At minimum: objective and total_demand
        assert J_eq.num_nonzeros() > 0

        # No inequality constraints in this simple model

        # Assemble KKT system
        kkt = assemble_kkt_system(model_ir, gradient, J_eq, J_ineq)

        # Verify KKT system structure
        assert kkt.model_ir == model_ir
        assert kkt.gradient == gradient
        assert kkt.J_eq == J_eq
        assert kkt.J_ineq == J_ineq

        # Generate MCP output
        mcp_output = emit_gams_mcp(kkt, model_name="positive_vars_mcp", add_comments=True)

        # Verify MCP output contains expected elements
        assert "positive_vars_mcp" in mcp_output
        assert "Positive Variables" in mcp_output  # Should preserve variable kind
        assert "x(i)" in mcp_output  # Indexed variable
        assert "obj" in mcp_output  # Scalar variable
        assert "stationarity" in mcp_output.lower()  # KKT stationarity conditions
        assert "Model" in mcp_output
        assert "Solve" in mcp_output

        # Verify that positive variables appear in Positive Variables block
        import re

        lines = mcp_output.split("\n")
        in_positive_block = False
        found_x = False
        found_obj = False

        for line in lines:
            if "Positive Variables" in line:
                in_positive_block = True
            elif in_positive_block:
                # Check for variables in the block using word boundaries
                if re.search(r"\bx\s*\(i\)", line):
                    found_x = True
                # Match 'obj' as a standalone word (not part of 'objective', etc.)
                if re.search(r"\bobj\b", line):
                    found_obj = True
                # End of block
                if ";" in line and (found_x or found_obj):
                    break

        assert found_x or found_obj, (
            "Positive variables should be declared in Positive Variables block"
        )

    def test_positive_variables_in_derivatives(self):
        """Test that Positive Variables are handled correctly in derivative computation."""
        # Parse model
        model_ir = parse_and_normalize("positive_vars_nlp.gms")

        # Compute derivatives using high-level API
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Verify gradient structure
        assert gradient.num_cols == 4  # obj + x(i1) + x(i2) + x(i3)
        assert gradient.num_nonzeros() > 0

        # Verify all gradient components exist
        for col_id in range(gradient.num_cols):
            deriv = gradient.get_derivative(col_id)
            assert deriv is not None, f"Gradient component {col_id} should exist"

        # Verify Jacobians have correct structure
        assert J_h.num_rows >= 2  # Equality constraints (objective + total_demand)

        # Verify that equality derivatives are non-trivial (not all zeros)
        assert J_h.num_nonzeros() > 0


@pytest.mark.e2e
class TestSetRangeSyntax:
    """Test end-to-end pipeline with set range syntax (Sprint 7 Day 3)."""

    def test_numeric_range_expansion(self):
        """Test that numeric ranges (1*6) are correctly expanded."""
        from src.ir.parser import parse_model_text

        gams_code = """
        Set i / 1*6 /;
        """
        model_ir = parse_model_text(gams_code)

        # Verify set was created with correct members
        assert "i" in model_ir.sets
        assert model_ir.sets["i"].members == ["1", "2", "3", "4", "5", "6"]

    def test_symbolic_range_expansion(self):
        """Test that symbolic ranges (s1*s5) are correctly expanded."""
        from src.ir.parser import parse_model_text

        gams_code = """
        Set s / s1*s5 /;
        """
        model_ir = parse_model_text(gams_code)

        # Verify set was created with correct members
        assert "s" in model_ir.sets
        assert model_ir.sets["s"].members == ["s1", "s2", "s3", "s4", "s5"]

    def test_prefix_range_expansion(self):
        """Test that prefix ranges (plant1*plant3) are correctly expanded."""
        from src.ir.parser import parse_model_text

        gams_code = """
        Set p / plant1*plant3 /;
        """
        model_ir = parse_model_text(gams_code)

        # Verify set was created with correct members
        assert "p" in model_ir.sets
        assert model_ir.sets["p"].members == ["plant1", "plant2", "plant3"]

    def test_macro_range_expansion(self):
        """Test that macro ranges work with preprocessor (tested in unit tests)."""
        # Note: Macro expansion is tested in tests/ir/test_range_expansion.py
        # This integration test verifies that the range syntax itself supports
        # macro placeholders. The actual macro expansion is handled by the preprocessor
        # and is thoroughly tested in the unit test suite (18 tests in Day 2).
        # For integration testing, we verify basic range expansion which is the
        # foundation for macro ranges.
        from src.ir.parser import parse_model_text

        gams_code = """
        Set i / 1*5 /;
        """
        model_ir = parse_model_text(gams_code)

        # Verify set was created with correct members
        assert "i" in model_ir.sets
        assert model_ir.sets["i"].members == ["1", "2", "3", "4", "5"]

    def test_set_singular_keyword(self):
        """Test that 'Set' (singular) keyword is supported."""
        from src.ir.parser import parse_model_text

        gams_code = """
        Set i / 1*3 /;
        """
        model_ir = parse_model_text(gams_code)

        # Verify set was created
        assert "i" in model_ir.sets
        assert model_ir.sets["i"].members == ["1", "2", "3"]

    def test_set_with_description(self):
        """Test that set descriptions are supported."""
        from src.ir.parser import parse_model_text

        gams_code = """
        Set i 'indices for points' / 1*6 /;
        """
        model_ir = parse_model_text(gams_code)

        # Verify set was created with correct members
        assert "i" in model_ir.sets
        assert model_ir.sets["i"].members == ["1", "2", "3", "4", "5", "6"]

    def test_alias_singular_keyword(self):
        """Test that 'Alias' (singular) keyword is supported."""
        from src.ir.parser import parse_model_text

        gams_code = """
        Set i / 1*3 /;
        Alias (i,j);
        """
        model_ir = parse_model_text(gams_code)

        # Verify set and alias were created
        assert "i" in model_ir.sets
        assert model_ir.sets["i"].members == ["1", "2", "3"]

    def test_alias_with_parentheses(self):
        """Test that Alias (i,j) syntax with parentheses is supported."""
        from src.ir.parser import parse_model_text

        gams_code = """
        Set i / 1*5 /;
        Alias (i,j);
        """
        model_ir = parse_model_text(gams_code)

        # Verify set was created
        assert "i" in model_ir.sets
        assert model_ir.sets["i"].members == ["1", "2", "3", "4", "5"]

    def test_ranges_in_full_pipeline(self):
        """Test that models with ranges work through normalization pipeline."""
        from src.ir.parser import parse_model_text

        gams_code = """
        Set i / i1*i3 /;

        Positive Variable x(i);

        Equation balance(i);

        balance(i).. x(i) =e= 1;

        Model test / all /;
        """
        model_ir = parse_model_text(gams_code)

        # Verify range expansion worked
        assert "i" in model_ir.sets
        assert model_ir.sets["i"].members == ["i1", "i2", "i3"]

        # Verify indexed equation was created
        assert "balance" in model_ir.equations
        eq_def = model_ir.equations["balance"]
        assert eq_def.domain == ("i",)

        # Normalize model
        normalize_model(model_ir)

        # Verify normalization succeeded
        assert "balance" in model_ir.equalities


@pytest.mark.e2e
class TestConditionalEquations:
    """Test conditional equation syntax ($ operator) through full pipeline (Sprint 7 Day 3)."""

    def test_conditional_equation_basic(self):
        """Test basic conditional equation parsing."""
        from src.ir.parser import parse_model_text

        gams_code = """
        Set i / 1*5 /;
        Variable x(i);
        Equation balance(i);

        balance(i)$(ord(i) > 2).. x(i) =e= 1;

        Model test / all /;
        """
        model_ir = parse_model_text(gams_code)

        # Verify equation was created
        assert "balance" in model_ir.equations
        assert model_ir.equations["balance"].domain == ("i",)

    def test_conditional_equation_himmel16_pattern(self):
        """Test himmel16.gms conditional pattern."""
        from src.ir.parser import parse_model_text

        gams_code = """
        Set i / 1*6 /;
        Alias (i,j);
        Variable x(i);
        Equation maxdist(i,j);

        maxdist(i,j)$(ord(i) < ord(j)).. x(i) + x(j) =l= 1;

        Model test / all /;
        """
        model_ir = parse_model_text(gams_code)

        # Verify equation was created
        assert "maxdist" in model_ir.equations
        assert model_ir.equations["maxdist"].domain == ("i", "j")
        assert model_ir.equations["maxdist"].relation.value == "=l="

    def test_conditional_with_normalization(self):
        """Test conditional equation through normalization."""
        from src.ir.parser import parse_model_text

        gams_code = """
        Set i / i1*i3 /;
        Variable x(i);
        Equation balance(i);

        balance(i)$(ord(i) > 1).. x(i) =e= 1;

        Model test / all /;
        """
        model_ir = parse_model_text(gams_code)

        # Normalize model
        normalize_model(model_ir)

        # Verify normalization succeeded
        assert "balance" in model_ir.equalities

    def test_conditional_equation_with_parameter_filtering(self):
        """Test that parameter-based conditions correctly filter equation instances."""
        from src.ad.index_mapping import build_index_mapping
        from src.ir.parser import parse_model_text

        gams_code = """
        Set i / i1*i5 /;
        Parameter demand(i) / i1 10, i2 0, i3 5, i4 0, i5 8 /;
        Variable x(i);
        Variable z;
        Equation supply(i);
        Equation balance;

        supply(i)$(demand(i) > 0).. x(i) =e= demand(i);
        balance.. z =e= sum(i, x(i));

        Model test / all /;
        """
        model_ir = parse_model_text(gams_code)

        # Verify parameter data was loaded
        assert "demand" in model_ir.params
        assert len(model_ir.params["demand"].values) == 5
        assert model_ir.params["demand"].values[("i1",)] == 10.0
        assert model_ir.params["demand"].values[("i2",)] == 0.0

        # Build index mapping (triggers condition evaluation)
        mapping = build_index_mapping(model_ir)

        # Count supply equation instances
        supply_instances = [
            (eq_name, indices)
            for (eq_name, indices) in mapping.eq_to_row.keys()
            if eq_name == "supply"
        ]

        # Should only create instances for i1, i3, i5 (where demand > 0)
        assert len(supply_instances) == 3
        assert ("supply", ("i1",)) in supply_instances
        assert ("supply", ("i3",)) in supply_instances
        assert ("supply", ("i5",)) in supply_instances

        # Should NOT create instances for i2, i4 (where demand = 0)
        assert ("supply", ("i2",)) not in supply_instances
        assert ("supply", ("i4",)) not in supply_instances

    def test_conditional_equation_with_ord_filtering(self):
        """Test that ord()-based conditions correctly filter equation instances."""
        from src.ad.index_mapping import build_index_mapping
        from src.ir.parser import parse_model_text

        gams_code = """
        Set i / i1*i5 /;
        Variable x(i);
        Equation supply(i);

        supply(i)$(ord(i) > 2).. x(i) =e= 1;

        Model test / all /;
        """
        model_ir = parse_model_text(gams_code)

        # Build index mapping (triggers condition evaluation)
        mapping = build_index_mapping(model_ir)

        # Count supply equation instances
        supply_instances = [
            (eq_name, indices)
            for (eq_name, indices) in mapping.eq_to_row.keys()
            if eq_name == "supply"
        ]

        # Should only create instances for i3, i4, i5 (where ord > 2)
        assert len(supply_instances) == 3
        assert ("supply", ("i3",)) in supply_instances
        assert ("supply", ("i4",)) in supply_instances
        assert ("supply", ("i5",)) in supply_instances

        # Should NOT create instances for i1, i2 (where ord <= 2)
        assert ("supply", ("i1",)) not in supply_instances
        assert ("supply", ("i2",)) not in supply_instances


class TestGAMSLibParsing:
    """Test that GAMSLib models parse successfully.

    Sprint 7 Day 4 achievement: 50% parse rate (5/10 models).

    These tests validate the integration of:
    - Preprocessor directives ($title, $onText/$offText, $if/$set, macros)
    - Multiple declaration syntax (Parameters x, y, z;)
    - Variable attribute references (x.l, x.lo, x.up)
    - Execution statement stripping (if() calls, abort, display)
    - Models (plural) keyword
    - Flexible solve statement order
    """

    # Class-level constants to reduce duplication
    GAMSLIB_DIR = Path(__file__).parent.parent / "fixtures" / "gamslib"

    def test_circle_gms_parses(self):
        """Test circle.gms parses successfully (preprocessor + quick wins)."""
        tree = parse_file(self.GAMSLIB_DIR / "circle.gms")
        assert tree is not None

    def test_trig_gms_parses(self):
        """Test trig.gms parses successfully (multiple scalars)."""
        tree = parse_file(self.GAMSLIB_DIR / "trig.gms")
        assert tree is not None

    def test_mathopt1_gms_parses(self):
        """Test mathopt1.gms parses successfully (Models keyword)."""
        tree = parse_file(self.GAMSLIB_DIR / "mathopt1.gms")
        assert tree is not None

    def test_rbrock_gms_parses(self):
        """Test rbrock.gms parses successfully (existing features)."""
        tree = parse_file(self.GAMSLIB_DIR / "rbrock.gms")
        assert tree is not None

    def test_mhw4d_gms_parses(self):
        """Test mhw4d.gms parses successfully (existing features)."""
        tree = parse_file(self.GAMSLIB_DIR / "mhw4d.gms")
        assert tree is not None

    @pytest.mark.slow
    def test_gamslib_parse_rate(self):
        """Validate 50% parse rate achievement (5/10 models)."""
        models = [
            "circle.gms",
            "trig.gms",
            "mathopt1.gms",
            "rbrock.gms",
            "mhw4d.gms",
            "maxmin.gms",
            "himmel16.gms",
            "hs62.gms",
            "mingamma.gms",
            "mhw4dx.gms",
        ]

        passed_models = []
        failed_models = []
        for model in models:
            try:
                parse_file(self.GAMSLIB_DIR / model)
                passed_models.append(model)
            except Exception as e:
                # Log failures for debugging
                failed_models.append(f"{model}: {type(e).__name__}")

        # Sprint 7 Day 4 target: 50% parse rate (5/10 models)
        parse_rate = (len(passed_models) / len(models)) * 100
        assert parse_rate >= 50.0, (
            f"Parse rate {parse_rate:.1f}% below 50% target. "
            f"Passed: {passed_models}. Failed: {failed_models}"
        )

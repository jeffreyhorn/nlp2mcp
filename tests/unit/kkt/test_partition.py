"""Unit tests for constraint partitioning."""

import pytest

from src.ir.ast import Const, IndexOffset, ParamRef, SubsetIndex
from src.ir.model_ir import ModelIR
from src.ir.symbols import SetDef, VariableDef, VarKind
from src.kkt.partition import partition_constraints


@pytest.mark.unit
class TestPartitionConstraints:
    """Tests for partition_constraints function."""

    def test_empty_model(self):
        """Empty model should return empty partition."""
        model = ModelIR()
        result = partition_constraints(model)

        assert result.equalities == []
        assert result.inequalities == []
        assert result.bounds_lo == {}
        assert result.bounds_up == {}
        assert result.bounds_fx == {}
        assert result.skipped_infinite == []
        assert result.duplicate_excluded == []

    def test_equalities_only(self):
        """Model with only equality constraints."""
        model = ModelIR()
        model.equalities = ["balance", "flow"]

        result = partition_constraints(model)

        assert result.equalities == ["balance", "flow"]
        assert result.inequalities == []

    def test_inequalities_only(self):
        """Model with only inequality constraints."""
        model = ModelIR()
        model.inequalities = ["capacity", "demand"]

        result = partition_constraints(model)

        assert result.equalities == []
        assert result.inequalities == ["capacity", "demand"]

    def test_mixed_constraints(self):
        """Model with both equalities and inequalities."""
        model = ModelIR()
        model.equalities = ["balance"]
        model.inequalities = ["capacity", "demand"]

        result = partition_constraints(model)

        assert result.equalities == ["balance"]
        assert result.inequalities == ["capacity", "demand"]

    def test_scalar_lower_bound(self):
        """Variable with scalar lower bound."""
        model = ModelIR()
        model.variables["x"] = VariableDef(name="x", lo=0.0)

        result = partition_constraints(model)

        assert ("x", ()) in result.bounds_lo
        assert result.bounds_lo[("x", ())].kind == "lo"
        assert result.bounds_lo[("x", ())].value == 0.0

    def test_scalar_upper_bound(self):
        """Variable with scalar upper bound."""
        model = ModelIR()
        model.variables["x"] = VariableDef(name="x", up=10.0)

        result = partition_constraints(model)

        assert ("x", ()) in result.bounds_up
        assert result.bounds_up[("x", ())].kind == "up"
        assert result.bounds_up[("x", ())].value == 10.0

    def test_scalar_both_bounds(self):
        """Variable with both lower and upper bounds."""
        model = ModelIR()
        model.variables["x"] = VariableDef(name="x", lo=0.0, up=10.0)

        result = partition_constraints(model)

        assert ("x", ()) in result.bounds_lo
        assert ("x", ()) in result.bounds_up
        assert result.bounds_lo[("x", ())].value == 0.0
        assert result.bounds_up[("x", ())].value == 10.0

    def test_scalar_fixed_value(self):
        """Variable with fixed value."""
        model = ModelIR()
        model.variables["x"] = VariableDef(name="x", fx=5.0)

        result = partition_constraints(model)

        assert ("x", ()) in result.bounds_fx
        assert result.bounds_fx[("x", ())].value == 5.0

    def test_infinite_lower_bound_skipped(self):
        """Variable with -INF lower bound should be skipped."""
        model = ModelIR()
        model.variables["x"] = VariableDef(name="x", lo=float("-inf"))

        result = partition_constraints(model)

        assert ("x", ()) not in result.bounds_lo
        assert ("x", (), "lo") in result.skipped_infinite

    def test_infinite_upper_bound_skipped(self):
        """Variable with +INF upper bound should be skipped."""
        model = ModelIR()
        model.variables["x"] = VariableDef(name="x", up=float("inf"))

        result = partition_constraints(model)

        assert ("x", ()) not in result.bounds_up
        assert ("x", (), "up") in result.skipped_infinite

    def test_indexed_lower_bound(self):
        """Variable with indexed lower bounds."""
        model = ModelIR()
        var = VariableDef(name="x", domain=("i",))
        var.lo_map[("i1",)] = 0.0
        var.lo_map[("i2",)] = 1.0
        model.variables["x"] = var

        result = partition_constraints(model)

        assert ("x", ("i1",)) in result.bounds_lo
        assert ("x", ("i2",)) in result.bounds_lo
        assert result.bounds_lo[("x", ("i1",))].value == 0.0
        assert result.bounds_lo[("x", ("i2",))].value == 1.0

    def test_indexed_upper_bound(self):
        """Variable with indexed upper bounds."""
        model = ModelIR()
        var = VariableDef(name="x", domain=("i",))
        var.up_map[("i1",)] = 10.0
        var.up_map[("i2",)] = 20.0
        model.variables["x"] = var

        result = partition_constraints(model)

        assert ("x", ("i1",)) in result.bounds_up
        assert ("x", ("i2",)) in result.bounds_up
        assert result.bounds_up[("x", ("i1",))].value == 10.0
        assert result.bounds_up[("x", ("i2",))].value == 20.0

    def test_indexed_infinite_bound_skipped(self):
        """Indexed variable with infinite bound should be skipped."""
        model = ModelIR()
        var = VariableDef(name="x", domain=("i",))
        var.lo_map[("i1",)] = 0.0
        var.lo_map[("i2",)] = float("-inf")
        model.variables["x"] = var

        result = partition_constraints(model)

        assert ("x", ("i1",)) in result.bounds_lo
        assert ("x", ("i2",)) not in result.bounds_lo
        assert ("x", ("i2",), "lo") in result.skipped_infinite

    def test_mixed_scalar_and_indexed_bounds(self):
        """Variable with both scalar and indexed bounds."""
        model = ModelIR()
        var = VariableDef(name="x", domain=("i",), lo=0.0)
        var.lo_map[("i1",)] = 1.0
        model.variables["x"] = var

        result = partition_constraints(model)

        # Both scalar and indexed bounds should be present
        assert ("x", ()) in result.bounds_lo
        assert ("x", ("i1",)) in result.bounds_lo
        assert result.bounds_lo[("x", ())].value == 0.0
        assert result.bounds_lo[("x", ("i1",))].value == 1.0

    def test_multiple_variables_with_bounds(self):
        """Multiple variables with different bounds."""
        model = ModelIR()
        model.variables["x"] = VariableDef(name="x", lo=0.0, up=10.0)
        model.variables["y"] = VariableDef(name="y", lo=5.0)
        model.variables["z"] = VariableDef(name="z", up=20.0)

        result = partition_constraints(model)

        assert ("x", ()) in result.bounds_lo
        assert ("x", ()) in result.bounds_up
        assert ("y", ()) in result.bounds_lo
        assert ("y", ()) not in result.bounds_up
        assert ("z", ()) not in result.bounds_lo
        assert ("z", ()) in result.bounds_up

    def test_normalized_bounds_excluded_from_inequalities(self):
        """Normalized bounds should not appear in inequalities list."""
        model = ModelIR()
        model.inequalities = ["capacity", "x_lo_bound", "x_up_bound"]
        model.normalized_bounds = {"x_lo_bound": None, "x_up_bound": None}

        result = partition_constraints(model)

        assert result.inequalities == ["capacity"]
        assert "x_lo_bound" not in result.inequalities
        assert "x_up_bound" not in result.inequalities

    def test_uniform_bounds_consolidate_to_indexed(self):
        """Uniform bounds covering all instances should consolidate to (var, ()).

        When all elements of an indexed variable have the same bound value
        (e.g., x.lo(c) = 0.001 for all c), consolidate to a single indexed entry.
        """
        model = ModelIR()
        # Define set with members
        from src.ir.symbols import SetDef

        model.sets["c"] = SetDef(name="c", members=["H", "H2", "H2O"])

        # Create variable with uniform lower bounds for all instances
        var = VariableDef(name="x", domain=("c",))
        var.lo_map[("H",)] = 0.001
        var.lo_map[("H2",)] = 0.001
        var.lo_map[("H2O",)] = 0.001
        model.variables["x"] = var

        result = partition_constraints(model)

        # Should consolidate to single indexed entry with () indices
        assert ("x", ()) in result.bounds_lo
        assert result.bounds_lo[("x", ())].value == 0.001
        assert result.bounds_lo[("x", ())].domain == ("c",)
        # Should NOT have per-instance entries
        assert ("x", ("H",)) not in result.bounds_lo
        assert ("x", ("H2",)) not in result.bounds_lo
        assert ("x", ("H2O",)) not in result.bounds_lo

    def test_partial_bounds_not_consolidated(self):
        """Partial bounds (subset of instances) should NOT consolidate.

        When only some elements have bounds (e.g., x.lo(subset) = 0.001),
        do NOT consolidate - keep per-instance entries.
        """
        model = ModelIR()
        # Define set with 3 members
        from src.ir.symbols import SetDef

        model.sets["c"] = SetDef(name="c", members=["H", "H2", "H2O"])

        # Create variable with bounds only for a subset of instances
        var = VariableDef(name="x", domain=("c",))
        var.lo_map[("H",)] = 0.001
        var.lo_map[("H2",)] = 0.001
        # H2O is NOT bounded
        model.variables["x"] = var

        result = partition_constraints(model)

        # Should NOT consolidate - keep per-instance entries
        assert ("x", ()) not in result.bounds_lo
        assert ("x", ("H",)) in result.bounds_lo
        assert ("x", ("H2",)) in result.bounds_lo
        assert result.bounds_lo[("x", ("H",))].value == 0.001
        assert result.bounds_lo[("x", ("H2",))].value == 0.001

    def test_uniform_upper_bounds_consolidate(self):
        """Uniform upper bounds covering all instances should consolidate."""
        model = ModelIR()
        from src.ir.symbols import SetDef

        model.sets["i"] = SetDef(name="i", members=["a", "b"])

        var = VariableDef(name="y", domain=("i",))
        var.up_map[("a",)] = 100.0
        var.up_map[("b",)] = 100.0
        model.variables["y"] = var

        result = partition_constraints(model)

        # Should consolidate to single indexed entry
        assert ("y", ()) in result.bounds_up
        assert result.bounds_up[("y", ())].value == 100.0
        assert ("y", ("a",)) not in result.bounds_up
        assert ("y", ("b",)) not in result.bounds_up

    def test_alias_indexed_uniform_bounds_consolidate(self):
        """Uniform bounds on alias-indexed variable should consolidate.

        When a variable is indexed over an alias (not a direct set), the
        coverage check should still work correctly via resolve_set_members().
        """
        model = ModelIR()
        from src.ir.symbols import AliasDef, SetDef

        # Define base set
        model.sets["i"] = SetDef(name="i", members=["a", "b", "c"])
        # Define alias over the set
        model.aliases["j"] = AliasDef(name="j", target="i")

        # Create variable indexed over the ALIAS (not the set directly)
        var = VariableDef(name="x", domain=("j",))
        var.lo_map[("a",)] = 0.5
        var.lo_map[("b",)] = 0.5
        var.lo_map[("c",)] = 0.5
        model.variables["x"] = var

        result = partition_constraints(model)

        # Should consolidate to single indexed entry even though domain is alias
        assert ("x", ()) in result.bounds_lo
        assert result.bounds_lo[("x", ())].value == 0.5
        assert result.bounds_lo[("x", ())].domain == ("j",)
        # Should NOT have per-instance entries
        assert ("x", ("a",)) not in result.bounds_lo
        assert ("x", ("b",)) not in result.bounds_lo
        assert ("x", ("c",)) not in result.bounds_lo

    def test_list_backed_set_uniform_bounds_consolidate(self):
        """Uniform bounds with list-backed set should consolidate.

        Some tests use plain lists instead of SetDef objects for sets.
        The coverage check should handle this via resolve_set_members().
        """
        model = ModelIR()

        # Use a plain list instead of SetDef (as some tests do)
        model.sets["i"] = ["x1", "x2"]

        var = VariableDef(name="y", domain=("i",))
        var.lo_map[("x1",)] = 1.0
        var.lo_map[("x2",)] = 1.0
        model.variables["y"] = var

        result = partition_constraints(model)

        # Should consolidate to single indexed entry
        assert ("y", ()) in result.bounds_lo
        assert result.bounds_lo[("y", ())].value == 1.0
        assert ("y", ("x1",)) not in result.bounds_lo
        assert ("y", ("x2",)) not in result.bounds_lo

    def test_infinite_scalar_bound_allows_consolidation(self):
        """Infinite scalar bound should not block uniform consolidation.

        When a variable has an infinite scalar bound (e.g., lo=-inf),
        it is skipped by partition_constraints(). The indexed bounds
        should still consolidate if they are uniform.
        """
        model = ModelIR()
        from src.ir.symbols import SetDef

        model.sets["i"] = SetDef(name="i", members=["a", "b"])

        # Variable with infinite scalar lower bound AND uniform indexed lower bounds
        var = VariableDef(name="x", domain=("i",), lo=float("-inf"))
        var.lo_map[("a",)] = 0.5
        var.lo_map[("b",)] = 0.5
        model.variables["x"] = var

        result = partition_constraints(model)

        # Scalar -inf bound should be skipped
        assert ("x", (), "lo") in result.skipped_infinite
        # Indexed bounds should consolidate (infinite scalar doesn't block it)
        assert ("x", ()) in result.bounds_lo
        assert result.bounds_lo[("x", ())].value == 0.5
        assert ("x", ("a",)) not in result.bounds_lo
        assert ("x", ("b",)) not in result.bounds_lo


@pytest.mark.unit
class TestVarKindImplicitBounds:
    """Tests for VarKind implicit bound synthesis (Issue #922)."""

    def test_positive_no_explicit_bounds(self):
        """VarKind.POSITIVE with no explicit bounds should synthesize lo=0."""
        model = ModelIR()
        model.variables["x"] = VariableDef(name="x", kind=VarKind.POSITIVE)

        result = partition_constraints(model)

        assert ("x", ()) in result.bounds_lo
        assert result.bounds_lo[("x", ())].value == 0.0
        assert ("x", ()) not in result.bounds_up

    def test_negative_no_explicit_bounds(self):
        """VarKind.NEGATIVE with no explicit bounds should synthesize up=0."""
        model = ModelIR()
        model.variables["x"] = VariableDef(name="x", kind=VarKind.NEGATIVE)

        result = partition_constraints(model)

        assert ("x", ()) in result.bounds_up
        assert result.bounds_up[("x", ())].value == 0.0
        assert ("x", ()) not in result.bounds_lo

    def test_binary_no_explicit_bounds(self):
        """VarKind.BINARY with no explicit bounds should synthesize lo=0, up=1."""
        model = ModelIR()
        model.variables["x"] = VariableDef(name="x", kind=VarKind.BINARY)

        result = partition_constraints(model)

        assert ("x", ()) in result.bounds_lo
        assert result.bounds_lo[("x", ())].value == 0.0
        assert ("x", ()) in result.bounds_up
        assert result.bounds_up[("x", ())].value == 1.0

    def test_positive_with_explicit_scalar_lo(self):
        """VarKind.POSITIVE with explicit scalar lo should NOT synthesize."""
        model = ModelIR()
        model.variables["x"] = VariableDef(name="x", kind=VarKind.POSITIVE, lo=5.0)

        result = partition_constraints(model)

        assert ("x", ()) in result.bounds_lo
        assert result.bounds_lo[("x", ())].value == 5.0  # Explicit, not implicit 0

    def test_positive_with_indexed_lo_map_only(self):
        """VarKind.POSITIVE with only indexed lo_map should still synthesize base lo=0.

        Indexed bounds may only cover a subset of indices, so uncovered
        indices still need the implicit lo=0 from VarKind.POSITIVE.
        """
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["a", "b", "c"])

        var = VariableDef(name="x", domain=("i",), kind=VarKind.POSITIVE)
        var.lo_map[("a",)] = 1.0  # Only covers 'a', not 'b' or 'c'
        model.variables["x"] = var

        result = partition_constraints(model)

        # Should have per-instance entry for 'a' AND implicit base lo=0
        assert ("x", ("a",)) in result.bounds_lo
        assert result.bounds_lo[("x", ("a",))].value == 1.0
        assert ("x", ()) in result.bounds_lo
        assert result.bounds_lo[("x", ())].value == 0.0

    def test_positive_with_consolidated_indexed_lo_not_overwritten(self):
        """VarKind.POSITIVE with uniform indexed bounds should NOT be overwritten.

        When all indexed bounds consolidate to (var, ()) with value 1.0,
        the implicit lo=0 should NOT overwrite that consolidated entry.
        """
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["a", "b"])

        var = VariableDef(name="x", domain=("i",), kind=VarKind.POSITIVE)
        var.lo_map[("a",)] = 1.0
        var.lo_map[("b",)] = 1.0
        model.variables["x"] = var

        result = partition_constraints(model)

        # Consolidated entry should have value 1.0, NOT implicit 0.0
        assert ("x", ()) in result.bounds_lo
        assert result.bounds_lo[("x", ())].value == 1.0

    def test_binary_with_explicit_lo_only(self):
        """VarKind.BINARY with only explicit lo should synthesize up=1 only."""
        model = ModelIR()
        model.variables["x"] = VariableDef(name="x", kind=VarKind.BINARY, lo=0.0)

        result = partition_constraints(model)

        assert ("x", ()) in result.bounds_lo
        assert result.bounds_lo[("x", ())].value == 0.0  # Explicit
        assert ("x", ()) in result.bounds_up
        assert result.bounds_up[("x", ())].value == 1.0  # Synthesized

    def test_continuous_no_implicit_bounds(self):
        """VarKind.CONTINUOUS should NOT get implicit bounds."""
        model = ModelIR()
        model.variables["x"] = VariableDef(name="x", kind=VarKind.CONTINUOUS)

        result = partition_constraints(model)

        assert ("x", ()) not in result.bounds_lo
        assert ("x", ()) not in result.bounds_up

    def test_positive_with_fx_skips_implicit_lo(self):
        """VarKind.POSITIVE with .fx should NOT synthesize implicit lo=0."""
        model = ModelIR()
        model.variables["x"] = VariableDef(name="x", kind=VarKind.POSITIVE, fx=5.0)

        result = partition_constraints(model)

        assert ("x", ()) in result.bounds_fx
        assert result.bounds_fx[("x", ())].value == 5.0
        assert ("x", ()) not in result.bounds_lo  # No redundant implicit lo

    def test_binary_with_fx_skips_implicit_bounds(self):
        """VarKind.BINARY with .fx should NOT synthesize implicit lo=0 or up=1."""
        model = ModelIR()
        model.variables["x"] = VariableDef(name="x", kind=VarKind.BINARY, fx=1.0)

        result = partition_constraints(model)

        assert ("x", ()) in result.bounds_fx
        assert result.bounds_fx[("x", ())].value == 1.0
        assert ("x", ()) not in result.bounds_lo  # No redundant implicit lo
        assert ("x", ()) not in result.bounds_up  # No redundant implicit up


@pytest.mark.unit
class TestExpressionBasedBounds:
    """Tests for expression-based bounds in partition (Issue #923)."""

    def test_scalar_lo_expr_creates_bound(self):
        """Scalar lo_expr should produce a bounds_lo entry with expr."""
        model = ModelIR()
        var = VariableDef(name="e", domain=("t",))
        var.lo_expr = ParamRef("req", indices=("t",))
        model.variables["e"] = var

        result = partition_constraints(model)

        assert ("e", ()) in result.bounds_lo
        bound = result.bounds_lo[("e", ())]
        assert bound.expr is not None
        assert isinstance(bound.expr, ParamRef)
        assert bound.domain == ("t",)

    def test_scalar_up_expr_creates_bound(self):
        """Scalar up_expr should produce a bounds_up entry with expr."""
        model = ModelIR()
        var = VariableDef(name="y", domain=("j",))
        var.up_expr = ParamRef("deltb", indices=("j",))
        model.variables["y"] = var

        result = partition_constraints(model)

        assert ("y", ()) in result.bounds_up
        bound = result.bounds_up[("y", ())]
        assert bound.expr is not None

    def test_lo_expr_map_single_entry_domain_match(self):
        """lo_expr_map with single entry matching domain should consolidate."""
        model = ModelIR()
        var = VariableDef(name="e", domain=("t",))
        var.lo_expr_map = {("t",): ParamRef("req", indices=("t",))}
        model.variables["e"] = var

        result = partition_constraints(model)

        assert ("e", ()) in result.bounds_lo
        bound = result.bounds_lo[("e", ())]
        assert bound.expr is not None
        assert isinstance(bound.expr, ParamRef)

    def test_lo_expr_map_index_offset_skipped(self):
        """lo_expr_map with IndexOffset key should be skipped."""
        model = ModelIR()
        var = VariableDef(name="x", domain=("t",))
        offset_key = IndexOffset(base="t", offset=Const(1), circular=False)
        var.lo_expr_map = {(offset_key,): ParamRef("p", indices=("t",))}
        model.variables["x"] = var

        result = partition_constraints(model)

        # Should NOT have created a bound entry
        assert ("x", ()) not in result.bounds_lo

    def test_lo_expr_map_subset_index_skipped(self):
        """lo_expr_map with SubsetIndex key should be skipped."""
        model = ModelIR()
        var = VariableDef(name="x", domain=("i",))
        subset_key = SubsetIndex(subset_name="s", indices=("i",))
        var.lo_expr_map = {(subset_key,): ParamRef("p", indices=("i",))}
        model.variables["x"] = var

        result = partition_constraints(model)

        assert ("x", ()) not in result.bounds_lo

    def test_lo_expr_map_multiple_entries_skipped(self):
        """lo_expr_map with multiple entries should be skipped."""
        model = ModelIR()
        var = VariableDef(name="x", domain=("t",))
        var.lo_expr_map = {
            ("t",): ParamRef("req", indices=("t",)),
            ("s",): ParamRef("other", indices=("s",)),
        }
        model.variables["x"] = var

        result = partition_constraints(model)

        assert ("x", ()) not in result.bounds_lo

    def test_numeric_lo_takes_precedence_over_lo_expr(self):
        """Numeric lo bound takes precedence over lo_expr."""
        model = ModelIR()
        var = VariableDef(name="e", domain=("t",), lo=0.0)
        var.lo_expr = ParamRef("req", indices=("t",))
        model.variables["e"] = var

        result = partition_constraints(model)

        # Numeric bound should be present with no expr
        assert ("e", ()) in result.bounds_lo
        bound = result.bounds_lo[("e", ())]
        assert bound.value == 0.0
        assert bound.expr is None

    def test_fx_expr_not_in_bounds_fx(self):
        """fx_expr should NOT produce a bounds_fx entry (not supported downstream)."""
        model = ModelIR()
        var = VariableDef(name="x", domain=("t",))
        var.fx_expr = ParamRef("p", indices=("t",))
        model.variables["x"] = var

        result = partition_constraints(model)

        # fx_expr should not be in bounds_fx
        assert ("x", ()) not in result.bounds_fx

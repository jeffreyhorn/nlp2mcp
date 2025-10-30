"""Unit tests for constraint partitioning."""

import pytest

from src.ir.model_ir import ModelIR
from src.ir.symbols import VariableDef
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

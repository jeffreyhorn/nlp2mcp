"""Unit tests for original symbols emission.

Tests verify correct usage of actual IR fields (Finding #3):
- SetDef = list[str] (members stored directly)
- AliasDef.target and .universe
- ParameterDef.domain and .values
- Scalars: empty domain () and values[()] = value
- Multi-dimensional keys: ("i1", "j2") → "i1.j2"
"""

import pytest

from src.emit.original_symbols import (
    emit_original_aliases,
    emit_original_parameters,
    emit_original_sets,
)
from src.ir.model_ir import ModelIR
from src.ir.symbols import AliasDef, ParameterDef, SetDef


@pytest.mark.unit
class TestEmitOriginalSets:
    """Test emission of original Sets block."""

    def test_empty_sets(self):
        """Test emission with no sets."""
        model = ModelIR()
        result = emit_original_sets(model)
        assert result == ""

    def test_single_set(self):
        """Test emission with single set."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["i1", "i2", "i3"])

        result = emit_original_sets(model)
        assert "Sets" in result
        assert "i /i1, i2, i3/" in result
        assert result.endswith(";")

    def test_multiple_sets(self):
        """Test emission with multiple sets."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["i1", "i2"])
        model.sets["j"] = SetDef(name="j", members=["j1", "j2", "j3"])

        result = emit_original_sets(model)
        assert "Sets" in result
        assert "i /i1, i2/" in result
        assert "j /j1, j2, j3/" in result
        assert result.endswith(";")

    def test_empty_set_members(self):
        """Test emission with set that has no members."""
        model = ModelIR()
        model.sets["universe"] = SetDef(name="universe", members=[])

        result = emit_original_sets(model)
        assert "Sets" in result
        assert "universe" in result
        # Empty sets just have the name, no slash notation


@pytest.mark.unit
class TestEmitOriginalAliases:
    """Test emission of original Alias declarations."""

    def test_empty_aliases(self):
        """Test emission with no aliases."""
        model = ModelIR()
        result = emit_original_aliases(model)
        assert result == ""

    def test_single_alias(self):
        """Test emission with single alias."""
        model = ModelIR()
        model.aliases["ip"] = AliasDef(name="ip", target="i")

        result = emit_original_aliases(model)
        assert "Alias(i, ip);" in result

    def test_multiple_aliases(self):
        """Test emission with multiple aliases."""
        model = ModelIR()
        model.aliases["ip"] = AliasDef(name="ip", target="i")
        model.aliases["jp"] = AliasDef(name="jp", target="j")

        result = emit_original_aliases(model)
        assert "Alias(i, ip);" in result
        assert "Alias(j, jp);" in result

    def test_alias_with_universe(self):
        """Test emission with alias that has universe constraint."""
        model = ModelIR()
        model.aliases["subset"] = AliasDef(name="subset", target="i", universe="all")

        result = emit_original_aliases(model)
        # Universe is stored but doesn't affect GAMS Alias syntax
        assert "Alias(i, subset);" in result


@pytest.mark.unit
class TestEmitOriginalParameters:
    """Test emission of original Parameters and Scalars."""

    def test_empty_parameters(self):
        """Test emission with no parameters."""
        model = ModelIR()
        result = emit_original_parameters(model)
        assert result == ""

    def test_scalar_parameter(self):
        """Test emission of scalar (empty domain, values[()] = value)."""
        model = ModelIR()
        model.params["discount"] = ParameterDef(name="discount", domain=(), values={(): 0.95})

        result = emit_original_parameters(model)
        assert "Scalars" in result
        assert "discount /0.95/" in result
        assert result.endswith(";")

    def test_scalar_with_no_value(self):
        """Test emission of scalar with no value (defaults to 0.0)."""
        model = ModelIR()
        model.params["threshold"] = ParameterDef(name="threshold", domain=(), values={})

        result = emit_original_parameters(model)
        assert "Scalars" in result
        assert "threshold /0.0/" in result

    def test_single_dimensional_parameter(self):
        """Test emission of parameter with one index."""
        model = ModelIR()
        model.params["demand"] = ParameterDef(
            name="demand",
            domain=("j",),
            values={("j1",): 100.0, ("j2",): 150.0, ("j3",): 200.0},
        )

        result = emit_original_parameters(model)
        assert "Parameters" in result
        assert "demand(j)" in result
        assert "j1 100" in result or "j1 100.0" in result
        assert "j2 150" in result or "j2 150.0" in result
        assert "j3 200" in result or "j3 200.0" in result

    def test_multi_dimensional_parameter(self):
        """Test emission of parameter with multiple indices.

        Multi-dimensional keys formatted as GAMS syntax: ("i1", "j2") → "i1.j2"
        """
        model = ModelIR()
        model.params["cost"] = ParameterDef(
            name="cost",
            domain=("i", "j"),
            values={("i1", "j1"): 2.5, ("i1", "j2"): 3.0, ("i2", "j1"): 1.8},
        )

        result = emit_original_parameters(model)
        assert "Parameters" in result
        assert "cost(i,j)" in result
        # Keys formatted as GAMS syntax
        assert "i1.j1 2.5" in result
        assert "i1.j2 3" in result or "i1.j2 3.0" in result
        assert "i2.j1 1.8" in result

    def test_parameter_with_no_data(self):
        """Test emission of parameter declared but with no data."""
        model = ModelIR()
        model.params["capacity"] = ParameterDef(name="capacity", domain=("i",), values={})

        result = emit_original_parameters(model)
        assert "Parameters" in result
        assert "capacity(i)" in result
        # No slash notation when no data

    def test_mixed_scalars_and_parameters(self):
        """Test emission with both scalars and parameters."""
        model = ModelIR()
        model.params["discount"] = ParameterDef(name="discount", domain=(), values={(): 0.95})
        model.params["demand"] = ParameterDef(name="demand", domain=("j",), values={("j1",): 100.0})

        result = emit_original_parameters(model)
        assert "Parameters" in result
        assert "demand(j)" in result
        assert "Scalars" in result
        assert "discount /0.95/" in result

    def test_multiple_scalars(self):
        """Test emission with multiple scalars."""
        model = ModelIR()
        model.params["alpha"] = ParameterDef(name="alpha", domain=(), values={(): 0.1})
        model.params["beta"] = ParameterDef(name="beta", domain=(), values={(): 0.2})

        result = emit_original_parameters(model)
        assert "Scalars" in result
        assert "alpha /0.1/" in result
        assert "beta /0.2/" in result

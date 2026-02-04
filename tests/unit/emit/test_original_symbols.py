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
    emit_computed_parameter_assignments,
    emit_original_aliases,
    emit_original_parameters,
    emit_original_sets,
)
from src.ir.ast import Binary, Call, Const, ParamRef
from src.ir.model_ir import ModelIR
from src.ir.symbols import AliasDef, ParameterDef, SetDef


@pytest.mark.unit
class TestEmitOriginalSets:
    """Test emission of original Sets block.

    Sprint 17 Day 10 (Issue #621): emit_original_sets now returns a tuple
    (pre_alias_sets, post_alias_sets) to handle sets that depend on aliases.
    """

    def test_empty_sets(self):
        """Test emission with no sets."""
        model = ModelIR()
        pre_alias, post_alias = emit_original_sets(model)
        assert pre_alias == ""
        assert post_alias == ""

    def test_single_set(self):
        """Test emission with single set."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["i1", "i2", "i3"])

        pre_alias, post_alias = emit_original_sets(model)
        assert "Sets" in pre_alias
        assert "i /i1, i2, i3/" in pre_alias
        assert pre_alias.endswith(";")
        assert post_alias == ""

    def test_multiple_sets(self):
        """Test emission with multiple sets."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["i1", "i2"])
        model.sets["j"] = SetDef(name="j", members=["j1", "j2", "j3"])

        pre_alias, post_alias = emit_original_sets(model)
        assert "Sets" in pre_alias
        assert "i /i1, i2/" in pre_alias
        assert "j /j1, j2, j3/" in pre_alias
        assert pre_alias.endswith(";")
        assert post_alias == ""

    def test_empty_set_members(self):
        """Test emission with set that has no members."""
        model = ModelIR()
        model.sets["universe"] = SetDef(name="universe", members=[])

        pre_alias, post_alias = emit_original_sets(model)
        assert "Sets" in pre_alias
        assert "universe" in pre_alias
        # Empty sets just have the name, no slash notation

    def test_subset_with_domain(self):
        """Test emission of subset with parent set relationship.

        Sprint 17 Day 5: Verify subset relationships are preserved.
        E.g., cg(genchar) /a, b, c/ should emit with domain.
        """
        model = ModelIR()
        model.sets["genchar"] = SetDef(name="genchar", members=["a", "b", "c", "upplim", "lowlim"])
        model.sets["cg"] = SetDef(name="cg", members=["a", "b", "c"], domain=("genchar",))

        pre_alias, post_alias = emit_original_sets(model)
        assert "Sets" in pre_alias
        assert "genchar /a, b, c, upplim, lowlim/" in pre_alias
        assert "cg(genchar) /a, b, c/" in pre_alias
        assert pre_alias.endswith(";")
        assert post_alias == ""

    def test_subset_without_members(self):
        """Test emission of subset without explicit members.

        Sprint 17 Day 5: Verify subset declarations without members are preserved.
        E.g., sub(parent) should emit as sub(parent).
        """
        model = ModelIR()
        model.sets["parent"] = SetDef(name="parent", members=["x", "y", "z"])
        model.sets["sub"] = SetDef(name="sub", members=[], domain=("parent",))

        pre_alias, post_alias = emit_original_sets(model)
        assert "Sets" in pre_alias
        assert "parent /x, y, z/" in pre_alias
        assert "sub(parent)" in pre_alias
        assert pre_alias.endswith(";")
        assert post_alias == ""

    def test_multi_dimensional_subset(self):
        """Test emission of multi-dimensional subset.

        Sprint 17 Day 5: Verify multi-dimensional domain is preserved.
        E.g., arc(n,np) should emit with both domain sets.
        """
        model = ModelIR()
        model.sets["n"] = SetDef(name="n", members=["n1", "n2"])
        model.sets["arc"] = SetDef(name="arc", members=["n1.n2"], domain=("n", "n"))

        pre_alias, post_alias = emit_original_sets(model)
        assert "Sets" in pre_alias
        assert "n /n1, n2/" in pre_alias
        assert "arc(n,n) /n1.n2/" in pre_alias
        assert pre_alias.endswith(";")
        assert post_alias == ""

    def test_set_depends_on_alias(self):
        """Test emission of set that depends on an alias.

        Sprint 17 Day 10 (Issue #621): Sets that reference aliased indices
        must be emitted after the Alias declarations.
        """
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["i1", "i2", "i3"])
        model.sets["ij"] = SetDef(name="ij", members=[], domain=("i", "j"))
        model.aliases["j"] = AliasDef(name="j", target="i")

        pre_alias, post_alias = emit_original_sets(model)

        # Set i should be in pre-alias (no alias dependency)
        assert "i /i1, i2, i3/" in pre_alias

        # Set ij(i,j) should be in post-alias (depends on alias j)
        assert "ij(i,j)" in post_alias
        assert "ij" not in pre_alias

    def test_mixed_sets_with_and_without_alias_deps(self):
        """Test emission with mix of alias-dependent and independent sets."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["i1", "i2"])
        model.sets["k"] = SetDef(name="k", members=["k1", "k2"])
        model.sets["ij"] = SetDef(name="ij", members=[], domain=("i", "j"))
        model.aliases["j"] = AliasDef(name="j", target="i")

        pre_alias, post_alias = emit_original_sets(model)

        # Sets without alias deps in pre-alias
        assert "i /i1, i2/" in pre_alias
        assert "k /k1, k2/" in pre_alias

        # Set with alias dep in post-alias
        assert "ij(i,j)" in post_alias
        assert "ij" not in pre_alias


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


@pytest.mark.unit
class TestEmitComputedParameterAssignments:
    """Test emission of computed parameter assignment statements.

    Sprint 17 Day 4: Tests for the new emit_computed_parameter_assignments function
    that emits expressions stored in ParameterDef.expressions as GAMS statements.
    """

    def test_empty_expressions(self):
        """Test emission with no expressions."""
        model = ModelIR()
        result = emit_computed_parameter_assignments(model)
        assert result == ""

    def test_no_expressions_in_parameters(self):
        """Test emission when parameters have values but no expressions."""
        model = ModelIR()
        model.params["cost"] = ParameterDef(name="cost", domain=("i",), values={("i1",): 10.0})
        result = emit_computed_parameter_assignments(model)
        assert result == ""

    def test_indexed_parameter_expression(self):
        """Test emission of indexed computed parameter like c(i,j) = f*d(i,j)/1000."""
        model = ModelIR()
        # Create expression: f * d(i,j) / 1000
        expr = Binary(
            "/",
            Binary("*", ParamRef("f", ()), ParamRef("d", ("i", "j"))),
            Const(1000.0),
        )
        model.params["c"] = ParameterDef(
            name="c", domain=("i", "j"), expressions={("i", "j"): expr}
        )

        result = emit_computed_parameter_assignments(model)
        assert "c(i,j) =" in result
        assert "f * d(i,j) / 1000" in result
        assert result.endswith(";")

    def test_parameter_with_function_call(self):
        """Test emission of parameter with function call like gplus(c) = gibbs(c) + log(...)."""
        model = ModelIR()
        # Create expression: gibbs(c) + log(750 * 0.07031)
        expr = Binary(
            "+",
            ParamRef("gibbs", ("c",)),
            Call("log", (Binary("*", Const(750.0), Const(0.07031)),)),
        )
        model.params["gplus"] = ParameterDef(
            name="gplus", domain=("c",), expressions={("c",): expr}
        )

        result = emit_computed_parameter_assignments(model)
        assert "gplus(c) =" in result
        assert "gibbs(c)" in result
        assert "log(" in result
        assert result.endswith(";")

    def test_scalar_expression(self):
        """Test emission of scalar computed parameter."""
        model = ModelIR()
        # Create expression: 2 * pi
        expr = Binary("*", Const(2.0), ParamRef("pi", ()))
        model.params["two_pi"] = ParameterDef(name="two_pi", domain=(), expressions={(): expr})

        result = emit_computed_parameter_assignments(model)
        assert "two_pi =" in result
        assert "2 * pi" in result
        assert result.endswith(";")

    def test_multiple_computed_parameters(self):
        """Test emission with multiple computed parameters."""
        model = ModelIR()
        # First parameter
        expr1 = Binary("*", ParamRef("a", ()), Const(2.0))
        model.params["double_a"] = ParameterDef(name="double_a", domain=(), expressions={(): expr1})
        # Second parameter
        expr2 = Binary("+", ParamRef("b", ("i",)), Const(1.0))
        model.params["b_plus_one"] = ParameterDef(
            name="b_plus_one", domain=("i",), expressions={("i",): expr2}
        )

        result = emit_computed_parameter_assignments(model)
        assert "double_a =" in result
        assert "b_plus_one(i) =" in result
        # Multiple lines
        assert result.count(";") == 2

    def test_skips_predefined_constants(self):
        """Test that predefined GAMS constants are skipped."""
        model = ModelIR()
        # This shouldn't be emitted since 'pi' is a predefined constant
        expr = Binary("*", Const(2.0), Const(3.14159))
        model.params["pi"] = ParameterDef(name="pi", domain=(), expressions={(): expr})

        result = emit_computed_parameter_assignments(model)
        assert result == ""

    def test_mixed_values_and_expressions(self):
        """Test parameter with both values and expressions (only expressions emitted)."""
        model = ModelIR()
        expr = Binary("+", ParamRef("x", ("i",)), Const(1.0))
        model.params["y"] = ParameterDef(
            name="y",
            domain=("i",),
            values={("a",): 5.0},  # Static value
            expressions={("i",): expr},  # Computed expression
        )

        result = emit_computed_parameter_assignments(model)
        # Only the expression should be emitted
        assert "y(i) =" in result
        assert "x(i) + 1" in result

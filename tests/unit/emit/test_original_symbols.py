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
    (phase1_sets, phase2_sets, phase3_sets) to handle complex alias dependencies.

    Emission phases:
    1. Phase 1: Sets with no alias dependencies
    2. Phase 1 aliases (handled by emit_original_aliases)
    3. Phase 2: Sets depending on phase 1 aliases
    4. Phase 2 aliases (handled by emit_original_aliases)
    5. Phase 3: Sets depending on phase 2 aliases
    """

    def test_empty_sets(self):
        """Test emission with no sets."""
        model = ModelIR()
        phase1, phase2, phase3 = emit_original_sets(model)
        assert phase1 == ""
        assert phase2 == ""
        assert phase3 == ""

    def test_single_set(self):
        """Test emission with single set."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["i1", "i2", "i3"])

        phase1, phase2, phase3 = emit_original_sets(model)
        assert "Sets" in phase1
        assert "i /i1, i2, i3/" in phase1
        assert phase1.endswith(";")
        assert phase2 == ""
        assert phase3 == ""

    def test_multiple_sets(self):
        """Test emission with multiple sets."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["i1", "i2"])
        model.sets["j"] = SetDef(name="j", members=["j1", "j2", "j3"])

        phase1, phase2, phase3 = emit_original_sets(model)
        assert "Sets" in phase1
        assert "i /i1, i2/" in phase1
        assert "j /j1, j2, j3/" in phase1
        assert phase1.endswith(";")
        assert phase2 == ""
        assert phase3 == ""

    def test_empty_set_members(self):
        """Test emission with set that has no members."""
        model = ModelIR()
        model.sets["universe"] = SetDef(name="universe", members=[])

        phase1, phase2, phase3 = emit_original_sets(model)
        assert "Sets" in phase1
        assert "universe" in phase1
        # Empty sets just have the name, no slash notation

    def test_subset_with_domain(self):
        """Test emission of subset with parent set relationship.

        Sprint 17 Day 5: Verify subset relationships are preserved.
        E.g., cg(genchar) /a, b, c/ should emit with domain.
        """
        model = ModelIR()
        model.sets["genchar"] = SetDef(name="genchar", members=["a", "b", "c", "upplim", "lowlim"])
        model.sets["cg"] = SetDef(name="cg", members=["a", "b", "c"], domain=("genchar",))

        phase1, phase2, phase3 = emit_original_sets(model)
        assert "Sets" in phase1
        assert "genchar /a, b, c, upplim, lowlim/" in phase1
        assert "cg(genchar) /a, b, c/" in phase1
        assert phase1.endswith(";")
        assert phase2 == ""
        assert phase3 == ""

    def test_subset_without_members(self):
        """Test emission of subset without explicit members.

        Sprint 17 Day 5: Verify subset declarations without members are preserved.
        E.g., sub(parent) should emit as sub(parent).
        """
        model = ModelIR()
        model.sets["parent"] = SetDef(name="parent", members=["x", "y", "z"])
        model.sets["sub"] = SetDef(name="sub", members=[], domain=("parent",))

        phase1, phase2, phase3 = emit_original_sets(model)
        assert "Sets" in phase1
        assert "parent /x, y, z/" in phase1
        assert "sub(parent)" in phase1
        assert phase1.endswith(";")
        assert phase2 == ""
        assert phase3 == ""

    def test_multi_dimensional_subset(self):
        """Test emission of multi-dimensional subset.

        Sprint 17 Day 5: Verify multi-dimensional domain is preserved.
        E.g., arc(n,np) should emit with both domain sets.
        """
        model = ModelIR()
        model.sets["n"] = SetDef(name="n", members=["n1", "n2"])
        model.sets["arc"] = SetDef(name="arc", members=["n1.n2"], domain=("n", "n"))

        phase1, phase2, phase3 = emit_original_sets(model)
        assert "Sets" in phase1
        assert "n /n1, n2/" in phase1
        assert "arc(n,n) /n1.n2/" in phase1
        assert phase1.endswith(";")
        assert phase2 == ""
        assert phase3 == ""

    def test_set_depends_on_alias(self):
        """Test emission of set that depends on an alias.

        Sprint 17 Day 10 (Issue #621): Sets that reference aliased indices
        must be emitted after the Alias declarations (phase 2).
        """
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["i1", "i2", "i3"])
        model.sets["ij"] = SetDef(name="ij", members=[], domain=("i", "j"))
        model.aliases["j"] = AliasDef(name="j", target="i")

        phase1, phase2, phase3 = emit_original_sets(model)

        # Set i should be in phase 1 (no alias dependency)
        assert "i /i1, i2, i3/" in phase1

        # Set ij(i,j) should be in phase 2 (depends on alias j)
        assert "ij(i,j)" in phase2
        assert "ij" not in phase1
        assert phase3 == ""

    def test_mixed_sets_with_and_without_alias_deps(self):
        """Test emission with mix of alias-dependent and independent sets."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["i1", "i2"])
        model.sets["k"] = SetDef(name="k", members=["k1", "k2"])
        model.sets["ij"] = SetDef(name="ij", members=[], domain=("i", "j"))
        model.aliases["j"] = AliasDef(name="j", target="i")

        phase1, phase2, phase3 = emit_original_sets(model)

        # Sets without alias deps in phase 1
        assert "i /i1, i2/" in phase1
        assert "k /k1, k2/" in phase1

        # Set with alias dep in phase 2
        assert "ij(i,j)" in phase2
        assert "ij" not in phase1
        assert phase3 == ""

    def test_case_insensitive_alias_detection(self):
        """Test that alias dependency detection is case-insensitive.

        Sprint 17 Day 10: GAMS is case-insensitive, so alias detection must
        handle different casing between alias names and domain indices.
        """
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["i1", "i2"])
        # Set domain uses uppercase J, but alias is lowercase j
        model.sets["ij"] = SetDef(name="ij", members=[], domain=("i", "J"))
        model.aliases["j"] = AliasDef(name="j", target="i")

        phase1, phase2, phase3 = emit_original_sets(model)

        # Set i should be in phase 1
        assert "i /i1, i2/" in phase1

        # Set ij(i,J) should be in phase 2 despite case difference
        assert "ij(i,J)" in phase2
        assert "ij" not in phase1

    def test_transitive_dependency(self):
        """Test that sets with transitive alias dependencies are in later phases.

        Sprint 17 Day 10: If set A depends on alias J, and set B depends on A,
        then B must also be in phase 2 (after phase 1 aliases).
        """
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["i1", "i2"])
        # ij depends on alias j (direct dependency)
        model.sets["ij"] = SetDef(name="ij", members=[], domain=("i", "j"))
        # triple depends on ij (transitive dependency through ij)
        model.sets["triple"] = SetDef(name="triple", members=[], domain=("ij", "i"))
        model.aliases["j"] = AliasDef(name="j", target="i")

        phase1, phase2, phase3 = emit_original_sets(model)

        # Set i should be in phase 1 (no alias dependency)
        assert "i /i1, i2/" in phase1

        # Both ij and triple should be in phase 2
        assert "ij(i,j)" in phase2
        assert "triple(ij,i)" in phase2
        assert "ij" not in phase1
        assert "triple" not in phase1

    def test_three_phase_dependency(self):
        """Test sets that depend on phase 2 aliases go to phase 3.

        Sprint 17 Day 10: If an alias targets a phase 2 set, sets depending
        on that alias must be in phase 3.
        """
        model = ModelIR()
        # Phase 1: base set
        model.sets["i"] = SetDef(name="i", members=["i1", "i2"])
        # Phase 1 alias: j is alias of i
        model.aliases["j"] = AliasDef(name="j", target="i")
        # Phase 2: ij depends on alias j
        model.sets["ij"] = SetDef(name="ij", members=[], domain=("i", "j"))
        # Phase 2 alias: k is alias of ij (a phase 2 set)
        model.aliases["k"] = AliasDef(name="k", target="ij")
        # Phase 3: xyz depends on alias k (which targets phase 2 set)
        model.sets["xyz"] = SetDef(name="xyz", members=[], domain=("i", "k"))

        phase1, phase2, phase3 = emit_original_sets(model)

        # Set i should be in phase 1
        assert "i /i1, i2/" in phase1
        assert "i /i1, i2/" not in phase2
        assert "i /i1, i2/" not in phase3

        # Set ij should be in phase 2
        assert "ij(i,j)" in phase2
        assert "ij" not in phase1

        # Set xyz should be in phase 3 (depends on phase 2 alias k)
        assert "xyz(i,k)" in phase3
        assert "xyz" not in phase1
        assert "xyz" not in phase2


@pytest.mark.unit
class TestEmitOriginalAliases:
    """Test emission of original Alias declarations.

    Sprint 17 Day 10: emit_original_aliases now returns a tuple
    (phase1_aliases, phase2_aliases, phase3_aliases) to handle aliases that
    target sets in each phase.
    """

    def test_empty_aliases(self):
        """Test emission with no aliases."""
        model = ModelIR()
        phase1, phase2, phase3 = emit_original_aliases(model)
        assert phase1 == ""
        assert phase2 == ""
        assert phase3 == ""

    def test_single_alias(self):
        """Test emission with single alias targeting a regular set."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["i1", "i2"])
        model.aliases["ip"] = AliasDef(name="ip", target="i")

        phase1, phase2, phase3 = emit_original_aliases(model)
        assert "Alias(i, ip);" in phase1
        assert phase2 == ""
        assert phase3 == ""

    def test_multiple_aliases(self):
        """Test emission with multiple aliases."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["i1"])
        model.sets["j"] = SetDef(name="j", members=["j1"])
        model.aliases["ip"] = AliasDef(name="ip", target="i")
        model.aliases["jp"] = AliasDef(name="jp", target="j")

        phase1, phase2, phase3 = emit_original_aliases(model)
        assert "Alias(i, ip);" in phase1
        assert "Alias(j, jp);" in phase1
        assert phase2 == ""
        assert phase3 == ""

    def test_alias_with_universe(self):
        """Test emission with alias that has universe constraint."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["i1"])
        model.aliases["subset"] = AliasDef(name="subset", target="i", universe="all")

        phase1, phase2, phase3 = emit_original_aliases(model)
        # Universe is stored but doesn't affect GAMS Alias syntax
        assert "Alias(i, subset);" in phase1

    def test_alias_targeting_phase2_set(self):
        """Test emission of alias that targets a phase 2 set.

        Sprint 17 Day 10: If an alias targets a set that is in phase 2
        (because that set depends on another alias), the alias must be
        emitted after phase 2 sets.
        """
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["i1", "i2"])
        # ij depends on alias j, so it's a phase 2 set
        model.sets["ij"] = SetDef(name="ij", members=[], domain=("i", "j"))
        # j is an alias of i
        model.aliases["j"] = AliasDef(name="j", target="i")
        # ijp targets ij (a phase 2 set), so it must be a phase 2 alias
        model.aliases["ijp"] = AliasDef(name="ijp", target="ij")

        phase1, phase2, phase3 = emit_original_aliases(model)

        # Alias j targets phase 1 set i, so it's a phase 1 alias
        assert "Alias(i, j);" in phase1

        # Alias ijp targets phase 2 set ij, so it's a phase 2 alias
        assert "Alias(ij, ijp);" in phase2
        assert "ijp" not in phase1
        assert phase3 == ""

    def test_alias_targeting_phase3_set(self):
        """Test emission of alias that targets a phase 3 set.

        Sprint 17 Day 10: If an alias targets a set that is in phase 3
        (because that set depends on a phase 2 alias), the alias must be
        emitted after phase 3 sets.
        """
        model = ModelIR()
        # Phase 1: base set
        model.sets["i"] = SetDef(name="i", members=["i1", "i2"])
        # Phase 1 alias: j is alias of i
        model.aliases["j"] = AliasDef(name="j", target="i")
        # Phase 2: ij depends on alias j
        model.sets["ij"] = SetDef(name="ij", members=[], domain=("i", "j"))
        # Phase 2 alias: k is alias of ij (a phase 2 set)
        model.aliases["k"] = AliasDef(name="k", target="ij")
        # Phase 3: xyz depends on alias k (which targets phase 2 set)
        model.sets["xyz"] = SetDef(name="xyz", members=[], domain=("i", "k"))
        # Phase 3 alias: xyzp targets xyz (a phase 3 set)
        model.aliases["xyzp"] = AliasDef(name="xyzp", target="xyz")

        phase1, phase2, phase3 = emit_original_aliases(model)

        # Alias j targets phase 1 set i
        assert "Alias(i, j);" in phase1
        # Alias k targets phase 2 set ij
        assert "Alias(ij, k);" in phase2
        # Alias xyzp targets phase 3 set xyz
        assert "Alias(xyz, xyzp);" in phase3
        assert "xyzp" not in phase1
        assert "xyzp" not in phase2


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

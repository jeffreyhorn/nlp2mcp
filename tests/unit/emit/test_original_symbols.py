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
    _expand_table_key,
    _expr_references_param,
    _needs_quoting,
    _quote_assignment_index,
    _sanitize_set_element,
    _sanitize_uel_element,
    collect_missing_param_labels,
    emit_computed_parameter_assignments,
    emit_interleaved_params_and_sets,
    emit_original_aliases,
    emit_original_parameters,
    emit_original_sets,
    emit_set_assignments,
    emit_subset_value_assignments,
)
from src.ir.ast import (
    Binary,
    Call,
    Const,
    DollarConditional,
    LhsConditionalAssign,
    ParamRef,
    SetMembershipTest,
    SymbolRef,
    Unary,
    VarRef,
)
from src.ir.model_ir import ModelIR
from src.ir.symbols import AliasDef, ParameterDef, SetAssignment, SetDef


def _get_phases(phase_list: list[str], num_phases: int = 3) -> tuple[str, ...]:
    """Helper to extract phases from a list, padding with empty strings if needed."""
    result = list(phase_list) + [""] * num_phases
    return tuple(result[:num_phases])


@pytest.mark.unit
class TestEmitOriginalSets:
    """Test emission of original Sets block.

    Sprint 17 Day 10 (Issue #621): emit_original_sets now returns a list of
    phase strings to handle complex alias dependencies with N phases.

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
        phases = emit_original_sets(model)
        assert phases == []

    def test_single_set(self):
        """Test emission with single set."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["i1", "i2", "i3"])

        phase1, phase2, phase3 = _get_phases(emit_original_sets(model))
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

        phase1, phase2, phase3 = _get_phases(emit_original_sets(model))
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

        phase1, phase2, phase3 = _get_phases(emit_original_sets(model))
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

        phase1, phase2, phase3 = _get_phases(emit_original_sets(model))
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

        phase1, phase2, phase3 = _get_phases(emit_original_sets(model))
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

        phase1, phase2, phase3 = _get_phases(emit_original_sets(model))
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

        phase1, phase2, phase3 = _get_phases(emit_original_sets(model))

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

        phase1, phase2, phase3 = _get_phases(emit_original_sets(model))

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

        phase1, phase2, phase3 = _get_phases(emit_original_sets(model))

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

        phase1, phase2, phase3 = _get_phases(emit_original_sets(model))

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

        phase1, phase2, phase3 = _get_phases(emit_original_sets(model))

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

    def test_set_depending_on_alias_chain(self):
        """Test that a set depending on a chained alias is placed correctly.

        If alias i2 targets alias i1 (not a set directly), and a set uses i2
        in its domain, the set must be emitted after i2 is declared.
        """
        model = ModelIR()
        # Phase 1: base set
        model.sets["i"] = SetDef(name="i", members=["i1", "i2"])
        # Phase 1 alias: j targets set i
        model.aliases["j"] = AliasDef(name="j", target="i")
        # Phase 2 alias: k targets alias j (alias chain)
        model.aliases["k"] = AliasDef(name="k", target="j")
        # Set that depends on alias k (a chained alias)
        model.sets["ik"] = SetDef(name="ik", members=[], domain=("i", "k"))

        phase1, phase2, phase3 = _get_phases(emit_original_sets(model))

        # Set i should be in phase 1
        assert "i /i1, i2/" in phase1
        # Set ik depends on alias k (phase 2), so it must be in phase 3
        # (aliases in phase p are emitted AFTER phase p sets)
        assert "ik(i,k)" in phase3
        assert "ik" not in phase1
        assert "ik" not in phase2

    def test_set_depending_on_both_phase1_and_phase2_aliases(self):
        """Test that a set depending on both phase-1 and phase-2 aliases goes to phase 3.

        Sprint 17 Day 10: If a set's domain references both a phase-1 alias AND
        a phase-2 alias, it must be placed in phase 3 (after phase-2 aliases),
        not phase 2. This prevents GAMS Error 140 for the phase-2 alias symbol.
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
        # This set depends on BOTH j (phase 1 alias) AND k (phase 2 alias)
        # It must go to phase 3, not phase 2
        model.sets["mixed"] = SetDef(name="mixed", members=[], domain=("j", "k"))

        phase1, phase2, phase3 = _get_phases(emit_original_sets(model))

        # Set i should be in phase 1
        assert "i /i1, i2/" in phase1

        # Set ij should be in phase 2
        assert "ij(i,j)" in phase2

        # Set mixed should be in phase 3 (depends on phase 2 alias k)
        # Even though it also depends on phase 1 alias j, the phase 2 alias
        # dependency takes precedence
        assert "mixed(j,k)" in phase3
        assert "mixed" not in phase1
        assert "mixed" not in phase2


@pytest.mark.unit
class TestEmitOriginalAliases:
    """Test emission of original Alias declarations.

    Sprint 17 Day 10: emit_original_aliases now returns a list of phase strings
    to handle aliases that target sets in each phase with N phases.
    """

    def test_empty_aliases(self):
        """Test emission with no aliases."""
        model = ModelIR()
        phases = emit_original_aliases(model)
        assert phases == []

    def test_single_alias(self):
        """Test emission with single alias targeting a regular set."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["i1", "i2"])
        model.aliases["ip"] = AliasDef(name="ip", target="i")

        phase1, phase2, phase3 = _get_phases(emit_original_aliases(model))
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

        phase1, phase2, phase3 = _get_phases(emit_original_aliases(model))
        assert "Alias(i, ip);" in phase1
        assert "Alias(j, jp);" in phase1
        assert phase2 == ""
        assert phase3 == ""

    def test_alias_with_universe(self):
        """Test emission with alias that has universe constraint."""
        model = ModelIR()
        # Define the universe set to keep IR consistent with parser invariants
        model.sets["all"] = SetDef(name="all", members=[])
        model.sets["i"] = SetDef(name="i", members=["i1"])
        model.aliases["subset"] = AliasDef(name="subset", target="i", universe="all")

        phase1, phase2, phase3 = _get_phases(emit_original_aliases(model))
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

        phase1, phase2, phase3 = _get_phases(emit_original_aliases(model))

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

        phase1, phase2, phase3 = _get_phases(emit_original_aliases(model))

        # Alias j targets phase 1 set i
        assert "Alias(i, j);" in phase1
        # Alias k targets phase 2 set ij
        assert "Alias(ij, k);" in phase2
        # Alias xyzp targets phase 3 set xyz
        assert "Alias(xyz, xyzp);" in phase3
        assert "xyzp" not in phase1
        assert "xyzp" not in phase2

    def test_alias_chain(self):
        """Test emission of alias chains where an alias targets another alias.

        Alias chains like Alias(i, i1), Alias(i1, i2) where i2's target is i1
        (another alias, not a set). The algorithm must look up alias_phases
        as a fallback when the target is not found in set_phases.
        """
        model = ModelIR()
        # Phase 1: base set
        model.sets["i"] = SetDef(name="i", members=["i1", "i2"])
        # Phase 1 alias: i1 targets set i
        model.aliases["i1"] = AliasDef(name="i1", target="i")
        # Alias chain: i2 targets alias i1 (not a set)
        model.aliases["i2"] = AliasDef(name="i2", target="i1")

        phase1, phase2, phase3 = _get_phases(emit_original_aliases(model))

        # Alias i1 targets phase 1 set i → phase 1
        assert "Alias(i, i1);" in phase1
        # Alias i2 targets alias i1 (phase 1) → phase 2 (must wait for i1)
        assert "Alias(i1, i2);" in phase2
        assert "i2" not in phase1
        assert phase3 == ""

    def test_alias_with_special_characters(self):
        """Test emission of aliases with special characters like '-'.

        Issue #665: Alias names containing special characters (e.g., 'i-alias')
        must be quoted in emitted GAMS to avoid syntax errors. The parser now
        strips quotes from escaped identifiers, so the emitter must re-quote
        them for valid GAMS output.
        """
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["a", "b"])
        # Alias with hyphen in name (requires quoting)
        model.aliases["i-alias"] = AliasDef(name="i-alias", target="i")

        phase1, phase2, phase3 = _get_phases(emit_original_aliases(model))

        # Alias name with '-' must be quoted
        assert "Alias(i, 'i-alias');" in phase1
        assert phase2 == ""
        assert phase3 == ""


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
        assert "threshold /0/" in result

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

    def test_parameter_with_no_data_no_expressions_skipped(self):
        """Issue #917: Parameters with no values and no expressions are skipped.

        These are typically loop-initialized reporting parameters that serve
        no purpose in the single-solve MCP and would cause GAMS $141 errors.
        """
        model = ModelIR()
        model.params["capacity"] = ParameterDef(name="capacity", domain=("i",), values={})

        result = emit_original_parameters(model)
        assert "capacity(i)" not in result

    def test_parameter_with_no_data_but_expressions_declared(self):
        """Parameters with no data but with expressions should still be declared."""
        from src.ir.ast import Const

        model = ModelIR()
        pdef = ParameterDef(name="capacity", domain=("i",), values={})
        pdef.expressions.append((("i",), Const(42.0)))
        model.params["capacity"] = pdef

        result = emit_original_parameters(model)
        assert "Parameters" in result
        assert "capacity(i)" in result

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

    def test_skip_domainless_parameter_with_indexed_values(self, caplog):
        """Test Issue #675: Skip parameters with empty domain but indexed values.

        Parameters declared without a domain but used with indexed values (like
        report parameters) cannot be properly emitted as scalars. They should be
        skipped with a warning.
        """
        import logging

        model = ModelIR()
        # Parameter with empty domain but indexed values - should be skipped
        model.params["report"] = ParameterDef(
            name="report",
            domain=(),  # Empty domain (declared as scalar)
            values={("x1", "global"): 1.0, ("x1", "solver"): 2.0},  # But indexed values
        )
        # Regular scalar - should be emitted
        model.params["discount"] = ParameterDef(name="discount", domain=(), values={(): 0.95})

        with caplog.at_level(logging.WARNING):
            result = emit_original_parameters(model)

        # "report" should NOT appear in output (skipped)
        assert "report" not in result
        # Regular scalar should still be emitted
        assert "discount /0.95/" in result
        # Warning should be logged
        assert any("report" in record.message for record in caplog.records)
        assert any("indexed values" in record.message for record in caplog.records)

    def test_skip_domainless_parameter_with_indexed_expressions(self, caplog):
        """Test Issue #675: Skip parameters with empty domain but indexed expressions.

        Parameters declared without a domain but with indexed expressions (like
        report parameters referencing .l values) cannot be properly emitted.
        """
        import logging

        model = ModelIR()
        # Parameter with empty domain but indexed expressions - should be skipped
        model.params["croprep"] = ParameterDef(
            name="croprep",
            domain=(),  # Empty domain
            values={},
            expressions=[(("revenue", "c"), Const(100.0))],  # Indexed expression
        )

        with caplog.at_level(logging.WARNING):
            result = emit_original_parameters(model)

        # "croprep" should NOT appear in output (skipped)
        assert "croprep" not in result
        # Warning should be logged
        assert any("croprep" in record.message for record in caplog.records)

    def test_wildcard_domain_preserved_as_asterisk(self):
        """Test Issue #679: Wildcard domains are preserved as '*' in emission.

        When a parameter is declared with a wildcard domain like Table compdat(*,alloy),
        the emitted GAMS should keep '*' rather than replacing it with a generated
        named set. This prevents E171 "Domain violation for set" errors when the
        original code indexes the parameter with different sets.

        Regression test to prevent reintroducing E171 via future refactors.
        """
        model = ModelIR()
        # Parameter with wildcard in first domain position
        model.params["compdat"] = ParameterDef(
            name="compdat",
            domain=("*", "alloy"),
            values={("lead", "steel"): 10.0, ("zinc", "steel"): 20.0, ("price", "steel"): 5.0},
        )

        result = emit_original_parameters(model)

        # Domain should contain '*', not a generated set name like 'wc_compdat_d1'
        assert "compdat(*,alloy)" in result
        assert "wc_compdat" not in result

    def test_multiple_wildcard_domains_preserved(self):
        """Test Issue #679: Multiple wildcard domains are all preserved.

        Parameters like Table rd(*,*) should emit with both wildcards preserved.
        """
        model = ModelIR()
        # Parameter with wildcards in both domain positions
        model.params["rd"] = ParameterDef(
            name="rd",
            domain=("*", "*"),
            values={("plant1", "market1"): 100.0, ("plant2", "market2"): 200.0},
        )

        result = emit_original_parameters(model)

        # Both wildcards should be preserved
        assert "rd(*,*)" in result
        assert "wc_rd" not in result


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
            name="c", domain=("i", "j"), expressions=[(("i", "j"), expr)]
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
            name="gplus", domain=("c",), expressions=[(("c",), expr)]
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
        model.params["two_pi"] = ParameterDef(name="two_pi", domain=(), expressions=[((), expr)])

        result = emit_computed_parameter_assignments(model)
        assert "two_pi =" in result
        assert "2 * pi" in result
        assert result.endswith(";")

    def test_multiple_computed_parameters(self):
        """Test emission with multiple computed parameters."""
        model = ModelIR()
        # First parameter
        expr1 = Binary("*", ParamRef("a", ()), Const(2.0))
        model.params["double_a"] = ParameterDef(
            name="double_a", domain=(), expressions=[((), expr1)]
        )
        # Second parameter
        expr2 = Binary("+", ParamRef("b", ("i",)), Const(1.0))
        model.params["b_plus_one"] = ParameterDef(
            name="b_plus_one", domain=("i",), expressions=[(("i",), expr2)]
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
        model.params["pi"] = ParameterDef(name="pi", domain=(), expressions=[((), expr)])

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
            expressions=[(("i",), expr)],  # Computed expression
        )

        result = emit_computed_parameter_assignments(model)
        # Only the expression should be emitted
        assert "y(i) =" in result
        assert "x(i) + 1" in result

    def test_multi_phase_cycle_ordering(self):
        """Parameters in a cycle with multiple phases are ordered correctly.

        syield depends on sys, sys depends on syield — a cycle. The topological
        sort should split syield into phases at the sys dependency boundary and
        mark the param as defined after any phase, allowing the cycle to proceed.
        """
        model = ModelIR()
        model.sets["s"] = SetDef(name="s", members=["s1"])
        model.sets["f"] = SetDef(name="f", members=["normal"])
        model.sets["c"] = SetDef(name="c", members=["wheat"])

        # sys(s,f) = sum(c, syield(c,s,f))  [reads syield]
        expr_sys = ParamRef("syield", ("c", "s", "f"))
        model.params["sys"] = ParameterDef(
            name="sys",
            domain=("s", "f"),
            values={},
            expressions=[(("s", "f"), expr_sys)],
        )
        # syield phase 0: syield(c,s,f) = mcp(s,c)  [no dep on sys]
        # syield phase 1: syield("straw",s,f) = sys(s,f)  [reads sys]
        expr_phase0 = ParamRef("mcp", ("s", "c"))
        expr_phase1 = ParamRef("sys", ("s", "f"))
        model.params["syield"] = ParameterDef(
            name="syield",
            domain=("c", "s", "f"),
            values={},
            expressions=[
                (("c", "s", '"normal"'), expr_phase0),
                (('"straw"', "s", "f"), expr_phase1),
            ],
        )
        model.params["mcp"] = ParameterDef(
            name="mcp", domain=("s", "c"), values={("s1", "wheat"): 1.0}
        )

        result = emit_computed_parameter_assignments(model)
        lines = [ln.strip() for ln in result.strip().splitlines() if ln.strip()]
        # syield phase 0 must come before sys (so sys can read syield)
        # sys must come before syield phase 1 (which reads sys)
        syield_first = next(i for i, ln in enumerate(lines) if "syield" in ln.lower())
        sys_line = next(i for i, ln in enumerate(lines) if ln.lower().startswith("sys("))
        assert syield_first < sys_line, "syield phase 0 should precede sys"


@pytest.mark.unit
class TestSetElementQuoting:
    """Test set element quoting and sanitization behavior.

    PR #664: Tests for auto-quoting of elements with special characters,
    preservation of pre-quoted elements, and handling of quoted elements
    with spaces.
    """

    def test_needs_quoting_with_hyphen(self):
        """Test that elements with hyphens need quoting."""
        assert _needs_quoting("gov-expend") is True
        assert _needs_quoting("machine-1") is True
        assert _needs_quoting("1964-i") is True

    def test_needs_quoting_with_plus(self):
        """Test that elements with plus signs need quoting."""
        assert _needs_quoting("food+agr") is True
        assert _needs_quoting("pulp+paper") is True

    def test_needs_quoting_simple_identifier(self):
        """Test that simple identifiers don't need quoting."""
        assert _needs_quoting("demand") is False
        assert _needs_quoting("i1") is False
        assert _needs_quoting("machine1") is False

    def test_sanitize_auto_quotes_hyphen(self):
        """Test that sanitizer auto-quotes elements with hyphens."""
        assert _sanitize_set_element("gov-expend") == "'gov-expend'"
        assert _sanitize_set_element("machine-1") == "'machine-1'"

    def test_sanitize_auto_quotes_plus(self):
        """Test that sanitizer auto-quotes elements with plus signs."""
        assert _sanitize_set_element("food+agr") == "'food+agr'"
        assert _sanitize_set_element("pulp+paper") == "'pulp+paper'"

    def test_sanitize_preserves_simple_identifier(self):
        """Test that sanitizer preserves simple identifiers without quoting."""
        assert _sanitize_set_element("demand") == "demand"
        assert _sanitize_set_element("i1") == "i1"

    def test_sanitize_preserves_prequoted_element(self):
        """Test that sanitizer preserves already-quoted elements."""
        assert _sanitize_set_element("'c-bond-ext'") == "'c-bond-ext'"
        assert _sanitize_set_element("'food+agr'") == "'food+agr'"

    def test_sanitize_prequoted_with_spaces(self):
        """Test that sanitizer accepts quoted elements with spaces.

        GAMS allows spaces in quoted labels (e.g., 'SAE 10' from bearing.gms).
        """
        assert _sanitize_set_element("'SAE 10'") == "'SAE 10'"
        assert _sanitize_set_element("'my label'") == "'my label'"

    def test_sanitize_normalizes_doubled_quotes(self):
        """Test that sanitizer normalizes doubled single quotes to single quotes.

        The parser sometimes produces ''label'' instead of 'label'
        (e.g., ''SAE 10'', ''max-stock'' from bearing/robert models).
        """
        assert _sanitize_set_element("''SAE 10''") == "'SAE 10'"
        assert _sanitize_set_element("''max-stock''") == "'max-stock'"
        assert _sanitize_set_element("''food+agr''") == "'food+agr'"

    def test_sanitize_strips_whitespace(self):
        """Test that sanitizer strips surrounding whitespace.

        Table row labels may have trailing whitespace from parsing.
        """
        assert _sanitize_set_element("  demand  ") == "demand"
        assert _sanitize_set_element(" 'SAE 10' ") == "'SAE 10'"

    def test_sanitize_rejects_dangerous_chars(self):
        """Test that sanitizer rejects elements with dangerous characters."""
        with pytest.raises(ValueError, match="unsafe characters"):
            _sanitize_set_element("bad;element")
        with pytest.raises(ValueError, match="unsafe characters"):
            _sanitize_set_element("bad/element")
        with pytest.raises(ValueError, match="unsafe characters"):
            _sanitize_set_element("bad$element")

    def test_sanitize_rejects_dangerous_chars_in_quoted(self):
        """Test that sanitizer rejects quoted elements with dangerous inner chars."""
        with pytest.raises(ValueError, match="unsafe characters"):
            _sanitize_set_element("'bad;element'")
        with pytest.raises(ValueError, match="unsafe characters"):
            _sanitize_set_element("'nested'quote'")

    def test_sanitize_quotes_reserved_constants(self):
        """Sprint 19 Day 2: Reserved GAMS constants must be quoted as set elements."""
        assert _sanitize_set_element("inf") == "'inf'"
        assert _sanitize_set_element("na") == "'na'"
        assert _sanitize_set_element("eps") == "'eps'"
        assert _sanitize_set_element("no") == "'no'"
        assert _sanitize_set_element("yes") == "'yes'"
        assert _sanitize_set_element("undf") == "'undf'"

    def test_sanitize_preserves_non_reserved_identifiers(self):
        """Non-reserved identifiers should not be affected by reserved word check."""
        assert _sanitize_set_element("eff") == "eff"
        assert _sanitize_set_element("money") == "money"
        assert _sanitize_set_element("gov") == "gov"

    def test_set_emission_quotes_special_elements(self):
        """Test that set emission properly quotes elements with special chars."""
        model = ModelIR()
        model.sets["m"] = SetDef(name="m", members=["gov-expend", "money", "food+agr"])

        phase1, _, _ = _get_phases(emit_original_sets(model))
        assert "m /'gov-expend', money, 'food+agr'/" in phase1

    def test_parameter_data_quotes_special_keys(self):
        """Test that parameter data properly quotes keys with special chars."""
        model = ModelIR()
        model.params["uinit"] = ParameterDef(
            name="uinit",
            domain=("m",),
            values={("gov-expend",): 110.5, ("money",): 200.0},
        )

        result = emit_original_parameters(model)
        assert "'gov-expend' 110.5" in result
        assert "money 200" in result or "money 200.0" in result

    def test_multidimensional_set_quotes_components_separately(self):
        """Test that multi-dimensional set members quote each component separately.

        For multi-dimensional sets like km(k,mode), members are stored as dot-separated
        tuples like "c-cracker.ho-low-s". Each component should be quoted individually
        to produce "'c-cracker'.'ho-low-s'" instead of incorrectly quoting the whole
        thing as "'c-cracker.ho-low-s'".
        """
        model = ModelIR()
        model.sets["k"] = SetDef(name="k", members=["pipestill", "reformer", "c-cracker"])
        model.sets["mode"] = SetDef(name="mode", members=["ho-low-s", "ho-high-s"])
        model.sets["km"] = SetDef(
            name="km",
            domain=["k", "mode"],
            members=["c-cracker.ho-low-s", "c-cracker.ho-high-s"],
        )

        phase1, _, _ = _get_phases(emit_original_sets(model))
        # Each component should be quoted separately
        assert "'c-cracker'.'ho-low-s'" in phase1
        assert "'c-cracker'.'ho-high-s'" in phase1
        # Should NOT quote the entire tuple
        assert "'c-cracker.ho-low-s'" not in phase1


@pytest.mark.unit
class TestExpandTableKey:
    """Test _expand_table_key function for handling dotted row headers.

    PR #677: The table parser stores data as 2-tuples (row_header, col_header) where
    row_header may be a dotted string representing multiple dimensions (e.g., 'low.a.distr').
    This function expands such keys to match the full domain size.
    """

    def test_key_already_matches_domain_size(self):
        """Test that keys already matching domain size are returned unchanged."""
        key = ("i1", "j1")
        result = _expand_table_key(key, 2)
        assert result == ("i1", "j1")

    def test_key_exceeds_domain_size(self):
        """Test that keys exceeding domain size are treated as malformed and return None."""
        key = ("a", "b", "c")
        result = _expand_table_key(key, 2)
        assert result is None

    def test_expand_single_dotted_element(self):
        """Test expanding a 2-tuple with one dotted row header to 3 dimensions."""
        # ('low.a', 'light-ind') should expand to ('low', 'a', 'light-ind')
        key = ("low.a", "light-ind")
        result = _expand_table_key(key, 3)
        assert result == ("low", "a", "light-ind")

    def test_expand_multi_dotted_element(self):
        """Test expanding a 2-tuple with multi-dotted row header to 4 dimensions."""
        # ('low.a.distr', 'light-ind') should expand to ('low', 'a', 'distr', 'light-ind')
        key = ("low.a.distr", "light-ind")
        result = _expand_table_key(key, 4)
        assert result == ("low", "a", "distr", "light-ind")

    def test_expand_both_elements_dotted(self):
        """Test expanding when both elements contain dots."""
        # ('a.b', 'c.d') should expand to ('a', 'b', 'c', 'd')
        key = ("a.b", "c.d")
        result = _expand_table_key(key, 4)
        assert result == ("a", "b", "c", "d")

    def test_malformed_key_returns_none_too_few(self):
        """Test that malformed keys with too few elements return None."""
        # ('a', 'b') cannot expand to 4 dimensions
        key = ("a", "b")
        result = _expand_table_key(key, 4)
        assert result is None

    def test_malformed_key_returns_none_too_many(self):
        """Test that keys expanding to more than domain_size return None."""
        # ('a.b.c', 'd') expands to 4 elements but domain_size is 3
        key = ("a.b.c", "d")
        result = _expand_table_key(key, 3)
        assert result is None

    def test_empty_key(self):
        """Test handling of empty key tuple."""
        key: tuple[str, ...] = ()
        result = _expand_table_key(key, 2)
        assert result is None

    def test_single_element_key(self):
        """Test expanding single element with dots."""
        key = ("a.b.c",)
        result = _expand_table_key(key, 3)
        assert result == ("a", "b", "c")

    def test_preserves_special_characters_in_elements(self):
        """Test that special characters within elements are preserved after split."""
        # ('low.c-bond-ext', 'machine-1') should expand properly
        key = ("low.c-bond-ext", "machine-1")
        result = _expand_table_key(key, 3)
        assert result == ("low", "c-bond-ext", "machine-1")


@pytest.mark.unit
class TestExprReferencesParam:
    """Test _expr_references_param for detecting self-referencing parameter expressions.

    Issue #738: Used to detect patterns like deltaq(sc) = deltaq(sc)/(1 + deltaq(sc))
    where the RHS references the parameter being assigned.
    """

    def test_direct_param_ref_match(self):
        """Test detection of a direct ParamRef matching the parameter name."""
        expr = ParamRef("deltaq", ("sc",))
        assert _expr_references_param(expr, "deltaq") is True

    def test_direct_param_ref_no_match(self):
        """Test that a ParamRef with a different name returns False."""
        expr = ParamRef("sigmaq", ("sc",))
        assert _expr_references_param(expr, "deltaq") is False

    def test_case_insensitive_match(self):
        """Test that matching is case-insensitive (GAMS is case-insensitive)."""
        expr = ParamRef("DeltaQ", ("sc",))
        assert _expr_references_param(expr, "deltaq") is True
        assert _expr_references_param(expr, "DELTAQ") is True

    def test_nested_in_binary_left(self):
        """Test detection of ParamRef nested in left branch of Binary expression."""
        # deltaq(sc) / (1 + deltaq(sc))
        expr = Binary("/", ParamRef("deltaq", ("sc",)), Const(2.0))
        assert _expr_references_param(expr, "deltaq") is True

    def test_nested_in_binary_right(self):
        """Test detection of ParamRef nested in right branch of Binary expression."""
        expr = Binary("/", Const(1.0), ParamRef("deltaq", ("sc",)))
        assert _expr_references_param(expr, "deltaq") is True

    def test_deeply_nested(self):
        """Test detection of ParamRef deeply nested in expression tree.

        Simulates: deltaq(sc) / (1 + deltaq(sc))
        """
        inner = Binary("+", Const(1.0), ParamRef("deltaq", ("sc",)))
        expr = Binary("/", ParamRef("deltaq", ("sc",)), inner)
        assert _expr_references_param(expr, "deltaq") is True

    def test_const_only_expression(self):
        """Test that a Const-only expression returns False."""
        expr = Const(42.0)
        assert _expr_references_param(expr, "deltaq") is False

    def test_other_param_refs_only(self):
        """Test that expression with only other ParamRefs returns False."""
        expr = Binary("*", ParamRef("alpha", ("i",)), ParamRef("beta", ("j",)))
        assert _expr_references_param(expr, "deltaq") is False

    def test_scalar_param_ref(self):
        """Test detection of scalar (no-index) ParamRef."""
        expr = Binary("*", Const(2.0), ParamRef("f", ()))
        assert _expr_references_param(expr, "f") is True

    def test_function_call_wrapping_param_ref(self):
        """Test detection of ParamRef inside a function call."""
        # log(deltaq(sc))
        expr = Call("log", (ParamRef("deltaq", ("sc",)),))
        assert _expr_references_param(expr, "deltaq") is True


@pytest.mark.unit
class TestSelfReferencingExpressionSkipping:
    """Test that emit_computed_parameter_assignments skips self-referencing expressions
    when the parameter has no prior values.

    Issue #738: Post-solve calibration patterns like:
      deltaq(sc) = (x.l(sc)/m.l(sc))**(1/sigmaq(sc))*...  <- Step 1 (dropped: .l refs)
      deltaq(sc) = deltaq(sc)/(1 + deltaq(sc))             <- Step 2 (self-ref, kept)
    The parser drops Step 1. Emitting Step 2 alone causes GAMS Error 141.
    """

    def test_self_ref_no_values_skipped(self):
        """Test that self-referencing expression is skipped when no values exist."""
        model = ModelIR()
        # Self-referencing expression: deltaq(sc) = deltaq(sc) / (1 + deltaq(sc))
        inner = Binary("+", Const(1.0), ParamRef("deltaq", ("sc",)))
        expr = Binary("/", ParamRef("deltaq", ("sc",)), inner)
        model.params["deltaq"] = ParameterDef(
            name="deltaq",
            domain=("sc",),
            values={},  # No values — Step 1 was dropped
            expressions=[(("sc",), expr)],
        )
        # Need to declare 'sc' as a set so it's recognized as a domain variable
        model.sets["sc"] = SetDef(name="sc", members=["sc1"])

        result = emit_computed_parameter_assignments(model)
        # Expression should be skipped entirely
        assert result == ""

    def test_self_ref_with_values_not_skipped(self):
        """Test that self-referencing expression is emitted when prior values exist."""
        model = ModelIR()
        # Self-referencing expression with prior values (Step 1 was NOT dropped)
        inner = Binary("+", Const(1.0), ParamRef("deltas", ("i",)))
        expr = Binary("/", ParamRef("deltas", ("i",)), inner)
        model.params["deltas"] = ParameterDef(
            name="deltas",
            domain=("i",),
            values={("i1",): 1.0},  # Has prior values
            expressions=[(("i",), expr)],
        )
        model.sets["i"] = SetDef(name="i", members=["i1"])

        result = emit_computed_parameter_assignments(model)
        # Expression should be emitted because values exist
        assert "deltas(i) =" in result

    def test_non_self_ref_no_values_emitted(self):
        """Test that non-self-referencing expression is emitted even without values."""
        model = ModelIR()
        # Non-self-referencing: c(i) = a(i) + 1
        expr = Binary("+", ParamRef("a", ("i",)), Const(1.0))
        model.params["c"] = ParameterDef(
            name="c",
            domain=("i",),
            values={},  # No values, but NOT self-referencing
            expressions=[(("i",), expr)],
        )
        model.sets["i"] = SetDef(name="i", members=["i1"])

        result = emit_computed_parameter_assignments(model)
        # Expression should be emitted (not self-referencing)
        assert "c(i) =" in result
        assert "a(i) + 1" in result

    def test_multiple_params_mixed_self_ref(self):
        """Test that only self-referencing params without values are skipped."""
        model = ModelIR()
        model.sets["sc"] = SetDef(name="sc", members=["sc1"])

        # Param 1: self-ref, no values → should be skipped
        inner1 = Binary("+", Const(1.0), ParamRef("deltaq", ("sc",)))
        expr1 = Binary("/", ParamRef("deltaq", ("sc",)), inner1)
        model.params["deltaq"] = ParameterDef(
            name="deltaq",
            domain=("sc",),
            values={},
            expressions=[(("sc",), expr1)],
        )

        # Param 2: not self-ref, no values → should be emitted
        expr2 = Binary("*", ParamRef("alpha", ("sc",)), Const(2.0))
        model.params["beta"] = ParameterDef(
            name="beta",
            domain=("sc",),
            values={},
            expressions=[(("sc",), expr2)],
        )

        result = emit_computed_parameter_assignments(model)
        # deltaq should be skipped, beta should be emitted
        assert "deltaq" not in result
        assert "beta(sc) =" in result


@pytest.mark.unit
class TestTransitiveCalibrationClassification:
    """Issue #763: Test transitive calibration parameter detection and ordering.

    Parameters that transitively depend on .l-referencing (calibration) parameters
    must be deferred to the calibration pass and emitted in dependency order.
    """

    def test_transitive_calibration_deferred(self):
        """A parameter referencing a calibration param is also deferred.

        Setup: cva = sum(v.l * x.l), rva = cva / cli
        - cva directly references .l → calibration
        - rva references cva (calibration) → also calibration (transitive)
        Both should be excluded from no_varref_attr pass.
        """
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["a", "b"])

        # cva = v.l(i) (directly references .l)
        cva_expr = VarRef("v", ("i",), attribute="l")
        model.params["cva"] = ParameterDef(
            name="cva", domain=(), values={}, expressions=[((), cva_expr)]
        )

        # rva = cva / 2 (references cva, a calibration param)
        rva_expr = Binary("/", ParamRef("cva", ()), Const(2.0))
        model.params["rva"] = ParameterDef(
            name="rva", domain=(), values={}, expressions=[((), rva_expr)]
        )

        # no_varref_attr pass should exclude both cva and rva
        result = emit_computed_parameter_assignments(model, varref_filter="no_varref_attr")
        assert "cva" not in result
        assert "rva" not in result

    def test_transitive_calibration_emitted_in_order(self):
        """Calibration pass emits dependencies before dependents.

        Setup: cva = v.l(i), rva = cva / 2
        In only_varref_attr pass, cva must appear before rva.
        """
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["a", "b"])

        cva_expr = VarRef("v", ("i",), attribute="l")
        model.params["cva"] = ParameterDef(
            name="cva", domain=(), values={}, expressions=[((), cva_expr)]
        )

        rva_expr = Binary("/", ParamRef("cva", ()), Const(2.0))
        model.params["rva"] = ParameterDef(
            name="rva", domain=(), values={}, expressions=[((), rva_expr)]
        )

        result = emit_computed_parameter_assignments(model, varref_filter="only_varref_attr")
        assert "cva" in result
        assert "rva" in result
        # cva must come before rva
        assert result.index("cva") < result.index("rva")


@pytest.mark.unit
class TestCollectVarrefNames:
    """Issue #763: Test _collect_varref_names helper and variable .l init ordering."""

    def test_collects_varref_l_names(self):
        """Detect .l references in expression trees."""
        from src.emit.emit_gams import _collect_varref_names

        # x.l(i) + y.l(j) → {x, y}
        expr = Binary("+", VarRef("x", ("i",), attribute="l"), VarRef("y", ("j",), attribute="l"))
        assert _collect_varref_names(expr) == {"x", "y"}

    def test_ignores_bare_varrefs(self):
        """Bare VarRef (no .l attribute) should not be collected."""
        from src.emit.emit_gams import _collect_varref_names

        expr = Binary("*", VarRef("x", ("i",)), Const(2.0))
        assert _collect_varref_names(expr) == set()

    def test_traverses_paramref_indices(self):
        """VarRef .l inside a ParamRef's index expressions should be found."""
        from src.emit.emit_gams import _collect_varref_names

        # p(x.l) — ParamRef with VarRef.l in index
        inner = VarRef("x", (), attribute="l")
        expr = ParamRef("p", (inner,))
        assert _collect_varref_names(expr) == {"x"}


@pytest.mark.unit
class TestInfParameterEmission:
    """Test that ±Inf parameter values are emitted as GAMS-compatible syntax."""

    def test_positive_inf_parameter(self):
        """Test +Inf in parameter data emitted as 'inf'."""
        model = ModelIR()
        model.params["cap"] = ParameterDef(
            name="cap", domain=("i",), values={("alaska",): float("inf"), ("texas",): 100.0}
        )
        result = emit_original_parameters(model)
        assert "alaska inf" in result
        assert "texas 100" in result

    def test_negative_inf_parameter(self):
        """Test -Inf in parameter data emitted as '-inf'."""
        model = ModelIR()
        model.params["slo"] = ParameterDef(
            name="slo", domain=("i",), values={("node1",): float("-inf"), ("node2",): 0.0}
        )
        result = emit_original_parameters(model)
        assert "node1 -inf" in result
        # Issue #967: Zero-valued entries are omitted to preserve GAMS sparse semantics
        assert "node2 0" not in result

    def test_inf_scalar(self):
        """Test +Inf scalar emitted as 'inf'."""
        model = ModelIR()
        model.params["bigm"] = ParameterDef(name="bigm", domain=(), values={(): float("inf")})
        result = emit_original_parameters(model)
        assert "bigm /inf/" in result

    def test_nan_parameter_emitted_as_na(self):
        """Test NaN in parameter data emitted as 'na' (GAMS native)."""
        model = ModelIR()
        model.params["p"] = ParameterDef(name="p", domain=("i",), values={("a",): float("nan")})
        result = emit_original_parameters(model)
        assert "a na" in result


@pytest.mark.unit
class TestQuoteAssignmentIndex:
    """Tests for _quote_assignment_index (Issues #886, #912, #916)."""

    def test_already_double_quoted(self):
        assert _quote_assignment_index('"foo"', set()) == '"foo"'

    def test_already_single_quoted(self):
        assert _quote_assignment_index("'foo'", set()) == "'foo'"

    def test_domain_variable_not_quoted(self):
        """Set name in sets_lower stays bare (backward-compatible)."""
        assert _quote_assignment_index("i", {"i", "j"}) == "i"

    def test_domain_variable_with_domain_lower(self):
        """Set name matching domain_lower stays bare."""
        assert _quote_assignment_index("i", {"i", "j"}, frozenset({"i"})) == "i"

    def test_hyphenated_element_quoted(self):
        """Issue #886/#916: period-1 must be quoted."""
        assert _quote_assignment_index("period-1", set()) == "'period-1'"

    def test_plus_element_quoted(self):
        """Elements with + must be quoted."""
        assert _quote_assignment_index("x+1", set()) == "'x+1'"

    def test_set_name_not_quoted_with_domain(self):
        """Set names stay bare even with domain_lower (cross-domain references)."""
        result = _quote_assignment_index("m", {"m", "n", "c"}, frozenset({"c", "*"}))
        assert result == "m"

    def test_literal_element_quoted_with_domain(self):
        """Non-domain, non-set element is quoted when domain context provided."""
        result = _quote_assignment_index("c1", {"m", "c"}, frozenset({"c", "*"}))
        assert result == "'c1'"

    def test_no_domain_context_set_not_quoted(self):
        """Without domain_lower, set names stay bare (backward-compatible)."""
        assert _quote_assignment_index("m", {"m", "n"}) == "m"

    def test_numeric_quoted(self):
        """Numeric-looking indices are quoted."""
        result = _quote_assignment_index("3", set())
        assert result == "'3'"

    def test_wildcard_never_quoted(self):
        """Wildcard '*' should never be quoted (universal set reference)."""
        assert _quote_assignment_index("*", set()) == "*"
        assert _quote_assignment_index("*", {"m"}, frozenset({"c"})) == "*"

    def test_hyphenated_domain_variable_quoted(self):
        """Domain variable names that need quoting are quoted via _quote_symbol."""
        # A hypothetical domain variable 'i-alias' contains a hyphen
        result = _quote_assignment_index("i-alias", {"i-alias"})
        assert result == "'i-alias'"


class TestEmitSetAssignmentsDeferral:
    """Issue #1007: Test .l-referencing set assignment deferral."""

    def _make_model_with_set_assignments(self, assignments: list[SetAssignment]) -> ModelIR:
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["a", "b"], domain=("*",))
        model.set_assignments = assignments
        return model

    def test_direct_varref_deferred(self):
        """Set assignment with VarRef attribute is deferred."""
        # it(i) = yes$(e.l(i))
        sa = SetAssignment(
            set_name="it",
            indices=("i",),
            expr=DollarConditional(
                value_expr=Const(1.0),
                condition=VarRef("e", ("i",), attribute="l"),
            ),
            location=None,
        )
        model = self._make_model_with_set_assignments([sa])

        # no_varref_attr should skip it
        result = emit_set_assignments(model, varref_filter="no_varref_attr")
        assert result == ""

        # only_varref_attr should emit it
        result = emit_set_assignments(model, varref_filter="only_varref_attr")
        assert "it(i)" in result

        # all should emit it
        result = emit_set_assignments(model, varref_filter="all")
        assert "it(i)" in result

    def test_transitive_dependency_deferred(self):
        """Set assignment depending on a deferred set is also deferred."""
        # it(i) = yes$(e.l(i))  -- direct VarRef
        sa_it = SetAssignment(
            set_name="it",
            indices=("i",),
            expr=DollarConditional(
                value_expr=Const(1.0),
                condition=VarRef("e", ("i",), attribute="l"),
            ),
            location=None,
        )
        # inn(i) = not it(i)  -- transitive dependency via SetMembershipTest
        sa_in = SetAssignment(
            set_name="inn",
            indices=("i",),
            expr=Unary("not", SetMembershipTest("it", (SymbolRef("i"),))),
            location=None,
        )
        model = self._make_model_with_set_assignments([sa_it, sa_in])

        # no_varref_attr should skip both
        result = emit_set_assignments(model, varref_filter="no_varref_attr")
        assert result == ""

        # only_varref_attr should emit both
        result = emit_set_assignments(model, varref_filter="only_varref_attr")
        assert "it(i)" in result
        assert "inn(i)" in result

    def test_non_varref_not_deferred(self):
        """Set assignment without VarRef is emitted in no_varref_attr pass."""
        # ku(i) = yes$(ord(i) < card(i))
        sa = SetAssignment(
            set_name="ku",
            indices=("i",),
            expr=DollarConditional(
                value_expr=Const(1.0),
                condition=Binary(
                    "<", Call("ord", (SymbolRef("i"),)), Call("card", (SymbolRef("i"),))
                ),
            ),
            location=None,
        )
        model = self._make_model_with_set_assignments([sa])

        result = emit_set_assignments(model, varref_filter="no_varref_attr")
        assert "ku(i)" in result

        result = emit_set_assignments(model, varref_filter="only_varref_attr")
        assert result == ""

    def test_invalid_varref_filter_raises(self):
        """Invalid varref_filter raises ValueError."""
        model = self._make_model_with_set_assignments([])
        with pytest.raises(ValueError, match="Invalid varref_filter"):
            emit_set_assignments(model, varref_filter="invalid")


class TestCollectMissingParamLabels:
    """Issue #1007: Test detection of labels lost by zero-filtering."""

    def test_all_zero_row_detected(self):
        """All-zero first-dimension label in *-domain param is detected."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["a", "b"], domain=("*",))
        model.params["zz"] = ParameterDef(
            name="zz",
            domain=("*", "i"),
            values={
                ("alpha", "a"): 1.0,
                ("alpha", "b"): 2.0,
                ("beta", "a"): 0.0,
                ("beta", "b"): 0.0,
            },
        )
        missing = collect_missing_param_labels(model)
        assert missing == {"beta"}

    def test_mixed_zero_nonzero_not_missing(self):
        """Label with at least one non-zero value is not missing."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["a", "b"], domain=("*",))
        model.params["zz"] = ParameterDef(
            name="zz",
            domain=("*", "i"),
            values={
                ("alpha", "a"): 0.0,
                ("alpha", "b"): 3.0,  # non-zero
            },
        )
        missing = collect_missing_param_labels(model)
        assert missing == set()

    def test_named_domain_not_tracked(self):
        """Parameters with named set first domain are not tracked."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["a", "b"], domain=("*",))
        model.params["mat"] = ParameterDef(
            name="mat",
            domain=("i", "i"),
            values={
                ("a", "a"): 0.0,
                ("a", "b"): 0.0,
            },
        )
        missing = collect_missing_param_labels(model)
        assert missing == set()

    def test_no_zero_values_no_missing(self):
        """Parameter with all non-zero values has no missing labels."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["a", "b"], domain=("*",))
        model.params["zz"] = ParameterDef(
            name="zz",
            domain=("*", "i"),
            values={
                ("alpha", "a"): 1.0,
                ("alpha", "b"): 2.0,
            },
        )
        missing = collect_missing_param_labels(model)
        assert missing == set()

    def test_wildcard_last_dim_quoted_literal_all_zero(self):
        """Quoted literal at non-first wildcard position with all-zero data is missing."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["a", "b"])
        model.params["tbl"] = ParameterDef(
            name="tbl",
            domain=("i", "*"),
            values={("a", "col1"): 1.0, ("b", "col2"): 0.0},
        )
        model.params["out"] = ParameterDef(
            name="out",
            domain=("i",),
            values={},
            expressions=[
                (
                    ("i",),
                    Binary("-", ParamRef("tbl", ("i", '"col1"')), ParamRef("tbl", ("i", '"col2"'))),
                ),
            ],
        )
        missing = collect_missing_param_labels(model)
        assert "col2" in missing

    def test_wildcard_index_variable_not_treated_as_missing(self):
        """Set/index variable at wildcard position should NOT be flagged as missing."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["a", "b"])
        model.sets["j"] = SetDef(name="j", members=["x", "y"])
        model.params["tbl"] = ParameterDef(
            name="tbl",
            domain=("i", "*"),
            values={("a", "x"): 1.0},
        )
        model.params["out"] = ParameterDef(
            name="out",
            domain=("i",),
            values={},
            expressions=[
                (("i",), ParamRef("tbl", ("i", "j"))),
            ],
        )
        missing = collect_missing_param_labels(model)
        assert "j" not in missing


@pytest.mark.unit
class TestSubsetValueAssignments:
    """Tests for emit_subset_value_assignments().

    Subcategory B: When parameter values have keys that are set/alias names
    (subset-qualified), they are emitted as executable assignments, not inline
    data. Mixed keys (some set names, some literals) must keep set names bare
    and quote literals appropriately.
    """

    def test_mixed_key_subset_stays_bare(self):
        """Test that subset name in mixed key is emitted bare, not quoted.

        vbar1(i,jwt) with value ('ii', '3') = 0 where ii is a subset of i.
        Should emit: vbar1(ii,'3') = 0;  (ii bare, '3' quoted)
        NOT: vbar1('ii','3') = 0;  (which causes GAMS $170 domain violation)
        """
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["ACT", "COM", "FAC"], domain=("*",))
        model.sets["ii"] = SetDef(name="ii", members=["ACT", "COM"], domain=("i",))
        model.sets["jwt"] = SetDef(name="jwt", members=["1", "2", "3"], domain=("*",))
        model.params["vbar1"] = ParameterDef(
            name="vbar1",
            domain=("i", "jwt"),
            values={("ii", "3"): 0.0},
        )

        result = emit_subset_value_assignments(model)
        assert "vbar1(ii," in result
        # ii should NOT be quoted
        assert "vbar1('ii'" not in result

    def test_pure_subset_key_stays_bare(self):
        """Test that pure subset keys (all elements are set names) stay bare.

        red(ii,jj) = 1 where ii and jj are subsets — both should be bare.
        """
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["ACT", "COM"], domain=("*",))
        model.sets["ii"] = SetDef(name="ii", members=["ACT", "COM"], domain=("i",))
        model.aliases["jj"] = AliasDef(name="jj", target="ii")
        model.params["red"] = ParameterDef(
            name="red",
            domain=("i", "i"),
            values={("ii", "jj"): 1.0},
        )

        result = emit_subset_value_assignments(model)
        assert "red(ii,jj)" in result
        assert "red('ii'" not in result


class TestEmitSetAssignmentsOnlyIndices:
    """Issue #881: Test only_indices filtering in emit_set_assignments."""

    def _make_model(self) -> ModelIR:
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["a", "b"], domain=("*",))
        model.sets["ku"] = SetDef(name="ku", members=[], domain=("i",))
        model.sets["ki"] = SetDef(name="ki", members=[], domain=("i",))
        # sa0: ku(i) = yes$(ord(i) < card(i))
        model.set_assignments = [
            SetAssignment(
                set_name="ku",
                indices=("i",),
                expr=DollarConditional(
                    value_expr=Const(1.0),
                    condition=Binary(
                        "<", Call("ord", (SymbolRef("i"),)), Call("card", (SymbolRef("i"),))
                    ),
                ),
                location=None,
            ),
            # sa1: ki(i) = yes$(ord(i) = 1)
            SetAssignment(
                set_name="ki",
                indices=("i",),
                expr=DollarConditional(
                    value_expr=Const(1.0),
                    condition=Binary("=", Call("ord", (SymbolRef("i"),)), Const(1.0)),
                ),
                location=None,
            ),
        ]
        return model

    def test_only_indices_subset(self):
        """only_indices=[0] emits only the first set assignment."""
        model = self._make_model()
        result = emit_set_assignments(model, varref_filter="all", only_indices=[0])
        assert "ku(i)" in result
        assert "ki(i)" not in result

    def test_only_indices_empty(self):
        """only_indices=[] emits nothing."""
        model = self._make_model()
        result = emit_set_assignments(model, varref_filter="all", only_indices=[])
        assert result == ""

    def test_only_indices_none_emits_all(self):
        """only_indices=None (default) emits all set assignments."""
        model = self._make_model()
        result = emit_set_assignments(model, varref_filter="all")
        assert "ku(i)" in result
        assert "ki(i)" in result


class TestSubsetValueAssignmentsExcludeParams:
    """Issue #881: Test exclude_params in emit_subset_value_assignments."""

    def test_excluded_param_skipped(self):
        """Param in exclude_params is not emitted."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["ACT", "COM"], domain=("*",))
        model.sets["ii"] = SetDef(name="ii", members=["ACT", "COM"], domain=("i",))
        model.params["gamma"] = ParameterDef(
            name="gamma",
            domain=("i",),
            values={("ii",): 0.0},
        )

        # Without exclusion, gamma is emitted
        result = emit_subset_value_assignments(model)
        assert "gamma(ii)" in result

        # With exclusion, gamma is skipped
        result = emit_subset_value_assignments(model, exclude_params={"gamma"})
        assert "gamma" not in result

    def test_non_excluded_param_still_emitted(self):
        """Params not in exclude_params are still emitted."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["ACT", "COM"], domain=("*",))
        model.sets["ii"] = SetDef(name="ii", members=["ACT", "COM"], domain=("i",))
        model.params["alpha"] = ParameterDef(
            name="alpha",
            domain=("i",),
            values={("ii",): 1.0},
        )
        model.params["beta"] = ParameterDef(
            name="beta",
            domain=("i",),
            values={("ii",): 2.0},
        )

        result = emit_subset_value_assignments(model, exclude_params={"alpha"})
        assert "alpha" not in result
        assert "beta(ii)" in result


class TestEmitInterleavedParamsAndSets:
    """Issue #881: Tests for emit_interleaved_params_and_sets."""

    def test_chain_ordering(self):
        """Set assignment must be emitted between params that depend on it.

        Chain: T0 = sam/scale → red(i)$(T0(i) < 0) = yes → redsam(i)$red = T0(i)
        The interleaved emitter must produce: T0 before red, red before redsam.
        """
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["a", "b"], domain=("*",))
        model.sets["red"] = SetDef(name="red", members=[], domain=("i",))

        # T0(i) = sam(i) / scalesam  (simple param dep)
        model.params["sam"] = ParameterDef(
            name="sam", domain=("i",), values={("a",): 10.0, ("b",): -5.0}
        )
        model.params["t0"] = ParameterDef(
            name="t0",
            domain=("i",),
            expressions=[
                (("i",), Binary("/", ParamRef("sam", ("i",)), SymbolRef("scalesam"))),
            ],
        )
        # redsam(i)$red(i) = T0(i)  (LHS conditional on dynamic set)
        model.params["redsam"] = ParameterDef(
            name="redsam",
            domain=("i",),
            values={("ii",): 0},
            expressions=[
                (
                    ("i",),
                    LhsConditionalAssign(
                        rhs=ParamRef("t0", ("i",)),
                        condition=SetMembershipTest("red", (SymbolRef("i"),)),
                    ),
                ),
            ],
        )

        # Set assignment: red(i) = yes$(T0(i) < 0)
        model.set_assignments = [
            SetAssignment(
                set_name="red",
                indices=("i",),
                expr=DollarConditional(
                    value_expr=Const(1.0),
                    condition=Binary("<", ParamRef("t0", ("i",)), Const(0.0)),
                ),
                location=None,
            ),
        ]

        code, param_names, sa_indices = emit_interleaved_params_and_sets(model)
        assert code != "", "Should produce interleaved output"

        # Check ordering: T0 before red, red before redsam
        lines = code.split("\n")
        t0_line = next((i for i, ln in enumerate(lines) if "t0(" in ln.lower()), None)
        red_line = next((i for i, ln in enumerate(lines) if "red(i)" in ln.lower()), None)
        redsam_line = next((i for i, ln in enumerate(lines) if "redsam(" in ln.lower()), None)
        assert t0_line is not None, "T0 should be emitted"
        assert red_line is not None, "red set assignment should be emitted"
        assert redsam_line is not None, "redsam should be emitted"
        assert t0_line < red_line, "T0 must come before red"
        assert red_line < redsam_line, "red must come before redsam"

        assert "t0" in param_names
        assert "redsam" in param_names
        assert 0 in sa_indices

    def test_no_interleaving_without_set_blocked_params(self):
        """Returns empty when no params have LHS conditions on dynamic sets."""
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["a", "b"], domain=("*",))
        model.sets["ku"] = SetDef(name="ku", members=[], domain=("i",))
        model.params["p"] = ParameterDef(
            name="p",
            domain=("i",),
            expressions=[
                (("i",), Binary("*", SymbolRef("i"), Const(2.0))),
            ],
        )
        # Set assignment with no LhsConditionalAssign deps from params
        model.set_assignments = [
            SetAssignment(
                set_name="ku",
                indices=("i",),
                expr=DollarConditional(
                    value_expr=Const(1.0),
                    condition=Binary(
                        "<", Call("ord", (SymbolRef("i"),)), Call("card", (SymbolRef("i"),))
                    ),
                ),
                location=None,
            ),
        ]

        code, param_names, sa_indices = emit_interleaved_params_and_sets(model)
        assert code == ""
        assert param_names == set()
        assert sa_indices == set()

    def test_transitive_deferred_set_excluded(self):
        """Transitive deferred set assignments must be excluded from interleaved output.

        it(i) = yes$(e.l(i))  — directly deferred (VarRef)
        inn(i) = not it(i)    — transitively deferred (depends on deferred set)
        red(i) = yes$(T0(i) < 0) — NOT deferred, should appear in interleaved output
        """
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["a", "b"], domain=("*",))
        model.sets["it"] = SetDef(name="it", members=[], domain=("i",))
        model.sets["inn"] = SetDef(name="inn", members=[], domain=("i",))
        model.sets["red"] = SetDef(name="red", members=[], domain=("i",))
        model.variables["e"] = None  # placeholder to make VarRef valid

        # T0(i) = sam(i) / scalesam
        model.params["sam"] = ParameterDef(
            name="sam", domain=("i",), values={("a",): 10.0, ("b",): -5.0}
        )
        model.params["t0"] = ParameterDef(
            name="t0",
            domain=("i",),
            expressions=[
                (("i",), Binary("/", ParamRef("sam", ("i",)), SymbolRef("scalesam"))),
            ],
        )
        # redsam(i)$red(i) = T0(i)  — LHS condition on dynamic set triggers interleaving
        model.params["redsam"] = ParameterDef(
            name="redsam",
            domain=("i",),
            values={("ii",): 0},
            expressions=[
                (
                    ("i",),
                    LhsConditionalAssign(
                        rhs=ParamRef("t0", ("i",)),
                        condition=SetMembershipTest("red", (SymbolRef("i"),)),
                    ),
                ),
            ],
        )

        model.set_assignments = [
            # SA 0: it(i) = yes$(e.l(i))  — directly deferred (VarRef)
            SetAssignment(
                set_name="it",
                indices=("i",),
                expr=DollarConditional(
                    value_expr=Const(1.0),
                    condition=VarRef("e", ("i",), attribute="l"),
                ),
                location=None,
            ),
            # SA 1: inn(i) = not it(i)  — transitively deferred
            SetAssignment(
                set_name="inn",
                indices=("i",),
                expr=Unary("not", SetMembershipTest("it", (SymbolRef("i"),))),
                location=None,
            ),
            # SA 2: red(i) = yes$(T0(i) < 0)  — NOT deferred
            SetAssignment(
                set_name="red",
                indices=("i",),
                expr=DollarConditional(
                    value_expr=Const(1.0),
                    condition=Binary("<", ParamRef("t0", ("i",)), Const(0.0)),
                ),
                location=None,
            ),
        ]

        code, param_names, sa_indices = emit_interleaved_params_and_sets(model)
        assert code != "", "Should produce interleaved output"

        # SA 0 (it) and SA 1 (inn) should NOT be in the interleaved output
        assert 0 not in sa_indices, "Directly deferred set 'it' must be excluded"
        assert 1 not in sa_indices, "Transitively deferred set 'inn' must be excluded"
        # SA 2 (red) should be included
        assert 2 in sa_indices, "Non-deferred set 'red' must be included"

        # The output should not contain inn or it assignments
        code_lower = code.lower()
        assert "inn(" not in code_lower, "'inn' set assignment must not appear"
        assert "it(" not in code_lower, "'it' set assignment must not appear"

    def test_index_blocked_param_interleaving(self):
        """Issue #1041: index-blocked params trigger interleaving.

        When a set assignment depends on a computed param whose expression keys
        use dynamic set names (or their aliases), the param must be emitted
        before the set assignment even when no LHS-condition-blocked params exist.

        Chain: ii(i) = yes → SAM(ii,jj) recomputed → Abar0(ii,jj) → NONZERO(ii,jj)$(Abar0)
        """
        model = ModelIR()
        model.sets["i"] = SetDef(name="i", members=["a", "b", "total"], domain=("*",))
        model.sets["ii"] = SetDef(name="ii", members=[], domain=("i",))
        model.sets["nonzero"] = SetDef(name="nonzero", members=[], domain=("i", "i"))

        # Alias: jj → ii (so jj is also a dynamic set alias)
        model.aliases["jj"] = AliasDef(name="jj", target="ii")

        # Computed param: abar0(ii,jj) = sam(ii,jj) / sam("total",jj)
        model.params["sam"] = ParameterDef(
            name="sam",
            domain=("i", "i"),
            values={("a", "a"): 1.0, ("a", "b"): 2.0, ("b", "a"): 3.0},
        )
        model.params["abar0"] = ParameterDef(
            name="abar0",
            domain=("i", "i"),
            expressions=[
                (
                    ("ii", "jj"),
                    Binary(
                        "/",
                        ParamRef("sam", ("ii", "jj")),
                        ParamRef("sam", ('"total"', "jj")),
                    ),
                ),
            ],
        )

        # Set assignments: ii(i) = yes, then NONZERO(ii,jj) = yes$(Abar0(ii,jj))
        model.set_assignments = [
            SetAssignment(
                set_name="ii",
                indices=("i",),
                expr=Const(1.0),
                location=None,
            ),
            SetAssignment(
                set_name="nonzero",
                indices=("ii", "jj"),
                expr=DollarConditional(
                    value_expr=Const(1.0),
                    condition=ParamRef("abar0", ("ii", "jj")),
                ),
                location=None,
            ),
        ]

        code, param_names, sa_indices = emit_interleaved_params_and_sets(model)
        assert code != "", "Should produce interleaved output for index-blocked params"

        # abar0 must be emitted (it's index-blocked)
        assert "abar0" in param_names, "abar0 should be in emitted param names"

        # Check ordering: abar0 before NONZERO set assignment
        lines = code.split("\n")
        abar0_line = next((i for i, ln in enumerate(lines) if "abar0(" in ln.lower()), None)
        nonzero_line = next((i for i, ln in enumerate(lines) if "nonzero(" in ln.lower()), None)
        assert abar0_line is not None, "abar0 should be emitted"
        assert nonzero_line is not None, "NONZERO set assignment should be emitted"
        assert abar0_line < nonzero_line, "abar0 must come before NONZERO"


@pytest.mark.unit
class TestLoopTreeToGams:
    """Tests for _loop_tree_to_gams() and related loop emission functions.

    Issue #1025: These functions convert Lark parse trees back to valid GAMS
    syntax for re-emitting loop statements containing parameter assignments.
    """

    def _make_tree(self, data: str, children: list) -> object:
        from lark import Tree

        return Tree(data, children)

    def _make_token(self, type_: str, value: str) -> object:
        from lark import Token

        return Token(type_, value)

    def test_simple_assign_loop(self):
        """Test emission of a simple loop with assignment."""
        from src.emit.original_symbols import _loop_tree_to_gams

        # loop(i, x(i) = 2 ;)
        assign = self._make_tree(
            "assign",
            [
                self._make_tree(
                    "lvalue",
                    [
                        self._make_tree(
                            "symbol_indexed",
                            [
                                self._make_tree("symbol_plain", [self._make_token("ID", "x")]),
                                self._make_tree(
                                    "index_list",
                                    [
                                        self._make_tree(
                                            "index_simple", [self._make_token("ID", "i")]
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
                self._make_token("EQUAL", "="),
                self._make_tree("number", [self._make_token("NUMBER", "2")]),
                self._make_token("SEMICOLON", ";"),
            ],
        )
        body = self._make_tree("loop_body", [assign])
        loop = self._make_tree(
            "loop_stmt",
            [
                self._make_tree("id_list", [self._make_token("ID", "i")]),
                body,
            ],
        )
        result = _loop_tree_to_gams(loop)
        assert result.strip().startswith("loop(i,")
        assert "x(i)" in result
        assert "= 2 ;" in result

    def test_paren_filtered_loop_with_id_index_list(self):
        """Test loop_stmt_paren_filtered: loop((ii,jj)$NONZERO(ii,jj), ...).

        Grammar: LOOP_K "(" "(" id_list ")" DOLLAR ID "(" index_list ")" "," loop_body ")" SEMI
        Lark children: [id_list, DOLLAR, ID, index_list, loop_body]
        """
        from src.emit.original_symbols import _loop_tree_to_gams

        id_list = self._make_tree(
            "id_list",
            [self._make_token("ID", "ii"), self._make_token("ID", "jj")],
        )
        index_list = self._make_tree(
            "index_list",
            [
                self._make_tree("index_simple", [self._make_token("ID", "ii")]),
                self._make_tree("index_simple", [self._make_token("ID", "jj")]),
            ],
        )
        assign = self._make_tree(
            "assign",
            [
                self._make_tree(
                    "lvalue", [self._make_tree("symbol_plain", [self._make_token("ID", "y")])]
                ),
                self._make_token("EQUAL", "="),
                self._make_tree("number", [self._make_token("NUMBER", "0")]),
                self._make_token("SEMICOLON", ";"),
            ],
        )
        body = self._make_tree("loop_body", [assign])
        # Real Lark layout: id_list, DOLLAR token, ID token, index_list, loop_body
        loop = self._make_tree(
            "loop_stmt_paren_filtered",
            [
                id_list,
                self._make_token("DOLLAR", "$"),
                self._make_token("ID", "NONZERO"),
                index_list,
                body,
            ],
        )

        result = _loop_tree_to_gams(loop)
        assert "loop(" in result
        assert "ii,jj" in result
        assert "$NONZERO(ii,jj)" in result

    def test_filtered_loop_with_id_dollar_expr(self):
        """Test loop_stmt_filtered: loop(i$(a > b), ...).

        Grammar: LOOP_K "(" ID DOLLAR "(" expr ")" "," loop_body ")" SEMI
        Lark children: [ID, DOLLAR, expr, loop_body]
        """
        from src.emit.original_symbols import _loop_tree_to_gams

        expr = self._make_tree(
            "expr",
            [
                self._make_tree(
                    "binop",
                    [
                        self._make_token("ID", "a"),
                        self._make_token("GT", ">"),
                        self._make_token("ID", "b"),
                    ],
                )
            ],
        )
        assign = self._make_tree(
            "assign",
            [
                self._make_tree(
                    "lvalue", [self._make_tree("symbol_plain", [self._make_token("ID", "y")])]
                ),
                self._make_token("EQUAL", "="),
                self._make_tree("number", [self._make_token("NUMBER", "0")]),
                self._make_token("SEMICOLON", ";"),
            ],
        )
        body = self._make_tree("loop_body", [assign])
        # Real Lark layout: ID token, DOLLAR token, expr, loop_body
        loop = self._make_tree(
            "loop_stmt_filtered",
            [
                self._make_token("ID", "i"),
                self._make_token("DOLLAR", "$"),
                expr,
                body,
            ],
        )

        result = _loop_tree_to_gams(loop)
        assert "loop(i$(a > b)" in result

    def test_indexed_loop(self):
        """Test loop_stmt_indexed: loop(setname(i,j), ...).

        Grammar: LOOP_K "(" ID "(" id_list ")" "," loop_body ")" SEMI
        Lark children: [ID, id_list, loop_body]
        """
        from src.emit.original_symbols import _loop_tree_to_gams

        id_list = self._make_tree(
            "id_list",
            [self._make_token("ID", "i"), self._make_token("ID", "j")],
        )
        assign = self._make_tree(
            "assign",
            [
                self._make_tree(
                    "lvalue", [self._make_tree("symbol_plain", [self._make_token("ID", "y")])]
                ),
                self._make_token("EQUAL", "="),
                self._make_tree("number", [self._make_token("NUMBER", "1")]),
                self._make_token("SEMICOLON", ";"),
            ],
        )
        body = self._make_tree("loop_body", [assign])
        loop = self._make_tree(
            "loop_stmt_indexed",
            [
                self._make_token("ID", "arc"),
                id_list,
                body,
            ],
        )

        result = _loop_tree_to_gams(loop)
        assert "loop(arc(i,j)" in result

    def test_indexed_filtered_loop(self):
        """Test loop_stmt_indexed_filtered: loop(arc(i,j)$(cond), ...).

        Grammar: LOOP_K "(" ID "(" id_list ")" DOLLAR "(" expr ")" "," loop_body ")" SEMI
        Lark children: [ID, id_list, DOLLAR, expr, loop_body]
        """
        from src.emit.original_symbols import _loop_tree_to_gams

        id_list = self._make_tree(
            "id_list",
            [self._make_token("ID", "i"), self._make_token("ID", "j")],
        )
        expr = self._make_tree(
            "expr",
            [
                self._make_tree(
                    "binop",
                    [
                        self._make_token("ID", "d"),
                        self._make_token("GT", ">"),
                        self._make_token("NUMBER", "0"),
                    ],
                )
            ],
        )
        assign = self._make_tree(
            "assign",
            [
                self._make_tree(
                    "lvalue", [self._make_tree("symbol_plain", [self._make_token("ID", "y")])]
                ),
                self._make_token("EQUAL", "="),
                self._make_tree("number", [self._make_token("NUMBER", "1")]),
                self._make_token("SEMICOLON", ";"),
            ],
        )
        body = self._make_tree("loop_body", [assign])
        loop = self._make_tree(
            "loop_stmt_indexed_filtered",
            [
                self._make_token("ID", "arc"),
                id_list,
                self._make_token("DOLLAR", "$"),
                expr,
                body,
            ],
        )

        result = _loop_tree_to_gams(loop)
        assert "loop(arc(i,j)$(d > 0)" in result

    def test_unaryop_handler(self):
        """Test that unaryop nodes (not 'unary') are handled correctly."""
        from src.emit.original_symbols import _loop_tree_to_gams

        # -x
        unary = self._make_tree(
            "unaryop",
            [self._make_token("MINUS", "-"), self._make_token("ID", "x")],
        )
        result = _loop_tree_to_gams(unary)
        assert result == "- x"

    def test_condition_with_expr_gets_parens(self):
        """Test that condition handler wraps expr children in parentheses."""
        from src.emit.original_symbols import _loop_tree_to_gams

        # $(a > b) — Lark discards anonymous parens, leaving condition > [expr]
        expr = self._make_tree(
            "expr",
            [
                self._make_tree(
                    "binop",
                    [
                        self._make_token("ID", "a"),
                        self._make_token("GT", ">"),
                        self._make_token("ID", "b"),
                    ],
                )
            ],
        )
        cond = self._make_tree(
            "condition",
            [self._make_token("DOLLAR", "$"), expr],
        )
        result = _loop_tree_to_gams(cond)
        assert result == "$(a > b)"

    def test_condition_without_expr_no_extra_parens(self):
        """Test that condition without expr child doesn't add extra parens."""
        from src.emit.original_symbols import _loop_tree_to_gams

        # $NONZERO — condition with plain ID, no parens needed
        cond = self._make_tree(
            "condition",
            [self._make_token("DOLLAR", "$"), self._make_token("ID", "NONZERO")],
        )
        result = _loop_tree_to_gams(cond)
        assert result == "$NONZERO"

    def test_sum_handler(self):
        """Test emission of sum(domain, expr)."""
        from src.emit.original_symbols import _loop_tree_to_gams

        # sum(i, x(i))
        domain = self._make_tree(
            "sum_domain",
            [self._make_tree("index_simple", [self._make_token("ID", "i")])],
        )
        body = self._make_tree(
            "symbol_indexed",
            [
                self._make_tree("symbol_plain", [self._make_token("ID", "x")]),
                self._make_tree(
                    "index_list",
                    [
                        self._make_tree("index_simple", [self._make_token("ID", "i")]),
                    ],
                ),
            ],
        )
        sum_node = self._make_tree("sum", [domain, body])
        result = _loop_tree_to_gams(sum_node)
        assert result == "sum(i, x(i))"

    def test_prod_handler(self):
        """Test emission of prod(domain, expr)."""
        from src.emit.original_symbols import _loop_tree_to_gams

        domain = self._make_tree(
            "sum_domain",
            [self._make_tree("index_simple", [self._make_token("ID", "j")])],
        )
        body = self._make_tree("symbol_plain", [self._make_token("ID", "y")])
        prod_node = self._make_tree("prod", [domain, body])
        result = _loop_tree_to_gams(prod_node)
        assert result == "prod(j, y)"

    def test_dollar_cond_handler(self):
        """Test emission of dollar_cond: term$term."""
        from src.emit.original_symbols import _loop_tree_to_gams

        # x$y
        node = self._make_tree(
            "dollar_cond",
            [self._make_token("ID", "x"), self._make_token("ID", "y")],
        )
        result = _loop_tree_to_gams(node)
        assert result == "x$y"

    def test_dollar_cond_paren_handler(self):
        """Test emission of dollar_cond_paren: term$(expr)."""
        from src.emit.original_symbols import _loop_tree_to_gams

        # x$(a > 0)
        inner = self._make_tree(
            "binop",
            [
                self._make_token("ID", "a"),
                self._make_token("GT", ">"),
                self._make_token("NUMBER", "0"),
            ],
        )
        node = self._make_tree(
            "dollar_cond_paren",
            [self._make_token("ID", "x"), inner],
        )
        result = _loop_tree_to_gams(node)
        assert result == "x$(a > 0)"

    def test_bracket_expr_handler(self):
        """Test emission of bracket_expr: [expr]."""
        from src.emit.original_symbols import _loop_tree_to_gams

        inner = self._make_tree(
            "binop",
            [
                self._make_token("ID", "a"),
                self._make_token("PLUS", "+"),
                self._make_token("ID", "b"),
            ],
        )
        node = self._make_tree("bracket_expr", [inner])
        result = _loop_tree_to_gams(node)
        assert result == "[a + b]"

    def test_brace_expr_handler(self):
        """Test emission of brace_expr: {expr}."""
        from src.emit.original_symbols import _loop_tree_to_gams

        inner = self._make_token("ID", "x")
        node = self._make_tree("brace_expr", [inner])
        result = _loop_tree_to_gams(node)
        assert result == "{x}"

    def test_yes_cond_handler(self):
        """Test emission of yes$cond."""
        from src.emit.original_symbols import _loop_tree_to_gams

        cond = self._make_tree(
            "condition",
            [self._make_token("DOLLAR", "$"), self._make_token("ID", "flag")],
        )
        node = self._make_tree("yes_cond", [cond])
        result = _loop_tree_to_gams(node)
        assert result == "yes$flag"

    def test_no_cond_handler(self):
        """Test emission of no$cond."""
        from src.emit.original_symbols import _loop_tree_to_gams

        cond = self._make_tree(
            "condition",
            [self._make_token("DOLLAR", "$"), self._make_token("ID", "flag")],
        )
        node = self._make_tree("no_cond", [cond])
        result = _loop_tree_to_gams(node)
        assert result == "no$flag"

    def test_compile_const_handler(self):
        """Test emission of compile-time constant %name%."""
        from src.emit.original_symbols import _loop_tree_to_gams

        path = self._make_tree(
            "compile_const_path",
            [self._make_token("ID", "myconst")],
        )
        node = self._make_tree("compile_const", [path])
        result = _loop_tree_to_gams(node)
        assert result == "%myconst%"

    def test_tuple_domain_cond_skips_dollar_token(self):
        """Test tuple_domain_cond correctly skips DOLLAR token at children[1].

        Grammar: "(" index_spec ")" DOLLAR expr -> tuple_domain_cond
        Lark children: [index_spec, DOLLAR, expr]
        The condition expr is at children[2], NOT children[1] (which is DOLLAR).
        """
        from src.emit.original_symbols import _loop_tree_to_gams

        index_spec = self._make_tree(
            "index_list",
            [
                self._make_tree("index_simple", [self._make_token("ID", "i")]),
                self._make_tree("index_simple", [self._make_token("ID", "j")]),
            ],
        )
        cond_expr = self._make_tree(
            "binop",
            [
                self._make_token("ID", "d"),
                self._make_token("GT", ">"),
                self._make_token("NUMBER", "0"),
            ],
        )
        node = self._make_tree(
            "tuple_domain_cond",
            [index_spec, self._make_token("DOLLAR", "$"), cond_expr],
        )
        result = _loop_tree_to_gams(node)
        assert result == "(i,j)$(d > 0)"

    def test_sum_with_tuple_domain_cond(self):
        """Test sum(domain, expr) where domain is tuple_domain_cond.

        Validates the full sum((i,j)$cond, expr) pattern doesn't produce
        garbled output like (i,j)$$.
        """
        from src.emit.original_symbols import _loop_tree_to_gams

        index_spec = self._make_tree(
            "index_list",
            [
                self._make_tree("index_simple", [self._make_token("ID", "i")]),
                self._make_tree("index_simple", [self._make_token("ID", "j")]),
            ],
        )
        cond_expr = self._make_tree(
            "binop",
            [
                self._make_token("ID", "d"),
                self._make_token("GT", ">"),
                self._make_token("NUMBER", "0"),
            ],
        )
        domain = self._make_tree(
            "tuple_domain_cond",
            [index_spec, self._make_token("DOLLAR", "$"), cond_expr],
        )
        body = self._make_tree(
            "symbol_indexed",
            [
                self._make_tree("symbol_plain", [self._make_token("ID", "x")]),
                self._make_tree(
                    "index_list",
                    [
                        self._make_tree("index_simple", [self._make_token("ID", "i")]),
                        self._make_tree("index_simple", [self._make_token("ID", "j")]),
                    ],
                ),
            ],
        )
        sum_node = self._make_tree("sum", [domain, body])
        result = _loop_tree_to_gams(sum_node)
        assert result == "sum((i,j)$(d > 0), x(i,j))"

    def test_index_simple_with_linear_lead(self):
        """index_simple with lag/lead suffix preserves offset (e.g. t+1)."""
        from src.emit.original_symbols import _loop_tree_to_gams

        suffix = self._make_tree(
            "linear_lead",
            [self._make_token("PLUS", "+"), self._make_token("NUMBER", "1")],
        )
        node = self._make_tree("index_simple", [self._make_token("ID", "t"), suffix])
        result = _loop_tree_to_gams(node)
        assert result == "t+1"

    def test_index_simple_with_circular_lag(self):
        """index_simple with circular lag suffix (e.g. j--2)."""
        from src.emit.original_symbols import _loop_tree_to_gams

        suffix = self._make_tree(
            "circular_lag",
            [self._make_token("CIRCULAR_LAG", "--"), self._make_token("NUMBER", "2")],
        )
        node = self._make_tree("index_simple", [self._make_token("ID", "j"), suffix])
        result = _loop_tree_to_gams(node)
        assert result == "j--2"

    def test_bound_indexed(self):
        """bound_indexed emits ID.BOUND_K(index_list) e.g. x.l(i)."""
        from src.emit.original_symbols import _loop_tree_to_gams

        idx = self._make_tree(
            "index_list",
            [self._make_tree("index_simple", [self._make_token("ID", "i")])],
        )
        node = self._make_tree(
            "bound_indexed",
            [self._make_token("ID", "x"), self._make_token("BOUND_K", "l"), idx],
        )
        result = _loop_tree_to_gams(node)
        assert result == "x.l(i)"

    def test_bound_scalar(self):
        """bound_scalar emits ID.BOUND_K e.g. z.fx."""
        from src.emit.original_symbols import _loop_tree_to_gams

        node = self._make_tree(
            "bound_scalar",
            [self._make_token("ID", "z"), self._make_token("BOUND_K", "fx")],
        )
        result = _loop_tree_to_gams(node)
        assert result == "z.fx"

    def test_set_attr(self):
        """set_attr emits ID.SET_ATTR_K e.g. i.ord."""
        from src.emit.original_symbols import _loop_tree_to_gams

        node = self._make_tree(
            "set_attr",
            [self._make_token("ID", "i"), self._make_token("SET_ATTR_K", "ord")],
        )
        result = _loop_tree_to_gams(node)
        assert result == "i.ord"

    def test_attr_access_indexed(self):
        """attr_access_indexed emits ID.ID(index_list) e.g. x.val(i)."""
        from src.emit.original_symbols import _loop_tree_to_gams

        idx = self._make_tree(
            "index_list",
            [self._make_tree("index_simple", [self._make_token("ID", "i")])],
        )
        node = self._make_tree(
            "attr_access_indexed",
            [self._make_token("ID", "x"), self._make_token("ID", "val"), idx],
        )
        result = _loop_tree_to_gams(node)
        assert result == "x.val(i)"

    def test_func_call_without_arg_list_emits_empty_parens(self):
        """func_call without arg_list should emit FUNCNAME() without error."""
        from src.emit.original_symbols import _loop_tree_to_gams

        # Grammar allows: func_call -> FUNCNAME arg_list?
        # Cover the case where arg_list is omitted entirely.
        node = self._make_tree("func_call", [self._make_token("FUNCNAME", "foo")])
        result = _loop_tree_to_gams(node)
        assert result == "foo()"

    def test_index_subset(self):
        """index_subset emits name(index_list) e.g. low(n,nn)."""
        from src.emit.original_symbols import _loop_tree_to_gams

        idx = self._make_tree(
            "index_list",
            [
                self._make_tree("index_simple", [self._make_token("ID", "n")]),
                self._make_tree("index_simple", [self._make_token("ID", "nn")]),
            ],
        )
        node = self._make_tree("index_subset", [self._make_token("ID", "low"), idx])
        result = _loop_tree_to_gams(node)
        assert result == "low(n,nn)"

    def test_index_subset_with_lag_lead(self):
        """index_subset with lag/lead suffix e.g. nh(i+1)."""
        from src.emit.original_symbols import _loop_tree_to_gams

        idx = self._make_tree(
            "index_list",
            [self._make_tree("index_simple", [self._make_token("ID", "i")])],
        )
        suffix = self._make_tree(
            "linear_lead",
            [self._make_token("PLUS", "+"), self._make_token("NUMBER", "1")],
        )
        node = self._make_tree("index_subset", [self._make_token("ID", "nh"), idx, suffix])
        result = _loop_tree_to_gams(node)
        assert result == "nh(i)+1"

    def test_offset_paren(self):
        """offset_paren emits (expr) e.g. (ord(n)-1)."""
        from src.emit.original_symbols import _loop_tree_to_gams

        inner = self._make_tree(
            "binop",
            [
                self._make_tree(
                    "func_call",
                    [
                        self._make_token("FUNCNAME", "ord"),
                        self._make_tree("arg_list", [self._make_token("ID", "n")]),
                    ],
                ),
                self._make_token("MINUS", "-"),
                self._make_tree("number", [self._make_token("NUMBER", "1")]),
            ],
        )
        node = self._make_tree("offset_paren", [inner])
        result = _loop_tree_to_gams(node)
        assert result == "(ord(n) - 1)"

    def test_yes_value(self):
        """yes_value emits bare 'yes'."""
        from src.emit.original_symbols import _loop_tree_to_gams

        node = self._make_tree("yes_value", [])
        result = _loop_tree_to_gams(node)
        assert result == "yes"

    def test_no_value(self):
        """no_value emits bare 'no'."""
        from src.emit.original_symbols import _loop_tree_to_gams

        node = self._make_tree("no_value", [])
        result = _loop_tree_to_gams(node)
        assert result == "no"


@pytest.mark.unit
class TestLoopContainsSolve:
    """Tests for _loop_contains_solve()."""

    def test_loop_with_solve_returns_true(self):
        """Loop body with a solve node should be detected.

        The grammar aliases solve_stmt -> solve, and the parser unwraps
        loop_body so body_stmts contains the inner statements directly.
        """
        from lark import Tree

        from src.ir.symbols import LoopStatement

        solve = Tree("solve", [])
        loop = LoopStatement(
            indices=("i",),
            body_stmts=[solve],
            location=None,
            raw_node=Tree("loop_stmt", []),
        )
        from src.emit.original_symbols import _loop_contains_solve

        assert _loop_contains_solve(loop) is True

    def test_loop_without_solve_returns_false(self):
        """Loop body without solve_stmt should return False."""
        from lark import Tree

        from src.ir.symbols import LoopStatement

        assign = Tree("assign", [])
        loop = LoopStatement(
            indices=("i",),
            body_stmts=[assign],
            location=None,
            raw_node=Tree("loop_stmt", []),
        )
        from src.emit.original_symbols import _loop_contains_solve

        assert _loop_contains_solve(loop) is False


@pytest.mark.unit
class TestEmitLoopStatements:
    """Tests for emit_loop_statements()."""

    def test_empty_loop_statements(self):
        """Empty loop_statements returns empty string."""
        from src.emit.original_symbols import emit_loop_statements

        model = ModelIR()
        assert emit_loop_statements(model) == ""

    def test_loop_with_no_raw_node_skipped(self):
        """Loop without raw_node is skipped."""
        from src.emit.original_symbols import emit_loop_statements
        from src.ir.symbols import LoopStatement

        model = ModelIR()
        model.loop_statements = [
            LoopStatement(indices=("i",), body_stmts=[], location=None, raw_node=None)
        ]
        assert emit_loop_statements(model) == ""

    def test_while_stmt_skipped(self):
        """while_stmt nodes are skipped in emit_loop_statements."""
        from lark import Tree

        from src.emit.original_symbols import emit_loop_statements
        from src.ir.symbols import LoopStatement

        model = ModelIR()
        while_node = Tree("while_stmt", [])
        model.loop_statements = [
            LoopStatement(
                indices=("i",),
                body_stmts=[],
                location=None,
                raw_node=while_node,
            )
        ]
        assert emit_loop_statements(model) == ""

    def test_loop_with_solve_skipped(self):
        """Loops containing solve statements are skipped."""
        from lark import Tree

        from src.emit.original_symbols import emit_loop_statements
        from src.ir.symbols import LoopStatement

        model = ModelIR()
        solve = Tree("solve", [])
        loop_node = Tree("loop_stmt", [])
        model.loop_statements = [
            LoopStatement(
                indices=("i",),
                body_stmts=[solve],
                location=None,
                raw_node=loop_node,
            )
        ]
        assert emit_loop_statements(model) == ""

    def test_loop_with_non_param_assign_skipped(self):
        """Loops with display/execute/put statements are skipped."""
        from lark import Token, Tree

        from src.emit.original_symbols import emit_loop_statements
        from src.ir.symbols import LoopStatement

        model = ModelIR()
        model.params["wbar3"] = ParameterDef(name="wbar3", domain=("i",), values={})
        # Body contains a display statement, not a parameter assignment
        display = Tree("display_stmt", [Token("ID", "x")])
        loop_node = Tree(
            "loop_stmt",
            [
                Tree("id_list", [Token("ID", "i")]),
                Tree("loop_body", [display]),
            ],
        )
        model.loop_statements = [
            LoopStatement(
                indices=("i",),
                body_stmts=[display],
                location=None,
                raw_node=loop_node,
            )
        ]
        assert emit_loop_statements(model) == ""

    def test_loop_assigning_variable_skipped(self):
        """Loops assigning to variables (not params) are skipped."""
        from lark import Token, Tree

        from src.emit.original_symbols import emit_loop_statements
        from src.ir.symbols import LoopStatement

        model = ModelIR()
        # No params declared — the loop body assigns to 'x' which is not a param
        assign = Tree(
            "assign",
            [
                Tree("lvalue", [Tree("symbol_plain", [Token("ID", "x")])]),
                Token("EQUAL", "="),
                Tree("number", [Token("NUMBER", "0")]),
                Token("SEMICOLON", ";"),
            ],
        )
        loop_node = Tree(
            "loop_stmt",
            [
                Tree("id_list", [Token("ID", "i")]),
                Tree("loop_body", [assign]),
            ],
        )
        model.loop_statements = [
            LoopStatement(
                indices=("i",),
                body_stmts=[assign],
                location=None,
                raw_node=loop_node,
            )
        ]
        assert emit_loop_statements(model) == ""

    def test_loop_assigning_param_emitted(self):
        """Loops assigning only to known params are emitted."""
        from lark import Token, Tree

        from src.emit.original_symbols import emit_loop_statements
        from src.ir.symbols import LoopStatement

        model = ModelIR()
        model.params["wbar3"] = ParameterDef(name="wbar3", domain=("i",), values={})
        assign = Tree(
            "assign",
            [
                Tree(
                    "lvalue",
                    [
                        Tree(
                            "symbol_indexed",
                            [
                                Tree("symbol_plain", [Token("ID", "wbar3")]),
                                Tree(
                                    "index_list",
                                    [Tree("index_simple", [Token("ID", "i")])],
                                ),
                            ],
                        )
                    ],
                ),
                Token("EQUAL", "="),
                Tree("number", [Token("NUMBER", "1")]),
                Token("SEMICOLON", ";"),
            ],
        )
        loop_node = Tree(
            "loop_stmt",
            [
                Tree("id_list", [Token("ID", "i")]),
                Tree("loop_body", [assign]),
            ],
        )
        model.loop_statements = [
            LoopStatement(
                indices=("i",),
                body_stmts=[assign],
                location=None,
                raw_node=loop_node,
            )
        ]
        result = emit_loop_statements(model)
        assert "loop(" in result
        assert "wbar3(i)" in result


class TestVarLevelLoopStatements:
    """Tests for variable .l loop emission (Issue #1088)."""

    @staticmethod
    def _make_var_level_assign(var_name: str, bound_kind: str = "l"):
        """Build a mock assign tree: var_name.bound_kind(t) = expr."""
        from lark import Token, Tree

        return Tree(
            "assign",
            [
                Tree(
                    "lvalue",
                    [
                        Tree(
                            "bound_indexed",
                            [
                                Token("ID", var_name),
                                Token("BOUND_K", bound_kind),
                                Tree(
                                    "index_list",
                                    [Tree("index_simple", [Token("ID", "t")])],
                                ),
                            ],
                        )
                    ],
                ),
                Token("EQUAL", "="),
                Tree("number", [Token("NUMBER", "1")]),
                Token("SEMICOLON", ";"),
            ],
        )

    @staticmethod
    def _make_param_assign(param_name: str):
        """Build a mock assign tree: param_name(t) = expr."""
        from lark import Token, Tree

        return Tree(
            "assign",
            [
                Tree(
                    "lvalue",
                    [
                        Tree(
                            "symbol_indexed",
                            [
                                Tree("symbol_plain", [Token("ID", param_name)]),
                                Tree(
                                    "index_list",
                                    [Tree("index_simple", [Token("ID", "t")])],
                                ),
                            ],
                        )
                    ],
                ),
                Token("EQUAL", "="),
                Tree("number", [Token("NUMBER", "1")]),
                Token("SEMICOLON", ";"),
            ],
        )

    def test_loop_body_only_var_level_assigns_basic(self):
        """Loop with a single var .l assign is detected."""
        from src.emit.original_symbols import _loop_body_only_var_level_assigns
        from src.ir.symbols import LoopStatement

        assign = self._make_var_level_assign("r")
        loop = LoopStatement(indices=("t",), body_stmts=[assign], location=None, raw_node=None)
        assert _loop_body_only_var_level_assigns(loop, {"r"})

    def test_loop_body_only_var_level_assigns_rejects_non_l(self):
        """Loop with .fx (not .l) assign is rejected."""
        from src.emit.original_symbols import _loop_body_only_var_level_assigns
        from src.ir.symbols import LoopStatement

        assign = self._make_var_level_assign("r", bound_kind="fx")
        loop = LoopStatement(indices=("t",), body_stmts=[assign], location=None, raw_node=None)
        assert not _loop_body_only_var_level_assigns(loop, {"r"})

    def test_loop_body_only_var_level_assigns_rejects_param(self):
        """Loop with parameter assign (not var .l) is rejected."""
        from src.emit.original_symbols import _loop_body_only_var_level_assigns
        from src.ir.symbols import LoopStatement

        assign = self._make_param_assign("myparam")
        loop = LoopStatement(indices=("t",), body_stmts=[assign], location=None, raw_node=None)
        assert not _loop_body_only_var_level_assigns(loop, {"r"})

    def test_loop_body_mixed_rejects(self):
        """Loop with mixed param + var .l assigns is rejected."""
        from src.emit.original_symbols import _loop_body_only_var_level_assigns
        from src.ir.symbols import LoopStatement

        assign_l = self._make_var_level_assign("r")
        assign_p = self._make_param_assign("myparam")
        loop = LoopStatement(
            indices=("t",),
            body_stmts=[assign_l, assign_p],
            location=None,
            raw_node=None,
        )
        assert not _loop_body_only_var_level_assigns(loop, {"r"})

    def test_loop_body_conditional_var_level(self):
        """Conditional var .l assign (conditional_assign_general) is accepted."""
        from lark import Token, Tree

        from src.emit.original_symbols import _loop_body_only_var_level_assigns
        from src.ir.symbols import LoopStatement

        assign = Tree(
            "conditional_assign_general",
            [
                Tree(
                    "lvalue",
                    [
                        Tree(
                            "bound_indexed",
                            [
                                Token("ID", "x"),
                                Token("BOUND_K", "l"),
                                Tree(
                                    "index_list",
                                    [Tree("index_simple", [Token("ID", "t")])],
                                ),
                            ],
                        )
                    ],
                ),
                Token("DOLLAR", "$"),
                Token("EQUAL", "="),
                Tree("number", [Token("NUMBER", "1")]),
            ],
        )
        loop = LoopStatement(indices=("t",), body_stmts=[assign], location=None, raw_node=None)
        assert _loop_body_only_var_level_assigns(loop, {"x"})

    def test_get_var_level_loop_varnames(self):
        """Collects variable names from qualifying .l loops."""
        from lark import Token, Tree

        from src.emit.original_symbols import get_var_level_loop_varnames
        from src.ir.symbols import LoopStatement, VariableDef

        model = ModelIR()
        model.variables["r"] = VariableDef(name="r", domain=("t",))
        assign = self._make_var_level_assign("r")
        loop_node = Tree(
            "loop_stmt",
            [
                Tree("id_list", [Token("ID", "t")]),
                Tree("loop_body", [assign]),
            ],
        )
        model.loop_statements = [
            LoopStatement(
                indices=("t",),
                body_stmts=[assign],
                location=None,
                raw_node=loop_node,
            )
        ]
        result = get_var_level_loop_varnames(model)
        assert result == {"r"}

    def test_get_var_level_loop_varnames_skips_while(self):
        """while_stmt loops are excluded from var level collection."""
        from lark import Tree

        from src.emit.original_symbols import get_var_level_loop_varnames
        from src.ir.symbols import LoopStatement, VariableDef

        model = ModelIR()
        model.variables["r"] = VariableDef(name="r", domain=("t",))
        assign = self._make_var_level_assign("r")
        while_node = Tree("while_stmt", [])
        model.loop_statements = [
            LoopStatement(
                indices=("t",),
                body_stmts=[assign],
                location=None,
                raw_node=while_node,
            )
        ]
        assert get_var_level_loop_varnames(model) == set()

    def test_emit_var_level_loop_statements_basic(self):
        """Qualifying var .l loop is emitted."""
        from lark import Token, Tree

        from src.emit.original_symbols import emit_var_level_loop_statements
        from src.ir.symbols import LoopStatement, VariableDef

        model = ModelIR()
        model.variables["r"] = VariableDef(name="r", domain=("t",))
        assign = self._make_var_level_assign("r")
        loop_node = Tree(
            "loop_stmt",
            [
                Tree("id_list", [Token("ID", "t")]),
                Tree("loop_body", [assign]),
            ],
        )
        model.loop_statements = [
            LoopStatement(
                indices=("t",),
                body_stmts=[assign],
                location=None,
                raw_node=loop_node,
            )
        ]
        result = emit_var_level_loop_statements(model)
        assert "loop(" in result
        assert "r" in result

    def test_emit_var_level_loop_statements_empty(self):
        """No loops returns empty string."""
        from src.emit.original_symbols import emit_var_level_loop_statements

        model = ModelIR()
        assert emit_var_level_loop_statements(model) == ""

    def test_emit_var_level_loop_skips_param_only(self):
        """Parameter-only loops are not emitted by var level emitter."""
        from lark import Token, Tree

        from src.emit.original_symbols import emit_var_level_loop_statements
        from src.ir.symbols import LoopStatement, VariableDef

        model = ModelIR()
        model.variables["r"] = VariableDef(name="r", domain=("t",))
        model.params["myparam"] = ParameterDef(name="myparam", domain=("t",), values={})
        assign = self._make_param_assign("myparam")
        loop_node = Tree(
            "loop_stmt",
            [
                Tree("id_list", [Token("ID", "t")]),
                Tree("loop_body", [assign]),
            ],
        )
        model.loop_statements = [
            LoopStatement(
                indices=("t",),
                body_stmts=[assign],
                location=None,
                raw_node=loop_node,
            )
        ]
        assert emit_var_level_loop_statements(model) == ""


class TestLoopAttrAccessEmission:
    """Tests for attr_access handling in loop body emission (Issue: harker fix)."""

    def test_attr_access_emits_dot(self):
        """attr_access node should emit 'model.attr', not 'model attr'."""
        from lark import Token, Tree

        from src.emit.original_symbols import _loop_tree_to_gams

        node = Tree("attr_access", [Token("ID", "harkoli"), Token("ID", "objVal")])
        assert _loop_tree_to_gams(node) == "harkoli.objVal"

    def test_attr_access_indexed_emits_dot_with_indices(self):
        """attr_access_indexed should emit 'model.attr(idx)'."""
        from lark import Token, Tree

        from src.emit.original_symbols import _loop_tree_to_gams

        idx = Tree("index_list", [Tree("index_simple", [Token("ID", "i")])])
        node = Tree(
            "attr_access_indexed",
            [Token("ID", "x"), Token("ID", "scaleOpt"), idx],
        )
        assert _loop_tree_to_gams(node) == "x.scaleOpt(i)"

    def test_set_attr_emits_dot(self):
        """set_attr node should emit 'i.ord'."""
        from lark import Token, Tree

        from src.emit.original_symbols import _loop_tree_to_gams

        node = Tree("set_attr", [Token("ID", "i"), Token("SET_ATTR_K", "ord")])
        assert _loop_tree_to_gams(node) == "i.ord"

    def test_model_attr_assignment_filtered(self):
        """Assignments referencing model attributes should be skipped."""
        from lark import Token, Tree

        from src.emit.original_symbols import emit_pre_solve_param_assignments
        from src.ir.symbols import LoopStatement

        assign = Tree(
            "assign",
            [
                Tree("lvalue", [Token("ID", "objold")]),
                Token("EQUALS", "="),
                Tree(
                    "attr_access",
                    [Token("ID", "m"), Token("ID", "objVal")],
                ),
                Token("SEMICOLON", ";"),
            ],
        )

        model = ModelIR()
        model.sets["iter"] = SetDef(name="iter", domain=(), members=["i1", "i2"])
        model.params["objold"] = ParameterDef(name="objold", domain=(), values={(): 0.0})
        model.model_equation_map["m"] = ["eq1"]

        solve = Tree("solve", [Token("ID", "m")])
        body = Tree("loop_body", [assign, solve])
        loop_node = Tree(
            "loop_stmt",
            [
                Token("LOOP", "loop"),
                Tree("id_list", [Token("ID", "iter")]),
                body,
            ],
        )
        model.loop_statements = [
            LoopStatement(
                indices=("iter",),
                body_stmts=[assign, solve],
                location=None,
                raw_node=loop_node,
            )
        ]

        result = emit_pre_solve_param_assignments(model)
        assert "objold" not in result
        assert "objVal" not in result

    def test_non_model_attr_not_filtered(self):
        """Non-model attr_access (e.g., x.scaleOpt) should still be emitted."""
        from lark import Token, Tree

        from src.emit.original_symbols import emit_pre_solve_param_assignments
        from src.ir.symbols import LoopStatement

        assign = Tree(
            "assign",
            [
                Tree("lvalue", [Token("ID", "myparam")]),
                Token("EQUALS", "="),
                Tree(
                    "attr_access",
                    [Token("ID", "x"), Token("ID", "scaleOpt")],
                ),
                Token("SEMICOLON", ";"),
            ],
        )

        model = ModelIR()
        model.sets["iter"] = SetDef(name="iter", domain=(), members=["i1"])
        model.params["myparam"] = ParameterDef(name="myparam", domain=(), values={(): 0.0})
        model.model_equation_map["mymodel"] = ["eq1"]

        solve = Tree("solve", [Token("ID", "mymodel")])
        body = Tree("loop_body", [assign, solve])
        loop_node = Tree(
            "loop_stmt",
            [
                Token("LOOP", "loop"),
                Tree("id_list", [Token("ID", "iter")]),
                body,
            ],
        )
        model.loop_statements = [
            LoopStatement(
                indices=("iter",),
                body_stmts=[assign, solve],
                location=None,
                raw_node=loop_node,
            )
        ]

        result = emit_pre_solve_param_assignments(model)
        assert "myparam" in result
        assert "x.scaleOpt" in result


@pytest.mark.unit
class TestSanitizeUelElement:
    """#1280: `_sanitize_uel_element` quotes UEL registry labels with known exceptions.

    The generic `_sanitize_set_element` treats a dot as GAMS tuple notation
    (so `x1.l` is left unquoted). That's wrong for the `nlp2mcp_uel_registry`
    set whose members are LITERAL attribute-access strings produced by
    zero-filtered parameter lookups — GAMS interprets them as tuple UELs and
    either rejects the declaration or silently truncates to the first
    component. The UEL-specific helper therefore forces quoting for ordinary
    unquoted labels, while preserving two shapes as-is:
      - labels already wrapped in single quotes by the base sanitizer
        (e.g., `'foo-bar'`, `'SAE 10'`); re-quoting would produce
        `''foo-bar''`.
      - the GUSS 3-tuple trailing-dot form `rapscenarios.scenario.''`
        (see issue #910 for the canonical shape); outer quotes would
        collapse it to the scalar label `'rapscenarios.scenario.'''`,
        losing the tuple semantics.
    """

    def test_dotted_attribute_label_gets_quoted(self):
        """`x1.l` → `'x1.l'` (the #1280 bug)."""
        assert _sanitize_uel_element("x1.l") == "'x1.l'"
        assert _sanitize_uel_element("x2.l") == "'x2.l'"
        assert _sanitize_uel_element("y.m") == "'y.m'"

    def test_plain_identifier_gets_quoted(self):
        """Plain identifiers are still quoted (GAMS accepts 'foo' === foo)."""
        assert _sanitize_uel_element("demand") == "'demand'"
        assert _sanitize_uel_element("i1") == "'i1'"

    def test_prequoted_element_passes_through(self):
        """Already-quoted labels are returned as-is, not double-quoted."""
        assert _sanitize_uel_element("'SAE 10'") == "'SAE 10'"
        assert _sanitize_uel_element("'max-stock'") == "'max-stock'"

    def test_element_with_hyphen_gets_single_quoted(self):
        """Hyphenated labels (already quoted by the base sanitizer) stay as single-quoted."""
        assert _sanitize_uel_element("gov-expend") == "'gov-expend'"

    def test_element_with_plus_gets_single_quoted(self):
        assert _sanitize_uel_element("food+agr") == "'food+agr'"

    def test_reserved_constants_get_quoted(self):
        """Reserved constants (already quoted by base) remain quoted, not double-quoted."""
        assert _sanitize_uel_element("inf") == "'inf'"
        assert _sanitize_uel_element("na") == "'na'"

    def test_dangerous_chars_still_rejected(self):
        """`_sanitize_uel_element` routes through `_sanitize_set_element` first,
        so injection-dangerous characters are still rejected."""
        with pytest.raises(ValueError, match="unsafe characters"):
            _sanitize_uel_element("bad;element")
        with pytest.raises(ValueError, match="unsafe characters"):
            _sanitize_uel_element("bad/element")

    def test_guss_trailing_dot_preserved(self):
        """GUSS 3-tuple with empty trailing component (e.g.,
        `rapscenarios.scenario.''`) must keep its `.''` structure — the UEL
        helper should not re-quote that compound form.
        """
        assert _sanitize_uel_element("foo.") == "foo.''"

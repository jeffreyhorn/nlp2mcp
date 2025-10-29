"""
Tests for Alias Resolution (Day 6)

Test Coverage:
-------------
1. Simple alias resolution (alias to direct set)
2. Chained aliases (alias to alias)
3. Alias with universe constraints
4. Circular alias detection
5. Alias not found error handling
6. Variables using aliased sets
7. Equations using aliased sets
"""

import pytest

from src.ad.index_mapping import (
    build_index_mapping,
    enumerate_variable_instances,
    resolve_set_members,
)
from src.ir.model_ir import ModelIR
from src.ir.symbols import AliasDef, EquationDef, Rel, SetDef, VariableDef

pytestmark = pytest.mark.unit

# ============================================================================
# Test Basic Alias Resolution
# ============================================================================


@pytest.mark.unit
class TestBasicAliasResolution:
    """Test basic alias resolution to direct sets."""

    def test_simple_alias_resolution(self):
        """Test alias resolves to target set members."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2", "i3"]))
        model_ir.add_alias(AliasDef("j", "i"))

        members, resolved_name = resolve_set_members("j", model_ir)

        assert members == ["i1", "i2", "i3"]
        assert resolved_name == "i"

    def test_alias_to_empty_set(self):
        """Test alias to set with no members."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", []))
        model_ir.add_alias(AliasDef("j", "i"))

        members, resolved_name = resolve_set_members("j", model_ir)

        assert members == []
        assert resolved_name == "i"

    def test_alias_target_not_found(self):
        """Test error when alias targets non-existent set."""
        model_ir = ModelIR()
        model_ir.add_alias(AliasDef("j", "unknown"))

        try:
            resolve_set_members("j", model_ir)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "not found" in str(e).lower()
            assert "unknown" in str(e)


# ============================================================================
# Test Chained Aliases
# ============================================================================


@pytest.mark.unit
class TestChainedAliases:
    """Test resolution of alias chains (alias to alias)."""

    def test_two_level_alias_chain(self):
        """Test alias pointing to another alias."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2"]))
        model_ir.add_alias(AliasDef("j", "i"))  # j → i
        model_ir.add_alias(AliasDef("k", "j"))  # k → j → i

        members, resolved_name = resolve_set_members("k", model_ir)

        assert members == ["i1", "i2"]
        assert resolved_name == "i"

    def test_three_level_alias_chain(self):
        """Test longer alias chain."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2", "i3"]))
        model_ir.add_alias(AliasDef("j", "i"))  # j → i
        model_ir.add_alias(AliasDef("k", "j"))  # k → j
        model_ir.add_alias(AliasDef("m", "k"))  # m → k → j → i

        members, resolved_name = resolve_set_members("m", model_ir)

        assert members == ["i1", "i2", "i3"]
        assert resolved_name == "i"

    def test_circular_alias_detected(self):
        """Test that circular aliases raise error."""
        model_ir = ModelIR()
        model_ir.add_alias(AliasDef("j", "k"))  # j → k
        model_ir.add_alias(AliasDef("k", "j"))  # k → j (cycle!)

        try:
            resolve_set_members("j", model_ir)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "circular" in str(e).lower()

    def test_self_referential_alias_detected(self):
        """Test that self-referential alias raises error."""
        model_ir = ModelIR()
        model_ir.add_alias(AliasDef("j", "j"))  # j → j (self-cycle!)

        try:
            resolve_set_members("j", model_ir)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "circular" in str(e).lower()


# ============================================================================
# Test Universe Constraints
# ============================================================================


@pytest.mark.unit
class TestUniverseConstraints:
    """Test alias resolution with universe constraints."""

    def test_alias_with_universe_constraint(self):
        """Test alias with universe restricts members."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2", "i3", "i4"]))
        model_ir.add_set(SetDef("u", ["i1", "i2"]))  # Universe subset
        model_ir.add_alias(AliasDef("j", "i", universe="u"))  # j = i ∩ u

        members, resolved_name = resolve_set_members("j", model_ir)

        # Only members in both i and u
        assert set(members) == {"i1", "i2"}
        assert resolved_name == "i"

    def test_alias_with_disjoint_universe(self):
        """Test alias with completely disjoint universe."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2"]))
        model_ir.add_set(SetDef("u", ["u1", "u2"]))  # No overlap
        model_ir.add_alias(AliasDef("j", "i", universe="u"))

        members, resolved_name = resolve_set_members("j", model_ir)

        # Empty intersection
        assert members == []
        assert resolved_name == "i"

    def test_alias_with_universe_superset(self):
        """Test alias with universe that is a superset (no restriction)."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2"]))
        model_ir.add_set(SetDef("u", ["i1", "i2", "i3", "i4"]))  # Superset
        model_ir.add_alias(AliasDef("j", "i", universe="u"))

        members, resolved_name = resolve_set_members("j", model_ir)

        # All members of i (universe doesn't restrict)
        assert members == ["i1", "i2"]
        assert resolved_name == "i"

    def test_chained_alias_with_universe(self):
        """Test chained alias where intermediate has universe."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2", "i3"]))
        model_ir.add_set(SetDef("u", ["i1", "i2"]))
        model_ir.add_alias(AliasDef("j", "i", universe="u"))  # j = i ∩ u
        model_ir.add_alias(AliasDef("k", "j"))  # k → j

        members, resolved_name = resolve_set_members("k", model_ir)

        # Should get restricted members from j
        assert set(members) == {"i1", "i2"}
        assert resolved_name == "i"

    def test_universe_not_found_raises_error(self):
        """Test error when universe set doesn't exist."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2"]))
        model_ir.add_alias(AliasDef("j", "i", universe="unknown"))

        try:
            resolve_set_members("j", model_ir)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "not found" in str(e).lower()


# ============================================================================
# Test Variables with Aliased Domains
# ============================================================================


@pytest.mark.unit
class TestVariablesWithAliases:
    """Test variable enumeration when domain uses aliases."""

    def test_variable_with_aliased_domain(self):
        """Test variable using alias enumerates correctly."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2", "i3"]))
        model_ir.add_alias(AliasDef("j", "i"))
        var_def = VariableDef("x", ("j",))  # x(j) where j is alias to i

        instances = enumerate_variable_instances(var_def, model_ir)

        assert instances == [("i1",), ("i2",), ("i3",)]

    def test_variable_with_restricted_alias_domain(self):
        """Test variable with alias that has universe constraint."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2", "i3", "i4"]))
        model_ir.add_set(SetDef("u", ["i1", "i2"]))
        model_ir.add_alias(AliasDef("j", "i", universe="u"))
        var_def = VariableDef("x", ("j",))

        instances = enumerate_variable_instances(var_def, model_ir)

        # Only restricted members
        assert set(instances) == {("i1",), ("i2",)}

    def test_variable_with_mixed_alias_and_direct_sets(self):
        """Test variable with both alias and direct set in domain."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2"]))
        model_ir.add_set(SetDef("k", ["k1", "k2"]))
        model_ir.add_alias(AliasDef("j", "i"))
        var_def = VariableDef("x", ("j", "k"))  # x(j,k)

        instances = enumerate_variable_instances(var_def, model_ir)

        expected = [
            ("i1", "k1"),
            ("i1", "k2"),
            ("i2", "k1"),
            ("i2", "k2"),
        ]
        assert instances == expected


# ============================================================================
# Test Complete Mapping with Aliases
# ============================================================================


@pytest.mark.unit
class TestMappingWithAliases:
    """Test building complete index mapping with aliases."""

    def test_complete_mapping_with_aliases(self):
        """Test full index mapping when variables use aliases."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2"]))
        model_ir.add_alias(AliasDef("j", "i"))
        model_ir.add_var(VariableDef("x", ("i",)))  # Direct set
        model_ir.add_var(VariableDef("y", ("j",)))  # Aliased set

        mapping = build_index_mapping(model_ir)

        # Total: 2 + 2 = 4 variables
        assert mapping.num_vars == 4

        # Check that both enumerate correctly
        assert mapping.get_col_id("x", ("i1",)) is not None
        assert mapping.get_col_id("x", ("i2",)) is not None
        assert mapping.get_col_id("y", ("i1",)) is not None
        assert mapping.get_col_id("y", ("i2",)) is not None

    def test_equations_with_aliased_domains(self):
        """Test equation enumeration with aliased domains."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2"]))
        model_ir.add_alias(AliasDef("j", "i"))
        model_ir.add_equation(EquationDef("g", ("j",), Rel.LE, (None, None)))

        mapping = build_index_mapping(model_ir)

        # 2 equation instances
        assert mapping.num_eqs == 2
        assert mapping.get_row_id("g", ("i1",)) is not None
        assert mapping.get_row_id("g", ("i2",)) is not None

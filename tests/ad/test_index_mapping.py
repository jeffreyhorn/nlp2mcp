"""
Tests for Index Mapping and Alias Resolution (Day 6)

Test Coverage:
-------------
1. Scalar variable enumeration
2. Single-index variable enumeration
3. Multi-index variable enumeration
4. Equation enumeration (scalar and indexed)
5. Complete index mapping construction
6. Column/row ID lookups (bijective mapping)
7. Deterministic ordering (reproducibility)
8. Cross-product generation
"""

from src.ad.index_mapping import (
    build_index_mapping,
    enumerate_equation_instances,
    enumerate_variable_instances,
    resolve_set_members,
)
from src.ir.model_ir import ModelIR
from src.ir.symbols import EquationDef, Rel, SetDef, VariableDef

# ============================================================================
# Test Set Member Resolution
# ============================================================================


class TestSetMemberResolution:
    """Test resolving set and alias names to concrete members."""

    def test_direct_set_resolution(self):
        """Test resolving a direct set returns its members."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2", "i3"]))

        members, resolved_name = resolve_set_members("i", model_ir)

        assert members == ["i1", "i2", "i3"]
        assert resolved_name == "i"

    def test_set_not_found_raises_error(self):
        """Test that resolving a non-existent set raises ValueError."""
        model_ir = ModelIR()

        try:
            resolve_set_members("unknown", model_ir)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "not found" in str(e).lower()
            assert "unknown" in str(e)


# ============================================================================
# Test Variable Enumeration
# ============================================================================


class TestVariableEnumeration:
    """Test enumeration of variable instances."""

    def test_scalar_variable(self):
        """Test scalar variable returns single empty tuple."""
        model_ir = ModelIR()
        var_def = VariableDef("x", ())

        instances = enumerate_variable_instances(var_def, model_ir)

        assert instances == [()]

    def test_single_index_variable(self):
        """Test variable with single index."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2", "i3"]))
        var_def = VariableDef("x", ("i",))

        instances = enumerate_variable_instances(var_def, model_ir)

        assert instances == [("i1",), ("i2",), ("i3",)]
        # Should be sorted
        assert instances == sorted(instances)

    def test_two_index_variable(self):
        """Test variable with two indices (cross-product)."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2"]))
        model_ir.add_set(SetDef("j", ["j1", "j2"]))
        var_def = VariableDef("x", ("i", "j"))

        instances = enumerate_variable_instances(var_def, model_ir)

        expected = [
            ("i1", "j1"),
            ("i1", "j2"),
            ("i2", "j1"),
            ("i2", "j2"),
        ]
        assert instances == expected
        # Should be sorted (lexicographic)
        assert instances == sorted(instances)

    def test_three_index_variable(self):
        """Test variable with three indices."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2"]))
        model_ir.add_set(SetDef("j", ["j1"]))
        model_ir.add_set(SetDef("k", ["k1", "k2"]))
        var_def = VariableDef("x", ("i", "j", "k"))

        instances = enumerate_variable_instances(var_def, model_ir)

        # 2 * 1 * 2 = 4 instances
        assert len(instances) == 4
        assert ("i1", "j1", "k1") in instances
        assert ("i1", "j1", "k2") in instances
        assert ("i2", "j1", "k1") in instances
        assert ("i2", "j1", "k2") in instances
        # Should be sorted
        assert instances == sorted(instances)

    def test_empty_set_raises_error(self):
        """Test that variable with empty domain set raises error."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", []))  # Empty set
        var_def = VariableDef("x", ("i",))

        try:
            enumerate_variable_instances(var_def, model_ir)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "no members" in str(e).lower()


# ============================================================================
# Test Equation Enumeration
# ============================================================================


class TestEquationEnumeration:
    """Test enumeration of equation instances."""

    def test_scalar_equation(self):
        """Test scalar equation returns single empty tuple."""
        model_ir = ModelIR()

        instances = enumerate_equation_instances("obj", (), model_ir)

        assert instances == [()]

    def test_single_index_equation(self):
        """Test equation with single index."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2"]))

        instances = enumerate_equation_instances("g", ("i",), model_ir)

        assert instances == [("i1",), ("i2",)]

    def test_two_index_equation(self):
        """Test equation with two indices."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2"]))
        model_ir.add_set(SetDef("j", ["j1", "j2"]))

        instances = enumerate_equation_instances("g", ("i", "j"), model_ir)

        expected = [
            ("i1", "j1"),
            ("i1", "j2"),
            ("i2", "j1"),
            ("i2", "j2"),
        ]
        assert instances == expected


# ============================================================================
# Test Complete Index Mapping
# ============================================================================


class TestIndexMapping:
    """Test building complete index mappings."""

    def test_empty_model(self):
        """Test mapping for model with no variables or equations."""
        model_ir = ModelIR()

        mapping = build_index_mapping(model_ir)

        assert mapping.num_vars == 0
        assert mapping.num_eqs == 0
        assert len(mapping.var_to_col) == 0
        assert len(mapping.eq_to_row) == 0

    def test_single_scalar_variable(self):
        """Test mapping with single scalar variable."""
        model_ir = ModelIR()
        model_ir.add_var(VariableDef("x", ()))

        mapping = build_index_mapping(model_ir)

        assert mapping.num_vars == 1
        assert mapping.get_col_id("x", ()) == 0
        assert mapping.get_var_instance(0) == ("x", ())

    def test_multiple_scalar_variables(self):
        """Test mapping with multiple scalar variables (alphabetical order)."""
        model_ir = ModelIR()
        model_ir.add_var(VariableDef("z", ()))
        model_ir.add_var(VariableDef("x", ()))
        model_ir.add_var(VariableDef("y", ()))

        mapping = build_index_mapping(model_ir)

        assert mapping.num_vars == 3
        # Should be sorted alphabetically
        assert mapping.get_col_id("x", ()) == 0
        assert mapping.get_col_id("y", ()) == 1
        assert mapping.get_col_id("z", ()) == 2

    def test_indexed_variable_mapping(self):
        """Test mapping with indexed variable."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2", "i3"]))
        model_ir.add_var(VariableDef("x", ("i",)))

        mapping = build_index_mapping(model_ir)

        assert mapping.num_vars == 3
        assert mapping.get_col_id("x", ("i1",)) == 0
        assert mapping.get_col_id("x", ("i2",)) == 1
        assert mapping.get_col_id("x", ("i3",)) == 2

        # Check reverse mapping
        assert mapping.get_var_instance(0) == ("x", ("i1",))
        assert mapping.get_var_instance(1) == ("x", ("i2",))
        assert mapping.get_var_instance(2) == ("x", ("i3",))

    def test_mixed_scalar_and_indexed_variables(self):
        """Test mapping with mix of scalar and indexed variables."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2"]))
        model_ir.add_var(VariableDef("y", ()))  # Scalar
        model_ir.add_var(VariableDef("x", ("i",)))  # Indexed

        mapping = build_index_mapping(model_ir)

        # Total: 1 scalar + 2 indexed = 3 variables
        assert mapping.num_vars == 3

        # Alphabetical: x comes before y
        assert mapping.get_col_id("x", ("i1",)) == 0
        assert mapping.get_col_id("x", ("i2",)) == 1
        assert mapping.get_col_id("y", ()) == 2

    def test_equation_mapping(self):
        """Test equation instance mapping."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2"]))
        model_ir.add_equation(EquationDef("g", ("i",), Rel.LE, (None, None)))
        model_ir.add_equation(EquationDef("obj", (), Rel.EQ, (None, None)))

        mapping = build_index_mapping(model_ir)

        # 2 g equations + 1 obj equation = 3 total
        assert mapping.num_eqs == 3

        # Alphabetical: g before obj
        assert mapping.get_row_id("g", ("i1",)) == 0
        assert mapping.get_row_id("g", ("i2",)) == 1
        assert mapping.get_row_id("obj", ()) == 2

        # Check reverse mapping
        assert mapping.get_eq_instance(0) == ("g", ("i1",))
        assert mapping.get_eq_instance(1) == ("g", ("i2",))
        assert mapping.get_eq_instance(2) == ("obj", ())

    def test_bijective_mapping(self):
        """Test that variable mapping is bijective (one-to-one)."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2"]))
        model_ir.add_var(VariableDef("x", ("i",)))
        model_ir.add_var(VariableDef("y", ()))

        mapping = build_index_mapping(model_ir)

        # Check forward and reverse consistency
        for col_id in range(mapping.num_vars):
            var_name, indices = mapping.get_var_instance(col_id)
            assert mapping.get_col_id(var_name, indices) == col_id

    def test_deterministic_ordering(self):
        """Test that mapping is deterministic across multiple builds."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i2", "i1", "i3"]))  # Unordered input
        model_ir.add_var(VariableDef("z", ()))
        model_ir.add_var(VariableDef("x", ("i",)))
        model_ir.add_var(VariableDef("y", ()))

        # Build mapping twice
        mapping1 = build_index_mapping(model_ir)
        mapping2 = build_index_mapping(model_ir)

        # Should be identical
        assert mapping1.var_to_col == mapping2.var_to_col
        assert mapping1.col_to_var == mapping2.col_to_var
        assert mapping1.num_vars == mapping2.num_vars

    def test_not_found_returns_none(self):
        """Test that lookup of non-existent variable/equation returns None."""
        model_ir = ModelIR()
        model_ir.add_var(VariableDef("x", ()))

        mapping = build_index_mapping(model_ir)

        assert mapping.get_col_id("y", ()) is None
        assert mapping.get_row_id("g", ()) is None
        assert mapping.get_var_instance(999) is None
        assert mapping.get_eq_instance(999) is None

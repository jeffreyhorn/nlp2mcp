"""Tests for variable scope handling from include files (Issue #418).

This module tests two fixes:
1. The preprocessor inserting missing semicolons before block keywords
2. The ModelIR.add_var() method merging variable kinds when re-declaring

These fixes ensure that variables declared in include files are properly
recognized when referenced in the main file, even when:
- The include file has declaration blocks without trailing semicolons
- Variables are declared with domains, then later marked as positive/binary/etc.
"""

import pytest

from src.ir.model_ir import ModelIR
from src.ir.parser import parse_model_text
from src.ir.preprocessor import insert_missing_semicolons
from src.ir.symbols import VariableDef, VarKind


@pytest.mark.unit
class TestInsertMissingSemicolons:
    """Test the preprocessor function that inserts missing semicolons."""

    def test_inserts_semicolon_before_variables_keyword(self):
        """Test that semicolon is inserted before 'variables' keyword."""
        source = """parameters p(i) test param

variables x(i) test var;"""
        result = insert_missing_semicolons(source)
        assert "test param;" in result
        assert "variables x(i)" in result

    def test_inserts_semicolon_before_equations_keyword(self):
        """Test that semicolon is inserted before 'equations' keyword."""
        source = """variables x test var

equations eq test eq;"""
        result = insert_missing_semicolons(source)
        assert "test var;" in result
        assert "equations eq" in result

    def test_inserts_semicolon_before_positive_keyword(self):
        """Test that semicolon is inserted before 'positive' keyword."""
        source = """variables x(i) test var

positive variables x;"""
        result = insert_missing_semicolons(source)
        assert "test var;" in result
        assert "positive variables x;" in result

    def test_no_duplicate_semicolons(self):
        """Test that no extra semicolons are added when already present."""
        source = """parameters p(i) test param;

variables x(i) test var;"""
        result = insert_missing_semicolons(source)
        # Should not have double semicolons
        assert ";;" not in result
        # Original semicolons preserved
        assert "test param;" in result
        assert "test var;" in result

    def test_handles_empty_lines_and_comments(self):
        """Test that empty lines and comments don't interfere."""
        source = """parameters p(i) test param

* This is a comment

variables x(i) test var;"""
        result = insert_missing_semicolons(source)
        assert "test param;" in result

    def test_poolmod_pattern(self):
        """Test the exact pattern from poolmod.inc that caused issue #418."""
        source = """parameters cl(comp_) min use of raw material
           cu(comp_) max availability of raw material

           psize(pool_) pool capacity


variables  q(comp_, pool_) pool quality from pooling raw materials
           y(pool_, pro_)  flow from pool to product
           z(comp_, pro_)  direct flow of rawmaterials to product
           cost          total cost
positive variables q,y,z;

equations obj objective function;"""
        result = insert_missing_semicolons(source)
        # Semicolon should be added after "pool capacity" before "variables"
        assert "pool capacity;" in result
        # Semicolon should be added after "total cost" before "positive"
        assert "total cost;" in result


@pytest.mark.unit
class TestAddVarMergeKind:
    """Test that add_var merges variable kinds correctly."""

    def test_positive_updates_kind_preserves_domain(self):
        """Test that 'positive variables x' updates kind but preserves domain."""
        model = ModelIR()

        # First declaration: variables x(i,j)
        model.add_var(VariableDef(name="x", domain=("i", "j"), kind=VarKind.CONTINUOUS))
        assert model.variables["x"].domain == ("i", "j")
        assert model.variables["x"].kind == VarKind.CONTINUOUS

        # Second declaration: positive variables x (no domain specified)
        model.add_var(VariableDef(name="x", domain=(), kind=VarKind.POSITIVE))
        # Domain should be preserved, kind should be updated
        assert model.variables["x"].domain == ("i", "j")
        assert model.variables["x"].kind == VarKind.POSITIVE

    def test_binary_updates_kind_preserves_domain(self):
        """Test that 'binary variables y' updates kind but preserves domain."""
        model = ModelIR()

        model.add_var(VariableDef(name="y", domain=("k",), kind=VarKind.CONTINUOUS))
        model.add_var(VariableDef(name="y", domain=(), kind=VarKind.BINARY))

        assert model.variables["y"].domain == ("k",)
        assert model.variables["y"].kind == VarKind.BINARY

    def test_continuous_redeclaration_replaces(self):
        """Test that re-declaring with CONTINUOUS (default) replaces entirely."""
        model = ModelIR()

        model.add_var(VariableDef(name="z", domain=("i",), kind=VarKind.POSITIVE))
        # Re-declare as continuous with different domain - should replace
        model.add_var(VariableDef(name="z", domain=("j",), kind=VarKind.CONTINUOUS))

        assert model.variables["z"].domain == ("j",)
        assert model.variables["z"].kind == VarKind.CONTINUOUS

    def test_scalar_to_indexed_replaces(self):
        """Test that adding indexed version replaces scalar."""
        model = ModelIR()

        model.add_var(VariableDef(name="w", domain=(), kind=VarKind.POSITIVE))
        model.add_var(VariableDef(name="w", domain=("i",), kind=VarKind.POSITIVE))

        assert model.variables["w"].domain == ("i",)
        assert model.variables["w"].kind == VarKind.POSITIVE


@pytest.mark.unit
class TestParserVariableScopeIntegration:
    """Integration tests for variable scope handling through the parser."""

    def test_variables_then_positive_preserves_domain(self):
        """Test parsing 'variables x(i); positive variables x;' preserves domain."""
        source = """Sets i /1*3/;
variables x(i);
positive variables x;"""
        model = parse_model_text(source)

        assert "x" in model.variables
        assert model.variables["x"].domain == ("i",)
        assert model.variables["x"].kind == VarKind.POSITIVE

    def test_multiple_variables_then_positive(self):
        """Test multiple variables declared then marked positive."""
        source = """Sets i /1*3/, j /a,b/;
variables q(i,j), y(j), z(i), cost;
positive variables q, y, z;"""
        model = parse_model_text(source)

        assert model.variables["q"].domain == ("i", "j")
        assert model.variables["q"].kind == VarKind.POSITIVE

        assert model.variables["y"].domain == ("j",)
        assert model.variables["y"].kind == VarKind.POSITIVE

        assert model.variables["z"].domain == ("i",)
        assert model.variables["z"].kind == VarKind.POSITIVE

        # cost was not in positive list, should remain continuous
        assert model.variables["cost"].domain == ()
        assert model.variables["cost"].kind == VarKind.CONTINUOUS

    def test_missing_semicolon_before_variables(self):
        """Test that missing semicolon before 'variables' is handled.

        Note: parse_model_text() doesn't apply preprocessing, so we manually
        call insert_missing_semicolons() to test the full pipeline behavior.
        """
        source = """Sets i /1*3/;
parameters p(i) test param

variables x(i) test var;"""
        # Apply preprocessing to insert missing semicolons
        preprocessed = insert_missing_semicolons(source)
        model = parse_model_text(preprocessed)

        assert "p" in model.params
        assert "x" in model.variables
        assert model.variables["x"].domain == ("i",)

    def test_missing_semicolon_before_positive(self):
        """Test that missing semicolon before 'positive' is handled.

        Note: parse_model_text() doesn't apply preprocessing, so we manually
        call insert_missing_semicolons() to test the full pipeline behavior.
        """
        source = """Sets i /1*3/;
variables x(i) test var

positive variables x;"""
        # Apply preprocessing to insert missing semicolons
        preprocessed = insert_missing_semicolons(source)
        model = parse_model_text(preprocessed)

        assert model.variables["x"].domain == ("i",)
        assert model.variables["x"].kind == VarKind.POSITIVE

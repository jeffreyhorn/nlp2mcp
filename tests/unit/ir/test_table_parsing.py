"""Unit tests for GAMS Table block parsing."""

from __future__ import annotations

import pytest

from src.ir.parser import parse_model_text


class TestSimpleTableParsing:
    """Test basic 2D table parsing."""

    def test_simple_2x2_table(self):
        """Test parsing a simple 2x2 table."""
        gams = """
        Sets
            i /i1, i2/
            j /j1, j2/;

        Table data(i,j)
               j1  j2
        i1     1   2
        i2     3   4;
        """
        model = parse_model_text(gams)

        assert "data" in model.params
        table = model.params["data"]
        assert table.domain == ("i", "j")
        assert table.values == {
            ("i1", "j1"): 1.0,
            ("i1", "j2"): 2.0,
            ("i2", "j1"): 3.0,
            ("i2", "j2"): 4.0,
        }

    def test_simple_3x3_table(self):
        """Test parsing a 3x3 table."""
        gams = """
        Sets
            i /i1, i2, i3/
            j /j1, j2, j3/;

        Table data(i,j)
               j1  j2  j3
        i1     1   2   3
        i2     4   5   6
        i3     7   8   9;
        """
        model = parse_model_text(gams)

        assert "data" in model.params
        table = model.params["data"]
        assert table.domain == ("i", "j")
        assert len(table.values) == 9
        assert table.values[("i2", "j2")] == 5.0
        assert table.values[("i3", "j3")] == 9.0

    def test_table_with_floats(self):
        """Test parsing a table with floating point values."""
        gams = """
        Sets
            i /i1, i2/
            j /j1, j2/;

        Table data(i,j)
               j1    j2
        i1     1.5   2.7
        i2     3.14  4.0;
        """
        model = parse_model_text(gams)

        table = model.params["data"]
        assert table.values[("i1", "j1")] == 1.5
        assert table.values[("i1", "j2")] == 2.7
        assert table.values[("i2", "j1")] == 3.14

    def test_table_case_insensitive(self):
        """Test that Table keyword is case-insensitive."""
        gams = """
        Sets i /i1/ j /j1/;

        table data(i,j)
               j1
        i1     42;
        """
        model = parse_model_text(gams)
        assert "data" in model.params
        assert model.params["data"].values[("i1", "j1")] == 42.0


class TestSparseTableParsing:
    """Test sparse table parsing with missing values."""

    def test_sparse_table_fills_zeros(self):
        """Test that missing cells are filled with 0.0."""
        gams = """
        Sets
            i /i1, i2, i3/
            j /j1, j2, j3/;

        Table sparse_data(i,j)
               j1  j2  j3
        i1     1       3
        i2         5
        i3     7       9;
        """
        model = parse_model_text(gams)

        table = model.params["sparse_data"]
        assert table.values == {
            ("i1", "j1"): 1.0,
            ("i1", "j2"): 0.0,
            ("i1", "j3"): 3.0,
            ("i2", "j1"): 0.0,
            ("i2", "j2"): 5.0,
            ("i2", "j3"): 0.0,
            ("i3", "j1"): 7.0,
            ("i3", "j2"): 0.0,
            ("i3", "j3"): 9.0,
        }

    def test_completely_empty_rows(self):
        """Test table with completely empty rows."""
        gams = """
        Sets
            i /i1, i2, i3/
            j /j1, j2/;

        Table data(i,j)
               j1  j2
        i1     1   2
        i2
        i3     5   6;
        """
        model = parse_model_text(gams)

        table = model.params["data"]
        # i2 row should be all zeros
        assert table.values[("i2", "j1")] == 0.0
        assert table.values[("i2", "j2")] == 0.0
        assert table.values[("i1", "j1")] == 1.0
        assert table.values[("i3", "j2")] == 6.0

    def test_sparse_with_irregular_spacing(self):
        """Test that sparse tables work with irregular whitespace."""
        gams = """
        Sets i /i1, i2/ j /j1, j2, j3/;

        Table data(i,j)
               j1      j2           j3
        i1     10                   30
        i2             20;
        """
        model = parse_model_text(gams)

        table = model.params["data"]
        assert table.values[("i1", "j1")] == 10.0
        assert table.values[("i1", "j2")] == 0.0
        assert table.values[("i1", "j3")] == 30.0
        assert table.values[("i2", "j1")] == 0.0
        assert table.values[("i2", "j2")] == 20.0
        assert table.values[("i2", "j3")] == 0.0


class TestTableWithDescriptiveText:
    """Test table parsing with descriptive text."""

    def test_table_with_description(self):
        """Test that descriptive text after table name is handled."""
        gams = """
        Sets
            i /i1, i2/
            j /j1, j2, j3/;

        Table data(i,j) "This is a descriptive text for the table"
               j1  j2  j3
        i1     10  20  30
        i2     40  50  60;
        """
        model = parse_model_text(gams)

        table = model.params["data"]
        assert table.domain == ("i", "j")
        assert table.values == {
            ("i1", "j1"): 10.0,
            ("i1", "j2"): 20.0,
            ("i1", "j3"): 30.0,
            ("i2", "j1"): 40.0,
            ("i2", "j2"): 50.0,
            ("i2", "j3"): 60.0,
        }

    def test_table_with_single_quotes(self):
        """Test descriptive text with single quotes."""
        gams = """
        Sets i /i1/ j /j1/;

        Table data(i,j) 'Single quoted description'
               j1
        i1     99;
        """
        model = parse_model_text(gams)
        assert model.params["data"].values[("i1", "j1")] == 99.0

    def test_table_no_domain_with_description_string(self):
        """Issue #713: Table without explicit domain but with description string.

        The description string on the same line as the table name should be
        skipped and not consumed as a row label or column header.
        """
        gams = """
        Table td 'target data'
                  1     2     3
        icbm   0.05  0.00  0.00
        mrbm   0.16  0.17  0.15;
        """
        model = parse_model_text(gams)
        table = model.params["td"]
        assert table.domain == ("*", "*")
        assert table.values[("icbm", "1")] == 0.05
        assert table.values[("mrbm", "2")] == 0.17
        assert ("target data", "1") not in table.values


class TestMultiDimensionalKeys:
    """Test that multi-dimensional keys are formatted correctly as tuples."""

    def test_2d_keys_are_tuples(self):
        """Test that 2D table keys are proper tuples."""
        gams = """
        Sets i /i1/ j /j1/;

        Table data(i,j)
               j1
        i1     5;
        """
        model = parse_model_text(gams)

        keys = list(model.params["data"].values.keys())
        assert len(keys) == 1
        assert keys[0] == ("i1", "j1")
        assert isinstance(keys[0], tuple)
        assert len(keys[0]) == 2

    def test_keys_match_domain_order(self):
        """Test that keys follow domain order (row, col)."""
        gams = """
        Sets
            rows /r1, r2/
            cols /c1, c2/;

        Table matrix(rows, cols)
               c1  c2
        r1     1   2
        r2     3   4;
        """
        model = parse_model_text(gams)

        table = model.params["matrix"]
        # First element of tuple should be row index
        assert ("r1", "c1") in table.values
        assert ("r2", "c2") in table.values


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_table(self):
        """Test table with no data rows (grammar requires at least headers)."""
        gams = """
        Sets i /i1/ j /j1/;

        Table data(i,j)
               j1;
        """
        model = parse_model_text(gams)

        assert "data" in model.params
        table = model.params["data"]
        assert table.domain == ("i", "j")
        # No data rows means empty values
        assert len(table.values) == 0

    def test_table_with_only_headers(self):
        """Test table with only column headers, no data."""
        gams = """
        Sets i /i1/ j /j1, j2/;

        Table data(i,j)
               j1  j2;
        """
        model = parse_model_text(gams)

        assert "data" in model.params
        # Should have empty values since no data rows
        assert len(model.params["data"].values) == 0

    def test_negative_values(self):
        """Test table with negative values."""
        gams = """
        Sets i /i1, i2/ j /j1, j2/;

        Table data(i,j)
               j1    j2
        i1     -5    10
        i2     15   -20;
        """
        model = parse_model_text(gams)

        table = model.params["data"]
        assert table.values[("i1", "j1")] == -5.0
        assert table.values[("i2", "j2")] == -20.0

    def test_scientific_notation(self):
        """Test table with scientific notation."""
        gams = """
        Sets i /i1/ j /j1, j2/;

        Table data(i,j)
               j1      j2
        i1     1.5e-3  2.0e+4;
        """
        model = parse_model_text(gams)

        table = model.params["data"]
        assert table.values[("i1", "j1")] == pytest.approx(0.0015)
        assert table.values[("i1", "j2")] == pytest.approx(20000.0)

    def test_single_column_table(self):
        """Test table with only one column."""
        gams = """
        Sets i /i1, i2, i3/ j /j1/;

        Table data(i,j)
               j1
        i1     10
        i2     20
        i3     30;
        """
        model = parse_model_text(gams)

        table = model.params["data"]
        assert len(table.values) == 3
        assert table.values[("i1", "j1")] == 10.0
        assert table.values[("i2", "j1")] == 20.0
        assert table.values[("i3", "j1")] == 30.0

    def test_single_row_table(self):
        """Test table with only one row."""
        gams = """
        Sets i /i1/ j /j1, j2, j3/;

        Table data(i,j)
               j1  j2  j3
        i1     1   2   3;
        """
        model = parse_model_text(gams)

        table = model.params["data"]
        assert len(table.values) == 3
        assert table.values[("i1", "j1")] == 1.0
        assert table.values[("i1", "j2")] == 2.0
        assert table.values[("i1", "j3")] == 3.0


class TestTableIntegration:
    """Test table integration with rest of model."""

    def test_table_with_parameters_and_scalars(self):
        """Test that tables coexist with other parameter types."""
        gams = """
        Sets i /i1, i2/ j /j1, j2/;

        Scalars
            alpha /1.5/
            beta /2.0/;

        Parameters
            single = 10
            indexed(i) /i1 5, i2 7/;

        Table matrix(i,j)
               j1  j2
        i1     1   2
        i2     3   4;
        """
        model = parse_model_text(gams)

        # Check all parameter types exist
        assert "alpha" in model.params
        assert "beta" in model.params
        assert "single" in model.params
        assert "indexed" in model.params
        assert "matrix" in model.params

        # Check table data
        assert model.params["matrix"].values[("i1", "j1")] == 1.0
        assert model.params["matrix"].values[("i2", "j2")] == 4.0

    def test_multiple_tables(self):
        """Test multiple table declarations."""
        gams = """
        Sets
            i /i1, i2/
            j /j1, j2/
            k /k1, k2/;

        Table first(i,j)
               j1  j2
        i1     1   2
        i2     3   4;

        Table second(i,k)
               k1  k2
        i1     10  20
        i2     30  40;
        """
        model = parse_model_text(gams)

        assert "first" in model.params
        assert "second" in model.params

        assert model.params["first"].domain == ("i", "j")
        assert model.params["second"].domain == ("i", "k")

        assert model.params["first"].values[("i1", "j1")] == 1.0
        assert model.params["second"].values[("i2", "k2")] == 40.0

    def test_table_domain_references_sets(self):
        """Test that table domain properly references declared sets."""
        gams = """
        Sets
            plants /p1, p2/
            markets /m1, m2, m3/;

        Table distance(plants, markets) "Distance in km"
               m1    m2    m3
        p1     100   200   150
        p2     300   100   250;
        """
        model = parse_model_text(gams)

        table = model.params["distance"]
        assert table.domain == ("plants", "markets")
        assert table.values[("p1", "m2")] == 200.0
        assert table.values[("p2", "m3")] == 250.0

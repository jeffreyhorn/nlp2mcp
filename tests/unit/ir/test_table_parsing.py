"""Unit tests for GAMS Table block parsing."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.ir.parser import parse_model_file, parse_model_text

_GAMSLIB = Path(__file__).parents[3] / "data" / "gamslib" / "raw"


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

    def test_table_no_domain_with_double_quoted_description(self):
        """Issue #713: Same as above but with double-quoted description string."""
        gams = """
        Table td "target data"
                  1     2
        icbm   0.05  0.00
        mrbm   0.16  0.17;
        """
        model = parse_model_text(gams)
        table = model.params["td"]
        assert table.domain == ("*", "*")
        assert table.values[("icbm", "1")] == 0.05
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


class TestTableContinuationParsing:
    """Tests for ISSUE_392: tables with '+' continuation blocks.

    The GAMS preprocessor (remove_table_continuation_markers) replaces '+' at the start
    of a continuation line with a space, so the entire table collapses into one table_row
    node in the parse tree.  The section-based fix in _handle_table_block() reconstructs
    the original structure from the token line numbers that are still preserved.

    These tests parse the actual GAMSlib source files (like.gms, robert.gms) so that the
    full preprocessor pipeline runs, which is the only way to trigger the continuation
    replacement that the fix addresses.
    """

    @pytest.fixture
    def like_table(self):
        """Parse like.gms and return the 'data' parameter."""
        path = _GAMSLIB / "like.gms"
        if not path.exists():
            pytest.skip(f"GAMSlib raw file not available in this environment: {path}")
        model = parse_model_file(path)
        return model.params["data"]

    @pytest.fixture
    def robert_table(self):
        """Parse robert.gms and return the 'c' parameter."""
        path = _GAMSLIB / "robert.gms"
        if not path.exists():
            pytest.skip(f"GAMSlib raw file not available in this environment: {path}")
        model = parse_model_file(path)
        return model.params["c"]

    def test_like_table_correct_value_count(self, like_table):
        """ISSUE_392: like.gms table data(*,i) parses all 62 values (2 rows x 31 cols)."""
        assert len(like_table.values) == 62

    def test_like_table_section1_first_value(self, like_table):
        """ISSUE_392: First value in section 1 (pressure at col 1) is 95."""
        assert like_table.values[("pressure", "1")] == 95.0

    def test_like_table_section1_last_value(self, like_table):
        """ISSUE_392: Last value in section 1 (pressure at col 15) is 170."""
        assert like_table.values[("pressure", "15")] == 170.0

    def test_like_table_section1_middle_value(self, like_table):
        """ISSUE_392: Middle value in section 1 (pressure col 9) is 140."""
        assert like_table.values[("pressure", "9")] == 140.0

    def test_like_table_section2_first_value(self, like_table):
        """ISSUE_392: First value in section 2 (pressure at col 16) is 175."""
        assert like_table.values[("pressure", "16")] == 175.0

    def test_like_table_section2_last_value(self, like_table):
        """ISSUE_392: Last value in section 2 (frequency at col 31) is 2."""
        assert like_table.values[("frequency", "31")] == 2.0

    def test_like_table_frequency_row_complete(self, like_table):
        """ISSUE_392: frequency row has all 31 values with no gaps."""
        missing = [c for c in range(1, 32) if ("frequency", str(c)) not in like_table.values]
        assert missing == [], f"frequency row missing columns: {missing}"

    def test_like_table_pressure_row_complete(self, like_table):
        """ISSUE_392: pressure row has all 31 values with no gaps."""
        missing = [c for c in range(1, 32) if ("pressure", str(c)) not in like_table.values]
        assert missing == [], f"pressure row missing columns: {missing}"

    def test_robert_table_correct_value_count(self, robert_table):
        """ISSUE_399: robert.gms table c(p,t) parses all 9 values (3 rows x 3 cols)."""
        assert len(robert_table.values) == 9

    def test_robert_table_spot_checks(self, robert_table):
        """ISSUE_399: robert.gms table values match GAMS source."""
        assert robert_table.values[("low", "1")] == 25.0
        assert robert_table.values[("low", "3")] == 10.0
        assert robert_table.values[("medium", "2")] == 50.0
        assert robert_table.values[("high", "1")] == 75.0
        assert robert_table.values[("high", "3")] == 100.0

    def test_robert_table_description_not_in_values(self, robert_table):
        """ISSUE_399: Description string 'expected profits' must not appear as a row label."""
        row_labels = {k[0] for k in robert_table.values}
        assert "expected profits" not in row_labels
        assert "'expected profits'" not in row_labels


class TestDottedColumnHeaders:
    """Tests for dotted compound column headers in multi-dimensional tables.

    When a table like ``Table SAM(u,v,r)`` has column headers ``BRD.JPN``,
    the parser must merge the separate ``BRD`` and ``JPN`` tokens into a
    single compound header ``BRD.JPN``.  The emitter's ``_expand_table_key``
    then splits on dots to reconstruct the full dimension tuple.
    """

    def test_dotted_compound_column_headers(self):
        """Dotted column headers like a.x are merged into compound headers."""
        gams = """\
Sets
    i /i1, i2/
    j /a, b/
    k /x, y/;

Table data(i,j,k)
       a.x  a.y  b.x  b.y
i1      1    2    3    4
i2      5    6    7    8;
"""
        model = parse_model_text(gams)
        table = model.params["data"]
        assert table.domain == ("i", "j", "k")
        assert len(table.values) == 8
        # Keys should be 2-tuples (row_label, compound_col_header)
        assert ("i1", "a.x") in table.values
        assert table.values[("i1", "a.x")] == 1.0
        assert table.values[("i1", "b.y")] == 4.0
        assert table.values[("i2", "a.y")] == 6.0
        assert table.values[("i2", "b.x")] == 7.0

    def test_mixed_dotted_and_simple_headers(self):
        """Only dotted headers are merged; simple ones stay as-is."""
        gams = """\
Sets
    i /i1/
    j /a, bx, c/;

Table data(i,j)
       a  bx  c
i1     1   2  3;
"""
        model = parse_model_text(gams)
        table = model.params["data"]
        assert ("i1", "a") in table.values
        assert ("i1", "bx") in table.values
        assert ("i1", "c") in table.values
        assert len(table.values) == 3

    def test_dotted_row_and_column_headers(self):
        """Both row and column headers can be dotted (4-domain table)."""
        gams = """\
Sets
    a /r1, r2/
    b /s1, s2/
    c /t1, t2/
    d /u1, u2/;

Table data(a,b,c,d)
             t1.u1  t1.u2  t2.u1  t2.u2
r1.s1          1      2      3      4
r1.s2          5      6      7      8
r2.s1          9     10     11     12
r2.s2         13     14     15     16;
"""
        model = parse_model_text(gams)
        table = model.params["data"]
        assert table.domain == ("a", "b", "c", "d")
        assert len(table.values) == 16
        # Both row and column are compound dotted labels
        assert ("r1.s1", "t1.u1") in table.values
        assert table.values[("r1.s1", "t1.u1")] == 1.0
        assert table.values[("r2.s2", "t2.u2")] == 16.0

    def test_three_part_dotted_column_header(self):
        """Three-part dotted column header a.b.c is merged correctly."""
        gams = """\
Sets
    i /r1/
    j /a/
    k /b/
    l /c/;

Table data(i,j,k,l)
       a.b.c
r1       42;
"""
        model = parse_model_text(gams)
        table = model.params["data"]
        assert ("r1", "a.b.c") in table.values
        assert table.values[("r1", "a.b.c")] == 42.0

    def test_twocge_sam_table(self):
        """twocge: SAM(u,v,r) with dotted column headers across continuations.

        Issue #968: Table + continuation sections with dotted column headers
        (e.g. BRD.JPN, BRD.USA) must produce distinct entries for each section.
        Before the fix, USA continuation headers were not detected as secondary
        headers, causing USA values to overwrite JPN values.
        """
        path = _GAMSLIB / "twocge.gms"
        if not path.exists():
            pytest.skip(f"GAMSlib raw file not available: {path}")
        model = parse_model_file(path)
        sam = model.params["sam"]
        assert sam.domain == ("u", "v", "r")
        # All keys should be 2-tuples with dotted compound column headers
        for key in sam.values:
            assert len(key) == 2, f"Expected 2-tuple key, got {key}"
            assert "." in key[1], f"Column header should be compound: {key}"
        # SAM should have at least 60 entries (30 JPN + 30 USA) — not ~30 from a single section
        assert len(sam.values) >= 60

        # Issue #968 regression: Both JPN and USA sections must be present
        col_regions = {key[1].split(".")[-1] for key in sam.values}
        assert "JPN" in col_regions, "JPN section entries missing"
        assert "USA" in col_regions, "USA section entries missing"
        jpn_keys = [k for k in sam.values if k[1].endswith(".JPN")]
        usa_keys = [k for k in sam.values if k[1].endswith(".USA")]
        assert len(jpn_keys) >= 30, f"Expected at least 30 JPN entries, got {len(jpn_keys)}"
        assert len(usa_keys) >= 30, f"Expected at least 30 USA entries, got {len(usa_keys)}"

        # Verify specific cells are not overwritten (JPN and USA have different values)
        assert sam.values[("BRD", "BRD.JPN")] == 21.0
        assert sam.values[("BRD", "BRD.USA")] == 40.0
        assert sam.values[("CAP", "BRD.JPN")] == 20.0
        assert sam.values[("CAP", "BRD.USA")] == 33.0

    def test_tforss_ymf_table(self):
        """tforss: ymf(at,k,s,cl) with dotted 2-part column headers."""
        path = _GAMSLIB / "tforss.gms"
        if not path.exists():
            pytest.skip(f"GAMSlib raw file not available: {path}")
        model = parse_model_file(path)
        ymf = model.params["ymf"]
        assert ymf.domain == ("at", "k", "s", "cl")
        for key in ymf.values:
            assert len(key) == 2, f"Expected 2-tuple key, got {key}"
        assert len(ymf.values) >= 40

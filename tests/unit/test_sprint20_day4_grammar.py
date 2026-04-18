"""Unit tests for Sprint 20 Day 4 grammar additions (Subcategories L, M, H)."""

from lark import Token, Tree

from src.ir.parser import _ModelBuilder, parse_model_text, parse_text


class TestSubcatL:
    """Test Subcat L: Set-Model Exclusion patterns."""

    def test_model_all_except_single(self):
        """Test model with single exclusion: Model m / all - eq1 /;"""
        source = """
        Variables x;
        Equations eq1, eq2;
        eq1.. x =e= 0;
        eq2.. x =e= 1;
        Model m / all - eq1 /;
        """
        result = parse_text(source)
        assert result is not None
        # Verify IR builder sets model_uses_all flag and collects exclusions
        ir = parse_model_text(source)
        assert ir.declared_model == "m"
        assert ir.model_equations == []  # empty for uses_all (exclusions in map)
        assert ir.model_uses_all is True
        # model_equation_map should have all equations minus excluded
        assert "eq1" not in ir.model_equation_map["m"]
        assert "eq2" in ir.model_equation_map["m"]

    def test_model_all_except_multiple(self):
        """Test model with multiple exclusions: Model m / all - eq1 - eq2 /;"""
        source = """
        Equations eq1, eq2, eq3;
        Model m / all - eq1 - eq2 /;
        """
        result = parse_text(source)
        assert result is not None

    def test_extract_model_refs_rewrites_all_subtraction(self):
        """Issue #1266: `/ all - eq1 /` can be parsed as either
        ``model_all_except`` (Lark 1.2+) or ``model_subtraction`` (Lark 1.1.9,
        which CI uses) because the keyword ``all`` also matches ``ID``. The
        IR builder must handle both shapes identically — treating the
        subtraction as an exclusion when the first ID is ``all``.

        This test constructs the "wrong-alternative" tree directly, so the
        defensive code path is pinned regardless of which Lark version the
        runtime picks.
        """
        # Synthesize `model_subtraction` children as Lark 1.1.9 produces
        # them for the input `all - eq1`: two bare ID tokens.
        sub_node = Tree(
            "model_subtraction",
            [Token("ID", "all"), Token("ID", "eq1")],
        )
        ref_list = Tree("model_ref_list", [sub_node])
        refs, uses_all = _ModelBuilder._extract_model_refs(ref_list)
        # Must be treated as `all - eq1`, i.e. uses_all with exclusion of eq1.
        assert uses_all is True
        assert refs == ["eq1"]

    def test_extract_model_refs_genuine_subtraction_still_logs_warning(self):
        """A real `m - n` subtraction (non-"all" first ID) must keep the
        union-fallback behavior so non-"all" cases aren't silently
        reinterpreted. Regression guard for the fix applied for #1266.
        """
        sub_node = Tree(
            "model_subtraction",
            [Token("ID", "m1"), Token("ID", "m2")],
        )
        ref_list = Tree("model_ref_list", [sub_node])
        refs, uses_all = _ModelBuilder._extract_model_refs(ref_list)
        # Both names end up in refs (union-fallback); uses_all stays False.
        assert uses_all is False
        assert refs == ["m1", "m2"]

    def test_model_dotted_ref(self):
        """Test model with dotted eq.var references: Model m / eq.var /;"""
        source = """
        Equations eq1, eq2;
        Variables x, y;
        eq1.. x =e= 0;
        eq2.. y =e= 0;
        Model m / eq1.x, eq2.y /;
        """
        result = parse_text(source)
        assert result is not None
        # Verify IR builder extracts equation names from dotted refs
        ir = parse_model_text(source)
        assert ir.declared_model == "m"
        assert ir.model_equations == ["eq1", "eq2"]
        assert ir.model_uses_all is False

    def test_model_mixed_refs(self):
        """Test model with mixed simple and dotted refs."""
        source = """
        Equations eq1, eq2, eq3;
        Variables x, y, z;
        eq1.. z =e= 0;
        eq2.. x =e= 0;
        eq3.. y =e= 0;
        Model m / eq1, eq2.x, eq3.y /;
        """
        result = parse_text(source)
        assert result is not None
        # Verify IR builder handles mixed ref types
        ir = parse_model_text(source)
        assert ir.declared_model == "m"
        assert ir.model_equations == ["eq1", "eq2", "eq3"]
        assert ir.model_uses_all is False

    def test_multi_model_with_dotted_refs(self):
        """Test multi-model declaration with dotted refs exercises _handle_model_multi."""
        source = """
        Equations eq1, eq2, eq3;
        Variables x, y, z;
        eq1.. x =e= 0;
        eq2.. y =e= 0;
        eq3.. z =e= 0;
        Model
            m1 / eq1.x, eq2.y /
            m2 / eq3.z /;
        """
        result = parse_text(source)
        assert result is not None
        # _handle_model_multi stores the first model's equations
        ir = parse_model_text(source)
        assert ir.model_equations == ["eq1", "eq2"]
        assert ir.model_uses_all is False

    def test_multi_model_with_all(self):
        """Test multi-model declaration where first model uses / all /."""
        source = """
        Equations eq1;
        Model
            m1 / all /
            m2 / eq1 /;
        """
        result = parse_text(source)
        assert result is not None
        ir = parse_model_text(source)
        assert ir.model_equations == []
        assert ir.model_uses_all is True


class TestSubcatM:
    """Test Subcat M: File and Acronym declarations."""

    def test_file_with_description(self):
        """Test File declaration with description: File f 'desc';"""
        source = """
        File repdat 'sensitivity data report file';
        """
        result = parse_text(source)
        assert result is not None
        # Verify IR builder registers the file handle in declared_files
        ir = parse_model_text(source)
        assert "repdat" in ir.declared_files

    def test_file_with_path(self):
        """Test File declaration with path: File f / 'path.txt' /;"""
        source = """
        File output / 'results.txt' /;
        """
        result = parse_text(source)
        assert result is not None

    def test_acronym_declaration(self):
        """Test Acronym declaration: Acronym id1, id2, id3;"""
        source = """
        Acronym future, call, puto;
        """
        result = parse_text(source)
        assert result is not None


class TestSubcatH:
    """Test Subcat H: Control Flow (repeat/until)."""

    def test_repeat_until_simple(self):
        """Test simple repeat/until loop."""
        source = """
        Scalar maxdelta;
        maxdelta = 1;
        repeat
            maxdelta = maxdelta - 0.1;
        until maxdelta < 0.005;
        """
        result = parse_text(source)
        assert result is not None

    def test_repeat_until_multiple_statements(self):
        """Test repeat/until with multiple statements in body."""
        source = """
        Parameters r(i), s(j), oldr(i), olds(j);
        repeat
            oldr(i) = r(i);
            olds(j) = s(j);
            r(i) = r(i) + 1;
            s(j) = s(j) + 1;
        until maxdelta < 0.005;
        """
        result = parse_text(source)
        assert result is not None

    def test_repeat_until_with_display(self):
        """Test repeat/until with display statement."""
        source = """
        Scalar maxdelta;
        repeat
            maxdelta = maxdelta - 0.1;
            display maxdelta;
        until maxdelta < 0.005;
        """
        result = parse_text(source)
        assert result is not None

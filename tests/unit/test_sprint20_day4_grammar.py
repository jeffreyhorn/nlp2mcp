"""Unit tests for Sprint 20 Day 4 grammar additions (Subcategories L, M, H)."""

from src.ir.parser import parse_model_text, parse_text


class TestSubcatL:
    """Test Subcat L: Set-Model Exclusion patterns."""

    def test_model_all_except_single(self):
        """Test model with single exclusion: Model m / all - eq1 /;"""
        source = """
        Equations eq1, eq2;
        Model m / all - eq1 /;
        """
        result = parse_text(source)
        assert result is not None
        # Verify IR builder sets model_uses_all flag
        ir = parse_model_text(source)
        assert ir.declared_model == "m"
        assert ir.model_uses_all is True

    def test_model_all_except_multiple(self):
        """Test model with multiple exclusions: Model m / all - eq1 - eq2 /;"""
        source = """
        Equations eq1, eq2, eq3;
        Model m / all - eq1 - eq2 /;
        """
        result = parse_text(source)
        assert result is not None

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


class TestSubcatM:
    """Test Subcat M: File and Acronym declarations."""

    def test_file_with_description(self):
        """Test File declaration with description: File f 'desc';"""
        source = """
        File repdat 'sensitivity data report file';
        """
        result = parse_text(source)
        assert result is not None

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

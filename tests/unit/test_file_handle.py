"""Unit tests for GAMS File handle declarations (Issue #746/#747).

Tests cover:
- File statement registers handle in declared_files
- File handle attribute access (sol.pc, sol.pw) passes validation
- Multiple file handles in a single model
"""

import pytest

from src.ir.parser import parse_model_text


class TestFileHandleDeclaration:
    """Test that File declarations register handles for validation."""

    def test_file_handle_registered(self):
        """File handle name is added to model.declared_files."""
        source = """
Set i / a, b /;
Parameter p(i) / a 1, b 2 /;
Variable x(i), z;
Equation obj;

obj.. z =e= sum(i, p(i) * x(i));

Model m / all /;
Solve m using NLP minimizing z;

File sol / solution.csv /;
"""
        model = parse_model_text(source)
        assert "sol" in model.declared_files

    def test_file_handle_attr_access(self):
        """File handle attribute assignment (sol.pc = 5) does not raise."""
        source = """
Set i / a, b /;
Parameter p(i) / a 1, b 2 /;
Variable x(i), z;
Equation obj;

obj.. z =e= sum(i, p(i) * x(i));

Model m / all /;
Solve m using NLP minimizing z;

File sol / solution.csv /;
put sol;
sol.pc = 5;
sol.pw = 32767;
"""
        model = parse_model_text(source)
        assert "sol" in model.declared_files

    def test_file_handle_multiple(self):
        """Multiple File declarations are all tracked."""
        source = """
Set i / a, b /;
Parameter p(i) / a 1, b 2 /;
Variable x(i), z;
Equation obj;

obj.. z =e= sum(i, p(i) * x(i));

Model m / all /;
Solve m using NLP minimizing z;

File sol / solution.csv /;
File listA1out / listA1.csv /;
put sol;
sol.pc = 5;
put listA1out;
listA1out.pc = 5;
"""
        model = parse_model_text(source)
        assert "sol" in model.declared_files
        assert "listA1out" in model.declared_files

    def test_undeclared_attr_still_raises(self):
        """Attribute access on an undeclared symbol still raises ParseError."""
        source = """
Set i / a, b /;
Variable x(i), z;
Equation obj;

obj.. z =e= sum(i, x(i));

Model m / all /;
Solve m using NLP minimizing z;

nosuchfile.pc = 5;
"""
        with pytest.raises(Exception, match="nosuchfile"):
            parse_model_text(source)

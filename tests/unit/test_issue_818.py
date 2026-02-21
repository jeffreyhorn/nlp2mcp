"""Unit tests for issue #818 (gussrisk: Set dict scenario mapping syntax).

Tests for:
- Triple-dotted set tuples (a.b.c) in set data
- solve ... scenario dict statement
"""

import pytest

from src.ir.parser import parse_model_text

pytestmark = pytest.mark.unit


class TestTripleDottedSetTuples:
    """Test triple-dotted tuples in set member data."""

    def test_triple_dotted_ids(self):
        """Triple-dotted set member: a.b.c with all IDs."""
        source = """
        Set dict / rap.param.riskaver, invest.level.stockoutput /;
        Variables obj;
        Equations defobj;
        defobj.. obj =e= 0;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "dict" in ir.sets
        members = ir.sets["dict"].members
        assert "rap.param.riskaver" in members
        assert "invest.level.stockoutput" in members

    def test_triple_dotted_with_string(self):
        """Triple-dotted set member: a.b.'' with empty string segment."""
        source = """
        Set dict / rapscenarios.scenario.'' /;
        Variables obj;
        Equations defobj;
        defobj.. obj =e= 0;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "dict" in ir.sets
        members = ir.sets["dict"].members
        assert len(members) == 1
        assert members[0] == "rapscenarios.scenario."


class TestSolveScenario:
    """Test solve ... scenario dict statement."""

    def test_solve_with_scenario(self):
        """solve model using nlp maximizing obj scenario dict parses."""
        source = """
        Set i / a /;
        Set dict / a.param.riskaver /;
        Variables obj;
        Equations defobj;
        defobj.. obj =e= 0;
        Model m / all /;
        solve m using nlp maximizing obj scenario dict;
        """
        ir = parse_model_text(source)
        assert ir.model_name == "m"
        assert ir.objective is not None

    def test_solve_scenario_other_order(self):
        """solve model maximizing obj using nlp scenario dict parses."""
        source = """
        Set i / a /;
        Variables obj;
        Equations defobj;
        defobj.. obj =e= 0;
        Model m / all /;
        solve m maximizing obj using nlp scenario dict;
        """
        ir = parse_model_text(source)
        assert ir.model_name == "m"
        assert ir.objective is not None

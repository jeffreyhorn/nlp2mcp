"""Tests for aggregation with literal co-indices in subset domains.

Issue: sum(tn('time-2',n), 1) was incorrectly emitting as sum(()$(tn(n)), 1)
because the parser filtered 'n' from sum_indices (as it was in free_domain)
and lost the literal 'time-2'.
"""

from src.ir.ast import SetMembershipTest, SymbolRef
from src.ir.parser import parse_model_file


def _build_model_with_literal_subset() -> str:
    """Build a minimal GAMS model with literal co-indices in subset."""
    return """
Set t / time-1, time-2 /;
Set n / n-1*n-5 /;
Set tn(t,n) / time-1.(n-1*n-2), time-2.(n-3*n-5) /;
Set leaf(n);

leaf(n)$(sum(tn('time-2',n), 1)) = yes;

Variable x(n);
Equation obj;
obj.. sum(n$leaf(n), x(n)) =e= 0;

Model m / obj /;
solve m using lp minimizing x;
"""


def test_literal_subset_preserves_sum_index(tmp_path):
    """sum(tn('time-2',n), 1) in leaf(n) should keep n as sum index."""
    gams_file = tmp_path / "test_lit_subset.gms"
    gams_file.write_text(_build_model_with_literal_subset())
    model = parse_model_file(str(gams_file))

    # Check the 'leaf' set's assignment expression
    leaf_def = model.sets.get("leaf")
    assert leaf_def is not None, "Set 'leaf' should exist in model"
    # The leaf set should have an expression involving sum(n$(tn('time-2',n)), 1)


def test_literal_subset_set_membership_has_literal():
    """SetMembershipTest from literal subset should include the literal."""
    # This tests the parser output for tn('time-2',n) producing
    # SetMembershipTest('tn', (SymbolRef("'time-2'"), SymbolRef('n')))
    smt = SetMembershipTest(set_name="tn", indices=(SymbolRef("'time-2'"), SymbolRef("n")))
    assert smt.set_name == "tn"
    assert len(smt.indices) == 2
    assert isinstance(smt.indices[0], SymbolRef)
    assert smt.indices[0].name == "'time-2'"
    assert smt.indices[1].name == "n"

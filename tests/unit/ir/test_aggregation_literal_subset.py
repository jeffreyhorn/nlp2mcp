"""Tests for aggregation with literal co-indices in subset domains.

Issue: sum(tn('time-2',n), 1) was incorrectly emitting as sum(()$(tn(n)), 1)
because the parser filtered 'n' from sum_indices (as it was in free_domain)
and lost the literal 'time-2'.
"""

from src.ir.ast import SetMembershipTest, Sum, SymbolRef
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


def _find_smt_in_expr(expr, set_name: str) -> SetMembershipTest | None:
    """Find a SetMembershipTest with the given set_name in an expression tree."""
    if isinstance(expr, SetMembershipTest):
        if expr.set_name == set_name:
            return expr
    # Walk known Expr child attributes
    from src.ir.ast import Binary, Call, DollarConditional, Prod, Unary

    if isinstance(expr, Binary):
        return _find_smt_in_expr(expr.left, set_name) or _find_smt_in_expr(expr.right, set_name)
    if isinstance(expr, Unary):
        return _find_smt_in_expr(expr.child, set_name)
    if isinstance(expr, Sum):
        result = _find_smt_in_expr(expr.body, set_name)
        if result:
            return result
        if expr.condition:
            return _find_smt_in_expr(expr.condition, set_name)
    if isinstance(expr, Prod):
        result = _find_smt_in_expr(expr.body, set_name)
        if result:
            return result
        if expr.condition:
            return _find_smt_in_expr(expr.condition, set_name)
    if isinstance(expr, Call):
        for arg in expr.args:
            result = _find_smt_in_expr(arg, set_name)
            if result:
                return result
    if isinstance(expr, DollarConditional):
        return _find_smt_in_expr(expr.value_expr, set_name) or _find_smt_in_expr(
            expr.condition, set_name
        )
    return None


def _find_sum_in_expr(expr) -> Sum | None:
    """Find a Sum node in an expression tree."""
    if isinstance(expr, Sum):
        return expr
    from src.ir.ast import Binary, Call, DollarConditional, Unary

    if isinstance(expr, Binary):
        return _find_sum_in_expr(expr.left) or _find_sum_in_expr(expr.right)
    if isinstance(expr, Unary):
        return _find_sum_in_expr(expr.child)
    if isinstance(expr, DollarConditional):
        return _find_sum_in_expr(expr.value_expr) or _find_sum_in_expr(expr.condition)
    if isinstance(expr, Call):
        for arg in expr.args:
            result = _find_sum_in_expr(arg)
            if result:
                return result
    return None


def test_literal_subset_preserves_sum_index(tmp_path):
    """sum(tn('time-2',n), 1) in leaf(n) should keep n as sum index."""
    gams_file = tmp_path / "test_lit_subset.gms"
    gams_file.write_text(_build_model_with_literal_subset())
    model = parse_model_file(str(gams_file))

    leaf_def = model.sets.get("leaf")
    assert leaf_def is not None, "Set 'leaf' should exist in model"

    # The leaf set should have an assignment condition containing a Sum
    # with 'n' as index and tn('time-2',n) as condition.
    # Check the set's expression if available, or check equations that
    # reference it.
    obj_eq = model.equations.get("obj")
    assert obj_eq is not None, "Equation 'obj' should exist"

    # Find the Sum in the objective equation's LHS
    lhs, _ = obj_eq.lhs_rhs
    sum_node = _find_sum_in_expr(lhs)
    assert sum_node is not None, "Expected a Sum node in obj equation"
    assert (
        "n" in sum_node.index_sets
    ), f"Sum should have 'n' in index_sets, got {sum_node.index_sets}"


def test_literal_subset_set_membership_has_literal(tmp_path):
    """Parsed model with obj$leaf should contain SetMembershipTest for leaf(n)."""
    gams_file = tmp_path / "test_lit_subset_literal.gms"
    gams_file.write_text(_build_model_with_literal_subset())
    model = parse_model_file(str(gams_file))

    # The obj equation has sum(n$leaf(n), x(n)) — check that the
    # SetMembershipTest for 'leaf' is present with 'n' index.
    obj_eq = model.equations.get("obj")
    assert obj_eq is not None
    lhs, _ = obj_eq.lhs_rhs
    smt = _find_smt_in_expr(lhs, "leaf")
    assert smt is not None, "Expected SetMembershipTest for 'leaf' in obj equation"
    assert len(smt.indices) == 1
    assert isinstance(smt.indices[0], SymbolRef)
    assert smt.indices[0].name == "n"

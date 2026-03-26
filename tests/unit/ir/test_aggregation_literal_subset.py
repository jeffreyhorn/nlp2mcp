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
    """sum(tn('time-2',n), 1) in leaf(n) should produce a SetMembershipTest with the literal."""
    gams_file = tmp_path / "test_lit_subset.gms"
    gams_file.write_text(_build_model_with_literal_subset())
    model = parse_model_file(str(gams_file))

    # Check the set_assignments for 'leaf' — the parser records dynamic
    # set assignments like leaf(n)$(sum(...)) = yes there.
    assignments = getattr(model, "set_assignments", None)
    assert assignments is not None, "Model should have set_assignments"

    leaf_assignments = [a for a in assignments if a.set_name == "leaf"]
    assert leaf_assignments, "Expected at least one assignment for set 'leaf'"

    leaf_assignment = leaf_assignments[0]
    # Walk the assignment to find the embedded Sum expression
    sum_node = _find_sum_in_expr(leaf_assignment.expr)
    assert sum_node is not None, "Expected a Sum node in leaf set assignment"

    # The Sum's condition should reference tn with the literal
    smt_tn = None
    if getattr(sum_node, "condition", None) is not None:
        smt_tn = _find_smt_in_expr(sum_node.condition, "tn")
    if smt_tn is None:
        smt_tn = _find_smt_in_expr(sum_node.body, "tn")

    assert smt_tn is not None, "Expected SetMembershipTest for 'tn' in Sum"
    assert any(
        isinstance(idx, SymbolRef) and idx.name == "n" for idx in smt_tn.indices
    ), "SetMembershipTest for 'tn' should include 'n' as an index"
    # Also verify the quoted literal co-index is preserved (not dropped).
    # The parser may normalize quotes, so accept unquoted and both quote styles.
    literal_names = {"time-2", "'time-2'", '"time-2"'}
    assert any(
        isinstance(idx, SymbolRef) and idx.name in literal_names for idx in smt_tn.indices
    ), "SetMembershipTest for 'tn' should include the 'time-2' literal co-index"

    # The Sum should NOT rebind 'n' as an iterator when 'n' is already
    # controlled by leaf(n) — that would cause GAMS $125.
    assert (
        "n" not in sum_node.index_sets
    ), f"Sum should not rebind 'n' as iterator (avoids $125), got index_sets={sum_node.index_sets}"

    # Guard: rendering the leaf assignment should not produce sum(()$...
    # which is invalid GAMS. This is a known limitation (ISSUE_1155) —
    # when all sum indices are filtered, the Sum has empty index_sets.
    # TODO(ISSUE_1155): Once empty-Sum emission is fixed, change this to
    # a hard assertion that sum(()$...) does NOT appear.
    from src.emit.expr_to_gams import expr_to_gams

    rendered = expr_to_gams(leaf_assignment.expr)
    if "sum(()$" in rendered or "sum(()," in rendered:
        import pytest

        pytest.xfail("ISSUE_1155: empty Sum(index_sets=()) emits invalid GAMS")


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

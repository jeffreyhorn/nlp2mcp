"""Sprint 25 / #1348 #1349: china + pindyck emit regressions.

#1348 (china): Set name `g` (a transitive subset of `ca`) was being
literalised as `'g'` in `gio('g', <elem>) = -1` instead of expanded
over g's members. Root cause: `_handle_assign` in `src/ir/parser.py`
only matched the LHS-index expansion when the index name equalled the
domain name (or was a direct alias). Subset chains like
`g(c) → c(ca)` were rejected. Fix walks the parent chain.

A second related bug surfaced once the gio expansion was correct:
`comp_up_purchase(ca)` emitted `purdata(cp,...)` in its body because
`_substitute_indices` had no `LhsConditionalAssign` case, so the
`cp → ca` rename in `_process_expr_map_bound` couldn't reach the
ParamRef inside the wrapped expression. Fixed in
`src/ad/constraint_jacobian.py`; the partition-side wrapper now folds
subset guards into existing LhsConditionalAssign conditions instead
of double-wrapping.

#1349 (pindyck): The post-`r.fx("1974") = 500` recurrence
`loop(t$to(t), r.l(t) = r.l(t-1) - d.l(t))` failed with $141 because
the `_fx_` equation replacement of `var.fx` lost the `.l` side effect
(GAMS `var.fx(idx) = val` sets both bounds AND `.l`). Fix: when the
`_fx_` equation is paired in the MCP, also emit `var.l(idx) = val`
so subsequent var-init recurrences have a populated initial value.
"""

from __future__ import annotations

import os
import sys

import pytest


@pytest.fixture(autouse=True)
def _high_recursion_limit():
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        yield
    finally:
        sys.setrecursionlimit(old)


def _emit_mcp_for(gms_path: str) -> str:
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_file
    from src.kkt.assemble import assemble_kkt_system

    model = parse_model_file(gms_path)
    normalize_model(model)
    j_eq, j_ineq = compute_constraint_jacobian(model)
    grad = compute_objective_gradient(model)
    kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
    return emit_gams_mcp(kkt)


@pytest.mark.integration
def test_china_does_not_quote_set_name_in_diagonal_assignment():
    """#1348: china's `gio(g,g) = -1` (where gio(ca,g), g(c), c(ca))
    must NOT emit `gio('g', <elem>) = -1`. The first `g` is a transitive
    subset of `ca` and must iterate over g's members. Repeated-symbol
    semantics tie the two `g` positions to the same element, producing
    a diagonal pattern (`gio('barley','barley') = -1`, etc.).
    """
    src = "data/gamslib/raw/china.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/china.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    assert "gio('g'," not in output, (
        "Set name 'g' must not be literalised as 'g' in gio assignments — "
        "it should iterate over g's members (transitive subset of ca)."
    )


@pytest.mark.integration
def test_china_comp_up_purchase_substitutes_subset_index_in_body():
    """#1348 (companion): `purchase.up(cp)$purdata(cp,"quantity") =
    purdata(cp,"quantity")` must rename `cp → ca` inside the wrapped
    LhsConditionalAssign so the emitted `comp_up_purchase(ca)` body uses
    `purdata(ca, "quantity")`, not `purdata(cp, "quantity")` (which
    would trip GAMS $149 "Uncontrolled set entered as constant").
    """
    src = "data/gamslib/raw/china.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/china.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    assert "comp_up_purchase(ca)" in output, "comp_up_purchase equation expected"
    # Locate the comp_up_purchase block and ensure no bare `cp` index reference
    # leaks into the body. The condition may reference `cp(ca)` (set membership
    # test) — that's correct. What we forbid is `purdata(cp,...)`.
    for line in output.splitlines():
        if line.startswith("comp_up_purchase("):
            assert (
                "purdata(cp," not in line
            ), f"comp_up_purchase body must use ca, not cp, in purdata(): {line}"
            break


@pytest.mark.integration
def test_pindyck_emits_l_init_for_fx_equation_diagonal():
    """#1349: pindyck's `r.fx("1974") = 500` is replaced by an `_fx_`
    complementarity equation, but the `.l` side effect of the original
    `.fx` (GAMS sets `r.l('1974') = 500` as well) must be preserved.
    Subsequent `loop(t$to(t), r.l(t) = r.l(t-1) - d.l(t))` reads
    `r.l('1974')` and would fail with $141 "Symbol declared but no
    values have been assigned" without the explicit `.l` init.
    """
    src = "data/gamslib/raw/pindyck.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/pindyck.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    # The four .fx-replaced variables in pindyck (td, s, cs, r) all need
    # explicit `.l('1974') = <value>` for the recurrence loop to succeed.
    for var, val in [("td", "18"), ("s", "6.5"), ("cs", "0"), ("r", "500")]:
        assert f"{var}.l('1974') = {val};" in output, (
            f"Expected `{var}.l('1974') = {val};` to preserve .fx side effect "
            f"after the fx replacement equation is paired in MCP."
        )

    # The recurrence loop must still be emitted and reference r.l(t-1).
    assert (
        "r.l(t) = r.l(t-1) - d.l(t)" in output
    ), "post-fx loop-based var-init must still be emitted"

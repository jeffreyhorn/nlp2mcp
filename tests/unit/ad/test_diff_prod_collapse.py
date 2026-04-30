"""Sprint 25 / #1330: `_diff_prod` collapses logarithmic-derivative sum
when wrt indices name-match the prod's bound indices.

Mathematical identity (for Cobb-Douglas / power products):

    d(prod_i f(i)) / d(x(j))  =  prod * δ(i, j) * f'(i) / f(i)
                              =  prod * f'(j) / f(j)        (single term)

The naive logarithmic-derivative form `prod * sum_i (df(i)/dx / f(i))`
iterates over ALL bound i and treats each as if it matched the wrt —
which is correct only when all `f(i)` are equal (e.g., a symmetric
optimum), and WRONG for asymmetric data.

Encountered in camcge (#1330): `omega = prod(i, cd(i)^cles(i))`. With
asymmetric `cles(i)` per sector, the naive sum gave `omega * sum(i,
cles(i)/cd(i))` (the same value for all stationarity rows), making the
KKT system structurally inconsistent even at the NLP optimum.

Fix: when `wrt_indices` (or post-collapse `effective_wrt`) has names
matching the prod's bound names, return `prod * (body_deriv / body)`
directly — no Sum wrapper.
"""

from __future__ import annotations

import pytest

from src.ad.derivative_rules import _diff_prod, differentiate_expr
from src.ir.ast import (
    Binary,
    DollarConditional,
    ParamRef,
    Prod,
    Sum,
    VarRef,
)


@pytest.mark.unit
def test_prod_with_symbolic_wrt_collapses_to_single_term():
    """`prod(i, cd(i)^cles(i))` differentiated w.r.t. cd(i) (symbolic)
    should yield `prod * (body_deriv / body)` — NOT a sum.
    """
    body = Binary("**", VarRef("cd", ("i",)), ParamRef("cles", ("i",)))
    expr = Prod(("i",), body, None)

    result = _diff_prod(expr, "cd", ("i",))

    # Result shape: Binary("*", expr, log_term)
    assert isinstance(result, Binary) and result.op == "*"
    # left should be the original prod (unchanged)
    assert result.left is expr
    # right should be (body_deriv / body) — NOT a Sum
    assert not isinstance(result.right, Sum), (
        "Expected collapsed form (no Sum); got Sum-wrapped result. " f"Got: {result.right!r}"
    )


@pytest.mark.unit
def test_prod_with_condition_inherits_dollar_filter():
    """`prod(i$cles(i), cd(i)^cles(i))` differentiated w.r.t. cd(i)
    should yield `prod * (body_deriv / body)$cles(i)` — the prod's
    `$-condition` carries through to the collapsed term.
    """
    body = Binary("**", VarRef("cd", ("i",)), ParamRef("cles", ("i",)))
    cond = ParamRef("cles", ("i",))
    expr = Prod(("i",), body, cond)

    result = _diff_prod(expr, "cd", ("i",))

    # Right side should be a DollarConditional wrapping the log term.
    assert isinstance(result.right, DollarConditional), (
        "Expected DollarConditional wrap inheriting prod's condition. " f"Got: {result.right!r}"
    )
    assert result.right.condition is cond


@pytest.mark.unit
def test_prod_concrete_wrt_with_set_membership_also_collapses():
    """`prod(i, cd(i)^cles(i))` differentiated w.r.t. cd("ag-subsist")
    (concrete) should ALSO collapse via `_sum_should_collapse`'s
    symbolic-substitution. The post-collapse `effective_wrt` becomes
    `("i",)` (symbolic), then the new collapse logic fires.
    """
    from src.config import Config
    from src.ir.model_ir import ModelIR
    from src.ir.symbols import SetDef

    body = Binary("**", VarRef("cd", ("i",)), ParamRef("cles", ("i",)))
    expr = Prod(("i",), body, None)

    # Build a config with model_ir so concrete index lookup can resolve.
    model = ModelIR()
    model.sets["i"] = SetDef(name="i", members=["ag-subsist", "ag-exp+ind"])
    cfg = Config(model_ir=model)

    result = _diff_prod(expr, "cd", ("ag-subsist",), cfg)

    # Same collapsed form as the symbolic case.
    assert isinstance(result, Binary) and result.op == "*"
    assert not isinstance(result.right, Sum), (
        "Expected collapsed form for concrete wrt too; got Sum. " f"Got: {result.right!r}"
    )


@pytest.mark.unit
def test_full_objective_gradient_for_camcge_pattern():
    """End-to-end: differentiate `omega = prod(i, cd(i)^cles(i))`
    w.r.t. cd via `differentiate_expr` (the public API) and check
    the result is the collapsed form.
    """
    body = Binary("**", VarRef("cd", ("i",)), ParamRef("cles", ("i",)))
    expr = Prod(("i",), body, None)

    result = differentiate_expr(expr, "cd", ("i",))

    # Should be a Binary("*", prod, log_term) where log_term is NOT a Sum.
    assert isinstance(result, Binary) and result.op == "*"
    assert not isinstance(result.right, Sum), (
        "Public API should also produce the collapsed form. " f"Got: {result!r}"
    )

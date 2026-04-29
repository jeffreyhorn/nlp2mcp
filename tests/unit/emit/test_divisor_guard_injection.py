"""Sprint 25 / #1320: parameter-divisor $-condition guard injection.

When original-source equations contain `1/p(i)` or `log(p(i))` with `p`
an indexed parameter that may be zero in some indices, GAMS aborts at
model-listing time with EXECERROR (e.g., gtm's `bdef` body has
`log((supc(i) - s(i))/supc(i))` with `supc(mexico) = 0` from empty
source data).

The fix injects `$(p(i) <> 0)` on the smallest enclosing `Sum`/`Prod`
whose body contains the offending divisor `ParamRef`. These tests
validate the helper's AST-level rewrite logic; the gtm corpus
regression lives in `tests/integration/emit/test_gtm_bdef_guard.py`.
"""

from __future__ import annotations

import pytest

from src.emit.equations import _collect_divisor_param_refs, _inject_divisor_guards
from src.ir.ast import Binary, Call, Const, ParamRef, Sum, VarRef


@pytest.mark.unit
def test_indexed_divisor_inside_sum_gets_guarded():
    """`Sum((i), 1/p(i))` → `Sum((i)$(p(i) <> 0), 1/p(i))`."""
    p_ref = ParamRef("p", ("i",))
    body = Binary("/", Const(1.0), p_ref)
    sum_expr = Sum(("i",), body, None)

    rewritten = _inject_divisor_guards(sum_expr)

    assert isinstance(rewritten, Sum)
    assert rewritten.condition is not None, "Expected Sum to gain a condition."
    # The condition should be `p(i) <> 0`.
    cond = rewritten.condition
    assert isinstance(cond, Binary), f"Expected Binary condition, got {type(cond).__name__}"
    assert cond.op == "<>"
    assert isinstance(cond.left, ParamRef) and cond.left.name == "p"
    assert isinstance(cond.right, Const) and cond.right.value == 0.0


@pytest.mark.unit
def test_log_argument_param_gets_guarded():
    """`Sum((i), log(p(i)))` → `Sum((i)$(p(i) <> 0), log(p(i)))`."""
    p_ref = ParamRef("p", ("i",))
    body = Call("log", (p_ref,))
    sum_expr = Sum(("i",), body, None)

    rewritten = _inject_divisor_guards(sum_expr)

    assert isinstance(rewritten, Sum)
    assert rewritten.condition is not None
    cond = rewritten.condition
    assert isinstance(cond, Binary) and cond.op == "<>"
    assert isinstance(cond.left, ParamRef) and cond.left.name == "p"


@pytest.mark.unit
def test_param_in_numerator_not_guarded():
    """`Sum((i), p(i) * x(i))` should NOT gain a divisor guard — the
    parameter is in numerator/multiplicative position.
    """
    p_ref = ParamRef("p", ("i",))
    x_ref = VarRef("x", ("i",))
    body = Binary("*", p_ref, x_ref)
    sum_expr = Sum(("i",), body, None)

    rewritten = _inject_divisor_guards(sum_expr)

    # No condition added, body unchanged.
    assert rewritten is sum_expr or rewritten.condition is None, (
        f"Expected no divisor guard for numerator-only ParamRef; got "
        f"condition={rewritten.condition!r}"
    )


@pytest.mark.unit
def test_multiple_offending_params_in_one_sum():
    """`Sum((i), 1/(a(i) * b(i)))` → guard with both `a(i) <> 0` AND
    `b(i) <> 0`.
    """
    a_ref = ParamRef("a", ("i",))
    b_ref = ParamRef("b", ("i",))
    denom = Binary("*", a_ref, b_ref)
    body = Binary("/", Const(1.0), denom)
    sum_expr = Sum(("i",), body, None)

    rewritten = _inject_divisor_guards(sum_expr)

    assert isinstance(rewritten, Sum)
    assert rewritten.condition is not None

    # Walk the condition tree and collect the ParamRef names that appear
    # in `<>` clauses.
    guarded_names: set[str] = set()

    def _walk(e):
        if isinstance(e, Binary):
            if e.op == "<>" and isinstance(e.left, ParamRef):
                guarded_names.add(e.left.name)
            elif e.op == "and":
                _walk(e.left)
                _walk(e.right)

    _walk(rewritten.condition)
    assert guarded_names == {"a", "b"}, f"Expected guards on both `a` and `b`, got: {guarded_names}"


@pytest.mark.unit
def test_existing_sum_condition_preserved_and_extended():
    """`Sum((i)$cond, 1/p(i))` → `Sum((i)$(cond and p(i) <> 0), 1/p(i))`."""
    p_ref = ParamRef("p", ("i",))
    body = Binary("/", Const(1.0), p_ref)
    existing_cond = Binary(">", VarRef("x", ("i",)), Const(0.0))
    sum_expr = Sum(("i",), body, existing_cond)

    rewritten = _inject_divisor_guards(sum_expr)

    assert isinstance(rewritten, Sum)
    assert rewritten.condition is not None

    # The new condition should be a Binary("and", ..., ...) combining
    # the old condition with the new guard.
    new_cond = rewritten.condition
    assert isinstance(new_cond, Binary) and new_cond.op == "and", (
        f"Expected Binary('and', ...) condition; got {new_cond!r}"
    )

    # One side should be the original cond (or contain it).
    sides_repr = (repr(new_cond.left), repr(new_cond.right))
    assert any("VarRef(x" in s for s in sides_repr), (
        f"Expected original cond (x > 0) preserved in one side; got {new_cond!r}"
    )
    # The other side should contain the new guard p <> 0.
    assert any("ParamRef(p" in s and "<>" in s for s in sides_repr), (
        f"Expected new guard `p <> 0` preserved in one side; got {new_cond!r}"
    )


@pytest.mark.unit
def test_collect_divisor_param_refs_basic():
    """Verify `_collect_divisor_param_refs` finds divisor-position
    ParamRefs and ignores numerator-position ones.
    """
    a_ref = ParamRef("a", ("i",))
    b_ref = ParamRef("b", ("i",))
    # a in numerator, b in denominator
    expr = Binary("/", a_ref, b_ref)

    found = _collect_divisor_param_refs(expr)
    found_names = {p.name for p in found}
    assert found_names == {"b"}, f"Expected only `b` (denominator) collected; got {found_names}"


@pytest.mark.unit
def test_scalar_param_in_divisor_not_guarded():
    """A scalar `ParamRef` (no indices) in divisor position should NOT
    be collected — its zero-ness is a static fact, not a per-iteration
    concern. The guard would be a global no-op.
    """
    p_scalar = ParamRef("p", ())  # Scalar — no indices.
    body = Binary("/", Const(1.0), p_scalar)
    sum_expr = Sum(("i",), body, None)

    rewritten = _inject_divisor_guards(sum_expr)

    # No condition added.
    assert rewritten is sum_expr or rewritten.condition is None, (
        f"Expected no guard for scalar ParamRef in divisor; got condition={rewritten.condition!r}"
    )


@pytest.mark.unit
def test_param_independent_of_sum_index_not_guarded():
    """A `ParamRef(p(j))` inside `Sum((i), 1/p(j))` should NOT be
    guarded — `p(j)` doesn't co-iterate with `i`, so its zero-ness
    isn't a per-i concern (the user can pre-guard or fix the param
    separately).
    """
    p_ref = ParamRef("p", ("j",))  # Indexed by j, not i.
    body = Binary("/", Const(1.0), p_ref)
    sum_expr = Sum(("i",), body, None)

    rewritten = _inject_divisor_guards(sum_expr)

    # No guard for an outer-scope param.
    assert rewritten is sum_expr or rewritten.condition is None, (
        f"Expected no guard for `p(j)` not co-iterating with sum index `i`; "
        f"got condition={rewritten.condition!r}"
    )

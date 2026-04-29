"""Sprint 25 / #1243: walker that collects VarRef nodes in divisor positions.

The MCP variable-init pass uses this walker to find FREE variables that
appear in `1/var` or `log(var)` patterns inside stationarity equation
bodies. Such variables would default to `.l = 0` and trigger
EXECERROR=1 from div-by-zero at GAMS model-listing time, so the
emitter auto-inits them to `1`.

These tests validate the walker's recursion and divisor-position
detection. The emitter wiring is tested separately in
`tests/unit/emit/test_var_in_denominator_init.py`.
"""

from __future__ import annotations

import pytest

from src.emit.equations import _collect_divisor_var_refs
from src.ir.ast import Binary, Call, Const, ParamRef, Sum, VarRef


@pytest.mark.unit
def test_simple_one_over_var_returns_var():
    """`Binary("/", Const(1), VarRef("y", ("p",)))` → returns `{y(p)}`."""
    y_ref = VarRef("y", ("p",))
    expr = Binary("/", Const(1.0), y_ref)

    found = _collect_divisor_var_refs(expr)

    assert found == {y_ref}


@pytest.mark.unit
def test_var_in_numerator_not_returned():
    """`Binary("/", VarRef("y", ()), Const(2))` → returns `{}` — y is
    in numerator position, not divisor.
    """
    expr = Binary("/", VarRef("y", ()), Const(2.0))

    found = _collect_divisor_var_refs(expr)

    assert found == set()


@pytest.mark.unit
def test_var_inside_denominator_arithmetic_returned():
    """`Binary("/", _, Binary("+", VarRef("y", ("p",)), Const(1)))` —
    the VarRef is transitively in divisor position.
    """
    y_ref = VarRef("y", ("p",))
    denom = Binary("+", y_ref, Const(1.0))
    expr = Binary("/", Const(1.0), denom)

    found = _collect_divisor_var_refs(expr)

    assert found == {y_ref}


@pytest.mark.unit
def test_log_argument_var_returned():
    """`Call("log", [VarRef("y", ("p",))])` → returns `{y(p)}`. log(0)
    is a domain error in GAMS just as 1/0 is, so we treat log args
    as divisor-like.
    """
    y_ref = VarRef("y", ("p",))
    expr = Call("log", (y_ref,))

    found = _collect_divisor_var_refs(expr)

    assert found == {y_ref}


@pytest.mark.unit
def test_walker_recurses_into_sum_body():
    """`Sum(("p",), Binary("/", _, VarRef("y", ("p",))))` → returns
    `{y(p)}`. The Sum boundary resets the divisor flag to False, but
    the inner Binary("/") sets it back to True for its right child.
    """
    y_ref = VarRef("y", ("p",))
    inner_div = Binary("/", Const(1.0), y_ref)
    sum_expr = Sum(("p",), inner_div, None)

    found = _collect_divisor_var_refs(sum_expr)

    assert found == {y_ref}


@pytest.mark.unit
def test_param_in_denominator_not_returned():
    """The walker only collects VarRefs — ParamRefs in divisor position
    are out of scope (handled by `_collect_divisor_param_refs` for #1320).
    """
    p_ref = ParamRef("p", ("i",))
    expr = Binary("/", Const(1.0), p_ref)

    found = _collect_divisor_var_refs(expr)

    assert found == set()


@pytest.mark.unit
def test_scalar_var_in_denominator_returned():
    """A scalar VarRef (no indices) in denominator is returned. A scalar
    FREE var with default `.l = 0` is just as broken as an indexed one.
    """
    y_ref = VarRef("y", ())
    expr = Binary("/", Const(1.0), y_ref)

    found = _collect_divisor_var_refs(expr)

    assert found == {y_ref}


@pytest.mark.unit
def test_prod_objective_logarithmic_derivative_pattern():
    """The pattern `prod(p, y(p)) * sum(p, 1/y(p))` from `_diff_prod`
    should yield `{y(p)}` because the inner `1/y(p)` is in divisor
    position. The outer `*` is irrelevant.
    """
    from src.ir.ast import Prod

    y_ref_outer = VarRef("y", ("p",))
    y_ref_inner = VarRef("y", ("p",))
    outer_prod = Prod(("p",), y_ref_outer, None)
    inner_div = Binary("/", Const(1.0), y_ref_inner)
    inner_sum = Sum(("p",), inner_div, None)
    full = Binary("*", outer_prod, inner_sum)

    found = _collect_divisor_var_refs(full)

    # The `y_ref_outer` is the body of `Prod` (not in a divisor); the
    # `y_ref_inner` is in the divisor of the `1/y` Binary.
    # Both share the same name+indices but they are equal as VarRef
    # dataclasses, so the set deduplicates them to size 1.
    assert {(v.name, v.indices) for v in found} == {("y", ("p",))}

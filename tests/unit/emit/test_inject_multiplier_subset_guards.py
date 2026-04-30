"""Sprint 25 / #1245: walker that wraps multiplier-bearing terms with
the source equation's subset filter.

When an NLP equation is declared over a parent set but defined over a
dynamic / static subset (e.g., camcge's `esupply(it)..` where `it` ⊂
`i`), the corresponding multiplier `nu_esupply` is parent-widened to
`(i,)` by #1327's fix. The stationarity equation body, however, still
emits the multiplier's coefficient expression unguarded — for indices
outside the subset, that coefficient may evaluate to UNDF (e.g.,
`1/gamma(in)` with `gamma(in) = 0`). GAMS aborts with EXECERROR=4
even though `nu_esupply.fx(i)$(not it(i)) = 0` (so the term itself is
zero).

The walker wraps each multiplier-bearing term with `$(subset(d))` so
GAMS skips evaluating the coefficient expression entirely outside
the subset. Mathematically a no-op; structurally avoids the abort.
"""

from __future__ import annotations

import pytest

from src.emit.equations import (
    _build_subset_guard_for_term,
    _collect_multiplier_refs_in_term,
    _inject_multiplier_subset_guards,
)
from src.ir.ast import (
    Binary,
    DollarConditional,
    MultiplierRef,
    SetMembershipTest,
    Sum,
    SymbolRef,
    VarRef,
)
from src.ir.model_ir import ModelIR
from src.kkt.kkt_system import KKTSystem


def _make_kkt_with_widening(
    mult_name: str, orig_dom: tuple[str, ...], widened_dom: tuple[str, ...]
) -> KKTSystem:
    """Build a minimal KKTSystem stub with one multiplier widening."""
    from src.ad.jacobian import GradientVector, JacobianStructure

    ir = ModelIR()
    grad = GradientVector()
    j_eq = JacobianStructure()
    j_ineq = JacobianStructure()
    kkt = KKTSystem(model_ir=ir, gradient=grad, J_eq=j_eq, J_ineq=j_ineq)
    kkt.multiplier_domain_widenings[mult_name] = (orig_dom, widened_dom)
    return kkt


@pytest.mark.unit
def test_widened_multiplier_term_gets_wrapped():
    """`Binary("*", expr, MultiplierRef("nu_X", ("i",)))` with
    `multiplier_domain_widenings: {"nu_X": (("it",), ("i",))}` should
    produce `DollarConditional(expr * nu_X(i), it(i))`.
    """
    kkt = _make_kkt_with_widening("nu_X", ("it",), ("i",))
    term = Binary("*", VarRef("foo", ("i",)), MultiplierRef("nu_X", ("i",)))

    rewritten = _inject_multiplier_subset_guards(term, kkt)

    assert isinstance(rewritten, DollarConditional)
    assert rewritten.value_expr is term
    assert isinstance(rewritten.condition, SetMembershipTest)
    assert rewritten.condition.set_name == "it"
    assert len(rewritten.condition.indices) == 1
    assert isinstance(rewritten.condition.indices[0], SymbolRef)
    assert rewritten.condition.indices[0].name == "i"


@pytest.mark.unit
def test_non_widened_multiplier_left_untouched():
    """A multiplier with no widening entry should not be wrapped."""
    kkt = _make_kkt_with_widening("nu_X", ("it",), ("i",))
    # nu_other has no widening
    term = Binary("*", VarRef("foo", ("i",)), MultiplierRef("nu_other", ("i",)))

    rewritten = _inject_multiplier_subset_guards(term, kkt)

    assert rewritten is term, "Term without widened multiplier should be unchanged"


@pytest.mark.unit
def test_widening_with_matching_domain_no_op():
    """A multiplier whose `orig_dom == widened_dom` is not a real
    parent/subset split — no guard should be injected.
    """
    kkt = _make_kkt_with_widening("nu_X", ("i",), ("i",))
    term = Binary("*", VarRef("foo", ("i",)), MultiplierRef("nu_X", ("i",)))

    rewritten = _inject_multiplier_subset_guards(term, kkt)

    assert rewritten is term


@pytest.mark.unit
def test_additive_terms_are_each_processed():
    """`(a * nu_X(i)) + (b * nu_Y(i))` with both nu_X and nu_Y widened
    should yield two independently wrapped terms.
    """
    kkt = _make_kkt_with_widening("nu_X", ("it",), ("i",))
    kkt.multiplier_domain_widenings["nu_Y"] = (("im",), ("i",))
    a_term = Binary("*", VarRef("a", ("i",)), MultiplierRef("nu_X", ("i",)))
    b_term = Binary("*", VarRef("b", ("i",)), MultiplierRef("nu_Y", ("i",)))
    body = Binary("+", a_term, b_term)

    rewritten = _inject_multiplier_subset_guards(body, kkt)

    assert isinstance(rewritten, Binary) and rewritten.op == "+"
    assert isinstance(rewritten.left, DollarConditional)
    assert isinstance(rewritten.right, DollarConditional)
    # First term wrapped with it(i)
    cond_a = rewritten.left.condition
    assert isinstance(cond_a, SetMembershipTest) and cond_a.set_name == "it"
    # Second term wrapped with im(i)
    cond_b = rewritten.right.condition
    assert isinstance(cond_b, SetMembershipTest) and cond_b.set_name == "im"


@pytest.mark.unit
def test_multiplier_inside_sum_body_wraps_inside_sum():
    """`Sum(("j",), expr * nu_X(j))` with nu_X widened from (jt,) to
    (j,) should wrap the BODY of the Sum, not the entire Sum.
    """
    kkt = _make_kkt_with_widening("nu_X", ("jt",), ("j",))
    body = Binary("*", VarRef("foo", ("j",)), MultiplierRef("nu_X", ("j",)))
    sum_expr = Sum(("j",), body, None)

    rewritten = _inject_multiplier_subset_guards(sum_expr, kkt)

    assert isinstance(rewritten, Sum)
    assert rewritten.index_sets == ("j",)
    # The body should now be a DollarConditional wrap.
    assert isinstance(rewritten.body, DollarConditional)
    cond = rewritten.body.condition
    assert isinstance(cond, SetMembershipTest) and cond.set_name == "jt"


@pytest.mark.unit
def test_collect_multiplier_refs_does_not_cross_sum_boundary():
    """`_collect_multiplier_refs_in_term` must NOT descend into Sum
    bodies — those are recursed separately by the outer walker.
    """
    inner_mult = MultiplierRef("nu_inner", ("j",))
    outer_mult = MultiplierRef("nu_outer", ("i",))
    sum_term = Sum(("j",), Binary("*", VarRef("x"), inner_mult), None)
    # Binary chain at the term level: outer_mult * Sum(... inner_mult ...)
    expr = Binary("*", outer_mult, sum_term)

    refs = _collect_multiplier_refs_in_term(expr)

    names = {r.name for r in refs}
    assert "nu_outer" in names
    assert "nu_inner" not in names, (
        "Should NOT collect multipliers inside Sum bodies — those are "
        "scoped to the inner aggregator's body."
    )


@pytest.mark.unit
def test_build_subset_guard_for_term_handles_no_multipliers():
    """A term with NO MultiplierRefs returns `None`."""
    kkt = _make_kkt_with_widening("nu_X", ("it",), ("i",))
    term = Binary("*", VarRef("a", ("i",)), VarRef("b", ("i",)))

    guard = _build_subset_guard_for_term(term, kkt)

    assert guard is None

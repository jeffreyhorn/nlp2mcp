"""Sprint 38 Day 12 / #983 + #1325: the partial-collapse condition must be
substituted the same way the body is.

`_diff_sum`'s partial-collapse path renames the *remaining* sum indices in the
condition (`j` -> `j__`, per #1111's alias disambiguation) but used to leave the
*matched* positions carrying the original sum-index name.  The enclosing `Sum`
binds only the remaining indices, so the matched name became a **free symbol
with no binder**.

elec: `sum(ut(i,j), 1/d(i,j))` differentiated w.r.t. `x("i1")` produced

    sum(j__$(ut(i,j__)), ...)      <- `i` free
  + sum(i__$(ut(i__,j)), ...)      <- `j` free

Downstream those became `ut(i,i)` (the diagonal of a strictly upper-triangular
set — always false, silently dropping half the gradient) and `ut(i,j)` (which
fails to constrain `i__`, admitting `i__ = i` and driving `d = 0` into a
divisor: `**** Exec Error ... division by zero`).
"""

from __future__ import annotations

import pytest

from src.config import Config
from src.ir.ast import Binary, Call, Const, SetMembershipTest, Sum, SymbolRef, VarRef
from src.ir.model_ir import ModelIR
from src.ir.symbols import AliasDef, SetDef, VariableDef


def _elec_like_model() -> ModelIR:
    """`Set i /i1../; Alias(i,j); Set ut(i,i);` — elec's declaration shape."""
    m = ModelIR()
    m.add_set(SetDef(name="i", members=["i1", "i2", "i3"]))
    m.add_alias(AliasDef(name="j", target="i"))
    m.add_set(SetDef(name="ut", members=[], domain=("i", "i")))
    m.add_var(VariableDef(name="x", domain=("i",)))
    return m


def _collect_sums(expr, out=None):
    out = [] if out is None else out
    if isinstance(expr, Sum):
        out.append(expr)
        _collect_sums(expr.body, out)
        if expr.condition is not None:
            _collect_sums(expr.condition, out)
    elif isinstance(expr, Binary):
        _collect_sums(expr.left, out)
        _collect_sums(expr.right, out)
    elif isinstance(expr, Call):
        for a in expr.args:
            _collect_sums(a, out)
    return out


def _free_names_in_condition(sum_node: Sum) -> set[str]:
    """Names a condition references that the Sum does NOT bind."""
    bound = {s.lower() for s in sum_node.index_sets}
    names: set[str] = set()

    def walk(e):
        if isinstance(e, SetMembershipTest):
            for ix in e.indices:
                if isinstance(ix, SymbolRef):
                    names.add(ix.name)
        elif isinstance(e, Binary):
            walk(e.left)
            walk(e.right)

    if sum_node.condition is not None:
        walk(sum_node.condition)
    # A quoted literal ("i1") is a concrete element, not a free symbol.
    return {n for n in names if n.lower() not in bound and not n.strip("'\"").startswith("i1")}


@pytest.mark.unit
def test_condition_has_no_unbound_symbol_after_partial_collapse():
    """Every Sum's condition may only name indices that Sum binds, or concrete
    elements.  An unbound name means the guard is evaluated against whatever
    happens to be in scope downstream — which is how `ut(i,i)` arose."""
    from src.ad.derivative_rules import differentiate_expr

    m = _elec_like_model()
    # sum((i,j)$ut(i,j), sqr(x(i) - x(j)))
    body = Call("sqr", (Binary("-", VarRef("x", ("i",)), VarRef("x", ("j",))),))
    obj = Sum(("i", "j"), body, SetMembershipTest("ut", (SymbolRef("i"), SymbolRef("j"))))

    from src.config import ensure_config_with_model_ir

    cfg = ensure_config_with_model_ir(Config(), m)
    deriv = differentiate_expr(obj, "x", ("i1",), cfg)

    sums = [s for s in _collect_sums(deriv) if s.condition is not None]
    assert sums, "expected at least one conditioned Sum in the derivative"
    for s in sums:
        free = _free_names_in_condition(s)
        assert not free, (
            f"Sum over {s.index_sets} has condition naming unbound symbol(s) {sorted(free)}. "
            "The matched positions must be substituted to the concrete wrt index, "
            "exactly as the body was."
        )


@pytest.mark.unit
def test_each_condition_names_its_own_summation_index():
    """The invariant from #1325's gate: a guard must constrain the index its
    own Sum iterates, otherwise the excluded pairs are never excluded."""
    from src.ad.derivative_rules import differentiate_expr
    from src.config import ensure_config_with_model_ir

    m = _elec_like_model()
    body = Call("sqr", (Binary("-", VarRef("x", ("i",)), VarRef("x", ("j",))),))
    obj = Sum(("i", "j"), body, SetMembershipTest("ut", (SymbolRef("i"), SymbolRef("j"))))

    cfg = ensure_config_with_model_ir(Config(), m)
    deriv = differentiate_expr(obj, "x", ("i1",), cfg)

    for s in _collect_sums(deriv):
        if s.condition is None or not isinstance(s.condition, SetMembershipTest):
            continue
        named = {ix.name.lower() for ix in s.condition.indices if isinstance(ix, SymbolRef)}
        bound = {b.lower() for b in s.index_sets}
        assert bound & named, (
            f"condition {s.condition.set_name}{tuple(sorted(named))} does not name "
            f"any index of its own Sum over {s.index_sets} — it cannot restrict it"
        )


@pytest.mark.unit
def test_unconditioned_sum_is_unaffected():
    """No condition -> the partial-collapse path must behave exactly as before."""
    from src.ad.derivative_rules import differentiate_expr
    from src.config import ensure_config_with_model_ir

    m = _elec_like_model()
    body = Call("sqr", (Binary("-", VarRef("x", ("i",)), VarRef("x", ("j",))),))
    obj = Sum(("i", "j"), body, None)

    cfg = ensure_config_with_model_ir(Config(), m)
    deriv = differentiate_expr(obj, "x", ("i1",), cfg)

    assert not isinstance(deriv, Const) or deriv.value != 0.0
    for s in _collect_sums(deriv):
        assert s.condition is None

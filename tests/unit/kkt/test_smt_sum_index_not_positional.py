"""Sprint 38 Day 12 / #983 + #1325: a self-mapped sum index is not an element.

`_replace_indices_in_expr`'s `Sum` branch overlays `{idx: idx}` self-mappings on
`element_to_set` so AD-generated names like `j__` survive re-symbolization.  But
that ALSO puts them *in* `element_to_set`, and the `SetMembershipTest` branch
keyed on exactly that membership to decide "this is a concrete element, resolve
it positionally against the set's declared domain".

For elec's `Set ut(i,i)` the declared domain is `i` at BOTH positions, so
`ut(i,j__)` collapsed to `ut(i,i)` — the diagonal of a strictly upper-triangular
set, identically false.

A self-mapping means "bound index, leave it alone", never "element".
"""

from __future__ import annotations

import pytest

from src.ir.ast import SetMembershipTest, Sum, SymbolRef, VarRef
from src.ir.model_ir import ModelIR
from src.ir.symbols import AliasDef, SetDef
from src.kkt.stationarity import _replace_indices_in_expr


def _model() -> ModelIR:
    m = ModelIR()
    m.add_set(SetDef(name="i", members=["i1", "i2", "i3"]))
    m.add_alias(AliasDef(name="j", target="i"))
    m.add_set(SetDef(name="ut", members=[], domain=("i", "i")))
    return m


@pytest.mark.unit
def test_sum_index_survives_against_a_repeated_declared_domain():
    """`sum(j__$(ut("i1", j__)))` -> `sum(j__$(ut(i, j__)))`, NOT `ut(i,i)`."""
    m = _model()
    node = Sum(
        ("j__",),
        VarRef("x", ("j__",)),
        SetMembershipTest("ut", (SymbolRef("i1"), SymbolRef("j__"))),
    )

    out = _replace_indices_in_expr(node, ("i",), {"i1": "i"}, m, ("i",))

    assert isinstance(out, Sum)
    cond = out.condition
    assert isinstance(cond, SetMembershipTest)
    assert [ix.name for ix in cond.indices] == ["i", "j__"], (
        "the bound sum index j__ must be preserved; resolving it positionally "
        "against ut's declared domain (i,i) yields the always-false ut(i,i)"
    )


@pytest.mark.unit
def test_second_position_element_still_resolves_positionally():
    """The #1086 behaviour this guard must NOT break: a genuine concrete
    element in a later position still resolves against the declared domain."""
    m = ModelIR()
    m.add_set(SetDef(name="n", members=["n1", "n2"]))
    m.add_set(SetDef(name="np", members=["n1", "n2"]))
    m.add_set(SetDef(name="arc", members=[], domain=("n", "np")))

    node = SetMembershipTest("arc", (SymbolRef("n1"), SymbolRef("n2")))
    # Empty equation domain, so #1086's equation-domain shortcut cannot fire and
    # BOTH positions go through the positional resolution this guard sits on.
    out = _replace_indices_in_expr(node, ("n",), {"n1": "n", "n2": "n"}, m, ())

    assert isinstance(out, SetMembershipTest)
    assert [ix.name for ix in out.indices] == ["n", "np"], (
        "concrete elements must still resolve against arc's declared domain "
        "(n,np) — the new guard only exempts self-mapped (bound) sum indices"
    )

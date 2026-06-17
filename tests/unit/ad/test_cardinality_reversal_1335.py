"""Unit tests for #1335 time-reversal offset resolution in `_diff_sum`.

`_try_resolve_cardinality_reversal` must recognize the exact idiom
`t + (card(t) - ord(t))` (which lands on the last element of `t` for every
iterate) and resolve it to that element — and reject everything else, so the
sum-preserving `_diff_sum` branch stays tightly gated.
"""

from __future__ import annotations

import pytest

from src.ad.derivative_rules import _try_resolve_cardinality_reversal
from src.ir.ast import Binary, Call, Const, IndexOffset, SymbolRef
from src.ir.model_ir import ModelIR
from src.ir.symbols import SetDef

pytestmark = pytest.mark.unit


def _model() -> ModelIR:
    m = ModelIR()
    m.sets["tt"] = SetDef(name="tt", domain=(), members=["1974", "1975", "1976", "1990"])
    # t is a subset of tt with explicit members
    m.sets["t"] = SetDef(name="t", domain=("tt",), members=["1974", "1975", "1976", "1990"])
    return m


def _card_minus_ord(card_arg: str, ord_arg: str) -> Binary:
    return Binary(
        "-",
        Call("card", (SymbolRef(card_arg),)),
        Call("ord", (SymbolRef(ord_arg),)),
    )


def test_resolves_to_last_element():
    m = _model()
    idx = IndexOffset("t", _card_minus_ord("t", "t"), False)
    assert _try_resolve_cardinality_reversal(idx, "t", m) == "1990"


def test_rejects_when_base_differs_from_sum_index():
    m = _model()
    idx = IndexOffset("t", _card_minus_ord("t", "t"), False)
    # sum index is something else → not the iterator being reversed
    assert _try_resolve_cardinality_reversal(idx, "n", m) is None


def test_rejects_plain_constant_offset():
    m = _model()
    idx = IndexOffset("t", Const(1.0), False)  # t+1, a normal lead — must not fire
    assert _try_resolve_cardinality_reversal(idx, "t", m) is None


def test_rejects_ord_of_other_index():
    m = _model()
    # card(t) - ord(n): does not cancel against base t → not constant
    idx = IndexOffset("t", _card_minus_ord("t", "n"), False)
    assert _try_resolve_cardinality_reversal(idx, "t", m) is None


def test_rejects_plus_offset():
    m = _model()
    # card(t) + ord(t) is not the reversal pattern
    idx = IndexOffset(
        "t",
        Binary("+", Call("card", (SymbolRef("t"),)), Call("ord", (SymbolRef("t"),))),
        False,
    )
    assert _try_resolve_cardinality_reversal(idx, "t", m) is None


def test_rejects_circular_offset():
    m = _model()
    # Circular (`++`/`--`) wrap-around offset must NOT resolve via the linear
    # cancellation — its modular edge semantics differ (review #1450).
    idx = IndexOffset("t", _card_minus_ord("t", "t"), True)
    assert _try_resolve_cardinality_reversal(idx, "t", m) is None


def test_rejects_dynamic_subset_without_static_members():
    # A dynamic subset (explicit parent domain, NO static members of its own)
    # would make resolve_set_members fall back to the PARENT's members, so
    # `members[-1]` would be the parent's last element — unsound (review #1450).
    m = ModelIR()
    m.sets["k"] = SetDef(name="k", domain=(), members=["a", "b", "c"])
    m.sets["ku"] = SetDef(name="ku", domain=("k",), members=[])  # populated at runtime
    idx = IndexOffset("ku", _card_minus_ord("ku", "ku"), False)
    assert _try_resolve_cardinality_reversal(idx, "ku", m) is None


def test_rejects_non_indexoffset():
    m = _model()
    assert _try_resolve_cardinality_reversal("t", "t", m) is None

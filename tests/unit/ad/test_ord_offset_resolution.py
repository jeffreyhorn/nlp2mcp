"""
Tests for ord() evaluation in IndexOffset resolution (Issue #1081).

Covers:
- _try_eval_offset() resolving Call('ord', (SymbolRef(elem),)) to Const
- _try_eval_offset() resolving Unary('-', Call('ord', ...)) to negative Const
- _try_eval_offset() resolving Binary('+'/'-', ...) with nested ord()
- _try_eval_offset() returning None for unresolvable expressions
- _resolve_index_offsets() resolving IndexOffset with ord() offset after
  sum expansion via _expand_sums_with_unresolved_offsets()
"""

from __future__ import annotations

import pytest

from src.ir.ast import (
    Binary,
    Call,
    Const,
    IndexOffset,
    Sum,
    SymbolRef,
    Unary,
    VarRef,
)
from src.ir.model_ir import ModelIR
from src.ir.symbols import SetDef

pytestmark = pytest.mark.unit


def _make_model_ir_with_set(set_name: str, members: list[str]) -> ModelIR:
    """Create a minimal ModelIR with one set."""
    model = ModelIR()
    sdef = SetDef(name=set_name, domain=(), members=members)
    model.sets[set_name] = sdef
    return model


# ---------------------------------------------------------------------------
# _try_eval_offset() — unit tests
# ---------------------------------------------------------------------------


class TestTryEvalOffset:
    """Tests for _try_eval_offset helper inside _resolve_index_offsets."""

    def _call_try_eval(self, offset_expr, model_ir):
        """Invoke _try_eval_offset via _resolve_index_offsets on a dummy VarRef."""
        from src.ad.constraint_jacobian import _resolve_index_offsets

        # Build a VarRef with an IndexOffset that uses the given offset_expr
        var = VarRef("x", (IndexOffset("3", offset_expr, False),))
        result = _resolve_index_offsets(var, model_ir, None)
        return result

    def test_ord_concrete_element(self):
        """ord('len-2') should resolve to 2.0 (1-based) when set has that element."""
        model_ir = _make_model_ir_with_set("l", ["len-1", "len-2", "len-3", "len-4"])
        # x has domain ('t',), set t = ['1','2','3','4','5']
        model_ir.sets["t"] = SetDef(name="t", domain=(), members=["1", "2", "3", "4", "5"])
        model_ir.variables["x"] = type("VDef", (), {"domain": ("t",)})()

        # IndexOffset('3', Call('ord', (SymbolRef('len-2'),))) with domain t
        # ord('len-2') = 2 (1-based), so 3 + 2 = 5 → position 4 → element '5'
        # Wait: offset is NEGATIVE in the original x(t - ord(l), l) pattern.
        # Let's test positive first: IndexOffset('3', Const(2.0)) → '5'
        # Here we test via _try_eval: Call('ord', (SymbolRef('len-2'),)) → Const(2.0)
        offset = Call("ord", (SymbolRef("len-2"),))
        result = self._call_try_eval(offset, model_ir)
        # pos('3') = 2 in set t, offset +2 → pos 4 → '5'
        assert isinstance(result, VarRef)
        assert result.indices == ("5",)

    def test_negative_ord(self):
        """Unary('-', Call('ord', ...)) should resolve to negative offset."""
        model_ir = _make_model_ir_with_set("l", ["len-1", "len-2", "len-3"])
        model_ir.sets["t"] = SetDef(name="t", domain=(), members=["1", "2", "3", "4", "5"])
        model_ir.variables["x"] = type("VDef", (), {"domain": ("t",)})()

        # Base='3', offset=Unary('-', Call('ord', SymbolRef('len-2')))
        # ord('len-2')=2 → offset=-2. pos('3')=2, 2+(-2)=0 → element '1'
        offset = Unary("-", Call("ord", (SymbolRef("len-2"),)))
        result = self._call_try_eval(offset, model_ir)
        assert isinstance(result, VarRef)
        assert result.indices == ("1",)

    def test_ord_out_of_bounds_returns_zero(self):
        """ord() offset leading to out-of-bounds should produce Const(0)."""
        model_ir = _make_model_ir_with_set("l", ["len-1", "len-2", "len-3"])
        model_ir.sets["t"] = SetDef(name="t", domain=(), members=["1", "2", "3"])
        model_ir.variables["x"] = type("VDef", (), {"domain": ("t",)})()

        # IndexOffset('1', Call('ord', SymbolRef('len-3'))) = pos 0 + 3 = 3 → out of bounds
        offset = Call("ord", (SymbolRef("len-3"),))
        result = self._call_try_eval(offset, model_ir)
        assert isinstance(result, Const)
        assert result.value == 0

    def test_binary_with_ord(self):
        """Binary expressions involving ord() should be evaluated."""
        model_ir = _make_model_ir_with_set("l", ["a", "b", "c"])
        model_ir.sets["t"] = SetDef(name="t", domain=(), members=["1", "2", "3", "4", "5"])
        model_ir.variables["x"] = type("VDef", (), {"domain": ("t",)})()

        # IndexOffset('3', Binary('-', Const(5), Call('ord', SymbolRef('b'))))
        # ord('b') = 2, so 5 - 2 = 3. pos('3') = 2, 2 + 3 = 5 → out of bounds for 5-elem set
        # Actually position 5 is out of bounds (0-indexed, max 4). Hmm, 0-indexed: pos 2 + 3 = 5, max=4.
        # Let's use a 6-element set to keep it in bounds.
        model_ir.sets["t"] = SetDef(name="t", domain=(), members=["1", "2", "3", "4", "5", "6"])
        offset = Binary("-", Const(5.0), Call("ord", (SymbolRef("b"),)))
        result = self._call_try_eval(offset, model_ir)
        # pos('3') = 2, offset = 3, new_pos = 5 → '6'
        assert isinstance(result, VarRef)
        assert result.indices == ("6",)

    def test_unresolvable_call(self):
        """Non-ord/card Call should leave IndexOffset unresolved."""
        model_ir = _make_model_ir_with_set("l", ["a", "b"])
        model_ir.sets["t"] = SetDef(name="t", domain=(), members=["1", "2", "3"])
        model_ir.variables["x"] = type("VDef", (), {"domain": ("t",)})()

        offset = Call("sqrt", (Const(4.0),))
        result = self._call_try_eval(offset, model_ir)
        # Should remain a VarRef with unresolved IndexOffset
        assert isinstance(result, VarRef)
        assert isinstance(result.indices[0], IndexOffset)

    def test_card_evaluation(self):
        """card(set_name) should resolve to set cardinality."""
        model_ir = _make_model_ir_with_set("l", ["a", "b", "c", "d"])
        # Need enough elements: base='3' (pos 2) + card(l)=4 = 6 → need 7+ elements
        model_ir.sets["t"] = SetDef(
            name="t", domain=(), members=["1", "2", "3", "4", "5", "6", "7"]
        )
        model_ir.variables["x"] = type("VDef", (), {"domain": ("t",)})()

        # _call_try_eval uses IndexOffset('3', offset) via base '3'
        # card(l) = 4, pos('3') = 2, 2 + 4 = 6 → element '7'
        offset = Call("card", (SymbolRef("l"),))
        result = self._call_try_eval(offset, model_ir)
        assert isinstance(result, VarRef)
        assert result.indices == ("7",)


# ---------------------------------------------------------------------------
# Sum expansion with unresolved offsets
# ---------------------------------------------------------------------------


class TestSumExpansionWithOrd:
    """Tests for _expand_sums_with_unresolved_offsets resolving ord() offsets."""

    def test_sum_with_ord_offset_expands(self):
        """Sum(l, x(t-ord(l),l)) should expand with resolved offsets."""
        from src.ad.constraint_jacobian import _expand_sums_with_unresolved_offsets

        model_ir = _make_model_ir_with_set("l", ["a", "b"])
        model_ir.sets["t"] = SetDef(name="t", domain=(), members=["1", "2", "3"])
        model_ir.variables["x"] = type("VDef", (), {"domain": ("t", "l")})()

        # Build: sum(l, x(IndexOffset('3', Unary('-', Call('ord', SymbolRef('l')))), l))
        inner = VarRef(
            "x",
            (
                IndexOffset("3", Unary("-", Call("ord", (SymbolRef("l"),))), False),
                "l",
            ),
        )
        expr = Sum(("l",), inner)

        result = _expand_sums_with_unresolved_offsets(expr, model_ir, {})

        # Should expand to x('2','a') + x('1','b')
        # l='a': ord('a')=1, 3-1=2 → x('2','a')
        # l='b': ord('b')=2, 3-2=1 → x('1','b')
        assert isinstance(result, Binary)
        assert result.op == "+"

        # Check that both terms are resolved VarRefs (no IndexOffset remaining)
        def _collect_varrefs(e):
            if isinstance(e, VarRef):
                return [e]
            if isinstance(e, Binary):
                return _collect_varrefs(e.left) + _collect_varrefs(e.right)
            return []

        refs = _collect_varrefs(result)
        assert len(refs) == 2
        idx_sets = {ref.indices for ref in refs}
        assert ("2", "a") in idx_sets
        assert ("1", "b") in idx_sets

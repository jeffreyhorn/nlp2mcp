"""Sprint 25 / #1234: scalar-constant offset resolution.

When a model declares `Scalar l /4/` and uses `pd(tt-l)`, the parser
produces `IndexOffset('tt', Unary('-', SymbolRef('l')))` — opaque to
the AD engine. The resolver substitutes `l → 4`, producing
`IndexOffset('tt', Const(-4))` which the AD treats as a standard
integer offset.
"""

from __future__ import annotations

import pytest

from src.ir.ast import (
    Binary,
    Const,
    IndexOffset,
    SymbolRef,
    Unary,
    VarRef,
)
from src.ir.model_ir import ModelIR
from src.ir.scalar_offset_resolver import (
    _resolve_offset_to_const,
    resolve_scalar_offsets,
)
from src.ir.symbols import EquationDef, ParameterDef, Rel


@pytest.mark.unit
def test_resolve_symbol_ref_to_scalar_value():
    """`SymbolRef('l')` with `l = 4` resolves to `Const(4.0)`."""
    scalars = {"l": 4.0}
    result = _resolve_offset_to_const(SymbolRef("l"), scalars)
    assert isinstance(result, Const)
    assert result.value == 4.0


@pytest.mark.unit
def test_resolve_unary_negation():
    """`Unary('-', SymbolRef('l'))` with `l = 4` resolves to `Const(-4.0)`."""
    scalars = {"l": 4.0}
    expr = Unary("-", SymbolRef("l"))
    result = _resolve_offset_to_const(expr, scalars)
    assert isinstance(result, Const)
    assert result.value == -4.0


@pytest.mark.unit
def test_resolve_binary_arithmetic():
    """`Binary('+', SymbolRef('a'), SymbolRef('b'))` with a=2, b=3 → Const(5)."""
    scalars = {"a": 2.0, "b": 3.0}
    expr = Binary("+", SymbolRef("a"), SymbolRef("b"))
    result = _resolve_offset_to_const(expr, scalars)
    assert isinstance(result, Const)
    assert result.value == 5.0


@pytest.mark.unit
def test_unresolvable_returns_none():
    """An offset referencing a non-scalar (or non-numeric) parameter
    can't be resolved at IR-build time; returns None."""
    scalars: dict[str, float] = {}
    result = _resolve_offset_to_const(SymbolRef("nonexistent"), scalars)
    assert result is None


@pytest.mark.unit
def test_resolve_scalar_offsets_in_equation_body():
    """End-to-end: a synthetic model with `pd(tt-l)` and `Scalar l /4/`
    should rewrite the equation body's IndexOffset.offset from
    `Unary('-', SymbolRef('l'))` to `Const(-4.0)`.
    """
    ir = ModelIR()
    # Scalar param l = 4
    ir.params["l"] = ParameterDef(name="l", domain=(), values={(): 4.0})
    # Equation body: VarRef('pd', (IndexOffset('tt', Unary('-', SymbolRef('l'))),))
    body = VarRef(
        "pd",
        (IndexOffset(base="tt", offset=Unary("-", SymbolRef("l")), circular=False),),
    )
    ir.equations["test_eq"] = EquationDef(
        name="test_eq",
        domain=("tt",),
        relation=Rel.EQ,
        lhs_rhs=(body, Const(0.0)),
    )

    rewrites = resolve_scalar_offsets(ir)

    assert rewrites > 0
    new_body = ir.equations["test_eq"].lhs_rhs[0]
    assert isinstance(new_body, VarRef)
    assert len(new_body.indices) == 1
    new_idx = new_body.indices[0]
    assert isinstance(new_idx, IndexOffset)
    assert new_idx.base == "tt"
    assert isinstance(new_idx.offset, Const)
    assert new_idx.offset.value == -4.0


@pytest.mark.unit
def test_no_op_when_no_scalars():
    """A model with no scalar params should pass through with 0 rewrites."""
    ir = ModelIR()
    rewrites = resolve_scalar_offsets(ir)
    assert rewrites == 0


@pytest.mark.unit
def test_no_op_when_offset_already_const():
    """An offset that's already `Const(-4)` should not be re-wrapped."""
    ir = ModelIR()
    ir.params["l"] = ParameterDef(name="l", domain=(), values={(): 4.0})
    body = VarRef(
        "pd",
        (IndexOffset(base="tt", offset=Const(-4.0), circular=False),),
    )
    ir.equations["test_eq"] = EquationDef(
        name="test_eq",
        domain=("tt",),
        relation=Rel.EQ,
        lhs_rhs=(body, Const(0.0)),
    )

    rewrites = resolve_scalar_offsets(ir)

    # No rewrite should occur — the offset was already `Const`.
    assert rewrites == 0


@pytest.mark.unit
def test_indexed_param_not_treated_as_scalar():
    """An indexed parameter (e.g., `a(i) /1, 2/`) MUST NOT be treated as
    a scalar substitution candidate, even if it has a value at key `()`
    by mistake. Only params with `domain == ()` are eligible.
    """
    ir = ModelIR()
    ir.params["a"] = ParameterDef(name="a", domain=("i",), values={("i1",): 1.0})
    body = VarRef(
        "pd",
        (IndexOffset(base="tt", offset=SymbolRef("a"), circular=False),),
    )
    ir.equations["test_eq"] = EquationDef(
        name="test_eq",
        domain=("tt",),
        relation=Rel.EQ,
        lhs_rhs=(body, Const(0.0)),
    )

    rewrites = resolve_scalar_offsets(ir)

    # Indexed param 'a' is not a scalar; offset stays opaque.
    assert rewrites == 0

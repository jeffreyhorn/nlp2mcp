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
    Call,
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
from src.ir.symbols import EquationDef, ParameterDef, Rel, VariableDef


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


@pytest.mark.unit
def test_non_integer_scalar_not_substituted():
    """A scalar with a non-integer value (e.g., `Scalar half /0.5/`)
    must NOT be substituted into an IndexOffset — `IndexOffset` requires
    integer offsets and the AD's `_resolve_idx` rejects non-integer
    floats.
    """
    ir = ModelIR()
    ir.params["half"] = ParameterDef(name="half", domain=(), values={(): 0.5})
    body = VarRef(
        "pd",
        (IndexOffset(base="tt", offset=SymbolRef("half"), circular=False),),
    )
    ir.equations["test_eq"] = EquationDef(
        name="test_eq",
        domain=("tt",),
        relation=Rel.EQ,
        lhs_rhs=(body, Const(0.0)),
    )

    rewrites = resolve_scalar_offsets(ir)

    assert rewrites == 0
    new_body = ir.equations["test_eq"].lhs_rhs[0]
    assert isinstance(new_body, VarRef)
    new_idx = new_body.indices[0]
    assert isinstance(new_idx, IndexOffset)
    # Offset stays as the original SymbolRef (not collapsed to Const(0.5)).
    assert isinstance(new_idx.offset, SymbolRef)


@pytest.mark.unit
def test_non_integer_leaf_blocks_resolution():
    """`_resolve_offset_to_const` is strictly integer-only at every
    sub-expression. A non-integer leaf scalar (e.g., `0.5`) causes the
    resolver to bail out at that leaf, so any expression containing one
    fails to resolve — even if the final arithmetic happens to land on
    an integer value (e.g., `0.5 + 0.5 = 1`).

    This conservative behavior is intentional: it keeps the leaf-level
    invariant simple ("only integers cross resolver boundaries") and
    matches AD's expectation that `IndexOffset.offset` be integer.
    Models that genuinely want `tt - 1` should write that literally
    rather than rely on the resolver to evaluate `tt - half - half`.
    """
    scalars = {"half": 0.5, "two": 2.0, "three": 3.0}

    # half by itself is non-integer — must NOT resolve.
    assert _resolve_offset_to_const(SymbolRef("half"), scalars) is None

    # 2 * 0.5 = 1 mathematically, but the leaf `half` returns None,
    # propagating up. (Resolver is leaf-strict.)
    expr_lands_on_int = Binary("*", SymbolRef("two"), SymbolRef("half"))
    assert _resolve_offset_to_const(expr_lands_on_int, scalars) is None

    # 3 * 0.5 = 1.5 — same outcome.
    expr_frac = Binary("*", SymbolRef("three"), SymbolRef("half"))
    assert _resolve_offset_to_const(expr_frac, scalars) is None

    # All-integer expression resolves cleanly.
    expr_int = Binary("+", SymbolRef("two"), SymbolRef("three"))
    assert _resolve_offset_to_const(expr_int, scalars).value == 5.0


@pytest.mark.unit
def test_scalar_with_runtime_assignment_excluded():
    """A scalar that's reassigned at runtime via `expressions` (e.g.,
    `Scalar l /4/; l = 2 * x.l;`) MUST be excluded from the substitution
    map. Trusting the initial value `4` would silently produce an
    incorrect offset if `l` changes before the affected equation is
    used.
    """
    ir = ModelIR()
    pdef = ParameterDef(name="l", domain=(), values={(): 4.0})
    # Simulate a runtime reassignment by adding a single entry to expressions.
    pdef.expressions.append(((), Const(7.0)))
    ir.params["l"] = pdef

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

    assert rewrites == 0
    # Offset stays in its original symbolic form.
    new_body = ir.equations["test_eq"].lhs_rhs[0]
    new_idx = new_body.indices[0]
    assert isinstance(new_idx.offset, Unary)


@pytest.mark.unit
def test_resolve_scalar_offsets_in_variable_scale():
    """`VariableDef.scale` (Issue #835) is an Expr-valued attribute that
    can carry IndexOffset indices and is emitted in the variable bounds
    pass, so it must participate in scalar-offset resolution alongside
    `l_expr` / `lo_expr` / `up_expr` / `fx_expr`.

    Verifies both the scalar `scale` slot and the per-element `scale_map`.
    """
    ir = ModelIR()
    ir.params["l"] = ParameterDef(name="l", domain=(), values={(): 4.0})

    # Scalar scale: x.scale = pd(tt-l) — synthetic but exercises the
    # `scale` attr branch.
    scale_expr = VarRef(
        "pd",
        (IndexOffset(base="tt", offset=Unary("-", SymbolRef("l")), circular=False),),
    )
    # Per-element scale: x.scale(i) = pd(tt-l)
    scale_map_expr = VarRef(
        "pd",
        (IndexOffset(base="tt", offset=Unary("-", SymbolRef("l")), circular=False),),
    )
    var = VariableDef(name="x", domain=("i",))
    var.scale = scale_expr
    var.scale_map[("i1",)] = scale_map_expr
    ir.variables["x"] = var

    rewrites = resolve_scalar_offsets(ir)

    # Two leaf rewrites: one in `scale`, one in `scale_map[('i1',)]`.
    assert rewrites == 2

    new_scale = ir.variables["x"].scale
    assert isinstance(new_scale, VarRef)
    assert isinstance(new_scale.indices[0], IndexOffset)
    assert isinstance(new_scale.indices[0].offset, Const)
    assert new_scale.indices[0].offset.value == -4.0

    new_scale_map_expr = ir.variables["x"].scale_map[("i1",)]
    assert isinstance(new_scale_map_expr.indices[0].offset, Const)
    assert new_scale_map_expr.indices[0].offset.value == -4.0


@pytest.mark.unit
def test_index_offset_collapsed_in_non_indices_tuple_field():
    """`IndexOffset` is an `Expr` subclass, so when it appears in a
    tuple-of-Expr field that is NOT named `indices` (e.g., `Call.args`),
    `_rewrite_expr` must dispatch on `IndexOffset` BEFORE the generic
    `Expr` recursion — otherwise the leaf-collapse logic is unreachable
    and the offset stays opaque.

    Construct a synthetic `Call("foo", (IndexOffset("tt", Unary("-",
    SymbolRef("l"))),))` inside an equation body. With the bugged
    ordering (`Expr` checked first), the IndexOffset would be re-entered
    via `_rewrite_expr`, walking only its inner `.offset` Expr without
    collapsing the IndexOffset itself to a new node with `Const(-4)`.
    With the fix, the leaf branch fires and collapses the offset.
    """
    ir = ModelIR()
    ir.params["l"] = ParameterDef(name="l", domain=(), values={(): 4.0})

    body = Call(
        "foo",
        (IndexOffset(base="tt", offset=Unary("-", SymbolRef("l")), circular=False),),
    )
    ir.equations["test_eq"] = EquationDef(
        name="test_eq",
        domain=("tt",),
        relation=Rel.EQ,
        lhs_rhs=(body, Const(0.0)),
    )

    rewrites = resolve_scalar_offsets(ir)

    assert rewrites == 1
    new_body = ir.equations["test_eq"].lhs_rhs[0]
    assert isinstance(new_body, Call)
    assert len(new_body.args) == 1
    new_arg = new_body.args[0]
    assert isinstance(new_arg, IndexOffset)
    assert isinstance(new_arg.offset, Const)
    assert new_arg.offset.value == -4.0

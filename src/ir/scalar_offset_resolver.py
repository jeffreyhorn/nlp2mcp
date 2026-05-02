"""Issue #1234: resolve scalar-constant references inside `IndexOffset.offset`.

When the source uses a `Scalar l /4/` and an offset `pd(tt-l)`, the parser
produces `IndexOffset('tt', Unary('-', SymbolRef('l')))` — opaque to the
AD engine, which expects integer offsets.

This pass walks the IR and replaces any `IndexOffset.offset` expression
that evaluates to a numeric constant (composed only of `Const`,
`SymbolRef`s pointing to scalar `ParameterDef`s with a single `()`
value, `Unary` `+`/`-`, and `Binary` `+`/`-`/`*` — division and
exponentiation are intentionally NOT supported because they easily
produce non-integer offsets that AD will refuse downstream) with a
single `Const(value)`.

Result: `pd(tt-l)` (where `l = 4`) becomes `pd(tt-4)` — a standard
integer offset that the AD machinery handles correctly.
"""

from __future__ import annotations

from src.ir.ast import (
    Binary,
    Const,
    Expr,
    IndexOffset,
    SubsetIndex,
    SymbolRef,
    Unary,
)
from src.ir.model_ir import ModelIR

# Synthetic attributes the parser may attach to frozen-dataclass `Expr`
# instances (and, in principle, other AST nodes like `IndexOffset`) via
# `object.__setattr__`. Reconstructing a node via `type(node)(**fields)`
# would lose these; we copy them onto replacement nodes to avoid
# downstream "Domain mismatch" errors during normalization / AD.
_SYNTHETIC_ATTRS = ("domain", "symbol_domain", "free_domain", "rank", "index_values")


def _copy_synthetic_attrs(old: object, new: object) -> None:
    """Copy any `_SYNTHETIC_ATTRS` present on ``old`` onto ``new``.

    Silently skips attrs that aren't set on ``old`` or can't be set on
    ``new`` (e.g., when the dataclass is frozen and the attr is part of
    its declared fields — a no-op in that case is fine).
    """
    for attr in _SYNTHETIC_ATTRS:
        if hasattr(old, attr):
            try:
                object.__setattr__(new, attr, getattr(old, attr))
            except (AttributeError, TypeError):
                pass


def _resolve_offset_to_const(offset_expr: Expr, scalars: dict[str, float]) -> Const | None:
    """Try to evaluate `offset_expr` to a numeric constant using `scalars`
    (a map of lowercase scalar parameter name → value). Returns
    `Const(value)` on success, or `None` if any sub-expression can't be
    resolved.

    Supported leaf/operator set:
    - `Const` (numeric values pass through)
    - `SymbolRef` resolving to a key in ``scalars``
    - `Unary` ops `+`, `-`
    - `Binary` ops `+`, `-`, `*` (division and exponentiation are
      intentionally rejected to avoid emitting non-integer offsets)
    """
    if isinstance(offset_expr, Const):
        # Already a const — pass through (caller may decide to wrap).
        if isinstance(offset_expr.value, (int, float)):
            return offset_expr
        return None
    if isinstance(offset_expr, SymbolRef):
        val = scalars.get(offset_expr.name.lower())
        if val is None:
            return None
        return Const(float(val))
    if isinstance(offset_expr, Unary):
        child = _resolve_offset_to_const(offset_expr.child, scalars)
        if child is None:
            return None
        if offset_expr.op == "-":
            return Const(-float(child.value))
        if offset_expr.op == "+":
            return child
        return None
    if isinstance(offset_expr, Binary):
        left = _resolve_offset_to_const(offset_expr.left, scalars)
        right = _resolve_offset_to_const(offset_expr.right, scalars)
        if left is None or right is None:
            return None
        lv = float(left.value)
        rv = float(right.value)
        if offset_expr.op == "+":
            return Const(lv + rv)
        if offset_expr.op == "-":
            return Const(lv - rv)
        if offset_expr.op == "*":
            return Const(lv * rv)
        return None
    return None


def _build_scalar_value_map(model_ir: ModelIR) -> dict[str, float]:
    """Collect all SCALAR parameters whose declared `domain == ()` and whose
    `values` map contains a single numeric entry at key `()`.

    Scalars without a numeric value (e.g., assigned at runtime via
    expressions) are excluded — those can't be substituted at IR-build time.
    """
    out: dict[str, float] = {}
    for name, pdef in model_ir.params.items():
        if pdef.domain:
            continue
        v = pdef.values.get(())
        if isinstance(v, (int, float)):
            out[name.lower()] = float(v)
    return out


def _make_resolved_index_offset(orig: IndexOffset, resolved: Const) -> IndexOffset:
    """Build a replacement `IndexOffset` with the resolved `Const` offset
    and copy any synthetic attributes from the original onto the new node.
    """
    new = IndexOffset(orig.base, resolved, orig.circular)
    _copy_synthetic_attrs(orig, new)
    return new


def _rewrite_indices(indices: tuple, scalars: dict[str, float], counter: list[int]) -> tuple:
    """Walk an indices tuple and rewrite any `IndexOffset` whose `.offset`
    resolves to a numeric constant. Other index types pass through.

    Returns the SAME tuple object when no rewrite happened — preserves
    identity so callers (e.g., `_rewrite_expr`) can skip dataclass
    reconstruction when nothing changed. Reconstructing the parent
    dataclass would lose synthetic attributes attached by the parser
    via `object.__setattr__` (e.g., `domain`, `symbol_domain`,
    `free_domain`, `rank`).

    `counter` is a single-element list used as a mutable counter to
    track the number of `IndexOffset` nodes actually rewritten (so
    callers report only leaf rewrites, not parent-Expr rebuilds).
    """
    new_indices: list = []
    changed = False
    for idx in indices:
        if isinstance(idx, IndexOffset):
            resolved = _resolve_offset_to_const(idx.offset, scalars)
            if resolved is not None and not isinstance(idx.offset, Const):
                new_indices.append(_make_resolved_index_offset(idx, resolved))
                changed = True
                counter[0] += 1
                continue
        new_indices.append(idx)
    if not changed:
        return indices
    return tuple(new_indices)


def _rewrite_expr(expr: Expr, scalars: dict[str, float], counter: list[int]) -> Expr:
    """Recursively rewrite Expr, resolving scalar offsets in any
    `*Ref.indices` tuples.

    Returns a new Expr (or the same object if no rewrite was needed).
    `counter` is propagated so leaf `IndexOffset` rewrites are counted
    (not the parent-Expr rebuilds we trigger to carry the change up).
    """
    import dataclasses as _dc

    if not hasattr(expr, "__dataclass_fields__"):
        return expr

    fields = _dc.fields(expr)  # type: ignore[arg-type]
    new_kwargs: dict[str, object] = {}
    changed = False
    for f in fields:
        val = getattr(expr, f.name, None)
        if f.name == "indices" and isinstance(val, tuple):
            # Rewrite indices tuple (handles IndexOffsets inside).
            new_indices_val: tuple = _rewrite_indices(val, scalars, counter)
            if new_indices_val is not val:
                changed = True
            new_kwargs[f.name] = new_indices_val
        elif isinstance(val, Expr):
            new_expr_val: Expr = _rewrite_expr(val, scalars, counter)
            if new_expr_val is not val:
                changed = True
            new_kwargs[f.name] = new_expr_val
        elif isinstance(val, tuple):
            inner_changed = False
            inner: list = []
            for item in val:
                if isinstance(item, Expr):
                    new_item: Expr = _rewrite_expr(item, scalars, counter)
                    if new_item is not item:
                        inner_changed = True
                    inner.append(new_item)
                elif isinstance(item, IndexOffset):
                    resolved = _resolve_offset_to_const(item.offset, scalars)
                    if resolved is not None and not isinstance(item.offset, Const):
                        inner.append(_make_resolved_index_offset(item, resolved))
                        inner_changed = True
                        counter[0] += 1
                    else:
                        inner.append(item)
                elif isinstance(item, SubsetIndex):
                    # SubsetIndex is opaque — pass through.
                    inner.append(item)
                else:
                    inner.append(item)
            if inner_changed:
                changed = True
                new_kwargs[f.name] = tuple(inner)
            else:
                new_kwargs[f.name] = val
        else:
            new_kwargs[f.name] = val
    if not changed:
        return expr
    new_expr = type(expr)(**new_kwargs)
    # Preserve synthetic attributes attached by the parser via
    # `object.__setattr__` on frozen-dataclass Exprs (e.g., `domain`,
    # `symbol_domain`, `free_domain`, `rank`, `index_values`). These
    # are read by downstream normalization (`_merge_domains`) and AD
    # code; losing them produces "Domain mismatch" errors.
    _copy_synthetic_attrs(expr, new_expr)
    return new_expr


def resolve_scalar_offsets(model_ir: ModelIR) -> int:
    """Issue #1234: rewrite the IR in place to resolve scalar-constant
    references in `IndexOffset.offset` expressions.

    Walks every Expr in:
    - `model_ir.equations` (lhs_rhs, condition)
    - `model_ir.params[*].expressions` (RHS Exprs)
    - `model_ir.variables[*]` (l_expr, lo_expr, up_expr, fx_expr +
      their `*_map` siblings)
    - `model_ir.objective.expr` (if set)

    Returns the number of `IndexOffset` nodes whose `.offset` was
    actually collapsed to `Const` (counted at the leaf rewrite sites,
    not at parent-Expr rebuilds — those are an implementation detail
    needed to propagate the change up through frozen dataclasses).
    """
    scalars = _build_scalar_value_map(model_ir)
    if not scalars:
        return 0

    counter: list[int] = [0]

    # Equations: lhs/rhs and condition.
    for eq_def in model_ir.equations.values():
        lhs, rhs = eq_def.lhs_rhs
        new_lhs = _rewrite_expr(lhs, scalars, counter) if isinstance(lhs, Expr) else lhs
        new_rhs = _rewrite_expr(rhs, scalars, counter) if isinstance(rhs, Expr) else rhs
        if new_lhs is not lhs or new_rhs is not rhs:
            eq_def.lhs_rhs = (new_lhs, new_rhs)
        if eq_def.condition is not None and isinstance(eq_def.condition, Expr):
            new_cond = _rewrite_expr(eq_def.condition, scalars, counter)
            if new_cond is not eq_def.condition:
                eq_def.condition = new_cond

    # Parameters: each (indices, expr) entry.
    for pdef in model_ir.params.values():
        new_exprs: list = []
        any_changed = False
        for indices, expr in pdef.expressions:
            new_expr = _rewrite_expr(expr, scalars, counter)
            new_indices = _rewrite_indices(indices, scalars, counter)
            if new_expr is not expr or new_indices is not indices:
                any_changed = True
            new_exprs.append((new_indices, new_expr))
        if any_changed:
            pdef.expressions = new_exprs

    # Variables: l_expr / lo_expr / up_expr / fx_expr and *_map.
    for var_def in model_ir.variables.values():
        for attr in ("l_expr", "lo_expr", "up_expr", "fx_expr"):
            cur = getattr(var_def, attr, None)
            if isinstance(cur, Expr):
                new_cur = _rewrite_expr(cur, scalars, counter)
                if new_cur is not cur:
                    setattr(var_def, attr, new_cur)
        for attr_map in (
            "l_expr_map",
            "lo_expr_map",
            "up_expr_map",
            "fx_expr_map",
        ):
            emap = getattr(var_def, attr_map, None)
            if not emap:
                continue
            new_map: dict = {}
            map_changed = False
            for indices, expr in emap.items():
                new_expr = _rewrite_expr(expr, scalars, counter)
                new_indices = _rewrite_indices(indices, scalars, counter)
                if new_expr is not expr or new_indices is not indices:
                    map_changed = True
                new_map[new_indices] = new_expr
            if map_changed:
                setattr(var_def, attr_map, new_map)

    # Objective expression (if extracted).
    if model_ir.objective is not None and model_ir.objective.expr is not None:
        new_obj = _rewrite_expr(model_ir.objective.expr, scalars, counter)
        if new_obj is not model_ir.objective.expr:
            model_ir.objective.expr = new_obj

    return counter[0]

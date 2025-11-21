from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

# ---------- Expression AST ----------


class Expr:
    """Base class for all expression nodes."""

    def children(self) -> Iterable[Expr]:
        return []

    def pretty(self) -> str:
        """Debug-friendly single-line rendering."""
        return repr(self)


@dataclass(frozen=True)
class Const(Expr):
    value: float

    def __repr__(self) -> str:
        return f"Const({self.value})"


@dataclass(frozen=True)
class SymbolRef(Expr):
    """Reference to a scalar symbol (variable or parameter) without indices."""

    name: str

    def __repr__(self) -> str:
        return f"SymbolRef({self.name})"


@dataclass(frozen=True)
class VarRef(Expr):
    """Reference to a variable; indices are symbolic (strings or IndexOffset)."""

    name: str
    indices: tuple[str | IndexOffset, ...] = ()

    def indices_as_strings(self) -> tuple[str, ...]:
        """Convert indices to strings, raising error if IndexOffset present."""
        result = []
        for idx in self.indices:
            if isinstance(idx, IndexOffset):
                raise NotImplementedError(f"IndexOffset not yet supported in this context: {idx}")
            result.append(idx)
        return tuple(result)

    def __repr__(self) -> str:
        idx = ",".join(str(i) if isinstance(i, IndexOffset) else i for i in self.indices)
        return f"VarRef({self.name}({idx}))" if idx else f"VarRef({self.name})"


@dataclass(frozen=True)
class ParamRef(Expr):
    """Reference to a parameter; indices symbolic (strings or IndexOffset)."""

    name: str
    indices: tuple[str | IndexOffset, ...] = ()

    def indices_as_strings(self) -> tuple[str, ...]:
        """Convert indices to strings, raising error if IndexOffset present."""
        result = []
        for idx in self.indices:
            if isinstance(idx, IndexOffset):
                raise NotImplementedError(f"IndexOffset not yet supported in this context: {idx}")
            result.append(idx)
        return tuple(result)

    def __repr__(self) -> str:
        idx = ",".join(str(i) if isinstance(i, IndexOffset) else i for i in self.indices)
        return f"ParamRef({self.name}({idx}))" if idx else f"ParamRef({self.name})"


@dataclass(frozen=True)
class EquationRef(Expr):
    """Reference to an equation with attribute access (e.g., eq1.m, eq2.l).

    Sprint 9 Day 6: Equations can be referenced for their attributes (.l, .m)
    in post-solve contexts (e.g., display eq.l, x = eq.m).
    """

    name: str
    indices: tuple[str | IndexOffset, ...] = ()
    attribute: str = "l"  # Default to level attribute (.l)

    def indices_as_strings(self) -> tuple[str, ...]:
        """Convert indices to strings, raising error if IndexOffset present."""
        result = []
        for idx in self.indices:
            if isinstance(idx, IndexOffset):
                raise NotImplementedError(f"IndexOffset not yet supported in this context: {idx}")
            result.append(idx)
        return tuple(result)

    def __repr__(self) -> str:
        idx = ",".join(str(i) if isinstance(i, IndexOffset) else i for i in self.indices)
        base = f"{self.name}({idx})" if idx else self.name
        return f"EquationRef({base}.{self.attribute})"


@dataclass(frozen=True)
class MultiplierRef(Expr):
    """Reference to a KKT multiplier variable (λ, ν, π)."""

    name: str
    indices: tuple[str | IndexOffset, ...] = ()

    def indices_as_strings(self) -> tuple[str, ...]:
        """Convert indices to strings, raising error if IndexOffset present."""
        result = []
        for idx in self.indices:
            if isinstance(idx, IndexOffset):
                raise NotImplementedError(f"IndexOffset not yet supported in this context: {idx}")
            result.append(idx)
        return tuple(result)

    def __repr__(self) -> str:
        idx = ",".join(str(i) if isinstance(i, IndexOffset) else i for i in self.indices)
        return f"MultiplierRef({self.name}({idx}))" if idx else f"MultiplierRef({self.name})"


@dataclass(frozen=True)
class Unary(Expr):
    op: str  # "+", "-", maybe functions map elsewhere
    child: Expr

    def children(self) -> Iterable[Expr]:
        yield self.child

    def __repr__(self) -> str:
        return f"Unary({self.op}, {self.child!r})"


@dataclass(frozen=True)
class Binary(Expr):
    op: str  # "+", "-", "*", "/", "^", comparisons, "and", "or"
    left: Expr
    right: Expr

    def children(self) -> Iterable[Expr]:
        yield self.left
        yield self.right

    def __repr__(self) -> str:
        return f"Binary({self.op}, {self.left!r}, {self.right!r})"


@dataclass(frozen=True)
class Sum(Expr):
    """sum(i,j, body) — indices are symbolic set names."""

    index_sets: tuple[str, ...]
    body: Expr

    def children(self) -> Iterable[Expr]:
        yield self.body

    def __repr__(self) -> str:
        idx = ",".join(self.index_sets)
        return f"Sum(({idx}), {self.body!r})"


@dataclass(frozen=True)
class Call(Expr):
    """Function call: exp(x), log(x), power(x,y), etc."""

    func: str
    args: tuple[Expr, ...]

    def children(self) -> Iterable[Expr]:
        yield from self.args

    def __repr__(self) -> str:
        args = ", ".join(repr(a) for a in self.args)
        return f"Call({self.func}, ({args}))"


@dataclass(frozen=True)
class IndexOffset(Expr):
    """
    Lead/lag indexing offset (Sprint 9 Day 3).

    Examples:
        i++1  → IndexOffset(base='i', offset=Const(1), circular=True)
        i--2  → IndexOffset(base='i', offset=Const(-2), circular=True)
        i+1   → IndexOffset(base='i', offset=Const(1), circular=False)
        i-3   → IndexOffset(base='i', offset=Const(-3), circular=False)
        i+j   → IndexOffset(base='i', offset=SymbolRef('j'), circular=False)

    Attributes:
        base: Base identifier (e.g., 'i', 't', 's')
        offset: Offset expression (Const, SymbolRef, Binary, etc.)
        circular: True for ++/-- (wrap-around), False for +/- (suppress)
    """

    base: str
    offset: Expr
    circular: bool

    def children(self) -> Iterable[Expr]:
        yield self.offset

    def __repr__(self) -> str:
        return f"IndexOffset(base={self.base!r}, offset={self.offset!r}, circular={self.circular})"

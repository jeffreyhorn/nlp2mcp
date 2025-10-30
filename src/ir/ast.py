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
    """Reference to a variable; indices are symbolic (strings)."""

    name: str
    indices: tuple[str, ...] = ()

    def __repr__(self) -> str:
        idx = ",".join(self.indices)
        return f"VarRef({self.name}({idx}))" if idx else f"VarRef({self.name})"


@dataclass(frozen=True)
class ParamRef(Expr):
    """Reference to a parameter; indices symbolic (strings)."""

    name: str
    indices: tuple[str, ...] = ()

    def __repr__(self) -> str:
        idx = ",".join(self.indices)
        return f"ParamRef({self.name}({idx}))" if idx else f"ParamRef({self.name})"


@dataclass(frozen=True)
class MultiplierRef(Expr):
    """Reference to a KKT multiplier variable (λ, ν, π)."""

    name: str
    indices: tuple[str, ...] = ()

    def __repr__(self) -> str:
        idx = ",".join(self.indices)
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

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class Rel(Enum):
    EQ = "=e="
    LE = "=l="
    GE = "=g="


class VarKind(Enum):
    CONTINUOUS = auto()
    POSITIVE = auto()
    NEGATIVE = auto()
    BINARY = auto()
    INTEGER = auto()


class ObjSense(Enum):
    MIN = "min"
    MAX = "max"


@dataclass
class SetDef:
    name: str
    members: list[str] = field(default_factory=list)  # canonical member strings
    # If empty, could indicate universe or defined elsewhere.


@dataclass
class AliasDef:
    """Alias of sets: alias A,B over universe U (optional)."""

    name: str
    target: str
    universe: str | None = None  # name of a set that defines the universe (optional)


@dataclass
class ParameterDef:
    name: str
    domain: tuple[str, ...] = ()  # e.g., ("i","j")
    values: dict[tuple[str, ...], float] = field(default_factory=dict)


@dataclass
class VariableDef:
    name: str
    domain: tuple[str, ...] = ()  # e.g., ("i","j")
    kind: VarKind = VarKind.CONTINUOUS
    lo: float | None = None  # None = -inf if unspecified
    up: float | None = None  # None = +inf if unspecified
    fx: float | None = None  # fixed value overrides lo/up
    l: float | None = None  # Initial level value  # noqa: E741
    # For indexed variables, lo/up/fx/l can be per-instance; v1 stub keeps scalars here.
    # You can expand to maps in Sprint 2/3 if needed:
    lo_map: dict[tuple[str, ...], float] = field(default_factory=dict)
    up_map: dict[tuple[str, ...], float] = field(default_factory=dict)
    fx_map: dict[tuple[str, ...], float] = field(default_factory=dict)
    l_map: dict[tuple[str, ...], float] = field(default_factory=dict)


@dataclass
class EquationHead:
    """Just the header declaration: name + optional domain."""

    name: str
    domain: tuple[str, ...] = ()


@dataclass
class EquationDef:
    name: str
    domain: tuple[str, ...]  # ("i",) etc.
    relation: Rel
    lhs_rhs: tuple  # (lhs_expr, rhs_expr) kept as AST later

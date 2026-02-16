from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ir.ast import Expr


@dataclass
class SourceLocation:
    """Source location information for AST nodes and IR elements."""

    line: int
    column: int
    filename: str | None = None

    def __str__(self) -> str:
        """Format as 'file.gms:line:column' or 'line:column' if no filename."""
        if self.filename:
            return f"{self.filename}:{self.line}:{self.column}"
        return f"{self.line}:{self.column}"


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
    domain: tuple[
        str, ...
    ] = ()  # Parent set(s) for subsets, e.g., cg(genchar) has domain=('genchar',)


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
    expressions: list[tuple[tuple[str, ...], Expr]] = field(
        default_factory=list
    )  # Sprint 10 Day 4: Store function calls/computed assignments as ordered list
    # Issue #741: Changed from dict to list to preserve sequential assignment order
    # for multi-step calibration patterns like:
    #   deltaq(sc) = f(x.l, m.l, ...)     <- Step 1
    #   deltaq(sc) = deltaq(sc)/(1+deltaq(sc))  <- Step 2 (same key)


@dataclass
class VariableDef:
    name: str
    domain: tuple[str, ...] = ()  # e.g., ("i","j")
    kind: VarKind = VarKind.CONTINUOUS
    lo: float | None = None  # None = -inf if unspecified
    up: float | None = None  # None = +inf if unspecified
    fx: float | None = None  # fixed value overrides lo/up
    l: float | None = None  # Initial level value  # noqa: E741
    m: float | None = None  # Marginal/dual value  # noqa: E741
    # For indexed variables, lo/up/fx/l/m can be per-instance; v1 stub keeps scalars here.
    # You can expand to maps in Sprint 2/3 if needed:
    lo_map: dict[tuple[str, ...], float] = field(default_factory=dict)
    up_map: dict[tuple[str, ...], float] = field(default_factory=dict)
    fx_map: dict[tuple[str, ...], float] = field(default_factory=dict)
    l_map: dict[tuple[str, ...], float] = field(default_factory=dict)
    m_map: dict[tuple[str, ...], float] = field(default_factory=dict)


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
    condition: object | None = None  # Optional condition expression (Expr) for $ operator filtering
    source_location: SourceLocation | None = None  # Source location of equation definition


@dataclass
class OptionStatement:
    """Represents a GAMS option statement.

    Sprint 8: Mock/store approach - options are parsed and stored but not processed.

    Examples:
        option limrow = 0;
        option limrow = 0, limcol = 0;
        option decimals = 8;
        option solprint = off;
        option arep:6:3:1;

    Attributes:
        options: List of (name, value) tuples where:
            - name is the option name (e.g., "limrow", "decimals", "arep")
            - value is None for flags, int for numbers, str for "on"/"off",
              or list[int] for format options (e.g., arep:6:3:1 -> [6, 3, 1])
        location: Source location of the option statement
    """

    options: list[tuple[str, int | str | list[int] | None]]
    location: SourceLocation | None


@dataclass
class ConditionalStatement:
    """Represents a GAMS if-elseif-else statement.

    Sprint 8 Day 2: Mock/store approach - conditionals are parsed and stored but not executed.

    Examples:
        if(abs(x.l - 5) < tol,
           display 'case 1';
        elseif abs(x.l - 10) < tol,
           display 'case 2';
        else
           display 'default';
        );

    Attributes:
        condition: The if condition expression (stored as raw tree)
        then_stmts: List of statements in the if block (stored as raw trees)
        elseif_clauses: List of (condition, statements) for each elseif
        else_stmts: List of statements in the else block, or None
        location: Source location of the if statement
    """

    condition: object  # Condition expression (Tree)
    then_stmts: list[object]  # Then block statements (Trees)
    elseif_clauses: list[tuple[object, list[object]]]  # (condition, statements) pairs
    else_stmts: list[object] | None  # Else block statements or None
    location: SourceLocation | None


@dataclass
class LoopStatement:
    """Represents a GAMS loop statement.

    Sprint 11 Day 2 Extended: Mock/store approach - loops are parsed and stored but not executed.

    Examples:
        loop((n,d),
           p = round(mod(p,10)) + 1;
           point.l(n,d) = p/10;
        );

    Attributes:
        indices: Tuple of index variable names (e.g., ('n', 'd'))
        body_stmts: List of statements in the loop body (stored as raw trees)
        location: Source location of the loop statement
    """

    indices: tuple[str, ...]  # Loop index variables
    body_stmts: list[object]  # Loop body statements (Trees)
    location: SourceLocation | None


@dataclass
class SetAssignment:
    """Represents a GAMS dynamic set assignment statement.

    Sprint 18 Day 3: Stores set assignments that populate subsets at runtime.

    Examples:
        ku(k) = yes$(ord(k) < card(k));
        ki(k) = yes$(ord(k) = 1);
        kt(k) = not ku(k);
        low(n,nn) = ord(n) > ord(nn);

    These assignments define subset membership dynamically and must be
    emitted in the generated GAMS file for proper execution.

    Attributes:
        set_name: Name of the set being assigned to
        indices: Tuple of index variable names (e.g., ('k',) or ('n', 'nn'))
        expr: The parsed expression for the RHS (Expr AST node)
        location: Source location of the assignment
    """

    set_name: str
    indices: tuple[str, ...]
    expr: Expr  # The parsed expression for the RHS
    location: SourceLocation | None

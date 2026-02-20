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
    """Reference to a variable; indices are symbolic (strings or IndexOffset).

    The optional ``attribute`` field captures GAMS variable attribute access
    (e.g., ``.l``, ``.m``, ``.lo``, ``.up``).  When non-empty the emitter
    renders ``name.attribute(indices)`` instead of ``name(indices)``.

    Issue #741: Preserving the attribute allows calibration assignments that
    reference ``.l`` values to be emitted as valid GAMS syntax rather than
    being dropped by the parser's variable-reference filter.
    """

    name: str
    indices: tuple[str | IndexOffset, ...] = ()
    attribute: str = ""  # e.g. "l", "m", "lo", "up"; empty means bare variable ref

    def indices_as_strings(self) -> tuple[str, ...]:
        """Convert indices to strings, including IndexOffset in GAMS syntax."""
        result = []
        for idx in self.indices:
            if isinstance(idx, IndexOffset):
                result.append(idx.to_gams_string())
            else:
                result.append(idx)
        return tuple(result)

    def __repr__(self) -> str:
        idx = ",".join(str(i) if isinstance(i, IndexOffset) else i for i in self.indices)
        attr = f".{self.attribute}" if self.attribute else ""
        base = f"{self.name}{attr}"
        return f"VarRef({base}({idx}))" if idx else f"VarRef({base})"


@dataclass(frozen=True)
class ParamRef(Expr):
    """Reference to a parameter; indices symbolic (strings or IndexOffset)."""

    name: str
    indices: tuple[str | IndexOffset, ...] = ()

    def indices_as_strings(self) -> tuple[str, ...]:
        """Convert indices to strings, including IndexOffset in GAMS syntax."""
        result = []
        for idx in self.indices:
            if isinstance(idx, IndexOffset):
                result.append(idx.to_gams_string())
            else:
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
        """Convert indices to strings, including IndexOffset in GAMS syntax."""
        result = []
        for idx in self.indices:
            if isinstance(idx, IndexOffset):
                result.append(idx.to_gams_string())
            else:
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
        """Convert indices to strings, including IndexOffset in GAMS syntax."""
        result = []
        for idx in self.indices:
            if isinstance(idx, IndexOffset):
                result.append(idx.to_gams_string())
            else:
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
    """sum(i,j, body) or sum(i$cond, body) — indices are symbolic set names.

    The optional condition field stores the dollar-filter expression.
    For sum, folding the condition as multiplication (sum(i, cond*body)) is
    mathematically equivalent, but the condition is preserved for fidelity.
    """

    index_sets: tuple[str, ...]
    body: Expr
    condition: Expr | None = None

    def children(self) -> Iterable[Expr]:
        if self.condition is not None:
            yield self.condition
        yield self.body

    def __repr__(self) -> str:
        idx = ",".join(self.index_sets)
        if self.condition is not None:
            return f"Sum(({idx})${self.condition!r}, {self.body!r})"
        return f"Sum(({idx}), {self.body!r})"


@dataclass(frozen=True)
class Prod(Expr):
    """prod(i,j, body) or prod(i$cond, body) — product over indices.

    Sprint 17 Day 6: Added for GAMS prod() aggregation function support.

    The optional condition field stores the dollar-filter expression.
    For prod, this MUST be stored separately (not folded as multiplication)
    because prod(i$cond, body) excludes filtered elements (contributing 1),
    while prod(i, cond*body) would contribute 0 and zero the entire product.
    """

    index_sets: tuple[str, ...]  # Symbolic set names to iterate over (e.g., ("i", "j"))
    body: Expr
    condition: Expr | None = None

    def children(self) -> Iterable[Expr]:
        if self.condition is not None:
            yield self.condition
        yield self.body

    def __repr__(self) -> str:
        idx = ",".join(self.index_sets)
        if self.condition is not None:
            return f"Prod(({idx})${self.condition!r}, {self.body!r})"
        return f"Prod(({idx}), {self.body!r})"


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
class SetMembershipTest(Expr):
    """Set membership test: set_name(indices).

    In GAMS, when a set name is used with indices in a conditional context
    (e.g., rn(n) in s(n)$rn(n)), it tests whether the index combination
    is a member of that set. Returns 1 if true, 0 if false.

    This is distinct from Call nodes which represent function invocations.
    """

    set_name: str
    indices: tuple[Expr, ...]

    def children(self) -> Iterable[Expr]:
        yield from self.indices

    def __repr__(self) -> str:
        idx = ", ".join(repr(i) for i in self.indices)
        return f"SetMembershipTest({self.set_name}, ({idx}))"


@dataclass(frozen=True)
class DollarConditional(Expr):
    """Dollar conditional operator: expr$condition

    Evaluates to expr if condition is non-zero (true), otherwise 0.

    Examples:
        x$y            → DollarConditional(value_expr=VarRef('x'), condition=VarRef('y'))
        (e - m)$t      → DollarConditional(value_expr=Binary('-', ...), condition=VarRef('t'))
        s(n)$rn(n)     → DollarConditional(value_expr=VarRef('s', ('n',)), condition=ParamRef('rn', ('n',)))

    Attributes:
        value_expr: The expression to evaluate if condition is true
        condition: The condition expression (non-zero = true)
    """

    value_expr: Expr
    condition: Expr

    def children(self) -> Iterable[Expr]:
        yield self.value_expr
        yield self.condition

    def __repr__(self) -> str:
        return f"DollarConditional({self.value_expr!r}${self.condition!r})"


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

    def _offset_expr_to_string(self, expr: Expr) -> str:
        """Convert an offset expression to GAMS string representation.

        This is a simplified version of expr_to_gams for offset expressions only.
        Handles Call, Binary, Unary, Const, and SymbolRef nodes.

        Args:
            expr: Offset expression to convert

        Returns:
            GAMS-formatted string representation
        """
        if isinstance(expr, Const):
            return str(int(expr.value)) if float(expr.value).is_integer() else str(expr.value)
        elif isinstance(expr, SymbolRef):
            return expr.name
        elif isinstance(expr, Call):
            args_str = ",".join(self._offset_expr_to_string(arg) for arg in expr.args)
            return f"{expr.func}({args_str})"
        elif isinstance(expr, Unary):
            child_str = self._offset_expr_to_string(expr.child)
            # For unary minus, if child is complex, wrap in parens
            if expr.op == "-":
                if isinstance(expr.child, (Binary, Call)):
                    return f"-({child_str})"
                else:
                    return f"-{child_str}"
            return f"{expr.op}{child_str}"
        elif isinstance(expr, Binary):
            left_str = self._offset_expr_to_string(expr.left)
            right_str = self._offset_expr_to_string(expr.right)
            return f"{left_str}{expr.op}{right_str}"
        else:
            # Fallback for any other expression type
            return repr(expr)

    def to_gams_string(self) -> str:
        """Convert IndexOffset to GAMS syntax string.

        Returns:
            GAMS-formatted string like 'i++1', 'i--2', 'i+1', 'i-3', 'i+j', 'i-j', 'i--j'

        Examples:
            IndexOffset('i', Const(1), circular=True)  -> 'i++1'
            IndexOffset('i', Const(-2), circular=True) -> 'i--2'
            IndexOffset('i', Const(1), circular=False) -> 'i+1'
            IndexOffset('i', Const(-3), circular=False) -> 'i-3'
            IndexOffset('i', SymbolRef('j'), circular=False) -> 'i+j'
            IndexOffset('i', Unary('-', SymbolRef('j')), circular=False) -> 'i-j'
            IndexOffset('i', Unary('-', SymbolRef('j')), circular=True) -> 'i--j'
            IndexOffset('i', Unary('-', Call('ord', ...)), circular=False) -> 'i-ord(...)'

        Raises:
            ValueError: If a constant offset is not an integer value.
            NotImplementedError: If the offset expression type is not supported.
        """
        # Serialize the offset expression
        if isinstance(self.offset, Const):
            offset_val = self.offset.value
            # Validate that offset is an integer (GAMS requires integer offsets)
            if not float(offset_val).is_integer():
                raise ValueError(f"IndexOffset requires integer offset, got {offset_val}")
            if self.circular:
                # Circular: use ++ for positive, -- for negative
                if offset_val >= 0:
                    return f"{self.base}++{int(offset_val)}"
                else:
                    return f"{self.base}--{int(abs(offset_val))}"
            else:
                # Linear: use + for positive, - for negative
                if offset_val >= 0:
                    return f"{self.base}+{int(offset_val)}"
                else:
                    return f"{self.base}{int(offset_val)}"  # Already has minus sign
        elif isinstance(self.offset, SymbolRef):
            # Symbolic offset like i+j (lead)
            if self.circular:
                return f"{self.base}++{self.offset.name}"
            else:
                return f"{self.base}+{self.offset.name}"
        elif isinstance(self.offset, Unary) and self.offset.op == "-":
            # Handle unary minus offsets produced by parser for lag operators
            # e.g., Unary("-", SymbolRef("j")) for i-j or i--j
            inner = self.offset.child
            if isinstance(inner, SymbolRef):
                # Symbolic lag: i-j or i--j
                if self.circular:
                    return f"{self.base}--{inner.name}"
                else:
                    return f"{self.base}-{inner.name}"
            elif isinstance(inner, Const):
                # Unary minus on constant: treat as negated constant
                offset_val = -inner.value
                if not float(offset_val).is_integer():
                    raise ValueError(f"IndexOffset requires integer offset, got {offset_val}")
                if self.circular:
                    if offset_val >= 0:
                        return f"{self.base}++{int(offset_val)}"
                    else:
                        return f"{self.base}--{int(abs(offset_val))}"
                else:
                    if offset_val >= 0:
                        return f"{self.base}+{int(offset_val)}"
                    else:
                        return f"{self.base}{int(offset_val)}"
            elif isinstance(inner, (Call, Binary)):
                # Sprint 20 Day 3: Handle Unary("-", Call(...)) and Unary("-", Binary(...)) patterns
                # e.g., sparta: t-(ord(l)-1) → Unary("-", Binary("-", Call("ord", ...), Const(1)))
                # e.g., tabora: t-ord(a) → Unary("-", Call("ord", ...))
                # Circular not supported for complex expressions
                if self.circular:
                    raise NotImplementedError(
                        f"Circular lead/lag with complex operand not supported: {inner}"
                    )
                inner_str = self._offset_expr_to_string(inner)
                # Wrap in parens if it's a Binary to preserve precedence
                if isinstance(inner, Binary):
                    return f"{self.base}-({inner_str})"
                else:
                    return f"{self.base}-{inner_str}"
            else:
                raise NotImplementedError(
                    f"Unary minus with complex operand not supported: {inner}"
                )
        elif isinstance(self.offset, Binary):
            # Sprint 20 Day 3: Handle Binary(op, ...) pattern
            # e.g., otpop: t+(card(t)-ord(t)) → Binary("-", Call("card",...), Call("ord",...))
            # Circular not supported for complex binary expressions
            if self.circular:
                raise NotImplementedError(
                    f"Circular lead/lag with Binary offset not supported: {self.offset}"
                )
            offset_str = self._offset_expr_to_string(self.offset)
            # Wrap complex offset in parentheses for clarity
            return f"{self.base}+({offset_str})"
        elif isinstance(self.offset, Call):
            # Sprint 20 Day 3: Handle Call(...) pattern (direct call without unary minus)
            # e.g., t+ord(i)
            if self.circular:
                raise NotImplementedError(
                    f"Circular lead/lag with Call offset not supported: {self.offset}"
                )
            offset_str = self._offset_expr_to_string(self.offset)
            return f"{self.base}+{offset_str}"
        else:
            # Complex expression - not supported
            raise NotImplementedError(
                f"Complex offset expressions not yet supported: {self.offset}"
            )


@dataclass(frozen=True)
class SubsetIndex(Expr):
    """
    Subset indexing for variable bounds (Sprint 12 - Issue #455).

    When a variable is indexed with a subset that filters indices, e.g.:
        f.lo(aij(as,i,j)) = 0
    where f(a,i,j) is a 3D variable and aij(a,i,j) is a subset.

    The subset reference provides all the indices needed to match the variable's domain.
    The inner indices (as,i,j) may further filter which elements are affected.

    Examples:
        aij(as,i,j)  → SubsetIndex(subset_name='aij', indices=('as', 'i', 'j'))
        low(n,nn)    → SubsetIndex(subset_name='low', indices=('n', 'nn'))

    Attributes:
        subset_name: Name of the subset being referenced (e.g., 'aij', 'low')
        indices: The indices within the subset reference (e.g., ('as', 'i', 'j'))
    """

    subset_name: str
    indices: tuple[str, ...]

    def children(self) -> Iterable[Expr]:
        return []

    def __repr__(self) -> str:
        idx = ",".join(self.indices)
        return f"SubsetIndex({self.subset_name}({idx}))"


@dataclass(frozen=True)
class CompileTimeConstant(Expr):
    """
    GAMS compile-time constant using %...% syntax.

    Examples:
        %solveStat.capabilityProblems%  → CompileTimeConstant(path=('solveStat', 'capabilityProblems'))
        %system.date%                   → CompileTimeConstant(path=('system', 'date'))
        %myvar%                         → CompileTimeConstant(path=('myvar',))

    Attributes:
        path: Tuple of identifiers forming the dotted path (e.g., ('solveStat', 'capabilityProblems'))
    """

    path: tuple[str, ...]

    def children(self) -> Iterable[Expr]:
        return []

    def __repr__(self) -> str:
        dotted = ".".join(self.path)
        return f"CompileTimeConstant(%{dotted}%)"

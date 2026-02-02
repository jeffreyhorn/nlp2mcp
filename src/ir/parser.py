"""Parser utilities that turn the grammar output into ModelIR structures."""

from __future__ import annotations

import math
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from functools import lru_cache
from itertools import product
from pathlib import Path

from lark import Lark, Token, Tree
from lark.exceptions import UnexpectedCharacters, UnexpectedEOF, UnexpectedToken

from ..utils.error_enhancer import ErrorEnhancer
from ..utils.errors import ParseError
from .ast import (
    Binary,
    Call,
    Const,
    DollarConditional,
    EquationRef,
    Expr,
    IndexOffset,
    MultiplierRef,
    ParamRef,
    Prod,
    SetMembershipTest,
    SubsetIndex,
    Sum,
    SymbolRef,
    Unary,
    VarRef,
)
from .model_ir import ModelIR, ObjectiveIR
from .preprocessor import normalize_double_commas, preprocess_gams_file
from .symbols import (
    AliasDef,
    ConditionalStatement,
    EquationDef,
    LoopStatement,
    ObjSense,
    OptionStatement,
    ParameterDef,
    Rel,
    SetDef,
    SourceLocation,
    VariableDef,
    VarKind,
)


class ParserSemanticError(ValueError):
    """Raised when parsed input violates semantic assumptions."""

    def __init__(self, message: str, line: int | None = None, column: int | None = None):
        super().__init__(message)
        self.line = line
        self.column = column

    def __str__(self) -> str:
        base = super().__str__()
        if self.line is not None and self.column is not None:
            return f"{base} (line {self.line}, column {self.column})"
        if self.line is not None:
            return f"{base} (line {self.line})"
        return base


_ROOT = Path(__file__).resolve().parents[1]
_GRAMMAR_PATH = _ROOT / "gams" / "gams_grammar.lark"

_WRAPPER_NODES = {
    "sum_expr",
    "or_expr",
    "and_expr",
    "comp_expr",
    "arith_expr",
    "term",
    "factor",
    "power",
}

_REL_MAP = {
    "=e=": Rel.EQ,
    "=l=": Rel.LE,
    "=g=": Rel.GE,
}

_VAR_KIND_MAP = {
    "POSITIVE_K": VarKind.POSITIVE,
    "NEGATIVE_K": VarKind.NEGATIVE,
    "BINARY_K": VarKind.BINARY,
    "INTEGER_K": VarKind.INTEGER,
}

# Aggregation functions that bind a set iterator as first argument (Sprint 10 Day 6)
_AGGREGATION_FUNCTIONS = {"smin", "smax", "sum", "prod", "card"}

_FUNCTION_NAMES = {"abs", "exp", "log", "log10", "log2", "sqrt", "sin", "cos", "tan", "sqr"}

# GAMS predefined constants (case-insensitive)
# These are automatically available in all GAMS models
# Note: This is the single source of truth for predefined constant values.
# The _init_predefined_constants() method uses this dictionary to create
# scalar parameters, and _make_symbol() checks this for constant references.
_PREDEFINED_CONSTANTS: dict[str, float] = {
    "yes": 1.0,  # Boolean true
    "no": 0.0,  # Boolean false
    "pi": math.pi,  # 3.141592653589793
    "inf": math.inf,  # Positive infinity
    "eps": sys.float_info.epsilon,  # Machine epsilon (2.220446049250313e-16)
    "na": math.nan,  # Not available marker (represented as NaN)
    "undf": math.nan,  # Undefined value marker (represented as NaN)
}


@lru_cache
def _build_lark() -> Lark:
    """Load the shared Lark parser (cached for reuse across tests).

    Note: Using standard lexer (not dynamic_complete) to avoid tokenization issues
    where multi-character identifiers are split into individual characters.
    """
    return Lark.open(
        _GRAMMAR_PATH,
        parser="earley",
        start="start",
        maybe_placeholders=False,
        ambiguity="resolve",
    )


def _resolve_ambiguities(node: Tree | Token) -> Tree | Token:
    """Collapse Earley ambiguity nodes by picking the first alternative.

    With ambiguity="resolve" in the parser, ambiguity nodes are rare, but this
    function handles any that do appear by consistently picking the first alternative.
    This avoids exponential blowup in pathological grammar cases.

    Uses iterative approach with explicit stack to avoid Python recursion limits
    for large parse trees (e.g., models with 1000+ variables).

    Memory note: The resolved dictionary uses id() for memoization, holding references
    to all processed nodes until completion. For extremely large models (10,000+ nodes),
    this consumes O(n) memory proportional to parse tree size. This is necessary for
    correctness as child nodes must remain accessible while building parent nodes.
    The dictionary is freed when the function returns.
    """
    if isinstance(node, Token):
        return node

    # Dictionary to memoize resolved nodes by their id
    # Memory trade-off: Holds references to all nodes during traversal
    resolved = {}

    # Stack for post-order traversal: (node, is_return_visit)
    stack = [(node, False)]

    while stack:
        current, is_return = stack.pop()

        if isinstance(current, Token):
            resolved[id(current)] = current
            continue

        if is_return:
            # Returning from children: construct resolved node
            if current.data == "_ambig":
                if not current.children:
                    resolved[id(current)] = current
                else:
                    # Pick first alternative
                    resolved[id(current)] = resolved[id(current.children[0])]
            else:
                # Reconstruct tree with resolved children
                resolved_children = [resolved[id(child)] for child in current.children]
                resolved[id(current)] = Tree(current.data, resolved_children)
        else:
            # First visit: schedule return visit and process children
            stack.append((current, True))

            # Push children to stack
            if current.data == "_ambig" and current.children:
                # Only process first child for ambiguity nodes
                stack.append((current.children[0], False))
            else:
                # Process all children in reverse order (for left-to-right processing)
                for child in reversed(current.children):
                    stack.append((child, False))

    return resolved[id(node)]


# Module-level ErrorEnhancer instance (stateless, can be reused)
_ERROR_ENHANCER = ErrorEnhancer()


def _extract_source_line_with_adjusted_column(
    source: str, line: int | None, column: int | None
) -> tuple[str | None, int | None]:
    """Extract source line and adjust column for whitespace stripping.

    Args:
        source: Full source text
        line: Line number (1-indexed)
        column: Column number (1-indexed)

    Returns:
        Tuple of (stripped source line, adjusted column number)
    """
    source_lines = source.split("\n")
    source_line = None
    adjusted_column = column

    if line and 1 <= line <= len(source_lines):
        source_line = source_lines[line - 1].lstrip()
        # Adjust column for stripped whitespace
        original_line = source_lines[line - 1]
        stripped_count = len(original_line) - len(original_line.lstrip())
        if column is not None:
            adjusted_column = max(1, column - stripped_count)

    return source_line, adjusted_column


def parse_text(source: str) -> Tree:
    """Parse a source string and return a disambiguated Lark parse tree.

    Args:
        source: GAMS source code to parse

    Returns:
        Disambiguated parse tree

    Raises:
        ParseError: If syntax errors are found (wraps Lark exceptions)
    """
    # Issue #565: Normalize double commas to single commas before parsing.
    # This handles GAMS visual alignment syntax like: Set l / a,, b /;.
    # NOTE: The same normalization is also performed in `preprocess_gams_file()`.
    # It is intentionally duplicated here so that callers which invoke `parse_text`
    # directly on raw GAMS source (bypassing preprocessing) still get correct
    # handling of visual-alignment double commas.
    source = normalize_double_commas(source)

    parser = _build_lark()
    try:
        raw = parser.parse(source)
        return _resolve_ambiguities(raw)
    except UnexpectedToken as e:
        # Extract source line and adjust column
        source_line, column = _extract_source_line_with_adjusted_column(source, e.line, e.column)

        # Format expected tokens
        expected = getattr(e, "expected", None)
        if expected:
            expected_str = ", ".join(sorted(expected))
            message = f"Unexpected token '{e.token}'. Expected one of: {expected_str}"
        else:
            message = f"Unexpected token: {e.token}"

        error = ParseError(
            message=message,
            line=e.line,
            column=column,
            source_line=source_line,
            suggestion="Check syntax near this location",
        )
        # Enhance error with contextual suggestions
        enhanced_error = _ERROR_ENHANCER.enhance(error, source)
        raise enhanced_error from e

    except UnexpectedCharacters as e:
        # Extract source line and adjust column
        source_line, column = _extract_source_line_with_adjusted_column(source, e.line, e.column)

        # Get the unexpected character
        char = getattr(e, "char", None)
        if char:
            message = f"Unexpected character: '{char}'"
        else:
            message = "Unexpected character in input"

        error = ParseError(
            message=message,
            line=e.line,
            column=column,
            source_line=source_line,
            suggestion="This character is not valid in this context",
        )
        # Enhance error with contextual suggestions
        enhanced_error = _ERROR_ENHANCER.enhance(error, source)
        raise enhanced_error from e

    except UnexpectedEOF as e:
        # Extract source line (use last line for EOF errors)
        source_lines = source.split("\n")
        last_line = len(source_lines)
        source_line, _ = _extract_source_line_with_adjusted_column(source, last_line, 1)

        # Format expected tokens
        expected = getattr(e, "expected", None)
        if expected:
            expected_str = ", ".join(sorted(expected))
            message = f"Unexpected end of file. Expected one of: {expected_str}"
        else:
            message = "Unexpected end of file"

        error = ParseError(
            message=message,
            line=last_line,
            column=1,
            source_line=source_line,
            suggestion="The file appears to be incomplete. Check for missing semicolons or closing brackets",
        )
        # Enhance error with contextual suggestions
        enhanced_error = _ERROR_ENHANCER.enhance(error, source)
        raise enhanced_error from e


def parse_file(path: str | Path) -> Tree:
    """Parse a GAMS source file and return the parse tree.

    This function preprocesses the file (expanding includes, macros, and
    stripping unsupported directives) before parsing.
    """
    preprocessed = preprocess_gams_file(path)
    return parse_text(preprocessed)


def parse_model_text(source: str) -> ModelIR:
    """Parse a source string into a populated ModelIR instance.

    Note: For large models (1000+ variables), this function requires an increased
    Python recursion limit due to deeply nested expression trees. The CLI automatically
    manages this, but if calling this function directly from other code, ensure
    sys.setrecursionlimit() is set appropriately (recommended: 10000).
    """
    tree = parse_text(source)
    return _ModelBuilder(source=source).build(tree)


def parse_model_file(path: str | Path) -> ModelIR:
    """
    Parse a file path into a populated ModelIR instance.

    This function automatically handles $include directives by preprocessing
    the file before parsing.
    """
    # Preprocess to expand all $include directives
    data = preprocess_gams_file(Path(path))
    return parse_model_text(data)


def _token_text(token: Token) -> str:
    value = str(token)
    if token.type == "STRING" and len(value) >= 2:
        return value[1:-1]
    return value


def _is_string_literal(token: Token) -> bool:
    """Check if a token is a string literal (quoted text) that should be treated as a description."""
    value = str(token)
    # Check if token value starts and ends with matching quotes
    if len(value) >= 2:
        if (value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'"):
            return True
    return False


def _strip_quotes(token: Token) -> str:
    """Strip quotes from ID tokens (e.g., 'i1', \"cost%\" → i1, cost%)."""
    value = str(token)
    if token.type == "ID" and len(value) >= 2:
        if (value[0] == "'" and value[-1] == "'") or (value[0] == '"' and value[-1] == '"'):
            return value[1:-1]
    return value


def _id_list(node: Tree) -> tuple[str, ...]:
    return tuple(_token_text(tok) for tok in node.children if isinstance(tok, Token))


def _id_or_wildcard_list(node: Tree) -> tuple[str, ...]:
    """Extract IDs or wildcards from id_or_wildcard_list.

    Handles the grammar rule:
        id_or_wildcard_list: id_or_wildcard ("," id_or_wildcard)*
        id_or_wildcard: ID | "*"
    """
    result = []
    for child in node.children:
        if isinstance(child, Token):
            result.append(_token_text(child))
        elif isinstance(child, Tree) and child.data == "id_or_wildcard":
            # Extract the token from id_or_wildcard rule
            for token in child.children:
                if isinstance(token, Token):
                    result.append(_token_text(token))
    return tuple(result)


def _domain_list(node: Tree) -> tuple[str, ...]:
    """Extract domain identifiers from domain_list (Sprint 11 Day 1).

    Supports both simple domains and nested/subset indexing.

    Examples:
        - Simple:      i                -> 'i'
        - Nested:      low(n,nn)        -> 'n', 'nn'
        - Mixed:       i, low(n,nn), k  -> 'i', 'n', 'nn', 'k'
        - Lag/Lead:    i+1              -> 'i'  (extract base identifier)

    Returns a flat tuple of all identifier names used in the domain.
    """
    identifiers = []
    for domain_elem in node.children:
        if not isinstance(domain_elem, Tree) or domain_elem.data != "domain_element":
            continue

        # domain_element: ID ("(" index_list ")")?
        #               | ID lag_lead_suffix
        # First child is always the ID
        if domain_elem.children:
            first_child = domain_elem.children[0]
            if isinstance(first_child, Token):
                # Simple domain: just the ID
                if len(domain_elem.children) == 1:
                    identifiers.append(_token_text(first_child))
                # Check second child to determine type
                elif len(domain_elem.children) == 2:
                    second_child = domain_elem.children[1]
                    if isinstance(second_child, Tree):
                        # Lag/lead suffix: ID lag_lead_suffix
                        # Extract just the base identifier (e.g., i+1 -> 'i')
                        if second_child.data in (
                            "linear_lead",
                            "linear_lag",
                            "circular_lead",
                            "circular_lag",
                        ):
                            identifiers.append(_token_text(first_child))
                        # Nested domain with index_list: ID "(" index_list ")"
                        # Extract identifiers from the index_list recursively
                        elif second_child.data == "index_list":
                            identifiers.extend(_extract_domain_indices(second_child))

    return tuple(identifiers)


def _extract_domain_indices(index_list_node: Tree) -> list[str]:
    """Recursively extract base identifiers from index_list for domain tracking.

    Examples:
        - i          -> ['i']
        - i+1        -> ['i']
        - nh(i+1)    -> ['i']
        - i, j+1     -> ['i', 'j']
    """
    identifiers = []
    for child in index_list_node.children:
        if isinstance(child, Token):
            identifiers.append(_token_text(child))
        elif isinstance(child, Tree):
            # index_list contains index_expr nodes, which are transformed to index_simple, index_subset, or index_string
            if child.data == "index_simple":
                # index_simple: ID lag_lead_suffix?
                # First child is the base ID
                if child.children and isinstance(child.children[0], Token):
                    identifiers.append(_token_text(child.children[0]))
            elif child.data == "index_subset":
                # index_subset: ID "(" index_list ")" lag_lead_suffix?
                # Recursively extract from the nested index_list
                for subchild in child.children:
                    if isinstance(subchild, Tree) and subchild.data == "index_list":
                        identifiers.extend(_extract_domain_indices(subchild))
            elif child.data == "index_string":
                # Issue #566: index_string: STRING (quoted index like 'route-1')
                if child.children and isinstance(child.children[0], Token):
                    identifiers.append(_strip_quotes(child.children[0]))
    return identifiers


def _extract_indices(node: Tree) -> tuple[str, ...]:
    """Extract indices from index_list, stripping quotes from escaped identifiers.

    Used for indexed parameter assignments like p('i1') where 'i1' should become i1.

    Sprint 9 Note: Now handles index_expr nodes from index_list grammar.
    Sprint 11 Day 2: Now handles index_simple and index_subset nodes.
    Only supports plain identifiers (no IndexOffset) for parameter assignments.
    """
    indices = []
    for child in node.children:
        if isinstance(child, Token):
            # Old-style direct token (from id_list)
            # Strip quotes from escaped ID tokens (e.g., 'i1', "cost%")
            indices.append(_strip_quotes(child) if child.type == "ID" else _token_text(child))
        elif isinstance(child, Tree) and child.data in (
            "index_expr",
            "index_simple",
            "index_subset",
            "index_string",
        ):
            # Sprint 11 Day 2: Grammar now produces index_simple and index_subset
            # Issue #566: Grammar now also produces index_string for quoted indices
            if child.data == "index_simple":
                # index_simple: ID lag_lead_suffix?
                id_token = child.children[0]
                if len(child.children) > 1:
                    # Has lag/lead suffix - not supported for parameter assignments
                    raise ParserSemanticError(
                        "Lead/lag indexing (i++1, i--1) not supported in parameter assignments"
                    )
                # Strip quotes if present
                indices.append(
                    _strip_quotes(id_token) if id_token.type == "ID" else _token_text(id_token)
                )
            elif child.data == "index_subset":
                # index_subset: ID "(" index_list ")" lag_lead_suffix?
                # Extract the subset name and its domain indices
                # e.g., arc(n,np) -> subset_name='arc', domain_indices=['n', 'np']
                # Find the nested index_list and extract domain indices
                for subchild in child.children:
                    if isinstance(subchild, Tree) and subchild.data == "index_list":
                        domain_indices = _extract_domain_indices(subchild)
                        indices.extend(domain_indices)
                        break
            elif child.data == "index_string":
                # Issue #566: index_string: STRING (quoted index like 'route-1')
                string_token = child.children[0]
                indices.append(_strip_quotes(string_token))
            else:
                # Old index_expr from legacy grammar
                # Only support plain ID (no lag/lead for parameter assignments)
                if len(child.children) == 1:
                    # No lag/lead suffix, just extract the ID
                    id_token = child.children[0]
                    # Strip quotes if present
                    indices.append(
                        _strip_quotes(id_token) if id_token.type == "ID" else _token_text(id_token)
                    )
                else:
                    # Has lag/lead suffix - not supported for parameter assignments
                    raise ParserSemanticError(
                        "Lead/lag indexing (i++1, i--1) not supported in parameter assignments"
                    )
    return tuple(indices)


def _extract_indices_with_subset(node: Tree) -> tuple[tuple[str, ...], str | None]:
    """Extract indices from index_list along with any subset constraint.

    Returns:
        Tuple of (indices, subset_name) where:
        - indices: tuple of domain index names
        - subset_name: name of constraining subset if present, None otherwise

    Example:
        - arc(n,np) -> (('n', 'np'), 'arc')
        - (i, j) -> (('i', 'j'), None)
    """
    indices: list[str] = []
    subset_name: str | None = None

    for child in node.children:
        if isinstance(child, Token):
            indices.append(_strip_quotes(child) if child.type == "ID" else _token_text(child))
        elif isinstance(child, Tree) and child.data in (
            "index_expr",
            "index_simple",
            "index_subset",
            "index_string",
        ):
            if child.data == "index_simple":
                id_token = child.children[0]
                if len(child.children) > 1:
                    raise ParserSemanticError(
                        "Lead/lag indexing (i++1, i--1) not supported in parameter assignments"
                    )
                indices.append(
                    _strip_quotes(id_token) if id_token.type == "ID" else _token_text(id_token)
                )
            elif child.data == "index_subset":
                # index_subset: ID "(" index_list ")" lag_lead_suffix?
                subset_name = _token_text(child.children[0])
                for subchild in child.children:
                    if isinstance(subchild, Tree) and subchild.data == "index_list":
                        domain_indices = _extract_domain_indices(subchild)
                        indices.extend(domain_indices)
                        break
            elif child.data == "index_string":
                # Issue #566: index_string: STRING (quoted index like 'route-1')
                string_token = child.children[0]
                indices.append(_strip_quotes(string_token))
            else:
                if len(child.children) == 1:
                    id_token = child.children[0]
                    indices.append(
                        _strip_quotes(id_token) if id_token.type == "ID" else _token_text(id_token)
                    )
                else:
                    raise ParserSemanticError(
                        "Lead/lag indexing (i++1, i--1) not supported in parameter assignments"
                    )

    return tuple(indices), subset_name


def _process_index_expr(index_node: Tree) -> str | IndexOffset | SubsetIndex:
    """Process a single index_expr from grammar (Sprint 9 Day 3, Sprint 11 Day 2 Extended).

    Returns:
        str: Simple identifier if no lag/lead suffix
        IndexOffset: If lag/lead operator present (i++1, i--2, i+j, etc.)
        SubsetIndex: If subset indexing (aij(as,i,j)) - Sprint 12 Issue #455

    Sprint 12 Issue #455: Support subset indexing (index_subset).
    For subset indexing like low(n,nn), we return a SubsetIndex that preserves
    both the subset name and the inner indices for proper bounds validation.
    """
    # Issue #566: Handle index_string: STRING (quoted index like 'route-1')
    if index_node.data == "index_string":
        string_token = index_node.children[0]
        return _strip_quotes(string_token)

    # Handle index_subset: ID "(" index_list ")" lag_lead_suffix?
    if index_node.data == "index_subset":
        # For subset indexing like aij(as,i,j), return SubsetIndex
        # Child 0: subset name (ID), Child 1: index_list with index_simple nodes
        subset_name = _token_text(index_node.children[0])
        index_list_node = index_node.children[1]

        # Extract string indices from the nested index_list
        # The index_list contains index_simple trees, each with an ID token
        inner_indices: list[str] = []
        for child in index_list_node.children:
            if isinstance(child, Tree):
                if child.data == "index_simple":
                    # index_simple has ID as first child
                    inner_indices.append(_token_text(child.children[0]))
                elif child.data == "index_string":
                    # Issue #566: index_string has STRING as first child
                    inner_indices.append(_strip_quotes(child.children[0]))
                elif child.data == "index_expr":
                    # Recursively process index_expr
                    result = _process_index_expr(child)
                    if isinstance(result, str):
                        inner_indices.append(result)
                    elif isinstance(result, SubsetIndex):
                        raise ParserSemanticError(
                            f"Nested subset indexing is not supported: found nested SubsetIndex in subset index '{subset_name}'"
                        )
                    elif isinstance(result, IndexOffset):
                        raise ParserSemanticError(
                            f"Index offsets are not supported in subset index '{subset_name}'"
                        )
                    else:
                        raise ParserSemanticError(
                            f"Unexpected result type '{type(result).__name__}' in subset index '{subset_name}'"
                        )
                else:
                    raise ParserSemanticError(
                        f"Unexpected node type '{child.data}' in subset index '{subset_name}'"
                    )
            elif isinstance(child, Token):
                # Direct token (fallback)
                inner_indices.append(_token_text(child))

        # Sprint 12 Issue #455: Return SubsetIndex to preserve full information
        # This allows _expand_variable_indices to properly handle bounds like
        # f.lo(aij(as,i,j)) where f(a,i,j) expects 3 indices
        return SubsetIndex(subset_name=subset_name, indices=tuple(inner_indices))

    # Handle index_simple: ID lag_lead_suffix?
    base_token = index_node.children[0]
    base = _token_text(base_token)

    # No suffix? Just return the base identifier
    if len(index_node.children) == 1:
        return base

    # Has lag_lead_suffix
    suffix_node = index_node.children[1]
    offset_node = suffix_node.children[0]  # offset_expr

    # Parse offset expression
    if isinstance(offset_node, Token):
        # Direct token (shouldn't happen with current grammar, but handle it)
        if offset_node.type == "NUMBER":
            offset_expr = Const(float(offset_node))
        else:
            offset_expr = SymbolRef(_token_text(offset_node))
    elif offset_node.data == "offset_number":
        offset_value = float(offset_node.children[0])
        offset_expr = Const(offset_value)
    elif offset_node.data == "offset_variable":
        offset_name = _token_text(offset_node.children[0])
        offset_expr = SymbolRef(offset_name)
    else:
        raise ParserSemanticError(f"Unknown offset_expr type: {offset_node.data}")

    # Determine circular flag and adjust offset for lag operators
    if suffix_node.data == "circular_lead":
        return IndexOffset(base=base, offset=offset_expr, circular=True)
    elif suffix_node.data == "circular_lag":
        # Convert lag to negative offset: i--2 → IndexOffset(base='i', offset=Const(-2))
        if isinstance(offset_expr, Const):
            negated = Const(-offset_expr.value)
        else:
            negated = Unary("-", offset_expr)
        return IndexOffset(base=base, offset=negated, circular=True)
    elif suffix_node.data == "linear_lead":
        return IndexOffset(base=base, offset=offset_expr, circular=False)
    elif suffix_node.data == "linear_lag":
        # Convert lag to negative offset: i-2 → IndexOffset(base='i', offset=Const(-2))
        if isinstance(offset_expr, Const):
            negated = Const(-offset_expr.value)
        else:
            negated = Unary("-", offset_expr)
        return IndexOffset(base=base, offset=negated, circular=False)
    else:
        raise ParserSemanticError(f"Unknown lag_lead_suffix type: {suffix_node.data}")


def _process_index_list(node: Tree) -> tuple[str | IndexOffset | SubsetIndex, ...]:
    """Process index_list from grammar (Sprint 9 Day 3, Sprint 12 Issue #455).

    Handles plain identifiers, lag/lead indexed expressions, and subset indexing.

    Returns tuple of str (plain ID), IndexOffset, or SubsetIndex objects.
    """
    indices = []
    for child in node.children:
        if isinstance(child, Token):
            # Old-style: direct ID token (from id_list in declarations)
            indices.append(_token_text(child))
        elif isinstance(child, Tree) and child.data in (
            "index_expr",
            "index_simple",
            "index_subset",
            "index_string",
        ):
            # New-style: index_expr tree (from index_list in references)
            # Sprint 11 Day 2: Grammar now produces index_simple and index_subset
            # Issue #566: Grammar now also produces index_string for quoted indices
            indices.append(_process_index_expr(child))
        else:
            # Fallback for unknown nodes
            raise ParserSemanticError(f"Unknown index_list child: {child}")
    return tuple(indices)


@dataclass
class _ModelBuilder:
    """Walks the parse tree and instantiates ModelIR components."""

    model: ModelIR = field(default_factory=ModelIR)
    source: str = ""  # Source text for error reporting
    _equation_domains: dict[str, tuple[str, ...]] = None
    _context_stack: list[tuple[str, Tree | Token | None, tuple[str, ...]]] = field(
        default_factory=list
    )
    _declared_equations: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if self._equation_domains is None:
            self._equation_domains = {}
        # Initialize predefined GAMS constants
        self._init_predefined_constants()

    def _init_predefined_constants(self) -> None:
        """Initialize predefined GAMS constants as scalar parameters.

        Uses _PREDEFINED_CONSTANTS as the single source of truth for values.
        Creates scalar parameters for constants that can be used in expressions
        (pi, inf, eps, na). Boolean constants (yes, no) and undf are handled
        directly in _make_symbol() without creating parameters.
        """
        # Constants that should be available as scalar parameters
        # (not yes/no/undf which are handled as literals in _make_symbol)
        param_constants = {"pi", "inf", "eps", "na"}

        for name in param_constants:
            value = _PREDEFINED_CONSTANTS[name]
            # Create a scalar parameter (no domain)
            param_def = ParameterDef(name=name, domain=(), values={(): value})
            self.model.params[name] = param_def

    def build(self, tree: Tree) -> ModelIR:
        for child in tree.children:
            if not isinstance(child, Tree):
                continue
            handler = getattr(self, f"_handle_{child.data}", None)
            if handler:
                handler(child)
        self._validate()
        return self.model

    def _handle_sets_block(self, node: Tree) -> None:
        # Sprint 12 Day 5 (Issue #417): Process set declarations (allows space and newline separation)
        for child in node.children:
            if not isinstance(child, Tree):
                continue
            # Route all set declarations through _process_set_decl
            self._process_set_decl(child)

    def _process_set_decl(self, child: Tree) -> None:
        """Process a single set_decl node (helper for _handle_sets_block)."""
        # Sprint 12 Day 5 (Issue #417): Handle new set_single and set_list patterns
        if child.data == "set_list":
            # Handle comma-separated list: Set i, j, k;
            for set_item in child.children:
                if isinstance(set_item, Tree):
                    self._process_set_item(set_item)
        elif child.data == "set_single":
            # Handle single set declaration with potential description
            set_single_item = child.children[0]
            self._process_set_item(set_single_item)
        else:
            # Legacy patterns - delegate to _process_set_item
            self._process_set_item(child)

    def _process_set_item(self, item: Tree) -> None:
        """Process a single set_item or set_single_item node."""
        if item.data == "set_simple":
            name = _token_text(item.children[0])
            # Skip optional STRING/desc_text description, find set_members node
            members_node = next(
                c for c in item.children if isinstance(c, Tree) and c.data == "set_members"
            )
            members = self._expand_set_members(members_node)
            self.model.add_set(SetDef(name=name, members=members))
        elif item.data == "set_empty":
            name = _token_text(item.children[0])
            # Note: desc_text is now allowed but we ignore it (no description field in SetDef yet)
            self.model.add_set(SetDef(name=name))
        elif item.data == "set_domain":
            # Subset without explicit members: cg(genchar)
            # Sprint 17 Day 5: Store domain (parent set) for subset relationships
            name = _token_text(item.children[0])
            domain = tuple(_id_list(item.children[1]))
            # Note: desc_text is now allowed but we ignore it
            # A set with domain but no members is a subset declaration (members inherited from parent)
            self.model.add_set(SetDef(name=name, members=[], domain=domain))
        elif item.data == "set_domain_with_members":
            # Subset with explicit members: cg(genchar) / a, b, c /
            # Sprint 17 Day 5: Store domain (parent set) for subset relationships
            name = _token_text(item.children[0])
            # Extract domain from id_list (the parent set(s))
            domain = tuple(_id_list(item.children[1]))
            members_node = next(
                c for c in item.children if isinstance(c, Tree) and c.data == "set_members"
            )
            members = self._expand_set_members(members_node)
            self.model.add_set(SetDef(name=name, members=members, domain=domain))
        elif item.data == "set_aliased":
            # Set with alias: ID STRING? alias_opt / set_members /
            name = _token_text(item.children[0])
            members_node = next(
                c for c in item.children if isinstance(c, Tree) and c.data == "set_members"
            )
            members = self._expand_set_members(members_node)
            self.model.add_set(SetDef(name=name, members=members))

    def _expand_set_members(self, members_node: Tree) -> list[str]:
        """Expand set members, handling range notation (e.g., i1*i100 or 1*10)."""
        result = []
        for child in members_node.children:
            if isinstance(child, Token):
                # Direct token - this indicates the grammar produced an unexpected token
                # instead of wrapping it in a set_element node
                raise self._error(
                    f"Unexpected direct token in set members: {child!r}. "
                    f"Expected set_element or set_range node from grammar.",
                    child,
                )
            elif isinstance(child, Tree):
                if child.data == "set_element":
                    # Simple element: ID or STRING
                    result.append(_token_text(child.children[0]))
                elif child.data == "set_element_with_desc":
                    # Element with inline description: SET_ELEMENT_ID STRING or STRING STRING
                    # Take first token, ignore description (second token)
                    # Sprint 16 Day 7: Handle STRING STRING case (preprocessor quotes hyphenated IDs)
                    # Note: _token_text() already strips quotes from STRING tokens
                    result.append(_token_text(child.children[0]))
                elif child.data == "set_tuple":
                    # Issue #567: Tuple notation with optional quoted parts
                    # ID.ID, ID.STRING, STRING.ID, STRING.STRING
                    # e.g., a.b, upper.'u-egypt', 'a'.b, 'a'.'b'
                    prefix = _token_text(child.children[0])
                    suffix = _token_text(child.children[1])
                    result.append(f"{prefix}.{suffix}")
                elif child.data == "set_tuple_with_desc":
                    # Issue #567: Tuple with description - all quote combinations
                    # ID.ID STRING, ID.STRING STRING, STRING.ID STRING, STRING.STRING STRING
                    # e.g., a.b "desc", upper.'u-egypt' "desc"
                    prefix = _token_text(child.children[0])
                    suffix = _token_text(child.children[1])
                    # Ignore description (third child)
                    result.append(f"{prefix}.{suffix}")
                elif child.data == "set_tuple_expansion":
                    # Issue #568: Tuple expansion with optional quoted prefix/suffixes
                    # ID.(id1,id2,...) or STRING.(id1,id2,...) or ID.('s-1','s-2',...)
                    # e.g., nw.(w,cc,n) or 'c-cracker'.('ho-low-s','ho-high-s')
                    prefix = _token_text(child.children[0])
                    # Second child is set_element_id_list node (handles both ID and STRING)
                    id_list_node = child.children[1]
                    suffixes = self._parse_set_element_id_list(id_list_node)
                    for suffix in suffixes:
                        result.append(f"{prefix}.{suffix}")
                elif child.data == "set_tuple_prefix_expansion":
                    # Issue #562: Tuple prefix expansion: (id1,id2).suffix (e.g., (jan,feb).wet)
                    # Expands to: jan.wet, feb.wet
                    # First child is set_element_id_list, second child is the suffix token
                    prefixes = self._parse_set_element_id_list(child.children[0])
                    suffix = _token_text(child.children[1])
                    for prefix in prefixes:
                        result.append(f"{prefix}.{suffix}")
                elif child.data == "set_range":
                    # Range notation: can be symbolic (i1*i100) or numeric (1*10)
                    # The grammar now produces range_expr with range_bound children
                    range_expr = child.children[0]  # Get the range_expr node
                    if not isinstance(range_expr, Tree) or range_expr.data != "range_expr":
                        raise self._error(
                            f"Expected range_expr node in set_range, got {range_expr}",
                            child,
                        )

                    # Extract the two range bounds (skipping the * operator token)
                    bounds = [
                        node.children[0]
                        for node in range_expr.children
                        if isinstance(node, Tree) and node.data == "range_bound"
                    ]

                    if len(bounds) != 2:
                        raise self._error(
                            f"Range notation requires exactly two bounds, got {len(bounds)}",
                            child,
                        )

                    start_bound = _token_text(bounds[0])
                    end_bound = _token_text(bounds[1])

                    expanded = self._expand_range(start_bound, end_bound, child)
                    result.extend(expanded)
                else:
                    raise self._error(
                        f"Unexpected set member node type: '{child.data}'. "
                        f"Expected 'set_element', 'set_element_with_desc', 'set_tuple', "
                        f"'set_tuple_with_desc', 'set_tuple_expansion', 'set_tuple_prefix_expansion', or 'set_range'.",
                        child,
                    )
        return result

    def _expand_range(self, start_bound: str, end_bound: str, node: Tree) -> list[str]:
        """Expand a range into a list of elements.

        Supports multiple range types:
        1. Numeric ranges: 1*10 -> ['1', '2', '3', ..., '10']
        2. Symbolic ranges: i1*i100 -> ['i1', 'i2', ..., 'i100']
        3. Pure alphabetic ranges: a*d -> ['a', 'b', 'c', 'd']
        4. Hyphenated ranges: route-1*route-5 -> ['route-1', 'route-2', ..., 'route-5']

        Args:
            start_bound: Start of range (either a number or identifier with number)
            end_bound: End of range (either a number or identifier with number)
            node: Parse tree node for error reporting

        Returns:
            List of expanded range elements as strings

        Note:
            Callers should use _token_text() before passing bounds to this method,
            which already strips quotes from STRING tokens.
        """
        # Check if this is a pure numeric range (e.g., 1*10)
        try:
            num_start = int(start_bound)
            num_end = int(end_bound)

            # Validate range direction
            if num_start > num_end:
                raise self._error(
                    f"Invalid range: start {num_start} is greater than end {num_end}", node
                )

            # Generate numeric range
            return [str(i) for i in range(num_start, num_end + 1)]

        except ValueError:
            # Not a pure numeric range, try other patterns
            pass

        # Sprint 16 Day 7: Check for pure single-letter alphabetic range (e.g., a*d)
        if len(start_bound) == 1 and len(end_bound) == 1:
            if start_bound.isalpha() and end_bound.isalpha():
                start_ord = ord(start_bound.lower())
                end_ord = ord(end_bound.lower())
                if start_ord > end_ord:
                    raise self._error(
                        f"Invalid range: '{start_bound}' comes after '{end_bound}'", node
                    )
                # Preserve case of start bound
                if start_bound.isupper():
                    return [chr(i).upper() for i in range(start_ord, end_ord + 1)]
                else:
                    return [chr(i) for i in range(start_ord, end_ord + 1)]

        # Parse symbolic range: identifier followed by number
        # Sprint 16 Day 7: Extended pattern to support hyphenated identifiers like route-1
        # Pattern matches: prefix (letters, digits, underscores, hyphens) followed by trailing number
        # Examples: i1, route-1, data-set-2, item_3, item2-1 (digit before hyphen is allowed)
        # The pattern uses non-greedy matching (*?) for the prefix:
        # - Prefix: starts with letter/underscore, followed by any identifier chars (non-greedy)
        # - Number: trailing digits (greedy, implicitly matches as many as possible)
        # Non-greedy means "item21" splits as ("item", "21") - prefix takes minimum chars
        # This is correct for GAMS range notation where we want the trailing number sequence
        symbolic_pattern = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_-]*?)(\d+)$")
        match_start = symbolic_pattern.match(start_bound)
        if not match_start:
            raise self._error(
                f"Invalid range start '{start_bound}': must be a number (e.g., 1) "
                f"or identifier followed by number (e.g., i1, route-1)",
                node,
            )

        match_end = symbolic_pattern.match(end_bound)
        if not match_end:
            raise self._error(
                f"Invalid range end '{end_bound}': must be a number (e.g., 100) "
                f"or identifier followed by number (e.g., i100, route-5)",
                node,
            )

        base_start = match_start.group(1)
        num_start = int(match_start.group(2))

        base_end = match_end.group(1)
        num_end = int(match_end.group(2))

        # Validate same base prefix
        if base_start != base_end:
            raise self._error(
                f"Range base mismatch: '{start_bound}' and '{end_bound}' have "
                f"different prefixes ('{base_start}' vs '{base_end}')",
                node,
            )

        # Validate range direction
        if num_start > num_end:
            raise self._error(
                f"Invalid range: start index {num_start} is greater than end index {num_end}", node
            )

        # Generate symbolic range
        return [f"{base_start}{i}" for i in range(num_start, num_end + 1)]

    def _process_alias_pair(self, pair_node: Tree) -> None:
        """Extract and register an alias pair from an alias_pair node.

        Args:
            pair_node: Tree node with data="alias_pair"

        Note:
            GAMS Alias syntax: Alias (target, alias_name1, alias_name2, ...)
            - First ID is always the existing set (target)
            - Remaining IDs are new alias names for that target

        Grammar: alias_pair: "(" ID "," id_list ")"
        Structure: [ID_token, id_list_tree]
        """
        if len(pair_node.children) < 2:
            raise self._error("Alias pair must have at least 2 parts", pair_node)

        # First child is an ID token
        first_id = _token_text(pair_node.children[0])

        # Second child is id_list tree containing remaining IDs
        id_list_node = pair_node.children[1]
        remaining_ids = [
            _token_text(tok)
            for tok in id_list_node.children
            if isinstance(tok, Token) and tok.type == "ID"
        ]

        if not remaining_ids:
            raise self._error("Alias pair must have at least one ID in the id_list", pair_node)

        # GAMS Alias syntax: Alias (target, alias_name1, alias_name2, ...)
        # - First ID is always the existing set (target)
        # - Remaining IDs are new alias names for that target
        # Examples:
        #   Alias (nx,i) → i is an alias for nx
        #   Alias (nc,j,k) → j and k are both aliases for nc
        target = first_id
        alias_names = remaining_ids
        for alias_name in alias_names:
            self._register_alias(alias_name, target, None, pair_node)

    def _handle_aliases_block(self, node: Tree) -> None:
        for child in node.children:
            if not isinstance(child, Tree):
                continue

            if child.data == "alias_multi":
                # Multiple alias pairs: Alias (nx,i), (ny,j);
                for pair_node in child.children:
                    if isinstance(pair_node, Tree) and pair_node.data == "alias_pair":
                        self._process_alias_pair(pair_node)
            elif child.data == "alias_single":
                # Single alias pair: Alias (i,j);
                pair_node = child.children[0]
                if isinstance(pair_node, Tree) and pair_node.data == "alias_pair":
                    self._process_alias_pair(pair_node)
            else:
                # Handle legacy syntax
                ids = [
                    _token_text(tok)
                    for tok in child.children
                    if isinstance(tok, Token) and tok.type == "ID"
                ]
                if child.data == "alias_plain" and len(ids) == 2:
                    # Traditional syntax: Aliases j, i (alias_name, target)
                    alias_name, target = ids
                    self._register_alias(alias_name, target, None, child)
                elif child.data == "alias_with_universe" and len(ids) == 3:
                    alias_name, target, universe = ids
                    self._register_alias(alias_name, target, universe, child)
                else:
                    raise self._error("Unsupported alias declaration form", child)

    def _handle_params_block(self, node: Tree) -> None:
        # Sprint 12 Day 5: Handle new param_decl_list structure
        for child in node.children:
            if isinstance(child, Tree) and child.data == "param_decl_list":
                # Process each param_decl in the list
                for param_decl_node in child.children:
                    if not isinstance(param_decl_node, Tree):
                        continue
                    self._process_param_decl(param_decl_node)
                return  # Done processing

        # Legacy path for backward compatibility
        for child in node.children:
            if not isinstance(child, Tree):
                continue
            if child.data == "param_list":
                # Handle comma-separated parameter names: Parameter x, y, z;
                # Grammar: ID "," id_list -> first ID + rest from id_list
                if not child.children or len(child.children) < 2:
                    raise self._error("Invalid param_list structure", child)
                first_name = _token_text(child.children[0])
                rest_names = (
                    _id_list(child.children[1]) if isinstance(child.children[1], Tree) else []
                )
                names = [first_name] + list(rest_names)
                for name in names:
                    param = ParameterDef(name=name, domain=())
                    self.model.add_param(param)
            elif child.data in {
                "param_domain",
                "param_domain_data",
                "param_plain",
                "param_plain_data",
            }:
                param = self._parse_param_decl(child)
                self.model.add_param(param)

    def _process_param_decl(self, child: Tree) -> None:
        """Process a single param_decl node (helper for _handle_params_block)."""
        # Sprint 12 Day 5 (Issue #417): Handle new param_single and param_list patterns
        if child.data == "param_list":
            # Handle comma-separated list: Parameter x, y, z;
            for param_item in child.children:
                if isinstance(param_item, Tree):
                    self._process_param_item(param_item)
        elif child.data == "param_single":
            # Handle single parameter declaration with potential description
            param_single_item = child.children[0]
            self._process_param_item(param_single_item)
        else:
            # Legacy patterns - delegate to _process_param_item
            self._process_param_item(child)

    def _process_param_item(self, item: Tree) -> None:
        """Process a single param_item or param_single_item node."""
        if item.data in {
            "param_domain",
            "param_domain_data",
            "param_plain",
            "param_plain_data",
        }:
            param = self._parse_param_decl(item)
            self.model.add_param(param)

    def _parse_table_value(self, value_text: str) -> float:
        """Parse a table value, handling special GAMS values like inf, -inf, eps, na.

        Args:
            value_text: The text representation of the value

        Returns:
            The parsed float value
        """
        # Try parsing as a regular number first
        try:
            return float(value_text)
        except ValueError:
            pass

        # Handle signed special values (e.g., -inf, +inf)
        value_lower = value_text.lower()
        if value_lower.startswith("-"):
            base_value = value_lower[1:]
            if base_value in _PREDEFINED_CONSTANTS:
                return -_PREDEFINED_CONSTANTS[base_value]
        elif value_lower.startswith("+"):
            base_value = value_lower[1:]
            if base_value in _PREDEFINED_CONSTANTS:
                return _PREDEFINED_CONSTANTS[base_value]

        # Handle unsigned special values
        if value_lower in _PREDEFINED_CONSTANTS:
            return _PREDEFINED_CONSTANTS[value_lower]

        # Default to 0.0 for unrecognized values
        return 0.0

    def _parse_param_data_value(self, value_node: Tree | Token) -> float:
        """Parse a param_data_value node, handling numbers and special GAMS values.

        Issue #564: Handles the grammar rule:
            param_data_value: NUMBER | SPECIAL_VALUE | MINUS SPECIAL_VALUE | PLUS SPECIAL_VALUE

        Args:
            value_node: Either a Tree (param_data_value) or Token (NUMBER/SPECIAL_VALUE)

        Returns:
            The parsed float value (na/undf become NaN, inf becomes infinity)
        """
        if isinstance(value_node, Token):
            # Direct token (NUMBER or SPECIAL_VALUE)
            return self._parse_table_value(_token_text(value_node))

        # Tree node - could be param_data_value with children
        if value_node.data == "param_data_value":
            children = [c for c in value_node.children if isinstance(c, Token)]
            if len(children) == 1:
                # Single token: NUMBER or SPECIAL_VALUE
                return self._parse_table_value(_token_text(children[0]))
            elif len(children) == 2:
                # MINUS/PLUS SPECIAL_VALUE (e.g., -inf, +inf)
                sign = _token_text(children[0])
                value = _token_text(children[1])
                return self._parse_table_value(sign + value)

        # Fallback: try to get the last token
        if value_node.children:
            last_child = value_node.children[-1]
            if isinstance(last_child, Token):
                return self._parse_table_value(_token_text(last_child))

        return 0.0

    def _combine_signed_special_tokens(self, tokens: list[Token]) -> list[Token]:
        """Combine MINUS/PLUS + ID tokens for special values like -inf, +inf, -eps.

        In GAMS, special values like -inf are tokenized as MINUS followed by ID("inf").
        This method identifies such patterns and combines them into a single synthetic token.

        Args:
            tokens: List of tokens to process

        Returns:
            New list with signed special values combined into single tokens
        """
        # Special value identifiers that can be prefixed with a sign
        special_values = {"inf", "eps", "na"}

        result: list[Token] = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            # Check if this is a MINUS or PLUS token followed by a special value ID
            if isinstance(token, Token) and token.type in ("MINUS", "PLUS") and i + 1 < len(tokens):
                next_token = tokens[i + 1]
                if (
                    isinstance(next_token, Token)
                    and next_token.type == "ID"
                    and _token_text(next_token).lower() in special_values
                ):
                    # Check they're on the same line and adjacent (no gap)
                    same_line = getattr(token, "line", None) == getattr(next_token, "line", None)
                    # Check column positions - sign should be immediately before ID
                    sign_col = getattr(token, "column", 0) or 0
                    id_col = getattr(next_token, "column", 0) or 0
                    # Allow for the sign character width (1 char)
                    adjacent = same_line and (id_col - sign_col <= 1)

                    if adjacent:
                        # Combine into a synthetic token
                        combined_value = _token_text(token) + _token_text(next_token)
                        synthetic_token = Token(
                            "ID",
                            combined_value,
                            line=getattr(token, "line", None),
                            column=getattr(token, "column", None),
                        )
                        result.append(synthetic_token)
                        i += 2  # Skip both tokens
                        continue

            result.append(token)
            i += 1

        return result

    def _handle_table_block(self, node: Tree) -> None:
        """
        Handle GAMS Table block.

        Uses token line and column positions to correctly parse sparse tables.
        Strategy:
        1. Group tokens by line number
        2. First line with IDs = column headers (and their column positions)
        3. Subsequent lines = data rows (match values to columns by position)

        Supports wildcard domains (*) where dimension names are inferred from data.
        """
        # Extract name and domain
        name = _token_text(node.children[0])

        # Handle table_domain_list which may contain wildcards
        domain_list_node = node.children[1]
        domain = []

        for child in domain_list_node.children:
            if isinstance(child, Tree):
                if child.data == "explicit_domain":
                    domain.append(_token_text(child.children[0]))
                elif child.data == "wildcard_domain":
                    domain.append("*")
                elif child.data == "wildcard_tuple_domain":
                    # Handle (*,*) or (*,*,*) etc.
                    # Count the number of wildcards in the tuple
                    wildcard_tuple_node = child.children[0]  # wildcard_tuple
                    num_wildcards = len(wildcard_tuple_node.children)
                    # Add each wildcard to domain
                    for _ in range(num_wildcards):
                        domain.append("*")

        domain = tuple(domain)

        # Find all table_content nodes (which can be table_row or PLUS tokens)
        # Also collect DESCRIPTION tokens which might contain column headers
        table_contents = [
            child
            for child in node.children
            if (isinstance(child, Tree) and child.data == "table_content")
            or (isinstance(child, Token) and child.type in ("PLUS", "DESCRIPTION"))
        ]

        if not table_contents:
            self.model.add_param(ParameterDef(name=name, domain=domain, values={}))
            return

        # Extract table_row nodes from table_content wrappers
        # PLUS tokens will be collected separately in the token collection phase
        table_rows = []
        for content in table_contents:
            if isinstance(content, Tree) and content.children:
                actual_node = content.children[0]
                if isinstance(actual_node, Tree) and actual_node.data == "table_row":
                    table_rows.append(actual_node)

        # Allow empty table_rows if we have DESCRIPTION tokens or continuations
        # (which might contain all the data)
        has_description_or_continuation = any(
            isinstance(c, Token)
            and c.type in ("DESCRIPTION", "PLUS")
            or (
                isinstance(c, Tree)
                and c.data == "table_content"
                and c.children
                and isinstance(c.children[0], Tree)
                and c.children[0].data == "table_continuation"
            )
            for c in table_contents
        )
        if not table_rows and not has_description_or_continuation:
            self.model.add_param(ParameterDef(name=name, domain=domain, values={}))
            return

        # Extract row labels first (to handle dotted labels and tuple labels)
        row_label_map = {}  # line_number -> row_label_string or list of row_label_strings
        for row in table_rows:
            # First child is always the row label (either table_row_label tree or ID token)
            if row.children:
                first_child = row.children[0]
                if isinstance(first_child, Tree):
                    if first_child.data == "simple_label":
                        # Simple or dotted label wrapped in simple_label
                        dotted_label_node = first_child.children[0]
                        # Filter out string literals (table descriptions) when building label
                        label_tokens = [
                            tok
                            for tok in dotted_label_node.children
                            if isinstance(tok, Token) and not _is_string_literal(tok)
                        ]
                        if label_tokens:
                            # Only create row label if there are non-string-literal tokens
                            label_parts = [_token_text(tok) for tok in label_tokens]
                            row_label = ".".join(label_parts)
                            # Get line number from first token
                            first_token = label_tokens[0]
                            if hasattr(first_token, "line"):
                                row_label_map[first_token.line] = row_label
                    elif first_child.data == "tuple_label":
                        # Tuple label like "(low,medium,high).ynot"
                        # Structure: tuple_label -> id_list, dotted_label
                        id_list_node = first_child.children[0]
                        dotted_label_node = first_child.children[1]

                        # Extract tuple elements
                        elements = [
                            _token_text(tok)
                            for tok in id_list_node.children
                            if isinstance(tok, Token)
                        ]

                        # Extract suffix (can be multi-part like "a.b.c")
                        suffix_parts = [
                            _token_text(tok)
                            for tok in dotted_label_node.children
                            if isinstance(tok, Token)
                        ]
                        suffix = ".".join(suffix_parts)

                        # Expand to multiple labels: elem1.suffix, elem2.suffix, ...
                        expanded_labels = [f"{elem}.{suffix}" for elem in elements]

                        # Get line number from first token (in id_list)
                        first_token = id_list_node.children[0]
                        if hasattr(first_token, "line"):
                            # Store as list to indicate this row should be replicated
                            row_label_map[first_token.line] = expanded_labels
                elif isinstance(first_child, Token):
                    # Simple ID label (legacy, shouldn't happen with new grammar)
                    row_label = _token_text(first_child)
                    if hasattr(first_child, "line"):
                        row_label_map[first_child.line] = row_label

        # Collect all tokens from table_row nodes with position info
        # Note: PLUS tokens are markers and will be skipped in line grouping
        all_tokens = []
        for row in table_rows:
            for child in row.children:
                if isinstance(child, Token):
                    all_tokens.append(child)
                elif isinstance(child, Tree):
                    if child.data == "table_value":
                        for grandchild in child.children:
                            if isinstance(grandchild, Token):
                                all_tokens.append(grandchild)
                            elif (
                                isinstance(grandchild, Tree)
                                and grandchild.data == "negative_special"
                            ):
                                # Handle -inf, -eps, etc. - combine MINUS and ID into one token
                                sign_token = grandchild.children[0]  # MINUS
                                id_token = grandchild.children[1]  # ID (e.g., inf)
                                combined_value = _token_text(sign_token) + _token_text(id_token)
                                synthetic_token = Token(
                                    "ID",
                                    combined_value,
                                    line=getattr(sign_token, "line", None),
                                    column=getattr(sign_token, "column", None),
                                )
                                all_tokens.append(synthetic_token)
                    elif child.data == "simple_label":
                        # simple_label wraps dotted_label
                        dotted_label_node = child.children[0]
                        for grandchild in dotted_label_node.children:
                            if isinstance(grandchild, Token):
                                # Skip string literals (table descriptions)
                                if not _is_string_literal(grandchild):
                                    all_tokens.append(grandchild)
                    elif child.data == "tuple_label":
                        # tuple_label contains id_list and dotted_label
                        # Collect tokens from both
                        for subnode in child.children:
                            if isinstance(subnode, Tree):
                                for tok in subnode.children:
                                    if isinstance(tok, Token):
                                        all_tokens.append(tok)

        # Collect PLUS tokens to identify continuation lines and extract continuation values
        plus_lines = set()  # Set of line numbers that start with +
        for content in table_contents:
            if isinstance(content, Tree):
                if content.data == "table_content" and content.children:
                    actual_node = content.children[0]
                    if isinstance(actual_node, Tree) and actual_node.data == "table_continuation":
                        # Extract PLUS token and collect continuation values
                        for token in actual_node.children:
                            if isinstance(token, Token):
                                if token.type == "PLUS":
                                    if hasattr(token, "line"):
                                        plus_lines.add(token.line)
                                else:
                                    # Add value tokens to all_tokens
                                    all_tokens.append(token)
                            elif isinstance(token, Tree) and token.data == "table_value":
                                for val_token in token.children:
                                    if isinstance(val_token, Token):
                                        all_tokens.append(val_token)
                                    elif (
                                        isinstance(val_token, Tree)
                                        and val_token.data == "negative_special"
                                    ):
                                        # Handle -inf, -eps in continuations
                                        sign_token = val_token.children[0]
                                        id_token = val_token.children[1]
                                        combined_value = _token_text(sign_token) + _token_text(
                                            id_token
                                        )
                                        synthetic_token = Token(
                                            "ID",
                                            combined_value,
                                            line=getattr(sign_token, "line", None),
                                            column=getattr(sign_token, "column", None),
                                        )
                                        all_tokens.append(synthetic_token)
            elif isinstance(content, Token) and content.type == "DESCRIPTION":
                # DESCRIPTION tokens may contain column headers that need to be parsed
                # These appear when column headers are on a line before a continuation marker
                # Parse the DESCRIPTION text to extract column header tokens
                desc_text = str(content)
                if desc_text and not _is_string_literal(content):
                    # Split on whitespace to get individual column names
                    # Create pseudo-tokens for each column header
                    col_names = desc_text.split()
                    if col_names and hasattr(content, "line") and hasattr(content, "column"):
                        # Estimate column positions based on the text
                        base_col = content.column
                        for col_name in col_names:
                            # Find position of this column name in the original text
                            col_pos = desc_text.find(col_name)
                            if col_pos >= 0:
                                # Create a pseudo-token with position info
                                from lark import Token as LarkToken

                                pseudo_token = LarkToken("ID", col_name)
                                pseudo_token.line = content.line
                                pseudo_token.column = (
                                    base_col if base_col is not None else 0
                                ) + col_pos
                                all_tokens.append(pseudo_token)

        if not all_tokens:
            self.model.add_param(ParameterDef(name=name, domain=domain, values={}))
            return

        # Post-process tokens to combine MINUS + ID for special values like -inf, -eps
        # This handles the case where "-inf" is tokenized as MINUS followed by ID("inf")
        all_tokens = self._combine_signed_special_tokens(all_tokens)

        # Group tokens by line
        from collections import defaultdict

        lines = defaultdict(list)
        for token in all_tokens:
            if hasattr(token, "line"):
                lines[token.line].append(token)

        # Sort tokens within each line by column position
        for line_num in lines:
            lines[line_num] = sorted(lines[line_num], key=lambda t: getattr(t, "column", 0))

        if not lines:
            self.model.add_param(ParameterDef(name=name, domain=domain, values={}))
            return

        # Sort lines by line number
        sorted_lines = sorted(lines.items())

        # Create a mapping to store column offsets for continuation tokens
        continuation_col_offsets: dict[int, int] = {}  # token id -> column offset

        # Merge continuation lines (those with +) with previous line
        merged_lines: list[tuple[int, list[Token]]] = []
        for line_num, line_tokens in sorted_lines:
            if line_num in plus_lines:
                # This is a continuation line - need to determine if it contains:
                # 1. Column headers (ID tokens) -> merge with first line (column headers)
                # 2. Data values (NUMBER tokens) -> merge with last line (previous data row)
                if merged_lines:
                    # Check if continuation line looks like column headers or data
                    # Column headers are all ID tokens (no numbers)
                    # Data rows have NUMBER tokens
                    has_number_tokens = any(
                        tok.type == "NUMBER" for tok in line_tokens if isinstance(tok, Token)
                    )
                    all_id_tokens = all(
                        tok.type == "ID" and not _is_string_literal(tok)
                        for tok in line_tokens
                        if isinstance(tok, Token)
                    )

                    # Determine if this is a column header continuation or data continuation
                    # 1. If only one line exists (column headers), continuation must be for headers
                    # 2. Otherwise, if all ID tokens and no numbers, it's column headers
                    if len(merged_lines) == 1:
                        is_column_header_continuation = True
                    else:
                        is_column_header_continuation = all_id_tokens and not has_number_tokens

                    if is_column_header_continuation:
                        # Merge with first line (column headers)
                        target_line_num, target_tokens = merged_lines[0]
                    else:
                        # Data continuation, merge with last line (previous data row)
                        target_line_num, target_tokens = merged_lines[-1]

                    # Need to adjust column positions of continuation tokens
                    # Find the maximum column position in the target line to know where to continue
                    if target_tokens:
                        # Get all column positions from target line tokens (with offsets applied)
                        prev_cols = []
                        for t in target_tokens:
                            if hasattr(t, "column") and t.column is not None:
                                col = t.column
                                # Apply offset if this token was from a continuation
                                if id(t) in continuation_col_offsets:
                                    col += continuation_col_offsets[id(t)]
                                prev_cols.append(col)
                        if prev_cols:
                            max_prev_col = max(prev_cols)
                            # Find the column spacing from the target line to determine spacing
                            col_spacing = 3  # default spacing
                            if len(target_tokens) >= 2:
                                # Calculate average spacing between columns
                                # Need to account for adjusted positions in continuation tokens
                                spacings = []
                                for j in range(len(target_tokens) - 1):
                                    if hasattr(target_tokens[j], "column") and hasattr(
                                        target_tokens[j + 1], "column"
                                    ):
                                        col1 = target_tokens[j].column or 0
                                        col2 = target_tokens[j + 1].column or 0
                                        # Apply offsets if these tokens were from continuation
                                        if id(target_tokens[j]) in continuation_col_offsets:
                                            col1 += continuation_col_offsets[id(target_tokens[j])]
                                        if id(target_tokens[j + 1]) in continuation_col_offsets:
                                            col2 += continuation_col_offsets[
                                                id(target_tokens[j + 1])
                                            ]
                                        spacings.append(col2 - col1)
                                if spacings:
                                    col_spacing = sum(spacings) // len(spacings)

                            # Store column offsets for continuation tokens
                            # Different handling for column header vs data continuations
                            if is_column_header_continuation:
                                # Column headers: place tokens sequentially after existing columns
                                for idx, token in enumerate(line_tokens):
                                    new_col = max_prev_col + (idx + 1) * col_spacing
                                    if hasattr(token, "column") and token.column is not None:
                                        offset = new_col - token.column
                                        continuation_col_offsets[id(token)] = offset
                            else:
                                # Data continuation: try to match with continuation column headers
                                # that have the same original column position
                                first_line_tokens = merged_lines[0][1] if merged_lines else []
                                has_matching_columns = False

                                for token in line_tokens:
                                    if hasattr(token, "column") and token.column is not None:
                                        token_col = token.column
                                        matching_offset = None
                                        for header_token in first_line_tokens:
                                            if (
                                                hasattr(header_token, "column")
                                                and header_token.column == token_col
                                                and id(header_token) in continuation_col_offsets
                                            ):
                                                matching_offset = continuation_col_offsets[
                                                    id(header_token)
                                                ]
                                                has_matching_columns = True
                                                break

                                        if matching_offset is not None:
                                            continuation_col_offsets[id(token)] = matching_offset

                                # If no matching continuation columns, use sequential placement
                                if not has_matching_columns:
                                    # Count existing data tokens to find which columns to map to
                                    data_tokens_count = len(
                                        [t for t in target_tokens[1:] if hasattr(t, "column")]
                                    )

                                    for idx, token in enumerate(line_tokens):
                                        if hasattr(token, "column") and token.column is not None:
                                            col_idx = data_tokens_count + idx
                                            if col_idx < len(first_line_tokens):
                                                target_col_header = first_line_tokens[col_idx]
                                                if (
                                                    hasattr(target_col_header, "column")
                                                    and target_col_header.column is not None
                                                ):
                                                    target_col = target_col_header.column
                                                    if (
                                                        id(target_col_header)
                                                        in continuation_col_offsets
                                                    ):
                                                        target_col += continuation_col_offsets[
                                                            id(target_col_header)
                                                        ]
                                                    offset = target_col - token.column
                                                    continuation_col_offsets[id(token)] = offset

                            # Update the target line with merged tokens
                            if is_column_header_continuation:
                                merged_lines[0] = (target_line_num, target_tokens + line_tokens)
                            else:
                                merged_lines[-1] = (target_line_num, target_tokens + line_tokens)
                        else:
                            # Update the target line with merged tokens
                            if is_column_header_continuation:
                                merged_lines[0] = (target_line_num, target_tokens + line_tokens)
                            else:
                                merged_lines[-1] = (target_line_num, target_tokens + line_tokens)
                    else:
                        # Update the target line with merged tokens
                        if is_column_header_continuation:
                            merged_lines[0] = (target_line_num, target_tokens + line_tokens)
                        else:
                            merged_lines[-1] = (target_line_num, target_tokens + line_tokens)

                    # Remove this line's label from row_label_map if it exists
                    if line_num in row_label_map:
                        del row_label_map[line_num]
                # else: no previous line, skip this continuation
            else:
                # Regular line (not a continuation marker line)
                merged_lines.append((line_num, line_tokens))

        sorted_lines = merged_lines

        if not sorted_lines:
            self.model.add_param(ParameterDef(name=name, domain=domain, values={}))
            return

        # First line should be column headers
        first_line_num, first_line_tokens = sorted_lines[0]

        # Remove column header line from row_label_map if it was added
        # (column headers are parsed as a table_row, so they might have been extracted as a row label)
        if first_line_num in row_label_map:
            del row_label_map[first_line_num]

        # Column headers: store name and column position
        col_headers = []  # List of (col_name, col_position) tuples
        for token in first_line_tokens:
            # Column headers can be ID or NUMBER tokens
            if token.type in ("ID", "NUMBER"):
                # Skip string literals (table descriptions) that were incorrectly parsed as IDs
                if token.type == "ID" and _is_string_literal(token):
                    continue
                col_name = _token_text(token)
                col_pos = getattr(token, "column", 0)
                # Apply continuation offset if this token came from a continuation line
                if id(token) in continuation_col_offsets:
                    col_pos += continuation_col_offsets[id(token)]
                col_headers.append((col_name, col_pos))

        if not col_headers:
            self.model.add_param(ParameterDef(name=name, domain=domain, values={}))
            return

        # Parse data rows
        values = {}
        for line_num, line_tokens in sorted_lines[1:]:
            if not line_tokens:
                continue

            # Get row header(s) from row_label_map (handles dotted labels and tuple labels)
            if line_num not in row_label_map:
                # Fallback: first token should be row header
                if line_tokens[0].type != "ID":
                    continue
                row_headers = [_token_text(line_tokens[0])]
            else:
                row_header_or_list = row_label_map[line_num]
                # Check if it's a tuple label (list) or simple label (string)
                if isinstance(row_header_or_list, list):
                    row_headers = row_header_or_list  # Multiple expanded labels
                else:
                    row_headers = [row_header_or_list]  # Single label

            # Match remaining tokens to columns by position
            # Collect all values for this row first
            row_values = {}  # col_name -> value
            used_columns = set()  # Track which columns have been matched
            for token in line_tokens[1:]:
                if token.type not in ("NUMBER", "ID"):
                    continue

                token_col = getattr(token, "column", 0)
                # Apply continuation column offset if this token came from a continuation line
                if id(token) in continuation_col_offsets:
                    token_col += continuation_col_offsets[id(token)]

                # Find the closest column header at or before this position
                # (to handle slight alignment variations)
                best_match = None
                min_dist = float("inf")
                for col_name, col_pos in col_headers:
                    # Skip columns that have already been matched
                    if col_name in used_columns:
                        continue
                    # Allow token to be within ~6 chars of column header position
                    dist = abs(token_col - col_pos)
                    if dist < min_dist and dist <= 6:
                        min_dist = dist
                        best_match = col_name

                if best_match:
                    # Parse the value
                    value_text = _token_text(token)
                    value = self._parse_table_value(value_text)
                    row_values[best_match] = value
                    used_columns.add(best_match)  # Mark this column as used

            # Replicate the row data for each expanded label (for tuple labels)
            for row_header in row_headers:
                for col_name, value in row_values.items():
                    key = (row_header, col_name)
                    values[key] = value

        # Fill in missing cells with 0.0
        # For each combination of row and column that doesn't have a value
        # Collect all row headers from the values that were already parsed
        all_row_headers = set()
        for row_header, _col_name in values.keys():
            all_row_headers.add(row_header)

        # Also collect row headers from lines (to handle completely empty rows)
        for _line_num, line_tokens in sorted_lines[1:]:
            if line_tokens and line_tokens[0].type == "ID":
                # First token is row header
                row_header = _token_text(line_tokens[0])
                all_row_headers.add(row_header)

        col_names = [name for name, _ in col_headers]
        for row_header in all_row_headers:
            for col_name in col_names:
                key = (row_header, col_name)
                if key not in values:
                    values[key] = 0.0

        self.model.add_param(ParameterDef(name=name, domain=domain, values=values))

    def _handle_variables_block(self, node: Tree) -> None:
        # Check for block-level variable kind (e.g., "Positive Variables")
        block_kind = None
        for child in node.children:
            # var_kind is a Tree node containing a Token
            if isinstance(child, Tree) and child.data == "var_kind":
                if child.children and isinstance(child.children[0], Token):
                    kind_token = child.children[0]
                    if kind_token.type in _VAR_KIND_MAP:
                        block_kind = _VAR_KIND_MAP[kind_token.type]
                        break

        # Sprint 12 Day 5: Handle new var_decl_list structure
        # variables_block now contains var_decl_list, which contains var_decl nodes
        for child in node.children:
            if isinstance(child, Tree) and child.data == "var_decl_list":
                # Process each var_decl in the list
                for var_decl_node in child.children:
                    if not isinstance(var_decl_node, Tree):
                        continue
                    # Delegate to existing logic by processing var_decl as if it were a direct child
                    self._process_var_decl(var_decl_node, block_kind)
                return  # Done processing

        # Process variable declarations (legacy path for backward compatibility)
        for child in node.children:
            if not isinstance(child, Tree):
                continue
            if child.data == "var_list":
                # Handle comma-separated list: Variables z "desc", t(i) "desc", x;
                # Get declaration-level var_kind if present
                idx = 0
                decl_kind = VarKind.CONTINUOUS
                if isinstance(child.children[idx], Tree) and child.children[idx].data == "var_kind":
                    if child.children[idx].children and isinstance(
                        child.children[idx].children[0], Token
                    ):
                        kind_token = child.children[idx].children[0]
                        if kind_token.type in _VAR_KIND_MAP:
                            decl_kind = _VAR_KIND_MAP[kind_token.type]
                    idx += 1
                # Process each var_item in the list
                for var_item in child.children[idx:]:
                    if not isinstance(var_item, Tree):
                        continue
                    if var_item.data == "var_item_indexed":
                        # var_item_indexed: var_kind? ID "(" id_list ")" STRING?
                        item_idx = 0
                        item_kind = VarKind.CONTINUOUS
                        # Check for item-level var_kind
                        if (
                            isinstance(var_item.children[item_idx], Tree)
                            and var_item.children[item_idx].data == "var_kind"
                        ):
                            if var_item.children[item_idx].children and isinstance(
                                var_item.children[item_idx].children[0], Token
                            ):
                                kind_token = var_item.children[item_idx].children[0]
                                if kind_token.type in _VAR_KIND_MAP:
                                    item_kind = _VAR_KIND_MAP[kind_token.type]
                            item_idx += 1
                        name = _token_text(var_item.children[item_idx])
                        domain = _id_list(var_item.children[item_idx + 1])
                        # Item-level > declaration-level > block-level
                        final_kind = (
                            item_kind
                            if item_kind != VarKind.CONTINUOUS
                            else (
                                decl_kind
                                if decl_kind != VarKind.CONTINUOUS
                                else (block_kind or VarKind.CONTINUOUS)
                            )
                        )
                        self.model.add_var(VariableDef(name=name, domain=domain, kind=final_kind))
                    elif var_item.data == "var_item_scalar":
                        # var_item_scalar: var_kind? ID STRING?
                        item_idx = 0
                        item_kind = VarKind.CONTINUOUS
                        # Check for item-level var_kind
                        if (
                            isinstance(var_item.children[item_idx], Tree)
                            and var_item.children[item_idx].data == "var_kind"
                        ):
                            if var_item.children[item_idx].children and isinstance(
                                var_item.children[item_idx].children[0], Token
                            ):
                                kind_token = var_item.children[item_idx].children[0]
                                if kind_token.type in _VAR_KIND_MAP:
                                    item_kind = _VAR_KIND_MAP[kind_token.type]
                            item_idx += 1
                        name = _token_text(var_item.children[item_idx])
                        # Item-level > declaration-level > block-level
                        final_kind = (
                            item_kind
                            if item_kind != VarKind.CONTINUOUS
                            else (
                                decl_kind
                                if decl_kind != VarKind.CONTINUOUS
                                else (block_kind or VarKind.CONTINUOUS)
                            )
                        )
                        self.model.add_var(VariableDef(name=name, domain=(), kind=final_kind))
            elif child.data in {"var_indexed", "var_scalar"}:
                # Handle single variable declaration (backward compatibility)
                decl_kind, name, domain, _description = self._parse_var_decl(child)
                # Declaration-level kind takes precedence over block-level kind
                final_kind = (
                    decl_kind
                    if decl_kind != VarKind.CONTINUOUS
                    else (block_kind or VarKind.CONTINUOUS)
                )
                # TODO: Support storing description in VariableDef. Description is parsed but not stored
                #       (no description field yet). Consider adding description field in future enhancement.
                self.model.add_var(VariableDef(name=name, domain=domain, kind=final_kind))

    def _process_var_decl(self, child: Tree, block_kind: VarKind | None) -> None:
        """Process a single var_decl node (helper for _handle_variables_block)."""
        if child.data == "var_list":
            # Handle comma-separated list: Variables z "desc", t(i) "desc", x;
            # Get declaration-level var_kind if present
            idx = 0
            decl_kind = VarKind.CONTINUOUS
            if isinstance(child.children[idx], Tree) and child.children[idx].data == "var_kind":
                if child.children[idx].children and isinstance(
                    child.children[idx].children[0], Token
                ):
                    kind_token = child.children[idx].children[0]
                    if kind_token.type in _VAR_KIND_MAP:
                        decl_kind = _VAR_KIND_MAP[kind_token.type]
                idx += 1
            # Process each var_item in the list
            for var_item in child.children[idx:]:
                if not isinstance(var_item, Tree):
                    continue
                if var_item.data == "var_item_indexed":
                    # var_item_indexed: var_kind? ID "(" id_list ")" STRING?
                    item_idx = 0
                    item_kind = VarKind.CONTINUOUS
                    # Check for item-level var_kind
                    if (
                        isinstance(var_item.children[item_idx], Tree)
                        and var_item.children[item_idx].data == "var_kind"
                    ):
                        if var_item.children[item_idx].children and isinstance(
                            var_item.children[item_idx].children[0], Token
                        ):
                            kind_token = var_item.children[item_idx].children[0]
                            if kind_token.type in _VAR_KIND_MAP:
                                item_kind = _VAR_KIND_MAP[kind_token.type]
                        item_idx += 1
                    name = _token_text(var_item.children[item_idx])
                    domain = _id_list(var_item.children[item_idx + 1])
                    # Item-level > declaration-level > block-level
                    final_kind = (
                        item_kind
                        if item_kind != VarKind.CONTINUOUS
                        else (
                            decl_kind
                            if decl_kind != VarKind.CONTINUOUS
                            else (block_kind or VarKind.CONTINUOUS)
                        )
                    )
                    self.model.add_var(VariableDef(name=name, domain=domain, kind=final_kind))
                elif var_item.data == "var_item_scalar":
                    # var_item_scalar: var_kind? ID STRING?
                    item_idx = 0
                    item_kind = VarKind.CONTINUOUS
                    # Check for item-level var_kind
                    if (
                        isinstance(var_item.children[item_idx], Tree)
                        and var_item.children[item_idx].data == "var_kind"
                    ):
                        if var_item.children[item_idx].children and isinstance(
                            var_item.children[item_idx].children[0], Token
                        ):
                            kind_token = var_item.children[item_idx].children[0]
                            if kind_token.type in _VAR_KIND_MAP:
                                item_kind = _VAR_KIND_MAP[kind_token.type]
                        item_idx += 1
                    name = _token_text(var_item.children[item_idx])
                    # Item-level > declaration-level > block-level
                    final_kind = (
                        item_kind
                        if item_kind != VarKind.CONTINUOUS
                        else (
                            decl_kind
                            if decl_kind != VarKind.CONTINUOUS
                            else (block_kind or VarKind.CONTINUOUS)
                        )
                    )
                    self.model.add_var(VariableDef(name=name, domain=(), kind=final_kind))
        elif child.data == "var_single":
            # Handle single variable declaration with potential description
            # var_single wraps a var_single_item which can be var_item_indexed or var_item_scalar
            var_single_item = child.children[0]
            if var_single_item.data == "var_item_indexed":
                # var_item_indexed: var_kind? ID "(" id_list ")" (STRING | desc_text)?
                item_idx = 0
                item_kind = VarKind.CONTINUOUS
                # Check for item-level var_kind
                if (
                    isinstance(var_single_item.children[item_idx], Tree)
                    and var_single_item.children[item_idx].data == "var_kind"
                ):
                    if var_single_item.children[item_idx].children and isinstance(
                        var_single_item.children[item_idx].children[0], Token
                    ):
                        kind_token = var_single_item.children[item_idx].children[0]
                        if kind_token.type in _VAR_KIND_MAP:
                            item_kind = _VAR_KIND_MAP[kind_token.type]
                    item_idx += 1
                name = _token_text(var_single_item.children[item_idx])
                domain = _id_list(var_single_item.children[item_idx + 1])
                # Item-level > block-level
                final_kind = (
                    item_kind
                    if item_kind != VarKind.CONTINUOUS
                    else (block_kind or VarKind.CONTINUOUS)
                )
                self.model.add_var(VariableDef(name=name, domain=domain, kind=final_kind))
            elif var_single_item.data == "var_item_scalar":
                # var_item_scalar: var_kind? ID (STRING | desc_text)?
                item_idx = 0
                item_kind = VarKind.CONTINUOUS
                # Check for item-level var_kind
                if (
                    isinstance(var_single_item.children[item_idx], Tree)
                    and var_single_item.children[item_idx].data == "var_kind"
                ):
                    if var_single_item.children[item_idx].children and isinstance(
                        var_single_item.children[item_idx].children[0], Token
                    ):
                        kind_token = var_single_item.children[item_idx].children[0]
                        if kind_token.type in _VAR_KIND_MAP:
                            item_kind = _VAR_KIND_MAP[kind_token.type]
                    item_idx += 1
                name = _token_text(var_single_item.children[item_idx])
                # Item-level > block-level
                final_kind = (
                    item_kind
                    if item_kind != VarKind.CONTINUOUS
                    else (block_kind or VarKind.CONTINUOUS)
                )
                self.model.add_var(VariableDef(name=name, domain=(), kind=final_kind))
        elif child.data in {"var_indexed", "var_scalar"}:
            # Handle single variable declaration (backward compatibility)
            decl_kind, name, domain, _description = self._parse_var_decl(child)
            # Declaration-level kind takes precedence over block-level kind
            final_kind = (
                decl_kind if decl_kind != VarKind.CONTINUOUS else (block_kind or VarKind.CONTINUOUS)
            )
            # TODO: Support storing description in VariableDef. Description is parsed but not stored
            #       (no description field yet). Consider adding description field in future enhancement.
            self.model.add_var(VariableDef(name=name, domain=domain, kind=final_kind))

    def _handle_scalars_block(self, node: Tree) -> None:
        for child in node.children:
            if not isinstance(child, Tree):
                continue

            # New grammar: scalar_list contains scalar_item nodes
            # scalar_list: scalar_item (","? scalar_item)+
            # scalar_single: scalar_single_item
            if child.data == "scalar_list":
                for scalar_item_node in child.children:
                    if not isinstance(scalar_item_node, Tree):
                        continue
                    self._process_scalar_item(scalar_item_node)
                continue
            elif child.data == "scalar_single":
                # Single scalar (uses scalar_single_item which supports desc_text)
                if child.children and isinstance(child.children[0], Tree):
                    self._process_scalar_item(child.children[0])
                continue

            # Fallback: shouldn't reach here with new grammar
            self._process_scalar_item(child)

    def _process_scalar_item(self, child: Tree) -> None:
        """Process a scalar node from either scalar_item or scalar_single_item."""
        name_token = child.children[0]
        name = _token_text(name_token)
        param = ParameterDef(name=name)

        if child.data == "scalar_with_data":
            # Format: ID [scalar_desc_text] "/" scalar_data_items "/" (ASSIGN expr)?
            # child.children[0] = ID
            # child.children[1] = scalar_desc_text (only for scalar_single_item) or first "/" token
            # Find the scalar_data_items node (skip scalar_desc_text if present and any tokens like '/')
            data_idx = 1
            while data_idx < len(child.children):
                node_candidate = child.children[data_idx]
                if isinstance(node_candidate, Tree) and node_candidate.data == "scalar_data_items":
                    break
                data_idx += 1

            if data_idx < len(child.children):
                data_node = child.children[data_idx]
                values = [
                    float(_token_text(tok))
                    for tok in data_node.scan_values(
                        lambda v: isinstance(v, Token) and v.type == "NUMBER"
                    )
                ]
                if values:
                    param.values[()] = values[-1]
                # Check for optional assignment after the data
                if len(child.children) > data_idx + 1 and isinstance(
                    child.children[data_idx + 1], Tree
                ):
                    value_expr = self._expr_with_context(
                        child.children[data_idx + 1], f"scalar '{name}' assignment", ()
                    )
                    param.values[()] = self._extract_constant(
                        value_expr, f"scalar '{name}' assignment"
                    )
        elif child.data == "scalar_with_assign":
            # Format: ID [scalar_desc_text] ASSIGN expr
            # child.children[0] = ID
            # child.children[1] = scalar_desc_text (only for scalar_single_item, may be empty)
            # child.children[-1] = expr (always the last child)
            # Get the expr node (always the last child after ID and scalar_desc_text)
            expr_idx = len(child.children) - 1
            value_expr = self._expr_with_context(
                child.children[expr_idx], f"scalar '{name}' assignment", ()
            )
            param.values[()] = self._extract_constant(value_expr, f"scalar '{name}' assignment")
        # else: scalar_plain, just declare without value

        self.model.add_param(param)

    def _parse_var_decl(self, node: Tree) -> tuple[VarKind, str, tuple[str, ...], str | None]:
        idx = 0
        kind = VarKind.CONTINUOUS
        # Check for declaration-level var_kind (wrapped in Tree node)
        if isinstance(node.children[idx], Tree) and node.children[idx].data == "var_kind":
            if node.children[idx].children and isinstance(node.children[idx].children[0], Token):
                kind_token = node.children[idx].children[0]
                if kind_token.type in _VAR_KIND_MAP:
                    kind = _VAR_KIND_MAP[kind_token.type]
            idx += 1
        # Get variable name (must be a Token)
        if not isinstance(node.children[idx], Token):
            raise self._error(f"Expected variable name token, got {type(node.children[idx])}", node)
        name = _token_text(node.children[idx])
        idx += 1
        domain: tuple[str, ...] = ()
        description: str | None = None
        # Check for domain specification (id_list for var_indexed)
        if idx < len(node.children) and isinstance(node.children[idx], Tree):
            # Sprint 12 Day 5: distinguish between id_list (domain) and desc_text (description)
            if node.children[idx].data == "id_list":
                domain = _id_list(node.children[idx])
                idx += 1
            # desc_text is handled below
        # Check for description (STRING token or DESC_TEXT/SCALAR_DESC_TEXT terminal)
        if idx < len(node.children):
            child = node.children[idx]
            if isinstance(child, Token):
                if child.type == "STRING":
                    description = _token_text(child)
                elif child.type == "DESC_TEXT":
                    # Sprint 12 Day 5 (Issue #417): DESC_TEXT is now a terminal token
                    description = str(child.value) if child.value else None
            elif isinstance(child, Tree) and child.data in ("desc_text", "scalar_desc_text"):
                # Legacy: desc_text as a rule node (backward compatibility)
                # desc_text/scalar_desc_text contains ID tokens - extract and join them
                # Note: scalar_desc_text may be empty (zero tokens), desc_text requires 2+
                if child.children:
                    desc_tokens = [_token_text(t) for t in child.children if isinstance(t, Token)]
                    description = " ".join(desc_tokens) if desc_tokens else None
        return kind, name, domain, description

    def _handle_equations_block(self, node: Tree) -> None:
        for child in node.children:
            if not isinstance(child, Tree):
                continue
            if child.data == "eqn_head_list":
                # Handle comma-separated list: Equations eq1, eq2, eq3;
                names = _id_list(child.children[0])
                for name in names:
                    self._declared_equations.add(name.lower())  # Issue #373: case-insensitive
                    self._equation_domains[name.lower()] = ()  # Issue #373: case-insensitive
            elif child.data == "eqn_head_scalar":
                name = _token_text(child.children[0])
                self._declared_equations.add(name.lower())  # Issue #373: case-insensitive
                self._equation_domains[name.lower()] = ()  # Issue #373: case-insensitive
            elif child.data == "eqn_head_domain":
                name = _token_text(child.children[0])
                domain = _domain_list(child.children[1])  # Sprint 11 Day 1: Use _domain_list
                self._ensure_sets(domain, f"equation '{name}' domain", child)
                self._declared_equations.add(name.lower())  # Issue #373: case-insensitive
                self._equation_domains[name.lower()] = domain  # Issue #373: case-insensitive
            elif child.data == "eqn_head_domain_list":
                # Handle comma-separated with domain: Equations eq1, eq2(i,j);
                # This is actually invalid GAMS syntax, but we handle it gracefully
                names = _id_list(child.children[0])
                domain = _domain_list(child.children[1])  # Sprint 11 Day 1: Use _domain_list
                self._ensure_sets(domain, "equation domain", child)
                for name in names:
                    self._declared_equations.add(name.lower())  # Issue #373: case-insensitive
                    self._equation_domains[name.lower()] = domain  # Issue #373: case-insensitive

    def _handle_eqn_def_scalar(self, node: Tree) -> None:
        name = _token_text(node.children[0])
        if name.lower() not in self._declared_equations:  # Issue #373: case-insensitive
            raise self._parse_error(
                f"Equation '{name}' defined without declaration",
                node,
                suggestion=f"Add a declaration like 'Equation {name};' before defining it",
            )

        # Extract source location from equation definition node
        source_location = self._extract_source_location(node)

        # Extract condition if present
        # Children: [ID, condition?, expr, REL_K, expr]
        condition_node = next(
            (c for c in node.children[1:] if isinstance(c, Tree) and c.data == "condition"), None
        )
        condition_expr = None
        if condition_node:
            # condition node: DOLLAR "(" expr ")" -> children are [DOLLAR_token, expr_tree]
            domain = self._equation_domains.get(name.lower(), ())  # Issue #373: case-insensitive
            condition_expr = self._expr_with_context(
                condition_node.children[1], f"equation '{name}' condition", domain
            )

        # Find expr nodes, skipping optional condition
        expr_nodes = [c for c in node.children[1:] if isinstance(c, Tree) and c.data != "condition"]
        rel_token = next(c for c in node.children if isinstance(c, Token) and c.type == "REL_K")

        lhs_node = expr_nodes[0]
        rhs_node = expr_nodes[1]
        domain = self._equation_domains.get(name.lower(), ())  # Issue #373: case-insensitive
        relation = _REL_MAP[rel_token.value.lower()]
        lhs = self._expr_with_context(lhs_node, f"equation '{name}' LHS", domain)
        rhs = self._expr_with_context(rhs_node, f"equation '{name}' RHS", domain)
        equation = EquationDef(
            name=name,
            domain=domain,
            relation=relation,
            lhs_rhs=(lhs, rhs),
            condition=condition_expr,
            source_location=source_location,
        )
        self.model.add_equation(equation)

    def _handle_eqn_def_domain(self, node: Tree) -> None:
        name = _token_text(node.children[0])
        domain = _domain_list(node.children[1])  # Sprint 11 Day 1: Use _domain_list
        if name.lower() not in self._declared_equations:  # Issue #373: case-insensitive
            raise self._parse_error(
                f"Equation '{name}' defined without declaration",
                node,
                suggestion=f"Add a declaration like 'Equation {name}({','.join(domain)});' before defining it",
            )
        self._ensure_sets(domain, f"equation '{name}' domain", node)

        # Extract source location from equation definition node
        source_location = self._extract_source_location(node)

        # Extract condition if present
        # Children: [ID, id_list, condition?, expr, REL_K, expr]
        condition_node = next(
            (c for c in node.children[2:] if isinstance(c, Tree) and c.data == "condition"), None
        )
        condition_expr = None
        if condition_node:
            # condition node: DOLLAR "(" expr ")" -> children are [DOLLAR_token, expr_tree]
            condition_expr = self._expr_with_context(
                condition_node.children[1], f"equation '{name}' condition", domain
            )

        # Find expr nodes, skipping optional condition
        expr_nodes = [c for c in node.children[2:] if isinstance(c, Tree) and c.data != "condition"]
        rel_token = next(c for c in node.children if isinstance(c, Token) and c.type == "REL_K")

        lhs_node = expr_nodes[0]
        rhs_node = expr_nodes[1]
        relation = _REL_MAP[rel_token.value.lower()]
        lhs = self._expr_with_context(lhs_node, f"equation '{name}' LHS", domain)
        rhs = self._expr_with_context(rhs_node, f"equation '{name}' RHS", domain)
        equation = EquationDef(
            name=name,
            domain=domain,
            relation=relation,
            lhs_rhs=(lhs, rhs),
            condition=condition_expr,
            source_location=source_location,
        )
        self.model.add_equation(equation)

    def _handle_solve(self, node: Tree) -> None:
        name = _token_text(node.children[0])
        self.model.model_name = name
        sense = ObjSense.MIN
        objvar = None
        idx = 1

        # Sprint 11 Day 2: solver_type can appear before OR after obj_sense
        # Grammar variant 2: "Solve"i ID "using"i solver_type obj_sense ID SEMI
        #   Children: [ID, solver_type, obj_sense, ID, SEMI]

        # Skip solver_type if it appears first
        if (
            idx < len(node.children)
            and isinstance(node.children[idx], Tree)
            and node.children[idx].data == "solver_type"
        ):
            idx += 1

        # Look for obj_sense
        if (
            idx < len(node.children)
            and isinstance(node.children[idx], Tree)
            and node.children[idx].data == "obj_sense"
        ):
            sense_token = node.children[idx].children[0]
            sense = ObjSense.MIN if sense_token.type == "MINIMIZING_K" else ObjSense.MAX
            idx += 1

        # Skip solver_type if it appears after obj_sense
        if (
            idx < len(node.children)
            and isinstance(node.children[idx], Tree)
            and node.children[idx].data == "solver_type"
        ):
            idx += 1

        if idx < len(node.children) and isinstance(node.children[idx], Token):
            objvar = _token_text(node.children[idx])
        if objvar:
            self.model.objective = ObjectiveIR(sense=sense, objvar=objvar)

    def _handle_model_all(self, node: Tree) -> None:
        name = _token_text(node.children[0])
        if self.model.declared_model is None:
            self.model.declared_model = name
        self.model.model_equations = []
        self.model.model_uses_all = True

    def _handle_model_with_list(self, node: Tree) -> None:
        name = _token_text(node.children[0])
        refs = [
            _token_text(tok)
            for tok in node.children[1].children
            if isinstance(tok, Token) and tok.type == "ID"
        ]
        if self.model.declared_model is None:
            self.model.declared_model = name
        self.model.model_equations = refs
        self.model.model_uses_all = False

    def _handle_model_decl(self, node: Tree) -> None:
        name = _token_text(node.children[0])
        if self.model.declared_model is None:
            self.model.declared_model = name
        self.model.model_equations = []
        self.model.model_uses_all = False

    def _handle_model_multi(self, node: Tree) -> None:
        """Handle multi-model declaration (Sprint 9 Day 5).

        Grammar structure:
            model_stmt: ("Models"i | "Model"i) model_decl_item+ SEMI
            model_decl_item: ID "/" model_ref_list "/"
                           | ID "/" "all"i "/"

        Example:
            Model
               m  / objdef, eq1  /
               mx / objdef, eq1x /;

        Note: Only the first model is stored in ModelIR (current limitation).
        """
        # Extract all model_decl_item nodes
        model_items = [
            child
            for child in node.children
            if isinstance(child, Tree) and child.data == "model_decl_item"
        ]

        if not model_items:
            raise self._error("Multi-model declaration has no model items", node)

        # Process the first model only (store in ModelIR)
        first_item = model_items[0]
        name = _token_text(first_item.children[0])

        if self.model.declared_model is None:
            self.model.declared_model = name

        # Check if this model uses "all" or has an equation list
        if len(first_item.children) > 1:
            second_child = first_item.children[1]
            if isinstance(second_child, Tree) and second_child.data == "model_ref_list":
                # Model has equation list
                refs = [
                    _token_text(tok)
                    for tok in second_child.children
                    if isinstance(tok, Token) and tok.type == "ID"
                ]
                # Special case: if the list contains only "all" (case-insensitive), treat it as / all /
                if len(refs) == 1 and refs[0].lower() == "all":
                    self.model.model_equations = []
                    self.model.model_uses_all = True
                else:
                    self.model.model_equations = refs
                    self.model.model_uses_all = False
        else:
            # No equations specified
            self.model.model_equations = []
            self.model.model_uses_all = False

    def _handle_option_stmt(self, node: Tree) -> None:
        """Handle option statement (Sprint 8: mock/store approach).

        Grammar structure:
            option_stmt: ("option"i | "options"i) option_list SEMI
            option_list: option_item ("," option_item)*
            option_item: ID "=" option_value  -> option_with_value
                       | ID ":" NUMBER (":" NUMBER)*  -> option_format
                       | ID                   -> option_flag
            option_value: NUMBER | ON | OFF

        Option values are stored as tuples (name, value) where value is:
            - int/float for numeric options (option limrow = 0)
            - str ("on"/"off") for boolean options (option solprint = off)
            - list[int] for format options (option arep:6:3:1 -> [6, 3, 1])
            - None for flag options (option clear)

        Example:
            option limrow = 0, limcol = 0;
            option arep:6:3:1;
            option limrow=0, arep:6, clear;
        """
        options = []

        # Find the option_list node
        option_list = next(
            (
                child
                for child in node.children
                if isinstance(child, Tree) and child.data == "option_list"
            ),
            None,
        )

        if option_list is None:
            raise self._error("Malformed option statement: missing option_list", node)

        # Process each option_item
        for item in option_list.children:
            if not isinstance(item, Tree):
                continue

            if item.data == "option_with_value":
                # ID "=" option_value
                if len(item.children) < 2:
                    raise self._error("Malformed option with value", item)

                name = _token_text(item.children[0])
                value_node = item.children[1]

                # option_value is always a Tree node with a single child token
                if not isinstance(value_node, Tree):
                    raise self._error("Expected option_value tree node", value_node)

                if not value_node.children:
                    raise self._error("option_value has no children", value_node)

                value_token = value_node.children[0]

                if not isinstance(value_token, Token):
                    raise self._error("Expected token in option_value", value_token)

                # Parse the value (NUMBER, "on", or "off")
                value_text = _token_text(value_token)
                if value_token.type == "NUMBER":
                    # Parse as int or float
                    try:
                        value = int(value_text)
                    except ValueError:
                        value = float(value_text)
                else:
                    # Keep as string ("on" or "off")
                    value = value_text.lower()

                options.append((name, value))

            elif item.data == "option_format":
                # ID ":" NUMBER (":" NUMBER)* - display format syntax
                # GAMS format syntax (d:r:c) expects integers only
                name = _token_text(item.children[0])
                # Collect all the format numbers (must be integers)
                format_numbers = []
                for child in item.children[1:]:
                    if isinstance(child, Token) and child.type == "NUMBER":
                        format_numbers.append(int(_token_text(child)))
                options.append((name, format_numbers))

            elif item.data == "option_flag":
                # ID only (flag with no value)
                name = _token_text(item.children[0])
                options.append((name, None))

        # Create OptionStatement and store in model
        location = self._extract_source_location(node)
        option_stmt = OptionStatement(options=options, location=location)

        # Sprint 8: Mock/store approach - just store, don't process
        self.model.option_statements.append(option_stmt)

    def _handle_if_stmt(self, node: Tree) -> None:
        """Handle if-elseif-else statement (Sprint 8 Day 2: mock/store approach).

        Grammar structure:
            if_stmt: "if"i "(" expr "," stmt+ elseif_clause* else_clause? ")" SEMI
            elseif_clause: "elseif"i expr "," stmt+
            else_clause: "else"i stmt+

        Example:
            if(abs(x.l - 5) < tol,
               display 'case 1';
            elseif abs(x.l - 10) < tol,
               display 'case 2';
            else
               display 'default';
            );
        """
        # Extract condition (first child should be expr)
        condition = None
        then_stmts = []
        elseif_clauses = []
        else_stmts = None

        # Parse children: expr, stmt+, elseif_clause*, else_clause?
        in_then = False
        for child in node.children:
            if isinstance(child, Token):
                continue  # Skip SEMI and other tokens

            if isinstance(child, Tree):
                if child.data in (
                    "expr",
                    "sum_expr",
                    "or_expr",
                    "and_expr",
                    "comp_expr",
                    "arith_expr",
                    "term",
                    "factor",
                    "power",
                    "atom",
                    "binop",
                    "compile_const",
                ):
                    # This is the main condition
                    if condition is None:
                        condition = child
                        in_then = True
                    # Note: elseif conditions are inside elseif_clause nodes
                elif child.data == "elseif_clause":
                    # Extract elseif condition and statements
                    in_then = False
                    elseif_cond = None
                    elseif_stmts = []
                    for elseif_child in child.children:
                        if isinstance(elseif_child, Tree):
                            if elseif_child.data in (
                                "expr",
                                "sum_expr",
                                "or_expr",
                                "and_expr",
                                "comp_expr",
                                "arith_expr",
                                "term",
                                "factor",
                                "power",
                                "atom",
                                "binop",
                                "compile_const",
                            ):
                                elseif_cond = elseif_child
                            else:
                                elseif_stmts.append(elseif_child)
                    if elseif_cond is not None:
                        elseif_clauses.append((elseif_cond, elseif_stmts))
                elif child.data == "else_clause":
                    # Extract else statements
                    in_then = False
                    else_stmts = []
                    for else_child in child.children:
                        if isinstance(else_child, Tree):
                            else_stmts.append(else_child)
                elif in_then:
                    # This is a statement in the then block
                    then_stmts.append(child)

        if condition is None:
            raise self._error("Malformed if statement: missing condition", node)

        # Create ConditionalStatement and store in model
        location = self._extract_source_location(node)
        cond_stmt = ConditionalStatement(
            condition=condition,
            then_stmts=then_stmts,
            elseif_clauses=elseif_clauses,
            else_stmts=else_stmts,
            location=location,
        )

        # Sprint 8: Mock/store approach - just store, don't execute
        self.model.conditional_statements.append(cond_stmt)

    def _handle_loop_stmt(self, node: Tree) -> None:
        """Handle loop statement (Sprint 11 Day 2 Extended: mock/store approach).

        Grammar structure:
            loop_stmt: "loop"i "(" id_list "," exec_stmt+ ")" SEMI
                     | "loop"i "(" "(" id_list ")" "," exec_stmt+ ")" SEMI  -> loop_stmt_paren

        Example:
            loop((n,d),
               p = round(mod(p,10)) + 1;
               point.l(n,d) = p/10;
            );
        """
        # Extract indices and body statements
        indices = None
        body_stmts = []

        for child in node.children:
            if isinstance(child, Token):
                # Sprint 12: Handle single ID as loop index (filtered loop case)
                if child.type == "ID" and indices is None:
                    indices = (str(child),)
                continue  # Skip SEMI and other tokens

            if isinstance(child, Tree):
                if child.data == "id_list":
                    # Extract loop indices
                    indices = _id_list(child)
                elif child.data == "loop_body":
                    # Sprint 12: Unwrap loop_body to extract individual statements
                    for stmt in child.children:
                        if isinstance(stmt, Tree):
                            body_stmts.append(stmt)
                else:
                    # This is a statement in the loop body
                    # Expected statement types: assign_stmt, solve_stmt, option_stmt, etc.
                    # All exec_stmt types from grammar are valid here
                    body_stmts.append(child)

        if indices is None:
            raise self._error("Malformed loop statement: missing indices", node)

        # Create LoopStatement and store in model
        location = self._extract_source_location(node)
        loop_stmt = LoopStatement(
            indices=indices,
            body_stmts=body_stmts,
            location=location,
        )

        # Sprint 11: Mock/store approach - just store, don't execute
        self.model.loop_statements.append(loop_stmt)

    def _handle_loop_stmt_paren(self, node: Tree) -> None:
        """Handle loop statement with double parentheses: loop((indices), ...)."""
        # Same as _handle_loop_stmt - the grammar handles the extra parens
        self._handle_loop_stmt(node)

    def _handle_loop_stmt_filtered(self, node: Tree) -> None:
        """Handle loop statement with conditional filter: loop(i$(cond), ...)."""
        # Same as _handle_loop_stmt - the filter condition is in the tree
        self._handle_loop_stmt(node)

    def _handle_loop_stmt_paren_filtered(self, node: Tree) -> None:
        """Handle loop statement with parens and filter: loop((i,j)$(cond), ...)."""
        # Same as _handle_loop_stmt - the grammar handles the structure
        self._handle_loop_stmt(node)

    def _handle_loop_stmt_indexed(self, node: Tree) -> None:
        """Handle loop over indexed set: loop(setname(i,j), ...)."""
        # Same as _handle_loop_stmt - indices come from id_list inside setname(...)
        self._handle_loop_stmt(node)

    def _handle_loop_stmt_indexed_filtered(self, node: Tree) -> None:
        """Handle loop over indexed set with filter: loop(setname(i,j)$(cond), ...)."""
        # Same as _handle_loop_stmt - the grammar handles the structure
        self._handle_loop_stmt(node)

    def _expand_subset_assignment(
        self,
        set_def: SetDef,
        param: ParameterDef,
        has_function_call: bool,
        expr: Expr | None,
        value: float | None,
        node: Tree | Token | None = None,
    ) -> None:
        """Expand subset assignment to all members of a set.

        Args:
            set_def: The set definition containing members to expand
            param: The parameter to assign values/expressions to
            has_function_call: True if the RHS contains function calls
            expr: The expression to assign (if has_function_call)
            value: The numeric value to assign (if not has_function_call)
            node: The AST node for error reporting
        """
        if not set_def.members:
            return

        for member in set_def.members:
            # member can be a single element or tuple for multi-dim sets
            # Multi-dim set members are stored as dot-separated strings (e.g., 'a.b')
            # Note: This assumes dots are tuple separators, not part of element names.
            # GAMS elements with literal dots (e.g., 'element.1') should be quoted
            # in the source, and our preprocessor preserves them without dots.
            if isinstance(member, tuple):
                key = member
            elif "." in member:
                # Split dot-separated member into tuple (e.g., 'nw.cc' -> ('nw', 'cc'))
                split_member = tuple(member.split("."))
                # Always validate dimension: if param.domain is empty, expect scalar (1 index)
                expected_dim = len(param.domain) if param.domain else 1
                if len(split_member) != expected_dim:
                    raise self._error(
                        f"Set member '{member}' splits into {len(split_member)} elements, "
                        f"but parameter '{param.name}' expects {expected_dim} "
                        f"index{'es' if expected_dim > 1 else ''}. "
                        "If your element name contains a dot, quote it in the source "
                        "(e.g., '\"element.1\"'). Alternatively, check that the parameter's "
                        "domain declaration matches the set member structure.",
                        node,
                    )
                key = split_member
            else:
                key = (member,)

            if has_function_call:
                param.expressions[key] = expr
            elif value is not None:
                param.values[key] = value

    def _handle_assign(self, node: Tree) -> None:
        # Expected structure: lvalue, ASSIGN token, expression
        if len(node.children) < 3:
            raise self._error("Malformed assignment statement", node)
        lvalue_tree = node.children[0]
        expr_tree = next(
            (
                child
                for child in reversed(node.children)
                if isinstance(child, Tree) and child.data != "lvalue"
            ),
            None,
        )
        if expr_tree is None:
            raise self._error("Malformed assignment expression", node)
        if not isinstance(lvalue_tree, Tree) or lvalue_tree.data != "lvalue":
            raise self._error("Malformed assignment target", lvalue_tree)

        # Extract target first to determine domain context
        target = next(
            (child for child in lvalue_tree.children if isinstance(child, (Tree, Token))),
            None,
        )
        if target is None:
            raise self._error("Empty assignment target", lvalue_tree)

        # Sprint 11 Day 2 Extended: Extract indices from lvalue to use as domain context
        # For indexed assignments like low(n,nn) = ord(n) > ord(nn), the indices
        # n and nn should be in scope when evaluating the expression
        domain_context = ()
        if isinstance(target, Tree):
            if target.data == "symbol_indexed" and len(target.children) > 1:
                # Extract index names from the lvalue for use as free domain
                try:
                    domain_context = _extract_indices(target.children[1])
                except (AttributeError, IndexError, TypeError):
                    # If extraction fails due to malformed tree, fall back to empty domain
                    domain_context = ()
            elif target.data == "bound_indexed" and len(target.children) > 2:
                # For variable bounds, also extract indices
                try:
                    indices = _process_index_list(target.children[2])
                    # Convert to strings for domain context (extract base from IndexOffset)
                    domain_context = tuple(
                        idx if isinstance(idx, str) else idx.base for idx in indices
                    )
                except (AttributeError, IndexError, TypeError):
                    # If extraction fails due to malformed tree, fall back to empty domain
                    domain_context = ()

        # Now evaluate expression with domain context
        expr = self._expr_with_context(expr_tree, "assignment", domain_context)

        # Determine if we're assigning to a variable bound or a parameter
        is_variable_bound = isinstance(target, Tree) and target.data in (
            "bound_indexed",
            "bound_scalar",
        )

        # Sprint 10 Day 4: Check if expression contains function calls
        # If so, store as expression instead of trying to evaluate
        has_function_call = self._contains_function_call(expr)

        # Sprint 17 Day 4: Check if expression contains variable references
        # Variable references (like x.l) are runtime values that cannot be stored
        has_variable_reference = self._contains_variable_reference(expr)

        # Try to extract a constant value. If the expression is non-constant
        # (e.g., contains variable attributes like x.l or function calls), we handle specially
        # (Sprint 8 mock/store approach - we don't execute expressions)
        value = None
        try:
            value = self._extract_constant(expr, "assignment")
        except ParserSemanticError:
            # Non-constant expressions:
            # - For variable bounds with expressions: parse and continue (Sprint 10 Day 6)
            # - For parameters with function calls: store as expression (Sprint 10 Day 4)
            # - For parameters with only param refs: store as expression (Sprint 17 Day 4)
            # - For parameters with variable refs: skip (runtime values, can't store)
            # (e.g., trig.gms: xdiff = 2.66695657 - x1.l uses x1.l which is runtime)
            if is_variable_bound:
                # Variable bounds with expressions (circle.gms: a.l = (xmin + xmax)/2)
                # Parse and continue without storing (mock/store approach)
                return
            # Sprint 17 Day 4: Store parameter expressions that don't reference variables
            # This enables computed parameters like c(i,j) = f*d(i,j)/1000 to be emitted
            if has_variable_reference:
                # Expression references variable attributes - skip (runtime value)
                return
            # Expression contains only parameters/constants - store as expression
            has_function_call = True  # Treat as expression to store

        if isinstance(target, Tree):
            if target.data == "bound_indexed":
                var_name = _token_text(target.children[0])
                bound_token = target.children[1]
                # Use _process_index_list to handle i++1, i--2, etc. (Sprint 9)
                indices = (
                    _process_index_list(target.children[2]) if len(target.children) > 2 else ()
                )
                self._apply_variable_bound(var_name, bound_token, indices, value, target)
                return
            if target.data == "bound_scalar":
                var_name = _token_text(target.children[0])
                bound_token = target.children[1]
                self._apply_variable_bound(var_name, bound_token, (), value, target)
                return
            if target.data == "attr_access":
                # Handle general attribute access: var.scale, model.scaleOpt, etc.
                # This is for attributes not covered by BOUND_K (lo, up, fx, l, m)
                # For now, we parse and validate but don't store attribute values
                # (mock/store approach - similar to how we handle variable bounds with expressions)
                # Common attributes: scale, prior, stage, scaleOpt
                # Validate that the base object exists (variable, parameter, equation, or model)
                # Issue #558: Equations can also have attributes like .stage in stochastic programming
                base_name = _token_text(target.children[0])
                if (
                    base_name not in self.model.variables
                    and base_name not in self.model.params
                    and base_name not in self.model.equations
                    and base_name != self.model.declared_model
                ):
                    raise self._error(
                        f"Symbol '{base_name}' not declared as a variable, parameter, equation, or model",
                        target,
                    )
                return
            if target.data == "attr_access_indexed":
                # Handle indexed attribute access: x.stage(g), var.scale(i), etc.
                # Issue #554: Parse but don't process - stochastic programming not modeled
                # Validate that the base object exists (variable, parameter, equation, or model)
                # Issue #558: Equations can also have attributes like .stage in stochastic programming
                base_name = _token_text(target.children[0])
                if (
                    base_name not in self.model.variables
                    and base_name not in self.model.params
                    and base_name not in self.model.equations
                    and base_name != self.model.declared_model
                ):
                    raise self._error(
                        f"Symbol '{base_name}' not declared as a variable, parameter, equation, or model",
                        target,
                    )
                return
            if target.data == "symbol_indexed":
                # Handle indexed assignment: p('i1') = 10, report('x1','global') = 1, or low(n,nn) = ...
                symbol_name = _token_text(target.children[0])

                # Extract indices and any subset constraint from id_list
                indices, subset_name = (
                    _extract_indices_with_subset(target.children[1])
                    if len(target.children) > 1
                    else ((), None)
                )

                # Sprint 11 Day 2 Extended: Check if this is a set assignment
                if symbol_name in self.model.sets:
                    # Set assignment like: low(n,nn) = ord(n) > ord(nn)
                    # For now, parse and validate but don't store (mock/store approach)
                    # The expression has already been validated with the correct domain context
                    return

                # Validate parameter exists
                if symbol_name not in self.model.params:
                    raise self._error(f"Parameter '{symbol_name}' not declared", target)

                param = self.model.params[symbol_name]

                # Handle subset indexing: dist(arc(n,np)) = value
                # Expand to all members of the subset
                if subset_name is not None:
                    if subset_name not in self.model.sets:
                        raise self._error(
                            f"Set '{subset_name}' used in subset indexing is not declared",
                            target,
                        )
                    subset_def = self.model.sets[subset_name]
                    self._expand_subset_assignment(
                        subset_def, param, has_function_call, expr, value, target
                    )
                    return

                # Handle simple subset name as index: flag(sub) where sub is a subset of i
                # Check if a single index is actually a subset name that should be expanded
                # Sprint 17 Day 4: Only expand for constant values, not for expressions
                # For expressions like gplus(c) = gibbs(c) + log(...), we store once with index
                # and emit as a single GAMS assignment statement
                if subset_name is None and len(indices) == 1 and indices[0] in self.model.sets:
                    simple_subset = self.model.sets[indices[0]]
                    # Note: SetDef currently doesn't store domain information (the parent set).
                    # E.g., for "Set sub(i) / b, c /", we only store name='sub', members=['b','c'].
                    # Future enhancement: add domain field to SetDef to enable validation that
                    # subset domain is compatible with parameter domain (e.g., reject p(sub_j)
                    # when p is defined over domain i but sub_j is a subset of j).
                    # Check if this set has members to expand (only for constant values)
                    if simple_subset.members and not has_function_call and value is not None:
                        self._expand_subset_assignment(
                            simple_subset, param, has_function_call, expr, value, target
                        )
                        return
                    # For expressions, fall through to store with the index name

                # Only validate index count if the parameter has an explicit domain declaration.
                # For parameters without an explicit domain, index count is not validated.
                # (e.g., mathopt1.gms: Parameter report; report('x1','global') = 1;)
                if len(param.domain) > 0 and len(indices) != len(param.domain):
                    index_word = "index" if len(param.domain) == 1 else "indices"
                    raise self._parse_error(
                        f"Parameter '{symbol_name}' expects {len(param.domain)} {index_word}, got {len(indices)}",
                        target,
                        suggestion=f"Provide exactly {len(param.domain)} {index_word} to match the parameter declaration",
                    )

                # Sprint 10 Day 4: Store expression if it contains function calls, otherwise store value
                if has_function_call:
                    param.expressions[tuple(indices)] = expr
                elif value is not None:
                    param.values[tuple(indices)] = value
                return
        elif isinstance(target, Token):
            name = _token_text(target)
            if name in self.model.params:
                param = self.model.params[name]
                if param.domain:
                    raise self._error(
                        f"Assignment to parameter '{name}' requires indices for domain {param.domain}",
                        target,
                    )
                # Sprint 10 Day 4: Store expression if it contains function calls, otherwise store value
                if has_function_call:
                    param.expressions[()] = expr
                elif value is not None:
                    param.values[()] = value
                return
            if name in self.model.variables:
                var = self.model.variables[name]
                var.lo = var.up = var.fx = value
                return
        raise self._parse_error(
            "Unsupported assignment target",
            lvalue_tree,
            suggestion="Assignment targets must be scalars, parameters, or variable attributes (e.g., x.l, x.lo, x.up)",
        )

    def _handle_conditional_assign(self, node: Tree) -> None:
        """Handle conditional assignments: lhs$(condition) = rhs;

        This transforms the conditional assignment into an if statement:
        lhs$(condition) = rhs  =>  if(condition, lhs = rhs;)

        Expected structure: lvalue, DOLLAR, "(", expr (condition), ")", ASSIGN, expr (rhs)
        """
        if len(node.children) < 4:
            raise self._error("Malformed conditional assignment statement", node)

        # Extract components: lvalue, condition expr, rhs expr
        lvalue_tree = node.children[0]
        if not isinstance(lvalue_tree, Tree) or lvalue_tree.data != "lvalue":
            raise self._error("Malformed assignment target", lvalue_tree)

        # Find the condition expression (after DOLLAR and before ASSIGN)
        # Find the rhs expression (after ASSIGN)
        condition_expr = None
        rhs_expr = None
        found_dollar = False
        found_assign = False

        for child in node.children[1:]:
            if isinstance(child, Token):
                if child.type == "DOLLAR":
                    found_dollar = True
                elif child.type == "ASSIGN":
                    found_assign = True
            elif isinstance(child, Tree):
                if found_dollar and not found_assign:
                    # This is the condition expression
                    condition_expr = child
                elif found_assign:
                    # This is the RHS expression
                    rhs_expr = child

        if condition_expr is None:
            raise self._error("Missing condition in conditional assignment", node)
        if rhs_expr is None:
            raise self._error("Missing right-hand side in conditional assignment", node)

        # Transform to if statement: create an if node and handle it
        # We create a synthetic Tree node for the if statement
        # Structure: if_stmt with condition and a body containing the assignment

        # Create a synthetic assignment node (without the condition)
        assign_node = Tree("assign", [lvalue_tree, Token("ASSIGN", ":="), rhs_expr])

        # Now create the if statement node
        # The if_stmt grammar expects: IF_K "(" expr "," exec_stmt+ elseif_clause* else_clause? ")" SEMI
        # We'll create a simpler conditional statement and store it

        # Extract indices from lvalue for domain context (same as in _handle_assign)
        target = next(
            (child for child in lvalue_tree.children if isinstance(child, (Tree, Token))),
            None,
        )
        domain_context = ()
        if isinstance(target, Tree):
            if target.data == "symbol_indexed" and len(target.children) > 1:
                try:
                    domain_context = _extract_indices(target.children[1])
                except (AttributeError, IndexError, TypeError):
                    domain_context = ()
            elif target.data == "bound_indexed" and len(target.children) > 2:
                try:
                    indices = _process_index_list(target.children[2])
                    domain_context = tuple(
                        idx if isinstance(idx, str) else idx.base for idx in indices
                    )
                except (AttributeError, IndexError, TypeError):
                    domain_context = ()

        # Evaluate the condition expression with domain context
        condition = self._expr_with_context(
            condition_expr, "conditional assignment", domain_context
        )

        # Create a ConditionalStatement and store it
        location = self._extract_source_location(node)
        cond_stmt = ConditionalStatement(
            condition=condition,
            then_stmts=[assign_node],  # Store the assignment node to be processed
            elseif_clauses=[],
            else_stmts=[],
            location=location,
        )

        # Store the conditional statement
        self.model.conditional_statements.append(cond_stmt)

        # Also process the assignment itself so variables/parameters are updated
        # This handles the actual data assignment in the "then" branch
        self._handle_assign(assign_node)

    def _expr(self, node: Tree | Token, free_domain: tuple[str, ...]) -> Expr:
        if isinstance(node, Token):
            if node.type == "NUMBER":
                return self._attach_domain(Const(float(node)), free_domain)
            if node.type == "ID":
                name = _token_text(node)
                if name.lower() in {"inf", "+inf"}:
                    return self._attach_domain(Const(math.inf), free_domain)
                if name.lower() == "-inf":
                    return self._attach_domain(Const(-math.inf), free_domain)
                return self._make_symbol(name, (), free_domain, node)
            raise self._error(
                f"Unexpected token in expression: {node!r}. "
                f"Expected a variable, parameter, number, or function call.",
                node,
            )

        if node.data in _WRAPPER_NODES:
            for child in node.children:
                if isinstance(child, (Tree, Token)):
                    if isinstance(child, Token) and child.type == "SEMI":
                        continue
                    return self._expr(child, free_domain)
            raise self._error(
                f"Empty expression node: {node.data}. Expected an expression inside the wrapper.",
                node,
            )

        if node.data == "symbol_plain":
            name_token = node.children[0]
            name = _token_text(name_token)
            if name.lower() in {"inf", "+inf"}:
                return self._attach_domain(Const(math.inf), free_domain)
            if name.lower() == "-inf":
                return self._attach_domain(Const(-math.inf), free_domain)
            return self._make_symbol(name, (), free_domain, name_token)

        if node.data == "symbol_indexed":
            name = _token_text(node.children[0])
            indices_node = node.children[1]
            if name in self.model.variables or name in self.model.params:
                # Use _process_index_list to handle i++1, i--2, etc. (Sprint 9)
                indices = _process_index_list(indices_node)
                return self._make_symbol(name, indices, free_domain, node)
            if name.lower() in _FUNCTION_NAMES:
                args: list[Expr] = []
                for child in indices_node.children:
                    if isinstance(child, Token):
                        args.append(self._make_symbol(_token_text(child), (), free_domain, child))
                    elif isinstance(child, Tree):
                        args.append(self._expr(child, free_domain))
                expr = Call(name.lower(), tuple(args))
                return self._attach_domain(expr, self._merge_domains(args, node))
            # Fallback for unknown symbols (use _process_index_list for i++1 support)
            indices = _process_index_list(indices_node)
            return self._make_symbol(name, indices, free_domain, node)

        if node.data == "number":
            return self._attach_domain(Const(float(node.children[0])), free_domain)

        if node.data == "sum":
            # Extract base identifiers from sum_domain (supporting lag/lead operators, tuples, and conditionals)
            sum_domain_node = node.children[1]

            # Handle sum_domain which can be index_spec or tuple_domain
            condition_expr = None
            if sum_domain_node.data == "tuple_domain":
                # Tuple notation: sum{(i,j), expr} or sum{(i,j)$cond, expr}
                index_spec_node = sum_domain_node.children[0]
            else:
                # Plain sum_domain -> index_spec
                index_spec_node = sum_domain_node.children[0]

            # index_spec contains: index_list (DOLLAR expr)?
            index_list_node = index_spec_node.children[0]

            # Check if there's a conditional (DOLLAR expr)
            if len(index_spec_node.children) > 1:
                # There's a conditional: extract it
                # Children are: index_list, DOLLAR token, expr
                condition_expr = self._expr(index_spec_node.children[2], free_domain)

            if index_list_node.data == "id_list":
                # Legacy path for old grammar (if any old tests use it)
                indices = _id_list(index_list_node)
            else:
                # New path: extract base identifiers from index_list
                indices = tuple(_extract_domain_indices(index_list_node))
            self._ensure_sets(indices, "sum indices", node)

            # Expand multi-dimensional set indices to their domain components
            # E.g., sum(a, ...) where a(n,n) expands body_domain to include (n, n)
            # This allows expressions like dist(a) to be expanded to dist(n, np)
            expanded_indices: list[str] = []
            for idx in indices:
                if isinstance(idx, str) and idx in self.model.sets:
                    set_def = self.model.sets[idx]
                    # Check if this set has a multi-dimensional domain (members are set names)
                    members_are_domain_sets = (
                        set_def.members is not None
                        and len(set_def.members) > 1
                        and all(
                            m in self.model.sets or m in self.model.aliases for m in set_def.members
                        )
                    )
                    # Check if members are multi-dimensional values (e.g., 'a.b')
                    members_are_multidim = (
                        set_def.members is not None
                        and len(set_def.members) > 0
                        and any("." in m for m in set_def.members)
                    )
                    if members_are_domain_sets:
                        # Expand to domain indices: a(n,n) -> (n, n)
                        expanded_indices.extend(set_def.members)
                    elif members_are_multidim:
                        # HEURISTIC: Infer domain indices for multi-dimensional sets with
                        # dot-separated element values (e.g., arc with members ['nw.w', 'e.cc']).
                        #
                        # Assumptions:
                        # 1. Only 2D sets are expanded; higher dimensions fall back to original
                        # 2. The base set has simple (non-dot) element names
                        # 3. There exists an alias of that base set for the second dimension
                        # 4. The pattern follows common GAMS convention: (base_set, alias)
                        #
                        # Limitations:
                        # - May not find correct expansion if multiple candidate base sets exist
                        # - Does not handle 3D+ sets
                        # - Relies on alias existence; fails gracefully if no alias found
                        #
                        # If expansion fails, the original index is kept and downstream
                        # processing may raise a more specific error.
                        first_member = set_def.members[0]
                        dim = len(first_member.split("."))
                        if dim == 2:
                            # Look for aliases of a base set with simple elements
                            base_sets = [
                                s
                                for s in self.model.sets
                                if s != idx and len(self.model.sets[s].members) > 0
                            ]
                            # Find a base set that has simple elements (not dots)
                            for bs_name in base_sets:
                                bs = self.model.sets[bs_name]
                                if bs.members and not any("." in m for m in bs.members):
                                    # Found a base set, check if there's an alias
                                    alias_name = None
                                    for a_name, a_def in self.model.aliases.items():
                                        if a_def.target == bs_name:
                                            alias_name = a_name
                                            break
                                    if alias_name:
                                        expanded_indices.extend([bs_name, alias_name])
                                        break
                            else:
                                # No suitable expansion found, keep original
                                expanded_indices.append(idx)
                        else:
                            # Non-2D sets: keep original (no heuristic for 3D+)
                            expanded_indices.append(idx)
                    else:
                        expanded_indices.append(idx)
                else:
                    expanded_indices.append(idx)

            # Only sum out indices that are NEW (not already in free_domain)
            # Indices already in free_domain are bound from outer scope, not summed out
            # Example: sum(arc(np,n), q(np,n)) in equation test(n)
            #   - n is in free_domain (outer equation index), stays in result
            #   - np is new to sum, gets summed out
            new_sum_indices = set(expanded_indices) - set(free_domain)
            remaining_domain = tuple(d for d in free_domain if d not in new_sum_indices)
            # Build body_domain without duplicates, preserving order
            # Use a set to track seen indices and filter duplicates
            seen: set[str] = set()
            body_domain = tuple(
                x
                for x in list(expanded_indices) + list(remaining_domain)
                if not (x in seen or seen.add(x))  # type: ignore[func-returns-value]
            )

            # If there's a condition, evaluate it in the body domain
            if condition_expr is not None:
                # Re-evaluate condition in body_domain since it may reference sum indices
                condition_expr = self._expr(index_spec_node.children[2], body_domain)

            body = self._expr(node.children[2], body_domain)

            # Apply condition by multiplying: sum(i$cond, expr) => sum(i, cond * expr)
            if condition_expr is not None:
                body = Binary("*", condition_expr, body)

            expr = Sum(indices, body)
            object.__setattr__(expr, "sum_indices", tuple(indices))
            return self._attach_domain(expr, remaining_domain)

        # Sprint 17 Day 6: Added prod handler (same logic as sum, but creates Prod)
        if node.data == "prod":
            # Extract base identifiers from sum_domain (reusing sum_domain rule)
            sum_domain_node = node.children[1]

            # Handle sum_domain which can be index_spec or tuple_domain
            # Note: Both cases extract the first child - tuple_domain wraps index_spec
            condition_expr = None
            index_spec_node = sum_domain_node.children[0]

            index_list_node = index_spec_node.children[0]

            # Check if there's a conditional (DOLLAR expr)
            if len(index_spec_node.children) > 1:
                condition_expr = self._expr(index_spec_node.children[2], free_domain)

            if index_list_node.data == "id_list":
                indices = _id_list(index_list_node)
            else:
                indices = tuple(_extract_domain_indices(index_list_node))
            self._ensure_sets(indices, "prod indices", node)

            # Simplified expansion for prod (same logic as sum but condensed)
            expanded_indices: list[str] = []
            for idx in indices:
                if isinstance(idx, str) and idx in self.model.sets:
                    set_def = self.model.sets[idx]
                    members_are_domain_sets = (
                        set_def.members is not None
                        and len(set_def.members) > 1
                        and all(
                            m in self.model.sets or m in self.model.aliases for m in set_def.members
                        )
                    )
                    if members_are_domain_sets:
                        expanded_indices.extend(set_def.members)
                    else:
                        expanded_indices.append(idx)
                else:
                    expanded_indices.append(idx)

            new_prod_indices = set(expanded_indices) - set(free_domain)
            remaining_domain = tuple(d for d in free_domain if d not in new_prod_indices)
            seen: set[str] = set()
            body_domain = tuple(
                x
                for x in list(expanded_indices) + list(remaining_domain)
                if not (x in seen or seen.add(x))  # type: ignore[func-returns-value]
            )

            if condition_expr is not None:
                condition_expr = self._expr(index_spec_node.children[2], body_domain)

            body = self._expr(node.children[2], body_domain)

            if condition_expr is not None:
                body = Binary("*", condition_expr, body)

            expr = Prod(indices, body)
            object.__setattr__(expr, "prod_indices", tuple(indices))
            return self._attach_domain(expr, remaining_domain)

        if node.data == "binop":
            left = self._expr(node.children[0], free_domain)
            op_token = node.children[1]
            right = self._expr(node.children[2], free_domain)
            expr = Binary(self._extract_operator(op_token), left, right)
            return self._attach_domain(expr, self._merge_domains([left, right], node))

        if node.data == "dollar_cond" or node.data == "dollar_cond_paren":
            # Dollar conditional: value_expr$condition or value_expr$(condition)
            # Evaluates to value_expr if condition is non-zero, otherwise 0
            # Both forms: children are [value_expr, DOLLAR_token, condition]
            # (Lark discards tokens defined as string literals in the grammar, such as "(" and ")",
            # from the parse tree; terminals defined without quotes like DOLLAR are included)
            value_expr = self._expr(node.children[0], free_domain)
            condition = self._expr(node.children[2], free_domain)
            from src.ir.ast import DollarConditional

            expr = DollarConditional(value_expr, condition)
            return self._attach_domain(expr, self._merge_domains([value_expr, condition], node))

        if node.data == "unaryop":
            op_token = node.children[0]
            operand = self._expr(node.children[1], free_domain)
            expr = Unary(self._extract_operator(op_token), operand)
            return self._attach_domain(expr, self._expr_domain(operand))

        if node.data == "funccall":
            func_tree = node.children[0]
            func_name = _token_text(func_tree.children[0]).lower()
            args: list[Expr] = []

            if len(func_tree.children) > 1:
                arg_list = func_tree.children[1]

                # Sprint 10 Day 6 / Sprint 11 Day 2: Handle aggregation functions with set iterators
                # Aggregation functions like smin(i, x(i)) or smin(low(n,nn), ...) have domain spec as first arg
                if func_name in _AGGREGATION_FUNCTIONS and len(arg_list.children) >= 1:
                    # First argument is the domain specification (creates local scope)
                    first_arg = arg_list.children[0]

                    # Sprint 11 Day 2: Handle subset domain like low(n,nn)
                    if isinstance(first_arg, Tree) and first_arg.data == "symbol_indexed":
                        # This is a subset domain like 'low(n,nn)' in smin(low(n,nn), expr)
                        # Extract the set name and indices
                        set_name = _token_text(first_arg.children[0])

                        # Check if this is a known set
                        if set_name in self.model.sets:
                            # Extract the indices from the subset reference
                            indices_node = first_arg.children[1]
                            indices = (
                                _extract_indices(indices_node)
                                if len(first_arg.children) > 1
                                else ()
                            )

                            # Add the subset reference as a SymbolRef for the aggregation
                            # (represents the domain being aggregated over)
                            args.append(SymbolRef(set_name))

                            # Remaining arguments are parsed with the subset indices in scope
                            # E.g., smin(low(n,nn), expr) - expr can reference n and nn
                            extended_domain = free_domain + indices
                            for child in arg_list.children[1:]:
                                if isinstance(child, (Tree, Token)):
                                    args.append(self._expr(child, extended_domain))

                            # Return with free_domain (the subset indices are bound)
                            expr = Call(func_name, tuple(args))
                            return self._attach_domain(expr, free_domain)

                    # Check if first arg is a simple symbol (symbol_plain tree with single ID token)
                    if (
                        isinstance(first_arg, Tree)
                        and first_arg.data == "symbol_plain"
                        and len(first_arg.children) == 1
                        and isinstance(first_arg.children[0], Token)
                    ):
                        # This is a set iterator like 'i' in smin(i, x(i))
                        # We parse it as a SymbolRef without validation
                        iterator_name = _token_text(first_arg.children[0])
                        args.append(SymbolRef(iterator_name))

                        # Remaining arguments are parsed with the iterator in the local scope
                        # Add the iterator to free_domain so it's recognized as a valid symbol
                        extended_domain = free_domain + (iterator_name,)
                        for child in arg_list.children[1:]:
                            if isinstance(child, (Tree, Token)):
                                args.append(self._expr(child, extended_domain))

                        # For aggregation functions with iterators, return with free_domain
                        # (the iterator is bound, so the result domain is the outer scope)
                        expr = Call(func_name, tuple(args))
                        return self._attach_domain(expr, free_domain)
                    else:
                        # Not a simple symbol or subset, parse all args normally
                        for child in arg_list.children:
                            if isinstance(child, (Tree, Token)):
                                args.append(self._expr(child, free_domain))
                else:
                    # Regular function call - parse all arguments normally
                    for child in arg_list.children:
                        if isinstance(child, (Tree, Token)):
                            args.append(self._expr(child, free_domain))

            expr = Call(func_name, tuple(args))
            return self._attach_domain(expr, self._merge_domains(args, node))

        # Support variable/equation attribute access in expressions (e.g., x1.l, eq.m)
        # Sprint 9 Day 6: Added equation attribute support
        if node.data == "bound_scalar":
            name = _token_text(node.children[0])
            attribute = _token_text(
                node.children[1]
            ).lower()  # Extract attribute (.l, .m, .lo, .up)

            # Check if this is an equation reference (Sprint 9 Day 6)
            if name in self.model.equations:
                # Return EquationRef for equation attributes
                from .ast import EquationRef

                expr = EquationRef(name=name, indices=(), attribute=attribute)
                return self._attach_domain(expr, free_domain)

            # Otherwise, treat as variable reference (Sprint 8 behavior)
            return self._make_symbol(name, (), free_domain, node)

        if node.data == "bound_indexed":
            name = _token_text(node.children[0])
            attribute = _token_text(node.children[1]).lower()  # Extract attribute
            # Use _process_index_list to handle i++1, i--2, etc. (Sprint 9)
            indices = _process_index_list(node.children[2]) if len(node.children) > 2 else ()

            # Check if this is an equation reference (Sprint 9 Day 6)
            if name in self.model.equations:
                # Return EquationRef for indexed equation attributes
                from .ast import EquationRef

                # Convert indices to strings (EquationRef uses tuple[str | IndexOffset, ...])
                expr = EquationRef(name=name, indices=indices, attribute=attribute)
                return self._attach_domain(expr, free_domain)

            # Otherwise, treat as variable reference (Sprint 8 behavior)
            return self._make_symbol(name, indices, free_domain, node)

        # Support compile-time constants: %identifier% or %path.to.value%
        if node.data == "compile_const":
            from .ast import CompileTimeConstant

            # Extract the dotted path from compile_time_const node
            # compile_time_const has compile_const_path child
            const_node = node.children[0]
            path = []
            for child in const_node.children:
                if isinstance(child, Token):
                    path.append(_token_text(child))
            expr = CompileTimeConstant(path=tuple(path))
            return self._attach_domain(expr, free_domain)

        # Support bracket expressions: [expr] is treated like (expr)
        if node.data == "bracket_expr":
            # Just unwrap and process the inner expression
            if len(node.children) > 0:
                return self._expr(node.children[0], free_domain)
            raise self._error("Empty bracket expression", node)

        raise self._error(
            f"Unsupported expression type: {node.data}. "
            f"This may be a parser bug or unsupported GAMS syntax. "
            f"Supported: variables, parameters, numbers, operators (+, -, *, /, ^), functions (sqrt, exp, log, etc.), sum().",
            node,
        )

    def _expr_with_context(self, node: Tree | Token, context: str, domain: Sequence[str]) -> Expr:
        domain_tuple = tuple(domain)
        self._context_stack.append((context, node, domain_tuple))
        try:
            return self._expr(node, domain_tuple)
        finally:
            self._context_stack.pop()

    def _current_context(self) -> str:
        return self._current_context_description()

    def _current_context_description(self) -> str:
        if not self._context_stack:
            return "expression"
        return " -> ".join(desc for desc, _, _ in self._context_stack)

    def _error(self, message: str, node: Tree | Token | None = None) -> ParserSemanticError:
        context_desc = self._current_context_description()
        if context_desc:
            message = f"{message} [context: {context_desc}]"
        if self._context_stack:
            current_domain = self._context_stack[-1][2]
            if current_domain:
                message = f"{message} [domain: {current_domain}]"
        line, column = self._node_position(node)
        if line is None and self._context_stack:
            for _, ctx_node, _ in reversed(self._context_stack):
                line, column = self._node_position(ctx_node)
                if line is not None:
                    break
        return ParserSemanticError(message, line, column)

    def _parse_error(
        self,
        message: str,
        node: Tree | Token | None = None,
        suggestion: str | None = None,
    ) -> ParseError:
        """Create a ParseError with location and source context extracted from node.

        This is similar to _error() but returns a ParseError with enhanced formatting
        including source line display and caret pointer.

        Args:
            message: Error message describing the problem
            node: Parse tree node or token to extract location from
            suggestion: Optional suggestion for how to fix the error

        Returns:
            ParseError with location, source context, and suggestion

        Example:
            raise self._parse_error(
                "Indexed assignments are not supported yet",
                target,
                suggestion="Use scalar assignment: x.l = 5"
            )
        """
        # Add context information to message
        context_desc = self._current_context_description()
        if context_desc:
            message = f"{message} [context: {context_desc}]"
        if self._context_stack:
            current_domain = self._context_stack[-1][2]
            if current_domain:
                message = f"{message} [domain: {current_domain}]"

        # Extract line/column from node
        line, column = self._node_position(node)
        if line is None and self._context_stack:
            for _, ctx_node, _ in reversed(self._context_stack):
                line, column = self._node_position(ctx_node)
                if line is not None:
                    break

        # Extract source line for display
        source_line = None
        if self.source and line is not None:
            source_lines = self.source.split("\n")
            if 1 <= line <= len(source_lines):
                source_line = source_lines[line - 1].lstrip()
                # Adjust column for stripped whitespace
                original_line = source_lines[line - 1]
                stripped_count = len(original_line) - len(original_line.lstrip())
                if column is not None:
                    column = max(1, column - stripped_count)

        return ParseError(
            message=message,
            line=line,
            column=column,
            source_line=source_line,
            suggestion=suggestion,
        )

    def _node_position(self, node: Tree | Token | None) -> tuple[int | None, int | None]:
        if node is None:
            return (None, None)
        if isinstance(node, Token):
            return getattr(node, "line", None), getattr(node, "column", None)
        if isinstance(node, Tree):
            meta = getattr(node, "meta", None)
            if meta is not None:
                line = getattr(meta, "line", None)
                column = getattr(meta, "column", None)
                if line is not None:
                    return line, column
            for child in node.children:
                line, column = self._node_position(child)
                if line is not None:
                    return line, column
        return (None, None)

    def _extract_source_location(
        self, node: Tree | Token | None, filename: str | None = None
    ) -> SourceLocation | None:
        """Extract source location from a parse tree node.

        Args:
            node: Parse tree node or token to extract location from
            filename: Optional filename to include in source location

        Returns:
            SourceLocation instance if line/column info is available, None otherwise
        """
        line, column = self._node_position(node)
        if line is not None and column is not None:
            return SourceLocation(line=line, column=column, filename=filename)
        return None

    def _make_symbol(
        self,
        name: str,
        indices: Sequence[str | IndexOffset | SubsetIndex],
        free_domain: Sequence[str],
        node: Tree | Token | None = None,
    ) -> Expr:
        # Sprint 11 Day 2 Extended: Expand set references in indices
        # When we see dist(low) where low is a 2D set, expand to dist(n,nn)
        #
        # Complex logic needed:
        # 1. If idx is a set with multi-dimensional domain, expand it
        #    (e.g., low in dist(low) where low has domain (n,n))
        # 2. BUT if idx is in free_domain AND is a base set (like 'n'), don't expand
        #    (e.g., n in point(n,d) where n is a domain variable)
        expanded_indices: list[str] = []
        for idx in indices:
            # Handle SubsetIndex objects by flattening to inner indices
            # This allows expressions like x = dist.l(low(n,nn)) to work
            if isinstance(idx, SubsetIndex):
                expanded_indices.extend(idx.indices)
                continue
            # Skip IndexOffset objects - only expand plain string identifiers
            if isinstance(idx, str) and idx in self.model.sets:
                set_def = self.model.sets[idx]
                # Check if this set's members are domain indices (other sets) or element values
                # E.g., low(n,n) has members ['n', 'n'] - domain indices (should expand)
                # E.g., d has members ['x', 'y'] - element values (should NOT expand)
                # Note: Single-member sets are not expanded even if the member is a set,
                # as they represent simple domain references rather than multi-dimensional expansions
                members_are_sets = (
                    set_def.members is not None
                    and len(set_def.members) > 0
                    and all(m in self.model.sets for m in set_def.members)
                )

                # Sprint 17 Day 5: Check if this is a subset with multi-dimensional domain
                # E.g., arc(n,n) without explicit members has domain=('n', 'n')
                # When q(arc) is used, expand to q(n, n) using domain
                has_multidim_domain = set_def.domain is not None and len(set_def.domain) > 1

                # Issue #428: Check if members are multi-dimensional (dot-separated values)
                # E.g., arc(n,n) / a.b, b.c / has members ['a.b', 'b.c'] - 2D element values
                # When q(arc) is used, expand to q(np, n) using free_domain indices
                members_are_multidim = (
                    set_def.members is not None
                    and len(set_def.members) > 0
                    and any("." in m for m in set_def.members)
                )

                # Check if this is a multi-dimensional set reference with set-based domain
                if members_are_sets and len(set_def.members) > 1:
                    # Multi-dimensional set with domain indices - always expand
                    # E.g., low(n,n) expands to (n, n)
                    expanded_indices.extend(set_def.members)
                elif has_multidim_domain and free_domain:
                    # Sprint 17 Day 5: Multi-dimensional subset via domain field
                    # E.g., arc(n,n) without members expands using domain
                    # Use free_domain to map to actual indices
                    dim = len(set_def.domain)
                    if len(free_domain) >= dim:
                        expanded_indices.extend(free_domain[-dim:])
                    else:
                        # Fall back to domain itself
                        expanded_indices.extend(set_def.domain)
                elif members_are_multidim and free_domain:
                    # Multi-dimensional set with element values (e.g., arc with members 'a.b')
                    # Infer dimensionality from first member and expand using free_domain
                    first_member = set_def.members[0]
                    dim = len(first_member.split("."))
                    if dim > 1 and len(free_domain) >= dim:
                        # HEURISTIC: Use the last 'dim' indices from free_domain
                        # E.g., free_domain = ('n', 'np'), dim = 2 -> expand to ('n', 'np')
                        # Or free_domain = ('np', 'n'), dim = 2 -> expand to ('np', 'n')
                        #
                        # Limitation: This assumes free_domain order matches the set's domain.
                        # A more robust solution would store domain info in SetDef during parsing.
                        # For now, this works for common patterns like sum(arc(np,n), q(arc)).
                        expanded_indices.extend(free_domain[-dim:])
                    else:
                        # Can't expand, keep as-is
                        expanded_indices.append(idx)
                elif idx in free_domain:
                    # Set that's in domain - don't expand
                    # E.g., n in point(n,d) where domain is (n,nn)
                    expanded_indices.append(idx)
                else:
                    # Set with element values or single-dim not in domain - don't expand
                    expanded_indices.append(idx)
            else:
                # Not a set reference, keep as-is
                expanded_indices.append(idx)

        idx_tuple = tuple(expanded_indices)
        if name in self.model.variables:
            expected = self.model.variables[name].domain
            if len(expected) != len(idx_tuple):
                index_word = "index" if len(expected) == 1 else "indices"
                raise self._error(
                    f"Variable '{name}' expects {len(expected)} {index_word} but received {len(idx_tuple)}",
                    node,
                )
            expr = VarRef(name, idx_tuple)
            object.__setattr__(expr, "symbol_domain", expected)
            object.__setattr__(expr, "index_values", idx_tuple)
            return self._attach_domain(expr, free_domain)
        if name in self.model.params:
            expected = self.model.params[name].domain
            # In GAMS, validation is skipped only for parameters with empty domains (true scalars),
            # allowing them to be implicitly expanded when used with indices. For parameters with an
            # explicit domain, the number of indices must match the domain length.
            if len(expected) > 0 and len(expected) != len(idx_tuple):
                index_word = "index" if len(expected) == 1 else "indices"
                raise self._error(
                    f"Parameter '{name}' expects {len(expected)} {index_word} but received {len(idx_tuple)}",
                    node,
                )
            expr = ParamRef(name, idx_tuple)
            object.__setattr__(expr, "symbol_domain", expected)
            object.__setattr__(expr, "index_values", idx_tuple)
            return self._attach_domain(expr, free_domain)
        # Check if it's a domain index (e.g., 'i' in a condition like ord(i))
        if not idx_tuple and name in free_domain:
            # It's a reference to a domain index variable
            return self._attach_domain(SymbolRef(name), free_domain)
        # Issue #560: Check if it's an alias that's in free_domain
        # When an alias like 'hp' is used as a sum domain (sum(hp$..., expr)),
        # references to 'hp' inside the expression should resolve correctly
        if not idx_tuple and name in self.model.aliases:
            # It's an alias - treat as a domain index reference
            return self._attach_domain(SymbolRef(name), free_domain)
        # Check if it's a GAMS predefined constant (yes, no, inf, eps, na, undf)
        # These are case-insensitive
        name_lower = name.lower()
        if not idx_tuple and name_lower in _PREDEFINED_CONSTANTS:
            return self._attach_domain(Const(_PREDEFINED_CONSTANTS[name_lower]), free_domain)
        # Issue #428: Check if it's a set membership test (e.g., rn(n) in a condition)
        # In GAMS, set(index) in a conditional context returns 1 if index is in set, 0 otherwise
        # Issue #560: Also check aliases - they can be used like sets
        if (name in self.model.sets or name in self.model.aliases) and idx_tuple:
            # Set membership test - use dedicated SetMembershipTest node
            # This represents the boolean check "is idx_tuple in set 'name'"
            from src.ir.ast import SetMembershipTest

            # Convert indices: domain variables become SymbolRef, literals become Const strings
            # Note: All indices in a set membership test should typically be domain variables.
            # If an index is not in free_domain, treat it as a literal element name.
            index_exprs: list[Expr] = []
            for i in idx_tuple:
                if isinstance(i, str) and i in free_domain:
                    index_exprs.append(SymbolRef(i))
                elif isinstance(i, str):
                    # Treat as literal element name - wrap in SymbolRef for consistency
                    # This handles cases like rn('a') where 'a' is a literal element
                    index_exprs.append(SymbolRef(i))
                else:
                    # IndexOffset or other non-string types
                    index_exprs.append(SymbolRef(str(i)))

            expr = SetMembershipTest(name, tuple(index_exprs))
            return self._attach_domain(expr, free_domain)
        if idx_tuple:
            raise self._parse_error(
                f"Undefined symbol '{name}' with indices {idx_tuple} referenced",
                node,
                suggestion=f"Declare '{name}' as a variable, parameter, or set before using it",
            )
        raise self._parse_error(
            f"Undefined symbol '{name}' referenced",
            node,
            suggestion=f"Declare '{name}' as a variable, parameter, or set before using it",
        )

    def _parse_param_decl(self, node: Tree) -> ParameterDef:
        name: str | None = None
        domain: tuple[str, ...] = ()
        data_node: Tree | None = None
        for child in node.children:
            if isinstance(child, Token):
                if child.type == "ID" and name is None:
                    name = _token_text(child)
            elif isinstance(child, Tree):
                if child.data == "id_list" and not domain:
                    domain = _id_list(child)
                elif child.data == "id_or_wildcard_list" and not domain:
                    domain = _id_or_wildcard_list(child)
                elif child.data == "param_data_items":
                    data_node = child
        if name is None:
            raise self._error("Parameter declaration missing name", node)
        param = ParameterDef(name=name, domain=domain)
        if domain:
            self._ensure_sets(domain, f"parameter '{name}' domain", node)
        if data_node is not None:
            param.values.update(self._parse_param_data_items(data_node, domain, name))
        return param

    def _parse_param_data_items(
        self, node: Tree, domain: tuple[str, ...], param_name: str
    ) -> dict[tuple[str, ...], float]:
        # Multi-dimensional parameter data is now supported via dotted notation (e.g., i1.j1)
        # Sprint 16 Day 7: Also supports tuple expansion (e.g., (route-1,route-2) 13)
        values: dict[tuple[str, ...], float] = {}
        for child in node.children:
            if not isinstance(child, Tree):
                continue
            if child.data == "param_data_tuple_expansion":
                # Sprint 16 Day 7: Handle tuple expansion like (route-1,route-2) 13
                # Expands to route-1=13, route-2=13
                # Issue #564: Also handles special values like (h1,h2) na
                # Note: Tuple expansion is only supported for 1-D parameters.
                # Multi-dimensional parameters require explicit dotted notation (e.g., i.j value).
                elements = self._parse_set_element_id_list(child.children[0])
                value_node = child.children[-1]
                value = self._parse_param_data_value(value_node)
                # Validate domain dimensionality before processing elements
                if len(domain) == 0:
                    raise self._error(
                        f"Parameter '{param_name}' tuple expansion syntax (elem1,elem2) requires a 1-D parameter domain, "
                        f"but '{param_name}' is scalar (no domain)",
                        child,
                    )
                elif len(domain) > 1:
                    raise self._error(
                        f"Parameter '{param_name}' tuple expansion syntax (elem1,elem2) requires a 1-D parameter domain, "
                        f"but '{param_name}' has {len(domain)}-D domain {domain}",
                        child,
                    )
                # First, validate all elements against the domain without mutating `values`
                for elem in elements:
                    self._verify_member_in_domain(param_name, domain[0], elem, child)
                # Only after successful validation, update `values` for all elements
                for elem in elements:
                    key_tuple = (elem,)
                    values[key_tuple] = value
            elif child.data == "param_data_range_expansion":
                # Issue #563: Handle range expansion like (ne2*ne5) 0
                # Expands to ne2=0, ne3=0, ne4=0, ne5=0
                # Issue #564: Also handles special values like (ne2*ne5) na
                if len(domain) != 1:
                    raise self._error(
                        f"Parameter '{param_name}' range expansion only supported for 1-D parameters",
                        child,
                    )
                range_expr_node = child.children[0]
                value_node = child.children[-1]
                value = self._parse_param_data_value(value_node)

                # Extract the two range bounds from range_expr
                bounds = [
                    node.children[0]
                    for node in range_expr_node.children
                    if isinstance(node, Tree) and node.data == "range_bound"
                ]
                if len(bounds) != 2:
                    raise self._error(
                        f"Range expression requires exactly two bounds, got {len(bounds)}",
                        child,
                    )
                start_bound = _token_text(bounds[0])
                end_bound = _token_text(bounds[1])

                # Expand range using the set membership
                expanded_members = self._expand_range_in_set(
                    start_bound, end_bound, domain[0], child
                )
                for member in expanded_members:
                    key_tuple = (member,)
                    values[key_tuple] = value
            elif child.data == "param_data_scalar":
                key = self._parse_data_indices(child.children[0])
                value_token = child.children[-1]
                value = float(_token_text(value_token))

                # Check if this is a range expression (e.g., 'a*c 10')
                if len(key) == 3 and key[0] == "__range__":
                    # Range notation: expand to multiple entries
                    if len(domain) != 1:
                        raise self._error(
                            f"Parameter '{param_name}' range notation only supported for 1-D parameters",
                            child,
                        )
                    range_start, range_end = key[1], key[2]
                    expanded_members = self._expand_range_in_set(
                        range_start, range_end, domain[0], child
                    )
                    for member in expanded_members:
                        values[(member,)] = value
                else:
                    # Standard scalar data
                    key_tuple: tuple[str, ...] = tuple(key) if domain else ()
                    if len(key_tuple) != len(domain):
                        raise self._error(
                            f"Parameter '{param_name}' data index mismatch: expected {len(domain)} dims, got {len(key_tuple)}",
                            child,
                        )
                    if domain:
                        for idx, set_name in zip(key_tuple, domain, strict=True):
                            # Skip wildcard domains - they accept any element
                            if set_name == "*":
                                continue
                            self._verify_member_in_domain(param_name, set_name, idx, child)
                    values[key_tuple] = value
            elif child.data == "param_data_matrix_row":
                row_indices = self._parse_data_indices(child.children[0])
                # Explicitly disallow range notation in matrix row indices
                if len(row_indices) == 3 and row_indices[0] == "__range__":
                    raise self._error(
                        f"Parameter '{param_name}' range notation not supported in table/matrix row indices",
                        child,
                    )
                number_tokens = list(
                    child.scan_values(lambda v: isinstance(v, Token) and v.type == "NUMBER")
                )
                values_list = [float(_token_text(tok)) for tok in number_tokens]
                if len(domain) != len(row_indices) + 1:
                    raise self._error(
                        f"Parameter '{param_name}' table row index mismatch",
                        child,
                    )
                set_prefix = domain[:-1]
                if len(set_prefix) != len(row_indices):
                    raise self._error(
                        f"Parameter '{param_name}' table indices do not match domain",
                        child,
                    )
                for idx_symbol, set_name in zip(row_indices, set_prefix, strict=True):
                    self._verify_member_in_domain(param_name, set_name, idx_symbol, child)
                last_set = domain[-1]
                domain_set = self._resolve_set_def(last_set, node=child)
                if not domain_set or len(domain_set.members) < len(values_list):
                    raise self._error(
                        f"Parameter '{param_name}' table has more columns than members in set '{last_set}'",
                        child,
                    )
                for col_value, col_member in zip(values_list, domain_set.members, strict=True):
                    key_tuple = tuple(row_indices + [col_member])
                    values[key_tuple] = col_value
        return values

    def _parse_set_element_id_list(self, node: Tree) -> list[str]:
        """Parse a set_element_id_list node for tuple expansion.

        Sprint 16 Day 7: Added for parsing (elem1,elem2) syntax in param data.
        Returns list of element identifiers from the comma-separated list.
        Handles both SET_ELEMENT_ID and STRING tokens (preprocessor quotes hyphenated IDs).
        Note: _token_text() already strips quotes from STRING tokens.
        """
        elements = []
        for child in node.children:
            if isinstance(child, Tree) and child.data == "set_element_id_or_string":
                # Extract the token from the wrapper node
                for token in child.children:
                    if isinstance(token, Token):
                        elements.append(_token_text(token))
            elif isinstance(child, Token) and child.type in ("SET_ELEMENT_ID", "STRING"):
                elements.append(_token_text(child))
        return elements

    def _parse_data_indices(self, node: Tree | Token) -> list[str]:
        """Parse data indices from a data_indices node.

        Returns a list of index strings. For simple indices like 'a' or 'a.b',
        returns ['a'] or ['a', 'b']. For range expressions like 'a*c', returns
        a special format ['__range__', 'a', 'c'] that the caller must expand.
        """
        if isinstance(node, Tree):
            # Check if this is a data_indices node containing a range_expr
            if node.data == "data_indices":
                for child in node.children:
                    if isinstance(child, Tree) and child.data == "range_expr":
                        # Extract range bounds from range_expr
                        bounds = []
                        for bound_node in child.children:
                            if isinstance(bound_node, Tree) and bound_node.data == "range_bound":
                                for tok in bound_node.children:
                                    if isinstance(tok, Token):
                                        bounds.append(_token_text(tok))
                            elif isinstance(bound_node, Token) and bound_node.type != "TIMES":
                                bounds.append(_token_text(bound_node))
                        if len(bounds) == 2:
                            # Return special marker for range that caller will expand
                            return ["__range__", bounds[0], bounds[1]]
                        else:
                            # Unexpected number of bounds - raise error for debugging
                            raise self._error(
                                f"Expected 2 bounds in range_expr, got {len(bounds)}: {bounds}",
                                child,
                            )
            # Standard case: extract tokens directly
            # Issue #555: Handle data_index wrapper nodes and STRING tokens
            result = []
            for child in node.children:
                if isinstance(child, Token) and child.type in (
                    "ID",
                    "NUMBER",
                    "SET_ELEMENT_ID",
                    "STRING",
                ):
                    result.append(_token_text(child))
                elif isinstance(child, Tree) and child.data == "data_index":
                    # Extract the token from the data_index wrapper
                    for tok in child.children:
                        if isinstance(tok, Token):
                            result.append(_token_text(tok))
            return result
        return [_token_text(node)]

    def _expand_range_in_set(
        self, start: str, end: str, set_name: str, node: Tree | Token
    ) -> list[str]:
        """Expand a range like 'a*c' to ['a', 'b', 'c'] using set membership.

        Args:
            start: Start of range (e.g., 'foulds3')
            end: End of range (e.g., 'foulds5')
            set_name: Name of the set to look up members from
            node: Parse tree node for error reporting

        Returns:
            List of set members from start to end inclusive

        Raises:
            ParserSemanticError if start/end not found in set or end before start
        """
        set_def = self._resolve_set_def(set_name, node=node)
        if not set_def:
            raise self._error(f"Cannot expand range: set '{set_name}' not found", node)

        members = set_def.members
        try:
            start_idx = members.index(start)
        except ValueError as err:
            raise self._error(f"Range start '{start}' not found in set '{set_name}'", node) from err
        try:
            end_idx = members.index(end)
        except ValueError as err:
            raise self._error(f"Range end '{end}' not found in set '{set_name}'", node) from err

        if end_idx < start_idx:
            raise self._error(
                f"Range end '{end}' comes before start '{start}' in set '{set_name}'",
                node,
            )

        return members[start_idx : end_idx + 1]

    def _attach_domain(self, expr: Expr, domain: Sequence[str]) -> Expr:
        domain_tuple = tuple(domain)
        object.__setattr__(expr, "domain", domain_tuple)
        object.__setattr__(expr, "free_domain", domain_tuple)
        object.__setattr__(expr, "rank", len(domain_tuple))
        return expr

    def _expr_domain(self, expr: Expr) -> tuple[str, ...]:
        return getattr(expr, "domain", ())

    def _merge_domains(self, exprs: Sequence[Expr], node: Tree | Token) -> tuple[str, ...]:
        domains = [self._expr_domain(expr) for expr in exprs if expr is not None]
        if not domains:
            return ()
        first = domains[0]
        for d in domains[1:]:
            if d != first:
                raise self._error("Expression domain mismatch", node)
        return first

    def _contains_function_call(self, expr: Expr) -> bool:
        """Check if an expression contains any function calls (recursively).

        Sprint 10 Day 4: Used to detect when parameter assignments contain function calls
        that should be stored as expressions rather than evaluated.
        """
        if isinstance(expr, Call):
            return True
        if isinstance(expr, (Binary, Unary)):
            # Check children recursively
            for child in expr.children():
                if self._contains_function_call(child):
                    return True
        if isinstance(expr, Sum):
            # Check the summation body
            if self._contains_function_call(expr.body):
                return True
        if isinstance(expr, IndexOffset):
            # Check the offset expression recursively
            if self._contains_function_call(expr.offset):
                return True
        # Check for function calls in indices of reference nodes
        if isinstance(expr, (VarRef, ParamRef)):
            for idx in expr.indices:
                if isinstance(idx, IndexOffset) and self._contains_function_call(idx):
                    return True
        # Check EquationRef and MultiplierRef if they're being used
        # These are imported locally in some contexts, so we check type name
        if type(expr).__name__ in ("EquationRef", "MultiplierRef"):
            for idx in expr.indices:  # type: ignore[attr-defined]
                if isinstance(idx, IndexOffset) and self._contains_function_call(idx):
                    return True
        return False

    def _contains_variable_reference(self, expr: Expr) -> bool:
        """Check if an expression contains any variable references (recursively).

        Sprint 17 Day 4: Used to detect when parameter assignments contain variable
        references (like x.l or x(i)) which are runtime values that cannot be stored
        as computed parameter expressions.

        Expressions that only contain parameter references (like f*d(i,j)/1000) can be
        stored and emitted as GAMS assignment statements.
        """
        if isinstance(expr, VarRef):
            # VarRef itself is a variable reference. Also check if its indices contain
            # variable references inside IndexOffset expressions (e.g., x(i + y.l)).
            for idx in expr.indices:
                if isinstance(idx, IndexOffset) and self._contains_variable_reference(idx):
                    return True
            return True
        if isinstance(expr, (Binary, Unary)):
            # Check children recursively
            for child in expr.children():
                if self._contains_variable_reference(child):
                    return True
        if isinstance(expr, Sum):
            # Check the summation body
            if self._contains_variable_reference(expr.body):
                return True
        if isinstance(expr, IndexOffset):
            # Check the offset expression recursively
            if self._contains_variable_reference(expr.offset):
                return True
        if isinstance(expr, Call):
            # Check function call arguments for variable references (e.g., log(x.l + 5))
            for arg in expr.args:
                if self._contains_variable_reference(arg):
                    return True
        # ParamRef is OK - it's a parameter, not a variable, but its indices may
        # contain variable references inside IndexOffset (e.g., d(i+x.l, j)).
        # Note: indices can be strings (e.g., "i", "j") or IndexOffset expressions.
        if isinstance(expr, ParamRef):
            for idx in expr.indices:
                if isinstance(idx, IndexOffset) and self._contains_variable_reference(idx):
                    return True
        # DollarConditional has value_expr and condition that may contain variable refs
        if isinstance(expr, DollarConditional):
            if self._contains_variable_reference(expr.value_expr):
                return True
            if self._contains_variable_reference(expr.condition):
                return True
        # SetMembershipTest indices may contain variable references
        if isinstance(expr, SetMembershipTest):
            for idx in expr.indices:
                if self._contains_variable_reference(idx):
                    return True
        # EquationRef (eq.m, eq.l) and MultiplierRef are runtime values like variables
        if isinstance(expr, (EquationRef, MultiplierRef)):
            return True
        return False

    def _extract_constant(self, expr: Expr, context: str) -> float:
        if isinstance(expr, Const):
            return float(expr.value)
        if isinstance(expr, Unary) and expr.op == "-" and isinstance(expr.child, Const):
            return -float(expr.child.value)
        if isinstance(expr, Unary) and expr.op == "+" and isinstance(expr.child, Const):
            return float(expr.child.value)
        # Handle predefined scalar parameters (pi, inf, eps, na) used as constants
        if isinstance(expr, ParamRef) and not expr.indices:
            param = self.model.params.get(expr.name)
            if param and not param.domain and () in param.values:
                return float(param.values[()])
        # Handle -inf for negative infinity (Unary minus on ParamRef)
        if isinstance(expr, Unary) and expr.op == "-" and isinstance(expr.child, ParamRef):
            param_ref = expr.child
            if not param_ref.indices:
                param = self.model.params.get(param_ref.name)
                if param and not param.domain and () in param.values:
                    return -float(param.values[()])
        raise self._error(f"Assignments must use numeric constants; got {expr!r} in {context}")

    def _apply_variable_bound(
        self,
        name: str,
        bound_token: Token | str,
        indices: Sequence[str],
        value: float,
        node: Tree | Token,
    ) -> None:
        if name not in self.model.variables:
            raise self._error(
                f"Bounds reference unknown variable '{name}'",
                node,
            )
        var = self.model.variables[name]
        idx_tuple = tuple(indices)
        bound_kind = (
            bound_token.lower()
            if isinstance(bound_token, str)
            else _token_text(bound_token).lower()
        )

        if var.domain:
            if not idx_tuple:
                raise self._error(
                    f"Variable '{name}' has indices {var.domain}; bounds must specify them",
                    node,
                )
            # Sprint 11 Day 2: Try to expand indices, but if sets have no members yet,
            # use mock/store approach (parse and continue without storing)
            try:
                index_tuples = self._expand_variable_indices(var, idx_tuple, name, node)
            except ParserSemanticError as e:
                # If expansion fails because sets have no members, just return
                # (mock/store approach - parse but don't store bounds)
                if "has no explicit members" in str(e):
                    return
                # Other errors should still be raised
                raise
        else:
            if idx_tuple:
                raise self._error(
                    f"Variable '{name}' is scalar; indexed bounds are not allowed",
                    node,
                )
            index_tuples = [()]

        for key in index_tuples:
            self._set_bound_value(var, name, key, value, bound_kind, node)

    def _set_bound_value(
        self,
        var: VariableDef,
        var_name: str,
        key: tuple[str, ...],
        value: float,
        bound_kind: str,
        node: Tree | Token | None = None,
    ) -> None:
        # Currently supported variable attributes (bound modifiers):
        #   "lo" (lower bound), "up" (upper bound), "fx" (fixed), "l" (level/initial value), "m" (marginal/dual value)
        # Additional GAMS attributes exist (e.g., ".prior", ".scale") but are not yet
        # implemented in the grammar or parser. This implementation focuses on the most
        # commonly used attributes needed to unblock GAMSLib models.
        label_map = {"lo": "lower", "up": "upper", "fx": "fixed", "l": "level", "m": "marginal"}
        map_attrs = {"lo": "lo_map", "up": "up_map", "fx": "fx_map", "l": "l_map", "m": "m_map"}
        scalar_attrs = {"lo": "lo", "up": "up", "fx": "fx", "l": "l", "m": "m"}
        label = label_map.get(bound_kind, bound_kind)
        index_hint = f" at indices {key}" if key else ""

        if math.isinf(value):
            if bound_kind == "lo" and value < 0:
                return
            if bound_kind == "up" and value > 0:
                return
            if bound_kind == "fx":
                raise self._error(
                    f"Fixed bound for variable '{var_name}' cannot be infinite",
                    node,
                )
            if bound_kind == "l":
                raise self._error(
                    f"Level (initial value) for variable '{var_name}' cannot be infinite",
                    node,
                )
            if bound_kind == "m":
                raise self._error(
                    f"Marginal (dual value) for variable '{var_name}' cannot be infinite",
                    node,
                )
            # For other cases (e.g., lo = +inf), treat like regular value

        if bound_kind not in map_attrs:
            raise self._error(
                f"Unknown bound modifier '{bound_kind}' for variable '{var_name}'",
                node,
            )

        if key:
            storage = getattr(var, map_attrs[bound_kind])
            existing = storage.get(key)
            if existing is not None and existing != value:
                raise self._error(
                    f"Conflicting {label} bound for variable '{var_name}'{index_hint}",
                    node,
                )
            storage[key] = value
        else:
            scalar_attr = scalar_attrs[bound_kind]
            existing = getattr(var, scalar_attr)
            if existing is not None and existing != value:
                raise self._error(
                    f"Conflicting {label} bound for variable '{var_name}'",
                    node,
                )
            setattr(var, scalar_attr, value)

    def _extract_operator(self, node: Tree | Token) -> str:
        if isinstance(node, Token):
            return node.value
        if isinstance(node, Tree):
            if node.children:
                return self._extract_operator(node.children[0])
            data = node.data
            if isinstance(data, Token):
                return data.value
            if isinstance(data, str):
                return data
        raise self._error("Unable to determine operator token", node)

    def _register_alias(
        self,
        alias: str,
        target: str,
        universe: str | None,
        node: Tree | None = None,
    ) -> None:
        if alias in self.model.sets or alias in self.model.aliases:
            raise self._error(
                f"Alias '{alias}' duplicates an existing set or alias",
                node,
            )
        self._ensure_set_exists(target, f"alias '{alias}' target", node)
        if universe is not None:
            self._ensure_set_exists(universe, f"alias '{alias}' universe", node)
        self.model.add_alias(AliasDef(name=alias, target=target, universe=universe))

    def _ensure_set_exists(
        self,
        name: str,
        context: str,
        node: Tree | Token | None = None,
    ) -> None:
        if self._resolve_set_def(name, node=node) is None:
            raise self._error(
                f"Unknown set or alias '{name}' referenced in {context}",
                node,
            )

    def _ensure_sets(
        self,
        names: Sequence[str],
        context: str,
        node: Tree | Token | None = None,
    ) -> None:
        for name in names:
            # Skip wildcard domains (used in table declarations)
            if name == "*":
                continue
            self._ensure_set_exists(name, context, node)

    def _resolve_set_def(
        self,
        name: str,
        seen: set[str] | None = None,
        node: Tree | Token | None = None,
    ) -> SetDef | None:
        if name in self.model.sets:
            return self.model.sets[name]
        alias = self.model.aliases.get(name)
        if alias:
            if seen is None:
                seen = set()
            if name in seen:
                raise self._error(f"Alias cycle detected involving '{name}'", node)
            seen.add(name)
            return self._resolve_set_def(alias.target, seen, node)
        return None

    def _verify_member_in_domain(
        self,
        param_name: str,
        set_name: str,
        member: str,
        node: Tree | Token | None = None,
    ) -> None:
        set_def = self._resolve_set_def(set_name, node=node)
        if set_def is None:
            raise self._error(
                f"Unknown set '{set_name}' referenced in parameter '{param_name}' data",
                node,
            )
        # Issue #435: Case-insensitive comparison for GAMS identifiers
        # Cache lowercase members on the SetDef instance for efficiency
        if set_def.members:
            members_lower = getattr(set_def, "_members_lower", None)
            if members_lower is None:
                members_lower = {m.lower() for m in set_def.members}
                set_def._members_lower = members_lower  # type: ignore[attr-defined]
            if member.lower() not in members_lower:
                raise self._error(
                    f"Parameter '{param_name}' references member '{member}' not present in set '{set_name}'",
                    node,
                )

    def _expand_variable_indices(
        self,
        var: VariableDef,
        index_symbols: Sequence[str | IndexOffset | SubsetIndex],
        var_name: str,
        node: Tree | Token | None = None,
    ) -> list[tuple[str, ...]]:
        # Sprint 12 Issue #455: Handle SubsetIndex for bounds like f.lo(aij(as,i,j))
        # When we have a single SubsetIndex, its inner indices provide the actual indices
        # for the variable's domain (e.g., aij(as,i,j) provides 3 indices for f(a,i,j))
        #
        # For SubsetIndex, we use the mock/skip approach:
        # - Validate that the index count matches the variable's domain
        # - Skip strict member validation since subsets may not have explicit members
        # - Return empty list to indicate bounds should be accepted without storing

        # Check for multiple SubsetIndex objects - not supported
        subset_count = sum(1 for s in index_symbols if isinstance(s, SubsetIndex))
        if subset_count > 1:
            raise self._error(
                f"Multiple subset indexing in variable bounds is not supported for variable '{var_name}'",
                node,
            )

        # Explicitly reject mixing SubsetIndex with other index types
        if subset_count > 0 and len(index_symbols) > 1:
            raise self._error(
                "Cannot mix subset indexing with other indices in variable bounds",
                node,
            )

        if len(index_symbols) == 1 and isinstance(index_symbols[0], SubsetIndex):
            subset_idx = index_symbols[0]
            # Validate that the subset name refers to a declared set
            if self._resolve_set_def(subset_idx.subset_name, node=node) is None:
                raise self._error(
                    f"Subset '{subset_idx.subset_name}' in variable bounds is not a declared set",
                    node,
                )
            # Validate index count matches variable domain
            if len(subset_idx.indices) != len(var.domain):
                index_word = "index" if len(var.domain) == 1 else "indices"
                raise self._error(
                    f"Variable '{var_name}' bounds expect {len(var.domain)} {index_word} but subset indexing provided {len(subset_idx.indices)}",
                    node,
                )
            # Mock/skip: Accept the bounds without full semantic validation
            # We can't fully expand subset-indexed bounds without complete set membership data
            return []

        if len(index_symbols) != len(var.domain):
            index_word = "index" if len(var.domain) == 1 else "indices"
            raise self._error(
                f"Variable '{var_name}' bounds expect {len(var.domain)} {index_word} but received {len(index_symbols)}",
                node,
            )
        member_lists: list[list[str]] = []
        for symbol, domain_name in zip(index_symbols, var.domain, strict=True):
            domain_set = self._resolve_set_def(domain_name, node=node)
            if domain_set is None:
                raise self._error(
                    f"Variable '{var_name}' references unknown domain set '{domain_name}'",
                    node,
                )

            # Early check: domain must have members for expansion
            if not domain_set.members:
                raise self._error(
                    f"Cannot expand bounds for variable '{var_name}' because set '{domain_name}' has no explicit members",
                    node,
                )

            # Check if symbol is a string (set name or literal)
            # If it's an IndexOffset or other non-string type, use all domain members
            if isinstance(symbol, str):
                resolved_symbol_set = self._resolve_set_def(symbol, node=node)
                if resolved_symbol_set is not None:
                    # Symbol is a set/alias name - validate and use its members
                    if domain_set.members and resolved_symbol_set.members:
                        if set(resolved_symbol_set.members) - set(domain_set.members):
                            raise self._error(
                                f"Alias '{symbol}' for variable '{var_name}' does not match domain '{domain_name}'",
                                node,
                            )
                    member_lists.append(domain_set.members)
                else:
                    # Symbol is a literal value (e.g., "1", "2", "pellets")
                    # Strip quotes - validate matching quotes at both ends
                    if len(symbol) >= 2 and (symbol[0] in ("'", '"') or symbol[-1] in ("'", '"')):
                        # At least one quote found - validate they match
                        if symbol[0] in ("'", '"') and symbol[-1] in ("'", '"'):
                            if symbol[0] == symbol[-1]:
                                literal_value = symbol[1:-1]
                            else:
                                raise self._error(
                                    f"Mismatched quotes in literal index '{symbol}' for variable '{var_name}' in domain '{domain_name}'",
                                    node,
                                )
                        else:
                            raise self._error(
                                f"Unmatched quote in literal index '{symbol}' for variable '{var_name}' in domain '{domain_name}'",
                                node,
                            )
                    else:
                        literal_value = symbol

                    if literal_value not in domain_set.members:
                        raise self._error(
                            f"Literal index '{literal_value}' not in domain set '{domain_name}' with members {domain_set.members}",
                            node,
                        )

                    # Use only the single literal value
                    member_lists.append([literal_value])
            else:
                # Symbol is not a string (e.g., IndexOffset like i++1)
                # Expand to all domain members (original behavior)
                member_lists.append(domain_set.members)
        return [tuple(comb) for comb in product(*member_lists)]

    def _validate(self) -> None:
        for alias_name, alias in self.model.aliases.items():
            self._ensure_set_exists(alias.target, f"alias '{alias_name}' target")
            if alias.universe is not None:
                self._ensure_set_exists(alias.universe, f"alias '{alias_name}' universe")

        for param in self.model.params.values():
            self._ensure_sets(param.domain, f"parameter '{param.name}' domain")

        for var in self.model.variables.values():
            self._ensure_sets(var.domain, f"variable '{var.name}' domain")

        for equation in self.model.equations.values():
            self._ensure_sets(equation.domain, f"equation '{equation.name}' domain")

        if self.model.model_equations and not self.model.model_uses_all:
            for eq_name in self.model.model_equations:
                if eq_name not in self.model.equations:
                    raise self._error(f"Model references unknown equation '{eq_name}'")

        # Note: We don't validate that model_name matches declared_model because:
        # 1. Multi-model declarations can declare multiple models, but we only store the first
        # 2. GAMS allows solving any declared model, not just the first one
        # 3. Model declarations and solve statements are independent in GAMS

        if self.model.objective is not None:
            objvar = self.model.objective.objvar
            if objvar not in self.model.variables:
                raise self._error(f"Objective references variable '{objvar}' which is not declared")

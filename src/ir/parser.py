"""Parser utilities that turn the grammar output into ModelIR structures."""

from __future__ import annotations

import math
import re
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from functools import lru_cache
from itertools import product
from pathlib import Path
from typing import ClassVar

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
from .preprocessor import (
    expand_multi_segment_tuple_row_labels,
    expand_tuple_only_table_rows,
    join_multiline_table_row_parens,
    normalize_double_commas,
    normalize_multi_line_continuations,
    normalize_special_identifiers,
    preprocess_gams_file,
)
from .symbols import (
    AliasDef,
    ConditionalStatement,
    EquationDef,
    LoopStatement,
    ObjSense,
    OptionStatement,
    ParameterDef,
    Rel,
    SetAssignment,
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
    "SOS1_K": VarKind.SOS1,
    "SOS2_K": VarKind.SOS2,
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
    # Issue #612: Normalize multi-line continuations to add missing commas.
    # This handles GAMS syntax where set/parameter members on separate lines
    # don't require explicit commas, e.g.:
    #   Set tw / (jan,feb).wet
    #            (mar,apr).dry /;
    # NOTE: The same normalization is also performed in `preprocess_gams_file()`.
    # It is intentionally duplicated here so that callers which invoke `parse_text`
    # directly on raw GAMS source (bypassing preprocessing) still get correct
    # handling of multi-line data blocks.
    source = normalize_multi_line_continuations(source)

    # Issue #565: Normalize double commas to single commas before parsing.
    # This handles GAMS visual alignment syntax like: Set l / a,, b /;.
    # NOTE: The same normalization is also performed in `preprocess_gams_file()`.
    # It is intentionally duplicated here so that callers which invoke `parse_text`
    # directly on raw GAMS source (bypassing preprocessing) still get correct
    # handling of visual-alignment double commas.
    source = normalize_double_commas(source)

    # Issue #665: Quote identifiers with special characters (-, +) in data blocks.
    # This handles identifiers like "20-bond-wt", "light-ind", "food+agr" in
    # Set/Parameter/Table declarations and data. Without quoting, these get
    # misinterpreted as arithmetic expressions.
    # NOTE: This normalization is also performed in `_preprocess_content()` (called
    # by `preprocess_gams_file()`). The duplication is intentional: file-based
    # parsing uses `preprocess_gams_file()` → `parse_text()`, while test code and
    # direct API users may call `parse_text()` directly with raw GAMS source.
    # Both paths must normalize special identifiers for correct parsing.
    source = normalize_special_identifiers(source)

    # Sprint 20 Day 8: Join multi-line parenthesized table row labels onto one line.
    # Must run before expand_tuple_only_table_rows.
    source = join_multiline_table_row_parens(source)

    # Day 8: Expand (a,b,c) tuple-only row labels in tables to individual rows.
    # Must run after normalize_special_identifiers.
    source = expand_tuple_only_table_rows(source)

    # Day 9: Expand multi-segment tuple/range row labels: a.(b,c).d, a.b.(c*e), etc.
    # Must run after expand_tuple_only_table_rows (Step 15b).
    source = expand_multi_segment_tuple_row_labels(source)

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
    """Extract text from a token, stripping quotes from STRING and escaped ID tokens.

    PR #658: Also strips leading/trailing whitespace from string content
    to handle cases like '"rating  "' → 'rating'.

    Issue #665: Also handles quoted ID tokens (escaped identifiers like '20-bond-wt')
    which are lexed as ID tokens via the ESCAPED pattern in the grammar.
    For escaped identifiers, we preserve inner whitespace as part of the name
    since GAMS quoted identifiers can legally contain spaces.
    """
    value = str(token)
    if len(value) >= 2:
        if token.type == "STRING":
            return value[1:-1].strip()
        # ID tokens can also be quoted via ESCAPED pattern (e.g., '20-bond-wt').
        # For escaped identifiers, preserve inner whitespace as part of the name.
        if token.type == "ID" and (
            (value[0] == "'" and value[-1] == "'") or (value[0] == '"' and value[-1] == '"')
        ):
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
    """Strip quotes from ID tokens (e.g., 'i1', \"cost%\" → i1, cost%).

    PR #658: Also strips leading/trailing whitespace from element labels
    to handle cases like 'rating  ' → 'rating'.
    """
    value = str(token)
    if token.type == "ID" and len(value) >= 2:
        if (value[0] == "'" and value[-1] == "'") or (value[0] == '"' and value[-1] == '"'):
            return value[1:-1].strip()
    return value.strip()


def _strip_quotes_from_indices(indices: tuple[str, ...]) -> tuple[str, ...]:
    """Strip quotes from index strings for storing in param.values.

    Sprint 18 Day 2: Indices may contain quotes that were preserved for expression
    emission (e.g., '"revenue"'). For value storage, we need canonical element
    names without quotes.

    PR #658: Also strips leading/trailing whitespace from element labels.
    """
    result = []
    for idx in indices:
        if len(idx) >= 2:
            if (idx.startswith('"') and idx.endswith('"')) or (
                idx.startswith("'") and idx.endswith("'")
            ):
                result.append(idx[1:-1].strip())
            else:
                result.append(idx.strip())
        else:
            result.append(idx.strip())
    return tuple(result)


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
    """Extract indices from index_list for parameter assignments.

    Used for indexed parameter assignments like p('i1') where 'i1' should become i1.

    Sprint 9 Note: Now handles index_expr nodes from index_list grammar.
    Sprint 11 Day 2: Now handles index_simple and index_subset nodes.
    Only supports plain identifiers (no IndexOffset) for parameter assignments.

    Note on quoting behavior:
    - For value storage (param.values), quotes are stripped via _strip_quotes()
    - For emission context (index_string), quotes may be preserved as '"element"'
      to allow the emitter to distinguish element literals from domain variables.
      (PR #658: Updated docstring to reflect quoting behavior)
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
                # Sprint 18 Day 2: Preserve quotes for element literals
                # PR #658: Strip whitespace from inside quotes
                text = str(child.children[0])
                if text.startswith("'") and text.endswith("'"):
                    indices.append(f'"{text[1:-1].strip()}"')
                elif text.startswith('"') and text.endswith('"'):
                    indices.append(f'"{text[1:-1].strip()}"')
                else:
                    indices.append(text)
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


def _get_quoted_index_positions(node: Tree) -> set[int]:
    """Determine which index positions in an index_list node were originally quoted.

    In GAMS, f(j,"k2") has an unquoted j (domain-over) and a quoted "k2" (literal).
    This function inspects the AST to identify quoted positions so the domain-over
    expansion logic can skip them.

    Args:
        node: The index_list Tree node from the grammar.

    Returns:
        Set of 0-based positions that had quoted (string) tokens.
    """
    quoted: set[int] = set()
    pos = 0
    for child in node.children:
        if isinstance(child, Token):
            text = str(child)
            if text.startswith('"') or text.startswith("'"):
                quoted.add(pos)
            pos += 1
        elif isinstance(child, Tree) and child.data in (
            "index_expr",
            "index_simple",
            "index_string",
        ):
            if child.data == "index_string":
                quoted.add(pos)
            elif child.data == "index_simple" and child.children:
                token = child.children[0]
                text = str(token)
                if text.startswith('"') or text.startswith("'"):
                    quoted.add(pos)
            elif child.data == "index_expr" and len(child.children) == 1:
                token = child.children[0]
                text = str(token)
                if text.startswith('"') or text.startswith("'"):
                    quoted.add(pos)
            pos += 1
        elif isinstance(child, Tree) and child.data == "index_subset":
            # Subset indexing like arc(n,np) — count inner indices
            for subchild in child.children:
                if isinstance(subchild, Tree) and subchild.data == "index_list":
                    inner_count = sum(
                        1
                        for c in subchild.children
                        if isinstance(c, Token)
                        or (
                            isinstance(c, Tree)
                            and c.data in ("index_expr", "index_simple", "index_string")
                        )
                    )
                    pos += inner_count
                    break
    return quoted


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
            # Sprint 18 Day 2: Preserve quotes for element literals
            token_text = str(child)
            if child.type == "ID" and len(token_text) >= 2:
                if token_text.startswith('"') and token_text.endswith('"'):
                    indices.append(token_text)  # Already double-quoted
                elif token_text.startswith("'") and token_text.endswith("'"):
                    indices.append(f'"{token_text[1:-1]}"')  # Normalize to double quotes
                else:
                    indices.append(token_text)  # Unquoted identifier
            else:
                indices.append(_token_text(child))
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
                # Sprint 18 Day 2: Preserve quotes for element literals
                # If the ID token starts/ends with quotes, it's an element literal
                # (e.g., "revenue", 'total') - normalize to double quotes for emitter
                token_text = str(id_token)
                if id_token.type == "ID" and len(token_text) >= 2:
                    if token_text.startswith('"') and token_text.endswith('"'):
                        # Already double-quoted - preserve as-is
                        indices.append(token_text)
                    elif token_text.startswith("'") and token_text.endswith("'"):
                        # Single-quoted - normalize to double quotes
                        indices.append(f'"{token_text[1:-1]}"')
                    else:
                        # Unquoted identifier - use as-is (domain variable)
                        indices.append(token_text)
                else:
                    indices.append(_token_text(id_token))
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
                # Sprint 18 Day 2: Preserve quotes for element literals
                # PR #658: Strip whitespace from inside quotes
                text = str(child.children[0])
                if text.startswith("'") and text.endswith("'"):
                    indices.append(f'"{text[1:-1].strip()}"')
                elif text.startswith('"') and text.endswith('"'):
                    indices.append(f'"{text[1:-1].strip()}"')
                else:
                    indices.append(text)
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


def _process_index_expr(
    index_node: Tree,
    expr_fn: Callable[[Tree], Expr] | None = None,
) -> str | IndexOffset | SubsetIndex:
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
    # Sprint 18 Day 2: Preserve quotes so emitter knows these are element literals
    # This fixes GAMS Error 120 where unquoted element labels like 'revenue'
    # are misinterpreted as undefined domain variables
    if index_node.data == "index_string":
        string_token = index_node.children[0]
        # Keep quotes around element literals - emitter's _quote_indices will normalize
        text = str(string_token)
        # Normalize to double quotes for consistency
        # PR #658: Strip whitespace from inside quotes (e.g., '"rating  "' → '"rating"')
        if text.startswith("'") and text.endswith("'"):
            return f'"{text[1:-1].strip()}"'
        elif text.startswith('"') and text.endswith('"'):
            return f'"{text[1:-1].strip()}"'
        return text  # Preserve as-is

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
                    # Sprint 18 Day 2: Preserve quotes for element literals
                    # PR #658: Strip whitespace from inside quotes
                    text = str(child.children[0])
                    if text.startswith("'") and text.endswith("'"):
                        inner_indices.append(f'"{text[1:-1].strip()}"')
                    elif text.startswith('"') and text.endswith('"'):
                        inner_indices.append(f'"{text[1:-1].strip()}"')
                    else:
                        inner_indices.append(text)
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
    token_str = str(base_token)

    # PR #658: For quoted IDs (element literals), preserve quotes but strip whitespace
    # E.g., '"rating  "' → '"rating"'
    if base_token.type == "ID" and len(token_str) >= 2:
        if token_str.startswith('"') and token_str.endswith('"'):
            base = f'"{token_str[1:-1].strip()}"'
        elif token_str.startswith("'") and token_str.endswith("'"):
            base = f'"{token_str[1:-1].strip()}"'  # Normalize to double quotes
        else:
            base = _token_text(base_token)
    else:
        base = _token_text(base_token)

    # No suffix? Just return the base identifier
    if len(index_node.children) == 1:
        return base

    # Has lag_lead_suffix
    # Grammar: lag_lead_suffix: CIRCULAR_LEAD offset_expr -> circular_lead
    # So suffix_node.children = [Token('CIRCULAR_LEAD', '++'), Tree('offset_number', ...)]
    # The offset_expr is the SECOND child (index 1), not the first
    suffix_node = index_node.children[1]
    offset_node = suffix_node.children[1]  # offset_expr (second child after operator token)

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
    elif offset_node.data == "offset_func":
        # Function call or indexed parameter offset: t-ord(l), t+li(k), etc.
        # Grammar: offset_func maps from either func_call or ref_indexed.
        # - func_call: wrap in synthetic funccall node for _expr() dispatch
        # - symbol_indexed (ref_indexed): pass directly to _expr()
        if expr_fn is None:
            raise ParserSemanticError(
                "offset_func requires an expr_fn to evaluate the function call; "
                "call _process_index_expr with expr_fn=lambda n: self._expr(n, domain)"
            )
        inner_node = offset_node.children[0]
        if inner_node.data == "symbol_indexed":
            # Issue #780: ref_indexed (e.g., li(k)) maps to symbol_indexed —
            # pass directly to _expr() since it handles symbol_indexed natively
            offset_expr = expr_fn(inner_node)
        else:
            # func_call: _expr() handles "funccall" whose child[0] is func_call
            funccall_node = Tree("funccall", [inner_node])
            offset_expr = expr_fn(funccall_node)
    elif offset_node.data == "offset_paren":
        # Parenthesized arithmetic offset: t-(ord(l)-1), t+(n-1), etc.
        # Grammar: offset_paren: "(" expr ")" — inner child is the expr tree
        if expr_fn is None:
            raise ParserSemanticError(
                "offset_paren requires an expr_fn to evaluate the inner expression; "
                "call _process_index_expr with expr_fn=lambda n: self._expr(n, domain)"
            )
        inner_expr_node = offset_node.children[0]
        offset_expr = expr_fn(inner_expr_node)
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


def _process_index_list(
    node: Tree,
    expr_fn: Callable[[Tree], Expr] | None = None,
) -> tuple[str | IndexOffset | SubsetIndex, ...]:
    """Process index_list from grammar (Sprint 9 Day 3, Sprint 12 Issue #455).

    Handles plain identifiers, lag/lead indexed expressions, and subset indexing.

    Args:
        node: The index_list parse tree node.
        expr_fn: Optional callable for evaluating arithmetic offset expressions
            (offset_paren). Pass ``lambda n: self._expr(n, domain)`` from an
            IRBuilder context to support offsets like ``t-(ord(l)-1)``.

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
            indices.append(_process_index_expr(child, expr_fn))
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
            domain = tuple(_id_or_wildcard_list(item.children[1]))
            # Note: desc_text is now allowed but we ignore it
            # A set with domain but no members is a subset declaration (members inherited from parent)
            self.model.add_set(SetDef(name=name, members=[], domain=domain))
        elif item.data == "set_domain_with_members":
            # Subset with explicit members: cg(genchar) / a, b, c /
            # Sprint 17 Day 5: Store domain (parent set) for subset relationships
            name = _token_text(item.children[0])
            # Extract domain from id_or_wildcard_list (the parent set(s))
            domain = tuple(_id_or_wildcard_list(item.children[1]))
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
                    # Element with inline description: SET_ELEMENT_ID STRING, STRING STRING,
                    # or NUMBER STRING. Take first token, ignore description (second token).
                    # Sprint 16 Day 7: Handle STRING STRING case (preprocessor quotes hyphenated IDs)
                    # Sprint 19 Day 1: Handle NUMBER STRING case (numeric set elements with descriptions)
                    # Note: _token_text() already strips quotes from STRING tokens
                    result.append(_token_text(child.children[0]))
                elif child.data == "set_multiword_with_desc":
                    # Sprint 20 Day 7: Multi-word set element with description
                    # e.g., "wire rod 'rolling of wire rod'" -> element "wire rod"
                    word1 = _token_text(child.children[0])
                    word2 = _token_text(child.children[1])
                    result.append(f"{word1} {word2}")
                elif child.data == "set_tuple":
                    # Issue #567: Tuple notation with optional quoted parts
                    # ID.ID, ID.STRING, STRING.ID, STRING.STRING
                    # e.g., a.b, upper.'u-egypt', 'a'.b, 'a'.'b'
                    prefix = _token_text(child.children[0])
                    suffix = _token_text(child.children[1])
                    result.append(f"{prefix}.{suffix}")
                elif child.data == "set_triple":
                    # Issue #818: Triple-dotted tuples for GUSS dictionary sets
                    # e.g., rapscenarios.scenario.'', rap.param.riskaver
                    seg1 = _token_text(child.children[0])
                    seg2 = _token_text(child.children[1])
                    seg3 = _token_text(child.children[2])
                    result.append(f"{seg1}.{seg2}.{seg3}")
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
                elif child.data == "set_tuple_cross_expansion":
                    # Day 8: Cross-product expansion: (a,b).(c,d) → a.c, a.d, b.c, b.d
                    # e.g., (1971,1974).(eng,tech,admin) or (premium,regular).(butane,sr-gas)
                    prefixes = self._parse_set_element_id_list(child.children[0])
                    suffixes = self._parse_set_element_id_list(child.children[1])
                    for prefix in prefixes:
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
                        f"Expected 'set_element', 'set_element_with_desc', 'set_multiword_with_desc', 'set_tuple', "
                        f"'set_triple', 'set_tuple_with_desc', 'set_tuple_expansion', 'set_tuple_prefix_expansion', "
                        f"'set_tuple_cross_expansion', or 'set_range'.",
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
        num_str_start = match_start.group(2)
        num_start = int(num_str_start)

        base_end = match_end.group(1)
        num_str_end = match_end.group(2)
        num_end = int(num_str_end)

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

        # Issue #782: Preserve leading-zero width from the start bound.
        # e.g. a01*a24 → a01, a02, ..., a24 (not a1, a2, ..., a24)
        width = len(num_str_start) if num_str_start.startswith("0") else 0

        # Generate symbolic range
        if width:
            return [f"{base_start}{i:0{width}d}" for i in range(num_start, num_end + 1)]
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

        # Sprint 19 Day 1: Handle tables with or without explicit domain
        # With domain: children = [ID, table_domain_list, (STRING)?, table_content+]
        # Without domain: children = [ID, (STRING)?, table_content+]
        domain_list_node = None
        if (
            len(node.children) > 1
            and isinstance(node.children[1], Tree)
            and node.children[1].data == "table_domain_list"
        ):
            domain_list_node = node.children[1]

        domain: list[str] = []

        if domain_list_node is None:
            # No explicit domain — infer wildcard domains from table structure
            domain = ["*", "*"]
        else:
            pass  # Fall through to existing domain extraction below

        for child in domain_list_node.children if domain_list_node is not None else []:
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
                        # Issue #665: Include STRING tokens as valid row labels
                        # (preprocessor quotes hyphenated identifiers like '20-bond-wt')
                        label_tokens = [
                            tok for tok in dotted_label_node.children if isinstance(tok, Token)
                        ]
                        if label_tokens:
                            # Only create row label if there are tokens
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
                    elif first_child.data == "tuple_cross_label":
                        # Day 8: Cross-product label like "(basmati,irri).(bullock,semi-mech)"
                        # Structure: tuple_cross_label -> set_element_id_list, set_element_id_list
                        prefixes = self._parse_set_element_id_list(first_child.children[0])
                        suffixes = self._parse_set_element_id_list(first_child.children[1])
                        expanded_labels = [f"{p}.{s}" for p in prefixes for s in suffixes]

                        # Get line number: scan recursively for first Token in subtree
                        first_token = next(
                            (
                                tok
                                for tok in first_child.scan_values(lambda v: isinstance(v, Token))
                            ),
                            None,
                        )
                        if first_token is not None and hasattr(first_token, "line"):
                            row_label_map[first_token.line] = expanded_labels
                    elif first_child.data == "tuple_suffix_expansion_label":
                        # Day 8: Suffix-expansion label like "sorghum.(bullock,'semi-mech')"
                        # Sprint 20 Day 7: Extended to support dotted_label prefix
                        # e.g. "wheat.bullock.standard.(heavy,january)"
                        # Structure: tuple_suffix_expansion_label -> dotted_label, set_element_id_list
                        prefix_node = first_child.children[0]  # dotted_label
                        suffix_list_node = first_child.children[1]  # set_element_id_list
                        # Extract prefix string from dotted_label (join parts with ".")
                        # dotted_label children can be Token (ID/STRING) or Tree (range_expr)
                        if isinstance(prefix_node, Tree) and prefix_node.data == "dotted_label":
                            parts: list[str] = []
                            for child_node in prefix_node.children:
                                if isinstance(child_node, Token):
                                    parts.append(_token_text(child_node))
                                elif (
                                    isinstance(child_node, Tree) and child_node.data == "range_expr"
                                ):
                                    bounds = [
                                        _token_text(b.children[0])
                                        for b in child_node.children
                                        if isinstance(b, Tree) and b.data == "range_bound"
                                    ]
                                    parts.append("*".join(bounds))
                            prefixes_for_label = [".".join(parts)] if parts else []
                        elif isinstance(prefix_node, Token):
                            prefixes_for_label = [_token_text(prefix_node)]
                        else:
                            prefixes_for_label = []
                        suffixes = self._parse_set_element_id_list(suffix_list_node)
                        expanded_labels = [f"{p}.{s}" for p in prefixes_for_label for s in suffixes]

                        # Get line number: scan recursively for first Token in subtree
                        first_token = next(
                            (
                                tok
                                for tok in first_child.scan_values(lambda v: isinstance(v, Token))
                            ),
                            None,
                        )
                        if first_token is not None and hasattr(first_token, "line"):
                            row_label_map[first_token.line] = expanded_labels
                elif isinstance(first_child, Token):
                    # Simple ID label (legacy, shouldn't happen with new grammar)
                    row_label = _token_text(first_child)
                    if hasattr(first_child, "line"):
                        row_label_map[first_child.line] = row_label

        # Collect all tokens from table_row nodes with position info
        # Note: PLUS tokens are markers and will be skipped in line grouping
        # Track row label tokens separately to avoid mis-parsing them as values
        all_tokens = []
        row_label_token_ids: set[int] = set()  # Token IDs that belong to row labels
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
                            elif (
                                isinstance(grandchild, Tree)
                                and grandchild.data == "negative_number"
                            ):
                                # Issue #704: Handle "- 0.0013" (MINUS NUMBER with space)
                                sign_token = grandchild.children[0]  # MINUS
                                num_token = grandchild.children[1]  # NUMBER
                                combined_value = _token_text(sign_token) + _token_text(num_token)
                                synthetic_token = Token(
                                    "NUMBER",
                                    combined_value,
                                    line=getattr(sign_token, "line", None),
                                    column=getattr(sign_token, "column", None),
                                )
                                all_tokens.append(synthetic_token)
                    elif child.data == "simple_label":
                        # simple_label wraps dotted_label
                        # Issue #665: Include STRING tokens for quoted row labels
                        # Track these as row label tokens to exclude from value matching
                        dotted_label_node = child.children[0]
                        for grandchild in dotted_label_node.children:
                            if isinstance(grandchild, Token):
                                all_tokens.append(grandchild)
                                row_label_token_ids.add(id(grandchild))
                    elif child.data == "tuple_label":
                        # tuple_label contains id_list and dotted_label
                        # Collect tokens from both, tracking them as row label tokens
                        for subnode in child.children:
                            if isinstance(subnode, Tree):
                                for tok in subnode.children:
                                    if isinstance(tok, Token):
                                        all_tokens.append(tok)
                                        row_label_token_ids.add(id(tok))
                    elif child.data in (
                        "tuple_cross_label",
                        "tuple_suffix_expansion_label",
                    ):
                        # Day 8: Recursively collect all tokens in the label subtree.
                        # scan_values handles arbitrarily nested Trees (range_expr etc.)
                        for tok in child.scan_values(lambda v: isinstance(v, Token)):
                            all_tokens.append(tok)
                            row_label_token_ids.add(id(tok))

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
                                    elif (
                                        isinstance(val_token, Tree)
                                        and val_token.data == "negative_number"
                                    ):
                                        # Issue #704: Handle "- 0.0013" in continuations
                                        sign_token = val_token.children[0]
                                        num_token = val_token.children[1]
                                        combined_value = _token_text(sign_token) + _token_text(
                                            num_token
                                        )
                                        synthetic_token = Token(
                                            "NUMBER",
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
                    # Heuristic: continuation lines with NUMBER tokens are likely data values,
                    # while lines with only ID/STRING tokens are likely column headers.
                    # Note: Column headers CAN be numeric (parsed later), but a continuation
                    # line of pure numbers is more likely data than header names.
                    # Issue #665: Quoted column headers may be STRING tokens or quoted ID tokens
                    has_number_tokens = any(
                        tok.type == "NUMBER" for tok in line_tokens if isinstance(tok, Token)
                    )
                    all_identifier_tokens = all(
                        tok.type in ("ID", "STRING")
                        for tok in line_tokens
                        if isinstance(tok, Token)
                    )

                    # Determine if this is a column header continuation or data continuation
                    # 1. If only one line exists (column headers), continuation must be for headers
                    # 2. Otherwise, if all identifier tokens and no numbers, it's column headers
                    if len(merged_lines) == 1:
                        is_column_header_continuation = True
                    else:
                        is_column_header_continuation = (
                            all_identifier_tokens and not has_number_tokens
                        )

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

        # Issue #713: Skip description string line if it was parsed as a table_row.
        # When a table has no explicit domain (e.g., "Table td 'target data'"),
        # the Earley parser may consume the description STRING as a row label
        # in the first table_row. Detect this: if the first line is on the same
        # line as the table name, it contains table metadata (name, domain, description)
        # — not column headers — and must be skipped.
        #
        # Two sub-cases:
        #   a) Single quoted-string token: just the description (original Issue #713 case,
        #      e.g. "Table td 'target data'" where domain token was consumed elsewhere).
        #   b) Multiple tokens: table name + domain + optional description all on one line
        #      (e.g. "Table data(*,i) 'systolic blood pressure data'" — tokens include
        #       the table name ID, domain ID, and description STRING).
        table_name_line = getattr(node.children[0], "line", None)
        first_line_num, first_line_tokens = sorted_lines[0]
        if table_name_line is not None and first_line_num == table_name_line:
            # Skip this line regardless of token count — it's the table declaration line
            if first_line_num in row_label_map:
                del row_label_map[first_line_num]
            sorted_lines = sorted_lines[1:]
            if not sorted_lines:
                self.model.add_param(ParameterDef(name=name, domain=domain, values={}))
                return
            first_line_num, first_line_tokens = sorted_lines[0]

        # Remove column header line from row_label_map if it was added
        # (column headers are parsed as a table_row, so they might have been extracted as a row label)
        if first_line_num in row_label_map:
            del row_label_map[first_line_num]

        # ISSUE_392: Detect secondary column-header lines that appear between data rows.
        # When the preprocessor removes '+' continuation markers (replacing them with spaces),
        # a GAMS table continuation line like:
        #   +   16  17  18  ...  31
        # becomes (the '+' replaced by a space to preserve column alignment):
        #       16  17  18  ...  31
        # This line has no ID row label — all tokens are NUMBER — and is therefore treated
        # as a secondary column-header line that starts a new header section, rather than
        # being merged into sorted_lines[0] (the primary column-header line).
        #
        # Detection (conservative): a non-first line is a secondary column-header line when
        # ALL its tokens are NUMBER type.  Data rows always start with an ID (the row label),
        # so a purely-numeric line cannot be a data row.
        secondary_header_indices: list[int] = []  # indices into sorted_lines to absorb
        for idx in range(1, len(sorted_lines)):
            _, line_tokens = sorted_lines[idx]
            if not line_tokens:
                continue
            if all(tok.type == "NUMBER" for tok in line_tokens if isinstance(tok, Token)):
                secondary_header_indices.append(idx)

        if secondary_header_indices:
            # Section-based processing for tables with continuation blocks.
            #
            # When the preprocessor removes '+' continuation markers, GAMS table blocks like:
            #
            #        1   2  ...  15
            #   r1  v1  v2  ... v15
            #   r2  ...
            #
            #   +   16  17  ...  31          <- '+' replaced by space; all-NUMBER line
            #   r1  v16 v17 ... v31
            #   r2  ...
            #
            # collapse into a single parse-tree row whose tokens still carry original line
            # numbers.  After grouping by line, sorted_lines has the structure above with
            # the continuation header appearing as a purely-numeric line.
            #
            # Strategy: split sorted_lines into independent sections, each containing
            # its own column-header line plus the data lines that follow it (up to the next
            # secondary header or end).  Process each section independently and accumulate
            # all values into the same `values` dict.
            #
            # Note: the section-based path uses proximity-based column matching (find the
            # nearest column header by column position) rather than the range-based matching
            # used in the standard path.  Proximity matching is necessary here because the
            # continuation preprocessor replaces '+' with a space — the token column positions
            # already reflect the final layout — so no artificial column-offset adjustment is
            # needed.  The range-based approach assumes a single merged header list with
            # non-overlapping ranges; with two independent section headers that share similar
            # column positions, non-overlapping ranges cannot be constructed.
            #
            # Section 0:  sorted_lines[0..first_secondary_idx-1]
            # Section k:  sorted_lines[sec_idx_k .. sec_idx_{k+1}-1]  (sec_idx_k is the header)

            # Build section boundaries: list of (header_idx, first_data_idx, end_idx)
            section_bounds: list[tuple[int, int, int]] = []
            prev_end = secondary_header_indices[0]  # section 0 ends just before first secondary
            section_bounds.append((0, 1, prev_end))
            for g, sec_idx in enumerate(secondary_header_indices):
                next_sec = (
                    secondary_header_indices[g + 1]
                    if g + 1 < len(secondary_header_indices)
                    else len(sorted_lines)
                )
                section_bounds.append((sec_idx, sec_idx + 1, next_sec))

            # Process each section with its own header and accumulate into `values`.
            section_values: dict[tuple[str, str], float] = {}

            for header_idx, data_start, data_end in section_bounds:
                sec_hdr_line_num, sec_hdr_tokens = sorted_lines[header_idx]
                # Build the column-label list for this section (same logic as main path)
                sec_col_headers: list[tuple[str, int]] = []  # (label, col_position)
                for tok in sec_hdr_tokens:
                    if tok.type in ("ID", "NUMBER", "STRING"):
                        col_pos = getattr(tok, "column", 0) or 0
                        col_label = str(tok).strip("'\"")
                        sec_col_headers.append((col_label, col_pos))

                # Process data lines in this section
                for data_idx in range(data_start, data_end):
                    data_line_num, data_tokens = sorted_lines[data_idx]
                    if not data_tokens:
                        continue
                    # First token is the row label (ID, NUMBER, or STRING).
                    # Use row_label_map (built from grammar tree labels) when available so
                    # that complex label types (dotted, tuple, cross-product, etc.) are
                    # handled correctly, consistent with the non-section-based path.
                    if data_tokens[0].type not in ("ID", "NUMBER", "STRING"):
                        continue
                    if data_line_num in row_label_map:
                        row_header_or_list = row_label_map[data_line_num]
                        row_labels: list[str] = (
                            row_header_or_list
                            if isinstance(row_header_or_list, list)
                            else [row_header_or_list]
                        )
                    else:
                        row_labels = [str(data_tokens[0]).strip("'\"")]

                    # Remaining tokens are values; match to column headers by proximity.
                    # Tiebreaker: when two headers are equidistant, prefer the header with
                    # the larger column position (i.e., the header to the right).
                    # This matches GAMS right-aligned number layout where a multi-digit value
                    # starts 1-2 chars to the left of its column header marker.
                    used_sec_columns: set[str] = set()  # prevent overwriting a matched cell
                    for val_tok in data_tokens[1:]:
                        # Values are NUMBER or ID only (consistent with non-section path)
                        if val_tok.type not in ("NUMBER", "ID"):
                            continue
                        # Skip tokens that belong to row labels (dotted/tuple labels)
                        if id(val_tok) in row_label_token_ids:
                            continue
                        val_col = getattr(val_tok, "column", 0) or 0
                        # Find the closest unmatched column header in this section
                        best_col_label = None
                        best_dist = float("inf")
                        best_col_pos = -1
                        for col_label, col_pos in sec_col_headers:
                            if col_label in used_sec_columns:
                                continue
                            dist = abs(val_col - col_pos)
                            if dist < best_dist or (dist == best_dist and col_pos > best_col_pos):
                                best_dist = dist
                                best_col_label = col_label
                                best_col_pos = col_pos
                        if best_col_label is not None:
                            value = self._parse_table_value(str(val_tok).strip("'\""))
                            # Store under each expanded row label (tuple labels expand to many)
                            for rl in row_labels:
                                section_values[(rl, best_col_label)] = value
                            used_sec_columns.add(best_col_label)

            # Replace `values` with the section-based results and return early,
            # bypassing the normal single-pass column-matching loop below.
            values: dict[tuple[str, ...], float] = {
                (row_lbl, col_lbl): val for (row_lbl, col_lbl), val in section_values.items()
            }
            self.model.add_param(ParameterDef(name=name, domain=domain, values=values))
            return

        # Column headers: store name and column position
        col_headers = []  # List of (col_name, col_position) tuples
        for token in first_line_tokens:
            # Column headers can be ID, NUMBER, or STRING tokens
            # Issue #665: Quoted identifiers like 'machine-1' may be STRING tokens
            if token.type in ("ID", "NUMBER", "STRING"):
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
                # Row labels can be ID, NUMBER, or STRING tokens
                # Issue #665: Quoted row labels (e.g., '20-bond-wt') may be STRING tokens
                if line_tokens[0].type not in ("ID", "NUMBER", "STRING"):
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
            # Skip row label tokens to avoid mis-parsing dotted labels like "medium.alp"
            # where "alp" would otherwise be treated as a value
            row_values = {}  # col_name -> value
            used_columns = set()  # Track which columns have been matched
            for token in line_tokens[1:]:
                # Skip tokens that belong to row labels (dotted/tuple labels)
                if id(token) in row_label_token_ids:
                    continue
                if token.type not in ("NUMBER", "ID"):
                    continue

                token_col = getattr(token, "column", 0)
                # Apply continuation column offset if this token came from a continuation line
                if id(token) in continuation_col_offsets:
                    token_col += continuation_col_offsets[id(token)]

                # Find the column header that this value falls under
                # Issue #665: Use range-based matching where each column "owns" the range
                # from its position (with small left tolerance) up to the next column's
                # start position. For the last column, it owns everything to the right.
                # The ranges are non-overlapping: each column ends where the next begins.
                best_match = None
                for idx, (col_name, col_pos) in enumerate(col_headers):
                    # Skip columns that have already been matched
                    if col_name in used_columns:
                        continue
                    # Determine the range this column owns
                    # Start: this column's position with small left tolerance, but
                    # not before the previous column's position (to avoid overlap)
                    left_tolerance = 3
                    if idx > 0:
                        prev_col_pos = col_headers[idx - 1][1]
                        # Allow left tolerance but don't overlap with previous column
                        range_start = max(prev_col_pos + 1, col_pos - left_tolerance)
                    else:
                        # First column: allow small left tolerance
                        range_start = col_pos - left_tolerance
                    # End: next column's position (exclusive), or infinity for last
                    if idx + 1 < len(col_headers):
                        next_col_pos = col_headers[idx + 1][1]
                        range_end = next_col_pos
                    else:
                        range_end = float("inf")
                    # Check if value falls in this column's range
                    if range_start <= token_col < range_end:
                        best_match = col_name
                        break

                # Fallback: if no range match (e.g., value is left of first header),
                # assign to the next unused column sequentially to avoid data loss
                if best_match is None:
                    for col_name, _ in col_headers:
                        if col_name not in used_columns:
                            best_match = col_name
                            break

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
        # Row labels can be ID, NUMBER, or STRING tokens
        # Issue #665: Quoted row labels (e.g., '20-bond-wt') may be STRING tokens
        for _line_num, line_tokens in sorted_lines[1:]:
            if line_tokens and line_tokens[0].type in ("ID", "NUMBER", "STRING"):
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
                        domain = _id_or_wildcard_list(var_item.children[item_idx + 1])
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
                    domain = _id_or_wildcard_list(var_item.children[item_idx + 1])
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
                domain = _id_or_wildcard_list(var_single_item.children[item_idx + 1])
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
                # Issue #564 follow-up: scalar_data_item can now be NUMBER,
                # SPECIAL_VALUE, or MINUS/PLUS SPECIAL_VALUE.  Walk each
                # scalar_data_item child and parse its tokens.
                values: list[float] = []
                for sdi in data_node.children:
                    if isinstance(sdi, Tree) and sdi.data == "scalar_data_item":
                        tokens = [c for c in sdi.children if isinstance(c, Token)]
                        if len(tokens) == 1:
                            values.append(self._parse_table_value(_token_text(tokens[0])))
                        elif len(tokens) == 2:
                            # MINUS/PLUS + SPECIAL_VALUE (e.g., -inf, +inf)
                            values.append(
                                self._parse_table_value(
                                    _token_text(tokens[0]) + _token_text(tokens[1])
                                )
                            )
                    elif isinstance(sdi, Token) and sdi.type in ("NUMBER", "SPECIAL_VALUE"):
                        values.append(self._parse_table_value(_token_text(sdi)))
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
            elif child.data == "eqn_head_mixed_list":
                # Sprint 19 Day 11: Handle mixed list where each name may have its own domain
                # e.g., "Equation lpcons(i), defdual(j);" or "Equation eq1, eq2(i);"
                for item in child.children:
                    if not isinstance(item, Tree):
                        continue
                    if item.data == "eqn_head_item_domain":
                        name = _token_text(item.children[0])
                        domain = _domain_list(item.children[1])
                        self._ensure_sets(domain, f"equation '{name}' domain", item)
                        self._declared_equations.add(name.lower())
                        self._equation_domains[name.lower()] = domain
                    elif item.data == "eqn_head_item_scalar":
                        name = _token_text(item.children[0])
                        self._declared_equations.add(name.lower())
                        self._equation_domains[name.lower()] = ()

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
            domain = self._equation_domains.get(name.lower(), ())  # Issue #373: case-insensitive
            # condition children: [DOLLAR_token, expr_or_ref_or_ID]
            # Works for all variants: $(expr), $[expr], $ref_bound, $ref_indexed, $ID
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

        # Issue #774: singleton equation instantiation with quoted string literal as domain element.
        # e.g. mmr3("2000-04").. — the quoted token is a set element, not a set name.
        # Skip set-validation for the literal tokens and use the equation's declared domain instead.
        # _domain_list strips quotes so we check raw tokens in the domain_list node.
        domain_list_node = node.children[1]
        raw_tokens = [
            c.children[0]
            for c in domain_list_node.children
            if isinstance(c, Tree) and c.data == "domain_element" and c.children
        ]
        if raw_tokens and all(isinstance(t, Token) and _is_string_literal(t) for t in raw_tokens):
            domain = self._equation_domains.get(name.lower(), ())

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
            # condition children: [DOLLAR_token, expr_or_ref_or_ID]
            # Works for all variants: $(expr), $[expr], $ref_bound, $ref_indexed, $ID
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

        # Skip solver_type (Tree) or bare MCP_CNS_SOLVER token (no-objective variant)
        if idx < len(node.children):
            child = node.children[idx]
            if isinstance(child, Tree) and child.data == "solver_type":
                idx += 1
            elif isinstance(child, Token) and child.type == "MCP_CNS_SOLVER":
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

        if (
            idx < len(node.children)
            and isinstance(node.children[idx], Token)
            and node.children[idx].type == "ID"
        ):
            objvar = _token_text(node.children[idx])
        if objvar:
            self.model.objective = ObjectiveIR(sense=sense, objvar=objvar)
        else:
            self.model.objective = None

    def _handle_model_all(self, node: Tree) -> None:
        name = _token_text(node.children[0])
        self.model.declared_model = name
        self.model.model_equations = []
        self.model.model_uses_all = True

    @staticmethod
    def _extract_model_refs(ref_list: Tree) -> tuple[list[str], bool]:
        """Extract equation references from a ``model_ref_list`` tree node.

        Returns ``(refs, uses_all)`` where *refs* is a list of equation names
        and *uses_all* is ``True`` when the list represents ``/ all /`` or
        ``/ all - eq1 ... /`` semantics.
        """
        refs: list[str] = []
        has_all_except = False
        for child in ref_list.children:
            if isinstance(child, Tree):
                if child.data == "model_simple_ref":
                    refs.append(_token_text(child.children[0]))
                elif child.data == "model_dotted_ref":
                    # For dotted refs like eq.var, use the equation name (first ID)
                    refs.append(_token_text(child.children[0]))
                elif child.data == "model_all_except":
                    has_all_except = True
            elif isinstance(child, Token) and child.type == "ID":
                # Backward compatibility: direct ID tokens
                refs.append(_token_text(child))

        # If the list contains only "all" (case-insensitive), treat as / all /
        if len(refs) == 1 and refs[0].lower() == "all":
            return [], True
        if has_all_except:
            return refs, True
        return refs, False

    def _handle_model_with_list(self, node: Tree) -> None:
        name = _token_text(node.children[0])
        # Issue #714: Find the model_ref_list Tree child dynamically —
        # a STRING description may appear between the model name and the list.
        ref_list = next(
            (c for c in node.children if isinstance(c, Tree) and c.data == "model_ref_list"),
            None,
        )
        if ref_list is None:
            raise self._error(f"Missing model_ref_list in model_with_list for '{name}'", node)

        refs, uses_all = self._extract_model_refs(ref_list)
        self.model.declared_model = name
        self.model.model_equations = refs
        self.model.model_uses_all = uses_all

    def _handle_model_decl(self, node: Tree) -> None:
        name = _token_text(node.children[0])
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

        Issue #729: All model names are now tracked in ``declared_models``.
        Only the *first* model's equation list / all flag is stored (unchanged).
        """
        # Extract all model_decl_item nodes
        model_items = [
            child
            for child in node.children
            if isinstance(child, Tree) and child.data == "model_decl_item"
        ]

        if not model_items:
            raise self._error("Multi-model declaration has no model items", node)

        # Register every model name (Issue #729)
        for item in model_items:
            self.model.declared_model = _token_text(item.children[0])

        # Store equation list / all flag from the first model only
        first_item = model_items[0]

        # Find the model_ref_list child (if any) — the / all / variant has no such child
        ref_list = next(
            (c for c in first_item.children if isinstance(c, Tree) and c.data == "model_ref_list"),
            None,
        )
        if ref_list is not None:
            refs, uses_all = self._extract_model_refs(ref_list)
            self.model.model_equations = refs
            self.model.model_uses_all = uses_all
        else:
            # / all / variant (no model_ref_list) or no equations
            self.model.model_equations = []
            self.model.model_uses_all = len(first_item.children) > 1

    def _handle_file_stmt(self, node: Tree) -> None:
        """Handle File declaration (Issue #746/#747).

        Grammar: file_stmt: "file"i ID "/" file_path "/" SEMI

        Registers the file handle name so that subsequent attribute
        assignments (e.g. ``sol.pc = 5;``) pass validation.  File I/O
        is irrelevant to the NLP->MCP transformation, so we only track
        the name and discard everything else.
        """
        file_name = _token_text(node.children[0])
        self.model.declared_files.add(file_name.lower())

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

        # Issue #749: Extract solve info from loop body so the objective
        # is recorded even when the Solve statement is inside a loop.
        # Issue #810: Recurse into nested loops to find solve at any depth.
        if self.model.objective is None:
            solve_node = self._find_solve_in_loop_body(body_stmts)
            if solve_node is not None:
                self._handle_solve(solve_node)

    @staticmethod
    def _find_solve_in_loop_body(stmts: list[Tree]) -> Tree | None:
        """Recursively search loop body statements for a solve node.

        Issue #810: Handles solve inside doubly (or deeper) nested loops.
        """
        _LOOP_DATA = {
            "loop_stmt",
            "loop_stmt_paren",
            "loop_stmt_filtered",
            "loop_stmt_paren_filtered",
            "loop_stmt_indexed",
            "loop_stmt_indexed_filtered",
        }
        for stmt in stmts:
            if not isinstance(stmt, Tree):
                continue
            if stmt.data == "solve":
                return stmt
            if stmt.data in _LOOP_DATA:
                # Collect child Trees from the nested loop's body
                inner_stmts: list[Tree] = []
                for child in stmt.children:
                    if isinstance(child, Tree):
                        if child.data == "loop_body":
                            inner_stmts.extend(c for c in child.children if isinstance(c, Tree))
                        elif child.data not in ("id_list", "solver_type", "expr"):
                            inner_stmts.append(child)
                result = _ModelBuilder._find_solve_in_loop_body(inner_stmts)
                if result is not None:
                    return result
        return None

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
                param.expressions.append((key, expr))
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
            # - For variable .l with expressions: store as expression (Sprint 20 Day 1)
            # - For other variable bounds with expressions: parse and continue (Sprint 10 Day 6)
            # - For parameters with function calls: store as expression (Sprint 10 Day 4)
            # - For parameters with only param refs: store as expression (Sprint 17 Day 4)
            # - For parameters with variable refs: skip (runtime values, can't store)
            # (e.g., trig.gms: xdiff = 2.66695657 - x1.l uses x1.l which is runtime)
            if is_variable_bound:
                # Sprint 20 Day 1: Store .l expressions for variable initialization
                # Extract bound_kind from target to check if this is a .l assignment
                bound_kind = None
                if isinstance(target, Tree):
                    if target.data == "bound_indexed" and len(target.children) > 1:
                        bound_kind = _token_text(target.children[1]).lower()
                    elif target.data == "bound_scalar" and len(target.children) > 1:
                        bound_kind = _token_text(target.children[1]).lower()

                if bound_kind == "l":
                    # Store .l expression for emission (circle.gms: a.l = (xmin + xmax)/2)
                    var_name = _token_text(target.children[0])
                    if var_name not in self.model.variables:
                        raise self._error(f"Variable '{var_name}' not declared", target) from None
                    var = self.model.variables[var_name]

                    # Extract indices for indexed .l assignments
                    if target.data == "bound_indexed" and len(target.children) > 2:
                        indices = _process_index_list(target.children[2])
                        # Use the full index objects as the key to preserve offsets and subset structure
                        idx_tuple = tuple(indices)
                        # When storing an expression-level .l for specific indices, clear any
                        # conflicting numeric level initialization for the same indices so
                        # there is a single source of truth.
                        if hasattr(var, "l_map") and var.l_map is not None:
                            # For indexed assignments, we need to clear entries with matching base indices
                            # Build a string-based key for comparison with l_map entries
                            str_indices = tuple(
                                (
                                    idx
                                    if isinstance(idx, str)
                                    else (
                                        idx.base
                                        if isinstance(idx, IndexOffset)
                                        else (
                                            idx.subset_name
                                            if isinstance(idx, SubsetIndex)
                                            else str(idx)
                                        )
                                    )
                                )
                                for idx in indices
                            )
                            var.l_map.pop(str_indices, None)
                        var.l_expr_map[idx_tuple] = expr
                    else:
                        # Scalar .l assignment: clear any existing numeric level information
                        # so that the expression becomes the sole initializer.
                        if hasattr(var, "l_map") and var.l_map is not None:
                            var.l_map.clear()
                        if hasattr(var, "l"):
                            var.l = None
                        var.l_expr = expr
                    return
                # For non-.l bounds (lo/up/fx with expressions): continue without storing
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
                # Validate that the base object exists (variable, parameter, equation, model, or file)
                # Issue #558: Equations can also have attributes like .stage in stochastic programming
                # Issue #746/#747: File handles (sol.pc, listA1out.pc) are also valid targets
                base_name = _token_text(target.children[0])
                if (
                    base_name not in self.model.variables
                    and base_name not in self.model.params
                    and base_name not in self.model.equations
                    and base_name.lower() not in self.model.declared_models
                    and base_name.lower() not in self.model.declared_files
                ):
                    raise self._error(
                        f"Symbol '{base_name}' not declared as a variable, parameter, equation, model, or file",
                        target,
                    )
                return
            if target.data == "attr_access_indexed":
                # Handle indexed attribute access: x.stage(g), var.scale(i), etc.
                # Issue #554: Parse but don't process - stochastic programming not modeled
                # Validate that the base object exists (variable, parameter, equation, model, or file)
                # Issue #558: Equations can also have attributes like .stage in stochastic programming
                # Issue #746/#747: File handles are also valid targets
                base_name = _token_text(target.children[0])
                if (
                    base_name not in self.model.variables
                    and base_name not in self.model.params
                    and base_name not in self.model.equations
                    and base_name.lower() not in self.model.declared_models
                    and base_name.lower() not in self.model.declared_files
                ):
                    raise self._error(
                        f"Symbol '{base_name}' not declared as a variable, parameter, equation, model, or file",
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
                    # Sprint 18 Day 3: Store set assignments for emission (P4 fix)
                    # Dynamic subsets must be populated at runtime via these assignments
                    location = self._extract_source_location(node)
                    set_assignment = SetAssignment(
                        set_name=symbol_name,
                        indices=indices,
                        expr=expr,
                        location=location,
                    )
                    self.model.set_assignments.append(set_assignment)
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
                # Issue #726: When a multi-dimensional set is used as a single index
                # (e.g., rp(ll,s) where ll(s,s) is 2D), GAMS implicitly expands the
                # set's dimensions. Compute effective index count by summing each
                # index's dimensionality.
                if len(param.domain) > 0 and len(indices) != len(param.domain):
                    effective_count = self._effective_index_count(indices)
                    if effective_count != len(param.domain):
                        index_word = "index" if len(param.domain) == 1 else "indices"
                        raise self._parse_error(
                            f"Parameter '{symbol_name}' expects {len(param.domain)} {index_word}, got {len(indices)} (effective {effective_count})",
                            target,
                            suggestion=(
                                f"Provide exactly {len(param.domain)} {index_word} to match the parameter "
                                f"declaration (current indices have effective dimension {effective_count})"
                            ),
                        )

                # Issue #622: Handle domain-over assignments like f(j,"k2") = 0 where
                # some indices are domain set names that should be expanded over all
                # members of that set. In GAMS, f(j,"k2") = 0 means "for all elements
                # e in set j, set f(e, k2) = 0".
                # Quoted indices like f("j","k2") are literal element references and
                # must NOT be expanded, even if they match a set name.
                if (
                    not has_function_call
                    and value is not None
                    and len(param.domain) > 0
                    and len(indices) == len(param.domain)
                    and len(target.children) > 1
                ):
                    # Determine which index positions were originally quoted (literal)
                    quoted_positions = _get_quoted_index_positions(target.children[1])

                    # Check which indices match their corresponding domain set name.
                    # Use _resolve_set_def to handle aliases (e.g., Alias(i,j); Parameter f(j);
                    # then f(j) = 0 should expand over the aliased set's members).
                    # Skip quoted indices — they are literal element references.
                    expand_positions: list[int] = []
                    expand_set_defs: dict[int, SetDef] = {}
                    for pos, idx in enumerate(indices):
                        if pos in quoted_positions:
                            continue
                        domain_name = param.domain[pos]
                        if idx.lower() == domain_name.lower():
                            resolved = self._resolve_set_def(idx)
                            if resolved is not None:
                                expand_positions.append(pos)
                                expand_set_defs[pos] = resolved

                    if expand_positions:
                        # Build list of member lists for positions that need expansion
                        # For non-expanding positions, use the literal index
                        dim_values: list[list[str]] = []
                        for pos, idx in enumerate(indices):
                            if pos in expand_positions:
                                members = expand_set_defs[pos].members
                                if not members:
                                    # Empty set: nothing to expand, skip entire assignment
                                    return
                                dim_values.append(members)
                            else:
                                # Sprint 18 Day 2: Strip quotes from literal index for canonical storage
                                stripped_idx = _strip_quotes_from_indices((idx,))[0]
                                dim_values.append([stripped_idx])

                        for combo in product(*dim_values):
                            param.values[combo] = value
                        return

                # Issue #726: When compact multi-dim set indices are used (literal count
                # != domain length but effective count matches), store as expression
                # so the assignment is emitted as a GAMS statement rather than stored
                # as param data (which would have mismatched key arity).
                is_compact_index = len(param.domain) > 0 and len(indices) != len(param.domain)

                # Sprint 10 Day 4: Store expression if it contains function calls, otherwise store value
                if has_function_call or is_compact_index:
                    # Keep quotes in expression indices for emitter
                    param.expressions.append((tuple(indices), expr))
                elif value is not None:
                    # Sprint 18 Day 2: Strip quotes from value indices for canonical storage
                    param.values[_strip_quotes_from_indices(tuple(indices))] = value
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
                    param.expressions.append(((), expr))
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

    def _handle_conditional_assign_general(self, node: Tree) -> None:
        """Handle conditional assignments: lhs$condition = rhs; (Issue #705)

        Uses the condition rule which supports all dollar conditional forms:
        $(expr), $[expr], $ref_indexed, $ref_bound, $ID

        Expected structure: lvalue, condition, ASSIGN, expr (rhs)
        """
        if len(node.children) < 3:
            raise self._error("Malformed conditional assignment statement", node)

        # Extract components
        lvalue_tree = node.children[0]
        if not isinstance(lvalue_tree, Tree) or lvalue_tree.data != "lvalue":
            raise self._error("Malformed assignment target", lvalue_tree)

        # Find condition node and rhs expression
        condition_node = None
        rhs_expr = None
        for child in node.children[1:]:
            if isinstance(child, Tree):
                if child.data == "condition":
                    condition_node = child
                else:
                    rhs_expr = child

        if condition_node is None:
            raise self._error("Missing condition in conditional assignment", node)
        if rhs_expr is None:
            raise self._error("Missing right-hand side in conditional assignment", node)

        # Create a synthetic assignment node (without the condition)
        assign_node = Tree("assign", [lvalue_tree, Token("ASSIGN", ":="), rhs_expr])

        # Extract indices from lvalue for domain context (same as in _handle_assign)
        target = next(
            (child for child in lvalue_tree.children if isinstance(child, (Tree, Token))),
            None,
        )
        domain_context: tuple[str, ...] = ()
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
        # condition children: [DOLLAR_token, expr_or_ref_or_ID]
        condition = self._expr_with_context(
            condition_node.children[1], "conditional assignment", domain_context
        )

        # Create a ConditionalStatement and store it
        location = self._extract_source_location(node)
        cond_stmt = ConditionalStatement(
            condition=condition,
            then_stmts=[assign_node],
            elseif_clauses=[],
            else_stmts=[],
            location=location,
        )

        # Store the conditional statement
        self.model.conditional_statements.append(cond_stmt)

        # Also process the assignment itself so variables/parameters are updated
        self._handle_assign(assign_node)

    def _handle_aggregation(
        self,
        node: Tree,
        aggregation_class: type[Sum] | type[Prod],
        free_domain: tuple[str, ...],
    ) -> Expr:
        """
        Handle sum/prod aggregation expressions with shared logic.

        Args:
            node: Parse tree node for sum or prod expression
            aggregation_class: Sum or Prod class to instantiate
            free_domain: Current free domain from enclosing scope

        Returns:
            Aggregation expression with attached domain

        Note:
            This method applies heuristic expansion for multi-dimensional sets.
            When a set contains "i.j" style tuples, it attempts to infer the base
            sets (e.g., expanding set "ij" to indices "i" and "j").
        """
        # Extract base identifiers from sum_domain (shared grammar rule for sum/prod)
        sum_domain_node = node.children[1]

        # Handle sum_domain which can be index_spec, tuple_domain, or tuple_domain_cond
        condition_expr = None
        condition_node = None  # Track source node for deferred evaluation in body_domain
        if sum_domain_node.data == "tuple_domain":
            index_spec_node = sum_domain_node.children[0]
        elif sum_domain_node.data == "tuple_domain_cond":
            # Issue #718 / #784: (index_spec)$expr — dollar condition outside tuple parens.
            # Do NOT evaluate condition here with free_domain — all sum indices (which are
            # not yet in free_domain) must be in scope for the condition. Defer evaluation
            # to after body_domain is computed below.
            index_spec_node = sum_domain_node.children[0]
            condition_node = sum_domain_node.children[2]
        else:
            index_spec_node = sum_domain_node.children[0]

        index_list_node = index_spec_node.children[0]

        # Check if there's a conditional (DOLLAR expr) inside index_spec
        if condition_node is None and len(index_spec_node.children) > 1:
            condition_node = index_spec_node.children[2]

        if index_list_node.data == "id_list":
            indices = _id_list(index_list_node)
        else:
            indices = tuple(_extract_domain_indices(index_list_node))

        # Use explicit names for error messages
        aggregation_name = "sum" if aggregation_class is Sum else "prod"

        self._ensure_sets(indices, f"{aggregation_name} indices", node)

        # Expand indices based on set definitions
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
                    # Heuristic expansion for multi-dimensional sets
                    members_are_multidim = (
                        set_def.members is not None
                        and len(set_def.members) > 0
                        and any("." in m for m in set_def.members)
                    )
                    if members_are_multidim:
                        first_member = set_def.members[0]
                        dim = len(first_member.split("."))
                        if dim == 2:
                            base_sets = [
                                s
                                for s in self.model.sets
                                if s != idx and len(self.model.sets[s].members) > 0
                            ]
                            for bs_name in base_sets:
                                bs = self.model.sets[bs_name]
                                if bs.members and not any("." in m for m in bs.members):
                                    alias_name = None
                                    for a_name, a_def in self.model.aliases.items():
                                        if a_def.target == bs_name:
                                            alias_name = a_name
                                            break
                                    if alias_name:
                                        expanded_indices.extend([bs_name, alias_name])
                                        break
                            else:
                                expanded_indices.append(idx)
                        else:
                            expanded_indices.append(idx)
                    else:
                        expanded_indices.append(idx)
            else:
                expanded_indices.append(idx)

        # Calculate domains
        new_agg_indices = set(expanded_indices) - set(free_domain)
        remaining_domain = tuple(d for d in free_domain if d not in new_agg_indices)
        seen: set[str] = set()
        body_domain = tuple(
            x
            for x in list(expanded_indices) + list(remaining_domain)
            if not (x in seen or seen.add(x))  # type: ignore[func-returns-value]
        )

        # Evaluate condition in body_domain (all sum indices in scope).
        # condition_node is set but condition_expr intentionally left None until now
        # so that deferred evaluation (Issue #784) uses the fully-expanded body_domain.
        if condition_node is not None:
            condition_expr = self._expr(condition_node, body_domain)

        body = self._expr(node.children[2], body_domain)

        # Store condition separately in the aggregation node.
        # Previously the condition was folded as multiplication (cond * body),
        # which is correct for Sum but wrong for Prod (where excluded elements
        # should contribute 1, not 0). See Issue #716.
        expr = aggregation_class(indices, body, condition_expr)

        return self._attach_domain(expr, remaining_domain)

    def _handle_smin_smax(
        self,
        node: Tree,
        func_name: str,
        free_domain: tuple[str, ...],
    ) -> Expr:
        """Handle smin/smax aggregation expressions (Sprint 19 Day 11).

        These now use dedicated grammar nodes with sum_domain (like sum/prod),
        so the tree structure is: [SMAX_K/SMIN_K, sum_domain, body_expr].
        Produces a Call node for IR fidelity.
        """
        sum_domain_node = node.children[1]
        body_node = node.children[2]

        # Extract index domain from sum_domain (same logic as _handle_aggregation)
        condition_expr = None
        if sum_domain_node.data == "tuple_domain":
            index_spec_node = sum_domain_node.children[0]
        elif sum_domain_node.data == "tuple_domain_cond":
            index_spec_node = sum_domain_node.children[0]
            condition_expr = self._expr(sum_domain_node.children[2], free_domain)
        else:
            index_spec_node = sum_domain_node.children[0]

        index_list_node = index_spec_node.children[0]
        if condition_expr is None and len(index_spec_node.children) > 1:
            condition_expr = self._expr(index_spec_node.children[2], free_domain)

        if index_list_node.data == "id_list":
            indices = _id_list(index_list_node)
        else:
            indices = tuple(_extract_domain_indices(index_list_node))

        self._ensure_sets(indices, f"{func_name} indices", node)
        extended_domain = free_domain + tuple(indices)
        body = self._expr(body_node, extended_domain)

        args: list[Expr] = [SymbolRef(idx) for idx in indices]
        if condition_expr is not None:
            args.append(condition_expr)
        args.append(body)

        expr = Call(func_name, tuple(args))
        remaining_domain = tuple(d for d in extended_domain if d not in indices)
        return self._attach_domain(expr, remaining_domain)

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
            # Sprint 19 Day 13: pass expr_fn so offset_paren (t-(ord(l)-1)) is supported
            _ef = lambda n: self._expr(n, free_domain)  # noqa: E731
            if name in self.model.variables or name in self.model.params:
                # Use _process_index_list to handle i++1, i--2, etc. (Sprint 9)
                indices = _process_index_list(indices_node, _ef)
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
            indices = _process_index_list(indices_node, _ef)
            return self._make_symbol(name, indices, free_domain, node)

        if node.data == "number":
            return self._attach_domain(Const(float(node.children[0])), free_domain)

        if node.data == "yes_value":
            return self._attach_domain(Const(1.0), free_domain)

        if node.data == "no_value":
            return self._attach_domain(Const(0.0), free_domain)

        if node.data == "yes_cond":
            # yes$(condition) — evaluates to 1 if condition holds, 0 otherwise.
            # Construct a DollarConditional with constant value 1.0 and the
            # parsed condition expression as the dollar condition.
            # condition children: [DOLLAR_token, inner_expr]
            # Attach free_domain to value_expr so _merge_domains sees matching
            # domains (mirroring dollar_cond where value_expr inherits domain
            # from _expr).
            value_expr = self._attach_domain(Const(1.0), free_domain)
            condition_tree = node.children[-1]
            condition = self._expr(condition_tree.children[1], free_domain)
            expr = DollarConditional(value_expr, condition)
            return self._attach_domain(expr, self._merge_domains([value_expr, condition], node))

        if node.data == "no_cond":
            # no$(condition) — always evaluates to 0. The condition is preserved
            # in the IR via DollarConditional but does not affect the numeric value.
            # Attach free_domain to value_expr so _merge_domains sees matching
            # domains (mirroring dollar_cond where value_expr inherits domain
            # from _expr).
            value_expr = self._attach_domain(Const(0.0), free_domain)
            condition_tree = node.children[-1]
            condition = self._expr(condition_tree.children[1], free_domain)
            expr = DollarConditional(value_expr, condition)
            return self._attach_domain(expr, self._merge_domains([value_expr, condition], node))

        if node.data == "sum":
            return self._handle_aggregation(node, Sum, free_domain)

        if node.data == "prod":
            return self._handle_aggregation(node, Prod, free_domain)

        if node.data in ("smin", "smax"):
            # Sprint 19 Day 11: smin/smax now use dedicated grammar nodes with sum_domain
            # Handle identically to sum/prod but produce a Call node for IR fidelity
            return self._handle_smin_smax(node, node.data, free_domain)

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
            expr = DollarConditional(value_expr, condition)
            return self._attach_domain(expr, self._merge_domains([value_expr, condition], node))

        if node.data == "unaryop":
            op_token = node.children[0]
            operand = self._expr(node.children[1], free_domain)
            expr = Unary(self._extract_operator(op_token), operand)
            return self._attach_domain(expr, self._expr_domain(operand))

        if node.data == "funccall" or node.data == "func_call":
            # funccall wraps func_call: funccall.children[0] == func_call tree
            # func_call appears directly when used in condition rule ($func_call)
            func_tree = node.children[0] if node.data == "funccall" else node
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
            # Issue #741: Preserve the attribute (.l, .m, etc.) on VarRef so the
            # emitter can render calibration assignments referencing .l values.
            expr = self._make_symbol(name, (), free_domain, node)
            if isinstance(expr, VarRef) and attribute:
                # Issue #672: normalize name to lowercase to match CaseInsensitiveDict keys.
                # Mutate via object.__setattr__ to preserve metadata (symbol_domain,
                # index_values) attached by _make_symbol rather than reconstructing.
                object.__setattr__(expr, "name", expr.name.lower())
                object.__setattr__(expr, "attribute", attribute)
                return self._attach_domain(expr, free_domain)
            return expr

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
            # Issue #741: Preserve the attribute (.l, .m, etc.) on VarRef.
            expr = self._make_symbol(name, indices, free_domain, node)
            if isinstance(expr, VarRef) and attribute:
                # Issue #672: normalize name to lowercase to match CaseInsensitiveDict keys.
                # Mutate via object.__setattr__ to preserve metadata (symbol_domain,
                # index_values) attached by _make_symbol rather than reconstructing.
                object.__setattr__(expr, "name", expr.name.lower())
                object.__setattr__(expr, "attribute", attribute)
                return self._attach_domain(expr, free_domain)
            return expr

        # Issue #781: Set ordinal attribute accessors (set.first, set.last, set.pos, set.ord)
        # tl.first  → ord(tl) == 1          (boolean: 1 when tl is first element)
        # tl.last   → ord(tl) == card(tl)   (boolean: 1 when tl is last element)
        # tl.ord    → ord(tl)               (same as ord(tl))
        # tl.pos    → ord(tl)               (same as ord(tl), GAMS synonym)
        _SET_ORDINAL_ATTRS = {"first", "last", "pos", "ord"}
        if node.data == "set_attr" or (
            node.data == "attr_access"
            and len(node.children) == 2
            and _token_text(node.children[1]).lower() in _SET_ORDINAL_ATTRS
        ):
            set_name = _token_text(node.children[0])
            attr = _token_text(node.children[1]).lower()
            ord_call = Call("ord", (SymbolRef(set_name),))
            if attr == "first":
                expr = Binary("==", ord_call, Const(1.0))
            elif attr == "last":
                card_call = Call("card", (SymbolRef(set_name),))
                expr = Binary("==", ord_call, card_call)
            else:
                # .ord and .pos are synonyms for ord(set)
                expr = ord_call
            return self._attach_domain(expr, free_domain)

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

        # Sprint 17 Day 8: Support brace expressions: {expr} is treated like (expr)
        if node.data == "brace_expr":
            # Just unwrap and process the inner expression
            if len(node.children) > 0:
                return self._expr(node.children[0], free_domain)
            raise self._error("Empty brace expression", node)

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
            # Issue #726: allow multi-dimensional sets as compact indices
            if len(expected) != len(idx_tuple):
                effective_count = self._effective_index_count(idx_tuple)
                if effective_count != len(expected):
                    index_word = "index" if len(expected) == 1 else "indices"
                    raise self._error(
                        f"Variable '{name}' expects {len(expected)} {index_word} but received {len(idx_tuple)} (effective {effective_count})",
                        node,
                    )
            # Issue #672: normalize name to lowercase to match CaseInsensitiveDict.keys()
            # which returns lowercase. This ensures AD differentiation matches correctly.
            expr = VarRef(name.lower(), idx_tuple)
            object.__setattr__(expr, "symbol_domain", expected)
            object.__setattr__(expr, "index_values", idx_tuple)
            return self._attach_domain(expr, free_domain)
        if name in self.model.params:
            expected = self.model.params[name].domain
            # In GAMS, validation is skipped only for parameters with empty domains (true scalars),
            # allowing them to be implicitly expanded when used with indices. For parameters with an
            # explicit domain, the number of indices must match the domain length.
            # Issue #726: allow multi-dimensional sets as compact indices
            if len(expected) > 0 and len(expected) != len(idx_tuple):
                effective_count = self._effective_index_count(idx_tuple)
                if effective_count != len(expected):
                    index_word = "index" if len(expected) == 1 else "indices"
                    raise self._error(
                        f"Parameter '{name}' expects {len(expected)} {index_word} but received {len(idx_tuple)} (effective {effective_count})",
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
            if child.data == "param_data_cross_expansion":
                # Sprint 20 Day 8: Cross-product expansion like (hydro-1*hydro-3).(1978,1983) inf
                prefixes = self._parse_set_element_id_list(child.children[0])
                suffixes = self._parse_set_element_id_list(child.children[1])
                value_node = child.children[-1]
                value = self._parse_param_data_value(value_node)
                # Validate domain dimensionality — cross-product requires exactly 2-D
                if len(domain) != 2:
                    raise self._error(
                        f"Parameter '{param_name}' cross-product expansion syntax (prefix).(suffix) requires a 2-D parameter domain, "
                        f"but '{param_name}' has {len(domain)}-D domain {domain}",
                        child,
                    )
                for p in prefixes:
                    self._verify_member_in_domain(param_name, domain[0], p, child.children[0])
                for s in suffixes:
                    self._verify_member_in_domain(param_name, domain[1], s, child.children[1])
                for p in prefixes:
                    for s in suffixes:
                        values[(p, s)] = value
            elif child.data == "param_data_tuple_expansion":
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
            elif child.data == "param_data_bare_value":
                # Sprint 20 Day 8: Scalar param in Parameter block: / value /
                if len(domain) > 0:
                    raise self._error(
                        f"Parameter '{param_name}' bare value syntax (/ value /) requires a scalar parameter, "
                        f"but '{param_name}' has {len(domain)}-D domain {domain}",
                        child,
                    )
                value = self._parse_param_data_value(child.children[0])
                values[()] = value
            elif child.data == "param_data_scalar":
                key = self._parse_data_indices(child.children[0])
                # Issue #564 follow-up: value can now be a param_data_value
                # Tree (for special values like na, inf) or a plain NUMBER Token.
                value_node = child.children[-1]
                if isinstance(value_node, Tree) and value_node.data == "param_data_value":
                    value = self._parse_param_data_value(value_node)
                else:
                    value = float(_token_text(value_node))

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
        Handles SET_ELEMENT_ID, STRING, NUMBER, and range_expr tokens.
        Day 8: Added range_expr and NUMBER support for patterns like (n-1*n-3) and (1971,1974).
        Note: _token_text() already strips quotes from STRING tokens.
        """
        elements = []
        for child in node.children:
            if isinstance(child, Tree) and child.data == "set_element_id_or_string":
                # Extract the token or sub-tree from the wrapper node
                inner = child.children[0]
                if isinstance(inner, Token):
                    elements.append(_token_text(inner))
                elif isinstance(inner, Tree) and inner.data == "range_expr":
                    # range_expr inside list: expand it (e.g., n-1*n-3)
                    bounds = [
                        _token_text(b.children[0])
                        for b in inner.children
                        if isinstance(b, Tree) and b.data == "range_bound"
                    ]
                    if len(bounds) == 2:
                        expanded = self._expand_range(bounds[0], bounds[1], inner)
                        elements.extend(expanded)
                    else:
                        elements.append("*".join(bounds))
            elif isinstance(child, Token) and child.type in ("SET_ELEMENT_ID", "STRING", "NUMBER"):
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
        if isinstance(expr, (Sum, Prod)):
            # Check the aggregation condition and body
            if expr.condition is not None and self._contains_function_call(expr.condition):
                return True
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
        """Check if an expression contains any *bare* variable references (recursively).

        Sprint 17 Day 4: Used to detect when parameter assignments contain variable
        references (like x(i)) which are runtime values that cannot be stored
        as computed parameter expressions.

        Issue #741: VarRef nodes with an attribute (e.g., x.l, v.m) are *not*
        treated as blocking references because they can be emitted as valid GAMS
        ``x.l(i)`` syntax for calibration assignments.  Only bare VarRef
        (no attribute) blocks storage.

        Expressions that only contain parameter references (like f*d(i,j)/1000)
        or variable attribute references (like x.l(i)) can be stored and emitted
        as GAMS assignment statements.
        """
        if isinstance(expr, VarRef):
            # Issue #741: VarRef with an attribute (.l, .m, .lo, .up) represents
            # a GAMS variable attribute access that can be emitted as-is.
            # Only bare VarRef (no attribute) is a blocking variable reference.
            if expr.attribute:
                # Still check if indices contain bare variable references
                for idx in expr.indices:
                    if isinstance(idx, IndexOffset) and self._contains_variable_reference(idx):
                        return True
                return False  # Attributed VarRef is OK to keep
            # Bare VarRef — this is a blocking variable reference
            for idx in expr.indices:
                if isinstance(idx, IndexOffset) and self._contains_variable_reference(idx):
                    return True
            return True
        if isinstance(expr, (Binary, Unary)):
            # Check children recursively
            for child in expr.children():
                if self._contains_variable_reference(child):
                    return True
        if isinstance(expr, (Sum, Prod)):
            # Check the aggregation condition and body
            if expr.condition is not None and self._contains_variable_reference(expr.condition):
                return True
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
        if name.lower() in self._declared_equations:
            # Issue #783: equation attribute assignments (.m, .l) are post-solve
            # bookkeeping (marginal/level initial values) — no-op for MCP purposes
            return
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
        map_attrs = {"lo": "lo_map", "up": "up_map", "fx": "fx_map", "l": "l_map", "m": "m_map"}
        scalar_attrs = {"lo": "lo", "up": "up", "fx": "fx", "l": "l", "m": "m"}
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
            # Issue #714: Allow repeated assignments (last-write-wins).
            # GAMS permits multiple conditional assignments to the same variable
            # attribute (e.g., tw.l(sa)=0; tw.l(i)$(not sa(i))=0.045;) where
            # the parser cannot statically resolve which indices each condition
            # covers. Accept the overwrite silently, matching GAMS semantics.
            storage[key] = value
            # Sprint 20 Day 1: Clear expression-based .l when setting numeric .l (mutual exclusion)
            if bound_kind == "l" and hasattr(var, "l_expr_map") and var.l_expr_map:
                # Clear matching expression entries (check all since keys may have offsets)
                keys_to_remove = [
                    expr_key
                    for expr_key in var.l_expr_map
                    if len(expr_key) == len(key)
                    and all(
                        (k1 == k2)
                        or (hasattr(k1, "base") and k1.base == k2)
                        or (hasattr(k1, "subset_name") and k1.subset_name == k2)
                        for k1, k2 in zip(expr_key, key, strict=True)
                    )
                ]
                for expr_key in keys_to_remove:
                    del var.l_expr_map[expr_key]
        else:
            scalar_attr = scalar_attrs[bound_kind]
            # Issue #714: Allow repeated scalar assignments (last-write-wins).
            setattr(var, scalar_attr, value)
            # Sprint 20 Day 1: Clear expression-based .l when setting numeric .l (mutual exclusion)
            if bound_kind == "l":
                if hasattr(var, "l_expr") and var.l_expr is not None:
                    var.l_expr = None
                if hasattr(var, "l_expr_map") and var.l_expr_map:
                    var.l_expr_map.clear()

    # Map GAMS word-form comparison operators to their symbolic equivalents.
    # This ensures downstream code (condition_eval, expr_to_gams) sees consistent
    # operator strings regardless of whether the model uses "ne" or "<>".
    # Note: Use ClassVar to avoid dataclass mutable default error
    _WORD_FORM_OPS: ClassVar[dict[str, str]] = {
        "ne": "<>",
        "le": "<=",
        "ge": ">=",
        "lt": "<",
        "gt": ">",
        "eq": "=",
    }

    def _extract_operator(self, node: Tree | Token) -> str:
        if isinstance(node, Token):
            normalized = self._WORD_FORM_OPS.get(node.value.lower())
            if normalized:
                return normalized
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

    def _effective_index_count(
        self, indices: list[str] | tuple[str, ...] | tuple[object, ...]
    ) -> int:
        """Compute effective index count, expanding multi-dimensional sets.

        In GAMS, a multi-dimensional set used as a single index position
        implicitly expands to fill multiple positions.  E.g., rp(ll, s)
        where ll(s,s) is 2-D effectively supplies 3 indices.

        Non-string entries (e.g. IndexOffset objects) are counted as 1.
        """
        count = 0
        for idx in indices:
            if not isinstance(idx, str):
                count += 1
                continue
            set_def = self.model.sets.get(idx)
            if set_def is not None and len(set_def.domain) > 1:
                count += len(set_def.domain)
            else:
                count += 1
        return count

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

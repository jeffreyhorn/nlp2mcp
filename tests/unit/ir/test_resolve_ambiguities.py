"""Tests for #1283 Option D fix (parser-layer table-row disambiguation).

When Earley parses a table row like `low.a 1 2 3` with ambiguity="resolve",
the `table_row` / `simple_label` / `dotted_label` rule chain allows a bare
NUMBER to parse as either a `table_value` (intended) or as a `simple_label`
row label (valid under the grammar but corrupting). Lark's Earley resolver
picks between these with a `PYTHONHASHSEED`-dependent tiebreak; a 20-seed
sweep on chenery produced corruption in 65% of runs.

The Option D fix has two layers:

1. **Defensive `_resolve_ambiguities` extension** (`_score_table_row_alternative`
   + `_pick_ambig_alternative`): when `_ambig` nodes reach the tree (rare
   under `ambiguity="resolve"`, but possible if the parser config changes),
   score each alternative by `(table_value_children_count, -table_row_node_count)`
   and pick the maximum.
2. **Post-parse table-row normalizer** (`_normalize_parsed_tables` +
   `_is_bare_number_row` + `_collapse_corrupted_table_rows`): walks the
   resolved parse tree and detects the #1283 corruption signature — a
   `table_row` consisting of a single bare-NUMBER label with zero
   `table_value` children — then merges each such row into the preceding
   real row as a `table_value`. This is the layer that actually fixes
   chenery under the current `ambiguity="resolve"` config.
"""

from lark import Token, Tree

from src.ir.parser import (
    _collapse_corrupted_table_rows,
    _is_bare_number_row,
    _normalize_parsed_tables,
    _pick_ambig_alternative,
    _resolve_ambiguities,
    _score_table_row_alternative,
)


def _num(value: str, line: int = 1) -> Token:
    tok = Token("NUMBER", value)
    tok.line = line
    return tok


def _id(value: str, line: int = 1) -> Token:
    tok = Token("ID", value)
    tok.line = line
    return tok


def _correct_row() -> Tree:
    """`low.a 1 2 3` parsed correctly: 1 row with 3 table_value children."""
    return Tree(
        "table_row",
        [
            Tree("simple_label", [Tree("dotted_label", [_id("low"), _id("a")])]),
            Tree("table_value", [_num("1")]),
            Tree("table_value", [_num("2")]),
            Tree("table_value", [_num("3")]),
        ],
    )


def _corrupted_rows() -> Tree:
    """`low.a 1 2 3` parsed corruptedly: 4 rows, each a bare-label parse."""
    return Tree(
        "table_section",
        [
            Tree(
                "table_row",
                [Tree("simple_label", [Tree("dotted_label", [_id("low"), _id("a")])])],
            ),
            Tree(
                "table_row",
                [Tree("simple_label", [Tree("dotted_label", [_num("1")])])],
            ),
            Tree(
                "table_row",
                [Tree("simple_label", [Tree("dotted_label", [_num("2")])])],
            ),
            Tree(
                "table_row",
                [Tree("simple_label", [Tree("dotted_label", [_num("3")])])],
            ),
        ],
    )


class TestScoreTableRowAlternative:
    """Score = (table_value_count, -table_row_count)."""

    def test_empty_tree_returns_zero(self):
        assert _score_table_row_alternative(Tree("table_section", [])) == (0, 0)

    def test_token_returns_zero(self):
        assert _score_table_row_alternative(_num("42")) == (0, 0)

    def test_correct_multi_row_label_parse_scores_3_minus_1(self):
        assert _score_table_row_alternative(_correct_row()) == (3, -1)

    def test_corrupted_multi_row_label_parse_scores_0_minus_4(self):
        assert _score_table_row_alternative(_corrupted_rows()) == (0, -4)

    def test_max_picks_correct_over_corrupted(self):
        alternatives = [_corrupted_rows(), _correct_row()]
        winner = max(alternatives, key=_score_table_row_alternative)
        assert winner is alternatives[1]


class TestPickAmbigAlternative:
    """Dispatch: only use the greediest-value heuristic when table_row is present."""

    def test_no_children_returns_self(self):
        ambig = Tree("_ambig", [])
        assert _pick_ambig_alternative(ambig) is ambig

    def test_no_table_row_falls_back_to_first(self):
        """Non-table ambiguities keep the historical first-alternative behavior."""
        alt_a = Tree("expr", [_id("a")])
        alt_b = Tree("expr", [_id("b")])
        ambig = Tree("_ambig", [alt_a, alt_b])
        assert _pick_ambig_alternative(ambig) is alt_a

    def test_table_row_present_picks_greediest_value(self):
        """Despite being first child, corrupted alternative must lose to correct."""
        corrupted = _corrupted_rows()
        correct = _correct_row()
        ambig = Tree("_ambig", [corrupted, correct])

        assert _score_table_row_alternative(corrupted) == (0, -4)
        assert _score_table_row_alternative(correct) == (3, -1)
        assert _pick_ambig_alternative(ambig) is correct


class TestResolveAmbiguitiesEndToEnd:
    """End-to-end: `_resolve_ambiguities` walks the tree and resolves _ambig nodes."""

    def test_token_passthrough(self):
        tok = _num("42")
        assert _resolve_ambiguities(tok) is tok

    def test_no_ambiguity_identity_reconstruction(self):
        """Trees without _ambig nodes are reconstructed but structurally equal."""
        tree = Tree(
            "table_row",
            [
                Tree("simple_label", [Tree("dotted_label", [_id("low")])]),
                Tree("table_value", [_num("1")]),
            ],
        )
        result = _resolve_ambiguities(tree)
        assert isinstance(result, Tree)
        assert result.data == "table_row"
        assert len(result.children) == 2

    def test_table_row_ambig_resolves_to_greediest_value(self):
        """The #1283 reproducer: _ambig with (corrupted, correct) must pick correct."""
        # The corrupted alternative is listed FIRST — pre-fix behavior would
        # pick it. Post-fix behavior picks the greediest-value alternative (correct).
        ambig = Tree("_ambig", [_corrupted_rows(), _correct_row()])
        result = _resolve_ambiguities(ambig)

        assert isinstance(result, Tree)
        assert result.data == "table_row"
        # 1 simple_label + 3 table_value children = 4 children total
        assert len(result.children) == 4
        assert (
            sum(1 for c in result.children if isinstance(c, Tree) and c.data == "table_value") == 3
        )

    def test_non_table_ambig_still_picks_first(self):
        """Non-table ambiguities use the historical first-alternative fallback."""
        alt_a = Tree("expr", [_id("a")])
        alt_b = Tree("expr", [_id("b")])
        ambig = Tree("_ambig", [alt_a, alt_b])
        result = _resolve_ambiguities(ambig)
        assert isinstance(result, Tree)
        assert len(result.children) == 1
        assert isinstance(result.children[0], Token)
        assert result.children[0].value == "a"


def _label_row(label_id: str, line: int = 1) -> Tree:
    """Build a `table_row` with a simple ID row label and zero values."""
    return Tree(
        "table_row",
        [Tree("simple_label", [Tree("dotted_label", [_id(label_id, line=line)])])],
    )


def _labeled_row_with_values(label_id: str, values: list[str], line: int = 1) -> Tree:
    """Build a `table_row` with a simple ID row label and N `table_value` children."""
    return Tree(
        "table_row",
        [
            Tree("simple_label", [Tree("dotted_label", [_id(label_id, line=line)])]),
            *[Tree("table_value", [_num(v, line=line)]) for v in values],
        ],
    )


def _corrupted_number_row(value: str, line: int = 1) -> Tree:
    """Build a #1283-corrupted bare-NUMBER `table_row` (single NUMBER label, no values)."""
    return Tree(
        "table_row",
        [Tree("simple_label", [Tree("dotted_label", [_num(value, line=line)])])],
    )


def _content(row: Tree) -> Tree:
    return Tree("table_content", [row])


class TestIsBareNumberRow:
    """Detect the #1283 corruption signature at the `table_row` level."""

    def test_detects_corrupted_bare_number_row(self):
        row = _corrupted_number_row("0.915")
        tok = _is_bare_number_row(row)
        assert isinstance(tok, Token)
        assert tok.value == "0.915"

    def test_rejects_row_with_values(self):
        """Legit bare-NUMBER row label (issue #863) — has table_value children."""
        row = Tree(
            "table_row",
            [
                Tree("simple_label", [Tree("dotted_label", [_num("9000011")])]),
                Tree("table_value", [_num("42")]),
            ],
        )
        assert _is_bare_number_row(row) is None

    def test_rejects_id_labeled_row(self):
        assert _is_bare_number_row(_label_row("low")) is None

    def test_rejects_multi_segment_dotted_label(self):
        row = Tree(
            "table_row",
            [Tree("simple_label", [Tree("dotted_label", [_id("low"), _id("a")])])],
        )
        assert _is_bare_number_row(row) is None

    def test_rejects_tuple_label_alternative(self):
        """tuple_cross_label, tuple_label, etc. are not simple_label."""
        row = Tree("table_row", [Tree("tuple_cross_label", [_id("dummy")])])
        assert _is_bare_number_row(row) is None

    def test_rejects_non_table_row(self):
        assert _is_bare_number_row(Tree("expr", [_id("x")])) is None


class TestCollapseCorruptedTableRows:
    """Merge corrupted bare-NUMBER rows into the preceding real row."""

    def test_collapse_single_corrupted_row(self):
        """`low 1` + `[2]` corrupted → `low 1 2`."""
        contents = [
            _content(_labeled_row_with_values("low", ["1"])),
            _content(_corrupted_number_row("2")),
        ]
        result = _collapse_corrupted_table_rows(contents)
        assert len(result) == 1
        row = result[0].children[0]
        values = [c for c in row.children if isinstance(c, Tree) and c.data == "table_value"]
        assert len(values) == 2
        assert values[0].children[0].value == "1"
        assert values[1].children[0].value == "2"

    def test_collapse_chenery_pattern(self):
        """Chenery-style: `low.a.distr` (no values) + [.915, .944, 2.60, .80] corrupted."""
        contents = [
            _content(_labeled_row_with_values("low", [])),
            _content(_corrupted_number_row("0.915")),
            _content(_corrupted_number_row("0.944")),
            _content(_corrupted_number_row("2.60")),
            _content(_corrupted_number_row("0.80")),
        ]
        result = _collapse_corrupted_table_rows(contents)
        assert len(result) == 1
        row = result[0].children[0]
        values = [c for c in row.children if isinstance(c, Tree) and c.data == "table_value"]
        assert len(values) == 4
        assert [v.children[0].value for v in values] == ["0.915", "0.944", "2.60", "0.80"]

    def test_legit_bare_number_row_preserved(self):
        """A legit bare-NUMBER row label (issue #863) with table_value children is NOT merged."""
        legit = Tree(
            "table_row",
            [
                Tree("simple_label", [Tree("dotted_label", [_num("9000011")])]),
                Tree("table_value", [_num("42")]),
            ],
        )
        contents = [_content(_label_row("prev")), _content(legit)]
        result = _collapse_corrupted_table_rows(contents)
        assert len(result) == 2

    def test_orphan_with_no_preceding_row_preserved(self):
        """If the first row is a bare-NUMBER orphan, preserve it — don't drop data."""
        contents = [_content(_corrupted_number_row("42"))]
        result = _collapse_corrupted_table_rows(contents)
        assert len(result) == 1
        inner = result[0].children[0]
        assert _is_bare_number_row(inner) is not None

    def test_bare_number_on_different_line_not_collapsed(self):
        """A bare-NUMBER row on a line AFTER the previous row is a legitimate
        numeric row label (the values likely come on a continuation line) —
        do NOT collapse it onto the previous row.
        """
        contents = [
            _content(_labeled_row_with_values("foo", ["1.0"], line=49)),
            _content(_corrupted_number_row("9000011", line=50)),
        ]
        result = _collapse_corrupted_table_rows(contents)
        # Both rows preserved — different lines means not #1283 corruption.
        assert len(result) == 2
        prev_row = result[0].children[0]
        prev_values = [
            c for c in prev_row.children if isinstance(c, Tree) and c.data == "table_value"
        ]
        assert len(prev_values) == 1  # unchanged
        assert _is_bare_number_row(result[1].children[0]) is not None

    def test_bare_number_followed_by_continuation_not_collapsed(self):
        """Bare-NUMBER row followed by a `table_continuation` is a legitimate
        numeric row label whose values arrive on the `+` line — don't collapse.
        """
        continuation = Tree(
            "table_continuation",
            [Token("PLUS", "+"), Tree("table_value", [_num("2.0")])],
        )
        contents = [
            _content(_labeled_row_with_values("foo", ["1.0"], line=1)),
            _content(_corrupted_number_row("9000011", line=1)),  # same line → gate A passes
            Tree("table_content", [continuation]),
        ]
        result = _collapse_corrupted_table_rows(contents)
        # Even on the same line, gate B (next is continuation) prevents collapse.
        assert len(result) == 3
        prev_row = result[0].children[0]
        prev_values = [
            c for c in prev_row.children if isinstance(c, Tree) and c.data == "table_value"
        ]
        assert len(prev_values) == 1  # unchanged


class TestNormalizeParsedTables:
    """End-to-end post-parse normalizer for #1283."""

    def test_token_passthrough(self):
        tok = _num("42")
        assert _normalize_parsed_tables(tok) is tok

    def test_non_table_tree_structurally_unchanged(self):
        tree = Tree("model_def", [_id("foo")])
        result = _normalize_parsed_tables(tree)
        assert isinstance(result, Tree)
        assert result.data == "model_def"
        assert len(result.children) == 1

    def test_table_block_with_corruption_repaired(self):
        """table_block wrapping corrupted rows: rewritten to 1 row with N values."""
        contents = [
            _content(_labeled_row_with_values("high", [])),
            _content(_corrupted_number_row("1")),
            _content(_corrupted_number_row("2")),
            _content(_corrupted_number_row("3")),
        ]
        block = Tree(
            "table_block",
            [_id("pdat"), Tree("table_domain_list", []), *contents],
        )
        result = _normalize_parsed_tables(block)
        assert isinstance(result, Tree)
        assert result.data == "table_block"
        # The first two preamble children are kept; the table_content tail is collapsed.
        table_contents = [
            c for c in result.children if isinstance(c, Tree) and c.data == "table_content"
        ]
        assert len(table_contents) == 1
        row = table_contents[0].children[0]
        values = [c for c in row.children if isinstance(c, Tree) and c.data == "table_value"]
        assert len(values) == 3
        assert [v.children[0].value for v in values] == ["1", "2", "3"]

    def test_nested_table_blocks_all_normalized(self):
        """Normalizer recurses: nested table_blocks are also repaired."""
        corrupted_block = Tree(
            "table_block",
            [
                _id("inner"),
                _content(_labeled_row_with_values("a", [])),
                _content(_corrupted_number_row("7")),
            ],
        )
        outer = Tree("program", [corrupted_block])
        result = _normalize_parsed_tables(outer)
        inner = result.children[0]
        assert isinstance(inner, Tree)
        assert inner.data == "table_block"
        table_contents = [
            c for c in inner.children if isinstance(c, Tree) and c.data == "table_content"
        ]
        assert len(table_contents) == 1
        values = [
            c
            for c in table_contents[0].children[0].children
            if isinstance(c, Tree) and c.data == "table_value"
        ]
        assert len(values) == 1
        assert values[0].children[0].value == "7"

"""Shared anchor resolver (Sprint 40 P10a): pin a source site by OWNING FUNCTION
plus an ANCHOR that must occur EXACTLY ONCE in that function's live code
(comments and bare strings blanked). Extracted verbatim from
tests/unit/kkt/test_positional_domain_sites.py.
"""

from __future__ import annotations

import ast
import functools
import io
import pathlib
import tokenize

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]


@functools.lru_cache(maxsize=16)
def _code_only(source: str) -> str:
    """``source`` with every COMMENT and every BARE-STRING STATEMENT blanked.

    Cached per source text: 16 rows over a 6,000-line file re-tokenised it 16
    times and took the two structural tests from ~3 s to ~7 s each.

    Same length, same line structure — so line ranges computed on the original
    still index into this text — but an anchor can now only match **executable
    code**. Without this, deleting a guarded expression while leaving its exact
    text in a comment or docstring kept both structural pins green, and those
    pins are the only protection the 11 structural-only rows have
    (PR #1743 review; the mutant is `test_the_anchor_pins_reject_a_COMMENTED_OUT_site`).

    ⚠ Inline string LITERALS are kept — they are code. A first revision blanked
    every STRING token and broke the `_try_dotted_key_lookup` anchor
    ``list(domain).index("*")``, whose ``"*"`` is the lookup key, not prose.
    Only string EXPRESSION STATEMENTS (docstrings and bare strings) are blanked.
    """
    lines = source.splitlines(keepends=True)
    out = [list(ln) for ln in lines]

    def _blank(r0, c0, r1, c1):
        for r in range(r0, r1 + 1):
            row = out[r - 1]
            lo = c0 if r == r0 else 0
            hi = c1 if r == r1 else len(row)
            for c in range(lo, min(hi, len(row))):
                if row[c] != "\n":
                    row[c] = " "

    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type == tokenize.COMMENT:
            _blank(*tok.start, *tok.end)
    for node in ast.walk(ast.parse(source)):
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            _blank(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
    return "".join("".join(row) for row in out)


def _owning_bodies(source: str, qualified: str) -> list[str]:
    """CODE-ONLY text of every function matching ``qualified``, nested paths allowed.

    ``"outer.inner"`` resolves to the ``inner`` FunctionDef found *inside*
    ``outer``'s body — so an anchor is searched only within the nested function's
    own lines (PR #1743 review). A bare name resolves to every top-level or
    nested def of that name, as before.

    The returned text has comments and strings blanked (`_code_only`), so an
    anchor must still be live code to count.
    """
    tree = ast.parse(source)
    lines = _code_only(source).splitlines()
    parts = qualified.split(".")

    def _defs_in(node):
        return [
            n
            for n in ast.walk(node)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n is not node
        ]

    candidates = [n for n in _defs_in(tree) if n.name == parts[0]]
    for part in parts[1:]:
        candidates = [c for n in candidates for c in _defs_in(n) if c.name == part]
    return ["\n".join(lines[n.lineno - 1 : (n.end_lineno or n.lineno)]) for n in candidates]


class AnchorError(AssertionError):
    """The anchor is absent, ambiguous, or its owning function does not exist."""


def resolve_unique(rel: str, qualified: str, snippet: str) -> int:
    """1-based line of the single occurrence of ``snippet`` in ``qualified``'s live code.

    Raises AnchorError when the function is missing, the anchor is absent, or it
    occurs more than once (an anchor that matches twice pins nothing).
    """
    source = (PROJECT_ROOT / rel).read_text(encoding="utf-8")
    tree = ast.parse(source)
    code_lines = _code_only(source).splitlines()
    parts = qualified.split(".")

    def _defs_in(node):
        return [
            n
            for n in ast.walk(node)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n is not node
        ]

    cands = [n for n in _defs_in(tree) if n.name == parts[0]]
    for part in parts[1:]:
        cands = [c for n in cands for c in _defs_in(n) if c.name == part]
    if not cands:
        raise AnchorError(f"{rel}::{qualified} — function gone")
    # One entry per OCCURRENCE, not per matching line (PR #1800 review): two
    # copies of the anchor on one line are still two, and pin nothing.
    hits = [
        i + 1
        for n in cands
        for i in range(n.lineno - 1, n.end_lineno or n.lineno)
        for _ in range(code_lines[i].count(snippet))
    ]
    if len(hits) != 1:
        raise AnchorError(
            f"{rel}::{qualified} — anchor {snippet!r} occurs {len(hits)}x (need exactly 1)"
        )
    return hits[0]

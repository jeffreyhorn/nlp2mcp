"""Sprint 25 / #1352: qdemo7 table parsing column-alignment regression.

The preprocessor's `normalize_special_identifiers` auto-quotes
hyphenated column headers in tables that have a description (e.g.,
`ref-p` → `'ref-p'` in qdemo7's `Table demdat(c,*) 'demand data'`).
Each apostrophe inserts a character into the header line, shifting
subsequent column positions by 2 chars per quoted header. Data row
lines are unchanged (numeric values don't get quoted), so Lark's
reported token columns for headers and data values become
mis-aligned by the cumulative apostrophe-shift.

For qdemo7's `wheat 100 2700 -.8 140` row, the value `140` was
reported by Lark at column 45 — which used to fall under `imp-p`
in the original source (col 43-47), but after preprocessing the
shifted ranges put it under `'exp-p'` instead. Result: `pe(wheat)`
became 140 (should be 0), `pm(wheat)` became 0 (should be 140),
and the emitted MCP became structurally infeasible — PATH bailed
at iteration 0 with `DuplicateRows Implied` for stat_exports/
stat_imports.

Fix: `_merge_dotted_col_headers` now compensates for the
apostrophe-shift by computing each header's "effective" identifier
column in the original (pre-quote) source — subtract preceding
cumulative shift and the leading apostrophe of this header (if
quoted). Data rows now align correctly with header ranges.
"""

from __future__ import annotations

import os
import sys

import pytest


@pytest.fixture(autouse=True)
def _high_recursion_limit():
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        yield
    finally:
        sys.setrecursionlimit(old)


@pytest.mark.integration
def test_qdemo7_demdat_aligns_under_correct_columns():
    """#1352: qdemo7's `demdat` table has hyphenated column headers
    that get auto-quoted by the preprocessor. The shifted header
    positions must not misalign data rows, so `wheat`'s `140` ends
    up under `imp-p` (correct) rather than `exp-p` (the bug).
    """
    from src.ir.parser import parse_model_file

    src = "data/gamslib/raw/qdemo7.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/qdemo7.gms is gitignored on this runner.")

    ir = parse_model_file(src)
    demdat = ir.params["demdat"]

    # Rows with a single trailing numeric value (wheat, beans, maize) must
    # land it under `imp-p`, NOT `exp-p`. Rows with two trailing values
    # (onions, cotton, tomato) keep the first under `exp-p` and the second
    # under `imp-p`.
    expected = {
        ("wheat", "imp-p"): 140.0,
        ("wheat", "exp-p"): 0.0,
        ("beans", "imp-p"): 270.0,
        ("beans", "exp-p"): 0.0,
        ("maize", "imp-p"): 85.0,
        ("maize", "exp-p"): 0.0,
        ("onions", "exp-p"): 40.0,
        ("cotton", "exp-p"): 300.0,
        ("tomato", "exp-p"): 60.0,
    }
    for key, want in expected.items():
        got = demdat.values.get(key, 0.0)
        assert got == want, (
            f"demdat{key} = {got}, expected {want}. Pre-fix the preprocessor's "
            f"auto-quoting of hyphenated table headers shifted column ranges, "
            f"causing values to land under the wrong header."
        )

"""Priority-10 AD cross-term property tests (Sprint 28 Day 12).

Each test emits a minimal synthetic GAMS model (committed under
``tests/fixtures/crossterm_shapes/``, always-run) in-process and pattern-asserts
that the target ``stat_*`` stationarity row contains the hand-derived cross-term
— turning the recurring offset/alias/parameter-valued-offset stationarity defect
class (#1224/#1381/#1388/#1390/#1398) into a systematic guard rather than
ad-hoc per-model goldens. See
``docs/planning/EPIC_4/SPRINT_28/PRIORITY_10_DIVERGENCE_PROPERTY_TESTS_DESIGN.md``.

Assertions normalize whitespace and match the key sub-expression (robust to
incidental re-parenthesization / term reordering).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.gradient import compute_objective_gradient
from src.config import Config
from src.emit.emit_gams import emit_gams_mcp
from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_file
from src.kkt.assemble import assemble_kkt_system
from src.kkt.reformulation import reformulate_model

pytestmark = pytest.mark.integration

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "crossterm_shapes"


def _emit(fixture: str) -> str:
    """Emit a synthetic fixture in-process (sub-second)."""
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        model = parse_model_file(str(FIXTURES / fixture))
        reformulate_model(model)
        normalized_eqs, _ = normalize_model(model)
        cfg = Config()
        gradient = compute_objective_gradient(model, cfg)
        j_eq, j_ineq = compute_constraint_jacobian(model, normalized_eqs, cfg)
        return emit_gams_mcp(assemble_kkt_system(model, gradient, j_eq, j_ineq, cfg))
    finally:
        sys.setrecursionlimit(old)


def _stat_row(emit: str, prefix: str) -> str:
    """Return the whitespace-stripped ``<prefix>.. … ;`` stationarity row."""
    m = re.search(rf"^{re.escape(prefix)}\.\..*?;", emit, re.MULTILINE | re.DOTALL)
    assert m is not None, f"{prefix}.. row not found"
    return re.sub(r"\s+", "", m.group(0))


def test_shape1_single_axis_offset() -> None:
    """Offset Sum: the offset is INVERTED in the cross-term (tt = t-1)."""
    row = _stat_row(_emit("shape1_single_axis_offset.gms"), "stat_x(t)")
    assert "1$(ord(t)=ord(tt)+1)*lam_link(tt)" in row, row
    assert "-lam_link(t)" in row, row


def test_shape2_self_alias_sum() -> None:
    """Self-alias Sum: eq index ↔ alias swap (a(jj,i), sum over jj)."""
    row = _stat_row(_emit("shape2_self_alias_sum.gms"), "stat_x(i)")
    assert "sum(jj," in row and "a(jj,i)*nu_bal(jj)" in row, row


def test_shape3_cross_set_alias_no_swap() -> None:
    """Cross-set alias Sum: NO i↔j swap (b(i,j), not b(j,i)) — the #1398 shape."""
    row = _stat_row(_emit("shape3_cross_set_alias.gms"), "stat_x(j)")
    assert "sum(i," in row and "b(i,j)*lam_dem(i)" in row, row
    assert "b(j,i)" not in row, f"cross-set indices wrongly swapped (#1398): {row}"


def test_shape4_parameter_valued_offset() -> None:
    """#1224: parameter-valued offset is INVERTED (i-li(k), j-lj(k)) + the l-1 term."""
    row = _stat_row(_emit("shape4_parameter_valued_offset.gms"), "stat_x(l,i,j)")
    assert "lam_pr(k,l,i-li(k),j-lj(k))" in row, row
    assert "lam_pr(k,l-1,i,j)" in row, row


def test_shape5_interior_edge_convex() -> None:
    """#1388: i±1 convexity cross-terms guarded by the canonical middle(i±1)."""
    row = _stat_row(_emit("shape5_interior_edge_convex.gms"), "stat_r(i)")
    assert "lam_convexity(i))$(middle(i))" in row, row
    assert "lam_convexity(i+1))" in row and "$(middle(i+1))" in row, row
    assert "lam_convexity(i-1))" in row and "$(middle(i-1))" in row, row


def test_shape6_tree_predicate_aliased_sum() -> None:
    """#1390: tree predicate preserved + INVERTED (tree(n,nn)) as a SINGLE guarded
    Sum — NOT per-element offset enumeration (the 22-phantom-term bug)."""
    row = _stat_row(_emit("shape6_tree_predicate_aliased_sum.gms"), "stat_y(n)")
    assert "sum(nn," in row and "1$(tree(n,nn))" in row and "nu_dembal(nn)" in row, row
    # No per-element offset enumeration of the multiplier (the #1390 defect).
    assert not re.search(r"nu_dembal\(n[+-]\d", row), f"phantom-offset enumeration (#1390): {row}"

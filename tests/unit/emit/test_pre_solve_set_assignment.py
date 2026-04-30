"""Sprint 25 / #1315 + #1323: dynamic-subset SET assignment extraction.

When a multi-solve loop body contains a dynamic-subset assignment
(e.g., lmp2's `loop(c, m(mm) = ord(mm) <= cases(c, 'm'); ...)`), the
MCP pre-solve emission must extract that assignment alongside the
parameter assignments. Without this, GAMS aborts with Error 66
(`symbol "m" has no values assigned`) because the dynamic subset is
referenced in equation domains/bodies but never populated.

These tests validate the emitter integration. The lmp2 corpus
regression lives in `tests/integration/emit/test_lmp2_set_extraction.py`.
"""

from __future__ import annotations

import re
import sys

import pytest


def _emit_mcp_for_source(gams_src: str) -> str:
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_text
    from src.kkt.assemble import assemble_kkt_system

    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        model = parse_model_text(gams_src)
        normalize_model(model)
        j_eq, j_ineq = compute_constraint_jacobian(model)
        grad = compute_objective_gradient(model)
        kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
        return emit_gams_mcp(kkt)
    finally:
        sys.setrecursionlimit(old)


# Synthetic minimal multi-solve NLP with a dynamic-subset assignment in
# the loop body — mirrors lmp2's structural shape.
_LMP2_SHAPE = """
Set
   mm / m1*m3 /
   nn / n1*n3 /;

Set
   m(mm) 'constraints'
   n(nn) 'variables'
   c     'cases' / c1*c2 /;

Table cases(c,*)
        m  n
   c1   2  2
   c2   3  3;

Parameter
   A(mm,nn)
   b(mm);

Variable x(nn), obj;
Equation Objective, Constraints(mm);

Objective..      obj  =e= sum(nn$(n(nn)), x(nn));
Constraints(m).. b(m) =l= sum(nn$(n(nn)), A(m,nn) * x(nn));

x.lo(nn) = 0;

Model lp / all /;

loop(c,
   m(mm) = ord(mm) <= cases(c,'m');
   n(nn) = ord(nn) <= cases(c,'n');
   A(mm,nn) = 1;
   b(mm) = 1;
   solve lp minimizing obj using nlp;
);
"""


@pytest.mark.unit
def test_dynamic_subset_assignment_extracted():
    """`m(mm) = ord(mm) <= cases('c1', 'm');` should be emitted in
    the pre-solve section.
    """
    output = _emit_mcp_for_source(_LMP2_SHAPE)

    # The set assignment should be emitted with `c` substituted to 'c1'.
    assert re.search(
        r"^\s*m\(mm\)\s*=\s*ord\(mm\)\s*<=\s*cases\('c1','m'\)\s*;",
        output,
        re.MULTILINE,
    ), (
        "Expected `m(mm) = ord(mm) <= cases('c1','m');` extracted from loop body. Output:\n"
        + output
    )


@pytest.mark.unit
def test_lhs_subset_name_not_substituted_to_parent():
    """LHS `m(mm)` must remain `m(mm)`, NOT be rewritten to `mm(mm)`.

    The existing dynamic-subset substitution (`m → mm`) was used for
    parameter assignments; for set assignments to a dynamic subset,
    that substitution must be skipped on the LHS.
    """
    output = _emit_mcp_for_source(_LMP2_SHAPE)

    # No `mm(mm) = ord(mm) ...` line should appear.
    assert not re.search(
        r"^\s*mm\(mm\)\s*=\s*ord\(", output, re.MULTILINE
    ), "LHS dynamic subset name was incorrectly substituted to its parent set."


@pytest.mark.unit
def test_param_referenced_only_via_subset_assignment_is_emitted():
    """`cases` is referenced only by the new subset assignments. The
    `_collect_model_relevant_params` extension must surface it so its
    Table values are emitted.
    """
    output = _emit_mcp_for_source(_LMP2_SHAPE)

    # cases values for both labels should be force-quoted in the mixed-key
    # branch (since 'm' and 'n' are also set names — literal collision).
    assert re.search(r"cases\('c1','m'\)\s*=\s*2", output) or re.search(
        r"cases\('c1','m'\)\s*=\s*2.0", output
    ), ("Expected `cases('c1','m') = 2` Table value emitted (post-#1315). Output:\n" + output)


@pytest.mark.unit
def test_subset_assignment_appears_before_solve_or_equations():
    """The extracted set assignment must come BEFORE the equation
    declarations and solve, so the subset is populated when the MCP
    references it.
    """
    output = _emit_mcp_for_source(_LMP2_SHAPE)
    lines = output.splitlines()

    set_assign_idx = None
    eq_decl_idx = None
    for i, line in enumerate(lines):
        if re.match(r"^\s*m\(mm\)\s*=\s*ord\(mm\)", line):
            set_assign_idx = i
        if line.strip().startswith("comp_Constraints") or line.strip().startswith("stat_x"):
            eq_decl_idx = i
            break

    assert set_assign_idx is not None, "Subset assignment line not found"
    assert eq_decl_idx is not None, "Equation declaration not found"
    assert set_assign_idx < eq_decl_idx, (
        f"Subset assignment (line {set_assign_idx}) must precede equations " f"(line {eq_decl_idx})"
    )


@pytest.mark.unit
def test_param_assignments_still_emitted():
    """Regression check: parameter assignments (`A`, `b`) from the loop
    body must still be emitted — the new branch should not displace them.
    """
    output = _emit_mcp_for_source(_LMP2_SHAPE)

    assert re.search(
        r"^\s*A\(mm,nn\)\s*=\s*1", output, re.MULTILINE
    ), "Expected parameter assignment `A(mm,nn) = 1` to still be emitted"
    assert re.search(
        r"^\s*b\(mm\)\s*=\s*1", output, re.MULTILINE
    ), "Expected parameter assignment `b(mm) = 1` to still be emitted"

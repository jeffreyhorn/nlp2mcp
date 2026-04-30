"""Sprint 25 / #1315 + #1323: lmp2 corpus regression for dynamic-subset extraction.

Pre-fix: `gams /tmp/lmp2_mcp.gms` failed with Error 66
(`equation stat_x.. symbol "m" has no values assigned`) because the
dynamic-subset assignment `m(mm) = ord(mm) <= cases(c, 'm')` inside
the multi-solve loop was not extracted into the MCP pre-solve section.

Post-fix: the assignment is extracted (with the loop index `c`
substituted to its first member `'c1'`), and `cases` is added to the
model-relevant param set so its Table values are emitted alongside.
"""

from __future__ import annotations

import os
import re
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


def _emit_mcp_for(gms_path: str) -> str:
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_file
    from src.kkt.assemble import assemble_kkt_system

    model = parse_model_file(gms_path)
    normalize_model(model)
    j_eq, j_ineq = compute_constraint_jacobian(model)
    grad = compute_objective_gradient(model)
    kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
    return emit_gams_mcp(kkt)


@pytest.mark.integration
def test_lmp2_emits_m_subset_assignment():
    """The dynamic-subset assignment `m(mm) = ord(mm) <= cases('c1','m');`
    must be extracted from the multi-solve loop body.
    """
    src = "data/gamslib/raw/lmp2.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/lmp2.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    assert re.search(
        r"^\s*m\(mm\)\s*=\s*ord\(mm\)\s*<=\s*cases\('c1','m'\)\s*;",
        output,
        re.MULTILINE,
    ), "Expected lmp2's `m(mm) = ord(mm) <= cases('c1','m');` to be extracted."


@pytest.mark.integration
def test_lmp2_emits_n_subset_assignment():
    """Same shape for `n(nn)` — the second dynamic subset."""
    src = "data/gamslib/raw/lmp2.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/lmp2.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    assert re.search(
        r"^\s*n\(nn\)\s*=\s*ord\(nn\)\s*<=\s*cases\('c1','n'\)\s*;",
        output,
        re.MULTILINE,
    ), "Expected lmp2's `n(nn) = ord(nn) <= cases('c1','n');` to be extracted."


@pytest.mark.integration
def test_lmp2_emits_cases_table_values():
    """Because `cases` is now referenced via the subset assignments, its
    Table values must be emitted in the pre-solve section. The mixed-key
    branch must force-quote the literal column labels (which collide
    with the dynamic-subset names `m` and `n`).
    """
    src = "data/gamslib/raw/lmp2.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/lmp2.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    # The Table has 5 cases × 2 columns = 10 entries. Spot-check the
    # first and last rows (both columns each) to verify the mixed-key
    # branch quotes the literal column labels `'m'` / `'n'` correctly.
    expected_pairs = [
        (("c1", "m"), 10),
        (("c1", "n"), 20),
        (("c5", "m"), 200),
        (("c5", "n"), 200),
    ]
    for (k1, k2), val in expected_pairs:
        pattern = rf"cases\('{k1}','{k2}'\)\s*=\s*{val}(\.0)?\s*;"
        assert re.search(
            pattern, output
        ), f"Expected `cases('{k1}','{k2}') = {val}` line. Output excerpt:\n" + "\n".join(
            line for line in output.split("\n") if "cases" in line
        )

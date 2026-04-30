"""Sprint 25 / #1327: lmp2 corpus regression for declaration-domain handling.

When an equation is declared over a parent set but defined over a dynamic
subset (e.g. lmp2's `Equation Constraints(mm); Constraints(m).. ...`), GAMS
rejects the dynamic subset as a declaration domain (Error 187).

This issue surfaced after #1315 / #1323 fixed the dynamic-subset SET
assignment extraction (Error 66 was previously masking it).

The fix tracks `declaration_domain` separately from `domain` in `EquationDef`;
the KKT pipeline uses `declaration_domain` for multiplier and complementarity
equation declarations, while the body retains the dynamic-subset head
(`comp_Constraints(m)..`) so GAMS still restricts the equation to subset
members.
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
def test_lmp2_lam_constraints_declared_over_parent_set():
    """`lam_Constraints` must be declared over `mm` (parent), not `m`
    (dynamic subset). GAMS rejects dynamic subsets as declaration
    domains with Error 187.
    """
    src = "data/gamslib/raw/lmp2.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/lmp2.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    assert re.search(
        r"^\s*lam_Constraints\(mm\)\s*$", output, re.MULTILINE
    ), "Expected `lam_Constraints(mm)` declaration over parent set."
    # The buggy form uses dynamic subset `m` as declaration domain.
    assert not re.search(
        r"^\s*lam_Constraints\(m\)\s*$", output, re.MULTILINE
    ), "lam_Constraints must NOT be declared over dynamic subset `m`."


@pytest.mark.integration
def test_lmp2_comp_constraints_declared_over_parent_set():
    """`comp_Constraints` must be declared over `mm` (parent) for the
    same reason as `lam_Constraints`.
    """
    src = "data/gamslib/raw/lmp2.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/lmp2.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    assert re.search(
        r"^\s*comp_Constraints\(mm\)\s*$", output, re.MULTILINE
    ), "Expected `comp_Constraints(mm)` declaration over parent set."
    assert not re.search(
        r"^\s*comp_Constraints\(m\)\s*$", output, re.MULTILINE
    ), "comp_Constraints must NOT be declared over dynamic subset `m`."


@pytest.mark.integration
def test_lmp2_comp_constraints_body_keeps_subset_head():
    """The complementarity equation BODY must keep the dynamic subset in
    its head (`comp_Constraints(m)..`) so GAMS restricts the equation
    to populated subset members. This mirrors the original NLP source
    pattern (`Constraints(m)..`) and is fully accepted by GAMS when the
    declaration uses the parent set.
    """
    src = "data/gamslib/raw/lmp2.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/lmp2.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    assert re.search(
        r"^\s*comp_Constraints\(m\)\.\.", output, re.MULTILINE
    ), "Expected body `comp_Constraints(m)..` to preserve the subset head."


@pytest.mark.integration
def test_lmp2_irrelevant_models_unaffected():
    """`Products(p)` is declared and defined over the same domain `p`
    (not parent/subset). Its multiplier `nu_Products` should still be
    declared over `p` — declaration_domain falls back to `domain` when
    they match.
    """
    src = "data/gamslib/raw/lmp2.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/lmp2.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    assert re.search(
        r"^\s*nu_Products\(p\)\s*$", output, re.MULTILINE
    ), "Expected `nu_Products(p)` declaration unchanged."

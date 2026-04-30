"""Sprint 25 / #1245: camcge corpus regression for multiplier subset guards.

Pre-fix: camcge's emitted MCP triggers EXECERROR=4 at PATH solve time
because `stat_pd(i)` and `stat_xxd(i)` contain CES-derivative terms
multiplied by multipliers (`nu_esupply(i)`, `nu_costmin(i)`, ...)
whose source equations (`esupply(it)`, `costmin(it)`) are defined
only on the traded subset `it`. For non-traded indices `in`, the CES
expressions evaluate to UNDF (`1/gamma(in) = 1/0`), aborting the solve.

Post-fix: each multiplier-bearing term in the stationarity body is
wrapped with `$(it(i))` (the source equation's body-domain filter),
so GAMS skips evaluation entirely for non-traded indices.
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
def test_camcge_stat_pd_wraps_traded_only_multiplier_terms():
    """`nu_esupply(i)` and `nu_costmin(i)` contributions to stat_pd(i)
    must be wrapped in `$(it(i))` since esupply/costmin are defined
    only on the traded subset.
    """
    src = "data/gamslib/raw/camcge.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/camcge.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)
    # Match the full `stat_pd(i)..` block (header through terminating `;`)
    # so the assertions hold even when `_wrap_long_equation_line` splits
    # the body across multiple physical lines.
    stat_pd_match = re.search(r"(?ms)^\s*stat_pd\(i\)\.\..*?;", output)
    assert stat_pd_match is not None, "stat_pd(i) equation block not found in MCP"
    stat_pd_block = stat_pd_match.group(0)

    # Match `... * nu_esupply(i))$(it(i))` form (the value-expr is the
    # full Binary("*",...) wrapped, with `it(i)` as the dollar condition).
    assert re.search(r"\* nu_esupply\(i\)\)\$\(it\(i\)\)", stat_pd_block, re.DOTALL), (
        "Expected `nu_esupply(i)` term to be wrapped in `$(it(i))`. Equation block:\n"
        + stat_pd_block[:500]
    )
    assert re.search(r"\* nu_costmin\(i\)\)\$\(it\(i\)\)", stat_pd_block, re.DOTALL), (
        "Expected `nu_costmin(i)` term to be wrapped in `$(it(i))`. Equation block:\n"
        + stat_pd_block[:500]
    )


@pytest.mark.integration
def test_camcge_stat_pd_does_not_wrap_all_i_multiplier_terms():
    """`nu_absorption(i)` and `nu_sales(i)` come from equations defined
    over the full `i` domain (no parent/subset split). Their terms in
    stat_pd must NOT be wrapped — wrapping would drop contributions
    from non-traded indices.
    """
    src = "data/gamslib/raw/camcge.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/camcge.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)
    stat_pd_match = re.search(r"(?ms)^\s*stat_pd\(i\)\.\..*?;", output)
    assert stat_pd_match is not None
    stat_pd_block = stat_pd_match.group(0)

    # nu_absorption(i) and nu_sales(i) should appear bare — no $(...)
    # wrapping immediately around them.
    assert re.search(
        r"\* nu_absorption\(i\)(?!\)\$\()", stat_pd_block, re.DOTALL
    ), "`nu_absorption(i)` should NOT be wrapped (full-domain equation)."
    assert re.search(
        r"\* nu_sales\(i\)(?!\)\$\()", stat_pd_block, re.DOTALL
    ), "`nu_sales(i)` should NOT be wrapped (full-domain equation)."


@pytest.mark.integration
def test_camcge_stat_xxd_wraps_traded_only_multiplier_terms():
    """`stat_xxd(i)` similarly contains contributions from
    `cet(it)`, `esupply(it)`, `armington(it)`, `costmin(it)` that
    must be wrapped in `$(it(i))`.
    """
    src = "data/gamslib/raw/camcge.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/camcge.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)
    stat_xxd_match = re.search(r"(?ms)^\s*stat_xxd\(i\)\.\..*?;", output)
    assert stat_xxd_match is not None, "stat_xxd(i) equation block not found in MCP"
    stat_xxd_block = stat_xxd_match.group(0)

    # Each traded-only multiplier should appear with the wrap.
    for mult in ("nu_cet", "nu_esupply", "nu_armington", "nu_costmin"):
        assert re.search(rf"\* {mult}\(i\)\)\$\(it\(i\)\)", stat_xxd_block, re.DOTALL), (
            f"Expected `{mult}(i)` to be wrapped in `$(it(i))`. Equation block:\n"
            + stat_xxd_block[:500]
        )

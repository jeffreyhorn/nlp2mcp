"""Sprint 38 Day 11 / #1062: tricp's collapsed stationarity head domain.

`tricp` declares `slp(n,n)` / `sln(n,n)`.  In GAMS that is the full `n x n`
product — every one of `card(n)**2` columns exists — but in an equation
*definition* a repeated controlling index binds to the SAME element, so the head
the emitter wrote from that declared domain,

    stat_slp(n,n)..  ( ... )$(e(n,n)) =E= 0;

ranged over the 20 diagonal pairs only.  `e` (54 edges) has no self-loops, so
`$(e(n,n))` was false for all of them and the block generated ZERO rows::

    ---- stat_slp  =E=
                    NONE

leaving all 54 on-edge `slp` columns (and 54 `sln`) with nothing to pair
against: `**** SOLVE ... ABORTED, EXECERROR = 108`.

`dedupe_repeated_variable_domains` rewrites the repeat to a fresh alias before
differentiation, so the head spans `n x n__` and `e` selects the 54 edges.
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
    from src.kkt.repeated_domain import dedupe_repeated_variable_domains

    model = parse_model_file(gms_path)
    normalize_model(model)
    dedupe_repeated_variable_domains(model)
    j_eq, j_ineq = compute_constraint_jacobian(model)
    grad = compute_objective_gradient(model)
    kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
    return emit_gams_mcp(kkt)


@pytest.mark.integration
def test_tricp_stationarity_head_spans_the_product():
    src = "data/gamslib/raw/tricp.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/tricp.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    assert "Alias(n, n__);" in output, "expected the minted alias to be declared"

    for var in ("slp", "sln"):
        head = re.search(rf"^stat_{var}\(([^)]*)\)\.\.", output, re.MULTILINE)
        assert head is not None, f"stat_{var} definition not emitted"
        indices = [s.strip() for s in head.group(1).split(",")]
        assert len(indices) == len(set(indices)), (
            f"stat_{var} head domain {indices} repeats a symbol — GAMS binds a "
            f"repeated controlling index to the same element, so the block "
            f"generates only the diagonal and every off-diagonal column of "
            f"{var} is left unmatched in the MCP."
        )
        assert indices == ["n", "n__"]

    # The guard must follow the head. `$(e(n,n))` is the diagonal of an
    # edge set with no self-loops — i.e. identically false.
    assert "$(e(n,n))" not in output, (
        "found the diagonal-collapsed guard `e(n,n)`; the gradient-condition "
        "remap must claim each de-duplicated domain slot at most once"
    )
    assert "$(e(n,n__))" in output


@pytest.mark.integration
def test_tricp_bound_complementarity_head_spans_the_product():
    """The same collapse hit `comp_lo_slp`, which pairs with `piL_slp`."""
    src = "data/gamslib/raw/tricp.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/tricp.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    for var in ("slp", "sln"):
        assert f"comp_lo_{var}(n,n__).." in output
        assert f"comp_lo_{var}(n,n).." not in output

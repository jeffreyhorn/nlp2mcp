"""Sprint 38 Day 12 / #983 + #1325: elec's stationarity guards must name their
own summation index.

elec's objective sums over the strictly upper-triangular pair set `ut(i,j)`:

    obj.. potential =e= sum{ut(i,j), 1.0/sqrt(sqr(x[i]-x[j]) + ...)};

so a point `p` appears in a pair either as the first or the second member, and
`stat_x(p)` needs BOTH sums, each restricted to pairs containing `p`:

    stat_x(i).. sum(j__$(ut(i,j__)), ...) + sum(i__$(ut(i__,i)), ...) + ...

Pre-fix the emit had `sum(j__$(ut(i,i)), ...)` — `ut(i,i)` is the DIAGONAL of a
strictly upper-triangular set, i.e. structurally empty, so half the gradient was
silently dropped — and `sum(i__$(ut(i,j)), ...)`, whose guard does not constrain
`i__` at all, so `i__ = i` was admitted and `d = 0` reached a divisor:
`**** Exec Error at line 99: division by zero (0)`.

Two independent defects produced that, in two different files:
  1. `_diff_sum`'s partial-collapse left the condition's matched position free.
  2. `_replace_indices_in_expr`'s SetMembershipTest branch mistook an
     AD-generated sum index (self-mapped by the Sum branch so it survives) for a
     concrete element and positionally resolved it against `ut`'s DECLARED
     domain — which for `Set ut(i,i)` is `i` at both positions.
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
def test_elec_no_diagonal_ut_guard():
    src = "data/gamslib/raw/elec.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/elec.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    assert "$(ut(i,i))" not in output, (
        "found the diagonal guard `$(ut(i,i))`. `ut` is strictly upper "
        "triangular, so its diagonal is empty and the guarded sum contributes "
        "NOTHING — half the gradient is silently dropped."
    )


@pytest.mark.integration
def test_elec_every_guard_constrains_its_own_sum_index():
    """The gate's invariant, asserted structurally rather than by error count.

    A run that merely stops erroring while keeping an unconstrained guard has
    dropped or corrupted gradient terms and is a FALSE pass.
    """
    src = "data/gamslib/raw/elec.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/elec.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    # Every `sum(<idx>$(ut(a,b)), ...)` must have <idx> among {a, b}.
    pairs = re.findall(r"sum\((\w+)\$\(ut\((\w+),(\w+)\)\)", output)
    assert pairs, "expected guarded sums over `ut` in the emitted stationarity"
    for sum_idx, a, b in pairs:
        assert sum_idx in (a, b), (
            f"sum({sum_idx}$(ut({a},{b}))) does not constrain its own summation "
            f"index {sum_idx!r} — every pair with {sum_idx} free is admitted, "
            "including the degenerate one that makes the distance zero."
        )

    # And the two halves of the gradient must both be present.
    assert re.search(r"sum\(j__\$\(ut\(i,j__\)\)", output), "missing the i-as-first-member half"
    assert re.search(r"sum\(i__\$\(ut\(i__,i\)\)", output), "missing the i-as-second-member half"


@pytest.mark.integration
def test_elec_set_declaration_is_left_alone():
    """`Set ut(i,i)` is a DECLARATION domain — repeated there means the full
    product, which is what the source intends. Only *guards* were wrong."""
    src = "data/gamslib/raw/elec.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/elec.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)
    assert re.search(
        r"^\s*ut\(i,i\)", output, re.MULTILINE
    ), "the re-emitted `Set ut(i,i)` declaration must be preserved verbatim"

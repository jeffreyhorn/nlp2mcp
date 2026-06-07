"""Sprint 27 #1378: under ``--nlp-presolve`` the emitted MCP must NOT re-emit
self-referential source parameter assignments, because the warm-start
``$include <source>.gms`` re-executes every source assignment exactly once.

launch.gms adjusts two engine-cost coefficients in place::

    pre2('stage-3') = pre2('stage-3')*10**pre3('stage-3');
    pre4('stage-3') = pre4('stage-3')*10**pre5('stage-3');

Before the fix, the MCP emitted these assignments AND ``$include``d
launch.gms, so the coefficients were DOUBLE-applied — corrupting the
objective for both the embedded NLP pre-solve and the final MCP. launch
then "solved" (MODEL STATUS 1 via presolve retry) to cost 2604.01, a 13.3%
mismatch vs the NLP optimum 2257.80.

The fix (``skip_self_ref_presolve`` in
``emit_computed_parameter_assignments``) suppresses the self-referential
assignment under presolve only; the ``$include`` applies it once. With it,
launch's embedded NLP and MCP both reach 2257.80 → ``compare_match``.

This guards the emit-level contract (no GAMS needed, so it runs in CI):
  - presolve emit: no ``pre2(...) = ... pre2(...)`` self-reference, but the
    ``$include`` IS present (the single correct application).
  - cold (non-presolve) emit: the self-referential assignment IS present
    (there is no ``$include`` to provide it, so the MCP must apply it).
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


def _emit_mcp_for(gms_path: str, *, nlp_presolve: bool) -> str:
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
    return emit_gams_mcp(
        kkt,
        nlp_presolve=nlp_presolve,
        source_file=gms_path if nlp_presolve else None,
    )


# A line that assigns pre2 (optionally indexed) from an RHS that references pre2.
_SELF_REF = re.compile(r"^\s*pre([24])\b[^=]*=\s*[^;]*\bpre\1\b", re.MULTILINE)


@pytest.mark.integration
def test_launch_presolve_omits_self_referential_param_assignment():
    """#1378: the presolve MCP must not double-apply launch's in-place
    ``pre2``/``pre4`` adjustment — it is suppressed here and provided once by
    the ``$include``."""
    src = "data/gamslib/raw/launch.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/launch.gms is gitignored on this runner.")

    output = _emit_mcp_for(src, nlp_presolve=True)

    # The $include (single correct application) must be present.
    assert (
        "$include" in output and "launch.gms" in output
    ), "Presolve emit must include the source model for the NLP warm-start."
    # The self-referential pre2/pre4 assignment must NOT be re-emitted.
    match = _SELF_REF.search(output)
    assert match is None, (
        "Found a self-referential pre2/pre4 assignment in the PRESOLVE emit — "
        "this is double-applied with the $include and corrupts the objective "
        f"(#1378). Offending line:\n{match.group(0) if match else ''}"
    )


@pytest.mark.integration
def test_launch_cold_keeps_self_referential_param_assignment():
    """Guard the other direction: without presolve there is no ``$include``, so
    the in-place adjustment MUST be emitted by the MCP itself."""
    src = "data/gamslib/raw/launch.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/launch.gms is gitignored on this runner.")

    output = _emit_mcp_for(src, nlp_presolve=False)

    assert _SELF_REF.search(output) is not None, (
        "Cold (non-presolve) emit must keep the in-place pre2/pre4 adjustment — "
        "there is no $include to apply it, so suppressing it would drop the "
        "coefficient adjustment entirely."
    )

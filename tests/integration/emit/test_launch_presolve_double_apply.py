"""Sprint 27 #1378: under ``--nlp-presolve`` the emitted MCP must NOT re-emit
self-referential source parameter assignments, because the warm-start
``$include <source>.gms`` re-executes every source assignment exactly once.

The motivating case is launch.gms, which adjusts two engine-cost coefficients
in place::

    pre2('stage-3') = pre2('stage-3')*10**pre3('stage-3');
    pre4('stage-3') = pre4('stage-3')*10**pre5('stage-3');

Before the fix, the MCP emitted these assignments AND ``$include``d
launch.gms, so under ``$onMultiR`` (where the ``/data/`` re-declaration does
not reset) the coefficients were DOUBLE-applied — corrupting the objective for
both the embedded NLP pre-solve and the final MCP. launch then "solved"
(MODEL STATUS 1 via presolve retry) to cost 2604.01, a 13.3% mismatch vs the
NLP optimum 2257.80.

The fix (``skip_self_ref_presolve`` in
``emit_computed_parameter_assignments``) suppresses the self-referential
assignment under presolve only; the ``$include`` applies it once.

The primary guard here uses a committed minimal synthetic fixture
(``tests/fixtures/issue_1378_self_ref_param.gms``) so the regression runs in
PR CI regardless of whether the (gitignored) GAMSlib ``launch.gms`` was
downloaded. Two additional checks exercise the real launch model and skip
when it is absent.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SYNTH_FIXTURE = _REPO_ROOT / "tests" / "fixtures" / "issue_1378_self_ref_param.gms"
_LAUNCH_SRC = _REPO_ROOT / "data" / "gamslib" / "raw" / "launch.gms"


@pytest.fixture(autouse=True)
def _high_recursion_limit():
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        yield
    finally:
        sys.setrecursionlimit(old)


def _emit_mcp_for(gms_path: Path, *, nlp_presolve: bool) -> str:
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_file
    from src.kkt.assemble import assemble_kkt_system

    model = parse_model_file(str(gms_path))
    normalize_model(model)
    j_eq, j_ineq = compute_constraint_jacobian(model)
    grad = compute_objective_gradient(model)
    kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
    return emit_gams_mcp(
        kkt,
        nlp_presolve=nlp_presolve,
        source_file=str(gms_path) if nlp_presolve else None,
    )


def _self_ref(param: str) -> re.Pattern[str]:
    """An assignment `<param>(...) = ... <param>(...)` (LHS appears on the RHS)."""
    p = re.escape(param)
    return re.compile(rf"^\s*{p}\b[^=]*=\s*[^;]*\b{p}\b", re.MULTILINE)


# --- Primary guard: committed synthetic fixture (always runs in CI) ----------

_SYNTH_SELF_REF = _self_ref("c")


def test_presolve_omits_self_referential_param_assignment_synthetic():
    """#1378: under presolve the self-referential ``c('i2') = c('i2')*2``
    assignment must be suppressed (the ``$include`` applies it once), while the
    ``$include`` itself is still emitted."""
    assert _SYNTH_FIXTURE.exists(), f"missing committed fixture: {_SYNTH_FIXTURE}"

    output = _emit_mcp_for(_SYNTH_FIXTURE, nlp_presolve=True)

    assert (
        "$include" in output
    ), "Presolve emit must include the source model for the NLP warm-start."
    match = _SYNTH_SELF_REF.search(output)
    assert match is None, (
        "Found a self-referential `c(...) = ... c(...)` assignment in the "
        "PRESOLVE emit — it is double-applied with the $include and corrupts "
        f"parameter values (#1378). Offending line:\n{match.group(0) if match else ''}"
    )


def test_cold_keeps_self_referential_param_assignment_synthetic():
    """Guard the other direction: without presolve there is no ``$include``, so
    the in-place adjustment MUST be emitted by the MCP itself."""
    assert _SYNTH_FIXTURE.exists(), f"missing committed fixture: {_SYNTH_FIXTURE}"

    output = _emit_mcp_for(_SYNTH_FIXTURE, nlp_presolve=False)

    assert _SYNTH_SELF_REF.search(output) is not None, (
        "Cold (non-presolve) emit must keep the in-place `c(...) = c(...)*2` "
        "adjustment — there is no $include to apply it, so suppressing it would "
        "drop the adjustment entirely."
    )


# --- Real-model checks: skip when the gitignored launch.gms is absent --------

_LAUNCH_SELF_REF = re.compile(r"^\s*pre([24])\b[^=]*=\s*[^;]*\bpre\1\b", re.MULTILINE)


@pytest.mark.integration
def test_launch_presolve_omits_self_referential_param_assignment():
    """#1378 on the real launch model: the presolve MCP must not double-apply
    launch's in-place ``pre2``/``pre4`` adjustment."""
    if not _LAUNCH_SRC.exists():
        pytest.skip("data/gamslib/raw/launch.gms is gitignored on this runner.")

    output = _emit_mcp_for(_LAUNCH_SRC, nlp_presolve=True)

    assert (
        "$include" in output and "launch.gms" in output
    ), "Presolve emit must include the source model for the NLP warm-start."
    match = _LAUNCH_SELF_REF.search(output)
    assert match is None, (
        "Found a self-referential pre2/pre4 assignment in the PRESOLVE emit — "
        "this is double-applied with the $include and corrupts the objective "
        f"(#1378). Offending line:\n{match.group(0) if match else ''}"
    )


@pytest.mark.integration
def test_launch_cold_keeps_self_referential_param_assignment():
    """Real launch model, cold path: the in-place adjustment MUST be present."""
    if not _LAUNCH_SRC.exists():
        pytest.skip("data/gamslib/raw/launch.gms is gitignored on this runner.")

    output = _emit_mcp_for(_LAUNCH_SRC, nlp_presolve=False)

    assert _LAUNCH_SELF_REF.search(output) is not None, (
        "Cold (non-presolve) emit must keep the in-place pre2/pre4 adjustment — "
        "there is no $include to apply it, so suppressing it would drop the "
        "coefficient adjustment entirely."
    )

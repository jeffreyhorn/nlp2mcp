"""Sprint 25 / #1330 (round 3): under `--nlp-presolve`, the MCP-side
variable-init pass must NOT emit `var.l = ...` assignments that
would clobber the NLP solve's warm-start values.

The presolve flow is:
1. `$include source.gms` — re-runs the source's calibration (which
   sets `var.l = <init_param>` etc.)
2. `Solve nlp ...` — overwrites `.l` with the NLP optimum
3. MCP block runs the MCP solve — warm-started from the NLP optimum

If the MCP-side variable-init pass re-emits `var.l = <init_param>`
(from the parser's `l_expr_map` or `l_map` fields), it overwrites
the NLP optimum and PATH starts from the calibration values instead
of the NLP solution. This regresses warm-start quality for any
model whose calibration values differ from the NLP optimum.

Fix: skip the entire variable `.l` initialization pass (and the
loop-based `.l` init) when emitting under `--nlp-presolve`. Bounds
(`.lo`/`.up`) are still emitted earlier; fix-inactive lines still
emit; GAMS clamps to bounds at solve time.
"""

from __future__ import annotations

import re
import sys

import pytest


def _emit_mcp_for_source(
    gams_src: str, *, nlp_presolve: bool, source_file: str | None = None
) -> str:
    """Emit MCP from in-memory GAMS source.

    Args:
        gams_src: GAMS source text.
        nlp_presolve: pass-through to `emit_gams_mcp`.
        source_file: path to the source file (must be under repo root for
            `_will_emit_nlp_presolve` to allow the var-init skip — see
            `_will_emit_nlp_presolve` docstring). Defaults to None, which
            simulates the "presolve aborts" path where the skip should
            NOT fire (the var-init pass falls back to its normal
            behavior).
    """
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
        return emit_gams_mcp(
            kkt, nlp_presolve=nlp_presolve, source_file=source_file
        )
    finally:
        sys.setrecursionlimit(old)


# Source pattern: `var.l = <expr-from-calibration-param>`. Without
# the var-init-skip fix, the MCP would emit this assignment after
# the NLP solve, clobbering the warm-start.
_SRC_WITH_CALIBRATED_INIT = """
Set i / a, b /;
Parameter pd0(i) / a 1.5, b 2.5 /;
Variable pd(i), x(i), obj;
pd.l(i) = pd0(i);
x.lo(i) = 0.01;
Equation Objective, Eq(i);
Objective.. obj =e= sum(i, pd(i) * x(i));
Eq(i).. x(i) =e= 1;
Model nlp /all/;
Solve nlp using nlp minimizing obj;
"""


@pytest.mark.unit
def test_var_l_init_emitted_without_presolve():
    """Sanity: without `--nlp-presolve`, the source's `pd.l(i) = pd0(i)`
    IS emitted in the MCP (this is the existing behavior — needed for
    the no-presolve path to have any starting values).
    """
    output = _emit_mcp_for_source(_SRC_WITH_CALIBRATED_INIT, nlp_presolve=False)

    assert re.search(r"^\s*pd\.l\(i\)\s*=\s*pd0\(i\)\s*;", output, re.MULTILINE), (
        "Without --nlp-presolve, the source's `pd.l(i) = pd0(i)` should "
        "appear in the emitted MCP."
    )


@pytest.mark.unit
def test_var_l_init_skipped_when_presolve_will_actually_emit(tmp_path):
    """Under `--nlp-presolve` AND with a valid `source_file` (under repo
    root), the MCP-side variable-init pass must NOT emit
    `pd.l(i) = pd0(i)` (or any other `var.l = ...` source-level init).
    The NLP warm-start is the sole source of `.l` values.
    """
    # Materialize the source under the repo root so the presolve
    # `$include` path resolution succeeds. The presolve emit's
    # early-return checks (`_will_emit_nlp_presolve`) gate the
    # var-init skip; without a valid in-repo path the skip is
    # correctly disabled (verified by the "fallback" test below).
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[3]
    src_path = repo_root / "tmp_test_presolve_src.gms"
    src_path.write_text(_SRC_WITH_CALIBRATED_INIT)
    try:
        output = _emit_mcp_for_source(
            _SRC_WITH_CALIBRATED_INIT,
            nlp_presolve=True,
            source_file=str(src_path),
        )
    finally:
        src_path.unlink(missing_ok=True)

    assert not re.search(r"^\s*pd\.l\(i\)\s*=\s*pd0\(i\)", output, re.MULTILINE), (
        "Under --nlp-presolve (with a valid in-repo source_file), "
        "`pd.l(i) = pd0(i)` would clobber the NLP warm-start. Should "
        "be skipped."
    )


@pytest.mark.unit
def test_var_l_init_falls_back_when_presolve_aborts():
    """Issue #1330 review: when `nlp_presolve=True` but the presolve
    `$include` block is NOT actually emitted (e.g., `source_file=None`,
    or outside the repo root), the var-init pass must FALL BACK to its
    normal behavior — otherwise the MCP would have neither a warm-start
    nor any fallback init, reintroducing listing-time div-by-zero.
    """
    # source_file=None → presolve emit aborts → var-init must NOT be skipped.
    output = _emit_mcp_for_source(
        _SRC_WITH_CALIBRATED_INIT, nlp_presolve=True, source_file=None
    )

    assert re.search(r"^\s*pd\.l\(i\)\s*=\s*pd0\(i\)", output, re.MULTILINE), (
        "When presolve emit aborts (source_file=None), the var-init "
        "pass must fall back to emitting `pd.l(i) = pd0(i)` so the MCP "
        "isn't left without warm-start values."
    )


@pytest.mark.unit
def test_lower_bound_complementarity_still_emitted_under_presolve():
    """Lower bound complementarity equations (`comp_lo_X(i).. X(i) -
    lo =G= 0;`) ARE the MCP-side encoding of bounds. They must still
    emit under `--nlp-presolve` so PATH enforces feasibility.
    """
    output = _emit_mcp_for_source(_SRC_WITH_CALIBRATED_INIT, nlp_presolve=True)

    assert re.search(
        r"^\s*comp_lo_x\(i\)\.\.\s*x\(i\)\s*-\s*0\.01\s*=G=\s*0", output, re.MULTILINE
    ), (
        "Lower bound complementarity equation should still be emitted "
        "under --nlp-presolve — it's how MCP encodes the bound."
    )

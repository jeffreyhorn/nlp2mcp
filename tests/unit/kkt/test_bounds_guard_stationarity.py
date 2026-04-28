"""Sprint 25 / #1192: bounds-aware conditional stationarity.

When a variable has parameter-dependent upper or lower bounds (e.g.,
`s.up(i) = 0.99 * supc(i)` in gtm), the bound expression can collapse
to `up == lo` at runtime for indices where the parameter is zero,
making the variable effectively fixed. The MCP must mirror the NLP's
"GAMS skips fixed-variable equations" behavior by:

1. Wrapping the stationarity body in `$(v.up(d) - v.lo(d) > eps)` so
   the row collapses to `0 =E= 0` for fixed instances (avoids
   div-by-zero from derivative terms with the parameter in a
   denominator).
2. Emitting `v.fx(d)$(not (v.up(d) - v.lo(d) > eps)) = 0` so GAMS
   treats the variable as fixed for those indices.

These tests validate the helper detection and emission. The
gtm-specific corpus regression lives in
`tests/integration/emit/test_gtm_runtime_div_by_zero.py`.
"""

from __future__ import annotations

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


def _emit_mcp(gms_text: str, tmp_path) -> str:
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_file
    from src.kkt.assemble import assemble_kkt_system

    src = tmp_path / "model.gms"
    src.write_text(gms_text)
    model = parse_model_file(str(src))
    normalize_model(model)
    j_eq, j_ineq = compute_constraint_jacobian(model)
    grad = compute_objective_gradient(model)
    kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
    return emit_gams_mcp(kkt)


@pytest.mark.unit
def test_param_dependent_upper_bound_emits_guard_and_fix(tmp_path):
    """Variable with `x.up(i) = cap(i)` where cap can be 0 must:
    - Emit `x.fx(i)$(not (x.up(i) - x.lo(i) > 1e-10)) = 0` (or similar
      bounds-collapse fix).
    - Wrap stationarity body in `$(x.up(i) - x.lo(i) > 1e-10)` (or
      equivalent).
    """
    gams = """\
Set i / a, b, c /;
Parameter cap(i) / a 0, b 1, c 2 /;
Variable x(i), z;
Equation defz, cap_eq(i);
defz..      z =e= sum(i, x(i) * x(i));
cap_eq(i).. x(i) =l= cap(i);
x.up(i) = cap(i);
Model M / defz, cap_eq /;
solve M using nlp minimizing z;
"""
    output = _emit_mcp(gams, tmp_path)

    # Bounds-collapse fix line (the .fx is emitted via the existing
    # fix-inactive path that consumes kkt.stationarity_conditions).
    assert "x.fx(i)$(not (" in output and "x.up(i)" in output and "x.lo(i)" in output, (
        "Expected `x.fx(i)$(not (x.up(i) - x.lo(i) > ...)) = ...` line in emission.\n\n"
        f"Output:\n{output}"
    )

    # Stationarity body guard
    stat_x_lines = [line for line in output.splitlines() if line.startswith("stat_x")]
    assert stat_x_lines, "Expected a `stat_x` equation in the emission."
    stat_body = "\n".join(stat_x_lines)
    assert "x.up(i)" in stat_body and "x.lo(i)" in stat_body, (
        "Expected `stat_x(i)` body to be wrapped in a "
        "`$(x.up(i) - x.lo(i) > ...)` guard.\n\n"
        f"stat_x lines:\n{stat_body}"
    )


@pytest.mark.unit
def test_static_numeric_bounds_no_guard(tmp_path):
    """Variable with only numeric bounds (no parameter dependency)
    must NOT trigger the bounds-collapse guard — there's no runtime
    way for `up == lo` to surprise us when both are compile-time
    constants.
    """
    gams = """\
Variable x, z;
Equation defz, cap_eq;
defz..   z =e= x * x;
cap_eq.. x =l= 2.0;
x.up = 1.0;
Model M / defz, cap_eq /;
solve M using nlp minimizing z;
"""
    output = _emit_mcp(gams, tmp_path)

    # No bounds-guard fix line for x
    assert "x.fx" not in output or "x.fx(i)$(not" not in output, (
        "Static-bound variable should not generate a bounds-collapse fix "
        "line.\n\n"
        f"Output:\n{output}"
    )

    # stat_x body should NOT be wrapped in `$(x.up - x.lo > ...)`
    stat_x_lines = [line for line in output.splitlines() if line.startswith("stat_x")]
    if stat_x_lines:
        stat_body = "\n".join(stat_x_lines)
        assert "x.up - x.lo" not in stat_body and "x.up(...)- x.lo" not in stat_body, (
            "Static-bound variable should not have a bounds-collapse guard on "
            "its stationarity body.\n\n"
            f"stat_x lines:\n{stat_body}"
        )


@pytest.mark.unit
def test_positive_var_with_param_upper_bound(tmp_path):
    """Positive variable (implicit `x.lo = 0`) with parameter-
    dependent upper bound — common shape for gtm's `s` variable. The
    guard should still fire correctly even though `lo` isn't
    explicitly set.
    """
    gams = """\
Set i / a, b /;
Parameter limit_(i) / a 0, b 5 /;
Positive Variable x(i), z;
Equation defz, lim_eq(i);
defz..       z =e= sum(i, x(i));
lim_eq(i)..  x(i) =l= limit_(i);
x.up(i) = limit_(i);
Model M / defz, lim_eq /;
solve M using nlp maximizing z;
"""
    output = _emit_mcp(gams, tmp_path)

    # Bounds-guard fix line should be present
    assert "x.fx(i)" in output and "x.up(i)" in output, (
        "Positive variable with parameter upper bound should still trigger "
        "the bounds-collapse fix.\n\n"
        f"Output:\n{output}"
    )

    # The guard on stationarity body
    stat_x_lines = [line for line in output.splitlines() if line.startswith("stat_x")]
    assert stat_x_lines, "Expected `stat_x` equation."
    stat_body = "\n".join(stat_x_lines)
    assert "x.up(i)" in stat_body and "x.lo(i)" in stat_body, (
        f"stat_x body must be wrapped in the bounds-collapse guard.\n\nstat_x lines:\n{stat_body}"
    )

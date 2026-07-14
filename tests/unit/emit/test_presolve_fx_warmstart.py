"""Sprint 29 / #1462: the `--nlp-presolve` dual transfer must warm-start the
per-element `_fx_` equation multipliers from the fixed variables' marginals.

Each `_fx_` complementarity equation (`var(idx) =e= val`) carries an equality
multiplier `nu_<var>_fx_<idx>` that appears in the fixed element's stationarity
row. The general dual-transfer loop (`nu_<eq>.l = <eq>.m`) skips these because
the `_fx_` equations are NOT original NLP equations — the NLP fixes the column
via `.fx`, so the fix dual surfaces as the *variable* marginal `var.m(idx)`, not
an equation marginal. Left at the default `.l = 0`, those multipliers leave a
nonzero stationarity residual at the fixed element (rocket: `stat_step` rel
0.497) and PATH diverges on the non-convex model.

`_emit_presolve_fx_warmstart` emits `nu_<var>_fx_<idx>.l = <var>.m(<idx>);` for
exactly the active `_fx_` multipliers (the Layer-4 cohort), mirroring
`_emit_presolve_fx_unfix`'s `eq_paired_in_mcp` gate.
"""

from __future__ import annotations

import re
import sys

import pytest


def _build_kkt(gams_src: str):
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
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
        return assemble_kkt_system(model, grad, j_eq, j_ineq)
    finally:
        sys.setrecursionlimit(old)


# A boundary-fixed dynamic chain (mirrors rocket's `v.fx('h0')`): the fixed
# element `t1` is inside the active stationarity domain, so its `_fx_` equation
# is paired in the MCP and its multiplier is referenced.
_SRC_FIXED_BOUNDARY = """
Set t / t1, t2, t3 /;
Variable x(t), obj;
x.fx('t1') = 1;
Equation Objective, link(t);
Objective.. obj =e= sum(t, sqr(x(t)));
link(t)$(ord(t) > 1).. x(t) =e= x(t-1) + 1;
Model nlp /all/;
Solve nlp using nlp minimizing obj;
"""

_SRC_NO_FIX = """
Set t / t1, t2, t3 /;
Variable x(t), obj;
Equation Objective, link(t);
Objective.. obj =e= sum(t, sqr(x(t)));
link(t)$(ord(t) > 1).. x(t) =e= x(t-1) + 1;
Model nlp /all/;
Solve nlp using nlp minimizing obj;
"""


@pytest.mark.unit
def test_fx_warmstart_emitted_for_fixed_boundary_element():
    """The `_fx_` multiplier for a fixed element with an active `_fx_` equation
    is warm-started from the variable's marginal `var.m(idx)`."""
    from src.emit.emit_gams import (
        _compute_suppressed_fx_equations,
        _emit_presolve_fx_warmstart,
    )

    kkt = _build_kkt(_SRC_FIXED_BOUNDARY)
    lines = _emit_presolve_fx_warmstart(
        kkt, _compute_suppressed_fx_equations(kkt), add_comments=True
    )
    body = "\n".join(lines)
    assert re.search(
        r"^\s*nu_x_fx_t1\.l\s*=\s*x\.m\('t1'\)\s*;", body, re.MULTILINE
    ), f"Expected `nu_x_fx_t1.l = x.m('t1');` warm-start, got:\n{body}"
    # The transfer reads the VARIABLE marginal (not an equation marginal — the
    # NLP has no `_fx_` equation), so `x_fx_t1.m` must NOT appear.
    assert "x_fx_t1.m" not in body


@pytest.mark.unit
def test_fx_warmstart_empty_without_fixed_elements():
    """No fixed elements → no `_fx_` warm-start lines (the helper returns [])."""
    from src.emit.emit_gams import (
        _compute_suppressed_fx_equations,
        _emit_presolve_fx_warmstart,
    )

    kkt = _build_kkt(_SRC_NO_FIX)
    lines = _emit_presolve_fx_warmstart(
        kkt, _compute_suppressed_fx_equations(kkt), add_comments=True
    )
    assert lines == [], f"Expected no warm-start lines for a fix-free model, got: {lines}"


@pytest.mark.unit
def test_fx_warmstart_in_full_presolve_emit(tmp_path, monkeypatch):
    """End-to-end: under `--nlp-presolve` with a valid in-repo source path, the
    full MCP emit contains the `_fx_` warm-start alongside the other dual
    transfers."""
    import src.emit.emit_gams as emit_gams_module
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_text
    from src.kkt.assemble import assemble_kkt_system

    # Resolve the repo-root + source path identically (avoid macOS /private
    # symlink mismatch that would route emit to the "outside repo root" path).
    repo_root = tmp_path.resolve()
    monkeypatch.setattr(emit_gams_module, "_REPO_ROOT", repo_root)
    src_path = repo_root / "fx_warmstart_src.gms"
    src_path.write_text(_SRC_FIXED_BOUNDARY)

    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        model = parse_model_text(_SRC_FIXED_BOUNDARY)
        normalize_model(model)
        j_eq, j_ineq = compute_constraint_jacobian(model)
        grad = compute_objective_gradient(model)
        kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
        output = emit_gams_mcp(kkt, nlp_presolve=True, source_file=str(src_path))
    finally:
        sys.setrecursionlimit(old)

    # Sanity: the presolve block actually emitted (not the "outside repo root"
    # omission path).
    assert "NLP Pre-Solve omitted" not in output
    assert re.search(
        r"^\s*nu_x_fx_t1\.l\s*=\s*x\.m\('t1'\)\s*;", output, re.MULTILINE
    ), "The `_fx_` warm-start should appear in the full --nlp-presolve emit."


# Sprint 32 P3 (#1330): a SCALAR-fixed variable (`s.fx = 2;`) stores its fixing
# in `var_def.fx` with an empty index tuple and an empty `fx_map`. `s` appears in
# the objective, so `stat_s` carries `nu_s_fx` and the `s_fx` equation is paired
# → both the warm-start transfer and the #1449 unfix must cover the scalar case
# (no index parens). The original `fx_map`-only loops skipped scalars entirely.
_SRC_SCALAR_FIX = """
Set t / t1, t2, t3 /;
Variable s, x(t), obj;
s.fx = 2;
Equation Objective, link(t);
Objective.. obj =e= sum(t, sqr(x(t) - s));
link(t)$(ord(t) > 1).. x(t) =e= x(t-1) + 1;
Model nlp /all/;
Solve nlp using nlp minimizing obj;
"""


@pytest.mark.unit
def test_fx_warmstart_emitted_for_scalar_fixed_variable():
    """A scalar `.fx` fixing warm-starts its `_fx_` multiplier from `var.m`
    (no index parens — `s.m`, not `s.m()`)."""
    from src.emit.emit_gams import (
        _compute_suppressed_fx_equations,
        _emit_presolve_fx_warmstart,
    )

    kkt = _build_kkt(_SRC_SCALAR_FIX)
    lines = _emit_presolve_fx_warmstart(
        kkt, _compute_suppressed_fx_equations(kkt), add_comments=True
    )
    body = "\n".join(lines)
    assert re.search(
        r"^\s*nu_s_fx\.l\s*=\s*s\.m\s*;", body, re.MULTILINE
    ), f"Expected `nu_s_fx.l = s.m;` (no parens) scalar warm-start, got:\n{body}"
    # Must NOT emit the invalid empty-parens form `s.m()`.
    assert "s.m()" not in body, f"Scalar marginal must be `s.m`, not `s.m()`:\n{body}"


@pytest.mark.unit
def test_fx_unfix_emitted_for_scalar_fixed_variable():
    """The #1449 unfix restores a scalar-fixed variable's natural bounds with no
    index parens (`s.lo = …; s.up = …;`), symmetric with the warm-start."""
    from src.emit.emit_gams import (
        _compute_suppressed_fx_equations,
        _emit_presolve_fx_unfix,
    )

    kkt = _build_kkt(_SRC_SCALAR_FIX)
    lines = _emit_presolve_fx_unfix(kkt, _compute_suppressed_fx_equations(kkt), add_comments=True)
    body = "\n".join(lines)
    assert re.search(
        r"^\s*s\.lo\s*=\s*[^;()]+;", body, re.MULTILINE
    ), f"Expected `s.lo = …;` (no parens) scalar unfix, got:\n{body}"
    assert re.search(
        r"^\s*s\.up\s*=\s*[^;()]+;", body, re.MULTILINE
    ), f"Expected `s.up = …;` (no parens) scalar unfix, got:\n{body}"
    # Must NOT emit the invalid empty-parens form `s.lo() =`.
    assert (
        "s.lo()" not in body and "s.up()" not in body
    ), f"Scalar unfix must have no parens:\n{body}"

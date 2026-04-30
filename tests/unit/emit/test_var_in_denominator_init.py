"""Sprint 25 / #1243: emitter auto-init for FREE vars in stationarity denominators.

When a FREE variable appears in `1/var` or `log(var)` patterns inside a
KKT-built stationarity equation, GAMS would abort with EXECERROR=1 from
div-by-zero at model-listing time (the variable defaults to `.l = 0`).

The fix emits `var.l(d) = 1;` for each such variable, mirroring the
auto-init that POSITIVE variables already receive. These tests validate
the emitter integration; the AST walker is tested separately in
`tests/unit/emit/test_collect_divisor_var_refs.py`.
"""

from __future__ import annotations

import re
import sys

import pytest


def _emit_mcp_for_source(
    gams_src: str, *, nlp_presolve: bool = False, source_file: str | None = None
) -> str:
    """Helper: parse GAMS source, build KKT, emit MCP, return output string."""
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_text
    from src.kkt.assemble import assemble_kkt_system

    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        model = parse_model_text(gams_src)
        normalize_model(model)
        j_eq, j_ineq = compute_constraint_jacobian(model)
        grad = compute_objective_gradient(model)
        kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
        return emit_gams_mcp(kkt, nlp_presolve=nlp_presolve, source_file=source_file)
    finally:
        sys.setrecursionlimit(old_limit)


# Source: minimal NLP whose objective is `prod(p, y(p))`. The
# logarithmic derivative produces `stat_y(p).. prod * sum(1/y(p))`,
# which would EXECERROR=1 on PATH unless `y.l(p) = 1` is emitted.
_PROD_OBJ_SRC = """
Set p / p1, p2, p3 /;
Variable y(p), obj;
Equation Objective, Products(p);
Objective.. obj =e= prod(p, y(p));
Products(p).. y(p) =e= 1;
Model nlp /all/;
Solve nlp using nlp minimizing obj;
"""


@pytest.mark.unit
def test_free_var_in_stationarity_denominator_gets_init():
    """A FREE variable that appears as `1/y(p)` in a stationarity equation
    should be initialized to 1 in the emitted MCP.
    """
    output = _emit_mcp_for_source(_PROD_OBJ_SRC)

    assert re.search(
        r"^\s*y\.l\(p\)\s*=\s*1\s*;", output, re.MULTILINE
    ), "Expected `y.l(p) = 1;` line in the emitted MCP. Output excerpt:\n" + "\n".join(
        line for line in output.split("\n") if "y.l" in line or "y.fx" in line
    )


@pytest.mark.unit
def test_free_var_init_skipped_when_presolve_will_emit(tmp_path, monkeypatch):
    """Under `--nlp-presolve` AND with a valid `source_file` (under
    `_REPO_ROOT`), the NLP solve provides the warm-start; the emitter
    must NOT overwrite `y.l` with the default `1`.

    Issue #1330 review: the var-init skip is gated on
    `_will_emit_nlp_presolve(...)` — passing `source_file=None` would
    correctly disable the skip (see test below).

    Uses `monkeypatch` to redirect `_REPO_ROOT` to `tmp_path` so the
    test file lives under the (patched) repo root without polluting
    the actual checkout — xdist-safe and read-only-checkout-safe.
    """
    import src.emit.emit_gams as emit_gams_module

    monkeypatch.setattr(emit_gams_module, "_REPO_ROOT", tmp_path)
    src_path = tmp_path / "tmp_test_free_var_presolve.gms"
    src_path.write_text(_PROD_OBJ_SRC)

    output = _emit_mcp_for_source(_PROD_OBJ_SRC, nlp_presolve=True, source_file=str(src_path))

    # No `y.l(p) = 1;` line should appear.
    assert not re.search(
        r"^\s*y\.l\(p\)\s*=\s*1\s*;", output, re.MULTILINE
    ), "Did NOT expect `y.l(p) = 1;` under --nlp-presolve. Output excerpt:\n" + "\n".join(
        line for line in output.split("\n") if "y.l" in line
    )


@pytest.mark.unit
def test_free_var_init_falls_back_when_presolve_aborts():
    """Issue #1330 review: when `nlp_presolve=True` but the presolve
    `$include` block won't actually emit (e.g., `source_file=None`),
    the FREE-var-in-denominator init must FALL BACK and emit
    `y.l(p) = 1;` so the MCP doesn't EXECERROR=1 from `1/y(p)` at
    listing time.
    """
    output = _emit_mcp_for_source(_PROD_OBJ_SRC, nlp_presolve=True, source_file=None)

    assert re.search(r"^\s*y\.l\(p\)\s*=\s*1\s*;", output, re.MULTILINE), (
        "When presolve emit aborts (source_file=None), the FREE-var "
        "denominator init must fall back to emitting `y.l(p) = 1;` "
        "so the MCP isn't left with a div-by-zero hazard."
    )


@pytest.mark.unit
def test_positive_var_in_denominator_uses_existing_branch():
    """A POSITIVE variable (not FREE) in stationarity denominator is
    handled by the existing POSITIVE auto-init branch — the new #1243
    branch should NOT emit a duplicate line.
    """
    src = """
    Set p / p1, p2 /;
    Positive Variable y(p);
    Variable obj;
    Equation Objective, Products(p);
    Objective.. obj =e= prod(p, y(p));
    Products(p).. y(p) =e= 1;
    Model nlp /all/;
    Solve nlp using nlp minimizing obj;
    """
    output = _emit_mcp_for_source(src)

    # POSITIVE branch emits `y.l(p) = 1;` followed by a min-clamp line.
    y_init_lines = [line for line in output.split("\n") if re.match(r"^\s*y\.l\(p\)\s*=", line)]
    # Expect exactly: `y.l(p) = 1;` and `y.l(p) = min(y.l(p), y.up(p));`
    # (NOT a third duplicate line from #1243's branch).
    assert len(y_init_lines) == 2, (
        f"Expected exactly 2 y.l(p) = ... lines (POSITIVE init + clamp), got {len(y_init_lines)}:\n"
        + "\n".join(y_init_lines)
    )
    assert any("= 1;" in line for line in y_init_lines), "Expected `y.l(p) = 1;` line"
    assert any("min(" in line for line in y_init_lines), "Expected POSITIVE clamp line"


@pytest.mark.unit
def test_free_var_with_explicit_l_skipped():
    """If the source provides explicit `y.l(p) = ...`, the new branch
    should not overwrite it (the `not has_init` guard).
    """
    src = """
    Set p / p1, p2 /;
    Variable y(p), obj;
    y.l(p) = 2;
    Equation Objective, Products(p);
    Objective.. obj =e= prod(p, y(p));
    Products(p).. y(p) =e= 1;
    Model nlp /all/;
    Solve nlp using nlp minimizing obj;
    """
    output = _emit_mcp_for_source(src)

    # The explicit `y.l(p) = 2;` should appear; the default `y.l(p) = 1;`
    # should NOT.
    assert re.search(
        r"^\s*y\.l\(\s*['\"]?p1['\"]?\s*\)\s*=\s*2", output, re.MULTILINE
    ) or re.search(
        r"^\s*y\.l\(p\)\s*=\s*2", output, re.MULTILINE
    ), "Expected explicit `y.l(...) = 2` to be preserved"
    # No `y.l(p) = 1` line.
    assert not re.search(
        r"^\s*y\.l\(p\)\s*=\s*1\s*;", output, re.MULTILINE
    ), "Expected the default `y.l(p) = 1;` to be skipped because explicit init was provided"


@pytest.mark.unit
def test_free_var_not_in_denominator_skipped():
    """A FREE variable that does NOT appear in any stationarity
    denominator should NOT receive the default `.l = 1` init.
    """
    src = """
    Set i / i1, i2 /;
    Variable z(i), obj;
    Parameter c(i) / i1 1, i2 2 /;
    Equation Objective, Constraints(i);
    Objective.. obj =e= sum(i, c(i) * z(i));
    Constraints(i).. z(i) =e= 1;
    Model nlp /all/;
    Solve nlp using nlp minimizing obj;
    """
    output = _emit_mcp_for_source(src)

    # `z` is free, doesn't appear in any 1/z denominator → no init.
    assert not re.search(
        r"^\s*z\.l\(i\)\s*=\s*1\s*;", output, re.MULTILINE
    ), "FREE var `z` is not in any denominator; should not get auto-init"

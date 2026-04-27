"""Sprint 25 Day 9 (WS2 Batch 2 remainder): emission invariants for the
three issues landed this day:

- #1276 (fawley/springchain): `.fx` lines for inactive multipliers must
  appear at most once per (multiplier, condition) pair, even when the
  upstream classification has multiple paths fixing the same multiplier.
- #1281 (lmp2): the supplemental `Parameter X(domain);` block emitted by
  `emit_pre_solve_param_assignments` must not redeclare parameters that
  the upstream `emit_original_parameters` block already declared.
- #1292 (turkpow): equation lines longer than ~60,000 chars must be
  wrapped at natural operator boundaries so GAMS doesn't reject them
  with `Error 98: Non-blank character(s) beyond max input line length
  (80000)`.

Each test is structured to fail loudly on the pre-fix behavior and pass
on the post-fix behavior. Where the bug surface needs the gamslib
sources to reproduce (fawley, lmp2, turkpow), the test skips when the
corpus isn't on the runner — mirroring other gamslib-skip tests in
the suite.

Markers: per `pyproject.toml`, the `unit` marker means "fast unit tests
with no I/O". The fawley/lmp2/turkpow tests below read
`data/gamslib/raw/*.gms` and run the full translate pipeline, so they
are marked `integration` (and turkpow is additionally `slow` because
its translation alone takes ~9 min on a typical workstation). Only
`test_short_equations_unchanged_by_wrap` is a pure in-memory synthetic
test and keeps the `unit` marker.
"""

from __future__ import annotations

import os
import sys

import pytest


@pytest.fixture(autouse=True)
def _high_recursion_limit():
    """Save/restore the recursion limit (cli sets 50000 for nested GAMS)."""
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        yield
    finally:
        sys.setrecursionlimit(old)


def _emit_mcp_for(gms_path: str) -> str:
    """Translate a .gms source through the full pipeline and return the
    emitted MCP as a string.
    """
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
def test_fawley_no_duplicate_nu_fx_lines():
    """#1276: fawley's emitted `.fx` lines for `nu_pbal` and `nu_qsb` must
    appear exactly once each. Pre-fix they appeared twice each because
    multiple upstream classification predicates (sections 2/2b/2c, 3/3a,
    etc. of the fix-inactive emission) emitted the same line.
    """
    src = "data/gamslib/raw/fawley.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/fawley.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)
    fx_lines = [line for line in output.splitlines() if line.startswith("nu_")]
    nu_pbal_fx = [line for line in fx_lines if line.startswith("nu_pbal.fx")]
    nu_qsb_fx = [line for line in fx_lines if line.startswith("nu_qsb.fx")]

    assert (
        len(nu_pbal_fx) == 1
    ), f"Expected exactly 1 nu_pbal.fx line; got {len(nu_pbal_fx)}: {nu_pbal_fx}"
    assert (
        len(nu_qsb_fx) == 1
    ), f"Expected exactly 1 nu_qsb.fx line; got {len(nu_qsb_fx)}: {nu_qsb_fx}"


@pytest.mark.integration
def test_fix_inactive_block_has_no_duplicate_lines():
    """Generalized #1276: across the entire emitted MCP, no `.fx` line
    starting with `nu_`, `lam_`, `piL_`, or `piU_` should appear more than
    once. The dedup logic in `emit_gams_mcp` makes this a strict invariant.
    """
    src = "data/gamslib/raw/fawley.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/fawley.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)
    seen: dict[str, int] = {}
    for line in output.splitlines():
        if (
            any(line.startswith(prefix) for prefix in ("nu_", "lam_", "piL_", "piU_"))
            and ".fx" in line
        ):
            seen[line] = seen.get(line, 0) + 1

    duplicates = {line: count for line, count in seen.items() if count > 1}
    assert (
        not duplicates
    ), "Found duplicate multiplier `.fx` lines in fawley emission:\n" + "\n".join(
        f"  ({c}×) {line}" for line, c in duplicates.items()
    )


@pytest.mark.integration
def test_lmp2_no_duplicate_parameter_declarations():
    """#1281: lmp2's supplemental `Parameter X(domain);` block must not
    redeclare params already in the upstream `Parameters` block. Pre-fix
    `A`, `b`, `cc` appeared in both blocks, triggering a GAMS Error 282
    symbol-redefinition compile failure.
    """
    src = "data/gamslib/raw/lmp2.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/lmp2.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    # Supplemental Parameter declarations are individual lines starting
    # with "Parameter X(...);". The upstream block uses the plural
    # "Parameters\n    X(...)" form, so they're easy to disambiguate.
    individual_decls = [line for line in output.splitlines() if line.startswith("Parameter ")]
    decl_names = [line.split()[1].split("(")[0].lower() for line in individual_decls]

    # `f` is genuinely needed (not in upstream block — it's a loop-only
    # parameter not referenced by any equation). `A`, `b`, `cc` MUST NOT
    # appear here because they ARE in the upstream block (case-insensitive
    # match: `A` upstream vs lowercase `a` here would still collide).
    for forbidden in ("a", "b", "cc"):
        assert forbidden not in decl_names, (
            f"`{forbidden}` was redeclared in the supplemental Parameter "
            f"block; pre-fix this triggered GAMS Error 282. Got "
            f"individual decl names: {decl_names}"
        )

    assert "f" in decl_names, (
        "`f` IS not in the upstream Parameters block (loop-only, not "
        "model-relevant), so the supplemental block must still declare it. "
        f"Got individual decl names: {decl_names}"
    )


@pytest.mark.integration
@pytest.mark.slow
def test_turkpow_max_line_length_under_gams_limit():
    """#1292: turkpow's `stat_zt` equation pre-fix was 144,628 chars on a
    single line, blowing past GAMS's 80,000-char input-line limit. The
    line-wrapping fix splits at `or`/`and`/`+`/`-` operator boundaries
    when a line exceeds the threshold; assert the resulting max line
    length stays under 80,000.
    """
    src = "data/gamslib/raw/turkpow.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/turkpow.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)
    max_line_len = max((len(line) for line in output.splitlines()), default=0)

    assert max_line_len < 80000, (
        f"Emitted line length {max_line_len} exceeds GAMS's 80,000-char "
        "input limit; pre-#1292 turkpow had a 144,628-char `stat_zt` "
        "line that triggered Error 98."
    )
    # Sanity: the wrap actually happened (some line had to be over the
    # 60,000 threshold pre-wrap). Without this, a future change that
    # silently bypasses the wrap path could pass the upper-bound check.
    has_wrapped_chunk = any(len(line) > 5000 for line in output.splitlines())
    assert has_wrapped_chunk, (
        "Expected at least one wrapped chunk over 5,000 chars (turkpow's "
        "stat_zt enumeration is large enough that the wrap should produce "
        "10k-char chunks)."
    )


@pytest.mark.unit
def test_short_equations_unchanged_by_wrap():
    """The line-wrap path is a no-op for equations under the threshold.
    Verify a small synthetic model emits without any wrap-induced
    newlines mid-equation (i.e., each equation definition fits on one
    line as before).
    """
    import tempfile

    gams = """\
Set i / 1*3 /;
Variable obj, x(i);
Equation defobj, c(i);
defobj.. obj =e= sum(i, x(i));
c(i).. x(i) =l= 10;
Model m / defobj, c /;
solve m using lp minimizing obj;
"""
    with tempfile.NamedTemporaryFile("w", suffix=".gms", delete=False) as f:
        f.write(gams)
        gms_path = f.name
    try:
        output = _emit_mcp_for(gms_path)
    finally:
        os.unlink(gms_path)

    lines = output.splitlines()

    # Short equations must not trigger the line-wrap logic, so no line in
    # the emitted output may begin with one of the wrap-continuation
    # operators (`_wrap_long_equation_line` injects the operator at the
    # start of each continuation chunk after a `\n`).
    wrap_operator_prefixes = ("or ", "and ", "+ ", "- ")
    continuation_lines = [line for line in lines if line.startswith(wrap_operator_prefixes)]
    assert not continuation_lines, (
        "Unexpected wrap-continuation line(s) for a short synthetic model: "
        f"{continuation_lines!r}"
    )

    # Cross-check: each emitted equation definition must fit on a single
    # line ending with `;` (not spilling across a continuation).
    equation_lines = [
        line for line in lines if line.startswith(("stat_", "c(", "defobj")) and ".." in line
    ]
    assert equation_lines, "Expected emitted equation definitions in output."
    for line in equation_lines:
        assert line.endswith(";"), (
            "Short equation expected to remain on a single line ending with ';'; "
            f"got line that doesn't end with ';': {line!r}"
        )

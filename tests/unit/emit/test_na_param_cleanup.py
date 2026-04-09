"""Test that parameters with NA values get cleanup before solve.

Issue #1195: Parameters containing GAMS NA (nan in IR) cause 'RHS value NA'
errors in stationarity equations. The emitter should detect these and emit
mapval(na) cleanup assignments before the solve statement.
"""

import math
import sys

import pytest


@pytest.mark.unit
def test_na_param_cleanup_emitted_before_solve(tmp_path):
    """Parameter with NA values should get a mapval(na) cleanup line."""
    gams = """\
Set i / a, b, c /;
Parameter tb(i) / a 10, b na, c 20 /;
Positive Variable x(i), obj;
Equation eq(i), objdef;
eq(i).. x(i) =g= 1;
objdef.. obj =e= sum(i, tb(i) * x(i));
Model m / eq, objdef /;
solve m using nlp minimizing obj;
"""
    gams_file = tmp_path / "test_na.gms"
    gams_file.write_text(gams)

    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        from src.ad.constraint_jacobian import compute_constraint_jacobian
        from src.ad.gradient import compute_objective_gradient
        from src.emit.emit_gams import emit_gams_mcp
        from src.ir.normalize import normalize_model
        from src.ir.parser import parse_model_file
        from src.kkt.assemble import assemble_kkt_system

        model = parse_model_file(str(gams_file))
        normalize_model(model)

        # Verify tb has NA in IR
        tb = model.params.get("tb")
        assert tb is not None
        assert any(math.isnan(v) for v in tb.values.values()), "tb should have NaN values"

        j_eq, j_ineq = compute_constraint_jacobian(model)
        grad = compute_objective_gradient(model)
        kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
        result = emit_gams_mcp(kkt)

        lines = result.splitlines()

        # Find the cleanup line and the solve line
        cleanup_lines = [
            (idx, line) for idx, line in enumerate(lines) if "mapval(na)" in line and "tb" in line
        ]
        solve_lines = [
            (idx, line) for idx, line in enumerate(lines) if "Solve" in line and "MCP" in line
        ]

        assert cleanup_lines, (
            "Expected a mapval(na) cleanup line for tb before solve; " "no cleanup found in output"
        )
        assert solve_lines, "Expected a Solve statement"

        # Cleanup must come before solve
        cleanup_idx = cleanup_lines[0][0]
        solve_idx = solve_lines[0][0]
        assert (
            cleanup_idx < solve_idx
        ), f"NA cleanup (line {cleanup_idx}) must come before Solve (line {solve_idx})"

        # Cleanup line should set to 1
        assert (
            "= 1;" in cleanup_lines[0][1]
        ), f"Expected cleanup to set NA to 1; got: {cleanup_lines[0][1]}"
    finally:
        sys.setrecursionlimit(old_limit)

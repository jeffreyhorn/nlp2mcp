"""Tests for lo_map/up_map bound emission in emit_gams.py.

Issue #1147: Numeric per-element bounds from lo_map/up_map must be emitted
before expression bounds (lo_expr_map/up_expr_map) so that RHS references
like r.lo("i1") resolve to the correct base value.
"""


def test_lo_map_emitted_before_expr_map(tmp_path):
    """lo_map bounds should appear before lo_expr_map in the emitted MCP."""
    gams = """\
Set i / i1, i2, i3 /;
Scalar R_min / 1 /;
Scalar alpha / 1.5 /;
Variable x(i), obj;
Positive Variable x;
x.lo(i) = R_min;
x.lo('i1') = max(R_min - alpha, x.lo('i1'));
Equation eq(i), objdef;
eq(i).. x(i) =g= 0;
objdef.. obj =e= sum(i, x(i));
Model m / eq, objdef /;
solve m using nlp minimizing obj;
"""
    gams_file = tmp_path / "test_bound_map.gms"
    gams_file.write_text(gams)

    import sys

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
        j_eq, j_ineq = compute_constraint_jacobian(model)
        grad = compute_objective_gradient(model)
        kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
        result = emit_gams_mcp(kkt)

        # Check that numeric lo bounds appear before expression lo bounds
        lines = result.split("\n")
        lo_map_line = None
        lo_expr_line = None
        for i, line in enumerate(lines):
            if "x.lo(" in line and "= 1;" in line and lo_map_line is None:
                lo_map_line = i
            if "x.lo(" in line and "max(" in line and lo_expr_line is None:
                lo_expr_line = i

        assert lo_map_line is not None, "Expected numeric x.lo bounds in output"
        if lo_expr_line is not None:
            assert lo_map_line < lo_expr_line, (
                f"Numeric lo bound (line {lo_map_line}) should appear before "
                f"expression lo bound (line {lo_expr_line})"
            )
    finally:
        sys.setrecursionlimit(old_limit)

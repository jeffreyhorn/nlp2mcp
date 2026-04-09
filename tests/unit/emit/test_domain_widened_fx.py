"""Test that domain-widened variables get .fx for out-of-subset instances.

Issue #1179: When a variable's domain is widened (e.g., n(t) → n(tl) where
t ⊂ tl), the extra instances outside the original subset must be fixed to
satisfy MCP matching.
"""

import sys

import pytest


@pytest.mark.unit
def test_widened_variable_gets_fx_for_out_of_subset(tmp_path):
    """Variable n(t) widened to n(tl) should get n.fx(tl)$(not t(tl)) = 0."""
    gams = """\
Set tl / 0, 1, 2 /;
Set t(tl) / 1, 2 /;
Positive Variable n(t), x(t), obj;
Equation eq(t), objdef;
eq(t).. x(t) + n(t) =g= 1;
objdef.. obj =e= sum(t, x(t) + n(t));
Model m / eq, objdef /;
solve m using nlp minimizing obj;
"""
    gams_file = tmp_path / "test_widen.gms"
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
        j_eq, j_ineq = compute_constraint_jacobian(model)
        grad = compute_objective_gradient(model)
        kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)

        # Manually widen n's domain from t to tl
        if not kkt.var_domain_widenings:
            kkt.var_domain_widenings = {}
        kkt.var_domain_widenings["n"] = ("tl",)

        result = emit_gams_mcp(kkt)

        # Should contain the .fx line for out-of-subset instances with
        # widened domain, subset guard, and zero fix value.
        n_fx_lines = [
            line for line in result.splitlines() if ".fx" in line and "n.fx" in line.lower()
        ]
        assert any(
            "n.fx(tl)$" in line and "t(tl)" in line and "= 0" in line for line in n_fx_lines
        ), (
            "Expected an n.fx line for the widened domain with the subset guard "
            f"and a zero fix value; fx lines: {n_fx_lines}"
        )
    finally:
        sys.setrecursionlimit(old_limit)

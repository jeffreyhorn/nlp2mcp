"""Test that empty equation instances get multiplier .fx emission.

Issue #1133: When an equation instance has no variable references (all
coefficients zero), the emitter should fix the associated multiplier to 0
to prevent GAMS MCP "empty equation but variable NOT fixed" errors.
"""

import sys

import pytest


@pytest.mark.unit
def test_empty_equation_multiplier_fx_emitted(tmp_path):
    """Multiplier for empty equation instance should get .fx = 0."""
    # Model where mbal(c) is empty for 'vacuum-res':
    # - u(c)$cr(c): vacuum-res not in cr
    # - sum(p, ap(c,p)*z(p)): ap('vacuum-res',p) all zero
    gams = """\
Set c / steel, fuel, 'vacuum-res' /;
Set p / proc1, proc2 /;
Set cr(c) / steel /;
Parameter ap(c,p) / steel.proc1 1, fuel.proc2 2 /;
Variable u(c), z(p), obj;
Positive Variable u, z;
Equation mbal(c), objdef;
mbal(c).. u(c)$cr(c) + sum(p, ap(c,p)*z(p)) =e= 0;
objdef.. obj =e= sum(c, u(c));
Model m / mbal, objdef /;
solve m using nlp minimizing obj;
"""
    gams_file = tmp_path / "test_empty_eq.gms"
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
        result = emit_gams_mcp(kkt)

        # Find nu_mbal.fx lines
        fx_lines = [line for line in result.splitlines() if "nu_mbal.fx" in line and "= 0" in line]

        # vacuum-res should have a .fx = 0 line
        vr_fx = [line for line in fx_lines if "vacuum-res" in line]
        assert vr_fx, (
            "Expected nu_mbal.fx('vacuum-res') = 0 for empty equation; "
            f"all nu_mbal.fx lines: {fx_lines}"
        )

        # steel and fuel should NOT have .fx = 0 from empty detection
        # (they may have .fx from other sections like stationarity conditions)
        empty_section_lines = []
        in_empty_section = False
        for line in result.splitlines():
            if "empty equation instances" in line.lower():
                in_empty_section = True
            elif in_empty_section and line.strip() == "":
                in_empty_section = False
            elif in_empty_section and "nu_mbal.fx" in line:
                empty_section_lines.append(line)

        # Only vacuum-res should be in the empty section
        for line in empty_section_lines:
            assert "vacuum-res" in line, f"Unexpected empty-equation .fx for non-vacuum-res: {line}"
    finally:
        sys.setrecursionlimit(old_limit)

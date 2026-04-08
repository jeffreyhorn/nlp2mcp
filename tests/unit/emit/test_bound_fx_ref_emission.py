"""Test that .lo/.up bounds are emitted when referenced by .fx expressions.

When a variable has complementarity equations (comp_lo/comp_up), the emitter
suppresses .lo/.up emission to avoid double-bounding. But if a .fx expression
references the bound (e.g., k.fx(tfirst) = k.lo(tfirst)), the bound must
still be emitted so the .fx assignment can resolve.
"""

import sys

import pytest


@pytest.mark.unit
def test_lo_emitted_when_fx_references_lo(tmp_path):
    """k.lo should be emitted when k.fx(tfirst) = k.lo(tfirst)."""
    gams = """\
Set t / 1990, 1991, 1992 /;
Set tfirst(t) / 1990 /;
Scalar k0 / 3 /;
Positive Variable k(t), obj;
Equation objdef, kk(t);
k.lo(t) = k0;
k.fx(tfirst) = k.lo(tfirst);
objdef.. obj =e= sum(t, k(t));
kk(t).. k(t) =g= 0;
Model m / objdef, kk /;
solve m using nlp minimizing obj;
"""
    gams_file = tmp_path / "test_fx_ref.gms"
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

        # k should have complementarity (comp_lo_k paired with piL_k)
        assert "comp_lo_k" in result, "Expected comp_lo_k equation"

        # k.lo must still be emitted despite complementarity suppression
        assert "k.lo(" in result, (
            "k.lo bounds must be emitted when k.fx references k.lo; "
            f"got:\n{[line for line in result.splitlines() if 'k.lo' in line.lower() or 'k.fx' in line.lower()]}"
        )

        # k.fx should reference k.lo
        assert "k.fx(" in result, "Expected k.fx assignment"
    finally:
        sys.setrecursionlimit(old_limit)


@pytest.mark.unit
def test_up_emitted_when_fx_references_up(tmp_path):
    """k.up should be emitted when k.fx(tlast) = k.up(tlast)."""
    gams = """\
Set t / 1990, 1991, 1992 /;
Set tlast(t) / 1992 /;
Scalar k_max / 10 /;
Positive Variable k(t), obj;
Equation objdef, kk(t);
k.up(t) = k_max;
k.fx(tlast) = k.up(tlast);
objdef.. obj =e= sum(t, k(t));
kk(t).. k(t) =l= 100;
Model m / objdef, kk /;
solve m using nlp minimizing obj;
"""
    gams_file = tmp_path / "test_fx_up_ref.gms"
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

        assert "k.up(" in result, "k.up bounds must be emitted when k.fx references k.up"
        assert "k.fx(" in result, "Expected k.fx assignment"
    finally:
        sys.setrecursionlimit(old_limit)

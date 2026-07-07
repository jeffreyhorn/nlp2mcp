"""Sprint 30 P7 (Class-B `stat_pz`): the `--nlp-presolve` dual transfer must
warm-start **mixed-case** equation multipliers.

`get_solved_model_equations()` lowercases its names, but `model_ir.equalities`
preserves the source casing (e.g. `eqDs`, `eqE`, `SAMEQ`). The general
dual-transfer loop matched `eq_name in eq_set` case-sensitively, so every
mixed-case equation was silently skipped — its `nu_<eq>.l = <eq>.m` warm-start
never emitted. That left the price stationarity rows non-zero at the NLP optimum
(the CGE `stat_pz` rel-1.0 Class-B fingerprint: irscge/lrgcge/moncge only
warm-started their all-lowercase price-equation duals). The fix maps the
lowercase name back to the source casing so the transfer is case-insensitive.
"""

from __future__ import annotations

import re
import sys

import pytest

pytestmark = pytest.mark.unit

# Two equalities with MIXED-case names (`eqFoo`, `Bar`) alongside an all-lowercase
# one (`link`). Pre-fix, only `link`'s dual was transferred; `eqFoo`/`Bar` were
# skipped by the case-sensitive membership test.
_SRC_MIXED_CASE = """
Set t / t1, t2, t3 /;
Variable x(t), y(t), obj;
Equation Objective, eqFoo(t), Bar(t), link(t);
Objective.. obj =e= sum(t, sqr(x(t)) + sqr(y(t)));
eqFoo(t).. y(t) =e= 2*x(t);
Bar(t).. x(t) =e= y(t) + 1;
link(t)$(ord(t) > 1).. x(t) =e= x(t-1) + 1;
Model nlp /all/;
Solve nlp using nlp minimizing obj;
"""


def _emit_presolve(tmp_path, monkeypatch) -> str:
    import src.emit.emit_gams as emit_gams_module
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_text
    from src.kkt.assemble import assemble_kkt_system

    repo_root = tmp_path.resolve()
    monkeypatch.setattr(emit_gams_module, "_REPO_ROOT", repo_root)
    src_path = repo_root / "mixed_case_src.gms"
    src_path.write_text(_SRC_MIXED_CASE)

    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        model = parse_model_text(_SRC_MIXED_CASE)
        normalize_model(model)
        j_eq, j_ineq = compute_constraint_jacobian(model)
        grad = compute_objective_gradient(model)
        kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
        return emit_gams_mcp(kkt, nlp_presolve=True, source_file=str(src_path))
    finally:
        sys.setrecursionlimit(old)


def test_mixed_case_equation_duals_are_transferred(tmp_path, monkeypatch):
    output = _emit_presolve(tmp_path, monkeypatch)
    assert "NLP Pre-Solve omitted" not in output
    # The mixed-case duals must be warm-started with SOURCE casing (matching the
    # nu_<eq> multiplier names used in the stationarity rows), not skipped.
    assert re.search(
        r"^\s*nu_eqFoo\.l\(t\)\s*=\s*eqFoo\.m\(t\)\s*;", output, re.MULTILINE
    ), "mixed-case `eqFoo` dual should be transferred"
    assert re.search(
        r"^\s*nu_Bar\.l\(t\)\s*=\s*Bar\.m\(t\)\s*;", output, re.MULTILINE
    ), "mixed-case `Bar` dual should be transferred"
    # The all-lowercase equality is still transferred (regression guard).
    assert re.search(r"^\s*nu_link\.l\(t\)\s*=\s*link\.m\(t\)\s*;", output, re.MULTILINE)

"""Unit tests for Sprint 27 #1356/#1357 comp_up subset/superset narrowing.

When a variable's upper bound is assigned over a STRICT subset of its declared
domain and the bound RHS reads a parameter declared over that same subset
(fawley ``u.up(cr) = crdat(cr,"supply")`` for ``u(c)`` with ``cr(c)``; otpop
``x.up(t) = xb(t)`` for ``x(tt)`` with ``t(tt)``), the flat-conjunction guard
``subset(parent) and param(parent,...) < inf`` makes GAMS evaluate the parameter
lookup for every parent element — including ``parent ∉ subset`` — triggering
``$171``.  The fix narrows the ``comp_up`` equation domain to the subset and
reindexes the body ``parent → subset``.
"""

from __future__ import annotations

import sys

import pytest


@pytest.mark.unit
def test_extract_subset_predicate_detects_subset_guard():
    from src.ir.ast import Binary, Const, SetMembershipTest, SymbolRef
    from src.ir.model_ir import ModelIR
    from src.ir.symbols import SetDef
    from src.kkt.complementarity import _extract_subset_predicate

    ir = ModelIR()
    ir.sets["c"] = SetDef(name="c", members=["a", "b", "d"])
    ir.sets["cr"] = SetDef(name="cr", members=["a", "b"], domain=("c",))  # strict subset

    # cr(c): subset predicate over parent c (in var_domain) → (subset, parent)
    cond = SetMembershipTest("cr", (SymbolRef("c"),))
    assert _extract_subset_predicate(cond, ("c",), ir) == ("cr", "c")

    # A non-membership condition → None
    assert _extract_subset_predicate(Binary("<", SymbolRef("c"), Const(1.0)), ("c",), ir) is None

    # Parent not in var_domain → None
    assert _extract_subset_predicate(cond, ("k",), ir) is None


@pytest.mark.unit
def test_extract_subset_predicate_ignores_pure_alias():
    """A pure alias (same members, no narrowing needed) must NOT be treated as a
    strict subset — partition.py emits no SetMembershipTest for aliases, and
    narrowing on an alias would be a no-op that risks domain churn."""
    from src.ir.ast import SetMembershipTest, SymbolRef
    from src.ir.model_ir import ModelIR
    from src.ir.symbols import AliasDef, SetDef
    from src.kkt.complementarity import _extract_subset_predicate

    ir = ModelIR()
    ir.sets["c"] = SetDef(name="c", members=["a", "b"])
    ir.aliases["cc"] = AliasDef(name="cc", target="c")

    cond = SetMembershipTest("cc", (SymbolRef("c"),))
    assert _extract_subset_predicate(cond, ("c",), ir) is None


@pytest.mark.unit
def test_bound_expr_subset_dependency_detects_subset_param():
    from src.ir.ast import ParamRef
    from src.ir.model_ir import ModelIR
    from src.ir.symbols import ParameterDef, SetDef
    from src.kkt.complementarity import _bound_expr_subset_dependency

    ir = ModelIR()
    ir.sets["c"] = SetDef(name="c", members=["a", "b", "d"])
    ir.sets["cr"] = SetDef(name="cr", members=["a", "b"], domain=("c",))
    # crdat declared over (cr, *) — first index is a strict subset
    ir.add_param(ParameterDef(name="crdat", domain=("cr", "*")))

    # crdat(c,"supply") references a param declared over subset cr
    rhs = ParamRef("crdat", ("c", "supply"))
    assert _bound_expr_subset_dependency(rhs, ir) == "cr"

    # A param declared over the FULL set is NOT a subset dependency (gtm/ibm1
    # false-positive guard from the corpus sweep §5.2).
    ir.add_param(ParameterDef(name="pc", domain=("c", "c")))
    assert _bound_expr_subset_dependency(ParamRef("pc", ("c", "c")), ir) is None


@pytest.mark.unit
def test_comp_up_subset_narrowing_end_to_end(tmp_path):
    """Mini fawley-shaped model: ``u(c)`` with ``u.up(cr) = sup(cr)`` and
    ``cr(c)`` → the comp_up equation must be narrowed to ``comp_up_u(cr)`` with
    the body reindexed to ``cr`` (no flat ``cr(c) and sup(c) < inf`` guard that
    would $171 on c ∉ cr)."""
    gams = """\
Set c / a, b, d /;
Set cr(c) / a, b /;
Parameter sup(cr) / a 100, b 165 /;
Variable u(c), z;
Equation obj, lim(c);
u.up(cr) = sup(cr);
obj.. z =e= sum(c, u(c));
lim(c).. u(c) =g= 1;
Model m / obj, lim /;
solve m using nlp maximizing z;
"""
    gms_file = tmp_path / "mini_fawley.gms"
    gms_file.write_text(gams)
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        from src.ad.constraint_jacobian import compute_constraint_jacobian
        from src.ad.gradient import compute_objective_gradient
        from src.emit.emit_gams import emit_gams_mcp
        from src.ir.normalize import normalize_model
        from src.ir.parser import parse_model_file
        from src.kkt.assemble import assemble_kkt_system

        model = parse_model_file(str(gms_file))
        neq, _ = normalize_model(model)
        grad = compute_objective_gradient(model)
        j_eq, j_ineq = compute_constraint_jacobian(model, neq)
        kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
        out = emit_gams_mcp(kkt)
    finally:
        sys.setrecursionlimit(old)

    comp_lines = [ln for ln in out.splitlines() if ln.startswith("comp_up_u")]
    assert comp_lines, f"Expected a comp_up_u equation. Output:\n{out[:1500]}"
    line = comp_lines[0]
    # Narrowed to the subset domain cr, body reindexed to cr, NO flat
    # `cr(c) and sup(c) < inf` conjunction.
    assert "comp_up_u(cr)" in line, f"Expected narrowed domain comp_up_u(cr). Got:\n{line}"
    assert "sup(cr)" in line and "u(cr)" in line, f"Body must reindex to cr. Got:\n{line}"
    assert "cr(c)" not in line, (
        f"The subset predicate must NOT remain as a flat conjunction in the "
        f"guard (that is the $171 bug). Got:\n{line}"
    )

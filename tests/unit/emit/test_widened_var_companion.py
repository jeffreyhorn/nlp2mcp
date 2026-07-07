"""Presolve widened-VARIABLE companion emit (Issue #1449, variable analog).

Under ``--nlp-presolve`` the MCP body needs a domain-widened variable at its
parent-set index (e.g. ``n(tl)`` in ``stat_m``), but the source ``$include``
re-declares it at its subset domain (``n(t)``) — GAMS rejects the two coexisting
declarations ($184 Domain list redefined). The fix mirrors the #1449 param
companion: declare the source var at its subset domain, and emit a ``n__pw``
FREE companion at the widened domain, bound to the source var on the subset by a
``couple_n`` equality, with the MCP stationarity rewired to the companion.

These tests guard the two helpers (`_rewrite_widened_var_refs`,
`_emit_widened_var_companions`) and the end-to-end presolve emit.
"""

from __future__ import annotations

import sys

import pytest

from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.gradient import compute_objective_gradient
from src.emit.emit_gams import (
    _emit_widened_var_companions,
    _rewrite_widened_var_refs,
    _widened_var_outofsubset_condition,
)
from src.emit.templates import emit_variables
from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_file
from src.kkt.assemble import assemble_kkt_system

pytestmark = pytest.mark.unit

_MODEL = """\
Set tl / 0, 1, 2 /;
Set t(tl) / 1, 2 /;
Positive Variable n(t), x(t), obj;
Equation eq(t), objdef;
eq(t).. x(t) + n(t) =g= 1;
objdef.. obj =e= sum(t, x(t) + n(t));
Model m / eq, objdef /;
solve m using nlp minimizing obj;
"""


def _kkt_with_widening(tmp_path):
    """Build a KKT for the small model and widen ``n`` from ``t`` to ``tl``."""
    f = tmp_path / "widen.gms"
    f.write_text(_MODEL)
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        model = parse_model_file(str(f))
        normalize_model(model)
        j_eq, j_ineq = compute_constraint_jacobian(model)
        grad = compute_objective_gradient(model)
        kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
    finally:
        sys.setrecursionlimit(old)
    kkt.var_domain_widenings = {"n": ("tl",)}
    return kkt


class TestRewriteWidenedVarRefs:
    def test_parent_index_ref_rewritten_subset_ref_left_alone(self, tmp_path):
        kkt = _kkt_with_widening(tmp_path)
        code = "stat_m(tl).. (n(tl) * nu(tl))$(t(tl)) + n(t) =E= 0;"
        out, renamed = _rewrite_widened_var_refs(code, kkt)
        # parent-index n(tl) -> n__pw(tl)
        assert "n__pw(tl)" in out
        # subset-index n(t) untouched (would corrupt the embedded NLP)
        assert "n(t)" in out
        assert renamed == {"n"}

    def test_no_widening_is_a_noop(self, tmp_path):
        kkt = _kkt_with_widening(tmp_path)
        kkt.var_domain_widenings = {}
        code = "stat_m(tl).. n(tl) =E= 0;"
        out, renamed = _rewrite_widened_var_refs(code, kkt)
        assert out == code
        assert renamed == set()


class TestEmitWidenedVarCompanions:
    def test_emits_free_companion_couple_eq_and_fix(self, tmp_path):
        kkt = _kkt_with_widening(tmp_path)
        lines, pairs = _emit_widened_var_companions(kkt, add_comments=False, only_vars={"n"})
        blob = "\n".join(lines)
        assert "Free Variable n__pw(tl);" in blob
        assert "Equation couple_n(t);" in blob
        assert "couple_n(t).. n__pw(t) =e= n(t);" in blob
        # out-of-subset fix on the companion (not the source var)
        assert "n__pw.fx(tl)$(not ((t(tl)))) = 0;" in blob
        # the Model-statement pair
        assert pairs == [("couple_n", "n__pw")]

    def test_only_vars_filter(self, tmp_path):
        kkt = _kkt_with_widening(tmp_path)
        lines, pairs = _emit_widened_var_companions(kkt, add_comments=False, only_vars=set())
        assert lines == []
        assert pairs == []

    def test_special_char_name_is_quoted(self, tmp_path):
        """Issue #665: a widened variable whose name needs quoting (e.g. 'p-x')
        must emit quoted companion + coupling names AND quoted Model pairs."""
        from src.ir.symbols import VariableDef

        kkt = _kkt_with_widening(tmp_path)
        # Inject a special-char variable widened t -> tl.
        kkt.model_ir.variables["p-x"] = VariableDef(name="p-x", domain=("t",))
        kkt.var_domain_widenings = {"p-x": ("tl",)}
        lines, pairs = _emit_widened_var_companions(kkt, add_comments=False, only_vars={"p-x"})
        blob = "\n".join(lines)
        assert "Free Variable 'p-x__pw'(tl);" in blob
        assert "Equation 'couple_p-x'(t);" in blob
        assert "'couple_p-x'(t).. 'p-x__pw'(t) =e= 'p-x'(t);" in blob
        # the Model-statement pair is emitted pre-quoted (no double-quoting)
        assert pairs == [("'couple_p-x'", "'p-x__pw'")]

    def test_outofsubset_condition(self, tmp_path):
        kkt = _kkt_with_widening(tmp_path)
        cond = _widened_var_outofsubset_condition(kkt, ("t",), ("tl",))
        assert cond == "(t(tl))"

    def test_dynamic_subset_domain_remapped_in_declarations(self, tmp_path):
        """Issue #739: a dynamically-assigned source subset (forbidden as a GAMS
        declaration domain) is remapped to its parent set in the Free Variable /
        Equation DECLARATIONS, while the coupling-equation DEFINITION keeps the
        raw subset so it applies only on the subset."""
        from src.ir.model_ir import SetAssignment
        from src.ir.symbols import SetDef, VariableDef

        kkt = _kkt_with_widening(tmp_path)
        # `td` is a dynamic subset of `tl`: assigned at runtime, no static members.
        kkt.model_ir.sets["td"] = SetDef(name="td", members=(), domain=("tl",))
        kkt.model_ir.set_assignments.append(
            SetAssignment(set_name="td", indices=("tl",), expr=None, location=None)
        )
        kkt.model_ir.variables["q"] = VariableDef(name="q", domain=("td",))
        kkt.var_domain_widenings = {"q": ("tl",)}
        lines, _ = _emit_widened_var_companions(kkt, add_comments=False, only_vars={"q"})
        blob = "\n".join(lines)
        # declarations use the PARENT set (tl), not the dynamic subset (td)
        assert "Equation couple_q(tl);" in blob
        assert "Free Variable q__pw(tl);" in blob
        # the coupling DEFINITION still binds on the raw subset (td)
        assert "couple_q(td).. q__pw(td) =e= q(td);" in blob


class TestPresolveSuppressesWidenedDeclaration:
    def test_emit_variables_declares_source_domain_when_suppressed(self, tmp_path):
        kkt = _kkt_with_widening(tmp_path)
        widened = emit_variables(kkt, suppress_widenings=False)
        assert "n(tl)" in widened
        suppressed = emit_variables(kkt, suppress_widenings=True)
        # under suppression n is declared at its source (subset) domain
        assert "n(t)" in suppressed
        assert "n(tl)" not in suppressed

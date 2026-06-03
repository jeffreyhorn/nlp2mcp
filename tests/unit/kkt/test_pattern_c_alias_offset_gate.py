"""Regression test for Pattern C (Sprint 25 Day 6): KKT stationarity must
not emit phantom ±N IndexOffsets on a variable's multiplier when the source
equation body has no IndexOffset referencing that variable's domain.

Context — `DAY5_PATTERN_A_INVESTIGATION.md` §"Evidence — launch's
`stat_iweight` is malformed":

The `launch.gms` source contains (paraphrased):

    Set s / stage-1*stage-3 /;
    Alias (s, ss);
    Set ge(s, ss);  ge(s, ss) = yes$(ord(s) >= ord(ss));
    Variable iweight(s), pweight(s), weight(s);
    Equation dweight(s);
    dweight(s).. weight(s) =e= sum(ss$ge(ss,s), iweight(ss) + pweight(ss)) + ...;

`dweight` differentiates w.r.t. `iweight(s_row)` to yield non-zero Jacobian
entries for every `(s_eq, s_row)` pair where `ge(s_row, s_eq)` holds — i.e.,
cross-element entries that `_compute_index_offset_key` treats as lead/lag
groups (positional offset between eq instance and var instance). The
downstream emission then produces `nu_dweight(s+1)`, `(s-1)`, `(s+2)`, etc.,
even though the source body has NO `IndexOffset` on `s` or `ss`.

This is Pattern C Bug #1 (phantom offsets). The correct emission for a
body with no IndexOffset should have all alias-sum Jacobian entries
consolidated into a single zero-offset multiplier term — the `sum(ss, ...)`
alone captures the alias iteration.

Day 6 fix: gate the ±N offset-group enumeration on the equation body
actually containing at least one `IndexOffset` node on the variable's
domain set (or an alias of it). When there's no real `IndexOffset`, all
offset groups collapse to zero so only a single `nu_dweight(s)`
multiplier term is emitted.

Day-5 Bug #2 (the mis-scoped `$(ge(ss, s))` condition inside an outer
`sum(ss, ...)` with a multiplier that doesn't depend on `ss`) is a
separate defect tracked via a follow-up issue; this test deliberately
does NOT over-specify the residual `sum(ss, ...)` body.
"""

from __future__ import annotations

import sys

import pytest


@pytest.mark.unit
def test_alias_only_conditional_sum_emits_no_phantom_offsets(tmp_path):
    """A `sum(ss$ge(ss,s), iweight(ss))` body — no `IndexOffset` — must
    not yield `nu_dweight(s+N)` / `nu_dweight(s-N)` terms in the
    stationarity for `iweight`, AND the consolidated multiplier must be
    indexed by the source alias `ss` (not the equation domain `s`).

    Sprint 26 Day 1 Phase A landed the proper Pattern C fix per Sprint 25
    SPRINT_LOG.md Day 11 §"Open follow-ups (revised)" — the consolidated
    zero-offset Sum now iterates over the equation domain with the body's
    condition swapped (``alias ↔ eq_dom``), producing the GAMS-equivalent
    of the target ``sum(ss$ge(s,ss), -nu_dweight(ss))`` shape rather than
    the over-counting ``sum(ss, -1$ge(ss,s) * nu_dweight(s))`` form that
    #1351 rolled back the original #1306 gate to avoid.

    Mirrors the minimal shape of launch.gms's dweight equation. Uses a
    small set (card(s)=3) so any enumeration would produce ±1, ±2
    offsets and make phantom-offset emission obvious in the output.
    """
    gams = """\
Set s / stage-1*stage-3 /;
Alias (s, ss);
Set ge(s, ss) 's is greater-equal than ss';
ge(s, ss) = yes$(ord(s) >= ord(ss));

Parameter iwf(s) / stage-1 0.5, stage-2 0.6, stage-3 0.7 /;

Positive Variable
    iweight(s) 'inert weight'
    pweight(s) 'propellant weight'
    weight(s)  'total weight'
    aweight(s) 'airframe weight'
    z 'objective';

Equation
    diweight(s) 'definition of inert weight'
    dweight(s)  'definition of weight'
    zdef;

diweight(s).. iwf(s) * iweight(s) =e= aweight(s);
dweight(s).. weight(s) =e= sum(ss$ge(ss,s), iweight(ss) + pweight(ss));

zdef.. z =e= sum(s, iweight(s) + pweight(s) + aweight(s));

Model m / diweight, dweight, zdef /;
solve m using nlp minimizing z;
"""
    gams_file = tmp_path / "mini_launch.gms"
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
        output = emit_gams_mcp(kkt)
    finally:
        sys.setrecursionlimit(old_limit)

    stat_iweight_lines = [line for line in output.splitlines() if "stat_iweight" in line]
    assert stat_iweight_lines, (
        "Expected at least one line mentioning stat_iweight in emitted MCP; "
        f"none found. Output (first 1200 chars):\n{output[:1200]}"
    )
    stat_iweight_text = "\n".join(stat_iweight_lines)

    # Bug #1 invariant — the stationarity body must not reference any
    # offset-indexed `nu_dweight(s±N)` multiplier when the source has no
    # IndexOffset on s.
    forbidden = ("nu_dweight(s+", "nu_dweight(s-")
    for needle in forbidden:
        assert needle not in stat_iweight_text, (
            f"Found phantom Pattern C offset {needle!r} in stat_iweight body; "
            f"the source dweight(s) equation has no IndexOffset on s. "
            f"Full stat_iweight text:\n{stat_iweight_text}"
        )

    # Sprint 26 Day 1 Phase A: the consolidated multiplier must be indexed
    # by the source alias ``ss`` (not the equation domain ``s``). Without
    # this re-index, the consolidated form ``sum(ss, -1$ge(ss,s) *
    # nu_dweight(s))`` over-counts and PATH reports model_infeasible
    # (the #1351 failure mode).
    assert "nu_dweight(ss)" in stat_iweight_text, (
        "Expected alias-indexed nu_dweight(ss) multiplier after the Sprint 26 "
        "Day 1 Phase A Pattern C consolidation transform. "
        f"Full stat_iweight text:\n{stat_iweight_text}"
    )

    # Negative: the unswapped ``nu_dweight(s)`` form must NOT appear (it would
    # be the over-counting body shape that #1351 rolled back to). Note that
    # ``"nu_dweight(s)"`` (with the closing paren) is distinct from
    # ``"nu_dweight(ss)"`` as a substring — ``"nu_dweight(s)" in
    # "nu_dweight(ss)"`` is False.
    assert "nu_dweight(s)" not in stat_iweight_text, (
        "Found over-counting nu_dweight(s) (eq-domain-indexed) multiplier in "
        "stat_iweight body — the consolidated builder should produce "
        "alias-indexed nu_dweight(ss) per Sprint 26 Day 1 Phase A. "
        f"Full stat_iweight text:\n{stat_iweight_text}"
    )

    # Sanity: the body's condition must be swapped to ``ge(s,ss)`` (from the
    # source's ``ge(ss,s)``) — that's the GAMS-equivalent of the target
    # ``sum(ss$ge(s,ss), -nu_dweight(ss))`` form.
    assert "ge(s,ss)" in stat_iweight_text, (
        "Expected swapped condition ``ge(s,ss)`` in stat_iweight body — "
        "the Pattern C consolidated builder swaps alias ↔ eq-domain indices. "
        f"Full stat_iweight text:\n{stat_iweight_text}"
    )


@pytest.mark.unit
def test_cross_set_alias_sum_is_not_pattern_c_swapped(tmp_path):
    """Sprint 27 #1398 gate tightening: a `sum(c$sc(s,c), xcrop(c))` body where
    the summed set ``c`` and the eq-domain set ``s`` are DIFFERENT sets (a
    2-set membership, NOT a self-alias) must NOT trigger the Pattern C
    ``alias ↔ eq_dom`` swap.

    This is the qdemo7 failure mode: the Sprint 26 Phase A gate over-reached,
    firing on cross-set alias sums and applying a blanket swap that transposed
    BOTH the source condition's argument order AND the multiplier index. The
    correct (naive) stationarity for ``stat_xcrop(c)`` of
    ``plow(s).. sum(c$sc(s,c), xcrop(c)) =l= cap(s)`` is::

        sum(s, 1$(sc(s,c)) * lam_plow(s))      # source-order cond, alias-indexed mult

    The over-reaching swap produced the buggy::

        sum(s, 1$(sc(c,s)) * lam_plow(c))      # transposed cond AND eq-index leak

    which references ``lam_plow(c)`` out of the ``plow`` (domain ``s``) multiplier's
    declared domain → GAMS path_syntax_error. The tightening restricts the gate
    to same-canonical-set self-aliases (launch's ``s``/``ss``), so this cross-set
    case falls through to the correct naive emit. (#1398 regressed 15 such models.)
    """
    gams = """\
Set s / summer, winter /;
Set c / cotton, wheat /;
Set sc(s,c) / summer.cotton, winter.wheat /;
Parameter cap(s) / summer 10, winter 8 /;
Positive Variable xcrop(c), z;
Equation plow(s), zdef;
plow(s).. sum(c$sc(s,c), xcrop(c)) =l= cap(s);
zdef.. z =e= sum(c, xcrop(c));
Model m / plow, zdef /;
solve m using nlp maximizing z;
"""
    gams_file = tmp_path / "mini_qdemo7.gms"
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
        output = emit_gams_mcp(kkt)
    finally:
        sys.setrecursionlimit(old_limit)

    stat_xcrop_lines = [line for line in output.splitlines() if "stat_xcrop" in line]
    assert stat_xcrop_lines, (
        "Expected at least one line mentioning stat_xcrop in emitted MCP; none "
        f"found. Output (first 1200 chars):\n{output[:1200]}"
    )
    stat_xcrop_text = "\n".join(stat_xcrop_lines)

    # Correct (naive) shape: source-order condition + alias-indexed multiplier.
    assert "1$(sc(s,c))" in stat_xcrop_text, (
        "Expected source-order condition `sc(s,c)` in stat_xcrop body (the gate "
        "must NOT swap a cross-set alias sum). "
        f"Full stat_xcrop text:\n{stat_xcrop_text}"
    )
    assert "lam_plow(s)" in stat_xcrop_text, (
        "Expected alias/constraint-domain-indexed multiplier `lam_plow(s)`. "
        f"Full stat_xcrop text:\n{stat_xcrop_text}"
    )

    # The Phase A over-reach signatures must NOT appear.
    assert "1$(sc(c,s))" not in stat_xcrop_text, (
        "Found transposed condition `sc(c,s)` — the Pattern C swap wrongly fired "
        "on a cross-set (s≠c) alias sum (#1398 over-reach). "
        f"Full stat_xcrop text:\n{stat_xcrop_text}"
    )
    assert "lam_plow(c)" not in stat_xcrop_text, (
        "Found eq-index-leaked multiplier `lam_plow(c)` (out of plow's domain `s`) "
        "— the Pattern C swap wrongly fired on a cross-set alias sum (#1398). "
        f"Full stat_xcrop text:\n{stat_xcrop_text}"
    )


@pytest.mark.unit
def test_helpers_unit_contracts():
    """Unit-level contracts on the three Pattern C helpers, covering the
    edge cases flagged in PR #1308 Copilot review:

      1. `_body_has_index_offset_on_sets` must detect `IndexOffset` nodes
         even when the offset's base is bound by an enclosing `Sum`
         (e.g. `sum(ss, x(ss+1))` — `ss` aliases the variable's domain
         AND `ss+1` is a legitimate source-level lead).
      2. `_body_has_aliased_conditional_sum_over_sets` must NOT fire when
         the sum's condition only references the summed index itself
         (e.g. `sum(ss$(ord(ss) > 1), ...)`) — that condition doesn't
         link the sum to the equation domain.
      3. `_expr_mentions_indices_canonical` must recognize index mentions
         that appear as `IndexOffset.base` (e.g. `ge(ss+1, s)` — the
         `ss+1` is an `IndexOffset` whose base is the string `ss`).
    """
    from src.ir.ast import Binary, Call, Const, IndexOffset, Sum, SymbolRef, VarRef
    from src.ir.model_ir import ModelIR
    from src.ir.symbols import AliasDef, SetDef
    from src.kkt.stationarity import (
        _body_has_aliased_conditional_sum_over_sets,
        _body_has_index_offset_on_sets,
        _expr_mentions_indices_canonical,
    )

    ir = ModelIR()
    ir.sets["s"] = SetDef(name="s", members=["stage-1", "stage-2", "stage-3"])
    ir.aliases["ss"] = AliasDef(name="ss", target="s")

    target_sets = frozenset({"s"})

    # --- Case 1: sum-bound IndexOffset must count. ---
    # Mirrors `sum(ss, x(ss+1))`.
    body_bound_offset = Sum(
        index_sets=("ss",),
        body=VarRef("x", (IndexOffset(base="ss", offset=Const(1.0), circular=False),)),
    )
    assert _body_has_index_offset_on_sets(body_bound_offset, target_sets, ir) is True, (
        "Expected sum-bound IndexOffset on an aliased domain to be detected; "
        "without this, sum(ss, x(ss+1)) would be misclassified as offset-free "
        "and the Pattern C gate would wrongly collapse real lead/lag groups."
    )

    # --- Case 2: condition that only references the summed index must NOT
    # be treated as referencing the equation domain. ---
    # Mirrors `sum(ss$(ord(ss) > 1), ...)` within an eq over domain (s,).
    body_sum_only_condition = Sum(
        index_sets=("ss",),
        body=VarRef("x", ("ss",)),
        condition=Binary(">", Call("ord", (SymbolRef(name="ss"),)), Const(1.0)),
    )
    assert (
        _body_has_aliased_conditional_sum_over_sets(
            body_sum_only_condition,
            target_sets,
            ir,
            eq_domain_canonical=frozenset({"s"}),
        )
        is False
    ), (
        "Sum whose condition only references its own summed index must NOT "
        "trigger the Pattern C gate — the condition doesn't link the sum "
        "to the equation's domain instance."
    )

    # But if the condition references a free equation-domain index in
    # ADDITION to the summed index (the launch shape: `ge(ss, s)`), the
    # gate MUST fire.
    body_launch_shape = Sum(
        index_sets=("ss",),
        body=VarRef("iweight", ("ss",)),
        condition=Call("ge", (SymbolRef(name="ss"), SymbolRef(name="s"))),
    )
    assert (
        _body_has_aliased_conditional_sum_over_sets(
            body_launch_shape,
            target_sets,
            ir,
            eq_domain_canonical=frozenset({"s"}),
        )
        is True
    ), "Launch-shape `sum(ss$ge(ss,s), ...)` must be detected by the gate."

    # --- Case 3: IndexOffset.base must be recognized as an index mention. ---
    # Mirrors a condition like `ge(ss+1, s)` inside a sum over ss where we
    # want to detect that the condition also references `s` (equation domain)
    # via the IndexOffset's base.
    condition_with_offset = Call(
        "ge",
        (
            IndexOffset(base="ss", offset=Const(1.0), circular=False),
            SymbolRef(name="s"),
        ),
    )
    # With `ss` bound (as it would be inside `sum(ss, ...)`), the `ss+1`
    # mention is filtered out, but `s` remains free → condition is linked
    # to the eq domain.
    assert (
        _expr_mentions_indices_canonical(
            condition_with_offset,
            target_canonical_sets=frozenset({"s"}),
            model_ir=ir,
            bound_indices=frozenset({"ss"}),
        )
        is True
    ), "`ge(ss+1, s)` with ss bound must still report a link via the free `s`."

    # And with neither ss nor s bound, a condition like `ord(ss+1)` must
    # count as a mention via the IndexOffset base — otherwise nested
    # lead/lag fingerprints slip past the gate.
    condition_offset_only = Call(
        "ord", (IndexOffset(base="ss", offset=Const(1.0), circular=False),)
    )
    assert (
        _expr_mentions_indices_canonical(
            condition_offset_only,
            target_canonical_sets=frozenset({"s"}),
            model_ir=ir,
            bound_indices=frozenset(),
        )
        is True
    ), (
        "`ord(ss+1)` must count as a mention of the canonical set via "
        "IndexOffset.base; otherwise the gate's condition-link check has "
        "false negatives on nested lead/lag fingerprints."
    )

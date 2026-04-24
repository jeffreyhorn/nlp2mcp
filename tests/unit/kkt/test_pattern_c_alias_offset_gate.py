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
    stationarity for `iweight`. Only a single zero-offset multiplier
    (possibly wrapped in `sum(ss, ...)` — Bug #2 is out of scope here)
    should appear.

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

    # Sanity: the zero-offset multiplier must still be present. Without
    # it, the stationarity would be missing the dweight contribution
    # entirely.
    assert "nu_dweight(s)" in stat_iweight_text, (
        "Expected zero-offset nu_dweight(s) multiplier to remain after "
        "the Pattern C gate consolidates phantom-offset groups. "
        f"Full stat_iweight text:\n{stat_iweight_text}"
    )

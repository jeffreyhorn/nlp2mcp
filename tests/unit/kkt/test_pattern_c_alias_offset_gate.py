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
def test_plain_alias_pattern_c_consolidates_from_source_body(tmp_path):
    """Sprint 27 #1381 Phase B-1: a plain-alias (no-``$``-condition) Pattern C
    sum — ``ieq(i).. idv(i) =e= sum(j, imat(i,j)*dk(j));`` with ``Alias(i,j)`` —
    must consolidate to a single source-body-driven term, NOT a phantom
    per-offset enumeration.

    The launch-shape gate requires a ``$`` condition, so camcge's plain-alias
    sums otherwise fall through to ``nu_ieq(i±N)`` phantom-offset enumeration
    (→ path_syntax_error).  Phase B-1 builds the consolidated term directly from
    the source ``Sum`` body BEFORE element-to-set (which would collapse
    ``imat(i,j) → imat(i,i)`` and break the Phase A swap), giving the correct
    ``sum(j, -imat(j,i) * nu_ieq(j))`` — coefficient swapped at the SOURCE level
    (``imat(j,i)``, not the mis-swapped ``imat(j,j)``), multiplier alias-indexed.
    """
    gams = """\
Set i / s1, s2, s3 /;
Alias (i,j);
Parameter imat(i,j);
imat(i,j) = 1 + ord(i) + 2*ord(j);
Positive Variable dk(i), idv(i), z;
Equation ieq(i), zdef;
ieq(i).. idv(i) =e= sum(j, imat(i,j)*dk(j));
zdef.. z =e= sum(i, dk(i) + idv(i));
Model m / ieq, zdef /;
solve m using nlp minimizing z;
"""
    gams_file = tmp_path / "mini_camcge.gms"
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

    stat_dk_lines = [line for line in output.splitlines() if "stat_dk" in line]
    assert stat_dk_lines, f"Expected a stat_dk line in emitted MCP. Output:\n{output[:1200]}"
    text = "\n".join(stat_dk_lines)

    # Correct consolidated form: a single alias-Sum with the source-swapped
    # coefficient imat(j,i) and an alias-indexed multiplier nu_ieq(j).
    assert (
        "imat(j,i)" in text
    ), f"Expected source-swapped coefficient imat(j,i) in stat_dk. Full:\n{text}"
    assert (
        "nu_ieq(j)" in text
    ), f"Expected alias-indexed multiplier nu_ieq(j) in stat_dk. Full:\n{text}"

    # No phantom per-offset enumeration (the unconsolidated failure mode).
    import re

    assert not re.search(r"nu_ieq\(i[+-]\d+\)", text), (
        f"Found phantom-offset nu_ieq(i±N) — the plain-alias sum was not "
        f"consolidated. Full:\n{text}"
    )
    # No Phase A mis-swap (element-to-set collapsed imat(i,j)→imat(i,i) then
    # swapped to imat(j,j)).
    assert "imat(j,j)" not in text, (
        f"Found mis-swapped imat(j,j) — Phase B-1 must swap the SOURCE "
        f"coefficient, not the element-to-set-collapsed one. Full:\n{text}"
    )


def _emit_mini_mcp(tmp_path, gams: str, fname: str) -> str:
    """Translate a small GAMS model to MCP and return the emitted text."""
    gams_file = tmp_path / fname
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
        # Match the real pipeline: pass the normalized equations to the Jacobian
        # so inequality (=l=/=g=) multiplier signs are canonical (test helper
        # parity with tests/e2e/test_gamslib_match.py::_do_pipeline_and_solve).
        normalized_eqs, _ = normalize_model(model)
        grad = compute_objective_gradient(model)
        j_eq, j_ineq = compute_constraint_jacobian(model, normalized_eqs)
        kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
        return emit_gams_mcp(kkt)
    finally:
        sys.setrecursionlimit(old_limit)


@pytest.mark.unit
def test_b2_eq_domain_factor_outside_sum_consolidates(tmp_path):
    """Sprint 27 #1381 Phase B-2: an alias-Sum multiplied by an eq-domain factor
    OUTSIDE the sum — camcge's ``prodinv(i).. pk(i)*dk(i) =e= kio(i)*savings -
    kio(i)*sum(j, dst(j)*p(j));`` — must consolidate to
    ``dst(i) * sum(j, kio(j) * nu_prodinv(j))``: the var-side coefficient
    ``dst(i)`` (from the inner-sum coefficient, reindexed sum→stat) stays OUTSIDE
    the new Sum, while the eq-side factor ``kio(i) → kio(j)`` moves INSIDE,
    reindexed to the alias; the multiplier is alias-indexed.  Without B-2 the
    standard path emits a phantom ``kio(i±N)*dst(i)*nu_prodinv(i±N)`` enumeration.
    """
    gams = """\
Set i / s1, s2, s3 /;
Alias (i,j);
Parameter kio(i), dst0(i);
kio(i) = 1 + ord(i);
dst0(i) = 2 + ord(i);
Positive Variable pk(i), dk(i), p(i), dst(i), savings, z;
Equation prodinv(i), zdef;
prodinv(i).. pk(i)*dk(i) =e= kio(i)*savings - kio(i)*sum(j, dst(j)*p(j));
zdef.. z =e= sum(i, pk(i) + dk(i) + p(i) + dst(i)) + savings;
Model m / prodinv, zdef /;
solve m using nlp minimizing z;
"""
    output = _emit_mini_mcp(tmp_path, gams, "mini_prodinv.gms")
    stat_p_lines = [ln for ln in output.splitlines() if "stat_p(" in ln]
    assert stat_p_lines, f"Expected a stat_p line. Output:\n{output[:1200]}"
    text = "\n".join(stat_p_lines)

    # Consolidated B-2 form: var-side dst(i) outside, eq-side kio(j) inside the Sum.
    assert "dst(i) * sum(j, kio(j) * nu_prodinv(j))" in text, (
        f"Expected consolidated B-2 form dst(i) * sum(j, kio(j) * nu_prodinv(j)). " f"Full:\n{text}"
    )
    # No phantom per-offset enumeration of the consolidated multiplier.
    import re

    assert not re.search(r"nu_prodinv\(i[+-]\d+\)", text), (
        f"Found phantom-offset nu_prodinv(i±N) — the eq-domain-factor sum was not "
        f"consolidated (B-2 builder did not fire). Full:\n{text}"
    )


@pytest.mark.unit
def test_b3_dim_mismatch_consolidates_no_outer_sum(tmp_path):
    """Sprint 27 #1381 Phase B-3: a dim-mismatch reducing Sum — cesam2's
    ``COLSUM(jj).. sum(ii, TSAM(ii,jj)) =e= Y(jj);`` over a 2-D variable ``TSAM``
    with a 1-D constraint domain (``jj`` a strict subset of ``i``) — must
    consolidate to ``nu_COLSUM(j)$(jj(j))`` (multiplier indexed by the variable
    coordinate the eq-domain index binds, guarded by the subset membership, NO
    outer Sum).  Its companion ``ROWSUM`` binds the other coordinate →
    ``nu_ROWSUM(i)$(ii(i))``.  Without B-3 the standard element-to-set path
    mis-binds the eq-domain index and emits a spurious ``sameas`` block.
    """
    gams = """\
Set i / total, a1, a2 /;
Set ii(i); ii(i) = yes; ii("total") = no;
Alias (i,j), (ii,jj);
Variable tsam(i,j), y(i), z;
Equation colsum(jj), rowsum(ii), zdef;
colsum(jj).. sum(ii, tsam(ii,jj)) =e= y(jj);
rowsum(ii).. sum(jj, tsam(ii,jj)) =e= y(ii);
zdef.. z =e= sum((i,j), tsam(i,j)) + sum(i, y(i));
Model m / colsum, rowsum, zdef /;
solve m using nlp minimizing z;
"""
    output = _emit_mini_mcp(tmp_path, gams, "mini_cesam2.gms")
    stat_lines = [ln for ln in output.splitlines() if "stat_tsam(" in ln]
    assert stat_lines, f"Expected a stat_tsam line. Output:\n{output[:1200]}"
    text = "\n".join(stat_lines)

    # COLSUM binds TSAM position 1 → multiplier indexed by j (the SECOND
    # variable coordinate), NOT the mis-bound position-0 nu_colsum(i).  (The
    # subset-membership guard $(jj(j)) is added downstream from the multiplier's
    # declared domain; the real cesam2 integration verifies it end-to-end.)
    assert "nu_colsum(j)" in text, (
        f"Expected dim-mismatch B-3 multiplier nu_colsum(j) (binding position 1). " f"Full:\n{text}"
    )
    assert "nu_colsum(i)" not in text, (
        f"Found mis-bound nu_colsum(i) — B-3 must bind the eq-domain index to "
        f"variable position 1 (j), not position 0 (i). Full:\n{text}"
    )
    # ROWSUM binds TSAM position 0 → nu_rowsum(i).
    assert "nu_rowsum(i)" in text, (
        f"Expected companion B-3 multiplier nu_rowsum(i) (binding position 0). " f"Full:\n{text}"
    )
    # No spurious sameas block on the COLSUM term, and no phantom offsets.
    import re

    assert not re.search(
        r"nu_colsum\(i[+-]\d+\)", text
    ), f"Found phantom-offset nu_colsum(i±N) in stat_tsam. Full:\n{text}"
    assert "sameas" not in text, (
        f"Found spurious sameas block — B-3 builder should bind by position, "
        f"not by sameas enumeration. Full:\n{text}"
    )


@pytest.mark.unit
def test_dynamic_subset_constant_assignment_not_dropped(tmp_path):
    """Sprint 27 #1381: a constant assignment indexed over a DYNAMIC subset —
    cesam2's ``wbar1(ii,jwt1) = 1/7;`` where ``ii(i)`` is populated at runtime
    via ``ii(i) = yes;`` — must NOT be silently dropped at parse time.

    The Issue #622 set-expansion path enumerates set-indexed constant assignments
    into per-element values, but a dynamic subset has no STATIC members, so the
    enumeration previously skipped the whole assignment → the parameter stayed
    unassigned and the generated model raised ``$141 Symbol declared but no
    values``.  The fix stores it as an expression so it is emitted as a GAMS
    statement (the solver expands the runtime-populated subset itself).
    """
    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        from src.ir.parser import parse_model_file

        gams = """\
Set i / total, a1, a2 /;
Set ii(i); ii(i) = yes; ii("total") = no;
Set jwt / w1, w2 /;
Set jwt1(jwt) / w1, w2 /;
Parameter wbar1(i,jwt);
wbar1(ii,jwt1) = 1/7;
Scalar z;
"""
        gams_file = tmp_path / "mini_dynsubset.gms"
        gams_file.write_text(gams)
        model = parse_model_file(str(gams_file))
    finally:
        sys.setrecursionlimit(old_limit)

    wbar1 = model.params.get("wbar1")
    assert wbar1 is not None
    # The assignment must survive — as an expression (set indices preserved),
    # NOT dropped (which would leave both values and expressions empty).
    assert wbar1.expressions, (
        "Dynamic-subset constant assignment wbar1(ii,jwt1) = 1/7 was dropped — "
        "expected it stored as an expression so it emits as a GAMS statement."
    )
    keys = [tuple(k) for k, _ in wbar1.expressions]
    assert ("ii", "jwt1") in keys, (
        f"Expected the assignment stored with its original set indices " f"(ii, jwt1); got {keys}."
    )


@pytest.mark.unit
def test_b3_does_not_fire_on_inequality_or_distinct_set_dim_mismatch(tmp_path):
    """Sprint 27 #1381 Phase B-3 regression guard: the dim-mismatch builder must
    NOT intercept a constraint whose standard path is already correct —
    specifically (a) inequalities and (b) variables whose two coordinates are
    DISTINCT canonical sets — mirroring trnsport's
    ``demand(j).. sum(i, x(i,j)) =g= b(j);`` (``x(i,j)`` over genuinely different
    sets ``i``/``j``).  If B-3 fired here it would emit ``+lam_demand(j)`` instead
    of the correct ``-lam_demand(j)`` and make the model infeasible.
    """
    gams = """\
Set i / s1, s2 /;
Set j / m1, m2, m3 /;
Parameter c(i,j); c(i,j) = ord(i) + ord(j);
Positive Variable x(i,j), z;
Equation supply(i), demand(j), zdef;
supply(i).. sum(j, x(i,j)) =l= 10;
demand(j).. sum(i, x(i,j)) =g= 1;
zdef.. z =e= sum((i,j), c(i,j)*x(i,j));
Model m / supply, demand, zdef /;
solve m using lp minimizing z;
"""
    output = _emit_mini_mcp(tmp_path, gams, "mini_trnsport.gms")
    stat_lines = [ln for ln in output.splitlines() if "stat_x(" in ln]
    assert stat_lines, f"Expected a stat_x line. Output:\n{output[:1200]}"
    text = "\n".join(stat_lines)

    # demand is a >= inequality: KKT for a min problem gives -lam_demand(j).
    assert "- lam_demand(j)" in text, (
        f"Expected -lam_demand(j) (correct =g= sign); B-3 must not consolidate "
        f"an inequality dim-mismatch. Full:\n{text}"
    )
    assert "+ lam_demand(j)" not in text, (
        f"Found +lam_demand(j) — B-3 wrongly intercepted the inequality and "
        f"flipped the multiplier sign. Full:\n{text}"
    )
    # No outer Sum-wrapped nu_-style consolidation of the demand/supply multipliers.
    assert "nu_demand" not in text and "nu_supply" not in text, (
        f"Inequality multipliers must stay lam_*, not be consolidated as nu_*. " f"Full:\n{text}"
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


@pytest.mark.unit
def test_b3_multiplier_ref_validity_guard():
    """PR #1417 review: `_b3_multiplier_ref_is_valid` must only let B-3 fire when
    the emitted `nu_X(binding_symbol)` reference is a valid GAMS index against the
    multiplier's declared domain — otherwise B-3 would bypass the subset→parent
    rename/widening and emit a domain-erroring reference.

    Cases:
      - multiplier declared over the PARENT, reference the parent → valid (cesam2).
      - multiplier declared over the PARENT, reference a subset → valid (cesam).
      - multiplier declared over a DYNAMIC subset (no static members) → emit widens
        it to the parent, so a parent reference is valid (mini-cesam2).
      - multiplier declared over a STATIC subset (has members) → NOT widened, so a
        parent reference is a domain error → invalid (fall back to standard path).
    """
    from src.ir.model_ir import ModelIR
    from src.ir.symbols import AliasDef, SetDef
    from src.kkt.stationarity import _b3_multiplier_ref_is_valid

    ir = ModelIR()
    ir.sets["i"] = SetDef(name="i", members=["a", "b", "c"])
    # dynamic subset of i (no static members — populated at runtime)
    ir.sets["ii"] = SetDef(name="ii", members=[], domain=("i",))
    # static subset of i (has members)
    ir.sets["istat"] = SetDef(name="istat", members=["a", "b"], domain=("i",))
    ir.aliases["j"] = AliasDef(name="j", target="i")
    ir.aliases["jj"] = AliasDef(name="jj", target="ii")

    # parent-declared multiplier, parent reference (cesam2-style): valid
    assert _b3_multiplier_ref_is_valid("j", ("j",), ir) is True
    # parent-declared multiplier, subset reference (cesam-style jj ⊆ j): valid
    assert _b3_multiplier_ref_is_valid("jj", ("j",), ir) is True
    # dynamic-subset-declared multiplier, parent reference (emit widens jj→i): valid
    assert _b3_multiplier_ref_is_valid("j", ("jj",), ir) is True
    # STATIC-subset-declared multiplier, parent reference: INVALID → fall back
    assert _b3_multiplier_ref_is_valid("j", ("istat",), ir) is False
    # non-1-D declared domain → invalid (defensive)
    assert _b3_multiplier_ref_is_valid("j", ("i", "j"), ir) is False

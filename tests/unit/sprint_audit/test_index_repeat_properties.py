"""Sprint 39 P10 — the P1/P2 repeated-index gate.

P1 is a HARD gate (0 violations across 3,109 heads when it landed). P2 is a
RATCHET against a recorded baseline, because 9 real violations sit in committed
goldens today and a gate that goes red on untouched history gets switched off.

⚠ THE SCOPING IS LOAD-BEARING, AND TWO TESTS PIN IT.
P2 scans ``$(...)`` guard CONTENT only. Two classes are deliberately outside it,
each because including them measured as a false positive:

* a ``Set ut(i,i)`` DECLARATION — legitimate, present in elec both before and
  after its fix (Prep Task 7);
* a source-faithful diagonal ASSIGNMENT — the survey proposed closing this
  "known gap" as a one-line extension when P2 graduated. Measured first, that
  extension is **8/8 false positives**: china, prolog, markov, orani, dinam,
  egypt and danwolfe all emit a diagonal assignment that appears **verbatim in
  their source**. Against 9 true findings that is roughly 1:1, and a check at
  that rate gets deleted.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Load by spec and restore sys.path — a module-level insert leaks import order
# into the whole pytest run (see test_phase0_added_only_requirements.py).
_SPEC = importlib.util.spec_from_file_location(
    "check_index_repeat_properties",
    PROJECT_ROOT / "scripts" / "sprint_audit" / "check_index_repeat_properties.py",
)
assert _SPEC and _SPEC.loader
_mod = importlib.util.module_from_spec(_SPEC)
# ⚠ Restore BOTH sys.path and sys.modules. The module must be in sys.modules
# while exec_module runs (dataclasses/typing resolution needs it), but leaving
# it there leaks import state into the rest of the pytest run and can make
# behaviour order-dependent under xdist (PR #1736 review).
_prev_mod = sys.modules.get("check_index_repeat_properties")
sys.modules["check_index_repeat_properties"] = _mod
_saved = list(sys.path)
try:
    _SPEC.loader.exec_module(_mod)
finally:
    sys.path[:] = _saved
    if _prev_mod is None:
        sys.modules.pop("check_index_repeat_properties", None)
    else:
        sys.modules["check_index_repeat_properties"] = _prev_mod

p1_violations = _mod.p1_violations
p2_violations = _mod.p2_violations
scan = _mod.scan


@pytest.mark.unit
def test_p1_flags_a_repeated_controlling_index_in_a_head():
    """P1 fail-before."""
    assert p1_violations("stat_x(i,i).. foo =E= 0;") == ["stat_x(i,i)"]
    assert p1_violations("stat_x(i,j).. foo =E= 0;") == []


@pytest.mark.unit
def test_p1_is_case_insensitive_like_gams():
    assert p1_violations("stat_x(I,i).. foo =E= 0;") == ["stat_x(I,i)"]


@pytest.mark.unit
def test_p1_scans_a_head_whose_GUARD_CONTAINS_A_DECIMAL():
    """⚠ SCOPE guard — the head regex must stop at the ``..`` operator.

    An earlier form matched the guard with ``[^.]*``, which stops at the first
    ``.``. Any head whose ``$`` guard contains a decimal literal was therefore
    never matched and never scanned: measured **9 heads** across egypt, ganges,
    gangesx, gtm, imsl, korcge (x2), tricp and turkey (x2). The reported head
    count was 3,100 when the true figure is **3,109**.

    P1's verdict happened to be unaffected -- none of the nine repeats an index
    -- but that is luck of the data. A HARD gate silently scanning 99.7 % of its
    input can pass on a violation it never looked at, which is the false
    negative a gate exists to prevent (PR #1736 review).
    """
    # Real shapes, from gtm and tricp respectively.
    assert p1_violations("comp_up_s(i)$(0.99 * supc(i) < inf).. foo =E= 0;") == []
    assert p1_violations("comp_lo_r(n)$(myScale * 0.001 > -inf).. foo =E= 0;") == []
    # …and the violation must still be caught THROUGH such a guard.
    assert p1_violations("comp_up_s(i,i)$(0.99 * supc(i) < inf).. foo =E= 0;") == ["comp_up_s(i,i)"]


@pytest.mark.unit
def test_p2_flags_a_repeated_index_inside_a_guard():
    """P2 fail-before — elec's shape."""
    assert p2_violations("eq(i).. 1$(ut(i,i)) =E= 0;") == ["ut(i,i)"]
    assert p2_violations("eq(i).. 1$(ut(i,j)) =E= 0;") == []


@pytest.mark.unit
def test_p2_catches_non_adjacent_and_higher_arity_repeats():
    """nonsharp's `inter(col,col,stm)` — missed by an earlier binary matcher."""
    assert p2_violations("eq(c).. 1$(inter(col,col,stm)) =E= 0;") == ["inter(col,col,stm)"]
    assert p2_violations("eq(c).. 1$(p(x,y,x)) =E= 0;") == ["p(x,y,x)"]


@pytest.mark.unit
def test_p2_does_NOT_flag_a_set_declaration():
    """⚠ SCOPING GUARD 1 — the declaration class.

    `Set ut(i,i)` is the model's own legitimate declaration and appears in elec
    both before and after its fix. A whole-file matcher flags it, which would
    make the check useless.
    """
    assert p2_violations("Set ut(i,i) 'diagonal';") == []


@pytest.mark.unit
def test_p2_does_NOT_flag_a_source_faithful_diagonal_assignment():
    """⚠ SCOPING GUARD 2 — the assignment-LHS class, and the reason the survey's
    proposed "one-line extension" was NOT applied.

    Each line below is emitted verbatim from its model's source. Extending P2 to
    the assignment LHS flags all of them: measured 8/8 false positives across
    china, prolog, markov, orani, dinam, egypt and danwolfe.
    """
    # ⚠ ALL EIGHT measured cases. An earlier revision listed six while the
    # docstring claimed 8/8 (PR #1736 review) -- the same defect class as a
    # table that omits a row its own arithmetic needs. The count is now DERIVED
    # from this tuple rather than asserted in prose.
    cases = (
        ("china", "crec(cf,cf)$((not sum(ca, crec(ca,cf)))) = 1;"),  # source :305
        ("prolog", "eta(g,g,h) = gamma(g, h) * (1 - beta(g,h)) / x0(g,h) - 1;"),  # :88
        ("markov", "pi(s,i,sp,j,sp) = pr(i,j);"),  # :56
        ("orani-ce", "ce(c,c) = 1;"),  # :30
        ("orani-etabar", "etabar(c,s,c,s) = -1. + alphae(c,s);"),  # :86
        ("dinam", "a(id,id,te)$t(te) = a(id,id,te) - 1;"),  # :271
        ("egypt", "yld(c,c,r) = yield(c,r);"),  # :707
        ("danwolfe", "e(i,i) = 0;"),  # deliberate diagonal
    )
    assert (
        len(cases) == 8
    ), f"the docstring claims 8/8 false positives; {len(cases)} cases are listed"
    for model, line in cases:
        assert (
            p2_violations(line) == []
        ), f"source-faithful diagonal wrongly flagged ({model}): {line}"


@pytest.mark.unit
def test_p2_still_flags_a_repeat_that_reaches_the_GUARD_of_an_assignment():
    """gussrisk's shape — the repeat is in the guard, not only the LHS.

    This is what keeps the scoping honest: narrowing to guard content does not
    blind P2 to assignments, only to their left-hand sides.
    """
    assert p2_violations("covar(stocks,stocks)$(NOT covar(stocks,stocks)) = 0;") == [
        "covar(stocks,stocks)"
    ]


@pytest.mark.unit
def test_the_committed_corpus_matches_the_committed_baseline():
    """The measured claim behind the ratchet, asserted rather than recalled."""
    mcp = PROJECT_ROOT / "data" / "gamslib" / "mcp"
    if not mcp.is_dir():
        pytest.skip("goldens absent")
    p1, p2, n_goldens, n_heads = scan(mcp)
    assert p1 == {}, f"P1 is a HARD gate and must stay at zero; found: {p1}"
    baseline_path = PROJECT_ROOT / "scripts" / "sprint_audit" / "index_repeat_p2_baseline.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    assert p2 == baseline, (
        "P2 drifted from its baseline. A NEW violation is a defect to fix; a "
        "REMOVED one means the baseline must shrink (`--update-baseline`)."
    )

"""Sprint 39 P5 (Day 12) — pins for the survey's `NEEDS A TEST` / `ALREADY GUARDED` sites.

`POSITIONAL_DOMAIN_SURVEY.md` catalogues 21 symbol→position sites. Four
`NEEDS A GUARD` ones were closed on Days 9 and 11 (#1737, #1741). This module
pins the rest: the property each remaining site *relies on*, so that a future
change which removes that property fails here rather than in a golden.

⚠ **THE SURVEY CITES SITES BY LINE NUMBER AND THOSE NUMBERS ROT.** Measured at
Day 12: all six `stationarity.py` citations had drifted **+318 to +346**, and
`condition_eval.py` by +1. The same drift was recorded on Day 8 (+293) and hit
again on Day 11. `test_every_catalogued_site_still_resolves_by_symbol` is the
structural fix — it pins the OWNING FUNCTION of each site, which survives edits
that move lines.

⚠ **DO NOT RE-GUARD THE `ALREADY GUARDED` SITES.** Three independent remedies
already exist (consume-once slot claiming, `seen_sym` duplicate bail-out, parser
alias substitution) plus `_sigma_sp_domain_collision`'s own `>= 2` conjunct.
These tests assert those remedies *fire*; they do not add new ones.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]

#: site → the function that owns it, relocated by content on Day 12.
#: ⚠ Keyed by SYMBOL, never by line, for the reason in the module docstring.
CATALOGUED_SITES: tuple[tuple[str, str, str], ...] = (
    # NEEDS A TEST
    ("src/ad/constraint_jacobian.py", "_substitute_indices", "symbolic_indices.index(...) ×4"),
    ("src/ir/parser.py", "_handle_assign", "alias expansion / first position"),
    ("src/ir/parser.py", "_handle_aggregation", "seen_domain + minted alias"),
    ("src/ir/condition_eval.py", "_try_dotted_key_lookup", "first position of '*'"),
    ("src/kkt/stationarity.py", "_apply_alias_offset_to_deriv", "declared_domain[pi] vs PARAM"),
    # ALREADY GUARDED
    ("src/kkt/stationarity.py", "_match_subset_domain", "used_var_positions consume-once"),
    ("src/kkt/stationarity.py", "_compute_index_offset_key", "used_var consume-once"),
    ("src/kkt/stationarity.py", "_remap_condition_to_domain", "set_declared_domain[pos]"),
    ("src/kkt/stationarity.py", "_sigma_sp_domain_collision", "canon_hits >= 2 conjunct"),
    ("src/ad/derivative_rules.py", "_diff_sum", "enumerate + seen_sym bail-out"),
)


@pytest.mark.unit
def test_every_catalogued_site_still_resolves_by_symbol():
    """⚠ The structural fix for the survey's rotting line numbers.

    Day 8 measured +293 lines of drift on `stationarity.py`; Day 11 hit it again
    while relocating the same site; Day 12 measured +318 to +346 across all six
    of that file's citations. Three recurrences of "the address moved" is the
    argument for pinning the SYMBOL, which is stable across the edits that move
    lines.

    If this fails, a site was renamed or removed — update `CATALOGUED_SITES` and
    the survey together, in the same commit.
    """
    missing = []
    for rel, func, shape in CATALOGUED_SITES:
        path = PROJECT_ROOT / rel
        assert path.is_file(), f"{rel} no longer exists"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        names = {
            n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        if func not in names:
            missing.append(f"{rel}::{func}  ({shape})")
    assert not missing, "catalogued site(s) no longer resolve by symbol:\n  " + "\n  ".join(missing)


@pytest.mark.unit
class TestSubstituteIndicesCollapse:
    """`_substitute_indices` — FOUR catalogued sites, the highest-reach shape (12/15).

    All four use `symbolic_indices.index(...)`, which returns the FIRST matching
    position. With a repeated symbolic domain every lookup resolves to position
    0 and the later positions become unreachable.
    """

    def test_the_collapse_is_real_and_the_distinct_case_is_not(self):
        """Fail-before at the defect, plus the positive control beside it."""
        from src.ad.constraint_jacobian import _substitute_indices
        from src.ir.ast import VarRef

        # ⚠ REPEATED: both coordinates collapse onto the FIRST concrete value.
        out = _substitute_indices(VarRef("x", ("i",)), ("i", "i"), ("a1", "a2"))
        assert out.indices == ("a1",), (
            "a repeated symbolic domain resolves every `i` to position 0; "
            f"'a2' is unreachable. Got {out.indices}"
        )

        # The positive control — distinct symbols substitute positionally.
        out = _substitute_indices(VarRef("x", ("i", "j")), ("i", "j"), ("a1", "b2"))
        assert out.indices == ("a1", "b2")

    def test_the_IndexOffset_base_collapses_the_same_way(self):
        """The `idx.base` site (#1045's lead/lag substitution) shares the defect."""
        from src.ad.constraint_jacobian import _substitute_indices
        from src.ir.ast import Const, IndexOffset, VarRef

        ref = VarRef("k", (IndexOffset("t", Const(1), False),))
        out = _substitute_indices(ref, ("t", "t"), ("1990", "1991"))
        assert out.indices[0].base == "1990", "the offset base collapses to position 0 too"

        # Positive control: a distinct domain substitutes the intended base.
        out = _substitute_indices(ref, ("s", "t"), ("x", "1991"))
        assert out.indices[0].base == "1991"


@pytest.mark.unit
def test_the_AD_collapse_is_reachable_but_EMIT_refuses_it(tmp_path, monkeypatch):
    """⚠ THE SAFETY PROPERTY THESE FOUR SITES ACTUALLY RELY ON — measured.

    The survey calls them "safe only because of a pass covering one of three
    sub-shapes". Measured, the truth is sharper and worth pinning exactly:

    * the AD layer **does** reach `_substitute_indices` with a repeated
      `symbolic_indices` — 12 calls for the model below, carrying `('i','i')`
      against concrete tuples including `('a1','a2')`, so the collapse is REAL
      and the off-diagonal instances get a wrong Jacobian;
    * **nothing wrong reaches output**, because `emit_gams_mcp` runs
      `detect_empty_equation_instances`, whose `#1737` guard REFUSES the
      repeated equation domain.

    So `#1737` is load-bearing for the AD layer too, not only for the two call
    sites it was written against. If it is ever narrowed, these four sites stop
    being protected — which is exactly what this test would catch.

    ⚠ NON-VACUITY: the spy count is asserted > 0 before the refusal is believed,
    because a counter that reads 0 because it was never wired is
    indistinguishable from a site that is genuinely never reached.
    """
    import src.ad.constraint_jacobian as cj
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.index_map import RepeatedDomainSymbolError
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_file
    from src.kkt.assemble import assemble_kkt_system

    repeated: list[tuple] = []
    real = cj._substitute_indices

    def _spy(expr, symbolic_indices, concrete_indices):
        sym = [s.lower() for s in symbolic_indices if isinstance(s, str)]
        if len(sym) != len(set(sym)):
            repeated.append((tuple(symbolic_indices), tuple(concrete_indices)))
        return real(expr, symbolic_indices, concrete_indices)

    monkeypatch.setattr(cj, "_substitute_indices", _spy)

    gams = """\
Set i / a1, a2 /;
Alias (i,j);
Variable x(i), z;
Equation rep(i,i), zdef;
rep(i,i).. x(i) =e= 1;
zdef.. z =e= sum(i, x(i));
Model m / rep, zdef /;
solve m using nlp minimizing z;
"""
    gfile = tmp_path / "mini_repeated_eq_domain.gms"
    gfile.write_text(gams)
    model = parse_model_file(str(gfile))
    normalized, _ = normalize_model(model)
    kkt = assemble_kkt_system(
        model,
        compute_objective_gradient(model),
        *compute_constraint_jacobian(model, normalized),
    )

    assert repeated, (
        "the AD layer was expected to REACH _substitute_indices with a repeated "
        "symbolic domain; 0 such calls means this test proves nothing"
    )
    # …and at least one carries genuinely distinct concrete values, which is
    # where information is actually lost.
    assert any(len(set(c)) > 1 for _s, c in repeated), (
        "every repeated call had identical concrete values, so nothing was lost; "
        f"got {sorted(set(repeated))}"
    )

    # The refusal: emit will not produce a model built on that collapse.
    with pytest.raises(RepeatedDomainSymbolError, match="repeats"):
        emit_gams_mcp(kkt)


@pytest.mark.unit
def test_sigma_sp_collision_requires_TWO_canonical_hits():
    """`_sigma_sp_domain_collision` — ALREADY GUARDED, and this pins the guard.

    ⚠ **`len(canon_hits) < 2` is a FAST PATH, not the guard** — measured, after
    a mutant weakening it to `< 1` survived. It is subsumed by
    `any(vi < later for vi in canon_hits)`: with a single hit that hit *is*
    `later`, so the ordering test is already False and the function returns None
    either way. The load-bearing condition is the ORDERING one — the exact
    declared-name match must be the LATER position, with a canon-only hit
    earlier — and that is what the case below pins.

    ⚠ Do NOT add another guard here — assert the existing one fires.
    """
    from src.kkt.stationarity import _sigma_sp_domain_collision

    def canon(name: str) -> str:
        return {"sp": "s", "spp": "s", "s": "s"}.get(name.lower(), name.lower())

    # markov's shape: `sp` matches var position 2 by name and 0 by canon → (0, 2).
    assert _sigma_sp_domain_collision(("sp", "j"), ("s", "i", "sp"), canon) == (0, 2)

    # ⚠⚠ THE DISCRIMINATING CASE, and it took two dead mutants to find.
    # The exact NAME match must be the LATER position, with a canon-only hit
    # EARLIER. Here the exact match is at position 0 and the canon-only hit is
    # at 2 — the wrong way round — so the function must decline.
    #
    # An earlier revision of this test asserted only the two obvious negatives
    # below, and BOTH mutants survived: weakening `len(canon_hits) < 2` to `< 1`,
    # and replacing `any(vi < later ...)` with `True`. Neither changed any
    # assertion, because with a single hit the ordering test is already False.
    assert _sigma_sp_domain_collision(("sp",), ("sp", "i", "s"), canon) is None, (
        "the exact name match is EARLIER than the canon-only hit; conjunct 1 "
        "must decline rather than return the earlier position"
    )

    # Only ONE canonical hit → declines.
    assert _sigma_sp_domain_collision(("sp", "j"), ("sp", "i", "k"), canon) is None

    # No hit at all → declines.
    assert _sigma_sp_domain_collision(("q",), ("s", "i", "sp"), canon) is None

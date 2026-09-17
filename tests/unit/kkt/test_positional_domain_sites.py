"""Sprint 39 P5 (Day 12) — pins for the survey's `NEEDS A TEST` / `ALREADY GUARDED` sites.

`POSITIONAL_DOMAIN_SURVEY.md` catalogues **21** symbol→position sites:

    21  =  4 `NEEDS A GUARD`   (closed Days 9 and 11 — #1737, #1741)
         + 1 `NOT REACHABLE (in sample)`  (`emit_gams.py:795`, deliberately out)
         + 7 `NEEDS A TEST`  +  9 `ALREADY GUARDED`   <-- the 16 THIS MODULE COVERS

(PR #1743 review: an earlier docstring said "the rest", which read as 17 and
silently absorbed the `NOT REACHABLE` site.)

⚠⚠ **WHAT THIS MODULE ACTUALLY ASSERTS — two different strengths, and the
difference matters** (PR #1743 review).

* **BEHAVIOURAL (5)** — the collapse or the remedy is executed and its result
  asserted: all four `_substitute_indices` shapes, and
  `_sigma_sp_domain_collision`'s ordering conjunct.
* **STRUCTURAL ONLY (11)** — the site's anchor text is asserted to exist inside
  its owning function, nothing is executed: `_handle_aggregation`'s
  `expanded_indices.index(...)`, `_try_dotted_key_lookup`,
  `_apply_alias_offset_to_deriv`, `_match_subset_domain`, both
  `_compute_index_offset_key` passes, `_remap_condition_to_domain`, `_diff_sum`'s
  two sites, `_handle_assign`, and `_handle_aggregation`'s `seen_domain` path.
  **A guard at these sites could keep its anchor text while its state update or
  early return is broken, and this module would not notice.**

⚠ **THIS TABLE WAS WRONG TWICE, so it is now DERIVED AND TESTED** (PR #1743
review). An earlier revision listed **7** structural sites and omitted **four** —
`_remap_condition_to_domain`, the `NEEDS A TEST` `_handle_aggregation` row,
`_try_dotted_key_lookup` and `_apply_alias_offset_to_deriv` — so two catalogued
sites fell outside **both** categories and the reader could not tell. The review
named two of the four; the other two surfaced only by computing the complement.
`test_every_site_has_exactly_one_strength_class` now asserts the partition is
**exhaustive and disjoint** at **5 / 11**, so a hand-written list can no longer
drift from the catalog.

⚠ **Why those are structural, measured rather than assumed.** A probe of **nine**
input shapes against `_match_subset_domain` and `_compute_index_offset_key` —
subset/alias/canon-collision combinations — with the consume-once guards
DISABLED produced **byte-identical results in every case**. A behavioural pin
built on any of them would have asserted nothing while looking rigorous, which
is the precise failure this PR hit three times already. Narrowing the claim is
the honest outcome; a discriminating input for those two sites is open work.

⚠ **THE SURVEY CITES SITES BY LINE NUMBER AND THOSE NUMBERS ROT.** Measured at
Day 12: all six `stationarity.py` citations had drifted **+318 to +346**, and
`condition_eval.py` by +1. The same drift was recorded on Day 8 (+293) and hit
again on Day 11. `test_every_catalogued_site_still_resolves_by_symbol_AND_snippet` is the
structural fix — it pins the OWNING FUNCTION of each site, which survives edits
that move lines.

⚠ **DO NOT RE-GUARD THE `ALREADY GUARDED` SITES.** Three independent remedies
already exist (consume-once slot claiming, `seen_sym` duplicate bail-out, parser
alias substitution) plus `_sigma_sp_domain_collision`'s own `>= 2` conjunct.
⚠ **AND THIS MODULE DOES NOT ASSERT MOST OF THEM FIRING** (PR #1743 review — an
earlier revision said *"these tests assert those remedies fire"*, which the
strength table above already contradicted two paragraphs earlier). Only
`_sigma_sp_domain_collision` is pinned **behaviourally**; the other **eight**
guarded rows are **structural only** (9 `ALREADY GUARDED` − 1 behavioural = 8;
an earlier revision said seven — PR #1743 review). The instruction not to re-guard them
stands on the survey's measurement, not on coverage in this file.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]

#: One row per catalogued site: (file, owning function, ANCHOR SNIPPET, verdict).
#:
#: ⚠ Keyed by SYMBOL, never by line — see the module docstring.
#:
#: ⚠⚠ AND BY AN ANCHOR SNIPPET, because a function name is not fine-grained
#: enough (PR #1743 review). `_handle_aggregation` owns TWO catalogued sites with
#: DIFFERENT verdicts — `parser.py:6086`'s `expanded_indices.index(...)` is
#: `NEEDS A TEST`, while `parser.py:6007`'s `seen_domain` path is
#: `ALREADY GUARDED`. Recording only the function name cannot tell them apart, so
#: a regression in the intended path would pass. The snippet pins which nested
#: site each row means.
CATALOGUED_SITES: tuple[tuple[str, str, str, str], ...] = (
    # ---------------------------------------------------------- NEEDS A TEST
    (
        "src/ad/constraint_jacobian.py",
        "_substitute_indices",
        # ⚠ `return ...` PREFIX IS LOAD-BEARING (PR #1743 review). The bare
        # expression `concrete_indices[symbolic_indices.index(idx)]` appears
        # TWICE — here in `_sub_idx` and again inside the `:1513` comprehension —
        # and the resolver searches the whole function, so without the prefix
        # this row was satisfied by the comprehension alone and `:1466` was not
        # independently pinned.
        "return concrete_indices[symbolic_indices.index(idx)]",
        "NEEDS A TEST",
    ),
    (
        "src/ad/constraint_jacobian.py",
        "_substitute_indices",
        "concrete_indices[symbolic_indices.index(idx.base)]",
        "NEEDS A TEST",
    ),
    (
        "src/ad/constraint_jacobian.py",
        "_substitute_indices",
        "concrete_indices[symbolic_indices.index(expr.name)]",
        "NEEDS A TEST",
    ),
    (
        # ⚠ DISTINCT from the `_sub_idx` row above, which shares the literal
        # text `concrete_indices[symbolic_indices.index(idx)]` (PR #1743 review).
        # This is the Sum/Prod FREE-INDEX comprehension — survey `:1513`, reach
        # 11/15 — and a shared anchor collapsed it into the `:1466` row, so a
        # change here could not be detected.
        "src/ad/constraint_jacobian.py",
        "_substitute_indices",
        # ⚠ `free_concrete = tuple(` and NOT `if idx not in expr.index_sets` —
        # the latter also appears on the `free_symbolic` line directly above, so
        # it did not pin THIS site and its mutant survived (PR #1743 review).
        "free_concrete = tuple(",
        "NEEDS A TEST",
    ),
    (
        "src/ir/parser.py",
        "_handle_aggregation",
        "expanded_indices.index(child_idxs[0])",
        "NEEDS A TEST",
    ),
    (
        "src/ir/condition_eval.py",
        "_try_dotted_key_lookup",
        'list(domain).index("*")',
        "NEEDS A TEST",
    ),
    (
        "src/kkt/stationarity.py",
        "_apply_alias_offset_to_deriv",
        "declared_domain[pi]",
        "NEEDS A TEST",
    ),
    # ------------------------------------------------------- ALREADY GUARDED
    # ⚠ DO NOT add guards for these — the survey measured the remedies as
    # already complete. ⚠ Most rows below are STRUCTURAL-ONLY pins (anchor text,
    # nothing executed); only `_sigma_sp_domain_collision` is asserted
    # behaviourally. See the strength table in the module docstring.
    (
        "src/kkt/stationarity.py",
        "_match_subset_domain",
        # ⚠ The GUARD line, not the bare name: `used_var_positions` appears
        # THREE times in `_match_subset_domain` (declaration, test, add), so the
        # bare name pinned nothing. Found by sweeping after the review flagged
        # the two other non-unique anchors.
        "if k in used_var_positions:",
        "ALREADY GUARDED",
    ),
    (
        # ⚠ TWO consume-once sites in one function — survey `:5140` and `:5148`.
        # Both write the literal `used_var.add(vi)`, so a shared anchor collapsed
        # them (PR #1743 review). They are the FIRST pass (exact canonical match)
        # and the SECOND pass (common root), and each is anchored on its own
        # guard condition.
        "src/kkt/stationarity.py",
        "_compute_index_offset_key",
        "if vi not in used_var and eq_canons[ei] == var_canons[vi]:",
        "ALREADY GUARDED",
    ),
    (
        "src/kkt/stationarity.py",
        "_compute_index_offset_key",
        "if vi not in used_var and eq_roots[ei] == var_roots[vi]:",
        "ALREADY GUARDED",
    ),
    (
        "src/kkt/stationarity.py",
        "_remap_condition_to_domain",
        "set_declared_domain[pos]",
        "ALREADY GUARDED",
    ),
    (
        "src/kkt/stationarity.py",
        "_sigma_sp_domain_collision",
        "any(vi < later for vi in canon_hits)",
        "ALREADY GUARDED",
    ),
    (
        "src/ad/derivative_rules.py",
        "_diff_sum",
        "enumerate(wrt_indices)",
        "ALREADY GUARDED",
    ),
    (
        # ⚠ The SECOND `_diff_sum` site — survey `:2411`, the explicit duplicate
        # bail-out. Collapsed into the `enumerate(wrt_indices)` row until
        # PR #1743 review; it is a different remedy at a different line.
        "src/ad/derivative_rules.py",
        "_diff_sum",
        "if sym_j in seen_sym:",
        "ALREADY GUARDED",
    ),
    (
        "src/ir/parser.py",
        "_handle_assign",
        # ⚠ NOT the loop header `for pos, idx in enumerate(indices):` — that
        # appears TWICE in `_handle_assign` (`:5530` and `:5598`), so removing
        # the alias-expansion loop would leave the pin passing on the later one
        # (PR #1743 review).
        "domain_name = param.domain[pos]",
        "ALREADY GUARDED",
    ),
    (
        "src/ir/parser.py",
        "_handle_aggregation",
        "for pos, dname in enumerate(domain_indices):",
        "ALREADY GUARDED",
    ),
)


@pytest.mark.unit
def test_every_catalogued_site_still_resolves_by_symbol_AND_snippet():
    """⚠ The structural fix for the survey's rotting line numbers.

    Day 8 measured +293 lines of drift on `stationarity.py`; Day 11 hit it again;
    Day 12 measured +318 to +346 across all six of that file's citations. Three
    recurrences is the argument for pinning the SYMBOL, which survives the edits
    that move lines.

    ⚠ **The symbol alone is not enough** (PR #1743 review). `_handle_aggregation`
    owns TWO catalogued sites with DIFFERENT verdicts — `:6086` is
    `NEEDS A TEST`, `:6007` is `ALREADY GUARDED` — so a function-name-only pin
    cannot tell a regression in one from the other. Each row therefore carries an
    ANCHOR SNIPPET that must appear **inside that function's own source range**,
    not merely somewhere in the file.

    If this fails, a site was renamed, removed, or rewritten — update
    `CATALOGUED_SITES` and the survey together, in the same commit.
    """
    problems = []
    for rel, func, snippet, verdict in CATALOGUED_SITES:
        path = PROJECT_ROOT / rel
        assert path.is_file(), f"{rel} no longer exists"
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        owners = [
            n
            for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == func
        ]
        if not owners:
            problems.append(f"{rel}::{func} — function gone ({verdict})")
            continue
        # ⚠ Scope the search to the FUNCTION's lines, so a snippet that merely
        # exists elsewhere in the file cannot satisfy the pin.
        lines = source.splitlines()
        body = "\n".join(
            "\n".join(lines[o.lineno - 1 : (o.end_lineno or o.lineno)]) for o in owners
        )
        if snippet not in body:
            problems.append(f"{rel}::{func} — anchor absent: {snippet!r} ({verdict})")
    assert not problems, "catalogued site(s) no longer resolve:\n  " + "\n  ".join(problems)


#: The sites this module pins BEHAVIOURALLY — executed, result asserted.
#: Everything else in `CATALOGUED_SITES` is STRUCTURAL ONLY (anchor text).
#: ⚠ Keep this as DATA, not prose: the hand-written table in the docstring was
#: wrong twice (PR #1743 review), and the test below derives the complement so
#: the two cannot disagree.
BEHAVIOURALLY_PINNED: frozenset[tuple[str, str]] = frozenset(
    {
        ("src/ad/constraint_jacobian.py", "_substitute_indices"),
        ("src/kkt/stationarity.py", "_sigma_sp_domain_collision"),
    }
)


@pytest.mark.unit
def test_every_anchor_occurs_EXACTLY_ONCE_in_its_function():
    """⚠ An anchor that matches twice pins nothing (PR #1743 review).

    The resolver searches the whole owning function, so a snippet appearing
    more than once there is satisfied by the OTHER occurrence — removing the
    catalogued site leaves the pin green. Measured: `for pos, idx in
    enumerate(indices):` occurred **twice** in `_handle_assign`, and
    `used_var_positions` **three times** in `_match_subset_domain` (declaration,
    membership test, add).

    ⚠ The existing uniqueness check compares ROWS to each other and structurally
    cannot catch this — the duplicate is between a row and a different LINE of
    its own function. This is the third distinct way an anchor has failed to
    pin its site in this PR, so it is now a property rather than a review catch.
    """
    problems = []
    for rel, func, snippet, _verdict in CATALOGUED_SITES:
        source = (PROJECT_ROOT / rel).read_text(encoding="utf-8")
        lines = source.splitlines()
        owners = [
            n
            for n in ast.walk(ast.parse(source))
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == func
        ]
        body = "\n".join(
            "\n".join(lines[o.lineno - 1 : (o.end_lineno or o.lineno)]) for o in owners
        )
        n = body.count(snippet)
        if n != 1:
            problems.append(f"{rel}::{func} — anchor occurs {n}x (need exactly 1): {snippet!r}")
    assert not problems, "non-pinning anchor(s):\n  " + "\n  ".join(problems)


@pytest.mark.unit
def test_every_site_has_exactly_one_strength_class():
    """⚠ The partition must be EXHAUSTIVE and DISJOINT (PR #1743 review).

    Two catalogued sites — `_try_dotted_key_lookup` and
    `_apply_alias_offset_to_deriv` — fell outside **both** listed categories in
    an earlier revision, so a reader could not tell whether they were pinned. So
    did `_remap_condition_to_domain` and the `NEEDS A TEST` `_handle_aggregation`
    row, which the review did not name and which surfaced only by computing the
    complement.

    Deriving the split from `CATALOGUED_SITES` rather than listing it by hand is
    what makes that unrepresentable: every row is behavioural or structural, and
    the counts are asserted so an added row cannot slip in unclassified.
    """
    behavioural = [s for s in CATALOGUED_SITES if (s[0], s[1]) in BEHAVIOURALLY_PINNED]
    structural = [s for s in CATALOGUED_SITES if (s[0], s[1]) not in BEHAVIOURALLY_PINNED]

    assert len(behavioural) + len(structural) == len(CATALOGUED_SITES), "partition must cover all"
    assert not (set(behavioural) & set(structural)), "partition must be disjoint"
    assert len(behavioural) == 5, [s[1] for s in behavioural]
    assert len(structural) == 11, [s[1] for s in structural]

    # ⚠ Every `BEHAVIOURALLY_PINNED` entry must actually appear in the catalog,
    # or a typo there would silently shrink the behavioural set to nothing.
    catalogued = {(s[0], s[1]) for s in CATALOGUED_SITES}
    assert BEHAVIOURALLY_PINNED <= catalogued, BEHAVIOURALLY_PINNED - catalogued


@pytest.mark.unit
def test_the_catalog_covers_both_verdicts_and_the_shared_function():
    """⚠ Non-vacuity for the pin above, and a guard on the classification itself.

    An earlier revision listed `_handle_assign` under `NEEDS A TEST`; the survey
    has it as `ALREADY GUARDED` (alias expansion), and the `NEEDS A TEST` parser
    site is `_handle_aggregation`'s `expanded_indices.index(...)` (PR #1743
    review). Pinning the counts and the shared-function case keeps a future
    edit from silently collapsing the two verdicts again.
    """
    # ⚠ THESE ARE THE SURVEY'S OWN COUNTS (PR #1743 review). An earlier revision
    # asserted 6/7 — the number of ROWS it happened to have — which is how three
    # sites went missing unnoticed: `constraint_jacobian:1513`,
    # `derivative_rules:2411` and the second `stationarity:5148` each shared an
    # anchor with a neighbour and were silently collapsed into it. Asserting the
    # count you HAVE proves nothing; asserting the count the survey SAYS is what
    # catches an omission.
    verdicts = [v for *_rest, v in CATALOGUED_SITES]
    assert verdicts.count("NEEDS A TEST") == 7, verdicts
    assert verdicts.count("ALREADY GUARDED") == 9, verdicts
    assert len(CATALOGUED_SITES) == 16, "the survey's remaining set is 16 sites"

    # ⚠ Every anchor must be UNIQUE, or two rows collapse again.
    anchors = [(r, f, s) for r, f, s, _v in CATALOGUED_SITES]
    assert len(anchors) == len(set(anchors)), (
        "two catalogued rows share a (file, function, anchor) triple and would "
        f"pin the same site: {sorted(a for a in anchors if anchors.count(a) > 1)}"
    )

    agg = [(f, s, v) for _r, f, s, v in CATALOGUED_SITES if f == "_handle_aggregation"]
    assert len(agg) == 2, f"_handle_aggregation owns two catalogued sites; got {agg}"
    assert {v for *_x, v in agg} == {"NEEDS A TEST", "ALREADY GUARDED"}, (
        "the two sites inside _handle_aggregation carry DIFFERENT verdicts; " f"got {agg}"
    )


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

    def test_the_Sum_free_index_comprehension_collapses_the_same_way(self):
        """The `Sum`/`Prod` free-index site — the 11/15-reach one."""
        from src.ad.constraint_jacobian import _substitute_indices
        from src.ir.ast import Sum, VarRef

        # `k` is bound by the Sum, so only the free `i` is substituted; with a
        # repeated free domain it collapses onto position 0.
        node = Sum(("k",), VarRef("x", ("i", "k")), None)
        out = _substitute_indices(node, ("i", "i"), ("a1", "a2"))
        assert out.body.indices == ("a1", "k"), out.body.indices

        out = _substitute_indices(node, ("i", "m"), ("a1", "b2"))
        assert out.body.indices == ("a1", "k"), "positive control: distinct domain"

        # ⚠⚠ THE DISCRIMINATING CASE — a symbolic index the Sum actually BINDS.
        # The site's safety is "don't substitute indices bound by the
        # aggregation", and neither case above exercises it: with no overlap
        # between `symbolic_indices` and `index_sets` the free-index filter is a
        # no-op, so a mutant replacing it with `tuple(symbolic_indices)` survived
        # (PR #1743 review). Here `k` is bound, so it must NOT be substituted.
        out = _substitute_indices(node, ("i", "k"), ("a1", "k9"))
        assert out.body.indices == ("a1", "k"), (
            "`k` is bound by the Sum and must survive substitution untouched; "
            f"got {out.body.indices}"
        )

    def test_the_SymbolRef_site_collapses_the_same_way(self):
        """The bare-index `SymbolRef` site (#730), inside `Call` arguments."""
        from src.ad.constraint_jacobian import _substitute_indices
        from src.ir.ast import SymbolRef

        assert _substitute_indices(SymbolRef("i"), ("i", "i"), ("a1", "a2")).name == "a1"
        assert _substitute_indices(SymbolRef("j"), ("i", "j"), ("a1", "b2")).name == "b2"


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
    from src.ir.ast import IndexOffset, ParamRef, Prod, Sum, VarRef
    from src.ir.index_map import RepeatedDomainSymbolError
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_file
    from src.kkt.assemble import assemble_kkt_system

    # ⚠ PER-SHAPE, not aggregate (PR #1743 review). An earlier revision asserted
    # only "some repeated call happened with distinct concrete values", which one
    # call could satisfy while the other `.index(...)` shapes stopped being
    # exercised entirely — no use as the integration pin for a FOUR-site claim.
    shapes: set[str] = set()
    repeated: list[tuple] = []
    real = cj._substitute_indices

    def _spy(expr, symbolic_indices, concrete_indices):
        sym = [s.lower() for s in symbolic_indices if isinstance(s, str)]
        if len(sym) != len(set(sym)):
            repeated.append((tuple(symbolic_indices), tuple(concrete_indices)))
            if isinstance(expr, (VarRef, ParamRef)):
                if any(isinstance(i, IndexOffset) for i in expr.indices):
                    shapes.add("IndexOffset")
                if any(isinstance(i, str) for i in expr.indices):
                    shapes.add("str")
            elif isinstance(expr, (Sum, Prod)):
                shapes.add("Sum/Prod")
        return real(expr, symbolic_indices, concrete_indices)

    monkeypatch.setattr(cj, "_substitute_indices", _spy)

    # ⚠ The model is deliberately richer than a bare `x(i)`: it carries a lead
    # (`x(i+1)`) and an inner `sum(j, ...)` so that THREE of the four `.index(...)`
    # shapes are actually exercised. A first revision used a minimal model and
    # reached only the `str` shape while the docstring claimed all four.
    gams = """\
Set i / a1, a2, a3 /;
Alias (i,j);
Parameter g(i,j);  g(i,j) = 1;
Variable x(i), y(i), z;
Equation rep(i,i), zdef;
rep(i,i).. x(i) + x(i+1) + sum(j, g(i,j) * y(j)) =e= 1;
zdef.. z =e= sum(i, x(i) + y(i));
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
    # …at least one carrying genuinely DISTINCT concrete values, which is where
    # information is actually lost.
    assert any(len(set(c)) > 1 for _s, c in repeated), (
        "every repeated call had identical concrete values, so nothing was lost; "
        f"got {sorted(set(repeated))}"
    )
    # ⚠ …and EACH expected shape individually, so a regression confined to one
    # `.index(...)` site cannot hide behind the others.
    assert shapes == {"str", "IndexOffset", "Sum/Prod"}, (
        "the integration model must exercise each of these shapes with a repeated "
        f"domain; got {sorted(shapes)}. ⚠ The fourth site, bare `SymbolRef`, is "
        "simply NOT EXERCISED BY THIS MODEL — not unreachable (PR #1743 review: "
        "an earlier message claimed it needs an unresolved `Call` argument, which "
        "is wrong; the parser represents ordinary calls such as `ord(i)` as a "
        "`Call` holding a `SymbolRef`, and `_substitute_indices` recurses into "
        "call arguments). It is covered by the direct unit test above — stated "
        "rather than quietly folded into an aggregate count."
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

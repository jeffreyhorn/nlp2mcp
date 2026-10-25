"""#1755: a single-binder sum whose reference repeats the binder (Sprint 40 P7).

``diagsum(j).. sum(i, tsam(i,i)) =e= 1`` differentiated to 0 for every instance,
including the diagonal ``tsam('i1','i1')``, so the constraint and its multiplier
were dropped from the MCP (``stat_tsam(i,j).. 1 =E= 0;``).

Layer (traced, ``ISSUE_1755`` Phase 0): ``_diff_sum``'s single-binder
partial-match loop symbolizes ONE position per attempt, so ``tsam(i,i)`` never
matched. The fix places the binder at every position it occupies, but ONLY when
the ``wrt`` values there are equal. The off-diagonal positive control
(``tsam('i1','i2')`` stays 0) is what keeps that condition honest.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from src.ad.derivative_rules import differentiate_expr
from src.config import Config
from src.ir.ast import (
    Binary,
    Call,
    Const,
    DollarConditional,
    ParamRef,
    SetMembershipTest,
    Sum,
    VarRef,
)
from src.ir.model_ir import ModelIR
from src.ir.symbols import SetDef

pytestmark = pytest.mark.unit

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _config() -> Config:
    model_ir = ModelIR()
    model_ir.sets["i"] = SetDef(name="i", members=["i1", "i2", "i3"])
    model_ir.sets["k"] = SetDef(name="k", members=["k1", "k2"])
    config = Config()
    config.model_ir = model_ir
    return config


def _is_zero(expr) -> bool:
    """`Sum((i), Const(0.0))` or `Const(0.0)`: what the loss looked like."""
    if isinstance(expr, Const):
        return expr.value == 0.0
    return isinstance(expr, Sum) and isinstance(expr.body, Const) and expr.body.value == 0.0


def _d(body, var: str, wrt: tuple[str, ...]):
    return differentiate_expr(Sum(("i",), body, None), var, wrt, _config())


#: Parameter values for `_value`, by (name, concrete indices). Only concrete keys
#: exist, so a parameter whose binder was NOT substituted fails loudly.
PARAMS = {
    ("c", ("i1",)): 5.0,
    ("c", ("i2",)): 7.0,
    ("active", ("i1",)): 1.0,
    ("active", ("i2",)): 0.0,
}


def _value(expr, members: set | None = None) -> float:
    """Numeric value of a constant derivative, expanding `Sum` over `i`'s 3 members.

    The mixed-reference cases (PR #1779 review) must be judged on the VALUE: a
    partial result such as `1 + 0` is a well-formed expression, only a wrong one.
    Product-rule leftovers like `x(i2,i2) * 0` are evaluated at two different
    variable values, and both must agree, so a non-constant result cannot pass.
    """

    def ev(node, xval: float) -> float:
        if isinstance(node, Const):
            return node.value
        if isinstance(node, VarRef):
            return xval
        if isinstance(node, ParamRef):
            # Only a SUBSTITUTED parameter has a value: c(i) or c(I) left in a
            # collapsed derivative is a bug, so it must not evaluate.
            key = (node.name, node.indices)
            assert key in PARAMS, f"unsubstituted or unexpected parameter: {node}"
            return PARAMS[key]
        if isinstance(node, SetMembershipTest):
            assert members is not None, f"membership test without a membership table: {node}"
            (idx,) = node.indices
            name = getattr(idx, "name", idx)
            return 1.0 if (node.set_name, name) in members else 0.0
        if isinstance(node, DollarConditional):
            return ev(node.value_expr, xval) if ev(node.condition, xval) != 0 else 0.0
        if isinstance(node, Sum):
            assert len(node.index_sets) == 1 and node.condition is None, node
            card = {"i": 3, "k": 2}[node.index_sets[0]]  # the test sets' sizes
            return card * ev(node.body, xval)  # the body is constant in the index here
        if isinstance(node, Binary) and node.op in ("+", "-", "*", "/"):
            lhs, rhs = ev(node.left, xval), ev(node.right, xval)
            if node.op == "+":
                return lhs + rhs
            if node.op == "-":
                return lhs - rhs
            return lhs * rhs if node.op == "*" else lhs / rhs
        raise AssertionError(f"unexpected node in a derivative: {node}")

    a, b = ev(expr, 7.0), ev(expr, 11.0)
    assert a == b, f"the derivative is not constant: {expr}"
    return a


class TestTheDiagonalDifferentiates:
    def test_the_diagonal_is_one(self):
        # FAIL-BEFORE: this returned Sum((i), Const(0.0)) on main.
        assert _d(VarRef("tsam", ("i", "i")), "tsam", ("i1", "i1")) == Const(1.0)

    def test_POSITIVE_CONTROL_the_off_diagonal_stays_zero(self):
        # No single value of `i` satisfies tsam(i,i) = tsam('i1','i2'). A fix that
        # collapsed on the binder alone (without the equal-values condition)
        # would return 1 here.
        assert _is_zero(_d(VarRef("tsam", ("i", "i")), "tsam", ("i1", "i2")))

    @pytest.mark.parametrize("wrt", [("i1", "I1"), ("I1", "i1"), ("i1", "'i1'"), ("'i1'", "i1")])
    def test_a_case_or_quote_varied_TARGET_is_still_the_diagonal(self, wrt):
        # PR #1779 review round 4. `_indices_match` strips quotes and ignores
        # case, so these name the same element in both coordinates. A raw-string
        # equality check called them inconsistent and left the derivative at 0.
        assert _d(VarRef("x", ("i", "i")), "x", wrt) == Const(1.0)
        # The substituted spelling is the one that passes set membership: i1.
        out = _d(Call("sqr", (VarRef("x", ("i", "i")),)), "x", wrt)
        assert "x(i1,i1)" in str(out), out

    @pytest.mark.parametrize("wrt", [("i1", "i2"), ("I1", "i2"), ("'i1'", "i2")])
    def test_POSITIVE_CONTROL_a_varied_off_diagonal_stays_zero(self, wrt):
        assert _is_zero(_d(VarRef("x", ("i", "i")), "x", wrt))

    @pytest.mark.parametrize("wrt", [("I1", "I1"), ("'i1'", "'i1'")])
    def test_a_FULLY_noncanonical_target_resolves_to_the_declared_member(self, wrt):
        # PR #1779 review round 5: neither coordinate spells `i1` as declared, so
        # a raw membership test found no candidate and the derivative stayed 0.
        assert _d(VarRef("x", ("i", "i")), "x", wrt) == Const(1.0)
        out = _d(Call("sqr", (VarRef("x", ("i", "i")),)), "x", wrt)
        assert "x(i1,i1)" in str(out), out  # substituted with the DECLARED spelling

    @pytest.mark.parametrize("wrt", [("I1", "I2"), ("'i1'", "'i2'")])
    def test_POSITIVE_CONTROL_a_fully_noncanonical_off_diagonal_stays_zero(self, wrt):
        assert _is_zero(_d(VarRef("x", ("i", "i")), "x", wrt))

    def test_a_BODY_level_dollar_condition_does_not_hide_the_diagonal(self):
        # PR #1779 review round 5. sum(i, x(i,i)$active(i)): the loop got
        # `0$active('i1')`, took the guarded zero for a match, and returned before
        # the #1755 fallback. Active i1 -> 1; inactive i2 -> 0.
        body = DollarConditional(VarRef("x", ("i", "i")), ParamRef("active", ("i",)))
        assert _value(_d(body, "x", ("i1", "i1"))) == 1.0
        assert _value(_d(body, "x", ("i2", "i2"))) == 0.0

    def test_a_QUOTIENT_body_does_not_hide_the_diagonal(self):
        # PR #1779 review round 6. sum(i, x(i,i)/2): each single-position attempt
        # gives (2*0 - x*0)/2^2, a quotient with a zero numerator that the loop
        # took for a match, so the derivative was 0, not 0.5. 0.5*x(i,i) worked.
        assert (
            _value(_d(Binary("/", VarRef("x", ("i", "i")), Const(2.0)), "x", ("i1", "i1"))) == 0.5
        )
        # A parameter denominator: d/dx('i1','i1') of sum(i, x(i,i)/c(i)) = 1/c('i1').
        body = Binary("/", VarRef("x", ("i", "i")), ParamRef("c", ("i",)))
        assert _value(_d(body, "x", ("i1", "i1"))) == 1.0 / 5.0

    def test_an_independent_INNER_SUM_does_not_hide_the_diagonal(self):
        # PR #1779 review round 7. sum(i, x(i,i) + sum(k, c(k))): the inner sum's
        # derivative `sum(k, 0)` was taken for a match, so the loop returned 0.
        body = Binary("+", VarRef("x", ("i", "i")), Sum(("k",), ParamRef("c", ("k",)), None))
        assert _value(_d(body, "x", ("i1", "i1"))) == 1.0

    def test_a_nested_VARIABLE_sum_does_not_hide_the_diagonal(self):
        body = Binary("+", VarRef("x", ("i", "i")), Sum(("k",), VarRef("y", ("k",)), None))
        assert _value(_d(body, "x", ("i1", "i1"))) == 1.0

    def test_a_SUM_VALUED_coefficient_is_kept(self):
        # d/dx('i1','i1') of sum(i, sum(k, c(k)) * x(i,i)) = sum(k, c(k)).
        body = Binary("*", Sum(("k",), ParamRef("c", ("k",)), None), VarRef("x", ("i", "i")))
        out = _d(body, "x", ("i1", "i1"))
        # ⚠ Asserting the coefficient merely APPEARS would be vacuous: the wrong
        # output also contains it, multiplied by 0 (measured on the previous
        # revision). It must appear multiplied by the diagonal's 1.
        assert "Binary(*, Sum((k), ParamRef(c(k))), Const(1.0))" in str(out), out

    def test_a_case_only_repeat_is_a_repeat(self):
        # GAMS identifiers are case-insensitive, so `I` is the binder `i`.
        # ⚠ The two-position w(i,I) is NOT a discriminator: main already returns
        # 1 for it, by accident. #1111's free-index conversion treats `I` as a
        # distinct FREE index and symbolizes it. So the case test uses three
        # positions, where that accident cannot cover both `i` positions (verified:
        # main and an exact-spelling mutant both return 0 here).
        assert _d(VarRef("w", ("i", "I", "i")), "w", ("i3", "i3", "i3")) == Const(1.0)
        # The accidental two-position case is pinned too, so the fix cannot break it.
        assert _d(VarRef("tsam", ("i", "I")), "tsam", ("i2", "i2")) == Const(1.0)

    def test_three_positions(self):
        assert _d(VarRef("w", ("i", "i", "i")), "w", ("i3", "i3", "i3")) == Const(1.0)
        assert _is_zero(_d(VarRef("w", ("i", "i", "i")), "w", ("i3", "i3", "i1")))

    def test_a_concrete_position_must_still_match(self):
        assert _d(VarRef("v", ("i", "i", "k1")), "v", ("i1", "i1", "k1")) == Const(1.0)
        assert _is_zero(_d(VarRef("v", ("i", "i", "k1")), "v", ("i1", "i1", "k2")))

    def test_MIXED_a_collapsing_and_a_summed_reference_both_count(self):
        # PR #1779 review. d/dx('i1','i1') of sum(i, x(i,i) + x('i1','i1')) over
        # i = {i1,i2,i3} is 1 (the diagonal, at i = i1) + 3 (the concrete
        # reference, once per iteration) = 4. The first revision returned the
        # collapsed part alone (1), dropping the summed remainder.
        body = Binary("+", VarRef("x", ("i", "i")), VarRef("x", ("i1", "i1")))
        assert _value(_d(body, "x", ("i1", "i1"))) == 4.0

    def test_MIXED_two_different_layouts_both_count(self):
        # sum(i, w(i,i,'i1') + w('i1',i,i)) at w('i1','i1','i1'): each layout
        # collapses at i = i1, so the derivative is 2, not the first layout's 1.
        body = Binary("+", VarRef("w", ("i", "i", "i1")), VarRef("w", ("i1", "i", "i")))
        assert _value(_d(body, "w", ("i1", "i1", "i1"))) == 2.0

    def test_one_layout_shared_by_two_references_counts_once(self):
        # sum(i, x(i,i) + 2*x(i,i)) at x('i2','i2') is 3. Both references share a
        # layout, which one symbolic differentiation covers, so it is not doubled.
        body = Binary(
            "+", VarRef("x", ("i", "i")), Binary("*", Const(2.0), VarRef("x", ("i", "i")))
        )
        assert _value(_d(body, "x", ("i2", "i2"))) == 3.0

    def test_MIXED_CASE_one_layout_counts_once_and_substitutes_both_spellings(self):
        # PR #1779 review round 2. Index matching is case-insensitive, so
        # w(i,i,i) and w(i,I,i) are ONE layout. Keyed by spelling, they were two,
        # and each symbolic differentiation counted both references: 4, not 2.
        body = Binary("+", VarRef("w", ("i", "i", "i")), VarRef("w", ("i", "I", "i")))
        assert _value(_d(body, "w", ("i1", "i1", "i1"))) == 2.0
        # With a coefficient that needs substituting under BOTH spellings:
        # d/dw('i1','i1','i1') of sum(i, c(i)*w(i,i,i) + c(I)*w(i,I,i)) = 2*c('i1').
        body = Binary(
            "+",
            Binary("*", ParamRef("c", ("i",)), VarRef("w", ("i", "i", "i"))),
            Binary("*", ParamRef("c", ("I",)), VarRef("w", ("i", "I", "i"))),
        )
        assert _value(_d(body, "w", ("i1", "i1", "i1"))) == 2 * 5.0

    def test_an_uppercase_binder_ONLY_in_a_coefficient_is_substituted(self):
        # PR #1779 review round 3. `I` appears in no reference to x, only in c(I).
        # The spellings came from x's references alone, so c(I) survived.
        body = Binary("*", ParamRef("c", ("I",)), VarRef("x", ("i", "i")))
        assert _value(_d(body, "x", ("i1", "i1"))) == 5.0  # c('i1')

    def test_each_layout_substitutes_the_coefficient_with_ITS_OWN_value(self):
        # sum(i, c(I)*(w(i,i,'i2','i2') + w('i1','i1',i,i))) at w('i1','i1','i2','i2'):
        # the first layout binds i = i1 and the second i = i2, so the derivative
        # is c('i1') + c('i2') = 12. One symbolic c(I) cannot carry both.
        body = Binary(
            "*",
            ParamRef("c", ("I",)),
            Binary(
                "+",
                VarRef("w", ("i", "i", "i2", "i2")),
                VarRef("w", ("i1", "i1", "i", "i")),
            ),
        )
        assert _value(_d(body, "w", ("i1", "i1", "i2", "i2"))) == 5.0 + 7.0

    def test_each_layout_keeps_ITS_OWN_binding_in_the_condition(self):
        # sum(i$active(i), w(i,i,'i2','i2') + w('i1','i1',i,i)) at
        # w('i1','i1','i2','i2') = active('i1') + active('i2') = 1 + 0 = 1.
        # The same symbolic active(i) on both layouts cannot give 1.
        body = Binary("+", VarRef("w", ("i", "i", "i2", "i2")), VarRef("w", ("i1", "i1", "i", "i")))
        out = differentiate_expr(
            Sum(("i",), body, ParamRef("active", ("i",))), "w", ("i1", "i1", "i2", "i2"), _config()
        )
        assert _value(out) == 1.0

    def test_the_binder_is_substituted_through_the_body(self):
        # d sum(i, sqr(tsam(i,i))) / d tsam('i2','i2') = 2*tsam('i2','i2').
        out = _d(Call("sqr", (VarRef("tsam", ("i", "i")),)), "tsam", ("i2", "i2"))
        assert "tsam(i2,i2)" in str(out) and "tsam(i,i)" not in str(out), out
        # A coefficient indexed by the binder is substituted too: c('i3').
        out = _d(
            Binary("*", ParamRef("c", ("i",)), VarRef("tsam", ("i", "i"))), "tsam", ("i3", "i3")
        )
        assert "c(i3)" in str(out) and "c(i)" not in str(out), out


REPRODUCER = """\
Set i / i1*i3 /;
Alias (i,j);
Variable tsam(i,j), z;
Equation diagsum(j), obj;
diagsum(j).. sum(i, tsam(i,i)) =e= 1;
obj.. z =e= sum((i,j), tsam(i,j));
Model m / all /;
solve m using lp minimizing z;
"""

SCALAR = """\
Set i / i1*i3 /;
Alias (i,j);
Variable tsam(i,j), z;
Equation diag, obj;
diag.. sum(i, tsam(i,i)) =e= 1;
obj.. z =e= sum((i,j), sqr(tsam(i,j)));
Model m / all /;
solve m using nlp minimizing z;
"""


def _translate(tmp_path: Path, source: str) -> subprocess.CompletedProcess:
    src = tmp_path / "model.gms"
    src.write_text(source)
    return subprocess.run(
        [sys.executable, "-m", "src.cli", str(src), "-o", str(tmp_path / "out.gms")],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )


class TestTheEmit:
    def test_the_reproducer_keeps_its_constraint_and_multiplier(self, tmp_path):
        out = _translate(tmp_path, REPRODUCER)
        assert out.returncode == 0, out.stderr
        emit = (tmp_path / "out.gms").read_text()
        # FAIL-BEFORE: exactly this row, and no diagsum / nu_diagsum at all.
        assert "stat_tsam(i,j).. 1 =E= 0;" not in emit
        assert "diagsum.nu_diagsum" in emit, "the pair must be in the model statement"
        stat = next(line for line in emit.splitlines() if line.startswith("stat_tsam("))
        assert "nu_diagsum" in stat, stat
        # Diagonal only: every occurrence is guarded by an i = j restriction.
        assert "sameas(i, 'i1') and sameas(j, 'i1')" in stat, stat

    def test_the_scalar_variant_matches_the_hand_derived_row(self, tmp_path):
        out = _translate(tmp_path, SCALAR)
        assert out.returncode == 0, out.stderr
        emit = (tmp_path / "out.gms").read_text()
        stat = next(line for line in emit.splitlines() if line.startswith("stat_tsam("))
        assert stat.startswith("stat_tsam(i,j).. 2 * tsam(i,j) + nu_diag$("), stat
        for e in ("i1", "i2", "i3"):
            assert f"sameas(i, '{e}') and sameas(j, '{e}')" in stat, stat
        assert "diag.nu_diag" in emit


def test_a_repeated_equation_domain_is_now_REFUSED_by_1737(tmp_path):
    """⚠ Expected, and not to be "fixed" by narrowing #1737.

    Shape (a) of ``CORRECTNESS_PRETRACES.md`` §6: before this fix ``dd``'s
    multiplier was never referenced (#1755 zeroed it), so ``dd`` was silently
    DROPPED and translation exited 0. Now the multiplier is referenced, the
    empty-equation scan reaches #1737's ``assert_no_repeated_symbol``, and the
    model is REFUSED. Silently wrong → refused is the correct direction.
    """
    out = _translate(
        tmp_path,
        """\
Set i / a1*a3 /;
Alias (i,j);
Variable tsam(i,j), z;
Equation dd(i,i), obj;
dd(i,i).. sum(j, tsam(j,j)) =e= 1;
obj.. z =e= sum((i,j), sqr(tsam(i,j)));
Model m / all /;
solve m using nlp minimizing z;
""",
    )
    assert out.returncode != 0, "dd must be refused, not silently dropped"
    assert "repeats" in (out.stdout + out.stderr), out.stdout + out.stderr


def test_a_quoted_label_spelled_like_the_binder_is_not_the_binder():
    """PR #1779 review round 6. With ``Set i / i, i1, i2 /``, the reference
    ``x('i','i')`` names the ELEMENT ``i``, and the parser keeps it quoted
    (``"i"``). Index matching strips quotes, so differentiating the body against
    a symbolic ``(i,i)`` target also counted it: ``sum(i, x(i,i) + x('i','i'))``
    at ``x('i1','i1')`` gave 2, not 1. The layout now differentiates against a
    fresh placeholder for the binder, which no label can spell."""
    model_ir = ModelIR()
    model_ir.sets["i"] = SetDef(name="i", members=["i", "i1", "i2"])
    config = Config()
    config.model_ir = model_ir
    body = Binary("+", VarRef("x", ("i", "i")), VarRef("x", ('"i"', '"i"')))
    out = differentiate_expr(Sum(("i",), body, None), "x", ("i1", "i1"), config)
    assert _value(out) == 1.0
    # ⚠ NOT asserted, pre-existing: when the TARGET element is spelled like the
    # binder (`x('i','i')` at `('i','i')`), the bare-string index representation
    # cannot tell the element `i` from the binder `i`. main returns 1 for
    # sum(i, x('i','i')) there, not 3; this PR does not change that.


def _config_with(**sets: list[str]) -> Config:
    model_ir = ModelIR()
    for name, members in sets.items():
        model_ir.sets[name] = SetDef(name=name, members=members)
    config = Config()
    config.model_ir = model_ir
    return config


def test_the_placeholder_cannot_collide_with_a_TARGET_label():
    """PR #1779 review round 8. With i = {i1, i2, i__binder1755}, the target
    w('i1','i1','i__binder1755') matched the renamed three-position w(i,i,i),
    giving 1 instead of 0. Neither reference is that instance."""
    config = _config_with(i=["i1", "i2", "i__binder1755"])
    body = Binary("+", VarRef("w", ("i", "i", "i2")), VarRef("w", ("i", "i", "i")))
    out = differentiate_expr(Sum(("i",), body, None), "w", ("i1", "i1", "i__binder1755"), config)
    assert _is_zero(out) or _value(out) == 0.0, out


def test_the_placeholder_cannot_collide_with_a_MEMBER_of_another_set():
    """With k = {i__binder1755}, the inner sum(k, x(k,k)) took the placeholder for
    a member of k and contributed 1, so the derivative was 2, not 1. Reserving the
    target labels alone does not fix this; the model's set members must be reserved
    too."""
    config = _config_with(i=["i1", "i2", "i3"], k=["i__binder1755"])
    body = Binary("+", VarRef("x", ("i", "i")), Sum(("k",), VarRef("x", ("k", "k")), None))
    out = differentiate_expr(Sum(("i",), body, None), "x", ("i1", "i1"), config)
    assert _value(out) == 1.0, out


# --- PR #1779 review round 9: shared-machinery fixes ---------------------------


def _subset_config(static_s: bool = True) -> Config:
    """i = {i1,i2,i3}; s(i) = {i1,i2} (static); ii(i) dynamic (no static members)."""
    model_ir = ModelIR()
    model_ir.sets["i"] = SetDef(name="i", members=["i1", "i2", "i3"])
    model_ir.sets["s"] = SetDef(name="s", members=["i1", "i2"], domain=("i",))
    model_ir.sets["ii"] = SetDef(name="ii", members=[], domain=("i",))
    config = Config()
    config.model_ir = model_ir
    return config


def test_CARD_operand_is_not_substituted_in_a_diagonal_collapse():
    # card(s) is the subset's cardinality (2). Substituted, it became card(i1),
    # which stationarity maps back to the PARENT's cardinality (3).
    from src.ir.ast import SymbolRef

    body = Binary("*", Call("card", (SymbolRef("s"),)), VarRef("x", ("s", "s")))
    out = differentiate_expr(Sum(("s",), body, None), "x", ("i1", "i1"), _subset_config())
    assert "Call(card, (SymbolRef(s)))" in str(out), out
    assert "card, (SymbolRef(i1))" not in str(out), out


def test_CARD_operand_is_not_substituted_in_a_single_position_collapse_either():
    # The shared substitution: the pre-existing single-position path had the same
    # card(s) -> card(i1) loss on main.
    from src.ir.ast import SymbolRef

    body = Binary("*", Call("card", (SymbolRef("s"),)), VarRef("y", ("s",)))
    out = differentiate_expr(Sum(("s",), body, None), "y", ("i1",), _subset_config())
    assert "Call(card, (SymbolRef(s)))" in str(out), out


def test_ORD_is_still_substituted():
    # Only card() is set-level; ord(s) is the iterate's position and must follow it.
    from src.ir.ast import SymbolRef

    body = Binary("*", Call("ord", (SymbolRef("s"),)), VarRef("y", ("s",)))
    out = differentiate_expr(Sum(("s",), body, None), "y", ("i1",), _subset_config())
    assert "Call(ord, (SymbolRef(i1)))" in str(out), out


@pytest.mark.parametrize(
    "wrt, member, expected",
    [(("i1", "i1"), "i1", 1.0), (("i2", "i2"), "i1", 0.0)],
)
def test_a_DYNAMIC_subset_binder_keeps_its_runtime_membership(wrt, member, expected):
    """sum(ii, x(ii,ii)) with ii assigned at runtime. AD resolves ii to the
    PARENT's elements, so the collapsed derivative must carry ii(<value>):
    active -> 1, inactive -> 0. It was an unguarded 1 for both."""
    from src.ir.ast import SetMembershipTest

    out = differentiate_expr(
        Sum(("ii",), VarRef("x", ("ii", "ii")), None), "x", wrt, _subset_config()
    )
    tests = [n for n in _walk(out) if isinstance(n, SetMembershipTest)]
    assert tests and all(t.set_name == "ii" for t in tests), out
    assert _value(out, members={("ii", member)}) == expected


def test_a_STATIC_subset_binder_gets_no_runtime_guard():
    # Membership resolution already rejects a static subset's non-members, so a
    # guard would only add text (and move goldens) for nothing.
    from src.ir.ast import SetMembershipTest

    out = differentiate_expr(
        Sum(("s",), VarRef("x", ("s", "s")), None), "x", ("i1", "i1"), _subset_config()
    )
    assert not [n for n in _walk(out) if isinstance(n, SetMembershipTest)], out


def _walk(node):
    yield node
    children = getattr(node, "children", None)
    if callable(children):
        for child in children():
            yield from _walk(child)


def test_CARD_inside_an_INDEX_OFFSET_follows_ord_onto_the_same_set():
    """The #1335 time-reversal idiom `p(t + (card(t) - ord(t)))` is a RELATIVE
    position: `card` and `ord` must be substituted TOGETHER (#1178). Preserving
    `card` there gave otpop `p(tt + (card(t) - ord(tt)))`, the wrong element, and
    lost its cold match (measured by the resolver in PR #1779 review round 9). A
    `card()` used as a value keeps its operand; inside an offset it does not."""
    from src.ad.derivative_rules import _substitute_sum_indices
    from src.ir.ast import IndexOffset, SymbolRef

    offset = Binary("-", Call("card", (SymbolRef("t"),)), Call("ord", (SymbolRef("t"),)))
    ref = ParamRef("p", (IndexOffset("t", offset, False),))
    out = _substitute_sum_indices(ref, ("t",), ("t1",))
    assert "card, (SymbolRef(t1))" in str(out) and "ord, (SymbolRef(t1))" in str(out), out
    # ...while a card() VALUE keeps its set operand.
    value = Binary("*", Call("card", (SymbolRef("t"),)), ParamRef("q", ("t",)))
    out = _substitute_sum_indices(value, ("t",), ("t1",))
    assert "card, (SymbolRef(t))" in str(out) and "q(t1)" in str(out), out


def _nested_config() -> Config:
    """x(i,j), Alias(i,j), runtime ii(i) (dynamic, no static members)."""
    from src.ir.symbols import AliasDef, VariableDef

    model_ir = ModelIR()
    model_ir.sets["i"] = SetDef(name="i", members=["i1", "i2"])
    model_ir.sets["ii"] = SetDef(name="ii", members=[], domain=("i",))
    model_ir.aliases["j"] = AliasDef(name="j", target="i")
    model_ir.variables["x"] = VariableDef(name="x", domain=("i", "j"))
    config = Config()
    config.model_ir = model_ir
    return config


def _guard_value(out, wrt: tuple[str, str], active: set[str]) -> float:
    """Evaluate a collapsed derivative's runtime guard at the target ``wrt``.

    A guard over a declared domain symbol (``ii(i)``) names a COORDINATE of the
    variable, so it is read at that coordinate of the target; a concrete one
    (``ii('i1')``) is read as written."""
    coords = {"i": wrt[0], "j": wrt[1]}
    members = set()
    for node in _walk(out):
        if isinstance(node, SetMembershipTest):
            (idx,) = node.indices
            name = getattr(idx, "name", idx)
            if coords.get(name, name) in active:
                members.add((node.set_name, name))
    return _value(out, members=members)


@pytest.mark.parametrize(
    "wrt, expected",
    [(("i1", "i2"), 1.0), (("i2", "i2"), 0.0)],
    ids=["active", "excluded"],
)
def test_an_ENCLOSING_sum_cannot_capture_the_guard_coordinate(wrt, expected):
    """PR #1779 review round 11. In sum(i, sum(ii, x(ii,i))) the inner guard was
    written over the declared coordinate `i`, which the OUTER binder `i` then
    substituted with the second coordinate: ii('i2') at x('i1','i2'), 0 instead of
    1. The guard now falls back to the binder when an enclosing sum binds the
    symbol, so it collapses to the right element first. Nested and flat agree."""
    config = _nested_config()
    nested = Sum(("i",), Sum(("ii",), VarRef("x", ("ii", "i")), None), None)
    flat = Sum(("ii",), VarRef("x", ("ii", wrt[1])), None)
    active = {"i1"}
    assert _guard_value(differentiate_expr(nested, "x", wrt, config), wrt, active) == expected
    assert _guard_value(differentiate_expr(flat, "x", wrt, config), wrt, active) == expected


@pytest.mark.parametrize(
    "wrt, expected",
    [(("i1", "i2"), 1.0), (("i2", "i2"), 0.0)],
    ids=["active", "excluded"],
)
def test_a_FREE_index_cannot_capture_the_guard_coordinate(wrt, expected):
    """PR #1779 review round 12. sum(ii, x(ii,i)) with a SYMBOLIC free `i` (the
    equation's own index): #1111's free-index recovery substituted the guard's
    declared `i` from the second coordinate, giving ii('i2') at x('i1','i2') with
    no enclosing sum. The flat control above uses a LITERAL second index, so it
    could not see this. Any name the body uses now counts as occupied."""
    config = _nested_config()
    body = Sum(("ii",), VarRef("x", ("ii", "i")), None)
    out = differentiate_expr(body, "x", wrt, config)
    assert _guard_value(out, wrt, {"i1"}) == expected, out


def test_a_QUOTED_label_does_not_occupy_the_guard_coordinate():
    """PR #1779 review round 14. A literal label ``p('j')`` (kept quoted, ``"j"``)
    is never rewritten by substitution, so it must not occupy the declared
    coordinate ``j``. Stripping its quotes did, forcing the ``jj`` guard back onto
    its binder, which stationarity then generalized to ``jj(i)``."""
    from src.ir.symbols import AliasDef, VariableDef

    model_ir = ModelIR()
    model_ir.sets["i"] = SetDef(name="i", members=["i1", "i2"])
    model_ir.sets["ii"] = SetDef(name="ii", members=[], domain=("i",))
    model_ir.sets["jj"] = SetDef(name="jj", members=[], domain=("i",))
    model_ir.aliases["j"] = AliasDef(name="j", target="i")
    model_ir.variables["x"] = VariableDef(name="x", domain=("i", "j"))
    config = Config()
    config.model_ir = model_ir
    body = Call("sqr", (Binary("-", VarRef("x", ("ii", "jj")), ParamRef("p", ('"j"',))),))
    out = differentiate_expr(Sum(("ii", "jj"), body, None), "x", ("i1", "i2"), config)
    tests = {
        (n.set_name, getattr(n.indices[0], "name", None))
        for n in _walk(out)
        if isinstance(n, SetMembershipTest)
    }
    assert ("jj", "j") in tests and ("ii", "i") in tests, out


def test_a_promoted_coordinate_is_not_captured_by_a_RENAMED_remaining_binder():
    """PR #1779 review round 14. i = {a,b}, runtime ii = {a}, Alias(ii,k),
    Alias(i,k__), x(k__): in sum((ii,k), x(ii)*p(k)) the promoted guard is
    ii(k__), and _partial_collapse_sum renamed the remaining binder k to k__,
    capturing it inside the surviving sum (1 instead of 0 at x('b')). The rename
    now avoids every name the body already uses."""
    from src.ir.symbols import AliasDef, VariableDef

    model_ir = ModelIR()
    model_ir.sets["i"] = SetDef(name="i", members=["a", "b"])
    model_ir.sets["ii"] = SetDef(name="ii", members=[], domain=("i",))
    model_ir.aliases["k"] = AliasDef(name="k", target="ii")
    model_ir.aliases["k__"] = AliasDef(name="k__", target="i")
    model_ir.variables["x"] = VariableDef(name="x", domain=("k__",))
    config = Config()
    config.model_ir = model_ir
    body = Binary("*", VarRef("x", ("ii",)), ParamRef("p", ("k",)))
    out = differentiate_expr(Sum(("ii", "k"), body, None), "x", ("b",), config)
    guard_symbols = {
        getattr(n.indices[0], "name", None) for n in _walk(out) if isinstance(n, SetMembershipTest)
    }
    assert "k__" in guard_symbols, out  # the promoted coordinate guard survives
    for node in _walk(out):
        if isinstance(node, Sum):
            assert "k__" not in node.index_sets, f"guard captured by {node.index_sets}"


def _numeric(expr, config, xvals, pvals=None, members=None, coords=None):
    """Evaluate a derivative NUMERICALLY, expanding Sum/Prod over the config's sets.

    The round-15 findings are about values (16 vs 32, 8 vs 12), so they are
    checked as values. A binder is expanded by substituting each member of its set,
    resolved through aliases, and a dynamic subset iterates its parent's members
    with its own membership supplied by ``members``.
    """
    from src.ad.derivative_rules import _substitute_sum_indices
    from src.ir.ast import Prod, SymbolRef

    model_ir = config.model_ir
    pvals = pvals or {}
    members = members or {}
    # A guard promoted to a declared COORDINATE (e.g. `ii(k__)`) names the target's
    # coordinate, which stationarity maps to the row index; read it at the target.
    coords = coords or {}

    def elements(name: str) -> list[str]:
        target = name
        # A binder renamed by _partial_collapse_sum (`k` -> `k____`) iterates the
        # original binder's set.
        while target not in model_ir.sets and target not in model_ir.aliases:
            assert target.endswith("_"), f"unknown binder {name}"
            target = target[:-1]
        while target in model_ir.aliases:
            target = model_ir.aliases[target].target
        if target in members:  # a dynamic subset: iterate exactly its members
            return sorted(members[target])
        sdef = model_ir.sets[target]
        return list(sdef.members) if sdef.members else elements(sdef.domain[0])

    def ev(node):
        if isinstance(node, Const):
            return node.value
        if isinstance(node, VarRef):
            return xvals[node.indices]
        if isinstance(node, ParamRef):
            return pvals.get((node.name, node.indices), 1.0)
        if isinstance(node, SetMembershipTest):
            (idx,) = node.indices
            name = getattr(idx, "name", idx)
            return 1.0 if coords.get(name, name) in members.get(node.set_name, ()) else 0.0
        if isinstance(node, DollarConditional):
            return ev(node.value_expr) if ev(node.condition) != 0 else 0.0
        if isinstance(node, Call) and node.func == "sqr":
            return ev(node.args[0]) ** 2
        if isinstance(node, Binary):
            if node.op == "and":
                return 1.0 if ev(node.left) != 0 and ev(node.right) != 0 else 0.0
            a, b = ev(node.left), ev(node.right)
            return {"+": a + b, "-": a - b, "*": a * b, "/": a / b if b else 0.0}[node.op]
        if isinstance(node, (Sum, Prod)):
            total = 0.0 if isinstance(node, Sum) else 1.0
            combos = [()]
            for b in node.index_sets:
                combos = [c + (e,) for c in combos for e in elements(b)]
            for combo in combos:
                if node.condition is not None:
                    cond = _substitute_sum_indices(node.condition, node.index_sets, combo)
                    if ev(cond) == 0:
                        continue
                body = _substitute_sum_indices(node.body, node.index_sets, combo)
                value = ev(body)
                total = total + value if isinstance(node, Sum) else total * value
            return total
        if isinstance(node, SymbolRef):
            raise AssertionError(f"unbound symbol in a numeric derivative: {node}")
        raise AssertionError(f"unhandled node: {node}")

    return ev(expr)


def test_an_enclosing_PRODUCT_cannot_capture_the_guard_coordinate():
    """PR #1779 review round 15. x(i), i = {a,b}, k = {k1,k2}, runtime ii = {a}:
    prod((i,k), sum(ii, x(ii))) = x(a)^4, so d/dx('a') = 4*x(a)^3 = 32 at x(a) = 2.
    The product's log-derivative sum re-binds `i`, and the promoted guard `ii(i)`
    was captured, excluding half the terms: 16. Products now push their binders
    like sums."""
    from src.ir.ast import Prod
    from src.ir.symbols import VariableDef

    model_ir = ModelIR()
    model_ir.sets["i"] = SetDef(name="i", members=["a", "b"])
    model_ir.sets["k"] = SetDef(name="k", members=["k1", "k2"])
    model_ir.sets["ii"] = SetDef(name="ii", members=[], domain=("i",))
    model_ir.variables["x"] = VariableDef(name="x", domain=("i",))
    config = Config()
    config.model_ir = model_ir
    expr = Prod(("i", "k"), Sum(("ii",), VarRef("x", ("ii",)), None), None)
    out = differentiate_expr(expr, "x", ("a",), config)
    value = _numeric(out, config, {("a",): 2.0, ("b",): 5.0}, members={"ii": {"a"}})
    assert value == 32.0, (value, out)


def test_a_rename_cannot_capture_a_concrete_TARGET_label():
    """PR #1779 review round 15. The round-14 fixture with i = {a, k___} and
    runtime ii = i: renaming the remaining binder `k` to `k___` turned the concrete
    x('k___') in the surviving sum into the binder. d/dx('k___') of
    sum((ii,k), sqr(x(ii))*p(k)) with p = 1 is 2*x(k___)*|k| = 2*3*2 = 12; it was 8."""
    from src.ir.symbols import AliasDef, VariableDef

    model_ir = ModelIR()
    model_ir.sets["i"] = SetDef(name="i", members=["a", "k___"])
    model_ir.sets["ii"] = SetDef(name="ii", members=[], domain=("i",))
    model_ir.aliases["k"] = AliasDef(name="k", target="ii")
    model_ir.aliases["k__"] = AliasDef(name="k__", target="i")
    model_ir.variables["x"] = VariableDef(name="x", domain=("k__",))
    config = Config()
    config.model_ir = model_ir
    body = Binary("*", Call("sqr", (VarRef("x", ("ii",)),)), ParamRef("p", ("k",)))
    out = differentiate_expr(Sum(("ii", "k"), body, None), "x", ("k___",), config)
    xvals = {("a",): 1.0, ("k___",): 3.0}
    value = _numeric(out, config, xvals, members={"ii": {"a", "k___"}}, coords={"k__": "k___"})
    assert value == 12.0, (value, out)

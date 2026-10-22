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
from src.ir.ast import Binary, Call, Const, DollarConditional, ParamRef, Sum, VarRef
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


def _value(expr) -> float:
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
        if isinstance(node, DollarConditional):
            return ev(node.value_expr, xval) if ev(node.condition, xval) != 0 else 0.0
        if isinstance(node, Sum):
            assert node.index_sets == ("i",) and node.condition is None, node
            return 3 * ev(node.body, xval)  # the body is constant in `i` here
        if isinstance(node, Binary) and node.op in ("+", "*"):
            lhs, rhs = ev(node.left, xval), ev(node.right, xval)
            return lhs + rhs if node.op == "+" else lhs * rhs
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

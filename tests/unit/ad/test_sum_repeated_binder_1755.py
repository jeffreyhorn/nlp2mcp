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
from src.ir.ast import Binary, Call, Const, ParamRef, Sum, VarRef
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


class TestTheDiagonalDifferentiates:
    def test_the_diagonal_is_one(self):
        # FAIL-BEFORE: this returned Sum((i), Const(0.0)) on main.
        assert _d(VarRef("tsam", ("i", "i")), "tsam", ("i1", "i1")) == Const(1.0)

    def test_POSITIVE_CONTROL_the_off_diagonal_stays_zero(self):
        # No single value of `i` satisfies tsam(i,i) = tsam('i1','i2'). A fix that
        # collapsed on the binder alone (without the equal-values condition)
        # would return 1 here.
        assert _is_zero(_d(VarRef("tsam", ("i", "i")), "tsam", ("i1", "i2")))

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

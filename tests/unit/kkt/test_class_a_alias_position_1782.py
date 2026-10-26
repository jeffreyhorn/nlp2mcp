"""#1782 (Sprint 40 P4, Class A / turkpow): an equation index matched to an ALIASED
variable position by alias root.

With ``Alias(t,v)``, ``e(t)`` and ``z(v,t)``, both of z's positions canonicalize to
``t``. ``_compute_index_offset_key`` and ``_match_subset_domain`` each took position
0 (``v``), so the multiplier became ``nu_e(v)``, the genuine ``t`` was minted as
``t__kkt1`` and summed over, and the guard repeated a coordinate: ``s(t,t)``. Both
now follow the variable position the equation index's REFERENCE occupies
(``_eq_index_ref_binding``, PR #1783 review rounds 1-2). In ``_match_subset_domain``
the binding only suppresses a rename, never creates one (round 3).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

PROJECT_ROOT = Path(__file__).resolve().parents[3]

ALIASED = """\
Set t / t1*t3 /;
Alias (t,v);
Set s(t,v);
s(t,v) = yes$(ord(t) <= ord(v));
Parameter c(t,v);
c(t,v) = 1 + ord(t) + 2*ord(v);
Variable z(v,t), obj;
Equation e(t), defobj;
e(t).. sum(v$s(t,v), c(v,t)*z(v,t)) =e= 1;
defobj.. obj =e= sum((v,t), sqr(z(v,t)));
Model m / all /;
solve m using nlp minimizing obj;
"""

# POSITIVE CONTROL: the same model with DISTINCT sets (and distinct labels: shared
# labels would reintroduce the element-to-set ambiguity) already emits the correct row.
DISTINCT = ALIASED.replace("Alias (t,v);", "Set v / v1*v3 /;").replace(
    "Parameter c(t,v);\nc(t,v)", "Parameter c(v,t);\nc(v,t)"
)

EXPECTED_ROW = "stat_z(v,t).. 2 * z(v,t) + c(v,t) * 1$(s(t,v)) * nu_e(t) =E= 0;"


def _emit(tmp_path: Path, source: str) -> str:
    src = tmp_path / "model.gms"
    src.write_text(source)
    out = tmp_path / "out.gms"
    proc = subprocess.run(
        [sys.executable, "-m", "src.cli", str(src), "-o", str(out)],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    assert proc.returncode == 0, proc.stderr
    return out.read_text()


def _stat_row(emit: str) -> str:
    return next(line for line in emit.splitlines() if line.startswith("stat_z("))


def test_the_aliased_fixture_emits_the_hand_derived_row(tmp_path):
    # FAIL-BEFORE (main): sum(t__kkt1, c(v,t__kkt1)*1$(s(t__kkt1,t__kkt1))*nu_e(v)).
    row = _stat_row(_emit(tmp_path, ALIASED))
    assert row == EXPECTED_ROW, row


def test_P2_no_guard_repeats_a_coordinate_and_the_multiplier_is_nu_e_t(tmp_path):
    row = _stat_row(_emit(tmp_path, ALIASED))
    for args in re.findall(r"\$\((?:\w+)\(([^()]*)\)\)", row):
        coords = [a.strip().lower() for a in args.split(",")]
        assert len(coords) == len(set(coords)), f"repeated coordinate in guard: {args}"
    assert "nu_e(t)" in row and "nu_e(v)" not in row, row
    assert "t__kkt" not in row, "no minted alias: nothing remains free to sum over"


def test_POSITIVE_CONTROL_distinct_sets_are_unchanged(tmp_path):
    row = _stat_row(_emit(tmp_path, DISTINCT))
    assert row == EXPECTED_ROW, row


def test_match_subset_domain_follows_the_REFERENCE_binding():
    """The unit of the second fix: e(t) against z(v,t) under Alias(t,v). With the
    reference binding {0: 1} (``t`` sits at z's position 1) no rename is needed;
    without one, the same-position fallback keeps its old answer {t: v}."""
    from src.ir.model_ir import ModelIR
    from src.ir.symbols import AliasDef, SetDef
    from src.kkt.stationarity import _match_subset_domain

    model_ir = ModelIR()
    model_ir.sets["t"] = SetDef(name="t", members=["t1", "t2", "t3"])
    model_ir.aliases["v"] = AliasDef(name="v", target="t")
    assert _match_subset_domain(("t",), ("v", "t"), model_ir, ref_binding={0: 1}) == {}
    assert _match_subset_domain(("t",), ("v", "t"), model_ir) == {"t": "v"}


# --- PR #1783 review: the binding comes from the REFERENCE, not the declared name ---

REVERSED = """\
Set i / i1*i3 /;
Alias (i,j);
Parameter c(i,j);
c(i,j) = 1 + ord(i) + 3*ord(j);
Variable x(i,j), obj;
Equation e(j,i), defobj;
e(j,i).. x(j,i) =e= c(j,i);
defobj.. obj =e= sum((i,j), ord(i)*sqr(x(i,j)));
Model m / all /;
solve m using nlp minimizing obj;
"""

FIXED_COORDINATE = """\
Set t / t1*t3 /;
Alias (t,v);
Variable z(v,t), obj;
Equation e(t), defobj;
e(t).. z(t,'t1') =e= ord(t);
defobj.. obj =e= sum((v,t), sqr(z(v,t)));
Model m / all /;
solve m using nlp minimizing obj;
"""

TRANSPOSED_SUM = """\
Set t / t1*t3 /;
Alias (t,v);
Parameter c(t,v);
c(t,v) = 1 + ord(t) + 2*ord(v);
Variable z(v,t), obj;
Equation e(t), defobj;
e(t).. sum(v, c(t,v)*z(t,v)) =e= 1;
defobj.. obj =e= sum((v,t), sqr(z(v,t)));
Model m / all /;
solve m using nlp minimizing obj;
"""


def test_a_REVERSED_equal_arity_domain_keeps_its_positional_multiplier(tmp_path):
    # e(j,i).. x(j,i) with x(i,j): j binds position 0. A declared-NAME preference
    # (position 1 is named `j`) emitted nu_e(j,i), with wrong multiplier values.
    emit = _emit(tmp_path, REVERSED)
    row = next(line for line in emit.splitlines() if line.startswith("stat_x("))
    assert "nu_e(i,j)" in row and "nu_e(j,i)" not in row, row


def test_a_FIXED_COORDINATE_reference_binds_the_coordinate_it_occupies(tmp_path):
    # e(t).. z(t,'t1'): t binds z's position 0 although position 1 is named `t`.
    # The name preference produced spurious offsets and an MCP that did not solve.
    row = _stat_row(_emit(tmp_path, FIXED_COORDINATE))
    assert row == "stat_z(v,t).. 2 * z(v,t) + nu_e(v)$(sameas(t, 't1')) =E= 0;", row


def test_a_TRANSPOSED_sum_reference_binds_position_zero(tmp_path):
    # e(t).. sum(v, c(t,v)*z(t,v)): t binds z's position 0.
    row = _stat_row(_emit(tmp_path, TRANSPOSED_SUM))
    assert row == "stat_z(v,t).. 2 * z(v,t) + c(v,t) * nu_e(v) =E= 0;", row


def test_the_binding_requires_the_SAME_single_position_in_EVERY_reference():
    """PR #1783 review round 2. A reference independent of the equation index
    (`z('t1','t1')`, `z('t2','t4')`) must not let the OTHER reference's position
    stand as the binding: a union did, and on `e(t).. 2*z('t3',t) - z('t2','t4')`
    it produced a silent wrong answer (MCP 37.75 vs NLP 7.5). Mixed references now
    leave the binding to the fallback (main's behaviour; that shape is a
    stationarity defect tracked on #1778)."""
    from src.ir.ast import Binary, Const, VarRef
    from src.ir.symbols import EquationDef, Rel
    from src.kkt.stationarity import _eq_index_ref_binding

    def eq(*refs):
        body = refs[0]
        for r in refs[1:]:
            body = Binary("+", body, r)
        return EquationDef(name="e", domain=("t",), relation=Rel.EQ, lhs_rhs=(body, Const(1.0)))

    bound = VarRef("z", ("v", "t"))
    assert _eq_index_ref_binding(eq(bound), "z", ("t",)) == {0: 1}
    assert _eq_index_ref_binding(eq(bound, VarRef("z", ("v", "t"))), "z", ("t",)) == {0: 1}
    # mixed: one reference holds `t`, another does not
    assert (
        _eq_index_ref_binding(eq(VarRef("z", ("t1", "t")), VarRef("z", ("t1", "t1"))), "z", ("t",))
        == {}
    )
    # inconsistent positions across references
    assert (
        _eq_index_ref_binding(eq(VarRef("z", ("t", "t1")), VarRef("z", ("t1", "t"))), "z", ("t",))
        == {}
    )
    # repeated within one reference
    assert _eq_index_ref_binding(eq(VarRef("z", ("t", "t"))), "z", ("t",)) == {}


# --- PR #1783 review round 3: the binding is applied ONCE ---

MULTI_INDEX = """\
Set i / a, b, c /;
Alias (i,j,k);
Variable z(i,j,k), obj;
Equation e(i,j), defobj;
e(i,j).. z('a',i,j) =e= ord(i) + ord(j);
defobj.. obj =e= sum((i,j,k), sqr(z(i,j,k)));
Model m / all /;
solve m using nlp minimizing obj;
"""


def test_a_MULTI_INDEX_binding_does_not_rename_the_remapped_multiplier(tmp_path):
    # The binding {0: 1, 1: 2} is right; the dimension-mismatch branch already
    # builds nu_e(j,k). Deriving the rename {i: j, j: k} from the binding and
    # applying it again made it nu_e(k,k), losing a coordinate (MCP did not solve).
    row = _stat_row(_emit(tmp_path, MULTI_INDEX))
    assert row == "stat_z(i,j,k).. 2 * z(i,j,k) + nu_e(j,k)$(sameas(i, 'a')) =E= 0;", row


def test_match_subset_domain_never_CREATES_a_rename_from_the_binding():
    """The binding only suppresses a rename (when the bound position carries the
    mult index's own name); it is never the source of one."""
    from src.ir.model_ir import ModelIR
    from src.ir.symbols import AliasDef, SetDef
    from src.kkt.stationarity import _match_subset_domain

    model_ir = ModelIR()
    model_ir.sets["i"] = SetDef(name="i", members=["a", "b", "c"])
    model_ir.aliases["j"] = AliasDef(name="j", target="i")
    model_ir.aliases["k"] = AliasDef(name="k", target="i")
    binding = {0: 1, 1: 2}
    assert _match_subset_domain(
        ("i", "j"), ("i", "j", "k"), model_ir, ref_binding=binding
    ) == _match_subset_domain(("i", "j"), ("i", "j", "k"), model_ir)

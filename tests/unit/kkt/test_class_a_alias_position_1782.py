"""#1782 (Sprint 40 P4, Class A / turkpow): an equation index matched to an ALIASED
variable position by alias root.

With ``Alias(t,v)``, ``e(t)`` and ``z(v,t)``, both of z's positions canonicalize to
``t``. ``_compute_index_offset_key`` and ``_match_subset_domain`` each took position
0 (``v``), so the multiplier became ``nu_e(v)``, the genuine ``t`` was minted as
``t__kkt1`` and summed over, and the guard repeated a coordinate: ``s(t,t)``. Both
now prefer the variable position declared with the equation index's own NAME.
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

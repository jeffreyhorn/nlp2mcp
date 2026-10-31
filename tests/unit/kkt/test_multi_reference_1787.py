"""#1787 (Sprint 40 Day 8, P4): a variable referenced twice, with the equation
index at DIFFERENT positions, gets one stationarity term per reference.

egypt's ``fodb(r,cf).. … + sum(rp$tranc(r,rp), trans(cf,rp,r) - trans(cf,r,rp))$ct(cf)``
against ``trans(c,r,rp)`` needs ``+nu_fodb(rp,c)$tranc(rp,r) - nu_fodb(r,c)$tranc(r,rp)``
(Prep Task 10 §2's hand-derived pair). Consolidating every Jacobian entry into one
representative kept a single term, built on a diagonal instance:
``1$(tranc(rp,rp))*nu_fodb(r,c)`` (P2's ``tranc(rp,rp)``).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# The bare shape. NLP 1.3333; before: no solve.
TWO_REFERENCES = """\
Set r / r1*r3 /, c / c1*c2 /;
Alias (r,rp);
Set tranc(r,rp);
tranc(r,rp) = yes$(ord(r) <> ord(rp));
Parameter d(r,c);
d(r,c) = ord(r) - 2 + ord(c)/4;
Positive Variable trans(c,r,rp);
Variable obj;
Equation fodb(r,c), defobj;
fodb(r,c).. sum(rp$tranc(r,rp), trans(c,rp,r) - trans(c,r,rp)) =e= d(r,c) - sum(rp, d(rp,c))/card(r);
defobj.. obj =e= sum((c,r,rp), sqr(trans(c,r,rp)));
Model m / all /;
solve m using nlp minimizing obj;
"""

# egypt's own shape: subset `cf(c)`, the outer `$ct(cf)`, a PARAMETER `tranc`, and
# another variable on the other side. NLP 33.25; before: 34.75 (silent).
EGYPT_SHAPE = """\
Set r / r1*r3 /, c / c1*c3 /, cf(c) / c1, c2 /, ct(c) / c2, c3 /;
Alias (r,rp);
Parameter tranc(r,rp), d(r,c);
tranc(r,rp) = 1$(ord(r) <> ord(rp));
d(r,c) = 2 + ord(r) - ord(c)/2;
Positive Variable trans(c,r,rp), fodder(r,c);
Variable obj;
Equation fodb(r,c), defobj;
fodb(r,cf).. fodder(r,cf) =e= d(r,cf) + sum(rp$tranc(r,rp), trans(cf,rp,r) - trans(cf,r,rp))$ct(cf);
defobj.. obj =e= sum((c,r,rp), sqr(trans(c,r,rp))) + sum((r,c), sqr(fodder(r,c) - 1));
Model m / all /;
solve m using nlp minimizing obj;
"""


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


def _row(emit: str, head: str) -> str:
    return next(line for line in emit.splitlines() if line.startswith(head))


def test_each_REFERENCE_gets_its_own_term(tmp_path):
    row = _row(_emit(tmp_path, TWO_REFERENCES), "stat_trans(")
    assert row == (
        "stat_trans(c,r,rp).. 2 * trans(c,r,rp) + 1$(tranc(rp,r)) * nu_fodb(rp,c)"
        " - 1$(tranc(r,rp)) * nu_fodb(r,c) - piL_trans(c,r,rp) =E= 0;"
    ), row


def test_the_EGYPT_shape_keeps_both_terms_under_its_conditions(tmp_path):
    row = _row(_emit(tmp_path, EGYPT_SHAPE), "stat_trans(")
    assert "1$(tranc(rp,r)))$(ct(c))) * nu_fodb(rp,c))$(cf(c))" in row, row
    assert "1$(tranc(r,rp)))$(ct(c))) * nu_fodb(r,c))$(cf(c))" in row, row
    assert "tranc(rp,rp)" not in row, row


def test_the_layouts_need_every_eq_index_and_two_placements():
    from src.ir.parser import parse_model_text
    from src.kkt.stationarity import _multi_reference_layouts

    model = parse_model_text(TWO_REFERENCES)
    layouts = _multi_reference_layouts(model.equations["fodb"], "trans")
    assert layouts == [{"c": 0, "rp": 1, "r": 2}, {"c": 0, "r": 1, "rp": 2}], layouts
    # one placement only -> not this shape
    single = parse_model_text(TWO_REFERENCES.replace(" - trans(c,r,rp)", ""))
    assert _multi_reference_layouts(single.equations["fodb"], "trans") is None

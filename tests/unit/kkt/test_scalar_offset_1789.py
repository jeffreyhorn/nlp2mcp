"""#1789 (Sprint 40 Days 8-10, P5): a SCALAR variable's stationarity row over a
head-offset equation keeps its lead/lag references.

``_add_jacobian_transpose_terms_scalar`` generalises ONE instance's derivative to
the whole constraint domain, mapping labels to set names by membership only:

* lead head (lnts' ``pos_eqn(c+2,h+1)``): ``u(h1) + u(h2)`` both mapped to ``h``
  -> ``2*u(h)``;
* lag head (robot's ``rho_eqn(h-1)``): the FIRST instance is the boundary, with
  no ``u(h-1)``, so the reference was dropped from every row.

The fix converts offset labels to ``IndexOffset`` relative to the constraint's
own labels (the indexed path's #1162 substitution) and generalises from the
instance with the most distinct references, not the boundary.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

PROJECT_ROOT = Path(__file__).resolve().parents[3]

_BASE = """\
Set h / h1*h5 /;
Parameter tgt(h);  tgt(h) = power(ord(h),3);
Variable x(h), u(h), obj;  Positive Variable step;
Equation dyn(h), defobj;
{dyn}
defobj.. obj =e= sum(h, sqr(x(h) - tgt(h))) + sum(h, sqr(u(h) - ord(h))) + sqr(step - 1);
x.fx('h1') = 0;
Model m / all /;  solve m using nlp minimizing obj;
"""

# NLP 68.5456 for both; before: 68.577 (lead) and 72.689 (lag).
LEAD_HEAD = _BASE.format(dyn="dyn(h+1).. x(h+1) =e= x(h) + 0.5*step*(u(h) + u(h+1));")
LAG_HEAD = _BASE.format(dyn="dyn(h-1).. x(h) =e= x(h-1) + 0.5*step*(u(h) + u(h-1));")

# Positive control: the derivative references only the constraint's OWN index.
OWN_INDEX = _BASE.format(dyn="dyn(h)$(ord(h) > 1).. x(h) =e= x(h-1) + step*u(h);")

# A quoted literal of the same set: NOT an offset. (Its membership lift to
# ``u(h)`` is #1789's second, still-open mechanism; the offset substitution must
# leave it exactly as it was.)
LITERAL = _BASE.format(dyn="dyn(h)$(ord(h) > 1).. x(h) =e= x(h-1) + step*(u(h) + u('h3'));")


def _stat_step(tmp_path: Path, source: str) -> str:
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
    return next(line for line in out.read_text().splitlines() if line.startswith("stat_step.."))


def test_LEAD_head_keeps_both_references(tmp_path):
    assert _stat_step(tmp_path, LEAD_HEAD) == (
        "stat_step.. 2 * (step - 1) + sum(h, ((-1) * ((u(h) + u(h+1)) * 0.5)) * nu_dyn(h))"
        " - piL_step =E= 0;"
    )


def test_LAG_head_does_not_generalise_the_boundary_instance(tmp_path):
    assert _stat_step(tmp_path, LAG_HEAD) == (
        "stat_step.. 2 * (step - 1) + sum(h, ((-1) * ((u(h) + u(h-1)) * 0.5)) * nu_dyn(h))"
        " - piL_step =E= 0;"
    )


def test_OWN_INDEX_row_is_unchanged(tmp_path):
    assert _stat_step(tmp_path, OWN_INDEX) == (
        "stat_step.. 2 * (step - 1) + sum(h$(ord(h) > 1), ((-1) * u(h)) * nu_dyn(h))"
        " - piL_step =E= 0;"
    )


def test_a_quoted_LITERAL_is_not_read_as_an_offset(tmp_path):
    # Pinned at main's emit: the offset substitution must not touch it.
    assert _stat_step(tmp_path, LITERAL) == (
        "stat_step.. 2 * (step - 1) + sum(h$(ord(h) > 1), ((-1) * (2 * u(h))) * nu_dyn(h))"
        " - piL_step =E= 0;"
    )

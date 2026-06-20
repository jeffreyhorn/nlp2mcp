"""Acceptance for the embedded-NLP-divergence detector (Sprint 28 Priority 10).

Unit-tests the pure comparison logic (`classify_divergence`) against the
documented pre-fix numbers of the bug class the detector exists to catch — so
the #1378 / #1424 / korcge-#1439 "must SURFACE" acceptance is verified without
reverting the merged fixes or invoking GAMS. The end-to-end GAMS path is
validated separately (korcge hard-diverges live; launch is clean) in the
design's acceptance run.

The detector HARD-FAILS only on unambiguous corruption — a GAMS abort or an
embedded NLP that is infeasible while the reference solves. A bare objective gap
is reported INFORMATIONALLY (``obj_gap``), because for a non-convex model the
warm-started embedded solve may reach a benign different local optimum,
indistinguishable from a real obj corruption without convexity context.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

# The detector lives under scripts/ (not an importable package); load it directly.
_SPEC = importlib.util.spec_from_file_location(
    "check_presolve_divergence",
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "diagnostics"
    / "check_presolve_divergence.py",
)
assert _SPEC and _SPEC.loader
_mod = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_mod)
classify_divergence = _mod.classify_divergence

TOL = 1e-4
OPTIMAL = 2  # GAMS MODEL STATUS: locally optimal


def test_clean_when_embedded_matches_reference() -> None:
    # launch post-#1378: embedded == reference == 2257.7976, solved optimally.
    status, _ = classify_divergence(2257.7976, 2257.7976, OPTIMAL, execerror=False, tol=TOL)
    assert status == "clean"


def test_solver_noise_is_clean() -> None:
    # two solves of the same model agree to ~1e-7 — below the solver tol.
    status, _ = classify_divergence(2257.7976, 2257.7978, OPTIMAL, execerror=False, tol=TOL)
    assert status == "clean"


def test_1378_launch_objective_gap_is_informational() -> None:
    # #1378 pre-fix: self-referential param re-applied → embedded 2604.01 vs 2257.80,
    # but the embedded solve was FEASIBLE (locally optimal). Surfaced as obj_gap
    # (info) — a convex-vs-non-convex distinction the detector can't make alone.
    status, detail = classify_divergence(2257.7976, 2604.01, OPTIMAL, execerror=False, tol=TOL)
    assert status == "obj_gap"
    assert "2604" in detail and "2257" in detail


def test_1424_camshape_infeasible_embedded_hard_diverges() -> None:
    # #1424 pre-fix: blanket subset-defaults → embedded NLP INFEASIBLE (MODEL
    # STATUS 5) while the reference solves → hard divergence.
    status, detail = classify_divergence(4.2841, 5.009, 5, execerror=False, tol=TOL)
    assert status == "diverged"
    assert "MODEL STATUS 5" in detail


def test_korcge_1439_execerror_hard_diverges() -> None:
    # #1439: the embedded $include run aborts (EXECERROR=5) before producing an obj.
    status, detail = classify_divergence(339.213, None, None, execerror=True, tol=TOL)
    assert status == "diverged"
    assert "EXECERROR" in detail


def test_embedded_no_objective_hard_diverges() -> None:
    # reference present + embedded "optimal" but no objective parsed → corruption.
    status, _ = classify_divergence(339.213, None, OPTIMAL, execerror=False, tol=TOL)
    assert status == "diverged"


def test_skipped_when_no_reference() -> None:
    # No usable DB NLP reference (raw NLP did not solve optimally) → can't compare.
    status, _ = classify_divergence(None, 1.0, OPTIMAL, execerror=False, tol=TOL)
    assert status == "skipped"


def test_nonconvex_local_optimum_is_informational() -> None:
    # chain: embedded 6.959 vs reference 5.0723 — a benign different local optimum
    # of a non-convex model, NOT a $onMultiR corruption → obj_gap (info), not fail.
    status, _ = classify_divergence(5.0723, 6.959, OPTIMAL, execerror=False, tol=TOL)
    assert status == "obj_gap"

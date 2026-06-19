"""Acceptance for the embedded-NLP-divergence detector (Sprint 28 Priority 10).

Unit-tests the pure comparison logic (`classify_divergence`) against the
documented pre-fix numbers of the bug class the detector exists to catch — so
the #1378 / #1424 / korcge-#1439 "must FLAG" acceptance is verified without
reverting the merged fixes or invoking GAMS. The end-to-end GAMS path is
validated separately (korcge flags live; launch is clean) in the design's
acceptance run.
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


def test_clean_when_embedded_matches_standalone() -> None:
    # launch post-#1378: embedded == standalone == 2257.7976.
    status, _ = classify_divergence(2257.7976, 2257.7976, execerror=False, tol=TOL)
    assert status == "clean"


def test_solver_noise_is_clean() -> None:
    # two solves of the same model agree to ~1e-6 — below the 1e-4 solver tol.
    status, _ = classify_divergence(2257.7976, 2257.7978, execerror=False, tol=TOL)
    assert status == "clean"


def test_1378_launch_objective_gap_flags() -> None:
    # #1378 pre-fix: self-referential param re-applied → embedded 2604.01 vs 2257.80.
    status, detail = classify_divergence(2257.7976, 2604.01, execerror=False, tol=TOL)
    assert status == "diverged"
    assert "2604" in detail and "2257" in detail


def test_1424_camshape_objective_gap_flags() -> None:
    # #1424 pre-fix: blanket subset-defaults → embedded infeasible (area 5.009) vs 4.2841.
    status, _ = classify_divergence(4.2841, 5.009, execerror=False, tol=TOL)
    assert status == "diverged"


def test_korcge_1439_execerror_flags() -> None:
    # #1439: the embedded $include run aborts (EXECERROR=5) before producing an obj.
    status, detail = classify_divergence(339.213, None, execerror=True, tol=TOL)
    assert status == "diverged"
    assert "EXECERROR" in detail


def test_indeterminate_when_objective_unparsed() -> None:
    status, _ = classify_divergence(None, 1.0, execerror=False, tol=TOL)
    assert status == "indeterminate"

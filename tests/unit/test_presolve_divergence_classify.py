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
import sys
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
# The module mutates global process state on import (sys.path.insert for its own
# `src`/`scripts` imports). Snapshot/restore sys.path so this dynamic load does
# not leak import-resolution order into the rest of the pytest run.
_saved_sys_path = list(sys.path)
try:
    _SPEC.loader.exec_module(_mod)
finally:
    sys.path[:] = _saved_sys_path
classify_divergence = _mod.classify_divergence
demo_refused = _mod.demo_refused
classify_demo_refusal = _mod.classify_demo_refusal

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


def test_a_DEMO_CEILING_refusal_is_recognised_and_is_not_a_divergence() -> None:
    """Sprint 40 Day 8: CI runs the demo, and the licensed-only presolve goldens
    committed on Day 3 abort there with EXECERROR. ``check_model`` classifies a
    listing carrying the demo's refusal line as SKIPPED before the EXECERROR rule,
    which would otherwise hard-fail it as a divergence."""
    refused = (
        "GAMS 54.2.1\n"
        "**** The model exceeds the demo license limits for nonlinear models\n"
        "**** SOLVE from line 900 ABORTED, EXECERROR = 1\n"
    )
    assert demo_refused(refused)
    # Positive control: korcge's genuine $include abort carries no refusal line,
    # so it is NOT skipped and still hard-diverges through classify_divergence.
    korcge = "**** SOLVE from line 412 ABORTED, EXECERROR = 5\n"
    assert not demo_refused(korcge)
    status, _ = classify_divergence(1.0, None, None, execerror=True, tol=TOL)
    assert status == "diverged"
    # The phrase must START the line, as GAMS writes it: not any mention of it.
    assert not demo_refused("* note: The model exceeds the demo license limits\n")


def test_a_demo_refusal_is_ATTRIBUTED_to_the_solve_it_belongs_to() -> None:
    """PR #1791 review: the presolve listing holds the embedded NLP AND the later
    MCP. A refusal of the MCP alone must not hide an embedded NLP that already
    failed (MODEL STATUS 4 against a reference that solves)."""
    refusal = "**** The model exceeds the demo license limits for nonlinear models\n"
    nlp_failed = "**** MODEL STATUS      4 Infeasible\n" + refusal
    status, detail = classify_demo_refusal(nlp_failed, 4, 10.0)
    assert status == "diverged" and "MODEL STATUS 4" in detail
    # The embedded NLP solved; only the MCP was refused -> skipped, not clean.
    nlp_ok = "**** MODEL STATUS      2 Locally Optimal\n" + refusal
    assert classify_demo_refusal(nlp_ok, 2, 10.0)[0] == "skipped"
    # The embedded NLP itself refused (no status before the refusal) -> skipped.
    assert classify_demo_refusal(refusal, None, 10.0)[0] == "skipped"
    # No reference: a failed NLP cannot be called a divergence -> skipped.
    assert classify_demo_refusal(nlp_failed, 4, None)[0] == "skipped"
    # No refusal at all -> None (normal classification).
    assert classify_demo_refusal("**** MODEL STATUS      2 Locally Optimal\n", 2, 10.0) is None

"""Solve-level regression tests for GAMSlib models that match NLP↔MCP.

These tests run the full pipeline (parse → translate → solve → compare) for
models that are known to produce matching objectives, guarding against
regressions.

Requirements:
- GAMS must be installed with PATH solver
- GAMSlib raw files must be present in data/gamslib/raw/
- Tests skip gracefully if either is unavailable
"""

import shutil
import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
GAMSLIB_RAW = PROJECT_ROOT / "data" / "gamslib" / "raw"


def _gams_available() -> bool:
    """Check if GAMS is available on PATH or in known locations."""
    if shutil.which("gams"):
        return True
    for p in [
        "/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams",
        "/Library/Frameworks/GAMS.framework/Versions/Current/Resources/gams",
        "/opt/gams/gams",
        "C:\\GAMS\\win64\\gams.exe",
    ]:
        if Path(p).exists():
            return True
    return False


def _run_pipeline_and_solve(model_id: str) -> float:
    """Run full pipeline for a model and return the MCP objective value.

    Raises pytest.skip if infrastructure is unavailable.
    """
    gms_file = GAMSLIB_RAW / f"{model_id}.gms"
    if not gms_file.exists():
        pytest.skip(f"GAMSlib file not found: {gms_file}")

    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        return _do_pipeline_and_solve(model_id, gms_file)
    finally:
        sys.setrecursionlimit(old_limit)


def _do_pipeline_and_solve(model_id: str, gms_file: Path) -> float:
    """Inner pipeline logic, called with recursion limit already set."""
    from scripts.gamslib.test_solve import solve_mcp
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_file
    from src.kkt.assemble import assemble_kkt_system

    # Parse → Translate
    model = parse_model_file(str(gms_file))
    normalized_eqs, _ = normalize_model(model)
    gradient = compute_objective_gradient(model)
    J_eq, J_ineq = compute_constraint_jacobian(model, normalized_eqs)
    kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)
    mcp_code = emit_gams_mcp(kkt, model_name="mcp_model", add_comments=True)

    # Write to temp file and solve
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".gms", prefix=f"{model_id}_mcp_", delete=False
    ) as f:
        f.write(mcp_code)
        mcp_path = Path(f.name)

    try:
        result = solve_mcp(mcp_path, timeout=120)
    finally:
        mcp_path.unlink(missing_ok=True)

    assert result["status"] == "success", f"MCP solve failed for {model_id}: {result.get('error')}"
    mcp_obj = result["objective_value"]
    assert mcp_obj is not None, f"No objective value from MCP solve for {model_id}"

    return mcp_obj


# Reference NLP objective values from verified convexity checks in gamslib_status.json
_NLP_REFERENCES: dict[str, float] = {
    "ajax": 441003.5953,
    "blend": 4.98,
    "chem": -47.7065,
    "demo1": 1898.52,
    "dispatch": 7.9546,
    "hhmax": 13.9288,
    "himmel11": -30665.5387,
    "house": 4500.0,
    "mathopt2": 0.0,
    "mhw4d": 27.8719,
    "mhw4dx": 27.8719,
    "prodmix": 18666.6667,
    "rbrock": 0.0,
    "splcge": 27.1441,
    "trnsport": 153.675,
    "wall": 1.0,
}

RTOL = 1e-4
ATOL = 1e-8

# MCP objective values for models that solve successfully but don't match
# NLP objectives (MCP-only regression guards).
_MCP_SOLVE_REFERENCES: dict[str, float] = {
    "alkyl": -1.765,
    "circle": 4.071,
    "himmel16": 0.0,
}

skip_no_gams = pytest.mark.skipif(not _gams_available(), reason="GAMS not available")


@pytest.mark.e2e
@skip_no_gams
class TestGamslibMatch:
    """Regression tests for models with verified NLP↔MCP objective match."""

    @pytest.mark.parametrize(
        "model_id",
        sorted(_NLP_REFERENCES.keys()),
    )
    def test_model_match(self, model_id: str):
        """Full pipeline solve + objective match for a GAMSlib model."""
        nlp_obj = _NLP_REFERENCES[model_id]
        mcp_obj = _run_pipeline_and_solve(model_id)

        diff = abs(nlp_obj - mcp_obj)
        max_abs = max(abs(nlp_obj), abs(mcp_obj))
        tolerance = ATOL + RTOL * max_abs

        assert diff <= tolerance, (
            f"{model_id}: objective mismatch — "
            f"NLP={nlp_obj}, MCP={mcp_obj}, diff={diff:.2e}, tol={tolerance:.2e}"
        )


@pytest.mark.e2e
@skip_no_gams
class TestGamslibSolve:
    """Regression tests for models that solve successfully.

    These models produce stable MCP objective values but don't match the
    NLP reference (due to non-convexity, bound handling, or other known
    issues). The tests guard against regressions in the solve pipeline.
    """

    @pytest.mark.parametrize(
        "model_id",
        sorted(_MCP_SOLVE_REFERENCES.keys()),
    )
    def test_model_solve(self, model_id: str):
        """Full pipeline solve + MCP objective stability for a GAMSlib model."""
        expected_obj = _MCP_SOLVE_REFERENCES[model_id]
        mcp_obj = _run_pipeline_and_solve(model_id)

        diff = abs(expected_obj - mcp_obj)
        max_abs = max(abs(expected_obj), abs(mcp_obj))
        tolerance = ATOL + RTOL * max_abs

        assert diff <= tolerance, (
            f"{model_id}: MCP objective changed — "
            f"expected={expected_obj}, got={mcp_obj}, diff={diff:.2e}, tol={tolerance:.2e}"
        )

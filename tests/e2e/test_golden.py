"""
End-to-End Golden Tests

These tests compare the full pipeline output against verified golden reference files.
Golden files are manually reviewed and committed to the repository as the "ground truth"
for correct behavior.

Each test runs the full pipeline (Parse → Normalize → AD → KKT → Emit) and compares
the output against the golden reference, ensuring:
- Deterministic output
- No regressions
- Correct KKT system generation
- Proper handling of all features (bounds, indexed variables, etc.)
"""

import re
from pathlib import Path

import pytest

from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.gradient import compute_objective_gradient
from src.emit.emit_gams import emit_gams_mcp
from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_file
from src.kkt.assemble import assemble_kkt_system


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace for comparison purposes.

    Removes:
    - Leading/trailing whitespace on each line
    - Empty lines
    - Multiple consecutive spaces → single space

    This allows comparison to ignore formatting differences that don't affect semantics.
    """
    lines = []
    for line in text.splitlines():
        # Strip leading/trailing whitespace
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
        # Normalize multiple spaces to single space
        line = re.sub(r"\s+", " ", line)
        lines.append(line)
    return "\n".join(lines)


def run_full_pipeline(input_file: str) -> str:
    """
    Run the full nlp2mcp pipeline on an input file.

    Args:
        input_file: Path to GAMS NLP input file

    Returns:
        Generated GAMS MCP code as string
    """
    # Parse
    model = parse_model_file(input_file)

    # Normalize
    normalize_model(model)

    # Compute derivatives
    gradient = compute_objective_gradient(model)
    J_eq, J_ineq = compute_constraint_jacobian(model)

    # Assemble KKT system
    kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

    # Emit GAMS MCP (full file with headers, comments, etc.)
    output = emit_gams_mcp(kkt, model_name="mcp_model", add_comments=True)

    return output


class TestGoldenFiles:
    """
    Golden file tests - compare pipeline output against verified reference files.

    These tests ensure:
    1. Output matches manually verified golden files
    2. No regressions in pipeline behavior
    3. Deterministic output (same input → same output)
    """

    @pytest.mark.e2e
    def test_simple_nlp_golden(self):
        """Test simple_nlp.gms against golden reference."""
        # Run pipeline
        output = run_full_pipeline("examples/simple_nlp.gms")

        # Load golden reference
        golden_path = Path("tests/golden/simple_nlp_mcp.gms")
        golden = golden_path.read_text()

        # Compare (normalized)
        output_norm = normalize_whitespace(output)
        golden_norm = normalize_whitespace(golden)

        assert output_norm == golden_norm, (
            f"Generated output doesn't match golden reference:\n"
            f"Golden file: {golden_path}\n"
            f"Run 'nlp2mcp examples/simple_nlp.gms' to see actual output"
        )

    @pytest.mark.e2e
    def test_bounds_nlp_golden(self):
        """Test bounds_nlp.gms against golden reference."""
        # Run pipeline
        output = run_full_pipeline("examples/bounds_nlp.gms")

        # Load golden reference
        golden_path = Path("tests/golden/bounds_nlp_mcp.gms")
        golden = golden_path.read_text()

        # Compare (normalized)
        output_norm = normalize_whitespace(output)
        golden_norm = normalize_whitespace(golden)

        assert output_norm == golden_norm, (
            f"Generated output doesn't match golden reference:\n"
            f"Golden file: {golden_path}\n"
            f"Run 'nlp2mcp examples/bounds_nlp.gms' to see actual output"
        )

    @pytest.mark.e2e
    def test_indexed_balance_golden(self):
        """Test indexed_balance.gms against golden reference."""
        # Run pipeline
        output = run_full_pipeline("examples/indexed_balance.gms")

        # Load golden reference
        golden_path = Path("tests/golden/indexed_balance_mcp.gms")
        golden = golden_path.read_text()

        # Compare (normalized)
        output_norm = normalize_whitespace(output)
        golden_norm = normalize_whitespace(golden)

        assert output_norm == golden_norm, (
            f"Generated output doesn't match golden reference:\n"
            f"Golden file: {golden_path}\n"
            f"Run 'nlp2mcp examples/indexed_balance.gms' to see actual output"
        )

    @pytest.mark.e2e
    def test_nonlinear_mix_golden(self):
        """Test nonlinear_mix.gms against golden reference."""
        # Run pipeline
        output = run_full_pipeline("examples/nonlinear_mix.gms")

        # Load golden reference
        golden_path = Path("tests/golden/nonlinear_mix_mcp.gms")
        golden = golden_path.read_text()

        # Compare (normalized)
        output_norm = normalize_whitespace(output)
        golden_norm = normalize_whitespace(golden)

        assert output_norm == golden_norm, (
            f"Generated output doesn't match golden reference:\n"
            f"Golden file: {golden_path}\n"
            f"Run 'nlp2mcp examples/nonlinear_mix.gms' to see actual output"
        )

    @pytest.mark.e2e
    def test_scalar_nlp_golden(self):
        """Test scalar_nlp.gms against golden reference."""
        # Run pipeline
        output = run_full_pipeline("examples/scalar_nlp.gms")

        # Load golden reference
        golden_path = Path("tests/golden/scalar_nlp_mcp.gms")
        golden = golden_path.read_text()

        # Compare (normalized)
        output_norm = normalize_whitespace(output)
        golden_norm = normalize_whitespace(golden)

        assert output_norm == golden_norm, (
            f"Generated output doesn't match golden reference:\n"
            f"Golden file: {golden_path}\n"
            f"Run 'nlp2mcp examples/scalar_nlp.gms' to see actual output"
        )

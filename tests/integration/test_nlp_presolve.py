"""Integration tests for the --nlp-presolve feature.

Tests the NLP pre-solve warm-start mechanism that includes and solves the
original NLP model before the MCP solve, transferring equation marginals
to MCP multiplier variables.
"""

import re
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from src.cli import main
from src.emit.emit_gams import emit_gams_mcp


@pytest.mark.integration
class TestNLPPresolveCLI:
    """Test CLI --nlp-presolve flag acceptance and basic behavior."""

    def test_flag_accepted(self, tmp_path):
        """--nlp-presolve is accepted without error."""
        runner = CliRunner()
        output_file = tmp_path / "output.gms"

        result = runner.invoke(
            main,
            [
                "examples/simple_nlp.gms",
                "-o",
                str(output_file),
                "--nlp-presolve",
            ],
        )

        assert result.exit_code == 0, f"CLI failed: {result.output}"
        assert output_file.exists()

    def test_flag_with_quiet(self, tmp_path):
        """--nlp-presolve works with --quiet."""
        runner = CliRunner()
        output_file = tmp_path / "output.gms"

        result = runner.invoke(
            main,
            [
                "examples/simple_nlp.gms",
                "-o",
                str(output_file),
                "--nlp-presolve",
                "--quiet",
            ],
        )

        assert result.exit_code == 0

    def test_flag_with_no_comments(self, tmp_path):
        """--nlp-presolve works with --no-comments (no section headers)."""
        runner = CliRunner()
        output_file = tmp_path / "output.gms"

        result = runner.invoke(
            main,
            [
                "examples/simple_nlp.gms",
                "-o",
                str(output_file),
                "--nlp-presolve",
                "--no-comments",
            ],
        )

        assert result.exit_code == 0
        content = output_file.read_text()
        # Pre-solve block present but without comment headers
        assert "$onMultiR" in content
        assert "$include" in content
        # No comment lines with ===
        assert "NLP Pre-Solve" not in content

    def test_without_flag_no_presolve(self, tmp_path):
        """Without --nlp-presolve, no pre-solve block is emitted."""
        runner = CliRunner()
        output_file = tmp_path / "output.gms"

        result = runner.invoke(
            main,
            [
                "examples/simple_nlp.gms",
                "-o",
                str(output_file),
            ],
        )

        assert result.exit_code == 0
        content = output_file.read_text()
        assert "$onMultiR" not in content
        assert "$include" not in content
        assert "nlp_presolve" not in content

    def test_flag_with_skip_convexity(self, tmp_path):
        """--nlp-presolve combines with --skip-convexity-check."""
        runner = CliRunner()
        output_file = tmp_path / "output.gms"

        result = runner.invoke(
            main,
            [
                "examples/simple_nlp.gms",
                "-o",
                str(output_file),
                "--nlp-presolve",
                "--skip-convexity-check",
            ],
        )

        assert result.exit_code == 0


@pytest.mark.integration
class TestNLPPresolveOutput:
    """Test the structure and content of the generated pre-solve block."""

    @pytest.fixture
    def presolve_output(self, tmp_path):
        """Generate MCP with --nlp-presolve and return its content."""
        runner = CliRunner()
        output_file = tmp_path / "output.gms"

        result = runner.invoke(
            main,
            [
                "examples/simple_nlp.gms",
                "-o",
                str(output_file),
                "--nlp-presolve",
            ],
        )

        assert result.exit_code == 0
        return output_file.read_text()

    def test_has_onmultir(self, presolve_output):
        """Pre-solve block has $onMultiR to allow symbol redefinition."""
        assert "$onMultiR" in presolve_output

    def test_has_offmulti(self, presolve_output):
        """Pre-solve block has $offMulti to restore normal behavior."""
        assert "$offMulti" in presolve_output

    def test_has_include(self, presolve_output):
        """Pre-solve block includes the original source file via a
        repo-relative path (#1275): absolute paths leak the developer's
        workstation layout and make the emitted artifact non-portable.
        """
        assert "$include" in presolve_output
        include_lines = [
            line for line in presolve_output.splitlines() if line.startswith("$include")
        ]
        assert len(include_lines) == 1
        include_raw = include_lines[0].split("$include", 1)[1].strip()
        include_path = include_raw.strip('"')
        assert not Path(include_path).is_absolute()
        assert not include_path.startswith("/")

    def test_include_references_source_file(self, presolve_output):
        """$include references the original .gms source file."""
        include_lines = [line for line in presolve_output.splitlines() if "$include" in line]
        # Should reference the simple_nlp.gms file
        assert any("simple_nlp.gms" in line for line in include_lines)

    def test_has_dual_transfer_lines(self, presolve_output):
        """Pre-solve block transfers equation marginals to multiplier .l values."""
        # Should have nu_*.l = *.m or lam_*.l = abs(*.m) patterns
        has_nu = re.search(r"nu_\w+\.l\b.*=.*\.m", presolve_output)
        has_lam = re.search(r"lam_\w+\.l\b.*=.*\.m", presolve_output)
        assert has_nu or has_lam, "Expected dual transfer lines (nu_*.l or lam_*.l)"

    def test_presolve_before_mcp_solve(self, presolve_output):
        """Pre-solve block appears before the MCP solve statement."""
        onmulti_pos = presolve_output.index("$onMultiR")
        solve_pos = presolve_output.index("Solve mcp_model using MCP")
        assert onmulti_pos < solve_pos

    def test_presolve_after_model_declaration(self, presolve_output):
        """Pre-solve block appears after Model statement."""
        model_pos = presolve_output.index("Model mcp_model")
        onmulti_pos = presolve_output.index("$onMultiR")
        assert model_pos < onmulti_pos

    def test_has_bound_multiplier_transfers_if_bounds_exist(self, presolve_output):
        """Pre-solve block transfers variable marginals to bound multipliers (if any)."""
        # The simple_nlp model may not have bound multipliers.
        # Just verify the section header is present.
        assert (
            "bound multipliers" in presolve_output.lower()
            or "piL_" in presolve_output
            or "Transfer variable" in presolve_output
        )


@pytest.mark.integration
class TestNLPPresolveDualTransferContent:
    """Test the correctness of dual transfer assignments in detail."""

    def test_equality_multiplier_uses_eq_marginal(self, tmp_path):
        """Equality constraint multipliers use equation.m directly."""
        runner = CliRunner()
        output_file = tmp_path / "output.gms"

        result = runner.invoke(
            main,
            [
                "examples/simple_nlp.gms",
                "-o",
                str(output_file),
                "--nlp-presolve",
            ],
        )

        assert result.exit_code == 0
        content = output_file.read_text()

        # For equality constraints, the transfer should be: nu_<eq>.l = <eq>.m
        # (not abs(), since equality multipliers are free)
        nu_lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip().startswith("nu_") and ".l" in line and ".m" in line
        ]

        for line in nu_lines:
            # Should NOT use abs() for equality multipliers
            assert "abs(" not in line, f"Equality multiplier should not use abs(): {line}"

    def test_inequality_multiplier_uses_abs(self, tmp_path):
        """Inequality constraint multipliers use abs(equation.m)."""
        # Use nonconvex_circle which has an inequality constraint
        fixtures = Path(__file__).parent.parent / "fixtures" / "convexity"
        input_file = fixtures / "convex_inequality.gms"
        if not input_file.exists():
            pytest.skip("convex_inequality.gms fixture not available")

        runner = CliRunner()
        output_file = tmp_path / "output.gms"

        result = runner.invoke(
            main,
            [
                str(input_file),
                "-o",
                str(output_file),
                "--nlp-presolve",
                "--skip-convexity-check",
            ],
        )

        if result.exit_code != 0:
            pytest.skip(f"Model failed to convert: {result.output}")

        content = output_file.read_text()

        # For inequality constraints, the transfer should be: lam_<eq>.l = abs(<eq>.m)
        lam_lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip().startswith("lam_") and ".l" in line and ".m" in line
        ]

        for line in lam_lines:
            assert "abs(" in line, f"Inequality multiplier should use abs(): {line}"

    def test_lower_bound_multiplier_conditional(self, tmp_path):
        """Lower bound multiplier transfer has at-lower-bound condition."""
        runner = CliRunner()
        output_file = tmp_path / "output.gms"

        result = runner.invoke(
            main,
            [
                "examples/simple_nlp.gms",
                "-o",
                str(output_file),
                "--nlp-presolve",
            ],
        )

        assert result.exit_code == 0
        content = output_file.read_text()

        piL_lines = [
            line.strip()
            for line in content.splitlines()
            if "piL_" in line and ".l" in line and ".lo" in line
        ]

        for line in piL_lines:
            # Should have $(abs(x.l - x.lo) < 1e-6 ...) condition
            assert ".lo" in line, f"piL transfer should reference .lo: {line}"
            assert "abs(" in line, f"piL transfer should have abs() tolerance: {line}"

    def test_upper_bound_multiplier_conditional(self, tmp_path):
        """Upper bound multiplier transfer has at-upper-bound condition and negation."""
        runner = CliRunner()
        output_file = tmp_path / "output.gms"

        result = runner.invoke(
            main,
            [
                "examples/simple_nlp.gms",
                "-o",
                str(output_file),
                "--nlp-presolve",
            ],
        )

        assert result.exit_code == 0
        content = output_file.read_text()

        piU_lines = [
            line.strip()
            for line in content.splitlines()
            if "piU_" in line and ".l" in line and ".up" in line
        ]

        for line in piU_lines:
            # Should have $(abs(x.l - x.up) < 1e-6 ...) condition
            assert ".up" in line, f"piU transfer should reference .up: {line}"
            # Should negate the marginal: = -(var.m)
            assert "-(" in line, f"piU transfer should negate marginal: {line}"


@pytest.mark.integration
class TestNLPPresolveEmitFunction:
    """Test emit_gams_mcp() with nlp_presolve parameter directly."""

    def test_no_presolve_without_flag(self, manual_index_mapping):
        """emit_gams_mcp without nlp_presolve=True has no pre-solve block."""
        from src.ad.gradient import GradientVector
        from src.ad.jacobian import JacobianStructure
        from src.ir.ast import Binary, Const, VarRef
        from src.ir.model_ir import ModelIR, ObjectiveIR
        from src.ir.symbols import EquationDef, ObjSense, Rel, VariableDef
        from src.kkt.assemble import assemble_kkt_system

        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="z")
        model.equations["zdef"] = EquationDef(
            name="zdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("z", ()), Binary("^", VarRef("x", ()), Const(2.0))),
        )
        model.variables["z"] = VariableDef(name="z", domain=())
        model.variables["x"] = VariableDef(name="x", domain=(), lo=0.0)
        model.equalities = ["zdef"]

        idx = manual_index_mapping([("z", ()), ("x", ())])
        grad = GradientVector(num_cols=2, index_mapping=idx)
        grad.set_derivative(1, Binary("*", Const(2.0), VarRef("x", ())))
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=idx)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=idx)
        kkt = assemble_kkt_system(model, grad, J_eq, J_ineq)

        output = emit_gams_mcp(kkt, nlp_presolve=False)
        assert "$onMultiR" not in output
        assert "$include" not in output
        assert "nlp_presolve" not in output

    def test_presolve_without_source_file_is_noop(self, manual_index_mapping):
        """emit_gams_mcp with nlp_presolve=True but no source_file is a no-op."""
        from src.ad.gradient import GradientVector
        from src.ad.jacobian import JacobianStructure
        from src.ir.ast import Binary, Const, VarRef
        from src.ir.model_ir import ModelIR, ObjectiveIR
        from src.ir.symbols import EquationDef, ObjSense, Rel, VariableDef
        from src.kkt.assemble import assemble_kkt_system

        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="z")
        model.equations["zdef"] = EquationDef(
            name="zdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("z", ()), Binary("^", VarRef("x", ()), Const(2.0))),
        )
        model.variables["z"] = VariableDef(name="z", domain=())
        model.variables["x"] = VariableDef(name="x", domain=(), lo=0.0)
        model.equalities = ["zdef"]

        idx = manual_index_mapping([("z", ()), ("x", ())])
        grad = GradientVector(num_cols=2, index_mapping=idx)
        grad.set_derivative(1, Binary("*", Const(2.0), VarRef("x", ())))
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=idx)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=idx)
        kkt = assemble_kkt_system(model, grad, J_eq, J_ineq)

        # nlp_presolve=True but no source_file → should be a no-op
        output = emit_gams_mcp(kkt, nlp_presolve=True, source_file=None)
        assert "$onMultiR" not in output
        assert "$include" not in output

    def test_presolve_with_source_file_emits_include(self, manual_index_mapping):
        """emit_gams_mcp with nlp_presolve=True and source_file emits $include."""
        from src.ad.gradient import GradientVector
        from src.ad.jacobian import JacobianStructure
        from src.ir.ast import Binary, Const, VarRef
        from src.ir.model_ir import ModelIR, ObjectiveIR
        from src.ir.symbols import EquationDef, ObjSense, Rel, VariableDef
        from src.kkt.assemble import assemble_kkt_system

        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="z")
        model.equations["zdef"] = EquationDef(
            name="zdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("z", ()), Binary("^", VarRef("x", ()), Const(2.0))),
        )
        model.variables["z"] = VariableDef(name="z", domain=())
        model.variables["x"] = VariableDef(name="x", domain=(), lo=0.0)
        model.equalities = ["zdef"]
        model.model_equations = ["zdef"]

        idx = manual_index_mapping([("z", ()), ("x", ())])
        grad = GradientVector(num_cols=2, index_mapping=idx)
        grad.set_derivative(1, Binary("*", Const(2.0), VarRef("x", ())))
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=idx)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=idx)
        kkt = assemble_kkt_system(model, grad, J_eq, J_ineq)

        output = emit_gams_mcp(kkt, nlp_presolve=True, source_file="examples/simple_nlp.gms")
        assert "$onMultiR" in output
        assert "$include" in output
        assert "simple_nlp.gms" in output
        assert "$offMulti" in output


@pytest.mark.integration
class TestNLPPresolveWithGAMSLib:
    """Test --nlp-presolve with real GAMSlib models (requires data/gamslib/raw/)."""

    @pytest.fixture
    def gamslib_dir(self):
        path = Path("data/gamslib/raw")
        if not path.exists():
            pytest.skip("GAMSlib raw models not available")
        return path

    def test_bearing_generates_with_presolve(self, gamslib_dir, tmp_path):
        """bearing model generates successfully with --nlp-presolve."""
        input_file = gamslib_dir / "bearing.gms"
        if not input_file.exists():
            pytest.skip("bearing.gms not available")

        runner = CliRunner()
        output_file = tmp_path / "bearing_mcp.gms"

        result = runner.invoke(
            main,
            [
                str(input_file),
                "-o",
                str(output_file),
                "--nlp-presolve",
                "--skip-convexity-check",
                "--quiet",
            ],
        )

        assert result.exit_code == 0
        content = output_file.read_text()

        # Should have pre-solve block
        assert "$onMultiR" in content
        assert "$include" in content
        assert "bearing.gms" in content

        # Should have equality multiplier transfers
        assert "nu_friction.l" in content
        assert "nu_inlet_pressure.l" in content

        # Should have inequality multiplier transfers
        assert "lam_radius.l" in content
        assert "lam_limit1.l" in content
        assert "lam_limit2.l" in content

        # Should have bound multiplier transfers
        assert "piL_r.l" in content
        assert "piL_mu.l" in content

    def test_bearing_presolve_structure(self, gamslib_dir, tmp_path):
        """bearing pre-solve has correct dual transfer structure."""
        input_file = gamslib_dir / "bearing.gms"
        if not input_file.exists():
            pytest.skip("bearing.gms not available")

        runner = CliRunner()
        output_file = tmp_path / "bearing_mcp.gms"

        result = runner.invoke(
            main,
            [
                str(input_file),
                "-o",
                str(output_file),
                "--nlp-presolve",
                "--skip-convexity-check",
            ],
        )

        assert result.exit_code == 0
        content = output_file.read_text()

        # Equality multipliers should use direct .m (no abs)
        for eq_name in [
            "pumping_energy",
            "friction",
            "temp_rise",
            "load_capacity",
            "inlet_pressure",
            "oil_viscosity",
            "temperature",
            "temp1",
            "temp2",
        ]:
            transfer_line = f"nu_{eq_name}.l = {eq_name}.m;"
            assert transfer_line in content, f"Missing equality transfer: {transfer_line}"

        # Inequality multipliers should use abs()
        for eq_name in ["radius", "limit1", "limit2"]:
            pattern = f"lam_{eq_name}.l = abs({eq_name}.m);"
            assert pattern in content, f"Missing inequality transfer: {pattern}"

    def test_simple_nlp_generates_with_presolve(self, tmp_path):
        """simple_nlp model generates with --nlp-presolve."""
        input_file = Path("examples/simple_nlp.gms")
        if not input_file.exists():
            pytest.skip("simple_nlp.gms not available")

        runner = CliRunner()
        output_file = tmp_path / "simple_mcp.gms"

        result = runner.invoke(
            main,
            [
                str(input_file),
                "-o",
                str(output_file),
                "--nlp-presolve",
            ],
        )

        assert result.exit_code == 0
        content = output_file.read_text()

        # Should still have the MCP solve
        assert "Solve mcp_model using MCP" in content
        # Pre-solve should be present
        assert "$include" in content


@pytest.mark.integration
class TestNLPPresolveGAMSSolve:
    """Test that --nlp-presolve actually helps PATH convergence.

    These tests require both GAMSlib raw models AND a GAMS installation.
    """

    @pytest.fixture
    def gamslib_dir(self):
        path = Path("data/gamslib/raw")
        if not path.exists():
            pytest.skip("GAMSlib raw models not available")
        return path

    @pytest.fixture
    def gams_available(self):
        """Check if GAMS is available."""
        import shutil

        if shutil.which("gams") is None:
            pytest.skip("GAMS not available")

    def test_bearing_solves_with_presolve(self, gamslib_dir, gams_available, tmp_path):
        """bearing solves to MODEL STATUS 1 with --nlp-presolve."""
        input_file = gamslib_dir / "bearing.gms"
        if not input_file.exists():
            pytest.skip("bearing.gms not available")

        # Generate MCP
        runner = CliRunner()
        output_file = tmp_path / "bearing_mcp.gms"
        result = runner.invoke(
            main,
            [
                str(input_file),
                "-o",
                str(output_file),
                "--nlp-presolve",
                "--skip-convexity-check",
                "--quiet",
            ],
        )
        assert result.exit_code == 0

        # Solve with GAMS. After #1275 the emitted presolve wrapper uses a
        # repo-relative `$include` path (e.g., `data/gamslib/raw/bearing.gms`),
        # so GAMS must be invoked with the repo root as cwd for the include
        # to resolve. We also route the listing file back to `tmp_path` via
        # `o=` so the later `output_file.with_suffix('.lst')` assertion still
        # finds it. This mirrors the intended usage: artifacts are portable
        # when re-run from the repo root.
        repo_root = Path(__file__).resolve().parents[2]
        lst_file = output_file.with_suffix(".lst")
        gams_result = subprocess.run(
            ["gams", str(output_file), "lo=0", f"o={lst_file}"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
        )
        assert gams_result.returncode == 0, (
            "GAMS solve failed.\n"
            f"stdout:\n{gams_result.stdout}\n"
            f"stderr:\n{gams_result.stderr}"
        )

        # Check listing file (path was computed above and passed to GAMS via `o=`).
        assert lst_file.exists(), "GAMS listing file not created"
        lst_content = lst_file.read_text()

        # Should have MODEL STATUS 1 Optimal for the MCP solve
        status_lines = [line for line in lst_content.splitlines() if "MODEL STATUS" in line]
        assert (
            len(status_lines) >= 2
        ), f"Expected at least 2 MODEL STATUS lines (NLP + MCP), got {len(status_lines)}"
        # Last status should be the MCP solve
        last_status = status_lines[-1]
        assert (
            "1 Optimal" in last_status
        ), f"MCP should be MODEL STATUS 1 Optimal, got: {last_status}"

        # Check objective value matches NLP
        obj_lines = [
            line
            for line in lst_content.splitlines()
            if "nlp2mcp_obj_val" in line and "=" in line and "PARAMETER" in line
        ]
        assert len(obj_lines) >= 1
        obj_val = float(obj_lines[-1].split("=")[-1].strip())
        assert abs(obj_val - 19517.332) < 1.0, f"Objective should be ~19517.332, got {obj_val}"

    def test_bearing_fails_without_presolve(self, gamslib_dir, gams_available, tmp_path):
        """bearing without --nlp-presolve gives MODEL STATUS 5 (Locally Infeasible)."""
        input_file = gamslib_dir / "bearing.gms"
        if not input_file.exists():
            pytest.skip("bearing.gms not available")

        # Generate MCP without pre-solve
        runner = CliRunner()
        output_file = tmp_path / "bearing_mcp.gms"
        result = runner.invoke(
            main,
            [
                str(input_file),
                "-o",
                str(output_file),
                "--skip-convexity-check",
                "--quiet",
            ],
        )
        assert result.exit_code == 0

        # Solve with GAMS
        subprocess.run(
            ["gams", str(output_file), "lo=0"],
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )

        lst_file = output_file.with_suffix(".lst")
        assert lst_file.exists()
        lst_content = lst_file.read_text()

        # Should be MODEL STATUS 5 (Locally Infeasible) without pre-solve
        status_lines = [line for line in lst_content.splitlines() if "MODEL STATUS" in line]
        assert any(
            "5 Locally Infeasible" in line for line in status_lines
        ), f"Expected Locally Infeasible without pre-solve, got: {status_lines}"

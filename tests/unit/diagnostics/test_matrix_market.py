"""Tests for Matrix Market export functionality."""

import tempfile
from pathlib import Path

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.diagnostics.matrix_market import (
    export_constraint_jacobian_matrix_market,
    export_jacobian_matrix_market,
)
from src.ir.ast import Const
from src.ir.model_ir import ModelIR
from src.kkt.kkt_system import KKTSystem


class TestMatrixMarketExport:
    """Test Matrix Market format export."""

    def test_export_simple_jacobian(self):
        """Test exporting a simple constraint Jacobian."""
        # Create 2x2 Jacobian with 3 nonzeros
        jacobian = JacobianStructure(num_rows=2, num_cols=2)
        jacobian.set_derivative(0, 0, Const(1.0))
        jacobian.set_derivative(0, 1, Const(2.0))
        jacobian.set_derivative(1, 1, Const(3.0))

        with tempfile.NamedTemporaryFile(mode="w", suffix=".mtx", delete=False) as f:
            temp_path = Path(f.name)

        try:
            export_constraint_jacobian_matrix_market(jacobian, temp_path)

            content = temp_path.read_text()

            # Check header
            assert "%%MatrixMarket matrix coordinate real general" in content
            assert "Constraint Jacobian from nlp2mcp" in content

            # Check dimensions line (1-based indexing)
            lines = content.strip().split("\n")
            dims_line = None
            for line in lines:
                if not line.startswith("%"):
                    dims_line = line
                    break

            assert dims_line is not None
            parts = dims_line.split()
            assert parts == ["2", "2", "3"]  # 2 rows, 2 cols, 3 nonzeros

            # Check entries (1-based indexing, sorted by row then col)
            data_lines = [line for line in lines if not line.startswith("%") and line.strip()][1:]
            assert len(data_lines) == 3

            # Entries should be (row, col, value)
            assert data_lines[0].split() == ["1", "1", "1.0"]
            assert data_lines[1].split() == ["1", "2", "1.0"]
            assert data_lines[2].split() == ["2", "2", "1.0"]

        finally:
            temp_path.unlink()

    def test_export_combined_jacobian(self):
        """Test exporting combined equality and inequality Jacobians."""
        model = ModelIR()
        gradient = GradientVector(num_cols=2)

        # Equality Jacobian: 1x2
        J_eq = JacobianStructure(num_rows=1, num_cols=2)
        J_eq.set_derivative(0, 0, Const(1.0))

        # Inequality Jacobian: 2x2
        J_ineq = JacobianStructure(num_rows=2, num_cols=2)
        J_ineq.set_derivative(0, 1, Const(1.0))
        J_ineq.set_derivative(1, 0, Const(1.0))

        kkt = KKTSystem(
            model_ir=model,
            gradient=gradient,
            J_eq=J_eq,
            J_ineq=J_ineq,
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".mtx", delete=False) as f:
            temp_path = Path(f.name)

        try:
            export_jacobian_matrix_market(kkt, temp_path)

            content = temp_path.read_text()

            # Check header
            assert "%%MatrixMarket matrix coordinate real general" in content
            assert "KKT Jacobian from nlp2mcp" in content

            lines = content.strip().split("\n")
            dims_line = None
            for line in lines:
                if not line.startswith("%"):
                    dims_line = line
                    break

            assert dims_line is not None
            parts = dims_line.split()
            # Total rows = J_eq rows + J_ineq rows = 1 + 2 = 3
            # Total cols = max(J_eq cols, J_ineq cols) = 2
            # Total nonzeros = 1 (J_eq) + 2 (J_ineq) = 3
            assert parts == ["3", "2", "3"]

            # Check entries
            data_lines = [line for line in lines if not line.startswith("%") and line.strip()][1:]
            assert len(data_lines) == 3

            # J_eq entry: row 1 (0+1), col 1 (0+1)
            assert data_lines[0].split() == ["1", "1", "1.0"]

            # J_ineq entries: rows offset by 1
            # (0, 1) -> (1+1, 1+1) = (2, 2)
            assert data_lines[1].split() == ["2", "2", "1.0"]
            # (1, 0) -> (1+1+1, 0+1) = (3, 1)
            assert data_lines[2].split() == ["3", "1", "1.0"]

        finally:
            temp_path.unlink()

    def test_export_empty_jacobian(self):
        """Test exporting empty Jacobian."""
        jacobian = JacobianStructure(num_rows=0, num_cols=0)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".mtx", delete=False) as f:
            temp_path = Path(f.name)

        try:
            export_constraint_jacobian_matrix_market(jacobian, temp_path)

            content = temp_path.read_text()

            # Check dimensions
            lines = content.strip().split("\n")
            dims_line = None
            for line in lines:
                if not line.startswith("%"):
                    dims_line = line
                    break

            assert dims_line is not None
            parts = dims_line.split()
            assert parts == ["0", "0", "0"]

        finally:
            temp_path.unlink()

    def test_export_sparse_jacobian(self):
        """Test exporting sparse Jacobian (many zeros)."""
        # Create 10x10 Jacobian with only 5 nonzeros
        jacobian = JacobianStructure(num_rows=10, num_cols=10)
        jacobian.set_derivative(0, 0, Const(1.0))
        jacobian.set_derivative(2, 4, Const(1.0))
        jacobian.set_derivative(5, 5, Const(1.0))
        jacobian.set_derivative(7, 2, Const(1.0))
        jacobian.set_derivative(9, 9, Const(1.0))

        with tempfile.NamedTemporaryFile(mode="w", suffix=".mtx", delete=False) as f:
            temp_path = Path(f.name)

        try:
            export_constraint_jacobian_matrix_market(jacobian, temp_path)

            content = temp_path.read_text()

            lines = content.strip().split("\n")
            dims_line = None
            for line in lines:
                if not line.startswith("%"):
                    dims_line = line
                    break

            parts = dims_line.split()
            assert parts == ["10", "10", "5"]  # Sparse: 5 out of 100 entries

            # Check data lines
            data_lines = [line for line in lines if not line.startswith("%") and line.strip()][1:]
            assert len(data_lines) == 5

        finally:
            temp_path.unlink()

    def test_file_path_as_string(self):
        """Test that export accepts string paths."""
        jacobian = JacobianStructure(num_rows=1, num_cols=1)
        jacobian.set_derivative(0, 0, Const(1.0))

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = str(Path(tmpdir) / "test.mtx")

            export_constraint_jacobian_matrix_market(jacobian, temp_path)

            assert Path(temp_path).exists()
            content = Path(temp_path).read_text()
            assert "%%MatrixMarket" in content

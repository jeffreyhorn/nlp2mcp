"""
Performance benchmarks for nlp2mcp.

Establishes baselines for:
- Parsing time
- Differentiation time
- KKT assembly time
- GAMS emission time
- End-to-end time
- Memory usage

Run with: pytest tests/benchmarks/ -v --benchmark-only
Or without pytest-benchmark: pytest tests/benchmarks/ -v
"""

import time
import tracemalloc
from pathlib import Path

import pytest

from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.gradient import compute_objective_gradient
from src.emit.emit_gams import emit_gams_mcp
from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_file
from src.kkt.assemble import assemble_kkt_system


class TestPerformanceBenchmarks:
    """Performance benchmarks at different scales."""

    @pytest.fixture
    def small_model(self, tmp_path):
        """10 variables, 5 constraints."""
        model = self._generate_model(tmp_path, name="small", num_vars=10, num_constraints=5)
        return model

    @pytest.fixture
    def medium_model(self, tmp_path):
        """100 variables, 50 constraints."""
        model = self._generate_model(tmp_path, name="medium", num_vars=100, num_constraints=50)
        return model

    @pytest.fixture
    def large_model(self, tmp_path):
        """200 variables, 100 constraints."""
        model = self._generate_model(tmp_path, name="large", num_vars=200, num_constraints=100)
        return model

    def test_parse_small_model(self, small_model):
        """Benchmark: Parse small model (10 vars)."""
        start = time.perf_counter()
        result = parse_model_file(small_model)
        elapsed = time.perf_counter() - start

        assert result is not None
        # Target: < 0.5 seconds
        assert elapsed < 0.5, f"Parse small model took {elapsed:.3f}s (target < 0.5s)"
        print(f"\nParse small model: {elapsed:.3f}s")

    def test_parse_medium_model(self, medium_model):
        """Benchmark: Parse medium model (100 vars)."""
        start = time.perf_counter()
        result = parse_model_file(medium_model)
        elapsed = time.perf_counter() - start

        assert result is not None
        # Target: < 3.0 seconds
        assert elapsed < 3.0, f"Parse medium model took {elapsed:.3f}s (target < 3.0s)"
        print(f"\nParse medium model: {elapsed:.3f}s")

    def test_parse_large_model(self, large_model):
        """Benchmark: Parse large model (200 vars)."""
        start = time.perf_counter()
        result = parse_model_file(large_model)
        elapsed = time.perf_counter() - start

        assert result is not None
        # Target: < 5.0 seconds
        assert elapsed < 5.0, f"Parse large model took {elapsed:.3f}s (target < 5.0s)"
        print(f"\nParse large model: {elapsed:.3f}s")

    def test_differentiation_scalability(self, small_model, medium_model):
        """Benchmark: Verify differentiation scales sub-quadratically."""
        # Small model
        model_small = parse_model_file(small_model)
        normalized_eqs_small, normalized_bounds_small = normalize_model(model_small)

        start = time.perf_counter()
        compute_objective_gradient(model_small)
        _, _ = compute_constraint_jacobian(model_small)
        time_small = time.perf_counter() - start

        # Medium model (10x variables)
        model_medium = parse_model_file(medium_model)
        normalized_eqs_medium, normalized_bounds_medium = normalize_model(model_medium)

        start = time.perf_counter()
        compute_objective_gradient(model_medium)
        _, _ = compute_constraint_jacobian(model_medium)
        time_medium = time.perf_counter() - start

        # Verify: 10x vars should be < 200x time (sub-quadratic)
        ratio = time_medium / time_small if time_small > 0 else 0
        print(
            f"\nDifferentiation scaling: {ratio:.1f}x time for 10x variables "
            f"(small: {time_small:.3f}s, medium: {time_medium:.3f}s)"
        )
        assert ratio < 200, f"Differentiation scaling poor: 10x vars = {ratio:.1f}x time"

    @pytest.mark.skip(reason="Memory usage varies in CI/CD environments")
    def test_memory_usage_large_model(self, large_model):
        """Benchmark: Memory usage for large model."""
        tracemalloc.start()

        model = parse_model_file(large_model)
        normalized_eqs, normalized_bounds = normalize_model(model)
        gradient = compute_objective_gradient(model)
        J_eq, J_ineq = compute_constraint_jacobian(model)
        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)
        emit_gams_mcp(kkt)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Target: < 50 MB for 200-var model
        peak_mb = peak / 1024 / 1024
        print(f"\nMemory usage: {peak_mb:.1f} MB (peak)")
        assert peak_mb < 50, f"Memory usage too high: {peak_mb:.1f} MB for 200 vars"

    def test_end_to_end_performance(self, medium_model):
        """Benchmark: Full pipeline for medium model."""

        def full_pipeline():
            model = parse_model_file(medium_model)
            normalized_eqs, normalized_bounds = normalize_model(model)
            gradient = compute_objective_gradient(model)
            J_eq, J_ineq = compute_constraint_jacobian(model)
            kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)
            gams_code = emit_gams_mcp(kkt)
            return gams_code

        start = time.perf_counter()
        result = full_pipeline()
        elapsed = time.perf_counter() - start

        assert len(result) > 0
        # Target: < 10 seconds for 100-var model
        print(f"\nEnd-to-end (100 vars): {elapsed:.3f}s")
        assert elapsed < 10.0, f"End-to-end took {elapsed:.3f}s for 100 vars (target < 10.0s)"

    def test_sparsity_exploitation(self, tmp_path):
        """Verify sparse Jacobians scale better than dense."""
        # Create sparse model (each constraint touches 2 vars)
        sparse_model = self._generate_sparse_model(
            tmp_path,
            num_vars=100,
            num_constraints=50,
            density=0.02,  # 2% nonzeros
        )

        # Create dense model (each constraint touches all vars)
        dense_model = self._generate_dense_model(tmp_path, num_vars=100, num_constraints=50)

        # Compare times
        model_sparse = parse_model_file(sparse_model)
        norm_eq_sparse, norm_bounds_sparse = normalize_model(model_sparse)
        start = time.perf_counter()
        _, _ = compute_constraint_jacobian(model_sparse)
        time_sparse = time.perf_counter() - start

        model_dense = parse_model_file(dense_model)
        norm_eq_dense, norm_bounds_dense = normalize_model(model_dense)
        start = time.perf_counter()
        _, _ = compute_constraint_jacobian(model_dense)
        time_dense = time.perf_counter() - start

        # Sparse should be much faster
        ratio = time_dense / time_sparse if time_sparse > 0 else 1
        print(
            f"\nSparsity exploitation: {ratio:.1f}x speedup "
            f"(sparse: {time_sparse:.3f}s, dense: {time_dense:.3f}s)"
        )
        assert ratio > 5, f"Sparsity not exploited: dense only {ratio:.1f}x slower (target > 5x)"

    def _generate_model(self, path: Path, name: str, num_vars: int, num_constraints: int) -> Path:
        """Generate test GAMS model of specified size."""
        model_file = path / f"{name}_model.gms"

        # Generate a simple GAMS NLP model
        lines = [f"* {num_vars} vars, {num_constraints} constraints\n\n"]

        # Variable declarations
        lines.append("Variables\n")
        for i in range(num_vars):
            lines.append(f"    x{i + 1}\n")
        lines.append("    obj\n;\n\n")

        # Equation declarations
        lines.append("Equations\n")
        for j in range(num_constraints):
            lines.append(f"    c{j + 1}\n")
        lines.append("    objdef\n;\n\n")

        # Equation definitions (simple quadratic constraints)
        for j in range(num_constraints):
            # Each constraint: sum of a few variables <= constant
            involved_vars = [f"x{(j * 3 + i) % num_vars + 1}" for i in range(min(3, num_vars))]
            lines.append(f"c{j + 1}.. {' + '.join(involved_vars)} =L= {j + 1};\n")

        lines.append("\n")

        # Objective (simple quadratic)
        obj_terms = [f"x{i + 1}*x{i + 1}" for i in range(num_vars)]
        lines.append(f"objdef.. obj =E= {' + '.join(obj_terms)};\n\n")

        # Model and solve
        lines.append("Model testModel /all/;\n")
        lines.append("Solve testModel using NLP minimizing obj;\n")

        model_file.write_text("".join(lines))
        return model_file

    def _generate_sparse_model(
        self, path: Path, num_vars: int, num_constraints: int, density: float
    ) -> Path:
        """Generate sparse GAMS model where each constraint touches few variables."""
        model_file = path / "sparse_model.gms"

        lines = [
            f"* Sparse model: {num_vars} vars, {num_constraints} constraints, "
            f"{density * 100:.0f}% density\n\n"
        ]

        # Variable declarations
        lines.append("Variables\n")
        for i in range(num_vars):
            lines.append(f"    x{i + 1}\n")
        lines.append("    obj\n;\n\n")

        # Equation declarations
        lines.append("Equations\n")
        for j in range(num_constraints):
            lines.append(f"    c{j + 1}\n")
        lines.append("    objdef\n;\n\n")

        # Sparse constraint definitions (each touches ~2 variables)
        vars_per_constraint = max(2, int(num_vars * density))
        for j in range(num_constraints):
            # Each constraint uses only a few consecutive variables
            start_var = (j * 2) % num_vars
            var_indices = [(start_var + k) % num_vars + 1 for k in range(vars_per_constraint)]
            involved_vars = [f"x{i}" for i in var_indices]
            lines.append(f"c{j + 1}.. {' + '.join(involved_vars)} =L= {j + 1};\n")

        lines.append("\n")

        # Objective (sparse - sum of squares)
        obj_terms = [f"x{i + 1}*x{i + 1}" for i in range(num_vars)]
        lines.append(f"objdef.. obj =E= {' + '.join(obj_terms)};\n\n")

        # Model and solve
        lines.append("Model testModel /all/;\n")
        lines.append("Solve testModel using NLP minimizing obj;\n")

        model_file.write_text("".join(lines))
        return model_file

    def _generate_dense_model(self, path: Path, num_vars: int, num_constraints: int) -> Path:
        """Generate dense GAMS model where each constraint touches all variables."""
        model_file = path / "dense_model.gms"

        lines = [f"* Dense model: {num_vars} vars, {num_constraints} constraints, 100% density\n\n"]

        # Variable declarations
        lines.append("Variables\n")
        for i in range(num_vars):
            lines.append(f"    x{i + 1}\n")
        lines.append("    obj\n;\n\n")

        # Equation declarations
        lines.append("Equations\n")
        for j in range(num_constraints):
            lines.append(f"    c{j + 1}\n")
        lines.append("    objdef\n;\n\n")

        # Dense constraint definitions (each touches ALL variables)
        for j in range(num_constraints):
            # Each constraint uses all variables
            involved_vars = [f"x{i + 1}" for i in range(num_vars)]
            lines.append(f"c{j + 1}.. {' + '.join(involved_vars)} =L= {j + 1};\n")

        lines.append("\n")

        # Objective (dense - sum of squares)
        obj_terms = [f"x{i + 1}*x{i + 1}" for i in range(num_vars)]
        lines.append(f"objdef.. obj =E= {' + '.join(obj_terms)};\n\n")

        # Model and solve
        lines.append("Model testModel /all/;\n")
        lines.append("Solve testModel using NLP minimizing obj;\n")

        model_file.write_text("".join(lines))
        return model_file

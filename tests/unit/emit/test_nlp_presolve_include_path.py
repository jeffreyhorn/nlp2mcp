"""Unit tests for #1275: `$include` path portability in `_emit_nlp_presolve`.

Emits an MCP with `nlp_presolve=True` against a synthetic model, then asserts
the emitted `$include` directive is:
  - repo-relative when the source file lives under the repo root, and
  - commented out + accompanied by a `UserWarning` when the source is
    outside the repo root (the artifact is then self-documenting about why
    it can't be re-run verbatim).

Running the emitter end-to-end (rather than unit-testing a private helper)
keeps the test resilient to internal refactors; the contract asserted here
is the surface the issue report cares about (the text of the `$include`
line in `<model>_mcp_presolve.gms`).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.emit.emit_gams import emit_gams_mcp
from src.ir.ast import Binary, Const, VarRef
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import EquationDef, ObjSense, Rel, VariableDef
from src.kkt.assemble import assemble_kkt_system

REPO_ROOT = Path(__file__).resolve().parents[3]


def _toy_kkt(manual_index_mapping):
    """Minimal 1-variable / 1-equation KKT system for presolve emission.

    Mirrors the fixture used elsewhere in `test_nlp_presolve.py`; kept local
    so this file has no cross-module dependency on that test's helpers.
    """
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
    return assemble_kkt_system(model, grad, J_eq, J_ineq)


def _extract_include_line(output: str) -> str:
    """Return the single non-commented `$include` line from the emitter output."""
    lines = [line for line in output.splitlines() if line.startswith("$include")]
    assert len(lines) == 1, f"expected exactly one $include line, got {lines!r}"
    return lines[0]


class TestIncludePathPortability:
    """#1275: emitted `$include` must not leak the developer's workstation path."""

    def test_in_repo_source_emits_relative_path(self, manual_index_mapping):
        """Source under the repo root → `$include "data/gamslib/raw/..."`."""
        kkt = _toy_kkt(manual_index_mapping)
        in_repo_source = REPO_ROOT / "examples" / "simple_nlp.gms"

        output = emit_gams_mcp(kkt, nlp_presolve=True, source_file=str(in_repo_source))

        include_line = _extract_include_line(output)
        raw = include_line.split("$include", 1)[1].strip().strip('"')
        assert not Path(raw).is_absolute()
        assert raw == "examples/simple_nlp.gms"

    def test_in_repo_source_always_forward_slashes(self, manual_index_mapping):
        """The emitted path uses POSIX separators even on Windows runners."""
        kkt = _toy_kkt(manual_index_mapping)
        source = REPO_ROOT / "examples" / "simple_nlp.gms"

        output = emit_gams_mcp(kkt, nlp_presolve=True, source_file=str(source))

        include_line = _extract_include_line(output)
        assert "\\" not in include_line

    def test_out_of_repo_source_emits_commented_include_with_warning(
        self, tmp_path, manual_index_mapping
    ):
        """Source outside repo root → commented `*$include ...` + UserWarning.

        The test uses `tmp_path` as the fake-external source location —
        `tmp_path` is a pytest-guaranteed directory that is NOT under the
        repo root, so it exercises the portability-reject branch without
        depending on any specific OS layout.
        """
        kkt = _toy_kkt(manual_index_mapping)
        external_source = tmp_path / "external_model.gms"
        external_source.write_text("* stub file\n")

        with pytest.warns(UserWarning, match="outside the repo root"):
            output = emit_gams_mcp(kkt, nlp_presolve=True, source_file=str(external_source))

        active_lines = [line for line in output.splitlines() if line.startswith("$include")]
        assert (
            active_lines == []
        ), f"expected no active $include for out-of-repo source, got {active_lines!r}"
        commented = [line for line in output.splitlines() if line.startswith("*$include")]
        assert len(commented) == 1
        # The emitter writes the absolute path via `Path.as_posix()`, which on
        # Windows produces `C:/...` while `str(Path(...))` produces `C:\...`.
        # Compare against the POSIX form on both sides so this test passes on
        # Linux/macOS runners *and* Windows.
        assert external_source.resolve().as_posix() in commented[0]

    def test_includes_onmulti_directive_regardless_of_path_branch(
        self, tmp_path, manual_index_mapping
    ):
        """Both the in-repo and out-of-repo paths preserve the $onMultiR /
        $offMulti bookends (needed so the pre-solve block doesn't conflict
        with the MCP's own symbol declarations).
        """
        kkt = _toy_kkt(manual_index_mapping)
        external_source = tmp_path / "external_model.gms"
        external_source.write_text("* stub file\n")

        with pytest.warns(UserWarning):
            out_external = emit_gams_mcp(kkt, nlp_presolve=True, source_file=str(external_source))
        out_in_repo = emit_gams_mcp(
            kkt,
            nlp_presolve=True,
            source_file=str(REPO_ROOT / "examples" / "simple_nlp.gms"),
        )

        for out in (out_external, out_in_repo):
            assert "$onMultiR" in out
            assert "$offMulti" in out

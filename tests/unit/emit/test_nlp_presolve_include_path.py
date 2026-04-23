"""Unit tests for #1275: `$include` path portability in `_emit_nlp_presolve`.

Emits an MCP with `nlp_presolve=True` against a synthetic model, then asserts:
  - the emitted `$include` is repo-relative when the source lives under the
    repo root, and
  - when the source is outside the repo root, the runnable pre-solve
    content ($onMultiR/$offMulti bookends, $include, dual transfers) is
    skipped and replaced with a short `*`-commented banner explaining the
    omission. A `UserWarning` fires in parallel. Skipping the runnable
    block is necessary because the dual-transfer assignments reference
    original equation names that only come into scope via the `$include`;
    emitting them without a working include would produce a `.gms` that
    won't compile.

Running the emitter end-to-end (rather than unit-testing a private helper)
keeps the test resilient to internal refactors; the contract asserted here
is the surface the issue report cares about (the text of the `$include`
line — or its absence — in `<model>_mcp_presolve.gms`).
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

    def test_out_of_repo_source_skips_presolve_entirely_with_warning(
        self, tmp_path, manual_index_mapping
    ):
        """Source outside repo root → NO runnable pre-solve content +
        self-documenting commented banner + UserWarning.

        The earlier draft commented out the `$include` but still emitted the
        dual-transfer assignments. Those transfers reference original NLP
        equation names that only come into scope via the `$include`, so the
        resulting artifact wouldn't compile in GAMS without manual edits.
        The emitter now takes the stricter "skip the whole warm-start"
        branch — the MCP itself remains runnable, and a short `*`-commented
        banner in the emitted file explains why the warm-start was dropped
        (so a downstream reader of `<model>_mcp_presolve.gms` doesn't have
        to cross-reference the Python warning).

        `tmp_path` is a pytest-guaranteed directory outside the repo, so it
        exercises the reject branch without depending on any OS layout.
        """
        kkt = _toy_kkt(manual_index_mapping)
        external_source = tmp_path / "external_model.gms"
        external_source.write_text("* stub file\n")

        with pytest.warns(UserWarning, match="outside the repo root"):
            output = emit_gams_mcp(kkt, nlp_presolve=True, source_file=str(external_source))

        # No runnable pre-solve content: no $include line (active OR
        # commented), no $onMultiR/$offMulti bookends, and (crucially) no
        # warm-start banner or dual-transfer assignments that would reference
        # undeclared equation names.
        #
        # Line-prefix checks avoid false positives from the explanatory
        # banner (which mentions `$include` as prose) and from any hypothetical
        # substring matches elsewhere in the emitted GAMS.
        output_lines = output.splitlines()
        for line in output_lines:
            stripped = line.lstrip()
            assert not stripped.startswith("$include"), (
                f"expected no active $include line when source is outside "
                f"repo root, got: {line!r}"
            )
            assert not stripped.startswith(
                "*$include"
            ), f"expected no commented $include line, got: {line!r}"
        for needle in ("$onMultiR", "$offMulti", "NLP Pre-Solve (warm-start for MCP duals)"):
            assert (
                needle not in output
            ), f"expected no {needle!r} when source is outside repo root, got:\n{output}"

        # But the emitted file DOES contain a short `*`-commented banner
        # explaining why the pre-solve block was omitted, so the artifact
        # remains self-documenting.
        assert "NLP Pre-Solve omitted" in output
        assert "outside the repo root" in output
        assert "#1275" in output

    def test_in_repo_source_includes_onmulti_bookends(self, manual_index_mapping):
        """In-repo sources get the `$onMultiR` / `$offMulti` bookends around
        the `$include`. These are needed so the pre-solve block can redefine
        MCP symbols without conflict.
        """
        kkt = _toy_kkt(manual_index_mapping)
        source = REPO_ROOT / "examples" / "simple_nlp.gms"

        output = emit_gams_mcp(kkt, nlp_presolve=True, source_file=str(source))

        assert "$onMultiR" in output
        assert "$offMulti" in output

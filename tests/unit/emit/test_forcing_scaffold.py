"""Sprint 30 P8: solution-forcing scaffold (``--force <strategy>``) tests.

The scaffold wraps the terminal ``Solve <model> using MCP;`` in a forcing driver
(homotopy / multistart / optfile) + a MODEL-STATUS reporter — the stable interface
the Sprint-31 PATH-consultation work inherits. These tests guard: (a) each driver's
structure + the reporter, (b) the ``none`` default leaves the plain solve untouched,
(c) validation, and (d) the Config field validation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.gradient import compute_objective_gradient
from src.config import Config
from src.emit.emit_gams import emit_gams_mcp
from src.emit.forcing import FORCING_STRATEGIES, emit_forcing_scaffold
from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_file
from src.kkt.assemble import assemble_kkt_system
from src.kkt.reformulation import reformulate_model

pytestmark = pytest.mark.unit

_FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "crossterm_shapes"
    / "shape1_single_axis_offset.gms"
)


def _emit_with_force(strategy: str) -> str:
    """Emit a small fixture's MCP with ``config.force_strategy = strategy``."""
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        model = parse_model_file(str(_FIXTURE))
        reformulate_model(model)
        normalized_eqs, _ = normalize_model(model)
        cfg = Config(force_strategy=strategy)
        gradient = compute_objective_gradient(model, cfg)
        j_eq, j_ineq = compute_constraint_jacobian(model, normalized_eqs, cfg)
        return emit_gams_mcp(assemble_kkt_system(model, gradient, j_eq, j_ineq, cfg), config=cfg)
    finally:
        sys.setrecursionlimit(old)


class TestEmitForcingScaffold:
    def test_optfile_emits_pathopt_and_reporter(self):
        out = emit_forcing_scaffold("optfile", "mcp_model")
        assert "$onecho > path.opt" in out
        assert "proximal_perturbation 1e-2" in out
        assert "merit_function normal" in out
        # PATH is forced so the emitted path.opt is actually applied
        assert "option mcp = path;" in out
        assert "mcp_model.optfile = 1;" in out
        assert "Solve mcp_model using MCP;" in out
        # MODEL-STATUS reporter (common to every strategy)
        assert "nlp2mcp_force_modelstat = mcp_model.modelStat;" in out
        assert "nlp2mcp_force_solvestat = mcp_model.solveStat;" in out

    def test_multistart_emits_restart_loop(self):
        out = emit_forcing_scaffold("multistart", "mcp_model")
        assert "Set nlp2mcp_force_pt" in out
        assert "loop(nlp2mcp_force_pt$(nlp2mcp_force_done = 0)," in out
        assert "Solve mcp_model using MCP;" in out
        # stops at the first MS 1/2
        assert "nlp2mcp_force_done$(mcp_model.modelStat <= 2) = 1;" in out
        assert "nlp2mcp_force_modelstat = mcp_model.modelStat;" in out

    def test_homotopy_emits_proximal_continuation_loop(self):
        out = emit_forcing_scaffold("homotopy", "mcp_model")
        assert "Set nlp2mcp_force_step" in out
        assert "Parameter nlp2mcp_force_mu(nlp2mcp_force_step)" in out
        assert "loop(nlp2mcp_force_step," in out
        # the model-agnostic proximal_perturbation continuation: PATH forced,
        # optfile enabled, path.opt rewritten per step with the mu schedule
        assert "option mcp = path;" in out
        assert "mcp_model.optfile = 1;" in out
        assert "file nlp2mcp_force_opt / path.opt /;" in out
        assert "putclose nlp2mcp_force_opt 'proximal_perturbation '" in out
        assert "Solve mcp_model using MCP;" in out
        assert "nlp2mcp_force_modelstat = mcp_model.modelStat;" in out

    def test_model_name_is_threaded(self):
        out = emit_forcing_scaffold("optfile", "my_mcp")
        assert "my_mcp.optfile = 1;" in out
        assert "Solve my_mcp using MCP;" in out
        assert "nlp2mcp_force_modelstat = my_mcp.modelStat;" in out

    def test_no_comments_suppresses_comments(self):
        out = emit_forcing_scaffold("optfile", "mcp_model", add_comments=False)
        assert "* --force" not in out
        assert "$onecho > path.opt" in out  # driver still present

    def test_unknown_strategy_raises(self):
        with pytest.raises(ValueError, match="unknown forcing strategy"):
            emit_forcing_scaffold("bogus", "mcp_model")

    def test_all_strategies_emit_a_solve_and_reporter(self):
        for s in FORCING_STRATEGIES:
            out = emit_forcing_scaffold(s, "mcp_model")
            assert "Solve mcp_model using MCP;" in out, s
            assert "Display nlp2mcp_force_modelstat, nlp2mcp_force_solvestat;" in out, s


class TestConfigForceStrategy:
    def test_default_is_none(self):
        assert Config().force_strategy == "none"

    @pytest.mark.parametrize("strategy", ["none", "homotopy", "multistart", "optfile"])
    def test_valid_strategies_accepted(self, strategy):
        assert Config(force_strategy=strategy).force_strategy == strategy

    def test_invalid_strategy_rejected(self):
        with pytest.raises(ValueError, match="force_strategy must be"):
            Config(force_strategy="bogus")


class TestEmitGamsMcpForcingBranch:
    """Guard the `emit_gams_mcp` branch that switches plain Solve <-> scaffold."""

    def test_none_emits_plain_solve(self):
        out = _emit_with_force("none")
        assert "Solve mcp_model using MCP;" in out
        # no forcing driver / reporter on the default path
        assert "nlp2mcp_force_modelstat" not in out
        assert "path.opt" not in out
        assert "loop(nlp2mcp_force" not in out

    def test_optfile_wraps_the_solve(self):
        out = _emit_with_force("optfile")
        assert "$onecho > path.opt" in out
        assert "option mcp = path;" in out
        assert "mcp_model.optfile = 1;" in out
        assert "nlp2mcp_force_modelstat = mcp_model.modelStat;" in out

    def test_multistart_wraps_the_solve(self):
        out = _emit_with_force("multistart")
        assert "loop(nlp2mcp_force_pt$(nlp2mcp_force_done = 0)," in out
        assert "nlp2mcp_force_modelstat = mcp_model.modelStat;" in out

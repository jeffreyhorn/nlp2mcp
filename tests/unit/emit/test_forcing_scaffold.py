"""Sprint 30 P8: solution-forcing scaffold (``--force <strategy>``) tests.

The scaffold wraps the terminal ``Solve <model> using MCP;`` in a forcing driver
(homotopy / multistart / optfile) + a MODEL-STATUS reporter — the stable interface
the Sprint-31 PATH-consultation work inherits. These tests guard: (a) each driver's
structure + the reporter, (b) the ``none`` default leaves the plain solve untouched,
(c) validation, and (d) the Config field validation.
"""

from __future__ import annotations

import pytest

from src.config import Config
from src.emit.forcing import FORCING_STRATEGIES, emit_forcing_scaffold

pytestmark = pytest.mark.unit


class TestEmitForcingScaffold:
    def test_optfile_emits_pathopt_and_reporter(self):
        out = emit_forcing_scaffold("optfile", "mcp_model")
        assert "$onecho > path.opt" in out
        assert "proximal_perturbation 1e-2" in out
        assert "merit_function normal" in out
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

    def test_homotopy_emits_continuation_loop(self):
        out = emit_forcing_scaffold("homotopy", "mcp_model")
        assert "Set nlp2mcp_force_step" in out
        assert "Parameter nlp2mcp_force_mu(nlp2mcp_force_step)" in out
        assert "loop(nlp2mcp_force_step," in out
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

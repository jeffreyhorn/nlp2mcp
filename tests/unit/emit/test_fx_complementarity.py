"""Tests for .fx emission of inactive complementarity multiplier instances.

Issue #942: Diagonal elements of multi-index complementarity equations (i,j)
where i and j share the same set produce empty equations. The multiplier
must be fixed to 0 on the diagonal.

Issue #943: Complementarity equations with lead/lag expressions (e.g., i+1)
implicitly exclude terminal indices. The multiplier must be fixed to 0 for
those excluded instances.
"""

from __future__ import annotations

import os
import sys

import pytest

from src.config import Config
from src.emit.emit_gams import emit_gams_mcp
from src.ir.parser import parse_model_file


def _gamslib_path(model_name: str) -> str:
    return os.path.join("data", "gamslib", "raw", f"{model_name}.gms")


def _skip_if_missing(model_name: str) -> str:
    path = _gamslib_path(model_name)
    if not os.path.exists(path):
        pytest.skip(f"GAMSlib model {model_name} not available")
    return path


def _generate_mcp(model_name: str) -> str:
    """Run full pipeline: parse -> reformulate -> AD -> assemble -> emit."""
    _skip_if_missing(model_name)
    path = _gamslib_path(model_name)
    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        from src.ad.constraint_jacobian import compute_constraint_jacobian
        from src.ad.gradient import compute_objective_gradient
        from src.ir.normalize import normalize_model
        from src.kkt.assemble import assemble_kkt_system
        from src.kkt.reformulation import reformulate_model

        model = parse_model_file(path)
        reformulate_model(model)
        normalized_eqs = normalize_model(model)
        config = Config()
        gradient = compute_objective_gradient(model, config)
        J_eq, J_ineq = compute_constraint_jacobian(model, normalized_eqs, config)
        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq, config)
        return emit_gams_mcp(kkt)
    finally:
        sys.setrecursionlimit(old_limit)


@pytest.mark.unit
class TestDiagonalComplementarityFix:
    """Issue #942: Fix multipliers on diagonal of same-set multi-index complementarity."""

    def test_ps2_f_s_diagonal_fx_emitted(self):
        """ps2_f_s: lam_ic.fx(i,j)$(ord(i) = ord(j)) = 0 must appear."""
        result = _generate_mcp("ps2_f_s")
        assert "lam_ic.fx(i,j)$(ord(i) = ord(j)) = 0;" in result

    def test_ps3_s_gic_diagonal_fx_emitted(self):
        """ps3_s_gic: lam_ic.fx(i,j)$(ord(i) = ord(j)) = 0 must appear."""
        result = _generate_mcp("ps3_s_gic")
        assert "lam_ic.fx(i,j)$(ord(i) = ord(j)) = 0;" in result


@pytest.mark.unit
class TestLeadLagComplementarityFix:
    """Issue #943: Fix multipliers for excluded terminal indices from lead/lag."""

    def test_ps3_s_leadlag_fx_emitted(self):
        """ps3_s: lam_licd.fx(i)$(not (ord(i) <= card(i) - 1)) = 0 must appear."""
        result = _generate_mcp("ps3_s")
        assert "lam_licd.fx(i)$(not (ord(i) <= card(i) - 1)) = 0;" in result

    def test_ps3_s_mn_leadlag_fx_emitted(self):
        """ps3_s_mn: lam_licd and lam_mn .fx must appear."""
        result = _generate_mcp("ps3_s_mn")
        assert "lam_licd.fx(i)$(not (ord(i) <= card(i) - 1)) = 0;" in result
        assert "lam_mn.fx(i)$(not (ord(i) <= card(i) - 1)) = 0;" in result

    def test_ps10_s_leadlag_fx_emitted(self):
        """ps10_s: lam_licd.fx(i)$(not (ord(i) <= card(i) - 1)) = 0 must appear."""
        result = _generate_mcp("ps10_s")
        assert "lam_licd.fx(i)$(not (ord(i) <= card(i) - 1)) = 0;" in result

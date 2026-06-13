"""Unit tests for the KKT-residual harness (Sprint 28 Priority 9 / PR27), Day 1.

Covers the Day-1 build: the dual-transfer reuse/extraction (Architecture A), the
residual-only (iterlim=0) rewrite, and the dual-transfer consistency self-check.
The "dual transfer on launch" check uses the committed ``launch_mcp_presolve.gms``
golden — a real ``--nlp-presolve`` emit — so it needs no GAMS.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "diagnostics"))

from kkt_residual import (  # noqa: E402  (path set above)
    DualTransfer,
    build_arg_parser,
    classify_consistency,
    extract_dual_transfer,
    main,
    make_residual_only,
)

LAUNCH_PRESOLVE = PROJECT_ROOT / "data" / "gamslib" / "mcp" / "launch_mcp_presolve.gms"


class TestExtractDualTransferOnLaunch:
    """Architecture A: the harness reuses the production ``--nlp-presolve`` dual
    transfer. On launch it must extract all four multiplier classes."""

    def test_launch_golden_present(self) -> None:
        assert LAUNCH_PRESOLVE.exists(), f"missing fixture: {LAUNCH_PRESOLVE}"

    def test_extracts_all_four_multiplier_classes(self) -> None:
        text = LAUNCH_PRESOLVE.read_text(encoding="utf-8")
        transfer = extract_dual_transfer(text)
        # launch warm-starts equalities (nu_*), inequalities (lam_*), and bounds.
        assert transfer.nu, "expected nu_* equality-multiplier transfers"
        assert transfer.lam, "expected lam_* inequality-multiplier transfers"
        assert transfer.piL, "expected piL_* lower-bound multiplier transfers"
        assert transfer.piU, "expected piU_* upper-bound multiplier transfers"
        assert not transfer.is_empty
        assert transfer.total == (
            len(transfer.nu) + len(transfer.lam) + len(transfer.piL) + len(transfer.piU)
        )

    def test_lam_transfers_use_abs(self) -> None:
        # Inequality marginals are loaded with abs() (GAMS =g=/=l= sign convention).
        text = LAUNCH_PRESOLVE.read_text(encoding="utf-8")
        transfer = extract_dual_transfer(text)
        assert all("abs(" in stmt for stmt in transfer.lam)

    def test_only_multiplier_assignments_captured(self) -> None:
        # Stray non-multiplier lines must not leak into the transfer.
        text = LAUNCH_PRESOLVE.read_text(encoding="utf-8")
        transfer = extract_dual_transfer(text)
        for stmt in transfer.nu + transfer.lam + transfer.piL + transfer.piU:
            assert stmt.startswith(("nu_", "lam_", "piL_", "piU_"))
            assert ".l" in stmt and stmt.endswith(";")


class TestExtractDualTransferEdgeCases:
    def test_empty_text_is_empty(self) -> None:
        assert extract_dual_transfer("").is_empty

    def test_no_multiplier_lines_is_empty(self) -> None:
        text = "Equations stat_x;\nstat_x.. x =E= 0;\nSolve mcp_model using MCP;\n"
        transfer = extract_dual_transfer(text)
        assert transfer.is_empty
        assert transfer.total == 0

    def test_classifies_by_prefix(self) -> None:
        text = (
            "nu_eq.l(i) = eq.m(i);\n"
            "lam_cap.l(i) = abs(cap.m(i));\n"
            "piL_x.l(i) = x.m(i);\n"
            "piU_x.l(i) = -(x.m(i));\n"
        )
        transfer = extract_dual_transfer(text)
        assert (len(transfer.nu), len(transfer.lam), len(transfer.piL), len(transfer.piU)) == (
            1,
            1,
            1,
            1,
        )


class TestMakeResidualOnly:
    def test_inserts_iterlim_before_solve(self) -> None:
        text = "Model mcp_model / all /;\nSolve mcp_model using MCP;\nDisplay x.l;\n"
        out = make_residual_only(text)
        assert "mcp_model.iterlim = 0;" in out
        # iterlim must precede the Solve.
        assert out.index("mcp_model.iterlim = 0;") < out.index("Solve mcp_model using MCP;")

    def test_preserves_indentation(self) -> None:
        text = "  Solve mcp_model using MCP;\n"
        out = make_residual_only(text)
        assert "  mcp_model.iterlim = 0;\n  Solve mcp_model using MCP;" in out

    def test_raises_without_solve(self) -> None:
        with pytest.raises(ValueError, match="no `Solve"):
            make_residual_only("Equations stat_x;\nstat_x.. x =E= 0;\n")

    def test_real_launch_golden_rewrites_once(self) -> None:
        text = LAUNCH_PRESOLVE.read_text(encoding="utf-8")
        out = make_residual_only(text)
        assert out.count("mcp_model.iterlim = 0;") == 1


class TestClassifyConsistency:
    def test_passes_when_all_within_tol(self) -> None:
        assert classify_consistency({"eq1": 1e-9, "eq2": -5e-10}) is None

    def test_flags_when_a_row_exceeds_tol(self) -> None:
        assert classify_consistency({"eq1": 1e-9, "comp_cap": 0.4}) == "dual_transfer_inconsistent"

    def test_tol_is_respected(self) -> None:
        # 1e-4 is fine at the default tol's neighbour but flagged at a tighter tol.
        residuals = {"eq1": 1e-4}
        assert classify_consistency(residuals, tol=1e-3) is None
        assert classify_consistency(residuals, tol=1e-6) == "dual_transfer_inconsistent"

    def test_empty_residuals_pass(self) -> None:
        assert classify_consistency({}) is None

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
    def test_non_finite_residuals_fail_closed(self, bad: float) -> None:
        # abs(nan) > tol is False — a NaN/inf row must still be treated as
        # offending (fail closed), not silently pass the self-check.
        assert classify_consistency({"stat_x": bad}) == "dual_transfer_inconsistent"

    def test_finite_within_tol_still_passes_alongside_nothing(self) -> None:
        assert classify_consistency({"eq1": 0.0, "eq2": 1e-9}) is None


def test_dual_transfer_dataclass_summary() -> None:
    transfer = DualTransfer(nu=["a"], lam=["b", "c"], piL=[], piU=["d"])
    assert transfer.total == 4
    assert not transfer.is_empty
    assert "total 4" in transfer.summary()


class TestCliFailFast:
    """Day-1 `main()` must fail fast (not silently ignore) on the flags whose
    behavior lands Days 2–3 — these checks run before any emit/GAMS work."""

    @pytest.mark.parametrize(
        "extra",
        [
            ["--gdx", "sol.gdx"],
            ["--json", "out.json"],
            ["--tol", "1e-4"],
            ["--nlp-solver", "CONOPT"],
            ["--no-cold-start"],
        ],
    )
    def test_unimplemented_flags_fail_fast(self, extra: list[str]) -> None:
        # Returns non-zero before touching the (nonexistent) model file or GAMS.
        assert main(["does_not_exist.gms", *extra]) == 2

    def test_help_text_has_no_typo(self) -> None:
        help_text = build_arg_parser().format_help()
        assert "no---gdx" not in help_text

    def test_deferred_flag_help_does_not_claim_an_active_default(self) -> None:
        # --tol/--nlp-solver argparse-default to None (sentinels) in Day 1, so the
        # help must not imply the documented value is the *current* default.
        # Collapse argparse's line-wrapping before matching the phrase. Every
        # fail-fast flag (--gdx/--json/--tol/--nlp-solver/--no-cold-start) must
        # say so in its help, so the docs match main()'s behavior.
        help_text = " ".join(build_arg_parser().format_help().split())
        assert help_text.count("not honored in the Day-1 build") >= 5


def test_no_args_defaults_are_inert_sentinels() -> None:
    # tol/nlp-solver default to None (sentinels) so an explicit value is detectable.
    args = build_arg_parser().parse_args(["model.gms"])
    assert args.tol is None
    assert args.nlp_solver is None
    assert args.gdx is None
    assert args.json is None
    assert args.no_cold_start is False

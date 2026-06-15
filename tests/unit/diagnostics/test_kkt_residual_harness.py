"""Unit tests for the KKT-residual harness (Sprint 28 Priority 9 / PR27), Days 1–2.

Covers the dual-transfer reuse/extraction (Architecture A), the residual-only
(iterlim=0) rewrite, the `nu` sign correction, gdxdump parsing, the relative-
residual Case-(a/b/c) verdict, the §2 self-check, the JSON/human output, and the
`--gdx` skip variant. The launch checks use the committed ``launch_mcp_presolve.gms``
golden — a real ``--nlp-presolve`` emit — so they need no GAMS.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "diagnostics"))

from kkt_residual import (  # noqa: E402  (path set above)
    REL_TOL_DEFAULT,
    DualTransfer,
    RowResidual,
    TransferCheck,
    Verdict,
    apply_residual_sign_correction,
    build_arg_parser,
    build_gdx_skip_variant,
    build_report,
    build_residual_only_mcp,
    check_dual_transfer,
    classify_consistency,
    classify_verdict,
    dual_scale,
    extract_dual_transfer,
    extract_equation_names,
    extract_multiplier_names,
    format_human,
    format_json,
    inject_residual_unload,
    main,
    make_residual_only,
    neutralize_nlp_solve,
    parse_gdxdump_allfields,
    parse_gdxdump_csv,
    primal_scale,
    relative_residual,
    row_kind,
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
    """Day-2 `main()`: only `--nlp-solver` is still deferred (fail-fast); the other
    flags are implemented. Model-existence is checked before any GAMS work."""

    def test_nlp_solver_still_fails_fast(self) -> None:
        # --nlp-solver is the one deferred flag — rejected before model/GAMS work.
        assert main(["does_not_exist.gms", "--nlp-solver", "CONOPT"]) == 2

    @pytest.mark.parametrize(
        "extra",
        [
            ["--gdx", "sol.gdx"],
            ["--json", "out.json"],
            ["--tol", "1e-4"],
            ["--no-cold-start"],
        ],
    )
    def test_missing_model_returns_2(self, extra: list[str]) -> None:
        # Implemented flags no longer fail-fast; a missing model still returns 2
        # (model-not-found) before any emit/GAMS work.
        assert main(["does_not_exist.gms", *extra]) == 2

    def test_help_text_has_no_typo(self) -> None:
        help_text = build_arg_parser().format_help()
        assert "no---gdx" not in help_text

    def test_only_nlp_solver_help_carries_the_deferred_disclaimer(self) -> None:
        # In the Day-2 build only --nlp-solver is unimplemented, so exactly its help
        # carries the "not honored" disclaimer; the implemented flags must not.
        help_text = " ".join(build_arg_parser().format_help().split())
        assert help_text.count("not honored in the Day-2 build") == 1
        assert "not honored in the Day-1 build" not in help_text

    def test_tol_help_states_relative_default(self) -> None:
        help_text = " ".join(build_arg_parser().format_help().split())
        assert "relative stationarity-residual tolerance" in help_text
        assert "default 0.001" in help_text  # REL_TOL_DEFAULT


def test_no_args_defaults_are_inert_sentinels() -> None:
    # tol/nlp-solver default to None (sentinels) so an explicit value is detectable
    # (main resolves --tol to REL_TOL_DEFAULT when unset).
    args = build_arg_parser().parse_args(["model.gms"])
    assert args.tol is None
    assert args.nlp_solver is None
    assert args.gdx is None
    assert args.json is None
    assert args.no_cold_start is False


class TestKeepFiles:
    def test_default_is_cleanup(self) -> None:
        assert build_arg_parser().parse_args(["model.gms"]).keep_files is False

    def test_flag_sets_keep(self) -> None:
        assert build_arg_parser().parse_args(["model.gms", "--keep-files"]).keep_files is True

    def test_keep_files_is_an_active_flag(self) -> None:
        # --keep-files controls cleanup *now* — it must NOT carry the deferred
        # disclaimer, and passing it alone must not trip the fail-fast path.
        help_text = " ".join(build_arg_parser().format_help().split())
        keep_help = help_text.split("--keep-files")[1].split("--")[0]
        assert "not honored" not in keep_help


# ---------------------------------------------------------------------------
# Day-2: sign correction, residual extraction, verdict, output
# ---------------------------------------------------------------------------


class TestSignCorrection:
    """The `nu_*` warm-start is negated for the residual check (design §2 Day-2):
    the production `nu = eq.m` is sign-flipped vs the emitted stationarity row."""

    def test_negates_nu_transfer(self) -> None:
        text = "nu_diweight.l(s) = diweight.m(s);\n"
        out = apply_residual_sign_correction(text)
        assert out == "nu_diweight.l(s) = -(diweight.m(s));\n"

    def test_scalar_nu_negated(self) -> None:
        out = apply_residual_sign_correction("nu_defvt.l = defvt.m;\n")
        assert out == "nu_defvt.l = -(defvt.m);\n"

    def test_lam_piL_piU_untouched(self) -> None:
        # Only the free multiplier nu is sign-ambiguous; non-negative magnitudes stay.
        text = (
            "nu_eq.l(s) = eq.m(s);\n"
            "lam_cap.l(s) = abs(cap.m(s));\n"
            "piL_x.l(s) = x.m(s);\n"
            "piU_x.l(s) = -(x.m(s));\n"
        )
        out = apply_residual_sign_correction(text)
        assert "nu_eq.l(s) = -(eq.m(s));" in out
        assert "lam_cap.l(s) = abs(cap.m(s));" in out  # unchanged
        assert "piL_x.l(s) = x.m(s);" in out  # unchanged
        assert "piU_x.l(s) = -(x.m(s));" in out  # unchanged

    def test_real_launch_golden_flips_every_nu(self) -> None:
        text = LAUNCH_PRESOLVE.read_text(encoding="utf-8")
        n_before = text.count("nu_")
        out = apply_residual_sign_correction(text)
        # Every nu_*.l transfer line now negates its rhs.
        transfer = extract_dual_transfer(text)
        for stmt in transfer.nu:
            sym = stmt.split(".l", 1)[0]
            assert f"{sym}.l" in out
        assert out.count("= -(") >= len(transfer.nu)
        assert n_before == out.count("nu_")  # no nu references lost


class TestInjectResidualUnload:
    def test_appends_execute_unload_after_solve(self) -> None:
        text = "  Solve mcp_model using MCP;\nDisplay x.l;\n"
        out = inject_residual_unload(text, "/tmp/k.gdx")
        assert "  Solve mcp_model using MCP;" in out
        assert "  execute_unload '/tmp/k.gdx';" in out
        assert out.index("Solve mcp_model") < out.index("execute_unload")

    def test_raises_without_solve(self) -> None:
        with pytest.raises(ValueError, match="execute_unload"):
            inject_residual_unload("Display x.l;\n", "/tmp/k.gdx")


class TestParseGdxdumpCsv:
    def test_indexed_symbol(self) -> None:
        csv = '"s","Val"\n"stage-1",16.08\n"stage-2",-3.5\n'
        out = parse_gdxdump_csv(csv)
        assert out == {("stage-1",): 16.08, ("stage-2",): -3.5}

    def test_scalar_symbol(self) -> None:
        out = parse_gdxdump_csv('"Val"\n-114.8\n')
        assert out == {(): -114.8}

    def test_multi_index(self) -> None:
        csv = '"i","j","Val"\n"a","b",1.0\n'
        assert parse_gdxdump_csv(csv) == {("a", "b"): 1.0}

    def test_empty(self) -> None:
        assert parse_gdxdump_csv("") == {}
        assert parse_gdxdump_csv('"s","Val"\n') == {}

    @pytest.mark.parametrize(
        "token,expected",
        [("NA", math.nan), ("INF", math.inf), ("-INF", -math.inf), ("UNDF", math.nan)],
    )
    def test_non_finite_tokens(self, token: str, expected: float) -> None:
        out = parse_gdxdump_csv(f'"s","Val"\n"x",{token}\n')
        val = out[("x",)]
        if math.isnan(expected):
            assert math.isnan(val)
        else:
            assert val == expected


class TestDualScaleAndRelative:
    def test_dual_scale_floors_at_one(self) -> None:
        assert dual_scale([]) == 1.0
        assert dual_scale([0.0, 0.0]) == 1.0
        assert dual_scale([0.3, -0.5]) == 1.0

    def test_dual_scale_is_max_magnitude(self) -> None:
        assert dual_scale([8.0, -14.0, 2.0]) == 14.0

    def test_dual_scale_ignores_non_finite(self) -> None:
        assert dual_scale([math.inf, 3.0, math.nan]) == 3.0

    def test_relative_residual(self) -> None:
        assert relative_residual(8e-3, 14.0) == pytest.approx(8e-3 / 14.0)
        assert relative_residual(-396.0, 1.0) == 396.0

    def test_relative_residual_preserves_non_finite(self) -> None:
        assert math.isnan(relative_residual(math.nan, 10.0))
        assert relative_residual(math.inf, 10.0) == math.inf


class TestRowKind:
    def test_prefixes(self) -> None:
        assert row_kind("stat_x") == "stationarity"
        assert row_kind("comp_lo_x") == "complementarity"
        assert row_kind("diweight") == "equality"
        assert row_kind("costdef") == "equality"


class TestCheckDualTransfer:
    def test_healthy_passes(self) -> None:
        # Inactive bound: activity within [lower, upper] → zero breach. costdef/dweight
        # with val == bound → zero residual (the Day-2 Val-vs-bound fix).
        rows = [
            RowResidual.equality("stat_x", ("a",), 1e-13),
            RowResidual.inequality("comp_lo_x", ("a",), 68.0, 1.0, math.inf),
            RowResidual("costdef", (), -850.0, -850.0, -850.0, "equality"),
        ]
        chk = check_dual_transfer(rows)
        assert chk.consistent and chk.reason is None
        assert chk.max_equality_residual == 0.0  # val == bound

    def test_comp_constant_in_bound_is_feasible(self) -> None:
        # launch comp_up_vt: `50000 - vt =G= 0` → val=-vt, lower=-50000 → feasible.
        rows = [RowResidual.inequality("comp_up_vt", (), -39136.0, -50000.0, math.inf)]
        assert check_dual_transfer(rows).consistent

    def test_gross_infeasibility_flags(self) -> None:
        # Activity below the lower bound by a large relative amount.
        rows = [
            RowResidual.equality("stat_x", (), 0.0),
            RowResidual.inequality("comp_lo_x", ("a",), 0.6, 1.0, math.inf),
        ]
        chk = check_dual_transfer(rows)
        assert not chk.consistent
        assert chk.reason is not None and chk.reason.startswith("gross_infeasibility")

    def test_non_finite_fails_closed(self) -> None:
        rows = [RowResidual.equality("stat_x", (), math.nan)]
        chk = check_dual_transfer(rows)
        assert not chk.consistent and "non_finite" in str(chk.reason)

    def test_small_relative_breach_within_feas_tol_ok(self) -> None:
        # A magnitude-50000 activity violating its bound by NLP tolerance is fine.
        rows = [RowResidual.inequality("comp_lo_x", ("a",), 49999.95, 50000.0, math.inf)]
        assert check_dual_transfer(rows).consistent


class TestClassifyVerdict:
    def _stat(self, specs):
        return [RowResidual.equality(n, idx, raw) for (n, idx, raw) in specs]

    OK = TransferCheck(True, None, 0.0, 0.0)

    def test_case_b_emit_bug(self) -> None:
        rows = self._stat([("stat_r", ("i1",), 396.0), ("stat_x", ("i1",), 1e-9)])
        v = classify_verdict(rows, scale=1.0, transfer=self.OK, tol=REL_TOL_DEFAULT)
        assert v.code == "case_b"
        assert v.max_row is not None and v.max_row.name == "stat_r"

    def test_case_a_with_cold_optimal(self) -> None:
        rows = self._stat([("stat_x", ("a",), 8e-3)])
        v = classify_verdict(
            rows, scale=14.0, transfer=self.OK, tol=REL_TOL_DEFAULT, cold_start_status="optimal"
        )
        assert v.code == "case_a"  # 8e-3/14 = 5.7e-4 < 1e-3

    def test_case_c_with_cold_diverged(self) -> None:
        rows = self._stat([("stat_x", ("a",), 5e-8)])
        v = classify_verdict(
            rows, scale=1.0, transfer=self.OK, tol=REL_TOL_DEFAULT, cold_start_status="diverged"
        )
        assert v.code == "case_c"

    def test_case_a_or_c_when_cold_skipped(self) -> None:
        rows = self._stat([("stat_x", ("a",), 1e-9)])
        v = classify_verdict(rows, scale=1.0, transfer=self.OK, tol=REL_TOL_DEFAULT)
        assert v.code == "case_a_or_c"

    def test_case_a_or_c_when_cold_unavailable(self) -> None:
        # A clean residual + an un-emittable cold MCP must not masquerade as Case c.
        rows = self._stat([("stat_x", ("a",), 1e-9)])
        v = classify_verdict(
            rows, scale=1.0, transfer=self.OK, tol=REL_TOL_DEFAULT, cold_start_status="unavailable"
        )
        assert v.code == "case_a_or_c"

    def test_inconsistent_transfer_short_circuits(self) -> None:
        bad = TransferCheck(False, "gross_infeasibility:comp_lo_x(a)", 0.4, 0.0)
        rows = self._stat([("stat_x", (), 0.0)])
        v = classify_verdict(rows, scale=1.0, transfer=bad, tol=REL_TOL_DEFAULT)
        assert v.code == "dual_transfer_inconsistent"

    def test_relative_residual_rescues_launch_like_row(self) -> None:
        # Same raw residual, different scale flips the verdict (relative, design §3).
        rows = self._stat([("stat_x", (), 8e-3)])
        small = classify_verdict(
            rows, scale=1.0, transfer=self.OK, tol=REL_TOL_DEFAULT, cold_start_status="optimal"
        )
        big = classify_verdict(
            rows, scale=14.0, transfer=self.OK, tol=REL_TOL_DEFAULT, cold_start_status="optimal"
        )
        assert small.code == "case_b"  # 8e-3 absolute > 1e-3
        assert big.code == "case_a"  # 8e-3/14 < 1e-3


class TestReportOutput:
    def _report(self):
        rows = [
            RowResidual.equality("stat_r", ("i1",), 396.0),
            RowResidual.equality("stat_x", ("i1",), 2e-8),
        ]
        verdict = Verdict("case_b", 396.0, rows[0], 1.0)
        transfer = TransferCheck(True, None, 4.1e-9, 20.0)
        return build_report("camshape", 1e-3, verdict, transfer, rows)

    def test_report_shape(self) -> None:
        rep = self._report()
        assert rep["model"] == "camshape"
        assert rep["verdict"] == "case_b"
        assert rep["max_residual_row"]["name"] == "stat_r"
        assert rep["dual_transfer"]["consistent"] is True
        assert len(rep["rows"]) == 2
        assert rep["rows"][0]["name"] == "stat_r"  # ranked by relative desc

    def test_format_json_roundtrips(self) -> None:
        import json as _json

        parsed = _json.loads(format_json(self._report()))
        assert parsed["verdict"] == "case_b"
        assert parsed["max_residual_row"]["index"] == ["i1"]

    def test_format_human_mentions_verdict_and_row(self) -> None:
        text = format_human(self._report())
        assert "CASE_B" in text
        assert "stat_r(i1)" in text
        assert "camshape" in text

    def test_format_human_inconsistent_transfer(self) -> None:
        verdict = Verdict(
            "dual_transfer_inconsistent", math.nan, None, 1.0, "gross_infeasibility:c"
        )
        transfer = TransferCheck(False, "gross_infeasibility:c", 0.4, 0.0)
        rep = build_report("m", 1e-3, verdict, transfer, [])
        text = format_human(rep)
        assert "INCONSISTENT" in text
        assert "DUAL_TRANSFER_INCONSISTENT" in text


class TestExtractNames:
    def test_extract_equation_names(self) -> None:
        text = LAUNCH_PRESOLVE.read_text(encoding="utf-8")
        names = extract_equation_names(text)
        assert "stat_aweight" in names
        assert "comp_pwlower" in names
        assert "costdef" in names
        assert len(names) == len(set(names))  # de-duped

    def test_extract_multiplier_names(self) -> None:
        text = LAUNCH_PRESOLVE.read_text(encoding="utf-8")
        names = extract_multiplier_names(text)
        assert "nu_diweight" in names
        assert all(n.startswith(("nu_", "lam_", "piL_", "piU_")) for n in names)


class TestGdxSkipVariant:
    def test_neutralize_nlp_solve(self) -> None:
        src = "Solve launch using NLP minimizing cost;\nDisplay x.l;\n"
        out, n = neutralize_nlp_solve(src)
        assert n == 1
        assert out.startswith("* [kkt-residual --gdx] NLP solve skipped:")
        assert "Display x.l;" in out

    def test_neutralize_no_solve(self) -> None:
        out, n = neutralize_nlp_solve("Display x.l;\n")
        assert n == 0 and out == "Display x.l;\n"

    def test_build_gdx_skip_variant_rewrites_include(self) -> None:
        text = '$include "data/gamslib/raw/launch.gms"\nDisplay x;\n'
        out = build_gdx_skip_variant(text, "launch.gms", "/scratch/neutralized.gms", "/s/sol.gdx")
        assert '$include "/scratch/neutralized.gms"' in out
        assert "execute_loadpoint '/s/sol.gdx';" in out
        assert "data/gamslib/raw/launch.gms" not in out

    def test_build_gdx_skip_variant_raises_without_include(self) -> None:
        with pytest.raises(ValueError, match="include"):
            build_gdx_skip_variant("Display x;\n", "launch.gms", "/n.gms", "/s.gdx")


class TestBuildResidualOnlyMcp:
    def test_no_gdx_chains_transforms(self) -> None:
        text = LAUNCH_PRESOLVE.read_text(encoding="utf-8")
        out = build_residual_only_mcp(
            text, "/tmp/k.gdx", gdx=None, source_basename=None, neutralized_include=None
        )
        assert "mcp_model.iterlim = 0;" in out
        assert "execute_unload '/tmp/k.gdx';" in out
        assert "= -(" in out  # nu sign correction applied

    def test_gdx_path_injects_loadpoint(self) -> None:
        text = LAUNCH_PRESOLVE.read_text(encoding="utf-8")
        out = build_residual_only_mcp(
            text,
            "/tmp/k.gdx",
            gdx="/s/sol.gdx",
            source_basename="launch.gms",
            neutralized_include="/scratch/n.gms",
        )
        assert "execute_loadpoint '/s/sol.gdx';" in out
        assert '$include "/scratch/n.gms"' in out
        assert "mcp_model.iterlim = 0;" in out


class TestRowResidualFields:
    """The Val-vs-bounds residual model (Day-2 fix): a constraint's constant lives
    in the bound, so the residual is the activity relative to [lower, upper]."""

    def test_stationarity_residual_is_val(self) -> None:
        r = RowResidual.from_fields("stat_x", ("a",), -3.5e-15, 0.0, 0.0)
        assert r.is_equality
        assert r.signed_residual == -3.5e-15
        assert r.infeasibility == pytest.approx(3.5e-15)

    def test_equality_with_constant_bound_is_zero_residual(self) -> None:
        # costdef: val == lower == upper == -850.76 → residual 0 (no discrepancy).
        r = RowResidual.from_fields("costdef", (), -850.76, -850.76, -850.76)
        assert r.kind == "equality"
        assert r.signed_residual == 0.0
        assert r.infeasibility == 0.0

    def test_inequality_constant_in_bound_feasible(self) -> None:
        # comp_up_vt: `50000 - vt =G= 0` → val=-vt, lower=-50000 → feasible.
        r = RowResidual.from_fields("comp_up_vt", (), -39136.0, -50000.0, math.inf)
        assert r.kind == "complementarity"
        assert not r.is_equality
        assert r.infeasibility == 0.0  # -39136 >= -50000

    def test_inequality_breach(self) -> None:
        r = RowResidual.from_fields("comp_lo_x", ("a",), 0.6, 1.0, math.inf)
        assert r.infeasibility == pytest.approx(0.4)

    def test_non_finite_val_propagates(self) -> None:
        r = RowResidual.from_fields("stat_x", (), math.nan, 0.0, 0.0)
        assert math.isnan(r.infeasibility)


class TestParseGdxdumpAllFields:
    def test_indexed_equation(self) -> None:
        csv = (
            '"s","Val","Marginal","Lower","Upper","Scale"\n'
            '"stage-1",68.07,0,1,+Inf,1\n'
            '"stage-2",28.31,0,1,+Inf,1\n'
        )
        out = parse_gdxdump_allfields(csv)
        assert out[("stage-1",)] == (68.07, 1.0, math.inf)
        assert out[("stage-2",)] == (28.31, 1.0, math.inf)

    def test_scalar_equation_with_equal_bounds(self) -> None:
        csv = '"Val","Marginal","Lower","Upper","Scale"\n-850.76,2257.8,-850.76,-850.76,1\n'
        out = parse_gdxdump_allfields(csv)
        assert out[()] == (-850.76, -850.76, -850.76)

    def test_neg_inf_lower(self) -> None:
        csv = '"Val","Marginal","Lower","Upper","Scale"\n-39136,0,-50000,+Inf,1\n'
        assert parse_gdxdump_allfields(csv)[()] == (-39136.0, -50000.0, math.inf)

    def test_empty(self) -> None:
        assert parse_gdxdump_allfields("") == {}


class TestPrimalScale:
    def test_uses_constraint_activities_not_stationarity(self) -> None:
        rows = [
            RowResidual.equality("stat_x", (), 1e6),  # excluded (stationarity)
            RowResidual.inequality("comp_lo_vt", (), 39136.0, 35000.0, math.inf),
        ]
        assert primal_scale(rows) == 39136.0

    def test_floors_at_one(self) -> None:
        assert primal_scale([]) == 1.0
        assert primal_scale([RowResidual.equality("dweight", (), 0.0)]) == 1.0


class TestReviewFixes:
    """PR #1441 review fixes: strict JSON + single-include guard."""

    def test_format_json_sanitizes_non_finite_to_null(self) -> None:
        import json as _json

        verdict = Verdict("dual_transfer_inconsistent", math.nan, None, 1.0, "non_finite")
        transfer = TransferCheck(False, "non_finite", math.inf, math.inf)
        rows = [RowResidual.equality("stat_x", (), math.nan)]
        rep = build_report("m", 1e-3, verdict, transfer, rows)
        text = format_json(rep)
        # Strict JSON: no NaN/Infinity tokens, parses, non-finite -> null.
        assert "NaN" not in text and "Infinity" not in text
        parsed = _json.loads(text)  # would raise on NaN/Infinity
        assert parsed["dual_transfer"]["max_comp_infeasibility"] is None
        assert parsed["rows"][0]["residual"] is None

    def test_build_gdx_skip_variant_rejects_multiple_includes(self) -> None:
        text = (
            '$include "data/gamslib/raw/launch.gms"\n'
            "Display x;\n"
            '$include "other/launch.gms"\n'
        )
        with pytest.raises(ValueError, match="exactly one"):
            build_gdx_skip_variant(text, "launch.gms", "/n.gms", "/s.gdx")


class TestReviewFixesRound2:
    """PR #1441 review round 2: NaN-bound fail-closed + RFC CSV parsing."""

    def test_check_dual_transfer_fails_closed_on_nan_bound(self) -> None:
        # Finite val but a NaN bound (corrupted NA/UNDF gdxdump) must fail closed —
        # infeasibility would otherwise treat the non-finite bound as "no bound".
        rows = [RowResidual.from_fields("comp_lo_x", ("a",), 5.0, math.nan, math.inf)]
        chk = check_dual_transfer(rows)
        assert not chk.consistent and "non_finite" in str(chk.reason)

    def test_check_dual_transfer_inf_bound_is_legitimate(self) -> None:
        # A +Inf upper bound is a normal one-sided constraint, not corruption.
        rows = [RowResidual.from_fields("comp_lo_x", ("a",), 5.0, 1.0, math.inf)]
        assert check_dual_transfer(rows).consistent

    def test_parse_gdxdump_csv_handles_quoted_comma_label(self) -> None:
        # A GAMS label containing a comma stays one field under RFC CSV parsing.
        out = parse_gdxdump_csv('"s","Val"\n"a,b",1.5\n')
        assert out == {("a,b",): 1.5}

    def test_parse_gdxdump_allfields_handles_quoted_comma_label(self) -> None:
        csv_text = '"s","Val","Marginal","Lower","Upper","Scale"\n"a,b",1.5,0,1,+Inf,1\n'
        assert parse_gdxdump_allfields(csv_text) == {("a,b",): (1.5, 1.0, math.inf)}


class TestReviewFixesRound3:
    """PR #1441 review round 3: explicit ValueError (not assert) for the --gdx
    precondition, so it is deterministic under `python -O` and caught by main()."""

    def test_gdx_without_source_basename_raises_valueerror(self) -> None:
        with pytest.raises(ValueError, match="source_basename/neutralized_include"):
            build_residual_only_mcp(
                "x", "/tmp/k.gdx", gdx="/s/sol.gdx", source_basename=None, neutralized_include="/n"
            )

    def test_gdx_without_neutralized_include_raises_valueerror(self) -> None:
        with pytest.raises(ValueError, match="source_basename/neutralized_include"):
            build_residual_only_mcp(
                "x",
                "/tmp/k.gdx",
                gdx="/s/sol.gdx",
                source_basename="m.gms",
                neutralized_include=None,
            )

"""
Issue #1335: Scalar-equation offset resolution / sum expansion.

Pre-Sprint 26 Day 9 fix: `_compute_equality_jacobian` / `_compute_inequality_jacobian`
gated `_resolve_index_offsets` + `_expand_sums_with_unresolved_offsets` behind
`if eq_domain:` (lines 986 + 1107 of `src/ad/constraint_jacobian.py`). For scalar
equations like otpop's `zdef.. z = sum(t, p(t + (card(t) - ord(t))))`, `eq_domain`
is empty so neither helper fired — the inner Sum's IndexOffset (`card(t)-ord(t)`)
stayed unresolved through the AD `_diff_sum` pipeline, so no `nu_zdef` cross-term
was emitted into `stat_p`.

Sprint 26 Day 9 fix:
1. Run `_resolve_index_offsets` + `_expand_sums_with_unresolved_offsets`
   regardless of `eq_domain` shape (gate relaxation).
2. Pass `iter_pos` through `_substitute_single_index` so `Call('ord', SymbolRef(t))`
   eagerly evaluates to `Const(iter_pos + 1)` during sum expansion — required
   because the substituted element (e.g. otpop '1974') may appear in multiple
   sets at different positions (`t` pos 0, `tt` pos 9, `th` pos 9), and the
   global `_try_eval_offset` lookup would otherwise return ambiguous.
"""

from src.ad.constraint_jacobian import _substitute_single_index
from src.ir.ast import Call, Const, SymbolRef


class TestIssue1335SubstituteOrdEager:
    """Unit-level: `_substitute_single_index` with `iter_pos` eagerly resolves
    `Call('ord', SymbolRef(var_name))` to `Const(iter_pos + 1)`."""

    def test_ord_substituted_to_iter_pos_plus_one(self):
        # expr: ord(t)
        expr = Call("ord", (SymbolRef("t"),))
        result = _substitute_single_index(expr, "t", "elem", iter_pos=0)
        assert isinstance(result, Const)
        assert result.value == 1.0  # 1-based

    def test_ord_substituted_at_non_zero_pos(self):
        expr = Call("ord", (SymbolRef("t"),))
        result = _substitute_single_index(expr, "t", "elem", iter_pos=9)
        assert isinstance(result, Const)
        assert result.value == 10.0

    def test_ord_unchanged_when_iter_pos_is_none(self):
        # Without iter_pos, Call(ord, var) still gets var-substituted normally
        # (returns Call with SymbolRef(value)) — matches pre-fix behavior.
        expr = Call("ord", (SymbolRef("t"),))
        result = _substitute_single_index(expr, "t", "1974")
        assert isinstance(result, Call)
        assert result.func == "ord"
        assert isinstance(result.args[0], SymbolRef)
        assert result.args[0].name == "1974"

    def test_ord_of_different_var_passes_through(self):
        # Call(ord, SymbolRef("s")) should NOT be touched when var_name is "t"
        expr = Call("ord", (SymbolRef("s"),))
        result = _substitute_single_index(expr, "t", "elem", iter_pos=0)
        assert isinstance(result, Call)
        assert result.func == "ord"
        assert isinstance(result.args[0], SymbolRef)
        assert result.args[0].name == "s"

    def test_card_passes_through_unchanged(self):
        # card() is a set-level intrinsic — argument is a set name, not an element.
        # Even with iter_pos, the var should not be substituted (set-level intrinsic).
        expr = Call("card", (SymbolRef("t"),))
        result = _substitute_single_index(expr, "t", "elem", iter_pos=0)
        assert isinstance(result, Call)
        assert result.func == "card"
        assert isinstance(result.args[0], SymbolRef)
        assert result.args[0].name == "t"


class TestIssue1335OtpopEmitContainsNuZdef:
    """End-to-end: translating `data/gamslib/raw/otpop.gms` must produce a
    `stat_p(tt)` body that contains `nu_zdef` (the scalar-equation
    cross-term). Pre-Sprint 26 Day 9 fix: 0 occurrences (the `if eq_domain:`
    gate skipped offset resolution + sum expansion for scalar `zdef`)."""

    def test_otpop_translate_emits_nu_zdef_in_stat_p_body(self, tmp_path):
        import pathlib
        import re
        import subprocess
        import sys

        repo_root = pathlib.Path(__file__).resolve().parent.parent.parent.parent
        otpop_src = repo_root / "data" / "gamslib" / "raw" / "otpop.gms"
        if not otpop_src.exists():
            import pytest

            pytest.skip(f"GAMSlib raw model not present: {otpop_src}")

        out_path = tmp_path / "otpop_mcp.gms"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.cli",
                str(otpop_src),
                "-o",
                str(out_path),
                "--skip-convexity-check",
                "--quiet",
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, (
            f"src.cli translation of otpop failed (rc={result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        emit = out_path.read_text()

        # Extract stat_p body — from the start of `stat_p(...).. ` to the
        # next `=E= 0;` on the same logical statement.
        m = re.search(r"^stat_p\([^)]*\)\.\.(.*?)=E= 0;", emit, re.MULTILINE | re.DOTALL)
        assert m is not None, (
            "Could not find stat_p body in otpop emit — Phase A / Day 1 emit "
            "shape may have changed."
        )
        stat_p_body = m.group(1)

        assert "nu_zdef" in stat_p_body, (
            "Issue #1335: stat_p body must contain at least one nu_zdef "
            "cross-term (the (zdef, p) Jacobian entry from "
            "`sum(t, p(t + (card(t) - ord(t))))`). Pre-fix: 0 occurrences. "
            f"Current body:\n{stat_p_body[:1500]}"
        )

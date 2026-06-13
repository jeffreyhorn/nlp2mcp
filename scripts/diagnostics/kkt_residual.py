"""KKT-residual verification harness (Sprint 28 Priority 9 / PR27).

Formalizes Sprint 27's GDX warm-from-good-optimum experiment into the standard
Case-(a/b/c) emit-bug-vs-non-convexity discriminator.

**Architecture A (chosen Sprint 28 Day 1):** the harness *reuses* the production
``--nlp-presolve`` emit for the warm-start. The Day-1 finding (PR24) corrected the
design doc's §2.66 premise — ``_emit_nlp_presolve`` (``src/emit/emit_gams.py``)
already loads the NLP duals into the MCP multipliers (``nu_<eq>.l = eq.m``,
``lam_<eq>.l = abs(eq.m)``, ``piL_*``/``piU_*`` from variable marginals), so the
harness does not re-derive the dual transfer via ``build_complementarity_pairs``.
It emits the MCP with ``--nlp-presolve`` (primal + dual warm-start), rewrites the
``Solve`` to an ``iterlim=0`` residual evaluation, and reads the per-row residuals.

See ``docs/planning/EPIC_4/SPRINT_28/PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md``.

Build status: Day 1 — CLI, dual-transfer reuse/extraction, residual-only rewrite,
and the consistency self-check. The GAMS run + residual parse + Case-(a/b/c)
verdict + JSON/human output land on Days 2–3.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

TOL_DEFAULT = 1e-6
DEFAULT_NLP_SOLVER = "CONOPT"
MCP_MODEL_NAME = "mcp_model"

# Headers the production --nlp-presolve emit writes around the dual transfer.
DUAL_HEADER = "Transfer NLP duals to MCP multiplier initialization"
BOUND_HEADER = "Transfer variable marginals to bound multipliers"

# A multiplier warm-start statement, e.g. `nu_diweight.l(s) = diweight.m(s);`.
_MULT_RE = re.compile(r"^(nu|lam|piL|piU)_\w+\.l\b.*=.*;")


@dataclass
class DualTransfer:
    """The multiplier warm-start statements the ``--nlp-presolve`` emit produced.

    Architecture A: the harness extracts (rather than re-derives) these from the
    emitted ``*_mcp_presolve.gms`` to confirm the production transfer covers the
    four multiplier classes before trusting any residual.
    """

    nu: list[str] = field(default_factory=list)  # equality multipliers (free)
    lam: list[str] = field(default_factory=list)  # inequality (>= 0, abs of .m)
    piL: list[str] = field(default_factory=list)  # lower-bound multipliers
    piU: list[str] = field(default_factory=list)  # upper-bound multipliers

    @property
    def total(self) -> int:
        return len(self.nu) + len(self.lam) + len(self.piL) + len(self.piU)

    @property
    def is_empty(self) -> bool:
        return self.total == 0

    def summary(self) -> str:
        return (
            f"nu={len(self.nu)} lam={len(self.lam)} "
            f"piL={len(self.piL)} piU={len(self.piU)} (total {self.total})"
        )


def extract_dual_transfer(mcp_presolve_text: str) -> DualTransfer:
    """Extract the multiplier warm-start statements from a ``--nlp-presolve`` emit.

    Pure string parse (no GAMS): scans for ``nu_*.l = … ;`` / ``lam_*.l = … ;`` /
    ``piL_*.l = … ;`` / ``piU_*.l = … ;`` assignments. This is the harness's
    dual-transfer *verification* layer under Architecture A — it confirms the
    production transfer is present (an empty result is a flag, cf. cesam's empty
    ``nu_*`` block found at Day 0).
    """
    transfer = DualTransfer()
    bucket = {
        "nu": transfer.nu,
        "lam": transfer.lam,
        "piL": transfer.piL,
        "piU": transfer.piU,
    }
    for raw in mcp_presolve_text.splitlines():
        line = raw.strip()
        m = _MULT_RE.match(line)
        if m is not None:
            bucket[m.group(1)].append(line)
    return transfer


def make_residual_only(mcp_text: str, model_name: str = MCP_MODEL_NAME) -> str:
    """Rewrite the emitted MCP so PATH evaluates residuals at the warm-start point
    without iterating: insert ``<model>.iterlim = 0;`` immediately before the
    ``Solve <model> using MCP;`` statement.

    ``iterlim = 0`` makes PATH report the system value at the start point (the
    transferred NLP KKT point) rather than solving — the residual-only evaluation
    the Case-(a/b/c) verdict reads. Raises ``ValueError`` if the Solve isn't found.
    """
    solve_re = re.compile(
        rf"^([ \t]*)Solve\s+{re.escape(model_name)}\s+using\s+MCP\s*;",
        re.IGNORECASE | re.MULTILINE,
    )

    def repl(match: re.Match[str]) -> str:
        indent = match.group(1)
        return f"{indent}{model_name}.iterlim = 0;\n{match.group(0)}"

    new_text, n = solve_re.subn(repl, mcp_text)
    if n == 0:
        raise ValueError(
            f"no `Solve {model_name} using MCP;` statement found to rewrite "
            "for residual-only (iterlim=0) evaluation"
        )
    return new_text


def classify_consistency(
    constraint_residuals: dict[str, float], tol: float = TOL_DEFAULT
) -> str | None:
    """Dual-transfer consistency self-check (design §2).

    The transferred NLP solution already satisfies primal feasibility +
    complementary slackness, so every *constraint*/*complementarity* row must be
    ``≈ 0`` at the warm-start point. If any exceeds ``tol`` the *transfer* is
    wrong (not the emit): return ``"dual_transfer_inconsistent"`` so a bad
    transfer never masquerades as a Case-b emit bug. Returns ``None`` when the
    self-check passes (the stationarity verdict may proceed).
    """
    offending = {k: v for k, v in constraint_residuals.items() if abs(v) > tol}
    return "dual_transfer_inconsistent" if offending else None


def emit_warmstarted_mcp(model_path: Path, out_path: Path) -> dict[str, object]:
    """Emit the MCP with ``--nlp-presolve`` (primal + dual warm-start) via the
    production emit path — Architecture A reuse. Returns the translate result
    dict (``status``/``output_file``/``error``).
    """
    from scripts.gamslib.batch_translate import translate_single_model

    return translate_single_model(model_path, out_path, nlp_presolve=True)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kkt_residual.py",
        description=(
            "KKT-residual verification harness (Sprint 28 Priority 9 / PR27): "
            "warm-start the MCP from the NLP KKT point and evaluate per-row "
            "residuals to classify Case (a) healthy / (b) emit bug / (c) "
            "non-convexity."
        ),
    )
    parser.add_argument("model", help="source NLP model (.gms) the pipeline translates")
    parser.add_argument(
        "--gdx",
        metavar="SOLUTION.gdx",
        help="pre-solved NLP solution (primals + marginals); if omitted, solve the NLP first",
    )
    parser.add_argument(
        "--tol",
        type=float,
        default=None,
        help=f"per-row residual tolerance (Day-2/3 verdict; default {TOL_DEFAULT})",
    )
    parser.add_argument("--json", metavar="OUT.json", help="write the machine-readable report here")
    parser.add_argument(
        "--nlp-solver",
        default=None,
        help=f"NLP solver for the path that solves the NLP when --gdx is not supplied (default {DEFAULT_NLP_SOLVER})",
    )
    parser.add_argument(
        "--no-cold-start",
        action="store_true",
        help="skip the cold-start MCP solve used to split Case a from Case c (residual + Case b/guard only)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    # Day-1 scope is emit + dual-transfer extraction + the residual-only rewrite.
    # The flags that drive the GAMS run / verdict / report are NOT honored yet —
    # fail fast rather than silently ignore them (they land Days 2–3).
    pending = [
        name
        for name, used in (
            ("--gdx", args.gdx is not None),
            ("--json", args.json is not None),
            ("--tol", args.tol is not None),
            ("--nlp-solver", args.nlp_solver is not None),
            ("--no-cold-start", args.no_cold_start),
        )
        if used
    ]
    if pending:
        print(
            "error: the Day-1 build only emits the warm-started MCP + the "
            "residual-only variant; these options are not implemented yet "
            f"(land Days 2–3): {', '.join(pending)}",
            file=sys.stderr,
        )
        return 2

    model_path = Path(args.model)
    if not model_path.exists():
        print(f"error: model not found: {model_path}", file=sys.stderr)
        return 2

    # Write to a scratch directory — never the committed golden dir.
    scratch = Path(tempfile.mkdtemp(prefix=f"kkt_residual_{model_path.stem}_"))
    presolve_path = scratch / f"{model_path.stem}_mcp_presolve.gms"
    print(f"[kkt-residual] {model_path.name} — emitting warm-started MCP (--nlp-presolve)…")
    result = emit_warmstarted_mcp(model_path, presolve_path)
    if result.get("status") != "success":
        err = result.get("error")
        print(f"error: warm-started MCP emit failed: {err}", file=sys.stderr)
        return 1

    mcp_text = presolve_path.read_text(encoding="utf-8")
    transfer = extract_dual_transfer(mcp_text)
    print(f"[kkt-residual] dual transfer (reused from --nlp-presolve): {transfer.summary()}")
    if transfer.is_empty:
        print(
            "[kkt-residual] WARNING: empty dual transfer — the presolve emit produced "
            "no multiplier warm-start; the self-check will gate any verdict.",
            file=sys.stderr,
        )

    # Residual-only variant (iterlim=0) — the input to the Day-2 GAMS evaluation.
    residual_path = scratch / f"{model_path.stem}_mcp_presolve_residual.gms"
    residual_path.write_text(make_residual_only(mcp_text), encoding="utf-8")

    print(f"[kkt-residual] warm-started MCP:  {presolve_path}")
    print(f"[kkt-residual] residual-only MCP: {residual_path}")
    # Days 2–3: run GAMS at iterlim=0 on the residual-only MCP, parse per-row
    # residuals, run the consistency self-check (classify_consistency) + the
    # Case-(a/b/c) verdict, and emit the JSON/human report.
    print(
        "[kkt-residual] Day-1 build: emit + dual-transfer reuse/extraction + "
        "residual-only rewrite + self-check ready. Verdict + run land Days 2–3."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

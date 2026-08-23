#!/usr/bin/env python3
"""Did the MCP actually solve, or did only the embedded NLP?

A ``--nlp-presolve`` emit warm-starts by running the original model inside the
generated file, then solves the MCP and reads the objective back::

    $include "data/gamslib/raw/<model>.gms"   * solves the NLP, sets <objvar>.l
    Solve mcp_model using MCP;                 * if this ABORTS, .l is untouched
    nlp2mcp_obj_val = <objvar>.l;              * still the NLP's own answer

**If the MCP solve aborts, the objective read returns the NLP's own value and
the comparison matches itself.** The recorded status is wrong the same way:
``parse_gams_listing`` takes the *last* ``MODEL STATUS`` in the listing, which
is the NLP's when the MCP produced none.

`weapons` is the discovered instance (Sprint 38 Day 9): one solve summary in the
whole listing (the embedded NLP's, MS-2 @ 1735.5696), the MCP aborted with
``EXECERROR = 1`` — yet the DB recorded ``model_optimal_presolve`` + match at
that same 1735.5696.

**The discriminator is per-solve attribution, not a global grep.** Every status
line in a GAMS listing belongs to the solve summary above it::

                   S O L V E      S U M M A R Y

         MODEL   mcp_model
         TYPE    MCP
         SOLVER  PATH                FROM LINE  1124

    **** SOLVER STATUS     1 Normal Completion
    **** MODEL STATUS      1 Optimal

So the question "did the MCP produce its own MODEL STATUS?" is answered by
finding a summary that is ``TYPE MCP`` **for our emitted model** and which
carries a ``MODEL STATUS`` — see ``EMITTED_MCP_MODEL`` for why the model name
matters and ``TYPE`` alone is not enough.

**Deliberately NOT keyed on ``EXECERROR``.** `check_presolve_divergence.py`'s
first branch treats any execution error as an *embedded-NLP* divergence, which
is how weapons — whose embedded NLP solved perfectly — got reported against the
wrong side. An abort tells you *something* failed, not *which model*.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json"

#: The model name our emitter always uses — verified uniform across all 39
#: committed presolve goldens.
#:
#: **`TYPE MCP` alone is NOT a safe test.** Two raw corpus sources solve an MCP
#: of their own (`cesam.gms`, `spatequ.gms`), and a presolve emit `$include`s the
#: raw source — so their listings carry a `TYPE MCP` summary that is *not* ours.
#: Neither is in the presolve+match population today, but keying on the model
#: name costs nothing and stops the check reading a foreign MCP solve as proof
#: that ours ran.
EMITTED_MCP_MODEL = "mcp_model"

_SUMMARY_HEADER = re.compile(r"^\s+S O L V E {6}S U M M A R Y\s*$", re.MULTILINE)
_MODEL_LINE = re.compile(r"^\s+MODEL\s+(\S+)", re.MULTILINE)
_TYPE_LINE = re.compile(r"^\s+TYPE\s+(\S+)", re.MULTILINE)
_SOLVER_LINE = re.compile(r"^\s+SOLVER\s+(\S+)", re.MULTILINE)
_SOLVER_STATUS = re.compile(r"^\*\*\*\* SOLVER STATUS\s+(\d+)\s*(.*?)$", re.MULTILINE)
_MODEL_STATUS = re.compile(r"^\*\*\*\* MODEL STATUS\s+(\d+)\s*(.*?)$", re.MULTILINE)


@dataclass
class SolveSummary:
    """One ``S O L V E   S U M M A R Y`` block and the statuses beneath it."""

    model: str | None
    type: str | None
    solver: str | None
    solver_status: int | None
    model_status: int | None
    model_status_text: str | None

    @property
    def is_mcp(self) -> bool:
        """An MCP-typed solve — ours or the raw model's own."""
        return (self.type or "").upper() == "MCP"

    @property
    def is_emitted_mcp(self) -> bool:
        """An MCP-typed solve of *our* generated model."""
        return self.is_mcp and self.model == EMITTED_MCP_MODEL


def parse_solve_summaries(lst_content: str) -> list[SolveSummary]:
    """Split a GAMS listing into solve summaries, each owning its status lines.

    Attribution is positional: a status line belongs to the nearest summary
    header *above* it. That is the whole point — a listing-wide search for
    ``MODEL STATUS`` cannot tell you which model produced it.
    """
    starts = [m.start() for m in _SUMMARY_HEADER.finditer(lst_content)]
    summaries: list[SolveSummary] = []

    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(lst_content)
        block = lst_content[start:end]

        # The header fields sit in the first few lines; the statuses follow.
        model = _MODEL_LINE.search(block)
        type_ = _TYPE_LINE.search(block)
        solver = _SOLVER_LINE.search(block)
        sstat = _SOLVER_STATUS.search(block)
        mstat = _MODEL_STATUS.search(block)

        summaries.append(
            SolveSummary(
                model=model.group(1) if model else None,
                type=type_.group(1) if type_ else None,
                solver=solver.group(1) if solver else None,
                solver_status=int(sstat.group(1)) if sstat else None,
                model_status=int(mstat.group(1)) if mstat else None,
                model_status_text=mstat.group(2).strip() if mstat else None,
            )
        )

    return summaries


@dataclass
class Attribution:
    """Whether a listing shows the MCP solving in its own right."""

    model_id: str
    summaries: list[SolveSummary] = field(default_factory=list)
    error: str | None = None

    @property
    def mcp_summaries(self) -> list[SolveSummary]:
        """Solves of *our* emitted MCP — not a raw source's own MCP solve."""
        return [s for s in self.summaries if s.is_emitted_mcp]

    @property
    def foreign_mcp_summaries(self) -> list[SolveSummary]:
        """MCP solves belonging to the included raw model (`cesam`, `spatequ`).

        Surfaced rather than ignored: if one of these ever appears it means the
        listing has an MCP status that must NOT be read as ours.
        """
        return [s for s in self.summaries if s.is_mcp and not s.is_emitted_mcp]

    @property
    def mcp_produced_status(self) -> bool:
        """The discriminator: *our* MCP solve reported a MODEL STATUS."""
        return any(s.model_status is not None for s in self.mcp_summaries)

    @property
    def verdict(self) -> str:
        if self.error:
            return "ERROR"
        if self.mcp_produced_status:
            return "MCP-SOLVED"
        if self.summaries:
            return "NLP-ONLY"
        return "NO-SOLVE"

    def as_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "verdict": self.verdict,
            "mcp_produced_status": self.mcp_produced_status,
            "n_summaries": len(self.summaries),
            "n_mcp_summaries": len(self.mcp_summaries),
            "n_foreign_mcp_summaries": len(self.foreign_mcp_summaries),
            "summaries": [
                {
                    "model": s.model,
                    "type": s.type,
                    "solver": s.solver,
                    "solver_status": s.solver_status,
                    "model_status": s.model_status,
                    "model_status_text": s.model_status_text,
                }
                for s in self.summaries
            ],
            "error": self.error,
        }


def presolve_match_models(db_path: Path = DB_PATH) -> list[str]:
    """Every model recorded ``model_optimal_presolve`` **and** match."""
    db = json.loads(db_path.read_text())
    out = []
    for m in db["models"]:
        solve = m.get("mcp_solve") or {}
        cmp_ = m.get("solution_comparison") or {}
        if (
            solve.get("outcome_category") == "model_optimal_presolve"
            and cmp_.get("comparison_status") == "match"
        ):
            out.append(m["model_id"])
    return sorted(out)


def run_one(model_id: str, workdir: Path, reslim: int = 300) -> Attribution:
    """Emit ``--nlp-presolve`` for one model, run GAMS, and attribute the solves.

    GAMS runs with ``cwd`` at the project root — the emitted
    ``$include "data/gamslib/raw/<id>.gms"`` is repo-relative — while every
    scratch artifact goes to ``workdir``. Never run GAMS *from* the repo root
    without ``ScrDir``: Sprint 37 Day 9 swept the scratch files into a commit.
    """
    raw = PROJECT_ROOT / "data" / "gamslib" / "raw" / f"{model_id}.gms"
    if not raw.exists():
        return Attribution(model_id, error=f"raw source absent: {raw}")

    emitted = workdir / f"{model_id}_mcp_presolve.gms"
    lst = workdir / f"{model_id}.lst"

    emit = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            str(raw.relative_to(PROJECT_ROOT)),
            "--nlp-presolve",
            "-o",
            str(emitted),
        ],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        timeout=600,
    )
    if emit.returncode != 0 or not emitted.exists():
        return Attribution(model_id, error=f"emit failed (rc={emit.returncode})")

    gams = shutil.which("gams")
    if not gams:
        return Attribution(model_id, error="gams executable not found")

    with tempfile.TemporaryDirectory(dir=str(workdir)) as scr:
        try:
            subprocess.run(
                [
                    gams,
                    str(emitted),
                    f"o={lst}",
                    "lo=2",
                    f"reslim={reslim}",
                    f"ScrDir={scr}",
                ],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT),
                timeout=reslim + 120,
            )
        except subprocess.TimeoutExpired:
            return Attribution(model_id, error=f"GAMS timeout after {reslim}s")

    if not lst.exists():
        return Attribution(model_id, error="no listing produced")

    content = lst.read_text(errors="replace")
    return Attribution(model_id, summaries=parse_solve_summaries(content))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--models",
        help="comma-separated model ids (default: every presolve+match row in the DB)",
    )
    ap.add_argument("--workdir", default=None, help="where to keep emits and listings")
    ap.add_argument("--reslim", type=int, default=300)
    ap.add_argument("--json", dest="json_out", help="write the full record here")
    args = ap.parse_args(argv)

    models = (
        [m.strip() for m in args.models.split(",") if m.strip()]
        if args.models
        else presolve_match_models()
    )

    workdir = Path(args.workdir) if args.workdir else Path(tempfile.mkdtemp(prefix="mcp_attr_"))
    workdir.mkdir(parents=True, exist_ok=True)

    results: list[Attribution] = []
    for i, mid in enumerate(models, 1):
        res = run_one(mid, workdir, reslim=args.reslim)
        results.append(res)
        detail = ", ".join(
            f"{s.model}/{s.type}"
            + (f" MS-{s.model_status}" if s.model_status is not None else " (no status)")
            for s in res.summaries
        )
        print(
            f"[{i:>2}/{len(models)}] {mid:<12} {res.verdict:<10} " f"{res.error or detail}",
            flush=True,
        )

    spurious = [r for r in results if r.verdict == "NLP-ONLY"]
    errors = [r for r in results if r.verdict == "ERROR"]

    print()
    print(f"Checked {len(results)} model(s) recorded model_optimal_presolve + match.")
    print(
        f"  MCP produced its own MODEL STATUS : {sum(1 for r in results if r.verdict == 'MCP-SOLVED')}"
    )
    print(f"  ONLY the embedded NLP solved      : {len(spurious)}")
    print(f"  could not be determined           : {len(errors)}")
    if spurious:
        print()
        print("SPURIOUS MATCHES — the recorded objective is the NLP's own value:")
        for r in spurious:
            print(f"  {r.model_id}")

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(
                {
                    "checked": len(results),
                    "spurious": [r.model_id for r in spurious],
                    "errors": [r.model_id for r in errors],
                    "results": [r.as_dict() for r in results],
                },
                indent=2,
            )
        )

    # Exit non-zero only when a determination failed: a spurious match is a
    # FINDING to report, not this script's failure.
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

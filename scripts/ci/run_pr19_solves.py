#!/usr/bin/env python3
"""Run PATH solves for PR19 CI per `DESIGN_PR19_SOLVE_TIME_CI.md` §"PATH Timeout".

Iterates a target list (parsed by ``parse_pr19_targets.py``), invokes::

    cd "$REPO_ROOT"
    gams "data/gamslib/mcp/<model>_mcp.gms" lo=0 reslim=<N> \
      ScrDir=<scratch>/<model> \
      o=<scratch>/<model>/<model>_mcp.lst

per Sprint 25 #1345/#1346/#1347 — `cwd=$REPO_ROOT` + `ScrDir=<tmpdir>` mirrors
``scripts/gamslib/test_solve.py::solve_mcp`` so any presolve-variant MCP's
repo-relative `$include "data/gamslib/raw/<model>.gms"` resolves correctly.

Captures exit code + MODEL STATUS + SOLVER STATUS + wall time per model into a JSON
file. Hard-fail (exit 1) when any model has ``rc != 0``, ``MODEL STATUS != 1``,
or ``SOLVER STATUS != 1``, UNLESS the tier is ``soft-fail`` (Pattern C
informational bucket — always exit 0).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

_MODEL_STATUS = re.compile(
    r"\*\*\*\*\s+MODEL STATUS\s+(?P<code>\d+)\s+(?P<text>.+?)\s*$", re.MULTILINE
)
_SOLVER_STATUS = re.compile(
    r"\*\*\*\*\s+SOLVER STATUS\s+(?P<code>\d+)\s+(?P<text>.+?)\s*$", re.MULTILINE
)


def _read_status(lst_path: Path) -> tuple[str, str]:
    """Parse MODEL STATUS and SOLVER STATUS strings from a GAMS listing file."""
    if not lst_path.is_file():
        return ("n/a (no lst)", "n/a (no lst)")
    text = lst_path.read_text(errors="replace")
    model_match = _MODEL_STATUS.search(text)
    solver_match = _SOLVER_STATUS.search(text)
    model_status = (
        f"{model_match.group('code')} {model_match.group('text')}" if model_match else "n/a"
    )
    solver_status = (
        f"{solver_match.group('code')} {solver_match.group('text')}" if solver_match else "n/a"
    )
    return (model_status, solver_status)


def _solve_one(model: str, repo_root: Path, scratch_base: Path, reslim: int) -> dict:
    mcp_path = repo_root / "data" / "gamslib" / "mcp" / f"{model}_mcp.gms"
    scratch_dir = scratch_base / model
    scratch_dir.mkdir(parents=True, exist_ok=True)
    lst_path = scratch_dir / f"{model}_mcp.lst"
    if not mcp_path.is_file():
        return {
            "model": model,
            "rc": -1,
            "wall_time": 0.0,
            "model_status": "n/a (mcp missing)",
            "solver_status": "n/a (mcp missing)",
            "passed": False,
            "error": f"mcp artifact not found at {mcp_path}",
        }
    start = time.monotonic()
    try:
        completed = subprocess.run(
            [
                "gams",
                str(mcp_path),
                "lo=0",
                f"reslim={reslim}",
                f"ScrDir={scratch_dir}",
                f"o={lst_path}",
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=reslim + 30,
        )
        rc = completed.returncode
    except subprocess.TimeoutExpired:
        rc = 124
    except FileNotFoundError:
        # `gams` not on PATH — common for local smoke tests when the user
        # forgot to source the GAMS env, and possible in CI if the install
        # step's $GITHUB_PATH update didn't propagate. Return a structured
        # record (mirrors the "mcp missing" branch) instead of crashing
        # with a traceback.
        wall_time = round(time.monotonic() - start, 2)
        return {
            "model": model,
            "rc": -1,
            "wall_time": wall_time,
            "model_status": "n/a (gams missing)",
            "solver_status": "n/a (gams missing)",
            "passed": False,
            "error": "`gams` not found on PATH",
        }
    wall_time = round(time.monotonic() - start, 2)
    model_status, solver_status = _read_status(lst_path)
    # Pass requires rc=0 AND MODEL STATUS=1 (Optimal/Solved) AND SOLVER STATUS=1
    # (Normal Completion). MODEL STATUS alone can stay at 1 from a prior
    # iteration even when SOLVER STATUS reports an abnormal termination
    # (e.g., 3 Resource Interrupt, 4 Terminated by Solver), so both are
    # needed to catch all PATH regressions.
    passed = rc == 0 and model_status.startswith("1 ") and solver_status.startswith("1 ")
    return {
        "model": model,
        "rc": rc,
        "wall_time": wall_time,
        "model_status": model_status,
        "solver_status": solver_status,
        "passed": passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", required=True, help="JSON from parse_pr19_targets.py")
    parser.add_argument(
        "--tier",
        required=True,
        choices=["hard-fail", "soft-fail"],
        help=(
            "Which target bucket to solve. hard-fail (tier_0_1) enforces pass/fail "
            "via exit code; soft-fail (pattern_c) always exits 0 — informational "
            "only. Pass/fail enforcement is derived from this flag (no separate "
            "--soft-fail switch — keeps the interface consistent with the bucket "
            "name)."
        ),
    )
    parser.add_argument("--output", required=True, help="Output JSON path for results")
    parser.add_argument("--reslim", type=int, default=30, help="Default per-model PATH timeout (s)")
    parser.add_argument(
        "--scratch-base",
        default="/tmp/pr19-scratch",
        help="Base directory for per-model GAMS scratch files",
    )
    args = parser.parse_args()

    repo_root = Path(
        subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    )
    targets = json.loads(Path(args.targets).read_text())
    bucket = targets["tier_0_1"] if args.tier == "hard-fail" else targets["pattern_c"]
    scratch_base = Path(args.scratch_base)
    scratch_base.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    for entry in bucket:
        per_model_reslim = entry.get("reslim") or args.reslim
        result = _solve_one(entry["model"], repo_root, scratch_base, per_model_reslim)
        results.append(result)
        marker = "✓" if result["passed"] else "✗"
        print(
            f"  {marker} {result['model']:<13} rc={result['rc']} {result['wall_time']:>5.2f}s  "
            f"{result['model_status']}",
            flush=True,
        )

    out = {"tier": args.tier, "results": results}
    Path(args.output).write_text(json.dumps(out, indent=2))

    # Soft-fail tier always exits 0 (informational); hard-fail tier exits 1
    # if any model regressed. Derived from --tier so the two CLI flags can't
    # disagree.
    if args.tier == "soft-fail":
        return 0
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

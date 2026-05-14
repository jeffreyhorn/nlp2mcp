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
file. Hard-fail (exit 1) when any model has ``rc != 0`` or ``MODEL STATUS != 1``,
UNLESS ``--soft-fail`` is set (Pattern C informational tier — always exit 0).
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
    wall_time = round(time.monotonic() - start, 2)
    model_status, solver_status = _read_status(lst_path)
    passed = rc == 0 and model_status.startswith("1 ")
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
        help="Which target bucket to solve: hard-fail (tier_0_1) or soft-fail (pattern_c)",
    )
    parser.add_argument("--output", required=True, help="Output JSON path for results")
    parser.add_argument("--reslim", type=int, default=30, help="Default per-model PATH timeout (s)")
    parser.add_argument(
        "--scratch-base",
        default="/tmp/pr19-scratch",
        help="Base directory for per-model GAMS scratch files",
    )
    parser.add_argument(
        "--soft-fail",
        action="store_true",
        help="Always exit 0; capture results without enforcing pass/fail on this bucket",
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

    if args.soft_fail:
        return 0
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Solve the licensed-tier targets and print a SUMMARY only (``licensed-solve.yml``).

Sprint 40 P1 (``CI_LICENSE_DESIGN.md`` §3). For each target id it runs::

    cd "$REPO_ROOT"
    gams data/gamslib/mcp/<id>_mcp.gms lo=0 reslim=<N> \\
      o=<out>/<id>/<id>_mcp.lst ScrDir=<out>/<id> procDirPath=<temp>

⚠ WHAT IS NEVER PRINTED. A licensed listing's header carries the licensee and
license fields, and a CI log is published. So every GAMS byte goes to files
under ``--out``, and the only things printed or written to the summary are:

* the model id;
* the edition, as classified by the shared parser (``licensed`` / ``demo`` /
  ``unknown``);
* GAMS's exit code;
* the generic ``MODEL STATUS`` / ``SOLVER STATUS`` lines;
* the wall time.

The listings themselves must NEVER be uploaded: they contain the header. The
workflow uploads nothing, and scans only the summary it prints.

Exit codes: 0 = every target ran under the LICENSED edition; 1 = at least one
did not (the license is not effective; a measurement made on the demo would be
meaningless); 2 = bad input. Solve outcomes are reported, not gated: they are
measurements, and P2 owns their interpretation.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.ci.run_pr19_solves import _MODEL_NAME, _read_status  # noqa: E402
from scripts.gamslib.test_solve import extract_license_edition  # noqa: E402


def read_targets(path: Path) -> list[str]:
    """Model ids, one per line; ``#`` comments and blank lines ignored."""
    ids = []
    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if not _MODEL_NAME.match(line):
            raise ValueError(f"invalid model id in {path}: {line!r}")
        ids.append(line)
    return ids


def solve_one(model: str, repo_root: Path, out: Path, reslim: int) -> dict:
    mcp = repo_root / "data" / "gamslib" / "mcp" / f"{model}_mcp.gms"
    if not mcp.is_file():
        return {"model": model, "edition": "unknown", "rc": -1, "error": "golden missing"}
    work = out / model
    work.mkdir(parents=True, exist_ok=True)
    lst = work / f"{model}_mcp.lst"
    # Never let a previous run's listing answer for this one (PR #1762 review).
    # With --out reused, a GAMS that failed to start would leave the OLD
    # licensed listing in place, and it would be classified as this run's.
    lst.unlink(missing_ok=True)
    start = time.monotonic()
    rc: int
    error: str | None = None
    with tempfile.TemporaryDirectory(prefix="gams_procdir_") as procdir:
        try:
            rc = subprocess.run(
                [
                    "gams",
                    str(mcp),
                    "lo=0",
                    f"reslim={reslim}",
                    f"o={lst}",
                    f"ScrDir={work}",
                    f"procDirPath={procdir}",
                ],
                cwd=repo_root,
                capture_output=True,  # captured and DISCARDED: never printed
                text=True,
                timeout=reslim + 60,
                check=False,
            ).returncode
        except subprocess.TimeoutExpired:
            rc, error = 124, f"timeout after {reslim + 60}s"
        except FileNotFoundError:
            rc, error = -1, "`gams` not found on PATH"
    text = lst.read_text(errors="replace") if lst.is_file() else ""
    model_status, solver_status = _read_status(lst)
    result = {
        "model": model,
        "edition": extract_license_edition(text) or "unknown",
        "rc": rc,
        "wall_time": round(time.monotonic() - start, 2),
        "model_status": model_status,
        "solver_status": solver_status,
    }
    if error:
        result["error"] = error
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument(
        "--targets", type=Path, default=PROJECT_ROOT / ".github/licensed-solve-targets.txt"
    )
    ap.add_argument("--out", type=Path, required=True, help="where listings go (NEVER uploaded)")
    ap.add_argument("--summary", type=Path, required=True, help="summary JSON (safe to print)")
    ap.add_argument("--reslim", type=int, default=120)
    args = ap.parse_args(argv)

    try:
        targets = read_targets(args.targets)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not targets:
        print(f"error: no targets in {args.targets}", file=sys.stderr)
        return 2

    args.out.mkdir(parents=True, exist_ok=True)
    results = []
    for model in targets:
        r = solve_one(model, PROJECT_ROOT, args.out, args.reslim)
        results.append(r)
        print(
            f"  {r['model']:<10} edition={r['edition']:<8} rc={r['rc']:<4} "
            f"{r.get('wall_time', 0):>6.2f}s  {r.get('model_status', 'n/a')}",
            flush=True,
        )

    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps({"results": results}, indent=2))

    not_licensed = [r["model"] for r in results if r["edition"] != "licensed"]
    if not_licensed:
        print(f"::error::not run under the licensed edition: {', '.join(not_licensed)}")
        return 1
    print(f"all {len(results)} target(s) ran under the licensed edition")
    return 0


if __name__ == "__main__":
    sys.exit(main())

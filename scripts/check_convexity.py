#!/usr/bin/env python3
"""Computational convexity test via dual KKT comparison.

Generates two MCP files (cold-start and warm-start), solves both with
PATH, and compares objective values.  If both reach STATUS 1 or 2
(Optimal/Locally Optimal) with different objectives, the problem is
provably non-convex.

Usage:
    python scripts/check_convexity.py examples/simple_nlp.gms
    python scripts/check_convexity.py data/gamslib/raw/bearing.gms --timeout 120
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Computational convexity test via dual KKT comparison",
    )
    parser.add_argument("input_file", help="Path to original GAMS NLP model (.gms)")
    parser.add_argument("--timeout", type=int, default=60, help="GAMS solve timeout (default: 60s)")
    parser.add_argument("--keep-files", action="store_true", help="Keep generated MCP files")
    parser.add_argument("--quiet", "-q", action="store_true", help="Only print the conclusion")

    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        return 1

    from scripts.gamslib.batch_translate import translate_single_model
    from src.diagnostics.convexity_numerical import check_convexity_numerical

    tmpdir = tempfile.mkdtemp(prefix="nlp2mcp_convexity_")
    tmp_path = Path(tmpdir)

    try:
        cold_path = tmp_path / "cold_mcp.gms"
        warm_path = tmp_path / "warm_mcp.gms"

        if not args.quiet:
            print(f"Input: {input_path}")
            print(f"Generating cold-start MCP...")

        cold_translate = translate_single_model(input_path, cold_path)
        if cold_translate["status"] != "success":
            print(f"Error: Cold-start translation failed: {cold_translate.get('error')}", file=sys.stderr)
            return 1

        if not args.quiet:
            print(f"Generating warm-start MCP (--nlp-presolve)...")

        warm_translate = translate_single_model(input_path, warm_path, nlp_presolve=True)
        if warm_translate["status"] != "success":
            print(f"Error: Warm-start translation failed: {warm_translate.get('error')}", file=sys.stderr)
            return 1

        if not args.quiet:
            print(f"Solving both MCP files with PATH (timeout={args.timeout}s)...")
            print()

        result = check_convexity_numerical(cold_path, warm_path, timeout=args.timeout)

        if not args.quiet:
            print("Computational Convexity Check:")
            cold_status = f"STATUS {result.status_cold}" if result.status_cold is not None else "no solve"
            warm_status = f"STATUS {result.status_warm}" if result.status_warm is not None else "no solve"
            cold_obj = f"{result.obj_cold:.6g}" if result.obj_cold is not None else "N/A"
            warm_obj = f"{result.obj_warm:.6g}" if result.obj_warm is not None else "N/A"
            print(f"  Cold-start MCP:  {cold_status}, obj = {cold_obj}")
            print(f"  Warm-start MCP:  {warm_status}, obj = {warm_obj}")
            if result.abs_diff is not None:
                print(f"  Difference:      abs={result.abs_diff:.6g}, rel={result.rel_diff:.6g}")
            print()

        if result.is_nonconvex:
            print(f"  NON-CONVEX (proven): {result.conclusion}")
        else:
            print(f"  {result.conclusion}")

        return 0

    finally:
        if not args.keep_files:
            import shutil as sh

            sh.rmtree(tmpdir, ignore_errors=True)
        elif not args.quiet:
            print(f"\nGenerated files kept in: {tmpdir}")


if __name__ == "__main__":
    sys.exit(main())

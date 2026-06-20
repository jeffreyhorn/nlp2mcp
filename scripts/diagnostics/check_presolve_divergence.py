#!/usr/bin/env python3
"""Embedded-NLP-divergence detector (Sprint 28 Priority 10).

Under ``--nlp-presolve`` the emitted MCP ``$include``s the source NLP under
``$onMultiR`` and solves it (the warm-start pre-solve). Because ``$onMultiR``
re-runs the source statements, a non-idempotent statement re-applies, so the
*embedded* NLP can silently diverge from the *standalone* NLP — the bug class
behind #1378 (launch: self-referential param re-applied → obj 2604 vs 2258) and
#1424 (camshape: blanket subset-defaults → embedded infeasible vs 4.2841), and
the korcge #1439 ``it/in`` + ``.fx``-before-``$include`` EXECERROR=5 abort.

The detector compares the embedded NLP objective (the ``nlp2mcp_obj_val`` capture
the presolve emit already writes after the ``$include``) to the standalone NLP
objective, and flags any relative gap > ``--tol`` OR a GAMS abort / non-optimal
embedded solve.

Usage::

    python scripts/diagnostics/check_presolve_divergence.py            # all presolve models; exit 1 on any divergence
    python scripts/diagnostics/check_presolve_divergence.py --model launch
    python scripts/diagnostics/check_presolve_divergence.py --tol 1e-4 --json out.json

Design: ``docs/planning/EPIC_4/SPRINT_28/PRIORITY_10_DIVERGENCE_PROPERTY_TESTS_DESIGN.md``.
Requires the gitignored GAMSLib corpus + a local GAMS/CONOPT.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gamslib.batch_translate import translate_single_model  # noqa: E402
from src.ir.parser import parse_model_file  # noqa: E402
from src.kkt.objective import extract_objective_info  # noqa: E402

RAW_DIR = PROJECT_ROOT / "data" / "gamslib" / "raw"
MCP_DIR = PROJECT_ROOT / "data" / "gamslib" / "mcp"
ALLOWLIST_PATH = Path(__file__).resolve().parent / "presolve_divergence_allowlist.txt"
DEFAULT_TOL = 1e-4


def load_allowlist() -> set[str]:
    if not ALLOWLIST_PATH.exists():
        return set()
    out: set[str] = set()
    for line in ALLOWLIST_PATH.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            out.add(line)
    return out


def _run_gams(gms: Path, scratch_dir: Path) -> tuple[str, int]:
    """Run GAMS on *gms* (lo=2), return (listing_text, returncode).

    Runs with ``cwd=PROJECT_ROOT`` so the presolve emit's
    ``$include "data/gamslib/raw/<model>.gms"`` resolves, while directing the
    listing (``o=``) and GAMS scratch (``ScrDir=``) into *scratch_dir* (a temp
    dir) so the run never litters the repo root.
    """
    lst = scratch_dir / (gms.stem + ".lst")
    proc = subprocess.run(
        ["gams", str(gms), "lo=2", f"o={lst}", f"ScrDir={scratch_dir}"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=300,
    )
    text = lst.read_text(encoding="utf-8", errors="ignore") if lst.exists() else proc.stdout
    return text, proc.returncode


def _parse_var_level(listing: str, var: str) -> float | None:
    """Parse a scalar variable's LEVEL from a ``---- VAR <var>`` row.

    A scalar prints ``---- VAR <name>  <LOWER>  <LEVEL>  <UPPER>  <MARGINAL>``
    where each column is a number, ``.`` (blank), or ``-INF``/``+INF``/``EPS``.
    Parse by COLUMN POSITION (LEVEL is the 2nd) — NOT by filtering the numeric
    tokens, which silently returns UPPER when LOWER is printed as ``.``.
    """
    for line in listing.splitlines():
        ms = re.match(rf"----\s+VAR\s+{re.escape(var)}\b\s+(.*)", line)
        if ms:
            cols = ms.group(1).split()
            if len(cols) >= 2:
                try:
                    return float(cols[1])  # LEVEL
                except ValueError:
                    return None  # '.', 'INF', 'EPS' — level not a finite number
    return None


def _parse_model_status(listing: str) -> int | None:
    m = re.search(r"\*\*\*\* MODEL STATUS\s+(\d+)", listing)
    return int(m.group(1)) if m else None


def _parse_scalar_display(listing: str, name: str) -> float | None:
    """Parse a `Display <scalar>` value (GAMS prints `PARAMETER <name> = <v>`)."""
    m = re.search(rf"{re.escape(name)}\s*=\s*(-?\d+\.?\d*(?:[eE][+-]?\d+)?)", listing)
    return float(m.group(1)) if m else None


def classify_divergence(
    std_obj: float | None,
    emb_obj: float | None,
    execerror: bool,
    tol: float,
) -> tuple[str, str]:
    """Pure comparison logic (unit-testable without GAMS). Returns (status, detail).

    - ``execerror`` (the embedded $include run aborted, e.g. korcge #1439) → diverged.
    - either objective unreadable → indeterminate.
    - relative objective gap > ``tol`` (#1378 launch 2604 vs 2258; #1424
      camshape's infeasible embedded objective ≠ standalone) → diverged.
    """
    if execerror:
        return (
            "diverged",
            "embedded presolve run aborted (EXECERROR) — the $include re-run diverged",
        )
    if std_obj is None or emb_obj is None:
        return (
            "indeterminate",
            f"could not parse objective (standalone={std_obj}, embedded={emb_obj})",
        )
    rel = abs(emb_obj - std_obj) / max(1.0, abs(std_obj))
    if rel > tol:
        return (
            "diverged",
            f"embedded {emb_obj:.6g} vs standalone {std_obj:.6g} (rel {rel:.3g} > tol {tol:g})",
        )
    return "clean", ""


def check_model(model_id: str, tol: float) -> dict:
    raw = RAW_DIR / f"{model_id}.gms"
    rec: dict = {"model": model_id, "status": "clean"}
    if not raw.exists():
        rec["status"] = "skipped"
        rec["detail"] = "raw source absent (gitignored corpus)"
        return rec

    objvar = extract_objective_info(parse_model_file(str(raw))).objvar

    with tempfile.TemporaryDirectory(dir=str(PROJECT_ROOT)) as td:
        wd = Path(td)
        # --- standalone NLP ---
        standalone = wd / f"{model_id}_standalone.gms"
        standalone.write_text(raw.read_text(encoding="utf-8"), encoding="utf-8")
        std_listing, _ = _run_gams(
            standalone, wd
        )  # scratch into the temp dir; cwd=root inside _run_gams
        std_obj = _parse_var_level(std_listing, objvar)
        std_status = _parse_model_status(std_listing)

        # --- embedded NLP (the presolve emit's $include pre-solve) ---
        presolve = wd / f"{model_id}_mcp_presolve.gms"
        tr = translate_single_model(raw, presolve, nlp_presolve=True)
        if tr.get("status") != "success" or not presolve.exists():
            rec["status"] = "emit_failed"
            rec["detail"] = tr.get("error", {}).get("message", "presolve emit failed")[:200]
            return rec
        emb_listing, rc = _run_gams(presolve, wd)
        emb_obj = _parse_scalar_display(emb_listing, "nlp2mcp_obj_val")
        # A non-zero EXECERROR ABORT (korcge #1439 = 5) or a user-error / matrix
        # error means the embedded $include run did NOT complete normally — a
        # divergence from standalone (which solves fine). Note GAMS also prints a
        # benign "(EXECERROR=0) CLEARED" line, so key off the ABORT, not "EXECERROR".
        execerror = bool(
            re.search(r"ABORTED,\s*EXECERROR\s*=\s*[1-9]", emb_listing)
            or "USER ERROR(S) ENCOUNTERED" in emb_listing
            or re.search(r"\*\*\*\* Matrix error", emb_listing)
        )

    rec.update(
        {
            "objvar": objvar,
            "standalone_obj": std_obj,
            "standalone_status": std_status,
            "embedded_obj": emb_obj,
            "tol": tol,
        }
    )
    if std_obj is not None and emb_obj is not None:
        rec["rel_diff"] = abs(emb_obj - std_obj) / max(1.0, abs(std_obj))
    rec["status"], rec["detail"] = classify_divergence(std_obj, emb_obj, execerror, tol)
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description="Embedded-NLP-divergence detector (Priority 10).")
    ap.add_argument("--model", help="check a single model id")
    ap.add_argument(
        "--tol",
        type=float,
        default=DEFAULT_TOL,
        help=f"relative obj tolerance (default {DEFAULT_TOL})",
    )
    ap.add_argument("--json", dest="json_path", help="write a machine-readable report")
    args = ap.parse_args()

    allowlist = load_allowlist()
    if args.model:
        models = [args.model]
    else:
        models = sorted(
            p.name[: -len("_mcp_presolve.gms")] for p in MCP_DIR.glob("*_mcp_presolve.gms")
        )

    results = [check_model(m, args.tol) for m in models]
    diverged = [r for r in results if r["status"] == "diverged" and r["model"] not in allowlist]
    allowlist_warn = [r for r in results if r["status"] == "diverged" and r["model"] in allowlist]
    other = [r for r in results if r["status"] in ("emit_failed", "indeterminate")]

    if args.json_path:
        Path(args.json_path).write_text(
            json.dumps({"results": results}, indent=2), encoding="utf-8"
        )

    print(f"Presolve divergence: checked {len(results)} model(s) (tol {args.tol:g}).")
    for r in allowlist_warn:
        print(f"  WARN allowlisted-but-diverged: {r['model']} — {r.get('detail','')}")
    for r in other:
        print(f"  {r['status'].upper()}: {r['model']} — {r.get('detail','')}")
    for r in diverged:
        print(f"  DIVERGED: {r['model']} — {r.get('detail','')}")
    if not diverged:
        print("  No (non-allowlisted) embedded-NLP divergence.")
        return 0
    print(
        f"  {len(diverged)} model(s) diverged: the embedded $include NLP differs from standalone."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

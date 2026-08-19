#!/usr/bin/env python3
"""Emit the CURRENT pipeline KPI block, derived from the results DB (Sprint 38 P6a).

Why this exists
---------------
Sprint 37's retrospective identified *quoting figures* as a recurring defect
source: a Day-8 prompt sweep corrected six stale figures and was re-staled by
that same sprint's re-baseline **within 24 hours**, and the defect then recurred
twice inside the closeout. The remedy is not more careful copying — it is to
stop copying. Every KPI in a sprint doc should be produced by running this, and
any figure that must be quoted should carry the commit it was measured at.

    python scripts/sprint_audit/kpi_block.py                 # markdown table
    python scripts/sprint_audit/kpi_block.py --format line   # one-line summary
    python scripts/sprint_audit/kpi_block.py --json          # machine-readable

Scope
-----
The headline KPIs are reported over the **convex candidates**, not all 219
models (see ``reference_match_kpi_corpus_scope``). ``all_219_match`` is reported
separately and is the only figure computed over the whole corpus.

The genuine floor is deliberately NOT derived here
--------------------------------------------------
It cannot be. A mechanical ``Match − (presolve ∧ match)`` count yields a number
that looks authoritative and is wrong, because the "cold emit byte-identical to
pre-fix" qualifier lives only in the hand-maintained partition. This tool prints
that mechanical count under an explicit ``NOT the genuine floor`` label so it can
never be mistaken for one, and points at the provenance file (P6c) instead.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json"

#: Convexity statuses that put a model in the candidate corpus the KPIs cover.
CONVEX_STATUSES = frozenset({"verified_convex", "likely_convex"})

#: Outcome categories that count as a solve (the presolve retry counts too).
SOLVED_OUTCOMES = frozenset({"model_optimal", "model_optimal_presolve"})


def _measured_at() -> str:
    """Short SHA of HEAD, or ``unknown`` outside a git checkout.

    Every emitted block carries this: a figure without the commit it was measured
    at is exactly the artifact this tool exists to eliminate.
    """
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            check=True,
        )
        return proc.stdout.strip() or "unknown"
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return "unknown"


def _dirty_db(db_path: Path | None = None) -> bool:
    """True if *db_path* has uncommitted changes — the block would not be reproducible.

    Must be asked about the DB actually read. Checking the default path while
    ``--db`` pointed elsewhere would report the dirtiness of a file that did not
    produce these figures — a false clean (no warning on a dirty alternate DB) or
    a false dirty (warning about an unrelated file).
    """
    target = Path(db_path) if db_path is not None else DATABASE_PATH
    try:
        rel = target.resolve().relative_to(PROJECT_ROOT)
    except ValueError:
        # Outside the repo: git cannot speak to it, so make no claim.
        return False
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "--", str(rel)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            check=True,
        )
        return bool(proc.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return False


def _outcome(model: dict[str, Any]) -> str | None:
    return (model.get("mcp_solve") or {}).get("outcome_category")


def _compare(model: dict[str, Any]) -> str | None:
    return (model.get("solution_comparison") or {}).get("comparison_status")


def compute_kpis(db: dict[str, Any]) -> dict[str, Any]:
    """Derive the KPI block from a loaded results DB.

    Pure: takes the parsed DB, returns the figures. Keyed on ``model_id`` — never
    ``model_name``, which holds the human description.
    """
    models = db.get("models", [])
    candidates = [m for m in models if (m.get("convexity") or {}).get("status") in CONVEX_STATUSES]

    cold_match = sum(
        1 for m in candidates if _compare(m) == "match" and _outcome(m) == "model_optimal"
    )
    presolve_match = sum(
        1 for m in candidates if _compare(m) == "match" and _outcome(m) == "model_optimal_presolve"
    )

    return {
        "candidates": len(candidates),
        "parse": sum(
            1 for m in candidates if (m.get("nlp2mcp_parse") or {}).get("status") == "success"
        ),
        "translate": sum(
            1 for m in candidates if (m.get("nlp2mcp_translate") or {}).get("status") == "success"
        ),
        "solve": sum(1 for m in candidates if _outcome(m) in SOLVED_OUTCOMES),
        "match": sum(1 for m in candidates if _compare(m) == "match"),
        "match_cold": cold_match,
        "match_presolve": presolve_match,
        "model_infeasible": sum(1 for m in candidates if _outcome(m) == "model_infeasible"),
        "path_syntax_error": sum(1 for m in candidates if _outcome(m) == "path_syntax_error"),
        "path_solve_terminated": sum(
            1 for m in candidates if _outcome(m) == "path_solve_terminated"
        ),
        "path_solve_license": sum(1 for m in candidates if _outcome(m) == "path_solve_license"),
        "all_219_match": sum(1 for m in models if _compare(m) == "match"),
        "total_models": len(models),
        # NOT the genuine floor — see the module docstring. Reported so the
        # difference between it and the provenance figure stays visible.
        "mechanical_cold_match_count": cold_match,
    }


def _render_markdown(k: dict[str, Any], sha: str, dirty: bool) -> str:
    rows = [
        ("convex candidates", k["candidates"]),
        ("Parse", k["parse"]),
        ("Translate", k["translate"]),
        ("Solve", k["solve"]),
        ("Match", k["match"]),
        ("&nbsp;&nbsp;cold-optimal", k["match_cold"]),
        ("&nbsp;&nbsp;presolve", k["match_presolve"]),
        ("model_infeasible", k["model_infeasible"]),
        ("path_syntax_error", k["path_syntax_error"]),
        ("path_solve_terminated", k["path_solve_terminated"]),
        ("path_solve_license", k["path_solve_license"]),
        (f"all-{k['total_models']} Match", k["all_219_match"]),
    ]
    out = [f"**KPI block — derived at `{sha}`**", ""]
    if dirty:
        out.append(
            "> ⚠ **The results DB has uncommitted changes.** These figures are NOT "
            "reproducible from `" + sha + "` alone — commit the DB or state that "
            "the block was taken from a dirty tree."
        )
        out.append("")
    out += ["| quantity | value |", "|---|---|"]
    out += [f"| {label} | **{value}** |" for label, value in rows]
    out += [
        "",
        f"*Genuine floor: NOT derivable from the DB. The mechanical "
        f"`Match − (presolve ∧ match)` count is **{k['mechanical_cold_match_count']}**, "
        f"which is **not** the floor — read it from the provenance file (P6c).*",
    ]
    return "\n".join(out)


def _render_line(k: dict[str, Any], sha: str, dirty: bool) -> str:
    line = (
        f"Solve {k['solve']} · Match {k['match']} "
        f"({k['match_cold']} cold + {k['match_presolve']} presolve) · "
        f"Translate {k['translate']} · mi {k['model_infeasible']} · "
        f"pse {k['path_syntax_error']} · all-{k['total_models']} {k['all_219_match']} "
        f"— derived at {sha}"
    )
    return line + ("  [WARNING: DB has uncommitted changes]" if dirty else "")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Emit the current pipeline KPI block, derived from the results DB."
    )
    ap.add_argument(
        "--format",
        choices=("markdown", "line"),
        default="markdown",
        help="output shape (default: markdown table)",
    )
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON instead")
    ap.add_argument(
        "--db",
        default=str(DATABASE_PATH),
        help="path to the results DB (default: data/gamslib/gamslib_status.json)",
    )
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"ERROR: results DB not found at {db_path}", file=sys.stderr)
        return 2
    try:
        db = json.loads(db_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not read results DB at {db_path}: {exc}", file=sys.stderr)
        return 2

    kpis = compute_kpis(db)
    sha = _measured_at()
    dirty = _dirty_db(db_path)

    if args.json:
        print(json.dumps({**kpis, "measured_at": sha, "db_dirty": dirty}, indent=2))
    elif args.format == "line":
        print(_render_line(kpis, sha, dirty))
    else:
        print(_render_markdown(kpis, sha, dirty))
    return 0


if __name__ == "__main__":
    sys.exit(main())

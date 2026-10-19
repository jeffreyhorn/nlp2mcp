#!/usr/bin/env python3
"""Report the genuine floor from its provenance file — never from the DB (P6c).

Why this exists
---------------
The genuine floor is **not derivable** from the results database. A mechanical
``Match − (presolve ∧ match)`` count over the convex candidates yields **65**,
which *looks* authoritative and is wrong: the qualifier that defines the floor —
*"the cold emit is byte-identical to pre-fix, so the match is a methodology
artifact rather than a genuine one"* — exists only in a hand-maintained
partition. Three independent derivations of the historical figure give **65**,
**93** and **76**.

So this tool does the opposite of deriving. It reads a declared baseline plus
one auditable entry per movement:

    floor = baseline.count + len(entries)

and **asserts that total against a committed ``expected_floor``**, exiting
non-zero on divergence. It never computes a floor from the DB, and there is no
flag that makes it do so — that path is the one that produces 65 and looks
authoritative.

**The license-unlocked ledger (Sprint 40 P1, owner Decision 1 = B).** A cold
match that exists only because the full license replaced the demo (the emit
never changed) is NOT genuine. It is recorded in the provenance file's
``license_unlocked`` list and reported BESIDE the floor, never in it:

    floor 75 (+k license-unlocked, not counted)

The ledger takes COLD matches only (``limb: license-unlocked-cold-match``); a
presolve-only match stays under the existing rule and never enters it. A model
may not be in both the floor and the ledger.

    python scripts/sprint_audit/floor_tracker.py            # report + assert
    python scripts/sprint_audit/floor_tracker.py --json     # machine-readable
    python scripts/sprint_audit/floor_tracker.py --show-mechanical
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROVENANCE_PATH = PROJECT_ROOT / "data" / "floor_provenance.json"
DATABASE_PATH = PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json"

CONVEX_STATUSES = frozenset({"verified_convex", "likely_convex"})

#: The only limb the non-counting ledger accepts: COLD matches. A presolve-only
#: match of an unlocked model stays under the existing rule (Decision 1).
LEDGER_LIMB = "license-unlocked-cold-match"


def _measured_at() -> str:
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


def compute_floor(provenance: dict[str, Any]) -> int:
    """``baseline.count + len(entries)`` — the only sanctioned derivation."""
    baseline = provenance.get("baseline") or {}
    count = baseline.get("count")
    if not isinstance(count, int):
        raise ValueError("floor provenance: baseline.count is missing or not an integer")
    entries = provenance.get("entries")
    if not isinstance(entries, list):
        raise ValueError("floor provenance: entries is missing or not a list")
    return count + len(entries)


def license_unlocked(provenance: dict[str, Any]) -> list[dict[str, Any]]:
    """The non-counting ledger. Absent means empty (pre-Sprint-40 files).

    ⚠ Deliberately NOT part of :func:`compute_floor`: the floor is
    ``baseline + entries`` and nothing else, so these never move it.
    """
    ledger = provenance.get("license_unlocked", [])
    if not isinstance(ledger, list):
        raise ValueError("floor provenance: license_unlocked is not a list")
    return ledger


def mechanical_count(db: dict[str, Any]) -> int:
    """The DB-derived count — reported ONLY to show that it is not the floor.

    Kept in the tool on purpose: the number is going to be computed by somebody
    eventually, and it is safer for it to appear here, labelled, than to be
    rediscovered and trusted.
    """
    models = db.get("models")
    if not isinstance(models, list):
        return 0
    total = 0
    for model in models:
        # Type-guarded on purpose. This path is ADVISORY -- it exists only so the
        # DB-derived number appears labelled rather than being rediscovered and
        # trusted. The tracker must stay fail-loud for provenance/floor
        # divergence and nothing else; a malformed DB entry must not take down
        # the floor report it is merely annotating.
        if not isinstance(model, dict):
            continue
        convexity = model.get("convexity")
        if not isinstance(convexity, dict) or convexity.get("status") not in CONVEX_STATUSES:
            continue
        comparison = model.get("solution_comparison")
        if not isinstance(comparison, dict) or comparison.get("comparison_status") != "match":
            continue
        solve = model.get("mcp_solve")
        if isinstance(solve, dict) and solve.get("outcome_category") == "model_optimal_presolve":
            continue
        total += 1
    return total


def validate_entries(provenance: dict[str, Any]) -> list[str]:
    """Structural problems that would make an entry unauditable later."""
    required = ("model_id", "limb", "since_sprint", "evidence")
    problems: list[str] = []
    seen: set[tuple[str, str]] = set()
    for i, entry in enumerate(provenance.get("entries") or []):
        if not isinstance(entry, dict):
            problems.append(f"entry {i}: not an object")
            continue
        for field in required:
            if not entry.get(field):
                problems.append(f"entry {i} ({entry.get('model_id', '?')}): missing {field!r}")
        key = (str(entry.get("model_id")), str(entry.get("limb")))
        if key in seen:
            problems.append(
                f"entry {i}: duplicate ({key[0]}, {key[1]}) — a model counted twice "
                f"inflates the floor silently"
            )
        seen.add(key)

    counted = {
        str(e.get("model_id")) for e in provenance.get("entries") or [] if isinstance(e, dict)
    }
    seen_ledger: set[str] = set()
    ledger = provenance.get("license_unlocked", [])
    for i, entry in enumerate(ledger if isinstance(ledger, list) else []):
        if not isinstance(entry, dict):
            problems.append(f"license_unlocked {i}: not an object")
            continue
        mid = str(entry.get("model_id"))
        for field in required:
            if not entry.get(field):
                problems.append(f"license_unlocked {i} ({mid}): missing {field!r}")
        if entry.get("limb") != LEDGER_LIMB:
            problems.append(
                f"license_unlocked {i} ({mid}): limb {entry.get('limb')!r} is not "
                f"{LEDGER_LIMB!r}. The ledger takes COLD matches only; a presolve-only "
                f"match stays under the existing rule"
            )
        if mid in counted:
            problems.append(
                f"license_unlocked {i} ({mid}): also an `entries` item. A model is either "
                f"fix-driven genuine (counted) or license-unlocked (not counted), never both"
            )
        if mid in seen_ledger:
            problems.append(f"license_unlocked {i} ({mid}): duplicate")
        seen_ledger.add(mid)
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Report the genuine floor from its provenance file (never from the DB)."
    )
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument(
        "--show-mechanical",
        action="store_true",
        help="also print the DB-derived count, labelled as NOT the floor",
    )
    ap.add_argument("--provenance", default=str(PROVENANCE_PATH))
    ap.add_argument("--db", default=str(DATABASE_PATH))
    args = ap.parse_args()

    path = Path(args.provenance)
    if not path.exists():
        print(f"ERROR: floor provenance not found at {path}", file=sys.stderr)
        return 2
    try:
        provenance = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not read floor provenance at {path}: {exc}", file=sys.stderr)
        return 2

    try:
        floor = compute_floor(provenance)
        ledger = license_unlocked(provenance)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    expected = provenance.get("expected_floor")
    problems = validate_entries(provenance)
    baseline = provenance.get("baseline") or {}
    entries = provenance.get("entries") or []

    mech: int | None = None
    if args.show_mechanical:
        db_path = Path(args.db)
        if db_path.exists():
            try:
                mech = mechanical_count(json.loads(db_path.read_text()))
            except (OSError, json.JSONDecodeError, AttributeError, TypeError, ValueError):
                # Advisory only -- report "unavailable" rather than failing the
                # floor assertion this tool actually exists to make.
                mech = None

    diverged = not isinstance(expected, int) or expected != floor
    sha = _measured_at()

    if args.json:
        print(
            json.dumps(
                {
                    "floor": floor,
                    "expected_floor": expected,
                    "baseline_count": baseline.get("count"),
                    "baseline_as_of": baseline.get("as_of"),
                    "entries": len(entries),
                    "license_unlocked_not_counted": len(ledger),
                    "diverged": diverged,
                    "problems": problems,
                    "mechanical_count_NOT_the_floor": mech,
                    "measured_at": sha,
                },
                indent=2,
            )
        )
    else:
        print(
            f"Genuine floor: {floor} (+{len(ledger)} license-unlocked, not counted)"
            f"   (derived at {sha})"
        )
        print(
            f"  = baseline {baseline.get('count')} (as of {baseline.get('as_of')}) "
            f"+ {len(entries)} recorded movement(s)"
        )
        for entry in entries:
            print(
                f"    + {entry.get('model_id')} [{entry.get('limb')}] "
                f"S{entry.get('since_sprint')} — {entry.get('evidence')}"
            )
        for entry in ledger:
            if isinstance(entry, dict):
                print(
                    f"    · {entry.get('model_id')} [{entry.get('limb')}] "
                    f"S{entry.get('since_sprint')} — NOT COUNTED — {entry.get('evidence')}"
                )
        if mech is not None:
            print(
                f"  DB mechanical count: {mech}  <-- NOT the floor. The "
                f"'cold emit byte-identical to pre-fix' qualifier is not in the DB."
            )
        for problem in problems:
            print(f"  PROBLEM: {problem}", file=sys.stderr)
        if diverged:
            print(
                f"  DIVERGENCE: computed {floor} but expected_floor is {expected!r}. "
                f"The tracker reports the committed expectation's failure rather than "
                f"its own number — update expected_floor in the same change that adds "
                f"the entry, so the floor can never move without an explicit edit.",
                file=sys.stderr,
            )

    if problems or diverged:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

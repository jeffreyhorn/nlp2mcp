#!/usr/bin/env python3
"""Validate SPRINT_39/PLAN.md against its own stated figures.

`PLAN.md` claims to be "validated by script". This is that script, committed so
the claim is reproducible from the repo rather than from prose — the same reason
`EPIC_5/artifacts/cge_scan.py` is committed.

⚠ WHY THIS EXISTS AS A FILE. PREP_PLAN's Task-12 Verification block originally
grepped ``^### Day [0-9]+`` headings and parsed ``^\\|\\s*\\d+\\s*\\|`` rows —
neither of which PLAN.md uses. It therefore found **zero** days and **zero**
budget rows, i.e. it verified nothing while looking like a verification
(PR #1723 review). A snippet that drifts from the document it checks is worse
than no snippet, so the checker lives beside the document instead.

Run from the repo root. Every check runs — failures are accumulated and
reported together — and the script exits non-zero if **any** check failed.
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import sys

# artifacts / SPRINT_39 / EPIC_4 / planning / docs / <repo root>  => parents[5]
ROOT = pathlib.Path(__file__).resolve().parents[5]
PLAN = ROOT / "docs/planning/EPIC_4/SPRINT_39/PLAN.md"
PROMPTS = ROOT / "docs/planning/EPIC_4/SPRINT_39/prompts/PLAN_PROMPTS.md"
DB = ROOT / "data/gamslib/gamslib_status.json"

#: A schedule row: | **0** | 2026-09-03 | 6 | **P1** 4h · **baseline** 2h |
ROW = re.compile(r"^\| \*\*(\d+)\*\* \| (\d{4}-\d{2}-\d{2}) \| (\d+) \| (.+) \|$", re.M)
CAP_DAY, CAP_TOTAL = 12, 168
GATE = "2026-09-09"


def main() -> int:
    if not PLAN.is_file():
        # Non-zero: a checker that "passes" without validating anything is the
        # failure mode this whole file exists to remove (PR #1723 review). The
        # caller that legitimately runs before Task 12 — PREP_PLAN's
        # Verification block — guards on the file's existence itself and says
        # so; that context belongs there, not here.
        print(f"ERROR: {PLAN} does not exist — nothing was validated", file=sys.stderr)
        return 2
    plan = PLAN.read_text(encoding="utf-8")
    rows = ROW.findall(plan)
    fail: list[str] = []

    def check(cond: bool, msg: str) -> None:
        print(f"  {'OK  ' if cond else 'FAIL'} {msg}")
        if not cond:
            fail.append(msg)

    check(len(rows) == 14, f"14 schedule rows found ({len(rows)})")
    if rows:
        nums = [int(d) for d, _, _, _ in rows]
        check(nums == list(range(14)), f"days are 0..13 in order ({nums})")
        total = sum(int(h) for _, _, h, _ in rows)
        peak = max(int(h) for _, _, h, _ in rows)
        check(total <= CAP_TOTAL, f"total {total} h <= {CAP_TOTAL} h cap")
        check(peak <= CAP_DAY, f"heaviest day {peak} h <= {CAP_DAY} h")
        check(f"TOTAL **{total} h**" in plan, f"the stated total matches the table ({total} h)")
        check(f"heaviest day **{peak} h**" in plan, f"the stated peak matches the table ({peak} h)")

        # Each row's parts must sum to that row's own total — this only became
        # checkable once the "--" placeholders were named (PR #1723 review).
        for d, _, h, alloc in rows:
            parts = [int(x) for x in re.findall(r"(\d+)h", alloc)]
            check(sum(parts) == int(h), f"Day {d}: parts {parts} sum to {h} h")
            check("--" not in alloc, f"Day {d}: allocation is named, not a placeholder")

        # Dates must be consecutive from Day 0, and the date gate must land on its day.
        d0 = dt.date.fromisoformat(rows[0][1])
        for d, date, _, _ in rows:
            want = (d0 + dt.timedelta(days=int(d))).isoformat()
            check(date == want, f"Day {d} is {want}")
        gate_rows = [d for d, date, _, alloc in rows if date == GATE]
        check(bool(gate_rows), f"the {GATE} date gate appears in the schedule")
        if gate_rows:
            alloc = next(a for d, date, _, a in rows if date == GATE)
            check("**P6**" in alloc, f"{GATE} (Day {gate_rows[0]}) carries P6")

    # Every close rule the acceptance table cites must be defined in §5.
    for rule in sorted(set(re.findall(r"\*\*(C\d)\*\*", plan))):
        check(bool(re.search(rf"^\| \*\*{rule}\*\* \|", plan, re.M)), f"{rule} is defined in the close-rule table")

    # The baseline must match a live KPI derivation, not a recalled figure.
    sys.path.insert(0, str(ROOT / "scripts" / "sprint_audit"))
    try:
        from kpi_block import compute_kpis  # noqa: E402
    finally:
        sys.path.pop(0)
    live = compute_kpis(json.loads(DB.read_text(encoding="utf-8")))
    for label, key in (("Solve", "solve"), ("Match", "match"), ("Translate", "translate")):
        check(f"{label} **{live[key]}**" in plan, f"baseline {label} **{live[key]}** matches the live KPI block")

    if PROMPTS.is_file():
        pr = PROMPTS.read_text(encoding="utf-8")
        check(pr.count("--resolve-changed --since-commit") == 2, "both checkpoints carry a runnable command")
        check("licence" not in pr.lower(), "prompts use the repo's 'license' spelling")

    print(f"\n{'PLAN VALIDATES' if not fail else f'{len(fail)} CHECK(S) FAILED'}")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())

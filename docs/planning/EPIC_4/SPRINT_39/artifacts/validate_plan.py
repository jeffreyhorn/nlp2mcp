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

    # ⚠ PROSE MUST NOT CONTRADICT THE TABLE. Added after the Day-0 re-budget left
    # SEVEN lines of stale prose behind while the table itself was correct —
    # five stale day-ranges, a stale hour total, and two claims C6's change had
    # invalidated. Review flagged three of the seven; a manual grep found two
    # more; these checks found the last two. (Count derived from the diff of
    # 036c8158, not recalled.) The recurring failure mode is that a table edit
    # does not re-read the sentences depending on it (PR #1724 review).
    if rows:
        # 1. Any "<N> h total" in prose must equal the schedule table's total.
        #    Two spellings, each with ONE capture group and unpacked explicitly —
        #    the earlier one-liner reused a loop variable and leant on
        #    isinstance() to tell a tuple from a string (PR #1724 review).
        #    Collected into one set first, so a phrase matching both spellings
        #    is reported once rather than twice.
        TOTAL_FORMS = (
            re.compile(r"\*\*(\d{2,3}) h\*\* total"),        # "**130 h** total"
            re.compile(r"the \*\*?(\d{2,3}) h\*\*? total"),   # "the 130 h total"
        )
        cited_totals = {
            int(m.group(1)) for form in TOTAL_FORMS for m in form.finditer(plan)
        }
        for cited in sorted(cited_totals):
            check(cited == total, f"prose total {cited} h matches the table ({total} h)")
        # 2. A priority's cited day-range must match the days it occupies.
        #    ⚠ DELIBERATELY NARROW. A range can be written either side of its
        #    priority — "P4 — sarf (Days 7-8)" and "**Days 8-12** (P5)" — and
        #    adjacent ranges defeat nearest-token attribution: in
        #    "**Days 8-12** (P5) and **Days 9-13** (P10)" the P10 range is
        #    textually closer to P5. Two unambiguous forms are checked and
        #    everything else is SKIPPED. Under-covering is acceptable here;
        #    mis-attributing is not, because a check that reports a false
        #    failure gets deleted (PR #1724 review).
        occupied = {}
        for prio in {m for m in re.findall(r"\*\*(P\d+)\*\*", plan)}:
            days = sorted(int(d) for d, _, _, alloc in rows if f"**{prio}**" in alloc)
            if days:
                occupied[prio] = (days[0], days[-1])
        cited: set[tuple[str, int, int]] = set()
        claimed: set[int] = set()          # offsets of ranges form (a) owns
        # (a) trailing: "**Days 8-12** (P5)" — the parenthesised priority wins,
        #     and claims that range so (b) cannot also reach across it.
        for m in re.finditer(r"Days (\d+)[–-](\d+)\*{0,2}\s*\((P\d+)\)", plan):
            cited.add((m.group(3), int(m.group(1)), int(m.group(2))))
            claimed.add(m.start())
        # (b) leading: "P4 — sarf (Days 7-8)" — nothing but punctuation between.
        for m in re.finditer(r"\b(P\d+)\b[^|\n\d]{0,24}?(Days (\d+)[–-](\d+))", plan):
            if m.start(2) in claimed:      # already owned by a trailing form
                continue
            cited.add((m.group(1), int(m.group(3)), int(m.group(4))))
        for prio, a, b in sorted(cited):
            if prio in occupied:
                check((a, b) == occupied[prio],
                      f"{prio}: cited range Days {a}-{b} matches its schedule rows "
                      f"{occupied[prio][0]}-{occupied[prio][1]}")

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

        # ⚠ THE PROMPTS MUST AGREE WITH THE TABLE. Added after the Day-0
        # re-budget (P4 26 h -> 11 h under branch B) updated PLAN.md and left
        # PLAN_PROMPTS.md untouched: FIVE headings drifted, and the Days 7-9
        # BODY still instructed the reader to execute branch A — 26 h of
        # implementation the same decision had removed. PLAN.md validated
        # cleanly throughout, because nothing compared the two files.
        #
        # Same class as the stale-prose checks above: a cascade renumbers
        # labels, it does not re-read CONTENT. (Five derived from the diff of
        # this commit, not recalled.)
        #
        # ⚠ DELIBERATELY NARROW, for the reason the day-range check above is:
        # only a `P<n>` token carrying its own hour figure is compared. Labels
        # without a priority number (`Checkpoint 1`, `baseline`,
        # `retest and close`) are SKIPPED — under-covering is acceptable here,
        # mis-attributing is not. `[^·]*` cannot cross a separator, so each
        # figure binds to the priority it actually follows.
        per_day: dict[int, dict[str, int]] = {}
        for day, _date, _tot, parts in rows:
            acc: dict[str, int] = {}
            for prio, hrs in re.findall(r"\*\*(P\d+)\*\* (\d+)h", parts):
                acc[prio] = acc.get(prio, 0) + int(hrs)
            per_day[int(day)] = acc

        headings = re.findall(r"^## Days? (\d+)(?:[–-](\d+))? \(.*?\) — (.+)$", pr, re.M)
        # ⚠ DERIVED, NOT HARDCODED. This read `== 8` when the prompts grouped
        # days into eight track-blocks — which both froze a departure from the
        # per-day convention S36/S37/S38 all follow (14 headings each), and
        # would have failed for the wrong reason the moment the file was split.
        # A guard that exists to catch a human forgetting to update something
        # must DERIVE the value (PR #1711). One heading per scheduled day.
        # ⚠ A LIST, NOT A SET. Built as a set this silently tolerated a
        # DUPLICATE day heading — two "## Day 0" sections collapse to one
        # element, `covered` still reads 0..13, and the check passes on a
        # structurally broken file (PR #1727 review). As a sorted list the same
        # single comparison catches all four ways the mapping can break:
        # a missing day, a duplicated day, an out-of-range day, and (with the
        # range rule below) a regrouping. Deriving the count separately would
        # be a second check saying the same thing.
        covered = sorted(d for lo, hi, _ in headings for d in range(int(lo), int(hi or lo) + 1))
        check(
            covered == list(range(len(rows))),
            f"exactly one prompt heading per scheduled day "
            f"({len(headings)} headings for {len(rows)} days; covered {covered})",
        )
        # ⚠ ONE HEADING PER DAY — the convention S36/S37/S38 all follow (14
        # headings each). S39 shipped eight track-grouped headings instead, and
        # that grouping is what let Days 2-3 carry NO P2 instruction at all
        # while their hours drifted unnoticed: a range heading's figures are
        # checked against the span TOTAL, so per-day drift inside the span is
        # invisible. Verified: regrouping days 2-3 back into one range passes
        # every other check in this file. Hence an explicit structural rule.
        grouped = [(lo, hi) for lo, hi, _ in headings if hi]
        check(not grouped, f"each prompt heading covers exactly one day (grouped: {grouped})")
        for lo, hi, tail in headings:
            span = range(int(lo), int(hi or lo) + 1)
            table: dict[str, int] = {}
            for d in span:
                for prio, hrs in per_day.get(d, {}).items():
                    table[prio] = table.get(prio, 0) + hrs
            label = f"Day{'s' if hi else ''} {lo}{'–' + hi if hi else ''}"
            cited = {p: int(h) for p, h in re.findall(r"(P\d+)[^·]*· (\d+) h", tail)}
            for prio, hrs in sorted(cited.items()):
                check(
                    table.get(prio) == hrs,
                    f"{label} heading cites {prio} {hrs} h; table has {table.get(prio, 0)} h",
                )
            # A priority the table places in the span must not be omitted from
            # the heading — how P5 (8 h) and P10 (5 h) went missing entirely.
            for prio in sorted(set(table) - set(cited)):
                check(False, f"{label} heading omits {prio} ({table[prio]} h in the table)")

    print(f"\n{'PLAN VALIDATES' if not fail else f'{len(fail)} CHECK(S) FAILED'}")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())

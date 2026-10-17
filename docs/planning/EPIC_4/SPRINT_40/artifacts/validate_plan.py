#!/usr/bin/env python3
"""Validate SPRINT_40/PLAN.md and its prompts against their own stated figures.

The schedule validates rather than asserts. This is Sprint 39's validator
(``../../SPRINT_39/artifacts/validate_plan.py``), carried forward with every
check that caught a real defect there, plus the checks Sprint 40's fixed points
need:

* P1 occupies Days 0-1 and nothing license-dependent (P2, P3, RT) runs before
  Day 2; RT is the first block of its day.
* P4 starts after P2 ends (egypt/shale need their licensed solves).
* P9 (the KPI-visible P9a relabel) runs after Checkpoint 2.
* Checkpoints sit on Days 5 and 10; ``close`` sits on Day 13.
* The unknown tally and the refutation rate are DERIVED from
  ``KNOWN_UNKNOWNS.md``, and every unknown id is routed in PLAN.md section 8.
* The nightly-slot figure is the one Task 7 measured.

Run from anywhere. Every check runs, failures are accumulated, and the script
exits non-zero if any check failed. It exits 2 if PLAN.md does not exist: a
checker that "passes" without validating anything is the failure mode this file
exists to remove (Sprint 39, PR #1723).
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import sys

# artifacts / SPRINT_40 / EPIC_4 / planning / docs / <repo root>  => parents[5]
ROOT = pathlib.Path(__file__).resolve().parents[5]
SPRINT = ROOT / "docs/planning/EPIC_4/SPRINT_40"
PLAN = SPRINT / "PLAN.md"
PROMPTS = SPRINT / "prompts/PLAN_PROMPTS.md"
UNKNOWNS = SPRINT / "KNOWN_UNKNOWNS.md"
DRY_RUN = SPRINT / "COHORT_DRY_RUN.md"
DB = ROOT / "data/gamslib/gamslib_status.json"

#: A schedule row: | **0** | 2026-10-18 | 10 | **baseline** 2h · **P1** 8h |
ROW = re.compile(r"^\| \*\*(\d+)\*\* \| (\d{4}-\d{2}-\d{2}) \| (\d+) \| (.+) \|$", re.M)
#: One allocation part: **P1** 8h, **RT** 3h, **close** 6h.
PART = re.compile(r"\*\*([A-Za-z]+\d*)\*\* (\d+)h")
CAP_DAY, CAP_TOTAL = 12, 168
ANCHOR = "bd2af6e9"
ANSWERS = "b44344a2"
#: Labels that need the license toolchain P1 delivers.
LICENSED = ("P2", "P3", "RT")
#: Every label the schedule must carry. Checked as a SET before any ordering
#: check: an ordering check over a label that is absent (or mistyped, e.g.
#: P40 for P4) has nothing to compare and silently passes (PR #1759 review).
REQUIRED_LABELS = {f"P{i}" for i in range(1, 11)} | {"RT", "CK", "baseline", "close"}
STATUS = {"✅": "verified", "❌": "wrong", "🔶": "partial", "🔍": "incomplete"}


def _days(rows: list[tuple[str, str, str, str]], label: str) -> list[int]:
    return sorted(int(d) for d, _, _, alloc in rows if f"**{label}**" in alloc)


def main() -> int:
    if not PLAN.is_file():
        print(f"ERROR: {PLAN} does not exist; nothing was validated", file=sys.stderr)
        return 2
    plan = PLAN.read_text(encoding="utf-8")
    rows = ROW.findall(plan)
    fail: list[str] = []

    def check(cond: bool, msg: str) -> None:
        print(f"  {'OK  ' if cond else 'FAIL'} {msg}")
        if not cond:
            fail.append(msg)

    # ---------------------------------------------------------------- schedule
    check(len(rows) == 14, f"14 schedule rows found ({len(rows)})")
    total = peak = 0
    if rows:
        nums = [int(d) for d, _, _, _ in rows]
        check(nums == list(range(14)), f"days are 0..13 in order ({nums})")
        total = sum(int(h) for _, _, h, _ in rows)
        peak = max(int(h) for _, _, h, _ in rows)
        check(total <= CAP_TOTAL, f"total {total} h <= {CAP_TOTAL} h cap")
        check(peak <= CAP_DAY, f"heaviest day {peak} h <= {CAP_DAY} h")
        check(f"TOTAL **{total} h**" in plan, f"the stated total matches the table ({total} h)")
        check(f"heaviest day **{peak} h**" in plan, f"the stated peak matches the table ({peak} h)")

        for d, _, h, alloc in rows:
            parts = [int(x) for _, x in PART.findall(alloc)]
            check(sum(parts) == int(h), f"Day {d}: parts {parts} sum to {h} h")
            # Every part must be a recognised token, so a typo cannot hide hours.
            leftover = PART.sub("", alloc).replace("·", "").strip()
            check(not leftover, f"Day {d}: allocation fully parsed (leftover {leftover!r})")

        d0 = dt.date.fromisoformat(rows[0][1])
        for d, date, _, _ in rows:
            want = (d0 + dt.timedelta(days=int(d))).isoformat()
            check(date == want, f"Day {d} is {want}")

        # ------------------------------------------------------- fixed points
        labels = {lbl for _, _, _, alloc in rows for lbl, _ in PART.findall(alloc)}
        check(
            labels == REQUIRED_LABELS,
            f"the schedule carries exactly the required labels "
            f"(missing {sorted(REQUIRED_LABELS - labels)}, unknown {sorted(labels - REQUIRED_LABELS)})",
        )
        p1 = _days(rows, "P1")
        check(p1 == [0, 1], f"P1 occupies exactly Days 0-1 ({p1})")
        for label in LICENSED:
            days = _days(rows, label)
            check(bool(days), f"{label} is scheduled")
            if days:
                check(days[0] >= 2, f"{label} starts after P1 (first day {days[0]})")
        rt = _days(rows, "RT")
        if rt:
            first_licensed = min(min(_days(rows, lbl) or [99]) for lbl in ("P2", "P3"))
            check(
                rt[0] <= first_licensed,
                f"RT (Day {rt[0]}) is no later than P2/P3 (Day {first_licensed})",
            )
            alloc = next(a for d, _, _, a in rows if int(d) == rt[0])
            check(alloc.lstrip().startswith("**RT**"), f"RT is the first block of Day {rt[0]}")
        p2, p4 = _days(rows, "P2"), _days(rows, "P4")
        if p2 and p4:
            check(p4[0] > p2[-1], f"P4 (from Day {p4[0]}) starts after P2 ends (Day {p2[-1]})")
        ck = _days(rows, "CK")
        check(ck == [5, 10], f"checkpoints on Days 5 and 10 ({ck})")
        p9 = _days(rows, "P9")
        if p9 and ck:
            check(p9[0] > ck[-1], f"P9 (the P9a relabel) runs after Checkpoint 2 ({p9})")
        check(_days(rows, "close") == [13], "close is on Day 13")
        check(_days(rows, "baseline") == [0], "baseline is on Day 0")
        if ck:
            alloc = next(a for d, _, _, a in rows if int(d) == ck[-1])
            check(alloc.lstrip().startswith("**CK**"), "Checkpoint 2 is the first block of its day")

        # ------------------------------------------- prose vs table (from S39)
        for form in (
            re.compile(r"\*\*(\d{2,3}) h\*\* total"),
            re.compile(r"the \*\*?(\d{2,3}) h\*\*? total"),
        ):
            for m in form.finditer(plan):
                check(
                    int(m.group(1)) == total,
                    f"prose total {m.group(1)} h matches the table ({total} h)",
                )
        occupied = {}
        for prio in set(re.findall(r"\*\*(P\d+)\*\*", plan)):
            days = _days(rows, prio)
            if days:
                occupied[prio] = (days[0], days[-1])
        cited: set[tuple[str, int, int]] = set()
        claimed: set[int] = set()
        for m in re.finditer(r"Days (\d+)[–-](\d+)\*{0,2}\s*\((P\d+)\)", plan):
            cited.add((m.group(3), int(m.group(1)), int(m.group(2))))
            claimed.add(m.start())
        for m in re.finditer(r"\b(P\d+)\b[^|\n\d]{0,24}?(Days (\d+)[–-](\d+))", plan):
            if m.start(2) in claimed:
                continue
            cited.add((m.group(1), int(m.group(3)), int(m.group(4))))
        for prio, a, b in sorted(cited):
            if prio in occupied:
                check(
                    (a, b) == occupied[prio],
                    f"{prio}: cited range Days {a}-{b} matches its schedule rows "
                    f"{occupied[prio][0]}-{occupied[prio][1]}",
                )

    # ------------------------------------- budget table vs the schedule
    # Each priority's SCHEDULED column must equal the sum of its allocations,
    # with exactly one row per priority. A P4 budget of "160 h" passed every
    # other check, because nothing read this column (PR #1759 review).
    if rows:
        budget = plan.split("### Budget against", 1)[-1].split("\n\n**", 1)[0]
        sums: dict[str, int] = {}
        for _, _, _, alloc in rows:
            for lbl, hrs in PART.findall(alloc):
                sums[lbl] = sums.get(lbl, 0) + int(hrs)
        groups: dict[str, tuple[str, ...]] = {f"P{i}": (f"P{i}",) for i in range(1, 11)}
        groups |= {"retest": ("RT", "close"), "checkpoints": ("CK",), "baseline": ("baseline",)}
        seen: dict[str, list[int]] = {}
        for first, hrs in re.findall(r"^\| ([^|]+?) \| (\d+) h \|", budget, re.M):
            m_p = re.match(r"(P\d+)\b", first)
            if m_p:
                key = m_p.group(1)
            elif "retest" in first:
                key = "retest"
            elif "checkpoint" in first:
                key = "checkpoints"
            elif "baseline" in first:
                key = "baseline"
            else:
                check(False, f"budget row {first!r} maps to no schedule label")
                continue
            seen.setdefault(key, []).append(int(hrs))
        for key, members in groups.items():
            want_h = sum(sums.get(lbl, 0) for lbl in members)
            got = seen.get(key, [])
            check(
                got == [want_h],
                f"budget table: exactly one {key} row, scheduled {want_h} h (found {got})",
            )

    # ------------------------------------------------------------ close rules
    for rule in sorted(set(re.findall(r"\*\*(C\d+)\*\*", plan)), key=lambda r: int(r[1:])):
        check(
            bool(re.search(rf"^\| \*\*{rule}\*\* \|", plan, re.M)),
            f"{rule} is defined in the close-rule table",
        )
    defined = re.findall(r"^\| \*\*(C\d+)\*\* \| .+? \| (.+?) \| .+ \|$", plan, re.M)
    none = [c for c, pre in defined if pre.startswith("**none**")]
    check(
        bool(none) and len(none) < len(defined),
        f"some, not all, close rules take no precondition ({len(none)} of {len(defined)})",
    )
    phrase = f"**{_word(len(none)).capitalize()} of {_word(len(defined))} take no precondition**"
    check(phrase in plan, f"the stated no-precondition count matches the table ({phrase})")

    # --------------------------------------------------------- fixed inputs
    check(ANSWERS in plan, f"the owner-answers commit {ANSWERS} is cited")
    check(f"--since-commit {ANCHOR}" in plan, f"checkpoints anchor to {ANCHOR}")

    # ------------------------------------------------ baseline vs live KPIs
    sys.path.insert(0, str(ROOT / "scripts" / "sprint_audit"))
    try:
        from kpi_block import compute_kpis  # type: ignore[import-not-found]  # noqa: E402
    finally:
        sys.path.pop(0)
    live = compute_kpis(json.loads(DB.read_text(encoding="utf-8")))
    for label, key in (("Solve", "solve"), ("Match", "match"), ("Translate", "translate")):
        check(
            f"{label} **{live[key]}**" in plan,
            f"baseline {label} **{live[key]}** matches the live KPI block",
        )
    check(
        f"`path_solve_license` **{live['path_solve_license']}**" in plan,
        f"baseline path_solve_license {live['path_solve_license']} matches the live KPI block",
    )

    # ------------------------------------- unknowns: tally, rate, routing
    ku = UNKNOWNS.read_text(encoding="utf-8")
    status: dict[str, str] = {}
    current = None
    for line in ku.splitlines():
        head = re.match(r"^## Unknown (\d+\.\d+):", line)
        if head:
            current = head.group(1)
            continue
        mark = re.match(r"^(✅|❌|🔶|🔍) \*\*Status", line)
        if mark and current and current not in status:
            status[current] = STATUS[mark.group(1)]
    counts = {k: sum(1 for v in status.values() if v == k) for k in STATUS.values()}
    n = len(status)
    tally = (
        f"{counts['verified']} ✅ · {counts['wrong']} ❌ · {counts['partial']} 🔶, "
        f"plus {counts['incomplete']} 🔍 routed"
    )
    check(tally in plan, f"the unknown tally is derived ({tally})")
    # The resolved NUMERATOR as well as the emoji breakdown: "28 of 29 were
    # resolved" edited to "27 of 29" left the breakdown intact and passed
    # (PR #1759 review). Every such phrase must equal the derived count.
    resolved = counts["verified"] + counts["wrong"] + counts["partial"]
    stated = re.findall(r"(\d+) of (\d+) unknowns (?:were|are) resolved", plan)
    check(bool(stated), "PLAN.md states how many unknowns were resolved")
    for got_r, got_n in stated:
        check(
            (int(got_r), int(got_n)) == (resolved, n),
            f"stated resolved count {got_r} of {got_n} is the derived {resolved} of {n}",
        )
    refuted = counts["wrong"] + counts["partial"]
    check(
        f"**{refuted} of {n} assumptions were refuted or partially refuted**" in plan,
        f"the refutation count is derived ({refuted} of {n})",
    )
    pct = round(100 * refuted / n)
    check(f"**{pct} %** refutation rate" in plan, f"the refutation rate is derived ({pct} %)")
    section8 = plan.split("## 8.", 1)[-1].split("## 9.", 1)[0]
    routed: set[str] = set()
    for cell in re.findall(r"^\| ([0-9.,–\- ]+) \|", section8, re.M):
        for part in cell.split(","):
            part = part.strip()
            span = re.fullmatch(r"(\d+)\.(\d+)[–-](\d+)\.(\d+)", part)
            if span and span.group(1) == span.group(3):
                lo, hi = int(span.group(2)), int(span.group(4))
                routed |= {f"{span.group(1)}.{i}" for i in range(lo, hi + 1)}
            elif re.fullmatch(r"\d+\.\d+", part):
                routed.add(part)
    check(
        set(status) <= routed,
        f"every unknown is routed in section 8 (missing {sorted(set(status) - routed)})",
    )
    check(
        routed <= set(status),
        f"section 8 routes no unknown that does not exist ({sorted(routed - set(status))})",
    )

    # ------------------------------------------------- Task 7's nightly figure
    wall = re.search(r"takes ([\d,]+) s", DRY_RUN.read_text(encoding="utf-8"))
    check(bool(wall), "COHORT_DRY_RUN.md states the whole-pipeline wall-clock")
    if wall:
        # EVERY cited wall-clock figure, not "at least one": the plan states it
        # twice, so an `in` test passed with one copy stale (mutation control).
        # Both spellings, grouped or not, normalised before comparing: a regex
        # for "2,162" alone let an ungrouped stale "2163" escape (PR #1759
        # review). Any bold "**N s**" in PLAN.md is read as this figure.
        want_s = int(wall.group(1).replace(",", ""))
        cited_s = [int(x.replace(",", "")) for x in re.findall(r"\*\*(\d[\d,]*) s\*\*", plan)]
        check(
            bool(cited_s) and set(cited_s) == {want_s},
            f"every cited nightly-slot figure is Task 7's {want_s} s ({cited_s})",
        )

    # ------------------------------------------------------------- prompts
    if not PROMPTS.is_file():
        check(False, f"{PROMPTS.name} exists")
    else:
        pr = PROMPTS.read_text(encoding="utf-8")
        # Each checkpoint is two commands: the dry run that DISCOVERS the model
        # count, then the run that ASSERTS it. A file count is the wrong <N>:
        # the resolver dedupes cold + presolve goldens (PR #1759 review).
        check(
            pr.count("--resolve-changed --since-commit") == 4,
            "both checkpoints carry a discovery and an asserted command (4)",
        )
        check(
            pr.count(f"--resolve-changed --since-commit {ANCHOR} --min-scope <N>") == 2,
            f"both asserted checkpoints anchor to {ANCHOR} with --min-scope",
        )
        check(
            pr.count(f"--resolve-changed --since-commit {ANCHOR} \\\n  --dry-run --json") == 2,
            "both checkpoints discover <N> from the resolver's dry-run model count",
        )
        check(
            not re.search(r"git diff --name-only[^\n`]*\|\s*wc -l", pr),
            "no checkpoint derives <N> from a file count",
        )
        check(
            "licence" not in pr.lower() and "licence" not in plan.lower(),
            "the repo's 'license' spelling",
        )
        for anchor, why in (
            ('grep -qE "Co-Authored-By|Generated with"', "the no-attribution grep"),
            ("The PR body is a pointer", "PR body as a pointer"),
            ("stated once, with the commit", "figures once, with their commit"),
            ("The leak gate runs ALONE", "leak gate alone"),
            ("Never `git stash`", "no git stash"),
            ("Pin by identity, not count", "pin by identity"),
            ("sweep the changed SET", "sweep the changed set"),
            ("License hygiene", "license hygiene"),
        ):
            check(anchor.lower() in pr.lower(), f"prompts embed the standing convention: {why}")

        per_day: dict[int, dict[str, int]] = {}
        for day, _date, _tot, parts in rows:
            acc: dict[str, int] = {}
            for prio, hrs in re.findall(r"\*\*(P\d+)\*\* (\d+)h", parts):
                acc[prio] = acc.get(prio, 0) + int(hrs)
            per_day[int(day)] = acc
        headings = re.findall(
            r"^## Days? (\d+)(?:[–-](\d+))? \((\d{4}-\d{2}-\d{2})\) — (.+)$", pr, re.M
        )
        covered = sorted(d for lo, hi, _, _ in headings for d in range(int(lo), int(hi or lo) + 1))
        check(
            covered == list(range(len(rows))),
            f"exactly one prompt heading per scheduled day ({len(headings)} headings; covered {covered})",
        )
        grouped = [(lo, hi) for lo, hi, _, _ in headings if hi]
        check(not grouped, f"each prompt heading covers exactly one day (grouped: {grouped})")
        dates = {int(d): date for d, date, _, _ in rows}
        for lo, _hi, date, tail in headings:
            d = int(lo)
            check(
                dates.get(d) == date,
                f"Day {d} heading date {date} matches the table ({dates.get(d)})",
            )
            table = per_day.get(d, {})
            cited_h = {p: int(h) for p, h in re.findall(r"(P\d+)[^·]*· (\d+) h", tail)}
            for prio, hrs in sorted(cited_h.items()):
                check(
                    table.get(prio) == hrs,
                    f"Day {d} heading cites {prio} {hrs} h; table has {table.get(prio, 0)} h",
                )
            for prio in sorted(set(table) - set(cited_h)):
                check(False, f"Day {d} heading omits {prio} ({table[prio]} h in the table)")
            hours = sum(int(h) for h in re.findall(r"· (\d+) h", tail))
            row_h = next(int(h) for dd, _, h, _ in rows if int(dd) == d)
            check(hours == row_h, f"Day {d} heading hours sum to {hours} h; table row is {row_h} h")

    print(f"\n{'PLAN VALIDATES' if not fail else f'{len(fail)} CHECK(S) FAILED'}")
    return 1 if fail else 0


def _word(n: int) -> str:
    words = "zero one two three four five six seven eight nine ten eleven twelve".split()
    return words[n] if n < len(words) else str(n)


if __name__ == "__main__":
    raise SystemExit(main())

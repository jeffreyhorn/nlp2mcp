#!/usr/bin/env python3
"""Catch a figure cited in a doc that contradicts the source it came from.

Why this exists
---------------
Every figure in this project's planning docs is *derived* from something — the
results DB, a provenance file, a table of verdicts, a set of headings. The
derivation is cheap. The failure is never the arithmetic; it is that a figure
gets **copied into prose and then goes stale**, while the source it came from
moves on.

Four real instances, all inside a single week of Sprint 39 prep:

* ``29.0`` research hours was published in **five places across four files**,
  labelled *"derived by summing the per-unknown estimates, not recalled"*. The
  sum had been **40.0** since the file's first commit. It was never summed.
* ``12 of 14`` figures reproduced, written into ``CHANGELOG.md`` and a PR body
  while the last measurement was still running. It came back clean, making the
  real count **13**, and neither citation was updated.
* A verification snippet reported ``30`` and ``31`` for the same quantity, two
  lines apart, because one form counted a fenced template and the other didn't.
* Three docs were corrected from ``29.0`` to ``40.0``; ``CHANGELOG.md``, the
  fourth file in the same PR, was not.

The shape is identical every time: **the primary artifact gets fixed and the
derived ones don't.** Review caught two of the four; the other two were found
only by sweeping. That ratio is the argument for a mechanical check.

What it does
------------
For each registered fact it (a) derives the true value by running the same code
the reporting tools run, and (b) scans **added or modified doc lines** for
citations of that fact, and compares.

Only changed lines are scanned, and that is a deliberate design choice rather
than an optimisation. ``CHANGELOG.md`` is full of figures that were correct when
written — *"Solve 108"* is right for Sprint 36 and wrong for today. A whole-file
scan would drown in false positives and be switched off within a week. Touching
a line is what makes its figures current, so touching a line is what puts them
in scope.

What it deliberately does not do
--------------------------------
It does not try to understand prose. A line that *discusses* a wrong figure —
*"the 29.0 h figure published at creation was wrong"* — is a correction, not a
claim, and must not be flagged; those exist precisely because the errors above
were recorded rather than quietly patched. Such lines are exempted by an
explicit marker list, and **every exemption is reported**, because an exemption
set that grows silently is the same class of defect this check exists to catch.
"""

from __future__ import annotations

import argparse
import functools
import json
import re
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# The sibling audit scripts are imported EAGERLY, while this path insert is in
# effect, and bound to module-level names. They were lazy (inside the derive
# functions), which quietly made the module depend on the `sys.path` mutation
# SURVIVING import — so a caller that politely restored `sys.path` afterwards,
# as a dynamic-import test should, got `ModuleNotFoundError: kpi_block` the
# moment a fact derived. Importing here puts them in `sys.modules`, after which
# the path entry is no longer needed by anything.
# `sys.path` is restored WHOLESALE, not just stripped of the entry added here.
# Importing the siblings also runs THEIR path mutations — `check_golden_staleness`
# and its transitive imports contribute three more entries — and leaving any of
# them behind changes import resolution for the rest of the process. That matters
# when this module is imported programmatically rather than run as a script,
# which is exactly how its own tests load it.
#
# Safe because every one of these imports is eager: once they return, the modules
# are in `sys.modules` and nothing downstream resolves through the path again.
# (Checked: no in-function `src.`/`scripts.` imports in the chain.)
_SAVED_SYS_PATH = list(sys.path)
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "sprint_audit"))
try:
    from check_golden_staleness import discover_goldens, load_allowlist  # noqa: E402
    from floor_tracker import compute_floor  # noqa: E402
    from kpi_block import compute_kpis  # noqa: E402
finally:
    sys.path[:] = _SAVED_SYS_PATH

DB_PATH = PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json"
PROVENANCE_PATH = PROJECT_ROOT / "data" / "floor_provenance.json"

#: Only these are scanned. Source files carry figures in tests and fixtures
#: where a literal is the point, not a citation.
DOC_SUFFIXES = (".md",)

#: A line whose *subject* is a wrong or superseded figure. These are corrections
#: and historical records, not live claims, and flagging them would penalise
#: exactly the practice that makes the errors auditable.
#:
#: Kept deliberately short. Each entry is a phrase this repo actually uses when
#: recording a wrong figure — not a general-purpose "sounds historical" list.
_EXEMPT_MARKERS = (
    "was wrong",
    "were wrong",
    "is wrong",
    "was also wrong",
    "wrong at every commit",
    "published at creation",
    "previously published",
    "no longer",
    "historical",
    "pre-fix",
    "superseded",
    "stale",
    "corrected to",
    "re-staled",
    "figures-ok",
)

#: Inline escape hatch, e.g. ``<!-- figures-ok: quoting Sprint 36's close -->``.
_INLINE_EXEMPT = re.compile(r"<!--\s*figures-ok\b")

#: Docs whose figures are supposed to be CURRENT. Everything else in ``docs/`` is
#: an archive: a closed sprint's log saying *"Solve 108"* is correct for that
#: sprint and must not be flagged when the file is touched for an unrelated edit.
#:
#: This matters more than it looks. Scanning every line of every doc — the
#: worst case if scoping were removed — yields **2,376** findings, dominated by
#: archived sprint logs and unrelated "N unknowns" prose. Scoping is what keeps
#: the signal readable, and an unreadable check is a disabled check.
#:
#: The sprint directories live under here.
SPRINT_ROOT = PROJECT_ROOT / "docs" / "planning" / "EPIC_4"


def current_sprint_dir(root: Path | None = None) -> Path | None:
    """The highest-numbered ``SPRINT_<n>`` directory, or ``None`` if there are none.

    **Derived, not declared.** This was a hardcoded ``SPRINT_39`` guarded by a
    test asserting the directory existed — a guard that could never fire, because
    closed sprints are never deleted: all 22 of ``SPRINT_18``…``SPRINT_39`` are
    still present. Leaving the constant at any past sprint satisfied
    ``.is_dir()`` forever while every new-sprint doc silently fell out of scope
    and the check reported PASS.

    That is the precise failure this tool exists to prevent — a check that
    silently narrows — sitting inside the guard written to prevent it. So the
    sprint is now read from the tree, and the only thing left to assert is that
    the derivation agrees with what is on disk.
    """
    root = SPRINT_ROOT if root is None else root
    if not root.is_dir():
        return None
    numbered = [
        (int(m.group(1)), p)
        for p in root.iterdir()
        if p.is_dir() and (m := re.fullmatch(r"SPRINT_(\d+)", p.name))
    ]
    if not numbered:
        return None

    # Keyed on the NUMBER alone. `max()` over the raw tuples falls through to
    # comparing Paths on a tie, which resolves — Paths are orderable — but
    # resolves *arbitrarily*, by lexical order.
    #
    # And a tie is reachable without any filesystem exotica: `SPRINT_39` and
    # `SPRINT_039` are distinct directories that both parse to 39. Two
    # directories claiming one sprint is genuinely ambiguous, and picking one
    # silently is the failure this tool exists to prevent — so it is refused.
    top = max(n for n, _p in numbered)
    claimants = sorted(p.name for n, p in numbered if n == top)
    if len(claimants) > 1:
        raise ValueError(
            f"ambiguous current sprint: {', '.join(claimants)} all parse to {top} "
            f"under {root}. Remove or rename the duplicates — silently choosing "
            "one would scope the doc-figure check to an arbitrary directory."
        )
    return next(p for n, p in numbered if n == top)


#: Docs whose figures are supposed to be CURRENT. Everything else in ``docs/`` is
#: an archive: a closed sprint's log saying *"Solve 108"* is correct for that
#: sprint and must not be flagged when the file is touched for an unrelated edit.
#:
#: This matters more than it looks. Scanning every line of every doc — the
#: worst case if scoping were removed — yields **2,376** findings, dominated by
#: archived sprint logs and unrelated "N unknowns" prose. Scoping is what keeps
#: the signal readable, and an unreadable check is a disabled check.
_STATIC_LIVE_DOC_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^CHANGELOG\.md$"),
    re.compile(r"^docs/planning/EPIC_4/(PROJECT_PLAN|SUMMARY)\.md$"),
)


def is_live_doc(path: Path, sprint_dir: Path | None = None) -> bool:
    """True if ``path``'s figures are expected to be current rather than archival.

    The current sprint is resolved at call time, so a rollover needs no edit
    here and cannot leave the scope pointing at a closed sprint.
    """
    posix = path.as_posix()
    if any(p.search(posix) for p in _STATIC_LIVE_DOC_PATTERNS):
        return True
    sprint = current_sprint_dir() if sprint_dir is None else sprint_dir
    if sprint is None:
        return False
    try:
        rel = sprint.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        rel = sprint.as_posix()
    return posix.startswith(f"{rel}/")


#: A cited number. Never ``[0-9.]+``: that alternation matches a bare ``"."``,
#: which silently captured the dot in ``29.0`` and made the check pass on the
#: exact figure it was written to catch.
NUM = r"\d+(?:\.\d+)?"

#: ``A → B`` states a movement, so the left figure is historical by
#: construction. Such lines are skipped — but reported, never silently.
#:
#: **Digits are required on both sides.** A bare ``->`` also appears in HTML
#: comment terminators (``-->``), Mermaid edges and type hints, and exempting on
#: that alone silently took ordinary prose out of scope — a false negative in a
#: tool whose entire job is to not have any.
_MOVEMENT = re.compile(r"\d\**\s*(?:→|->)\s*\**\d")


@dataclass(frozen=True)
class Fact:
    """One derivable quantity and the ways it is written down."""

    name: str
    derive: Callable[[], float | int]
    #: How to reproduce the derivation by hand. Printed on failure, so a reader
    #: can check the checker rather than trusting it.
    source: str
    #: Each pattern must expose the cited number as group ``value``.
    patterns: tuple[re.Pattern[str], ...]
    #: Lines legitimately about a *different* population. **Regexes, not
    #: substrings.** A substring blocklist is unsound here: an entry ``"or 75"``
    #: added to scope out *"73 or 75"* also matches inside *"**flo**or 75"*, which
    #: silenced the floor check entirely.
    skip_if: tuple[re.Pattern[str], ...] = field(default=())


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- derivations


@functools.lru_cache(maxsize=1)
def _kpis() -> dict[str, Any]:
    """The KPI block, computed once per process.

    Six facts read from this. Uncached, each re-read the 461 KB results DB and
    re-ran the full pass over the model list — five computations per run, ~210 ms
    of a pre-push hook spent recomputing an identical answer.

    Cached on the assumption that the DB does not change mid-run, which holds for
    a CLI invocation. Tests that mutate the DB must call ``_kpis.cache_clear()``.
    """
    return compute_kpis(_load(DB_PATH))


def _floor() -> int:
    return compute_floor(_load(PROVENANCE_PATH))


def _leak_scope() -> int:
    allow = load_allowlist()
    return sum(1 for (mid, _pre, _p) in discover_goldens() if mid not in allow)


def _outside_fences(text: str) -> list[str]:
    """Lines with fenced blocks removed.

    A ``KNOWN_UNKNOWNS.md`` template lives inside a fence and carries the same
    headings as a real entry. Counting it yields 31 unknowns against a real 30 —
    a discrepancy that shipped in a verification snippet and had to be corrected
    in review.
    """
    out: list[str] = []
    in_fence = False
    for line in text.split("\n"):
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return out


def _known_unknowns() -> list[str]:
    return _outside_fences(
        (PROJECT_ROOT / "docs/planning/EPIC_4/SPRINT_39/KNOWN_UNKNOWNS.md").read_text(
            encoding="utf-8"
        )
    )


def _unknown_count() -> int:
    return sum(1 for line in _known_unknowns() if re.match(r"^## Unknown \d", line))


def _research_hours() -> float:
    lines = _known_unknowns()
    total = 0.0
    for i, line in enumerate(lines):
        if not line.strip().startswith("### Estimated Research Time"):
            continue
        for nxt in lines[i + 1 : i + 4]:
            if nxt.strip():
                m = re.match(rf"~?({NUM})", nxt.strip())
                if m:
                    total += float(m.group(1))
                break
    return round(total, 1)


def _reconfirmation_reproduced() -> int:
    """Rows in the Task-2 verdict table marked ✅.

    ``12 of 14`` was written while the final measurement was still running and
    never revisited; the true count became 13 when it came back clean.
    """
    p = PROJECT_ROOT / "docs/planning/EPIC_4/SPRINT_39/BASELINE_RECONFIRMATION.md"
    if not p.exists():
        raise FileNotFoundError(p)
    return sum(
        1
        for line in p.read_text(encoding="utf-8").split("\n")
        if re.match(r"^\| *\d+ *\|.*\| *✅ ", line)
    )


def _dangling_presolve_rows() -> int:
    db = _load(DB_PATH)
    rows = [
        m
        for m in db.get("models", [])
        if (m.get("mcp_solve") or {}).get("outcome_category") == "model_optimal_presolve"
    ]
    # The DB stores repo-relative paths ("data/gamslib/mcp/..."). Resolving them
    # against the CWD makes the count depend on where the tool was invoked: from
    # `src/` this returned 48 — the entire presolve population — instead of 14,
    # because nothing resolved. A wrong *derived truth* is worse than no check:
    # every correct citation of 14 would then be reported as contradicting it.
    return sum(
        1
        for m in rows
        if (f := (m.get("mcp_solve") or {}).get("mcp_file_used"))
        and not (PROJECT_ROOT / f).exists()
    )


# ------------------------------------------------------------------- registry


def _kpi(key: str) -> Callable[[], int]:
    return lambda: _kpis()[key]


FACTS: tuple[Fact, ...] = (
    Fact(
        name="Solve",
        derive=_kpi("solve"),
        source="scripts/sprint_audit/kpi_block.py  ->  solve",
        patterns=(re.compile(rf"\bSolve\s+\**(?P<value>{NUM})\**"),),
    ),
    Fact(
        name="Match",
        derive=_kpi("match"),
        source="scripts/sprint_audit/kpi_block.py  ->  match",
        patterns=(re.compile(rf"(?<!-)\bMatch\s+\**(?P<value>{NUM})\**"),),
        # "all-219 Match 99" is a different population from the 142-candidate one.
        skip_if=(re.compile(r"all-219"),),
    ),
    Fact(
        name="Translate",
        derive=_kpi("translate"),
        source="scripts/sprint_audit/kpi_block.py  ->  translate",
        patterns=(re.compile(rf"\bTranslate\s+\**(?P<value>{NUM})\**"),),
    ),
    Fact(
        name="genuine floor",
        derive=_floor,
        source="scripts/sprint_audit/floor_tracker.py  ->  baseline + entries",
        patterns=(re.compile(rf"\b(?:genuine\s+)?floor\s+(?:is\s+)?\**(?P<value>{NUM})\**"),),
        # The open question is written as "73, 74 or 75" / "73/74/75" in the plan.
        # Anchored on digits so it cannot match inside an ordinary word.
        skip_if=(re.compile(r"\b73\s*(?:,|/|or)\s*7[45]\b"),),
    ),
    Fact(
        name="path_solve_license cohort",
        derive=_kpi("path_solve_license"),
        source="scripts/sprint_audit/kpi_block.py  ->  path_solve_license",
        patterns=(
            re.compile(rf"`?path_solve_license`?\s*\**(?P<value>{NUM})\**"),
            re.compile(rf"\**(?P<value>{NUM})\**[- ]model\s+`?licen[cs]e-gated`?"),
        ),
    ),
    Fact(
        name="path_solve_terminated",
        derive=_kpi("path_solve_terminated"),
        source="scripts/sprint_audit/kpi_block.py  ->  path_solve_terminated",
        patterns=(re.compile(rf"`?path_solve_terminated`?\s+(?:is\s+)?\**(?P<value>{NUM})\**"),),
    ),
    Fact(
        name="leak-gate in-scope goldens",
        derive=_leak_scope,
        source="check_golden_staleness.discover_goldens() minus load_allowlist()",
        # "in-scope" is used for other populations too ("12 in-scope models",
        # "<= 8 in-scope" for model_infeasible). Require the golden/leak-gate
        # context, or this reports on unrelated planning prose.
        patterns=(
            re.compile(rf"\**(?P<value>{NUM})\**\s+in-scope\s+golden"),
            re.compile(rf"leak[- ]gate[^0-9\n]{{0,30}}\**(?P<value>{NUM})\**\s+in-scope"),
            re.compile(rf"leak-gate\s+scope[^0-9\n]{{0,20}}\**(?P<value>{NUM})\**"),
        ),
    ),
    Fact(
        name="Sprint 39 unknowns",
        derive=_unknown_count,
        source="count of '## Unknown N.N' in KNOWN_UNKNOWNS.md, outside fences",
        # The TOTAL only. `KNOWN_UNKNOWNS.md` is full of per-category counts
        # ("Category 1 …: 3 unknowns") and subset counts ("6 of 30"), and an
        # unqualified `N unknowns` matched all of them — 203 hits across the
        # live docs, swamping the real signal.
        patterns=(
            re.compile(rf"\**(?P<value>{NUM})\**\s+unknowns\b(?=[^.\n]{{0,40}}(?:categor|across))"),
            # `| Total unknowns | 22–30 (aim 25+) | **30** |` — the claim is the
            # LAST cell. A forward scan stops at the target range's "22", which is
            # then correctly discarded as a range endpoint, so the real figure was
            # never reached and the row reported clean.
            re.compile(rf"\|\s*Total\s+unknowns\s*\|[^|\n]*\|\s*\**(?P<value>{NUM})\**\s*\|", re.I),
            re.compile(rf"\bunknowns:\s*\**(?P<value>{NUM})\**"),
        ),
        skip_if=(re.compile(r"\bof\s+(?:the\s+)?30\b"),),
    ),
    Fact(
        name="Sprint 39 research hours",
        derive=_research_hours,
        source="sum of '### Estimated Research Time' in KNOWN_UNKNOWNS.md, outside fences",
        # Both forms require the number ADJACENT to the label. The earlier
        # `[^0-9]{0,24}` window reached across "**, leak gate **" and captured
        # the leak-gate figure as a research-hours citation.
        patterns=(
            re.compile(rf"\**(?P<value>{NUM})\**\s*(?:h|hours)?\**\s+research\s+hours?\b", re.I),
            re.compile(rf"research\s+time\b[^0-9\n]{{0,8}}\**(?P<value>{NUM})\**", re.I),
            # The acceptance-table row: `| Research time | 28–36 h | **40.0 h** |`
            # — the claim is the LAST cell, and the target range is not a claim.
            #
            # The row LABEL is required. Without it this matched any markdown
            # cell holding an hours estimate — `| Create … | 1h | … |` in an
            # unrelated Sprint-16 plan reported "research hours: cited 1". A
            # check that fires on unrelated edits is a check that gets switched
            # off, which is the failure this tool was built to avoid.
            re.compile(
                rf"\|\s*Research\s+time\s*\|[^|\n]*\|\s*\**(?P<value>{NUM})\s*h\**\s*\|",
                re.I,
            ),
        ),
    ),
    Fact(
        name="dangling mcp_file_used rows",
        derive=_dangling_presolve_rows,
        source="DB: presolve rows whose recorded mcp_file_used no longer exists",
        # The forward form must not cross punctuation. An earlier
        # `dangling[^0-9\n]{0,32}` scanned past the end of the clause in
        # "(… / 14 dangling), all correct — P7 must name which" and captured the
        # 7 of "P7" as the cited figure.
        patterns=(
            # Forward: "…count of dangling `mcp_file_used` rows is **14**".
            # The window is generous but cannot cross clause punctuation.
            re.compile(rf"dangling\b[^0-9\n,)|—;.]{{0,40}}\**(?P<value>{NUM})\**"),
            # Reverse: "**14 dangling** rows". The trailing "rows" is required —
            # without it, "14 of the 48 dangling" matches the POPULATION (48)
            # rather than the count.
            re.compile(rf"\**(?P<value>{NUM})\**\s+dangling\**\s+(?:mcp_file_used\s+)?rows?\b"),
            re.compile(rf"all\s+\**(?P<value>{NUM})\**\s+(?:presolve-record\s+)?rows"),
        ),
    ),
    Fact(
        name="Task-2 figures reproduced",
        derive=_reconfirmation_reproduced,
        source="count of ✅ rows in BASELINE_RECONFIRMATION.md's verdict table",
        # "N of 14" alone matches any ratio out of fourteen — `+4 of 14 new`,
        # `9 of 14 categories`. Tie it to the claim: a `reproduc…` must follow
        # within the same sentence.
        patterns=(
            re.compile(rf"\**(?P<value>{NUM})\**\s+of\s+(?:the\s+)?14\b(?=[^.\n]{{0,60}}reproduc)"),
        ),
    ),
)


def _is_range_endpoint(text: str, start: int, end: int) -> bool:
    """True if the match sits inside ``N–M`` (a target range, not a claim).

    ``| Research time | 28–36 h | **40.0 h** |`` cites one figure and states one
    target. Blocking the whole line on the range — the first attempt — also
    blocked the claim beside it.
    """
    before = text[max(0, start - 1) : start]
    after = text[end : end + 1]
    return (before in "-–—" and start > 0) or (after in "-–—" and after != "")


# --------------------------------------------------------------------- diffing


def _merge_base(base: str) -> str:
    """The fork point of ``base`` and ``HEAD``, or ``base`` if there is none.

    Diffing straight against ``base`` answers *"how does the worktree differ from
    base"*, which is **not** the question. Once ``base`` advances, a line that
    another branch rewrote shows up as *added here* simply because this branch
    still has the older text — so a stale figure someone else introduced is
    attributed to this change.

    Demonstrated, not assumed. With ``main`` ahead by one unrelated commit::

        git diff main            ->  +ours untouched          # never touched here
                                     +feature adds: Solve 999
        git diff <merge-base>    ->  +feature adds: Solve 999

    The merge base is used against the **worktree** rather than ``base...HEAD``
    because the three-dot form drops uncommitted work, and running the check
    before committing is the main way it gets used.
    """
    try:
        return subprocess.run(
            ["git", "merge-base", base, "HEAD"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except subprocess.CalledProcessError:
        # No common ancestor (an unrelated history, or a bare SHA). Fall back to
        # `base` and say so: a silent fallback would quietly restore the very
        # over-scoping this function exists to avoid.
        print(
            f"  note: no merge base for {base!r} and HEAD — diffing against {base!r} directly.",
            file=sys.stderr,
        )
        return base


def changed_doc_lines(base: str) -> dict[Path, list[tuple[int, str]]]:
    """Added/modified doc lines this branch introduced, as ``{path: [(lineno, text)]}``.

    Parsed from unified diff hunk headers rather than by re-reading files, so a
    line is in scope only if this change actually touched it. Measured from the
    merge base rather than from ``base`` — see :func:`_merge_base`.
    """
    fork = _merge_base(base)
    try:
        raw = subprocess.run(
            ["git", "diff", "--unified=0", "--no-color", fork, "--"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"ERROR: `git diff {fork}` failed: {exc.stderr.strip()}") from exc

    out: dict[Path, list[tuple[int, str]]] = {}
    path: Path | None = None
    lineno = 0
    # `+++ b/…` is a FILE HEADER only before the first hunk. Distinguishing it by
    # prefix alone also discards body content: an added line holding `++ foo`
    # arrives as `+++ foo`, and markdown legitimately contains such text. Track
    # header-vs-body explicitly instead — a content line is never misread, and a
    # header line is never mistaken for content.
    in_header = False
    for line in raw.split("\n"):
        if line.startswith("diff --git "):
            in_header, path, lineno = True, None, 0
            continue
        if in_header and line.startswith("+++ "):
            target = line[4:]
            candidate = Path(target[2:] if target.startswith("b/") else target)
            path = candidate if candidate.suffix in DOC_SUFFIXES else None
            continue
        if line.startswith("@@"):
            in_header = False
            m = re.search(r"\+(\d+)", line)
            lineno = int(m.group(1)) if m else 0
            continue
        if path is None or in_header:
            continue
        if line.startswith("+"):
            out.setdefault(path, []).append((lineno, line[1:]))
            lineno += 1
    return out


def _exempt_reason(line: str) -> str | None:
    if _INLINE_EXEMPT.search(line):
        return "inline figures-ok marker"
    low = line.lower()
    for marker in _EXEMPT_MARKERS:
        if marker in low:
            return f"corrective/historical phrasing: {marker!r}"
    return None


# ---------------------------------------------------------------------- check


@dataclass
class Finding:
    path: Path
    lineno: int
    fact: str
    cited: str
    truth: str
    source: str
    line: str


def scan_line(
    path: Path,
    lineno: int,
    text: str,
    truths: dict[str, float | int],
) -> tuple[list[Finding], str | None]:
    """Check one line. Returns ``(findings, exemption_reason)``.

    Pure: takes the derived truths rather than deriving them, so tests can pin
    them instead of depending on a database that moves.
    """
    reason = _exempt_reason(text)
    if reason is None and _MOVEMENT.search(text):
        reason = "movement line (A → B): the left figure is historical"
    if reason:
        return [], reason

    findings: list[Finding] = []
    seen: set[tuple[str, str]] = set()
    for fact in FACTS:
        if fact.name not in truths:
            continue
        if any(p.search(text) for p in fact.skip_if):
            continue
        truth = truths[fact.name]
        for pattern in fact.patterns:
            for m in pattern.finditer(text):
                cited_raw = m.group("value")
                if _is_range_endpoint(text, m.start("value"), m.end("value")):
                    continue
                try:
                    cited = float(cited_raw)
                except ValueError:
                    continue
                if abs(cited - float(truth)) <= 1e-9:
                    continue
                # Several patterns per fact may match the same figure.
                if (fact.name, cited_raw) in seen:
                    continue
                seen.add((fact.name, cited_raw))
                findings.append(
                    Finding(
                        path=path,
                        lineno=lineno,
                        fact=fact.name,
                        cited=cited_raw,
                        truth=f"{truth}",
                        source=fact.source,
                        line=text.strip(),
                    )
                )
    return findings, None


def derive_truths() -> dict[str, float | int]:
    """Derive every fact whose source currently exists.

    A fact whose source is a future deliverable is **omitted**, not defaulted —
    a missing source must not read as a satisfied check.
    """
    truths: dict[str, float | int] = {}
    for fact in FACTS:
        try:
            truths[fact.name] = fact.derive()
        except FileNotFoundError:
            continue
    return truths


def check(
    base: str,
) -> tuple[list[Finding], int, list[tuple[Path, int, str]], dict[str, float | int], int]:
    """Return ``(findings, lines_scanned, exemptions, truths, archived_lines)``.

    The derived truths are returned rather than recomputed by the caller: every
    derivation re-reads the DB and re-runs the KPI computation, and a second
    pass could report a coverage figure the scan never used if a derivation ever
    became time-dependent.
    """
    changed = changed_doc_lines(base)
    truths = derive_truths()

    findings: list[Finding] = []
    exemptions: list[tuple[Path, int, str]] = []
    scanned = 0
    archived = 0

    for path, lines in sorted(changed.items()):
        if not is_live_doc(path):
            archived += len(lines)
            continue
        for lineno, text in lines:
            scanned += 1
            line_findings, reason = scan_line(path, lineno, text, truths)
            if reason:
                exemptions.append((path, lineno, reason))
            findings.extend(line_findings)
    return findings, scanned, exemptions, truths, archived


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Flag a figure cited in a changed doc that contradicts its source."
    )
    ap.add_argument(
        "--base",
        default="origin/main",
        help="revision to diff against (default: origin/main)",
    )
    ap.add_argument(
        "--min-scope",
        type=int,
        default=None,
        help=(
            "fail if fewer than N doc lines were scanned. Asserted on DISCOVERY: a "
            "check that silently narrows to nothing reports PASS and is a "
            "false-negative generator."
        ),
    )
    ap.add_argument("--list-facts", action="store_true", help="print the registry and exit")
    args = ap.parse_args()

    if args.list_facts:
        for fact in FACTS:
            try:
                value: object = fact.derive()
            except Exception as exc:  # noqa: BLE001 - reported, not raised
                value = f"(underivable: {exc})"
            print(f"  {fact.name:34} = {value}\n      {fact.source}")
        return 0

    findings, scanned, exemptions, truths, archived = check(args.base)

    # Report the DERIVABLE count, not the registered one. A fact whose source is
    # absent is skipped by `derive_truths`, so quoting len(FACTS) claims coverage
    # the run did not have — the precise overstatement this tool exists to catch.
    # Taken from the scan's own truths, so the number reported is the number used.
    derivable = len(truths)
    coverage = f"{derivable} fact(s)"
    if derivable < len(FACTS):
        coverage += f" ({len(FACTS) - derivable} skipped: source not present)"
    print(f"Doc-figure check: {scanned} changed doc line(s) scanned against {coverage}.")
    if archived:
        print(f"  {archived} line(s) in archived docs not scanned (figures there are historical).")
    if exemptions:
        print(f"  {len(exemptions)} line(s) exempted as corrective/historical:")
        for path, lineno, reason in exemptions[:10]:
            print(f"    {path}:{lineno}  ({reason})")
        if len(exemptions) > 10:
            print(f"    … and {len(exemptions) - 10} more")

    if args.min_scope is not None and scanned < args.min_scope:
        print(
            f"ERROR: coverage floor not met — scanned {scanned} line(s), "
            f"expected at least {args.min_scope}.",
            file=sys.stderr,
        )
        return 2

    if not findings:
        print("  No cited figure contradicts its source.")
        return 0

    print(f"\n{len(findings)} figure(s) contradict their source:\n", file=sys.stderr)
    for f in findings:
        print(f"  {f.path}:{f.lineno}", file=sys.stderr)
        print(f"    {f.fact}: cited {f.cited}, derived {f.truth}", file=sys.stderr)
        print(f"    source: {f.source}", file=sys.stderr)
        print(f"    line:   {f.line[:120]}", file=sys.stderr)
        print(file=sys.stderr)
    print(
        "If a citation is deliberately historical, mark it " "`<!-- figures-ok: <reason> -->`.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Phase-0 acceptance-gate doc check (Sprint 37 P7).

CONTRIBUTING.md §392-447: any PR touching ``src/{ad,kkt,emit}`` must carry a
``docs/issues/ISSUE_<N>_*.md`` with a ``## Phase 0: Acceptance Gate`` section
containing 4 canonical ``### `` subsections, BEFORE the ``src/`` commit lands.

Enforcement was previously by reviewer memory only. Measured compliance over the
three most recent emit-touching PRs before this check existed: **1 of 3**, and
that one only after a reviewer asked (Sprint 37 Prep Task 10 §2.1).

Two rules this implements, both calibrated against the real corpus rather than
assumed (Task 10 §2.2):

* **Prefix matching at BOTH levels.** The heading match is a prefix, because
  ``ISSUE_1330``'s heading carries a parenthetical suffix
  (``## Phase 0: Acceptance Gate (Sprint 28 Prep Task 5 …)``) and a ``$``-anchored
  match silently drops it. Subsection names are prefix-matched for the same
  reason (``### Expected Emit Pattern (hypothesis — PR24)``).
* **Extras allowed.** An *exactly-4* check fails ``ISSUE_1224``, which has
  carried 6 subsections since Sprint 28. CONTRIBUTING was reworded to match in
  PR #1670; this check and that wording now agree.

Exit codes: 0 = pass (or not applicable), 1 = missing/non-conforming Phase-0 doc,
2 = usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ISSUES_DIR = PROJECT_ROOT / "docs" / "issues"

# The paths CONTRIBUTING §392 names. Deliberately NARROWER than the leak gate's,
# which also arms on `src/ir/**` — do not widen them to match.
EMIT_PATH_RE = re.compile(r"^src/(ad|kkt|emit)/.*\.py$")

REQUIRED = [
    "Hand-Derived KKT Shape",
    "Expected Emit Pattern",
    "Verification Methodology",
    "PROCEED/REPLAN Signal",
]

PHASE0_HEADING = re.compile(r"^## Phase 0: Acceptance Gate\b", re.M)


def phase0_subsections(text: str) -> list[str] | None:
    """Return the ``### `` subsection titles under the Phase-0 heading.

    Returns None when the document has no Phase-0 heading at all.
    """
    m = PHASE0_HEADING.search(text)
    if not m:
        return None
    rest = text[m.end() :]
    nxt = re.search(r"^## ", rest, re.M)
    body = rest[: nxt.start()] if nxt else rest
    return [h.strip() for h in re.findall(r"^### (.+)$", body, re.M)]


def missing_subsections(text: str) -> list[str]:
    """Required subsection names absent from *text*. Empty list == conforming."""
    subs = phase0_subsections(text)
    if subs is None:
        return list(REQUIRED)
    return [r for r in REQUIRED if not any(h.startswith(r) for h in subs)]


def issue_docs_from_body(body: str) -> list[Path]:
    """Resolve `ISSUE_<N>` / `#<N>` references in a PR body to issue docs.

    CONTRIBUTING already requires the PR description to reference the Phase-0
    PROCEED signal, so this adds no authoring burden — and it lets a follow-on
    fix cite a doc that landed in an earlier PR.
    """
    # A bare `#<N>` is NOT accepted. PR bodies routinely cite *pull requests*
    # that way, and `docs/issues/` is dense enough that an unrelated citation
    # resolves: a body mentioning PR #747 would match `ISSUE_747_*.md` and
    # satisfy the gate without any Phase-0 doc being written for the change.
    # (This PR's own body cites #1620 and #1596 as historical PRs.) Require an
    # explicit issue reference — `ISSUE_<N>` or `Issue #<N>` / `issue #<N>`.
    nums = set(re.findall(r"ISSUE_(\d+)", body or "")) | set(
        re.findall(r"\bissues?\s*#\s*(\d+)", body or "", re.IGNORECASE)
    )
    out: list[Path] = []
    for n in sorted(nums, key=int):
        out.extend(sorted(ISSUES_DIR.glob(f"ISSUE_{n}_*.md")))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase-0 acceptance-gate doc check.")
    ap.add_argument(
        "--changed-files",
        required=True,
        help="path to a file listing the PR's changed paths, one per line",
    )
    ap.add_argument("--pr-body", help="path to a file containing the PR body text")
    ap.add_argument("--json", dest="json_path", help="write a machine-readable report")
    args = ap.parse_args()

    changed_path = Path(args.changed_files)
    if not changed_path.is_file():
        print(f"ERROR: --changed-files not found: {changed_path}", file=sys.stderr)
        return 2
    changed = [ln.strip() for ln in changed_path.read_text().splitlines() if ln.strip()]

    emit_files = [f for f in changed if EMIT_PATH_RE.match(f)]
    report: dict = {"emit_files": emit_files, "applicable": bool(emit_files)}

    if not emit_files:
        print(
            "Phase-0 gate: not applicable — this PR changes no "
            "src/{ad,kkt,emit}/**/*.py file."
        )
        report["verdict"] = "not_applicable"
        _write(args.json_path, report)
        return 0

    # Candidate docs: those changed by the PR, plus any referenced from the body.
    changed_docs = [
        PROJECT_ROOT / f
        for f in changed
        if f.startswith("docs/issues/ISSUE_") and f.endswith(".md")
    ]
    body = Path(args.pr_body).read_text() if args.pr_body and Path(args.pr_body).is_file() else ""
    referenced_docs = issue_docs_from_body(body)

    candidates: list[Path] = []
    for p in changed_docs + referenced_docs:
        if p not in candidates and p.is_file():
            candidates.append(p)

    report["candidates"] = [str(p.relative_to(PROJECT_ROOT)) for p in candidates]

    conforming: list[str] = []
    defects: list[tuple[str, list[str]]] = []
    for p in candidates:
        miss = missing_subsections(p.read_text())
        rel = str(p.relative_to(PROJECT_ROOT))
        if miss:
            defects.append((rel, miss))
        else:
            conforming.append(rel)

    report["conforming"] = conforming
    report["defects"] = [{"doc": d, "missing": m} for d, m in defects]

    if conforming:
        print(
            f"Phase-0 gate PASS: {len(emit_files)} emit file(s) changed; "
            f"conforming Phase-0 doc(s): {', '.join(conforming)}"
        )
        report["verdict"] = "pass"
        _write(args.json_path, report)
        return 0

    # Fail — point at the rule, the specific defect, and the fix.
    print("Phase-0 acceptance gate MISSING for an emit-touching PR.", file=sys.stderr)
    print("", file=sys.stderr)
    print(
        "This PR changes src/{ad,kkt,emit}, which CONTRIBUTING.md §392-447 requires to",
        file=sys.stderr,
    )
    print("carry a Phase-0 acceptance gate BEFORE the src/ commit lands.", file=sys.stderr)
    print("", file=sys.stderr)
    print(f"  changed emit files : {', '.join(emit_files)}", file=sys.stderr)
    if defects:
        print(f"  issue docs checked : {', '.join(d for d, _ in defects)}", file=sys.stderr)
        for doc, miss in defects:
            print(f"  defect ({doc}):", file=sys.stderr)
            print("    missing required subsection(s):", file=sys.stderr)
            for r in miss:
                print(f"      ### {r}", file=sys.stderr)
    else:
        print("  issue docs checked : (none — no ISSUE_*.md changed, and the", file=sys.stderr)
        print("                       PR body references no resolvable issue)", file=sys.stderr)
    print("", file=sys.stderr)
    print("Add a `## Phase 0: Acceptance Gate` section with these 4 `### ` subsections:", file=sys.stderr)
    print("  ### Hand-Derived KKT Shape       ### Expected Emit Pattern", file=sys.stderr)
    print("  ### Verification Methodology     ### PROCEED/REPLAN Signal", file=sys.stderr)
    print(
        "(additional subsections are allowed). Format reference: docs/issues/ISSUE_1356_*.md",
        file=sys.stderr,
    )
    print("", file=sys.stderr)
    print("If this PR is exception-scope (no emit-shape change), apply the `skip-phase0`", file=sys.stderr)
    print("label and say why in the PR description.", file=sys.stderr)
    report["verdict"] = "fail"
    _write(args.json_path, report)
    return 1


def _write(path: str | None, report: dict) -> None:
    if path:
        Path(path).write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Sprint audit: emit-affecting `*_mcp.gms` artifact change detector.

Scans git history for changes under `data/gamslib/mcp/` matching the emit-
artifact suffixes (`*_mcp.gms` and `*_mcp_presolve.gms`) and groups them by
the triggering commit. Codifies Sprint 26 retrospective recommendation PR22
— auto-generates the PR14 review list + mid-sprint retest comparison
surface from git log instead of from a frozen prompt document.

Usage:
    # Date-based (subject to same-day commit-boundary ambiguity):
    python scripts/sprint_audit/changed_emit_artifacts.py \\
        --since-date "2026-04-22"

    # Commit-based (unambiguous; preferred for mid-sprint retests):
    python scripts/sprint_audit/changed_emit_artifacts.py \\
        --since-commit <sprint-day-0-sha>

    # JSON output for downstream tooling:
    python scripts/sprint_audit/changed_emit_artifacts.py \\
        --since-commit <sha> --format json

    # Markdown table for inclusion in retest reports:
    python scripts/sprint_audit/changed_emit_artifacts.py \\
        --since-commit <sha> --format markdown --mode retest

CLI design:
    --since-date and --since-commit are mutually exclusive; exactly one
    must be specified. Two distinct flags is the correct design because
    `git log --since` is date-based (accepts ISO-8601 dates or relative
    expressions) and does NOT accept commit SHAs, so a single overloaded
    `--since` would be misleading.

    The Sprint Day 0 commit SHA is the recommended `--since-commit`
    value for mid-sprint retests; `--since-date` is provided for quick
    ad-hoc invocations where exact commit-boundary precision is not
    needed.

Implementation notes:
    - Uses `subprocess.run(argv_list, ...)` so argv elements are passed
      verbatim without shell parsing.
    - The git pathspec is the directory `data/gamslib/mcp/` (NOT a
      `*.gms` glob): argv-list calls bypass shell glob expansion, and
      Git's interpretation of unadorned `*` pathspecs is not reliable
      across versions / `core.literalPathspecs` settings.
    - The `*_mcp.gms` / `*_mcp_presolve.gms` suffix filter is applied
      in Python after parsing the git log output.
    - `git log --name-only --pretty=format:COMMIT:%H` produces output
      where `COMMIT:<sha>` lines mark commit boundaries and subsequent
      non-blank lines are changed file paths. Subjects are NOT included
      in the format string (including `%n%s` would add a non-path line
      per commit that the parser would misclassify).
    - For display, commit subjects are fetched in a separate `git log`
      pass keyed by SHA.

Exit codes:
    0 - Success (zero or more matching commits found)
    2 - Invalid arguments (validation error)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

EMIT_DIR = "data/gamslib/mcp/"
EMIT_SUFFIXES = ("_mcp.gms", "_mcp_presolve.gms")


@dataclass(frozen=True)
class CommitGroup:
    """A commit and the emit-artifact file paths changed in it."""

    sha: str
    subject: str
    files: tuple[str, ...] = field(default_factory=tuple)


def _run_git(argv: list[str]) -> str:
    """Run a git command and return its stdout (text mode)."""
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        argv,
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def validate_commit_sha(sha: str) -> str:
    """Resolve and validate a commit SHA via `git rev-parse`.

    Returns the full SHA on success; raises SystemExit with a clear
    message on failure.
    """
    try:
        full = _run_git(["git", "rev-parse", "--verify", f"{sha}^{{commit}}"]).strip()
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(
            f"error: --since-commit {sha!r} is not a valid commit SHA "
            f"in this repository (git rev-parse exit {exc.returncode})\n"
        )
        if exc.stderr:
            sys.stderr.write(exc.stderr)
        raise SystemExit(2) from exc
    return full


def collect_changed_artifacts(
    *,
    since_date: str | None,
    since_commit: str | None,
) -> list[CommitGroup]:
    """Scan git log for emit-affecting changes under data/gamslib/mcp/.

    Exactly one of since_date / since_commit must be set. Returns a list
    of CommitGroup entries in git-log order (most recent first). Commits
    with no matching files (e.g., touched a non-suffix file under
    data/gamslib/mcp/) are omitted.
    """
    if (since_date is None) == (since_commit is None):
        raise ValueError("exactly one of since_date / since_commit must be provided")

    argv = [
        "git",
        "log",
        "--name-only",
        "--pretty=format:COMMIT:%H",
    ]
    if since_date is not None:
        argv += ["--since", since_date]
    else:
        assert since_commit is not None
        argv += [f"{since_commit}..HEAD"]
    argv += ["--", EMIT_DIR]

    raw = _run_git(argv)

    groups: list[CommitGroup] = []
    current_sha: str | None = None
    current_files: list[str] = []

    def flush() -> None:
        nonlocal current_sha, current_files
        if current_sha is None:
            return
        matched = tuple(p for p in current_files if p.endswith(EMIT_SUFFIXES))
        if matched:
            groups.append(CommitGroup(sha=current_sha, subject="", files=matched))
        current_sha = None
        current_files = []

    for line in raw.splitlines():
        if not line:
            continue
        if line.startswith("COMMIT:"):
            flush()
            current_sha = line[len("COMMIT:") :]
        else:
            current_files.append(line)
    flush()

    if groups:
        subjects = _fetch_subjects([g.sha for g in groups])
        groups = [
            CommitGroup(sha=g.sha, subject=subjects.get(g.sha, ""), files=g.files) for g in groups
        ]

    return groups


def _fetch_subjects(shas: list[str]) -> dict[str, str]:
    """Fetch commit subjects keyed by SHA (one separate git log pass)."""
    if not shas:
        return {}
    argv = ["git", "log", "--no-walk", "--pretty=format:%H %s", *shas]
    raw = _run_git(argv)
    subjects: dict[str, str] = {}
    for line in raw.splitlines():
        if not line:
            continue
        sha, _, subject = line.partition(" ")
        subjects[sha] = subject
    return subjects


def format_text(
    groups: list[CommitGroup],
    *,
    mode: str,
    range_label: str,
) -> str:
    """Human-readable grouped-by-commit text output."""
    lines: list[str] = []
    header = "PR14 review list" if mode == "pr14" else "Mid-sprint retest surface"
    lines.append(f"# {header}")
    lines.append(f"Range: {range_label}")
    total_files = sum(len(g.files) for g in groups)
    unique = len({p for g in groups for p in g.files})
    lines.append(f"Commits: {len(groups)}; emit changes: {total_files} " f"({unique} unique paths)")
    lines.append("")
    if not groups:
        lines.append("(no emit-affecting changes in range)")
        return "\n".join(lines) + "\n"
    for g in groups:
        lines.append(f"{g.sha[:12]}  {g.subject}")
        for path in g.files:
            lines.append(f"    {path}")
        lines.append("")
    return "\n".join(lines)


def format_markdown(
    groups: list[CommitGroup],
    *,
    mode: str,
    range_label: str,
) -> str:
    """Markdown-table output suitable for inclusion in retest reports."""
    header = "PR14 review list" if mode == "pr14" else "Mid-sprint retest surface"
    lines: list[str] = []
    lines.append(f"## {header}")
    lines.append("")
    lines.append(f"- **Range:** {range_label}")
    total_files = sum(len(g.files) for g in groups)
    unique = len({p for g in groups for p in g.files})
    lines.append(
        f"- **Commits:** {len(groups)} — **emit changes:** {total_files} "
        f"({unique} unique paths)"
    )
    lines.append("")
    if not groups:
        lines.append("_(no emit-affecting changes in range)_")
        return "\n".join(lines) + "\n"
    lines.append("| Commit | Subject | Changed emit artifact |")
    lines.append("|---|---|---|")
    for g in groups:
        sha_short = g.sha[:12]
        # one row per file; first row per commit shows commit info,
        # subsequent rows leave those columns blank for readability.
        for i, path in enumerate(g.files):
            if i == 0:
                lines.append(f"| `{sha_short}` | {g.subject} | `{path}` |")
            else:
                lines.append(f"|  |  | `{path}` |")
    return "\n".join(lines) + "\n"


def format_json(
    groups: list[CommitGroup],
    *,
    mode: str,
    range_label: str,
) -> str:
    """Machine-readable JSON output."""
    payload = {
        "mode": mode,
        "range": range_label,
        "commit_count": len(groups),
        "emit_change_count": sum(len(g.files) for g in groups),
        "unique_path_count": len({p for g in groups for p in g.files}),
        "commits": [{"sha": g.sha, "subject": g.subject, "files": list(g.files)} for g in groups],
    }
    return json.dumps(payload, indent=2) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="changed_emit_artifacts",
        description=(
            "Scan git log for emit-affecting changes under "
            "data/gamslib/mcp/ (filters *_mcp.gms and *_mcp_presolve.gms), "
            "grouped by triggering commit. Codifies Sprint 26 retrospective "
            "recommendation PR22."
        ),
        epilog=(
            'Sprint 26 dry-run expectation: --since-date "2026-04-22" or '
            "--since-commit <sprint-26-day-0-sha> must surface AT LEAST "
            "(a) launch artifacts from the Day 1 Phase A landing AND "
            "(b) artifacts for all 15 #1398-affected models from the Day "
            "13 regeneration sweep (qdemo7, egypt, ferts, shale, sambal, "
            "qsambal, harker, tfordy, dinam, ganges, gangesx, fawley, "
            "srpchase, sroute, turkpow). #1400 (scripts/gamslib/* path-"
            "relativization) is intentionally out of scope for this script."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    range_group = parser.add_mutually_exclusive_group(required=True)
    range_group.add_argument(
        "--since-date",
        metavar="DATE",
        help=(
            "Date passed to `git log --since DATE` (ISO-8601 or relative "
            "expression like '2 days ago'). Subject to same-day commit-"
            "boundary ambiguity — prefer --since-commit for unambiguous "
            "sprint boundaries."
        ),
    )
    range_group.add_argument(
        "--since-commit",
        metavar="SHA",
        help=(
            "Commit SHA used to build `git log SHA..HEAD`. Validated via "
            "`git rev-parse` before use. Recommended for mid-sprint "
            "retests because commit boundaries are unambiguous."
        ),
    )
    parser.add_argument(
        "--format",
        choices=("text", "markdown", "json"),
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--mode",
        choices=("pr14", "retest"),
        default="retest",
        help=(
            "Report header label: 'pr14' for per-PR review lists, "
            "'retest' for mid-sprint retest comparison surfaces (default). "
            "Does not affect the diff-detection logic."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.since_commit is not None:
        resolved = validate_commit_sha(args.since_commit)
        range_label = f"{resolved[:12]}..HEAD"
        groups = collect_changed_artifacts(since_date=None, since_commit=resolved)
    else:
        range_label = f"--since {args.since_date}"
        groups = collect_changed_artifacts(since_date=args.since_date, since_commit=None)

    if args.format == "json":
        sys.stdout.write(format_json(groups, mode=args.mode, range_label=range_label))
    elif args.format == "markdown":
        sys.stdout.write(format_markdown(groups, mode=args.mode, range_label=range_label))
    else:
        sys.stdout.write(format_text(groups, mode=args.mode, range_label=range_label))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

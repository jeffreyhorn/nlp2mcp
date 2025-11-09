#!/usr/bin/env python3
"""
Changelog Generator for nlp2mcp

Generates changelog entries from git commits following Keep a Changelog format.

Usage:
    python scripts/generate_changelog.py [--since TAG] [--version VERSION] [--dry-run]

Examples:
    python scripts/generate_changelog.py --since v0.1.0 --version 0.2.0
    python scripts/generate_changelog.py --dry-run
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


CHANGELOG_CATEGORIES = {
    "Added": ["add", "feat", "feature", "new"],
    "Changed": ["change", "update", "refactor", "improve"],
    "Deprecated": ["deprecate", "deprecated"],
    "Removed": ["remove", "delete"],
    "Fixed": ["fix", "bug", "bugfix"],
    "Security": ["security", "vuln", "cve"],
}


def run_git_command(cmd: List[str]) -> str:
    """
    Run a git command and return output.

    Args:
        cmd: Git command as list of strings

    Returns:
        Command output as string
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {e}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        raise


def get_commits_since(since_tag: Optional[str] = None) -> List[str]:
    """
    Get commit messages since a given tag or all commits.

    Args:
        since_tag: Git tag to start from (e.g., "v0.1.0")

    Returns:
        List of commit messages
    """
    if since_tag:
        # Get commits since tag
        cmd = ["git", "log", f"{since_tag}..HEAD", "--pretty=format:%s"]
    else:
        # Get all commits
        cmd = ["git", "log", "--pretty=format:%s"]

    output = run_git_command(cmd)

    if not output:
        return []

    return output.split("\n")


def categorize_commit(commit_msg: str) -> Optional[str]:
    """
    Categorize a commit message into a changelog category.

    Args:
        commit_msg: Git commit message

    Returns:
        Category name or None if no match
    """
    commit_lower = commit_msg.lower()

    for category, keywords in CHANGELOG_CATEGORIES.items():
        for keyword in keywords:
            # Use word boundary matching to avoid false positives
            # e.g., "add" won't match "address", "fix" won't match "prefix"
            pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(pattern, commit_lower):
                return category

    return None


def parse_commits(commits: List[str]) -> Dict[str, List[str]]:
    """
    Parse commits into categorized changelog entries.

    Args:
        commits: List of commit messages

    Returns:
        Dictionary mapping categories to commit messages
    """
    categorized = {cat: [] for cat in CHANGELOG_CATEGORIES.keys()}
    uncategorized = []

    for commit in commits:
        # Skip merge commits
        if commit.startswith("Merge "):
            continue

        # Skip empty commits
        if not commit.strip():
            continue

        category = categorize_commit(commit)

        if category:
            categorized[category].append(commit)
        else:
            uncategorized.append(commit)

    # Add uncategorized to "Changed" if not obvious
    if uncategorized:
        categorized["Changed"].extend(uncategorized)

    return categorized


def format_changelog_entry(
    version: str,
    date: str,
    categorized_commits: Dict[str, List[str]],
) -> str:
    """
    Format changelog entry for a version.

    Args:
        version: Version number (e.g., "0.2.0")
        date: Release date (e.g., "2025-11-08")
        categorized_commits: Categorized commit messages

    Returns:
        Formatted changelog entry
    """
    lines = []
    lines.append(f"## [{version}] - {date}")
    lines.append("")

    # Add each category that has commits
    for category in CHANGELOG_CATEGORIES.keys():
        commits = categorized_commits.get(category, [])
        if commits:
            lines.append(f"### {category}")
            lines.append("")
            for commit in commits:
                # Clean up commit message (remove conventional commit prefixes if present)
                cleaned = re.sub(
                    r"^(feat|fix|docs|style|refactor|test|chore)(\([^)]+\))?:\s*", "", commit
                )
                lines.append(f"- {cleaned}")
            lines.append("")

    return "\n".join(lines)


def read_changelog(changelog_path: Path) -> str:
    """
    Read current changelog content.

    Args:
        changelog_path: Path to CHANGELOG.md

    Returns:
        Current changelog content
    """
    if changelog_path.exists():
        return changelog_path.read_text()

    # Return template if no changelog exists
    return """# Changelog

All notable changes to the nlp2mcp project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

"""


def insert_changelog_entry(current_content: str, new_entry: str) -> str:
    """
    Insert new changelog entry after the [Unreleased] section.

    Args:
        current_content: Current CHANGELOG.md content
        new_entry: New changelog entry to insert

    Returns:
        Updated changelog content
    """
    # Find the [Unreleased] section
    unreleased_pattern = r"(## \[Unreleased\].*?)(\n## \[|$)"

    match = re.search(unreleased_pattern, current_content, re.DOTALL)

    if match:
        # Insert new entry after [Unreleased] section
        before_unreleased = current_content[: match.end(1)]
        after_unreleased = current_content[match.end(1) :]

        return f"{before_unreleased}\n\n{new_entry}\n{after_unreleased}"
    else:
        # No [Unreleased] section, append at end
        return f"{current_content}\n\n{new_entry}\n"


def main():
    """Main entry point for changelog generator."""
    parser = argparse.ArgumentParser(
        description="Generate changelog entries from git commits",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --since v0.1.0 --version 0.2.0
  %(prog)s --version 0.5.0-beta --since v0.1.0
  %(prog)s --dry-run
        """,
    )
    parser.add_argument(
        "--since",
        help="Git tag to start from (e.g., v0.1.0). If not provided, uses all commits.",
    )
    parser.add_argument(
        "--version",
        help="Version number for the new entry (e.g., 0.2.0)",
    )
    parser.add_argument(
        "--date",
        help="Release date (YYYY-MM-DD). Defaults to today.",
        default=datetime.now().strftime("%Y-%m-%d"),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show generated entry without modifying CHANGELOG.md",
    )

    args = parser.parse_args()

    # Find changelog file
    repo_root = Path(__file__).parent.parent
    changelog_path = repo_root / "CHANGELOG.md"

    try:
        # Get commits
        print(f"Fetching commits{f' since {args.since}' if args.since else ''}...")
        commits = get_commits_since(args.since)

        if not commits:
            print("No commits found.")
            return 0

        print(f"Found {len(commits)} commits")

        # Categorize commits
        categorized = parse_commits(commits)

        # Show categorization summary
        for category, items in categorized.items():
            if items:
                print(f"  {category}: {len(items)} items")

        # Generate changelog entry
        if not args.version:
            print("\nError: --version is required to generate changelog entry", file=sys.stderr)
            print("Usage: python scripts/generate_changelog.py --version 0.2.0 --since v0.1.0")
            return 1

        new_entry = format_changelog_entry(args.version, args.date, categorized)

        if args.dry_run:
            print("\n" + "=" * 60)
            print("Generated changelog entry (DRY RUN):")
            print("=" * 60)
            print(new_entry)
            print("=" * 60)
            print("\n[DRY RUN] No changes made.")
            return 0

        # Read current changelog
        current_content = read_changelog(changelog_path)

        # Insert new entry
        updated_content = insert_changelog_entry(current_content, new_entry)

        # Write updated changelog
        changelog_path.write_text(updated_content)

        print(f"\n✓ Updated {changelog_path}")
        print(f"\nNext steps:")
        print(f"  1. Review changes: git diff CHANGELOG.md")
        print(f"  2. Manually edit CHANGELOG.md to add any missing details")
        print(f"  3. Commit: git commit -am 'Update CHANGELOG for {args.version}'")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

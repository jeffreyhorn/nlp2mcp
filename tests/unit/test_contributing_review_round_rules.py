"""Sprint 40 P10e: the Review-Round Rules in ``CONTRIBUTING.md``.

These four rules were scattered across sprint prompt preambles, where they
rotated out of sight every ~12 days. They are copied into ``CONTRIBUTING.md``
so they survive the rollover, but a copy is only durable if **something keeps
the two in step**. This test is that something.

It is intentionally stdlib-only (no pytest imports needed beyond collection)
and the current-sprint directory is **resolved**, not hardcoded, so the next
sprint's directory becomes the source of truth automatically.
"""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SPRINT_ROOT = PROJECT_ROOT / "docs" / "planning" / "EPIC_4"
CONTRIBUTING = PROJECT_ROOT / "CONTRIBUTING.md"

#: The four rule headings, in the order the prompt lists them. Each is a
#: canonical name — the CONTRIBUTING section must contain every one, and the
#: current-sprint prompt preamble must still describe every one.
#:
#: Matched as substrings so a trailing qualifier (``(Sprint 40 P10e)``) does
#: not break the check. Keyed by the headline phrase a reader greps for.
_RULE_PHRASES: tuple[str, ...] = (
    "Pin by identity, not count",
    "When a classification moves, sweep the changed",
    "Never `git stash`",
    "grep the PR's own docs",
)


def _current_sprint_dir() -> Path:
    """The highest-numbered ``SPRINT_<n>`` directory.

    Derived rather than pinned (``check_doc_figures.current_sprint_dir``'s
    rationale applies verbatim): hardcoding ``SPRINT_40`` would silently take
    every later sprint's prompt out of scope the moment the next directory
    lands, and the test would keep reporting PASS against a frozen target.
    """
    numbered = [
        (int(m.group(1)), p)
        for p in SPRINT_ROOT.iterdir()
        if p.is_dir() and (m := re.fullmatch(r"SPRINT_(\d+)", p.name))
    ]
    assert numbered, f"no SPRINT_<n> directory under {SPRINT_ROOT}"
    top = max(n for n, _p in numbered)
    return next(p for n, p in numbered if n == top)


def test_contributing_has_the_review_round_rules_section() -> None:
    """A standalone section header anchors the copy. Without one, any future
    reorganisation of CONTRIBUTING could fold the rules into another heading
    and silently drop them, and a substring-only test would still pass."""
    text = CONTRIBUTING.read_text(encoding="utf-8")
    assert re.search(
        r"^## Review-Round Rules\b", text, re.M
    ), "CONTRIBUTING.md must contain a top-level ## Review-Round Rules section"


def test_every_prompt_rule_is_in_CONTRIBUTING() -> None:
    """Each of the four rules in the current-sprint prompt is in the copy.

    If a sprint prep adds a fifth rule, this test fails and forces the author
    to decide whether it is a durable rule (goes to CONTRIBUTING) or a
    sprint-local practice (stays in the prompt and is removed from
    ``_RULE_PHRASES``). Silent divergence between the two surfaces is what the
    copy was meant to prevent.
    """
    text = CONTRIBUTING.read_text(encoding="utf-8")
    missing = [phrase for phrase in _RULE_PHRASES if phrase not in text]
    assert not missing, f"review-round rule(s) missing from CONTRIBUTING.md: {missing}"


def test_the_current_sprint_prompt_still_lists_these_rules() -> None:
    """The prompt preamble is the live expression; CONTRIBUTING is its mirror.

    Grep is intentional — the file is loose markdown, a parser would couple the
    test to formatting that reviewers routinely churn. A phrase match on four
    distinct sentences is a stable enough signal.

    The sprint directory is resolved, so a rollover does not break this: the
    next sprint's ``prompts/PLAN_PROMPTS.md`` becomes the source of truth.
    """
    sprint = _current_sprint_dir()
    prompt = sprint / "prompts" / "PLAN_PROMPTS.md"
    assert prompt.is_file(), f"current sprint has no prompts/PLAN_PROMPTS.md: {prompt}"
    text = prompt.read_text(encoding="utf-8")
    missing = [phrase for phrase in _RULE_PHRASES if phrase not in text]
    assert not missing, (
        f"prompt {prompt.relative_to(PROJECT_ROOT)} is missing review-round "
        f"rule(s) that CONTRIBUTING claims are carried from it: {missing}"
    )


def test_resolution_ignores_non_sprint_directories() -> None:
    """``SPRINT_<n>`` only; a stray directory must not become the "current sprint".

    ``EPIC_4`` holds non-sprint dirs (``PROJECT_PLAN`` artifacts, retrospective
    collations); the fullmatch guard is what keeps them out. A permissive
    ``startswith("SPRINT_")`` would catch ``SPRINT_NOTES`` and crash on ``int``.
    """
    siblings = {p.name for p in SPRINT_ROOT.iterdir() if p.is_dir()}
    non_sprint = {n for n in siblings if not re.fullmatch(r"SPRINT_\d+", n)}
    picked = _current_sprint_dir()
    assert picked.name not in non_sprint
    assert re.fullmatch(r"SPRINT_\d+", picked.name)

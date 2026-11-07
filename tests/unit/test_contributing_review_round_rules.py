"""Sprint 40 P10e: the Review-Round Rules in ``CONTRIBUTING.md``.

These four rules were scattered across sprint prompt preambles, where they
rotated out of sight every ~12 days. They are copied into ``CONTRIBUTING.md``
so they survive the rollover, but a copy is only durable if **something keeps
the two in step**. This test is that something.

The test is intentionally stdlib-only and the current-sprint directory is
**resolved**, not hardcoded, so the next sprint's directory becomes the source
of truth automatically.

Parity is checked **symmetrically**, by extracting each surface's rule headings
and comparing the normalised sets (PR #1801 review). An earlier version pinned
four hardcoded phrases and asked each surface whether they were present — which
a fifth rule added to either side alone would silently satisfy, since neither
check discovers what the OTHER document actually contains.
"""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SPRINT_ROOT = PROJECT_ROOT / "docs" / "planning" / "EPIC_4"
CONTRIBUTING = PROJECT_ROOT / "CONTRIBUTING.md"


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


# ------------------------------------------------- normalisation & extraction


_TRAILING_PUNCT = re.compile(r"[.,;:]+\s*$")
_BACKTICK_RUN = re.compile(r"`+")
_WHITESPACE = re.compile(r"\s+")


def _normalise(heading: str) -> str:
    """Make two surfaces' rule headings directly comparable.

    The two sources style them differently:

    * **CONTRIBUTING** uses ``### Pin by identity, not count`` — a markdown
      level-3 heading, no trailing punctuation.
    * **the prompt preamble** uses ``- **Pin by identity, not count.**`` — a
      bold bullet, usually with a trailing period, and sometimes with a word
      capitalised for emphasis (``SET``) that reads ordinary-case in the copy.

    Normalisation strips both forms down to the same canonical key:
    lowercase, no backticks, no trailing punctuation, single-spaced. The
    comparison is then exact, so a genuinely different heading cannot collide.
    """
    s = _BACKTICK_RUN.sub("", heading).strip()
    s = _TRAILING_PUNCT.sub("", s)
    s = _WHITESPACE.sub(" ", s)
    return s.lower()


def _extract_contributing_rules(text: str) -> set[str]:
    """Every ``### `` heading inside the ``## Review-Round Rules`` section.

    Bounded between the section header and the next ``## `` heading. Reading
    unbounded would pick up unrelated ``### `` headings elsewhere in the file
    — exactly the drift the parity check exists to make visible.
    """
    m = re.search(
        r"^## Review-Round Rules\b[^\n]*\n(.*?)(?=^## |\Z)",
        text,
        re.M | re.S,
    )
    if not m:
        return set()
    body = m.group(1)
    return {_normalise(h) for h in re.findall(r"^###[ \t]+(.+?)[ \t]*$", body, re.M)}


def _extract_prompt_rules(text: str) -> set[str]:
    """Every first-bold phrase in a bullet under the ``**Review-round rules**`` block.

    Bounded between the ``**Review-round rules**`` header and the first blank
    line that is followed by non-bullet text — the same cue a reader uses to
    see the block ending. The first ``**...**`` of each bullet is the rule
    name; anything after it is prose.
    """
    # The bullet marker class is ``[-*+]`` on BOTH the block boundary and the
    # per-line match. Markdown accepts all three as list markers; narrowing to
    # ``-`` lets a one-sided rule written with ``*`` or ``+`` escape the parity
    # check — the block terminates at the ``*``/``+`` line (so later bullets
    # vanish) OR the line is read but the regex rejects it (so the rule
    # vanishes). Either way the extracted set stays equal to the other
    # surface's and a real divergence reads as clean (PR #1801 review r4).
    #
    # The block boundary is "blank line, then a line that is NOT a bullet and
    # NOT indented continuation". A bullet is ``[-*+]`` followed by whitespace
    # — expressed as a negative lookahead so a line starting with ``**Another
    # header**`` (which begins with ``*``, a valid bullet marker) still counts
    # as the block end (``**`` is not ``* ``). A simple char-class like
    # ``[^\s\-*+]`` can't express that distinction.
    m = re.search(
        r"^\*\*Review-round rules\*\*[^\n]*\n(.*?)(?=\n\n(?![-*+][ \t]|\s))",
        text,
        re.M | re.S,
    )
    if not m:
        return set()
    body = m.group(1)
    rules: set[str] = set()
    for raw in body.splitlines():
        line = raw.lstrip()
        # Match against ``line.lstrip()`` so indented bullets are not silently
        # dropped — an earlier form guarded on the stripped line but matched
        # against the raw one, so ``  - **Foo** bar`` failed at position 0
        # and the rule disappeared from the extracted set (PR #1801 review r2).
        #
        # No separate ``startswith`` guard: a redundant space-only guard
        # discarded tab-separated bullets (``-\t**Foo**``) that the regex below
        # accepts, so a fifth rule in that form could escape the parity check
        # (PR #1801 review r3). The regex is the single source of truth about
        # what counts as a rule bullet.
        bold = re.match(r"[-*+][ \t]+\*\*(.+?)\*\*", line)
        if bold:
            rules.add(_normalise(bold.group(1)))
    return rules


# ------------------------------------------------- the checks


def test_contributing_has_the_review_round_rules_section() -> None:
    """A standalone section header anchors the copy. Without one, any future
    reorganisation of CONTRIBUTING could fold the rules into another heading
    and silently drop them, and a substring-only test would still pass."""
    text = CONTRIBUTING.read_text(encoding="utf-8")
    assert re.search(
        r"^## Review-Round Rules\b", text, re.M
    ), "CONTRIBUTING.md must contain a top-level ## Review-Round Rules section"


def _both_rule_sets() -> tuple[set[str], set[str], Path]:
    sprint = _current_sprint_dir()
    prompt = sprint / "prompts" / "PLAN_PROMPTS.md"
    assert prompt.is_file(), f"current sprint has no prompts/PLAN_PROMPTS.md: {prompt}"
    contrib = _extract_contributing_rules(CONTRIBUTING.read_text(encoding="utf-8"))
    pr = _extract_prompt_rules(prompt.read_text(encoding="utf-8"))
    return contrib, pr, prompt


def test_the_two_surfaces_hold_the_SAME_SET_of_rules() -> None:
    """Symmetric parity: neither side may carry a rule the other does not.

    A fifth rule in the prompt alone, OR in CONTRIBUTING alone, fails this
    test. The earlier form — four hardcoded phrases asked of each surface —
    could not: it only noticed rules it already knew about, so adding one in
    one place left every assertion green (PR #1801 review).
    """
    contrib, prompt_rules, prompt_path = _both_rule_sets()
    assert contrib, "CONTRIBUTING.md Review-Round Rules section parsed to no rules"
    assert prompt_rules, (
        f"{prompt_path.relative_to(PROJECT_ROOT)} Review-round rules block " "parsed to no rules"
    )
    only_contrib = contrib - prompt_rules
    only_prompt = prompt_rules - contrib
    assert not only_contrib and not only_prompt, (
        "review-round rules diverge between surfaces:\n"
        f"  only in CONTRIBUTING.md: {sorted(only_contrib)}\n"
        f"  only in {prompt_path.relative_to(PROJECT_ROOT)}: {sorted(only_prompt)}"
    )


def test_a_one_sided_fifth_rule_is_detected_in_either_direction() -> None:
    """The regression case for the parity test itself.

    An earlier version was vacuously true: four hardcoded phrases, asked of
    each surface. Adding a fifth rule to either file alone left every
    assertion green. This test re-runs the real extractors against synthetic
    one-sided inputs and demands the discrepancy be visible in BOTH
    directions, so the parity check cannot regress to the earlier form.
    """
    base_contrib = (
        "## Review-Round Rules\n"
        "\npreamble\n"
        "\n### Alpha\n"
        "body\n"
        "\n### Beta\n"
        "body\n"
        "\n## Next Section\n"
    )
    base_prompt = (
        "**Review-round rules** (recorded here):\n"
        "- **Alpha.** body\n"
        "- **Beta.** body\n"
        "\n**Another header**\n"
    )
    assert _extract_contributing_rules(base_contrib) == _extract_prompt_rules(base_prompt)

    # A fifth rule in CONTRIBUTING only.
    contrib_plus = base_contrib.replace("### Beta\n", "### Beta\nbody\n\n### Gamma\n")
    assert _extract_contributing_rules(contrib_plus) - _extract_prompt_rules(base_prompt) == {
        "gamma"
    }

    # A fifth rule in the prompt only.
    prompt_plus = base_prompt.replace("- **Beta.** body\n", "- **Beta.** body\n- **Gamma.** body\n")
    assert _extract_prompt_rules(prompt_plus) - _extract_contributing_rules(base_contrib) == {
        "gamma"
    }

    # A fifth rule in the prompt only, written with a TAB after the dash — valid
    # Markdown, accepted by the capture regex. An earlier guard rejected it on
    # the space-only ``startswith("- ")`` test, so a one-sided rule in this form
    # silently escaped the parity check (PR #1801 review r3).
    prompt_tab = base_prompt.replace("- **Beta.** body\n", "- **Beta.** body\n-\t**Gamma.** body\n")
    assert _extract_prompt_rules(prompt_tab) - _extract_contributing_rules(base_contrib) == {
        "gamma"
    }

    # A fifth rule in the prompt only, written with an asterisk bullet, and
    # another with a plus bullet. Both are valid Markdown list markers; an
    # earlier form matched only ``-`` on both the block boundary and the per-
    # line regex, so a ``*``/``+`` rule either terminated the block (dropping
    # later bullets) or was rejected by the line regex — the rule vanished
    # from the extracted set and parity read clean (PR #1801 review r4).
    for marker in ("*", "+"):
        prompt_marker = base_prompt.replace(
            "- **Beta.** body\n",
            f"- **Beta.** body\n{marker} **Gamma.** body\n",
        )
        assert _extract_prompt_rules(prompt_marker) - _extract_contributing_rules(base_contrib) == {
            "gamma"
        }, f"bullet marker {marker!r} escaped parity"


def test_prompt_extractor_sees_indented_bullets() -> None:
    """A nested bullet must not silently vanish from the rule set.

    Markdown lets bullet items carry sub-items as indented bullets. The
    earlier form guarded on ``line.lstrip()`` but matched against the raw
    line, so an indented rule passed the guard and failed the regex at
    position 0 — it fell out of the set entirely, and the parity test could
    not see it (PR #1801 review).
    """
    body = (
        "**Review-round rules** (recorded here):\n"
        "- **Alpha.** body\n"
        "  - **Nested.** an indented rule\n"
        "- **Beta.** body\n"
        "\n**Another header**\n"
    )
    assert _extract_prompt_rules(body) == {"alpha", "nested", "beta"}


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


def test_normalisation_folds_the_two_styles_to_the_same_key() -> None:
    """Prompt bullets include trailing periods and backticks; CONTRIBUTING headings don't.

    The extractors feed ``_normalise`` the inner bold content (``**`` already
    stripped by the capture group), so this test pins the remaining folds:
    trailing period, backticks around a code span, capitalisation. If
    normalisation is too strict these styles disagree and parity is
    impossible; if too lax, a different rule collides with an existing one.
    """
    assert _normalise("Never `git stash` to switch branches.") == _normalise(
        "Never git stash to switch branches"
    )
    assert _normalise("Pin by identity, not count") == _normalise("Pin by identity, not count.")
    assert _normalise("WHEN a classification moves") == _normalise("when a classification moves")
    # ...but genuinely different headings must still differ.
    assert _normalise("Pin by identity, not count") != _normalise("Pin by count, not identity")

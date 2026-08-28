"""A figure copied into prose goes stale; the source it came from does not.

Every fixture in this file is a **real line that really shipped**, not an
invented example of what a stale figure might look like. A checker tested only
against idealised inputs proves that it matches its author's mental model of the
defect, which is precisely the thing that was wrong in each of these cases.

The four instances, all from one week of Sprint 39 prep:

* ``29.0`` research hours, published in five places across four files under the
  words *"derived by summing the per-unknown estimates, not recalled"*. The sum
  had been ``40.0`` since the file's first commit.
* ``12 of 14`` figures reproduced, written while the last measurement was still
  running; it came back clean, making the real count ``13``.
* ``unknowns: 31`` printed two lines from a ``30`` for the same quantity.
* Three docs corrected from ``29.0`` to ``40.0``; the fourth file in the same PR
  was not.

The regression tests below are equally concrete. Each one names the specific
wrong behaviour an earlier revision of the checker actually had — a substring
blocklist that matched inside a word, a number pattern that captured ``"."`` —
because those are the failures that made it report success on real defects.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
_SPEC = importlib.util.spec_from_file_location(
    "check_doc_figures",
    PROJECT_ROOT / "scripts" / "sprint_audit" / "check_doc_figures.py",
)
assert _SPEC and _SPEC.loader
cdf = importlib.util.module_from_spec(_SPEC)
sys.modules["check_doc_figures"] = cdf
_SPEC.loader.exec_module(cdf)


#: Pinned rather than derived. Deriving them here would re-implement the thing
#: under test, and the test would then pass against a broken derivation.
TRUTHS: dict[str, float | int] = {
    "Solve": 111,
    "Match": 96,
    "Translate": 135,
    "genuine floor": 73,
    "path_solve_license cohort": 11,
    "path_solve_terminated": 0,
    "leak-gate in-scope goldens": 186,
    "Sprint 39 unknowns": 30,
    "Sprint 39 research hours": 40.0,
    "dangling mcp_file_used rows": 14,
    "Task-2 figures reproduced": 13,
}

DOC = Path("docs/planning/EPIC_4/SPRINT_39/PREP_PLAN.md")


def _scan(text: str):
    return cdf.scan_line(DOC, 1, text, TRUTHS)


def _facts(text: str) -> set[str]:
    findings, _ = _scan(text)
    return {f.fact for f in findings}


# --------------------------------------------------------------- the real four


@pytest.mark.parametrize(
    ("line", "fact"),
    [
        pytest.param(
            "✅ **COMPLETE — 30 unknowns, 10 categories, 29.0 research hours.**",
            "Sprint 39 research hours",
            id="research-hours-headline",
        ),
        pytest.param(
            "| Research time | 28–36 h | **29.0 h** |",
            "Sprint 39 research hours",
            id="research-hours-acceptance-table",
        ),
        pytest.param(
            "**30 unknowns across 10 categories, 29.0 research hours**.",
            "Sprint 39 research hours",
            id="research-hours-prompts-header",
        ),
        pytest.param(
            "- **12 of 14 figures reproduced outright**, including the full KPI block",
            "Task-2 figures reproduced",
            id="twelve-of-fourteen",
        ),
        pytest.param(
            'print(f"unknowns: 31 | missing-section: {len(bad)}")',
            "Sprint 39 unknowns",
            id="unknowns-31-vs-30",
        ),
    ],
)
def test_catches_the_figures_that_actually_shipped_wrong(line: str, fact: str) -> None:
    """Fail-before evidence: each of these reached `main` and was caught by hand."""
    assert fact in _facts(line)


@pytest.mark.parametrize(
    "line",
    [
        pytest.param(
            "✅ **COMPLETE — 30 unknowns, 10 categories, 40.0 research hours**",
            id="research-hours-corrected",
        ),
        pytest.param(
            "**13 of 14** numbers reproduced; 14 claims reproduced.",
            id="thirteen-of-fourteen",
        ),
        pytest.param(
            "Solve **111** · Match **96** · Translate **135** · all-219 Match **99**",
            id="current-kpi-block",
        ),
        pytest.param(
            "leak gate clean at **186** in-scope / **7** allowlisted",
            id="current-leak-scope",
        ),
        pytest.param(
            "the live count of dangling `mcp_file_used` rows is **14**",
            id="current-dangling",
        ),
        pytest.param("genuine floor **73** (baseline 73 + 0 entries)", id="current-floor"),
    ],
)
def test_correct_figures_do_not_fire(line: str) -> None:
    findings, reason = _scan(line)
    assert reason is None, "a correct line must be checked, not exempted"
    assert findings == []


# ------------------------------------------------------- checker's own defects


def test_substring_scoping_does_not_match_inside_a_word() -> None:
    """``"or 75"`` as a substring matches inside "fl**oor 75**".

    An earlier revision scoped out the open 73/74/75 discussion with a substring
    blocklist. ``"or 75"`` then matched inside the word *floor*, disabling the
    floor check entirely — it reported clean on a line citing the wrong floor.
    """
    assert "genuine floor" in _facts("`path_solve_terminated` is 4 and the genuine floor 75.")


def test_the_open_floor_question_is_still_scoped_out() -> None:
    """…but the real "73, 74 or 75" discussion must not be flagged."""
    assert _facts("**The floor is 73, 74 or 75** — the 74 reading is live.") == set()


def test_the_number_pattern_cannot_match_a_bare_dot() -> None:
    """``[0-9.]+`` matches ``"."`` — and did.

    An earlier revision captured the dot inside ``29.0``, so the comparison ran
    against ``float(".")``, raised ValueError, was swallowed by the
    ``except ValueError: continue`` guard, and the single most important figure
    passed silently.

    This asserts the invariant on ``NUM`` **directly**. Asserting it end-to-end
    does not work: the current patterns anchor on adjacent text, so they capture
    ``29.0`` correctly even under the broken alternation, and the test passes
    against the defect — which is what the first version of this test did.
    """
    assert cdf.re.fullmatch(cdf.NUM, ".") is None, "NUM must not accept a bare dot"
    assert cdf.re.fullmatch(cdf.NUM, "29.0") is not None
    assert cdf.re.fullmatch(cdf.NUM, "14") is not None


def test_a_decimal_figure_is_captured_whole() -> None:
    findings, _ = _scan("30 unknowns across 10 categories, 29.0 research hours.")
    cited = {f.cited for f in findings if f.fact == "Sprint 39 research hours"}
    assert cited == {"29.0"}, f"expected the whole number, got {cited}"


def test_a_target_range_is_not_read_as_a_claim() -> None:
    """``| Research time | 28–36 h | **29.0 h** |`` states a target and cites a figure.

    Blocking the whole line on the range — the first attempt — also blocked the
    claim sitting beside it, so the row reported clean.
    """
    findings, _ = _scan("| Research time | 28–36 h | **29.0 h** |")
    cited = {f.cited for f in findings if f.fact == "Sprint 39 research hours"}
    assert "29.0" in cited
    assert "28" not in cited and "36" not in cited


def test_dangling_pattern_does_not_reach_into_the_next_clause() -> None:
    """``(… / 14 dangling), all correct — P7 must name which`` cites 14, not 7.

    A forward window of 32 non-digit characters scanned past the clause and
    captured the ``7`` of *P7*, producing "cited 7, derived 14" on a correct line.
    """
    assert _facts("(48 / 40 / 34 / 31 / 14 dangling), all correct — P7 must name which") == set()


def test_dangling_pattern_does_not_read_the_population_as_the_count() -> None:
    """``14 of the 48 dangling`` cites 14; ``48`` is the population it is drawn from."""
    assert _facts("· 31 presolve∧match∧convex-candidate · 14 of the 48 dangling.") == set()


def test_research_hours_does_not_reach_across_a_clause_into_another_figure() -> None:
    """A ``[^0-9]{0,24}`` window spanned ``"**, leak gate **"`` and captured 186."""
    line = "**Prep Task 2 — 30 unknowns, 40.0 research hours**, leak gate **186** in-scope."
    assert _facts(line) == set()


# ------------------------------------------------------------------ exemptions


def test_a_correction_is_not_a_claim() -> None:
    """Recording a wrong figure must not itself trip the check.

    These lines exist because the errors were written down rather than quietly
    patched. Penalising them would delete the audit trail.
    """
    _, reason = _scan("The 29.0 h figure published at creation was wrong; the sum is 40.0 h.")
    assert reason is not None


def test_a_movement_line_is_exempt_and_the_reason_is_reported() -> None:
    """``Solve 108 → 111`` is history on the left by construction.

    The reason is returned rather than dropped: an exemption set that grows
    invisibly is the same defect class this check exists to catch.
    """
    findings, reason = _scan("Solve 108 → 111, Match 94 → 96 over the sprint.")
    assert findings == []
    assert reason is not None and "movement" in reason


def test_inline_escape_hatch_works() -> None:
    line = "Sprint 36 closed FLAT at Solve 108. <!-- figures-ok: historical close -->"
    findings, reason = _scan(line)
    assert findings == []
    assert reason is not None and "figures-ok" in reason


def test_an_ordinary_line_is_not_exempt() -> None:
    """The exemption markers must not swallow ordinary prose."""
    _, reason = _scan("Solve **108** at the close.")
    assert reason is None


# -------------------------------------------------------------- diff & scoping


def test_only_added_lines_are_in_scope(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Untouched history must stay out of scope.

    ``CHANGELOG.md`` holds hundreds of figures that were correct when written.
    Scanning whole files would bury the signal, and the check would be disabled.
    """
    import subprocess

    repo = tmp_path / "r"
    repo.mkdir()
    run = lambda *a: subprocess.run(a, cwd=repo, check=True, capture_output=True)  # noqa: E731
    run("git", "init", "-q")
    run("git", "config", "user.email", "t@t")
    run("git", "config", "user.name", "t")
    doc = repo / "d.md"
    doc.write_text("Sprint 36 closed at Solve 108.\n", encoding="utf-8")
    run("git", "add", "d.md")
    run("git", "commit", "-qm", "base")
    doc.write_text("Sprint 36 closed at Solve 108.\nNow Solve 108.\n", encoding="utf-8")

    monkeypatch.setattr(cdf, "PROJECT_ROOT", repo)
    changed = cdf.changed_doc_lines("HEAD")
    lines = [t for _p, rows in changed.items() for _n, t in rows]
    assert lines == ["Now Solve 108."], "only the added line belongs in scope"


def test_a_fact_with_a_missing_source_is_omitted_not_defaulted() -> None:
    """A future deliverable must not read as a satisfied check."""

    def _missing() -> int:
        raise FileNotFoundError("not written yet")

    fact = cdf.Fact(
        name="future thing",
        derive=_missing,
        source="a doc that does not exist yet",
        patterns=(cdf.re.compile(rf"future\s+(?P<value>{cdf.NUM})"),),
    )
    monkey = cdf.FACTS
    try:
        cdf.FACTS = (fact,)
        assert "future thing" not in cdf.derive_truths()
    finally:
        cdf.FACTS = monkey


def test_no_registered_fact_has_a_rotted_derivation() -> None:
    """A fact must either derive, or be absent for the one permitted reason.

    "Absent" and "broken" are different, and the difference matters: a fact
    whose source is an unmerged deliverable is legitimately underivable
    (``FileNotFoundError``, which ``derive_truths`` skips by design), while a
    fact whose source moved or whose schema changed raises something else and
    would silently take its citations out of scope while the check still
    reported PASS.

    An earlier version of this test asserted that *every* fact derives, and
    failed the moment it ran on a branch where a Task-2 deliverable had not
    landed — flagging a working design as a defect.
    """
    rotted: list[str] = []
    for fact in cdf.FACTS:
        try:
            fact.derive()
        except FileNotFoundError:
            continue  # source not written yet — permitted, and skipped by design
        except Exception as exc:  # noqa: BLE001 - collected, then asserted on
            rotted.append(f"{fact.name}: {type(exc).__name__}: {exc}")
    assert rotted == [], f"facts whose derivation is broken: {rotted}"


def test_every_fact_has_at_least_one_pattern_with_a_value_group() -> None:
    for fact in cdf.FACTS:
        assert fact.patterns, f"{fact.name} has no patterns"
        for pattern in fact.patterns:
            assert "value" in pattern.groupindex, f"{fact.name}: {pattern.pattern}"

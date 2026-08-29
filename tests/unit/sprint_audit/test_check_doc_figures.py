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
# The module mutates global process state on import (sys.path.insert, so it can
# reach `kpi_block` / `floor_tracker` / `check_golden_staleness`). Snapshot and
# restore sys.path so this dynamic load cannot leak import-resolution order into
# the rest of the pytest run and cause order-dependent failures.
# Same pattern, and the same reason, as tests/unit/test_presolve_divergence_classify.py.
_saved_sys_path = list(sys.path)
try:
    _SPEC.loader.exec_module(cdf)
finally:
    sys.path[:] = _saved_sys_path


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
    "current-sprint unknowns": 30,
    "current-sprint research hours": 40.0,
    "dangling mcp_file_used rows": 14,
    "Task-2 figures reproduced": 13,
}

# Derived, like the implementation. Pinning a sprint number here would make the
# suite fail at the next rollover on a behaviour that had not changed.
_SPRINT = cdf.current_sprint_dir()
assert _SPRINT is not None, "no SPRINT_<n> directory found; the scope would be empty"
DOC = _SPRINT.relative_to(PROJECT_ROOT) / "PREP_PLAN.md"


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
            "current-sprint research hours",
            id="research-hours-headline",
        ),
        pytest.param(
            "| Research time | 28–36 h | **29.0 h** |",
            "current-sprint research hours",
            id="research-hours-acceptance-table",
        ),
        pytest.param(
            "**30 unknowns across 10 categories, 29.0 research hours**.",
            "current-sprint research hours",
            id="research-hours-prompts-header",
        ),
        pytest.param(
            "- **12 of 14 figures reproduced outright**, including the full KPI block",
            "Task-2 figures reproduced",
            id="twelve-of-fourteen",
        ),
        pytest.param(
            'print(f"unknowns: 31 | missing-section: {len(bad)}")',
            "current-sprint unknowns",
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
    cited = {f.cited for f in findings if f.fact == "current-sprint research hours"}
    assert cited == {"29.0"}, f"expected the whole number, got {cited}"


def test_a_target_range_is_not_read_as_a_claim() -> None:
    """``| Research time | 28–36 h | **29.0 h** |`` states a target and cites a figure.

    Blocking the whole line on the range — the first attempt — also blocked the
    claim sitting beside it, so the row reported clean.
    """
    findings, _ = _scan("| Research time | 28–36 h | **29.0 h** |")
    cited = {f.cited for f in findings if f.fact == "current-sprint research hours"}
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


# ------------------------------------------------- defects found in PR review


def test_the_module_never_uses_the_unsafe_number_alternation() -> None:
    """``[0-9.]+`` must not appear anywhere, including in the derivations.

    The module documents why that alternation is unsafe and then used it inside
    ``_research_hours`` — deriving the very figure whose corruption motivated
    the constant. A doc-comment is not a constraint; this is.
    """
    src = (PROJECT_ROOT / "scripts" / "sprint_audit" / "check_doc_figures.py").read_text(
        encoding="utf-8"
    )
    offenders = [
        line.strip()
        for line in src.split("\n")
        if "[0-9.]+" in line and not line.lstrip().startswith(("#", "*", '"'))
    ]
    assert offenders == [], f"unsafe number pattern in use: {offenders}"


def test_dangling_count_does_not_depend_on_the_working_directory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The DB stores repo-relative paths; resolving them against CWD miscounts.

    Measured before the fix: from ``src/`` this returned **48** — the whole
    presolve population — instead of 14, because nothing resolved. A wrong
    derived truth is worse than no check: every correct citation of 14 would
    then be reported as contradicting it.
    """
    from_root = cdf._dangling_presolve_rows()
    monkeypatch.chdir(PROJECT_ROOT / "src")
    assert cdf._dangling_presolve_rows() == from_root


@pytest.mark.parametrize(
    ("line", "is_movement"),
    [
        ("Solve 108 → 111", True),
        ("Solve **108** → **111**", True),
        ("`path_solve_terminated` 4 → 0", True),
        pytest.param("<!-- see the note -->", False, id="html-comment-terminator"),
        pytest.param("graph: A --> B", False, id="mermaid-edge"),
        pytest.param("def f() -> int:", False, id="type-hint"),
    ],
)
def test_movement_requires_digits_on_both_sides(line: str, is_movement: bool) -> None:
    """A bare ``->`` exempted HTML comments, Mermaid edges and type hints.

    Every such line silently left the scan — a false negative in a tool whose
    entire job is to not have any.
    """
    assert bool(cdf._MOVEMENT.search(line)) is is_movement


def test_added_content_beginning_with_plus_is_not_dropped(tmp_path: Path) -> None:
    """``+++ b/…`` is a header only before the first hunk.

    An added line holding ``++ foo`` arrives in the diff as ``+++ foo``.
    Excluding it by prefix discarded real markdown content, which is a false
    negative that no amount of pattern work would recover.
    """
    import subprocess

    repo = tmp_path / "r"
    repo.mkdir()
    run = lambda *a: subprocess.run(a, cwd=repo, check=True, capture_output=True)  # noqa: E731
    run("git", "init", "-q")
    run("git", "config", "user.email", "t@t")
    run("git", "config", "user.name", "t")
    doc = repo / "d.md"
    doc.write_text("base\n", encoding="utf-8")
    run("git", "add", "d.md")
    run("git", "commit", "-qm", "base")
    doc.write_text("base\n++ emphasis with Solve 108\nplain Solve 108\n", encoding="utf-8")

    original = cdf.PROJECT_ROOT
    try:
        cdf.PROJECT_ROOT = repo
        lines = [t for _p, rows in cdf.changed_doc_lines("HEAD").items() for _n, t in rows]
    finally:
        cdf.PROJECT_ROOT = original
    assert "++ emphasis with Solve 108" in lines


def _install_hooks_recipe() -> str:
    makefile = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")
    return makefile.split("install-hooks:", 1)[1].split("\n\n", 1)[0]


def test_the_pre_push_hook_anchors_itself_to_the_repo_root() -> None:
    """The hook derives figures from repo-relative paths, so cwd matters.

    Git does run hooks from the worktree root — measured, not assumed — but a
    worktree or a manual invocation need not, and the failure mode there is a
    silently wrong derived truth rather than a crash.
    """
    assert "rev-parse --show-toplevel" in _install_hooks_recipe()


def test_the_hook_is_installed_via_gits_resolved_hooks_directory() -> None:
    """``.git/hooks`` is wrong in two common setups, both measured.

    * In a **linked worktree** ``.git`` is a *file*, so ``mkdir -p .git/hooks``
      fails outright with "Not a directory" and the target errors out — while
      the hook text it installs talks about worktrees.
    * With **core.hooksPath** set, ``.git/hooks`` is not where git looks, so a
      hook installed there silently never runs.

    ``git rev-parse --git-path hooks`` resolves all three cases (plain repo,
    worktree, core.hooksPath); verified against each.
    """
    recipe = _install_hooks_recipe()
    assert "--git-path hooks" in recipe
    assert ".git/hooks" not in recipe, "hardcoding .git/hooks breaks worktrees and core.hooksPath"


# ------------------------------- false-positive pressure (PR #1711, round 2)


@pytest.mark.parametrize(
    ("line", "why"),
    [
        pytest.param(
            "| Create `src/nlp2mcp/reporting/` structure | 1h | Module skeleton |",
            "an unrelated hours cell in a Sprint-16 plan",
            id="hours-cell-without-the-label",
        ),
        pytest.param(
            "- Translate: 21 (+4 of 14 new, 29%)", "a ratio out of fourteen", id="n-of-14-ratio"
        ),
        pytest.param("covered 9 of 14 categories", "another ratio", id="n-of-14-categories"),
        pytest.param(
            "Category 1 (Floor Classification): 3 unknowns",
            "a per-category count, not the total",
            id="per-category-unknowns",
        ),
        pytest.param(
            "- 12 in-scope models: bearing, chain, cpack",
            "'in-scope' is used for other populations",
            id="in-scope-non-golden",
        ),
    ],
)
def test_unrelated_prose_does_not_fire(line: str, why: str) -> None:
    """False positives are what get a check disabled.

    Each of these fired before: an hours cell in an unrelated Sprint-16 plan was
    read as a Sprint-39 research-hours citation, `+4 of 14` as the Task-2 verdict
    count, and every per-category "N unknowns" as the total.
    """
    findings, _ = _scan(line)
    assert findings == [], f"false positive on {why}: {[f.fact for f in findings]}"


@pytest.mark.parametrize(
    ("line", "fact"),
    [
        ("| Research time | 28–36 h | **29.0 h** |", "current-sprint research hours"),
        ("| Total unknowns | 22–30 (aim 25+) | **31** |", "current-sprint unknowns"),
    ],
)
def test_an_acceptance_row_is_read_from_its_last_cell(line: str, fact: str) -> None:
    """`| label | target range | claim |` — the claim is the LAST cell.

    A forward scan stops at the target range's first number, which is then
    correctly discarded as a range endpoint — so the real figure was never
    reached and the row reported clean.
    """
    assert fact in _facts(line)


def test_archived_docs_are_out_of_scope() -> None:
    """A closed sprint's log saying "Solve 108" is correct for that sprint.

    Unscoped, a whole-corpus scan yields 2,376 findings — dominated by archived
    logs. An unreadable check is a disabled check.
    """
    assert cdf.is_live_doc(Path("CHANGELOG.md"))
    assert cdf.is_live_doc(DOC), f"{DOC} is the current sprint and must be live"
    assert not cdf.is_live_doc(Path("docs/planning/EPIC_3/SPRINT_16/PLAN.md"))
    assert not cdf.is_live_doc(Path("docs/planning/EPIC_4/SPRINT_38/SPRINT_LOG.md"))


def test_the_current_sprint_is_the_highest_numbered_one_on_disk() -> None:
    """The scope is derived, so rollover cannot leave it pointing at a closed sprint.

    The previous guard asserted only that ``CURRENT_SPRINT_DIR.is_dir()`` — which
    could never fail, because closed sprints are never deleted: all of
    ``SPRINT_18``…``SPRINT_39`` are still present. Leaving the constant at any
    past sprint satisfied it forever while every new-sprint doc silently fell out
    of scope and the check reported PASS. A vacuous guard, inside the tool whose
    subject is checks that silently narrow.
    """
    import re as _re

    root = PROJECT_ROOT / "docs" / "planning" / "EPIC_4"
    numbered = sorted(
        int(m.group(1))
        for p in root.iterdir()
        if p.is_dir() and (m := _re.fullmatch(r"SPRINT_(\d+)", p.name))
    )
    assert numbered, "no SPRINT_<n> directories found — the scope would be empty"
    assert cdf.current_sprint_dir() == root / f"SPRINT_{numbered[-1]}"


def test_rollover_needs_no_code_edit(tmp_path: Path) -> None:
    """Creating the next sprint's directory moves the scope by itself.

    This is the property the old guard was trying and failing to protect: a
    human must not have to remember to bump a constant, because the failure of
    remembering is silent.
    """
    root = tmp_path / "EPIC_4"
    (root / "SPRINT_38").mkdir(parents=True)
    (root / "SPRINT_39").mkdir()
    assert cdf.current_sprint_dir(root) == root / "SPRINT_39"

    (root / "SPRINT_40").mkdir()
    assert (
        cdf.current_sprint_dir(root) == root / "SPRINT_40"
    ), "scope must follow the new sprint with no code change"


def test_sprint_numbers_are_compared_numerically_not_lexically() -> None:
    """``SPRINT_9`` must not outrank ``SPRINT_40``.

    A string sort puts "SPRINT_9" after "SPRINT_40", which would pin the scope
    to a long-closed sprint the moment the numbering passed 9 — and, being a
    narrowing, would report PASS while doing it.
    """
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for n in (9, 38, 40):
            (root / f"SPRINT_{n}").mkdir()
        assert cdf.current_sprint_dir(root) == root / "SPRINT_40"


def test_a_tree_with_no_sprint_directories_yields_no_sprint_scope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Absent is absent — not "everything is live", and not a crash.

    ``sprint_dir=None`` means *resolve at call time*, so the absence has to be
    injected at the root. (Passing ``None`` explicitly reads like "no sprint" and
    is not — a wart this test found by asserting the wrong thing first.)
    """
    assert cdf.current_sprint_dir(tmp_path) is None

    monkeypatch.setattr(cdf, "SPRINT_ROOT", tmp_path)
    assert not cdf.is_live_doc(DOC.parent / "x.md")
    # the static entries stay live regardless — they are not sprint-scoped
    assert cdf.is_live_doc(Path("CHANGELOG.md"))


def test_check_returns_its_truths_so_reporting_cannot_diverge() -> None:
    """`main` must not re-derive for the coverage line.

    Deriving twice doubles the DB reads and lets the reported coverage describe
    a different derivation from the one the scan used.
    """
    findings, scanned, exemptions, truths, archived = cdf.check("HEAD")
    assert isinstance(truths, dict) and truths, "check() must return the truths it used"


def test_scope_is_measured_from_the_merge_base_not_the_base_tip(tmp_path: Path) -> None:
    """A branch being *behind* base must not pull other people's lines into scope.

    Diffing straight against ``base`` answers "how does the worktree differ from
    base", which is the wrong question. Once base advances, a line another branch
    rewrote appears as *added here* — because this branch still holds the older
    text — so a stale figure someone else introduced gets attributed to this
    change.

    Measured on a real repo rather than argued: with ``main`` one unrelated
    commit ahead, the two-dot diff reports ``+ours untouched`` (never touched on
    this branch) alongside the genuine change; the merge-base diff reports only
    the genuine one.
    """
    import subprocess

    repo = tmp_path / "r"
    repo.mkdir()
    run = lambda *a: subprocess.run(a, cwd=repo, check=True, capture_output=True)  # noqa: E731
    run("git", "init", "-q", "-b", "main")
    run("git", "config", "user.email", "t@t")
    run("git", "config", "user.name", "t")
    doc = repo / "d.md"

    doc.write_text("shared\nours untouched\n", encoding="utf-8")
    run("git", "add", "d.md")
    run("git", "commit", "-qm", "base")

    run("git", "checkout", "-q", "-b", "feature")
    doc.write_text("shared\nours untouched\nfeature adds: Solve 999\n", encoding="utf-8")
    run("git", "commit", "-qam", "feature")

    run("git", "checkout", "-q", "main")
    doc.write_text("shared\nmain rewrote this: Solve 108\n", encoding="utf-8")
    run("git", "commit", "-qam", "main advances")
    run("git", "checkout", "-q", "feature")

    original = cdf.PROJECT_ROOT
    try:
        cdf.PROJECT_ROOT = repo
        lines = [t for _p, rows in cdf.changed_doc_lines("main").items() for _n, t in rows]
    finally:
        cdf.PROJECT_ROOT = original

    assert lines == ["feature adds: Solve 999"], (
        "only this branch's own change belongs in scope; got " f"{lines}"
    )


def test_uncommitted_work_stays_in_scope(tmp_path: Path) -> None:
    """``base...HEAD`` would drop it, and checking before committing is the point."""
    import subprocess

    repo = tmp_path / "r"
    repo.mkdir()
    run = lambda *a: subprocess.run(a, cwd=repo, check=True, capture_output=True)  # noqa: E731
    run("git", "init", "-q", "-b", "main")
    run("git", "config", "user.email", "t@t")
    run("git", "config", "user.name", "t")
    doc = repo / "d.md"
    doc.write_text("shared\n", encoding="utf-8")
    run("git", "add", "d.md")
    run("git", "commit", "-qm", "base")
    run("git", "checkout", "-q", "-b", "feature")
    doc.write_text("shared\ncommitted: Solve 999\n", encoding="utf-8")
    run("git", "commit", "-qam", "feature")
    doc.write_text("shared\ncommitted: Solve 999\nuncommitted: Solve 777\n", encoding="utf-8")

    original = cdf.PROJECT_ROOT
    try:
        cdf.PROJECT_ROOT = repo
        lines = [t for _p, rows in cdf.changed_doc_lines("main").items() for _n, t in rows]
    finally:
        cdf.PROJECT_ROOT = original

    assert "uncommitted: Solve 777" in lines
    assert "committed: Solve 999" in lines


# ------------------------------------------- import hygiene and derivation cost


def test_the_module_works_after_its_sys_path_entry_is_removed() -> None:
    """Restoring ``sys.path`` after a dynamic import must not break derivation.

    The sibling imports (`kpi_block`, `floor_tracker`, `check_golden_staleness`)
    were lazy — inside the derive functions — which quietly made the module
    depend on its ``sys.path`` mutation *surviving* import. A caller that
    politely restored ``sys.path``, which is exactly what a dynamic-import test
    should do, then got ``ModuleNotFoundError: kpi_block`` the moment a fact
    derived.

    This test loads the module in isolation, restores ``sys.path``, and only
    then derives — so the failure it guards against is the one that was actually
    latent, not the one the import line looks like it has.
    """
    import importlib.util as _iu

    spec = _iu.spec_from_file_location(
        "cdf_isolated", PROJECT_ROOT / "scripts" / "sprint_audit" / "check_doc_figures.py"
    )
    assert spec and spec.loader
    module = _iu.module_from_spec(spec)
    # Register before exec: dataclasses resolve their module globals through
    # `sys.modules[__name__]`, and omitting this fails with a bare AttributeError
    # that looks like a defect in the module under test rather than in the test.
    sys.modules[spec.name] = module
    saved = list(sys.path)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = saved
        sys.modules.pop(spec.name, None)

    assert not any("scripts/sprint_audit" in p for p in sys.path), "path entry should be gone"
    truths = module.derive_truths()
    assert truths, "derivation must not depend on the sys.path entry persisting"


def test_the_kpi_block_is_computed_once_per_process() -> None:
    """Six facts read the KPI block; uncached, each re-read a 461 KB DB.

    Measured at five full recomputations per run — roughly 210 ms of a pre-push
    hook spent producing an identical answer.
    """
    assert hasattr(cdf._kpis, "cache_clear"), "_kpis must be cached"
    cdf._kpis.cache_clear()
    first = cdf._kpis()
    assert cdf._kpis() is first, "repeated calls must return the cached object"
    info = cdf._kpis.cache_info()
    assert info.hits >= 1 and info.misses == 1


def test_importing_the_module_leaks_nothing_onto_sys_path() -> None:
    """Not just the entry this module adds — the ones its imports add too.

    Importing the siblings runs *their* path mutations as well:
    `check_golden_staleness` and its transitive imports contribute three further
    entries. Removing only the one added here left those behind, still changing
    import resolution for the rest of the process — the leak this was meant to
    close, minus one entry.
    """
    import importlib.util as _iu

    spec = _iu.spec_from_file_location(
        "cdf_leakcheck", PROJECT_ROOT / "scripts" / "sprint_audit" / "check_doc_figures.py"
    )
    assert spec and spec.loader
    module = _iu.module_from_spec(spec)
    sys.modules[spec.name] = module

    # The siblings must be evicted first. Left in `sys.modules` they are simply
    # rebound on import, their `sys.path.insert` never re-runs, and the probe
    # reports "no leak" whatever the module does — which is what the first
    # version of this test did: it passed against a deliberately reverted fix.
    evicted = {
        name: sys.modules.pop(name)
        for name in ("check_golden_staleness", "floor_tracker", "kpi_block")
        if name in sys.modules
    }
    before = list(sys.path)
    try:
        spec.loader.exec_module(module)
        after = list(sys.path)
    finally:
        sys.modules.pop(spec.name, None)
        sys.modules.update(evicted)
        sys.path[:] = before

    # Exact list, not set membership. The sibling inserts PROJECT_ROOT, which is
    # ALREADY on sys.path under pytest — so a membership test sees nothing new
    # and reports clean while duplicates accumulate. That is the second way this
    # test was decorative; both were found by reverting the fix and watching it
    # pass.
    assert after == before, (
        "import mutated sys.path; "
        f"added {[p for p in after if p not in before] or '(duplicates only)'}, "
        f"length {len(before)} -> {len(after)}"
    )


def test_a_duplicate_sprint_number_is_refused_rather_than_resolved(tmp_path: Path) -> None:
    """`SPRINT_39` and `SPRINT_039` both parse to 39, and both can exist.

    ``max()`` over ``(int, Path)`` tuples does resolve such a tie — Paths *are*
    orderable, so it does not raise — but it resolves *arbitrarily*, by lexical
    order, and would scope the whole check to whichever directory happened to
    sort higher. Silently choosing is the failure this tool exists to prevent,
    so it is refused with a message naming the claimants.
    """
    (tmp_path / "SPRINT_38").mkdir()
    (tmp_path / "SPRINT_39").mkdir()
    (tmp_path / "SPRINT_039").mkdir()
    with pytest.raises(ValueError, match=r"ambiguous current sprint"):
        cdf.current_sprint_dir(tmp_path)


def test_selection_is_keyed_on_the_number_alone(tmp_path: Path) -> None:
    """The winner must not depend on Path ordering when numbers differ."""
    (tmp_path / "SPRINT_9").mkdir()
    (tmp_path / "SPRINT_40").mkdir()
    (tmp_path / "SPRINT_100").mkdir()
    assert cdf.current_sprint_dir(tmp_path) == tmp_path / "SPRINT_100"


def test_derivations_follow_the_scope_across_a_rollover(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scope and truths must move together, or the check reports confident nonsense.

    The scope was derived while the fact derivations stayed pinned to a fixed
    sprint. At the first rollover that combination scans the NEW sprint's docs
    and compares them against the OLD sprint's numbers — so every correct figure
    in the new sprint is reported as contradicting its source. That is worse
    than not checking: it is a check that is wrong in the direction of looking
    authoritative.
    """
    root = tmp_path / "EPIC_4"
    (root / "SPRINT_39").mkdir(parents=True)
    (root / "SPRINT_39" / "KNOWN_UNKNOWNS.md").write_text(
        "## Unknown 1.1: a\n### Estimated Research Time\n1.0 hour\n"
        "\n## Unknown 1.2: b\n### Estimated Research Time\n1.0 hour\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(cdf, "SPRINT_ROOT", root)
    assert cdf._unknown_count() == 2
    assert cdf._research_hours() == 2.0

    # Roll over, with deliberately different content.
    (root / "SPRINT_40").mkdir()
    (root / "SPRINT_40" / "KNOWN_UNKNOWNS.md").write_text(
        "## Unknown 1.1: a\n### Estimated Research Time\n3.0 hours\n", encoding="utf-8"
    )
    assert cdf.current_sprint_dir() == root / "SPRINT_40"
    assert cdf._unknown_count() == 1, "unknowns must come from the sprint being scanned"
    assert cdf._research_hours() == 3.0, "hours must come from the sprint being scanned"


def test_a_sprint_scoped_fact_names_no_sprint_number() -> None:
    """A fact called "Sprint 39 unknowns" that reads Sprint 40's file is a lie.

    The names appear verbatim in findings output, so a pinned name outlives the
    thing it describes exactly as a pinned path did.
    """
    import re as _re

    offenders = [f.name for f in cdf.FACTS if _re.search(r"[Ss]print\s*\d", f.name)]
    assert offenders == [], f"fact names pin a sprint number: {offenders}"

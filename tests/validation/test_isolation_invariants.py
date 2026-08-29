"""The validation suite must never touch `tests/golden/` for build artifacts.

`tests/golden/` holds committed reference `.gms` inputs shared by every xdist
worker. GAMS is invoked with ``cwd=<file>.parent`` and its `.lst` is read back
from the same place, so any test that *runs* GAMS there, or *reads* an artifact
from there, is coupled to whatever the other workers are doing.

The write side is covered behaviourally by `conftest.golden_dir_stays_clean`,
which fails the session if artifacts appear in the directory.

**The read side cannot be covered that way**, and that gap is why this file
exists. `test_solve_min_max_test_mcp` solved a copy in `tmp_path` but still
resolved its `.lst` from `golden_file.parent` — a partial isolation that no test
could catch, because the line sits behind a ``strict=True`` xfail for an
unrelated known bug and is never reached. It would have surfaced only when that
bug was fixed and the xfail lifted, as either a `FileNotFoundError` or, worse, a
silent read of a stale listing left by another worker.

So this is a source-level assertion rather than a behavioural one. That is a
deliberate trade: it is brittle to renaming, and it is the only form that can
see code the runtime never executes.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

VALIDATION_DIR = Path(__file__).resolve().parent

#: What GAMS drops next to the model it is run on.
_ARTIFACT_SUFFIXES = ("lst", "log", "put", "lxi", "gdx")

#: A path rooted at the shared golden directory rather than at a per-test copy.
_SHARED_ROOTS = (
    r"golden_file\.parent",
    r"golden_dir\s*/",
    r"Path\(\s*[\"']tests/golden[\"']\s*\)\s*/",
)

#: The extension must carry its dot. Without it the alternation matches any
#: word ENDING in one of the suffixes — `golden_dir / "catalog"` matched on the
#: "log" of "catalog" — so an ordinary future filename would trip the guard and
#: teach people to delete it.
_ARTIFACT_PATH = re.compile(
    r"(?:" + "|".join(_SHARED_ROOTS) + r")[^\n]{0,80}?\.(?:" + "|".join(_ARTIFACT_SUFFIXES) + r")\b"
)


def _sources() -> list[Path]:
    return sorted(p for p in VALIDATION_DIR.glob("test_*.py") if p.name != Path(__file__).name)


def _code_lines(path: Path) -> list[tuple[int, str]]:
    """Lines with comments and docstring bodies excluded.

    Without this the check flags its own explanatory comments — the fix's
    comment names `golden_file.parent` precisely to say "not this".
    """
    out: list[tuple[int, str]] = []
    in_doc = False
    for n, raw in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        line = raw.split("#", 1)[0]
        fences = line.count('"""') + line.count("'''")
        if in_doc:
            in_doc = fences % 2 == 0
            continue
        if fences:
            in_doc = fences % 2 == 1
            continue
        if line.strip():
            out.append((n, line))
    return out


@pytest.mark.validation
def test_no_artifact_path_is_rooted_at_the_shared_golden_directory() -> None:
    """A `.lst` must be resolved from the copy that was solved, not the golden."""
    offenders = [
        f"{path.name}:{n}: {line.strip()}"
        for path in _sources()
        for n, line in _code_lines(path)
        if _ARTIFACT_PATH.search(line)
    ]
    assert offenders == [], (
        "GAMS artifact paths resolved from the shared golden directory:\n  "
        + "\n  ".join(offenders)
        + "\nResolve them from the per-test copy (e.g. `test_file.with_suffix('.lst')`)."
    )


@pytest.mark.validation
def test_the_guard_can_actually_see_the_defect_it_guards_against() -> None:
    """The pattern must match the real line that shipped.

    Asserted directly, because the guard's own subject matter is code that the
    runtime never reaches — so "the suite is green" says nothing about whether
    this check works.
    """
    shipped = '        lst_file = golden_file.parent / (golden_file.stem + ".lst")'
    assert _ARTIFACT_PATH.search(shipped), "the guard would not have caught the real defect"

    fixed = '        lst_file = test_file.with_suffix(".lst")'
    assert not _ARTIFACT_PATH.search(fixed), "the guard flags the corrected form"


@pytest.mark.validation
@pytest.mark.parametrize(
    "line",
    [
        pytest.param('data = golden_dir / "catalog"', id="catalog-ends-in-log"),
        pytest.param('p = golden_dir / "dialog_notes"', id="dialog"),
        pytest.param('x = golden_dir / "putative_case"', id="putative"),
        pytest.param('f = golden_file.parent / "gdxdump_readme"', id="gdx-prefix"),
    ],
)
def test_the_guard_does_not_fire_on_ordinary_filenames(line: str) -> None:
    """An extension is a dot plus a suffix, not a suffix anywhere in a word.

    Without the dot the alternation matched the "log" of "catalog". A guard that
    fires on unrelated filenames is a guard that gets deleted.
    """
    assert not _ARTIFACT_PATH.search(line)

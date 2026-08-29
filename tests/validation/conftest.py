"""Guards for the validation suite.

`tests/golden/` holds committed reference `.gms` files that several tests feed
to GAMS. GAMS is invoked with ``cwd=<file>.parent`` and its ``.lst`` is read
back from the same place, so pointing it at the golden directory makes every
xdist worker write and read build artifacts in one shared location.

Two files previously coped with that by deleting ``tests/golden/*.lst`` and
``*.log`` in an autouse fixture — after *every* test in the file, including
tests that had written nothing. Under xdist that is a race, not a cleanup: one
worker's teardown deletes another worker's in-flight listing, and the victim
fails with "GAMS did not create .lst file". It is order-dependent, so it passes
in isolation and on a re-run, which is what makes it expensive to diagnose.

The fix was to stop writing there at all — each test copies its golden to
``tmp_path`` first. This guard keeps it that way: the cleanup fixtures are gone,
so a regression no longer hides behind them, it leaves evidence.
"""

from __future__ import annotations

from pathlib import Path

import pytest

#: Build artifacts GAMS drops beside the model it is run on.
_ARTIFACT_PATTERNS = ("*.lst", "*.log", "*.put", "*.lxi", "*.gdx")

GOLDEN_DIR = Path(__file__).resolve().parents[2] / "tests" / "golden"


def _artifacts() -> list[Path]:
    if not GOLDEN_DIR.is_dir():
        return []
    return sorted(p for pattern in _ARTIFACT_PATTERNS for p in GOLDEN_DIR.glob(pattern))


def _fail(when: str, found: list[Path]) -> None:
    names = ", ".join(p.name for p in found)
    pytest.fail(
        f"GAMS artifacts present in {GOLDEN_DIR} {when}: {names}. "
        "Copy the golden file to `tmp_path` and run GAMS on the copy — running "
        "in the shared directory races with other xdist workers. If these are "
        "leftovers from an older run, delete them; nothing should write here."
    )


@pytest.fixture(scope="session", autouse=True)
def golden_dir_stays_clean() -> None:
    """Assert `tests/golden/` holds NO build artifacts, before and after.

    The first version diffed against a pre-existing set and failed only on
    *new* paths. That misses the common regression: a test that rewrites
    `simple_nlp_mcp.lst`, the same filename a previous run left behind, is
    invisible to a set difference — and the directory is not clean either way,
    so the fixture's own name was untrue.

    Checked at session start as well, because a leftover is itself evidence the
    invariant was broken: nothing in this suite writes here any more, so the
    only way an artifact appears is a regression or an aborted older run. Both
    are worth surfacing immediately rather than at the end of a six-minute run.

    Session-scoped rather than per-test: a per-test assertion would itself have
    to inspect a directory other workers are using — the problem it prevents.
    """
    if found := _artifacts():
        _fail("at session start", found)
    yield
    if found := _artifacts():
        _fail("after the session", found)

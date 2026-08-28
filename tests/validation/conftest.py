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


@pytest.fixture(scope="session", autouse=True)
def golden_dir_stays_clean() -> None:
    """Fail if the validation suite wrote build artifacts into `tests/golden/`.

    Asserted at session end rather than per test, because per-test assertion
    would itself have to look at a directory other workers are using — the
    problem it exists to prevent.
    """
    pre_existing = set(_artifacts())
    yield
    leaked = [p for p in _artifacts() if p not in pre_existing]
    if leaked:
        names = ", ".join(p.name for p in leaked)
        pytest.fail(
            f"GAMS artifacts were written into {GOLDEN_DIR}: {names}. "
            "Copy the golden file to `tmp_path` and run GAMS on the copy — "
            "running in the shared directory races with other xdist workers."
        )

"""Sprint 27 #1400: the pipeline must record `mcp_file_generated` as a
repo-relative path so `gamslib_status.json` is machine-portable (no absolute
PROJECT_ROOT prefix leaking the runner's home directory, which would break
byte-identical comparison across machines).

⚠ Sprint 39 P7 renamed the field `mcp_file_used` -> `mcp_file_generated`. The
#1400 PROPERTY is untouched by that — a path is still written, so there is no
"null is an allowed case" to add — but the tests below exercised only
`_repo_relative_path`, never the branch that WRITES the key. That gap meant the
rename could have landed with the writer untouched and this suite still green,
so `test_the_writer_records_the_NEW_key_repo_relatively` was added to close it.
"""

from __future__ import annotations

import pytest

from scripts.gamslib.run_full_test import PROJECT_ROOT, _repo_relative_path
from tests.helpers.anchor_resolver import _code_only, resolve_unique


@pytest.mark.unit
def test_path_under_project_root_is_relativized():
    p = PROJECT_ROOT / "data" / "gamslib" / "mcp" / "launch_mcp_presolve.gms"
    assert _repo_relative_path(p) == "data/gamslib/mcp/launch_mcp_presolve.gms"
    # accepts a string too
    assert _repo_relative_path(str(p)) == "data/gamslib/mcp/launch_mcp_presolve.gms"


@pytest.mark.unit
def test_relativized_path_has_no_absolute_prefix():
    p = PROJECT_ROOT / "data" / "gamslib" / "mcp" / "bearing_mcp_presolve.gms"
    rel = _repo_relative_path(p)
    assert not rel.startswith("/"), f"leaked an absolute path: {rel}"
    assert str(PROJECT_ROOT) not in rel


@pytest.mark.unit
def test_path_outside_project_root_falls_back_unchanged():
    # Graceful fallback — never silently corrupt a path we can't relativize.
    assert _repo_relative_path("/tmp/somewhere/else.gms") == "/tmp/somewhere/else.gms"


@pytest.mark.unit
def test_the_writer_records_the_NEW_key_repo_relatively():
    """⚠ Sprint 39 P7 obligation 4 — pins the WRITER, not just the helper.

    The three tests above call `_repo_relative_path` directly; none reaches
    `run_full_test.py`'s record-writing branch. So before this test the suite
    could not tell `mcp_file_used` from `mcp_file_generated`, and the rename's
    most load-bearing line was the one nothing checked.

    Read out of the source rather than re-executed: driving the branch needs a
    GAMS solve, and the property here is *which key is assigned and with what* —
    which the assignment itself states.

    Sprint 40 P10a: through the shared anchor resolver. The previous whole-module
    ``in`` checks were unscoped and comment-sensitive: renaming the key to
    ``mcp_file_path`` and leaving the old assignment in a ``# was: …`` comment
    passed both. Now the writer must be LIVE code, exactly once, in
    ``run_pipeline``; and the old key is checked against code only.
    """
    rel = "scripts/gamslib/run_full_test.py"
    resolve_unique(
        rel,
        "run_pipeline",
        'model["mcp_solve"]["mcp_file_generated"] = _repo_relative_path(',
    )
    source = (PROJECT_ROOT / rel).read_text(encoding="utf-8")
    assert _code_only(source).count('model["mcp_solve"]["mcp_file_used"] =') == 0, (
        "the old key must not still be written — two names for one field is how "
        "a migrated DB silently re-acquires the pre-migration shape"
    )

"""Sprint 27 #1400: the pipeline must record `mcp_file_used` as a repo-relative
path so `gamslib_status.json` is machine-portable (no absolute PROJECT_ROOT
prefix leaking the runner's home directory, which would break byte-identical
comparison across machines).
"""

from __future__ import annotations

import pytest

from scripts.gamslib.run_full_test import PROJECT_ROOT, _repo_relative_path


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

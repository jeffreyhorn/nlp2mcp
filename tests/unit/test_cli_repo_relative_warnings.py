"""Unit guard for #1400: the CLI installs a repo-relative ``warnings.formatwarning``
so captured stderr (into the gamslib DB ``message`` field) doesn't leak the
runner's absolute home path.
"""

from __future__ import annotations

import os
import warnings

from src.cli import _PROJECT_ROOT, _install_repo_relative_formatwarning


def test_formatwarning_relativizes_in_repo_path() -> None:
    saved = warnings.formatwarning
    try:
        _install_repo_relative_formatwarning()
        abs_file = os.path.join(str(_PROJECT_ROOT), "src", "ad", "index_mapping.py")
        out = warnings.formatwarning("msg", UserWarning, abs_file, 648)
        assert "src/ad/index_mapping.py:648" in out.replace(os.sep, "/")
        assert str(_PROJECT_ROOT) not in out  # no absolute home-dir prefix
    finally:
        warnings.formatwarning = saved


def test_formatwarning_leaves_out_of_repo_paths_absolute() -> None:
    saved = warnings.formatwarning
    try:
        _install_repo_relative_formatwarning()
        out = warnings.formatwarning("msg", UserWarning, "/usr/lib/python/site.py", 10)
        assert "/usr/lib/python/site.py:10" in out  # external path untouched
    finally:
        warnings.formatwarning = saved


def test_install_is_idempotent() -> None:
    saved = warnings.formatwarning
    try:
        _install_repo_relative_formatwarning()
        first = warnings.formatwarning
        _install_repo_relative_formatwarning()
        assert warnings.formatwarning is first  # not double-wrapped
    finally:
        warnings.formatwarning = saved

"""Sprint 40 P10a: the shared anchor resolver (`tests/helpers/anchor_resolver.py`).

An anchor pins a source site by OWNING FUNCTION plus a snippet that must occur
EXACTLY ONCE in that function's live code. Anything else -- absent, twice, or
present only in a comment -- pins nothing and must be refused, not passed.
"""

from __future__ import annotations

import pytest

from tests.helpers.anchor_resolver import AnchorError, resolve_unique

pytestmark = pytest.mark.unit

_MODULE = '''\
def writer(row):
    """Docstring mentioning row["mcp_file"] = path, which is prose."""
    row["mcp_file"] = "out.gms"
    return row


def twice(row):
    row["k"] = 1
    row["k"] = 1
    return row


def commented(row):
    # row["gone"] = 1  (was: the old key)
    return row
'''


@pytest.fixture
def module(tmp_path):
    path = tmp_path / "fixture_module.py"
    path.write_text(_MODULE, encoding="utf-8")
    return str(path)


def test_a_UNIQUE_anchor_resolves_to_its_line(module):
    # Line 3: the docstring's copy of the text is blanked, so only the live
    # assignment counts.
    assert resolve_unique(module, "writer", 'row["mcp_file"] = "out.gms"') == 3


def test_an_anchor_appearing_TWICE_in_one_function_is_refused(module):
    with pytest.raises(AnchorError, match="occurs 2x"):
        resolve_unique(module, "twice", 'row["k"] = 1')


def test_an_anchor_present_only_in_a_COMMENT_is_refused(module):
    with pytest.raises(AnchorError, match="occurs 0x"):
        resolve_unique(module, "commented", 'row["gone"] = 1')


def test_a_missing_FUNCTION_is_refused(module):
    with pytest.raises(AnchorError, match="function gone"):
        resolve_unique(module, "no_such_function", "anything")

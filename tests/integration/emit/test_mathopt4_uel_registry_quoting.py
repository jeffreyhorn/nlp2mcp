"""Sprint 25 / #1280: mathopt4 corpus regression for `nlp2mcp_uel_registry`
quoting of attribute-access labels.

When the UEL registry includes attribute-access labels like `x1.l` /
`x2.l` (produced by zero-filtered parameter lookups in `mathopt4`),
GAMS must see them as **single-quoted literals**:

```gams
Set nlp2mcp_uel_registry / 'x1.l', 'x2.l' /;
```

The unquoted form `x1.l, x2.l` is interpreted by GAMS as a 2-tuple
notation (`x1.l` = element `x1` paired with element `l`), which:
- on newer GAMS versions, raises `$161 Conflicting dimensions in
  element` because the set is declared 1-D, OR
- on older versions, silently truncates the UEL to the first
  component, producing wrong downstream attribute lookups.

`_sanitize_uel_element` (in `src/emit/original_symbols.py`) handles
the quoting; this test verifies that the emitter actually CALLS it
end-to-end on `mathopt4`'s registry.
"""

from __future__ import annotations

import os
import re
import sys

import pytest


@pytest.fixture(autouse=True)
def _high_recursion_limit():
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        yield
    finally:
        sys.setrecursionlimit(old)


def _emit_mcp_for(gms_path: str) -> str:
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_file
    from src.kkt.assemble import assemble_kkt_system

    model = parse_model_file(gms_path)
    normalize_model(model)
    j_eq, j_ineq = compute_constraint_jacobian(model)
    grad = compute_objective_gradient(model)
    kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
    return emit_gams_mcp(kkt)


@pytest.mark.integration
def test_mathopt4_uel_registry_quotes_dotted_labels():
    """`mathopt4`'s `nlp2mcp_uel_registry` must single-quote attribute
    labels (`x1.l`, `x2.l`). Unquoted, GAMS rejects with `$161
    Conflicting dimensions` (newer versions) or silently truncates
    (older versions).
    """
    src = "data/gamslib/raw/mathopt4.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/mathopt4.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    # Find the UEL registry declaration line.
    registry_match = re.search(r"Set\s+nlp2mcp_uel_registry\s*/(.*?)/;", output, re.DOTALL)
    assert (
        registry_match is not None
    ), "Expected `Set nlp2mcp_uel_registry / ... /;` declaration in MCP."
    registry_body = registry_match.group(1)

    # `x1.l` and `x2.l` MUST appear as `'x1.l'` and `'x2.l'`.
    assert (
        "'x1.l'" in registry_body
    ), f"Expected `'x1.l'` (quoted) in UEL registry. Body:\n{registry_body}"
    assert (
        "'x2.l'" in registry_body
    ), f"Expected `'x2.l'` (quoted) in UEL registry. Body:\n{registry_body}"

    # Unquoted forms must NOT appear.
    assert not re.search(
        r"(?<!')x1\.l(?!')", registry_body
    ), f"UEL registry must not contain unquoted `x1.l`. Body:\n{registry_body}"
    assert not re.search(
        r"(?<!')x2\.l(?!')", registry_body
    ), f"UEL registry must not contain unquoted `x2.l`. Body:\n{registry_body}"


@pytest.mark.integration
def test_mathopt4_uel_registry_does_not_double_quote_plain_labels():
    """Plain labels (no dots) like `x1_0` should be quoted by the
    sanitizer (consistent quoting style) but should NOT be
    double-quoted (e.g., `''x1_0''`).
    """
    src = "data/gamslib/raw/mathopt4.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/mathopt4.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)
    registry_match = re.search(r"Set\s+nlp2mcp_uel_registry\s*/(.*?)/;", output, re.DOTALL)
    assert registry_match is not None
    registry_body = registry_match.group(1)

    # `x1_0` should appear as `'x1_0'`, NOT as `''x1_0''`.
    assert "'x1_0'" in registry_body
    assert "''x1_0''" not in registry_body

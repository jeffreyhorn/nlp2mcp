"""Regression guard for the Sprint-33 P6 fix: a variable's expression ``.l`` init
must NOT be emitted when it references a variable pruned from the MCP.

sample.gms declares two models — ``sample`` (original formulation, uses ``n``) and
``sampler`` (reciprocal formulation, uses ``nr``) — and translates the LAST solve
(``sampler``), so ``n`` (used only by the non-translated ``cbal``/``vbal``) is
pruned from the MCP. The source calibration init ``c.l = sum(h, data(h,"cost") *
n.l(h))`` (``c``'s ``l_expr``) has ``c`` in the MCP but references the dropped
``n`` — emitting it produced ``$140 Unknown symbol`` at GAMS compile
(``path_syntax_error``).

The fix (``src/emit/emit_gams.py`` variable-init pass) skips an expression ``.l``
init whose ``.l``-variable references are not a subset of the declared MCP
variables (``kkt.stationarity``). This guard asserts the emitted MCP no longer
references ``n`` and compiles clean. Skips when the (gitignored) raw model is
absent.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SAMPLE = PROJECT_ROOT / "data" / "gamslib" / "raw" / "sample.gms"


@pytest.mark.skipif(not SAMPLE.exists(), reason="raw sample.gms not present (gitignored corpus)")
def test_sample_no_pruned_var_l_init(tmp_path: Path) -> None:
    out = tmp_path / "sample_mcp.gms"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            str(SAMPLE),
            "-o",
            str(out),
            "--quiet",
            "--skip-convexity-check",
        ],
        cwd=str(PROJECT_ROOT),
        check=True,
        capture_output=True,
        text=True,
    )
    text = out.read_text(encoding="utf-8")

    # The pruned original-formulation variable `n` (translated model is `sampler`,
    # which uses `nr`) must not be referenced anywhere in the emitted MCP — in
    # particular the `c.l = sum(h, data(h,"cost")*n.l(h))` init must be skipped.
    assert not re.search(
        r"\bn\.l\b", text
    ), "emitted MCP references the pruned variable `n.l` (the P6 path_syntax_error bug)"

    # The translated model is the reciprocal formulation `sampler` (vbalr/cbalr,
    # using `nr`), so `nr` gets a stationarity equation — a sanity check that the
    # fix drops only the pruned-var init, not the correct emit.
    assert "stat_nr" in text, "expected stat_nr (the reciprocal primal) in the emitted MCP"

"""Regression test for Sprint 25 Day 10 / #1278: KKT stationarity must
preserve the alias-position distinction in `ord(...)` arguments when an
equation has multiple positions over the same root set via aliases.

The twocge model contains (paraphrased):

    Set i / BRD, MLK /; Set r / JPN, USA /;
    Alias (r, rr);
    Variable e(i, r), m(i, r);
    Equation eqw(i, r, rr);
    eqw(i, r, rr).. (e(i, r) - m(i, rr))$(ord(r) <> ord(rr)) =e= 0;

The Jacobian transpose contribution to `stat_e(i, r)` from `eqw` is

    sum(rr$(ord(r) <> ord(rr)), nu_eqw(i, r, rr))

Pre-fix, the emitter produced `sum(rr, 1$(ord(r) <> ord(r)) * ...)` —
an always-false tautology that suppresses every contribution. Two
defects combined to produce this:

1. The constraint-position override (`_build_constraint_element_mapping`)
   maps each concrete element at eq position `p` to `mult_domain[p]`.
   When the representative row has duplicate eq indices (e.g.,
   `eqw('BRD', 'JPN', 'JPN')`), `JPN→r` at position 1 is overwritten to
   `JPN→rr` at position 2 (last write wins). Both `ord(JPN)` lifts
   then become `ord(rr)`.
2. Even with a row whose eq indices are distinct (e.g.,
   `eqw('BRD', 'JPN', 'USA')`), the `Call("ord", ...)` handler in
   `_replace_indices_in_expr` resolves the override result `'rr'` to
   its alias target `'r'` because `'r'` is in `equation_domain`,
   collapsing both positions onto `'r'`.

Day 10 fix:

- Representative picker (`stationarity.py` indexed-Jacobian loop) now
  prefers entries with distinct equation indices to avoid the override
  collision.
- `Call("ord", ...)` lift in `_replace_indices_in_expr` keeps the
  override-chosen alias when the alias's target is in `equation_domain`
  (and the alias itself is not). The alias becomes a controlled sum
  index after Sum-wrapping.
"""

from __future__ import annotations

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


def _emit_mcp(gms_text: str, tmp_path) -> str:
    """Translate inline GAMS source through the full pipeline."""
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_file
    from src.kkt.assemble import assemble_kkt_system

    src = tmp_path / "model.gms"
    src.write_text(gms_text)
    model = parse_model_file(str(src))
    normalize_model(model)
    j_eq, j_ineq = compute_constraint_jacobian(model)
    grad = compute_objective_gradient(model)
    kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
    return emit_gams_mcp(kkt)


@pytest.mark.unit
def test_alias_position_ord_condition_preserves_distinction(tmp_path):
    """A constraint indexed (i, r, rr) with rr aliasing r and a
    `$(ord(r) <> ord(rr))` body condition must NOT collapse to
    `$(ord(r) <> ord(r))` when lifted into the stationarity equations.
    """
    gams = """\
Set i / g1, g2 /;
Set r / R1, R2 /;
Alias (r, rr);

Variable e(i, r), m(i, r), z;

Equation eqw(i, r, rr), zdef;

eqw(i, r, rr).. (e(i, r) - m(i, rr))$(ord(r) <> ord(rr)) =e= 0;
zdef..          z =e= sum((i, r), e(i, r) + m(i, r));

Model M / eqw, zdef /;
solve M using nlp minimizing z;
"""
    output = _emit_mcp(gams, tmp_path)

    import re

    self_tautologies = [
        m.group(0)
        for line in output.splitlines()
        for m in re.finditer(r"ord\((\w+)\)\s*<>\s*ord\(\1\)", line)
    ]
    assert not self_tautologies, (
        "Pre-#1278 emission collapsed `ord(r) <> ord(rr)` to a "
        f"self-tautology: {self_tautologies}\nFull output:\n{output}"
    )

    # Cross-check: the alias-distinguishing condition must appear at least
    # once. Without it, the eqw multiplier term is unconditionally summed
    # (also wrong, just in a different way).
    assert re.search(r"ord\(r\)\s*<>\s*ord\(rr\)", output) or re.search(
        r"ord\(rr\)\s*<>\s*ord\(r\)", output
    ), (
        "Expected at least one `ord(r) <> ord(rr)` (or symmetric) condition "
        f"to survive the lift. Output:\n{output}"
    )


@pytest.mark.unit
def test_alias_position_ord_appears_in_stat_e_and_stat_m(tmp_path):
    """Both the stat_e and stat_m stationarity equations should carry the
    `ord(r) <> ord(rr)` condition on their `nu_eqw` contribution. This is
    a sharper localization than the corpus-wide tautology check.
    """
    gams = """\
Set i / g1, g2 /;
Set r / R1, R2 /;
Alias (r, rr);

Variable e(i, r), m(i, r), z;

Equation eqw(i, r, rr), zdef;

eqw(i, r, rr).. (e(i, r) - m(i, rr))$(ord(r) <> ord(rr)) =e= 0;
zdef..          z =e= sum((i, r), e(i, r) + m(i, r));

Model M / eqw, zdef /;
solve M using nlp minimizing z;
"""
    output = _emit_mcp(gams, tmp_path)
    lines = output.splitlines()

    def _equation_text(prefix: str) -> str:
        # Equations may span multiple lines if the long-line wrap fires;
        # join until we hit the terminating ';'.
        for i, line in enumerate(lines):
            if line.startswith(prefix):
                chunk = [line]
                j = i + 1
                while j < len(lines) and ";" not in chunk[-1]:
                    chunk.append(lines[j])
                    j += 1
                return "\n".join(chunk)
        return ""

    stat_e = _equation_text("stat_e")
    stat_m = _equation_text("stat_m")

    assert stat_e, "Expected a `stat_e` equation in the emission."
    assert stat_m, "Expected a `stat_m` equation in the emission."

    import re

    eqw_cond_pattern = re.compile(r"ord\(r\)\s*<>\s*ord\(rr\)")
    assert eqw_cond_pattern.search(stat_e), (
        f"stat_e missing `ord(r) <> ord(rr)` on its eqw contribution:\n{stat_e}"
    )
    assert eqw_cond_pattern.search(stat_m), (
        f"stat_m missing `ord(r) <> ord(rr)` on its eqw contribution:\n{stat_m}"
    )


@pytest.mark.integration
def test_twocge_no_ord_self_tautology():
    """Corpus-level regression for the original twocge bug. Pre-fix the
    emission contained six `ord(r) <> ord(r)` tautologies (3 in stat_e,
    3 in stat_m for the eqw and eqpw contributions).
    """
    import os

    src = "data/gamslib/raw/twocge.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/twocge.gms is gitignored on this runner.")

    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_file
    from src.kkt.assemble import assemble_kkt_system

    model = parse_model_file(src)
    normalize_model(model)
    j_eq, j_ineq = compute_constraint_jacobian(model)
    grad = compute_objective_gradient(model)
    kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
    output = emit_gams_mcp(kkt)

    import re

    self_tautologies = [
        m.group(0)
        for line in output.splitlines()
        for m in re.finditer(r"ord\((\w+)\)\s*<>\s*ord\(\1\)", line)
    ]
    assert not self_tautologies, (
        f"twocge emission contains ord-self tautologies (the #1278 regression): {self_tautologies}"
    )

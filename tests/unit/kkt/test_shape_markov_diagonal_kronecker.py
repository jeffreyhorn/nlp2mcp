"""Shape fixture for the markov σ=sp diagonal-Kronecker split (Issue #1110 Part 2).

Guards the Sprint-37 Day-2 landing: when a constraint references a variable both
directly and inside a sum, and the off-diagonal coefficient is a parameter
coupling the constraint index to the variable's own independent index, the
emitter used to fuse the Kronecker ``1`` into the off-diagonal coefficient and
sum the whole product over indices it does not depend on (one spurious offset
group per set element — 45 on the real markov model).

**Corpus-free by design.** The obvious spelling of this fixture would parse
``data/gamslib/raw/markov.gms`` and ``pytest.skip`` when it is absent — but
``ci.yml`` provisions only the five ``--fast`` fixtures (chenery, abel,
partssupply, ps2_f, himmel11), so a skip-guarded fixture would skip on *every*
CI run and guard nothing.  See ``SPRINT_37/P7_INFRA_CATALOG.md`` §1.1.  These
tests build an inline synthetic instead and run unconditionally in ~0.6 s.

The synthetic is a scaled-down markov: ``|s|``=3 instead of 8, which changes the
number of spurious groups (15 vs 45) but not the structure.  The assertions are
therefore **structural** — where ``nu_constr(s,i)`` sits — and deliberately do
NOT assert a group count.
"""

from __future__ import annotations

import re

import pytest

from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.gradient import compute_objective_gradient
from src.config import Config
from src.emit.expr_to_gams import expr_to_gams
from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_text
from src.kkt.assemble import assemble_kkt_system
from src.kkt.stationarity import build_stationarity_equations

pytestmark = pytest.mark.unit


def _stat_z(source: str) -> str:
    """Run source through parse → normalize → AD → KKT and return stat_z as GAMS."""
    model = parse_model_text(source)
    normalized_eqs, _ = normalize_model(model)
    config = Config()
    gradient = compute_objective_gradient(model, config)
    j_eq, j_ineq = compute_constraint_jacobian(model, normalized_eqs, config)
    kkt = assemble_kkt_system(model, gradient, j_eq, j_ineq, config)
    stationarity = build_stationarity_equations(kkt, config)
    return expr_to_gams(stationarity["stat_z"].lhs_rhs[0])


# markov's shape: z(s,i,sp) referenced both directly (`z(sp,j,spp)`) and inside a
# sum, with pi assigned only on the σ=sp slice (`pi(s,i,sp,j,sp) = pr(i,j)`), so
# the coupling parameter carries the equation index and the variable's own third
# index at two distinct positions of its tuple.
_MARKOV_SHAPE = """
Set s / a, b, c /
    i / normal, disrupted /;
Alias (s,sp,spp), (i,j);
Scalar b_ / 0.95 /, beta / 0.0625 /;
Table pr(i,j)
              normal  disrupted
   normal        .8       .2
   disrupted     .5       .5;
Parameter pi(s,i,sp,j,spp);
pi(s,i,sp,j,sp) = pr(i,j);
Variable z(s,i,sp), pvcost;
Positive Variable z;
Equation constr(s,i), cost;
constr(sp,j).. sum(spp, z(sp,j,spp)) - b_*sum((s,i,spp), {coupling}*z(s,i,spp)) =e= beta;
cost.. pvcost =e= sum((s,i,spp), z(s,i,spp));
Model mm / all /; solve mm using {solver} minimizing pvcost;
"""


def test_kronecker_diagonal_is_a_bare_additive_term():
    """The diagonal multiplier must not be trapped inside the off-diagonal sum.

    Fail-before (the pre-#1110-Part-2 emit, measured): the diagonal multiplier is
    emitted as ``sum((s__kktN,j), (1 - b*pi(...)) * nu_constr(s,i))`` — indexed by
    the stationarity equation's own head indices yet summed over alias indices it
    does not depend on, which multiplies it by card(s)*card(j).

    Pass-after: ``nu_constr(s,i)`` appears as a bare additive term.
    """
    text = _stat_z(_MARKOV_SHAPE.format(coupling="pi(s,i,sp,j,spp)", solver="lp"))

    assert re.search(r"\+ nu_constr\(s,i\)(?!\))", text), (
        "the Kronecker diagonal nu_constr(s,i) is not emitted as a bare additive "
        f"term; got: {text}"
    )
    # ... and it must NOT be inside a sum over indices it does not depend on.
    assert not re.search(r"sum\(\([^)]*\),[^;]*?nu_constr\(s,i\)", text), (
        "nu_constr(s,i) is still trapped inside a sum — the Kronecker delta is "
        f"being multiplied by the alias cardinality; got: {text}"
    )


def test_off_diagonal_is_a_single_sum_without_the_kronecker_one():
    """The σ=sp off-diagonal collapses to one sum, with no fused ``1 -``.

    Deliberately does not assert the number of spurious ``s__kktN`` groups: that
    figure is scale-dependent (15 here at |s|=3, 45 on the real model at |s|=8).
    """
    text = _stat_z(_MARKOV_SHAPE.format(coupling="pi(s,i,sp,j,spp)", solver="lp"))

    assert re.search(
        r"sum\(j,[^;]*pi\(s,i,sp,j,sp\)[^;]*nu_constr\(sp,j\)", text
    ), f"the σ=sp off-diagonal sum is missing or mis-indexed; got: {text}"
    assert "1 - b_ *" not in text, (
        "the Kronecker `1` is still fused into the off-diagonal coefficient; " f"got: {text}"
    )


def test_call_nodes_survive_symbolization():
    """Regression: ``Call`` nodes must be rebuilt with ``func``, not ``name``.

    ``_try_build_sigma_sp_crossterm`` re-symbolises the representative derivative
    (concrete set elements → domain symbols).  Its ``Call`` branch originally
    reconstructed nodes as ``Call(e.name, ...)``, but ``Call`` stores the function
    name in ``func`` (``src/ir/ast.py``), so any derivative containing ``exp``,
    ``ord``, ``power``… raised ``AttributeError`` and crashed translation.

    No GAMSLib model exercises this: markov is the only model the conjoined gate
    fires on, and its derivative is ``Unary(-, Binary(*, ParamRef, ParamRef))``
    with no ``Call``.  The bug was found in review and is unreachable from the
    corpus — hence this synthetic, which both fires the gate and puts a ``Call``
    in the derivative.
    """
    text = _stat_z(_MARKOV_SHAPE.format(coupling="exp(pi(s,i,sp,j,spp))", solver="nlp"))

    # The gate still fires (bare diagonal present) ...
    assert re.search(
        r"\+ nu_constr\(s,i\)(?!\))", text
    ), f"the discriminator did not fire on the Call-bearing variant; got: {text}"
    # ... and the Call was rebuilt with its indices symbolised, not left as
    # concrete elements and not crashing.
    assert re.search(r"exp\(pi\(s,i,sp,j,sp\)\)", text), (
        "the Call node was not correctly re-symbolised inside the off-diagonal "
        f"coefficient; got: {text}"
    )

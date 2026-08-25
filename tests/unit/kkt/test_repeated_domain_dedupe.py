"""Unit tests for #1062's repeated-variable-domain de-duplication.

`tricp` declares `slp(n,n)` — in GAMS that is the full `n x n` product, so
`card(n)**2` columns exist.  But a *definition* head written from that declared
domain, `stat_slp(n,n)..`, has a repeated controlling index, which GAMS binds to
the SAME element; the block then generates only the diagonal, and every
off-diagonal column is left unmatched in the MCP.

`dedupe_repeated_variable_domains` rewrites the second and later occurrences to
fresh aliases before differentiation, so the head spans the product.  It must be
an exact no-op for every variable whose domain has no repeat.
"""

from __future__ import annotations

from src.ir.model_ir import ModelIR
from src.ir.symbols import AliasDef, SetDef, VariableDef
from src.kkt.repeated_domain import dedupe_repeated_variable_domains


def _model(*vars_: VariableDef, sets: tuple[str, ...] = ("n", "c", "i")) -> ModelIR:
    m = ModelIR()
    for s in sets:
        m.add_set(SetDef(name=s, members=[]))
    for v in vars_:
        m.add_var(v)
    return m


def test_no_repeat_is_an_exact_noop():
    m = _model(
        VariableDef(name="x", domain=("n", "c")),
        VariableDef(name="y", domain=("n",)),
        VariableDef(name="z", domain=()),
    )
    aliases_before = dict(m.aliases)

    assert dedupe_repeated_variable_domains(m) == {}

    assert m.variables["x"].domain == ("n", "c")
    assert m.variables["y"].domain == ("n",)
    assert m.variables["z"].domain == ()
    assert dict(m.aliases) == aliases_before


def test_repeated_symbol_gets_a_fresh_alias():
    """tricp's shape: slp(n,n) -> slp(n,n__), with Alias(n, n__) registered."""
    m = _model(VariableDef(name="slp", domain=("n", "n")))

    rewritten = dedupe_repeated_variable_domains(m)

    assert rewritten == {"slp": ("n", "n")}
    assert m.variables["slp"].domain == ("n", "n__")
    assert m.aliases["n__"].target == "n"


def test_repeat_in_a_later_position():
    """ferts' shape: xi(c,i,i) -> xi(c,i,i__); position 0 is untouched."""
    m = _model(VariableDef(name="xi", domain=("c", "i", "i")))

    dedupe_repeated_variable_domains(m)

    assert m.variables["xi"].domain == ("c", "i", "i__")
    assert m.aliases["i__"].target == "i"


def test_alias_is_shared_across_variables_over_the_same_set():
    """Two variables repeating `n` must not mint two aliases of `n`."""
    m = _model(
        VariableDef(name="slp", domain=("n", "n")),
        VariableDef(name="sln", domain=("n", "n")),
    )

    dedupe_repeated_variable_domains(m)

    assert m.variables["slp"].domain == ("n", "n__")
    assert m.variables["sln"].domain == ("n", "n__")
    assert [a for a in m.aliases if a.lower().startswith("n_")] == ["n__"]


def test_triple_repeat_mints_distinct_aliases():
    m = _model(VariableDef(name="t", domain=("n", "n", "n")))

    dedupe_repeated_variable_domains(m)

    assert m.variables["t"].domain == ("n", "n__", "n___")
    assert m.aliases["n__"].target == "n"
    assert m.aliases["n___"].target == "n"


def test_minted_name_avoids_an_existing_symbol():
    """`n__` already taken (here by an alias) -> mint `n___` instead."""
    m = _model(VariableDef(name="slp", domain=("n", "n")))
    m.add_alias(AliasDef(name="n__", target="n"))

    dedupe_repeated_variable_domains(m)

    assert m.variables["slp"].domain == ("n", "n___")
    assert m.aliases["n___"].target == "n"


def test_minted_name_avoids_a_variable_of_the_same_name():
    """GAMS has ONE symbol namespace: a variable named `n__` blocks the alias."""
    m = _model(
        VariableDef(name="slp", domain=("n", "n")),
        VariableDef(name="n__", domain=()),
    )

    dedupe_repeated_variable_domains(m)

    assert m.variables["slp"].domain == ("n", "n___")


def test_repeat_detection_is_case_insensitive():
    """GAMS labels and symbols are case-insensitive; the IR is not."""
    m = _model(VariableDef(name="slp", domain=("n", "N")))

    rewritten = dedupe_repeated_variable_domains(m)

    assert rewritten == {"slp": ("n", "N")}
    assert m.variables["slp"].domain[0] == "n"
    assert m.variables["slp"].domain[1].lower() == "n__"

"""De-duplicate repeated set symbols in variable declaration domains (Issue #1062).

GAMS declares a variable such as ``slp(n,n)`` over the *full* ``n x n`` product,
so every one of ``card(n)**2`` columns exists.  But in a GAMS **equation
definition** (and in an assignment) a controlling index name that is repeated
binds to the *same* element, so a head written from that declared domain --
``stat_slp(n,n)..`` -- generates only the ``card(n)`` diagonal rows.  In an MCP
that leaves every off-diagonal column with no row to pair against::

    ---- stat_slp  =E=
                    NONE
    **** Unmatched variable not free or fixed
         slp(n0,n1)

The KKT builders take their equation-head domains (and, positionally, the index
symbols used to build the bodies) straight from ``VariableDef.domain``.  This
pass runs *before* differentiation and rewrites the second and later occurrences
of a repeated symbol to a freshly minted alias of the same set, registering the
alias so the emitter declares it::

    Alias(n, n__);
    stat_slp(n,n__)..  ( ... )$(e(n,n__)) =E= 0;

The rewrite is an identity for any variable whose declared domain has no
repeated symbol, so models without the pattern are untouched.
"""

from __future__ import annotations

import logging

from src.ir.model_ir import ModelIR
from src.ir.symbols import AliasDef

logger = logging.getLogger(__name__)


def _mint_alias_name(base: str, taken: set[str]) -> str:
    """Return a fresh ``base__``-style symbol not colliding with ``taken``.

    ``taken`` holds lowercase names; the returned name is lowercase-unique.
    Matches the ``__`` suffix convention the AD layer already uses for sum
    indices, so the emitter's existing Alias machinery reads naturally.
    """
    candidate = f"{base}__"
    while candidate.lower() in taken:
        candidate += "_"
    return candidate


def dedupe_repeated_variable_domains(model_ir: ModelIR) -> dict[str, tuple[str, ...]]:
    """Rewrite repeated symbols in variable domains to fresh aliases.

    Args:
        model_ir: Model IR, mutated in place.  Variable domains gain alias
            symbols and ``model_ir.aliases`` gains the corresponding entries.

    Returns:
        Mapping of variable name -> original declared domain, for every variable
        that was rewritten.  Empty when the model has no repeated-symbol domain.
    """
    rewritten: dict[str, tuple[str, ...]] = {}

    # Every name that could collide with a minted alias.  Sets and aliases are
    # the semantic collisions; params/vars/equations are included because GAMS
    # has a single symbol namespace.
    taken: set[str] = set()
    for bucket in (
        model_ir.sets,
        model_ir.aliases,
        model_ir.params,
        model_ir.variables,
        model_ir.equations,
    ):
        taken.update(name.lower() for name in bucket)

    # Aliases minted per base set are reused across variables so two variables
    # repeating the same set share one Alias declaration.
    minted: dict[str, list[str]] = {}

    for var_name in list(model_ir.variables):
        var_def = model_ir.variables[var_name]
        domain = var_def.domain
        if not domain or len(domain) == len({d.lower() for d in domain}):
            continue

        seen: dict[str, int] = {}
        new_domain: list[str] = []
        for sym in domain:
            key = sym.lower()
            occurrence = seen.get(key, 0)
            seen[key] = occurrence + 1
            if occurrence == 0:
                new_domain.append(sym)
                continue
            # Second or later occurrence: take the n-th minted alias of `sym`,
            # minting it if this is the deepest repeat seen so far.
            pool = minted.setdefault(key, [])
            while len(pool) < occurrence:
                alias_name = _mint_alias_name(sym, taken)
                taken.add(alias_name.lower())
                pool.append(alias_name)
                model_ir.add_alias(AliasDef(name=alias_name, target=sym))
            new_domain.append(pool[occurrence - 1])

        rewritten[var_name] = domain
        var_def.domain = tuple(new_domain)
        logger.info(
            "Issue #1062: de-duplicated repeated domain for variable "
            f"{var_name}: {domain} -> {var_def.domain}"
        )

    return rewritten

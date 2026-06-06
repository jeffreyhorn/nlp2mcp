"""Tests for _objective_varref_positional_rename() — #1381 follow-up.

The objective-gradient of an aliased multi-D variable collapses when the
objective references the variable through SUBSET indices that share a common
parent set.  cesam2's ``sum((ii,jj,jwt3)$nonzero(ii,jj), W3(ii,jj,jwt3)*…)``
with ``ii(i)`` and ``jj`` (alias of ``ii``) — both dynamic subsets of root
``i`` — makes the downstream superset-wrap bind BOTH ``ii`` and ``jj`` to the
first domain superset ``i``, collapsing the guard ``nonzero(ii,jj)`` to
``nonzero(i,i)`` (diagonal) and dropping the gradient on off-diagonal cells.

The fix is COLLISION-driven: an objective index is renamed to its positional
domain coordinate ONLY when another index shares the same root set but maps to
a DIFFERENT domain coordinate.  A LONE subset index (harker's ``d(l)`` with
``l ⊂ n``) is left untouched so its load-bearing ``sum(l__$sameas(l__,n), …)``
self-sum survives (renaming ``l→n`` would yield a GAMS $171 domain violation on
the subset-domain parameter ``coefs(l,*)``).
"""

from __future__ import annotations

import pytest

from src.ir.ast import VarRef
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import AliasDef, ObjSense, SetDef
from src.kkt.stationarity import _objective_varref_positional_rename

pytestmark = pytest.mark.unit


def _cesam2_like() -> ModelIR:
    """Root set ``i`` with dynamic subset ``ii(i)``; aliases ``j→i``, ``jj→ii``;
    support set ``jwt`` with strict subset ``jwt3(jwt)``.  Mirrors cesam2."""
    m = ModelIR()
    m.add_set(SetDef(name="i", members=["ACT", "COM", "FAC", "ENT"]))
    m.add_set(SetDef(name="ii", members=[], domain=("i",)))
    m.add_set(SetDef(name="jwt", members=["1", "2", "3", "4", "5", "6", "7"]))
    m.add_set(SetDef(name="jwt3", members=["1", "2", "3"], domain=("jwt",)))
    m.add_alias(AliasDef(name="j", target="i"))
    m.add_alias(AliasDef(name="jj", target="ii"))
    return m


class TestCollisionRename:
    def test_cesam2_two_same_root_subsets_rename_positionally(self):
        """ii,jj both root ``i`` but map to distinct coords i,j → rename both;
        jwt3 (lone, root jwt) is left alone."""
        m = _cesam2_like()
        m.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="DENTROPY")
        m.objective.expr = VarRef("W3", ("ii", "jj", "jwt3"))
        rename = _objective_varref_positional_rename(m, "W3", ("i", "j", "jwt"))
        assert rename == {"ii": "i", "jj": "j"}

    def test_lone_subset_index_not_renamed(self):
        """harker: d(l) with l ⊂ n, single index → no collision → no rename
        (preserves the load-bearing self-sum that keeps coefs(l,*) domain-valid)."""
        m = ModelIR()
        m.add_set(SetDef(name="n", members=["a", "b", "c"]))
        m.add_set(SetDef(name="l", members=[], domain=("n",)))
        m.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        m.objective.expr = VarRef("d", ("l",))
        rename = _objective_varref_positional_rename(m, "d", ("n",))
        assert rename == {}

    def test_indices_equal_domain_no_rename(self):
        """Objective references the variable with its own domain symbols → {}."""
        m = _cesam2_like()
        m.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="z")
        m.objective.expr = VarRef("W3", ("i", "j", "jwt"))
        rename = _objective_varref_positional_rename(m, "W3", ("i", "j", "jwt"))
        assert rename == {}

    def test_two_subsets_same_target_coord_not_renamed(self):
        """Two same-root indices mapping to the SAME domain coord do not collide
        (no collapse to break) → no rename."""
        m = _cesam2_like()
        m.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="z")
        # both positions map to domain coord ``i`` (same coord) — no collision
        m.objective.expr = VarRef("W2", ("ii", "jj"))
        rename = _objective_varref_positional_rename(m, "W2", ("i", "i"))
        assert rename == {}

    def test_no_objective_returns_empty(self):
        m = _cesam2_like()
        rename = _objective_varref_positional_rename(m, "W3", ("i", "j", "jwt"))
        assert rename == {}

    def test_var_not_in_objective_returns_empty(self):
        m = _cesam2_like()
        m.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="z")
        m.objective.expr = VarRef("OTHER", ("ii", "jj", "jwt3"))
        rename = _objective_varref_positional_rename(m, "W3", ("i", "j", "jwt"))
        assert rename == {}

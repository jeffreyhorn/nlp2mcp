"""Tests for emission ordering of computed parameters around set assignments.

Sprint 21 Day 8: Verifies that compute_set_assignment_param_deps() correctly
excludes parameters whose expression keys reference dynamic set names, so they
are emitted AFTER set assignments rather than before.
"""

from src.emit.original_symbols import compute_set_assignment_param_deps
from src.ir.ast import Const, ParamRef, SymbolRef
from src.ir.model_ir import ModelIR
from src.ir.symbols import ParameterDef, SetAssignment, SetDef


class TestComputeSetAssignmentParamDeps:
    """Test compute_set_assignment_param_deps() dynamic-set exclusion."""

    def test_dynamic_set_indexed_params_excluded_from_early(self):
        """Params with expression keys referencing dynamic sets are excluded.

        Scenario (qdemo7-like):
          - Set assignment: cn(c) = yes$demdat(c,"ref-p")
          - Param beta(cn) = demdat(cn,...) — uses dynamic set 'cn' as key
          - Param demdat has static data only (no expressions)
          - beta should be EXCLUDED from early params
        """
        model_ir = ModelIR()
        model_ir.sets["c"] = SetDef(name="c", members=["wheat", "rice"])
        model_ir.sets["cn"] = SetDef(name="cn", members=[])

        # demdat: has static values, referenced by set assignment
        demdat = ParameterDef(name="demdat", domain=("c", "*"))
        demdat.values[("wheat", "ref-p")] = 10.0
        demdat.values[("rice", "ref-p")] = 20.0
        model_ir.params["demdat"] = demdat

        # beta: computed param with dynamic set 'cn' as expression key
        beta = ParameterDef(name="beta", domain=("cn",))
        beta.expressions.append(
            (("cn",), ParamRef("demdat", indices=(SymbolRef("cn"), Const("ref-p"))))
        )
        model_ir.params["beta"] = beta

        # Set assignment: cn(c) = yes$demdat(c,"ref-p")
        model_ir.set_assignments.append(
            SetAssignment(
                set_name="cn",
                indices=("c",),
                expr=ParamRef("demdat", indices=(SymbolRef("c"), Const("ref-p"))),
                location=None,
            )
        )

        result = compute_set_assignment_param_deps(model_ir)
        # demdat is a direct dependency and has no dynamic-set-indexed keys
        assert "demdat" in result
        # beta is excluded because its key ('cn',) references dynamic set 'cn'
        assert "beta" not in result

    def test_no_dynamic_sets_all_early_params_kept(self):
        """When no params use dynamic set keys, all early params are kept.

        Scenario:
          - Set assignment: ku(k) = yes$m0(k)
          - Param m0 has expressions with static keys
          - m0 should be in early params
        """
        model_ir = ModelIR()
        model_ir.sets["k"] = SetDef(name="k", members=["k1", "k2"])
        model_ir.sets["ku"] = SetDef(name="ku", members=[])

        # m0: computed param with regular (non-dynamic-set) key
        m0 = ParameterDef(name="m0", domain=("k",))
        m0.expressions.append((("k",), Const(1.0)))
        model_ir.params["m0"] = m0

        # Set assignment: ku(k) = yes$m0(k)
        model_ir.set_assignments.append(
            SetAssignment(
                set_name="ku",
                indices=("k",),
                expr=ParamRef("m0", indices=(SymbolRef("k"),)),
                location=None,
            )
        )

        result = compute_set_assignment_param_deps(model_ir)
        # m0 should be in early params — 'k' is a regular set, not dynamic
        assert "m0" in result

    def test_mixed_keys_param_disqualified(self):
        """Param with some dynamic-set keys and some static keys is excluded.

        Scenario:
          - Set assignment: cn(c) = yes$demdat(c,"ref-p")
          - Param demdat has: expression key ('cn',"dem-a") AND expression key ('c',"price")
          - Even though only one key uses 'cn', the whole param is excluded
        """
        model_ir = ModelIR()
        model_ir.sets["c"] = SetDef(name="c", members=["wheat"])
        model_ir.sets["cn"] = SetDef(name="cn", members=[])

        # demdat: has expressions with both dynamic-set and static keys
        demdat = ParameterDef(name="demdat", domain=("c", "*"))
        demdat.values[("wheat", "ref-p")] = 10.0
        # Expression with dynamic set key 'cn'
        demdat.expressions.append(
            (("cn", '"dem-a"'), ParamRef("alpha", indices=(SymbolRef("cn"),)))
        )
        # Expression with static key 'c'
        demdat.expressions.append((("c", '"price"'), Const(5.0)))
        model_ir.params["demdat"] = demdat

        # alpha: also uses cn key
        alpha = ParameterDef(name="alpha", domain=("cn",))
        alpha.expressions.append(
            (("cn",), ParamRef("demdat", indices=(SymbolRef("cn"), Const("ref-p"))))
        )
        model_ir.params["alpha"] = alpha

        # Set assignment: cn(c) = yes$demdat(c,"ref-p")
        model_ir.set_assignments.append(
            SetAssignment(
                set_name="cn",
                indices=("c",),
                expr=ParamRef("demdat", indices=(SymbolRef("c"), Const("ref-p"))),
                location=None,
            )
        )

        result = compute_set_assignment_param_deps(model_ir)
        # Both demdat and alpha should be excluded — both have cn-keyed expressions
        assert "demdat" not in result
        assert "alpha" not in result

    def test_transitive_dep_with_dynamic_set_key(self):
        """Transitive dependency with dynamic set key is also excluded.

        Scenario:
          - Set assignment: cn(c) = yes$demdat(c,"ref-p")
          - Param beta(cn) depends on demdat
          - Param alpha(cn) depends on beta
          - Both beta and alpha should be excluded
        """
        model_ir = ModelIR()
        model_ir.sets["c"] = SetDef(name="c", members=["wheat"])
        model_ir.sets["cn"] = SetDef(name="cn", members=[])

        # demdat: static data only
        demdat = ParameterDef(name="demdat", domain=("c", "*"))
        demdat.values[("wheat", "ref-p")] = 10.0
        model_ir.params["demdat"] = demdat

        # beta(cn) depends on demdat
        beta = ParameterDef(name="beta", domain=("cn",))
        beta.expressions.append(
            (("cn",), ParamRef("demdat", indices=(SymbolRef("cn"), Const("ref-p"))))
        )
        model_ir.params["beta"] = beta

        # alpha(cn) depends on beta
        alpha = ParameterDef(name="alpha", domain=("cn",))
        alpha.expressions.append((("cn",), ParamRef("beta", indices=(SymbolRef("cn"),))))
        model_ir.params["alpha"] = alpha

        # Set assignment: cn(c) = yes$demdat(c,"ref-p")
        model_ir.set_assignments.append(
            SetAssignment(
                set_name="cn",
                indices=("c",),
                expr=ParamRef("demdat", indices=(SymbolRef("c"), Const("ref-p"))),
                location=None,
            )
        )

        result = compute_set_assignment_param_deps(model_ir)
        # demdat stays early (static data, no cn-keyed expressions)
        assert "demdat" in result
        # beta and alpha both excluded (cn-keyed expressions)
        assert "beta" not in result
        assert "alpha" not in result

    def test_no_set_assignments_returns_empty(self):
        """No set assignments → empty result (pre-existing behavior)."""
        model_ir = ModelIR()
        model_ir.params["x"] = ParameterDef(name="x")
        result = compute_set_assignment_param_deps(model_ir)
        assert result == set()

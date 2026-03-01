"""Tests for emission ordering.

- Sprint 21 Day 8: Verifies that compute_set_assignment_param_deps() correctly
  excludes parameters whose expression keys reference dynamic set names, so they
  are emitted AFTER set assignments rather than before.
- Issue #921: Verifies that .fx/.lo/.up bounds referencing .l values are emitted
  AFTER the Variable Initialization section (deferred bounds).
"""

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.emit.emit_gams import emit_gams_mcp
from src.emit.original_symbols import compute_set_assignment_param_deps
from src.ir.ast import Const, ParamRef, VarRef
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import ObjSense, ParameterDef, SetAssignment, SetDef, VariableDef, VarKind
from src.kkt.kkt_system import KKTSystem


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
        beta.expressions.append((("cn",), ParamRef("demdat", indices=("cn", '"ref-p"'))))
        model_ir.params["beta"] = beta

        # Set assignment: cn(c) = yes$demdat(c,"ref-p")
        model_ir.set_assignments.append(
            SetAssignment(
                set_name="cn",
                indices=("c",),
                expr=ParamRef("demdat", indices=("c", '"ref-p"')),
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
                expr=ParamRef("m0", indices=("k",)),
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
        demdat.expressions.append((("cn", '"dem-a"'), ParamRef("alpha", indices=("cn",))))
        # Expression with static key 'c'
        demdat.expressions.append((("c", '"price"'), Const(5.0)))
        model_ir.params["demdat"] = demdat

        # alpha: also uses cn key
        alpha = ParameterDef(name="alpha", domain=("cn",))
        alpha.expressions.append((("cn",), ParamRef("demdat", indices=("cn", '"ref-p"'))))
        model_ir.params["alpha"] = alpha

        # Set assignment: cn(c) = yes$demdat(c,"ref-p")
        model_ir.set_assignments.append(
            SetAssignment(
                set_name="cn",
                indices=("c",),
                expr=ParamRef("demdat", indices=("c", '"ref-p"')),
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
        beta.expressions.append((("cn",), ParamRef("demdat", indices=("cn", '"ref-p"'))))
        model_ir.params["beta"] = beta

        # alpha(cn) depends on beta
        alpha = ParameterDef(name="alpha", domain=("cn",))
        alpha.expressions.append((("cn",), ParamRef("beta", indices=("cn",))))
        model_ir.params["alpha"] = alpha

        # Set assignment: cn(c) = yes$demdat(c,"ref-p")
        model_ir.set_assignments.append(
            SetAssignment(
                set_name="cn",
                indices=("c",),
                expr=ParamRef("demdat", indices=("c", '"ref-p"')),
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


class TestDeferredBoundEmission:
    """Issue #921: Bounds referencing .l must be emitted after Variable Initialization."""

    def test_fx_referencing_l_emitted_after_init(self, manual_index_mapping):
        """x.fx = x.l must appear after x.l initialization, not before."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)
        # Variable x with .l init and .fx that references .l
        x_var = VariableDef(name="x", domain=(), kind=VarKind.CONTINUOUS)
        x_var.l_expr = Const(5.0)  # x.l = 5
        x_var.fx_expr = VarRef(name="x", attribute="l")  # x.fx = x.l
        model.variables["x"] = x_var

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])
        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)
        result = emit_gams_mcp(kkt)

        # .l init must appear before .fx bound
        l_init_pos = result.index("x.l = 5")
        fx_bound_pos = result.index("x.fx = x.l")
        assert (
            l_init_pos < fx_bound_pos
        ), f".l init at pos {l_init_pos} should precede .fx bound at pos {fx_bound_pos}"

    def test_deferred_bounds_wrapped_in_implicit_assign(self, manual_index_mapping):
        """Deferred bounds must be wrapped in $onImplicitAssign/$offImplicitAssign."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)
        x_var = VariableDef(name="x", domain=(), kind=VarKind.CONTINUOUS)
        x_var.fx_expr = VarRef(name="x", attribute="l")  # x.fx = x.l
        model.variables["x"] = x_var

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])
        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)
        result = emit_gams_mcp(kkt)
        lines = result.splitlines()

        # Find the deferred .fx line and verify it's between $onImplicitAssign/$offImplicitAssign
        fx_idx = next(i for i, ln in enumerate(lines) if "x.fx = x.l" in ln)
        preceding = lines[:fx_idx]
        following = lines[fx_idx + 1 :]
        # Last $onImplicitAssign before .fx line
        on_indices = [i for i, ln in enumerate(preceding) if "$onImplicitAssign" in ln]
        off_indices = [i for i, ln in enumerate(following) if "$offImplicitAssign" in ln]
        assert on_indices, "$onImplicitAssign not found before deferred .fx bound"
        assert off_indices, "$offImplicitAssign not found after deferred .fx bound"

    def test_non_l_bounds_not_deferred(self, manual_index_mapping):
        """Bounds that don't reference .l should stay in the early section."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)
        x_var = VariableDef(name="x", domain=(), kind=VarKind.CONTINUOUS)
        x_var.lo_expr = Const(0.0)  # x.lo = 0 (no .l reference)
        model.variables["x"] = x_var

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])
        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)
        result = emit_gams_mcp(kkt)

        # x.lo = 0 should be in early "Variable Bounds" section, not inside
        # a deferred $onImplicitAssign block.  Use comment-independent markers.
        lines = result.splitlines()
        lo_idx = next(
            (i for i, ln in enumerate(lines) if "x.lo = 0;" in ln or "x.lo = 0.0;" in ln),
            None,
        )
        assert lo_idx is not None, "x.lo bound not found in emitted result"

        # Verify x.lo is NOT between a $onImplicitAssign/$offImplicitAssign pair
        # that wraps deferred bounds (if any such pair exists after init).
        on_off_pairs: list[tuple[int, int]] = []
        on_stack: list[int] = []
        for i, ln in enumerate(lines):
            if "$onImplicitAssign" in ln:
                on_stack.append(i)
            elif "$offImplicitAssign" in ln and on_stack:
                on_off_pairs.append((on_stack.pop(), i))
        for on_idx, off_idx in on_off_pairs:
            assert not (on_idx < lo_idx < off_idx), (
                f"x.lo at line {lo_idx} is inside $onImplicitAssign block "
                f"(lines {on_idx}-{off_idx}), should be in early bounds"
            )

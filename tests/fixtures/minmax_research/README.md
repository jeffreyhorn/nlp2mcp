# Min/Max Reformulation Research Test Cases

**Purpose:** Validate reformulation strategies for min/max in objective-defining equations

**Research Document:** `docs/research/minmax_objective_reformulation.md`

**Sprint 5 Prep Task:** Task 2 - Research Min/Max Reformulation Strategies

---

## Test Cases Overview

### Original NLP Models

These test the original GAMS NLP formulations to establish expected solutions:

1. **test1_minimize_min.gms** - minimize z where z = min(x,y)
2. **test2_maximize_max.gms** - maximize z where z = max(x,y) 
3. **test3_minimize_max.gms** - minimize z where z = max(x,y)
4. **test4_maximize_min.gms** - maximize z where z = min(x,y)
5. **test5_nested_minmax.gms** - nested min/max
6. **test6_constraint_min.gms** - min in constraint (regression test)

### Manual MCP Reformulations

These test Strategy 2 (Direct Constraints) by manually creating MCP formulations:

1. **test1_minimize_min_manual_mcp.gms** - Strategy 2 applied to test 1

---

## Key Findings

### Finding 1: Strategy 2 FAILS for minimize z where z = min(x,y)

**Mathematical Proof:**

Strategy 2 reformulation:
```
minimize z
s.t. z <= x
     z <= y
```

KKT stationarity for z:
```
∂L/∂z = 1 + λ_x + λ_y = 0
```

Where λ_x, λ_y ≥ 0 (multipliers for inequalities)

**Problem:** This requires λ_x + λ_y = -1, which is impossible since both must be ≥ 0.

**Conclusion:** Strategy 2 DOES NOT WORK for this case.

**Implication:** The research doc's Strategy 2 is NOT a viable solution. We need Strategy 1 (Objective Substitution) or Strategy 3 (Parse-time reformulation) instead.

---

## Test Results

### Test 1: minimize z where z = min(x,y)

**Strategy 2 Result:** INFEASIBLE (as predicted)

The manual MCP file `test1_minimize_min_manual_mcp.gms` demonstrates the mathematical impossibility.

**Next Steps:**
- Test the symmetric case (test 2: maximize/max)
- Determine if any sense/function combinations work with Strategy 2
- If Strategy 2 fails for all cases, abandon it and focus on Strategy 1

---

## Research Questions Status

From `docs/planning/SPRINT_5/KNOWN_UNKNOWNS.md`:

### Unknown 1.1: Does Strategy 2 handle all objective-defining cases?

**Status:** ❌ DISPROVEN

**Finding:** Strategy 2 (Direct Constraints) FAILS for minimize z where z = min(x,y)

**Reason:** Creates mathematically infeasible KKT system (requires negative multipliers)

**Remaining Tests:**
- [ ] Test 2: maximize z where z = max(x,y) - May work (symmetric)
- [ ] Test 3: minimize z where z = max(x,y) - Need to test
- [ ] Test 4: maximize z where z = min(x,y) - Need to test

### Unknown 1.2: How to detect objective-defining min/max?

**Status:** Not yet addressed - depends on whether Strategy 2 works for ANY cases

### Unknown 1.3: Nested min/max handling?

**Status:** Not yet addressed - depends on Strategy 2 viability

---

## Recommendation

Based on Test 1 results, Strategy 2 is NOT a general solution. 

**Action Items:**
1. Complete testing of all 4 sense/function combinations (min/max with minimize/maximize)
2. If Strategy 2 only works for symmetric cases (min/minimize, max/maximize), document limitation
3. If Strategy 2 fails for all cases, ABANDON and focus on Strategy 1 (Objective Substitution)
4. Update research doc with findings
5. Update Known Unknowns with verified results
6. Update Sprint 5 Priority 1 implementation plan accordingly

---

## References

- Research doc: `docs/research/minmax_objective_reformulation.md`
- Known Unknowns: `docs/planning/SPRINT_5/KNOWN_UNKNOWNS.md` (Category 1)
- Prep Plan: `docs/planning/SPRINT_5/PREP_PLAN.md` (Task 2)

# Plan: Fix fawley MCP EXECERROR (Empty Equation + Unfixed Multiplier)

**Goal:** Fix the GAMS execution error that prevents fawley's MCP from
solving.

**Issue:** #1133 (fawley: Empty mbal equation for vacuum-res)
**Estimated effort:** 2–3 hours
**Models unblocked:** fawley (and potentially other models with empty
equation instances due to sparse data)

---

## Current State

fawley translates successfully but GAMS aborts the SOLVE with
`EXECERROR = 1`:

```
**** MCP pair mbal.nu_mbal has empty equation but associated variable is NOT fixed
     nu_mbal(vacuum-res)
**** SOLVE from line 350 ABORTED, EXECERROR = 1
```

The element `vacuum-res` appears in set `c` but has no entries in any
process yield table, blend possibility, or recipe.  The equation
`mbal('vacuum-res')` evaluates to `0 =E= 0` (all coefficients zero),
making it an empty equation.  GAMS requires that the multiplier variable
for an empty MCP equation be fixed (`.fx = 0`), otherwise it aborts.

---

## Model Structure

Fawley is a refinery blending LP with:
- 18 commodities (`c`), 8 processes (`p`), 3 transport modes (`tr`)
- 4 product types (`cf`), 3 crude types (`cr`), 1 import (`ci`)
- Objective: maximize `profit` (scalar, via chain of defining equations)

The `mbal(c)` equation tracks material balance for each commodity:
```gams
mbal(c).. u(c)$(cr(c)) + sum(p, ap(c,p)*z(p)) + sum(tr, at(c,tr)*trans(tr))
          + import(c)$(ci(c))
    =E= sum(cfq$(bposs(cfq,c)), bq(c,cfq)) + invent(c)
         + sum((cfr,r), recipes(cfr,c,r)*rb(cfr,r));
```

For `vacuum-res`: `cr('vacuum-res')` is false, no `ap('vacuum-res',p)`
entries exist, no `at('vacuum-res',tr)` entries, no `bposs` entries,
no `recipes` entries → all terms are zero.

---

## Root Cause

The emitter pairs `mbal(c)` with `nu_mbal(c)` in the MCP model
statement for ALL elements of `c`, including `vacuum-res`.  When the
equation body evaluates to `0 =E= 0`, GAMS requires the multiplier
to be fixed:

```gams
nu_mbal.fx('vacuum-res') = 0;
```

This `.fx` statement is not emitted.

---

## Fix Strategy

### Approach: Detect and fix multipliers for empty equation instances

After assembling the KKT system and before emission, scan each equality
equation instance for empty bodies.  For instances where all variable
coefficients are zero (the equation reduces to a constant), fix the
corresponding multiplier to zero.

**Implementation options:**

**Option A: Emission-time detection (simplest)**

In `src/emit/emit_gams.py`, after the equation definitions are emitted
and before the model statement, add a pass that:

1. For each indexed equality equation, evaluate which instances have
   non-zero variable coefficients
2. For instances where the body is all-zero, emit
   `nu_<eq>.fx(<element>) = 0;`

This can use the Jacobian to check: if no row in `J_eq` corresponds to
a given equation instance, or if all derivatives in that row are zero,
the equation is empty.

**Option B: IR-level detection (more robust)**

Add a helper in `src/kkt/` that uses the Jacobian structure to identify
empty equation instances, and store them in the KKTSystem. The emitter
then reads this list and emits `.fx` statements.

### Recommended: Option A

It's the simplest path — the Jacobian already has the information. For
each equation in the MCP, check which instances have Jacobian rows with
at least one non-zero derivative.  Instances with no non-zero entries
get their multiplier fixed to 0.

```python
# In emit_gams_mcp(), after equation definitions:
for eq_name in kkt.multipliers_eq:
    mult_name = create_eq_multiplier_name(eq_name)
    eq_def = kkt.model_ir.equations.get(eq_name)
    if not eq_def or not eq_def.domain:
        continue  # scalar equations can't have empty instances
    # Find equation instances with no Jacobian entries
    for row_id in range(kkt.J_eq.num_rows):
        rname, ridx = kkt.J_eq.index_mapping.row_to_eq[row_id]
        if rname != eq_name:
            continue
        has_nonzero = any(
            kkt.J_eq.get_derivative(row_id, col_id) is not None
            for col_id in range(kkt.J_eq.index_mapping.num_vars)
        )
        if not has_nonzero:
            idx_str = ",".join(f"'{i}'" for i in ridx)
            sections.append(f"{mult_name}.fx({idx_str}) = 0;")
```

---

## Secondary Issue: Stationarity Equations Look Trivial

The stationarity equations for scalar intermediate variables
(`purchase`, `recurrent`, `revenue`, `transport`) look trivial:

```gams
stat_purchase.. 1 + nu_dpur =E= 0;
stat_revenue.. -1 + nu_drev =E= 0;
```

These are **actually correct** — they solve to `nu_dpur = -1` and
`nu_drev = 1`. The constant term is the objective gradient (negated
for MAX), and the multiplier term is from the defining equation's
Jacobian. These equations constrain the multipliers to specific values,
which is correct for scalar variables defined by a single equation.

At initialization (`nu_dpur.l = 0`), they appear infeasible (LHS=0,
RHS=-1), but PATH solves them trivially. **This is not a bug.**

---

## Verification

```bash
python -m src.cli data/gamslib/raw/fawley.gms -o /tmp/fawley_mcp.gms --quiet

# Check the .fx statement is emitted
grep "nu_mbal.fx" /tmp/fawley_mcp.gms
# Expected: nu_mbal.fx('vacuum-res') = 0;

# Compile and solve
gams /tmp/fawley_mcp.gms lo=3 o=/tmp/fawley_solve.lst
grep "MODEL STATUS" /tmp/fawley_solve.lst
# Expected: MODEL STATUS 1 Optimal

grep "nlp2mcp_obj_val" /tmp/fawley_solve.lst | grep "="
# Expected: ~2899.25 (matching NLP reference)
```

---

## Success Criteria

- [ ] `nu_mbal.fx('vacuum-res') = 0;` emitted in the MCP file
- [ ] GAMS compilation succeeds (no EXECERROR)
- [ ] fawley solves to MODEL STATUS 1 or 2
- [ ] Objective matches NLP reference (2899.25) within tolerance
- [ ] No test regressions (`make test` passes)
- [ ] Other models with empty equation instances unaffected or improved

---

## Files to Modify

| File | Change |
|------|--------|
| `src/emit/emit_gams.py` | Add empty-equation multiplier fixing after equation definitions |
| `tests/` | Add test for empty equation multiplier fixing |
| `docs/issues/completed/ISSUE_1133*` | Update status to FIXED |

---

## Related Issues

- **#1133**: fawley empty mbal equation (this fix)
- **#1130** (FIXED): fawley table column alignment
- **#1041**: cesam2 empty equation (similar pattern, different model)

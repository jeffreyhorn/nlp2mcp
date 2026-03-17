# markov: Stationarity Uses Single Representative Derivative for Multi-Pattern Jacobian

**GitHub Issue:** [#1110](https://github.com/jeffreyhorn/nlp2mcp/issues/1110)
**Status:** OPEN
**Model:** markov (GAMSlib SEQ=82)
**Error category:** `path_solve_terminated` (MODEL STATUS 5, Locally Infeasible)
**NLP objective:** 2401.577

## Description

The markov model translates to MCP but PATH immediately exits with infeasibility (0 iterations, residual 1e20). The root cause is that `_add_indexed_jacobian_terms()` in `src/kkt/stationarity.py` picks a single representative Jacobian entry and generalizes its derivative expression to ALL constraint-variable pairings via a sum. This is incorrect when the derivative expression structurally differs across pairings — specifically when some pairings include a Kronecker-delta "+1" term and others do not.

## Root Cause

The original `constr` equation in markov is:

```gams
constr(sp,j).. sum(spp, z(sp,j,spp)) - b * sum((s,i,spp), pi(s,i,sp,j,spp) * z(s,i,spp)) =E= beta;
```

The Jacobian `d constr(sp',j') / d z(s,i,sp)` has two components:

1. **From `sum(spp, z(sp',j',spp))`:** Derivative is `1` **only when** `sp'=s AND j'=i` (i.e., `spp=sp` matches the variable's 3rd index). This is a Kronecker delta: `delta(sp'=s, j'=i)`.

2. **From `-b * sum((s'',i'',spp), pi(s'',i'',sp',j',spp) * z(s'',i'',spp))`:** Derivative is `-b * pi(s,i,sp',j',sp)` for **all** `(sp', j')` pairings.

So the correct full derivative is:

```
d constr(sp',j') / d z(s,i,sp) = delta(sp'=s, j'=i) - b * pi(s,i,sp',j',sp)
```

The AD system computes the derivative for each specific `(constr(sp0,j0), z(s0,i0,sp0_var))` pair individually:
- When `sp0=s0, j0=i0`: returns `1 - b*pi(s0,i0,sp0,j0,sp0_var)`
- When `sp0!=s0` or `j0!=i0`: returns `-b*pi(s0,i0,sp0,j0,sp0_var)`

But `_add_indexed_jacobian_terms()` picks a **single representative entry** (one where `sp0=s0, j0=i0`) and uses its derivative expression `(1 - b*pi(s,i,s__kkt1,j,sp))` for ALL `(s__kkt1, j)` in the sum. This incorrectly adds `+1` to every entry, not just the diagonal.

## Current (Wrong) Output

```gams
stat_z(s,i,sp).. c(s,sp,i)
    + sum((s__kkt1,j), (1 - b * pi(s,i,s__kkt1,j,sp)) * nu_constr(s__kkt1,j))
    + ...
```

This expands to `SUM nu_constr(s__kkt1,j) - b * SUM pi(...) * nu_constr(...)`, where the first sum includes ALL 16 `nu_constr` terms. The correct first sum should be only `nu_constr(s,i)`.

## Expected (Correct) Output

```gams
stat_z(s,i,sp).. c(s,sp,i)
    + nu_constr(s,i)
    + sum((s__kkt1,j), (- b * pi(s,i,s__kkt1,j,sp)) * nu_constr(s__kkt1,j))
    + ...
```

Or equivalently using sameas:

```gams
stat_z(s,i,sp).. c(s,sp,i)
    + sum((s__kkt1,j), (sameas(s__kkt1,s)*sameas(j,i) - b * pi(s,i,s__kkt1,j,sp)) * nu_constr(s__kkt1,j))
    + ...
```

## Reproduction

```bash
python -m src.cli data/gamslib/raw/markov.gms -o /tmp/markov_mcp.gms
# Check stat_z equation — the nu_constr sum should NOT have "+1" for all entries
grep "stat_z" /tmp/markov_mcp.gms

# Run in GAMS:
gams /tmp/markov_mcp.gms lo=3
# Expected: MODEL STATUS 5 (Locally Infeasible), 0 iterations
```

To verify the derivative values, inspect the GAMS listing (limrow=3):
```bash
gams /tmp/markov_mcp.gms lo=3 limrow=3
# In stat_z(empty,normal,empty), nu_constr(3,normal) has coefficient 1.0
# But it should have coefficient -b*pi(empty,normal,3,normal,empty) = 0
# (since pi is only nonzero when 3rd and 5th indices match)
```

## Analysis

The problem is architectural in `_add_indexed_jacobian_terms()` (~line 2649 in `src/kkt/stationarity.py`). The function:

1. Groups Jacobian entries by offset pattern (`offset_groups`)
2. For each offset group, takes `group_entries[0]` as the representative
3. Extracts the derivative expression from that one entry
4. Uses it as the body of `sum((mult_domain), derivative * multiplier)`

This "single representative" approach works when all entries in the group have the **same symbolic derivative** (which is the common case — e.g., when a constraint body is `sum(j, a(i,j)*x(j))`, every `d/dx(j)` gives `a(i,j)` with the same symbolic form).

But it fails for `constr(sp,j)` because:
- `z(sp,j,spp)` appears as a "direct" variable reference (the constraint's own domain matches the first two variable indices)
- `z(s,i,spp)` also appears inside `sum((s,i,spp), ...)` with independent iteration variables
- The derivative combines both: `delta_diagonal + indirect_term`
- Different Jacobian entries have different derivative expressions depending on whether the constraint indices match the variable indices

## Potential Fix Approaches

### Approach A: Split Jacobian entries by derivative expression

Within each offset group, sub-group entries by whether their derivative expression is structurally the same. If there are multiple distinct derivative expressions, emit separate stationarity terms for each sub-group (with appropriate sameas guards for the restricted entries).

For markov, this would produce:
- Group 1 (diagonal, `sp'=s, j'=i`): `(1 - b*pi(s,i,s,i,sp)) * nu_constr(s,i)` — direct term
- Group 2 (off-diagonal): `sum((s__kkt1,j)$(not (sameas(s__kkt1,s) and sameas(j,i))), (-b*pi(s,i,s__kkt1,j,sp)) * nu_constr(s__kkt1,j))` — sum term

### Approach B: Detect and decompose multi-reference constraints

When the AD reports that a constraint has multiple VarRef nodes for the same variable (one direct, one inside a sum), decompose the Jacobian contribution into:
1. The "direct" part (Kronecker delta) — emitted as a non-summed `nu_constr(s,i)` term
2. The "indirect" part — emitted as a summed term

### Approach C: Sample multiple representative entries

Instead of using `group_entries[0]` only, sample a diagonal and off-diagonal entry. If their derivatives differ, detect the pattern and handle accordingly.

## Impact

This bug affects any model where a constraint body contains BOTH:
- A direct VarRef to the decision variable with constraint-domain indices (e.g., `z(sp,j,spp)`)
- A sum over the same variable with independent iteration indices (e.g., `sum((s,i,spp), pi*z(s,i,spp))`)

This is the "self-referential transition" pattern common in Markov/dynamic programming models.

## Related Issues

- #1104 (markov): AD quoted-index fix + dimension-mismatch alias collision (FIXED)
- #914 (markov): Uninitialized pi parameter (FIXED)

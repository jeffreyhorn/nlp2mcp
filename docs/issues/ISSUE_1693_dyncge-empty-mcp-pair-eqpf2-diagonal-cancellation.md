# dyncge: empty MCP pair `eqpf2.nu_eqpf2` from diagonal self-cancellation (EXECERROR=4)

**GitHub:** #1693 · **Model:** `dyncge` (A Recursive-Dynamic Standard CGE Model) · **Status:** OPEN
**Created:** Sprint 38 Day 3 (P7 Phase-0 backfill) · **Measured at:** `2723c22a`, GAMS **54.2.1** / PATH **5.2.01**

## Problem Summary

`dyncge` aborts at **GAMS execution, before PATH is invoked** (`solver_version: None`; DB outcome `path_solve_terminated`):

```
**** MCP pair eqpf2.nu_eqpf2 has empty equation but associated variable is NOT fixed   (×4)
**** SOLVE from line 569 ABORTED, EXECERROR = 4
```

## Root Cause

`eqpf2` carries **no condition at all** — not on the head, not on the body:

```gams
eqpf2(h_mob,i,j).. pf(h_mob,j) =e= pf(h_mob,i);
```

On the **diagonal `i = j`** this reads `pf(h_mob,j) =e= pf(h_mob,j)`; every coefficient cancels and GAMS generates a **structurally empty row**. An MCP requires an empty row to be paired with a **fixed** column, and `nu_eqpf2` is not fixed there.

**⚠ Same symptom as #1331 (twocge), different cause.** twocge's rows are empty because a `$`-condition removes the body; dyncge's are empty because the two sides are the *same expression* under `i = j`. **A fix that lifts dollar conditions will not detect dyncge.** This distinction was measured, not assumed — dyncge's IR shows `condition = None` and `lhs_rhs[0] = VarRef(pf(h_mob,j))` with no `DollarConditional`.

---

## Phase 0: Acceptance Gate

### Hand-Derived KKT Shape

`eqpf2` states that the mobile factor's price is equal across sectors: `pf(h_mob,j) = pf(h_mob,i)` for every ordered pair `(i,j)`. The relation is **reflexive**, so the diagonal instance `i = j` is the tautology `pf = pf` — it carries **no information and defines no constraint**.

A KKT multiplier prices a constraint. For an instance that is identically satisfied for *all* values of the primal variables, there is no constraint to price: the multiplier is not merely unconstrained, it is **meaningless**. The correct shape is therefore

> `nu_eqpf2(h_mob,i,j)` **must be fixed to 0 exactly on the tautological instances**, i.e. where `i = j`.

With `h_mob = {LAB}` and `i = {AGR, LMN, HMN, SRV}` that is **4 instances** — `(LAB,AGR,AGR)`, `(LAB,LMN,LMN)`, `(LAB,HMN,HMN)`, `(LAB,SRV,SRV)` — and 4 is exactly the measured `EXECERROR`. The remaining **12** off-diagonal rows are genuine and must be untouched.

This is a **0-bucket well-formedness fix**: it removes an abort; it changes the mathematics of no instance that actually exists.

### Expected Emit Pattern

```gams
nu_eqpf2.fx(h_mob,i,j)$(sameas(i,j)) = 0;
```

The emitted model currently contains **one** `nu_*.fx(` guard and **none** for `eqpf2`.

**Traced fix-surface (Day-3, `2723c22a`):** `src/emit/emit_gams.py`, the §3 equality-multiplier fixing loop (~`3255–3273`). It bails at `if eq_def.condition is None: continue` — and unlike twocge, **dyncge has no condition to lift from the body either**. Detecting this case requires recognising that the equation's LHS and RHS become the **same expression** under an index identification, i.e. a structural self-cancellation test on `lhs_rhs`, which is **new logic rather than a widened condition-lift**.

**⚠ The line numbers are a traced hypothesis, not a result** — prep-doc fix surfaces were wrong ~4× in Sprint 27. Confirm before implementing.

### Verification Methodology

Run from a **scratch directory**, never the repo root (GAMS writes scratch files to `cwd`).

1. **Fail-before** (`2723c22a`): `gams dyncge_mcp.gms lo=0 errmsg=1` → `rc=3`, with **4 × `**** MCP pair eqpf2.nu_eqpf2 has empty equation but associated variable is NOT fixed`** and **`**** SOLVE from line 569 ABORTED, EXECERROR = 4`**. The count is **derived**: card(h_mob) × card(i) diagonal = 1 × 4 = 4 = the EXECERROR.
2. **Structural assertion, stronger than the count:** the equation listing must show `eqpf2` generating **12** rows after the fix (the off-diagonal pairs), and the four diagonal instances must be *absent from the pairing*, not merely silent.
3. **Pass-after:** zero `has empty equation but associated variable is NOT fixed` lines; no `ABORTED, EXECERROR`; `modelstat` asserted before any objective read.
4. **Leak gate:** `make check-goldens` shows **only `dyncge` drifting**. **State the in-scope count in the result** — it is **185 after P4's Day-8 adoption, not 163**.
5. **Determinism:** byte-stable golden across `PYTHONHASHSEED {0,1,42}`.

**Read counts from GAMS's own `**** N ERROR(S)` / `EXECERROR = n` line, never from `grep -o '$NNN'`** — marker counting undercounts even when nothing is truncated.

### PROCEED/REPLAN Signal

**PROCEED** — the 4 empty-pair messages disappear, `eqpf2` retains its 12 off-diagonal rows, `dyncge` reaches PATH (any `modelstat`), and nothing outside `dyncge` drifts.

**REPLAN** — any of: the guard fixes a multiplier on a **non**-tautological instance (that silently changes the solution); a model outside `dyncge` drifts; or the self-cancellation test proves not to be expressible on `lhs_rhs` without the enclosing index context. **If the test is not locally expressible, bank that finding rather than widening it** — that is precisely the failure mode #1668 hit twice, where a predicate looked clean on inspection and the discriminating information was not present at the site.

### Bucket / KPI

**0 bucket expected.** dyncge is `path_solve_terminated` with `solver_version: None` — it aborts **before PATH is invoked**. Clearing the abort lets it *reach* PATH; whether it then solves or matches is **unclaimed**. **Do not project a Solve or Match gain.** NLP reference: **MS-2 @ 539570.5027**.

### Regression guard

A fixture asserting that a reflexive equality equation (`e(i,j).. v(j) =e= v(i)`) yields a multiplier fixed on the diagonal and free off it. **The fixture must be a minimal synthetic model, not dyncge** — dyncge's emit is slow enough to make it a poor unit fixture.

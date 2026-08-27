# dyncge: empty MCP pair `eqpf2.nu_eqpf2` from diagonal self-cancellation (EXECERROR=4)

**GitHub:** #1693 · **Model:** `dyncge` (A Recursive-Dynamic Standard CGE Model) · **Status:** ✅ **RESOLVED (2026-08-26)** — Sprint 38 Day 12, PR #1704, main `31340922`
**Resolution:** section 2c's diagonal-triviality test **reused for equalities** as a new section 3c — the gate's claim that this needed *new logic* was wrong; the test had existed since **#942** and was only ever applied to inequalities. `eqpf2` now generates **12 off-diagonal rows and 0 diagonal**, **0** empty-pair errors, `MODEL STATUS 1 Optimal`. **Solve +1; Match NOT claimed.**
**⚠ Closing this issue does NOT mean dyncge is correct.** The abort was *masking* a second, independent defect: `kkt_residual.py` → **`CASE_B`**, max relative **6.22e-02** at `stat_pf(CAP,SRV)`; the cold MCP solves to **381401.119** against the NLP's **539570.5027** (29.3 % mismatch). That is a **new diagnosis in the `pf`/`pq` block, not `eqpf2`**, and needs its own issue — **this one is not widened to cover it.**
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

---

## Resolution — Sprint 38 Day 12 (2026-08-25)

**Status: FIXED as specified.** `dyncge` `path_solve_terminated` → **`model_optimal`** (Solve +1). **Match NOT claimed** — see the new finding below.

**Fingerprint re-reproduced at `cf8c0284`** (fresh translate byte-identical to the committed golden): rc 3 · **4 × `**** MCP pair eqpf2.nu_eqpf2 has empty equation but associated variable is NOT fixed`** · `**** SOLVE from line 569 ABORTED, EXECERROR = 4`. The count is derived, not counted: `card(h_mob) × card(i)` diagonal = 1 × 4 = 4 = the `EXECERROR`.

### ⚠ The gate was wrong that this needs new logic

The gate says *"Detecting this case requires recognising that the equation's LHS and RHS become the same expression under an index identification … which is **new logic** rather than a widened condition-lift."*

**That logic already existed.** Section **2c** (`emit_gams.py`, #942 / #1021 / #1104) has performed exactly this diagonal-triviality test — substitute `d_j → d_i`, then four escalating emptiness checks — since Sprint 24. **It was never inequality-specific; it was only ever *applied* to `kkt.complementarity_ineq`.** dyncge's `eqpf2` is an equality, so it never reached the loop.

The change is therefore a **reuse**, not new machinery:

- `_diagonal_instance_is_trivial(eq_def, d_i, d_j, model_ir)` — 2c's four checks, extracted verbatim.
- `_same_set_domain_pairs(domain, resolve_canonical)` — the alias-root pairing, extracted.
- **Section 3c** — the equality analogue, emitting `nu_<eq>.fx(<domain>)$(ord(d_i) = ord(d_j)) = 0;`.
- Section 2c now calls the helper, so both populations share one implementation and one hardening history.

The emitted guard uses `ord(i) = ord(j)` rather than the gate's `sameas(i,j)`; they select the same instances, and `ord` matches what 2c has always emitted.

**Soundness, stated explicitly:** the test is **sufficient, not necessary**. It may miss an empty row, but it must never call a live row empty — pinning the multiplier of a constraint that actually binds is a *silent wrong answer*, not an error. That is #1693's own REPLAN condition, and it is why the negative-control test (`v(j) =e= 2*v(i)`, whose diagonal `v = 2v` is informative) asserts that **no** guard is emitted.

### Verification

| gate criterion | before | after |
|---|---|---|
| `has empty equation but associated variable is NOT fixed` | **4** | **0** |
| `eqpf2` rows generated | — | **12**, and **0 diagonal** (counted from the equation listing) |
| terminal state | `ABORTED, EXECERROR = 4` | rc **0**, no `ABORTED` |
| modelstat (GAMS's own line) | — | **`MODEL STATUS 1 Optimal`** |

**Leak gate PASS at 186 in-scope** (7 allowlisted; scope is 186 after Day 12 adopted `elec_mcp_presolve.gms`) — **exactly `dyncge` drifted** (+46 bytes). Section 3c fires on **one model in the whole corpus**.

Regression guard: `tests/unit/emit/test_equality_diagonal_multiplier_fix.py` (4) — a **minimal synthetic** reflexive equality (per the gate: *not* dyncge) yields a diagonal-only guard; the guard is never unconditional; a non-reflexive equality gets none; a single-index equality is untouched.

### ⚠ NEW FINDING — dyncge has a SECOND, independent emit defect

`scripts/diagnostics/kkt_residual.py data/gamslib/raw/dyncge.gms` → **`CASE_B — emit_bug`**, max relative stationarity residual **6.22e-02** (tol 1e-3) at `stat_pf(CAP,SRV)`; dual transfer CONSISTENT.

Warm-started at the NLP's own KKT point, dyncge's stationarity rows do **not** evaluate to zero. The empty-pair abort was real and is fixed, but it was **masking** a gradient defect underneath. Consequences:

- The cold MCP solves to `MODEL STATUS 1 Optimal` at **381401.119** against the NLP's **539570.5027** — a **29.3 %** mismatch, recorded as `mismatch`.
- The presolve retry also fails to match (`0/1`), so there is **no spurious match** to adjudicate here.
- **Solve +1 is genuine; Match is 0 and must not be claimed.** #1693's own Bucket/KPI note anticipated exactly this: *"Clearing the abort lets it reach PATH; whether it then solves or matches is unclaimed."*

**This needs a new issue and a new diagnosis** — it is not #1693, and #1693 should be closed on its own terms rather than widened to cover it. The top residual rows are `stat_pf(CAP,SRV)`, `stat_pq(HMN)`, `stat_pf(LAB,SRV)`, `stat_pf(LAB,HMN)`, `stat_pf(CAP,LMN)`, which points at the `pf`/`pq` block rather than at `eqpf2`.

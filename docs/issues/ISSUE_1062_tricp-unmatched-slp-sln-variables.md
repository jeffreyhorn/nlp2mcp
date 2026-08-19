# tricp: Unmatched Variables `slp`/`sln` — 760 MCP Errors

**GitHub Issue:** [#1062](https://github.com/jeffreyhorn/nlp2mcp/issues/1062)
**Status:** OPEN
**Severity:** High — execution errors, model fails to solve
**Date:** 2026-03-12
**Affected Models:** tricp

---

## Problem Summary

The tricp model's generated MCP file has 760 "Unmatched variable not free or fixed" errors for variables `slp(i,j)` and `sln(i,j)`. The stationarity equations `stat_slp(n,n)` and `stat_sln(n,n)` are defined over the full `(n,n)` cross product (400 instances for 20 nodes), but these variables only participate in equation `eq1(e(i,j))` which is conditioned on the edge set `e`. Off-edge instances have no corresponding equation in the MCP model.

---

## Error Details

GAMS execution errors (760 total):
```
**** Unmatched variable not free or fixed
     slp(n0,n1)

**** Unmatched variable not free or fixed
     slp(n0,n2)
...
```

380 errors for `slp` + 380 errors for `sln` = 760 total.

Additionally, the model exceeds GAMS demo license limits:
```
**** The model exceeds the demo license limits for nonlinear models of more than 1000 rows or columns
**** SOLVE from line 190 ABORTED, EXECERROR = 760
```

Model size: 779 equations x 1,723 variables (43,836 nonlinear elements).

---

## Root Cause

In the original GAMS model:
```gams
Set e(n,n) 'edge pairs' / n0.n1, n0.n2, ... /;  (* sparse 2D subset *)
Variable slp(n,n) 'positive slack';
Variable sln(n,n) 'negative slack';

eq1(e(i,j))..
   sum(k, sqr(x(i,k) - x(j,k))) =e= sqr(r(i) + r(j)) + slp(e) - sln(e);
```

Key observations:
1. `slp` and `sln` are declared over `(n,n)` (full cross product: 20x20 = 400 instances)
2. But they only appear in `eq1(e(i,j))` which is conditioned on edge set `e` (sparse: ~20 edges)
3. In the original NLP, only `e`-active instances of `slp`/`sln` matter

The MCP transformation generates `stat_slp(n,n)` and `stat_sln(n,n)` over the full `(n,n)` domain. The MCP model definition pairs `stat_slp.slp` and `stat_sln.sln`, but for the ~380 off-edge instances, these stationarity equations are trivially `0 =E= 0` (no gradient terms), while the corresponding `slp`/`sln` variables exist and are positive. GAMS requires every non-free, non-fixed variable to be matched with exactly one equation in MCP.

The fix should either:
1. Condition `stat_slp`/`stat_sln` on `e(n,n)` and fix off-edge `slp`/`sln` instances to 0
2. Or restrict the variable declaration domain to match the active equation domain

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/tricp.gms -o /tmp/tricp_mcp.gms
gams /tmp/tricp_mcp.gms lo=2
# NOTE: As of 2026-04-01, compilation fails first with $148/$149 errors
# (see ISSUE_933). The 760 unmatched-variable errors described below
# were observed on an earlier version before the compilation errors appeared.
```

---

## Proposed Fix

The stationarity equation builder needs to detect when a variable only participates in equations conditioned on a subset. For `slp(n,n)` which only appears in `eq1(e(i,j))`, the stationarity `stat_slp` should be conditioned on `e`:

```gams
stat_slp(i,j)$(e(i,j)).. ... =E= 0;
slp.fx(i,j)$(not e(i,j)) = 0;
```

This is similar to the multiplier domain widening pattern but in reverse — here we need to restrict the stationarity domain to match the active equation domain, rather than widen a multiplier domain.

---

## Related

- #1056 tricp: smax emission dimension mismatch (FIXED — separate compilation issue)
- #933 tricp: translation timeout (resolved by timeout increase)
- This is a domain/conditioning issue in the stationarity builder, not the expression emitter

---

## Sprint 24 Progress

### Fix 1: Gradient condition index remapping (compilation fix)
Added `_remap_condition_to_domain` in `stationarity.py` that remaps gradient
condition indices to the variable's domain. `SetMembershipTest(e, (n, i))` →
`SetMembershipTest(e, (n, n))` when the variable domain is `(n, n)`.

**Result:** Compilation errors ($149) resolved. Unmatched variables reduced
from 760 to 108.

### Remaining: 108 unmatched variables
The 108 remaining unmatched variables are EDGE instances of `slp`/`sln`
where the stationarity equation `stat_slp(n,n)` is valid but doesn't
reference variable `slp`. This is because `slp` has derivative = 1 in
`eq1` (linear coefficient), so the stationarity reduces to
`nu_eq1 + bounds = 0` — the variable itself doesn't appear.

**NOT FIXED** — this is a fundamental MCP formulation issue where variables
with unit-coefficient derivatives produce stationarity equations that
don't reference the paired variable. GAMS MCP requires the paired
variable to appear in the equation.

Possible fix: add `0*slp(n,n)` dummy term to force the variable reference
in the stationarity equation, or use a different MCP formulation for
linear variables.

## Phase 0: Acceptance Gate

**Authored:** Sprint 38 Day 2 (P7 backfill) · **Fingerprint re-reproduced at `b823a9a5`**, GAMS 54.2.1 / PATH 5.2.01.

**⚠ The "760 MCP errors" in this doc's title and body does NOT reproduce. The measured count today is 108** (54 `slp` + 54 `sln`), and the model **compiles cleanly** — the note claiming `$148`/`$149` compilation errors block reproduction is also stale. See *Verification Methodology* for the current, derived figures.

### Hand-Derived KKT Shape

`tricp` declares the slacks over a repeated set: `slp(n,n)`, `sln(n,n)`, with `card(n) = 20`. They are used only on the sparse edge set `e(n,n)` (**54 edges**, no self-loops):

```gams
eq1(e(i,j)).. sum(k, sqr(x(i,k) - x(j,k))) =e= sqr(r(i) + r(j)) + slp(e) - sln(e);
obj..         obj =e= 100*z + sum(e, slp(e) + sln(e));
```

∂L/∂slp(i,j) exists **for every edge** `(i,j) ∈ e` — 54 instances — and is identically absent off-edge. So the stationarity block must span **the full `n × n` product restricted to `e`**, i.e. 54 rows for `slp` and 54 for `sln`.

**The emitted head collapses that to the diagonal.** In a GAMS equation *definition*, a repeated controlling index name binds to the **same element**, so

```gams
stat_slp(n,n)..  (…)$(e(n,n)) =E= 0;
```

ranges over only the **20 diagonal pairs** `(n,n)` — and since `e` has **no self-loops**, `$(e(n,n))` is false for all 20, so the block generates **zero rows**. Every on-edge `slp`/`sln` column is then left with no row to pair against.

> The correct shape requires the stationarity head to use **two distinct index symbols** over `n`, e.g. `stat_slp(n,n__)`, so the block spans `n × n` before the `e` restriction selects the 54 edges.

### Expected Emit Pattern

```gams
Alias(n, n__);                                        * or reuse the existing i / j aliases
stat_slp(n,n__).. ( … )$(e(n,n__)) =E= 0;             * 54 rows
stat_sln(n,n__).. ( … )$(e(n,n__)) =E= 0;             * 54 rows
```

with the pairing `stat_slp.slp` / `stat_sln.sln` unchanged, and the **existing** off-edge guards retained:

```gams
sln.fx(n,n)$(not (e(n,n))) = 0;   piL_sln.fx(n,n)$(not (e(n,n))) = 0;
slp.fx(n,n)$(not (e(n,n))) = 0;   piL_slp.fx(n,n)$(not (e(n,n))) = 0;
```

**Those guards are already emitted and are correct — they are not the defect.** The defect is solely the collapsed head domain.

**Traced fix-surface (Day-2, `b823a9a5`):** the stationarity **head-domain** emission in `src/emit/emit_gams.py`. The variable's IR domain is literally `('n','n')` (`slp`, `sln`), and that tuple is emitted verbatim as the equation head. The emitter **already has `__`-aliasing machinery** — it produces `gp__`, `i__`, `j__` for `prod`/`sum` bounds and emits `Alias(...)` lines (~`2855`) — so the fix applies existing capability to the head domain rather than adding a mechanism. **⚠ Traced hypothesis, not a result** — confirm before implementing.

### Verification Methodology

Run from a **scratch directory**.

1. **Fail-before** (`b823a9a5`): `gams tricp_mcp.gms lo=0 errmsg=1` → `rc=3`; **108 × `**** Unmatched variable not free or fixed`**, terminating in **`**** SOLVE from line 205 ABORTED, EXECERROR = 108`**. The unmatched columns are **on-edge** (`slp(n0,n1)`, `slp(n0,n2)`, …), which is what distinguishes this from an off-edge guard failure. Tally by symbol: **54 `slp` + 54 `sln`**.
2. **The decisive structural check**, which no error count alone gives you — the equation listing must show:
   ```
   ---- stat_slp  =E=            ---- stat_sln  =E=
                   NONE                          NONE
   ```
   **Zero rows generated.** After the fix each must list **54** rows. Model statistics should move from **387 single equations / 640 single variables** toward a matched pairing.
3. **Pass-after:** zero `Unmatched variable` lines; no `ABORTED, EXECERROR`; `modelstat` asserted before any objective read.
4. **Leak gate:** only `tricp` drifts. **State the in-scope count** (185 after P4's Day-8 adoption, not 163). Determinism ×3.

### PROCEED/REPLAN Signal

**PROCEED** — `stat_slp` and `stat_sln` each generate **54** rows, zero unmatched variables, `tricp` reaches PATH, and nothing outside `tricp` drifts.

**REPLAN** — aliasing the head domain perturbs any model whose stationarity head legitimately *is* diagonal (a genuine `(n,n)` diagonal relation), or the corpus sweep drifts a model outside `tricp`. **That risk is the reason this is a leak-gated change**: the repeated-domain pattern is not unique to `tricp`, and a blanket alias would be wrong for a truly diagonal equation. If the sweep shows collateral drift, bank the narrowed requirement — *alias only when the variable's own domain repeats a set AND the stationarity is restricted by a sparse subset of that product*.

### Bucket / KPI

**0 bucket expected.** `tricp` is `path_solve_terminated` with `solver_version: None` — it aborts at **GAMS execution before PATH runs**. **Translate-stable, Solve-uncertain, Match-unclaimed.**

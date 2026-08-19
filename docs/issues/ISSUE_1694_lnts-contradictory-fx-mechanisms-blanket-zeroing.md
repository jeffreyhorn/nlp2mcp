# lnts: contradictory `.fx` mechanisms pin `y` to 0 against `_fx_` equations demanding 5 and 45 (MS-4 at iteration 0)

**GitHub:** #1694 · **Model:** `lnts` (Particle steering, COPS 2.0 #9) · **Status:** OPEN
**Created:** Sprint 38 Day 3 (P7 Phase-0 backfill); defect found in Sprint 38 prep (Task 10) · **Measured at:** `2723c22a`, GAMS **54.2.1** / PATH **5.2.01**

## Problem Summary

`lnts` emits and **compiles cleanly** (`gams rc=0`), but PATH returns **MODEL STATUS 4 Infeasible at ITERATION COUNT 0** — the signature of a contradiction detected during setup, not a numerical failure.

## Root Cause — two `.fx` mechanisms acting on the same cells

The emitter turns a labelled `.fx` into an **equation + multiplier pair**, which is correct and preserves the value:

```gams
y_fx_y2_h50.. y("y2","h50") - 5  =E= 0;
y_fx_y3_h50.. y("y3","h50") - 45 =E= 0;
```

A **second, independent mechanism** blanket-zeroes pruned instances:

```gams
y.fx(c,h)$(not ((ord(c) <= card(c) - 2) and (ord(h) <= card(h) - 1))) = 0;
```

`card(h) = 51`, so `h50` has `ord(h) = 51` and the guard fires on **exactly the cells those equations constrain**. Runtime probe (`display y.lo, y.up` immediately before the solve):

```
y.lo(y2,h50) = y.up(y2,h50) = 0      while y_fx_y2_h50 demands 5
y.lo(y3,h50) = y.up(y3,h50) = 0      while y_fx_y3_h50 demands 45
```

**The value is consistent when written and contradicted when pruned.**

---

## Phase 0: Acceptance Gate

### Hand-Derived KKT Shape

`lnts` fixes boundary conditions at the final interval: `y.fx('y2','h%nh%') = 5`, `y.fx('y3','h%nh%') = 45`, `y.fx('y4','h%nh%') = 0`, plus `y.fx(c,'h0') = 0`. These are **real constraints of the model**, not incidental initialisation.

In the MCP, a variable fixed at a labelled element may be represented **either** as a bound (`y.fx = v`, eliminating the column) **or** as an explicit equation paired with a multiplier (`y_fx_… .. y(…) − v =E= 0`). Both are sound; what is unsound is **applying both to the same cell with different values**.

Separately, instances outside the active domain must be pinned so they do not float. The correct shape is therefore:

> The blanket pruning guard must apply **only to cells that are not already constrained by an explicit `_fx_` equation**. Where a cell carries such an equation, that equation is authoritative and the blanket zeroing must **skip** it.

**The two available resolutions are NOT equivalent, and choosing wrongly is silent:**

| resolution | correct when |
|---|---|
| suppress the `_fx_` equation, keep the blanket `.fx` | the fixed value **equals** the blanket value (0) |
| **skip the cell in the blanket guard, keep the equation** | **general — and required whenever the fixed value is nonzero** |

`lnts`'s values are **5 and 45**, so only the second is correct here. Suppressing the equations would drive the model to a *different, silently wrong* solution rather than an infeasible one — strictly worse than the current abort.

### Expected Emit Pattern

```gams
y_fx_y2_h50.. y("y2","h50") - 5  =E= 0;          * retained, authoritative
y_fx_y3_h50.. y("y3","h50") - 45 =E= 0;          * retained, authoritative

* the blanket guard must exclude cells carrying a _fx_ equation:
y.fx(c,h)$(not ((ord(c) <= card(c) - 2) and (ord(h) <= card(h) - 1))
            and not (sameas(c,'y2') and sameas(h,'h50'))
            and not (sameas(c,'y3') and sameas(h,'h50'))
            and not (sameas(c,'y4') and sameas(h,'h50'))) = 0;
```

(The exact exclusion form is an implementation choice; the **invariant** is that no cell is simultaneously blanket-zeroed and constrained by a `_fx_` equation.)

**Traced fix-surface (Day-3, `2723c22a`):**

- **The blanket emission** — `src/emit/emit_gams.py` ~`3012`, `fx_lines.append(f"{var_name}.fx({domain_str})$(not ({combined})) = {fix_val};")`, with `fix_val = 0` because `y` is free (no `fx`/`lo`/`up`). The sibling site at ~`2952` has the same shape.
- **The existing conflict-resolution function** — `_compute_suppressed_fx_equations` (~`874`). Its docstring describes **exactly this conflict**. **It does not fire here:** it detects only *membership-style* conditions via `_collect_position_memberships` (`position_members` / `tuple_constraints`), whereas `lnts`'s pruning condition is an **ordinal/cardinality** predicate (`ord`/`card`), so `constraints.is_empty()` short-circuits it.

So the mechanism exists and its **detection is too narrow** — but note its resolution (suppress the equation) is the wrong branch for a nonzero fix. **⚠ Traced hypothesis, not a result; confirm before implementing.**

### Verification Methodology

Run from a **scratch directory**.

1. **Fail-before** (`2723c22a`): `gams lnts_mcp.gms lo=0 errmsg=1` → `rc=0` (it compiles), `**** MODEL STATUS 4 Infeasible`, `ITERATION COUNT 0`.
2. **The decisive check is a RUNTIME BOUND PROBE, not a source read.** Insert `display "PROBE", y.lo, y.up;` immediately before `Solve mcp_model using MCP;` — **before the SOLVE statement, not before the `* Solve Statement` comment header**, which splits a comment block and yields `$140`/`$241`/`$257` errors that look like a real finding. Fail-before shows `y.lo = y.up = 0` at `(y2,h50)` and `(y3,h50)`; pass-after must show those cells **unfixed by the blanket guard**, with the `_fx_` equations still present and paired.
3. **Pass-after:** PATH iterates (`ITERATION COUNT > 0`) and returns any `modelstat` other than 4-at-zero-iterations. **A different infeasibility is still progress** — it means the contradiction is gone and the remaining behaviour is the model's own.
4. **Correctness, not just termination:** the retained `_fx_` equations must still bind — assert `y.l('y2','h50') = 5` and `y.l('y3','h50') = 45` in any solution reported.
5. **Leak gate:** only `lnts` drifts. **State the in-scope count** (185 after P4's Day-8 adoption, not 163). Determinism ×3.

### PROCEED/REPLAN Signal

**PROCEED** — the probe shows the cells no longer blanket-zeroed, the `_fx_` equations remain and bind at 5 / 45, PATH iterates, and nothing outside `lnts` drifts.

**REPLAN** — the narrowing perturbs any of the **five other models that match the source pattern but are not defective** (see below), or the exclusion cannot be expressed without enumerating labels per model. **If it requires per-model enumeration, bank it** — a label-enumerated guard is not a general fix.

### ⚠ The source pattern is a FALSE POSITIVE in 5 of 6 cases

Scanning for the co-occurrence — a variable carrying **both** a `_fx_` equation and a blanket pruned zeroing — matches **six models**:

| model | outcome | verdict |
|---|---|---|
| **lnts** | `model_infeasible` | ✅ the true positive |
| catmix | `model_optimal_presolve` | ❌ false positive |
| otpop | `model_optimal` | ❌ false positive |
| springchain | `model_optimal` | ❌ false positive |
| ganges / gangesx | `path_syntax_error` | ❌ false positive |

**Tightening to "the `_fx_` equation has a nonzero RHS" does NOT help** — catmix (1), otpop (29.4) and springchain (2) all still match. **The discriminator is whether the pruning guard actually covers the fixed tuple**, which is a runtime property of `ord`/`card` against the model's own set sizes and **cannot be read off the source**.

**Negative control (must be kept in any regression suite):** `otpop`'s `x.lo` is unset at `1974` with `x.up = 32.250` — never zeroed — and the model solves **MS-1 Optimal**. Any fix that perturbs otpop is over-firing.

### Bucket / KPI

**0 bucket expected.** `lnts` is `model_infeasible`; the NLP reference is **MS-2 @ 0.5547**. Removing the contradiction lets PATH actually iterate — it does **not** imply the MCP then solves or matches. **Translate-stable, Solve-uncertain, Match-unclaimed.**

### Regression guard

A minimal synthetic fixture: a variable with a labelled nonzero `.fx` at a boundary element, plus an active-domain pruning condition that covers that element. Assert the emitted model does **not** contain both a `_fx_` equation and a blanket `.fx` for the same cell. **Include `otpop` as the negative control** — the fixture is only meaningful if it also demonstrates non-firing on a matching-but-sound model.

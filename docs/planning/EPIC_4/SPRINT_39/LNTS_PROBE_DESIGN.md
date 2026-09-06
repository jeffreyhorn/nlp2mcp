# lnts Runtime Bound Probe — Design

**Sprint 39 Prep Task 5 (P3)** · **Authored:** 2026-08-31 · **Measured at:** `4bbe7c3c`
**Status of the hypothesis at authoring time:** banked since Sprint 38, **never tested**.

> **The criteria in §4 were written and committed BEFORE the probe was run.** That ordering is the point of this document. A source read can show that two mechanisms *exist*; only a runtime observation shows that they *collide*. Sprint 38's §4.1 requires runtime observation for a runtime property, and this hypothesis has survived a sprint on a source read alone.

---

## 1. The hypothesis, as banked

Two `.fx` mechanisms act on the same cells:

- **Mechanism A — the `_fx_` equations.** The correct one: `y_fx_y2_h50.. y("y2","h50") - 5 =E= 0;`
- **Mechanism B — a blanket pruned-instance zeroing** that fires on those same cells, giving `y.lo = y.up = 0`.

Against equations demanding **5** and **45**, that is infeasible before any iteration — hence **MS-4 at iteration 0**.

## 2. What the source shows (necessary, not sufficient)

Both mechanisms are present in `data/gamslib/mcp/lnts_mcp.gms`:

```gams
140  y_fx_y1_h0..   y("y1","h0")  - 0  =E= 0;      ...
144  y_fx_y2_h50..  y("y2","h50") - 5  =E= 0;      ← demands 5
145  y_fx_y3_h50..  y("y3","h50") - 45 =E= 0;      ← demands 45
146  y_fx_y4_h50..  y("y4","h50") - 0  =E= 0;

160  y.fx(c,h)$(not ((ord(c) <= card(c) - 2) and (ord(h) <= card(h) - 1))) = 0;
```

Sets: `c` = {y1, y2, y3, y4} (**card 4**) · `h` = h0…h`%nh%`, so `h50` is the **last** element.

**This is still only a source read.** It does not establish that GAMS computes the bound the way the expression appears to say, that mechanism B is not overridden later, or that the `_fx_` equation is not itself dropped. §4 settles that.

## 3. The probe

Inject, into a **copy** of the golden, immediately before `Solve` and after all fixing:

```gams
display y.lo, y.up;
```

Run from a scratch directory, then read the **displayed effective bounds** — not the source text — for the four tuples that carry a `_fx_` equation at `h50`.

**Why `display` and not the equation listing:** it reports the bound GAMS actually holds at solve time, after every assignment has executed in order. The listing's bound columns would do as a cross-check, but `display` is the direct observation of the quantity in dispute.

## 4. Confirm / refute criteria — **fixed in advance**

Let `D(c,h)` be the value demanded by that tuple's `_fx_` equation, and `[lo, up]` the displayed effective bounds.

### CONFIRM the two-mechanism collision — **all three must hold**

| # | criterion |
|---|---|
| C1 | For **at least one** tuple with `D ≠ 0` — i.e. `("y2","h50") → 5` or `("y3","h50") → 45` — the effective bounds are **`lo = up = 0`**. |
| C2 | That contradiction is **exactly** `lo = up = 0 ≠ D`, i.e. the bound is *zero*, not merely different. A non-zero disagreement would mean some third mechanism, not the blanket zeroing. |
| C3 | The **negative-control tuple** `("y4","h50")`, whose `D = 0`, shows `lo = up = 0` and is therefore **consistent** — the same blanket fires there, harmlessly. This distinguishes "the blanket is wrong" from "the blanket is wrong *where D ≠ 0*". |

### REFUTE — **any one is sufficient**

| # | criterion |
|---|---|
| R1 | Every `_fx_`-carrying tuple shows bounds consistent with its `D` (e.g. `("y2","h50")` shows `lo = up = 5`). The blanket does not reach these cells, and MS-4 has another cause. |
| R2 | The contradicted tuples show a **non-zero** bound different from `D`. Mechanism B is not the blanket zeroing; find the real writer. |
| R3 | No tuple is contradicted, yet MS-4 at iteration 0 still reproduces. The infeasibility is elsewhere entirely — bounds are not the mechanism. |

### REPLAN exit

**If any refute criterion fires, the banked hypothesis is refuted.** Bank the real mechanism and **do not widen the track**: the named fix (`fix_rhs = "0"` fallback, "same shape as the Sprint-33 P6 fix") would then be addressing a mechanism that does not exist here, and P3 returns to diagnosis rather than proceeding to implementation.

## 5. Negative controls

- **Internal:** `("y4","h50")` — carries a `_fx_` equation demanding **0**, and the blanket also fixes it to 0. Consistent, so it must *not* be reported as a collision. If the probe flags it, the probe is over-reporting.
- **External:** **`cesam` must not be batched with lnts.** It shows the same MS-4-at-iteration-0 *signature* but has **0 `_fx_` equations**, so this mechanism cannot apply to it. Sprint 38 checked rather than assumed. **A shared signature is not a shared mechanism.**

## 6. What this probe does *not* establish

It tests the **runtime collision**, nothing else. It does not identify the *layer* that emits the blanket, does not show that the named `fix_rhs = "0"` fallback is reached, and does not license the banked fix. Those are separate steps — see Unknown 3.2, where the fallback is instrumented rather than inferred.

---

## 7. RESULT — executed Sprint 39 Day 4, 2026-09-07 (measured at `6fa78b12`, GAMS 54.2.1)

### ✅ CONFIRMED — all three criteria hold; no refute criterion fires

Probe: `display y.lo, y.up` plus eight scalars, injected into a **copy** in a scratch dir immediately before `Solve`, after all fixing.

| tuple | `_fx_` demands `D` | effective `lo` | effective `up` | criterion |
|---|---|---|---|---|
| `y("y2","h50")` | **5** | **0** | **0** | **C1 ✓ · C2 ✓** — contradicted, and the bound is *exactly zero* |
| `y("y3","h50")` | **45** | **0** | **0** | **C1 ✓ · C2 ✓** |
| `y("y4","h50")` | 0 | 0 | 0 | **C3 ✓** — consistent; the blanket fires harmlessly, so the probe is not over-reporting |
| `y("y1","h50")` | *(no `_fx_` at h50)* | 0 | 0 | outside the criteria |

`MODEL STATUS 4 Infeasible`, **ITERATION COUNT 0** — the signature reproduces.

**R1 ✗** (bounds are *not* consistent with `D`) · **R2 ✗** (the bound is zero, not a different non-zero) · **R3 ✗** (tuples *are* contradicted). **The banked hypothesis survives its first runtime test.**

### The emitting layer — traced, not read

| site | fires for `y`? | emits |
|---|---|---|
| `emit_gams.py:3061` — the **banked** `fix_rhs = "0"` fallback | **NO — never** | — |
| `emit_gams.py:3005` (section 1a) | yes | the big-OR line (golden 156) |
| **`emit_gams.py:3121` (section 1b)** | **yes** | **the killing blanket** (golden 160) |

**Prep is vindicated on both counts.** ⚠ An intermediate run of mine attributed the append to line 3091; that was **my tracer's bug** — it recorded list growth at the line where it was *observed* (the loop header) rather than the line that executed the append. Corrected by attributing to the previously-executed line in the same frame. I nearly reported prep as wrong on the strength of it.

### Root cause — two DIFFERENT conditions, and only one is consulted

`_compute_suppressed_fx_equations` (`:874`) already resolves this class of conflict, by **suppressing** the `_fx_` equation when the blanket would contradict it. It decides membership against **`kkt.stationarity_conditions`**.

The section-1b blanket at `:3121` fires on a **different** condition — `infer_lead_lag_condition`, cached in `_eq_cache` at `:3080`.

**So a cell can be *inside* the stationarity condition — its `_fx_` equation survives — while being *outside* the lead/lag condition, so the blanket zeroes it anyway.** lnts's `h50` cells are exactly that gap: `y_fx_y2_h50` and `y_fx_y3_h50` are emitted (golden 144–145) *and* zeroed (golden 160).

This is more specific than "the blanket is wrong", and it rules out one tempting fix: **extending the suppression to the lead/lag condition would DROP the `_fx_` equations demanding 5 and 45**, which are real boundary conditions from the source. That changes the model's meaning and must not be done.

### Fix design for Day 5

At `:3121`, the blanket must **not** zero a cell that carries a surviving (non-suppressed) `_fx_` equation — the explicit fix is authoritative; the blanket is cleanup for genuinely pruned instances. Machinery to reuse: `_fx_eq_name()` (`:711`) and the `suppressed` set (`:920`).

⚠ **Add a positive exclusion; do not widen the lead/lag condition.** Section 1b serves the whole corpus, and the Day-2 leak showed what a loosened predicate costs here (10 goldens against a zero-drift baseline).

⚠ **`cesam` remains out of scope** — same MS-4-at-iteration-0 signature, **0 `_fx_` equations**, so this mechanism cannot apply. Not batched.

---

**Document Status:** ✅ Design complete and **EXECUTED** — criteria fixed before execution (Prep Task 5); result CONFIRMED (Sprint 39 Day 4).
**Last Updated:** 2026-09-07 — probe executed, hypothesis confirmed, layer traced

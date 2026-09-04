# dyncge: phantom `nu_eqXp(j±k)` IndexOffset terms in `stat_pf` — the first SILENT instance of the #1381 family

**GitHub Issue:** [#1714](https://github.com/jeffreyhorn/nlp2mcp/issues/1714)
**Status:** OPEN — diagnosed Sprint 39 Prep Task 4, 2026-08-30
**Severity:** High — the model compiles, solves to `MODEL STATUS 1`, and is **silently wrong by 29.3 %**
**Affected Models:** dyncge (confirmed). Root-cause family: camcge (#1354), cesam2 (#1355), consolidated in **#1381**
**Measured at:** `37665091`, GAMS **54.2.1** / PATH **5.2.01**
**Layer:** **KKT / stationarity** — `src/kkt/stationarity.py`. ⚠ **REFINED by trace on Day 1 (2026-09-04): the named ~7107–7131 path is the SYMPTOM site, not the birth site.** It does execute (91 hits), but it only decorates offsets that already exist. The offsets are *born* upstream at **~6290–6455**, where the Pattern-C recogniser cascade fails to claim `(eqXp, pf)` and `allow_nonzero_offsets` stays `True`. Evidence: `docs/planning/EPIC_4/SPRINT_39/artifacts/trace_dyncge_layer.py`. See **Day-1 layer confirmation** below.

**Cross-references:**
- **#1381** — Pattern C Phase B: plain-alias + dim-mismatch consolidation (**the fix probably belongs here**)
- #1354 camcge / #1355 cesam2 — the same root cause, discovered via PATH `$141`
- #1081 — the dimension-mismatch lead/lag path whose guard this misapplies
- #1693 — the empty-pair abort that **masked** this defect; closes cleanly on its own terms (not widened)

---

## Problem Summary

Fixing #1693's `eqpf2` empty-pair abort revealed a second, independent defect it had been masking. `stat_pf(h,j)` carries **manufactured index-offset terms** — `nu_eqXp(j±1..3)` and `nu_eqII(j±1..3)`, each gated on `$(ord(h) = k)` — where the correct emit is a plain sum over the equation's free index.

Unlike every previously known instance of this family, **dyncge does not fail loudly**: the guards keep the phantom references in range, so GAMS compiles it, PATH solves it to optimality, and the answer is simply wrong.

---

## Phase 0: Acceptance Gate

### Hand-Derived KKT Shape

Derived from `data/gamslib/raw/dyncge.gms` **before** reading any emitter output.

Sets: `i(u)` = goods {AGR, LMN, HMN, SRV} (**4**) · `h(u)` = factor {CAP, LAB} (**2**) · `Alias (i,j), (h,k)`.

`pf` appears in exactly five equations (verified exhaustively over all 29 equation definitions):

| equation | ∂/∂pf(H,J) | shape |
|---|---|---|
| `eqF(h,j)..  F(h,j) =e= beta(h,j)*py(j)*Y(j)/pf(h,j)` | `+beta(H,J)·py(J)·Y(J)/pf(H,J)²` | diagonal, (h,j)=(H,J) |
| `eqSp..  Sp =e= ssp*(sum((h,j), pf*F) - Td)` | `−ssp·F(H,J)` | scalar eq; inner sum collapses |
| `eqXp(i)..  Xp(i) =e= alpha(i)*(sum((h,j), pf*F) - Sp - Td)/pq(i)` | `−alpha(i)·F(H,J)/pq(i)` | **free eq index i ⇒ `sum(i, …)`** |
| `eqpf2(h_mob,i,j)..  pf(h_mob,j) =e= pf(h_mob,i)` | `+1` / `−1` | the #1693 diagonal case |
| `eqII(j)..  pk*II(j) =e= pf('CAP',j)^ζ·F('CAP',j)/Σᵢ[pf('CAP',i)^ζ·F('CAP',i)]·(Sp+ε·Sf)` | quotient rule | **CAP only**; pf in numerator *and* denominator sum |

**The operative line.** `eqXp`'s index `i` is **free and unrelated to the head's `(h,j)`**. Differentiating the inner `sum((h,j), …)` collapses it to the head instance, leaving `i` to be summed:

```
stat_pf(h,j)  ⊃  sum(i, ((-1) * alpha(i) * f(h,j) / pq(i)) * nu_eqXp(i))
```

There is **no lead/lag anywhere in dyncge's source** — no `i+1`, no `j-1`. Any offset in `stat_pf` is manufactured.

`stat_pq(i)` was hand-derived the same way as a control: seven pq-bearing equations (`eqpzs`, `eqTd`, `eqXv`, `eqXp`, `eqM`, `eqD`, `eqPRICE`), each verified term-by-term against the emit **including the `eqM`/`eqD` chain rules**, where the emitted tail `/A · B·C/B²` reduces exactly to `1/pq`. **`stat_pq` is correct.**

### Expected Emit Pattern

**Correct** — one plain sum, no offsets, no `ord()` guards:

```gams
stat_pf(h,j).. ... + sum(i, ((-1) * alpha(i) * f(h,j) / pq(i)) * nu_eqXp(i)) + ... =E= 0;
```

**Emitted today** — the diagonal plus a fan of manufactured offsets:

```gams
((-1) * (pq(j) * alpha(j) * f(h,j) / sqr(pq(j)))) * nu_eqXp(j)
+ (((… pq(j+1) … ) * nu_eqXp(j+1))$(ord(j) <= card(j) - 1))$(ord(h) = 1)$(sameas(j,'AGR') or …)
+ (((… pq(j+2) … ) * nu_eqXp(j+2))$(ord(j) <= card(j) - 2))$(ord(h) = 2)$(…)
+ (((… pq(j+3) … ) * nu_eqXp(j+3))$(ord(j) <= card(j) - 3))$(ord(h) = 3)$(…)
+ … and the matching j-1, j-2, j-3 terms
```

**Why this is wrong, precisely.** The offsets are selected by `ord(h)` — the **factor** index — for a sum that ranges over `i`, the **goods** index. `h` has 2 members, so:

- `ord(h)=1` (CAP) → fires `j±1` only
- `ord(h)=2` (LAB) → fires `j±2` only
- `ord(h)=3` → **dead terms; can never fire**

So each row keeps a different, wrong subset of the four `nu_eqXp` multipliers, and no row sums all four. `eqII` is corrupted identically (CAP rows only), which is why CAP rows carry the largest residual while LAB rows are also wrong.

**Fix surface (hypothesis, not a result).** ⚠ **TRACED ON DAY 1 — this hypothesis was HALF right; see the Day-1 section below before implementing here.** The branch does execute, but fixing it would suppress the *guard*, not the offsets. `src/kkt/stationarity.py` ~7107–7131, the `is_dim_mismatch and has_real_offset` branch added for #1081. Its comment describes a genuine lead/lag (`bal4(t) → x(t,l)`, "offset k applies when `ord(l) = k`"). dyncge reaches it because `Alias (i,j)` makes `i` and `j` share a set root, so a free equation index is mistaken for a shifted head index. **The `ord()` guard is a symptom; the offsets should never have been created.** ⚠ Confirm before implementing — Sprint 38 saw three of four gates name the wrong layer.

### Verification Methodology

1. **Fail-before.** `scripts/diagnostics/kkt_residual.py data/gamslib/raw/dyncge.gms` → `CASE_B`, max rel **6.22e-02** at `stat_pf(CAP,SRV)`; top rows `stat_pf(CAP,SRV)` · `stat_pq(HMN)` · `stat_pf(LAB,SRV)` · `stat_pf(LAB,HMN)` · `stat_pf(CAP,LMN)`.
2. **Structural fail-before.** `stat_pf` contains ≥ 1 `nu_eqXp(j±k)` or `nu_eqII(j±k)` reference and ≥ 1 `$(ord(h) = …)` guard. Assert both go to **zero**.
3. **Pass-after.** `stat_pf` contains `sum(i, … nu_eqXp(i))`; the residual reaches **`CASE_A`**. *A non-erroring emit is not a pass.*
4. **Negative control.** `stat_pq` is already correct and **must not change** — byte-identical before and after.
5. **Leak gate.** `make check-goldens` — expect drift on **dyncge only**; `--expect-drift dyncge` must pass unqualified. The shared dim-mismatch path is high-blast-radius, so an unexpected drift is a leak, not a bonus.
6. **Determinism.** ≥ 3 `PYTHONHASHSEED` values, byte-identical emits.
7. **Objective.** Cold MCP currently **MS-1 @ 381401.119** vs NLP **539570.5027**. Target: match within tolerance — *assert `modelstat` before reading any objective*.

### PROCEED/REPLAN Signal

**PROCEED** if the residual reaches `CASE_A` and `stat_pq` is unchanged and the leak gate drifts dyncge alone.

**REPLAN** if any of:
- the residual persists as **`CASE_C_OBJDEF`** after the offsets are corrected — dyncge would then be a non-convexity case like elec, and the honest target becomes a *documented divergence* with `modelstat` asserted, **not** a Match. ⚠ elec's verdict changed from `CASE_B` to `CASE_C_OBJDEF` as the classifier improved; treat this as live, not remote.
- the fix drifts any model other than dyncge — hand back to **#1381** as Pattern C Phase B rather than patching here.
- correcting `stat_pf` leaves `stat_pq(HMN)`'s residual in place, which would indicate a second, independent defect (see *Open question* below).

---

## ⚠ Why this instance matters beyond dyncge

Every previously known member of this family was found because it produced a **PATH `$141` compile failure** on a phantom `nu_X(i±N)` reference — that is how #1354 and #1355 were discovered.

**dyncge is the first known SILENT instance.** Its guards keep every phantom reference in range, so the emit compiles, solves to `MS-1`, and is wrong by 29.3 % with no diagnostic of any kind.

**Consequence for #1381:** its "at minimum 13 affected models" is a census of models that failed *loudly*. Silent instances are invisible to that method, so the family's blast radius is plausibly larger than recorded. A search for the *structural* signature — `nu_X(idx±k)` paired with an `ord(…) = k` guard in a stationarity row — would be a cheap way to find them, and is recommended as follow-up work.

---

## Day-1 layer confirmation (Sprint 39, 2026-09-04) — traced, not read

Reproduced first, at `8aae26f4` / GAMS 54.2.1: residual **`CASE_B`**, max rel **6.22e-02** at `stat_pf(CAP,SRV)`, and the same five top rows in the same order as recorded at `37665091`. Structural fail-before also reproduces: **6** `nu_eqXp(j±k)` + **6** `nu_eqII(j±k)` refs, **12** `$(ord(h) = k)` guards, offsets **±1..±3**, `ord(h)` values **{1,2,3}** while `h` has **2** members, and **0** occurrences of the correct `nu_eqXp(i)`.

**Method.** `docs/planning/EPIC_4/SPRINT_39/artifacts/trace_dyncge_layer.py` runs the real emit under a line tracer over `stationarity.py` and wraps the recogniser cascade. No conclusion below is read off the source.

**Result — the named layer is real but downstream.**

| site | executes for dyncge? |
|---|---|
| `allow_nonzero_offsets = True` (default) | **HIT** — 63 |
| Pattern-C claims the pair ⇒ offsets suppressed | **MISS — 0** |
| `offset_key` zeroed by suppression | **MISS — 0** |
| `is_dim_mismatch and has_real_offset` *(the named surface)* | **HIT** — 91 |
| `ord()` guard constructed *(~7124–7132)* | **HIT** — 216 |

So ~7107–7131 **is** on the path — but it decorates offsets that already exist. **The suppression that should prevent them never fires once.**

**Why it never fires.** The cascade is four recognisers, and *all four* miss `pf` (0 claimed, 56 calls). Two of them do claim elsewhere in dyncge (B-1 once, B-3 twice), so the machinery works — it simply does not recognise this shape:

| recogniser | claimed / missed (all vars) | `pf` |
|---|---|---|
| `_find_pattern_c_alias_sum` (launch-shape) | 0 / 791 | 0 / 44 |
| `_find_plain_alias_pattern_c` (B-1) | 1 / 62 | 0 / 4 |
| `_find_b2_pattern_c` (B-2) | 0 / 62 | 0 / 4 |
| `_find_dim_mismatch_pattern_c` (B-3) | 2 / 60 | 0 / 4 |

**The consequence, measured directly.** Of the **168** offset keys produced for 2-D variables, **72 carry a non-zero real offset**, every one of shape `('UNMATCHED', ±k)` with k ∈ {1,2,3} — the first coordinate (`h`) unmatched, the second (`j`) shifted. That is exactly the emitted `nu_eqXp(j±1..3)` fan, and the multiplicities **18/18/12/12/6/6** are the 3:2:1 boundary-valid counts over a 4-element set. **Nothing zeroes them** — the suppression line is a MISS above. This is independent corroboration: the recogniser misses and the manufactured offsets are two separately observed facts, not one inferred from the other.

**The structural reason, and it is a single shared gate.** B-1, B-2 and B-3 each require a **single-index** `Sum` — `len(expr.index_sets) == 1` at lines **604**, **743** and **949** — and the launch-shape gate requires a `$` condition dyncge has none of. dyncge's operative term is

```gams
eqXp(i)..  Xp(i) =e= alpha(i)*(sum((h,j), pf(h,j)*F(h,j)) - Sp - Td)/pq(i);
```

a **two-index `Sum` binding BOTH of `pf`'s coordinates, with the equation's own index `i` free and unrelated to either.** B-3's *dimension* gate (`0 < len(eq_domain) < len(var_domain)`) actually passes (1 < 2) — the miss is the arity of the `Sum`, not the dimension mismatch. B-1's set gate passes too (`common = {i}`, since `Alias(i,j)` shares a root).

**Checked before proposing new logic** (the S38-D12 rule, and P8's 8b): **no existing member covers this population.** The nearest, B-3, handles a higher-dimensional variable whose *equation index binds one coordinate* while the sum binds the other (cesam2's `COLSUM(jj).. sum(ii, TSAM(ii,jj))`). Here the equation index binds **neither**; the sum collapses the variable entirely. That is a distinct Pattern-C member, not a widening of B-3.

**Consequence for the plan.** This lands where `ISSUE_1714` already pointed — *"the `ord()` guard is a symptom; the offsets should never have been created"* and *"#1381 — the fix probably belongs here."* The trace promotes both from hypothesis to measurement. It also means the REPLAN exit *"hand back to #1381 as Pattern C Phase B rather than patching here"* is the **expected** route, not the fallback.

⚠ **`eqSp` carries the identical `sum((h,j), pf(h,j)*F(h,j))` term** (line 420), so any recogniser added for `eqXp` will see `eqSp` too. `eqSp` is scalar-domain, so it takes a different branch — **this must be verified, not assumed**, before implementing.

---

## Open question (deliberately not closed here)

`stat_pq(HMN)` carries the **second-largest** residual (5.90e-02), yet `stat_pq` was verified correct term-by-term. Its residual is therefore **not explained by a defect in its own row** — most plausibly it *surfaces* there through multipliers shared with the corrupted `stat_pf` rows (`nu_eqXp` appears in both). **This has not been proven**, and the PROCEED/REPLAN signal above treats a surviving `stat_pq` residual as evidence of a second defect.

---

**Document Status:** ✅ Phase-0 gate authored — Sprint 39 Prep Task 4
**Last Updated:** 2026-08-30

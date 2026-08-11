# Sprint 37 Day 1 — P1 markov `σ=sp` Discriminator Control (PR24/PR27, `/tmp`-only)

**Date:** 2026-08-11 · **Branch:** `planning/sprint37-day1-markov-control` · **Scope:** control-only — a scratch `src/kkt/stationarity.py` patch was implemented for measurement and **REVERTED**; the file is **byte-identical to the anchor `78ceaead`** and the DB is untouched.

**Verdict: ✅ PROCEED to Day 2.** All four Phase-0 criteria in `ISSUE_1110` are satisfied on the control — and **the one that blocked Sprint 36 is the one that passed most decisively**: `make leak-check MODEL=markov` returned the **unqualified `LEAK GATE PASS`** over all 163 in-scope goldens. Day 1 also closed the honest limitation Task 4 recorded: **zero unverified models remain** (4 timeouts → 0), including **`ferts`**, the third S36 leak.

---

## 1. What was built

Mechanism C as a **gated, additive early-out** in `_add_indexed_jacobian_terms`, mirroring the existing `_try_build_param_offset_crossterm` precedent (`src/kkt/stationarity.py:5933–5938` on `main` at `32322ee1` — the call at `:5933`, the `if … is not None: expr = Binary("+", …); continue` early-out at `:5936–5938`): when the conjoined discriminator fires for a `(constraint, variable)` pair, the two hand-derived terms are appended and the pair `continue`s — bypassing the offset-group machinery entirely. Every non-firing pair takes the untouched path.

**`_compute_index_offset_key` was NOT touched.** That shared matcher is the whole cohort-leak surface, and leaving it alone is Mechanism C's premise (Task 4 §4).

Three helpers, matching the Task-4 design one-for-one:

| helper | conjunct |
|---|---|
| `_sigma_sp_domain_collision` | **(1)** a multiplier-domain index whose alias-canon matches ≥2 variable positions, a later position an exact declared-name match and an earlier one canon-only |
| `_sigma_sp_value_param_refs` | value-branch walk — never a `$`-condition, never a `Sum`/`Prod` condition (this is what excludes `sroute`'s `1$(darc(ip,ipp))` structurally) |
| `_sigma_sp_param_couples` | **(2)** a value-branch `ParamRef` carrying an equation-index value and the variable's collision-position value at **two distinct positions** of its own tuple |

## 2. Two runtime facts traced, not assumed (PR24)

The prep design named `constr('sp','j')`, but the source *declares* `constr(s,i)` and *defines* `constr(sp,j)..`. Which one reaches the emitter decides whether conjunct 1 fires at all, so it was measured:

```
eqdef.domain                     : ('sp', 'j')
_get_constraint_domain('constr') : ('sp', 'j')     <- the DEFINITION domain
var z domain                     : ('s', 'i', 'sp')
(constr,z) nonzero entries       : 2048
distinct offset_key groups       : 45              <- the blow-up, reproduced
```

⇒ conjunct 1 resolves to `(mult_pos=0, var_pos=2)`, as designed.

**A second fact the design did not anticipate.** Re-symbolising the representative derivative (concrete elements → domain symbols) is **ambiguous** on most markov entries: `var=('12','normal','12')` has the same element at positions 0 and 2, so `'12'` maps to both `s` and `sp`. The control therefore **rejects any candidate entry whose mapped elements are not pairwise distinct** and takes the first unambiguous one on the `σ=sp` slice. Without that filter the emitted parameter indices are silently wrong in a way that still compiles. This belongs in the Day-2 landing.

## 3. Correctness — `CASE_A` reached

| measurement | baseline | control |
|---|---|---|
| `kkt_residual.py markov` | `CASE_B` — emit_bug | **`CASE_A` — healthy (KKT correct, PATH converges)** |
| max stationarity row | `stat_z(empty,disrupted,empty)` rel **1.33e+01** | `stat_z(6,normal,empty)` rel **2.84e-16** |
| dual transfer | CONSISTENT | CONSISTENT (comp infeas 0.00e+00, equality resid 5.97e-16) |

**2.84e-16 is the banked S36 Day-2 figure (2.8e-16) reproduced** — from a re-implementation, since that prototype was never committed.

### The emit collapse

```
golden   stat_z(s,i,sp).. c(s,sp,i) + sum((s__kkt1,j), ((1 - b*pi(s,i,s,i,s__kkt1)) * nu_constr(s,i))$(…))
                        + …44 more s__kktN groups…
control  stat_z(s,i,sp).. c(s,sp,i) + nu_constr(s,i)$(sp(s) and j(i))
                        + sum(j, (((-1) * (b * pi(s,i,sp,j,sp))) * nu_constr(sp,j))$(sp(sp) and j(j)))
                        + [equil term, unchanged] - piL_z(s,i,sp)
```

| measurement | golden | control |
|---|---|---|
| `stat_z` characters | 14,695 | **3,967** |
| distinct `s__kktN` groups | **45** | **0** |

The Kronecker `1` is no longer fused into the off-diagonal coefficient, and the diagonal multiplier `nu_constr(s,i)` is a bare additive term rather than being summed over indices it does not depend on — exactly the `ISSUE_1110` *Expected Emit Pattern*.

## 4. Bucket / KPI — cold solve, `modelstat` asserted

```
**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal
---- VAR pvcost   -INF   2401.5774   +INF   .
```

**Cold** (no `--nlp-presolve`), against the NLP reference **2401.5773** ⇒ relative difference **4e-8**, far inside the 2e-3 tolerance ⇒ **match**.

That is the methodology→genuine transition demonstrated end-to-end: **genuine floor 75 → 76**, with **Match unchanged at 93** (a partition transfer — presolve-match 30→29, cold-optimal 63→64). Reporting this as "+1 Match" would double-count.

## 5. Leak-freedom — the gate that blocked Sprint 36, PASSED

Run against the patched tree (this is Day 2's gate, executed a day early because the control was in hand):

```
Golden staleness: checked 163 in-scope golden(s) (7 allowlisted, 6 workers).
    EXPECTED DRIFT: markov_mcp.gms (-11619 bytes)
  LEAK GATE PASS: exactly the expected model(s) drifted (markov);
                  all other in-scope goldens byte-identical.
```

**The unqualified form** — not `PARTIAL` (which would mean the sweep was narrowed), no `LEAK:` line, no `NO-OP:` line. All three Sprint-36 leak models — **`cesam`, `ferts`, `sroute`** — are byte-identical, as are the six 2-D cohort models and the 18 goldens CI was silently skipping until the `--min-scope` fix.

This is a **byte-diff of real emitted output**, which is strictly stronger evidence than the predicate scan below.

## 6. Corpus scan — and Task 4's unverified tail is now closed

| gate | Task 4 (design time) | **Day 1 (420 s timeout)** |
|---|---|---|
| conjoined `(1)∧(2)` fires on | `['markov']` | **`['markov']`** — unchanged |
| domain gate reached | 14 models | **15** — `+ferts` |
| **unverified (timeout)** | **4** — `clearlak, dinam, ferts, tabora` | **0** |
| errors | 0 | 0 |

Task 4 raised its own limitation honestly: *"`ferts` (the third S36 leak) timed out and is therefore unverified at design time."* Raising the per-model timeout from 120 s to 420 s resolves all four, and **`ferts` is measured as domain-gate-only — correctly excluded by the derivative conjunct.** The 15 models reaching the domain gate (S36's signature) versus exactly 1 surviving the conjunction is the quantified statement of what the derivative conjunct buys.

Wall: 1,885 s over 142 models. The 6 pathologically-slow models (`sarf, ganges, gangesx, turkpow, egypt, indus`) remain skipped — but they are covered by §5's leak gate, which sweeps goldens rather than running the predicate.

## 7. Phase-0 status (`ISSUE_1110`)

| criterion | required | measured | status |
|---|---|---|---|
| Correctness | `CASE_A`, rel < 1e-3 | `CASE_A`, **2.84e-16** | ✅ |
| Bucket / KPI | cold `MODEL STATUS 1`, `pvcost` 2401.577, match | **1 Optimal, 2401.5774, match** | ✅ |
| Leak-freedom | unqualified `LEAK GATE PASS` | **PASS**, 163 goldens, markov only | ✅ |
| Regression guard | fixture fail-before/pass-after | spec ready (corpus-free, Task 10 §1.1) — **lands Day 3** | ⏳ |

**PROCEED signal: GO.** The REPLAN exit (*the predicate fires on any model besides markov, or the cold solve misses `MODEL STATUS 1`*) is **not** triggered on either limb.

## 8. Disposition

- `src/kkt/stationarity.py` **reverted and verified byte-identical to `78ceaead`**; the reverted tree re-emits the 45-group `CASE_B` baseline, confirming the control left nothing behind.
- **Unknown 1.3** (markov leak-freedom) has its evidence in hand but is **formally resolved at the Day-2 landing**, not here — the gate passed against a tree that no longer exists.
- **Day-2 impact:** its 11 h budget assumed the leak gate was the day's risk. That risk is retired before any `src/` commit, so Day 2 becomes landing-and-verification rather than discovery. Two items carry forward into it: the **ambiguous-element filter** (§2) is load-bearing and must survive review, and the fixture (Day 3) is still the only unmet Phase-0 criterion.

---

**Document Status:** ✅ Complete — Sprint 37 Day 1 (control PROCEED; `src/` reverted, DB untouched).
**Last Updated:** 2026-08-11 · **Owner:** Sprint 37 execution team

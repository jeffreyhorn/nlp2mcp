# Sprint 38 Prep Task 4 — ganges P1: `$149` Rebind-Predicate Design & Leak-Surface Analysis

**Date:** 2026-08-17 · **Branch:** `planning/sprint38-task4` · **Measured at:** `f04c3a44` · **Scope:** control-only — a **read-only probe** was inserted into `src/ad/derivative_rules.py`, measured, and **reverted**. `src/` is byte-identical to `main`; DB and goldens untouched.

**Verdict: 🔶 REPLAN — #1668 direction 2 is NOT implementable as specified.** The task set out to design a positive requirement separating ganges (where the `$149` rebind is correct) from `prolog` (where it over-fires). **A live probe shows the two are indistinguishable on every piece of information available at the rebind site.** The blocker is not a missing predicate; it is **missing context** — and that changes P1's shape and cost.

This is the control-first discipline working as designed: the refutation cost one probe and zero `src/` changes, and it arrives in prep rather than on Day 3 of an 18–24 h track.

---

## 1. What was being designed

The banked `$149` fix (`docs/planning/EPIC_4/SPRINT_35/DAY3_P4_BANK_CARRYFORWARD.md` §5) inserts a rebind into `_diff_prod`, just before `return Binary("*", expr, log_term)`:

```python
if (wrt_indices is not None and effective_wrt is not None
        and len(effective_wrt) == len(wrt_indices)
        and effective_wrt != wrt_indices):
    rebind = {e: w for e, w in zip(effective_wrt, wrt_indices, strict=True)
              if isinstance(e, str) and isinstance(w, str) and e != w}
    if rebind:
        log_term = _apply_index_substitution(log_term, rebind)
```

It fires whenever the collapse substituted a concrete `wrt` for the prod's symbolic bound. **There is no check that the rewrite is legitimate** — that is the over-fire.

Sprint 37 Day 4 characterised the failure precisely: on `prolog` the rebind rewrites the variable reference while the sibling parameter keeps the old index, pairing price `g` with exponent `eta(g,gp,h)`; and *"`gp` was **already bound** by the enclosing `sum(gp, …)`, so there was no free-index leak to repair"*. The rebind's own justifying comment — *"so `j` leaks free"* — does not apply there.

**That gave a clean candidate positive requirement**, in the Sprint-37 fawley shape (assert what must be *true* of the genuine case, rather than subtracting exclusions):

> **Candidate:** the rebind may fire only when the index it rewrites is **genuinely free** at the site — i.e. not bound by any enclosing `Sum`/`Prod`.

And it looked cheap to implement: `_diff_prod` **already receives** `bound_indices: frozenset[str]`, documented as *"Indices bound by enclosing Sum/Prod"*, with both `_diff_sum` and `_diff_prod` doing `new_bound = bound_indices | frozenset(expr.index_sets)` before recursing. No new plumbing appeared to be needed.

## 2. The candidate is refuted — measured, not argued

A **read-only probe** (prints only; changes no value) was inserted at the exact rebind site and both models emitted.

### 2.1 Probe v1 — `bound_indices` at the site

```
model=prolog  rebind gp->food         e_in_bound=False  bound=[]
model=prolog  rebind gp->l-industry   e_in_bound=False  bound=[]
model=ganges  rebind j->agricult      e_in_bound=False  bound=[]
model=ganges  rebind j->cap-good      e_in_bound=False  bound=[]
   … (6 ganges sites, all identical)
```

**`bound_indices` is EMPTY for both models.** The enclosing `sum(gp, …)` that Day 4 identified is **not visible** at `_diff_prod` — it has been stripped before differentiation reaches this point. So `e ∉ bound_indices` is `True` for prolog *and* ganges, and the candidate would fire on both. **Refuted.**

### 2.2 Probe v2 — every other locally-available signal

| field | `prolog` (over-fires) | `ganges` (correct) |
|---|---|---|
| rebind shape | `gp -> food` (symbolic → concrete element) | `j -> agricult` (symbolic → concrete element) |
| `e ∈ bound_indices` | `False` | `False` |
| `bound_indices` | `[]` | `[]` |
| `e ∈ expr.index_sets` (prod's own binder) | **`True`** | **`True`** |
| `e` occurs in retained `expr` | `['ParamRef', 'VarRef']` | `['ParamRef', 'VarRef']` |
| `e` occurs in `log_term` | `['ParamRef', 'VarRef']` | `['ParamRef', 'VarRef']` |

**Identical on every field.** No predicate over `(effective_wrt, wrt_indices, bound_indices, expr, log_term)` can separate them, because the tuple is the same in the correct and the incorrect case.

### 2.3 What this means

**#1668 direction 2 — "restrict the trigger to a genuinely-free `prod` bound" — cannot be expressed at the rebind site.** The site cannot determine freeness: the information that would establish it (`gp` bound by an enclosing `sum`) is destroyed before `_diff_prod` runs, which `bound=[]` proves directly.

**This is the fawley lesson inverted.** fawley succeeded because a positive requirement *existed in the information available at its site* (the coefficient references the subset's parent). Here no such requirement exists — the correct and incorrect cases are locally identical, so the fix is not a predicate at all.

## 3. Where the discriminator must come from instead

Three candidate directions, in increasing cost. **None is validated here** — that is the next effort's job.

| # | direction | what it requires | risk |
|---|---|---|---|
| **A** | **Thread enclosing-binder context into `_diff_prod`** so `bound_indices` is genuinely populated at the rebind site | Find where the enclosing `Sum` is stripped and preserve its `index_sets` through to `_diff_prod`. Then the §2 candidate becomes testable. | Touches the shared differentiation entry path — **full-corpus leak exposure**, the S36 lesson |
| **B** | **Move the rebind later**, to a stage that still has the equation's free-index context (the stationarity re-symbolization) | Relocate rather than re-scope; the S37 fawley track showed an emission-path relocate is feasible but is its own multi-day effort | Changes which models the fix reaches |
| **C** | **#1668 direction 1** — rebind parameter indices *consistently*, so variable and sibling parameter move together | Makes the rewrite total rather than partial. Day 4 called direction 2 "closer to the original intent", but direction 2 is now refuted, so **direction 1 is back in scope** | May alter correct models' emit; needs its own leak gate |

**Direction C is the cheapest to test** and was prematurely deprioritised: Day 4 preferred direction 2 on intent grounds, and direction 2 is now the one that cannot be built. It should be evaluated first.

## 4. Leak surface — deferred, with a reason

The prompt asks for a full-corpus leak-surface map (every model traversing the rebind path). **That map is not derivable yet**, because the rebind path itself is about to move: under direction A it widens (more context, more models reachable), under B it changes stage entirely, under C it covers a different node type. Mapping the *current* path would produce a figure that is stale the moment the direction is chosen — precisely the banked-staleness failure this sprint keeps correcting.

**What is established and reusable:** the probe methodology. Inserting a read-only print at the rebind site and diffing the field tuple across a correct model and an over-firing model is cheap (one fast emit + one 325 s emit) and is the instrument any of the three directions needs. The two known members of the surface are **ganges/gangesx** (intended) and **`prolog`** (must stay byte-identical); Day 4 additionally showed **`korcge`** drifts benignly from the `rPower` gate — verified still `MODEL STATUS 1 Optimal` @ 339.2130 — so it belongs in `--expect-drift` when the cascade lands, not in the leak set.

## 5. Phase-0 acceptance gate (unchanged, and still specifiable)

The gate does not depend on which direction is chosen, so it is recorded now, expressed against Task 3's assertions:

- **Per-model, ganges AND gangesx** (never inferred from one): emit → compile → **count `$NNN` by GAMS's own `**** N ERROR(S)` line** (see §7) → assert 0 → solve cold AND presolve with `modelstat` asserted → bucket.
- **Full-corpus leak gate:** `make check-goldens` with `--expect-drift ganges,gangesx,korcge`; **`prolog` byte-identical** is an explicit criterion. Scope asserted via `--min-scope` so a silently narrowed sweep cannot pass (Task 3 §3.1).
- **Determinism ×3** `PYTHONHASHSEED {0,1,42}` on both goldens.
- **Slow-emit budget:** ganges 325 s, gangesx 243 s measured — nightly regen slot, not the PR gate.

## 6. Bucket expectation — **0**, restated

A fully clean cascade moves ganges and gangesx `path_syntax_error → model_infeasible`: **pse 6 → 4, mi 7 → 9. Solve stays 108, Match stays 94.** The 6th blocker (embedded `ganges0` **MS-5 @ −386785.5017** vs standalone **MS-2 @ 6395.5444**, `mcp_model` **MS-4**) is untouched. A genuine +2 needs the #1378/#1424 embedded-divergence class, which is **not scoped**. The prep-era "+2 or 0" was refuted on S37 Days 4–5 and must not return.

## 7. Correction folded in — the Sprint-37 `$141` finding is **RETRACTED**

Task 2 reported *"the ganges `$141` count does not reproduce — banked 78, measured 15 cold / 49 presolve"*. **That finding is withdrawn: the measurement method was invalid.**

**Concurrency was ruled out first** (the initial hypothesis). A serial ganges cold run with nothing else executing produced a **byte-identical emit** (md5 `72c5d5f268e9dad458f61f58491872c5`) and **identical counts** to the loaded run; load affects **runtime only** (325 s → 162 s).

**The actual defect: GAMS truncates its own error listing.** The listing carries `**** 300  Remaining errors not printed for this line` (×2), and `errmsg=1` does **not** lift it:

| run | printed `$141` | printed total | **GAMS total** | suppressed | true `$141` |
|---|---|---|---|---|---|
| cold | 15 | 29 | **51** | 22 | ≤ 37 |
| presolve | 49 | 175 | **199** | 24 | **≤ 73** |
| banked (S37 Day 4) | — | — | — | — | **78** |

**Every `grep -o '\$NNN'` count is a count of *printed markers*** — an undercount. The authoritative figure is GAMS's own `**** N ERROR(S)` line.

**Decisive corollary:** the cold run has only **51 errors of all kinds**, so `78 × $141` cannot describe a cold compile — independently confirming the banked figure came from the presolve run, as `DAY4_GANGES_CONTROL.md` §1 states.

A residual gap may remain — **≤73 vs 78** — but it is far smaller and differently shaped than the retracted "15 vs 78", and no conclusion about it is supportable until a truncation-free census exists. **Any future `$NNN` comparison must read `**** N ERROR(S)` and check for `Remaining errors not printed`.**

**Three counting errors accumulated on this one figure:** `grep -c` counting lines → the wrong variant (cold vs presolve) → printed-markers-under-a-cap. The corrected records are `BASELINE_RECONFIRMATION.md` §3, `KNOWN_UNKNOWNS.md` 1.1, `PREP_PLAN.md` Task 2, and the CHANGELOG.

## 8. REPLAN exit — taken, and what it banks

**The exit condition is met:** no positive requirement is expressible at the rebind site. P1 as scoped (18–24 h, "implement a design rather than search for one") **cannot proceed**, because there is no design to implement.

**Banked for the next effort:**
1. The refutation itself, with the probe output — direction 2 is closed, so nobody re-attempts it.
2. **The probe methodology** — a read-only print at the rebind site, field-tuple diffed across a correct and an over-firing model.
3. **Three named directions** (§3) with direction **C** recommended first as cheapest-to-test and prematurely deprioritised.
4. The unchanged **Phase-0 gate** (§5) and the **0-bucket** expectation (§6).

**Recommended disposition:** re-budget P1 from 18–24 h to a **~4–6 h direction-C evaluation** using the probe, and reallocate the remainder. The sprint has no floor lever regardless (`PROJECT_PLAN.md`, Sprint 38 Goal), so the freed budget should go to **P2 sarf** — the only KPI mover — or to P8.

---

**Document Status:** ✅ Complete — Sprint 38 Prep Task 4. **REPLAN**: #1668 direction 2 refuted by live probe; three replacement directions named; the S37 `$141` finding retracted.
**Last Updated:** 2026-08-17 · **Owner:** Sprint 38 execution team

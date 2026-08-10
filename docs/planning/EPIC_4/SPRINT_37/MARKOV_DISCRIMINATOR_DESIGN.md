# markov P1 — `σ=sp` Derivative-Structure Discriminator Design (Prep Task 4)

**Date:** 2026-08-10 · **Branch:** `planning/sprint37-task4` · **Scope:** docs/analysis-only (measurement scripts in `/tmp`; `src/` untouched).

**One line:** the three derivative structures are now **measured, not assumed** — and measurement refuted **two** successive designs before settling one. A derivative test *alone* fires on 15 models; conjoining it with Sprint 36's domain-collision signature still leaked on `iobalance` (a value coincidence); adding a **distinct-position** requirement yields a predicate that, scanned across 142 models, fires on **exactly `['markov']`** while excluding 13 of the 14 models that reach the domain gate — including S36's `cesam` and `sroute` leaks.

Reference: `SPRINT_36/DAY2_MARKOV_OFFDIAG_CONTROL.md` (emission proven, gate leaks), `MARKOV_OFFDIAGONAL_DESIGN.md` (Mechanism C), `SPRINT_37/LEAK_HARNESS_DESIGN.md` (the `make leak-check` gate). Phase-0 doc: `docs/issues/ISSUE_1110_markov-sigma-sp-discriminator.md`.

---

## 1. The three derivative structures — MEASURED

Extracted from the live Jacobian (`compute_constraint_jacobian` → `get_derivative`) for each model, i.e. exactly the ASTs that reach `_add_indexed_jacobian_terms`.

### markov — genuine param-coupling (must FIRE)
`constr(sp,j)` vs `z(s,i,sp)`; the **off-diagonal** entry (σ≠s):
```
Unary(-)
  Binary(*)
    ParamRef b()
    ParamRef pi(s, i, σ, τ, sp)          e.g. pi(15,disrupted,12,disrupted,12)
```
The coefficient is a **`ParamRef` in the value branch** whose index tuple carries **both** an equation index (`σ`, position 2) **and** the variable's own third index (`sp`, position 4). It is nonzero only on the `σ=sp` slice — the sample above has σ=12, sp=12. (The diagonal entry is `Binary(-, Const(1.0), Binary(*, b, pi(...)))` — the Kronecker `1` plus the same coupling.)

### sroute — conditional-constant (must NOT fire)
`nb(i,ip)` vs `x(i,ip,ipp)`:
```
Unary(-)
  DollarCond
   VAL:  Const(1.0)                      ← the VALUE is a bare constant
   COND: ParamRef darc(ipp, chicago)     ← the parameter lives ONLY in the condition
```
The parameter never multiplies anything; it only gates. **Excluded structurally** by walking value branches only.

### cesam — variable-bilinear (must NOT fire)
`SAMMAKE` vs `a`:
```
Unary(-)
  Binary(+)
    VarRef x(ACT)
    VarRef err1(ACT)                     ← VarRefs; NO ParamRef at all
```
**Excluded trivially** — there is no parameter to couple.

## 2. The refutation: a derivative-structure test alone is too broad

The obvious predicate — *"the value branch contains a `ParamRef` carrying both an equation index and an independent variable index"* — was prototyped and scanned across the corpus (142 models with goldens; `sarf/ganges/gangesx/turkpow/egypt/indus` skipped as pathologically slow, documented not dropped).

**Result: it fires on 15 models** — `agreste, ajax, cesam, cesam2, china, fawley, marco, markov, orani, prolog, shale, tfordy, tforss, twocge, uimp`. A parameter that couples an equation index to a variable index is an *ordinary* modelling pattern, not a markov fingerprint. Shipping that predicate would have produced a leak at least as bad as Sprint 36's.

**This is the same failure mode the S36 retrospective warned about** ("a 'leak-free by construction' design claim is a hypothesis"), caught this time *before* any `src/` change because the predicate was scanned corpus-wide at design time.

## 3. The discriminator: a CONJUNCTION

The derivative test is only meaningful **inside** the structural context Mechanism C already requires. The gate is:

**(1) Domain-collision signature** (Sprint 36's, unchanged) — a constraint/multiplier domain index whose **alias-canon** matches ≥2 variable positions, where a **later** position is an exact declared-name match and an **earlier** one is canon-only.
- markov: `constr('sp','j')` vs `z('s','i','sp')` → `sp` matches var pos 2 by name and pos 0 by canon (`s`,`sp`,`spp` are aliases) ⇒ collision at (mult 0, var 2). ✔
- This is precisely what leaked in S36 — it also fires on `sroute` `(nb, x)`, `cesam` `(SAMMAKE, a)`/`(SAMMAKE, tsam)`, and `ferts`.

**(2) Value-branch parameter coupling at distinct positions** (new) — a `ParamRef` reachable through **value** positions only (never a `$`-condition or a `Sum`/`Prod` condition) that carries an equation-index value **and** the variable's collision-position value at **two distinct positions of its own index tuple** (hence ≥2 indices; see the `iobalance` refinement below).
- markov: `pi(s,i,σ,τ,sp)` carries σ (eq) and sp (var pos 2) ⇒ fires. ✔
- sroute: the only `ParamRef` (`darc`) is inside the condition ⇒ no value-branch param ⇒ excluded. ✔
- cesam: no `ParamRef` at all ⇒ excluded. ✔

### Measured verdicts on the S36 leak set

| model | domain gate (1) — S36's | conjoined gate (1)∧(2) | required |
|---|---|---|---|
| **markov** | fires on `(constr, z)` | **FIRES** on `(constr, z)` | fire ✔ |
| **sroute** | fires on `(nb, x)` — *the S36 leak* | **excluded** | not fire ✔ |
| **cesam** | fires on `(SAMMAKE, a)`, `(SAMMAKE, tsam)` — *the S36 leak* | **excluded** | not fire ✔ |
| **dyncge** | reaches the gate | **excluded** | not fire ✔ |

The conjunction reproduces the S36 leak (proving the domain conjunct is faithfully reconstructed) and then excludes every member of it.

### A third refinement, found by measurement: `iobalance`

The conjunction as first written **still leaked** — on `iobalance`. Root cause: `colbal(j)` vs `a(i,j)` (alias `j→i`) satisfies conjunct (1), and its derivative is `ParamRef x(1)` — a **single-index** parameter whose lone index `'1'` happens to equal *both* the equation value and the variable's collision value. A naive "carries both" test fires on that **value coincidence**.

markov's coupling is structural: `pi(s,i,σ,τ,sp)` carries σ at position 2 and sp at position 4 — **two distinct positions of the same parameter**, which is what "couples" actually means. Conjunct (2) therefore requires the eq-index and collision-index matches at **distinct positions** of the parameter's own index tuple (and hence ≥2 indices). `iobalance`'s 1-index `x(1)` cannot satisfy it.

### Full-corpus scan — the decisive evidence

Scanned 142 of the 163 in-scope models (`sarf/ganges/gangesx/turkpow/egypt/indus` excluded as pathologically slow; `clearlak/dinam/ferts/tabora` timed out at 120 s — **4 unverified, recorded not hidden**):

| gate | models fired on |
|---|---|
| derivative structure **alone** | **15** — `agreste, ajax, cesam, cesam2, china, fawley, marco, markov, orani, prolog, shale, tfordy, tforss, twocge, uimp` |
| domain collision **alone** (S36's) | **14** reached it — `cesam, dyncge, iobalance, irscge, lrgcge, markov, mine, moncge, qsambal, quocge, sambal, sroute, stdcge, twocge` |
| **conjunction (1)∧(2), distinct-position** | **`['markov']` — exactly one** |

The domain gate reaching 14 models (including `cesam` and `sroute`) confirms the S36 leak is faithfully reproduced; the derivative conjunct then excludes **13 of 14**, leaving markov alone. `ferts` (the third S36 leak) timed out and is therefore **unverified at design time** — the `make leak-check` gate covers it at landing.

## 4. Hook point & composition

**All inside `src/kkt/stationarity.py` `_add_indexed_jacobian_terms`:**

| step | location | change |
|---|---|---|
| detect | after `offset_groups` is built (`:6136–6158`), before the `#1038` consolidation (`:6171+`) | compute the conjoined signature once per `(eq, var)` group |
| suppress | the same `offset_groups` dict | drop the 44 spurious off-diagonal groups for this pair (mirroring Part-1's `_skip_summed_term`) |
| emit | the correction append region (`:7214+`, alongside the `deriv_groups` loop) | append `− b·sum(j, pi(s,i,sp,j,sp)·nu_constr(sp,j))` with σ re-symbolised to the variable's `sp` |

**`_compute_index_offset_key` is NOT touched** — that shared matcher is the whole cohort-leak surface, and Mechanism C's premise is to leave it alone.

**Composition with the diagonal path:** reconciliation **(a)** — Part-1 emits the Kronecker `+ nu_constr(s,i)` only, and the off-diagonal covers all `σ=sp` entries including the self term. No exclusion guard, no double count. The Phase-0 `CASE_A` control arbitrates (a) vs (b) empirically.

**Existing infrastructure reused:** `_derivative_structure_key` (`:5475`) is *not* usable for this — it deliberately normalises index tuples to arity counts (`P(pi,5)`), which erases the very coupling we test. `_collect_free_indices` (`:4394`) is the right precedent for index-aware walking.

## 5. Phase-0 acceptance gate

Full text: `docs/issues/ISSUE_1110_markov-sigma-sp-discriminator.md` (4 `###` subsections). Summary:

1. **Correctness** — `kkt_residual.py markov` → `CASE_A` (rel ≈ 2.8e-16, from `CASE_B` 13.3), dual CONSISTENT.
2. **Bucket/KPI** — cold MCP `MODEL STATUS 1 Optimal`, `pvcost = 2401.577`, match ⇒ **genuine floor 75 → 76** (`modelstat` asserted).
3. **Leak-freedom (mandatory)** — `make leak-check MODEL=markov` prints the **unqualified** `LEAK GATE PASS` (a `PARTIAL` verdict fails: it means the sweep was narrowed). `cesam`/`ferts`/`sroute` + the 2-D cohort byte-identical. **Never** clear drift with `make regen-goldens`.
4. **Regression guard** — the `shape_markov_diagonal_kronecker` fixture fails-before/passes-after; quality gate green.

## 6. `shape_markov_diagonal_kronecker` fixture spec (lands with the fix, P7)

- **Type:** fast, in-process (no subprocess CLI) so it runs in `make test` — the durable fix for the "red since March" window where a `slow` integration test was the *only* guard.
- **Skip-if-absent:** `pytest.skip` when `data/gamslib/raw/markov.gms` is missing (CI lacks the raw corpus).
- **Asserts on the emitted `stat_z`:** (a) exactly one off-diagonal sum of the shape `sum(j, …pi(s,i,sp,j,sp)… * nu_constr(sp,j))`; (b) the Kronecker `nu_constr(s,i)` present; (c) **zero** `s__kkt*` synthetic-alias groups (the 44 spurious groups gone).
- **Fail-before (measured on the committed golden, not assumed):** `markov_mcp.gms` contains **45 distinct `s__kkt*` aliases** (the 44 spurious off-diagonal groups + the diagonal) and **zero** occurrences of `nu_constr(sp,j)` — so assertions (a) and (c) both fail today and must pass after.

## 7. REPLAN exit

If the conjunction still leaks full-corpus, narrow conjunct (2) to require the **specific coupling arity/shape** observed on markov (param whose index tuple contains the eq index at the collision-mirrored position), and failing that fall back to a per-signature allowlist. If neither is leak-free, **bank again with the new evidence** — Part-1 alone is 0 bucket and needs the same gate, so it is not a consolation landing.

---

## 8. Known-Unknown dispositions

| Unknown | Verdict | Basis |
|---|---|---|
| **1.2** a derivative-structure discriminator separates markov from cesam/sroute | ✅ VERIFIED (with two corrections) | §1 measured all three ASTs; the **conjoined, distinct-position** predicate fires on **exactly `['markov']`** across 142 scanned models. **Correction 1:** the derivative test *alone* is far too broad — 15 models (§2). **Correction 2:** the naive conjunction still leaked on `iobalance` via a value coincidence; it needs the distinct-position requirement (§3). Both were caught by measurement at design time. |
| **1.3** the discriminator passes the full-corpus leak gate | 🔶 DESIGN-VERIFIED (strong), empirical gate deferred to landing | The predicate scan fires on exactly `['markov']` over 142 models, excluding 13 of the 14 domain-gate reachers (incl. `cesam`, `sroute`). **Not yet a full leak-gate pass:** 6 models were skipped as slow and 4 timed out (`clearlak/dinam/ferts/tabora` — `ferts` is the third S36 leak), and a predicate scan is not a golden byte-diff. The definitive proof is `make leak-check MODEL=markov` **at implementation time**, per the S36 lesson that design-time claims stay hypotheses. |
| **1.4** markov cold-solves to `model_optimal` + genuine match | ✅ VERIFIED (inherited + re-confirmed) | S36 Day-2 proved the emission reaches `CASE_A` **and** cold-solves to 2401.577 + match; Task 2 re-confirmed markov is `verified_convex` ∈ the 30-model methodology partition with `mcp_objective 2401.5773` ⇒ the flip is a true +1 (75→76). |
| **1.5** the markov discriminator co-exists with the fawley P4 change | ✅ VERIFIED (stronger than expected) | **fawley declares no aliases at all** (`ir.aliases == {}`), so conjunct (1) — which requires an alias-canon match across ≥2 variable positions — is **structurally unsatisfiable** on fawley: the markov gate never even reaches it (measured: `domain_gate_pairs: []`). Conversely fawley's discriminator fires when the summed constraint index is **absent** from the coefficient, whereas markov's requires it **present** — logical complements on one axis. Disjoint by construction *and* by measurement. |

---

**Document Status:** ✅ Complete — Sprint 37 Prep Task 4 (markov `σ=sp` derivative-structure discriminator design).
**Last Updated:** 2026-08-10 · **Owner:** Sprint 37 execution team

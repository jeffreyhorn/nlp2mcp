# Sprint 38 Day 12 — P8 sweep day 4: elec #983/#1325 + dyncge #1693

**Date:** 2026-08-25 · **Branch:** `planning/sprint38-day12-p8-sweep2` · **Measured at:** `cf8c0284` · **Toolchain:** GAMS **54.2.1** / PATH **5.2.01**

**Verdict: ✅ elec #983/#1325 FIXED (KKT residual `CASE_A`) · ✅ dyncge #1693 FIXED (Solve only) — `Solve 109 → 111` · `Match 95 → 96` · `all-219 98 → 99` · **`path_solve_terminated` 2 → 0, the category is empty**. ⚠ Genuine floor UNCHANGED at 73. ⚠ NEW FINDING: dyncge has a second, independent emit defect (`CASE_B`).**

**This is the sprint's largest bucket move, and the first that was not predicted to be one.** `ISSUE_1325`'s gate says *"0 bucket expected … Do not project a Solve or Match gain."* That instruction was right to give (nothing should be *projected*), and the measured outcome exceeded it.

---

## 1. Fingerprint re-reproduced, not quoted

Fresh translate at `cf8c0284`, **byte-identical to the committed golden**, run from a scratch directory:

| §4.1 criterion | measurement |
|---|---|
| return code | **3** |
| **anchored** `^**** Exec Error at line N: division by zero (0)` | lines **99**, **100**, **101** |
| **line ↔ equation mapping, read from the `.gms` not assumed** | line 99 = `stat_x`, 100 = `stat_y`, 101 = `stat_z` ✓ |
| `Evaluation error(s) in equation "stat_{x,y,z}(iN)"` | **30** |
| **terminal state, from GAMS's own line** | `**** SOLVE from line 133 ABORTED, EXECERROR = 3` |

(`**** EXECERROR AT LINE 40 CLEARED (EXECERROR=0)` also appears; it is the *source's* own error clearing, not a defect.)

## 2. What was actually wrong — two defects, in two files, and the gate traced neither

The gate traced this to *"the stationarity term-assembly that pairs a derivative's summation index with the originating equation's condition"*. **The first defect is upstream of stationarity entirely, and the second is in a different function than described.**

Printing the objective gradient directly — before any KKT assembly — shows the emit was doomed already:

```
d(obj)/d x("i1") = sum(j__$(ut(i,j__)),  ... x("i1") - x(j__) ...)     <- `i` is FREE
                 + sum(i__$(ut(i__,j)),  ... x(i__) - x("i1") ...)     <- `j` is FREE
```

**Defect 1 — `src/ad/derivative_rules.py`, `_diff_sum` partial-collapse.** `working_condition` has only the *remaining* sum indices renamed (`j` → `j__`, per #1111's alias disambiguation). Its *matched* positions still carry the original sum-index name — which the enclosing `Sum` does **not** bind. The condition was therefore substituted differently from the body it guards. Fix: apply the same `sub_sym → sub_concrete` substitution to the condition.

> This is **not** the #1085 case in the sibling `else` branch. There the sum collapses *fully* and every index is re-symbolized as one unit, so keeping the condition symbolic is correct. Here the Sum survives and binds only `final_remaining`.

**Defect 2 — `src/kkt/stationarity.py`, `_replace_indices_in_expr`.** Its own sum-index protection is what collapsed the guard. The `Sum` branch overlays `{idx: idx}` self-mappings so AD names like `j__` survive re-symbolization — **and that also puts them in `element_to_set`**. The `SetMembershipTest` branch keys on exactly that membership to decide *"concrete element ⇒ resolve positionally against the set's declared domain"*. elec declares

```gams
Set ut(i,i) 'upper triangular part';
```

so the declared domain is `i` at **both** positions, and `ut(i,j__)` resolved to **`ut(i,i)`**. Fix: a self-mapping means *"bound index, leave it alone"*, never *"element"* — so require `element_to_set[idx.name] != idx.name`.

**Both fixes are necessary — measured, not assumed:**

| configuration | emitted guards |
|---|---|
| neither | `ut(i,i)` , `ut(i,j)` |
| defect-1 fix only | `ut(i,i)` , `ut(i,i)` |
| defect-2 fix only | `ut(i,j__)` , `ut(i__,j)` |
| **both** | **`ut(i,j__)` , `ut(i__,i)`** ✓ |

**Why each was harmful, in the mathematics.** `ut` is strictly upper triangular, so `ut(i,i)` is **structurally empty** — that half of the gradient contributed nothing and was silently dropped. And `ut(i,j)` under `sum(i__, …)` constrains nothing about `i__`, so `i__ = i` was admitted, making `d(i,i) = 0` and dividing by it.

**Emitted, after:**

```gams
stat_x(i).. sum(j__$(ut(i,j__)), …) + sum(i__$(ut(i__,i)), …) + 2 * x(i) * nu_ball(i) =E= 0;
```

which is the gate's Expected Emit Pattern exactly.

## 3. Verification

| gate criterion | before | after |
|---|---|---|
| division-by-zero exec errors | **3** (lines 99/100/101) | **0** |
| `Evaluation error(s)` | **30** | **0** |
| terminal state | `ABORTED, EXECERROR = 3` | rc **0**, no `ABORTED` |
| MCP solve (cold, from GAMS's own summary) | — | `TYPE MCP` / `SOLVER PATH` / **`MODEL STATUS 1 Optimal`**, 218 iterations, **0 evaluation errors** |
| **KKT residual (`kkt_residual.py`)** | — | **`CASE_A` — healthy (KKT correct, PATH converges)**, max relative **1.69e-08** vs tol 1e-3; dual transfer CONSISTENT |

**`CASE_A` is the criterion that matters**, and the gate says so: it is what separates *"no longer divides by zero"* from *"computes the right gradient"*. Warm-started at the NLP's own KKT point, every stationarity row evaluates to ~0.

- **Leak gate — PASS at 185 in-scope** (7 allowlisted): **exactly `elec` drifted** (−12 bytes), all other goldens byte-identical. That is a very tight radius for two changes in core AD/stationarity code.
- **`make test`** — 5223 → **5231 passed** (8 new), 10 skipped, 1 xfailed.
- **Determinism ×3** — `PYTHONHASHSEED` 0/1/42: 1 distinct hash, byte-identical to the committed golden.
- **Negative-test discipline:** the new AD test was confirmed to **fail** without the fix (`Sum over ('j__',) has condition naming unbound symbol(s) ['i']`), not merely to pass with it.

## 4. Two corrections to the gate itself

1. **`grep -c 'ut(i,i)' elec_mcp.gms` "must go from non-zero to 0" is unsatisfiable as written.** It goes **4 → 1**, and the survivor is line 20 — the **source's own `Set ut(i,i)` declaration**, re-emitted verbatim. A repeated *declaration* domain in GAMS means the full product and is correct; only *guards* were wrong. The gate's stated **intent** — "every `$(ut(...))` must name its own enclosing summation index" — is fully met, and is what the new tests assert.
2. **"elec is non-convex, so no Solve or Match gain may be projected" is stale.** The DB records elec as **`likely_convex`**, i.e. inside the 142 convex candidates. (The Thomson problem does have many local minima, so the *spirit* of the caution was sound — see §5.)

## 5. KPI — and why the floor does NOT move

| | at `cf8c0284` | after elec | after Day 12 (elec + dyncge) |
|---|---|---|---|
| Solve | 109 | 110 | **111** |
| Match | 95 (65 cold + 30 presolve) | 96 (65 + 31) | **96 (65 cold + 31 presolve)** |
| all-219 Match | 98 | 99 | **99** |
| `path_solve_terminated` | 2 | 1 | **0 — the category is empty** |
| **genuine floor** | **73** | 73 | **73 — unchanged** |

**`path_solve_terminated` reaching zero is the two-day story, not the one-day one:** Day 11 moved `tricp` out of it (to `license-gated`), and Day 12 moved `elec` and `dyncge` out (to `model_optimal_presolve` and `model_optimal`). Three models, three different destinations, one category emptied.

**The match is a PRESOLVE match, so no provenance entry is due and the cold count stays 65.** This is exactly the distinction P6c exists to enforce, and it would have been easy to misreport: the pipeline's summary line says *"Pre-solve retry: 1/1 recovered from STATUS 5"*, which is **wrong about the trigger**. elec's cold solve **succeeded** (MS-1 @ **244.624**); the retry fired on the *other* branch, `_cold_objective_mismatches_nlp`, because 244.624 ≠ the NLP's 243.8128. **That summary string is hardcoded for both trigger paths** (`run_full_test.py` ~1826) and should name which one fired.

**Is the presolve match spurious in the Day-10 sense? No — checked, not assumed.** `check_mcp_solve_attribution.py` reports **`MCP-SOLVED — elec/NLP MS-2, mcp_model/MCP MS-1`**: the listing carries our own `mcp_model` MCP summary, not merely the embedded NLP's. `check_presolve_divergence.py --model elec --tol 1e-3` also passes. Both are the gates `weapons` failed, so `elec_mcp_presolve.gms` is adopted; the presolve golden count goes 39 → **40** and leak-gate scope 185 → **186**.

**Reading the cold-vs-warm gap honestly:** the cold MCP reaches a *different* stationary point (244.624) from the NLP's (243.8128). With `CASE_A` established, that is not an emit defect — it is the Thomson problem having many KKT points, and PATH cold-starting into a different one. The warm start lands it on the NLP's, in **1 iteration**.

## 6. dyncge #1693 — fixed, and it uncovered a second defect

**Fingerprint re-reproduced at `cf8c0284`** (fresh translate byte-identical to the golden): rc 3 · **4 ×** `**** MCP pair eqpf2.nu_eqpf2 has empty equation but associated variable is NOT fixed` · `**** SOLVE from line 569 ABORTED, EXECERROR = 4`. The count is derived: `card(h_mob) × card(i)` diagonal = 1 × 4 = 4.

`eqpf2(h_mob,i,j).. pf(h_mob,j) =e= pf(h_mob,i)` with `Alias (i,j)` is **reflexive**, so at `i = j` it reads `pf = pf` — no constraint, nothing for a multiplier to price, an empty row against a free `nu_eqpf2`.

### ⚠ The gate was wrong that this needs new logic

It says detecting this *"requires … **new logic** rather than a widened condition-lift."* **The logic already existed.** Section **2c** (#942 / #1021 / #1104) has done exactly this diagonal-triviality test since Sprint 24 — substitute `d_j → d_i`, then four escalating emptiness checks. **It was never inequality-specific; it was only ever applied to `kkt.complementarity_ineq`.** dyncge's `eqpf2` is an equality, so it never reached the loop.

So the change is a **reuse of corpus-hardened logic**, not new machinery: `_diagonal_instance_is_trivial` and `_same_set_domain_pairs` extracted from 2c, a new **section 3c** applying them to equalities, and 2c rewired to the same helper so both populations share one implementation.

**Soundness, stated because it is the REPLAN condition:** the test is **sufficient, not necessary**. It may miss an empty row; it must never call a live row empty, because pinning a binding constraint's multiplier is a *silent wrong answer*, not an error.

### Verification

| gate criterion | before | after |
|---|---|---|
| empty-pair messages | **4** | **0** |
| `eqpf2` rows generated | — | **12**, with **0 diagonal** (counted from the listing) |
| terminal state | `ABORTED, EXECERROR = 4` | rc **0**, no `ABORTED` |
| modelstat, from GAMS's own line | — | **`MODEL STATUS 1 Optimal`** |

**Leak gate PASS at 186 in-scope** — **exactly `dyncge` drifted** (+46 bytes). Section 3c fires on **one model in the entire corpus**.

### ⚠ NEW FINDING — a second, independent defect in dyncge

`kkt_residual.py` → **`CASE_B — emit_bug`**, max relative residual **6.22e-02** (tol 1e-3) at `stat_pf(CAP,SRV)`, dual transfer CONSISTENT. Warm-started at the NLP's own KKT point, dyncge's stationarity rows do **not** evaluate to zero.

**The empty-pair abort was masking a gradient defect.** The cold MCP now solves to `MODEL STATUS 1 Optimal` at **381401.119** against the NLP's **539570.5027** — a **29.3 %** mismatch. The presolve retry also fails to match (`0/1`), so **there is no spurious match to adjudicate**.

**Solve +1 is genuine; Match is 0 and is not claimed.** #1693's own Bucket/KPI note called this exactly: *"Clearing the abort lets it reach PATH; whether it then solves or matches is unclaimed."* The residual's top rows (`stat_pf`, `stat_pq`) point at the `pf`/`pq` block, not at `eqpf2` — **a new diagnosis, and therefore a new issue, not a widening of #1693.**

## 7. Carry

- **`path_solve_terminated` is empty.** Every remaining non-solve is `license-gated` (11), `model_infeasible` (7) or `path_syntax_error` (6).
- **dyncge's `CASE_B` needs a new issue and a new diagnosis** — top residual rows `stat_pf(CAP,SRV)`, `stat_pq(HMN)`, `stat_pf(LAB,SRV)`. It is not #1693 and must not be folded into it.
- **A pattern now seen twice in two days.** tricp (Day 11) and elec both trace back to **a repeated set symbol in a declaration domain** being used positionally somewhere downstream — `slp(n,n)` as a variable domain, `ut(i,i)` as a set domain. Day 11 fixed the variable-domain case at the declaration; this fixes the set-domain case at the point of use. **Anywhere the code resolves an index "positionally against the declared domain" is suspect when that domain repeats a symbol**, and that idiom appears in several more places in `stationarity.py`.

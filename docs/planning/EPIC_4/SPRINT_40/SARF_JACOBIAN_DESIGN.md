# sarf Jacobian O(active) Re-Architecture — Design (Sprint 40 Prep Task 9)

**Measured at:** `8fda6f9d` (`main`) · **Date:** 2026-10-14 · **Machine:** 8 physical / 16 logical cores, shared. Load averages are recorded per run, because they moved timings by up to ~2.5×. **Shares and call counts are the robust figures; wall times are indicative.**

**Scope:** design only. `src/` and `tests/` are untouched; every measurement used scratch harnesses outside the repo (reproduced in `artifacts/SARF_PROFILING_HARNESS.md`). The one prototype was **in memory only** and is never landed.

---

## Bottom line

1. **The non-termination is one loop, and the cause is an omission, not an algorithmic limit.**
   - Sprint 38 Day 7's referenced-instance filter (#1385) was applied **only to `_compute_equality_jacobian`**. **`_compute_inequality_jacobian` and `_compute_bound_jacobian` still iterate every declared instance.**
   - sarf has **792 inequality rows** that reference `task` (369,024 declared instances), so that loop asks for **792 × 369,024 = 292.3 M** differentiations: roughly 36 h at the measured rate.
   - The equality path, filtered, completes in 26–59 s.
2. **Filtering the inequality path works and is byte-identical.** In an in-memory prototype, the inequality path drops from 292.3 M to **158,666** differentiations and **completes** (131–171 s). On the declared-size fixture, the emit is **byte-identical at every size** while the work goes flat.
3. **But sarf then hits two more things nobody has seen, because nothing ever got past its Jacobian:**
   - **`validate_jacobian_entries` scans the Jacobian densely** (rows × columns: (404 + 824) × 369,165 ≈ 453 M probes), taking **113 s**;
   - **`assemble_kkt_system` crashes**: `RecursionError` in the recursive `simplify`, reached from `build_stationarity_equations` on the indexed-variable branch.
   - **So +1 Translate needs at least three changes, not one, and still faces the ≤ 300 s gate:** ~450 s was spent before the crash, even at light load.
4. **`gradient.py:453` is dead:** statically (no production caller), and dynamically (never executed over **all 186** leak-gate goldens, §5).
5. **Re-estimate:**
   - **P6 as "+1 Translate this sprint" is high-risk.** Recommended scope for Task 12: land the **filter (E1/E2)** plus **E3/E4** as byte-identical, corpus-safe changes (~8–12 h), and **diagnose the recursion (E5)** as a bounded item.
   - **Project +1 Translate only conditionally** (§8).

---

## 1. Profile at HEAD (Unknown 6.1)

**Positive control first:** a deliberate `time.sleep(5)` wrapped around `src.cli.parse_model_file` (patched at its point of use, on `trnsport`). The profile attributes **5.005 s** to `time.sleep` inside the wrapper, so attribution of inserted work is sound.

**Run A, `cProfile`, full sarf translate, hard-stopped at 600 s,** with snapshots at 120 s and 600 s (two windows). Load average 17 at start, 15 at end. **sarf did not terminate**, as always.

| window | self time | dominated by |
|---|---|---|
| **0–120 s (warm-up)** | 119.8 s | **parsing**: Earley `predict_and_complete` 14.9 %, `visit` 10.5 %, `grammar.__eq__` 8.2 % |
| **120–600 s (steady state)** | 447.7 s | **AD only**: `derivative_rules.py` 33.9 %, `ad_core.py` 21.4 %, builtins 20.6 %, `case_insensitive_dict.py` 12.9 %, `index_mapping.py` 5.3 %, import machinery 4.1 % |

**Steady-state per-callee breakdown** (self time, 120–600 s):

| callee | self % | calls at 600 s |
|---|---|---|
| `ad_core.simplify` | **20.9 %** | 6,265,433 |
| `CaseInsensitiveDict.__contains__` (+ `__getitem__` 2.7 %, `str.lower` 3.3 %) | **10.3 %** | 11,470,002 |
| `builtins.isinstance` | 8.2 % | 59,202,512 |
| `derivative_rules._is_concrete_instance_of` | 8.7 % | 3,740,866 |
| `derivative_rules._diff_sum` | 5.6 % | 680,589 |
| `index_mapping.resolve_set_members` | 4.5 % | 3,744,216 |
| `derivative_rules.differentiate_expr` | 4.3 % | 3,331,471 |
| **import re-resolution** (`importlib._bootstrap.parent` 4.1 % + `str.rpartition` 3.0 %) | **7.1 %** | 10,027,595 |
| `derivative_rules._partial_index_match` | 3.2 % | 220,545 |

**What it asks for, by name:** `_substitute_indices` does not appear in the top rows. `_diff_sum` is a dispatcher (5.6 % self), and the cost is in what it calls: `simplify`, case-insensitive lookups and instance resolution. Index enumeration (`enumerate_variable_instances`, 40 calls, 5.7 s cumulative) is negligible. **The order matches Sprint 39 Day 7's run** (`simplify` 19.2 %, lookups ~18.9 %, instance resolution ~14.8 %, imports 7.5 %). **`src/ad/` has not changed since 2026-08-25, before that run**, and nothing landed since (#1737/#1741 included) touches this path.

**"Is 70.9 % still in `compute_constraint_jacobian`?"** The figure is **cap-dependent**, because the run never ends. Here `compute_constraint_jacobian` is **315.2 s of 600 s (52.5 %)**; Sprint 39's 70.9 % was 637.9 of 900 s. As the cap grows the share tends to 100 %, so the stable statement is: **all of the unbounded cost is inside it, in one loop** (below).

**Run B, unprofiled phase timing** (wall timestamps at phase entry and exit, `differentiate_expr` counted per Jacobian path, cap 900 s, load ~14): this resolves where inside.

| phase | wall | `differentiate_expr` calls |
|---|---|---|
| parse | 42.2 s | — |
| objective gradient | 69.1 s | **369,165**: every declared instance of every variable |
| `_compute_equality_jacobian` (filtered) | 58.6 s | 122,866: **completes** |
| `_compute_inequality_jacobian` (**unfiltered**) | **> 728 s, still running at the cap** | **1,642,266** by the cap, of **292,267,008** required |

The required figure: 792 inequality rows reference `task` (`labor` 24, `equipb1` 648, `equipb2` 120) × 369,024 declared `task` instances. At ~2,255 differentiations/s, that's **~36 h**.

*Run A's 120 s snapshot truncated the cumulative accounting of frames already open, which made the gradient look like 8.7 s. Run B's unprofiled wall clock is the authority for phase times; Run A's self times are the authority for shares.*

## 2. Entry points — anchored by code (owning function + anchor occurring exactly once in live code)

Resolved with `_owning_bodies` / `_code_only` from `tests/unit/kkt/test_positional_domain_sites.py`, so comments and docstrings cannot satisfy an anchor. Line numbers are at `8fda6f9d` and are informational only.

| id | file :: function | anchor (unique in that function's code) | role |
|---|---|---|---|
| **E1** | `src/ad/constraint_jacobian.py` :: `_compute_inequality_jacobian` | `for var_indices in var_instances:` (L1300) | **the non-terminating loop**: rows × **declared** instances, no filter |
| **E2** | `src/ad/constraint_jacobian.py` :: `_compute_bound_jacobian` | `for var_indices in var_instances:` (L1384) | same shape for bound rows; not hit by sarf (its 2 bounds are among the inequalities), but hit by the fixture |
| **R1** | `src/ad/constraint_jacobian.py` :: `_compute_equality_jacobian` | `referenced = _referenced_index_tuples(constraint_expr, var_name, model_ir)` (L1174) | the existing filter to **reuse** |
| **R2** | same | `key=position.__getitem__` (L1181) | its order-preserving sort, not O(declared) filtering (the Day-7 trap) |
| **E3** | `src/ad/gradient.py` :: `compute_objective_gradient` | `enumerate_variable_instances` (L287) | the objective gradient differentiates **every** declared instance (369,165 calls, 21–69 s) |
| **E4** | `src/validation/numerical.py` :: `validate_jacobian_entries` | `for row_id in range(jacobian.num_rows):` (L144) | **dense** rows × columns scan to find stored entries: (404 equality + 824 inequality rows) × 369,165 columns ≈ 453 M probes, **113 s** (35 s + 78 s, matching the 404 : 824 row ratio) |
| **E5** | `src/kkt/stationarity.py` :: `build_stationarity_equations` | `stat_expr = _build_indexed_stationarity_expr(` (L2548) | builds the indexed `stat_task` expression whose simplification then recurses to the limit |
| **E6** | `src/ad/ad_core.py` :: `simplify` | `simplified_left = simplify(left)` (L170) | **recursive** binary simplification; the `RecursionError` frame |
| **E7** | `src/ad/ad_core.py` :: `simplify` | `from ..ir.ast import (` (L127) | function-local import re-resolved per call (part of the 7.1 %) |
| **E8** | `src/ad/derivative_rules.py` :: `_is_concrete_instance_of` | `from .index_mapping import resolve_set_members` (L3087) | the other hot local import |
| C1 | `src/ad/constraint_jacobian.py` :: `_precompute_variable_instances` | `enumerate_variable_instances(var_def, model_ir)` (L80) | the declared column cache: **keep** (it is the order source) |
| C2 | `src/ad/index_mapping.py` :: `build_index_mapping` | `enumerate_variable_instances` (L634) | `col_id` assignment: **must not change** (renumbers every model) |
| D1 | `src/ad/gradient.py` :: `compute_gradient_for_expression` | `enumerate_variable_instances` (L453) | dead (§5) |

## 3. The prototype — the filter applied to E1, in memory only

`_compute_inequality_jacobian` is rebuilt from its **own source**, with the R1/R2 construction inserted before E1's loop, and swapped in at runtime. `src/` on disk is untouched. Recorded in the harness artifact.

- **On the fixture (§6): byte-identical at every size**, and the inequality work goes from 4 × 3N to a flat 16.
- **On sarf** (cap 1,200 s, load ~5): the Jacobian **completes**.

| phase | wall |
|---|---|
| parse | 10.3 s |
| gradient (E3, unfiltered) | 20.9 s |
| equality Jacobian | 26.3 s |
| **inequality Jacobian, filtered** | **131.2 s**, 158,666 calls (vs 292.3 M) |
| `validate_jacobian_entries` ×2 (E4) | **113.3 s** |
| `assemble_kkt_system` | 146.1 s, then **`RecursionError`** |

- **The crash path:** `assemble_kkt_system` → `build_stationarity_equations` (E5) → `apply_simplification` → `simplify_advanced` → `simplify` (E6), recursing past the CLI's 50,000 limit.
- ⚠ **A prototype bug of exactly the dangerous kind was caught by the fixture.** The first version's inserted lines landed one indentation level too shallow, so only the last variable per row was differentiated. That silently **dropped the `cap(i)` constraint**: `lam_cap` and `comp_cap` vanished, with no error. **Only the fixture's byte-identity golden caught it.** This is why the fixture is part of the gate (§7).

## 4. Atomicity boundary (Unknown 6.3)

**The filter changes no output: it only skips derivatives that are identically zero.** Zero derivatives are never stored (`_is_zero_const`), the column set and `col_id`s are untouched (C1/C2), and order follows the declared position map (R2). So **E1 + E2 is self-contained**: one commit, no cross-function consistency obligation. This differs from Sprint 39's fear, which concerned *column* narrowing (renumbering), not row work.

- **E3** (gradient) is the same kind of change, also independent.
- **E4** is pure validation, independent, and must still raise on a non-finite constant.
- **E5/E6** (recursion) changes simplification, which **every model's emit goes through**. It is the one item with real corpus-wide emit risk, so it must land **separately**, behind its own byte-identity gate.

**A flag is unnecessary for E1–E4** (byte-identity is the proof). **It is advisable for E5/E6**, if the fix changes simplification order.

**Shared-helper requirement (Sprint 39 Day-5 lesson, `ISSUE_1694`):** do **not** copy the R1/R2 block into E1 and E2. Factor it into one helper, e.g. `_effective_instances(constraint_expr, var_name, var_instances, position_maps)`, used by all three paths, so the predicate cannot drift between copies.

**#1737 / #1741 interaction** (feeds Task 10, Unknown 8.2): their guards live in `src/ir/index_map.py`, `condition_eval.py`, `kkt/empty_equation_detector.py` and `kkt/repeated_domain.py`, **outside this touch set**. The filter is **repeat-safe**: `_referenced_index_tuples` walks positions with `enumerate(indices)` and resolves labels by `var_def.domain[position]`, never symbol→position, which is the Sprint-39 Task-7 discriminator. sarf's `task(g,t,mn,mn)` has a repeated declared domain, so the gate must include it, and it does: sarf is the target.

## 5. `gradient.py:453` — still dead (Unknown 6.3)

- **Static:** `compute_gradient_for_expression`'s only references are its own docstring and `tests/integration/ad/test_gradient.py`. No production caller, and no `getattr` or string reference.
- **Dynamic:** a `coverage run --include=*/src/ad/gradient.py` translate of **every leak-gate golden** (186: 146 cold + 40 `--nlp-presolve`), 4 in parallel. **All 186 measured**: 181 at a 900 s cap, and the 5 slow ones re-run at 2,400 s.
  - **Positive control:** `compute_objective_gradient` executed **27 of 28** statements, L287 included.
  - `compute_gradient_for_expression` executed **1 of 19**: its `def` line, at import. **L453 never executed.**
  - **5 hit the 900 s cap under load** (dinam, ferts, ganges, gangesx, turkpow; a killed run writes no data). **Re-run at a 2,400 s cap, all completed** (547–1,232 s). In the combined data from all 186, **L287 executed and L453 did not**.

## 6. Fail-before fixture — declared cardinality scaled, active set fixed (Unknown 6.2)

**sarf cannot be its own fixture** (it does not terminate). The fixture is synthetic, and the generator is in the harness artifact:

```gams
Set i / i1*i3 /, j / j1*j<N> /, a(j) / j1*j5 /;
Variable z;
Positive Variable x(i,j);
x.up('i1','j1') = 5;
Equation obj, cap(i);
obj..    z =e= sum((i,a), x(i,a));
cap(i).. sum(a, x(i,a)) =l= 10;
Model m / all /;
solve m using lp minimizing z;
```

Declared `x` = 3N; **active (referenced) `x` = 15 at every size**. It has one equality row (the filtered path), three inequality rows plus a bound row (the unfiltered path; bounds are counted among the inequalities).

| N | declared `x` | equality diffs | **inequality diffs, fail-before** | translate, fail-before | inequality diffs, **prototype** | translate, prototype | emit sha256 (**golden**) | prototype emit |
|---|---|---|---|---|---|---|---|---|
| 100 | 300 | 16 | **1,200** | 2.19 s* | **16** | 1.1 s | `b9152b4b06d3c8b0dd515f2f0669e626faf9e39e6ce90ddd8c9f1f61cf758602` | byte-identical |
| 400 | 1,200 | 16 | **4,800** | 1.36 s | **16** | 1.2 s | `6d650c5467b2d5ca1c6b758096d9a7fbc8b31a64d16b872c63d2455209f3f7b1` | byte-identical |
| 1,600 | 4,800 | 16 | **19,200** | 4.32 s | **16** | 1.6 s | `16ae7ab63ad1dfe25e1222354e69ec5887568225e2d455f9a28b5be1bd94d041` | byte-identical |
| 6,400 | 19,200 | 16 | **76,800** | 14.49 s | **16** | 3.6 s | `9171a467da3f7c562656c108aa20b097525e660d404ff1368347b0b0badc6c7b` | byte-identical |

\* includes interpreter warm-up.

- **Positive control:** the work grows **exactly linearly with declared size** (4 rows × 3N) while the active set is constant. This is the documented O(declared)-per-row signature (`SPRINT_38/SARF_REARCH_DESIGN.md`, `SPRINT_38/DAY7_SARF_GATE_P6C.md`). After the filter it is **flat**.
- **Correctness:** the emits are **byte-identical** to the fail-before golden at all four sizes.
- **It terminates in seconds both ways.**

## 7. The gate (P6, for the change this design supports)

| criterion | requirement |
|---|---|
| fixture | all four sizes: emit **sha256 equal** to the §6 golden; inequality `differentiate_expr` count **constant** in N (16) |
| leak gate | **full scope**, byte-identical (`make check-goldens`). `make leak-check MODEL=sarf` is `NO-OP` (no golden) and **is not the gate** |
| sarf (E1–E4) | the Jacobian **completes**; inequality calls ≈ **158,666** (not 292 M); reported phase times |
| sarf (+1 Translate) | completes at **≤ 300 s** on a nightly slot with a byte-stable golden, scope **186 → 187**; `stat_task` symbolic-index check **with its positive control** (`SPRINT_39/SARF_CALLSITE_PLAN.md` §7); determinism ×3 |
| Day-7 trap | no narrowing whose own cost is O(declared) per row. Use the sort-by-position construction (R2), never a filtered declared list |

## 8. Re-estimate and REPLAN exits

| item | entry points | est. | expected effect on sarf | risk |
|---|---|---|---|---|
| filter, inequality + bound paths, one shared helper | E1, E2 (+R1/R2) | **4–6 h** | Jacobian completes (~131–171 s) | low: byte-identical, fixture-gated |
| gradient filter | E3 | 2–3 h | −21 to −69 s | low |
| sparse validation | E4 | 1–2 h | −113 s | low |
| hoist the two local imports | E7, E8 | 1 h | ~−7 % of AD time | low (S39 verified no cycle) |
| **`simplify` recursion on deep stationarity expressions** | E5, E6 | **6–12 h, uncertain** | removes the crash; time unknown | **high**: touches every emit |
| **total** | | **14–24 h** | | |

**+1 Translate is not established by this design.** Even the prototype's crash point (~450 s at light load) is past the 300 s gate before emit has run, and emit has **never** been reached for sarf. **Recommendation to Task 12:**
- **P6 lands E1–E4 + E7/E8** (≈ 8–12 h): corpus-safe, byte-identical, and they turn sarf from "never finishes the Jacobian" into "reaches KKT assembly";
- **P6 diagnoses E5/E6** as a bounded item;
- **Project +1 Translate only if E5/E6 lands and the gate's 300 s is met.**

**REPLAN exits:**
1. **Timeout re-trigger:** after E1–E4, if sarf still exceeds the cap **before** reaching `assemble_kkt_system`, stop and re-attribute; do not iterate on the filter.
2. **Atomicity / correctness violation:** **any** golden or fixture-hash change from E1–E4 means the filter skipped a non-zero derivative. Stop. It is a `_referenced_index_tuples` false negative (the cesam2 case-folding precedent), not a tuning issue.
3. **Recursion fix balloons:** if E5/E6 needs a change to `simplify`'s algorithm, rather than to the shape of the expression `_build_indexed_stationarity_expr` builds, re-scope it to its own issue and **remove +1 Translate from the projection**.

## 9. Touch set for Task 10 (Unknown 8.2)

`src/ad/constraint_jacobian.py` (E1, E2, R1/R2 helper) · `src/ad/gradient.py` (E3) · `src/validation/numerical.py` (E4) · `src/ad/ad_core.py` (E6, E7) · `src/ad/derivative_rules.py` (E8) · `src/kkt/stationarity.py` (E5, only if the fix is on the builder side). **No overlap** with the #1737/#1741 guard files.

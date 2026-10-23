# ISSUE #1755 — a sum whose reference repeats its binder never collapses (derivative 0, constraint dropped)

**GitHub:** [#1755](https://github.com/jeffreyhorn/nlp2mcp/issues/1755) · **Status:** 🔴 **OPEN** — filed Sprint 40 Prep Task 10 (2026-10-15)
**Layer:** **AD** — `src/ad/derivative_rules.py::_diff_sum`, its **single-binder partial-match loop** (the `len(wrt_indices) > len(expr.index_sets)` branch, Issues #1086/#1111). ⚠ Re-located on Sprint 40 Day 5 by a call trace: `_sum_should_collapse` returns False here, but it is not where the derivative is lost (see *Phase 0* below).
**Measured at:** `b85afbc0` (`main`) · **Track:** Sprint 40 P7 (the diagonal-reference defect)

**Minimal reproducer (on `main` b85afbc0):**

```gams
Set i / i1*i3 /;
Alias (i,j);
Variable tsam(i,j), z;
Equation diagsum(j), obj;
diagsum(j).. sum(i, tsam(i,i)) =e= 1;
obj.. z =e= sum((i,j), tsam(i,j));
Model m / all /;
solve m using lp minimizing z;
```

`python -m src.cli diagsum.gms -o out.gms` emits **`stat_tsam(i,j).. 1 =E= 0;`**, infeasible by construction. The constraint `diagsum` and its multiplier are **dropped from the MCP entirely**.

**Mechanism:**
- `_sum_should_collapse` begins with `if len(sum_index_sets) != len(wrt_indices): return False`, so it pairs sum binders with the variable's positions positionally.
- `sum(i, tsam(i,i))` has **one** binder in **two** positions, so it never collapses, even for the diagonal instance `tsam('i1','i1')`, where `i = i1` is consistent.
- The body is then differentiated symbolically, `_diff_varref(tsam(i,i))` vs `tsam('i1','i1')` gives `0`, and every derivative of the row is 0.
- The all-zero row and its multiplier vanish downstream.

**Correct row (hand-derived, verified by solve):** for the scalar variant `diag.. sum(i, tsam(i,i)) =e= 1;` with objective `sum((i,j), sqr(tsam(i,j)))`, the correct row is `stat_tsam(i,j).. 2*tsam(i,j) + nu_diag$(sameas(i,j)) =E= 0;`. A hand-patched MCP solves **MS 1 at objective 0.333**, matching the NLP's 0.3333 (MS 2).

**Scope:** no committed golden contains a non-zero constant-only stationarity row, so the pattern is latent in the corpus. (egypt's dropped constraints share the outcome but not the gate: see *A related corpus case* below and #1776.) But a dropped term in a row that has other terms would not show up in that grep.

**Fix direction:** collapse when every position referencing the same binder carries the same concrete value. That is a binder→value map built from the reference's index positions, not `zip(binders, wrt)`.

Sprint 40 P7. Analysis: `docs/planning/EPIC_4/SPRINT_40/CORRECTNESS_PRETRACES.md`.

## How the layer was located (not assumed)

Instrumenting `differentiate_expr` inside the real pipeline shows `d[sum(i, tsam(i,i)) − 1] / d tsam(a,b)` returns **0 for all nine instances**, including the diagonal `('i1','i1')`.

A `sys.settrace` of one diagonal differentiation gives `_diff_sum` → `_sum_should_collapse` → **`False`** → `_diff_varref(tsam(i,i))` vs `('i1','i1')` → `_alias_match` → `None` → `Const(0)`. The result is `sum(i, 0) − 0`.

## Phase-0 gate (outline)

- **Fail-before:** this reproducer emits `stat_tsam(i,j).. 1 =E= 0;` and contains no `diagsum` / `nu_diagsum`.
- **Pass-after:** `diagsum` and `nu_diagsum` are present, and `stat_tsam` carries `nu_diagsum` on the diagonal only. The scalar variant solves to the NLP objective (0.3333).
- **Positive control:** an off-diagonal instance (`tsam('i1','i2')`) still differentiates to **0**, so the fix must not collapse inconsistent binder values.
- **Corpus:** the full leak gate, byte-identical, **complete** (no unverified timeouts). A golden that changes is a candidate *corpus* instance of this defect, and is to be examined rather than refreshed blindly.

## Phase 0: Acceptance Gate (Sprint 40 Day 5, P7)

### Layer

**AD — `src/ad/derivative_rules.py::_diff_sum`, the single-binder partial-match loop** (the `len(wrt_indices) > len(expr.index_sets)` branch with `len(expr.index_sets) == 1`, added for #1086 and extended for #1111).

**The layer named in prep was the gate, not the loss site, and Day 5 re-traced it.** A call trace of `d sum(i, tsam(i,i)) / d tsam('i1','i1')` inside the pipeline gives:

```
_sum_should_collapse(('i',), ('i1','i1'))            -> False   (1 binder, 2 positions)
_diff_varref(tsam(i,i), wrt=('i','i1'))              -> 0       (loop: position 1 symbolic)
_diff_varref(tsam(i,i), wrt=('i1','i'))              -> 0       (loop: position 2 symbolic)
_diff_varref(tsam(i,i), wrt=('i1','i1'))             -> 0       (fallthrough, concrete)
=> Sum((i), Const(0.0))
```

- `_sum_should_collapse`'s `len(sum_index_sets) != len(wrt_indices)` early return does reject the call. But making it return True would only reach the full-collapse branch, which pairs binders with positions by `zip(expr.index_sets, wrt_indices, strict=True)`: a `ValueError` for 1 binder and 2 positions.
- **The derivative is lost in the loop.** It symbolizes **one position at a time**, so the binder is never placed at *both* positions of `tsam(i,i)`, the only `wrt` that matches the reference.

### Nearest Existing Mechanism

**Nearest:** the loop itself (#1086 per-position retry; #1111 conversion of the *other* positions to free body indices).

**Why it does not apply:**
- The #1086 retry symbolizes **one** position per attempt.
- The #1111 conversion skips **bound** indices (`_body_bound`, which includes the binder `sum_idx`) on purpose, so it cannot put the binder at a second position.
- The duplicate guard (`duplicate_sym`) then rejects any substitution map that names the binder twice. **That guard is correct and is not widened:** a map from the binder to two different values has no honest value.

**Also considered and rejected:**
- **Widening `_sum_should_collapse`.** It answers "does every binder pair with one position?", and the full-collapse branch assumes the answer is yes (`zip(..., strict=True)`). Admitting unequal counts there is the positional-correspondence error of the sibling **#1776**, not a fix for it.
- **`_partial_index_match`** (the multi-binder `else` branch): it does not cover this shape, because it is reached only with two or more binders.
- **#1737 (`assert_no_repeated_symbol`):** it guards a repeated symbol in an **equation domain** being bound to an instance. Here the repeat is in a **reference's argument list** inside a sum, so the mechanism does not reach it. #1737 is **not narrowed** (see the PROCEED/REPLAN signal).

### Positive Control

The **off-diagonal** instance must still differentiate to **0**: `d sum(i, tsam(i,i)) / d tsam('i1','i2')`. The fix may place the binder at several positions **only when the `wrt` values at those positions are equal**. A reference whose positions carry different values must not collapse. A test asserts this, and a mutant that drops the equal-values condition must fail it.

### Hand-Derived KKT Shape

**Scalar variant** (`diag.. sum(i, tsam(i,i)) =e= 1;`, objective `sum((i,j), sqr(tsam(i,j)))`, `Set i /i1*i3/`, `Alias (i,j)`):

- `∂/∂tsam(a,b) [sum(i, tsam(i,i))] = 1` if `a = b`, else 0.
- **Stationarity:** `stat_tsam(i,j).. 2*tsam(i,j) + nu_diag$(sameas(i,j)) =E= 0` (up to the emitter's sign convention for the equality multiplier).
- `diag` is restored and paired with `nu_diag`.
- **Solution:** `tsam(i,i) = 1/3`, off-diagonal 0, `nu_diag = -2/3`, objective **3 · (1/3)² = 0.3333**, which equals the NLP's MS 2 optimum 0.3333 (prep's hand-patched MCP solved MS 1 at 0.333).

**Indexed reproducer** (`diagsum(j).. sum(i, tsam(i,i)) =e= 1;`, linear objective):
- `diagsum(j)` does not depend on `j` in its body, so `∂ diagsum(j) / ∂ tsam(a,a) = 1` for **every** `j`.
- **Stationarity:** `stat_tsam(i,j).. 1 + (sum over j' of nu_diagsum(j'))$(sameas(i,j)) =E= 0`. The emitter may write the `j'` sum through an alias.

### Expected Emit Pattern

- **Reproducer:** `diagsum` and `nu_diagsum` are **present**, the pair `diagsum.nu_diagsum` is in the model statement, and `stat_tsam` carries `nu_diagsum` **only on the diagonal** (a `sameas(i,j)`-shaped condition or an equivalent diagonal restriction). **No** `stat_tsam(i,j).. 1 =E= 0;`.
- **Corpus:** **byte-identical** is the expectation, because the corpus grep for the constant-only symptom found no instance (`CORRECTNESS_PRETRACES.md` §4). The new attempt runs **only after** every existing attempt has returned zero, so a model the loop already handled cannot change. **Any golden that changes is a candidate corpus instance to examine, not refresh.**

### Verification Methodology

1. **Fail-before, at the layer:** `differentiate_expr(sum(i, tsam(i,i)), 'tsam', ('i1','i1'))` returns a structurally-zero result on `main`; the test asserts the same call returns 1 after.
2. **Positive control** (above): `('i1','i2')` stays 0.
3. **Shape coverage:** a case-only repeat `tsam(i,I)` (GAMS identifiers are case-insensitive); a three-position repeat `w(i,i,i)`; a mixed reference `v(i,i,'k1')` whose third position is concrete and must still match.
4. **Emit:** the reproducer's MCP carries `nu_diagsum` on the diagonal and no `1 =E= 0`.
5. **Solve (GAMS, run on a copy in `tmp_path`):** the scalar variant's MCP solves to 0.3333 within the comparison tolerance.
6. **Corpus:** `make check-goldens`, **alone**, complete (`--fail-on-unverified`, 0 timeouts). Then `make check-index-repeats` and the full `make test`.
7. **Mutation controls**, each in a throwaway worktree: revert the fix (tests 1, 4, 5 fail); drop the equal-values condition (test 2 fails).

### PROCEED/REPLAN Signal

- **PROCEED** if tests 1–5 pass, the positive control holds, the leak gate is complete and byte-identical (or every changed golden is examined and shown to be a genuine instance), and `check-index-repeats` is unchanged.
- ⚠ **Expected, not a regression:** the fix newly references multipliers, so a model whose equation domain **repeats** a symbol (shape (a) in `CORRECTNESS_PRETRACES.md` §6, `dd(i,i)`) turns from *silently dropped* into **refused by #1737**. That is #1737 working. **Never narrow #1737 to make such a model translate.** A test pins the refusal.
- **REPLAN** if any golden changes for a reason other than this shape, or if the fix needs to touch `_sum_should_collapse`'s full-collapse branch (that is #1776's territory, and would mix the two defects).
- **Out of scope:** #1776 (equal binder/index counts, the `else`/full-collapse side). It shares the function and a future binder→position helper, but not this gate.

## Phase 0 results (Sprint 40 Day 5): PROCEED, with one finding routed

**The fix:** `_diff_sum_repeated_binder` (`src/ad/derivative_rules.py`), called at the end of the single-binder loop, only after every existing attempt returned zero. It places the binder at every position it occupies, but only when the `wrt` values there are equal (case-insensitively for the spelling), then substitutes it back. The result is the **whole** derivative: every distinct layout once, plus the summed remainder (PR #1779 review round 1).

| criterion | result |
|---|---|
| fail-before, at the layer | `d sum(i, tsam(i,i)) / d tsam('i1','i1')` was `Sum((i), Const(0.0))`; now `Const(1.0)` |
| **positive control** | the off-diagonal `('i1','i2')` stays 0, as do `w(i,i,i)` at `('i3','i3','i1')` and `v(i,i,'k1')` at `('i1','i1','k2')` |
| scalar variant, emit | `stat_tsam(i,j).. 2 * tsam(i,j) + nu_diag$(<the diagonal>) =E= 0;` with `diag.nu_diag` paired: **the hand-derived row** |
| scalar variant, **solve** | PATH MS 1 at **0.333**, against the NLP's 0.3333 |
| reproducer, emit | `diagsum` and `nu_diagsum` present and paired; `nu_diagsum` on the diagonal only; no `1 =E= 0` |
| #1737 | shape (a) `dd(i,i).. sum(j, tsam(j,j)) =e= 1` is now **refused** (it was silently dropped). Pinned. #1737 untouched |
| leak gate | `make check-goldens`, alone: **200 in-scope goldens, all clean**, rc 0 with `--fail-on-unverified`. **Byte-identical corpus-wide**, as predicted |
| `check-index-repeats` | P1 0 / 3,370; P2 11 = baseline |
| mutation controls | revert the fix: 12 of 13 tests fail (round 1's count); drop the equal-values condition: the positive control fails; exact spelling instead of case-insensitive: the case test fails; drop the summed remainder, keep only the first layout, or stop deduplicating layouts: each fails its mixed-reference test; key layouts by spelling, or merge no spellings: the mixed-case test fails (review round 2) |

**PR #1779 review: the result is the WHOLE derivative.** The first revision returned the first matching layout's collapsed contribution alone. With mixed references that dropped the rest:
- `sum(i, x(i,i) + x('i1','i1'))` at `x('i1','i1')` gave **1, not 4**. The concrete reference's summed contribution (3) was lost. On `main` the fallthrough gave 3, so this was a regression in that shape.
- `sum(i, w(i,i,'i1') + w('i1',i,i))` gave **1, not 2**.

The helper now sums **every distinct layout once**, plus the **summed remainder** (exactly the caller's normal case). **Round 2:** a layout is keyed by the canonical binder spelling, because index matching is case-insensitive. `w(i,i,i)` and `w(i,I,i)` are one layout, and their spellings are merged for substitution. Keyed by spelling, they counted 4, not 2. **Round 3:** the binder's spellings are collected across the whole body and condition, not only from the variable's references (`c(I)` alone was left). Each layout's **condition** is substituted with that layout's own value (`active('i1') + active('i2')`). ⚠ The stationarity layer still maps that concrete condition back to the first domain position, so the end-to-end result for such shapes stays wrong. That is recorded on #1778; it is not an AD defect. **Round 4:** the equal-values check compares the way `_indices_match` does (quotes stripped, case-insensitive), so `('i1','I1')` and `('i1',"'i1'")` are the diagonal; the substitution keeps the set-member spelling. **Round 5:** a fully noncanonical target (`('I1','I1')`) resolves to the **declared** member spelling. `_is_structurally_zero` recognizes a guarded zero `0$cond`, so a body-level `$` condition no longer ends the single-binder loop before the fallback. That change reaches all 5 `_is_structurally_zero` call sites, and the leak gate is byte-identical. **Round 6:** a quotient with a zero numerator is recognized as zero. Each layout is differentiated against a fresh placeholder for the binder, so a quoted label spelled like the binder (`x('i','i')`) is no longer counted. ⚠ A **target** spelled like the binder stays ambiguous, as it is on `main`. **Round 7:** a `Sum` with a structurally zero body is zero (not `Prod`: an empty product is 1), so a nested zero-derivative sum no longer ends the loop early. The two parts are disjoint. Regressions cover both cases, plus a shared-layout case that must not double-count; each is judged on its **value**.

- ⚠ **A related pre-existing limitation, out of scope:** the #1086 loop *before* the helper returns its **first** non-zero attempt. So `sum(i, x(i,'i1') + x(i,i))` still gives 1, not 2, the same as on `main`. Filed as **#1780**: changing that loop needs its own gate.

**Where the measurement differed from the prediction (recorded, not smoothed over):**

1. **The indexed reproducer's row is not the hand-derived one.** AD now returns 1 for every `j`, but the stationarity row aggregates the cross-instance multipliers wrongly: at `(i1,i1)` it gives `2·nu_diagsum(i1)`, not `nu_diagsum(i1)+nu_diagsum(i2)+nu_diagsum(i3)`. **That is a separate, pre-existing defect, filed as #1778.**
   - A reproducer with **no** repeated binder (`e(j).. sum(i, tsam(i,'i1')) =e= 1`) emits byte-identically on an untouched `main` and solves to a **wrong 0.375** against an NLP of 0.3333.
   - Its guard `nu_e(i)$(ord(i) = k)` looks like the phantom-IndexOffset family (#1381/#1714): a hypothesis, not traced.
   - It is latent in the corpus (0 goldens match the shape). #1755's own criteria are met; its pass-after named the diagonal placement and the scalar solve, both of which hold.
2. **A pinned reachability claim became live.** `test_pattern_c_alias_offset_gate.py` asserted that a diagonal reference *never* reaches Pattern-C B-3. Because #1755 makes the reference differentiate, B-3 is now consulted and **declines** (returns `None`). The test now asserts "reached and declined", and the change is recorded in ISSUE_1741.
   - ⚠ Measured by mutation: #1741's own guard is not the only decliner for that fixture.

**Out of scope, unchanged:** #1776, the equal-count `_diff_sum` sibling.

## A related corpus case: egypt — a SIBLING, now #1776 (Sprint 40 Day 4, 2026-10-20)

- egypt's `landb(r,tm).. sum((c,z)$zr(z,r), xcrop(r,c)*land(c,z,tm)) =l= …` gets **0 Jacobian entries**, and `landb`, `waterb` and their multipliers vanish from `egypt_mcp.gms`. `labbal` silently loses its `xcrop` terms.
- **The outcome is this issue's** (derivative 0, constraint dropped), **but the gate is different.**
  - `_sum_should_collapse` returns False both for egypt's two-binder sum and for a working one-binder variant, so the collapse decision is not where they diverge.
  - The divergence is in `_diff_sum`: its partial-index-match branches are gated on `len(wrt) > len(binders)` and `<`. Equal counts (2 and 2) fall through to an assumed positional correspondence.
- Filed with a 10-line reproducer and the instrumented trace as **#1776**.
- Both need the same thing, a binder→position map built from the reference's index positions, so one helper may serve both. That makes P7 the natural owner of #1776 too.

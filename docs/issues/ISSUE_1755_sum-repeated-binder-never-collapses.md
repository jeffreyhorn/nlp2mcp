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

## A related corpus case: egypt — a SIBLING, now #1776 (Sprint 40 Day 4, 2026-10-20)

- egypt's `landb(r,tm).. sum((c,z)$zr(z,r), xcrop(r,c)*land(c,z,tm)) =l= …` gets **0 Jacobian entries**, and `landb`, `waterb` and their multipliers vanish from `egypt_mcp.gms`. `labbal` silently loses its `xcrop` terms.
- **The outcome is this issue's** (derivative 0, constraint dropped), **but the gate is different.**
  - `_sum_should_collapse` returns False both for egypt's two-binder sum and for a working one-binder variant, so the collapse decision is not where they diverge.
  - The divergence is in `_diff_sum`: its partial-index-match branches are gated on `len(wrt) > len(binders)` and `<`. Equal counts (2 and 2) fall through to an assumed positional correspondence.
- Filed with a 10-line reproducer and the instrumented trace as **#1776**.
- Both need the same thing, a binder→position map built from the reference's index positions, so one helper may serve both. That makes P7 the natural owner of #1776 too.

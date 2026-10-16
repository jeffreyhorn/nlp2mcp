# ISSUE #1755 — a sum whose reference repeats its binder never collapses (derivative 0, constraint dropped)

**GitHub:** [#1755](https://github.com/jeffreyhorn/nlp2mcp/issues/1755) · **Status:** 🔴 **OPEN** — filed Sprint 40 Prep Task 10 (2026-10-15)
**Layer:** **AD** — `src/ad/derivative_rules.py::_sum_should_collapse`, called from `_diff_sum` (traced by instrumentation; see below)
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

**Scope:** no committed golden contains a non-zero constant-only stationarity row, so the pattern is latent in the corpus. But a dropped term in a row that has other terms would not show up in that grep.

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

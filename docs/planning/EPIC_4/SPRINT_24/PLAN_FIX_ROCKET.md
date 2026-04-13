# Plan: Fix rocket Jacobian Explosion (#1134)

**Goal:** Fix the dense Jacobian bug so rocket's stationarity equations
are sparse (2–3 `nu_v_eqn` terms per variable, not 52), enabling
cold-start PATH convergence without requiring `--nlp-presolve`.

**Issue:** [#1134](https://github.com/jeffreyhorn/nlp2mcp/issues/1134)
**Estimated effort:** 3–5 hours
**Models unblocked:** rocket (and any model with lag-indexed equations +
auxiliary variables — potentially chain, others with `h-1`-style domains)

---

## Current State

The rocket model **translates and solves** today, but only via the
`--nlp-presolve` warm-start workaround (STATUS 2 Locally Optimal,
obj=1.0128, matching the NLP reference).  The underlying stationarity
equations are **mathematically wrong**: each auxiliary variable's
stationarity has 52 `nu_v_eqn` terms instead of the correct 2–3.

### The Model

Goddard rocket trajectory optimization (COPS benchmark #10):
- 51 discretization intervals (`h0..h50`)
- 8 variables: `final_velocity`, `step`, `v(h)`, `ht(h)`, `g(h)`, `m(h)`, `t(h)`, `d(h)`
- 6 equations: `obj`, `df(h)`, `gf(h)`, `h_eqn(h-1)`, `m_eqn(h-1)`, `v_eqn(h-1)`

The three dynamics equations use **lag indexing** (`h-1`):
```gams
h_eqn(h-1).. ht(h) =e= ht(h-1) + .5*step*(v(h) + v(h-1));
m_eqn(h-1).. m(h)  =e= m(h-1) - .5*step*(T(h) + T(h-1))/c;
v_eqn(h-1).. v(h)  =e= v(h-1) + .5*step*((T(h) - D(h) - m(h)*g(h))/m(h)
                              + (T(h-1) - D(h-1) - m(h-1)*g(h-1))/m(h-1));
```

### The Bug

`v_eqn(h-1)` references `g(h)` and `g(h-1)` — only 2 instances of `g`
per equation instance.  The Jacobian `∂v_eqn/∂g` should be:

| Condition | Derivative |
|-----------|-----------|
| `h' = h` (same index) | `−0.5 * step / m(h)` |
| `h' = h+1` (lag reference) | `−0.5 * step / m(h-1)` |
| otherwise | 0 |

**Correct stationarity** (`stat_g(h)`, 2–3 terms):
```gams
stat_g(h).. nu_gf(h)
  + (-0.5*step/m(h)) * nu_v_eqn(h)
  + (-0.5*step/m(h))$(ord(h) < card(h)) * nu_v_eqn(h+1)
  - piL_g(h) =E= 0;
```

**Actual output** (`stat_g(h)`, 52 terms):
```gams
stat_g(h).. nu_gf(h)
  + (...) * nu_v_eqn(h)
  + (...) * nu_v_eqn(h-1)$(ord(h) > 1)
  + (...) * nu_v_eqn(h-2)$(ord(h) > 2)
  ...
  + (...) * nu_v_eqn(h-50)$(ord(h) > 50)
  - piL_g(h) =E= 0;
```

The same 52-term explosion affects `stat_d(h)`, `stat_m(h)`, `stat_t(h)`,
and `stat_v(h)`.

### Why the Bug Happens

The AD pipeline works in two phases:

1. **Jacobian computation** (`src/ad/constraint_jacobian.py`): Substitutes
   symbolic indices with concrete elements (h→h27), resolves offsets
   (h27−1→h26), then differentiates.  The **concrete-level Jacobian is
   correct** — only truly non-zero entries are stored.

2. **Stationarity assembly** (`src/kkt/stationarity.py`,
   `_add_indexed_jacobian_terms()`): Reconstructs indexed equations from
   the concrete entries.  For each variable column, it loops through ALL
   equation rows and collects non-zero entries.  It then groups entries by
   offset pattern and emits one term per group.

The problem is in phase 2: when the code finds non-zero entry
`∂v_eqn(h20)/∂g(h27)`, it computes the offset as `h27 − h20 = +7` and
emits `nu_v_eqn(h-7)`.  But this entry only exists because **one specific
concrete instance** happened to have a cross-reference — the equation
`v_eqn(h20)` references `g(h20)` and `g(h19)`, not `g(h27)`.  The
concrete Jacobian correctly has `∂v_eqn(h20)/∂g(h27) = 0`, but
`∂v_eqn(h27)/∂g(h27) ≠ 0`, and the assembly treats the offset pattern
from *any* instance as valid for the *indexed* equation.

In other words: the code sees that *somewhere* in the 51×51 matrix,
`v_eqn` has a non-zero derivative w.r.t. `g` at every offset from 0 to
−50 (because diagonal entries exist at each shift), and emits all of them.

---

## Fix Strategy

### Approach: Instance-Filtered Offset Groups

The fix is in `_add_indexed_jacobian_terms()`.  When building offset
groups for a constraint, **validate each offset against the expected
sparsity pattern** from the concrete Jacobian:

1. For each (equation_instance, variable_instance) pair with a non-zero
   derivative, compute the index offset.
2. Group entries by offset.
3. For each offset group, check: does this offset correspond to a
   **structural** dependency (i.e., does the equation template actually
   reference the variable at this offset)?
4. Filter out spurious offset groups that arise from coincidental
   concrete-element overlaps.

### How to Detect Structural Dependencies

An offset is **structural** if, for the majority of equation instances,
the derivative at that offset is non-zero.  A spurious offset appears
only for a small number of instances (typically 1).

For rocket's `v_eqn/g`:
- Offset 0: `∂v_eqn(hi)/∂g(hi)` is non-zero for **all 50** equation instances → structural
- Offset +1: `∂v_eqn(hi)/∂g(hi+1)` is non-zero for **49** instances → structural (lag)
- Offset −7: `∂v_eqn(hi)/∂g(hi−7)` is non-zero for **0** instances → spurious

Wait — if the concrete Jacobian is correct (only 2 non-zero entries per
row), then the offset analysis should already show that offset 0 has 50
entries, offset +1 has 49 entries, and all other offsets have 0 entries.
The bug must be that the assembly code is **not correctly computing
offsets** or is **not filtering by instance count**.

### Diagnostic Step (30 min)

Before coding the fix, add instrumentation to `_add_indexed_jacobian_terms()`
to dump the offset groups for `v_eqn/g`:

```python
if eq_name == "v_eqn" and var_name_base == "g":
    for offset, entries in offset_groups.items():
        print(f"  offset={offset}: {len(entries)} entries")
```

This will reveal whether the problem is:
- **(A)** The concrete Jacobian has too many non-zero entries (bug in AD), or
- **(B)** The offset computation is wrong (bug in assembly), or
- **(C)** The filtering is missing (assembly emits all offset groups regardless of count)

---

## Implementation Plan

### Phase 1: Diagnose (30 min)

1. Add debug logging to `_add_indexed_jacobian_terms()` for the rocket
   model's `v_eqn/g` pair
2. Print offset groups with entry counts
3. Identify whether the root cause is (A), (B), or (C) above

### Phase 2: Fix Stationarity Assembly (2–3h)

Based on diagnosis, implement the appropriate fix:

**If (C) — missing filter (most likely):**

In `_add_indexed_jacobian_terms()`, after computing offset groups, filter
to retain only **structural** offsets.  An offset is structural if the
number of instances with non-zero derivatives at that offset is at least
`max(1, total_instances / 2)` (majority rule).  This distinguishes:

- Offset 0 (50 instances) → structural → keep
- Offset +1 (49 instances) → structural → keep
- Offset −k for k≥2 (0–1 instances) → spurious → drop

The threshold handles edge cases:
- Boundary elements (h0, h50) naturally have fewer instances for lag
  offsets, so the majority count for offset +1 is 49 not 50
- A single-element equation (degenerate) still passes with threshold 1

**If (B) — wrong offset computation:**

Fix the offset calculation to use the equation's domain element relative
to the variable's domain element, accounting for the equation's own lag
index.  The equation `v_eqn(h-1)` is stored as row `("v_eqn", ("h1",))`
— the h-1 domain has already been resolved.  The offset from variable
`g(h27)` to equation `v_eqn(h26)` should be computed as:
`eq_index − var_index = h26 − h27 = −1`, but the correct structural
offset is `0` (same `h`) and `+1` (lag reference).  This discrepancy
needs investigation.

**If (A) — incorrect AD:**

The AD engine incorrectly resolves offset references during
differentiation.  This would require fixes in
`src/ad/constraint_jacobian.py`, specifically in `_resolve_index_offsets()`
or `_substitute_indices()`.

### Phase 3: Verify (30 min)

1. Retranslate rocket and check stationarity sparsity:
   ```bash
   python -m src.cli data/gamslib/raw/rocket.gms -o /tmp/rocket_mcp.gms
   grep "stat_g(h)\.\." /tmp/rocket_mcp.gms | tr '+' '\n' | grep -c "nu_v_eqn"
   # Expected: 2 or 3 (was 52)
   ```

2. Solve without `--nlp-presolve`:
   ```bash
   gams /tmp/rocket_mcp.gms lo=2
   # Expected: MODEL STATUS 1 or 2
   ```

3. Verify objective matches NLP reference (1.0128)

4. Run `make test` — ensure no regressions

5. Run pipeline retest on affected models:
   ```bash
   .venv/bin/python scripts/gamslib/run_full_test.py --model rocket --verbose
   ```

### Phase 4: Check Other Models (30 min)

Other models with lag-indexed equations may benefit from this fix:
- `chain` — uses lag-indexed constraints
- Any model currently requiring `--nlp-presolve` that has lag domains

Run the full pipeline and compare solve counts before/after.

---

## Files to Modify

| File | Change |
|------|--------|
| `src/kkt/stationarity.py` | Filter offset groups in `_add_indexed_jacobian_terms()` |
| `src/ad/constraint_jacobian.py` | Possibly fix offset computation (depends on diagnosis) |
| `tests/unit/kkt/` | Add test for lag-indexed constraint stationarity sparsity |
| `docs/issues/ISSUE_1134_*` | Update status to FIXED |

---

## Success Criteria

- [ ] `stat_g(h)` has 2–3 `nu_v_eqn` terms (not 52)
- [ ] `stat_d(h)` has 2–3 `nu_v_eqn` terms (not 52)
- [ ] `stat_m(h)` has 2–3 `nu_v_eqn` terms (not 52)
- [ ] `stat_t(h)` has 2–3 `nu_v_eqn` terms (not 52)
- [ ] `stat_v(h)` has 2–3 `nu_v_eqn` terms (not 52)
- [ ] rocket solves to MODEL STATUS 1 or 2 **without** `--nlp-presolve`
- [ ] Objective matches NLP reference (1.0128) within tolerance
- [ ] Multi-pattern warnings for `v_eqn/t` and `v_eqn/v` resolved
- [ ] No test regressions (`make test` passes)
- [ ] No pipeline regressions (solve count ≥ current)

---

## Related Issues

- **#1131** (FIXED): Missing sameas guard on objective gradient for rocket
  — same class of bug, but in the gradient rather than the Jacobian
- **#1134** (OPEN): This issue — Jacobian explosion from lag-indexed equations
- **#757/#1199**: bearing infeasibility — different root cause (convergence,
  not Jacobian structure), fixed via `--nlp-presolve`
- **#1049**: pak sameas guard — similar guard pattern, but for fixed literal
  indices rather than lag offsets

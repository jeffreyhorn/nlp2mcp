# ISSUE #1741 — a repeated index in a B-3 reference collapses every position lookup

**GitHub:** [#1741](https://github.com/jeffreyhorn/nlp2mcp/issues/1741) · **Status:** 🟢 **GUARDED** (Sprint 39 Day 11) — latent defect, no corpus model triggers it
**Layer:** **KKT / stationarity** — `src/kkt/stationarity.py`, `_build_pattern_c_dim_mismatch_term` (the Pattern-C B-3 builder)
**Measured at:** `90b43e1e` · GAMS **54.2.1**

## Problem

`_pos` resolves a symbol to a position in the reference's index tuple by
returning the **first** match:

```python
def _pos(sym: str) -> int | None:
    for k, ix in enumerate(src_indices):
        if isinstance(ix, str) and ix.lower() == sym.lower():
            return k
    return None
```

For a diagonal reference such as `X(i,i)` every lookup returns `0`, so
`sum_position` and the single `bindings[eqi]` land on the **same** coordinate and
B-3 consolidates against a binding the source never expressed.

This is the survey's `stationarity._pos` site (`POSITIONAL_DOMAIN_SURVEY.md`,
**NEEDS A GUARD**, reach 2/15). It is the symbol→position step the survey names
as the discriminator — not positional indexing, which is repeat-safe.

⚠ **The survey cites this site as `stationarity.py:1091`/`:1104`. Those line
numbers have since aged out** — `:1091` is now inside `_find_full_collapse_sum`.
The site was relocated by symbol (`_pos`, `bindings`), which is how it should be
cited from here on.

## Phase 0: Acceptance Gate

### Layer

`src/kkt/stationarity.py` — the guard sits in `_build_pattern_c_dim_mismatch_term`
immediately after `src_indices = var_ref.indices`, before `_pos` is defined, so
no position lookup can run against a collapsing tuple.

### Nearest Existing Mechanism

**Nearest:** `src/ir/index_map.py` (`assert_no_repeated_symbol` / `build_index_map`,
issue #1737, Sprint 39 Day 9) — same defect *class*, a repeated symbol silently
losing a position.

**Why it does not apply here, and why the remedy differs:**

1. **It raises; this site must not.** `index_map` raises because it has no correct
   fallback: a collapsed map has no honest value to return. This builder's
   contract is *"return `None` and the caller takes the standard path"*, and the
   standard path handles the general case correctly. Declining a special case is
   always safe; refusing to emit is not.
2. **It is equation-domain-keyed; this is a VarRef's index tuple.** `index_map`
   guards a *domain* being bound to an instance. Here the repeat is in a
   reference's argument list inside an equation body — a diagonal *usage*, which
   `dedupe_repeated_variable_domains` (`src/kkt/repeated_domain.py`, #1062) does
   not touch: that rewrites repeated symbols in variable **declaration** domains.

**Also considered and rejected:** widening the existing `len(bindings) != 1`
bail-out. It answers a different question (how many eq-domain indices bind), and
`len(bindings) == 1` is exactly the collapsing case — so widening it would
either miss this or reject the supported cesam2 shape.

### Hand-Derived KKT Shape

**Unchanged — and that is the acceptance criterion.** This is a *defensive*
change: it converts a silently wrong consolidation into a fallback onto the
standard path. No stationarity row, multiplier, complementarity pair or bound may
differ for any model that translates today.

The derivation is therefore **negative**: for every corpus model the guard's
condition is **false**, so `_build_pattern_c_dim_mismatch_term` returns exactly
what it returned before.

### Expected Emit Pattern

**BYTE-IDENTICAL corpus-wide.** No new emitted construct. `make check-goldens`
must report **186 in-scope, all clean, 0 drifted**; any drift is a failure and
means a corpus model *was* reaching B-3 through a collapsed binding.

On a model that does carry a diagonal B-3 reference, the expected behaviour is
the **standard path's** emit — not an error, and not the B-3 consolidated form.

### Verification Methodology

1. **Fail-before at the defect itself**, asserted on `_pos`'s own arithmetic, so
   the guard cannot later be read as redundant: `_pos('i')` over `('i','i')` is
   `0`; `len(bindings) == 1`, so the existing bail-out does **not** fire; and
   `sum_position == binding_position`.
2. **Shape coverage.** Adjacent repeat `('i','i')` and a case-only repeat
   `('i','I')` — GAMS identifiers are case-insensitive, so both are repeats.
3. **⚠ A POSITIVE control that the guard does not disable B-3.** A distinct
   `('i','j')` reference must get **past** this guard — asserted by spying on the
   next call (`_b3_multiplier_ref_is_valid`), because every other assertion in
   the test is `is None` and would pass vacuously against a guard that declined
   everything.
4. **Emit invariance.** `make check-goldens` → **186 clean, 0 drift**, run
   **uncontended** (a contended run reports unverified timeouts and silently
   narrows scope — this sprint hit that twice).
5. **⚠ Scope, not just verdict.** State how many models could reach the guard
   (**0** today) alongside the pass, so a future reader can tell a real pass from
   an unexercised one.

### PROCEED/REPLAN Signal

**PROCEED** — `check-goldens` **186 clean, 0 drift, uncontended**; the guard
declines both repeat shapes and neither distinct shape; full suite green.

**REPLAN** if any of:

- **any golden drifts.** A defensive change has no emit improvement to trade
  against; one drifted byte means a corpus model was relying on the collapsed
  binding, and the correct fix is then diagonal handling, not a fallback.
- **the guard rejects a distinct-symbol reference.** That would disable B-3 and
  regress cesam2's consolidated form to the standard path.
- **the guard is reached in a hot loop.** It is O(arity) per B-3 candidate; if a
  profile shows it mattering, the cost must be measured before accepting it.

### Bucket / KPI

**0 bucket, no KPI movement.** No model changes status: the guard is unreachable
with current corpus data, which is precisely why it can land safely.

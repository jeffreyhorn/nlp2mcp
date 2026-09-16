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
reach 2/15) — **catalogued `NEEDS A GUARD` at prep, and recorded ✅ GUARDED
there since Day 11 by this very change**. The prep-era verdict is quoted as
history, not as an open obligation (PR #1742 review). It is the symbol→position
step the survey names as the discriminator — not positional indexing, which is
repeat-safe.

⚠ **The survey cites this site as `stationarity.py:1091`/`:1104`. Those line
numbers had already drifted `+293` before this issue was opened** — Day 8
measured it (PR #1728 inserted B-4's ~256 lines at ~1004) and `:1091` now lands
inside `_find_full_collapse_sum`. Day 11 hit the same wall again, which is why
the remedy here is an **address format**, not another measurement: cite this site
by SYMBOL (`_pos`, `bindings`).

⚠ **A REPEATED `eq_domain` COLLAPSES INDEPENDENTLY, and needs its own check**
(PR #1742 review — the first revision of this guard missed it). `bindings` is a
**dict keyed by the eq-domain symbol**, so `eq_domain=("i","i")` writes the same
key twice: `len(bindings)` stays 1, the `!= 1` bail-out does not fire, and B-3
proceeds as though the equation had one index. The reference guard cannot catch
this — it inspects `src_indices`, and the two collapse independently.

⚠⚠ **The two checks must NOT be merged into one list.** `src_indices` and
`eq_domain` legitimately **share** symbols — that overlap is B-3's whole premise,
the equation index binding one coordinate of a higher-dimensional variable.
cesam2 is `src_indices=("i","j")` with `eq_domain=("i",)`; concatenated that is
`["i","j","i"]`, so a merged repeat test **rejects the case the builder exists to
serve**. Measured, and pinned by an anti-merge control in the test.

⚠ **MEASURED ORDERING: the `eq_domain` half is defence in depth behind an
earlier raise.** A repeated EQUATION domain raises at the Day-9 `#1737` guard
(`empty_equation_detector`'s `assert_no_repeated_symbol`) **before** B-3 is
consulted, and a diagonal VARIABLE reference never reaches B-3 at all — the
builder is called **0 times** for such a model. So this half is not reachable
end-to-end today; it holds if a future caller reaches the builder without going
through the empty-equation scan.

Both facts are **COUNTED, not narrated** —
`test_b3_is_never_reached_by_either_repeat_shape` spies on
`_build_pattern_c_dim_mismatch_term` and asserts the call count is **0** for each
shape. ⚠ A `pytest.raises` alone does NOT establish the ordering: it passes
unchanged if B-3 runs first and the raise arrives afterwards (PR #1742 review —
an earlier revision of that test claimed both facts while establishing neither,
and its fixture used `tsam(i,j)`, which is not a diagonal reference at all). The
counter runs against a **non-vacuity control** on cesam2 first, because a spy
that was never wired reads 0 exactly like a real zero. Mutation-checked:
disabling the `#1737` guard fails the ordering assertion, and unwiring the spy
fails the control.

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

> ✅ **SATISFIED on Sprint 39 Day 11 — this section is the gate as written
> BEFORE the work, kept in acceptance-gate voice** (the Phase-0 format requires
> this heading, and `ISSUE_1737` is written the same way). Recorded outcome:
> **PROCEED** — `check-goldens` **186 in-scope, all clean, 0 drift, uncontended**;
> `make test` **5431 passed**, 10 skipped, 1 xfailed; none of the REPLAN exits
> fired. Read the conditions below as the criteria that were applied, not as
> work still pending (PR #1742 review).

**PROCEED** — `check-goldens` **186 clean, 0 drift, uncontended**; the guard
declines every repeat shape (repeated reference, repeated `eq_domain`, and the
case-only variants) and **lets a distinct-symbol reference through to the rest
of the builder**, which is what the positive control asserts — it may still
return `None` further down for unrelated reasons, and that is not this guard's
doing (PR #1742 review: an earlier wording said *"declines … neither distinct
shape"*, which reads as a failed positive control). Full suite green.

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

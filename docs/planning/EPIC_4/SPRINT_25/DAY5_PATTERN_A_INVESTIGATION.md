# Sprint 25 Day 5 — Phase 1 Pattern A Investigation (Evidence-Driven)

**Branch:** `sprint25-day5-pattern-a-investigation`
**Date:** 2026-04-24
**Purpose:** Identify the ACTUAL failure shape of qabel, abel, launch (the three
Phase 1 targets the Day 3 mechanical port of `_find_var_indices_in_body` into
`_partial_collapse_sum` failed to move). Traces captured at
`/tmp/sprint25-day5/{qabel,abel,launch}_trace.stderr` (231k / 3k / ~21k lines)
under `SPRINT25_DAY2_DEBUG=1`.

## Repro

The `/tmp/sprint25-day5/` paths below are ephemeral scratch; to regenerate
the three traces + emitted MCPs:

```bash
mkdir -p /tmp/sprint25-day5
for m in qabel abel launch; do
  SPRINT25_DAY2_DEBUG=1 .venv/bin/python -m src.cli \
    data/gamslib/raw/${m}.gms \
    -o /tmp/sprint25-day5/${m}_mcp.gms \
    --skip-convexity-check --quiet \
    2> /tmp/sprint25-day5/${m}_trace.stderr
done
```

The `SPRINT25_DAY2_DEBUG=1` env var activates `[SPRINT25_DAY2]` trace
lines in `src/ad/derivative_rules.py::_diff_varref` and
`_partial_collapse_sum`; greppable by the `[SPRINT25_DAY2][<tag>]` prefix.

---

## TL;DR

None of the three Phase 1 targets exhibits a Pattern A bug. Their rel_diff
mismatches come from **KKT stationarity assembly**, not the AD layer:

- **qabel, abel (rel_diff 0.08, 0.30):** AD criterion derivative is
  byte-correct (symmetric quadratic form). The mismatch — if it's a real
  bug at all — lives in the stateq Lagrangian term's sign / offset /
  domain-condition handling (uses `nu_stateq(n, k-1)` with `$(ord(k) > 1)`
  where a naïve formulation would expect `nu_stateq(n, k)` with
  `$(ord(k) >= 2)`; the emitter's declared domain for `nu_stateq` is
  `(n, k)` shifted vs. the formal `(n, k+1)`, so the `k-1` may be
  deliberate — needs end-to-end solve to confirm, not action=c).

- **launch (rel_diff 0.17):** Stationarity emitter invents IndexOffset
  shifts on an alias that has none in the source. `stat_iweight` emits
  `nu_dweight(s+1)`, `(s+2)`, `(s-1)`, `(s-2)` — none of which appear in
  the original `dweight(s).. weight(s) =e= sum(ss$ge(ss,s), ...)`. This is
  **Pattern C** (alias-of-IndexOffset, originally deferred to Days 7–9
  in the pre-pivot plan — now promoted to Day 6 per the revised Sprint 25
  schedule in `PLAN.md`) manifesting during KKT assembly as an "expand
  the alias via ±N offsets" strategy.

**Gate 2 (speculated Day 6+): NO-GO for Phase 2 in its original shape.**
The Phase 1 hypothesis (`_partial_collapse_sum` recovery helps multi-index
alias cases) is orthogonal to the actual bug surface. Defer the alias
workstream to Pattern C. Phase 2's "broader Pattern A rollout" should be
dropped from the sprint.

---

## Evidence — AD layer is correct (qabel / abel)

qabel and abel share the same criterion shape:

```gams
criterion..
  j =e= .5 * sum((k, n, np), (x(n,k) - xtilde(n,k))
                             * w(n, np, k)
                             * (x(np, k) - xtilde(np, k)));
```

Expected derivative w.r.t. `x(n_row, k_row)`:

```text
∂j/∂x(n_row, k_row)
  = 0.5 * (sum(np, w(n_row, np, k_row) * (x(np, k_row) - xtilde(np, k_row)))
         + sum(n,  (x(n, k_row) - xtilde(n, k_row)) * w(n, n_row, k_row)))
```

Emitter output for abel's `stat_x(n, k)` criterion portion:

```gams
0.5 * (sum(np__, (x(np__,k) - xtilde(np__,k)) * w(n, np__, k))
     + sum(n__,  (x(n__,k)  - xtilde(n__,k))  * w(n__, n, k)))
```

Byte-for-byte match to the expected form (with `np__`/`n__` being the
Sprint 24 renamed remaining sum indices). Confirmed via Day 2
`SPRINT25_DAY2_DEBUG` trace: `_partial_collapse_sum` enumerates both
alias matchings, recovery doesn't fire (body's indices already match
the sum's own names), substitution emits correctly.

**The criterion-level AD is correct.** Day 3's port doesn't help because
there's nothing to help — qabel/abel aren't blocked by Pattern A.

## Evidence — KKT stateq term on qabel/abel

The non-criterion portion of `stat_x(n, k)` in both models:

```gams
+ ((-1) * a(n,n)) * nu_stateq(n,k)
+ (((-1) * a(n+1,n)) * nu_stateq(n+1,k))$(ord(n) <= card(n) - 1)
+ nu_stateq(n, k-1)$(ord(k) > 1)
+ (((-1) * a(n-1,n)) * nu_stateq(n-1,k))$(ord(n) > 1)
```

Notes:

- `nu_stateq` is declared as `nu_stateq(n, k)` even though the formal
  domain of `stateq` is `(n, k+1)`. The emitter indexes the multiplier by
  the pre-shift k, so `nu_stateq(n, k-1)$(ord(k) > 1)` is consistent with
  the "formal row t = k+1, nu indexed by k = formal_k" convention.
- The three `a(n±0, n) * nu_stateq(n±0, k)` terms together sum over all
  `n_e ∈ n` by enumeration (card(n)=2 for abel; the ±1 shifts plus the
  identity case cover both elements). Mathematically acceptable for this
  specific set cardinality, but the strategy is fragile.

I can't verify rightness at compile-time (the GAMS `action=c` compile on
ganges/qabel/abel throws pre-existing Error 141 cascades on dual-transfer
lines — unrelated to this analysis). A full PATH solve is the only
ground truth for whether the current stat_x is numerically correct.

**Tentative conclusion:** qabel/abel may be "correct but nonconvex +
poor init" (rel_diff from solver behavior, not emission) OR may have a
subtle sign/condition bug in the stateq term. Either way, **Pattern A
fix in `_partial_collapse_sum` is irrelevant.**

## Evidence — launch's `stat_iweight` is malformed (NOT Pattern A)

Source — the `dweight` equation definition in `data/gamslib/raw/launch.gms`
(the `data/gamslib/raw/` directory is gitignored; the file is downloaded
via `scripts/download_gamslib_raw.sh`. Grep `^dweight\b` in the source to
locate):

```gams
dweight(s)..  weight(s) =e= sum(ss$ge(ss,s), iweight(ss) + pweight(ss))
                            + instweight + pl;
```

One alias (`ss` aliases `s`), one conditional sum. No IndexOffset.

Emitter output (`stat_iweight` body):

```gams
 iwf(s) * nu_diweight(s)
+ sum(ss, ((-1) * 1$(ge(ss,s))) * nu_dweight(s))
+ sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s+1))$(ord(s) <= card(s) - 1))
+ sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s+2))$(ord(s) <= card(s) - 2))
+ sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s-1))$(ord(s) > 1))
+ sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s-2))$(ord(s) > 2))
 ...
```

Two bugs visible in the emission:

1. **Phantom IndexOffsets on `s`.** The source has `sum(ss$ge(ss,s), ...)` — a
   conditional sum over the alias `ss`, not any lead/lag shifts. But the
   emitter produces five copies of the term indexed by `s+0, s+1, s+2,
   s-1, s-2`, presumably trying to enumerate all possible alias bindings
   via ±N offsets (card(s)=5 for launch's `stages` set). This is
   **Pattern C** (alias-of-IndexOffset from the AUDIT) manifesting in the
   KKT stationarity emitter.

2. **Mis-scoped `$(ge(ss, s))` condition inside an outer sum.** Each of
   the five `sum(ss, ...)` clauses still has `1$(ge(ss, s))` in the body
   referencing the sum variable `ss`. But the body multiplies by
   `nu_dweight(s+N)` (or `(s)`/`(s-N)`), which doesn't depend on `ss` at
   all. Result: the sum over `ss` degenerates into `card(ss-satisfying-ge) *
   nu_dweight(s±N)` — a spurious multiplicative factor vs. the expected
   single-term contribution `$(ge(ss, s))` acting as a gate.

**Pattern A fix in `_partial_collapse_sum` doesn't touch any of this.**
The bugs are in KKT stationarity assembly, not AD.

---

## Gate decision — Sprint 25 shape

Per the Day 5 investigation outcome, pivot WS1 to Pattern C:

### Day 5 outcome (today)
Investigation complete. Phase 1 hypothesis disproved on all three
target models. AD layer is correct. Bugs live in KKT stationarity
assembly (Pattern C + alias-as-offset enumeration).

### Recommended Day 6–9 plan

1. **Day 6**: Pivot to Pattern C in KKT emit/stationarity. Target:
   launch's `stat_iweight` phantom-offset generation. Reproduce
   minimally, locate the enumeration code, prototype a gate that
   only runs when the source has an actual IndexOffset.
2. **Day 7**: Validate on launch + regression sweep (54 models + the
   deferred multi-solve cluster from the AUDIT). Document rel_diff
   impact if any.
3. **Day 8**: Revisit qabel/abel stateq term — run a full PATH solve
   (not `action=c`) and measure rel_diff post-Day-6-fix. If
   unchanged, their rel_diff is nonconvex-solver noise, not an
   emission bug.
4. **Day 9+**: WS2 emitter batch 3 (remaining `ANALYSIS_RECOVERED_TRANSLATES`
   priorities) — independent of Pattern A/C.

### Sprint timeline

Original Phase 2 (broader Pattern A rollout, Days 5–9) is dropped.
Replaced by Pattern C investigation + prototype (Days 6–7) plus
remaining WS2 catalog work (Days 8–10+). Sprint may extend 1–2 days
to accommodate the Pattern C prototype ramp.

---

## Files referenced

- Traces: `/tmp/sprint25-day5/{qabel,abel,launch}_trace.stderr`
- Emitted MCPs: `/tmp/sprint25-day5/{qabel,abel,launch}_mcp.gms`
- Day 2 findings (prior context): `/tmp/sprint25-phase1-findings.md`

## Key code pointers for Day 6

Pattern C manifestation in launch's stat_iweight — the phantom
`s+1..s+2, s-1..s-2` terms come from somewhere in KKT stationarity
emission. Candidate locations to inspect:

- `src/kkt/stationarity.py::_compute_lead_lag_conditions`
  and `_collect_lead_lag_offsets` — these compute IndexOffset-based
  domain restrictions; worth checking whether the alias `ss` in a
  conditional sum is being coerced into offset form. (Function names
  used as stable references per the convention in
  `docs/planning/EPIC_4/SPRINT_25/PROFILE_HARD_TIMEOUTS.md`.)
- Anywhere stationarity emission iterates the equation body and
  enumerates alias bindings — grep for `card` + `ord` + alias name
  patterns on the emitter side.

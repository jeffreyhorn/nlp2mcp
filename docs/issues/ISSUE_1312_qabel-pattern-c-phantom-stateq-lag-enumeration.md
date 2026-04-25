# qabel: Pattern C Variant — Massive Phantom Stateq Lag Enumeration on Large-Cardinality `k`

**GitHub Issue:** [#1312](https://github.com/jeffreyhorn/nlp2mcp/issues/1312)
**Status:** OPEN — targeted for Sprint 26 carryforward
**Severity:** High — produces a numerically wildly-wrong (1.4e17 vs NLP 46965) MCP for qabel; was previously masked by the unrelated #1311 AD bug
**Date filed:** 2026-04-25
**Discovered:** Sprint 25 Day 8 (PR #1310, post-#1311 fix) — see "How this got unmasked" below
**Related:**
- `#1311` (RESOLVED in PR #1310 — the AD u-criterion-gradient drop that was masking this issue)
- `#1150` (qabel/abel — original "Pattern A" classification; remains open until #1312 lands)
- `#1306` (Pattern C Bug #1 — launch-shaped phantom-offset gate, RESOLVED Sprint 25 Day 6 PR #1308; deliberately narrow, doesn't cover this large-cardinality variant)
- `DAY7_COHORT_SWEEP.md` §"#1150 qabel — Pattern C (massive enumeration variant)" (the original observation, classified at the time as a distinct Pattern C variant out of scope for Day 6)

---

## Problem Summary

The KKT stationarity emitter produces an enormous enumeration of phantom lag offsets on qabel's `stat_u` (and `stat_x`):

```gams
* qabel post-#1311: stat_u contains 60+ enumerated stateq lag terms
stat_u(m,k).. (... criterion u-gradient ...
            + sum(n, ((-1) * b(n,m)) * nu_stateq(n,k))
            + sum(n, (((-1) * b(n,m)) * nu_stateq(n,k-9))$(ord(k) > 9))
            + sum(n, (((-1) * b(n,m)) * nu_stateq(n,k-10))$(ord(k) > 10))
            ...
            + sum(n, (((-1) * b(n,m)) * nu_stateq(n,k-68))$(ord(k) > 68)))$(ku(k)) =E= 0;
```

Source: `qabel.gms` declares `Set k 'quarters' / q1*q%qmax% /` with `qmax=75` (card(k)=75) and `stateq(n, k+1).. x(n,k+1) =e= sum(np, a(n,np)*x(np,k)) + sum(m, b(n,m)*u(m,k)) + c(n);`. The source has a single `+1` lead on `k`, plus `a(n+1,n)`/`a(n-1,n)` IndexOffsets on `n`. Nothing in the source references `k-9` through `k-68`.

The runtime effect: PATH receives an MCP whose stationarity is structurally wrong for any concrete `k` value, and converges to a fixed point with `nlp2mcp_obj_val ≈ 1.4e+17` versus the NLP baseline of `46965.04`.

## Reproduction

On a checkout where #1311 has landed (current main as of 2026-04-25):

```bash
python -m src.cli data/gamslib/raw/qabel.gms -o /tmp/qabel.gms --skip-convexity-check

# Count phantom enumeration terms:
grep "^stat_u" /tmp/qabel.gms | tr '+' '\n' | grep -c "nu_stateq(n,k-"
# Expected: 60.

# Solve and observe the blow-up:
gams /tmp/qabel.gms lo=2
grep "PARAMETER nlp2mcp_obj_val" qabel.lst
# ~1.4e+17 (vs NLP baseline 46965.04 — 14 orders of magnitude off).
```

Inspecting `stat_x` shows the same shape, multiplied by the cross-product with `n+1` / `n-1` Jacobian variants — yielding hundreds of phantom terms on `stat_x`.

## How this got unmasked

Pre-#1311 (the AD u-criterion-gradient drop), qabel's `stat_u` was effectively **under-determined**: the Jacobian transpose terms (with the phantom enumeration) were the only contribution, but the criterion-gradient term — which `stat_u` is supposed to balance against — was missing. PATH found *a* solution to that under-determined system (whatever zeroes the transpose terms), and the blow-up didn't manifest. The post-#1311 emission correctly includes the criterion-gradient, which interacts with the phantom enumeration multiplicatively and amplifies the bias to ~1.4e17.

So #1311 unmasked this issue rather than introducing it. The phantom enumeration was always there — see `DAY7_COHORT_SWEEP.md`'s qabel row, which captured the same emission shape and noted "Pattern C (massive enumeration variant) — distinct from launch-shape; Day 6 gate's IndexOffset-present check correctly leaves it alone since source has `a(n±1,n)`. Pre-existing emission shape; unchanged from Day 5."

## Root Cause

`src/kkt/stationarity.py::_compute_index_offset_key` groups Jacobian entries by **positional offset** between concrete equation and variable instances. For qabel:

- `stateq(n, k+1)` is defined for k ∈ q1..q74 (74 instances per n).
- Variable `u(m, k)` is defined for k ∈ q1..q75.
- The Jacobian entry `∂stateq(n_eq, k_eq)/∂u(m_v, k_v)` is non-zero when `k_eq = k_v + 1`.
- For each (k_eq, k_v) pair where this holds, `_compute_index_offset_key` computes `pos(k_eq) - pos(k_v) = 1` consistently.

That should produce a single offset key `(0, +1)`. But for qabel, the grouping appears to produce 60+ distinct offset keys spanning -9 to -68 — much more than the single `+1` the source justifies. Hypotheses (need investigation during fix):

- The AD's symbolic differentiation may be returning multiple matchings for the same `(eq, var)` pair via aliasing of `n`, and `_compute_index_offset_key` re-classifies them under different offset keys.
- The interaction between qabel's `Alias(n, np)` and the `sum(np, a(n,np)*x(np,k))` body produces cross-element Jacobian entries on `n` whose `k` positional offsets are misclassified — perhaps the sum's `np` binding is being misinterpreted as a `k` shift.
- Issue #1045's offset-grouping logic (`_compute_index_offset_key` was added for `totalcap(t)` lead/lag) doesn't generalize cleanly to qabel's combined `n`-aliasing + `k`-lead/lag case. The Day 6 fix (issue #1306) added a narrow source-body gate; Day 6's `_body_has_index_offset_on_sets` returns True for qabel because of `a(n+1, n)`, so the consolidation-to-zero-offset path is correctly skipped — but a more nuanced gate is needed that consolidates non-zero offsets that don't correspond to any source-body offset.

The launch-shaped Day 6 Pattern C gate doesn't fire because qabel's source DOES have a real `IndexOffset` on `n` (`a(n+1, n)`, `a(n-1, n)`); the gate's "no real IndexOffset on the variable's domain" precondition fails. A different gating heuristic is needed for this case.

## Candidate Fix Approaches

1. **Cardinality-bounded gate.** If the offset-key enumeration produces more than `_MAX_PHANTOM_OFFSETS` distinct non-zero keys (e.g. > 4), audit them: any keys not corresponding to a source-body `IndexOffset` magnitude should be consolidated. This is conservative — preserves twocge-style `±1` lead/lag while suppressing the qabel blow-up.
2. **Source-body offset matching.** Build a set `source_offsets ⊆ ℤ` of all `IndexOffset.offset` integer values that appear in the equation body indexing the variable's domain. Only emit offset-grouped multiplier terms whose offset key matches one of `source_offsets ∪ {0}`. Drops phantom enumeration regardless of cardinality.
3. **Fix at `_compute_index_offset_key`.** Audit why grouping produces 60+ keys for qabel when the formal derivative has only one `+1` shift. May reveal that the grouping is mis-classifying alias iterations as offsets. If so, fix at the source — preferred long-term but higher risk.

Approach 2 is most surgical and aligns with the Day 6 source-body gate's philosophy.

## Expected Impact

Direct: qabel's MCP objective drops from ~1.4e17 to ~46965 (Match recovery). **+1 Match.**

Likely also helps abel: post-#1311, abel converges to `obj = 97.185` vs NLP `225.195`. abel's smaller card(k)=8 bounds the masking — abel only emits `±1` and `±2` offsets, but those can still bias the symmetric quadratic gradient enough to push PATH to a different local minimum. **+1 Match (likely).**

The fix may also affect other models with combined alias-on-`n` + lead-on-`k` patterns (the `stateq(n, k+1)` family). A regression sweep is needed during the fix; the corpus audit recommended for #1311 is even more important here.

## Files

- `src/kkt/stationarity.py::_compute_index_offset_key` — likely root cause site.
- `src/kkt/stationarity.py::_add_indexed_jacobian_terms` — call site that consumes the offset keys; if Approach 2 is taken, the gate lives here.
- `src/kkt/stationarity.py::_body_has_index_offset_on_sets` (Day 6 helper) — may need to evolve into the source-offset-set helper.
- `src/kkt/stationarity.py::_build_offset_multiplier` — emission target.
- `data/gamslib/raw/{qabel,abel}.gms` — primary repro corpus.

## Scheduling

Filed during Sprint 25 Day 8 (PR #1310). Targeting **Sprint 26 carryforward** — not in scope for Sprint 25 Day 13 buffer because the fix needs:

1. An audit of why `_compute_index_offset_key` produces 60+ keys for qabel.
2. A gating-heuristic design that distinguishes qabel-style phantoms from twocge-style legitimate lead/lag.
3. A corpus regression sweep (the same one #1311 needs but didn't have time for).

This combination of investigation + design + corpus validation is more than 1 day's work, and Sprint 25's Day 13 buffer is reserved for shorter clean-up tasks per the revised plan.

## Status

Open. Not in scope for Sprint 25 Day 14 retest. Sprint 26 lever for ≥+1 Match (qabel) and likely +1 more (abel).

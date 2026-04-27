# #1277 (post-Day 6 follow-up) — twocge: Pattern C plain-alias sum still mis-emits stat_tz / stat_tx

## Status

Original #1277 was closed when the Pattern C Day 6 gate (PR landed
2026-04-20-ish) consolidated phantom ±N offset groups for the
**launch-style conditional alias sum**:

    sum(ss$ge(ss, s), iweight(ss) + ...)

Day 10 re-validation (2026-04-25) confirms the gate does NOT cover
twocge's source shape, and `stat_tz` and `stat_tx` continue to emit
inconsistent shifted/unshifted indices.

## Source (twocge.gms:247)

    eqXg(i, r).. Xg(i, r) =e= mu(i, r) * (
        Td(r) + sum(j, Tz(j, r)) + sum(j, Tm(j, r)) - Sg(r)
    ) / pq(i, r);

The body has a **plain alias sum** `sum(j, Tz(j, r))` — `j` is an alias
of `i` and the sum has **no `$`-condition**. There is no `IndexOffset`
node anywhere in the body.

## Mis-emission (Day 10 master @ commit `1dcde4fd` — `data/gamslib/raw/twocge.gms`)

`stat_tz(j, r)` (and the analogous `stat_tx`):

    stat_tz(j, r)..  nu_eqTz(j, r)
      + ((-1) * (pq(j, r) * mu(j,   r) / sqr(pq(j,   r)))) * nu_eqXg(j,   r)
      + (((-1) * (pq(j, r) * mu(j+1, r) / sqr(pq(j,   r)))) * nu_eqXg(j+1, r))$(ord(j) <= card(j) - 1)
      + (((-1) * (pq(j, r) * mu(j-1, r) / sqr(pq(j,   r)))) * nu_eqXg(j-1, r))$(ord(j) > 1)
      + ((-1) * ssg(r)) * nu_eqSg(r) - piL_tz(j, r) =E= 0;

Compare `stat_tm(i, r)` (correct):

    stat_tm(i, r)..  nu_eqTm(i, r)
      + ((-1) * (pq(i,   r) * mu(i,   r) / sqr(pq(i,   r)))) * nu_eqXg(i,   r)
      + (((-1) * (pq(i+1, r) * mu(i+1, r) / sqr(pq(i+1, r)))) * nu_eqXg(i+1, r))$(ord(i) <= card(i) - 1)
      + (((-1) * (pq(i-1, r) * mu(i-1, r) / sqr(pq(i-1, r)))) * nu_eqXg(i-1, r))$(ord(i) > 1)
      + ((-1) * ssg(r)) * nu_eqSg(r) - piL_tm(i, r) =E= 0;

In `stat_tz` the offset is applied to `mu` and `nu_eqXg` but **NOT** to
`pq`/`sqr(pq)`. Mathematically the j±1 terms shouldn't exist at all —
`Tz` is consumed inside `sum(j, ...)`, not via lead/lag — but the
offset-key grouping splits the alias-sum entries into ±1 buckets.

## Root Cause

`_compute_index_offset_key` (`src/kkt/stationarity.py:3453`) sees:

- `eqXg(BRD, R) / Tz(MLK, R)`: positional offset = pos(BRD) − pos(MLK) = −1
- `eqXg(MLK, R) / Tz(BRD, R)`: positional offset = +1
- `eqXg(BRD, R) / Tz(BRD, R)`:  offset = 0

so the entries get split into three offset groups. The Pattern C Day 6
gate (lines ~4108–4161) consolidates them only when **both** of:

1. The body contains no `IndexOffset` on the variable's domain.
2. The body contains an **aliased conditional sum** — `body_has_aliased_conditional_sum_over_sets()` requires a `$`-condition that
   references the equation's own domain.

twocge satisfies (1) but **not** (2): `sum(j, Tz(j, r))` has no
`$`-condition. So the gate doesn't fire and the spurious ±1 groups
emit per-offset multiplier terms.

## Why stat_tx mixes shifted/unshifted

The variable's per-instance Jacobian columns are `Tz(j, r)` for each
concrete `j ∈ {BRD, MLK}`. The offset-group representative for the
+1 group is `eqXg(MLK, R) / Tz(BRD, R)`, whose derivative is
`(-mu(MLK, R) / pq(MLK, R))`. When the multiplier domain `(j, r)` is
emitted with shifted indices `(j+1, r)`, the Day-6 path `_apply_alias_offset_to_deriv` (`stationarity.py:1906`) shifts only those parameter indices whose declared domain matches the
constraint's domain. `pq` and `sqr(pq)` apparently don't get the shift
applied because of an interaction between the alias substitution and
the param-domain matching — the `mu` reference does, hence the
`pq(j, r) * mu(j+1, r)` mix.

(Day 10 did not deeply trace this second-stage interaction since the
groups should not have been split in the first place — fixing the
gate scope subsumes the per-param shift inconsistency.)

## Suggested Fix Direction

Widen the Pattern C Day-6 gate to also recognize **plain alias-sum
without `$`-condition** as a sum-iteration fingerprint, when:

- The body has no `IndexOffset` on any index that resolves to a set in
  the variable's domain.
- The body contains a `Sum` whose index name resolves (via alias) to a
  set in the variable's domain.

Both are local body-traversal checks similar to the existing helpers
`_body_has_index_offset_on_sets` and
`_body_has_aliased_conditional_sum_over_sets`. A new
`_body_has_aliased_plain_sum_over_sets` (no condition required) can
extend the consolidation criterion.

Care: the existing condition-based gate was deliberately narrow to
preserve real lead/lag patterns (paklive's `nutbal(n,t).. ... xtransf(n,t--1)`,
qabel/abel's `stateq`). Both of those have an `IndexOffset` node in
the body (`t-1`/`t--1`), so they continue to fail criterion (1) and
remain on the per-offset path. The gate widening only affects bodies
that have no `IndexOffset` at all, which is the same precondition the
existing gate uses.

## Estimated Effort

2–4 h: write `_body_has_aliased_plain_sum_over_sets`, extend the gate,
add a regression test mirroring the twocge fingerprint, validate
launch / paklive / qabel canaries unchanged, and verify twocge
`stat_tz` / `stat_tx` collapse to a single zero-offset multiplier
term.

## Related

- Closed #1277 (original report, Pattern C symptom)
- #1143 (polygon: offset-alias gradient — same bug class)
- #1146 (himmel16: cyclic offset-alias gradient mismatch)
- Day 6 gate: `src/kkt/stationarity.py` ≈ lines 4108–4161
- Day 10 PR: this issue is a deferred follow-up; #1278 (alias-position
  ord tautology) is fixed in the same PR.

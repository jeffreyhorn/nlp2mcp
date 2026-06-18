# otpop `stat_p`: `pdef` `ord(n)-1` cross-term wrong — `sum(n,alpha(n))` instead of per-lead weight

**GitHub Issue:** [#1452](https://github.com/jeffreyhorn/nlp2mcp/issues/1452)
**Status:** OPEN — filed Sprint 28 Day 7 follow-on (2026-06-18). **The last gate to otpop's +1 Solve/+1 Match** (after #1393 kdef, #1335 zdef, #1449 presolve).
**Severity:** Medium — produces a wrong KKT cross-term; otpop solves but mismatches (pi 3160.86 vs NLP 4217.7978).
**Affected models:** otpop (confirmed); likely any model with `var(tt - (ord(n)-1))` adaptive-expectations / distributed-lag structure.

## How it surfaced

With #1393 + #1335 + #1449 landed, otpop's `--nlp-presolve` now **compiles and solves (MCP MS 1 Optimal)**, the embedded NLP warm-starts correctly (4217.7978), and the KKT-residual harness finally runs on otpop. Its verdict:

```
verdict: CASE_B — emit_bug   (dual transfer CONSISTENT, dual scale 307)
max-residual row: stat_p(1983)  rel 1.16   (raw -358)
top rows: stat_p(1980), (1981), (1982), (1983), (1984)   — the middle years
```

The MCP converges to pi = 3160.86, not the NLP's 4217.7978.

## Root cause

```
pdef(tt)..  pd(tt) =e= sum(n, alpha(n) * p(tt - (ord(n) - 1)));   ! n=1*3, alpha=(.5,.3,.2)
```
So `pd(tt) = 0.5·p(tt) + 0.3·p(tt-1) + 0.2·p(tt-2)`, and `p(tt)` appears in `pdef(tt)` (coef `alpha('1')`), `pdef(tt+1)` (`alpha('2')`), `pdef(tt+2)` (`alpha('3')`). Correct `stat_p(tt)` cross-term:
```
- ( 0.5·nu_pdef(tt) + 0.3·nu_pdef(tt+1) + 0.2·nu_pdef(tt+2) )
```

Emitted (cold + presolve golden):
```
sum(n, ((-1)*alpha(n)) * nu_pdef(tt))
  + sum(n, ((-1)*alpha(n)) * nu_pdef(tt+1))$(ord(tt) <= card(tt)-1)
  + sum(n, ((-1)*alpha(n)) * nu_pdef(tt+2))$(ord(tt) <= card(tt)-2)
```
= `sum(n, alpha(n)) = 1.0` applied to **each** lead — the `n`-sum is mixed with the lead offset, so every lead gets the *total* weight (1.0) instead of its *specific* weight `alpha(n)`.

## Localization (2026-06-18) — the AD is correct; the bug is the stationarity re-symbolization

The constraint Jacobian is **right**:
```
∂pdef('1983')/∂p('1983') = -alpha(1)   (lead 0)
∂pdef('1984')/∂p('1983') = -alpha(2)   (lead +1)
∂pdef('1985')/∂p('1983') = -alpha(3)   (lead +2)
```
So #1081 expansion + AD produce the correct per-instance derivatives — the specific element `alpha('1')`/`alpha('2')`/`alpha('3')` at each lead.

The bug is in **`_add_indexed_jacobian_terms`** (`src/kkt/stationarity.py`), which groups the per-instance entries by lead offset (`_compute_index_offset_key` → offsets 0/+1/+2 — correct) and then **re-symbolizes the per-group coefficient wrongly**: the offset-0 group has the constant coefficient `alpha('1')`, but the re-symbolization treats the alpha-domain element `'1'` as an *uncontrolled index*, maps it to the symbolic `n`, and wraps it in `sum(n, …)` → `sum(n, alpha(n))` (= 1.0). Same mechanism as [[ISSUE_1393]] (a concrete index wrongly summed), but in the **indexed-constraint branch** rather than the scalar branch.

**Correct re-symbolization** — either keep the per-group constant element (`-alpha('1')·nu_pdef(tt)`, `-alpha('2')·nu_pdef(tt+1)`, `-alpha('3')·nu_pdef(tt+2)`), or, equivalently, a single `sum(n, (-1)·alpha(n)·nu_pdef(tt+(ord(n)-1)))`. The offset (lead) determines the alpha element; it must not be summed over.

### Exact fix surface (2026-06-18)

`src/kkt/stationarity.py`, in `_add_indexed_jacobian_terms`, the offset-group re-symbolization at **`indexed_deriv = _replace_indices_in_expr(derivative, var_domain, constraint_element_to_set, …)` (~line 6177)**. For the offset-0 group `derivative = -alpha('1')`; `constraint_element_to_set` maps the alpha-domain element `'1'` → its set `n`, so `alpha('1')` → `alpha(n)`, and downstream the now-uncontrolled `n` is wrapped in `sum(n, …)`. The element `'1'` is **offset-determined** (the group's `offset_key` is 0 and `ord('1')-1 = 0`), so it must be pinned, not re-symbolized to the iterator. A correct, tightly-gated fix must detect that a coefficient's param-index element correlates with the group's `offset_key` (via `ord(elem)-1 == offset`) and keep the concrete element (or emit the single `sum(n, alpha(n)·nu(tt+(ord(n)-1)))` form), **without** disturbing genuine uncontrolled-index sums.

**Risk:** `_replace_indices_in_expr` / `_add_indexed_jacobian_terms` is the shared cross-term path for every model — the fix needs a tight gate + full-corpus golden regression. Recommended as a focused task (this is the 4th distinct otpop AD bug, comparable in depth to #1393/#1335).

Same family as the offset-handling work in [[ISSUE_1393]] / [[ISSUE_1335]] / [[ISSUE_1224]], for an `ord(<sum-index>)-1` offset in an indexed equality.

## Acceptance

`stat_p(tt)` emits the per-lead weights (`0.5·nu_pdef(tt) + 0.3·nu_pdef(tt+1) + 0.2·nu_pdef(tt+2)`); the harness residual at `stat_p(1980–1984)` → 0; otpop's presolve MCP matches the NLP (`pi ≈ 4217.7978`, MS 1) — completing otpop's +1 Solve/+1 Match.

## Related

- [[ISSUE_1393]], [[ISSUE_1335]] — the other two otpop `stat_p`/`stat_x` cross-term fixes (kdef, zdef).
- [[ISSUE_1449]] — the presolve `$184`/warm-start fix that unblocked the harness and surfaced this.

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

## The AD bug

Differentiating `sum(n, alpha(n)·p(tt-(ord(n)-1)))` w.r.t. `p` must invert the `ord(n)-1` offset **per `n`**, mapping each `n` to lead `nu_pdef(tt+(ord(n)-1))` with coefficient `alpha(n)`. Instead the cross-term sums `alpha(n)` over `n` at each fixed lead. Same family as the offset-handling work in [[ISSUE_1393]] / [[ISSUE_1335]] / [[ISSUE_1224]], but for an `ord(<sum-index>)-1` offset in an indexed equality.

## Acceptance

`stat_p(tt)` emits the per-lead weights (`0.5·nu_pdef(tt) + 0.3·nu_pdef(tt+1) + 0.2·nu_pdef(tt+2)`); the harness residual at `stat_p(1980–1984)` → 0; otpop's presolve MCP matches the NLP (`pi ≈ 4217.7978`, MS 1) — completing otpop's +1 Solve/+1 Match.

## Related

- [[ISSUE_1393]], [[ISSUE_1335]] — the other two otpop `stat_p`/`stat_x` cross-term fixes (kdef, zdef).
- [[ISSUE_1449]] — the presolve `$184`/warm-start fix that unblocked the harness and surfaced this.

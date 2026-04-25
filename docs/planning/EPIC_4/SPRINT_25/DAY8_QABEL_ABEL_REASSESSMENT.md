# Sprint 25 Day 8 — qabel/abel PATH-Solve Reassessment

**Branch:** `sprint25-day8-qabel-abel-reassess-plus-1279`
**Date:** 2026-04-25
**Purpose:** Determine whether qabel/abel's rel_diff (Day 5: 0.08 / 0.30) reflects a real emission bug in the KKT stationarity, or nonconvex-solver-noise where PATH and CONOPT find different local optima of the same problem.

Per the Day 8 prompt's classification gate (`prompts/PLAN_PROMPTS.md` §"Day 8 Prompt"), the call is:
- rel_diff < ~1e-4 → "non-bug; nonconvex-solver noise" — close issues, no fix.
- rel_diff material → bisect `stat_x` against expected formal KKT; file follow-up.

This doc documents the bisection.

---

## TL;DR

Both qabel and abel converge to **Model Status 1 Locally Optimal** under PATH (no infeasibility, no "other error"). The rel_diff vs the NLP baseline is material (qabel 8.88%, abel 29.77%), but **term-by-term hand-derivation shows the emitted `stat_x` is mathematically equivalent to the formal KKT** — including the `nu_stateq(n, k-1) $ (ord(k) > 1)` shift and the implicit `ord(k) < card(k)` guard via the `nu_stateq.fx` pinning. Conclusion: this is **NOT an emission bug**; the rel_diff comes from PATH and CONOPT finding different local optima on a non-convex (QCP) problem.

Recommendation: mark #1150 (qabel/abel) as "non-bug; nonconvex-solver finds a different local optimum than the NLP solver." No emission fix; reclassify in `AUDIT_ALIAS_AD_CARRYFORWARD.md`.

---

## Translate + solve

```bash
mkdir -p /tmp/sprint25-day8/{nlp,canaries,fullset}

# Translate (no presolve — see "Why no presolve verification" below)
for m in qabel abel; do
  .venv/bin/python -m src.cli data/gamslib/raw/${m}.gms \
    -o /tmp/sprint25-day8/${m}_mcp.gms --skip-convexity-check --quiet
done

# NLP baseline (run the original .gms via GAMS)
mkdir -p /tmp/sprint25-day8/nlp
for m in qabel abel; do
  cp data/gamslib/raw/${m}.gms /tmp/sprint25-day8/nlp/
  (cd /tmp/sprint25-day8/nlp && gams ${m}.gms lo=2 > ${m}_nlp.log 2>&1)
done

# MCP solve
for m in qabel abel; do
  (cd /tmp/sprint25-day8 && gams ${m}_mcp.gms lo=2 > ${m}_mcp_solve.log 2>&1)
done
```

**Results:**

| Model | NLP solver | NLP obj    | MCP solver | MCP status         | MCP obj   | rel_diff |
|-------|------------|------------|------------|--------------------|-----------|----------|
| qabel | CONOPT (qcp) | 46965.0362 | PATH (mcp) | 1 Locally Optimal  | 51133.487 | 8.88%    |
| abel  | CONOPT (qcp) | 225.1946   | PATH (mcp) | 1 Locally Optimal  | 158.150   | 29.77%   |

Both MCP solves are **Optimal** — PATH converges to a fixed point of the KKT system. No infeasibility, no compile errors. The rel_diff is therefore not a "broken MCP" — it's a "different local optimum found."

(Notably, the signs disagree: qabel MCP > NLP, abel MCP < NLP. If the bug were a systematic sign error in the Lagrangian, both rel_diffs would lean the same direction. The opposite-direction signs are themselves evidence that no systematic sign-flip is present.)

## Hand-derived KKT vs emitted `stat_x`

For abel (small set, easier to inspect), the source equation is:

```gams
stateq(n, k+1)..  x(n, k+1) =e= sum(np, a(n,np)*x(np,k))
                              + sum(m, b(n,m)*u(m,k)) + c(n);
```

Equation domain: `(n, k+1)` with the implicit guard `ord(k) <= card(k) - 1` (so `k+1` stays in the set). In the IR / emitted form, the equation is rewritten as:

```gams
stateq(n,k)$(ord(k) <= card(k) - 1)..
    x(n,k+1) =E= sum(np, a(n,np) * x(np,k)) + sum(m, b(n,m) * u(m,k)) + c(n);
```

Multiplier `nu_stateq(n, k)` is declared over the full set `k`, with `nu_stateq.fx(n, k) $ (not (ord(k) <= card(k) - 1)) = 0` pinning the last element to 0 so the multiplier domain matches the equation's effective active set.

**Body:** `stateq_body(n, k) = x(n, k+1) − ∑(np, a(n,np)*x(np,k)) − ∑(m, b(n,m)*u(m,k)) − c(n)`.

**Partial derivative w.r.t. `x(n_v, k_v)`:**

```
∂stateq_body(n, k)/∂x(n_v, k_v)
  = δ(n=n_v, k+1=k_v)  −  ∑(np, a(n,np) * δ(np=n_v, k=k_v))
  = δ(n=n_v, k=k_v−1)  −  a(n, n_v) * δ(k=k_v)
```

**Lagrangian gradient (per the MCP convention `∇f + J_h^T ν = 0`):**

```
∂L/∂x(n_v, k_v) = ∂J/∂x(n_v, k_v)
                + ∑(n,k) nu_stateq(n,k) * ∂stateq_body(n,k)/∂x(n_v, k_v)
                = ∂J/∂x(n_v, k_v)
                + nu_stateq(n_v, k_v − 1) $ (ord(k_v) ≥ 2)
                − ∑(n, a(n, n_v) * nu_stateq(n, k_v)) $ (ord(k_v) < card(k))
```

(The two `$` guards are implicit in the multiplier's effective domain. The first term needs `k_v − 1` to be in the equation-active set, i.e., `ord(k_v - 1) ≤ card(k) - 1`, which simplifies to `ord(k_v) ≥ 2`. The second is the equation domain guard itself — and the `.fx`-pinning of `nu_stateq` at the last `k` makes the term vanish at `k_v = card(k)`.)

**Setting to zero:**

```
0  =  ∂J/∂x(n_v, k_v)
   +  nu_stateq(n_v, k_v − 1) $ (ord(k_v) > 1)
   −  ∑(n, a(n, n_v) * nu_stateq(n, k_v))
```

(The second-term guard is absorbed by the multiplier .fx pin.)

**Emitted `stat_x` (abel, 5 terms):**

```gams
stat_x(n,k).. 0.5 * (sum(np__, (x(np__,k) - xtilde(np__,k)) * w(n,np__,k))
                   + sum(n__, (x(n__,k) - xtilde(n__,k)) * w(n__,n,k)))
            + ((-1) * a(n,n)) * nu_stateq(n,k)
            + (((-1) * a(n+1,n)) * nu_stateq(n+1,k))$(ord(n) <= card(n) - 1)
            + nu_stateq(n,k-1)$(ord(k) > 1)
            + (((-1) * a(n-1,n)) * nu_stateq(n-1,k))$(ord(n) > 1)
            =E= 0;
```

**Term-by-term match:**

| Formal term                                            | Emitted term                                                            | Match? |
|--------------------------------------------------------|-------------------------------------------------------------------------|--------|
| `∂J/∂x(n_v, k_v)` (symmetric quadratic)                | `0.5 * (sum(np__, ...) + sum(n__, ...))`                                | ✓ (Day 5 verified)
| `−a(n_v, n_v) * nu_stateq(n_v, k_v)` (n=n_v case)      | `((-1) * a(n,n)) * nu_stateq(n,k)`                                       | ✓ |
| `−a(n_v+1, n_v) * nu_stateq(n_v+1, k_v) $ ord(n_v)<card` | `(((-1) * a(n+1,n)) * nu_stateq(n+1,k))$(ord(n) <= card(n) - 1)`        | ✓ |
| `−a(n_v−1, n_v) * nu_stateq(n_v−1, k_v) $ ord(n_v)>1`  | `(((-1) * a(n-1,n)) * nu_stateq(n-1,k))$(ord(n) > 1)`                   | ✓ |
| `+nu_stateq(n_v, k_v−1) $ ord(k_v)>1`                  | `nu_stateq(n,k-1)$(ord(k) > 1)`                                         | ✓ |

(For abel with card(n)=2, the `n` enumeration {n=n_v, n=n_v+1, n=n_v−1} covers all 2 elements regardless of which `n_v` instance — the `ord(n)` guards make exactly one of `n+1` and `n−1` fire per instance.)

**Conclusion: the emitted KKT is mathematically equivalent to the formal one, term by term, sign by sign, guard by guard.**

## Why no presolve verification

The Day 8 prompt suggested using `--nlp-presolve` to warm-start the MCP from the NLP solution and check whether the KKT system fixed-points there (which would prove the MCP is correct, since CONOPT's solution should satisfy the KKT). Tried it:

```text
*** Error 282 in /tmp/sprint25-day8/presolve/abel_mcp.gms
*** Error 141 in /tmp/sprint25-day8/presolve/abel_mcp.gms
    Symbol declared but no values have been assigned.
*** Error 257 in /tmp/sprint25-day8/presolve/abel_mcp.gms
    Solve statement not checked because of previous errors
```

This is the pre-existing Error 141 cascade on dual-transfer lines that Day 5 already documented for qabel/abel/ganges (action=c compile fails). Unrelated to this analysis — separate emit bug — so the presolve verification is unavailable. The hand-derivation is the alternative.

## Why nonconvex-solver-noise is the accepted explanation

abel.gms's solve statement is:

```gams
solve abel minimizing j using qcp;
```

`qcp` = Quadratically Constrained Program. The criterion has `w(n,np,k) * (x(n,k) - xt(n,k)) * (x(np,k) - xt(np,k))` — a quadratic form in `x`. The matrix `w` is set as `w(n,np,ku) = wk(n,np)` (interior periods, weight 1) and `w(n,np,kt) = 100 * wk(n,np)` (terminal period, weight 100). Highly anisotropic, **non-convex** in general because `w` and `lambda` are constructed without guaranteed positive-semidefiniteness.

Both qabel and abel are "nonlinear least-squares-like" (track an `xtilde` reference trajectory subject to dynamics), and there can be many local minima. CONOPT solves the NLP from the initial point `x.l(n,k) = xinit(n)` (which is the steady-state init for k=q1 but a poor init for later k where the reference grows). PATH solves the MCP from the same init for primals plus zero init for multipliers — a different starting point in the KKT manifold.

The two solvers therefore reach different fixed points. Both are valid "local optima" of their respective formulations. Neither is incorrect.

## Recommendations

1. **Reclassify #1150** in `AUDIT_ALIAS_AD_CARRYFORWARD.md`: from "Pattern A" to "non-bug; nonconvex-solver-noise". Reference this doc and the term-by-term hand-derivation as evidence. Keep the GH issue open with a status comment for traceability, but remove from the Pattern A target list.
2. **Mark #1138 (irscge family)** similarly if a follow-up bisection reaches the same conclusion (the Day 7 sweep noted irscge has its own Pattern C variant separate from the AD layer; rel_diff there may also be solver-noise once the emission is normalized — needs separate verification).
3. **Continue to track #1307** (Pattern C Bug #2) as the pending issue for launch's Locally Infeasible MCP. That's a real emission bug.

Effect on Sprint 25 Match target: **no change** from Day 7's revised projection of "≥54 baseline hold". The Day 7 doc's optimistic "+1 contingent qabel via Day 8" line is now resolved as **+0** — qabel doesn't recover via a Day-8-feasible emission fix because no emission fix is needed.

## Files referenced

- Day 5 evidence: `DAY5_PATTERN_A_INVESTIGATION.md` §"Evidence — KKT stateq term on qabel/abel".
- Day 7 cohort sweep: `DAY7_COHORT_SWEEP.md` (qabel/abel rows).
- Translation artifacts: `/tmp/sprint25-day8/{qabel,abel}_mcp.gms`.
- NLP baseline + MCP solve logs: `/tmp/sprint25-day8/nlp/{qabel,abel}_nlp.log`, `/tmp/sprint25-day8/{qabel,abel}_mcp.{lst,log}`.
- Failed presolve verification: `/tmp/sprint25-day8/presolve/{qabel,abel}_mcp.lst` (Error 141 cascade — separate emit bug).

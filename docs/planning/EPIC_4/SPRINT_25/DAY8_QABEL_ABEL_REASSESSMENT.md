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

Both qabel and abel converge to **Model Status 1 Locally Optimal** under PATH (no infeasibility). The rel_diff vs the NLP baseline is material (qabel 8.88%, abel 29.77%).

**Initial hypothesis (rejected):** "Both NLPs are non-convex (qcp) and PATH/CONOPT find different local optima — solver-noise, not an emission bug."

**Multi-start NLP refuted that:** 5 randomized initial points each converged to the SAME NLP objective for both models (qabel: 46965.036 × 5; abel: 225.195 × 5). The NLPs have unique optima, so the rel_diff cannot be solver-noise.

**Bisection found a real AD bug.** Inspecting the gradient output via `compute_objective_gradient`, the AD layer emits `Const(0.0)` for `u(m, k_v)` derivatives at every `k_v` — including those where the criterion's `sum(ku, ...)` aggregation is active (`ku` is a declared subset of `k`). The criterion's u-quadratic term is silently dropped by the AD when the sum's bound index is a SUBSET of the variable's declared domain (rather than the same name or an alias).

Concretely, the criterion in both models is:

```gams
.5 * sum((k, n, np), (x(n,k) - xt(n,k))   * w(n,np,k)   * (x(np,k) - xt(np,k)))
+ .5 * sum((ku, m, mp), (u(m,ku) - ut(m,ku)) * lambda(m,mp) * (u(mp,ku) - ut(mp,ku)))
```

The x-quadratic (sum over `k`) is differentiated correctly — Day 5 verified the symmetric form is byte-for-byte right. But the u-quadratic (sum over the SUBSET `ku ⊆ k`) is dropped entirely.

Filed as issue [#1311](https://github.com/jeffreyhorn/nlp2mcp/issues/1311). Likely fix area: `src/ad/derivative_rules.py::_diff_varref` and/or `src/ad/index_mapping.py` (subset-of-domain matching for sum binding). NOT a same-day fix — targeting Sprint 26 (or Day 13 buffer if schedule allows).

**Recommendation update:** withdraw the "non-bug; nonconvex-solver-noise" reclassification of #1150. Keep #1150 open and add a status comment linking to #1311 (AD layer is the actual bug; fixing #1311 is expected to recover both qabel and abel).

Effect on Sprint 25 Match target: Day 7's revised "≥54 baseline hold" projection still stands for the Day 14 retest (no Day-8 lever for +1 since the fix doesn't land in this PR). Sprint 26 carries a credible "+2 from #1311 fix" lever (qabel, abel) once the AD subset-domain bug is resolved.

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

## Why "nonconvex-solver-noise" was rejected

The initial hypothesis seemed plausible: abel.gms uses `solve abel minimizing j using qcp;` (Quadratically Constrained Program), the matrix `w(n,np,k)` is highly anisotropic (`100 * wk` at the terminal period), and `lambda` is asymmetric in abel's source (`'money.gov-expend' 0.444` — off-diagonal). On those data alone, a "non-convex problem with multiple local optima" reading was reasonable.

Two checks falsified it:

1. **Per-k convexity check.** `w(n,np,k)` is just diagonal-positive `wk = diag(0.0625, 1)` scaled by 1 or 100. PSD for every k. So the x-quadratic is convex. For abel, lambda's symmetric part has eigenvalues `[-0.047, 1.047]` (indefinite — non-convex in u). For qabel, lambda is diagonal-positive `diag(1, 0.444)` (convex in u). So qabel SHOULD be fully convex.

2. **Multi-start NLP.** Five different initial points (x.l/u.l perturbed by ×0.5, ×1.5, ×2 in various combinations) all converged to the SAME NLP objective for both models:
   - qabel: 46965.036 × 5 starts
   - abel:  225.195   × 5 starts

   For convex qabel, this is the expected behavior. For abel (with indefinite lambda), this means the dynamics-as-implicit-constraints make the effective optimization unique — the indefinite-lambda would only allow unbounded descent if the dynamics didn't pin u as a function of x's evolution.

If the NLPs have unique optima and the MCP's KKT system represented those optima faithfully, the MCP solve would converge to the same objective. The 8.88% / 29.77% gap is therefore real evidence of a missing or wrong term in the KKT system — not solver behavior.

## The actual bug — AD drops u-criterion gradient

Direct inspection of `compute_objective_gradient`'s output for abel:

```python
from src.ad.gradient import compute_objective_gradient
g = compute_objective_gradient(model)
# Every u(m, k) entry returns Const(0.0):
#   u(gov-expend, 1964-i) -> Const(0.0)
#   ... including indices where ku(k) is yes
# x entries return the correct symmetric quadratic form (Day 5 verified).
```

The criterion's u-quadratic term is silently dropped by the AD when the sum's bound index is a subset of the variable's declared domain:

```gams
* x is declared over (n, k); the x-quadratic sums (k, n, np) — bound `k` matches variable's `k`. Works.
* u is declared over (m, k); the u-quadratic sums (ku, m, mp) — bound `ku` is a SUBSET of `k`. Fails.
.5 * sum((ku, m, mp), (u(m, ku) - utilde(m, ku)) * lambda(m, mp) * (u(mp, ku) - utilde(mp, ku)))
```

Filed as [#1311](https://github.com/jeffreyhorn/nlp2mcp/issues/1311). Fix is not in scope for Sprint 25 Day 8 (needs an audit of subset-domain handling in `src/ad/derivative_rules.py::_diff_varref` and/or `src/ad/index_mapping.py`, plus a corpus-wide check for other models with the same shape).

**Note that `stat_x` IS still correct** (verified term-by-term against the formal KKT in §"Hand-derived KKT vs emitted `stat_x`"). The bug is specific to `stat_u`, which is missing the u-criterion contribution but has the correct stateq Lagrangian transpose.

## Recommendations

1. **Do NOT reclassify #1150** as "non-bug; nonconvex-solver-noise" — that conclusion was wrong. Keep #1150 open with a status comment linking to #1311. Once #1311 lands, qabel and abel are expected to recover (rel_diff → near zero) and #1150 closes naturally.
2. **Audit other models with `sum(subset, ...)` criterion shapes.** Issue #1311's body recommends a corpus-wide check. The Day 7 cohort's rel_diff classifications (e.g., #1138 irscge family, #1140 ps-family) may have been mis-attributed to "nonconvex" or "stochastic" when the actual cause is the same AD subset-domain bug. Out of scope for Day 8; flagged in #1311.
3. **Continue to track #1307** (Pattern C Bug #2) as the pending issue for launch's Locally Infeasible MCP. That's a separate, also-real emission bug.

Effect on Sprint 25 Match target: **no change to the Day 14 retest** — #1311 is not landing in Sprint 25, so the Match target stays at Day 7's "≥54 baseline hold". For Sprint 26, #1311's expected impact is **+2 Match (qabel, abel) plus possibly more** depending on what the corpus audit surfaces.

## Files referenced

- Day 5 evidence: `DAY5_PATTERN_A_INVESTIGATION.md` §"Evidence — KKT stateq term on qabel/abel".
- Day 7 cohort sweep: `DAY7_COHORT_SWEEP.md` (qabel/abel rows).
- Translation artifacts: `/tmp/sprint25-day8/{qabel,abel}_mcp.gms`.
- NLP baseline + MCP solve logs: `/tmp/sprint25-day8/nlp/{qabel,abel}_nlp.log`, `/tmp/sprint25-day8/{qabel,abel}_mcp.{lst,log}`.
- Failed presolve verification: `/tmp/sprint25-day8/presolve/{qabel,abel}_mcp.lst` (Error 141 cascade — separate emit bug).

# maxmin: stat_mindist stationarity residual (Case b) — objective-variable cross-term missing

**GitHub:** #1447
**Status:** DEFERRED → Sprint 29
**Filed:** Sprint 28 Day 5 (2026-06-16)

## Summary

`maxmin` (circle-packing: `solve maxmin1a max mindist using dnlp;`) emits an MCP whose **`stat_mindist` stationarity row is wrong** (Case b). The model reaches MODEL STATUS 1 but at a **wrong objective** (mismatch).

## How it surfaced

**Surfaced, not caused, by #1388** (Sprint 28 Day 5, PR #1446). Before #1388, maxmin's MCP was `path_solve_terminated`. The #1388 offset-cross-term condition-guard fix (correct) changed maxmin's `stat` emit so PATH now converges to a (wrong) MODEL STATUS 1, exposing this separate, pre-existing `stat_mindist` bug.

## Evidence

- Cold solve (post-#1388): **MODEL STATUS 1, obj ≈ 0.104** — a mismatch.
- KKT-residual harness: **Case b**, max-residual row **`stat_mindist`**, residual ≈ **1.0** at the NLP KKT point.

## Root cause (hypothesis)

`mindist` is the **objective variable** (`max mindist`) and appears in `mindist1a(low(n,nn)).. mindist =l= sqrt(sum(d, sqr(point(n,d) - point(nn,d))))`. The objective-variable stationarity should be:

```
stat_mindist..  (-1) + sum(low, lam_mindist1a(low))  =E= 0     (sum of constraint multipliers = 1)
```

A residual of **exactly 1.0** = the bare objective gradient (`-1`) with **nothing balancing it** → the `sum(low, lam_mindist1a)` cross-term is **missing** (or mis-emitted) from `stat_mindist`. `low(n,nn)` is a 2-D subset and `mindist` is scalar, so the gap is plausibly a scalar-objvar ← 2-D-subset-domain-constraint Jacobian-transpose path.

## Scope

- **Sprint 29.** Not a Sprint-28 target. maxmin was already failing (`path_solve_terminated`) — not a regression of a previously-correct behavior, but it now mis-solves (a confident wrong answer).
- maxmin uses **DNLP** (`sqrt` non-smooth at 0; pairwise distances > 0 at a feasible packing) — verify the fix against the NLP/DNLP reference objective once `stat_mindist` is corrected.

## Acceptance

`stat_mindist` residual → 0 at the NLP KKT point (harness Case a), and maxmin's MCP objective matches the NLP/DNLP reference (`compare_objective_match`).

## Provenance

- #1388 camshape offset-cross-term guard fix (Sprint 28 Day 5, PR #1446) — surfaced this. maxmin's `_mcp.gms` golden was regenerated there (the correct guard re-index); its `stat_mindist` cross-term gap is **this** issue.

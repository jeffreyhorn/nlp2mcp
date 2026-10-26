# ISSUE #1787 — stationarity: a variable referenced twice with the eq index at different positions keeps one term (egypt `tranc(rp,rp)`, tfordy `stat_v`)

**GitHub:** [#1787](https://github.com/jeffreyhorn/nlp2mcp/issues/1787) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 7 (2026-10-26); the Day 8 P4 target (egypt)

**Measured at:** `main` `500ffa1f` · **Layer:** stationarity assembly (KKT): offset grouping / representative selection under the Pattern C consolidation

## Summary

When an equation references a variable **twice, with its own index at different positions**, the stationarity row keeps the contribution of only one reference. This is egypt's Class-A reference `tranc(rp,rp)` (the P2 ratchet) and tfordy's `stat_v`. **Sprint 40 Day 8 (P4) target.**

## Reproducer (egypt's shape)

```gams
Set r / r1*r3 /, c / c1*c2 /;
Alias (r,rp);
Set tranc(r,rp);
tranc(r,rp) = yes$(ord(r) <> ord(rp));
Parameter d(r,c);
d(r,c) = ord(r) - 2 + ord(c)/4;
Positive Variable trans(c,r,rp);
Variable obj;
Equation fodb(r,c), defobj;
fodb(r,c).. sum(rp$tranc(r,rp), trans(c,rp,r) - trans(c,r,rp)) =e= d(r,c) - sum(rp, d(rp,c))/card(r);
defobj.. obj =e= sum((c,r,rp), sqr(trans(c,r,rp)));
Model m / all /;
solve m using nlp minimizing obj;
```

- **Emitted:** `stat_trans(c,r,rp).. 2 * trans(c,r,rp) + 1$(tranc(rp,rp)) * nu_fodb(r,c) - piL_trans(c,r,rp) =E= 0;`. The MCP does not solve; the NLP gives 1.3333.
- **Correct** (Prep Task 10 §2): `2*trans(c,r,rp) + nu_fodb(rp,c)$tranc(rp,r) − nu_fodb(r,c)$tranc(r,rp) − piL`.

## In the corpus

- **egypt** `stat_trans(c,r,rp)`: `-(1$(tranc(rp,rp)))*nu_fodb(r,c)` (golden + presolve; P2 baseline).
- **tfordy** `stat_v(s,k,t,te)`, from `pfs(s,k,t).. sum(te$vpos(t,te), v(s,k,t,te)) =l= … + sum(tp$vpos(tp,t), v(s,k,tp,t))`: only `vpos(t,te)*lam_pfs(s,k,t)`. The second reference's `−vpos(t,te)*lam_pfs(s,k,te)` is missing.
  - The same row also emits `lbal`'s `yv(t,te,s,cl,k)` as **`yv(t,t,s,cl,k)`**: a collapsed coordinate (a ParamRef outside a guard, so P2 does not see it).
  - **The KKT-residual harness classifies tfordy CASE_B (emit bug)** on `main`: `stat_w` rel 1.27, `stat_v` rel 1.0 at the NLP point. Its committed match is presolve-only and rests on the warm start.
  - ⚠ **Sprint 40 Day 7 (#1782) corrects tfordy's `stat_h`** (`sum(tp, avl(tp,t)*nu_ainvc(tp))`, previously #1307's `sum(tp, avl(t,tp))*nu_ainvc(t)`). That changes PATH's path, and tfordy goes **match → model_infeasible**. The owner decided to land it, recorded as exposing this defect, not as a regression of a sound match.

## Shape and first step

- The references bind the eq index at different variable positions, so `_eq_index_ref_binding` gives no binding, and the Pattern C gate (when it fires) consolidates every entry into one representative group. The representative is a diagonal instance (`r = rp`), where the two terms cancel or coincide.
- **First step:** group the Jacobian entries by WHICH variable position the eq label occupies (label equality per entry), and pick an off-diagonal representative per group. Each group then re-symbolises like a single-reference shape (one term per reference).

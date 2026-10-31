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

## Phase 0: Acceptance Gate (Sprint 40 Day 8, P4: egypt)

### Layer

**KKT / stationarity**: the Pattern C consolidation in `_add_indexed_jacobian_terms`. The pattern is found (binder `rp`, eq index `r`), every entry is consolidated into one offset-0 group, and one representative's derivative stands for all. When the references hold the eq index at different variable positions, that representative carries ONE reference's contribution (or, on a diagonal instance, both cancelled).

### Nearest Existing Mechanism

**Nearest:** the Day-7 binder rewrite (#1782), which re-symbolises one representative by position.

**Why it does not apply:** it needs the eq index ABSENT from every reference. Here it is present in both, at different positions, so there is no single placement to rewrite.

### Positive Control

A single-reference equation, or several references with ONE placement of the eq indices (`_multi_reference_layouts` returns None), keeps today's path byte-identically.

### Hand-Derived KKT Shape

Prep Task 10 §2: `∂/∂trans(c,r,rp)` of `fodb(r',cf).. … + sum(rp'$tranc(r',rp'), trans(cf,rp',r') − trans(cf,r',rp'))$ct(cf)` is `+nu_fodb(rp,c)$tranc(rp,r) − nu_fodb(r,c)$tranc(r,rp)` under `$ct(c)$cf(c)`, with the sign flipped for RHS placement.

### Expected Emit Pattern

- **One term per placement** (`_build_multi_reference_terms`). Each is built from an entry whose eq labels sit at that placement's positions and at no other's, so its derivative holds only that reference. It is re-symbolised by position before the element map: every variable label and the reference's binder become the variable's position names, and the multiplier and the equation condition follow the eq indices.
- **egypt:** `stat_trans` gets both terms, and P2 loses `tranc(rp,rp)` (golden + presolve).

### Verification Methodology

1. **Fail-before / pass-after** on `TWO_REFERENCES` (no solve → 1.3333 = NLP) and `EGYPT_SHAPE` (34.75 → 33.25 = NLP), plus `_multi_reference_layouts`'s contract.
2. The positive control.
3. `make check-index-repeats`, the full leak gate with `--resolve-changed`, then `make test`.

### PROCEED/REPLAN Signal

- **PROCEED** if 1–3 hold and the resolver holds every bucket.
- **REPLAN** on any backward move.
- **egypt staying MS 5 is expected** (Task 10: necessary, not sufficient).
- **tfordy's `pfs`:** ⚠ first thought not this pass's shape, from a fixture that repeated `v`'s domain. The real `v(s,k,t,te)` does not, and the leak gate shows the second term restored (see Day 8 results). tfordy also needs its collapsed `yv(t,t,…)` fixed, so it stays on #1787.

## Day 8 results

- **egypt:** both `stat_trans` terms; P2 `tranc(rp,rp)` gone (golden + presolve). Still `model_infeasible`, as expected.
- **Also fixed by the same pass** (leak gate, resolver):
  - **harker**'s `stat_t` network balance (`+nu_nbal(np) − nu_nbal(n)`, match held);
  - **sroute**'s `stat_x` (`model_infeasible` → presolve match);
  - **tfordy**'s `pfs` second reference (still infeasible: `yv(t,t,…)` remains).
- **Open here:** tfordy's `lbal` `yv(t,t,…)` collapse.


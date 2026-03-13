# weapons: MCP Known Limitation — Locally Infeasible After Model Equation Scoping

**GitHub Issue:** [#1067](https://github.com/jeffreyhorn/nlp2mcp/issues/1067)
**Model:** weapons (SEQ=18) — Weapons Assignment
**Type:** NLP
**Category:** Known Limitation (numerical conditioning)

---

## Summary

The weapons model changed from model_optimal (model_status=1) to locally infeasible (model_status=5, 22662 iterations) after PR #1037 added model equation scoping. This is a known limitation, not a bug — the scoping correctly uses the `war` model's equations as specified by the solve statement.

## Resolution: Accepted as Known Limitation

After investigation, this is **not a code bug** and cannot be fixed without incorrect behavior:

1. **Model equation scoping is correct.** The solve statement says `solve war`, so we must use the `war` model's 3 equations (maxw, minw, etd). Using the `warp` model's equations would be incorrect — `warp` is a different model the user did not solve.

2. **The KKT system is mathematically correct.** The stationarity equations for the `war` formulation are the correct derivatives of the Lagrangian. The product rule applied directly to `etd`'s nested `prod(w$td(w,t), (1-td(w,t))**x(w,t))` expression gives the right math — it's just numerically harder for PATH than the decomposed `prob(t)` chain.

3. **The baseline was also problematic.** Before PR #1037, the code incorrectly included all equations from all models (including `warp`), reaching obj=1361.56 vs NLP reference=1735.57 — a 21.6% objective mismatch. The current formulation actually reaches obj=1728.97 (0.4% from NLP reference 1735.57) but fails PATH's feasibility tolerance (residual=39.627).

4. **Future improvement paths exist but are out of scope:**
   - Automatic intermediate variable introduction (major AD architecture feature)
   - NLP warm-start (requires running GAMS twice)
   - PATH solver tuning (solver-specific, not our code)

## Model Structure

The original GAMS model defines two equivalent formulations:
```gams
Model
   war  'traditional'  / maxw, minw, etd         /
   warp 'extended'     / maxw, minw, probe, etdp /;
solve war maximizing tetd using nlp;
```

- `war` uses `etd`: `tetd =E= sum(t, mv(t)*(1 - prod(w$td(w,t), (1-td(w,t))**x(w,t))))`
- `warp` uses `probe(t)` as an intermediate: `prob(t) =E= 1 - prod(w$td(w,t), ...)` and `tetd =E= sum(t, mv(t)*prob(t))`

The `warp` formulation decomposes the gradient chain through `prob(t)`, which was numerically better-conditioned for PATH. But the user solves `war`, not `warp`.

## PATH Solver Output

```
MODEL STATUS      5 Locally Infeasible
22662 iterations
Maximum residual: 39.627 at comp_minw('20')
MCP objective: 1728.97 (vs NLP reference: 1735.57)
```

## Files

- `data/gamslib/raw/weapons.gms` — original NLP
- `data/gamslib/mcp/weapons_mcp.gms` — generated MCP (correct but PATH-infeasible)

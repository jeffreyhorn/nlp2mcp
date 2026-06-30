# hhfair: Objective Mismatch (MCP=54.9 vs NLP=87.2)

**GitHub Issue:** [#1236](https://github.com/jeffreyhorn/nlp2mcp/issues/1236)
**Status:** OPEN
**Severity:** Medium — Model solves optimally but objective differs from NLP
**Date:** 2026-04-09
**Last Updated:** 2026-04-09
**Affected Models:** hhfair

---

## Problem Summary

After fixing EXECERROR (#1179), hhfair solves to MODEL STATUS 1 Optimal but
with MCP obj=54.885 vs NLP obj=87.159 (37% mismatch). This indicates an
incorrect KKT formulation — the stationarity conditions produce a different
optimum than the original NLP.

---

## Current Status

- **Translation**: Success
- **GAMS compilation**: Success
- **PATH solve**: MODEL STATUS 1 Optimal, SOLVER STATUS 1 Normal Completion
- **Objective**: MCP=54.885, NLP=87.159 (37% mismatch)
- **Pipeline category**: model_optimal (mismatch)
- **Previous fixes**: #1179 (EXECERROR, domain-widened variable fixing)

---

## Root Cause (Investigation Needed)

The model has complex mathematical features that may cause AD/KKT errors:

1. **Product aggregation objective**: `obj =e= prod(t, u(t)**ufact(t))` —
   the derivative of a product aggregation uses the logarithmic derivative
   approach. If `ufact(t)` or `u(t)` have edge-case values, the derivative
   may be incorrect.

2. **CES utility function**: `u(t) =e= (a1*c(t)**(-a2) + (1-a1)*(th-l(t)-n(t))**(-a2))**(-1/a2)/100`
   — deeply nested power expressions with negative exponents. The chain rule
   through `(-a2)` powers and `(-1/a2)` root is complex.

3. **Domain widening effects**: Variable `n(t)` was widened to `n(tl)`.
   The extra `n(0) = 0` fixup may affect the KKT system structure.

4. **Set hierarchy**: `tl={0,1,2,3}`, `t(tl)={1,2,3}`, `tt(t)={3}` — 
   subset relationships may cause incomplete Jacobian contributions.

---

## Reproduction

**Prerequisite:** GAMSlib raw sources must be downloaded into `data/gamslib/raw/`
(not checked in; run `python scripts/gamslib/download_models.py` or obtain
`hhfair.gms` from https://www.gams.com/latest/gamslib_ml/hhfair.128).

```bash
.venv/bin/python -m src.cli data/gamslib/raw/hhfair.gms -o /tmp/hhfair_mcp.gms --quiet
gams /tmp/hhfair_mcp.gms lo=0

# Output:
# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      1 Optimal
# nlp2mcp_obj_val = 54.885 (NLP: 87.159)
```

---

## Potential Fix Approaches

1. **Verify product aggregation derivative**: Check that `_diff_prod` correctly
   handles `prod(t, u(t)**ufact(t))` — the logarithmic derivative should produce
   `prod(t, u(t)**ufact(t)) * sum(t, ufact(t) * u(t)**(ufact(t)-1) * du/dx / u(t)**ufact(t))`.

2. **Verify CES utility derivative**: Hand-compute `∂utility/∂c`, `∂utility/∂l`,
   `∂utility/∂n` and compare against the generated stationarity terms.

3. **Check variable initialization**: Poor starting point may cause PATH to
   converge to a different KKT solution (local vs global optimum for non-convex
   utility function).

---

## Files Involved

- `src/ad/derivative_rules.py` — `_diff_prod` for product aggregation
- `src/ad/gradient.py` — Objective gradient computation
- `src/kkt/stationarity.py` — Stationarity equation assembly
- `data/gamslib/raw/hhfair.gms` — Original model (119 lines)

---

## Related Issues

- #1179 (FIXED) — EXECERROR from domain-widened variable

## Phase 0: Acceptance Gate

> **Day-0 status (Sprint 29 Prep Task 2/4, 2026-06-25):** hhfair is the **only live objective-mismatch-cohort target** — on the current Day-0 DB it **still mismatches** (`model_optimal` cold, **72.147 vs 87.159**; the 54.9 figure above is stale). It is therefore the single genuine **+1 Match** opportunity in P6 (firm only if Case b). **⚠️ Day-0 blocker:** `kkt_residual.py data/gamslib/raw/hhfair.gms` currently **errors before producing a verdict** — the warm-started residual MCP fails to compile (**13 GAMS errors, `$141` "symbol declared but no values assigned" + `$257`**), traceable to the domain-widened variable `n(tl)` / the `n(0)=0` fixup. The Day-0 trace must first make the residual emit compile (~~or warm-start via `--gdx` from a pre-solved NLP~~) **before** the Case-b/Case-c verdict can be read. **_[Day-8 correction — OBSOLETE: this Day-0 status is superseded by the decision block below. The blocker's first error is `$184` (the #1449 widened-VARIABLE `n`), not the `$141`; and `--gdx` does NOT bypass it — the presolve `$include` supplies the symbol declarations, not just the solve, so the widened-variable redeclaration conflict fires regardless. → REPLAN to Sprint 30.]_**

### Hand-Derived KKT Shape

hhfair maximizes `obj =e= prod(t, u(t)**ufact(t))` (product-aggregation objective) with the CES utility
`u(t) =e= (a1*c(t)**(-a2) + (1-a1)*(th-l(t)-n(t))**(-a2))**(-1/a2)/100`.

The product-aggregation gradient uses the log-derivative form `∂obj/∂u(t) = obj · ufact(t)/u(t)`, so `stat_u(t)` must read:

```
stat_u(t)..  obj·ufact(t)/u(t) · [coeff] + sum(g, ∂g/∂u(t)·nu_g)  =E= 0
```

and `stat_c(t)`/`stat_l(t)`/`stat_n(t)` carry the chain-rule through the `(-a2)` powers and `(-1/a2)` root of the CES `u(t)` definition. The **set hierarchy** `tl={0,1,2,3}` ⊃ `t(tl)={1,2,3}` ⊃ `tt(t)={3}` plus the widened `n(tl)` must not leak unconditioned `n(0)` terms into the `t`-domain stationarity.

### Expected Emit Pattern

`hhfair_mcp.gms` `stat_u`/`stat_c`/`stat_l`/`stat_n` should carry the log-derivative product gradient + the CES chain-rule terms, with the `n(tl)` widening confined to `n(0)=0` and **no** spurious unconditioned `n(0)`/`tl`-domain term in the `t`-domain rows. (Hypothesis — to be confirmed by the Day-0 trace, **after** the residual-emit compile is fixed.)

### Verification Methodology

```bash
# 1) Reproduce the Day-0 harness blocker (first error is $184; $257/$141 cascade — 13 errors):
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/hhfair.gms --keep-files --json /tmp/phase0_hhfair.json
# 2) NOTE (Day-8): --gdx does NOT bypass this — the presolve $include supplies the symbol
#    declarations (not just the solve), so the $184 widened-variable redeclaration fires
#    regardless. Fixing the residual emit requires the #1449 widened-VARIABLE fix (Sprint 30).
# 3) Compare the cold MCP objective to the NLP reference (87.159):
.venv/bin/python -m src.cli data/gamslib/raw/hhfair.gms -o /tmp/hhfair_mcp.gms --quiet && gams /tmp/hhfair_mcp.gms lo=0 o=/tmp/hhfair_mcp.lst ScrDir=/tmp   # run from the repo root (emits may $include repo-relative paths); o= -> /tmp
```

- **PROCEED (Case b):** once the residual MCP compiles, a localizable `stat_*` residual (likely on the CES/product rows) → emit fix.
- **REPLAN (Case c):** clean residual but cold PATH diverges → non-convexity (the `prod`/CES nest is non-convex) → Sprint 30 forcing.

### PROCEED/REPLAN Signal

> **🔴 DECIDED — REPLAN to Sprint 30 (Sprint 29 Day 8, 2026-06-30).** The Day-8 root-cause refined the Day-0 attribution: the residual emit's **first** error is **`$184` at `hhfair.gms(43)`** (under the `$onMultiR $include`), which cascades to `$257` (solve skipped) → the `$141` marginals-unassigned. **`$184` = the #1449 widened-symbol conflict, but for a VARIABLE:** the source declares `n(t)`; the MCP widens it to `n(tl)` (because `n` appears in `stat_m(tl)`/`stat_c`/`stat_n` over `tl`, from the bilinear `timemoney(t).. n(t)*(m(t)-…)`); the `$include` re-declaring `n(t)` collides with the widened `n(tl)` under `$onMultiR`. **The #1449 param `__pw`-companion fix does NOT transfer** — `n` is a *live nonlinear-stat coefficient* (not a value-copy), so it needs a companion *variable* + value-coupling (an emit-architecture workstream). **And the +Match needs the presolve warm-start anyway:** the cold MCP solves to MS-1 but **mismatches** (72.1 vs NLP 87.2) — non-convex (W301 nonlinear-equality on `utility` and `timemoney`; W303 bilinear on `timemoney`; plus the CES `prod(t,u(t)**ufact(t))` objective nest), so it cold-converges to a spurious KKT point; recovering the match requires warm-starting from the NLP optimum, which is exactly what the `$184` blocks. **→ REPLAN to Sprint 30** (the #1449 widened-variable presolve fix is the prerequisite; the CES verdict is unreadable until it lands). **hhfair Match stays mismatched — no headline +Match this sprint** (the only live P6 +Match). **sambal/qsambal #1112 check (Unknown 6.2):** both **match cold** already (Match-neutral); `xw(i,j)` is a parameter (cell weights), not a constraint dollar-condition routing through the offset-alias #1112 — **no #1112 consolidation needed.**

- **(historical — superseded by the Day-8 decision block above; `--gdx` guidance is wrong, see note)** GATED on the Day-0 harness build. Verdict is currently unobtainable (harness aborts on `$141`/`$257`). Step 1 of Sprint 29 work = make the residual emit compile (fix the `n(tl)` `$141`, ~~or use `--gdx`~~), then read the verdict. PROCEED if Case b on a CES/product `stat_*` row; REPLAN to Sprint 30 if Case c (non-convex `prod`/CES). This is the only cohort member that can still yield +1 Match. **_[Day-8 correction: the blocker is `$184` (the #1449 widened-VARIABLE `n`), not the `$141` dual-transfer domain; `--gdx` does NOT bypass it — the presolve `$include` provides the symbol declarations, not just the solve, so `$184` fires regardless. → REPLAN.]_**
- **Traced Fix-Surface (Day-0) — BLOCKER REPRODUCED + root localized (Sprint 29 Day 0, 2026-06-29):** `kkt_residual.py data/gamslib/raw/hhfair.gms --keep-files` aborts with **13 GAMS errors** (`$141` "symbol declared but no values assigned" + `$257` "solve not checked") — the verdict is still unobtainable, as expected. The retained scratch (`hhfair_mcp_presolve_residual.gms`) localizes the `$141` root: the **dual-transfer block emits multiplier inits over the widened `tl` domain** — e.g. line 103 `nu_budget.l(tl) = -(budget.m(tl))` (and `nu_income`/`nu_savings`/`nu_timemoney`, plus the `lam_dom2.l(t) = abs(dom2.m(t))` at line 107) — while the set split is `tl /'0','1','2','3'/` vs the active subset `t(tl) /'1','2','3'/`. The source equations populate `.m` only over `t`, so `.m('0')` is **declared-but-unassigned** → `$141`. The domain-widened variable `n(tl)` (with the `n('0')=0` fixup) is what propagates the wide `tl` domain onto the multipliers. ~~**Candidate fix surface:** the presolve dual transfer `src/emit/emit_gams.py` `_emit_nlp_presolve` (the `nu_<eq>.l = -(…​.m)` / `lam`/`piL`/`piU` transfers at ~1281–1310) should restrict the transfer domain to the **active subset** (the equation's actual domain), not the widened declaration domain.~~ **_[Day-8 correction — DISPROVEN: this candidate surface and the `--gdx` workaround were both wrong. The `$141` is a downstream cascade; the FIRST error is `$184` (the #1449 widened-VARIABLE `n`), so restricting the transfer domain does not fix the compile, and `--gdx` does NOT bypass it (the presolve `$include` supplies the symbol declarations, not just the solve). The real fix surface is the #1449 widened-variable presolve handling — REPLAN'd to Sprint 30 (see the decision block above).]_** Scratch retained at `output/kkt_residual_hhfair_*` during the trace.

# Epic 5 Scoping — CGE Walras' Law Degeneracy (camcge #1330)

**Status:** STUB / scoping observation (authored Sprint 29 Prep Task 7, 2026-06-27). Not an Epic-5 implementation plan — the structure + evidence so the in-sprint Priority-5 task is a write-up only (no `src/`).
**Origin:** #1330 camcge, REPLAN'd to Epic 5 at the Sprint 28 Day-11 Task-6 gate (2026-06-19) — see `docs/issues/ISSUE_1330_*.md` + `docs/planning/EPIC_4/SPRINT_28/SPRINT_LOG.md` §"Day 11".
**One-line scope:** the CGE Walras-law redundancy (a linearly-dependent market-clearing row + an unfixed price numéraire) is a **domain-specific structural preprocessing transformation**, not a general nlp2mcp emit change — it belongs in Epic 5. **Sprint 29 spends no `src/` budget on camcge** (Priority 5 = this write-up only).

---

## 1. The camcge Walras-degeneracy diagnosis (structural singularity)

camcge translates and compiles cleanly (post-#1245), and the **emitted KKT system is structurally correct** — at the NLP optimum (MODEL STATUS 2, obj 191.7346) the full CGE stationarity + market-clearing system evaluates to ≈ 0 at machine precision (`gdp_check ≈ -4.83e-10`, `stat_cd_check ≈ 1e-7`; three Sprint-27 investigation rounds confirmed this). The MCP nonetheless returns **MODEL STATUS 4 Infeasible at iteration 0** (cold) — the signature of a **singular Jacobian**, not an emit/AD bug.

**Root cause (Walras' law).** The goods-market clearing rows `equil(i)` and the labor-market clearing `lmequil(lc)` are **linearly dependent given household budget balance**: summing all market-clearing equations weighted by their prices yields the budget identity, so **one market-clearing row is redundant**. Combined with the fact that **no price numéraire is fixed** (CGE equilibria are homogeneous of degree 0 in prices — only relative prices are determined), the KKT Jacobian has a **one-dimensional nullspace** (the redundant row) plus a **price-scaling indeterminacy**. PATH cannot pivot from the valid KKT point: its linear system at the warm-start has no useful descent direction (the cold MCP shows `stat_cd` rows INFES at a uniform -0.2022 — the singular-system fingerprint).

**Not a localizable emit bug.** The Day-11 harness run reported verdict CASE_B with max-residual `stat_mps` (rel 1.05, raw -210), **but that is a fix-multiplier-transfer artifact**, not a real emit defect: `mps` is a fixed variable, the synthetic `mps_fx` equation has no NLP marginal, so `nu_mps_fx` is not warm-started and the residual equals exactly the (correct, hand-derived) gradient terms. The structural-singularity story is the real one: **inherent CGE degeneracy → Epic 5.**

---

## 2. CGE cohort survey — shared vs distinct degeneracies

**⚠️ Key finding (Unknown 5.1 — the assumption is INVERTED): the cohort does NOT uniformly share the Walras degeneracy.** Only **camcge #1330** is the inherent structural Walras singularity. The other "CGE cohort" issues are **distinct, ordinary emit/AD bugs** that nlp2mcp can fix without a domain-specific transformation. This **narrows** the Epic-5 scope to the single camcge Walras transformation (plus the related CES-conditioning observation), rather than a multi-transformation program.

| Issue | Model | Failure | Degeneracy class | Disposition |
|---|---|---|---|---|
| **#1330** | camcge | MS-4 Infeasible at iter 0 (singular Jacobian) | **Inherent Walras redundancy** (`equil`+`lmequil` dependent, no numéraire) | **Epic 5** — structural transformation |
| #1354 | camcge | `$141` compile error (3×) | **Emit bug** — phantom IndexOffset `nu_ieq(i±N)` enumeration (Pattern-C variant) | nlp2mcp backlog (emit fix) |
| #1355 | cesam2 | `$141` compile error | **Emit bug** — phantom IndexOffset `nu_COLSUM(i±N)` under `$(jj(i±N))` guards (same Pattern-C family as #1354) | nlp2mcp backlog (emit fix) |
| #1317 | twocge | `stat_tz`/`stat_tx` mis-emit | **Emit bug** — Pattern-C gate doesn't cover the plain-alias sum | nlp2mcp backlog (emit fix) |
| #1331 | twocge | EXECERROR=8 (empty MCP pair) | **Emit bug** — `eqpw`/`eqw` with `$(ord(r)<>ord(rr))` → `0=0` self-region rows; multipliers not fixed | nlp2mcp backlog (empty-equation multiplier fix) |
| #1251 | twocge | EXECERROR=8 (8 MCP pairing errors) | **Emit bug** — same empty-trade-equation (`r=rr → 0=0`) as #1331 | nlp2mcp backlog (duplicate-class of #1331) |
| #1070 | prolog | (historical) MS-5 CES singular Jacobian | **CES conditioning** — fractional exponents singular near bounds | *Largely resolved* — prolog now matches (Case-a healthy, #1247); a *related* conditioning observation, not the Walras redundancy |

**So:** the genuinely inherent-degeneracy member is **camcge #1330 alone**. #1354/#1355 (phantom-offset `$141`), #1317 (Pattern-C alias sum), and #1331/#1251 (empty-equation MCP pairing) are **compile-time emit defects** with localizable nlp2mcp fixes — they are *not* Walras-singular and do **not** need the Epic-5 transformation. #1070 prolog's CES singular Jacobian is a *related conditioning* family but is effectively resolved (prolog matches). The "CGE cohort" label conflated a structural degeneracy with a cluster of ordinary emit bugs that happen to occur in CGE models.

---

## 3. The named transformation + solution-preservation argument (Unknown 5.2)

**Transformation (CGE-domain structural preprocessing):**
1. **Redundant-row drop** — remove **one** market-clearing row (e.g. the labor-market `lmequil(lc)`, or one goods-market `equil(i)`). By Walras' law it is linearly dependent on the remaining market-clearing rows + household budget balance, so it carries no independent information; the dropped market clears automatically at the solution.
2. **Price-numéraire fix** — fix one price as the numéraire (e.g. a consumer price index `cpi = 1`, or a chosen good's price `p('numéraire-good') = 1`). This removes the price-level indeterminacy.

**Why it preserves the economic solution (paper argument for camcge):**
- **Redundancy (the dropped row is free).** Let the market-clearing rows be `g_i(x) = 0` (goods) and the labor row `h(x) = 0`, and let budget balance be `B(x, p) = 0`. Walras' law states `∑_i p_i·g_i + w·h ≡ B` identically in `x, p`. Hence given `B = 0` and `g_i = 0 ∀i`, the labor row `h = 0` follows (when `w ≠ 0`). Dropping `h` (or any single row by the symmetric argument) therefore loses **no** equilibrium constraint — the reduced system has the **same solution set** minus the rank-deficiency, so the Jacobian becomes nonsingular along that direction.
- **Numéraire (the price ray collapses to a point).** CGE equilibrium conditions are **homogeneous of degree 0 in prices**: scaling all prices by `λ > 0` leaves every excess-demand and zero-profit condition unchanged, so equilibria come as a **ray** `{λ·p* : λ > 0}`. The real allocation (all quantities) is identical along the ray. Fixing the numéraire selects the single representative `λ = λ₀` with no effect on quantities. Choosing `λ₀` consistent with camcge's documented NLP optimum (obj **191.7346**) reproduces that optimum exactly — the numéraire fix is a *selection*, not a *perturbation*.
- **Conclusion:** drop-one-row + fix-one-numéraire yields a **nonsingular** square MCP whose unique solution is camcge's NLP equilibrium (191.7346). The transformation is solution-preserving **on paper**; an in-Epic-5 implementation must confirm it empirically (open question Q3 below).

**Generality:** the *argument* (Walras redundancy + price homogeneity) is generic to closed CGE models, but **which** row is redundant and **which** price is the natural numéraire is **per-model** (depends on the model's closure + the SAM). So Epic 5 needs a per-model numéraire-selection rule, not a single hard-coded row/price.

---

## 4. Scope boundary — nlp2mcp vs Epic-5 / CGE-domain (Unknown 5.3)

- **Epic 5 (CGE-domain structural transformation):** the Walras-redundancy elimination + numéraire selection. It requires **model-class awareness** (recognising the market-clearing + budget-balance structure, choosing a redundant row, picking a numéraire) — that is economic-model-domain knowledge, not a general KKT/emit transformation. nlp2mcp emits a faithful KKT system; it should **not** silently drop a user equation or fix a price, because for a *non-degenerate* model that would change the problem. So this is a **CGE-aware preprocessing layer** (Epic 5), invoked only for models detected as Walras-degenerate.
- **Stays in nlp2mcp (general emit improvements — NOT Epic 5):** the *distinct* cohort bugs — the phantom-IndexOffset `$141` enumeration (#1354/#1355), the Pattern-C alias-sum mis-emit (#1317), and the **empty-equation multiplier pairing** (#1331/#1251, fixing the multiplier of a structurally-empty `$`-conditioned equation) — are all general nlp2mcp emit fixes that help these CGE models *and* any other model with the same shape. They keep a sliver of the cohort in nlp2mcp backlog.
- **The boundary:** *faithful KKT emission of the user's model* = nlp2mcp; *recognising and resolving an inherent economic-equilibrium rank-deficiency* = Epic 5. The Sprint-28 Day-11 Task-6 gate already established that **no general emit fix exists** for camcge's singularity (the emit is correct) — confirming the boundary sits exactly here.

---

## 5. Open questions for the Epic-5 task

1. **Numéraire-selection rule.** Is there a robust automatic rule (e.g. fix the price of the SAM's largest sector, or a CPI aggregate), or must each CGE model declare its numéraire?
2. **Degeneracy detection.** How does the preprocessing layer *detect* Walras-degeneracy (PATH basis-singularity report? a rank check on the market-clearing block? a model-structure heuristic?) without falsely flagging a well-posed model?
3. **Empirical confirmation.** Does drop-`lmequil` + fix-`cpi=1` actually drive camcge to MODEL STATUS 1 at 191.7346 (the §3 paper argument verified in GAMS)?
4. **Cohort generality.** Does the same transformation (with a per-model row/numéraire) recover any *other* genuinely Walras-degenerate model, or is camcge the only one in the corpus? (The §2 survey suggests camcge is currently the sole inherent case.)
5. **CES conditioning (#1070 family).** Is the CES singular-Jacobian-near-bounds conditioning a separate Epic-5 sub-topic (scaling / bound-init), or fully resolved now that prolog matches?

## Verification

```bash
test -f docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md && echo present
grep -Ei 'Walras|numéraire|redundant|equil|lmequil' docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md | head
grep -Ei '#1330|#1354|#1355|#1317|#1331|#1251|#1070' docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md | head
```

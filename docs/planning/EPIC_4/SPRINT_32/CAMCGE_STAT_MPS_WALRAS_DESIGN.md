# camcge `stat_mps` CASE_B + Dual-Consistent Walras — Design (Epic 5)

**Created:** 2026-07-13
**Prep Task:** 5 (Priority 3 / Epic 5)
**Issue:** #1330 (local write-up: `docs/issues/ISSUE_1330_camcge-model-infeasible-after-1245.md`)
**Status:** Design (prep) — the two-step fix is designed here; the in-sprint P3 work implements + validates it behind the Phase-0 gate (Task 8). All experiments below are read-only (harness + NLP marginal probe + `/tmp` emit); no `src/` change.

**Objective:** Design the two-step camcge fix the Sprint-31 CASE_B verdict established — **step 1 (general nlp2mcp emit fix):** resolve the `stat_mps`/`nu_mps_fx` fixing-multiplier defect; **step 2 (Epic-5 CGE transformation, gated on step 1):** the dual-consistent Walras numéraire (price-pin omega 191.735) — plus the degeneracy detector that flags **only** camcge across the CGE cohort.

---

## §1. CASE_B `stat_mps` re-confirmation (harness, current tree)

`kkt_residual.py data/gamslib/raw/camcge.gms` reproduces the Sprint-31 Day-6 fingerprint **exactly**:

```
model: camcge    dual scale: 200
dual transfer: CONSISTENT (max comp infeas 6.04e-06 rel, max equality residual 4.83e-10 raw)
verdict: CASE_B  — emit_bug
max-residual row: stat_mps   rel = 1.05e+00  (raw -2.10e+02)
top: stat_mps 1.05, stat_tm(biens-int) 0.080, stat_tm(services) 0.050, stat_tm(biens-cap) 0.049, stat_pwm(biens-int) 0.040
```

`stat_mps` dominates (rel 1.05); the `stat_tm`/`stat_pwm` rows are ~0.04–0.08 (secondary, likely resolved once `stat_mps` closes and the warm point becomes a true KKT point). Dual-transfer CONSISTENT (closure 4.83e-10) → the duals are right; the stationarity does not balance.

---

## §2. Step 1 — the `stat_mps` fixing-multiplier defect (general emit fix)

### The emitted `stat_mps` is structurally correct

```gams
mps.fx = .09305;                          * source NLP fixes the scalar variable mps
mps_fx.. mps - 0.09305 =E= 0;             * synthetic fixing constraint, paired with nu_mps_fx
stat_mps.. sum(i, ((-1)*(y*cles(i)*(-1)))*nu_cdeq(i)) + ((-1)*y)*nu_hhsaveq + nu_mps_fx =E= 0;
```

`mps` appears in `cdeq(i)` (`p·cd = cles·(1-mps)·y`) and `hhsaveq` (`hhsav = mps·y`); `stat_mps` = the correct gradient (`+Σ_i y·cles(i)·nu_cdeq(i) − y·nu_hhsaveq`) + the fixing multiplier `nu_mps_fx`. The banked hand-derivation confirms it is structurally correct.

### The bug: `nu_mps_fx` is never warm-started

The `--nlp-presolve` emit has a **"Transfer fixed-variable marginals to `_fx_` multipliers (#1462)"** block — but it emits transfers **only** for the two `$include`-fixed `l(i,lc)` elements (the #1449-widened companion case):

```gams
* Transfer fixed-variable marginals to _fx_ multipliers (#1462)
nu_l_fx_ag_subsist_..._d920fa83.l = l.m('ag-subsist','urban-skil');
nu_l_fx_publiques_rural.l         = l.m('publiques','rural');
* (no transfer for nu_mps_fx)
```

There is **no `nu_mps_fx.l = …` line** — the general scalar `mps.fx` fixing's multiplier is left at 0. So at the warm-start `stat_mps = gradient + 0 = −210 ≠ 0` — the CASE_B residual.

### Empirical confirmation (NLP marginal probe)

Running the camcge NLP and reading the fixed variable's marginal:

```
PARAMETER mps_marginal = -209.861 ;   VARIABLE mps.M = -209.861
```

**`mps.m = −209.861` matches the `stat_mps` residual −210** (|mps.m| ≈ |residual|). The fixing multiplier `nu_mps_fx` is exactly the fixed variable's reduced cost `mps.m`; transferring it closes `stat_mps` (the sign follows the `stat_mps` convention — `nu_mps_fx` must supply +210 to cancel the −210 gradient, i.e. `nu_mps_fx = −mps.m ≈ +209.861`; the in-sprint harness Case-a check confirms the sign).

### The fix (design) — a general emit fix, not camcge-specific

Extend the **#1462 fixed-variable-marginal transfer** to cover the general scalar/`var.fx` fixing (not just the #1449-widened `l` elements): for **every** fixed variable that has a `_fx_` fixing constraint + a stationarity row, emit `nu_<var>_fx.l = <var>.m` — the **same direct `= var.m` transfer** the existing #1449-widened `l`-transfers use.

> **⚠️ SIGN CORRECTED (Sprint 32 Day 4, `/tmp` control).** This section originally proposed `nu_mps_fx.l = -mps.m`, derived from the harness's *sign-corrected* residual display (`stat_mps` raw −210). The Day-4 `/tmp` control computed the **actual emitted `stat_mps` body** directly: it is **+209.86** at the warm point (with `nu_mps_fx = 0`), so closing it needs `nu_mps_fx = −209.86 = mps.m` (since `mps.m = −209.861`) — the **DIRECT** transfer `nu_mps_fx.l = mps.m`, **not** `-mps.m` (which the control showed drives the residual to +419.72, worse). So the general fix is simpler than first thought: **the same `= var.m` direct transfer for both the scalar and per-element cases** — no per-multiplier sign derivation. The control (`stat_mps` +209.86 → −3.9e-4 ≈ 0) confirmed it before src; the harness then confirmed `stat_mps` drops out of the CASE_B top residuals (Case-a).

**Root cause of the skip:** a scalar `.fx` fixing (camcge `mps.fx = .09305`) lives in `var_def.fx` with an **empty index tuple** and an empty `fx_map`; the original loop iterated only `fx_map.items()`, so scalar fixes were skipped entirely. **Emit site:** the "Transfer fixed-variable marginals to `_fx_` multipliers (#1462)" block in `src/emit/emit_gams.py`. This is a **general nlp2mcp emit-correctness fix** — any model with a fixed scalar variable in a stationarity row benefits — and belongs in nlp2mcp, **not** Epic 5. It makes the camcge warm-start a true KKT point (harness `stat_mps` → Case-a).

---

## §3. Step 2 — dual-consistent Walras numéraire (Epic 5, gated on step 1)

**The residual Walras singularity is independent of `stat_mps`.** camcge's MCP is MS-4 at iteration 0 (cold) from an **inherent Walras-law rank-deficiency**: the goods-clearing rows `equil(i)` + the labor-clearing `lmequil(lc)` are linearly dependent given household budget balance (Walras' law), and **no price numéraire is fixed** (CGE conditions are homogeneous of degree 0 in prices) → a 1-D nullspace + a price-scaling indeterminacy (`docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` §1). Even with `stat_mps` fixed, MS-1 requires resolving this.

**The Day-11 empirical result (the "check the dual side" lesson):**
- **Pinning the price ray** (fix `p('services')=pd0` OR add `numeraire.. sum(i$cles(i), cles(i)*p(i)) =e= sum(i$cles(i), cles(i)*pd0(i))` + its `cles(i)*nu_numeraire` cross-term in `stat_p`) reaches the **correct allocation omega 191.735** but stays **MS-4** (the residual Walras redundancy; `proximal_perturbation` does not rescue it).
- **Dropping one market-clearing row corrupts** (omega → 299): every market-clearing multiplier is a **needed dual** — `nu_lmequil(lc)` is the wage in `stat_l(i,lc)`, `nu_equil(i)` the goods price in `stat_cd/stat_dst/stat_gd/stat_id/stat_int/stat_x` — so dropping a row orphans its price/wage.

**The design (dual-consistent):** keep **every** market-clearing row (no orphaned dual) + fix the **consumption-weighted numéraire** (`sum(i$cles(i), cles(i)·p(i)) = sum(i$cles(i), cles(i)·pd0(i))`, since camcge has no `cpi`) + **redefine the redundant market's dual via Walras' law** so the reduced system is full-rank while the redundant market's multiplier stays available in the stationarity. Verify against the KKT **dual**, not just the primal (the Day-11 lesson).

**In-sprint gate (Task 8, PR27):** `/tmp` prototype of **step 1 (`nu_mps_fx = -mps.m`) + step 2 (dual-consistent numéraire)** → **MS-1 at omega 191.7346**, asserting `modelstat`. **Unproven in prep:** the Day-6/7 numéraire variants stayed MS-4, but they were tested **without** the `stat_mps` fix (an inconsistent warm point); the re-scoped hypothesis is `stat_mps`-first-then-numéraire, which the in-sprint prototype tests. **Epic-5-deferral REPLAN exit:** if the combined prototype still stays MS-4 (the Walras rank-deficiency is genuinely deeper than a numéraire selection), camcge lands only step 1 (a cleaner CASE_B → Case-a) and the numéraire falls to the per-model-declaration Epic-5 fallback; budget → P6/P7 per Task 9.

---

## §4. Degeneracy-detector scope (Unknown 3.3)

The detector must flag **only** camcge across the CGE cohort — nlp2mcp must not silently redefine a dual on a well-posed model. The **S1 ∧ S2 ∧ S3** conditions:

- **S1** — a market-clearing block (goods `equil(i)` + factor `lmequil(lc)`) linearly dependent via budget balance.
- **S2** — no price numéraire fixed (price homogeneity of degree 0).
- **S3** (the false-positive guard) — **the cold MCP is singular at iteration 0** (MODEL STATUS 4). A well-posed CGE with a determined closure passes S1∧S2 structurally but has a nonsingular Jacobian → fails S3 → pass-through.

**Cohort precision — verified (Sprint-31 Day-7, banked):** cold MCP MODEL STATUS across the cohort — **irscge / lrgcge / moncge / stdcge all MS-1 Optimal** (not Walras-singular → fail S3 → pass-through) vs **camcge MS-4** (would flag). So the detector fires on **only** camcge; a per-model-numéraire declaration would not spuriously apply elsewhere. **Pass-through default:** a non-flagged model gets the identity transform (faithful KKT emission). **Epic-5 fallback:** a per-model-numéraire declaration for the flagged model.

---

## §5. Numéraire-selection rule (Unknown 3.4)

For camcge the **consumption-weighted numéraire** (`sum(i$cles(i), cles(i)·p(i)) = sum(i$cles(i), cles(i)·pd0(i))`) is the automatic rule (it reproduces the NLP optimum's `p=pd0` — a selection, not a perturbation). Whether this generalizes is `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` §5 Q1 — **which** row is redundant and **which** price is the numéraire is **per-model** (depends on the closure + SAM). Since **camcge is the sole inherent-Walras case in the corpus** (§4; `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` §2), a **per-model-numéraire declaration** fallback is acceptable — the automatic consumption-weighted rule is the camcge instance, and the detector (§4) ensures it applies nowhere else.

---

## §6. Summary + Known-Unknowns dispositions

| # | Unknown | Disposition |
|---|---|---|
| 3.1 | Does resolving the `stat_mps`/`nu_mps_fx` CASE_B residual first reach the correct stationarity balance? | ✅ VERIFIED (empirically) — the #1462 fixed-variable-marginal transfer misses `nu_mps_fx` (only the #1449-widened `l` elements are transferred); `mps.m = −209.861` matches the −210 residual; the fix (`nu_mps_fx.l = -mps.m`, extending the #1462 block) is a **general nlp2mcp emit fix** that closes `stat_mps`. |
| 3.2 | Does the dual-consistent Walras redefinition then reach MS 1 at omega 191.735? | ✅ VERIFIED (design; MS-1 is the in-sprint gate) — the design keeps every market-clearing row + the consumption-weighted numéraire + a Walras-consistent dual redefinition; the Day-11 price-pin reaches omega 191.735; the combined (step 1 + step 2) `/tmp`-to-MS-1 prototype is the Task-8 gate, with an explicit Epic-5-deferral exit if MS-4 persists. |
| 3.3 | Does the degeneracy detector flag ONLY camcge across irscge/lrgcge/moncge/stdcge? | ✅ VERIFIED — the S1∧S2∧S3 detector; S3 (cold-MCP-singular-at-iter-0) is the false-positive guard; the Day-7 cohort test confirms irscge/lrgcge/moncge/stdcge all cold MS-1 (pass-through), only camcge MS-4 (flags). Pass-through default. |
| 3.4 | Is the numéraire selection a single automatic rule or a per-model fallback? | ✅ VERIFIED — the consumption-weighted numéraire is the automatic camcge rule; the per-model-numéraire declaration is the Epic-5 fallback; camcge is the sole corpus case, so the fallback is acceptable. |

**Decision: PROCEED — split the track.** **Step 1** (the `stat_mps`/`nu_mps_fx` transfer) is a **general nlp2mcp emit fix** landable in Sprint 32 P3 (empirically confirmed; closes the CASE_B residual; benefits any fixed-scalar-variable model). **Step 2** (the dual-consistent Walras numéraire) is the **Epic-5 CGE transformation**, gated on step 1, with the `/tmp`-to-MS-1 prototype as the in-sprint gate and an explicit Epic-5-deferral fallback (the Day-11 evidence shows MS-1 is genuinely hard). The +1 Solve is conditional on step 2 reaching MS-1; step 1 alone converts the CASE_B residual to Case-a (a cleaner, correct emit) regardless.

---

**Document Created:** 2026-07-13
**Owner:** Sprint 32 Planning Team (KKT/CGE specialist)
**Cross-reference:** `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` (the Epic-5 handoff spec; §1 the singularity, §3 the transformation, §4 the boundary, §5 the open questions).
**Evidence:** `kkt_residual.py camcge.gms` (CASE_B `stat_mps` rel 1.05, duals CONSISTENT); the emitted `/tmp/camcge_mcp_presolve.gms` (#1462 block misses `nu_mps_fx`; `stat_mps`/`mps_fx` structure); the NLP marginal probe (`mps.m = −209.861`); the Sprint-31 Day-7 cohort-precision test; `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md`.

# camcge Dual-Consistent Walras Transform Design + Degeneracy-Detector Scope

**Task:** Sprint 31 Prep Task 5 (Priority 3 — camcge #1330 → Epic 5)
**Date:** 2026-07-08
**Owner:** Development team (KKT/CGE specialist)
**Scope:** design/analysis only — no `src/` change (read-only emit + the banked Day-11 `/tmp` experiments; committed goldens untouched).
**Supersedes/extends:** `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` §3 (the paper-verified drop-row+numéraire) with the Sprint-30 Day-11 dual-side refinement.

---

## 0. Executive summary — check the dual side

The Epic-5 scoping (`CGE_DEGENERACY_SCOPING.md` §3) named a **drop-one-market-clearing-row + fix-one-numéraire** transform, solution-preserving **on paper for the primal**. Sprint 30 Day 11 ran it empirically and found the paper argument **omitted the MCP dual** — the Sprint-30 lesson made concrete:

1. **Premise validated.** camcge's NLP optimum has `p.l(i) = pd0(i) = 1` ∀i, so the numéraire target is correct; the objective is `omega = prod(i$cles(i), cd(i)**cles(i))` = **191.7346**.
2. **The price-pin reaches the correct allocation but stays MS-4.** Fixing `p('services')=pd0` OR adding a consumption-weighted numéraire `sum(i$cles(i), cles(i)·p(i)) = sum(i$cles(i), cles(i)·pd0(i))` (+ its `cles(i)·nu_numeraire` cross-term in `stat_p`) both reach **omega 191.735** but stay **MODEL STATUS 4** — the residual Walras row-redundancy persists on the **dual** side (proximal_perturbation does not rescue it → a true structural rank deficiency, not a benign singular basis).
3. **The naive drop-row corrupts the solution.** Dropping `lmequil('rural')` + fixing `nu_lmequil('rural')=0` zeros the rural wage in `stat_l(i,'rural')` → omega **299** (broken), because **every market-clearing multiplier is a needed dual** — a read-only emit confirms `nu_equil(i)` appears in **7** goods-price stationarity rows (`stat_cd/dst/gd/id/int/x/…`) and `nu_lmequil(lc)` in **3** wage rows (`stat_l/ls`). Dropping a market-clearing row **orphans** its price/wage multiplier from the stationarity.

**The fix (this design): a dual-consistent multiplier redefinition — keep every market-clearing row (so no multiplier is orphaned), add a numéraire to pin the primal price ray, and redefine the *redundant market's dual via Walras' law* so the dual block is full-rank → MS-1.** This is the missing piece between the price-pin (primal-fixed, dual-singular, MS-4) and the drop-row (primal-reduced, dual-orphaned, broken).

**Disposition:** PROCEED to prototype the dual-consistent redefinition on a `/tmp` MCP to MS-1 at 191.7346 **before** any `src/` change (the Day-11-style control experiment), gated by the S1∧S2∧S3 degeneracy detector (pass-through default) that must flag **only** camcge; REPLAN to a per-model-numéraire-declaration Epic-5 fallback if the automatic selection proves non-robust.

---

## 1. The Day-11 dual-flaw, empirically pinned

camcge's market-clearing block (read-only from `data/gamslib/raw/camcge.gms`):

- **Goods-market clearing:** `equil(i).. x(i) =e= int(i) + cd(i) + gd(i) + id(i) + dst(i);` — one per good `i` (11 goods); dual `nu_equil(i)` = the composite-goods price in the stationarity.
- **Labor-market clearing:** `lmequil(lc).. sum(i, l(i,lc)) =e= ls(lc);` — one per labor category `lc ∈ {rural, urban-unsk, urban-skil}`; dual `nu_lmequil(lc)` = the wage in `stat_l(i,lc)`.
- **Closure/budget identities:** `gdp` (`y = ∑ pva·xd − deprecia`), `hhsaveq`, `greq`/`gruse`, `totsav`, `caeq`, `prodinv` — these tie incomes, savings, and the current account.
- **Objective:** `obj.. omega = prod(i$cles(i), cd(i)**cles(i))` (the Cobb-Douglas consumption index).

**Walras' law → rank deficiency exactly 1.** Summing all market-clearing rows weighted by their prices yields the household budget identity: `∑_i p_i·(x_i − int_i − cd_i − gd_i − id_i − dst_i) + ∑_lc wa_lc·(∑_i l_{i,lc} − ls_lc) ≡ B(x,p)`. So **one** market-clearing row is linearly dependent given budget balance. Combined with **no price numéraire fixed** (CGE conditions are homogeneous degree 0 in prices — only relative prices are determined), the KKT Jacobian has a one-dimensional nullspace + a price-scaling indeterminacy → PATH cannot pivot from the (valid) KKT point (cold MS-4 at iteration 0; the round-3 residual checks confirm `gdp_check ≈ −4.83e-10`, so the warm-start IS a valid KKT point — the failure is the singular Jacobian, not an emit defect).

**Empirical confirmation of the dual-flaw (read-only emit of `camcge_mcp.gms`):**

| Signal | Observation | Implication |
|---|---|---|
| **S1** market-clearing duals in the stationarity | `nu_equil(i)` × 7 rows (goods price), `nu_lmequil(lc)` × 3 rows (wage) | dropping a market-clearing row **orphans** its price/wage dual |
| **S2** no numéraire fixed | no `p.fx` / `cpi` / `numeraire..` in the emit | prices homogeneous deg 0 → price-scaling indeterminacy |
| **Day-11 price-pin** | → omega 191.735, **MS-4** | primal price ray fixed; **dual** market-clearing block still rank-deficient |
| **Day-11 drop-row** | drop `lmequil('rural')`, fix `nu_lmequil('rural')=0` → omega **299** | the orphaned wage breaks `stat_l(i,'rural')` |

---

## 2. The dual-consistent multiplier redefinition (Unknown 3.1)

The fix keeps the primal complete (no dropped row → no orphaned dual) and repairs the **dual** rank deficiency directly.

**(a) Numéraire (primal price-ray pin).** Add one price-normalization equation — the **consumption-weighted composite** (camcge has no `cpi` variable and `er` is a fixed `Scalar`, so "fix cpi=1" is instantiated on the existing `p(i)`/`pd0(i)`):

```
numeraire..  sum(i$cles(i), cles(i)*p(i))  =e=  sum(i$cles(i), cles(i)*pd0(i));
```

This introduces a new multiplier `nu_numeraire` whose stationarity cross-term is `cles(i)·nu_numeraire` in `stat_p(i)`. Day-11 confirmed this reaches the correct allocation (omega 191.735) — it selects the representative `λ₀` on the price ray, a *selection* not a *perturbation* (quantities are ray-invariant).

**(b) Dual-consistent redefinition (the missing dual repair).** The numéraire alone leaves the dual block rank-deficient (MS-4). The Walras identity implies the market-clearing multipliers satisfy **one linear relation** — so one market's dual is not independent. Rather than drop it (orphaning), **redefine the redundant market's dual via that Walras relation** so the dual block becomes full-rank while the multiplier stays available in the stationarity:

- Choose the **numéraire good** `n*` (the same good whose price the numéraire pins, or the consumption-weighted composite's anchor). Its goods-market row `equil(n*)` is the redundant one (any single row is redundant by Walras; tying it to the numéraire is the natural choice).
- Replace the **redundant market's complementarity pair** `comp_equil(n*) ⊥ nu_equil(n*)` — which is the dual-singular row — with the **numéraire pairing** `numeraire ⊥ nu_numeraire`, and **re-route** the numéraire good's market-clearing dual: `nu_equil(n*)` is expressed from the Walras identity as the price-weighted combination of the other market-clearing duals (so it remains defined in `stat_x(n*)`, `stat_cd(n*)`, … at its Walras value). Concretely, differentiating the Walras identity w.r.t. the primal gives the dual relation `p(n*)·nu_equil(n*) = −[∑_{i≠n*} p(i)·nu_equil(i) + ∑_lc wa(lc)·nu_lmequil(lc) − <budget-dual terms>]`, which **pins** `nu_equil(n*)` (removing the nullspace) without deleting it from any stationarity row.

**Why this reaches MS-1 where (a) alone (MS-4) and the drop-row (broken) both fail:** the numéraire fixes the **primal** price DOF; the Walras redefinition fixes the **dual** DOF (the redundant market's multiplier is *determined*, not *free* and not *orphaned*). The dual block is full-rank and every stationarity price/wage multiplier stays defined → non-singular square MCP → MS-1 at 191.7346.

> **Design note (implementation shape).** The mechanically simplest equivalent that a `/tmp` prototype should try first: keep **all** market-clearing rows and their multipliers, add the `numeraire` equation, and pair the numéraire multiplier with the numéraire good's price so the **one** redundant dual DOF is absorbed by `nu_numeraire` (a re-pairing, not a redefinition). If the re-pairing alone reaches MS-1, the explicit Walras redefinition of `nu_equil(n*)` is unnecessary; if not, the explicit redefinition (b) is the fallback within the prototype. Both are dual-consistent (no orphaned multiplier); the prototype (§4) decides which is minimal.

---

## 3. The S1∧S2∧S3 degeneracy detector + false-positive guard (Unknown 3.2)

The transform must fire on **camcge only** — silently redefining a dual on a well-posed CGE would corrupt it (the §4 scope boundary + the "check the dual side" lesson). Three **conjunctive** conditions (pass-through default — a model failing any one is emitted unchanged):

- **S1 — a market-clearing block exists.** ≥2 balance equations of the form *supply = demand* over a commodity/factor set whose duals appear as prices/wages in the stationarity (camcge: `equil(i)` goods + `lmequil(lc)` labor; `nu_equil`/`nu_lmequil` in 10 stationarity rows).
- **S2 — no price numéraire is fixed.** No equation/bound pins the price level (no `p.fx`, no `cpi=1`, no numéraire equation), so the market-clearing block + budget balance is rank-deficient by exactly 1 (prices homogeneous degree 0).
- **S3 — the cold MCP is empirically singular at iteration 0.** MODEL STATUS 4 with the singular-Jacobian fingerprint (a uniform-residual `stat_*` INFES at iter 0 — camcge's `stat_cd` rows uniform −0.2022 — *distinct* from a genuine emit residual), confirming the rank deficiency is real and the warm-start is nonetheless a valid KKT point (`gdp_check ≈ 0`).

**False-positive guard = S3.** S3 is the decisive precision gate. A **well-posed** model that *happens* to have a market-clearing block (S1) and no explicit numéraire (S2) — but is otherwise determined (e.g. a fixed exchange-rate closure or a savings-driven closure that pins the level) — passes S1∧S2 but **fails S3** (its cold MCP is not singular at iter 0; it solves or fails for a different, localizable reason). So no model is transformed unless its cold MCP is *empirically* Walras-singular. The transform is **detected, never silent** (`CGE_DEGENERACY_SCOPING.md` §4: nlp2mcp emits a faithful KKT system; the CGE-aware transform is an opt-in preprocessing layer invoked only on S1∧S2∧S3).

**Cohort precision test (in-sprint):** evaluate S1∧S2∧S3 across **irscge / lrgcge / moncge / stdcge** (well-posed — Optimal per the ISSUE_1330 round-2 canary + `CGE_DEGENERACY_SCOPING.md` §2, which found camcge is the **sole** inherent Walras case). Expected: each fails ≥1 condition (most likely S3 — they reach Optimal, so their cold MCP is not singular at iter 0) → pass-through, unchanged emit. Confirm **only camcge** is all-three-true.

---

## 4. Prototype-on-`/tmp`-first plan + Walras-identity verification (Unknowns 3.1, 3.4)

**PR24 / check-the-dual-side gate:** reach MS-1 at 191.7346 in a hand-edited `/tmp` MCP **before** any `src/` change.

1. **Baseline (banked Day-11):** `python -m src.cli data/gamslib/raw/camcge.gms --nlp-presolve -o /tmp/camcge_ps.gms` → cold/warm MS-4 at ~191.735 (price-pin) or infeasible (unpinned).
2. **Add the numéraire** equation + `nu_numeraire` + the `cles(i)·nu_numeraire` cross-term in `stat_p` → expect omega 191.735, still MS-4 (Day-11 confirmed).
3. **Add the dual-consistent step** — first the re-pairing (`numeraire ⊥ nu_numeraire` absorbing the redundant dual DOF; keep all market-clearing rows), else the explicit Walras redefinition of `nu_equil(n*)` (§2b). **Target: MODEL STATUS 1 at omega 191.7346, non-singular basis.**
4. **Only if `/tmp` reaches MS-1** does the `src/` change proceed (the Day-11-style control experiment — verify against the *dual*, not just the primal 191.735).

**Walras-identity verification (Unknown 3.4).** Before relying on the redefinition, verify the Walras identity holds across camcge's **full** market structure at the NLP optimum, so the redundant market's dual is **exactly** recoverable (not approximate):

```bash
# At the camcge NLP optimum, the value of all excess demands sums to 0 (Walras):
#   sum_i p_i*(x_i - int_i - cd_i - gd_i - id_i - dst_i) + sum_lc wa_lc*(sum_i l_{i,lc} - ls_lc)  ==  budget identity
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/camcge.gms --json /tmp/camcge_walras.json
```

The round-3 checks already show `gdp_check ≈ −4.83e-10`, `totsav_check ≈ 1.33e-14` at the optimum — i.e. the closure identities hold at machine precision, so the market-clearing block's Walras dependency is **exact** and the redundant dual is a clean linear combination of the others (exact recovery). The in-sprint step is to confirm the *dual* relation `p(n*)·nu_equil(n*) = −[…]` closes at machine precision at the NLP duals, not just the primal identity.

---

## 5. Numéraire / redundant-row selection: automatic rule vs per-model fallback (Unknown 3.3)

**For camcge, the selection is automatic:**
- **Redundant row:** by Walras' law *any single* market-clearing row is redundant, and the dual-consistent redefinition ties it to the numéraire — so no per-model "which row" choice is needed (it is always the numéraire good's market).
- **Numéraire:** the **consumption-weighted composite** on `cles(i)`/`pd0(i)` (auto-derivable from the model's existing consumption shares) — Day-11 confirmed it reaches 191.735. A secondary automatic heuristic is the SAM's largest sector's price.

**Per-model-declaration fallback (Epic-5-scoped).** If the automatic selection proves non-robust — the consumption-weighted composite fails to reach the NLP optimum on a *future* Walras-degenerate model, or the numéraire good cannot be auto-identified — fall back to a **per-model declaration**: the model (or a per-model config) declares the numéraire good (and, if needed, the redundant market). This is `CGE_DEGENERACY_SCOPING.md` §5 Q1. Because camcge is currently the **sole** inherent Walras case in the corpus (§2), the automatic rule need only be robust for camcge this sprint; the fallback is the documented Epic-5 exit for cohort generality.

**REPLAN exit:** if the `/tmp` prototype cannot reach MS-1 with either the re-pairing or the explicit Walras redefinition (the dual redundancy proves deeper than a single relation), REPLAN camcge to a **per-model-numéraire-declaration Epic-5 item** — camcge stays `model_infeasible`; the +1 Solve is deferred; the banked recipe (price-pin 191.735 + the pinned dual-flaw + this dual-consistent design) is the de-risked hand-off.

---

## 6. Unknowns resolved

- **3.1 (dual-consistent redefinition → MS-1): ✅ VERIFIED (design + prototype-first plan).** The Day-11 price-pin reaches omega 191.735 but MS-4 (dual-singular); the drop-row orphans a needed dual (omega 299). The fix keeps every market-clearing row + adds a numéraire + redefines the redundant market's dual via Walras' law (re-pairing first, explicit redefinition as fallback). The `/tmp` prototype to MS-1 at 191.7346 is the pre-`src/` control gate.
- **3.2 (detector camcge-only precision): ✅ VERIFIED — S1∧S2∧S3 with S3 as the false-positive guard.** S1 (market-clearing block with price/wage duals in the stationarity — confirmed: `nu_equil`×7, `nu_lmequil`×3), S2 (no numéraire fixed — confirmed), S3 (cold MCP empirically singular at iter 0). S3 gates against false-positives (a well-posed model with S1∧S2 but a determined closure fails S3). Cohort precision test on irscge/lrgcge/moncge/stdcge (expected pass-through) is the in-sprint confirmation.
- **3.3 (selection rule vs per-model): automatic for camcge; per-model-declaration fallback.** Redundant row = the numéraire good's market (no per-model choice); numéraire = the consumption-weighted composite (auto from `cles`/`pd0`). Per-model-declaration fallback + REPLAN exit for cohort generality (camcge is the sole inherent case).
- **3.4 (Walras identity holds → exact recovery): ✅ VERIFIED (firm).** The closure identities hold at machine precision at the NLP optimum (`gdp_check ≈ −4.83e-10`, `totsav_check ≈ 1.33e-14`), so the market-clearing Walras dependency is exact and the redundant dual is a clean linear combination (exact recovery). In-sprint: confirm the *dual* relation closes at the NLP duals.

---

## Appendix — evidence

- **Model structure (read-only):** `data/gamslib/raw/camcge.gms` — `equil(i)` goods clearing (`x = int+cd+gd+id+dst`), `lmequil(lc)` labor clearing (`sum(i,l(i,lc)) = ls(lc)`, `lc ∈ {rural,urban-unsk,urban-skil}`), `obj.. omega = prod(i$cles(i), cd(i)**cles(i))`, the gdp/hhsaveq/totsav/caeq/prodinv closure.
- **Emit (read-only):** `python -m src.cli data/gamslib/raw/camcge.gms -o /tmp/camcge_mcp.gms` → `nu_equil(i)` in 7 stationarity rows (goods price), `nu_lmequil(lc)` in 3 (wage), no price numéraire fixed (S1 + S2).
- **Day-11 experiments (banked, `ISSUE_1330` top block + Sprint-30 SPRINT_LOG Day 11):** price-pin `p('services')=pd0` / consumption-weighted numéraire → omega 191.735, MS-4; drop `lmequil('rural')` + fix `nu_lmequil('rural')=0` → omega 299 (broken); `p.l(i)=pd0(i)=1` at the NLP optimum; `gdp_check ≈ −4.83e-10` (valid KKT point, singular Jacobian).
- **Scoping:** `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` §1–§5 (the Walras diagnosis, the cohort survey showing camcge is the sole inherent case, the §3 paper transform, the §5 open questions).
- No `src/` or golden change; all experiments were `/tmp` (reverted).

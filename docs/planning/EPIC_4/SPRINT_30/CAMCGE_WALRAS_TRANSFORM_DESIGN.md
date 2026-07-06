# camcge → Epic 5 Walras Transformation — Implementation Design (Priority 6)

**Task:** Sprint 30 Prep Task 7 (Priority 6 foundation — turns the paper-verified Epic-5 transformation into an implementation design)
**Date:** 2026-07-06
**Owner:** Development team (CGE / Epic-5)
**Scope:** design/analysis only — no `src/` change. Grounded in a read of `data/gamslib/raw/camcge.gms` (variable/equation structure) + the Sprint-27/28 `ISSUE_1330` diagnosis + the Sprint-29 `CGE_DEGENERACY_SCOPING.md` paper argument.

---

## 0. Executive summary

`CGE_DEGENERACY_SCOPING.md` proved (on paper) that camcge's MS-4-at-iteration-0 is an **inherent CGE Walras-law rank-deficiency** — the goods-market `equil(i)` and labor-market `lmequil(lc)` clearing rows are linearly dependent given household budget balance (one row is redundant), and no price numéraire is fixed (CGE equilibria are homogeneous of degree 0 in prices) → a singular KKT Jacobian PATH cannot pivot from. The fix is a **CGE-domain structural preprocessing transformation** (drop one redundant market-clearing row + fix a price numéraire), solution-preserving on paper. This task resolves the three `§5` open questions into an implementation design and **grounds it in camcge's actual structure**, surfacing one refinement:

- **Grounding refinement (this task): camcge has NO `cpi` variable, and `er` is a fixed `Scalar` (= 0.21), not a free numéraire.** The scoping doc's canonical "fix-`cpi=1`" is a *generic placeholder* (its §3 itself says "e.g. a consumer price index `cpi = 1`, or a chosen good's price"). For camcge concretely, the numéraire must be instantiated on an **existing** variable: a **base-consumption-weighted composite-price index** pinned to its calibrated level — `sum(i$cles(i), cles(i)*p(i)) =e= sum(i$cles(i), cles(i)*pd0(i))` — which *is* a CPI = 1 normalization (the prices calibrate to `p.l(i)=pd0(i)`), reconciling the scoping doc with the model. This is the single most important input the empirical P6 Day-0 run needs.
- **Detection heuristic (Q2):** a **market-clearing-block rank check** (the primary signal) corroborated by the **MS-4-at-iteration-0 / PATH basis-singularity** signature, gated by a **structural precondition** (≥ 2 market-clearing rows + an aggregate budget-balance identity + price homogeneity). The **false-positive guard is the correctness gate**: default = **pass through untouched**; transform **only** when *all three* fire — so a well-posed CGE that already fixes a numéraire (full-rank market-clearing block) is never touched.
- **Selection rule (Q3):** drop the **labor-market row `lmequil(lc)`** (the smaller block; Walras-redundant) + add the consumption-weighted numéraire above. Per-model, because *which* row is redundant and *which* price is the natural numéraire depend on the model's closure — so the rule ships with a **per-model declaration fallback** (opt-in), acceptable because camcge is the corpus's **sole** inherent Walras case.
- **Empirical confirmation (Q1 → P6 Day-0):** the drop-`lmequil` + fix-the-numéraire GAMS run must reach **MODEL STATUS 1 at omega 191.7346** with a non-singular PATH basis; the cohort-generality check confirms camcge is the only model flagged.

---

## 1. camcge — the actual structure (grounding the design)

`data/gamslib/raw/camcge.gms` (Cameroon CGE, SEQ=81; `solve camcge maximizing omega using nlp;`, NLP ref **omega = 191.7346**):

| Structural element | camcge form (`file` evidence) | role in the degeneracy |
|---|---|---|
| **Goods-market clearing** | `equil(i).. x(i) =e= int(i) + cd(i) + gd(i) + id(i) + dst(i);` (over sectors `i`) | one of the two market-clearing blocks |
| **Labor-market clearing** | `lmequil(lc).. sum(i, l(i,lc)) =e= ls(lc);` (over labor categories `lc`) | the **redundant** row (Walras) — the drop candidate |
| **Budget balance / income** | `y`, `hhsaveq.. hhsav =e= mps*y`, `totsav`, `greq`, `caeq` (the SAM income/savings identities) | the identity that makes one market-clearing row linearly dependent |
| **Consumption behavior** | `cdeq(i).. p(i)*cd(i) =e= cles(i)*(1 - mps)*y;` | Cobb-Douglas; ties `cd(i)` to the composite price `p(i)` and income `y` |
| **Objective (welfare)** | `obj.. omega =e= prod(i$cles(i), cd(i)**cles(i));` | Cobb-Douglas welfare index over `cd(i)`, weights `cles(i)` |
| **Prices (free, homogeneous)** | `p(i)`, `pd(i)`, `px(i)`, `pk(i)`, `pva(i)`, `wa(lc)`; all `.lo = .01`; calibrated `p.l(i)=pd0(i)` | the price ray — homogeneous of degree 0 ⇒ the numéraire target |
| **Nominal partial anchor** | `er` = `Scalar / .21 /` (fixed); `pmdef/pedef` tie *traded* prices to world prices × `er` | anchors traded prices only — **not** a full domestic price-level numéraire; **no `cpi` variable exists** |

**Why the price level is still free despite `er`.** `er` (a fixed scalar) pins the *traded*-goods domestic prices via `pmdef(it).. pm(it)=pwm(it)*er*(1+tm(it))` and `pedef`. But the **domestic (non-traded) price level** — the common scale of `p(i)`/`pd(i)`/`wa(lc)` — is determined only by the market-clearing + zero-profit system, which is homogeneous of degree 0 in those prices. So the price ray persists (the scoping-doc "no numéraire fixed" holds for the domestic level), and `er` being fixed does **not** remove the singularity. This is exactly why fixing a domestic price index (§3) is required.

**The two degeneracy directions (confirmed structurally correct at the NLP optimum — `gdp_check ≈ -4.83e-10`, `stat_cd_check ≈ 1e-7`, three Sprint-27 rounds):**
1. **Redundant market-clearing row** (`equil` + `lmequil` linearly dependent given the SAM budget identities) → a one-dimensional nullspace.
2. **Domestic price-level indeterminacy** (homogeneity of degree 0) → the price ray, unfixed by `er`.

Both must be removed for the KKT Jacobian to be non-singular; removing only one leaves the other singular direction.

---

## 2. Degeneracy-detection heuristic + false-positive guard (Unknown 6.2, `§5` Q2)

The heuristic runs at CGE-preprocessing time and must **transform only genuinely-degenerate models** — silently dropping a user row / fixing a price on a well-posed model would corrupt a correct problem. So the **default is pass-through**, and the transform fires only on a **conjunction** of three independent signals (any one alone is insufficient):

| Signal | Test | Why it is necessary (and insufficient alone) |
|---|---|---|
| **S1 — market-clearing rank deficiency** (primary) | Assemble the market-clearing block (`equil(i)` + `lmequil(lc)`) Jacobian at the calibrated/warm-start point; compute its numerical rank (SVD / QR with a tolerance). Flag if `rank < #rows` (a nullspace exists). | Directly detects the Walras redundancy. *Insufficient alone:* a merely ill-scaled (but full-rank) block could read as near-deficient — needs S2/S3 to avoid a scaling false positive. |
| **S2 — singular-Jacobian solve signature** (corroborating) | The full-MCP `kkt_residual.py` verdict + a **cold PATH solve**: **MODEL STATUS 4 Infeasible at iteration 0** with a uniform `stat_*`-row INFES (camcge's `stat_cd` uniform −0.2022) and a PATH **basis-singularity** report. | Confirms the rank-deficiency actually defeats PATH (not just a benign near-dependency). *Insufficient alone:* MS-4-at-iter-0 can also come from a genuine emit bug (Case b) — must be paired with S1 (rank) + the residual-clean check to isolate *structural* singularity from an emit defect. |
| **S3 — structural precondition** (gating) | A model-structure signature: **≥ 2 market-clearing rows** (goods + factor) **+** an aggregate **budget-balance / income identity** (`y`/`hhsaveq`/`totsav`) **+** price homogeneity (all-prices-scale symmetry in the market-clearing + zero-profit block, **no** existing numéraire constraint). | Restricts the heuristic to the CGE-equilibrium class. *Insufficient alone:* structure ≠ degeneracy (a well-posed CGE that already fixes a numéraire has this structure but is full-rank). |

**Decision rule (the false-positive guard):**

```
if S1 (rank < #market-clearing rows)  AND  S2 (MS-4-at-iter-0 + residual-clean + basis-singular)  AND  S3 (CGE structure, no existing numéraire):
    → TRANSFORM (drop redundant row + fix numéraire), §3
else:
    → PASS THROUGH untouched   ← the conservative default (a well-posed model is NEVER transformed)
```

**Why this cannot corrupt a well-posed model.** A well-posed CGE that *already* fixes a numéraire (or is otherwise non-degenerate) has a **full-rank** market-clearing block (S1 fails) and **solves** (S2 fails: no MS-4-at-iter-0). Either failure defaults to pass-through. The transform requires the *conjunction*, and the **residual-clean** sub-check inside S2 (the emitted KKT ≈ 0 at the NLP optimum) is what distinguishes an *inherent structural* singularity (transform) from an *emit bug* (Case b — route to the general emit path, NOT the transform). The guard is deliberately conservative: a false *negative* (a degenerate model left untouched) merely fails to gain a Solve; a false *positive* (a well-posed model transformed) would corrupt output — so the rule is tuned to never false-positive, at the cost of possibly missing an exotic degenerate model (acceptable — camcge is the sole known case, §4).

**Reliability caveat (feeds the Task-6 REPLAN judgment).** S1's rank test needs a numerical tolerance, and rank-by-tolerance is the fragile piece. The Task-6 assessment therefore treats the *automatic* heuristic as PROCEED-conditional and ships a **per-model declaration fallback** (§3) so P6 lands camcge's +1 Solve even if the auto-detector is deferred.

---

## 3. Redundant-row + numéraire selection (Unknowns 6.1, 6.3, `§5` Q1/Q3) — reproduces 191.7346 on paper

### 3.1 Redundant-row drop

**Rule:** drop **one** market-clearing row. For camcge, drop the **labor-market row `lmequil(lc)`** (the smaller block — `|lc|` labor categories vs `|i|` sectors — minimizing the perturbation surface). By Walras' law it is linearly dependent on the remaining goods-market rows + the budget identities, so it carries no independent information; the labor market clears automatically at the solution.

**Solution-preservation (paper).** Let the goods rows be `g_i(x)=0`, the labor row `h(x)=0`, and budget balance `B(x,p)=0`. Walras' law: `∑_i p_i·g_i + ∑_lc wa_lc·h_lc ≡ B` identically. Given `B=0` and all `g_i=0`, `h=0` follows (when `wa ≠ 0`). Dropping `h` (`lmequil`) loses **no** equilibrium constraint — the reduced system has the **same solution set** minus the rank-deficiency.

### 3.2 Numéraire fix — the camcge-concrete instantiation

**Rule:** fix one price normalization to pin the domestic price level. Because camcge has **no `cpi` variable** (§1), instantiate the numéraire as a **base-consumption-weighted composite-price index** held at its calibrated value:

```gams
numeraire..  sum(i$cles(i), cles(i)*p(i))  =e=  sum(i$cles(i), cles(i)*pd0(i));
```

where `cles(i)` are the consumption shares (the same weights as the `omega` objective) and `pd0(i)` the calibrated base domestic prices (the model already warm-starts `p.l(i)=pd0(i)`). This **is** a "CPI = 1" normalization expressed on camcge's existing `p(i)` — a consumption-basket price index equal to its base-year level.

**Solution-preservation (paper).** CGE equilibrium conditions are **homogeneous of degree 0 in prices**: scaling all domestic prices by `λ>0` leaves every excess-demand and zero-profit condition unchanged, so equilibria form a **ray** `{λ·p* : λ>0}`; the real allocation (all quantities `x`,`cd`,`l`,…) is identical along the ray. The numéraire constraint selects the single representative with `sum(i,cles·p) = sum(i,cles·pd0)`, i.e. **λ = 1** (the calibrated level, since `p* = pd0` at calibration). It is a **selection, not a perturbation** — quantities are untouched, so the Cobb-Douglas welfare `omega = prod(i$cles, cd(i)**cles(i))` evaluates to the **calibrated optimum 191.7346**. Combined with §3.1, the reduced square MCP is **non-singular** and its unique solution is camcge's NLP equilibrium.

**Why a consumption-weighted index (not a single good's price).** Fixing a single `p('sector')` also selects the ray, but a `cles`-weighted basket (a) mirrors the welfare metric so the numéraire is economically the consumer's cost-of-living, and (b) is robust if any single base price is near its `.lo=.01` floor. Either works on paper; the basket is the recommended default, `p('numéraire-good')=pd0` the fallback.

### 3.3 Selection is per-model (Unknown 6.3) → the declaration fallback

*Which* row is redundant and *which* price is the numéraire depend on the model's closure + SAM. The general *argument* (Walras redundancy + homogeneity) is generic, but the *instantiation* is per-model. So the rule ships two tiers:
1. **Automatic (stretch):** the detection heuristic (§2) picks the factor-market row (`lmequil`) to drop + the consumption-weighted index to fix, from the structural signature.
2. **Per-model declaration (fallback, opt-in):** the model author (or a camcge-specific entry) declares the drop-row + numéraire. **Acceptable because camcge is the sole inherent case** (§4) — a single declaration lands the +1 Solve without a general auto-detector. This is the Task-6 REPLAN target if the automatic heuristic proves unreliable.

---

## 4. Empirical-confirmation experiment + cohort-generality check (Unknown 6.1, `§5` Q1/Q4)

### 4.1 The P6 Day-0 empirical run (gates the whole priority)

```bash
# 1. Emit camcge MCP (warm-started), then hand-apply the transform on a /tmp copy:
.venv/bin/python -m src.cli data/gamslib/raw/camcge.gms --nlp-presolve -o /tmp/camcge_ps.gms
#    - delete/comment the lmequil(lc) market-clearing row + its paired multiplier/comp row
#    - add:  numeraire.. sum(i$cles(i), cles(i)*p(i)) =e= sum(i$cles(i), cles(i)*pd0(i));  (+ its multiplier)
# 2. Solve cold from repo root (the emit's $include is repo-relative):
cd <repo> && gams /tmp/camcge_ps.gms lo=2
# EXPECT:  **** MODEL STATUS 1 Optimal   (was: MODEL STATUS 4 Infeasible at iteration 0)
#          omega = 191.7346              (the NLP optimum — solution preserved)
#          PATH basis non-singular (the rank deficiency removed)
```

**PROCEED** if MS 1 at 191.7346 with a non-singular basis (Unknown 6.1 ✅). **REPLAN** to a deeper Epic-5 diagnosis if it does not reach MS 1 (the transform premise invalid) — then the Class-B `stat_pz` general-emit work (P7) absorbs the freed budget (Task 6).

### 4.2 Cohort-generality check (is camcge the sole inherent case?)

Run the detection heuristic (§2) across the CGE cohort — `camcge` + `irscge`/`lrgcge`/`moncge`/`stdcge`:

```bash
for m in camcge irscge lrgcge moncge stdcge; do
  .venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/$m.gms   # S2 signature
  # + the market-clearing-block rank check (S1) at the warm-start
done
# EXPECT: only camcge flagged (S1∧S2∧S3). irscge/lrgcge/moncge/stdcge already solve/match
#         (model_optimal_presolve + compare_objective_match) → full-rank block → PASS THROUGH.
```

This is the **false-positive validation** (§2): the four cohort models are known-good (Sprint-29 Unknown 5.1 — they are *distinct ordinary emit bugs* or already-matching, **not** Walras-singular), so a heuristic that flags any of them has a false positive and must be tightened (or the automatic tier deferred to the declaration fallback). Expected outcome: **only camcge** flagged → the guard is reliable on the cohort.

---

## 5. The nlp2mcp / Epic-5 boundary (Unknown 5.3 carryforward)

- **Epic 5 (CGE-domain structural preprocessing) — this transform:** the Walras-redundancy elimination (drop-row) + numéraire selection. It needs **model-class awareness** (recognising the market-clearing + budget-balance structure, choosing a redundant row + a numéraire) — economic-domain knowledge, invoked **only** for detected-degenerate models (§2 guard). nlp2mcp emits a *faithful* KKT system; it must **not** silently drop a user row / fix a price for a non-degenerate model.
- **Stays in nlp2mcp (general emit — NOT Epic 5):** the **Class-B CGE `stat_pz`** coefficient discrepancy (irscge/lrgcge/moncge, `docs/issues/ISSUE_classB_cge_stat_pz.md`) — confirmed **NOT Walras** (dual transfer CONSISTENT, all `pz` cross-terms present, a coefficient/scaling discrepancy) — is a general-emit fix (Sprint-30 **P7**), one fix across several models. Likewise the phantom-offset `$141` (#1354/#1355), the Pattern-C alias sum (#1317), and the empty-equation multiplier pairing (#1331/#1251) are ordinary emit bugs.
- **The boundary:** *faithful KKT emission of the user's model* = nlp2mcp; *recognising + resolving an inherent economic-equilibrium rank-deficiency* = Epic 5. camcge is the sole model on the Epic-5 side.

---

## 6. Open questions resolved (maps `CGE_DEGENERACY_SCOPING.md` §5 → this design)

| §5 open question | Resolution (this design) |
|---|---|
| **Q1 — numéraire-selection rule** | A **base-consumption-weighted composite-price index** pinned to its calibrated level (§3.2), instantiated on camcge's existing `p(i)`/`pd0(i)` (no `cpi` variable exists); a single good's price `p('numéraire-good')=pd0` as fallback. Automatic tier + per-model declaration tier (§3.3). |
| **Q2 — degeneracy detection w/o false positives** | The **S1 rank ∧ S2 singular-solve-signature ∧ S3 CGE-structure** conjunction with a **pass-through default** (§2); the residual-clean sub-check separates structural singularity from an emit bug; conservative (never false-positive). |
| **Q3 — empirical confirmation** | The P6 Day-0 GAMS run (drop-`lmequil` + fix the numéraire → **MS 1 at 191.7346**, non-singular basis, §4.1). |
| **Q4 — cohort generality** | The §4.2 heuristic sweep over camcge + irscge/lrgcge/moncge/stdcge; expected **camcge sole** flagged (false-positive validation). |
| **Q5 — CES conditioning (#1070 family)** | Out of this transform's scope — prolog matches (Case-a healthy); a *related* scaling/bound-init observation, not the Walras redundancy. Left as a separate Epic-5 sub-topic. |

---

## Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_30/CAMCGE_WALRAS_TRANSFORM_DESIGN.md && echo "camcge design present"
grep -qiE "detect|rank|basis-singular|false.positive|false.flag|pass through" docs/planning/EPIC_4/SPRINT_30/CAMCGE_WALRAS_TRANSFORM_DESIGN.md && echo "detection heuristic designed"
grep -qiE "numéraire|numeraire|redundant.row|drop.*row|lmequil" docs/planning/EPIC_4/SPRINT_30/CAMCGE_WALRAS_TRANSFORM_DESIGN.md && echo "selection rule designed"
grep -qE "191.7346" docs/planning/EPIC_4/SPRINT_30/CAMCGE_WALRAS_TRANSFORM_DESIGN.md && echo "empirical target recorded"
```

## Appendix — evidence

- Model structure (§1): `data/gamslib/raw/camcge.gms` — `equil(i)` (line 393), `lmequil(lc)` (339), `cdeq(i)` (364), `obj/omega` (395), `er` Scalar (82), `p.l(i)=pd0(i)` (401), `cles(i)` (44/165). No `cpi` variable (full grep).
- Diagnosis (§1): `docs/issues/ISSUE_1330_*.md` (three Sprint-27 investigation rounds; `gdp_check ≈ -4.83e-10`; MS-4-at-iter-0; `stat_cd` uniform −0.2022; PATH basis-singularity); the Sprint-28 Day-11 Task-6 harness verdict.
- Paper argument (§3): `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` §3 (Walras redundancy + homogeneity solution-preservation) + §5 (the open questions).
- Boundary + cohort (§4.2, §5): `CGE_DEGENERACY_SCOPING.md` §2 (camcge sole inherent case; the cohort are distinct ordinary emit bugs); `docs/issues/ISSUE_classB_cge_stat_pz.md` (Class-B NOT Walras → nlp2mcp P7).
- No `src/` or golden change; design only.

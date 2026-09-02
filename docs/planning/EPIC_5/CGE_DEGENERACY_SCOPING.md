# Epic 5 Scoping — CGE Walras' Law Degeneracy (camcge #1330)

> ## ⛔ BANNED VARIANTS — READ BEFORE ANYTHING ELSE
>
> **Do not re-run any of these. Each was measured, not argued** (detail + provenance in §4a):
>
> | variant | outcome |
> |---|---|
> | **B1 drop-row** (drop `lmequil` or one `equil(i)`) | **primal-correct @ omega 299, but MS-4** — the dropped market's multiplier is **orphaned out of the stationarity**, breaking the MCP *dual*. **Silent unless you look for it.** |
> | **B2 price-pin / numéraire alone** | correct primal (191.7346), still **MS-4** |
> | **B3 single-dual-pin** | **MS-4** |
> | **B4 objective-gradient sign flip** | inert; control-refuted, `ISSUE_1236` closed |
>
> **Why every single-mechanism variant returns MS-4 — the two-nullspaces diagnosis:** the KKT Jacobian has **two** independent singularities, a **price-scaling ray** and a **row-redundancy nullspace**. **A numéraire closes the first only.**
>
> **B1 is the dangerous one because it is primal-correct.** Three-plus sprints of variants have all stayed MS-4. `camcge #1330` remains Epic-5-scoped and is **not** implemented in Sprint 39.


> **Toolchain stamp (added 2026-08-18, Sprint 38 Prep Task 8).** **Original measurements** throughout this document — including the refutations in §3 and §4a — were taken under **GAMS 51.3.0 / PATH 5.2.01**.
> **The current toolchain is GAMS 54.2.1 / PATH 5.2.01** (the corpus was re-pinned 2026-08-12); figures explicitly dated 2026-08-18 or later are from it.
> **Re-confirmed 2026-08-18 under the current toolchain:** camcge emits in **19 s**,
> is **641 single equations / 641 variables**, its embedded NLP reaches **MS-2 @ omega 191.7346**, and `mcp_model` is **MS-4 Infeasible**.
> The diagnosis and every refutation below hold on the current toolchain.
>
> **Re-confirmed again 2026-08-22 (Sprint 38 Day 10, P5), by measurement rather than quotation** — and with **no banned variant re-run**: emit compiles clean with **0 × `$141`**, **641 single equations / 641 variables**, `mcp_model` **MS-4 Infeasible** (solver status 1). **#1330 remains Epic-5-scoped.**

**Status:** FINALIZED scoping write-up (authored Sprint 29 Prep Task 7, 2026-06-27; **finalized Sprint 29 Day 11 Priority 5, 2026-06-30**). Not an Epic-5 implementation plan — the structure + evidence so the in-sprint Priority-5 task is a write-up only (no `src/`).
**Origin:** #1330 camcge, REPLAN'd to Epic 5 at the Sprint 28 Day-11 Task-6 gate (2026-06-19) — see `docs/issues/ISSUE_1330_*.md` + `docs/planning/EPIC_4/SPRINT_28/SPRINT_LOG.md` §"Day 11".

> **✅ Priority 5 CONFIRMED — camcge #1330 → Epic 5, write-up only (Sprint 29 Day 11, 2026-06-30).** The Day-11 review re-confirms the Sprint-28 Day-11 Task-6 gate finding with **no new `src/` attempt**: camcge's MCP MS-4-at-iteration-0 is an **inherent Walras-law rank-deficiency** (a linearly-dependent market-clearing row + an unfixed price numéraire → a singular KKT Jacobian), **not a localizable emit/AD bug** — the emitted KKT system is structurally correct at the NLP optimum (§1). The fix is a **CGE-domain structural preprocessing transformation** (drop-one-redundant-row + fix-one-numéraire, §3), which needs economic-model-class awareness and therefore belongs in **Epic 5**, not the general nlp2mcp emit path (§4). Sprint 29 spends **zero `src/` budget** on camcge. The distinct cohort emit bugs (#1354/#1355 phantom-offset `$141`, #1317 Pattern-C alias sum, #1331/#1251 empty-equation MCP pairing) stay in the nlp2mcp backlog — they are **not** Walras-singular (§2). This document is the Epic-5 handoff spec; the §5 open questions are the Epic-5 task's starting point.
**One-line scope:** the CGE Walras-law redundancy (a linearly-dependent market-clearing row + an unfixed price numéraire) is a **domain-specific structural preprocessing transformation**, not a general nlp2mcp emit change — it belongs in Epic 5. **Sprint 29 spends no `src/` budget on camcge** (Priority 5 = this write-up only).

---

## 1. The camcge Walras-degeneracy diagnosis (structural singularity)

camcge translates and compiles cleanly (post-#1245), and the **emitted KKT system is structurally correct** — at the NLP optimum (MODEL STATUS 2, obj 191.7346) the full CGE stationarity + market-clearing system evaluates to ≈ 0 well within solver tolerance (`gdp_check ≈ -4.83e-10`, near machine precision; `stat_cd_check ≈ 1e-7`; three Sprint-27 investigation rounds confirmed this). The MCP nonetheless returns **MODEL STATUS 4 Infeasible at iteration 0** (cold) — the signature of a **singular Jacobian**, not an emit/AD bug.

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

> ### ♻ RE-TRIAGED 2026-08-22 (Sprint 38 Day 10, P5) — four of the five backlog rows are DISCHARGED, one is STILL LIVE
>
> **All seven issues above are still OPEN on GitHub, while three of the four models now solve and match.** A match is **not** a discharge — so each row was re-checked **against its own fingerprint**, not inferred from the KPI. Measured at `643a2dab`, GAMS 54.2.1.
>
> | issue | fingerprint checked | verdict |
> |---|---|---|
> | **#1354** camcge | compiles + `nu_ieq` / `nu_actp` offsets | **DISCHARGED** — clean, **0 × `$141`**, no offsets |
> | **#1355** cesam2 | compiles + `nu_COLSUM` offsets | **DISCHARGED** — clean, no offsets; cesam2 `model_optimal` + match |
> | **#1331** twocge | `EXECERROR=8` / "empty equation" | **DISCHARGED** — fixed S38 Day 9; listing shows MCP **MS-1**, no pairing error |
> | **#1251** twocge | same fingerprint (duplicate class) | **DISCHARGED** with #1331 |
> | **#1317** twocge | the emitted `stat_tz` row | ⚠ **STILL LIVE** |
> | #1070 prolog | DB state | resolved in effect (`model_optimal` + match) |
>
> **⚠ #1317 — twocge matches with a wrong coefficient.** `stat_tm` shifts `pq`, **`stat_tz` does not**: the emitted off-diagonal term reduces to `-mu(j±1,r)/pq(j,r)` where the hand-derived value is `-mu(j±1,r)/pq(j±1,r)`. Set `i` has only **2** members, so the guarded `±1` window happens to enumerate the whole set — the *structure* is accidentally complete and only the *coefficient* is wrong. At the solution the two prices are **0.9755 / 0.9746**, so the error is **≈ 0.09 %** against a **0.2 %** match tolerance. **Masked, not absent, and the margin is thin.** twocge's Day-9 bucket move is genuine (the MCP really solved, MS-1) but the comparison is on the **objective** and would not detect a wrong **dual** — the same shape as B1's warning in §4a.
>
> **Net: the CGE cohort is now camcge #1330 (Epic 5) + twocge #1317 (nlp2mcp emit).** #1317 has **no *dedicated* `ISSUE_1317_*` file and no Phase-0 gate** — but its analysis is **not** missing: the issue body points at `docs/issues/ISSUE_1277_twocge_pattern_c_plain_alias_sum_post_day6.md` (#1317 re-validates #1277), which documents this exact plain-alias `stat_tz`/`stat_tx` defect. It is one of the ungated Tier-1 issues Sprint 38 P7 left unscheduled. **Recommended: gate it and schedule it ahead of the remaining P8 shortlist**, as the only known-live *numerical* mis-emit on a model already counted in the KPI.

**So:** the genuinely inherent-degeneracy member is **camcge #1330 alone**. #1354/#1355 (phantom-offset `$141`), #1317 (Pattern-C alias sum), and #1331/#1251 (empty-equation MCP pairing) are **compile-time emit defects** with localizable nlp2mcp fixes — they are *not* Walras-singular and do **not** need the Epic-5 transformation. #1070 prolog's CES singular Jacobian is a *related conditioning* family but is effectively resolved (prolog matches). The "CGE cohort" label conflated a structural degeneracy with a cluster of ordinary emit bugs that happen to occur in CGE models.

---

## 3. The named transformation + solution-preservation argument (Unknown 5.2)

> **⚠ SUPERSEDED IN PART — the drop-row half was REFUTED (Sprint 30 Day 11, 2026-07-08; re-confirmed S34/S36).** This section's *"drop-one-redundant-row + fix-one-numéraire"* is **primal-correct but breaks the MCP dual**: every market-clearing multiplier is a needed price/wage in the stationarity, so dropping a row **orphans its multiplier** → **omega 299, MS-4** (not the 191.7346 §3 concludes). The price-pin half is sound in isolation — pinning the price ray reaches the correct **primal** (omega 191.7346) — but stays **MS-4**, because the numéraire fixes only the *price-scaling ray*, not the *row-redundancy nullspace* (the **two-nullspaces** diagnosis, empirically re-confirmed S36 Day 11).
>
> **The current formulation is three-part and keeps every row:** (1) **keep every market-clearing row** (no orphaned dual), (2) the **consumption-weighted numéraire** `sum(i$cles(i), cles(i)·(p(i) − pd0(i))) = 0`, and (3) **redefine the redundant market's dual via Walras' law** so the reduced system is full-rank *while that dual stays available in the stationarity*. Part (3) is the hard piece and the actual Epic-5 research. Refs: `EPIC_4/SPRINT_34/CAMCGE_ROCKET_PLAN.md` §4, `EPIC_4/SPRINT_36/DAY11_P5_CONSULTATION.md` §3, `EPIC_4/SPRINT_37/CONSULTATION_INTEGRATION_PREP.md`.
>
> **Banked evidence is discouraging:** price-pin → MS-4; single-dual-pin → MS-4; drop-row → corrupt @ omega 299. Three-plus sprints of variants have all stayed MS-4. Read §3 below as the *original* reasoning, not the current plan.


**Transformation (CGE-domain structural preprocessing):**
1. **Redundant-row drop** — remove **one** market-clearing row (e.g. the labor-market `lmequil(lc)`, or one goods-market `equil(i)`). By Walras' law it is linearly dependent on the remaining market-clearing rows + household budget balance, so it carries no independent information; the dropped market clears automatically at the solution.
2. **Price-numéraire fix** — fix one price as the numéraire (e.g. a consumer price index `cpi = 1`, or a chosen good's price `p('numéraire-good') = 1`). This removes the price-level indeterminacy.

**Why it preserves the economic solution (paper argument for camcge):**
- **Redundancy (the dropped row is free).** Let the market-clearing rows be `g_i(x) = 0` (goods) and the labor row `h(x) = 0`, and let budget balance be `B(x, p) = 0`. Walras' law states `∑_i p_i·g_i + w·h ≡ B` identically in `x, p`. Hence given `B = 0` and `g_i = 0 ∀i`, the labor row `h = 0` follows (when `w ≠ 0`). Dropping `h` (or any single row by the symmetric argument) therefore loses **no** equilibrium constraint — the reduced system has the **same solution set** minus the rank-deficiency, so the Jacobian becomes nonsingular along that direction.
- **Numéraire (the price ray collapses to a point).** CGE equilibrium conditions are **homogeneous of degree 0 in prices**: scaling all prices by `λ > 0` leaves every excess-demand and zero-profit condition unchanged, so equilibria come as a **ray** `{λ·p* : λ > 0}`. The real allocation (all quantities) is identical along the ray. Fixing the numéraire selects the single representative `λ = λ₀` with no effect on quantities. Choosing `λ₀` consistent with camcge's documented NLP optimum (obj **191.7346**) reproduces that optimum exactly — the numéraire fix is a *selection*, not a *perturbation*.
- **Conclusion (HISTORICAL — the empirical answer to Q3 is NO; see the ⚠ note at the head of §3):** drop-one-row + fix-one-numéraire *was argued to* yield a **nonsingular** square MCP whose unique solution is camcge's NLP equilibrium (191.7346), solution-preserving **on paper**, with an in-Epic-5 implementation to confirm it empirically (open question Q3).
  **It was implemented and it does not hold.** Sprint 30 Day 11 measured the drop-row variant at **omega 299, MS-4** — primal-correct but the dropped market's multiplier is orphaned out of the stationarity, breaking the MCP *dual*. The price-pin half reaches the correct **primal** (191.7346) but still **MS-4**. **Q3 is therefore answered: NO for this transformation.** Use the three-part formulation in the ⚠ note instead.

**Generality:** the *argument* (Walras redundancy + price homogeneity) is generic to closed CGE models, but **which** row is redundant and **which** price is the natural numéraire is **per-model** (depends on the model's closure + the SAM). So Epic 5 needs a per-model numéraire-selection rule, not a single hard-coded row/price.

---

## 4. Scope boundary — nlp2mcp vs Epic-5 / CGE-domain (Unknown 5.3)

- **Epic 5 (CGE-domain structural transformation):** the Walras-redundancy elimination + numéraire selection. It requires **model-class awareness** (recognising the market-clearing + budget-balance structure, choosing a redundant row, picking a numéraire) — that is economic-model-domain knowledge, not a general KKT/emit transformation. nlp2mcp emits a faithful KKT system; it should **not** silently drop a user equation or fix a price, because for a *non-degenerate* model that would change the problem. So this is a **CGE-aware preprocessing layer** (Epic 5), invoked only for models detected as Walras-degenerate.
- **Stays in nlp2mcp (general emit improvements — NOT Epic 5):** the *distinct* cohort bugs — the phantom-IndexOffset `$141` enumeration (#1354/#1355), the Pattern-C alias-sum mis-emit (#1317), and the **empty-equation multiplier pairing** (#1331/#1251, fixing the multiplier of a structurally-empty `$`-conditioned equation) — are all general nlp2mcp emit fixes that help these CGE models *and* any other model with the same shape. They keep a sliver of the cohort in nlp2mcp backlog.
- **The boundary:** *faithful KKT emission of the user's model* = nlp2mcp; *recognising and resolving an inherent economic-equilibrium rank-deficiency* = Epic 5. The Sprint-28 Day-11 Task-6 gate already established that **no general emit fix exists** for camcge's singularity (the emit is correct) — confirming the boundary sits exactly here.

---

## 4a. BANNED variants — consolidated (added 2026-08-18, Sprint 38 Prep Task 8)

**Do not attempt any of these. Each was measured, not argued.**

| # | variant | outcome | first refuted | re-confirmed |
|---|---|---|---|---|
| **B1** | Drop a redundant market-clearing row (`lmequil` or one `equil(i)`) | **corrupt @ omega 299, MS-4** — primal-correct, but the dropped market's multiplier is **orphaned out of the stationarity**, breaking the MCP *dual* | S30 Day 11 | S34, S36, S37 |
| **B2** | Price-pin / numéraire **alone** | correct **primal** (omega 191.7346) but still **MS-4** — a numéraire closes the *price-scaling ray*, not the *row-redundancy nullspace* | S32 | S36 Day 11, S37 Day 10 |
| **B3** | Single-dual-pin | **MS-4** | S32 | S36 |
| **B4** | Objective-gradient sign flip (`ν_objective` reduction) | inert on the CGE cluster; control-refuted | S31 Day 10 | `ISSUE_1236` closed |

**B1 deserves its own warning: it is *primal-correct*.** A reader checking only the primal will conclude it works; the failure is in the dual and is silent unless the orphaned multiplier is looked for.

**The reusable insight (why every single-mechanism variant returns MS-4) — the two-nullspaces diagnosis:** the KKT Jacobian has **two** independent sources of singularity, a **price-scaling ray** and a **row-redundancy nullspace**. **A numéraire closes the first only.** Any fix addressing one and not the other leaves the system singular.

---

## 5. Open questions for the Epic-5 task

1. ~~**Numéraire-selection rule.** Is there a robust automatic rule (e.g. fix the price of the SAM's largest sector, or a CPI aggregate), or must each CGE model declare its numéraire?~~
   **🟡 PROPOSED — per-model declaration (Sprint 39 Prep Task 10; §6).** An automatic rule is **not warranted**, and on the measured cohort not **achievable** either. A general rule would serve a population of **one**.
2. ~~**Degeneracy detection.** How does the preprocessing layer *detect* Walras-degeneracy … without falsely flagging a well-posed model?~~
   **🟡 PROPOSED — no pre-solve structural detector, so Epic 5 is a RETRY LOOP, not preprocessing (Task 10; §7).** The best structural detector scores **0 true positives and 1 false positive** on the corpus: it **excludes camcge** — the sole true positive — and flags `agreste`, which is not a Walras case.
3. ~~**Empirical confirmation.** Does drop-`lmequil` + fix-`cpi=1` actually drive camcge to MODEL STATUS 1 at 191.7346 (the §3 paper argument verified in GAMS)?~~
   **✅ ANSWERED — NO (Sprint 30 Day 11; re-confirmed S34/S36/S37).** The drop-row variant measures **omega 299, MS-4** — primal-correct, but the dropped market's multiplier is orphaned out of the stationarity, breaking the MCP *dual*. The price-pin half alone reaches the correct **primal** (191.7346) yet stays **MS-4**. Do **not** re-run this experiment. **The live open question is instead:** does the *three-part* formulation (keep every row + consumption-weighted numéraire + **Walras-law dual redefinition**) reach MS-1? Banked evidence is discouraging — price-pin MS-4, single-dual-pin MS-4, drop-row corrupt @ 299; **3+ sprints of variants have all stayed MS-4**. The control is cheap to re-run (Sprint-37 Day-10 measurement, **GAMS 54.2.1 / PATH 5.2.01**: **19 s** emit, 641 single equations / 641 variables, demo-reachable; embedded NLP MS-2 @ omega 191.7346, `mcp_model` MS-4).
4. **Cohort generality.** Does the same transformation (with a per-model row/numéraire) recover any *other* genuinely Walras-degenerate model, or is camcge the only one in the corpus? (The §2 survey suggests camcge is currently the sole inherent case.)
5. **CES conditioning (#1070 family).** Is the CES singular-Jacobian-near-bounds conditioning a separate Epic-5 sub-topic (scaling / bound-init), or fully resolved now that prolog matches?

## Verification

```bash
test -f docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md && echo present
grep -Ei 'Walras|numéraire|redundant|equil|lmequil' docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md | head
grep -Ei '#1330|#1354|#1355|#1317|#1331|#1251|#1070' docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md | head
```

---

## 6. Numéraire-selection rule — PROPOSED (Unknown 9.1)

**Sprint 39 Prep Task 10** · **Measured at:** `04f50d6c` · **2026-09-02** · **Analysis over the corpus IR only; no camcge experiment was run.**

### 6.1 The CGE-cohort survey

Structural scan of all 219 corpus models (`artifacts/cge_scan.py`); every count below is a **lower bound**.

**⚠ The parsed count is load-dependent, so it is quoted as a range.** Three models — `iswnm`, `mexls`, `turkey` — sit at the **120 s per-model timeout** and flip depending on machine load: three runs gave **176 / 178 / 179** parsed. The figures below are from the **clean run (179 parsed, 40 not)**, taken with nothing else running. A count taken while `make test` was running would report `turkey` unparsed and drop it from the table. The **numéraire column is the script's `fixed_prices` field**, which probes all four places a GAMS `.fx` can land (`fx`, `fx_map`, `fx_expr`, `fx_expr_map`) — see §7.2 and `artifacts/README.md` for why the distinction is load-bearing.

Models with ≥ 2 price-like variables **and** a market-clearing equation — the CGE shape (**10**):

| model | price vars | clearing eqs | balance eqs | SAM-like params | numéraire declared? |
|---|---|---|---|---|---|
| **camcge** | 9 | 4 | 4 | `io(i,j)`, `zz(*,i)` | **⚠ `pwm` only — a *world* price** |
| **korcge** | 9 | 3 | 4 | `io(i,j)`, `zz(*,i)` | ✅ **`pindex`** — a genuine price index |
| orani | 6 | 5 | 0 | — | `phi`, `pm` |
| tfordy | 6 | 2 | 0 | — | none |
| tforss | 6 | 2 | 0 | — | none |
| paperco | 4 | 4 | 0 | — | none |
| agreste | 2 | 2 | 1 | — | none |
| turkey | 2 | 2 | 0 | — | none |
| fawley | 2 | 4 | 0 | — | none |
| nebrazil | 2 | 2 | 0 | — | none |

**Only two models have the full CGE signature** (many prices + clearing + balance + a SAM): **camcge and korcge**. They are near-twins structurally — same SAM parameter names, 9 price variables each — and they differ in exactly the thing that matters.

### 6.2 ⚠ The finding: camcge fixes a price, and it is the wrong one

**camcge does declare a fixed price — `pwm.fx(i) = pwm0(i)`** — but `pwm` is the **world market price of imports**: exogenous data, not a numéraire for the domestic price system. Its nine domestic prices (`p`, `pd`, `pe`, `pk`, `pm`, `pva`, `px`) are all endogenous and **none is pinned**.

**korcge fixes `pindex`** — an actual price-index numéraire — and korcge **solves and matches** (`model_optimal`, match).

**The IR cannot tell these apart.** Both read as *"a variable whose name starts with `p` carries an `.fx`"*. Distinguishing them needs the economic meaning of the symbol, which no structural signal in the IR carries.

### 6.3 The proposed rule

**Per-model declaration. An automatic rule is neither warranted nor, on this cohort, achievable.**

Three reasons, in order of decisiveness:

1. **Population of one (Q5).** The §2 survey establishes camcge as the **sole inherent** Walras case, and §6.1 confirms only one other model even has the shape — and it already declares its own numéraire. **A general rule would serve exactly one model.** Building an inference engine for a population of one is how a scoping document becomes a project.
2. **The obvious automatic rules fail on the only case (Q1/Q2).** *"Fix the largest sector by SAM value"* needs a SAM the IR can identify: camcge's SAM-like parameters are `io(i,j)` and `zz(*,i)`, and nothing distinguishes an input–output matrix from any other 2-D parameter by structure. *"Fix any already-fixed price"* selects `pwm` — the **world** price — which is precisely the pin that does **not** close the price-scaling ray.
3. **A CPI aggregate needs a model-side symbol (Q3).** camcge has no CPI variable. Introducing one is a change to the *model*, not to the emitted MCP, and Epic 5's transformation is supposed to be applied by the translator.

**Q4 — correct or merely consistent?** Consistent is enough **for the ray**: any valid numéraire closes the price-scaling nullspace, which is why B2 reaches the correct primal (191.7346). It is **not** enough for the problem, because the **row-redundancy nullspace remains** — that is the two-nullspaces diagnosis, and it is why B2 is still MS-4. **A numéraire rule is a necessary component, never a sufficient one.**

**Failure modes of the proposed declaration, to be handled when Epic 5 starts:**

| failure mode | handling |
|---|---|
| declared symbol is not a variable, or not in the model | reject at parse; do not emit |
| declared symbol is already `.fx`-fixed (the camcge `pwm` trap) | **reject, and say why** — fixing an exogenous price does not close the ray |
| declared symbol is indexed and the declaration names no element | require an element; a set-wide pin over-determines the system |
| no declaration on a model the detector flags | **do nothing** — see §7; there is no safe automatic fallback |

## 7. Degeneracy detection — PROPOSED (Unknown 9.2)

### 7.1 The candidate detectors, applied to the corpus

Each applied as **analysis over the IR** of the **179** parsed models of the clean run (see §6.1 on why that count is a range). Expected true positives: **1** (camcge).

| detector | flags | of which convex candidates | camcge flagged? |
|---|---|---|---|
| **D1** ≥ 2 price-like variables | 34 | 31 | ✅ |
| **D2** D1 + a market-clearing equation | 10 | 9 | ✅ |
| **D3** D2 + a balance/income equation | **3** | 3 | ✅ |
| **D4** D3 + **no price variable is `.fx`-fixed** | **1** | 1 | ❌ **NO** |

D3's three flags are `agreste`, `camcge`, `korcge`. Narrowing from 34 to 3 is real progress — and then the last conjunct, the one that encodes *"has no numéraire"*, **inverts the answer**.

### 7.2 ⚠ D4 scores 0 true positives and 1 false positive

| | |
|---|---|
| **camcge** — the sole true positive | **excluded**, because it fixes `pwm` (a world price) |
| **korcge** — well-posed, solves and matches | excluded, because it fixes `pindex` (a real numéraire) — **right answer, wrong reason** |
| **agreste** — not a Walras case | **flagged** |

**Precision 0. Recall 0.** The rule is not discriminating on degeneracy at all; it is discriminating on *"does this model happen to fix any symbol whose name starts with `p`"* — a question whose answer is identical for the model that needs the transformation and the model that does not.

**⚠ And one conjunct was silently inert while being measured.** The first pass of `cge_scan.py` probed `fx` and `fx_map` only. GAMS `pwm.fx(i) = pwm0(i)` lands in **`fx_expr_map`**, so camcge read as having *no* fixed price and D4 appeared to flag it correctly. The corrected four-field probe reversed the result. **The detector's most important conjunct was doing nothing, and the run looked healthy** — recorded because a Sprint-39 detector will face the same trap. `cge_scan.py` now emits **both** probes (`fixed_prices`, correct; `fixed_prices_fx_only`, incomplete), so the failure is visible in the script's own output and not only here. **And it was not a camcge quirk** — the two disagree on **5** models: `camcge`, `glider`, `korcge`, `otpop`, `robot`. On camcge they read `["pwm"]` vs `[]`; on `robot`, `["phi","phi_dot"]` vs `["phi_dot"]` — the incomplete probe found one of two fixes and looked like it had worked.

**⚠ An earlier draft said 6 and named `orani`. That was wrong, and the way it was wrong is the point.** The legacy field originally tested `if getattr(vd, "fx", None)`, which drops a **scalar fix to `0.0`** — so `orani`'s `phi` disagreed for the *truthiness* bug, not the `fx_expr_map` one, and the field was disagreeing for two unrelated reasons at once. Corrected to `vd.fx is not None or vd.fx_map`, so the two probes now differ in **exactly one dimension — the field set** — and every disagreement is attributable to it. `orani` drops out; the figure is **5**. (Found in review of this PR.)

### 7.3 The proposed design: a retry loop, not preprocessing

**There is no pre-solve structural signal that separates camcge from korcge**, and that is not a tuning problem — the distinguishing fact is the *economic role* of a fixed symbol, which the IR does not carry.

This answers the architectural question 9.2 raised: **detection works only post-solve, so Epic 5 is a retry loop.**

```
solve the MCP cold
  └── MS-4 (infeasible / singular basis) ?
        └── AND the model is D3-shaped (many prices + clearing + balance) ?
              └── AND a numéraire is DECLARED for it (§6.3) ?
                    └── apply the transformation and re-solve
                    └── otherwise: report MS-4 unchanged
```

**Why this is safe where a preprocessor is not.** Every gate is a *narrowing* on a model that has **already failed**: D3's 3 flags are irrelevant to `korcge`, which never reaches the retry because it solves. **A false positive costs one re-solve on an already-failed model; a false positive in a preprocessor would transform a healthy one.** That asymmetry is the whole argument.

**The shape is not new** — the presolve-retry path (`run_full_test.py:936`) is exactly this: solve, detect failure, re-solve differently. Epic 5 would add a second trigger, not a new architecture. ⚠ And it inherits that path's hazard, which Sprint 38 Day 9 measured on `weapons`: **a retry whose MCP aborts can read back the embedded NLP's answer and match itself.** Any Epic-5 retry must assert the MCP produced its **own** `MODEL STATUS` — `scripts/sprint_audit/check_mcp_solve_attribution.py`.

### 7.4 What would need measuring, and why it is out of scope here

The prompt asks that a needed-but-forbidden measurement be recorded rather than taken. One qualifies:

**A rank check on the assembled market-clearing block** — the one detector that could work pre-solve, because redundancy is what actually defines the degeneracy. It is **not** an IR-level question: it needs the *numeric* Jacobian at a point, which means building the KKT system and evaluating it. That is a solve-adjacent measurement on camcge, and §4a's banned list exists precisely to stop "just one more camcge measurement".

**Recorded, not run.** If Epic 5 wants it, it is a first-day task with its own Phase-0 gate — and the honest prior from §7.2 is discouraging: a rank check would separate camcge from korcge only if the redundancy is visible *before* the numéraire question is settled, and the two-nullspaces diagnosis says the two singularities are independent.

---

**§6–§7 Document Status:** ✅ Complete — Sprint 39 Prep Task 10. Q1 and Q2 are **proposed**, not open. Q3/Q4 answers unchanged.
**Last Updated:** 2026-09-02

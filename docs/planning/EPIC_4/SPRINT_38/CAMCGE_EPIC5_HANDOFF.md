# Sprint 38 Prep Task 8 — camcge Epic-5 Handoff + turkey Testbed Determination (P5)

**Date:** 2026-08-18 · **Branch:** `planning/sprint38-task8` · **Measured at:** `860b0e7b` · **Scope:** docs only. No `src/`, DB or golden change.

**Verdict: 🔶 THE HANDOFF IS ALREADY WRITTEN — THREE GAPS, NOT A DOCUMENT.** The task assumed the camcge refutation record needed assembling. **It does not**: `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` already carries the diagnosis, every refuted variant, the two-nullspaces analysis, the three-part formulation, and an explicit *do-not-re-run* instruction. Writing a second document would have duplicated ~90 % of it and created a second thing to keep in sync.

**turkey is not a special case: ten models share the identical licence block, and §4 treats them as one cohort.**

---

## 1. The audit (5.2) — what the Epic-5 doc already has

Checked `CGE_DEGENERACY_SCOPING.md` against the S32–S37 refutation history:

| item the prompt asked to assemble | already present? |
|---|---|
| price-pin → MS-4 | ✅ ×4 |
| single-dual-pin → MS-4 | ✅ ×2 |
| drop-row → corrupt @ omega 299 | ✅ ×4 |
| **two-nullspaces** diagnosis | ✅ (§3 ⚠ note) |
| three-part formulation (keep rows + numéraire + dual redefinition) | ✅ ×3 |
| NLP optimum 191.7346 | ✅ ×7 |
| 641 rows / demo-reachable | ✅ |
| per-model numéraire generality | ✅ ×2 |
| **"Do not re-run this experiment"** | ✅ (§5 Q3) |

**§3 carries a `⚠ SUPERSEDED IN PART` banner** recording that the drop-row half was refuted in Sprint 30 Day 11 and re-confirmed in S34/S36, and **§5 Q3 is marked ✅ ANSWERED — NO** with the live question restated as the three-part formulation. The document is *current*, not stale.

### The three real gaps

| # | gap | fix |
|---|---|---|
| 1 | Emit time recorded as **18 s**; the S37 Day-10 control measured **19 s** | corrected |
| 2 | **Zero mentions of GAMS 54.2.1** — every figure predates the re-pin and carries no toolchain attribution | stamp added |
| 3 | No **consolidated BANNED list** — the bans are correct but spread through prose, so a reader skimming for "what must I not do" has to reconstruct them | §2 below, mirrored into the scoping doc |

Gap 2 is the same defect Task 7 found in the consultation bundle: **measurements without a toolchain stamp**, in a document written before the corpus was re-pinned. It is worth noting that this has now appeared twice in one prep cycle.

## 2. The BANNED list — consolidated, with attribution

**Do not attempt any of these. Each was measured, not argued.**

| # | variant | outcome | first refuted | re-confirmed |
|---|---|---|---|---|
| **B1** | **Drop a redundant market-clearing row** (`lmequil` or one `equil(i)`) | **corrupt @ omega 299, MS-4** — primal-correct, but the dropped market's multiplier is **orphaned out of the stationarity**, breaking the MCP *dual* | S30 Day 11 | S34, S36, S37 |
| **B2** | **Price-pin / numéraire alone** | correct **primal** (omega 191.7346) but still **MS-4** — a numéraire fixes the *price-scaling ray*, not the *row-redundancy nullspace* | S32 | S36 Day 11, S37 Day 10 |
| **B3** | **Single-dual-pin** | **MS-4** | S32 | S36 |
| **B4** | **The objective-gradient sign flip** (`ν_objective` reduction) | inert on the CGE cluster; control-refuted | S31 Day 10 | ISSUE_1236 closed |

**B1 is the dangerous one and deserves its own warning: it is *primal-correct*.** A reader who checks only the primal will conclude it works. The failure is in the dual, and it is silent unless you look for the orphaned multiplier.

**Why B2 fails is the reusable insight — the two-nullspaces diagnosis:**

> The KKT Jacobian has **two** independent sources of singularity: a **price-scaling ray** (CGE conditions are homogeneous of degree 0 in prices) and a **row-redundancy nullspace** (Walras' law makes one market-clearing row linearly dependent given budget balance). **A numéraire closes the first only.** Any fix addressing one and not the other leaves the system singular — which is why every single-mechanism variant has returned MS-4.

## 3. camcge status, stamped (5.3)

**Re-confirmed under GAMS 54.2.1 / PATH 5.2.01** (S37 Day-10 control, all figures reproducing the prediction):

| quantity | measured |
|---|---|
| emit time | **19 s** |
| model size | **641 single equations / 641 variables** — demo-reachable |
| embedded NLP | **MS-2 Locally Optimal @ omega 191.7346** |
| `mcp_model` | **MS-4 Infeasible** |
| current DB row | `model_infeasible` |

**The MCP is MS-4 against a *correct* NLP optimum.** That is structural rank-deficiency, **not an emit defect** — the distinction that keeps camcge in Epic 5 rather than in the emit backlog.

**The per-model-numéraire fallback remains the right recommendation.** Nothing since Sprint 32 has changed the two-nullspaces analysis, and the S37 control reproduced every predicted figure under the new toolchain. What it buys: a *selection* on the price ray rather than a perturbation, reproducing the documented optimum exactly. What it does **not** buy: closure of the row-redundancy nullspace — that is the three-part formulation's part (3), and it is the actual Epic-5 research.

## 4. The licence-gated cohort (5.1) — **10 models, treated uniformly**

**Corrected scope (owner, 2026-08-18): turkey is not a special case.** An earlier draft of this task singled turkey out for reclassification. That was wrong — **ten models carry the identical block**, and they should be treated as one cohort rather than one model plus nine unexamined others.

### 4.1 The cohort

| property | value |
|---|---|
| **Models (10)** | `egypt` · `ferts` · `glider` · `robot` · `shale` · `sroute` · `srpchase` · `tabora` · `tfordy` · `turkey` |
| Share of the corpus | **10 of 142 convex candidates (7 %)** |
| Outcome | all `path_solve_license`, all `comparison_status: not_tested` |
| **Rejected at** | **generation** — `solver_version: None` on all ten; **PATH is never invoked** |
| Toolchain | all recorded under GAMS **54.2.1** |
| **Emit status** | **all ten have committed goldens** — translate succeeded; only the *solve* is blocked |

The shared signature is exact: same outcome, same null solver version, same cause. **This is one licence problem, not ten model problems.**

### 4.2 What the cohort is worth

**Ceiling: Solve 108 → 118** if all ten solve and match. Realistically fewer will match, but **the emit for all ten is already verified** — goldens are committed and swept by the leak gate — so nothing stands between them and a solve attempt except licence capacity.

**One licence unlocks all ten as a batch.** That is the operative fact for the pursuit: the ask is worth ~10 models, not 1. A single `--only-solve` pass over the cohort is all that's needed once capacity exists.

### 4.3 The treatment — uniform, and neither inflated nor written off

**Classification: `licence-gated`.** For all ten, identically:

1. **Not counted in sprint KPI projections.** No sprint may claim any of these as reachable upside. This is the phantom-upside failure mode that turkey alone exhibited across S35–S37.
2. **Not written off as blocked-indefinitely.** A licence is being **actively pursued** — the owner is raising it with Dirkse and Ferris. "Blocked" would misstate that.
3. **Tracked as a named, quantified cohort** with its ceiling stated (+10 Solve), so the value of the licence is visible rather than implicit.
4. **Re-tested as a batch** the moment capacity exists — one `--only-solve` over the ten, not ten separate efforts.

**Wording, applicable verbatim wherever these models are projected:**

> **Licence-gated cohort (10 models):** `egypt`, `ferts`, `glider`, `robot`, `shale`, `sroute`, `srpchase`, `tabora`, `tfordy`, `turkey`. All emit correctly (goldens committed) and all are rejected at **generation** by the GAMS demo 1000-row nonlinear limit — `solver_version: None`, PATH never invoked. **Excluded from KPI projections** until a larger licence exists; **not** written off, as one is being pursued. **Ceiling +10 Solve (108 → 118).** Re-test as a single batch on capacity.

### 4.4 A convergence worth using

**The licence ask and the P3 consultation go to the same people.** Task 7 resolved the consultation channel as email to Ferris (`ferris@cs.wisc.edu`) and Dirkse (`steve@gams.com` / `sdirkse@gams.com`), and the owner is meeting them about licence capacity. **The two conversations can be one**, and the cohort figure — *"10 models, 7 % of our corpus, blocked only by the 1000-row demo limit"* — is a concrete, quantified ask rather than a general request.

**What a reduced instance would buy: nothing for the KPI.** A smaller instance of any cohort member could raise confidence that its emit solves, but the KPI requires **the model itself** to solve and match. Worth stating because it is the tempting engineering workaround, and it does not deliver.

## 5. What P5 delivers, stated honestly

With camcge Epic-5-scoped and turkey blocked, **P5's Sprint-38 deliverable is documentation, not bucket movement**:

- the three scoping-doc corrections (§1), so Epic 5 inherits stamped, consolidated refutations
- the BANNED list (§2), with B1 flagged as primal-correct-but-dual-breaking
- the **licence-gated cohort** treatment (§4) — 10 models, uniform classification, ceiling +10 Solve

**0 bucket for Sprint 38**, and the plan already says so. The value is that Epic 5 starts from four refuted variants rather than rediscovering them, and that **ten** licence-gated models stop inflating projections while remaining visible as a quantified, actively-pursued opportunity.

---

**Document Status:** ✅ Complete — Sprint 38 Prep Task 8. **5.2 ❌ WRONG** (the handoff was already written; three narrow gaps, not a document) · **5.3 ✅ VERIFIED** (per-model numéraire still correct, now stamped under v54) · **5.1 🔶 reframed — a 10-model licence-gated cohort**, excluded from projections but actively pursued; ceiling +10 Solve.
**Last Updated:** 2026-08-18 · **Owner:** Sprint 38 execution team · **Licence pursuit:** active (owner, with Dirkse/Ferris)

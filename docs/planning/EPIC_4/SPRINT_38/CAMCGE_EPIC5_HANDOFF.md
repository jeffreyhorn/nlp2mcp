# Sprint 38 Prep Task 8 — camcge Epic-5 Handoff + turkey Testbed Determination (P5)

**Date:** 2026-08-18 · **Branch:** `planning/sprint38-task8` · **Measured at:** `860b0e7b` · **Scope:** docs only. No `src/`, DB or golden change.

**Verdict: 🔶 THE HANDOFF IS ALREADY WRITTEN — THREE GAPS, NOT A DOCUMENT.** The task assumed the camcge refutation record needed assembling. **It does not**: `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` already carries the diagnosis, every refuted variant, the two-nullspaces analysis, the three-part formulation, and an explicit *do-not-re-run* instruction. Writing a second document would have duplicated ~90 % of it and created a second thing to keep in sync.

**turkey is a different matter: it is a procurement decision, and the default is to reclassify it as blocked.**

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

## 4. turkey (5.1) — a procurement decision, defaulting to BLOCKED

### 4.1 What is established

| fact | evidence |
|---|---|
| Local licence is **GAMS_Demo** | `gamslice.txt` → `GAMS_Demo, for EULA and demo limitations…`, `O_DEMO` |
| turkey's MCP is **3,866 rows** vs the **1000-row** demo nonlinear limit | S35–S37 record |
| turkey **never reaches PATH** | DB: `outcome_category = path_solve_license`, **`solver_version: None`** — rejected at *generation*, so no solver was invoked |
| The compile-recovery **works** | the S35 `$161` fix moved it `path_syntax_error → path_solve_license`; S37 Day 9 corrected the stale row and Day 10 confirmed it stable |
| **No licensed >1000-row environment exists** in local or CI infrastructure | S36 prep (Task 7), re-confirmed S37 prep |

**turkey is blocked on one thing only: licence capacity.** The emit is correct enough to reach the size check, and nothing else stands between it and a solve.

### 4.2 The options, and what each would actually buy

| option | buys the +1? | note |
|---|---|---|
| Commercial GAMS licence | ✅ yes | cost/timeline unknown to this session — **requires a human** |
| Academic licence | ✅ yes, if eligible | eligibility is an institutional question |
| Time-limited evaluation licence | ✅ yes, if it covers >1000 nonlinear rows | would need to cover a single re-solve; unverified |
| Hosted/cloud GAMS runner | ✅ yes | introduces CI/secret-management scope |
| **Reduced turkey instance** | ❌ **no** | a smaller instance under 1000 rows would raise *confidence* that the emit solves, but the KPI requires **turkey itself** to solve and match. **It cannot earn the +1.** |

**The last row is the one worth stating explicitly**, because a reduced instance is the tempting engineering workaround and it does not deliver the thing being carried.

### 4.3 Recommendation: reclassify as BLOCKED

turkey's +1 has been carried as *"pending a testbed"* since **Sprint 35** and was **already refuted once in Sprint 37 prep** ("no licensed >1000-row testbed is procurable"). Carrying it a fourth time on the same unexamined assumption is the phantom-upside failure mode.

**Unless a licence is actually being procured, reclassify. Wording, applicable verbatim:**

> **turkey — RECLASSIFIED BLOCKED (Sprint 38, 2026-08-__).** turkey's +1 Solve/+1 Match is **not "pending a testbed"** but **blocked on licence capacity**: its MCP is 3,866 rows against the GAMS demo 1000-row nonlinear limit, and the model is rejected at *generation* (`solver_version: None` — PATH is never invoked). The emit is correct; the `$161` compile-recovery landed in Sprint 35. **Removed from sprint projections** until a licensed >1000-row environment exists. A reduced instance cannot substitute — the KPI requires turkey itself to solve and match.

**If a licence *is* being procured**, the only additional need is a date, and turkey returns to the projection with that date attached.

## 5. What P5 delivers, stated honestly

With camcge Epic-5-scoped and turkey blocked, **P5's Sprint-38 deliverable is documentation, not bucket movement**:

- the three scoping-doc corrections (§1), so Epic 5 inherits stamped, consolidated refutations
- the BANNED list (§2), with B1 flagged as primal-correct-but-dual-breaking
- the turkey determination (§4) and its reclassification wording

**0 bucket for Sprint 38**, and the plan already says so. The value is that Epic 5 starts from four refuted variants rather than rediscovering them, and that turkey stops inflating projections.

---

**Document Status:** ✅ Complete — Sprint 38 Prep Task 8. **5.2 ❌ WRONG** (the handoff was already written; three narrow gaps, not a document) · **5.3 ✅ VERIFIED** (per-model numéraire still correct, now stamped under v54) · **5.1 🔍 open — procurement, requires a human**, defaulting to BLOCKED.
**Last Updated:** 2026-08-18 · **Owner:** Sprint 38 execution team · **turkey licence decision:** requires a human

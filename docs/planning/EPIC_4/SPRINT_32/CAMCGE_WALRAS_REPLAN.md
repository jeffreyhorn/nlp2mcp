# Sprint 32 Day 5 — camcge P3 step 2 REPLAN: dual-consistent Walras → Epic 5

**Date:** 2026-07-14
**Day:** 5 (Priority 3 — camcge dual-consistent Walras, #1330 → Epic 5)
**Outcome:** 🔴 **REPLAN → Epic 5.** Step 1 (the scalar-`fx` general emit fix) **landed** on main (PR #1553); step 2 (the dual-consistent Walras numéraire) does **not** reach MS-1 → Epic-5 deferral. camcge stays `model_infeasible`.
**Discipline:** the PR24/PR27 `/tmp` control ran **before** any Walras `src/` change and refuted the re-scoped hypothesis. **No step-2 `src/` change.**

---

## 1. The re-scoped hypothesis under test

The Sprint-32 design (`CAMCGE_STAT_MPS_WALRAS_DESIGN.md` §3) re-scoped the S30/S31 REPLAN: those numéraire/Walras variants stayed MS-4, **but** they were tested on an inconsistent warm point (before the `stat_mps` fix). The Day-5 hypothesis: **`stat_mps`-fixed-first (step 1, now on main) + the consumption-weighted numéraire → MS-1 at omega 191.7346.**

## 2. The `/tmp` control (step 1 landed + numéraire)

Built on the current `camcge_mcp_presolve.gms` (step 1 present: `nu_mps_fx.l = mps.m` + the scalar unfix), added the design's numéraire:

- `numeraire.. sum(i$(cles(i)), cles(i) * (p(i) − pd0(i))) =E= 0;` complemented by a free `nu_numeraire`;
- the `+ (cles(i)·nu_numeraire)$(cles(i))` cross-term in `stat_p(i)` (the numéraire's gradient w.r.t. `p(i)`);
- **every** market-clearing row kept (no orphaned dual).

**Result:** GAMS 53, 0 compile errors —

| | value |
|---|---|
| `omega` (objective) | **191.7346** — the **correct allocation** (= the NLP reference) ✅ |
| MCP MODEL STATUS | **4 — Infeasible** ❌ (not MS-1) |
| Residual INFES rows | the **accounting identities**: `gdp` 131.96, `depreq` 131.96, `hhsaveq` 97.26, `gruse` 43.97 (equality-definitional closure rows) |

So the numéraire pins the price ray and delivers the **right primal** (omega 191.7346), but PATH still reports **MS-4** with the residual singularity on the accounting-identity closure — the **primal-correct / basis-singular** signature. **The re-scoped hypothesis is refuted:** fixing `stat_mps` first does **not** let the numéraire reach MS-1.

## 3. Diagnosis — the Walras rank-deficiency is deeper than a numéraire

The numéraire removes the price-scaling nullspace (homogeneity degree 0), but the **residual Walras rank-deficiency remains** (the market-clearing + accounting identities carry a dependency the numéraire selection doesn't resolve). This is exactly the design's REPLAN trigger (§3): *"if the combined prototype still stays MS-4 (the Walras rank-deficiency is genuinely deeper than a numéraire selection), camcge lands only step 1 and the numéraire falls to the per-model-declaration Epic-5 fallback."* Consistent with 3 sprints of prep (ISSUE_1330: price-pin MS-4, single-dual-pin MS-4, drop-row corrupt @ 299) — now confirmed to hold **even with step 1**. The **dual-consistent redefinition** (redefine the redundant market's dual via Walras' law so the reduced system is full-rank) is, per the design, *"genuinely deeper Epic-5 MCP research, not a same-day hand-transform"* — an open item, not a Day-5 landing.

## 4. Disposition

- **REPLAN step 2 → Epic 5** (the per-model-numéraire / dual-consistent-Walras redefinition). **No step-2 `src/` change** (the `/tmp` control refuted the fix pre-src — PR24/PR27, the 7th consecutive control-first REPLAN across S30–S32).
- **Step 1 LANDED** (PR #1553, on main): the scalar-`fx` marginal warm-start transfer is a **general nlp2mcp emit-correctness fix** — camcge `stat_mps` → Case-a; any scalar-`.fx`-in-stationarity model benefits. This is the firm part Task 9 predicted lands regardless.
- **camcge stays `model_infeasible`** in Sprint 32; its +1 Solve defers to Epic 5.
- **Both firm +Solve movers have now REPLAN'd** (mine 5th-coupling Day 1; camcge Walras Day 5) — exactly the Task-9 honest projection (Solve ≥ 109 needs BOTH; each REPLAN drops one). **Solve stays 107** unless a **P6** candidate (cpack offset-alias / fawley second-index Case-b) converts; **genuine floor ≥ 75 now rests entirely on a P6 emit change** (camcge step 1 does not cold-match — camcge doesn't solve). Freed step-2 budget (~6–12 h) + the Days 2–3 mine budget → **P6 + P7** (Task 9 reallocation order).
- **The de-risked Epic-5 hand-off:** the working numéraire recipe (omega 191.7346), the exact residual-singularity characterization (INFES on `gdp`/`depreq`/`hhsaveq`/`gruse` at the correct primal), and the confirmation that step-1-first does not change the MS-4 outcome.

## 5. Checkpoint 1 (Day 5)

`run_full_test.py --resolve-changed --since-commit 4cbf8bff` → **GO** (no emit golden changed since the anchor — step 1 changed only `src/`, and camcge has no committed presolve golden). Golden-staleness clean (PR #1553). No changed-golden model moved backward. **PR25 tally unchanged:** genuine floor 74 / methodology 21 (camcge step 1 does not cold-match; no floor movement).

## 6. Evidence

GAMS 53 on the hand-edited `/tmp` `camcge_num2.gms` (0 compile errors): `omega = 191.7346`, MCP MS-4, INFES on `gdp`/`depreq`/`hhsaveq`/`gruse`. The base step-1 camcge (`camcge_base_abs.gms`) is MS-4. The embedded NLP `$include camcge.gms` solves MS-2 (Locally Optimal) in every run. Anchor `4cbf8bff`; step 1 on main at `4d15c7f4` (PR #1553). See `CAMCGE_STAT_MPS_WALRAS_DESIGN.md` §3 + `docs/issues/ISSUE_1330_*.md` §"Phase 0: Acceptance Gate".

---

**Document Created:** 2026-07-14
**Owner:** Sprint 32 execution (KKT/CGE specialist)

# Sprint 34 Phase-0 Acceptance Gates (PR20 + PR24 + PR27)

**Prep Task:** 8 (Critical) · **Date:** 2026-07-19 · **Owner:** Sprint 34 prep (KKT/emit specialist)
**Day-0 code anchor:** `750803b2` (S33 close) · no `src/` drift since (Task 2 `BASELINE_METRICS.md`)
**Scope:** docs-only — consolidates the per-track PROCEED/REPLAN gates for the five Sprint-34 priorities (P1 mine dual subsystem, P2 sarf symbolic emit, P3 fawley second-index + forcing, P4 max-convention bound-transfer [NEW], P5 camcge Epic-5 + rocket Sprint-35). The authoritative per-track detail lives in each Task-3–7 design doc (`MINE_DUAL_SUBSYSTEM_DESIGN.md`, `SARF_EMIT_MODE_DESIGN.md`, `FAWLEY_CORRECTION_FORCING_DESIGN.md`, `BOUND_TRANSFER_SIGN_DESIGN.md`, `CAMCGE_ROCKET_PLAN.md`, all under `docs/planning/EPIC_4/SPRINT_34/`); this document is the single-page index + the control-experiment discipline for the sprint.

---

## 0. The standing discipline (why these gates exist)

- **PR24 — the banked fix surface is a Day-0-re-confirm hypothesis, not fact.** Sprint 33 REPLAN'd/deferred every deep track after a control refuted the banked premise: mine's H1 keying was proven **value-invariant**, fawley reached **H-b**, sarf was Option-B-deferred. Each gate below frames its fix surface as a hypothesis re-confirmed at Day 0 in the Task-3–7 designs.
- **PR27 — the `/tmp` control runs BEFORE any high-blast-radius `src/` change.** Every emit gate's PROCEED precondition is a `/tmp` control that must pass first.
- **Assert `modelstat` before reading an objective** (the Sprint-31 measurement-error lesson): every warm/cold solve step asserts `mcp_model.modelstat` before any objective read. **`x.up=inf` is a structurally invalid experiment (BANNED)** for mine. **The objective-gradient sign flip is BANNED** for the Case-c family (control-refuted 4× S30–S31).
- **The keying-invariance reframe (P1).** Because a keying/pairing change is **value-invariant** on the warm residual (S33 Day-2), P1's gate is the **cold MCP reaching MS-1**, **not** the warm residual `N → 0` (which no keying change can move). This corrects the S33 `N→0` gate that was un-passable by construction.
- **Emit-touching CI gates.** Every `src/`-touching PR (P1/P2/P3/P4) must also pass the **golden-staleness check (PR26)**, the **presolve-divergence detector**, and the **`--resolve-changed --since-commit 750803b2` checkpoint re-solve** — no changed golden moves backward vs the **Day-0 code anchor `750803b2`** (the Sprint 33 close). NB: `4cbf8bff` (the S31 close, the old DB byte-anchor) is **historical** — the S33 P6 sample fix moved the DB off it.

---

## 1. Per-track gates (P1–P5)

### P1 — mine Head-Offset Dual Subsystem (#1443)

- **Disposition:** PROCEED (**H_dual** — anchor the head-placed precedence dual's *complementarity* to the head-side variable, a structural pairing change). **NB — H1 head-label re-keying was REFUTED (value-invariant, S33 Day-2):** re-labelling the multiplier leaves the warm residual byte-identical, so the fix is **not** a keying tweak.
- **PROCEED precondition (PR24/PR27 `/tmp` before `src/`, `modelstat` asserted, `x.up=inf` BANNED):** re-confirm the CASE_B fingerprint (`stat_x(3,1,1)` rel 2.37, dual CONSISTENT) + the **22-row** `c`-boundary + `d\c`-ring residual. Prototype **H_dual** by hand-editing a **scratch copy** (`/tmp/mine_mcp_prototype.gms` + `/tmp/mine_mcp_presolve_prototype.gms`, **not** the committed `data/gamslib/mcp/mine_mcp.gms`), run from the **repo root** (the emit `$include "data/gamslib/raw/mine.gms"` is repo-relative). **Gate (reframed — the key correction):** the **cold** MCP reaches **MODEL STATUS 1 at profit 17500** (`modelstat=1` asserted), with the 22 boundary rows closing in the *cold* solution + interior rows unperturbed — **NOT** `N → 0` at the warm point (keying-invariant). Fix surface: the `head_domain_offsets` IR carrier (`src/ir/symbols.py` field, `src/ir/parser.py` populate) wired into `_try_build_param_offset_crossterm` (`src/kkt/stationarity.py:5712`, the first stationarity-cross-term consumer) + the `_emit_nlp_presolve` transfer (`src/emit/emit_gams.py`). No-regression: `--resolve-changed --since-commit 750803b2` GO (srpchase / the param-offset cohort byte-stable).
- **REPLAN exit (H3′):** H_dual cannot drive the **cold** MCP to MS-1 @ 17500 without perturbing interior rows or regressing srpchase → the boundary is a genuine dual-degeneracy the emit cannot deterministically reconcile → hand off a deeper head-offset dual architecture (or a PATH-consultation question) to a later sprint; mine stays `model_infeasible`; budget → P6/P7 (Task 9).

### P2 — sarf Symbolic/Parametric `stat_task` Emit Mode (#1385)

- **Disposition:** PROCEED (the three-site O(active) symbolic emit + the 2-D constraint gate, atomically).
- **PROCEED precondition (PR20 tractability + atomicity):** eliminate the 369,024-column materialization at **all three** sites — S1 the `acost3` body-differentiation (`src/ad/constraint_jacobian.py`), S2 the variable-column enumeration (`src/ad/index_mapping.py`), S3 the variable stationarity (`src/kkt/stationarity.py`) — replaced by **one** symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)` (the 7-term derivation) + `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0`. **Time `sarf` translate:** must be **seconds** (srpchase's 1-D analogue ~2.9s — the O(active=398) reference), not the current **> 116s** (live re-confirm). The `stat_task` matches the derivation with **symbolic** multiplier indices — **no set-name-literal indices** (verify via `grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` = empty). The 2-D constraint gate + the S1/S2/S3 parametric emit + the `task.fx` fixing land **atomically** (a re-emit without cross-terms = an inconsistent MCP); the golden is byte-stable + deterministic ×3 `PYTHONHASHSEED`; `--resolve-changed --since-commit 750803b2` GO (sarf the only changed golden).
- **REPLAN exit:** the parametric emit **re-triggers the translate timeout** (a 4th enumeration site, unexpectedly still O(instances)) → re-scope the parametric emit (documented); +Translate deferred; budget → P6/P7.

### P3 — fawley Second-Index Correction + Forcing (#1111/#1112)

- **Disposition:** PROCEED (the **constraint-index-diagonal** `sameas` correction, for **correctness**) + the **forcing hand-off** for the +Solve. **NB — H-b is CONFIRMED (S33 Day-4), not conditional:** sameas + all bound-transfer signs → warm `max|stat_bq| ~0` but the MCP still solves **MS-5 @ 4399.557** (LP opt 2899.25); the divergence is non-emit. **The fix surface is the general `sameas`-guard path (`_build_sameas_guard`/`_get_or_create_fresh_alias` in `_add_indexed_jacobian_terms`, `src/kkt/stationarity.py:5861`), NOT the 1-D polygon core** (`bq` is 2-D; `_var_at_two_indices_complement` `src/kkt/stationarity.py:7291` never fires).
- **PROCEED precondition (PR24/PR27 `/tmp` before `src/`, `modelstat` asserted):** re-confirm `max|stat_bq|` 473 → 18.468 with the constraint-index-diagonal `$(sameas(cfq__, cf))` on qsb/pbal; the residual-18.468 is the **P4** cc-dist bound-transfer cell (not a second over-sum), so `max|stat_bq| → 0` needs **P3 + P4** together. **Gate:** the constraint-index-diagonal correction closes the over-sum, fires on **every** qsb/pbal `cfq`, with **no mbal-term change** and **no 1-D-core regression**; `--resolve-changed --since-commit 750803b2` GO (polygon/ps2 use the 1-D core, a different path). The **+Solve is a P5 forcing hand-off** (H-b) — the correction ships for correctness, and the +1 genuine floor is **contingent on forcing** (fawley does not cold-match under H-b).
- **REPLAN exit:** the generalization **leaks onto the mbal / variable-index-diagonal shape or regresses the 1-D polygon core** (correctness risk) → REPLAN. (No H-a/H-b branch — H-b is already confirmed; fawley moves no in-sprint bucket, the +Solve is the P5 forcing survey's.)

### P4 — Max-Convention Bound-Transfer-Sign Track (NEW)

- **Disposition:** PROCEED (the **sign-robust** `piL_*/piU_*` transfer, `= abs(var.m)` at the active bound). **Honest finding: the MAXIMIZE `model_infeasible` cohort is otherwise-attributed** (fawley H-b, mine P1/`x.m=0`, camcge Epic-5, rocket Case-c), so the realistic +Solve target reduces to **agreste** (P6-entangled) — P4's firm value is the **general warm-start-correctness fix**; the +Solve is **contingent**.
- **PROCEED precondition (PR24/PR27 `/tmp` before `src/`, `modelstat` asserted):** re-confirm the min-convention gates at `src/emit/emit_gams.py:1590` (`piL`: `…and var.m > 0`) + `:1603` (`piU`: `…and var.m < 0`) skip the correctly-signed multiplier for MAXIMIZE; the sign-robust `= abs(var.m)` at the **active bound** closes the fawley cc-dist cell (`bq.m = -18.468`, Day-4 proven) + the mine 3 upper-bound `x.m > 0` rows. **Gate:** implement sense-aware (**Option B** — `model_ir.objective.sense == ObjSense.MAX`; MINIMIZE byte-identical, only MAXIMIZE goldens change; precedent `src/ad/gradient.py:300`); the sign-robust transfer fires **only** at active bounds (no over-transfer on interior/presolve-match models); `--resolve-changed --since-commit 750803b2` GO over the ~20 MAXIMIZE presolve-match models (the regression-risk set). The **+Solve survey** (in-sprint): for each candidate (primarily agreste), does the sign-robust transfer close the warm residual **AND** reach MS-1 (warm-residual-driven → +Solve) vs stay MS-5 (structural)?
- **REPLAN / documented-finding exit:** no candidate is warm-residual-driven (the a-priori-likely outcome) → the sign-robust transfer ships as a **general warm-start-correctness fix** with **no +Solve** (a documented finding, not a correctness REPLAN); OR the change over-transfers / regresses the MAXIMIZE presolve-match cohort (`--resolve-changed` NO-GO) → re-scope (Option B is the mitigation).

### P5 — camcge Dual-Consistent Walras (#1330 → Epic 5) + rocket PATH (#1462 → Sprint 35)

- **Disposition:** camcge **Epic-5-deferred**; rocket **→ Sprint-35 consultation**. **No Sprint-34 emit; the Case-c sign flip is BANNED.** Step 1 (`nu_mps_fx` → `stat_mps` Case-a) landed on main (S32, PR #1553).
- **PROCEED precondition (PR27 check-the-dual-side, `/tmp` before `src/` — the Epic-5 gate):** the `/tmp` prototype of the **full** dual-consistent redefinition (keep **every** market-clearing row + the consumption-weighted numéraire + **redefine the redundant market's dual via Walras' law**) must reach **MS-1 at omega 191.7346** (assert `modelstat`), verified against the KKT **dual** not just the primal. The **S1∧S2∧S3 detector** must flag **only** camcge (**S3** = cold-MCP-singular-at-iter-0, the false-positive guard; irscge/lrgcge/moncge/stdcge pass through cold MS-1, only camcge cold MS-4 — live DB confirmed). **rocket:** re-confirm the residual is **clean at the NLP point** (the boundary signature `stat_ht(h0)`/`stat_ht(h50)`/`stat_step`, dual CONSISTENT) **before** any forcing — a *forcing* problem, not an emit bug; the sign flip is not exercised.
- **REPLAN exit (the realized disposition):** the camcge `/tmp` prototype stays **MS-4** (the Walras rank-deficiency is deeper than the dual redefinition too) → the numéraire falls to a per-model-numéraire-declaration **Epic-5** item; camcge stays `model_infeasible` (**expected**, given the banked price-pin-MS-4 evidence). rocket's `--force` survey is **exhausted** (all MS-5) → the packaged PATH-consultation input is **submitted to the Sprint-35 consultation** (a conditional hand-off, no firm KPI); budget → P6/P7.

---

## 2. Gate summary table

| Track | Model | Disposition | PROCEED precondition (control-before-`src/`) | REPLAN exit |
|---|---|---|---|---|
| **P1** | mine (#1443) | PROCEED (H_dual) | anchor the head-placed dual's complementarity to the head-side variable (via `head_domain_offsets`); **cold** MCP MS-1 @ 17500 (`modelstat`; **not** warm `N→0` — keying-invariant); no-regression GO. **NB: H1 keying REFUTED (value-invariant).** | H_dual can't reach cold MS-1 without perturbing interior/regressing srpchase → deeper dual architecture (later sprint) |
| **P2** | sarf (#1385) | PROCEED | eliminate 369K at 3 sites (S1 `acost3` / S2 index-map / S3 stationarity); one symbolic `stat_task$taskposs` + `task.fx`; translate seconds not >116s; no set-name literals; atomic; golden byte-stable + det ×3; GO | parametric emit re-triggers the timeout → re-scope; +Translate deferred |
| **P3** | fawley (#1111/#1112) | PROCEED (correctness) + forcing hand-off | the constraint-index-diagonal `sameas` path (2-D, NOT the 1-D core); 473→18.468, no mbal/1-D-core move (GO); **+Solve → P5 forcing (H-b confirmed)**; floor contingent on forcing | gate leaks onto mbal / regresses the 1-D core → REPLAN |
| **P4** | bound-transfer (NEW) | PROCEED (correctness; +Solve contingent) | sign-robust `= abs(var.m)` at the active bound (Option B sense-aware, `src/emit/emit_gams.py:1590`/`:1603`); closes fawley cc-dist + mine 3-row cells; no over-transfer; GO over the MAXIMIZE presolve cohort; +Solve survey (agreste) | no candidate warm-residual-driven → general-correctness fix, no +Solve (documented); over-transfer → re-scope |
| **P5** | camcge (#1330) + rocket (#1462) | camcge **Epic-5-deferred**; rocket **→ Sprint-35** | camcge: `/tmp` full dual-consistent redefinition → MS-1 @ 191.7346 (dual side); S1∧S2∧S3 flags camcge only. rocket: residual clean at NLP point; **sign flip BANNED** | camcge `/tmp` stays MS-4 → per-model Epic-5 fallback (**expected**); rocket survey exhausted → Sprint-35 consultation |

**Cross-cutting:** every gate cites `kkt_residual.py` (PR27) as the Case-(a/b/c) verdict engine; every emit-touching PR (P1/P2/P3/P4) must also pass the golden-staleness check (PR26), the presolve-divergence detector, and the **`--resolve-changed --since-commit 750803b2`** checkpoint re-solve; P5-camcge is Epic-5-deferred (no Sprint-34 emit) and P5-rocket is a docs/forcing hand-off (no emit change). **`modelstat` is asserted before every objective read; `x.up=inf` is BANNED (mine); the sign flip is BANNED (Case-c).**

---

## 3. Known-Unknowns dispositions (gate-layer)

| Unknown | Summary | Gate disposition |
|---|---|---|
| **1.2** | mine H_dual reconciliation → cold MS-1 | ✅ (gate) — P1 PROCEED (H_dual) behind the **cold-MCP-MS-1-@-17500** gate (`modelstat` asserted, `x.up=inf` BANNED), **not** the warm `N→0` (keying-invariant); H3′ deeper-dual-architecture REPLAN exit. |
| **2.2** | sarf three-site O(active) elimination / no timeout re-trigger | ✅ (gate) — P2 PROCEED behind the O(active=398) translate-budget probe (seconds not >116s) + the atomicity/anti-pattern (no set-name literals) checks; timeout-re-trigger REPLAN exit. |
| **3.1** | fawley constraint-index-diagonal `sameas` correction | ✅ (gate) — P3 PROCEED (correctness) behind the 473→18.468 constraint-index-diagonal correction + the no-regression GO (no mbal / 1-D-core move); **the +Solve is a P5 forcing hand-off (H-b confirmed)**; gate-leak REPLAN exit. |
| **4.1** | bound-transfer sign-robust transfer / no over-transfer | ✅ (gate) — P4 PROCEED behind the sign-robust `= abs(var.m)` closing the fawley cc-dist + mine 3-row cells + the active-bound gating (no over-transfer) + `--resolve-changed` GO over the MAXIMIZE presolve cohort; +Solve contingent on the survey; documented-general-correctness-finding exit. |
| **5.1** | camcge dual-consistent Walras `/tmp`-to-MS-1 | ✅ (gate) — P5-camcge gated on the `/tmp` full-redefinition prototype reaching MS-1 @ 191.7346 (dual side) + the S1∧S2∧S3 detector; **Epic-5-deferral REPLAN exit is the expected outcome** (the numéraire falls to the per-model Epic-5 fallback). |

---
**Document Status:** ✅ Complete — Sprint 34 Prep Task 8 (docs-only)
**Last Updated:** 2026-07-19 · **Owner:** Sprint 34 prep (KKT/emit specialist)

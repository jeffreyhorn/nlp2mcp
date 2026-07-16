# Sprint 33 Phase-0 Acceptance Gates (PR20 + PR24 + PR27)

**Prep Task:** 8 (Critical) · **Date:** 2026-07-16 · **Owner:** Sprint 33 prep (KKT/emit specialist)
**Scope:** docs-only — consolidates the per-track PROCEED/REPLAN gates for the five Sprint-33 priorities (P1 mine, P2 sarf, P3 fawley, P4 camcge, P5 rocket/Case-c). The authoritative per-track detail lives in each Task-3–7 design doc (`MINE_CROSSTERM_DESIGN.md`, `SARF_EMIT_SUBSYSTEM_DESIGN.md`, `FAWLEY_SECOND_INDEX_DESIGN.md`, `CAMCGE_WALRAS_DESIGN.md`, `ROCKET_CASEC_FORCING_PLAN.md`); this document is the single-page index + the control-experiment discipline for the sprint.

---

## 0. The standing discipline (why these gates exist)

- **PR24 — the banked fix surface is a Day-0-re-confirm hypothesis, not fact.** Sprint 32 REPLAN'd all five deep tracks after a control refuted the original premise — and Sprint 33's own Task 3 **refuted the banked mine premise** (the cross-term is algebraically correct; the fix is re-scoped to multiplier-keying). Each gate frames its fix surface as a hypothesis re-confirmed at Day 0 in the Task-3–7 designs.
- **PR27 — the `/tmp` control runs BEFORE any high-blast-radius `src/` change.** Every emit gate's PROCEED precondition is a `/tmp` control that must pass first.
- **Assert `modelstat` before reading an objective** (the Sprint-31 measurement-error lesson): every warm/cold solve step asserts `mcp_model.modelstat` before any objective read. **`x.up=inf` is a structurally invalid experiment (BANNED)** for mine. **The objective-gradient sign flip is BANNED** for the Case-c family (control-refuted 4× S30–S31).
- **Emit-touching CI gates.** Every `src/`-touching PR (P1/P2/P3) must also pass the **golden-staleness check (PR26)**, the **presolve-divergence detector**, and the **`--resolve-changed --since-commit ee51ed9e` checkpoint re-solve** — no changed golden moves backward vs the **Day-0 code anchor `ee51ed9e`** (the Sprint 32 close; distinct from `4cbf8bff`, the DB byte-anchor).

---

## 1. Per-track gates (P1–P5)

### P1 — mine Head-Offset Bound-Active Cross-Term Architecture (#1443)

- **Disposition:** PROCEED (H1 — the head-offset multiplier-keying reconciliation). **NB — the banked premise was REFUTED (Task 3):** the emitted `stat_x` cross-term is algebraically correct (verified by from-scratch ∂-derivation + source trace of `_try_build_param_offset_crossterm`), so the fix is **not** a cross-term re-derivation.
- **PROCEED precondition (PR24/PR27 `/tmp` before `src/`, `modelstat` asserted, `x.up=inf` BANNED):** re-confirm the wrong-sign `N` at the **6 bound-active `c`-boundary rows** (`x(1,3,{1,2,3})`, `x(3,1,2)`, `x(3,2,1)`, `x(4,1,1)`). Prototype **H1** — key `comp_pr`/`lam_pr` + the `stat_x` cross-term to the **head label `(k,l+1,i,j)`** (where the NLP stores `pr.m`) via the currently-unused `head_domain_offsets` IR — in a `/tmp` control → warm residual **`N → 0` at ALL 6 bound-active rows AND unchanged (0) at every interior row** → presolve **MS-1 at profit 17500**. Fix surface: `src/kkt/stationarity.py` (`_try_build_param_offset_crossterm` + the multiplier keying) + `src/ad/…` head-label multiplier plumbing. No-regression: `--resolve-changed --since-commit ee51ed9e` GO (srpchase / the param-offset cohort byte-stable).
- **REPLAN exit (H3):** H1 (and the H2 `d\c`-ring reconciliation) cannot drive `N → 0` without perturbing interior rows or regressing srpchase → the residual is a deeper head-offset dual-architecture gap → hand off a dedicated head-offset dual subsystem to a later sprint; mine stays `model_infeasible`; budget → P6/P7 (Task 9).

### P2 — sarf Symbolic Parametric `stat_task` Emit Subsystem (#1385)

- **Disposition:** PROCEED (the three-site O(active) symbolic emit + the 2-D constraint gate, atomically).
- **PROCEED precondition (PR20 tractability + atomicity):** eliminate the 369,024-column materialization at **all three** sites — S1 the `acost3` body-differentiation (`src/ad/constraint_jacobian.py`), S2 the variable-column enumeration (`src/ad/index_mapping.py`), S3 the variable stationarity (`src/kkt/stationarity.py`) — replaced by **one** symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)` (the banked 7-term derivation) + `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0`. **Time `sarf` translate:** must be **seconds** (srpchase's 1-D analogue ~2.9s on the current runner; 6.56s under the slower Sprint-32 runner — the same O(active) reference), not the current **> 75s**. The `stat_task` matches the banked derivation with **symbolic** multiplier indices — **no set-name-literal indices** (verify via `grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` = empty). The 2-D constraint gate + the S1/S2/S3 parametric emit + the `task.fx` fixing land **atomically** (a re-emit without cross-terms = an inconsistent MCP); the golden is byte-stable + deterministic ×3 `PYTHONHASHSEED`; `--resolve-changed --since-commit ee51ed9e` GO (sarf the only changed golden).
- **REPLAN exit:** the parametric emit **re-triggers the translate timeout** (unexpectedly still O(instances)) → re-scope the parametric emit (documented); +Translate deferred; budget → P6/P7.

### P3 — fawley Second-Index Cross-Term Generalization (#1111/#1112)

- **Disposition:** PROCEED (conditional) — the second-index `sameas`-guard generalization. **NB — the fix surface is the general indexed cross-term `sameas`-guard path (`_build_sameas_guard` / `_get_or_create_fresh_alias`), NOT the 1-D polygon core** (`bq` is 2-D).
- **PROCEED precondition (PR24/PR27 `/tmp` before `src/`, `modelstat` asserted):** re-confirm the Day-11 control (`max|stat_bq|` 473 → 18, 96%) and localize the residual 18.47 **by column**. Prototype the full generalization (extend the diagonal-`sameas` logic so **every** second-index `cfq` gets the `$(sameas(cfq__, cf))` restriction, covering qsb/pbal) → **`max|stat_bq| → 0`** (not 96%) at the warm point → presolve **MS-1 at the LP optimum 2899.25** (**H-a**). Fix surface: `src/kkt/stationarity.py` (the `sameas`-guard path in `_add_indexed_jacobian_terms`). No-regression: `--resolve-changed --since-commit ee51ed9e` GO — polygon/ps2 (the 1-D core, a different path) untouched, and **no mbal-term change** for fawley or any other 2-D indexed-cross-term user.
- **REPLAN exit:** the generalization **leaks onto the mbal / first-index shape or regresses the 1-D polygon core** (correctness risk) → REPLAN; **OR** `max|stat_bq| → 0` yet the MCP stays **MS-5** (**H-b** — the divergence is a non-emit LP-convergence, separable from the emit) → the emit fix ships as a **genuine** cross-term correction and fawley's +Solve hands off to the P5 forcing survey. The +1 Solve / +1 genuine floor is **conditional** on the H-a/H-b outcome.

### P4 — camcge Dual-Consistent Walras Numéraire (#1330 → Epic 5)

- **Disposition:** **Epic-5-deferred.** Step 1 (the scalar-`fx` `nu_mps_fx` transfer → `stat_mps` Case-a) landed on main (S32, PR #1553); step 2 (the dual-consistent Walras numéraire) is the Epic-5 CGE transformation.
- **PROCEED precondition (PR27 check-the-dual-side, `/tmp` before `src/` — the Epic-5 gate):** the `/tmp` prototype of the **full** dual-consistent redefinition (keep **every** market-clearing row + the consumption-weighted numéraire + **redefine the redundant market's dual via Walras' law**) must reach **MS-1 at omega 191.7346** (assert `modelstat`), verified against the KKT **dual** not just the primal. The **S1∧S2∧S3 detector** must flag **only** camcge across irscge/lrgcge/moncge/stdcge (**S3** = cold-MCP-singular-at-iter-0, the false-positive guard; the four siblings pass through cold MS-1, only camcge cold MS-4).
- **REPLAN exit (the realized disposition):** the `/tmp` prototype stays **MS-4** (the Walras rank-deficiency is deeper than the dual redefinition too) → the numéraire falls to a per-model-numéraire-declaration **Epic-5** item; camcge stays `model_infeasible`. Given the banked evidence (price-pin MS-4, 3+ sprints of MS-4 variants), this is the **expected** outcome — the Sprint-33 disposition is Epic-5-deferred; budget → P6/P7.

### P5 — rocket + hhfair/CGE Case-c Forcing (#1462 / #1236)

- **Disposition:** PROCEED (hand-off + forcing survey; **no firm KPI**). **No emit fix; the sign flip is BANNED.**
- **PROCEED precondition (PR27 residual-clean-before-forcing):** re-confirm each Case-c model's residual is **clean at the NLP point** *before* any forcing — **rocket** the discretized-optimal-control **boundary** signature (`stat_ht(h0)`/`stat_ht(h50)`/`stat_step`, move with the warm-start value; interior near tol; dual CONSISTENT); **hhfair + CGE cluster** the `case_c_objdef` signature (`stat_u`/`stat_xp`, the objective-defining intermediate variable, `nu_obj=±1`). This keeps them *forcing* problems, not latent emit bugs (a Case-b interior residual would mean fix the emit first). The `--force {homotopy,multistart,optfile}` survey: **"a lever crosses"** = global MS-1 (rocket MS-5→MS-1 = +Solve; hhfair mismatch→87.159 = +Match; CGE cluster cold match at 26.0914 = methodology→genuine floor); **"banked"** = documented Case-c. **The sign flip is not exercised** (BANNED, refuted 4×).
- **REPLAN exit:** N/A for the emit (no emit fix). rocket's survey is **exhausted** (all MS-5) → the packaged PATH-consultation input is **submitted to the Sprint-34 consultation** (rocket's +1 Solve is a conditional hand-off); any hhfair/CGE multistart cross is conditional (a priori unpromising) → else banked Case-c.

---

## 2. Gate summary table

| Track | Model | Disposition | PROCEED precondition (control-before-`src/`) | REPLAN exit |
|---|---|---|---|---|
| **P1** | mine (#1443) | PROCEED (H1) | head-label-keyed `comp_pr`/`lam_pr`/cross-term (via `head_domain_offsets`); warm residual `N → 0` at all 6 bound-active rows + interior unchanged (`modelstat`) → presolve MS-1 @ 17500; no-regression GO. **NB: cross-term premise REFUTED — the fix is multiplier-keying.** | H1/H2 can't close `N` without perturbing interior/regressing srpchase → deeper head-offset dual subsystem (later sprint) |
| **P2** | sarf (#1385) | PROCEED | eliminate 369K at 3 sites (S1 `acost3` / S2 index-map / S3 stationarity); one symbolic `stat_task$taskposs` + `task.fx`; translate seconds not >75s; no set-name literals; atomic; golden byte-stable + det ×3; GO | parametric emit re-triggers the timeout → re-scope; +Translate deferred |
| **P3** | fawley (#1111/#1112) | PROCEED (conditional) | the `sameas`-guard path generalization (2-D, NOT the 1-D core); `max\|stat_bq\| → 0` (not 96%) → MS-1 @ 2899.25 (H-a); no polygon/ps2/mbal move (GO) | gate leaks onto mbal / regresses the 1-D core → REPLAN; OR `max\|stat_bq\|→0` but MS-5 (H-b non-emit) → emit ships genuine, +Solve → P5 forcing |
| **P4** | camcge (#1330) | **Epic-5-deferred** | `/tmp` full dual-consistent redefinition (keep every row + numéraire + Walras-law dual redefinition) → MS-1 @ 191.7346 before `src/`; S1∧S2∧S3 flags camcge only | `/tmp` stays MS-4 → numéraire → per-model Epic-5 fallback; camcge `model_infeasible` (**expected**) |
| **P5** | rocket/Case-c (#1462/#1236) | PROCEED (hand-off + survey, no firm KPI) | residual clean at NLP point (rocket boundary / hhfair-CGE `case_c_objdef`) before forcing; `--force` survey (crosses = global MS-1 vs banked); **sign flip BANNED** | rocket survey exhausted → PATH-consultation input **submitted to Sprint 34**; hhfair/CGE cross conditional → else banked Case-c |

**Cross-cutting:** every gate cites `kkt_residual.py` (PR27) as the Case-(a/b/c) verdict engine; every emit-touching PR (P1/P2/P3) must also pass the golden-staleness check (PR26), the presolve-divergence detector, and the **`--resolve-changed --since-commit ee51ed9e`** checkpoint re-solve; P4 is Epic-5-deferred (no Sprint-33 emit); P5 is a docs/forcing hand-off (no emit change). **`modelstat` is asserted before every objective read; `x.up=inf` is BANNED (mine); the sign flip is BANNED (Case-c).**

---

## 3. Known-Unknowns dispositions (gate-layer)

| Unknown | Summary | Gate disposition |
|---|---|---|
| **1.1** | mine cross-term / bound-active reconciliation | ✅ (gate) — P1 PROCEED (H1) behind the warm-residual→0-at-bound-active-rows gate (`modelstat` asserted, `x.up=inf` BANNED); the cross-term premise is refuted (the fix is head-label multiplier-keying); deeper-coupling (H3) REPLAN exit. |
| **2.1** | sarf three-site O(active) elimination | ✅ (gate) — P2 PROCEED behind the O(active=398) translate-budget probe (seconds not >75s) + the atomicity/anti-pattern (no set-name literals) checks; timeout-re-trigger REPLAN exit. |
| **3.1** | fawley second-index `sameas`-guard generalization | ✅ (gate) — P3 PROCEED (conditional) behind the `max\|stat_bq\|→0` + MS-1 @ 2899.25 (H-a) / H-b-non-emit gate + the no-regression GO; gate-leak / mbal-regression REPLAN exit. |
| **4.1** | camcge dual-consistent Walras `/tmp`-to-MS-1 | ✅ (gate) — P4 gated on the `/tmp` full-redefinition prototype reaching MS-1 @ 191.7346 + the S1∧S2∧S3 detector; **Epic-5-deferral REPLAN exit is the expected outcome** (the numéraire falls to the per-model Epic-5 fallback). |
| **5.1** | rocket Case-c residual-clean-before-forcing | ✅ (gate) — P5 gated on the residual being clean at the NLP point (rocket boundary / `case_c_objdef`) before any forcing + the sign-flip BAN; the `--force` survey's crosses-vs-banked criteria; no emit fix. |

---
**Document Created:** 2026-07-16 · **Owner:** Sprint 33 prep (KKT/emit specialist)

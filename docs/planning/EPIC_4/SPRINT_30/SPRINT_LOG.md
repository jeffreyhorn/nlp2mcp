# Sprint 30 — Progress Log

Head-Domain-Offset Emit Architecture, Non-Convex Forcing & Offset-Alias AD (Sprint 29 carryforward). Schedule: `PLAN.md`; prompts: `prompts/PLAN_PROMPTS.md`.

| Day | Priority / Work | Metric delta | Status |
|---|---|---|---|
| 0 | Kickoff + Day-0 traces (PR24) | — (baseline confirmed) | ✅ DONE (docs/trace-only) |

---

## Day 0 — Kickoff + Day-0 Traces (2026-07-06)

**Branch:** `planning/sprint30-day0-kickoff`. Docs/trace-only — no `src/` change.

### Baseline confirmed = Sprint 29 final (no drift)

- **`git diff 68b5b4a7..HEAD -- src/ scripts/` is EMPTY** (S29 close = `68b5b4a7`, "SPRINT 29 CLOSED") → Day-0 = Sprint 29 final without a retest (Unknown 8.2). Every commit since the close is docs-only (the Sprint-30 PROJECT_PLAN insertion + the Tasks 1–10 prep PRs).
- **DB recompute (canonical 142-model scope, `convexity.status ∈ {verified_convex, likely_convex}`)** reproduces the Sprint 29 final headline exactly:

  | Metric | Day-0 | Target (S30) |
  |---|---|---|
  | Translate | **135** | ≥ 135 (stretch +1) |
  | Solve | **107** | ≥ 109 (mine + rocket, REPLAN-prone) |
  | Match | **92** | maintain ≥ 92; genuine floor 69 → ≥ 72 |
  | model_infeasible | **7** | ≤ 5 |
  | path_syntax_error | **8** | ≤ 8 |
  | path_solve_terminated | **4** | ≤ 5 |
  | path_solve_license | 9 | — |

- **PR25 tally:** genuine floor **69** / methodology ~23. Firm path (genuine floor → ≥ 72) = robert (P1a) + Class-B `stat_pz` (P7) + offset-alias polygon/himmel16 (P5) + hhfair-if-Case-b (P3). The +2 Solve (mine + rocket) is REPLAN-gated (§`REPLAN_RISK_ASSESSMENT.md`).

### Day-0 traces (PR24) — every banked surface re-confirmed at Sprint-30 HEAD

| Track | Trace result (Sprint-30 Day-0) | Verdict |
|---|---|---|
| **robert** (P1a) | `kkt_residual.py` → CASE_B, `stat_x(high,3)` rel **7.20**, dual transfer CONSISTENT — but this top row is the **same-index transfer artifact** (`TOOLING_READINESS_AUDIT.md` Tool 1). The operative surface is the objective-gradient `stat_s` drop, cold-confirmed by the control experiment (`stat_s`-patch → **11025.0**; `stat_x`-patch → unchanged 6741.67). | Confirmed — objective-gradient `stat_s`, NOT the head-offset cross-term (Unknown 1.1 ❌ / 1.4 ❌ absorbed by the P1 split). |
| **mine** (P1b) | `kkt_residual.py` → CASE_B, `stat_x(4,1,1)` rel **1.33**, CONSISTENT. **Cold-INFES histogram** (the 4th-site question): cold MS-5, **51 INFES** dominated by the `comp_pr` precedence complementarity (`pr` rows nw 6 / ne 9 / se 12 / sw 11 = 38) + the coupled **`x → 4.07e10`** blowup + `def` (1). **NO distinct 4th bound-row site** — `comp_lo_x`/`comp_up_x`/`stat_x` are **not** in the INFES set (the #1224 `stat_x` cross-term already landed). The `nw` direction (`li=lj=0`) is least-infeasible (6) vs ne/se/sw (9/11/12) — the parameter-offset directions carry the residual, exactly the Day-7 `l+1 × li(k)/lj(k)` coupling. | Confirmed — the 3-site set appears **complete** (no 4th site); PROCEED-lean on the coordinated `comp_pr` fix; the cold `x → 4e10` is the LCP residual the fix must drive to 0. |
| **rocket** (P2) | Case-c — the emit residual is clean at the NLP point; the cold/presolve MCP is **MS-5** intrinsic non-convergence (Task-4 evidence: 477 INFES; no PATH-option config converges). | Confirmed — forcing-scaffold territory; the +1 Solve is the Days-2–3 REPLAN decision (→ Sprint-31 PATH consultation). |
| **hhfair** (P3) | Emit `--nlp-presolve` + GAMS `action=c`: **first error is `$184` "Domain list redefined"** on the widened-VARIABLE `n` (source `n(t)` at `hhfair.gms:43` under the `$onMultiR $include` vs the MCP-widened `n(tl)`), *then* the `$257`/`$141` cascade. | Confirmed — the `$184` widened-VARIABLE blocker (not the Day-0-attributed `$141`), matching the Sprint-29 Day-8 diagnosis. |
| **Class-B** (P7) | `kkt_residual.py` on the cluster → **irscge** `stat_pz(MLK)` rel **1.00**, **lrgcge** `stat_pz(MLK)` rel **1.00**, **moncge** `stat_pz(BRD)` rel **1.00** — all CASE_B, all dual transfer CONSISTENT. | Confirmed — identical relative residual (missing-unit-coefficient fingerprint) → **one general-emit coefficient fix converts all three**; NOT Walras (full-rank block, distinct from camcge). |
| **polygon** (P5) | `kkt_residual.py` → CASE_B, `stat_theta(i12)` rel **0.492**, CONSISTENT. | Confirmed — the successor-offset objective cross-term (coupled with the distance-Jacobian symmetry, the Day-5-revert coupling). |
| **himmel16** (P5) | `kkt_residual.py` → CASE_B, `stat_area(1)` rel **2.00**, CONSISTENT. | Confirmed — the cyclic `i++1` cross-term is present; the 2.0 is the objvar-gradient-sign defect (distinct from polygon). |
| **camcge** (P6) | Banked: MS-4 Infeasible at iteration 0 (inherent Walras-law singular Jacobian) — the Epic-5 drop-one-`lmequil`-instance + fix-numéraire transformation (`CAMCGE_WALRAS_TRANSFORM_DESIGN.md`). | Confirmed banked (Day-11 empirical gate). |
| **sarf** (P4) | Banked: `translate_failure` (the 2-D dynamic-subset blow-up — `tbal`/`equipb1`/`equipb2` = 1,152 instances — that the srpchase 1-D short-circuit doesn't catch). | Confirmed banked (Day-9 atomic symbolic-emit + tractability gate). |

### Gate Traced-Fix-Surface lines

- **mine / rocket / hhfair** gates already carry a *confirmed* `Traced Fix-Surface (Day-0)` from Sprint-29 Day-0 — still valid (no `src/` drift); the Sprint-30 Day-0 re-confirmation above is recorded here (the mine cold-INFES histogram is the new Sprint-30 finding: no 4th site).
- **robert / Class-B** gates carried a `Day-0 hypothesis` — **upgraded to Sprint-30 Day-0 CONFIRMED** (this log's table + the gate notes).

### Day-0 outcome

Baseline = Sprint 29 final (no drift); all 9 banked surfaces re-confirmed at HEAD; the mine 3-site set is complete (no 4th bound-row site); Sprint 30 proceeds to **Day 1 (P1a robert objective-gradient fix)**. No `src/` change; no metric change. Trace-notes only.

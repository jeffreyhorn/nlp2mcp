# Max-Convention Bound-Transfer-Sign Track: Design (Sprint 34 Prep Task 6 — NEW)

**Created:** 2026-07-19 · **Owner:** Sprint 34 prep (emit specialist)
**Prep Task:** 6 (Priority 4 — NEW) · **Priority:** High
**Day-0 code anchor:** `750803b2` (S33 close) · no `src/` drift since (Task 2 `BASELINE_METRICS.md`)
**Anchors:** `SPRINT_33/DAY4_FAWLEY_CONTROL.md` §3 (the untransferred-bound-multiplier root) + §5 (the NEW cross-cutting finding) · `SPRINT_33/DAY5_FAWLEY_CLOSE.md` §3 (the hand-off)

> **Disposition (prep):** this document designs the **sign-robust `piL_*/piU_*` warm-start transfer** (the general max-convention correctness fix) + the MAXIMIZE-cohort **+Solve survey**. **The freshest, least-refuted lever** (a general warm-start-transfer gap discovered S33 Day 4, not a twice-refuted deep track) — but the honest finding below is that the current MAXIMIZE `model_infeasible` cohort is **otherwise-attributed** (fawley H-b, mine P1, camcge Epic-5, rocket Case-c, agreste P6), so P4's realistic outcome is a **general warm-start-correctness fix**, with the +Solve **contingent** on the in-sprint survey. **No `src/` change** — the `/tmp` control + the survey are the in-sprint gate.

---

## 1. Day-0 re-confirm (the gap — live)

The `--nlp-presolve` warm-start transfers the NLP bound multipliers to the MCP `piL_*/piU_*` in `_emit_nlp_presolve` (`src/emit/emit_gams.py`). The two transfer lines, re-confirmed live:

```python
# src/emit/emit_gams.py:1590  (lower-bound multiplier)
f"{qm}.l{domain_str}$(abs({qv}.l{domain_str} - {qv}.lo{domain_str}) < 1e-6 and {qv}.m{domain_str} > 0) = {qv}.m{domain_str};"
# src/emit/emit_gams.py:1603  (upper-bound multiplier)
f"{qm}.l{domain_str}$(abs({qv}.l{domain_str} - {qv}.up{domain_str}) < 1e-6 and {qv}.m{domain_str} < 0) = -({qv}.m{domain_str});"
```

Each gate has a **position** test (`abs(var.l − var.bound) < 1e-6` — the bound is active) **AND** a **sign** test (`var.m > 0` for `piL`, `var.m < 0` for `piU`). The sign tests encode the **MINIMIZE** convention: at an active *lower* bound a MINIMIZE reduced cost is `≥ 0`; at an active *upper* bound it is `≤ 0`. **For a MAXIMIZE solve the signs flip**, so both gates **skip the correctly-signed multiplier** → `piL`/`piU` left at 0 → a wrong warm-start (the harness CASE_B warm residual).

### The two discovery cells (Day-4, control-proven)

| Model | sense | cell | bound | `var.m` | current gate | result |
|---|---|---|---|---|---|---|
| **fawley** | MAX | `bq(cc-dist, fuel-oil)` | lower (active) | **−18.468** | `piL … and var.m > 0` → **skips** | `piL_bq = 0`; residual `= −bq.m` = 18.468 |
| **mine** | MAX | 3 upper-bound-active `x` rows | upper (active) | **> 0** | `piU … and var.m < 0` → **skips** | `piU_x = 0` at those 3 rows |

Both are MAXIMIZE LP solves (`solve exxon maximizing profit`; `solve mine maximizing profit`). The Day-4 control proved the sign-robust transfer (`= abs(bq.m)`) drives the fawley cc-dist warm residual **→ 0**; the mine 3-row case is the symmetric `piU` direction (S33 Day-2 §1: "max-convention upper-bound transfer closes only the 3 upper-bound-active `x.m>0` rows"). **The gap is general** (any MAXIMIZE model with an active-bound multiplier), not fawley-specific.

---

## 2. The sign-robust transfer design (Unknowns 4.1, 4.4)

**The fix:** the bound multiplier `piL`/`piU` equals the **magnitude** of the reduced cost at the active bound — `= abs(var.m)` — for **both** senses. Drop the min-convention sign gate; keep the active-bound **position** gate (so no over-transfer at interior/inactive bounds — `abs(var.m)` is ≈ 0 for a non-binding var anyway). **Fix surface (a Day-0-re-confirm hypothesis, PR24):** `src/emit/emit_gams.py:1590` (`piL`) + `:1603` (`piU`) in `_emit_nlp_presolve` — the **sole** fix surface (the indexed equality-multiplier transfers already use `abs()`, `src/emit/emit_gams.py:~145`).

**Two implementation options (a real blast-radius decision):**

- **Option A — universal `abs` (simpler):** `piL … $(abs(var.l − var.lo) < 1e-6) = abs(var.m)`; `piU … $(abs(var.l − var.up) < 1e-6) = abs(var.m)`. Correct for both senses (a bound multiplier is `|reduced cost|`). **Downside:** the emitted transfer *string* changes for **every** presolve-emitting model, so **all ~44 presolve goldens byte-change** (though MINIMIZE models re-solve **value-identically** — `abs(var.m) = var.m` when `var.m ≥ 0`). Large golden churn; `--resolve-changed` GO iff every bucket is invariant.
- **Option B — sense-aware (surgical, RECOMMENDED):** condition on the objective sense (`model_ir.objective.sense == ObjSense.MAX`, available in the IR — `src/ir/parser.py:55/4072`, used at `src/kkt/reformulation.py:717`). For **MINIMIZE** keep the current gates (byte-identical — zero churn); for **MAXIMIZE** flip to the sign-robust form. **Only the MAXIMIZE goldens change** → minimal blast radius + golden churn, and the regression surface is confined to the MAXIMIZE cohort.

**Recommendation: Option B** — the surgical, sense-aware emit keeps the MINIMIZE cohort byte-identical (no churn, no regression surface) and confines the change to the MAXIMIZE cohort, matching the fix's actual scope.

**Over-transfer / correctness (Unknown 4.1):** the position gate confines the transfer to active bounds; `abs(var.m)` is value-identical to the current form for MINIMIZE (so no MINIMIZE behavior change under Option B — byte-identical; under Option A — value-identical); for MAXIMIZE it supplies the previously-skipped `|var.m|`. No over-transfer on interior/inactive bounds (the position gate) or on presolve-match MINIMIZE models (value-identical).

---

## 3. The MAXIMIZE cohort + the +Solve survey (Unknowns 4.2, 4.3)

### 3.1 The cohort (from the committed DB + `solve … maximizing` scan)

The corpus has **~85 MAXIMIZE candidates** (of 142). The **+Solve targets** are the MAXIMIZE `model_infeasible` candidates — and each is **already attributed to another track**:

| MAXIMIZE `model_infeasible` | MS | attribution | P4 +Solve? |
|---|---|---|---|
| **fawley** | 5 | **H-b** (Task 5 — the warm residual closes but the MCP still solves MS-5 @ 4399.557; non-emit) | **No** (structural) |
| **mine** | 5 | **P1** head-offset dual; at the `c`-boundary `x.m=0` (nothing to transfer); P4 closes only the 3 upper-bound `x.m>0` warm-residual rows, not the solve | **No** (P1) |
| **camcge** | 4 | **Epic 5** Walras rank-deficiency (structural, not warm-residual-driven) | **No** (Epic 5) |
| **rocket** | 5 | **Case-c** non-convex (structural) | **No** (Case-c) |
| **agreste** | 5 | **P6** double-`solve` scenario-driver (CASE_B `stat_sales`; scope-verify pending) | **the one open candidate** |

**Honest finding:** four of the five MAXIMIZE `model_infeasible` candidates are structurally/otherwise-attributed, so **P4's realistic +Solve target reduces to agreste** — and agreste is **P6-entangled** (its CASE_B may be a scenario-driver artifact, not warm-residual-driven). So the **+Solve is contingent and a-priori uncertain**; P4's firm value is the **general warm-start-correctness fix** (it closes the harness CASE_B warm residual for MAXIMIZE models, improving the presolve-recovery substrate corpus-wide).

### 3.2 The +Solve survey (in-sprint)

For each MAXIMIZE `model_infeasible` candidate whose divergence is **not** already attributed to a structural track (primarily **agreste**), the in-sprint control: apply the sign-robust transfer, assert `modelstat`, and check whether the warm residual closes **AND** the MCP reaches MS-1 (**warm-residual-driven** → a +Solve) vs stays MS-5 (**structural**, like fawley's H-b). This per-candidate solve is **in-sprint** (Days 1–7), not runnable in this docs-only prep.

### 3.3 The regression-risk set (no-regression, Unknown 4.3)

The MAXIMIZE **presolve-match** cohort (~20 models: camshape, cclinpts, cpack, etamac, harker, himmel16, irscge, like, lrgcge, marco, moncge, paperco, polygon, robert, stdcge, tforss, weapons, worst, ps10_s_mn, ps5_s_mn) currently solves via presolve. The sign-robust change alters their warm-start (adds the skipped multipliers) → PATH starts from a different point → they must **not** regress. **Gate:** `--resolve-changed --since-commit 750803b2` **GO** — re-solve every changed golden, every bucket invariant. Under Option B only the MAXIMIZE goldens change, confining the re-solve set to this cohort + the MAXIMIZE `model_infeasible` candidates.

---

## 4. The pre-`src/` `/tmp` control (PR24/PR27 gate) — specification (executed in-sprint)

Run **before** any `src/` change; assert `modelstat`. **In this docs-only prep the criteria are a specification** (the Day-4 control already proved the fawley cc-dist closure).

1. **Re-confirm the gap** — the sign-robust `= abs(var.m)` closes the warm residual on the fawley cc-dist cell (Day-4, proven) + the mine 3 upper-bound rows (the symmetric `piU` direction). *Gate:* the harness warm residual at those cells → 0.
2. **+Solve survey** — for agreste (+ any newly-identified warm-residual-driven MAXIMIZE `model_infeasible`), apply the sign-robust transfer and assert `modelstat`: warm residual → 0 **AND** MS-1 (+Solve) vs MS-5 (structural).
3. **No-regression** — `--resolve-changed --since-commit 750803b2` **GO** (the MAXIMIZE presolve-match cohort re-solves to the same bucket; under Option B the MINIMIZE cohort is byte-unchanged).

**PROCEED** iff the sign-robust transfer closes the warm cells (proven) + `--resolve-changed` GO; **+Solve** iff a candidate is warm-residual-driven (survey); else **the correctness fix ships as a documented general warm-start improvement** (no +Solve).

---

## 5. Sizing + REPLAN exit (Unknown 4.2)

**10–16 h:**
- `/tmp` re-confirm (fawley + mine cells) + the MAXIMIZE-cohort +Solve survey (~3–5 h) — the Phase-0 control.
- The sign-robust transfer (Option B sense-aware at `src/emit/emit_gams.py:1590`/`:1603`) + the objective-sense wiring (~4–7 h).
- No-regression (`--resolve-changed`, the MAXIMIZE cohort) + determinism ×3 + a MAXIMIZE bound-transfer regression fixture (~3–4 h).

**REPLAN / documented-finding exit:** if the +Solve survey finds **no** warm-residual-driven MAXIMIZE `model_infeasible` candidate (the a-priori-likely outcome, given the attribution table §3.1), P4 ships the **sign-robust transfer as a general warm-start-correctness fix** (closes the harness CASE_B warm residual for the MAXIMIZE cohort) with **no +Solve** — a documented general-correctness finding, not a REPLAN on correctness. If the change **over-transfers / regresses** the MAXIMIZE presolve-match cohort (`--resolve-changed` NO-GO), re-scope (the sense-aware Option B is the mitigation).

**Front-load:** P4 is the freshest lever — run the survey early (Days 1–5) so its (likely modest) +Solve disposition is known by the Day-5 checkpoint.

---

## 6. Outcome for the Known Unknowns

| Unknown | Verdict | Finding |
|---|---|---|
| **4.1** | ✅ **VERIFIED** | The sign-robust `= abs(var.m)` at the active bound is correct for both senses (a bound multiplier is `|reduced cost|`); the position gate confines it to active bounds (no over-transfer). Two implementation options: **A** universal `abs` (all presolve goldens byte-change, MINIMIZE value-identical) vs **B** sense-aware (`ObjSense.MAX`-conditioned; MINIMIZE byte-identical, only MAXIMIZE goldens change) — **Option B recommended** (surgical, minimal churn). |
| **4.2** | ✅ **VERIFIED (design-level; the per-candidate +Solve survey is in-sprint)** | The MAXIMIZE `model_infeasible` cohort = {fawley, mine, camcge, rocket, agreste}; four are otherwise-attributed (fawley H-b, mine P1/`x.m=0`, camcge Epic-5, rocket Case-c), so the realistic +Solve target reduces to **agreste** (P6-entangled). **The +Solve is contingent/uncertain**; P4's firm value is the **general warm-start-correctness fix**. The per-candidate solve is in-sprint. |
| **4.3** | ✅ **VERIFIED (gate specified; the `--resolve-changed` run is in-sprint)** | The change byte-alters the transfer line; under **Option B** only the MAXIMIZE goldens change (MINIMIZE byte-identical). No-regression gate = `--resolve-changed --since-commit 750803b2` GO over the MAXIMIZE presolve-match cohort (~20 models) — the regression-risk set; the executed run is in-sprint. |
| **4.4** | ✅ **VERIFIED** | The min-convention gate is localized to `src/emit/emit_gams.py:1590` (`piL`, `and var.m > 0`) + `:1603` (`piU`, `and var.m < 0`) in `_emit_nlp_presolve` — the **sole** fix surface (re-confirmed live; the indexed equality-multiplier transfers already use `abs()` at `~:145`). |

---
**Document Status:** ✅ Complete — Sprint 34 Prep Task 6 (design; no `src/`)
**Last Updated:** 2026-07-19 · **Owner:** Sprint 34 prep (emit specialist)

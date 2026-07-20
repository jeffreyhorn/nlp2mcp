# Sprint 34 — Day 0 Trace Notes (Kickoff + Day-0 Traces + Control Probes)

**Date:** 2026-07-20
**Branch:** `planning/sprint34-day0-kickoff`
**Day-0 code anchor:** `750803b2` (S33 close, PR #1581)
**Scope:** docs/trace-only — no `src/` change. GO/NO-GO for Day 1.
**Verdict:** ✅ **GO for Day 1.** Baseline confirmed = S33 close; all four Phase-0 fingerprints re-confirmed **exactly** on the live tree; the control-probe setups re-confirmed; the deep `/tmp` construction controls (P1 H_dual cold-MS-1, P3 fawley localize, P4 abs-cell) are the in-sprint executed gates (Days 1/5/4) per their designs.

---

## 1. Baseline confirmation (= S33 close, no retest)

| Check | Result |
|---|---|
| `git diff 750803b2..HEAD -- src/ scripts/` | **empty** (no drift → reuse the committed DB, no fresh retest) |
| DB md5 (`data/gamslib/gamslib_status.json`) | `6166acab90dcaff8789255f8ada83c54` — matches `BASELINE_METRICS.md` byte-for-byte |
| Code-anchor derivation (`git log --first-parent main --grep='SPRINT 33 CLOSED'`) | `750803b2ee7472afe7443c395c02359b8f1ae3be` ✓ |
| `run_full_test.py --resolve-changed --since-commit 750803b2 --dry-run` | **GO: no emit goldens changed** ✓ |
| Determinism ×3 `PYTHONHASHSEED {0,1,42}` — mine re-emit | md5 `a394cbc3dee15015aa099d7a84e0fa30` ×3 byte-identical — **and matches the `BASELINE_METRICS.md`-recorded md5 exactly** (confirms determinism *and* zero emit drift from S33 close) |

**Day-0 baseline (142 corpus), byte-identical to S33 close:** Parse 142 · Translate 135 · Solve 108 · Match 93 · genuine floor 75 · model_infeasible 7 · path_syntax_error 7 · all-219 Match 96. Every Sprint-34 KPI delta is measured against this.

---

## 2. Day-0 traces (PR24) — Phase-0 fingerprints re-confirmed on the live tree

All four re-confirmed **exactly** vs `PHASE_0_ACCEPTANCE_GATES.md` §1 (`kkt_residual.py <model>.gms`, JSON in `/tmp/day0_*.json`):

| Track | Model | Verdict | Max-residual row | dual |
|---|---|---|---|---|
| **P1** | mine | CASE_B | `stat_x(3,1,1)` rel **2.37** (raw −3.20e+04), dual scale 1.35e+04 | CONSISTENT (comp 0, eq 0) |
| **P3** | fawley | CASE_B | `stat_bq(res-arab-l,fuel-oil)` rel **0.973** (raw **473**), dual scale 486 | CONSISTENT (eq 1.8e−12) |
| **P5** | camcge | CASE_B | **`stat_mps` cleared by S32 step 1** → top is now `stat_tm(biens-int)` rel 0.076 (the deeper MS-4 Walras/market-clearing residual; `stat_tm` guard stays `case_b`) | CONSISTENT |
| **P5** | rocket | CASE_C_OBJDEF | `stat_ht(h0)` rel **1.00** / `stat_step` 0.497 / `stat_ht(h50)` 0.438 (boundary; sign flip BANNED) | CONSISTENT |

- **mine** — matches the P1 fingerprint (CASE_B 2.37, dual CONSISTENT); the `(3,1,1)`-boundary shape + the 22-row `c`-boundary/`d\c`-ring breadth is the Task-3-established characterization. Cross-term algebraically correct + H1 keying value-invariant (S32/S33 — carried in, not re-litigated).
- **fawley** — matches exactly (0.973/473, `(*,fuel-oil)` column, dual scale 486). The residual-18.468 (the P4 cc-dist cell) is the target of the P3+P4 pair, not P3 alone.
- **camcge** — `stat_mps` no longer the top residual (S32 step 1 `nu_mps_fx` transfer holds on the live tree); the remaining MS-4 Walras structure (`stat_tm`/`stat_pwm`) is the Epic-5 scope.
- **rocket** — Case-c clean at the NLP point (a *forcing* problem, not an emit bug); the Sprint-35 PATH-consultation hand-off.

---

## 3. Control probes (all before any `src/`)

### (1) P2 sarf O(active) scoping probe — run FIRST (cheapest verdict) ✅ re-confirmed

- **`task(g,t,mn,mn)` Cartesian domain = 369,024** (card g=16 · t=24 · mn=31 · mn=31), confirmed from the declaration (`sarf.gms:394`) + the set member lists.
- The **active subset** `taskposs(g,t) ∧ tech(g,m,n)` is **runtime-computed** (`taskposs` at `sarf.gms:371` from `treq`/`atask`/`btask`; `tech` a data table) — **not statically enumerable** without running GAMS through the data section, exactly the Task-4 finding. The **398 active** is Task-4-verified (per-column diff of `acost3`'s scalar `sum((g,t,m,n)$taskposs, oc·task)` at `sarf.gms:454` + the `tbal`/`cap` sites `:426`/`:443`/`:446`).
- **Live blow-up confirmed:** the DB bucket for sarf is `nlp2mcp_translate.status = failure` (the > 116s materialization) with `parse = success` — the P2 REPLAN-gated build stands. The three enumeration sites (S1 `acost3` body-diff / S2 variable-column enumeration / S3 variable stationarity) are the atomic re-emit surface.

### (2) P1 H_dual `/tmp` structural prototype → cold-MS-1 — **Day-1 executed gate** (Unknown 1.2, DESIGN-SPECIFIED)

- **Seeded and re-confirmed at the fingerprint level:** mine CASE_B `stat_x(3,1,1)` 2.37, dual CONSISTENT; the DB confirms the **cold mine MCP is `mcp_solve.status = failure`** (MS-5; the NLP reference `model_status=1, objective 17500.0` — the cold-MS-1 gate target). The 22-row `c`-boundary + `d\c`-ring residual + `x.m=0` degeneracy is the Task-3 characterization.
- **The gate is the cold MCP reaching MS-1 @ 17500** (`modelstat=1` asserted; **`x.up=inf` BANNED**) — **NOT** the warm residual `N→0` (keying/pairing-invariant, S33 Day-2). The H_dual structural complementarity-pairing prototype (`/tmp/mine_mcp_prototype.gms` + `/tmp/mine_mcp_presolve_prototype.gms`, run from the repo root — the emit `$include` is repo-relative) is the **Day-1 executed gate** per `KNOWN_UNKNOWNS.md` Unknown 1.2 (the empirical "does H_dual reach cold MS-1?" is the Day-1/Day-2 verify, not a docs-prep result). **High REPLAN prior** — the premise is twice-refuted; no cold-MS-1 pass is claimed at Day 0.

### (3) P3 fawley localize-by-column `/tmp` — **Day-5 executed gate**

- The fingerprint (`stat_bq` 0.973/473, `(*,fuel-oil)` column) is re-confirmed. The `/tmp` sameas-patch localization (`max|stat_bq|` 473 → **18.468**, the constraint-index-diagonal control) is control-proven (S32 Day-11 + S33 Task-5); the residual-18.468 localizes to the **P4 cc-dist cell**, so `max|stat_bq| → 0` needs **P3 + P4 together**. H-b is confirmed (emit closes yet MCP MS-5 @ 4399.557; DB `mcp_solve.status = failure`, NLP LP opt 2899.2528). The correction ships for **correctness**; the +Solve is the P5 forcing hand-off. The `/tmp` re-confirm is the Day-5 gate.

### (4) P4 bound-transfer `/tmp` abs-cell — **Day-4 executed gate**

- The min-convention gates are at `src/emit/emit_gams.py:1590` (`piL`: `…and var.m > 0`) + `:1603` (`piU`: `…and var.m < 0`). The sign-robust `= abs(var.m)` at the active bound targets the fawley cc-dist cell (`bq.m=-18.468`, Day-4-proven) + the mine 3 upper-bound `x.m>0` rows. **Honest finding (Task 6):** the MAXIMIZE `model_infeasible` cohort is otherwise-attributed → the realistic +Solve target is **agreste** (DB: `mcp_solve.status = failure`, NLP MS-1 obj 17706.43; P6-entangled double-`solve`). The Option-B sense-aware `/tmp` cell + agreste survey is the Day-4 gate.

### (5) P5 camcge/rocket clean-at-NLP ✅ re-confirmed

- **camcge:** `stat_mps` cleared (§2); the residual is the MS-4 Walras structure; DB `mcp_solve.status = failure` with the NLP `model_status=2` (locally optimal, omega 191.7346 — the Epic-5 dual-consistent target). Epic-5-deferred.
- **rocket:** Case-c clean at the NLP point (§2); Sprint-35 PATH-consultation hand-off. **0 floor; sign flip BANNED.**

---

## 4. P6 back-half seed (Day 11) — re-confirmed at Day 0

- **ganges + gangesx:** both DB `mcp_solve.status = failure` with **identical NLP objective 6395.5444** — consistent with the Task-10 live-diagnosed **shared `$141/$145/$149` NaN-sanitization root** (`param(i)$(NOT (param(i) > -inf and param(i) < inf)) = 0` over params whose assignment depends on `dst.l`), distinct from sample's `$140` (the S33 P6 fix, a no-op here). A single fix may recover both — the designated best-remaining-shot.
- **agreste:** the double-`solve` scope caveat (`agreste.gms:294`/`:298`) — scope-verify before treating CASE_B `stat_sales` as an emit bug.

---

## 5. PR25 tally (genuine-floor vs methodology) — restated

- **Genuine floor 75** (anchor). The → +1 conversion map: **P1 H_dual cold-match** (High prior); **P3's genuine correction** *only if forcing lands the solve* (H-b — contingent, not firm); **P6 ganges/gangesx cold-match** (the firmest — the S33 sample precedent that the failure-cohort is a genuine bucket source). **P4 = 0 floor directly; P5 = 0 floor.**
- **Modal outcome = flat-KPI** (Solve 108 / Translate 135 / Match 93 / floor 75), beaten if at all by **P6**.

---

## 6. Go/No-Go

✅ **GO for Day 1.** No `src/` drift; DB byte-identical to S33 close; `--resolve-changed` GO; determinism ×3 byte-identical (and md5-matched to the recorded baseline); all four Phase-0 fingerprints re-confirmed exactly; the sarf O(active) blow-up + the P6 shared-root seed re-confirmed. No Day-0 blocker (the sole `🔍 INCOMPLETE` — Unknown 1.2, mine H_dual cold-MS-1 — is intentionally the Day-1 executed gate, not a prep blocker). Day 1 begins the **P1 mine H_dual head-offset dual reconciliation** against the reframed **cold-MS-1 @ 17500** gate. Docs/trace-only — no `src/`.

# Sprint 33 → Sprint 34 Carryforwards

**Filed:** 2026-07-17 (Sprint 33 close) · **Source:** `SPRINT_LOG.md` + `SPRINT_RETROSPECTIVE.md`
Each carryforward is **control-confirmed and de-risked** — a specification, not an open question. Sprint 33 shipped zero broken code; these are the precisely-characterized next steps.

---

## 1. mine — head-offset dual subsystem (P1, #1443)

**Disposition:** REPLAN (H3). H1 head-label multiplier re-keying was **control-refuted** (value-invariant: `l+1`-shifted transfer already stores the head-label value at the body label; warm residual unchanged 22→22 rows). No emit-consistent change closes the `c`-boundary — at the max row `stat_x(3,1,1)`, `x` is bound-active with NLP reduced cost `x.m=0`, the cross-term is structurally correct (−16000), and closing needs +16000 that neither a keying change (banned sign flip) nor a bound multiplier (`x.m=0`) can supply.
**The gap:** a deeper head-offset dual-architecture mismatch (the head-placed precedence dual `pr.m(k,l+1)` does not map to the `stat_x` boundary stationarity; 22-row breadth, broader than the banked 6).
**Hand-off:** `DAY2_MINE_REPLAN.md` + `DAY1_PROGRESS_NOTES.md` (the validated residual decomposition) + `MINE_CROSSTERM_DESIGN.md` + the S31 `head_domain_offsets` IR foundation (on `main`). A Sprint-34 dedicated head-offset dual subsystem.

## 2. sarf — symbolic-emit subsystem (P2, #1385)

**Disposition:** REPLAN (Option B, sprint-owner decision). Not refuted — a genuine 20–28h high-risk atomic rebuild for the lowest-leverage bucket (+1 Translate), deferred to a focused effort.
**The fix (spec):** a from-scratch **symbolic/parametric emit mode** for `task(g,t,mn,mn)` — stop enumerating its 369,024 columns (the active `taskposs ∧ tech` = 398 is not statically enumerable; `taskposs` is runtime-computed), emit one guarded `stat_task(g,t,m,n)$taskposs(g,t)` (the banked 7-term derivation) + `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0`, and let GAMS instantiate the 398 live rows. Three sites (S1 `acost3` body-diff `constraint_jacobian.py`, S2 column enum `index_mapping.py`, S3 stationarity `stationarity.py`), **atomic** (no safe partial).
**Hand-off:** `DAY6_SARF_ASSESSMENT.md` + `SARF_EMIT_SUBSYSTEM_DESIGN.md` (blow-up locus, 398-active sizing, 7-term derivation, atomicity spec, the O(active) budget gate).

## 3. fawley — sameas cross-term correction (P3, #1111/#1112)

**Disposition:** H-b (+Solve → forcing); the genuine sameas correction deferred (risk/reward). The qsb/pbal cross-terms miss the `$(sameas(cfq__,cf))` the mbal term has (control-proven: `max|stat_bq|` 473→18.468); but the fix surface is a **constraint-index diagonal** in `_add_indexed_jacobian_terms` (~1400 lines, a dozen `sameas` paths) — high blast radius for zero in-sprint bucket (fawley is H-b: MS-5 persists even with the warm residual closed).
**Hand-off:** `DAY4_FAWLEY_CONTROL.md` + `DAY5_FAWLEY_CLOSE.md` + `FAWLEY_SECOND_INDEX_DESIGN.md`. Needs the constraint-index diagonal extension + the no-regression gate (no mbal / 1-D-core move) + a fawley 2-D second-index shape fixture. fawley's +Solve is a forcing hand-off (H-b, non-emit divergence at fawley's scale).

## 4. The max-convention bound-transfer-sign track (NEW, cross-cutting)

**Disposition:** a general warm-start-transfer gap discovered Day 4. The `piL_*/piU_*` warm-start transfers are gated on min-convention `.m > 0` / `.m < 0`; for a **MAXIMIZE** solve they skip the correctly-signed bound multipliers — surfaced in **both** fawley (`bq.m<0` at a lower bound → the residual-18.468 cell) and mine (`x.m>0` upper-bound multipliers). For fawley it does not unlock the solve (H-b), but it is worth checking as a **+Solve lever on other MAXIMIZE models** whose MCP divergence is warm-residual-driven (not structural).
**Hand-off:** `DAY4_FAWLEY_CONTROL.md` §5 (the bound-transfer-sign analysis + the per-cell decomposition). A sign-robust transfer (`= abs(.m)` at the active bound) is the candidate fix; scope + regression-test across the max-model cohort.

## 5. camcge — dual-consistent Walras numéraire (#1330 → Epic 5)

**Disposition:** Epic-5-deferred (unchanged from S32). Step 1 (`nu_mps_fx` scalar-`fx` transfer → `stat_mps` Case-a) landed on `main` (S32). Step 2 (the dual-consistent Walras redefinition) reaches omega 191.7346 but MS-4 — deeper CGE research.
**Hand-off:** `CAMCGE_WALRAS_DESIGN.md` + `EPIC_5/CGE_DEGENERACY_SCOPING.md` (the S1∧S2∧S3 detector, the numéraire recipe).

## 6. rocket + Case-c forcing (#1462 / #1236)

**Disposition:** the FINALIZED rocket PATH-consultation input is submission-ready → the Sprint-34 PATH-author consultation (Ferris/Dirkse). hhfair + irscge/lrgcge/moncge + cesam/lnts are documented Case-c (bilinear / objective-defining-intermediate-variable; the sign flip is BANNED).
**Hand-off:** `ROCKET_CASEC_FORCING_PLAN.md` + `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`.

## Banked P6 follow-ons (not Sprint-34-primary)

- **ganges / gangesx** `path_syntax_error` — a **different** root than sample's `$140` (theirs is `$141/$145/$149` on bound-clamp `x$(not(...))=0` + parameter-assignment lines; their `.l`-init referenced vars are *declared*, so the P6 sample fix does not touch them). A separate translate-syntax diagnosis.
- **agreste** — CASE_B `stat_sales` rel 2.0 needs harness scope-verify (a single-model-solved-twice scenario driver; genuine factor-of-2 dropped-gradient vs driver artifact).

---
**Filed:** 2026-07-17 · Sprint 33 close. All six carryforwards are control-confirmed, de-risked specifications.

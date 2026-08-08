# Sprint 36 — Day 8: P4 ganges/gangesx cascade — fixes VERIFIED, rPower REPRODUCES as the deep class → BANK

**Date:** 2026-08-08 · **Branch:** `planning/sprint36-day8-p4-ganges` · **Scope:** `/tmp` control (scratch `src/` cascade prototype, **reverted** — `src/` byte-identical to `main`); no `src/` ships, no golden change.

**Outcome: BANK P4. The "surface rPower FIRST" strategy resolved P4 decisively on Day 8. The banked cascade fixes are now EMPIRICALLY VERIFIED — with `$141`/`$145` (corrected helper) + `$149` (`_diff_prod` §5 patch) applied, the ganges COLD compile drops `$141`/`$145`/`$149` to 0 and surfaces `$66` (×17: the presolve-gated calibration params unassigned in the cold MCP — the documented 4th blocker). And `rPower` REPRODUCES as the deep #1378/#1424 embedded-NLP-divergence class: the PRESOLVE MCP compiles past the cascade, then aborts at generation with `**** Exec Error at line 2216: rPower: FUNC DOMAIN: x**y, x=0, y<0` → `SOLVE ABORTED, EXECERROR = 1`. The recovery needs BOTH the cold path (`$66`) AND the presolve path (`rPower`) solved atomically for +2; `rPower` is a separate deep-bug-class dedicated effort (>> the ~16h Day 8–9 budget), and a partial landing = 0 bucket + golden churn. Per the design's REPLAN trigger, P4 banks — a STRONGER bank than the Task-6 prep, now with both terminals empirically reproduced. ganges/gangesx stay `path_syntax_error` (Solve 108); genuine floor 75.** Verifies Unknowns 4.1–4.5 (the cascade + terminals), and resolves the P4 in-sprint disposition (REPLAN → bank).

Reference: `GANGES_RECOVERY_SEQUENCING.md` (Task 6 — the cascade + REPLAN triggers), `../SPRINT_35/DAY3_P4_BANK_CARRYFORWARD.md` §5 (the `$149` patch, §5.1 the `$141`-helper correction), git `a8ff626c` (the `$141`/`$145` fixes).

---

## 1. The cascade fixes — EMPIRICALLY VERIFIED (cold path)

Applied to scratch `src/`:
- **`$141` + `$145`** from `a8ff626c` (`emit_post_assignment_na_cleanup` skips), **corrected** per DAY3 §5.1 / PR #1617: removed the divergent children()-only `_expr_contains_varref_attr` and delegated `_param_assignment_references_varref_attr` to the traversal-complete `_expr_contains_varref_attribute` (which descends into index exprs).
- **`$149`** the `_diff_prod` §5 patch (`derivative_rules.py:3410`, the `symbolic_name_match` collapse branch): rebind the collapsed prod-dummy → the original wrt index when `effective_wrt != wrt_indices`.

**Cold compile result** (`gams a=c` on the fixed cold MCP): `$NNN` codes = **`{66: 17, 256: 1, 2: 1}`** — **`$141`/`$145`/`$149` are GONE (0)**. The cascade fixes work; `$66` now surfaces (×17: "Symbol declared but no values assigned" — the calibration params `aid`/`adst`/`deltax`/… presolve-gated, so absent from the cold MCP, referenced by `stat_ax`/`stat_invtot`). This is the documented 4th blocker, now unmasked by the fixes (each root masks the next).

## 2. rPower — REPRODUCES as the deep #1378/#1424 class (presolve path, the likely REPLAN)

**Presolve compile result** (the fixed presolve MCP compiles past `$141`/`$145`/`$149`, then executes generation):
```
**** Exec Error at line 2216: rPower: FUNC DOMAIN: x**y, x=0,y<0
**** SOLVE from line 1665 ABORTED, EXECERROR = 1
```
This is exactly the characterized `rPower` (Task 6 §1 blocker 5): under `--nlp-presolve` the emitted MCP `$include`s the source, which re-executes the `.l`-based power calibrations (`as(i) = s.l(i)*(deltas(i)*k(i)**(-rhos(i)) + …)**(1/rhos(i))`, `ganges.gms:602/617/…`). Under the `$onMultiR` re-inclusion the base is `0` with a negative exponent → `x**y, x=0, y<0` → generation aborts. The standalone NLP solves fine (MS-2 @ 6395.5444) because its state order differs; the re-inclusion is non-idempotent — **the #1378/#1424 embedded-NLP-divergence bug class, confirmed empirically** (the emitter already skips *some* presolve params for exactly this at `original_symbols.py:1868`, but not the power-op calibrations).

## 3. Why BANK (the REPLAN trigger fires)

| factor | reading |
|---|---|
| Cold terminal | `$66` ×17 — needs the cold calibration-param assignment (Task 6 §3 step 3), which carries the `ac(i+2,r)` **match-correctness** risk (a Task-6 REPLAN trigger, not just compile). |
| Presolve terminal | `rPower` — the #1378/#1424 embedded-NLP-divergence deep class, **reproduced**; the design's explicit REPLAN trigger ("rPower proves as hard as the #1378/#1424 precedents → bank"). |
| Atomicity | +2 needs `$141`+`$145`+`$149`+`$66` (cold) AND `rPower` (presolve) together; **a partial landing = 0 bucket + golden churn** (Task 6 §Atomicity). |
| Budget | Task 6: a 16–22h dedicated deep effort — the `rPower` divergence investigation alone is a dedicated bug class, >> the ~16h Day 8–9 slot. |
| Sprint pattern | markov / fawley / sarf all control-first-banked; ganges is the 4th deep track. |

**⇒ BANK.** Ship nothing — the cascade fixes verified working (cold `$141`/`$145`/`$149` → 0) do NOT recover a bucket on their own (cold still `$66`, presolve still `rPower` → still `path_syntax_error`), and shipping them would churn the ganges/gangesx goldens + ~9 collateral calibration goldens for **0 bucket** (the atomicity rule's exact prohibition).

## 4. The bank (stronger than Task 6's prep bank)

The dedicated ganges/gangesx effort now inherits **empirically-verified** components:
1. **`$141`/`$145`/`$149` — VERIFIED working** (cold compile: those codes → 0). The corrected `$141` helper + the `$149` `_diff_prod` patch are ready (this control's history + `a8ff626c` + DAY3 §5).
2. **`$66` (cold) — reproduced** (×17): the calibration-param cold assignment, with the `ac(i+2,r)` match-correctness risk to resolve.
3. **`rPower` (presolve) — reproduced** as the #1378/#1424 embedded-NLP-divergence class (generation `x**y,x=0,y<0` at the `.l`-based power calibrations) — the deep gating blocker.
4. **Atomicity + full per-model protocol** (ganges AND gangesx; emit → compile → count → solve cold+presolve → bucket → match) + the nightly slow-golden regen.

## 5. KPI + Go/No-Go

**BANK — clean.** ganges/gangesx stay `path_syntax_error` → **Solve 108 / Match 93 / genuine floor 75** unchanged; DB byte-unchanged; `src/` byte-identical to `main` (the cascade prototype reverted). Zero broken code. The "surface rPower FIRST" strategy did exactly its job — P4 resolved on **Day 8** (not Day 12), with **both terminals empirically reproduced**, freeing **Day 9**.

**Sprint status:** all four deep tracks resolved (markov bank / fawley defer / sarf bank / ganges bank) — the honest projection's **fully-flat branch**: Solve 108 · Match 93 · floor 75 · Translate 135. The remaining in-sprint value: **P7 robustlp de-allowlist** (Day 10, the bounded fix from Task 9 — a WARN-clearance, not a bucket) + the P5 consultation submissions (Day 11) + the async GAMS-54 re-baseline. **turkey's +1 stays testbed-deferred.** Day 9 (freed) → bring P7 forward or stage the carryforwards.

---

**Document Status:** ✅ Complete — Sprint 36 Day 8 (P4 ganges/gangesx; cascade VERIFIED, rPower reproduced as the deep class → BANK; Solve flat 108, floor 75)
**Last Updated:** 2026-08-08 · **Owner:** Sprint 36 Execution Team

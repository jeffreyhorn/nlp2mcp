# Sprint 36 → Sprint 37 Carryforwards + Day-13 Retest Staging

**Date:** 2026-08-09 · **Branch:** `planning/sprint36-day12-carryforwards` · **Scope:** docs-only.

**Sprint 36 in one line:** the four deep tracks (markov / fawley / sarf / ganges) all resolved to **control-first banks/defers with empirically-sharpened specs** (flat KPIs — Solve 108 / Match 93 / genuine floor 75 / Translate 135), and **P7 robustlp shipped** (the NA-guard de-allowlist, the sprint's one `src/` landing). Every bank is *stronger* than its prep version because each blocker was reproduced live, not just characterized. This doc hands the sharpened banks to Sprint 37 / Epic 5 and stages the Day-13 retest.

Anchor: `78ceaead` (S34 close — the `--resolve-changed` / DB anchor; DB byte-unchanged all sprint). S36 shipped delta: `src/emit/emit_gams.py` (+37, P7) + the harness/allowlist (P7) + the pre-existing S35 turkey `original_symbols.py`.

---

## 1. Carryforwards (sharpest-first)

### 1.1 markov Part-2 `σ=sp` — the +1-floor lever (emission PROVEN; blocker = the discriminator)
- **State:** the emission is **DONE + VERIFIED** (Day 2: Mechanism C drives markov `CASE_B` rel 13.3 → `CASE_A` rel 2.8e-16, and the cold MCP solves to the reference **2401.577 + match** — the methodology→genuine +1, floor **75→76**, proven).
- **Sole blocker:** the domain-only signature gate **leaks full-corpus** (cesam/ferts/sroute) — a leak-free gate needs a **derivative-structure discriminator** that fires on the genuine param-coupled `σ=sp` (`-b·pi(s,i,σ,τ,sp)`) and excludes conditional-constant / variable-bilinear structures. **Leak-verification must be full-corpus (163 goldens), not the 6-model cohort** (which missed all three leaks).
- **Value/effort:** the sprint's **strongest local upside** (+1 floor, no testbed, tiny model); a dedicated markov-discriminator effort. Refs: `DAY2_MARKOV_OFFDIAG_CONTROL.md`, `DAY3_MARKOV_BANK.md`, `MARKOV_OFFDIAGONAL_DESIGN.md`.

### 1.2 P4 ganges/gangesx — the ≥5-blocker cascade (+2 or 0; fixes VERIFIED)
- **State:** `$141`/`$145`/`$149` **VERIFIED working** (Day 8: the corrected `$141` helper + the `$149` `_diff_prod` patch drive the cold compile's `$141`/`$145`/`$149` → 0). Both terminals **reproduced**: `$66` ×17 (cold, unassigned calibration params) + `rPower` (presolve, `x**y,x=0,y<0` at generation).
- **Sole remaining blocker:** `rPower` is the **#1378/#1424 embedded-NLP-divergence deep class** (the `.l`-based power calibrations re-run non-idempotently under the presolve `$onMultiR` `$include`); `$66` additionally carries the `ac(i+2,r)` match-correctness risk. Recovery is **atomic** (both paths for +2; a partial = 0 bucket + golden churn).
- **Value/effort:** +2 Solve/Match/floor if both paths land, else 0 (bimodal); a 16–22h dedicated deep effort. Refs: `DAY8_P4_GANGES_BANK.md`, `GANGES_RECOVERY_SEQUENCING.md`, git `a8ff626c` + the `_diff_prod` §5 patch.

### 1.3 fawley P3 — constraint-index-diagonal (0 bucket; correctness confirmed) + the `--force` +Solve
- **State:** the correctness target is confirmed (Day-9 hand-edit `stat_bq` 473→1.14e-13, reproduces on byte-identical goldens). The Day-4 implementation attempt revealed the `qsb`/`pbal` terms emit via a path **≠** the design's assumed partial-overlap branch, and the S35 orientation predicate is reverted/absent.
- **Blockers:** (a) locate the `qsb`/`pbal` emission path + rebuild the constraint-index-diagonal orientation predicate + layer the discriminator + verify **full-corpus** (0 bucket regardless — H-b); (b) the **`--force` survey is NEGATIVE** (Day 11: homotopy/multistart/optfile all leave fawley MS-5) — the +Solve needs a **stronger continuation / reformulation**, a Sprint-37 consultation, not the current scaffold. Refs: `DAY4_FAWLEY_DEFER.md`, `DAY11_P5_CONSULTATION.md` §4, `FAWLEY_DISCRIMINATOR_DESIGN.md`.

### 1.4 sarf P2 — 369K symbolic-emit re-architecture (+1 Translate; lowest-leverage)
- **State:** blow-up re-confirmed non-terminating (>100s cap; O(369,024)). No bounded control exists — the timing measurement requires the full atomic re-arch.
- **Blocker:** a **20–28h atomic re-architecture** of the `enumerate_variable_instances` → column-index → Jacobian → gradient → stationarity flow (6 call sites, 142 models), **not landable without a full-corpus regression harness first** (the byte-stable proof the symbolic-branch predicate is sarf-only). +1 Translate (never displaces a bucket track). Refs: `DAY6_SARF_BANK.md`, `SARF_DESIGN_REFRESH.md`.

### 1.5 rocket — PATH consultation (submit → reply)
- The **FINALIZED** input (`../SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`) is ready to submit to the PATH authors. **+1 Solve contingent** on a recommended option-set / continuation schedule; the reply feeds Sprint 37. Ref: `DAY11_P5_CONSULTATION.md` §1.

### 1.6 mine — primal-degenerate-LP question (consultation; 0 bucket)
- Pose the reconciliation question (`../SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md`); the only non-invariant lever is an LP-side reformulation (out of emit scope). **0 bucket.** Ref: `DAY11_P5_CONSULTATION.md` §2.

### 1.7 camcge — Epic-5 Walras gate (MS-4; per-model-numéraire fallback)
- **State (Day 11):** the Walras `/tmp` control ran (demo, 641 rows) → MS-4; a **numéraire alone is insufficient** (fixes the price-scaling ray, not the row-redundancy nullspace — the two-nullspaces diagnosis, empirically confirmed). The full three-part dual-consistent Walras redefinition (numéraire + **Walras-law dual redefinition**) is the **Epic-5 gate** (expected MS-4). **Fallback:** the per-model-numéraire declaration (`../../EPIC_5/CGE_DEGENERACY_SCOPING.md`). Ref: `DAY11_P5_CONSULTATION.md` §3.

### 1.8 turkey — >1000-row testbed solve (license-gated; +1 deferred)
- turkey's compile-recovery reaches PATH, but its 3,866-row MCP exceeds the 1000-row demo limit → **no licensed >1000-row GAMS-54 testbed exists** (local + CI both demo). The +1 Solve/Match is **deferred to a licensed cycle** (the sole external dependency). Ref: `GAMS54_TESTBED_PLAN.md` §3.

### 1.9 GAMS-54 v53→v54 re-baseline (infra; the Day-13 decision)
- The v54 re-baseline of the solving set is **demo-runnable** (the baseline is demo-built). **Decision (Day 13, §3 below):** keep the v53(51.3.0)-built KPIs (108/93/75) unless the demo re-solve shows **zero bucket regressions**. Note: P7 already restored robustlp's v54 solvability (one v53→v54 gap closed). Ref: `GAMS54_TESTBED_PLAN.md` §4.

## 2. Shipped in Sprint 36 (NOT carried)

- **P7 robustlp NA-guard de-allowlist (Day 10, landed):** `_emit_nlp_presolve` NA-guards the presolve marginal→multiplier `.L` warm-start (incl. `_fx_`); robustlp de-allowlisted, v54-solvable (`model_optimal_presolve` + match). Phase-0 gated (`docs/issues/ISSUE_1322_*.md`). Not a bucket (already counted); a robustness win. Ref: `DAY10_P7_ROBUSTLP.md`.

## 3. Day-13 retest staging

**Pre-retest state (confirmed Day 12):** DB byte-identical to `78ceaead`; KPIs recompute **Solve 108 / Match 93 (63 cold + 30 presolve) / floor 75 / Translate 135**; `src/` delta since anchor = P7 `emit_gams.py` + harness/allowlist + the S35 turkey `original_symbols.py`; **17 P7 presolve goldens + turkey** changed since the anchor.

**The Day-13 retest battery:**
1. **Determinism ×3** `{0,1,42}` — a stable-model md5 set. Suggested stable models: a P7-touched presolve golden (`robustlp`, `ps2_s`) + a cold model (`markov`) + turkey (the S35 md5 reference `fd5b1f2b…`); each emitted under `PYTHONHASHSEED ∈ {0,1,42}` must be md5-identical.
2. **`--resolve-changed --since-commit 78ceaead`** — re-solves the 17 P7 presolve goldens + turkey; **GO** iff every changed golden holds its bucket (robustlp `model_optimal_presolve` + match; turkey `path_solve_license` testbed-gated). (Confirmed GO twice during Day 10.)
3. **Golden-staleness** (`check_golden_staleness.py`) — clean (no unintended drift).
4. **DB byte-check** — `git diff 78ceaead..HEAD -- data/gamslib/gamslib_status.json` empty (0 bucket move).
5. **PR25 re-baseline** — Solve 108 / Match 93 / floor 75.
6. **GAMS-54 version decision** — keep v53 baseline (per §1.9) unless the demo re-solve shows zero bucket regressions.
7. **Closeout** — `SPRINT_LOG.md` + `SPRINT_RETROSPECTIVE.md`; `../SUMMARY.md` row 36 against the floor-75 anchor + the actual flat close + the P7 landing.

## 4. Honest close (projection realized)

The sprint landed the **projection's flat branch** (`PLAN.md` §2: "floor 75 or 76 — markov-contingent → the **75 branch**"). markov's +1 did not land (the discriminator is a dedicated effort); P4 did not land (rPower is the deep divergence class); sarf/fawley are 0-bucket/lowest-leverage. **The sprint's firm product:** one shipped robustness landing (P7), four empirically-sharpened banks (each blocker reproduced), the rocket/mine submissions, and zero broken code across 11 days — the control-first discipline that has held S30–S36.

---

**Document Status:** ✅ Complete — Sprint 36 Day 12 (Sprint-37 carryforwards + Day-13 retest staging)
**Last Updated:** 2026-08-09 · **Owner:** Sprint 36 Execution Team

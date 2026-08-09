# Sprint 36 — Sprint Log (Day 0 – Day 13)

**Theme:** Sprint-35 carryforward — the four deep emit tracks (markov / fawley / sarf / ganges) + P7 infrastructure + the P5 consultation trio.
**Anchor:** `78ceaead` (S34 close). **Close:** 2026-08-09. **Prep:** Tasks 1–10 (10 design/scoping docs + the schedule).

**Headline: FLAT (Solve 108 / Match 93 / genuine floor 75 / Translate 135) — the honest projection's 75 branch — with ONE `src/` landing (P7 robustlp) and four empirically-sharpened banks.** Every deep track resolved via control-first bank/defer with **zero broken code**; each bank's blocker was reproduced live (not just characterized), so the Sprint-37 hand-offs are far sharper than their prep versions.

---

## 1. Final KPIs (142 convex candidates)

| KPI | Day-0 (S35 close) | S36 close | Δ |
|---|---|---|---|
| Solve | 108 | **108** | 0 |
| Match | 93 (63 cold + 30 presolve) | **93** (63 + 30) | 0 |
| genuine floor | 75 | **75** | 0 |
| Translate | 135 | **135** | 0 |
| model_infeasible / path_syntax_error | 7 / 7 | **7 / 7** | 0 |
| all-219 Match | 96 | **96** | 0 |

**DB byte-unchanged since the anchor** (0 bucket move). The one `src/` landing (P7 robustlp) is a v54-robustness / de-allowlist win, not a bucket (robustlp was already `model_optimal_presolve` + match in the v53 DB).

## 2. Day-by-day

| Day | Track | Outcome |
|---|---|---|
| 0 | Kickoff | GO — baseline + all fingerprints re-confirmed; robustlp `(NA)*v` traced to the same NA `.L` root (sharpened Task 9). |
| 1 | P1 markov Phase-0 control | PASS — the `CASE_A` cold emit → cold match **2401.577** (the +1 payoff proven; reconciliation (a) confirmed). |
| 2 | P1 markov Mechanism C control | REPLAN — emission reaches `CASE_A` + cold-match in `src/`, but the domain-only gate **leaks full-corpus** (cesam/ferts/sroute). |
| 3 | P1 markov disposition | BANK — the discriminator is a dedicated effort (3 structurally-distinct leaks); floor flat 75. |
| 4 | P3 fawley control | DEFER — correctness confirmed (`stat_bq` 473→1.14e-13), but the `qsb`/`pbal` emission path ≠ the design's branch; 0 bucket (H-b). |
| 5 | Checkpoint 1 | GO — no regression; both front-loaded tracks resolved with 0 `src/`; budget → P2/P4. |
| 6 | P2 sarf | BANK — blow-up re-confirmed non-terminating; the 20–28h atomic re-arch has no bounded control; +1 Translate lowest-leverage. |
| 8 | P4 ganges/gangesx | BANK — `$141`/`$145`/`$149` **VERIFIED working** (cold cascade → 0); `rPower` reproduced as the #1378/#1424 deep class; +2 or 0, banked. |
| 10 | Checkpoint 2 + **P7 robustlp** | **LANDED** — NA-guard the presolve multiplier `.L` warm-start (incl `_fx_`); EXECERROR-84 gone; robustlp de-allowlisted, v54-solvable; Phase-0 gated. |
| 11 | P5 consultation | 0 `src/` — rocket/mine submit-ready; camcge Walras `/tmp` → MS-4 (numéraire-alone insufficient); fawley `--force` survey NEGATIVE → all Sprint 37. |
| 12 | Carryforwards | `SPRINT_37_CARRYFORWARDS.md` (sharpest-first) + Day-13 retest staging. |
| 13 | Final retest + close | GO on all gates (§3). |

(Days 7 and 9 folded — sarf banked Day 6 freed budget, P4 resolved Day 8.)

## 3. Day-13 retest — GO on every gate

| gate | result |
|---|---|
| Determinism ×3 `{0,1,42}` | ✓ markov (`d5184334…`) · robustlp (`a7f10b3e…`) · ps2_s (`70c5b183…`) md5-identical |
| `--resolve-changed --since-commit 78ceaead` | **GO** — all 18 changed goldens held their bucket (robustlp `model_optimal_presolve` + match `= same`; turkey `path_solve_license` testbed-gated) |
| Golden-staleness (163 goldens) | **all clean** (0 drift) |
| DB byte-check | `git diff 78ceaead..HEAD -- gamslib_status.json` empty (0 bucket move) |
| PR25 re-baseline | Solve 108 / Match 93 (63+30) / floor 75 / mi 7 / pse 7 / all-219 96 |

## 4. GAMS-54 v53→v54 version decision

**KEEP the v53(51.3.0)-built KPIs (108/93/75) as the canonical baseline.** No full 142-model v54 re-baseline showing *zero* bucket regressions was completed this sprint (only P7 restored robustlp's v54 solvability + `--resolve-changed` confirmed the 18 *changed* goldens hold under v54). The full demo v54 re-baseline of the 142 candidates is carried to Sprint 37 (`SPRINT_37_CARRYFORWARDS.md` §1.9); re-pin to v54 only on confirmed zero regressions. (`GAMS54_TESTBED_PLAN.md` §4.)

## 5. Shipped `src/`

- **P7 robustlp NA-guard de-allowlist** (`src/emit/emit_gams.py` `_emit_nlp_presolve` + `scripts/diagnostics/kkt_residual.py` + the allowlist + 17 presolve goldens): NA-guard the presolve marginal→multiplier `.L` warm-start (eq/ineq/bound + `_fx_`) with the #1322 idiom; clears the GAMS-54 EXECERROR-84; robustlp de-allowlisted, `model_optimal_presolve` + match under v54. Phase-0 gated (`docs/issues/ISSUE_1322_na-multiplier-level-warmstart-guard.md`). A no-op for finite marginals (byte-additive goldens). **Not a bucket** (already counted). Ref: `DAY10_P7_ROBUSTLP.md`.

The four deep tracks shipped **0 `src/`** (all banked/deferred). `src/kkt/stationarity.py` and `src/ad/derivative_rules.py` byte-identical to the anchor all sprint.

## 6. Carryforwards → Sprint 37

`SPRINT_37_CARRYFORWARDS.md` (sharpest-first): markov Part-2 (emission PROVEN; blocker = the derivative-structure discriminator, full-corpus) — the +1-floor lever · P4 ganges (fixes VERIFIED; rPower deep class + $66) — +2 or 0 · fawley (emission-path relocate + `--force` NEGATIVE) — 0 bucket · sarf (20–28h atomic re-arch) — +1 Translate · rocket/mine (consultation) · camcge (Epic-5 Walras) · turkey (testbed-gated +1) · GAMS-54 v53→v54 re-baseline.

---

**Document Status:** ✅ Complete — Sprint 36 close (FLAT 108/93/75/135; P7 landed; four sharpened banks; retest GO ×all).
**Last Updated:** 2026-08-09 · **Owner:** Sprint 36 Execution Team

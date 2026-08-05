# Sprint 35 — Sprint Log

**Theme:** Quality, performance & PATH-feedback integration (Epic-4 SUMMARY row 35). **Anchor:** S34 close `78ceaead`. **Close:** Day 13 (this PR). **Mode:** **bimodal-FLAT** (P4 banked Day 3 — the projection's flat branch).

## Final KPIs (142 convex-candidate corpus)

| KPI | S34 close | **S35 close** | projection (flat / upside) |
|---|---|---|---|
| Translate | 135 | **135** | 135 / 135 |
| Solve | 108 | **108** | 108 / 110 |
| Match | 93 | **93** | 93 / 95 |
| genuine floor | 75 | **75** | 75 / 77 |
| path_syntax_error | 7 | **7** | 7 / 5 |
| model_infeasible | 7 | **7** | — |
| all-219 Match | 96 | **96** | — |

**Landed the flat branch on every axis; `≥ 112` a-priori refuted (not reached).** Match 93 = **63 cold-optimal genuine + 30 presolve-match candidates** → **genuine floor 75** (DB byte-identical to the anchor ⇒ the S34 hand-partition carries forward verbatim). **The floor did not move** (no cold match landed — the cold-match-contingent upside did not realize).

## Close-gate results (Day 13)

- **DB integrity:** `git diff 78ceaead..HEAD -- data/gamslib/gamslib_status.json` **empty** → **0 bucket move** all sprint.
- **Determinism ×3** (`PYTHONHASHSEED ∈ {0,1,42}`): turkey (the sprint's one changed golden) re-emit **✅ md5 `fd5b1f2b73bd265a70287a3d02de198d` byte-identical across all three seeds — and matches the committed golden** (golden-staleness clean). Emit-level, seed-invariant; the rest of the corpus is byte-unchanged from the S34 close (which was ✅×3).
- **`--resolve-changed --since-commit 78ceaead`:** at-risk set = **{turkey}** (only changed golden); **GO — `path_syntax_error → path_solve_license ~ shift`, bucket held** (both non-bucket; the compile-recovery is real — turkey now reaches PATH, blocked only by the 1000-row demo limit).
- **Golden-staleness:** clean by construction (no `src/` change on the close branch; the one drifted golden, turkey, was regenerated + validated with PR #1620).

## Per-day ledger

| Day | PR | Track | Outcome |
|---|---|---|---|
| 0 | #1616 | Kickoff | LIVE fingerprint re-confirm (P4 `$141`×15/`$145`×3/`$149`×9; mine CASE_B; fawley CASE_B H-b). No Day-0 blocker. |
| 1 | in #1617 | P4 | `$141`+`$145` NA-cleanup skips — later banked. |
| 2 | #1618 | P4 | `$149` `/tmp` control PROCEED — `_diff_prod` cross-index prod-dummy rebind; verified surgical (ganges `$149` 9→0; lmp2/camcge byte-identical). |
| 3 | #1617 (BANK) | P4 | **ganges/gangesx = ≥5-blocker cascade** (`$141`/`$145`/`$149` fixed → `$66` cold → `rPower` presolve). No bucket → **all `src/` banked** (reverted). |
| 5 | #1619 | Checkpoint 1 | GO, zero regression; tally == Day-0 baseline. P4 REPLAN freed budget → P6/P7. |
| 6 | #1620 | P6 | **turkey `$161` COMPILE-recovery** (domain-less 2-D-set arity inference, gated `not set_def.domain`) — the sprint's one `src/` landing (testbed-gated solve). **GAMS 53→54.2.1** license-expiry cascade fixed (local 22→0; CI workflows bumped). |
| 7 | #1621 | P6 | turkpow/clearlak **DEFER** (heavily multi-root: ragged-Table parse bug / uninitialized dynamic sets). P6 fully triaged. |
| 8 | #1622 | P5 | camcge **Epic-5-deferred** (MS-4 Walras rank-deficiency @ omega 191.7346). **Sprint-36 consultation bundle** assembled (rocket + mine + fawley). |
| 9 | #1623 | P3 | fawley `/tmp` control **VERIFIED** (`max\|stat_bq\|` 473.4→1.14e-13) but the general `src/` predicate **leaks onto markov #1110** → **DEFER**. Surfaced Follow-up 3 (markov `slow` test). |
| 10 | #1624 | P7 + Checkpoint 2 | **GO.** `--resolve-changed` = {turkey}, `path_syntax_error → path_solve_license` (compile-recovery real, testbed-gated). No net-new fixture (turkey covered). SUMMARY row 35 provisional. |
| 11 | #1625 | slack | **markov `stat_z` diagonal-Kronecker bug = a +1-floor lever** (methodology→genuine; `CASE_B` rel 13.3). Leak-gated landing **attempted & reverted**: diagonal split works (13.3→1.55), off-diagonal `σ=sp` enumeration is a 2nd, deeper bug. Banked (2-part Sprint-36 spec). |
| 12 | #1626 | carryforwards | `SPRINT_36_CARRYFORWARDS.md` + `DAY13_RETEST_STAGING.md`. |
| 13 | this PR | close | Final retest + `SPRINT_LOG`/`SPRINT_RETROSPECTIVE`; SUMMARY row 35 finalized. |

## Dispositions (5 deep tracks + P6/P7)

- **P1 mine** — REPLAN'd in prep (primal-degenerate-LP; value-invariant) → Sprint-36 consultation.
- **P2 sarf** — REPLAN'd (369K-column re-architecture) → dedicated symbolic-emit effort.
- **P3 fawley** — control-VERIFIED, `src/` DEFER (leaks onto markov) → dedicated effort + `--force` survey.
- **P4 ganges/gangesx** — BANKED (≥5-blocker cascade); the `$149` fix verified+banked → Sprint-36 recovery bundle.
- **P5 camcge / rocket** — camcge → Epic 5; rocket → Sprint-36 PATH consultation.
- **P6** — turkey recovered (compile, testbed-gated +1); turkpow/clearlak/dinam/indus deferred (multi-root).
- **P7** — no net-new fixture (turkey's landing carries its 3 unit tests).
- **NEW (Day 11): markov** — a fully-diagnosed +1-floor lever, half-de-risked, banked to Sprint 36.

## GAMS version axis (v53 → v54)

The 108/93/75 baseline + the committed DB were built under **GAMS 53**; CI + local now validate under **54.2.1** (the Day-6 license-expiry cascade). Per `DAY13_RETEST_STAGING.md` §3: the local determinism / `--resolve-changed` / golden-staleness gates are **emit-level (version-independent)** and stay valid; only solve buckets carry v53→v54 risk, and the demo license can't solve the >1000-row models regardless. **Decision: report the v53-built KPIs as the S35 baseline (unchanged), and open the v54 corpus re-baseline as the first Sprint-36 infra task** (`FOLLOWUPS_GAMS54_TRANSITION.md`). 5 OBJ-GAP models (agreste/cesam/chain/fawley/rocket) flagged for that re-baseline.

---

**Document Status:** ✅ Sprint 35 closed (Day 13)
**Last Updated:** 2026-08-04
**Owner:** Sprint 35 Execution Team

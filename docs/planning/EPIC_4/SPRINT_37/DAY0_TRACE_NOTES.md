# Sprint 37 Day 0 — Kickoff, Baseline Re-Confirm, GO/NO-GO

**Date:** 2026-08-11 · **Branch:** `planning/sprint37-day0-kickoff` · **Scope:** docs/trace-only — measurements under GAMS 54.2.1; **no `src/` change, DB untouched.**

**Verdict: ✅ GO for Day 1.** The baseline recomputes exactly, all four banked fingerprints reproduce live, and all four GO/NO-GO conditions hold. **One Day-0 deliverable is NOT done and cannot be done by the execution agent: the consultation send** (§5) — it needs a human, and the bundle does not say to whom.

---

## 1. Day-0 baseline — CONFIRMED exactly (142 convex candidates)

| KPI | measured | expected (S36 close) | |
|---|---|---|---|
| convex candidates | 142 | 142 | ✅ |
| Parse | 142 | 142 | ✅ |
| Translate | 135 | 135 | ✅ |
| **Solve** | **108** | 108 | ✅ |
| **Match** | **93** = 63 cold + 30 presolve | 93 = 63 + 30 | ✅ |
| model_infeasible | 7 | 7 | ✅ |
| path_syntax_error | 7 | 7 | ✅ |
| all-219 Match | 96 | 96 | ✅ |

**markov ∈ the 30-model presolve-match (methodology) partition** — `outcome_category = model_optimal_presolve`, `comparison_status = match`, `convexity = verified_convex`, objective **2401.5773**. So the P1 lever is a **true +1 genuine floor** and a partition transfer (presolve-match 30→29, cold-optimal 63→64) with **Match unchanged at 93**.

**Genuine-floor anchor: 75.**

### Code/DB integrity vs the anchor `78ceaead`

```
git diff --stat 78ceaead..HEAD -- src/
  src/emit/emit_gams.py        | 37 ++++++   (S36 P7 robustlp NA-guard)
  src/emit/original_symbols.py | 52 ++++++   (S35 turkey $161)
```

- `src/kkt/stationarity.py` and `src/ad/derivative_rules.py` — **byte-identical to the anchor** (empty diff) ⇒ every banked emit fingerprint reproduces deductively, and both S37 emit tracks start from the state their diagnoses were measured against.
- `data/gamslib/gamslib_status.json` — **byte-unchanged** since the anchor.

**A measurement-method note (Day-0 self-correction).** The first KPI recompute returned Solve 0 / Match 0 because it read `mcp_solve.outcome` and `solution_match.status`; the DB's actual keys are **`mcp_solve.outcome_category`** and **`solution_comparison.comparison_status`**. Parse/Translate were right, which is exactly what made the error look like a catastrophic regression rather than a bad field name. Recorded because the same two keys drive every checkpoint recompute this sprint (Days 5, 10, 13) — read them from this note, not from memory.

## 2. Banked fingerprints — all four reproduce live

| # | model | expected (banked) | **measured today** | |
|---|---|---|---|---|
| 1 | **markov** | `CASE_B`, `stat_z` rel ≈ 13.3, dual CONSISTENT | `CASE_B`; max `stat_z(empty,disrupted,empty)` rel **1.33e+01** (raw −4.79e+04); dual **CONSISTENT** (comp infeas 0.00e+00, equality resid 5.97e-16); dual scale 3.6e+03 | ✅ |
| 2 | **fawley** | `CASE_B`, `stat_bq` rel ≈ 0.973, max = `stat_trans(tr-2)` rel 1.00 | `CASE_B`; max **`stat_trans(tr-2)` rel 1.00e+00** (raw −4.88e+02); **`stat_bq(res-arab-l,fuel-oil)` rel 9.73e-01** + siblings; dual CONSISTENT | ✅ |
| 3 | **ganges** | cascade surfaces intact, `a8ff626c` reachable | `a8ff626c` reachable; `_expr_contains_varref_attribute` (`$141` helper) present; `_diff_prod` at `derivative_rules.py:3276` | ✅ |
| 4 | **sarf** | non-terminating at cap (>330 s) | **non-terminating at a 200 s cap** — no completion, matching the banked behaviour in kind | ✅ |

markov's `CASE_B` → `CASE_A` transition is the Day-1/Day-2 gate; fawley's max row staying the **emit-correct** `stat_trans(tr-2)` re-confirms the H-b finding (the P4 fix cannot move a bucket, by construction).

## 3. GO/NO-GO gate — all four conditions hold

| # | condition | evidence |
|---|---|---|
| a | baseline re-confirmed | §1 — every KPI exact; DB + emit tree byte-identical to `78ceaead` |
| b | `make leak-check` working on `main` | target present (`--expect-drift "$(MODEL)"`); mechanism exercised scoped: correct **`NO-OP`** verdict on a clean tree *and* the **SUBSET warning** ("`--models` restricted this sweep to 1 golden … cannot support a full-corpus leak claim"). Both anti-false-confidence paths fire. |
| c | `ISSUE_1110` + `ISSUE_1111` conforming | both: 8 `###` subsections, **all 4 canonical present**, `Traced Fix-Surface (Day-0)` line present |
| d | zero INCOMPLETE unknowns | ✅ 20 · 🔶 4 · ❌ 3 · **🔍 0** |

**⇒ GO for Day 1** (P1 markov discriminator control, `/tmp` only).

## 4. Gate infrastructure landed since the schedule was written

Two P7 items the Day-9 slot budgeted for are **already on `main`**, and one is now blocking:

- `golden-staleness` no longer uses an `on.pull_request.paths:` filter — it runs on every PR and decides internally, so it **always reports a conclusion**. It is now a **required status check** (`required_status_checks.contexts`), with `enforce_admins: true` ⇒ **a red PR can no longer merge.**
- `--min-scope 170` + `--all` corpus provisioning: CI was checking **148 of 170** goldens and reporting PASS, because `discover_goldens()` silently drops any golden whose raw source is absent and the download defaulted to `convex` mode (135 models). Now measured in CI: **`Provisioned 219 raw model(s)` → `checked 163 in-scope golden(s) (7 allowlisted)`** — CI finally matches the local sweep.

**Why it mattered for *this* sprint:** the 18 previously-unswept goldens include **`iobalance`** (the model whose single-index value coincidence refuted the second markov discriminator design — the reason the predicate carries its distinct-position clause), **`orani`** (in the 15-model false-positive set of the naive derivative-only predicate), and **`ps2_f_s` / `ps2_s` / `ps3_s_gic`** (three of the six S36 2-D cohort members). A Day-2 markov predicate regressing onto exactly those would have passed CI green. The eight leak-associated models (markov, fawley, cesam, ferts, sroute, dinam, prolog, shale) were all inside the 135, so **no prior result is invalidated**.

**Day-9 impact:** its P7 scope shrinks to the Phase-0-doc CI check + CONTRIBUTING rewording + floor tracking; the leak-harness wiring is done.

**Still unverified:** CI has exercised the *RUN* path (this branch's predecessor swept 163 green) but **not yet the SKIP path** (a docs-only PR reporting green in seconds). That logic was validated by local replay against PR #1661's real file list, not by a live run. This Day-0 PR is docs-only, so it is the first live exercise of that path — under a now-required gate.

## 5. ⚠ The consultation send — NOT DONE (needs the owner)

**Day 0's second deliverable is not something the execution agent can perform.** Transmitting the package to the PATH authors is an outbound human communication; it has not been done and **the checkbox in `SPRINT_36/CONSULTATION_BUNDLE.md:46` is deliberately left unticked.** Ticking it would make the record claim a send that did not happen — the precise failure that let this slip four sprints while every *preparation* box sat ticked above it.

**A Day-0 finding that explains the slippage mechanically:** the bundle specifies **no recipient, no address, and no channel.** A repo-wide grep for `ferris|dirkse|@cs.wisc|@gams.com|mailto|email` across the bundle and the finalized input returns **nothing**. So "submit rocket to PATH authors" was never an executable instruction — it named an outcome with no addressee, on the day of the sprint most likely to be compressed. That is a better explanation of four sprints of slippage than inattention, and it is fixable in one line.

**Everything else is ready** — the send is copy-paste once a channel is chosen:

| item | state | source |
|---|---|---|
| rocket question | **FINALIZED 2026-07-15**, §3 of the input; §2 carries the ruled-out-lever survey so the authors are not asked about levers already exhausted | `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` (99 lines) |
| mine question | specified (primal-degenerate LP; value-invariance proof) — **0 bucket either way**, so it costs nothing to batch | `SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md` |
| bundling rationale | written | `SPRINT_36/CONSULTATION_BUNDLE.md` §"Why bundle these three" |

**Owner action (~30 min):** pick the channel (the PATH maintainers directly, or the GAMS support/forum route), send the two questions, then tick `CONSULTATION_BUNDLE.md:46` **and record the date and channel in it** so the next sprint can tell "sent" from "ready to send" — the distinction this whole track lost.

**KPI consequence:** rocket's +1 Solve stays contingent on the send *and then* a reply. It is **not** in the Sprint-37 projection, and P3's realized cost drops to the ~3 h camcge control on Day 10 (Task 9 measured P3 down from its 12–16 h budget for exactly this reason).

## 6. Day-1 readiness

Day 1 is the **P1 markov discriminator control, `/tmp` only** — no `src/`. Preconditions confirmed today: the markov `CASE_B` fingerprint is live (§2), `ISSUE_1110` carries a conforming Phase-0 gate with a traced fix surface (§3c), the target emit form is specified, and the leak instrument works (§3b). The Day-1 REPLAN exit is unchanged: **the predicate fires on any model besides markov ⇒ do not proceed to `src/`.**

---

**Document Status:** ✅ Complete — Sprint 37 Day 0 (GO for Day 1; the consultation send is outstanding and owner-assigned).
**Last Updated:** 2026-08-11 · **Owner:** Sprint 37 execution team

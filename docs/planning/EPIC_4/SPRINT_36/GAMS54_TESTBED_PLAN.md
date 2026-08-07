# Sprint 36 — GAMS-54 Licensed-Testbed Re-Baseline Harness Plan (Prep Task 7)

**Date:** 2026-08-07 · **Owner:** Sprint 36 execution team · **Branch:** `planning/sprint36-task7` · **Scope:** docs/analysis-only (license + infra probes; no `src/` change).

**Outcome: a Day-0 risk surfaced and bounded. There is NO licensed >1000-row GAMS-54 testbed — the local install AND both CI workflows are GAMS *demo* (1000-row solve limit). BUT the impact is narrow: the entire Solve/Match baseline was built under a demo license (DB `gams_version` 51.3.0), so every *currently-solving* model is demo-solvable, and the v54 corpus re-baseline of that set is fully demo-runnable (local + CI). Only turkey's +1 (3,866-row MCP) is genuinely license-gated. The v53→v54 baseline decision is therefore makeable in-sprint on the demo; turkey's solve is the sole external dependency, deferred until a license is procured.** Verifies Unknowns 6.1, 6.2, 7.1, 7.2.

Reference: `../SPRINT_35/FOLLOWUPS_GAMS54_TRANSITION.md` (the v53→v54 transition + the 5 OBJ-GAPs), `../SPRINT_35/DAY6_*` (turkey `$161` compile-recovery + the >1000-row testbed note). Infra: `.github/workflows/pr19-emit-solve-validation.yml`, `.github/workflows/presolve-divergence.yml`; `scripts/gamslib/run_full_test.py` (`--resolve-changed --since-commit <SHA>`).

---

## 1. Testbed access — the Day-0 risk (Unknown 6.1)

**Probed both environments on current `main`:**

| environment | GAMS | license | solve limit |
|---|---|---|---|
| **local** (`Versions/54/Resources/gams`) | 54.2.1 (`GAMSX … Jul 13, 2026`) | `gamslice.txt` = **`GAMS Demo`** (time-limited, stops Nov 26 2026) | **1000 rows/cols** |
| **CI** `pr19-emit-solve-validation.yml` | 54.2.1 (`linux_x64_64_sfx.exe`) | step **"Install GAMS demo"** | **1000 rows/cols** |
| **CI** `presolve-divergence.yml` | 54.2.1 (same installer) | step **"Install GAMS demo"** | **1000 rows/cols** |

**Finding: there is no licensed >1000-row GAMS-54 testbed anywhere in the current infrastructure.** Unknown 6.1's assumption ("a licensed >1000-row testbed is available") is **wrong** — this is a Day-0 risk.

**Why the impact is bounded (the load-bearing insight):** the Solve 108 / Match 93 baseline in `gamslib_status.json` was itself built under a **demo** license (`gams_version` = `51.3.0`, demo). A model can only contribute to the Solve/Match count if it *solved* on the demo → **every currently-solving model is ≤ the 1000-row limit.** turkey is `path_syntax_error` (not in the 108) — it is the *upside*, not the baseline. So:
- the **v54 re-baseline of the solving set is demo-runnable** (local + CI) — no license needed;
- only **turkey's +1** (and any future >1000-row recovery) needs a license.

**Contingency (no license procured this sprint):** run the v54 re-baseline on the demo for the solving set (covers the whole KPI corpus); keep the v53(51.3.0)-built KPIs as the S36 baseline; **defer turkey's solve** to a licensed cycle. This is the expected path — turkey was already a "pending v54 testbed" carryforward from S35 Day 6.

## 2. Re-baseline diff scope (what the v54 re-solve compares)

Run `run_full_test.py --resolve-changed --since-commit <S36-anchor>` (GO/NO-GO, never persists) — or a full `run_full_test.py` re-solve into a scratch DB — under the **demo v54** and diff buckets against the v53(51.3.0) DB:

1. **The 142 convex candidates** — re-solve, diff `outcome_category` (Solve bucket) + `comparison_status` (Match bucket) vs the DB. All are demo-solvable (§1), so this is complete on the demo.
2. **The 5 OBJ-GAP models** `agreste / cesam / chain / fawley / rocket` (Unknown 7.1) — the S35 v54 transition flagged an objective gap on these; all are tiny (agreste 14 eqns … cesam 21 eqns) and all produced a v54 demo result (4 `model_infeasible`, chain `model_optimal_presolve`), so the re-check is demo-runnable. Question: does the objective gap flip a *bucket* (Solve or Match), or is it a benign within-tolerance objective difference?
3. **The PR19 Tier-0/1 canaries** — the emit-solve-validation gate's pinned models; confirm they still solve+match under v54 demo (they already run in `pr19-emit-solve-validation.yml`, so this is CI-covered).

## 3. turkey's >1000-row solve (Unknown 6.2)

- turkey's compile-recovery is **real and landed** (S35 Day 6, PR #1620: the domain-less 2-D set `ao` arity-inference fix). The emitted MCP is `data/gamslib/mcp/turkey_mcp.gms` (852 golden lines → **3,866 generated rows** when GAMS instantiates the domains).
- 3,866 rows **> the 1000-row demo limit** → GAMS rejects the model at generation on the demo; turkey **cannot be solved locally or in demo-CI.**
- **Invocation once a license exists:** on a licensed >1000-row GAMS-54 machine, `run_full_test.py` (single-model) emit+solve turkey → assert `modelstat` (per the "always assert modelstat before reading an objective" discipline) → if optimal, the KKT-residual/match check → update the DB entry → determinism ×3 `{0,1,42}`.
- **Status: BLOCKED (license-gated), deferred.** The compile-recovery reaches PATH (`$161` cleared); the solve is untestable on the demo. turkey's potential +1 is carried to a licensed testbed cycle — the sole external dependency in the plan.

## 4. DB-version decision (Unknown 7.2)

**Decision: keep the v53(51.3.0)-built KPIs as the S36 baseline; do NOT re-pin the DB to v54 mid-sprint. Open the v54 re-baseline as an infra task; pin to v54 only if the demo re-solve confirms bucket stability.**

Criteria / artifact:
- **Keep v53 baseline (recommended default):** report Solve 108 / Match 93 / floor 75 unchanged; the v54 re-solve (§2) is a *verification* run producing a bucket-diff artifact, not a DB overwrite. Rationale: the KPI history + all sprint anchors (`--resolve-changed --since 78ceaead`) are v53-referenced; re-pinning mid-sprint would break the anchor chain and conflate a version change with sprint work.
- **Re-pin to v54 (only if):** the §2 demo re-solve shows **zero bucket regressions** across the 142 candidates (OBJ-GAPs benign, no Solve/Match losses) AND the team decides v54 is the canonical baseline for S37+. If any bucket regresses, file it (allowlist / follow-up) and stay on v53.
- **Artifact:** a `GAMS54_REBASELINE_DIFF.md` (produced at the async Day-slot) — the per-model v53→v54 bucket diff + the OBJ-GAP dispositions + the re-pin recommendation. This is the decision record `../SPRINT_35/FOLLOWUPS_GAMS54_TRANSITION.md` calls for at the Day-13 retest.

## 5. Local vs testbed checklist

| gate / step | runs where | version-dependent? |
|---|---|---|
| emit determinism ×3 `{0,1,42}` | **local / CI** | no (emit is solver-independent) |
| golden-staleness scan | **local / CI** | no |
| `--resolve-changed` GO/NO-GO (emit goldens) | **local / CI** | no |
| `make test` / typecheck / lint / format | **local / CI** | no |
| PR19 Tier-0/1 emit-solve canaries (≤1000 rows) | **demo CI** | yes (solve) — demo-OK |
| v54 re-baseline of the 142 candidates | **demo** (local or CI) | yes (solve) — demo-OK (§1) |
| 5 OBJ-GAP bucket re-check | **demo** | yes (solve) — demo-OK |
| **turkey 3,866-row solve** | **licensed testbed** | yes (solve) — **needs a license** |
| any future >1000-row recovery (ganges 852-line MCP, etc.) | **licensed testbed** | yes (solve) — needs a license |

**Rule of thumb: everything emit-level is local/version-independent; everything solve-level is demo-runnable *except* >1000-row models (turkey), which need a license.**

## 6. Async Day-slot (feeds Day-10 / Day-13)

- **The v54 re-baseline (§2) + OBJ-GAP re-check (§2.2) + the diff artifact (§4):** a **demo** run — no external dependency — scheduled as an **async slot before Day-10** (the Checkpoint-2 / carryforward window), so the bucket-stability answer + the re-pin recommendation are in hand for the **Day-13 retest** (the GAMS-version-axis decision the S35 close deferred).
- **turkey's solve (§3):** gated on license procurement — **not** on the sprint calendar. If a license lands mid-sprint, slot the single-model solve+determinism into the same async window; otherwise carry turkey's +1 forward (unchanged from S35).

## 7. Go / No-Go

**GO with a bounded Day-0 risk.** No licensed >1000-row testbed exists (6.1 wrong) — but the KPI baseline is demo-built, so the v54 re-baseline + OBJ-GAP re-check + the version decision are all **demo-runnable in-sprint** (7.1/7.2 resolved on the demo). Only turkey's +1 is license-gated (6.2 blocked, deferred — a pre-existing S35 carryforward, not a new blocker). The plan needs **no new infrastructure** to execute the KPI-relevant work; the license is required only to *bank the turkey upside*, which the honest projection already treats as contingent.

**REPLAN triggers:** the §2 demo re-solve shows bucket regressions under v54 (→ stay v53, file follow-ups) — or a license *is* procured (→ add turkey's solve to the async slot, re-open the +1).

---

**Document Status:** ✅ Complete — Sprint 36 Prep Task 7 (GAMS-54 testbed harness plan; GO, bounded Day-0 risk)
**Last Updated:** 2026-08-07
**Owner:** Sprint 36 Execution Team

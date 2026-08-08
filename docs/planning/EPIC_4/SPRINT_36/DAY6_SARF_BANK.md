# Sprint 36 — Day 6: sarf P2 symbolic-emit re-architecture — baseline re-confirmed → BANK (atomic 20–28h dedicated effort)

**Date:** 2026-08-08 · **Branch:** `planning/sprint36-day6-sarf-symbolic` · **Scope:** docs-only (baseline re-measurement, measurement-only; no `src/`, no golden change).

**Outcome: BANK sarf P2. The blow-up baseline re-confirms (sarf emit still non-terminating at a 100s cap — the O(369,024)-column failure; the S1/S2/S3 sites byte-unchanged since the anchor). But the "PR27 timing control" the day calls for CANNOT be a bounded Day-6 prototype: measuring whether the O(active) emit completes requires BUILDING the O(active) emit, which is the full atomic 20–28h re-architecture across 6 call sites — "a partial landing = an inconsistent MCP" (no safe partial). For the lowest-leverage bucket (+1 Translate), on the 4×-failed Sprint-26 path, that the design says is "not landable without the full-corpus regression harness" and whose most-likely outcome is a REPLAN — and which must not displace P4 (the sprint's only remaining bucket lever) — this is exactly the design's disposition: a dedicated effort, banked. The freed Days-6–7 budget → P4 ganges (Days 7–9), giving the bimodal bucket gate more room. Translate stays 135 (sarf stays translate_failure).** Verifies Unknowns 2.1 (baseline), 2.2/2.3/2.4 (design applies unchanged — Task 5).

Reference: `SARF_DESIGN_REFRESH.md` (Task 5 — the O(active) refresh + the REPLAN triggers), `../SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md` (the 3-site + 6-call-site + 7-term design), `../SPRINT_35/PHASE_0_ACCEPTANCE_GATES.md` (the O(active) timing gate), `PLAN.md` §3 (P2 never displaces a bucket track).

---

## 1. Baseline re-confirmed (Unknown 2.1)

- **Blow-up:** a bounded re-measurement — `python -m src.cli data/gamslib/raw/sarf.gms` under a **100s cap** — is **still running at the cap (non-terminating)**, vs the srpchase ~2.9s single-digit-second reference for a healthy emit. The O(369,024)-column failure reproduces (`task(g,t,mn,mn)` = 16·24·31·31 = 369,024 declared; ~398 active).
- **Code-surface integrity:** the 3 sites — `src/ad/constraint_jacobian.py` (S1), `src/ad/index_mapping.py` (S2, `enumerate_variable_instances`), `src/kkt/stationarity.py` (S3) — are all **byte-identical to the anchor `78ceaead`**. So the blow-up + the O(active) design apply exactly as Task 5 measured (2026-08-07). No refresh needed.

## 2. Why there is no bounded Day-6 "timing control"

The day's PR27 gate is: "confirm the O(369K) → O(active) reduction prototypes under the cap." But — unlike markov/fawley, where a hand-edited `/tmp` MCP gave a bounded control before any `src/` — **there is no bounded sarf prototype:**
- The O(active) emit is produced by the **S1/S2/S3 short-circuit + the parametric `stat_task` + `task.fx`** landing in **one atomic change** (Task 5 §4; the S35 design §4). **A partial landing = an inconsistent MCP** (multipliers with no stationarity coupling) — it would not even instantiate, let alone time.
- So the only way to *measure* whether the re-arch completes under the cap is to **do the full 20–28h re-architecture** (6 call sites, 142 models). There is no cheaper timing signal.
- The one bounded measurement that DOES exist — the baseline (§1) — is confirmed non-terminating.

## 3. The disposition (the design's own honest call)

Per `SARF_DESIGN_REFRESH.md` §5 (GO to carry the design, disposition unchanged):
- **20–28h atomic, foundational re-architecture** of the `enumerate_variable_instances` → column-index → Jacobian → gradient → stationarity flow — the sprint's **largest single track**, >> the Day 6–7 (~18h) budget.
- **Lowest-leverage bucket: +1 Translate** (not a Solve/Match/floor mover).
- **The 4×-failed Sprint-26 path**, "no safe partial."
- **"Not landable without the full-corpus regression harness"** (the byte-stable proof that the symbolic-branch predicate is sarf-only — a prerequisite that itself is dedicated-effort work).
- **REPLAN is "its most likely outcome"** (§5) — the design says to schedule it so that surfaces early.
- **`PLAN.md` §3: P2 must not displace a bucket track** — P4 ganges (Days 8–9) is the sprint's only remaining bucket lever.

**⇒ BANK.** Attempting a 20–28h atomic re-arch (with an inconsistent-MCP partial-failure mode, no full-corpus harness yet, for +1 Translate) inside a ~18h slot — right after markov/fawley both control-first-banked — would either ship a broken partial or overrun the budget and starve P4. The disciplined outcome, which the design pre-concludes, is to carry sarf to a **dedicated effort**.

## 4. Freed-budget reallocation

Banking sarf on Day 6 frees the Days-6–7 budget:
- **P4 ganges (the ≥5-blocker cascade, the sprint's only remaining bucket gate) moves earlier → Days 7–9**, giving the bimodal +2-or-0 track more room and surfacing its `rPower` REPLAN (the likely blocker) even earlier than the Day-8 plan.
- The sarf dedicated effort → **Sprint 37 carryforward**, with the S35 design + Task-5 refresh (measured baseline, 6-call-site corpus-safety surface, 7-term derivation, atomicity spec, regression-harness requirement) as the implementer-ready hand-off.

## 5. KPI + Go/No-Go

**BANK — clean.** `Translate` stays **135** (sarf stays `translate_failure` — the O(369K) emit is unchanged); genuine floor **75**; Solve 108 / Match 93 unchanged; DB byte-unchanged; **no `src/` touched** (measurement-only). Zero broken code. The control-first discipline held: the baseline was re-confirmed, the atomic-re-arch reality was recognized, and no risky/partial `src/` shipped for the lowest-leverage bucket.

**Forward (`PLAN.md` §2):** floor 75 · Solve 108–110 (P4 ganges bimodal, now Days 7–9) · Translate 135 (sarf banked) · robustlp de-allowlist (Day 10) · turkey +1 testbed-deferred.

---

**Document Status:** ✅ Complete — Sprint 36 Day 6 (sarf P2 baseline re-confirmed → BANK; atomic dedicated effort, Translate flat 135, budget → P4)
**Last Updated:** 2026-08-08 · **Owner:** Sprint 36 Execution Team

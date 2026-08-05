# Sprint 35 — Day-13 Retest Staging (drafted Day 12)

Pre-stages the Day-13 final retest + closeout so Day 13 is execution, not discovery. Anchor: S34 close `78ceaead`; S35 close will be the Day-13 merge. The sprint ran **modal-FLAT** (P4 banked Day 3, markov banked Day 11, turkey testbed-pending), so the expected outcome is the projection's **flat branch** — pre-filled below to be confirmed, not derived, on Day 13.

---

## 1. Retest checklist (the Day-13 prompt's gates)

- [ ] **Determinism ×3** — emit the corpus under `PYTHONHASHSEED ∈ {0,1,42}`; every golden byte-identical across seeds (emit-level; local-runnable — no solve needed). Expected: ✅×3 (no src/ change this sprint touches emit except the Day-6 turkey `_infer_domainless_tuple_arity`, which is deterministic).
- [ ] **`--resolve-changed --since-commit 78ceaead`** = GO. At-risk set (git-diff of `data/gamslib/mcp/`) = **{turkey}** only (confirmed Checkpoint 2). Expected: turkey `path_syntax_error → path_solve_license ~ shift`, **bucket held → GO** (both non-bucket; the 1000-row demo limit blocks the local solve).
- [ ] **Golden-staleness** — clean by construction (no src/ change on the close branch; the one drifted golden, turkey, was regenerated + validated with PR #1620).
- [ ] **PR25 genuine-vs-methodology final tally** — recompute over the 142 convex candidates. Expected: **Solve 108 / Match 93 / genuine floor 75** (DB byte-unchanged since the anchor → the S34 hand-partition carries forward verbatim; recompute confirmed Day 10).
- [ ] **DB integrity** — `git diff 78ceaead..HEAD -- data/gamslib/gamslib_status.json` empty (0 bucket move).

## 2. Expected close vs the bimodal projection ([PLAN.md](PLAN.md) §2)

| KPI | flat branch | upside branch | **expected (FLAT)** |
|---|---|---|---|
| Solve | 108 | 110 | **108** |
| Match | 93 | 95 | **93** |
| genuine floor | 75 | 77 | **75** |
| Translate | 135 | 135 | **135** |
| path_syntax_error | 7 | 5 | **7** |
| (a-priori refuted) | — | — | **not ≥ 112** ✅ |

**Which mode landed:** **bimodal-FLAT**, not P4 PROCEED. P4 (ganges/gangesx) banked Day 3 as a ≥5-blocker cascade; no cold match landed. **The floor did NOT move** (75, cold-match-contingent branch did not realize) — every mover was refuted or banked (P1 mine, P2 sarf, P3 fawley, P4 ganges, P5 camcge/rocket). The sprint's product is **de-risking + two verified-but-banked landings** (Day-9 fawley control 473→1.14e-13; Day-11 markov diagonal split 13.3→1.55) + **one landed compile-recovery** (turkey, testbed-gated) + a **newly-discovered +1 floor lever** (markov, §1 of the carryforwards).

**Honest framing for the retrospective:** this is the *third consecutive* modal-flat sprint (S33 +1 was the last genuine bucket move). The deep-track REPLAN pattern held — control-first, zero broken code shipped. The upside is now concentrated in two banked levers (markov +1 floor, local; turkey +1, testbed) for Sprint 36 / the next testbed cycle.

## 3. The GAMS-version axis (NEW this retest — [FOLLOWUPS_GAMS54_TRANSITION.md](FOLLOWUPS_GAMS54_TRANSITION.md))

The 108/93/75 baseline + the committed DB were built under **GAMS 53**; CI + local now validate under **GAMS 54.2.1** (the license-expiry cascade, Day 6). GAMS 54 is stricter and does not solve identically to 53. **Decision required at close:**

1. **Re-solve the corpus under GAMS 54 in the licensed testbed** and diff buckets vs the v53-built DB. Are 108/93/75 preserved?
2. **Decide the canonical validation version** — pin the DB to 54 and re-baseline, or keep 53 where a license is available for solving.
3. **Re-check the 5 OBJ-GAP models** (agreste/cesam/chain/fawley/rocket) — benign local-optima differences or a real regression?
4. Confirm the PR19 Tier-0/1 canaries stay green under 54 (first 54 CI validation).

**Recommendation to carry into the decision:** the local determinism/`--resolve-changed`/golden-staleness gates are **emit-level** (version-independent) and stay valid. Only the *solve* buckets carry a v53→v54 risk, and the local demo license can't solve the >1000-row models regardless. So the practical close is: **report the v53-built KPIs as the S35 baseline (unchanged), and open the v54 re-baseline as the first Sprint-36 infra task** (a testbed re-solve), rather than blocking the S35 close on a testbed cycle. Confirm this framing on Day 13.

## 4. Closeout deliverables (Day 13)

- [ ] `SPRINT_35/SPRINT_LOG.md` — per-day ledger (Days 0–13; PRs #1616–#162x), final KPIs, determinism/`--resolve-changed`/DB-integrity results, the GAMS-version-axis decision.
- [ ] `SPRINT_35/SPRINT_RETROSPECTIVE.md` — the modal-flat honest close; the two banked levers (markov/turkey) as the live upside; the control-first REPLAN discipline (5 tracks); the v53→v54 transition; the markov lever as the sprint's genuine discovery.
- [ ] Update `EPIC_4/SUMMARY.md` row 35 from "provisional" → final (should match the Day-10 provisional fill: 108/93/75 FLAT).
- [ ] The carryforwards are already drafted: `SPRINT_36_CARRYFORWARDS.md` (Day 12).
- [ ] Quality gate only if `*.py` touched (the close is expected docs/DB-only → N/A).

---

**Document Status:** ✅ Staged — Sprint 35 Day 12 (for Day-13 execution)
**Last Updated:** 2026-08-04
**Owner:** Sprint 35 Execution Team

# Sprint 37 — Retrospective

**Closed 2026-08-13** · floor **75 → 76** (first advance since Sprint 33) · 2 firm `src/` landings · 2 tracks banked with bounded next steps

---

## 1. What worked

**Pulling P4 and P5 forward when P2 died on Day 5.** The plan front-loaded ganges across Days 4–5 with fawley/sarf at 7–8. When ganges REPLAN'd, the freed budget went straight into fawley — which **landed on Day 6**, clearing a gate blocked since Sprint 35. A sprint that would have gone flat on its planned lever produced two landings instead. The prerequisite was that P2's stop condition was pre-registered and honoured on the day it triggered, rather than being nursed for another three days.

**Control-first (PR24/PR27) paid twice, in opposite directions.** markov's Day-1 control passed the leak gate unqualified, and the Day-2 landing was byte-identical to it — no surprises. ganges' Day-4 control proved all four fixes work *and* that the cascade cannot land, at the cost of zero broken code in `src/`. The discipline is not "verify before landing"; it is that a control can return **PROCEED** or **REPLAN** and both are cheap.

**The third fawley attempt succeeded by adding, not subtracting.** Two prior narrowings only ever removed cases from an over-firing predicate, and both leaked. The one that worked added a **positive** requirement — the coefficient must reference the subset's parent. Worth generalizing: when a predicate over-fires, subtracting exclusions chases symptoms; naming what must be *true* of the real case usually terminates.

## 2. The recurring failure mode: verifying a component, asserting a system property

This sprint produced at least six instances, and they are the same bug in different clothing:

| # | what was verified | what was asserted | the gap |
|---|---|---|---|
| 1 | the `determinism` marker matches a selector | the determinism test runs in CI | `nightly.yml` is **path-scoped**; no job invoked the path |
| 2 | `--resolve-changed` returned GO | markov's shift was confirmed | it selects by **git diff** — uncommitted goldens are invisible |
| 3 | a helper matching the `$141` fingerprint exists | the cascade is on `main` | the helper was from an unrelated cesam fix |
| 4 | "populate `solver_version`" was instructed twice | the field would populate | the **extractor's regex had never matched** |
| 5 | my nested-`**` detector flagged 28 sites | 28 defects | it was wrong about 27 |
| 6 | my loop reported "all 20 artifacts untracked" | the artifacts were gone | `git ls-files` showed **19 still tracked** |

**#4 and #6 are the expensive ones.** #4 wasted two sprints of re-baseline instructions on a missing *write* when the defect was a failed *read*. #6 is worse: the verification loop and the ground truth disagreed, and I reported the loop. A check that can pass while the property is false is not a weak check — it is a **false negative generator**, and it is more dangerous than no check, because it retires the question.

**The countermeasure that actually worked** was asserting the property at the point of use rather than the point of definition: `--min-scope 170` is asserted on **discovery**, before any narrowing, so a gate that silently sweeps 3 goldens instead of 163 fails loudly. That pattern — assert the *scope* of a check, not just its result — is the one worth propagating.

## 3. Banked staleness: a sweep is a snapshot, not a fix

Day 8 swept `PLAN_PROMPTS.md` for stale figures: 6 corrections to Days 8–13, Days 0–7 byte-identical. **Day 9 immediately re-staled the same document** — the v54 re-baseline moved Match 93 → 94 and cold-optimal 64 → 65, so by Day 13 the prompt read *"the partition is presolve-match 29 / cold-optimal 64 with Match unchanged at 93"* against an actual **29 / 65 / 94**. The floor conclusion (**76**) was unaffected and the day's instructions were still executable, but the numbers in the instruction were wrong within 24 hours of being corrected.

This is the sprint's most general finding, and it recurred in four places: the OBJ-GAP set banked at 5 and measured at **8**; Day 4's prompt presuming a cascade that was not on `main`; `SUMMARY.md` row 37 pointing three sprints at the wrong theme; and the prompt sweep above.

**The lesson is not "sweep more often."** Every one of these documents was accurate when written. The defect is that **figures were copied into instructions instead of being derived at execution time**. A prompt that said "recompute the partition and report it" would never go stale; one that says "the partition is 29/64" goes stale the moment anything moves. Where a figure must be quoted, it should carry the commit it was measured at.

## 4. Documentation trusted as specification

Three defects this sprint came from a document describing behaviour the code did not have:

- `extract_path_version`'s **docstring asserted a listing format GAMS does not emit** — which is presumably exactly how the never-matching regex survived review. A reviewer checking code against its docstring finds agreement; both were wrong together.
- The **genuine floor cannot be derived from the DB**. A mechanical count yields 65 against a recorded 76, because the "cold emit byte-identical to pre-fix" qualifier lives only in a hand-partition. Any future floor-tracking automation will silently emit 65 and look authoritative.
- PR #1674 review caught me **fixing the implementation while leaving the stale docstring** — the exact defect that PR diagnosed, recurring inside its own fix.

The shared root: a description and its behaviour drifted, and the description was trusted. This is distinct from §2 (where a check was wrong) and §3 (where a figure aged). Here the artifact was **wrong when written** and stayed authoritative for sprints.

## 5. The `git add -A` incident

A `git add -A` after a GAMS run in the repo root committed **20 runtime artifacts** — including **`decis.lic` (license material)** and a DECIS output file carrying a third-party copyright header — plus **36 unintended presolve goldens**. Review caught 4 of 56.

The goldens are the more serious half. They would have expanded the swept corpus 170 → 206 using references generated **in that same run**, making the gate certify its own output. All 56 were removed; the artifacts are now `.gitignore`d so the mechanism cannot repeat.

Two things to carry: **GAMS writes scratch files to `cwd`, and `cwd` is the repo root**; and **generating references and committing them in one unreviewed step is how a gate stops being a gate**.

## 6. On the sprint's honesty

The +1 Match and the +1 floor are **different models with different causes**, and the row says so: markov earned the floor through a real emit fix; hhfair's Match came free from the v54 solver with byte-identical emit and adds **nothing** to the floor. It would have been easy to report "+1 Match, +1 floor" as one achievement.

Likewise the DB **changed** this sprint, and the log states it. Three prior sprints reported "flat" backed by a byte-unchanged DB; that is what made their flatness a measurement rather than an absence of looking. Reporting this sprint's DB movement in the same breath as the KPIs keeps that distinction usable.

And the P3 consultation send is recorded as **not done**, for the third sprint. It was never executable by the execution agent — the bundle names no recipient, address, or channel. Carrying it as "in progress" would have been a fiction; it needs a human to name a recipient.

## 7. Recommendations for Sprint 38

1. **Derive figures in prompts, don't quote them** — or quote them with the commit they were measured at (§3).
2. **Assert the scope of every gate, not just its verdict** — `--min-scope` is the template; the leak gate and `--resolve-changed` both have silent-narrowing modes (§2).
3. **Floor provenance must travel with the floor.** Any automation that reports it needs the per-model hand-partition, or it will report 65 (§4).
4. **ganges' next step is the rebind predicate, not the cascade.** All four fixes work; only `$149`'s over-fire onto `prolog` blocks it (#1668).
5. **Decide the 36 presolve goldens deliberately.** They plausibly fix the 153-cold/17-presolve coverage asymmetry — as a reviewed change, not a side effect of a solve run (§5).
6. **The consultation send needs an owner named in the sprint plan**, or it should be struck from the plan (§6).

---

**Document Status:** ✅ Complete — Sprint 37 retrospective.
**Last Updated:** 2026-08-13 · **Owner:** Sprint 37 execution team

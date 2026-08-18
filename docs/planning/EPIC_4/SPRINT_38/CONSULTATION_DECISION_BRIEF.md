# Sprint 38 Prep Task 7 — Consultation Ownership Decision Brief (P3)

**Date:** 2026-08-18 · **Branch:** `planning/sprint38-task7` · **Measured at:** `6c517315` · **Scope:** docs only.

**For a Day-0 decision. Both branches are executable the same day.**

---

## 1. The single question

> **By what channel — and to what address — should the rocket PATH-consultation be sent to Michael Ferris and Steven Dirkse?**

**The gap is narrower than it has been described.** Every prior write-up, including this task's own prompt, says *"the bundle names no recipient, address, or channel."* That is true of the **bundle**, but not of the project:

| | status |
|---|---|
| **Recipient identity** | ✅ **known** — Michael Ferris and Steven Dirkse, named four times in `PROJECT_PLAN.md` (S39 component, S39 acceptance criterion, S40 feedback integration, External Dependencies) |
| **Address / channel** | ❌ **missing everywhere** |

So the blocker is **one fact, not two**. That matters: "nobody knows who to send it to" invites a research task; "we know who, we lack an address" is a two-minute answer from someone who has it.

## 2. Why this cannot be deferred again — it is not only P3's problem

**Sprint 39 carries the identical gap.** Its "Submit and Follow Up" step reads *"Send document to Michael Ferris and Steven Dirkse"* — named recipients, no channel — for a **broader** consultation document compiled from the Sprint-22 case studies.

**Consequence: striking P3 relocates the problem rather than resolving it.** The channel must be established for Sprint 39 regardless of which branch is chosen here. A strike buys one sprint, and Sprint 39's send then slips for the same reason this one has slipped five times.

**⇒ The channel question should be answered on Day 0 even if the strike branch is taken.**

## 3. The two branches, costed

### Branch A — SEND

**Needs:** the address/channel. Nothing else — §5's package is complete.

**Buys:**

| model | contingent gain | note |
|---|---|---|
| **rocket** (#1462) | **+1 Solve** | contingent on a usable option-set / regularization schedule in the reply |
| **fawley** (#1111/#1112) | **+Solve** | **same class** — the S36 `--force` survey was NEGATIVE (homotopy / multistart / optfile all leave MS-5), so consultation is its *only* remaining lever |
| **mine** (#1443) | **0 bucket** | the only non-invariant lever is an LP-side reformulation, out of emit scope |

**Costs:** ~30 minutes to send; then an unbounded wait. **No sprint work is blocked on the reply** — Sprint 39 integrates it if it arrives.

### Branch B — STRIKE

**Removes from projections:** rocket's +1 Solve, fawley's +Solve. **mine is unaffected** (already 0 bucket).

**Does *not* invalidate Sprint 39.** Its consultation component (~8–10 h of 22–28 h) compiles the **Sprint-22 case studies** into a broader document; the rocket input *feeds* it as one input. Solution Forcing (~6–8 h), Remaining Pipeline Fixes (~6–8 h) and the retest (~2 h) are untouched. **Sprint 39 remains viable — it loses an input, not its premise.**

**Real cost:** rocket and fawley have **no other lever**. Every emittable-GAMS avenue is exhausted for both (§4 of the input: PATH options, μ-continuation, multistart, and the division-by-variable reformulation all fail). Striking means their +Solve is **unreachable indefinitely**, not merely deferred.

### Recommendation

**Branch A**, on the narrow grounds that the missing input is one address and the alternative permanently forfeits two models' only remaining lever. But **the decisive action either way is establishing the channel**, because Sprint 39 needs it regardless (§2).

## 4. What is *actually* stale in the bundle — one thing, and it is fixable in a line

The bundle was authored **2026-08-03**; the corpus was re-pinned to **GAMS 54.2.1 on 2026-08-12**, nine days later.

**The failure state still reproduces.** Under GAMS 54.2.1 / PATH 5.2.01, rocket, mine and fawley are all `model_infeasible` — the bucket the question describes.

**But the bundle carries no version stamp at all**, and its quoted figures (`INFES 477 → 382`, objective `1.0128`, `nh=10`) were measured under the **pre-re-pin** toolchain. A recipient attempting to reproduce `382` on 54.2.1 may get a different number and conclude the report is unreliable.

**Fix before sending:** add one line to §1 of the input —

```
Measured under GAMS 51.3.0 / PATH 5.2.01. Re-confirmed model_infeasible
under GAMS 54.2.1 / PATH 5.2.01 (2026-08-18); the INFES and objective
figures below are from the original toolchain.
```

That is the whole remediation. Nothing else in the package is stale.

## 5. The send package — complete except one field

**Attach:** `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` (§3 question, §2 ruled-out-lever survey, §4 remaining-lever sweep) + `data/gamslib/raw/rocket.gms` + the two reproduction commands.

**Covering message (fill the two bracketed fields, add the version line from §4, send):**

> **To:** `[ADDRESS — Michael Ferris, Steven Dirkse]`
> **Channel:** `[EMAIL / GitHub issue / mailing list — TO BE NAMED]`
> **Subject:** PATH convergence on a discretized optimal-control MCP (Goddard rocket, COPS) — option-set / regularization guidance
>
> We generate MCPs from GAMS NLP models (KKT stationarity + complementarity) and solve them with PATH. One model resists every lever we can reach from the emitter, and we would value your guidance.
>
> **The model.** `rocket.gms` from GAMSLib (the Goddard rocket, COPS), discretized optimal control. The embedded NLP solves to 1.0128. The generated MCP is **MODEL STATUS 5** with `EXIT — other error` at an ill-conditioned initial Jacobian, including when warm-started from the NLP optimum.
>
> **What we ruled out.** We initially suspected the division-by-variable terms (`1/m(h)`, `1/ht(h)²`). `proximal_perturbation` / `merit_function` / `crash_method` move INFES **477 → 382** but never converge. An auxiliary-variable reformulation removing **all** division-by-variable from the initial Jacobian **also** fails — MS-5 cold, MS-5 warm-started from the optimum, and MS-5 at every μ-continuation step. **So the non-convergence appears intrinsic to the discretized optimal-control MCP structure, not to Jacobian conditioning.** The residual at the NLP optimum is clean except the boundary rows (`stat_ht(h0)`, `stat_ht(h50)`, `stat_step`), which move with the warm-start value — a non-convex boundary signature.
>
> **Our question.** Which PATH option set, regularization schedule, or model reformulation would force convergence for this class of discretized optimal-control MCP?
>
> **Reproducing it** (GAMS 54.2.1, PATH 5.2.01):
> ```bash
> python -m src.cli data/gamslib/raw/rocket.gms -o rocket_mcp_presolve.gms --nlp-presolve
> gams rocket_mcp_presolve.gms      # -> MODEL STATUS 5, warm-started from the embedded NLP optimum
> ```
>
> Full write-up attached, including the complete ruled-out-lever survey. Happy to supply any additional artifacts.

**What a reply must contain to be actionable:** a concrete option set / `optfile` contents, a regularization or continuation schedule, or a named reformulation class. A diagnosis without one of those three does not unblock rocket.

## 6. Strike wording — executable same-day

If Branch B is chosen, apply verbatim:

**`PROJECT_PLAN.md`**, Sprint 38 P3 deliverable:

> **P3 STRUCK 2026-08-__.** The rocket/mine consultation was not sent; after five carries (S33–S37) no channel was established. **rocket's +1 Solve and fawley's +Solve are removed from all projections** and reclassified as **consultation-gated — unreachable without external input**, since every emittable-GAMS lever is exhausted for both. mine is unaffected (0 bucket). **Sprint 39 remains viable** — its consultation compiles the Sprint-22 case studies and loses one input, not its premise. **The channel gap is NOT closed by this strike**: Sprint 39's own "Submit and Follow Up" step carries the identical gap and must establish a channel independently.

**`CONSULTATION_BUNDLE.md`**, line 46 — replace the unchecked box with:

> - [x] **STRUCK (Sprint 38, 2026-08-__)** — not sent; no channel established across S33–S37. rocket/fawley +Solve reclassified consultation-gated.

## 7. Tracking record — for the SEND branch

**Where the send is recorded:** a comment on **issue #1462**, which today carries **exactly one comment** (the Sprint-28 bisect, 2026-06-20) and **no send record whatsoever** — the reason "was it ever sent?" needed archaeology in Sprint 37.

**Comment to post at send time:**

> **Consultation sent 2026-08-__** to `<recipients>` via `<channel>`. Package: `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` + `rocket.gms` + reproduction commands (GAMS 54.2.1 / PATH 5.2.01). Awaiting reply. Actionable reply = an option set / `optfile`, a regularization or continuation schedule, or a named reformulation class.

**Follow-up rule:** if no reply within **one sprint** (14 days), post a follow-up comment and treat rocket's +1 as consultation-gated for planning purposes — **without** re-opening the send decision.

Also tick `CONSULTATION_BUNDLE.md` line 46. **Note that box conflates three actions** — *"submit rocket; pose the mine question; run the fawley `--force` survey"* — and the **fawley survey was completed in Sprint 36** (result: NEGATIVE). A single checkbox spanning three actions, one already done, is part of why it never got ticked. **Split it on strike or send.**

---

**Document Status:** ✅ Complete — Sprint 38 Prep Task 7. Both branches executable; **the decision needs one fact: the channel/address.** Recipient identity is already known.
**Last Updated:** 2026-08-18 · **Owner:** **Requires a human decision-maker**

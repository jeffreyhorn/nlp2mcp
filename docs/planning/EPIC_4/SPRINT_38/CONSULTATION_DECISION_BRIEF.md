# Sprint 38 Prep Task 7 — Consultation Ownership Decision Brief (P3)

**Date:** 2026-08-18 · **Branch:** `planning/sprint38-task7` · **Measured at:** `6c517315` · **Scope:** docs only.

**For a Day-0 decision. Both branches are executable the same day.**

---

## 1. The single question — ✅ ANSWERED 2026-08-18

> ~~By what channel — and to what address — should the rocket PATH-consultation be sent to Michael Ferris and Steven Dirkse?~~

**✅ RESOLVED (owner, 2026-08-18). Channel: email.**

| recipient | address |
|---|---|
| **Michael Ferris** | `ferris@cs.wisc.edu` |
| **Steven Dirkse** | `steve@gams.com` *or* `sdirkse@gams.com` |

**Note on Dirkse's address:** two were supplied as alternatives without a preference. **Recommend addressing both** — a bounce on one is silent, and this is a one-shot message after five carries. Cost of including both is zero.

**⇒ Branch A (SEND) is unblocked. §5's package is ready; only the pre-send version stamp was outstanding, and it is now applied.**

**⚠ The send itself is a human action.** This session has no email capability (the claude.ai Gmail connector is unauthenticated and unavailable here), so the message in §5 is prepared to copy-paste. **§7's tracking comment should be posted to #1462 at send time.**

**Why the gap was narrower than described** *(the finding that led here — retained as the record):* every prior write-up, including this task's own prompt, said *"the bundle names no recipient, address, or channel."* That was true of the **bundle**, but not of the project:

| | status |
|---|---|
| **Recipient identity** | ✅ **known** — Michael Ferris and Steven Dirkse, named four times in `PROJECT_PLAN.md` (S39 component, S39 acceptance criterion, S40 feedback integration, External Dependencies) |
| **Address / channel** | ~~❌ missing everywhere~~ → ✅ **supplied by the owner 2026-08-18** (email; see above) |

So the blocker was **one fact, not two** — and it was answered in a single message, which is what that reframing predicted. *"Nobody knows who to send it to"* invites a research task; *"we know who, we lack an address"* is a two-minute answer.

## 2. Why this cannot be deferred again — it is not only P3's problem

**Sprint 39 carries the identical gap.** Its "Submit and Follow Up" step reads *"Send document to Michael Ferris and Steven Dirkse"* — named recipients, no channel — for a **broader** consultation document compiled from the Sprint-22 case studies.

**Consequence: striking P3 relocates the problem rather than resolving it.** The channel must be established for Sprint 39 regardless of which branch is chosen here. A strike buys one sprint, and Sprint 39's send then slips for the same reason this one has slipped five times.

**⇒ The channel question needed answering regardless of branch. It now is — which also unblocks Sprint 39's own send**, so that gap is closed too rather than deferred.

## 3. The two branches, costed

### Branch A — SEND

**Needs:** ~~the address/channel~~ — **✅ supplied 2026-08-18.** Nothing outstanding; §5's package is complete and the §4 version stamp is applied.

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

### Recommendation → ✅ ADOPTED

**Branch A (SEND).** The owner supplied the channel on 2026-08-18, unblocking it. Branch B's wording (§6) is retained unused, in case a send proves undeliverable.

## 4. What is *actually* stale in the bundle — one thing, and it is fixable in a line

The bundle was authored **2026-08-03**; the corpus was re-pinned to **GAMS 54.2.1 on 2026-08-12**, nine days later.

**The failure state still reproduces.** Under GAMS 54.2.1 / PATH 5.2.01, rocket, mine and fawley are all `model_infeasible` — the bucket the question describes.

**But the bundle carries no version stamp at all**, and its quoted figures (`INFES 477 → 382`, objective `1.0128`, `nh=10`) were measured under the **pre-re-pin** toolchain. A recipient attempting to reproduce `382` on 54.2.1 may get a different number and conclude the report is unreliable.

**✅ APPLIED 2026-08-18** to `docs/planning/EPIC_4/SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` §1, as a marked toolchain-stamp note. The wording drafted here was:

```
Measured under GAMS 51.3.0 / PATH 5.2.01. Re-confirmed model_infeasible
under GAMS 54.2.1 / PATH 5.2.01 (2026-08-18); the INFES and objective
figures below are from the original toolchain.
```

That was the whole remediation, and it is done. Nothing else in the package is stale — the attachment is ready to send as-is.

## 5. The send package — ✅ COMPLETE AND READY

**Attach:** `docs/planning/EPIC_4/SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` (§3 question, §2 ruled-out-lever survey, §4 remaining-lever sweep) + `data/gamslib/raw/rocket.gms` + the two reproduction commands.

> ## ✅ SENT 2026-08-26 — and the package below was NOT what went out.
>
> Email to `ferris@cs.wisc.edu`, `steve@gams.com`, `sdirkse@gams.com`. Recorded on **#1462**; the mine question on **#1443**. Follow-up due **2026-09-09**.
>
> **Three corrections were made at send time, all from live re-measurement on GAMS 54.2.1 / PATH 5.2.01:**
>
> 1. **The failure description below is STALE.** It says `EXIT — other error` at an ill-conditioned initial Jacobian. rocket now gives `SOLVER STATUS 1 Normal Completion` / `MODEL STATUS 5 Locally Infeasible` after **9,241 iterations**, 0 evaluation errors — PATH completes and reports infeasibility, it does not abort.
> 2. **The attachments changed.** `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` is an internal planning doc (sprint numbering, deferral history, unresolvable cross-references, and a `CASE_B — emit_bug` label that reads as *our* bug); it was replaced by **`docs/planning/EPIC_4/SPRINT_38/ROCKET_CONSULTATION_EXTERNAL.md`**, an externally-scoped extract. `rocket.gms` was replaced by **`data/gamslib/mcp/rocket_mcp_presolve.gms`** — the NLP source solves fine and is GAMSLib seq 319, so it was never the artifact in question.
> 3. **Two further threads rode along**, since they go to the same recipients: the **license-capacity request** for the 11-model cohort, and the **`agreste` + `mine`** LP-derived-MCP question, reframed around the signature the two share.
>
> The §5 text below is retained **as authored** for provenance. **Do not re-send it.**

**Covering message — as prepared (superseded; see the banner above).** Addresses filled; the §4 version stamp is applied to the attachment.

> **To:** `ferris@cs.wisc.edu`, `steve@gams.com`, `sdirkse@gams.com`
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

> **P3 STRUCK `<FILL: YYYY-MM-DD>`.** The rocket/mine consultation was not sent; after five carries (S33–S37) no channel was established. **rocket's +1 Solve and fawley's +Solve are removed from all projections** and reclassified as **consultation-gated — unreachable without external input**, since every emittable-GAMS lever is exhausted for both. mine is unaffected (0 bucket). **Sprint 39 remains viable** — its consultation compiles the Sprint-22 case studies and loses one input, not its premise. **The channel gap is NOT closed by this strike**: Sprint 39's own "Submit and Follow Up" step carries the identical gap and must establish a channel independently.

**`CONSULTATION_BUNDLE.md`**, line 46 — replace the unchecked box with:

> - [x] **STRUCK (Sprint 38, `<FILL: YYYY-MM-DD>`)** — not sent; no channel established across S33–S37. rocket/fawley +Solve reclassified consultation-gated.

## 7. Tracking record — for the SEND branch

**Where the send is recorded:** a comment on **issue #1462**, which today carries **exactly one comment** (the Sprint-28 bisect, 2026-06-20) and **no send record whatsoever** — the reason "was it ever sent?" needed archaeology in Sprint 37.

**Comment to post at send time:**

> **Consultation sent `<FILL: YYYY-MM-DD>`** to `<FILL: recipients>` via `<FILL: channel>`. Package: `docs/planning/EPIC_4/SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` + `rocket.gms` + reproduction commands (GAMS 54.2.1 / PATH 5.2.01). Awaiting reply. Actionable reply = an option set / `optfile`, a regularization or continuation schedule, or a named reformulation class.

**Follow-up rule:** if no reply within **one sprint** (14 days), post a follow-up comment and treat rocket's +1 as consultation-gated for planning purposes — **without** re-opening the send decision.

Also tick `CONSULTATION_BUNDLE.md` line 46. **Note that box conflates three actions** — *"submit rocket; pose the mine question; run the fawley `--force` survey"* — and the **fawley survey was completed in Sprint 36** (result: NEGATIVE). A single checkbox spanning three actions, one already done, is part of why it never got ticked. **Split it on strike or send.**

---

**Document Status:** ✅ Complete — Sprint 38 Prep Task 7. **The channel was supplied by the owner on 2026-08-18 and Branch A (SEND) is unblocked.** The package is ready to copy-paste; the send is a human action.
**Last Updated:** 2026-08-26 · **Owner:** Sprint 38 execution team · **Remaining human action:** ✅ **NONE — both complete.** Sent 2026-08-26; tracking comments posted to #1462 and #1443; `SPRINT_36/CONSULTATION_BUNDLE.md` boxes ticked. **Next checkpoint: 2026-09-09 follow-up if no reply.**

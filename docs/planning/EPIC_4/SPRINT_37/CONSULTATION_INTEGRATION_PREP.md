# Consultation Reply-Integration Prep (rocket/mine P3) + camcge Epic-5 Walras Gate Scoping (Prep Task 9)

**Date:** 2026-08-10 · **Branch:** `planning/sprint37-task9` · **Scope:** docs/analysis-only — a `/tmp` camcge control; no `src/` change, DB untouched.

**One line:** the headline is not a technical finding — **the rocket consultation has never been sent.** It has been "FINALIZED, ready to submit" since 2026-07-15 and has slipped S33 → S34 → S35 → S36; the bundle's one *action* checkbox is still unchecked. So a reply cannot have arrived, and the +1 is contingent on a message nobody has transmitted. Separately, the **Epic-5 handoff spec still prescribes a transformation that Sprint 30 refuted** — fixed here.

Reference: `SPRINT_36/DAY11_P5_CONSULTATION.md`, `SPRINT_36/CONSULTATION_BUNDLE.md`, `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`, `SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md`, `EPIC_5/CGE_DEGENERACY_SCOPING.md`.

---

## 1. rocket #1462 — the reply cannot have arrived: nothing was sent (Unknown 3.1)

The prompt asks whether the PATH authors' reply has arrived and how to integrate it. **The prior question is unmet.** Evidence:

| check | finding |
|---|---|
| `CONSULTATION_BUNDLE.md` hand-off checklist | preparation items all `[x]`; the single **action** item — `- [ ] **Sprint 36:** submit rocket to PATH authors; pose the mine LP-degeneracy question; run the fawley --force survey` — is **unchecked** |
| S36 Day-11 §1 wording | "is **ready to submit** to the PATH authors" — *ready*, not sent |
| issue #1462 | 1 comment, from the **Sprint-28** bisect; no submission or reply record; issue still OPEN |
| grep for a send/reply record | none anywhere in `EPIC_4/` or `EPIC_5/` |
| the input doc itself | "FINALIZED (Sprint 32 Day 9, **2026-07-15**)"; its own renumbering note records the consultation slipping **S33 → S34 → S35** and being retargeted to S36 |

**So rocket has been submission-ready for ~4 weeks across four sprint boundaries without being transmitted.** The phrase that enabled the drift is in the input doc: *"Submitted as part of the Sprint-36 consultation bundle"* — which means *packaged into the bundle document*, and reads as *sent*. My own Task-1 Known-Unknown inherited that reading ("the FINALIZED input was submitted from the Sprint-36 carryforward"); it was wrong.

**Disposition:** the blocker is **neither technical nor PATH-author latency — it is that nobody has pressed send.** No amount of further prep moves it. This needs a human action (email the finalized package to Ferris/Dirkse), and it should be tracked as an owner-assigned action item, not another banked hand-off.

### Integration staging (unchanged, and still correct)

When a reply does arrive, the integration is bounded — the scaffold already exists:

- The recommended **option set / regularization schedule** maps onto `--nlp-presolve --force homotopy` → `proximal_perturbation` μ-continuation + `mcp_model.optfile = 1` (`CONSULTATION_BUNDLE.md` §rocket; scaffold at `src/cli.py:207`).
- A recommended **reformulation** instead would be a new track, not an option-set plug-in — scope it when it arrives.
- **The Case-c objective-gradient sign flip stays BANNED** (control-refuted ×4).

**+1 Solve remains contingent** — now explicitly on *sending*, then on the reply.

## 2. mine #1443 — 0-bucket confirmed; the question was also never posed (Unknown 3.2)

**The technical claim holds.** The Sprint-34 value-invariance proof settles it: *no relabeling of the dual can create the missing +16000 — the scalar system is invariant under relabeling*. The only non-invariant lever is an **LP-side reformulation**, which is outside emit scope. So mine is **0 bucket** regardless of the consultation outcome, and `x.up=inf` stays **BANNED** (control-refuted). DB: `model_infeasible`, unchanged.

**But the same unchecked action item covers mine** — "pose the mine LP-degeneracy question" was never done either. The question is *specified* (`SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md`), not *posed*. Since mine is 0-bucket either way, this costs no KPI — but it should be batched with the rocket send rather than carried as a separate hand-off.

## 3. camcge #1330 — baseline reproduced; the gate is Epic-5 (Unknown 3.3)

Ran the `/tmp` control on current `main` (GAMS 54.2.1, demo):

| quantity | measured |
|---|---|
| emit (`--nlp-presolve`) | **18 s** |
| embedded NLP `camcge` | **MS-2 Locally Optimal @ omega 191.7346** ✔ (the documented optimum) |
| MCP `mcp_model` | **MS-4 Infeasible** |
| MCP size | **641 single equations / 641 single variables** — confirms demo-reachable (<1000) |

The premise reproduces exactly: the NLP reaches the correct optimum, and the MCP is MS-4 — the structural Walras rank-deficiency, not an emit defect.

**The three-part dual-consistent Walras redefinition is the Epic-5 gate, and was deliberately not attempted here.** It is: (1) keep every market-clearing row (no orphaned dual), (2) the consumption-weighted numéraire `sum(i$cles(i), cles(i)·(p(i) − pd0(i))) = 0`, (3) **redefine the redundant market's dual via Walras' law** — part (3) being the hard piece and a from-scratch CGE-aware emit layer. Expected outcome **MS-4**: price-pin → MS-4, single-dual-pin → MS-4, drop-row → corrupt @ omega 299; **3+ sprints of variants have all failed to reach MS-1**. Attempting it in a prep task would be re-running a refuted experiment.

## 4. The Epic-5 handoff spec was stale — fixed (Unknown 3.4)

**The per-model-numéraire fallback is correct**, and the Epic-5 doc argues it well: the Walras-redundancy + price-homogeneity argument is generic to closed CGE models, but *which* row is redundant and *which* price is the natural numéraire is **per-model** (depends on closure + SAM), so Epic 5 needs a **per-model numéraire-selection rule**, not a hard-coded one. The cohort survey supports the narrow scope — **camcge is the only inherent Walras singularity**; the DB confirms `irscge`/`lrgcge`/`moncge`/`stdcge`/`quocge` all **match**, and the other "CGE cohort" issues are ordinary emit bugs.

**But the handoff spec prescribed a refuted transformation.** `EPIC_5/CGE_DEGENERACY_SCOPING.md` §3 still specified *"drop-one-redundant-row + fix-one-numéraire"* and concluded it "yields a nonsingular square MCP whose unique solution is camcge's NLP equilibrium (191.7346)". **Sprint 30 Day 11 refuted the drop-row half** — it is primal-correct but **breaks the MCP dual** (every market-clearing multiplier is a needed price/wage in the stationarity; dropping a row orphans it → **omega 299, MS-4**). The document contained **zero** occurrences of "refut": the finding never propagated from the sprint docs into the spec Epic 5 will actually start from.

**Fixed in this task:** added a `⚠ SUPERSEDED IN PART` note at §3 recording the refutation, the two-nullspaces diagnosis, the current three-part formulation, and the discouraging banked evidence — so an Epic-5 implementer reads §3 as the *original* reasoning, not the current plan.

This is the same failure mode as §1: **information that exists in sprint docs but never reaches the document that will be used.**

## 5. P3 expectations

| track | expectation | gating |
|---|---|---|
| **rocket** | **+1 Solve contingent** | on **sending** (a human action, never done), then on the reply |
| **mine** | **0 bucket** | value-invariance proof; LP-side reformulation out of emit scope |
| **camcge** | **0 bucket — Epic 5** | three-part Walras redefinition; expected MS-4; per-model-numéraire fallback |
| **fawley +Solve** | **0 bucket — Sprint 38** | `--force` survey NEGATIVE (S36 Day 11); needs a stronger continuation/reformulation |

**P3 contributes no Sprint-37 bucket.** Its product is submissions and scoping — and the single highest-value action in the whole track is *sending the two already-finalized packages*.

---

## 6. Known-Unknown dispositions

| Unknown | Verdict | Basis |
|---|---|---|
| **3.1** the rocket reply has arrived and maps to a `--force homotopy` option-set | ❌ **WRONG (refuted)** — no reply, because **the submission was never sent** | §1 — the bundle's action checkbox `- [ ] submit rocket to PATH authors` is **unchecked**; S36 Day-11 says "ready to submit"; issue #1462's only comment is the Sprint-28 bisect; no send/reply record anywhere. FINALIZED **2026-07-15**, slipped S33→S34→S35→S36. The integration staging itself remains correct and bounded (option-set → `--force homotopy`; Case-c flip BANNED), so nothing technical blocks it. |
| **3.2** the mine question is truly 0-bucket | ✅ **VERIFIED** (with the same send caveat) | §2 — the S34 value-invariance proof holds (no dual relabeling creates the missing +16000); the only non-invariant lever is an LP-side reformulation, out of emit scope ⇒ **0 bucket** either way; `x.up=inf` BANNED. **But the question was also never posed** — the same unchecked action item. Costs no KPI; batch with the rocket send. |
| **3.3** the camcge three-part Walras redefinition is reachable to MS-1 in a `/tmp` demo control | 🔶 **DESIGN-VERIFIED — control reproduces; MS-1 expected NOT reachable** | §3 — measured: emit 18 s, embedded NLP **MS-2 @ 191.7346**, MCP **MS-4**, **641 rows** (demo-reachable confirmed). The three-part redefinition is the **Epic-5 gate** and was deliberately not attempted: price-pin → MS-4, single-dual-pin → MS-4, drop-row → corrupt @ 299; 3+ sprints of variants all stayed MS-4. Running it here would re-run a refuted experiment. |
| **3.4** the per-model-numéraire fallback is the correct Epic-5 scoping | ✅ **VERIFIED — and a stale-spec defect fixed** | §4 — the fallback is correct and well-argued (per-model numéraire selection; camcge is the *only* inherent Walras singularity, DB-confirmed: irscge/lrgcge/moncge/stdcge/quocge all match). **Defect found:** the Epic-5 handoff spec still prescribed the **drop-row** transformation that Sprint 30 **refuted** (breaks the MCP dual → omega 299, MS-4), with **zero** refutation notes. **Fixed here** with a `⚠ SUPERSEDED IN PART` note carrying the refutation, the two-nullspaces diagnosis, and the current three-part formulation. |

---

**Document Status:** ✅ Complete — Sprint 37 Prep Task 9 (consultation integration prep + camcge Epic-5 scoping).
**Last Updated:** 2026-08-10 · **Owner:** Sprint 37 execution team

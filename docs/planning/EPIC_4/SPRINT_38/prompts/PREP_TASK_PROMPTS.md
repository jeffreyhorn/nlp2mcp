# Sprint 38 Prep Task Prompts (Tasks 2–11)

**Purpose:** ready-to-paste execution prompts for the Sprint-38 preparation tasks defined in `docs/planning/EPIC_4/SPRINT_38/PREP_PLAN.md`. Paste one prompt per prep task, in order. Task 1 (Create Known Unknowns List) is already ✅ COMPLETE — 28 unknowns across 8 categories.

**Standing conventions (apply to every prompt below):**
- Work on a branch **`planning/sprint38-task<Z>`** where `<Z>` is the task number (e.g. Task 4 → `planning/sprint38-task4`), branched from `main`.
- **Verify each associated Known Unknown**: update `docs/planning/EPIC_4/SPRINT_38/KNOWN_UNKNOWNS.md` — change each unknown's Verification Results line from `🔍 **Status:** INCOMPLETE` to `✅ **Status:** VERIFIED` (or `❌ **Status:** WRONG` with the correction), and add **Verified by**, **Date**, **Findings**, **Evidence**, and **Decision** lines under it (mirroring the Sprint-37 resolved-unknown format). The three code spans above are the **literal text to paste**, `**` markers included — they render as bold `Status:` in the target document.
- **A refuted unknown is a result, not a failure.** Sprint 37 had three (`3.1` the consultation was never sent; `6.1` no licensed testbed; `7.3` skip-if-absent fixtures are inert), and each one *changed the plan* for the better. Record `❌ WRONG` plainly and state what it changes.
- **Update `PREP_PLAN.md`**: set the task **Status → ✅ COMPLETE (date)**, add a **Time Spent** line, fill the **Changes** and **Result** sections (replace "To be completed"), and check off **all** acceptance criteria `- [ ]` → `- [x]` (including the "Unknowns … verified and updated in KNOWN_UNKNOWNS.md" criterion). Also update the Prep Task Overview row (prefix ✅) and the Summary/Critical-Path entry.
- **Update `CHANGELOG.md`**: add a Task-completion entry under `[Unreleased]` → `### Sprint 38 Preparation` (newest first) summarizing what was verified/produced, including any refutation.
- **Quality gate (only if `*.py` changed):** run `make typecheck && make lint && make format && make test` and confirm **all pass before committing**. Prep tasks are docs/analysis by default (docs-only → the gate is N/A); if a task touches `src/`, `tests/` or `scripts/`, the gate is **mandatory**.
- **Commit message:** `Complete Sprint 38 Prep Task <Z>: <Task Title>` (single commit; list the verified unknowns and the produced artifact in the body). **No `Co-Authored-By` line; no "Generated with Claude Code" attribution.**
- **Open a PR** with `gh pr create` (summary + the unknowns verified + the deliverables), push the branch, **then wait for reviewer comments.** Address each review comment on its own thread via `gh api repos/jeffreyhorn/nlp2mcp/pulls/<N>/comments/<id>/replies -f body="..."` — **not** as a top-level PR comment.
- **Run every verification command you write**, rather than only writing it. Broken acceptance-gate commands reached review twice in Sprint 37 (inverted `awk` exit codes, a nonexistent golden path, non-POSIX `\s`), and Task 1's own block shipped with a `^## Category` grep against a `# Category` document.

**Reference:** task definitions in `docs/planning/EPIC_4/SPRINT_38/PREP_PLAN.md` · unknowns in `docs/planning/EPIC_4/SPRINT_38/KNOWN_UNKNOWNS.md` (incl. the Task-to-Unknown mapping appendix) · sprint scope in `docs/planning/EPIC_4/PROJECT_PLAN.md` (Sprint 38, Weeks 41–42) · carryforwards in `docs/planning/EPIC_4/SPRINT_37/SPRINT_38_CARRYFORWARDS.md` · process findings in `docs/planning/EPIC_4/SPRINT_37/SPRINT_RETROSPECTIVE.md` §7.

**Recommended order (critical path):** 2 → 3 → 4 → 6 → 11, with Tasks 5, 7, 8, 9, 10 overlapping. Task 3 must precede Tasks 4 and 6 (both express their Phase-0 gate against its assertions); Task 4 must precede Task 6 (P4 changes the gate P1 runs against); Task 9 must precede Task 10 (an issue without a Phase-0 section is not eligible for the sweep). **Task 7 should be started early regardless of order** — its central question is answered by a human, and the answer needs time to arrive.

---

## Prep Task 2 Prompt — Re-Derive the Sprint-37 Baseline & Carryforward Fingerprints

On a new branch `planning/sprint38-task2` (from `main`), execute Sprint-38 Prep Task 2. **Depends on Task 1.** (Priority: **Critical**; est. 3–4h.)

**Objective:** Re-derive — **not** re-read — the Sprint-37 close baseline and every banked carryforward fingerprint on current `main`, so Sprint 38 starts from measured state rather than inherited documentation. This task exists because banked staleness was Sprint 37's most general finding, demonstrated three times including inside its own closeout.

**What to do:** (1) Recompute the KPI block directly from `data/gamslib/gamslib_status.json` over the 142 convex candidates — use **`model_id`** as the key (**not** `model_name`, which holds the description) and `mcp_solve.outcome_category` + `solution_comparison.comparison_status` as the fields; the S37 Day-0 measurement error was wrong keys returning Solve 0 / Match 0. Expect **Solve 108 · Match 94 (65 cold + 29 presolve) · Translate 135 · mi 7 · pse 6 · all-219 97**; any discrepancy is a **finding**, not a typo to smooth over. (2) Re-derive the genuine floor from the hand-partition and confirm the mechanical count still yields **65** against the recorded **76**; record the per-model reasons — this is Task 3's input for the provenance file. (3) Re-verify the **ganges cascade fingerprint**: confirm `src/` is byte-identical to the reverted state (the cascade is **not** on `main`), re-run the cold compile on both ganges and gangesx and confirm **78 / 3 / 9** `$141`/`$145`/`$149` by *specific error signature*, not a non-zero count, and confirm `prolog` is still `model_optimal` + match. (4) Re-verify the **sarf sites**: `constraint_jacobian.py:78`, `index_mapping.py:634`, `stationarity.py`, plus the six corpus-safety call sites — S37 already found this precondition stale once; re-confirm the blow-up is non-terminating **under a cap**, and do *not* full-profile (Task 5 owns that). (5) Re-verify the golden/gate inventory: **170** discovered, **7** allowlisted, **163** in-scope, **17** presolve, `--min-scope 170`, `MAX_WORKERS = 3`. (6) Record every derived figure **with the SHA it was measured at**.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_38/BASELINE_RECONFIRMATION.md` — every figure with the SHA it was measured at
- A confirmed-or-corrected KPI block (108 / 94 / 76 / 135 / mi 7 / pse 6 / 97)
- Fingerprint verdicts for the ganges cascade, the sarf sites, and the golden/gate inventory
- A per-model floor-provenance draft (input to Task 3's P6c design)
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns **1.1, 2.1, 4.1**

**Unknowns to verify** (in `KNOWN_UNKNOWNS.md`, set each to **✅ VERIFIED** or **❌ WRONG**, and add **Verified by / Date / Findings / Evidence / Decision**)**:** **1.1** (the four-fix cascade still takes ganges AND gangesx to `rc=0`), **2.1** (the three sarf materialization sites and six call sites are still where the design says), **4.1** (all 36 presolve goldens are reproducible from a clean re-solve — run the re-solve **from a scratch directory**, and **never `git add -A` afterward**; the S37 Day-9 incident swept 20 runtime artifacts including `decis.lic` plus 36 unintended goldens into a commit).

Then update `PREP_PLAN.md` (Task 2 → ✅ COMPLETE, Changes/Result, all ACs), update `CHANGELOG.md`, run the quality gate **only if** `*.py` changed (expected docs/analysis-only), commit as `Complete Sprint 38 Prep Task 2: Re-Derive the Sprint-37 Baseline & Carryforward Fingerprints`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 3 Prompt — Measurement-Integrity Design: Gate Scope, Floor Provenance & Re-Anchoring (P6)

On a new branch `planning/sprint38-task3` (from `main`), execute Sprint-38 Prep Task 3. **Depends on Tasks 1, 2.** (Priority: **Critical**; est. 4–5h.)

**Objective:** Design the four P6 deliverables — the derived-figure helper, the two gate-scope assertions, the provenance-carrying floor tracker, and the DB re-anchor — so they can be implemented directly in the sprint, and so **every other priority's acceptance gate can be expressed against them**. This task sits on the critical path *ahead* of the deep tracks because P6 defines how Sprint 38 measures itself.

**What to do:** (1) **6a — the derived-figure helper:** design a `scripts/sprint_audit/` entry point emitting the current KPI block on demand, in both a human-readable and a machine-readable form the day-prompt templates can embed; specify the rule that any quoted figure **carries its measurement SHA**. (2) **6b — the two gate-scope assertions:** for `--resolve-changed`, assert the selection is non-empty and covers the expected change set, exiting non-zero when the git-diff selection is empty but uncommitted goldens exist (the S37 false GO was *silent*); for `leak-check`, distinguish "clean" from "nothing to check" — a `NO-OP` must be a **non-zero exit or an explicit `UNVERIFIED` verdict**, never mistakable for a pass. Specify exact failure messages and name the false-positive modes. (3) **6c — the floor provenance file:** schema with per-model `model_id`, limb (`cold-match` | `fix-changed-cold-emit`), the sprint it began counting, and the evidence; it must reproduce **76** exactly from Task 2's draft partition, and must **fail loudly** if its total diverges from the hand-partition rather than reporting its own number. (4) **6d — the re-anchor:** choose and justify the commit (candidate: the S37 close `8cffec29`), compare what `--resolve-changed` selects there versus at `78ceaead`, and record what re-anchoring costs (S34–S37 drift stops being re-checked every run).

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_38/MEASUREMENT_INTEGRITY_DESIGN.md` covering all four sub-deliverables
- The derived-figure helper's output contract (human + machine forms)
- Exact assertion semantics and failure messages for both gate-narrowing modes, with false-positive modes named
- The floor-provenance schema, validated to reproduce **76** from Task 2's partition
- The re-anchor commit chosen, with what it selects and what re-anchoring costs
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns **6.1, 6.2, 6.3, 6.4**

**Unknowns to verify** (in `KNOWN_UNKNOWNS.md`, set each to **✅ VERIFIED** or **❌ WRONG**, and add **Verified by / Date / Findings / Evidence / Decision**)**:** **6.1** (both gate-narrowing modes reproduce live — **reproduce them, do not merely describe them**; this is the fail-before evidence), **6.2** (a provenance file reproduces the floor of 76 exactly — any model that cannot be attributed is a finding: either the floor is wrong or the provenance is incomplete), **6.3** (the S37 close is the correct re-anchor and its cost is known), **6.4** (the assertions have no false-positive mode that would get the guard disabled in practice).

Then update `PREP_PLAN.md` (Task 3 → ✅ COMPLETE, Changes/Result, all ACs), update `CHANGELOG.md`, **run the quality gate if the design prototypes anything under `scripts/`** (a design-only pass is docs-only; any `scripts/` edit makes the gate mandatory), commit as `Complete Sprint 38 Prep Task 3: Measurement-Integrity Design — Gate Scope, Floor Provenance & Re-Anchoring`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 4 Prompt — ganges P1: `$149` Rebind-Predicate Design & Leak-Surface Analysis

On a new branch `planning/sprint38-task4` (from `main`), execute Sprint-38 Prep Task 4. **Depends on Tasks 1, 2, 3.** (Priority: **Critical**; est. 5–7h.)

**Objective:** Design the narrowed `$149` rebind predicate that keeps ganges and gangesx at `rc=0` while leaving `prolog` byte-identical, and analyse the leak surface well enough that the sprint **implements a design rather than searching for one**.

**What to do:** (1) **Characterise the `prolog` over-fire precisely** — reproduce the drift, capture which rebind fires on which expression shape, and establish what distinguishes `prolog`'s bound from ganges' **structurally, not by name**. (2) **Draft the positive requirement.** Follow the Sprint-37 fawley pattern: two narrowings failed because they only *subtracted* exclusions; the third succeeded by **adding a positive requirement** about what must be true of the genuine case. State what must be true of a *genuinely-free `prod` bound* (#1668 direction 2, which is closer to the original intent than direction 1), express it in terms available at the emit site, and identify the IR/AST predicates needed. **Explicitly reject any name-based or domain-only discriminator** — that is the S35–S37 leak pattern. (3) **Map the leak surface full-corpus** — identify every model whose emit traverses the same rebind path; this must be *derived*, not guessed, because Sprint 36's 6-model cohort missed all three markov leaks. (4) **Specify the Phase-0 acceptance gate**: per-model (ganges AND gangesx) emit → compile → count `$NNN` (assert 0) → solve cold AND presolve with `modelstat` asserted → bucket; `make check-goldens` full-corpus showing **only ganges/gangesx drift with `prolog` byte-identical**; determinism ×3; the 335s slow-emit goldens on a nightly regen slot — all expressed against Task 3's gate-scope assertions. (5) **Define the REPLAN exit** and what it banks.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_38/GANGES_REBIND_PREDICATE_DESIGN.md`
- A precise structural characterisation of the `prolog` over-fire
- The **positive requirement** the narrowed predicate asserts, with the IR predicates it needs
- The full-corpus leak surface (which models traverse the rebind path)
- The Phase-0 acceptance gate, expressed against Task 3's assertions
- A stated REPLAN exit and what it banks
- **A restated bucket expectation of 0** (lateral pse → mi), so the sprint cannot drift back to "+2 or 0"
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns **1.2, 1.3, 1.4, 1.5**

**Unknowns to verify** (in `KNOWN_UNKNOWNS.md`, set each to **✅ VERIFIED** or **❌ WRONG**, and add **Verified by / Date / Findings / Evidence / Decision**)**:** **1.2** (a positive requirement separates ganges from `prolog` while preserving `rc=0` — the deliverable), **1.3** (the narrowed predicate passes the full-corpus 163-golden gate with `prolog` byte-identical — assert scope explicitly so a silently narrowed sweep cannot masquerade as a pass), **1.4** (the bucket really is 0, and **no gate or report treats a rise in `model_infeasible` as a regression** — grep the acceptance criteria, KPI table and gate scripts for monotonicity assumptions; mi 7 → 9 is expected and lateral), **1.5** (the general `$149` fix unblocks the `$149` half of dinam/indus/turkpow/clearlak — feed the result to Task 10's candidate pool).

Then update `PREP_PLAN.md` (Task 4 → ✅ COMPLETE, Changes/Result, all ACs), update `CHANGELOG.md`, run the quality gate **only if** `*.py` changed (a scratch predicate must be **reverted** — `src/` byte-identical to `main` at commit time, per the S30–S37 control-first discipline), commit as `Complete Sprint 38 Prep Task 4: ganges P1 — $149 Rebind-Predicate Design & Leak-Surface Analysis`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 5 Prompt — sarf P2: O(active) Re-Architecture Design Refresh & Atomicity Plan

On a new branch `planning/sprint38-task5` (from `main`), execute Sprint-38 Prep Task 5. **Depends on Tasks 1, 2.** (Priority: **Critical**; est. 5–7h.)

**Objective:** Refresh the sarf re-architecture design against the Sprint-37 profile, and produce an atomicity plan detailed enough that the 20–28h implementation is **a build rather than an investigation**. This is the sprint's only KPI mover (+1 Translate → 136) and its largest single cost.

**What to do:** (1) **Re-validate the design premise against the profile.** The banked design blamed "369K columns"; the S37 profile showed the columns are cheap and *differentiating each one* is not — `compute_constraint_jacobian` is **137 s of a 180 s cap**, with ~**762K** top-level `differentiate_expr` calls against the **398** columns that matter. Confirm the O(active) short-circuit actually removes that differentiation volume rather than only skipping enumeration, and estimate the post-re-arch call count. (2) **Specify the atomic change set:** the 2-D constraint gate + the S1/S2/S3 short-circuit + the parametric `stat_task` + `task.fx`, as **one unit** — a partial landing leaves multipliers with no stationarity coupling, i.e. an inconsistent MCP, and is explicitly a REPLAN rather than progress. Cover each of the three sites (**S1 `constraint_jacobian.py:78`, S2 `index_mapping.py:634`, S3 `stationarity.py`**) with what changes, its guard, and its fallback for every other model; enumerate the **six** corpus-safety call sites with their unperturbed-proof. (3) **Design the verification strategy around the two gate peculiarities:** sarf has **no golden**, so `make leak-check MODEL=sarf` reports `NO-OP` and fails for a non-correctness reason — the real gate is `make check-goldens` (zero drift ×163) **plus sarf newly producing a golden**; and **sarf cannot be its own fixture** because at 369,024 columns the fail-before state does not terminate, so design a **corpus-free surrogate** with a terminating fail-before state. (4) **Specify the Phase-0 gate (PR20):** single-digit seconds; `stat_task` matching the banked 7-term derivation with **symbolic** multiplier indices (`grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` empty); byte-stable golden; determinism ×3. (5) **Define the REPLAN exit with a named trigger day** — the plan calls for taking it **early rather than nursing it**.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_38/SARF_REARCH_DESIGN.md`
- A profile-validated premise: the short-circuit removes differentiation volume, with an estimated post-re-arch call count
- The atomic change set, site by site, with the guard and fallback for each
- The six corpus-safety call sites enumerated with their unperturbed-proof
- A **surrogate fixture** design (since sarf cannot be its own fixture)
- The golden-creation step and its interaction with Task 6's scope change
- The Phase-0 gate (PR20) and a REPLAN exit with a named trigger day
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns **2.2, 2.3, 2.4, 2.5**

**Unknowns to verify** (in `KNOWN_UNKNOWNS.md`, set each to **✅ VERIFIED** or **❌ WRONG**, and add **Verified by / Date / Findings / Evidence / Decision**)**:** **2.2** (the short-circuit removes `differentiate_expr` volume, not merely column enumeration — the premise a 20–28h atomic build rests on), **2.3** (the re-arch actually reaches single-digit seconds, i.e. the ~66× reduction; **pre-register a fallback threshold** so a 40s result is a decision, not an argument), **2.4** (a corpus-free surrogate fixture exists with a genuine fail-before state — a skip-if-absent fixture is inert in CI and guards nothing), **2.5** (sarf's new golden passes determinism ×3, and both P2/P4 landing orders leave `--min-scope` correct).

**Do NOT re-attempt the memoization.** Sprint 37 built it, measured **~5%** against the **~66×** needed, and reverted it; it is recorded in `ISSUE_1385` precisely so a future effort does not retry it as a shortcut.

Then update `PREP_PLAN.md` (Task 5 → ✅ COMPLETE, Changes/Result, all ACs), update `CHANGELOG.md`, run the quality gate **only if** `*.py` changed (any prototype must be reverted before commit), commit as `Complete Sprint 38 Prep Task 5: sarf P2 — O(active) Re-Architecture Design Refresh & Atomicity Plan`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 6 Prompt — Presolve-Golden Adoption Plan & Runtime Impact (P4)

On a new branch `planning/sprint38-task6` (from `main`), execute Sprint-38 Prep Task 6. **Depends on Tasks 1, 2, 3, 4.** (Priority: **High**; est. 3–4h.)

**Objective:** Plan the **deliberate, reviewed** adoption of the 36 presolve goldens — including the per-model review protocol, the `--min-scope` change, and the leak-gate runtime impact at the enlarged scope. The golden corpus is **153 cold vs 17 presolve** while `model_optimal_presolve` accounts for **29 of the 94 matches**, so the presolve emit path is materially under-covered.

**What to do:** (1) **Inventory and reproduce the 36** — regenerate from a clean re-solve (**from a scratch directory; never `git add -A` afterward**) and confirm all 36 reappear identically; list them by model with the outcome that produced each. Any non-reproducible golden is **not adoptable**. (2) **Design the per-model review protocol:** what "reviewed" means concretely — each golden checked against its model's **expected** presolve emit, not merely against the run that produced it; a triage order (models whose presolve path is load-bearing for a match first); a rejection criterion and where an exclusion's justification is recorded. (3) **Measure the runtime impact:** time `make check-goldens` at 163 in-scope today, project 199, and confirm the 3-worker default still yields **0 timeouts** — Sprint 37 measured 4/2/0 timeouts at 6 workers before fixing the default. If the projection is marginal, choose the mitigation (worker count, nightly split) **in prep**. (4) **Specify the `--min-scope` change:** 170 → 206 discovered, applied **atomically with the adoption** so the assertion never lags the corpus; confirm it still fires on **discovery**, before allowlist narrowing. (5) **Sequence against P1** — P1's full-corpus gate run must complete at the *old* scope first; specify the handoff.

**The hazard this task exists to prevent:** adopting these the way Sprint 37 accidentally did would expand what `check-goldens` sweeps (170 → 206) **using references generated by that very run** — a self-certifying reference set. Generating references and committing them in one unreviewed step is how a gate stops being a gate.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_38/PRESOLVE_GOLDEN_ADOPTION_PLAN.md`
- The 36 goldens inventoried by model, with reproducibility confirmed
- A per-model review protocol with triage order and rejection criterion
- Measured sweep runtime at 163 and a projection at 199, with a mitigation if timeouts appear
- The `--min-scope` 170 → 206 change specified, applied atomically with adoption
- The P1 → P4 sequencing handoff
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns **4.2, 4.3, 4.4**

**Unknowns to verify** (in `KNOWN_UNKNOWNS.md`, set each to **✅ VERIFIED** or **❌ WRONG**, and add **Verified by / Date / Findings / Evidence / Decision**)**:** **4.2** (each golden matches its model's **expected** presolve emit rather than the generating run — define the protocol first, then pilot it on a subset; watch for any golden that would freeze a *bug* into the reference set), **4.3** (the sweep runtime at ~199 in-scope still gives 0 timeouts at 3 workers — golden-staleness is a **required status check**, so a timing-out gate blocks every PR, not just P4's), **4.4** (`--min-scope` needs 170 → 206 and still fires on discovery; consider **deriving** the value from the corpus rather than hard-coding it, per the same "derive, don't quote" principle as P6a).

Then update `PREP_PLAN.md` (Task 6 → ✅ COMPLETE, Changes/Result, all ACs), update `CHANGELOG.md`, run the quality gate **only if** `*.py` changed, commit as `Complete Sprint 38 Prep Task 6: Presolve-Golden Adoption Plan & Runtime Impact`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 7 Prompt — Consultation Ownership Decision Package (P3)

On a new branch `planning/sprint38-task7` (from `main`), execute Sprint-38 Prep Task 7. **Depends on Task 1.** (Priority: **High**; est. 2–3h.) **Start this early regardless of task order — its central question is answered by a human, and the answer needs time to arrive.**

**Objective:** Prepare everything needed for the **Day-0 send-or-strike decision**, so the decision itself takes minutes and the outcome is executable either way.

**This is not an engineering task, and that is the point.** The rocket/mine consultation bundle has been **FINALIZED since 2026-07-15** and has slipped **S33 → S34 → S35 → S36 → S37** with its one *action* checkbox unchecked. Sprint 37 Day 0 established why: **the bundle names no recipient, address, or channel**, so it was never executable by an execution agent. Carrying it a sixth time without an owner converts a task into a permanent fixture and **quietly inflates every sprint's projected upside** — rocket's +1 Solve and fawley's +Solve have both been counted as reachable while the gating action went undone.

**What to do:** (1) **Assemble the send package** — confirm the bundle is complete and current (question set, reproducible cases, ruled-out-lever survey), draft the covering message leaving **only recipient and channel blank**, and identify what a reply would need to contain to be actionable. (2) **Cost the strike branch** — enumerate exactly what is removed from projections (rocket +1 Solve, fawley +Solve) and any downstream dependency, noting that `PROJECT_PLAN.md` now records **Sprint 39's antecedent as Sprint 38 P3**; draft the reclassification wording so the strike is executable same-day. (3) **Prepare the decision brief** — one page: what is being asked, the two branches, what each costs, and the fact that this is the fifth carry. **Name the specific question the human must answer: who receives this, and by what channel.** (4) **Specify the tracking record** — if sent, where the send is recorded and how a reply is tracked (issue #1462 currently carries only the Sprint-28 bisect comment).

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_38/CONSULTATION_DECISION_BRIEF.md` — one page, two branches, costed
- A send package complete except for recipient and channel
- The strike branch's reclassification wording, executable same-day
- The tracking-record specification for a send
- **An explicit statement of the single question a human must answer**
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns **3.1, 3.2, 3.3**

**Unknowns to verify** (in `KNOWN_UNKNOWNS.md`, set each to **✅ VERIFIED** or **❌ WRONG**, and add **Verified by / Date / Findings / Evidence / Decision**)**:** **3.1** (who is the recipient, and by what channel — **this is answered by a person, not an experiment**; the verification is that a recipient and channel are written down, or that the strike decision is. If unanswered by Day 0, the **strike branch executes by default** — a sixth carry is not an acceptable outcome, and the unknown should be recorded ❌ WRONG against the assumption that an owner would be named), **3.2** (what the strike actually costs, and whether Sprint 39 — "PATH Author Consultation & Solution Forcing" — remains viable if the consultation was never sent), **3.3** (would a reply be actionable as-is — are the reproducible cases still reproducible under **GAMS 54.2.1**, given the corpus was re-pinned *after* the bundle was written?).

Then update `PREP_PLAN.md` (Task 7 → ✅ COMPLETE, Changes/Result, all ACs), update `CHANGELOG.md`, run the quality gate **only if** `*.py` changed (expected docs-only), commit as `Complete Sprint 38 Prep Task 7: Consultation Ownership Decision Package`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 8 Prompt — camcge Epic-5 Handoff Scoping + turkey Testbed Procurement (P5)

On a new branch `planning/sprint38-task8` (from `main`), execute Sprint-38 Prep Task 8. **Depends on Tasks 1, 2.** (Priority: **Medium**; est. 3–4h.)

**Objective:** Scope the camcge Epic-5 handoff so **Epic 5 starts from Sprint 32–37's refutations rather than repeating them**, and determine whether a licensed >1000-row GAMS-54 environment is obtainable for turkey.

**What to do:** (1) **Assemble the camcge refutation record** — every Walras variant tried, its sprint, its outcome, and why it fails structurally: price-pin → MS-4, single-dual-pin → MS-4, drop-row → corrupt @ omega 299. State the **two-nullspaces diagnosis** reusably (a numéraire fixes the price-scaling ray, not the row-redundancy nullspace), and record the **BANNED** list with reasons — **drop-row explicitly**, because it is primal-correct and therefore tempting. Baseline from the S37 Day-10 control (GAMS 54.2.1): emit **19 s**, **641 single equations / 641 variables**, embedded NLP **MS-2 @ omega 191.7346**, `mcp_model` **MS-4 Infeasible** — the MCP is MS-4 against a *correct* NLP optimum, i.e. structural rank-deficiency, **not an emit defect**. (2) **Scope the per-model-numéraire fallback** for Epic 5 — what it would implement, and what it does and does not buy; cross-reference `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md`. (3) **Investigate turkey testbed options concretely** — is a licence covering >1000 nonlinear rows obtainable, at what cost, by when? Consider academic licences, hosted runners, time-limited evaluations, or a reduced instance preserving the failure mode. turkey's MCP is **3,866 rows** against the demo **1000-row** limit. (4) **If negative, draft the wording that reclassifies turkey's +1 as blocked rather than pending** — it has been carried as "pending a testbed" since Sprint 35 and was already refuted once in Sprint 37 prep. (5) **If both branches are negative, state P5's deliverable honestly as documentation** rather than implying bucket movement.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_38/CAMCGE_EPIC5_HANDOFF.md` — refutation record + two-nullspaces diagnosis + BANNED list
- The per-model-numéraire fallback scoped for Epic 5
- A concrete turkey testbed determination: obtainable (with cost/date) or blocked
- Reclassification wording if turkey remains blocked
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns **5.1, 5.2, 5.3**

**Unknowns to verify** (in `KNOWN_UNKNOWNS.md`, set each to **✅ VERIFIED** or **❌ WRONG**, and add **Verified by / Date / Findings / Evidence / Decision**)**:** **5.1** (is a licensed >1000-row GAMS-54 environment obtainable at all — **this is procurement, not engineering, and may require a human**; a fourth carry of phantom upside is the failure mode to avoid), **5.2** (does the Epic-5 handoff need anything not already measured — audit the existing scoping doc against the S32–S37 refutation history and list the gaps), **5.3** (is the per-model-numéraire fallback still the right recommendation, given nothing since Sprint 32 has changed the two-nullspaces analysis).

**Do NOT re-run the three-part Walras redefinition.** 3+ sprints of variants have all stayed MS-4; running it here would re-run a refuted experiment.

Then update `PREP_PLAN.md` (Task 8 → ✅ COMPLETE, Changes/Result, all ACs), update `CHANGELOG.md`, run the quality gate **only if** `*.py` changed (expected docs-only), commit as `Complete Sprint 38 Prep Task 8: camcge Epic-5 Handoff Scoping + turkey Testbed Procurement`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 9 Prompt — Phase-0 Compliance Survey over the Open Backlog (P7)

On a new branch `planning/sprint38-task9` (from `main`), execute Sprint-38 Prep Task 9. **Depends on Task 1.** (Priority: **Medium**; est. 3–4h.) **Must precede Task 10** — an issue without a Phase-0 section is not implementable, so this survey determines which backlog candidates are even eligible.

**Objective:** Survey the open issue backlog for missing `## Phase 0: Acceptance Gate` sections and produce the catalog that P7 backfills.

**Why this matters:** two long-open items were found in Sprint 37 to have **never had a Phase-0 section** — `$66`/#1289 (open since **Sprint 25**) and sarf/#1385 — and both were discovered only when a sprint tried to *budget* them. An issue without a Phase-0 gate is not schedulable work; it is an idea. Finding that out mid-sprint wastes the slot.

**What to do:** (1) **Enumerate the open backlog** — open issues a future sprint might plausibly schedule (emit/AD/KKT-touching), cross-referenced against `docs/issues/ISSUE_*.md`. (2) **Run the compliance check** using `scripts/sprint_audit/check_phase0_doc.py`'s own semantics — "rule C": the four canonical `###` subsections present, prefix-matched, extras permitted. Classify three ways: **compliant / has doc but no Phase-0 section / no doc at all**. (3) **Prioritise the backfill** by likelihood of being scheduled — anything in Sprint 38's own P8 candidate pool ranks first. (4) **Confirm `$66`/#1289's authored gate is complete**, or finish it. (5) **Produce the catalog** as a table Task 10 can filter on and P7 can work through in the sprint.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_38/PHASE0_COMPLIANCE_CATALOG.md`
- A three-way classification of the open backlog (compliant / doc-without-gate / no doc)
- A prioritised backfill list, with Sprint 38's P8 candidates ranked first
- Confirmation that `$66`/#1289's gate is complete
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns **7.1, 7.2**

**Unknowns to verify** (in `KNOWN_UNKNOWNS.md`, set each to **✅ VERIFIED** or **❌ WRONG**, and add **Verified by / Date / Findings / Evidence / Decision**)**:** **7.1** (how many open backlog issues lack a Phase-0 section — the count sizes P7's 8–10h; check whether `check_phase0_doc.py` classifies consistently with a manual read, and whether any *closed* issues show the problem is historical rather than current), **7.2** (is `$66`/#1289's authored gate complete — all four canonical subsections, passes the gate script, reflects that `$66` is reachable only after the cascade lands, and carries the `ac(i+2,r)` match-correctness risk).

Then update `PREP_PLAN.md` (Task 9 → ✅ COMPLETE, Changes/Result, all ACs), update `CHANGELOG.md`, run the quality gate **only if** `*.py` changed (running the existing gate script is not a change; editing it is), commit as `Complete Sprint 38 Prep Task 9: Phase-0 Compliance Survey over the Open Backlog`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 10 Prompt — Emit-Backlog Candidate Catalog & Selection-Rule Dry Run (P8)

On a new branch `planning/sprint38-task10` (from `main`), execute Sprint-38 Prep Task 10. **Depends on Tasks 1, 2, 9.** (Priority: **Medium**; est. 3–4h.)

**Objective:** Build the candidate catalog for the P8 backlog sweep and **dry-run the pre-registered selection rule** against it, so the sprint's slack absorber cannot drift into an open-ended diagnosis effort.

**Why this matters:** P8 exists because Sprint 38 has **no floor-moving lever**, and the honest response is to spend the slack on adjacent backlog rather than inflating the deep tracks. But an under-specified sweep is exactly how a sprint loses a week. The rule is pre-registered: **a model enters the sweep only if it has a reproduced fingerprint AND a named fix surface**; anything requiring a new diagnosis is banked, not started.

**What to do:** (1) **Assemble the candidate pool** — query the DB for `path_solve_terminated`, `path_syntax_error` and `model_infeasible` models outside the deep tracks (`ganges`, `gangesx`, `sarf`, `camcge`, `turkey`, `rocket`, `mine`, `fawley`, `markov`), and cross-reference each against its issue doc and Task 9's compliance catalog. (2) **Apply the selection rule** — for each candidate determine whether there is a **reproduced** fingerprint and a **named** fix surface; reproduce fingerprints for the top candidates, **asserting the specific mechanism, not a grep hit**. Record rejections with reasons (new diagnosis required / structural / no Phase-0 doc). (3) **Exclude known structural blockers** unless P1's `$149` fix demonstrably unblocks their half: turkpow (ragged `Table mdatat`), clearlak (dynamic sets). (4) **Confirm P8 has ≥2 eligible candidates** — if fewer survive, **say so and recommend where the 12–16h goes instead**; that is a prep finding, not a mid-sprint discovery.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_38/BACKLOG_CANDIDATE_CATALOG.md`
- The candidate pool with each model's outcome category and issue doc
- Selection-rule verdicts: eligible / rejected, with the rejection reason
- Reproduced fingerprints for the top candidates, asserting mechanism not pattern
- A stated finding on whether P8 has ≥2 eligible candidates, and a budget recommendation if not
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns **8.1, 8.2**

**Unknowns to verify** (in `KNOWN_UNKNOWNS.md`, set each to **✅ VERIFIED** or **❌ WRONG**, and add **Verified by / Date / Findings / Evidence / Decision**)**:** **8.1** (does P8 have ≥2 candidates satisfying the rule — consume Unknown **1.5**'s result from Task 4 and **7.1**'s from Task 9), **8.2** (can a fingerprint match be a false positive — **yes, and the rule must guard against it**: Sprint 37 Day 0 recorded a helper matching the `$141` pattern that came from an unrelated cesam fix. Derive the operational criterion for "reproduced" versus "pattern-matched" and apply it to every catalog entry; each candidate should carry its reproduction command).

Then update `PREP_PLAN.md` (Task 10 → ✅ COMPLETE, Changes/Result, all ACs), update `CHANGELOG.md`, run the quality gate **only if** `*.py` changed (expected docs/analysis-only), commit as `Complete Sprint 38 Prep Task 10: Emit-Backlog Candidate Catalog & Selection-Rule Dry Run`, push, open a PR, and wait for reviewer comments.

---

## Prep Task 11 Prompt — Plan Sprint 38 Detailed Schedule

On a new branch `planning/sprint38-task11` (from `main`), execute Sprint-38 Prep Task 11. **Depends on all tasks (1–10).** (Priority: **Critical**; est. 3–4h.)

**Objective:** Produce `SPRINT_38/PLAN.md` and `SPRINT_38/prompts/PLAN_PROMPTS.md` — a Day-0-through-Day-13 schedule with per-priority budgets, checkpoints, REPLAN exits, and a Day-0 GO/NO-GO gate — consuming the designs and findings from Tasks 1–10.

**What to do:** (1) **Build the day-by-day schedule** — Day 0 (baseline re-confirm + GO/NO-GO + **the P3 decision**), Days 1–13 across the eight priorities, honouring **P1 before P4** (P4 changes what `check-goldens` sweeps); front-load P1 and P2 (the two that produce landings); name P2's REPLAN trigger day per Task 5; checkpoints at Day 5 and Day 10; final retest Day 13. **No day exceeds 12h** — verify by mechanical count, not by eye. (2) **Write the per-day prompts** in the S37 format, **deriving figures at execution time rather than quoting them** (P6a) — this is the sprint whose retrospective demanded it. (3) **Define REPLAN exits and the Day-0 GO/NO-GO gate** from Tasks 4, 5, 6, 8, 10 and Task 2's re-derivation. (4) **Verify the budget mechanically** — sum per-day hours; assert ≤12h/day and <168h total (per-priority: P1 18–24h · P2 20–28h · P3 4–6h · P4 10–14h · P5 10–14h · P6 14–18h · P7 8–10h · P8 12–16h · retest 4h = 100–134h). (5) **Record the pre-registered close rules** — the three-gate firm-landing-vs-carryforward rule, the **mi-may-rise-to-9 reporting rule**, and the floor-from-provenance rule.

**Two constraints the schedule must honour:**
- **Day 13's prompt must explicitly name `SPRINT_39_CARRYFORWARDS.md`** alongside SPRINT_LOG, SPRINT_RETROSPECTIVE and the SUMMARY row. Sprint 37's Day-13 prompt listed only the first three, so the carryforwards file was missed at close and had to be added afterward.
- **The schedule must NOT reinstate a genuine-floor target.** Sprint 38 is deliberately not floor-targeted; naming the absence of a floor lever is the mitigation that prevents the pressure which produced Sprint 36's reverted landing attempt.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_38/PLAN.md` — Day 0 + Days 1–13, per-priority budgets, checkpoints, REPLAN exits, GO/NO-GO gate
- `docs/planning/EPIC_4/SPRINT_38/prompts/PLAN_PROMPTS.md` — one prompt per day, figures derived not quoted
- A mechanical budget verification (≤12h/day, <168h total)
- Pre-registered close rules, including the mi-rise and floor-provenance reporting rules

**Unknowns** (none owned exclusively — Task 11 **integrates all 28**; confirm each is **✅ VERIFIED** or **❌ WRONG** in `KNOWN_UNKNOWNS.md` with its **Findings / Evidence / Decision** filled)**:** Confirm every unknown is ✅ VERIFIED or ❌ WRONG (none left 🔍 INCOMPLETE), schedule any 🔶 DESIGN-VERIFIED unknown into the sprint day that closes it, and derive the Day-0 GO/NO-GO conditions from the Critical unknowns. **If any Critical unknown is still INCOMPLETE, that is a NO-GO condition** — say so rather than scheduling around it.

Then update `PREP_PLAN.md` (Task 11 → ✅ COMPLETE, Changes/Result, all ACs) and the prep Success Criteria checklist, update `CHANGELOG.md` with a **prep-cycle completion summary** (all 11 tasks, the unknown resolution tally, and any refutations that changed the plan), run the quality gate **only if** `*.py` changed, commit as `Complete Sprint 38 Prep Task 11: Plan Sprint 38 Detailed Schedule`, push, open a PR, and wait for reviewer comments.

---

**END OF SPRINT 38 PREP TASK PROMPTS**

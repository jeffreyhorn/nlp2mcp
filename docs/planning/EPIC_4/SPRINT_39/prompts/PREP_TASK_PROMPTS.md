# Sprint 39 Prep Task Prompts (Tasks 2–12)

**Purpose:** ready-to-paste execution prompts for the Sprint-39 preparation tasks defined in `docs/planning/EPIC_4/SPRINT_39/PREP_PLAN.md`. Paste one prompt per prep task. Task 1 (Create Known Unknowns List) is already ✅ **COMPLETE** — **30 unknowns across 10 categories, 40.0 research hours** (⚠ over the 28–36 h target — the 29.0 h figure published at creation was wrong; see `PREP_PLAN.md` correction 1).

**Standing conventions (apply to every prompt below):**

- Work on a branch **`planning/sprint39-task<Z>`** where `<Z>` is the task number (e.g. Task 4 → `planning/sprint39-task4`), branched from `main`.
- **Verify each associated Known Unknown**: update `docs/planning/EPIC_4/SPRINT_39/KNOWN_UNKNOWNS.md` — change each unknown's Verification Results line from `🔍 **Status:** INCOMPLETE` to `✅ **Status:** VERIFIED` (or `❌ **Status:** WRONG` with the correction, or `🔶 **Status:** PARTIALLY WRONG`), and add **Verified by**, **Date**, **Measured at** (the commit), **Findings**, **Evidence**, and **Decision** lines beneath it. The code spans above are the **literal text to paste**, `**` markers included — they render as a bold `Status:` in the target document.
- **A refuted unknown is a result, not a failure.** Sprint 38's prep refuted **6 of 28** outright and partially refuted 3 more — a 32 % refutation rate on assumptions that had already survived a planning pass — and every refutation *improved* the plan. Record `❌ WRONG` plainly and state what it changes.
- **Update `PREP_PLAN.md`**: set the task **Status → ✅ COMPLETE (date)**, add a **Time Spent** line, fill the **Changes** and **Result** sections (replacing "*To be completed*"), and check off **all** acceptance criteria `- [ ]` → `- [x]`, including the "Unknowns … verified and updated in KNOWN_UNKNOWNS.md" criterion. Also prefix the Prep Task Overview row with ✅.
- **Update `CHANGELOG.md`**: add an entry under `[Unreleased]` → `### Sprint 39 Prep` (newest first) summarising what was verified or produced, **including any refutation**.
- **Quality gate:** run **`make typecheck && make lint && make format && make test`** and confirm **all pass before committing** — **mandatory if any `*.py` changed** (`src/`, `tests/` or `scripts/`). Prep tasks are docs/analysis by default; if nothing under those paths changed, state "docs only — quality gate N/A" in the commit body rather than skipping it silently.
- **Commit message:** `Complete Sprint 39 Prep Task <Z>: <Task Title>` — a single commit, with the verified unknowns and the produced artifacts listed in the body. **No `Co-Authored-By` line; no "Generated with Claude Code" attribution** in the commit or the PR body.
- **Open a PR** with `gh pr create` (summary + unknowns verified + deliverables), push the branch, **then wait for reviewer comments.** Address each review comment **on its own thread** via `gh api repos/jeffreyhorn/nlp2mcp/pulls/<N>/comments/<id>/replies -f body="..."` — **not** as a top-level PR comment.
- **Run every verification command you write**, rather than only writing it. Sprint 38 shipped broken acceptance-gate commands to review more than once; `grep -c` counts *lines, not occurrences*, and `echo "exit=$?"` after a pipe reports the **last** command's status.
- **Run all GAMS from a scratch directory.** Corpus sources write artifacts to `cwd` — four models do `execute_unload "result.gdx"`. **Never `git add -A` after a GAMS run in the repo root.**
- **Read counts from GAMS's own line** (`**** ... EXECERROR = n`, `**** N ERROR(S)`, `MODEL STATUS`), never from a marker count, which undercounts under listing truncation. **Anchor `^****` when grepping a `.lst`** — it contains echoed source too.
- **Derive figures; do not recall them.** Anything quoted carries the commit it was measured at. This applies to *counts of findings* as much as to KPIs — Sprint 38's closeout mis-stated its own finding count from memory and review caught it.

**Reference:** task definitions in `docs/planning/EPIC_4/SPRINT_39/PREP_PLAN.md` · unknowns in `docs/planning/EPIC_4/SPRINT_39/KNOWN_UNKNOWNS.md` (incl. the Task-to-Unknown mapping appendix) · sprint scope in `docs/planning/EPIC_4/PROJECT_PLAN.md` (Sprint 39, Weeks 43–44) · carryforwards in `docs/planning/EPIC_4/SPRINT_38/SPRINT_39_CARRYFORWARDS.md` · process findings in `docs/planning/EPIC_4/SPRINT_38/SPRINT_RETROSPECTIVE.md` §§2–4, 7 · Epic goals in `docs/planning/EPIC_4/GOALS.md`.

**Recommended order (critical path):** **2 → {3, 4, 5, 6} → 12**, with Tasks 7, 8, 9, 10 overlapping. **Task 2 gates everything technical** — four priorities rest on fingerprints nobody has re-measured. **Task 7 should precede Task 11** (the catalog cross-check consumes the survey) and is worth starting early because Task 4 wants its output for Unknown 2.3. **Task 9 is date-sensitive**, not effort-sensitive: its central question (has a reply arrived?) is answered by other people, so start it early and revisit.

**Baseline at Sprint-38 close (`9ab2c0c3`) — re-derive, do not copy:** Solve **111** · Match **96** (65 cold + 31 presolve) · Translate **135** · Parse **142**/142 · `path_solve_terminated` **0** · `path_solve_license` **11** · mi **7** · pse **6** · all-219 **99** · genuine floor **73** (provenance file) · leak-gate scope **186** (7 allowlisted).

> **Anchor note.** Sprint 38's own close docs cite `8e32be09` (the HEAD they were written against, PR #1705); `9ab2c0c3` is the close PR #1706 itself and is the anchor to use. The two differ by **docs only** — the DB is byte-identical and both derive Solve 111 / Match 96 — so a cross-reference to `8e32be09` is not a wrong baseline, just a different commit. See `PREP_PLAN.md` §Anchor.

---

## Prep Task 2 Prompt — Re-Derive the Sprint-38 Baseline & Carryforward Fingerprints

On a new branch `planning/sprint39-task2` (from `main`), execute Sprint-39 Prep Task 2. **Depends on Task 1.** (Priority: **Critical**; est. **3–4 h**.)

**Objective:** Re-derive — **not** re-read — every headline figure and every banked fingerprint Sprint 39's plan quotes, on current `main`, and record which reproduce and which do not, **before any design work assumes them**. This task gates every technical unknown in the sprint.

**Why it exists:** Sprint 38 proved twice that a banked figure is a liability. Its Day-8 prompt sweep corrected six stale figures and was **re-staled by that same sprint's Day-9 re-baseline within 24 hours**. At consultation send time, a package carried for **five sprints** described a failure mode (`EXIT — other error`) that **no longer reproduced** — prep had re-verified the *conclusion* and stamped the toolchain, but not the *description*.

**What to do:** (1) **Re-derive the KPI block** with `scripts/sprint_audit/kpi_block.py` and the floor with `scripts/sprint_audit/floor_tracker.py`; confirm each line against the baseline above and **record the commit**. The floor must come from `data/floor_provenance.json` — the mechanical `Match − (presolve ∧ match)` count yields **65** and looks authoritative. (2) **Confirm `path_solve_terminated` is still 0** — Sprint 38 emptied that category and a model returning to it is a regression. (3) **Re-reproduce each fingerprint** from a scratch directory: **dyncge** (`scripts/diagnostics/kkt_residual.py` → `CASE_B`, max relative **6.22e-02** at `stat_pf(CAP,SRV)`; cold MCP MS-1 @ **381401.119** vs NLP **539570.5027**); **lnts** (MS-4 at iteration 0; the `y("y2","h50")` / `5` / `45` values); **sarf** (killed at **28 m 40 s** vs the ≤300 s gate — **cap the run; it does not terminate**); **agreste / mine** (MS-5 after **9,734** / **10,662** iterations, NLP MS-1 @ 17706.43 / 17500.0); **weapons** (still spurious). (4) **Confirm the leak-gate inventory** — 186 in-scope, 7 allowlisted, `--min-scope` still asserted on **discovery**. (5) **Verify the four sarf call sites still exist at their recorded locations** — both `stationarity.py` and `emit_gams.py` changed in Sprint 38 (Days 9, 11, 12). (6) **Re-count the presolve-record population** — the live count of dangling `mcp_file_used` rows is **14** (13 pre-existing plus `weapons`); confirm it. (7) **Write `BASELINE_RECONFIRMATION.md`** recording, per figure: reproduced / corrected / not reproducible, each with its command and commit. **A correction is a finding, and must be routed to the task that depends on it.**

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_39/BASELINE_RECONFIRMATION.md` — per-figure verdict with the command and commit for each
- A corrections list, each routed to a named downstream prep task or sprint priority
- Confirmation that the four sarf call sites still exist where recorded
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns **1.1, 2.2, 3.3, 4.1, 7.1, 10.1**

**Unknowns to verify** (set each to ✅ / ❌ / 🔶 and add **Verified by / Date / Measured at / Findings / Evidence / Decision**): **1.1** (did twocge's and elec's **cold** emits actually change — `git show --numstat` on `204f35ac` and `82b91c94`, and read the hunks), **2.2** (contributes: re-reproduce dyncge's residual and confirm the top rows; the *locus* question belongs to Task 4), **3.3** (does lnts still reproduce MS-4 at iteration 0, and is a fresh emit byte-identical to its golden), **4.1** (are the four sarf call sites still where Day 7 recorded them), **7.1** (is the population still 14, and is `weapons` still the only spurious match — re-run `scripts/sprint_audit/check_mcp_solve_attribution.py` over the full presolve population), **10.1** (contributes: what is the current non-solving candidate population).

**Then close the task out:** update `KNOWN_UNKNOWNS.md` (each listed unknown → `✅ **Status:** VERIFIED` / `❌ **Status:** WRONG` / `🔶 **Status:** PARTIALLY WRONG`, plus **Verified by / Date / Measured at / Findings / Evidence / Decision**); update `PREP_PLAN.md` (**Task 2 Status → ✅ COMPLETE (date)**, add **Time Spent**, fill **Changes** and **Result** replacing "*To be completed*", check off **all** acceptance criteria `- [ ]` → `- [x]`, and prefix the Prep Task Overview row with ✅); add a `### Sprint 39 Prep` entry to `CHANGELOG.md`; run **`make typecheck && make lint && make format && make test`** if any `*.py` changed (expected docs/analysis-only — if so, state "docs only — quality gate N/A" explicitly rather than skipping it silently); commit as `Complete Sprint 39 Prep Task 2: Re-Derive the Sprint-38 Baseline & Carryforward Fingerprints`; push; open a PR with `gh pr create`; and **wait for reviewer comments**, replying to each on its own thread.

---

## Prep Task 3 Prompt — The Floor-Classification Decision Package (P1)

On a new branch `planning/sprint39-task3` (from `main`), execute Sprint-39 Prep Task 3. **Depends on Tasks 1, 2.** (Priority: **Critical**; est. **2–3 h**.)

**Objective:** Assemble a one-page package an owner can decide from on Day 0: **is the genuine floor 73 or 75?** Include the evidence, the counter-argument, the downstream consequences of each answer, and the exact edit each implies.

**Why it exists:** **Sprint 39 cannot report a floor movement until this resolves** — its own baseline depends on the answer. It is also the second consecutive sprint where a *decision*, not effort, is the blocker: the consultation slipped five sprints on the absence of a named recipient. A ready package scheduled Day 0 is the mitigation.

**The state of play:** `scripts/sprint_audit/floor_tracker.py` reports **73** (`baseline 73 + 0 entries`), the number of record under Sprint 38's close rule #3. But the definition — *methodology = cold emit **byte-identical to pre-fix**; genuine = a real emit fix **changed the cold emit**, still genuine if it matches only via the presolve warm-start (the polygon/ps2 precedent)* — appears to owe two entries. **twocge** (S38 D9, `204f35ac`) and **elec** (S38 D12, `82b91c94`) both had their cold emit changed, both now match, and **both were aborting beforehand**. Sprint 38 Day 9 applied the wrong test ("it matched via the presolve retry"); Day 12 inherited it.

**What to do:** (1) **Re-verify both claims from git**, not from prose — that the **cold** goldens (not the `_presolve` variants) changed, and *what* changed. (2) **Sweep for a THIRD qualifying model.** If the test was applied wrongly twice it may have been applied wrongly before: walk `git log --follow` over `data/gamslib/mcp/*_mcp.gms` for the baseline period, intersect with today's matching models, subtract the provenance entries. **A third instance changes the decision's shape** from "add two entries" to "the classification needs re-deriving" — which the provenance file's own README says is *impossible*, so that would be a methodological problem for the owner, not a bookkeeping fix. (3) **State the counter-argument for 73 fairly.** The strongest case is that the "still genuine" clause was written for the polygon/ps2 **non-convex** shape, which twocge may not fit — check twocge's convexity and cold-solve behaviour and say so either way. If the clause fits elec but not twocge, **the honest answer is 74**, which neither the plan nor the carryforwards anticipate. (4) **Write the exact edit each answer implies** — the two JSON entries with `limb`, `since_sprint`, `evidence`, `pr`; and the downstream reports needing re-baselining (Rolling-KPIs floor line, footnote ⁸, `SUMMARY.md` rows 38–39). (5) **Restate Sprint 39's acceptance criteria under each answer.**

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_39/FLOOR_DECISION_BRIEF.md` — one page: evidence, counter-argument, both answers' consequences, both edits
- A sweep result stating whether any **third** model qualifies
- Draft `floor_provenance.json` entries, ready to apply if the answer is 75
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns **1.1, 1.2, 1.3**

**Unknowns to verify:** **1.1** (did both cold emits change, and substantively — shared with Task 2, which supplies the git evidence), **1.2** (is there a third qualifying model), **1.3** (does the "still genuine via warm-start" clause actually apply to twocge, given the precedent is about non-convex models).

**Then close the task out:** update `KNOWN_UNKNOWNS.md` (each listed unknown → `✅ **Status:** VERIFIED` / `❌ **Status:** WRONG` / `🔶 **Status:** PARTIALLY WRONG`, plus **Verified by / Date / Measured at / Findings / Evidence / Decision**); update `PREP_PLAN.md` (**Task 3 Status → ✅ COMPLETE (date)**, add **Time Spent**, fill **Changes** and **Result** replacing "*To be completed*", check off **all** acceptance criteria `- [ ]` → `- [x]`, and prefix the Prep Task Overview row with ✅); add a `### Sprint 39 Prep` entry to `CHANGELOG.md`; run **`make typecheck && make lint && make format && make test`** if any `*.py` changed (else state "docs only — quality gate N/A"); commit as `Complete Sprint 39 Prep Task 3: The Floor-Classification Decision Package`; push; open a PR with `gh pr create`; and **wait for reviewer comments**, replying to each on its own thread.

---

## Prep Task 4 Prompt — dyncge Second-Defect Diagnosis & Layer Trace (P2)

On a new branch `planning/sprint39-task4` (from `main`), execute Sprint-39 Prep Task 4. **Depends on Tasks 1, 2.** (Priority: **Critical**; est. **5–7 h**.)

**Objective:** Take dyncge's `CASE_B` residual from a *symptom* to a **located defect with a named layer**, and author its Phase-0 acceptance gate — so Sprint 39 Day 1 starts implementing rather than diagnosing.

**Why it exists:** P2 is **the sprint's only new diagnosis**, and dyncge is precisely the model whose previous gate mis-scoped — `ISSUE_1693` demanded *"new logic rather than a widened condition-lift"* for a diagonal-triviality test that **had existed since #942** and was merely applied to inequalities. Reusing it cost ~40 lines of extraction. Sprint 38's most transferable finding is that **three of four Phase-0 gates named the wrong layer**.

**The fingerprint:** fixing #1693's empty-pair abort revealed a defect it had been **masking** — `scripts/diagnostics/kkt_residual.py` → **`CASE_B — emit_bug`**, max relative **6.22e-02** at `stat_pf(CAP,SRV)`, top rows `stat_pf(CAP,SRV)` · `stat_pq(HMN)` · `stat_pf(LAB,SRV)` · `stat_pf(LAB,HMN)` · `stat_pf(CAP,LMN)`, dual transfer CONSISTENT. Cold MCP MS-1 @ **381401.119** vs NLP **539570.5027** (29.3 % mismatch); the presolve retry also fails (`0/1`), so **there is no spurious match to adjudicate**.

**What to do:** (1) **Re-reproduce the residual** and confirm the top rows (Task 2 supplies this). (2) **Hand-derive the KKT shape** for `stat_pf` and `stat_pq` from dyncge's source — **before reading the emitter**. This is the step that distinguishes a wrong coefficient from a missing term. (3) **Compare term by term** against the emitted rows for the top residual instances, and find the **first divergence**. (4) **Trace to a LAYER, then a site** — parser / IR / AD / KKT / emit. **Start from `stationarity.py` and the AD entry points and work outward; do not begin at the emitter.** Record the layer *and why*. Remember elec: its defect surfaced in `stat_x` but originated in `derivative_rules.py`, upstream of stationarity entirely, and required **two** fixes in two files. (5) **Check whether the mechanism already exists elsewhere** — is this the positional-vs-declared-domain class (dyncge has `Alias (u,v), (i,j), (h,k)`), an alias-root collision of the #1062/#1350 kind, or the `_diff_sum` partial-collapse defect? Cross-check against Task 7's survey if it has landed. (6) **Author the Phase-0 gate** in a **new issue** — hand-derived shape, expected emit pattern, fail-before/pass-after with the **`CASE_A` requirement**, leak-gate expectation, determinism, and a **named layer with a one-line justification**. (7) **Decide whether `CASE_A` is even reachable** — dyncge may be non-convex like elec, in which case the honest target is a *documented* divergence with `modelstat` asserted, not a Match. **State this before the sprint, not during it.**

**Deliverables:**
- A new `docs/issues/ISSUE_<n>_dyncge-*.md` with a complete Phase-0 acceptance gate, including a **named layer**
- A hand-derived KKT shape for `stat_pf` / `stat_pq` and a term-by-term comparison against the emit
- A stated position on whether `CASE_A` is reachable, or whether a documented divergence is the honest target
- A cross-check result: is this mechanism already known under another name?
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns **2.1, 2.2, 2.3, 2.4**

**Unknowns to verify:** **2.1** (is `CASE_A` reachable, or is dyncge non-convex — note elec's harness verdict *changed* from `CASE_B` to `CASE_C_OBJDEF` as the classifier improved), **2.2** (is the defect **in** the `pf`/`pq` block or does it merely **surface** there), **2.3** (is this mechanism already known under another name — the S38 dyncge lesson), **2.4** (does #1693 close cleanly on its own terms, or is it being widened).

**Then close the task out:** update `KNOWN_UNKNOWNS.md` (each listed unknown → `✅ **Status:** VERIFIED` / `❌ **Status:** WRONG` / `🔶 **Status:** PARTIALLY WRONG`, plus **Verified by / Date / Measured at / Findings / Evidence / Decision**); update `PREP_PLAN.md` (**Task 4 Status → ✅ COMPLETE (date)**, add **Time Spent**, fill **Changes** and **Result** replacing "*To be completed*", check off **all** acceptance criteria `- [ ]` → `- [x]`, and prefix the Prep Task Overview row with ✅); add a `### Sprint 39 Prep` entry to `CHANGELOG.md`; run **`make typecheck && make lint && make format && make test`** if any `*.py` changed (else state "docs only — quality gate N/A"); commit as `Complete Sprint 39 Prep Task 4: dyncge Second-Defect Diagnosis & Layer Trace`; push; open a PR with `gh pr create`; and **wait for reviewer comments**, replying to each on its own thread.

---

## Prep Task 5 Prompt — lnts Fingerprint Reproduction & Runtime-Probe Design (P3)

On a new branch `planning/sprint39-task5` (from `main`), execute Sprint-39 Prep Task 5. **Depends on Tasks 1, 2.** (Priority: **Critical**; est. **4–6 h**.)

**Objective:** Reproduce lnts's failure from anchored GAMS diagnostics, **design the runtime bound probe** that would confirm or refute the two-`.fx`-mechanism hypothesis, and trace the fix surface — because **none of the three has ever been done**.

**Why it exists:** lnts is the one Sprint-38 P8 candidate whose budget never arrived, so **both its mechanism and its fix surface are untraced**. Its stated surface — the `fix_rhs = "0"` fallback in `emit_gams.py` — is the *emitter*, which is exactly where three of four Sprint-38 gates wrongly pointed.

**The hypothesis, as banked and never tested:** two `.fx` mechanisms act on the same cells. The correct one emits `y_fx_y2_h50.. y("y2","h50") - 5 =E= 0;` while a blanket pruned-instance zeroing fires on exactly those cells, giving `y.lo = y.up = 0` against equations demanding **5** and **45** — hence **MS-4 at iteration 0**. The named fix is to skip tuples already carrying a `<var>_fx_<labels>` equation, *"the same shape as the Sprint-33 P6 fix"*.

**What to do:** (1) **Re-emit lnts** and confirm the fresh emit is byte-identical to its committed golden — so the measurement describes the golden. (2) **Reproduce the failure** from a scratch directory, meeting all four §4.1 criteria: **anchored `^****` diagnostics** (a `.lst` contains echoed source), a **terminal state from GAMS's own line**, **runtime observation** for runtime properties, and **a passing negative control**. (3) **Confirm both `.fx` mechanisms are present** in the emit — the `y_fx_*` equation(s) and any blanket zeroing targeting the same tuples. (4) **Design the runtime bound probe.** It must read the **effective** bounds GAMS computes at solve time (a `display y.lo, y.up;` injected after all fixing, or the equation listing's bound columns) and show the contradiction against the `_fx_` equation's demanded value. **Write the confirm and refute criteria BEFORE running it.** A source read can show two mechanisms exist; only a probe shows they collide. (5) **Trace the fix surface from `stationarity.py` / the AD entry points outward**, and only *then* consider the emitter. Instrument the `fix_rhs = "0"` fallback and confirm it is actually reached — do not infer it from reading. Record the layer. (6) **Author the Phase-0 gate** with the probe as fail-before evidence. (7) **Define the REPLAN exit:** if the probe shows no contradictory bounds, the hypothesis is **refuted** — bank the real mechanism and do not widen the track.

**⚠ Do NOT batch `cesam` with this.** Sprint 38 checked rather than assumed: cesam shows the same MS-4-at-iteration-0 *signature* but has **0 `_fx_` equations**, so lnts's mechanism cannot apply. **A shared signature is not a shared mechanism.**

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_39/LNTS_PROBE_DESIGN.md` — the runtime bound probe, with confirm/refute criteria stated in advance
- A reproduced fingerprint meeting all four §4.1 criteria, including a passing negative control
- A traced fix surface with its **layer** named, reached from AD/KKT outward
- A Phase-0 gate on the lnts issue, or the issue created if none exists
- A written REPLAN exit
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns **3.1, 3.2, 3.3**

**Unknowns to verify:** **3.1** (do two `.fx` mechanisms actually collide **at runtime** — the decisive measurement), **3.2** (is the `fix_rhs = "0"` fallback even reached, and is the Sprint-33 P6 analogy genuine or superficial), **3.3** (does lnts still reproduce MS-4 at iteration 0 — shared with Task 2).

**Then close the task out:** update `KNOWN_UNKNOWNS.md` (each listed unknown → `✅ **Status:** VERIFIED` / `❌ **Status:** WRONG` / `🔶 **Status:** PARTIALLY WRONG`, plus **Verified by / Date / Measured at / Findings / Evidence / Decision**); update `PREP_PLAN.md` (**Task 5 Status → ✅ COMPLETE (date)**, add **Time Spent**, fill **Changes** and **Result** replacing "*To be completed*", check off **all** acceptance criteria `- [ ]` → `- [x]`, and prefix the Prep Task Overview row with ✅); add a `### Sprint 39 Prep` entry to `CHANGELOG.md`; run **`make typecheck && make lint && make format && make test`** if any `*.py` changed (else state "docs only — quality gate N/A"); commit as `Complete Sprint 39 Prep Task 5: lnts Fingerprint Reproduction & Runtime-Probe Design`; push; open a PR with `gh pr create`; and **wait for reviewer comments**, replying to each on its own thread.

---

## Prep Task 6 Prompt — sarf's Four Call Sites: Cost Attribution & Atomicity Plan (P4)

On a new branch `planning/sprint39-task6` (from `main`), execute Sprint-39 Prep Task 6. **Depends on Tasks 1, 2.** (Priority: **Critical**; est. **5–7 h**.)

**Objective:** Confirm the four untouched call sites still exist, **attribute the remaining wall-clock cost to them by measurement**, and produce an atomicity plan — so P4's 20–28 h is spent implementing rather than re-profiling.

**Why it exists:** P4 is **Sprint 39's only KPI mover** (+1 Translate → 136). Its Sprint-38 change is already in `main` and **emit-preserving**, but sarf still ran **28 m 40 s** against a **≤300 s** gate. The claim that the remaining cost is *located, not suspected* is the entire basis for the estimate, and has not been re-checked since Sprint 38 Day 7 — during which both `stationarity.py` and `emit_gams.py` changed materially.

**What to do:** (1) **Locate the four call sites on current `main`** by **symbol**, not line number, and record their present `file:line`, noting anything that moved. (2) **Attribute cost by measurement, not by reading.** Profile a **capped** sarf translate (the uncapped run does not terminate) and report what fraction of wall-clock each of the four accounts for. **If the four do not dominate, that is a finding that changes P4's estimate and must be reported now, not in the sprint.** Distinguish **per-column** cost (which the O(active) argument addresses) from **per-row** cost (which it explicitly does not — the 1,183 rows are untouched). (3) **Re-validate the O(active) projection** — ~141 s, from 1,183 rows × 398 active columns at 3,343 diff/s. The ≤300 s gate was revised *because of* this projection (owner decision, 2026-08-18); if it has moved, the gate's headroom changes. (4) **Write the atomicity plan** — which changes land as one unit and why a partial landing is an **inconsistent MCP** rather than partial progress; enumerate the corpus-safety call sites that must be provably unperturbed. (5) **Design the surrogate fixture** — **sarf cannot be its own fixture** (at 369,024 declared columns the fail-before state does not terminate), so specify a corpus-free surrogate exercising the same shape at a size that terminates, and check it hits **all four** sites. (6) **Restate the Phase-0 gate**: ≤300 s on a nightly slot, byte-stable golden, symbolic multiplier indices (`grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` **empty**), determinism ×3, and `--min-scope` raised **186 → 187**.

**Two gate peculiarities — do not rediscover them:** `make leak-check MODEL=sarf` reports `NO-OP` because sarf has no golden; the real gate is `make check-goldens` at full scope **plus sarf newly producing a golden**. And Day 7's first narrowing attempt **traded 436 M differentiations for 436 M dict lookups** and still did not terminate — *narrowing a loop's body does not help if the narrowing itself is O(the thing you removed)*.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_39/SARF_CALLSITE_PLAN.md` — the four sites at their **current** locations, with measured cost attribution
- A re-validated O(active) projection, or a corrected one
- An atomicity plan naming the unit and the corpus-safety sites that must be unperturbed
- A corpus-free surrogate fixture specification
- The restated Phase-0 gate, with a REPLAN exit for a timeout re-trigger
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns **4.1, 4.2, 4.3, 4.4**

**Unknowns to verify:** **4.1** (are the four sites still where Day 7 recorded them — shared with Task 2), **4.2** (do they actually account for the bulk of remaining wall-clock), **4.3** (does the ~141 s projection still hold), **4.4** (can a surrogate fixture be built, and does the scope go 186 → 187).

**Then close the task out:** update `KNOWN_UNKNOWNS.md` (each listed unknown → `✅ **Status:** VERIFIED` / `❌ **Status:** WRONG` / `🔶 **Status:** PARTIALLY WRONG`, plus **Verified by / Date / Measured at / Findings / Evidence / Decision**); update `PREP_PLAN.md` (**Task 6 Status → ✅ COMPLETE (date)**, add **Time Spent**, fill **Changes** and **Result** replacing "*To be completed*", check off **all** acceptance criteria `- [ ]` → `- [x]`, and prefix the Prep Task Overview row with ✅); add a `### Sprint 39 Prep` entry to `CHANGELOG.md`; run **`make typecheck && make lint && make format && make test`** if any `*.py` changed (else state "docs only — quality gate N/A"); commit as `Complete Sprint 39 Prep Task 6: sarf's Four Call Sites — Cost Attribution & Atomicity Plan`; push; open a PR with `gh pr create`; and **wait for reviewer comments**, replying to each on its own thread.

---

## Prep Task 7 Prompt — Positional-vs-Declared-Domain Site Survey (P5)

On a new branch `planning/sprint39-task7` (from `main`), execute Sprint-39 Prep Task 7. **Depends on Tasks 1, 2.** (Priority: **High**; est. **4–5 h**.)

**Objective:** Enumerate every site that resolves an index **positionally against a declared domain**, classify each by whether it mishandles a domain that repeats a symbol, and produce the catalog P5's audit consumes.

**Why it exists:** this is the defect class that produced **wrong answers in two different layers on two consecutive days**, and **neither instance crashed at the point of the defect** — both surfaced far away, found while chasing unrelated symptoms. That is exactly the profile of a class worth surveying rather than waiting to trip over. P5 is **0-bucket by design**; prep produces the catalog, the sprint produces the guards and tests.

**The two known instances:** **tricp (S38 D11)** — `slp(n,n)` as a **variable** domain; in a GAMS equation *definition* a repeated controlling index binds to the **same element**, so the head generated **zero rows** and 108 on-edge columns went unmatched. Fixed by a **pre-differentiation IR pass**, because the body is built positionally from the same tuple and the collapse reached back into the objective gradient. **elec (S38 D12)** — `Set ut(i,i)` as a **set** domain; `_replace_indices_in_expr`'s `Sum` branch overlays `{idx: idx}` self-mappings so AD names like `j__` survive, **which also puts them in `element_to_set`** — the very membership the `SetMembershipTest` branch used to decide *"concrete element ⇒ resolve positionally"*. Both declared positions being `i`, the guard collapsed to `ut(i,i)`: the diagonal of a **strictly upper-triangular** set, identically false, **silently dropping half the gradient**.

**What to do:** (1) **Enumerate the sites** — grep `src/kkt/`, `src/ad/`, `src/emit/` and `src/ir/` for positional indexing (`domain[pos]`, `smt_domain[pos]`, `var_domain[pos]`, `set_declared_domain[pos]`) and for **first-match scans** over a domain tuple (the #1350 shape that needed consume-once matching). (2) **For each site, determine behaviour under a repeated domain** — does it collapse, and does the collapse produce a wrong answer or a harmless rename? (3) **Measure corpus incidence per shape.** The *variable*-domain case was measured in Sprint 38 (exactly two models: `tricp`, `ferts`); **the set-domain case was never surveyed** — elec was found by chasing a division-by-zero. Count models with a repeated-symbol **set** domain, and check whether **parameter** domains (`ferts` declares `rail(i,i)`) are resolved positionally anywhere. (4) **Classify each site**: already guarded / needs a guard / needs only a test / not reachable — **and every "not reachable" verdict needs an argument, not an assertion**. (5) **Rank by blast radius** — a site every model reaches is worth more than one two models reach. (6) **Specify the property test** covering the class generically, and check for legitimate counter-examples (is a repeated head ever *correct*?).

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_39/POSITIONAL_DOMAIN_SURVEY.md` — every site, classified and ranked by blast radius
- Corpus incidence per shape: repeated *variable* domains vs repeated *set* domains (and parameters)
- A property-test specification covering the class generically
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns **5.1, 5.2, 5.3**

**Unknowns to verify:** **5.1** (how many sites resolve positionally against a declared domain — the audit's cost is a direct function of this), **5.2** (how many corpus models have a repeated-symbol **set** domain — a matching model that is silently wrong is the worst outcome in this class), **5.3** (is a generic property test expressible).

**Note:** Task 4 wants this survey's output for Unknown 2.3, and Task 11 wants it for the 10.1 cross-check. **Start this early.**

**Then close the task out:** update `KNOWN_UNKNOWNS.md` (each listed unknown → `✅ **Status:** VERIFIED` / `❌ **Status:** WRONG` / `🔶 **Status:** PARTIALLY WRONG`, plus **Verified by / Date / Measured at / Findings / Evidence / Decision**); update `PREP_PLAN.md` (**Task 7 Status → ✅ COMPLETE (date)**, add **Time Spent**, fill **Changes** and **Result** replacing "*To be completed*", check off **all** acceptance criteria `- [ ]` → `- [x]`, and prefix the Prep Task Overview row with ✅); add a `### Sprint 39 Prep` entry to `CHANGELOG.md`; run **`make typecheck && make lint && make format && make test`** if any `*.py` changed (else state "docs only — quality gate N/A"); commit as `Complete Sprint 39 Prep Task 7: Positional-vs-Declared-Domain Site Survey`; push; open a PR with `gh pr create`; and **wait for reviewer comments**, replying to each on its own thread.

---

## Prep Task 8 Prompt — Presolve-Record Remedy Design (P7)

On a new branch `planning/sprint39-task8` (from `main`), execute Sprint-39 Prep Task 8. **Depends on Tasks 1, 2.** (Priority: **High**; est. **3–4 h**.)

**Objective:** Design a **systemic** remedy covering all affected presolve-record rows — the spurious match and the dangling `mcp_file_used` references — and codify the presolve-golden adoption rule that emerged in Sprint 38.

**Why it exists:** **Match 96 is overstated by 1** and has been since Day 10, when Sprint 38 found `weapons`'s MCP had aborted while the objective read back the embedded NLP's own answer. Sprint 38 **reported rather than corrected** it, because a model-by-model fix *"manufactures a worse number than the one being checked"*. The correction is also a KPI **fall**, which makes it exactly the kind of change to design and explain in advance rather than discover at close.

**The two findings share a population and a cause:** (1) a presolve emit warm-starts by solving the original model inside the generated file, so if the MCP aborts, `nlp2mcp_obj_val = <objvar>.l` reads back **the NLP's own answer and matches itself**; weapons' listing held a single solve summary (the embedded NLP's, MS-2 @ 1735.5696) and the MCP aborted with `EXECERROR = 1`. (2) `mcp_file_used` dangles for **14** rows — 13 pre-existing plus `weapons`, whose presolve golden was reverted in review — because the field records the artifact the solve *generated*, not a committed golden. **`weapons` is in both findings**, which is part of why one remedy has to cover both.

**What to do:** (1) **Re-count the population** (Task 2 supplies it). (2) **Choose the remedy shape and argue it** — either wire the attribution check into the pipeline's record-writing so a spurious match cannot be recorded, **or** re-specify `mcp_file_used` (null unless a committed golden exists) and back-fill. **Enumerate which of the 14 rows each remedy corrects, and say why the chosen one covers all of them.** Check every consumer of `mcp_file_used` and `outcome_category` for breakage — the DB is the substrate the KPI helper, the floor tracker and the `--resolve-changed` checkpoint all read. (3) **Design the KPI-fall communication.** If weapons is reclassified, Match goes 96 → 95; write the wording that reports it **as a correction with its reason in the same sentence**. (4) **Codify the adoption rule**: adopt a presolve golden only if `scripts/sprint_audit/check_mcp_solve_attribution.py` reports `MCP-SOLVED` **and** `check_presolve_divergence.py --model X` passes **and** the DB's `mcp_file_used` references it. Include the weapons lesson — *a golden can pass structure/DB/NA-guard/determinism review and still not RUN*; "the emit actually executes" belongs in any adoption protocol. (5) **Specify the regression test:** a fixture whose MCP aborts must **not** be recordable as a match.

**⚠ Preserve the attribution tool's positional method.** It is **deliberately not keyed on `EXECERROR`**, which conflates MCP-side and NLP-side aborts — that is how weapons was first reported against the wrong half of the file.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_39/PRESOLVE_RECORD_REMEDY.md` — the chosen remedy with its per-row coverage argument
- The KPI-fall communication wording, pre-written
- The presolve-golden adoption rule, drafted for CONTRIBUTING
- A regression-test specification for the aborting-MCP case
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns **7.1, 7.2, 7.3**

**Unknowns to verify:** **7.1** (is the population still 14, is `weapons` still the only spurious match — shared with Task 2), **7.2** (which remedy shape covers **all** rows — if none does, P7 must be re-scoped **before** the sprint), **7.3** (does the Match 96 → 95 correction break any gate or report that assumes monotonicity — grep the CI workflows).

**Then close the task out:** update `KNOWN_UNKNOWNS.md` (each listed unknown → `✅ **Status:** VERIFIED` / `❌ **Status:** WRONG` / `🔶 **Status:** PARTIALLY WRONG`, plus **Verified by / Date / Measured at / Findings / Evidence / Decision**); update `PREP_PLAN.md` (**Task 8 Status → ✅ COMPLETE (date)**, add **Time Spent**, fill **Changes** and **Result** replacing "*To be completed*", check off **all** acceptance criteria `- [ ]` → `- [x]`, and prefix the Prep Task Overview row with ✅); add a `### Sprint 39 Prep` entry to `CHANGELOG.md`; run **`make typecheck && make lint && make format && make test`** if any `*.py` changed (else state "docs only — quality gate N/A"); commit as `Complete Sprint 39 Prep Task 8: Presolve-Record Remedy Design`; push; open a PR with `gh pr create`; and **wait for reviewer comments**, replying to each on its own thread.

---

## Prep Task 9 Prompt — Consultation Reply-Integration & Follow-Up Package (P6)

On a new branch `planning/sprint39-task9` (from `main`), execute Sprint-39 Prep Task 9. **Depends on Task 1.** (Priority: **Medium**; est. **2–3 h**.)

**Objective:** Prepare **both branches** of the date-gated consultation priority — integrate a reply, or post the follow-up — so neither requires improvisation on the day.

**Why it exists:** P6 is **date-gated at 2026-09-09** and cannot be pulled earlier. Its value depends entirely on whether a reply arrives, and the failure mode is documented: the consultation slipped **five sprints** on the absence of an owner, and **re-opening the send decision** is what caused each slip. There is a subtler risk too — the package sent on 2026-08-26 was itself corrected at send time because its banked failure description had **rotted over five carries**.

**The state of play:** sent **2026-08-26** to `ferris@cs.wisc.edu`, `steve@gams.com`, `sdirkse@gams.com`, carrying three threads — **rocket** (`SOLVER STATUS 1 Normal Completion` / `MODEL STATUS 5 Locally Infeasible` after **9,241 iterations**, 0 evaluation errors; residual on `stat_step` under three of PATH's four final norms); the **11-model license-capacity ask**; and **`agreste` + `mine` as one question** (two verified-convex LPs, MS-5 *Locally* Infeasible after **9,734** / **10,662** iterations — structurally odd for a pure LCP). Tracked on **#1462** and **#1443**.

**What to do:** (1) **Draft the follow-up comment** for the no-reply branch, ready to post on 2026-09-09. **It must not re-open the send decision.** (2) **Prepare the reply-integration checklist** per thread: where a recommended option set plugs into the `--force {homotopy,multistart,optfile}` scaffold; what a license grant triggers (a single `--only-solve` batch over the 11); what an answer on the LCP question means for `agreste`, which has **no open owning issue** (#1068 is an earlier, closed diagnosis). (3) **Re-measure all three threads' figures** so a reply is read against current numbers, not send-time ones. (4) **Pre-write the cohort re-test procedure** — one `--only-solve` pass — with the caveat that **`ferts`'s emit was silently wrong until S38 D11**, so *"a golden exists"* has never meant *"the golden is correct"* for this cohort, and **no member's emit has ever been exercised by a solve**. (5) **State the projection discipline explicitly:** rocket's **+1** and the cohort's **+11** are **not Sprint-39 projections** and must not enter acceptance criteria.

**An actionable reply** is a concrete option set / `optfile`, a regularization or continuation schedule, or a named reformulation class. A diagnosis without one of those three does not unblock rocket — **define the response to a non-actionable reply too**.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_39/CONSULTATION_FOLLOWUP_PACKAGE.md` — both branches prepared
- A ready-to-post follow-up comment that does **not** re-open the send decision
- A per-thread reply-integration checklist
- The 11-model cohort re-test procedure with the `ferts` caveat
- Re-measured figures for all three threads
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns **6.1, 6.2, 6.3**

**Unknowns to verify:** **6.1** (has a reply arrived, and would it be actionable — check #1462 and #1443), **6.2** (if a license arrives, does the 11-model batch actually solve, and is a per-model sanity check warranted before spending capacity), **6.3** (does `agreste` need a new owning issue).

**Note:** this task's central question is answered by other people. **Start it early and revisit**, rather than scheduling it once.

**Then close the task out:** update `KNOWN_UNKNOWNS.md` (each listed unknown → `✅ **Status:** VERIFIED` / `❌ **Status:** WRONG` / `🔶 **Status:** PARTIALLY WRONG`, plus **Verified by / Date / Measured at / Findings / Evidence / Decision**); update `PREP_PLAN.md` (**Task 9 Status → ✅ COMPLETE (date)**, add **Time Spent**, fill **Changes** and **Result** replacing "*To be completed*", check off **all** acceptance criteria `- [ ]` → `- [x]`, and prefix the Prep Task Overview row with ✅); add a `### Sprint 39 Prep` entry to `CHANGELOG.md`; run **`make typecheck && make lint && make format && make test`** if any `*.py` changed (else state "docs only — quality gate N/A"); commit as `Complete Sprint 39 Prep Task 9: Consultation Reply-Integration & Follow-Up Package`; push; open a PR with `gh pr create`; and **wait for reviewer comments**, replying to each on its own thread.

---

## Prep Task 10 Prompt — Epic-5 Design Scoping: Numéraire Rule & Degeneracy Detection (P9)

On a new branch `planning/sprint39-task10` (from `main`), execute Sprint-39 Prep Task 10. **Depends on Tasks 1, 2.** (Priority: **Medium**; est. **3–4 h**.)

**Objective:** Scope the two **answerable** Epic-5 open questions as design work — the numéraire-selection rule and degeneracy detection — **without running any camcge experiment**, and with the banned variants recorded as banned.

**Why it exists:** Epic 5's value is its **refutation record**. Three-plus sprints of camcge variants have all stayed MS-4, and the most dangerous one is *primal-correct*, which makes it perpetually tempting. Scoping the answerable questions in prep is what lets Epic 5 **start** rather than re-scope — and prep is where the temptation to re-run a banned experiment is cheapest to refuse.

**⚠ BANNED variants — consolidated in `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` §4a. Do NOT re-run any of them:** **price-pin** → MS-4 · **single-dual-pin** → MS-4 · **drop-row** → **primal-correct at omega 299 but breaks the MCP dual silently**, because the dropped market's multiplier is orphaned out of the stationarity. **camcge #1330 stays Epic-5-scoped and is not implemented in Sprint 39** — MS-4 against a *correct* NLP optimum is structural Walras rank-deficiency, not an emit defect.

**Already answered, and it narrows the scope:** **Q3** — does drop-row + fix-cpi reach MS-1? **No** (S30 D11, re-confirmed S34/S36/S37). **Q4** — cohort generality? The §2 survey found **camcge is the sole inherent Walras case**; every other "CGE cohort" issue is an ordinary emit/AD bug, several of which Sprint 38 fixed (#1331 twocge landed D9). **Epic 5 is a single-transformation program.**

**What to do:** (1) **Survey the corpus CGE cohort** for what a numéraire-selection rule must handle — how many declare a numéraire, how many have an unambiguous largest sector by SAM value, how many are ambiguous. (2) **Draft the numéraire-selection rule** with its failure modes, and state plainly whether a fully automatic rule is achievable or whether **per-model declaration is required** — a negative answer is a perfectly good deliverable and may be the honest one. (3) **Draft the degeneracy-detection design, and spend the effort on the FALSE-POSITIVE analysis.** A detector that flags well-posed models is worse than none, because it routes healthy models into a transformation they do not need. Apply the candidate detectors as **analysis over the corpus IR** — camcge is the only expected true positive — and count the flags. (4) **Record both as *proposed*, not open**, in `CGE_DEGENERACY_SCOPING.md`, keeping Q3/Q4's answers intact. (5) **Re-state the BANNED list at the top** of whatever is written, so the next reader meets it before the temptation. (6) **Run no camcge experiment.** If a measurement seems necessary, that itself is a finding — record what would need measuring and why it is out of scope here.

**Deliverables:**
- `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` extended with a proposed numéraire-selection rule and a degeneracy-detection design
- A **false-positive analysis** for the detection design, using the corpus as the test set
- A CGE-cohort numéraire survey
- Q1 and Q2 moved from *open* to *proposed*, with Q3/Q4's answers preserved
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns **9.1, 9.2**

**Unknowns to verify:** **9.1** (is an automatic numéraire-selection rule achievable, or is per-model declaration required — and given camcge is the sole case, is a *general* rule even warranted), **9.2** (can Walras-degeneracy be detected without falsely flagging a well-posed model — **the false-positive half is the hard half**; if detection only works post-solve, that changes Epic 5's architecture from preprocessing to a retry loop).

**Then close the task out:** update `KNOWN_UNKNOWNS.md` (each listed unknown → `✅ **Status:** VERIFIED` / `❌ **Status:** WRONG` / `🔶 **Status:** PARTIALLY WRONG`, plus **Verified by / Date / Measured at / Findings / Evidence / Decision**); update `PREP_PLAN.md` (**Task 10 Status → ✅ COMPLETE (date)**, add **Time Spent**, fill **Changes** and **Result** replacing "*To be completed*", check off **all** acceptance criteria `- [ ]` → `- [x]`, and prefix the Prep Task Overview row with ✅); add a `### Sprint 39 Prep` entry to `CHANGELOG.md`; run **`make typecheck && make lint && make format && make test`** if any `*.py` changed (else state "docs only — quality gate N/A"); commit as `Complete Sprint 39 Prep Task 10: Epic-5 Design Scoping — Numéraire Rule & Degeneracy Detection`; push; open a PR with `gh pr create`; and **wait for reviewer comments**, replying to each on its own thread.

---

## Prep Task 11 Prompt — Emit-Backlog Catalog Refresh & Process-Infrastructure Spec (P8, P10)

On a new branch `planning/sprint39-task11` (from `main`), execute Sprint-39 Prep Task 11. **Depends on Tasks 1, 2, 7.** (Priority: **Medium**; est. **3–4 h**.)

**Objective:** Refresh the emit-backlog candidate catalog against the post-Sprint-38 corpus, and specify the four process-infrastructure changes the Sprint-38 retrospective recommended.

**Why it exists:** **P10 is the deliberate schedule filler**, and its pre-registered selection rule is what stops it becoming an open-ended diagnosis sprint — but that rule needs a *current* catalog, and Sprint 38 removed four models from `path_solve_terminated` entirely. **P8 is the infrastructure that would have prevented Sprint 38's most repeated failure**: three of four gates named the wrong layer, one demanded new logic for logic that existed.

**The selection rule (unchanged, because it worked):** a model enters the sweep only with a **reproduced fingerprint** *and* a **named fix surface**. Anything needing a new diagnosis is **banked, not started**.

**Current bank:** **`agreste`** — the highest-value bank; an **LP**, `verified_convex`, NLP MS-1 @ 17706.43, MCP MS-5 after **9,734 iterations**; a *locally* infeasible pure LCP is structurally odd. **Also now posed to the PATH authors — check #1443 before starting local work**, and note it has **no open owning issue**. **`cesam`** — new diagnosis; same MS-4-at-0-iterations *signature* as lnts but **0 `_fx_` equations**, so lnts's mechanism cannot apply. **`indus`** (31 errors across 7 families), **`dinam`** (22), **`turkpow`**, **`clearlak`** — broad, not bounded, or structurally excluded.

**The four process findings (S38 retrospective §7):** **8a** record the **LAYER** in a Phase-0 gate, not just `file:line` · **8b** check whether the logic already exists for another **population** before authoring new emit logic · **8c** stop pre-registering close rules against **unstarted** carryforward tracks · **8d** re-derive a carried package's **evidence** at use time, not only its conclusion (corollary: an internal planning doc is not an external deliverable).

**What to do:** (1) **Refresh the catalog** against the current DB — every non-solving candidate with its outcome category, whether it has an owning issue, whether that issue has a Phase-0 gate, and whether a fingerprint is reproduced. (Sprint 38 found **0 of 5** candidates had a gate, which is why P7 gated P8 that sprint.) (2) **Apply the selection rule** and produce a ranked shortlist, every rejection carrying its reason. (3) **Cross-check against Task 7's survey** — is any backlog model an instance of the positional-domain class? That moves it from "new diagnosis" to "named fix surface". (4) **Specify 8a** — the Phase-0 template's new *layer* field and the `scripts/sprint_audit/check_phase0_doc.py` assertion. **Dry-run the assertion over all existing gates first**: it changes a **required CI status check**, and one that fails on every existing PR forces either a mass backfill or an immediate revert. Decide whether it applies only to *new* gates and how "new" is determined mechanically. (5) **Specify 8b** — where the check lives, and **retro-apply the draft to all four Sprint-38 P8 gates**: a check that would have fired on all four is too broad; one that fires on none is useless. (6) **Specify 8c and 8d** as CONTRIBUTING rules, each with its motivating incident — and check 8c's preconditions against the "could this be used to excuse a miss?" test. (7) **Write the fail-before test for each** — a template change without a test is a suggestion.

**⚠ Do not re-open the ganges rebind site.** #1668 direction 1 is a measured **no-op** (265 fires, zero residual) and direction 2's information is absent — ganges and `prolog` are *locally indistinguishable* there.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_39/BACKLOG_CANDIDATE_CATALOG.md` — refreshed population, selection rule applied, ranked shortlist with rejection reasons
- `docs/planning/EPIC_4/SPRINT_39/PROCESS_INFRA_SPEC.md` — specs for 8a–8d, each with its motivating incident and a fail-before test
- A cross-check result: which backlog models, if any, are instances of the positional-domain class
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns **8.1, 8.2, 8.3, 10.1, 10.2**

**Unknowns to verify:** **8.1** (can `scripts/sprint_audit/check_phase0_doc.py` assert a layer field without breaking the existing gates), **8.2** (where does the "does this exist for another population?" check live, and would it have caught dyncge without false-firing on tricp), **8.3** (are close-rule preconditions expressible without becoming escape hatches), **10.1** (does the refreshed catalog still yield ≥2 qualifying candidates — if not, what absorbs P10's 12–16 h), **10.2** (is Sprint 38's Unknown 1.5 measurable this sprint, or should it be **closed as unreachable** rather than carried a third time).

**Then close the task out:** update `KNOWN_UNKNOWNS.md` (each listed unknown → `✅ **Status:** VERIFIED` / `❌ **Status:** WRONG` / `🔶 **Status:** PARTIALLY WRONG`, plus **Verified by / Date / Measured at / Findings / Evidence / Decision**); update `PREP_PLAN.md` (**Task 11 Status → ✅ COMPLETE (date)**, add **Time Spent**, fill **Changes** and **Result** replacing "*To be completed*", check off **all** acceptance criteria `- [ ]` → `- [x]`, and prefix the Prep Task Overview row with ✅); add a `### Sprint 39 Prep` entry to `CHANGELOG.md`; run **`make typecheck && make lint && make format && make test`** if any `*.py` changed (else state "docs only — quality gate N/A"); commit as `Complete Sprint 39 Prep Task 11: Emit-Backlog Catalog Refresh & Process-Infrastructure Spec`; push; open a PR with `gh pr create`; and **wait for reviewer comments**, replying to each on its own thread.

---

## Prep Task 12 Prompt — Plan Sprint 39 Detailed Schedule

On a new branch `planning/sprint39-task12` (from `main`), execute Sprint-39 Prep Task 12. **Depends on all tasks (1–11).** (Priority: **Critical**; est. **3–4 h**.)

**Objective:** Convert the prep findings into a day-by-day Sprint 39 schedule with per-day budgets, pre-registered REPLAN exits, checkpoints and close rules — the document the sprint is actually executed from.

**Why it exists:** Sprint 38's schedule absorbed a **Day-1 REPLAN of its top priority** without losing the sprint, because the REPLAN exits and the budget reallocation were pre-registered. Sprint 39 carries three tracks that could REPLAN (P2's residual persisting, P3's probe refuting the hypothesis, P4's timeout re-triggering) and one that is **date-gated and cannot be moved**.

**Budget:** 14 days (Day 0 + Days 1–13) at ≤ 12 h/day = **168 h cap**; the plan's estimate is **116–160 h**, heaviest day ~11.4 h.

**Fixed points that constrain the schedule:** **P1 is Day 0** (a decision, and the baseline depends on it) · **P6 is date-gated at 2026-09-09** and cannot be pulled earlier · **P4 is the only KPI mover** and the largest single cost · **P7 changes how the pipeline records solves**, so it is scheduled **after P1 settles the baseline** · checkpoints at **Day 5** and **Day 10**, final retest **Day 13** under ≥ 3 `PYTHONHASHSEED`.

**What to do:** (1) **Assign priorities to days**, honouring the fixed points, with a per-day hour budget summing under 168 and no day over 12. (2) **Write the REPLAN exit for each track** — the *specific evidence* that triggers it and **where the budget goes**. (3) **Schedule the checkpoints** and the final retest, with the DB checkpoint **re-anchored to `9ab2c0c3`**. (4) **Pre-register the close rules, and state each rule's PRECONDITION explicitly.** Sprint 38 learned this the hard way: its close rule #2 was written around P1's cascade, P1 was REPLAN'd on Day 1, and a sound rule went unmet for reasons unconnected to the close. Include: the **three-gate firm-landing rule** (per-model Phase-0 gate + an **unqualified** leak-gate pass + in `main`); **`path_solve_terminated` must maintain 0** — a model returning to it is a **regression**, not churn; **Match may FALL to 95** if P7 reclassifies `weapons` — a **correction, not a regression**, reported with its reason in the same sentence; the floor read from the provenance file **on whichever baseline P1 settled**; every figure derived at execution time. (5) **Write the day prompts** (`prompts/PLAN_PROMPTS.md`), each naming its branch, its deliverable and its gate. (6) **Record the risk register** with mitigations, and the acceptance criteria with each figure's source. (7) **Route every unresolved Known Unknown to the day that closes it** — all 30 must be either resolved in prep or routed.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_39/PLAN.md` — day-by-day schedule, per-day budgets, REPLAN exits, checkpoints, risk register, acceptance criteria
- `docs/planning/EPIC_4/SPRINT_39/prompts/PLAN_PROMPTS.md` — one prompt per day, each naming branch, deliverable and gate
- A pre-registered close-rule set, **each rule carrying its precondition**
- A routing table from every unresolved Known Unknown to the day that closes it
- A summary of the prep phase's refutations — **what prep found wrong, and what each changed**

**Unknowns:** *(integrates all)* — no new verification; consumes every verified unknown and routes the rest.

**Then close the task out:** `KNOWN_UNKNOWNS.md` needs no new verdicts from this task, but **confirm every unknown is either resolved or routed to a sprint day** and record that check; update `PREP_PLAN.md` (**Task 12 Status → ✅ COMPLETE (date)**, add **Time Spent**, fill **Changes** and **Result**, check off **all** acceptance criteria `- [ ]` → `- [x]`, prefix the Overview row with ✅); add a `### Sprint 39 Prep` entry to `CHANGELOG.md`; run **`make typecheck && make lint && make format && make test`** if any `*.py` changed (else state "docs only — quality gate N/A"); commit as `Complete Sprint 39 Prep Task 12: Plan Sprint 39 Detailed Schedule`; push; open a PR with `gh pr create`; and **wait for reviewer comments**, replying to each on its own thread.

---

## Appendix: Task-to-Unknown Quick Reference

| Prep Task | Branch | Unknowns **owned** (unless marked) | Priority | Est. |
|---|---|---|---|---|
| 2 — Re-Derive Baseline & Fingerprints | `planning/sprint39-task2` | *(contributes to, does not own)* 1.1, 2.2, 3.3, 4.1, 7.1, 10.1 | Critical | 3–4 h |
| 3 — Floor-Classification Decision Package | `planning/sprint39-task3` | 1.1, 1.2, 1.3 | Critical | 2–3 h |
| 4 — dyncge Second-Defect Diagnosis & Layer Trace | `planning/sprint39-task4` | 2.1, 2.2, 2.3, 2.4 | Critical | 5–7 h |
| 5 — lnts Fingerprint & Runtime-Probe Design | `planning/sprint39-task5` | 3.1, 3.2, 3.3 | Critical | 4–6 h |
| 6 — sarf's Four Call Sites | `planning/sprint39-task6` | 4.1, 4.2, 4.3, 4.4 | Critical | 5–7 h |
| 7 — Positional-vs-Declared-Domain Survey | `planning/sprint39-task7` | 5.1, 5.2, 5.3 | High | 4–5 h |
| 8 — Presolve-Record Remedy Design | `planning/sprint39-task8` | 7.1, 7.2, 7.3 | High | 3–4 h |
| 9 — Consultation Reply-Integration & Follow-Up | `planning/sprint39-task9` | 6.1, 6.2, 6.3 | Medium | 2–3 h |
| 10 — Epic-5 Design Scoping | `planning/sprint39-task10` | 9.1, 9.2 | Medium | 3–4 h |
| 11 — Backlog Catalog & Process-Infra Spec | `planning/sprint39-task11` | 8.1, 8.2, 8.3, 10.1, 10.2 | Medium | 3–4 h |
| 12 — Plan Sprint 39 Detailed Schedule | `planning/sprint39-task12` | *(integrates all)* | Critical | 3–4 h |

**Total:** **37–51 h across these 11 prompts** (the plan's ~40–55 h is the full 12-task figure — it includes Task 1, already ✅ complete at 3–4 h).

**Every one of the 30 unknowns is owned by exactly one task.** The table can read as contradicting this, because Task 2's row lists ids that also appear under Tasks 3–11 — those are **contributions, not ownership**, and are marked as such above. Task 2 re-derives the *figures* those unknowns rest on; the owning task does the verification. Task 12 integrates. Excluding Tasks 2 and 12, the owning sets partition all 30 ids exactly, with no id owned twice and none unowned — checked mechanically, not by eye.

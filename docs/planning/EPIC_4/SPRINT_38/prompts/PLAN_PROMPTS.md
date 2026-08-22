# Sprint 38 Per-Day Execution Prompts

**Covers:** Day 0 + Days 1–13. **P1 ganges Day 1 only (REPLAN'd)**; **P7 Days 2–3 (pulled forward)**; P6a/P6b Day 4 (they unblock Days 7 and 9); P2 sarf Days 5–7 with its REPLAN trigger at Day 6 end; P4 Day 8; P6d Day 9; P5 Days 10–11; **P8 Days 9–12**; checkpoints Days 5 and 10; final retest Day 13. Schedule: `../PLAN.md`.

> **⚠ RE-PLANNED 2026-08-19.** P1 REPLAN'd on Day 1 — #1668 direction 1 is a **no-op** and the asymmetry is manufactured downstream, so **neither direction is implementable at the rebind site** (`../DAY1_GANGES_CONTROL.md`). Direction A is banked, located, untested; owner decision: **HOLD**. Days 2–3 were void, so **P7 moved into them**, which lets **P8 start Day 9** and absorb P1's freed hours. **112 h total, max day 10 h.** Unknown **1.5 carries** — its measurement window needed a fix in the tree.

## How to Use

Paste one day's prompt per session. Each references the prep docs in `docs/planning/EPIC_4/SPRINT_38/` (this file is in `prompts/`, so sibling docs are `../<DOC>.md`). Per-day workflow: branch `planning/sprint38-dayN-<slug>` from `main` → work → quality gate ONLY if `*.py` changed → commit → push → PR → wait for review → on merge, "checkout main and pull".

## Cross-Cutting Rules (every day)

- **DERIVE FIGURES, DO NOT QUOTE THEM.** This is the sprint whose retrospective demanded it, and it is P6a's whole point. **The source of truth is `data/gamslib/gamslib_status.json`.** ✅ **The helper shipped on Day 4 — use it:**
  ```bash
  .venv/bin/python scripts/sprint_audit/kpi_block.py                 # markdown table
  .venv/bin/python scripts/sprint_audit/kpi_block.py --format line   # one-line summary
  .venv/bin/python scripts/sprint_audit/kpi_block.py --json          # machine-readable
  ```
  Every block it emits **carries the commit it was derived at**, and warns if the DB is uncommitted (the figures would not be reproducible from that SHA). **It deliberately does NOT emit the genuine floor** — that is not DB-derivable; it prints the mechanical count under a `NOT the floor` label and points at the provenance file (P6c). *("The DB" throughout these prompts means `gamslib_status.json`; it is the only KPI source, and the helper is a convenience over it, not a second one.)* **Any figure that must be quoted carries the commit it was measured at.** Sprint 37 corrected six stale figures in a prompt sweep and was re-staled by its own re-baseline **within 24 hours**; the same defect then reached its closeout twice. **No prompt in this file quotes a KPI — that is deliberate.**
- **The genuine floor baseline is 73**, not the 76 still written in older docs (owner decision, PR #1683 — S31–S37 overstated it by 3 via three out-of-corpus `non_convex` models). **Sprint 38 has no floor lever and no floor target.** Do not introduce one.
- **The leak gate is the defining discipline.** Emit-touching PRs must reach an **unqualified `LEAK GATE PASS`** — a `PARTIAL` verdict **fails** (the sweep narrowed), as does any `LEAK:` or `NO-OP:` line. **Never clear drift with `make regen-goldens`** — it launders the leak into the corpus. **sarf is the exception:** it has no golden, so `leak-check MODEL=sarf` reports `NO-OP`; its gate is `make check-goldens` (zero drift) **plus sarf newly producing a golden**.
- **`/tmp` control BEFORE `src/`** on every emit-touching change (PR24/PR27). **Run GAMS from a scratch directory, never the repo root** — GAMS writes scratch files to `cwd`, and a `git add -A` there swept 20 artifacts in Sprint 37.
- **Phase-0 doc BEFORE the `src/` commit** for `src/{ad,kkt,emit}` changes (CONTRIBUTING §392–447). P1 has `ISSUE_1667`, P2 has `ISSUE_1385`. Four canonical `###` subsections, extras permitted.
- **Count errors from GAMS's own `**** N ERROR(S)` line — never `grep -o '$NNN'`.** Marker counting undercounts **even when nothing is truncated** (one printed line can carry several codes), and separately GAMS truncates its listing with `Remaining errors not printed for this line`, which `errmsg=1` does **not** lift.
- **Prep-doc `file:line` fix surfaces are HYPOTHESES.** They were wrong ~4× in Sprint 27. Trace before implementing.
- **Standing bans:** `modelstat` asserted before every objective read · `x.up=inf` **BANNED** (mine) · the Case-c objective-gradient sign flip **BANNED** · the camcge **drop-row BANNED** (primal-correct, breaks the MCP dual).
- **No co-authored-by / no Claude-Code attribution** in commits or PRs; reply to each PR review comment **thread** individually.

---

## Day 0 Prompt — Baseline re-confirm + GO/NO-GO + the P3 send (~3 h)

Re-confirm the Day-0 baseline **by deriving it from `data/gamslib/gamslib_status.json` at execution time** — Solve, Match (cold + presolve split), Translate, `model_infeasible`, `path_syntax_error`, all-219, and the genuine floor. Compare against the S37 close recorded in `../../SPRINT_37/SPRINT_LOG.md`, and **report the floor as 73** (the re-baselined figure; older docs still say 76 and P6c owes the historical correction). Verify `git diff` against the S37 close shows **no `src/` change** — the prep cycle was docs-only.

**Then execute P3.** The decision is already made: **SEND** (`../CONSULTATION_DECISION_BRIEF.md`). Confirm the package is unchanged and the §4 toolchain stamp is still applied to `../../SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`. **The send is a human action** — flag it for the owner with the §5 copy-paste message. Once the owner confirms it went out, post §7's tracking comment to **#1462** and split `../../SPRINT_36/CONSULTATION_BUNDLE.md`'s three-action checkbox. Closes Unknown **3.3**.

**GO/NO-GO — report each condition explicitly:** (a) baseline re-derived and matching; (b) `make check-goldens` and `make leak-check` working on `main` at scope 163; (c) `ISSUE_1667` and `ISSUE_1385` present and conforming; (d) **all unknowns resolved.**

**⚠ Condition (d) FAILS, and you must say so rather than work around it.** Unknowns **1.1** and **1.3** are **Critical** and 🔍 INCOMPLETE. **That is a NO-GO for P1 as a landing track** — scope it that way: both are **unanswerable by construction** (contingent on a landable fix, and Task 4 proved direction 2 unbuildable), no further prep resolves them, and the other seven priorities do not depend on them. **P1 therefore enters as an EVALUATION, not a landing.** Record this in the Day-0 notes.

Docs/trace-only. **No PR**, or a docs-only trace-notes PR.

## Day 1 Prompt — P1: direction-C control, `/tmp` only (~7 h) ← first REPLAN gate

Branch `planning/sprint38-day1-ganges-control`. **PR24/PR27 control before any `src/`.**

Implement **#1668 direction 1** as a scratch patch — *rebind parameter indices consistently, so the variable and its sibling parameter move together* (`../GANGES_REBIND_PREDICATE_DESIGN.md` §3, direction **C**). **Direction 2 is refuted and must not be re-attempted:** Task 4 measured ganges and `prolog` **locally indistinguishable at the rebind site**, with `bound_indices` **empty for both** — there is no discriminator to build a predicate from. Direction C was deprioritised in Sprint 37 on intent grounds only, and is the cheapest untested replacement.

Then, **per model and never inferred across the pair** — ganges **and** gangesx: emit → compile → read **GAMS's own `**** N ERROR(S)` line** → assert `$141`/`$145`/`$149` are **0** and `gams rc` is **0**. Then sweep the corpus in scratch and confirm nothing outside `{ganges, gangesx, korcge}` is perturbed.

**REPLAN exit — take it the SAME DAY.** If direction C misses `rc=0` on either model, **or** perturbs anything outside that set: **stop.** Evaluate directions A and B **on paper only**, bank the result on **#1668**, and **move P1's remaining ~14 h to P8** (`../BACKLOG_CANDIDATE_CATALOG.md` — its catalog is already built for exactly this). Do **not** spend Days 2–3 nursing it; that pattern produced Sprint 36's reverted landing.

**Closes Unknown 1.1** either way — record the answer. `/tmp`-only; no `src/`. Docs/control-notes PR. Then wait for reviewer comments.

## Day 2 Prompt — P7: Phase-0 backfill, day 1 (~6 h) ← pulled forward from Day 9

Branch `planning/sprint38-day2-phase0-backfill`. *(This slot was "P1 `src/` land + leak gate"; it is void after the Day-1 REPLAN.)*

Backfill Phase-0 acceptance gates (`../PHASE0_COMPLIANCE_CATALOG.md`). Task 9 measured **43 open issues with no gate**; against 8–10 h that is ~12 minutes each, **which is not credible** for a gate needing a hand-derived KKT shape and a verification methodology. **Work top-down and stop at budget**, in **P8's shortlist order** — an un-gated issue **is not eligible for the P8 sweep**, so this is precisely what unblocks Days 9–12:

1. **#1331** — twocge, the two empty MCP pairs `eqpw.nu_eqpw` / `eqw.nu_eqw`
2. **#1062** — tricp, 108 × `Unmatched variable not free or fixed`
3. **#983 / #1325** — elec, division by zero → 30 × evaluation errors in `stat_x(iN)`

Each gate needs the four canonical `###` subsections (extras permitted). Use `../BACKLOG_CANDIDATE_CATALOG.md` §2.1 for the reproduced fingerprint and named fix surface — **but re-reproduce, do not quote**: anchored `^****` diagnostics, a terminal state read from GAMS's own line, runtime observation for runtime properties.

**Docs-only** — writing a Phase-0 gate touches no `src/`, so the quality gate is N/A. Then wait for reviewer comments.

## Day 3 Prompt — P7: Phase-0 backfill, day 2 + close (~4 h) ← pulled forward from Day 10

Branch `planning/sprint38-day3-phase0-backfill2`. The two candidates that need a doc **created**, not merely gated — Task 9's Tier 1 missed both:

- **dyncge** — 4 × empty-equation-unfixed on `eqpf2.nu_eqpf2`; **#1331's mechanism**, so it can borrow that shape
- **lnts** — the new defect: two `.fx` mechanisms contradicting, `y.lo = y.up = 0` while `y_fx_*` equations demand **5** and **45**, giving **MS-4 at iteration 0**. Fix surface is the `fix_rhs = "0"` fallback in `emit_gams.py`, which must skip tuples already carrying a `<var>_fx_<labels>` equation — **trace the line numbers; they are a hypothesis.**

**Also demote clearlak #1291 and turkpow #1316 out of Tier-1 priority** — both are **structurally excluded** from P8, so gating them buys P8 nothing.

**Report the remaining ~32 un-gated issues** as a standing backlog item. **Do not silently drop them** — that count is P7's honest deliverable alongside the gates.

**⚠ Do NOT attempt Unknown 1.5 here.** The original Day 3 measured dinam/indus/turkpow/clearlak *"while the fix is in the tree"*. **There is no fix in the tree** — P1 REPLAN'd. 1.5 **stays INCOMPLETE and carries**; recording anything else would restate their current failure, not answer the question. Then wait for reviewer comments.

## Day 4 Prompt — P6a derived-figure helper + P6b the two gate-scope assertions (~10 h)

Branch `planning/sprint38-day4-measurement-integrity`. **This day unblocks Days 7 and 9 — it is not an infrastructure aside. Do not reorder it later.**

**6a (~4 h). ✅ SHIPPED as `scripts/sprint_audit/kpi_block.py`.** Emits the **current** KPI block on demand, derived from the DB. Convert the day-prompt and sprint-doc templates from quoted figures to derived ones, and require any figure that must be quoted to **carry the commit it was measured at**.

**6b (~6 h).** Give both known narrowing modes an asserted scope and a **non-zero exit on an empty selection**:
- **`--resolve-changed` selects by git diff**, so uncommitted goldens are invisible — this produced a **false GO** in Sprint 37
- **`make leak-check MODEL=<id>` reports `NO-OP`** when the model has no golden — which is exactly how P2's gate fails for a non-correctness reason on Day 7

**Each needs a test that fails before and passes after** — that fail-before evidence is also what closes Unknown **6.1** (currently 🔶 design-verified). A check that silently narrows is a **false-negative generator, worse than no check**.

`*.py` changes ⇒ **run the full quality gate**: `make typecheck && make format && make lint && make test`. Then wait for reviewer comments.

## Day 5 Prompt — Checkpoint 1 + P2 sarf implementation day 1 (~9 h)

Branch `planning/sprint38-day5-checkpoint1-sarf`.

**Checkpoint 1 (~1 h).** Full pipeline via the `--resolve-changed` checkpoint. **Derive every figure** using the Day-4 helper. Record P1's disposition (landed / REPLANed) and any budget reallocation already made.

**P2 begins (~8 h)** (`../SARF_REARCH_DESIGN.md`). The change set is **atomic by construction**: the 2-D constraint gate + **S1 `constraint_jacobian.py:78`** + **S2 `index_mapping.py:634`** + **S3 in `stationarity.py`** + the parametric `stat_task` + `task.fx`, as **one unit**. A partial landing leaves multipliers with no stationarity coupling — an inconsistent MCP, and an explicit REPLAN rather than partial progress. **Trace the three sites before implementing**; the line numbers are hypotheses. Six corpus-safety call sites must be provably unperturbed.

**Do NOT re-attempt the memoization.** Sprint 37 measured it dead at **~5 %** against the **~66×** needed; the **927×** declared-vs-active column ratio (369,024 vs 398) is the only headroom. **Phase-0 doc (`ISSUE_1385`) before the `src/` commit.** Then wait for reviewer comments.

## Day 6 Prompt — P2 sarf implementation day 2 (~10 h) ← named REPLAN trigger, end of day

Branch `planning/sprint38-day6-sarf-impl2`. Continue the atomic change set.

**The REPLAN trigger is a single observable number, checked at end of day** (`../SARF_REARCH_DESIGN.md` §6): a bounded sarf run must show the **per-row call count dropping from 369,024 toward ~398**. It is visible **within minutes** using the §1.2 probe and **does not require the change to be complete**.

**If S1+S2 do not agree on the active column set by end of day, take the exit.** Take it **early rather than nursing it**. What the exit banks and does not invalidate: the row/column census, the measured call rate, the probe, the surrogate design, and the revised threshold. On exit, **P2's remaining ~6 h moves to P8**, and #1385 is re-scoped rather than closed. Then wait for reviewer comments.

## Day 7 Prompt — P2 sarf: the gate (~6 h) + P6c floor provenance (~4 h)

Branch `planning/sprint38-day7-sarf-gate`.

**P2's gate is inverted — do not rediscover this.** `make leak-check MODEL=sarf` **cannot work**: sarf has no golden, so it reports `NO-OP` and fails for a non-correctness reason. **Day 4's 6b is what makes that NO-OP loud rather than misleading.** The real gate:

- **`make check-goldens` — zero drift across the 163** (still pre-P4)
- **sarf newly produces a golden: 163 → 164**
- **sarf completes with a byte-stable golden, wall-clock ≤ 300 s on a nightly slot.** This is the **owner-decided** threshold (2026-08-18), revised from "single-digit seconds". **A result near ~141 s is the ACCEPTED outcome, not a shortfall** — the KPI is **+1 Translate**, which requires only that sarf *complete*. Do not treat 141 s as a REPLAN.
- `stat_task` matches the banked 7-term derivation with **symbolic** multiplier indices: `grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` must be **empty**
- determinism ×3. **sarf cannot be its own fixture** — at 369,024 columns the fail-before state does not terminate; use the surrogate.

**P6c (~4 h).** Ship the **provenance-carrying floor tracker**: a per-model partition file recording *why* each model counts toward the genuine floor. **A mechanical `Match − (presolve ∧ match)` count yields 65 and looks authoritative** — it is wrong, because the *"cold emit byte-identical to pre-fix"* qualifier lives only in the hand-partition. **6c also owes the historical re-baseline** that the owner decision left outstanding: S31–S37 actuals, `SUMMARY.md` row 37, and the memory files still say floor 76. Then wait for reviewer comments.

## Day 8 Prompt — P4: adopt the 22 Tier-1 presolve goldens (~10 h)

Branch `planning/sprint38-day8-presolve-goldens` (`../PRESOLVE_GOLDEN_ADOPTION_PLAN.md`).

**Adopt Tier 1 only — 22 of the 36.** The other **14 are deferred behind a per-model sign-off**, defaulting to *defer*: 7 are `mismatch`, 6 `skipped`, one is `mine` (`model_infeasible`). Adopting them pins **an emit that demonstrably does not reproduce its NLP solution** as the reference — and when someone later fixes it, the gate flags drift and the reflex is `make regen-goldens`, which is the laundering path the leak gate exists to prevent.

**Per golden:** regenerated from a clean `--only-solve` **in a scratch directory**; structurally correct (warm-start block, marginal→multiplier `.l` assignments, the **#1322 NA-guard** where the model needs it); **agreeing with its DB row**; byte-stable across `PYTHONHASHSEED {0,1,42}`. **Rejection ⇒ record it in `scripts/sprint_audit/golden_staleness_allowlist.txt` with a one-line reason**, next to the mechanism rather than in a planning doc.

**Raise `--min-scope` in the SAME commit**, derived from **`git ls-files 'data/gamslib/mcp/*.gms'`**. Do **not** derive it from the filesystem: that is the same quantity `discover_goldens()` starts from, so the assertion would compare a number to itself and always pass — the self-certification defect this priority is about, reappearing inside its own guard.

Scope moves **163 → 185**, discovered **170 → 192**. Re-measure CI runtime **from real CI runs, not locally** — the local machine is ~2× the runner, and extrapolating from it would falsely conclude "adoption blocks every PR". Then wait for reviewer comments.

## Day 9 Prompt — P4 close (~2 h) + P6d re-anchor (~2 h) + P8 sweep day 1 (~6 h)

Branch `planning/sprint38-day9-reanchor-phase0`.

**P6d — re-anchor the DB checkpoint** from `78ceaead` (four sprints stale) to the **S37 close**. **This must come after Day 4's 6b**: the re-anchor selects **0 models**, so re-anchoring first makes the checkpoint **silent** — it would pass by measuring nothing. 6b's scope assertion is what makes that loud.

**P8 begins here rather than Day 11** — that is what pulling P7 forward bought. Its gates were written Days 2–3, so the shortlist is eligible now. Work the pre-registered rule (`../BACKLOG_CANDIDATE_CATALOG.md`): **reproduced fingerprint AND named fix surface**; anything needing a new diagnosis is **banked, not started**. Start with **twocge** (#1331).

**⚠ P8 now runs AFTER P4's scope change.** P4 adopted on Day 8, so leak gates run at **185 in-scope, not 163**. Expected and harmless — P8's own models drift by design — but **state the scope in every gate result**, so a later reader is not silently comparing against 163. Then wait for reviewer comments.

## Day 10 Prompt — Checkpoint 2 (~1 h) + P5 (~4 h) + P8: the spurious-match investigation (~4 h)

Branch `planning/sprint38-day10-checkpoint2-p5`.

**Checkpoint 2.** Full pipeline via the **re-anchored** checkpoint (`--since-commit 8cffec29`); **figures derived, not quoted** — use `scripts/sprint_audit/kpi_block.py`.

> **⚠ RE-PLANNED 2026-08-21 (owner decision): Day 10's P8 slot is NOT tricp/elec.** It is an investigation into whether some recorded **presolve matches are spurious**. tricp moves to Day 11, elec to Day 12 — both already funded from P8's remaining 16 h.

**The hypothesis, from Day 9's CI failure.** A presolve emit warm-starts by writing the NLP's solution into the variables **before** the MCP solve, and reads the objective *after* it:

```gams
$include "data/gamslib/raw/<model>.gms"   * solves the NLP, sets <objvar>.l
Solve mcp_model using MCP;                 * if this ABORTS, .l is untouched
nlp2mcp_obj_val = <objvar>.l;              * still the NLP's own answer
```

**If the MCP aborts, the objective read returns the NLP's value and the comparison matches itself.** `weapons` is the discovered instance: **one `MODEL STATUS` in the whole listing** (the embedded NLP's, MS-2 @ 1735.5696), the MCP aborted with `EXECERROR = 1` and produced none — yet the DB records `model_optimal_presolve` + **match** @ 1735.5696, and a fresh pipeline run reproduces it.

**Do this, in this order:**

1. **Establish the discriminator first** — distinguish *"the MCP produced its own `MODEL STATUS`"* from *"only the embedded NLP did"*. **Do not key on `EXECERROR`**: `check_presolve_divergence.py`'s first branch already conflates MCP-side and NLP-side aborts, which is how weapons got reported as an *embedded-NLP* divergence when its embedded NLP solved correctly.
2. **Apply it to every model recorded `model_optimal_presolve`** (**30** as of Day 9) and report how many never produced an MCP status.
3. **Report before changing anything.** A non-zero count means the Match KPI is overstated — **that is a finding for the owner, not a number to quietly correct. Do NOT edit the DB or re-classify any model on Day 10.**

**REPLAN exit:** if the discriminator cannot be established from the listing alone, **say so and stop**. A partial heuristic applied to 30 models would manufacture a worse number than the one being checked.

**State the blast radius precisely, because it will be misread otherwise:** up to **30 presolve matches** are in question (Match 95 = 65 cold + 30 presolve). **Cold matches are unaffected** — there is no warm start to read back — so **the genuine floor of 73 is not at risk either way.** Say that explicitly.

**P5 (`../CAMCGE_EPIC5_HANDOFF.md`).** camcge is **Epic-5-scoped, not fixed here**: MS-4 against a *correct* NLP optimum is structural rank-deficiency, not an emit defect. The refutations are already consolidated as **B1–B4** — **B1 (drop-row) is the dangerous one: it is *primal-correct* and breaks the MCP dual silently.** Do **not** re-run any of them. Confirm #1330 is Epic-5-scoped and re-triage ≥1 residual model. Then wait for reviewer comments.

## Day 11 Prompt — P5 close (~2 h) + P8 sweep day 3 (~8 h): tricp #1062

Branch `planning/sprint38-day11-p8-sweep`.

**P5 closes** by recording the **10-model `license-gated` cohort** — `egypt`, `ferts`, `glider`, `robot`, `shale`, `sroute`, `srpchase`, `tabora`, `tfordy`, `turkey`. All emit correctly with committed goldens; all are rejected at **generation** (`solver_version: None`, PATH never invoked). **Excluded from KPI projections but NOT written off** — capacity is being actively pursued with the same people as the P3 consultation. Record the **ceiling (Solve +10)** and that they re-test as **one batch**. Closes Unknown **5.1** as a tracked **procurement** item, not an engineering result.

**P8 continues.** Next: **dyncge** (#1331's mechanism, so it can borrow that shape). **There are no Day-3 `$149` clears to take** — P1 REPLAN'd, so that pool never materialised.

**Re-reproduce every fingerprint; do not quote it.** Apply §4.1's four criteria: **anchored `^****` GAMS diagnostics** (a `.lst` contains echoed source too — an unanchored grep matched the emitter's own comment in prep); **a terminal state read from GAMS's own line**; **runtime observation** for runtime properties; and **a passing negative control**. The structural pattern behind the lnts defect was **wrong 5 times out of 6**. Then wait for reviewer comments.

## Day 12 Prompt — P8 sweep day 4 (~8 h): elec #983/#1325

Branch `planning/sprint38-day12-p8-sweep2`. Continue with **dyncge** (4 × empty-equation-unfixed on `eqpf2.nu_eqpf2` — #1331's mechanism, so it can borrow that shape) and **lnts**.

**lnts is the new defect found in prep.** The emitter has **two mechanisms acting on the same `.fx` cells**: the correct one emits `y_fx_y2_h50.. y("y2","h50") - 5 =E= 0`, while a blanket pruned-instance zeroing fires on exactly those cells, giving `y.lo = y.up = 0` against equations demanding **5** and **45** — hence **MS-4 at iteration 0**. Fix surface: the `fix_rhs = "0"` fallback in `emit_gams.py` must **skip tuples already carrying a `<var>_fx_<labels>` equation** — the same shape as the Sprint-33 P6 fix. **Trace the line numbers; they are a hypothesis.** Confirm with a **runtime bound probe**, not a source read.

**Rejected candidates stay rejected.** agreste and cesam require a **new diagnosis** and are banked, not started — that is the rule's whole purpose. Then wait for reviewer comments.

## Day 13 Prompt — Final Retest + Closeout (~6 h)

Branch `planning/sprint38-day13-close`. Final full pipeline retest under **≥3 `PYTHONHASHSEED`** values. Recompute the genuine-floor partition **from the provenance file** (P6c), never by hand.

**Apply the pre-registered close rules (`../PLAN.md` §9):**
1. **Three-gate firm-landing rule** — per-model Phase-0 gate + an **unqualified** leak-gate pass (a `PARTIAL` **fails**) + in `main`. Anything else is a **carryforward with a bounded next step**, not a partial win.
2. **`model_infeasible` may have risen to 9, and that is SUCCESS** — report it as a lateral move **in the same sentence as** the `path_syntax_error` fall. Alone, it reads as a regression.
3. **Report the floor from the provenance file, baseline 73.** If 6c's historical re-baseline did not land, say **pending re-baseline** rather than quoting 76.
4. **Derive every figure**; anything quoted carries its commit.

**Produce ALL FOUR closeout artifacts — the fourth is explicitly named because Sprint 37's Day-13 prompt omitted it and it was missed at close:**

1. `SPRINT_LOG.md`
2. `SPRINT_RETROSPECTIVE.md`
3. the Epic-4 `SUMMARY.md` row 38
4. **`SPRINT_39_CARRYFORWARDS.md`** — the per-sprint carryforwards file is an **unbroken S33→S38 convention**; write it regardless of what any prompt lists.

Then wait for reviewer comments.

# Sprint 38 Detailed Schedule (Day 0 + Days 1–13)

**Prep:** Tasks 1–11 complete (10 design/scoping docs + this schedule). **Anchor:** Day-0 *code* state = S37 close `8cffec29` plus the prep commits (docs-only). The `--resolve-changed --since-commit` / DB anchor is **still `78ceaead`** and **P6d re-anchors it to the S37 close** — see §3, where the ordering matters.
**Budget:** ≤ 12 h/day over 14 days; 168 h cap; nominal **116 h**, max day **10 h** (§8, verified mechanically). Risk **MEDIUM-HIGH** — P2 is a re-architecture that lands atomically or not at all, and P1 enters the sprint **without an implementable fix**.

**This sprint is deliberately NOT floor-targeted, and this schedule does not reinstate a floor target.** No carryforward can move the genuine floor: P1 is 0-bucket by construction, P2 is +1 Translate, P5 is license-gated, camcge is Epic-5. Naming that absence is the mitigation — it is the pressure to produce a floor gain that generated Sprint 36's reverted landing attempt.

---

## 1. Sprint 38 Goal

Land the Sprint-37 carryforwards. The prep phase changed this sprint's shape more than any before it: **six of the eight priorities were altered by a measurement**, and two were measured *down* to a fraction of their budget. The schedule below is built on what prep found, not on what the plan assumed.

**The single most important thing prep established: P1 has no implementable fix.** Task 4 measured that #1668 direction 2 — the direction the plan calls *"closer to the original intent"* — **cannot be built**: ganges and `prolog` are **locally indistinguishable at the rebind site**, with `bound_indices` empty for both. The predicate the whole priority rests on has no discriminator to be made of. Direction **C** (#1668 direction 1) is the cheapest untested replacement and is Day 1's entire job.

**The sprint's only KPI mover is P2**, and prep refuted its acceptance threshold too — the O(active) short-circuit projects to **~141 s, not single-digit seconds**. The owner accepted that (§2): the KPI is **+1 Translate**, which needs sarf only to *complete*.

## 2. Acceptance Criteria (honest projection)

| KPI | Day-0 (S37 close) | if P1 **and** P2 land | if only P2 lands | if neither lands |
|---|---|---|---|---|
| **genuine floor** | **73** | **73** | **73** | **73** |
| Solve | 108 | 108 | 108 | 108 |
| Match | 94 | 94 | 94 | 94 |
| Translate | 135 | **136** | **136** | 135 |
| path_syntax_error | 6 | **4** | 6 | 6 |
| model_infeasible | 7 | **9** | 7 | 7 |

**Five things this table deliberately does not claim.**

- **The floor does not move in any column.** There is no floor lever in this sprint. **Do not promise floor > 73.**
- **The floor baseline is 73, not 76** — the owner decision of 2026-08-18 (PR #1683). Sprints 31–37 overstated it by 3 because the provenance credits three **out-of-corpus `non_convex`** models (`ps2_f_s`, `ps2_s`, `ps3_s_gic`). **P6c owes the historical re-baseline**; until it lands, older docs still say 76.
- **P1's win is lateral, not a gain.** A fully clean cascade buys `path_syntax_error → model_infeasible`: **pse 6 → 4, mi 7 → 9**. Solve and Match are unchanged. **`model_infeasible` rising to 9 is the expected result of success**, and §9's reporting rule exists so it is not read as a regression.
- **P2 is +1 Translate and nothing else.** sarf recovering to translate does not imply it solves or matches.
- **P8 is Translate-stable, Solve-uncertain, Match-unclaimed** (Task 10 §5.2). Its five eligible candidates already emit; a fix moves them from *aborts at GAMS execution* toward a solve. **It is not a KPI projection.**

## 3. Sequencing Constraints (from the prep outputs)

Five constraints, each from a measurement rather than a preference. **Four are ordering constraints that a plausible-looking schedule would violate.**

1. **P1's full-corpus gate must run at the OLD scope (163), before P4 adopts** (Task 6 §5). P1 asserts *"only ganges/gangesx drift, `prolog` byte-identical"*; adding 22 goldens mid-track changes the comparison set and makes a clean P1 result **unattributable**. ⇒ P1 Days 1–3, P4 Day 8.
2. **P6b must precede P2's gate run** (banked Task 3/5). `make leak-check MODEL=sarf` reports **`NO-OP`** because sarf has no golden — it fails for a non-correctness reason. Running P2's gate before 6b gives a **misleading NO-OP** that looks like a P2 failure. ⇒ P6b Day 4, P2's gate Day 7.
3. **P6b must precede P6d** (banked Task 3). The re-anchor selects **0 models**, so re-anchoring first makes the checkpoint **silent** — it would pass by measuring nothing. 6b's scope assertion is what makes that failure loud. ⇒ 6b Day 4, 6d Day 9.
4. **P7 gates P8** (Task 10 §5 — *new this prep cycle*). **Not one of P8's 11 candidates has a Phase-0 gate, and 5 have no issue doc at all**, so under CONTRIBUTING §392–447 **zero are implementable**. P7's first block must be P8's shortlist. ⇒ P7 Days 9–10, P8 Days 11–12.
5. **P2 is atomic.** The 2-D constraint gate + S1/S2/S3 + `task.fx` land as **one unit**; a partial landing leaves multipliers with no stationarity coupling — an inconsistent MCP, and an explicit REPLAN rather than partial progress (Task 5 §3).

**Standing bans, unchanged:** `modelstat` asserted before every objective read · `x.up=inf` **BANNED** (mine) · the Case-c objective-gradient sign flip **BANNED** (refuted ×4) · the camcge **drop-row BANNED** (primal-correct, breaks the MCP dual — Task 8 §2 B1) · **never clear drift with `make regen-goldens`**.

## 4. Day 0 — Baseline re-confirm + GO/NO-GO + the P3 send (~3 h)

Re-confirm Day-0 = S37 close: **Solve 108 · Match 94 (65 cold + 29 presolve) · Translate 135 · mi 7 · pse 6 · all-219 97 · genuine floor 73** (the re-baselined figure, not the 76 in older docs). **Derive every figure from `data/gamslib/gamslib_status.json` at execution time** — do not quote this paragraph (P6a; §9). *("The DB" means that file throughout this plan.)*

**Then execute P3.** The decision was made in prep: **SEND** (Task 7). The package is complete and the channel is known — email to `ferris@cs.wisc.edu`, `steve@gams.com`, `sdirkse@gams.com`. **The send itself is a human action**; the agent's job is to confirm the package is unchanged, then post the §7 tracking comment to **#1462** once the send is confirmed.

**GO/NO-GO gate.**

| # | condition | source |
|---|---|---|
| a | Day-0 baseline re-derived and matching the S37 close | Task 2 |
| b | `make check-goldens` and `make leak-check` working on `main` at scope 163 | Task 6 |
| c | Phase-0 docs exist for every track that will touch `src/{ad,kkt,emit}` — **P1 (`ISSUE_1667`) and P2 (`ISSUE_1385`)** | Task 9 |
| d | **NOT satisfied — see below** | Task 4 |

**⚠ Condition (d) fails, and this schedule says so rather than working around it.** Two **Critical** unknowns are still 🔍 INCOMPLETE — **1.1** (does the cascade still reach `rc=0`) and **1.3** (does the narrowed predicate pass the full-corpus gate). Per the standing rule, *a Critical unknown left INCOMPLETE is a NO-GO condition*.

**Scope it correctly: this is a NO-GO for P1 as a landing track, not for the sprint.** Both unknowns are **unanswerable by construction** — each is contingent on a landable fix existing, and Task 4 established none does. They are not oversights; no amount of further prep resolves them. The other seven priorities do not depend on either.

**⇒ P1 enters the sprint as an EVALUATION, not a landing.** Day 1 is a `/tmp` direction-C control whose outcome *is* the answer to 1.1 and 1.3. **If Day 1 fails, P1 REPLANs to documentation on Day 1, not Day 3** — and the schedule below states where its budget goes.

Docs/trace-only. No PR, or a docs-only trace-notes PR.

## 5. Days 1–13

### Day 1 — P1: direction-C control, `/tmp` only (~7 h) ← **the sprint's first REPLAN gate**

Branch `planning/sprint38-day1-ganges-control`. **PR24/PR27 control before any `src/`.** Implement **#1668 direction 1** (Task 4 §3 direction C — *rebind parameter indices consistently, so variable and sibling parameter move together*) as a scratch patch. Direction C was prematurely deprioritised: Day 4 of Sprint 37 preferred direction 2 on intent grounds, and **direction 2 is the one that cannot be built**.

Then, per-model and never inferred across the pair: emit ganges **and** gangesx, compile, and **read GAMS's own `**** N ERROR(S)` line** — not a `grep -o '$NNN'` count, which counts only *printed* markers and undercounts even when nothing is truncated (Task 10 §4c). Assert `$141`/`$145`/`$149` → 0 and `gams rc` → 0.

**REPLAN exit — take it the same day.** Direction C does not reach `rc=0` on both models, **or** it perturbs a model outside `{ganges, gangesx, korcge}` in a scratch sweep ⇒ **P1 REPLANs to documentation immediately.** Evaluate direction A or B on paper only, bank the result on #1668, and **move P1's remaining ~14 h to P8** (the designated slack absorber, whose catalog is already built). Do **not** spend Days 2–3 nursing it — that is exactly the pattern that produced a reverted landing in Sprint 36.

**Closes:** Unknown **1.1**. `/tmp`-only. Docs/control-notes PR.

### Day 2 — P1: `src/` land + full-corpus leak gate **at scope 163** (~9 h)

Branch `planning/sprint38-day2-ganges-land`. Land direction C. Then the gate that refused Sprint 37, run **at the old scope of 163 goldens** (constraint 1 — P4 has not adopted yet):

- `make check-goldens` shows **ONLY ganges/gangesx drift**, with **`prolog` byte-identical** — the explicit criterion, since `prolog` is a live `model_optimal` + match model
- `--expect-drift ganges,gangesx,korcge` — `korcge` belongs in expect-drift, not the leak set: its drift is the benign `rPower` gate and it still solves **MS-1 Optimal @ 339.2130**
- **`--min-scope` asserted on discovery**, so a silent narrowing fails loudly
- slow-emit goldens (ganges **325 s**, gangesx **243 s**) on a **nightly** slot, not the PR gate; determinism ×3

**Closes:** Unknown **1.3**. **REPLAN exit:** any leak outside the expect-drift set, or `prolog` drifting ⇒ revert, bank on #1668, and re-scope P1 to documentation.

### Day 3 — P1: per-model Phase-0 gate + bucket verdict / REPLAN absorption (~5 h)

Branch `planning/sprint38-day3-ganges-verdict`. Run `ISSUE_1667`'s Phase-0 gate per model: emit → compile → `$NNN` = 0 → solve **cold AND presolve** with `modelstat` asserted → bucket. Expect the **lateral** move: `path_syntax_error → model_infeasible`, **pse 6 → 4, mi 7 → 9, Solve and Match unchanged**.

**Then close Unknown 1.5 while the fix is in the tree** — re-compile **dinam, indus, turkpow, clearlak** and record whether the general `$149` fix clears their `$149` half. 1.5 has been unanswerable all prep for want of an applied fix; this is the one hour in the sprint when it is answerable. **Read GAMS's own error total per model.** Any model that clears feeds P8's pool on Day 11.

**⚠ Do not re-scope P1 upward on a good result.** The bucket is **0** and the prep-era *"+2 or 0"* was refuted in Sprint 37 — the 6th blocker (embedded `ganges0` **MS-5 @ −386785.5017** vs standalone **MS-2 @ 6395.5444**) is untouched and `mcp_model` stays MS-4.

### Day 4 — P6a derived-figure helper + P6b the two gate-scope assertions (~10 h)

Branch `planning/sprint38-day4-measurement-integrity`. **This day unblocks Days 7 and 9 (constraints 2 and 3) — it is not an infrastructure aside.**

**6a (4 h).** Ship the `scripts/sprint_audit/` helper that emits the current KPI block **on demand from the DB**. This is the sprint whose retrospective demanded it: a Sprint-37 prompt sweep corrected 6 stale figures and was **re-staled by that sprint's own re-baseline within 24 hours**. Any figure that must be quoted **carries the commit it was measured at**.

**6b (6 h).** Give both known narrowing modes an asserted scope and a **non-zero exit on an empty selection**: `--resolve-changed` selects by **git diff**, so uncommitted goldens are invisible (this produced a false GO in Sprint 37), and `make leak-check MODEL=<id>` reports **`NO-OP`** for a model with no golden. **Each needs a test that fails before and passes after** — which is also how Unknown **6.1** closes (it is 🔶 design-verified; the live fail-before evidence is produced here).

### Day 5 — Checkpoint 1 + P2 sarf: implementation day 1 (~9 h)

Branch `planning/sprint38-day5-checkpoint1-sarf`. **Checkpoint 1 (1 h)** — full pipeline via `--resolve-changed`, figures **derived, not quoted** (6a is now available). Record P1's disposition.

**P2 begins (8 h).** The atomic change set: the 2-D constraint gate, **S1 `constraint_jacobian.py:78`**, **S2 `index_mapping.py:634`**, **S3 in `stationarity.py`**, the parametric `stat_task`, and `task.fx` — **one unit**. Six corpus-safety call sites must be provably unperturbed. **The `file:line` references are hypotheses**; trace them Day 5 before implementing (prep-doc fix surfaces were wrong ~4× in Sprint 27).

**Do not re-attempt the memoization.** Sprint 37 measured it dead at **~5 %** against the **~66×** needed; the **927×** declared-vs-active column ratio is the only headroom.

### Day 6 — P2 sarf: implementation day 2 (~10 h) ← **named REPLAN trigger, end of day**

Branch `planning/sprint38-day6-sarf-impl2`. **The trigger is a single observable number** (Task 5 §6): a bounded sarf run must show the per-row call count dropping from **369,024 toward ~398**. It is visible within minutes using the §1.2 probe and **does not require the change to be complete**.

**If S1+S2 do not agree on the active column set by end of day, take the exit.** Take it **early rather than nursing it** — a partial landing is an inconsistent MCP, not partial progress. What the exit banks: the row/column census, the measured call rate, the probe, the surrogate design, and the revised threshold — none invalidated by an incomplete build. On exit, **P2's remaining 6 h moves to P8**.

### Day 7 — P2 sarf: the gate (~6 h) + P6c floor provenance (~4 h)

Branch `planning/sprint38-day7-sarf-gate`. **P2's gate is inverted and this is the second time it has to be said:** `make leak-check MODEL=sarf` **cannot work** — sarf has no golden, so it reports `NO-OP` and fails for a non-correctness reason. **P6b (Day 4) is what makes that NO-OP loud instead of misleading.** The real gate:

- **`make check-goldens` — zero drift across the 163** (still pre-P4)
- **sarf newly produces a golden: 163 → 164**
- **sarf completes with a byte-stable golden, wall-clock ≤ 300 s on a nightly slot** — the **owner-decided** threshold (2026-08-18), revised from "single-digit seconds". **~141 s is the ACCEPTED result, not a shortfall**; holding the old threshold would convert a 927× win into a REPLAN
- `stat_task` matches the banked 7-term derivation with **symbolic** multiplier indices: `grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` **empty**
- determinism ×3 · **sarf cannot be its own fixture** (at 369,024 columns the fail-before state does not terminate)

**P6c (4 h):** ship the **provenance-carrying floor tracker** — a per-model partition file recording *why* each model counts. A mechanical `Match − (presolve ∧ match)` yields **65** against the recorded figure, because the *"cold emit byte-identical to pre-fix"* qualifier lives only in the hand-partition. **6c also owes the historical re-baseline** the owner decision left outstanding: S31–S37 actuals, the `SUMMARY.md` row 37, and the memory files still say floor 76.

### Day 8 — P4: adopt the 22 Tier-1 presolve goldens (~10 h)

Branch `planning/sprint38-day8-presolve-goldens`. **Tier 1 only — 22 of the 36** (Task 6). The other 14 are **deferred behind a per-model sign-off**: 7 are `mismatch`, 6 `skipped`, one is `mine` (`model_infeasible`). Adopting them would pin, as the reference, an emit that **demonstrably does not reproduce its NLP solution** — and when someone later fixes it the gate flags drift, whose reflex is `make regen-goldens`, i.e. the laundering path the leak gate exists to prevent.

Per golden: regenerated from a clean `--only-solve` **from a scratch directory**; structurally correct (warm-start block, marginal→multiplier `.l` assignments, the **#1322 NA-guard** where the model needs it); **agreeing with its DB row**; byte-stable across `PYTHONHASHSEED {0,1,42}`.

**Raise `--min-scope` in the same commit** — derived from **`git ls-files 'data/gamslib/mcp/*.gms'`**, not from the filesystem. The filesystem count is **vacuous**: it is the same quantity `discover_goldens()` starts from, so the assertion would compare a number to itself and always pass — the self-certification defect this priority is about, reappearing in its own guard.

**Scope 163 → 185, discovered 170 → 192.** CI runtime projects **~13.0–14.1 min against a 25-min budget**. **The local number is a trap** — 26.3 min here, ~2× the runner; extrapolating from it would have falsely concluded "adoption blocks every PR".

### Day 9 — P4 close (~2 h) + P6d re-anchor (~2 h) + P7 backfill day 1 (~6 h)

Branch `planning/sprint38-day9-reanchor-phase0`. **P6d re-anchors the DB checkpoint** from `78ceaead` (four sprints stale) to the **S37 close** — **after 6b**, because the re-anchor selects **0 models** and would otherwise pass silently by measuring nothing (constraint 3).

**P7 begins, and its ordering is Task 10's finding.** Task 9 measured **43 open issues with no Phase-0 gate** — against 8–10 h that is ~12 min each, **not credible**. So P7 works top-down and **stops at budget**, in P8's shortlist order: **#1331** (twocge) → **#1062** (tricp) → **#983/#1325** (elec).

### Day 10 — Checkpoint 2 (~1 h) + P7 close (~4 h) + P5 (~4 h)

Branch `planning/sprint38-day10-checkpoint2-p5`. **Checkpoint 2**, figures derived not quoted.

**P7 closes** with the two candidates that need a doc **created**, not merely gated — **dyncge** and **lnts**. Task 9's Tier 1 missed both, and demoting **clearlak #1291** and **turkpow #1316** out of Tier-1 priority is part of this: both are **structurally excluded** from P8, so gating them buys P8 nothing.

**P5 (4 h).** camcge is **Epic-5-scoped, not fixed here** — MS-4 against a *correct* NLP optimum is structural rank-deficiency. The refutations are already consolidated (**B1–B4**, with B1 flagged as the dangerous one: *primal-correct, breaks the MCP dual*). Confirm #1330 is Epic-5-scoped and re-triage ≥1 residual model.

### Day 11 — P5 close (~2 h) + P8 sweep day 1 (~8 h)

Branch `planning/sprint38-day11-p8-sweep`. **P5 closes** by recording the **10-model `license-gated` cohort** — `egypt`, `ferts`, `glider`, `robot`, `shale`, `sroute`, `srpchase`, `tabora`, `tfordy`, `turkey`: **7 % of the corpus**, all emitting correctly with committed goldens, all rejected at **generation** (`solver_version: None`, PATH never invoked). **Excluded from KPI projections but NOT written off** — capacity is being pursued with the same people as the P3 consultation. **Ceiling Solve 108 → 118**, re-tested as **one batch**.

**P8 begins**, working the pre-registered rule: **reproduced fingerprint AND named fix surface**. Order: **twocge** (#1331), **tricp** (#1062), **elec** (#983/#1325). Take any Day-3 `$149` clears first if they materialised.

**Every fingerprint must be re-reproduced, not quoted** — under Task 10 §4.1: anchored `^****` GAMS diagnostics (not echoed source — a `.lst` contains both); an asserted terminal state read from **GAMS's own line**; **runtime observation** for runtime properties; and **a passing negative control**.

### Day 12 — P8 sweep day 2 (~8 h)

Branch `planning/sprint38-day12-p8-sweep2`. Continue: **dyncge** (empty-equation-unfixed on `eqpf2.nu_eqpf2`, #1331's mechanism) and **lnts** (the new defect — two `.fx` mechanisms contradicting, `y.lo = y.up = 0` while the `_fx_` equations demand **5** and **45**, giving **MS-4 at iteration 0**). lnts's fix surface is the `fix_rhs = "0"` fallback in `emit_gams.py`, which must skip tuples already carrying a `<var>_fx_<labels>` equation — **the same shape as the Sprint-33 P6 fix**, and its line numbers are **a hypothesis to trace**, not a finding.

**Rejected candidates stay rejected.** agreste and cesam need a **new diagnosis** and are banked, not started — agreste as the highest-value bank (an **LP**, `verified_convex`, whose MCP is *locally* infeasible, which is structurally odd for a pure LCP).

### Day 13 — Final retest + closeout (~6 h)

Branch `planning/sprint38-day13-close`. Final pipeline retest under **≥3 `PYTHONHASHSEED`**; recompute the PR25 genuine-floor partition **from the provenance file** (P6c), not by hand.

**Produce all four closeout artifacts:**

1. `SPRINT_LOG.md`
2. `SPRINT_RETROSPECTIVE.md`
3. the Epic-4 `SUMMARY.md` row 38
4. **`SPRINT_39_CARRYFORWARDS.md`** ← **named explicitly.** Sprint 37's Day-13 prompt listed only the first three, so the carryforwards file was missed at close and had to be added afterward in a separate PR. The per-sprint carryforwards file is an **unbroken S33→S38 convention**; write it regardless of what any prompt lists.

## 6. REPLAN Exits — pre-registered, with where the budget goes

| track | trigger | day | budget reallocation |
|---|---|---|---|
| **P1** | direction C misses `rc=0` on either model, or perturbs anything outside `{ganges, gangesx, korcge}` | **Day 1** | ~14 h → **P8** |
| **P1** | any leak outside expect-drift, or `prolog` drifts | Day 2 | ~5 h → **P8** |
| **P2** | S1+S2 do not agree on the active column set — per-row calls not dropping 369,024 → ~398 | **Day 6, end of day** | ~6 h → **P8** |
| **P4** | a golden is non-reproducible or structurally missing an idiom its model requires | Day 8 | exclude it in `golden_staleness_allowlist.txt` **with a one-line reason**; continue |
| **P7** | budget exhausted before the shortlist completes | Day 10 | **report the remainder**; do not silently drop it |
| **P8** | a candidate's fingerprint fails re-reproduction under §4.1 | Days 11–12 | drop it, take the next; **no new diagnosis** |

**P8 is the designated absorber for every REPLAN**, which is why its catalog was built in prep with five eligible candidates against a threshold of two.

## 7. Known Unknowns Status

**28 unknowns: 17 ✅ VERIFIED · 5 ❌ WRONG · 3 🔶 PARTIALLY WRONG · 3 🔍 INCOMPLETE.**

**The 3 INCOMPLETE, and why none is an oversight:**

| # | priority | why it is open | closes |
|---|---|---|---|
| **1.1** | **Critical** | contingent on a landable fix; Task 4 showed direction 2 unbuildable | **Day 1** |
| **1.3** | **Critical** | there is no predicate to gate | **Day 2** |
| 1.5 | Medium | unanswerable without the cascade applied | **Day 3** |

**The two Critical ones are a NO-GO for P1 as a landing track (§4), stated rather than scheduled around.**

**The 3 PARTIALLY WRONG, each scheduled into the day that closes it:** **3.3** (would a reply be actionable) → **Day 0** with the send · **6.1** (do both gate-narrowing modes reproduce live) → **Day 4**, as 6b's fail-before evidence · **5.1** (is a licensed >1000-row environment obtainable) → **Day 11**, tracked as a **procurement** item, not resolvable by engineering.

## 8. Budget — verified mechanically

| day | content | h |
|---|---|---|
| 0 | baseline + GO/NO-GO + P3 send | 3 |
| 1 | P1 direction-C control | 7 |
| 2 | P1 land + leak gate @163 | 9 |
| 3 | P1 verdict + Unknown 1.5 | 5 |
| 4 | P6a + P6b | 10 |
| 5 | Checkpoint 1 + P2 impl 1 | 9 |
| 6 | P2 impl 2 + REPLAN trigger | 10 |
| 7 | P2 gate + P6c | 10 |
| 8 | P4 Tier-1 adoption | 10 |
| 9 | P4 close + P6d + P7 | 10 |
| 10 | Checkpoint 2 + P7 close + P5 | 9 |
| 11 | P5 close + P8 day 1 | 10 |
| 12 | P8 day 2 | 8 |
| 13 | final retest + closeout | 6 |
| | **total** | **116** |

**≤ 12 h/day: PASS (max 10) · < 168 h: PASS · within the 100–134 h band: PASS.**

| priority | scheduled | plan band | |
|---|---|---|---|
| P1 | 21 | 18–24 | ✅ |
| P2 | 24 | 20–28 | ✅ |
| **P3** | **1** | 4–6 | ⬇ **measured down** |
| P4 | 12 | 10–14 | ✅ |
| **P5** | **6** | 10–14 | ⬇ **measured down** |
| P6 | 16 | 14–18 | ✅ |
| P7 | 10 | 8–10 | ✅ top of band |
| P8 | 16 | 12–16 | ✅ top of band |
| retest | 4 | 4 | ✅ |
| overhead | 6 | — | baseline + closeout |

**The two priorities prep measured down, and where the 10 h went.**

- **P3: 4–6 h → 1 h.** The plan budgeted a *decision*. **Prep made it** (Task 7: **SEND**), the owner supplied the channel, and the package is ready to copy-paste. What remains is a **human action of ~30 minutes** plus posting a tracking comment. Budgeting 5 h would reserve time for a decision already taken.
- **P5: 10–14 h → 6 h.** The plan budgeted *writing* the Epic-5 handoff. **Task 8 found it already written** — `CGE_DEGENERACY_SCOPING.md` carried every substantive item, and a second document would have duplicated ~90 % of it. Prep patched the three real gaps in place. What remains is confirming #1330's scoping and re-triaging one residual model.

**Both freed hours go to the two priorities prep showed were under-budgeted** — P7 (43 un-gated issues against 8–10 h) and P8 (the REPLAN absorber). This is a re-allocation justified by measurement, not a schedule adjusted to fit.

## 9. Pre-registered Close Rules

**Fix these now, so a Day-13 result is read rather than argued.**

**1. The three-gate firm-landing rule.** A track counts as a **firm landing** only if all three hold: (a) its Phase-0 gate passes **per model**, never inferred across a pair; (b) the **full-corpus leak gate** passes **unqualified** — a `PARTIAL` verdict **fails**, because the sweep was narrowed, as does any `LEAK:` or `NO-OP:` line; (c) the change is in `main`. Anything else is a **carryforward** with a bounded next step, not a partial win.

**2. `model_infeasible` may rise to 9, and that is success.** P1's clean cascade produces `path_syntax_error → model_infeasible` — **pse 6 → 4, mi 7 → 9**. It **must be reported as a lateral move**, in the same sentence as the pse fall. Reported alone, a rising `mi` reads as a regression; it is the shape of P1 working.

**3. The floor is read from the provenance file, never re-derived by hand.** After P6c, the genuine floor comes from the per-model partition file. **A mechanical `Match − (presolve ∧ match)` count yields 65 and looks authoritative** — it is wrong, because the *"cold emit byte-identical to pre-fix"* qualifier exists only in the hand-partition. **The baseline is 73** (owner decision, PR #1683); if 6c's historical re-baseline has not landed, say the figure is **pending re-baseline** rather than quoting 76.

**4. Derive figures at execution time.** Every KPI in the closeout comes from the 6a helper. Any figure that must be quoted **carries the commit it was measured at**. Sprint 37 closed with a refuted figure in `SPRINT_LOG.md` §7 and a mid-sprint partition in its S36 comparison — both were accurate when banked and wrong when used.

## 10. Risk Register

| risk | likelihood | impact | mitigation |
|---|---|---|---|
| **Direction C fails like direction 2** | **Medium-High** | P1 → 0 | Day-1 `/tmp` gate; **REPLAN the same day**, 14 h → P8 |
| P2's atomic set cannot be made consistent | Medium | −1 Translate (the only KPI mover) | one observable number at Day 6 end; exit early |
| P4 adoption breaks CI runtime | **Low** | required check times out | measured on **real CI runs**, not locally; ~14.1 min worst vs 25-min budget |
| P7 under-budgeted vs 43 issues | **High** | backlog persists | scope to the shortlist; **report the remaining 32** |
| A P8 fingerprint is a false positive | Medium | a wasted slot | §4.1's four criteria, including **a passing negative control** |
| Stale figures reach the closeout | Medium | a wrong headline | P6a + close rule 4 |
| The floor is reported as 76 | **Medium** | a 3-model overstatement | close rule 3; 6c owes the historical re-baseline |

## 11. Related Documents

`KNOWN_UNKNOWNS.md` · `BASELINE_RECONFIRMATION.md` (T2) · `MEASUREMENT_INTEGRITY_DESIGN.md` (T3) · `GANGES_REBIND_PREDICATE_DESIGN.md` (T4) · `SARF_REARCH_DESIGN.md` (T5) · `PRESOLVE_GOLDEN_ADOPTION_PLAN.md` (T6) · `CONSULTATION_DECISION_BRIEF.md` (T7) · `CAMCGE_EPIC5_HANDOFF.md` (T8) · `PHASE0_COMPLIANCE_CATALOG.md` (T9) · `BACKLOG_CANDIDATE_CATALOG.md` (T10) · `prompts/PLAN_PROMPTS.md` · `../PROJECT_PLAN.md` (Sprint 38) · `../../../CONTRIBUTING.md` §392–447

---

**Document Status:** ✅ Complete — Sprint 38 Prep Task 11. Budget verified mechanically (116 h, max day 10 h). **P1 enters as an evaluation, not a landing** — two Critical unknowns are unanswerable until Day 1 runs, and that is recorded as a NO-GO for the track rather than scheduled around.
**Last Updated:** 2026-08-18 · **Owner:** Sprint 38 execution team

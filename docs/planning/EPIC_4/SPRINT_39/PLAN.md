# Sprint 39 Plan (Weeks 43–44) — Day-by-Day Schedule

**Sprint 39 Prep Task 12** · **Planned at:** `e754ec90` · **2026-09-02**
**Baseline:** Solve **111** · Match **96** (65 cold + 31 presolve) · Translate **135** · `path_solve_terminated` **0** · all-219 **99** · genuine floor **⚠ 73, 74 or 75 — P1 decides on Day 0**
**DB checkpoint anchor:** `9ab2c0c3` (Sprint-38 close)

> **⚠ "Weeks 43–44" are PROJECT-RELATIVE sprint weeks, not ISO weeks**, and the distinction matters because the two are seven weeks apart. ISO weeks 43–44 of 2026 are **2026-10-19 … 11-01**, but this sprint runs **2026-09-03 … 09-16**. The labels are consistent across the plan — Sprint 38 is "Weeks 41–42" and closed **2026-08-26**, which is ISO week **35**, so they cannot be ISO weeks. **Read the dates, not the week numbers**; the dates are what the 2026-09-09 gate is checked against.

> **⚠ Three things about this sprint that the schedule is built around.**
> **P1 is a decision, not work, and it blocks the sprint's own baseline** — nothing that reads the floor can be reported before Day 0 settles it.
> **P4's premise was refuted in prep.** Its four call sites are **0.5 %** of wall-clock and one is dead code; the 20–28 h estimate assumed otherwise. **Three branches are pre-registered below — the owner picks one on Day 0**, not on Day 7.
> **P6 cannot move.** The date gate is **2026-09-09**, which is **Day 6**.

---

## 1. The schedule

| Day | date | h | allocation |
|---|---|---|---|
| **0** | 2026-09-03 | 6 | **P1** 4h · **baseline** 2h |
| **1** | 2026-09-04 | 9 | **P2** 9h |
| **2** | 2026-09-05 | 10 | **P2** 7h · **P8** 3h |
| **3** | 2026-09-06 | 9 | **P2** 4h · **P8** 5h |
| **4** | 2026-09-07 | 10 | **P3** 10h |
| **5** | 2026-09-08 | 10 | **P3** 8h · **CK** 2h |
| **6** | 2026-09-09 | 10 | **P6** 6h · **P8** 4h |
| **7** | 2026-09-10 | 11 | **P4** 11h |
| **8** | 2026-09-11 | 11 | **P4** 11h |
| **9** | 2026-09-12 | 11 | **P4** 4h · **P9** 2h · **P10** 5h |
| **10** | 2026-09-13 | 11 | **CK** 2h · **P7** 9h |
| **11** | 2026-09-14 | 11 | **P7** 4h · **P5** 7h |
| **12** | 2026-09-15 | 11 | **P5** 6h · **P10** 5h |
| **13** | 2026-09-16 | 10 | **P10** 4h · **retest + close** 6h |

TOTAL **140 h** against a **168 h** cap; heaviest day **11 h**.

**Days are consecutive calendar days**, matching how prep ran (Tasks 1–12 spanned 2026-08-26 → 09-02 including weekends). Day 0 is the day after prep completes.

### Budget against the PROJECT_PLAN estimates

| priority | scheduled | estimate | |
|---|---|---|---|
| P1 | 4 h | 4–6 h | ✅ |
| P2 | 20 h | 16–22 h | ✅ |
| P3 | 18 h | 14–18 h | ✅ |
| P4 | 26 h | 20–28 h | ✅ |
| P5 | 13 h | 12–16 h | ✅ |
| P6 | 6 h | 6–10 h | ✅ |
| P7 | 13 h | 10–14 h | ✅ |
| P8 | 12 h | 10–14 h | ✅ |
| P9 | 2 h | 8–12 h | ⚠ **under** |
| P10 | 14 h | 12–16 h | ✅ |
| checkpoints | 4 h | — | |
| **baseline** (Day 0) + **retest + close** (Day 13) | 8 h | — | not a priority; the two non-priority blocks named in the schedule |

**P9 is deliberately under.** Prep Task 10 delivered the Epic-5 design in full — both open questions are now *proposed*, with a false-positive analysis and a corpus survey. What remains is recording it in the Epic-5 handoff, which is 2 h, not 8–12. **The freed ~8 h is not reallocated**; it is the sprint's slack, and the 140 h total sits 28 h under the cap deliberately.

## 2. Fixed points

| constraint | why | where it lands |
|---|---|---|
| **P1 on Day 0** | a decision that **blocks the baseline** — the floor is read from `data/floor_provenance.json` and every later report depends on which answer is taken | Day 0 |
| **P6 date-gated 2026-09-09** | cannot be pulled earlier; the consultation was sent 2026-08-26 | **Day 6 = 2026-09-09** ✅ |
| **P7 after P1** | it changes how the pipeline *records* solves; the baseline must be settled first | Days 10–11 |
| **P7 after Checkpoint 2** | the checkpoint reads the DB that P7 modifies — running it after would compare against a changed recording path | CK2 Day 10 **before** P7 starts |
| **P4 is the only track that can move a KPI UPWARD** | **+1 Translate → 136**, and the largest single cost. ⚠ It is *not* the only track that moves a KPI at all — **P7 moves Match 96 → 95**, but as a **correction** (C2), not a gain. The distinction is why C6 and C2 are separate rules | Days 7–9 |
| checkpoints | Day 5 and Day 10 | both `--resolve-changed --since-commit 9ab2c0c3` |
| final retest | ≥3 `PYTHONHASHSEED`, byte-identical | Day 13 |

## 3. REPLAN exits — the specific evidence, and where the budget goes

**A REPLAN is not a failure.** Sprint 38 absorbed a Day-1 REPLAN of its top priority without losing the sprint, because the exits were pre-registered.

### P2 — dyncge (Days 1–3)

| trigger | evidence | budget goes to |
|---|---|---|
| the residual persists as **`CASE_C_OBJDEF`** | `kkt_residual.py` after the offsets are corrected | **P5** (Days 11–12 widen). dyncge becomes a *documented divergence* with `modelstat` asserted, **not** a Match — elec's verdict changed this way as the classifier improved, so treat it as live |
| the fix drifts **any model other than dyncge** | `make check-goldens` | hand back to **#1381 Pattern C Phase B**; do not patch here |
| `stat_pq(HMN)`'s residual survives | `kkt_residual.py` per-row | a **second, independent defect** — bank it, do not widen Day 3 |

### P3 — lnts (Days 4–5)

| trigger | evidence | budget goes to |
|---|---|---|
| the probe **refutes** the two-mechanism collision | any of `LNTS_PROBE_DESIGN.md` §4's R1/R2/R3 | **P10** (Day 9/12/13). Bank the real mechanism; **do not widen the track** — the named fix would then address a mechanism that does not exist |
| the fix at `emit_gams.py:3121` does not clear MS-4 | GAMS listing, iteration 0 | bank and stop. The surface was already corrected once in prep (the banked `:3060–61` **never runs**) |

### P4 — sarf (Days 7–9) — ⚠ **three branches, owner picks on Day 0**

Prep Task 6 measured the four call sites at **0.5 %** of wall-clock, found **`gradient.py:453` is dead code**, and put **70.9 %** in `compute_constraint_jacobian` — a path Sprint 38 Day 7 already changed.

| branch | what Days 7–9 do | budget |
|---|---|---|
| **A — keep as scoped** | narrow the three live enumeration sites; accept a much smaller expected gain | 26 h as scheduled |
| **B — re-scope onto the differentiation path** | Day 7 becomes diagnosis + a new Phase-0 gate for `_diff_sum`; implementation is **not** attempted this sprint | 11 h; **15 h → P5 and P10** |
| **C — defer** | P4 does not run | 0 h; **26 h → P5, P10 and slack** |

**Mid-track REPLAN (branches A and B alike):** if a candidate narrowing still exceeds **300 s**, **stop and re-attribute rather than iterating.** §2 of `SARF_CALLSITE_PLAN.md` shows the dominant path is one Day 7 already touched, so a second timeout is evidence the lever is in `compute_constraint_jacobian`/`_diff_sum` — different work, different estimate.

### P6 — consultation (Day 6)

| trigger | response |
|---|---|
| **no reply** | post the pre-written follow-up (`CONSULTATION_FOLLOWUP_PACKAGE.md` §3). **It must not re-open the send decision** — five slips came from exactly that |
| **a non-actionable reply** | record it verbatim on the owning issue, note which of the three actionable forms it lacks, mark the thread **answered but not actionable**, and **send no clarifying question** |
| an actionable reply naming an option set | ⚠ **`src/` work with a quality gate, not a flag** — the scaffold takes a *strategy*, not option values; the literals are `forcing.py:73–74` and `:122` |

### P7 — presolve remedy (Days 10–11)

| trigger | response |
|---|---|
| Remedy A's attribution gate would reject a *non*-spurious row | `check_mcp_solve_attribution.py` over all 34 before landing |
| the back-fill breaks a consumer | `check_doc_figures.py`'s `dangling mcp_file_used rows` fact goes 14 → 0; **the docs must move in the same PR** |

## 4. Checkpoints and the final retest

| when | what | verdict rule |
|---|---|---|
| **Day 5** | `run_full_test.py --resolve-changed --since-commit 9ab2c0c3 --min-scope <n>` | **NO-GO on any `backward` bucket move or any `missing` row.** Re-solves every model whose emit golden changed; never persists |
| **Day 10** | same, **before P7 lands** | same. ⚠ Running it *after* P7 would diff against a changed recording path |
| **Day 13** | full retest + determinism **×3** `PYTHONHASHSEED`, byte-identical over the full golden scope | any drift is a landing failure, not churn |

**⚠ Two gate properties not to rediscover.** `make leak-check MODEL=sarf` reports `NO-OP` because sarf has no golden — the real gate is `make check-goldens` at full scope **plus sarf newly producing one**. And the leak gate is **load-dependent**: Sprint 37 needed `MAX_WORKERS = 3` on every run, because `ganges`/`clearlak` sit near the hardcoded 600 s budget.

## 5. Pre-registered close rules — each with its PRECONDITION

Format per Task 11's 8c spec. **A precondition may reference only a track's *start* state, never its outcome**; it is fixed here and cannot be edited at close; a rule whose precondition fails is **VOID, not unmet**, and the closeout says which failed.

| # | rule | precondition | if the precondition fails |
|---|---|---|---|
| **C1** | **`path_solve_terminated` maintains 0.** A model returning to it is a **REGRESSION, not churn** | **none** — a corpus-wide invariant, independent of every track | cannot be voided |
| **C2** | **Match may FALL to 95**, reported as a **correction, not a regression**, with its reason in the same sentence | **P7 started** | Match stays 96; the rule is void and the closeout says so |
| **C3** | **Three-gate firm landing:** a per-model Phase-0 gate **and** an *unqualified* leak-gate pass **and** in `main`. Two of three is not a landing | **none** — applies to every landing | cannot be voided |
| **C4** | The floor is read from `data/floor_provenance.json` **on whichever baseline P1 settled**, never from a mechanical DB count | **P1 decided on Day 0** | ⚠ **the sprint cannot report a floor at all** — escalate, do not improvise |
| **C5** | **Every figure is derived at execution time**, and any figure quoted in a doc carries the commit it was measured at | **none** | cannot be voided |
| **C6** | **+1 Translate → 136** is reported only if sarf newly produces a golden | **P4 branch A or B started** | void under branch C; report Translate 135 flat, with the deferral named |

**⚠ C1 and C3 and C5 take no precondition, and that is the evidence the mechanism is not an escape hatch.** If every rule needed one, preconditions would be gameable by construction. Three of six do.

**Reporting rule for C2, pre-written** (`PRESOLVE_RECORD_REMEDY.md` §5), to be used verbatim so the fall is never a bare number:

> **Match 96 → 95 is a CORRECTION, not a regression.** `weapons` was recorded as a **presolve** match, but the presolve retry's MCP produced no `MODEL STATUS` of its own… **This is not "weapons cannot be solved as an MCP"** — its **cold** emit solves, to `model_optimal` @ **1700.397**, a **2.03 %** divergence from the NLP and therefore a **mismatch**.

## 6. Acceptance criteria — with each figure's source

| criterion | baseline → target | source |
|---|---|---|
| Solve ≥ **111** | 111 → 111 | `kpi_block.py` |
| **Match ≥ 95**, and exactly 95 if P7 lands | 96 → **95** | `kpi_block.py` — the fall is **C2**, reported with its reason in the same sentence |
| Translate **135**, or **136** if P4 lands | 135 → **136** *(conditional)* | `kpi_block.py` — **C6**; void under P4 branch C |
| `path_solve_terminated` **= 0** | 0 → 0 | `kpi_block.py` — **C1** |
| genuine floor **≥ the P1 answer** | 73 → **73 / 74 / 75** | `floor_tracker.py` reading `data/floor_provenance.json` — **never** the mechanical DB count, which yields **65** and looks authoritative |
| determinism | — | Day 13, ×3 `PYTHONHASHSEED`, byte-identical |
| leak gate | — | `make check-goldens` at full scope, **unqualified**; `--min-scope` asserted on discovery |

**Tool paths**, given once so the table can use short names: `scripts/sprint_audit/kpi_block.py` · `scripts/sprint_audit/floor_tracker.py`. Both are run **at execution time** (close rule **C5**); `kpi_block.py` carries its commit and warns on a dirty DB.

**⚠ `Match ≥ 96` as originally written is superseded.** Task 8 established that P7's correction takes Match to 95 legitimately; a criterion demanding ≥ 96 would fail a correct correction.

## 7. Risk register

| risk | likelihood | mitigation |
|---|---|---|
| **P1 is not decided on Day 0** | medium — it is an owner call, open since Sprint 38 close | **C4 voids the floor report.** Escalate; do not improvise a figure |
| **P4's branch is not chosen** | medium — the same owner call, routed by Task 6 | Day 7 opens on branch **A** by default and REPLANs to **B** at the first 300 s timeout. Say so at Day 0 rather than discovering it |
| P2 lands but dyncge is `CASE_C_OBJDEF` | medium — elec's verdict changed this way | pre-registered exit; budget → P5 |
| P3's probe refutes the hypothesis | low — Task 5 confirmed it at runtime | bank; budget → P10 |
| a licence grant arrives mid-sprint | low | the three-stage cohort procedure is written (`CONSULTATION_FOLLOWUP_PACKAGE.md` §5); **Stage 0 costs no licence capacity** |
| the leak gate times out under load | **high — it did on every Sprint-37 run** | `MAX_WORKERS = 3`; assert `--min-scope` on discovery |
| a figure is quoted stale | **high — this recurred through prep** | C5; `make check-doc-figures` before every push |

## 8. Known-Unknown routing

**All 30 unknowns were resolved in prep** (11 ✅ · 11 ❌ · 8 🔶), so none needs routing to a day *to be answered*. What each resolution **feeds** is routed instead:

| unknowns | resolved as | consumed by |
|---|---|---|
| 1.1–1.3 | the floor decision package | **Day 0** (P1) |
| 2.1–2.4 | dyncge located, #1714 filed with a gate | **Days 1–3** (P2) |
| 3.1–3.3 | lnts confirmed at runtime, fix surface **corrected** | **Days 4–5** (P3) |
| 4.1–4.4 | P4's premise **refuted**; three branches | **Day 0 decision**, then Days 7–9 |
| 5.1–5.3 | 21-site catalog + two properties | **Days 11–12** (P5) and **Days 9/12/13** (P10) |
| 6.1–6.3 | both branches prepared; no reply as of 2026-09-02 | **Day 6** (P6) |
| 7.1–7.3 | remedy A+B; Match 96→95 | **Days 10–11** (P7) |
| 8.1–8.3 | 8a–8d specified with fail-befores | **Days 2, 3, 6** (P8) |
| 9.1–9.2 | Epic-5 design delivered, both answers negative | **Day 9** (P9, 2 h to record) |
| 10.1 | P10 **re-routed** off the backlog | **Days 9, 12, 13** (P10) |
| 10.2 | **closed as unreachable** | nothing — do not carry to Sprint 40 |

**⚠ 10.2 is closed, not routed.** Carrying it a third time is the phantom-upside pattern; `git log 9ab2c0c3..HEAD -- src/` returns zero commits, so its blocking precondition has not moved.

## 9. What prep found wrong — and what each changed

**19 of 30 assumptions were refuted or partially refuted — a 63 % refutation rate**, against Sprint 38's 32 %. The document's own success criterion is *"a prep phase that confirms everything has probably not looked hard enough."*

The ones that **changed the sprint**, not just a figure:

| # | the assumption | what prep found | what it changed |
|---|---|---|---|
| **4.2** | sarf's four call sites account for the remaining cost | **0.5 % of wall-clock**; `gradient.py:453` is **dead code**; 70.9 % is in `compute_constraint_jacobian` | **P4's estimate is unresolved.** Three branches pre-registered; owner decides Day 0 |
| **10.1** | ≥2 backlog candidates satisfy the selection rule | two qualify and **neither is available** — one is P3's track, one is a live consultation thread | **P10 re-routed** to landing Task 7's P2 property |
| **5.2** | the set-domain shape is as rare as the variable shape | **16 vs 5** — 8× — and **21 parameter** domains nobody had counted | P5's exposure is an order of magnitude larger |
| **7.2** | one remedy covers all affected presolve rows | **neither does** — two defect kinds sharing one row | P7 is **A + B together**, not one change |
| **3.2** | lnts's banked fix surface is `fix_rhs = "0"` | that surface **never runs**; the real blanket is `emit_gams.py:3121` | **Day 4 would have opened on dead code** |
| **9.1 / 9.2** | an automatic numéraire rule and a pre-solve degeneracy detector are achievable | **both no** — the detector scores precision 0, recall 0 | Epic 5 becomes a **retry loop**, not preprocessing |
| **8.1** | a layer field can be asserted without breaking existing gates | **60 gates, 59 would fail** | 8a is **added-only scoped**; measured 0 of 60 |
| **1.3** | the "still genuine" clause may not apply to twocge | the named precedent `polygon` is `likely_convex` **exactly like twocge** | **74 became a live answer** the plan had not considered |
| **10.2** | ganges's `$149` question is still worth carrying | **zero commits to `src/` since S38 close** | **closed as unreachable**; third carry refused |

**And three that cost nothing but would have cost a day each:** `weapons`'s cold emit **solves** (so the correction is not a failure record and `path_solve_terminated` stays 0); the three consultation figures **come from different emits** (so a reply had no unambiguous file to act on); and rocket's cold emit runs to **16,024** iterations, a figure appearing nowhere, which would have read as a contradiction to anyone re-measuring.

---

**Document Status:** ✅ Complete — Sprint 39 Prep Task 12. **GO for Day 0**, with two owner decisions outstanding: the floor (P1) and P4's branch.
**Last Updated:** 2026-09-02

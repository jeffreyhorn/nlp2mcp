# Sprint 39 — Sprint Log

**Weeks 43–44** *(project-relative, not ISO)* · **Days 0–13 = 2026-09-03 … 2026-09-16**
Plan: `PLAN.md` · prompts: `prompts/PLAN_PROMPTS.md`

---

## Day 0 — 2026-09-03 · P1: the floor-classification decision · 6 h

**Branch:** `planning/sprint39-day0-floor` · **Measured at:** `388082b0` · **No production code changed (`src/`, `tests/` untouched); `*.py` under `docs/` did change, so the quality gate was run — see below**

### Baseline, re-derived at execution time (close rule C5)

| quantity | value |
|---|---|
| convex candidates | 142 |
| Parse | 142 |
| Translate | **135** |
| Solve | **111** |
| Match | **96** (65 cold + 31 presolve) |
| model_infeasible | 7 |
| path_syntax_error | 6 |
| **`path_solve_terminated`** | **0** |
| path_solve_license | 11 |
| all-219 Match | 99 |
| **genuine floor** | **73 → 75** *(decided today)* |

Derived by `scripts/sprint_audit/kpi_block.py` and `floor_tracker.py`, not recalled.

### ✅ DECISION 1 — the genuine floor is **75**

**Owner decision, taken 2026-09-03.** Both `twocge` and `elec` owe provenance entries; `data/floor_provenance.json` now carries them with `expected_floor` **75**, and `floor_tracker.py` agrees (it exits non-zero on divergence).

**Every figure the brief rests on was re-verified before applying it**, because the brief was measured at `8a5a88bc` and close rule C5 requires derivation at execution time. Nothing had moved — **0 commits to `src/`, to the goldens, or to the DB** since — and all three cold solves reproduce exactly:

| model | cold status | cold objective | NLP | cold match? |
|---|---|---|---|---|
| **twocge** | **MS-1 Optimal** | **55.508** | 56.7778 | ✗ (−2.2 %) |
| **elec** | **MS-1 Optimal** | **244.624** | 243.8128 | ✗ (+0.33 %) |
| **polygon** *(the precedent)* | **MS-5 Locally Infeasible** | 0.766 | 0.7797 | ✗ |

And the convexity/corpus facts that decide the case: `polygon`, `twocge` and `elec` are all **`likely_convex` and in-corpus**; the `non_convex` `ps2_f_s` / `ps2_s` / `ps3_s_gic` are all **out-of-corpus** — the three the 2026-08-18 re-baseline removed.

**The reasoning applied.** The written definition classifies *methodology* as "cold emit byte-identical to pre-fix". Both models fail that test — each had its cold emit changed by a real fix, each was aborting beforehand (`path_solve_terminated`, `solver_version: None`), each MCP now produces its own status, and each matches via the presolve warm start, which the definition explicitly admits as genuine. `polygon` is the in-corpus precedent of identical shape. **Sprint 38 Day 9 applied the wrong test** ("matched via presolve ⇒ methodology"), which is what produced the flat-73 report.

**Consequence:** Sprint 39 opens at **floor 75**. "No floor regression" means **≥ 75**. Sprint 38's close record re-reads **73 → 75 (+2)**.

**Downstream sites updated in this change:** `data/floor_provenance.json` (2 entries + `expected_floor`), `SUMMARY.md` (the S38 row and its open-decision note), `PROJECT_PLAN.md` (P1's deliverable), `SPRINT_39/PLAN.md` (baseline + acceptance criterion).

### ✅ DECISION 2 — P4 takes **branch B** (re-scope)

**Owner decision, taken 2026-09-03**, on Task 6's measurement: the four call sites are **0.5 %** of wall-clock, `gradient.py:453` is **dead code**, and **70.9 %** sits in `compute_constraint_jacobian` — a path Sprint 38 Day 7 already changed.

Days 7–8 become **diagnosis of the differentiation path plus a Phase-0 gate for it**. **No implementation this sprint.** P4 drops **26 h → 11 h**.

**Where the freed 15 h went.** P5 and P10 each rose to the **top of their own estimates** (13 → 16 h, 14 → 16 h), absorbing **5 h**. The remaining **10 h returned to slack** — neither can take more without exceeding its band, and inflating a track to spend a budget is what P10 exists to prevent. **Sprint total 140 h → 130 h**, heaviest day 11 h.

**⚠ Consequences, both pre-registered:**
- **C6 is VOID.** Translate reports **135 flat**, naming the re-scope.
- **The sprint has no upward KPI mover.** Its only KPI movement is P7's Match **96 → 95**, a *correction* (C2). That is the honest shape given P4's premise was refuted, not an underperformance.

**⚠ C6's precondition was also corrected today.** It read *"P4 branch A or B started"* — but branch B explicitly does not implement, so it can never produce a golden. Fixed before the sprint runs rather than discovered at close, which is exactly what 8c's precondition discipline is for.

### Gate

- `floor_tracker.py` → **75**, agreeing with the recorded decision, **exit 0**
- `artifacts/validate_plan.py` → **PLAN VALIDATES** after the re-budget
- `make check-doc-figures` → clean
- Quality gate **RUN, not waived** — `src/` and `tests/` are untouched, but `artifacts/validate_plan.py` was extended during review, and it is `*.py`. typecheck / format / lint clean; `make test` **5301 passed / 10 skipped / 1 xfailed**.
  - ⚠ This line originally read *"N/A — no `*.py` changed"*, which was **true when Day 0 was written and false by the time the PR merged** — the review rounds added the validator. The waiver test is now stated over `src/`/`tests/`, which a review round cannot invalidate. Same aging-out class as the banked-staleness findings: **a claim about a PR's contents must be re-read against the PR's final file list, not its first commit.**

---

## Day 1 — planned 2026-09-04, **executed 2026-09-03** · P2: dyncge — confirm the layer · 9 h

**Branch:** `planning/sprint39-day1-dyncge` · **Measured at:** `8aae26f4` · **No `src/` change — this day was scoped to confirm the layer, not to implement**

### Fail-before, reproduced before anything else

Residual **`CASE_B`**, max rel **6.22e-02** at `stat_pf(CAP,SRV)`; the five top rows match the prep record at `37665091` **in the same order**. Structural: **6** `nu_eqXp(j±k)` + **6** `nu_eqII(j±k)`, **12** `$(ord(h) = k)` guards, offsets **±1..±3**, `ord(h)` ∈ {1,2,3} while `h` has **2** members, **0** occurrences of the correct `nu_eqXp(i)`.

The package had **not** rotted — worth stating explicitly, since the standing lesson is that a long-carried package rots in place.

### The layer is CONFIRMED but REFINED — and the refinement is the day's result

`ISSUE_1714` named `stationarity.py` ~7107–7131 and labelled it a hypothesis. Traced with `docs/planning/EPIC_4/SPRINT_39/artifacts/trace_dyncge_layer.py` (line tracer over the real emit + wrapped recognisers), **not read**:

- The named surface **does execute** — 91 hits at the branch, 216 at guard construction. It is real.
- But the suppression that would stop the offsets being *born* **never fires once**: 0 hits, and `allow_nonzero_offsets` stays `True`.
- **All four** Pattern-C recognisers miss `pf` (0 claimed / 56 calls). Two claim elsewhere in dyncge (B-1 ×1, B-3 ×2), so the machinery works — it does not recognise **this shape**.

**Single shared cause:** B-1/B-2/B-3 each require a **single-index `Sum`** (`len(index_sets) == 1` at lines 604 / 743 / 949); the launch-shape gate requires a `$` condition dyncge lacks. dyncge's term is `sum((h,j), pf(h,j)*F(h,j))` — a **two-index Sum binding both of `pf`'s coordinates with the equation index `i` free and unrelated**. B-3's *dimension* gate passes (1 < 2); the miss is the **Sum's arity**, not the dimension mismatch.

So ~7107–7131 is the **symptom** site and ~6290–6455 is the **birth** site. Fixing the named surface would suppress the guard, not the offsets.

**This is why the day was scoped to a trace.** Three of four Sprint-38 gates named the wrong layer; this one named a real code path that is nonetheless the wrong place to fix. Implementing against the banked surface would have produced a guard-suppression patch that leaves the wrong answer intact — and the emit would still have compiled and solved MS-1, which is exactly how this defect stayed silent.

### Checked before proposing new logic (S38-D12 rule / P8 8b)

**No existing member covers this population.** The nearest — B-3 — handles a variable whose *equation index binds one coordinate* while the sum binds the other (cesam2 `COLSUM(jj).. sum(ii, TSAM(ii,jj))`). Here the equation index binds **neither**. A distinct Pattern-C member, not a widening of B-3.

### Carried into Day 2

- ⚠ **`eqSp` (line 420) carries the identical `sum((h,j), pf*F)` term.** Scalar-domain, so a different branch — **verify, do not assume**.
- The `stat_pq(HMN)` open question stands; `stat_pq` remains the negative control and must stay byte-identical.
- Route is **#1381 Pattern C Phase B**, which `ISSUE_1714` listed as a REPLAN exit. On this evidence it is the **expected** route, not a fallback.

### Gate

- Fail-before reproduced (residual + structural), both recorded above
- **No `src/` or `tests/` change**; the only `*.py` is the new `docs/planning/EPIC_4/SPRINT_39/artifacts/trace_dyncge_layer.py`, so the quality gate was **run rather than waived**

---

## Day 2 — planned 2026-09-05, **executed 2026-09-04** · P2: dyncge — the new Pattern-C member · 7 h

**Branch:** `planning/sprint39-day2-dyncge` · **Measured at:** `9ee4fe0f` · **`src/` CHANGED — quality gate run**

### ⚠ PROCEED is NOT met. This is a corpus-safe PARTIAL fix.

| control | result |
|---|---|
| 1 · residual `CASE_A` | ✗ **`CASE_B` @ 6.26e-02** (`stat_pf(CAP,SRV)`) — eqII unfixed |
| 2 · structural | ◐ `nu_eqXp(j±k)` **6 → 0** ✓ · `nu_eqII(j±k)` **6** ✗ · `$(ord(h)=k)` **6** ✗ |
| 3 · negative control | ✓ `stat_pq` **byte-identical** |
| 4 · leak gate | ✓ **dyncge alone** (186 checked, no timeout), against a **measured zero-drift baseline** |
| 6 · determinism ×3 | ✓ identical MD5 across `PYTHONHASHSEED` 0/1/42 |
| — · tests | ✓ 5301 passed / 10 skipped / 1 xfailed |

### `eqSp` — the day's first task, discharged

**Verified by trace, not assumed: `eqSp` does NOT reach the cascade.** Only the four *indexed* equations reach line 6292 for `pf`; `eqSp` is scalar-domain and the cascade lives inside `_add_indexed_jacobian_terms`, so the exclusion is **structural**. Its emitted term `((-1) * (ssp * f(h,j))) * nu_eqSp` already matches the hand-derivation.

### The nearest member is B-2, not B-3 — a correction to Day 1

B-2 fails on the `Sum`'s **arity alone**; its condition gate, canonical-overlap gate (`common = {i}`) and single-pattern guard all already pass for dyncge. Day 1 named B-3, which is right about the *dimension relationship* and wrong about *body shape*. B-2 is still not widened: its walker descends only through `*`, and dyncge's `Sum` sits inside `(sum(...) - Sp - Td)` under a division, so relaxing its arity gate would not even reach this shape.

### ⚠ The discriminator took TWO wrong attempts, and both failed SILENTLY

The condition is **same set root, different symbol**. Neither half alone works:

1. **Canonical sets only** — matched **nothing**. Under `Alias (i,j)` the variable's `j` resolves to `i`, so the test reported "related" for exactly the shape it existed to catch. **That is the same conflation that produces the defect.**
2. **Symbols only** — matched the **whole corpus**. 10 goldens drifted against a **measured baseline of zero**: agreste, egypt (**−28 KB**), fawley, shale, tforss, turkey. These are ordinary full-collapse shapes the standard path **already emits correctly** — B-4 was rewriting working emits.

⚠ **Attempt 2 passed `make test`, `typecheck` and `lint`.** Only the leak gate *against a measured baseline* caught it. I had also guessed egypt/shale drift was pre-existing (they carry a known live emit defect); the baseline run refuted that — **all 10 were mine**.

### ⚠ A second silent bug in the builder

Differentiating the whole body at the `Sum`'s own bound names produced `sum((h__,j__), f(h__,j__))` — F summed over **every** instance where the correct coefficient is `f(h,j)` at the head instance. It compiled and would have been silently wrong: **the same failure class as the defect under repair.** Fixed with an explicit chain-rule split (placeholder substitution for the outer factor, sum-body derivative for the inner).

### Carried to Day 3 — the `eqII` route (the landing decision is TAKEN; see below)

`eqII` is a **second, distinct member**, not a gap in B-4:

```gams
eqII(j).. pk*II(j) =e= pf('CAP',j)**zeta*F('CAP',j) / sum(i, pf('CAP',i)**zeta*F('CAP',i)) * (Sp + eps*Sf);
```

A **literal `'CAP'`** in `pf`'s first coordinate, `pf` both inside and outside the `Sum`, and the `Sum` binding only **one** coordinate. B-4 declines on both its full-collapse requirement and its single-pattern guard — correctly.

### ✅ OWNER DECISION 2026-09-05 — land B-4 as a PARTIAL fix

The verified half is banked rather than held or handed back. **What this decides, and what it does not:**

- **Decided:** B-4 lands. `eqXp` is fixed, corpus-safe (186 goldens clean, no timeouts), `stat_pq` byte-identical, 3 mutation-verified tests.
- **NOT decided:** `eqII`. It remains open, and **dyncge is still wrong** — the residual stays **`CASE_B` @ 6.26e-02**. Day 3 still chooses between the literal-index member and the **#1381** Pattern C Phase B hand-back.
- **⚠ No KPI moves.** dyncge does not become a Solve or Match gain, because it does not yet reach `CASE_A`. The committed golden encodes a **less-wrong but still incorrect** emit. Anyone reading `dyncge_mcp.gms` as correct would be misled — `ISSUE_1714` stays **OPEN** and says so.
- **⚠ The PROCEED signal was not met and was not waived.** Landing here is a scope decision about banking verified work, not a judgement that the acceptance gate passed.

---

## Day 3 — 2026-09-06 · P2: verify or hand back · 4 h · + P8 8a/8b · 5 h

**Branch:** `planning/sprint39-day3-dyncge` · **Measured at:** `74c5efba`

### P2 — VERIFY FAILED; `eqII` HANDED BACK to #1381

| control | verdict |
|---|---|
| 1 · residual `CASE_A` | ❌ **`CASE_B` @ 6.26e-02** |
| 2 · structural | ❌ `nu_eqXp(j±k)` 0 ✓ · `nu_eqII(j±k)` **6** ✗ · `$(ord(h)=k)` **6** ✗ |
| 3 · negative control | ✅ `stat_pq` byte-identical to the pre-B4 golden |
| 4 · leak gate | ✅ 186 checked, all clean, no timeouts |
| 5 · determinism ×3 | ✅ 1 distinct hash |
| 6 · objective | — not re-measured; decided by 1–2 |

Hand-back package in `ISSUE_1714` §*Day-3 verdict*: what `eqII` needs that no member has (literal coordinate; variable in numerator **and** denominator sum; eq index binding the non-literal coordinate), and what B-4 already proves reusable.

### ⚠ A CORRECT PARTIAL FIX MADE THE TOP ROW WORSE

`stat_pf(CAP,SRV)` **6.22e-02 → 6.26e-02** after `eqXp` was corrected. Two wrong terms had been partially cancelling; removing one exposed the other. Only `stat_pf(LAB,SRV)` improved (4.26 → 3.87e-02); three rows unchanged.

**Residual magnitude is NOT a progress metric for a row with more than one defect.** Only `CASE_A`, or a per-term hand-derivation, is valid. Recorded because it would mislead whoever takes `eqII`.

### ⚠ The third REPLAN exit could NOT be discharged

`stat_pq(HMN)` is completely insensitive to the fix (5.90e-02, unchanged), but that exit's premise is *"correcting `stat_pf`"* — and `stat_pf` is only **partially** corrected. Open in both directions; recorded, not absorbed.

### ⚠ SCOPE SLIP FOUND — P8 8a was never landed

Day 2 spent its full budget on P2 and dropped its 3 h of P8 without recording it. `check_phase0_doc.py` and `phase0-gate.yml` were last touched in **Sprint 37**. Since 8a and 8b share the *added-only* mechanism, both landed today.

### P8 8a + 8b

- **Mechanism:** `pulls.listFiles` already returns `status`; the workflow discarded it. It now emits `status\tfilename`, and the checker parses it — **bare paths still work**, and a bare path is treated as *not added*, so the legacy format can never tighten the gate by accident.
- **8a:** an added doc must carry a `**Layer:**` line.
- **8b:** an added doc must carry `### Nearest Existing Mechanism` **and record why it does not apply** — naming one is not enough.
- **⚠ ADDED-ONLY BY DESIGN.** Unconditional requirements would retroactively fail **all 39** conforming issue docs. A gate that goes red on untouched history gets switched off, and a switched-off gate protects nothing.
- **3 mutants killed** (8b removed · 8b why-not check removed · 8a removed). `ISSUE_1714` backfilled as a worked example — it passes even when treated as *added*.

### Gate

typecheck / format / lint clean · `make test` **5310 passed** / 10 skipped / 1 xfailed (+6) · leak gate 186 all clean

---

## ⚠ SCHEDULE DRIFT — execution is running AHEAD of the plan's calendar

Recorded 2026-09-06, after review flagged a Day-4 entry dated **in the future relative to its own commit**. Derived from commit dates, not recalled:

| day | plan date | actually executed | drift |
|---|---|---|---|
| Day 1 | 2026-09-04 | **2026-09-03** | 1 day early |
| Day 2 | 2026-09-05 | **2026-09-04** | 1 day early |
| Day 3 | 2026-09-06 | 2026-09-06 | on plan |
| Day 4 | 2026-09-07 | **2026-09-06** | 1 day early |

Day headings are **plan labels**; where they differ from execution, both are now shown. The earlier headings asserted the plan date as though it were the date of the work.

### ⚠ THIS HAS A CONSEQUENCE FOR P6, AND IT IS NOT COSMETIC

**Day 6's P6 gate is `2026-09-09` — a CALENDAR date, not a day-number.** The prompt's *"This day cannot move"* constrains the **date**. At the current pace Day 6 is reachable on **2026-09-07 or 08**, i.e. **before the gate date**.

**If Day 6 is executed early, P6 must still wait for 2026-09-09.** Posting the follow-up sooner shortens the consultation window the gate exists to provide, and the five prior slips all came from re-opening that decision. Running the rest of Day 6 early is fine; **the send is date-bound.**

---

## Day 4 — planned 2026-09-07, **executed 2026-09-06** · P3: lnts · 10 h

**Branch:** `planning/sprint39-day4-lnts` · **Measured at:** `6fa78b12` · **Docs only — `src/`, `tests/`, `data/` untouched; no `*.py` in the PR**

### ✅ The banked hypothesis is CONFIRMED at runtime — its first actual test

Criteria were fixed in advance (`LNTS_PROBE_DESIGN.md` §4, committed 2026-08-31) and honoured. Probe injected into a **copy** in a scratch dir.

| tuple | `_fx_` demands | effective bounds | criterion |
|---|---|---|---|
| `y("y2","h50")` | **5** | `lo = up = 0` | **C1 ✓ C2 ✓** |
| `y("y3","h50")` | **45** | `lo = up = 0` | **C1 ✓ C2 ✓** |
| `y("y4","h50")` | 0 | `lo = up = 0` | **C3 ✓** consistent — probe not over-reporting |

`MODEL STATUS 4`, **ITERATION COUNT 0**. **No refute criterion fires.** A hypothesis carried since Sprint 38 on a source read alone now has a runtime observation behind it.

### The layer — traced, and prep is VINDICATED

`emit_gams.py:3061` (the banked `fix_rhs = "0"` fallback) **never fires**; **`:3121` emits the killing blanket**. Both prep claims hold.

⚠ **An intermediate run of mine said `:3091`, and that was my own tracer bug** — it attributed list growth to the line where growth was *observed* (the loop header) rather than the line that executed the append. I nearly reported prep as wrong. Fixed by attributing to the previously-executed line in the same frame. **Third time this sprint a measurement artifact of mine nearly became a reported finding.**

### Root cause — sharper than "the blanket is wrong"

`_compute_suppressed_fx_equations` (`:874`) already handles this conflict class by **suppressing** the `_fx_` equation — deciding membership against **`kkt.stationarity_conditions`**. But the section-1b blanket at `:3121` fires on a **different** condition, `infer_lead_lag_condition` (cached at `:3080`).

**A cell can be inside the stationarity condition — so its `_fx_` equation survives — yet outside the lead/lag condition, so the blanket zeroes it.** lnts's `h50` cells are exactly that gap.

This **rules out** a tempting fix: extending the suppression to the lead/lag condition would **drop** the `_fx_` equations demanding 5 and 45, which are real boundary conditions from the source.

### Carried to Day 5 (P3 finish, 8 h + Checkpoint 1)

Exclude cells carrying a surviving `_fx_` equation from the `:3121` blanket. Reuse `_fx_eq_name()` (`:711`) and the `suppressed` set (`:920`). ⚠ **Add a positive exclusion; do not widen the lead/lag condition** — section 1b serves the whole corpus, and Day 2 measured what a loosened predicate costs (10 goldens vs a zero-drift baseline). ⚠ `cesam` stays out of scope: same signature, **0 `_fx_` equations**.

---

## Day 5 — planned 2026-09-08, **executed 2026-09-07** · P3: lnts *(planned as "finish")* · 8 h · + Checkpoint 1 · 2 h — ⚠ **REPLAN: banked, not landed**

**Branch:** `planning/sprint39-day5-lnts` · **Measured at:** `c1ad2bfd`

### ⚠ VERDICT: REPLAN. The mechanism is BANKED, not landed. `src/` is reverted.

The fix was implemented at the section-1b blanket Day 4 traced, measured against the **PROCEED/REPLAN signal fixed in advance** in `ISSUE_1694` — and it **fails that signal**. The `src/` change and all three goldens are **reverted**; only the findings are kept.

| PROCEED requires (all four) | result |
|---|---|
| cells no longer blanket-zeroed | ✅ bounds at `h50` `lo = up = 0` → free |
| `_fx_` equations remain **and bind at 5 / 45** | ❌ **`y2.h50` = 4.8997, `y3.h50` = 41.9700 — both `INFES`** |
| PATH iterates | ✅ MS-4 @ iter 0 → MS-5 @ **1508** |
| **nothing outside `lnts` drifts** | ❌ **`robot` and `springchain` drifted** |

**Two REPLAN conditions fire:**

1. **"perturbs any of the five other models that match the source pattern but are not defective"** — **`springchain` is named in that list** and its emit changed. Its behaviour is identical (control re-solve: MS-1, 289 iters, obj −185.4461) but the criterion says *perturbed*, not *broken*.
2. **"if it requires per-model enumeration, bank it — a label-enumerated guard is not a general fix"** — the exclusion emits literal labels (`sameas(c,'y2') and sameas(h,'h50')`). **It is exactly that.**

`otpop`, the named negative control, did **not** drift — the only criterion that came back clean.

### ⚠ I FIRST REPORTED THIS AS A SUCCESS. THAT WAS WRONG.

PR #1732 initially described it as *"the same defect corrected in three models, not a leak"* and **corpus-safe**. That came from testing whether `springchain` still **behaves** identically — a weaker test than the pre-registered one, which forbids **perturbing** it at all. **Substituting a weaker criterion that happens to let the work land is exactly what an advance-fixed signal exists to prevent.** It survived until the **CI Phase-0 gate** failed the PR (emit change with no Phase-0 reference) and forced a re-read of `ISSUE_1694`. The gate caught a process miss and, through it, a reporting error.

### What is established and banked

- the collision is **real and runtime-confirmed** (Day 4);
- the layer is **`emit_gams.py` section 1b**, traced;
- root cause: **two different conditions** — suppression tests `kkt.stationarity_conditions`, the blanket fires on `infer_lead_lag_condition`;
- removing the contradiction is **not sufficient** — lnts then fails on its own **dynamics** (364 `INFES` rows: `velo1_eqn`, `tf_eqn`, `stat_step`; `tf - 50*step =E= 0` at LHS −1), a second defect the collision was masking.

**Open problem for a landable fix:** express "the pruning guard actually covers the fixed tuple" **symbolically** — a runtime `ord`/`card` property — so no model's labels appear in the emit.

### ✅ Checkpoint 1 — GO (run against the CANDIDATE emit, before the revert)

```
[resolve-changed] re-solving 4 changed-golden model(s) since 9ab2c0c3:
                  dyncge, lnts, robot, springchain
  all 4 -> same bucket;  GO
```

No `backward`, no `missing`. ⚠ Discovery was **4**, not the 3 asserted via `--min-scope` — the flag was a valid *lower bound*, but the figure to quote is 4. ⚠ This checkpoint exercised the **candidate** emit; with `src/` reverted the corpus is back to its `c1ad2bfd` state, which the checkpoint's own "same bucket" result confirms was never disturbed.

### KPIs

**Nothing moves, and nothing lands.** lnts stays `model_infeasible`.

### Gate

typecheck / format / lint clean · `make test` **5310 passed** / 10 skipped / 1 xfailed *(run against the candidate)* · `src/` and goldens **reverted to `main`**

---


## Day 6 — 2026-09-09 · P6: the date gate · 6 h · + P8 8c/8d · 4 h

**Branch:** `planning/sprint39-day6-consultation` · **Measured at:** `e662c2f6` · **Docs only — no `src/`, `tests/` or `data/` change; no `*.py` in the PR**

### ✅ P6 — the follow-up is POSTED. The five-sprint slip is broken.

**The date gate was met, not anticipated.** Executed on **2026-09-09**, the gate date itself — Days 1–5 ran up to a day early, and this was the one day that could not be pulled forward.

**Preconditions re-verified at the gate date, not carried from the package's 2026-09-01 check:**

| check | result |
|---|---|
| #1462 rocket | **OPEN**, last comment 2026-08-26 — my own send record |
| #1443 mine / LP-degeneracy | **OPEN**, last comment 2026-08-26 — my own send record |
| elapsed | **14 days** since the send |
| ⇒ branch taken | **no reply → post the pre-written follow-up (§3)** |

Posted **verbatim** from §3 — full comment on **#1462**, one-line cross-reference on **#1443**. Checked against the three banned additions (no restatement of the question, no "why it matters", no recipient-list change) and against the failure mode: the draft states the send as a completed fact, offers **re-routing rather than reconsideration**, carries no deadline, and ends by relieving the recipient of obligation. **Nothing re-opened the send decision** — the mechanism behind all five prior slips.

### ⚠ 8d was applied to this package before posting, and it mattered

The follow-up cites figures measured at **`84656666`**, and `src/` has changed since — a Pattern-C member landed on Day 2. The check was **not** "do the figures still read the same?" but "**do they still describe the same artifacts?**":

```
UNCHANGED  rocket_mcp.gms          UNCHANGED  rocket_mcp_presolve.gms
UNCHANGED  agreste_mcp.gms         UNCHANGED  agreste_mcp_presolve.gms
UNCHANGED  mine_mcp.gms
```

All five emits **byte-unchanged since the measurement commit**, so the figures still hold. Had any drifted, they would have been stale regardless of how plausible they looked — the Sprint-38 rocket lesson, where the *conclusion* survived five carries and the *failure description* did not.

### ✅ The email is SENT — P6 is fully discharged

§3 also requires the email. **This session has no email capability**, which the Sprint-38 decision brief anticipated (*"the send itself is a human action"*). **The owner sent it on 2026-09-09**, to the three addresses that brief settled on 2026-08-18:

| recipient | address |
|---|---|
| Michael Ferris | `ferris@cs.wisc.edu` |
| Steven Dirkse | `steve@gams.com` **and** `sdirkse@gams.com` |

Both of Dirkse's addresses were supplied without a preference and the brief recommends addressing both — *"a bounce on one is silent"*.

**Both channels are now complete: the GitHub comments and the email.** P6 has no outstanding action, and the consultation that slipped five sprints is fully followed up.

### P8 8c/8d — landed as CONTRIBUTING rules

New section: **Close-Rule Preconditions and Carried-Package Evidence**.

- **8c — a close rule's precondition is a START STATE, never an outcome.** Evidence from this sprint: **C6** carried the precondition *"P4 branch A **or B** started"*, but branch B is the **re-scope** branch and never implements, so it could never produce a golden. The precondition was **unsatisfiable under half the branches it named**, and read like a start state while depending on an outcome. Caught Day 0 only because choosing the branch forced a re-read. Rule also fixes the reporting: **VOID ≠ unmet**.
- **8d — re-derive a carried package's EVIDENCE, not only its conclusion.** Evidence: Sprint 38's rocket (conclusion survived five carries, failure description did not) and today's P6 application above. Prefer a **cheap invariant** — "the emit is byte-identical to the measurement commit" — over a full re-measure, and **record the measurement commit** with every carried figure, since a figure with no provenance can only be re-trusted, not re-derived.

⚠ **Both are review rules, stated as NOT automated, and the doc says so.** 8a/8b are mechanically enforced by `check_phase0_doc.py`; 8c and 8d are semantic judgements — whether a condition is a start state, whether an artifact still matches its measurement — and a cue-matching check would be gameable without being reliable. Claiming enforcement that does not exist would be the same defect these rules exist to prevent.

### Gate

`check-doc-figures` clean · `validate_plan.py` **PLAN VALIDATES** · no `*.py` in the PR

---

## Day 7 — planned 2026-09-10, **executed 2026-09-09** · P4: sarf — diagnose · 6 h

**Branch:** `planning/sprint39-day7-sarf` · **Measured at:** `9efbb723` · **Branch B — diagnosis only, no `src/` change**

### ⚠ THREE DISTINCT RUNS ARE CITED BELOW — provenance, so no figure is misattributed

| # | run | cap | outcome | what it produced |
|---|---|---|---|---|
| 1 | **pipeline translate** (`run_full_test`) | 600 s | `failure` @ **600.08 s**, no golden | the fact that **sarf never completes a translate** |
| 2 | **prep §2 profile** (`cProfile`) | **900 s** | did **not** finish | the **70.9 % cumulative** figure |
| 3 | **Day-7 profile** (`cProfile`, this section) | **600 s** | did **not** finish — wall **600.3 s**, **573.2 s** profiled | the **self-time table** below |

They are three separate executions, not one measurement described three ways. Run 1 is the whole translate under the pipeline's own timeout; runs 2 and 3 profile `compute_constraint_jacobian` alone, at different caps. *(Run 3's 573.2 s is `cProfile`'s accounted function time, which is less than the 600.3 s wall clock.)*

### ⚠ "Run the profile to completion" is impossible for sarf, and that is a fact about the model

`sarf` has **never completed a translate** — DB: `nlp2mcp_translate.status = failure` at **600.08 s**, **no golden**. The prompt's alternative applies: *say so explicitly*.

**It also means §2's own 70.9 % is a lower bound over a capped run**, not a completed attribution — `compute_constraint_jacobian` shows `ncalls = 1`, still on the stack at **run 2**'s 900 s cap. Enough to establish §2's real claim (*the cost is differentiation, not enumeration* — `enumerate_variable_instances` genuinely completed), but not readable as "70.9 % of the translate".

**Method: SELF time (`tottime`) + call counts, valid regardless of completion.** Cumulative treated as a lower bound.

### The attribution — run 3 (cap 600 s; 573.2 s profiled)

| frame | self | % | ncalls |
|---|---|---|---|
| `simplify` | **109.9 s** | **19.2 %** | 26.9 M |
| `CaseInsensitiveDict.__contains__` | **68.1 s** | **11.9 %** | 55.8 M |
| `_is_concrete_instance_of` | 55.0 s | 9.6 % | 18.6 M |
| `isinstance` | 48.1 s | 8.4 % | 213.8 M |
| `_partial_index_match` | 34.3 s | 6.0 % | 1.9 M |
| `resolve_set_members` | 30.0 s | 5.2 % | 18.6 M |
| **`<frozen importlib._bootstrap>:645(parent)`** | **25.4 s** | **4.4 %** | **45.5 M** |
| `str.lower` | 21.6 s | 3.8 % | 77.6 M |
| `CaseInsensitiveDict.__getitem__` | 18.6 s | 3.2 % | 18.6 M |
| **`str.rpartition`** | **17.7 s** | **3.1 %** | **45.5 M** |
| **`_diff_sum`** | **16.5 s** | **2.9 %** | 1.9 M |

### ⚠ `_diff_sum` is 2.9 % of self time, not 57 %

§2 named it at **57.1 % cumulative** and the prompt directed attribution at it. **Its own work is 2.9 %** — it is a dispatcher. Same distinction that forced §2's correction of Task 2, applied one level deeper: **cumulative says what a frame is waiting on; self time says what does the work.**

### ⚠ 7.5 % is PURE IMPORT OVERHEAD — not differentiation

`<frozen importlib._bootstrap>:645(parent)` (25.4 s) + `str.rpartition` (17.7 s) = **43.1 s / 573 s**, from **45.5 M import re-resolutions**, attributed exactly to two function-local imports:

| function | calls |
|---|---|
| `ad_core.simplify` `:127` | 26,908,871 |
| `_is_concrete_instance_of` `:3087` | 18,582,862 |
| **sum** | **45,491,733** vs measured **45,513,129** — 0.05 % apart |

**Both hoistable — verified, not assumed:** neither `src/ir/ast.py` nor `src/ad/index_mapping.py` imports `src/ad/ad_core.py` / `src/ad/derivative_rules.py` at module level (**no cycle**), and `src/ad/derivative_rules.py` already imports `..ir.ast` at module scope.

⚠ My first cycle check was invalid — `grep … | head || echo` reports **head's** exit status, so the fallback never fired and empty output proved nothing. Re-done with an AST parse. **The pipe-exit-status trap, from my own notes, hit again.**

### What this means for P4

**The cheapest lever is not algorithmic** — ~7.5 % from moving two `import` statements to module scope. The genuine algorithmic cost is `simplify` (19.2 %) + case-insensitive lookup (~18.9 %) ≈ **38 %**, neither addressed by anything P4 was originally scoped to do; the four original sites remain **0.5 %**.

**Nothing implemented.** Day 8 authors the Phase-0 gate. **C6 VOID; Translate reports 135 flat.**

---

## Day 8 — planned 2026-09-11, **executed 2026-09-09/10** · P4: the Phase-0 gate · 5 h · + P5 · 5 h

**Branch:** `planning/sprint39-day8-sarf` · **Measured at:** `7d8aaee6`

### P4 — the differentiation-path Phase-0 gate is authored (branch B: no implementation)

Added to **`ISSUE_1385`** as a **second, independent gate**, for the **per-column cost** lever. The gate already there narrows **how many columns** are differentiated (436,555,392 → 259,728); this one reduces **what each column costs**. Total work is the **product**, so neither subsumes the other and either can land alone.

⚠ **The fail-before is explicitly NOT anchored on `_diff_sum`.** Prep's §2 named it at **57.1 % cumulative** and Day 7's own prompt directed attribution at it — but its **self time is 2.9 %**. A gate anchored there would pass against a change that does nothing, which is precisely the failure Day 1 caught for dyncge.

Anchors instead on Day 7's attribution: a **call-count** assertion for the import lever (`<frozen importlib._bootstrap>:645(parent)` **45,513,129 → ~0**, machine-independent), and per-frame self-time/call-count targets for `simplify` (19.2 %) and case-insensitive lookup (~18.9 %). Emit invariance is the whole of the expected pattern: **byte-identical corpus-wide, any drift is a failed gate.**

### ⚠ Being the first customer of my own Day-3 rules found a bug in them

`ISSUE_1385` now carries **two** `## Phase 0: Acceptance Gate` sections. Both `phase0_subsections` and `subsection_body` used `PHASE0_HEADING.search`, which stops at the **first** — so the new gate was invisible, and the checker reported *"Nearest Existing Mechanism missing"*, then *"present, but records no reason"*, **for a section it had never read**. That is worse than not checking: a specific, wrong reason.

Both functions now scan **every** Phase-0 section. ⚠ Fixing `phase0_subsections` alone was not enough — the identical bug lived in `subsection_body`, and the first fix looked like it worked because the failure message merely changed. Regression test added; **both mutants killed**.

### P5 — all four `NEEDS A GUARD` sites TRACED; none is a confirmed defect

| site | keyed on | corpus repeats | dedupe covers? | verdict |
|---|---|---|---|---|
| `empty_equation_detector.py:127` | **equation** | **0** | ✗ | **LATENT** — unguarded, unreachable |
| `condition_eval.py:117` | **equation** | **0** | ✗ | **LATENT** — same |
| `stationarity.py:1384` *(was `:1091`)* | **variable** | 5 | ✓ | **PROTECTED UPSTREAM** |
| `stationarity.py:1398` *(was `:1104`)* | **variable** | 5 | ✓ | **PROTECTED UPSTREAM** |

⚠ **Two of the four line references were already stale — by this sprint's own Day-2 landing.** B-4 (PR #1728) inserted ~256 lines at ~1004, so `stationarity.py:1091` now lands inside `_find_full_collapse_sum`. **+293 line drift**; relocated by content.

⚠ **"Reach 10/15" is not "triggered 10/15".** Reach counts models that execute the line, not models that pass it a repeated domain. A 220-model scan finds only **five** models with the shape, **all variable domains, zero equation domains**.

**Recommendation:** guard the two **equation-keyed** sites — genuinely unprotected, unreachable only by corpus accident. **Do not** guard the variable-keyed pair: `dedupe_repeated_variable_domains` rewrites every repeated variable domain before the AD layer (measured: tricp, lop, ferts all rewritten, **zero repeats remaining**), so a local guard would be **dead code whose fail-before has nothing to fail on**.

### ⚠ Method note — a 29-minute probe answered nothing

The first P5 attempt profiled full emits of the five triggering models with **dedupe bypassed** (it called parse → normalize → jacobian → emit directly; `dedupe` is invoked only from `src/cli.py:476`). It ran **29 minutes without emitting one model** and was killed: un-deduped, `lop`'s `dtr(s,s,s,s)` is |s|⁴ columns. **The probe removed the protection that makes those models tractable.** A bounded test of the transformation itself answered the question in seconds.

### Gate

typecheck / format / lint clean · `make test` **5311 passed** / 10 skipped / 1 xfailed (+1) · `check-doc-figures` clean · Phase-0 checker verified end-to-end on `ISSUE_1385` as an *added* doc (exit 0)

---

## Day 10 (plan 2026-09-13; executed 2026-09-11) — Checkpoint 2 GO · P7 lands A **and** B

### Checkpoint 2 — GO (run FIRST, before P7 changed the recording path)

`--resolve-changed --since-commit 9ab2c0c3 --min-scope 1`. Scope **discovered** then asserted: exactly one golden changed since the S38 close — `dyncge` (Day 2's B-4). Bucket held: `model_optimal`/`mismatch` → `model_optimal`/`mismatch`, **same**. No `backward`, no `missing`.

### The KPI correction, reported with its reason

> **Match 96 → 95 is a CORRECTION, not a regression.** `weapons` was recorded as a **presolve** match, but the presolve retry's MCP produced no `MODEL STATUS` of its own. A `--nlp-presolve` emit warm-starts by solving the original model inside the generated file, so when that MCP solve aborted, `nlp2mcp_obj_val = tetd.l` still held the embedded NLP's own answer (1735.5696) and the comparison matched itself. **This is not "weapons cannot be solved as an MCP"** — its **cold** emit solves, to `model_optimal` @ **1700.397**, which is a **2.03 %** divergence from the NLP and therefore a **mismatch**. That cold result is the true record. The overstatement dates from Sprint 38 Day 9, was reported at the time, and is corrected here. **Match 95 is the first figure in this series that is true.** Solve (111), cold-optimal (65) and the genuine floor (75) are unaffected; presolve-match moves 31 → 30 and all-219 Match 99 → 98 for the same single reason.

*(The floor reads **75**, not the 73 this wording was drafted against at prep — re-baselined on Day 0. Derived from `floor_tracker.py`, unchanged by P7.)*

### Remedy A — the gate is on the BRANCH, not on one write

⚠ **The plan's correction was right and the merged §9 obligation 5 was half of a truth.** The `mcp_file_generated` assignment is the sole writer *of the key*, but the branch it sits in — `if retry_result["status"] == "success" and retry_mcp_solved:` — makes **three** writes: `presolve_required`, the file path, `outcome_category`. Gating the path write alone would have left the other two asserting a presolve success.

⚠ *The predicate is `retry_mcp_solved`, renamed from `retry_attributed` in review — `MCP-FAILED` **is** attributed and is deliberately rejected, so the old name asserted the weaker property while the branch enforced the stronger one. ⚠⚠ **Switching to symbol references did not make this citation stable**: the rename broke it two rounds later (PR #1740 review). A symbol is more durable than a line number and still not durable — **any doc that names code is a claim that ages out, and a rename is exactly the edit that ages it.*** ⚠ *Referenced by symbol, not line number.* The plan cited `:936`/`:954` and this log repeated them; both were stale within the same PR, because the review rounds that hardened the gate inserted ~30 lines of comment above them (PR #1740 review). **A line number in a doc is a figure that ages out faster than any other** — it can be invalidated by an edit that changes no behaviour at all.

**The defect, stated mechanically:** `parse_gams_listing` takes the **last** match of each pattern across the **whole** listing (`finditer(...)[-1]`), with no notion of which model produced it. A `--nlp-presolve` listing holds the embedded source solve *and* ours, so when our MCP aborts before reporting, the source's status is the last one present and is read back as ours.

`solve_mcp` now computes `mcp_produced_own_status` **while `lst_content` is still in hand** — it is read inside a `TemporaryDirectory` and discarded, so the attribution cannot be recovered later. It reuses `parse_solve_summaries` rather than adding a second regex: attribution is **positional**, and a listing-wide search cannot answer the question.

⚠ **The arrivals at the restore branch need different bookkeeping, and WHICH arrival is which changed during the sprint.** `run_solve_stage` counts a retry by its own status, so the rollback must undo whatever *that* retry produced — never assume. As shipped:

| retry verdict | arrives as | rollback |
|---|---|---|
| **`EMBEDDED-ONLY`** (the live `weapons` case) · **`MCP-FAILED`** | **failure** — `solve_mcp` refuses to claim success for a contradicted status | undo `solve_failure`, pop the retry's error |
| **`MCP-NO-STATUS`** / **`NO-SOLVE`** (indeterminate) | **success** — nothing contradicts the scalars | undo `solve_success`, pop nothing |
| a genuine solver failure | failure | undo `solve_failure`, pop the retry's error |

⚠ *An earlier revision of this line said an "unattributed retry reported success" — true before `solve_mcp` began downgrading contradicted statuses, and false for the one verdict the sprint actually exercises (PR #1740 review).* **Popping `solve_errors` when this retry pushed none discards the COLD error.** Pinned by a test, which itself had to move to an indeterminate fixture once `EMBEDDED-ONLY` stopped reaching the success arm.

**It fired live**, re-captured from the shipped code rather than quoted from the first run:

```
[SOLVE]  SUCCESS: objective=1700.4
[RETRY]  spurious-KKT mismatch — retrying with --nlp-presolve...
[SOLVE]  FAILURE: path_solve_terminated
[RETRY]  REJECTED (EMBEDDED-ONLY): the status belongs to the embedded source solve — keeping the cold record
[COMPARE] MISMATCH: diff=3.52e+01 > tolerance=3.47e+00

  Pre-solve retry: 0/1 recovered, 1 REJECTED (no usable answer from our MCP)
```

⚠ **THIS BLOCK HAS NOW GONE STALE THREE TIMES, EACH FOR A DIFFERENT REASON** — `[RETRY] UNATTRIBUTED` before the message became verdict-keyed; then `[SOLVE] SUCCESS: objective=1735.57` before `solve_mcp` began refusing to claim success for a borrowed status; and the summary line was missing before the formatter reported rejections at all. **A transcript is the most perishable evidence in a PR**: it captures one moment of one build, and *every* behavioural fix invalidates it. The rule that follows — re-capture, never re-word, and re-capture LAST, after the final behavioural change. ⚠ *The first revision of this entry recorded `[RETRY] UNATTRIBUTED`, which was the message at the time and is not what the shipped code prints* — the label became verdict-keyed when review showed "unattributed" was false for an aborted own-MCP (PR #1740 review). **A pasted log is evidence only while the code that produced it is the code being shipped**, so this was re-run rather than re-worded.

### Remedy B — the rename, and the obligations that were not optional

`2.2.1 → 3.0.0`, **48 rows**, `migrate_schema_v3.0.0.py`. Major per the schema's own declared rule; the first breaking bump in this file's history.

⚠ **The migration's own `--validate` caught a real defect before writing**: the root is *also* `additionalProperties: false`, so its `_migration_summary_v3_0_0` bookkeeping key was rejected. It refused to write — the fail-closed behaviour restored deliberately after v2.2.0/v2.2.1 dropped the flag v2.1.0 had.

**Obligation 2's control holds, both rows:** the fact derives **14** after the rename alone (*not* 0 — 0 would mean the checker is reading a key that no longer exists) and **13** after Remedy A reverts `weapons` to its cold golden.

⚠ **`weapons_mcp_presolve.gms` was generated by the re-solve and deliberately NOT committed.** It fails §6's adoption rule item 1 — its MCP does not solve — which is the entire finding.

### A consequence nothing predicted

`make typecheck` broke, and not on anything I edited. `mypy src/` follows `src/diagnostics/convexity_numerical.py:67` into `scripts/gamslib/test_solve.py`; Remedy A's import extended that chain to the attribution module, which reaches an optional `jsonschema` import with no stubs. **The dependency was always optional — the import graph is what changed.** Resolved with a `[[tool.mypy.overrides]]` entry beside the existing `lark`/`numpy` ones, rather than declaring stubs for a package the project deliberately does not depend on.

### Verification

`typecheck` · `format` · `lint` clean. Mutation-killed twice: reverting Remedy A's condition fails the record-path assertion; reverting pattern 2's renamed token fails the new positive reverse-form test.

⚠ **The scope claim needed correcting mid-review.** This day was originally recorded as *"`src/` untouched"*; that was true at the first commit and false after the review round that gated `src/diagnostics/convexity_numerical.py` on the attribution verdict. The accurate statement is narrower and is what actually carries the argument: **the EMIT implementation — `src/{ad,kkt,emit}` — is untouched**, so emit is byte-identical by construction, Phase-0 does not arm (it keys on exactly those three trees), and the `weapons` cold golden re-translated byte-identical, confirming it. `src/diagnostics/` is a consumer of solve results, not an emit path.


## Day 9 — planned 2026-09-12, **executed 2026-09-10** · P9 · 2 h · + P10 · 5 h · + P5 · 3 h

**Branch:** `planning/sprint39-day9-epic5` · **Measured at:** `a933eca9`

### P9 — the Epic-5 design is RECORDED (recording, not designing)

Both remaining questions move from *open* to **PROPOSED**, pointing at `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md`: **9.1** numéraire-selection rule (§6), **9.2** degeneracy detection (§7). Recorded in `docs/planning/EPIC_4/SPRINT_38/CAMCGE_EPIC5_HANDOFF.md`.

⚠ **Flagged for whoever implements §7:** its detectors have **exactly one expected true positive (camcge)**. On that evidence a detector *tuned* to camcge is indistinguishable from one that generalises. §7 states the count; it does not demonstrate generality.

### ⚠ A stale figure corrected — the license cohort is 11, not 10

The handoff recorded **10 models / ceiling +10 Solve**. **Derived from the DB**, `path_solve_license` is **11**: egypt · ferts · glider · robot · shale · sroute · srpchase · tabora · tfordy · **tricp** · turkey. `tricp` joined after that document was written. **Ceiling is +11.**

### P10 — the P1/P2 gate is LANDED (`make check-index-repeats`)

| property | design | today |
|---|---|---|
| **P1** — no emitted head repeats a controlling index | **HARD gate** | **0** violations / 3,109 heads |
| **P2** — no `$(...)` guard references a repeated index | **RATCHET** vs baseline | **9** across 6 models, baselined |

P2 is a ratchet because **9 real violations sit in committed goldens now**; a gate that goes red on untouched history gets switched off — the same reasoning that made 8a/8b added-only. Fixing one requires shrinking the baseline (`--update-baseline`), and the gate reports entries that have disappeared.

**All four exit paths verified end-to-end**, not just the happy one: clean → 0 · new P2 violation → **1** · P1 violation → **1** · stale baseline entry → 0 **plus a ratchet notice**.

### ⚠ P10 did NOT follow the survey's recommendation — measured first, it was 8/8 false positives

The survey ranks *"close P2's known LHS gap — a one-line extension"* as part of graduation. **Measured before implementing:** extending P2 to assignment left-hand sides adds **8 violations across 7 more models**, and **every one is source-faithful**:

```
china    crec(cf,cf)$(not sum(ca, crec(ca,cf))) = 1;   verbatim in source :305
prolog   eta(g,g,h) = ...                              verbatim in source :88
markov   pi(s,i,sp,j,sp) = pr(i,j);                    verbatim in source :56
orani    ce(c,c) = 1;  ·  etabar(c,s,c,s)              verbatim in source :30/:86
dinam    a(id,id,te)                                   verbatim in source :271
egypt    yld(c,c,r) = yield(c,r);                      verbatim in source :707
danwolfe e(i,i) = 0;                                   deliberate diagonal
```

**8 false positives against 9 true findings — roughly 1:1.** A check at that rate gets deleted, which is exactly what the survey itself predicts for the `Set ut(i,i)` declaration class. **The guard-content scoping is load-bearing, not a limitation.** Two tests pin the decision so it is not "fixed" later.

### P5 — the two EQUATION-keyed sites guarded; the variable-keyed pair deliberately not

New shared module `src/ir/index_map.py`, used by **both** call sites rather than duplicated (the S38-D12 rule, and the PR #1734 lesson about copying a predicate). It **raises** instead of silently collapsing.

⚠ **The two sites call DIFFERENT entry points, and that is the design** (PR #1736 review — an earlier revision of this line said both call `build_index_map`, which aged out when the hoist landed in `c428836a`):

| site | binds | calls |
|---|---|---|
| `src/ir/condition_eval.py` | one instance per call | **`build_index_map`** — validate + build |
| `src/kkt/empty_equation_detector.py` | many instances of ONE domain | **`assert_no_repeated_symbol`** once *outside* the loop, then `dict(zip(..., strict=True))` per instance |

The domain is constant across the instance loop, so re-checking it per instance adds cost without adding safety after the first iteration. **Do not "fix" `empty_equation_detector` back to `build_index_map`** — that silently reinstates the per-instance re-check the hoist removed. `assert_no_repeated_symbol` exists precisely so the validate step can be hoisted; `build_index_map` delegates to it, so neither site can drift from the other's notion of "repeated".

⚠ **`strict=True` does not catch this.** It compares *lengths*, which agree; the collapse happens in the `dict` construction afterwards — `dict(zip(("i","i"),("i1","i2")))` is `{"i": "i2"}`, first position silently discarded. The test asserts that defect explicitly before asserting the guard.

**Raising is safe, measured:** no corpus model declares a repeated **equation** domain (220-model scan), and these sites are equation-keyed. **The variable-keyed pair is left alone** — `dedupe_repeated_variable_domains` rewrites every repeated variable domain upstream, so a guard there would be dead code whose fail-before has nothing to fail on.

### ⚠ I repeated Day 5's contention mistake

The first leak-gate run reported *"All in-scope goldens clean"* **with 2 unverified timeouts** (ganges, gangesx) — because I started it in the same command as `make test`. That is a claim over **184 of 186**, not full scope. Re-run uncontended: **186 checked, all clean, no timeouts.** Second occurrence of this exact error; the rule is simply that the leak gate runs alone.

### Gate

typecheck / format / lint clean · `make test` **5325 passed** / 10 skipped / 1 xfailed (**+14**) · leak gate **186 clean, uncontended** · `make check-index-repeats` PASS · `check-doc-figures` clean · dyncge/elec/springchain emits byte-identical

---

## Day 11 — planned 2026-09-14, **executed 2026-09-15** · P7 finish · 4 h · + P5 · 5 h

### The fall was already reported on Day 10 — this day VERIFIED it rather than repeating it

Close rule **C2** requires the Match fall to carry its reason in the same
sentence. Day 10 discharged that in both live docs, so the Day-11 obligation is
confirmation, not re-publication:

| site | carries the C2 wording |
|---|---|
| `CHANGELOG.md` :13 | ✅ with **floor 75** |
| `SPRINT_LOG.md` §7 (Day 10) :504 | ✅ with **floor 75** |

**All figures re-derived at `90b43e1e` with `kpi_block.py` and `floor_tracker.py`,
not recalled:** Solve **111** · Match **95** · cold-optimal **65** · presolve
**30** · all-219 Match **98** · `path_solve_terminated` **0** · genuine floor
**75**. Every one matches what Day 10 reported.

### ⚠ The template that C2 says to quote VERBATIM was stale

`PRESOLVE_RECORD_REMEDY.md` §5 read *"the genuine floor (73)"*. That was written
at prep, when 73 was believed; the **Day-0 owner decision re-baselined it to
75**, and `floor_tracker.py` derives 75 today.

The number was wrong in the one place it could do the most damage. C2 says to
use that block **verbatim**, so a Day-13 closeout quoting it unchanged would
have reported a floor contradicting its own tool — **inside a sentence whose
entire purpose is to correct a figure**. Day 10's two uses had silently fixed it
in passing; only the source lagged, so nothing flagged it.

Corrected to 75, with the reason recorded in the document rather than as a
silent edit.

**Banked staleness, third instance this sprint** (after the Day-8 prompt sweep
and the Day-9 re-baseline): a figure written at prep and quoted at close
describes a sprint that no longer exists. `check-doc-figures` does not cover it
— the remedy doc is not a live doc, and the stale figure sat in a *template*
rather than in a claim.

### P7's seven obligations — verified discharged, not assumed

Re-derived against merged `main`, each by running the thing rather than reading it:

| # | obligation | evidence |
|---|---|---|
| 1 | checker updated in the **same commit** as the DB migration | `check_doc_figures.py` reads `mcp_file_generated`; no occurrence of the old key remains |
| 2 | the fact derives **13** (rename **+** Remedy A), and **0 is the FAILURE signal** | derived **13** ✅ |
| 3 | fact name, `source` string and fixture renamed; **pattern 3 untouched** | name = *"presolve rows whose generated file is absent"*; 3 patterns intact, pattern 3 still `all\s+N\s+(?:presolve-record\s+)?rows` |
| 4 | a test that the **writer** emits the new key, repo-relative | `tests/gamslib/test_run_full_test_path_relative.py` |
| 5 | `run_full_test.py` is the **sole writer** | the only remaining `mcp_file_used` occurrences are a historical **comment** and the migration's required `OLD_KEY` constant |
| 6 | `schema.json` property renamed **and** its description corrected | `additionalProperties: false` retained; description now says *generated*, justified by the field's lifecycle |
| 7 | `schema_version` bumped + migration script, **all three sites** | DB **3.0.0**, schema root description **3.0.0**, `migrate_schema_v3.0.0.py` present; 0 rows carry the old key |

⚠ **My first obligation-5 probe FAILED, and the probe was wrong, not the code.**
A bare substring search for `mcp_file_used` in `run_full_test.py` hit a comment
explaining the rename. **A substring probe reports the absence of a string, not
the absence of a meaning** — the same finding this sprint already recorded when
a diff probe matched on capitalisation and tense. Verified by reading the two
hits rather than by trusting the count.

### P5 — the last two `NEEDS A GUARD` sites closed (#1741)

Both remaining sites (`stationarity.py` survey rows `:1091` and `:1104`) are
**one function**, `_build_pattern_c_dim_mismatch_term`, so **one guard closes
both ends**. All four `NEEDS A GUARD` sites are now closed: D9 took the two
index-map sites (#1737), D11 takes this pair.

**The defect.** `_pos` returns the FIRST position whose symbol matches, so a
diagonal reference like `X(i,i)` collapses `sum_position` and `bindings[eqi]`
onto position 0 and B-3 consolidates against a coordinate the source never
expressed.

**⚠ Neither existing guard catches it, which is the reason a new one was needed.**
`len(bindings) != 1` rejects MULTIPLE eq-domain indices — here `len(bindings)`
is exactly 1. The canonical-set fallback declines when the sum and binding
coordinates resolve to DISTINCT sets — but a collapse makes them the SAME
position, so it compares a symbol with itself, finds them equal, and proceeds.

**⚠ THE REMEDY DIFFERS FROM D9's ON PURPOSE — `return None`, not `raise`.**
`index_map` raises because a collapsed map has no honest value to return. This
builder's contract is *"return `None` and the caller takes the standard path"*,
and that path handles the general case correctly. **Declining a special case is
always safe; refusing to emit is not** — raising here would break models that
translate correctly today. Recorded in the survey so a later reader does not
"harmonise" the two and silently undo it.

**⚠ The survey's line citations had aged out — AND DAY 8 ALREADY SAID SO**
(PR #1742 review). `:1091` now lands inside `_find_full_collapse_sum`. Day 8
measured the drift exactly (**+293 lines**, from PR #1728) and wrote *"relocated
by content, not by offset"*; Day 11 hit the same wall while locating the same
site and recorded it as if new. **The finding was not the problem — the ADDRESS
FORMAT was**, and re-recording a drift is not a fix for it. The survey now says
to cite these sites by SYMBOL, which is the thing that actually stops the third
recurrence. Same root as the P7 obligation-5 probe on the same day: an address
written at survey time does not survive the file changing.

**Verification.** Fail-before asserted on `_pos`'s own arithmetic (so the guard
cannot later read as redundant); both repeat shapes declined, including the
case-only `('i','I')` — GAMS identifiers are case-insensitive; **and a positive
control that a distinct `('i','j')` reference gets PAST the guard**, asserted by
spying on the next call, because every other assertion is `is None` and would
pass vacuously against a guard that declined everything. Mutation-killed.

**Emit invariance: `make check-goldens` 186 in-scope, all clean, 0 drift,
UNCONTENDED** — run alone, per the rule this sprint has now broken twice. The
guard is therefore latent: **0 corpus models reach it**, stated alongside the
pass so a future reader can tell a real pass from an unexercised one.

Phase-0: `docs/issues/ISSUE_1741_pattern-c-b3-repeated-index-collapse.md`
(gate verified locally: PASS, 1 emit file changed).


## Day 12 — planned 2026-09-15, **executed 2026-09-16** · P5 finish · 3 h · + P10 · 6 h

### P5 — the remaining 16 sites pinned, and the address rot ended structurally

New `tests/unit/kkt/test_positional_domain_sites.py`. **No new guards** — the
nine `ALREADY GUARDED` sites keep their existing remedies — **three shared
mechanisms** (consume-once slot claiming, the `seen_sym` duplicate bail-out,
parser alias substitution) **plus `_sigma_sp_domain_collision`'s own
purpose-built detector**, which is a fourth and is not one of the three
(PR #1743 review).

⚠ **BUT THIS MODULE DOES NOT ASSERT MOST OF THEM FIRING, and an earlier revision
of this entry said it did** (PR #1743 review). The honest split:

| strength | count | sites |
|---|---|---|
| **BEHAVIOURAL** — executed, result asserted | **5** | the four `_substitute_indices` shapes; `_sigma_sp_domain_collision`'s ordering conjunct |
| **STRUCTURAL ONLY** — anchor text asserted to exist, nothing executed | **11** | `_handle_aggregation`'s `expanded_indices.index(...)`, `_try_dotted_key_lookup`, `_apply_alias_offset_to_deriv`, `_match_subset_domain`, both `_compute_index_offset_key` passes, `_remap_condition_to_domain`, `_diff_sum`'s two sites, `_handle_assign`, `_handle_aggregation`'s `seen_domain` path |

⚠ **This table was wrong twice.** An earlier revision listed **7** structural
sites and omitted **four** — `_remap_condition_to_domain`, the `NEEDS A TEST`
`_handle_aggregation` row, `_try_dotted_key_lookup` and
`_apply_alias_offset_to_deriv` — leaving **four** catalogued sites outside
**both** categories (⚠ an earlier revision said *two* while listing four; none
of the four is behavioural, so all four were unclassified — PR #1743 review).
The review named two of the four; the others surfaced only by
computing the complement. The module now derives the split from
`CATALOGUED_SITES` and `test_every_site_has_exactly_one_strength_class` asserts
it is **exhaustive and disjoint at 5 / 11**, so a hand-written table can no
longer drift from the catalog.

⚠ **Note the classification cuts ACROSS the verdicts:** three `NEEDS A TEST`
sites are structural-only, and one `ALREADY GUARDED` site
(`_sigma_sp_domain_collision`) is behavioural. Verdict and pin-strength are
independent axes.

**A guard at a structural-only site could keep its anchor text while its state
update or early return is broken, and this module would not notice.** That gap
is deliberate and measured: a probe of **nine** input shapes against
`_match_subset_domain` and `_compute_index_offset_key`, with the consume-once
guards DISABLED, produced **byte-identical results in every case** — so a
behavioural pin built on any of them would have asserted nothing while looking
rigorous, the same failure this sprint hit three times. Finding a discriminating
input for those two is **carried to Sprint 40**.

**⚠ THIRD MEASUREMENT OF THE SAME ROT, so the fix is structural this time.** All
six `stationarity.py` citations had drifted **+318 to +346**; `condition_eval.py`
by +1; **every other file's citations still land exactly**. Only the file this
sprint kept editing rots, which is the mechanism rather than a coincidence.
`test_every_catalogued_site_still_resolves_by_symbol_AND_snippet` pins each site's **owning
function**, which survives the edits that move lines — and fails if one is
renamed. The survey carries the full relocation table.

**⚠ THE REAL SAFETY PROPERTY OF THE FOUR `_substitute_indices` SITES, MEASURED —
and it is sharper than the survey's wording.** The survey called them *"safe only
because of a pass covering one of three sub-shapes"*. Instrumented:

* the AD layer **does** reach `_substitute_indices` with a repeated
  `symbolic_indices` — **12 calls** for a `rep(i,i)` model, carrying `('i','i')`
  against concrete tuples including `('a1','a2')`, so the collapse is **real**
  and the off-diagonal instances get a wrong Jacobian;
* **nothing wrong reaches output**, because `emit_gams_mcp` runs
  `detect_empty_equation_instances`, whose **#1737** guard refuses the repeated
  equation domain.

So **#1737 is load-bearing for the AD layer too**, not only for the two call
sites it was written against. Narrowing it would silently unprotect these four.
That is now a test, with the spy count asserted **> 0** first so the refusal is
not believed against a dead probe.

⚠ **AND PER-SHAPE, NOT AGGREGATE** (PR #1743 review). A first revision asserted
only *"some repeated call happened with distinct concrete values"* — which **one**
call satisfies while the other `.index(...)` shapes stop being exercised, no use
as the integration pin for a **four-site** claim. The model now carries a lead
(`x(i+1)`) and an inner `sum(j, …)` so **three** of the four shapes are reached
(`str`, `IndexOffset`, `Sum/Prod`) and **each is asserted individually**. The
fourth — bare `SymbolRef` — is **simply not exercised by this model**, and is
covered by a direct unit test instead, **stated rather than folded into an
aggregate count**. ⚠ An earlier revision said it was *"not reachable from a
GAMS source"* and needed an *"unresolved `Call` argument"* — **wrong**: the
parser represents an ordinary `ord(i)` as a `Call` holding a `SymbolRef`, and
`_substitute_indices` recurses into call arguments (PR #1743 review). The test
module was corrected a round earlier; this mirror was not.

⚠ **The function name alone was not a sufficient address either.**
`_handle_aggregation` owns **two** catalogued sites with **different verdicts**
(`:6086` `NEEDS A TEST`, `:6007` `ALREADY GUARDED`), so a function-name pin
cannot tell a regression in one from the other — and the first revision also
**misclassified** `_handle_assign` as `NEEDS A TEST` when the survey has it
`ALREADY GUARDED`. Each row now carries an **anchor snippet** that must appear
inside that function's own source range, plus a test pinning the verdict counts
and the shared-function case.

⚠⚠ **AND THE CATALOG WAS SHORT BY THREE SITES** (PR #1743 review). It carried
**13 rows for 16 sites**: `constraint_jacobian:1513`, `derivative_rules:2411`
and the second `stationarity:5148` each **shared an anchor with a neighbour** and
were silently collapsed into it, so a change to any of the three could not be
detected. Each now has its own row and its own distinguishing anchor.

**The count assertion was the thing that hid it:** it asserted **6/7 — the
number of rows the catalog happened to have**, which is unfalsifiable by
construction. It now asserts the survey's **7/9 (16 total)** and additionally
that every `(file, function, anchor)` triple is **unique**, so a future
collapse fails rather than passing quietly. *Asserting the count you HAVE proves
nothing; asserting the count the SOURCE says is what catches an omission.*

**⚠ TWO DEAD MUTANTS BEFORE THE `_sigma_sp_domain_collision` TEST DISCRIMINATED.**
Weakening `len(canon_hits) < 2` to `< 1` survived, and so did replacing
`any(vi < later …)` with `True`. Measuring showed why: **`< 2` is a FAST PATH,
not the guard** — with a single hit, that hit *is* `later`, so the ordering test
is already False and the function returns `None` either way. The load-bearing
condition is the **ordering** one, and it needed a case where the exact
declared-name match sits EARLIER than the canon-only hit. The `< 2` mutant still
survives, correctly, and the docstring now says so rather than claiming a guard
that is not there.

### P10 — the six P2-flagged models TRIAGED; **two classes, not one**

`docs/planning/EPIC_4/SPRINT_39/P2_VIOLATION_TRIAGE.md`. Every emitted line and
source rule read from the tree.

The survey's framing — *"manufactured unless the source declares it so"* — is
**half right**:

* **Class A, MANUFACTURED** (dinam, egypt, turkpow ×3, **nonsharp ×1**): the
  source keeps the two positions DISTINCT and emit substitutes one symbol into
  both, so **a coordinate is lost and the reference reads the wrong cell**.
  ⚠ nonsharp's `inter(col__kkt1,col__kkt1,stm)` carries a **KKT-minted alias in
  both coordinates** — the survey already records it as manufactured — so it is
  Class A even though the model's *other* reference is declaration-derived. An
  earlier revision put the whole model in Class B and hid this effect
  (PR #1743 review). Where the symbol
  is an `ord`-style relation that cell is tautological — **identically FALSE**
  (dinam: `ord(te) > ord(te)`, the term is silently dropped) or **identically
  TRUE** (turkpow: `ord(v) >= ord(v)`, the guard is inert). Where it is a data
  table it is simply the **wrong lookup** (egypt's `tranc(rp,rp)` for
  `tranc(r,rp)`). ⚠ An earlier revision of this entry gave only the tautological
  symptom, which its own egypt row contradicted (PR #1743 review).
* **Class B, DECLARATION-faithful but ASSIGNMENT-narrowing** (gussrisk,
  **nonsharp ×1** — its `inter(col,col,stm)` reference only; shale is B-origin
  with an A effect): the source **declares** the
  SYMBOL — a **set OR a parameter** — over the same set twice. ⚠ Measured, and
  not a quibble: `gussrisk`'s `covar` is declared under `Parameter` but
  `nonsharp`'s `inter` is declared under **`Set`**, so naming only parameters is
  wrong for half the class and sends a reader to the wrong declaration block
  (PR #1743 review). That is legal GAMS meaning the full product — and
  emit reuses that domain in an assignment/guard, where GAMS reads the
  **DIAGONAL**. The symbols are the source's own; the *context* is what changed.

**Class A is a downstream symptom of P5's sites**, not an independent bug list —
turkpow is the clearest case, where the KKT alias minter put `t__kkt1` into
**both** coordinates of a `vs(t,v)` reference.

**⚠ No fix lands, and the baseline stays at 9.** Each Class-A fix is a `src/kkt`
or `src/ad` emit change needing its own Phase-0 doc, golden regen and a re-solve
— and for **three** of the six the re-solve is unavailable: **egypt and shale
are license-gated**, and **nonsharp is convexity-excluded with no `mcp_solve`
record at all** (⚠ an earlier revision said *two*, written before nonsharp's
KKT-minted reference was reclassified to Class A — PR #1743 review). Landing a
partial fix would move the ratchet while being unable to demonstrate correctness
on three of the six.

**0 bucket, no KPI movement**, stated precisely because the Class-A set changed:

| model | Class-A effect | today's status | moves a figure? |
|---|---|---|---|
| dinam, turkpow | yes | `mcp_solve: failure` (`path_syntax_error`) | no |
| egypt, shale | yes (shale: B origin) | `mcp_solve: failure` (`path_solve_license`) | no |
| **nonsharp** | yes (×1 of its 2 refs) | **no `mcp_solve` record** — convexity-`excluded`, outside the 142 | no |

So **four** Class-A-effect models are `mcp_solve: failure` and a **fifth** has no
solve record; none contributes to a reported figure. ⚠ *"all four models with a
Class-A effect are `mcp_solve: failure`"* — the earlier wording — became false
the moment nonsharp gained a Class-A reference, and the gate evidence has to
name the no-solve exception rather than absorb it into "failure". Carried to
Sprint 40 as a classified work list.

### Gate

typecheck / format / lint clean · **`make test` 5444 passed**, 10 skipped,
1 xfailed (measured at `9f76f905`; the Day-13 retest re-derives this) · `make check-index-repeats` PASS (P2 **9 = baseline 9**) ·
`check-doc-figures` clean.

⚠ **The suite figure was missing from this section and stale where it did
appear** (PR #1743 review). The reconciliation, since the arithmetic does not
close against the Day-11 log at face value:

| | |
|---|---|
| Day 11, **as logged** | 5431 — the figure at its first commit |
| Day 11, **as merged** | **5433** — its own review rounds added 2 tests |
| this module collects | **11** nodes (at `9f76f905`) |
| Day 12 final | **5444** = 5433 + 11 ✅ measured at `9f76f905` |

⚠ **This reconciliation has now been re-derived FOUR times** (5438 → 5441 → 5443 → 5444; PR #1743 review). The **5438 (+5)** first
recorded was correct at the *first* Day-12 commit, when the module had 5 tests.
The **5441 = 5433 + 8** that replaced it was correct until the very round that
wrote it added `test_every_site_has_exactly_one_strength_class` — a **9th** node
— making the true figure **5442 = 5433 + 9** (PR #1743 review). The module now
collects **11** nodes after the permanent commented-out-site mutant test, giving
**5444 = 5433 + 11**, measured at `9f76f905`.

**The rule this keeps proving — and which I broke once more AFTER writing it
down: a node count written in the same round that adds a node is stale before
the commit lands.** The 5443 (+10) was recorded in the round that added the 11th
node; the suite in that very round measured 5444 and the commit message said
so, but the three mirrors were not re-derived. **So this table is now pinned to
a commit** and is explicitly superseded by whatever the **Day-13 final retest**
measures. Do not update it per review round; update it once, from that run. **A gate figure quoted from the commit that
produced it goes stale the moment a review round adds a test** — the same
banked-staleness shape as the floor-73 template on Day 11, in the same document.


## Day 13 — planned 2026-09-16, **executed 2026-09-18** · retest and close · 6 h · + P10 · 5 h

**Branch:** `planning/sprint39-day13-close` · **Measured at:** `bd2af6e9` (the #1743
merge) · **Docs only** — `src/`, `scripts/`, `tests/` untouched.

### Headline

**Sprint 39 closed. Solve 111 · Match 95 · Translate 135 · genuine floor 75 ·
`path_solve_terminated` 0.** Every KPI figure is unchanged from open **except
Match, which fell 96 → 95 as a correction** — the sprint's one KPI movement,
pre-registered as close rule C2 and reported with its reason in the same
sentence (below). **The sprint had no upward KPI mover by Day-0 decision** (P4
took branch B), which was the pre-registered honest shape, not an
underperformance.

**Match 96 → 95 is a CORRECTION, not a regression.** `weapons` was recorded as a
**presolve** match, but the presolve retry's MCP produced no `MODEL STATUS` of
its own. A `--nlp-presolve` emit warm-starts by solving the original model inside
the generated file, so when that MCP solve aborted, `nlp2mcp_obj_val = tetd.l`
still held the embedded NLP's own answer (1735.5696) and the comparison matched
itself. **This is not "weapons cannot be solved as an MCP"** — its **cold** emit
solves, to `model_optimal` @ **1700.397**, which is a **2.03 %** divergence from
the NLP and therefore a **mismatch**. That cold result is the true record. The
overstatement dates from Sprint 38 Day 9, was reported at the time, and is
corrected here. **Match 95 is the first figure in this series that is true.**
Solve (111), cold-optimal (65) and the genuine floor (75) are unaffected;
presolve-match moves 31 → 30 and all-219 Match 99 → 98 for the same single
reason.

### Closing figures — every one derived at `bd2af6e9`, none recalled (C5)

| quantity | open (Day 0, `388082b0`) | close (`bd2af6e9`) | Δ | source |
|---|---|---|---|---|
| convex candidates | 142 | 142 | — | `kpi_block.py` |
| Parse | 142 | 142 | — | `kpi_block.py` |
| Translate | **135** | **135** | **— (C6 VOID)** | `kpi_block.py` |
| Solve | **111** | **111** | — | `kpi_block.py` |
| Match | **96** | **95** | **−1 (C2 correction)** | `kpi_block.py` |
| &nbsp;&nbsp;cold-optimal | 65 | 65 | — | `kpi_block.py` |
| &nbsp;&nbsp;presolve | 31 | 30 | −1 (weapons) | `kpi_block.py` |
| all-219 Match | 99 | 98 | −1 (weapons) | `kpi_block.py` |
| model_infeasible | 7 | 7 | — | `kpi_block.py` |
| path_syntax_error | 6 | 6 | — | `kpi_block.py` |
| **`path_solve_terminated`** | **0** | **0** | **— (C1 held)** | `kpi_block.py` |
| path_solve_license | 11 | 11 | — | `kpi_block.py` |
| **genuine floor** | **75** (re-baselined 73 → 75 on Day 0) | **75** | — | `floor_tracker.py` |
| P2 ratchet | 9 | 9 | — | `check_index_repeat_properties.py` |
| leak-gate scope | 186 | 186 | — | `check_golden_staleness.py` |
| `make test` | 5301 (Day 0) · 5211 (S38 close) | **5444** | +143 vs Day 0 | this run |

⚠ **The floor is read from `data/floor_provenance.json` via `floor_tracker.py`
on the baseline P1 settled on Day 0 (C4).** The DB's mechanical count is **65**
and is **not** the floor; the tool says so on every run.

### Close gates — the full retest

| gate | result |
|---|---|
| `--resolve-changed --since-commit 9ab2c0c3` | **GO** — scope **discovered** by dry-run (1 model, `dyncge`) then asserted with `--min-scope 1`; `model_optimal`/`mismatch` → same, bucket held |
| `make check-goldens`, **unqualified**, run **alone** | **186 in-scope, all clean, 0 drift, no timeouts** |
| Determinism ×3 `PYTHONHASHSEED` {0, 1, 42} | **PASS ×3** — 186 goldens byte-identical to their committed files under every seed, each run alone |
| `make test` | **5444 passed**, 10 skipped, 1 xfailed |
| `make check-index-repeats` | PASS — P1 0/3,109 · P2 **9 = baseline 9** |
| `make check-doc-figures` | no cited figure contradicts its source |

⚠ **Only one golden changed in the whole sprint** (`dyncge_mcp.gms`, +3/−3, Day 2),
which is why the resolve-changed scope is 1. Every other `src/` change this
sprint was **emit-neutral by construction** — three latent guards and one
result-only diagnostics change — and the unqualified leak gate is what proves
it, four times over.

### The six close rules, each checked against its PRECONDITION (`PLAN.md` §5)

| rule | precondition | precondition held? | verdict |
|---|---|---|---|
| **C1** `path_solve_terminated` maintains 0 | none (cannot be voided) | — | **✅ MET — 0 at open, 0 at close.** No model returned to it |
| **C2** Match may fall to 95, reported as a correction with its reason in the same sentence | P7 started | ✅ P7 landed Day 10 | **✅ MET — 96 → 95, wording above is §5's verbatim block with the floor corrected 73 → 75 on Day 11** |
| **C3** Three-gate firm landing: Phase-0 gate + unqualified leak gate + in `main` | none (cannot be voided) | — | **✅ MET for all three emit landings** (below); two of three is claimed for none |
| **C4** Floor read from `floor_provenance.json` on the P1-settled baseline | P1 decided on Day 0 | ✅ decided 2026-09-03: 75 | **✅ MET — `floor_tracker.py` → 75 at `bd2af6e9`** |
| **C5** Every figure derived at execution time, carrying its commit | none (cannot be voided) | — | **✅ MET — every figure above names its tool and commit** |
| **C6** +1 Translate → 136 only if sarf newly produces a golden | P4 **branch A** started | ❌ **branch B chosen on Day 0** | **⚠ VOID, not unmet.** Translate reports **135 flat**; the re-scope is P4's Day-7/8 attribution (`_diff_sum` 2.9 % self, 70.9 % in `compute_constraint_jacobian`) |

**VOID is not the same as unmet, and C6 is the worked example:** its precondition
was corrected on Day 0 *before* the sprint ran (it read "branch A or B", but B
does not implement and so can never produce a golden). A rule whose precondition
fails says something about the *plan*, not the *work*.

### Firm landings — the three-gate rule (C3) applied

| landing | Phase-0 gate | leak gate (unqualified) | in `main` | bucket |
|---|---|---|---|---|
| **P2 dyncge B-4** — Pattern-C member for the full-collapse Sum (Day 2, #1728) | `ISSUE_1714` ✅ | 186 clean ✅ | ✅ | **0 — PARTIAL.** `eqXp` fixed; `eqII` handed back to #1381 (Day 3). Owner decision to land the partial |
| **P5 #1737** — `src/ir/index_map.py`, repeated EQUATION domain **raises** (Day 9, #1736) | `ISSUE_1737` ✅ | 186 clean ✅ | ✅ | **0 — latent**, no corpus model reaches it |
| **P5 #1741** — Pattern-C B-3 repeated-index guard, **declines to `None`** (Day 11, #1742) | `ISSUE_1741` ✅ | 186 clean ✅ | ✅ | **0 — latent**, no corpus model reaches it |

**Three emit landings, all three-gated, all 0-bucket — and that is the correct
reading, not a disappointment.** Two are guards for a defect class (S38 D11/D12)
that the P5 survey showed is one symbol→position step away from live at 21
sites; the third is a partial fix whose remainder is named. **The two guards
deliberately differ** (raise vs. decline) and the reason is recorded in the
survey so a later reader does not "harmonise" them.

**Non-emit landings, not three-gated because they touch no emit path:** P7's
Remedy A + B (`run_full_test.py` attribution gate; `mcp_file_used` →
`mcp_file_generated` with schema **3.0.0** and a migration, Day 10); the shared
attribution predicates moved into the packaged `src/diagnostics/solve_attribution.py`
(#1740 review); P8's Phase-0 8a/8b requirements and the P1/P2 index-repeat gate
(Day 3, Day 9); P6's consultation follow-up **posted on its gate date** (Day 6 —
the five-sprint slip is broken); P9's Epic-5 design recorded (Day 9).

### REPLAN'd and banked — stated as outcomes, not deferrals

- **P3 lnts** (Days 4–5): hypothesis **CONFIRMED at runtime**, implementation
  written and verified, then **REVERTED** — the mechanism is banked, the landing
  is not, because the fix touched a live-match model's emit path without a
  fail-before the leak gate could hold.
- **P4 sarf** (Days 7–8): **branch B** — attribution, not implementation.
  `_diff_sum` is 2.9 % self, 7.5 % inclusive; **70.9 %** sits in
  `compute_constraint_jacobian`. The Phase-0 gate is authored for whoever
  implements.
- **P10 P2 models** (Day 12): the six triaged into **two classes** — Class A
  (manufactured, coordinate lost) and Class B (declaration-faithful,
  assignment-narrowing). **No fix landed, baseline held at 9**: each Class-A fix
  needs its own Phase-0 doc and a re-solve, and **three of the five Class-A-effect
  models have no solve** (egypt/shale license-gated, nonsharp convexity-excluded).

### The sprint in figures — derived, since a count of findings is a figure too

| figure | value | derivation |
|---|---|---|
| execution-day PRs merged | **18** (#1724–#1743, less two issue numbers and three prep PRs) | `gh pr list --state merged` |
| Copilot review rounds across them | **68** | `gh api .../reviews`, filtered by author, summed |
| of which on the four P7/P5 PRs #1736/#1740/#1742/#1743 | 6 + 7 + 5 + 8 = **26** | same |
| goldens changed | **1** (`dyncge`) | `git diff --stat 9ab2c0c3..HEAD -- data/gamslib/mcp/` |
| DB rows migrated | **48** (2.2.1 → 3.0.0); **47** carry `mcp_file_generated` after Remedy A reverted weapons | `migrate_schema_v3.0.0.py`; DB scan |
| new tests | **+143** vs Day 0 (5301 → 5444) | `make test` |
| P5 sites: guarded / pinned | **4** guarded (#1737 ×2, #1741 ×2) · **16** pinned (5 behaviourally, 11 structurally) | `test_positional_domain_sites.py` |
| prep unknowns | 30, all resolved: 11 ✅ / 11 ❌ / 8 🔶 — refutation **63 %** | `KNOWN_UNKNOWNS.md` |

⚠ **One recalled figure was wrong and is corrected here rather than carried:**
during #1743's review I repeatedly wrote *"fifteen rounds"*; the API says **8**
Copilot reviews on that PR. The 15 counted my own re-issued reply rounds. The
derived figure stands.

### P10 on Day 13 — carried, not worked

The prompt allots 5 h to P10 on this day. Day 12's triage dispositioned it:
**no Class-A fix can be demonstrated correct on three of the five affected
models**, so landing one would move the ratchet without evidence. The 5 h went to
the retest and the four close documents instead; the classified work list is
§*Carryforwards* and `SPRINT_40_CARRYFORWARDS.md`.


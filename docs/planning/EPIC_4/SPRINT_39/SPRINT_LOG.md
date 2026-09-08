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

## Day 5 — planned 2026-09-08, **executed 2026-09-07** · P3: lnts finish · 8 h · + Checkpoint 1 · 2 h

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


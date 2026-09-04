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

## Day 1 — 2026-09-04 · P2: dyncge — confirm the layer · 9 h

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

## Day 2 — 2026-09-04 · P2: dyncge — the new Pattern-C member · 7 h

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

### Carried to Day 3 — the land-or-hand-back decision

`eqII` is a **second, distinct member**, not a gap in B-4:

```gams
eqII(j).. pk*II(j) =e= pf('CAP',j)**zeta*F('CAP',j) / sum(i, pf('CAP',i)**zeta*F('CAP',i)) * (Sp + eps*Sf);
```

A **literal `'CAP'`** in `pf`'s first coordinate, `pf` both inside and outside the `Sum`, and the `Sum` binding only **one** coordinate. B-4 declines on both its full-collapse requirement and its single-pattern guard — correctly. Day 3 chooses: add the literal-index member, or hand the family back to **#1381** as Pattern C Phase B.

---

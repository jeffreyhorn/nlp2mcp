# lnts — Is the Banked Diff Landable? Premise Test & Phase-0 Gate (Sprint 40 Prep Task 8)

**Measured at:** `b134b8b6` (`main`) · **Date:** 2026-10-14 · **Toolchain:** GAMS 54.2.1, every GAMS invocation classified **`licensed`** from its own retained listing

**Scope and hygiene:** every GAMS run went through the retention-patched `solve_mcp` / `kkt_residual.py` inside a **scratch worktree** on a local branch (`scratch/sprint40-task8-guard`) that is **never pushed or landed**. Raw listings lived in a `mktemp` directory removed by an `EXIT` trap. Sanitized provenance for every invocation is in §4. The sketches' `src/` changes were **uncommitted** on that scratch branch, so the `head_sha` in each tuple is `main`'s `b134b8b6`; the sketch itself is described in §3 and preserved as **local-only** commit `5c087e5a` on `scratch/sprint40-task8-guard` (not pushed; the retention patch was never committed). **`src/` is unchanged on this task branch.**

---

## Verdict: **C — not landable this sprint. Remove the +1 Solve from P5's projection.**

Neither the banked diff with a gate (A) nor a symbolic guard (B) can deliver **+1 Solve**:

- **A fails, as banked.** Both of Day 5's REPLAN conditions reproduce **byte for byte** on today's `main`, and **a gate changes neither** (§1).
- **B is only half-achievable.** A narrowed guard removes the perturbation entirely (robot, springchain, otpop, catmix, ganges, gangesx byte-identical), and a positional form removes the literal labels. But it still enumerates cells, by position instead of by name. **More decisively, lnts still does not solve with the collision removed:** MS 5 under every variant (§2, §4).
- **The "second defect" is not lnts's dynamics. It is an emit defect.** `kkt_residual.py` with the collision removed gives **`case_b` at `stat_step`** (relative residual 9.66). **The same `stat_step` row is the worst `case_b` row for robot** (Task 7), so the class is **confirmed for two models**, both COPS time-discretised with `tf =e= step*nh`. **glider** (`stat_step` second-worst, `case_b`) and **rocket** (`stat_step` second, current verdict `CASE_C_OBJDEF`) are **unconfirmed candidates**. **The class is untracked** (§4).

**Recommendation for Task 12:**
- **P5's projection: +1 Solve → +0** (lnts banked).
- **Free P5's budget toward the `stat_step` class**, which bounds **two confirmed models** (lnts, robot), plus up to two candidates (glider, rocket) pending a fresh diagnosis, rather than one. That is a scheduling recommendation, not a decision taken here.

---

## 1. Day 5's failures, and whether a gate would change them (Unknown 5.1)

Re-read in full: `../SPRINT_39/SPRINT_LOG.md` §Day 4–5 and `docs/issues/ISSUE_1694_…md` (the PROCEED/REPLAN signal fixed in advance). The banked diff is commit `0e7fd5fb`'s `src/` change, 50 lines in `emit_gams.py` section 1b. **It still applies cleanly to `main`**, and its emits reproduce Day 5 **exactly**:

| model | `main` emit = golden? | Day-5 emit vs `main` | Day 5 recorded |
|---|---|---|---|
| `lnts` | ✅ | **+292 B** | +292 B |
| `robot` | ✅ | **+135 B** | +135 B |
| `springchain` | ✅ | **+45 B** | +45 B |
| `otpop` | ✅ | identical | identical |

| failed condition (pre-registered) | evidence, re-measured today | would a gate change it? |
|---|---|---|
| PROCEED: "`_fx_` equations remain **and bind at 5 / 45**" | the Day-5 candidate solves **MS 5 @ 1,508 iterations**, identical to Day 5; the probe shows `y2.h50`, `y3.h50` freed, but PATH does not reach the demanded values | **No.** It is a property of the emitted model; a gate only decides whether the change may land |
| PROCEED: "**nothing outside `lnts` drifts**" | robot +135 B and springchain +45 B drift again | **No.** A gate would *detect* the drift and stop the landing; it cannot remove it |
| REPLAN: "perturbs any of the five other models that match the source pattern" | springchain, named in that list, drifts | **No**, same as above |
| REPLAN: "requires per-model enumeration → bank" | the emitted exclusion is literally `sameas(c,'y2') and sameas(h,'h50')`, … | **No.** The emitted text is the same with or without a gate |

**Answer to "was the Day-5 failure procedural?" No.** The CI Phase-0 gate is what *exposed* the misreport on Day 5. But both REPLAN conditions are substantive and reproduce on `main`, and a gate authored first would simply have failed the same diff earlier.

## 2. The runtime bound probe, re-run on `main` (the positive control)

`LNTS_PROBE_DESIGN.md` §3: the effective bounds are displayed immediately before `Solve`, in a **copy** of the emit. Criteria C1–C3 as pre-registered.

| emit | `y2.h50` (D = 5) | `y3.h50` (D = 45) | `y4.h50` (D = 0) | result |
|---|---|---|---|---|
| **`main`** | `lo = up = 0` | `lo = up = 0` | `lo = up = 0` | **C1 ✓ C2 ✓ C3 ✓: the collision is still there.** MS 4 @ iteration 0 |
| Day-5 candidate | free (−INF/+INF) | free | **free** (unnecessarily) | MS 5 @ 1,508 |
| narrowed / positional sketch (§3) | free | free | **`lo = up = 0`** (kept: D equals the blanket value) | MS 5 @ 226 |

## 3. The symbolic guard — sketched on a scratch branch, never landed (Unknown 5.2)

**What the two conditions test.** Both section-1 and section-1b blankets in `emit_gams.py` run over the **same** variables (`kkt.stationarity_conditions`):
- **Section 1** zeroes cells outside the **stationarity condition**. For lnts that condition already enumerates the `_fx_` tuples by label (`main`'s golden, line 156: `… or sameas(c, 'y2') and sameas(h, 'h50') or …`), so it leaves `y2.h50` free.
- **Section 1b** (line 160) zeroes cells outside the **lead/lag condition**, built only from equations with a domain. Its cache skips scalar equations (`if eq_def is None or not eq_def.domain: continue`), and **lnts's `_fx_` equations are scalar**. So 1b never sees that `y2.h50` is constrained, and zeroes it.

**Q2: is there an already-emitted set of fixed tuples?** **No.** The source's `y.fx('y2','h%nh%') = 5` becomes the scalar equation `y_fx_y2_h50`, and **the fixed tuples exist only as literal source labels**. No emitted set or parameter carries them. A guard that references a set would have to *add* one, which moves the label enumeration into set data rather than removing it.

**The sketches** (scratch branch, uncommitted, on top of the banked diff):

1. **Narrowed discriminator.** Exclude a surviving `_fx_` cell from the 1b blanket **only if** (a) the blanket **actually covers it**: the lead/lag condition evaluates **false** at that tuple, which the emitter computes from the sets' static member order; **and** (b) its demand **differs** from the blanket's value. This is "the pruning guard actually covers the fixed tuple", evaluated at emit time: `ISSUE_1694` said it "cannot be read off the source", but it can be read off the IR's static sets.
2. **Positional form.** Write each excluded cell as `ord`/`card` instead of `sameas`. The lnts guard becomes `… or (ord(c) = 2 and ord(h) = card(h)) or (ord(c) = 3 and ord(h) = card(h))`: **no labels**.

**Emit diffs against `main`** (each `main` emit verified byte-identical to its golden first):

| model | Day-5 banked | narrowed (labels) | positional (no labels) |
|---|---|---|---|
| `lnts` | +292 B | +86 B: **exactly** `y2.h50`, `y3.h50` | changed: the two cells, positionally |
| `robot` | **+135 B** | **identical** | **identical** |
| `springchain` | **+45 B** | **identical** | **identical** |
| `otpop` (negative control) | identical | identical | identical |
| `catmix` | — | — | **identical** |
| `ganges` | — | — | **identical** |
| `gangesx` | — | — | **identical** |

**Positive control:** the Day-5 guard and the symbolic guard **differ** on lnts, robot and springchain, as the task requires.

- **Why Day 5's drift was semantically empty:** every robot and springchain cell the banked diff touched was already consistent or never reached. robot's `*_dot` cells demand 0 at `firstlast`, which is the value the blanket writes. springchain's `x.n0` demands 0, and `x.n10` lies outside the blanket (`ord(n) > 1` holds there).

**Answer:** 🔶 **partly.**
- Perturbation is **solved**: robot, springchain, otpop, catmix, ganges and gangesx are byte-identical.
- Labels are **removable**: the positional form contains none.
- But the exclusion **still enumerates cells**, by position, derived per model from its `fx_map`. In general (an interior fixed tuple), the positional form is `ord(i) = k`, a per-model constant.
- **Whether that satisfies "not per-model enumeration" is a judgment the pre-registered signal did not anticipate. This task does not settle it**, because §4 makes it moot for this sprint.

## 4. The second defect — scoped (Unknown 5.3)

**Reproduced:**
- The Day-5 candidate is MS 5 @ **1,508** iterations. **365** rows are flagged `INFES` by this run's counter (Day 5 reported 364; the counter tallies listing lines, so ±1 is the counting method): `stat_y` 105, `pos_eqn` 100, `velo1_eqn` 50, `velo2_eqn` 50, `comp_lo_u` 28, `comp_up_u` 23, …
- The narrowed / positional sketch is still MS 5, @ 226 iterations, with 208 `INFES` rows (`stat_y` 102, `pos_eqn` 100).

**Classified:** `kkt_residual.py data/gamslib/raw/lnts.gms`, run with the sketch `src` (the collision removed), gives **`case_b` (emit bug)**:
- dual transfer **consistent**;
- worst row **`stat_step`**, relative residual **9.66**; the next four rows the report lists are all below 0.008.
- At the NLP's own KKT point, the emitted **stationarity equation for the scalar `step`** is wrong. So it is **emit / KKT, not the model's dynamics**: the `velo1_eqn` / `tf_eqn` `INFES` rows Day 5 saw are where PATH ends up after following a wrong `stat_step`.

**It is a cross-model class:**

| model | source structure | `kkt_residual.py` |
|---|---|---|
| `lnts` | `tf_eqn.. tf =e= step*nh;` | `case_b`, worst `stat_step` rel 9.66 (this task) |
| `robot` | `tf_eqn.. tf =e= step*nh;` | `case_b`, worst `stat_step` rel 10.1 (Task 7) |
| `glider` | `tf_eqn.. t_f =e= step*nh;` | `case_b`, `stat_step` second-worst rel 0.38 (Task 7) |
| `rocket` | COPS time-step | **current verdict `CASE_C_OBJDEF`** (not `case_b`): worst `stat_ht(h0)` rel 1.00, `stat_step` **second** at 0.497 (`SPRINT_38/ROCKET_CONSULTATION_EXTERNAL.md`; this supersedes `ISSUE_1462`'s Sprint-29 `case_b`) |

**Membership:** **confirmed** where `stat_step` is the worst `case_b` row: **lnts, robot**. **Unconfirmed candidates:** **glider** (`case_b`, but `stat_step` is second to `stat_cl`) and **rocket** (`stat_step` second under a `CASE_C_OBJDEF` verdict). Each needs a fresh full diagnosis before it is counted in the class.

**Tracked?** **No issue tracks a `stat_step` defect.** `ISSUE_1694` calls it lnts's "dynamics"; `ISSUE_1462` records rocket's residual as `CASE_C_OBJDEF` (latest) and earlier attributed it to the `_fx_`-at-`h0` warm start. **Needs one** (routed below).

**Provenance of every Task-8 measurement** (sanitized: edition class and solver from each invocation's own retained listing, then deleted). Several source variants share `head_sha` `b134b8b6`, because the sketch `src/` was uncommitted. **The variant column is what distinguishes them**, and each input was a separately named copy (`<model>_<variant>_mcp.gms`), so every row associates with exactly one invocation:

| model | variant | stage | site · phase | edition | solver | MS / iterations | invocation id | head_sha |
|---|---|---|---|---|---|---|---|---|
| `lnts` | `main` golden + bound probe | `probe` | `solve_mcp` · `batch` | licensed | PATH | 4 / 0 | `lnts_mainprobe_mcp.1792015132780435000.30262` | `b134b8b6aaf0ddfc3fd3332d1a8f2467bb94d4cc` |
| `lnts` | `main` golden | `mcp` | `solve_mcp` · `batch` | licensed | PATH | 4 / 0 | `lnts_main_mcp.1792015139943778000.30472` | `b134b8b6aaf0ddfc3fd3332d1a8f2467bb94d4cc` |
| `lnts` | Day-5 banked + bound probe | `probe` | `solve_mcp` · `batch` | licensed | PATH | 5 / 1508 | `lnts_day5probe_mcp.1792015142620120000.30570` | `b134b8b6aaf0ddfc3fd3332d1a8f2467bb94d4cc` |
| `lnts` | Day-5 banked | `mcp` | `solve_mcp` · `batch` | licensed | PATH | 5 / 1508 | `lnts_day5_mcp.1792015147239519000.30740` | `b134b8b6aaf0ddfc3fd3332d1a8f2467bb94d4cc` |
| `lnts` | narrowed/positional sketch + bound probe | `probe` | `solve_mcp` · `batch` | licensed | PATH | 5 / 226 | `lnts_symprobe_mcp.1792015151994169000.30903` | `b134b8b6aaf0ddfc3fd3332d1a8f2467bb94d4cc` |
| `lnts` | narrowed/positional sketch | `mcp` | `solve_mcp` · `batch` | licensed | PATH | 5 / 226 | `lnts_sym_mcp.1792015157634603000.31060` | `b134b8b6aaf0ddfc3fd3332d1a8f2467bb94d4cc` |
| `robot` | Day-5 banked | `mcp` | `solve_mcp` · `batch` | licensed | PATH | 5 / 27417 | `robot_day5_mcp.1792015162328272000.31216` | `b134b8b6aaf0ddfc3fd3332d1a8f2467bb94d4cc` |
| `springchain` | Day-5 banked | `mcp` | `solve_mcp` · `batch` | licensed | PATH | 1 / 289 | `springchain_day5_mcp.1792015184006152000.31980` | `b134b8b6aaf0ddfc3fd3332d1a8f2467bb94d4cc` |
| `springchain` | `main` golden | `mcp` | `solve_mcp` · `batch` | licensed | PATH | 1 / 289 | `springchain_main_mcp.1792015186408468000.32091` | `b134b8b6aaf0ddfc3fd3332d1a8f2467bb94d4cc` |
| `lnts` | sketch `src` (residual cold start) | `residual-cold` | `solve_mcp` · `residual` | licensed | PATH | 5 / 226 | `lnts_mcp_cold.1792015205672347000.32190` | `b134b8b6aaf0ddfc3fd3332d1a8f2467bb94d4cc` |
| `lnts` | sketch `src` (residual evaluation) | `residual` | `kkt_residual` · `residual` | licensed | PATH | 6 / 0 | `lnts_mcp_presolve_residual.1792015193636538000.32190` | `b134b8b6aaf0ddfc3fd3332d1a8f2467bb94d4cc` |

*Emit-only steps (the seven-model diffs in §3) launch no GAMS and so have no invocation. The robot baseline is Task 7's committed tuple, not a new solve.*

**robot's drift (Q3):**
- **Baseline:** Task 7's committed row: `model_infeasible` (MS 5), `MCP-FAILED` / own, `case_b`, provenance `mcp`·licensed·PATH·`robot_mcp.1792010281137925000.13402`·`79eeccff`.
- **Day-5 candidate emit**, solved licensed here: **MS 5 @ 27,417 iterations**, objective 11.464 (NLP reference 9.1469), `MCP-FAILED`. **Same bucket, so not harmful, and not helpful.** The narrowed / positional sketches leave robot **byte-identical**, so the question disappears for B.

**springchain (Q4):**
- The Day-5 emit and `main`'s golden solve identically: **MS 1, 289 iterations, objective −185.446** (both re-solved here).
- Under the pre-registered wording it is **perturbed** (the emit changed) though not **broken**, so the criterion fires as Day 5 said.
- **It should not be weakened.** The narrowed discriminator shows the perturbation was avoidable, so "perturbed" stays the right test.

## 5. Phase-0 gate — for the surviving branch (a future landing, not this sprint)

**Layer:** `src/emit/emit_gams.py`, section **1b** (the lead/lag blanket), plus the **`stat_step` stationarity** path in `src/kkt/stationarity.py`. A future landing needs **both**: the guard alone is proven insufficient.

**Fail-before (must hold on the pre-change emit):**
- the §2 probe on lnts shows C1 ✓ C2 ✓ C3 ✓ (`y2.h50`, `y3.h50` at `lo = up = 0` against demands 5 and 45);
- lnts is MS 4 @ iteration 0;
- `kkt_residual.py` on lnts, with the guard applied, gives `case_b` at `stat_step`.

**Pass-after (all required):**
1. **probe:** `y2.h50`, `y3.h50` free, **`y4.h50` still `lo = up = 0`** (only contradicted cells are excluded);
2. **lnts** solves **MS 1/2**, attributed **`MCP-SOLVED` / own=True**, and the `_fx_` rows bind at **5 and 45** (within solver tolerance);
3. **`kkt_residual.py`** on lnts reports the dual transfer **consistent** and **every** stationarity row's relative residual **within the harness tolerance** (default 0.001). A mere change in which row is worst does **not** pass: 0.005 at `stat_step` and 0.007 at `stat_y` both exceed tolerance, yet would move the worst-row label;
4. **perturbation:** the emits of **`robot`, `springchain`, `otpop`** (plus `catmix`, `ganges`, `gangesx`) are **byte-identical** to their pre-change goldens for the **guard** half. The `stat_step` half is *expected* to change robot (and possibly the candidates glider and rocket), so it needs its **own** gate: each changed model's stationarity rows must meet check 3's tolerance test;
5. **no labels and explicit owner approval, both required:** the 1b guard emits no `sameas(…, '<label>')` of its own, **and**, because a positional guard still enumerates cells, the owner has **explicitly approved** per-model positional enumeration in a dated decision recorded **before** the landing. A rejection, or no decision, blocks the landing; it is not a pass.

**+1 Solve may be claimed only when (2) holds on a cold solve.** A presolve-only match would be booked under the existing methodology rule.

## 6. Routing

- **lnts → banked** (P5: +1 → +0). The guard design (§3) is kept for whoever picks up the `stat_step` class.
- **New: the `stat_step` stationarity class** (confirmed: lnts, robot; candidates pending a fresh diagnosis: glider, rocket): **needs an issue**, and Task 12 decides where it sits (P2's R-B-robot / R-B-glider already point at it, and `ISSUE_1462` should cross-reference it).
- **robot:** unchanged from Task 7 (R-B-robot), now known to be this class.

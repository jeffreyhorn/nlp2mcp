# Sprint 38 Day 11 — P5 close + P8 sweep day 3: tricp #1062

**Date:** 2026-08-25 · **Branch:** `planning/sprint38-day11-p8-sweep` · **Measured at:** `3f2a2067` · **Toolchain:** GAMS **54.2.1** / PATH **5.2.01**

**Verdict: ✅ P5 CLOSED (Unknown 5.1 → procurement) · ✅ P8 tricp #1062 FIXED — 108 unmatched → 0, `stat_slp`/`stat_sln` NONE → 54 rows each · ⚠ 0 bucket moves, and tricp becomes the license-gated cohort's 11th member.**

**Two prompt premises are corrected up front, both by measurement:**

1. The Day-11 prompt body says *"Next: **dyncge** (#1331's mechanism, so it can borrow that shape)."* **Its rationale is false and was already refuted on Day 3** — `dyncge`'s `eqpf2(h_mob,i,j).. pf(h_mob,j) =e= pf(h_mob,i)` self-cancels at `i=j` with **no condition anywhere**, so #1331's condition-lift cannot detect it. The prompt's own header, and `PLAN.md` §5, both name **tricp #1062** for Day 11. **tricp is what was worked.**
2. `ISSUE_1062`'s gate expects that **only `tricp` drifts**. **Two models carry the defect**, not one — `ferts` has the identical shape at `xi(c,i,i)`. The second drift is intended and is declared here *before* the gate was run, not rationalised after it.

---

## 1. P8 — tricp #1062

### 1.1 Fingerprint re-reproduced, not quoted

Fresh translate from `data/gamslib/raw/tricp.gms` at `3f2a2067`; the output is **byte-identical to the committed golden**, so the golden is what was measured.

Run from a scratch directory, `gams tricp_mcp.gms lo=0 errmsg=1`:

| criterion (§4.1) | measurement |
|---|---|
| GAMS return code | **3** |
| **anchored** `^**** Unmatched variable not free or fixed` | **108** |
| tally by symbol | **54 `slp` + 54 `sln`** |
| columns are **on-edge** | `slp(n0,n1)`, `slp(n0,n2)`, `slp(n0,n3)`, … |
| **terminal state, read from GAMS's own line** | `**** SOLVE from line 205 ABORTED, EXECERROR = 108` |
| **the decisive structural check** | `---- stat_sln  =E=` → `NONE` · `---- stat_slp  =E=` → `NONE` |

`e` has **54 edges and no self-loops** (counted from the source's set literal), and `card(n) = 20`. 54 + 54 = 108 exactly.

**The doc's headline figure stays refuted.** The title's *"760 MCP errors"* does not reproduce (108 does), and the note claiming `$148`/`$149` compilation errors block reproduction is stale — the model compiles cleanly. Both were already corrected in the Day-2 gate; re-measured today, both hold.

### 1.2 Negative control — a passing one, in isolation

The claimed mechanism is *"a repeated controlling index in an equation **definition** binds to the same element"*. That is a runtime property of GAMS, so it was observed at runtime rather than asserted from the manual:

```gams
Set n / n0*n5 /;  Set e(n,n) / n0.n1, n1.n2, n2.n3 /;  Alias(n, n__);
Variable v(n,n), w(n,n);  Equation diag(n,n), spanned(n,n);
diag(n,n)..      (v(n,n))$(e(n,n))    =E= 0;
spanned(n,n__).. (w(n,n__))$(e(n,n__)) =E= 0;
```

```
---- diag  =E=                    ---- spanned  =E=
                NONE              spanned(n0,n1)..  w(n0,n1) =E= 0 ;
                                  spanned(n1,n2)..  w(n1,n2) =E= 0 ;
                                  spanned(n2,n3)..  w(n2,n3) =E= 0 ;
```

Unconditioned, the same pair generates **6 + 36 = 42** single equations — the diagonal versus the full product. The control reproduces tricp's exact `NONE` signature from six lines of GAMS with no nlp2mcp involvement.

### 1.3 The fix surface — traced, and NOT where the gate hypothesised

The Day-2 gate traced the fix to *"the stationarity head-domain emission in `src/emit/emit_gams.py`"*. **That is the wrong layer.** The head domain is not decided in the emitter; it is `domain=var_def.domain` at `src/kkt/stationarity.py:2296`, taken verbatim from the variable's declaration — and, more importantly, the **same repeated tuple is what the body is built from**, positionally. Renaming only the head would have left the body referring to `n` in both positions.

Nor is the emitter reached in time: `compute_objective_gradient` runs **before** KKT assembly, and the repeat had already collapsed the objective gradient there — `∂/∂slp` came out as `sum(i, 1$(e(n,i)))`, a summation over the second index, because position 2 had no symbol of its own to bind.

**The change is therefore a pre-differentiation IR pass**, `src/kkt/repeated_domain.py`:

> `dedupe_repeated_variable_domains(model_ir)` — for each variable whose declared domain repeats a set symbol, rewrite the second and later occurrences to a freshly minted alias of that set (`n` → `n__`), registering the alias so the emitter declares it. Wired into `src/cli.py` as step 2.7, immediately before "Compute derivatives".

**It is an exact identity for any variable whose domain has no repeat**, which is what bounds the blast radius (§1.5).

**A second, non-obvious defect had to be fixed with it.** With `slp`'s domain now `(n, n__)`, `_remap_condition_to_domain` still produced the diagonal guard `$(e(n,n))`. Its #1350 lookup asks *"which var_domain index has root `n`?"* — and `e` is **itself** declared `e(n,n)`, so it asks that at **both** positions and a first-match scan answers `n` twice. Each domain slot may now be claimed by at most one condition index. For any domain with no two entries sharing a root, the new scan returns exactly what the old one did.

**Emitted, after (`stat_slp`, `.fx` guard, bound complementarity):**

```gams
Alias(n, n__);
stat_slp(n,n__).. (1$(e(n,n__)) + (((-1) * nu_eq1(n,n__))$(i(n) and j(n__)))$(e(n,n__))
                   - piL_slp(n,n__))$(e(n,n__)) =E= 0;
comp_lo_slp(n,n__).. slp(n,n__) - 0 =G= 0;
slp.fx(n,n__)$(not (e(n,n__))) = 0;
```

Note the gradient term is now `1$(e(n,n__))` — the spurious `sum(i, …)` is gone, which is the pre-differentiation placement paying off.

### 1.4 Pass-after — the gate's PROCEED criteria, measured

| gate criterion | before | after |
|---|---|---|
| anchored `Unmatched variable not free or fixed` | **108** | **0** |
| `stat_slp` rows generated | **0** (`NONE`) | **54** |
| `stat_sln` rows generated | **0** (`NONE`) | **54** |
| model statistics | 387 eq × 640 var | **1,255 eq × 1,400 var** |
| terminal state (GAMS's own line) | `ABORTED, EXECERROR = 108` | `**** Terminated due to a licensing error` |

The emitted rows carry the hand-derived KKT shape exactly:

```
stat_slp(n0,n1)..  - nu_eq1(n0,n1) - piL_slp(n0,n1) =E= -1 ;
```

i.e. `1 − nu_eq1 − piL_slp = 0`, the objective's unit coefficient on `slp(e)` minus `eq1`'s and the lower bound's — which is what §"Hand-Derived KKT Shape" predicted.

**The gate's third PROCEED clause, *"`tricp` reaches PATH", is NOT met and cannot be on this license.** Fixing the collapse takes the MCP from 387 rows to **1,255**, past the GAMS demo limit of 1000 nonlinear rows. GAMS's own lines:

```
**** The model exceeds the demo license limits for nonlinear models of more than 1000 rows or columns
**** Terminated due to a licensing error
```

Classified with the project's own taxonomy (`scripts/gamslib/test_solve.py`), not by eye:

```
BEFORE(fix) -> no_solve_summary -> path_solve_terminated
AFTER(fix)  -> license_limit    -> path_solve_license
```

**So the correct reading is: the KKT defect is fixed and structurally verified; the solve is now blocked by capacity, not by us.** The original NLP is *under* the demo limit (it solves — `model_status 2 @ 3838.2686`); the KKT expansion is what crosses it.

### 1.5 Blast radius — measured before the change, not after

Scanning every committed golden for a `stat_*` / `comp_lo_*` / `comp_up_*` head whose index tuple repeats a symbol:

| model | heads |
|---|---|
| `tricp` | `stat_slp(n,n)` · `stat_sln(n,n)` · `comp_lo_slp(n,n)` · `comp_lo_sln(n,n)` |
| `ferts` | `stat_xi(c,i,i)` · `comp_lo_xi(c,i,i)` |

**Exactly two, out of the whole corpus.** Every other model has no repeated-symbol variable domain, so the pass is a literal no-op for it.

**`ferts` was carrying a silent wrong answer, and it is worth naming.** Its `stat_xi` body is a sum of ~50 fixed-value multiplier terms guarded by conjunctions like

```gams
nu_xi_fx_ammonia_assiout_aswan$(sameas(c,'ammonia') and sameas(i,'assiout') and sameas(i,'aswan'))
```

`sameas(i,'assiout') and sameas(i,'aswan')` is **identically false** — one symbol cannot equal two labels. Every off-diagonal `_fx_` term was therefore silently dropped. After the pass the third conjunct reads `sameas(i__,'aswan')` and the terms survive. `ferts` is `path_solve_license`, so this **cannot** move a bucket; it is a correctness repair to a golden that no solve has ever exercised.

> **This qualifies the cohort record written today.** §4.1 of the handoff says all ten cohort members *"have committed goldens — translate succeeded"*. `ferts` shows that "a golden exists" and "the golden is right" are different claims, and the second one has never been tested for any cohort member, because none of them solve.

### 1.6 Gates

- **`make test`** — **5211 passed** before the new tests, **5223 passed** after (10 skipped, 1 xfailed, 432 s), re-run against the adopted goldens and the updated DB.
- **New tests** — 8 unit (`tests/unit/kkt/test_repeated_domain_dedupe.py`), 2 regression on the remap's slot-claiming (`tests/unit/kkt/test_remap_condition_to_domain.py`), 2 integration on tricp's emitted head (`tests/integration/emit/test_tricp_repeated_domain_head.py`).
- **`ferts` compile check** — `gams ferts_mcp.gms action=c` → **rc 0**; the only anchored `^****` line in the listing is `**** FILE SUMMARY`, i.e. no error diagnostic. (It cannot be solved on this license, so a compile is the strongest available check.)
- **Determinism ×3** — `PYTHONHASHSEED` 0 / 1 / 42, both models: **1 distinct hash each**, and both **byte-identical to the committed golden**.
- **Goldens adopted** — `check_golden_staleness.py --fix` refreshed **exactly 2** (`ferts` +143 B, `tricp` +83 B).
- **DB update** — `run_full_test.py --model tricp` / `--model ferts`. The diff touches **exactly two model entries**, and carries **exactly one semantic change**: tricp's `outcome_category` `path_solve_terminated` → `path_solve_license`. `ferts` re-solves to `path_solve_license`, unchanged.
- **Full-corpus leak gate** — see §3.

---

## 2. P5 — CLOSED

**Unknown 5.1 closes as a tracked *procurement* item, not an engineering result.** Nothing here is new measurement; §4 of `CAMCGE_EPIC5_HANDOFF.md` already carries the full record, and the close is the act of fixing it as the standing wording.

**The cohort (10):** `egypt` · `ferts` · `glider` · `robot` · `shale` · `sroute` · `srpchase` · `tabora` · `tfordy` · `turkey`.

| property | value |
|---|---|
| share | **10 of 142 convex candidates (7 %)** |
| signature | all `path_solve_license`, all `not_tested`, all **`solver_version: None`** — rejected at *generation*, PATH never invoked |
| emit | all ten have committed goldens; only the **solve** is blocked |
| **ceiling** | **Solve +10**, as one batch |
| treatment | **excluded from KPI projections**; **not** written off — capacity is being pursued with the same people as the P3 consultation |

**The standing wording, applicable verbatim wherever these models are projected:**

> **License-gated cohort:** all emit correctly (goldens committed) and all are rejected at **generation** by the GAMS demo 1000-row nonlinear limit — `solver_version: None`, PATH never invoked. **Excluded from KPI projections** until a larger license exists; **not** written off, as one is being pursued. Re-test as a **single batch** on capacity.

**Two amendments this day forces:**

1. **The cohort is 11, not 10.** `tricp` joins it (§1.4) — same signature, same block, same batch. The ceiling is **Solve +11** against today's Solve, not +10. `tricp` is `likely_convex`, so it is inside the 142.
2. **"Emit verified" means "a golden exists", not "the golden is correct"** (§1.5). No cohort member's emit has ever been exercised by a solve; `ferts` was wrong and nothing caught it.

**Why a reduced instance still buys nothing:** the KPI requires *the model itself* to solve and match. This is unchanged, and is worth restating because it is the tempting engineering workaround.

---

## 3. Leak gate

**Scope stated, per the standing rule: 185 in-scope goldens (7 allowlisted), not 163.**

```
Golden staleness: checked 185 in-scope golden(s) (7 allowlisted, 3 workers).
    EXPECTED DRIFT: ferts_mcp.gms (+143 bytes)
    EXPECTED DRIFT: tricp_mcp.gms (+83 bytes)
  LEAK GATE PASS: exactly the expected model(s) drifted (ferts, tricp); all other in-scope goldens byte-identical.
```

**Both drifts were declared before the gate ran** (§1.5), from a scan of the committed goldens for repeated-symbol heads — not read off the gate and rationalised afterwards. The gate is an unqualified **PASS**, not a `PARTIAL`.

**Models with no committed golden are outside this gate, so they were checked separately.** Of the 219 raw sources, 16 have no golden *and* contain an adjacent repeated index tuple. Parsing each and inspecting **variable** domains specifically, exactly one — `lop`, with `dtr(s,s,s,s)` — has a repeated variable domain; the other 15 either fail to parse or have none. `lop` is `convexity: excluded` and is rejected as **discrete** (`phi` INTEGER, `x` BINARY, `y` INTEGER) before differentiation is reached, so the pass cannot run on it. **No non-golden model is affected.**

---

## 4. KPI

Derived with `scripts/sprint_audit/kpi_block.py` and `scripts/sprint_audit/floor_tracker.py`, never quoted.

| | at `3f2a2067` (start of day) | after Day 11 |
|---|---|---|
| Solve | 109 | **109** |
| Match | 95 (65 cold + 30 presolve) | **95 (65 + 30)** |
| Translate | 135 | **135** |
| `path_solve_terminated` | 3 | **2** |
| **license-gated** | **10** | **11** |
| **genuine floor** | **73** | **73** |

Re-derived at the **clean commit `a43ea7b2`** (no dirty-DB warning):

```
Solve 109 · Match 95 (65 cold + 30 presolve) · Translate 135 · mi 7 · pse 6 · all-219 98 — derived at a43ea7b2
Genuine floor: 73   (derived at a43ea7b2)  = baseline 73 (as of S37-close) + 0 recorded movement(s)
```

All three census figures were **re-derived after the DB update**, and the license census reads `11` with `path_solve_terminated` down to `2` (`dyncge`, `elec` — Day 12's two candidates).

**0 bucket moves, exactly as `ISSUE_1062`'s gate predicted** ("0 bucket expected … Translate-stable, Solve-uncertain, Match-unclaimed"). The one census change is lateral: `tricp` leaves `path_solve_terminated` and joins `license-gated`.

**The floor is untouched and no provenance entry is due.** `tricp` did not match — it did not solve. `floor_tracker.py` reports **73** from the provenance file, unchanged.

**Report the lateral move in the same sentence as the win, or it reads wrong in both directions.** "`path_solve_terminated` 3 → 2" alone reads as progress toward a solve; "license-gated 10 → 11" alone reads as a regression. Neither is true on its own: **a genuine emit defect was removed, and the model it unblocked is now blocked by license capacity instead.**

---

## 5. Carry

- **#1062 → resolvable once capacity exists.** The emit defect is fixed and structurally verified (54 rows, 0 unmatched, correct KKT shape). What remains is a solve, which needs the license. It re-tests with the cohort batch; nothing further is owed by engineering.
- **The dyncge/lnts shortlist is untouched** and remains for Day 12 in the P7 sweep order. Day 11 deliberately did not start dyncge (§ opening note).
- **A generalisable finding for the sweep:** the P7 gates' traced fix surfaces are hypotheses — this one carries its own `⚠ Traced hypothesis, not a result` warning — and it was **wrong about the layer**, not merely the line: `emit_gams.py` versus a pass that has to run *before* differentiation. The standing rule (prep-doc `file:line` fix-surfaces are hypotheses; bugs are usually decided upstream of the emitter) held again. **The remaining four gated candidates should be re-traced from `stationarity.py` and the AD entry points outward, not from the emitter inward.**

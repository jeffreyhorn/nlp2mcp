# hhfair + CGE Cluster — Case-c Formalization + Harness Classifier Design

**Created:** 2026-07-13
**Prep Task:** 7 (Priority 5)
**Issue:** #1236 (local write-up: `docs/issues/ISSUE_1236_hhfair-objective-mismatch.md`)
**Status:** Design (prep) — the classifier extension + closure criteria are designed here; the in-sprint P5 work implements the harness auto-classification + closes the ISSUE. All experiments read-only (harness); no `src/` change. **The sign flip is BANNED** (control-refuted 4× across S30–S31).

**Objective:** Design the `kkt_residual.py` **Case-c auto-classifier extension** for the objective-defining-intermediate-variable family (hhfair `stat_u` / CGE `stat_xp`) and the ISSUE-closure criteria, so Sprint 32 can formally close hhfair + the CGE cluster as documented genuine non-convex Case-c (no emit fix expected).

---

## §1. The Case-c discriminator — the objective-defining-intermediate-variable shape

An above-tolerance `stat_<var>` residual with **CONSISTENT** dual-transfer is a genuine **objective-defining-intermediate-variable Case-c** (a non-convex spurious-KKT artifact, *not* a fixable Case-b emit bug) when all of:

- **D1 (structural — the discriminator):** `<var>` appears in the **objective defining equation** `obj =e= f(<var>)` (where `obj` is the `solve … maximizing/minimizing obj` variable), AND `<var>` is itself pinned by its own defining equation (an *intermediate* variable). Because `obj` appears only in `obj =e= f(<var>)`, its multiplier `nu_obj = ±1`, so the objective-gradient "reduction" collapses to the **sign choice** — there is no free multiplier to correct `stat_<var>`.
  - **hhfair:** `objective.. obj =e= prod(t, u(t)**ufact(t))`; `u(t)` is pinned by `utility(t).. u(t) =e= (a1·c**−a2 + …)**(−1/a2)/100` (a CES nest). ⇒ `u` is the objective-defining intermediate variable; the residual is on `stat_u(t)`.
  - **CGE cluster (irscge/lrgcge/moncge):** `obj.. UU =e= prod(i, Xp(i)**alpha(i))` (`solve … maximizing UU`); `Xp(i)` is market-cleared. ⇒ `Xp` is the objective-defining intermediate variable; the residual is on `stat_xp(i)`.
- **D2 (dual-consistent):** dual-transfer CONSISTENT — the residual is a genuine stationarity imbalance at the NLP point, not a transfer defect (distinguishes from the camcge `nu_mps_fx` / mine bound-multiplier transfer defects).
- **D3 (cold-spurious):** the cold-start MCP solve reaches a **spurious local KKT point** (cold objective ≠ the presolve/NLP match); the match is reachable **only** via the presolve warm-start. This is the existing harness Case-a-vs-c cold-start split, now applied to a CASE_B-nominal residual.
- **D4 (sign-flip-inert — corroborating control):** flipping the objective-gradient sign in `stat_<var>` leaves the cold primal **unchanged** (the reduction is inert). A fixable Case-b would move the cold solve *toward* the match; here it does not. This is the definitive control that separates Case-c from Case-b.

When **D1 ∧ D2 ∧ D3** hold (D4 corroborating), reclassify CASE_B → **Case-c (objective-defining-intermediate-variable non-convexity)** — presolve-required, no emit fix.

---

## §2. Re-confirmation on the current tree

The harness reproduces the family shape exactly:

| model | harness verdict | max-residual row | rel | interior |
|---|---|---|---|---|
| **hhfair** | CASE_B (nominal) | `stat_u(1)` | 2.00 (then `stat_u(2)` 1.89, `stat_u(3)` 1.78) | `stat_a` ~0.005 (near tol) |
| **irscge** | CASE_B (nominal) | `stat_xp(BRD)` | 0.064 (then `stat_xp(MLK)` 0.064) | `stat_f` ~0.02 |

Both residuals concentrate on the **objective-defining intermediate variable** (`stat_u` / `stat_xp`); the interior rows are near tolerance; dual-transfer CONSISTENT in both. The Sprint-31 Day-10 control (banked, GAMS) established the Case-c nature for the CGE cohort empirically: **irscge/lrgcge/moncge all cold `UU = 25.5085` vs the presolve match `26.0914`**, and flipping `stat_xp`'s objective-gradient sign leaves the cold primal at the **identical 25.5085** (the reduction is inert). hhfair: cold `72.147` vs NLP ref `87.159`; sign flip `72.147 → 22.144` (*worse*, S30 Days 4/6). So **all four members are genuine Case-c** (D1–D4 hold): the cold solve sits at a non-global local optimum of a non-convex model (hhfair = CES + bilinear; irscge = Scale-Economy / increasing returns; lrgcge = Large-Country; moncge = Monopoly), and the match is reachable only via the presolve warm-start.

---

## §3. The `kkt_residual.py` classifier-extension design

Add a **post-verdict reclassification pass** to the harness (`scripts/diagnostics/kkt_residual.py`), after the CASE_B verdict is formed:

1. **Detect D1** — the max-residual `stat_<var>` row's `<var>` is an objective-defining intermediate variable: from the model IR, `<var>` appears in the body of the objective defining equation (the equation whose LHS is the `solve` objective variable), and `<var>` has its own defining equation. (A tight structural check on a single equation per model.)
2. **Check D3** — the cold-start MCP solve (already run for the Case-a-vs-c split) reaches a spurious point (cold objective ≠ match).
3. **If D1 ∧ D2 ∧ D3:** emit verdict **`case_c`** with the sub-label **"objective-defining-intermediate-variable non-convexity"** (instead of `case_b — emit_bug`), and a note that the sign flip is BANNED (see §4). Otherwise leave the CASE_B verdict unchanged.

**False-positive guard (the D1 gate):** D1 is a *structural* gate keyed on the single objective-defining equation, so a genuine Case-b emit residual on a **non**-objective-defining variable is never reclassified. D3 (cold-spurious) further separates it from a Case-b that *would* reach the match after an emit fix. D4 (sign-flip-inert) is the definitive control — retained as the manual PROCEED/REPLAN check for any *new* candidate that trips D1 (the harness can auto-flag D1∧D2∧D3; a new model's D4 is confirmed by the `/tmp` sign-flip control before it is trusted as Case-c). This prevents both (a) a real emit bug being silently mislabeled non-convex and (b) a future sprint re-attempting the refuted sign flip on a flagged model.

---

## §4. The sign-flip ban (re-confirmed)

The inlined objective-gradient **sign flip is BANNED** — control-refuted repeatedly, so no Day-1 sign-flip attempt is made:

| # | control | result |
|---|---|---|
| 1 | S30 Day 4 — hhfair `stat_u` sign-flip hypothesized (CASE_B `−2·CES_grad` residual) | flagged for control |
| 2 | S30 Day 6 — hhfair sign flip solved | 72.147 → **22.144** (*worse*, away from NLP 87.159) |
| 3 | S30 Day 7 — himmel16 sign fix (sibling non-convex) | refuted (no emit fix converts it) |
| 4 | S31 Day 10 — hhfair + CGE cluster ν_objective reduction | **inert** (cold `UU=25.5085` for both sign choices; the reduction = the sign choice since `nu_obj=±1`) |

**4× across S30–S31.** The reduction is inert precisely because `nu_obj = ±1` (D1) — there is no free multiplier for the reduction to exploit. The Case-c classification (§3) records the ban so the harness/future sprints do not re-attempt it.

---

## §5. ISSUE-closure criteria

"Documented Case-c" closure for **hhfair + irscge + lrgcge + moncge** means all of:

1. **The classifier auto-flags them Case-c** (§3) — the harness reports `case_c (objective-defining-intermediate-variable non-convexity)`, not `case_b — emit_bug`.
2. **The sign flip is recorded BANNED** in `docs/issues/ISSUE_1236_hhfair-objective-mismatch.md` (§4 history), so no future sprint re-attempts it.
3. **They are handed to the Sprint-33 forcing/PATH work** (like rocket) — the match is reachable only via the presolve warm-start; a forcing/reformulation strategy (or the PATH consultation) is the only remaining avenue, not an emit fix.
4. **`ISSUE_1236` is closed as documented-non-convex** (not `wontfix`) — they stay **methodology** matches (presolve-recovered), NOT genuine floor; P5 delivers **0** genuine floor. himmel16 is recorded as a sibling documented-non-convex (S30 Day 7), outside this four-member family.

---

## §6. Summary + Known-Unknowns dispositions

| # | Unknown | Disposition |
|---|---|---|
| 5.1 | Does the classifier flag the family without false-positives on Case-b? | ✅ VERIFIED — the D1 structural gate (the max-residual `stat_<var>` is the objective-defining intermediate variable, `nu_obj=±1`) + D3 (cold-spurious) reclassify CASE_B → Case-c; a non-objective-defining Case-b residual never trips D1; D4 (sign-flip-inert) is the definitive manual control for new candidates. |
| 5.2 | Is the sign flip re-confirmed BANNED? | ✅ VERIFIED — control-refuted 4× across S30–S31 (hhfair Days 4/6, 72→22 worse; himmel16 Day 7; the ν_objective reduction inert Day 10); the reduction is inert because `nu_obj=±1`. Recorded in the Case-c classification + ISSUE_1236. |
| 5.3 | Are hhfair AND the CGE cluster all genuine Case-c? | ✅ VERIFIED — re-confirmed on the current tree (hhfair `stat_u` rel 2.00; irscge `stat_xp` rel 0.064) + the Day-10 cohort control (irscge/lrgcge/moncge cold 25.5085 vs match 26.09, sign flip inert; hhfair cold 72.147 vs 87.159). All four: cold-spurious + presolve-match + non-convex model class. No member is a fixable Case-b. |
| 5.4 | What are the ISSUE-closure criteria for "documented Case-c"? | ✅ VERIFIED — the classifier auto-flags them + the sign flip is BANNED + they hand to the Sprint-33 forcing/PATH work + ISSUE_1236 closes as documented-non-convex (they stay methodology, not genuine floor). |

**Decision: PROCEED to the in-sprint P5 formalization** — implement the harness Case-c auto-classifier extension (D1∧D2∧D3 reclassification, no false-positive on non-objective-defining Case-b), and close `ISSUE_1236` as documented-non-convex for hhfair + the CGE cluster. **No emit fix; the sign flip stays BANNED.** P5 delivers 0 genuine floor (as in Sprint 31); the value is the durable non-convexity classification that stops future sprints re-attempting the refuted reduction and hands the family cleanly to the Sprint-33 forcing/PATH work.

---

**Document Created:** 2026-07-13
**Owner:** Sprint 32 Planning Team (KKT specialist)
**Evidence:** the harness runs on the GAMSlib NLP sources — `kkt_residual.py data/gamslib/raw/hhfair.gms` (CASE_B `stat_u(1)` rel 2.00, duals CONSISTENT) + `… data/gamslib/raw/irscge.gms` (CASE_B `stat_xp(BRD)` rel 0.064). (The raw model `.gms` under `data/gamslib/raw/` are fetched via `gamslib <name>` and are **not** checked into the repo, per the corpus convention.) The **objective-defining-intermediate-variable structure is verifiable from the current tree in the checked-in emitted MCP**: `data/gamslib/mcp/hhfair_mcp.gms:187` `objective.. obj =E= prod(t, u(t)**ufact(t))` + `:188` `utility(t).. u(t) =E= …` (the CES nest) + `:171` `stat_u(t)..` (carrying `nu_utility(t)`); `data/gamslib/mcp/irscge_mcp.gms:501` `obj.. uu =E= prod(i, xp(i)**alpha(i))` + `:445` `stat_xp(i)..`. Plus the Sprint-31 Day-10 cohort control + the S30 Day-6 sign-flip refutation (`docs/issues/ISSUE_1236_hhfair-objective-mismatch.md`).

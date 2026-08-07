# Sprint 36 — Property-Fixture & 2-D-Cohort Regression-Harness Catalog + robustlp NA Survey (Prep Task 9)

**Date:** 2026-08-07 · **Owner:** Sprint 36 execution team · **Branch:** `planning/sprint36-task9` · **Scope:** docs/analysis-only (fixture specs + harness invocation + a live robustlp reproduction; no `src/` change — the fixtures/fix land in execution).

**Outcome: the test scaffolding that guards the two shared-`_add_indexed_jacobian_terms` emit fixes (markov, fawley) is catalogued, the shared 2-D-cohort golden-staleness harness is specified, the markov `slow`-test disposition is decided, and the robustlp NA root is reproduced live — correcting the allowlist's characterization (the NA is in the multiplier `.L` warm-start levels, not the Jacobian coefficients) and bounding the de-allowlist fix.** Verifies Unknowns 1.3 (jointly with Task 3), 1.5, 7.3, 7.4, 7.5.

Reference: `MARKOV_OFFDIAGONAL_DESIGN.md` (Task 3), `FAWLEY_DISCRIMINATOR_DESIGN.md` (Task 4), `../SPRINT_35/DAY11_MARKOV_DIAGONAL_LEVER.md`. Tools: `scripts/sprint_audit/check_golden_staleness.py`, `scripts/diagnostics/presolve_divergence_allowlist.txt`, `src/emit/original_symbols.py:152` (`emit_post_assignment_na_cleanup`).

---

## 1. Property-fixture catalog (Unknown 7.4) — mapped to the landing each guards

Two per-fix fixtures, each **fail-before / pass-after** the landing it guards, each **skip-if-absent** on the gitignored raw source:

| fixture | guards | level | asserts | skip-if-absent |
|---|---|---|---|---|
| **`shape_markov_diagonal_kronecker`** | Task 3 (markov `σ=sp` diagonal-Kronecker split, #1110) | fast in-process (AD→KKT emit of the markov `stat_z`, no subprocess) | `stat_z` carries the **direct** `nu_constr(s,i)` diagonal correction term **and** the `sum(...) * nu_constr(s__kkt1,...)` off-diagonal `σ=sp` sum (the `CASE_A` split) — fails on the current `CASE_B` collapsed emit | `pytest.skip` if `data/gamslib/raw/markov.gms` absent (CI lacks raw) |
| **`shape_fawley_2d_second_index`** | Task 4 (fawley constraint-index-diagonal correction, #1111/#1112) | fast in-process (the `_add_indexed_jacobian_terms` second-index branch) | the fawley `stat_bq` second-index transpose term fires **only** when the summed constraint index is absent from the derivative coefficient (the Task-4 discriminator) — disjoint from markov | `pytest.skip` if `data/gamslib/raw/fawley.gms` absent |

**Naming/placement:** both are in-process unit/integration fixtures under `tests/unit/kkt/` (alongside the existing `test_multi_pattern_jacobian.py`, which already unit-tests `_derivative_structure_key`). Each maps 1:1 to its Task-3 / Task-4 landing so a red fixture localizes the regression to one fix.

## 2. The shared 2-D-cohort golden-staleness harness (Unknowns 1.3, 7.4)

**The mechanical leak-freedom gate** for *either* shared-function change is the existing `check_golden_staleness.py` over the 2-D cohort — no new tool needed:

```bash
python scripts/sprint_audit/check_golden_staleness.py \
    --models cesam2,camcge,ps2_f_s,ps2_s,ps3_s_gic,polygon
# exit 0 + "no drift" REQUIRED after either the markov or the fawley change;
# any drift here = a cohort leak (the fawley Day-9 precedent) → revert.
```

- All six cohort goldens are committed and present (`cesam2_mcp.gms`, `camcge_mcp.gms` cold; `ps2_f_s`/`ps2_s`/`ps3_s_gic`/`polygon` `_mcp_presolve.gms`). The harness byte-diffs each emit against its committed golden.
- **Leak-free by construction (Task 3):** Mechanism C is additive and gated on the markov-specific `σ=sp` signature; it does **not** touch the shared `_compute_index_offset_key` matcher, so it cannot re-group cohort entries. Task 4's fawley discriminator is disjoint (fires only when the summed index is absent from the coefficient). The harness is the **empirical confirmation** of that design guarantee — the Day-1 Phase-0 gate.
- **Cost caveat:** the cohort emits are minutes-scale (camcge ~5-min-class; the CGE/2-D models are the slow ones) → this is a **nightly/async or targeted per-PR** step, **not** an inline `make test` step. The fast per-fix fixtures (§1) are the inline guard; this harness is the leak backstop.

## 3. markov `slow`-test disposition (Unknown 1.5)

**Measured:** a markov emit via the subprocess CLI is **~12.4 s** (not minutes-scale — markov is tiny, 2 vars / 3 eqns; the `slow` mark is subprocess-integration convention). The existing guard is `tests/integration/kkt/test_markov_multi_pattern.py::test_markov_stationarity_has_correction_term` (`pytest.mark.slow` + `integration`, **red since birth** — it asserts the `nu_constr(s,i)` correction the fix will emit).

**Decision (disposition option 3, refined):**
1. **Add the fast in-process `shape_markov_diagonal_kronecker` fixture (§1) as the PRIMARY guard** — it runs in `make test` (no subprocess), so it closes the silent-regression window that let the integration test stay red-and-unnoticed since March (a `slow` test doesn't run in the default `make test`).
2. **Flip the integration test red→green** with the Task-3 fix, and **update its assertion to the sharpened `σ=sp` target form** (S35 Follow-up-3) — the current assertion (`nu_constr(s,i)` present + a `sum(...)*nu_constr(s__kkt1,...)` regex) is necessary but not sufficient; tighten it to the exact diagonal-split target so it can't pass on a partially-correct emit.
3. **Keep the integration test `slow`** (subprocess end-to-end guard, CI slow lane) — the fast fixture is what prevents a silent regression, so the 12.4 s subprocess need not enter `make test`.

**Rationale:** the "red since March" failure mode was *a `slow` test as the only guard*. Adding a fast in-process fixture — not merely un-marking the slow test — is the durable fix; the integration test remains as the full-pipeline backstop.

## 4. robustlp NA-coefficient root survey + de-allowlist plan (Unknown 7.3)

**Reproduced live** (`robustlp_mcp_presolve.gms` + raw `$include`, GAMS 54.2.1 demo): **`**** SOLVE … ABORTED, EXECERROR = 84`**, with repeated **`**** Matrix error - illegal level value`** on:
```
lam_socpqcpcons(1..7)   (.LO, .L, .UP = 0, NA, +INF)
piL_y(1..7)             (.LO, .L, .UP = 0, NA, +INF)
```
and Range Statistics **`Matrix [min,max] : [1.000E-02, 4.974E+00]`** (finite) vs **`Bound [min,max] : [NA, NA]`**.

**Corrected root (supersedes the allowlist wording):** the NA is **not** in the Jacobian matrix coefficients (the matrix range is finite) — it is in the **`.L` warm-start *level* values of the emitted multiplier variables** `lam_socpqcpcons(i)` (the SOCP/QCP constraint multipliers) and `piL_y(i)` (variable-`y` lower-bound multipliers). The presolve warm-start transfers the QCP solve's marginals into `<mult>.l`, and those source marginals are **NA** (the QCP returns no finite marginal for those rows/bounds), so the emitted `<mult>.l = <var>.m` sets an **NA level**. GAMS 54's stricter matrix generation rejects an MCP variable with `.L = NA` as EXECERROR-84 "illegal level value" (GAMS 53 tolerated it). The current `presolve_divergence_allowlist.txt` entry ("the Jacobian carries NA coefficients") is imprecise — the defect is an **NA multiplier level**, not an NA coefficient.

**Why the existing #1322 cleanup misses it:** `emit_post_assignment_na_cleanup` (`original_symbols.py:152`) only guards **indexed *parameters* whose assignments contain a division** — it never touches the presolve **multiplier `.L` warm-start** section, which is where robustlp's NA enters.

**Bounded fix + de-allowlist plan:**
1. In the presolve marginal-transfer emit (the "Transfer variable marginals to bound multipliers" section), **NA-guard the multiplier `.L` warm-start** — reuse the #1322 idiom `<mult>.l$(NOT (<mult>.l > -inf and <mult>.l < inf)) = 0;` (or guard the source `<var>.m` at transfer time). One emit-path extension; no change to the Jacobian or the cold emit.
2. Regenerate the robustlp presolve golden; re-run → expect EXECERROR-84 gone (multiplier levels finite).
3. **De-allowlist:** remove `robustlp` from `presolve_divergence_allowlist.txt`; whether robustlp then matches or is a normal mismatch is surfaced by the gate (the allowlist is about *hard divergence*, not match).
4. Guard with a fixture asserting no emitted multiplier `.l` is initialized from a potentially-NA marginal (fail-before / pass-after).

**Scope note:** bounded and self-contained (one presolve emit section), so de-allowlisting robustlp this sprint is feasible. Because korcge (the other allowlist entry, EXECERROR-5, #1439) is a *different* class (embedded-`$include` `.l=0` ordering), this fix does not touch it.

## 5. Genuine-floor recompute + Epic-4 SUMMARY row-36 groundwork (Unknown 7.5)

**Recomputed from the committed DB** (byte-unchanged since the anchor `78ceaead`):
- 142 convex candidates → **Solve 108** / **Match 93 = 63 cold-optimal + 30 presolve** — matches the S34/S35 baseline exactly.
- **markov ∈ the 30-model presolve-match (methodology) partition** (`model_optimal_presolve` + match, `verified_convex`) — confirmed. So the markov +1 lever (methodology→genuine, Task 3) is a **true +1**, not a double-count: fixing markov's cold emit moves it *out* of the methodology partition *into* the genuine floor.
- **Genuine-floor anchor = 75** carries forward (the DB is byte-unchanged, so the S34/S35 hand-partition is intact; the floor advances only via emit-changing cold-matches — the S30 §3 / S31 §3 conditionality lesson).

**SUMMARY row-36 groundwork:** the Epic-4 `SUMMARY.md` genuine-floor ramp (S30 70 → S31 74 → S33 75 → S34 75 → S35 75, modal-flat) anchors the **S36 row at floor 75**, with the **≥76 target** carried by the single tracked emit lever (**markov methodology→genuine**, +1). The row-36 entry is written at S36 close against this anchor — no SUMMARY edit in prep (execution-time update); this note fixes the anchor + the lever so the row is unambiguous.

## 6. Go / No-Go

**GO — the fixture/harness scaffolding + the robustlp fix are catalogued and bounded.** The two per-fix fixtures (§1) map 1:1 to the Task-3/Task-4 landings; the shared cohort golden-staleness harness (§2) is the mechanical leak backstop (leak-free by design, empirically gated Day-1); the markov `slow`-test disposition (§3) closes the silent-regression window with a fast in-process fixture; the robustlp NA root is reproduced + corrected + the de-allowlist fix bounded (§4); the genuine-floor anchor holds at 75 with markov the tracked +1 (§5).

**REPLAN triggers:** the cohort golden-staleness harness (§2) shows a leak after either shared-function change (→ revert, adopt a fallback mechanism per Task 3); the robustlp NA-guard changes the *cold* emit or fails to clear EXECERROR-84 (→ stays allowlisted, re-scope); the markov integration assertion can't be sharpened to the `σ=sp` target without over-fitting (→ keep the fast fixture as the sole guard).

---

**Document Status:** ✅ Complete — Sprint 36 Prep Task 9 (fixture & harness catalog + robustlp NA survey; GO, robustlp root corrected + bounded)
**Last Updated:** 2026-08-07
**Owner:** Sprint 36 Execution Team

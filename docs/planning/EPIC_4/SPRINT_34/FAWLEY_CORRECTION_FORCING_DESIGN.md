# fawley #1111/#1112 — Second-Index Correction + Forcing: Design (Sprint 34 Prep Task 5)

**Created:** 2026-07-19 · **Owner:** Sprint 34 prep (KKT/emit specialist)
**Prep Task:** 5 (Priority 3 foundation) · **Priority:** High
**Day-0 code anchor:** `750803b2` (S33 close) · no `src/` drift since (Task 2 `BASELINE_METRICS.md`)
**Anchors:** `SPRINT_33/DAY4_FAWLEY_CONTROL.md` (the 473→18.468 control, the **H-b confirmed** verdict, §3 the bound-transfer-sign gap) · `SPRINT_33/DAY5_FAWLEY_CLOSE.md` (the constraint-index-diagonal fix-surface refinement, the deferral decision) · `SPRINT_33/FAWLEY_SECOND_INDEX_DESIGN.md` (the emit mechanism, the from-scratch ∂-derivation)

> **Disposition (prep):** this document designs the **split outcome** the Sprint-33 control established — (1) the **genuine constraint-index-diagonal `sameas` correction** (ships for emit-correctness) + (2) the **forcing hand-off** for fawley's **H-b** +Solve (to the P5 `--force` survey). **fawley moves no in-sprint bucket** (H-b: it stays `model_infeasible` and does not cold-match without forcing), so the correction is a *correctness* fix, and the +Solve / floor gain is **contingent on forcing**. **No `src/` change** — the `/tmp` control is the Sprint-34 in-sprint gate.

---

## 1. Day-0 re-confirm (the fingerprint still holds — live)

`scripts/diagnostics/kkt_residual.py data/gamslib/raw/fawley.gms` on the live tree (S33-close `750803b2`, 2026-07-19):

```
verdict: CASE_B  — emit_bug
dual scale: 486
dual transfer: CONSISTENT (max comp infeas 0, max equality residual 1.82e-12 raw)
max-residual row: stat_bq(res-arab-l,fuel-oil)   rel = 0.973  (raw +473)
top: stat_bq(res-arab-l,fuel-oil) 0.973 · (res-arab-h,fuel-oil) 0.973 · (res-brega,fuel-oil) 0.973 · (fuel-imp,fuel-oil) 0.973 · (fuel-equiv,fuel-oil) 0.973
```

Identical to the S33 Day-0/Day-4 fingerprint; the residual concentrates on the **`(*, fuel-oil)`** column (`fuel-oil` is a `cfq`). Day-0 bucket (Task 2 `BASELINE_METRICS.md`): fawley `model_infeasible`, **MS 5**, LP opt **2899.25**. fawley is a **MAXIMIZE** solve (`solve exxon maximizing profit using lp`, `fawley.gms:255`).

---

## 2. The emit mechanism + the constraint-index-diagonal gap (Unknown 3.1)

`bq(c,cf)` (a **2-D** `Positive Variable`, `fawley.gms:201/212`) appears in three equations with two index shapes. The emitted `stat_bq` (`data/gamslib/mcp/fawley_mcp.gms:238`):

```gams
stat_bq(c,cf).. ( sum(cfq__, (((-1)*1$(bposs(cfq__,c)))*nu_mbal(c))$(sameas(cfq__, cf)))
  + sum((cfq__,l,s), ((prop(c,s)*sum(m$(ms(m,s)), char(c,m))*1$(bposs(cf,c))*nu_qsb(cfq__,l,s))$(cfq(cfq__)))$(specs(cfq__,l,s)))
  + sum((cfq__,m), ((((-1)*(char(c,m)*1$(bposs(cf,c))))*nu_pbal(cfq__,m))$(cfq(cfq__)))$(cfm(cfq__,m)))
  - piL_bq(c,cf) )$(cfq(cf)) =E= 0;
```

| Equation | `bq` body ref | summed var index | restriction needed | emitted? |
|---|---|---|---|---|
| `mbal(c)` | `sum(cfq$bposs, bq(c,cfq))` | `bq`'s **second** index `cfq` | `sameas(cfq__, cf)` on the **summed variable index** | **✓** (mbal carries it) |
| `qsb(cfq,l,s)` | `sum(c$bposs, char·bq(c,cfq))` | `bq`'s **first** index `c` | `sameas(cfq__, cf)` on the **constraint's own index** `cfq` (= `bq`'s 2nd index = stat index `cf`) | **✗ (over-sums all `cfq__`)** |
| `pbal(cfq,m)` | `sum(c$bposs, char·bq(c,cfq))` | `bq`'s **first** index `c` | same as qsb — **constraint-index diagonal** | **✗** |

**The Day-5 refinement (the precise gap):** mbal's `sameas` restricts the **summed variable index** to the stat index — the existing diagonal logic handles it. qsb/pbal sum over `bq`'s **first** index `c`; the restriction they need is on the **constraint's own index** `cfq` (which equals `bq`'s second index, = the stat index `cf`) — a **constraint-index diagonal** the current logic does **not** recognize. From a from-scratch ∂-derivation, `∂qsb(cfq,·)/∂bq(c,cf)` and `∂pbal(cfq,·)/∂bq(c,cf)` are nonzero **only when `cfq = cf`**, so the correct terms require `$(sameas(cfq__, cf))`. **The over-sum is the bug** — control-proven (§3): `max|stat_bq|` **473.412 → 18.468**.

---

## 3. H-b confirmed — the +Solve is non-emit (Unknown 3.2)

The Sprint-33 Day-4 control (`SPRINT_33/DAY4_FAWLEY_CONTROL.md`) is **decisive** (repo-root `--nlp-presolve` substrate, `modelstat` asserted):

| Emit state | warm <code>max&#124;stat_bq&#124;</code> | MCP MODEL STATUS | obj |
|---|---|---|---|
| baseline | 473 | MS-5 | 6862 |
| + sameas (qsb/pbal) | **18.468** | **MS-5** | 4399.557 |
| + sameas + all bound-transfer signs | **~0** | **MS-5** | 4399.557 |

- The residual **18.468** after sameas is a **single cell** `stat_bq(cc-dist, fuel-oil)` — an **untransferred bound multiplier**, **not** a second over-sum: `bq(cc-dist,fuel-oil)` at its lower bound, `bq.m = −18.468`, and the residual `= −bq.m` (the min-convention transfer `piL_bq…$(bq.m > 0)` skips `bq.m < 0` on a MAXIMIZE solve). **This cell is the P4 max-convention bound-transfer-sign track's, not P3's sameas gap.**
- **H-b confirmed:** closing the *entire* emit residual (sameas + all bound-transfer signs → warm `max|stat_bq| ~0`) still solves **MS-5 @ 4399.557** — far from the LP optimum **2899.25**, and the objective is *identical* with or without the bound-transfer fix. The divergence is **non-emit** — an LP-convergence/structural issue at fawley's scale (a large degenerate blending LP), separable from the `stat_bq` emit.

**Consequence for `max|stat_bq| → 0`:** the sameas correction (P3) alone gives **473 → 18.468**; reaching **→ 0** needs the P4 bound-transfer fix on the cc-dist cell too. Neither — nor both — reaches MS-1 (H-b). So P3's genuine correction is a **correctness fix that moves no bucket**.

---

## 4. The design — (A) the correction + (B) the forcing hand-off

### 4.A Constraint-index-diagonal `sameas` correction (the genuine emit fix)

**Fix (a Day-0-re-confirm hypothesis, PR24):** extend the diagonal-`sameas` logic in the general indexed cross-term emit so that when a **summed constraint index** (the fresh alias `cfq__`, bound via the constraint's own domain) equals the stationarity variable's index, it emits `$(sameas(cfq__, cf))` — covering the **constraint-index diagonal** shape (qsb/pbal: `bq`'s first index summed, second index = the constraint index = the stat index), **symmetrically** with the variable-index diagonal (mbal). **Fix surface:** `src/kkt/stationarity.py` — the `_build_sameas_guard` (`:4623`) / `_get_or_create_fresh_alias` (`:4496`) restriction path inside `_add_indexed_jacobian_terms` (`:5861`, **~1430 lines**, a dozen issue-specific `sameas` paths #764/#767/#1049/#1110/#1111/#1112/#1224/#1306/#1351). **NOT** the 1-D polygon core `_var_at_two_indices_complement` (`:7291`), which returns `None` unless the variable is 1-D — `bq` is 2-D, so it never fires here.

### 4.B The no-regression gate (Unknown 3.3, correctness half)

- **No mbal-term change** — the mbal `$(sameas(cfq__, cf))` (variable-index diagonal) must be preserved for fawley and every other 2-D indexed-cross-term user.
- **No 1-D-core regression** — polygon/ps2 use `_var_at_two_indices_complement` (a *different* path), so they are structurally untouched.
- `--resolve-changed --since-commit 750803b2` **GO** — fawley the only changed golden; the 2-D indexed-cross-term cohort emit-diffed before the `src/` change.

### 4.C The forcing hand-off (the H-b +Solve)

Because fawley is **H-b**, the +Solve is **not** an emit fix — it hands to the **P5 `--force` survey** (homotopy / multistart / optfile) + the PATH consultation. Boundary: **P3 ships the genuine sameas correction** (correctness + the P7 fixture); **P5 owns fawley's +Solve** (the non-emit MS-5 @ 4399.557 divergence). The P4 bound-transfer-sign track owns the cc-dist residual cell (it closes the warm residual but — for fawley — not the solve).

### 4.D Genuine-floor credit (Unknown 3.3, floor half)

The correction **changes the cold emit** (adds `sameas` to qsb/pbal) → a **genuine** cross-term fix (not methodology). But under **H-b, fawley does not cold-match** (the cold MCP stays MS-5 without a forcing lever), so per the PR25 genuine-floor definition — which credits a *matched* model — **there is no in-sprint genuine-floor gain**. The +1 genuine floor is **contingent on forcing landing the solve** (P5). This corrects the Day-5-prompt premise that the H-b branch yields "+genuine floor": it does **not** for fawley, because it doesn't cold-match. (Ref: `SPRINT_33/DAY5_FAWLEY_CLOSE.md` §1.)

---

## 5. The pre-`src/` `/tmp` control (PR24/PR27 gate) — in-sprint executed, spec here

Run **before** any `src/` change; assert `modelstat`. **In this docs-only prep the criteria are a specification, not an executed result** (the Day-4 control already established the H-b verdict + the 473→18.468 measurement).

1. **Reproduce + localize** — re-emit fawley, patch the qsb/pbal `stat_bq` terms with the constraint-index-diagonal `$(sameas(cfq__, cf))`, eval per `(c,cf)` at the warm LP point (the harness residual mechanism, avoiding the `--nlp-presolve` domain-redef path where present). *Gate:* `max|stat_bq|` 473 → 18.468, the residual localized to the cc-dist/fuel-oil cell (the P4 bound-transfer cell, not a second sameas gap).
2. **Correctness + no-regression** — the sameas restriction fires on **every** qsb/pbal `cfq` (not just fuel-oil); **no mbal-term change**; `--resolve-changed --since-commit 750803b2` GO; the 2-D indexed-cross-term cohort emit-diffed.
3. **Solve disposition (already H-b)** — sameas + the P4 bound-transfer → warm `max|stat_bq| ~0` but MCP still MS-5 @ 4399.557 ⇒ the +Solve hands to P5 forcing (H-b re-confirmed).

**PROCEED (correctness):** the sameas correction ships iff probe 1 reproduces 473→18.468 + probe 2 is clean (no mbal/1-D-core regression). **The +Solve is a P5 forcing hand-off** (H-b). **REPLAN** iff the generalization leaks onto the mbal / first-index shape or regresses the 1-D core.

---

## 6. Sizing + REPLAN exit + the P7 fixture (Unknown 3.4)

**12–18 h:**
- `/tmp` reproduce + per-column localization + the constraint-index-diagonal prototype + the no-regression check (~4–6 h) — the Phase-0 control.
- Extend the diagonal-`sameas` logic in `_add_indexed_jacobian_terms` (`_build_sameas_guard` / `_get_or_create_fresh_alias` path) to the constraint-index-diagonal (qsb/pbal) shape (~5–8 h).
- No-regression (`--resolve-changed`, the 2-D indexed-cross-term emit-diff) + determinism ×3 + a **fawley 2-D second-index regression fixture** (~3–4 h) — the P7 `shape` fixture, fail-before/pass-after, following the S33 `tests/integration/emit/test_sample_pruned_var_l_init.py` pattern (raw-file emit + skip-if-absent; asserts the `$(sameas(cfq__,cf))` guard present on the qsb/pbal terms).

**Gate-leak REPLAN exit:** REPLAN iff the generalization (a) leaks onto the mbal / variable-index-diagonal shape or regresses the 1-D polygon core (a correctness regression on already-passing models). The de-risked hand-off is this document + the Day-4 per-column localization.

**Split-outcome summary:** P3 ships a **genuine correctness fix** (no in-sprint bucket); fawley's **+Solve is a P5 forcing hand-off** (H-b); the **cc-dist residual cell is P4's** (the max-convention bound-transfer-sign track). The +1 genuine floor is **contingent** on forcing landing the solve.

---

## 7. Outcome for the Known Unknowns

| Unknown | Verdict | Finding |
|---|---|---|
| **3.1** | ✅ **VERIFIED** | The qsb/pbal `sameas` gap is a **constraint-index diagonal** (the summed constraint index `cfq` = `bq`'s 2nd index = the stat index `cf`), distinct from mbal's variable-index diagonal. Fix surface = the general `sameas`-guard path (`_build_sameas_guard`/`_get_or_create_fresh_alias` in `_add_indexed_jacobian_terms`, `:5861`, ~1430 lines), **not** the 1-D core `_var_at_two_indices_complement` (`:7291`; never fires for 2-D `bq`). The correction gives `max|stat_bq|` **473 → 18.468** (control-proven); **→ 0 also needs the P4 bound-transfer fix** on the cc-dist cell. |
| **3.2** | ✅ **VERIFIED** | **H-b confirmed** (Day-4): sameas + all bound-transfer signs → warm `max|stat_bq| ~0` but the MCP still solves **MS-5 @ 4399.557** (LP opt 2899.25), objective identical with/without the bound-transfer fix. The divergence is **non-emit** (LP-convergence at fawley's scale) → the +Solve hands to P5 forcing. |
| **3.3** | ✅ **VERIFIED** | The correction changes the cold emit → **genuine** (not methodology). But under H-b fawley **does not cold-match** (stays MS-5 without forcing), so the PR25 floor — which credits a matched model — gives **no in-sprint floor gain**; the +1 genuine floor is **contingent on forcing** (P5). Corrects the Day-5-prompt "+genuine floor" premise (it doesn't hold for fawley). |
| **3.4** | ✅ **VERIFIED** | Sized **12–18 h** + the gate-leak REPLAN exit. The P7 fawley 2-D second-index fixture (fail-before/pass-after, `test_sample_pruned_var_l_init.py` pattern) lands **only once** the correction lands. The split outcome: correctness ships (no bucket); +Solve → P5 forcing; the cc-dist cell → P4. |

---
**Document Status:** ✅ Complete — Sprint 34 Prep Task 5 (design; no `src/`)
**Last Updated:** 2026-07-19 · **Owner:** Sprint 34 prep (KKT/emit specialist)

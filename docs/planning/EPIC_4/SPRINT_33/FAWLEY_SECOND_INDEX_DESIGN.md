# fawley #1111/#1112 — Second-Index Cross-Term Generalization: Design

**Prep Task:** 5 (Priority 3 foundation) · **Date:** 2026-07-16 · **Owner:** Sprint 33 prep (KKT/emit specialist)
**Status:** design complete — **PROCEED (conditional)**. The primary emit bug (qsb/pbal miss the `sameas` restriction) is a real, designable fix that closed 96% in the banked control; the residual 18.47 + the MS-5 persistence are a **gate-leak / LP-convergence risk** (the +1 Solve is conditional). **Fix-surface refinement:** the fix is **not** the 1-D polygon core (`bq` is 2-D) — it is the general indexed cross-term `sameas`-guard path.

> **PR24 discipline:** every fix surface below is a hypothesis for the in-sprint `/tmp` control to validate **before** any `src/` change. This document sizes and de-risks P3.

---

## 1. Day-0 re-confirm

`kkt_residual.py data/gamslib/raw/fawley.gms` on the current tree (Sprint 32 close `ee51ed9e`):

```
dual transfer: CONSISTENT (max comp infeas 0.00e+00 rel, max equality residual 1.82e-12 raw)
verdict: CASE_B  — emit_bug
max-residual row: stat_bq(res-arab-l,fuel-oil)  rel = 9.73e-01  (raw +4.73e+02)
  stat_bq(res-arab-l,fuel-oil) rel 0.973 · stat_bq(res-arab-h,fuel-oil) 0.973 · stat_bq(res-brega,fuel-oil) 0.973 · stat_bq(fuel-imp,fuel-oil) 0.973 · stat_bq(fuel-equiv,fuel-oil) 0.973
```

CASE_B holds; the dual transfer is CONSISTENT; the residual concentrates on the **`(*, fuel-oil)`** column (`fuel-oil` is a `cfq`). Reproduces the Sprint-32 Day-11 `P6_BACKLOG_RETRIAGE.md` §2 control. The banked control's sameas patch measured **`max|stat_bq|` 473.4 → 18.468 (96% closed)** but the patched MCP still solves **MS-5 @ 5739** (not the LP optimum **2899.25**).

> **Re-measurement note:** a fresh GAMS re-run of the sameas patch was attempted on a `--nlp-presolve` emit but that variant has pre-existing `Domain list redefined` compile errors (the known `$onMulti` re-declaration issue, unrelated to the patch). The committed golden `data/gamslib/mcp/fawley_mcp.gms` compiles clean and the harness re-confirms the **473** baseline byte-identically; the banked **473 → 18.47** patch measurement therefore stands (byte-identical model + emit). The exact per-column localization of the 18.47 is an in-sprint `/tmp` control step (§5).

## 2. The emit mechanism — mbal has `sameas`, qsb/pbal don't

`bq(c,cf)` (a **2-D** `Positive Variable`, `1000 tons`) appears in three equations, with two different index shapes:

| Equation | body reference | shape | `bq` index that = the equation index |
|---|---|---|---|
| `mbal(c)` | `sum(cfq$bposs(cfq,c), bq(c,cfq))` | `bq`'s **first** index `c` = the equation index; **second** index `cfq` is **summed** | first (`c`) |
| `qsb(cfq,l,s)` | `sum(c$bposs(cfq,c), … char(c,m)·bq(c,cfq))` | `bq`'s **second** index `cfq` = the equation's **first** index; **first** index `c` is **summed** | second (`cfq`) |
| `pbal(cfq,m)` | `sum(c$bposs(cfq,c), char(c,m)·bq(c,cfq))` | same as qsb — second index `cfq` = equation's first index | second (`cfq`) |

The emitted `stat_bq` (verbatim from `data/gamslib/mcp/fawley_mcp.gms:238`):
```gams
stat_bq(c,cf).. (sum(cfq__, (((-1) * 1$(bposs(cfq__,c))) * nu_mbal(c))$(sameas(cfq__, cf))) + sum((cfq__,l,s), ((prop(c,s) * sum(m$(ms(m,s)), char(c,m)) * 1$(bposs(cf,c)) * nu_qsb(cfq__,l,s))$(cfq(cfq__)))$(specs(cfq__,l,s))) + sum((cfq__,m), ((((-1) * (char(c,m) * 1$(bposs(cf,c)))) * nu_pbal(cfq__,m))$(cfq(cfq__)))$(cfm(cfq__,m))) - piL_bq(c,cf))$(cfq(cf)) =E= 0;
```

(The three `sum(...)` terms are, in order, the **mbal**, **qsb**, and **pbal** cross-terms, then the `piL_bq` bound term.)

The **mbal** cross-term carries `$(sameas(cfq__, cf))` (the summed alias restricted to the stat index); the **qsb / pbal** cross-terms sum `nu_qsb(cfq__,l,s)` / `nu_pbal(cfq__,m)` over **all** `cfq__` (guarded only by `$(cfq(cfq__))` membership, not the diagonal restriction). From a from-scratch ∂-derivation: `∂qsb(cfq,l,s)/∂bq(c,cf)` and `∂pbal(cfq,m)/∂bq(c,cf)` are **nonzero only when `cfq = cf`**, so the correct terms require the same `$(sameas(cfq__, cf))` the mbal term has. **The over-sum is the bug** (confirmed: the banked sameas patch closes 96%).

## 3. Fix-surface refinement — the general `sameas`-guard path, NOT the 1-D polygon core

The landed #1111/#1112 core `_var_at_two_indices_complement` (`src/kkt/stationarity.py:7291`) **cannot** be the fix: it returns `None` unless `len(var_domain) == 1` (a **1-D** variable at both positions of a 2-D constraint — polygon's `r(i)`). fawley's `bq(c,cf)` is **2-D**, so the polygon core never fires here.

The `sameas(cfq__, cf)` on the mbal term instead comes from the **general indexed cross-term emit** — the fresh-alias generation (`_get_or_create_fresh_alias`, `stationarity.py:4496`) + the diagonal `sameas`-restriction logic (`_build_sameas_guard`, `:4623`; wired via `_add_indexed_jacobian_terms`). That logic adds the `sameas(alias, stat_idx)` restriction for the **variable's-first-index = equation-index, second-index-summed** shape (mbal) but **not** for the **variable's-second-index = equation's-first-index** shape (qsb/pbal) — the summed constraint index `cfq` that must equal the variable's second index `cf` is not recognized as a diagonal restriction.

**Fix (hypothesis):** extend the diagonal-`sameas` logic in the indexed cross-term emit so that when a summed constraint index (the fresh alias `cfq__`) is bound (via the constraint's own domain) to a variable index that equals the stationarity variable's index, it emits `$(sameas(cfq__, cf))` — covering the **variable's-second-index-summed** shape (qsb/pbal), symmetrically with the first-index shape (mbal). Fix surface: `src/kkt/stationarity.py` — the `_build_sameas_guard` / `_get_or_create_fresh_alias` restriction path in `_add_indexed_jacobian_terms` (NOT `_var_at_two_indices_complement`).

## 4. The residual 18.47 — diagnosis

After the sameas patch restricts all three cross-terms to `cfq__ = cf`, a from-scratch ∂-derivation confirms **each of the three cross-terms is individually correct** (labels, signs, coefficients, conditions match `mbal`/`qsb`/`pbal`). So the 18.47 is **not** a fourth over-summed term. Two candidates remain (the in-sprint `/tmp` per-column decomposition discriminates):

- **H-a (second gate-leak):** a residual at a **different `cfq` column** (not `fuel-oil`) of the same second-index shape that the single-column-dominant patch under-closes — i.e. the generalization must fire on **every** `cfq`, not just the dominant one. If so, the full gate generalization (§3) closes it (`max|stat_bq| → 0`).
- **H-b (non-emit LP-convergence):** the patched MCP still solves **MS-5 @ 5739** — a *large* jump from the LP optimum 2899.25, not a near-optimal point with a tiny residual. This suggests an **LP-convergence component separable from the `stat_bq` emit** (fawley is a large degenerate blending LP; PATH may struggle from the cold/warm point even with `stat_bq` near-closed). If H-b dominates, closing the emit residual does **not** by itself reach MS-1 → the +1 Solve needs a forcing/warm-start lever, not just the emit fix.

**Working diagnosis:** the primary bug is the qsb/pbal `sameas` gap (H-a mechanism — a genuine emit fix); but the MS-5 persistence flags a likely H-b component, so **closing 18.47 may not alone reach MS-1** — the "#1111/#1112 gate leaks" REPLAN risk, confirmed as a live concern (Unknown 3.2).

## 5. The pre-`src/` `/tmp` control + no-regression (PR24/PR27)

Run **before** any `src/` change; assert `modelstat`:
1. **Reproduce + localize.** Re-emit fawley, patch the qsb/pbal `stat_bq` terms with `$(sameas(cfq__, cf))`, and eval the residual per `(c,cf)` at the warm LP point (via the harness residual mechanism, avoiding the `--nlp-presolve` domain-redef path). **Gate:** confirm `max|stat_bq|` 473 → ~18, and **localize the 18.47 by column** — does it sit on a *second* `cfq` (H-a) or is it distributed/near-zero with MS-5 driven elsewhere (H-b)?
2. **Full gate generalization.** Prototype the §3 extension so **every** second-index `cfq` gets the sameas restriction. **Gate:** `max|stat_bq| → 0` (not 96%) at the warm point, then presolve to **MS-1 at 2899.25** (`modelstat=1` asserted). If it reaches MS-1 → H-a; if `max|stat_bq| → 0` but still MS-5 → H-b (the emit is correct; the divergence is non-emit → forcing hand-off).
3. **No-regression.** `--resolve-changed --since-commit ee51ed9e` GO — **`ee51ed9e` is the Day-0 code anchor (the Sprint 32 close), the correct emit-diff baseline; `4cbf8bff` is the DB byte-anchor (Sprint 31 close), a different purpose** — — no polygon/ps2 move (they use the 1-D core, a *different* path, so naturally safe) and **no mbal-term change** for fawley or any other 2-D indexed-cross-term user (the mbal sameas must be preserved). Spot re-emit + emit-diff before the src change.

**PROCEED** iff probe 2 reaches `max|stat_bq| → 0` **and** MS-1 at 2899.25 and probe 3 is clean; **PROCEED-as-forcing** if `max|stat_bq| → 0` but MS-5 persists (emit fix ships as a genuine cross-term correction; the +Solve becomes a forcing hand-off); **REPLAN** if the generalization leaks onto mbal / regresses the 1-D core.

## 6. Sizing + REPLAN exit (Unknown 3.4)

**12–18 h:**
- `/tmp` reproduce + per-column localization + the full-generalization prototype + the MS-1/MS-5 discrimination (~4–6 h) — the Phase-0 control.
- Extend the diagonal-`sameas` logic in `_add_indexed_jacobian_terms` (`_build_sameas_guard` / `_get_or_create_fresh_alias` path) to the variable's-second-index-summed shape (~5–8 h).
- No-regression (`--resolve-changed`, emit-diff for the 2-D indexed-cross-term cohort) + determinism ×3 + a fawley second-index regression fixture (~3–4 h).

**Cold-match / genuine floor (Unknown 3.4):** the fix **changes the cold emit** (adds the sameas to qsb/pbal) → a **genuine** cross-term correction (not methodology). fawley cold-matches (+1 genuine floor + 1 Solve) **iff** the emit fix reaches MS-1 (H-a). If H-b dominates (MS-5 persists), the emit fix is still genuine but fawley needs a forcing lever to solve → **+1 Solve conditional**, +1 genuine floor conditional on the cold match.

**Gate-leak REPLAN exit:** REPLAN iff (a) the generalization leaks onto the mbal / first-index shape or regresses the 1-D polygon core (correctness risk), or (b) `max|stat_bq| → 0` yet the MCP stays MS-5 (H-b — the divergence is non-emit) → the emit fix ships as a genuine cross-term correction and fawley's +Solve hands off to the P5 forcing survey. The de-risked hand-off is this document + the per-column localization.

## 7. Outcome for the Known Unknowns

| Unknown | Verdict | Finding |
|---|---|---|
| **3.1** | ✅ VERIFIED | The second-index gate generalizes — but the fix surface is the **general indexed cross-term `sameas`-guard path** (`_build_sameas_guard` / `_get_or_create_fresh_alias` in `_add_indexed_jacobian_terms`), **not** the 1-D polygon core `_var_at_two_indices_complement` (which never fires for the 2-D `bq`). The qsb/pbal cross-terms need the same `$(sameas(cfq__, cf))` the mbal term has; a from-scratch ∂-derivation confirms this. |
| **3.2** | ✅ VERIFIED (design-level) | The residual 18.47 is **not** a fourth over-sum (the three cross-terms are individually correct post-sameas). It is either a second-column gate-leak (H-a) or a non-emit LP-convergence (H-b); the banked patched MCP's **MS-5 @ 5739** persistence flags a likely H-b component → **closing 18.47 may not alone reach MS-1**. The in-sprint `/tmp` per-column decomposition (§5) discriminates; not fully closed in this docs-only prep. |
| **3.3** | ✅ VERIFIED | No-regression is structurally favorable: polygon/ps2 use the **1-D** core (a different path, untouched); the risk is perturbing the **mbal / first-index** sameas on the same 2-D path — guarded by the `--resolve-changed` GO + the 2-D indexed-cross-term emit-diff (§5 probe 3). |
| **3.4** | ✅ VERIFIED | Sized **12–18 h**. The fix changes the cold emit (genuine, not methodology); fawley cold-matches (+1 Solve, +1 genuine floor) **iff** the emit fix reaches MS-1 (H-a) — **conditional** on the H-a/H-b discrimination (if H-b, +Solve hands off to forcing). |

---
**Document Created:** 2026-07-16 · **Owner:** Sprint 33 prep (KKT/emit specialist)

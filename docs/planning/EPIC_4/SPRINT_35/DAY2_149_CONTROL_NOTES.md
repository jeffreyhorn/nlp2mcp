# Sprint 35 — Day 2 Control Notes: `$149` `/tmp` product-rule fix (the sole live REPLAN gate)

**Day:** 2 (Priority 4, `$149` — the sprint's only live REPLAN gate) · **Date:** 2026-07-25 · **Owner:** Sprint 35 execution
**Day-0 code anchor:** `78ceaead` · **Branch:** `planning/sprint35-day2-p4-149-control` (docs/control-only — the `src/` prototype was reverted)
**Scope:** PR27 `/tmp` control BEFORE any `src/` change. Prototype tested, evidence captured, `src/` reverted. No `src/` ships in Day 2.

## ✅ VERDICT: PROCEED

The `$149` `_diff_prod` fix is **surgical**: it drives ganges's 9 `$149` → 0 with the correct hand-derived cross-term, and leaves the two most-sensitive prod-in-stationarity regression models (lmp2, camcge) **byte-identical**, with 767 AD/emit unit+e2e tests green. Day 3 re-applies this fix onto the Day-1 branch (`$141`+`$145`) as the all-three-roots landing.

---

## 1. Mechanism (confirmed live, not inferred)

The real emit differentiates `les(i,r)` w.r.t. a **concrete** column (e.g. `pc("agricult")`), via `compute_constraint_jacobian` → `differentiate_expr(les, "pc", ("agricult",))` → `_diff_prod` on `prod(j, (pc(j)/pc00(j))**ac(j,r))`. Then, in `_diff_prod`:

1. `_sum_should_collapse(("j",), ("agricult",))` fires — `"agricult"` **is** a concrete member of set `j` (`j` aliases `i`) — so `effective_wrt` is substituted to the prod's symbolic bound `("j",)`.
2. Body differentiated w.r.t. `effective_wrt=("j",)` → nonzero power-rule derivative referencing `j`.
3. `symbolic_name_match` (`effective_wrt == expr.index_sets`, `j == j`) → the **collapse** branch returns `prod(j,…) * (f'(j)/f(j))` — the factor references the prod's bound `j`.
4. The emitter's `collect_index_aliases` (`src/emit/expr_to_gams.py:757`) renames a `Prod` bound **only** on collision with the equation domain or an *enclosing* binder — **never for a sibling multiplicative factor**. ganges's equation is `stat_pc(i)` (domain `i`), and `j ≠ i`, so `j` is **not** renamed → the sibling `j` emits **free** → GAMS **`$149`** ("uncontrolled set entered as constant"), ×9.

**Why camcge (and the 18 others) compile:** they are the **name-match** case — `prod(i, cd(i)**cles(i))` differentiated w.r.t. `cd("ag-subsist")` → `effective_wrt=("i",)`, prod bound `i` **==** the equation domain `i` (`stat_cd(i)`), so aliasing renames the prod's `i → i__` and the sibling factor's `i` correctly references the equation's free index. ganges is the **cross-index** case (prod over `j`, differentiate w.r.t. `pc(i)`, `j ≠ i`) that the aliasing contract does not cover — exactly Task 4 §3.

Minimal faithful repro (hand-built ModelIR: alias `j→i`, set `i` with concrete members, var `pc`, params `pc00`/`ac`) reproduces chunk 2 verbatim: `d(prod)/d(pc("agricult"))` → `prod(j,…) * (pc(j)/pc00(j))**ac(j,r) * … / (pc(j)/pc00(j))**ac(j,r)` with free `j`.

## 2. The fix (AD layer — Task 4 option (a))

In `_diff_prod`'s `symbolic_name_match` collapse branch (`src/ad/derivative_rules.py:~3410`), rebind the collapsed `log_term`'s prod-dummy index → the **original** wrt index when `_sum_should_collapse` substituted a concrete wrt (i.e. `effective_wrt != wrt_indices`). The factor then references the *differentiated column* (`pc("agricult")` → re-symbolized by the stationarity assembly to the equation's free `i`), not the prod's free dummy:

```python
        if (
            wrt_indices is not None
            and effective_wrt is not None
            and len(effective_wrt) == len(wrt_indices)
            and effective_wrt != wrt_indices
        ):
            rebind = {
                e: w
                for e, w in zip(effective_wrt, wrt_indices, strict=True)
                if isinstance(e, str) and isinstance(w, str) and e != w
            }
            if rebind:
                log_term = _apply_index_substitution(log_term, rebind)
        return Binary("*", expr, log_term)
```

(placed just before the existing `return Binary("*", expr, log_term)`; full patch in `/tmp/s35_day2_149_fix.patch`, 39 lines, one file). Uses the existing `_apply_index_substitution` helper. **Conservative:** it fires only for the exact concrete-collapse case (`len(effective_wrt) == len(wrt_indices)` and they differ); the partial-index `#724` path and the pure-symbolic name-match path are untouched. For the name-match case (camcge) the rebind maps `i → "ag-subsist"`, which re-symbolizes back to `i` — value **and bytes** unchanged (verified below).

## 3. Evidence (all three gate conditions MET)

**(a) Cross-term correct** — the emitted `stat_pc(i)` derivative factor (with the fix) is:
```
prod(j, (pc(j)/pc00(j))**ac(j,r)) * (pc(i)/pc00(i))**ac(i,r) * ac(i,r)/(pc(i)/pc00(i)) * 1/pc00(i)**1 / (pc(i)/pc00(i))**ac(i,r)
```
The prod keeps its scoped `j`; the derivative factor is bound to the stationarity index **`i`** — Task 4's **form 2** (`P · f'(i)/f(i)`), which reduces to the hand-derived **form 1** `P · ac(i,r)/pc(i)`. **No free `j`.**

**(b) `$149` eliminated** — ganges compiled (`gams a=c`) with the fix: `$149` **9 → 0** (and the `$300` overflow marker is gone too — the malformed `**1/` chain compiles now that it is index-bound, per Task 4 §5.2). Residual on this `$149`-only branch: `$141`×15 + `$145`×3 + `$257`×1 (cascade) — the `$141`/`$145` roots are the Day-1 fixes, correctly **absent** here (this branch is `$149`-only from `main`).

**(c) Regression byte-identical** — re-emitted the two most-sensitive prod-in-stationarity models:
- **lmp2** (the `prod(p, y(p))` symmetric-optimum case the #1330 comment calls out as most sensitive): **BYTE-IDENTICAL** ✓
- **camcge** (the #1330 collapsed-form motivator): **BYTE-IDENTICAL** ✓

**Unit/e2e** — 767 passed / 0 failed across the AD prod/derivative/#1330 + emit + `test_gamslib_match` selection (incl. cesam2). The warnings observed are pre-existing (cesam2 set-membership), unrelated to the fix.

## 4. Caveats + Day-3 landing requirements

- **⚠ `ac(i+2,r)` secondary artifact remains** (Task 4 §5.2) — the first `sum(r,…)` term carries a spurious `+2` index offset (`ac(i+2,r)`) that this `$149` fix does **not** touch (it is a separate latent index-offset misattribution; it compiles, so it is not a `$149`). It is a **value-correctness risk to the Day-4 cold solve/match** (Unknown 4.4): ganges may compile-and-solve but not *match* if the stationarity value is wrong. Flag for a Day-3 look; the solve/match verdict is Day 4.
- **Full 18-model regression is the Day-3 gate.** Day 2 byte-checked the **2 most sensitive** (lmp2, camcge). The Day-3 landing must byte-compare **all 18** prod-in-stationarity models (`agreste camcge dyncge etamac hhfair hhmax irscge korcge lmp2 lrgcge moncge prolog qdemo7 quocge splcge stdcge twocge weapons`) + `--resolve-changed --since-commit 78ceaead` GO.
- **`/tmp`-only.** The `src/` prototype was reverted; this branch is docs/control-only. Day 3 re-applies the §2 patch onto `planning/sprint35-day1-p4-banked-roots` (which carries `$141`+`$145`), regenerates the goldens once (now compiling), and promotes that draft to the real all-three-roots PR.

## 5. Next (Day 3)

Land `$149` (§2 patch) onto the Day-1 branch → per-model emit→compile→count (ganges AND gangesx, `$NNN` → assert the `$149` gone; `$141`/`$145` already gone from Day 1) → regenerate goldens (scoped `--fix`) + determinism ×3 → full 18-model regression byte-check + `--resolve-changed` GO. Then Day 4: per-model cold+presolve solve/match (Unknown 4.4), watching the `ac(i+2,r)` value risk.

---

**Document Status:** ✅ Complete — Sprint 35 Day 2 (PROCEED)
**Last Updated:** 2026-07-25
**Owner:** Sprint 35 Execution Team

# Sprint 35 — Day 3 (P4): BANK — ganges/gangesx recovery is a ≥5-blocker cascade

**Day:** 3 (Priority 4 — `$149` land + per-model residual count) · **Date:** 2026-07-25 · **Owner:** Sprint 35 execution
**Branch:** `planning/sprint35-day1-p4-banked-roots` (now docs-only — **all `src/` reverted, nothing ships**)
**Outcome: BANK all three roots + the correct `$149` fix.** ganges/gangesx do **not** recover; the per-model protocol surfaced a 4th root (`$66`, cold) and a 5th blocker (`rPower` embedded-NLP `$onMultiR` divergence, presolve) that neither prep nor the Day-2 control anticipated. Per **"no bucket → no `src/`"**, the fix is banked and P4's budget reallocates to P6/P7.

---

## 1. What Day 3 did, and what it found

Applied the `$149` `_diff_prod` fix (Day-2 control, PROCEED) onto the Day-1 branch (which carried `$141`+`$145`) → all three roots present → ran the **per-model protocol** (emit → `gams a=c` → count `$NNN`, ganges AND gangesx independently, never inferred). The protocol did exactly its job — it caught what prep missed.

### The `$149` fix is correct and surgical (confirmed corpus-wide)

Beyond the Day-2 lmp2/camcge byte-check, the **full golden-staleness scan** (163 in-scope goldens) confirmed the only verified drifts are **gangesx** (−925 bytes, a beneficiary) and **prolog** (−3 bytes, the `$141` collateral). **None** of the 17 non-collateral prod-in-stationarity models drifted. So `$149` is a genuine, surgical emit-correctness fix — it is banked as *correct-but-no-bucket*, not as wrong.

### The blocker cascade — each root masked the next (the S34 Day-11 lesson, ×2)

| # | Blocker | GAMS | Path | Cause | Status |
|---|---|---|---|---|---|
| 1 | `$141` ×15 | Symbol declared, no values | cold + presolve | NA-cleanup guard over presolve-gated `.l`-calibration params | ✅ fixed (Day 1) — **banked** |
| 2 | `$145` ×3 | Set identifier expected | cold + presolve | NA-cleanup over a universal-set (`*`-domain) param | ✅ fixed (Day 1) — **banked** |
| 3 | `$149` ×9 | Uncontrolled set as constant | cold + presolve | cross-index product-rule leaks the prod bound `j` free (Task 4) | ✅ fixed (Day 2/3, **correct + surgical**) — **banked** |
| **4** | **`$66` ×1** | Symbol used, not assigned | **cold** | calibration params (`adst`, `aid`, `aex`, `deltax`, `as`, `deltas`, `av`, `deltav`) are presolve-gated → **unassigned in the cold MCP**, but referenced in `stat_ax`/`stat_invtot`/… | ❌ **4th root — prep missed** |
| **5** | **`rPower`** | `x**y, x=0, y<0` FUNC DOMAIN | **presolve** | the presolve emit `$include`s the source under `$onMultiR`; the re-included NLP `ganges0` hits a power-domain error at generation — **the embedded-NLP-diverges-from-standalone bug class** (#1378 launch / #1424 camshape family) | ❌ **5th blocker — separate deep bug class** |

**Prep (Tasks 4/5) found 3 roots; there are at least 5**, and the last two are on *different* paths (cold vs presolve) and *different* bug classes.

## 2. Why neither path recovers — the decisive evidence

- **Cold** (all three roots): `gams a=c` → `$141`/`$145`/`$149` = **0**, but **`$66`×1** (2 errors incl. cascade `$257`). The calibration params are structurally unavailable in the cold MCP (they are `.l`-calibration, assigned only under the warm-start). Both ganges and gangesx: identical.
- **Presolve** (all three roots): the emit **compiles clean** (0 errors — recompiled from the repo root, where `$include "data/gamslib/raw/ganges.gms"` resolves; the earlier 151-error result was a `/tmp` co-location artifact). **But solving it aborts at the NLP warm-start:** `*** Error at line 2216: rPower: FUNC DOMAIN: x**y, x=0, y<0` while *generating* the re-included `ganges0` NLP. The **raw** `ganges.gms` NLP solves fine standalone (MODEL STATUS **2 Locally Optimal**, objective **6395.5444**, 0 infeasible) — so the failure is introduced purely by the `$onMultiR` re-inclusion, i.e. the embedded-NLP divergence bug class, **not** by any P4 fix (which is MCP-side, after the NLP solve).
- **The pipeline interaction that seals it:** `run_full_test.py` triggers the presolve retry **only** on a cold solve returning STATUS 5 or a spurious-KKT mismatch — **not** on a cold `path_syntax_error` (compile failure). So even a `$66` cold fix could not recover ganges: cold → (best case) STATUS 5 → retry → **presolve `rPower` fails anyway**. Neither path reaches a matching solve.

## 3. The bank decision (per "no bucket → no `src/`")

The three-root fix moves **no bucket** — ganges/gangesx stay `path_syntax_error` on cold (`$66`) and cannot be reached on presolve (`rPower`). Shipping it would churn ganges/gangesx/prolog goldens for **0 bucket** — exactly what the rule forbids (the S34-banked precedent). So **all `src/` is reverted**; this branch is docs-only. P4's 14–20 h reallocates to **P6** (the second bucket source) + P7. This is the bimodal projection's **"P4 REPLANs → flat"** branch (Task 11): headline Solve/Match/floor hold at 108/93/75 unless P6 recovers a residual-cohort model.

**The firm product (zero broken code):**
- **`$149` is a verified, surgical emit-correctness fix** — banked, ready to ship the day ganges recovery is pursued. The complete patch is §5 below.
- **`$141`/`$145` are verified** (Day 1: 15→0, 3→0) — banked, in git history (`a8ff626c`) + `DAY1_PROGRESS_NOTES.md`.
- **ganges/gangesx are now fully characterized** — the ≥5-blocker cascade, each verified live — a precise recovery spec replacing prep's "3 roots."

## 4. Sprint-36 carryforward — ganges/gangesx dedicated recovery

Recovery needs, in order, a dedicated effort spanning **three** layers (well beyond a bounded in-sprint attempt):
1. **`$141`/`$145`/`$149`** — the three verified emit fixes (§5 + `DAY1`/`DAY2` notes). Re-apply as the foundation. **Correctness fix on re-apply (PR #1617 review):** the Day-1 `$141` change introduced a new `_expr_contains_varref_attr` helper that only traverses `Expr.children()` — it **misses attributed `VarRef`s inside index expressions** (e.g. an `.l` ref inside an `IndexOffset`), so `_param_assignment_references_varref_attr` could return `False` when it should be `True` and re-emit the `$141` guard. The module **already has** the correct helper `_expr_contains_varref_attribute` (`src/emit/original_symbols.py:1340`), which explicitly traverses `VarRef`/`ParamRef`/`MultiplierRef` indices. **Re-apply must delegate to `_expr_contains_varref_attribute` (or match its traversal) instead of the divergent `_expr_contains_varref_attr`.**
2. **`$66` (cold)** — define the presolve-gated calibration params in the cold MCP (a default cold assignment, e.g. `param(domain) = 0`, so the stationarity + cleanup stop erroring and cold at least compiles → solves → could trigger the retry). Emit-scoped; collateral-golden effects; the pre-existing `ac(i+2,r)` value artifact (Task 4 §5.2) is a further *match*-correctness risk.
3. **`rPower` (presolve `$onMultiR` divergence)** — the embedded-NLP-diverges-from-standalone bug class (#1378/#1424 family): the re-included `ganges0` NLP hits a power-domain error the standalone NLP does not. This is the **gating blocker for the presolve recovery path** and a separate, known-hard investigation.
4. **Pipeline (optional):** consider triggering the presolve retry on a cold `path_syntax_error` (a `run_full_test.py` change), so a clean presolve emit is reachable when cold cannot compile — but only *after* (3) is fixed, else the retry still fails.

**Bundle with the existing Sprint-36 package** (rocket PATH consultation + mine primal-degenerate-LP + fawley `--force` survey).

## 5. Banked `$149` patch (`src/ad/derivative_rules.py:_diff_prod`)

Insert just before the existing `return Binary("*", expr, log_term)` in the `symbolic_name_match` collapse branch (Task 4 option a; verified correct + surgical Day 2/3):

```python
        # Sprint 35 / #1443 ($149): rebind the collapsed factor's prod-dummy
        # index to the original wrt index when `_sum_should_collapse`
        # substituted a concrete wrt to the prod's symbolic bound
        # (effective_wrt != wrt_indices). The log_term references the prod's
        # bound index; when that bound differs from the equation's free index
        # (the CROSS-index case: prod over `j`, differentiate w.r.t. `pc(i)`,
        # `j != i`), the emitter's aliasing will NOT rename it — it renames a
        # Prod bound only on collision with the equation domain or an enclosing
        # binder, never for a sibling multiplicative factor — so `j` leaks free
        # → GAMS $149. Rebinding to the original (concrete) wrt index makes the
        # factor reference the differentiated column, which the stationarity
        # re-symbolization maps to the equation's free index (yielding the
        # correct `f'(i)/f(i)`). For the name-match case (prod bound already ==
        # equation index, e.g. camcge's `prod(i, cd(i)**cles(i))`) the value is
        # unchanged. Skip when nothing was substituted.
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
```

Evidence it is correct + surgical: ganges `$149` 9→0 (and the `$300` overflow marker gone); the emitted `stat_pc(i)` factor bound to `i` matching the hand-derived `prod(j,…) * ac(i,r)/pc(i)`; lmp2 + camcge byte-identical; the full golden-staleness scan shows no non-collateral prod model drifts; 767 AD/emit/e2e unit tests pass (Day 2). The `$141`/`$145` patches are in `DAY1_PROGRESS_NOTES.md` §1 + git `a8ff626c`.

---

**Document Status:** ✅ Complete — Sprint 35 Day 3 (P4 BANK)
**Last Updated:** 2026-07-25
**Owner:** Sprint 35 Execution Team

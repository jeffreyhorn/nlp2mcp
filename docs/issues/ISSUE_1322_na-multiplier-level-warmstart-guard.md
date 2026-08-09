# Issue #1322 — NA-propagation guard for presolve multiplier warm-start levels (robustlp de-allowlist)

**Class:** #1322 (NA-propagation into the generated matrix). **Manifestation (this issue):** a presolve multiplier warm-start *level* (`<mult>.L`), not a parameter value. Sibling manifestation already fixed: `emit_post_assignment_na_cleanup` (indexed-param division assignments). **Model:** robustlp (GAMS-54 EXECERROR-84). **Sprint:** 36 Day 10.

Under `--nlp-presolve`, `_emit_nlp_presolve` transfers NLP marginals into the MCP multiplier warm-start levels (`nu_/lam_/piL_/piU_/nu_*_fx_*`). When the NLP solver returns **no** marginal for a row/bound, `.m` is `NA`, so the transferred `<mult>.L` becomes `NA`. GAMS-53 tolerated it; GAMS-54's stricter matrix generation rejects an MCP variable with `.L = NA` as **EXECERROR-84 ("Matrix error - illegal level value")**, and the `NA` also propagates into any bilinear stationarity coefficient built from the multiplier (`(NA)*v` from `2*v*lam(...)`).

---

## Phase 0: Acceptance Gate

### Hand-Derived KKT Shape

The `--nlp-presolve` warm-start is not a KKT *equation* change — it seeds the MCP's dual variables at the NLP KKT point so PATH starts warm. For an original constraint `g(x)` with NLP marginal `g.m`, the paired MCP multiplier's level is initialized `μ.L := |g.m|` (ineq) / `g.m` (eq); for a bound at `x`, `π.L := |x.m|` at an active bound; for a fixed column's `_fx_` equation, `ν_fx.L := x.m`. The multiplier `.L` is a **warm-start level (a starting value), not a matrix coefficient** — its only KKT requirement is that it be a *finite* real; PATH re-derives the exact dual from it. Therefore, when the source marginal is `NA` (the solver reported no dual for that row/bound), the correct warm-start value is the **neutral default `0`** — identical to the un-warm-started default for that multiplier, and a valid feasible starting point (PATH converges the dual from 0 exactly as it would cold). No stationarity/primal-feasibility/complementarity equation changes; the guard only sanitizes a *starting value*.

### Expected Emit Pattern

In each emitted `<model>_mcp_presolve.gms`, after the marginal→multiplier transfer block (`<mult>.l[<dom>] = <marginal>;` for `nu_/lam_/piL_/piU_` and the `_fx_` transfers), a reset guard for every warmed multiplier:
```gams
* Reset any NA/UNDF warm-start multiplier levels to 0 (#1322)
<mult>.l<dom>$(NOT (<mult>.l<dom> > -inf and <mult>.l<dom> < inf)) = 0;
```
one line per transferred multiplier (eq/ineq/bound with their domain; `_fx_` multipliers scalar). The block is emitted **after** the `_fx_` warm-start so it covers the `_fx_` multipliers too; for a model with no `_fx_` warm-start the block position is byte-identical to emitting it before. The guard is a **no-op for finite levels** — `$(NOT (x > -inf and x < inf))` is false for every finite `x`, so a model without NA marginals is unchanged in its *solve* (the goldens gain only the inert guard lines).

### Verification Methodology

1. **Reproduce (Day-0):** compile `robustlp_mcp_presolve.gms` under GAMS 54.2.1 → `**** SOLVE … ABORTED, EXECERROR = 84`, `Bound [min,max] = [NA,NA]`, `lam_socpqcpcons`/`piL_y` `.L = NA` (`DAY0_KICKOFF.md` §3.1; `FIXTURE_AND_HARNESS_CATALOG.md` §4).
2. **After the fix:** re-compile → **EXECERROR-84 gone**, MODEL STATUS 1 Optimal.
3. **No-op / byte-additivity:** full-corpus `check_golden_staleness.py` — every drifted golden is a `*_mcp_presolve.gms` and the diff is **purely additive** (0 removals; all additions are the guard block), **0 cold goldens**; non-`_fx_` models re-emit byte-identical after the `_fx_`-coverage restructure.
4. **Case-(a/b/c) discriminator (PR27):** `kkt_residual.py` on a finite-marginal model is unchanged (the guard never fires) — the harness's `extract_dual_transfer` skips the guard resets (`_NA_GUARD_RE`), so the dual-transfer verification is preserved.
5. **Regression:** `--resolve-changed --since-commit 78ceaead` GO (every changed golden holds its bucket; robustlp `model_optimal_presolve` + match = same); determinism ×3 `{0,1,42}` md5-identical; full `make test` green.

### PROCEED/REPLAN Signal

**PROCEED** — the fix is a warm-start-value sanitizer (no KKT equation change), a proven no-op for finite marginals, and it clears EXECERROR-84 while robustlp holds `model_optimal_presolve` + match under GAMS 54. REPLAN only if a guarded reset changed a finite-marginal model's *solve* (it cannot — the guard is inert for finite `x`) or if `--resolve-changed` showed any bucket regression (it did not).

**Traced Fix-Surface (Day-0):** `src/emit/emit_gams.py` — `_emit_nlp_presolve` (the eq/ineq transfer loop ~`:1554`, the bound-lo/up loops ~`:1596`/`:1614`, the `_fx_` warm-start call ~`:1655`, and the NA-guard block that follows). Trace evidence: the emitted `robustlp_mcp_presolve.gms` transfer lines (`lam_socpqcpcons.l(i) = abs(socpqcpcons.m(i));`, `piL_y.l(i)$(…) = y.m(i);`) + the GAMS-54 `.lst` (`Matrix error - illegal level value` on `lam_socpqcpcons(1..7)`/`piL_y(1..7)` with `.L = NA`), reproduced live 2026-08-08 (`DAY10_P7_ROBUSTLP.md` §1–§2).

---

**Status:** ✅ FIXED (Sprint 36 Day 10) — NA-guard landed in `_emit_nlp_presolve`; robustlp de-allowlisted; KPIs 108/93/75 unchanged (robustlp was already `model_optimal_presolve` + match in the v53 DB — this restores its v54 solvability).

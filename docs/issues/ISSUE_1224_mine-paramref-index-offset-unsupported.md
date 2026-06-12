# mine: Parameter-Valued Index Offsets Unsupported

**GitHub Issue:** [#1224](https://github.com/jeffreyhorn/nlp2mcp/issues/1224)
**Status:** TRANSLATE FIXED (Sprint 27 Day 12, 2026-06-08) — mine now translates + compiles clean (+1 Translate). Correct SOLVE (the parameter-valued-offset KKT cross-term) is DEFERRED to Sprint 28; mine's next failure mode is `model_infeasible` (see below).
**Severity:** Medium — Translation aborts with internal error
**Date:** 2026-04-07
**Last Updated:** 2026-06-11 (Sprint 28 Prep Task 5 — Phase 0 Refresh — Sprint 28 Solve gate added; prior: Sprint 27 Day 12 — emit-render fix lands +1 Translate; Solve cross-term → Sprint 28)
**Affected Models:** mine

---

## Sprint 27 Day 12 resolution (2026-06-08) — emit-render fix → +1 Translate; Solve → Sprint 28

**Corrected fix surface (NOT the prep-doc guess).** The Day-11/Day-12 prompt + KU 6.1 anticipated the fix at `src/ad/constraint_jacobian.py:_try_eval_offset:133` + `src/ad/derivative_rules.py:2793` (the AD/Jacobian path, evaluating the offset to a constant). Empirically that is wrong for mine: the `pr` equation is kept **symbolic over `k`** in the MCP, so its complementarity `comp_pr(k,l,i,j)` is emitted with `k` unbound — the offset `li(k)` can NEVER be reduced to a constant at emit time. The hard error is raised in **`src/ir/ast.py` `IndexOffset.to_gams_string()`** (the `else` branch), NOT in the AD layer (translation reaches the emit phase before crashing).

**Fix (Approach 2, minimal): render parameter-valued offsets.** GAMS natively accepts a parameter expression as a lead/lag amount and evaluates it at runtime (`x(l, i+li(k), j+lj(k))` is valid GAMS). So `IndexOffset.to_gams_string()` gains a `ParamRef` branch that renders `base+param(idx)` (mirroring the existing `Call` branch; `_offset_expr_to_string` already knew how to render a `ParamRef`). No enumeration/constant-evaluation needed; `k` stays symbolic.

- **Result:** mine emits `comp_pr(k,l,i,j)$(...).. x(l,i+li(k),j+lj(k)) - x(l+1,i,j) =G= 0;`, translates, and **compiles clean** (`action=c`, 0 errors). **+1 Translate** (`translate_internal_error` → `translate_success`).
- **Blast radius: additive / zero-regression.** The `ParamRef` branch only fires where `to_gams_string()` previously *raised*; any model that translates today has no parameter-valued offset (it would have crashed), so no translating model is affected.

**KU 6.2 — mine's next failure mode: `model_infeasible`.** The emitted MCP solves to MODEL STATUS 4 Infeasible. The `stat_x(l,i,j)` cross-term from `pr` is incomplete: the Jacobian does not **invert** the parameter-valued offset (it emits `sum(k, lam_pr(k,l,i,j))` instead of `sum(k, lam_pr(k, l, i-li(k), j-lj(k)))`) and drops the `-sum(k, lam_pr(k, l-1, i, j))` contribution from the `-x(l+1,i,j)` term. Producing the correct stationarity for parameter-valued offsets requires the AD cross-term inversion at `src/ad/constraint_jacobian.py` / `src/ad/derivative_rules.py:2793` — the deeper change the prep doc named. **Deferred to Sprint 28** (the conditional Solve gain).

## Phase 0: Acceptance Gate

**Authored:** 2026-06-08 (Sprint 27 Day 12). The landed fix touches `src/ir/ast.py` only — outside the PR20-gated `src/{ad,kkt,emit}` set — so a Phase 0 gate is not strictly required, but recorded here for completeness.

### Hand-Derived KKT Shape

This fix is **emit-only** (string rendering); it does NOT change the KKT shape. The `pr` constraint `x(l, i+li(k), j+lj(k)) - x(l+1,i,j) ≥ 0 ⊥ lam_pr(k,l,i,j) ≥ 0` is preserved verbatim — only its GAMS *string* now renders the parameter-valued offset instead of crashing. (The *correct* `stat_x` cross-term — `sum(k, lam_pr(k,l,i-li(k),j-lj(k))) - sum(k, lam_pr(k,l-1,i,j))` — is the Sprint 28 Solve fix, NOT this PR.)

### Expected Emit Pattern

```gams
comp_pr(k,l,i,j)$(...).. x(l,i+li(k),j+lj(k)) - x(l+1,i,j) =G= 0;
```
i.e. the lead/lag amount is the parameter expression `li(k)`/`lj(k)`, rendered as `base+param(idx)`. Constant offsets (`t+1`, `t-3`) and symbol offsets (`i+j`) render unchanged.

### Verification Methodology

```bash
# 1. mine translates + compiles clean (was: "Complex offset expressions not yet supported").
.venv/bin/python -m src.cli data/gamslib/raw/mine.gms -o /tmp/mine_mcp.gms --skip-convexity-check --quiet
grep -E 'i\+li\(k\)|j\+lj\(k\)' /tmp/mine_mcp.gms            # expect: present in comp_pr
gams /tmp/mine_mcp.gms a=c lo=2 | grep -cE '\*\*\*\* .*Error' # expect: 0

# 2. Const/symbol offsets unchanged (unit test).
.venv/bin/python -m pytest tests/unit/ir/test_index_offset_paramref.py -q

# 3. mine's next failure mode (KU 6.2).
gams /tmp/mine_mcp.gms lo=2 | grep 'MODEL STATUS'           # expect: 4 Infeasible (Sprint 28 Solve)
```

### PROCEED/REPLAN Signal

**PROCEED** if: (a) mine translates + compiles clean (0 errors); (b) parameter-valued offsets render as `base+param(idx)`; (c) Const/symbol offset rendering unchanged (regression). **All met (Day 12).** **REPLAN** if any currently-translating model regresses (impossible by construction — the branch only fires where emit previously raised).

### Phase 0 Refresh (Sprint 28 Prep Task 5 — Solve fix, PR24 + PR27)

The gate above covered the Sprint 27 **translate** fix (emit-only string render, landed). This refresh is the Sprint 28 **Solve** gate — the `stat_x` cross-term that must invert the parameter-valued offset.

- **Hand-Derived KKT Shape (Solve):** `stat_x(l,i,j)` ← `sum(k, lam_pr(k,l,i-li(k),j-lj(k))) - sum(k, lam_pr(k,l-1,i,j))` (the offset is *inverted* `i-li(k)`/`j-lj(k)` relative to the forward constraint `pr.. x(l,i+li(k),j+lj(k))`, plus the `l-1` lag). The emit currently produces the non-inverted `sum(k, lam_pr(k,l,i,j))` → `model_infeasible`.
- **Expected Emit Pattern is a hypothesis (PR24):** prep names the AD/Jacobian inversion (`src/ad/constraint_jacobian.py` cross-term build / `src/ad/derivative_rules.py:2793`) as the candidate surface — but it may instead be `src/kkt/stationarity.py` (cross-term assembly) or the same `src/ir/ast.py` render layer; established by the Day-0 trace, not trusted from this doc.
- **Verification Methodology (PR27):**
  ```bash
  # NOTE: scripts/diagnostics/kkt_residual.py is a forthcoming Sprint 28 Priority 9 deliverable (PR27) — not yet in the repo; this is the in-sprint Phase-0 command, not runnable on current main.
  .venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/mine.gms --gdx mine_nlp.gdx --tol 1e-6 --json phase0_mine.json
  ```
  Target: mine **MODEL STATUS 1**. Expect **Case b** with `stat_x(l,i,j)` (the non-inverted `lam_pr` row) as the max-residual before the fix; the inverted shape drives that residual → 0. Also check boundary cells (Unknown 1.3): a residual non-zero *only* where `i-li(k)`/`j-lj(k)` lands out of domain ⇒ a domain-guard need, not the inversion.
- **Traced Fix-Surface (Day-0):** **Candidate (structural localization, 2026-06-12; harness-residual confirmation pending Day 4).** Confirmed the defect manifests in `mine_mcp.gms:103` `stat_x(l,i,j)` — the cross-term is the **non-inverted** `sum(k, lam_pr(k,l,i,j)$(c(l,i,j)))`, with no offset inversion and no `l-1` companion term. The surface that *builds* this `lam_pr` cross-term (AD/Jacobian vs `stationarity.py` assembly) is still to be pinned by the instrumented trace + harness Case-b residual on Day 4 (PR24) — the structural localization confirms the row, not yet the build site.
- **Cross-links:** KNOWN_UNKNOWNS Category 1 (Unknowns 1.1, 1.2, 1.3); BASELINE_METRICS §2 mine provenance row (S27 +1 Translate; Solve carried to S28, +1 firm).

---

## Problem Summary

The mine model (GAMSlib SEQ=39, "Opencast Mining") uses parameter-valued index
offsets in equation `pr`: `x(l, i+li(k), j+lj(k))` where `li(k)` and `lj(k)`
are parameters that provide the offset amount. The AD engine and index mapping
code only support constant integer offsets (e.g., `i+1`, `t-2`) and fail with
"Complex offset expressions not yet supported: ParamRef(li(k))".

---

## Root Cause

The equation `pr` uses parameter-dependent offsets:

```gams
Set k 'neighbors' / ne, se, sw, nw /;
Parameter
   li(k) 'lead for i' / (se,sw) 1 /
   lj(k) 'lead for j' / ("ne",se) 1 /;

pr(k,l+1,i,j)$c(l,i,j).. x(l,i+li(k),j+lj(k)) =g= x(l+1,i,j);
```

The offset `i+li(k)` is not a constant — it depends on the value of parameter
`li` at index `k`. For `k=se`, `li(se)=1` so the offset is `i+1`; for `k=ne`,
`li(ne)=0` so the offset is `i+0` (i.e., just `i`). The grammar parses this
as `IndexOffset(base="i", offset=ParamRef("li", ("k",)))`, but the AD engine
expects `offset` to be a `Const` (integer literal).

Additionally, the equation condition `$c(l,i,j)` references a 3-dimensional
subset `c` that has no concrete members at compile time (dynamically computed),
causing a separate warning about unevaluable set membership.

---

## Reproduction

```bash
# Translate — fails with internal error
.venv/bin/python -m src.cli data/gamslib/raw/mine.gms -o /tmp/mine_mcp.gms --quiet

# Error output:
# Error: Unexpected error - Complex offset expressions not yet supported: ParamRef(li(k))
```

---

## Error Details

```
Error: Unexpected error - Complex offset expressions not yet supported: ParamRef(li(k))
```

Also emits warning:
```
Failed to evaluate condition SetMembershipTest(c, (SymbolRef(l), SymbolRef(i), SymbolRef(j)))
with indices ('nw', '1', '1', '1'): Set membership for 'c' cannot be evaluated statically
because the set has no concrete members at compile time.
```

---

## Potential Fix Approaches

1. **Enumerate parameter-valued offsets**: For each value of `k`, evaluate
   `li(k)` and `lj(k)` at parse time and expand the equation into separate
   instances with constant offsets. E.g., for `k=se`: `x(l, i+1, j+1)`,
   for `k=ne`: `x(l, i+0, j+1)`, etc. This requires the parameter values
   to be known at IR build time.

2. **Support ParamRef offsets in IndexOffset**: Extend `IndexOffset.offset`
   to accept `Expr` (not just `Const`) and propagate through AD and
   stationarity building. This is a significant architectural change.

3. **Partial support with concrete expansion**: If the parameter has known
   concrete values and the set is small, expand each `(k, offset_value)`
   combination into separate equation instances with constant offsets.
   Handles mine's case (4 neighbors) without general ParamRef offset support.

---

## Files Involved

- `src/ir/ast.py` — `IndexOffset` definition (offset field type)
- `src/ad/constraint_jacobian.py` — Offset expression validation
- `src/ir/parser.py` — Index offset parsing
- `data/gamslib/raw/mine.gms` — Original model (80 lines)

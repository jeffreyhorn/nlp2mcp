# Sprint 27 Priority 5 comp_up Subset/Superset Fix-Surface Analysis

**Status:** ✅ COMPLETE (Day 0 prep — fix surface mapped; implementation lands Sprint 27 Day 1 per Task 11 schedule)
**Date:** 2026-05-28
**Owner:** Prep Task 7
**Inputs:** `docs/issues/ISSUE_1356_*.md` Phase 0 section (Sprint 27 Prep Task 2 / PR #1403); `docs/issues/ISSUE_1357_*.md` Phase 0 section (same); `src/kkt/complementarity.py:465-513`; `src/emit/emit_gams.py:1518-1698 + :2230-2243`; corpus sweep across `data/gamslib/mcp/*_mcp.gms` (Sprint 27 Day 0 baseline); Sprint 25 #1349 fix at `src/emit/emit_gams.py:1518-1531 + :1679-1698 + :1897-1906`.

---

## 1. Purpose

This document maps Sprint 27 Priority 5 (comp_up subset/superset domain widening, #1356 fawley + #1357 otpop) to specific patch sites in `src/kkt/complementarity.py` and `src/emit/emit_gams.py` ahead of Sprint 27 Day 1 implementation. It records:

- The **Phase 0 target shape** for each model (cross-referenced from ISSUE_1356 / ISSUE_1357 Phase 0 sections authored in Sprint 27 Prep Task 2).
- The **source-code patch sites** at `file:line` precision — both the equation-generation logic in `complementarity.py` and the matched-pair `.fx` fixup logic in `emit_gams.py`.
- A **unified diff sketch** illustrating the patch shape.
- The **affected-model corpus sweep** verifying fawley + otpop are the only models exhibiting the bug.
- The **implementation effort estimate** vs Priority 5's 8–12h budget.
- The **Sprint 25 #1349 (clearlak) regression risk assessment** — both fixes touch `emit_gams.py` variable-bound emission code, so coordinated review is required.
- A **Day 1 readiness assessment**.

The patch itself ships at Sprint 27 Day 1; this document is the engineering input.

---

## 2. Phase 0 Target Shape (cross-reference from Sprint 27 Prep Task 2)

### 2.1 #1356 fawley

**Current (buggy) emit** at `data/gamslib/mcp/fawley_mcp.gms`:

```gams
* L273:
comp_up_u(c)$(cr(c) and crdat(c,"supply") < inf).. crdat(c,"supply") - u(c) =G= 0;
* L315:
piU_u.fx(c)$(not (cr(c) and crdat(c,"supply") < inf)) = 0;
```

**Bug:** Equation domain is `c` (full crude set), but bound parameter `crdat` is declared over subset `cr(c)`. GAMS evaluates `crdat(c,"supply") < inf` at compile time for ALL `c`, including `c ∉ cr`, triggering `$171` ("Domain violation for set") at each non-subset element. The flat-conjunction guard `(cr(c) and crdat(c,"supply") < inf)` doesn't short-circuit — GAMS evaluates both operands before the `and`.

**Hand-derived expected shape (from ISSUE_1356 Phase 0):**

Either (a) equation-domain narrowing:

```gams
comp_up_u(cr)$(crdat(cr,"supply") < inf).. crdat(cr,"supply") - u(cr) =G= 0;
piU_u.fx(c)$(not cr(c)) = 0;
piU_u.fx(cr)$(not (crdat(cr,"supply") < inf)) = 0;
```

OR (b) nested `$`-filter (preserves outer domain `c`):

```gams
comp_up_u(c)$(cr(c))$(crdat(c,"supply") < inf).. crdat(c,"supply") - u(c) =G= 0;
piU_u.fx(c)$(not cr(c)) = 0;
piU_u.fx(c)$(cr(c))$(not (crdat(c,"supply") < inf)) = 0;
```

Either shape is acceptable per the Phase 0 verification methodology. **Recommendation:** Option (b) nested-`$` form preserves the equation-domain (`c`) for consistency with `piU_u`'s declared multiplier domain; Option (a) narrows the equation domain (`cr`) which may surface as a separate symbolic-domain change downstream.

### 2.2 #1357 otpop

**Current (buggy) emit** at `data/gamslib/mcp/otpop_mcp.gms`:

```gams
* L217:
comp_up_x(tt)$(t(tt) and xb(tt) < inf).. xb(tt) - x(tt) =G= 0;
* L247:
piU_x.fx(tt)$(not (t(tt) and xb(tt) < inf)) = 0;
```

**Bug:** Structurally identical to fawley — `tt` is the full year set (1965–1990), `xb(tt)` is declared over subset `t(tt)` (post-1973 only). GAMS evaluates `xb(tt) < inf` at compile time for all `tt`, triggering `$171` for each `tt ∉ t`.

**Hand-derived expected shape (from ISSUE_1357 Phase 0):** Same two acceptable forms as fawley with names substituted (`comp_up_x` / `piU_x` / `t(tt)` / `xb(tt)`).

### 2.3 Per-term verification methodology (both models)

```bash
# Regenerate emit:
.venv/bin/python -m src.cli data/gamslib/raw/fawley.gms -o /tmp/fawley_mcp.gms --skip-convexity-check --quiet
.venv/bin/python -m src.cli data/gamslib/raw/otpop.gms  -o /tmp/otpop_mcp.gms  --skip-convexity-check --quiet

# Verify zero $171 errors (was 3 each pre-fix):
for m in fawley otpop; do
  gams /tmp/${m}_mcp.gms action=c lo=2 o=/tmp/${m}_compile.lst
  echo "${m}: $(grep -c '\*\*\* Error 171' /tmp/${m}_compile.lst) error-171 (expect: 0)"
done

# Verify acceptable emit shape:
grep -nE '^comp_up_u|^piU_u\.fx' /tmp/fawley_mcp.gms
# Expect: either (a) comp_up_u(cr)$(crdat(cr,"supply") < inf) AND piU_u.fx(c)$(not cr(c)) + piU_u.fx(cr)$(not (...))
#       OR (b) comp_up_u(c)$(cr(c))$(crdat(c,"supply") < inf) AND piU_u.fx(c)$(not cr(c)) + piU_u.fx(c)$(cr(c))$(not (...))
grep -nE '^comp_up_x|^piU_x\.fx' /tmp/otpop_mcp.gms
# Expect: same shape options for x / t(tt) / xb(tt)
```

---

## 3. Source-Code Patch Sites

### 3.1 `src/kkt/complementarity.py:465-513` — comp_up equation generation

**Function:** `build_complementarity_pairs()` (per Sprint 26 baseline) — the section starting L465 generates upper-bound complementarity equations from `bound_def` records.

**Patch site A — `up_guard` assembly (L473-483):**

```python
# Current (L473-483):
up_guard: Expr | None = None
if bound_def.expr is not None:
    guard_expr = bound_def.expr
    if isinstance(guard_expr, LhsConditionalAssign):
        # Preserve the assignment condition: only generate
        # complementarity equations where the conditional
        # assignment is active and the resulting bound is < INF.
        rhs_guard = Binary("<", guard_expr.rhs, Const(float("inf")))
        up_guard = Binary("and", guard_expr.condition, rhs_guard)
    else:
        up_guard = Binary("<", guard_expr, Const(float("inf")))
```

**Bug:** When `guard_expr.condition` is a subset-membership predicate (e.g., `cr(c)` or `t(tt)`) AND `guard_expr.rhs` references a parameter declared over the same subset (`crdat(c,"supply")` or `xb(tt)`), the resulting flat `Binary("and", condition, rhs_guard)` joins them with a logical AND that GAMS does NOT short-circuit — GAMS evaluates `crdat(c,"supply") < inf` for all `c ∈ outer_domain`, triggering `$171` at non-subset elements.

**Proposed fix:** Detect when `guard_expr.condition` is a subset predicate AND `guard_expr.rhs` references the same subset; if so, restructure to nested-`$` form so the subset predicate gates the parameter lookup. Alternatively, narrow the equation domain to the subset.

**Patch site B — Equation definition (L485-494, indexed branch):**

```python
# Current (L485-494):
if var_domain:
    # Indexed variable: create indexed equation comp_up_x(i).. up - x(i) =G= 0
    F_piU = Binary("-", _bound_expr(bound_def), VarRef(var_name, var_domain))
    comp_eq = EquationDef(
        name=f"comp_up_{var_name}",
        domain=var_domain,
        relation=Rel.GE,
        lhs_rhs=(F_piU, Const(0.0)),
        condition=up_guard,
    )
```

**Bug:** `domain=var_domain` is the variable's full declared domain (the superset). When `up_guard` references a subset-restricted parameter, the equation's body `crdat(c,"supply") - u(c)` is evaluated for ALL `c ∈ var_domain`, including `c ∉ cr` — triggering `$171` independently of the `up_guard` issue.

**Proposed fix:** When the bound expression references a subset-restricted parameter, narrow `domain` to the subset (e.g., `domain=("cr",)` for fawley). The subset can be inferred from the parameter's declared domain (queryable via `model_ir.parameters[<name>].domain`).

### 3.2 `src/emit/emit_gams.py:2230-2243` — `piU_x.fx` matched-pair fixup (Issue #966)

**Function:** Emit phase for matched-pair multiplier fixing (Sprint 25 Issue #966) — emits `piU_x.fx(idx)$(not cond)` to fix bound multipliers to 0 when the primal variable is inactive.

**Patch site C — `piU_x.fx` emission with cond_gams (L2230-2243):**

```python
# Current (L2230, L2243):
fx_lines.append(f"{var_name}.fx({domain_str})$(not ({cond_gams})) = {fix_val};")
# ... L2239-2243:
piU_name = create_bound_up_multiplier_name(var_name)
if (var_name, ()) in kkt.complementarity_bounds_up:
    comp_pair_up = kkt.complementarity_bounds_up[(var_name, ())]
    if ref_mults is None or comp_pair_up.variable in ref_mults:
        fx_lines.append(f"{piU_name}.fx({domain_str})$(not ({cond_gams})) = 0;")
```

**Bug:** `cond_gams` is the same flat-conjunction string `(cr(c) and crdat(c,"supply") < inf)` rendered from the `complementarity.py` Patch site A's `up_guard`. The `not (...)` wrapper inherits the subset/superset evaluation issue.

**Proposed fix:** When `cond_gams` was restructured at Patch site A to nested-`$` form, the rendering at this site automatically benefits. **No change needed at this site IF Patch sites A + B are coordinated correctly.** This site is a consumer of the `up_guard` shape, not a producer.

**Coordination requirement:** Patch sites A + B in `complementarity.py` MUST produce a guard structure that, when rendered by `emit_gams.py`, yields a `not (cr(c))` outer + nested `$(not (crdat(c,"supply") < inf))` inner — OR the equation domain narrowing applies to `piU_x.fx` consistently.

### 3.3 #1349 interaction surface (`src/emit/emit_gams.py:1518-1698 + :1897-1906`)

**Sprint 25 #1349 fix region:**

- L1518-1531: `fx_to_l_overrides_by_var: dict[str, list[str]]` accumulator — collects `var.l(idx) = val` lines to preserve the `.l` side effect when `var.fx` is replaced by a complementarity equation.
- L1668-1698: `eq_paired_in_mcp` check — when the complementarity equation is paired, emit `var.l(idx) = val` to the accumulator instead of `var.fx(idx) = val`.
- L1897-1906: merge `.fx → .l` per-instance overrides into the bound block.

**Interaction risk with Priority 5:**

The Priority 5 patch sites A + B + (downstream) C operate on **comp_up equation generation** and **piU_x.fx matched-pair fixup at L2230-2243**. Sprint 25 #1349 operates on **var.fx → var.l side-effect preservation at L1518-1698 + L1897-1906**.

- **Different code regions:** L1518-1698 + L1897-1906 (Sprint 25 #1349) vs L2230-2243 (Priority 5 consumer site) — distinct functions, distinct accumulators.
- **Shared file:** Both touch `src/emit/emit_gams.py`. PR-level review must verify both code paths.
- **Clearlak canary:** Sprint 25 #1349 used clearlak as the test model for the `.l` side-effect preservation. If Priority 5 changes alter how `var.fx` or `piU_x.fx` is conditionally emitted (e.g., new emission paths for subset-narrowed equations), regression risk to clearlak's post-solve recurrence loop exists.

**Regression risk: LOW** — Patch sites A + B (`complementarity.py`) don't touch the `emit_gams.py` `.l` accumulator. Patch site C (`emit_gams.py:2230-2243`) consumes a restructured `cond_gams` string but doesn't alter the `.l`-override branch logic. Mitigation: byte-stability check on clearlak's regenerated emit after Priority 5 lands (verify zero diff vs current main; if any diff, root-cause and ensure #1349 behavior preserved).

---

## 4. Unified Diff Sketch (illustrative; concrete diff lands at Sprint 27 Day 1)

The diff is approximately 50–80 lines across 2 files. Below is the high-level shape:

### 4.1 `src/kkt/complementarity.py`

```diff
@@ src/kkt/complementarity.py:469-494 @@
 # For expression-based bounds (e.g., x.up(s) = param(s)), some
 # instances may have INF values — add a guard condition to skip
 # them and avoid degenerate complementarity equations.
 # Applies to both indexed and scalar variables.
+#
+# Sprint 27 #1356 + #1357: when the bound parameter is declared
+# over a subset of var_domain (subset/superset mismatch), the
+# flat-conjunction guard `Binary("and", cond, rhs_guard)` causes
+# GAMS to evaluate `param < inf` for all var_domain elements,
+# triggering $171 on non-subset elements. Restructure to nested
+# `$`-filter form OR narrow equation domain to the subset.
 up_guard: Expr | None = None
+narrowed_domain: tuple[str, ...] | None = None  # If subset detected
 if bound_def.expr is not None:
     guard_expr = bound_def.expr
     if isinstance(guard_expr, LhsConditionalAssign):
-        rhs_guard = Binary("<", guard_expr.rhs, Const(float("inf")))
-        up_guard = Binary("and", guard_expr.condition, rhs_guard)
+        # Detect subset/superset mismatch: condition is a single-arg
+        # subset predicate (e.g., `cr(c)` where `cr` ⊂ `c`), AND
+        # rhs references a parameter declared over `cr`.
+        subset_name = _extract_subset_predicate(guard_expr.condition, var_domain, model_ir)
+        rhs_subset = _bound_expr_subset_dependency(guard_expr.rhs, model_ir)
+        if subset_name is not None and subset_name == rhs_subset:
+            # Recommended: narrow equation domain to subset.
+            narrowed_domain = (subset_name,)
+            rhs_guard = Binary("<", guard_expr.rhs, Const(float("inf")))
+            up_guard = rhs_guard  # No outer subset predicate needed when domain is narrowed
+        else:
+            rhs_guard = Binary("<", guard_expr.rhs, Const(float("inf")))
+            up_guard = Binary("and", guard_expr.condition, rhs_guard)
     else:
         up_guard = Binary("<", guard_expr, Const(float("inf")))

 if var_domain:
+    # Sprint 27 #1356 + #1357: use narrowed_domain if subset detected
+    eq_domain = narrowed_domain if narrowed_domain is not None else var_domain
     F_piU = Binary("-", _bound_expr(bound_def), VarRef(var_name, var_domain))
     comp_eq = EquationDef(
         name=f"comp_up_{var_name}",
-        domain=var_domain,
+        domain=eq_domain,
         relation=Rel.GE,
         lhs_rhs=(F_piU, Const(0.0)),
         condition=up_guard,
     )
     comp_bounds_up[(var_name, ())] = ComplementarityPair(
         equation=comp_eq, variable=piU_name, variable_indices=var_domain
     )
```

**New helper functions** (in `complementarity.py` or a sibling utilities module):

```python
def _extract_subset_predicate(
    condition: Expr,
    var_domain: tuple[str, ...],
    model_ir: ModelIR,
) -> str | None:
    """If `condition` is a single-arg subset predicate `subset(eq_idx)`
    where `subset` ⊂ `eq_idx`'s declared set, return the subset name.
    Otherwise return None.
    """
    # Match SetMembershipTest(subset, (eq_idx,)) shape
    # Verify model_ir.sets[subset].domain == (parent,) where parent
    # is the set associated with eq_idx in var_domain.
    # Reuse pattern from src/kkt/stationarity.py:_find_superset_in_domain.
    ...

def _bound_expr_subset_dependency(
    bound_expr: Expr,
    model_ir: ModelIR,
) -> str | None:
    """If `bound_expr` references a parameter declared over a single-arg
    subset, return the subset name. Otherwise return None.
    """
    # Extract parameter refs; check their declared domain against
    # model_ir.sets for single-parent subset declarations.
    ...
```

### 4.2 `src/emit/emit_gams.py`

**No direct edits expected** at L2230-2243 if `complementarity.py` produces correctly-structured `up_guard` + narrowed `domain`. The matched-pair `piU_x.fx` fixup at L2243 inherits the corrected `cond_gams` rendering automatically.

**Defensive change (optional):** When `cond_gams` references a subset predicate, emit a separate `piU_x.fx(c)$(not subset(c)) = 0;` fixup line BEFORE the inner condition fixup, matching the expected emit shape from Phase 0:

```diff
@@ src/emit/emit_gams.py:2239-2243 @@
 piU_name = create_bound_up_multiplier_name(var_name)
 if (var_name, ()) in kkt.complementarity_bounds_up:
     comp_pair_up = kkt.complementarity_bounds_up[(var_name, ())]
     if ref_mults is None or comp_pair_up.variable in ref_mults:
+        # Sprint 27 #1356 + #1357: emit subset-narrowing fixup separately
+        # so the inner $(not (rhs < inf)) condition evaluates within the
+        # subset only (avoiding $171 on the parameter lookup).
+        subset_name = _detect_subset_in_cond(cond_gams)
+        if subset_name is not None:
+            inner_cond = _strip_subset_from_cond(cond_gams, subset_name)
+            fx_lines.append(f"{piU_name}.fx({domain_str})$(not {subset_name}({domain_str})) = 0;")
+            fx_lines.append(f"{piU_name}.fx({domain_str})$({subset_name}({domain_str}))$(not ({inner_cond})) = 0;")
+        else:
             fx_lines.append(f"{piU_name}.fx({domain_str})$(not ({cond_gams})) = 0;")
```

**Note:** The defensive change above is the **nested-`$` form** alternative if Patch site B chooses NOT to narrow `domain` (preserves equation-domain `c` while applying subset-narrowing at the emit boundary). Sprint 27 Day 1 implementation may choose either approach; both produce GAMS-compile-clean emit per the Phase 0 acceptance gate.

---

## 5. Affected-Model Corpus Sweep (Unknown 5.2 Resolution)

### 5.1 Sweep command and results

Per the Task 7 prompt, ran POSIX ERE sweep:

```bash
grep -lE 'comp_up_x\(.*\)\$\(.*<[[:space:]]*inf\)' data/gamslib/mcp/*_mcp.gms
# Results:
#   data/gamslib/mcp/gtm_mcp.gms
#   data/gamslib/mcp/ibm1_mcp.gms
#   data/gamslib/mcp/otpop_mcp.gms
#   data/gamslib/mcp/tricp_mcp.gms
```

Also ran broader sweep (catches fawley's `comp_up_u` shape):

```bash
grep -lE 'comp_up_[a-z]+\(.*\)\$\(.*<[[:space:]]*inf\)' data/gamslib/mcp/*_mcp.gms
# Returns 28 models including fawley, otpop, gtm, ibm1, tricp, and 23 others
# with comp_up patterns matching the flat-conjunction shape — but only 2
# (fawley + otpop) actually exhibit the $171 bug.
```

### 5.2 Per-model classification (Sprint 27 Day 0 baseline buckets)

| Model | Day 0 solve status | Day 0 outcome category | Affected? |
|---|---|---|---|
| `fawley` | failure | path_syntax_error | **✅ YES — #1356 target** (subset `cr(c)` + param `crdat(c,"supply")`) |
| `otpop` | failure | path_syntax_error | **✅ YES — #1357 target** (subset `t(tt)` + param `xb(tt)`) |
| `gtm` | success | model_optimal (compare=match) | ❌ NO — `pc(i,j)` declared over `(i,j)` (full eq-domain); no subset/superset mismatch |
| `ibm1` | success | model_optimal (compare=match) | ❌ NO — `sup(s,"inventory")` declared over `(s,*)` (full eq-domain); no mismatch |
| `tricp` | failure | path_solve_terminated | ❌ NO — bound expr is `myScale * smax((i,kp), fx(i,kp))` (no subset-restricted parameter); failure is `path_solve_terminated`, NOT `path_syntax_error` — unrelated bug class |

**Verdict (Unknown 5.2):** **CONFIRMED — fawley + otpop are the only 2 models affected by the comp_up subset/superset bug.** The 4 corpus-sweep matches that share the regex shape (gtm/ibm1/otpop/tricp) include 2 false positives (gtm/ibm1 — parameters declared over full eq-domain; no mismatch) and 1 unrelated failure (tricp — `path_solve_terminated`, not `path_syntax_error`).

The corpus sweep's regex match is **necessary but not sufficient** for the bug — the bug requires BOTH (a) the flat-conjunction guard shape AND (b) the bound parameter is declared over a strict subset of the equation domain. Only fawley + otpop satisfy both.

### 5.3 Sweep audit note

The 28-model broader sweep (covering `comp_up_u` and other variants) includes models like `agreste`, `cesam`, `lnts`, `indus`, etc. — all are in `model_infeasible` or `compare_match` buckets, meaning their comp_up shape compiles + solves cleanly. None of these models exhibit subset/superset parameter declarations against the bound's eq-domain.

**No additional models discovered.** Priority 5 scope CONFIRMED at 2 models.

---

## 6. Implementation Effort Estimate

### 6.1 Effort breakdown

| Sub-task | Effort | Notes |
|---|---|---|
| `complementarity.py` subset-detection helpers (`_extract_subset_predicate` + `_bound_expr_subset_dependency`) | 1.5h | Reuse pattern from `src/kkt/stationarity.py:_find_superset_in_domain` per Task 6 review |
| `complementarity.py` up_guard + equation-domain restructure (Patch sites A + B) | 1.5h | Single-function change at L473-494 |
| `emit_gams.py` defensive subset-detection at piU_x.fx fixup (Patch site C; optional) | 1h | Skip if Patch site B narrows equation domain instead |
| Unit tests for new helpers + integration tests for fawley + otpop emit | 1.5h | New tests in `tests/unit/kkt/test_complementarity.py` + `tests/integration/emit/test_fawley_comp_up.py` / `test_otpop_comp_up.py` |
| Clearlak byte-stability regression check (Sprint 25 #1349 canary) | 0.5h | Regenerate `clearlak_mcp.gms`, diff against current main artifact |
| GAMS compile-check verification on fawley + otpop (Phase 0 PROCEED gate) | 0.5h | Run `gams action=c lo=2` on both; expect 0 errors |
| 11 Tier 0/1 canary byte-stability regression check (per PR19 widening Day 0) | 0.5h | Sprint 27 Day 0 widening lands fawley + otpop in PR19; CI runs this automatically once widening merges |
| Buffer for review iteration | 1h | PR review may surface refinements |
| **Total** | **~7.5–8h** | **Within Priority 5's 8–12h budget** |

### 6.2 Patch shape verdict (Unknown 5.1 resolution)

**COORDINATED patch across `src/kkt/complementarity.py` + `src/emit/emit_gams.py`.**

The "coordinated" classification reflects:

- **Mandatory** changes to `complementarity.py` Patch sites A + B (`up_guard` restructure + equation-domain narrowing).
- **Optional defensive** changes to `emit_gams.py` Patch site C (subset-detection at piU_x.fx fixup) — only needed if Patch site B chooses NOT to narrow equation domain.

If Sprint 27 Day 1 chooses the equation-domain-narrowing approach (Option a in §2.1 / §2.2 / §3.1 Patch B), the fix lands as a **single-file change to `complementarity.py`**. If Day 1 chooses the nested-`$`-filter approach (Option b), the fix lands as a **coordinated change across both files**.

**Recommendation:** Equation-domain-narrowing (Option a / single-file). Rationale: smaller patch surface, cleaner semantic alignment with the parameter's declared domain, no `emit_gams.py` change needed, lower regression risk to #1349. Day 1 engineer may override this recommendation if domain-narrowing surfaces downstream issues (e.g., the multiplier's declared domain becoming inconsistent with the narrowed equation domain — though `piU_x` is declared by the same `bound_def` so this should not arise).

**Final verdict (Unknown 5.1):** **Single-file `complementarity.py`-only patch recommended.** Coordinated `complementarity.py + emit_gams.py` patch is a defensive fallback if equation-domain-narrowing surfaces issues.

---

## 7. Sprint 25 #1349 (Clearlak) Regression Risk Assessment (Unknown 5.3 Resolution)

### 7.1 Code-path overlap analysis

| Code region | Sprint 25 #1349 site | Priority 5 site | Overlap? |
|---|---|---|---|
| `src/emit/emit_gams.py:1518-1531` (fx_to_l_overrides accumulator) | YES | NO | None |
| `src/emit/emit_gams.py:1668-1698` (eq_paired_in_mcp / `.fx → .l` substitution) | YES | NO | None |
| `src/emit/emit_gams.py:1897-1906` (merge .l overrides) | YES | NO | None |
| `src/emit/emit_gams.py:2230-2243` (piU_x.fx matched-pair fixup) | NO | YES (Patch site C, optional) | None — different function |
| `src/kkt/complementarity.py:465-513` (comp_up generation) | NO | YES (Patch sites A + B) | None |

**No direct code-path overlap.** The two fixes operate on distinct functions within `emit_gams.py` + an unrelated module (`complementarity.py`).

### 7.2 Indirect risk: `.fx` emission semantics

The Sprint 25 #1349 fix is concerned with **`var.fx(idx) = val` ↔ `var.l(idx) = val` side-effect preservation when the source's `var.fx` is replaced by an `_fx_` complementarity equation**. Priority 5 modifies **how `piU_x.fx` is emitted in the matched-pair fixup AND how the comp_up equation's domain is narrowed** — both are downstream of #1349's accumulator logic.

**Verification check:** After Priority 5 lands, regenerate `clearlak_mcp.gms` and diff against current main:

```bash
.venv/bin/python -m src.cli data/gamslib/raw/clearlak.gms -o /tmp/clearlak_mcp_post_pr5.gms --skip-convexity-check --quiet
diff -u data/gamslib/mcp/clearlak_mcp.gms /tmp/clearlak_mcp_post_pr5.gms
# Expect: zero diff (clearlak doesn't use subset/superset bounds; Priority 5 path inactive for clearlak)
```

If diff is non-zero, root-cause:
- If diff is in `_fx_` complementarity equation generation: Priority 5 unexpectedly modified clearlak's path; investigate.
- If diff is in `var.l(idx) = val` lines: Sprint 25 #1349 behavior changed; rollback Priority 5 changes affecting the `.l` accumulator.

### 7.3 Final verdict (Unknown 5.3)

**Regression risk: LOW.** Code paths are distinct; clearlak's emit shape doesn't trigger Priority 5's subset/superset detection (clearlak's bound parameters are declared over their equation domains, not subsets). **Mitigation:** byte-stability regression check on clearlak as part of Priority 5 PR pre-merge verification.

**11 Tier 0/1 canary byte-stability:** Priority 5 changes are inactive for the 11 Tier 0/1 canaries (none have subset/superset bound parameters). Expected byte-stable; verified by PR19 widening's CI on Sprint 27 Day 0.

---

## 8. Day 1 Readiness Assessment

| Readiness Criterion | Status |
|---|---|
| Phase 0 target shape documented (ISSUE_1356 + ISSUE_1357 §"Phase 0 Acceptance Gate") | ✅ Sprint 27 Prep Task 2 / PR #1403 |
| Patch sites identified at `file:line` precision | ✅ §3 (Patch sites A, B, C with exact line ranges) |
| Unified diff sketch authored | ✅ §4 (50–80 line shape sketch with helper-function signatures) |
| Affected-model corpus sweep complete | ✅ §5 (2 models confirmed: fawley + otpop; 4 false-positive matches identified) |
| Implementation effort within budget | ✅ §6.1 (~7.5–8h vs 8–12h budget) |
| Patch shape verdict | ✅ §6.2 (single-file `complementarity.py`-only recommended) |
| Sprint 25 #1349 regression risk assessed | ✅ §7 (LOW risk; mitigated by clearlak byte-stability check) |
| Day 1 engineer has all inputs | ✅ This document + linked Phase 0 sections + source-code refs |

**Day 1 readiness: GO.** Sprint 27 Day 1 engineer can begin implementation immediately using this document as the engineering input. Estimated wall-clock: 7.5–8h within Priority 5's 8–12h budget.

**Recommended Day 1 sequence:**

1. Author `_extract_subset_predicate` + `_bound_expr_subset_dependency` helpers in `complementarity.py` (1.5h).
2. Apply Patch sites A + B (`up_guard` restructure + equation-domain narrowing) (1.5h).
3. Add unit tests (`tests/unit/kkt/test_complementarity.py`) + integration tests (`tests/integration/emit/`) (1.5h).
4. Verify fawley + otpop GAMS compile-clean (0.5h).
5. Verify clearlak byte-stability (0.5h).
6. Open PR; review iteration buffer (1h).

---

## 9. Verification Summary

| Verification Target | Result |
|---|---|
| Phase 0 target shape cross-reference (from Prep Task 2) | ✅ §2 (both #1356 fawley + #1357 otpop) |
| Source-code patch sites identified at `file:line` precision | ✅ §3 (3 patch sites: A `complementarity.py:473-483`, B `:485-494`, C `emit_gams.py:2230-2243`) |
| Unified diff sketch (~50-100 lines) | ✅ §4 (illustrative shape with helper signatures + comment annotations) |
| Affected-model corpus sweep | ✅ §5 (4 narrow-regex matches; 2 broader-regex matches confirmed bug; **fawley + otpop only**) |
| Implementation effort estimate | ✅ §6.1 (~7.5–8h within 8–12h budget) |
| Patch shape verdict (Unknown 5.1) | ✅ §6.2 (single-file `complementarity.py`-only recommended; coordinated fallback if domain-narrowing surfaces issues) |
| Affected-model count (Unknown 5.2) | ✅ §5.2 (2 models confirmed) |
| Clearlak regression risk (Unknown 5.3) | ✅ §7 (LOW risk; mitigated by byte-stability check) |
| Day 1 readiness | ✅ §8 (GO; engineer has all inputs) |

**Sprint 27 Priority 5 PROCEED at the 8–12h budget.** Patch shape recommendation: single-file `complementarity.py`-only via equation-domain narrowing. Coordinated `complementarity.py + emit_gams.py` defensive fallback if Day 1 surfaces downstream issues.

---

## 10. Related Documents

- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 7 — this task's specification.
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` §Unknowns 5.1, 5.2, 5.3 — research questions this task verifies.
- `docs/issues/ISSUE_1356_*.md` §"Phase 0 Acceptance Gate" — fawley target shape source (Sprint 27 Prep Task 2 / PR #1403).
- `docs/issues/ISSUE_1357_*.md` §"Phase 0 Acceptance Gate" — otpop target shape source.
- `CONTRIBUTING.md` §"Phase 0 Acceptance Gates" — verification methodology (Sprint 26 retro PR20 codification, Sprint 27 Prep Task 2).
- `docs/planning/EPIC_4/SPRINT_27/PR19_WIDENING_DESIGN.md` (Sprint 27 Prep Task 5) — Sprint 27 Day 0 widening lands fawley + otpop in PR19 Pattern C tier for automated regression detection.
- `docs/planning/EPIC_4/SPRINT_25/SPRINT_LOG.md` (Sprint 25 #1349 entry) — clearlak `.l` side-effect preservation fix.
- Source code:
  - `src/kkt/complementarity.py:465-513` (Patch sites A + B)
  - `src/emit/emit_gams.py:1518-1698 + :1897-1906` (Sprint 25 #1349 region — code-path overlap analysis)
  - `src/emit/emit_gams.py:2230-2243` (Patch site C — piU_x.fx matched-pair fixup)
  - `src/kkt/stationarity.py:3626-3670` (`_find_superset_in_domain`) — reference pattern for new helpers
- Sprint 27 Day 0 baseline: `data/gamslib/gamslib_status.json` — fawley + otpop both at `solve.outcome_category = path_syntax_error` (Day 0 verified).

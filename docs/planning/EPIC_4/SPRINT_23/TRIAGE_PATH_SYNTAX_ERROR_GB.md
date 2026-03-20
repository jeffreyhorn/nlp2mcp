# Triage: path_syntax_error Subcategories G+B

**Created:** 2026-03-20
**Sprint:** 23 (Priority 4 — path_syntax_error ≤ 15)
**Source:** Sprint 23 Prep Task 6
**Related:** Sprint 22 `PATH_SYNTAX_ERROR_STATUS.md`, KU-18–KU-21

---

## 1. Executive Summary

The Sprint 23 prep plan estimated **7 models** (2 subcategory G + 5 subcategory B). After running the current pipeline on all 20 remaining path_syntax_error models, the actual counts are:

- **Subcategory G (set index reuse):** 1 model (srkandw)
- **Subcategory B (domain violation, $171):** 4 models (chenery, hhfair, otpop, shale)
- **Total G+B:** 5 models (not 7 as estimated)

The discrepancy is because Sprint 22 fixed 3 of the original 4 subcategory G models (kand, prolog, spatequ) and reclassified cesam from B to a different status. The prep plan's "2 G + 5 B = 7" estimate was based on pre-Sprint 22 counts that were not updated.

---

## 2. Full Classification of 20 Remaining path_syntax_error Models

| # | Model | Primary Error Codes | Subcategory | Root Cause |
|---|-------|-------------------|-------------|------------|
| 1 | camcge | $141 | A (missing data) | Missing parameter values; Issues #882/#871 |
| 2 | cesam2 | $140 | A* ($140 unknown symbol) | Undefined `centropy` function reference; Issue #1041 |
| 3 | **chenery** | **$171**, $445 | **B (domain violation)** | Index shadowing: `t` used as sum loop index and in condition `$(t(i))` |
| 4 | china | $141 | A (missing data) | Missing parameter data (alias domain mismatch in IR) |
| 5 | clearlak | $352, $149, $126 | C+New | Uninitialized sets + uncontrolled set in stationarity |
| 6 | decomp | $140 | A (unknown symbol) | Missing subset data in equations |
| 7 | dinam | $140 | A (unknown symbol) | Missing parameter data (domain-less params with indexed values) |
| 8 | feedtray | — (translate fail) | T (translate) | `LhsConditionalAssign` not supported in IR |
| 9 | harker | $140, $409 | A (unknown symbol) | Missing parameter data + unrecognizable items |
| 10 | **hhfair** | **$171** | **B (domain violation)** | `nu_budget(tl+1)$(ord(tl)...)`: domain violation on offset reference |
| 11 | indus | $140, $130, $148... | A (complex) | 38 errors: missing data, dimension mismatches, division on set |
| 12 | lmp2 | $140 | A (unknown symbol) | Missing subset assignment data |
| 13 | nonsharp | $352 | New ($352) | Uninitialized dynamic subsets used as domains; Issue #956 |
| 14 | **otpop** | **$171** | **B (domain violation)** | `$(t(tt))` domain check: alias-as-subset condition on equation domain |
| 15 | ramsey | $141 | A (missing data) | Missing parameter values |
| 16 | sample | $140 | A (unknown symbol) | Unknown symbol reference |
| 17 | saras | $140, $148 | A (unknown symbol) | Multiple missing params + dimension mismatches |
| 18 | **shale** | **$171** | **B (domain violation)** | `$(cf(c) and t(tf))`: subset condition on stationarity equation domain |
| 19 | **srkandw** | $2, $148, $171, $311 | **G (set index reuse)** | `sum(()$(tn(n)), 1)`: empty sum domain from index filter bug |
| 20 | worst | $141 | A (missing data) | Unreferenced MCP variable ($483 in Sprint 22; now $141) |

**Bold** = G+B target models.

### Subcategory Distribution Summary

| Subcategory | Count | Models |
|-------------|-------|--------|
| A (missing data) | 10 | camcge, china, decomp, dinam, harker, indus, lmp2, ramsey, sample, saras |
| A* (cesam2) | 1 | cesam2 (undefined function, not simple missing data) |
| **B (domain violation)** | **4** | **chenery, hhfair, otpop, shale** |
| C (uncontrolled set) | 1 | clearlak |
| **G (set index reuse)** | **1** | **srkandw** |
| New ($352) | 1 | nonsharp |
| T (translate fail) | 1 | feedtray |
| I/Other (worst) | 1 | worst |

---

## 3. Subcategory G: Set Index Reuse (1 Model)

### srkandw

**GAMS Errors:** $2 (Identifier expected), $171 (Domain violation), $148 (Dimension mismatch), $311 (ord function usage)

**Primary Bug:** Empty sum domain from incorrect index filtering

**Original GAMS:**
```gams
leaf(n)$(sum(tn('time-2',n), 1)) = yes;
```

**MCP Translation (incorrect):**
```gams
leaf(n) = yes$(sum(()$(tn(n)), 1));
```

**Root Cause:** In `_handle_aggregation()` (parser.py ~line 4758), the subset domain `tn('time-2',n)` is parsed and the index `n` is extracted from the nested index list. Because `n` is already in the equation's `free_domain` (from `leaf(n)`), the code at line ~4986-4992 filters `n` out of `sum_indices`, producing an empty tuple `()`. The first component `'time-2'` (a literal) is also lost.

**Correct MCP should be:**
```gams
leaf(n) = yes$(sum(n$(tn('time-2',n)), 1));
```

**Secondary Bug:** `ord('0-default')` on line 63 produces $311 because in GAMS `ord()` is unary and expects a set element (for example, `ord(i)`), not a quoted literal like `'0-default'`. This is a separate preprocessor issue (ScenRedParms is GUSS-related post-solve code that should be stripped).

**Fix Approach:** Modify `_handle_aggregation()` to NOT filter out indices that appear in subset specifications with literal co-indices. When `tn('time-2',n)` is encountered:
1. Keep `n` in `sum_indices` (it's an iteration variable, not a filter)
2. Preserve the literal `'time-2'` in the `SetMembershipTest` condition

**Effort Estimate:** 2-3h (parser change + unit tests)

**Sprint 22 KU-04 Status:** The `resolve_index_conflicts()` aliasing mechanism is sound for renaming conflicts, but srkandw's bug is NOT an aliasing problem — it's a semantic misinterpretation where the parser incorrectly treats a subset domain index as a filter variable. This requires a parser-level fix, not just better alias detection.

---

## 4. Subcategory B: Domain Violations (4 Models)

All 4 models produce GAMS $171 (Domain violation for set) in stationarity equations. Each has a different specific cause.

### 4.1 chenery — Index Shadowing in Sum

**GAMS Error:** $171 (Domain violation), $445 (Multiple operators)

**Problematic Line:**
```gams
stat_e(i)$(t(i)).. alp(i) * nu_dh(i) + 1$(t(i)) * lam_mb(i)
    + sum(t, ((-1) * h(t)) * lam_tb)$(t(i)) - piL_e(i) + piU_e(i) =E= 0;
```

**Root Cause:** The stationarity equation uses `t` as both:
1. A subset condition on the equation: `$(t(i))` (t is a subset of i)
2. A loop index in the Jacobian sum: `sum(t, ...)`

GAMS interprets `sum(t, ...)$(t(i))` ambiguously — the `t` in the condition `$(t(i))` could refer to the sum loop index or the global set `t`. The `$445` (multiple operators) error on `stat_m` is a secondary consequence.

**Fix Approach:** The emitter needs to rename the sum loop index to avoid shadowing the condition set. `resolve_index_conflicts()` should detect this conflict and alias the sum index (e.g., `sum(t__, ...)$(t(i))`).

**Effort Estimate:** 1-2h (extend index conflict detection to condition-scope conflicts)

**Existing Issue:** None filed yet.

### 4.2 hhfair — Offset Reference Domain Violation

**GAMS Error:** $171 (Domain violation)

**Problematic Line:**
```gams
stat_m(tl).. ... + nu_budget(tl+1)$(ord(tl) <= card(tl) - 1) + ... =E= 0;
```

**Root Cause:** `nu_budget(tl+1)` references the *next* element in ordered set `tl`. GAMS $171 fires because `tl+1` is not a valid literal member of the domain — it requires proper lag/lead syntax. The stationarity emitter generated `tl+1` as arithmetic, but GAMS wants structural set operations.

**Fix Approach:** The IR's `IndexOffset(+1, tl)` nodes must **not** serialize to arithmetic on the index (current bad output: `nu_budget(tl+1)`). Instead, the emitter should introduce a lead index (e.g., an alias `tlp`) over ordered set `tl` and emit a successor-based reference such as `nu_budget(tlp)$(ord(tlp) = ord(tl) + 1)` (or an equivalent lag/lead form), so that "next-period" access is expressed via valid GAMS lag/lead semantics rather than `tl+1`.

**Effort Estimate:** 2-3h (may need emitter changes for IndexOffset handling)

**Existing Issue:** None filed yet.

### 4.3 otpop — Alias-as-Subset Condition

**GAMS Error:** $171 (Domain violation)

**Problematic Line:**
```gams
stat_p(tt).. ... * nu_sup(tt) + sum(t, ((-1) * (del(t) * x(tt) * 0.365 * (1 - c)))
    * nu_kdef)$(t(tt)) - piL_p(tt) =E= 0;
```

**Root Cause:** The condition `$(t(tt))` uses `t` (an alias of a subset of `tt`) as a domain check on `tt`. GAMS $171 fires because `t` is not a proper domain for `tt` — the subset relationship is inverted or the condition references the wrong set hierarchy.

**Fix Approach:** Investigate the original GAMS model's set relationships. The stationarity builder applied a condition `$(t(tt))` that may have been incorrectly propagated from the equation body or may need a different form.

**Effort Estimate:** 2-3h (needs investigation of subset/alias relationships in IR)

**Existing Issue:** None filed yet.

### 4.4 shale — Subset Condition on Wrong Domain

**GAMS Error:** $171 (Domain violation)

**Problematic Line:**
```gams
stat_x(c,tf)$(cf(c) and t(tf)).. ((-1) * nu_mf(c,tf))
    + ((-1) * pf(c,tf)) * nu_arev(tf) - lam_cind(tf) - piL_x(c,tf) =E= 0;
```

**Root Cause:** `$(cf(c) and t(tf))` applies two subset conditions — `cf` on `c` and `t` on `tf`. GAMS $171 fires likely because `t(tf)` uses `t` to validate `tf` but the domain relationship isn't properly declared, OR because the multiplier `lam_cind(tf)` references a variable whose domain `tf` doesn't match the equation's condition scope.

**Fix Approach:** Verify the set hierarchy `t` ⊂ `tf` in the original model. The condition may need to be restructured, or `lam_cind` needs domain adjustment.

**Effort Estimate:** 2-3h (domain analysis + potential stationarity builder fix)

**Existing Issue:** None filed yet.

---

## 5. Cross-Category Overlap

### 5.1 G+B Models vs. Other Categories

| G+B Model | model_infeasible? | path_solve_terminated? | Notes |
|-----------|:-----------------:|:---------------------:|-------|
| srkandw | No | No | — |
| chenery | No | No | — |
| hhfair | No | No | — |
| otpop | No | No | — |
| shale | No | No | — |

**No overlap.** None of the 5 G+B models appear in model_infeasible (15 models) or path_solve_terminated (10 models).

### 5.2 Cascade Risk Assessment (KU-20)

For each G+B model, what happens if the syntax error is fixed?

| Model | CGE? | Non-convex? | Cascade Risk |
|-------|:----:|:-----------:|:------------:|
| srkandw | No | No (LP) | **Low** — LP models typically solve without infeasibility |
| chenery | No | No (NLP) | **Low** — simple NLP, unlikely to be infeasible |
| hhfair | No | No (NLP) | **Low** — welfare optimization model |
| otpop | No | No (NLP) | **Low** — simple optimization model |
| shale | No | No (NLP) | **Medium** — larger model with complex domain conditioning |

**Overall cascade risk: LOW.** None of the 5 models are CGE models (which Sprint 22 KU-24 identified as highest cascade risk). At most 1 model (shale) might cascade to model_infeasible, and 0-1 is well within the ≤ 3 influx budget.

---

## 6. Ranked Fix List

| Priority | Model | Subcategory | Estimated Effort | Dependencies | Confidence |
|----------|-------|-------------|-----------------|-------------|------------|
| 1 | srkandw | G | 2-3h | Parser fix for `_handle_aggregation()` subset domain filtering | High |
| 2 | chenery | B | 1-2h | Extend `resolve_index_conflicts()` for condition-scope shadowing | High |
| 3 | shale | B | 2-3h | Domain analysis + stationarity builder condition fix | Medium |
| 4 | otpop | B | 2-3h | Alias-subset condition investigation + fix | Medium |
| 5 | hhfair | B | 2-3h | IndexOffset emission fix (may benefit otpop too) | Medium |

**Total estimated effort: 9-14h** (higher than the prep plan's 2-3h estimate, which assumed batch-fixable patterns).

### Fix Dependencies and Grouping

1. **chenery** likely shares root cause with the Sprint 22 subcategory G mechanism (index conflict detection). May be fixable by extending `resolve_index_conflicts()`.
2. **hhfair** and **otpop** both involve offset arithmetic / alias domain issues. Fixing one may inform the other.
3. **srkandw** is a standalone parser bug.
4. **shale** requires independent investigation of domain conditioning in multi-index stationarity equations.

---

## 7. New Subcategory Assessment (KU-21)

Sprint 22 discovered these new subcategories:

| Subcategory | Model(s) | Error | Status | Effort |
|-------------|----------|-------|--------|--------|
| K (smax domain) | tricp | $148 (dimension mismatch) | Issue #1062 open; 760 MCP errors | **High** — not low-effort; complex sparse conditioning |
| GUSS dict | gussrisk | $161 | Issue #910 **CLOSED** — already fixed | **0h** (done) |
| Hyphenated labels | gtm | $120/$340 | Issue #827 open; moved to path_solve_terminated | **Low-Medium** — preprocessor or grammar fix, 1-2h |

**Assessment:** The "low-effort" assumption is **partially correct**:
- gussrisk: Already fixed (0h)
- gtm: Likely 1-2h (unquoted hyphenated labels in preprocessor)
- tricp: NOT low-effort — Issue #1062 describes 760 errors from sparse edge-set conditioning; estimated 4-6h

---

## 8. KU Verification Results

### KU-18: Subcategory G Aliasing Mechanism Is Sound

**Result:** ⚠️ PARTIALLY CONFIRMED

**Finding:** Only 1 subcategory G model remains (srkandw), not 2 as estimated. The `resolve_index_conflicts()` mechanism is sound for naming conflicts, but srkandw's bug is a different class: the parser incorrectly filters out a subset domain index (`n`) because it appears in the equation's free domain. This requires a parser-level fix in `_handle_aggregation()`, not just enhanced alias detection. Sprint 22 KU-04's finding (mechanism is sound, detection needs enhancement) remains accurate for naming conflicts, but srkandw needs a semantic fix.

### KU-19: Subcategory B Models Have Diverse Root Causes

**Result:** ✅ VERIFIED

**Finding:** The 4 subcategory B models (not 5 as estimated — cesam2 is actually $140, not $171) have 4 distinct root causes:
1. **chenery:** Index shadowing between sum loop variable and condition set
2. **hhfair:** Offset arithmetic on ordered set elements without lag/lead syntax
3. **otpop:** Alias-as-subset condition applied to wrong domain level
4. **shale:** Subset condition on multi-index stationarity equation with domain mismatch

No common emitter bug — Sprint 22 KU-03's refutation is confirmed. Each model requires individual investigation and a potentially different fix approach.

### KU-20: path_syntax_error → model_infeasible Cascade Risk

**Result:** ✅ VERIFIED (low risk)

**Finding:** None of the 5 G+B models are CGE models (the highest cascade risk per Sprint 22 KU-24). None overlap with the current model_infeasible (15) or path_solve_terminated (10) lists. At most 1 model (shale, due to complex domain conditioning) might cascade to model_infeasible. Expected influx: 0-1 models, well within the ≤ 3 budget. The model_infeasible ≤ 8 target is not at risk from these fixes.

### KU-21: New Sprint 22 Subcategories Are Low-Effort

**Result:** ⚠️ PARTIALLY CONFIRMED

**Finding:**
- **gussrisk (GUSS dict):** Issue #910 already closed — 0h remaining effort
- **gtm (hyphenated labels):** Likely 1-2h preprocessor fix — low-effort confirmed
- **tricp (smax domain, subcategory K):** NOT low-effort — Issue #1062 describes 760 MCP errors from sparse edge-set conditioning; estimated 4-6h. This is a significant task, not a quick fix.

Sprint 23 should target gtm (if it yields a solve) but defer tricp unless budget allows.

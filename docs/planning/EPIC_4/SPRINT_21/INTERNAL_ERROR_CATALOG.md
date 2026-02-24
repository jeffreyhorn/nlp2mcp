# internal_error Root Cause Catalog (7 Models)

**Created:** 2026-02-23
**Sprint:** 21 (Priority 2 workstream)
**Budget:** 6–10h
**Status:** Catalog complete, ready for Sprint 21 execution

---

## 1. Executive Summary

All 7 internal_error models were run through `parse_model_file()` with full traceback capture. The errors fall into **4 distinct root cause subcategories**, with **lead/lag indexing in parameter assignments** being the dominant blocker (3/7 models). No two subcategories share the same fix, but the lead/lag subcategory offers clear batch-fix potential.

### Root Cause Distribution

| Subcategory | Root Cause | Models | Count | Fix Type | Est. Effort |
|-------------|-----------|--------|-------|----------|-------------|
| B | Lead/lag indexing in parameter assignments | imsl, sarf, tfordy | 3 | A: Handler/case | 2–3h |
| C | Undefined symbol from missing `$libInclude` | clearlak | 1 | A: Handler/case | 1h |
| D1 | Variable index arity mismatch | indus | 1 | A: Handler/case | 1–2h |
| D2 | Malformed `if` statement parsing | senstran | 1 | B: Grammar+handler | 2–3h |
| A | Table row index mismatch | turkpow | 1 | A: Handler/case | 1–2h |

**Total estimated effort: 7–11h** (within the 6–10h budget, with some buffer needed)

### Key Findings

1. **Lead/lag is the primary blocker** (3/7 models) — contrary to the pre-research assumption that it was NOT the primary blocker
2. **No architectural changes needed** — all fixes are incremental (handler/case additions or targeted grammar fixes)
3. **Batch fix opportunity**: The 3 lead/lag models (imsl, sarf, tfordy) can all be fixed with a single `_extract_indices` enhancement
4. **One model (clearlak) depends on external include files** — may need to be reclassified as `missing_include`

---

## 2. Per-Model Analysis

### 2.1 clearlak — Undefined Symbol from Missing `$libInclude`

**Subcategory:** C (Undefined symbol reference)
**Error:** `ParserSemanticError: Parameter 'ScenRedParms' not declared [context: expression] (line 142, column 1)`
**Parser function:** `_handle_assign` (line 3820 of `src/ir/parser.py`)

**Root Cause:**
- Line 141: `$libInclude scenred.gms` — includes an external library file
- Lines 143+: Multiple assignments to `ScenRedParms('num_leaves')`, `ScenRedParms('num_random')`, etc.
- `ScenRedParms` is declared in the external `scenred.gms` file, which is not available to nlp2mcp
- The preprocessor strips the `$libInclude` directive, leaving the assignments to an undeclared parameter

**GAMS Source Context:**
```gams
$libInclude scenred.gms
* following lines assign to ScenRedParms, declared in scenred.gms
ScenRedParms('num_leaves')     = sum(leaf, 1);
ScenRedParms('num_random')     = 1;
ScenRedParms('num_nodes')      = card(n);
```

**Fix Options:**
1. **Auto-declare on first assignment** — if a parameter is used in an assignment but not declared, auto-declare it (lenient mode)
2. **Reclassify as `missing_include`** — since the root cause is a missing external library file, not an IR builder bug

**Recommended Fix:** Option 2 (reclassify). This is not an IR builder bug — it's a missing dependency. Alternatively, option 1 can be implemented as a general resilience improvement.

**Fix Type:** A (handler/case)
**Estimated Effort:** 1h

---

### 2.2 imsl — Lead/Lag Indexing in Parameter Assignment

**Subcategory:** B (Lead/lag syntax not handled)
**Error:** `ParserSemanticError: Lead/lag indexing (i++1, i--1) not supported in parameter assignments`
**Parser function:** `_handle_conditional_assign_general` → `_extract_indices` (line 612 of `src/ir/parser.py`)

**Root Cause:**
- Line 40: `w(m+floor((ord(n)-1)/k),n)$(ord(m) = 1) = 1 - mod(ord(n)-1,k)/k;`
- Line 41: `w(m+1,n)$w(m,n) = 1 - w(m,n);`
- Both use **linear lead** syntax (`m+floor(...)`, `m+1`) in the LHS index position of a parameter assignment
- The grammar correctly parses this as `index_simple` with a `lag_lead_suffix` (linear_lead)
- But `_extract_indices()` at line 610-614 raises an error when it encounters any `lag_lead_suffix` in parameter context

**GAMS Source Context:**
```gams
w(m+floor((ord(n)-1)/k),n)$(ord(m) = 1) = 1 - mod(ord(n)-1,k)/k;
w(m+1,n)$w(m,n) = 1 - w(m,n);
```

**Lead/lag usage:** 2 instances, both in conditional parameter assignments
**Lead/lag type:** Linear lead (`+` offset), not circular (`++`)

**Fix:** Extend `_extract_indices()` to handle `lag_lead_suffix` in parameter assignments by extracting the base index and storing the offset expression for later use in the IR.

**Fix Type:** A (handler/case)
**Estimated Effort:** 2–3h (shared with sarf, tfordy — same fix)

---

### 2.3 indus — Variable Index Arity Mismatch

**Subcategory:** D1 (Variable index arity mismatch)
**Error:** `ParserSemanticError: Variable 'ppc' expects 0 indices but received 2 (effective 2) [context: equation 'cost' RHS] [domain: ('g',)] (line 1099, column 210)`
**Parser function:** `_make_symbol` (line 4784 of `src/ir/parser.py`)

**Root Cause:**
- `ppc` is declared as a scalar `Positive Variable` (0 indices) at line 986
- But used with 2 indices at line 1025 (within the `cost(g)` equation): `sum(sea, pp*ppc(g,sea))`
- This is a GAMS source issue — either the declaration should include `(g,sea)` or the usage is wrong
- The GAMS compiler may be more lenient about index arity in certain contexts

**GAMS Source Context:**
```gams
Positive Variable pdev, ndev, mad, dr, inj, tw, ts, scc, ccc, pcc, slc, clc, plc
                  acost, x, xca, animal, ppc, esl, itw, itr, efl, slkwater, slkland;
...
+  sum(sea, pp*ppc(g,sea))   ← uses ppc with 2 indices
```

**Fix:** The IR builder's `_make_symbol()` could be made more lenient for index arity mismatches — treating extra indices as a warning rather than a hard error. Alternatively, inspect whether GAMS actually declares `ppc(g,sea)` somewhere that the parser misses (e.g., implicit domain from a table or loop context).

**Fix Type:** A (handler/case)
**Estimated Effort:** 1–2h

---

### 2.4 sarf — Lead/Lag Indexing in Parameter Assignment

**Subcategory:** B (Lead/lag syntax not handled)
**Error:** `ParserSemanticError: Lead/lag indexing (i++1, i--1) not supported in parameter assignments`
**Parser function:** `_handle_assign` → `_extract_indices` (line 612 of `src/ir/parser.py`)

**Root Cause:**
- Line 365: `luse(c,t++(cs(c,"start",s)-1),s) = 1$(ord(t) <= length(c,s));`
- Uses **circular lead** syntax (`t++expr`) in the LHS index position of a parameter assignment
- Same `_extract_indices()` limitation as imsl

**GAMS Source Context:**
```gams
luse(c,t++(cs(c,"start",s)-1),s) = 1$(ord(t) <= length(c,s));
```

**Lead/lag usage:** 1 instance, circular lead (`++`)
**Lead/lag type:** Circular lead with complex offset expression

**Fix:** Same as imsl — extend `_extract_indices()` to handle lead/lag in parameter assignments.

**Fix Type:** A (handler/case)
**Estimated Effort:** Included in imsl fix (2–3h total for all 3 lead/lag models)

---

### 2.5 senstran — Malformed `if` Statement

**Subcategory:** D2 (Malformed `if` statement parsing)
**Error:** `ParserSemanticError: Malformed if statement: missing condition [context: expression] (line 81, column 1)`
**Parser function:** `_handle_if_stmt` (line 3392 of `src/ir/parser.py`)

**Root Cause:**
- Line 81: `if(pors, ...);` — a GAMS `if(condition, statements)` with a simple scalar identifier as the condition
- The IR builder's `_handle_if_stmt` expects a specific parse tree structure for the condition but doesn't handle the case where the condition is a bare identifier (`pors`)
- `pors` is a scalar parameter set to 1 on line 78

**GAMS Source Context:**
```gams
pors = 1;  ← line 78
...
if(pors,                          ← line 81 — condition is bare identifier
   repdat.nw =  5;
   repdat.nd =  0;
   repdat.lw = 11;
   put repdat "low/high i          j                  x(i,j)" /;
);
```

**Fix:** The `_handle_if_stmt` handler needs to be updated to recognize a bare identifier as a valid condition expression. This may involve a minor grammar adjustment or just an IR builder handler update.

**Fix Type:** B (grammar + handler)
**Estimated Effort:** 2–3h

---

### 2.6 tfordy — Lead/Lag Indexing in Parameter Assignment

**Subcategory:** B (Lead/lag syntax not handled)
**Error:** `ParserSemanticError: Lead/lag indexing (i++1, i--1) not supported in parameter assignments`
**Parser function:** `_handle_assign` → `_extract_indices` (line 612 of `src/ir/parser.py`)

**Root Cause:**
- Line 97: `yv(te,te+3,s,cl,k) = ymf("a-30",k,s,cl);` — linear lead `te+3`
- Line 139: `avl(t,t-1) = 1;` — linear lag `t-1`
- Line 140: `avl(t,t-2) = 1;` — linear lag `t-2`
- All use linear lead/lag (`+N`, `-N`) in parameter assignment LHS indices
- Same `_extract_indices()` limitation as imsl and sarf

**GAMS Source Context:**
```gams
yv(te,te+3,s,cl,k) = ymf("a-30",k,s,cl);    ← te+3 linear lead
avl(t,t-1) = 1;                                ← t-1 linear lag
avl(t,t-2) = 1;                                ← t-2 linear lag
```

**Additional lead/lag in equations (not blocking — equations may hit separate issues later):**
- Line 189: `sy1(te-1)..` — equation domain with lag
- Line 191: `sy2(cl,te-1)..` — equation domain with lag
- Line 193: `sy3("pulplogs",te-1)..` — equation domain with lag
- Line 195: `sy4("pulp",t-1)..` — equation domain with lag

**Lead/lag usage:** 3 instances in parameter assignments (blocking), 4 in equation domains (may be secondary issue)
**Lead/lag types:** Linear lead (`+3`) and linear lag (`-1`, `-2`)

**Fix:** Same as imsl — extend `_extract_indices()` to handle lead/lag in parameter assignments.

**Fix Type:** A (handler/case)
**Estimated Effort:** Included in imsl fix (2–3h total for all 3 lead/lag models)

---

### 2.7 turkpow — Table Row Index Mismatch

**Subcategory:** A (Table row index mismatch)
**Error:** `ParserSemanticError: Parameter 'hlo' table row index mismatch [context: expression] (line 74, column 17)`
**Parser function:** `_parse_param_data_items` (line 5042 of `src/ir/parser.py`)

**Root Cause:**
- Parameter `hlo(m,te)` is declared at line 73 with domain `(m, te)`
- The inline data block at line 74 uses a dotted format: `hydro-4.1978 250`
- The parser expects data row indices to match the declared domain structure
- The dotted index `hydro-4.1978` may be parsed as a single token rather than two domain-separated indices (`hydro-4` and `1978`)

**GAMS Source Context:**
```gams
Parameter
   hlo(m,te) 'lower bound: hydro unit expansions (mw)'
             /  hydro-4.1978   250 /
```

**Fix:** The `_parse_param_data_items` function needs to handle dotted index notation for multi-dimensional parameters, splitting `hydro-4.1978` into `('hydro-4', '1978')` based on the declared domain cardinality.

**Fix Type:** A (handler/case)
**Estimated Effort:** 1–2h

---

## 3. Recommended Fix Order

Based on batch-fix potential, model count, and estimated effort:

| Priority | Subcategory | Models | Effort | Rationale |
|----------|-------------|--------|--------|-----------|
| 1 | B: Lead/lag in parameter assignments | imsl, sarf, tfordy | 2–3h | Highest leverage: one fix unblocks 3 models |
| 2 | D2: Malformed `if` statement | senstran | 2–3h | Grammar+handler fix, independent of other fixes |
| 3 | A: Table row index mismatch | turkpow | 1–2h | Targeted fix, may benefit other table-heavy models |
| 4 | D1: Variable index arity mismatch | indus | 1–2h | Lenient mode, may benefit other models with GAMS source quirks |
| 5 | C: Undefined symbol (missing include) | clearlak | 1h | Reclassify or add lenient auto-declare |

**Recommended Sprint 21 approach:**
1. **Day N:** Fix lead/lag in `_extract_indices()` → unblock imsl, sarf, tfordy (3 models)
2. **Day N+1:** Fix `if` statement condition parsing → unblock senstran (1 model)
3. **Day N+1:** Fix table row dotted index parsing → unblock turkpow (1 model)
4. **Day N+2:** Fix variable index arity → unblock indus (1 model)
5. **Day N+2:** Reclassify or fix clearlak → resolve clearlak (1 model)

---

## 4. Lead/Lag Analysis Summary

Since lead/lag is the dominant blocker (3/7 models), here is a consolidated view:

| Model | Line | Expression | Lead/Lag Type | Context |
|-------|------|-----------|---------------|---------|
| imsl | 40 | `m+floor((ord(n)-1)/k)` | Linear lead | Conditional param assign |
| imsl | 41 | `m+1` | Linear lead | Conditional param assign |
| sarf | 365 | `t++(cs(c,"start",s)-1)` | Circular lead | Param assign |
| tfordy | 97 | `te+3` | Linear lead | Param assign |
| tfordy | 139 | `t-1` | Linear lag | Param assign |
| tfordy | 140 | `t-2` | Linear lag | Param assign |

**Grammar status:** The Lark grammar already parses all lead/lag patterns correctly (via `lag_lead_suffix` rule with `linear_lead`, `linear_lag`, `circular_lead`, `circular_lag` variants). The issue is exclusively in the IR builder's `_extract_indices()` function at line 610-614, which rejects any `lag_lead_suffix` in parameter assignment context.

**Fix scope:** Extend `_extract_indices()` to extract the base index and lag/lead offset expression, then store the offset information in the IR for use during translation/emission.

---

## 5. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Lead/lag fix exposes secondary errors in imsl/sarf/tfordy | Medium | Low | After fixing lead/lag, re-run models to find next error (may be a different IR builder issue) |
| indus ppc arity issue is intentional GAMS behavior | Medium | Medium | Test with lenient mode; verify GAMS compiler accepts the code |
| senstran `if` fix causes regressions in other `if` handling | Low | High | Comprehensive `if` statement test suite before and after fix |
| turkpow dotted index fix doesn't generalize | Low | Low | Only turkpow uses this pattern in the 7-model set; can be targeted |
| clearlak reclassification reduces internal_error count metric improvement | Low | Low | Honest reclassification is better than a fake fix |

---

## 6. Notes

- **Note on `parse_file()` vs `parse_model_file()`:** The PREP_PLAN.md task description references `parse_file()`, but the pipeline uses `parse_model_file()` followed by `validate_model_structure()`. All 7 models succeed with `parse_file()` (Lark grammar parsing only) but fail in `parse_model_file()` (which includes IR builder tree-walking). The errors are in the IR builder, not the grammar — confirming the "parse but crash in IR builder" classification.
- **Lead/lag in equations:** tfordy also has lead/lag in equation domain definitions (lines 189-195). These are separate from the parameter assignment issue and may require additional handling in the equation builder.

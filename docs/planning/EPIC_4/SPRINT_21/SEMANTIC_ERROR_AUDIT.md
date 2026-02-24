# Semantic Error Audit: 7 `semantic_undefined_symbol` Models

**Created:** 2026-02-24
**Sprint:** 21 (Semantic Error Resolution workstream)
**Status:** Audit complete

---

## 1. Executive Summary

All 7 `semantic_undefined_symbol` models were audited. **None are caused by `$include` references.** Instead, all 7 fail because the nlp2mcp parser/IR builder doesn't recognize certain GAMS built-in functions or language features:

| Root Cause | Models | Count | Fixability |
|-----------|--------|-------|------------|
| Missing GAMS built-in function in grammar | camcge, feedtray, cesam2, sambal, procmean | 5 | **Fixable** — add to FUNCNAME regex |
| Missing Acronym semantic support | worst | 1 | **Fixable** — add acronym handling to IR builder |
| sameas() string literal misinterpretation | cesam | 1 | **Fixable** — fix condition handling in IR builder |

**Key finding:** All 7 models are fixable parser/IR bugs. None should be excluded from metrics.

**Recommended fix:** Add `sign`, `mapval`, `centropy`, `betareg` to the FUNCNAME terminal in `gams_grammar.lark` (5 models fixed, ~1h). Add acronym value handling to IR builder (1 model, ~1-2h). Fix sameas condition parsing (1 model, ~1h). **Total: ~3-4h for all 7 models.**

---

## 2. Per-Model Analysis

### 2.1 camcge — Missing `sign()` Built-in Function

| Field | Value |
|-------|-------|
| **Model** | camcge |
| **Type** | NLP |
| **Error** | `Undefined symbol 'sign' with indices ('i', 'lc')` |
| **Location** | Line 169 (preprocessed: ~line 169) |
| **Has `$include`?** | No |

**Error Context:**
```gams
xllb(i,lc) = xle(i,lc) + (1 - sign(xle(i,lc)));
```

**Root Cause:** `sign()` is a GAMS built-in function that returns -1, 0, or +1 based on the sign of its argument. It is listed in the [GAMS commands reference](https://github.com/ShiroTakeda/gams-mode/blob/master/gams-commands.txt) as a standard function but is missing from the nlp2mcp grammar's `FUNCNAME` terminal.

**Fix:** Add `sign` to the FUNCNAME regex in `src/gams/gams_grammar.lark` line 797.

**Classification:** **Parser bug — fixable** (grammar change, <30min)

---

### 2.2 feedtray — Missing `sign()` Built-in Function

| Field | Value |
|-------|-------|
| **Model** | feedtray |
| **Type** | NLP |
| **Error** | `Undefined symbol 'sign' with indices ('hllo',)` |
| **Location** | Line 277 (preprocessed: ~line 340) |
| **Has `$include`?** | No |

**Error Context:**
```gams
hl.lo(i) = (1 - 0.5*sign(hllo))*hllo/ hscale;
hv.lo(i) = (1 - 0.5*sign(hvlo))*hvlo/ hscale;
hl.up(i) = (1 + 0.5*sign(hlhi))*hlhi/ hscale;
hv.up(i) = (1 + 0.5*sign(hvhi))*hvhi/ hscale;
```

**Root Cause:** Same as camcge — `sign()` is a GAMS built-in function missing from the grammar.

**Fix:** Same as camcge — add `sign` to FUNCNAME. Fixes both models.

**Classification:** **Parser bug — fixable** (same fix as camcge)

---

### 2.3 cesam2 — Missing `centropy()` Built-in Function

| Field | Value |
|-------|-------|
| **Model** | cesam2 |
| **Type** | NLP |
| **Error** | `Undefined symbol 'CENTROPY' with indices ('ii', 'jj', 'jwt3', 'ii', 'jj', 'jwt3')` |
| **Location** | Line 431 |
| **Has `$include`?** | No |

**Error Context:**
```gams
ENTROPY.. DENTROPY =e= sum[(ii,jj,jwt3)$nonzero(ii,jj),
    CENTROPY(W3(ii,jj,jwt3),wbar3(ii,jj,jwt3))]
  + sum[(ii,jwt1), CENTROPY(W1(ii,jwt1),wbar1(ii,jwt1))]
  + sum[(macro,jwt2), CENTROPY(W2(macro,jwt2),wbar2(macro,jwt2))];
```

**Root Cause:** `centropy()` is a GAMS built-in intrinsic function for cross-entropy computation (`centropy(x, y) = x*log(x/y)`). The model's own comments (lines 45-48) confirm it is a "GAMS intrinsic function." It is listed in the [GAMS commands reference](https://github.com/ShiroTakeda/gams-mode/blob/master/gams-commands.txt) but is missing from FUNCNAME.

**Fix:** Add `centropy` to FUNCNAME.

**Classification:** **Parser bug — fixable** (grammar change, <30min)

---

### 2.4 sambal — Missing `mapval()` Built-in Function

| Field | Value |
|-------|-------|
| **Model** | sambal |
| **Type** | NLP |
| **Error** | `Undefined symbol 'mapval' with indices ('i',)` |
| **Location** | Line 36 |
| **Has `$include`?** | No |

**Error Context:**
```gams
tw(i)$(mapval(tb(i))     = mapval(na)) = 0;
xw(i,j)$(mapval(xb(i,j)) = mapval(na)) = 0;
```

**Root Cause:** `mapval()` is a GAMS built-in function for extended range arithmetic — it returns a classification code for special values (NA, INF, EPS, UNDF, etc.). Documented in [GAMS Parameters documentation](https://www.gams.com/latest/docs/UG_Parameters.html) and listed in the GAMS commands reference. Missing from FUNCNAME.

**Fix:** Add `mapval` to FUNCNAME.

**Classification:** **Parser bug — fixable** (grammar change, <30min)

---

### 2.5 procmean — Missing `betareg()` Built-in Function

| Field | Value |
|-------|-------|
| **Model** | procmean |
| **Type** | NLP |
| **Error** | `Undefined symbol 'betareg' with indices ('y', 'alpha', 'beta')` |
| **Location** | Line 45 |
| **Has `$include`?** | No |

**Error Context:**
```gams
tcdef.. tc =e= k1*T*betareg(y,alpha,beta)
  - k1*{(delta + a)*betareg(y,alpha,beta)
        +(b - a)*betareg(y,alpha + 1,beta)*g3}
  + k2*{(delta + a)*[1 - betareg(y,alpha,beta)]
        +(b - a)*[1 - betareg(y,alpha + 1,beta)*g3]}
  - k2*T*[1 - betareg(y,alpha,beta)];
```

**Root Cause:** `betareg()` is a GAMS built-in function for the regularized incomplete Beta function. It computes the cumulative distribution function of the Beta distribution: `betareg(x, a, b) = I_x(a, b)`. Listed in the GAMS commands reference. Missing from FUNCNAME.

**Fix:** Add `betareg` to FUNCNAME.

**Classification:** **Parser bug — fixable** (grammar change, <30min)

---

### 2.6 worst — Missing Acronym Semantic Support

| Field | Value |
|-------|-------|
| **Model** | worst |
| **Type** | NLP |
| **Error** | `Undefined symbol 'future' referenced` |
| **Location** | Line 93 |
| **Has `$include`?** | No |

**Error Context:**
```gams
Acronym  future, call, puto;

tpv.. pval =e= sum((i,t,j)$pdata(i,t,j,"nom"),
    (f(i,t) - pdata(i,t,j,"price")*pdata(i,t,j,"nom"))
        $(pdata(i,t,j,"type") = future)
  + (c(i,j,t)*pdata(i,t,j,"nom"))
        $(pdata(i,t,j,"type") = call)
  + (p(i,j,t)*pdata(i,t,j,"nom"))
        $(pdata(i,t,j,"type") = puto));
```

**Root Cause:** GAMS `Acronym` statements declare symbolic constants (like enums). The grammar already parses `Acronym` statements via the `acronym_stmt` rule (grammar line 650), but the IR builder (`src/ir/parser.py`) has no handler for `acronym_stmt` — acronym values are never registered as known symbols. When `future`, `call`, `puto` are later used in conditional expressions, the IR builder rejects them as undefined.

**Fix:** Add an `acronym_stmt` handler to the IR builder that registers each acronym name as a known symbol (likely as a special constant or a zero-valued parameter). ~1-2h.

**Classification:** **IR builder bug — fixable** (add handler, 1-2h)

---

### 2.7 cesam — sameas() String Literal Misinterpretation

| Field | Value |
|-------|-------|
| **Model** | cesam |
| **Type** | NLP |
| **Error** | `Undefined symbol 'ROW' referenced [context: equation 'ROWSUM' condition]` |
| **Location** | Line 371 |
| **Has `$include`?** | No |

**Error Context:**
```gams
ROWSUM(ii)$(not sameas(ii,"ROW")).. sum(jj, TSAM(ii,jj)) =e= Y(ii);
```

**Root Cause:** `ROW` is a set element declared in the model (line 45: `ROW 'Rest of world'`). In the equation condition `$(not sameas(ii,"ROW"))`, the `"ROW"` is a quoted string literal — it refers to the set element by name. The IR builder is correctly parsing the `sameas()` call but then rejecting `"ROW"` as an undefined symbol reference during semantic validation. The IR builder should recognize string literals in sameas() as set element name references, not as undeclared symbols.

**Fix:** Fix the condition handler in the IR builder to accept string literals in sameas() comparisons without requiring them to be separately declared as parameters or variables. ~1h.

**Classification:** **IR builder bug — fixable** (condition handling fix, 1h)

---

## 3. Root Cause Summary

### By Root Cause Category

| Root Cause | Models | Fix Location | Fix Effort |
|-----------|--------|-------------|------------|
| Missing `sign()` in FUNCNAME | camcge, feedtray | Grammar (FUNCNAME regex) | <30min (1 regex edit, fixes 2 models) |
| Missing `centropy()` in FUNCNAME | cesam2 | Grammar (FUNCNAME regex) | <30min (1 regex edit) |
| Missing `mapval()` in FUNCNAME | sambal | Grammar (FUNCNAME regex) | <30min (1 regex edit) |
| Missing `betareg()` in FUNCNAME | procmean | Grammar (FUNCNAME regex) | <30min (1 regex edit) |
| Missing Acronym handler in IR builder | worst | IR builder (parser.py) | 1-2h (new handler) |
| sameas string literal misinterpretation | cesam | IR builder (parser.py) | 1h (condition fix) |

### Batch Fix Opportunities

1. **Grammar FUNCNAME update** (1 edit, 5 models fixed): Add `sign|centropy|mapval|betareg` to the FUNCNAME regex. This is a single-line change that unblocks 5 of 7 models.

2. **IR builder Acronym handler** (1 new handler, 1 model fixed): Add `acronym_stmt` visitor that registers acronym names as known symbols.

3. **IR builder sameas fix** (1 condition fix, 1 model fixed): Fix string literal handling in equation conditional expressions.

**Total effort: ~3-4h for all 7 models.**

---

## 4. Recommendations

### Sprint 21 Fix Priority

| Priority | Fix | Models | Effort | Impact |
|----------|-----|--------|--------|--------|
| 1 | Add 4 functions to FUNCNAME regex | camcge, feedtray, cesam2, sambal, procmean | 30min | 5 models parse → translate pipeline |
| 2 | Add Acronym handler to IR builder | worst | 1-2h | 1 model parses |
| 3 | Fix sameas string literal handling | cesam | 1h | 1 model parses |

### Metric Impact

- **Current parse rate:** 132/160 (82.5%)
- **After FUNCNAME fix:** 137/160 (85.6%) — +5 models
- **After all 3 fixes:** 139/160 (86.9%) — +7 models
- **Sprint 21 parse target:** ≥135/160 (84.4%)

The FUNCNAME fix alone exceeds the Sprint 21 parse target. All 3 fixes together push parse rate to 86.9%.

### Should These Models Be Excluded from Metrics?

**No.** None of the 7 models should be excluded:
- None depend on `$include` files
- None have GAMSLIB source errors
- All fail due to nlp2mcp parser/IR builder bugs that are fixable
- All 7 models are standard NLP models that should be parseable

---

## 5. GAMS Built-in Functions Not in Grammar

This audit revealed 4 GAMS built-in functions missing from the FUNCNAME terminal. A broader survey of GAMS built-in functions suggests additional functions that may be needed in the future:

| Function | Category | Used By | Currently in Grammar? |
|----------|----------|---------|----------------------|
| `sign` | Discontinuous | camcge, feedtray | No |
| `centropy` | Information theory | cesam2 | No |
| `mapval` | Extended arithmetic | sambal | No |
| `betareg` | Statistical | procmean | No |
| `binomial` | Statistical | (potential) | No |
| `entropy` | Information theory | (potential) | No |
| `sigmoid` | Activation | (potential) | No |
| `ifthen` | Conditional | (potential) | No |
| `div` | Safe division | (potential) | No |
| `div0` | Safe division | (potential) | No |

**Recommendation:** Add `sign|centropy|mapval|betareg` now to fix the 7 blocked models. Consider a broader GAMS function audit during Sprint 21 to prevent future occurrences.

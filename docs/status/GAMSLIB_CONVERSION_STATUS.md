# GAMSLib Conversion Status Dashboard

**Generated:** 2025-11-21 09:21:55
**Sprint:** Sprint 8
**Total Models:** 10
**Report:** [`gamslib_ingestion_sprint8.json`](../../reports/gamslib_ingestion_sprint8.json)

---

## Overall KPIs

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Parse Rate** | 40.0% (4/10) | ≥10% | ✅ |
| **Convert Rate** | 0.0% (0/4) | ≥50% | ⚠️ Sprint 6: Not implemented |
| **Solve Rate** | 0.0% (N/A) | TBD | ⚠️ Sprint 6: Not implemented |
| **End-to-End** | 0.0% (0/10) | TBD | ⚠️ Sprint 6: Not implemented |

**Sprint 6 Target:** ✅ Parse ≥1 model (≥10% rate) - ✅ MET

---

## Model Status

| Model | Status | Progress | Missing Features | Convert | Solve | E2E |
|-------|--------|----------|------------------|---------|-------|-----|
| circle | ⚠️ PARTIALLY PARSED | 57% (16/28) | parse error | - | - | ❌ |
| himmel16 | 🟡 MOSTLY PARSED | 79% (26/33) | variable attributes (.l, .m, etc.) | - | - | ❌ |
| hs62 | 🟡 MOSTLY PARSED | 83% (15/18) | parse error | - | - | ❌ |
| mathopt1 | ✅ PASS | 100% (20/20) | - | - | - | ❌ |
| maxmin | ⚠️ PARTIALLY PARSED | 40% (19/47) | nested indexing | - | - | ❌ |
| mhw4d | ✅ PASS | 100% (14/14) | - | - | - | ❌ |
| mhw4dx | ⚠️ PARTIALLY PARSED | 51% (27/53) | variable attributes (.l, .m, etc.) | - | - | ❌ |
| mingamma | 🟡 MOSTLY PARSED | 89% (33/37) | parse error | - | - | ❌ |
| rbrock | ✅ PASS | 100% (8/8) | - | - | - | ❌ |
| trig | ✅ PASS | 100% (14/14) | - | - | - | ❌ |

**Legend:**
- ✅ PASS: 100% parsed successfully
- 🟡 MOSTLY PARSED: 75-99% parsed
- ⚠️ PARTIALLY PARSED: 25-74% parsed
- ❌ FAIL: <25% parsed
- `-` Not attempted (stage not implemented yet)

---

## Error Breakdown

### Parse Errors
| Error Type | Count | Models |
|------------|-------|--------|
| `ParseError` | 5 | circle, hs62, maxmin, mhw4dx, mingamma |
| `ParserSemanticError` | 1 | himmel16 |

**Note:** Convert and solve errors will appear here once those stages are implemented.

---

## Failure Details

### circle.gms
**Model:** circle
**Status:** Parse Failed
**Progress:** 57% (16/28 lines parsed)
**Missing Features:** parse error
**Error Type:** `ParseError`
**Error Message:**
```
Error: Parse error at line 40, column 13: Undefined symbol 'i' referenced [context: assignment]
  xmin = smin(i, x(i));
              ^

Suggestion: Declare 'i' as a variable, parameter, or set before using it
```

### himmel16.gms
**Model:** himmel16
**Status:** Parse Failed
**Progress:** 79% (26/33 lines parsed)
**Missing Features:** variable attributes (.l, .m, etc.)
**Error Type:** `ParserSemanticError`
**Error Message:**
```
Conflicting level bound for variable 'x' at indices ('1',) [context: expression] (line 63, column 1)
```

### hs62.gms
**Model:** hs62
**Status:** Parse Failed
**Progress:** 83% (15/18 lines parsed)
**Missing Features:** parse error
**Error Type:** `ParseError`
**Error Message:**
```
Error: Parse error at line 44, column 14: Unexpected character: '-'
  diff   optcr - relative distance from global;
               ^

Suggestion: This character is not valid in this context
```

### maxmin.gms
**Model:** maxmin
**Status:** Parse Failed
**Progress:** 40% (19/47 lines parsed)
**Missing Features:** nested indexing
**Error Type:** `ParseError`
**Error Message:**
```
Error: Parse error at line 51, column 12: Unexpected character: '('
  defdist(low(n,nn))..   dist(low) =e= sqrt(sum(d, sqr(point(n,d) - point(nn,d))));
             ^

Suggestion: This character is not valid in this context
```

### mhw4dx.gms
**Model:** mhw4dx
**Status:** Parse Failed
**Progress:** 51% (27/53 lines parsed)
**Missing Features:** variable attributes (.l, .m, etc.)
**Error Type:** `ParseError`
**Error Message:**
```
Error: Parse error at line 63, column 11: Unexpected character: 'a'
  elseif    abs(m.l-44.02207169) < tol, // local solution
            ^

Suggestion: This character is not valid in this context
```

### mingamma.gms
**Model:** mingamma
**Status:** Parse Failed
**Progress:** 89% (33/37 lines parsed)
**Missing Features:** parse error
**Error Type:** `ParseError`
**Error Message:**
```
Error: Parse error at line 60, column 1: Unexpected character: ')'
  );
  ^

Suggestion: This character is not valid in this context
```

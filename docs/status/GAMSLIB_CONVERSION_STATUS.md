# GAMSLib Conversion Status Dashboard

**Generated:** 2025-11-24 08:14:13
**Sprint:** Sprint 8
**Total Models:** 10
**Report:** [`gamslib_ingestion_sprint8.json`](../../reports/gamslib_ingestion_sprint8.json)

---

## Overall KPIs

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Parse Rate** | 70.0% (7/10) | ≥10% | ✅ |
| **Convert Rate** | 0.0% (0/7) | ≥50% | ⚠️ Sprint 6: Not implemented |
| **Solve Rate** | 0.0% (N/A) | TBD | ⚠️ Sprint 6: Not implemented |
| **End-to-End** | 0.0% (0/10) | TBD | ⚠️ Sprint 6: Not implemented |

**Sprint 6 Target:** ✅ Parse ≥1 model (≥10% rate) - ✅ MET

---

## Model Status

| Model | Status | Progress | Missing Features | Convert | Solve | E2E |
|-------|--------|----------|------------------|---------|-------|-----|
| circle | ⚠️ PARTIALLY PARSED | 57% (16/28) | parse error | - | - | ❌ |
| himmel16 | ✅ PASS | 100% (33/33) | - | - | - | ❌ |
| hs62 | ✅ PASS | 100% (18/18) | - | - | - | ❌ |
| mathopt1 | ✅ PASS | 100% (20/20) | - | - | - | ❌ |
| maxmin | ⚠️ PARTIALLY PARSED | 40% (19/47) | nested indexing | - | - | ❌ |
| mhw4d | ✅ PASS | 100% (14/14) | - | - | - | ❌ |
| mhw4dx | ✅ PASS | 100% (53/53) | - | - | - | ❌ |
| mingamma | ⚠️ PARTIALLY PARSED | 54% (20/37) | parse error | - | - | ❌ |
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
| `ParseError` | 3 | circle, maxmin, mingamma |

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

### mingamma.gms
**Model:** mingamma
**Status:** Parse Failed
**Progress:** 54% (20/37 lines parsed)
**Missing Features:** parse error
**Error Type:** `ParseError`
**Error Message:**
```
Error: Parse error at line 41, column 13: Undefined symbol 'y1opt' referenced [context: assignment]
  y2opt = log(y1opt);
              ^

Suggestion: Declare 'y1opt' as a variable, parameter, or set before using it
```

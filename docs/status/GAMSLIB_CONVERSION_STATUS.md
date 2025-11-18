# GAMSLib Conversion Status Dashboard

**Generated:** 2025-11-18 08:20:13
**Sprint:** Sprint 6
**Total Models:** 10
**Report:** [`gamslib_ingestion_sprint6.json`](../../reports/gamslib_ingestion_sprint6.json)

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

| Model | Parse | Convert | Solve | E2E | Notes |
|-------|-------|---------|-------|-----|-------|
| circle | ❌ | - | - | ❌ | Parse error: ParseError |
| himmel16 | ❌ | - | - | ❌ | Parse error: ParseError |
| hs62 | ❌ | - | - | ❌ | Parse error: ParseError |
| mathopt1 | ✅ | - | - | ❌ | Parsed successfully |
| maxmin | ❌ | - | - | ❌ | Parse error: ParseError |
| mhw4d | ✅ | - | - | ❌ | Parsed successfully |
| mhw4dx | ❌ | - | - | ❌ | Parse error: ParseError |
| mingamma | ❌ | - | - | ❌ | Parse error: ParseError |
| rbrock | ✅ | - | - | ❌ | Parsed successfully |
| trig | ✅ | - | - | ❌ | Parsed successfully |

**Legend:**
- ✅ Success
- ❌ Failed
- `-` Not attempted (stage not implemented yet)

---

## Error Breakdown

### Parse Errors
| Error Type | Count | Models |
|------------|-------|--------|
| `ParseError` | 6 | circle, himmel16, hs62, maxmin, mhw4dx, mingamma |

**Note:** Convert and solve errors will appear here once those stages are implemented.

---

## Failure Details

### circle.gms
**Model:** circle
**Status:** Parse Failed
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
**Error Type:** `ParseError`
**Error Message:**
```
Error: Parse error at line 46, column 39: Unexpected character: '+'
  areadef(i).. area(i) =e= 0.5*(x(i)*y(i++1) - y(i)*x(i++1));
                                        ^

Suggestion: This character is not valid in this context
```

### hs62.gms
**Model:** hs62
**Status:** Parse Failed
**Error Type:** `ParseError`
**Error Message:**
```
Error: Parse error at line 35, column 1: Unexpected character: 'm'
  mx / objdef, eq1x /;
  ^

Suggestion: This character is not valid in this context
```

### maxmin.gms
**Model:** maxmin
**Status:** Parse Failed
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
**Error Type:** `ParseError`
**Error Message:**
```
Error: Parse error at line 26, column 1: Unexpected character: 'm'
  m2 / y2def /;
  ^

Suggestion: This character is not valid in this context
```

# GAMSLib Conversion Status Dashboard

**Generated:** 2025-11-24 13:30:13
**Sprint:** Sprint 8
**Total Models:** 10
**Report:** [`gamslib_ingestion_sprint8.json`](../../reports/gamslib_ingestion_sprint8.json)

---

## Overall KPIs

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Parse Rate** | 90.0% (9/10) | ≥10% | ✅ |
| **Convert Rate** | 0.0% (0/9) | ≥50% | ⚠️ Sprint 6: Not implemented |
| **Solve Rate** | 0.0% (N/A) | TBD | ⚠️ Sprint 6: Not implemented |
| **End-to-End** | 0.0% (0/10) | TBD | ⚠️ Sprint 6: Not implemented |

**Sprint 6 Target:** ✅ Parse ≥1 model (≥10% rate) - ✅ MET

---

## Model Status

| Model | Status | Progress | Missing Features | Convert | Solve | E2E |
|-------|--------|----------|------------------|---------|-------|-----|
| circle | ✅ PASS | 100% (28/28) | - | - | - | ❌ |
| himmel16 | ✅ PASS | 100% (33/33) | - | - | - | ❌ |
| hs62 | ✅ PASS | 100% (18/18) | - | - | - | ❌ |
| mathopt1 | ✅ PASS | 100% (20/20) | - | - | - | ❌ |
| maxmin | ⚠️ PARTIALLY PARSED | 40% (19/47) | nested indexing | - | - | ❌ |
| mhw4d | ✅ PASS | 100% (14/14) | - | - | - | ❌ |
| mhw4dx | ✅ PASS | 100% (53/53) | - | - | - | ❌ |
| mingamma | ✅ PASS | 100% (37/37) | - | - | - | ❌ |
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
| `ParseError` | 1 | maxmin |

**Note:** Convert and solve errors will appear here once those stages are implemented.

---

## Failure Details

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

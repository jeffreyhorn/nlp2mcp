# GAMSLib NLP Benchmark Dashboard (MOCK)

**Sprint:** 6  
**Date:** 2025-11-12 (Day 0 - Mock)  
**Purpose:** Checkpoint 0 Demo Artifact  
**Models:** 10 Tier 1 NLP models from GAMSLIB

---

## Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Total Models** | 10 | ≥ 10 | ✅ Met |
| **Parse Success Rate** | 50% (5/10) | ≥ 10% | ✅ Met |
| **Convert Success Rate** | 80% (4/5) | ≥ 50% | ✅ Met |
| **Solve Success Rate** | 75% (3/4) | Not Required | ℹ️  Bonus |
| **End-to-End Success** | 30% (3/10) | - | ℹ️ Tracking |

---

## Model Results

| Model | Parse | Convert | Solve | Error Category | Notes |
|-------|-------|---------|-------|----------------|-------|
| trig | ✅ | ✅ | ✅ | - | Success |
| rbrock | ✅ | ✅ | ✅ | - | Success |
| himmel16 | ✅ | ✅ | ✅ | - | Success |
| hs62 | ✅ | ✅ | ❌ | SOLVER_ERROR | PATH numerics |
| mhw4d | ✅ | ❌ | - | UNSUPPORTED_EXPR | Complex function |
| mhw4dx | ❌ | - | - | INDEXED_OPERATION | Sum over set |
| circle | ❌ | - | - | INDEXED_OPERATION | Lead/lag operators |
| maxmin | ❌ | - | - | DOLLAR_CONDITION | $if statement |
| mathopt1 | ❌ | - | - | SYNTAX_ERROR | Unrecognized token |
| mingamma | ❌ | - | - | ATTRIBUTE_NOT_SUPPORTED | .l attribute |

---

## Error Breakdown

### Parse Errors (5 models, 50% failure rate)

| Category | Count | Models Affected | Priority |
|----------|-------|-----------------|----------|
| INDEXED_OPERATION | 2 | mhw4dx, circle | High |
| DOLLAR_CONDITION | 1 | maxmin | Medium |
| ATTRIBUTE_NOT_SUPPORTED | 1 | mingamma | High |
| SYNTAX_ERROR | 1 | mathopt1 | Medium |

**Top Priority for Sprint 7:** Indexed operations (sum, prod) and attributes (.l, .m)

### Conversion Errors (1 model, 20% failure rate of parsed)

| Category | Count | Models Affected | Priority |
|----------|-------|-----------------|----------|
| UNSUPPORTED_EXPR | 1 | mhw4d | Medium |

**Notes:** mhw4d uses complex mathematical function not yet in AD system

### Solve Errors (1 model, 25% failure rate of converted)

| Category | Count | Models Affected | Priority |
|----------|-------|-----------------|----------|
| SOLVER_ERROR | 1 | hs62 | Low |

**Notes:** PATH numerical issues, not nlp2mcp bug

---

## Detailed Failure Information

### mhw4dx (Parse Failure)

**Error:** INDEXED_OPERATION

**Details:**
```
Line 15: sum(i, x(i)*y(i)) =e= 10;
```

**Cause:** Parser does not support indexed summation syntax

**Fix Required:** Implement sum/prod operators in parser (Sprint 7)

---

### circle (Parse Failure)

**Error:** INDEXED_OPERATION  

**Details:**
```
Line 22: x(t+1) =e= x(t) + delta;
```

**Cause:** Lead/lag operators (t+1, t-1) not supported

**Fix Required:** Add lead/lag operator support (Sprint 7)

---

### maxmin (Parse Failure)

**Error:** DOLLAR_CONDITION

**Details:**
```
Line 5: $if not declared points $abort "Points set required"
```

**Cause:** Preprocessor directives not supported

**Fix Required:** Implement basic $if/$set support or skip with warning (Sprint 7)

---

### mathopt1 (Parse Failure)

**Error:** SYNTAX_ERROR

**Details:**
```
Line 18: obj =e= sqr(x-2) + sqr(y-3)**2;
```

**Cause:** Parser confused by double exponent (likely missing parens)

**Fix Required:** Improve error recovery, suggest fix (Sprint 7 UX)

---

### mingamma (Parse Failure)

**Error:** ATTRIBUTE_NOT_SUPPORTED

**Details:**
```
Line 25: if (x.l > 0) then ...
```

**Cause:** Variable attributes (.l, .m, .lo, .up) in expressions not supported

**Fix Required:** Parse attributes as metadata, strip in expressions (Sprint 7)

---

### mhw4d (Conversion Failure)

**Error:** UNSUPPORTED_EXPR

**Details:**
```
Line 30: f =e= gamma(x) + lgamma(y);
```

**Cause:** gamma() and lgamma() not in AD function library

**Fix Required:** Add special functions to AD system (Sprint 7)

---

### hs62 (Solve Failure)

**Error:** SOLVER_ERROR

**Details:**
```
PATH termination: Numerical difficulties
```

**Cause:** Model has poor scaling or conditioning

**Fix Required:** None (PATH limitation, not nlp2mcp bug). User can try different solver or add scaling.

---

## Progress Tracking

### Sprint-over-Sprint

| Sprint | Total | Parse% | Convert% | Solve% | E2E% |
|--------|-------|--------|----------|--------|------|
| 6 (Mock) | 10 | 50% | 80% | 75% | 30% |
| 7 (Target) | 15 | 70% | 85% | 70% | 42% |
| 8 (Target) | 20 | 80% | 90% | 75% | 54% |

**Improvement Plan:**
- Sprint 7: Add indexed operations, attributes → expect +20% parse rate
- Sprint 8: Add special functions, improve error recovery → expect +10% parse rate

---

## Notes

### This is a MOCK Dashboard

This dashboard is created as part of **Sprint 6 Day 0: Pre-Sprint Research & Setup** to demonstrate the proposed layout and KPI format.

**Status:** Demo artifact for Checkpoint 0

**Actual Data:** This uses hypothetical results. Real data will be generated on Sprint 6 Day 5-6 when the ingestion script runs on actual GAMSLib models.

**Purpose:** Validates dashboard design before implementation (Unknown 3.4 resolution)

---

## Implementation Checklist

For Day 6 implementation:

- [x] KPI summary table format defined
- [x] Model results table format defined
- [x] Error breakdown by category format defined
- [x] Detailed failure information format defined
- [x] Progress tracking table format defined
- [x] Unicode emoji scheme (✅/❌/ℹ️/⚠️/-) chosen
- [x] Markdown rendering verified in GitHub
- [ ] Python generator script implemented (Day 6)
- [ ] JSON input format finalized (Day 5)
- [ ] Integration with ingestion script (Day 6)

---

## References

- Unknown 3.4 Resolution: `docs/research/dashboard_design.md`
- Unknown 3.5 Resolution: `docs/research/gamslib_kpi_definitions.md`
- Unknown 3.3 Resolution: `docs/research/gamslib_parse_errors_preliminary.md`
- KPI Targets: Sprint 6 PLAN.md, Day 5 tasks
- Dashboard Generator: To be implemented Day 6

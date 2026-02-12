# Fix Roadmap for Sprint 19+

**Created:** 2026-02-12 (Sprint 18 Day 11)
**Purpose:** Prioritize remaining fixes based on ROI (models fixed / effort)

---

## Executive Summary

Sprint 18 reduced path_syntax_error from 22 to 8 models. The remaining 8 models (7 architectural + 1 excluded) require parser or KKT generation changes that were beyond Sprint 18 scope.

**Recommended Sprint 19 Focus:** Cross-indexed sums (ISSUE_670) - highest ROI with 6 models blocked.

---

## Priority 1: Cross-Indexed Sums (ISSUE_670)

**Models Affected:** abel, qabel, chenery, mexss, orani, robert (partial)
**Count:** 6 models
**Error:** GAMS Error 149 "Uncontrolled set entered as constant"
**Effort:** High (8-16 hours)
**ROI:** High (6 models / high effort = best ratio)

### Problem Description

When differentiating constraints with sums over indices not in the equation domain, the KKT stationarity equations contain uncontrolled set references.

**Example (abel):**
```gams
* Original constraint:
e(k).. sum(np, a(n,np)*x(np,k)) =E= b(k);

* Stationarity equation (problematic):
stat_x(i,k).. sum(np, ...) + lam_e(k)*a(n,np) = 0;
*                                    ^^^ 'n' not controlled in stat_x domain
```

### Proposed Solution

Modify KKT stationarity builder to:
1. Detect cross-indexed terms in differentiated expressions
2. Wrap uncontrolled indices in appropriate sum expressions
3. Ensure all stationarity equation indices are properly scoped

### Implementation Tasks

1. [ ] Analyze KKT stationarity equation generation in `src/kkt/stationarity.py` and related KKT assembly modules (e.g., `src/kkt/assemble.py`)
2. [ ] Identify where cross-indexed sums create uncontrolled indices
3. [ ] Design index scoping mechanism for stationarity equations
4. [ ] Implement fix with comprehensive test coverage
5. [ ] Validate on all 6 affected models

---

## Priority 2: Table Parsing - Continuation Syntax (ISSUE_392)

**Models Affected:** like
**Count:** 1 model
**Error:** GAMS Error 170 "Domain violation for element"
**Effort:** Medium (2-4 hours)
**ROI:** Low (1 model / medium effort)

### Problem Description

Tables with `+` continuation syntax are not fully parsed. The grammar rule exists but the semantic handler doesn't properly capture data from continuation rows.

**Example (like):**
```gams
Table data(*,i) 'systolic blood pressure data'
                 1   2   3   4   5   ...  15
   pressure     95 105 110 115 120  ... 170
   frequency     1   1   4   4  15  ...  17
   +            16  17  18  19  20  ...  31   <- continuation not parsed
   pressure    175 180 185 190 195  ... 260
   frequency     8   6   6   7   4  ...   2;
```

Only 4 of 62 values are captured (93.5% data loss).

### Proposed Solution

Modify table parsing semantic handler to:
1. Detect `+` continuation marker
2. Extend column indices from previous row
3. Continue adding data to existing row labels

### Implementation Tasks

1. [ ] Review grammar rule for table continuation in `src/gams/gams_grammar.lark`
2. [ ] Update semantic handler in `src/ir/parser.py` to process continuation
3. [ ] Add unit tests for table continuation parsing
4. [ ] Validate on `like` model

---

## Priority 3: Table Parsing - Description as Header (ISSUE_399)

**Models Affected:** robert
**Count:** 1 model
**Error:** GAMS Error 170 "Domain violation for element"
**Effort:** Medium (2-4 hours)
**ROI:** Low (1 model / medium effort)

### Problem Description

Table descriptions are incorrectly parsed as column headers.

**Example (robert):**
```gams
Table c(p,t) 'expected profits'   <- 'expected profits' treated as header
          1    2    3
low      25   20   10
medium   50   50   50
high     75   80  100
```

Only 4 of 9 values are captured (55% data loss).

### Proposed Solution

Modify table parsing to:
1. Distinguish quoted descriptions from column headers
2. Only treat unquoted identifiers/numbers as column headers
3. Skip description strings in header row processing

### Implementation Tasks

1. [ ] Analyze table header parsing logic in `src/ir/parser.py`
2. [ ] Add check to skip quoted strings as column headers
3. [ ] Add unit tests for table with description
4. [ ] Validate on `robert` model

---

## Priority 4: MCP Pairing Issues (ISSUE_672)

**Models Affected:** alkyl, bearing
**Count:** 2 models
**Error:** MCP pair has empty equation but variable is NOT fixed
**Effort:** Medium (4-6 hours)
**ROI:** Medium (2 models / medium effort)

### Problem Description

Certain bound structures produce invalid MCP pairings where equations are empty but corresponding variables are not fixed.

### Proposed Solution

Review MCP pairing logic in `src/kkt/partition.py` to handle edge cases with bounds.

### Implementation Tasks

1. [ ] Analyze MCP pairing failures in alkyl, bearing
2. [ ] Identify bound configurations causing empty equations
3. [ ] Fix pairing logic to handle these cases
4. [ ] Validate on affected models

---

## Priority 5: PATH Solver Terminated (Investigation)

**Models Affected:** 20 models
**Error:** PATH solver fails (numerical/feasibility)
**Effort:** High (ongoing investigation)
**ROI:** Variable (may be model-specific issues)

### Models

cpack, dispatch, hansmcp, house, jobt, meanvar, mhw4d, oligomcp, port, process, ps1, ps2_s, ps3_f, ps3_s, ps3_s_gic, ps3_s_mn, scarfssa, traffic, transeq, two3mcp

### Investigation Approach

1. Group by error type (infeasible, iteration limit, etc.)
2. Compare MCP formulation to original NLP
3. Check variable bounds and initialization
4. Identify patterns in failing models

---

## Effort Summary

| Priority | Issue | Models | Effort | Sprint 19 Recommendation |
|----------|-------|--------|--------|--------------------------|
| P1 | Cross-indexed sums | 6 | 8-16h | **Primary focus** |
| P2 | Table continuation | 1 | 2-4h | If time permits |
| P3 | Table description | 1 | 2-4h | If time permits |
| P4 | MCP pairing | 2 | 4-6h | Secondary focus |
| P5 | PATH terminated | 20 | High | Investigation only |

---

## Sprint 19 Recommended Plan

### Week 1: Cross-Indexed Sums (ISSUE_670)
- Days 1-2: Analysis and design
- Days 3-4: Implementation
- Day 5: Testing on all 6 models

### Week 2: Table Parsing + MCP Pairing
- Days 1-2: ISSUE_392 (table continuation)
- Days 3-4: ISSUE_399 (table description) or ISSUE_672 (MCP pairing)
- Day 5: Integration testing and documentation

### Expected Outcomes

If all P1-P4 items are completed:
- path_syntax_error: 8 → 0 (all remaining are architectural, now fixed)
- Additional solving models: potentially +10 (6 from ISSUE_670 + 2 from table + 2 from MCP)
- Note: Some models may still have path_solve_terminated issues

---

## Architectural Debt Deferred

These items were identified but intentionally deferred:

1. **Parser improvements for Parse target (80+)**: Table data blocks, computed parameters, put/display statements were original Sprint 18 goals but deprioritized for emission fixes.

2. **Action=C compile-only mode**: Not implemented in Sprint 18.

3. **Lexer improvements**: `lexer_invalid_char` affects ~70 models but requires grammar extensions.

---

*Roadmap created based on Sprint 18 findings. Priorities should be reassessed at Sprint 19 planning.*

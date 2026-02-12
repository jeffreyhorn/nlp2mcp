# GAMSLIB Pipeline Status Report

**Generated:** 2026-02-12 (Sprint 18 Final)
**nlp2mcp Version:** 1.1.0
**Data Source:** Sprint 18 Day 10 pipeline retest

---

## Executive Summary

The nlp2mcp pipeline was tested against **159** GAMSLIB models on **2026-02-11** (Sprint 18 Day 10).

- **Full Pipeline Success:** 7 models (4.4%)
- **Parse Success:** 61/159 (38.4%)
- **Translate Success:** 48/61 (78.7%)
- **Solve Success:** 20/48 (41.7%)

**Key Bottleneck:** Parse stage (38.4% success rate)

**Sprint 18 Improvements:**
- Solve: 13 → 20 models (+7)
- path_syntax_error: 22 → 7 (-15, excluding mingamma)
- Full Pipeline: 4 → 7 models (+3)

---

## Pipeline Stage Summary

| Stage             | Attempted   | Success   | Failure   | Success Rate   |
|-------------------|-------------|-----------|-----------|----------------|
| Parse             | 159         | 61        | 98        | 38.4%          |
| Translate         | 61          | 48        | 13        | 78.7%          |
| Solve             | 48          | 20        | 28        | 41.7%          |
| Compare           | 13          | 7         | 6         | 53.8%          |
| **Full Pipeline** | **159**     | **7**     | **152**   | **4.4%**       |

*Note: 1 model (mingamma) excluded from testing - GAMS lacks required psi function.*

---

## Solve Stage Failure Breakdown

| Category | Count | Description |
|----------|-------|-------------|
| path_solve_terminated | 20 | PATH solver fails (numerical/feasibility) |
| path_syntax_error | 7 | GAMS compilation errors (architectural) |

*Note: mingamma is excluded from counts above (GAMS lacks psi function).*

### Path Syntax Error Details (7 architectural models + 1 excluded)

| Model | Error | Root Cause | Status |
|-------|-------|------------|--------|
| abel | E149 | Cross-indexed sums | ARCHITECTURAL |
| qabel | E149 | Cross-indexed sums | ARCHITECTURAL |
| chenery | E149 | Cross-indexed sums | ARCHITECTURAL |
| mexss | E149 | Cross-indexed sums | ARCHITECTURAL |
| orani | E149 | Cross-indexed sums | ARCHITECTURAL |
| robert | E170 | Table parsing + cross-indexed sums | ARCHITECTURAL |
| like | E170 | Table continuation parsing | ARCHITECTURAL |
| mingamma | E140 | GAMS lacks psi function | EXCLUDED |

**Note:** All 7 remaining path_syntax_error models require architectural changes (parser or KKT generation). See [docs/issues/](../issues/) for details.

---

## Successful Models

The following **7** models complete the full pipeline successfully (solution matches original):

1. **blend** (new in Sprint 18)
2. **himmel11**
3. **hs62**
4. **mathopt1**
5. **mathopt2**
6. **rbrock**
7. **simple_nlp**

### Models That Solve (20 total)

Models that successfully compile and solve (may have solution mismatch):

| Model | Status | Notes |
|-------|--------|-------|
| blend | match | Fixed in Sprint 18 Day 7 |
| chem | mismatch | Fixed in Sprint 18 Day 3 (P5) |
| demo1 | mismatch | Fixed in Sprint 18 Day 2 (P1) |
| fdesign | mismatch | |
| harker | mismatch | |
| himmel11 | match | |
| himmel16 | not_compared | Fixed in Sprint 18 Day 2 (P3) |
| hs62 | match | |
| mathopt1 | match | |
| mathopt2 | match | |
| pak | not_compared | |
| pollut | not_compared | Fixed in Sprint 18 Day 2 (P1) |
| rbrock | match | |
| sample | not_compared | Fixed in Sprint 18 Day 7 |
| scarfmcp | not_compared | |
| simple_nlp | match | |
| transmcp | not_compared | |
| wall | not_compared | |
| wallmcp | mismatch | |
| weapons | mismatch | |

---

## Top Blockers

| Rank | Error Category | Count | Stage | Notes |
|------|----------------|-------|-------|-------|
| 1 | `lexer_invalid_char` | ~70 | parse | Unsupported GAMS syntax |
| 2 | `internal_error` | ~20 | parse | Parser edge cases |
| 3 | `path_solve_terminated` | 20 | solve | Numerical/feasibility issues |
| 4 | `path_syntax_error` | 7 | solve | All architectural |
| 5 | `translate_error` | 13 | translate | Various translation issues |

*Parse-stage counts (`lexer_invalid_char`, `internal_error`) are approximated from Sprint 18 Day 10 pipeline logs; other counts are exact from the 159-model run.*

---

## Architectural Limitations Discovered (Sprint 18)

### 1. Cross-Indexed Sums (ISSUE_670) - 6 models
Sums over indices not in equation domain produce "uncontrolled set as constant" errors in stationarity equations. Requires KKT assembly changes.

**Affected models:** abel, qabel, chenery, mexss, orani, robert (partial)

### 2. Table Parsing Limitations - 2 models
- **ISSUE_392**: Table `+` continuation syntax not fully parsed (like)
- **ISSUE_399**: Table description parsed as column header (robert)

### 3. MCP Pairing Issues (ISSUE_672) - 2 models
Complementarity pair inconsistencies for certain bound structures.

**Affected models:** alkyl, bearing

---

## Sprint History

| Sprint | Date | Parse | Translate | Solve | Full Pipeline |
|--------|------|-------|-----------|-------|---------------|
| 16 | 2026-01-28 | 48 (30.0%) | 21 (43.8%) | 11 (52.4%) | 5 (3.1%) |
| 17 | 2026-02-07 | 62 (38.8%) | 50 (80.7%) | 13 (26.0%) | 4 (2.5%) |
| **18** | **2026-02-11** | **61 (38.4%)** | **48 (78.7%)** | **20 (41.7%)** | **7 (4.4%)** |

---

## Recommended Focus for Sprint 19

1. **Cross-indexed sums (ISSUE_670)**: High ROI - 6 models blocked
2. **Table parsing (ISSUE_392, ISSUE_399)**: Medium effort - 2 models blocked
3. **MCP pairing (ISSUE_672)**: Medium effort - 2 models blocked
4. **path_solve_terminated investigation**: Lower priority - numerical issues

See `docs/planning/EPIC_4/SPRINT_18/FIX_ROADMAP.md` for detailed prioritization.

---

*Report updated for Sprint 18 completion.*

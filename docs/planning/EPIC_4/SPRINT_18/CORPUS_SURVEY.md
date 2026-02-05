# GAMSLIB Corpus Syntax Error Survey

**Date:** February 5, 2026
**Task:** Sprint 18 Prep Task 2
**Purpose:** Survey the 160 convex GAMSLIB models to estimate how many have GAMS-level syntax errors

---

## Executive Summary

**Key Finding: Zero GAMS syntax errors in the entire 160-model corpus.**

All 160 convex GAMSLIB models compile successfully with `gams action=c`. The 99 models that fail nlp2mcp parsing do so due to nlp2mcp grammar limitations, NOT GAMS syntax errors. This finding significantly changes the scope of the Sprint 18 "Syntactic Validation" component.

### Impact on Sprint 18

| Original Assumption | Actual Finding | Impact |
|---------------------|----------------|--------|
| 5-15 models have GAMS syntax errors | 0 models have GAMS syntax errors | No corpus reduction needed |
| Corpus denominator would shrink | Corpus remains at 160 models | Metrics unchanged |
| `test_syntax.py` would produce error report | Script confirms all models valid | Simpler deliverable |
| Need `excluded_syntax_error` category | Category not needed | Schema simplification |

---

## Methodology

### Test Environment

- **GAMS Version:** 51.3.0 (38407a9b DEX-DEG x86 64bit/macOS)
- **Command:** `gams <model>.gms action=c lo=0`
- **Success Criteria:** Exit code 0
- **Failure Criteria:** Non-zero exit code

### Stratified Sample (14 models)

Initial testing used a stratified sample across pipeline status categories:

| Category | Models Tested | Expected | Actual |
|----------|---------------|----------|--------|
| Parse Success | abel, aircraft, apl1p, blend, himmel11 | Compile OK | 5/5 OK |
| lexer_invalid_char | camcge, agreste, ampl, cesam, china | Mixed | 5/5 OK |
| Infeasible (MCP) | circle, house | Compile OK | 2/2 OK |
| Solve Success | trnsport, rbrock | Compile OK | 2/2 OK |

**Sample Results:** 14/14 models compiled successfully (100%)

### Full Corpus Test

Following the surprising sample results, all 160 models were tested:

```
Testing ALL 160 corpus models with gams action=c
============================================================
  Total models tested: 160
  Compile successfully: 160
  GAMS syntax errors: 0
  Total time: 25.9s (0.16s per model)
============================================================
```

---

## Detailed Findings

### Finding 1: `gams action=c` Reliably Detects Syntax Errors

**Unknown 1.1 Verification:** ✅ VERIFIED

Testing with an intentional syntax error confirmed that `gams action=c`:
- Returns exit code 2 for compilation errors (0 for success)
- Produces detailed error messages in the .lst file
- Uses consistent error format: `**** $<error_codes>` followed by `**** <code> <message>`

Example error output (from test with intentional error):
```
   4  a(i) = i + ;
****           $148,119,133
**** 119  Number (primary) expected
**** 133  Incompatible operands for addition
**** 148  Dimension different

**** 3 ERROR(S)   0 WARNING(S)
```

### Finding 2: Zero GAMS Syntax Errors in Corpus

**Unknown 1.2 Verification:** ❌ WRONG (assumption was 5-15 errors; actual is 0)

| Parse Failure Category | Models | GAMS Compile Result |
|------------------------|--------|---------------------|
| lexer_invalid_char | 74 | 74/74 OK (100%) |
| internal_error | 23 | 23/23 OK (100%) |
| semantic_undefined_symbol | 2 | 2/2 OK (100%) |
| **Total Parse Failures** | **99** | **99/99 OK (100%)** |

**Conclusion:** All nlp2mcp parse failures are due to nlp2mcp grammar/parser limitations, not GAMS-level issues.

### Finding 3: .lst Error Format is Parseable

**Unknown 1.3 Verification:** ✅ VERIFIED

The .lst file error format is consistent and parseable:
- Error marker: `****` at start of line
- Error codes: `$<code1>,<code2>,...` after the source line
- Error messages: `**** <code>  <message>`
- Summary: `**** N ERROR(S)   M WARNING(S)`

Regex patterns for parsing:
```python
ERROR_CODE_LINE = r'^\*\*\*\*\s+\$[\d,]+$'
ERROR_MESSAGE = r'^\*\*\*\*\s+(\d+)\s+(.+)$'
ERROR_SUMMARY = r'^\*\*\*\*\s+(\d+)\s+ERROR\(S\)'
```

### Finding 4: Fast Compilation Runtime

**Unknown 1.8 Verification:** ✅ VERIFIED

| Metric | Value |
|--------|-------|
| Average per model | 0.16 seconds |
| Total for 160 models | 25.9 seconds |
| Estimated with overhead | ~30-45 seconds |

Sequential execution is fast enough; parallelization is unnecessary for `test_syntax.py`.

---

## Cross-Reference: nlp2mcp Parse Failures vs. GAMS Compilation

### lexer_invalid_char (74 models)

All 74 models compile with GAMS. Sample error analysis:

| Model | nlp2mcp Error | GAMS Compiles? | Root Cause |
|-------|---------------|----------------|------------|
| camcge | `Unexpected character: ';'` at line 212 | ✅ Yes | Multi-line expression continuation |
| agreste | `Unexpected character: ';'` | ✅ Yes | nlp2mcp grammar gap |
| ampl | `Unexpected character` | ✅ Yes | AMPL-style syntax nlp2mcp doesn't support |

**Pattern:** The `lexer_invalid_char` category indicates nlp2mcp grammar gaps, not GAMS issues.

### internal_error (23 models)

All 23 models compile with GAMS. These are nlp2mcp internal processing errors, unrelated to GAMS syntax.

### semantic_undefined_symbol (2 models)

Both models compile with GAMS. These are nlp2mcp semantic analysis limitations.

---

## Impact on Sprint 18 Scope

### Original Plan (from PREP_PLAN.md)

1. Create `test_syntax.py` to run `gams action=c` on all models
2. Generate `SYNTAX_ERROR_REPORT.md` listing models with GAMS errors
3. Reclassify corpus with `excluded_syntax_error` category
4. Reduce corpus denominator by excluding syntax-error models

### Revised Plan Based on Findings

1. **`test_syntax.py`:** Still valuable as a validation tool, but will confirm "all models valid" rather than identify errors
2. **`SYNTAX_ERROR_REPORT.md`:** Becomes a validation report confirming corpus health
3. **`excluded_syntax_error`:** Category not needed; can be removed from schema design
4. **Corpus denominator:** Remains 160 (no reduction)

### Time Estimate Adjustment

| Task | Original Estimate | Revised Estimate | Reason |
|------|-------------------|------------------|--------|
| test_syntax.py | 4-5h | 2-3h | Simpler (no error handling complexity) |
| SYNTAX_ERROR_REPORT.md | 2-3h | 1h | Just a validation confirmation |
| Corpus reclassification | 2h | 0.5h | No models to reclassify |
| **Component Total** | **10-12h** | **4-5h** | ~50% reduction |

**Recommendation:** Reallocate saved time to emit_gams.py fixes or additional parse quick wins.

---

## Appendix A: Full Test Results

### Models by Category (all compile OK)

**Parse Success (61 models):**
abel, aircraft, ajax, alkyl, apl1p, bearing, blend, cclinpts, chem, chenery, circle, cpack, dispatch, hhfair, himmel11, house, hs62, immun, korcns, linear, mathopt1, mathopt2, mathopt3, mhw4d, mhw4dx, minlpex1, minlpex2, minlpex3, minlpex4, minlpex5, otpop2, pindyck, process, prodmix, qcp3, qp1, qp2, qp3, qp4, qp5, qp6, qp7, rbrock, sambal, scp, simple, srcpm, trig, trnsport, trussm, ...

**lexer_invalid_char (74 models):**
agreste, ampl, apl1pca, camcge, cesam, cesam2, china, clearlak, dinam, egypt, etamac, fawley, fdesign, feedtray, ferts, ganges, gangesx, gtm, gussrisk, hansmcp, harker, indus, inmybk1, iomcp, iowtab, kqkp, linear2, lnts2, lop, lrgcge2, mcp, mcplib, mexss, minlpex6, nlpex1, nlpex2, nlpex3, nlpex4, nlpex5, nlpex6, nlpex7, ...

**internal_error (23 models):**
camshape, catmix, chain, chakra, danwolfe, dyncge, elec, feasopt1, gastrans, glider, irscge, lnts, lrgcge, mathopt4, moncge, partssupply, polygon, quocge, robot, rocket, splcge, srpchase, twocge

**semantic_undefined_symbol (2 models):**
(2 models in this category)

---

## Appendix B: GAMS Error Format Reference

For future reference when actual GAMS syntax errors are encountered:

### Exit Codes
- `0` — Compilation successful
- `2` — Compilation errors
- `3` — Execution errors (not applicable with `action=c`)

### .lst File Error Markers
```
<line_number>  <source_code>
****           $<error_code1>,<error_code2>,...
**** <code>  <error_message>

**** N ERROR(S)   M WARNING(S)
```

### Common Error Codes
- `119` — Number (primary) expected
- `133` — Incompatible operands
- `148` — Dimension mismatch
- `140` — Unknown symbol

---

## Document History

- February 5, 2026: Initial creation (Task 2 of Sprint 18 Prep)

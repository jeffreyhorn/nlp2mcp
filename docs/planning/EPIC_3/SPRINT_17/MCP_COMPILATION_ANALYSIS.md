# Sprint 17 MCP Compilation Analysis

**Created:** January 28, 2026  
**Sprint:** 17 Prep - Task 4  
**Status:** Complete  
**Purpose:** Detailed analysis of 8 path_syntax_error models to identify MCP compilation failures

---

## Executive Summary

This document analyzes all 8 models that successfully translate to MCP but fail GAMS compilation. These models are "almost there" - fixing these errors directly adds to solve success.

**Models Analyzed:**
| Model | Type | GAMS Error Code | Root Cause Category |
|-------|------|-----------------|---------------------|
| ajax | LP | 66, 256 | Missing Table data |
| chem | NLP | 66, 70, 256 | Missing computed parameter + dimension mismatch |
| dispatch | NLP | 171, 257 | Subset not declared as subset |
| least | NLP | 66, 256 | Missing Table data |
| port | LP | 171, 257 | Subset not declared as subset |
| ps2_f_inf | NLP | 145, 148, 257 | Reserved word `inf` as set element |
| sample | NLP | 120, 149, 171, 340, 257 | Unquoted set element references |
| trnsport | LP | 66, 256 | Missing computed parameter |

**Error Pattern Summary:**
| Pattern | Models | Effort | Description |
|---------|--------|--------|-------------|
| Missing Table data | 2 | 6h | ajax, least |
| Missing computed parameter data | 2 | 4h | chem, trnsport |
| Subset relationship lost | 2 | 4h | dispatch, port |
| Reserved word as set element | 1 | 2h | ps2_f_inf |
| Unquoted set element references | 1 | 3h | sample |

**Total Estimated Fix Effort:** ~19h for +8 models

---

## Table of Contents

1. [Error Category Analysis](#1-error-category-analysis)
2. [Model-Level Details](#2-model-level-details)
3. [Root Cause Summary](#3-root-cause-summary)
4. [Proposed Fixes](#4-proposed-fixes)
5. [Priority Ordering](#5-priority-ordering)
6. [Appendices](#appendices)

---

## 1. Error Category Analysis

### 1.1 GAMS Error 66: Symbol Not Defined or Assigned (4 models)

**Error Message:**
```
****  66  The symbol shown has not been defined or assigned
```

**Affected Models:** ajax, chem, least, trnsport

**Root Cause:** Parameters are declared but their data values are not emitted. This happens in two scenarios:

1. **Table data not emitted:** Parameters defined via `Table` statements have their declaration emitted but not their data values.
2. **Computed parameters not emitted:** Parameters with assignment statements (e.g., `c(i,j) = f*d(i,j)/1000;`) are declared but the assignment is missing.

**Code Location:** `src/emit/original_symbols.py` lines 130-185

**Evidence:**

*ajax - Table data missing:*
```gams
* Original GAMS:
Table prate(g,m) 'production rate (tons per hour)'
             machine-1  machine-2  machine-3
  20-            1.75       2.5        2.
  25-            1.8        3.        2.
  c-bond-ext     3.         4.        2.8
  tissue-wrp     1.5        1.75      1.75 ;

* Generated MCP (data missing):
Parameters
    prate(g,m)
    pcost(g,m)
```

*trnsport - Computed parameter missing:*
```gams
* Original GAMS:
Parameter c(i,j) 'transport cost in thousands of dollars per case';
c(i,j) = f*d(i,j)/1000;

* Generated MCP (assignment missing):
Parameters
    c(i,j)
;
Scalars
    f /0.0/   * Should be 90, scalar value also wrong
;
```

---

### 1.2 GAMS Error 171: Domain Violation for Set (2 models)

**Error Message:**
```
**** 171  Domain violation for set
```

**Affected Models:** dispatch, port

**Root Cause:** Subset relationships are lost during emission. When a set is declared as a subset of another (e.g., `cg(genchar)` or `g(b)`), the generated code emits them as independent sets, losing the domain relationship.

**Code Location:** `src/emit/original_symbols.py` lines 63-89 (emit_original_sets)

**Evidence:**

*dispatch - Subset relationship lost:*
```gams
* Original GAMS:
Set genchar     'generator characteristics' / a, b, c, upplim, lowlim /
    cg(genchar) 'cost categories'           / a, b, c /;

* Generated MCP (subset relationship lost):
Sets
    genchar /a, b, c, upplim, lowlim/
    cg /a, b, c/   * Missing (genchar) subset declaration
;

* Error in equation:
costfn.. cost =E= sum((i,cg), gendata(i,cg) * power(p(i), pexp(cg)));
*                                        ^^^ cg used to index gendata(i,genchar)
```

*port - Same pattern:*
```gams
* Original GAMS:
Set b    'bonds'    / municip-a, municip-b, corporate, us-ser-e, us-ser-f /
    g(b) 'grouping' / corporate, us-ser-e,  us-ser-f /;

* Generated MCP:
Sets
    b /municip-a, municip-b, corporate, us-ser-e, us-ser-f/
    g /corporate, us-ser-e, us-ser-f/   * Missing (b) subset declaration
;

* Error in equation:
comp_groupmin.. sum(g, investment(g)) =G= 0;
*                                  ^^^ investment declared as (b), not (g)
```

---

### 1.3 GAMS Error 145/148: Reserved Word as Set Element (1 model)

**Error Message:**
```
**** 145  Set identifier or quoted element expected
**** 148  Dimension different - The symbol is referenced with more/less indices as declared
```

**Affected Model:** ps2_f_inf

**Root Cause:** The set element `inf` is a GAMS reserved word representing positive infinity. When used as a set element, it must be quoted as `'inf'`.

**Code Location:** `src/emit/original_symbols.py` lines 63-89 and `src/emit/expr_to_gams.py`

**Evidence:**

```gams
* Original GAMS:
Set i 'type of supplier' / inf /;
Parameter theta(i) 'efficiency' / inf 0.3 /;

* Generated MCP (reserved word not quoted):
Sets
    i /inf/   * Should be /'inf'/
;
Parameters
    theta(i) /inf 0.3/   * Should be /'inf' 0.3/
;

* Error in stationarity equations:
stat_util.. ... + 0 * nu_rev(inf) + 0 * nu_pc(inf) =E= 0;
*                          ^^^ GAMS interprets as positive infinity, not set element
```

---

### 1.4 GAMS Error 120/149/340: Unquoted Set Element References (1 model)

**Error Message:**
```
**** 120  Unknown identifier entered as set
**** 149  Uncontrolled set entered as constant
**** 340  A label/element with the same name exist. You may have forgotten to quote a label/element reference.
```

**Affected Model:** sample

**Root Cause:** Set elements used in expressions are emitted without quotes. GAMS requires set element references to be quoted (e.g., `'a'` not `a`) when used in contexts where they could be confused with identifiers.

**Code Location:** `src/emit/expr_to_gams.py` - expression emission for set element references

**Evidence:**

```gams
* Original model set:
Set j 'variate' / a, b /;

* Generated stationarity equation (unquoted element references):
stat_n_1.. ... - ((-1) * k1("1",a)) / n("1") ** 2 * lam_vbal(a) - ((-1) * k1("1",b)) / n("1") ** 2 * lam_vbal(b) ...
*                         ^                        ^                        ^                        ^
* Should be:
stat_n_1.. ... - ((-1) * k1("1",'a')) / n("1") ** 2 * lam_vbal('a') - ((-1) * k1("1",'b')) / n("1") ** 2 * lam_vbal('b') ...
```

---

### 1.5 GAMS Error 70: Dimension Mismatch (1 model)

**Error Message:**
```
****  70  The dimensions of the equ.var pair do not conform
```

**Affected Model:** chem (secondary error)

**Root Cause:** In addition to missing computed parameter `gplus`, the model has dimension mismatches in MCP complementarity pairs. This is likely a consequence of the primary error (missing parameter) rather than a separate issue.

---

## 2. Model-Level Details

### ajax (LP)

**GAMS Errors:**
```
****  66 equation stat_outp.. symbol "pcost" has no values assigned
****  66 equation stat_outp.. symbol "prate" has no values assigned
```

**Missing Data:**
- `prate(g,m)` - Table data (production rates)
- `pcost(g,m)` - Table data (production costs)

**Fix:** Emit Table data in `emit_original_parameters()`

---

### chem (NLP)

**GAMS Errors:**
```
****  66 equation stat_x_H.. symbol "gplus" has no values assigned
****  70 x dimensions are different (10 occurrences)
```

**Missing Data:**
- `gplus(c)` - Computed parameter: `gplus(c) = gibbs(c) + log(750*.07031);`

**Fix:** Emit computed parameter assignments

---

### dispatch (NLP)

**GAMS Errors:**
```
**** 171  Domain violation for set
```

**Root Cause:** `cg(genchar)` subset relationship lost

**Fix:** Emit subset declarations: `cg(genchar) /a, b, c/`

---

### least (NLP)

**GAMS Errors:**
```
****  66 equation stat_b1.. symbol "dat" has no values assigned
```

**Missing Data:**
- `dat(i,*)` - Table data

**Fix:** Emit Table data in `emit_original_parameters()`

---

### port (LP)

**GAMS Errors:**
```
**** 171  Domain violation for set
```

**Root Cause:** `g(b)` subset relationship lost

**Fix:** Emit subset declarations: `g(b) /corporate, us-ser-e, us-ser-f/`

---

### ps2_f_inf (NLP)

**GAMS Errors:**
```
**** 145  Set identifier or quoted element expected
**** 148  Dimension different
```

**Root Cause:** Reserved word `inf` used as set element without quoting

**Fix:** Quote reserved words: `/'inf'/` and `nu_rev('inf')`

---

### sample (NLP)

**GAMS Errors:**
```
**** 120  Unknown identifier entered as set
**** 149  Uncontrolled set entered as constant
**** 171  Domain violation for set
**** 340  A label/element with the same name exist
```

**Root Cause:** Set elements `a` and `b` used unquoted in expressions

**Fix:** Quote set element references in expressions: `lam_vbal('a')` not `lam_vbal(a)`

---

### trnsport (LP)

**GAMS Errors:**
```
****  66 equation stat_x.. symbol "c" has no values assigned
```

**Missing Data:**
- `c(i,j)` - Computed parameter: `c(i,j) = f*d(i,j)/1000;`
- `f` - Scalar value incorrect (emitted as 0.0 instead of 90)

**Fix:** Emit computed parameter assignments and fix scalar value emission

---

## 3. Root Cause Summary

### By Code Location

| Location | Issue | Models | Fix Type |
|----------|-------|--------|----------|
| `src/emit/original_symbols.py:130-185` | Table data not emitted | ajax, least | Add Table emission |
| `src/emit/original_symbols.py:130-185` | Computed params not emitted | chem, trnsport | Add assignment emission |
| `src/emit/original_symbols.py:63-89` | Subset relationships lost | dispatch, port | Track/emit subset domains |
| `src/emit/original_symbols.py:63-89` | Reserved words not quoted | ps2_f_inf | Quote reserved word elements |
| `src/emit/expr_to_gams.py` | Set elements unquoted | sample | Quote element references |

### By IR Gap

| IR Component | Issue | Impact |
|--------------|-------|--------|
| `ParameterDef.values` | Table data not stored | 4 models (ajax, chem, least, trnsport) |
| `SetDef` | No subset/superset tracking | 2 models (dispatch, port) |
| Expression emission | No reserved word detection | 1 model (ps2_f_inf) |
| Expression emission | Element references unquoted | 1 model (sample) |

---

## 4. Proposed Fixes

### Fix 1: Emit Table Data (6h, +2 models: ajax, least)

**Problem:** Table data is not preserved in IR or emitted.

**Solution:**
1. Ensure parser stores Table data in `ParameterDef.values`
2. Update `emit_original_parameters()` to emit all stored values

**Files to modify:**
- `src/ir/parser.py` - Verify Table parsing stores values
- `src/emit/original_symbols.py` - Verify emission handles all values

**Effort:** 6h (investigation + implementation + testing)

---

### Fix 2: Emit Computed Parameter Assignments (4h, +2 models: chem, trnsport)

**Problem:** Assignment statements (`c(i,j) = expr;`) are not emitted.

**Solution:**
1. Store parameter assignments in IR (new field or separate list)
2. Emit assignments after parameter declarations

**Files to modify:**
- `src/ir/model_ir.py` - Add assignment storage
- `src/ir/parser.py` - Parse and store assignments
- `src/emit/original_symbols.py` - Emit assignments

**Effort:** 4h

---

### Fix 3: Preserve Subset Relationships (4h, +2 models: dispatch, port)

**Problem:** Subset declarations like `cg(genchar)` lose the superset reference.

**Solution:**
1. Add `superset: str | None` field to `SetDef`
2. Update parser to capture subset declarations
3. Emit as `cg(genchar) /a, b, c/` instead of `cg /a, b, c/`

**Files to modify:**
- `src/ir/model_ir.py` - Add `SetDef.superset`
- `src/ir/parser.py` - Parse subset declarations
- `src/emit/original_symbols.py` - Emit subset syntax

**Effort:** 4h

---

### Fix 4: Quote GAMS Reserved Words (2h, +1 model: ps2_f_inf)

**Problem:** Reserved words like `inf`, `eps`, `na`, `pi` need quoting when used as set elements.

**Solution:**
1. Define reserved word list (already exists: `PREDEFINED_GAMS_CONSTANTS`)
2. Quote reserved words in set declarations and element references

**Files to modify:**
- `src/emit/original_symbols.py` - Quote in set/parameter emission
- `src/emit/expr_to_gams.py` - Quote in expression emission

**Effort:** 2h

---

### Fix 5: Quote Set Element References in Expressions (3h, +1 model: sample)

**Problem:** Set elements like `a`, `b` need quoting when used in expressions.

**Solution:**
1. Track which identifiers are set elements vs variables
2. Quote set element references in expression emission

**Files to modify:**
- `src/emit/expr_to_gams.py` - Quote element references

**Effort:** 3h

**Note:** This may overlap with Fix 4 and could be combined.

---

## 5. Priority Ordering

| Priority | Fix | Effort | Models Fixed | ROI |
|----------|-----|--------|--------------|-----|
| P1 | Table data emission | 6h | 2 | 0.33 |
| P1 | Computed parameter assignments | 4h | 2 | 0.50 |
| P2 | Subset relationships | 4h | 2 | 0.50 |
| P2 | Quote reserved words | 2h | 1 | 0.50 |
| P2 | Quote set element refs | 3h | 1 | 0.33 |

**Recommended Order:**
1. Computed parameters (4h, +2 models) - highest ROI
2. Subset relationships (4h, +2 models) - high ROI
3. Table data (6h, +2 models) - broader impact
4. Reserved word quoting (2h, +1 model) - quick fix
5. Set element quoting (3h, +1 model) - may combine with #4

**Total:** ~19h for +8 models (considering some overlap in fixes 4 and 5)

---

## Appendices

### Appendix A: Reproducing Generated MCP Files

The MCP files used in this analysis were generated into a local temporary directory during the investigation. To reproduce them, run the following commands:

```bash
# Create output directory
mkdir -p mcp_analysis

# Generate MCP for each model
for model in ajax chem dispatch least port ps2_f_inf sample trnsport; do
    python -m src.cli data/gamslib/raw/${model}.gms -o mcp_analysis/${model}_mcp.gms
done

# Compile with GAMS to see errors
for model in ajax chem dispatch least port ps2_f_inf sample trnsport; do
    echo "=== $model ==="
    gams mcp_analysis/${model}_mcp.gms lo=2
done
```

Expected output files:
- `mcp_analysis/ajax_mcp.gms`
- `mcp_analysis/chem_mcp.gms`
- `mcp_analysis/dispatch_mcp.gms`
- `mcp_analysis/least_mcp.gms`
- `mcp_analysis/port_mcp.gms`
- `mcp_analysis/ps2_f_inf_mcp.gms`
- `mcp_analysis/sample_mcp.gms`
- `mcp_analysis/trnsport_mcp.gms`

### Appendix B: GAMS Error Code Reference

| Code | Description |
|------|-------------|
| 66 | Symbol not defined or assigned |
| 70 | Dimensions of equ.var pair do not conform |
| 120 | Unknown identifier entered as set |
| 145 | Set identifier or quoted element expected |
| 148 | Dimension different |
| 149 | Uncontrolled set entered as constant |
| 171 | Domain violation for set |
| 256 | Error(s) in analyzing solve statement |
| 257 | Solve statement not checked due to previous errors |
| 300 | Remaining errors not printed for this line |
| 340 | Label/element with same name exists - may need quoting |

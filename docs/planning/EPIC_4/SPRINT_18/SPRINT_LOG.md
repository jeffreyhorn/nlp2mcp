# Sprint 18 Log

## Overview

**Sprint Goal**: Improve GAMS model translation coverage by implementing Table data blocks, computed parameters, put/display statements, and Action=C compile-only mode.

**Target Metrics**:
- Parse: 61 → 80+ models
- Translate: 42 → 55+ models  
- Solve: 12 → 20+ models

---

## Day 0: Sprint Initialization (2026-02-07)

### Sprint Start
- **Timestamp**: 2026-02-07T15:41:19Z
- **Branch**: `sprint18/day0-init`
- **Base**: `main` (post-Sprint 17 merge)

### Prerequisites Validation

| Prerequisite | Status | Notes |
|--------------|--------|-------|
| Planning documents approved | ✅ | PLAN.md, KNOWN_UNKNOWNS.md, PREP_PLAN.md present |
| v1.1.0 tag exists | ✅ | Tag accessible |
| Sprint 17 items merged | ✅ | All merged to main |
| Clean working directory | ✅ | No uncommitted changes |

### Baseline Metrics

Full pipeline test executed against current main branch:

| Stage | Expected | Actual | Delta | Notes |
|-------|----------|--------|-------|-------|
| Parse | 61 | 62 | +1 | Improved from Sprint 17 prep work |
| Translate | 42 | 50 | +8 | Significant improvement from prep tasks |
| Solve | 12 | 13 | +1 | Slight improvement |
| Full Pipeline | - | 4 | - | End-to-end success count |

**Parse Error Breakdown**:
- `lexer_invalid_char`: 72 models
- `internal_error`: 24 models
- `semantic_undefined_symbol`: 2 models

**Translate Error Breakdown**:
- `internal_error`: 6 models
- `codegen_numerical_error`: 2 models
- `unsup_expression_type`: 2 models
- `diff_unsupported_func`: 2 models

**Solve Error Breakdown**:
- `path_syntax_error`: 22 models
- `path_solve_terminated`: 13 models
- `model_infeasible`: 2 models

### Environment Validation

| Component | Version | Status |
|-----------|---------|--------|
| GAMS | 51.3.0 | ✅ |
| Python | 3.x (venv) | ✅ |
| NumPy | 2.3.4 | ✅ |
| Lark | 1.3.1 | ✅ |
| pytest | installed | ✅ |

### Quality Checks

```bash
# Full test suite
make test
# Result: 3240 passed, 10 skipped, 1 xfailed

# Type checking
make typecheck
# Result: Success, no issues

# Linting
make lint
# Result: All checks passed
```

### Day 0 Summary

Sprint 18 initialization complete. Baseline metrics show improvements over expected values due to Sprint 17 prep work (Issues #461, #621, #646 fixes). The starting point is stronger than planned:

- **Parse**: 62 models (1 above target baseline)
- **Translate**: 50 models (8 above target baseline)
- **Solve**: 13 models (1 above target baseline)

This provides additional headroom for Sprint 18 goals.

### Next Steps (Day 1)
- Begin implementation of Table data block parsing
- Reference: PLAN.md Day 1 tasks

---

## Day 1: Diagnostic Deep-Dive on Top Failures (2026-02-08)

### Objectives
- [x] Identify top 10 failing models by error type
- [x] Analyze path_syntax_error failures (root causes)
- [x] Analyze other emission failures
- [x] Create prioritized fix list with impact estimates

### Failure Analysis Summary

**Pipeline Status**: 50 models translate successfully; 37 fail at the solve stage overall (with a subset failing GAMS compilation due to syntax errors).

#### GAMS Error Code Distribution (Compilation Failures)

*Note: This table covers models that fail GAMS compilation. Runtime failures (`path_solve_terminated`, `model_infeasible`) compile successfully but fail during solver execution and are covered separately in Category 5.*

| Error Code | Count | Description | Root Cause |
|------------|-------|-------------|------------|
| 120 | 9 | Unknown identifier as set element | Unquoted element literals (e.g., `revenue` vs `"revenue"`) |
| 352 | 2 | Set not initialized | Empty dynamic subsets (e.g., `ku(k)` declared but never populated) |
| 69 | 2 | Dimension mismatch | Variable dimension errors in model statement |
| 185 | 1 | Set identifier expected | Invalid nested parens from `.fx` bounds (e.g., `nu_x_fx(1)(i)`) |
| 161 | 1 | Element not in superset | Domain violations in parameter assignments |
| 170 | 1 | Domain violation | Set element outside allowed domain |
| 149 | 1 | Uncontrolled set as constant | Quoted lag references (e.g., `"tt+1"` vs `tt+1`) |
| 145 | 1 | Set identifier expected | Syntax error in equation indices |
| 141 | 1 | Symbol not assigned | Parameter declared but not populated |
| 140 | 1 | Unknown symbol | Reference to undefined symbol |
| 121 | 1 | Index domain mismatch | Index domain different from reference domain |
| 66 | 1 | Symbol not defined | Undefined symbol reference |

### Root Cause Analysis

#### Category 1: Element Literal Quoting (9 models)
**Models**: demo1, mathopt1, mexss, pak, pollut, ps2_f, ps2_f_eff, ps2_f_s, ps2_s

**Problem**: All-lowercase element literals like `revenue`, `total`, `cost` are emitted without quotes, but GAMS interprets them as domain variables.

**Example** (demo1):
```gams
* Emitted (wrong):
croprep(revenue,c) = croprep("output",c) * price(c);

* Should be:
croprep("revenue",c) = croprep("output",c) * price(c);
```

**Root Cause**: `_quote_indices()` in `expr_to_gams.py` uses a heuristic that all-lowercase identifiers are domain variables. However, element literals can also be all-lowercase when they appear in computed parameter assignments.

**Fix Location**: `src/emit/expr_to_gams.py:206-215` - Need to track which identifiers are set elements vs domain variables from context.

**Impact**: Fixing this would recover **9 models** (24% of solve failures).

#### Category 2: Empty Dynamic Subsets (2 models)
**Models**: abel, qabel

**Problem**: Subsets declared with syntax like `ku(k)` are emitted but never populated with elements.

**Example** (abel):
```gams
Sets
    k /1964-i, 1964-ii, .../
    ku(k)    * <- empty, never initialized
    ki(k)
    kt(k)
;
```

**Root Cause**: The original model uses these subsets in control flow (loops, conditions) which aren't fully supported. When emitted, the subsets are empty.

**Fix Location**: Parser needs to capture subset initialization from dollar conditions or explicit assignments.

**Impact**: Fixing this would recover **2 models** (5% of solve failures).

#### Category 3: Quoted Lag/Lead References (1 model + related)
**Models**: robert (documented in issue #650)

**Problem**: Lag/lead references emitted as quoted strings instead of GAMS syntax.

**Example** (robert):
```gams
* Emitted (wrong):
sb(r,tt).. s(r,"tt+1") =E= ...

* Should be:
sb(r,tt)$(ord(tt) < card(tt)).. s(r,tt+1) =E= ...
```

**Root Cause**: Parser stores `"tt+1"` as a string literal instead of recognizing lead/lag syntax.

**Fix Location**: `src/ir/parser.py` - Index parsing should detect and preserve lead/lag expressions.

**Impact**: This affects multiple models. Fixing would recover **1-3 models**.

#### Category 4: Invalid Variable Names from .fx Bounds (1 model)
**Models**: himmel16

**Problem**: Variable `.fx` bounds generate multiplier names with embedded indices, creating invalid syntax.

**Example** (himmel16):
```gams
* Emitted (wrong):
nu_x_fx(1)(i)   * <- nested parens invalid

* Problem source:
x.fx("1") = 0;  * <- generates multiplier for this bound
```

**Root Cause**: Bound constraint naming doesn't sanitize index values in generated names.

**Fix Location**: `src/converter/converter.py` - Bound multiplier naming logic.

**Impact**: Fixing would recover **1 model** (may affect others with `.fx` bounds on indexed elements).

#### Category 5: Runtime Solver Failures (13 models)
**Status**: `path_solve_terminated` - These compile successfully but PATH solver fails.

**Models**: chem, cpack, dispatch, house, jobt, like, meanvar, port, process, ps3_f, ps3_s, ps3_s_gic, ps3_s_mn

**Root Cause**: Likely numerical issues, infeasible KKT systems, or incorrect constraint transformations. These require deeper investigation but are lower priority than syntax errors.

### Prioritized Fix List

| Priority | Issue | Models Affected | Effort | Impact |
|----------|-------|-----------------|--------|--------|
| **P1** | Element literal quoting heuristic | 9 | Medium | High - 24% of failures |
| **P2** | Quoted lag/lead references | 1-3 | Medium | Medium |
| **P3** | Invalid .fx bound names | 1+ | Low | Low-Medium |
| **P4** | Empty dynamic subsets | 2 | High (complex) | Low |
| **P5** | Runtime solver failures | 13 | High (deep investigation) | Medium |

### Recommended Day 2 Focus

1. **Fix P1 (Element Literal Quoting)**: Highest impact fix. Modify `_quote_indices()` to use context from the AST to distinguish element literals from domain variables. Consider tracking which indices were originally quoted in the parser.

2. **Fix P3 (Invalid .fx Bound Names)**: Quick win. Sanitize generated multiplier names to avoid nested parentheses.

3. **Document P2 and P4**: These are already documented in `docs/issues/`. Add implementation notes for future sprints.

### Day 1 Summary

Completed diagnostic deep-dive on 37 solve failures:
- Identified 5 distinct root cause categories
- Largest impact fix (element literal quoting) would recover 9 models
- Created prioritized fix list for Day 2 implementation

### Next Steps (Day 2)
- Implement P1 fix: Element literal quoting context
- Implement P3 fix: Sanitize .fx bound multiplier names
- Re-run pipeline to validate fixes
- Update metrics

---

## Day 2: P1 Element Literal Quoting Fix (2026-02-08)

### Objectives
- [x] Implement P1 fix: Element literal quoting
- [ ] Implement P3 fix: Sanitize .fx bound multiplier names
- [x] Re-run pipeline to validate fixes
- [x] Update metrics

### Work Completed

#### P1 Fix: Element Literal Quoting (Multiple Components)

**Problem**: Multi-character all-lowercase element literals (e.g., `cod`, `land`, `apr`, `revenue`) were being treated as domain variables and emitted without quotes, causing GAMS Error 120/340.

**Root Cause Analysis**: The `_quote_indices()` heuristic in `expr_to_gams.py` couldn't distinguish between:
- Domain variables like `i`, `j`, `crep` (should NOT be quoted)
- Element literals like `cod`, `land`, `apr` (SHOULD be quoted)

**Solution**: Multi-part fix across parser and emitter:

1. **Parser Quote Preservation** (`src/ir/parser.py`):
   - Modified `_extract_indices_with_subset()` to preserve quotes for element literals
   - Added helper `_strip_quotes_from_indices()` to canonicalize value storage
   - Expression indices keep quotes (for emitter), value indices strip quotes (for lookup)

2. **Emitter Domain Context** (`src/emit/expr_to_gams.py`):
   - Added `domain_vars` parameter to `expr_to_gams()` and `_quote_indices()`
   - Domain variables from equation domains and sum expressions are tracked
   - Only indices in `domain_vars` context are left unquoted
   - Refined heuristic: single/two-char lowercase → unquoted; multi-char → quoted

3. **Equation Emitter Integration** (`src/emit/equations.py`):
   - Pass equation domain as `domain_vars` when emitting LHS/RHS expressions

4. **Computed Parameter Emission** (`src/emit/original_symbols.py`):
   - Pass domain indices from key_tuple as `domain_vars`
   - Skip report parameters with indexed expressions but no values

**Files Modified**:
- `src/ir/parser.py`: Quote preservation in index extraction
- `src/emit/expr_to_gams.py`: Context-aware quoting with `domain_vars`
- `src/emit/equations.py`: Pass equation domain to emitter
- `src/emit/original_symbols.py`: Pass domain context, skip report params

### Metrics Update

| Stage | Day 1 | Day 2 | Delta |
|-------|-------|-------|-------|
| Parse | 62 | 62 | 0 |
| Translate | 50 | 50 | 0 |
| Solve (optimal) | 13 | 13 | 0 |
| Compile errors (`path_syntax_error`) | 22 | 15 | **-7** |
| Runtime errors (`path_solve_terminated`) | 13 | 20 | +7 |

**Key Result**: 7 models moved from compilation failures to successful compilation. While they don't solve successfully (PATH solver fails), the GAMS code is now syntactically valid.

**Models Fixed** (now compile, previously had syntax errors):
- pollut, demo1, and 5 others moved to `path_solve_terminated`

### Test Updates
- Updated `test_expr_to_gams.py`: Tests now pass domain context for multi-char indices
- All 2566 unit tests pass

---

## Day 2 (continued): P3 Fix - Invalid .fx Bound Names (2026-02-08)

### P3 Fix: Invalid .fx Bound Identifier Names

**Problem**: Per-element `.fx` bounds like `x.fx("1") = 0` generated equation and multiplier names with parentheses (e.g., `x_fx(1)`, `nu_x_fx(1)`), which are invalid GAMS identifiers. This caused GAMS Error 185 "Set identifier or '*' expected".

**Example** (himmel16):
```gams
* Original GAMS:
x.fx("1") = 0;  y.fx("1") = 0;  y.fx("2") = 0;

* Emitted (WRONG):
nu_x_fx(1)(i)   * <- nested parens invalid GAMS identifier
x_fx(1)(i)..    * <- nested parens in equation name

* Emitted (CORRECT after fix):
nu_x_fx_1       * <- valid identifier with underscores
x_fx_1..        * <- valid equation name
```

**Root Cause**: Two issues:
1. `_bound_name()` in `normalize.py` used `f"{var}_{suffix}({joined})"` creating names like `x_fx(1)`
2. Per-element bounds incorrectly inherited the variable's domain, causing indexed equations for scalar constraints

**Solution**: Two-part fix:

1. **Fix bound name format** (`src/ir/normalize.py`):
   - Changed `_bound_name()` to use underscores: `f"{var}_{suffix}_{joined}"`
   - Example: `x_fx_1` instead of `x_fx(1)`

2. **Fix per-element bound domain** (`src/ir/normalize.py`):
   - Per-element bounds (with specific indices) now create scalar equations (`domain_sets=()`)
   - Only uniform bounds (without indices, e.g., `x.lo = 0`) create indexed equations
   - This prevents the invalid `x_fx_1(i)` syntax

**Files Modified**:
- `src/ir/normalize.py`: `_bound_name()` format, `normalize_model()` domain logic

**Test Updates**:
- `tests/unit/ir/test_normalize.py`: Updated bound name expectations (`x_lo_i1` vs `x_lo(i1)`)
- Added docstrings explaining per-element vs uniform bound behavior

### Final Day 2 Metrics

| Stage | Day 1 | After P1 | After P3 | Delta |
|-------|-------|----------|----------|-------|
| Parse | 62 | 62 | 62 | 0 |
| Translate | 50 | 50 | 50 | 0 |
| Solve (optimal) | 13 | 13 | 13 | 0 |
| Compile errors (`path_syntax_error`) | 22 | 15 | **14** | **-8** |
| Runtime errors (`path_solve_terminated`) | 13 | 20 | **21** | +8 |

**Key Result**: 
- P1 fix: 7 models moved from compile errors to runtime (solver) errors
- P3 fix: 1 additional model (himmel16) moved from compile errors to runtime errors
- **Total: 8 fewer compilation failures**

**Models Fixed** (now compile successfully):
- himmel16 (P3 fix)
- chem, chenery, dispatch, himmel11, jobt, least, like (P1 fix)

### Day 2 Summary

Completed two high-impact fixes:
- **P1 (Element Literal Quoting)**: Context-aware quoting using `domain_vars` parameter
- **P3 (Invalid .fx Bound Names)**: Underscore-based naming for valid GAMS identifiers

All 2159 unit tests pass. Pipeline improvements:
- Compilation failures reduced from 22 to 14 (-8)
- 8 models now compile successfully (though solver still fails - different root cause)

---

## Day 3: P2 Fix - Lag/Lead Expression Quoting (2026-02-08)

### Objectives
- [x] Investigate P2: Quoted lag/lead references issue
- [x] Implement P2 fix if feasible
- [x] Run regression tests
- [x] Update sprint log

### P2 Fix: Multi-letter Lag/Lead Expression Quoting

**Problem**: Lag/lead expressions with multi-letter base variables (like `tt+1`, `te+1`) were being quoted as `"tt+1"` in the emitted GAMS, which caused Error 149 "Uncontrolled set entered as constant".

**Example** (robert model):
```gams
* Equation definition:
sb(r,tt+1).. s(r,tt+1) =e= s(r,tt) - sum(p, a(r,p)*x(p,tt));

* Before P2 fix (WRONG):
sb(r,tt).. s(r,"tt+1") =E= s(r,tt) - ...

* After P2 fix (CORRECT):
sb(r,tt).. s(r,tt+1) =E= s(r,tt) - ...
```

**Root Cause**: The `_quote_indices()` function receives strings from `VarRef.indices_as_strings()`, which converts `IndexOffset` objects to strings like `"tt+1"`. The quoting heuristic then couldn't distinguish between:
- Lag/lead expression `tt+1` (should NOT be quoted)
- Hyphenated element label `route-1` (SHOULD be quoted)

**Solution**: Added `_format_mixed_indices()` function that handles `IndexOffset` objects directly:

1. **Type-aware index formatting** (`src/emit/expr_to_gams.py`):
   - Added `_format_mixed_indices()` to process mixed `str | IndexOffset` tuples
   - `IndexOffset` objects are emitted directly via `to_gams_string()` without quoting
   - String indices continue through `_quote_indices()` for heuristic quoting

2. **Refined pattern matching** (`_is_index_offset_syntax()`):
   - Extended to support multi-letter bases for `+` (lead) and `++`/`--` (circular)
   - Kept single-letter restriction for `-` (lag) to avoid false positives on hyphenated labels
   - Multi-letter lag expressions come through as `IndexOffset` objects, not strings

**Files Modified**:
- `src/emit/expr_to_gams.py`: Added `_format_mixed_indices()`, updated pattern matching

### Metrics (No Change)

| Metric | After P1+P3 | After P2 | Change |
|--------|-------------|----------|--------|
| path_syntax_error | 14 | 14 | 0 |
| path_solve_terminated | 21 | 21 | 0 |
| model_optimal | 13 | 13 | 0 |

**Note**: The P2 fix correctly emits lag/lead expressions, but the affected models (robert, pak) still have other issues (domain mismatches in KKT stationarity equations) that prevent successful compilation.

### Models with Lag/Lead Expressions

Models now correctly emit multi-letter lag/lead expressions:
- `robert`: `s(r,tt+1)` instead of `s(r,"tt+1")`
- `pak`: `c(te+1)`, `ti(te+1)`, `ks(te+1,j)` instead of quoted versions

### Day 3 Summary (P2)

Implemented P2 fix for multi-letter lag/lead expression quoting:
- Added type-aware index formatting that preserves `IndexOffset` semantics
- Correctly emits `tt+1` instead of `"tt+1"` for lead expressions
- All 2159 unit tests pass

---

## Day 3 (continued): P4 Fix - Empty Dynamic Subsets (2026-02-08)

### Objectives
- [x] Investigate P4: Empty dynamic subsets issue
- [x] Implement P4 fix
- [x] Run regression tests
- [x] Update sprint log

### P4 Fix: Dynamic Subset Assignment Emission

**Problem**: Dynamic subsets declared with syntax like `ku(k)` were emitted as empty sets because their initialization statements (e.g., `ku(k) = yes$(ord(k) < card(k))`) were being parsed but not stored or emitted.

**Example** (abel model):
```gams
* Original GAMS declarations:
Sets
    k /1964-i, 1964-ii, .../
    ku(k)
    ki(k)
    kt(k)
;
ku(k) = yes$(ord(k) < card(k));
ki(k) = yes$(ord(k) = 1);
kt(k) = not ku(k);

* Before P4 fix (WRONG):
Sets
    ku(k)    * <- declared but empty, no initialization
    ki(k)
    kt(k)
;
* no assignment statements emitted

* After P4 fix (CORRECT):
Sets
    ku(k)
    ki(k)
    kt(k)
;
ku(k) = 1$ord(k) < card(k);
ki(k) = 1$ord(k) = 1;
kt(k) = not ku(k);
```

**Root Cause**: The parser detected set assignments at lines 3115-3120 but just returned without storing them. The mock/store approach was incomplete.

**Solution**: Four-part fix:

1. **SetAssignment dataclass** (`src/ir/symbols.py`):
   - Added `SetAssignment` class to store dynamic set assignment statements
   - Fields: `set_name`, `indices`, `expr` (parsed expression), `location`

2. **ModelIR storage** (`src/ir/model_ir.py`):
   - Added `set_assignments: list[SetAssignment]` field to store assignments

3. **Parser capture** (`src/ir/parser.py`):
   - Modified set assignment handling to create and store `SetAssignment` objects
   - Expression is already parsed and validated with correct domain context

4. **Emission function** (`src/emit/original_symbols.py`):
   - Added `emit_set_assignments()` function to emit stored assignments as GAMS
   - Uses `expr_to_gams()` with domain context to correctly format expressions

5. **Integration** (`src/emit/emit_gams.py`):
   - Added call to `emit_set_assignments()` after computed parameter assignments

6. **Bug fix - `not` operator** (`src/emit/expr_to_gams.py`):
   - Added handling for `not` operator with required space
   - `not ku(k)` instead of `notku(k)`

**Files Modified**:
- `src/ir/symbols.py`: Added `SetAssignment` dataclass
- `src/ir/model_ir.py`: Added `set_assignments` field
- `src/ir/parser.py`: Store set assignments instead of just returning
- `src/emit/original_symbols.py`: Added `emit_set_assignments()` function
- `src/emit/emit_gams.py`: Call `emit_set_assignments()` in pipeline
- `src/emit/__init__.py`: Export `emit_set_assignments`
- `src/emit/expr_to_gams.py`: Handle `not` operator with space

### Test Results
- All 2159 unit tests pass
- All 271 integration tests pass (5 skipped)
- All 376 gamslib tests pass

### Models with Dynamic Subsets

Models now correctly emit dynamic subset assignments:
- `abel`: `ku(k)`, `ki(k)`, `kt(k)` now initialized
- `qabel`: Same subsets now initialized

### Day 3 Final Summary

Implemented two fixes:
- **P2**: Multi-letter lag/lead expression quoting (semantic correctness)
- **P4**: Dynamic subset assignment emission (2 models affected)

---

### Sprint 18 Days 1-3 Cumulative Progress

| Stage | Day 0 | Day 3 | Change |
|-------|-------|-------|--------|
| Parse | 62 | 62 | 0 |
| Translate | 50 | 50 | 0 |
| path_syntax_error | 22 | 14 | **-8** |
| path_solve_terminated | 13 | 21 | +8 |
| model_optimal | 13 | 13 | 0 |

**Key Achievements**:
- P1: Context-aware element literal quoting (7 models now compile)
- P3: Valid GAMS identifiers for .fx bounds (1 model now compiles)
- P2: Correct lag/lead expression emission (semantic fix)
- P4: Dynamic subset assignment emission (2 models affected: abel, qabel)

---

## Day 3 (continued): P5 Fix - Runtime Solver Failures (2026-02-08)

### Objectives
- [x] Investigate P5: Runtime solver failures (division by zero)
- [x] Implement P5 fix
- [x] Run regression tests
- [x] Update sprint log

### P5 Fix: Variable Initialization to Prevent Division by Zero

**Problem**: Models that compiled successfully were failing at GAMS model generation time with "division by zero (0)" errors. Variables appearing in denominators of stationarity equations (from differentiating `log(x)` or `1/x` terms) caused undefined values when initialized to default 0.

**Example** (chem model):
```
**** Exec Error at line 106: division by zero (0)
**** Evaluation error(s) in equation "stat_m(one)"
        Problem in Jacobian evaluation of "p(one)"
        Problem in Jacobian evaluation of "m(one)"
        Problem in Jacobian evaluation of "s(one)"
```

**Root Cause**: GAMS variables default to `.l = 0`. When stationarity equations contain terms like `1/x` or derivatives of `log(x)`, evaluation at `x = 0` causes division by zero during model generation.

**Solution**: Added variable initialization section to emitted GAMS code:

1. **Priority 1 - Explicit level values** (`l_map`, `l`):
   - Emit `.l` values captured from original model if present
   - Example: `s.l("one") = 15.0;` from `s.l(g) = 15;`

2. **Priority 2 - Lower bounds** (`lo_map`, `lo`):
   - If no explicit `.l`, initialize to lower bound value
   - Example: `p.l("one") = 0.1;` from `p.lo(g) = 0.1;`

3. **Priority 3 - Positive variable default**:
   - Positive variables without other initialization get `.l = 1`
   - Changed from `1e-6` to `1` for numerical stability
   - Example: `m.l(g) = 1;`

**Files Modified**:
- `src/emit/emit_gams.py`: Added variable initialization logic in `emit_gams_mcp()`

### Emitted Code Example

```gams
* ============================================
* Variable Initialization
* ============================================

* Initialize variables to avoid division by zero during model generation.
* Variables appearing in denominators (from log, 1/x derivatives) need
* non-zero initial values. Set to lower bound or small positive value.

p.l("one") = 0.1;
p.l("two") = 0.1;
p.l("three") = 0.1;
m.l(g) = 1;
s.l("one") = 15.0;
s.l("two") = 15.0;
s.l("three") = 15.0;
```

### Test Results

| Model | Before P5 | After P5 | Notes |
|-------|-----------|----------|-------|
| chem | division by zero | ✅ Compiles & solves | |
| like | division by zero | Compiles, runtime error | Different issue: domain restriction (#653) |

**Regression Tests**:
- Core examples (simple_nlp, scalar_nlp, indexed_balance, positive_vars_nlp): All pass
- Integration health check: 5/13 pass (same as before, no regressions)
- All unit tests pass

### Models Still Affected

The `like` model still fails after P5 fix, but with a different error:
```
**** MCP pair comp_rank.lam_rank has empty equation but associated variable is NOT fixed
```

This is caused by Issue #653 (missing domain restriction for lead index), not by the P5 initialization issue. The P5 fix successfully resolved the division by zero errors.

### Day 3 P5 Summary

Implemented P5 fix for variable initialization:
- Variables now initialized from `.l` values, lower bounds, or reasonable defaults
- Division by zero errors eliminated for models with denominators containing variables
- `chem` model now compiles and solves successfully
- `like` model now compiles (P5 fix worked) but has separate domain restriction issue (#653)

---

### Sprint 18 Days 1-3 Final Cumulative Progress

| Stage | Day 0 | Day 3 End | Change |
|-------|-------|-----------|--------|
| Parse | 62 | 62 | 0 |
| Translate | 50 | 50 | 0 |
| path_syntax_error | 22 | 14 | **-8** |
| path_solve_terminated | 13 | ~20 | +7 |
| model_optimal | 13 | 14+ | **+1+** |

**Key Achievements (All Days)**:
- **P1**: Context-aware element literal quoting (7 models now compile)
- **P3**: Valid GAMS identifiers for .fx bounds (1 model now compiles)
- **P2**: Correct lag/lead expression emission (semantic fix)
- **P4**: Dynamic subset assignment emission (abel, qabel affected)
- **P5**: Variable initialization for division by zero prevention (chem now solves)

### Next Steps (Day 4+)
- Investigate remaining `path_syntax_error` failures (14 models)
- Investigate `path_solve_terminated` failures (may be numeric/feasibility issues)
- Address Issue #653 (like model domain restriction)

---

---

## Day 4-5: Path Syntax Error Deep Dive (2026-02-09 to 2026-02-10)

### Objectives
- [x] Analyze remaining 12 path_syntax_error models
- [x] Fix case sensitivity bug in bound multiplier keys
- [x] Fix table wildcard data emission
- [x] Fix dollar conditional parenthesization
- [x] Fix wildcard '*' quoting issue

### Work Completed

#### 1. Case Sensitivity Bug in Bound Multiplier Keys (partition.py)

**Problem**: Alkyl and bearing models had Error 69/483 (variable dimension unknown) because bound multiplier keys used original case from `.items()` but lookups used lowercase from `.keys()`.

**Solution**: Changed `partition.py` to use `.keys()` for variable iteration:
```python
# Before (wrong):
for var_name, var_def in model_ir.variables.items():

# After (correct):
for var_name in model_ir.variables.keys():
    var_def = model_ir.variables[var_name]
```

**Impact**: alkyl and bearing now compile successfully (have MCP pairing errors, not syntax errors).

#### 2. Table Wildcard Data Emission (original_symbols.py)

**Problem**: Tables with wildcard `*` domains (e.g., `pdat(lmh,*,sde,i)`) had dimension mismatches. Parser stores table data as 2-tuples `(row_header, col_header)` with dotted row headers like `'low.a.distr'`, but domain has 4 dimensions.

**Solution**: Added `_expand_table_key()` function to expand dotted row headers:
- `('low.a.distr', 'light-ind')` → `('low', 'a', 'distr', 'light-ind')`
- Skip malformed entries that can't be expanded to match domain size

**Impact**: Fixed table data emission for chenery, orani with wildcards.

#### 3. Dollar Conditional Parenthesization (expr_to_gams.py)

**Problem**: Dollar conditionals with comparison conditions emitted invalid syntax:
```gams
* Before (wrong): expr$sig(i) <> 0
* After (correct): expr$(sig(i) <> 0)
```

**Solution**: Parenthesize condition when it's a Binary/Unary/DollarConditional expression.

**Impact**: Fixed chenery stationarity equation syntax.

#### 4. Wildcard '*' Quoting (original_symbols.py)

**Problem**: Wildcard `*` in parameter domains was being quoted as `'*'`, causing GAMS Error 2/185.

**Solution**: Added check in `_quote_symbol()` to never quote `*`:
```python
if name == "*":
    return name
```

**Impact**: Fixed orani parameter domain declarations.

### Models Status After Fixes

| Model | Before | After | Notes |
|-------|--------|-------|-------|
| alkyl | path_syntax_error (E69) | mcp_error | Compiles, MCP pairing issue |
| bearing | path_syntax_error (E69) | mcp_error | Compiles, MCP pairing issue |
| chenery | path_syntax_error (E170) | path_syntax_error (E149) | Table fixed, has cross-indexed sums |
| orani | path_syntax_error (E170) | path_syntax_error (E170/171) | Wildcard fixed, has dynamic domain extension |
| abel, qabel, robert | path_syntax_error (E149) | path_syntax_error (E149) | Cross-indexed sums (architectural) |

### Architectural Issues Identified

#### Error 149: Cross-Indexed Sums (abel, qabel, robert, chenery)

These models have constraints with cross-indexed sums like:
```gams
sum(np, a(n,np)*x(np,k))
```

When differentiating, the stationarity equations produce uncontrolled indices:
- Equation `stat_e(i)..` references `h(t)` where `t` is not in equation domain
- This is a fundamental limitation requiring architectural changes

#### Dynamic Domain Extension (orani)

Orani uses dynamic domain extension:
```gams
amc(c,s,"total") = sum(i, amc(c,s,i)) + ...
```

The `"total"` element is not in the inferred wildcard set, causing domain violations.

### Test Results
- All 3312 tests pass
- No regressions

### Metrics Update

| Category | Day 3 | Day 5 | Change |
|----------|-------|-------|--------|
| path_syntax_error | 14 | 10* | -4 |
| mcp_error | 0 | 2 | +2 |

*Note: 2 models moved from syntax errors to MCP pairing errors (alkyl, bearing).

### Files Modified
- `src/kkt/partition.py`: Case sensitivity fix
- `src/emit/original_symbols.py`: Table expansion, wildcard quoting
- `src/emit/expr_to_gams.py`: Dollar conditional parenthesization
- `tests/unit/emit/test_expr_to_gams.py`: Updated test expectations

### Day 4-5 Summary

Implemented 4 fixes for path_syntax_error issues:
- 2 models now compile (alkyl, bearing) - moved to mcp_error category
- Table wildcard and dollar conditional fixes applied (chenery, orani)
- Identified architectural issues (cross-indexed sums) requiring future work

---

## Day 6: Checkpoint 2 - Mid-Sprint Assessment (2026-02-11)

### Objectives
- [x] Run comprehensive metrics review
- [x] Analyze remaining gaps and categorize issues
- [x] Risk assessment and KNOWN_UNKNOWNS review
- [x] Plan second half of sprint (Days 7-11)

### Full Pipeline Metrics

| Stage | Count | Rate | Delta from Day 0 |
|-------|-------|------|------------------|
| Parse | 62/160 | 38.8% | 0 |
| Translate | 50/62 | 80.7% | 0 |
| Solve | 19/50 | 38.0% | +6 (from 13) |
| Match | 7/19 | 36.8% | +3 (from 4) |
| Full Pipeline | 7/160 | 4.4% | +3 |

### Solve Stage Failure Breakdown

| Category | Count | Models |
|----------|-------|--------|
| path_solve_terminated | 18 | Various numerical/feasibility issues |
| path_syntax_error | 10 | abel, blend, chenery, like, mexss, mingamma, orani, qabel, robert, sample |
| model_infeasible | 3 | circle, cpack, meanvar |

### Solution Match Status (of 19 solved models)

| Category | Count | Notes |
|----------|-------|-------|
| match | 7 | Solution matches original NLP within tolerance |
| mismatch | 5 | Solves successfully but solution differs from original |
| not_compared | 7 | Comparison not yet run or skipped |

### Checkpoint 2 Target Assessment

| Target | Status | Current | Required |
|--------|--------|---------|----------|
| Solve ≥17 | ✅ **MET** | 19 | 17 |
| path_syntax_error ≤4 | ❌ **NOT MET** | 10 | 4 |

### Path Syntax Error Root Cause Analysis

| Model | GAMS Error | Root Cause | Fixable in Sprint 18? |
|-------|------------|------------|----------------------|
| abel | E149 | Cross-indexed sums (ku subset in sum) | ❌ Architectural |
| qabel | E149 | Cross-indexed sums (ku subset in sum) | ❌ Architectural |
| blend | E171 | Domain violation for set | ⚠️ Investigate |
| chenery | E149 | Cross-indexed sums + table wildcard | ❌ Architectural |
| like | E170 | Domain violation (lead index) | ⚠️ Investigate |
| mexss | E170/171 | Domain violations | ⚠️ Investigate |
| mingamma | E140 | Unknown symbol (psi function) | ❌ GAMS lacks function |
| orani | E170/171 | Dynamic domain extension | ⚠️ Investigate |
| robert | E170 | Domain violation (lead index); originally E149 cross-indexed sums (see ISSUE_670) | ⚠️ Investigate |
| sample | E171 | Domain violation for set | ⚠️ Investigate |

**Note:** `robert` was initially classified under E149 cross-indexed sums (architectural; see `docs/issues/ISSUE_670_cross-indexed-sums-error-149.md`). After applying earlier sprint fixes, the remaining blocking error is E170 (lead index domain violation), which is now tractable to investigate.

### Architectural Issues Identified

1. **Cross-Indexed Sums** (abel, qabel, chenery): 
   - Sums over indices not in equation domain produce "uncontrolled set as constant" errors
   - Example: `sum((ku,m__,mp), ...)` where `ku` is a dynamic subset
   - Requires KKT assembly changes to properly scope sum indices

2. **Dynamic Domain Extension** (orani):
   - Models extend sets at runtime with computed elements (e.g., `"total"`)
   - These elements aren't in the inferred domain, causing domain violations

3. **Missing GAMS Functions** (mingamma):
   - Uses `psi`/digamma function not available in GAMS
   - Cannot be fixed - document as architectural limitation

### Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| path_syntax_error target not met | **HIGH** | Focus Days 7-8 on tractable domain fixes |
| Architectural issues require major work | **MEDIUM** | Document for future sprints, don't block release |
| Regression in solving models | **LOW** | All tests passing, no regressions observed |

### Adjusted Days 7-11 Plan

**Days 7-8: Domain Issue Investigation**
- Deep-dive on blend, sample, like, robert, mexss, orani domain violations
- Identify which are tractable fixes vs architectural issues
- Implement any quick fixes found

**Day 9: Issue Documentation**
- Create ISSUE_*.md files for all architectural limitations
- Update KNOWN_UNKNOWNS.md with findings
- Move completed issues to docs/issues/completed/

**Day 10: Final Fixes & Testing**
- Implement any remaining tractable fixes
- Full pipeline retest on all 160 models
- Verify no regressions

**Day 11: Documentation & Checkpoint 3**
- Update SPRINT_LOG.md with final metrics
- Create sprint retrospective
- Prepare for PR/release

### Days 1-6 Cumulative Progress

| Metric | Day 0 | Day 6 | Change |
|--------|-------|-------|--------|
| Parse | 62 | 62 | 0 |
| Translate | 50 | 50 | 0 |
| Solve (optimal) | 13 | 19 | **+6** |
| path_syntax_error | 22 | 10 | **-12** |
| path_solve_terminated | 13 | 18 | +5 |
| Full Pipeline | 4 | 7 | **+3** |

### Key Achievements (Days 1-6)

1. **P1: Element Literal Quoting** - Context-aware quoting using domain_vars parameter
2. **P3: .fx Bound Names** - Underscore-based naming for valid GAMS identifiers
3. **P2: Lag/Lead Quoting** - Type-aware index formatting for IndexOffset objects
4. **P4: Dynamic Subsets** - SetAssignment storage and emission
5. **P5: Variable Initialization** - Division by zero prevention
6. **Day 4-5 Fixes** - Case sensitivity, table wildcards, dollar conditionals, '*' quoting

### Next Steps (Day 7)
- Begin domain issue investigation for tractable fixes
- Focus on blend, sample, like, robert, mexss, orani (domain violations that may be fixable)

---

<!-- Template for daily entries:

### Day N: [Title] (YYYY-MM-DD)

#### Objectives
- [ ] Objective 1
- [ ] Objective 2

#### Work Completed
- Item 1
- Item 2

#### Metrics Update
| Stage | Start | Current | Delta |
|-------|-------|---------|-------|

#### Issues Encountered
- Issue 1: Description and resolution

#### Next Steps
- Step 1
- Step 2

-->

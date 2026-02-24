# GAMS Macro Expansion — Preprocessor Design Document

**Created:** 2026-02-23
**Sprint:** 21 (Priority 1 workstream)
**Estimated Implementation Time:** 4–8 hours
**Status:** Design complete, ready for implementation

---

## 1. Executive Summary

The nlp2mcp preprocessor already supports `$set`, `$if not set ... $set`, `%name%` expansion, `$if/$else/$endif` conditionals, and `$macro` function definitions. The remaining gaps are:

1. **`$eval` directive** — evaluate arithmetic expressions and store result as a macro
2. **System macros** — `%system.X%`, `%gams.X%`, `%modelStat.X%`, `%solveLink.X%`
3. **`$setglobal` directive** — global-scope macro definition (1 corpus usage)

This document provides the architecture for closing these gaps based on a comprehensive corpus survey of 229 GAMSlib files (219 `.gms` + 10 `.inc`).

---

## 2. Corpus Survey Results

### 2.1 Overall Macro Prevalence

| Feature | Files Using | % of Corpus | Total Instances |
|---------|-------------|-------------|-----------------|
| `$set` directives | ~45 | 20% | ~80+ |
| `%name%` expansion | ~54 | 24% | 200+ |
| `$if`/`$ifThen` with macros | ~30 | 13% | 100+ |
| `$macro` definitions | 3 | 1.3% | 9 |
| `$eval` directives | 5 | 2.2% | 7 |
| `%system.*%`/`%gams.*%` | ~20 | 9% | 40+ |
| `%modelStat.*%` | ~13 | 6% | 40+ |
| `%solveLink.*%` | ~8 | 3.5% | 15+ |
| `$setglobal` | 1 | 0.4% | 1 |

### 2.2 `$eval` Expressions (All 7 Instances)

| File | Line | Expression | Operations Used |
|------|------|-----------|-----------------|
| springchain.gms | 22 | `$eval NM1 %N%-1` | Subtraction |
| gqapsdp.gms | 60 | `$eval imax card(i)` | `card()` function |
| gqapsdp.gms | 61 | `$eval jmax card(j)` | `card()` function |
| gqapsdp.gms | 62 | `$eval xmax %imax%*%jmax%` | Multiplication |
| emfl.gms | 30 | `$eval new %N1%*%N2%` | Multiplication |
| spbenders4.gms | 88 | `$eval cardS card(s)+1` | `card()` + addition |
| srpchase.gms | 20 | `$eval DIM %DIM%+1` | Addition |

**Key finding:** All `$eval` expressions use only simple integer arithmetic (`+`, `-`, `*`) and `card()` function calls. No division, exponentiation, floating-point, string operations, or nested function calls.

### 2.3 System Macros Found in Corpus

#### Solver Selection Macros (most common)
| Macro | Uses | Value Type |
|-------|------|------------|
| `%system.lp%` | 9 | Solver name (e.g., "CPLEX") |
| `%system.nlp%` | 2 | Solver name (e.g., "CONOPT") |
| `%gams.nlp%` | 6 | Solver name |
| `%gams.mip%` | 6 | Solver name |
| `%gams.lp%` / `%gams.LP%` | 6 | Solver name |

#### Model Status Constants (built-in)
| Macro | Numeric Value |
|-------|--------------|
| `%modelStat.optimal%` | 1 |
| `%modelStat.locallyOptimal%` | 2 |
| `%modelStat.unbounded%` | 3 |
| `%modelStat.infeasible%` | 4 |
| `%modelStat.locallyInfeasible%` | 5 |
| `%modelStat.intermediateInfeasible%` | 6 |
| `%modelStat.feasibleSolution%` | 8 |
| `%modelStat.integerSolution%` | 9 |
| `%modelStat.integerInfeasible%` | 10 |
| `%modelStat.intermediateNonoptimal%` | 14 |
| `%modelStat.intermediateNonInteger%` | 16 |
| `%modelStat.infeasibleNoSolution%` | 19 |

#### Solve Link Constants (built-in)
| Macro | Numeric Value |
|-------|--------------|
| `%solveLink.callModule%` | 1 |
| `%solveLink.aSyncThreads%` / `%solveLink.asyncThreads%` | 4 |
| `%solveLink.loadLibrary%` | 5 |
| `%solveLink.asyncGrid%` | 6 |

#### Infrastructure Macros
| Macro | Uses | Purpose |
|-------|------|---------|
| `%gams.scrdir%` | 5 | Scratch directory path |
| `%gams.scrext%` | 5 | Script extension (.cmd/.sh) |
| `%system.dirsep%` | 4 | Directory separator |
| `%gams.input%` | 4 | Current input file name |
| `%gams.lo%` | 4 | Log level |
| `%gams.wdir%` | 2 | Working directory |
| `%gams.jobTrace%` | 6 | Job trace control |
| `%gams.license%` | 2 | License string |
| `%system.fileSys%` | 1 | "UNIX" or "WINDOWS" |
| `%system.redirlog%` | 2 | Redirect logging |
| `%gams.jt%` | 1 | Job trace flag |

#### Environment Macros
| Macro | Uses | Purpose |
|-------|------|---------|
| `%sysEnv.GMSPYTHONLIB%` | 4 | Python library path |
| `%sysEnv.PMI_RANK%` | 1 | MPI rank |
| `%sysEnv.PMI_SIZE%` | 1 | MPI size |

### 2.4 Blocking Model Analysis

**springchain.gms** — Blocked by missing `$eval` support:
- Line 21: `$if not set N $set N 10` (already handled)
- Line 22: `$eval NM1 %N%-1` (**NOT handled** — preprocessor strips this)
- Uses `%N%` (8 places) and `%NM1%` (1 place) for set ranges and formulas
- After expansion: `%N%` → `10`, `%NM1%` → `9`

**saras.gms** — Blocked by missing `%system.nlp%` support:
- Line 1488: `option nlp = %system.nlp%;`
- Context: Restores default NLP solver after temporarily switching to CONOPT
- For nlp2mcp purposes, `%system.nlp%` can expand to `CONOPT` (reasonable default)

---

## 3. Architecture

### 3.1 Current Preprocessing Pipeline

```
_preprocess_content(content):
  1. extract_conditional_sets()     — $if not set X $set X val
  2. extract_set_directives()       — $set X val
  3. process_conditionals()         — $if/$else/$endif
  4. expand_macros()                — %name% → value
  5. extract_macro_definitions()    — $macro name(args) body
  6. expand_macro_calls()           — name(args) → expanded body
  7. strip_conditional_directives()
  8. strip_set_directives()
  9. strip_macro_directives()
  9b. strip_eol_comments()
  10. strip_unsupported_directives()
  11+. normalization steps...
```

### 3.2 Proposed Changes

Add three new capabilities to the existing pipeline:

#### A. System Macro Registry (Before Step 1)

Insert a new Step 0 that seeds the macro dictionary with system macros:

```python
SYSTEM_MACROS: dict[str, str] = {
    # Solver selection defaults
    "system.lp": "CPLEX",
    "system.nlp": "CONOPT",
    "gams.lp": "CPLEX",
    "gams.LP": "CPLEX",
    "gams.nlp": "CONOPT",
    "gams.mip": "CPLEX",
    # Model status constants
    "modelStat.optimal": "1",
    "modelStat.locallyOptimal": "2",
    "modelStat.unbounded": "3",
    "modelStat.infeasible": "4",
    "modelStat.locallyInfeasible": "5",
    "modelStat.intermediateInfeasible": "6",
    "modelStat.feasibleSolution": "8",
    "modelStat.integerSolution": "9",
    "modelStat.integerInfeasible": "10",
    "modelStat.intermediateNonoptimal": "14",
    "modelStat.intermediateNonInteger": "16",
    "modelStat.infeasibleNoSolution": "19",
    # Solve link constants
    "solveLink.callModule": "1",
    "solveLink.asyncThreads": "4",
    "solveLink.aSyncThreads": "4",
    "solveLink.loadLibrary": "5",
    "solveLink.asyncGrid": "6",
    # Infrastructure defaults
    "system.dirsep": "/",
    "system.fileSys": "UNIX",
    "gams.scrdir": "/tmp/",
    "gams.scrext": ".sh",
    "gams.wdir": "./",
    "gams.lo": "0",
    "gams.input": "",
    "gams.jobTrace": "",
    "gams.jt": "0",
    "gams.license": "",
    "system.redirlog": "0",
}
```

**Implementation:** Add `SYSTEM_MACROS` as a module-level constant. In `_preprocess_content()`, initialize `macros = dict(SYSTEM_MACROS)` before Step 1 so system macros are available for conditional tests and `%name%` expansion.

#### B. `$eval` Directive Processing (Between Steps 2 and 3)

New function `process_eval_directives()`:

```python
def process_eval_directives(
    source: str, macros: dict[str, str]
) -> tuple[str, dict[str, str]]:
    """Process $eval directives: evaluate expression and store result.

    Handles:
      $eval name expression
      $evalGlobal name expression  (treated same as $eval)
      $evalLocal name expression   (treated same as $eval)

    Expressions support:
      - Integer arithmetic: +, -, *, //, ()
      - Macro references: %name% (expanded before evaluation)
      - card() function: card(setname) (returns 0 — not supported at
        compile time in nlp2mcp; models using card() in $eval are
        unlikely to parse correctly without runtime set data)

    Returns:
        (modified_source, updated_macros)
    """
```

**Expression evaluator scope** (minimal, matching corpus needs):
- Integer literals
- Arithmetic operators: `+`, `-`, `*` (no division needed in corpus, but include `//` for safety)
- Parentheses for grouping
- Macro expansion within expressions (`%name%` → value before eval)
- `card()` function: return `0` with a warning (requires runtime set cardinality, not available at preprocess time)

**Safety:** Implement a simple recursive descent parser for these arithmetic expressions — do NOT use `eval()`. Note that `ast.literal_eval` only handles Python literals and is not suitable for expressions like `10-1` or `4*7`.

**Implementation approach:**
1. Scan source line-by-line for `$eval` / `$evalGlobal` / `$evalLocal` directives
2. Extract variable name and expression
3. Expand `%macro%` references in the expression
4. Evaluate the arithmetic expression safely
5. Store result in macros dict
6. Replace the directive line with a comment

#### C. `$setglobal` Support (In Step 2)

Minimal change: treat `$setglobal` identically to `$set` in `extract_set_directives()`. The scoping distinction (`$set` = local to current file, `$setglobal` = global across includes) is irrelevant for nlp2mcp since we flatten all includes into a single source string before preprocessing.

**Implementation:** Update the regex in `extract_set_directives()` from:
```python
pattern = r'\$set\s+(\w+)\s+...'
```
to:
```python
pattern = r'\$set(?:global|local)?\s+(\w+)\s+...'
```

Similarly update `strip_set_directives()` to strip `$setglobal` and `$setlocal` lines.

### 3.3 Updated Pipeline

```
_preprocess_content(content):
  0. Initialize macros with SYSTEM_MACROS          ← NEW
  1. extract_conditional_sets()
  2. extract_set_directives()                       ← UPDATED ($setglobal)
  2b. process_eval_directives()                     ← NEW
  3. process_conditionals()
  4. expand_macros()
  5. extract_macro_definitions()
  6. expand_macro_calls()
  7. strip_conditional_directives()
  8. strip_set_directives()                         ← UPDATED ($setglobal)
  8b. strip_eval_directives()                       ← NEW
  9. strip_macro_directives()
  ...
```

### 3.4 Processing Order Rationale

The GAMS compiler processes directives in source order, with macro expansion happening inline (each `$set`/`$eval` takes effect immediately for subsequent lines). Our batch approach (extract all, then expand all) works for the GAMSlib corpus because:

1. No model has circular `$eval` dependencies
2. `$set` values referencing earlier macros are already handled by `extract_set_directives()` expanding `%macro%` in values
3. `$eval` expressions referencing `$set` macros work because we process `$set` before `$eval`
4. Macro expansion before `$ontext/$offtext` stripping is correct — GAMS processes `$set`/`$eval` before stripping comment blocks, but macros defined inside `$ontext` blocks are also skipped (our approach handles this correctly since `$ontext` blocks don't contain `$set` directives in the corpus)

---

## 4. Safe Expression Evaluator Design

### 4.1 Approach: Simple Recursive Descent

Rather than using Python's `eval()` (security risk) or `ast.literal_eval` (limited to literals), implement a minimal expression evaluator:

```python
def _safe_eval_int(expr: str) -> int:
    """Safely evaluate a simple integer arithmetic expression.

    Supports: integer literals, +, -, *, //, parentheses.
    Raises ValueError for unsupported expressions.
    """
```

Grammar:
```
expr   → term (('+' | '-') term)*
term   → factor (('*' | '//') factor)*
factor → '-' factor | '(' expr ')' | INTEGER
```

### 4.2 `card()` Handling

The `card(setname)` function in `$eval` requires knowing the cardinality of a set at compile time. Since nlp2mcp doesn't have this information during preprocessing, we have two options:

1. **Return 0 with warning** — simple, makes affected models produce wrong derived macros
2. **Parse set definitions first** — extract set cardinalities from the source before processing `$eval`

For Sprint 21, **option 1** is recommended. The 3 corpus instances using `card()` in `$eval` across 2 models (gqapsdp, spbenders4) are not in our immediate target list. If they become targets later, we can add set cardinality extraction.

### 4.3 Error Handling

- **Undefined macros in expressions:** Leave `%name%` as-is; `_safe_eval_int()` will raise `ValueError`; skip the `$eval` and log a warning
- **Malformed expressions:** Log warning, skip the `$eval`, leave macro undefined
- **Division by zero:** Raise `ValueError`, skip the `$eval`
- **Non-integer results:** GAMS `$eval` produces integers; truncate toward zero

---

## 5. Impact Analysis

### 5.1 Models Unblocked by This Work

| Model | Blocking Feature | Expected Impact |
|-------|-----------------|-----------------|
| springchain | `$eval NM1 %N%-1` | Will parse and translate |
| saras | `%system.nlp%` | Will parse (already parses with stripped directive) |
| ~13 models | `%modelStat.*%` | Correct option/abort statements |
| ~8 models | `%solveLink.*%` | Correct solveLink settings |

### 5.2 Models NOT Unblocked (Require Further Work)

| Model | Missing Feature | Reason |
|-------|----------------|--------|
| gqapsdp | `$eval card(i)` | Needs compile-time set cardinality |
| spbenders4 | `$eval card(s)+1`, `%sysEnv.*%` | Needs cardinality + environment |
| emfl | `$eval %N1%*%N2%` | May work if N1/N2 are defined via `$set` |

### 5.3 Existing Tests Impact

No regressions expected — system macros are only expanded for `%name%` patterns not currently in the macro dictionary, and `$eval` directives are currently stripped (so adding evaluation changes behavior from "stripped" to "evaluated + stripped", which is strictly better).

---

## 6. Test Plan

### 6.1 Unit Tests

```python
class TestEvalDirective:
    def test_simple_subtraction(self):
        """$eval NM1 %N%-1 with N=10 → NM1=9"""

    def test_multiplication(self):
        """$eval xmax %imax%*%jmax% with imax=4, jmax=7 → xmax=28"""

    def test_addition(self):
        """$eval DIM %DIM%+1 with DIM=999 → DIM=1000"""

    def test_card_returns_zero_with_warning(self):
        """$eval imax card(i) → imax=0 (with warning)"""

    def test_undefined_macro_skips(self):
        """$eval x %undefined%-1 → warning, x not defined"""

    def test_nested_parentheses(self):
        """$eval x (3+4)*2 → x=14"""

class TestSystemMacros:
    def test_system_nlp_expanded(self):
        """option nlp = %system.nlp% → option nlp = CONOPT"""

    def test_modelstat_optimal(self):
        """m.modelStat = %modelStat.optimal% → m.modelStat = 1"""

    def test_solvelink_loadlibrary(self):
        """solveLink = %solveLink.loadLibrary% → solveLink = 5"""

    def test_unknown_system_macro_left_as_is(self):
        """%system.unknown% left unchanged"""

class TestSetGlobal:
    def test_setglobal_treated_as_set(self):
        """$setglobal name value → same as $set name value"""

    def test_setlocal_treated_as_set(self):
        """$setlocal name value → same as $set name value"""
```

### 6.2 Integration Tests

```python
class TestSpringchainExpansion:
    def test_springchain_parses(self):
        """springchain.gms parses successfully with $eval support"""

    def test_springchain_macro_values(self):
        """Verify N=10, NM1=9 after preprocessing"""

class TestSarasExpansion:
    def test_saras_system_nlp_expanded(self):
        """saras.gms: option nlp = %system.nlp% → option nlp = CONOPT"""
```

### 6.3 Regression Tests

- Run `make test` — all existing 3,715 tests must pass
- Run pipeline retest on all 160 models — verify no regressions in parse/translate/solve/match counts

---

## 7. Implementation Plan

### Phase 1: System Macros (1–2h)
1. Add `SYSTEM_MACROS` constant dictionary
2. Initialize macros from `SYSTEM_MACROS` in `_preprocess_content()`
3. Add unit tests for system macro expansion
4. Run `make test` to verify no regressions

### Phase 2: `$eval` Directive (2–3h)
1. Implement `_safe_eval_int()` recursive descent evaluator
2. Implement `process_eval_directives()` function
3. Implement `strip_eval_directives()` function
4. Insert into pipeline between Steps 2 and 3
5. Add unit tests
6. Test against springchain.gms

### Phase 3: `$setglobal` / `$setlocal` (30min)
1. Update `extract_set_directives()` regex to match `$setglobal`/`$setlocal`
2. Update `strip_set_directives()` to strip these variants
3. Add unit test

### Phase 4: Integration & Regression (1–2h)
1. Run full test suite
2. Pipeline retest all 160 models
3. Verify springchain and saras parse correctly
4. Document any new models that start parsing/translating

---

## 8. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| System macro values wrong for specific models | Medium | Low | Values only affect `option` statements and abort conditions; incorrect values don't affect mathematical formulation |
| `$eval` evaluation order matters | Low | Medium | Corpus has no interdependent `$eval` chains; our line-by-line processing matches GAMS order |
| Existing tests break from new macro expansion | Low | High | System macros use dotted names (`system.nlp`) that don't collide with user macro names |
| `card()` in `$eval` needed for target models | Low | Low | Only 3 instances across 2 models use `card()` in `$eval`; none are Sprint 21 targets |

---

## 9. Out of Scope (Deferred)

- `$eval` with `card()` function (requires set cardinality at preprocess time)
- `%sysEnv.*%` environment variable macros (4 corpus uses, all in non-target models)
- `$batInclude` positional parameter macros `%1`–`%9` (already handled by existing code)
- `$macro` function `.local` scoping issues (known GAMS bug per documentation)


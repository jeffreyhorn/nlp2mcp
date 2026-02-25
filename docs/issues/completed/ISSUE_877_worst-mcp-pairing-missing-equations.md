# worst: MCP Model Pairing Error — Dollar-Conditioned Equations Dropped from KKT

**GitHub Issue:** [#877](https://github.com/jeffreyhorn/nlp2mcp/issues/877)
**Status:** FIXED
**Severity:** High — Model compiles but GAMS rejects MCP model ($483)
**Date:** 2026-02-25
**Affected Models:** worst

---

## Problem Summary

The worst model translates to MCP but GAMS rejects it with error $483 ("Mapped variables
have to appear in the model"). The stationarity equation `stat_q(t)` is emitted as
`0 =E= 0` — completely empty — because the original equations `dd1` and `dd2` that
reference variable `q(t)` were dropped entirely from the KKT system.

---

## Root Causes (Multiple)

### 1. Acronym Values Lost During Parsing
`_parse_table_value()` converted acronym identifiers (`future`, `call`, `puto`) to `0.0`.
The `ParameterDef.values` type was `dict[..., float]` with no provision for string values.
The condition evaluator (`condition_eval.py`) also lacked support for the `=` operator
and acronym-to-acronym comparisons.

### 2. Missing Acronym Declarations in MCP Output
The emitter never produced `Acronym` declarations, so GAMS could not interpret acronym
values in parameter data. Acronyms were also incorrectly emitted as `Scalar` declarations
with value 0.

### 3. Condition Evaluation Fallback Missing
`enumerate_equation_instances()` returned 0 instances for dollar-conditioned equations
when the condition couldn't be evaluated at compile time, causing equations to be dropped.

### 4. Dollar Condition Not Propagated to Indexed Stationarity
The indexed Jacobian path in `_add_indexed_jacobian_terms()` didn't propagate equation
dollar conditions, unlike the scalar path.

### 5. Empty Stationarity Equations Without Guard
When ALL terms in a stationarity equation are dollar-conditioned, instances where no
conditions hold produce `0 =E= 0`. For equations with sum-lifted conditions (where
inner conditions reference sum indices not in the equation domain), the guard condition
needed to be wrapped in an existence check: `sum((extra_indices), 1$cond)`.

---

## Fix Details

### Files Changed

| File | Change |
|------|--------|
| `src/ir/symbols.py` | Changed `ParameterDef.values` type from `float` to `float \| str` |
| `src/ir/parser.py` | `_parse_table_value()` preserves acronym values as strings |
| `src/ir/condition_eval.py` | Added `=` operator, acronym support in SymbolRef/ParamRef |
| `src/emit/emit_gams.py` | Emit `Acronym` declarations before parameters |
| `src/emit/original_symbols.py` | Skip acronyms from Scalar emission; handle str values in `_format_param_value()` |
| `src/ad/index_mapping.py` | Fallback: include all instances when condition filters all out |
| `src/kkt/stationarity.py` | Dollar condition propagation in indexed path; `_extract_all_conditioned_guard()` with sum-lifted conditions |

### Result
- worst: **0 compilation errors** (was $483), **Solver Status 1 Normal Completion**, **Model Status 1 Optimal**
- All 3783 tests pass

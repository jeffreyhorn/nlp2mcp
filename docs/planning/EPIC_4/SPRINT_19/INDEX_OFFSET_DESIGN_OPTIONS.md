# IndexOffset IR Design Options

**Date:** 2026-02-13
**Task:** Sprint 19 Prep Task 6
**Purpose:** Evaluate design options for IndexOffset IR support to enable GAMS lead/lag indexing

---

## Executive Summary

The IndexOffset IR node type **already exists** in `src/ir/ast.py` (implemented Sprint 9 Day 3) and is already integrated into the grammar and emit layer. This document evaluates the existing design against alternatives, confirms it is the correct approach, and identifies the remaining work needed in the AD and KKT pipeline stages to fully support the 8 blocked models.

**Key finding:** The existing Option B design (IndexOffset as a standalone IR node used within VarRef/ParamRef index tuples) is the correct approach. No IR redesign is needed. The remaining work is:
1. Parser semantic handler already constructs IndexOffset nodes from parse trees (`src/ir/parser.py:786-933`) — no additional parser work needed
2. AD: implement IndexOffset-aware index substitution/mapping when collapsing sums (extend `_apply_index_substitution` in `src/ad/derivative_rules.py` so lead/lag indices are substituted correctly) (~4h)
3. KKT stationarity: structurally compatible with IndexOffset indices, but end-to-end correctness depends on the AD changes above — no additional KKT-specific work anticipated
4. Emit layer already handles IndexOffset via `_format_mixed_indices()` — no changes needed

**Effort estimate:** 8h total (4h AD index-substitution work + 2h end-to-end pipeline tracing + 2h testing/integration), down from 14-16h originally estimated in GOALS.md.

---

## GAMS Lead/Lag Semantics

### Syntax Forms

| Syntax | Name | Semantics | Boundary Behavior |
|--------|------|-----------|-------------------|
| `x(t+1)` | Linear lead | Value at next element in ordered set | Returns 0 / suppressed if out of bounds |
| `x(t-1)` | Linear lag | Value at previous element | Returns 0 / suppressed if out of bounds |
| `x(t++1)` | Circular lead | Value at next element, wrapping | Wraps: last → first |
| `x(t--1)` | Circular lag | Value at previous element, wrapping | Wraps: first → last |
| `x(t+n)` | Multi-period lead | Value n elements forward | Same as single lead |
| `x(t-n)` | Multi-period lag | Value n elements backward | Same as single lag |
| `x(t+j)` | Symbolic lead | Value offset by symbol j | Resolved at runtime |

### Key Properties

1. **Set ordering required:** Lead/lag only works on ordered sets. Unordered sets produce errors.
2. **Independent variables:** In dynamic optimization, `x(t)` and `x(t+1)` are treated as **separate decision variables**. Differentiating with respect to `x(t)` gives 0 for expressions involving only `x(t+1)`, and vice versa.
3. **GAMSLib usage:** Analysis of the repository shows only circular lead (`++`) is used in GAMSLib models (e.g., himmel16.gms uses `i++1`). Linear lead/lag appears in the 8 blocked models.
4. **Circular vs. linear distinction:** Critical for correctness — circular wraps around set boundaries, linear suppresses (returns 0).

---

## Current IR AST Node Structure

### Node Hierarchy

```
Expr (base class)
├── Value Nodes: Const, SymbolRef, CompileTimeConstant
├── Reference Nodes: VarRef, ParamRef, EquationRef, MultiplierRef
├── Operator Nodes: Unary, Binary
├── Aggregation Nodes: Sum, Prod
├── Function/Test Nodes: Call, SetMembershipTest, DollarConditional
└── Index Control Nodes: IndexOffset, SubsetIndex
```

### VarRef Index Storage

All reference nodes (VarRef, ParamRef, EquationRef, MultiplierRef) use the same index pattern:

```python
@dataclass(frozen=True)
class VarRef(Expr):
    name: str
    indices: tuple[str | IndexOffset, ...] = ()
```

The `indices` tuple accepts both plain string indices (`"i"`, `"t"`) and `IndexOffset` objects. The `indices_as_strings()` method converts IndexOffset objects to GAMS syntax strings for display.

### Existing IndexOffset Node

**Location:** `src/ir/ast.py:256-370`

```python
@dataclass(frozen=True)
class IndexOffset(Expr):
    base: str       # Base identifier (e.g., 'i', 't')
    offset: Expr    # Offset expression (Const, SymbolRef, etc.)
    circular: bool  # True for ++/--, False for +/-
```

**Supported representations:**
- `IndexOffset("i", Const(1), circular=True)` → `i++1`
- `IndexOffset("i", Const(-2), circular=True)` → `i--2`
- `IndexOffset("i", Const(1), circular=False)` → `i+1`
- `IndexOffset("t", Const(-1), circular=False)` → `t-1`
- `IndexOffset("i", SymbolRef("j"), circular=False)` → `i+j`

---

## Design Options Evaluated

### Option A: IndexOffset as Attribute of VarRef

**Description:** Store offset information directly on the VarRef node as additional attributes, rather than in the index tuple.

```python
@dataclass(frozen=True)
class VarRef(Expr):
    name: str
    indices: tuple[str, ...]  # Plain strings only
    offsets: tuple[int | None, ...] = ()  # Per-index offset
    circular: tuple[bool, ...] = ()       # Per-index circular flag
```

**Example:** `x(i, t+1)` → `VarRef("x", ("i", "t"), offsets=(None, 1), circular=(None, False))`

**Assessment:**

| Stage | Impact | Notes |
|-------|--------|-------|
| Parser | Medium | Must populate offsets/circular tuples from parse tree |
| AD | Medium | Index matching needs to compare base+offset, not just string |
| KKT | Medium | Stationarity must generate different equations per offset instance |
| Emit | Medium | Must reconstruct GAMS syntax from separate attributes |

**Pros:**
- Clear separation of identity (base index) from modification (offset)
- VarRef indices stay as plain strings

**Cons:**
- Breaks the existing index storage pattern used by all reference nodes
- Requires parallel tuples that must stay synchronized
- Cannot support symbolic offsets easily (offset as `int | None` is too restrictive)
- Would require modifying ParamRef, EquationRef, MultiplierRef identically
- Doesn't leverage the existing IndexOffset node

**Verdict:** ❌ REJECTED — Duplicates functionality, breaks existing patterns, restrictive type.

---

### Option B: IndexOffset as Standalone IR Node in Index Tuple (EXISTING DESIGN)

**Description:** IndexOffset is a separate `Expr` node that appears inside the `indices` tuple of reference nodes. This is the **current implementation**.

```python
@dataclass(frozen=True)
class IndexOffset(Expr):
    base: str
    offset: Expr
    circular: bool

@dataclass(frozen=True)
class VarRef(Expr):
    name: str
    indices: tuple[str | IndexOffset, ...] = ()
```

**Example:** `x(i, t+1)` → `VarRef("x", ("i", IndexOffset("t", Const(1), False)))`

**Assessment:**

| Stage | Impact | Notes |
|-------|--------|-------|
| Parser | None | Grammar and semantic handler both already implemented (`src/ir/parser.py:786-933`) |
| AD | Low | `_diff_varref()` tuple equality works; but `_apply_index_substitution` needs extension for IndexOffset |
| KKT | None | Stationarity enumeration already iterates over all index combinations; depends on AD fix |
| Emit | None | `_format_mixed_indices()` already handles IndexOffset via `to_gams_string()` |

**Pros:**
- Already implemented and tested (Sprint 9 Day 3, Sprint 18 Day 3)
- Clean composition — IndexOffset is just another Expr in the index tuple
- Supports arbitrary offset expressions (Const, SymbolRef, Binary, etc.)
- AD differentiation matching works via frozen dataclass equality (`_diff_varref()`)
- Emit layer already handles it (`_format_mixed_indices()` at `src/emit/expr_to_gams.py:180`)
- Grammar already has lead/lag rules (`gams_grammar.lark:310-340`)
- Parser semantic handler already constructs IndexOffset (`src/ir/parser.py:786-933`)
- All four reference nodes share the same `tuple[str | IndexOffset, ...]` pattern

**Cons:**
- Index tuple has mixed types (`str | IndexOffset`) — slightly less uniform
- `to_gams_string()` doesn't support complex offset expressions (raises `NotImplementedError`)

**Verdict:** ✅ RECOMMENDED — Already implemented, proven correct, minimal remaining work.

---

### Option C: IndexOffset as Modified Index String

**Description:** Transform lead/lag indices to modified strings at parse time, storing the offset information encoded in the string.

```python
# No IndexOffset node — just strings with encoding
VarRef("x", ("i", "t__LEAD_1_LINEAR"))  # x(i, t+1)
VarRef("y", ("t__LAG_2_CIRCULAR",))     # y(t--2)
```

**Assessment:**

| Stage | Impact | Notes |
|-------|--------|-------|
| Parser | Low | Parse tree → encoded string transformation |
| AD | Low | String equality still works for matching |
| KKT | Low | Would need to decode strings for index resolution |
| Emit | High | Must parse encoded strings back to GAMS syntax — fragile |

**Pros:**
- Index tuple stays as `tuple[str, ...]` — uniform type
- Simple parser integration

**Cons:**
- String encoding is fragile and error-prone
- Loss of semantic information (offset as string vs. Expr)
- Cannot support symbolic offsets (`t+j`) without complex encoding
- Emit must parse/decode strings — reverse of what parser does
- No support for complex offset expressions
- Violates the principle of preserving semantic structure in the IR

**Verdict:** ❌ REJECTED — Fragile, information-losing, doesn't support symbolic offsets.

---

### Option D: IndexOffset as Wrapper Node Around Full Expression

**Description:** Create a wrapper node that wraps an entire variable reference, rather than appearing inside the index tuple.

```python
@dataclass(frozen=True)
class LeadLag(Expr):
    child: VarRef           # The wrapped variable reference
    index_name: str         # Which index to offset
    offset: Expr            # Offset expression
    circular: bool          # Circular flag

# x(i, t+1) → LeadLag(VarRef("x", ("i", "t")), "t", Const(1), False)
```

**Assessment:**

| Stage | Impact | Notes |
|-------|--------|-------|
| Parser | Medium | Must construct wrapper after VarRef is built |
| AD | High | Differentiation must unwrap LeadLag to find VarRef, then re-wrap |
| KKT | High | All VarRef-handling code must also check for LeadLag wrappers |
| Emit | Medium | Must detect wrapper and emit correct syntax |

**Pros:**
- Clean separation — VarRef stays simple
- Explicit about what is being modified

**Cons:**
- Every pipeline stage that handles VarRef must also handle LeadLag
- AD differentiation rules become more complex (must look inside wrapper)
- KKT enumeration must unwrap to find variable name and indices
- Emit must detect wrapping pattern
- Not compatible with existing emit code that expects IndexOffset in indices
- Significantly more code changes across the pipeline

**Verdict:** ❌ REJECTED — Invasive changes across all pipeline stages, breaks existing code.

---

## Design Comparison Summary

| Criterion | Option A (Attribute) | Option B (Standalone Node) | Option C (String) | Option D (Wrapper) |
|-----------|---------------------|---------------------------|-------------------|-------------------|
| Already implemented | No | **Yes** | No | No |
| Parser impact | Medium | **None** | Low | Medium |
| AD impact | Medium | **Low** | Low | High |
| KKT impact | Medium | **None** | Low | High |
| Emit impact | Medium | **None** | High | Medium |
| Symbolic offsets | Limited | **Full** | No | Full |
| Type safety | Medium | **High** | Low | High |
| Code changes needed | ~200 lines | **~50 lines** | ~100 lines | ~300 lines |

---

## Recommended Design: Option B (Existing Implementation)

Option B is the clear winner — it's already implemented, tested, and integrated into the emit layer. The remaining work is minimal:

### Remaining Work

#### 1. Parser: Already Complete (0h)

The grammar already parses lead/lag syntax into tree nodes (`gams_grammar.lark:310-340`), and the semantic handler in `src/ir/parser.py` already constructs `IndexOffset` objects from the parse tree. The `_process_index_expr()` function (`src/ir/parser.py:786-933`) handles all four forms:
- `circular_lead` → `IndexOffset(base, offset, circular=True)`
- `circular_lag` → `IndexOffset(base, Const(-offset), circular=True)`
- `linear_lead` → `IndexOffset(base, offset, circular=False)`
- `linear_lag` → `IndexOffset(base, Const(-offset), circular=False)`

No additional parser work is needed.

#### 2. AD: Index Substitution Extension (~4h)

The AD system's `_diff_varref()` function uses frozen dataclass equality for index matching, which handles IndexOffset correctly:
- `IndexOffset("t", Const(1), False) == IndexOffset("t", Const(1), False)` → `True`
- `IndexOffset("t", Const(1), False) != "t"` → correct independent variable treatment

However, the AD sum-collapse/index-substitution logic has an explicit limitation. In `_apply_index_substitution` (`src/ad/derivative_rules.py:1788`), the code currently skips IndexOffset objects when substituting indices:

```python
# For now, only substitute string indices (IndexOffset not supported in AD yet)
new_indices = tuple(
    substitution.get(idx, idx) if isinstance(idx, str) else idx for idx in expr.indices
)
```

This means that when the AD system collapses sum expressions and substitutes concrete indices for symbolic ones, IndexOffset objects are passed through unchanged. For full IndexOffset support, `_apply_index_substitution` needs to be extended to:
1. Detect when an IndexOffset's `base` matches a substitution key
2. Create a new IndexOffset with the substituted base (e.g., `IndexOffset("i", Const(1), False)` with substitution `{"i": "i1"}` → `IndexOffset("i1", Const(1), False)`)

This is a localized change (~50 lines) but requires careful testing.

#### 3. KKT: No Direct Changes Needed (0h)

Stationarity equations enumerate variable instances by iterating over set members. IndexOffset indices are carried through the enumeration as-is. The KKT builder generates one stationarity equation per variable instance, and the index matching ensures correct gradient computation. End-to-end correctness depends on the AD index-substitution fix above.

#### 4. Emit: Already Complete (0h)

`_format_mixed_indices()` in `src/emit/expr_to_gams.py:180` already detects `IndexOffset` objects and emits them via `to_gams_string()`. The Sprint 18 Day 3 fix specifically addressed the quoting issue where IndexOffset expressions were being treated as strings. `_is_index_offset_syntax()` at `src/emit/expr_to_gams.py:69` provides heuristic detection for mixed string inputs.

#### 5. End-to-End Pipeline Tracing and Testing (~4h)

- Trace the `unsup_index_offset` error classification to understand where models are currently rejected
- Test the 8 blocked models end-to-end after AD fix
- Verify correct MCP output for models with lead/lag expressions
- Integration test with himmel16.gms (circular lead, already parses)

---

## 8 Blocked Models

The following 8 models are blocked by `unsup_index_offset` at the translate stage:

### Direct Lead/Lag Parse Failures (Subcategory D)

| # | Model | Failing Syntax | Pattern |
|---|-------|---------------|---------|
| 1 | **launch** | `+` in index | `x(t+1)` — Launch vehicle optimization |
| 2 | **mine** | `+` in index | `x(t+1)` — Mine scheduling |
| 3 | **sparta** | `-` in index | `x(t-1)` — Spatial equilibrium |
| 4 | **tabora** | `+` in index | `x(t+1)` — Dynamic model |

### Cascading Failures from Lead/Lag (Subcategory B)

| # | Model | Root Cause | Notes |
|---|-------|-----------|-------|
| 5 | **ampl** | `x(t+1)` | Cascading parse failure from lead/lag |
| 6 | **otpop** | `x(t+1)` | Cascading parse failure from lead/lag |

### Pipeline-Stage Failures Involving Lead/Lag

| # | Model | Error Type | Notes |
|---|-------|-----------|-------|
| 7 | **robert** | `path_syntax_error` (E170) | Lead index domain violation after parsing |
| 8 | **pak** | `path_solve_terminated` | Lead/lag expressions quoted as strings (Sprint 18 Day 3) |

**Source:** `docs/planning/EPIC_4/SPRINT_19/LEXER_ERROR_CATALOG.md` (Subcategory D), GOALS.md line 159.

---

## Grammar and Parser Status

Both the grammar and semantic handler are **already fully implemented**. No changes are needed.

### Existing Grammar Rules (`gams_grammar.lark:310-340`)

```lark
index_list: index_expr ("," index_expr)*

index_expr: ID "(" index_list ")" lag_lead_suffix?  -> index_subset
          | ID "[" index_list "]" lag_lead_suffix?  -> index_subset
          | ID lag_lead_suffix?                     -> index_simple
          | STRING                                  -> index_string

lag_lead_suffix: CIRCULAR_LEAD offset_expr   -> circular_lead
               | CIRCULAR_LAG offset_expr    -> circular_lag
               | PLUS offset_expr            -> linear_lead
               | MINUS offset_expr           -> linear_lag

offset_expr: NUMBER                          -> offset_number
           | ID                              -> offset_variable

CIRCULAR_LEAD: "++"
CIRCULAR_LAG: "--"
```

### Existing Semantic Handler (`src/ir/parser.py:786-933`)

The `_process_index_expr()` function already constructs IndexOffset IR objects from parse tree nodes. It handles all four lag/lead forms, supports numeric and symbolic offsets, and correctly negates lag offsets. The function is called from `_process_index_list()` which is used throughout the parser for all index contexts (variable references, parameter assignments, equation definitions, etc.).

No grammar or parser changes are needed.

---

## Impact Assessment Across Pipeline Stages

| Pipeline Stage | Component | Status | Remaining Work |
|---------------|-----------|--------|----------------|
| **Parser** | Grammar rules | ✅ Done | None |
| **Parser** | Semantic handler | ✅ Done | None — `_process_index_expr()` in `src/ir/parser.py:786-933` |
| **AD** | `_diff_varref()` | ✅ Works | None — frozen dataclass equality handles IndexOffset |
| **AD** | `_apply_index_substitution()` | ⚠️ Partial | ~4h — IndexOffset skipped during sum-collapse substitution (`src/ad/derivative_rules.py:1806`) |
| **KKT** | Stationarity builder | ✅ Works | None — depends on AD fix for end-to-end correctness |
| **KKT** | Multiplier generation | ✅ Works | None — indices propagated as-is |
| **Emit** | `_format_mixed_indices()` | ✅ Done | None — Sprint 18 Day 3 fix (`src/emit/expr_to_gams.py:180`) |
| **Emit** | `to_gams_string()` | ✅ Done | None — handles all GAMS syntax forms (`src/ir/ast.py:256`) |
| **Emit** | `_is_index_offset_syntax()` | ✅ Done | None — heuristic detection (`src/emit/expr_to_gams.py:69`) |

---

## Unknowns Verified

### Unknown 7.3: IndexOffset Interaction with Automatic Differentiation

**Status:** ✅ VERIFIED

**Finding:** The core assumption about differentiation is correct: `x(t+1)` and `x(t)` are treated as independent variables during differentiation. The AD system's `_diff_varref()` function (at `src/ad/derivative_rules.py:201-275`) uses exact tuple equality: `expr.indices == wrt_indices`. Since `IndexOffset` is a frozen dataclass, `IndexOffset("t", Const(1), False) != "t"`, so `d/dx(t) [x(t+1)] = 0` automatically. Similarly, `IndexOffset("t", Const(1), False) == IndexOffset("t", Const(1), False)`, so `d/dx(t+1) [x(t+1)] = 1`. However, AD's sum-collapse/index-substitution logic (`_apply_index_substitution` in `src/ad/derivative_rules.py:1788`) still has an explicit limitation ("IndexOffset not supported in AD yet"), so full IndexOffset support in AD is **not** complete and additional work remains in that area.

**Impact on Sprint 19:** No additional work is needed to change `_diff_varref()` itself; the verified tuple-equality behavior can be reused as-is. The remaining AD effort for IndexOffset is confined to the index-substitution / sum-collapse path (extending `_apply_index_substitution` to handle `IndexOffset` correctly, ~4h). The 14-16h GOALS.md estimate can be reduced to ~8h.

### Unknown 7.4: Grammar Changes for Lead/Lag Syntax

**Status:** ✅ VERIFIED

**Finding:** The assumption is partially correct. The grammar **already supports** lead/lag syntax — the `lag_lead_suffix` rule with `CIRCULAR_LEAD`, `CIRCULAR_LAG`, `PLUS`, and `MINUS` alternatives is implemented in `gams_grammar.lark:310-340`. The `++` and `--` tokens are unambiguous (GAMS uses these exclusively for circular lead/lag). For `+` and `-`, the grammar resolves ambiguity by context: within `index_expr`, `+`/`-` followed by `offset_expr` (NUMBER or ID) is lead/lag, not arithmetic. In addition, the parser semantic code (`src/ir/parser.py:786-933`) already processes `lag_lead_suffix` into `IndexOffset` IR nodes.

**Correction:** No grammar file changes are needed, and no additional work is required in the parser semantic handler — `_process_index_expr()` already constructs `IndexOffset` nodes. The remaining work is to identify and fix the **downstream** handling of `IndexOffset` that still produces `unsup_index_offset` failures (specifically `_apply_index_substitution` in the AD module and end-to-end pipeline tracing).

**Impact on Sprint 19:** The 2h "parser spike" allocation should be spent on end-to-end IndexOffset pipeline tracing and downstream fixes (AD index substitution), not on grammar or parser work.

---

## Recommendations for Sprint 19

1. **Do not redesign the IR.** The existing IndexOffset node is correct and well-integrated.
2. **Extend `_apply_index_substitution`** (~4h) to handle IndexOffset objects during AD sum-collapse, substituting the `base` field when it matches a substitution key.
3. **Trace `unsup_index_offset` classification** (~2h) to understand where the 8 blocked models are currently rejected and map the downstream fixes needed.
4. **Test with blocked models** (~2h) — run all 8 blocked models end-to-end after AD fix and verify correct MCP output.
5. **Revise effort estimate** from 14-16h (GOALS.md) to ~8h for Sprint 19.
6. **Consider extending `to_gams_string()`** to handle complex offset expressions (currently raises `NotImplementedError` for non-trivial cases) if any of the 8 blocked models require it.

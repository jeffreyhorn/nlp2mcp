# IndexOffset IR Design Options

**Date:** 2026-02-13
**Task:** Sprint 19 Prep Task 6
**Purpose:** Evaluate design options for IndexOffset IR support to enable GAMS lead/lag indexing

---

## Executive Summary

The IndexOffset IR node type **already exists** in `src/ir/ast.py` (implemented Sprint 9 Day 3) and is already integrated into the grammar and emit layer. This document evaluates the existing design against alternatives, confirms it is the correct approach, and identifies the remaining work needed in the AD and KKT pipeline stages to fully support the 8 blocked models.

**Key finding:** The existing Option B design (IndexOffset as a standalone IR node used within VarRef/ParamRef index tuples) is the correct approach. No IR redesign is needed. The remaining work is:
1. Parser semantic handler to construct IndexOffset nodes from parse trees (~2h)
2. AD system already handles IndexOffset via tuple equality — no changes needed
3. KKT stationarity already works with IndexOffset indices — no changes needed
4. Emit layer already handles IndexOffset via `_format_mixed_indices()` — no changes needed

**Effort estimate:** 4h total (2h parser handlers + 2h testing/integration), down from 14-16h originally estimated in GOALS.md.

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

**Location:** `src/ir/ast.py:348-464`

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
| Parser | Low | Grammar already has `lag_lead_suffix` rules; semantic handler creates IndexOffset |
| AD | None | Tuple equality matching works: `IndexOffset(...)` == `IndexOffset(...)` by dataclass `eq` |
| KKT | None | Stationarity enumeration already iterates over all index combinations |
| Emit | None | `_format_mixed_indices()` already handles IndexOffset via `to_gams_string()` |

**Pros:**
- Already implemented and tested (Sprint 9 Day 3, Sprint 18 Day 3)
- Clean composition — IndexOffset is just another Expr in the index tuple
- Supports arbitrary offset expressions (Const, SymbolRef, Binary, etc.)
- AD system works automatically via frozen dataclass equality
- Emit layer already handles it (`_format_mixed_indices()` at `expr_to_gams.py:156-207`)
- Grammar already has lead/lag rules (`gams_grammar.lark:310-340`)
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
| Parser impact | Medium | **Low** | Low | Medium |
| AD impact | Medium | **None** | Low | High |
| KKT impact | Medium | **None** | Low | High |
| Emit impact | Medium | **None** | High | Medium |
| Symbolic offsets | Limited | **Full** | No | Full |
| Type safety | Medium | **High** | Low | High |
| Code changes needed | ~200 lines | **~50 lines** | ~100 lines | ~300 lines |

---

## Recommended Design: Option B (Existing Implementation)

Option B is the clear winner — it's already implemented, tested, and integrated into the emit layer. The remaining work is minimal:

### Remaining Work

#### 1. Parser Semantic Handler (~2h)

The grammar already parses lead/lag syntax into tree nodes. The semantic handler (transformer) needs to construct `IndexOffset` objects from the parse tree. Current grammar rules:

```lark
lag_lead_suffix: CIRCULAR_LEAD offset_expr   -> circular_lead
               | CIRCULAR_LAG offset_expr    -> circular_lag
               | PLUS offset_expr            -> linear_lead
               | MINUS offset_expr           -> linear_lag

offset_expr: NUMBER -> offset_number
           | ID     -> offset_variable
```

The transformer needs methods:

```python
def circular_lead(self, items):
    return ("lead", True, items[0])

def circular_lag(self, items):
    return ("lag", True, items[0])

def linear_lead(self, items):
    return ("lead", False, items[0])

def linear_lag(self, items):
    return ("lag", False, items[0])

def index_simple(self, items):
    name = str(items[0])
    if len(items) > 1 and items[1] is not None:
        direction, circular, offset = items[1]
        if direction == "lag":
            offset = Unary("-", offset) if not isinstance(offset, Const) else Const(-offset.value)
        return IndexOffset(base=name, offset=offset, circular=circular)
    return name
```

#### 2. Testing and Integration (~2h)

- Test parsing of all 4 syntax forms: `t+1`, `t-1`, `t++1`, `t--1`
- Test multi-period offsets: `t+2`, `t-3`
- Test symbolic offsets: `t+j`
- Integration test with himmel16.gms (circular lead)
- Test the 8 blocked models for parse success

#### 3. No AD Changes Needed

The AD system uses frozen dataclass equality for index matching:

```python
# In _diff_varref():
if expr.indices == wrt_indices:
    return Const(1.0)
```

Since `IndexOffset` is a frozen dataclass, Python's `==` operator compares all fields:
- `IndexOffset("t", Const(1), False) == IndexOffset("t", Const(1), False)` → `True`
- `IndexOffset("t", Const(1), False) == IndexOffset("t", Const(-1), False)` → `False` (different offset)

This means `d/dx(t+1) [x(t+1)] = 1` and `d/dx(t) [x(t+1)] = 0` **automatically** — exactly the correct behavior for treating lead/lag references as independent variables.

#### 4. No KKT Changes Needed

Stationarity equations enumerate variable instances by iterating over set members. IndexOffset indices are carried through the enumeration as-is. The KKT builder generates one stationarity equation per variable instance, and the index matching ensures correct gradient computation.

#### 5. No Emit Changes Needed

`_format_mixed_indices()` in `expr_to_gams.py:156-207` already detects `IndexOffset` objects and emits them via `to_gams_string()`. The Sprint 18 Day 3 fix specifically addressed the quoting issue where IndexOffset expressions were being treated as strings.

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

## Grammar Change Sketch

The grammar already has lead/lag rules. The remaining work is in the **semantic handler** (Lark transformer), not the grammar itself.

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

### Semantic Handler Changes Needed

The Lark transformer class needs these methods to convert parse tree nodes into IndexOffset IR objects:

```python
# In the transformer class:

def offset_number(self, items):
    """Convert offset number to Const."""
    return Const(float(items[0]))

def offset_variable(self, items):
    """Convert offset variable to SymbolRef."""
    return SymbolRef(str(items[0]))

def circular_lead(self, items):
    """Handle i++n syntax."""
    return ("lead", True, items[0])

def circular_lag(self, items):
    """Handle i--n syntax."""
    return ("lag", True, items[0])

def linear_lead(self, items):
    """Handle i+n syntax."""
    return ("lead", False, items[0])

def linear_lag(self, items):
    """Handle i-n syntax."""
    return ("lag", False, items[0])

def index_simple(self, items):
    """Handle simple index with optional lead/lag suffix."""
    name = str(items[0])
    if len(items) > 1 and items[1] is not None:
        direction, circular, offset_expr = items[1]
        if direction == "lag":
            # Negate offset for lag
            if isinstance(offset_expr, Const):
                offset_expr = Const(-offset_expr.value)
            else:
                offset_expr = Unary("-", offset_expr)
        return IndexOffset(base=name, offset=offset_expr, circular=circular)
    return name
```

### No Grammar File Changes Needed

The grammar already supports all four lead/lag forms. Only the transformer (semantic handler) needs implementation to produce IndexOffset IR nodes from the parse tree.

---

## Impact Assessment Across Pipeline Stages

| Pipeline Stage | Component | Status | Remaining Work |
|---------------|-----------|--------|----------------|
| **Parser** | Grammar rules | ✅ Done | None |
| **Parser** | Semantic handler | ❌ Missing | ~2h — transformer methods for IndexOffset construction |
| **AD** | `_diff_varref()` | ✅ Works | None — frozen dataclass equality handles IndexOffset |
| **AD** | Index enumeration | ✅ Works | None — IndexOffset carried through |
| **KKT** | Stationarity builder | ✅ Works | None — index-aware enumeration handles IndexOffset |
| **KKT** | Multiplier generation | ✅ Works | None — indices propagated as-is |
| **Emit** | `_format_mixed_indices()` | ✅ Done | None — Sprint 18 Day 3 fix |
| **Emit** | `to_gams_string()` | ✅ Done | None — handles all GAMS syntax forms |
| **Emit** | `_is_index_offset_syntax()` | ✅ Done | None — heuristic detection for mixed inputs |

---

## Unknowns Verified

### Unknown 7.3: IndexOffset Interaction with Automatic Differentiation

**Status:** ✅ VERIFIED

**Finding:** The assumption is correct. `x(t+1)` and `x(t)` are treated as independent variables during differentiation. The AD system's `_diff_varref()` function (at `src/ad/derivative_rules.py:201-275`) uses exact tuple equality: `expr.indices == wrt_indices`. Since `IndexOffset` is a frozen dataclass, `IndexOffset("t", Const(1), False) != "t"`, so `d/dx(t) [x(t+1)] = 0` automatically. Similarly, `IndexOffset("t", Const(1), False) == IndexOffset("t", Const(1), False)`, so `d/dx(t+1) [x(t+1)] = 1`. No AD changes are needed.

**Impact on Sprint 19:** Saves ~4h of estimated AD work. The 14-16h GOALS.md estimate can be reduced to ~4h.

### Unknown 7.4: Grammar Changes for Lead/Lag Syntax

**Status:** ✅ VERIFIED

**Finding:** The assumption is partially correct. The grammar **already supports** lead/lag syntax — the `lag_lead_suffix` rule with `CIRCULAR_LEAD`, `CIRCULAR_LAG`, `PLUS`, and `MINUS` alternatives is implemented in `gams_grammar.lark:310-340`. The `++` and `--` tokens are unambiguous (GAMS uses these exclusively for circular lead/lag). For `+` and `-`, the grammar resolves ambiguity by context: within `index_expr`, `+`/`-` followed by `offset_expr` (NUMBER or ID) is lead/lag, not arithmetic.

**Correction:** No grammar changes are needed. The remaining work is only in the **semantic handler** (Lark transformer) to construct IndexOffset IR nodes from the parse tree (~2h).

**Impact on Sprint 19:** The 2h "parser spike" can be spent entirely on semantic handler implementation and testing, not grammar design.

---

## Recommendations for Sprint 19

1. **Do not redesign the IR.** The existing IndexOffset node is correct and well-integrated.
2. **Implement semantic handler methods** (~2h) to construct IndexOffset from parse tree nodes.
3. **Test with blocked models** (~2h) — parse all 8 blocked models and verify correct IR construction.
4. **Revise effort estimate** from 14-16h (GOALS.md) to ~4h for Sprint 19, with remaining translation work (if any) deferred to Sprint 20-21.
5. **Consider extending `to_gams_string()`** to handle complex offset expressions (currently raises `NotImplementedError` for non-trivial cases) if any of the 8 blocked models require it.

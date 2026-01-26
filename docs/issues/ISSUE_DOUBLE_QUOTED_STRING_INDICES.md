# Issue: Double-Quoted String Indices in Generated MCP Code

**Status:** Open  
**Category:** Code Generation / Emit  
**Affected Models:** ajax, least, port, sample (4+ models)  
**Priority:** High  
**GitHub Issue:** [#571](https://github.com/jeffreyhorn/nlp2mcp/issues/571)

## Summary

The MCP code generation emits parameter references with double-escaped quotes (`""value""`) instead of properly quoted strings (`"value"`). This causes GAMS Error 409 "Unrecognizable item" because GAMS cannot parse the malformed string literal.

## Reproduction

**Model:** `data/gamslib/mcp/ajax_mcp.gms`

**Generated code (line 79):**
```gams
dem(g).. sum(m, outp(g,m)) =E= dempr(g,""demand"");
```

**GAMS Error:**
```
*** Error 409 in ajax_mcp.gms
    Unrecognizable item - skip to find a new statement
```

**Expected code:**
```gams
dem(g).. sum(m, outp(g,m)) =E= dempr(g,"demand");
```

## Root Cause Analysis

The issue occurs when:
1. The original GAMS model has a parameter indexed by a string literal: `dempr(g,"demand")`
2. During parsing, the string "demand" is captured (possibly with its quotes)
3. During emission, the index is quoted again by `_quote_indices()`
4. Result: `""demand""` (double-quoted)

**Trace:**
- Parser stores: `"demand"` (with quotes) or `demand` (without quotes)
- `_quote_indices()` adds quotes: `'"demand"'` → becomes `""demand""` when embedded

## Analysis

Looking at `src/emit/expr_to_gams.py`:

```python
def _quote_indices(indices: tuple[str, ...]) -> list[str]:
    result = []
    for idx in indices:
        # Single lowercase letter = domain variable, don't quote
        if len(idx) == 1 and idx.islower():
            result.append(idx)
        else:
            # Everything else is an element label, quote it
            result.append(f'"{idx}"')
    return result
```

If `idx` is already `"demand"` (with embedded quotes), this produces `'""demand""'`.

## Affected Models

| Model | Error Count | Example |
|-------|-------------|---------|
| ajax | 2 | `dempr(g,""demand"")` |
| least | 6+ | `dat(i,""y"")`, `dat(i,""x"")` |
| port | 4+ | Similar patterns |
| sample | 4+ | Similar patterns |

## Proposed Fix

**Location:** `src/emit/expr_to_gams.py` in `_quote_indices()`

**Approach 1: Strip existing quotes before re-quoting**
```python
def _quote_indices(indices: tuple[str, ...]) -> list[str]:
    result = []
    for idx in indices:
        # Strip any existing quotes first
        idx_clean = idx.strip('"').strip("'")
        
        # Single lowercase letter = domain variable, don't quote
        if len(idx_clean) == 1 and idx_clean.islower():
            result.append(idx_clean)
        else:
            # Everything else is an element label, quote it
            result.append(f'"{idx_clean}"')
    return result
```

**Approach 2: Fix at parse time**
- Ensure the parser strips quotes from string indices when storing them
- Store just `demand` not `"demand"`

**Approach 3: Check for existing quotes**
```python
def _quote_indices(indices: tuple[str, ...]) -> list[str]:
    result = []
    for idx in indices:
        # If already quoted, use as-is
        if idx.startswith('"') and idx.endswith('"'):
            result.append(idx)
        elif len(idx) == 1 and idx.islower():
            result.append(idx)
        else:
            result.append(f'"{idx}"')
    return result
```

## Test Case

```python
def test_quote_indices_no_double_quoting():
    """Indices should not be double-quoted."""
    # Already quoted
    assert _quote_indices(('"demand"',)) == ['"demand"']
    # Unquoted multi-char
    assert _quote_indices(('demand',)) == ['"demand"']
    # Domain variable
    assert _quote_indices(('i',)) == ['i']
```

## Related Files

- `src/emit/expr_to_gams.py`: `_quote_indices()` function (line ~60)
- `src/ir/parser.py`: String index handling during parse
- `src/ir/ast.py`: ParamRef index storage

## Notes

This is related to the S-2 fix from Sprint 16 Day 8, which added the `_quote_indices()` function. The fix correctly handles domain variables vs element labels but doesn't handle the case where indices come in already quoted from the parser.

The fix should be straightforward - just strip existing quotes before deciding whether to add them.

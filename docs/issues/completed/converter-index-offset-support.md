# Converter: IndexOffset Support in expr_to_gams

**Status:** Open  
**Priority:** Medium  
**Affects:** himmel16.gms (Tier 1), potentially other models with circular indexing  
**GitHub Issue:** [#461](https://github.com/jeffreyhorn/nlp2mcp/issues/461)

---

## Summary

The MCP converter fails when processing models that use circular index offset syntax (`i++`, `i--`) because `expr_to_gams.py` doesn't support serializing `IndexOffset` objects back to GAMS format.

## Symptoms

- **Model:** himmel16.gms
- **Parse:** SUCCESS
- **Convert:** FAILS

```
NotImplementedError: IndexOffset not yet supported in this context: IndexOffset(base='i', offset=SymbolRef(++), circular=True)
```

## Root Cause

In `src/emit/expr_to_gams.py`, the `expr_to_gams()` function calls `var_ref.indices_as_strings()` which raises `NotImplementedError` for `IndexOffset` objects.

**Location:** `src/ir/ast.py` line 50 in `indices_as_strings()` method

```python
def indices_as_strings(self) -> list[str]:
    result = []
    for idx in self.indices:
        if isinstance(idx, str):
            result.append(idx)
        elif isinstance(idx, IndexOffset):
            raise NotImplementedError(f"IndexOffset not yet supported in this context: {idx}")
        ...
```

## Example

himmel16.gms uses circular lag/lead indexing:

```gams
x(i++) =e= ...
```

The parser correctly creates an `IndexOffset` AST node:
```
IndexOffset(base='i', offset=SymbolRef(++), circular=True)
```

But when the converter tries to emit this back to GAMS format, it fails.

## Proposed Solution

Extend `indices_as_strings()` in `src/ir/ast.py` to handle `IndexOffset`:

```python
elif isinstance(idx, IndexOffset):
    if idx.circular:
        # Circular: i++ or i--
        if idx.offset and hasattr(idx.offset, 'name'):
            result.append(f"{idx.base}{idx.offset.name}")
        else:
            result.append(f"{idx.base}++")  # or i-- based on offset
    else:
        # Non-circular: i+1 or i-1
        result.append(f"{idx.base}+{idx.offset}" if idx.offset else idx.base)
```

Alternatively, add a dedicated `to_gams()` method to `IndexOffset` class.

## Impact

- **Tier 1 Parse Rate:** Currently 90% (9/10) - would become 100% (10/10) with this fix
- **Models Affected:** himmel16.gms (confirmed), potentially others using `i++`/`i--` syntax

## Testing

1. Unit test for `IndexOffset.to_gams()` or `indices_as_strings()` with IndexOffset
2. Integration test: himmel16.gms converts successfully
3. Regression test: Ensure other models still work

## References

- Sprint 12 Day 10 investigation
- `src/ir/ast.py` - IndexOffset class definition
- `src/emit/expr_to_gams.py` - Expression emitter
- `tests/fixtures/gamslib/himmel16.gms` - Test model

---

**Created:** 2025-12-12  
**Sprint:** Sprint 12 Day 10

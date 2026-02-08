# Issue: robert Translation Bug - Quoted Literal Instead of Lag Reference

**Status**: Open
**GitHub Issue**: #650 (https://github.com/jeffreyhorn/nlp2mcp/issues/650)
**Model**: `robert.gms`
**Component**: Converter / Index Expression Emission

## Summary

The `robert` model translation incorrectly emits lead/lag index references as quoted string literals (e.g., `"tt+1"`) instead of proper GAMS lag/lead expressions (e.g., `tt+1`).

## Original Model Context

The `robert.gms` model contains equations with lead/lag indexing:
```gams
sb(r,tt).. s(r,tt+1) =e= s(r,tt) - sum(p, a(r,p)*x(p,tt));
```

The `tt+1` is a lead reference that should access the next element in set `tt`.

## Bug Description

### Expected Output
```gams
sb(r,tt)$(ord(tt) < card(tt)).. s(r,tt+1) =E= s(r,tt) - sum(p, a(r,p) * x(p,tt));
```

### Actual Output
```gams
sb(r,tt).. s(r,"tt+1") =E= s(r,tt) - sum(p, a(r,p) * x(p,tt));
```

### Problems
1. `"tt+1"` is a quoted string literal, not a lead expression
2. This will not match any element in set `tt` (there's no element literally named "tt+1")
3. Missing domain restriction to avoid the last period where `tt+1` is out of range

## Root Cause

The converter's expression-to-GAMS emission is treating the lead/lag index expression as a string label and quoting it, rather than recognizing it as a dynamic index reference that should remain unquoted.

This likely occurs in `expr_to_gams.py` or the index serialization logic, where `IndexOffset` nodes may be incorrectly serialized.

## Steps to Reproduce

1. Parse `data/gamslib/raw/robert.gms` (raw GAMS models must be downloaded locally)
2. Translate to MCP format
3. Examine equations containing lead/lag references

```bash
python -c "
from src.ir.parser import parse_model_file
from src.converter.converter import Converter

ir = parse_model_file('data/gamslib/raw/robert.gms')
converter = Converter(ir)
result = converter.convert()
# Search for quoted lag patterns
import re
for line in result.output.split('\n'):
    if re.search(r'\"[a-z]+\+\d+\"', line, re.IGNORECASE):
        print(line)
"
```

## Affected Components

- `src/emit/expr_to_gams.py` - Index expression emission
- `src/ir/ast.py` - `IndexOffset.to_gams_string()` method
- `src/converter/converter.py` - Equation emission

## Additional Notes

- Domain restrictions should be added to prevent out-of-range lead/lag access
- The pattern `$(ord(tt) < card(tt))` prevents generation for the last element where `tt+1` would be undefined

## Priority

High - The generated GAMS code is syntactically valid but semantically incorrect, leading to silent failures.

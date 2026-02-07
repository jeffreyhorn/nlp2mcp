# Converter Emits GAMS Reserved Words as Parameter Names

**GitHub Issue:** #646
**GitHub URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/646

## Problem

The MCP converter emits standard mathematical constants (`pi`, `inf`, `na`, `eps`) as GAMS parameter declarations, but these are GAMS reserved/predefined words and cannot be used as user-defined identifiers.

This causes GAMS Error 2 ("Identifier expected") when compiling the converted output.

## Reproduction

1. Parse and convert any model (e.g., himmel16.gms):

```python
from src.ir.parser import parse_model_text
from src.converter.converter import Converter
from pathlib import Path

source = Path('data/gamslib/raw/himmel16.gms').read_text()
model = parse_model_text(source)
converter = Converter(model)
result = converter.convert()
print(result.output[:500])
```

2. The output begins with:

```gams
* Parameter Declarations
Parameter pi / 3.141592653589793 /;
Parameter inf / inf /;
Parameter na / nan /;
Parameter eps / 2.220446049250313e-16 /;
```

3. Compiling this with GAMS fails:

```
--- test.gms(3) 2 Mb 1 Error
*** Error   2 in test.gms
```

4. Verify these are reserved words:

```gams
Parameter pi / 1 /;   * Error 2
Parameter inf / 1 /;  * Error 2
Parameter na / 1 /;   * Error 2
Parameter eps / 1 /;  * Error 2
```

## Root Cause

The converter unconditionally emits these standard parameters in every converted model. These identifiers are predefined in GAMS:

- `pi` - Mathematical constant π (3.14159...)
- `inf` - Infinity
- `na` - Not available / missing value
- `eps` - Machine epsilon

## Proposed Solution

Since GAMS already provides these as predefined constants, the converter should:

1. **Remove emission of these parameters entirely** - GAMS already has them built-in
2. OR **Rename them** to non-reserved names (e.g., `nlp2mcp_pi`, `nlp2mcp_inf`, etc.) if explicit definitions are needed

The first option is preferred since it's simpler and uses GAMS's native constants.

## Files Involved

The parameter emission logic is likely in `src/converter/converter.py` or `src/emit/` modules.

## Impact

- All converted models fail to compile in GAMS due to these reserved word errors
- This blocks end-to-end validation of converted models

## Related Issues

- Discovered while testing Issue #461 (IndexOffset support) with himmel16.gms

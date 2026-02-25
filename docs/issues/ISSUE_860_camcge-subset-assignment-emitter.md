# Camcge: Subset-Qualified Assignment Emitted as Inline Data + Parameter Ordering

**GitHub Issue:** [#860](https://github.com/jeffreyhorn/nlp2mcp/issues/860)
**Status:** OPEN
**Severity:** Medium — Model translates but GAMS compilation fails (path_syntax_error)
**Date:** 2026-02-24
**Affected Models:** camcge

---

## Problem Summary

The camcge model parses and translates to MCP, but the emitted GAMS code fails compilation
with 15 errors. Two distinct emitter bugs are present: (1) subset-qualified parameter
assignments are incorrectly emitted as inline data blocks, and (2) parameter assignment
statements are emitted in the wrong order, causing references to undefined values.

---

## Error Details

**Error A — GAMS $170: Domain violation for element (line 33):**

```gams
gamma(i) /in 0/
```

GAMS interprets `/in 0/` as assigning the value 0 to element "in" of set `i`, but "in" is
not a member of set `i`. The original GAMS source has:

```gams
gamma(in) = 0;
```

where `in(i)` is a **subset** of `i`. The emitter incorrectly converted the subset-qualified
assignment into an inline parameter data block.

**Error B — GAMS $141: Symbol declared but no values assigned (lines 81, 87-95):**

Multiple parameters (`delta`, `ac`, `rhoc`, `rhot`, `gamma`, `eta`, `ad`, `cles`) are
referenced before their values are computed. For example:

```gams
delta(it) = pm0(it) / pd0(it) * (m0(it) / xxd0(it)) ** (1 + rhoc(it));
```

Here `rhoc(it)` is used but not yet assigned. The emitter does not preserve the original
statement ordering from the GAMS source.

---

## Reproduction Steps

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_file
from src.mcp.emitter import emit_mcp
ir = parse_file('data/gamslib/raw/camcge.gms')
mcp_code = emit_mcp(ir)
with open('/tmp/camcge_mcp.gms', 'w') as f:
    f.write(mcp_code)
print('Translate OK, check /tmp/camcge_mcp.gms')
"
# Then compile with GAMS:
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/camcge_mcp.gms action=c
```

---

## Root Cause

### Bug 1: Subset-qualified assignment emission

When the IR builder encounters `gamma(in) = 0`, it stores the assignment with subset
qualifier `in`. During MCP emission, the emitter does not distinguish between:
- Subset-qualified assignment: `gamma(in) = 0;` (assign to subset elements)
- Inline data: `gamma(i) /in 0/` (initialize with data block)

The emitter incorrectly renders the subset qualifier as an inline data key.

### Bug 2: Parameter assignment ordering

The emitter collects all parameter assignments and emits them in declaration order (or
alphabetical order) rather than preserving the original source order. This causes parameters
that depend on other computed parameters to reference undefined values.

---

## Suggested Fix

**Bug 1:** In the MCP emitter, detect when a parameter assignment uses a subset qualifier
and emit it as an executable assignment statement (`gamma(in) = 0;`) rather than as inline
data. This requires distinguishing between data-block initialization and computed assignments
in the IR.

**Bug 2:** Preserve the original source order of parameter assignment statements in the IR
and emit them in the same order. This may require adding an ordering field to the IR's
parameter storage or maintaining a separate ordered list of assignment statements.

**Effort estimate:** ~3-4h (two separate emitter fixes)

---

## Files That Need Changes

| File | Change |
|------|--------|
| `src/mcp/emitter.py` | Fix subset-qualified assignment emission; preserve statement order |
| `src/ir/model_ir.py` | Possibly add assignment ordering metadata |

---

## Related Issues

- Sprint 21 SEMANTIC_ERROR_AUDIT section 2.1 documents the original parse blocker (`sign()`)

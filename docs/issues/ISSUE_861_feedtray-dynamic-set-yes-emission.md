# Feedtray: Dynamic Set `yes$` Assignments Emitted as Arithmetic

**GitHub Issue:** [#861](https://github.com/jeffreyhorn/nlp2mcp/issues/861)
**Status:** OPEN
**Severity:** Medium — Model translates but GAMS compilation fails (path_syntax_error)
**Date:** 2026-02-24
**Affected Models:** feedtray

---

## Problem Summary

The feedtray model parses and translates to MCP, but the emitted GAMS code fails compilation
with 4 errors. The root cause is that dynamic set membership assignments using `yes$`
syntax are emitted as arithmetic parameter assignments using `1$`, creating type mismatches
in downstream expressions.

---

## Error Details

**GAMS $133: Incompatible operands for addition (lines 62-65):**

Emitted code:

```gams
reb(i) = 1$(ord(i) = 1);
con(i) = 1$(ord(i) = card(i));
col(i) = 1 - (reb(i) + con(i));        <-- $133 error
belowf(i) = 1$(ord(i) <= 6);
abovef(i) = 1 - belowf(i);             <-- $133 error
```

Original GAMS source:

```gams
reb(i) = yes$(ord(i) = 1);
con(i) = yes$(ord(i) = card(i));
col(i) = yes - (reb(i) + con(i));
belowf(i) = yes$(ord(i) le 6);
abovef(i) = yes - belowf(i);
```

In the original model, `reb`, `con`, `col`, `belowf`, and `abovef` are **dynamic sets**
whose membership is assigned using `yes$` conditionals. The emitter converts these to
numeric parameter assignments (`1$`), which changes the symbol type from set to parameter
and causes type errors in subsequent expressions that perform set arithmetic.

---

## Reproduction Steps

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_file
from src.mcp.emitter import emit_mcp
ir = parse_file('data/gamslib/raw/feedtray.gms')
mcp_code = emit_mcp(ir)
with open('/tmp/feedtray_mcp.gms', 'w') as f:
    f.write(mcp_code)
print('Translate OK, check /tmp/feedtray_mcp.gms')
"
# Then compile with GAMS:
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/feedtray_mcp.gms action=c
```

---

## Root Cause

The IR builder converts `yes$` set membership assignments into numeric `1` values during
parsing. It treats `yes` as the constant `1` rather than preserving the set-membership
semantics. When the emitter generates MCP code, it emits these as parameter assignments
(`reb(i) = 1$(...)`) instead of set membership assignments (`reb(i) = yes$(...)`).

GAMS distinguishes between:
- **Set membership**: `reb(i) = yes$(ord(i) = 1)` — assigns set membership
- **Parameter value**: `reb(i) = 1$(ord(i) = 1)` — assigns numeric value

These are semantically different: set membership supports set operations (`+`, `-`, `*` for
union, difference, intersection), while parameter values do not.

---

## Suggested Fix

**Option A: Preserve `yes` keyword in IR**

Track whether an assignment uses `yes$` vs numeric conditional in the IR. The emitter can
then emit the correct syntax. This requires adding a flag or using a sentinel value.

**Option B: Detect set-type assignments in emitter**

When emitting assignments to symbols declared as sets (not parameters), use `yes$` syntax
instead of `1$`.

**Effort estimate:** ~2-3h

---

## Files That Need Changes

| File | Change |
|------|--------|
| `src/ir/parser.py` | Preserve `yes` semantics in set membership assignments |
| `src/mcp/emitter.py` | Emit `yes$` for set membership assignments |
| `src/ir/model_ir.py` | Possibly add set-assignment metadata |

---

## Related Issues

- Sprint 21 SEMANTIC_ERROR_AUDIT section 2.2 documents the original parse blocker (`sign()`)

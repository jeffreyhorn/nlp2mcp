# Worst: Table Data Not Emitted for `f0` and `pdata` Parameters

**GitHub Issue:** [#863](https://github.com/jeffreyhorn/nlp2mcp/issues/863)
**Status:** OPEN
**Severity:** Medium — Model translates but GAMS compilation fails (path_syntax_error)
**Date:** 2026-02-24
**Affected Models:** worst

---

## Problem Summary

The worst model parses and translates to MCP, but the emitted GAMS code fails compilation
with 6 errors. The emitter correctly emits the `tdata` table with inline data, but declares
`f0(i,t)` and `pdata(i,t,j,*)` as empty parameters with no data. Variables initialized from
these empty parameters then trigger GAMS $141 errors.

---

## Error Details

**GAMS $141: Symbol declared but no values assigned (lines 75-82, 137):**

Emitted code:

```gams
Parameters
    tdata(t,*) /jun.term 0.09167, .../   <-- data present
    f0(i,t)                               <-- NO DATA
    pdata(i,t,j,*)                        <-- NO DATA
;
```

The original model declares `f0` and `pdata` as `Table` statements with multi-row data:

```gams
Table f0(i,t)  initial forward prices
              jun       sep
bond        96.65     92.14
note        97.21     93.23

Table pdata(i,t,j,*)  put and call prices ...
```

The emitter successfully captures `tdata` table data but fails to emit data for `f0` and
`pdata`. These empty parameters are then used in variable initialization:

```gams
f.l(i,t) = f0(i,t) * exp(tdata(t,"r0") * tdata(t,"term"));    <-- $141 on f0
```

Additionally, the acronym values (`future`, `call`, `puto`) used in conditions like
`pdata(i,t,j,"type") = call` fail because `pdata` has no values to compare against.

---

## Reproduction Steps

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_file
from src.mcp.emitter import emit_mcp
ir = parse_file('data/gamslib/raw/worst.gms')
mcp_code = emit_mcp(ir)
with open('/tmp/worst_mcp.gms', 'w') as f:
    f.write(mcp_code)
print('Translate OK, check /tmp/worst_mcp.gms')
"
# Then compile with GAMS:
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/worst_mcp.gms action=c
```

---

## Root Cause

The IR builder parses `Table` declarations and stores data in the parameter's `values` dict.
However, for multi-dimensional tables with wildcard domains (`pdata(i,t,j,*)`), the table
data parsing may fail silently — the parameter is created but left empty. The emitter then
emits the parameter declaration without inline data.

This may be related to how the table parser handles the `*` (star/wildcard) domain and
multi-line tabular data formats. The `tdata` table works because it has a simpler structure
(`tdata(t,*)`), while `f0(i,t)` and `pdata(i,t,j,*)` have more complex multi-dimensional
structures.

---

## Suggested Fix

Debug the table data parsing path in the IR builder for `f0(i,t)` and `pdata(i,t,j,*)`.
Verify that:

1. The table header (column labels) is correctly parsed for multi-dimensional tables
2. The row data is correctly associated with the right index combinations
3. The `*` domain in `pdata(i,t,j,*)` is handled correctly

**Effort estimate:** ~3-4h (table data parsing investigation + fix)

---

## Files That Need Changes

| File | Change |
|------|--------|
| `src/ir/parser.py` | Fix table data parsing for multi-dimensional tables |
| `src/mcp/emitter.py` | Verify table data emission handles all captured data |

---

## Related Issues

- **Issue #809** (completed): Previous worst parse blocker (equation negative in function arg)
- Sprint 21 SEMANTIC_ERROR_AUDIT section 2.6 documents the acronym handling fix

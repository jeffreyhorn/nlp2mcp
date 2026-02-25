# Cesam2: Alias Domain Resolution Failure During Translation

**GitHub Issue:** [#858](https://github.com/jeffreyhorn/nlp2mcp/issues/858)
**Status:** OPEN
**Severity:** Medium — Model parses but fails at translate stage
**Date:** 2026-02-24
**Affected Models:** cesam2

---

## Problem Summary

The cesam2 model parses successfully (fixed in Sprint 21 Day 1 by adding `centropy` to
FUNCNAME) but fails during the translation stage with an `internal_error`. The error occurs
when the AD/index mapping module tries to enumerate equation instances for `ASAMEQ(ii,jj)`
and cannot resolve the domain set `jj` because it is an alias for `ii` with no concrete
members at build time.

---

## Error Details

```
Error: Invalid model - Equation 'asameq' uses domain set 'jj' which has no members
```

---

## Reproduction Steps

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_file
from src.mcp.emitter import emit_mcp
ir = parse_file('data/gamslib/raw/cesam2.gms')
mcp_code = emit_mcp(ir)
"
```

---

## Root Cause

The model declares alias pairs at line 103:

```gams
Alias (i,j), (ii,jj);
```

This creates `j` as alias for `i`, and `jj` as alias for `ii`. The equation `ASAMEQ`
uses `(ii,jj)` as its domain:

```gams
ASAMEQ(ii,jj)$ICOEFF(ii,jj)..   A(ii,jj) =e= abar0(ii,jj)*EXP(ERR3(ii,jj));
```

The translation stage (`src/ad/index_mapping.py`, `resolve_set_members()` function, around
lines 354-360) tries to enumerate all instances of this equation by resolving the domain
sets. When it encounters `jj`, it attempts alias resolution but `jj` → `ii` → no concrete
members defined at parse time (members come from data blocks loaded at runtime).

In GAMS, alias domains are resolved dynamically at solve time. The IR builder correctly
stores the alias relationship, but the translation pipeline assumes all indexed equation
domains have concrete set members at build time.

---

## Suggested Fix

**Option A: Resolve aliases transitively to the base set**

When `resolve_set_members()` encounters an alias, follow the alias chain to the base set
and use its members. If `jj` → `ii` → `i`, and `i` has members from data blocks, use those
members for `jj`.

**Option B: Propagate dynamic subset data through aliases**

During IR construction, when populating set members from data blocks, also populate alias
set members. This requires the IR builder to track alias relationships and propagate member
data.

**Effort estimate:** ~2-3h (requires understanding of alias resolution in index_mapping.py)

---

## Files That Need Changes

| File | Change |
|------|--------|
| `src/ad/index_mapping.py` | Fix `resolve_set_members()` to follow alias chains |
| `src/ir/parser.py` | Possibly propagate members through alias definitions |

---

## Related Issues

- **Issue #817** (completed): Previous cesam2 blocker (conditional assignment in loop parsing)
- This is a **separate, downstream** issue from #817; cesam2 now parses but fails at translate

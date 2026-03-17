# indus: Translation Blocked by Injection-Safety Check + GAMS Line Length Limit

**GitHub Issue:** [#934](https://github.com/jeffreyhorn/nlp2mcp/issues/934)
**Status:** FIXED
**Severity:** Medium — Translation fails due to injection-safety check; secondary line-length issue
**Date:** 2026-02-26 (updated 2026-03-16)
**Affected Models:** indus
**Sprint:** 21 (Day 11 triage), fixed Sprint 22 Day 12

---

## Problem Summary

The `indus.gms` model (GAMSlib SEQ=159, "Indus Agricultural Model") parses successfully but **fails during MCP translation** because the model contains set elements with double-quote characters (e.g., `"sc-mill"`). The `_sanitize_set_element()` function rejects these as injection-unsafe.

A secondary concern was that some generated equation definitions might exceed GAMS's maximum line length (~80000 characters).

---

## Fix: Double-Quoted Set Element Normalization (RESOLVED)

### Root Cause
The GAMS model uses variable bounds with double-quoted string literals as indices, e.g., `xca.up(g,"sc-mill")`. The parser stores these as `'"sc-mill"'` (with embedded double quotes) in the variable's `up_expr_map`. When the emitter calls `_sanitize_set_element()`, the function only handled single-quoted pre-quoted elements, rejecting double-quoted ones as containing dangerous `"` characters.

### Fix Applied
Added double-quote to single-quote normalization in `_sanitize_set_element()` in `src/emit/original_symbols.py`. Before checking for single-quoted elements, the function now detects double-quoted elements and converts them to single-quoted form (GAMS's standard quoting style). The inner content then passes through the existing single-quoted validation path.

**File changed:** `src/emit/original_symbols.py` (line ~269)
- Added normalization block: if element starts and ends with `"`, convert to `'inner'`
- The existing single-quoted validation then handles control-char and injection checks

### Verification
- Before fix: `Error: Invalid model - Set element '"sc-mill"' contains unsafe characters`
- After fix: `✓ Generated MCP: /tmp/indus_mcp.gms`

---

## Secondary Issue: Line Length Limit (NOT AN ISSUE)

The generated MCP file's longest line is 10,759 characters, well under GAMS's ~80,000 character limit. The line-length concern did not materialize — the stationarity equations for `x(g,c,t,s,w)` stay within limits.

---

## Model Details

| Property | Value |
|----------|-------|
| GAMSlib SEQ | 159 |
| Solve Type | LP |
| Convexity | verified_convex |
| Reference Objective | 901.1615 |
| Parse Status | success (~38s) |
| Translate Status | success (after fix) |
| Variables | 27 |
| Equations | 22 |
| Sets | 37 |
| Parameters | 155 |

---

## Related Issues

- iswnm: Related model (same Indus basin system)
- This model was previously blocked by a variable index arity error (`ppc` expected 0 indices but received 2), which was fixed in a prior sprint.

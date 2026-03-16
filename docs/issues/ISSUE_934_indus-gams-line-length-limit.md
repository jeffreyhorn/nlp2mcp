# indus: Translation Blocked by Injection-Safety Check + GAMS Line Length Limit

**GitHub Issue:** [#934](https://github.com/jeffreyhorn/nlp2mcp/issues/934)
**Status:** OPEN — BLOCKED
**Severity:** Medium — Translation fails due to injection-safety check; secondary line-length issue
**Date:** 2026-02-26 (updated 2026-03-16)
**Affected Models:** indus
**Sprint:** 21 (Day 11 triage), revisited Sprint 22 Day 12

---

## Problem Summary

The `indus.gms` model (GAMSlib SEQ=159, "Indus Agricultural Model") parses successfully but **fails during MCP translation** because the model contains set elements with double-quote characters (e.g., `"sc-mill"`). The `_sanitize_set_element()` function rejects these as injection-unsafe.

Even if the injection-safety blocker is fixed, a secondary issue exists: some generated equation definitions produce lines exceeding GAMS's maximum line length (~80000 characters).

---

## Current Blocker: Injection-Safety Check

### Error Message
```
Error: Invalid model - Set element '"sc-mill"' contains unsafe characters
that could cause GAMS injection. Dangerous characters: {'"'}
```

### Root Cause
The GAMS model uses set elements containing embedded double quotes (e.g., `"sc-mill"` as a set element label). The `_sanitize_set_element()` function in `src/emit/original_symbols.py` rejects any set element containing `"` as a potential GAMS injection risk.

### Reproduction
```bash
python -m src.cli data/gamslib/raw/indus.gms -o /tmp/indus_mcp.gms
# Error: Invalid model - Set element '"sc-mill"' contains unsafe characters ...
```

### Suggested Fix
The injection-safety check needs to handle quoted set element labels. In GAMS, set elements can be quoted strings. The sanitizer should:
1. Strip outer quotes from set element labels before validation
2. Or allow double quotes when they are part of the GAMS quoting syntax
3. Code location: `src/emit/original_symbols.py`, `_sanitize_set_element()` function

---

## Secondary Issue: Line Length Limit

Once the injection-safety blocker is resolved, the model will hit a GAMS line-length error:

### Root Cause
The 5-dimensional variable `x(g,c,t,s,w)` generates stationarity equations with extremely long symbolic expressions. The KKT stationarity equation `stat_x(g,c,t,s,w)` must contain Jacobian terms from all 22 equations where `x` appears, each expanded with full index substitutions and alias renaming. When these terms are concatenated on a single line, the equation definition exceeds GAMS's maximum line length.

GAMS has a hard-coded line length limit (approximately 80000 characters). The emitter currently outputs each equation definition as a single line.

### Suggested Fix
Add line-breaking to the GAMS emitter. GAMS supports continuation lines — any line can be continued by breaking at a whitespace boundary. The emitter should track line length during equation emission and insert line breaks when approaching the limit.

---

## Model Details

| Property | Value |
|----------|-------|
| GAMSlib SEQ | 159 |
| Solve Type | LP |
| Convexity | verified_convex |
| Reference Objective | 901.1615 |
| Parse Status | success (~38s) |
| Translate Status | FAIL — injection-safety check |
| Variables | 27 |
| Equations | 22 |
| Sets | 37 |
| Parameters | 155 |

---

## Related Issues

- iswnm: Related model (same Indus basin system)
- This model was previously blocked by a variable index arity error (`ppc` expected 0 indices but received 2), which was fixed in a prior sprint.

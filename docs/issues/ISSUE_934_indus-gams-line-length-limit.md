# indus: GAMS Line Length Limit — Generated MCP Has Lines >80000 Characters

**GitHub Issue:** [#934](https://github.com/jeffreyhorn/nlp2mcp/issues/934)
**Status:** OPEN
**Severity:** Medium — Model translates successfully but GAMS rejects the output due to line length
**Date:** 2026-02-26
**Affected Models:** indus
**Sprint:** 21 (Day 11 triage)

---

## Problem Summary

The `indus.gms` model (GAMSlib SEQ=159, "Indus Agricultural Model") now parses and translates successfully, but GAMS rejects the generated MCP file because some equation definitions produce lines exceeding GAMS's maximum line length (~80000 characters). The PATH solver cannot be invoked.

---

## Model Details

| Property | Value |
|----------|-------|
| GAMSlib SEQ | 159 |
| Solve Type | LP |
| Convexity | verified_convex |
| Reference Objective | 901.1615 |
| Parse Status | success (~38s) |
| Translate Status | success |
| GAMS Solve | FAIL — line length error |
| Variables | 27 |
| Equations | 22 |
| Sets | 37 |
| Parameters | 155 |

### Key Variables (selected)

| Variable | Domain | Notes |
|----------|--------|-------|
| x | (g,c,t,s,w) | 5-dimensional — primary source of long stationarity equations |
| ppc | — | Scalar (previously caused index arity error, now fixed) |
| tw | (g,m) | 2-dimensional |
| ts | (g,m) | 2-dimensional |

---

## Reproduction

```bash
# Generate MCP (succeeds)
python -m src.cli data/gamslib/raw/indus.gms -o /tmp/indus_mcp.gms

# Run GAMS (fails with line length error)
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/indus_mcp.gms lo=2
```

---

## Root Cause

The 5-dimensional variable `x(g,c,t,s,w)` generates stationarity equations with extremely long symbolic expressions. The KKT stationarity equation `stat_x(g,c,t,s,w)` must contain Jacobian terms from all 22 equations where `x` appears, each expanded with full index substitutions and alias renaming. When these terms are concatenated on a single line, the equation definition exceeds GAMS's maximum line length.

GAMS has a hard-coded line length limit (approximately 80000 characters). The emitter currently outputs each equation definition as a single line.

---

## Possible Fixes

| Approach | Impact | Effort |
|----------|--------|--------|
| Line-breaking in emitter (split long equation definitions across multiple lines using GAMS continuation syntax) | High — directly solves the issue | Low-Medium |
| Expression simplification/factoring before emission | Medium — may reduce line length | Medium |
| Emit intermediate variables for long sub-expressions | Medium — breaks up equations into smaller pieces | Medium |

**Recommended:** Add line-breaking to the GAMS emitter. GAMS supports continuation lines — any line can be continued by breaking at a whitespace boundary. The emitter should track line length during equation emission and insert line breaks when approaching the limit.

---

## Related Issues

- iswnm: Related model (same Indus basin system)
- This model was previously blocked by a variable index arity error (`ppc` expected 0 indices but received 2), which was fixed in a prior sprint.

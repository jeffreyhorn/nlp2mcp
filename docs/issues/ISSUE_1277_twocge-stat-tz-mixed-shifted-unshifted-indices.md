# twocge: `stat_tz` Mixes Shifted and Unshifted Indices (Offset-Alias KKT Consistency Bug)

**GitHub Issue:** [#1277](https://github.com/jeffreyhorn/nlp2mcp/issues/1277)
**Status:** OPEN — Deferred to Sprint 25
**Severity:** Medium — Incorrect KKT pairing in a corpus model; twocge currently fails comparison
**Date:** 2026-04-19
**Last Updated:** 2026-04-19
**Affected Models:** `twocge` (primary); likely also other two-region CGE models with offset indices
**Labels:** `sprint-25`

---

## Problem Summary

In `data/gamslib/mcp/twocge_mcp.gms` around line 497, the `stat_tz` stationarity equation's neighbor terms use inconsistent shifted/unshifted index combinations. A representative snippet:

```gams
... mu(j+1,r) ... pq(j,r) ... nu_eqXg(j+1,r) ...
```

Sibling stationarity equations in the same file (e.g., `stat_tm`, `stat_tx`) use a consistently shifted pattern — every `mu` / `pq` / `nu_*` in the neighbor term is shifted by the same `±1`. The mixed-offset pattern in `stat_tz` is the anomaly: it mixes `j+1` and `j` in what should be a single offset-group.

## Likely Root Cause

Same bug family as `polygon` (#1143) and `himmel16` (#1146): when the AD walks a body expression containing both offset (`x(t+1)`) and non-offset (`x(t)`) references to variables differentiated w.r.t. a third variable, the resulting Jacobian terms inherit offsets inconsistently. Either:

- The offset gets attached to only one operand in the derivative chain rule, or
- The offset propagation rule conflates the summation index with the constraint instance index when both are present.

For twocge specifically, the aliasing is region (`r`) plus a lead/lag over time index (`j`, `j+1`, `j-1`). That combination doesn't appear in polygon's 1D offset pattern, so it may require additional fix logic beyond what #1143 will land.

---

## Reproduction

```bash
grep -n "^stat_tz" data/gamslib/mcp/twocge_mcp.gms | head -3
grep -n "^stat_tm" data/gamslib/mcp/twocge_mcp.gms | head -3
# Compare the neighbor-term shapes: stat_tm's pattern is the reference; stat_tz's is the bug
```

## Impact

`twocge` currently fails comparison. Fixing `stat_tz` is a necessary (though likely not sufficient) step toward recovering twocge's match.

---

## Related

- **#1143** (polygon: Offset-Alias Gradient Complete Failure) — same class, 1D offset
- **#1146** (himmel16: Cyclic Offset Alias Gradient Mismatch, 43.0%)
- KNOWN_UNKNOWNS Pattern C (offset-alias) — Sprint 24 carried this forward
- **#1251** (twocge: Empty trade equations when r=rr) — DIFFERENT bug, same model
- **#1278** (twocge: `ord(r) <> ord(r)` tautology) — DIFFERENT bug, same model

## Suggested Approach

1. Ensure the general offset-alias fix planned for #1143 lands first. Re-run twocge; most of Pattern C should be fixed as a byproduct.
2. If `stat_tz` mixed-offset persists after #1143, extend the fix to also cover the 2D alias (region × time) case. The additional logic should recognize when an expression has offsets on SOME operands only and either promote all operands to the same offset group or explicitly reject the mixed form as a user-level error.

---

## Out of Scope

- twocge's other known bugs: #1251 (empty trade equations), #1278 (ord tautology), #906 (SAM data ordering).

---

## References

- PR #1273 review comment #3106233162
- #1143 (primary offset-alias fix tracking)
- Sibling Sprint 25 issues: #1275, #1276, #1278–#1280

## Estimated Effort

Likely subsumed by #1143 fix; 1–2h additional regression / verification after that lands.

---

## Files Involved

- `src/ad/*.py` — derivative chain-rule index-offset propagation
- `src/kkt/stationarity.py` — instance enumeration with offsets
- `data/gamslib/mcp/twocge_mcp.gms` — reference artifact
- `data/gamslib/raw/twocge.gms` — source model

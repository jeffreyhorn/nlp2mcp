# cesam2: PATH $141 on Phantom IndexOffset `nu_COLSUM(i±N)` References in `stat_tsam` Stationarity

**GitHub Issue:** [#1355](https://github.com/jeffreyhorn/nlp2mcp/issues/1355)
**Status:** OPEN — Sprint 26 carryforward (filed Sprint 25 Day 13)
**Severity:** Medium — model translates cleanly post-Sprint-25 SetMembershipTest fixes but PATH compilation fails; user gets no MCP solution
**Date:** 2026-05-05
**Last Updated:** 2026-05-05
**Affected Models:** cesam2 (confirmed); same Pattern C variant family as #1354 (camcge)

---

## Problem Summary

cesam2 translate succeeds (post-#1338, post-#1342, post-#1344 SetMembershipTest fixes), but the emitted MCP fails GAMS compilation with **`$141`** ("Symbol declared but no values have been assigned") on `nu_COLSUM(i±N)` references inside `$(jj(i±N))` guards in the assembled `stat_tsam(i,j)` stationarity equation.

Pre-Sprint-25 baseline: `path_solve_terminated` (translate failed). Post-Sprint-25 (Day 11 retest): `path_syntax_error` — one of the four bucket additions during Sprint 25 (see SPRINT_LOG.md Day 11 §"Revised Checkpoint 2 evaluation").

---

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/cesam2.gms \
  -o /tmp/cesam2_mcp.gms --skip-convexity-check --quiet
gams /tmp/cesam2_mcp.gms lo=2

# *** Error 141 in /tmp/cesam2_mcp.gms (line 207, line 414)
# *** Status: Compilation error(s)
```

---

## Buggy Emit — `stat_tsam(i,j)` (line 300, condensed)

```gams
stat_tsam(i,j).. (nu_ROWSUM(i)$(ii(i))
  + (nu_COLSUM(i)$(jj(i)))$(... 10 sameas conjunctions ...)
  + (((nu_COLSUM(i+7)$(jj(i+7)))$(ord(i) <= card(i) - 7))$(ord(j) = 7))$(...)
  + (((nu_COLSUM(i+1)$(jj(i+1)))$(ord(i) <= card(i) - 1))$(ord(j) = 1))$(...)
  + (((nu_COLSUM(i-9)$(jj(i-9)))$(ord(i) > 9))$(ord(j) = 9))$(...)
  + ... (i±N for N = 1..9, gated by ord(j) = N) ...
  ) =E= 0;
```

The `nu_COLSUM(i+7)`, `nu_COLSUM(i-9)`, etc. references are emitted for offsets the `i` set never realizes for those `j` ranges, triggering `$141`. The triple-nested `$cond` guards (column-offset bound + row-offset bound + per-`sameas` matrix-block guard) are correct in spirit — they encode the SAM block structure — but the multiplier `nu_COLSUM(i+N)` is referenced at indices outside `nu_COLSUM`'s declared domain, which GAMS rejects regardless of whether the guard would mask it at runtime.

---

## Likely Root Cause

Same Pattern C family as **#1354 (camcge)**: per-offset `nu_<eq>(i±N)` enumeration in stationarity where the source SAM-balance equation `tsam(i,j)` uses `sameas`-conditional aliases that the AD layer expands into per-offset terms instead of a single domain-scoped sum.

The `sameas('ACT', 'CAP')`-style guards in cesam2's source SAM block are decomposed into per-`(row,col)` pairs by the AD layer, and each pair gets a literal `i+N` IndexOffset emission rather than a sum-over-`j$(jj(j) and sameas(...))` consolidation.

---

## Where to Fix

`src/kkt/stationarity.py` — same broadening as **#1354**: detect plain-alias enumeration (no `$cond` filter required, and additionally allow `sameas`-decomposed shapes) and consolidate per-offset emission into a single domain-scoped sum:

```gams
sum(j$(jj(j) and sameas_block_filter(i,j)),
    nu_COLSUM(j))
```

scoped to the equation's declared domain.

The Pattern C gate currently only fires for the launch-specific `$ge(ss, s)` shape; needs to also fire for plain `imat(i,j)`-style alias-only references (#1354) and `sameas`-decomposed SAM-block references (this issue).

---

## Tests to Add

- **Unit test** in `tests/unit/kkt/`: minimal `ModelIR` with a scalar SAM-balance equation `tsam(i,j).. ROWSUM(i) - sum(jp$(jj(jp) and sameas(jp, j)), COLSUM(jp)) =e= 0`. Assert that `stat_tsam(i,j)` body has no `nu_COLSUM(i+N)$(jj(i+N))` references for `N != 0`.
- **Integration test** in `tests/integration/emit/`: assert cesam2's emitted `stat_tsam(i,j)` has no `nu_COLSUM(i+N)` substring for `N >= 1`.
- **Pipeline check**: after fix, cesam2 moves out of `path_syntax_error`. Open question whether it then surfaces #1041 (MCP pair empty equation, separate root cause) — verify post-fix.

---

## Files Involved

- `src/kkt/stationarity.py` — Pattern C gate (needs `sameas`-aware widening)
- `src/ad/constraint_jacobian.py` — alias unification path producing the per-offset enumeration
- `src/ir/condition_eval.py` — `sameas` evaluator (no fix needed; mentioned for context)
- `data/gamslib/raw/cesam2.gms` — primary integration test source
- `data/gamslib/mcp/cesam2_mcp.gms` — current buggy emit

---

## Estimated Effort

**4–8h** if the fix lands as part of #1354 (likely the same code path, plus a `sameas`-block helper). Standalone effort would be ~6–10h.

---

## Related

- **#1041** (cesam2: MCP pair empty equation — separate bug, also open).
- **#1338, #1342, #1344** (cesam2 SetMembershipTest fixes that unblocked translate).
- **#1354** (camcge — same Pattern C variant family, simpler shape; fix likely shared).

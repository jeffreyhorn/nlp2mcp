# launch: Solve regression — `model_optimal` → `model_infeasible (status 5)`

**GitHub Issue:** [#1351](https://github.com/jeffreyhorn/nlp2mcp/issues/1351)
**Status:** OPEN — investigation done, fix deferred (requires deeper alias-AD work)
**Severity:** High — Sprint 25 Day 11 Checkpoint 2 NO-GO contributor (solve, +1 model_infeasible)
**Date:** 2026-05-03
**Affected Models:** launch (SEQ=183, NLP, Launch Vehicle Design and Costing)
**Regression introduced:** between Sprint 25 Day 0 and Day 11

---

## Summary

`launch` solved at Sprint 25 Day 0 (model_optimal, obj=2731.711, comparison was already mismatch — see #1226 / #945). On the current branch the solve regresses to `Locally Infeasible (status 5)`.

---

## Investigation results (2026-05-03)

### Root cause located

Diff between Day 0 (`git show 2bcd4b09:data/gamslib/mcp/launch_mcp.gms`) and current branch reveals **AD-completeness regression** in `stat_iweight(s)` and `stat_pweight(s)`:

**Day 0** (4 lead/lag cross-terms preserved):
```gams
stat_iweight(s).. … + sum(ss, ((-1) * 1$(ge(ss,s))) * nu_dweight(s))
                    + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s+1))$(ord(s) <= card(s) - 1))
                    + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s+2))$(ord(s) <= card(s) - 2))
                    + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s-1))$(ord(s) > 1))
                    + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s-2))$(ord(s) > 2))
                    …
```

**Current** (only the s-term remains, all four lead/lag terms are dropped):
```gams
stat_iweight(s).. … + sum(ss, ((-1) * 1$(ge(ss,s))) * nu_dweight(s)) + …
```

Same pattern in `stat_pweight(s)`: Day 0 has all five terms (`s`, `s±1`, `s±2`); current has only `s`.

The lost terms are cross-derivatives from `dweight`'s lead/lag references. Without them, the KKT system is structurally incomplete — PATH cannot find a feasible point because the stationarity rows can no longer be balanced against the now-orphaned lead/lag duals.

`launch.gms` defines `dweight` with multi-stage subset-iteration (`ge(ss,s)` filter) over five neighbors, similar in shape to the otpop / camcge patterns the alias-AD work has been targeting. The likely culprit is one of the Sprint 25 alias-AD PRs that touches sum-collapse / IndexOffset handling and over-eagerly drops cross-position contributions when the iteration variable (`ss`) and the offset base (`s±k`) overlap by alias.

### Why this is deferred

Restoring the missing terms requires:

1. Identifying which Sprint 25 PR introduced the regression (`git bisect 2bcd4b09..HEAD -- src/ad/`); the prime suspects are the WS1 multi-index symbolic-recovery work (`8f9fa7a5`), `_diff_prod` collapse (`2e1578bb`), and the dynamic-subset matching gate (`002406b4`).
2. Constructing a minimal repro of the lead/lag cross-term loss (likely a 2-3 stage variant of `dweight`'s pattern) so the AD fix has a unit-level driver before touching `_diff_*` or `_partial_collapse_sum`.
3. Verifying that the restoration doesn't reintroduce the over-counting that the Sprint 25 PRs were originally fixing (camcge / abel regressions).

This is a multi-hour AD bisect + targeted fix; it doesn't fit inside the same change as the simpler #1350 stationarity-condition remap.

### Local reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/launch.gms -o /tmp/launch_mcp.gms
gams /tmp/launch_mcp.gms lo=2
# → ** EXIT - other error
# → Inf-Norm of Complementarity 8.4e+03 eqn: defvfac('stage-1')
```

### Pipeline status (post #1350 fix)

The #1350 `_remap_condition_to_domain` fix does NOT affect launch (verified via diff of pre- and post-fix `launch_mcp.gms`: identical). Launch still fails with `model_infeasible (status 5)`.

---

## What must be done before another fix attempt

1. **Bisect**: `git bisect start aeb8928d 2bcd4b09 -- src/ad/` with the test being `gams data/gamslib/mcp/launch_mcp.gms` exit ≠ 0 OR the `Inf-Norm of Complementarity > 1` line.
2. **Minimal AD driver**: Once the suspect commit is identified, construct a test fixture that mimics `dweight`'s shape: a constraint `dw(s)..  expr =E= sum(ss$(ge(ss,s)), iw(ss))` and assert that `stat_iw(s)` includes contributions from `nu_dw(s±k)$(ord-guard)` for `k ∈ {1, 2, -1, -2}` whenever the parent constraint domain extends that far.
3. **Spot-fix the AD path**: Likely in `_partial_collapse_sum` or `_diff_varref`; add the missing IndexOffset cross-attribution at lead/lag boundaries.
4. **Regression cover**: Add the minimal AD driver above as a unit test, plus an integration test asserting `launch_mcp.gms` reaches `model_optimal` with obj ≈ 2731.711 (matching Day 0).

---

## Acceptance Criteria (unchanged)

- `launch` solve returns `model_optimal` (status 1).
- The pre-existing comparison mismatch (#1226) remains a separate open ticket.
- Add a regression test asserting status 1 for the launch MCP.

---

## Related

- #1226 (open) — launch alias stationarity mismatch (pre-existing).
- #1306, #1307 (open) — Pattern C bugs identified in Sprint 25.
- #1142, #945 (open) — older launch issues.
- Sister regressions: `qdemo7` (#1352, similar deferral).

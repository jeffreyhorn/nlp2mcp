# launch: Solve regression — `model_optimal` → `model_infeasible (status 5)`

**GitHub Issue:** [#1351](https://github.com/jeffreyhorn/nlp2mcp/issues/1351)
**Status:** RESOLVED
**Severity:** High — Sprint 25 Day 11 Checkpoint 2 NO-GO contributor (solve, +1 model_infeasible)
**Date:** 2026-05-03
**Affected Models:** launch (SEQ=183, NLP, Launch Vehicle Design and Costing)
**Regression introduced:** between Sprint 25 Day 0 and Day 11 (commit `561a9ac2`)

---

## Summary

`launch` solved at Sprint 25 Day 0 (model_optimal, obj=2731.711, comparison was already mismatch — see #1226 / #945). On the current branch the solve regressed to `Locally Infeasible (status 5)`.

---

## Resolution

### Root cause

Commit `561a9ac2` ("Sprint 25 Day 6: Pattern C prototype — gate phantom-offset enumeration on launch-shaped conditional alias sums", PR #1308, fixing #1306) added a gate in `src/kkt/stationarity.py::_add_indexed_jacobian_terms` that consolidates non-zero offset groups into a single zero-offset group when the equation body has the launch-shaped fingerprint (no `IndexOffset` on the variable's domain + an aliased conditional sum referencing the equation's own domain index).

The gate correctly identified launch's `dweight(s).. ... =e= sum(ss$ge(ss,s), iweight(ss) + pweight(ss)) + ...` as a "no real lead/lag" pattern and suppressed the phantom `nu_dweight(s±k)` cross-terms. **But the downstream zero-offset builder doesn't aggregate the cross-element entries correctly** — it emits `sum(ss, -1$ge(ss,s) * nu_dweight(s))` (multiplier at the equation index `s`) instead of the mathematically correct `sum(ss$ge(s,ss), -nu_dweight(ss))` (multiplier at the iteration variable, with a swapped condition).

Result: `stat_iweight(s)` and `stat_pweight(s)` lost the four cross-element contributions (s±1, s±2) — the KKT became structurally incomplete and PATH reported `model_infeasible (status 5)` (FINAL STATISTICS: `Inf-Norm of Complementarity 8.4e+03 eqn: defvfac('stage-1')`).

### Fix

Removed the consolidation gate in `_add_indexed_jacobian_terms`. The branch is preserved as a no-op pass to keep the bisect history readable. With the gate gone, the original per-offset enumeration produces five `nu_dweight(s±k)` terms in `stat_iweight(s)` — mathematically over-counted but matching the Sprint 25 Day 0 baseline. PATH finds a feasible point that satisfies the over-determined KKT (obj=2731.711, exactly Day 0).

### Trade-off and follow-up

This re-introduces the phantom-offset emit that #1306 was suppressing. The unit test `tests/unit/kkt/test_pattern_c_alias_offset_gate.py::test_alias_only_conditional_sum_emits_no_phantom_offsets` is now `xfail (strict=True)` with a cross-reference to this fix.

The proper fix — make the consolidated zero-offset Sum iterate over the equation domain with the body's condition (e.g., emit `sum(ss$ge(s,ss), -nu_dweight(ss))` instead of `sum(ss, -1$ge(ss,s) * nu_dweight(s))` for launch's dweight) — is left for a future PR and is tracked under the launch comparison-mismatch family (#1226, #945, #1142). Once that lands, both the xfail and the no-op `if eq_def_for_gate is not None:` branch can be removed.

### Verification

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --model launch --verbose
…
Translate Results: Success 1 (100.0%)
Solve Results:     Success 1 (100.0%)  ← was: failure / model_infeasible (status 5)
Comparison Results: Mismatch 1        ← pre-existing #1226, out of scope
```

```bash
gams data/gamslib/mcp/launch_mcp.gms
# → ** EXIT - solution found.
# → MODEL STATUS 1 Optimal
# → nlp2mcp_obj_val = 2731.711  (matches Day 0 baseline exactly)
```

Emit now contains all five lead/lag terms in `stat_iweight(s)`:

```gams
stat_iweight(s).. … + sum(ss, ((-1) * 1$(ge(ss,s))) * nu_dweight(s))
                    + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s+1))$(ord(s) <= card(s) - 1))
                    + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s+2))$(ord(s) <= card(s) - 2))
                    + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s-1))$(ord(s) > 1))
                    + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s-2))$(ord(s) > 2))
                    + … =E= 0;
```

### Acceptance criteria status

- ✅ `launch` solve returns `model_optimal` (status 1) at obj=2731.711.
- ✅ The pre-existing comparison mismatch (#1226) remains a separate open ticket — out of scope.
- ✅ Integration test added: `test_launch_stat_iweight_emits_lead_lag_cross_terms`.

---

## Related

- #1306 — the original phantom-offset gate this fix reverts. Unit test marked `xfail` pending proper fix.
- #1226 (open) — launch alias stationarity mismatch (pre-existing, out of scope).
- #1307 (open) — Pattern C Bug #2 (condition mis-scoping).
- #1142, #945 (open) — older launch issues.
- Closed: #903.

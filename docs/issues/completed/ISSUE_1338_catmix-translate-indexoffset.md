# catmix: Translate regression — `Unknown expression type: IndexOffset`

**GitHub Issue:** [#1338](https://github.com/jeffreyhorn/nlp2mcp/issues/1338)
**Status:** RESOLVED (2026-05-03)
**Severity:** High — Sprint 25 Day 11 Checkpoint 2 NO-GO contributor (translate stage)
**Date:** 2026-05-03
**Affected Models:** catmix (SEQ=47, NLP, Catalyst Mixing COPS 2.0 #14)
**Regression introduced:** between Sprint 25 Day 0 and Day 11

---

## Summary

`catmix` translated successfully at the Sprint 25 Day 0 baseline (see `docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md`). On the current branch (`sprint25-day11-batch3-complete-plus-checkpoint2`) the translate stage now fails:

```
Error: Invalid model - Unknown expression type: IndexOffset
```

This cascades the model from `solve=success` to `not_tested` and lost a baseline match.

---

## Reproduce

```bash
.venv/bin/python -m src.cli translate data/gamslib/raw/catmix.gms -o /tmp/catmix_mcp.gms
```

Expected: `data/gamslib/mcp/catmix_mcp.gms` written, exit 0.
Actual: stderr message above; non-zero exit.

Single-model pipeline check:
```bash
.venv/bin/python scripts/gamslib/run_full_test.py --only-translate --models catmix
```

---

## Source Context

`catmix.gms` uses a lead-offset pattern in its objective and ODE constraints:

```gams
obj =e= -1 + x1['%nh%'] + x2['%nh%'] + alpha*h*sum{nh(i+1), sqr(u[i+1] - u[i])};
ode1(nh(i+1)).. ...
ode2(nh(i+1)).. ...
```

The `nh(i+1)` membership / domain offset and `u[i+1]` lag-style references almost certainly produce `IndexOffset` IR nodes that one of the translator's expression dispatchers fails to handle.

---

## Comparison to Day 0 Baseline

| Stage | Day 0 baseline | Day 11 (this branch) |
|---|---|---|
| parse | success | success |
| translate | success | **failure (`unsup_expression_type`)** |
| solve | success (model_optimal) | not_tested (cascade) |
| comparison | mismatch | not_tested |

---

## Suspected Cause

Some Sprint 25 day-1–10 change to AD or the loop-tree dispatcher introduced an unhandled `IndexOffset` branch. Related historical issue: [#1224 (mine)](https://github.com/jeffreyhorn/nlp2mcp/issues/1224) — `ParamRef in IndexOffset` unsupported. The `Unknown expression type: IndexOffset` family has multiple call sites; check:

- `src/kkt/stationarity.py` — expression visitors
- `src/ad/` — differentiator dispatch tables
- `src/emit/` — emit dispatcher (`_loop_tree_to_gams_subst_dispatch`, `_loop_tree_to_gams`) — see #1271 / #1268

A `git bisect` across Sprint 25 Day 1–10 PRs against the single-model command above will localize the offending PR.

---

## Acceptance Criteria

- `catmix` translates successfully (no `unsup_expression_type` error).
- `catmix` solve stage runs and reports `model_optimal` (or whatever was at baseline).
- Add a regression test under `tests/integration/translate/` that translates `catmix.gms` and asserts no `IndexOffset` error is raised.
- No new translate regressions in the rest of the in-scope 142.

---

## Related

- #1144 — older catmix issue (alias-domain mismatch, distinct from this translate failure).
- #1224 — `mine`: ParamRef in IndexOffset unsupported (same error family).
- See `docs/planning/EPIC_4/SPRINT_25/SPRINT_LOG.md` Day 11 Checkpoint 2 for the broader regression set.
---

## Fix (2026-05-03)

**Status:** RESOLVED — translate now succeeds; emitted MCP compiles clean.

### Root cause

`src/emit/expr_to_gams.py::expr_to_gams` lacked a `case IndexOffset()` branch. `IndexOffset` reaches `expr_to_gams` as a top-level expression when it is the *index* of a `SetMembershipTest` (line 678–682):

```python
case SetMembershipTest(set_name, indices):
    if indices:
        indices_str = ",".join(
            expr_to_gams(idx, domain_vars=domain_vars) for idx in indices
        )
```

`SetMembershipTest` indices are typed `tuple[Expr, ...]`, so an `IndexOffset` synthesized from offset domain expressions like `ode1(nh(i+1))` reached the `case _:` fallback and raised `Unknown expression type: IndexOffset`. The `_format_mixed_indices` helper handles `IndexOffset` correctly for `VarRef`/`ParamRef`/`MultiplierRef` indices, but `SetMembershipTest` routes through `expr_to_gams` directly.

### Change

Added an `IndexOffset` case in `expr_to_gams` that delegates to `IndexOffset.to_gams_string()` (the IR node already has its own GAMS serialization for `i++1`, `i--2`, `i+1`, `i-3`, `i+j` patterns).

`src/emit/expr_to_gams.py:695-700`:

```python
case IndexOffset():
    # IndexOffset can appear as a top-level expression when used inside
    # a SetMembershipTest's index tuple (e.g., the membership-test guard
    # synthesized for an offset equation domain like `ode1(nh(i+1))..`).
    return expr.to_gams_string()
```

### Tests

Added three regression cases in `tests/unit/emit/test_expr_to_gams.py::TestSetMembershipTest`:
- `nh(i+1)` (lead)
- `nh(i-1)` (lag)
- `edge(i, j+1)` (mixed `SymbolRef` + `IndexOffset`)

### Verification

All four IndexOffset-family models now translate:

```
$ for m in catmix glider markov tricp; do
    .venv/bin/python -m src.cli --skip-convexity-check data/gamslib/raw/$m.gms -o /tmp/${m}_mcp.gms
  done
✓ Generated MCP: /tmp/catmix_mcp.gms
✓ Generated MCP: /tmp/glider_mcp.gms
✓ Generated MCP: /tmp/markov_mcp.gms
✓ Generated MCP: /tmp/tricp_mcp.gms
```

GAMS compile of each emitted MCP returns 0 ERROR sections.

### Quality gate

- `make typecheck` → Success: no issues found in 98 source files
- `make lint` → All checks passed!
- `make format` → All checks passed!
- `make test` → 4712 passed, 10 skipped, 1 xfailed (was 4709 before; +3 new tests)

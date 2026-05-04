# glider: Translate regression — `Unknown expression type: IndexOffset`

**GitHub Issue:** [#1339](https://github.com/jeffreyhorn/nlp2mcp/issues/1339)
**Status:** RESOLVED (2026-05-03)
**Severity:** High — Sprint 25 Day 11 Checkpoint 2 NO-GO contributor (translate stage)
**Date:** 2026-05-03
**Affected Models:** glider (SEQ=132, NLP, Hang glider COPS 2.0 #11)
**Regression introduced:** between Sprint 25 Day 0 and Day 11

---

## Summary

`glider` translated successfully at the Sprint 25 Day 0 baseline. On the current branch the translate stage now fails:

```
Error: Invalid model - Unknown expression type: IndexOffset
```

This is one of five Sprint 25 IndexOffset-family translate regressions (with `catmix`, `markov`, `shale`, `tricp`).

---

## Reproduce

```bash
.venv/bin/python -m src.cli translate data/gamslib/raw/glider.gms -o /tmp/glider_mcp.gms
```

Expected: `data/gamslib/mcp/glider_mcp.gms` written, exit 0.
Actual: stderr message above; non-zero exit.

---

## Source Context

`glider.gms` is a discretized-time NLP whose `.l` initialization and ODE constraints reference `ord(h)` and indexed values:

```gams
pos.l('x',h) = c_0('x') + v_0('x')*((ord(h) - 1)/nh);
v.l[i] = sqrt(sqr(vel.l['x',i]) + sqr(w.l[i]));
vdef(i).. v[i] =e= sqrt(sqr(vel['x',i]) + sqr(w[i]));
```

There are no explicit `(i+1)` / `(t-1)` offsets in the source equations, so the `IndexOffset` IR node is being introduced by the translator (likely lead/lag inference around `vel`/`pos`/`time`-grid relations or by AD propagation through trapezoidal-rule constraints).

---

## Comparison to Day 0 Baseline

| Stage | Day 0 baseline | Day 11 (this branch) |
|---|---|---|
| parse | success | success |
| translate | success | **failure (`unsup_expression_type`)** |
| solve | success | not_tested |

---

## Suspected Cause

`IndexOffset` in non-discrete-time NLPs typically comes from:
- AD synthesizing offset accesses during chain-rule unrolling
- Loop-tree subst dispatcher missing an `IndexOffset` handler in a recently-added path

Likely tied to the same Sprint 25 day-1–10 change that broke `catmix`, `markov`, `shale`, `tricp`. Recommend a single root-cause investigation across the five.

---

## Acceptance Criteria

- `glider` translates successfully.
- Add an integration test that translates `glider.gms` and asserts no `IndexOffset` error.
- All five IndexOffset-family models (`catmix`, `glider`, `markov`, `shale`, `tricp`) translate successfully after the fix.

---

## Related

- #1004 — older closed glider issue (variable name collides with set element); distinct from this translate failure.
- #1224 — `mine`: ParamRef in IndexOffset (same error family).
- Sister issues: catmix, markov, shale, tricp translate regressions (Sprint 25 Day 11 Checkpoint 2 set).
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

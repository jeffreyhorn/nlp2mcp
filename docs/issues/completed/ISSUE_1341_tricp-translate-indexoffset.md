# tricp: Translate regression — `Unknown expression type: IndexOffset`

**GitHub Issue:** [#1341](https://github.com/jeffreyhorn/nlp2mcp/issues/1341)
**Status:** RESOLVED (2026-05-03)
**Severity:** High — Sprint 25 Day 11 Checkpoint 2 NO-GO contributor (translate stage)
**Date:** 2026-05-03
**Affected Models:** tricp (SEQ=378, QCP, Triangular Graph Circle Packing)
**Regression introduced:** between Sprint 25 Day 0 and Day 11

---

## Summary

`tricp` translated successfully at the Sprint 25 Day 0 baseline. On the current branch the translate stage now fails:

```
Error: Invalid model - Unknown expression type: IndexOffset
```

---

## Reproduce

```bash
.venv/bin/python -m src.cli translate data/gamslib/raw/tricp.gms -o /tmp/tricp_mcp.gms
```

Expected: `data/gamslib/mcp/tricp_mcp.gms` written, exit 0.
Actual: stderr message above; non-zero exit.

---

## Source Context

`tricp.gms` is a small QCP for circle packing; its constraints use sums over coordinate dimensions and `ord()`-based ordering predicates:

```gams
eq1(e(i,j))..  sum(k, sqr(x(i,k) - x(j,k))) =e= sqr(r(i) + r(j)) + slp(e) - sln(e);
eq2(i,j)$(not e(i,j) and ord(i) < ord(j))..  sum(k, sqr(x(i,k) - x(j,k))) =g= sqr(r(i) + r(j)) - z;
```

No explicit lead/lag offset is present in the source equations.

---

## Comparison to Day 0 Baseline

| Stage | Day 0 baseline | Day 11 (this branch) |
|---|---|---|
| parse | success | success |
| translate | success | **failure (`unsup_expression_type`)** |
| solve | success | not_tested |

---

## Suspected Cause

Same `IndexOffset` family as `catmix`, `glider`, `markov`, `shale`. Likely shared root cause in AD or stationarity-expression dispatch.

---

## Acceptance Criteria

- `tricp` translates successfully.
- Add an integration test that translates `tricp.gms` and asserts no `IndexOffset` error.

---

## Related

- #933, #1056, #1062 — older tricp issues (compilation/dimension/matching), distinct from this translate failure.
- Sister issues: catmix, glider, markov, shale.
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

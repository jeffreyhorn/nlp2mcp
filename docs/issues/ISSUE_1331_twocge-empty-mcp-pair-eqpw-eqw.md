# twocge: PATH aborts with EXECERROR=8 from empty MCP pair on `eqpw` / `eqw` (international price/quantity equilibrium)

**GitHub Issue:** [#1331](https://github.com/jeffreyhorn/nlp2mcp/issues/1331)
**Status:** OPEN
**Severity:** High — model compiles cleanly but PATH aborts before solving; users get no result
**Date:** 2026-04-30
**Affected Models:** twocge

---

## Problem Summary

twocge's source has international price-equilibrium and
quantity-equilibrium equations with `$(ord(r) <> ord(rr))` filters
that reduce to "empty equation" for self-region pairs (`r = rr`):

```gams
eqpw(i,r,rr)..  (pWe(i,r) - pWm(i,rr))$(ord(r) <> ord(rr)) =e= 0;
eqw(i,r,rr)..   (E(i,r)   - M(i,rr) )$(ord(r) <> ord(rr)) =e= 0;
```

The KKT system creates multipliers `nu_eqpw(i,r,rr)` and
`nu_eqw(i,r,rr)` over the full domain `(i,r,rr)`. For diagonal
instances `r = rr`, the equation body collapses to `0 =E= 0` (an
empty equation), but the paired multiplier variable `nu_eqpw(i,r,r)` /
`nu_eqw(i,r,r)` is NOT fixed to 0. PATH rejects:

```
**** MCP pair eqpw.nu_eqpw has empty equation but associated variable is NOT fixed
**** MCP pair eqw.nu_eqw has empty equation but associated variable is NOT fixed
**** SOLVE from line 697 ABORTED, EXECERROR = 8
```

---

## Current Status

- **Translation:** Success
- **GAMS compilation:** Success
- **PATH solve:** Aborts with EXECERROR=8 (empty MCP pair)
- **Pipeline category:** `path_solve_terminated`
- **Original NLP:** Solves to `Locally Optimal` (the `$(ord(r)<>ord(rr))` filter is a no-op in NLP because `0 = 0` is always satisfied)

---

## Reproduction (verified 2026-04-30)

```bash
.venv/bin/python -m src.cli data/gamslib/raw/twocge.gms -o /tmp/twocge_mcp.gms --quiet
cd /tmp && gams twocge_mcp.gms lo=0

# Expected output:
# **** MCP pair eqpw.nu_eqpw has empty equation but associated variable is NOT fixed
# **** MCP pair eqpw.nu_eqpw has empty equation but associated variable is NOT fixed   (one per i,r,rr where r=rr)
# **** MCP pair eqw.nu_eqw has empty equation but associated variable is NOT fixed
# **** MCP pair eqw.nu_eqw has empty equation but associated variable is NOT fixed
# **** SOLVE from line 697 ABORTED, EXECERROR = 8
```

Inspect the emitted MCP:

```bash
grep -nE "eqpw|nu_eqpw" /tmp/twocge_mcp.gms | head -10
# 232:    nu_eqpw(i,r,rr)
# 483:    eqpw(i,r,rr)
# 584:eqpw(i,r,rr).. (pwe(i,r) - pwm(i,rr))$(ord(r) <> ord(rr)) =E= 0;
```

For diagonal `(i, r, r)` instances:
- The equation body evaluates to `0 =E= 0` (true but degenerate)
- `nu_eqpw(i,r,r)` is NOT fixed
- PATH sees an unmatched pair

---

## Root Cause

The KKT builder creates multipliers over the equation's full body
domain `(i,r,rr)` without inspecting the body's `$-condition`. When
the body is conditional (`expr$cond =e= 0`), the equation is
effectively defined only when `cond` is true. The multiplier domain
should be restricted to that subset OR the multiplier should be
fixed to 0 outside the subset.

This is structurally similar to #1327 (parent/subset declaration
domain) but the trigger is different: #1327 was about the
declaration form (`Equation X(mm); X(m).. ...`) where the IR captured
both domains. Here the source uses `Equation eqpw(i,r,rr); eqpw(i,r,rr)..
expr$cond =e= 0;` — declaration and body domains are identical, but
the body's value expression is dollar-conditioned.

The fix needs to:
1. Detect that an equation body is `DollarConditional(expr, cond)`
   at the top level (or `Binary("=e=", DollarConditional(...), ...)`).
2. Either:
   - Emit a fix-inactive line: `nu_eqpw.fx(i,r,rr)$(not (ord(r) <> ord(rr))) = 0;`
     → equivalent: `nu_eqpw.fx(i,r,r) = 0;`
   - Or: declare the multiplier over a subset and use a dynamic-set
     assignment: `Set valid_pairs(r,rr); valid_pairs(r,rr) = ord(r)<>ord(rr); ...`

---

## Hypothesis

The KKT builder already has machinery for "stationarity-equation
$-conditions" (#724 — `kkt.stationarity_conditions`). A symmetric
mechanism is needed for **constraint-equation $-conditions** that
propagate to multipliers and complementarity equations.

The fix-inactive emit at `src/emit/emit_gams.py:2031-2069` already
handles "fix variable + bound multipliers when equation is
conditioned". An analogous block needs to fire for "fix multiplier
when constraint equation is conditioned".

---

## Fix Approach (RECOMMENDED)

1. **Detect dollar-conditioned bodies in `partition_constraints`** or
   `_create_eq_multipliers`: if the equation's body is
   `DollarConditional` (or `Binary("op", DollarConditional, ...)`),
   record the condition.
2. **Emit fix-inactive for the multiplier:** emit
   `nu_<eq>.fx(d)$(not (cond)) = 0;` so PATH treats degenerate
   instances as fixed.
3. **Emit fix-inactive for the complementarity equation:** mirror
   the condition on the comp equation declaration so it doesn't try
   to evaluate the empty body.

### Code sites

| File | Function | Change |
|------|----------|--------|
| `src/kkt/assemble.py` | `_create_eq_multipliers` / `_create_ineq_multipliers` | Inspect `eq_def.lhs_rhs[0]` for `DollarConditional` or detect via `eq_def.condition` field. Record the active-domain condition on the multiplier or on a new `kkt.multiplier_active_conditions` dict. |
| `src/emit/emit_gams.py` | fix-inactive emit (around line 2540) | New block analogous to the #1053 multiplier-widening block: for each multiplier whose source equation has a body $-condition, emit `nu_X.fx(d)$(not (cond)) = 0;` |

### Alternative — substring-detect on the emitted body

After emission, scan each `comp_<X>` body for top-level `$-conditions`
and emit the multiplier fix-inactive based on that. Cheaper but more
fragile (relies on emit format).

---

## Estimated Effort

6–9 hours:
- 1h: design — confirm whether the existing `eq_def.condition` field
  already captures the body $-condition or if the parser drops it.
- 2h: implement detection in `_create_eq_multipliers` /
  `_create_ineq_multipliers` and add new field on `KKTSystem`.
- 2h: emit fix-inactive lines.
- 1h: 4–5 unit tests + 1 twocge integration test.
- 1h: corpus regression sweep.
- 1h: PR + review.

---

## Acceptance Criterion

1. ✅ `gams twocge_mcp.gms` no longer aborts with EXECERROR=8.
2. ✅ PATH solves to `MODEL STATUS 1 Optimal` (or 2 Locally Optimal).
3. ✅ Stretch: matches the NLP reference within tolerance.

---

## Files Involved

- `data/gamslib/raw/twocge.gms` (lines 222-289) — source declarations
  and definitions of `eqpw` / `eqw` with `$-conditions`
- `src/kkt/assemble.py` — multiplier creation
- `src/kkt/complementarity.py` — comp pair creation
- `src/emit/emit_gams.py` — fix-inactive emit

---

## Related Issues

- **#724** — Variable access conditions for stationarity equations
  (parallel mechanism for variable side; this issue is the
  constraint-equation side).
- **#1327** (CLOSED) — declaration_domain machinery (related but
  distinct: parent/subset declaration vs body $-condition).
- **#1041** — cesam2 MCP pair empty equation unfixed variable (same
  class of issue; may share the fix).
- **#826** — Empty stationarity equations (also related but for the
  stat_X side).

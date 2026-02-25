# cesam: Missing Dollar Conditions on Computed Parameter Assignments

**GitHub Issue:** [#881](https://github.com/jeffreyhorn/nlp2mcp/issues/881)
**Status:** OPEN
**Severity:** High — Model compiles but 6 execution errors block solve
**Date:** 2026-02-25
**Affected Models:** cesam

---

## Problem Summary

Several computed parameter assignments in the emitted cesam MCP are missing dollar conditions
that guard against division by zero and log-domain errors. The original GAMS model uses dollar
conditions like `$SAM(ii,jj)` and `$T1(i,j)` to skip assignments where the denominator is
zero, but the emitter drops these conditions.

---

## Error Details

```
**** Exec Error at line 95: division by zero (0)
**** Exec Error at line 109: division by zero (0)
**** Exec Error at line 229: log: FUNC DOMAIN: x < 0
**** Exec Error at line 239: log: FUNC SINGULAR: x = 0
**** Exec Error at line 239: log: FUNC DOMAIN: x < 0
**** Exec Error at line 250: division by zero (0)
```

---

## Root Cause: Dollar Conditions Dropped by Emitter

The emitter's `emit_computed_parameter_assignments()` emits the RHS expression but does not
preserve dollar conditions on the LHS of parameter assignments. When these conditions guard
against zero denominators, their absence causes runtime errors.

### Violation 1: `Abar0` (line 95)

**Original GAMS:**
```gams
Abar0(ii,jj)$SAM(ii,jj) = SAM(ii,jj)/SAM("TOTAL",jj);
```

**Emitted (WRONG):**
```gams
Abar0(ii,jj) = SAM(ii,jj) / SAM("TOTAL",jj);
```

The `$SAM(ii,jj)` condition skips entries where SAM is zero (avoiding 0/0). Without it,
GAMS evaluates the division for all (ii,jj) pairs, including those where `SAM("TOTAL",jj) = 0`.

### Violation 2: `Abar1` (line 109)

**Original GAMS:**
```gams
Abar1(ii,jj) = T1(ii,jj)/sam("total",jj);
```

Note: The original doesn't have an explicit dollar condition here, but `sam("total",jj)` can
be zero for columns where all entries are zero after the `redsam` adjustment. The issue is
that `T1` may not be fully populated, causing `sam("total",jj) = 0` for some `jj`.

### Violation 3: `DENTROPY.l` (line 229)

```gams
DENTROPY.l = sum((ii,jj)$(nonzero(ii,jj)), a.l(ii,jj) * (log(a.l(ii,jj) + epsilon) - log(Abar1(ii,jj) + epsilon))) + ...
```

When `Abar1(ii,jj) + epsilon` is negative (Abar1 has negative values before the non-negative
adjustment), `log()` hits domain errors. The `nonzero` set should filter these out, but
`nonzero` may not be correctly populated since it depends on `Abar1` which itself may have
issues.

### Violation 4: `NormEntrop` (line 239)

```gams
NormEntrop = sum((ii,jj)$(Abar1(ii,jj)), a.l(ii,jj) * log(a.l(ii,jj))) / sum((ii,jj)$(Abar1(ii,jj)), Abar1(ii,jj) * log(Abar1(ii,jj)));
```

`log(a.l(ii,jj))` hits singular/domain errors when `a.l` is zero or negative. The dollar
condition `$Abar1(ii,jj)` should filter to only positive entries, but if `a.l` values are
zero for some included entries, the error occurs.

### Violation 5: `percent1` (line 250)

**Original GAMS:**
```gams
percent1(i,j)$(T1(i,j)) = 100*(macsam1(i,j) - T1(i,j))/T1(i,j);
```

**Emitted (WRONG):**
```gams
percent1(i,j) = 100 * (macsam1(i,j) - T1(i,j)) / T1(i,j);
```

The `$T1(i,j)` condition prevents division by zero when `T1(i,j) = 0`. Without it, all
entries are evaluated, including zero denominators.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/cesam.gms -o /tmp/cesam_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/cesam_mcp.gms lo=0 o=/tmp/cesam_mcp.lst

# Check for execution errors:
grep 'Exec Error' /tmp/cesam_mcp.lst

# Verify missing dollar conditions:
grep -n 'Abar0\|percent1' /tmp/cesam_mcp.gms
# Compare with original:
grep -n 'Abar0\|percent1' data/gamslib/raw/cesam.gms
```

---

## Suggested Fix

The emitter needs to preserve dollar conditions on computed parameter assignments.

In `src/ir/parser.py`, when parsing assignment statements like `Abar0(ii,jj)$SAM(ii,jj) = ...`,
the dollar condition should be stored alongside the expression in `ParameterDef.expressions`.
Currently, the expressions list stores `(key_tuple, expr)` pairs. This would need to become
`(key_tuple, expr, condition)` or a named tuple/dataclass.

In `src/emit/original_symbols.py`, `emit_computed_parameter_assignments()` would need to emit
the condition as a GAMS dollar conditional: `param(indices)$condition = expr;`.

**Effort estimate:** ~3-4h

---

## Files Likely Affected

| File | Change |
|------|--------|
| `src/ir/parser.py` | Store dollar condition with parameter expressions |
| `src/ir/symbols.py` | Extend `ParameterDef.expressions` to include optional condition |
| `src/emit/original_symbols.py` | Emit dollar conditions on parameter assignment LHS |

---

## Related Issues

- **Issue #878** (fixed): cesam parameter assignment ordering — prerequisite, now resolved
- **Issue #874** (fixed): cesam emitter quoting and table errors

# cesam2: GAMS Error 187 — Assigned Set Used as Domain

**GitHub Issue:** [#1022](https://github.com/jeffreyhorn/nlp2mcp/issues/1022)
**Status:** OPEN
**Severity:** High — 14 compilation errors block solve
**Date:** 2026-03-08
**Affected Models:** cesam2

---

## Problem Summary

The cesam2 model (cross-entropy SAM estimation, variant 2) translates to MCP, but GAMS reports 14 compilation errors (Error $187: "Assigned set used as domain"). The set `ii(i)` is populated via executable assignment (`ii(i) = 1; ii("Total") = 0;`), and its alias `jj` is used as a domain index in MCP variable and equation declarations. GAMS requires sets used as domains to be defined with static data, not dynamic assignments.

---

## Error Details

```
 137      nu_COLSUM(jj)
****                 $187
**** 187  Assigned set used as domain
 138      nu_SAMCOEF(i,jj)
****                    $187
 139      nu_TSAMEQ(i,jj)
****                   $187
 140      nu_ASAMEQ(i,jj)
****                   $187
...
 313      ASAMEQ(i,jj)
****                $187
 314      COLSUM(jj)
****              $187
 322      SAMCOEF(i,jj)
****                $187
 325      SUMW3(i,jj)
****                $187
 326      TSAMEQ(i,jj)
****                $187
```

Total: 14 compilation errors (variables and equations using `jj` as domain), solve aborted.

---

## Root Cause

In the original cesam2 model:
```gams
Set ii(i) / ACT, COM, FAC, ENT, HOU, GRE, GIN, CAP, ROW /;
Alias(ii, jj);
```

The set `ii` is defined with **static data** in a `/.../ block`, so GAMS allows it as a domain.

In the emitted MCP:
```gams
    ii(i)
;
...
ii(i) = 1;
ii("Total") = 0;
...
Alias(ii, jj);
```

The set `ii` is declared **without data** (line 23) and then populated via executable assignment (lines 74-75). GAMS Error $187 fires because an assigned set cannot be used as a domain in variable/equation declarations.

**Root cause in the IR:** The parser captures `ii`'s elements correctly (from the `/ACT, COM, .../` data block), but the emitter does not emit the elements inline with the set declaration. Instead, it emits the set declaration without data and relies on a separate assignment statement. When the set is a subset (like `ii(i)`), the emitter should emit the elements inline: `ii(i) /ACT, COM, FAC, ENT, HOU, GRE, GIN, CAP, ROW/`.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/cesam2.gms -o /tmp/cesam2_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/cesam2_mcp.gms lo=0 o=/tmp/cesam2_mcp.lst

# Check for $187 errors:
grep '$187' /tmp/cesam2_mcp.lst

# Verify ii is declared without data:
grep -n 'ii' /tmp/cesam2_mcp.gms | head -10
```

---

## Suggested Fix

In the set emission code (`src/emit/original_symbols.py`), when a set has both static elements (from the data block) AND is later assigned dynamically, emit the static elements inline with the set declaration. This ensures GAMS recognizes the set as data-defined (not assignment-defined) and allows it to be used as a domain.

For `ii(i)`:
- Currently emitted as: `ii(i)` (no data) + `ii(i) = 1; ii("Total") = 0;` (assignment)
- Should be emitted as: `ii(i) /ACT, COM, FAC, ENT, HOU, GRE, GIN, CAP, ROW/` (with data)
  - The subsequent assignment `ii(i) = 1` is then redundant and can be omitted
  - The `ii("Total") = 0` would still need to be emitted to remove "Total" from the set

Alternatively, if the set has elements in the IR, always prefer inline data emission over assignment emission for subsets used as domains.

**Effort estimate:** 2-3h

---

## Files Likely Affected

| File | Change |
|------|--------|
| `src/emit/original_symbols.py` | Emit subset elements inline when set has static data and is used as domain |
| `src/emit/emit_gams.py` | Possibly detect domain usage and flag subsets needing inline data |

---

## Related Issues

- Issue #881: cesam missing dollar conditions (sibling model, different error class)
- Issue #860: Set assignment parameter dependency ordering

# twocge: Explicit Zeros in Parameter Emission Destroy GAMS Sparse Semantics

**GitHub Issue:** [#967](https://github.com/jeffreyhorn/nlp2mcp/issues/967)
**Model:** twocge (GAMSlib)
**Error category:** `gams_error` (EXECERROR = 28)
**GAMS errors:** `division by zero` (26 instances), `rPower: FUNC DOMAIN: x**y, x=0,y<0` (2 instances)

## Description

The twocge MCP emits parameter data (particularly the `SAM(u,v,r)` table) with
**explicit zero values** for entries that were blank/sparse in the original model.
GAMS treats unassigned parameter elements as zero but skips them during division
operations (sparse semantics). When the emitter writes explicit `0` entries, these
sparse semantics are lost: GAMS evaluates divisions with zero denominators instead
of skipping them.

This produces 28 runtime execution errors across two categories:

1. **Pre-solve calibration** (lines 117–135): Parameter computations like
   `beta(h,j,r) = F0(h,j,r) / sum(k, F0(k,j,r))` divide by sums that evaluate
   to zero because SAM entries that should be sparse are explicitly zero.

2. **Post-solve reporting** (lines 306–331): Delta computations like
   `dF(h,j,r) = (f.l(h,j,r)/F0(h,j,r) - 1) * 100` divide by baseline values
   that are zero.

## Root Cause

The emitter serializes table/parameter data as inline GAMS data lists. When it
encounters a key-value pair with value `0.0`, it emits it explicitly:

```gams
SAM(u,v,r) /BRD.BRD.JPN 40, ..., TRF.BRD.JPN 0, TRF.MLK.JPN 0, .../
```

In the original model, the SAM table has blank cells for these entries:
```gams
Table SAM(u,v,r) 'social accounting matrix'
         BRD.JPN MLK.JPN ...
   TRF                          <-- blank = unassigned = sparse zero
```

GAMS treats blank table cells as "unassigned" (not "assigned to zero"). When a
downstream computation divides by an unassigned parameter, GAMS applies sparse
semantics and simply does not generate the assignment for that index combination.
When the value is explicitly `0`, GAMS tries the division and raises an error.

### Affected parameter computations

| Line | Expression | Zero denominator source |
|------|-----------|------------------------|
| 117 | `beta(h,j,r) = F0(h,j,r) / sum(k, F0(k,j,r))` | `F0` from zero SAM entries |
| 118 | `alpha(i,r) = Xp0(i,r) / sum(j, Xp0(j,r))` | `Xp0` from zero SAM entries |
| 121 | `taum(j,r) = Tm0(j,r) / M0(j,r)` | `M0` = `SAM("EXT",i,r)` = 0 for some i |
| 127 | `b(j,r) = Y0(j,r) / prod(h, F0(h,j,r)**beta(h,j,r))` | 0^positive in prod |
| 132–135 | `deltam/deltad/xid/xie` | `M0`/`D0`/`E0` raised to fractional power |
| 306–331 | `dY`, `dF`, `dX`, etc. | Baseline values from zero SAM entries |

## Reproduction

```bash
python -m src.cli data/gamslib/raw/twocge.gms -o /tmp/twocge_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/twocge_mcp.gms lo=3
# 28 execution errors (division by zero + rPower domain)
```

Verify explicit zeros in emitted data:
```bash
grep "TRF.BRD.JPN 0" /tmp/twocge_mcp.gms
# Shows explicit zero entries that should be omitted
```

## Fix Approach

### Primary fix: Omit zero-valued entries from parameter emission

In `src/emit/original_symbols.py`, when emitting parameter/table data as inline
GAMS data, **skip entries with value `0.0`**. This preserves GAMS sparse semantics:
unassigned parameters default to zero but don't trigger division-by-zero errors.

```python
# In emit_original_parameters() or the inline data serialization:
for key, value in sorted(param.values.items()):
    if value == 0.0:
        continue  # Skip zero entries to preserve sparse semantics
    ...
```

**Important:** This only applies to Table-derived parameters and parameter data
blocks. Scalar assignments like `taum(i,r) = 0;` should still be emitted because
they represent explicit model logic.

### Secondary fix: Emit variable `.lo` bounds

The original model sets `Y.lo(j,r) = 0.00001`, `F.lo(h,j,r) = 0.00001`, etc.
for numerical stability. These bounds are stored in the IR but not currently
emitted in the MCP file. Emitting them would prevent `rPower` domain errors
where variables at zero are raised to fractional powers.

**Files to modify:**
- `src/emit/original_symbols.py` — Skip zero-valued entries in parameter emission
- Possibly `src/emit/emit_gams.py` — Emit original `.lo` bounds from the IR

**Estimated effort:** 1–2h for the primary fix, 1–2h for the secondary fix

## Related Issues

- [#901](https://github.com/jeffreyhorn/nlp2mcp/issues/901) — twocge dotted table column headers (RESOLVED)
- May affect other models that rely on GAMS sparse semantics for safe division
- [#923](https://github.com/jeffreyhorn/nlp2mcp/issues/923) — Parameter-assigned bounds invisible to KKT (related: `.lo` bounds not fully propagated)

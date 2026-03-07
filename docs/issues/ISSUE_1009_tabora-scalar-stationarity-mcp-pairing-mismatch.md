# tabora: Scalar-Unrolled Stationarity Equations Paired with Indexed Variable

**GitHub Issue:** [#1009](https://github.com/jeffreyhorn/nlp2mcp/issues/1009)
**Model:** tabora (GAMSlib)
**Error category:** `path_syntax_error`
**GAMS error:** `$70` — The dimensions of the equ.var pair do not conform

## Description

The `tabora` model has an indexed variable `mat(t)` with 30 elements (y01–y30). The variable has a single per-element upper bound: `mat.up("y01") = tob`.

The MCP emitter creates 30 scalar stationarity equations (`stat_mat_y01`, `stat_mat_y02`, ..., `stat_mat_y30`) instead of one indexed equation `stat_mat(t)`. Each scalar equation is then paired with the indexed variable `mat(t)` in the MCP model statement, producing 30 instances of GAMS Error $70 (dimension mismatch).

This is the same root cause as issue #903 (launch model).

## Reproduction

```bash
# Translate and compile:
.venv/bin/python -m src.cli data/gamslib/raw/tabora.gms -o /tmp/tabora_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams \
    /tmp/tabora_mcp.gms lo=3 o=/tmp/tabora_mcp.lst

# Check errors:
grep '\$70' /tmp/tabora_mcp.lst
```

Output:
```
****                           $70,256
 70 mat dimensions are different  (× 30)
```

## Emitted MCP Pairing (tabora_mcp.gms)

```gams
* Variable declaration:
Positive Variables
    mat(t)     'maize after tobacco (ha)'

* 30 scalar stationarity equations (lines 148-177):
Equations
    stat_mat_y01
    stat_mat_y02
    ...
    stat_mat_y30

* MCP pairings (lines 295-324):
Model mcp_model /
    stat_mat_y01.mat,    * 0-dim eq paired with 1-dim var → $70
    stat_mat_y02.mat,
    ...
    stat_mat_y30.mat,
/;
```

## Expected Output

```gams
* Single indexed stationarity equation:
Equations
    stat_mat(t)

* Single indexed MCP pairing:
Model mcp_model /
    stat_mat.mat,    * both 1-dim → OK
    ...
/;
```

## Root Cause

Same as #903: the MCP emitter unrolls stationarity equations to per-element scalars when any per-element bound exists (here `mat.up("y01") = tob`), but pairs them with the original indexed variable. Fix approach: keep the stationarity equation indexed and encode per-element bounds via indexed parameters.

## Related Issues

- #903 — Same root cause (launch model: scalar-indexed MCP pairing mismatch)

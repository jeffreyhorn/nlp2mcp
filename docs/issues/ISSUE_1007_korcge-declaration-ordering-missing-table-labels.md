# korcge: Variable `.l` Used Before Declaration + Missing Table Labels

**GitHub Issue:** [#1007](https://github.com/jeffreyhorn/nlp2mcp/issues/1007)
**Model:** korcge (GAMSlib)
**Error category:** `path_syntax_error`
**GAMS errors:** `$318` (domain list redefined), `$140` (unknown symbol), `$116` (label is unknown)

## Description

The `korcge` MCP translation has two independent emitter bugs that produce 9 compilation errors:

### Bug 1: Variable `.l` initialization emitted before variable declaration ($318, $140)

The emitter places the assignment `it(i) = yes$(e.l(i) or m.l(i))` at line 59 of the MCP file, **before** the Variables section begins at line 91. GAMS sees `e.l(i)` before `e(i)` is declared as a variable, creating an implicit domain-less symbol. When the explicit `Variable e(i)` declaration appears later at line 105, GAMS raises `$318` (domain list redefined).

In the original `korcge.gms`, variable declarations (lines 123–176) precede `.l` initializations (lines 251–252), and the `it(i)` set definition using `.l` values appears at line 260 — well after both.

### Bug 2: Zero-valued table rows dropped from parameter initialization ($116)

The `zz(*,i)` table in the original model has rows for `depr`, `dstr`, and `te` where all values are `0.0`. The `sectres(*,i)` table has a row for `dst` where all values are `0.0`. The emitter omits these all-zero rows during parameter initialization, but the model later references them:

```gams
depr(i) = zz("depr",i);   * $116 — "depr" label not in zz
dstr(i) = zz("dstr",i);   * $116 — "dstr" label not in zz
te(i)   = zz("te",i);     * $116 — "te" label not in zz
dst.l(i) = sectres("dst",i);  * $116 — "dst" label not in sectres
```

## Reproduction

```bash
# Translate and compile:
.venv/bin/python -m src.cli data/gamslib/raw/korcge.gms -o /tmp/korcge_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams \
    /tmp/korcge_mcp.gms lo=3 o=/tmp/korcge_mcp.lst

# Check errors:
grep '\$318\|\$140\|\$116' /tmp/korcge_mcp.lst
```

Output:
```
****                 $140      $140
****         $318
****         $318
****                    $116
****                    $116
****                $116
****                         $116
```

## Error Details

| Line | Error | Symbol | Description |
|------|-------|--------|-------------|
| 59 | $140 | `e.l(i)`, `m.l(i)` | Unknown symbol — used before variable declaration |
| 105 | $318 | `e(i)` | Domain list redefined — earlier `.l` usage created implicit symbol |
| 106 | $318 | `m(i)` | Domain list redefined — same as above |
| 70 | $116 | `zz("depr",i)` | Label "depr" unknown — zero-valued row dropped |
| 71 | $116 | `zz("dstr",i)` | Label "dstr" unknown — zero-valued row dropped |
| 73 | $116 | `zz("te",i)` | Label "te" unknown — zero-valued row dropped |
| 283 | $116 | `sectres("dst",i)` | Label "dst" unknown — zero-valued row dropped |

## Root Cause

1. **Declaration ordering ($318/$140):** The emitter does not enforce GAMS declaration-before-use ordering. Statements that reference `.l` suffixes must appear after the corresponding `Variables` block. The emitter should either reorder these statements or defer `.l`-dependent assignments to a post-declaration section.

2. **Zero-value label loss ($116):** When converting `Table` data to inline parameter assignments, the emitter filters out entries with value 0.0 (since GAMS defaults uninitialized parameters to 0). However, this optimization drops the **label declaration** itself — GAMS needs to see the label to recognize it in subsequent string-indexed lookups like `zz("depr",i)`.

## Fix Approach

**Bug 1:** Reorder emitted blocks so that all `.l`-referencing statements appear after the Variables declaration section.

**Bug 2:** When a table has a string/UEL first dimension and the original model references specific labels via quoted strings, preserve those labels in the emitted parameter even when their values are all zero. Emit `zz("depr",i) = 0;` explicitly, or include zero-valued rows in the data initialization block.

## Related Issues

- Cascading errors: $257 (solve not checked) and $141 (omega.l unassigned) are consequences of the primary errors above

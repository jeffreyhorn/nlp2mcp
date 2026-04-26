# turkpow: Table-data emission produces spurious entries when source rows have empty cells / `+inf` values

**GitHub Issue:** [#1316](https://github.com/jeffreyhorn/nlp2mcp/issues/1316)
**Status:** OPEN
**Severity:** High — blocks turkpow compile (Error 170 cascade) even after #1292's line-wrap fix
**Discovered:** Sprint 25 Day 9 (PR #1314, post-#1292 verification)
**Affected Models:** turkpow (observed); other models with table-data rows that have empty cells or `+inf` values may share the same shape

---

## Problem Summary

The emitter mis-handles table data when source rows have empty cells (interpreted by GAMS as "no value, default zero") or use `+inf` for unbounded columns. The result is a Parameter declaration whose data block contains BOTH the correct row-by-column entries AND spurious entries that conflate values from other rows as labels.

For turkpow, the source `Table mdatat(m,labels)` includes:

```gams
Table mdatat(m,labels) 'data for thermal plants'
             initcap  avail      opcost  opcost-g   capcost  capcost-g     life  maxcap
*               (mw)           (mill tl       (%)  (mill tl        (%)  (years)    (mw)
   gas-t         120     .8         1.7     -.005       2.5                  30    +inf
   oil           847     .9         1.1     -.005       4.5       -.01       30    +inf
   lignite-1     960     .8          .6     -.005       5         -.01       30
   lignite-2             .8          .2     -.005       7         -.01       30    2500
   lignite-3             .8          .2     -.005       7         -.01       30    3500
   nuclear               .8          .3     -.005       9         -.02       30    +inf;
```

The emitted Parameter block contains correct entries (e.g., `'lignite-3'.avail 0.8`, `'lignite-3'.opcost 0.2`, ..., `'lignite-3'.maxcap 3500`) PLUS spurious extras like `'lignite-3'.'.9' 0.8`, `'lignite-3'.initcap 0.3`, `'lignite-3'.'-.005' -0.005`, `'lignite-3'.'4.5' 9`, `'lignite-3'.'-.01' -0.02`, `'lignite-3'.'30' 30`, `'lignite-3'.'inf' inf`.

The spurious labels are VALUES from neighboring rows being mis-attributed as labels.

GAMS then rejects with cascading `Error 170 (Domain violation)` — the labels `.9`, `4.5`, `-.005`, etc. aren't in the `labels` set declaration.

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/turkpow.gms -o /tmp/turkpow_mcp.gms --skip-convexity-check --quiet
gams /tmp/turkpow_mcp.gms action=c lo=2 2>&1 | grep -B 1 "\$170\|Error 170" | head -20

# Inspect the spurious entries:
grep "lignite-3" /tmp/turkpow_mcp.gms | head -3
```

## Likely Root Cause

The table parser appears to associate values across row boundaries when:
- A source row has empty cells (e.g., `lignite-1`'s `maxcap` column is empty).
- A source row uses `+inf` (which the parser may handle as a special token).
- Adjacent rows have varying cardinalities of populated columns.

The result is that values from earlier rows leak into later rows' data dict — but the LABEL slot is wrongly populated with another row's VALUE (e.g., `'lignite-3'.'.9'` where `.9` is `oil`'s `avail` value).

Likely fix sites:
- `src/ir/parser.py` (table parsing — where row × column data is collected).
- `src/emit/original_symbols.py::emit_original_parameters` (data emission — where the dict is serialised; the `_expand_table_key` helper at line ~957 may be the smoking gun).

The issue is consistent with prior table-parsing bugs (e.g., #1007 zero-filtering, #913 last-write-wins dedup): table data with non-rectangular row shapes triggers known-fragile code paths.

## Candidate Fix Approaches

1. **Audit `_expand_table_key`** for handling of empty cells and `inf` literals. Specifically, ensure that an empty cell is NOT promoted to a string key in adjacent rows. Add a unit test that mirrors turkpow's "lignite-3 with empty initcap" shape.
2. **Audit the table-row tokenization** in the parser. The source row `lignite-3 .8 .2 -.005 7 -.01 30 3500` has 8 values for 8 labels, plus a leading `lignite-3` row label. If the parser is splitting by whitespace AND treating `.9` (from a previous row's column) as a continuation of the current row, the boundary is wrong.
3. **Filter post-parse:** strip Parameter values whose key contains any element NOT in the parameter's declared label set. This is a defensive emitter-level filter; it doesn't fix the parser bug but makes the emission compile.

Approach (3) is the safest immediate fix; (1) and (2) are the structural fix.

## Expected Impact

Direct: turkpow's MCP compiles cleanly post-fix; turkpow either solves (matching its Sprint 25 Priority 2 recovered-translate target) or hits its next latent bug.

Same shape may affect other models with non-rectangular table data (e.g., models with optional columns or `+inf` values). Need a corpus audit during the fix.

## Files

- `src/ir/parser.py` (table-row tokenization; likely root cause).
- `src/emit/original_symbols.py::emit_original_parameters` and `_expand_table_key` (data emission; possible defensive filter site).
- `data/gamslib/raw/turkpow.gms` — primary repro corpus.

## Related

- `#1292` (resolved Sprint 25 Day 9): the 144,628-char `stat_zt` line-wrap was the FIRST blocker on turkpow; this is the SECOND.
- `#1007` (table data zero-filtering label-drop) — same general code area.

## Status

Open. Filed during Sprint 25 Day 9 (PR #1314). Targeting Sprint 26 carryforward.

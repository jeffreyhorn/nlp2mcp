# qdemo7: Solve regression — `model_optimal` → `model_infeasible (status 4)`

**GitHub Issue:** [#1352](https://github.com/jeffreyhorn/nlp2mcp/issues/1352)
**Status:** RESOLVED
**Severity:** High — Sprint 25 Day 11 Checkpoint 2 NO-GO contributor (solve, +1 model_infeasible)
**Date:** 2026-05-03 (resolved 2026-05-04)
**Affected Models:** qdemo7 (SEQ=292, QCP, Nonlinear Simple Agricultural Sector Model QCP)
**Regression introduced:** between Sprint 25 Day 0 and Day 11

---

## Summary

`qdemo7` solved at Sprint 25 Day 0 (model_optimal, obj=1134.681). On the current branch solve regressed to global `Infeasible (status 4)` (note: globally infeasible, not "Locally Infeasible" — strictly worse than #1351's status 5).

---

## Resolution

### Root cause: table parser column-alignment bug after preprocessor quoting

The qdemo7 source has a `Table demdat(c,*) 'demand data'` whose columns include hyphenated names (`ref-p`, `ref-q`, `exp-p`, `imp-p`):

```gams
Table demdat(c,*) 'demand data'
            ref-p    ref-q   elas  exp-p  imp-p
   wheat      100     2700    -.8           140
   beans      200      900    -.4           270
   onions     125      700   -1.      40    inf
```

For wheat/beans/maize, the `imp-p` column has a value (140 / 270 / 85) but `exp-p` is blank.

The preprocessor's `normalize_special_identifiers` auto-quotes hyphenated headers when the table has a description (`'demand data'`), so the header line becomes:

```gams
            'ref-p'    'ref-q'   elas  'exp-p'  'imp-p'
```

Each apostrophe-pair shifts subsequent columns by 2 chars. Data rows are *unchanged* (numeric values aren't quoted). Lark's reported token columns therefore reflect the **post-quote layout for headers** but the **original layout for data values** — they no longer line up.

For the `wheat 100 2700 -.8 140` row, `_merge_dotted_col_headers` returned header positions in the post-quote layout (with cumulative apostrophe-shifts). The gap-midpoint range matcher then placed `140` at column 45 under `'exp-p'` (post-quote range 39–48) instead of `imp-p` (post-quote range 48+). Result for wheat:

- `ce(wheat) = yes` (incorrect — `exp-p=140` made it look exportable)
- `cm(wheat) = yes` (because `cm(c) = yes$(demdat(c,"imp-p") < inf)` and the parser-misread `imp-p=0 < inf` is true)
- `pe(wheat) = 140`, `pm(wheat) = 0` (both inverted from the source)

The emitted MCP then had:

```gams
stat_exports(wheat).. nu_dem(wheat) - piL_exports(wheat) =E= 140
stat_imports(wheat).. -nu_dem(wheat) - piL_imports(wheat) =E= 0
```

`nu_dem(wheat)` cannot be both ≥140 and ≤0; PATH detected the contradiction at iteration 0 (`DuplicateRows Implied: stat_exports(wheat) stat_imports(wheat)`) and exited with `*** EXIT - infeasible.` (`MODEL STATUS 4 Infeasible`).

The seven post-Day-0 emit changes flagged in the original investigation (#1322 NA-cleanup, #1192 bounds-collapse, the new `((-1)*pe(c))` and `pm(c)` obj-gradient terms in stat_exports / stat_imports, the new `((-1)*(alpha+beta*natcon))` derivative in stat_natcon, the `cn(c)` regating, and the dropped `nu_dem.fx`) were **all correct improvements** that *exposed* the underlying parser bug. Day 0's emit was incomplete enough that the table-parsing error didn't manifest as a contradiction; the more correct Sprint 25 emit pulls the wrong parameter values into balanced equations and the contradiction surfaces.

### Fix

`src/ir/parser.py::_merge_dotted_col_headers` now compensates for the apostrophe-shift after greedy dot-merging. For each header in source order:

- If the source token is quoted (auto-quoted by the preprocessor — detected via `len(str(token)) > len(name) + 2`), the identifier itself starts one column right of the apostrophe, and the cumulative shift before this header is removed.
- Otherwise, only the cumulative shift from preceding quoted headers on the same line is removed.

The returned `(name, col_pos, source_width)` tuple now carries the **original-source-equivalent** identifier position and width, restoring alignment with unchanged data row positions. The downstream gap-midpoint matcher is unchanged.

### Verification

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --model qdemo7
…
Translate Results:  Success 1 (100.0%)
Solve Results:      Success 1 (100.0%)  ← was: failure / model_infeasible (status 4)
Comparison Results: Match     1 (100.0%) ← was: not_tested
Full pipeline success: 1/1 (100.0%)
```

```bash
.venv/bin/python -c "
from src.ir.parser import parse_model_file
ir = parse_model_file('data/gamslib/raw/qdemo7.gms')
demdat = ir.params['demdat']
for c in ('wheat','beans','maize','onions','cotton','tomato'):
    print(f'{c}: exp-p={demdat.values.get((c,\"exp-p\"),0)}, imp-p={demdat.values.get((c,\"imp-p\"),0)}')
"
# wheat: exp-p=0.0, imp-p=140.0   ← wheat correctly imports at 140 (was: exp at 140)
# beans: exp-p=0.0, imp-p=270.0
# maize: exp-p=0.0, imp-p=85.0
# onions: exp-p=40.0, imp-p=inf
# cotton: exp-p=300.0, imp-p=inf
# tomato: exp-p=60.0, imp-p=inf
```

The current MCP objective is 1589042.386 (matching the corrected NLP via `Comparison: Match`). The Day 0 baseline objective of 1134.681 was based on a *misparsed* table — i.e., a different (incorrect) problem; both Day 0 NLP and Day 0 MCP solved the same wrong problem to similar wrong values.

### Acceptance criteria status

- ✅ `qdemo7` solve returns `model_optimal`. (objective is 1589042.386 not 1134.681 because Day 0's value reflected the misparsed table)
- ✅ The pre-existing #918 mismatch is unchanged — and in fact this fix ALSO makes the comparison MATCH for qdemo7, making #918 also closeable for this model.
- ✅ Regression test added: `test_qdemo7_demdat_aligns_under_correct_columns`.

---

## Related

- #918 (open) — qdemo7 empty MCP equations for conditionally-absent variables (pre-existing; this fix incidentally closes the comparison-mismatch shape for qdemo7 by fixing the parser).
- #673 — original fix that introduced auto-quoting of hyphenated headers in tables with descriptions; this issue's fix patches the column-alignment side effect.
- #1322 — NA-cleanup (post-Day-0 emit change that helped surface the bug; correct as-is).
- #1192 — bounds-collapse guard (post-Day-0 emit change that helped surface the bug; correct as-is).
- Sister regression: `launch` (#1351, fixed via different mechanism — Pattern C consolidation revert).

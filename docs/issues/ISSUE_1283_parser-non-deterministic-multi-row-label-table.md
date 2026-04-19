# Parser: Non-Deterministic Table Parsing for Multi-Row-Label Rows `(v1,v2,v3).col`

**GitHub Issue:** [#1283](https://github.com/jeffreyhorn/nlp2mcp/issues/1283)
**Status:** OPEN — Deferred to Sprint 25
**Severity:** High — Silently corrupts emitted parameter values on an unknown fraction of pipeline runs; can mask or confound other bugs downstream
**Date:** 2026-04-19
**Last Updated:** 2026-04-19
**Affected Models:** `chenery` (reproducer); any model using multi-row-label table expansion
**Labels:** `sprint-25`

---

## Problem Summary

The parser produces **non-deterministic output** when translating a GAMS source with a table whose row labels use the multi-value dotted expansion syntax `(v1,v2,v3).col`. For `chenery.gms`, three back-to-back CLI invocations of the same command produced different output — typically 2 correct + 1 corrupted per 3 runs during manual reproduction. The corrupted variant silently shifts every value by one column and drops the last column entirely.

## Source Construct

```gams
Table ddat(lmh,*,i) 'demand parameters'
                            light-ind  food+agr  heavy-ind  services
   (low,medium,high).ynot        100      230         220       450
   medium.p-elas                -.674     -.246      -.587     -.352
   high  .p-elas               -1        -1         -1        -1    ;
```

The intended expansion is 12 entries per `ynot` row-label (3 labels × 4 columns). Under the flaky path, the parser emits 9 entries, shifted right by one column:

- **Correct:** `low.ynot.'light-ind' 100, .'food+agr' 230, .'heavy-ind' 220, .services 450`
- **Corrupted:** `low.ynot.'light-ind' 230, .'food+agr' 220, .'heavy-ind' 450`  ← light-ind gets 230, services dropped

## Reproduction

```bash
for i in 1 2 3; do
  .venv/bin/python -m src.cli data/gamslib/raw/chenery.gms -o /tmp/chenery_mcp_$i.gms --quiet
done

for i in 1 2 3; do
  echo "=== run $i ==="
  grep "ddat" /tmp/chenery_mcp_$i.gms | head -1 | tr ',' '\n' | grep "low.ynot" | head -4
done
```

On my machine a roughly 1-in-3 rate was observed during manual reproduction; the rate may vary with `PYTHONHASHSEED`, memory layout, and concurrent CPU load.

## Impact

- **chenery** (tracked under #1177 as `model_infeasible`): corrupt parameter data has been silently contaminating `chenery_mcp.gms` on some pipeline runs. It's plausible that this has been confounding #1177's investigation — investigators have been debugging KKT/alias-derivative theories against a baseline that sometimes had wrong data loaded.
- **Other corpus models** using `(v1,v2,...).col` expansion are potentially affected. Audit needed.
- **PR #1282's Day 13 addendum** caught this because a reviewer spotted the corrupt values in the freshly-regenerated `chenery_mcp.gms`; the prior Day 13 retest (`d0b655cc`) happened to produce correct output and the bug went unnoticed.

## Suspected Root Cause

Non-determinism in parser / IR under identical inputs points to ordered-but-non-deterministic data structure behavior. Candidates:

1. **Dict / set iteration order** interacting with column-header keys (`light-ind`, `food+agr`, etc., which contain non-alphanumeric characters). Python's `set`/`dict` are order-preserving in CPython 3.7+, but intermediate state with ad-hoc ordering (e.g., temporary `set()` membership checks driving a fan-out loop) can still produce different results across runs when hash seeds differ.
2. **Regex backtracking** in the table-row-header tokenizer, specifically for headers containing hyphens or plus signs (`light-ind`, `food+agr`). A rule that's supposed to greedily match a single token may sometimes split at the punctuation in a way that shifts the column-alignment anchor by one.
3. **Lark ambiguity resolution** (cf. KU-27) picking a different alternative on different runs.

## Suggested Fix

1. **Pin down determinism.** Add `PYTHONHASHSEED=0` (or equivalent) to the pipeline scripts and CI config until the root cause is fixed — this forces the bug to be consistently-reproducing rather than intermittent.
2. **Write a determinism unit test.** Exercise the `(v1,v2,v3).col` pattern 10× in a loop and assert identical byte-level output.
3. **Trace the flaky path.** Instrument parser / emitter table-parsing paths with logging; run the reproduction until the flaky variant fires, then compare logged state against a known-good run.
4. **Fix the underlying ordering / tokenization bug.** Likely in `src/ir/parser.py` table handler or `src/gams/gams_grammar.lark` table rules.

## Regression Guards

After fix:

- `chenery_mcp.gms` must emit correct table values on every run — 10× seed sweep via `PYTHONHASHSEED=1..10`.
- Any other corpus model using `(v1,v2,...).col` maintains correct output. Spot-check CGE family, `twocge`, and others with multi-row tables.
- **Broader test:** the full `gamslib_status.json` translate results must be byte-stable across 10 consecutive pipeline runs with different hash seeds. This is a useful determinism guard for the whole project and should be added to CI.

## Related

- **#1177** (chenery: MCP Locally Infeasible after $171 fix): data corruption from this bug may be masking or creating the infeasibility; investigation of #1177 should verify which chenery_mcp.gms variant was being analyzed.
- **KU-27** (Lark 1.1.9 vs 1.2+ grammar disambiguation, resolved in PR #1267): different bug, same "parser non-determinism breaks the pipeline" family. The `model_all_except` fix there was defensive; a similar defensive-coding pass may be needed here once the root cause is identified.
- **Sibling Sprint 25 issues:** #1275–#1281.

## References

- PR #1282 review comment [#3107378559](https://github.com/jeffreyhorn/nlp2mcp/pull/1282#discussion_r3107378559)
- GAMSlib source: `data/gamslib/raw/chenery.gms` (`ddat` and `tdat` table declarations)

## Estimated Effort

4–6 hours (instrument + reproduce on-demand + root-cause + fix + determinism regression test).

## Files Involved

- `src/ir/parser.py` (table row-header expansion path)
- `src/gams/gams_grammar.lark` (table rules)
- `data/gamslib/raw/chenery.gms` — primary reproducer source
- `tests/unit/ir/test_table_parsing.py` or similar — new determinism test

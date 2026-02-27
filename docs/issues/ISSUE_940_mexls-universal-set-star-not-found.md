# mexls: Universal Set '*' Not Found in ModelIR

**GitHub Issue:** [#940](https://github.com/jeffreyhorn/nlp2mcp/issues/940)
**Status:** OPEN
**Severity:** Medium — Model parses but cannot be translated (missing universal set support)
**Date:** 2026-02-26
**Affected Models:** mexls
**Sprint:** 21 (Day 11 triage)

---

## Problem Summary

The `mexls.gms` model (GAMSlib SEQ=210, "Mexico Steel - Large Static") parses successfully but fails during KKT translation because the model references the GAMS universal set `'*'`, which is not represented in the ModelIR.

---

## Model Details

| Property | Value |
|----------|-------|
| GAMSlib SEQ | 210 |
| Solve Type | LP |
| Convexity | verified_convex |
| Reference Objective | 27569.5989 |
| Parse Status | success |
| Translate Status | failure — `internal_error` |

---

## Error Message

```
Error: Invalid model - Set or alias '*' not found in ModelIR.
Available sets: ['im', 'ir', 'is', 'j', 'l', 'mm', 'mr', 'ms', 'pm', 'pr', 'ps',
'cs', 'craw', 'cm', 'cr', 'crv', 'cmr', 'cms', 'crs', 'css', 'cf', 'ce', 'cfv',
'o', 'own', 'isex', 'res', 'ds', ...]
```

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/mexls.gms -o /tmp/mexls_mcp.gms
# Or:
python scripts/gamslib/run_full_test.py --model mexls --only-translate --verbose
```

---

## Root Cause

In GAMS, `'*'` is the "universal set" — a predefined set that contains all labels (set elements) used anywhere in the model. It does not need to be declared explicitly. Some models use `'*'` as a domain in variable or equation declarations, or in display/report statements.

The error is raised in `src/ad/index_mapping.py:194`:
```python
f"Set or alias '{set_or_alias_name}' not found in ModelIR. "
```

The ModelIR does not currently have a representation for the universal set `'*'`. When the KKT builder encounters a variable or equation declared over `'*'`, it tries to look up the set definition and fails.

---

## Possible Fixes

| Approach | Impact | Effort |
|----------|--------|--------|
| Add implicit universal set `'*'` to ModelIR during parsing — populate with all set elements encountered | High — would unblock mexls and any other model using `'*'` | Medium |
| Special-case `'*'` in index_mapping — compute the union of all set elements | Medium | Low-Medium |
| Replace `'*'` references during preprocessing with the actual superset | Medium | Medium |

### Implementation Notes

The universal set `'*'` should contain the union of all set elements declared in the model. During IR construction:
1. Track all set elements as they are parsed
2. Create a synthetic set `'*'` in `ModelIR.sets` containing all elements
3. Or: in `index_mapping.py`, when encountering `'*'`, compute the union dynamically

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/ad/index_mapping.py:190-200` | Where the error is raised |
| `src/ir/parser.py` | How set domains are parsed — does it preserve `'*'`? |
| `src/ir/model_ir.py` | ModelIR structure — where to add universal set |
| `data/gamslib/raw/mexls.gms` | Original model to inspect `'*'` usage |

---

## Related Issues

- None directly — this is a unique universal set support gap

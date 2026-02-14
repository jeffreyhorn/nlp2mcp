# Validation: Dynamic Set `ie` Has No Members at Equation Instantiation (ganges, gangesx)

**GitHub Issue:** [#723](https://github.com/jeffreyhorn/nlp2mcp/issues/723)
**Status:** Open
**Severity:** High — Blocks translation of ganges and gangesx models; equations using `ie` domain produce no instances
**Discovered:** 2026-02-13 (Sprint 19, after Issues #714 and #719 fixed conflicting bounds and circular dependency)
**Affected Models:** ganges, gangesx

---

## Problem Summary

The ganges and gangesx models define a dynamic subset `ie(i)` that is populated at execution time via a conditional assignment:

```gams
ie(i) = yes$(a("source",i) + a(i,"sink"));
```

Eight equations use `ie` as their domain (e.g., `export(ie)`, `domestic(ie)`, `bal(ie)`). Because the pipeline cannot statically resolve the members of `ie` — it depends on the runtime values of parameter `a(i,j)` — the equation instantiation phase finds zero members for `ie` and fails with:

```
Error: Invalid model - Equation 'export' uses domain set 'ie' which has no members
```

---

## Reproduction

**Models:** `ganges` (`data/gamslib/raw/ganges.gms`), `gangesx` (`data/gamslib/raw/gangesx.gms`)

**Command:**
```bash
python -m src.cli data/gamslib/raw/ganges.gms
python -m src.cli data/gamslib/raw/gangesx.gms
```

**Error (identical for both):**
```
Error: Invalid model - Equation 'export' uses domain set 'ie' which has no members
```

**Warnings emitted before the error (8 total):**
```
WARNING  validation.model - Equation 'export' uses dynamic set 'ie' as domain, which currently has no members
WARNING  validation.model - Equation 'domestic' uses dynamic set 'ie' as domain, which currently has no members
WARNING  validation.model - Equation 'ares' uses dynamic set 'ie' as domain, which currently has no members
WARNING  validation.model - Equation 'bres' uses dynamic set 'ie' as domain, which currently has no members
WARNING  validation.model - Equation 'jres' uses dynamic set 'ie' as domain, which currently has no members
WARNING  validation.model - Equation 'bal' uses dynamic set 'ie' as domain, which currently has no members
WARNING  validation.model - Equation 'benefit' uses dynamic set 'ie' as domain, which currently has no members
WARNING  validation.model - Equation 'mtarget' uses dynamic set 'ie' as domain, which currently has no members
```

---

## Root Cause

### Dynamic set `ie` declaration (line 27 of `ganges.gms`)

```gams
sets  i    rivers and canals / source, kesinga, hirakud, sambalpur,
                               tikarapara, naraj, cuttack, sukamundi, ... /
      ie(i)    efficiency nodes
```

`ie` is declared as a subset of `i` with **no initial members** — no `/.../ ` enumeration follows.

### Dynamic set population (line 94 of `ganges.gms`)

```gams
ie(i) = yes$(a("source",i) + a(i,"sink"));
```

This execution-time assignment populates `ie` with all nodes `i` that have a nonzero arc coefficient to/from `"source"` or `"sink"` in the `a(i,j)` parameter. The `a` parameter is populated from a `Table` declaration (lines 46-92), so the data IS statically available — but the pipeline does not execute assignment statements to resolve dynamic set membership.

### Equations using `ie` (lines 145-152 of `ganges.gms`)

```gams
equations export(ie)        capacity on water export
          domestic(ie)      domestic water use
          ares(ie)          net canal capacity  - Loss
          bres(ie)          net canal capacity  - No Loss
          jres(ie)          capacity of junction node
          bal(ie)           material balance at each efficiency node
          benefit           objective function definition
          mtarget(ie)       minimum supply target ;
```

### Validation failure (line 337-338 of `src/validation/model.py`)

The validator checks if equation domain sets have members. Since `ie` was never populated (no execution of the `ie(i) = yes$...` assignment), it reports zero members.

---

## Fix Approaches

### Option A: Execute simple dynamic set assignments (recommended)

Add an execution phase that evaluates conditional set assignment statements of the form:

```gams
set_name(indices) = yes$condition;
```

When the condition references only statically-known parameters (like `a` which comes from a `Table`), the pipeline can evaluate the condition for each element of the parent set and populate the dynamic subset.

**Scope:** `src/ir/builder.py` or a new `src/ir/set_evaluator.py` module. Requires:
1. Detecting assignment statements that target set membership (`= yes$...`)
2. Evaluating the dollar condition using the already-parsed parameter data
3. Populating the `SetInfo.elements` in the `ModelIR`

This is similar to the existing `condition_eval.py` logic but applied at the set level rather than equation level.

### Option B: Fall back to parent set domain

When a dynamic subset has no members but its parent set does, use the parent set's domain for equation instantiation and add a dollar condition to filter at runtime. This is less precise but simpler.

**Tradeoff:** Generates more equation instances than needed (all `i` instead of just `ie`), which increases the MCP problem size but is functionally correct since the dollar condition filters inactive instances.

### Option C: Special-case `yes$` pattern

Recognize `ie(i) = yes$(expr)` as a set-filtering pattern and convert it to a compile-time set evaluation when `expr` references only statically-known data.

---

## Additional Context

- The `gangesx` model is an extended version of `ganges` with the same set structure
- Both models are NLP water resource optimization models from the GAMSLib
- The `a(i,j)` parameter used in the condition is fully defined via a `Table` statement with all values statically available
- Similar dynamic set patterns (`set_name(i) = yes$condition`) appear in other GAMSLib models (see also Issue #671 for `orani` dynamic domain extension)

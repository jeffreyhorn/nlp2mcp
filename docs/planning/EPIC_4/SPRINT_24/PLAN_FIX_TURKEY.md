# Plan: Fix turkey MCP (Compilation Errors → Solve to Optimality)

**Goal:** Fix the turkey model so it compiles, solves, and reaches
optimality.

**Related issue reference:** Sprint 24 Day 11 triage — turkey classified
as `path_syntax_error` (`compilation_error`)
**Estimated effort:** 3–5 hours (2 compilation blockers + potential
solve-time issues)
**Models potentially unblocked:** turkey (may share patterns with other
large agricultural sector models)
**NLP reference objective:** 29330.1580

---

## Pre-fix State

The turkey model (Turkish Agricultural Sector Model, SEQ=108) parses
and translates successfully, but the generated MCP file fails to compile
in GAMS with 9 errors:

```
****  161  Conflicting dimensions in element     (6 occurrences on set ao)
****  116  Label is unknown                      (1 occurrence: "other-q")
****  257  Solve statement not checked because of previous errors
****  141  Symbol declared but no values have been assigned
```

Errors 161 and 116 are the root causes; 257 and 141 are cascading
failures from the unresolved compilation.

---

## Model Structure

Turkey is a large agricultural sector model (NLP with LP linearization):
- 38 crops (`c`), 24 annual (`ca ⊂ c`), 14 tree (`ct ⊂ c`)
- 5 livestock commodities (`cl`), 7 livestock types (`l`)
- 50 regions (`r`), 4 soil types (`s`), 4 quarters (`tq`)
- Dynamic set `cll(cl,l)` populated at runtime from demand data
- Post-solve reporting uses 2D mapping set `ao(ctp,c)` with dotted
  notation
- Objective: maximize `cps` (consumer + producer surplus)

---

## Issue 1: 2D Mapping Set `ao` Emitted as 1D (Error 161)

### Root Cause

The original model declares `ao` as a 2D mapping set using GAMS
dotted notation:

```gams
Set ao 'aggregated output'
    / grains.(wheat, corn, rye, rice, barley)
      pulses.(chickpea, drybean, lentil)
      vegetables.(potato, onion, gr-pepper, tomato, cucumber, melon)
      ... /;
```

The parser stores these as 1D members with dotted names:
`['grains.wheat', 'grains.corn', ...]` with `domain: ()`.

The emitter outputs:

```gams
ao /grains.wheat, grains.corn, .../
```

GAMS interprets the dotted elements as 2D (since dots separate
dimensions in GAMS), but the set declaration has no domain —
Error 161 "Conflicting dimensions in element".

### Key Insight: Post-Solve Only

The set `ao` and the related parameter `acctg` appear **only** in the
post-solve reporting section (`$sTitle Value Accounting`, lines
1108–1136 of the original model).  They are NOT referenced by any
equation, variable, or constraint in the optimization model.  The same
applies to set `ctp` and parameters `procc`, `prot`, `areac`,
`costsum`, `acctg`.

### Fix Strategy

**Option A (recommended):** Exclude post-solve-only symbols from the
MCP output.  Detect that `ao`, `ctp`, `acctg`, `procc`, `prot`,
`areac`, `costsum` are unreferenced by any equation/variable/constraint
and omit them.  This eliminates the error entirely without modifying set
emission logic.

**Option B (general fix):** When emitting a set whose members contain
dots and whose IR domain is empty, infer the dimensionality from the
member notation and emit with the correct domain.  E.g., detect that
`ao` members have `ctp.c` structure and emit `ao(ctp,c) / ... /`.

Option A is simpler and sufficient for turkey.  Option B is more general
but more complex and risks regressions.

### Files

| File | Change |
|------|--------|
| `src/emit/emit_gams.py` or `src/emit/original_symbols.py` | Skip unreferenced post-solve sets/params |

---

## Issue 2: Missing Wildcard Labels in Parameter Data (Error 116)

### Root Cause

The parameters `tradel(l,cl,*)` and `tradec(c,*)` use wildcard domains.
Their data tables include columns like `"other-q"` where all values are
zero.  The emitter omits zero-valued entries from inline data
declarations.

When assignment statements reference `tradel(l,cl,"other-q")`, GAMS
sees `"other-q"` as an unknown label because it never appeared in any
set or parameter data — Error 116.

The affected assignments are pre-solve computations needed for the
model:

```gams
qdl(cl,l) = tradel(l,cl,"production") + tradel(l,cl,"import-q")
          - tradel(l,cl,"export-q") - tradel(l,cl,"other-q");
qdc(c) = tradec(c,"production") + tradec(c,"import-q")
        - tradec(c,"export-q") - tradec(c,"other-q");
```

### Fix Strategy

When emitting wildcard-domain parameters, collect all unique wildcard
labels that appear in **assignment statements** referencing the
parameter.  If a label has no nonzero data entries, emit at least one
dummy entry (e.g., a comment or a zero-valued placeholder) — OR declare
the missing labels via a helper set.

Alternatively, in the emitter's computed parameter assignment phase,
detect references to wildcard parameters with labels not present in the
data and replace them with `0` (since missing GAMS data defaults to 0).

### Files

| File | Change |
|------|--------|
| `src/emit/original_symbols.py` or `src/emit/emit_gams.py` | Handle missing wildcard labels |

---

## Issue 3: Dynamic Set `cll` Has No Compile-Time Members

### Root Cause

The set `cll(cl,l)` is declared empty and populated at runtime:

```gams
Set cll(cl,l) 'tuples of livestock commodities and livestock in model';
cll(cl,l) = yes$betal(cl,l);
```

The IR has `cll.members = []`.  Multiple equations use `$cll(cl,l)` as
a condition:

```gams
mball(cl,l)$cll(cl,l)..  yieldl(cl,l)*xlive(l)/1000 =g= salesl(cl,l);
ndeml(cl,l)$cll(cl,l)..  natconl(cl,l) =e= ...;
```

The Jacobian code cannot evaluate `cll` membership statically, so it
includes all `(cl,l)` instances by default (per the warning).  This may
cause:
- Spurious equation instances in the KKT system
- Unmatched multiplier variables for empty instances
- Incorrect stationarity equations

### Fix Strategy

Pre-evaluate `cll(cl,l)` from the data.  Since
`cll(cl,l) = yes$betal(cl,l)` and `betal` is computed from `qdl`,
`demandl`, and `pdl` (all derived from table data), the members of
`cll` can be determined at IR build time by evaluating the chain:

1. `qdl(cl,l) = tradel(l,cl,"production") + ...`
2. `pdl(cl,l) = pricel(cl,l,"1979")`
3. `demandl(l,cl) = ...` (population-based)
4. `betal(cl,l) = pdl(cl,l) / qdl(cl,l) / demandl(l,cl)`
5. `cll(cl,l) = yes$betal(cl,l)` — nonzero where betal is nonzero

If full evaluation is too complex, a simpler approach: populate `cll`
members from the sparsity pattern of `tradel` data (any `(cl,l)` pair
that has production data is likely in `cll`).

### Files

| File | Change |
|------|--------|
| `src/ir/parser.py` or `src/emit/original_symbols.py` | Pre-evaluate dynamic set from data |

---

## Potential Issue 4: Empty Equation Instances (Post-Compilation)

After compilation errors are resolved, the model may encounter unmatched
multiplier variables (similar to china's Issue 2) for equation instances
where all variable coefficients are zero.  The empty equation detector
(enhanced for china) should handle this, but turkey's larger scale and
dynamic sets may expose additional edge cases.

### Diagnosis

Run the MCP after fixing Issues 1–3 and check for `EXECERROR` /
unmatched variables.  Apply the same `detect_empty_equation_instances()`
analysis.

---

## Verification

**Prerequisite:** Raw GAMSlib sources are gitignored. Download them
first: `python scripts/gamslib/download_models.py --model turkey`

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/turkey.gms -o /tmp/turkey_mcp.gms --quiet

# Compile
gams /tmp/turkey_mcp.gms lo=3 o=/tmp/turkey_solve.lst
# Expected: no compilation errors (Errors 161, 116 fixed)

grep "MODEL STATUS" /tmp/turkey_solve.lst
# Target: MODEL STATUS 1 (Optimal) or 2 (Locally Optimal)

grep "nlp2mcp_obj_val" /tmp/turkey_solve.lst | grep "="
# Expected: ~29330.1580 (matching NLP reference)
```

---

## Success Criteria

- [ ] No compilation errors (Errors 161, 116 resolved)
- [ ] No unmatched variable errors
- [ ] turkey solves to MODEL STATUS 1 or 2
- [ ] Objective matches NLP reference (29330.1580) within tolerance
- [ ] No test regressions (`make test` passes)

---

## Recommended Fix Order

1. **Issue 1** (ao set dimension) — unblocks compilation; likely
   solvable by excluding post-solve symbols
2. **Issue 2** (missing wildcard labels) — unblocks compilation
3. **Issue 3** (dynamic set cll) — fixes equation enumeration
4. **Issue 4** (empty equations) — diagnose after 1–3 are fixed

Issues 1 and 2 are compilation blockers and relatively isolated.
Issue 3 is deeper and may require data-flow analysis to pre-evaluate
the dynamic set.

---

## Related

- **china model**: Fixed in PR #1261 plan; shared the
  `path_syntax_error` / `compilation_error` triage classification.
  China's fixes (parameter ordering, empty inequality detection,
  stationarity Jacobian for subset-domain variables) may partially
  apply if turkey has similar subset patterns.
- **Issue #1133** (fawley): Empty equation detection framework — already
  extended for inequalities in the china fix.

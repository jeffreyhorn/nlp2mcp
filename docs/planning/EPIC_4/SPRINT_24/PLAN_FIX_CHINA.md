# Plan: Fix china MCP (Compilation Error + Stationarity Bug)

**Goal:** Fix the china model so it compiles, solves, and reaches
optimality.

**Related issue reference:** Sprint 24 Day 11 triage — china classified
as `path_syntax_error` (`compilation_error`)
**Estimated effort:** 4–6 hours (3 distinct issues)
**Models potentially unblocked:** china, turkey (same Error 141 ordering/uninitialized-symbol category)
**NLP reference objective:** 40561.5739

---

## Pre-fix State

The china model (Organic Fertilizer Use in Intensive Farming, SEQ=59)
parses and translates successfully, but the generated MCP file fails to
compile in GAMS with Error 141:

```
**** 141  Symbol declared but no values have been assigned.
 162  syield("straw",s,f) = sys(s,f);
```

The parameter `sys(s,f)` is used on line 162 before it is computed on
line 164.  Even after manually fixing the ordering, the model aborts
with `EXECERROR = 4` due to 4 unmatched multiplier variables and
likely-incorrect stationarity coefficients.

---

## Model Structure

China is a linear program modeling fertilizer use for triple-cropping:
- 28 commodities (`ca`), 12 crops (`c ⊂ ca`), 11 fertilizer types
  (`cf ⊂ ca`)
- 11 cropping sequences (`s`), 2 fertility levels (`f`)
- Key equation: `mb(ca).. =G= ... + sum(cf, crec(ca,cf)*xfert(cf))`
- Objective: maximize `income` (via defining equations `cdef`, `incdef`)

The sets `c`, `cf`, `cp`, `cs`, `cu` are all subsets of the superset
`ca`.  Variables declared over `ca` are used with subset indices in
equations (e.g., `xfert(cf)` in `mb(ca)`).

---

## Issue 1: Parameter Assignment Ordering (Error 141)

### Root Cause

The original model has sequential dependencies between `sys` and
`syield`:

```gams
sys(s,f)             = sum(c, cdata(c,"straw-y")*syield(c,s,f));
sys(s,f)             = sys(s,f) - syield("e-rice",s,f)*cdata("e-rice","straw-y");
syield("straw",s,f)  = sys(s,f);
syield("rapes-c",s,f) = .8*syield("rapeseed",s,f);
```

The topological sort in `emit_computed_parameter_assignments()` (in
`src/emit/original_symbols.py`) reorders these so
`syield("straw") = sys(s,f)` appears before `sys` is computed.  This is a cyclic
dependency at the parameter level (`sys` reads `syield`, then `syield`
reads `sys`), but the statement-level sort should split `syield` into
phases at the `sys` dependency boundary.

### Fix Strategy

Debug `_topological_sort_statements()` for why the `syield("straw")`
statement is not placed in a separate phase that depends on `sys`.
Likely causes:
- `sys` not recognized as writable (missing from eligible list)
- Phase boundary detection not triggering on the `sys` read
- The `syield` parameter's early phases pulling later phases with them

### Files

| File | Change |
|------|--------|
| `src/emit/original_symbols.py` | Fix topological sort for `sys`/`syield` pattern |

---

## Issue 2: Empty Inequality Equation Instances (Unmatched Variables)

### Root Cause

After fixing the ordering, GAMS reports 4 unmatched variables:

```
**** Unmatched variable not free or fixed
     lam_mb(gm-seeds)
     lam_mb(c-straw)
     lam_mb(c-gm)
     lam_mb(c-hyacinth)
```

The equation `mb(ca)` evaluates to `0 ≥ 0` for these 4 elements
because no variable has nonzero coefficients for them.  GAMS drops the
empty equation instances but the multiplier variables remain declared
and unpaired.

The existing `detect_empty_equation_instances()` in
`src/kkt/empty_equation_detector.py` only scans **equalities**
(`model_ir.equalities`).  The `mb` equation is `=G=` (inequality), so
it is not analyzed.

### Fix Strategy

Extend `detect_empty_equation_instances()` to also scan inequality
equations.  The function iterates over `model_ir.equalities`; it
should also iterate over `model_ir.inequalities` (or a combined set).
The same coefficient-sparsity analysis applies — check if all variable
coefficients are zero for a given domain instance.

The emitter already emits `.fx = 0` for empty equality multipliers
(Issue #1133 block in `emit_gams_mcp()`).  A parallel block is needed
for inequality multipliers (`lam_*`), or the existing block can be
generalized to handle both.

### Files

| File | Change |
|------|--------|
| `src/kkt/empty_equation_detector.py` | Add inequality equation scanning |
| `src/emit/emit_gams.py` | Emit `.fx = 0` for empty inequality multipliers |

---

## Issue 3: Incorrect Stationarity Jacobian Transpose

### Root Cause

The stationarity equation `stat_xfert(ca)` has incorrect coefficients
in its Jacobian transpose terms.  The equation `mb(ca)` contains:

```gams
sum(cf, crec(ca,cf)*xfert(cf))
```

The correct stationarity for `xfert(cf₀)` requires:

```
∑_{ca'} crec(ca', cf₀) · lam_mb(ca')
```

i.e., sum over all `ca'` of `crec(ca', cf₀) · lam_mb(ca')`.  Since
`ca` is the running index of `stat_xfert`, each `ca'` is expressed as
an offset `ca+N`.  The correct term for offset N should be:

```
crec(ca+N, ca) · lam_mb(ca+N)
```

But the emitter generates:

```
sum(cf__, crec(ca, cf__)) · lam_mb(ca+N)
```

This replaces `crec(ca+N, ca)` (coefficient for a specific `ca'`) with
`sum(cf__, crec(ca, cf__))` (sum of ALL coefficients in row `ca`).

**Concrete example:** For `xfert('c-straw')`, the `lam_mb('straw')`
coefficient should be `crec('straw', 'c-straw') = 0.12`, but the
emitter produces `sum(cf__, crec('c-straw', cf__)) = 1.0`.

### Impact

The wrong coefficients produce incorrect KKT conditions, which means
the MCP would solve to a different point than the NLP optimum even if
Issues 1–2 are fixed.

### Fix Strategy

This is a bug in `_add_indexed_jacobian_terms()` in
`src/kkt/stationarity.py` (around lines 3939–4680).  When the
equation index (`ca`) and variable index (`cf`) are in a
subset–superset relationship and offset expressions are used, the
Jacobian transpose must:

1. Use `crec(ca+N, ca)` — the parameter's first index should be the
   offset-shifted equation element, and the second index should be the
   current variable element
2. NOT wrap the coefficient in `sum(cf__, ...)` — the sum over `cf__`
   is from the original equation body but should be resolved to a
   specific element during transposition

The fix likely involves the element-to-set mapping logic (lines
4244–4289) and how `_replace_indices_in_expr()` handles the parameter
indices during Jacobian transposition for subset-domain variables.

### Files

| File | Change |
|------|--------|
| `src/kkt/stationarity.py` | Fix Jacobian transpose index mapping for subset-domain variables |

---

## Verification

**Prerequisite:** Raw GAMSlib sources are gitignored. Download them
first: `python scripts/gamslib/download_models.py --model china`

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/china.gms -o /tmp/china_mcp.gms --quiet

# Check Issue 1 (parameter assignment ordering / Error 141)
# Confirm `sys(s,f)` is assigned before any use; should not see
# "sys" used before defined during compilation

# Compile
gams /tmp/china_mcp.gms lo=3 o=/tmp/china_solve.lst
# Expected: no compilation errors (Error 141 fixed)
# Expected: no EXECERROR (empty equation multipliers fixed)

grep "MODEL STATUS" /tmp/china_solve.lst
# Target: MODEL STATUS 1 (Optimal) or 2 (Locally Optimal)

grep "nlp2mcp_obj_val" /tmp/china_solve.lst | grep "="
# Expected: ~40561.5739 (matching NLP reference)
```

---

## Success Criteria

- [ ] No compilation errors (Error 141 resolved)
- [ ] No unmatched variable errors (empty inequality instances fixed)
- [ ] Stationarity equations have correct Jacobian coefficients
- [ ] china solves to MODEL STATUS 1 or 2
- [ ] Objective matches NLP reference (40561.5739) within tolerance
- [ ] No test regressions (`make test` passes)
- [ ] turkey model also checked for similar improvements

---

## Recommended Fix Order

1. **Issue 1** (parameter ordering) — unblocks compilation
2. **Issue 2** (empty inequality equations) — unblocks GAMS solve
3. **Issue 3** (stationarity Jacobian) — fixes correctness for optimal
   solution

Issues 1 and 2 are relatively isolated fixes.  Issue 3 is deeper and
may benefit from studying how other models with subset-indexed
variables in sums handle the Jacobian transpose.

---

## Related

- **Issue #1133** (fawley): Same empty-equation pattern but for
  equalities — already fixed
- **turkey model**: Classified with china under the same
  `path_syntax_error` / `compilation_error` triage status; the shared
  compilation blocker is Error 141 (ordering/uninitialized-symbol), so
  turkey likely has similar subset/alias dimension issues
- **Sprint 24 Day 11 triage**: china listed as `path_syntax_error`
  with 1–2h estimate (underestimate given Issue 3)

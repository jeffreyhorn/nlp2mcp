# Plan: Fix Dotted Parameter Key Lookup in Condition Evaluator (#1223)

**Goal:** Fix condition evaluation for parameters with dotted multi-dimensional
keys (e.g., `pdata(i,t,j,"type")` stored as `('9000011.jun.1', 'type')`), so
conditioned equation instances are correctly enumerated and Jacobian entries
are generated.

**Estimated effort:** 2-3 hours
**Models unblocked:** worst (and potentially any model with `Table` parameters
using `*` wildcard domain that produces dotted keys)

---

## Problem Recap

The `worst` model has 4 conditioned equations (`callval`, `putval`, `dd1`,
`dd2`) that all return 0 instances from `enumerate_equation_instances`. This
causes variables `d1`/`d2` to have zero stationarity (`0 =E= 0`), producing
GAMS Error 483.

The root cause is a key format mismatch in `condition_eval.py`:

### What the condition evaluator constructs

For `pdata(i,t,j,"type")` at indices `('9000011', 'jun', '1')`:

```python
concrete_indices = ('9000011', 'jun', '1', 'type')  # 4-tuple
```

### What `pdata.values` actually stores

```python
pdata.values = {
    ('9000011.jun.1', 'type'): 'future',   # 2-tuple, first 3 dims dotted
    ('9000011.jun.1', 'nom'): -35000.0,
    ...
}
```

The parser's Table handler for `Table pdata(i,t,j,*)` collapses the first
3 dimensions into a single dotted string when building the values dict. This
is because GAMS Table syntax treats multi-dimensional row headers as dotted
labels:

```
Table pdata(i,t,j,*) 'portfolio data'
                type     strike    nom       price
9000011.jun.1   future            -35000     96.6
9000011.oct.1   future             15000     96.6
```

The row header `9000011.jun.1` becomes a single string key for the first 3
domain positions.

### Why lookup fails

`condition_eval.py` line 156:
```python
if concrete_indices in param.values:  # ('9000011','jun','1','type') NOT in values
    return param.values[concrete_indices]
```

The 4-tuple `('9000011', 'jun', '1', 'type')` doesn't match the 2-tuple
`('9000011.jun.1', 'type')`.

---

## Fix: Dotted Key Fallback in condition_eval.py

### Step 1: Add dotted-key lookup fallback (~1h)

**File:** `src/ir/condition_eval.py`, around line 156

After the direct tuple lookup fails, try constructing a dotted-key variant:

```python
# Direct lookup
if concrete_indices in param.values:
    return param.values[concrete_indices]

# Dotted-key fallback: for parameters with star (*) domains where the
# parser collapses multi-dimensional row headers into dotted strings,
# try joining the first N indices with '.' and keeping the rest separate.
# Example: ('9000011', 'jun', '1', 'type') → ('9000011.jun.1', 'type')
if param.domain and '*' in param.domain:
    star_pos = param.domain.index('*')
    if star_pos > 1 and len(concrete_indices) > star_pos:
        dotted_prefix = '.'.join(concrete_indices[:star_pos])
        remaining = concrete_indices[star_pos:]
        dotted_key = (dotted_prefix,) + remaining
        if dotted_key in param.values:
            return param.values[dotted_key]
```

**Key insight:** The `*` in `param.domain` tells us where the star domain
starts. All indices before `*` are collapsed into a single dotted string
by the parser. So for `domain = ('i', 't', 'j', '*')` with `star_pos = 3`:
- `concrete_indices[:3] = ('9000011', 'jun', '1')` → `'9000011.jun.1'`
- `concrete_indices[3:] = ('type',)` → remaining
- `dotted_key = ('9000011.jun.1', 'type')` → matches!

### Step 2: Handle non-star dotted keys (~30min)

Some models may have dotted keys without a `*` domain (e.g., `Table p(i,j)`
with row headers `a.b`). For these, try progressively dotting from the left:

```python
# Progressive dotting fallback (for any parameter with dotted keys)
if not found:
    for split_pos in range(2, len(concrete_indices)):
        dotted_prefix = '.'.join(concrete_indices[:split_pos])
        remaining = concrete_indices[split_pos:]
        candidate = (dotted_prefix,) + remaining
        if candidate in param.values:
            return param.values[candidate]
```

This is O(N) where N is the number of dimensions, which is typically 2-5.

### Step 3: Also fix the comparison side (~30min)

The condition `pdata(i,t,j,"type") = call` compares the result of the
parameter lookup against the value of scalar parameter `call`. The `call`
parameter has `values = {(): 0.0}` but the comparison expects a string
match (`'future' = 'call'`). Need to verify that string-vs-number
comparison works correctly.

Actually: `call` is a scalar parameter with value `0.0`, not a string.
But the GAMS model uses `call` as an **acronym** (not a number). Check
if `call` is in `model_ir.acronyms`:

```python
# From the investigation:
# call param: domain=(), values={(): 0.0}
# But 'call' might be an acronym for string comparison
```

The fix: check `model_ir.acronyms` for `call` and use the acronym
string value for comparison instead of the numeric 0.0.

### Step 4: Unit tests (~30min)

**File:** `tests/unit/ir/test_condition_eval_dotted.py` (new)

Test cases:
1. Parameter with `*` domain and dotted keys → correct lookup
2. Condition `pdata(i,t,j,"type") = acronym` → correct string comparison
3. Non-dotted parameter → unchanged behavior (regression)

### Step 5: Integration test (~15min)

- Verify worst equations get nonzero instances after fix
- Verify `stat_d1`/`stat_d2` are no longer `0 =E= 0`

---

## Detailed Key Format Analysis

### How the parser creates dotted keys

In `src/ir/parser.py`, the Table handler reads multi-dimensional row headers
as dotted strings. For `Table pdata(i,t,j,*)`:

```
Row header: "9000011.jun.1"
Column headers: "type", "strike", "nom", "price"
```

The row header is stored as a single string `'9000011.jun.1'` and the
column header becomes the second element: `('9000011.jun.1', 'type')`.

The domain `('i', 't', 'j', '*')` indicates 4 dimensions, but the values
dict only has 2-element tuples because the first 3 are collapsed.

### Why this doesn't affect all models

Most models use set-element-based table rows where each dimension is a
separate column, producing N-tuple keys matching the domain. The dotted
format only occurs when:
1. The Table has a `*` (universal set) domain
2. Row headers use dotted notation for multi-dimensional labels
3. The condition evaluator needs to look up values at runtime

---

## Files Modified

| File | Change |
|------|--------|
| `src/ir/condition_eval.py` | Add dotted-key fallback in parameter lookup |
| `tests/unit/ir/test_condition_eval_dotted.py` | NEW — unit tests |

---

## Risk Assessment

**Low risk:** The fix adds a fallback after the existing lookup fails.
If the dotted key also doesn't match, the behavior is unchanged (returns
default 0.0 or raises error). No existing behavior is modified.

**Potential false positive:** If a parameter has both `('a.b', 'c')` and
`('a', 'b', 'c')` entries, the dotted fallback could match the wrong one.
This is extremely unlikely in practice (requires a parameter with duplicate
entries in different key formats).

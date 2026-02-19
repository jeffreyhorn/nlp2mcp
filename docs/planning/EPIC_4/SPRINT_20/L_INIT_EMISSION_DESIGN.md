# Sprint 20: `.l` Initialization Emission Design

**Created:** 2026-02-19
**Task:** Sprint 20 Prep Task 4
**Unknowns Addressed:** 1.1, 1.2, 1.3, 1.4

---

## Executive Summary

The `.l` initialization emission gap is a **parser gap**, not an emitter gap. The MCP
emitter (`src/emit/emit_gams.py`) already has a complete variable initialization section
that reads from `VariableDef.l` and `VariableDef.l_map`. The problem is that circle's
`.l` assignments (`a.l = (xmin+xmax)/2`) use non-constant expressions — the parser
currently drops these with `return` rather than storing them.

**Fix location:** `src/ir/parser.py` lines ~3560–3575 and `src/ir/symbols.py` +
`src/emit/emit_gams.py`.

**Revised effort estimate:** ~4h (was ~2h assuming emit-only) — requires IR + emit changes.

**Impact:**
- **circle**: Fix will provide PATH with a warm start → high confidence PATH converges
- **bearing**: Constant `.l` assignments ARE already captured and emitted. Bearing's
  remaining blocker is `.scale` (6 scale assignments, no `.scale` support) — a separate
  item. The `.l` fix does NOT unblock bearing.
- **8 models** have expression-based `.l = expr` assignments currently missed: circle,
  circpack, glider, hs62, lnts, mlbeta, mlgamma, robot
- **28 models** with constant `.l` assignments are already captured and emitted correctly

---

## Finding 1.1: Does the IR Currently Capture `.l` Assignments?

**Answer: Partially — constant `.l` values are captured; expression-based are not.**

### What IS captured

`VariableDef` in `src/ir/symbols.py` has:
```python
l: float | None = None          # scalar .l = <constant>
l_map: dict[tuple[str,...], float]  # indexed .l(i) = <constant>
```

The parser (`src/ir/parser.py`, `_apply_variable_bound`) stores constant `.l` values
via `_set_bound_value()`. Example from bearing.gms (already working):
```gams
R.l  = 6.0;       # stored → var_def.l = 6.0
mu.l = 6e-6;      # stored → var_def.l = 6e-6
```

### What is NOT captured

Expression-based `.l` assignments fail at the `_extract_constant()` call in
`_handle_assign` (parser.py ~line 3557). The handler sets `is_variable_bound = True`,
then when `_extract_constant` raises `ParserSemanticError` (non-constant), it hits:

```python
if is_variable_bound:
    # Variable bounds with expressions (circle.gms: a.l = (xmin + xmax)/2)
    # Parse and continue without storing (mock/store approach)
    return   # ← .l expression is DROPPED HERE
```

**Evidence:** Inspecting circle's IR directly:
```python
# circle.gms lines 46–48:
#   a.l = (xmin + xmax)/2;
#   b.l = (ymin + ymax)/2;
#   r.l = sqrt(sqr(a.l - xmin) + sqr(b.l - ymin));

ir = parse_model_file('data/gamslib/raw/circle.gms')
# → a.l=None, b.l=None, r.l=None  (all dropped)
```

**Models with expression-based `.l` assignments (currently missed — 8 total):**
circle, circpack, glider, hs62, lnts, mlbeta, mlgamma, robot

---

## Finding 1.3: Does the MCP Emitter Have a Prolog Section?

**Answer: Yes — a complete initialization section already exists.**

`src/emit/emit_gams.py` lines ~170–240 contains a variable initialization loop
(added in Sprint 18 Day 3 for P5 fix) that:

1. Reads `var_def.l_map` (indexed constant `.l` values)
2. Reads `var_def.l` (scalar constant `.l` value)
3. Falls back to `.lo_map` / `.lo` if no explicit `.l`
4. For POSITIVE variables: emits `var.l = 1` (or clamping)

This section is emitted **after the Variables/Equations declarations** and **before
the Model/Solve statement** — exactly the right location for `.l` initializations.

The section is already present and working for bearing.gms (constant `.l` values).
No new "prolog" concept needs to be created.

---

## Finding 1.2: Will `.l` Init Alone Resolve PATH Infeasibility for circle and bearing?

### Circle (#753)

**Yes — high confidence.**

circle.gms lines 46–48 initialize `a`, `b`, `r` to the centroid of the data points
— a well-chosen starting point close to the minimum enclosing circle solution. The
Sprint 19 PR #750 determinism fix ensures random data is stable. Without `a.l`/`b.l`/`r.l`,
PATH starts at all-zero which is far from the solution (r=0 is the lower bound, at the
boundary of feasibility). With the fix, PATH will receive a warm start.

**Evidence from ISSUE_753:** The issue explicitly identifies missing `.l` initialization
as the root cause. The determinism fix (PR #750) was step 1; `.l` emission is step 2.

### Bearing (#757)

**Partially — `.l` is already emitted, but bearing still fails.**

Bearing's constant `.l` assignments (R.l=6.0, mu.l=6e-6, etc.) are already captured
and emitted by the current pipeline. Bearing translates successfully (`python -m src.cli
data/gamslib/raw/bearing.gms` exits 0). Bearing's blocker is `.scale`:

```gams
mu.scale = 1.0e-6;     # 6 .scale assignments
h.scale  = hmin;
W.scale  = Ws;
PL.scale = 1.0e4;
Ep.scale = 1.0e4;
Ef.scale = 1.0e4;
m.scaleOpt = 1;        # enables scaling
```

GAMS scaling (`.scale`) tells the solver how to normalize variables for numerical
stability. Without scaling, PATH faces a poorly-conditioned problem (mu ranges from
1e-6 to 1, W is ~1e5). The `.scale` attribute is not in `VariableDef` and is not
emitted. **Bearing needs a separate `.scale` emission fix — not addressed by Priority 1.**

---

## Finding 1.4: Models Beyond circle That Would Benefit

**Count: 8 models have expression-based `.l = expr` that would be fixed:**
circle, circpack, glider, hs62, lnts, mlbeta, mlgamma, robot

**28 models** already have constant `.l` assignments captured and emitted. These are
already benefiting from the existing initialization code.

**Total models with any `.l =` assignment in source:** 55 (out of ~219 catalog models)

---

## Fix Strategy

### What Needs to Change

Three files require changes:

#### 1. `src/ir/symbols.py` — Add expression-based `.l` storage fields

```python
@dataclass
class VariableDef:
    # ... existing fields ...
    l: float | None = None
    l_map: dict[tuple[str,...], float] = field(default_factory=dict)

    # NEW: expression-based .l assignments (non-constant RHS)
    l_expr: Expr | None = None            # scalar: a.l = (xmin+xmax)/2
    l_expr_map: list[tuple[tuple[str,...], Expr]] = field(default_factory=list)
    # indexed: x.l(i) = f(i) stored as [(indices_tuple, expr), ...]
```

#### 2. `src/ir/parser.py` — Store expression instead of dropping

In `_handle_assign` (~line 3562), change the `is_variable_bound` early-return to
attempt expression storage:

```python
if is_variable_bound:
    # Try to parse the expression for storage in the IR
    var_name = ...  # extract from target
    bound_kind = ...  # extract attribute ("l", "lo", "up", etc.)
    if bound_kind == "l":
        # Store the expression for later emission
        parsed_expr = self._build_expr(expr_node)
        if indices:
            var.l_expr_map.append((tuple(indices), parsed_expr))
        else:
            var.l_expr = parsed_expr
        return
    # For non-.l bounds (lo/up/fx with expressions): keep existing return
    return
```

**Note:** Only `.l` expressions need to be stored — `.lo`/`.up` expressions can
continue to be dropped (they set bounds, not initializations; PATH tolerates default
bounds). This minimizes scope.

#### 3. `src/emit/emit_gams.py` — Emit expression-based `.l` assignments

In the existing initialization loop (~line 170), after the `l_map`/`l` check, add:

```python
# NEW: Expression-based .l assignments (non-constant RHS)
if not has_init and var_def.l_expr_map:
    for indices, expr in var_def.l_expr_map:
        idx_str = ",".join(indices)
        expr_str = expr_to_gams_string(expr)
        init_lines.append(f"{var_name}.l({idx_str}) = {expr_str};")
        has_init = True
elif not has_init and var_def.l_expr is not None:
    expr_str = expr_to_gams_string(var_def.l_expr)
    init_lines.append(f"{var_name}.l = {expr_str};")
    has_init = True
```

### Before / After Example (circle.gms)

**Current circle_mcp.gms initialization section:**
```gams
* (no .l initialization — section is empty for a, b, r)
```

**After fix:**
```gams
* Variable initializations
a.l = (xmin + xmax) / 2;
b.l = (ymin + ymax) / 2;
r.l = sqrt(sqr(a.l - xmin) + sqr(b.l - ymin));
```

These match the original GAMS source lines 46–48 exactly. PATH will start from the
centroid of the point cloud, which is close to the optimal enclosing circle.

### Key Implementation Note

The expression `r.l = sqrt(sqr(a.l - xmin) + sqr(b.l - ymin))` references `a.l` and
`b.l`. In the emitted MCP, `a.l` and `b.l` are runtime variable attributes — this is
valid GAMS (reading `.l` after it was set by the preceding lines). The emitter must
preserve the original assignment ordering. Since all three assignments are sequential
in the source, storing them in order and emitting in order is correct.

---

## Bearing Assessment

| Aspect | Status |
|--------|--------|
| Constant `.l` captured | ✅ Already working |
| Constant `.l` emitted | ✅ Already working (bearing translates) |
| `.scale` captured | ❌ Not in `VariableDef`, not in grammar |
| `.scale` emitted | ❌ Not emitted |
| PATH convergence | ❌ Blocked by `.scale` absence |

**Conclusion:** The `.l` emission fix does NOT unblock bearing. Bearing requires
a separate `.scale` emission workstream (~3–4h). This should be a Sprint 20 item
separate from Priority 1 (`.l` initialization).

---

## Revised Effort Estimate

| Step | Effort |
|------|--------|
| Add `l_expr`/`l_expr_map` to `VariableDef` | 0.5h |
| Parser: store `.l` expressions instead of dropping | 1h |
| Emitter: emit `l_expr`/`l_expr_map` | 0.5h |
| Tests: unit test for expression `.l` capture + circle regression | 1h |
| End-to-end: run circle through pipeline, verify PATH convergence | 0.5h |
| **Total** | **~3.5h** |

Previous estimate was ~2h (assumed emit-only fix). Actual fix requires IR + emit +
parser changes: **~3.5–4h**.

---

## Impact Assessment

| Model | Current Status | After Fix |
|-------|---------------|-----------|
| circle | Translates ✅, PATH infeasible ❌ | Warm start → PATH likely converges ✅ |
| circpack | Unknown (not tested) | `.l` init added |
| glider | Unknown | `.l` init added |
| hs62 | Unknown | `.l` init added |
| lnts | Unknown | `.l` init added |
| mlbeta | lexer_invalid_char ❌ | No change (parse blocker first) |
| mlgamma | lexer_invalid_char ❌ | No change (parse blocker first) |
| robot | Unknown | `.l` init added |
| bearing | Translates ✅, PATH infeasible ❌ | No change (`.scale` is blocker) |

**Predicted solve rate improvement from `.l` fix alone:** +1–3 models (circle certain;
circpack/glider/hs62/robot possible depending on whether PATH convergence was the
blocker; mlbeta/mlgamma still blocked at parse stage).

---

## Fix Location Summary

| File | Lines | Change |
|------|-------|--------|
| `src/ir/symbols.py` | ~86–95 | Add `l_expr: Expr | None` and `l_expr_map: list` fields to `VariableDef` |
| `src/ir/parser.py` | ~3560–3575 | In `_handle_assign`, store `.l` expressions instead of dropping |
| `src/emit/emit_gams.py` | ~185–195 | Emit `l_expr`/`l_expr_map` in initialization section |

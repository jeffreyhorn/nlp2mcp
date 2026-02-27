# nonsharp: 37 GAMS Compilation Errors in MCP Output

**GitHub Issue:** [#956](https://github.com/jeffreyhorn/nlp2mcp/issues/956)
**Status:** OPEN
**Severity:** High — Model parses and translates but MCP output has 37 compilation errors
**Date:** 2026-02-27
**Affected Models:** nonsharp
**Sprint:** 21

---

## Problem Summary

The `nonsharp.gms` model (nonsharp separation sequencing via Benders decomposition) parses and translates to MCP successfully, but the emitted GAMS file has **37 compilation errors** across several categories:

1. **Bug A**: Unquoted set elements in `.l` initialization (18 errors)
2. **Bug B**: Dynamic subset `k(km)` used as variable domain (2 errors)
3. **Bug C**: Dynamic subset domains lost in equation translation (2+ errors)
4. **Bug D**: Undefined parameter `nfeas` in conditional `.fx` (1 error)
5. **Bug E**: Cascading errors from above ($257, $141) (remaining)

---

## Error Details

### Bug A: Unquoted Set Elements in `.l` Initialization (18 errors)

Set elements `a`, `b`, `c` are emitted bare instead of quoted in variable `.l` initialization:

```gams
cfin.l("col-1",a) = 20.0;     ← $120/$171: 'a' not quoted
cfin.l("col-1",b) = 20.0;     ← $120/$171: 'b' not quoted
cfin.l("col-1",c) = 20.0;     ← $121/$171: 'c' not quoted
...
rec.l("col-1","top",a) = 0.85;  ← $171: 'a' not quoted
rec.l("col-1","top",b) = 0.85;  ← $171: 'b' not quoted
rec.l("col-1","top",c) = 0.85;  ← $121/$171: 'c' not quoted
...  (12 more for rec)
```

**Root cause:** The emitter's `.l` initialization code (`emit_gams.py`) generates element-level assignments from `l_map` but doesn't quote single-letter elements that GAMS might interpret as identifiers. The element `c` is especially problematic because `c` is also declared as a free variable in the model.

**Fix:** Apply `_needs_quoting()` / `_quote_symbol()` to all literal elements in `.l` initialization output. This is similar to the fix applied in PR #951 for `_quote_assignment_index()`.

### Bug B: Dynamic Subset `k(km)` Used as Variable Domain (2 errors)

```gams
Positive Variables
    lam_laerr(k)     ← $187: assigned set used as domain
    lam_intcut(k)    ← $187: assigned set used as domain
```

**Root cause:** In the original model, `k(km)` is a dynamic subset:
```gams
km 'static iterations' / 1*150 /
k(km) 'dynamic iterations' / 1 /;
```

The KKT builder creates multiplier variables `lam_laerr(k)` and `lam_intcut(k)` indexed over the dynamic subset `k`. GAMS Error 187 rejects assigned sets as variable domains.

**Fix:** Use the parent set `km` instead of `k` for multiplier variable domains, with appropriate `$k(km)` conditioning on equations.

### Bug C: Dynamic Subset Domains Lost in Equations (2+ errors)

The original `lpobj` equation uses domain-restricted sets:
```gams
lpobj.. c =e= sum(acol(col), (cost(col)*yp(col) +
    (a1(col) + sum(key(col,stm,cp), a2(col,stm)*rec(col,stm,cp))
    + sum(cp, a3(col,cp)*xin(col,cp)))*fin(col)));
```

The MCP emitter loses these domain restrictions:
```gams
lpobj.. c =E= sum(col, cost(col) * yp(col) +
    (a1(col) + sum((col,stm,cp), a2(col,stm) * rec(col,stm,cp))
    + sum(cp, a3(col,cp) * xin(col,cp))) * fin(col));
```

**Problems:**
1. `acol(col)` → `col`: includes inactive columns
2. `key(col,stm,cp)` → `(col,stm,cp)`: Cartesian product instead of restricted subset
3. Inner `sum((col,stm,cp), ...)` reuses `col` from outer scope → $125 "set is under control already"

**Root cause:** The IR's expression representation doesn't preserve subset-filtered sum domains. When `sum(acol(col), ...)` is parsed, the domain restriction `acol` is either lost or not propagated through the KKT stationarity builder.

### Bug D: Undefined Parameter in Conditional `.fx` (1 error)

```gams
lam_laerr.fx(k)$(not (nfeas(k) = 0)) = 0;   ← $141: nfeas not assigned
```

**Root cause:** `nfeas(km)` is a parameter that is set dynamically during the Benders iteration loop (`nfeas(count) = 0` at line 475, `nfeas(count) = 1` at line 488). The MCP emitter references it in a `.fx` statement, but the parameter's values come from loop-body assignments that aren't emitted.

---

## Root Causes Summary

| Bug | Root Cause | Fix Complexity |
|-----|-----------|---------------|
| A | `.l` init elements not quoted | Low (1–2h) — apply existing quoting logic |
| B | Dynamic subset used as multiplier domain | Medium (2–3h) — use parent set + conditioning |
| C | Subset-filtered sum domains lost in IR | High (4–6h) — deep IR/expression change |
| D | Loop-body parameter not emitted | Medium (2–3h) — related to #952/#953 |

---

## Reproduction

```python
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
from src.emit.gams_emitter import emit_gams

m = parse_model_file('data/gamslib/raw/nonsharp.gms')
result = emit_gams(m)

with open('/tmp/nonsharp_mcp.gms', 'w') as f:
    f.write(result)

# /Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/nonsharp_mcp.gms lo=2
# → 37 compilation errors
```

Verify unquoted elements:
```bash
grep -n "cfin\.l.*,a)" /tmp/nonsharp_mcp.gms
# Lines 219-224: cfin.l("col-1",a) etc. — 'a', 'b', 'c' unquoted
```

---

## GAMS Source Context

### Dynamic subset definition (lines 84–87):
```gams
km        'static iterations'  / 1*150 /
kloop     'loop counter'       / 1*20  /
k(km)     'dynamic iterations' / 1     /
count(km) 'dynamic counter'    / 1     /;
```

### Conditional equations (lines 323, 330):
```gams
lagrange(k)$(nfeas(k) = 1)..
    c =g= ...
laerr(k)$(nfeas(k) = 0)..
    alp =g= ...
```

### Domain-restricted sum (lines 279–281):
```gams
lpobj.. c =e= sum(acol(col), (cost(col)*yp(col) +
    (a1(col) + sum(key(col,stm,cp), a2(col,stm)*rec(col,stm,cp))
    + sum(cp, a3(col,cp)*xin(col,cp)))*fin(col)));
```

### Dynamic parameter assignment in loop body (lines 475, 488):
```gams
nfeas(count) = 0;
...
nfeas(count) = 1;
```

---

## Related Issues

- #891: Original nonsharp tracking issue (parse error fixed via `abort.noerror` normalization)
- #952: lmp2 loop-body assignments not emitted (same class as Bug D)
- #953: paperco loop-body assignments not emitted (same class as Bug D)
- PR #951: Quoting fixes for assignment indices (same class as Bug A)

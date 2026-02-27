# trnspwl: ord() on dynamic set ($197) + unquoted element labels ($120/$149)

**GitHub Issue:** [#949](https://github.com/jeffreyhorn/nlp2mcp/issues/949)
**Model:** trnspwl (GAMSlib SEQ=385)
**Status:** OPEN
**Error category:** `gams_compilation_error`
**Severity:** Medium — model parses and translates but GAMS compilation fails (59 errors)

---

## Problem Summary

The trnspwl MCP output has two classes of GAMS compilation errors:

1. **`$197` — `ord()` on dynamic set `ss`**: The original GAMS uses `ss.off` where `ss(s)` is a subset (dynamic set). Our parser translates `.off` to `ord(ss) - 1`, but GAMS rejects `ord()` on non-constant (dynamic) sets.

2. **`$120/$149/$340` — Unquoted element labels in per-instance assignments**: The emitter generates `nseg(slope0) = ...` instead of `nseg("slope0") = ...`. GAMS interprets bare `slope0` as a set reference rather than a quoted element label.

---

## Error Details

### Error 1: $197 on line 49

```
  49  p(ss) = xlow + (xhigh - xlow) / (card(ss) - 1) * (ord(ss) - 1);
****                                                         $197
**** 197  Lag or 'ord' illegal with non constant set
```

**Original GAMS (line 145):**
```gams
p(ss) = xlow + (xhigh-xlow)/(card(ss)-1)*ss.off;
```

Here `ss(s)` is a dynamic subset: `Set ss(s) 'sample points' / s1*s6 /;`. The original uses `.off` which GAMS handles natively on dynamic sets. Our translation to `ord(ss) - 1` fails because `ord()` requires a static/ordered set.

### Error 2: $120/$149 on lines 51-57

```
  51  nseg(slope0) = p(s+1) - p(s);
****            $120,340,171,149 $149
```

The per-instance parameter assignments use unquoted element names (`slope0`, `s1`..`s6`). GAMS expects quoted labels: `nseg("slope0")`.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/trnspwl.gms -o /tmp/trnspwl_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/trnspwl_mcp.gms lo=2
grep '^\*\*\*\*' trnspwl_mcp.lst
```

---

## Root Cause

### Issue 1: ord() on dynamic set
The `.off` → `ord()-1` translation in `_expr()` is correct for static sets but not for dynamic subsets. GAMS `.off` is a native attribute that works on any set, while `ord()` is restricted to static/ordered sets.

**Fix options:**
- **Option A:** Emit `.off` directly instead of translating to `ord()-1`. This requires the emitter to recognize `Binary("-", Call("ord", ...), Const(1.0))` patterns and reconstruct `.off`, which is fragile.
- **Option B:** Keep the IR translation but detect when the set is dynamic and emit `ss.off` in the GAMS output instead. Requires set-type awareness in the emitter.
- **Option C:** Emit `(ord(ss) - 1)` only for static sets; for dynamic sets, store the original `.off` attribute in the IR and pass it through to the emitter.

### Issue 2: Unquoted element labels
The emitter's per-instance parameter assignment code generates bare identifiers where quoted strings are needed. This is a general emitter quoting issue.

**Fix:** In `emit_computed_parameter_assignments()` or similar, wrap singleton set element indices in quotes when they appear as literal labels.

---

## GAMS Source Context

```gams
Set
   s     'SOS2 elements' / slope0, s1*s6, slopeN /
   ss(s) 'sample points' /         s1*s6         /;

p(ss) = xlow + (xhigh-xlow)/(card(ss)-1)*ss.off;  $ line 145

nseg(g) = p(g+1) - p(g);  $ line 152 (original uses indexed set g)
```

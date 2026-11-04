# ISSUE #1797 — parser: a zero-padded numeric range (`01*24`) loses its padding (sarf `$170`)

**GitHub:** [#1797](https://github.com/jeffreyhorn/nlp2mcp/issues/1797) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 10 (2026-11-04), a sarf blocker behind #1795

**Layer:** parser, `_expand_range` (`src/ir/parser.py`)

## Summary

`_expand_range` (`src/ir/parser.py`) drops the zero padding of a **pure numeric** range: `Set t / 01*24 /` becomes `1, 2, …, 24`, while GAMS keeps `'01' … '24'`. The symbolic branch already preserves the width (#782: `a01*a24`); the numeric branch returns `str(i)`.

## Reproducer

```gams
Set t / 01*03 /;
Parameter d(t) / '02' 5 /;
Variable x(t), obj;
Equation defobj;
defobj.. obj =e= sum(t, sqr(x(t) - d(t)));
Model m / all /; solve m using nlp minimizing obj;
```

→ `ParserSemanticError: Parameter 'd' references member '02' not present in set 't'`. In **sarf** (`t 'time periods (in fortnights)' / 01*24 /`) the `Table` data is not validated at parse time, so the MCP emits `t /'1', …, '24'/` beside `btask(…,'04')` / `lreq(…,'07')` data and fails compile with **`$170` domain violations** (97 errors, then `$257`).

## Fix

Use the start bound's width when it has a leading zero, as the symbolic branch does (`f"{i:0{width}d}"`). Verified in a scratch worktree (Sprint 40 Day 10): sarf's MCP then compiles with 0 errors. A grep of `data/gamslib/raw/` finds **sarf only** using a zero-padded numeric range, so no committed golden should move (leak gate to confirm).

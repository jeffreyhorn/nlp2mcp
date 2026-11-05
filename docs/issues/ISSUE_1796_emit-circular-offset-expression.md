# ISSUE #1796 — emit: a circular lead/lag with an expression amount (`t++(expr)`) raises `NotImplementedError`

**GitHub:** [#1796](https://github.com/jeffreyhorn/nlp2mcp/issues/1796) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 10 (2026-11-04), a sarf blocker behind #1795

**Layer:** IR / emit, `IndexOffset.to_gams_string` (`src/ir/ast.py`)

## Summary

`IndexOffset.to_gams_string` (`src/ir/ast.py`) raises `NotImplementedError("Circular lead/lag with Binary offset not supported")` for a circular lead/lag whose amount is an expression, and likewise for a `Call`/`ParamRef` amount and the `Unary("-", …)` complex form. GAMS accepts these: `t++(expr)` / `t--(expr)`.

## Reproducer (sarf, line 365)

```gams
luse(c,t++(cs(c,"start",s)-1),s) = 1$(ord(t) <= length(c,s));
```

Once sarf gets past `assemble_kkt_system` (behind #1795), emit aborts:

```
Error: Unexpected error - Circular lead/lag with Binary offset not supported: Binary(-, ParamRef(cs(c,"start",s)), Const(1.0))
```

## Fix

Render the circular form instead of raising: `f"{base}++({offset})"` for a `Binary`, `f"{base}++{offset}"` for `Call`/`ParamRef`, and `f"{base}--(...)"` for the `Unary("-", …)` forms. Verified in a scratch worktree (Sprint 40 Day 10): with it (and the zero-padded-range fix), sarf's MCP compiles with **0 errors**. The linear (non-circular) branches are unchanged, so no other golden can move (needs the leak gate to confirm).

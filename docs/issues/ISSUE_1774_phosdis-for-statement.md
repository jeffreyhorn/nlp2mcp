# ISSUE #1774 — phosdis: grammar has no for(s = a to b, ...) statement (multi-solve inside the loop)

**GitHub:** [#1774](https://github.com/jeffreyhorn/nlp2mcp/issues/1774) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 4 (2026-10-20), routed, not fixed in place

**Route:** P3 parse (Sprint 40 P3 routing note) · **Model:** `phosdis` (NLP-gated, `verified_convex`, admitted by rule Sprint 40 Day 3) · **Measured at:** `de0a7186`

## Fingerprint (reproduced)

`parse: failure`, `lexer_invalid_char`:

```
Parse error at line 609, column 10: Unexpected character: '='
  for(iter = 1 to 7, count = 0; loop(ss$(count < 4), s(ss) = yes; count = count+1; ); ss(s) = no; solve …
```

The grammar has no **`for(<scalar> = <a> to <b>, …)`** statement. phosdis solves the model piecemeal inside it (`solveOpt = replace`).

## Fix surface, and a scope question first

- **Grammar:** a `for` statement (`for(s = a to|downto b [by c], body);`), parsed like `loop` and `while`.
- ⚠ **Scope first.** phosdis's single `solve` sits **inside** the `for`/`loop`, so the NLP objective is the last iteration's. That is the multi-solve **reference question** recorded on Sprint 40 Day 3 (`SPRINT_LOG.md`, P3). Parsing it does not settle which solve the MCP should reproduce. Do not book a phosdis comparison until it is settled.

**Reach in the corpus:** `for(` also appears in `kqkpsdp` (RMIQCP) and `maxcut` (MIP), both excluded.

**Not fixed in place.**

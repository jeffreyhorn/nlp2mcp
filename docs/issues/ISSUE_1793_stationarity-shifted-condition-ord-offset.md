# ISSUE #1793 — stationarity: the #1388 condition shift emits `ord(h+1)` inside a shifted `$` condition (illegal GAMS, `$8`)

**GitHub:** [#1793](https://github.com/jeffreyhorn/nlp2mcp/issues/1793) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 9 (2026-11-03), found while building a positive control for #1789, not fixed in place

**Measured at:** `main` `c410057d` · **Layer:** KKT / stationarity, `_reindex_condition_symbols` (called from `_add_indexed_jacobian_terms`, the #1388 offset cross-term guard)

## Summary

For an offset cross-term, the multiplier is the neighbouring instance (`nu_dyn(h+1)`), so #1388 rewrites the equation's `$` condition at that offset by mapping `SymbolRef(h)` → `IndexOffset(h, +1)`. The `Call` branch recurses into **`ord`'s argument** with the same map, producing `ord(h+1)`. GAMS does not accept a lead/lag inside `ord`, so the MCP fails to compile: `$8 ')' expected`, cascading to `$37`, `$408` and `$409`.

```gams
Set h / h1*h5 /;
Parameter tgt(h);  tgt(h) = ord(h);
Variable x(h), obj;
Equation dyn(h), defobj;
dyn(h)$(ord(h) > 1).. x(h) =e= 0.5*x(h-1) + 1;
defobj.. obj =e= sum(h, sqr(x(h) - tgt(h)));
Model m / all /;  solve m using nlp minimizing obj;
```

NLP 14.9267. Emitted:

```
stat_x(h).. 2 * (x(h) - tgt(h)) + (((-0.5) * nu_dyn(h+1))$(ord(h) <= card(h) - 1))$(ord(h+1) > 1) + nu_dyn(h)$(ord(h) > 1) =E= 0;
```

## Expected

For a non-circular offset, `ord(h+k)` becomes `ord(h) + k`. The neighbour's existence is already guarded by the enclosing `$(ord(h) <= card(h) - 1)`. So the guard should read `$(ord(h) + 1 > 1)`. A circular offset needs the wrapped form. Parameter and set-membership references in the condition keep their `IndexOffset`; those are legal.

## Corpus

**dinam.** Its committed golden carries `$(ord(te+1) > last)` in `stat_v` and `stat_x` (lines 472–473), and a compile shows `$8`/`$37`/`$408`/`$409` there. That is **in addition to** the `$140`/`$148`/`$149`/`$171` recorded on #926: one more dinam blocker, not the whole story. No other committed golden contains `ord(<index>±k)`.

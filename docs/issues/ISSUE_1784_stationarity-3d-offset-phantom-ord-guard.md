# ISSUE #1784 — stationarity: a lead/lag reference inside a sum over a 3-D variable's middle index gets phantom `$(ord(k) = n)` guards — MCP does not solve

**GitHub:** [#1784](https://github.com/jeffreyhorn/nlp2mcp/issues/1784) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 7 (2026-10-26), found while promoting the P8 pins, not fixed in place (P8 is tests only)

**Measured at:** `main` `500ffa1f` · **Layer:** stationarity assembly (KKT), not traced yet

## Summary

A 3-D variable referenced with a lead/lag (or circular) offset inside a `sum` over its middle index gets a stationarity row with **phantom `$(ord(k) = n)` guards**: the sum binder `k` is mistaken for an offset-carrying coordinate. The MCP does not solve. Without the offset the same model is correct.

Found while promoting the P8 structural pins (Sprint 40 Day 7). This is Prep Task 10's `oik3` fixture (`CORRECTNESS_PRETRACES.md` §5); §5 recorded only its multiplier offsets (`lam_e(i-1,ip+1)`), not these guards.

## Reproducers

```gams
* (a) lead/lag, NLP 4.5
Set i / a, b, c, d /, k / k1, k2 /;
Alias (i,ip);
Variable x(i,k,ip), obj;
Equation e(i,ip), defobj;
e(i,ip)$(ord(i) < card(i) and ord(ip) > 1).. sum(k, x(i+1,k,ip-1)) =l= 1;
defobj.. obj =e= sum((i,k,ip), sqr(x(i,k,ip) - 1));
Model m / all /; solve m using nlp minimizing obj;
```

Emitted (abridged):

```
stat_x(i,k,ip).. 2 * (x(i,k,ip) - 1) + (((lam_e(i-1,ip+1)$(ord(i) > 1 and ord(ip) <= card(ip) - 1))$(ord(k) = 1))$(ord(i) < card(i) and ord(ip) > 1))$(...) =E= 0;
```

- `$(ord(k) = 1)` drops every `k2` instance; the correct term holds for every `k`.
- The equation's own condition is evaluated at the VARIABLE's indices `(i,ip)` instead of the shifted multiplier's `(i-1,ip+1)`.
- The MCP aborts: `MCP pair comp_e.lam_e has unmatched equation` (×5).

```gams
* (b) circular, NLP 8.0: e(i,ip).. sum(k, x(i++1,k,ip--1)) =l= 1;
```

This emits `lam_e(i+3,ip+1)$(...)$(ord(k) = 3)` and similar terms. It mixes the offsets with `k` and does not solve.

```gams
* (c) positive control, NLP 8.0: e(i,ip).. sum(k, x(i,k,ip)) =l= 1;
```

This emits `stat_x(i,k,ip).. 2*(x(i,k,ip) - 1) + lam_e(i,ip) =E= 0;` and solves to 8.0.

## Shape

The `ord(k) = n` beside an offset multiplier is the phantom-IndexOffset family's fingerprint (#1381; silent members #1714). The offset groups are built per `k` instance, and `k`, an unmatched (`999`) position, picks up an `ord(k)` guard from the grouping.

## First step

Trace `_add_indexed_jacobian_terms`'s offset groups for `(e, x)`. Check where the `ord(k) = n` guard is formed for the sentinel position (the `#1038` sum-index-binding consolidation is the first candidate).

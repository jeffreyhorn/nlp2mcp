# ISSUE #1773 — indus89: grammar has no Singleton Set declaration

**GitHub:** [#1773](https://github.com/jeffreyhorn/nlp2mcp/issues/1773) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 4 (2026-10-20), routed, not fixed in place

**Route:** P3 parse (Sprint 40 P3 routing note) · **Model:** `indus89` (NLP-gated, `verified_convex`, admitted by rule Sprint 40 Day 3) · **Measured at:** `de0a7186`

## Fingerprint (reproduced)

`parse: failure`, `lexer_invalid_char`:

```
Parse error at line 128, column 11: Unexpected character: 'S'
  Singleton Set
            ^
```

The grammar has no **`Singleton Set`** declaration. `indus89` declares:

```gams
Singleton Set
*  change the set isr to setup data for desired year.
   isr(is)     'irrigation system scenario for this run' / 1988 /;
```

It appears twice in the file (lines 128 and 3056).

## Fix surface

`src/gams/gams_grammar.lark`: accept `Singleton Set[s]` as a set declaration. Record the singleton flag in `SetDef`. A singleton holds at most one element, and GAMS lets it be used where a scalar element is expected; the IR needs that only if a reference depends on it. Run `make test` after the grammar change.

**Reach in the corpus:** `Singleton Set` also appears in `guss2dim` and `spbenders4`. Neither is a convex candidate today.

**Not fixed in place.**

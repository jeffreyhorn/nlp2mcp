# ISSUE #1792 — emit: a parameter used only in an equation's `$` condition loses its assignment (`$141`)

**GitHub:** [#1792](https://github.com/jeffreyhorn/nlp2mcp/issues/1792) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 8 (2026-11-03), found during the PR #1791 assessment, not fixed in place

**Measured at:** `main` `e5915ad2` (identical) · **Layer:** emit (parameter-relevance filter), not traced yet

## Summary

A parameter whose ONLY use in the model is inside an **equation's `$` condition** loses its assignment in the emitted MCP. GAMS then fails to compile with `$141` (symbol declared, no values assigned). Identical on `main`.

```gams
Set r / r1*r4 /;
Parameter w(r);
w(r) = ord(r);
Variable x(r), obj;
Equation e(r), defobj;
e(r)$(w(r-1) >= 1).. x(r) =g= 1;
defobj.. obj =e= sum(r, sqr(x(r)));
Model m / all /;  solve m using nlp minimizing obj;
```

The emitted MCP declares `w(r)` but omits `w(r) = ord(r);`, so every reference to `w` in the multiplier `.fx` lines and the guarded rows is `$141`. With literal data (`Parameter w(r) / r1 1, … /`) the same model translates and solves.

Seen twice in Sprint 40:
- PR #1788 round 2: `a(t) = ord(t)/4;` used only in `pr(t)$(sum(w, a(w)) >= 1)`;
- PR #1791: `w(r) = ord(r);` used only in `fodb(r,c)$(w(r-1) >= 1)`.

## First step

The parameter-relevance filter (`model_relevant_params`, which `emit_original_parameters` uses) likely collects references from equation BODIES only. Include equation conditions.

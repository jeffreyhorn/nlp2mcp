# ISSUE #1781 — emit: a parameter-data label spelled like an alias is emitted unquoted (`p(j) = 1;`), $171

**GitHub:** [#1781](https://github.com/jeffreyhorn/nlp2mcp/issues/1781) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 5 (2026-10-25), PR #1779 review round 14, not fixed in place

**Found by:** Sprint 40 Day 5, PR #1779 review round 14 · **Layer:** emit, parameter-data section · **Pre-existing:** identical on `main`

## Reproducer

```gams
Set i / i1, i2 /;  Alias (i,j);
Set lab / j /;
Parameter p(lab) / j 1 /;
...
```

The emitted data line is **`p(j) = 1;`**, with the label `j` unquoted. GAMS reads `j` as the **alias** `j`, not the element `'j'` of `lab`, and fails to compile: **`$171 Domain violation for set`**, then `$257`/`$141`. The whole MCP never solves.

## Fix direction

Quote element labels in emitted parameter (and set) data whenever the label collides with a set, alias or other identifier name. The safe form is to quote every label: `p('j') = 1;`.

## Scope

Latent in the corpus as far as measured: the PR #1779 leak gate is byte-identical, so no committed golden has hit it. It needs a label spelled exactly like a set or alias name.

**Not fixed in place.**

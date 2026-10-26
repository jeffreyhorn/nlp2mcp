# ISSUE #1785 — objective gradient: an aliased 2-D variable's `ord()` terms are re-symbolised onto the other index — silent wrong answer (MCP 19 vs NLP 0)

**GitHub:** [#1785](https://github.com/jeffreyhorn/nlp2mcp/issues/1785) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 7 (2026-10-26), found while building egypt's Class-A fixture (P4), not fixed in place

**Measured at:** `main` `500ffa1f` (byte-identical on an untouched `main` worktree) · **Layer:** objective gradient re-symbolisation, not traced yet

## Summary

**A silent wrong answer on a 7-line model.** The objective gradient of an aliased 2-D variable re-symbolises `ord()` of one index as the OTHER index's `ord()` for part of the instances. The MCP solves (MS 1) to **19.0; the NLP optimum is 0.0**.

```gams
Set r / r1*r3 /;
Alias (r,rp);
Variable x(r,rp), obj;
Equation defobj;
defobj.. obj =e= sum((r,rp), (1 + ord(r))*sqr(x(r,rp) - ord(rp)));
Model m / all /;
solve m using nlp minimizing obj;
```

Emitted (identical on `main` at `500ffa1f`):

```
stat_x(r,rp).. (((1 + ord(r)) * 2 * (x(r,rp) - ord(r)))$(sameas(r, 'r1') and sameas(rp, 'r1'))
  + ((1 + ord(r)) * 2 * (x(r,rp) - ord(rp)))$(sameas(r, 'r1') and (sameas(rp, 'r2') or sameas(rp, 'r3')))
  + ((1 + ord(rp)) * 2 * (x(r,rp) - ord(r)))$((sameas(r, 'r2') or sameas(r, 'r3')) and sameas(rp, 'r1'))
  + ((1 + ord(rp)) * 2 * (x(r,rp) - ord(rp)))$(...) ...
```

The correct row is `(1 + ord(r)) * 2 * (x(r,rp) - ord(rp))` for every instance.

## Shape

The gradient is grouped per instance class, and each group's representative concrete derivative is mapped back to symbols. A label shared by the two aliased positions (`r1` is both `r` and `rp` at `(r1,r1)`; at `(r2,r1)`, `ord('r1')` belongs to `rp` but the map sends it to `r`) goes to the wrong coordinate. It is the same concrete→symbolic mapping over aliased positions as #1778, but in the **objective-gradient** path rather than the constraint-Jacobian one.

Found while building egypt's Class-A fixture (Sprint 40 Day 7, P4).

## First step

Find where the objective gradient's per-instance groups are formed and re-symbolised for an aliased multi-index variable. A representative with distinct labels per position, or position-aware mapping, is the likely remedy. Then grep the goldens for `ord(<alias>)` inside `stat_*` rows of aliased variables, to scope corpus impact.

## A second reproducer: `ord()` of a SUBSET re-symbolised as the parent's `ord()`

Found the same day, while building shale's `acap` fixture. Also a silent wrong answer, and also identical on `main` at `500ffa1f`:

```gams
Set tf / f1*f4 /, t(tf) / f2*f4 /;
Variable p(tf), obj;
Equation defobj;
defobj.. obj =e= sum(t, ord(t)*sqr(p(t) - 3)) + sum(tf, sqr(p(tf)));
Model m / all /;
solve m using nlp minimizing obj;
```

Emitted: `stat_p(tf).. ((2 * p(tf))$(sameas(tf, 'f1')) + (2 * ord(tf) * (p(tf) - 3) + 2 * p(tf))$(t(tf)))$(…) =E= 0;`. The MCP gives **18.027**; the NLP gives **17.25**.

`ord(t)` counts within the subset `t` (1 at `f2`), while `ord(tf)` counts within `tf` (2 at `f2`). Re-symbolising the concrete `ord('f2')` onto the row's index `tf` shifts it by one. It is the same concrete→symbolic `ord()` mapping as above, over a subset rather than an alias.

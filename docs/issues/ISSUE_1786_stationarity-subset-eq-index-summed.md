# ISSUE #1786 — stationarity: a subset-defined equation sums over its bound subset index when another eq index has no variable counterpart — silent wrong answer (shale `stat_z`)

**GitHub:** [#1786](https://github.com/jeffreyhorn/nlp2mcp/issues/1786) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 7 (2026-10-26), found while building shale's Class-A fixture (P4); routed as shale's candidate underlying defect, not fixed in place

**Measured at:** `main` `500ffa1f` (byte-identical on an untouched `main` worktree) · **Layer:** stationarity assembly (KKT), not traced yet

## Summary

**A silent wrong answer on a 10-line model, and a candidate for shale's "defect underneath"** (Prep Task 10 §2: restoring shale's `cpu` coupling was necessary but not sufficient).

An equation defined over a SUBSET (`e(c,t)` with `t(tf)`) contributes to a variable declared over the PARENT (`z(p,tf)`). When another equation index (`c`) has no counterpart in the variable, the stationarity row SUMS over the subset index `t`, though `t` is bound by the reference `z(p,t)` and must map to the row's `tf`.

```gams
Set tf / 1*3 /, t(tf) / 1*2 /, p / p1*p2 /, c / c1*c2 /;
Parameter a(c,p);
a(c,p) = ord(c) + ord(p);
Positive Variable z(p,tf);
Variable obj;
Equation e(c,tf), defobj;
e(c,t).. sum(p, a(c,p)*z(p,t)) =g= 4;
defobj.. obj =e= sum((p,tf), ord(tf)*sqr(z(p,tf)));
Model mm / all /;
solve mm using nlp minimizing obj;
```

Emitted (identical on `main` at `500ffa1f`):

```
stat_z(p,tf).. 2 * ord(tf) * z(p,tf) + sum((c,t), (((-1) * a(c,p)) * lam_e(c,t))$(t(t))) - piL_z(p,tf) =E= 0;
```

The MCP solves (MS 1) to **9.026; the NLP optimum is 3.692**. The correct term is `sum(c, -a(c,p) * lam_e(c,tf))$(t(tf))`.

The 1-D variant `e(m,t).. c(m,t)*z(t) =g= 4` with `z(tf)` (more equation dims than variable dims) is wrong the same way: `sum((m,t), -c(m,t)*lam_e(m,t))$(t(t))`, MCP 13.04 vs NLP 7.56.

## In the corpus: shale

`stat_z(p,tf)` (golden L357) has this shape on every subset-defined balance: `sum((crs,t), (a(crs,p) * nu_msu(crs,t))$(crs(crs) and t(t)))`, and likewise `nu_mrw`, `nu_mi`, `nu_mf`. Each sums over `t` instead of binding it to `tf`.

## Shape

- **Equal arity** (`e(c,t)` against `z(p,tf)`): the positional match fails at position 0 (`c` vs `p`), so `_match_subset_domain` finds no full match. Both equation indices are then treated as free and summed.
- **More equation dims than variable dims:** `_compute_index_offset_key` returns zeros, and nothing binds `t`.

In both cases the binding of `t` is visible in the reference `z(p,t)`. #1782's `_eq_index_ref_binding` already reads it, but the binding is consulted only in the `len(eq) < len(var)` path.

Found Sprint 40 Day 7 (P4), while building shale's Class-A fixture.

## First step

Check the corpus scope: grep the goldens for `sum((…,<subset>), …)$(<subset>(<subset>))` in `stat_*` rows whose domain holds the subset's parent. Then trace `_add_indexed_jacobian_terms` for `(e, z)` above, and make the equal-arity / more-eq-dims paths bind an index that every reference holds at one position.

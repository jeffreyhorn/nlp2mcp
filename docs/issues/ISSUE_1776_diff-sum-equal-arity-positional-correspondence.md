# ISSUE #1776 — AD: _diff_sum takes equal binder/index counts as positional correspondence — derivative 0, constraint dropped (egypt landb/labbal/waterb)

**GitHub:** [#1776](https://github.com/jeffreyhorn/nlp2mcp/issues/1776) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 4 (2026-10-20), routed, not fixed in place

**Layer (traced, not assumed):** AD, `src/ad/derivative_rules.py::_diff_sum`, the length gates at ~L2348 (`len(wrt_indices) > len(expr.index_sets)`, partial index match) and ~L2461 (`<`, partial collapse) · **Found by:** Sprint 40 Day 4 routing (R-PRE-140, #1766) · **Measured at:** `de0a7186` · **Sibling of:** #1755 (same outcome, a different gate)

## Minimal reproducer

```gams
Set r /r1*r2/, c /c1*c2/, z /z1*z2/, tm /t1*t2/;
Set zr(z,r) / z1.r1, z2.r2 /;
Parameter land(c,z,tm);
land(c,z,tm) = 1;
Positive Variable xcrop(r,c);
Variable obj;
Equation landb(r,tm), defobj;
landb(r,tm).. sum((c,z)$zr(z,r), xcrop(r,c)*land(c,z,tm)) =l= 10;
defobj.. obj =e= sum((r,c), xcrop(r,c));
Model m / all /;
solve m using lp maximizing obj;
```

The emit drops **`landb` and `lam_landb` entirely**, and `stat_xcrop(r,c).. -1 - piL_xcrop(r,c) =E= 0` loses the constraint term. That is wrong: `landb` binds for this LP.

| variant | `lam_landb` kept? |
|---|---|
| `sum((c,z)$zr(z,r), …)` (two binders) | **no** |
| `sum((c,z), …)` (two binders, no condition) | **no** |
| `sum((z,c)$zr(z,r), …)` (binder order swapped) | **no** |
| `sum(c, … land(c,'z1',tm))` (one binder) | yes |
| `sum(c$zr('z1',r), …)` (one binder, conditioned) | yes |

## Mechanism (instrumented)

- `_sum_should_collapse(('c','z'), ('r1','c1'))` returns **False** in the failing case. ⚠ It also returns False for the working one-binder case, so **the collapse decision is not the divergence.**
- In the one-binder case, `len(wrt)=2 > len(binders)=1` enters the **partial-index-match** branch (~L2348). It differentiates against a partly symbolic `('r1','c')`, and `_diff_varref(xcrop(r1,c))` gives **1.0**.
- In the two-binder case, `len(wrt)=2 == len(binders)=2`, so **neither** the `>` branch nor the `<` partial-collapse branch (~L2461) runs. The only path left treats the binders as if they corresponded to the variable's positions. Every attempt is against a concrete `('r1','c1')`, and `_diff_varref(xcrop(r1,c))` gives **0**. The row's derivatives are all 0, and the row and its multiplier vanish downstream.
- **The defect: equal counts are taken to mean positional correspondence.** Here binder `c` sits at position 2 of `xcrop(r,c)`, binder `z` appears nowhere in `xcrop`, and position 1 is the equation index `r`.

## In the corpus: egypt

- `landb(r,tm)` gets 0 Jacobian entries (60 rows) and `waterb` gets 0 (1 row), and both vanish from `egypt_mcp.gms`.
- **`labbal` silently loses its `xcrop` terms:** the committed `stat_xcrop(r,c)` carries only `lam_comb` and `lam_vegetb`. `labbal` survives only because its RHS has the variables `tlab` and `flab`.
- This is one cause of egypt's cold `model_infeasible`, **alongside** the Class-A `tranc(rp,rp)` that P4 owns. It also causes the presolve `$140` (#1766).

## Fix direction

Decide correspondence **by the variable's index positions**, not by binder count. For each binder, find the position(s) of the reference where it appears. A binder at no position (`z` here) stays a sum dimension. A position holding a non-binder (`r` here) must already match the concrete `wrt` value. This is the same binder→position map #1755 needs, so one helper may serve both.

**Scope check before fixing:** grep the goldens for constraints whose multiplier is absent while the source equation is in the solved model. "Absent multiplier" is the loud form; a dropped term in a surviving row (`labbal`) is the silent one.

**Not fixed in place.** P7 (#1755) is the natural owner: it is the same function and the same helper, and a Phase-0 gate is required.

# ISSUE #1795 — stationarity: a non-Cartesian multiplier guard is emitted as an OR of `sameas` tuples (sarf `stat_task`, 51,792 tuples)

**GitHub:** [#1795](https://github.com/jeffreyhorn/nlp2mcp/issues/1795) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 10 (2026-11-04); the re-scoped E5 of `SARF_JACOBIAN_DESIGN.md` (P6, C7 UNMET)

**Measured at:** `main` `1abcd687` · **Layer:** KKT / stationarity, `_build_sameas_guard` → `_build_tuple_or_guard`

## Summary

sarf's `stat_task` carries a **non-Cartesian** multiplier guard built as an OR of `sameas` conjunctions over every entry tuple (`_build_sameas_guard` → `_build_tuple_or_guard`, `src/kkt/stationarity.py`). For `lam_labor` that is **51,792 tuples** of 4 `sameas` each, built as a left-deep `Binary("or", …)` chain. It breaks sarf twice:

1. **Python:** `apply_simplification` on `stat_task` recurses down the chain and hits `RecursionError` (limit 50,000) inside `assemble_kkt_system` — the E5 item of `SARF_JACOBIAN_DESIGN.md`. Measured Sprint 40 Day 10: stack = 49,993 × `simplify` (`ad_core.py:171`, the `Binary` left child), entered from `build_stationarity_equations` → `apply_simplification`; the term's deepest path is **51,791 `or`** + 3 `and`.
2. **GAMS:** with the chain built as a balanced tree instead (depth ≈ 16; scratch experiment), translation completes and the MCP compiles, but GAMS **model generation** did not finish in 37 min (`gamscmex.out` at 100 % CPU, no solver started): the emitted file carries **207,218 `sameas` calls**, and the guard is evaluated for each of `stat_task`'s 369,024 instances.

The guard's **semantics are correct** (#1381 follow-up: a per-dimension AND would over-select). Its **shape** is the defect.

## Proposed fix (shape, not `simplify`)

Emit a non-Cartesian entry set as a **declared set** and guard with a membership test, e.g.

```gams
Set nz_labor_task(g,t,mn,mn) / ... the 51,792 tuples ... /;
stat_task(g,t,mn,mn__).. ... $nz_labor_task(g,t,mn,mn__) ...
```

Generation then costs one membership lookup per instance. A threshold (e.g. > 64 tuples) keeps every current golden byte-identical (the largest tuple-OR in the committed goldens is far smaller — to be measured). ⚠ The fix touches `stationarity.py`, which holds #1741's guard (`_build_pattern_c_dim_mismatch_term`): guard-impact review required.

⚠ **Repeated domain: the DECLARATION may repeat `mn`, the REFERENCE must not.** A repeated symbol in a set's declared domain is safe. A repeated symbol in a *membership test* binds both positions to the same element, so `$nz_labor_task(g,t,mn,mn)` would test **only the diagonal** and change the guard's semantics for every off-diagonal `task` instance. The test must use the stationarity head's **distinct** controlling indices, `(g,t,mn,mn__)`, as emitted for sarf today. This is the same rule `tests/integration/emit/test_tricp_repeated_domain_head.py` pins (the head `stat_slp(n,n__)` and the guard `$(e(n,n__))`, never `$(e(n,n))`), and P2 of `make check-index-repeats` would flag the diagonal form as a guard referencing a repeated index.

## Context

Sprint 40 Day 10 (P6, C7): E5/E6 started and is re-scoped here, so **C7 is reported UNMET** (Translate 135 flat). Two further sarf blockers sit behind this one and are filed separately (circular lead/lag with an expression amount; zero-padded numeric ranges).

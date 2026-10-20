# ISSUE #1780 — AD: `_diff_sum`'s single-binder loop returns its first non-zero attempt, so mixed layouts under-count

**GitHub:** [#1780](https://github.com/jeffreyhorn/nlp2mcp/issues/1780) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 5 (2026-10-20), PR #1779 review follow-up, not fixed in place

**Found by:** PR #1779 review follow-up (Sprint 40 Day 5, #1755) · **Layer:** AD, `src/ad/derivative_rules.py::_diff_sum`, the single-binder partial-match loop (#1086) · **Pre-existing:** the same result on `main` before #1755

## Reproducer (AD level)

`i = {i1, i2, i3}`; `d/dx('i1','i1')` of `sum(i, x(i,'i1') + x(i,i))`:

| | value |
|---|---|
| correct | **2**: `x(i,'i1')` at `i = i1`, plus `x(i,i)` at `i = i1` |
| `main`, and after #1755 | **1** |

## Mechanism

- The #1086 loop tries each candidate position and **returns the first non-zero** derivative. That was designed for an alias ambiguity: `sum(np, t(np,n))` against `t('three','four')`, where exactly one position is the right one.
- Here the position-0 attempt `('i','i1')` is non-zero, because of `x(i,'i1')`, so the loop returns **before** any other layout is tried. The diagonal `x(i,i)` is never counted.
- #1755's `_diff_sum_repeated_binder` runs only after every loop attempt is zero, so it does not see this case either.
- PR #1779 made that helper sum **all** repeated-binder layouts plus the summed remainder. This is the same principle, applied to the pre-existing loop.

## Why it is not fixed in #1779

Changing the loop from "first non-zero" to "sum of all distinct layouts" changes a path every single-binder sum takes. It needs its own Phase-0 gate, and the leak gate, to show the #1086 alias case is not double-counted, because there the attempts are alternatives, not addends.

## First step

Enumerate the corpus goldens whose stationarity rows come from this loop with **more than one** non-zero attempt, by instrumenting `_diff_sum` during `make check-goldens`. Zero means the change is safe to make byte-identically. Any other count means each is a candidate instance.

**Not fixed in place.**

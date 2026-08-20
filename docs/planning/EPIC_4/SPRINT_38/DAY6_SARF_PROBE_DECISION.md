# Sprint 38 Day 6 — P2 sarf: counter-only probe → **PROCEED**

**Date:** 2026-08-20 · **Branch:** `planning/sprint38-day6-sarf-impl2` · **Measured at:** `dfc2ae6d` · **Toolchain:** GAMS **54.2.1** · **Scope:** measurement only. **`src/` was probed and reverted** — byte-identical (`c7e1d14142048ffecdfa59b601dd49f9`; verify with §6's portable checksum).

**Verdict: ✅ PROCEED. The per-row referenced-column count drops from 369,024 to 24–136 on most rows, measured on real instantiated expressions.** Total **259,728** differentiations ≈ **78 s** — inside the owner's ≤300 s gate, and **1.8× better than the design's O(active)** while needing **none** of the machinery Day 5 found missing.

**⚠ Day 5's headline projection was WRONG and is corrected here: 4,532 (~1.4 s) → 259,728 (~78 s).** The reason is stated in §2; it does not change the decision.

---

## 1. The restated trigger, and why the plan's original could not fire

The plan's Day-6 trigger reads *"S1+S2 do not agree on the active column set"*. **Day 5 established that the active column set cannot be formed at all** — `resolve_set_members('taskposs')` falls back to the parent set, at the wrong arity — so the trigger could never fire either way.

**Restated (Day 5 §6):** *insert the instance collector as a counter only, and if the per-row referenced-column count does not drop from 369,024 to a small number by end of Day 6, take the exit.*

That is what was run.

## 2. Correcting Day 5 — only `tbal`'s condition is `tech`

Day 5 claimed the surviving columns are *"exactly the `(m,n)` for which `tech(g,m,n)` is nonzero"*, projecting **4,532 ≈ 1.4 s**. **Inspecting the actual ASTs shows that is true of one equation out of six:**

| equation | Sum indices | Sum **condition** | `task` reference |
|---|---|---|---|
| `tbal(g,t)` | `(m,n)` | **`tech(g,m,n)`** ← statically resolvable | `task(g,t,m,n)` |
| `equipb1(m,t)` | `(g,n)` | `taskposs(g,t)` ← **not** resolvable | `task(g,t,m,n)` |
| `equipb2(n,t)` | `(g,m)` | `taskposs(g,t)` | `task(g,t,m,n)` |
| `labor(t)` | `(g,m,n)` | `taskposs(g,t)` | `task(g,t,m,n)` |
| `cbal(c)` | `(t)` | `taskposs("harvest-c",t)` | fully **concrete** |
| `acost3` | `(g,t,m,n)` | `taskposs(g,t)` | `task(g,t,m,n)` |

In the other five, `tech` appears as a **multiplicative coefficient**, not a condition. So a `tech`-based filter is a *value* argument (a zero coefficient ⇒ a zero derivative), not the *structural* one Day 5 asserted. **The 4,532 figure assumed the structural reading and is withdrawn.**

## 3. What actually works — and it needs no condition evaluation at all

**The binding of a `VarRef`'s indices already bounds the referenced columns**, before any condition is consulted:

- an index in the **row's own domain** is fixed by the row ⇒ **1** value
- an index bound by an enclosing **`Sum`** ranges over that set ⇒ `card(set)`
- a **quoted literal** ⇒ **1**

Applied to `task(g,t,m,n)` per equation:

| equation | rows | referenced/row | binding | total |
|---|---|---|---|---|
| `tbal` | 384 | **136** | `g:row t:row m:27 n:5` + 1 concrete | 52,224 |
| `equipb1` | 648 | **80** | `g:16 t:row m:row n:5` | 51,840 |
| `equipb2` | 120 | **432** | `g:16 t:row m:27 n:row` | 51,840 |
| `labor` | 24 | **2,160** | `g:16 t:row m:27 n:5` | 51,840 |
| `cbal` | 6 | **24** | all concrete, `t:24` | 144 |
| `acost3` | 1 | **51,840** | `g:16 t:24 m:27 n:5` | 51,840 |
| | **1,183** | | | **259,728** |

**No `taskposs`. No `tech`. No evaluator.** Only the AST's own index binding — which is present at the hot loop today.

| approach | differentiations | at 3,343/s | needs |
|---|---|---|---|
| current | 436,555,392 | ~36.3 h | — |
| design's O(active) | 470,834 | ~141 s | a `taskposs` evaluator (**does not exist**) |
| **structural bound** | **259,728** | **~78 s** | **nothing that is missing** |

## 4. Measured, not projected — the counter-only probe

A read-only counter at the hot loop (`constraint_jacobian.py`, immediately before the per-instance loop), printing declared vs referenced and then `continue`-ing so no differentiation runs. **`D6_PROBE`-gated; `src/` reverted afterwards and verified byte-identical.**

First `task` row reached:

```
D6PROBE eq=cbal var=task declared=369024 referenced=24 ratio=15376.0x
D6PROBE eq=cbal var=sales declared=6 referenced=1 ratio=6.0x
```

Sweeping every row (815 `(row, var)` pairs; 391 of them `task`) before the run was capped:

| equation | rows measured | referenced/row | projected | |
|---|---|---|---|---|
| `acost3` | 1 | **51,840** | 51,840 | ✅ MATCH |
| `cbal` | 6 | **24** | 24 | ✅ MATCH |
| `tbal` | 384 | **136** | 136 | ✅ MATCH |

**Every equation reached matches its static projection exactly**, on *instantiated* expressions rather than declarations. Over those three: **144,288,384 declared vs 104,208 referenced — 1,385×**. `equipb1`/`equipb2`/`labor` were not reached before the cap; at their projected 155,520 the total is **259,728**.

**Honest scope of the measurement:** three of six equations were confirmed directly; the other three are projected by the same rule that predicted these three exactly. The implementation must confirm them.

## 5. Decision — PROCEED, and what Day 7 implements

**PROCEED.** The trigger's condition is met decisively: per-row referenced columns fall from 369,024 to **24–2,160 on five of six equations**, and the total lands **inside the ≤300 s gate** using only machinery that already exists.

**The change is NOT the design's S1/S2/S3.** It is a single, narrower edit:

> At the `constraint_jacobian.py` hot loop, iterate the variable's **referenced** instances — derived from the constraint expression's index binding — instead of every **declared** instance.

**Blast radius is corpus-wide and that is the whole risk.** This changes which columns receive derivatives for *every* model, so:

- **A column that is referenced but missed ⇒ a silently dropped derivative.** The collector must be a **superset** of what the current loop would produce non-zero results for; the safe form treats an unrecognised index as *free* (full cardinality) rather than as a literal.
- **The full-corpus leak gate is mandatory and must show ZERO drift** across the in-scope goldens. Any drift means a derivative changed, which for every model except sarf would be a defect.
- `acost3` still costs 51,840 (all four indices free) — **80 % of the remaining total sits in one scalar row.** A later refinement could use `tech`'s static zero-support there, but it is **not needed for the gate** and should not be bundled.

**Atomicity still holds**, and is now simpler: the collector plus the loop change land together, or not at all.

**REPLAN exit for Day 7 (restated):** if the full-corpus gate shows drift on any model other than sarf, revert — **do not narrow the collector to chase the gate**, because a collector narrowed to fit is exactly how a dropped derivative gets laundered into the goldens.

## 6. Reproduction

```bash
# §3 — the structural bound, from the IR alone (no conditions evaluated).
#   Self-contained: paste and run from the repo root. Prints 259,728.
.venv/bin/python - <<'EOF'
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
from src.ir.ast import VarRef, Sum
ir = parse_model_file('data/gamslib/raw/sarf.gms')
card = {k: len(v.members) for k, v in ir.sets.items() if getattr(v, 'members', None)}

def children(e):
    for a in getattr(e, '__dict__', {}).values():
        if hasattr(a, '__dict__'):
            yield a
        elif isinstance(a, tuple):
            for x in a:
                if hasattr(x, '__dict__'):
                    yield x

# Iterative DFS carrying the Sum indices in scope. Nested recursive walks are
# O(n^2) on these expressions and will appear to hang.
def task_refs(root):
    out, stack = [], [(root, frozenset())]
    while stack:
        node, binders = stack.pop()
        if isinstance(node, Sum):
            binders = binders | frozenset(node.index_sets)
        if isinstance(node, VarRef) and node.name == 'task':
            out.append((node.indices, binders))
        for c in children(node):
            stack.append((c, binders))
    return out

rows_total = diffs_total = 0
for n in ('tbal', 'equipb1', 'equipb2', 'labor', 'cbal', 'acost3'):
    e = ir.equations[n]
    rowdom = set(e.domain)
    rows = 1
    for d in e.domain:
        rows *= card.get(d, 1)
    cols = 0
    for side in e.lhs_rhs:
        for idxs, binders in task_refs(side):
            c = 1
            for ix in idxs:
                sym = ix if isinstance(ix, str) else getattr(ix, 'base', str(ix))
                # quoted literal or fixed by the row -> 1; otherwise full cardinality
                m = 1 if (sym.startswith('"') or sym in rowdom) else card.get(sym, 1)
                c *= m
            cols += c
    rows_total += rows
    diffs_total += rows * cols
    print(f"{n:10s} rows={rows:<6d} referenced/row={cols:<7d} total={rows*cols:,}")
print(f"TOTAL rows={rows_total} diffs={diffs_total:,}  (~{diffs_total/3343:.0f} s at 3,343/s)")
EOF

# §4 — the counter-only probe. Insert immediately before
#   `for var_indices in var_instances:` in constraint_jacobian.py, gated on
#   D6_PROBE, printing declared/referenced then `continue`. REVERT AFTERWARDS.
cd /tmp/d6run
D6_PROBE=1 .venv/bin/python -m src.cli data/gamslib/raw/sarf.gms -o sarf_mcp.gms 2>probe.log
grep D6PROBE probe.log

# revert + verify — portable, and NORMALISED to a bare hash.
#   md5sum (Linux) prints "<hash>  <file>"; md5 -q (macOS) prints "<hash>".
#   The awk strips the filename so the output matches the value quoted below
#   on both platforms.
git checkout -- src/ad/constraint_jacobian.py
{ md5sum src/ad/constraint_jacobian.py 2>/dev/null \
  || md5 -q src/ad/constraint_jacobian.py; } | awk '{print $1}'
#   -> c7e1d14142048ffecdfa59b601dd49f9
```

---

**Document Status:** ✅ Complete — Sprint 38 Day 6. **✅ PROCEED** — measured 369,024 → 24/136/51,840 referenced per row, three equations confirmed exactly against projection; total **259,728 ≈ 78 s**, inside the ≤300 s gate, needing **none** of the missing machinery. **Day 5's 4,532 projection is corrected to 259,728** (only `tbal`'s condition is `tech`). **`src/` reverted, byte-identical.**
**Last Updated:** 2026-08-20 · **Owner:** Sprint 38 execution team

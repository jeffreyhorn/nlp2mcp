# Sprint 38 Day 5 — Checkpoint 1 + P2 sarf: trace and control

**Date:** 2026-08-20 · **Branch:** `planning/sprint38-day5-checkpoint1-sarf` · **Measured at:** `41d0549f` · **Toolchain:** GAMS **54.2.1** / PATH **5.2.01** · **Scope:** measurement + trace. **No `src/` change** — PR24/PR27 control before any implementation.

**Verdict: 🔶 THE DESIGN'S TWO PILLARS ARE BOTH BLOCKED — measured, not argued. A third route is available, needs no blocked dependency, and projects ~100× better than the design's target.**

The Phase-0 gate for P2 is **not** being taken to `src/` today. That is the control-first discipline working: three days of implementation would have been spent building toward an activity set the codebase cannot produce.

---

## 1. Checkpoint 1 — and the Day-4 assertion fires on its first real use

**KPI block, derived (not quoted) via the Day-4 helper:**

```
Solve 108 · Match 94 (65 cold + 29 presolve) · Translate 135 · mi 7 · pse 6 · all-219 97 — derived at 41d0549f
```

Unchanged from Day 0, as expected: `git diff 8cffec29..HEAD -- src/ data/` is **empty**. Days 1–4 changed docs, `scripts/` and `tests/` only.

**The checkpoint refused to run, correctly.** `--resolve-changed --since-commit 8cffec29` selected **0 changed goldens** and, instead of the pre-Day-4 `verdict: GO`, returned **exit 1**:

> *no emit goldens changed since 8cffec29, so the checkpoint measured NOTHING and cannot certify anything. This is not a GO.*

Re-run with `--allow-empty` (Days 1–4 were legitimately golden-free), it reports GO carrying its own disclaimer — *"This certifies nothing."* **This is the Sprint-37 false-GO path, closed and demonstrated on a live checkpoint rather than in a unit test.**

**P1 disposition (recorded per the prompt):** REPLAN'd Day 1, 0 bucket, ~14 h reallocated. **P7 pulled to Days 2–3 and closed** (6 gates). **P8 moved to Days 9–12 at 26 h.** Sprint total 116 h → **112 h**.

## 2. The census — derived independently, and it confirms the design

Every figure below was re-derived; none is quoted from the prep doc.

| quantity | derived | source | design's figure |
|---|---|---|---|
| `task` declared columns | **369,024** | IR: `16 × 24 × 31 × 31` | 369,024 ✓ |
| active `(g,t)` (`taskposs`) | **129** | **GAMS itself** | — |
| nonzero `tech(g,m,n)` | **44** | GAMS: `nTech`; **and** IR: 165 entries → 44 nonzero | — |
| **active columns** | **398** | **GAMS**: `sum((g,t)$taskposs, sum((m,n)$tech, 1))` | 398 ✓ |
| rows referencing `task` | **1,183** | IR equation domains | 1,183 ✓ |
| declared/active ratio | **927×** | 369,024 / 398 | 927× ✓ |

**The IR count of nonzero `tech` (44) and GAMS's own `nTech` (44) agree** — two independent derivations of the number the whole projection rests on.

## 3. Pillar 1 — S1/S2 cannot be built: the activity set is not obtainable

The design's S1/S2 require *"active instances for gated variables"*, gated on *"`taskposs`-style membership"*. **`taskposs` is not resolvable.**

```
resolve_set_members('taskposs', ir)
  → warning: Dynamic subset 'taskposs' has no static members;
             falling back to parent set 'g' (16 members)
```

**Two failures, not one:**

| | expected | actual |
|---|---|---|
| **content** | the 129 active `(g,t)` pairs | **all 16** members of the parent set |
| **arity** | 2-D `(g,t)` | **1-D** `g` |

The fallback returns the *wrong set at the wrong arity*. A gate built on it would not merely be imprecise — it would compare 1-tuples against 2-D column indices.

**The data exists in the IR; the evaluator does not.** `ir.set_assignments` captures all three statements defining `taskposs`, and the tables they depend on are present (`atask` 288 values, `btask` 412, `tech` 165). Computing it needs an interpreter for `$`-conditioned parameter assignments, `ord`, and `sum` over computed params:

```
treq(g,t,c,s)      = 1$(atask(c,g,s) = ord(t)) + btask(c,g,s,t)
treq("transport",…) = treq(…) * cropdata(…) * yield(…)
taskposs(g,t)      = sum((c,s), yes$treq(g,t,c,s))
taskposs("spray",t) = taskposs("spray",t) + taskposs("harvest-c",t)
```

That is **a new static-evaluator subsystem**, and `resolve_set_members` is called from the AD layer across the whole corpus — **high blast radius**. It is not in the 20–28 h re-architecture estimate.

## 4. Pillar 2 — S3's symbolic path does not exist either

S3 asks for a parametric `stat_task(g,t,m,n)$taskposs(g,t)` instead of enumerated rows, and the Phase-0 gate tests for exactly that (*symbolic multiplier indices; `grep 'nu_…("'` empty*).

**There is no symbolic-instance machinery in `src/`.** A search for `symbolic_instance` / `SymbolicInstance` returns nothing. `ISSUE_1385`'s companion doc is titled *"option-1 short-circuit redesign **symbolic instance handling**"* — i.e. the mechanism is **named as work to be done**, not as an existing path to switch on.

**So both routes the design offers are unbuilt**: one needs a set evaluator, the other needs a symbolic-instance layer.

## 5. A third route — filter columns per row from `tech`'s STATIC data

**The reframing that unblocks it:** the design assumed the activity predicate is `taskposs`. But **the predicate that actually bounds the columns is `tech`, and `tech` is a Table — statically present in the IR.** `taskposs` restricts which *rows* exist, and GAMS already applies that via the equation's own `$` condition.

The hot loop (`constraint_jacobian.py:1002–1013`) already holds `constraint_expr`. For a row like

```gams
tbal(g,t)$taskposs(g,t).. … =e= sum((m,n)$tech(g,m,n), task(g,t,m,n)) …
```

the surviving `task` columns are exactly the `(m,n)` for which `tech(g,m,n)` is nonzero — **44 entries, known at emit time.**

**Projection, per equation (using only `tech`'s static support):**

| equation | rows | `task` columns referenced |
|---|---|---|
| `tbal(g,t)` | 384 | 1,056 |
| `equipb1(m,t)` | 648 | 1,056 |
| `equipb2(n,t)` | 120 | 1,056 |
| `labor(t)` | 24 | 1,056 |
| `cbal(c)` | 6 | 264 |
| `acost3` | 1 | 44 |
| **total** | **1,183** | **4,532** |

| approach | differentiations | at the measured 3,343/s |
|---|---|---|
| current | 436,555,392 | **~36.3 h** |
| design's O(active) | 470,834 | **~141 s** |
| **per-row filter** | **4,532** | **~1.4 s** |

**~100× better than the design's target, and it would meet the ORIGINAL "single-digit seconds" gate** that Task 5 refuted and the owner revised to ≤300 s.

### 5.1 What it needs, and what is honestly not yet established

**Needs:** an instance-level collector. `find_variables_in_expr` returns variable **names** only (`set[str]`); there is no helper returning the *index tuples* of a variable referenced in an expression. The new helper must resolve a `VarRef` inside `Sum((m,n), …)$ParamRef(tech(g,m,n))` against `tech`'s static support.

**⚠ Not established — state plainly:**

1. **4,532 is a projection from a static support count, not a measured run.** It must be confirmed by the **per-call-site counter probe** — the one Prep Task 5 used to produce the 3,343 diff/s rate, described in `SARF_REARCH_DESIGN.md` **§1.2 "Measured, on a bounded run"** — before any claim is made. *(That §1.2 is in the design doc, not in this one.)*
2. **I have not verified the collector can be written cheaply** at that call site, only that the inputs are present.
3. **Rows are untouched** (1,183), exactly as the design noted for O(active). This reduces columns only.
4. **`tech`'s keys are stored dotted** — `('plough.f-plow-6', 'tractor-l')`, a 3-D table held as `(g.m, n)` 2-tuples. **A consumer assuming 3-tuples silently gets nothing.** My own first count fell into this and reported "33 distinct g" for a 16-member set; splitting on `.` gives 44 nonzero, which then matched GAMS's `nTech` exactly. Any implementation must handle it explicitly.

## 6. Recommendation for Day 6

**Do not implement S1/S2 or S3 as written.** Both are blocked on machinery that does not exist, and building either is a new subsystem rather than the scoped re-architecture.

**Prove or kill the §5 route first, with a probe rather than an implementation** — the same shape as Day 1, and reusing the counter harness from `SARF_REARCH_DESIGN.md` §1.2. Insert the instance collector as a *counter only* (no behaviour change) at `constraint_jacobian.py:1013`, and confirm the per-row referenced-column count drops from 369,024 toward **≤ 44**. That is observable in minutes and does not require the change to be complete.

**The Day-6 REPLAN trigger still applies and is now sharper.** The plan's trigger — *"S1+S2 do not agree on the active column set"* — is already unreachable, because **the active column set cannot be formed**. Restate it as: *if the per-row collector does not drop the count to ≤ 44 by end of Day 6, take the exit.*

**If §5 also fails, P2 REPLANs and its remaining budget follows P1's to P8** — which, with Days 2–3's gates landed, has five eligible candidates ready.

## 7. Reproduction

```bash
# §1 — checkpoint (refuses, then opts in)
.venv/bin/python scripts/gamslib/run_full_test.py --resolve-changed --since-commit 8cffec29 --quiet ; echo $?
.venv/bin/python scripts/gamslib/run_full_test.py --resolve-changed --since-commit 8cffec29 --allow-empty --json
.venv/bin/python scripts/sprint_audit/kpi_block.py --format line

# §2 — the 398, from GAMS itself (truncate the model before Variables, then count)
#   nTaskposs=129  nTech=44  nActive=398  nDeclared=369024
gams probe.gms lo=0 errmsg=1

# §3 — the blocked resolver
.venv/bin/python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
from src.ad.index_mapping import resolve_set_members
ir = parse_model_file('data/gamslib/raw/sarf.gms')
print(ir.sets['taskposs'].domain, len(ir.sets['taskposs'].members))
print(len(resolve_set_members('taskposs', ir)[0]))   # 16 — the parent set, arity 1"

# §5 — tech's static support (NOTE the dotted keys)
.venv/bin/python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
ir = parse_model_file('data/gamslib/raw/sarf.gms')
t = ir.params['tech'].values
tri = {(a.partition('.')[0], a.partition('.')[2], n): v for (a, n), v in t.items()}
print(len(tri), sum(1 for v in tri.values() if v))   # 165 entries, 44 nonzero"
```

---

**Document Status:** ✅ Complete — Sprint 38 Day 5. **Checkpoint 1 GO (empty, explicitly opted in).** **P2's designed change set is blocked at both pillars**; a third route using `tech`'s static support projects **~1.4 s** vs the design's ~141 s, and is to be **probed, not implemented**, on Day 6. **No `src/` change.**
**Last Updated:** 2026-08-20 · **Owner:** Sprint 38 execution team

# Sprint 38 Prep Task 5 — sarf P2: O(active) Re-Architecture Design Refresh & Atomicity Plan

**Date:** 2026-08-17 · **Branch:** `planning/sprint38-task5` · **Measured at:** `949a4587` · **Scope:** control-only — a **read-only probe** was inserted at S1's per-column call site, measured, and **reverted**. `src/` is byte-identical to `main`; DB and goldens untouched.

**Verdict: 🔶 PROCEED, WITH THE PHASE-0 THRESHOLD REFUTED.** The design premise (2.2) is **confirmed decisively** — and the timing claim (2.3) is **not**. The O(active) short-circuit buys a **927× reduction**, taking sarf from **~36 hours to ~141 seconds**. That is enough to earn the **+1 Translate KPI**, and roughly **16× short of the pre-registered "single-digit seconds" gate**.

The prompt asked for a fallback threshold to be pre-registered *"so a 40 s result is a decision, not an argument"*. The measurement says the result will be ~141 s, so **that decision is needed now, not in-sprint**.

---

## 1. 2.2 — the premise is CONFIRMED (structurally and by measurement)

### 1.1 The call is per-column, and the sparsity check is per-*variable*

`constraint_jacobian.py` (S1), the hot loop:

```python
for var_name, var_instances in var_instances_cache:
    if var_name not in referenced_vars:      # sparsity check — VARIABLE level only
        continue
    for var_indices in var_instances:        # every DECLARED instance
        col_id = index_mapping.get_col_id(var_name, var_indices)
        if col_id is None:
            continue
        derivative = differentiate_expr(constraint_expr, var_name, var_indices, config)
```

Once a variable is referenced anywhere in a row, the loop differentiates w.r.t. **every declared instance of it**. There is no active-column filter. So **`differentiate_expr` volume is directly proportional to declared columns** — the short-circuit removes it proportionally, rather than merely skipping enumeration.

### 1.2 Measured, on a bounded run

A read-only counter at that exact call site, 120 s cap:

```
T5PROBE calls=75000   rows=1 elapsed=20.2s rate=3712/s byvar=[('task', 74994), ('sales', 6)]
T5PROBE calls=150000  rows=1 elapsed=43.4s rate=3458/s byvar=[('task', 149994), ('sales', 6)]
T5PROBE calls=250000  rows=1 elapsed=74.8s rate=3343/s byvar=[('task', 249994), ('sales', 6)]
```

Three facts, all decisive:

- **`rows=1`** — after 75 s and a quarter-million differentiations it is **still on the first constraint row**.
- **`byvar` is ~100 % `task`** (249,994 of 250,000). The blow-up is one variable.
- **Rate ≈ 3,343 calls/s**, mildly degrading (3712 → 3343).

One row therefore costs **369,024 calls ≈ 110 s**. This is exactly the shape the Sprint-37 profile implied and it is now measured at the call site rather than inferred from a profile.

## 2. 2.3 — the "single-digit seconds" claim is REFUTED

The column count is only half the product. The other half is **rows**.

### 2.1 Row census (derived from the IR, not assumed)

`task(g,t,mn,mn)` with `|g|=16, |t|=24, |mn|=31` ⇒ **369,024** declared columns ✓ (matches the banked figure).

Equations referencing `task`:

| equation | domain | instances |
|---|---|---|
| `equipb1` | `(m,t)` | **648** |
| `tbal` | `(g,t)` | **384** |
| `equipb2` | `(n,t)` | **120** |
| `labor` | `(t)` | 24 |
| `cbal` | `(c)` | 6 |
| `acost3` | scalar | 1 |
| | **total** | **1,183** |

### 2.2 The projection

| | differentiations | at 3,343/s |
|---|---|---|
| **current** | 1,183 × 369,024 = **436,555,392** | **~36.3 hours** |
| **O(active) columns** | 1,183 × 398 = **470,834** | **~141 seconds** |
| Phase-0 gate (PR20) | — | **single-digit seconds** |

**The 36.3-hour figure explains the non-termination directly** — it is not a pathological hang, it is 436 million differentiations.

**The short-circuit delivers its full 927× — and still lands ~16× short of the gate**, because it reduces columns only. The 1,183 rows are untouched.

### 2.3 The threshold decision (pre-registered here, as instructed)

| option | threshold | consequence |
|---|---|---|
| **(a) accept ~141 s** ✅ *recommended* | "sarf translates within the pipeline budget" | **The KPI is +1 Translate — sarf only needs to *complete*.** 141 s does that. The 100 s cap that currently kills it is a *test-harness* cap, not a product requirement, and is itself adjustable. |
| (b) hold single-digit seconds | unchanged | Requires **also gating rows** (the 2-D constraint gate must cut 1,183 → ~tens), which is additional scope not in the 20–28 h estimate |
| (c) abandon | — | Forfeits the sprint's only KPI mover for a threshold the KPI does not require |

**Recommendation: (a).** The Phase-0 gate should assert **"sarf completes and produces a byte-stable golden"** with a **generous wall-clock ceiling (e.g. ≤ 300 s, nightly slot)**, not single-digit seconds. Holding a threshold the KPI does not need would convert a 927× win into a REPLAN.

**If (b) is preferred**, the row side must be scoped explicitly and the 20–28 h estimate revisited — that is a materially different piece of work and should not be discovered mid-build.

## 3. The atomic change set

The change lands as **one unit**; a partial landing leaves multipliers with no stationarity coupling — an inconsistent MCP, and an explicit REPLAN rather than partial progress.

| site | location | change | guard | fallback |
|---|---|---|---|---|
| **S1** | `constraint_jacobian.py:78` (`_precompute_variable_instances`) → consumed at the `:1013` hot loop | Return **active** instances for gated variables instead of all declared | Gate fires only for variables whose activity set is known (`taskposs`-style membership) | Un-gated variables keep full enumeration — every other model is on the existing path |
| **S2** | `index_mapping.py:634` | Column-index construction restricted to the same active set, so `get_col_id` stays consistent with S1 | Same activity predicate | Unchanged for un-gated variables |
| **S3** | `stationarity.py` | Emit parametric `stat_task(g,t,m,n)$taskposs(g,t)` rather than enumerated rows | Same | Existing enumeration retained otherwise |
| — | emit | `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0` | — | Pins inactive columns so the MCP stays square |

**S1 and S2 must move together**: S1 changes which instances are differentiated, S2 changes which column ids exist. If they disagree, `get_col_id` returns `None` for live columns (silently dropping derivatives) or ids for dead ones.

### 3.1 The six corpus-safety call sites

`enumerate_variable_instances` has exactly **six** non-definition call sites; each must be shown unperturbed for un-gated variables:

| # | site | in scope? |
|---|---|---|
| 1 | `index_mapping.py:634` | **S2 — changes** |
| 2 | `constraint_jacobian.py:78` | **S1 — changes** |
| 3 | `gradient.py:287` | must be unperturbed |
| 4 | `gradient.py:453` | must be unperturbed |
| 5 | `complementarity.py:367` | must be unperturbed |
| 6 | `complementarity.py:512` | must be unperturbed |

**Unperturbed-proof:** sites 3–6 are shown unchanged by the full-corpus gate (zero drift across the in-scope goldens). `gradient.py` and `complementarity.py` are **byte-unchanged since the S34 anchor** (Task 2), so any drift there is attributable to this change alone.

## 4. Verification strategy — the two gate peculiarities

### 4.1 `leak-check` is the wrong instrument for sarf

sarf has **no committed golden**, so `make leak-check MODEL=sarf` puts it in `missing` and reports:

```
NO-OP: expected drift on sarf but the emit was byte-identical — the fix did not change the emit.
exit 2
```

Task 3 established this **exits non-zero correctly**, but the message is wrong for this case (nothing was compared). Task 3's design adds an `UNVERIFIABLE` verdict and an `--expect-new` flag precisely for it. **This design depends on that P6b change**, and the dependency should be sequenced: **P6b before P2's gate run**.

**The real gate is:** `make check-goldens` shows **zero drift across the in-scope corpus**, **plus** sarf newly producing a golden.

### 4.2 sarf cannot be its own fixture — surrogate design (2.4)

At 369,024 columns the fail-before state does not terminate, so a `sarf`-based fixture can never demonstrate fail-before/pass-after.

**Surrogate requirements:**
- **Corpus-free** — constructed in-test, not read from `data/gamslib/raw/`, which is absent in CI. A skip-if-absent fixture is **inert** and guards nothing (the S37 Unknown 7.3 refutation).
- **Terminating fail-before** — the un-gated path must complete in test time. From §1.2's 3,343 calls/s, a surrogate with **~5,000 declared columns and a handful of rows** costs ~1.5 s un-gated and is near-instant gated: a genuine, fast fail-before.
- **Same guarded path** — a 4-D variable with a 2-D activity set (`taskposs`-shaped), so the gate predicate is exercised rather than merely the arithmetic.
- **Asserts the shape, not just the time** — the emitted `stat_*` must carry **symbolic** multiplier indices; `grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("'` must be empty. A timing-only fixture would pass on a wrong-but-fast emit.

### 4.3 Golden creation and the scope interaction (2.5)

sarf newly produces a golden, and Task 6 adopts 36 presolve goldens. **Both move `--min-scope`, and the arithmetic is order-independent:**

| | discovered | in-scope |
|---|---|---|
| start | 170 | 163 |
| P2 then P4 | 171 → **207** | 164 → **200** |
| P4 then P2 | 206 → **207** | 199 → **200** |

**Either order ends at 207 discovered / 200 in-scope**, so `--min-scope` must finish at **207**. The only hazard is an intermediate commit where the assertion lags the corpus — so each landing must raise `--min-scope` **in the same change**, exactly as Task 6 specifies.

**Determinism ×3 on the new golden is DESIGN-VERIFIED only** — the golden does not exist yet, so `PYTHONHASHSEED {0,1,42}` byte-stability is an in-sprint gate, not a prep result.

## 5. Phase-0 acceptance gate (PR20), revised

- **sarf completes** and produces `data/gamslib/mcp/sarf_mcp.gms` — wall-clock **≤ 300 s** on a nightly slot (**revised from "single-digit seconds"** per §2.3; the original threshold is refuted at ~141 s projected).
- **`stat_task` matches the banked 7-term derivation** with **symbolic** multiplier indices — `grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` **empty**.
- **Atomic:** the 2-D constraint gate + S1/S2/S3 + `task.fx` in one change; a partial landing is a REPLAN.
- **Byte-stable golden**, determinism ×3 `{0,1,42}`.
- **Full-corpus:** `make check-goldens` zero drift, `--min-scope` raised in the same change.
- **Surrogate fixture** lands with the change, corpus-free, fail-before/pass-after.

## 6. REPLAN exit — named trigger

**Trigger day: the end of the second implementation day.** If by then S1+S2 do not agree on the active column set — measured by a bounded sarf run showing the per-row call count dropping from 369,024 toward ~398 — **take the exit**. That single number is observable within minutes using the §1.2 probe and does not require the change to be complete.

The plan calls for taking this exit **early rather than nursing it**, because a partial landing is an inconsistent MCP rather than partial progress.

**What the exit banks:** the row/column census (§2.1), the measured call rate, the probe, the surrogate design, and the revised threshold — none of which is invalidated by an incomplete build.

## 7. Reproduction

```bash
# §1.2 — the per-column call probe (insert at constraint_jacobian.py:1013, revert after)
#   counts calls, distinct rows, and attribution by variable; 120 s cap is enough

# §2.1 — the row census
.venv/bin/python - <<'EOF'
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
from src.ir.ast import VarRef
ir = parse_model_file('data/gamslib/raw/sarf.gms')
sizes = {k: len(v.members) for k, v in ir.sets.items() if getattr(v, 'members', None)}
sizes['mn'] = 31
# walk eq.lhs_rhs for VarRef('task'); multiply eq.domain sizes
EOF
```

---

**Document Status:** ✅ Complete — Sprint 38 Prep Task 5. **2.2 VERIFIED** (premise confirmed, measured at the call site) · **2.3 ❌ WRONG** (~141 s projected, not single-digit seconds; threshold decision pre-registered) · **2.4 ✅** (surrogate designed) · **2.5 ✅** (scope arithmetic order-independent; determinism design-verified).
**Last Updated:** 2026-08-17 · **Owner:** Sprint 38 execution team

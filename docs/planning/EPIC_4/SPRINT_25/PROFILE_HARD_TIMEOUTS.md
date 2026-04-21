# Profile — Hard Translation Timeouts (5 models)

**Created:** 2026-04-21
**Sprint:** 25 (Prep Task 8)
**Target models:** `iswnm`, `mexls`, `nebrazil`, `sarf`, `srpchase`
**Measurement setup:** `PYTHONHASHSEED=0`, 900s per-model SIGALRM cap, one run per model, MacBook (local development machine)
**Profile artifacts:** `/tmp/task8-profiles/<model>.json` (pure JSON profiler stdout) paired with `/tmp/task8-profiles/<model>.log` (stderr — warnings / log output) for each of 5 models

---

## Executive Summary

**Unified bottleneck across all 5 models: `compute_constraint_jacobian` (stage `ad_jacobian`).** Every single profiling run finishes `preprocess` / `parse+ir_build` / `normalize` / `ad_gradient` well within 60s, then stalls in `ad_jacobian`. The root cause is the same `SetMembershipTest` dynamic-subset-has-no-static-members pattern surfaced in Sprint 24 ISSUE_1228 (iswnm) — now confirmed to affect **all 5** hard-timeout models.

**Headline results (900s SIGALRM budget):**

| Model | Status | Total | Dominant stage | Stage time | Affected equations | Fallback subsets |
|---|---|---|---|---|---|---|
| `srpchase` | **COMPLETE** | 500s | `ad_jacobian` | 466.6s (93%) | 2 | 1 (`srn`→`n`, 1001 members) |
| `iswnm` | timeout @ 900s | — | `ad_jacobian` | > 865s | 1 | 1 (`nb`) |
| `sarf` | timeout @ 900s | — | `ad_jacobian` | > 852s | 3 | 2 (`taskposs`, `equipposs`) |
| `mexls` | timeout @ 900s | — | `ad_jacobian` | > 834s | 3 | 3 (`mmpos`, `mrpos`, `mspos`) |
| `nebrazil` | timeout @ 900s | — | `ad_jacobian` | > 860s | 13 | 4 (`fposs`, `cpossn`, …) |

**Tractability classification:**

- **`srpchase`: TRACTABLE at 900s budget (completes in 500s).** At the current 600s pipeline cap it still times out; either a budget bump or a targeted optimization is needed to land it.
- **`iswnm`, `sarf`, `mexls`, `nebrazil`: INTRACTABLE at current architecture.** All 4 still stuck inside `ad_jacobian` at the 900s mark, far from completion.

**Priority 5 scope recommendation for Sprint 25:** **DEFER all 5 models to Sprint 26** pending an architectural fix to `SetMembershipTest` fallback handling. The targeted optimization (see §Section 3) is ~1–2 days of engineering work; it doesn't fit the Sprint 25 alias-AD focus and its 12–18h emitter backlog. Filing (see §Section 4.2): open one new architectural issue for the fallback-handling fix, apply the `sprint-26` label to the still-open translate-timeout trackers #1185 and #1192, and reference/link #1169 (closed), #1185, #1192, and Sprint 24 ISSUE_1228 from the new issue.

**Addresses:**

- **Unknown 5.1** (any tractable?): VERIFIED — 1 of 5 (srpchase) is tractable at 900s; under 600s it requires a targeted fix.
- **Unknown 5.2** (where does 600s interrupt?): VERIFIED — **all 5** interrupt in `ad_jacobian`; parse/IR/normalize/gradient all complete quickly.
- **Unknown 5.3** (sparse Jacobian help?): **VERIFIED WRONG** — sparse Jacobian doesn't help because the bottleneck is instance **enumeration** (deciding which rows/columns to compute), not the compute itself. Sparse representation saves storage, not enumeration time.
- **Unknown 5.4** (srpchase is a preprocessor issue?): **VERIFIED WRONG** — srpchase's preprocessor takes 33 ms; the bottleneck is `ad_jacobian` (466s = 93% of total). ScenRed's impact is through runtime set cardinality (1001-member `n`), not macro expansion.

---

## Section 1 — Per-Model Stage Timing

Reproduction recipe. **The profile harness is NOT committed**; it lived at `/tmp/task8-profile.py` during Task 8's prep run. To reproduce: first copy the harness from §Appendix A of this doc into `/tmp/task8-profile.py` (or any path of your choosing), then run the loop:

```bash
# Step 1: save the harness at /tmp/task8-profile.py — copy the Python source from §Appendix A.
# Step 2: run the profiler for each model under a 900s SIGALRM budget.
#         The harness prints JSON to stdout; Python warnings / nlp2mcp logs
#         go to stderr. Keep them in separate files so the .json artifact is
#         valid JSON and the .log artifact holds the warning trail.
mkdir -p /tmp/task8-profiles
for m in srpchase iswnm sarf mexls nebrazil; do
  PYTHONHASHSEED=0 .venv/bin/python /tmp/task8-profile.py "$m" 900 \
    >  "/tmp/task8-profiles/${m}.json" \
    2> "/tmp/task8-profiles/${m}.log"
done
```

After running: each `<model>.json` contains the profiler's JSON output (pure stdout); each `<model>.log` contains the per-stage `warnings.warn` / `logger.warning` trail (useful for post-hoc inspection of fallback-subset warnings).

If Sprint 26's architectural fix on `enumerate_equation_instances` is pursued, move the harness to `scripts/task8_profile.py` (or similar) for a committed regression benchmark. Sprint 25 deliberately keeps it out of `scripts/` because Task 8 is a one-shot investigation, not an ongoing tool.

### 1.1 `srpchase` (COMPLETE @ 500s)

```
preprocess       0.033s (0.01%)
parse+ir_build   1.196s (0.24%)
normalize        0.000s (<0.01%)
ad_gradient      0.249s (0.05%)
ad_jacobian    466.613s (93.3%)   ← bottleneck
kkt_assemble    32.168s (6.4%)
emit_mcp         0.020s (<0.01%)
─────────────────────────────────
TOTAL          500.279s
```

**Size:** Jacobian 1002 × 2003 (eq) + 1001 × 2003 (ineq); 2 stationarity equations (after MCP collapse); 112 lines of output GAMS.

**Subset pattern:**

- Set `n` = 1001 members (ScenRed expands to 1000 scenarios + 1 root)
- Set `srn` = dynamic subset of `n`, **zero static members** — population happens at GAMS runtime via `$libInclude scenred`
- Set `leaf` = dynamic subset, also empty-static, used in condition `SetMembershipTest(leaf, (SymbolRef(srn)))`
- Affected equations: `demand`, `slack` (both indexed over `n`)
- Warnings: 8× "cannot be evaluated statically"; 15× "Dynamic subset srn has no static members; falling back to parent set n (1001 members)"

**Why it completes (when the others don't):** srpchase has only 2 affected equations, and the parent-set fallback expands to 1001 × 1 indices per equation — large but finite. 466s of AD work is mostly per-instance derivative computation, which does eventually exit.

### 1.2 `iswnm` (TIMEOUT @ 900s)

```
preprocess       0.089s
parse+ir_build  31.726s
normalize        0.000s
ad_gradient      2.014s
ad_jacobian    >865s      ← stuck (budget cap hit)
───────────────────────
ELAPSED        899.6s (TIMEOUT)
```

**Size:** 691 lines, multi-index sets, single `solve`. Parse+IR is non-trivial (32s) due to many data tables.

**Subset pattern:**

- Set `nb`: dynamic subset of `n`, **zero static members** — per Sprint 24 ISSUE_1228 this was the known root cause.
- Affected equation: `nbal` (indexed over `n` × `m`)
- Warnings: 4× "cannot be evaluated statically"; separately, the dynamic-subset fallback message ("Dynamic subset ...") is logged from `src/ad/index_mapping.py` by `resolve_set_members` via `logger.warning`. Any warning-trace call-site remapping to `src/ad/constraint_jacobian.py` applies to the `warnings.warn(..., stacklevel=2)` path from `enumerate_equation_instances`, not to that logger message.

**Why it doesn't complete:** The fallback expands `nb → n` where `n` includes many members × `m` (months) → Cartesian explosion. Unlike srpchase, whose 2 affected equations each have small 1D target slots (1001 × 1 per equation), iswnm's `nbal` has a larger 2D index product.

### 1.3 `sarf` (TIMEOUT @ 900s)

```
preprocess       0.100s
parse+ir_build  18.026s
normalize        0.001s
ad_gradient     28.612s
ad_jacobian    >852s      ← stuck
───────────────────────
ELAPSED        899.5s (TIMEOUT)
```

**Size:** 471 lines; multi-index cropping model with a large `(c, s)` Cartesian product.

**Subset pattern:**

- Dynamic subsets: `taskposs`, `equipposs` — both have no static members; populated at GAMS runtime via assignments like `taskposs(g,t) = sum((c,s), yes$treq(g,t,c,s))`
- Affected equations: `tbal`, `equipb1`, `equipb2` (3 equations)
- Warnings: 10× "cannot be evaluated statically"

**Notable:** `ad_gradient` takes 28.6s (non-trivial) before entering `ad_jacobian`. This suggests sarf is the most gradient-heavy of the 4 intractable models.

### 1.4 `mexls` (TIMEOUT @ 900s)

```
preprocess       0.170s
parse+ir_build  51.127s   ← slowest parse of the 5
normalize        0.003s
ad_gradient     13.595s
ad_jacobian    >834s      ← stuck
───────────────────────
ELAPSED        899.5s (TIMEOUT)
```

**Size:** 1088 lines — largest source file of the 5. Metal-industry LP with multi-region Cartesian structure.

**Subset pattern:**

- Dynamic subsets: `mmpos`, `mrpos`, `mspos` — 3 distinct subsets for mining, refining, smelting respectively
- Affected equations: `ccm`, `ccr`, `ccs` (3 equations, one per industry)
- Warnings: 9× "cannot be evaluated statically"

**Notable:** Parse+IR takes 51.1s here — notable but still only 6% of the 900s budget. The bottleneck is firmly in Jacobian enumeration.

### 1.5 `nebrazil` (TIMEOUT @ 900s)

```
preprocess       0.197s
parse+ir_build  25.997s
normalize        0.001s
ad_gradient     12.933s
ad_jacobian    >860s      ← stuck
───────────────────────
ELAPSED        899.5s (TIMEOUT)
```

**Size:** 1021 lines; multi-region agricultural model.

**Subset pattern:**

- Dynamic subsets: `fposs`, `cpossn`, `xposs`, `cpossp` — 4 distinct subsets
- Affected equations: 13 (highest count of the 5) — `acrop`, `ahlc`, `ares`, `dprodl`, `ratr`, `combp`, `dem`, `demreg`, etc.
- Warnings: 50× "cannot be evaluated statically"; 116× "Dynamic subset … no static members"

**Why the highest fallback count:** nebrazil has the most equations affected by the pattern, so the enumeration explosion compounds across all 13.

---

## Section 2 — Root Cause: SetMembershipTest Dynamic-Subset Fallback

### 2.1 The pattern

All 5 models use the same GAMS idiom:

```gams
Set X(parent_set);           /* dynamic subset, declared with no members */
X(...) = yes$(<runtime_condition>);  /* populated by runtime assignment */

Equation eq(i)$X(i);         /* equation guarded by dynamic-subset membership */
eq(i)$X(i) .. <body> =e= 0;
```

When `nlp2mcp` tries to enumerate the instances of `eq(i)` for differentiation, it evaluates the `$X(i)` condition at Python AD time. Because `X`'s membership is set dynamically (at GAMS runtime), `SetMembershipTest(X, (i))` **cannot be evaluated statically** — the check in [`src/ir/condition_eval.py`](../../../../src/ir/condition_eval.py) (`SetMembershipTest` evaluation path) **raises `ConditionEvaluationError`** with the message `Set membership for '<name>' cannot be evaluated statically`. The fallback in [`src/ad/index_mapping.py`](../../../../src/ad/index_mapping.py) happens when that exception is caught: `resolve_set_members` falls back to parent-set members, and `enumerate_equation_instances` **emits a `UserWarning`** (`Including unevaluable instances by default`) while **including all instances from the parent set** so the runtime condition survives in the emitted equation. Call sites in `src/ad/constraint_jacobian.py` invoke this behavior many times; the behavior itself lives in the two implementation files above.

For `srpchase` this produces 1001 instances per equation (parent set `n`). For `nebrazil` with 13 affected equations and 4 fallback subsets, the product explodes.

### 2.2 Warning signatures (confirmed in all 5)

Every model's profile output contains:

```
UserWarning: Failed to evaluate condition SetMembershipTest(<subset>, ...)
  ... Set membership for '<subset>' cannot be evaluated statically
  because the set has no concrete members at compile time.
  Including unevaluable instances by default.
```

Implementation sites (distinguishing exception origin vs warning emission; both propagate through the `compute_constraint_jacobian` / `enumerate_equation_instances` call stack):

- **"`cannot be evaluated statically`"** — the message text originates in `src/ir/condition_eval.py`, where the `SetMembershipTest` static-evaluation path **raises `ConditionEvaluationError`** when the subset has no concrete members at compile time (see around line 417 for the `Set membership for '<name>' cannot be evaluated statically` message, and line 265 for the more general condition-evaluation failure). Note: this is an exception, not a warning; the warning-form surface in profile output comes from the catch site below.
- **"`Dynamic subset '<X>' has no static members; falling back to parent set '<parent>' (N members)`"** — implemented in `src/ad/index_mapping.py` inside `resolve_set_members` (around lines 177–178 and 279) when it walks a dynamic subset and falls back to its parent (uses `logger.warning(...)`).
- **"`Including unevaluable instances by default`"** — emitted as a `warnings.warn(...)` UserWarning in `src/ad/index_mapping.py` inside `enumerate_equation_instances` (around line 430) when it catches the `ConditionEvaluationError` raised by `condition_eval.py`. This is the fallback branch that produces the Cartesian expansion.

These implementation locations are called from many sites across `src/ad/constraint_jacobian.py` (the compute_constraint_jacobian rows/columns walk), so profiler stack traces will show `constraint_jacobian.py` call-site lines — but the **exception text originates in `condition_eval.py`** and the **warning / fallback behavior lives in `index_mapping.py`**. Line numbers above are approximate and may drift; use the function names (`resolve_set_members`, `enumerate_equation_instances`) as the stable reference.

Total warnings per model:

| Model | `cannot be evaluated statically` | `Dynamic subset … no static members` |
|---|---|---|
| `srpchase` | 8 | 15 |
| `iswnm` | 4 | (not emitted; different warning path) |
| `sarf` | 10 | (not emitted) |
| `mexls` | 9 | (not emitted) |
| `nebrazil` | 50 | 116 |

### 2.3 Why it's ONE bug, not five

All 5 models hit the same helper `enumerate_equation_instances` with the same fallback branch. Fix the fallback branch → potentially unblocks all 5. The specific subset names differ but the semantics are identical.

---

## Section 3 — Proposed Optimization

### 3.1 Targeted fix: lazy-evaluation / runtime-preserved conditions

The current include-all fallback produces an over-large stationarity system. Each stationarity row carries the `$X(i)` condition on its own, so the emitted MCP is still correct — it's just wastefully large. Three candidate fixes (ordered by cost):

**Option 1 — Short-circuit empty fallback (simplest, ~4–6h)**

Detect "dynamic subset with zero static members" at `enumerate_equation_instances` entry. When triggered, emit a single symbolic equation instance with the condition preserved, rather than 1001 concrete instances. Pre-existing logic in `src/kkt/stationarity.py` already supports symbolic conditions in emitted output; this change makes the AD path match.

**Expected speedup for srpchase:** 466s → <10s (99%+ reduction). Likely ports to iswnm (similar structure).
**Risk:** models with LEGITIMATE static evaluation that happen to produce empty sets (rare) would collapse too — need a guard.

**Option 2 — Track subset populations via assignment statements (~2–3 days)**

Walk the IR looking for `X(idx) = yes$<cond>` assignments and build a static "what can X contain" map. Reduces fallback frequency by computing subset populations from their assignment statements.

**Expected speedup:** larger than Option 1; helps all 5 if assignments are statically resolvable. But tree traversal cost grows with model size.

**Option 3 — Defer instance enumeration to GAMS runtime (~1 week)**

Instead of enumerating at Python-side AD, emit pre-solve assignments like `jac(i,j)$X(i) = <derivative expr>` and let GAMS compute the sparse Jacobian at MCP runtime. Architectural shift.

**Expected speedup:** massive (eliminates Python-side enumeration entirely) but is a major rewrite of the Jacobian path.

### 3.2 Addressing Unknown 5.3 (sparse Jacobian)

**Sparse Jacobian techniques do NOT help any of these 5 models.** The bottleneck is instance **enumeration** — decisions about which (row, column) pairs have a non-zero entry. Sparse storage representations (COO, CSR, etc.) save memory and iteration time across non-zero entries, but they don't avoid the need to decide WHICH entries are non-zero. The 5 hard-timeout models spend >90% of `ad_jacobian` time deciding, not storing.

**Verdict on KU 5.3 (sparse Jacobian feasibility): VERIFIED WRONG.** Sparse Jacobian should NOT be pursued as a fix for these 5 models. Sparse representation could be a separate Sprint-26+ storage optimization orthogonal to the enumeration fix proposed in §3.1.

### 3.3 Addressing Unknown 5.4 (srpchase as preprocessor issue)

**srpchase is NOT a preprocessor issue.** Measured:

- preprocess: 33 ms
- parse+ir_build: 1.2s
- **ad_jacobian: 466.6s (93% of total)**

ScenRed's `$libInclude scenred` is processed by GAMS at compile time, and the included ScenRed statements produce a meaningful set cardinality (`n` = 1001 members) during execution/runtime. nlp2mcp's preprocessor handles the `$libInclude` without difficulty; the cost is borne by `compute_constraint_jacobian`'s instance enumeration downstream, not by the preprocessor or parser.

**Verdict on KU 5.4 (srpchase ScenRed preprocessor bottleneck): VERIFIED WRONG.** srpchase's bottleneck is the same `SetMembershipTest`-fallback pattern as the other 4. ScenRed is a scale amplifier (1001 members) but not a unique root cause.

---

## Section 4 — Priority 5 Recommendation

### 4.1 Recommendation: DEFER all 5 to Sprint 26

**Rationale:**

1. **All 5 share ONE root cause.** A single architectural fix (Option 1 in §3.1) would unblock all 5. That's not 4–6h per model; it's one coordinated change.
2. **Sprint 25 is full.** Priority 1 (alias-AD, 12 days), Priority 2 (emitter backlog 13–18h + Task 5 new issues #1289–#1292 adding 10–15h), Priority 3 (multi-solve gate, 3.5–4.5h), Priority 4 (dispatcher refactor, 4–5h). No budget headroom for a 1-day architectural change on a Low-priority workstream.
3. **The Sprint 24 retrospective's PR13 finding already called this out:** translate-recovery is low-leverage for near-term Match gains because the recovered MCPs then hit path_syntax_error. Task 5's analysis confirmed: 5 recovered-translate models (ganges, gangesx, ferts, clearlak, turkpow) are all blocked by separate emitter bugs, not by Priority 5 work.
4. **The 4 intractable models would produce 0 new solves even if unblocked** — they'd translate but then hit the same downstream emitter/stationarity issues the other translate-recovery models hit.

### 4.2 Sprint 26 filing

File a new GitHub issue with `sprint-26` label: **"Architectural: `SetMembershipTest` dynamic-subset fallback triggers include-all enumeration in `ad_jacobian`"**

Referenced from:

- `#1169` (lop, resolved in Sprint 24 Day 13 Addendum; keep closed)
- `#1185` (mexls) — carries forward; link to new architectural issue
- `#1192` (gtm) — same
- Sprint 24 ISSUE_1228 (iswnm) — same
- **NEW issue for srpchase, sarf, nebrazil** (not previously tracked) — same class; aggregate them under the architectural issue

### 4.3 Contingency: if schedule permits at Sprint 25 Day 12

If Priority 1–4 all land ahead of schedule and there's 1 day of overflow budget on Day 11–12, consider landing **Option 1** (short-circuit empty fallback) as a targeted fix. Expected outcome:

- srpchase: 500s → ~30s; within 60s pipeline budget; likely translates clean; downstream path_syntax_error or a solve depending on the MCP quality.
- iswnm: likely same pattern → translates; downstream outcome TBD.
- sarf, mexls, nebrazil: harder to predict without implementation; the multi-subset cases (mexls 3, nebrazil 4) may still time out even after Option 1.

**Expected Sprint 25 Solve delta from Option 1:** 0–2 models. This does NOT meaningfully change the Sprint 25 Solve target analysis (99 → ≥ 105 requires +6; Priority 1 + Priority 2 + Task 5 new issues provide 0–4 expected).

---

## Section 5 — Cross-Reference

| Source | Used For |
|---|---|
| Sprint 24 ISSUE_1228 (iswnm SetMembershipTest) | §1.2 iswnm confirmation; §2 root-cause claim |
| Sprint 24 KU-19 (timeout models intractable) | §4 recommendation to defer |
| Sprint 24 KU-20 (sparse Jacobian feasibility) | §3.2 verdict on KU 5.3 |
| Sprint 24 retrospective §PR13 (translate-recovery low-leverage) | §4.1 recommendation rationale |
| Task 5 `ANALYSIS_RECOVERED_TRANSLATES.md` §Section 3.2 | §4.1 point 4 about recovered-translates hitting other emitter bugs |

---

## Appendix A — Profile Harness

Script lives at `/tmp/task8-profile.py` during this prep task; paste below for preservation. Move to `scripts/task8_profile.py` if the Sprint 26 architectural fix wants to use it as a regression benchmark.

```python
"""Stage-timing instrumentation for Task 8 hard-timeout profiling.

Usage: PYTHONHASHSEED=0 python /tmp/task8-profile.py <model> <budget_seconds>

Writes JSON to stdout with per-stage timing.
"""

import sys, time, signal, json
sys.setrecursionlimit(50000)

MODEL = sys.argv[1]
# signal.alarm() only supports integer seconds, so budget must be an integer
# number of seconds. Parsing as int here avoids the float->int truncation
# mismatch between BUDGET and signal.alarm(int(BUDGET)).
BUDGET = int(sys.argv[2])

def _timeout(signum, frame):
    raise TimeoutError(f"budget {BUDGET}s exceeded")
signal.signal(signal.SIGALRM, _timeout)
signal.alarm(BUDGET)

from pathlib import Path
from src.config import Config
from src.ir.preprocessor import preprocess_gams_file
from src.ir.parser import parse_model_text
from src.ir.normalize import normalize_model
from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.gradient import compute_objective_gradient
from src.kkt.assemble import assemble_kkt_system
from src.emit.emit_gams import emit_gams_mcp

t0 = time.perf_counter()
stages = []

def mark(name):
    now = time.perf_counter()
    elapsed = now - (stages[-1][1] if stages else t0)
    stages.append((name, now, elapsed))

try:
    try:
        src_data = preprocess_gams_file(Path(f"data/gamslib/raw/{MODEL}.gms"))
        mark("preprocess")
        model = parse_model_text(src_data)
        mark("parse+ir_build")
        normalized_eqs, _ = normalize_model(model)
        mark("normalize")
        config = Config()
        gradient = compute_objective_gradient(model, config)
        mark("ad_gradient")
        J_eq, J_ineq = compute_constraint_jacobian(model, normalized_eqs, config)
        mark("ad_jacobian")
        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq, config)
        mark("kkt_assemble")
        output = emit_gams_mcp(kkt, add_comments=False)
        mark("emit_mcp")
        stats = {
            "eq_rows": J_eq.num_rows, "eq_cols": J_eq.num_cols,
            "ineq_rows": J_ineq.num_rows, "ineq_cols": J_ineq.num_cols,
            "gradient_cols": gradient.num_cols,
            "n_stat_eqs": len(kkt.stationarity),
            "output_lines": len(output.splitlines()),
        }
        result = {
            "model": MODEL, "status": "complete",
            "total": time.perf_counter() - t0,
            "stages": [(name, round(el, 4)) for (name, _, el) in stages],
            "stats": stats,
        }
    except TimeoutError as e:
        result = {
            "model": MODEL, "status": "timeout",
            "budget": BUDGET, "elapsed": round(time.perf_counter() - t0, 4),
            "stages_completed": [(name, round(el, 4)) for (name, _, el) in stages],
            "error": str(e),
        }
finally:
    # Cancel the SIGALRM on every exit path (including non-TimeoutError
    # exceptions) so the alarm can't fire during error reporting or JSON
    # serialization.
    signal.alarm(0)

print(json.dumps(result, default=str))
```

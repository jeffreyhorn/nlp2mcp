# Audit — Alias-AD Carryforward State

**Created:** 2026-04-19
**Sprint:** 25 (Prep Task 2)
**Predecessors:** `SPRINT_24/ANALYSIS_ALIAS_DIFFERENTIATION.md`, `SPRINT_24/DESIGN_ALIAS_DIFFERENTIATION_V2.md`
**Data sources:** `data/gamslib/gamslib_status.json` (Day 13 Addendum snapshot, 2026-04-19), `src/ad/derivative_rules.py`, `src/kkt/stationarity.py`, `SPRINT_24/SPRINT_LOG.md` Days 1–10

---

## Executive Summary

Sprint 23 landed the full `bound_indices`/`_alias_match`/`_same_root_set` threading design. Sprint 24 added a narrower set of post-processing helpers (`_apply_alias_offset_to_deriv`, `_var_inside_alias_sum`, single-index-sum collapse fix, concrete-element IndexOffset base rewrite) that recovered 3 models from `path_syntax_error` (polygon, catmix, cclinpts), stabilized dispatch under narrowed guards, and resolved qabel/abel compilation, but did **not** close out the derivative-mathematics bug for any of the 11 open alias-AD tracking issues.

After re-running reproductions against the current parser/AD/emitter state (Day 13 Addendum), the 11 open issues split cleanly into a smaller Pattern surface than Sprint 24 projected:

- **Pattern A** (summation-index tracked through derivative chain): **6 issues / 15 models** — dominant.
- **Pattern C** (offset + alias interaction, derivative-math subset): **2 issues / 2 models**.
- **Pattern E** (non-differentiation — IR domain, multi-solve semantics, or infeasibility-adjacent): **3 issues / 3 models** — won't be fixed by the alias-AD work.
- **Pattern B** and **Pattern D** as defined in Sprint 24 are now empty — `#1141 kand` reclassifies to Pattern E (multi-solve semantics, not AD) and `#1142 launch` reclassifies to Pattern A (alias-family per Day 9 investigation).

**Implication for Sprint 25 Priority 1 scope:** one architectural patch to the summation-context / partial-collapse path resolves the 6 Pattern A issues; a small `IndexOffset.base` extension (2–3h) resolves Pattern C. Patterns B/D collapsing to zero shrinks the investigation surface from "4 distinct patterns" to "2 active patterns + 3 unrelated issues to route elsewhere." The original Sprint 25 `Match 54 → ≥62` target (+8) is built around this 8-issue workable scope (6 A + 2 C) with a ≤1 regression tolerance.

**Regression surface:** 10 of the 54 matching models use aliases (up from Sprint 23's count of 8 — `nemhaus` is now MINLP-excluded, replaced by `partssupply`, `prolog`, `sparta` entering the matching set during Sprint 24). Dispatch remains the primary canary; Sprint 24's secondary canaries (quocge, marco, paklive) are re-validated — marco is no longer in the matching set (irrelevant), quocge + paklive remain in-set.

---

## Section 1 — Sprint 24 Landed vs. Stubbed Inventory

### Landed in Sprint 23 (still in place)

| Component | File:Line | Status |
|---|---|---|
| `bound_indices` keyword-only parameter | `src/ad/derivative_rules.py:74` | ✅ Live — threaded through all 20+ dispatch targets |
| Threading through every `_diff_*` handler | `src/ad/derivative_rules.py:138–168` | ✅ Live |
| `_same_root_set()` — cycle-safe alias chain resolver | `src/ad/derivative_rules.py:262–279` | ✅ Live |
| `_alias_match()` — emits `sameas(...)` guard on alias match, `Const(1)` on exact, `None` on miss | `src/ad/derivative_rules.py:282–338` | ✅ Live |
| `_diff_varref()` alias fallback when exact match fails | `src/ad/derivative_rules.py:339–436` (call at 428) | ✅ Live |
| `_diff_sum()` augments `bound_indices` with its own `index_sets` on normal path | `src/ad/derivative_rules.py:2028` | ✅ Live |
| `_partial_collapse_sum()` alias-aware matching | `src/ad/derivative_rules.py:2173+` | ✅ Live |

### Added in Sprint 24 (landed and still in place)

| Component | File:Line | What it does | Motivated by |
|---|---|---|---|
| `_collect_bound_indices()` helper | `src/ad/derivative_rules.py:238–245` | Walks expression tree to collect all Sum/Prod iteration indices — used by single-index collapse path to avoid converting concrete→symbolic if target would shadow a bound index | Day 5 regression fix (marco, paklive) |
| `_find_var_indices_in_body()` helper | `src/ad/derivative_rules.py:248–259` | Finds all `VarRef(var_name)` index tuples in an expression — guides concrete→symbolic index conversion | Day 3 (single-index sum collapse) |
| Single-index sum collapse: concrete→symbolic conversion for remaining wrt indices | `src/ad/derivative_rules.py:1911–1989` (Issue #1111 path) | When `sum(np, a(n,np)*x(np,k))` w.r.t. `x(consumpt,q1)` is differentiated, remaining concrete wrt indices (`consumpt`, `q1`) are converted back to their symbolic free-set names (`n`, `k`) if a body VarRef uses that free index. Prevents collapse to 0. Skips bound indices. | Day 3 (qabel/meanvar cross-terms) |
| `_apply_alias_offset_to_deriv()` | `src/kkt/stationarity.py:1743–1845` | Rewrites `ParamRef(a, (n, n))` → `ParamRef(a, (IndexOffset(np, 1), n))` for alias cross-terms when the offset group carries an offset, using the declared param domain and a preferred alias lookup to avoid GAMS Error 125 | Day 4 (qabel `a(n+1,n)` → `a(np+1,n)`) |
| `_body_has_alias_sum()` | `src/kkt/stationarity.py:1858–1867` | Coarse filter: does constraint body contain any Sum indexed by an alias? | Day 4 |
| `_var_inside_alias_sum()` + `_var_has_alias_coindex()` | `src/kkt/stationarity.py:1870–1912` | Narrow filter: does target variable sit *inside* an alias-indexed sum as a cross-term (alias index + at least one other index)? Distinguishes qabel `sum(np, a(n,np)*x(np,k))` (True for `x`) from quocge `sum(j, RT(j))` (False for `RT` → no spurious guard) | Day 5 regression fix (quocge, marco, paklive) |
| Per-constraint memoization: `_alias_sum_cache`, `_body_sum_aliases_cache`, `_root_offsets`, `_off_map`, `_pref` | `src/kkt/stationarity.py:4340–4422` | Avoids O(eq × var) reclassification and multi-position offset ambiguity | Day 4–5 |
| `_replace_indices_in_expr` IndexOffset.base canonicalization | `src/kkt/stationarity.py` (Day 6) | Maps `IndexOffset("i1", Const(1))` (concrete element base) → `IndexOffset("i", Const(1))` (declared set base) for VarRef/ParamRef in `has_linear_offset` path, with `element_to_set` fallback | Day 6 (polygon, catmix, cclinpts compile) |

### Stubbed / Not Landed (architecturally open in Sprint 24)

| Gap | Intended Fix Site | Why Not Landed | Sprint 25 Task |
|---|---|---|---|
| **Multi-index partial-collapse** concrete→symbolic conversion | `_partial_collapse_sum()` in `src/ad/derivative_rules.py` | Day 3's concrete→symbolic fix applies only to the *single-index* collapse path (`len(expr.index_sets) == 1`). The multi-index path (`_partial_collapse_sum`) has its own enumeration/match logic and does not apply the same `_find_var_indices_in_body`-guided free-index recovery. Sprint 24 Day 3 noted this explicitly. | Priority 1 Day 1–3 |
| **`IndexOffset.base` extraction in `_alias_match`** | `src/ad/derivative_rules.py:304–307` | Current `_alias_match()` requires IndexOffset structural equality (`expr_idx == wrt_idx`) and returns `None` on any mixed `str`/`IndexOffset` pair. Pattern C (polygon, himmel16) needs: `_same_root_set(expr_idx.base, wrt_idx, aliases)` → emit an offset-aware guard. Scaffold exists in `DESIGN_ALIAS_DIFFERENTIATION_V2.md` §Pattern C. | Priority 1 Day 5–7 |
| **Full Jacobian-transpose assembly rewrite** | `_add_indexed_jacobian_terms` + single-representative-instance logic in `build_stationarity_equations` (`src/kkt/stationarity.py`) | Sprint 24 Day 1–2 identified the root cause: picking one representative constraint instance and generalizing loses alias cross-terms for constraint instances not represented by the chosen example. Day 3–4 added post-hoc `_apply_alias_offset_to_deriv` patches that work for qabel/abel (single-index, single-alias). CGE and PS-family models use multi-index sums that this patch doesn't handle — the patch happens post-differentiation rather than inside the assembly. Day 5 Checkpoint narrowed the guard rather than fixing the assembly. | Priority 1 Day 3–7 (scope TBD by Task 6) |
| **Condition-scope alias threading** (original Pattern D) | `_diff_dollar_conditional` in `src/ad/derivative_rules.py` | Never investigated — launch (#1142) was reclassified on Day 9 to Pattern A (alias-family), so the original Pattern D motivator is gone. | Closed as Pattern D (empty) |
| **Multi-level alias nesting** (original Pattern B) | `_same_root_set` for chained aliases | Never investigated — kand (#1141) was reclassified on Day 9 to Pattern E (multi-solve comparison bug, not AD). | Closed as Pattern B (empty) |

---

## Section 2 — Pattern Classification Table (11 Open Issues)

Classification columns: "S24 Pattern" is the original Sprint 24 Prep analysis; "S25 Revised" is this audit's current-state finding after Sprint 24 fixes landed + Day 9 investigations.

| Issue | Model(s) | S24 Pattern | S25 Revised | Current State (pipeline) | Rel. Diff | Notes |
|---|---|---|---|---|---|---|
| #1138 | irscge, lrgcge, moncge, stdcge | A | **A** | translate✅ / solve✅ / compare=mismatch (all 4) | 1.0–2.2% | Tight mismatches; classic CGE alias cross-terms |
| #1139 | meanvar | A | **A** | `pipeline_status: legacy_excluded` (as of 2026-04-16) | — | Still useful as *offline* test model; exclude from canary set |
| #1140 | ps2_s, ps3_s, ps3_s_gic, ps3_s_mn, ps5_s_mn, ps10_s_mn | A | **A** | translate✅ / solve✅ / compare=mismatch or skipped | 0.5–9.1% | ps5_s_mn/ps10_s_mn comparison=skipped (pipeline skips large PS variants) |
| #1141 | kand | B | **E** ⚠ reclassified | translate✅ / solve✅ / compare=mismatch | 92.5% | **Not an alias-AD bug.** Day 9 investigation (#1225): kand has two models (kand, kandsp); nlp2mcp reformulates the last solve (kandsp) but the NLP comparison uses the first model. Multi-solve semantics — fix belongs in the pipeline comparator or the multi-solve gate, not AD. |
| #1142 | launch | D | **A** ⚠ reclassified | translate✅ / solve✅ / compare=mismatch | 17.3% | **Reclassified from Pattern D → Pattern A.** Day 9 (#1226): launch uses `Alias(s,ss)`; Jacobian/stationarity bug is in the same family as other CGE/alias models. The original "condition-scope" Pattern D framing was a misdiagnosis. |
| #1143 | polygon | C | **C** | translate✅ / solve✅ / compare=mismatch | 33.8% | Day 6 fixed the compile error (concrete `i1+1` → `i+1`). Derivative math still broken — complete 100% gradient failure at `theta(i+1)*r(i+1)*r(i)` → needs `IndexOffset.base` extraction in `_alias_match`. |
| #1144 | catmix | E | **E** | translate✅ / solve✅ / compare=mismatch | 0.2% | Day 6 fixed compile error (catmix `IndexOffset("0", 1)` → `IndexOffset("nh", 1)`). Remaining 0.2% is IR-level domain inference, not AD. Near-match; could qualify at a wider tolerance. |
| #1145 | cclinpts | A | **A** | translate✅ / solve✅ / compare=mismatch | **100%** | Day 6 fixed compile error. Now solves but objective is the wrong sign/scale — likely the multi-index partial-collapse gap (see stubbed row in §1). |
| #1146 | himmel16 | C | **C** | translate✅ / solve✅ / compare=mismatch | 43.0% | Circular offset (`++`) with alias interaction. Same fix site as polygon. |
| #1147 | camshape | E | **E→A-adjacent** | translate✅ / solve=failure (model_infeasible, status 5) | — | Day 6 fixed compile error. Now **translates + reaches PATH**, but PATH returns Locally Infeasible. Sprint 24 Day 13 listed as "alias-related infeasibility." If Pattern A fix lands, the Jacobian accuracy may change enough to make the problem feasible — but separate to confirm post-fix. |
| #1150 | qabel, abel | A | **A** | translate✅ / solve✅ / compare=mismatch | 8.2% / 29.8% | qabel is the Day 3/Day 4 lead model; compile is fixed, math still off. abel is the "abel-family" companion; Day 4 landed the `a(np+1,n)` fix for qabel/abel specifically. Residual mismatch suggests the single-index path doesn't cover all PS-family assembly cases. |

### Revised Pattern Distribution

| Pattern | S24 Count | S25 Count | Issues | Models |
|---|---|---|---|---|
| **A** (summation index) | 6 | **6** | #1138, #1139, #1140, #1142, #1145, #1150 | ~15 |
| **B** (root-set tree) | 1 | **0** | — | — |
| **C** (offset + alias) | 2 | **2** | #1143, #1146 | 2 |
| **D** (condition-scope) | 1 | **0** | — | — |
| **E** (non-differentiation) | 2 | **3** | #1141, #1144, #1147 | 3 |

**Shift summary:** Pattern B and D empty; Pattern E +1 (kand joins catmix + camshape). Pattern A unchanged in count but now absorbs launch (previously D). Pattern C unchanged.

---

## Section 3 — Pattern → Architectural Fix Site Map

### Pattern A (6 issues, ~15 models) → Primary fix site

**Symptom:** Constraint body contains `sum(alias, coefficient(n, alias)*x(alias, k))`. Differentiating w.r.t. `x(concrete_i, concrete_k)` must produce `coefficient(n, concrete_i)` at the correct offset position, but currently produces 0 or an incorrect symbolic term for the cross-term instances.

**Fix sites (in priority order):**

1. **`_partial_collapse_sum()`** (`src/ad/derivative_rules.py:2173+`) — extend the multi-index partial-collapse path with the Day 3 single-index concrete→symbolic logic (`_find_var_indices_in_body` + bound-index guard). This is the biggest gap left from Sprint 24 and the most likely root cause for CGE + PS-family mismatches.
2. **`_diff_sum()` normal path** (`src/ad/derivative_rules.py:2025–2034`) — already augments bound_indices correctly; no change expected.
3. **`_apply_alias_offset_to_deriv()` in stationarity** (`src/kkt/stationarity.py:1743`) — currently handles single-alias, single-offset-position case. Extend to multi-position offsets (currently skipped at line 4389 when multiple sets resolve to the same root with different offsets).
4. **Jacobian assembly rewrite** (`build_stationarity_equations`) — the deeper representative-instance-based assembly issue. Out of scope for the first fix round; revisit in Sprint 25 Phase 2 or defer.

**Dependencies within Pattern A:**
- qabel/abel (#1150) → tests the single-index path (already largely working post-Sprint 24).
- CGE family (#1138) → tests the multi-index `_partial_collapse_sum` path.
- PS-family (#1140) → tests the multi-index + multi-position offset case.
- meanvar (#1139) → quadratic transpose; tests multi-alias cross-term enumeration. **Offline only** (pipeline-excluded).
- launch (#1142) → single-alias `Alias(s,ss)`, simpler; good early-validation canary.
- cclinpts (#1145) → 100% mismatch, so a tight post-fix signal (either recovers or doesn't).

### Pattern C (2 issues, 2 models) → Secondary fix site

**Symptom:** `_alias_match()` returns `None` when either side is an `IndexOffset` but the other is a plain string. Structural equality is overly strict for the alias case.

**Fix site:** `src/ad/derivative_rules.py:304–307`. Extend to:

```python
if isinstance(expr_idx, IndexOffset) and isinstance(wrt_idx, str):
    if _same_root_set(expr_idx.base, wrt_idx, aliases):
        # Free alias variable with offset: emit offset-aware guard
        # e.g., sameas(expr_idx.base + offset, wrt_idx)
        ...
# (and symmetric case for wrt_idx being IndexOffset)
```

**Note:** the Sprint 24 Day 6 IndexOffset.base canonicalization is in the *emitter* (`_replace_indices_in_expr`); this proposed Pattern C extension is in the *differentiator* (`_alias_match`). They're separate code paths.

**Dependency:** Pattern C **depends on Pattern A** — Pattern A must land first so the derivative chain reaches `_alias_match` correctly for the offset case. Pattern C without Pattern A won't fix polygon because the upstream collapse is also broken.

### Pattern B (0 issues) → Closed — reclassified

Originally proposed for kand (#1141) based on its tree/hierarchical alias usage. Day 9 investigation (#1225) determined kand's mismatch is a multi-solve comparison semantics issue (comparator targets first-solved model while nlp2mcp reformulates last-solved), not a `_same_root_set` tree-traversal bug. No AD fix needed at this site. The `_same_root_set` cycle-safe resolver from Sprint 23 is already correct for multi-level alias chains to the extent any 11-issue model exercises it.

### Pattern D (0 issues) → Closed — reclassified

Originally proposed for launch (#1142) based on dollar-conditional alias scoping. Day 9 investigation (#1226) determined launch's mismatch is a standard alias Jacobian/stationarity bug in the same family as CGE models. Reclassified to Pattern A. The `_diff_dollar_conditional` bound_indices threading is already correct; no condition-scope-specific work is needed in Sprint 25.

### Pattern E (3 issues, 3 models) → Route out of alias-AD scope

- **#1141 kand** → routes to **Priority 3 (Multi-solve gate extension, #1270)** or the pipeline comparator; the gate currently catches saras-style top-level marginal feedback as the dominant saras-style case, but kand's two-model-but-same-ish-structure pattern is a different variant of "which solve is the comparison target?". Not a Sprint 25 Priority 1 item.
- **#1144 catmix** → IR-level domain inference bug (per Sprint 24 Day 6 notes). Separate investigation; not blocked by alias-AD. 0.2% mismatch is near-match and may close under a wider tolerance threshold.
- **#1147 camshape** → post-Day-6 state is `model_infeasible`; recovery depends on whether Pattern A fix changes Jacobian accuracy enough for PATH to find a feasible start. **Re-evaluate after Pattern A lands**; if still infeasible, route to the same "PATH convergence / Category B" bucket as agreste/chain/fawley/lnts/robustlp.

### Subsumed-By Relationships

| Fixed First | Subsumes | Rationale |
|---|---|---|
| Pattern A fix | #1138, #1139 (offline), #1140, #1142, #1145, #1150 | All currently attribute mismatch to the same upstream gap (`_partial_collapse_sum` multi-index case). |
| Pattern A + C fixes | #1143, #1146 | Pattern C needs Pattern A upstream. |
| Pattern A (+ luck) | #1147 | Only if Jacobian accuracy delta is enough to reach feasibility. Not guaranteed. |
| **Unrelated**: | #1141, #1144 | Neither is fixed by alias-AD; track in Priority 3 / IR workstreams. |

---

## Section 4 — Regression Risk Assessment

### Alias Users Among the 54 Currently-Matching Models

Re-verified against `data/gamslib/raw/*.gms` (`\balias\s*\(` case-insensitive). **10 matching models** use aliases (up from Sprint 23's 8):

| Model | S23 Canary? | S25 Role |
|---|---|---|
| dispatch | ✅ Yes | **Primary canary** (non-negotiable) — `sum((i,j), p(i)*b(i,j)*p(j))` is the exact regression class the `bound_indices` guard was designed for |
| gussrisk | ✅ Yes | Secondary canary |
| partssupply | New (Sprint 24) | Secondary canary — joined matching set after Sprint 24 `$ifThen` fix |
| prolog | New (Sprint 24) | Secondary canary — joined matching set after Sprint 24 multiplier-dimension fix |
| ps2_f | ✅ Yes | Secondary canary |
| ps3_f | ✅ Yes | Secondary canary |
| quocge | ✅ Yes | **Regression-sensitive canary** — Sprint 24 Day 5 Checkpoint 1 regressed this; fix was the `_var_inside_alias_sum` co-index guard |
| ship | ✅ Yes | Secondary canary |
| sparta | New (Sprint 24) | Secondary canary |
| splcge | ✅ Yes | Secondary canary |

**Dropped from S23 canary list:** `nemhaus` (now MINLP-excluded via v2.2.0 migration; no longer in pipeline scope).

**Dropped regression candidates from S24 Day 5:** `marco` (no longer in matching set — now in `path_syntax_error` or similar; check status to confirm which).

### 41 Non-Alias Matching Models

The remaining 44 (= 54 − 10) matching models don't use aliases, so the alias-AD code path is unreachable by design. Risk of regression is near-zero for this subset, consistent with Sprint 24's Day 5 experience (regressions were confined to the alias-using matching models).

### Risk Level: LOW

- Code path isolated: alias-AD changes only touch `_alias_match`, `_partial_collapse_sum`, and `_apply_alias_offset_to_deriv`. None are reachable without an alias declaration in the source IR.
- `bound_indices` guard is Sprint 23-era and has survived Sprint 24's churn — extending Pattern C via `IndexOffset.base` still respects the guard.
- **Budget:** ≤1 regression tolerated (still yields net +7 toward Match ≥62 target); ≥2 regressions trigger Task 6's "stop the sprint" procedure.

---

## Section 5 — Canary-Test Priority Ladder

**Tier 0 — Smoke (non-negotiable, must pass before any subsequent test):**

1. `dispatch` — guards `bound_indices`; Sprint 22 regression signature; must produce identical stationarity to pre-fix (trivial newline diff OK).

**Tier 1 — Alias-using matching models (run all 9 after Tier 0):**

2. `quocge` — regressed + re-fixed in S24 Day 5; most sensitive canary in the set.
3. `paklive` — regressed + re-fixed in S24 Day 5 via `_collect_bound_indices`. (Not alias-using itself, but was caught up in Day 5 bound-index fix — included defensively.)
4. `partssupply` — new matching model; verify S24 `$ifThen` fix remains matched.
5. `prolog` — new matching model with alias; verify S24 multiplier-dimension fix holds.
6. `sparta`, `gussrisk`, `ps2_f`, `ps3_f`, `ship`, `splcge` — remaining alias users.

**Tier 2 — Golden-file regression across the 44 non-alias matching models:**

7. Generate pre-fix stationarity output for all 44 (reuse `/tmp/gamslib-golden/` mechanism from S24 Day 0).
8. Post-fix: diff each. Expected: identical for all 44 (alias code path unreachable). Any diff is a false positive in the fix's scope and needs investigation before merge.

**Tier 3 — Pattern-A validation (target issues):**

9. `qabel`, `abel` — single-alias baseline (S24 Day 4 fix still applies).
10. `launch` — single-alias `Alias(s,ss)`; smaller CGE than irscge. Fast validation canary for Pattern A on CGE-like model.
11. `irscge` — tightest CGE mismatch (2.2%); best signal on whether CGE cross-terms resolve.
12. `cclinpts` — 100% mismatch; binary pass/fail signal.

**Tier 4 — Pattern-C validation (after Tier 3 passes):**

13. `polygon` — 100% gradient failure; `IndexOffset.base` extraction target.
14. `himmel16` — circular offset; same fix site, different offset style.

**Tier 5 — Adjacent / infeasibility canaries (informational only; no block on regression):**

15. `cesam`, `korcge`, `camshape` — Sprint 24 Day 13 "alias-related infeasibility." Expected to recover once Pattern A lands, but recovery is not a Sprint 25 Priority 1 gate.

---

## Section 6 — Cross-Reference to Sprint 24 KUs

| S24 KU | S24 Content | S25 Carryforward Mapping |
|---|---|---|
| **KU-01** (Pattern A summation-context) | VERIFIED in S24: need `_alias_match` + bound threading; architecture landed S23 | Confirmed still valid; the missing piece is the *multi-index partial-collapse* free-index recovery (not `_alias_match` itself) |
| **KU-04** (Pattern C offset-alias, 55–65% success) | "the `_alias_match()` helper needs to extract `IndexOffset.base`" | Reaffirmed; Pattern A prerequisite now explicit |
| **KU-13** (influx risk for alias fix) | S24 Day 13 Addendum measured 100% influx for translate-recovery; alias-AD influx not measured separately | Unknown 1.2 budget: ≤1 regression; ≥2 triggers stop-the-sprint |
| **KU-17** (infeasibility influx) | S24 Day 13: 3 alias-related infeasibles (camshape, cesam, korcge) | Priority 1 success probability estimate: camshape 40%, cesam 40%, korcge 35% (Pattern A fix changes Jacobian numerics; can't predict PATH feasibility deterministically) |

**Note on KU-32 (sameas guard validation):** tracked under Unknown 1.5 in `SPRINT_25/KNOWN_UNKNOWNS.md`, verified by Task 6 (rollout design) — not in scope for this audit, which focuses on carryforward state rather than guard-emission correctness.

---

## Section 7 — Open Questions for Task 6 (Rollout Design)

This audit deliberately stops at classification and fix-site mapping. The following decisions belong to **Task 6 (Alias-AD Rollout Design)** and are noted here as inputs:

1. **Phase split:** should Pattern A (6 issues) and Pattern C (2 issues) be a single PR or two? Task 6 should decide based on Jacobian-assembly scope.
2. **Checkpoint gates:** Day 3 (Pattern A canary-only), Day 5 (Tier 1 full), Day 7 (Tier 2 golden files), Day 9 (Tier 3/4 target models). Exact criteria TBD.
3. **Rollback procedure:** feature-flag vs. git revert. Unknown 1.8 assumes "all-or-nothing with git revert" given pervasive code paths; Task 6 to confirm.
4. **camshape decision:** re-classify as Pattern E or retry as Pattern A adjacent after the fix lands? This is a post-fix empirical call.
5. **#1141 kand routing:** close as "not an alias bug, route to #1270 family" vs. file a new issue.

---

## Appendix A — Data Collection Script

Status-JSON re-extraction used for Section 2's "Current State" column:

```python
import json
with open('data/gamslib/gamslib_status.json') as f:
    data = json.load(f)
targets = {
    '#1138': ['irscge','lrgcge','moncge','stdcge'],
    '#1139': ['meanvar'],
    '#1140': ['ps2_s','ps3_s','ps3_s_gic','ps3_s_mn','ps5_s_mn','ps10_s_mn'],
    '#1141': ['kand'], '#1142': ['launch'], '#1143': ['polygon'],
    '#1144': ['catmix'], '#1145': ['cclinpts'], '#1146': ['himmel16'],
    '#1147': ['camshape'], '#1150': ['qabel','abel'],
}
by_id = {m.get('model_id','').lower(): m for m in data.get('models', [])}
for issue, models in targets.items():
    for m in models:
        e = by_id.get(m.lower(), {})
        t = (e.get('nlp2mcp_translate') or {}).get('status')
        s = (e.get('mcp_solve') or {}).get('status')
        c = (e.get('solution_comparison') or {}).get('comparison_status')
        rd = (e.get('solution_comparison') or {}).get('relative_difference')
        print(f'{issue} {m}: translate={t} solve={s} compare={c} rd={rd}')
```

## Appendix B — Alias-User Detection Script (for Tier 1/2 canary list)

```python
import re
from pathlib import Path
matching = [...]  # 54 models from solution_comparison.comparison_status == 'match'
alias_re = re.compile(r'\balias\s*\(', re.IGNORECASE)
for m in matching:
    p = Path(f'data/gamslib/raw/{m}.gms')
    if p.exists() and alias_re.search(p.read_text(errors='ignore')):
        print(m)
```

Re-run both scripts at the start of Sprint 25 Day 1 to confirm no drift from this audit's Day 13 Addendum snapshot.

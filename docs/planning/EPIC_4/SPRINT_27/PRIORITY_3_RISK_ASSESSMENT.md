# Sprint 27 Priority 3 AD Architectural Redesigns Risk Assessment (PR16 Hypothesis Validation)

**Status:** ✅ COMPLETE (Day 0 prep — experiment designs ready; binding verdicts pending Sprint 27 Day 0/1 prototype execution per the "scheduled for Day 0" outcome explicitly permitted by Task 6 prompt)
**Date:** 2026-05-28
**Owner:** Prep Task 6
**Inputs:** PROJECT_PLAN.md §Sprint 27 Priority 3 (30–48h budget); ISSUE_1390 / ISSUE_1385 / ISSUE_1393 / ISSUE_1335 issue docs; Sprint 26 Day 9 SPRINT_LOG (3-approach enumeration for #1335); Sprint 25 DAY5_PATTERN_A_INVESTIGATION.md (PR16 methodology); source code: `src/ad/constraint_jacobian.py:903,1027`, `src/ad/derivative_rules.py:2556,2607`, `src/ad/index_mapping.py:377`, `src/kkt/stationarity.py`.

---

## 1. Purpose

This document applies the **Sprint 25 Day 5 hypothesis-validation methodology** (codified as Sprint 25 retrospective recommendation **PR16**) to the 3 Priority 3 AD architectural redesigns slated for Sprint 27 — **#1390 kand per-instance enumeration**, **#1385 Option 1 short-circuit**, **#1393 + #1335 scalar-eq Sum-collapse** — BEFORE Sprint 27 commits the **30–48h Priority 3 budget**. For each redesign it records:

- The **central architectural hypothesis** (a single falsifiable claim).
- The **validation experiment design** (~30–90 min Sprint 27 Day 0 execution): patch site, prototype patch shape, regeneration command, per-term grep verification, hand-derived KKT comparison, PATH-solve check where applicable.
- The **PROCEED / REPLAN criteria** (explicit, binary).
- The **tentative verdict** based on hand-derived architectural analysis (this prep authoring). The **binding verdict** is produced by Sprint 27 Day 0 prototype execution.

It also records:

- The **coordinated-design analysis** (KU-38 resolution): pair-wise architectural-overlap assessment + serial-vs-coordinated implementation recommendation.
- The **#1335 approach selection** (KU-39 resolution): which of the 3 documented approaches Sprint 27 commits to.
- The **Phase 0 binary-signal criteria** (KU 3.5 resolution).

**Why this matters:** Sprint 26 produced 5 architectural reclassifications (Days 1, 3, 4, 7, 9) — each shipped GREEN through unit/integration/byte-stability gates but introduced subtle math-correctness regressions caught only by Copilot reviewer hand-derived KKT comparison. **Unit tests, integration tests, and byte-stability gates cannot catch AD/KKT pipeline architectural-drift regressions.** The Sprint 25 PR16 methodology — hand-derive expected shape, regenerate, byte-compare against expectation — is the only reliable filter. Task 6 applies this PR16 filter to each Priority 3 redesign BEFORE the 30–48h budget commits.

**Execution model:** All 3 validation experiments are **DESIGN-READY** with concrete patch sites, prototype commands, regeneration commands, and grep-based verification specifications. The experiments are **SCHEDULED FOR SPRINT 27 DAY 0** (Priority 3 entry gate per Task 11 schedule). Day 0 engineer executes each experiment in turn (~30–90 min each, ~3h cumulative); each produces a binding PROCEED / REPLAN signal per the criteria below. This document's tentative verdicts are **hand-derived architectural-analysis projections** (not prototype results) — they inform schedule planning but do not bind execution.

---

## 2. PR16 Methodology Reference

From `docs/planning/EPIC_4/SPRINT_25/DAY5_PATTERN_A_INVESTIGATION.md`: PR16 combines (a) **trace capture** of AD differentiation decisions at helper-function level, (b) **artifact inspection** by regenerating the target model's MCP emit and comparing against hand-derived KKT, (c) **empirical end-to-end verification** (don't rely on unit/integration gates — verify the actual emit shape byte-for-byte against the formal derivative), (d) **concrete-instance validation** (pin a specific equation instance and verify its KKT cross-term shape).

The Sprint 25 Day 5 investigation disproved the Phase 1 hypothesis (alias-AD recovery helps multi-index cases) by discovering that qabel/abel's AD derivatives were byte-correct, and the mismatch came from KKT stationarity assembly (Pattern C, not Pattern A). **Lesson:** architectural hypotheses fail not at the AD-math level but at the pipeline-boundary level (what downstream code assumes about upstream output). Only hand-derived verification catches these. Sprint 27 Priority 3's 3 redesigns are all pipeline-boundary problems — exactly the failure class PR16 is designed for.

---

## 3. Redesign A — #1390 kand Tree-Predicate-Aliased Sum Per-Instance Enumeration

### 3.1 Central Architectural Hypothesis

> **Replacing per-instance enumeration with predicate-constrained-Sum architecture on `stat_y(j,t,n)` cross-term emission reduces the 22-element phantom-offset output to 1 element matching the hand-derived KKT (a single guarded Sum over a `tree(n,n_inner)`-predicate-bound `n_inner` index), without regressing the 11 Tier 0/1 byte-stable canary models.**

Falsifiability: the experiment regenerates `kand_mcp.gms`; the cross-term either matches the hand-derived 1-element guarded Sum shape OR it doesn't.

### 3.2 Source Problem (canonical)

`data/gamslib/raw/kand.gms` declares:

```gams
Set tree(n,n);    "9-element static tree-predicate alias"
Equation dembalx(j,tn(t,n))..
   sum(i, a(j,i)*x(i,t)) + y(j,tn)
   =g= dem(n,j) + eps*sum(tree(nn,n), y(j,t-1,nn));
```

**Hand-derived KKT cross-term for `stat_y(j,t,n)`** (Lagrangian L = … + sum(n, lam_dembalx(j,t,n) · (sum(i, a(j,i)·x(i,t)) + y(j,tn) − dem(n,j) − eps · sum(tree(nn,n), y(j,t-1,nn))))) gives ∂L/∂y(j,t,n) contribution from the `t' = t+1` shifted constraint:

```gams
sum(n_inner$tree(n,n_inner), eps * lam_dembalx(j,t+1,n_inner))$(tn(t+1,n_inner))
```

**Single guarded Sum, 1 element.**

**Observed (buggy) emit** in current Sprint 27 Day 0 `data/gamslib/mcp/kand_mcp.gms` (per ISSUE_1390 documentation):

```gams
sum(nn, eps * 1$(tree(nn,n)) * lam_dembalx(j,t+1,n+9))$(tn(t,n)) +
sum(nn, eps * 1$(tree(nn,n)) * lam_dembalx(j,t+1,n+10))$(tn(t,n)) +
... [20 more terms, k = -8 .. +11] ...
```

**22 phantom-offset terms**, each iterating the full 9-element `nn` domain. The per-instance enumeration in `_compute_equality_jacobian`/`_compute_inequality_jacobian` iterates over the static `n` elements at the contributing instance, producing one cross-term per element-substitution rather than a single predicate-guarded Sum.

### 3.3 Validation Experiment Design (~45 min, Sprint 27 Day 0)

**Patch site (model-name-guarded prototype):**

`src/ad/constraint_jacobian.py:903` (`_compute_equality_jacobian`) + `:1027` (`_compute_inequality_jacobian`) — at the per-element enumeration loop that produces cross-terms for tree-predicate-aliased Sums. Insert a static predicate `_is_tree_predicate_aliased_sum(eq, sum_body)` that returns True when the equation's body contains a Sum whose iterator is bound by a 2-set membership predicate (e.g., `tree(nn,n)`); when True, replace the enumeration with a single predicate-guarded Sum-builder call.

**Prototype guard (illustrative):**

```python
# In _compute_equality_jacobian / _compute_inequality_jacobian, immediately
# before the per-element enumeration loop:
if model_ir.name == 'kand' and _is_tree_predicate_aliased_sum(eq, sum_body):
    # Emit single predicate-guarded Sum cross-term instead of 9 enumerated
    cross_term = _build_predicate_guarded_sum_cross_term(eq, ...)
    J.add(eq_row, var_col, cross_term)
    continue
```

The `_is_tree_predicate_aliased_sum` and `_build_predicate_guarded_sum_cross_term` are **prototype helpers** for the experiment only; the Sprint 27 implementation may refactor them.

**Execution steps:**

```bash
# 1. Apply model-name-guarded prototype patch (per Day 0 engineer)

# 2. Regenerate kand emit:
.venv/bin/python -m src.cli data/gamslib/raw/kand.gms -o /tmp/kand_mcp_experiment.gms

# 3. Verify phantom-offset terms eliminated (PRE-fix count: ~22):
grep -cE 'lam_dembalx\(j,t\+1,n[+-][0-9]+\)' /tmp/kand_mcp_experiment.gms
# Expect: 0 (post-fix, no phantom-offset cross-terms)

# 4. Verify single guarded Sum cross-term present (PRE-fix: 0; POST-fix: 1):
grep -cE 'sum\([a-z_]+\$tree\([a-z_,]+\), eps \* lam_dembalx\(j,t\+1,' /tmp/kand_mcp_experiment.gms
# Expect: ≥ 1 match (stat_y guarded Sum cross-term)

# 5. Pin and hand-derive a concrete instance (e.g., stat_y('p-1','time-2','n-4')):
awk "/^stat_y\\('p-1','time-2','n-4'\\)\\.\\./,/=E= 0;/" /tmp/kand_mcp_experiment.gms
# Compare emitted body byte-for-byte against the hand-derived KKT for that
# (j,t,n) = (p-1, time-2, n-4) instance.

# 6. Regression check on Tier 0/1 canaries (regenerate each, byte-compare
# against current main-branch artifact):
for m in dispatch quocge partssupply prolog sparta gussrisk ps2_f ps3_f ship splcge paklive; do
  .venv/bin/python -m src.cli data/gamslib/raw/${m}.gms -o /tmp/${m}_mcp_experiment.gms
  diff -u /tmp/${m}_mcp_experiment.gms data/gamslib/mcp/${m}_mcp.gms || echo "REGRESSION: $m"
done
# Expect: zero diff on all 11 canaries (model-name guard means the predicate
# path is inactive for non-kand models, so byte-stability must hold trivially).

# 7. Revert prototype patch (CRITICAL — zero src/ diff in Task 6 commit).
```

### 3.4 PROCEED / REPLAN Criteria (binary)

**PROCEED if ALL hold:**

- Phantom-offset grep returns 0 (step 3).
- Predicate-guarded Sum grep returns ≥ 1 (step 4).
- Hand-derived KKT byte-comparison on the pinned instance matches (step 5).
- All 11 Tier 0/1 canaries byte-stable (step 6).

**REPLAN if ANY hold:**

- Phantom-offset grep still > 0 (predicate detection failed).
- Predicate-guarded Sum missing (cross-term builder failed).
- Hand-derived KKT mismatch (semantic regression — predicate-preservation approach is wrong).
- Any Tier 0/1 canary diverges (model-name guard leaked).

### 3.5 Tentative Verdict (PROJECTION — binding verdict pending Day 0 execution)

🟢 **Tentative PROCEED.** Architectural-analysis basis: (a) `_compute_equality_jacobian`/`_compute_inequality_jacobian` already accept a per-equation differentiation strategy via callback (the per-element enumeration is one of several differentiation paths); inserting a predicate-guarded path at the same dispatch site is a well-localized change. (b) `tree(n,n)` predicate has a clear AST shape (`SetMembershipTest` on a 2-set parameter) detectable via static analysis. (c) The hand-derived KKT shape is unambiguous (predicate-bound Sum). (d) Model-name guard limits regression risk to kand only — by construction, Tier 0/1 canaries are unaffected.

**Risk factors that could flip to REPLAN:** the per-element enumeration may not have a clean callback insertion point (would force a deeper refactor); the tree-predicate detection may match unrelated Sums (would produce false positives on other models). Day 0 execution will resolve.

---

## 4. Redesign B — #1385 srpchase Option 1 Short-Circuit Symbolic-Instance Handling

### 4.1 Central Architectural Hypothesis

> **An alternative short-circuit shape — Option B (runtime-guard emission with concrete-index semantics preserved at the AD → emit boundary) — applied to srpchase allows the model to translate cleanly (<10s, vs current 600s+ translate_timeout) AND produce GAMS-compile-clean emit with correct multiplier references, WITHOUT regressing the 11 Tier 0/1 byte-stable canaries.**

Falsifiability: the experiment regenerates `srpchase_mcp.gms` and runs `gams action=c lo=2`; either translation completes in <10s AND compile produces zero errors AND multiplier references resolve, OR it doesn't.

### 4.2 Source Problem (canonical)

`data/gamslib/raw/srpchase.gms` — 600s+ translate timeout in production pipeline (per Sprint 27 Day 0 `gamslib_status.json` bucket `translate_timeout`). Sprint 26 Day 4 attempted a short-circuit ("Option 1") that detected single-`SetMembershipTest` equation conditions (e.g., `slack(srn)$(srn(srn))`) and enumerated only ONE symbolic instance instead of the Cartesian product. **Result:** translation dropped from 846s to 5.7s — but the emit was structurally broken:

```gams
stat_y(n).. ((((-1) * 1$(ancestor(srn,srn))) * nu_slack("srn"))$(srn(srn)))$((not leaf(srn))) =E= 0;
```

**Three concrete bugs:**

1. **`nu_slack("srn")` literal-string indices** — `srn` is a SET NAME, not a concrete element of `n`. PATH compile rejects.
2. **`1$(ancestor(srn,srn))`** — same root cause: `ancestor` is a 2-set membership parameter expecting concrete elements, not set names.
3. **Missing cross-terms** — `J_g^T·lam_demand` entries dropped because `_diff_varref` requires exact concrete-index matches; with symbolic placeholders, they become 0.

**Root cause:** The Sprint 26 Day 4 design assumed downstream AD/emit pipeline would handle symbolic-index instances (citing Sprint 25 #1306/#1308 prior art on indexed stationarity equations). The assertion was wrong. #1306/#1308 bind the symbolic index in the equation header (`stat_<eq>(i)..`) — the body's symbolic references are valid because the header binds them. The Day 4 placeholder tries to use the SET NAME as if it were an instance value, but downstream `_diff_varref` treats it as a CONCRETE element string per the Cartesian-enumeration contract. The Day 4 attempt was rolled back; `_build_symbolic_instance_placeholder` does NOT currently exist in `src/ad/index_mapping.py` (confirmed by grep on current main).

### 4.3 Validation Experiment Design (~60 min, Sprint 27 Day 0)

**Option selection — Option B (runtime-guard emission), NOT Option A (symbolic-instance handling end-to-end):**

The Sprint 26 Day 4 attempt is Option A's mirror image — it tried to pass symbolic indices through the AD layer to the emit layer and failed at the emit boundary. Option A's full version would require concrete-index → symbolic-index translation throughout `_diff_varref`, `_diff_paramref`, `_diff_setmembershiptest`, `_build_indexed_stationarity_expr`, and `emit_equation_definition` — a multi-module refactor (~18–28h) that exceeds the #1385 sub-priority budget (6–10h).

**Option B (preferred):** Keep the existing AD pipeline's concrete-index Cartesian-enumeration contract intact. At the **emit boundary** (where `enumerate_equation_instances` would otherwise produce 9 concrete instances of `slack(srn)$(srn(srn))`), insert a **runtime-guard emission** path:

1. Detect the single-`SetMembershipTest` condition at `enumerate_equation_instances` site (already there at `src/ad/index_mapping.py:377`).
2. Instead of enumerating only ONE symbolic placeholder, enumerate ZERO instances (skip the equation in the Jacobian).
3. At emit time, generate the equation body as a `sum(<bound_idx>$(<predicate>), <body>)` runtime-guard expression — preserving the predicate as a GAMS-side filter.

This shape preserves concrete-index semantics in the AD layer (no symbolic placeholders leak) AND produces GAMS-compile-clean emit with the predicate as a runtime guard.

**Patch sites (model-name-guarded prototype):**

- `src/ad/index_mapping.py:377` (`enumerate_equation_instances`): add `if model.name == 'srpchase' and _is_single_setmembership_condition(condition): return []` (returns empty list → skip AD enumeration).
- `src/kkt/stationarity.py` (the indexed-stationarity-expression builder): when an equation has no AD-enumerated instances but has a single-SetMembershipTest condition, emit the body wrapped in `sum(<bound_idx>$(<predicate>), <expr>)`.

**Execution steps:**

```bash
# 1. Apply model-name-guarded Option B prototype patch.

# 2. Regenerate srpchase emit (measure wall-clock translate time):
time .venv/bin/python -m src.cli data/gamslib/raw/srpchase.gms -o /tmp/srpchase_mcp_experiment.gms
# Expect: <10s (vs 600s+ baseline at current main)

# 3. GAMS compile-check (catches multiplier-reference resolution failures):
gams /tmp/srpchase_mcp_experiment.gms action=c lo=2 o=/tmp/srpchase_compile.lst
echo "Compile rc: $?"  # Expect: 0
grep -cE '^\*\*\*\*' /tmp/srpchase_compile.lst
# Expect: 0 (no GAMS error markers)

# 4. Verify no quoted-literal-set-name indices appeared:
grep -nE 'nu_[a-z_]+\("[a-z_]+"\)' /tmp/srpchase_mcp_experiment.gms
# Expect: 0 matches (no `nu_slack("srn")` style indices)

# 5. Verify multiplier references resolve symbolically (not literal "srn"):
grep -nE '1\$\(ancestor\("srn",' /tmp/srpchase_mcp_experiment.gms
# Expect: 0 matches (no quoted-literal `ancestor("srn",...)` predicates)

# 6. Hand-derive stat_y(srn) KKT and byte-compare emit body against it.

# 7. Regression check on 11 Tier 0/1 canaries (per §3.3 step 6).

# 8. Revert prototype patch (CRITICAL — zero src/ diff in Task 6 commit).
```

### 4.4 PROCEED / REPLAN Criteria (binary)

**PROCEED if ALL hold:**

- Translation completes in <10s (step 2).
- GAMS compile produces 0 errors (step 3).
- No quoted-literal set-name indices in emit (steps 4 + 5).
- Hand-derived KKT byte-comparison on stat_y(srn) matches (step 6).
- All 11 Tier 0/1 canaries byte-stable (step 7).

**REPLAN if ANY hold:**

- Translation still >10s (short-circuit not triggered).
- GAMS compile errors (multiplier references still malformed).
- Quoted-literal indices appear (concrete-index semantics not preserved at emit boundary).
- Hand-derived KKT mismatch.
- Any Tier 0/1 regression.

### 4.5 Tentative Verdict (PROJECTION — binding verdict pending Day 0 execution)

🟡 **Tentative PROCEED-with-caveat.** Architectural-analysis basis: (a) Option B preserves the existing concrete-index Cartesian-enumeration contract throughout the AD layer, avoiding the multi-module refactor Option A would require. (b) Runtime-guard emission as `sum(<bound>$(<predicate>), <body>)` is a well-established GAMS pattern; PATH accepts the predicate as a domain filter. (c) Model-name guard limits Tier 0/1 regression risk to zero by construction.

**Risk factors that could flip to REPLAN:** the cross-term contributions from `J_g^T·lam_demand` (the 3rd bug in §4.2) may not naturally re-derive under Option B — the AD layer still doesn't enumerate any instances, so it cannot produce cross-terms for the empty `enumerate_equation_instances` return. The emit-boundary runtime-guard must ALSO emit the cross-terms structurally (without AD-layer enumeration). This is a non-trivial design step; the experiment may surface it as a REPLAN.

**Caveat:** If Day 0 execution reveals the cross-term coverage issue, the #1385 sub-priority may need to **partial-PROCEED** — short-circuit for translate-time only (5.7s achievable), with explicit deferred handling of cross-terms via a Sprint 28 fix.

---

## 5. Redesign C — #1393 + #1335 otpop Scalar-Equation Sum-Collapse with Symbolic Superset

### 5.1 Central Architectural Hypothesis

> **Approach 3 (hybrid post-AD collapse to symbolic-Sum) — extending `_is_concrete_instance_of` (`src/ad/derivative_rules.py:2607`) to recognize SYMBOLIC superset names as "concrete" w.r.t. subset iteration variables when the symbolic name appears as an eq-domain index — fixes BOTH (a) the `stat_x(tt)` / `stat_p(tt)` `kdef` Sum-over-counting (#1393) AND (b) the `stat_p(tt)` missing `nu_zdef` time-reversal cross-term (#1335) AND allows otpop to PATH-solve to objective `pi ≈ 4217.80`, WITHOUT regressing the 8 currently-passing scalar-eq models.**

Falsifiability: the experiment regenerates `otpop_mcp.gms`, then runs PATH-solve; either both bugs are fixed AND the objective matches the NLP optimum AND no scalar-eq models regress, OR they don't.

### 5.2 Source Problem (canonical)

`data/gamslib/raw/otpop.gms` has two distinct scalar-equation Sum-collapse bugs:

**Bug #1393 (over-counting):** `kdef` scalar equation contains `sum(t, del(t) * (...))` where `t ⊂ tt` (subset relation, with `tt` the eq-domain of `stat_x(tt)` and `stat_p(tt)`). The expected post-collapse `stat_x(tt)` cross-term (hand-derived):

```gams
(del(tt) * 0.365 * (1 - c) * p(tt))$(t(tt)) * nu_kdef
```

Observed (over-counted by |t| = 17):

```gams
sum(t__, ((-1) * (del(t__) * 0.365 * (1 - c) * p(tt))) * nu_kdef)$(t(tt))
```

Root cause: `_sum_should_collapse` (`derivative_rules.py:2556`) calls `_is_concrete_instance_of('tt', 't', config)` to check whether `tt` is a concrete element of set `t`. Returns False because `tt` is SYMBOLIC (eq-domain index of `stat_x(tt)`), not a concrete element. The Sum doesn't collapse; it falls through to symbolic-Sum preservation, producing the 17× over-counted wrap.

**Bug #1335 (missing time-reversal cross-term):** `zdef` scalar equation contains `sum(t, ... * p(t + (card(t) - ord(t))))`. The offset `t + (card(t) - ord(t))` evaluates to the LAST element of `t` (always `'1990'` for `t = '1974'..'1990'`). Expected `stat_p(tt)` cross-term:

```gams
((v * 0.365 * sum(t, xb(t) - x(t))) * nu_zdef)$(sameas(tt, '1990'))
```

Observed: NO `nu_zdef` anywhere in `stat_p(tt)` — cross-term entirely missing. Root cause: `_try_eval_offset` (constraint_jacobian.py:133–260) handles `card(<set>)` and `ord(<concrete-element>)`, but only when the argument is already a concrete element. For `t + (card(t) - ord(t))` inside `sum(t, ...)`, the offset expression is evaluated BEFORE substituting `t → t'`, so `ord(t)` has no concrete element to look up.

### 5.3 #1335 Approach Selection (KU-39 Resolution)

Per Sprint 26 Day 9 SPRINT_LOG, 3 approaches were enumerated but not selected:

| Approach | Description | Patch surface | Risk |
|---|---|---|---|
| **A** | Extend `_expand_sums_with_unresolved_offsets` AND fix downstream re-symbolization in `_add_indexed_jacobian_terms` to preserve expanded-Sum shapes. | `src/ad/derivative_rules.py:1847+` + `src/kkt/stationarity.py` re-symbolization helpers | **High** — touches multiple modules; risks regressing existing IndexOffset / SetMembershipTest handling from Sprint 25. |
| **B** | Resolve IndexOffset `card(t) - ord(t)` symbolically (without expanding) so AD's `_diff_sum` computes the partial without Sum expansion. | `src/ir/condition_eval.py` (or `src/ad/index_eval.py`) | **Medium** — narrower than A but requires new symbolic-offset-evaluation infrastructure not currently in the codebase. |
| **C** | Hybrid post-AD collapse: extend `_is_concrete_instance_of` to recognize symbolic supersets, allowing `_sum_should_collapse` to fire on symbolic eq-domain indices that are supersets of the iteration variable. | `src/ad/derivative_rules.py:2607` (one function, ~30-line addition) | **Low** — contained, single-function change; reuses existing collapse-logic infrastructure. |

**Selected: Approach C (hybrid post-AD collapse).** Rationale:

- **Smallest patch surface** (single function, ~30 lines) — reduces regression risk to the 8 currently-passing scalar-eq models.
- **Reuses existing collapse infrastructure** — `_sum_should_collapse` and `_is_concrete_instance_of` already work for the concrete-element case; the extension teaches them to recognize SYMBOLIC supersets via the model_ir subset declaration (`t ⊂ tt` is queryable from `model_ir.sets`).
- **Subsumes both #1393 (over-counting) and #1335 (missing cross-term)** under the same fix — because both bugs trace to the same root cause (`_is_concrete_instance_of` returns False on symbolic supersets), one patch fixes both.
- **Day 9 SPRINT_LOG explicitly notes Approach C as "the lightest"** — Sprint 26's engineer-level intuition aligns with the architectural analysis here.

**Day 0 execution decision rule:** If Approach C's prototype fails the verification criteria (§5.5), fall back to Approach B (symbolic offset evaluation); if Approach B also fails, fall back to Approach A (full Sum-expansion redesign).

### 5.4 Validation Experiment Design (~75 min, Sprint 27 Day 0)

**Patch site (model-name-guarded prototype, Approach C):**

`src/ad/derivative_rules.py:2607` (`_is_concrete_instance_of`). Add a 3rd strategy: when `concrete` is a SYMBOLIC name appearing as an eq-domain index AND there exists a subset relation `symbolic ⊂ concrete` in `model_ir.sets`, return True. This allows `_sum_should_collapse` to recognize `_is_concrete_instance_of('tt', 't')` as True when `t ⊂ tt` is declared.

**Prototype guard (illustrative):**

```python
# In _is_concrete_instance_of (derivative_rules.py:2607), after the existing
# model_ir set-membership check at strategy 1:
#
# Note: SetDef does NOT have a `subset_of` field. Subset relations are
# represented by `SetDef.domain` — a tuple of parent set names
# (see src/ir/symbols.py:48-54). For example, `Set t(tt) /...;` produces
# `SetDef(name='t', members=[...], domain=('tt',))`. Alias resolution is
# also required (e.g., if `tt` is declared as `Alias(t,tt)`, the canonical
# resolution must follow `model_ir.aliases` to the underlying set).
#
# Existing helpers in src/kkt/stationarity.py:3626-3670 already implement
# this lookup: `_find_superset_in_domain(subset_idx, var_domain, model_ir)`
# returns the in-scope parent index name (with alias resolution) given a
# subset index and a domain tuple. The Approach C prototype below can
# reuse the same lookup pattern; for the AD layer's _is_concrete_instance_of,
# we check whether `symbolic` is a declared subset whose parent (after
# alias resolution) matches `concrete`.
if config is not None and config.model_ir is not None and config.model_ir.name == 'otpop':
    model_ir = config.model_ir
    # Strategy 3: symbolic-superset check — concrete may be the eq-domain
    # index whose set is a SUPERSET of the symbolic iteration variable's set.
    if isinstance(concrete, str) and concrete != symbolic:
        # Resolve both names through any alias chain to canonical set names.
        # (`_resolve_alias_target` from src/kkt/stationarity.py handles
        # transitive alias chains and self-aliasing safely.)
        canonical_symbolic = _resolve_alias_target(symbolic, model_ir)
        canonical_concrete = _resolve_alias_target(concrete, model_ir)
        if canonical_symbolic in model_ir.sets:
            symbolic_set = model_ir.sets[canonical_symbolic]
            # SetDef.domain is a tuple of parent set names; a single-parent
            # entry like `domain=('tt',)` signals a subset declaration.
            if len(symbolic_set.domain) == 1:
                parent = symbolic_set.domain[0]
                canonical_parent = _resolve_alias_target(parent, model_ir)
                if canonical_parent == canonical_concrete:
                    return True
```

**API reuse note:** Day 0 engineer can simplify the prototype by calling the existing `_find_superset_in_domain` helper from `src/kkt/stationarity.py:3626-3670` with a single-element `var_domain=(concrete,)` tuple — that helper already encapsulates the alias-resolution + subset-domain-lookup logic. Whether to inline the logic (per the snippet above) or call the existing helper is a Day 0 implementation choice; both produce equivalent results.

**Execution steps:**

```bash
# 1. Apply model-name-guarded Approach C prototype patch.

# 2. Regenerate otpop emit:
.venv/bin/python -m src.cli data/gamslib/raw/otpop.gms -o /tmp/otpop_mcp_experiment.gms

# 3. Verify #1393 over-counted Sum is GONE (PRE-fix: ≥1 match):
grep -cE 'sum\(t__,[^)]+\* nu_kdef' /tmp/otpop_mcp_experiment.gms
# Expect: 0 (over-counted Sum collapsed)

# 4. Verify post-collapse single-term shape PRESENT:
grep -nE 'del\(tt\) \* 0\.365 \* \(1 - c\) \* p\(tt\)' /tmp/otpop_mcp_experiment.gms
# Expect: ≥ 1 match (matches hand-derived stat_x(tt) cross-term)

# 5. Verify #1335 nu_zdef cross-term PRESENT in stat_p(tt):
awk '/^stat_p\(.*\)\.\./,/=E= 0;/' /tmp/otpop_mcp_experiment.gms | grep -c 'nu_zdef'
# Expect: ≥ 1 (was 0 pre-fix)

# 6. Pin and hand-derive stat_x('1990') + stat_p('1990') KKT, byte-compare
# against emitted bodies.

# 7. GAMS compile-check otpop emit (catches structural emit errors):
gams /tmp/otpop_mcp_experiment.gms action=c lo=2 o=/tmp/otpop_compile.lst
grep -cE '^\*\*\*\*' /tmp/otpop_compile.lst
# Expect: 0 (no NEW GAMS errors — otpop has pre-existing $171 from #1357 comp_up
# subset/superset; note them separately if seen and confirm not introduced by
# Approach C).

# 8. Run PATH-solve with NLP warm-start:
gams /tmp/otpop_mcp_experiment.gms o=/tmp/otpop_solve.lst lo=2
grep -E 'MODEL STATUS|OBJECTIVE' /tmp/otpop_solve.lst
# Expect: MODEL STATUS 1 (Optimal) AND objective ≈ 4217.80 (matches NLP optimum
# per ISSUE_1335 / ISSUE_1393).

# 9. Regression check on 8 currently-passing scalar-eq models (TBD list — derive
# from gamslib_status.json scalar-equation models in compare_match bucket).

# 10. Revert prototype patch (CRITICAL — zero src/ diff in Task 6 commit).
```

### 5.5 PROCEED / REPLAN Criteria (binary)

**PROCEED if ALL hold:**

- #1393 over-counted Sum eliminated (step 3 returns 0).
- Post-collapse single-term shape present (step 4 returns ≥ 1).
- #1335 `nu_zdef` cross-term present in `stat_p(tt)` (step 5 returns ≥ 1).
- Hand-derived KKT byte-comparison matches on both pinned instances (step 6).
- GAMS compile clean except pre-existing $171 noted (step 7).
- PATH-solve produces MODEL STATUS 1 AND objective ≈ 4217.80 (step 8).
- All 8 currently-passing scalar-eq models byte-stable (step 9).

**REPLAN if ANY hold:**

- #1393 over-count persists.
- Post-collapse shape wrong.
- #1335 cross-term still missing (Approach C doesn't subsume #1335).
- Hand-derived KKT mismatch.
- GAMS compile NEW errors.
- PATH-solve fails or objective mismatch.
- Scalar-eq regression.

**Fallback rule** (per §5.3): if Approach C produces REPLAN, attempt Approach B (symbolic offset evaluation, ~3–5h additional effort). If B also REPLAN, attempt Approach A (full Sum-expansion redesign, ~8–12h). If all 3 REPLAN, defer #1393 + #1335 to Sprint 28 and reallocate Priority 3 budget to higher-leverage work (#1378 deep-dive or #1387/#1388 implementation).

### 5.6 Tentative Verdict (PROJECTION — binding verdict pending Day 0 execution)

🟢 **Tentative PROCEED for #1393, 🟡 Tentative PROCEED-with-caveat for #1335.** Architectural-analysis basis:

- **#1393 (Sum over-counting):** The fix is well-localized — `_is_concrete_instance_of` already accepts `config.model_ir` and has two strategies (model_ir set-membership + heuristic prefix). Adding a 3rd strategy for subset-relation lookup is a contained ~30-line addition reusing existing infrastructure. The hand-derived collapse is unambiguous. **High confidence PROCEED.**
- **#1335 (missing time-reversal cross-term):** The hypothesis is that Approach C ALSO fixes #1335 by allowing `_sum_should_collapse` to fire on the `zdef` sum body, which would trigger the AD machinery to compute the partial w.r.t. `p('1990')`. But `_try_eval_offset` may need a separate fix to resolve `card(t) - ord(t)` to `'1990'` — Approach C alone may not subsume #1335. **Moderate confidence PROCEED-with-caveat.**

**Risk factors that could flip to REPLAN:** the subset relation `t ⊂ tt` IS queryable in the standard `model_ir.sets` representation via `SetDef.domain` (a tuple of parent set names; see `src/ir/symbols.py:48-54`), AND alias resolution is already implemented (see `_find_superset_in_domain` at `src/kkt/stationarity.py:3626-3670`) — so the previously-flagged "may not be queryable" concern is resolved at the IR-API level. The remaining risk is Sprint 25 dynamic-subset handling (per #723) for cases where the subset has a runtime `$`-condition: `resolve_set_members` falls back to parent-set members, which may produce false-positive supersets in subset-of-subset chains. Day 0 execution will verify whether otpop's `t ⊂ tt` relation is dynamic-subset-affected.

---

## 6. Coordinated Design Analysis (KU-38 Resolution)

### 6.1 Pair-wise Architectural Overlap

| Pair | Shared Constraint | Pipeline Stage Overlap | Recommendation |
|---|---|---|---|
| **#1390 + #1385** | Both involve symbolic-vs-concrete index handling in the AD layer (#1390 = cross-term enumeration; #1385 = instance enumeration). | `src/ad/constraint_jacobian.py` (#1390) vs `src/ad/index_mapping.py` (#1385) — adjacent modules but distinct functions. | **Serial.** No direct code reuse; distinct fix surfaces. |
| **#1385 + #1393+#1335** | Both touch the AD → emit pipeline boundary (how concrete AD output gets re-symbolized for emit). | `src/ad/index_mapping.py` (#1385) vs `src/ad/derivative_rules.py` (#1393+#1335) — different AD subsystems. | **Serial.** Option B (#1385's runtime-guard emission) and Approach C (#1393+#1335's collapse extension) are orthogonal. If Option A were selected for #1385 (rejected here), there would be moderate coordinated-design interaction with #1335; Option B has none. |
| **#1390 + #1393+#1335** | Both involve Sum-structure preservation (predicates vs collapse logic). | `src/ad/constraint_jacobian.py` (#1390) vs `src/ad/derivative_rules.py` (#1393+#1335) — different AD subsystems; #1390 produces Sum cross-terms, #1393+#1335 collapses Sum cross-terms. | **Serial.** Complementary but orthogonal: #1390's predicate preservation operates upstream; #1393+#1335's collapse operates downstream. No code reuse. |

### 6.2 Shared Methodology (not implementation)

While the **implementations** are serial (independent), all 3 redesigns share:

- **Same Phase 0 acceptance-gate methodology** (PR16: hand-derive KKT → regenerate → byte-compare → PROCEED/REPLAN). Reuse the same validation template.
- **Same regression-check surface** (11 Tier 0/1 byte-stable canaries + per-redesign target-model recovery check). Avoid re-running identical tests; share the canary baseline.
- **Same documentation pattern** (each redesign gets a Phase 0 section in its issue doc per CONTRIBUTING.md §"Phase 0 Acceptance Gates" — Sprint 27 Prep Task 2 codified this for issues #1356/#1357/#1387/#1388; Sprint 27 Day 0 should author Phase 0 sections for #1390/#1385/#1393/#1335 similarly).

### 6.3 Recommendation: Serial Implementation

**Recommended sequence (lightest → heaviest, lowest risk → highest risk):**

1. **#1393 + #1335 (Approach C)** — lowest risk (~30-line addition, single function), highest confidence (Approach C explicitly recommended by Sprint 26 Day 9 SPRINT_LOG). ~6–10h.
2. **#1390 (predicate-guarded Sum)** — medium risk (cross-term enumeration redesign, but well-localized at the dispatch site). ~10–16h.
3. **#1385 (Option B runtime-guard emission)** — highest risk (Sprint 26 Day 4 attempt failed; PROCEED-with-caveat tentative verdict per §4.5). ~6–10h IF Option B works cleanly; ~12–18h if cross-term coverage issue surfaces.

**Coordinated-design would NOT reduce total effort** because the 3 fix surfaces are orthogonal (different modules, different functions, different architectural layers). Coordinated design's overhead (joint design meetings, shared interface discussions) would likely add ~2–4h without commensurate savings.

**Serial schedule allows early REPLAN gating:** if #1393+#1335 (lowest-risk first) REPLAN, Sprint 27 can immediately reallocate Priority 3's budget to other priorities. If #1390 REPLAN, the same option exists. #1385's higher risk is deferred to the end, where REPLAN's impact is contained.

### 6.4 Cascading REPLAN Rule (KU 3.5 Sub-Resolution)

- If **#1390 REPLAN**: #1385 and #1393+#1335 PROCEED independently (no architectural dependency).
- If **#1385 REPLAN**: #1390 and #1393+#1335 PROCEED independently.
- If **#1393+#1335 REPLAN**: #1390 and #1385 PROCEED independently.
- If **2 or more REPLAN**: Sprint 27 reallocates Priority 3's remaining budget to other priorities (Task 11 schedule decision at Sprint 27 Day 0 retrospective).

**No cascading REPLAN required** because the 3 redesigns are architecturally orthogonal (per §6.1 pair-wise overlap analysis).

---

## 7. Phase 0 Binary-Signal Criteria (KU 3.5 Resolution)

Per Sprint 26 retrospective PR16 codification: each Phase 0 validation experiment must produce a **binary PROCEED / REPLAN signal**. Ambiguous outcomes are NOT permitted — if the experiment's verification fails on ANY criterion in the PROCEED list, the signal is REPLAN regardless of partial successes.

**Explicit per-experiment criteria** are defined in §3.4 (#1390), §4.4 (#1385), §5.5 (#1393+#1335).

**Ambiguity-resolution rule:** if an experiment produces partial PROCEED (e.g., target-model fix works but unrelated regression appears), the signal is **REPLAN with caveat**. The redesign returns to its issue doc for refinement; Sprint 27 implementation does not proceed until a subsequent Phase 0 validation produces clean PROCEED.

**Per-experiment partial-PROCEED handling:**

- **#1385 partial-PROCEED:** if translation-time fix works (5.7s achievable) but cross-term coverage issue surfaces, escalate to a "scoped-PROCEED" decision — Sprint 27 implements the translate-time short-circuit only and explicitly defers cross-term handling to Sprint 28. This is permitted because the translate-time fix is independently valuable.
- **#1390 partial-PROCEED:** not anticipated — the predicate-detection either fires correctly OR it produces malformed cross-terms; binary by construction.
- **#1393+#1335 partial-PROCEED:** if #1393 fixes but #1335 cross-term still missing, escalate to Approach B fallback per §5.5 fallback rule. Approach C alone may not subsume #1335.

---

## 8. Verification Summary (Sprint 27 Day 0 Prep)

| Verification Target | Result |
|---|---|
| Per-redesign hypothesis statement (3 hypotheses) | ✅ §3.1, §4.1, §5.1 |
| Per-redesign validation experiment design (concrete patch sites, prototype shape, regen commands, grep verification, PROCEED/REPLAN criteria) | ✅ §3.3, §4.3, §5.4 |
| Per-redesign tentative verdict (hand-derived architectural projection) | ✅ §3.5 (🟢), §4.5 (🟡), §5.6 (🟢 + 🟡) |
| Coordinated-design analysis (KU-38 resolution) | ✅ §6 — Serial implementation recommended; pair-wise overlap analysis shows orthogonal fix surfaces; coordinated-design would add overhead without savings |
| #1335 approach selection (KU-39 resolution) | ✅ §5.3 — **Approach C (hybrid post-AD collapse) SELECTED.** Fallback rule: C → B → A per §5.5 if Day 0 execution REPLAN. |
| Phase 0 binary-signal criteria (KU 3.5 resolution) | ✅ §7 — Binary by construction; partial-PROCEED resolved via scoped-PROCEED or fallback rule per-experiment |
| Sprint 27 Day 0 experiment execution scheduled | ✅ All 3 experiments DESIGN-READY; ~3h cumulative Day 0 work for binding verdicts |
| Zero `src/` diff in Task 6 commit | ✅ (all prototype patches scheduled for Day 0; this prep authoring is docs-only) |

---

## 9. Sprint 27 Day 0 Execution Plan (handoff)

Sprint 27 Day 0 engineer executes the 3 experiments in the recommended sequence (lowest-risk first per §6.3). Each experiment is ~30–90 min; cumulative ~3h Day 0 work. After each experiment, the engineer records the binding PROCEED/REPLAN signal back in this document (§3.5, §4.5, §5.6) and updates KNOWN_UNKNOWNS.md §3.1–3.5 from 🟡 PARTIALLY VERIFIED to ✅ VERIFIED with the binding verdict.

**Execution order:**

1. **Experiment C (#1393+#1335 Approach C)** — §5.4 steps 1–10. Expect ~75 min. If REPLAN, fall back to Approach B (§5.5 fallback rule).
2. **Experiment A (#1390 predicate-guarded Sum)** — §3.3 steps 1–7. Expect ~45 min. If REPLAN, file follow-up issue documenting alternative predicate-detection design.
3. **Experiment B (#1385 Option B runtime-guard)** — §4.3 steps 1–8. Expect ~60 min. If REPLAN, consider scoped-PROCEED per §7 partial-PROCEED rule.

Total: ~3h Day 0. PROCEED-all → 30–48h Sprint 27 Priority 3 implementation budget committed. ≥1 REPLAN → Sprint 27 retrospective decision on budget reallocation per §6.4 cascading rule.

---

## 10. Related Documents

- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 6 — this task's specification.
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` §Unknowns 3.1, 3.2, 3.3, 3.4, 3.5 — research questions this task verifies.
- `docs/planning/EPIC_4/SPRINT_25/DAY5_PATTERN_A_INVESTIGATION.md` — canonical PR16 methodology reference.
- `docs/planning/EPIC_4/SPRINT_26/SPRINT_LOG.md` Day 9 entry — 3-approach enumeration for #1335.
- `docs/issues/ISSUE_1390_*.md`, `ISSUE_1385_*.md`, `ISSUE_1393_*.md`, `ISSUE_1335_*.md` — per-redesign issue docs (source problem + fix-surface notes).
- `CONTRIBUTING.md` §"Phase 0 Acceptance Gates" (Sprint 27 Prep Task 2 codification of PR20) — verification methodology.
- `docs/planning/EPIC_4/SPRINT_27/PR19_WIDENING_DESIGN.md` (Sprint 27 Prep Task 5) — Sprint 27 Day 0 widening lands the broader PR19 target list including kand + otpop + srpchase for byte-stability regression detection on each Priority 3 fix.
- Source code: `src/ad/constraint_jacobian.py:903,1027`, `src/ad/derivative_rules.py:2556,2607`, `src/ad/index_mapping.py:377`, `src/kkt/stationarity.py`.

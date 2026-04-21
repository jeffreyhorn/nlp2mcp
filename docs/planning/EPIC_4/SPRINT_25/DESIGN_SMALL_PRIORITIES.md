# Design — Small Priorities (#1270 Multi-Solve Gate Extension, #1271 Dispatcher Refactor)

**Created:** 2026-04-21
**Sprint:** 25 (Prep Task 7)
**Issues:** [#1270](https://github.com/jeffreyhorn/nlp2mcp/issues/1270), [#1271](https://github.com/jeffreyhorn/nlp2mcp/issues/1271)
**Predecessor docs:** [`../SPRINT_24/AUDIT_MULTI_SOLVE_DRIVERS.md`](../SPRINT_24/AUDIT_MULTI_SOLVE_DRIVERS.md), [`../SPRINT_24/PLAN_FIX_DECOMP.md`](../SPRINT_24/PLAN_FIX_DECOMP.md), [`../SPRINT_24/PLAN_FIX_PARTSSUPPLY.md`](../SPRINT_24/PLAN_FIX_PARTSSUPPLY.md)
**In-tree issue docs:** [`../../../issues/ISSUE_1270_multi-solve-gate-saras-style-top-level-marginal-reads.md`](../../../issues/ISSUE_1270_multi-solve-gate-saras-style-top-level-marginal-reads.md), [`../../../issues/ISSUE_1271_refactor-collapse-loop-tree-dispatchers.md`](../../../issues/ISSUE_1271_refactor-collapse-loop-tree-dispatchers.md)

---

## Executive Summary

Sprint 25 Priorities 3 and 4 are both **mechanical, well-bounded changes** that benefit from 1–2 hours of design pre-work to lock scope before implementation. Both pre-design tasks are completed in this document.

- **#1270 Multi-Solve Gate (Priority 3):** Approach A (cross-reference) committed. Corpus survey identifies **14 candidate models** with ≥2 solves and ≥1 `eq.m` reference; of those, **2 are currently matching** (gussrisk, sparta — must remain non-flagged) and **1 is currently translate-success / solve-failure** (saras — the canonical target). The extension is a single-function change in [`src/validation/driver.py`](../../../../src/validation/driver.py#L151) (`_collect_equation_marginals`) plus a new top-level pass and a parameter-usage-tracking helper. Estimated effort: **3–4h** including the saras integration test and partssupply regression guard.

- **#1271 Dispatcher Refactor (Priority 4):** Unified signature `_loop_tree_to_gams(node, *, token_subst=None)`. Caller inventory shows **only 1 external use site** for the substituting variant (`emit_pre_solve_param_assignments` line 3271), and the substituting dispatcher is **fully nested** inside that one function — so the refactor is well-bounded. Byte-diff regression strategy: snapshot all currently-translating models (translate=success per `gamslib_status.json`, ~135 models) before the refactor, regenerate after, expect zero diffs. Estimated effort: **4–6h** matching the issue doc's bound.

**Combined effort: 7.5–9.5h.** This is **0.5–2.5h above** the PREP_PLAN's original "≤ 7h" acceptance-criterion budget. Two paths forward documented in §Section 3: (a) treat both items as a deferred / post-Checkpoint-2 cleanup block on Day 11 (recommended); (b) split across Days 5–6 with a second contributor while Priority 2 Batch 2 lands in parallel. The acceptance criterion in PREP_PLAN was relaxed accordingly (see §Task 7 Acceptance Criteria — "≤ 7.5h at the low end").

**Day allocation per [`DESIGN_ALIAS_AD_ROLLOUT.md`](DESIGN_ALIAS_AD_ROLLOUT.md) §Section 5 parallel-work table:** both Priority 3 and Priority 4 are deferred to **Day 11** (post-Checkpoint-2 cleanup window) — they have no alias-AD coupling and benefit from the late-sprint context where Priority 1 outcomes are known. Alternative: dispatch to a separate contributor on Days 4–6 alongside Priority 2 Batch 2.

---

## Section 1 — #1270 Multi-Solve Gate Extension

### 1.1 Approach Decision: Approach A (cross-reference)

**Committed:** Approach A — flag any `eq.m` read whose receiving parameter later appears in another declared model's constraint body.

**Rationale:**

- **Approach A** has the cleanest semantic fit ("the dual feeds the next solve's constraints"). Distinguishes feedback from reporting because reporting writes to display parameters that don't appear in any model's constraint body.
- **Approach B** (sequence between solves) over-fires on multi-stage display patterns (`solve A; report.value = A.eq.m; solve B; ...`) — would need an additional exclusion list for `display`/`put`/`abort`, adding fragility.
- **Approach C** (allowlist) doesn't scale and treats symptoms.

**Trade-off accepted:** Approach A requires parameter-usage tracking across model bodies (~50 lines of new code in `driver.py`). The implementation cost is justified by the regression-canary safety (partssupply, ibm1 pass; the 2 currently-matching candidates from the corpus survey also pass).

### 1.2 Corpus Survey: Candidate Models

Corpus query (filtered to `pipeline_status` not `skipped`):

```python
# Models with >=2 solve statements AND >=1 X.m reference (case-insensitive)
candidates = []
for mid in in_scope_models:
    text = read(f'data/gamslib/raw/{mid}.gms')
    n_solves = count(re.findall(r'^\s*solve\b', text, re.IGNORECASE | re.MULTILINE))
    em_refs = count(re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*\.[mM][\s\(]', text))
    if n_solves >= 2 and em_refs >= 1:
        candidates.append((mid, n_solves, em_refs))
```

**Result: 14 candidates (2026-04-21 snapshot):**

| Model | Solves | `eq.m` refs | Current pipeline state | Approach A expected | Notes |
|---|---|---|---|---|---|
| `saras` | 7 | 16 | translate=success / solve=failure | **FLAG (target)** | Canonical case from ISSUE_1270 |
| `msm` | 5 | 5 | not in pipeline | NEEDS EMPIRICAL CHECK | |
| `sparta` | 4 | 1 | translate=success / solve=success / **match** | **MUST NOT FLAG** (regression canary) | |
| `gussex1` | 3 | 4 | not in pipeline | NEEDS EMPIRICAL CHECK | |
| `otpop` | 3 | 2 | translate=success / solve=success / mismatch (rd=0.81) | needs verification | high rd may indicate driver miss |
| `srcpm` | 2 | 7 | not in pipeline | NEEDS EMPIRICAL CHECK | |
| `demo7` | 2 | 2 | not in pipeline | NEEDS EMPIRICAL CHECK | |
| `qp3` | 2 | 2 | not in pipeline | NEEDS EMPIRICAL CHECK | `ydefb.m(t) = ydefa.m(t)` is suspicious |
| `spbenders1` | 2 | 2 | not in pipeline | likely flag (Benders) | |
| `spbenders2` | 2 | 2 | not in pipeline | likely flag (Benders) | |
| `spbenders4` | 2 | 2 | not in pipeline | likely flag (Benders) | |
| `turkey` | 2 | 2 | translate=success / solve=failure | needs verification | |
| `gussrisk` | 2 | 1 | translate=success / solve=success / **match** | **MUST NOT FLAG** (regression canary) | |
| `imsl` | 2 | 1 | translate=success / solve=success / mismatch (rd=0.98) | needs verification | high rd may indicate driver miss |

**Survey caveat:** the regex heuristic doesn't strip `*`-comments perfectly (saras's loop-bracketing tripped a sub-survey's loop tracking). Sprint 25 implementation should re-run the candidate list against the parser-state IR rather than raw-text grep.

### 1.3 Test-Fixture Matrix

Sprint 25 implementation lands tests under `tests/unit/validation/test_driver.py` and `tests/integration/test_decomp_skipped.py` covering 4 scenarios:

| Fixture | Pattern | Expected gate result |
|---|---|---|
| **F1: saras-style** | 2 declared models + 2 solves, top-level `param(idx) = eq.m(idx)`, then `param` referenced in second model's constraint body | **flag** (`is_driver=True`, exit 4) |
| **F2: post-solve reporting** | 1 declared model + 1 solve, top-level `report.value = eq.m`, parameter NOT used in any constraint body (display only) | **must NOT flag** (current ibm1 / single-solve baseline preserved) |
| **F3: multi-stage display** | 2 declared models + 2 solves, top-level `report.value = eq.m` between solves, parameter NOT used in any constraint body | **must NOT flag** (this is the sole reason Approach A is needed over Approach B) |
| **F4: partssupply-style `var.l` reporting** | 2 declared models + 2 solves, `var.l` reads (NOT `eq.m`) used in next iteration's constraint | **must NOT flag** (Approach A scopes to `.m` only; `.l` is out of scope unless explicitly extended later) |

### 1.4 Code-Site Identification

**Single function to extend:** [`src/validation/driver.py:151`](../../../../src/validation/driver.py#L151) `_collect_equation_marginals` and the calling code at [`src/validation/driver.py:204–211`](../../../../src/validation/driver.py#L204) inside `scan_multi_solve_driver`.

**Current scope** (line 204–211):

```python
# Only count equation-marginal accesses whose enclosing loop body
# also contains a ``solve`` — a one-off ``eq.m`` after a single
# solve (post-solve reporting) does not make the script a driver.
equation_marginals: list[tuple[str, str]] = []
for loop_stmt in model_ir.loop_statements or []:
    if not isinstance(loop_stmt, LoopStatement):
        continue
    if not any(_tree_contains_solve(stmt) for stmt in loop_stmt.body_stmts or []):
        continue
    for stmt in loop_stmt.body_stmts or []:
        _collect_equation_marginals(stmt, equation_names, equation_marginals)
```

**Extension** (Sprint 25 implementation sketch):

```python
# Existing: collect from solve-containing loops (decomp/danwolfe).
# New: also collect top-level eq.m reads whose receiving parameter is later
# referenced in another declared model's constraint body (saras pattern).
top_level_marginals = _collect_top_level_marginals_with_param_feedback(
    model_ir, equation_names
)
equation_marginals.extend(top_level_marginals)

# ...
def _collect_top_level_marginals_with_param_feedback(
    model_ir: ModelIR,
    equation_names: frozenset[str],
) -> list[tuple[str, str]]:
    """Approach A: flag eq.m reads whose receiving parameter feeds a constraint body."""
    # 1. Walk top-level statements (not inside any loop): find assignments
    #    `param = expr involving X.m` where X in equation_names. Collect (param, X).
    # 2. Build a set of all parameter names referenced inside any model's
    #    constraint body (model_ir.equations[*].lhs_rhs).
    # 3. Emit (X, "m") for each (param, X) where param is in the set from step 2.
    ...
```

The two new helpers (`_collect_top_level_marginals_with_param_feedback` + a `_param_referenced_in_any_constraint_body` inner helper) add ~40–60 lines.

### 1.5 Regression Guards

Must continue to pass (already in `tests/unit/validation/test_driver.py`):

- `test_scan_ibm1_one_model_many_solves_is_not_driver` — ibm1 (1 model, 5 solves on it).
- `test_scan_partssupply_style_variable_level_is_not_driver` — partssupply (2 models, `var.l` reads only, no `eq.m`).

New tests added by Sprint 25 implementation:

- `test_scan_saras_style_top_level_marginal_with_feedback_is_driver` — F1 fixture.
- `test_scan_post_solve_reporting_no_constraint_feedback_is_not_driver` — F2 fixture.
- `test_scan_multi_stage_display_no_constraint_feedback_is_not_driver` — F3 fixture.

### 1.6 Effort Estimate

| Activity | Hours |
|---|---|
| Implementation: `_collect_top_level_marginals_with_param_feedback` + caller wiring | 1.5–2 |
| Unit tests (4 fixtures) | 1 |
| Integration test (saras CLI exit-4) | 0.5 |
| Corpus verification: re-run on the 14 candidates against the actual IR; confirm gussrisk + sparta don't flag | 0.5–1 |
| **Total** | **3.5–4.5h** |

Alignment: ISSUE_1270 estimated 2–3h for Approach A + tests; this design adds ~1h for the corpus verification step (necessary safety because the survey is regex-based, not IR-based).

---

## Section 2 — #1271 Dispatcher Refactor

### 2.1 Unified Signature

**Committed:** module-level `_loop_tree_to_gams(node, *, token_subst=None)` per ISSUE_1271's proposal:

```python
def _loop_tree_to_gams(
    node: object,
    *,
    token_subst: Mapping[str, str] | None = None,
) -> str:
    """Walk a loop-body subtree and emit GAMS source.

    When ``token_subst`` is None (default), behavior is identical to the
    pre-refactor ``_loop_tree_to_gams``. When provided, ID tokens are
    rewritten through the map during emission, matching the behavior
    previously in ``_loop_tree_to_gams_subst_dispatch``.
    """
```

The substitution point is a **single inline lookup** at every ID-emission branch:

```python
if isinstance(node, Token) and node.type == "ID":
    name = str(node)
    if token_subst is not None:
        name = token_subst.get(name.lower(), name)
    return name
```

### 2.2 Caller Inventory

**Module-level `_loop_tree_to_gams` (current canonical):**

- Defined: [`src/emit/original_symbols.py:2556`](../../../../src/emit/original_symbols.py#L2556)
- Internal recursive call sites: many (inside the function body itself; exact grep count is implementation-dependent and not load-bearing for the refactor — the refactor preserves every existing call site by design)
- Direct same-module callers (in `src/emit/original_symbols.py`): present (e.g., `emit_loop_statements` and other emission helpers around lines 2780, 2782, 2784, 2786, 2986, 3368) — these continue to work unchanged because the new `token_subst` kwarg is optional and defaults to `None` (canonical behavior)
- Callers outside this module (elsewhere in `src/`): none
- Test imports of `_loop_tree_to_gams`: many in `tests/unit/emit/test_original_symbols.py` (multiple test methods import the function locally) — all continue to work unchanged via the optional-kwarg default

**Nested `_loop_tree_to_gams_subst_dispatch` (substituting variant):**

- Defined: [`src/emit/original_symbols.py:3047`](../../../../src/emit/original_symbols.py#L3047), nested inside `emit_pre_solve_param_assignments` (line 2991)
- Wrapper helper: `_tree_to_gams_subst` at [line 3026](../../../../src/emit/original_symbols.py#L3026), also nested
- External callers: **0** (it's nested inside one function, not module-level)
- Single in-function call site: [line 3271](../../../../src/emit/original_symbols.py#L3271): `gams_text = _tree_to_gams_subst(stmt, sub)`
- External callers (tests): the test file references the `_subst_dispatch` name in a comment only ([`tests/integration/test_pre_solve_dollar_condition.py:6`](../../../../tests/integration/test_pre_solve_dollar_condition.py#L6)) — no actual import.

**Refactor scope is well-bounded:** the substituting variant is fully encapsulated inside one function; removing it touches one file (`src/emit/original_symbols.py`) and one call site (line 3271).

### 2.3 Refactor Plan

**Step 1 — Extend module-level `_loop_tree_to_gams`:**

- Add `token_subst: Mapping[str, str] | None = None` keyword parameter.
- Add a module-level helper `_subst_id(name: str, token_subst: Mapping[str, str] | None) -> str` that returns `token_subst.get(name.lower(), name) if token_subst is not None else name`.
- Apply `_subst_id(...)` at every ID-emission branch (~3–5 sites in the function body).
- Recursive calls pass `token_subst` through unchanged.

**Step 2 — Inside `emit_pre_solve_param_assignments`:**

- Remove nested `_tree_to_gams_subst` (line 3026) and `_loop_tree_to_gams_subst_dispatch` (line 3047). Both definitions deleted in their entirety.
- Replace the single call site at line 3271 with: `gams_text = _loop_tree_to_gams(stmt, token_subst=sub)`.

**Step 3 — Backward-compatibility window:**

- **Not needed.** No external module imports `_loop_tree_to_gams_subst_dispatch`. The nested name is purely internal.
- The canonical `_loop_tree_to_gams` keeps its name; existing callers (4 tests) continue to work without changes — the new keyword argument is optional and defaults to the pre-refactor behavior.

### 2.4 Byte-Diff Regression Strategy

**Pre/post comparison across all currently-translating models** per ISSUE_1271 §Scope of Work:

```bash
# 1. Snapshot pre-refactor MCP outputs (on main branch before refactor PR)
mkdir -p /tmp/sprint25-dispatcher-pre
.venv/bin/python -c "
import json, subprocess, os
from pathlib import Path
with open('data/gamslib/gamslib_status.json') as f: data = json.load(f)
translating = [
    m['model_id'] for m in data['models']
    if (m.get('nlp2mcp_translate') or {}).get('status') == 'success'
]
env = os.environ.copy()
env['PYTHONHASHSEED'] = '0'  # Pin parser determinism per Task 3 #1283 mitigation
out = Path('/tmp/sprint25-dispatcher-pre')
for mid in sorted(translating):
    subprocess.run(
        ['.venv/bin/python', '-m', 'src.cli', f'data/gamslib/raw/{mid}.gms',
         '-o', str(out / f'{mid}_mcp.gms'), '--quiet'],
        env=env,
    )
print(f'Snapshotted {len(translating)} models')
"

# 2. Refactor lands on the branch.
# 3. Post-refactor regen + diff
mkdir -p /tmp/sprint25-dispatcher-post
# (same loop into /tmp/sprint25-dispatcher-post)
diff -r /tmp/sprint25-dispatcher-pre /tmp/sprint25-dispatcher-post
# Expected: empty output (zero byte diffs)
```

**Acceptance:** `diff -r` produces empty output. Any non-zero diff requires investigation before merging the refactor PR.

**Currently-translating model count (2026-04-21 snapshot):** 135 models per `gamslib_status.json` `nlp2mcp_translate.status == "success"`. (ISSUE_1271 estimated "~60 models"; the actual count is ~2× because translate-success now includes models recovered post-PR #1274 timeout doubling.)

### 2.5 Out of Scope

Per ISSUE_1271 §"Explicitly Out of Scope":

- **Do not** fix emission bugs in this PR. Existing bugs in either dispatcher (e.g., #1268 — decomp `bound_scalar` handler; should already be added to subst dispatch by the time #1271 lands) remain as bugs after the refactor; they're fixed in separate PRs.
- **Do not** rename handler methods inside the unified dispatcher. Keep patches small and obviously equivalent.

### 2.6 Effort Estimate

| Activity | Hours |
|---|---|
| Step 1: extend module-level dispatcher with `token_subst` parameter | 1–1.5 |
| Step 2: remove nested duplicates inside `emit_pre_solve_param_assignments` | 0.5 |
| Step 3: byte-diff regression (snapshot + diff across 135 models) | 1.5–2 |
| Step 4: unit-test additions (with/without `token_subst` parity tests) | 1 |
| **Total** | **4–5h** |

Alignment: ISSUE_1271 estimated 4–6h. This design's lower bound is tighter (4h) because the caller inventory shows zero external imports, removing backward-compatibility complexity.

---

## Section 3 — Day Allocation

Per [`DESIGN_ALIAS_AD_ROLLOUT.md`](DESIGN_ALIAS_AD_ROLLOUT.md) §Section 5 parallel-work table, the alias-AD rollout schedule has the following candidate windows for Priority 3/4 work:

### Option A: Day 11 (post-Checkpoint-2 cleanup) — RECOMMENDED

- Sprint 25 Day 11 is currently allocated to "Pattern E routing decisions + residual Pattern A/C work" (Priority 1 cleanup).
- Both Priority 3 (#1270, ~3.5–4.5h) and Priority 4 (#1271, ~4–5h) fit in a single Day 11 / Day 12 pair if no Phase 4 cleanup blockers arise.
- **Pros:** Keeps both small priorities decoupled from Priority 1's critical path; lands them when alias-AD outcomes are known so the Match-target accounting is finalized first.
- **Cons:** Compressed Day 11 if Phase 4 cleanup runs long.

### Option B: Days 4–6 alongside Priority 2 Batch 2

- Priority 2 Batch 2 (#1279 + #1276 + #1281) is allocated to Days 3–4. A separate contributor could pick up #1270 and #1271 on Days 5–6.
- **Pros:** Earlier landing → integrated into Day 8 highest-leverage day's metrics.
- **Cons:** Requires a separate contributor; risks alias-AD merge conflicts in `src/validation/driver.py` (none expected, but adds review burden).

### Recommendation

**Option A (Day 11)** as the default; switch to Option B if a second contributor is available for Days 5–6 dispatch and Priority 1's Phase 1–2 progress permits.

---

## Section 4 — Cross-Reference

| Source | Used For |
|---|---|
| ISSUE_1270 §"Candidate Approaches" | §1.1 approach commit |
| ISSUE_1270 §"Scope of Work" | §1.4 code-site identification |
| ISSUE_1270 §"Regression Guards" | §1.5 regression-guard test list |
| ISSUE_1271 §"Proposal" | §2.1 unified signature |
| ISSUE_1271 §"Scope of Work" | §2.3 refactor plan + §2.4 byte-diff strategy |
| `src/validation/driver.py:151–225` | §1.4 current-code reading |
| `src/emit/original_symbols.py:2556 (canonical)`, `:2991–3170 (subst-nested)` | §2.2 caller inventory |
| `data/gamslib/gamslib_status.json` (2026-04-21 snapshot) | §1.2 corpus survey |
| Sprint 24 KU-29, KU-30 | Source of these two issues (carryforward to Sprint 25) |

---

## Appendix A — Sprint 25 Implementation Checklist

Lift this list verbatim into the Sprint 25 Day 11 (or Days 5–6) PR description.

### #1270 (Priority 3)

- [ ] Implement `_collect_top_level_marginals_with_param_feedback` in `src/validation/driver.py`
- [ ] Wire it into `scan_multi_solve_driver` — append to `equation_marginals` list before dedup
- [ ] Add 4 unit-test fixtures (F1–F4) in `tests/unit/validation/test_driver.py`
- [ ] Add CLI integration test for `saras` exit-code 4 in `tests/integration/test_decomp_skipped.py`
- [ ] Re-run the 14-candidate corpus survey against the IR (not regex) and confirm gussrisk + sparta still pass
- [ ] Update `data/gamslib/gamslib_status.json` for any newly-flagged corpus model (mark as `multi_solve_driver_out_of_scope`)
- [ ] Quality gate: `make typecheck && make lint && make format && make test`
- [ ] PR description includes: which corpus models now exit 4 (saras + N more), which canaries verified non-flagging

### #1271 (Priority 4)

- [ ] **Pre-refactor snapshot:** generate MCP outputs for all currently-translating models (~135) into `/tmp/sprint25-dispatcher-pre/` with `PYTHONHASHSEED=0`
- [ ] Extend `_loop_tree_to_gams` in `src/emit/original_symbols.py` with `token_subst` keyword parameter
- [ ] Add `_subst_id` module-level helper
- [ ] Remove nested `_tree_to_gams_subst` and `_loop_tree_to_gams_subst_dispatch` from `emit_pre_solve_param_assignments`
- [ ] Update single call site (line ~3271) to use `_loop_tree_to_gams(stmt, token_subst=sub)`
- [ ] Add parity unit tests under `tests/unit/emit/` covering both call shapes
- [ ] **Post-refactor regen + diff:** generate MCP outputs into `/tmp/sprint25-dispatcher-post/` and `diff -r` against pre-snapshot — must be empty
- [ ] Quality gate: `make typecheck && make lint && make format && make test`
- [ ] PR description includes: confirmation of zero byte-diffs across 135 models
- [ ] CHANGELOG entry under `[Unreleased]` documenting the parameter addition / signature change (and the removal of the nested `_tree_to_gams_subst` / `_loop_tree_to_gams_subst_dispatch` helpers from `emit_pre_solve_param_assignments`)

# Translation Timeout Option 1 Short-Circuit Redesign — Symbolic-Instance Handling in AD/Emit Pipeline

**GitHub Issue:** [#1385](https://github.com/jeffreyhorn/nlp2mcp/issues/1385)
**Status:** OPEN (filed Sprint 26 Day 4, 2026-05-12 — after Day 4 Priority 4 rollback)
**Severity:** Medium — affects 5 GAMSlib `translate_timeout` models that Option 1 was meant to recover (srpchase, iswnm, sarf, mexls, nebrazil) plus blocks any downstream Solve / Match gain those models would have produced post-recovery.
**Date:** 2026-05-12
**Last Updated:** 2026-05-12
**Affected Models:** srpchase (#885 / #931 / #932 / #1185 / #1228 carry forward), iswnm, sarf, mexls, nebrazil
**Target Sprint:** Sprint 27 (10–16h across three sub-phases)
**Cross-references:**
- `docs/planning/EPIC_4/SPRINT_26/DESIGN_OPTION_1_SHORT_CIRCUIT.md` — Sprint 26 Prep Task 6 design (full original spec; needs revision per this issue's findings)
- Sprint 26 Day 4 PR (Day 4 Priority 4 reclassification PR — when retitled)
- Sprint 26 Day 3 PR #1382 + Sprint 27 #1381 — same root-cause class (design assumed downstream handling that doesn't exist)
- Sprint 25 `PROFILE_HARD_TIMEOUTS.md` §3.1 — original Option 1 proposal

---

## Problem Summary

Sprint 26 Day 4 attempted to implement the Option 1 short-circuit per Task 6 design ([`DESIGN_OPTION_1_SHORT_CIRCUIT.md`](../planning/EPIC_4/SPRINT_26/DESIGN_OPTION_1_SHORT_CIRCUIT.md)). The translate-time savings were achieved (srpchase 846s → 5.7s; iswnm 61.1s recovered) **but the resulting MCP emit was structurally wrong** — the Copilot reviewer caught broken multiplier references like `nu_slack("srn")` and `lam_demand("srn")` where `srn` is a SET NAME (subset of `n`), not a valid element of `n` (which has elements `n0..n1000`). The KKT system was missing entire `J_g^T·lam_demand` cross-terms because Jacobian entries were dropped when the placeholder index didn't match concrete elements during AD differentiation.

Day 4 src/ changes rolled back (commit `243fe578` reverted on the Day 4 PR branch). Option 1 short-circuit deferred to Sprint 27 for a builder-pipeline-aware redesign.

---

## Symptom — Wrong consolidated emit on srpchase (Day 4 broken impl)

Day 4 commit `243fe578` translated srpchase in 5.7s (vs Sprint 25 main's 846s) — translation completed under the design's `<10s` target. But the resulting emit had structural KKT errors:

```gams
stat_y(n).. ((((-1) * 1$(ancestor(srn,srn))) * nu_slack("srn"))$(srn(srn)))$((not leaf(srn))) + ((((-1) * 1$(ancestor(srn,srn))) * lam_demand("srn"))$(srn(srn)))$(leaf(srn)) - piL_y(n) =E= 0;

stat_x(n).. (prob(n) * price(n) - piL_x(n))$(srn(n)) =E= 0;
```

Three concrete failures visible in this 2-line excerpt:

1. **`nu_slack("srn")` / `lam_demand("srn")` literal-string indices**: `srn` is a SET NAME (subset of `n`), not a valid element of `n`. GAMS would emit UEL/domain errors at runtime.
2. **`1$(ancestor(srn,srn))` membership-test on literal strings**: same root cause — the placeholder `("srn",)` flowed through downstream code as a concrete element.
3. **`stat_x(n)` missing the `comp_demand` cross-term**: the Jacobian entries involving `x(srn)` got dropped during AD differentiation because `_diff_varref` requires exact index matches; with symbolic indices the entries become 0 and the `J_g^T·lam_demand` term doesn't appear.

---

## Root Cause

The Day 4 implementation followed the Task 6 design doc §2.3 verbatim:

```python
def _build_symbolic_instance_placeholder(eq_domain):
    return [tuple(eq_domain)]  # e.g., [("srn",)] for srpchase's slack(srn)$..
```

The design asserted: *"The downstream emit path already handles symbolic-index instances (see Sprint 25 #1306 / #1308 prior art on emitting `stat_<eq>(i)..` equation heads with a body that references the equation domain symbolically)."*

**This assertion was wrong.** The Sprint 25 #1306 / #1308 prior art is for INDEXED stationarity equations where the equation HEADER `stat_<eq>(i)..` BINDS the symbolic index `i`. The body's symbolic references to `i` are valid because they're bound by the header.

The Day 4 placeholder is different: it tries to use the SET NAME (`"srn"`) as if it were an instance/element value. The downstream AD pipeline (`src/ad/constraint_jacobian.py::_diff_varref` etc.) treats the placeholder tuple `("srn",)` as a CONCRETE element string per the existing Cartesian-enumeration contract — NOT as a bound symbol. So `"srn"` becomes a literal quoted string in the emit.

This is the **same root-cause class** as Sprint 26 Day 3 Phase B reclassification (Sprint 27 #1381): the design doc validated against an assumption that the downstream pipeline would handle a new shape, but the assumption didn't hold in practice. Same lesson: design-time inspection of consumer code is not enough — empirical end-to-end verification (GAMS `action=c` compile + KKT body shape check vs hand-derived Lagrangian) is required.

---

## Why iswnm "looked OK" but srpchase didn't

Day 4 noticed iswnm translated successfully (61.1s under 180s budget) and the emit looked structurally reasonable on quick inspection. The discrepancy:

- **iswnm**'s equations have `eq_domain` like `(c, m)`, `(n, n1, m)` — none of those names happen to coincide with bound subset names that AD needs to substitute against. The placeholder `("c", "m")` for an iswnm equation would hit the same `_diff_varref` bug, but iswnm's emit happens not to expose the symptom on quick scan because the affected stationarity equations are structured differently.
- **srpchase**'s equations are explicitly declared `slack(srn)$..` with `srn` as the eq_domain. The placeholder `("srn",)` flows directly into multiplier references like `nu_slack(...)`, immediately producing the literal-string bug.

iswnm's emit was NOT verified against a hand-derived KKT on Day 4 — only against the "translation completes" criterion. It is likely also broken in subtle ways that didn't surface in a quick visual scan. Sprint 27 redesign work must include hand-derived KKT verification for both srpchase + iswnm.

---

## Proposed Fix Approach — Three Sub-Phases

Sprint 27 work, ~10–16h. Likely structured as:

### Phase 1 (~3–4h): Inventory + design choice

Inventory all AD/emit code paths that consume `enumerate_equation_instances` results and assume concrete element indices:

- `src/ad/constraint_jacobian.py::_diff_varref` (and friends — `_diff_paramref`, `_diff_setmembership`, etc.): Jacobian-construction sites that match indices for symbolic differentiation.
- `src/kkt/stationarity.py::_build_indexed_stationarity_expr`: emits `stat_<eq>(...)..` headers + body — needs to know whether the body should reference symbolic or concrete indices.
- `src/kkt/complementarity.py`: same treatment for `lam_<eq>` references.
- `src/emit/equations.py::emit_equation_definition`: serializes the equation to GAMS — currently quotes index values like `"srn"` because they're treated as element names.

Then choose between:

- **Option A — Symbolic-instance handling end-to-end (more invasive, more general):** modify all the consumer sites above to handle symbolic indices alongside concrete ones. Symbolic indices flow through as bound-set names; emit produces equation heads like `stat_slack(srn)..` with multiplier references like `nu_slack(srn)` (no quotes), gated by the runtime `$cond` from the source equation.
- **Option B — Alternative short-circuit shape (narrower, easier):** instead of returning a single symbolic instance, emit at translation time a single equation entry that PRESERVES the runtime `$cond` as an emit-time guard on every concrete instance. Pseudocode: `for elem in parent_set.members: emit stat_<eq>(elem)$cond_at_runtime`. The `$cond` is the user's original SetMembershipTest, evaluated at GAMS runtime per concrete instance. This avoids the symbolic-instance correctness issues but requires guard-emission infrastructure.

Phase 1 deliverable: a sub-design doc proposing Option A or B with specific patch sites and a rough effort estimate.

### Phase 2 (~4–6h): Implementation

Per the Phase 1 choice, implement either Option A or Option B. Whichever option is chosen, the implementation must:

- Preserve byte-stability for any equation whose condition is NOT a single dynamic-subset SetMembershipTest (current Day 4 verified this property — Tier 0 + Tier 1 11/11 byte-identical).
- Produce GAMS-compile-clean emit on srpchase + iswnm (verified via `gams action=c` with 0 error markers).
- Match a hand-derived Lagrangian gradient for the affected equations on srpchase + iswnm.

### Phase 3 (~3–6h): Integration test coverage

The Day 4 integration test (`test_srpchase_translate_completes_under_30s`) only verified "translation completes within 30s" + "stat_ appears in the output" — not emit correctness. Sprint 27 must add:

- **`tests/integration/ad/test_srpchase_emit_correct.py`** (new file): assert specific KKT body shapes match hand-derived Lagrangian for srpchase's `slack(srn)`, `demand(leaf(srn))` equations. Verify no quoted-literal indices.
- **`tests/integration/ad/test_iswnm_emit_correct.py`** (new file): same shape verification for iswnm's `nbal(n,m)` / `canaldiv(c,m)` / `f(n,n1,m)` / `rcont(n,m)` equations.
- **GAMS compile-clean check**: `gams action=c lo=2` on both srpchase + iswnm regenerated MCP artifacts must produce 0 error markers.
- **Tier 0 + Tier 1 (11 models) byte-identical regression**: must continue to pass.

---

## Tests to Add (Sprint 27)

### Phase 1 deliverable

Sub-design doc (no test changes).

### Phase 2

`tests/unit/ad/test_enumerate_equation_instances_short_circuit.py`:

- **Test 1 — positive case (single SetMembershipTest)**: same as Day 4's Test 1 but with assertion strengthened to verify the result is *correctly substitutable in downstream emit* — not just "matches the placeholder". E.g., assert the placeholder is something that downstream `_build_indexed_stationarity_expr` correctly serializes to a symbolic equation head (Option A) OR that the runtime `$cond` is correctly emitted as a per-instance guard (Option B).
- **Test 7 — emit correctness regression** (NEW): build a minimal ModelIR with a dynamic-subset condition, run the full pipeline (translate + KKT + emit), assert the emitted body has no quoted-literal subset names and references multipliers symbolically.

### Phase 3 (integration)

- **`tests/integration/ad/test_srpchase_emit_correct.py`**: hand-derived KKT shape check.
- **`tests/integration/ad/test_iswnm_emit_correct.py`**: same.
- **`tests/integration/ad/test_srpchase_gams_compile_clean.py`**: `gams action=c` produces 0 error markers.
- **`tests/integration/ad/test_iswnm_gams_compile_clean.py`**: same.

Plus the existing Day 4 `test_srpchase_translate_completes_under_30s` test (which verifies translation time bound) is kept unchanged.

---

## Files Involved

- `src/ad/index_mapping.py`:
  - `enumerate_equation_instances` — gate-site insertion needs to be re-thought (Phase 1 design choice determines exact form).
  - `_is_dynamic_subset_membership_short_circuit` — predicate is conservatively scoped (Day 4 added; rolled back); will be re-introduced as part of Phase 2.
  - `_build_symbolic_instance_placeholder` — Day 4 helper that proved insufficient; will be replaced (Option A) or removed (Option B).
- `src/ad/constraint_jacobian.py`:
  - `_diff_varref` (and friends) — index-matching logic that currently assumes concrete elements.
- `src/kkt/stationarity.py`:
  - `_build_indexed_stationarity_expr` — equation-header emission with symbolic vs concrete indices.
- `src/kkt/complementarity.py`:
  - `lam_<eq>` reference emission.
- `src/emit/equations.py`:
  - `emit_equation_definition` — index-value quoting logic.
- `src/ir/condition_eval.py`:
  - `SetMembershipTest` evaluation path — alongside the index_mapping changes per Day 4 attempt.
- `tests/unit/ad/test_enumerate_equation_instances_short_circuit.py` (Day 4 added; rolled back; will be re-introduced).
- `tests/integration/ad/test_srpchase_translate_under_budget.py` (Day 4 added; rolled back; will be re-introduced).
- `tests/integration/ad/test_srpchase_emit_correct.py` (NEW — Sprint 27 must add).
- `tests/integration/ad/test_iswnm_emit_correct.py` (NEW — Sprint 27 must add).

---

## Estimated Effort

| Sub-phase | Scope | Effort |
|---|---|---|
| Phase 1 | Inventory consumer sites + Option A vs B design choice + sub-design doc | 3–4h |
| Phase 2 | Implement chosen option (symbolic-instance handling OR runtime-guard emission) | 4–6h |
| Phase 3 | Integration tests verifying emit CORRECTNESS (not just translation completion) on srpchase + iswnm | 3–6h |
| **Total** | | **10–16h** |

Plus regression coverage (Tier 0 + Tier 1 byte-stable) and PR14 obligation (regenerated `srpchase_mcp.gms` + `iswnm_mcp.gms` golden artifacts with reviewer verification of emit shape).

---

## Scope and Sprint Routing

**Target: Sprint 27.** Sprint 26 Day 4 reclassification documents this deferral. Sprint 26 schedule impact:

- Sprint 26 Translate target relaxed: `≥ 132/142` (was `+2 from Priority 4`) → `maintain ≥ 130/142` (no Priority 4 contribution this sprint).
- Day 5 Checkpoint 1 criteria updated: "Priority 4 Option 1 short-circuit: srpchase translates" reclassified to `n/a — deferred to Sprint 27 #1385`.
- Day 8 buffer (already free per Day 3 reschedule) absorbs whatever forward-pull alternatives the user chooses; Day 9 Priority 5 work remains as planned.

The 5 translate-timeout candidate issues (#885, #931, #932, #1185, #1228) carry forward to Sprint 27 — they remain `sprint-26` labeled until Sprint 27 implementation work re-attempts the recovery.

---

## Lessons Learned

This is the second Sprint 26 reclassification (after Day 3 Pattern B → Sprint 27 #1381) where a prep-task design assumed downstream pipeline behavior that didn't hold in practice. Both shared the same diagnostic gap:

- **Prep-task validation at the design stage** (read code; identify patch sites; verify nothing obvious blocks the change) is necessary but insufficient.
- **Empirical end-to-end verification** — actually running the pipeline AND verifying emit correctness against hand-derived expected output — must be part of the design-validation phase, not deferred to implementation day.

For Sprint 27 prep:

- Pattern C Phase B redesign (#1381) and Option 1 short-circuit redesign (this issue) should both have a Phase 0 sub-task: "translate one concrete target model with a prototype patch + verify GAMS compile-clean + KKT body shape against hand-derived Lagrangian" BEFORE committing to the implementation budget.

---

## Related

- **Sprint 25 PROFILE_HARD_TIMEOUTS.md §3.1** — original Option 1 proposal
- **Sprint 26 Task 6 DESIGN_OPTION_1_SHORT_CIRCUIT.md** — design that turned out to be incomplete
- **Sprint 26 Day 4 PR** — Priority 4 reclassification PR (when retitled)
- **Sprint 27 #1381** — Pattern C Phase B redesign (same class of design-validation gap)
- **Sprint 26 Day 4 Priority 5 #1334 re-investigation PR** — separate docs-only PR; not affected by this issue
- **#885, #931, #932, #1185, #1228** — translate-timeout candidates that carry forward to Sprint 27 alongside this issue

# Translation Timeout Option 1 Short-Circuit Redesign — Symbolic-Instance Handling in AD/Emit Pipeline

**GitHub Issue:** [#1385](https://github.com/jeffreyhorn/nlp2mcp/issues/1385)
**Status:** PARTIALLY DONE (Sprint 27 Day 7) — translate-time short-circuit LANDED; the runtime-guard equation-body re-emit + `J_gᵀ·lam` cross-terms are **REPLAN'd → Sprint 30** (Sprint 29 Day 9: smallest target = sarf; cross-terms hand-derived and banked, but the atomic symbolic-emit is the Sprint-26-Day-4-failed architecture — intractable to de-risk in budget; see the Day-9 PROCEED/REPLAN Signal below). _(was: DEFERRED → Sprint 29; re-deferred at Sprint 28 Day 11 — the day was consumed by the camcge Task-6 gate + the #1374/#1400 cleanups.)_
**Severity:** Medium — affects 5 GAMSlib `translate_timeout` models that Option 1 was meant to recover (srpchase, iswnm, sarf, mexls, nebrazil) plus blocks any downstream Solve / Match gain those models would have produced post-recovery.
**Date:** 2026-05-12
**Last Updated:** 2026-06-20 (Sprint 28 Day 13 closeout — re-deferred to Sprint 29; the cross-term half remains the atomic re-emit + `J_gᵀ·lam` work, unchanged in scope)

## Sprint 27 Day 7 (2026-06-07) — translate-time-only short-circuit LANDED (cross-terms → Sprint 28)

Per the Day-0 SCOPED-PROCEED verdict (`PRIORITY_3_RISK_ASSESSMENT.md` §4.5) and the Option 1 re-plan, Sprint 27 lands the **translate-time-only** half of Option B and **defers** the cross-term half to Sprint 28.

**Landed (`src/ad/index_mapping.py`):** `enumerate_equation_instances` now skips AD enumeration for the srpchase **dynamic-subset Cartesian blow-up shape** — generalized from the Day-0 model-name guard (`'purchase'`) to a tight STRUCTURAL gate (`_is_blowup_dynamic_subset_equation`): a 1-D **dynamic** subset (0 static members) of a **large** parent set (≥100 members), with a single (optionally negated) `SetMembershipTest` domain condition, whose body sums over a **2-D set** (the `sum(ancestor(srn,n), …)` Cartesian filter). For that shape it returns `[]`, skipping the `differentiate_expr`/`simplify` blow-up (the real >180s cost per the Day-0 profiling).

**Verification:** srpchase translate **6.56s** (was >180s `translate_timeout`); GAMS `action=c` compile-clean; 0 quoted-literal set-name indices. **Blast radius = srpchase ONLY** — full-corpus byte scan: 136 models byte-identical (gate didn't fire), the 7 pre-existing FAILs unchanged, and the parse-timeout models are `translate_timeout` both before and after (no bucket change). 5 new unit tests (`tests/unit/ad/test_blowup_enumeration_skip.py`). **This is a Translate-bucket gain** (srpchase: `translate_timeout` → translate-success), **NOT a Solve/Match gain** — iswnm/mexls/nebrazil/sarf do not reach `compare_match` this sprint.

**DEFERRED to Sprint 28 (coupled — must land together):**
1. The **runtime-guard equation-body re-emit** at `src/kkt/stationarity.py` — re-emit the skipped `slack`/`demand` as `sum(<bound>$(<predicate>), <body>)` runtime-guarded GAMS equations so the constraints appear in the MCP.
2. The **`J_gᵀ·lam` cross-terms** — the skipped equations' contributions to every variable's stationarity (`∂slack/∂y · nu_slack`, etc.). The AD layer enumerates ZERO instances for the skipped equations, so these are absent.

Re-emitting the constraints (1) WITHOUT the cross-terms (2) would create an inconsistent MCP (multipliers with no complementarity coupling), so both are deferred together. The current landed scope produces a smaller, internally-consistent (slack/demand-free) MCP that compiles — translate gain only.
**Affected Models:** srpchase, iswnm, sarf, mexls, nebrazil (5 GAMSlib `translate_timeout` models that Option 1 was meant to recover; srpchase has no separate carryforward issue — it's the primary Option 1 target).
**Related issues** (Sprint 26 `sprint-26` labeled, carrying forward to Sprint 27 alongside this redesign):
- **#885** — sarf: Translation timeout from combinatorial explosion in variable instances
- **#931** — iswnm: Translation timeout — Indus surface water network submodule
- **#932** — nebrazil: Translation timeout — North-East Brazil agricultural model
- **#1185** — mexls (SEQ=210): Translation timeout (large LP)
- **#1228** — iswnm: Translation timeout — empty set causes instance explosion

**Target Sprint:** Sprint 27 (10–16h across three sub-phases)
**Cross-references:**
- `docs/planning/EPIC_4/SPRINT_26/DESIGN_OPTION_1_SHORT_CIRCUIT.md` — Sprint 26 Prep Task 6 design (full original spec; needs revision per this issue's findings)
- Sprint 26 Day 4 PR (Day 4 Priority 4 reclassification PR — when retitled)
- Sprint 26 Day 3 PR #1382 + Sprint 27 #1381 — same root-cause class (design assumed downstream handling that doesn't exist)
- Sprint 25 `PROFILE_HARD_TIMEOUTS.md` §3.1 — original Option 1 proposal

---

## Phase 0: Acceptance Gate

> **Day-0 status (Sprint 29 Prep Task 4, 2026-06-25):** unlike the other Sprint-29 tracks, #1385 is **not** a standard `kkt_residual.py` target at Day-0 — the timeout models do not yet emit a *complete* MCP (the skipped `slack`/`demand` constraints and their `J_gᵀ·lam` cross-terms are absent by design after the Sprint-27 translate-time short-circuit), so there is no warm-startable MCP to read a residual from. The gate is therefore **structural** (hand-derived runtime-guard `stat_*` cross-terms) with an **atomic-landing** requirement; the harness becomes the post-fix verifier once the cross-terms exist.

### Hand-Derived KKT Shape

For each short-circuited constraint `g` (e.g. srpchase `slack(srn)`/`demand(srn)` re-emitted as a runtime-guarded `sum(<bound>$(<predicate>), <body>)`), every primal variable `y` it touches must gain the Jacobian-transpose cross-term in its stationarity:

```
stat_y(...)..  ∂obj/∂y + sum(g, ∂g/∂y · nu_g)  =E= 0      (nu_g for =e=,  lam_g≥0 for =l=/=g=)
```

The re-emitted constraint row and its multiplier coupling must land **together** — re-emitting `g` (so the constraint appears) **without** the `∂g/∂y·nu_g` cross-terms (2) produces an **inconsistent MCP** (a multiplier with no complementarity coupling). This is the load-bearing atomicity constraint.

### Expected Emit Pattern

`<model>_mcp.gms` should contain (1) the runtime-guarded re-emitted constraint `g.. sum(<bound>$(<predicate>), <body>) …` and (2) the matching `+ sum(g, ∂g/∂y·nu_g)` term in **every** `stat_y` that `g` touches — with **no** quoted-set-name multiplier indices (the Day-4 `nu_slack("srn")` bug). (Hypothesis — to be confirmed by the Day-0 trace on the chosen smallest target.)

### Verification Methodology

```bash
# Pick the smallest viable timeout target (Unknown 3.2 — fewest skipped-constraint instances):
for m in iswnm sarf mexls nebrazil; do
  echo "== $m =="; timeout 200 .venv/bin/python -m src.cli data/gamslib/raw/$m.gms -o /tmp/${m}_mcp.gms --quiet && wc -l /tmp/${m}_mcp.gms
done
# After the runtime-guard re-emit + cross-terms land, the harness becomes the verifier:
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/<smallest>.gms --json /tmp/phase0_1385.json
# Structural check: no quoted-set-name multiplier indices (fail loudly if the
# emit is missing — don't let a missing file masquerade as "clean"):
out=/tmp/<smallest>_mcp.gms
if [ ! -f "$out" ]; then
  echo "ERROR: $out not emitted (translate failed?)" >&2
elif grep -qE 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' "$out"; then
  echo "BUG: set-name multiplier index emitted"
else
  echo "clean: no set-name multiplier indices"
fi
```

- **PROCEED (Case b / structural):** the smallest target's hand-derived `stat_*` cross-terms are tractable and the re-emit + cross-terms can land atomically; post-fix harness residual → 0 (Case a).
- **REPLAN:** if even the smallest target's cross-terms are intractable in the budget (the combinatorial instance count remains too large), keep the translate-only short-circuit and re-defer the cross-term half.

### PROCEED/REPLAN Signal

> **🔴 DECIDED — REPLAN to Sprint 30 (Sprint 29 Day 9, 2026-06-30).** Smallest target selected = **sarf** (471 lines, the smallest of iswnm 691 / nebrazil 1021 / mexls 1088). Day-9 trace pinned the blow-up and hand-derived the cross-terms, but the **atomic symbolic-emit implementation is intractable in the Day-9 budget** given the Sprint-26 precedent → re-defer the cross-term half.
>
> **Blow-up diagnosis (sarf).** Three constraints over **2-D dynamic-subset conditions** blow up the AD enumeration: `tbal(g,t)$taskposs(g,t)` (**384** instances), `equipb1(m,t)$equipposs(m,t)` (**648**), `equipb2(n,t)$equipposs(n,t)` (**120**). `taskposs`/`equipposs` are computed from `treq`/`tech` data (sarf.gms:371–384) so they have **zero concrete members at compile time** → `enumerate_equation_instances` includes the **full Cartesian** product ("Including unevaluable instances by default") → `differentiate_expr` blows up (>200s). **The existing srpchase short-circuit (`_is_blowup_dynamic_subset_equation`) is 1-D-only** (`len(eq_domain) != 1` bails) so it does **not** fire on sarf's 2-D shape — sarf currently `translate_timeout`s with no short-circuit.
>
> **Hand-derived cross-terms (the gate deliverable — TRACTABLE).** The main variable `task(g,t,mn,mn)` (4-D) is touched by five guarded constraints; its stationarity is:
> ```
> stat_task(g,t,m,n)$taskposs(g,t)..
>     - (nu_tbal(g,t))$tech(g,m,n)                          [tbal RHS sum, normalized LHS-RHS]
>     + (tadj(g)*nu_tbal(g,t))$(sameas(g,'harvest-c') and sameas(m,'cotton-p') and sameas(n,'self-prop'))
>     + tech(g,m,n)*lam_labor(t)                             [labor]
>     + (tech(g,m,n)*lam_equipb1(m,t))$equipposs(m,t)        [equipb1, m=implement]
>     + (tech(g,m,n)*lam_equipb2(n,t))$equipposs(n,t)        [equipb2, n=power source]
>     + oc(g,m,n)*nu_acost3                                  [acost3]
>     - piL_task(g,t,m,n)  =E= 0;
> ```
> All terms carry the runtime `$taskposs(g,t)`/`$equipposs` guards; sum indices are the stat equation's own domain `(g,t,m,n)` — **no quoted-set-name multiplier indices** (the Day-4 `nu_slack("srn")` bug).
>
> **Why REPLAN (the implementation, not the derivation).** Landing this requires (a) extending the short-circuit gate to the **2-D** dynamic-subset shape AND (b) a **new symbolic runtime-guard cross-term emit path** in `stationarity.py` (the short-circuited equations enumerate **zero** instances, so the cross-terms can't be assembled from per-instance Jacobian entries — they must be built by symbolically differentiating each constraint body parametrically in `(g,t,m,n)`). **This is precisely the architecture that FAILED in Sprint 26 Day 4** (commit `243fe578`, reverted — the `nu_slack("srn")`/`lam_demand("srn")` set-name-literal-index bug + dropped `J_gᵀ·lam` cross-terms). sarf is **strictly harder than srpchase** (4-D `task` × 5 guarded constraints × **nested** `taskposs`/`equipposs` guards, vs srpchase's 1-D `slack`/`demand`). The **atomicity constraint** (Unknown 3.1) forbids banking translate-only (re-emit without correct cross-terms = inconsistent MCP), so there is **no safe partial landing** — it is all-or-nothing, and the "all" is a high-risk architectural rewrite the ~7h budget can't de-risk against the Sprint-26 failure mode. **→ REPLAN to Sprint 30** as a dedicated builder-pipeline-aware symbolic-emit workstream (sarf as the reference target; the hand-derivation above is the banked spec). **No +Translate this sprint** (sarf stays `translate_timeout`).

- **Translate gain only is already banked** (srpchase translate-time short-circuit landed Sprint 27). The Sprint-29 gate is the **cross-term half**: PROCEED only if a smallest-target (`iswnm`/`sarf`/`mexls`/`nebrazil`) has hand-derivable runtime-guard `stat_*` cross-terms that land **atomically** with the constraint re-emit; otherwise re-defer.
- **Traced Fix-Surface (Day-0):** **to be confirmed by the Day-0 trace** — the runtime-guard equation-body re-emit in `src/kkt/stationarity.py` and the `J_gᵀ·lam` cross-term assembly for the short-circuited equations (the AD layer enumerates zero instances for them — `src/ad/index_mapping.py` `enumerate_equation_instances` / `_is_blowup_dynamic_subset_equation`). Trace command: pick the smallest target, hand-derive its skipped-constraint cross-terms, and cite the `file:line` where the re-emit + cross-term must be injected. **Note (Task 5):** the smallest-target selection + the PROCEED/REPLAN decision is finalized by Task 5.

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

This is the second Sprint 26 reclassification (after Day 3 Pattern C Phase B → Sprint 27 #1381) where a prep-task design assumed downstream pipeline behavior that didn't hold in practice. Both shared the same diagnostic gap:

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

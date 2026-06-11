# kand: alias-AD per-instance enumeration produces 22 phantom-offset cross-terms in stat_y (tree-predicate-aliased Sum architecture redesign)

**GitHub Issue:** [#1390](https://github.com/jeffreyhorn/nlp2mcp/issues/1390)
**Status:** DEFERRED to Sprint 28 (Sprint 27 Day 5 re-scoped Phase 0 = re-REPLAN; the documented fix premise is disproven — see "Sprint 28 carryforward" below). The linked GitHub issue remains open.
**Severity:** Medium — produces a valid MCP solve that converges to Optimal but with ~92.5% rel_diff vs the NLP optimum; not a localized AD-helper bug but an architecture-level reclassification.
**Date:** 2026-05-12
**Last Updated:** 2026-06-06
**Affected Models:** kand (target); likely affects other models with tree-predicate-aliased Sum bodies (stochastic-programming scenario-tree shapes).
**Target Sprint:** ~~Sprint 27~~ → **Sprint 28** (re-diagnose the TRUE mismatch source — it is NOT the phantom-term enumeration; see below).

## Phase 0: Acceptance Gate (Sprint 28 Prep Task 5)

**Authored:** 2026-06-11 (Sprint 28 Prep Task 5 per PR20 + PR24). **Diagnosis-heavy / REPLAN-prone track** — see the Task 6 precondition below.
**Target:** re-diagnose the TRUE 195.0-vs-2613.0 gap (kand `cost` MCP 195.0 vs NLP/LP 2613.0). **The phantom-term enumeration in `stat_y` is proven inert (Sprint 27 Day 5) and is explicitly OUT OF SCOPE.**
**Cross-links:** KNOWN_UNKNOWNS Category 5 (Unknowns 5.1, 5.2); BASELINE_METRICS §2 kand provenance row (`model_optimal`/mismatch; Match-only, 0 Solve credit); harness design `docs/planning/EPIC_4/SPRINT_28/PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md`; Sprint 27 re-REPLAN evidence `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md` §3.5.

### Hand-Derived KKT Shape

**Not yet hand-derivable** — that is the point of this gate. The Sprint 27 Day-5 prototype proved the documented shape (the `tree(nn,n)`-predicate-conditioned aliased-Sum collapse in `stat_y`) is **inert**: the collapsed emit still solves to `195.0 ≠ 2613.0`. The true defect is therefore elsewhere; the candidate stationarity targets to hand-derive at Day 0 are:

- `stat_y(j,t,n)` / `bal(j,t,n)` stationarity (the back-link `Sum(nn$tree(nn,n), y(j,t-1,nn))`);
- the `t-1` ↔ `t+1` lag duality (whether the emitted lag direction matches the NLP's);
- the LP first-stage / recourse coupling (a structural, not per-term, divergence).

### Expected Emit Pattern (hypothesis — PR24)

**No emit-pattern hypothesis is asserted** — per PR24 and the Sprint 27 re-REPLAN, the fix surface is unknown until a fresh Day-0 trace localizes the 195-vs-2613 gap. The prior `stationarity.py:3257`/`:3088` offset-re-symbolization surface is recorded as **disproven** (collapse achievable there but solution-inert), NOT as the surface.

### Verification Methodology (PR27)

```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/kand.gms --gdx kand_nlp.gdx --tol 1e-6 --json phase0_kand.json
```

The harness is the **localization instrument**. The dual-transfer consistency self-check must pass first (kand's `lam_dembalx` are `tree(nn,n)`-conditioned; Unknown 5.2). Then: **Case b** (a `stat`/`comp` row exceeds tol) ⇒ a localizable emit row → in-sprint fix; **Case c** (all residuals ≈ 0 but cold PATH lands at 195.0) ⇒ the gap is non-convexity / LP-recourse coupling, not an emit bug. Target on success: kand `cost = 2613.0` (Match).

### PROCEED/REPLAN Signal

**PROCEED to a `src/` fix** ONLY if: (a) the Task 6 hypothesis-validation (below) plus a Day-0 trace localize the gap to a concrete stationarity/complementarity `file:line` (the **Traced Fix-Surface (Day-0)**, PR24); AND (b) the harness reports **Case b** with that row as max-residual. **REPLAN to Sprint 29** (explicit exit) if the harness reports **Case c** (residuals clean, gap is LP first-stage/recourse-coupling architecture) — file a re-scoped Phase-0 successor; do NOT commit `src/` against a Case-c verdict.

**Task 6 precondition:** this track is one of the three diagnosis-heavy carryforwards (#1387/#1390/camcge). Its REPLAN risk is assessed in Task 6 (PR16 hypothesis-validation) **before** any Priority-5 `src/` budget is spent.

**Traced Fix-Surface (Day-0):** _TBD at sprint Day 0 — no prep surface is trusted (the prior one is disproven, PR24); the harness Case-(b/c) verdict + Day-0 trace establish it._

---

## Sprint 28 carryforward — Sprint 27 Day 5 re-scoped Phase 0 result (2026-06-06): re-REPLAN

Sprint 27 Day 0 disproved the originally-documented AD patch site (`constraint_jacobian.py:903/1027` — `_apply_offset_substitution` fires in `stationarity.py`, not there). The Option 1 re-plan redirected #1390 to the `stationarity.py` offset re-symbolization layer and scheduled a Day 5 re-scoped Phase 0. **That Phase 0 returned re-REPLAN** (full verdict: `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md` §3.5, Day-5 binding block):

- An env-guarded prototype on the redirected layer (post-Day-4 the functions are at `_apply_offset_substitution:3257` / `_apply_alias_offset_to_deriv:3088`) **successfully collapsed the 22 phantom `lam_dembalx(j,t+1,n±k)` terms into the hand-derived single predicate-guarded Sum** `(eps*sum(nn$(tree(n,nn)), lam_dembalx(j,t+1,nn)))$(ord(t) <= card(t)-1)` (with the diagonal `-lam_dembalx(j,t,n)` preserved), and it compiles `action=c`-clean. So the collapse **is achievable** at this layer.
- **BUT the collapsed emit is solution-equivalent to the verbose 22-term enumeration: both solve to MCP `cost = 195.0`, unchanged, vs NLP/LP optimum `2613.0` (the ~92.5% rel_diff persists).** kand stays `compare_objective_mismatch` *with the collapse applied*.
- **Conclusion: the phantom-term enumeration is NOT the root cause of the kand mismatch.** The back-link contribution is reproduced faithfully by the collapse (just verbosely), so collapsing it is a cosmetic/structural cleanup, not a correctness fix. The real defect lies elsewhere.
- **Mechanism note for the re-diagnosis:** kand's back-link is `Sum(index_sets=('nn',), condition=SetMembershipTest(tree,(nn,n)), body=y(j,t-1,nn))` — a `tree(nn,n)`-conditioned alias-Sum on the `n`-axis COMBINED with a genuine `t-1` lag on a different axis. The Pattern-C gate bails because `_body_has_index_offset_on_sets` sees the `t` lag (the guard that protects real lead/lag canaries), so the `n`-axis predicate falls to offset-enumeration. That is why 22 terms appear — but it is not why the objective is wrong.

**Sprint 28 re-diagnosis direction:** find the TRUE source of the 195.0 vs 2613.0 gap — candidate surfaces are the `bal(j,t,n)`/`x` stationarity, the `t-1`↔`t+1` lag duality, or the LP first-stage/recourse coupling — NOT the `tree`-predicate re-symbolization (now proven inert to the objective). The phantom-term collapse may still be done as a separate readability cleanup, but it does not deliver the +1 Match. **Sprint 27 Match target lowered 66 → 65** to reflect the lost #1390 Match gain (recorded in PLAN §17 / SPRINT_LOG Day 5).
**Cross-references:**
- Predecessor: #1141 (now CLOSED 2026-05-12 via Sprint 26 Day 7 — see [docs/issues/completed/ISSUE_1141_kand-alias-tree-mismatch.md](completed/ISSUE_1141_kand-alias-tree-mismatch.md)).
- Sister Sprint 27 carryforwards (similar AD-architecture-level reclassifications):
  - #1381 (Pattern C Phase B redesign — Sprint 26 Day 3 reclassification).
  - #1385 (Option 1 short-circuit redesign — Sprint 26 Day 4 reclassification).
- Reclassification source: [docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md](../planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md) §"Issue #1141" (original keep-open rationale; superseded by Day 7 intractability discovery).

> ⚠️ **HISTORICAL (superseded by the Day-5 re-REPLAN above).** Everything from here down is the original Sprint-26 framing, which assumed the 22 phantom-offset terms are the *root cause* of the kand mismatch. The Sprint 27 Day 5 re-scoped Phase 0 **disproved that premise** (collapsing the terms is solution-equivalent; MCP stays 195.0 ≠ NLP 2613.0). The Sprint 28 re-diagnosis must look elsewhere (see the carryforward above). Read the sections below as background on the phantom-term *symptom* only — NOT as the fix direction.

## Problem Summary

kand produces `solution_comparison.comparison_status = mismatch` with NLP-MCP rel_diff ~92.5% on the obj. The bug is rooted in how the AD / stationarity pipeline handles a tree-predicate-aliased Sum body: instead of emitting a single guarded cross-term, it enumerates over each static element of the `n` set and produces 22 phantom-offset terms.

Sprint 26 Day 6 scoping (`docs/planning/EPIC_4/SPRINT_26/SPRINT_LOG.md` Day 6 §"kand alias-AD scoping") established the bug shape. Day 7 `SPRINT25_DAY2_DEBUG=1` trace analysis confirmed the root cause is AD-architecture-level — not a localized helper bug that fits inside Day 7's 4–6h budget. Reclassified to Sprint 27 per the Day 7 Task 5 contingency in `docs/planning/EPIC_4/SPRINT_26/prompts/PLAN_PROMPTS.md`.

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/kand.gms \
  -o /tmp/kand_mcp.gms --skip-convexity-check --quiet

# Inspect the broken stat_y emit (22 phantom-offset terms):
grep -E "^stat_y\(j,t,n\)" /tmp/kand_mcp.gms
# Expected: 1 cross-term: sum(n_inner$tree(n,n_inner), eps * lam_dembalx(j,t+1,n_inner))$(tn(t+1,n_inner))
# Observed (the bug): 22 sum(nn, eps * 1$(tree(nn,n)) * lam_dembalx(j,t+1,n+k))$(...) terms for k=-8..+11

gams /tmp/kand_mcp.gms lo=2
# Solves Optimal but rel_diff ~92.5% vs NLP
```

## Bug shape (from Day 6 scoping)

**Source body** (`data/gamslib/raw/kand.gms:99–100`):

```gams
dembalx(j,tn(t,n))..
   sum(i, a(j,i)*x(i,t)) + y(j,tn) =g= dem(n,j) + eps*sum(tree(nn,n), y(j,t-1,nn));
```

**Set declarations** (`data/gamslib/raw/kand.gms:17–56`):
- `Alias (n,nn);` — `nn` is the alias of `n`.
- `tree(n,n)` is a static 9-element predicate over `(parent, child)` pairs:
  - `(n-1, n-4), (n-1, n-5), (n-1, n-6)`
  - `(n-2, n-7), (n-2, n-8), (n-2, n-9)`
  - `(n-3, n-10), (n-3, n-11), (n-3, n-12)`

**Expected `stat_y(j,t,n)` cross-term** (hand-derived from KKT):

```gams
... + sum(n_inner$tree(n,n_inner), eps * lam_dembalx(j,t+1,n_inner))$(tn(t+1,n_inner)) + ...
```

(For specific `n` values: `n=n-1` produces a cross-term over `n_inner ∈ {n-4, n-5, n-6}`; `n=n-2` produces one over `{n-7, n-8, n-9}`; `n=n-3` produces one over `{n-10, n-11, n-12}`; all other `n` values produce no cross-term from this Sum.)

**Current emit (broken)** — 22 phantom-offset terms:

```gams
stat_y(j,t,n).. (prob(n) * f(j,t) * 1$(tn(t,n)) + ((-1) * lam_dembalx(j,t,n))$(tn(t,n))
  + sum(nn, ((eps * 1$(tree(nn,n)) * lam_dembalx(j,t+1,n+9))$(...))$(tn(t,n)))
  + sum(nn, ((eps * 1$(tree(nn,n)) * lam_dembalx(j,t+1,n+10))$(...))$(tn(t,n)))
  + ... [20 more terms with offsets k = -8..+11] ...
  + sum(nn, ((eps * 1$(tree(nn,n)) * lam_dembalx(j,t+1,n-8))$(...))$(tn(t,n)))
  - piL_y(j,t,n))$(tn(t,n)) =E= 0;
```

## Root cause (from Day 7 SPRINT25_DAY2_DEBUG=1 trace analysis)

The AD pipeline's cross-term enumeration step iterates over each static element of the `n` set (n-1, n-2, ..., n-9) as a candidate wrt_indices, producing one cross-term per element-substitution. Trace excerpt (Day 7, captured against current main):

```
[diff_varref] enter name='y' expr.indices=('p-2', 'time-1', 'nn') wrt_indices=('p-2', 'time-2', 'n-5') bound_indices=['nn']
[diff_varref] -> Const(0.0) [no match]
[diff_varref] enter name='y' expr.indices=('p-2', 'time-2', 'n-9') wrt_indices=('p-2', 'time-2', 'n-5') bound_indices=[]
[diff_varref] -> Const(0.0) [no match]
[diff_varref] enter name='y' expr.indices=('p-2', 'time-2', 'n-9') wrt_indices=('p-2', 'time-2', 'n-9') bound_indices=[]
[diff_varref] -> Const(1.0) [exact index match]
```

After enumeration, each match-positive concrete-element pair is converted back to symbolic + offset form for emit. This produces one phantom-offset term per static element relationship, NOT a single predicate-guarded Sum.

## Investigation pointers (Phase 0 / Sprint 27 prep work)

1. The fix surface is the AD-architecture choice: per-instance enumeration vs predicate-constrained-sum. Single-helper fixes won't suffice — the enumeration happens in `_compute_inequality_jacobian` / `_compute_equality_jacobian` (`src/ad/constraint_jacobian.py:903`, `:1027`) which iterates over each equation instance.

2. The correct architecture (hypothesized): when a constraint body has a Sum with a static-set predicate (`sum(tree(nn,n), ...)`), the stationarity cross-term should preserve the predicate structure rather than enumerate. This is analogous to Issue #666's `_preserve_subset_var_indices` (preserves subset VarRef indices) and Issue #1164/#1175's `KKTSystem.param_domain_widenings` (preserves widened parameter domains) — both Sprint 23+24 architectural changes.

3. **Phase 0 acceptance gate** (per Sprint 27 prep methodology established Sprint 26 Days 3 + 4): translate kand with a prototype patch + verify GAMS compile-clean + hand-derive `stat_y('p-1', 'time-2', 'n-4')` KKT instance vs the emit BEFORE committing the full implementation budget. The Sprint 26 Day 3 + Day 4 reclassifications established that prep-task design validation at the patch-site level is insufficient; empirical end-to-end correctness verification is required.

## Proposed Fix Approach — Three Sub-Phases

(Phase decomposition added Sprint 26 Day 8 per buffer use 4 — Sprint 27 design notes only. No `src/` implementation at this point. Mirrors the Phase 1/2/3 structure used in #1381 and #1385 Sprint 27 carryforwards.)

### Phase 1 (~3–4h): Inventory + design choice

**Deliverable:** decision between two competing architecture options.

- **Option A — Predicate-preserving cross-term:** detect when a Sum body has a static-set predicate over the equation domain (`sum(tree(nn, eq_domain_index), body)`) and preserve the predicate as a guard rather than enumerating. Touch sites: `src/ad/constraint_jacobian.py:903` / `:1027` per-equation iteration; introduce a `_preserve_predicate_constrained_sum` helper analogous to Issue #666's `_preserve_subset_var_indices` at `src/kkt/stationarity.py:2943+`.
- **Option B — Emit-time guard reconstruction:** let the per-instance enumeration run as today, but post-process the AD output to detect when the cross-terms differ only by a `lam_<eq>` index that follows a predicate, and collapse them back into a single guarded Sum at the stationarity-assembly step. Touch sites: `src/kkt/stationarity.py` cross-term accumulation; new post-processing pass.

Phase 1 must include the **Phase 0 acceptance gate** (per Sprint 26 Days 3 + 4 reclassification methodology): translate kand with a Phase-1 prototype + verify GAMS compile-clean + hand-derive `stat_y('p-1', 'time-2', 'n-4')` KKT instance against the emit. BEFORE committing the Phase 2 implementation budget.

### Phase 2 (~4–6h): Implementation

Implement the chosen option from Phase 1. Reuse existing infrastructure:
- `_partial_collapse_sum` + `_partial_index_match` (`src/ad/derivative_rules.py`) — these are the alias-AD matching helpers; should NOT need modification if Option A is chosen (the architecture change is at the per-equation iteration level, not the per-term differentiation level).
- `_expand_sum_body` / `_expand_sums_with_unresolved_offsets` (`src/ad/constraint_jacobian.py:484`, `:327`) — these handle static-set element substitution; Option A would add a fast-path that skips expansion when the Sum has a predicate constraining iteration to a small predicate-satisfying set.
- `KKTSystem.param_domain_widenings` precedent (Issue #1164/#1175, `src/kkt/kkt_system.py:201`) — model for how to communicate the predicate structure from the IR to the emit-time stationarity assembly.

### Phase 3 (~3–6h): Integration test coverage + Tier 0/1/2 byte-stable regression

Integration tests verifying EMIT CORRECTNESS (hand-derived KKT shape + GAMS compile-clean), not just "translation completes". This is the Sprint 26 Days 3 + 4 lesson — narrow unit tests that only verify "the patch fires" pass even when the downstream emit is structurally wrong.

## Tests to Add (Sprint 27)

### Phase 1 deliverable

- 1 hand-derived KKT shape verification document at `docs/issues/ISSUE_1390_kand_phase_0_handderived_kkt.md` (or inline in this issue body) — pins the expected `stat_y('p-1', 'time-2', 'n-4')` and `stat_y('p-2', 'time-2', 'n-9')` cross-term shapes.

### Phase 2

- 1 unit test in `tests/unit/ad/test_predicate_constrained_sum.py` (synthetic 3-element tree predicate + Sum body) asserting the chosen architecture produces a single guarded Sum cross-term, not per-element enumeration.
- 1 unit test asserting the predicate is preserved through `differentiate_expr` for both equality-jacobian and inequality-jacobian paths.

### Phase 3 (integration)

- 1 integration test in `tests/integration/ad/test_kand_tree_predicate.py`:
  - Translate kand from `data/gamslib/raw/kand.gms`.
  - Assert `grep -cE "lam_dembalx\(j,t\+1,n[\+\-][0-9]+\)" data/gamslib/mcp/kand_mcp.gms` returns 0 (no phantom-offset cross-terms).
  - Assert `grep -cE "sum\([a-z_]+\\\$tree\(n," data/gamslib/mcp/kand_mcp.gms` returns ≥ 1 (single predicate-guarded Sum).
  - Run `gams data/gamslib/mcp/kand_mcp.gms lo=2` and assert MODEL STATUS 1 Optimal.
  - Assert NLP-MCP rel_diff < 1% (vs current 92.5%).
- Tier 0/1 byte-stable canary check (11 models, mirror Sprint 26 Day 5 retest list).

## Files Involved

- `src/ad/constraint_jacobian.py` (`_compute_inequality_jacobian` + `_compute_equality_jacobian` per-equation enumeration at `:903` / `:1027`; `_expand_sum_body` / `_expand_sums_with_unresolved_offsets` static-set substitution at `:484` / `:327`).
- `src/ad/derivative_rules.py` (`_partial_collapse_sum` + `_partial_index_match`; `_diff_varref` with `bound_indices`).
- `src/kkt/stationarity.py` (cross-term accumulation site; Option B post-processing would land here).
- `src/kkt/kkt_system.py` (`param_domain_widenings` precedent at `:201` — pattern for communicating predicate structure to emit time).
- `data/gamslib/raw/kand.gms` (source — kept as the target reproducer; do NOT use any other model for Phase 0 acceptance gate).
- `data/gamslib/mcp/kand_mcp.gms` (current emit with 22 phantom terms; will regenerate post-fix).

## Effort estimate

10–16h across three sub-phases (Phase 1: 3–4h architecture choice + Phase 0 acceptance gate; Phase 2: 4–6h implementation; Phase 3: 3–6h integration test coverage + Tier 0/1 byte-stable regression). Mirrors the Sprint 27 #1381 (Pattern C Phase B redesign) + #1385 (Option 1 short-circuit redesign) effort profiles for similar AD-architecture-level reclassifications.

## Related

- **#1141** — closed 2026-05-12 via Sprint 26 Day 7; the original alias-AD framing remains accurate; the close-and-refile follows the Day 7 §"intractable in budget" contingency per `docs/planning/EPIC_4/SPRINT_26/prompts/PLAN_PROMPTS.md` Day 7 Task 5 contingency.
- **#1381** (Sprint 27): Pattern C Phase B redesign — similar AD-architecture-level reclassification from Sprint 26 Day 3.
- **#1385** (Sprint 27): Option 1 short-circuit redesign — similar reclassification from Sprint 26 Day 4.
- **Sprint 26 Prep Task 5**: `docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md` §"Issue #1141" — original keep-open rationale; superseded by Day 7 intractability discovery.

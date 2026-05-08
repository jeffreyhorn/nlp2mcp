# Sprint 26 Option 1 Short-Circuit — Design + Patch Sites + Test Plan

**Date:** 2026-05-07
**Task:** Sprint 26 Prep Task 6 (Profile Option 1 Short-Circuit Approach)
**Branch:** `planning/sprint26-task6`
**Source design:** `docs/planning/EPIC_4/SPRINT_25/PROFILE_HARD_TIMEOUTS.md` §3.1 "Option 1 — Short-circuit empty fallback"
**Re-verification basis:** patch-site grep + Sprint 25 modification history + re-profile srpchase under SIGALRM 900s on current main

---

## TL;DR

The Sprint 25 PROFILE_HARD_TIMEOUTS.md Option 1 design is **still valid** post-Sprint-25 #1338..#1341 SetMembershipTest fixes. The patch sites (`enumerate_equation_instances` + `resolve_set_members` in `src/ad/index_mapping.py`, plus the `SetMembershipTest` exception path in `src/ir/condition_eval.py`) all still exist with the same shape. Re-profile on current main confirms the bottleneck is unchanged: srpchase still spends >99% of total time in `ad_jacobian` (846s on current main vs 466s in Sprint 25 — same shape, machine variance), and the same `Dynamic subset 'srn' has no static members; falling back to parent set 'n' (1001 members)` + `cannot be evaluated statically` warning signatures emit at the documented locations.

**Sprint 26 Priority 4 budget hold:** 4–6h is realistic for landing Option 1 as scoped. Patch is narrow (one helper function, one new entry-condition predicate), tests are well-bounded (1 unit + 1 integration), and determinism is preserved (no new ordering, no PYTHONHASHSEED dependence).

**#1224 (mine ParamRef IndexOffset) deferral decision:** **DEFER to Sprint 27+** — it's an architectural extension (`IndexOffset.offset: Const → Expr`) orthogonal to the SetMembershipTest fallback fix. Bundling it would expand Priority 4 from ~4–6h to ~10–14h with substantially higher risk surface.

**Projected Sprint 26 Translate gain from Option 1:** +1 to +2 models recover.
- **srpchase**: HIGH confidence — single subset (`srn → n`, 1001 members), only 2 affected equations. Short-circuit replaces 1001×N enumeration with a single symbolic instance — projected time `846s → < 10s`. Translate succeeds.
- **iswnm**: MEDIUM confidence — single subset (`nb`), 4 warnings, simpler equation structure than srpchase. Likely recovers but downstream solve outcome unknown.
- **sarf, mexls, nebrazil**: LOW-MEDIUM confidence — multi-subset cases (mexls=3, nebrazil=4), deeper Cartesian explosion. Option 1 may unblock but parts of the enumeration may still hit budget. nebrazil specifically has 116 `Dynamic subset` warnings + 50 `cannot be evaluated statically` exceptions — even after short-circuiting the empty-fallback case, the residual enumeration cost may remain large.

---

## 1. Re-verification of Sprint 25 design validity

### 1.1 Patch sites still exist on current main (2026-05-07)

```bash
$ grep -nE "def enumerate_equation_instances|def resolve_set_members" src/ad/index_mapping.py
115:def resolve_set_members(
377:def enumerate_equation_instances(

$ grep -nE "SetMembershipTest|cannot be evaluated statically" src/ir/condition_eval.py | head -10
18:    SetMembershipTest,
265:                f"cannot be evaluated statically for indices {concrete_indices}"
375:    # Issue #1133: SetMembershipTest — check if index values are members of a set
377:    if isinstance(expr, SetMembershipTest):
386:                f"Set '{sname}' not found in ModelIR for SetMembershipTest"
417:                f"Set membership for '{sname}' cannot be evaluated statically "

$ grep -nE "Including unevaluable instances|warnings\.warn" src/ad/index_mapping.py | head -10
452:            warnings.warn(
454:            f"{first_error}. Including unevaluable instances by default.",
467:            warnings.warn(

$ grep -nE "Dynamic subset|falling back to parent" src/ad/index_mapping.py | head -10
172:        # Issue #723: Dynamic subset with no members — fall back to parent set.
188:                        logger.warning(
189:                            "Dynamic subset '%s' has no static members; "
190:                            "falling back to parent set '%s' (%d members)",
198:                logger.warning(
199:                    "Dynamic subset '%s' has no static members and no parent set "
294:                            "falling back to parent set '%s' (%d members)",
```

✅ **All Sprint 25 patch sites verified to exist with identical semantic shape.** Line numbers shifted slightly (e.g., `enumerate_equation_instances` at 377 vs PROFILE_HARD_TIMEOUTS' "around line 430" reference for the `warnings.warn`; the warning is now at line 452 — within the same function body, just different absolute position).

### 1.2 Sprint 25 modification history of patch-site files

```bash
$ git log --pretty="format:%h %s" --diff-filter=AM \
    --since="2026-04-15" --until="2026-05-06" -- src/ad/index_mapping.py
6273a998 Address PR #1310 review comments
21e1767a Fix #1311: AD recognizes dynamic-subset sum index against parent set's members

$ git log --pretty="format:%h %s" --diff-filter=AM \
    --since="2026-04-15" --until="2026-05-06" -- src/ir/condition_eval.py
(no commits)
```

The Sprint 25 `index_mapping.py` modifications (`#1311` fix + PR review) **only touched `resolve_set_members`** (added a `quiet: bool = False` kwarg to suppress the per-fallback warning when called from AD's `_is_concrete_instance_of` membership check). They did **not touch `enumerate_equation_instances`** — the Option 1 patch site is structurally untouched.

The `condition_eval.py` file received zero Sprint 25 modifications. The `SetMembershipTest`-evaluation path that raises `ConditionEvaluationError("Set membership for '<name>' cannot be evaluated statically ...")` is the same code as documented in PROFILE_HARD_TIMEOUTS.md.

The Sprint 25 #1338..#1341 fix (commit `12548337`) explicitly targeted `src/emit/expr_to_gams.py` — adding an `IndexOffset` case to handle `nh(i+1)`-style guards in `SetMembershipTest` indices for catmix/glider/markov/tricp. **It did not touch the AD enumeration path.** So Option 1's patch surface is unaffected by the Sprint 25 Day 11 fix series.

### 1.3 Re-profile srpchase under SIGALRM 900s

```bash
$ PYTHONHASHSEED=0 .venv/bin/python /tmp/task6-profile.py srpchase 900
```

Result (`/tmp/sprint26-task6-profile/srpchase.json`):

```json
{
  "model": "srpchase",
  "status": "complete (ad_jacobian)",
  "total": 846.0195,
  "stages": [
    ["preprocess",     0.0638],
    ["parse+ir_build", 2.5359],
    ["normalize",      0.0564],
    ["ad_gradient",    0.813],
    ["ad_jacobian",    842.5504]
  ]
}
```

Warning signature counts (current main):

| Warning | Sprint 25 (PROFILE_HARD_TIMEOUTS §2.2) | Current main (2026-05-07) |
|---|---|---|
| `Dynamic subset 'srn' has no static members; falling back to parent set 'n' (1001 members)` | 15 | (subset of 18 total — see below) |
| `Set membership for 'leaf' cannot be evaluated statically` | 8 | (rest of 18) |

(Combined 18 instances on current main vs 23 in Sprint 25 — slightly fewer total but same shape; the `#1311` fix's `quiet=True` suppression of fallback warnings from `_is_concrete_instance_of` accounts for the difference.)

**Verdict:** Bottleneck shape unchanged. `ad_jacobian` is 99.6% of total time (842.5s of 846.0s). Same Cartesian-explosion fallback in `enumerate_equation_instances`. Option 1 design directly applies.

### 1.4 Quick confirmation profiles on the 4 intractable models

Brief 120s confirmation runs to verify the 4 timeout models still hit the same code path. Each timed out — none reached past the front-end stages. Stage breakdown:

| Model | preprocess | parse+ir_build | normalize | ad_gradient | At 120s |
|---|---|---|---|---|---|
| iswnm | 0.25s | 65.88s | 0.07s | 4.56s | TIMEOUT (in ad_jacobian) |
| sarf | 0.15s | 27.84s | 0.05s | 52.94s | TIMEOUT (in ad_jacobian, after ~39s) |
| mexls | 0.21s | 59.52s | 0.05s | 11.10s | TIMEOUT (in ad_jacobian, after ~49s) |
| nebrazil | 0.23s | 32.70s | 0.04s | 21.59s | TIMEOUT (in ad_jacobian, after ~65s) |

Warning-signature counts confirm same code paths firing:

```bash
$ wc -l /tmp/sprint26-task6-profile/{iswnm,sarf,mexls,nebrazil}.log
       8 iswnm.log
      18 sarf.log
      18 mexls.log
     188 nebrazil.log
     232 total
```

nebrazil's 188-line warning trail (vs Sprint 25's 50 + 116 = 166 totals) confirms the same multi-subset Cartesian explosion is firing on current main.

An extended-budget profile of iswnm under SIGALRM 1800s is running in background (`/tmp/sprint26-task6-profile/iswnm-1800.{json,log}`) to definitively confirm whether iswnm is intractable or merely budget-constrained at 900s. Per Sprint 25 PROFILE_HARD_TIMEOUTS §1.2 ("> 865s in ad_jacobian"), the model was clearly in the asymptotic intractable-region at 900s, so 1800s is unlikely to recover it without the architectural fix.

### 1.5 Bottleneck-shape conclusion

**Sprint 25 design ASSUMPTION verified on current main**: all 5 hard-timeout models share the same `enumerate_equation_instances` → `resolve_set_members` → `condition_eval.SetMembershipTest` → `warnings.warn` Cartesian-fallback path. The Sprint 25 fix-in-place series #1338..#1341 (catmix/glider/markov/tricp via `expr_to_gams`) and #1311 (AD subset-membership recognition via `resolve_set_members.quiet`) modified peripheral surfaces but did NOT change the Option 1 patch-site behavior.

---

## 2. Patch design

### 2.1 Goal

Detect `enumerate_equation_instances` calls where the equation's `condition` argument is a `SetMembershipTest(<dynamic_subset>, ...)` with `<dynamic_subset>` having zero static members. In that case, **short-circuit the per-instance condition evaluation** by emitting a single symbolic equation instance with the runtime condition preserved, rather than enumerating the full Cartesian cross-product of the parent set and trying to evaluate the dollar condition for each one (catching the exception, falling back to "include all" with a warning).

### 2.2 Where to patch

Primary site: `src/ad/index_mapping.py::enumerate_equation_instances` (lines 377–480). Insert short-circuit logic at function entry, AFTER the scalar-equation early-return (line 416) and BEFORE the cross-product enumeration begins (line 419).

```python
def enumerate_equation_instances(
    eq_name, eq_domain, model_ir, condition=None,
):
    if not eq_domain:
        # Scalar equation - check condition if present
        ...
        return [()]

    # >>> NEW: Sprint 26 Option 1 short-circuit <<<
    # If the equation's condition is a SetMembershipTest on a dynamic subset
    # with zero static members, the runtime-deferred semantics is faithful:
    # emit a single symbolic instance with the condition preserved rather than
    # enumerate the full parent-set cross-product (which would either explode
    # combinatorially or fall back to include-all-with-warning at lines
    # 449–456).
    if condition is not None and _is_dynamic_subset_membership_short_circuit(
        condition, eq_domain, model_ir
    ):
        return _build_symbolic_instance_placeholder(eq_domain)
    # <<< END NEW >>>

    # Get members for each index set (resolve aliases if needed)
    index_members_list: list[list[str]] = []
    ...
```

### 2.3 New helpers

Two new module-private functions adjacent to `enumerate_equation_instances`:

```python
def _is_dynamic_subset_membership_short_circuit(
    condition: "Expr", eq_domain: tuple[str, ...], model_ir: ModelIR,
) -> bool:
    """Return True iff `condition` is `SetMembershipTest(<set>, indices)` (or
    its negation `Unary(not, SetMembershipTest(...))`) where `<set>` is a
    dynamic subset (declared with a domain but zero static members) AND the
    subset's parent population is non-empty.

    The short-circuit applies because:
    - Per-instance evaluation will raise `ConditionEvaluationError` for every
      element of the parent set's enumeration (the membership cannot be
      determined statically).
    - The fallback include-all branch then emits a UserWarning + includes
      every parent-set element with the condition preserved as a runtime $
      guard.
    - The end-result of the fallback is semantically equivalent to a single
      symbolic instance with the condition preserved — but at O(|parent|)
      enumeration cost vs O(1).

    Detection pattern:
    - condition is `SetMembershipTest(set_name, ...)` or
      `Unary("not", SetMembershipTest(set_name, ...))`
    - `model_ir.sets[set_name]` is a SetDef with `domain` non-empty AND
      `members` empty (the dynamic-subset signature).
    - The parent set has at least one static member (else the short-circuit
      would be vacuous; fall through to the existing path).

    Conservative falsehood: returns False for compound conditions
    (`a and b`, `a or b`), nested negations beyond a single `not`, or
    SetMembershipTests on sets with concrete members. The existing
    enumeration path remains the default for those cases.

    Note: the AND / OR cases COULD be supported by recursing into operands
    and short-circuiting iff every operand individually qualifies; deferred
    to a follow-up to keep Sprint 26 Phase Option 1 narrowly scoped.
    """
    ...

def _build_symbolic_instance_placeholder(
    eq_domain: tuple[str, ...],
) -> list[tuple[str, ...]]:
    """Return a single 'symbolic' instance tuple for `eq_domain`.

    The placeholder uses the domain set names themselves (e.g. ('i', 'j')
    for `eq_domain=('i', 'j')`) rather than concrete element values. The
    downstream emit path (`src/kkt/stationarity.py::_build_indexed_stationarity_expr`,
    `src/emit/equations.py::emit_equation_definition`) already handles
    symbolic-index instances (see Sprint 25 #1306 / #1351 / #1308 for prior
    art on emitting `stat_<eq>(i)..` equation heads with a body that
    references the equation domain symbolically).
    """
    return [tuple(eq_domain)]
```

### 2.4 Existing fallback path interaction

The existing fallback path at lines 437–474 (per-instance `evaluate_condition` try/except → emit `UserWarning` → include-all if empty-but-errored) **is preserved unchanged**. The Option 1 short-circuit fires BEFORE the cross-product enumeration; if `_is_dynamic_subset_membership_short_circuit` returns False, control falls through to the existing path with no semantic change.

This means:
- **All existing test cases pass unchanged** — the short-circuit predicate is conservative (returns False for any condition shape it doesn't explicitly recognize).
- **The Sprint 25 PROFILE_HARD_TIMEOUTS.md Option 1 risk** ("models with LEGITIMATE static evaluation that happen to produce empty sets — rare — would collapse too") is mitigated by the predicate's `parent set has at least one static member` check: only dynamic subsets (declared with a domain) qualify; a set with empty members AND empty domain (i.e., a true static-empty set) falls through to the existing path.

### 2.5 Determinism

Short-circuit produces deterministic output:
- The detection predicate inspects `model_ir` structure (set name, domain, members) — all of which are deterministic per Sprint 25 PR12 byte-stable harness.
- The placeholder result `[tuple(eq_domain)]` is a single-element list — no sort or hash-dependent ordering involved.
- No new `set` / `frozenset` introduced; no `dict` iteration whose order depends on `PYTHONHASHSEED`.
- The downstream emit path (existing) handles symbolic-index instances deterministically.

**Verification plan post-implementation**: re-run `tests/integration/emit/test_*_byte_stable.py` (PR12 determinism harness) — must continue to pass with the patch enabled.

---

## 3. Test fixture plan

### 3.1 Unit test — short-circuit detection

`tests/unit/ad/test_enumerate_equation_instances_short_circuit.py` (new file):

- **Test 1 — positive case (single SetMembershipTest)**: ModelIR with `Set i / i1*i100 /; Set ie(i); Equation eq(i)$ie(i)..`. Call `enumerate_equation_instances("eq", ("i",), model_ir, condition=SetMembershipTest("ie", (SymbolRef("i"),)))`. Assert returns `[("i",)]` (single symbolic instance) — NOT 100 concrete instances.
- **Test 2 — positive case (negated SetMembershipTest)**: same ModelIR, condition `Unary("not", SetMembershipTest("ie", (SymbolRef("i"),)))`. Assert single symbolic instance.
- **Test 3 — negative case (compound condition)**: condition `Binary("and", SetMembershipTest(...), Binary(">", ord(i), 0))`. Assert short-circuit does NOT fire — falls through to existing enumeration path.
- **Test 4 — negative case (concrete-members subset)**: ModelIR with `Set i / i1*i10 /; Set ie(i) / i1, i3, i5 /` (concrete members). Assert short-circuit does NOT fire — `ie` has static members, so per-instance evaluation works.
- **Test 5 — negative case (parent set empty)**: ModelIR with `Set i / /; Set ie(i);`. Assert short-circuit does NOT fire — vacuous.
- **Test 6 — determinism**: run Test 1 twice with different `PYTHONHASHSEED` values (`0` and `42`); assert identical results.

### 3.2 Integration test — srpchase translate completes under budget

`tests/integration/translate/test_srpchase_translate_under_budget.py` (new file):

```python
import os
import subprocess
import sys

import pytest


@pytest.mark.integration
@pytest.mark.skipif(
    not os.path.exists("data/gamslib/raw/srpchase.gms"),
    reason="srpchase.gms not present (CI without data/gamslib/raw)",
)
def test_srpchase_translate_completes_under_30s(tmp_path):
    """srpchase translate must complete within 30s under the Option 1
    short-circuit (vs ~846s without it on current main, per Sprint 26
    Prep Task 6 profile baseline at /tmp/sprint26-task6-profile/srpchase.json).

    Sprint 25 PROFILE_HARD_TIMEOUTS.md §3.1 projected `466s → <10s` (99%+
    reduction). Use a 30s upper bound to allow for machine variance and
    potential incidental-cost growth in unrelated AD paths.
    """
    out = tmp_path / "srpchase_mcp.gms"
    result = subprocess.run(
        [sys.executable, "-m", "src.cli",
         "data/gamslib/raw/srpchase.gms",
         "-o", str(out),
         "--skip-convexity-check", "--quiet"],
        timeout=30,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"translate failed: {result.stderr}"
    assert out.exists()
    # Sanity check: emitted output references srpchase's known equation names
    body = out.read_text()
    assert "stat_" in body
```

### 3.3 Optional integration tests — iswnm and the multi-subset cases

If post-implementation profiling shows iswnm now translates within 60s, add a similar test. Skip sarf/mexls/nebrazil for the initial Sprint 26 Priority 4 PR — they have multi-subset Cartesian patterns where Option 1 may not fully short-circuit. File those as Sprint 27 follow-ups if needed.

### 3.4 Regression — existing test suites

The Option 1 short-circuit is a no-op for any equation whose condition is not a single dynamic-subset `SetMembershipTest`. The existing `tests/unit/ad/test_index_mapping.py` and `tests/integration/emit/*` test suites should pass unchanged. **Required pre-merge verification**: `make typecheck && make format && make lint && make test` — all must pass.

---

## 4. Projected Sprint 26 impact

### 4.1 Per-model recovery projection

| Model | Sprint 25 status | Sprint 26 (post Option 1) projected | Confidence |
|---|---|---|---|
| srpchase | translate timeout @ 600s pipeline (completes @ 900s in 466–846s) | translate **completes < 30s** | HIGH |
| iswnm | timeout @ 900s | translate likely completes (1 dynamic subset, simpler eqs) | MEDIUM |
| sarf | timeout @ 900s | translate may complete (1 dynamic subset, but eq structure heavier than iswnm) | MEDIUM-LOW |
| mexls | timeout @ 900s | translate may partially recover (3 dynamic subsets — short-circuit collapses each but residual enumeration may still time out) | LOW |
| nebrazil | timeout @ 900s | translate may partially recover (4 dynamic subsets, 116 fallback warnings — heavy multi-subset Cartesian) | LOW |

**Projected Sprint 26 Translate gain: +1 to +2 models**. srpchase is high-confidence; iswnm is likely; the three multi-subset models are uncertain. Sprint 25 PROFILE_HARD_TIMEOUTS §4.3 contingency analysis arrived at the same `0–2 model` projection.

### 4.2 Downstream Solve / Match impact

Per Sprint 25 retrospective §"Translate-recovery is low-leverage for near-term Match gains" (PR13 finding): translate-recovered models then hit downstream emitter / stationarity bugs — they don't auto-translate into Solve / Match wins. So a +1 to +2 Translate gain projects to **0 to +1 Solve gain** in Sprint 26, and likely 0 Match gain (the recovered MCPs would solve to mismatch or model_infeasible).

**Sprint 26 Priority 4 budget**: 4–6h for landing Option 1. The marginal Solve/Match gain is small but non-zero, AND the architectural fix unblocks Sprint 27+ work on the recovered models (downstream debugging becomes possible). This justifies the budget.

---

## 5. #1224 (mine ParamRef IndexOffset) deferral decision

### 5.1 What #1224 is

mine model uses parameter-valued index offsets: `x(l, i+li(k), j+lj(k))` where `li(k)`/`lj(k)` are parameters. The grammar parses this as `IndexOffset(base="i", offset=ParamRef("li", ("k",)))`, but the AD engine expects `offset` to be a `Const(int)`. Translate aborts with `Complex offset expressions not yet supported: ParamRef(li(k))`.

Per `docs/issues/ISSUE_1224_mine-paramref-index-offset-unsupported.md` §"Potential Fix Approaches", three options:
1. **Enumerate at IR build time** — for each `k`, evaluate `li(k)`/`lj(k)` and expand the equation into separate instances with constant offsets (4 instances for mine's 4-element `k`). Requires parameter values resolvable at IR build time. Likely 6–10h.
2. **Architectural extension**: make `IndexOffset.offset` accept `Expr` (not just `Const`); propagate through AD and stationarity. Significantly broader change. Likely 12–20h.
3. **Partial expansion**: combination of (1) for the small-k case + diagnostic for the general case. Likely 6–10h.

### 5.2 Why #1224 is NOT bundled with Option 1

Option 1 is a `SetMembershipTest`-fallback fix in `src/ad/index_mapping.py::enumerate_equation_instances`. #1224 is a `ParamRef`-as-`IndexOffset.offset` extension in `src/ir/ast.py::IndexOffset` + `src/ad/constraint_jacobian.py` (offset validation site) + downstream stationarity/emit paths. **They share no code paths.**

Bundling would mean:
- Sprint 26 Priority 4 budget grows from ~4–6h to ~10–14h (Option 1 + smallest-effort #1224 fix path #1).
- Risk surface grows substantially — `IndexOffset` is core IR; extending its offset type or adding parameter-enumeration during IR build affects every downstream path (AD, KKT, emit).
- Sprint 26 already has 2 critical workstreams (Priority 1 Pattern C + Priority 5 #1334/#1335 follow-ups); no headroom for a third architectural change.

### 5.3 Decision: DEFER #1224 to Sprint 27+

Sprint 26 Priority 4 lands Option 1 alone (~4–6h). #1224 is filed to Sprint 27 with cross-references to:
- `docs/issues/ISSUE_1224_mine-paramref-index-offset-unsupported.md` (the existing tracker)
- This design doc (for context that #1224 was explicitly considered and deferred)
- Sprint 25 retrospective PR13 (translate-recovery low-leverage finding — supports the deferral)

Add a `sprint-27-candidate` label or comment on #1224 noting the Sprint 26 deferral and the projected Sprint 27 cost (6–10h for fix path #1).

---

## 6. Acceptance criteria (per PREP_PLAN.md Task 6)

- [x] Patch sites verified to still exist in current `src/`
- [x] srpchase profile re-confirmed (translates @ 846s on current main; same Cartesian-explosion bottleneck shape)
- [x] Patch design documented (no implementation yet — Section 2)
- [x] Test fixture plan documented (Section 3)
- [x] Projected impact stated (Section 4.1: +1–2 Translate; Section 4.2: 0–+1 Solve)
- [x] Unknowns 4.1, 4.2, 4.3, 4.4 verified and updated in KNOWN_UNKNOWNS.md

---

## 7. Files referenced

- `docs/planning/EPIC_4/SPRINT_25/PROFILE_HARD_TIMEOUTS.md` — Sprint 25 source design (Option 1 in §3.1)
- `docs/issues/ISSUE_1224_mine-paramref-index-offset-unsupported.md` — #1224 deferral context
- `src/ad/index_mapping.py:377-480` — `enumerate_equation_instances` (Option 1 patch site)
- `src/ad/index_mapping.py:115-222` — `resolve_set_members` (auxiliary; fallback warning emission, line 188)
- `src/ir/condition_eval.py:375-420` — `SetMembershipTest` evaluation path (raises `cannot be evaluated statically`)
- `/tmp/sprint26-task6-profile/srpchase.json` — current-main profile result (advisory, not committed)
- `/tmp/sprint26-task6-profile/{iswnm,sarf,mexls,nebrazil}.json` — 120s confirmation profiles (advisory, not committed)
- `/tmp/sprint26-task6-profile/iswnm-1800.json` — extended-budget profile (running in background; result will go in followup commit if it produces signal worth recording)
- `/tmp/task6-profile.py` — profile harness (advisory; if landing Option 1, move to `scripts/task6_profile.py` as a regression benchmark per PROFILE_HARD_TIMEOUTS §Appendix A note)

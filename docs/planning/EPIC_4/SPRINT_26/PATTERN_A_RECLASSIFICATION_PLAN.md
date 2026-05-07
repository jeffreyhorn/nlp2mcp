# Sprint 26 Pattern A Cohort Reclassification Plan

**Date:** 2026-05-07
**Task:** Sprint 26 Prep Task 4 (Pattern A Cohort Reclassification Pre-Work)
**Branch:** `planning/sprint26-task4`
**Source classification:** Sprint 25 Day 7 cohort sweep — `docs/planning/EPIC_4/SPRINT_25/DAY7_COHORT_SWEEP.md` §"Classification Table"
**Re-verification basis:** translate + emit on current `main` (post Sprint 25 fix-in-place series #1338..#1352)

---

## TL;DR

Per-issue action distribution across the 6 Pattern A cohort issues:

| Issue | Day 7 classification | Re-verified status (2026-05-07) | Sprint 26 Priority 2 action |
|---|---|---|---|
| #1138 (irscge family — 4 CGE models) | Pattern C plain-alias | ✅ Day 7 still accurate | **Subsume into Sprint 26 Priority 1 Phase B** |
| #1139 (meanvar) | AD-correct, pipeline-excluded | ✅ Day 7 still accurate | **Close as not-a-bug** |
| #1140 (ps2_f_s family — 7 stochastic models) | AD-correct multi-solve | ✅ Day 7 still accurate (and: 7 are now `non_convex` runtime-filter per Prep Task 2) | **Close as informational mismatch** |
| #1142 (launch) | Pattern C Bug #1 + Bug #2 | ⚠ Bug #1 fix ROLLED BACK in #1351 (current emit has phantom offsets again) | **Subsume into Sprint 26 Priority 1 Phase A** |
| #1145 (cclinpts) | Condition-guard / sign bug | ✅ Day 7 still accurate | **Close-and-refile as Sprint 27 issue** |
| #1150 (qabel + abel) | Split: qabel = Pattern C massive; abel = AD-correct | ❌ STALE — qabel "massive enumeration" GONE on current main; both halves now resolved | **Close as resolved** (#1311 fixed qabel; abel reclassified `non_convex` per Prep Task 2) |

**Sprint 26 Priority 2 effort (revised):**
- Original (Sprint 25 retrospective estimate): ~2–4h investigative + close work
- Revised (after Task 4): **~1.5h mechanical closure** (4 issue closures + 1 close-and-refile + 1 forward-link to Priority 1 PR)
- Time saved: 1–2.5h freed for Priority 1 (Phase A + B) or Priority 5 (#1334 follow-up + #1335)

**Test xfail impact:** 1 affected test — `tests/unit/kkt/test_pattern_c_alias_offset_gate.py::test_alias_only_conditional_sum_emits_no_phantom_offsets` (xfail strict=True). The test docstring already references #1142 + the Priority 1 Phase A fix as the un-xfail trigger. No other tests reference the 6 cohort issue numbers.

**Source/docs reference impact:** 1 source comment — `src/kkt/stationarity.py:4336` references "the launch comparison-mismatch family (#1226, #945, #1142)" as the tracker for the #1306 xfail. When #1142 closes (subsumed into Priority 1 Phase A), this comment should be updated to reference the Phase A PR instead.

---

## Per-issue actions

### Issue #1138: CGE Models — Alias-Aware Gradient Mismatch (irscge, lrgcge, moncge, stdcge)

**Current state:** OPEN, labeled `alias-differentiation`, `sprint-25`, `sprint-26`. Title: "CGE Models: Alias-Aware Gradient Mismatch (irscge, lrgcge, moncge, stdcge)".

**Day 7 sweep classification:** Pattern C plain-alias variant (NOT launch-shaped). Same family as quocge's pre-existing emission shape. Source `eqpzs(j).. pz(j) =e= ay(j)*py(j) + sum(i, ax(i,j)*pq(i))` has no IndexOffset; emit produces `nu_eqpzs(i±N)` per-offset enumeration via the alias-as-IndexOffset expansion path.

**Re-verification on current main (2026-05-07):**

```
$ grep -E "^stat_pq" /tmp/sprint26-task4-verify/irscge_mcp.gms | head -1
stat_pq(i).. ((-1) * ax(i,i)) * nu_eqpzs(i)
  + (((-1) * ax(i,i)) * nu_eqpzs(i+1))$(ord(i) <= card(i) - 1)
  + (((-1) * ax(i,i)) * nu_eqpzs(i-1))$(ord(i) > 1)
  + ... =E= 0;
```

✅ **Day 7 classification still accurate.** The `nu_eqpzs(i±1)` enumeration is present in the current emit. This is the exact bug shape that camcge (#1354) carries — the same Pattern C plain-alias variant identified during Sprint 26 Prep Task 3.

**Action: Subsume into Sprint 26 Priority 1 Phase B.**

When Sprint 26 Priority 1 Phase A (consolidated builder fix) + Phase B (gate generalization to plain-alias) lands, the irscge / lrgcge / moncge / stdcge family will be byte-stable (the per-offset enumeration consolidates to `sum(j$(domain_filter), ax(j,i) * nu_eqpzs(j))` — equivalent to the source).

**Closure mechanics (Sprint 26 Day N after Priority 1 Phase B PR merges):**
1. Verify the 4 CGE models are byte-stable post-Phase-B by comparing emit vs the un-buggy expected form.
2. Comment on #1138 with: "Subsumed by Sprint 26 Priority 1 Phase B (PR #NNNN). The plain-alias-variant Pattern C generalization eliminates the `nu_eqpzs(i±N)` enumeration on irscge / lrgcge / moncge / stdcge."
3. Close #1138 with `closes` reference to the Phase B PR.

**Test xfail impact:** None. No tests reference #1138.

**Source/docs reference impact:** None.

---

### Issue #1139: meanvar — Portfolio Quadratic Alias Gradient Mismatch

**Current state:** OPEN, labeled `alias-differentiation`, `sprint-25`, `sprint-26`. Title: "meanvar: Portfolio Quadratic Alias Gradient Mismatch".

**Day 7 sweep classification:** Other (AD-correct). meanvar is `legacy_excluded` (pipeline-dropped); the emit shows clean Sprint-24 renamed-alias sums with no phantom offsets and no zero-derivative.

**Re-verification on current main (2026-05-07):**

```
$ grep -cE "nu_[a-zA-Z_]+\([a-zA-Z]+[+-][0-9]+" /tmp/sprint26-task4-verify/meanvar_mcp.gms
0

$ grep -E "^stat_x" /tmp/sprint26-task4-verify/meanvar_mcp.gms | head -1
stat_x(i).. ((-1) * (sum(j__, x(j__) * q(i,j__)) + sum(i__, x(i__) * q(i__,i)))) * nu_vbal
  + nu_budget + (sf * sum(h, mu(h)) + (1 - sf) * mu(i)) * nu_meanbal
  - piL_x(i) + piU_x(i) =E= 0;
```

✅ **Day 7 classification still accurate.** Phantom-offset count = 0. The emit is structurally correct — the symmetric quadratic gradient is computed by two separately-aliased sums (`j__` for `q(i,j)` half + `i__` for `q(i,i)` half — Sprint 24 renaming pattern). Any rel_diff observed pre-S25 originates from a non-AD source (likely from `legacy_excluded` status preventing pipeline measurement at all).

**Action: Close as not-a-bug.**

The `legacy_excluded` schema status (per `data/gamslib/gamslib_status.json` v2.2.1) means meanvar is intentionally outside the comparison set. Whatever rel_diff originally motivated #1139 was either pre-S24 noise or measurement against a different scope.

**Closure mechanics (Sprint 26 Day 1):**
1. Comment on #1139 with: "Sprint 26 Prep Task 4 re-verification confirms meanvar's emit is AD-correct (`stat_x(i)..` uses clean Sprint-24 renamed-alias sums; phantom-offset count = 0). meanvar is `legacy_excluded` per the v2.2.1 schema — intentionally outside the comparison set. No action needed; closing as not-a-bug."
2. Close #1139.

**Test xfail impact:** None. No tests reference #1139.

**Source/docs reference impact:** None.

---

### Issue #1140: PS-Family Stochastic Programming — Alias Gradient Mismatch

**Current state:** OPEN, labeled `alias-differentiation`, `sprint-25`, `sprint-26`. Title: "PS-Family: Alias Gradient Mismatch in Stochastic Programming Models".

**Day 7 sweep classification:** Other (AD-correct multi-solve / stochastic dynamics). 7 affected models: ps2_f_s, ps2_s, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp, ps10_s. Emit has no phantom offsets or zeros. Rel_diff (0.5%–27.4% per Sprint 25 AUDIT) likely comes from scenario / multi-solve dynamics rather than the AD layer.

**Re-verification on current main (2026-05-07):**

```
$ grep -cE "nu_[a-zA-Z_]+\([a-zA-Z]+[+-][0-9]+" /tmp/sprint26-task4-verify/ps2_f_s_mcp.gms
0
```

✅ **Day 7 classification still accurate.** Phantom-offset count = 0.

**Additional context (post-Sprint-25):** All 7 PS-family models are now `convexity.status = non_convex` baseline, treated as runtime-filter (per `BASELINE_METRICS.md` §5). Their `solution_comparison.comparison_status = mismatch` is informational only — the same handling abel got after Sprint 26 Prep Task 2's reclassification analysis.

**Action: Close as informational mismatch.**

The 7 PS-family models are correctly classified as `non_convex` runtime-filter; their AD layer is correct; the rel_diff observed in pre-S25 measurements is NOT a bug to fix. The original "alias gradient mismatch" framing was incorrect — there is no alias bug in the emit.

**Closure mechanics (Sprint 26 Day 1):**
1. Comment on #1140 with: "Sprint 26 Prep Task 4 re-verification: ps2_f_s emit phantom-offset count = 0 (AD layer correct). All 7 PS-family models are now `convexity.status = non_convex` (per `BASELINE_METRICS.md` §5) and are runtime-filtered — their `solution_comparison.comparison_status = mismatch` is informational. The original 'alias gradient mismatch' framing was incorrect; closing as not-a-bug. If a follow-up rel_diff investigation is needed, file as Sprint 27 multi-solve dynamics workstream (separate issue scope)."
2. Close #1140.

**Test xfail impact:** None. No tests reference #1140.

**Source/docs reference impact:** None.

---

### Issue #1142: launch — Conditional Alias Gradient Mismatch

**Current state:** OPEN, labeled `alias-differentiation`, `sprint-25`, `sprint-26`. Title: "launch: Conditional Alias Gradient Mismatch".

**Day 7 sweep classification:** Pattern C Bug #1 (RESOLVED Day 6 PR #1308) + Bug #2 (pending #1307). Bug #1 = phantom ±N offsets on `nu_dweight`; Bug #2 = `nu_dweight(s)` inside `sum(ss, ...)` doesn't depend on `ss`, producing a spurious `card(ss-satisfying-ge)` factor.

**Re-verification on current main (2026-05-07):**

```
$ grep -E "^stat_iweight" /tmp/sprint26-task4-verify/launch_mcp.gms | head -1
stat_iweight(s).. (-1032.935643) * pweight(s) ** ... + iwf(s) * nu_diweight(s)
  + sum(ss, ((-1) * 1$(ge(ss,s))) * nu_dweight(s))
  + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s+1))$(ord(s) <= card(s) - 1))
  + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s+2))$(ord(s) <= card(s) - 2))
  + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s-1))$(ord(s) > 1))
  + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s-2))$(ord(s) > 2))
  + ... =E= 0;
```

⚠ **Day 7 classification needs an update.** The Day 7 sweep was conducted post-Day-6-PR-#1308 (Bug #1 fixed). But Sprint 25 Day 11 #1351 ROLLED BACK the Day 6 fix — the consolidated zero-offset builder lost cross-element aggregation, leaving launch with `model_infeasible`. So as of current main: **Bug #1 phantom offsets are BACK** (per the current emit), AND **Bug #2 is still pending**. The Sprint 26 Prep Task 3 PROCEED/REPLAN analysis already recommended addressing both via the two-phase Sprint 26 Priority 1 plan.

**Action: Subsume into Sprint 26 Priority 1 Phase A.**

Sprint 26 Priority 1 Phase A IS the launch fix per Sprint 25 SPRINT_LOG.md Day 11 §"Open follow-ups (revised)" — rewriting the consolidated zero-offset builder to emit `sum(ss$ge(s,ss), -nu_dweight(ss))` correctly (preserving cross-element aggregation). When Phase A lands, launch's Bug #1 + Bug #2 are both fixed.

**Closure mechanics (Sprint 26 Day N after Priority 1 Phase A PR merges):**
1. Verify launch's `stat_iweight` emit no longer has the per-offset `nu_dweight(s±N)` enumeration AND the consolidated `sum(ss, ...)` form correctly references `ss` (Bug #2 fix).
2. Comment on #1142 with: "Subsumed by Sprint 26 Priority 1 Phase A (PR #NNNN). Phase A's consolidated zero-offset builder rewrite eliminates both Bug #1 (phantom ±N offsets) and Bug #2 (mis-scoped `$(ge(ss, s))` body)."
3. Close #1142 with `closes` reference to the Phase A PR.
4. Also close #1306 (Bug #1) and #1307 (Bug #2) as duplicates of the Phase A PR — they share the same root cause.

**Test xfail impact:** ✅ **1 affected test.** `tests/unit/kkt/test_pattern_c_alias_offset_gate.py::test_alias_only_conditional_sum_emits_no_phantom_offsets` is currently `xfail(strict=True)` with reason explicitly tracking the Phase A fix:

> "the launch comparison-mismatch family (#1226, #945, #1142). Once that lands, remove this xfail."

When Phase A lands and the test passes, remove the `xfail` decorator.

**Source/docs reference impact:** 1 source comment in `src/kkt/stationarity.py:4336`:

```python
# The phantom-offsets quality concern from #1306 is re-tracked
# via the launch comparison-mismatch family (#1226, #945, #1142)
```

Replace with a forward-link to the Phase A PR after #1142 / #1306 / #1307 close.

---

### Issue #1145: cclinpts — Alias-Aware Gradient Mismatch (69.9%)

**Current state:** OPEN, labeled `alias-differentiation`, `sprint-25`, `sprint-26`. Title: "cclinpts: Alias-Aware Gradient Mismatch (69.9%)".

**Day 7 sweep classification:** Other (offset-handling / condition-guard bug, NOT Pattern A). `stat_b(j)` / `stat_fb(j)` have legitimate `fb(j-1) * 1$(not last(j))` / `b(j-1) * 1$(not first(j))` offset terms matching the source body. The 100% rel_diff suggests a condition-guard or sign bug downstream of AD.

**Re-verification on current main (2026-05-07):**

```
$ grep -E "^stat_b\(j\)|^stat_fb" /tmp/sprint26-task4-verify/cclinpts_mcp.gms | head -2
stat_b(j).. ((-1) * (((-1) * ((fb(j) - fb(j-1)) * 1$((not last(j)))))
  + 0.5 * (fb(j) - fb(j-1)) * 1$((not first(j)))))
  + ((-1) * ((1 - gamma) * b(j) ** (1 - gamma) * (1 - gamma) / b(j) / sqr(1 - gamma) ...
stat_fb(j).. ((-1) * (0.5 * (b(j) - b(j-1)) * 1$((not first(j)))))
  + nu_FBCalc(j) =E= 0;
```

✅ **Day 7 classification still accurate.** The legitimate `(j-1)` lag offsets matching the source are present; this is NOT a Pattern A bug. The original 69.9% rel_diff originates from a condition-guard or sign bug somewhere downstream of AD (not yet localized).

**Action: Close-and-refile as Sprint 27 issue.**

**Closure mechanics (Sprint 26 Day 1):**
1. File new Sprint 27 issue with the following draft:

   **Title:** "cclinpts: stat_b / stat_fb condition-guard or sign bug producing ~70% rel_diff (post-Pattern-A reclassification)"

   **Body:**

   ```markdown
   ## Problem Summary

   cclinpts produces `solution_comparison.comparison_status = mismatch` with NLP-MCP rel_diff ~69.9% on the obj. The Sprint 25 Day 7 cohort sweep determined this is NOT a Pattern A AD-layer bug (the emit has legitimate `fb(j-1) * 1$(not last(j))` lag offsets matching the source body) — it's a condition-guard or sign issue downstream of AD.

   Original alias-AD framing tracked under the now-closed #1145 (closed Sprint 26 Day 1 per Pattern A cohort reclassification — see `docs/planning/EPIC_4/SPRINT_26/PATTERN_A_RECLASSIFICATION_PLAN.md` §"Issue #1145").

   ## Reproduction

   ```bash
   .venv/bin/python -m src.cli data/gamslib/raw/cclinpts.gms \
     -o /tmp/cclinpts_mcp.gms --skip-convexity-check --quiet
   gams /tmp/cclinpts_mcp.gms lo=2
   # Compare obj vs cclinpts NLP solve
   ```

   ## Investigation pointers

   1. Inspect `stat_b(j)` and `stat_fb(j)` emit for sign convention vs the source NLP's `=e=` direction.
   2. Look at the `fb(j) - fb(j-1)` / `b(j) - b(j-1)` cross terms — does the AD layer correctly distinguish first-order forward vs first-order backward differences?
   3. Compare against a manually-computed KKT for one stationarity equation (Day 5 methodology).

   ## Files involved (preliminary)

   - `src/kkt/stationarity.py` (likely)
   - `data/gamslib/raw/cclinpts.gms`
   - `data/gamslib/mcp/cclinpts_mcp.gms`

   ## Effort estimate

   3–6h investigation + fix.

   ## Related

   - **#1145** (closed Sprint 26 Day 1) — the original alias-AD framing, reclassified out via Day 7 cohort sweep + Sprint 26 Prep Task 4.
   ```

2. Comment on #1145 with: "Sprint 26 Prep Task 4 re-verification confirms Day 7 sweep classification: this is NOT a Pattern A AD bug — the emit has legitimate offset terms matching the source body. Refiled as new Sprint 27 issue: #NNNN. Closing #1145."

3. Close #1145.

**Test xfail impact:** None. No tests reference #1145.

**Source/docs reference impact:** None.

---

### Issue #1150: AD regression — alias-aware differentiation collapses distinct sum indices (qabel + abel)

**Current state:** OPEN, labeled `sprint-25`, `sprint-26`. Title: "AD regression: alias-aware differentiation collapses distinct sum indices".

**Day 7 sweep classification:** Split — qabel = Pattern C massive enumeration variant (k-9..k-68 stateq enumeration); abel = AD-correct nonconvex/solver noise.

**Re-verification on current main (2026-05-07):**

```
$ grep -E "^stat_x" /tmp/sprint26-task4-verify/qabel_mcp.gms | head -1
stat_x(n,k).. 0.5 * (sum(np__, (x(np__,k) - xtilde(np__,k)) * w(n,np__,k))
  + sum(n__, (x(n__,k) - xtilde(n__,k)) * w(n__,n,k)))
  + ((-1) * a(n,n)) * nu_stateq(n,k)
  + (((-1) * a(n+1,n)) * nu_stateq(n+1,k))$(ord(n) <= card(n) - 1)
  + nu_stateq(n,k-1)$(ord(k) > 1)
  + (((-1) * a(n-1,n)) * nu_stateq(n-1,k))$(ord(n) > 1) =E= 0;

$ grep -oE "k[+-][0-9]+" /tmp/sprint26-task4-verify/qabel_mcp.gms | sort -u
k-1
k+1
```

❌ **Day 7 qabel classification is STALE.** The Day 7 sweep (2026-04-24) reported qabel had a "k-9..k-68 massive enumeration" of stateq offsets. Current main shows ONLY `k-1` and `k+1` — the legitimate single-step lead/lag matching the source `stateq(n, k+1)..  x(n, k+1) =e= a(n,n)*x(n,k) + a(n+1,n)*x(n+1,k) + a(n-1,n)*x(n-1,k) + ...`. The "massive enumeration" is GONE.

The qabel emit and abel emit are now structurally identical (the only diff is the `k` set definition and the alias `ku`/`ki` predicate form). Both have clean ±1 stateq lead/lag and the symmetric quadratic criterion derivative (`0.5 * (sum(np__, ...) + sum(n__, ...))`) — exactly the AD-correct form Day 5 / Day 7 already verified for abel.

**Resolution attribution:** This was almost certainly fixed by **#1311** (CLOSED 2026-04-25 during Sprint 25): "AD: criterion's u-quadratic gradient dropped to `Const(0.0)` when sum index is a subset of variable's domain (qabel/abel)". The #1311 fix unified qabel's emit shape with abel's clean form.

**Additional context (post-Sprint-25):** abel was reclassified `convexity.status = non_convex` on 2026-04-25 (see `docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md` §5.1, identified by Sprint 26 Prep Task 2). qabel was excluded from the convexity comparison via the multi-solve gate during Sprint 25.

**Action: Close as resolved (both halves).**

**Closure mechanics (Sprint 26 Day 1):**
1. Comment on #1150 with: "Sprint 26 Prep Task 4 re-verification confirms both halves of #1150 are resolved on current main:

   - **qabel half**: Day 7 sweep (2026-04-24) reported a `k-9..k-68` massive stateq enumeration. Current emit has ONLY clean `k-1`/`k+1` lead/lag offsets matching the source `stateq(n,k+1)` declaration. Resolution likely attributable to #1311 (CLOSED 2026-04-25) which fixed the AD subset-domain bug.
   - **abel half**: Day 7 sweep classified abel as AD-correct/solver noise. abel was subsequently reclassified `convexity.status = non_convex` on 2026-04-25 (Sprint 25 Day 4, commit `c922bb2d`) per `BASELINE_METRICS.md` §5.1 — runtime-filtered, `comparison_status = mismatch` is informational.

   No further action needed; closing as resolved. Re-verification evidence at `/tmp/sprint26-task4-verify/qabel_mcp.gms` vs `abel_mcp.gms` (now byte-identical apart from the `k` set definition)."

2. Close #1150.

**Test xfail impact:** None. No tests reference #1150.

**Source/docs reference impact:** None.

---

## Summary metrics

| Metric | Value |
|---|---|
| Total cohort issues | 6 |
| Day 7 classifications still accurate | 5 (#1138, #1139, #1140, #1142 with Bug #1 caveat, #1145) |
| Day 7 classifications stale on current main | 1 (#1150 qabel — already resolved) |
| Subsume into Priority 1 Phase A | 1 (#1142) |
| Subsume into Priority 1 Phase B | 1 (#1138) |
| Close as not-a-bug / informational | 3 (#1139, #1140, #1150) |
| Close-and-refile as Sprint 27 issue | 1 (#1145) |
| Test xfails affected | 1 (`test_alias_only_conditional_sum_emits_no_phantom_offsets`) |
| Source comment updates needed | 1 (`src/kkt/stationarity.py:4336`) |
| Sprint 26 Priority 2 effort estimate | ~1.5h mechanical closure |

## Cross-references

- Sprint 25 Day 7 cohort sweep (source of original classifications): `docs/planning/EPIC_4/SPRINT_25/DAY7_COHORT_SWEEP.md`
- Sprint 25 Audit (Pattern A/B/C/D/E framework): `docs/planning/EPIC_4/SPRINT_25/AUDIT_ALIAS_AD_CARRYFORWARD.md`
- Sprint 25 retrospective §Priority 2: `docs/planning/EPIC_4/SPRINT_25/SPRINT_RETROSPECTIVE.md`
- Sprint 26 Prep Task 2 — abel reclassification context for #1150 abel: `docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md` §5.1
- Sprint 26 Prep Task 3 — Pattern C hypothesis validation (motivates #1142 routing to Phase A): `docs/planning/EPIC_4/SPRINT_26/PATTERN_C_HYPOTHESIS_VALIDATION.md`
- Re-verification artifacts (advisory, not committed): `/tmp/sprint26-task4-verify/<model>_mcp.gms` for irscge, meanvar, ps2_f_s, launch, cclinpts, qabel, abel.

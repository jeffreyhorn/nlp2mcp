# Sprint 25 Day 7 — Pattern C Validation + Pattern A Cohort Classification Sweep

**Branch:** `sprint25-day7-pattern-c-validation-plus-cohort-sweep`
**Date:** 2026-04-24
**Purpose:** Validate the Day 6 Pattern C prototype on the full 54-model matching set, and perform an evidence-gathering sweep on the six original Pattern A candidate models (#1138, #1139, #1140, #1142, #1145, #1150) to confirm their actual symptom shape — establishing that dropping the original Phase 2 broader Pattern A rollout (per the Day 5 investigation) was correct.

Reproduction: traces captured at `/tmp/sprint25-day7/cohort/<model>_{mcp.gms,trace.stderr}` via

```bash
mkdir -p /tmp/sprint25-day7/cohort
SPRINT25_DAY2_DEBUG=1 .venv/bin/python -m src.cli data/gamslib/raw/<model>.gms \
  -o /tmp/sprint25-day7/cohort/<model>_mcp.gms --skip-convexity-check --quiet \
  2> /tmp/sprint25-day7/cohort/<model>_trace.stderr
```

---

## TL;DR

- **54-set golden-file regression: 54/54 PASS** (byte-identical to golden). Day 6 Pattern C gate causes zero regressions on the matching set.
- **launch (Pattern C Bug #1 fix) → locally infeasible at solve time.** Compile OK (`action=c` Normal completion). `Solve mcp_model` produces Model Status 5 (Locally Infeasible); PATH exits "other error" with residual 8.4e3; `nlp2mcp_obj_val = 3689.28` vs. NLP baseline ~2258. The structural phantom-offset fix lands correctly but does NOT numerically recover launch — consistent with Day-5 Bug #2 (issue #1307, mis-scoped `$(ge(ss, s))` condition with `nu_dweight(s)` outside the `sum` body) still biasing the stationarity. Launch is therefore **NOT** a Match candidate for the Day 14 pipeline retest until #1307 lands.
- **Pattern A cohort sweep confirms the Day 5 pivot was correct.** None of the 6 cohort models exhibits the original Pattern A fingerprint (AD emitting `0` for a known-nonzero derivative). Classification details below.

## Classification Table

| Issue | Model(s) | Shape | Day 6 gate behavior | Evidence |
|-------|----------|-------|---------------------|----------|
| #1138 | irscge (+ lrgcge, moncge, stdcge) | **Pattern C (plain-alias, not launch-shaped)** | Does NOT fire (correct — no conditional alias sum) | `stat_pq(i)`, `stat_tm(i)`, `stat_tz(j)` emit `nu_eqpzs(i+1)$(ord(i) <= card(i)-1)` etc. Source `eqpzs(j).. pz(j) =e= ay(j)*py(j) + sum(i, ax(i,j)*pq(i))` has no IndexOffset. Same family as quocge's pre-existing emission shape (already in Tier 1 canary / golden). |
| #1139 | meanvar | **Other (AD-correct structure)** | N/A | `stat_x(i)` emits clean Sprint-24 renamed-alias sums: `sum(j__, x(j__) * q(i,j__)) + sum(i__, x(i__) * q(i__,i))`. No phantom offsets, no zero-derivative. Rel_diff originates elsewhere. Pipeline-excluded per `AUDIT_ALIAS_AD_CARRYFORWARD.md` — no action needed for this sprint. |
| #1140 | ps2_f_s (+ ps2_s, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp, ps10_s — 7 total) | **Other (AD-correct structure; multi-solve / stochastic dynamics)** | N/A | `stat_w(i)`, `stat_x(i)` emit plain `sum(j, ...)` without phantom offsets or zeros. No Pattern-A AD gap visible in the emission. Rel_diff (0.5%–27.4% per AUDIT) likely comes from scenario/multi-solve dynamics rather than the AD layer. Separate investigation needed — NOT Pattern A. |
| #1142 | launch | **Pattern C Bug #1 (RESOLVED Day 6, PR #1308) + Bug #2 (pending #1307)** | Fires correctly; phantom ±N offsets on `nu_dweight` eliminated | See §Launch section below. Post-Day-6 emission has `iwf(s) * nu_diweight(s)` + single `sum(ss, ((-1) * 1$(ge(ss,s))) * nu_dweight(s))` term; Bug #2 (`nu_dweight(s)` inside `sum(ss, ...)` doesn't depend on `ss`) produces a spurious `card` factor, yielding Locally Infeasible solve. |
| #1145 | cclinpts | **Other (offset-handling / condition-guard bug, not AD phantom)** | N/A | `stat_b(j)` / `stat_fb(j)` have legitimate `fb(j-1) * 1$(not last(j))` / `b(j-1) * 1$(not first(j))` offset terms matching the source body. 100% rel_diff suggests a condition-guard or sign bug downstream of AD, not a Pattern A gap. Separate investigation needed. |
| #1150 | qabel | **Pattern C (massive enumeration — distinct variant)** | Does NOT fire (plain-alias path; source has `a(n±1,n)` so IndexOffset-present check blocks the gate) | `stat_x(n,k)` has enormous enumeration of offsets `k-9 .. k-68` with guards `$(ord(k) > N)`, plus `(n+1, k-N)` / `(n-1, k-N)` cross products — cardinality of k is ~68. Pre-existing since at least Day 5; unchanged by the Day 6 gate. This is a distinct Pattern C variant (large-k stateq enumeration) NOT touched by the launch-shaped gate. |
| #1150 | abel | **Other (AD-correct structure; nonconvex/solver noise)** | N/A | `stat_x(n,k)` emits clean 4-term form matching the symmetric quadratic derivative (per Day 5 investigation). AD is byte-correct. Rel_diff 29.8% likely from stateq domain-shift convention or nonconvex-solver noise. |

---

## Task 1 — Full 54-Set Golden-File Regression

Prerequisite: a golden-file tree from a Day 0 run at
`/tmp/sprint25-golden/<model>_mcp.gms` (created during the Sprint 25 Day 0
setup step — see `prompts/PLAN_PROMPTS.md` §"Day 0 Prompt"). If it doesn't
exist, regenerate from main before applying the Day 6 fix, then re-run
this regression on the Day-6 branch.

Command:

```bash
mkdir -p /tmp/sprint25-day7/fullset
if [ ! -d /tmp/sprint25-golden ]; then
  echo "ERROR: /tmp/sprint25-golden missing — regenerate per Day 0 setup." >&2
  exit 1
fi
MATCHING=($(python3 -c "import json, pathlib; d=json.loads(pathlib.Path('data/gamslib/gamslib_status.json').read_text()); \
  print(' '.join(e['model_id'] for e in d['models'] \
  if (e.get('solution_comparison') or {}).get('comparison_status') == 'match'))"))
for m in "${MATCHING[@]}"; do
  .venv/bin/python -m src.cli data/gamslib/raw/${m}.gms \
    -o /tmp/sprint25-day7/fullset/${m}_mcp.gms --skip-convexity-check --quiet > /dev/null 2>&1
  diff -q /tmp/sprint25-golden/${m}_mcp.gms /tmp/sprint25-day7/fullset/${m}_mcp.gms > /dev/null 2>&1 \
    && echo "✅ $m" || echo "❌ $m REGRESSED"
done
```

**Result: 54 PASS, 0 FAIL.** The Day 6 Pattern C gate produces byte-identical emissions for all 54 models in the matching set. The narrow "launch-shaped conditional alias sum" fingerprint means the gate only fires on the specific pattern documented in `DAY5_PATTERN_A_INVESTIGATION.md`; all other alias-iteration patterns (quocge, prolog, irscge, and everything in the Tier 0/1/2 canaries) are untouched.

---

## Task 2 — Full Launch Re-validation

**Compile-only check (`action=c`):** Normal completion. The emitted MCP parses and all symbols resolve.

**Full PATH solve:**

```text
**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      5 Locally Infeasible
----    395 PARAMETER nlp2mcp_obj_val      =     3689.280
```

Pre-Day-6 (from `DAY5_PATTERN_A_INVESTIGATION.md` + `ISSUE_1142`):
- Objective 2731.7 vs NLP baseline 2257.8 (17.4% rel_diff)

Post-Day-6:
- Objective 3689.28 vs NLP baseline 2257.8 (63% rel_diff) + **Locally Infeasible**

**Analysis:** The Pattern C Bug #1 fix is structurally correct (phantom ±N `nu_dweight` offsets gone), but the residual `sum(ss, ((-1) * 1$(ge(ss,s))) * nu_dweight(s))` still carries Bug #2 — the multiplier `nu_dweight(s)` doesn't depend on the summed index `ss`, so the sum degenerates into a `card(ss-satisfying-ge) * nu_dweight(s)` factor. That spurious `card` factor scales the stationarity contribution incorrectly, and PATH fails to find a feasible point. **Launch does NOT recover without the Bug #2 fix (issue #1307).**

Launch is therefore NOT flagged as a Match candidate for the Day 14 pipeline retest. The pipeline-retest Match count from Day 6 alone is expected to be unchanged vs baseline (+0 from Pattern C on launch). Any Match gain from the Pattern C family depends on whether other Pattern-C-shaped models exist that the gate DOES recover (see cohort sweep below — none of the 6 cohort models fit the exact launch-shape fingerprint, so Day 14's Pattern C Match delta is likely **0**).

---

## Task 3 — Pattern A Cohort Sanity Sweep

The six original Pattern A issues, mapped to concrete models per
`AUDIT_ALIAS_AD_CARRYFORWARD.md` §Pattern A table:

| Issue | Canonical models | Pipeline status | Sweep coverage |
|---|---|---|---|
| #1138 | irscge, lrgcge, moncge, stdcge | translate✅ / solve✅ / mismatch | Sampled `irscge` |
| #1139 | meanvar | `legacy_excluded` (pipeline-dropped) | Included for completeness |
| #1140 | ps2_f_s, ps2_s, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp, ps10_s | translate✅ / solve✅ / mismatch (7 models) | Sampled `ps2_f_s` (lowest rel_diff) |
| #1142 | launch | translate✅ / solve✅ / mismatch | Full; see §Launch above |
| #1145 | cclinpts | translate✅ / solve✅ / mismatch (100%) | Full |
| #1150 | qabel, abel | translate✅ / solve✅ / mismatch | Both |

No sweep-time AD `0`-derivative emissions observed across any of the 7 trace files. The `SPRINT25_DAY2_DEBUG=1` env flag activated the `[SPRINT25_DAY2]` trace lines in `src/ad/derivative_rules.py::_diff_varref` and `_partial_collapse_sum`; trace inspection showed normal substitution paths without the "gave up, emit 0" signature characteristic of the original Pattern A hypothesis.

## Evidence per model

### #1138 irscge — Pattern C (plain-alias, not launch-shape)

Emitted `stat_pq(i)`:

```gams
stat_pq(i).. ((-1) * ax(i,i)) * nu_eqpzs(i)
  + (((-1) * ax(i,i)) * nu_eqpzs(i+1))$(ord(i) <= card(i) - 1)
  + (((-1) * ax(i,i)) * nu_eqpzs(i-1))$(ord(i) > 1)
  + ... (other non-offset terms) ...
  =E= 0;
```

Source:
```gams
eqpzs(j).. pz(j) =e= ay(j)*py(j) + sum(i, ax(i,j)*pq(i));
```

The source has NO IndexOffset. `sum(i, ax(i,j)*pq(i))` iterates plain-alias `i` over its canonical set; cross-element Jacobian entries get grouped by positional offset in `_compute_index_offset_key`, same fingerprint as launch but without the `$condition(alias, eq_domain_idx)` qualifier. Day 6 gate's Precondition (b) (aliased conditional sum tied to eq domain) fails → gate does NOT fire → emission unchanged. This is the **same shape as quocge's stat_pq / stat_rt** (see `ISSUE_1306`'s discussion of quocge in PR #1308 review comments), deliberately out of scope for the narrow Day 6 gate.

Future Pattern C gate extension (candidate Sprint 26 work) could cover plain-alias iteration, but requires an evaluation of whether the current phantom-offset emission is merely *cosmetically noisy* or *numerically wrong* — quocge currently matches with the phantom shape, so a broader gate risks regressing it. Need more evidence before widening.

### #1139 meanvar — Other (AD-correct, pipeline-excluded)

Emitted `stat_x(i)`:
```gams
stat_x(i).. ((-1) * (sum(j__, x(j__) * q(i,j__))
                   + sum(i__, x(i__) * q(i__,i)))) * nu_vbal
            + nu_budget + (...) * nu_meanbal
            - piL_x(i) + piU_x(i) =E= 0;
```

Sprint 24's `_partial_collapse_sum` correctly produced the symmetric quadratic derivative (renamed aliases `j__`, `i__`). No phantom offsets, no zero-derivative emission. Pipeline status `legacy_excluded` per `AUDIT_ALIAS_AD_CARRYFORWARD.md` — not in the Match target scope for Sprint 25. No action.

### #1140 ps2_f_s — Other (multi-solve / stochastic dynamics)

Emitted `stat_w(i)`:
```gams
stat_w(i).. ((-1) * (p(i) * (-1))) - lam_pc(i)
            + sum(j, (-1) * lam_ic(i,j))
            - piL_w(i) =E= 0;
```

Plain `sum(j, ...)` with no offsets or zeros. The AD emission is clean. The 0.5%–27.4% rel_diff range across the 7-model ps-family per `AUDIT_ALIAS_AD_CARRYFORWARD.md` is more consistent with scenario / multi-solve dynamics (PS-family is stochastic programming) than with an AD gap. Separate investigation needed — target Sprint 26 carryforward, reclassified out of Pattern A.

### #1142 launch — Pattern C (Bug #1 resolved, Bug #2 pending)

See §Task 2 above. Post-Day-6 emission shows phantom offsets eliminated; Bug #2 still present per issue #1307. Launch still Locally Infeasible.

### #1145 cclinpts — Other (condition-guard / sign bug)

Emitted `stat_b(j)`:

```gams
stat_b(j).. ((-1) * (((-1) * ((fb(j) - fb(j-1)) * 1$((not last(j)))))
                   + 0.5 * (fb(j) - fb(j-1)) * 1$((not first(j)))))
          + ((-1) * ((1 - gamma) * b(j) ** (1 - gamma) * (1 - gamma) / b(j)
                     / sqr(1 - gamma))) * nu_FBCalc(j)
          + nu_b_fx_s1$(sameas(j, 's1'))
          + nu_b_fx_s30$(sameas(j, 's30'))
          - piL_b(j) + piU_b(j) =E= 0;
```

The `(fb(j) - fb(j-1)) * 1$(not last(j))` pattern matches source-level lead/lag with a `last(j)` domain guard. No phantom offsets on the multipliers; the `j-1` offset is real (matches the source objective's finite-difference terms). The 100% rel_diff more likely comes from:

- A sign flip on the finite-difference term, OR
- An incorrect handling of the `(not first(j))` / `(not last(j))` boundary conditions in the stationarity transpose, OR
- The `b(j) ** (1 - gamma)` derivative's algebraic form (numerator/denominator grouping).

This is **NOT a Pattern A AD gap** — it's a downstream emission/condition-handling bug. Reclassify as a separate issue; target Sprint 26.

### #1150 qabel — Pattern C (massive enumeration variant)

Emitted `stat_x(n,k)` has enumeration `nu_stateq(n, k-9)$(ord(k) > 9)` through `nu_stateq(n, k-68)` with cross-products by `(n±1, k-N)`. card(k) is ≈ 69 in qabel; the source body has stateq indexed by `(n, k+1)` at the LHS (one legitimate lead) plus `a(n±1, n)` param-level offsets, but the enumeration spans 68 lag values of k.

This is Pattern C-shaped (phantom lag enumeration driven by positional-offset Jacobian grouping), but NOT the launch shape — the source DOES have `a(n+1, n)` and `a(n-1, n)` IndexOffsets on `n`, so the Day 6 gate's Precondition (a) (no real IndexOffset on the variable's domain) fails → gate does NOT fire → emission unchanged. Pre-existing emission shape; unchanged from Day 5.

Separate investigation needed — qabel's k-offset enumeration is a distinct Pattern C variant that the current gate doesn't handle. Target Sprint 26.

### #1150 abel — Other (AD-correct; stateq convention or solver noise)

Emitted `stat_x(n,k)`:

```gams
stat_x(n,k).. 0.5 * (sum(np__, (x(np__,k) - xtilde(np__,k)) * w(n,np__,k))
                    + sum(n__, (x(n__,k) - xtilde(n__,k)) * w(n__,n,k)))
            + ((-1) * a(n,n)) * nu_stateq(n,k)
            + (((-1) * a(n+1,n)) * nu_stateq(n+1,k))$(ord(n) <= card(n) - 1)
            + nu_stateq(n,k-1)$(ord(k) > 1)
            + (((-1) * a(n-1,n)) * nu_stateq(n-1,k))$(ord(n) > 1)
            =E= 0;
```

Clean — 5 terms matching the symmetric quadratic criterion derivative + stateq Jacobian-transpose with ±1 offsets on both `n` and `k`. AD is byte-correct per Day 5 (`DAY5_PATTERN_A_INVESTIGATION.md` §"Evidence — AD layer is correct (qabel / abel)"). abel's card(k) is small (2), so no massive k-enumeration like qabel. The 29.8% rel_diff is likely from nonconvex-solver behavior (abel is a nonlinear QP-like model) or the stateq domain-shift convention per the Day 5 notes — NOT an AD gap. No Sprint 25 action beyond the existing Day 8 PATH-solve reassessment plan.

---

## Synthesis

The Day 5 pivot was correct. The original Pattern A hypothesis — that `_partial_collapse_sum` multi-index concrete→symbolic recovery would unblock the 6 cohort models — does not match the bug surface we actually see. Breakdown of the cohort by shape:

- **Pattern C variants (3 of 6):** #1138 irscge (plain-alias, same family as quocge), #1142 launch (launch-shape, Day 6 fixed Bug #1), #1150 qabel (massive k-enumeration). Only launch's variant is covered by the current Day 6 gate.
- **Other (3 of 6):** #1139 meanvar (AD correct, pipeline-excluded), #1140 ps2_f_s family (AD correct, stochastic/multi-solve dynamics), #1145 cclinpts (condition-guard / sign bug), #1150 abel (AD correct, stateq convention or solver noise).

**Nothing in the cohort matches the original Pattern A fingerprint** (AD emitting `0` for a known-nonzero derivative via a `_partial_collapse_sum` gap). Phase 2 in its originally-scoped shape remains dropped.

Future work spillover (Sprint 26 or Day 13 buffer):
- Plain-alias Pattern C variant (irscge, quocge family): extend gate after evaluating quocge's current-matching numerical behavior.
- Massive-enumeration Pattern C variant (qabel): separate investigation into why `_compute_index_offset_key` groups produce `k-9..k-68` offsets; may be upstream of the gate.
- cclinpts condition-guard bug: separate issue, needs its own reproducer.
- ps-family stochastic-dynamics rel_diff: evaluate against multi-solve driver semantics (separate workstream).

## Tier 0 + Tier 1 canary

Ran post-cohort-sweep to confirm nothing regressed in tandem:

```
✅ dispatch  ✅ quocge  ✅ partssupply  ✅ prolog  ✅ sparta
✅ gussrisk  ✅ ps2_f  ✅ ps3_f  ✅ ship  ✅ splcge  ✅ paklive
```

All 11 canaries byte-identical to golden.

---

## Gate decision — Day 14 retest expectations

Revised Match-target expectations per this sweep:

- **+0 from Pattern C on launch** (Bug #2 blocks launch recovery until #1307).
- **+0 from cohort sweep** (no additional Pattern-C-shaped models fixable by the current narrow gate).
- **Pattern C Bug #2 fix (#1307)** is now the single remaining lever for a launch Match — target Day 13 buffer OR Sprint 26 per the Day 6 prompt task 9.

The Day 5 pivot's +2 Match projection (+1 launch, +1 contingent qabel via Day 8) has shifted:

- +1 contingent qabel via Day 8 PATH solve unchanged — still gated on the Day 8 reassessment.
- +1 launch via Pattern C now gated on #1307 landing — unlikely in Sprint 25.

Revised Sprint 25 Match-target: **≥54 (baseline hold, not the earlier ≥56)**. Day 8 PATH solve reassessment (qabel/abel) is the remaining lever for a single-model Match gain.

---

## Files referenced

- Regression artifacts: `/tmp/sprint25-day7/fullset/*.gms` (54 files, byte-identical to golden).
- Cohort traces + MCP output: `/tmp/sprint25-day7/cohort/*_{mcp.gms,trace.stderr}`.
- Launch compile + solve logs: `/tmp/sprint25-day7/launch_{compile.log,mcp.log,mcp.lst}`.
- Day 5 investigation: `DAY5_PATTERN_A_INVESTIGATION.md`.
- Day 6 Pattern C prototype: `docs/issues/completed/ISSUE_1306_launch-pattern-c-phantom-offsets.md`.
- Day 6 Bug #2 follow-up: `docs/issues/ISSUE_1307_launch-pattern-c-misscoped-alias-condition.md`.

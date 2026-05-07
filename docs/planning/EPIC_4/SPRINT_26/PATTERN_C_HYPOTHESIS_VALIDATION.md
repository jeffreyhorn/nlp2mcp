# Sprint 26 Pattern C Generalization — Hypothesis Validation (PR16)

**Date:** 2026-05-07
**Task:** Sprint 26 Prep Task 3 (PR16 — pre-Sprint-0 hypothesis validation)
**Methodology:** Sprint 25 Day 5 — trace capture + emitted-artifact byte comparison against formal symbolic derivative
**Branch:** `planning/sprint26-task3`
**Models examined:** camcge, cesam2, fawley (held-out: otpop)
**Decision:** ⚠️ **REPLAN Sprint 26 Priority 1**

---

## TL;DR

The Sprint 26 Priority 1 hypothesis as written — _"the launch-shape Pattern C gate generalizes to plain-alias enumeration AND `sameas`-decomposed SAM-block aliases via a 1-line `$cond` filter removal, unblocking 4 target models (camcge, cesam2, fawley, otpop) with +4 Solve / +3–4 Match"_ — is **disproved on two of four target models** and **structurally insufficient on the remaining two**:

1. **fawley (#1356) is NOT a Pattern C variant.** Static analysis shows zero phantom-`IndexOffset` enumeration in fawley's emit. GAMS compile errors trace to subset/superset domain widening in `comp_up_u(c)` and `piU_u.fx(c)` — distinct bug family that belongs in Priority 5 (AD residuals) or a new workstream, not Pattern C.

2. **otpop (#1357) is also not primarily a Pattern C variant.** The `$171` errors trace to the same subset/superset comp_up shape as fawley. The `$141` cascade has phantom-offset markers but those are the #1334 ParamRef substitution issue. Per the issue doc itself: "likely subsumed by #1334."

3. **camcge (#1354) and cesam2 (#1355) ARE Pattern C variants.** The buggy emit shape on both matches the launch-shape alias-as-IndexOffset expansion, with cesam2 carrying additional `sameas`-block guards. Hand-derived formal KKT confirms a clean `sum(j$(domain_filter), ...)` form is the correct fix shape.

4. **The 1-line `$cond` removal hypothesis is structurally insufficient even for camcge/cesam2.** Sprint 25 Day 11 issue #1351 disabled the launch-shape Pattern C gate (`allow_nonzero_offsets = True` hardcoded in `src/kkt/stationarity.py:4339`) because the downstream consolidated zero-offset builder collapses all offset groups to a single zero-offset term, losing cross-element aggregation. A prototype patch confirming this bug was implemented during Task 3 and produced byte-level regressions on 3 of 12 canary+launch outputs (quocge, prolog, launch) — the same launch failure mode that #1351 rolled back. Per Sprint 25 SPRINT_LOG.md Day 11 §"Open follow-ups (revised)":

   > Sprint 26: proper fix for the launch Pattern C consolidation (#1306 test xfail) — make consolidated zero-offset Sum iterate over the equation domain with the body's condition (`sum(ss$ge(s,ss), -nu_dweight(ss))` instead of the over-counting `sum(ss, -1$ge(ss,s) * nu_dweight(s))` per-offset enumeration), then remove both the xfail and the no-op `if eq_def_for_gate is not None:` branch.

**Recommendation:** REPLAN Priority 1 with a two-phase scope:
- **Phase A (~6h):** Fix the consolidated zero-offset builder per Sprint 25 #1351 follow-up. Restore the launch fix (#1306) and remove the `xfail` regression test.
- **Phase B (~6–10h):** Generalize the gate predicate to plain-alias (camcge) and `sameas`-decomposed (cesam2). This is _impossible_ without Phase A — broader gate + broken builder reproduces #1351 on more models.
- **Reduce target list:** 4 → **2** (camcge + cesam2). fawley and otpop reclassify out of Priority 1.
- **Revised effort:** 12–16h (vs original 12–18h, with 2 fewer targets but additional builder fix scope).

---

## 1. Methodology

Per Sprint 25 retrospective process recommendation **PR16**, this prep task applies the Day 5 methodology PRE-Sprint-0 to validate the Pattern C generalization hypothesis before committing the Priority 1 budget.

### 1.1 Trace capture

The 3 primary target models (camcge, cesam2, fawley) get full Day-5-methodology treatment (trace + emit + hand-derived formal KKT). The 4th model otpop is held out as a confirmation check after the primary 3 — the issue doc itself flags otpop as "likely subsumed by #1334" so it's run for completeness but not given a separate hand-derived KKT in §1.2.

```bash
mkdir -p /tmp/sprint26-day0-validation

# Primary 3 targets (full Day-5 treatment)
for m in camcge cesam2 fawley; do
  SPRINT25_DAY2_DEBUG=1 .venv/bin/python -m src.cli \
    data/gamslib/raw/${m}.gms \
    -o /tmp/sprint26-day0-validation/${m}_mcp.gms \
    --skip-convexity-check --quiet \
    2> /tmp/sprint26-day0-validation/${m}_trace.stderr
done

# Held-out 4th model (subsumption check — see §2.4)
SPRINT25_DAY2_DEBUG=1 .venv/bin/python -m src.cli \
  data/gamslib/raw/otpop.gms \
  -o /tmp/sprint26-day0-validation/otpop_mcp.gms \
  --skip-convexity-check --quiet \
  2> /tmp/sprint26-day0-validation/otpop_trace.stderr
```

All 4 models translate cleanly (exit=0, no stderr errors). Output: 4 `_mcp.gms` files + 4 `_trace.stderr` files in `/tmp/sprint26-day0-validation/`.

### 1.2 Hand-derived formal KKT

For each of the 3 primary target models, the formal Lagrangian derivative was hand-derived from the source NLP:

- camcge `stat_dk(i)` — `/tmp/sprint26-day0-validation/camcge_formal_kkt.md`
- cesam2 `stat_tsam(i,j)` — `/tmp/sprint26-day0-validation/cesam2_formal_kkt.md`
- fawley `stat_u(c)` (closest stationarity to the bug site) — `/tmp/sprint26-day0-validation/fawley_formal_kkt.md`

### 1.3 Byte-comparison against emitted form

Each emit was statically inspected for phantom-offset patterns:

```bash
grep -oE "nu_[a-zA-Z_]+\([a-zA-Z]+[+-][0-9]+" \
  /tmp/sprint26-day0-validation/<model>_mcp.gms | sort | uniq -c
```

| Model | Phantom-offset count | Pattern C shape |
|---|---|---|
| camcge | ≥ 100 (across `nu_ieq`, `nu_actp`, `nu_pkdef`, `nu_inteq`, `nu_prodinv`) | ✅ Confirmed |
| cesam2 | 18 distinct (`nu_COLSUM(i±N)` for N=1..9) | ✅ Confirmed |
| fawley | **0** | ❌ Disproved |
| otpop | 5 (mostly `nu_adef(tt+N)`, `nu_pdef(tt+N)`) — but the `$171` blocker is comp_up | ⚠ Partial / non-blocking |

### 1.4 GAMS compile verification (fawley + otpop)

```bash
gams /tmp/sprint26-day0-validation/<m>_mcp.gms a=c lo=2 \
  o=/tmp/sprint26-day0-validation/<m>.lst
grep -nE "\\\$171|\\\$141|\\\$257" /tmp/sprint26-day0-validation/<m>.lst
```

- **fawley**: `$171` at lst lines 273, 317 → both reference `crdat(c,"supply")` where `crdat` is on subset `cr` and the equation instance variable is `c` (superset).
- **otpop**: `$171` at lst lines 221, 253 → `comp_up_x(tt)$(t(tt) and xb(tt) < inf)` referencing `xb(tt)` where `xb` is declared on subset.

Both are **subset/superset comp_up domain widening bugs**, not Pattern C.

### 1.5 Prototype patch — broader gate experiment

To validate Unknown 1.1 (canary regression risk) and confirm the #1351 architectural concern, a temporary instrumentation patch was applied to `src/kkt/stationarity.py:4339` re-enabling the gate with the broader predicate (no `$cond` filter required) and adding `[SPRINT26_PATTERN_C_GATE_FIRED]` debug marker. The patch was reverted before commit; full source preserved in this document for reference.

The prototype:
1. Set `allow_nonzero_offsets = False` on the broader predicate (body has no IndexOffset on the variable's domain — no `$cond` filter required).
2. Emitted a debug marker per gate firing.

```bash
mkdir -p /tmp/sprint26-prototype-canaries
for m in dispatch quocge partssupply prolog sparta gussrisk ps2_f ps3_f \
         ship splcge paklive launch camcge cesam2 fawley otpop; do
  .venv/bin/python -m src.cli data/gamslib/raw/${m}.gms \
    -o /tmp/sprint26-prototype-canaries/${m}_mcp.gms --skip-convexity-check --quiet \
    2> /tmp/sprint26-prototype-canaries/${m}_gate.stderr
done
```

#### Gate-firing count (prototype on Tier 0/1 canaries + launch + targets)

| Model | Firings | Byte-stable vs baseline? |
|---|---|---|
| dispatch | 0 | ✅ Yes |
| quocge | 67 | ❌ **REGRESSED** (14 diff lines) |
| partssupply | 4 | ✅ Yes |
| prolog | 13 | ❌ **REGRESSED** (4 diff lines) |
| sparta | 0 | ✅ Yes |
| gussrisk | 0 | ✅ Yes |
| ps2_f | 4 | ✅ Yes |
| ps3_f | 4 | ✅ Yes |
| ship | 6 | ✅ Yes |
| splcge | 14 | ✅ Yes |
| paklive | 10 | ✅ Yes |
| **launch** | 24 | ❌ **REGRESSED** (8 diff lines — #1351 reproduction) |
| **camcge** (target) | 70 | (target — expected to change) |
| **cesam2** (target) | 24 | (target — expected to change) |
| fawley (target) | 15 | (target firings — but no Pattern C bug present) |
| otpop (target) | 6 | (target firings — but $171 is non-Pattern-C) |

**Gate-firing total: 261 across canaries + launch + targets.** Per Unknown 1.1, the expected was "4–8 firings" if the gate was correctly selective. Actual: **122 firings on the 11 canaries alone**. The broader predicate (no `$cond` filter) is **far too permissive** — fires on any model where any equation has an alias-only inner sum.

**Most firings produced no byte diff** because most matched offset_groups have only a single zero-offset key already, so the consolidation is a no-op. But on three models — quocge (`stat_pq`, `stat_rt`, `stat_tm`, `stat_tz`), prolog (`stat_q`), and launch (`stat_iweight`, `stat_pweight`) — the prototype produced byte-level regressions: per-offset terms collapse into single zero-offset terms, losing cross-element aggregation. **This is the #1351 bug reproduced on 3 of 12 canary+launch outputs.**

### 1.6 Diff excerpt (launch — the #1351 reproduction)

```diff
-stat_iweight(s).. ... + sum(ss, ((-1) * 1$(ge(ss,s))) * nu_dweight(s))
-                       + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s+1))$(ord(s) <= card(s) - 1))
-                       + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s+2))$(ord(s) <= card(s) - 2))
-                       + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s-1))$(ord(s) > 1))
-                       + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s-2))$(ord(s) > 2))
-                       + ... =E= 0;
+stat_iweight(s).. ... + sum(ss, ((-1) * 1$(ge(ss,s))) * nu_dweight(s))
+                       + ... =E= 0;
```

The 5 per-offset terms (s, s±1, s±2) collapsed to a single `sum(ss, ((-1)*1$(ge(ss,s))) * nu_dweight(s))` term. Cross-element aggregation lost. Same bug as Sprint 25 Day 11 reported in #1351.

#### Diff excerpt (quocge — new regression NOT covered by Sprint 25 Day 6)

```diff
-stat_pq(i).. ((-1) * ax(i,i)) * nu_eqpzs(i)
-           + (((-1) * ax(i,i)) * nu_eqpzs(i+1))$(ord(i) <= card(i) - 1)
-           + (((-1) * ax(i,i)) * nu_eqpzs(i-1))$(ord(i) > 1)
-           + ... =E= 0;
+stat_pq(i).. ((-1) * ax(i,i)) * nu_eqpzs(i) + ... =E= 0;
```

quocge `stat_pq` has 3 per-offset terms `(i, i+1, i-1)` that all collapse to the single `(i)` term. **A canary that was previously byte-stable now regresses**, demonstrating the broader gate is not bounded by the launch shape — it activates on the quocge `eqpzs(j).. pz(j) =e= ... + sum(i, ax(i,j)*pq(i))` plain-alias enumeration as well.

This is exactly what Sprint 25 retrospective §"What We'd Do Differently" #1 (PR16) said would happen if the hypothesis is wrong: "wrong about the cohort." 4 of 4 target models, only 2 actually exhibit the hypothesis-claimed shape, and the 1-line "fix" regresses canaries.

---

## 2. Per-model verdicts

### 2.1 camcge (#1354): ✅ CONFIRMED Pattern C plain-alias variant

- **Bug shape:** alias-as-IndexOffset expansion of `sum(j, imat(i,j)*dk(j))` into 21 per-offset condition-guarded terms `nu_ieq(i±N)$(ord(i) <op> ...)` for N ∈ {-10..+10}.
- **Formal KKT (hand-derived):** `stat_dk(i)..  pk(i)*nu_prodinv(i) - sum(j, imat(j,i) * nu_ieq(j)) =e= 0;`
- **GAMS-compile failure mode:** `$141` on `nu_ieq(i+10)` etc. — symbol declared but reference is symbolically out-of-domain.
- **Card(i) = 11**, so `±10` enumeration covers all 11 elements exactly once per i — equivalent to a sum-over-j.
- **Prototype gate firings on camcge:** 70 (across 5 distinct multipliers — `nu_ieq`, `nu_actp`, `nu_pkdef`, `nu_inteq`, `nu_prodinv`).
- **Required fix (with builder fixed):** consolidation to `sum(j$(domain_filter), imat(j,i) * nu_ieq(j))`.
- **Subsumed by Phase B fix:** ✅ Yes.

### 2.2 cesam2 (#1355): ✅ CONFIRMED Pattern C sameas-decomposed variant

- **Bug shape:** alias-as-IndexOffset expansion of `sum(jj, TSAM(ii,jj))` for `COLSUM(jj)` differentiation, with additional sameas-block guards from the SAM-tabular structure decomposition.
- **Formal KKT (hand-derived):** `stat_tsam(i,j)..  nu_ROWSUM(i)$(ii(i)) + nu_COLSUM(j)$(jj(j)) + ... =e= 0;` (the `nu_COLSUM(j)` reference has `j` as the variable's second index, NOT enumerated via offsets).
- **GAMS-compile failure mode:** `$141` on `nu_COLSUM(i+9)$(jj(i+9))` etc.
- **Card(i) = 10**, so `±9` enumeration covers all 10 elements.
- **Prototype gate firings on cesam2:** 24.
- **Required fix (with builder fixed):** consolidation to `nu_COLSUM(j)$(jj(j) and <sameas-block-guard>)`.
- **Subsumed by Phase B fix:** ✅ Yes — but Phase B requires sameas-block guard preservation in the consolidated builder.
- **Additional risk:** the consolidated builder must merge the equation-domain sum with the sameas-block guard correctly; the launch-shape fix alone (Phase A) does not give us this for free.

### 2.3 fawley (#1356): ❌ DISPROVED — not a Pattern C variant

- **Bug shape:** `comp_up_u(c)$(cr(c) and crdat(c,"supply") < inf)..` references `crdat(c,"supply")` where `c` is the superset and `crdat` is declared on subset `cr`. Subset/superset domain widening violation.
- **Phantom-offset count:** 0.
- **GAMS-compile failure mode:** `$171` ("Domain violation for set") on `crdat(c,"supply")` references at lst lines 273 and 317.
- **NOT a stationarity bug:** The `stat_u(c)` emit is structurally correct. The bug is in `comp_up_u` and `piU_u.fx` emission.
- **Required fix:** subset-aware comp_up emission — either narrow the equation domain to `cr` directly, or wrap parameter references with explicit subset gates (`crdat(cr,"supply")$cr(c)`).
- **Subsumed by Phase B fix:** ❌ NO — different code path entirely (`src/kkt/complementarity.py` and `src/emit/emit_gams.py`, not `src/kkt/stationarity.py`).
- **Reclassification proposal:** route to Sprint 26 Priority 5 (AD residuals — orthogonal subset-domain work alongside #1334) or file a new dedicated workstream for comp_up subset-domain widening.

### 2.4 otpop (#1357): ⚠ PARTIAL — `$171` is comp_up subset/superset, `$141` is #1334 ParamRef

- **Bug shape (primary blocker, $171):** same comp_up subset/superset shape as fawley. `comp_up_x(tt)$(t(tt) and xb(tt) < inf)..` references `xb(tt)` where `tt` is the superset and `xb` is on subset `t`.
- **Bug shape (secondary, $141):** small phantom-offset count (5 markers across `nu_adef`, `nu_pdef`) — these match the #1334 ParamRef substitution issue described in `docs/issues/ISSUE_1334_ad-scalar-constraint-spurious-sum-on-subset-param-domain.md`.
- **Per the issue doc itself**: "Possibly subsumed by #1334." Confirmed — `$141` cascade is the #1334 spurious-Sum-on-subset-ParamRef bug.
- **Required fix:**
  - $171 portion: same comp_up subset-domain widening fix as fawley.
  - $141 portion: subsumed by #1334 (Priority 5 in Sprint 26).
- **Subsumed by Phase B fix:** ❌ NO — neither bug shape is Pattern C.
- **Reclassification proposal:** close #1357 as duplicate of #1334 + the comp_up subset-domain bug filed alongside fawley's reclassification.

---

## 3. Decision: REPLAN Sprint 26 Priority 1

### 3.1 Per Unknown 1.6 decision rule

| Hypothesis status | Threshold |
|---|---|
| 3/3 PROCEED | Sprint 26 commits Priority 1 budget as planned |
| 2/3 PROCEED | Defer disproved model to Sprint 27, proceed with 2-target Priority 1 |
| 1/3 or 0/3 PROCEED | REPLAN Priority 1 entirely |

**Actual:** 2/3 confirmed Pattern C (camcge, cesam2). 1/3 disproved (fawley). Held-out otpop also disproved as primarily Pattern C.

**By the literal decision rule: 2/3 PROCEED → defer disproved models, proceed with 2-target Priority 1.**

### 3.2 But: the #1351 architectural blocker requires REPLAN even on the 2 confirmed sites

The 2/3 PROCEED threshold assumes the Pattern C fix is achievable via gate widening. It is not — the prototype patch (gate enabled with broader predicate) reproduces the #1351 launch bug PLUS introduces new versions on quocge and prolog. The downstream consolidated zero-offset builder is structurally broken for any Pattern C variant.

**Sprint 26 Priority 1 cannot be a 1-line `$cond` removal.** It requires:

- **Phase A (~6h):** Restore the launch fix by re-implementing the consolidated zero-offset builder so it emits `sum(j$(domain_filter), <body>)` over the equation domain, preserving cross-element aggregation. Per Sprint 25 SPRINT_LOG.md Day 11 §"Open follow-ups":

  > make consolidated zero-offset Sum iterate over the equation domain with the body's condition (`sum(ss$ge(s,ss), -nu_dweight(ss))` instead of the over-counting `sum(ss, -1$ge(ss,s) * nu_dweight(s))` per-offset enumeration), then remove both the xfail and the no-op `if eq_def_for_gate is not None:` branch.

- **Phase B (~6–10h):** Generalize the gate predicate to plain-alias (catches camcge) and `sameas`-decomposed (catches cesam2). Re-enable on the 2 confirmed Pattern C target sites only. The predicate must be tighter than "any alias-only inner sum" — it must require the source body's expansion to currently be enumerated as per-offset terms, AND the consolidation must preserve sameas-block guards for cesam2.

- **Reduce target list 4 → 2:** Remove fawley and otpop from Pattern C scope. Re-route to:
  - Priority 5 (AD residuals) for the comp_up subset/superset bugs — they share investigation territory with #1334.
  - Or file a new workstream for comp_up subset-domain widening if Priority 5 is full.

### 3.3 Revised Sprint 26 Priority 1 budget

| Original | Revised |
|---|---|
| 12–18h, 4 target models, "remove the $cond filter" | 12–16h, 2 target models, **2-phase: builder fix + gate generalization** |
| Projected: +4 Solve / +3–4 Match | Projected: +2 Solve / +2 Match (camcge + cesam2 only) |
| Risk: cascading #1351 bug across canaries | Risk: lower — Phase A unblocks the architecture; Phase B is tightly scoped |

The reduced projected gain (+2 Solve / +2 Match instead of +4 Solve / +3–4 Match) is the cost of accurate scope. Sprint 26 retrospective should compare this projection against final to validate the PR16 prep methodology.

---

## 4. Tier 0/1 canary regression report (prototype patch)

Run on a temporarily-applied broader-gate prototype (set `allow_nonzero_offsets = False` on the no-`$cond`-filter predicate). Patch reverted before committing this validation document.

| Canary model | Firings | Byte-diff |
|---|---|---|
| dispatch | 0 | byte-stable |
| quocge | 67 | **REGRESSED** (4 stat equations: `stat_pq`, `stat_rt`, `stat_tm`, `stat_tz` lose per-offset terms) |
| partssupply | 4 | byte-stable |
| prolog | 13 | **REGRESSED** (`stat_q(i,t)` loses 4 of 5 condition-guarded terms) |
| sparta | 0 | byte-stable |
| gussrisk | 0 | byte-stable |
| ps2_f | 4 | byte-stable |
| ps3_f | 4 | byte-stable |
| ship | 6 | byte-stable |
| splcge | 14 | byte-stable |
| paklive | 10 | byte-stable |

**Canary regressions: 2 of 11 (quocge, prolog). Plus launch (12th model) regresses with the #1351 reproduction.**

Trace files at `/tmp/sprint26-prototype-canaries/<model>_gate.stderr` (advisory, not committed).
Hand-derived formal-KKT excerpts at `/tmp/sprint26-day0-validation/<model>_formal_kkt.md` (advisory, not committed).

---

## 5. Prototype patch (NOT committed to main — for reference only)

The prototype patch applied to `src/kkt/stationarity.py:4339` and immediately reverted:

```python
# Line 4339 — ORIGINAL (the no-op left in place after #1351):
allow_nonzero_offsets = True
if eq_def_for_gate is not None and variable_canonical_sets:
    pass

# PROTOTYPE (broader gate — produces #1351 bug on launch + 2 canaries):
allow_nonzero_offsets = True
if eq_def_for_gate is not None and variable_canonical_sets:
    if not _body_has_index_offset_on_sets(
        eq_def_for_gate.lhs_rhs[0], variable_canonical_sets, kkt.model_ir,
    ) and not _body_has_index_offset_on_sets(
        eq_def_for_gate.lhs_rhs[1], variable_canonical_sets, kkt.model_ir,
    ):
        import sys as _sys
        _sys.stderr.write(
            f"[SPRINT26_PATTERN_C_GATE_FIRED] eq={eq_name_base}\n"
        )
        allow_nonzero_offsets = False
```

The prototype IS NOT a recommended Sprint 26 Day 1 starting point. It is solely the validation experiment that disproves the simple-gate-widening hypothesis.

The actual Sprint 26 Day 1 starting point should be Phase A: rewriting the consolidated zero-offset builder. Phase B's gate predicate may end up looking like the prototype, but only after Phase A is in place.

---

## 6. Recommendations to Sprint 26 PROJECT_PLAN.md / Issues

### 6.1 Update Priority 1 scope in `docs/planning/EPIC_4/PROJECT_PLAN.md` Sprint 26 entry

- Replace "validate the 'plain-alias variant of Pattern C' hypothesis on 2–3 representative models (e.g. camcge + cesam2 + fawley) using the Day 5 methodology" → "validation complete (Task 3, 2026-05-07): hypothesis confirmed on camcge + cesam2 only; fawley reclassified to comp_up subset-domain workstream. Priority 1 scope: Phase A consolidated-builder fix + Phase B gate generalization for 2 targets."
- Update target-list bullet from 4 → 2.
- Update +Solve / +Match projection accordingly (+2 Solve / +2 Match if Phase A+B both land).

### 6.2 Update issue docs

- `docs/issues/ISSUE_1356_fawley-stationarity-domain-violations-171.md`:
  - §"Likely Root Cause" → mark case (1) confirmed (subset/superset comp_up domain violation, not Pattern C).
  - §"Where to Investigate" → narrow to `comp_up_u`, `piU_u.fx` emission, NOT `src/kkt/stationarity.py`.
  - §"Related" → remove "#1354 / #1355 (Pattern C variant family)" association; add cross-reference to Priority 5 / #1334 routing.
- `docs/issues/ISSUE_1357_otpop-stationarity-domain-violations-171.md`:
  - Confirm subsumption by #1334 for the `$141` portion.
  - Carve out the `$171` comp_up bug as separate from #1334 (also a subset-domain widening, different code path).
  - Cross-reference fawley's reclassification.

### 6.3 Update Known Unknowns (1.1–1.6)

- Unknown 1.1 (canary regression risk): VERIFIED — broader gate regresses 2 of 11 canaries plus launch.
- Unknown 1.2 (sameas-decomposed): VERIFIED — confirmed Pattern C variant on cesam2; fix requires sameas-block-guard preservation in consolidated builder.
- Unknown 1.3 (#1334 interaction): VERIFIED — orthogonal in code path, but otpop is subsumed by #1334 not by Pattern C.
- Unknown 1.4 (mathematical equivalence): VERIFIED on camcge/cesam2 — per-offset enumeration is mathematically equivalent to the sum form. But the consolidated builder currently produces a STRUCTURALLY INCOMPLETE collapsed form, not the equivalent sum form.
- Unknown 1.5 (canaries with imat-shaped patterns): VERIFIED — quocge, splcge are CGE-family canaries with at-risk shapes. quocge regresses under the prototype.
- Unknown 1.6 (PROCEED/REPLAN signal): VERIFIED — methodology produces a clean signal: PROCEED on camcge/cesam2 (Pattern C confirmed), REPLAN overall (architectural blocker on builder + 2 of 4 targets disproved).

---

## 7. Sprint 25 retrospective PR16 codification — outcome

**PR16 (run hypothesis-validation pre-Sprint-0 for multi-issue workstreams sharing a single hypothesized root cause)** is validated as a high-value process recommendation. Without this prep activity, Sprint 26 Day 1 would have started with "remove the `$cond` filter" and discovered mid-sprint:

- 2 of 4 target models don't actually have the bug shape (fawley, otpop) — wasted ~6–10h of investigation.
- The simple gate widening regresses 2 canaries plus launch — wasted ~4–6h on the rollback / bisect.
- Total wasted Sprint 26 mid-sprint cost without PR16: ~10–16h, plus a likely Day 5 pivot replicating Sprint 25's mid-sprint replan event.

**With PR16 applied:** ~6h of prep (Task 3) replaces ~10–16h of mid-sprint waste. Net savings: ~4–10h. **PR16 pays for itself.**

The methodology recommendation generalizes: any sprint with 3+ issues claimed to share a single hypothesized root cause should run PR16-style validation pre-Day-0. Sprint 26's own PR16 Task 3 (this document) is the first production application.

---

## 8. Files referenced

- `/tmp/sprint26-day0-validation/<model>_mcp.gms` — current main emit (advisory)
- `/tmp/sprint26-day0-validation/<model>_trace.stderr` — `SPRINT25_DAY2_DEBUG=1` trace (advisory)
- `/tmp/sprint26-day0-validation/<model>_formal_kkt.md` — hand-derived formal KKT (advisory)
- `/tmp/sprint26-day0-validation/<model>.lst` — GAMS compile errors (advisory)
- `/tmp/sprint26-baseline-canaries/` — baseline canary outputs (advisory)
- `/tmp/sprint26-prototype-canaries/` — prototype-patch canary outputs + gate firings (advisory)
- `src/kkt/stationarity.py:4318–4346` — current Pattern C gate (no-op since #1351)
- `docs/planning/EPIC_4/SPRINT_25/SPRINT_LOG.md` Day 11 — #1351 rollback
- `docs/planning/EPIC_4/SPRINT_25/DAY5_PATTERN_A_INVESTIGATION.md` — methodology reference
- `docs/issues/ISSUE_1354..1357_*.md` — original issue docs (reclassification proposed for #1356, #1357)

## 9. Acceptance criteria (per PREP_PLAN.md Task 3)

- [x] Day 5 methodology applied to 3 target models (camcge, cesam2, fawley)
- [x] Hand-derived formal KKT documented for at least 1 target stationarity equation per model
- [x] Byte-comparison vs emitted form documented per model
- [x] Prototype patch tested on Tier 0/1 canaries (11 canaries + launch + 4 targets)
- [x] Recommendation written: **REPLAN with two-phase scope, target list 4 → 2** with rationale
- [x] Unknowns 1.1, 1.2, 1.3, 1.4, 1.5, 1.6 verified and updated in KNOWN_UNKNOWNS.md

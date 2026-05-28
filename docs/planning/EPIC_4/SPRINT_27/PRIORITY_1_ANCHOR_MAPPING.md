# Sprint 27 Priority 1 (#1398) Anchor-Model Mapping

**Status:** ✅ COMPLETE (Day 0 prep)
**Date:** 2026-05-28
**Owner:** Prep Task 4
**Inputs:** Sprint 27 Day 0 `data/gamslib/mcp/*_mcp.gms` regenerated artifacts (`e0be4fb1`-baselined; no `src/` changes since); Sprint 27 PROJECT_PLAN.md §"Priority 1: Phase A Gate Predicate Tightening (#1398)"; Sprint 27 KNOWN_UNKNOWNS.md §Unknown 1.1 verification table.

---

## 1. Purpose

This document is the Sprint 27 Day 0 anchor-model mapping for the **#1398 Phase A gate-predicate tightening** workstream (Priority 1). It records:

- The Sprint 27 Day 0 bucket for each of the 15 #1398-affected models (cross-referenced against Task 3 baseline).
- For each of the 8 anchor models, the distinguishing **emit pattern** observed in the regenerated `data/gamslib/mcp/<model>_mcp.gms` artifact (which stationarity equation, cross-term structure, alias-conditional shape).
- For each non-anchor model, the **presumed-matching anchor** with justification.
- An **Open Questions** subsection for any ambiguous mapping, anchor-pair collapse risk, or scope-impact note that escalates to Sprint 27 Day 1/2 hand-derived KKT verification.

The mapping is the input to Sprint 27 Day 1/2 **Phase 0 acceptance gate** (per Sprint 26 retrospective recommendation PR20 codified in CONTRIBUTING.md §"Phase 0 Acceptance Gates"): hand-derive expected KKT shape on each anchor before committing any change to `src/kkt/stationarity.py`. Per-term grep-based pattern-match verification (not byte-diff) confirms the regenerated emit matches the hand-derived form.

This document is **inspection-based**, not formal: it documents the structural shapes observed in the emit artifacts. Formal hand-derived KKT verification is the Sprint 27 Day 1/2 work that uses this mapping as input. Ambiguous shape claims (anchor pair collapse risk; 9th-shape candidate among non-anchors) are recorded in §6 as Day 1/2 escalations.

---

## 2. Cross-Reference: 15 #1398-Affected Models in Sprint 27 Day 0 Baseline

Per Task 3 (BASELINE_METRICS.md §6.2 + Unknown 1.1 verification table), all 15 #1398-affected models are confirmed at non-compare_match buckets in the Sprint 27 Day 0 baseline:

| # | Model | Day 0 Bucket | Anchor or Non-Anchor? | Notes |
|---|---|---|---|---|
| 1 | `qdemo7` | path_syntax_error | **Anchor** | `stat_xcrop(c)` — Phase A overreach primary target; +1 firm Solve / +1 firm Match recovery anchor |
| 2 | `egypt` | path_syntax_error | Non-anchor → **qdemo7** | `stat_xcrop(r,c)` (2-region extension of qdemo7 shape) |
| 3 | `ferts` | path_syntax_error | **Anchor** | `stat_z(p,i)` — multi-bound-index sum with `ppos(i,p)` 2-set alias-conditional |
| 4 | `shale` | path_syntax_error | Non-anchor → **ferts** | `stat_z(p,tf)` (same multi-bound-index sum family) |
| 5 | `sambal` | compare_mismatch | **Anchor** | `stat_x(i,j)` — `__kkt1` synthetic alias + `xb(i,i__kkt1)` parameter-as-condition + `nu_cbal(i)` cbal-derivative shape |
| 6 | `qsambal` | compare_mismatch | Non-anchor → **sambal** | `stat_x(i,j)` (structurally identical, quadratic variant) |
| 7 | `harker` | compare_mismatch | Non-anchor → **sroute** (tentative) | `stat_t(n,np)` `arc(n,np)` parameter-as-condition network shape |
| 8 | `tfordy` | path_solve_license | Non-anchor → **sambal** (tentative) | `stat_x(c,t)` Pattern C with `cf(c)` parameter-as-condition + `lam_bal(c,t)` cbal-style multiplier |
| 9 | `dinam` | path_syntax_error | **Anchor** | `stat_ka(te)` row-multiplier-collapse + claimed 2nd shape via `comp_mb(i,t)` differentiate-vs-current-eq-index |
| 10 | `ganges` | translate_timeout (Day 0; was path_syntax_error at Sprint 26 Day 13 final) | **Anchor** | `stat_pls(r)` — 4 inner Pattern C alias-sums with `ri(i,r)` 2-set membership + outer set-guard `$(sum(i, 1$(ri(r,i))))` |
| 11 | `gangesx` | path_syntax_error | Non-anchor → **ganges** | `stat_pls(r)` (eXtended variant — same 4-sum + `ri(i,r)` family) |
| 12 | `fawley` | path_syntax_error | (Folded into #1356 — see §6 Open Question 1) | `stat_bq(c,cf)` Pattern C-like shape; per PROJECT_PLAN.md L1032 "already in #1356 scope" |
| 13 | `srpchase` | translate_timeout (Day 0; was path_syntax_error at Sprint 26 Day 13 final) | Non-anchor → **turkpow** (tentative) | `stat_x(n)` / `stat_y(n)` with `ancestor(srn,srn)` self-loop indicator (mirrors turkpow's `vs(t__,t__)` self-loop family) |
| 14 | `sroute` | path_solve_license | **Anchor** | `stat_x(i,ip,ipp)` — `darc(ip,ipp)` network arc parameter + nested `(not sameas(i,ipp))` negation guard |
| 15 | `turkpow` | path_syntax_error | **Anchor** | `stat_zt(m,v,b,t)` — `vs(t__,t__)` self-loop alias + `bs(bp,b)` separate-var conditional + massive `sameas`-Cartesian inner-sum-of-bs-conditioned-products |

**Cross-reference summary:** 15/15 #1398-affected models present at non-compare_match buckets in Sprint 27 Day 0 baseline. **No self-recoveries.** No scope shrinkage. Priority 1 scope CONFIRMED at 15 models. (`ganges` + `srpchase` are at `translate_timeout` due to Sprint 27 Day 0 machine-variance churn at the 600s translate boundary — both were `path_syntax_error` at Sprint 26 Day 13 final and remain in #1398 scope per Unknown 1.1 verification; they'll return to `path_syntax_error` on a faster runner.)

**Anchor count from the 15:** 7 (qdemo7, ferts, sambal, dinam, ganges, sroute, turkpow). The 8th anchor is `launch` — NOT in the 15-affected cohort; serves as the **byte-stability anchor** preserving the Sprint 26 Day 1 PR #1379 launch fix output.

**Non-anchor mapping cohort:** 7 (egypt, shale, qsambal, harker, tfordy, gangesx, srpchase). `fawley` is the 15th #1398-affected model but is folded into Priority 5 (#1356); see §6 Open Question 1.

---

## 3. Anchor: launch — Byte-Stability Anchor

**Bucket at Day 0:** compare_mismatch (NOT in the 15-affected cohort — launch is the Sprint 26 PR #1379 Phase A fix target whose emit shape must be preserved by the Sprint 27 #1398 tightening).

**Distinguishing emit pattern:** Pattern C consolidated zero-offset via `s ↔ ss` alias swap with **`ge(s, ss)` order-comparison alias-indicator**. Canonical PR #1379 target shape.

**Per-term emit (from `data/gamslib/mcp/launch_mcp.gms` L276 + L279):**

```
stat_iweight(s).. ... + sum(ss, ((-1) * 1$(ge(s,ss))) * nu_dweight(ss)) + ... =E= 0;
stat_pweight(s).. ... + sum(ss, ((-1) * 1$(ge(s,ss))) * nu_dweight(ss)) + ... =E= 0;
```

**Distinguishing features:**

- **Order-relation alias-indicator** `1$(ge(s,ss))` — distinct from the parameter-set-membership indicators used by other anchors (`sc(c,s)`, `xb(i,j)`, `ri(i,r)`, etc.). Sprint 27 tightening must continue to accept `ge(s,ss)` order-relation as a valid Pattern C trigger.
- **Eq-index `s` paired with synthetic-alias `ss`** declared via `Alias(s, s__)` / `Alias(s, ss)` GAMS preamble.
- **Multiplier `nu_dweight(ss)` uses the bound alias index** `ss`, not the eq index `s` — this is the correct semantic per the Lagrangian `-sum_{k≤s} nu_dweight(k)` of the dweight constraint.

**Phase 0 verification approach (per CONTRIBUTING.md §"Phase 0 Acceptance Gates"):**

After Sprint 27 tightening lands, regenerate `launch_mcp.gms` and verify per-term:

```bash
grep -n 'sum(ss, ((-1) \* 1\$(ge(s,ss))) \* nu_dweight(ss))' data/gamslib/mcp/launch_mcp.gms
# Expect: 2 matches (stat_iweight + stat_pweight)
```

**Byte-stability:** Sprint 27 #1398 tightening must preserve launch's regenerated `.gms` byte-identical to Sprint 26 Day 13 final (per PR12 determinism guard). Any byte-level change is a regression. Unknown 4.2 (will Priority 4 #1378 break launch byte-stability?) feeds into this anchor.

---

## 4. Anchors (7 from the 15-affected cohort)

### 4.1 Anchor: qdemo7 — `stat_xcrop(c)` Pattern C with `sc(c,s)` 2-set membership

**Bucket at Day 0:** path_syntax_error.

**Distinguishing emit pattern (from `qdemo7_mcp.gms` L240):**

```
stat_xcrop(c).. ... + sum(s, 1$(sc(c,s)) * lam_plow(c)) + ... =E= 0;
```

**Distinguishing features:**

- **Pattern C alias-sum** with parameter-set-membership indicator. Source constraint (per `data/gamslib/raw/qdemo7.gms` L177 + `qdemo7_mcp.gms` L248): `comp_plow(s).. ((-1) * (sum(c$(sc(s,c)), xcrop(c)) − ...)) =G= 0;` — the source uses **`sc(s,c)`** (s first, c second) per the parameter declaration `sc(s,c) /summer.cotton, ..., winter.onions/` (L24).
- **Suspected bug (2 compounding errors):** Current emit (`stat_xcrop(c)` L240) is `sum(s, 1$(sc(c,s)) * lam_plow(c))` — has BOTH (a) the indicator's argument order swapped (`sc(c,s)` instead of `sc(s,c)`) AND (b) the multiplier using the eq-domain index `c` instead of the sum bound index `s`. The hand-derived KKT for `stat_xcrop(c)` of the Lagrangian L = … + sum(s, lam_plow(s) * (sum(c$(sc(s,c)), xcrop(c)) − plow_cap(s))) gives ∂L/∂xcrop(c) = sum(s$(sc(s,c)), lam_plow(s)) — with `sc(s,c)` argument order matching the source constraint AND with `lam_plow(s)` bound-index multiplier. The Phase A `_find_pattern_c_alias_sum` gate over-consolidated, propagated `c` instead of `s` into the multiplier, AND swapped the parameter-indicator argument order.
- **Path failure mechanism:** GAMS PATH compile-error surfaces because `lam_plow(c)` introduces an out-of-scope index reference at the consolidated sum's body (the `lam_plow` symbol's declared domain mismatches the sum-body indexer used).

**Phase 0 verification approach:**

After Sprint 27 tightening lands, regenerate `qdemo7_mcp.gms` and verify per-term:

```bash
# Expected post-fix emit (BOTH bugs fixed — sc(s,c) source-matching arg order
# AND lam_plow(s) bound-index multiplier):
grep -n 'sum(s, 1\$(sc(s,c)) \* lam_plow(s))' data/gamslib/mcp/qdemo7_mcp.gms
# Expect: 1 match (stat_xcrop)

# Regression checks — neither buggy shape must appear:
grep -n 'sum(s, 1\$(sc(c,s)) \* lam_plow(c))' data/gamslib/mcp/qdemo7_mcp.gms
# Expect: 0 matches (current Sprint 27 Day 0 buggy shape — arg order swapped + eq-index leak)
grep -n 'sum(s, 1\$(sc(c,s)) \* lam_plow(s))' data/gamslib/mcp/qdemo7_mcp.gms
# Expect: 0 matches (partial-fix shape — multiplier corrected but indicator still wrong-order)
grep -n 'sum(s, 1\$(sc(s,c)) \* lam_plow(c))' data/gamslib/mcp/qdemo7_mcp.gms
# Expect: 0 matches (partial-fix shape — indicator corrected but multiplier still leaks)
```

**Recovery impact:** qdemo7 is the **+1 firm Solve / +1 firm Match** recovery anchor for Sprint 27 Priority 1 (compare_match at Sprint 26 Day 0 → path_syntax_error post-PR #1379 regression). Fix verified by qdemo7 returning to compare_match.

### 4.2 Anchor: ferts — `stat_z(p,i)` multi-bound-index Pattern C with `ppos(i,p)` 2-set membership

**Bucket at Day 0:** path_syntax_error.

**Distinguishing emit pattern (from `ferts_mcp.gms` L367):**

```
stat_z(p,i).. (sum(c, ((-1) * (a(c,i) * 1$(ppos(i,p)))) * lam_mb(c,p))
             + sum(m, (b(m,i) * 1$(ppos(i,p)) * lam_cc(m,p))$(mpos(m,p))))$(ppos(p,i)) =E= 0;
```

**Distinguishing features:**

- **Multi-bound-index sums:** `sum(c, ...)` and `sum(m, ...)` over bound indices that are NOT the eq-domain indices (`p,i`).
- **2-index alias-conditional `ppos(i,p)`** — parameter set-membership with order-significant arguments (`i` is eq index, `p` is eq index; conditional asserts the process `p` is at position `i`).
- **Multiplier `lam_mb(c,p)`** uses **bound index `c` + eq index `p`** — distinct from qdemo7's single-index multiplier collapse.
- **Outer eq-level guard** `$(ppos(p,i))` — conditional gates the entire equation on the same parameter-set-membership.

**Phase 0 verification approach:**

```bash
grep -n 'sum(c, ((-1) \* (a(c,i) \* 1\$(ppos(i,p)))) \* lam_mb(c,p))' data/gamslib/mcp/ferts_mcp.gms
# Expect: 1 match (stat_z)
grep -n 'sum(m, (b(m,i) \* 1\$(ppos(i,p)) \* lam_cc(m,p))\$(mpos(m,p)))' data/gamslib/mcp/ferts_mcp.gms
# Expect: 1 match (stat_z)
```

**Recovery impact:** ferts returning to its Sprint 26 Day 0 bucket (`path_solve_license` — license-gated; not a structural fix) confirms the Phase A gate-overreach revert. ferts is the **multi-bound-index sum shape** anchor for the Sprint 27 tightening; the gate predicate must distinguish single-bound-index from multi-bound-index Pattern C contexts.

### 4.3 Anchor: sambal — `stat_x(i,j)` `__kkt1` synthetic alias + cbal-derivative shape

**Bucket at Day 0:** compare_mismatch.

**Distinguishing emit pattern (from `sambal_mcp.gms` L90):**

```
stat_x(i,j).. (... + sum(i__kkt1, ((-1) * 1$(xb(i,i__kkt1))) * nu_cbal(i)))$(xw(i,j)) =E= 0;
```

**Distinguishing features:**

- **`__kkt1` synthetic alias index** — the AD pass introduces a fresh alias `i__kkt1` of the original index `i` to avoid GAMS Error 125 ("set under control already") inside the consolidated sum.
- **Parameter-as-condition `1$(xb(i,i__kkt1))`** — `xb` is a parameter (not a set), used as a 0/1 conditional gate. Distinct from set-membership indicators (`sc(c,s)`, `ppos(i,p)`, `ri(i,r)`) where the conditional is set-membership.
- **Multiplier `nu_cbal(i)`** uses the **eq-domain index `i`**. Hand-derived KKT for sambal: the cbal constraint is ∑_j x(i,j) = c_total(i), so ∂L/∂x(i,j) = −nu_cbal(i) — eq-domain-index multiplier is correct here, not a bug. This anchor verifies that the gate predicate must NOT propagate bound-index into multipliers when the eq-domain index is semantically correct.

**Phase 0 verification approach:**

```bash
grep -n 'sum(i__kkt1, ((-1) \* 1\$(xb(i,i__kkt1))) \* nu_cbal(i))' data/gamslib/mcp/sambal_mcp.gms
# Expect: 1 match (stat_x)
```

**Recovery impact:** sambal stays at compare_mismatch (Sprint 26 Day 0 baseline bucket — pre-existing solver-numerical issue, not a Phase A regression). The Sprint 27 fix is verified by sambal's regenerated emit being byte-identical to a hand-derived reference, NOT by sambal becoming compare_match (which depends on solver behavior).

### 4.4 Anchor: ganges — `stat_pls(r)` 4 inner Pattern C alias-sums with `ri(i,r)` + outer set-membership guard

**Bucket at Day 0:** translate_timeout (machine-variance churn — was path_syntax_error at Sprint 26 Day 13 final; remains in #1398 scope per Unknown 1.1).

**Distinguishing emit pattern (from `ganges_mcp.gms` L1011):**

```
stat_pls(r).. (sum(i, ((-1) * (depl(r) * ls(r) * 1$(ri(i,r)))) * nu_qdep(r))
             + sum(i, ((-1) * (ls(r) * 1$(ri(i,r)))) * nu_values(r))
             + sum(i, (... * 1$(ri(i,r)) ...) * nu_firsts(r))$((not si(r)))
             + sum(i, ((-1) * ((1 - tw(r)) * ls(r) * 1$(ri(i,r)))) * nu_yself(r))
             - piL_pls(r))$(sum(i, 1$(ri(r,i)))) =E= 0;
```

**Distinguishing features:**

- **4 separate inner Pattern C alias-sums** with the same `ri(i,r)` 2-set membership pattern but distinct outer multipliers (`nu_qdep`, `nu_values`, `nu_firsts`, `nu_yself`).
- **Outer eq-level guard `$(sum(i, 1$(ri(r,i))))`** — set-membership existential quantification: equation gated only if at least one `i` satisfies `ri(r,i)`. Distinct from ferts's deterministic `$(ppos(p,i))`.
- **Multiplier `nu_<eq>(r)` uses eq-domain index `r`** for all 4 inner sums — semantically correct (each `nu_<eq>` constraint is indexed by `r`).
- **Nested CES-derivative shape** in the `nu_firsts` term (with `sigmas(r)` exponent + `sqr(...)` divisor) — Pattern C alias-sum interacts with non-trivial nonlinear expressions, distinct from sambal's simpler linear cbal-derivative.

**Phase 0 verification approach:**

```bash
# 4 inner alias-sums all present in stat_pls (use grep -o for occurrence count,
# not grep -c which counts lines — stat_pls is a single long line):
grep -o '1\$(ri(i,r))' data/gamslib/mcp/ganges_mcp.gms | wc -l
# Expect: ≥ 4 occurrences total in the file (4 in stat_pls + any in other
# eqs that share the ri(i,r) pattern). At Sprint 27 Day 0 baseline: 7
# occurrences across 2 lines (4 in stat_pls L1011 + 3 in stat_ks-family L1036).

# Outer set-membership guard preserved:
grep -n 'piL_pls(r))\$(sum(i, 1\$(ri(r,i))))' data/gamslib/mcp/ganges_mcp.gms
# Expect: 1 match (stat_pls outer wrapping)
```

**Recovery impact:** ganges returning to `path_syntax_error` (a faster runner; or persisting at `translate_timeout` if the runner remains slow) plus the regenerated emit matching the 4-inner-sum + outer-guard shape confirms the fix. ganges is the **repeated-Pattern-C-with-distinct-outer-multipliers + set-membership-existential** anchor.

### 4.5 Anchor: sroute — `stat_x(i,ip,ipp)` `darc(ip,ipp)` network arc + `(not sameas(i,ipp))` negation guard

**Bucket at Day 0:** path_solve_license.

**Distinguishing emit pattern (from `sroute_mcp.gms` L94):**

```
stat_x(i,ip,ipp).. darc(i,ip) + (1$(darc(ip,ipp)) * lam_nb(i,ip))$((not sameas(i, ipp))) - piL_x(i,ip,ipp) =E= 0;
```

**Distinguishing features:**

- **3-index eq domain `(i,ip,ipp)`** — distinct from the 1- or 2-index eqs of qdemo7/ferts/sambal/ganges.
- **Parameter-as-condition `1$(darc(ip,ipp))`** — `darc` is the network-arc indicator parameter, gated on the 2nd and 3rd eq indices (not the 1st).
- **Multiplier `lam_nb(i,ip)`** uses **2 eq-domain indices** (`i`, `ip`), excluding `ipp` — the multiplier-index projection is fewer indices than the eq.
- **Outer `(not sameas(i, ipp))` negation guard** — distinguishes self-loop case (`i == ipp` excluded). Combined with the inner `1$(darc(ip,ipp))`, encodes a sparse network-flow stationarity.
- **NO sum-over-bound-index** — sroute's distinguishing feature is that the Pattern C shape appears WITHOUT a wrapping `sum(_, ...)`. The tightening must handle this "unwrapped" Pattern C case correctly.

**Phase 0 verification approach:**

```bash
grep -n '(1\$(darc(ip,ipp)) \* lam_nb(i,ip))\$((not sameas(i, ipp)))' data/gamslib/mcp/sroute_mcp.gms
# Expect: 1 match (stat_x)
```

**Recovery impact:** sroute stays at `path_solve_license` (license-gated; not a structural fix). The Sprint 27 fix is verified by the regenerated emit matching the no-sum + parameter-arc + negation-guard shape, NOT by sroute solving.

### 4.6 Anchor: turkpow — `stat_zt(m,v,b,t)` `vs(t__,t__)` self-loop + `bs(bp,b)` separate-var conditional + sameas-Cartesian

**Bucket at Day 0:** path_syntax_error.

**Distinguishing emit pattern (from `turkpow_mcp.gms` L213):**

```
stat_zt(m,v,b,t).. (
  sum(t__kkt1, (((-1) * (opcostt(m,v,t__kkt1) * dur(b) * 1$(vs(t__kkt1,t__kkt1)))) * nu_ao(v))$(t(v)))
+ sum(t__kkt2, (((-1) * (1$(vs(t__kkt2,t__kkt2)) * 1$(bs(bp,b)))) * lam_db(b,v))$(t(v)))
+ ((lam_cct(m,v,t)$(mt(m) and t(t)))$(vs(t,v)))$(<MASSIVE sameas-Cartesian enumeration over m × v × b × t tuples>)
- piL_zt(m,v,b,t)
)$(<more conditions>) =E= 0;
```

**Distinguishing features:**

- **`__kkt1` and `__kkt2` synthetic aliases** for the bound index `t` (sambal has one such; turkpow has two distinct ones in the same equation).
- **Self-loop alias indicator `1$(vs(t__kkt1, t__kkt1))`** — `vs` is the vintage-set-relation parameter; the indicator gates only on diagonal entries (`t__ == t__`). This is the "inner-sum-of-bs-conditioned-products" shape called out in PROJECT_PLAN.md L1033.
- **Separate-variable 2-index condition `1$(bs(bp,b))`** — `bs` separately indexed by `bp` (an external/closure index) and `b` (eq index), distinct from the self-loop pattern.
- **Massive `sameas`-Cartesian enumeration** — the `lam_cct(m,v,t)` contribution is wrapped in a giant `or`-disjunction of `sameas(m, 'xxx') and sameas(v, 'yyyy') and sameas(b, 'zzz') and sameas(t, 'wwww')` tuples (Cartesian of model classes × vintages × buckets × time periods). Distinct from any other anchor's pattern.
- **4-index eq domain `(m,v,b,t)`** — widest eq-domain in the cohort.

**Phase 0 verification approach:**

```bash
# Both __kkt aliases present (use grep -o for occurrence count since
# turkpow's stat_zt is a single long line):
grep -oE '\bt__kkt[12]\b' data/gamslib/mcp/turkpow_mcp.gms | sort -u
# Expect: 2 unique aliases (t__kkt1, t__kkt2)
grep -oE '\bt__kkt[12]\b' data/gamslib/mcp/turkpow_mcp.gms | wc -l
# Expect: ≥ 4 total occurrences (each alias appears at least twice — declaration + use in stat_zt)

# Self-loop indicators preserved (each on the same single stat_zt line):
grep -oE '1\$\(vs\(t__kkt[12],t__kkt[12]\)\)' data/gamslib/mcp/turkpow_mcp.gms | wc -l
# Expect: ≥ 2 total occurrences (one per __kkt alias)

# Separate-var conditional present:
grep -o '1\$(bs(bp,b))' data/gamslib/mcp/turkpow_mcp.gms | wc -l
# Expect: ≥ 1 occurrence
```

**Recovery impact:** turkpow returning to `path_syntax_error` or earlier (Sprint 26 Day 0 was `translate_timeout`; runner-dependent) plus the regenerated emit matching all 3 sub-shapes (self-loop, separate-var conditional, sameas-Cartesian) confirms the fix.

### 4.7 Anchor: dinam — `stat_ka(te)` row-multiplier-collapse + `comp_mb(i,t)` differentiate-vs-current-eq-index (CLAIMED 2 SHAPES)

**Bucket at Day 0:** path_syntax_error.

**Distinguishing emit patterns:**

**Shape A — `stat_ka(te)` row-multiplier-collapse** (from `dinam_mcp.gms` L466):

```
stat_ka(te).. sum((s,t), (((-1) * (alr(te) * interval * 1$(ts2(te,t)))$(sun(s))) * nu_drql(s,te))$(t(te)))
            + sum(s, ((... * 1$(ts2(te,te)))$(sun(s)) ...) * nu_drql(te,s))$(t(s)))
            + sum(tep, sum(s, ((-1) * (interval * alr(te+7) * 1$(ts2(te+7,tep)))$(sun(s))) * nu_trql(s,te))$(ord(te) > last))
            + ...
            + sum((i,t), (bk(i,"agri",t) * lam_mb(i,t))$(t(t)))
            - piL_ka(te) =E= 0;
```

Distinguishing features (Shape A):
- **2-index alias-conditional `1$(ts2(te,t))`** and **self-loop `1$(ts2(te,te))`** in the SAME equation (rare — only turkpow also has self-loop within a single eq, but turkpow's are bound-index self-loops via `__kkt` aliases; dinam's `1$(ts2(te,te))` uses the eq-domain index `te` for BOTH sides).
- **Multiplier `nu_drql(s,te)` mixes bound index `s` + eq index `te`** — distinct from ferts (bound + eq) because dinam's bound `s` is non-time, while ferts's is `c`.
- **Inner sum bound index `tep` with offset `te+7`** — IndexOffset(eq_index) appears INSIDE the Pattern C alias-conditional. Sprint 27 Priority 6 #1224 territory (`IndexOffset(ParamRef)` — but here the offset is on a set index, not a param ref; the IndexOffset variant is set-arithmetic).
- **`lam_mb(i,t)` row-multiplier-collapse** at the bottom — both `i` and `t` are BOUND indices of the sum, NOT eq indices. This is the **row-multiplier-collapse** feature called out in PROJECT_PLAN.md L1033. The hand-derived KKT for dinam's stat_ka(te) of the comp_mb(i,t) constraint contribution gives ∂L/∂ka(te) = sum((i,t)$(...), bk(i,"agri",t) * lam_mb(i,t)) — the multiplier-index collapses to the bound-index set, NOT propagating the eq index `te` into `lam_mb`. The Phase A gate predicate must distinguish row-multiplier-collapse from index-leak.

**Shape B — `comp_mb(i,t)` differentiate-vs-current-eq-index** (from `dinam_mcp.gms` L483):

```
comp_mb(i,t).. ((-1) * (sum(j, a(i,j,t) * x(j,t) + b(i,j,t) * v(j,t))
                      + bk(i,"agri",t) * ka(t) + apc(i,t) * con(t) + apz(i,t) * zt(t)
                      + es(i) * sum(tep$(ts(t,tep)), zmi(t,tep) * em(tep))
                      + e(i,t)$(im(i)) + csm(i) * ea(t)
                      + sum(s, ssr(i,s) * ul(s,t)))) =G= 0;
```

This is the **constraint** (=G= 0), not a stationarity equation. The "differentiate-vs-current-eq-index" shape claim is that when stat_ka(te) above differentiates this constraint, the term `bk(i,"agri",t) * ka(t)` produces `bk(i,"agri",t) * 1$(sameas(t,te)) * lam_mb(i,t)` in the naive emit — and the Phase A gate must consolidate the `1$(sameas(t,te))` away when `t == te` is the only valid case (collapsing to `bk(i,"agri",te) * lam_mb(i,te)` with bound-index `i` only).

**Open question (escalates to Day 1/2 — see §6 Open Question 4):** Are Shape A and Shape B truly distinct gate-predicate inputs (justifying separate hand-derived KKT verification), or is Shape B just the "input pre-collapse" form of Shape A's "output post-collapse" form (i.e., 1 logical shape with 2 positional variations)?

**Phase 0 verification approach (Shape A):**

```bash
# Row-multiplier-collapse: lam_mb with BOTH bound indices, no eq index leakage:
grep -n 'sum((i,t), (bk(i,"agri",t) \* lam_mb(i,t))\$(t(t)))' data/gamslib/mcp/dinam_mcp.gms
# Expect: 1 match (stat_ka)

# 2-index alias-conditional with eq-index self-loop:
grep -n '1\$(ts2(te,te))' data/gamslib/mcp/dinam_mcp.gms
# Expect: ≥ 1 match
```

---

## 5. Non-Anchor Mappings (7 Models)

Each non-anchor model is assigned to a presumed-matching anchor based on the structural shape of its `_mcp.gms` stationarity equations. Verification is provisional pending Sprint 27 Day 1/2 hand-derived KKT — ambiguous mappings are flagged in §6.

- **egypt → qdemo7** — `stat_xcrop(r,c)` (from `egypt_mcp.gms` L290) is the explicit 2-region (`r`) extension of qdemo7's `stat_xcrop(c)`. Same `yld(c+k,c,r) * lam_comb(c+k)` Pattern C indexing with crop-rotation offsets (`c+22`, `c+8`, etc.); same `lam_landbal` + `lam_comb` multiplier family. Confidence: **high**. Sprint 27 fix on the qdemo7 shape should mechanically apply to egypt.
- **shale → ferts** — `stat_z(p,tf)` (from `shale_mcp.gms` L357) shares the multi-bound-index sum structure: `sum((crs,t), (a(crs,p) * nu_msu(crs,t))$(...))` and `sum((cf,t), ...$(cf(cf) and t(t)))`. Multiplier-index projection across bound `+ eq` mirrors ferts's `lam_mb(c,p)` shape. shale has additional sameas-Cartesian inner enumeration (similar to turkpow's pattern) but the dominant Pattern C shape is the multi-bound-index sum — ferts-family. Confidence: **medium-high**. The sameas-Cartesian sub-shape is a candidate 9th-shape claim — see §6 Open Question 2.
- **qsambal → sambal** — `stat_x(i,j)` (from `qsambal_mcp.gms` L90) is structurally identical to sambal's `stat_x(i,j)`: same `__kkt1` synthetic alias, same `1$(xb(i,i__kkt1))` parameter-as-condition, same `nu_cbal(i)` cbal-derivative. qsambal is the quadratic-objective variant of sambal; the structural KKT shape is unchanged because the nonlinearity is in the objective, not the constraints. Confidence: **high**. Sprint 27 fix on sambal should mechanically apply to qsambal.
- **harker → sroute** (tentative) — `stat_t(n,np)` (from `harker_mcp.gms` L126) uses `1$(arc(n,np))` parameter-as-condition for network arcs (mirrors sroute's `darc(ip,ipp)` family). Additional features: `sum(l__$(sameas(l__, n)), ...)` linear-path enumeration in stat_d / stat_s. The dominant network-arc shape maps to sroute; the sameas-aliased inner-sum is a sub-shape that may be a 9th-shape candidate. Confidence: **medium**. See §6 Open Question 3.
- **tfordy → sambal** (tentative) — `stat_x(c,t)` (from `tfordy_mcp.gms` L221) has `(1$(cf(c)) * lam_bal(c,t))$(t(t))` Pattern C with `cf(c)` parameter-as-condition + `lam_bal(c,t)` 2-index multiplier. Closer to sambal's cbal-style multiplier family than sroute's network-flow family. Confidence: **medium**. The Pattern C shape is simpler than sambal's `__kkt1` synthetic alias structure — may or may not be a sub-shape. See §6 Open Question 3.
- **gangesx → ganges** — `stat_pls(r)` (from `gangesx_mcp.gms` L1011) has 4 inner Pattern C alias-sums with `1$(ri(i,r))` 2-set membership identical to ganges. gangesx is the eXtended variant of ganges (same set/parameter structure, slightly different objective). Confidence: **high**. Sprint 27 fix on ganges should mechanically apply to gangesx.
- **srpchase → turkpow** (tentative) — `stat_x(n)` and `stat_y(n)` (from `srpchase_mcp.gms` L131-132) use `1$(ancestor(srn,srn))` self-loop indicator (mirrors turkpow's `vs(t__,t__)` self-loop family) + Pattern C-style nested guards `($(srn(srn)))$((not leaf(srn)))`. The 4-index eq-domain of turkpow vs srpchase's 1-index eq-domain (`stat_x(n)`) is a structural difference — srpchase's shape may be a degenerate subset of turkpow's. Confidence: **low-medium**. See §6 Open Question 3.

---

## 6. Open Questions (Escalate to Sprint 27 Day 1/2 Hand-Derived KKT)

### Open Question 1: `fawley`'s #1398 surface vs #1356 fix scope

`fawley` is in the 15 #1398-affected models per Sprint 27 PROJECT_PLAN.md L1032, but L1032 explicitly notes "fawley (already in #1356 scope)". `fawley_mcp.gms` L244 shows `stat_bq(c,cf)` with Pattern C alias-sum `sum(cfq__, (((-1) * 1$(bposs(cfq__,c))) * nu_mbal(c))$(sameas(cfq__, cf)))` — structurally closest to **sambal**'s `__kkt1` + parameter-as-condition + eq-index-multiplier shape.

**Question:** Does the Sprint 27 #1356 comp_up subset/superset fix (Priority 5) subsume fawley's #1398 surface, or does fawley need a separate Phase 0 verification under the qdemo7/sambal/dinam anchors?

**Action:** Sprint 27 Day 1 verify by inspecting fawley's regenerated emit AFTER the #1356 fix lands. If the Pattern C alias-sum shape changes (no longer matches sambal-family), confirm #1356 subsumes the #1398 surface. Else, add a fawley Phase 0 sub-section under sambal.

### Open Question 2: shale's sameas-Cartesian sub-shape — candidate 9th shape?

shale's `stat_z(p,tf)` contains a sameas-Cartesian inner enumeration (`lam_mmr3$((sameas(p, 'dispose-u') or ...))`), structurally similar to turkpow's `lam_cct(m,v,t)$(<sameas-Cartesian>)` shape but smaller. shale is provisionally mapped to ferts based on the multi-bound-index sum dominant feature, but the sameas-Cartesian sub-shape may require turkpow-style verification.

**Question:** Does the Sprint 27 tightening's handling of turkpow's sameas-Cartesian shape generalize to shale's smaller sameas-Cartesian (i.e., 1 shape, 2 scales), or are these distinct gate-predicate inputs?

**Action:** Sprint 27 Day 2 verify by hand-deriving KKT for one shale sameas-Cartesian instance and comparing the gate predicate against the turkpow case. If predicate inputs differ, add shale Phase 0 sub-section under turkpow.

### Open Question 3: Non-anchor mapping confidence (harker, tfordy, srpchase)

3 of the 7 non-anchor mappings have medium-to-low confidence (harker → sroute, tfordy → sambal, srpchase → turkpow). Each model has a dominant shape that maps tentatively, plus a sub-shape that may or may not require separate verification.

**Question:** Are the tentative mappings correct, or do harker/tfordy/srpchase exhibit 9th, 10th, 11th distinct shapes not covered by the 8 anchors?

**Action:** Sprint 27 Day 1/2 hand-derive KKT for each tentative-mapping model's dominant equation; verify against the presumed-anchor's hand-derived form. If shapes differ, expand anchor set OR document sub-shape as a tightening-required edge case.

### Open Question 4: dinam's "2 distinct shapes" justification (Shape A vs Shape B)

Per Unknown 1.2 Research Question #4: "Does the dinam '2 distinct shapes' justification hold up under formal analysis, or is dinam actually 1 shape with positional variations?"

Inspection-only finding (this document): Shape A (`stat_ka(te)` row-multiplier-collapse) and Shape B (`comp_mb(i,t)` differentiate-vs-current-eq-index) appear to be related — Shape B is the pre-collapse constraint form, Shape A is the post-collapse stationarity form. They may be **1 logical shape with 2 positional variations** (constraint emit vs stationarity emit derived from the same gate-predicate path).

**Question:** Does the formal hand-derived KKT confirm 1 shape or 2?

**Action:** Sprint 27 Day 1/2 hand-derive both shapes; if 1 shape collapses, reduce dinam's Phase 0 verification budget from 2 to 1. If 2, both remain.

### Open Question 5: Anchor-pair collapse risk

Inspection-only finding: no two anchors show structurally identical shapes. Closest near-pairs:

- **launch vs sambal** — both use synthetic-alias indices (`ss` / `__kkt1`) inside Pattern C sums. Distinct via the alias-indicator (`ge(s,ss)` order-relation vs `xb(i,i__kkt1)` parameter-as-condition).
- **qdemo7 vs ferts** — both use set-membership indicators (`sc(c,s)` 2-set / `ppos(i,p)` 2-set). Distinct via the bound-index count (qdemo7 1-bound vs ferts 2-bound).
- **ganges vs gangesx** — same family (gangesx → ganges mapping, NOT an anchor-pair).

**Question:** Will formal hand-derived KKT collapse any near-pair to a single shape?

**Action:** Sprint 27 Day 1 hand-derive launch + sambal pair; if shape collapses, reduce verification budget by 1h. Repeat for qdemo7 + ferts.

---

## 7. Verification Summary (Sprint 27 Day 0 Prep)

| Verification Target | Result |
|---|---|
| 15/15 #1398-affected models present at non-compare_match Day 0 buckets | ✅ Confirmed (per §2 + Unknown 1.1 verification) |
| 8 anchor models distinguishing emit patterns documented | ✅ §3 (launch) + §4 (7 in-cohort anchors) |
| 7 non-anchor models mapped to anchors with justification | ✅ §5 |
| Anchor-pair collapse risk surveyed | ✅ §6 Open Question 5 (no collapse identified in inspection; Day 1/2 confirmation pending) |
| 9th-shape candidate flagged | ✅ §6 Open Question 2 (shale sameas-Cartesian sub-shape) |
| dinam 2-shape claim assessed | ✅ §6 Open Question 4 (inspection suggests possible 1-shape collapse; Day 1/2 confirmation pending) |
| `fawley` scope-impact flagged | ✅ §6 Open Question 1 (folded into #1356; Day 1 confirmation pending) |
| Self-recoveries / scope-shrinkage flagged | ✅ No self-recoveries; ganges + srpchase at `translate_timeout` due to machine-variance churn but remain in #1398 scope (per Unknown 1.1) |

**Sprint 27 Priority 1 scope decision:** **CONFIRMED at 15 models** with 8 anchors. **5 Open Questions** escalate to Day 1/2 Phase 0 hand-derived KKT for resolution. **No anchor-set expansion or contraction required from this inspection-only audit.**

---

## 8. Related Documents

- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 4 — this task's specification.
- `docs/planning/EPIC_4/SPRINT_27/BASELINE_METRICS.md` §6.2 + §6.3 — Day 0 bucket inventory (Task 3 output).
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` §Unknown 1.1 (15-model bucket verification), §Unknown 1.2 (anchor-distinctness research questions), §Unknown 4.2 (launch byte-stability vs Priority 4).
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §Sprint 27 §"Priority 1: Phase A Gate Predicate Tightening (#1398)" L1030-L1033 — anchor list source.
- `CONTRIBUTING.md` §"Phase 0 Acceptance Gates" (codified Sprint 26 retro PR20) — verification methodology.
- `data/gamslib/mcp/<model>_mcp.gms` for each of the 15 affected models — emit artifacts inspected for this mapping.

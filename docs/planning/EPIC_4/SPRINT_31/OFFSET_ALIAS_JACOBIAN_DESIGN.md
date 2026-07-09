# Offset-Alias #1111/#1112 Recipe Re-Confirmation + Distance-Jacobian Second-Index Design

**Task:** Sprint 31 Prep Task 4 (Priority 2 foundation)
**Date:** 2026-07-08
**Owner:** Development team (AD specialist)
**Scope:** design/analysis only — no `src/` change (read-only parses/emits + the read-only KKT-residual harness; committed goldens untouched).

---

## 0. Executive summary

Sprint 30 Day 7 control-verified polygon's 4-term coupled fix (warm-match 0.780 ≈ NLP 0.7797); Day 8 implemented the **objective-successor half** (interior-representative selection) but reverted it — it can't ship without the coupled **distance-Jacobian second-index** cross-term, which is the #1111/#1112 general-alias core. This task **re-confirms the recipe on the current tree** and designs the coupled second-index restoration.

**Headline findings (all empirically re-confirmed on the current tree):**

1. **The 4-term recipe reproduces exactly (Unknown 2.1 ✅).** The KKT-residual harness on `polygon.gms` is byte-identical to the banked Day-0 fingerprint: **CASE_B, `stat_theta(i12)` rel 0.492, dual-transfer CONSISTENT.** The current `polygon_mcp.gms` emit drops precisely the four banked terms — the distance **second-index** sum (`$(ord(j)<ord(i))`) and the objective **predecessor** cross-term — while keeping the first-index distance sum (`$(ord(j)>ord(i))`) and the own-row objective successor.
2. **Two PR24 fix-surface corrections.** (a) The distance second-index drop is in **`_add_indexed_jacobian_terms` (`src/kkt/stationarity.py:5767`)**, NOT `src/ad/constraint_jacobian.py` as the prompt/`ISSUE_1143` Day-8 block name it — the constraint Jacobian *computes* both first- and second-index derivative entries; the *stationarity* transpose-sum assembly drops the second. (b) The reverted objective half (`_count_additive_terms` / `_distinct_base_offsets`) is confirmed **absent on `main`** (correctly reverted), and `shape8_offset_alias_successor` is **strict-xfail**.
3. **#1110 orthogonality confirmed (Unknown 2.2).** The Issue #1110 multi-pattern logic (`stationarity.py:6155–6338`) emits a **single scalar** `_multi_pattern_correction` (the diagonal-vs-off-diagonal delta `min_d − maj_d` at the matched point) — it is *keyed on derivative-structure-pattern multiplicity*. The polygon second-index term is a **whole complementary sum** *keyed on constraint-index-POSITION multiplicity* (the same variable instance appears at position 0 AND position 1 of a 2-index constraint). Different structural predicate, additive code path → restoring the second-index sum does not touch the #1110 majority/minority machinery the CGE multi-pattern cohort depends on.
4. **himmel16 is non-convex — a scope guard, not a P2 target (Unknown 2.4 ✅).** `ISSUE_1146` records the Day-7 control experiment refuting its sign fix (flipping `stat_area`'s obj-grad sign is inert; the cold objective stays 0.385 — a spurious local optimum of the non-convex max-hexagon-area problem). No emit fix converts it.

**Disposition:** PROCEED with the coupled fix (objective-successor half + distance second-index half, landed together, tightly gated to var-at-two-indices), with `shape8` enable as the completion gate. REPLAN to a Sprint-32 #1111/#1112 AD-engine filing only if the gate cannot be made tight (it leaks into the CGE multi-pattern cohort).

---

## 1. Recipe re-confirmation on the current tree (Unknown 2.1)

**Harness (read-only):**

```
$ .venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/polygon.gms
dual transfer: CONSISTENT (max comp infeas 1.52e-12 rel, max equality residual 0.00e+00)
verdict: CASE_B — emit_bug
max-residual row: stat_theta(i12)   rel = 4.92e-01
  stat_theta(i12) 4.92e-01 / stat_theta(i13) 4.87e-01 / stat_theta(i11) 4.80e-01 / …
```

Byte-identical to the Sprint-29/30 Day-0 fingerprint (`ISSUE_1143`: CASE_B, `stat_theta(i12)` rel 0.492, CONSISTENT). **The banked recipe is valid on the current tree — no drift.**

**The current emit drops exactly the four banked terms** (`/tmp/polygon_mcp.gms`, regenerated read-only):

```
stat_r(i)..     ((-1)*(0.5*sin(theta(i+1)-theta(i))*r(i+1)*1$(j(i))))
              + sum(j, ((2*r(i) - cos(theta(j)-theta(i))*r(j)*2) * lam_distance(i,j))$(ord(j) > ord(i)))
              - piL_r(i) + piU_r(i) =E= 0;                    # first-index distance sum ONLY
stat_theta(i).. ((-1)*(0.5*r(i+1)*r(i)*cos(theta(i+1)-theta(i))*(-1)*1$(j(i))))
              + lam_ordered(i) + ((-1)*lam_ordered(i-1))$(ord(i)>1)
              + sum(j, (((-1)*(2*r(i)*r(j)*((-1)*(sin(theta(j)-theta(i))))*(-1)))*lam_distance(i,j))$(ord(j) > ord(i)))
              - piL_theta(i) + piU_theta(i) =E= 0;            # first-index distance sum ONLY
```

Missing (the banked 4-term recipe, `ISSUE_1143` Day-7):

| # | Missing term | Class |
|---|---|---|
| 1 | `stat_r(i) += ((-1) * (0.5 * sin(theta(i)-theta(i-1)) * r(i-1) * 1$(j(i-1))))` | objective predecessor |
| 2 | `stat_theta(i) += ((-1) * (0.5 * r(i) * r(i-1) * cos(theta(i)-theta(i-1)) * 1$(j(i-1))))` | objective predecessor |
| 3 | `stat_r(i) += sum(j, ((2*r(i) - cos(theta(j)-theta(i))*r(j)*2) * lam_distance(j,i))$(ord(j) < ord(i)))` | distance **second-index** |
| 4 | `stat_theta(i) += sum(j, ((2*r(i)*r(j)*sin(theta(i)-theta(j))) * lam_distance(j,i))$(ord(j) < ord(i)))` | distance **second-index** |

The control experiment (`ISSUE_1143` Day-7): hand-patching all four → **warm-match 0.780 ≈ 0.7797** (cold stays MS-5 — non-convex area-max — so this is a **presolve/warm** match, converting polygon mismatch → match, a genuine-floor +1). The distance-only subset alone → 0.000 (broken) — confirming the "land all together" coupling.

**PR24 corrections recorded:** (a) fix-surface file is `stationarity.py:5767`, not `constraint_jacobian.py`; (b) the objective half is absent on `main` (reverted); (c) `shape8` strict-xfail.

---

## 2. The distance second-index drop + the restoration (Unknown 2.2)

### 2.1 Where the second-index sum is dropped

`_add_indexed_jacobian_terms` (`src/kkt/stationarity.py:5767`, called from the stationarity builder at `:2714`/`:2726`) assembles the Jacobian-transpose cross-terms for an indexed variable:

1. It scans the Jacobian and **groups entries by constraint name** into `constraint_entries` (`:5789–5806`) — so for `distance(i,j)` and variable `r`, the entries where `r` appears at **position 0** (var==`i`, `ord(j)>ord(i)`) *and* the entries where `r` appears at **position 1** (var==`j`, i.e. `r(i)` is the second index of `distance(j,i)` for rows `j<i`) all land in the **same** `constraint_entries["distance"]` list.
2. For each constraint it takes `entries[0]` as the representative (`:5814`) and builds **one** transpose sum from that structure — the first-index direction (`ord(j)>ord(i)`).
3. The Issue #1110 multi-pattern logic (`:6155–6338`) then detects that the group holds ≥2 distinct *derivative-structure keys* and emits a **single scalar** `_multi_pattern_correction = (min_d − maj_d)·mult` (`:6334`, applied at `:7080–7082`) — the diagonal-vs-off-diagonal delta.

The empirical Jacobian shape (`ISSUE_1143` Day-8): `distance/r` has **300 first-index + 300 second-index** nonzero entries with **distinct structure keys** (`2*r − cos*(r*2)` vs `2*r − cos*(2*r)`). The #1110 scalar correction captures a *point delta*, not the **complementary sum** over the second-index rows — so the whole `sum(j, …·lam_distance(j,i))$(ord(j)<ord(i))` is dropped.

### 2.2 The restoration (the general-alias core)

Emit a **second, separate transpose sum** for the second-index-position entries, mirroring the first-index sum with **inverted multiplier index order** and a **flipped `ord` condition**:

```
# first-index (existing):   sum(j, ∂distance(i,j)/∂·(i) · lam_distance(i,j))$(ord(j) > ord(i))
# second-index (NEW):       sum(j, ∂distance(j,i)/∂·(i) · lam_distance(j,i))$(ord(j) < ord(i))
```

**Design:** inside `_add_indexed_jacobian_terms`, when a constraint's grouped entries map the **same variable instance to ≥2 distinct constraint index-positions** (var-at-two-indices — position 0 in some rows, position 1 in others), split the group by variable-index-POSITION and emit one transpose sum per position, each with its own multiplier-index order and `ord` guard derived from that position's rows. The first-index sum is unchanged; the second-index sum is the new emission. This is genuinely new *per-constraint-position* cross-term logic (the #1111/#1112 general-alias core), distinct from the #1110 pattern-multiplicity correction.

### 2.3 #1110 orthogonality (Unknown 2.2)

The two mechanisms live in the same function but key on **different structural predicates**:

| | Issue #1110 multi-pattern correction (`:6155–6338`) | Distance second-index restoration (NEW) |
|---|---|---|
| **Trigger** | one variable appears **directly AND inside a sum** in a constraint body → ≥2 distinct *derivative-structure keys* in the group | one variable instance appears at **≥2 distinct constraint index-POSITIONS** of a multi-index constraint |
| **Topology** | diagonal vs off-diagonal | var-at-two-indices (position 0 vs position 1) |
| **Emission** | a **single scalar** `_multi_pattern_correction` (`min_d − maj_d`) | a **whole complementary sum** with inverted multiplier order + flipped `ord` |

They are additive and independent: the second-index split keys on position multiplicity (a property of the index mapping), not on derivative-structure-pattern multiplicity, so it does not enter the #1110 majority/minority selection that the CGE multi-pattern cohort depends on. **Verification (in-sprint):** the `--resolve-changed` GO list on the CGE multi-pattern models stays byte-identical after the restoration (they have no var-at-two-indices constraint, so the new gate never fires).

---

## 3. Coupled-landing design + gate (Unknown 2.3)

The two halves **must land together** — neither alone matches, and the objective half *alone* regresses polygon to **MS-5 Locally Infeasible** (the Sprint-29 coupling: a complete objective gradient over a still-inconsistent constraint KKT admits a degenerate `area=0` solution).

| Half | Fix surface | Status |
|---|---|---|
| **Objective successor** | `_build_indexed_gradient_term` (`stationarity.py:2864`) — the interior-representative selection (`_count_additive_terms`: pick the non-zero instance with the **most additive gradient terms** before re-symbolizing, so the predecessor image is not dropped by a boundary column) | implemented+verified Day 8, **reverted** (banked in `ISSUE_1143`); re-land |
| **Distance second-index** | `_add_indexed_jacobian_terms` (`stationarity.py:5767`) — the new per-position complementary sum (§2.2) | new (this design) |

**Tight gate (both halves):** fire only on the offset-alias / var-at-two-indices shape — the objective half when the summand gradient carries a non-circular successor offset image (`j(i+1)`-style), the Jacobian half when a variable instance maps to ≥2 constraint index-positions under an ordinal/offset condition. Both return unchanged for every other shape (the #1387/#1455 per-instance-offset cohort and the CGE multi-pattern cohort are untouched).

**Completion gate:** `shape8_offset_alias_successor` drops its `strict=True` xfail (its assertion `"x(i+1)*1$(j(i))"` **and** `"x(i-1)*1$(j(i-1))"` in `stat_x(i)` passes once the objective half is applied), **and** polygon warm-matches 0.780 with the coupled fix, **and** the CGE multi-pattern GO list is byte-stable. Add a companion **distance-second-index property fixture** (a `shape10`-style synthetic guarding `sum(j, …·lam_g(j,i))$(ord(j)<ord(i))`) so the Jacobian half is guarded independently of polygon (P7 infrastructure).

---

## 4. himmel16 non-convex scope guard (Unknown 2.4)

himmel16 (`ISSUE_1146`) is **documented non-convex** — the Sprint-30 Day-7 control experiment refuted its `stat_area` sign fix: flipping the objective-gradient sign `(-1)→(1)` in the cold emit is **inert** (the cold objective stays at 0.385). himmel16 matches **warm** (0.674 ≈ NLP 0.675) but cold-converges to a spurious 0.385 (max-hexagon-area is non-convex; multiple local optima); the harness CASE_B / `stat_area` rel-2.0 signal is a uniform-`nu = −eq.m` negation artifact (the emit `stat_area = −1 + nu_areadef` is correct: `nu_areadef=+1` at the optimum → residual 0). **No emit fix converts himmel16.** It is a scope guard, NOT a P2 target — `shape7_offset_alias_cyclic` guards the *structural* cyclic decomposition (himmel16's **circular** lead `i++1` — GAMS's wrap-around `++` operator, distinct from the linear `i+1` `+` — decomposes into a linear predecessor `i-1`$(ord>1) plus a boundary wrap `i+(card-1)`$(ord<=1)), but the numeric residual is inherent non-convexity and is not asserted. The P2 second-index restoration is orthogonal to himmel16's shape and must not be expected to convert it.

---

## 5. Sprint-32 REPLAN exit (Unknown 2.3)

If the var-at-two-indices gate **cannot be made tight** — i.e., the second-index split fires on (or the #1110 machinery entangles with) the CGE multi-pattern cohort and regresses a byte-golden — then the per-position cross-term logic requires the full **#1111 alias-aware-differentiation / #1112 dollar-condition-propagation core**, which is an AD-engine restructure beyond a Sprint-31 tight-gate fix. **REPLAN to a Sprint-32 #1111/#1112 AD-engine filing**, reallocating budget per the Task-7 assessment; polygon's genuine-floor +1 becomes conditional. The banked control-verified 4-term recipe (§1) + the working objective half + this second-index design make that filing a well-specified, de-risked hand-off (not an open question).

---

## 6. Unknowns resolved

- **2.1 (recipe re-confirmation): ✅ VERIFIED — no drift.** Harness byte-identical to the Day-0 fingerprint (CASE_B, `stat_theta(i12)` 0.492, CONSISTENT); the current emit drops exactly the four banked terms. PR24 corrections: fix-surface file is `stationarity.py:5767` (not `constraint_jacobian.py`); objective half absent on `main`; `shape8` strict-xfail.
- **2.2 (second-index drop + #1110 orthogonality): ✅ VERIFIED.** Drop is in `_add_indexed_jacobian_terms` (`stationarity.py:5767`) — the per-constraint group builds one sum on the first-index representative and drops the second-index complementary sum; restoration = a new gated per-position sum (inverted multiplier order + flipped `ord`). #1110 is orthogonal (single-scalar diagonal-vs-off-diagonal delta keyed on pattern multiplicity, vs a whole sum keyed on position multiplicity).
- **2.3 (tight gate vs core): localized fix ships this sprint; Sprint-32 REPLAN exit named.** Gate = var-at-two-indices (position multiplicity + ordinal/offset condition); `shape8` enable + polygon warm-match 0.780 + CGE byte-stable is the completion gate; REPLAN to the #1111/#1112 AD-engine filing if the gate leaks.
- **2.4 (himmel16 non-convex): ✅ VERIFIED — scope guard.** Sign-fix refuted (`ISSUE_1146`); no emit fix converts it; `shape7` guards the structure, not the numeric residual. Not a P2 target.

---

## Appendix — evidence

- **Harness (read-only):** `.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/polygon.gms` → CASE_B, `stat_theta(i12)` rel 0.492, dual-transfer CONSISTENT.
- **Current emit (read-only):** `.venv/bin/python -m src.cli data/gamslib/raw/polygon.gms -o /tmp/polygon_mcp.gms` → `stat_r`/`stat_theta` carry the first-index distance sum `$(ord(j)>ord(i))` and the own-row objective successor, dropping the second-index `$(ord(j)<ord(i))` sum + the objective predecessor.
- **Code trace (read-only):** `_add_indexed_jacobian_terms` (`stationarity.py:5767`, called `:2714/:2726`; per-constraint grouping `:5789–5806`; representative `entries[0]` `:5814`); Issue #1110 multi-pattern (`:6155–6338`, scalar correction applied `:7080–7082`); `_build_indexed_gradient_term` (`:2864`, objective half; `_count_additive_terms` absent on `main` = reverted).
- **Banked recipe:** `ISSUE_1143` Day-7 (the 4 terms + control-verified warm-match 0.780) + Day-8 (objective half implemented/reverted; distance half = #1111/#1112 core).
- **himmel16:** `ISSUE_1146` (sign-fix refuted, non-convex).
- No `src/` or golden change; all probes were read-only.

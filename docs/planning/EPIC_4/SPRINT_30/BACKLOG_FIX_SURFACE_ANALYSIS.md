# Sprint 30 — Backlog Fix-Surface Analysis (the banked tracks)

**Task:** Sprint 30 Prep Task 9 (analysis-only — Day-0 patch-site hypotheses per PR24; fixtures added in-sprint). Zero `src/` here.
**Date:** 2026-07-06
**Scope:** the Sprint-30 tracks whose diagnosis is **banked but not yet implemented** — #1385 sarf runtime-guard cross-terms (hand-derived Sprint 29 Day 9), the offset-alias #1146/#1143 + #1111/#1112 fix (reverted Sprint 29 Day 5), and the Class-B CGE `stat_pz` coefficient discrepancy (harness-localized Sprint 29 Day 12) — plus the hhfair widened-VARIABLE blast radius (Unknown 3.3) and the property-test fixture plan (Task 8 catalog).
**Inputs:** the Task-5 Phase-0 gates, the Task-8 tooling-readiness audit (property-catalog extensibility), the banked ISSUE docs, and fresh Day-0 `kkt_residual.py` runs on the Class-B cluster.
**Method:** each fix-surface is a Day-0 hypothesis (PR24 — the banked `file:line` is a *hypothesis* to re-confirm on Day 0, not a fact). REPLAN-prone tracks carry an explicit Sprint-31 exit.

---

## Part A — #1385 sarf runtime-guard cross-terms (the atomic symbolic-emit)

**Banked state (Sprint 29 Day 9):** smallest target = **sarf** (471 lines). The `stat_task(g,t,m,n)` cross-terms are **hand-derived + banked** in `ISSUE_1385` (the 6-guarded-term derivation). REPLAN'd to Sprint 30 because the *implementation* — a new symbolic runtime-guard cross-term emit path — is the Sprint-26-Day-4-failed architecture (the `nu_slack("srn")` set-name-literal-index bug), not the *derivation*.

**Fix-surface hypothesis (PR24, two coupled sites — must land atomically):**

| Site | `file` (Day-0 hypothesis) | Role |
|---|---|---|
| **Gate extension** | `src/ad/index_mapping.py` — `enumerate_equation_instances` / `_is_blowup_dynamic_subset_equation` | The srpchase short-circuit is **1-D-only** (`len(eq_domain) != 1` bails); sarf's blow-up constraints are **2-D dynamic-subset** (`tbal(g,t)$taskposs(g,t)`, `equipb1(m,t)$equipposs(m,t)`, `equipb2(n,t)$equipposs(n,t)`). Extend the gate to the 2-D shape so these skip per-instance AD enumeration. |
| **Symbolic runtime-guard cross-term emit** | `src/kkt/stationarity.py` — a new symbolic-emit path (the short-circuited equations enumerate **zero** instances, so the `J_gᵀ·lam` cross-terms cannot be assembled from per-instance Jacobian entries — they must be built by symbolically differentiating each constraint body parametrically in `(g,t,m,n)`) | Re-emit the runtime-guarded constraint bodies **and** inject the matching `+ sum(g, ∂g/∂y·nu_g)` cross-term into every `stat_y` the constraint touches, with the `$taskposs`/`$equipposs` guards and **no quoted-set-name multiplier indices**. |

**The atomicity constraint (Unknown 4.1 — the load-bearing risk):** re-emitting the constraints WITHOUT the cross-terms = an inconsistent MCP (multipliers with no complementarity coupling), so there is **no safe partial landing** — the gate extension + the cross-term emit must land together. The banked `stat_task(g,t,m,n)` derivation (`ISSUE_1385` §PROCEED/REPLAN) is the emit target: 6 guarded terms (`nu_tbal`, the `tadj` special term, `lam_labor`, `lam_equipb1`, `lam_equipb2`, `nu_acost3`) + `piL_task`, all indexed over the stat equation's own domain `(g,t,m,n)` — **no set-name-literal indices** (the Day-4 failure mode).

**Instance-count tractability (Unknown 4.2 — the REPLAN trigger):** the skipped-constraint instance counts are **tbal 384 + equipb1 648 + equipb2 120 = 1,152** (the `taskposs`/`equipposs` conditions are computed from `treq`/`tech` data, zero concrete members at compile time → the full Cartesian is what blows up `differentiate_expr` >200 s). The **symbolic** re-emit must **not** re-enumerate these per-instance — it differentiates the constraint body *once* parametrically in `(g,t,m,n)` and emits a single runtime-guarded row, so the emit-time cost is O(constraints), not O(instances). **REPLAN to Sprint 31** if the symbolic re-emit path cannot avoid the per-instance enumeration (i.e., it re-triggers the translate-timeout) — that is the concrete tractability gate, checked Day-0 by timing the emit on sarf.

**Verification (Day-0):** emit `sarf_mcp.gms`; assert (a) it emits under the translate budget (no timeout), (b) the `stat_task` row matches the banked 6-term derivation, (c) `grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("'` finds **no** set-name multiplier index, (d) GAMS `action=c` compile-clean; then the harness becomes the residual verifier (Case a at the NLP optimum). **+Translate target** (sarf `translate_failure → translate`); not a Solve/Match gain this sprint.

---

## Part B — Offset-alias #1146/#1143 (the Day-5 revert coupling + coordinated fix)

**Shared root cause (Unknown 7.1 context):** both himmel16 (#1146) and polygon (#1143) are harness-**Case b** on a single `stat_*` row, both **already match warm** (cold-robustness / genuine-floor, NOT +Match), both route through `src/ad/derivative_rules.py` (`_diff_varref`, `_partial_collapse_sum`) + `src/kkt/stationarity.py:3486` (`_replace_indices_in_expr`). **But they are distinct shapes with distinct remaining bugs** (below), so the "one fix, two models" framing from Sprint 29 is **refined**: they share the code path, not the exact defect.

### B.1 polygon (#1143) — the Day-5 revert root cause (Unknown 5.1)

**Day-5 revert (confirmed from `ISSUE_1143`):** the Day-4 representative-selection fix made polygon's **objective gradient** correct (`stat_theta`/`stat_r` gained the predecessor offset-image cross-term), but the Day-5 Checkpoint re-solve caught **`match` (0.7797) → `mismatch` (spurious 0.0 optimum)**. Root cause of the regression = polygon has a **SECOND, independent bug**: the `distance(i,j)` **constraint-Jacobian symmetry** — `stat_r` sums only the `ord(j)>ord(i)` first-index direction, dropping the symmetric second-index `r(j)` term (the "Multi-pattern Jacobian: skipping correction for distance/r" warning). With the objective gradient now complete but the distance-Jacobian still one-sided, the KKT admits a degenerate `area=0` solution → mismatch.

**Coordinated-fix hypothesis (PR24):** land **together** (a) the objective-gradient successor-offset cross-term (the reverted representative-selection in `_diff_varref` :371 / `_partial_collapse_sum` non-circular branch ~:1989/:2022, preserved in the `shape8` xfail) **and** (b) the `distance(i,j)` constraint-Jacobian second-index symmetry (`src/ad/constraint_jacobian.py` — the multi-pattern-Jacobian correction that currently skips the `r(j)` direction). **Neither alone matches** — (a) alone regressed to 0.0 (the Day-5 revert); (b) alone leaves the dropped objective cross-term. This is the load-bearing coupling Unknown 5.1 names.

### B.2 himmel16 (#1146) — the cyclic cross-term is present; a numeric/sign defect

**Refined Day-4 finding (from `ISSUE_1146`):** himmel16's `stat_x`/`stat_y` **already carry** the circular `i++1` decomposition (`nu_areadef(i-1)$(ord>1)` linear predecessor + `nu_areadef(i+5)$(ord<=card-5)` boundary wrap) — the cross-term structure is **present, not dropped**, so the #1143 representative-selection fix does **not** change himmel16 (`stat_area` stays rel 2.0). The 2.0 residual is a **numeric/sign defect** in the objvar-defining-gradient interaction: `stat_area.. -1 + nu_areadef(i)`, where the `-1` is the `totarea = sum(area)` gradient and the transferred `nu_areadef` carries the equality sign — a `_diff_varref(circular=True)` + dual-transfer-sign reconciliation (`_diff_varref` :371, circular branch ~:1866). **Distinct from polygon** — himmel16 needs the cyclic-coefficient/objvar-gradient-sign fix, not the successor cross-term + distance-Jacobian.

### B.3 The #1111/#1112 architectural-REPLAN boundary (Unknown 5.2)

The single-row integer-residual signatures **lean localized** — a cross-term correction gated tightly to the cyclic (`i++1`) / successor (`ord(j)=ord(i)+1`) shapes. **REPLAN to Sprint 31** (the **#1111** alias-aware-differentiation / **#1112** dollar-condition-propagation AD-engine core) **only if** a localized gate cannot make the composition correct without threading the general alias-differentiation core — e.g. if the polygon distance-Jacobian symmetry fix or the himmel16 objvar-sign fix cannot be scoped to the offset-alias shape without changing general alias diff. The #1111/#1112 footprint is small (3 open issues: #1146/#1143/#1162), so it is a **Sprint-31 candidate, not an Epic-5 necessity** — flagged here for the Task-6 REPLAN assessment.

---

## Part C — Class-B CGE `stat_pz` (general-emit coefficient discrepancy)

**Fresh Day-0 harness confirmation (this task — the one-fix-several evidence, Unknown 7.1):**

| Model | Verdict | Max-residual row | rel | Dual transfer |
|---|---|---|---|---|
| **irscge** | CASE_B — emit_bug | `stat_pz(MLK)` | **1.00** | CONSISTENT |
| **lrgcge** | CASE_B — emit_bug | `stat_pz(MLK)` | **1.00** | CONSISTENT |
| **moncge** | CASE_B — emit_bug | `stat_pz(BRD)` | **1.00** | CONSISTENT |

All three localize to the **same** `stat_pz` row shape with an **identical relative residual of exactly 1.00** and **CONSISTENT** dual transfer — the fingerprint of a **missing unit-coefficient factor** on the `pz`-referencing cross-term (the terms are present; the *coefficient* is off by a unit factor). The **CASE_B** verdict (not the MS-4-at-iteration-0 singular-Jacobian signature) confirms this is **NOT** the camcge (#1330) Walras degeneracy (Unknown 7.3) — the market-clearing block is full-rank; the fix stays in **nlp2mcp general emit**, not Epic 5.

**Fix-surface hypothesis (PR24):** the general stationarity-emit coefficient path for the CGE output-price variable `pz(j)` — the Jacobian-transpose **coefficient** on the `pz`-referencing cross-terms in `src/kkt/stationarity.py` / `src/ad/constraint_jacobian.py`. `pz(j)` is defined by the zero-profit/price row `eqpzs(j)` (activity price = unit cost) and appears in the market-clearing/income rows; one of those cross-terms carries a mis-scaled (or missing-unit) coefficient. Because the residual is **identical (rel 1.0)** across irscge/lrgcge/moncge, **one general-emit coefficient fix converts all three** (the "one fix, several models" verdict). **stdcge** (`stat_epsilon` rel 2.0) and **marco** (`stat_w` rel 3.3) are **adjacent per-variable variants** — likely the *same* coefficient-path bug on a different output variable (stdcge probable; marco is model-specific and tracked separately).

**Payoff + disposition:** genuine-floor (cold-robustness) — all five already `model_optimal_presolve`-match; the models are non-convex, so a correct emit confirms via residual → 0 (Case a) at the NLP optimum even where the cold solve still needs the warm-start. **PROCEED-conditional** on the one-fix-several confirmation (now strongly evidenced for irscge/lrgcge/moncge); **REPLAN** to the highest-residual 1–2 models only if the coefficient proves per-model (still worth the cold-robustness; not an architectural REPLAN).

---

## Part D — hhfair widened-VARIABLE blast radius (Unknown 3.3)

**Fix-surface (from `ISSUE_1236` Day-8):** hhfair's compile blocker is **`$184`** — the #1449 widened-symbol conflict but for a **VARIABLE** `n` (source `n(t)` vs MCP-widened `n(tl)`, because `n` appears in `stat_m(tl)`/`stat_c`/`stat_n` over `tl` via the bilinear `timemoney(t).. n(t)*(m(t)-…)`). The #1449 **parameter** `__pw`-companion fix does **not** transfer — `n` is a *live nonlinear-stat coefficient* (not a value-copy), so it needs a **companion variable + value-coupling** (an emit-architecture generalization of #1449 from the parameter case to the variable case).

**Blast-radius hypothesis (PR24):** the widened-VARIABLE fix is a **new, distinct companion-*variable* emit path**, additive to the existing #1449 widened-*parameter* `__pw`-companion path — it must be gated to widened variables that are live nonlinear-stat coefficients and must **not** touch the parameter path. The **#1449 widened-parameter presolve cohort = 4 models** (`cclinpts`, `chain`, `otpop`, `rocket` — the `*_mcp_presolve.gms` carrying the `#1449` marker), which must stay **byte-identical** after the widened-VARIABLE fix. **Blast-radius check (Day-0):** `grep -lE "#1449" data/gamslib/mcp/*_mcp_presolve.gms` → the 4 models; byte-scan them before/after the fix (0 diff) + `--resolve-changed` GO. After the `$184` compile clears, read the CES/product objective-mismatch verdict (Unknown 3.1/3.2): PROCEED if Case-b `stat_*` (+1 Match), REPLAN to Sprint 31 if inherent non-convexity (the `prod`/CES nest).

---

## Part E — Property-test fixture plan (Task-8 catalog)

**Catalog state (Task 8, re-confirmed):** `tests/integration/emit/test_ad_crossterm_shapes.py` = **7 passed, 1 xfailed** over `shape1`–`shape8`. `shape7_offset_alias_cyclic` **passes** (structural-decomposition guard for himmel16's `i++1`); `shape8_offset_alias_successor` is **xfail-strict** (`#1143/#1447: reverted; pending coupled distance-Jacobian fix`).

| Fixture | Track | Plan |
|---|---|---|
| **new head-domain-offset fixture** (P8, e.g. `shape9_head_domain_offset.gms`) | #1385 / mine-robert head-offset | The one **genuinely-missing** shape (none of shape1–8 covers the `nu_sb`/`lam_pr` head-offset cross-term; shape8 is the distinct Category-5 *offset-alias* successor). A minimal synthetic `sb(r,tt+1)`-shaped equation asserting `stat_x` references the head-labeled multiplier. Clean one-file add (a `.gms` + a `def test_shape9_...` using the existing `_emit`/`_stat_row` helpers — no refactor, per Task 8). |
| **`shape8_offset_alias_successor`** (enable) | #1143 polygon | Flip from xfail-strict to passing by dropping `@pytest.mark.xfail` **when the coordinated offset-gradient + distance-Jacobian fix lands** (Part B.1). Its assertions (`x(i+1)*1$(j(i))` own-row successor + `x(i-1)*1$(j(i-1))` predecessor cross-term) are the polygon regression guard. |
| **`shape7_offset_alias_cyclic`** (extend) | #1146 himmel16 | Already passes as a **structural** guard (the `i++1` decomposition is present). Its **numeric** correctness (the 2.0 objvar-gradient-sign defect, Part B.2) is not assertable without a GAMS residual eval — add a numeric assertion (or a companion residual-fixture) when the himmel16 objvar-sign fix lands. |

---

## Summary — the banked fix-surfaces at a glance

| Track | Fix surface (Day-0 hypothesis) | Coupling / risk | Payoff | Disposition |
|---|---|---|---|---|
| **#1385 sarf** | `index_mapping.py` 2-D gate + `stationarity.py` symbolic runtime-guard cross-term emit | **atomic** (re-emit + cross-terms together); instance-count blow-up (1,152) must not re-enumerate | +1 Translate | PROCEED; REPLAN S31 if the symbolic emit re-triggers the timeout |
| **#1143 polygon** | objective-gradient successor cross-term **+** distance-Jacobian symmetry (`derivative_rules.py` + `constraint_jacobian.py`) | **coupled** — neither alone matches (Day-5 revert) | genuine-floor | PROCEED (coordinated); REPLAN S31 if #1111/#1112 core needed |
| **#1146 himmel16** | cyclic-coefficient / objvar-gradient-sign in `_diff_varref(circular=True)` + dual-transfer sign | distinct from polygon; numeric/sign (not a dropped term) | genuine-floor | PROCEED (localized); REPLAN S31 if #1111/#1112 core needed |
| **Class-B `stat_pz`** | general-emit coefficient path for `pz(j)` cross-terms (`stationarity.py` / `constraint_jacobian.py`) | one-fix-several (irscge/lrgcge/moncge identical rel 1.0) | genuine-floor | PROCEED-conditional; per-model REPLAN → 1–2 models |
| **hhfair widened-VAR** | #1449 generalized to the variable case (companion variable + value-coupling) | must not regress the 4 #1449 widened-param presolve models | +1 Match (if Case b post-compile) | PROCEED; REPLAN S31 if post-compile non-convexity |

## Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_30/BACKLOG_FIX_SURFACE_ANALYSIS.md && echo present
grep -Ei '#1385|sarf|#1146|#1143|#1111|#1112|stat_pz|distance-Jacobian|shape7|shape8|widened-VAR' docs/planning/EPIC_4/SPRINT_30/BACKLOG_FIX_SURFACE_ANALYSIS.md | head
# Class-B one-fix-several (identical stat_pz 1.0 across the cluster):
for m in irscge lrgcge moncge; do .venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/$m.gms 2>&1 | grep -iE "max-residual|verdict"; done
# hhfair blast-radius cohort (the #1449 widened-parameter presolve set):
grep -lE "#1449" data/gamslib/mcp/*_mcp_presolve.gms 2>/dev/null | xargs -n1 basename
# Property catalog (7 passed, 1 xfailed):
.venv/bin/python -m pytest tests/integration/emit/test_ad_crossterm_shapes.py -q 2>&1 | tail -1
```

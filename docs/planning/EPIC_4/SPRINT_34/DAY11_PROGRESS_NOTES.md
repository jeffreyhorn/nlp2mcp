# Sprint 34 — Day 11 Progress Notes (P6 failure-cohort re-triage + the `$141` NaN-cleanup fix)

**Date:** 2026-07-21
**Branch:** `planning/sprint34-day11-p6-cohort`
**Track:** P6 — failure-cohort re-triage (the designated best-remaining-shot)
**Disposition:** 📋 **BANK the (verified) `$141` fix + ship the corrected multi-root re-triage (docs-only, no `src/`).** **0 in-sprint bucket recovered — the cohort is far more multi-root than the prep diagnosed.** The `$141` NaN-cleanup emit-bug fix is written and empirically verified (removes ganges's 15 `$141` errors) but **banked, not shipped**: it recovers no model (every cohort member has additional independent blockers), touches only already-failing slow-emit CGE models whose goldens are **un-regenerable in the CI budget** (the regen soft-timed-out on ganges/gangesx/clearlak/turkpow), so shipping it for 0 bucket would leave stale goldens. The deep blockers (`$149` CES/LES AD, `$161` dotted-tuple set) are characterized for a dedicated effort.

---

## 1. The corrected diagnosis — the cohort is deeply multi-root (the prep's "one fix recovers ganges/gangesx" is REFUTED)

Compiled every `path_syntax_error` cohort golden live (repo root). **Error profiles (root, not cascade):**

| Model | error codes | roots |
|---|---|---|
| **ganges** | `$141`×15 · `$145`×3 · `$149`×9 | (a) `.l`-calibration NaN-cleanup · (b) `series(*,years)` universal-set cleanup · (c) `stat_pc` CES/LES uncontrolled index |
| **gangesx** | `$141`×15 · `$145`×3 · `$149`×9 | same as ganges |
| **turkey** | `$161`×6 (+ `$141`/`$257` cascades) | dotted-tuple **set** declaration (`Set ao /grains.wheat, …/`) — unrelated to `$141` |
| **dinam** | `$140`×5 · `$141`×1 · `$149`×3 · `$171`×2 | multi-root (`$140` pruned-`.l`-init + `$141` + `$149` + `$171`) |
| **indus** | `$140`×5 · `$141`×8 · `$148`×2 · `$149`×3 | multi-root |
| **turkpow** | `$141`×1 · `$149`×1 · `$171`×5 | multi-root |
| **clearlak** | `$141`×2 · `$149`×1 | multi-root |

**Finding (corrects `TOOLING_AND_BACKLOG_ANALYSIS.md` §2 / Unknown 6.1):** the prep hypothesis "ganges/gangesx share a single `$141/$145/$149` root; one fix recovers both" is **substantially wrong**. The `$141`, `$145`, and `$149` are **three independent roots**, and **no cohort model recovers from the `$141` fix alone** — every one carries additional independent blockers, several of them deep:
- **`$149` (ganges/gangesx/dinam/indus/turkpow/clearlak)** — an **uncontrolled index in the stationarity emit** (ganges `stat_pc`: the derivative of a CES/LES `prod(j, (pc(j)/pc00(j))**ac(j,r))` term w.r.t. `pc(i)` leaves a free `j`). A **deep AD-core product-rule bug**, not tractable in-session.
- **`$161` (turkey)** — a **dotted-tuple set declaration** (`Set ao` with mixed quoted/unquoted `grains.wheat`-style members). A set-emit bug; the `$141`/`$257` are cascades from it.
- **`$145` (ganges/gangesx)** — a NaN-cleanup line over a **universal-set (`*`) domain** param (`series(*,years)`), invalid GAMS. A second, narrower NaN-cleanup gap.
- **`$140` (dinam/indus)** — the pruned-var `.l`-init shape (sample's S33 root); **NOT** recovered by the sample fix here (verify per-model — the S33 multi-root lesson holds).

This is exactly the "verify per-model; the cohort is multi-root" discipline (`TOOLING` §2 caveat) — realized more strongly than the prep anticipated. **The P6 mandate's "OR the cohort re-triaged with banked diagnoses" branch is the outcome.**

## 2. The `$141` NaN-cleanup fix (genuine emit-correctness, verified)

**Root:** the Issue #1322 NaN-cleanup (`emit_post_assignment_na_cleanup`, `src/emit/original_symbols.py`) emits a **self-referential** guard `param(i)$(NOT (param(i) > -inf and param(i) < inf)) = 0;` over indexed model-relevant params with a division in their assignment — **including `.l`-referencing calibration** params (ganges `adst(i) = dst.l(i)/sum(j, dst.l(j))`). Those calibration assignments are **presolve-gated** (`emit_gams.py:2730`, `if presolve_include_emitted:` — they need the variable `.l` values the pre-solve `$include` populates), so in the **cold** MCP the param is **declared-but-unassigned**, and the self-referential cleanup guard reads it → **`$141`** "Symbol declared but no values assigned."

**Fix:** in `emit_post_assignment_na_cleanup`, skip params whose assignment references a **variable attribute** (`.l`) — via a new `_param_assignment_references_varref_attr` mirroring `_param_assignment_has_division`, using the existing `_expr_contains_varref_attribute`. Such a param is `.l`-calibration (presolve-gated, emitted separately), **not** the #1322 data-division-NA pathology (Table-derived zero-divisor vectors), so the cleanup correctly skips it. (The cleanup is also emitted *before* the calibration in code order, so for `.l`-params it was mis-ordered — never doing useful NA-cleanup — making the skip safe.)

**Verified:** ganges's `$141`×15 are **gone** (cleanup 25→10 lines); the compile advances past them (leaving the pre-existing `$145`/`$149`). Analogous to the S33 sample `.l`-init fix (a *variable*-`.l` shape) but for the *parameter*-calibration shape — a distinct, genuine emit-correctness fix.

## 3. Why bank (not ship) the `$141` fix

The fix (`_param_assignment_references_varref_attr` + the skip in `emit_post_assignment_na_cleanup`) is **correct and verified** — but banked, for three converging reasons:

1. **0 bucket.** No cohort model recovers from it — every one carries an additional independent blocker (`$149`/`$161`/`$145`/`$140`), several deep (§1). The P6 mandate is met on the **"OR the cohort re-triaged with banked diagnoses"** branch, not the recovery branch.
2. **The affected goldens are un-regenerable in budget.** The fix only touches params with `.l`-referencing division assignments — the **slow-emit CGE cohort** (ganges/gangesx). `make regen-goldens` **soft-timed-out** on exactly those models (ganges/gangesx/clearlak/turkpow — "slow-emit, run nightly"), refreshing **0** goldens. No fast/passing model is affected. Shipping the `src/` would leave the committed ganges/gangesx goldens **stale** (old emit) with no in-budget way to regenerate them.
3. **Sprint discipline: no bucket → no `src/`.** Consistent with P1/P2/P3/P5 (all shipped 0 `src/` at 0 bucket). Unlike P4 (which shipped a correctness-only fix), P4's goldens were fast + regenerable + `--resolve-changed` GO; here they are not.

**Banked artifact (the de-risked hand-off):** the exact fix — a `_param_assignment_references_varref_attr(param_def)` helper (mirroring `_param_assignment_has_division`, using `_expr_contains_varref_attribute`) + a skip in `emit_post_assignment_na_cleanup` — is documented verbatim above (§2), verified to remove ganges's 15 `$141`, ready for the dedicated ganges-recovery effort (which can afford the slow golden regen and tackles `$145`/`$149` together).

**Checkpoint:** no `src/`/golden change shipped → `--resolve-changed --since-commit 750803b2` remains GO (the Day-4 P4 goldens hold); the baseline is unmoved.

## 4. KPI + hand-off

- **KPI unmoved:** Solve 108 / Match 93 / genuine floor 75 / model_infeasible 7 / path_syntax_error 7 — **no bucket recovered** (the cohort's deep blockers — `$149` CES/LES AD, `$161` set-emit — are not tractable in-session).
- **Banked for a dedicated effort (the de-risked hand-off):** (a) the `$149` `stat_pc` CES/LES product-rule uncontrolled-index AD bug (the highest-leverage cohort blocker — it gates ganges/gangesx/dinam/indus/turkpow/clearlak); (b) the `$161` turkey dotted-tuple set-declaration emit; (c) the `$145` `series(*,years)` universal-set NaN-cleanup gap; (d) the per-model `$140` verification (dinam/indus).
- **The S33 sample precedent stands but is harder here:** the failure-cohort *is* a genuine bucket source, but this cohort's remaining blockers are deeper than sample's single `$140` — a bucket move needs the `$149`/`$161` fixes, which are dedicated-effort AD/emit work.

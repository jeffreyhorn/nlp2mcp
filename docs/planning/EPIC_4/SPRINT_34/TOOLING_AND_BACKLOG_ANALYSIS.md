# Sprint 34 — Reusable-Tooling Readiness Audit + Backlog Fix-Surface Analysis (Priorities 6 + 7)

**Prep Task:** 10 (Medium) · **Date:** 2026-07-19 · **Owner:** Sprint 34 prep (tooling/infra)
**Day-0 code anchor:** `750803b2` (S33 close) · no `src/` drift since (Task 2 `BASELINE_METRICS.md`)
**Scope:** docs/analysis only — audits the reused tooling + pre-scopes the P6 failure-cohort + P7 infrastructure; no `src/` change.

---

## Executive summary

Sprint 34's diagnostic tooling is **reused, not rebuilt** — a **pure** reuse (the S32 `case_c_objdef` classifier + the S33 P6 `test_sample_pruned_var_l_init.py` fixture pattern are on `main`), so Sprint 34 adds **zero new diagnostic-tool code** and only **three P7 test fixtures** (shape12/shape13 + a fawley 2-D second-index fixture, each gated on P1/P2/P3 landing). All reusable tools are confirmed present, and the checkpoint gate is ready: `run_full_test.py --resolve-changed --since-commit 750803b2 --dry-run` reports **GO (no emit goldens changed)** at Day 0 (`750803b2` an ancestor of `main`; the DB byte-anchor `4cbf8bff` is historical). The P6 fill/absorb-slack work is pre-scoped from **live diagnosis** so Day-6+ P6 is a plan, not a cold survey: **ganges/gangesx share a single, live-confirmed `$141/$145/$149` translate-syntax root** (the NaN-sanitization emit pass), **distinct from sample's `$140`** (pruned-var `.l`-init, the S33 P6 fix) — a single fix may recover **both**; **agreste is a double-`solve` scope caveat** (two `solve … maximizing yfarm using lp` at lines 294/298); the cohort is **multi-root** (verify per-model). No blocking tool gap.

---

## §1. Per-track tooling-readiness audit (Unknown 6.1 tooling-layer)

All reusable tools confirmed present on `main` (the `--resolve-changed` dry-run + the ganges/gangesx compile diagnosis + the DB/source sweep were exercised this task):

| Tool | Path | Confirmed |
|---|---|---|
| KKT-residual harness (incl. `case_c_objdef`) | `scripts/diagnostics/kkt_residual.py` | ✅ present; `reclassify_objdef_case_c` landed (S32); exercised live on mine/fawley (Tasks 3/5) |
| `--resolve-changed` checkpoint | `scripts/gamslib/run_full_test.py` | ✅ **GO dry-run at `750803b2`** this task |
| Golden-staleness gate | `scripts/sprint_audit/check_golden_staleness.py` | ✅ present |
| Presolve-divergence detector | `scripts/diagnostics/check_presolve_divergence.py` | ✅ present |
| `--force` solution-forcing scaffold | `src/cli.py` (`--force`) | ✅ present |
| AD cross-term property catalog | `tests/integration/emit/test_ad_crossterm_shapes.py` (**shapes 1–11**) | ✅ present |
| P6 regression-fixture pattern | `tests/integration/emit/test_sample_pruned_var_l_init.py` | ✅ present (the S33 raw-emit + skip-if-absent pattern) |

| Track | Guarding tool | New tool code for Sprint 34 |
|---|---|---|
| **P1 mine** (head-offset dual subsystem) | `kkt_residual.py` — the **cold**-solve verdict (the reframed gate) + the CASE_B `stat_x` fingerprint; `--resolve-changed` golden-diff on `mine_mcp*.gms` | **None** — the harness reports the `stat_x` Case-b verdict + the CONSISTENT dual flag; new coverage = the **P7 shape12 fixture** (§4). |
| **P2 sarf** (three-site symbolic `stat_task` emit) | the translate-budget timer (`run_full_test.py` emit timing) + the golden-staleness gate on `sarf_mcp.gms` | **None** — the O(active=398) timing probe uses the existing translate path; sarf has **no golden today** (`translate_failure`), so the first emit *creates* `sarf_mcp.gms` (caught by the golden-staleness gate). New coverage = the **P7 shape13 fixture**. |
| **P3 fawley** (constraint-index-diagonal `sameas`) | `kkt_residual.py` — the CASE_B `stat_bq` verdict + `max\|stat_bq\|` residual; `--resolve-changed` on `fawley_mcp*.gms` | **None** — the harness scores the residual; new coverage = the **P7 fawley 2-D second-index fixture** (§4). |
| **P4 bound-transfer** (NEW, sign-robust transfer) | `kkt_residual.py` — the CASE_B warm-residual verdict at the active-bound cells (fawley cc-dist, mine 3 rows); `--resolve-changed` over the MAXIMIZE presolve cohort | **None** — the harness already scores the warm residual; new coverage = a **P7 MAXIMIZE bound-transfer regression fixture** (§4). |
| **P5 camcge/rocket** (Epic-5 / Sprint-35) | `kkt_residual.py` (`stat_mps` / `case_c_objdef`) + the S1∧S2∧S3 detector logic (Task 7, analysis) + the `--force` scaffold | **None** — Epic-5-deferred / Sprint-35 hand-off; the detector + scaffold are reused. |

**Conclusion:** **zero new diagnostic-tool code for Sprint 34** — a pure reuse. The only new test artifacts are the P7 fixtures (§4), each gated on its track landing. No blocking tool gap.

---

## §2. P6 failure-cohort re-triage (Unknowns 6.1, 6.2, 6.3) — LIVE-diagnosed

The `path_syntax_error` cohort (models whose *emitted* MCP fails at the GAMS/PATH **compile** stage) is the Sprint-33-proven bucket source (sample recovered → +1 Solve/Match/floor). This task diagnosed the ganges/gangesx root **live**.

### ganges / gangesx — the `$141/$145/$149` root (Unknown 6.1)

Compiled the committed goldens (`data/gamslib/mcp/{ganges,gangesx}_mcp.gms`) from the repo root (the emit `$include` is repo-relative). **Both have the identical error profile: `$141` ×15, `$145` ×3, `$149` ×9.** The codes:

| Code | GAMS meaning | Root |
|---|---|---|
| **$141** (×15) | "Symbol declared but no values have been assigned" | the NaN-sanitization emit pass emits `param(i)$(NOT (param(i) > -inf and param(i) < inf)) = 0;` — a **self-referential guard** that *reads* `param(i)` — over parameters (`adst`, `aex`, `aid`, `an`, `as`, `av`, `az`, `cg`, `deltan`, `deltas`, …) whose source value-assignment is `= dst.l(i)/sum(j, dst.l(j))` (depends on a **variable level** `dst.l`), which is pruned/absent/mis-ordered in the MCP context → the guard reads an unassigned symbol |
| **$145** (×3) | "Set identifier or quoted element expected" | the same construct's index/domain in the sanitization guard |
| **$149** (×9) | "Uncontrolled set entered as constant" | the same construct's uncontrolled index |

**Conclusion (Unknown 6.1):** ganges and gangesx share a **single, identical translate-syntax root** — the NaN-sanitization / parameter-reset emit pass emitting `param(i)$(NOT (param(i) > -inf …)) = 0;` over declared-but-unassigned parameters (whose source assignment depends on a variable level). **A single fix may recover both.** The fix surface (a hypothesis, PR24): the NaN-sanitization pass (`src/emit/emit_gams.py`) should **skip** a parameter whose value depends on a variable level (unavailable in the MCP context) or emit its assignment before the guard. **Distinct from sample's `$140`** (pruned-var `.l`-init — a *variable* `.l` reference; the S33 P6 fix — skip an `.l`-init whose refs aren't a subset of the declared MCP vars — is a **no-op** here, since ganges/gangesx's root is *parameter* sanitization, not `.l`-init, and their `.l`-init refs are declared). **Each recovery is `--resolve-changed`-gated + a golden-staleness check on the new goldens.**

### agreste — the double-`solve` scope caveat (Unknown 6.2)

agreste is `model_infeasible` MS-5 with a banked CASE_B `stat_sales` rel 2.0. **Confirmed live: agreste has TWO `solve agreste maximizing yfarm using lp;` statements (lines 294, 298)** — a single-model-solved-twice **scenario driver**. So the factor-of-2 in `stat_sales` may be a **driver-doubling artifact** (the model solved twice, doubling a gradient in the harness's single-solve scoping), **not** a genuine dropped-gradient emit bug. **Scope-verify** the harness's single-solve scoping **before** treating the CASE_B `stat_sales` as an emit bug — the right call may be to document + defer (a false CASE_B).

### The cohort is multi-root (Unknown 6.3)

**Confirmed: the `path_syntax_error` cohort is multi-root** — sample (`$140`, pruned-var `.l`-init, recovered S33) ≠ ganges/gangesx (`$141/$145/$149`, parameter-sanitization). The S33 lesson holds: **verify per-model; do not assume a single shared root** (the earlier "one fix recovers the cohort" hypothesis was only partially right — one fix recovers the ganges/gangesx *pair*, but not sample's distinct `$140`). The residual cohort (clearlak/dinam/indus/turkey/turkpow) each needs its own compile-diagnosis before treatment.

---

## §3. P7 infrastructure groundwork (Unknowns 7.1, 7.3)

### The property fixtures (Unknown 7.1)

The AD cross-term property catalog is at **shapes 1–11** (`tests/integration/emit/test_ad_crossterm_shapes.py`). The three Sprint-34 fixtures — each following the S33 `test_sample_pruned_var_l_init.py` pattern (raw-file emit + skip-if-absent) — land **only once** their track lands:

| Fixture | Track | Assertion | Gated on |
|---|---|---|---|
| **shape12** (head-offset dual) | P1 | the emitted `stat_x` carries the head-anchored dual reconciliation | P1 landing (cold MS-1) |
| **shape13** (sarf symbolic) | P2 | the emitted `stat_task` is one guarded `$taskposs` symbol, no set-name literals | P2 landing (translate seconds) |
| **fawley 2-D second-index** | P3 | the emitted `stat_bq` carries `$(sameas(cfq__,cf))` on the qsb/pbal terms | P3 landing (the correction) |

Each is **fail-before/pass-after**, correctly **deferred if its track REPLANs** (the S33 precedent — shape12/13/fawley were all deferred when P1/P2/P3 didn't land). A **P4 MAXIMIZE bound-transfer regression fixture** (the sign-robust transfer at an active bound) is added if P4's correctness fix lands (Option B sense-aware).

### Genuine-floor tracking + Epic-4 SUMMARY (Unknown 7.3)

- **Genuine-floor recompute — anchor 75.** The PR25 genuine-vs-methodology partition re-baselines to **75** (the S33 close; 63 cold + 12 genuine-presolve). The P7 recompute maintains anchor 75 unless a Sprint-34 track lands a genuine cold-emit change (P1/P3-cold-match/P6 recovery → +1).
- **Epic-4 `SUMMARY.md` row 34 — a Day-12 continuation + a theme reconcile.** `SUMMARY.md` row 33 is filled (the S33 close). **Row 34 currently reads `| 34 | 33–34 | Quality, performance & PATH-feedback integration | (planned) | … |`** — but that theme is the **pre-insertion Sprint 34**, now **Sprint 35** (the Sprint-34 insertion renumbered it). So the row-34 continuation (a Day-12 close task, mirroring S33's) must **(1) reconcile the theme** — row 34 = "S33 carryforward — mine head-offset dual / sarf symbolic-emit / fawley 2nd-index + forcing / max-convention bound-transfer / camcge Walras [Epic 5] + rocket PATH [Sprint 35]"; **(2) fill the cells** in the rows-28–33 format (Theme / Headline KPIs at close / Firm landing(s) / REPLAN'd → carryforward); **(3) add a row 35** for the renumbered Quality/PATH theme.

---

## §4. Known-Unknowns dispositions

| Unknown | Summary | Disposition |
|---|---|---|
| **6.1** | ganges/gangesx single `$141/$145/$149` root vs sample's `$140` | ✅ VERIFIED — **live-confirmed**: ganges + gangesx have the identical profile (`$141`×15 / `$145`×3 / `$149`×9), the NaN-sanitization guard on declared-but-unassigned params (assignment depends on `dst.l`); a single fix may recover both; **distinct** from sample's `$140` (pruned-var `.l`-init, sample fix a no-op). Fix surface = the sanitization pass (a hypothesis); `--resolve-changed`-gated. |
| **6.2** | agreste genuine CASE_B or double-`solve` artifact | ✅ VERIFIED — **live-confirmed**: two `solve agreste maximizing yfarm` (lines 294/298); the CASE_B `stat_sales` rel 2.0 is likely a driver-doubling artifact — **scope-verify the single-solve harness scoping before treating it as an emit bug** (document + defer if a false CASE_B). |
| **6.3** | the failure-cohort is multi-root (verify per-model) | ✅ VERIFIED — the cohort is multi-root (sample `$140` ≠ ganges/gangesx `$141/$145/$149`); verify per-model, do not batch (the S33 lesson). The residual cohort each needs its own compile-diagnosis. |
| **7.1** | shape12/shape13/fawley fixtures fail-before/pass-after, gated on P1/P2/P3 | ✅ VERIFIED — the catalog is at shapes 1–11; the three fixtures (+ a P4 bound-transfer fixture) follow the `test_sample_pruned_var_l_init.py` pattern, land only once their track lands, and are deferred if the track REPLANs. |
| **7.3** | Epic-4 `SUMMARY.md` row-34 format + Day-12 continuation | ✅ VERIFIED — row 34 currently holds the **pre-insertion** Quality/PATH theme (now Sprint 35); the Day-12 continuation reconciles the theme (row 34 = the S33 carryforwards), fills the rows-28–33-format cells at close, and adds a row 35. Genuine-floor recompute maintains anchor **75**. |

---

## §5. Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_34/TOOLING_AND_BACKLOG_ANALYSIS.md && echo present
# the ganges/gangesx root + the agreste scope + the multi-root confirm:
grep -qiE '\$141.*\$145.*\$149|141.*15|NaN-sanitization' docs/planning/EPIC_4/SPRINT_34/TOOLING_AND_BACKLOG_ANALYSIS.md && echo "ganges root present"
grep -qiE 'double-.solve.*294|lines 294' docs/planning/EPIC_4/SPRINT_34/TOOLING_AND_BACKLOG_ANALYSIS.md && echo "agreste scope present"
grep -qiE 'multi-root' docs/planning/EPIC_4/SPRINT_34/TOOLING_AND_BACKLOG_ANALYSIS.md && echo "multi-root present"
# the P7 fixtures + anchor-75 + SUMMARY row-34:
grep -qiE 'shape12|shape13' docs/planning/EPIC_4/SPRINT_34/TOOLING_AND_BACKLOG_ANALYSIS.md && echo "P7 fixtures present"
grep -qiE 'anchor 75|anchor \*\*75' docs/planning/EPIC_4/SPRINT_34/TOOLING_AND_BACKLOG_ANALYSIS.md && echo "anchor-75 present"
```

---
**Document Status:** ✅ Complete — Sprint 34 Prep Task 10 (docs-only)
**Last Updated:** 2026-07-19 · **Owner:** Sprint 34 prep (tooling/infra)

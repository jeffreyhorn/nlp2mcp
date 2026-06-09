# Sprint 27 Retrospective

**Sprint window:** 2026-06-01 (Day 0) → 2026-06-08 (Day 13)
**Anchor SHA:** `148662a5`
**Final metrics (142-model GAMSlib corpus):** Parse 142 · Translate **135** · Solve **105** · Match **62** · Tests **4,779** · Determinism **byte-identical ×3 seeds** ✅
**Headline outcome:** Translate / Parse / Tests / Determinism targets **met**; Solve / Match **missed** by exactly the work formally carried forward to Sprint 28. No silent regressions across the sprint.

---

## What Went Well

1. **Phase 0 acceptance gates (PR20) repeatedly caught mis-scoped prep work _before_ wasted implementation.** Days 0, 6, 11, 12 each found that the prep-doc fix surface was wrong, and the Phase-0 prototype-before-production discipline turned those into cheap REPLANs instead of expensive reverts:
   - Day 0: Priority 3 (#1390, #1393+#1335) Approach C proven **inert** (byte-identical emit, no `src` diff) — redirected to the `stationarity.py` layer.
   - Day 11: #1388 prep named the boundary guards; the §4.6 discriminator proved those **inert** and surfaced a *different* bug (#1424).
   - Day 12/13: #1224 and #1374 prep both named AD/Jacobian surfaces; the real fixes were in `src/ir/ast.py` (emit render) and `src/emit/emit_gams.py` (the suppressed-fx restore path).

2. **A reusable bug class was identified and exploited twice.** The "**embedded NLP pre-solve diverges from standalone**" pattern under `--nlp-presolve` (the `$include` under `$onMultiR` re-running source statements) drove two wins: Day 9 **launch → match** (double-applied self-referential param #1378) and Day 11 **camshape #1424** (dynamic-subset blanket corruption). The GDX warm-from-good-optimum experiment became a standard tool for proving a target objective is a valid MCP KKT point.

3. **Determinism held end-to-end.** The Day-10 and Day-13 retests were byte-identical to committed (Solve/Match sets), and the final 3× `PYTHONHASHSEED` retest was byte-identical modulo wall-time — the pipeline is reproducible, and #1400 removed the last machine-portability leak in `mcp_file_used`.

4. **Net-new bug discovery during investigation.** #1424 (dynamic-subset blanket corruption — the emitted MCP was solving the *wrong problem* for camshape/cclinpts) was found while running the #1388 discriminator and shipped with zero regression (16 goldens, all matches re-solved identical).

5. **Disciplined "measure, don't sweep" at checkpoints.** Day-10 and Day-13 retests deliberately committed the DB + only fix-changed goldens, reverting incidental presolve-retry/staleness regens — keeping checkpoint diffs honest.

## What We'd Do Differently

1. **Stop trusting prep-doc `file:line` fix surfaces; treat them as hypotheses.** Across Days 0/6/11/12/13 the named surface was wrong more often than right (the real surfaces were `stationarity.py`, `src/ir/ast.py`, the emit restore pass — not the AD `_try_eval_offset`/`constraint_jacobian` sites the prep named). Prep should record the *symptom + reproducer* and defer the surface to a Day-0 trace.

2. **The Day-0 Solve/Match projections were over-optimistic.** The "+6 firm Match" assumed fawley/otpop/camcge would land; all three went `model_infeasible` (forward bucket moves needing deferred work). Future projections should distinguish "bucket-forward" moves from genuine Solve/Match gains.

3. **Golden staleness accumulated silently.** Several `*_mcp.gms` / `*_mcp_presolve.gms` goldens (cesam/fawley/korcge/dinam) were stale vs current emit, surfacing as noise in unrelated PRs (Days 9/10/13). A periodic golden-refresh sweep (or a CI staleness check) would prevent this.

4. **Day 12 was over-packed**, forcing #1224 to consume the whole day and slipping #1400/#1374 to Day 13 (then #1374's `.l` shape to Sprint 28). Multi-bug models (camshape, cclinpts) repeatedly proved larger than their single-line prep estimates.

## Sprint 28 Recommendations

1. **Parameter-valued-offset KKT cross-term (#1224, highest-leverage Solve).** mine now translates but is `model_infeasible` because `stat_x` doesn't invert the parameter-valued offset (`sum(k, lam_pr(k,l,i,j))` should be `sum(k, lam_pr(k,l,i-li(k),j-lj(k)))` minus the `l-1` term). This is the AD/Jacobian inversion the #1224 prep named.

2. **camshape #1388 Case-(b) `stat_r` divergence** — per-term hand-derivation vs emit at `stationarity.py:1835` (#1424 already landed; this is the remaining +1 Solve).

3. **otpop #1393+#1335** — the `stationarity.py` symbolic-collapse path + `_try_eval_offset` `card(t)-ord(t)` evaluator (now confirmed distinct fixes). Unblocks otpop's Solve/Match.

4. **cclinpts #1387** — the three coupled changes (AD offset-enumeration + gradient→stationarity re-symbolization anchor + non-convex warm-start), per the Day-6 binding diagnosis.

5. **kand #1390** — re-diagnose the true 195.0-vs-2613.0 mismatch source (the phantom-term collapse is proven inert).

6. **camcge** singular-Jacobian CGE degeneracy (separate from Pattern C).

7. **Lower-priority cleanups:** #1374 `.l` denominator/override dedup (robot); #1400 `message`-field captured-warning path relativization; #1385 runtime-guard cross-terms; golden-staleness sweep + CI check.

## KU Coverage Summary

All Sprint 27 Known-Unknowns were resolved across Days 0–13 (verdicts recorded in `KNOWN_UNKNOWNS.md`):

- **Cat 1 (#1398 Phase A gate):** 1.1–1.4 ✅ (Days 0–1) — canonical-set identity sufficient; no positional info needed.
- **Cat 3 (#1390 / #1385 / #1393+#1335):** 3.1–3.5 — binding REPLANs Day 0/5; #1385 SCOPED-PROCEED (translate-only); #1390 + #1393+#1335 → Sprint 28.
- **Cat 4 (#1378 launch):** 4.1 ✅ (solver-tunable; match via the double-apply fix) · 4.2 ✅ (byte-stability anchor preserved — presolve-only fix).
- **Cat 5 (#1356/#1357 comp_up):** 5.1–5.3 ✅ (Day 5; single-file change; clearlak byte-stable).
- **Cat 6 (#1224 mine):** 6.1 ✅ STANDALONE · 6.2 ✅ next failure mode = `model_infeasible`.
- **Cat 7 (#1387 / #1388):** 7.1–7.3 — both multi-bug → Sprint 28; #1424 split out and fixed; the §4.6 3-way discriminator classified camshape Case (b).
- **Cat 8 (#1400):** 8.1 ✅ (second leak = `message` field) · 8.2 ✅ (PROJECT_ROOT-relative).
- **Cat 9 (#1374):** 9.4 ✅ (3 models / 13 dups / 2 shapes; dominant `.fx` shape fixed).

## Process Recommendations Delivery (PR20–PR23)

| Rec | Description | Status |
|---|---|---|
| PR20 | Phase 0 acceptance-gate codified + backlog issue sections | ✅ delivered in prep; **heavily exercised** — caught 4 mis-scopes |
| PR21 | Prep-task end-to-end emit verification template | ✅ delivered in prep |
| PR22 | Mid-sprint audit script (`changed_emit_artifacts.py`) | ✅ delivered in prep; used Days 5/10/13 |
| PR23 | CI-workflow PR self-review checklist | ✅ delivered in prep |

## Related Documents

- `docs/planning/EPIC_4/SPRINT_27/SPRINT_LOG.md` (per-day entries + final metrics)
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` · `KNOWN_UNKNOWNS.md` · `PRIORITY_{1,3,5,7}_*.md`
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 27"
- Sprint 28 carryforward issues: `docs/issues/ISSUE_{1390,1393,1335,1387,1388,1224,1374,1400,1424}_*.md`

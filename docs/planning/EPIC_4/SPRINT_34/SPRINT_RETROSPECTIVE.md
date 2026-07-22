# Sprint 34 — Retrospective

**Weeks 33–34** · code anchor S33 close `750803b2` · DB byte-anchor `750803b2` (byte-unchanged all sprint)

## 1. Outcome vs targets

| Target | Result |
|---|---|
| Solve ≥ 109 (stretch ≥ 110) | ✗ **108** (flat — every mover REPLAN'd/deferred) |
| Match maintain ≥ 93 | ✓ **93** |
| genuine floor ≥ 76 | ✗ **75** (maintained; the ≥ 76 step missed) |
| Translate ≥ 135 | ✓ **135** |
| model_infeasible ≤ 7 | ✓ **7** |
| Determinism ×3 `{0,1,42}` | ✓ byte-identical |
| No regression (`--resolve-changed`) | ✓ **GO** (DB byte-unchanged) |

**Full modal-flat close — 0 bucket moves.** This is *exactly* the Task-9 honest projection (authored Day −1): every in-sprint Solve/floor mover was a from-scratch AD/emit track with a High/Medium-High REPLAN prior, so a flat close was the modal outcome. The sprint delivered its **de-risking** value, not a KPI gain.

## 2. What landed (firm)

- **P4 — sense-aware bound-transfer sign (Option B).** The one `src/` landing: the `--nlp-presolve` bound-multiplier warm-start transfer is now objective-sense-aware (`= abs(var.m)` at the active bound for MAXIMIZE, dropping the min-convention sign gate; MINIMIZE byte-identical). A **general warm-start-correctness fix** (improves the presolve-recovery substrate) with **no +Solve** — the agreste survey confirmed the sole open MAXIMIZE candidate is structural (MS-5), the a-priori documented outcome. Guarded by the Day-12 fail-before/pass-after fixture. 11 presolve goldens regenerated; `--resolve-changed` GO.
- **P7 — the P4 fixture + the floor-75 recompute + the Epic-4 SUMMARY row-34.** Additive tests + docs; `make test` 5037 passed.

## 3. What we'd do differently / key lessons

- **The prep fix-surface hypotheses were optimistic — again.** P6's "ganges/gangesx share one `$141/$145/$149` root; one fix recovers both" was **substantially wrong**: three independent roots, no model recovers from `$141` alone, and the deepest (`$149`) is a CES/LES product-rule stationarity AD bug. This re-confirms the standing lesson (prep `file:line`/root hypotheses are wrong ~half the time — verify per-model at execution). The corrected multi-root diagnosis is the day's real product.
- **"No bucket → no `src/`" held under temptation.** The P6 `$141` fix was correct and *verified* — but banked, because it recovered 0 bucket and touched only slow-emit CGE goldens un-regenerable in the CI budget (shipping would leave stale goldens). The discipline (consistent with P1/P2/P3/P5) avoided golden churn + regression risk for no gain. P4 was the exception that *proves* the rule: it shipped because its goldens were fast, regenerable, and `--resolve-changed` GO.
- **Control/harness-first discipline continued to prevent bad ships.** P1's cold-MS-1 control refuted H_dual before any `src/`; the P6 `$141` fix was verified *then* reverted; every disposition ran its `/tmp` or compile control first. Zero broken code across the sprint.
- **The genuine-floor ramp remains conditional, not independent +1s** (the Sprint-30 §3 lesson, borne out again). The ≥ 76 step needed a genuine *cold-emit* mover (mine or fawley); both REPLAN'd/deferred; a warm-start fix (P4) yields 0 floor by definition. Flat-75 was the modal outcome the projection named.

## 4. Sprint 35 / Epic 5 carryforwards

All filed in `SPRINT_35_CARRYFORWARDS.md` — each a de-risked, control-confirmed, precisely-pinned hand-off:
- **mine** — head-offset dual subsystem (P1; H_dual refuted, `x.m=0`-degenerate boundary — needs a dual-architecture rethink).
- **sarf** — symbolic `stat_task` emit mode (P2; a corpus-wide re-architecture of `enumerate_variable_instances`, 20–28 h dedicated).
- **fawley** — the qsb/pbal constraint-index-diagonal `sameas` correction (P3; H-b, ~1430-line surface; the +Solve is a forcing tail).
- **the P6 `$141` fix + the ganges `$149` CES/LES AD bug** — the verified-and-banked NaN-cleanup fix + the deep product-rule stationarity blocker (gates ganges/gangesx/dinam/indus/turkpow/clearlak) + turkey's `$161` set-emit root.
- **camcge** — the dual-consistent Walras numéraire (→ Epic 5; detector cohort + numéraire recipe banked).
- **rocket** — the FINALIZED PATH-consultation input (→ the Sprint-35 author consultation).

## 5. Process notes

- **8 day-execution PRs (#1574, #1577, #1578, #1579, #1599, #1600, #1601 + the Day-4 #1596), zero broken code.** The one `src/` change (P4) passed the full gate (typecheck/format/lint/test) + determinism ×3 + an 11-golden `--resolve-changed` GO. Every emit-touching disposition ran a control **before** any `src/`.
- **The Task-9 modal-flat projection was accurate to the bucket.** Naming the honest flat-KPI outcome up front kept the sprint focused on de-risking + banking rather than forcing a bad ship — the recurring PR24/PR27 discipline.

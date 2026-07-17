# Sprint 33 — Retrospective

**Sprint:** 33 (S32 carryforward) · **Weeks 31–32** · **Closed:** 2026-07-17
**Code anchor:** S32 close `ee51ed9e`

## 1. Outcome vs targets

| Metric (142 corpus) | Day-0 | Close | Target | Verdict |
|---|---|---|---|---|
| Solve | 107 | **108** | +1 conditional | ✅ (via P6, not the projected P1/P3) |
| Match (as-measured) | 92 | **93** | ≥ 92 | ✅ |
| genuine floor | 74 | **75** | ≥ 75 | ✅ |
| Translate | 135 | 135 | +1 (P2) | ✗ (sarf REPLAN, Option B) |
| model_infeasible | 7 | 7 | ≤ 7 | ✅ |
| path_syntax_error | 8 | **7** | ≤ 8 | ✅ |

**One genuine bucket move (P6 sample: +1 Solve / +1 Match / +1 genuine floor), meeting the floor ≥ 75 target. Zero broken code shipped across 8 execution PRs.**

## 2. What landed (firm)

- **P6 sample — the sprint's only in-sprint bucket move.** A `path_syntax_error` emit bug: the variable-init pass passed through an expression `.l` init (`c.l = sum(h, data(h,"cost")*n.l(h))`) referencing a variable (`n`) **pruned** from the MCP (sample's last solve translates the `nr` reciprocal model, not the `n` original). Fix: skip such an init when its `.l`-refs aren't a subset of the *declared* MCP variables (`kkt.stationarity`), not the broader `kkt.referenced_variables`. A genuine cold-emit correction → +1 Solve / +1 Match / +1 genuine floor. Guarded by a fail-before/pass-after fixture (P7).
- **Six precisely-characterized Sprint-34 hand-offs** (§4), each control-confirmed.

## 3. What we'd do differently / key lessons

1. **The Task-9 honest projection was borne out — and then beaten by the designated fallback.** All three deep tracks (P1 mine, P2 sarf, P3 fawley) resolved with no in-sprint bucket — exactly the modal-flat-KPI projection. **But P6, which Task 9 named the best-remaining-shot, delivered the +1.** The lesson from Sprint 32 ("the value is the de-risking, not the bucket") held for the deep tracks, *and* the front-loaded-REPLAN → freed-budget → P6 reallocation worked exactly as designed: the deep REPLANs surfaced by Day 6, freeing the back half for the P6 win.
2. **Control-first caught two more banked premises before any bad ship (PR24/PR27).** P1's H1 was **value-invariant** — proven by a `/tmp` control (`d_N` = `d_Nh1` row-for-row) *before* any `src/` change; a from-scratch re-derivation would have chased a fix that cannot exist. P3's fawley reached **H-b** (MS-5 persists even with the warm residual closed) via the same control. Both were dispositioned on evidence, not hope. **This is the sprint's real discipline product.**
3. **A new cross-cutting finding the prep didn't anticipate: the max-convention bound-transfer-sign gap.** The `piL_*/piU_*` warm-start transfers are gated on min-convention `.m>0`/`.m<0`; for a MAXIMIZE solve they skip correctly-signed multipliers — surfaced in **both** fawley (`bq.m<0` at a lower bound) and mine (upper-bound multipliers). For fawley it doesn't unlock the solve (H-b), but it may be a genuine +Solve lever on *other* max models whose divergence is warm-residual-driven. Candidate Sprint-34 track.
4. **Deferring a genuine-but-no-bucket fix on a high-blast-radius path is the right call (P3 Day 5, P2 Day 6).** The fawley sameas correction and the sarf symbolic-emit subsystem are both real and worth doing — but shipping a change to a ~1400-line / three-layer general emit function for zero in-sprint bucket, in a flat-KPI sprint, is poor risk/reward. Both deferred to focused Sprint-34 efforts with full regression rigor. Deliberate, not a correctness REPLAN.
5. **The failure cohort is a genuine bucket source — but multi-root.** The `path_syntax_error` cohort (8 models) was *not* a single shared root: sample (`$140`, pruned-var `.l`-init, 2-model structure) recovered; ganges/gangesx (`$141/$145/$149`, bound-clamp/param-assignment, referenced vars declared) are a different root, banked. **Verify per-model, don't assume a shared root** (the earlier "single fix may recover several" hypothesis was only partially right).

## 4. Sprint 34 / Epic 5 carryforwards

Filed in `SPRINT_34_CARRYFORWARDS.md`. Six de-risked hand-offs:
1. **mine head-offset dual subsystem** (P1) — H1 refuted; the residual is a deeper head-offset dual-architecture gap (22-row breadth, `x.m=0` `c`-boundary degeneracy). `DAY2_MINE_REPLAN.md` + `MINE_CROSSTERM_DESIGN.md`.
2. **sarf symbolic-emit subsystem** (P2) — the three-site O(active) parametric emit mode. `DAY6_SARF_ASSESSMENT.md` + `SARF_EMIT_SUBSYSTEM_DESIGN.md`.
3. **fawley sameas correction** (P3) — the constraint-index diagonal fix in `_add_indexed_jacobian_terms` (control-proven 473→18.468). `DAY4_FAWLEY_CONTROL.md`.
4. **The max-convention bound-transfer-sign track** (NEW) — general warm-start-transfer gap (shared mine/fawley); check as a +Solve lever on other max models.
5. **camcge dual-consistent Walras** → Epic 5 (step 1 landed S32). `CAMCGE_WALRAS_DESIGN.md`.
6. **rocket PATH-consultation input** → the Sprint-34 consultation; hhfair/CGE + cesam/lnts documented Case-c. `ROCKET_CASEC_FORCING_PLAN.md`.
- **Banked P6:** ganges/gangesx `$141/$145/$149` translate-syntax root; agreste CASE_B scope-verify (scenario driver).

## 5. Process notes

- **8 execution PRs (#1573–1580), zero broken code**; every emit-touching disposition ran a `/tmp` or harness control **before** any `src/` change. The one `src/` change (P6 sample) passed the full gate (typecheck/format/lint/test) + determinism ×3 + a sample-only blast-radius confirmation.
- **Git gotcha:** a `git stash pop` during a fail-before demo popped a *pre-existing* stash into a 50-file `UU` conflict; `git reset --hard HEAD` cleaned it (committed fix safe, untracked survives). Avoid stash operations mid-execution.
- **The prep paid off:** Task 8's Phase-0 gates + Task 9's honest projection + Task 10's P6 cohort scoping meant every day started against a spec, and the flat-KPI-modal reality was expected, not a surprise.

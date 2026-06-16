# Sprint 28 Per-Day Execution Prompts

One self-contained prompt per day. Each states **only the day's scope** — no forward-looking claim about work not yet done (the Sprint 27 stale-prompt failure mode). Run the day's prompt, then the next day's.

## How to Use

Paste the day's prompt. It names the day's scope, the Phase-0 gate(s) to clear, the KKT-residual harness invocation where relevant, and the stale-assumption reminder. The detailed rationale is in `PLAN.md`.

## Cross-Cutting Rules (every day)

- **PR24:** the fix surface is whatever the **Day-0 trace** established (the `Traced Fix-Surface (Day-0)` line in the issue's Phase-0 gate) — never the prep-doc guess. A PROCEED that cites only the prep surface is invalid.
- **Quality gate before every commit:** `make typecheck && make format && make lint && make test`.
- **Emit-touching PRs:** include the regenerated `.gms` diff (PR14) and pass the golden-staleness check (PR26).
- **Flag stale assumptions:** if anything in this prompt or the issue's Phase-0 gate contradicts what you find, STOP and correct the doc before proceeding — do not implement against a stale assumption.
- **PR25:** when reporting a Solve/Match delta, label it genuine bucket-to-success vs bucket-forward; only genuine counts toward the target.

---

## Day 0 Prompt — Kickoff + Day-0 Traces (~8 h)

Confirm the Day-0 baseline equals Sprint 27 final (reuse the committed `gamslib_status.json` unless `main` changed since the Day-13 retest; see `BASELINE_METRICS.md`). Land the one-time golden refresh: `make regen-goldens`, then commit the 4 drifted presolve goldens (camshape/cesam/fawley/korcge) as a single reviewable commit, separate from any fix. (Heads-up: the refreshed `korcge_mcp_presolve.gms` faithfully reproduces a current-emit bug — its `--nlp-presolve` variant aborts EXECERROR=5 — tracked in `docs/issues/ISSUE_1439_*.md`; **not a blocker** since korcge solves via the non-presolve file, and **not a refresh regression**.) Then run the **Day-0 traces (PR24)** for mine, camshape, otpop, cclinpts, kand, camcge: instrument the candidate surfaces, emit each `<model>_mcp.gms`, locate the offending row, and **fill the `Traced Fix-Surface (Day-0)` line in each issue's Phase-0 gate** with the confirmed `file:line` + evidence. Restate the PR25 Day-0 projection tally (firm Solve +3 + camcge conditional; Match +3). Do NOT start any `src/` fix today.

## Day 1 Prompt — KKT-Residual Harness build (start) (~4 h)

Begin building `scripts/diagnostics/kkt_residual.py` per `PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md`: the CLI (`<model.gms> [--gdx <solution.gdx>] [--tol 1e-6] [--json <out.json>] [--nlp-solver <name>] [--no-cold-start]`) and the dual-transfer mechanism (nu/lam/piL/piU via `build_complementarity_pairs`; the inequality→`comp_*` generalization; the constraint-row consistency self-check that returns `dual_transfer_inconsistent`). Unit-test the dual transfer on a known-good case (launch).

## Day 2 Prompt — KKT-Residual Harness build (verdict + output) (~4 h)

Implement the Case-(a/b/c) verdict (stationarity residuals only, after the §2 self-check passes; `tol=1e-6`; the optional cold-start comparison for a-vs-c, skippable via `--no-cold-start`) and the JSON + human output. Wire `--gdx` to skip the NLP solve.

## Day 3 Prompt — KKT-Residual Harness validate + land (~4 h)

Validate against the three known cases: launch → Case a; camshape → Case b (`stat_r('i1')` ≈ 396); cclinpts → Case c (max\|r\| = 5e-8, cold PATH diverges). Reference the harness command from the Phase-0 `### Verification Methodology` template (PR27). Open the P9 PR. This verifies Unknowns 9.1/9.2/9.3.

## Day 4 Prompt — Priority 1: #1224 mine (~11 h)

Clear the `ISSUE_1224` Phase-0 gate: run `kkt_residual.py data/gamslib/raw/mine.gms --gdx mine_nlp.gdx` → confirm **Case b** with `stat_x(l,i,j)` as the max-residual row. At the **traced** surface, implement the inverted parameter-valued offset (`sum(k, lam_pr(k,l,i-li(k),j-lj(k))) − sum(k, lam_pr(k,l-1,i,j))`); check boundary cells (clip vs guard, Unknown 1.3). Target: mine MODEL STATUS 1 (**+1 Solve**). Open the PR with the emit `.gms` diff + golden-staleness pass.

> **[Day-4 outcome]** `stat_x` inverted-offset fix **landed** (PR #1444, gated, byte-stable). mine did **not** reach MS 1 — a deeper head-domain-offset mis-emit (`pr(k,l+1,i,j)`) leaves the convex-LP MCP infeasible; a time-boxed probe confirmed it's systemic → **+1 Solve REPLAN'd to Sprint 29 (#1443)** (findings: PR #1445). Solve forecast revised in `PLAN.md` §1/§2 (firm path now 107; ≥ 109 at-risk); targets unchanged.

## Day 5 Prompt — Checkpoint 1 + Priority 2: #1388 camshape (~10 h)

**Checkpoint 1:** pipeline retest (`changed_emit_artifacts.py --since-commit <Day-0 SHA>`) + golden-staleness check; report the PR25 tally (genuine gains so far). Then clear the `ISSUE_1388` gate: harness → Case b (`stat_r('i1')` ≈ 396, post-#1424 warm-start valid); implement the per-term `stat_r` fix at the traced surface. Target: camshape MS 1, area ≈ 4.2841 (**+1 Solve**).

## Day 6 Prompt — Priority 3a: #1393 otpop kdef Sum-collapse (~7 h)

Clear the `ISSUE_1393` gate. At the traced `stationarity.py` symbolic-collapse surface, fix the over-counted `kdef` cross-term to the single `$(t(tt))`-guarded form (no `sum(t__, …)`). Verify with the harness + the structural grep (**regenerate the MCP to `/tmp` first**, then grep — do not grep the committed golden). Companion #1335 lands Day 7.

## Day 7 Prompt — Priority 3b: #1335 otpop zdef cross-term + close (~7 h)

Clear the `ISSUE_1335` gate. Extend `_try_eval_offset` (Approach B) to resolve `card(t)-ord(t)` symbolically so `nu_zdef` appears in `stat_p` with the `sameas(tt,'1990')` guard, without regressing other models' offset handling. Target: otpop cost ≈ 4217.80 (**+1 Solve + 1 Match**). Open the combined otpop PR.

## Day 8 Prompt — Priority 4: #1387 cclinpts — Task-6 gate + implement (~11 h)

**Task-6 decision pivot first (Unknown 4.1):** re-run the Day-6 `_diff_sum` offset-enum prototype on current `main` to re-confirm the anchor blocker; trace the re-symbolization callers. **If the anchor fix is local (gateable to the differentiated variable's column index) → PROCEED.** **If architectural (touches all callers) → REPLAN to Sprint 29:** file a re-scoped Phase-0 successor, do NOT commit `src/`, and skip to Day 10's work. Sign-flip stays a misdiagnosis. If PROCEED, begin the three coupled changes (AD offset-enum + anchor fix + non-convex warm-start) — they land together.

## Day 9 Prompt — Priority 4: #1387 cclinpts close (or REPLAN closeout) (~7 h)

If Day 8 PROCEED'd: finish the three coupled changes; harness re-check; target cclinpts rel_diff < 1% (**+1 Match**); open the PR (full-corpus byte-stability + golden-staleness). If Day 8 REPLAN'd: confirm the Sprint 29 re-scoped filing is complete and the tree is clean; reallocate the freed time to Day 10/11 slack.

## Day 10 Prompt — Checkpoint 2 + Priority 5: #1390 kand — Task-6 gate (~10 h)

**Checkpoint 2:** pipeline retest + golden-staleness + PR25 tally. Then **#1390 kand (Task-6 gate):** confirm the NLP reference 2613.0 (Unknown 5.3); run the harness — the dual-transfer self-check (tree-conditioned `lam_dembalx`, Unknown 5.2) must pass first. **Case b (a localizable `bal`/`x`/lag-duality row) → PROCEED** to the fix at the traced surface; **Case c (LP first-stage/recourse coupling) → REPLAN to Sprint 29** (re-scoped Phase-0 filing). Phantom-term collapse stays out of scope. Target if PROCEED: kand 2613.0 (**+1 Match**).

## Day 11 Prompt — Priority 6: camcge — Task-6 gate + Priority 7 cleanups (~10 h)

**camcge (Task-6 gate, Unknown 6.1):** run the harness (expect Case c, KKT structurally correct); read the PATH listing basis-singularity report + a Jacobian rank check at the NLP point. **Single redundant Walras row + a numéraire fix that preserves the economic solution → PROCEED (+1 Solve conditional); otherwise REPLAN to an Epic 5 inherent-degeneracy observation.** Then **P7 cleanups:** #1374 robot `.l` dedup (suppress the override when it matches the denominator-init `.l`) + #1400 message-field relativization (a repo-relative `warnings.formatwarning` in `src/cli.py`, or relativize the captured text). **#1385 only if slack remains** (it is the atomic re-emit + symbolic-instance cross-terms, ~6–10 h — defer to Sprint 29 if Day 11 is tight).

## Day 12 Prompt — Priority 8 golden-staleness CI + Priority 10 divergence/property tests (~10 h)

**P8 (Task 7):** build `scripts/sprint_audit/check_golden_staleness.py [--fix]`, the `.github/workflows/golden-staleness.yml` job (parallel regen; `src/{ad,kkt,emit,ir}/` trigger; the 6-model allowlist), and `make regen-goldens`; measure the CI runtime (Unknown 8.2). **P10 (Task 8):** build `scripts/diagnostics/check_presolve_divergence.py` and **replay #1378 + #1424 pre-fix as the acceptance test** (both must FLAG); **also exercise korcge (#1439)** — its `--nlp-presolve` variant aborts EXECERROR=5 from the it/in + `.fx`-before-`$include` ordering bug, a concrete divergence-class case the detector should catch (see `docs/issues/ISSUE_1439_*.md`). Build the 6 AD cross-term property tests under `tests/integration/emit/` (`@pytest.mark.integration`). Both CI-wired.

## Day 13 Prompt — Final Retest + Closeout (~8 h, tight)

Run the **final 3× `PYTHONHASHSEED` retest** (PR12) + the golden-staleness check; confirm byte-identical (modulo wall-time). Write the **PR25 final projection tally** (realized Solve/Match vs ≥110/≥65, each delta genuine vs bucket-forward). Author the `SPRINT_LOG.md` final entry + `SPRINT_RETROSPECTIVE.md`; file the Sprint 29 carryforwards for any REPLAN'd track (#1387/#1390/camcge/#1385 as applicable). Do not start new `src/` work.

---

## Pipeline Retest Cadence (Days 5, 10, 13)

Day 5 (Checkpoint 1), Day 10 (Checkpoint 2): `changed_emit_artifacts.py --since-commit <Day-0 SHA>` + golden-staleness + PR25 tally. Day 13: full 3× `PYTHONHASHSEED` retest + final PR25 tally.

## Related Documents

- `PLAN.md` (the detailed schedule + budget + risk register)
- `KNOWN_UNKNOWNS.md`, `BASELINE_METRICS.md`, the six Phase-0 gates, and the Task 4/6/7/8/9 design docs (see `PLAN.md` §18).

# Sprint 40: Per-Day Execution Prompts

**Written by** Prep Task 12 · **2026-10-17** · companion to `../PLAN.md` (schedule, REPLAN exits §3, checkpoints §4, close rules §5)

## Standing conventions (every day, every review round)

**Every day:**
1. Branch `planning/sprint40-dayN-<slug>` from `main` and do the work.
2. Run the **quality gate if any `*.py` changed anywhere in the final PR**: `make typecheck && make format && make lint && make test`.
3. Commit, push, and open a PR.
4. Wait for review, and reply to each comment **on its own thread**.

**Re-derive the gate condition before every push**, review rounds included. A review round that adds a script flips a waived PR into one that owes the gate:

```bash
PY=$(git diff main...HEAD --name-only | grep -c '\.py$') || true
if [ "$PY" -gt 0 ]; then echo "$PY .py file(s) changed: QUALITY GATE REQUIRED"; else echo "0 .py: gate may be waived"; fi
```

- Run it **after committing**. It reads `main...HEAD`.
- State a waiver over the stable scope, *"`src/` and `tests/` untouched"*, **never** as "no `*.py` changed".

**No attribution, anywhere.** Check both places:

```bash
if git log -1 --format=%B | grep -qE "Co-Authored-By|Generated with"; then echo "ATTRIBUTION IN COMMIT"; exit 1; fi
if grep -qE "Co-Authored-By|Generated with" /tmp/pr-body.md; then echo "ATTRIBUTION IN PR BODY"; exit 1; fi
gh pr create --base main --head <branch> --title "<title>" --body-file /tmp/pr-body.md
```

Use `if`, not `&&`: `grep -q` exits 1 on no-match. Use `-E` with `|`, not a BRE `\|`.

**The PR body is a pointer** (Sprint 39 retrospective §7.4):
- Write it as *"see `SPRINT_LOG.md` §Day N"*, plus anything that cannot rot.
- At the end of every review round, regenerate it from the docs or re-check it: `gh pr view <N> --json body -q .body > /tmp/pr-body.md`.
- Once P10d lands (Day 12), also run `make check-doc-figures TEXT=/tmp/pr-body.md`.
- **Never patch the body per round.**

**A figure is stated once, with the commit it was measured at** (close rule **C6**):
- Derive it with `scripts/sprint_audit/kpi_block.py` and `scripts/sprint_audit/floor_tracker.py`. The mechanical DB count yields 65 and looks authoritative; it is not the floor.
- Run `make check-doc-figures` before every push.

**The leak gate runs ALONE.** Never start it in the same command as `make test`, or beside any other GAMS run.
- Contention causes **timeouts**, and before P10c the plain sweep reports them as *"All in-scope goldens clean (N … unverified)"* with rc 0. That is a claim over fewer models than the scope.
- From Day 1 on, `make check-goldens` derives `--min-scope` and passes `--fail-on-unverified`.
- Before then, read the summary line: **any `TIMEOUT` line means the run is not a pass.**

**Review-round rules** (P10e, recorded here and in CONTRIBUTING on Day 12):
- **Pin by identity, not count.** A test or a claim about "N of M" names the set. Ask which swap preserves N.
- **When a classification moves, sweep the changed SET.** Grep every claim mentioning a member of the moved set, not just the flagged line.
- **Never `git stash` to switch branches.** Use `git show <ref>:<path>` or `pytest --collect-only`; both are read-only.
- **After any round that changes `src/`, grep the PR's own docs** for every symbol name they mention and re-read those lines. A doc written before a review round describes the code that was replaced.

**License hygiene** (P1 onward):
- Never commit license-file content, `USER:`/licensee lines, license IDs, node, memory or core data. Record only the **edition class** (`licensed` / `demo` / `null`).
- Scan every diff before committing, plus a manual read of any `.lst`-derived text. Use Python, because the lookahead needs PCRE and macOS `grep` has no `-P`:

  ```bash
  git diff --cached | python3 -c 'import re,sys; h=[l for l in sys.stdin if l.startswith("+") and re.search(r"licensee|USER: (?!GAMS Demo,)", l, re.I)]; print("".join(h) or "clean"); sys.exit(1 if h else 0)'
  ```

  Controls, measured: a `+USER: <licensee>` line gives rc 1, and the generic `+USER: GAMS Demo,` marker gives rc 0. A diff that adds this command line itself will hit on its own regex text. Read the hit; don't suppress it.
- The secret lives only in the `gams-licensed` environment. **No `pull_request` job ever receives it.**
- The repo spelling is **`license`**.

**MINLP/MIP are out of scope:** exclude them, never relax them (`andean`, `nonsharp`).

**GAMS runs go in a scratch directory or a throwaway worktree, never the repo root,** and never `git add -A` after one. Validation tests copy into `tmp_path`.

**`kkt_residual.py`'s `CASE_B` is a refusal, not a caveat.** A presolve match without our MCP's own `MODEL STATUS` is not a match (`check_mcp_solve_attribution.py`).

---

## Day 0 (2026-10-18) — baseline · 2 h · + P1: schema 3.1.0 and its writers · 8 h

Branch `planning/sprint40-day0-schema`.

**Baseline (2 h):**
- Re-derive with `kpi_block.py --format line` and `floor_tracker.py` at HEAD, and record both with the commit.
- Confirm `git diff bd2af6e9 HEAD -- src/ data/gamslib/mcp/` is still empty. If it is not, name what moved before anything else runs.
- **The three owner answers are fixed inputs** (`OWNER_DECISION_BRIEF.md`, committed at `b44344a2`). **Do not re-open any of them.**

**P1, schema 3.1.0 (8 h).** `SCHEMA_3_1_0_DESIGN.md` is the specification.
- Add `license_edition` (`licensed` / `demo` / `null`) to **both** `mcp_solve_result` and `convexity_result`, plus `gams_version` in `convexity_result`.
- **`null` means unrecorded, never a guessed `"demo"`.**
- Add `scripts/gamslib/migrate_schema_v3.1.0.py`, following the v3.0.0 pattern: additive, never overwrites, refuses a second run, writes `_migration_summary_v3_1_0`.
- Update `schema.json`'s `description` "(v3.0.0)", which `test_db_manager.py` reads as the canonical version.
- **All 11 writers W1–W11**, including the three the plan missed:
  - `run_full_test.py::mark_cascade_not_tested` (two `mcp_solve` constructions);
  - `db_manager.py update`;
  - the schema description.
  - ⚠ `update_model_solve_result` and `run_solve_stage` are **fixed-key-list** writers that drop unnamed fields. That is how `mcp_attribution` was lost in Sprint 39.
- **One parser:** `extract_license_edition` + `extract_solver_name` beside `extract_gams_version` in `test_solve.py`, imported by `verify_convexity.py`.
  - The discriminator uses generic markers only: `USER: GAMS Demo,` or the refusal line ⇒ demo; a non-demo `USER:` prefix ⇒ licensed. **Prefix-matched, never captured.**
- `db_manager.py`: `cmd_init --empty` stamps **3.1.0**, and the catalog-init chain gains `migrate_schema_v3.1.0.py`.
- Apply the migration to `gamslib_status.json` in the same PR. Every existing row gets `null`.

**Gate:**
- **Positive control:** the new fields **fail** 3.0.0 validation and **pass** 3.1.0, which still rejects an unknown key.
- One writer test per stage, from a licensed and a demo `.lst` fixture.
- Quality gate.
- `kpi_block.py` byte-identical before and after the migration, because no outcome moves.

**REPLAN exits:** `PLAN.md` §3 P1.

## Day 1 (2026-10-19) — P1: CI, the ledger and the corpus readers · 10 h · + P10: 10c, the leak gate fails on timeouts · 2 h

Branch `planning/sprint40-day1-ci`.

**P1 (10 h).** `CI_LICENSE_DESIGN.md` §3 and §6, and `OWNER_DECISION_BRIEF.md` §Decision 2.

- **Owner action first:** create the `gams-licensed` environment (deployment branches **`main` only**, **no required reviewers**) and store `GAMS_ACCESS_CODE` **there only**, never as a repository secret.
- Land `.github/workflows/licensed-solve.yml`, triggered by `push` to `main`, `schedule` and `workflow_dispatch`. **Never `pull_request_target`.**
  - It activates with `gamsgetkey … || exit 1`.
  - Mask with `::add-mask::`.
  - Scan its own outputs in-job, with a pattern file written from the secret and deleted after. The positive control is the scan run against the license file itself, which must hit.
- **The PR side, same PR:**
  - rename the step to *"Install GAMS (demo edition)"*, keeping the pinned installer and its SHA-256 guard (`CI_LICENSE_DESIGN.md` §6);
  - **replace the raw `gams audit lo=2` print with an edition classification only**, in **both** GAMS-installing PR workflows (`pr19-emit-solve-validation.yml`, `presolve-divergence.yml`). Run a tiny probe, **capture** its listing to a file without echoing it, apply Task 3's discriminator, and print only `edition=demo` / `edition=licensed`. Raw audit output can carry licensee, license-ID, path and node fields, and a CI log is published;
  - teach `run_pr19_solves.py` to detect the demo refusal and report *skipped: over the demo ceiling*, instead of letting six cohort models license-fail as if they were emit failures.
- **Decision 1's ledger:**
  - add the `license_unlocked` list (non-counting, **cold matches only**) to `data/floor_provenance.json`, and make `floor_tracker.py` report **"floor 75 (+*k* license-unlocked, not counted)"**. Presolve-only matches stay under the existing rule and never enter the list;
  - amend the floor definition so a cold license-unlocked match is not read as genuine.
- **Decision 2's readers:** `corpus_admissions.json` + `kpi_block.py --corpus continuity|current`, reporting both denominators. Include the test that `continuity` on today's DB equals `current` (142).
- **`check_doc_figures.py` becomes corpus-aware, before any admission** (`OWNER_DECISION_BRIEF.md` §Decision 2; P3 admits on Day 3). Today it checks headline figures against one fact set, so a **correct** continuity/expanded sentence with different numerators would fail the mandatory pre-push gate the moment W10 admits a model.
  - Derive **both** fact sets (`compute_kpis` over each corpus), each with its KPI denominators.
  - Match a figure written `N/D` to its corpus by `D`; a `D` matching neither corpus is an error.
  - Check a bare figure against **continuity**.
  - Tests: a correct two-clause sentence with differing figures passes; a wrong numerator in either clause fails; a `D` matching neither corpus fails; the equal-denominator case passes; a bare figure is checked against continuity.
  - P10d's `--text` mode (Day 12) does **not** cover this.
- **The danwolfe / decomp check** (Task 6 side finding): `kpi_block` counts them (142) and `batch_parse.get_candidate_models` skips them (140). Make the two readers agree, or state in the code why they differ. Pin the pair **by identity**.

**P1 Phase-0 gate:**
- a **> 1,000-row nonlinear probe** that **fails on the demo and solves licensed**, run locally now and in `licensed-solve.yml` on `main` after merge. Record that in Day 2's log;
- a **same-repository PR** run shown to print *demo*, skip the large tier, and be **refused** the secret;
- no license text in any log or artifact.

**P10c (2 h):** `PROCESS_AND_SMALL_ITEMS.md` §10c.
- `check_golden_staleness.py --fail-on-unverified` returns **3** when `timed_out` is non-empty.
- `make check-goldens` derives `MIN_SCOPE` from `git ls-files 'data/gamslib/mcp/*.gms'` and passes both flags.
- CI stays soft on timeouts.
- **Fail-before:** faked `check_one` timeouts give rc 0 today and must give 3 after; plain `main([])` still gives 0.

**Night of Day 1, after merge:** launch the **first licensed full run** (RT) in a throwaway worktree on a **scratch copy** of the DB. It is read on Day 2 and never persisted.

## Day 2 (2026-10-20) — RT: the license-neutrality gate · 3 h · + P2: batch preparation · 5 h · + P3: licensed convexity · 2 h

Branch `planning/sprint40-day2-neutrality`.

**RT first (3 h), close rule C8.**
- Diff the scratch DB from last night's licensed full run against the committed DB, on outcome, objective (relative 1e-6) and verdict.
- **Every row outside the two populations must keep its outcome.** The populations are pinned by identity in `BASELINE_RECONFIRMATION.md` §3: 11 MCP-gated, 10 NLP-gated.
- **This closes Unknown 1.5.** Any other row that moved is a toolchain finding, explained **before** any KPI is reported.
- Record that `licensed-solve.yml`'s first `main` run activated and passed the probe (P1's gate).

**P2 (5 h):**
- Confirm all 11 cohort re-emits are **byte-identical** at HEAD. A drift is a staleness finding, not a result.
- Identify **turkey's pre-fix golden** (before the Sprint 35 `$161` fix) for Decision 1's fail-before sub-rule.
- Launch the **batch on tonight's nightly slot**: one `run_full_test.py --model <id>` per model, with the new writers, so each row is written once with `license_edition: "licensed"`. Task 7 measured the whole two-population pipeline at about 36 min (`COHORT_DRY_RUN.md` §Wall-clock).

**P3 (2 h):**
- Run the licensed `verify_convexity.py` over the 9 in-scope NLP-gated models, **output-only**. `andean` is MIP: excluded, never relaxed.
- Start **W10**, `apply_convexity_results.py`: `--db` with no default; omit unknown non-nullable fields; replace, not merge; **refuse a model entering the convex set unless `--admit`ted**.

## Day 3 (2026-10-21) — P2: batch results, attribution and residuals · 6 h · + P3: admission by rule · 4 h

Branch `planning/sprint40-day3-cohort`.

**P2 (6 h):**
- For every model, record three things:
  - the comparison verdict;
  - `check_mcp_solve_attribution.py` (`MCP-SOLVED` for any claimed match, or it is not booked);
  - for every non-match, a `kkt_residual.py` verdict **or** the recorded harness failure. Task 7: the presolve emit fails to compile or execute for 6 models.
- Run turkey's pre-fix golden licensed. **If it matches, turkey is not fix-driven** (C5). Its match is presolve-only, so it falls under the existing rule (methodology, not counted) and **does not** enter the cold-match ledger.
- **Only a license-unlocked COLD match enters the `license_unlocked` ledger.** Task 7's four matches were all presolve-only, so expect none; a cold match here is a finding to record by identity.
- Persist the batch rows, and report them **once, pinned to the batch commit**, with the pre-written C3 wording (`PLAN.md` §5). **License-unlocked, never recovered.**
- **C1:** cohort rows at `path_solve_terminated` are a **first-measurement influx, listed by identity**. Task 7 measured `ferts` and `tabora` there. They are not a regression and not part of the 0.

**P3 (4 h):**
- W10 `--admit` for every model the licensed verifier classified convex (Decision 2: admit **by rule**). ⚠ **Only after Day 1's corpus-aware `check_doc_figures.py` is on `main`.** Without it, the first correct two-denominator sentence fails `make check-doc-figures`.
- **Record the multi-solve reference question.** `airsp2` classifies from a `DECISM` solve, and `airsp`, `msm`, `phosdis` are multi-solve too. Keep any affected comparison out of the headline until it is settled (`PLAN.md` §3 P3).
- Run the pipeline for the admitted models.

## Day 4 (2026-10-22) — P2: route every non-match · 5 h · + P3: pipeline results and the corpus record · 5 h

Branch `planning/sprint40-day4-routing`.

**P2 (5 h). Measure and route; do not fix in place.** P10's rule needs a reproduced fingerprint **and** a named fix surface; only `egypt` and `shale` qualify, and they go to P4.
- Open the routing-note issue documents (`COHORT_DRY_RUN.md` §Routing):
  - **R-PRE-140** (egypt, srpchase);
  - **R-EXEC** (ferts, tabora: capture the execution-error line this time, sanitized);
  - **R-B-glider**, **R-B-sroute**, **R-B-tricp** (⚠ check its 6.15e6 equality residual first);
  - **R-B-robot**: link it to **P5**, because robot's worst row is `stat_step`.
- Commit `ISSUE_933`'s re-scope: compile errors gone; tricp is `case_b`.
- **Sweep the changed set:** any doc naming a cohort model's bucket now quotes a moved membership.

**P3 (5 h):**
- Results for the models reaching an MCP (Task 7: `airsp2`, `torsion` match via presolve; `jbearing` → **R-JB-171**; `minsurf` → R-EXEC + R-B-minsurf).
- Route the five that reach none: parse `emfl` / `indus89` / `phosdis`; translate timeout `airsp` / `msm`.
- Write the **corpus record** with both denominators, from `kpi_block.py --corpus`.

## Day 5 (2026-10-23) — P3: the expanded-scope sentence · 1 h · + P7: #1755, the diagonal defect · 7 h · + Checkpoint 1 · 2 h

Branch `planning/sprint40-day5-diagonal`.

**P3 (1 h), close rule C4:**
- one sentence carrying the 142 continuity figure **and** the expanded figure;
- the Rolling-KPIs footnote, in the S23–S25 precedent's form.

**P7 (7 h).** `ISSUE_1755` and `CORRECTNESS_PRETRACES.md` §4.
- **Layer: AD**, `derivative_rules._sum_should_collapse`. Its `len(sum_index_sets) != len(wrt_indices)` early return rejects a reference that repeats one binder.
- **Phase-0 doc first**, with the layer and the **positive control**: the off-diagonal `tsam('i1','i2')` still differentiates to 0.
- **Fail-before:** the reproducer emits `stat_tsam(i,j).. 1 =E= 0;` and no `nu_diagsum`.
- **Pass-after:** `nu_diagsum` is on the diagonal, and the scalar variant solves to 0.3333.
- ⚠ This fix newly references multipliers, so it can expose a repeated equation domain to **#1737's refusal**. That is #1737 working; **never narrow it.**

**Checkpoint 1 (2 h), end of day:**

```bash
# discover the scope first: the resolver's own MODEL count (not a file count)
.venv/bin/python scripts/gamslib/run_full_test.py --resolve-changed --since-commit bd2af6e9 \
  --dry-run --json 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("error") or len(d["changed_models"]))'
# then assert it
.venv/bin/python scripts/gamslib/run_full_test.py \
  --resolve-changed --since-commit bd2af6e9 --min-scope <N>
```

- **NO-GO on any `backward` or `missing` row.** It never persists.
- `<N>` is the dry run's **model** count. The resolver dedupes a model's cold and presolve goldens, so a `git diff | wc -l` file count over-states it and would falsely reject the checkpoint.
- If the dry run reports the empty-selection error, the run needs `--allow-empty` and **certifies nothing**. Say so; do not report it as a GO over the corpus.
- **Plus a licensed re-run of the 11 cohort models**, because PR workflows are demo-only (Task 4's trade-off).

## Day 6 (2026-10-24) — P7: #1755 finish · 3 h · + P4: turkpow, Class A · 7 h

Branch `planning/sprint40-day6-turkpow`.

**P7 (3 h):**
- Run the full leak gate, **complete** and alone. Every changed golden is a **candidate corpus instance** to examine, never to blindly refresh.
- Determinism ×3.
- Land it (C2), or bound it with its mechanism named.

**P4 (7 h). It starts after P2, so egypt and shale have their solves.** `CORRECTNESS_PRETRACES.md` §1.
- **Layer: KKT re-symbolisation**, `_replace_indices_in_expr`'s alias ChainMap layer. It maps the AD's deliberately symbolic sum binder `v` onto `t`.
- **Do not patch the `t__kkt1` mint.** It is downstream and correct.
- **Phase-0 fail-before:** `Alias (t,v)`, a variable `z(v,t)`, and `e(t).. sum(v$s(t,v), c(v,t)*z(v,t))`. Assert that no `$(…)` guard repeats a coordinate and that the multiplier is `nu_e(t)`.
- **Positive control:** the same fixture without `Alias` already passes.

## Day 7 (2026-10-25) — P4: land turkpow, start egypt and shale · 5 h · + P8: the structural pins become behavioural · 5 h

Branch `planning/sprint40-day7-classa`.

**P4 (5 h):**
- Land turkpow, with the P2 ratchet **9 → ≤ 6** and `--update-baseline` **in the same commit**. nonsharp's 2 cannot move by regeneration (MINLP, refused).
- egypt (`tranc(rp,rp)`) and shale (`ts(tf,tf)`): Class-A fixes, verified against their **licensed solves**.
  - ⚠ Task 10: **necessary, not sufficient.** Both stay MS 5.
  - Land on property + golden evidence, route the underlying defect, and project no Solve.

**P8 (5 h).** `CORRECTNESS_PRETRACES.md` §5.
- Promote `_match_subset_domain` and `_compute_index_offset_key`'s structural pins to **behavioural** pins, using the 3-D aliased fixtures.
- **Positive control:** each assertion **fails** with its consume-once guard neutralised.

## Day 8 (2026-10-26) — P4: finish, plus the Class-B design · 4 h · + P8: finish · 1 h · + P5: the `stat_step` class · 5 h

Branch `planning/sprint40-day8-statstep`.

**P4 (4 h):**
- Finish egypt and shale.
- **Write the Class-B design:** the declaration-vs-assignment context **is** in the IR (`ParameterDef.domain` vs `expressions[k][0]`), and gussrisk's fix layer is emit (`emit_post_assignment_na_cleanup`). **Implement only if budget remains.**
- nonsharp has one reference of each class; do not treat it as one item.

**P8 (1 h):** finish and land.

**P5 (5 h). lnts verdict C: do not re-apply the banked diff, and do not project +1 Solve.**
- **File the `stat_step` issue.** It is untracked today.
- Write its Phase-0 doc: confirmed in **lnts** and **robot** (`case_b` at `stat_step`); candidates **glider** and **rocket**, unconfirmed.
- Trace whether lnts's and robot's rows share one mechanism. If not, split them (`PLAN.md` §3 P5).

## Day 9 (2026-10-27) — P6: sarf, E1–E4 and the import hoists · 8 h · + P5: trace · 2 h

Branch `planning/sprint40-day9-sarf`.

**P6 (8 h).** `SARF_JACOBIAN_DESIGN.md` §§6–8.
- **E1/E2:** the referenced-instance filter for the **inequality and bound** paths, as one shared helper.
- ⚠ **Build each position map once, on a cache miss.** `cache.setdefault(key, {…})` evaluates the comprehension on every call. That is an O(declared) rebuild per row that looks cached, and it was in the design's own first prototype.
- **E3:** the gradient filter. **E4:** sparse validation. **E7/E8:** hoist the two local imports.
- **Gate:** byte-identical goldens and fixture hashes at all four fixture sizes. **Any change is a `_referenced_index_tuples` false negative. Stop** (exit 2).

**P5 (2 h):** continue the trace.

## Day 10 (2026-10-28) — Checkpoint 2 · 2 h · + P6: land, then bound the recursion · 6 h · + P5: land or bank · 1 h

Branch `planning/sprint40-day10-sarf`.

**Checkpoint 2 runs FIRST, before P6 lands and before P9a** (Day 11's relabels would read as `forward` moves):

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --resolve-changed --since-commit bd2af6e9 \
  --dry-run --json 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("error") or len(d["changed_models"]))'
.venv/bin/python scripts/gamslib/run_full_test.py \
  --resolve-changed --since-commit bd2af6e9 --min-scope <N>
```

The same rules as Checkpoint 1, plus the licensed cohort re-run.

**P6 (6 h):**
- Land E1–E4 + E7/E8 (C2), with the leak gate alone.
- Then **diagnose E5/E6**, the `simplify` recursion behind `build_stationarity_equations`, **as a bounded item**.
- **C7's precondition is E5/E6 starting.** **+1 Translate → 136** is reported only if sarf produces a byte-stable golden at ≤ 300 s.
- If the fix needs `simplify`'s algorithm changed rather than the expression's shape, re-scope it to its own issue. **C7 is then VOID.**
- ⚠ A builder-side E5 fix touches `stationarity.py`, which also holds #1741's guard, so it needs a guard-impact review.

**P5 (1 h):** land the `stat_step` fix behind its gate (C2), or bank it with its mechanism named.

## Day 11 (2026-10-29) — P9: the smaller items · 6 h · + P10: 10a and 10b · 4 h

Branch `planning/sprint40-day11-small`.

**P9 (6 h).** `PROCESS_AND_SMALL_ITEMS.md` Part 2. The owner answers are recorded there.
- **P9a, report own-infeasible MCPs against an optimal NLP as `mismatch`.** It is **KPI-visible**, so it gets its own Phase-0 doc per §P9a.4:
  - **both sites:** `test_solve.py`'s `_own_infeasible_answer` **and** the cascade at `run_full_test.py` ~L1149–1151. A Case-6-only change is **inert**;
  - **derive the affected set first, from today's DB, with the widened condition, and pin it by identity** in two parts (`PLAN.md` §5 C9):
    - the remainder of **prep's 7** (agreste, camcge, cesam, fawley, lnts, mine, rocket), dropping by name any that P5 or another landing moved;
    - the **cohort additions** P2 persisted. Task 7 measured `egypt`, `robot`, `shale`, `sroute` and `tricp` as own-infeasible; re-derive, do not copy.
  - **Never assert "+7" or prep's list alone**: a correct relabel would fail it;
  - **positive control:** the cascade site unchanged ⇒ the DB stays byte-identical;
  - report per **C9**: the **measured** `mismatch` +*k* / `not_tested` −*k*, **0** `kpi_block` figures move, and the *k* checkpoint `forward` moves are **relabels**. **Do not add a checkpoint exception.**
- **P9b:** retire `scripts/integration_health_check.py`. First confirm `grep -rn integration_health_check` finds no reader outside `docs/`.
- **P9c:** rename `all_219_match` → `all_models_match` across its 4 readers in one commit, then run `make check-doc-figures`.

**P10 (4 h):**
- **10a:** land `tests/helpers/anchor_resolver.py` (verbatim `_code_only` / `_owning_bodies`, `AnchorError`, `resolve_unique`). Migrate the 2 weaker resolvers. Re-apply the `mcp_file_path` mutant, which must fail.
- **10b:** add the `**Positive control:**` field, required on **added** Phase-0 docs only.
  - The regex is `[ \t]*\S`, **not** `\s*`, which consumes the newline.
  - Document it in CONTRIBUTING together with the `**Layer:**` field.

## Day 12 (2026-10-30) — P10: 10d and 10e · 4 h

Branch `planning/sprint40-day12-process`.

- **10d:**
  - `check_doc_figures.py --text FILE`;
  - the `Makefile` `check-doc-figures` target forwards `TEXT` (today it is silently dropped), keeping the `FACTS` and default `--base` modes;
  - a test through the `make` entry point with a stale body and a clean diff.
- **10e:** the CONTRIBUTING section *"Review-Round Rules"*, carrying the four rules in this file's preamble, plus a stdlib grep test that resolves the highest `SPRINT_<n>` directory.

The day is deliberately light. **The remaining hours are the sprint's slack.**

## Day 13 (2026-10-31) — close: retest and close documents · 6 h

Branch `planning/sprint40-day13-close`.

**Retest:**
- The full pipeline.
- Determinism **×3** `PYTHONHASHSEED`, byte-identical over the full golden scope.
- `make check-goldens` **alone**, with the derived `--min-scope` and `--fail-on-unverified`. **Any timeout is a FAIL.**
- The licensed cohort run.
- `make check-index-repeats`.
- `make check-doc-figures`.

**Write, in this order:**
1. `SPRINT_LOG.md`;
2. `SPRINT_RETROSPECTIVE.md`;
3. the `SUMMARY.md` row;
4. **`SPRINT_41_CARRYFORWARDS.md`**. It is a convention, not a prompt item; the next prep looks for it by name.

**Check every close rule against its precondition** (`PLAN.md` §5) and state each verdict. A **VOID** rule is not the same as an unmet one. Report:
- the cohort per **C3**;
- the scope per **C4**;
- the floor per **C5**: "floor 75 (+*k* license-unlocked, not counted)", where *k* counts **cold** matches only;
- the influx per **C1**, by identity.

**Derive every closing figure.** A count of findings is a figure too.

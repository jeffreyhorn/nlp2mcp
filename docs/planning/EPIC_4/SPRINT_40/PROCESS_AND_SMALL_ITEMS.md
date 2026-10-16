# Sprint 40 — Process Mechanisms (P10) & Smaller Items (P9)

**Prep Task 11** · measured on `main` at `0cb24ff2` · 2026-10-16
**Unknowns:** 9.1, 9.2, 10.1, 10.2 (`KNOWN_UNKNOWNS.md`)

Every probe in this document ran outside the repo (`/tmp/t11`) or on a scratch
branch or DB. The committed DB and the goldens were only read. Each probe was
first shown able to fail (§7.5 of the Sprint 39 retrospective), and each
section records that positive control next to its result.

---

## Summary

| item | verdict on `main` | next step | est. |
|---|---|---|---|
| **10a** one anchor resolver | extraction is a pure refactor: 16/16 sites resolve identically | land `tests/helpers/anchor_resolver.py`; migrate **2** weaker resolvers | 2.5 h |
| **10b** positive-control field | an unconditional requirement fails **42/42** docs; the added-only rule fails **0** | `**Positive control:**` field, enforced on added docs only (P8a's pattern) | 1.5 h |
| **10c** the leak gate runs alone | `--min-scope` catches a vacuous scope but **not** contention, which shows up as timeouts | `--min-scope` **and** a new `--fail-on-unverified` in `make check-goldens` | 1.5 h |
| **10d** the PR body is a pointer | `check_doc_figures.scan_line` already flags a stale figure in arbitrary text | a `--text FILE` mode, run on the PR body before `gh pr create` and on every review round | 2.0 h |
| **10e** review-round rules | not recorded in CONTRIBUTING today | one CONTRIBUTING section, plus `SPRINT_40/prompts/PLAN_PROMPTS.md`, with a grep check | 1.0 h |
| **P9a** 7 `model_infeasible` → `mismatch` | **0** `kpi_block` figures move, but **two** code sites are needed and the checkpoint gate reads it as 7 moves | **KPI-visible**: own Phase-0 doc (§P9a.4). **Owner: relabel as `mismatch`** | 3–4 h |
| **P9b** `integration_health_check.py` | still fails uninstalled, **and fails installed too** (8 of 13 examples) | **Owner: retire the script** | 0.5 h |
| **P9c** `all_219_match` key | present; **4** readers | rename it in one commit with its readers | 0.5 h |
| **P9d** ganges embedded-NLP-diverges issue | was unfiled (`--state all`) | **filed as #1758** from Appendix A (owner, 2026-10-16) | done |
| **P9e** #1668 | **already CLOSED** on 2026-09-03 (`COMPLETED`) | none; drop from P9 | 0 |
| *(carried)* #933 tricp | OPEN, untriaged, last updated 2026-04-01 | triage or close | 0.5 h |

**P10 total: 8.5 h** (PROJECT_PLAN budgets ~10–14 h). **P9 total: 4.5–5.5 h** after the owner answers (P9a 3–4 · P9b retire 0.5 · P9c 0.5 · #933 0.5; P9d filed). The budget is ~6–10 h.

---

# Part 1 — P10: the process changes as mechanisms

## 10a. One resolver for anchors (Sprint 39 retrospective §7.3) — Unknown 10.1

**The resolver today.** It lives in `tests/unit/kkt/test_positional_domain_sites.py`
and has two pieces:

- `_code_only(source)` (L232, `@functools.lru_cache(maxsize=16)`) blanks out
  comments and bare string expressions.
- `_owning_bodies(source, qualified)` handles nested dotted owners.

`test_every_anchor_occurs_EXACTLY_ONCE_in_its_function` applies both to the
16 `CATALOGUED_SITES` rows. There are also 5 `BEHAVIOURALLY_PINNED` rows. The
dependencies are `ast`, `functools`, `tokenize` and the project root, with no
fixtures and no module globals beyond the two tables, so it is self-contained.

**Scratch extraction.** This was a local-only commit `b79c1278` on
`scratch/sprint40-task11-resolver`, never pushed. It:

- moved both functions verbatim into `tests/helpers/anchor_resolver.py`;
- added `class AnchorError(AssertionError)` and
  `resolve_unique(rel, qualified, snippet) -> int`, which raises when the anchor
  is absent, ambiguous, or its function is gone;
- made the test module import the helper.

| check | result |
|---|---|
| sites resolving the same before and after | **16/16** |
| owning-body text identical | **16/16** |
| module tests after extraction | **11 passed** |
| positive control: ambiguous anchor (`used_var_positions`, 3× in `_match_subset_domain`) | **refused** |
| positive control: absent anchor | **refused** |

**Two weaker resolvers to migrate.** Each was shown to pass a mutant that the
shared resolver refuses.

1. **`tests/gamslib/test_run_full_test_path_relative.py:60`** runs
   `inspect.getsource(run_full_test)` over the **whole module**, then does
   `in src` checks. These checks are unscoped, comment-sensitive and do no
   uniqueness check.
   - **Mutant:** rename the writer's key to `mcp_file_path`, and leave the old
     assignment text in a `# was: …` comment.
   - **Measured:** the weak test **passes** the mutant. The two `in` checks are
     satisfied by the comment and by the key's absence.
   - `_code_only` counts the anchor **1 → 0**, so `resolve_unique` would refuse it.
2. **`tests/unit/sprint_audit/test_check_doc_figures.py:418`** is a whole-file
   `[0-9.]+` absence check. It filters comments ad hoc, dropping lines that
   start with `#`, `*` or `"`. As a result it:
   - **misses** a real use on a line that starts with a string (`    "[0-9.]+",` in a list);
   - **false-fires** on an unprefixed docstring body line or an inline comment.

   Replacing it with `_code_only(src).count("[0-9.]+") == 0` makes it neither
   miss nor false-fire.

**Mechanism.**

- **Location:** `tests/helpers/anchor_resolver.py` (new), consumed by:
  - `test_positional_domain_sites.py`;
  - `test_run_full_test_path_relative.py`;
  - `test_check_doc_figures.py`.
- **Fail-before test:** `tests/unit/test_anchor_resolver.py`, with three cases,
  each against a small inline fixture module:
  - `resolve_unique` returns 1 on a unique anchor;
  - it raises `AnchorError` on an anchor appearing twice in one function;
  - it raises on an anchor appearing only in a comment.

  Before the helper lands, the module fails at import. After, it passes. Then
  re-apply the `mcp_file_path` mutant to the migrated path test, which must fail.
- **Estimate: 2.5 h** (helper + test 1 h, two migrations 1 h, mutant runs 0.5 h).

## 10b. A positive control in every probe (§7.5) — Unknown 10.2(a)

**Precedent (S39 P8a, `../SPRINT_39/PROCESS_INFRA_SPEC.md`).** Sprint 39's P8a
grandfathered old docs by the **PR's git status**, not by a date or a list:

- `missing_for_added()` (`check_phase0_doc.py:149`) applies
  `REQUIRED_WHEN_ADDED` and `LAYER_FIELD` (L60, L66) **only** to docs whose
  status in the PR is `added`.
- A modified old doc is held only to the base `REQUIRED` subsections.

**Dry run over every Phase-0 doc.** There are **42** under `docs/`: 29 top-level
in `docs/issues/`, and the rest in `completed/` or `finished/`.

| rule | docs failing |
|---|---|
| base `REQUIRED` subsections (today) | 1 (`finished/ISSUE_1455_…`, pre-existing) |
| docs that already carry `**Layer:**` | 4 |
| docs that already carry `**Positive control:**` | **0** (the phrase appears anywhere in 1) |
| **positive-control field required unconditionally** | **42 of 42** |
| **positive-control field required on `added` docs only** | **0** |

An unconditional rule would turn the gate red on untouched history, and
`missing_for_added`'s own docstring explains why a red gate on history gets
disabled. The added-only rule costs nothing on existing docs.

**The field, specified concretely enough to check:**

```
**Positive control:** <the known input that must make the probe fire> → <what firing looks like>
```

It sits in the doc header, next to `**Layer:**`. Examples, from Sprint 39's two
vacuous passes:

- "`-S` run with `site-packages` on `PYTHONPATH` → `ModuleNotFoundError: src`"
- "mutant `if False:` applied → test fails"

**Mechanism.**

- **Location:** `check_phase0_doc.py`.
  - Add `POSITIVE_CONTROL_FIELD = re.compile(r"^\*\*Positive control:\*\*\s*\S", re.M)`.
    The `\S` rejects an empty field.
  - Append it to `missing_for_added()` next to the layer check.
  - Document the field in `CONTRIBUTING.md` §Phase 0 Acceptance Gates →
    Workflow step 2 (L443). ⚠ That step describes only "the 4 required
    subsections". **P8a's `**Layer:**` field is enforced but documented
    nowhere outside `SPRINT_39/`** (`grep -rln 'Layer:\*\*'` finds no
    CONTRIBUTING hit). Document both in the same edit.
- **Fail-before test:** two cases in `tests/unit/sprint_audit/test_phase0_added_only_requirements.py`:
  - an `added` fixture doc with every current field but no positive control is
    **accepted today** and must be **rejected after**;
  - the same doc with `status == "modified"` must still be accepted. That is
    the grandfathering control.

  The draft regex's own positive control already ran: it accepts a doc with
  the field and rejects one without.
- **Estimate: 1.5 h.**

## 10c. The leak gate runs ALONE (carryforward §8.7) — Unknown 10.2(b)

**Confirmed on `main`:**

- `Makefile` L90–91, `check-goldens:`, runs a plain
  `$(PYTHON) scripts/sprint_audit/check_golden_staleness.py` with **no** `--min-scope`.
- `.github/workflows/golden-staleness.yml` L148–152 derives
  `MIN_SCOPE=$(git ls-files 'data/gamslib/mcp/*.gms' | wc -l)`, which is
  **193** today, and passes it.
- `--min-scope` is compared against the **discovered** count, before the
  7-model allowlist is removed. That leaves 186 in scope.

**Positive control 1 — a vacuous scope.** Run in a scratch worktree with no
raw sources:

| form | output | rc |
|---|---|---|
| Makefile (plain) | "checked 0 in-scope golden(s) … All in-scope goldens clean." | **0**, a vacuous pass | <!-- figures-ok: scratch-worktree control output with no raw sources -->
| CI (`--min-scope 193`) | "coverage floor not met — discovered 0 … expected at least 193" | **2** |

So deriving `--min-scope` locally closes the vacuous-scope hole.

**But that is not how the Sprint 39 incident failed.** `../SPRINT_39/SPRINT_LOG.md`
(the "I repeated Day 5's contention mistake" section) records the first run
reporting *"All in-scope goldens clean"* **with 2 unverified timeouts**
(ganges, gangesx). That was "a claim over 184 of 186". **Contention does not
reduce the discovered count. It causes timeouts**, and the plain sweep reports
those as soft (`check_golden_staleness.py:391–393`, `:474–480`).

**Positive control 2 — the real failure mode.** `/tmp/t11/p10c_timeout.py`
fakes `check_one` so that ganges and gangesx time out; no emit runs. The fake
visibly fired (2 `TIMEOUT (unverified, soft)` lines), and the output then
reproduces the incident's message exactly:

| argv | final line | rc |
|---|---|---|
| *(none)*, today's `make check-goldens` | "All in-scope goldens clean (2 slow-emit timeout(s), unverified)." | **0** |
| `--min-scope 193`, the CI form | same | **0** |

**`--min-scope` alone would have missed the incident it is meant to catch.**
Under `--expect-drift` (`make leak-check`), timeouts already block
(`unverified_blocks`, L411). Only the plain sweep treats them as soft.

**Mechanism.**

- **Location:** `check_golden_staleness.py` gets `--fail-on-unverified`. With
  it, a plain sweep returns non-zero (proposed **3**, distinct from drift 1 and
  scope 2) when `timed_out` is non-empty. The `Makefile` target becomes:

  ```make
  check-goldens:
  	@MIN_SCOPE=$$(git ls-files 'data/gamslib/mcp/*.gms' | wc -l | tr -d ' '); \
  	test "$$MIN_SCOPE" -gt 0 || { echo "no committed goldens — floor would be vacuous"; exit 1; }; \
  	$(PYTHON) scripts/sprint_audit/check_golden_staleness.py --min-scope "$$MIN_SCOPE" --fail-on-unverified
  ```

  CI is **left soft** on timeouts. Hosted runners can legitimately exceed the
  600 s budget on ganges (259–293 s standalone), and CI runs one job alone
  anyway. Making CI strict is a separate decision with a red-build cost, not
  part of this mechanism.
- **Fail-before test:** in `tests/gamslib/test_gate_scope_assertions.py`,
  monkeypatch `check_one` exactly as the scratch probe does:
  - `main(["--fail-on-unverified"])` with two timeouts must return 3. Today it
    is an argparse error, rc 2.
  - `main([])` must still return 0. That pins CI's soft behaviour.
  - Add a `Makefile` grep test asserting that `check-goldens` passes both flags.
- **Estimate: 1.5 h.**

## 10d. The PR description is a pointer (§7.4, §7.1)

**What rots.** Per-round patches to the PR body. The mechanizable half is "each
figure stated once, with its commit": a PR body figure that contradicts its
source.

**Probe.** `check_doc_figures.scan_line` is pure: it takes the derived truths
and one line. Fed arbitrary text through `derive_truths()` at `0cb24ff2`:

- `"Closed at Solve 111 · Match 96 · Translate 135"` → **1 finding** (`Match`, <!-- figures-ok: deliberately stale fixture input for the 10d probe -->
  cited 96, truth 95, source `kpi_block.py -> match`);
- the same line with 95 → **0 findings**.

The checker today reads only changed doc lines from `git diff`, so a PR body is
invisible to it.

**Mechanism.**

- **Location:**
  - `check_doc_figures.py` gets `--text FILE`, which scans every line of
    `FILE` through `scan_line` with the same exemptions and movement-line rule.
  - The `SPRINT_40/prompts/PLAN_PROMPTS.md` "Before creating the PR" block
    gains `make check-doc-figures TEXT=/tmp/pr-body.md`.
  - The review-round template gains two steps:
    - regenerate the body from the docs at the end of the round, or reduce it
      to `see SPRINT_LOG.md §Day N`;
    - `gh pr view N --json body -q .body > /tmp/pr-body.md`, then check it,
      before replying.
- **Fail-before test:** in `test_check_doc_figures.py`:
  - a body file containing `Match 96` with pinned truths `{"Match": 95}`: today <!-- figures-ok: deliberately stale fixture input for the 10d fail-before test -->
    rc 2 (unknown option), after **rc 1 with one finding**;
  - the same file with `Match 95` → rc 0. That is the positive and negative
    control pair.
- **Estimate: 2.0 h** (option + tests 1.5 h, prompt text 0.5 h).

## 10e. Review-round rules recorded (§7.2, §7.6, §7.7)

**Today.** `CONTRIBUTING.md` has none of the three rules: `grep -n stash`
returns 0. `SPRINT_40/prompts/PLAN_PROMPTS.md` does not exist yet; Task 12
writes it.

**Mechanism.**

- **Location:** a CONTRIBUTING section, "Review-Round Rules (Sprint 40 P10e)",
  after §Close-Rule Preconditions, with one paragraph each:
  - **Pin by identity, not count.** A test asserting "N of M" names the set.
    Ask which swap preserves N.
  - **Sweep the changed set.** When a classification moves, grep every claim
    mentioning a member of the moved set, not just the flagged line.
  - **Never `git stash` to switch branches.** Use `git show <ref>:<path>` and
    `pytest --collect-only`, both read-only.

  The same three lines go into the per-day and review-round templates of
  `SPRINT_40/prompts/PLAN_PROMPTS.md`.
- **Fail-before test:** a grep check in
  `tests/unit/sprint_audit/test_process_rules_recorded.py` (stdlib only).
  - Each of the three rule anchors must occur in `CONTRIBUTING.md`, and in
    `SPRINT_<n>/prompts/PLAN_PROMPTS.md` for the **highest** `n` (the same
    scope rule as `check_doc_figures.current_sprint_dir`, so it needs no bump at
    rollover).
  - Today it fails (0 of 3 anchors, and no file).
  - The anchors are resolved with 10a's `_code_only`-style care: in Markdown,
    an anchor inside a fenced block does not count.
- **Estimate: 1.0 h.**

---

# Part 2 — P9: the smaller items, re-verified on `main`

## P9a. The 7 `model_infeasible` comparisons — Unknown 9.1 — **KPI-visible**

**Identity**, derived from the DB at `0cb24ff2` (convex candidates with
`outcome_category == model_infeasible`): **agreste, camcge, cesam, fawley,
lnts, mine, rocket**. This is the same set `test_solve.py:956–957` names.

### P9a.1 What the DB actually holds — the carryforward's framing is incomplete

All seven carry `comparison_status: "not_tested"` ("Skipped due to solve
failure"), **not** `skipped`. `compare_solutions` would return
`skipped`/`compare_mcp_failed` (Case 6) for them, but the pipeline **never
calls it**:

- `run_full_test.py:1149–1151`: `if result["status"] != "success":` →
  `mark_cascade_not_tested(model, "solve", stats)`;
- `solve_mcp` sets `status: "failure"` for every `model_status` outside {1, 2},
  and all seven are MS 5 / SS 1.

So **widening Case 6 alone is DB-inert.** The relabel needs **two** sites:

1. `test_solve.py:968`, `_own_infeasible_answer`: drop `and nlp_infeasible`.
2. `run_full_test.py:1149–1151`: let a completed own-infeasible solve reach
   the compare stage instead of cascading.

### P9a.2 Scratch replay (`/tmp/t11/p9a.py`)

The replay rebuilds `compare_solutions` from its own source with only the
exemption widened; `src/` and `scripts/` on disk are untouched.

- **Per row:** as-is → `skipped/compare_mcp_failed`; widened →
  `mismatch/compare_status_mismatch`, for all 7.
- **Whole-corpus A/B:** exactly these **7** of 219 rows change verdict. No
  other row moves, which matches the PR #1740 measurement quoted in the code
  comment.
- **Scratch DB** with the 7 widened results written in:
  - validates against `data/gamslib/schema.json` with **0** errors;
  - `kpi_block.py --json` against it is **byte-identical** to the committed DB's;
  - writing `skipped` instead also leaves every KPI unchanged.

### P9a.3 Every reader of `comparison_status`, and what moves

| reader | reads | moves? |
|---|---|---|
| `kpi_block.py:102` (`match`, `match_cold`, `match_presolve`, `all_219_match`) | `== "match"` only | **no — 0 of the block's quantities** |
| `floor_tracker.py:94` | `== "match"` only | no |
| `check_doc_figures.py` facts | via `kpi_block` | no |
| `check_mcp_solve_attribution.py:846–871` | enum validity only | no (`mismatch` is in the schema enum) |
| `db_manager.py:528` (status summary) | tallies every value | **yes**: `mismatch` 15 → 22, `not_tested` 31 → 24 |
| `run_full_test.py:1360–1378` (`_extract_bucket` / `_bucket_severity`, the `--resolve-changed` checkpoint) | `_COMPARE_RANK = {"match": 2, "mismatch": 1}` | **yes**: severity 1 → 11 for all 7, classified **`forward`** |
| `run_full_test.py:638–647` (run stats) | match / mismatch / else | yes: counted as mismatches instead of cascade skips |

The checkpoint row is the one that matters. On landing, `_classify_bucket_move`
reports **7 forward moves**, which is not an emit improvement. **Afterwards,
any run in which these rows fall back to `not_tested` is classified `backward`,
which is a checkpoint NO-GO.** One example is a run without the compare stage.

### P9a.4 Its own Phase-0 requirement

This is **KPI-visible** and must not be folded into another track or a review
fix. Its Phase-0 doc must carry:

- **Fix surface:** both sites above. A PR that touches only Case 6 is inert
  and must be rejected as such.
- **Expected bucket movement**, stated before the change:
  - `kpi_block` **0** (Solve 111 · Match 95 unchanged);
  - DB tally `mismatch` +7 / `not_tested` −7;
  - checkpoint: 7 `forward` moves, all **relabels, not fixes**. The PR body
    must say so in the same sentence.
- **Identity pin:** the 7 names above as a set. A count of 7 is not enough
  (§7.2).
- **Positive control:** with the cascade site unchanged, the DB must stay
  byte-identical. This proves the second site is load-bearing.
- **Regression note:** after landing, a compare-less run must not be read as
  7 regressions. Either the checkpoint learns the label change, or the doc
  records the expected `backward`.
- **Owner decision:** whether `mismatch` is the more honest verdict for
  "NLP optimal, our MCP proved infeasible" is a reporting-semantics call, not
  an engineering one.

**Owner answer (2026-10-16):** report these 7 rows as `mismatch`. P9a is
therefore a sprint item, landed behind the Phase-0 doc above with both code
sites.

**Estimate:** 3–4 h, including the doc, both sites, a fixture test and the
7-model DB re-run.

## P9b. `scripts/integration_health_check.py` — Unknown 9.2(a)

- **Uninstalled (simulated faithfully):** `PYTHONPATH=.venv/lib/python3.12/site-packages python -S`.
  This keeps `lark` importable but skips the editable install's `.pth`. Result:
  **rc 1**, `ModuleNotFoundError: No module named 'src'` at L16. **Reproduces.**
  - Six module-level `src` imports (L16–21), no `sys.path` bootstrap.
  - **Positive control:** the PREP_PLAN verification command (plain
    `python -S … --help`) also fails on `src` today, but it **cannot confirm a
    fix**. `-S` hides `lark` as well. With `PYTHONPATH=.` (standing in for the
    bootstrap), `src` resolves and the run then fails on `No module named
    'lark'`. So plain `-S` reports "failure reproduces" before **and** after
    the bootstrap. Verify the fix with the `PYTHONPATH=<site-packages> -S` form.
- **Installed: also rc 1.** "❌ INTEGRATION HEALTH CHECK FAILED", **5 passed /
  8 failed of 13**.
  - The hard-coded `["examples/simple_nlp.gms"]` list (L205–207) is
    **overwritten** by `sorted(Path("examples").glob("*.gms"))` (L210–213),
    which is CWD-relative.
  - The 8 failures are example-file defects or deliberately unsupported inputs:
    `abs()` without `--smooth-abs`, `min`, `*` comments, a missing include,
    an empty domain.
- **Not wired anywhere:** no `Makefile` target, no workflow. It is a Sprint 3
  checkpoint relic.

**The item is larger than described.** The 2-line bootstrap (as in
`run_full_test.py:65–66`) fixes the import but not the exit code. **Next step
(owner's choice):**

- **(i)** bootstrap + restrict to the intended list + resolve paths against
  the repo root (1.5 h); or
- **(ii)** retire the script (0.5 h). Nothing calls it.

**Owner answer (2026-10-16):** retire the script. Delete
`scripts/integration_health_check.py` in the sprint. That is a `*.py` change,
so the quality gate applies. First confirm again that nothing references it
(`grep -rn integration_health_check` outside `docs/`).

## P9c. `kpi_block.py`'s `all_219_match` key — Unknown 9.2(b)

The key is still present (`kpi_block.py:139`). **Readers:**

- `kpi_block.py:160` (markdown) and `:186` (line format);
- `check_doc_figures.py:457–461` (the `all-population Match` fact; its comment
  explains keeping the key);
- `tests/gamslib/test_gate_scope_assertions.py:391–396`.

The rendered label already derives from `total_models`, so only the key name
is stale.

**Next step:** rename it to `all_models_match` in one commit across the 4
readers, and re-run `make check-doc-figures` (the fact's `source` string names
the key). **0.5 h.**

## P9d. The ganges embedded-NLP-diverges issue — Unknown 9.2(c)

`gh issue list --state all --search ganges` (29 results, open and closed)
returns **no** issue for the 6th blocker. Related issues:

- **OPEN:** #1667 (deferred bounds before `$include`), #929 / #930 (translation
  timeouts), #1378 (launch), #1424 (camshape / cclinpts dynamic subsets);
- **CLOSED:** #1668, #1289.

ganges/gangesx are both `likely_convex` · `path_syntax_error` · `not_tested`
in the DB.

**Filed as [#1758](https://github.com/jeffreyhorn/nlp2mcp/issues/1758)**
(owner, 2026-10-16), from Appendix A. The issue states that its figures date
from Sprint 37 Day 4, before the license, and were not re-measured. Re-confirm
them with the #1667 control patch before starting work (about 1 h).

## P9e. #1668 — Unknown 9.2(d)

`gh issue view 1668` shows **CLOSED**, `stateReason: COMPLETED`, closed
**2026-09-03T00:33:59Z**, with 0 comments. The carryforward's "still OPEN"
premise is **stale**: someone closed it at Sprint 39 Day 0. **No close note is
needed; drop it from P9.** Appendix B records the note that would have been
posted, only because the task asked for a draft. Its one useful addition is a
closing comment explaining why, because the issue was closed silently.

## Carried, not in PROJECT_PLAN P9: #933 (tricp)

Carryforward §7 lists `ISSUE_933_tricp-mcp-compilation-errors.md` as "still
OPEN and untriaged". GitHub confirms it is OPEN, last updated 2026-04-01.
tricp is in the license-gated cohort (P2), so triage it **with** that batch
rather than as filler. **0.5 h.**

---

## Appendix A — issue text: ganges embedded-NLP divergence (filed as #1758, 2026-10-16)

> **Title:** ganges/gangesx: embedded `ganges0` NLP diverges from the standalone source under `--nlp-presolve` (#1378/#1424 class)
>
> **Summary.** With the #1667 deferred-bounds ordering fix applied (control,
> Sprint 37 Day 4), the ganges presolve emit compiles cleanly (`$141`/`$145`/`$149`
> 78/3/9 → 0/0/0, no `rPower`). But the NLP solved **inside** the emitted file
> diverges from the same source solved standalone:
>
> | run | model status | objective |
> |---|---|---|
> | standalone `ganges.gms` | MS-2 Locally Optimal | 6395.5444 |
> | embedded `ganges0` (via `$include` under `--nlp-presolve`) | MS-5 Locally Infeasible | −386785.5017 |
>
> The warm start is therefore wrong, and `mcp_model` ends MS-4. This is the
> 6th blocker of the ganges cascade and has had no issue of its own.
>
> **Class.** Embedded-NLP-diverges-from-standalone (#1378 launch, #1424
> camshape/cclinpts). `$include` re-runs the source under `$onMultiR`, where a
> re-declaration does not reset, so any non-idempotent statement or blanket
> default emitted before the include changes what the embedded solve sees.
>
> **Expected bucket effect.** A clean cascade alone moves
> `path_syntax_error → model_infeasible`, a lateral move. +2 Solve/Match needs
> this divergence fixed **as well as** #1667. #929/#930 (translation time) are
> independent.
>
> **Reproduce.** Apply the #1667 control (`ISSUE_1667_…md` §Control result),
> emit with `--nlp-presolve`, and compare the embedded `ganges0` solve's
> `MODEL STATUS` with `gams ganges.gms`.
>
> **First step.** Bisect the emitted prefix: which statement emitted before the
> `$include` makes the embedded solve differ? This is the same method that
> located #1378.
>
> **Related:** #1667, #929, #930, #1378, #1424 · `SPRINT_37/GANGES_RECOVERY_DESIGN.md` §3.

## Appendix B — DRAFT close note for #1668 (do not post; moot)

> **Not needed:** #1668 was closed as COMPLETED on 2026-09-03, with no comment.
> If a record is wanted, this is a closing comment:
>
> Closed on measurement (Sprint 39 Unknown 10.2): both fix directions were
> measured and closed. The `$149` rebind is not landable as banked because it
> mis-pairs `p(g)` with `eta(g,gp,h)` on prolog. ganges' remaining blockers are
> tracked in #1667 and in #1758 (the embedded-NLP divergence).

# Sprint 27 Prep Task 10: PR23 CI-Workflow PR Self-Review Checklist — Design

**Status:** ✅ COMPLETE
**Date:** 2026-05-30
**Owner:** Prep Task 10
**Codifies:** Sprint 26 retrospective recommendation **PR23**
**Source data:** Sprint 26 PR #1396 — 42 Copilot review comments across 11 rounds

---

## 1. Purpose

Author a structured self-review checklist for CI-workflow PRs (covering `.github/workflows/*.yml` / `.github/workflows/*.yaml` — which is also where reusable workflows live — plus `scripts/ci/*` and `.github/actions/*` — which is where composite actions live — matching the scope clauses in the delivered `CONTRIBUTING.md` section) so PR authors can catch the recurring failure modes that produced 11 review rounds on Sprint 26 PR #1396. The deliverable is a new `## CI Workflow PR Checklist (PR23, Sprint 27 Prep Task 10)` section in `CONTRIBUTING.md`.

---

## 2. Source Data — Sprint 26 PR #1396 Review-Comment Categorization

PR #1396 (PR19 CI extension — emit-solve validation workflow + `scripts/ci/parse_pr19_targets.py` + `scripts/ci/run_pr19_solves.py`) produced 42 distinct top-level review comments across 11 review rounds.

Pulled via `gh api repos/jeffreyhorn/nlp2mcp/pulls/1396/comments?per_page=100 --paginate | jq '[.[] | select(.in_reply_to_id == null)] | length'` = **42**.

The 42 comments cluster into the **7 recurring categories** below.

### 2.1 Input validation (8 comments)

| ID | Path:line | Issue |
|---|---|---|
| 3239091432 | `parse_pr19_targets.py:83` | `int(reslim_raw)` no error-handling — malformed `reslim=30s` crashes with `ValueError` trace. |
| 3239154011 | `parse_pr19_targets.py:83` | Restatement of the same `int(reslim_raw)` validation gap. |
| 3239816472 | `parse_pr19_targets.py:77` | `reslim` accepts negative values — `gams ... reslim=-5` is invalid AND breaks `timeout=reslim+30`. |
| 3239907399 | `run_pr19_solves.py:210` | `--reslim` CLI flag has no non-negativity validation. |
| 3239713498 | `run_pr19_solves.py:215` | `entry.get('reslim') or args.reslim` falsy-coerces 0 — use explicit `is None`. |
| 3241094136 | `parse_pr19_targets.py:63` | `model_part` not validated against safe pattern — path-traversal risk via `..`/separators. |
| 3241094187 | `run_pr19_solves.py:79` | Same model-name validation gap on the consumer (defense in depth). |
| 3238239775 | `run_pr19_solves.py:109` | `gams` not on PATH → `FileNotFoundError` crash instead of structured failure record. |

### 2.2 Pagination (2 comments)

| ID | Path:line | Issue |
|---|---|---|
| 3241462665 | `pr19-emit-solve-validation.yml:89` | `issues.listComments` paginated; may miss marker on long-lived PRs → duplicate comments on rerun. |
| 3241462739 | `pr19-emit-solve-validation.yml:344` | Same pagination issue in the results-comment upsert. |

### 2.3 Fork tolerance (1 comment)

| ID | Path:line | Issue |
|---|---|---|
| 3241094201 | `pr19-emit-solve-validation.yml:81` | PR-comment upsert API calls have no fork-PR guard; commonly fail with 403 for fork PRs and break the whole workflow. |

### 2.4 Schema validation (6 comments)

| ID | Path:line | Issue |
|---|---|---|
| 3238239761 | `parse_pr19_targets.py:93` | Unknown `tier=` values silently dropped from both buckets — typo (e.g., `tier=pattern-c`) silently reduces coverage. |
| 3239091423 | `parse_pr19_targets.py:93` | Restatement — prefer hard-error or explicit `unknown` bucket. |
| 3239154032 | `parse_pr19_targets.py:93` | Third restatement of the same unknown-tier issue (recurred across review rounds 1–3). |
| 3239816515 | `run_pr19_solves.py:209` | `json.loads + targets["tier_0_1"]` indexing raises traceback on missing file / invalid JSON / missing key. |
| 3241212011 | `run_pr19_solves.py:281` | Per-entry shape not validated — `entry["model"]` raises on non-dict / missing key / non-string. |
| 3241310033 | `run_pr19_solves.py:322` | `entry.get('reslim')` not type-checked — hand-edited string/float values raise `TypeError` on `<0` comparison. |

### 2.5 Error handling (6 comments)

| ID | Path:line | Issue |
|---|---|---|
| 3239595479 | `run_pr19_solves.py:149` | `git rev-parse --show-toplevel` no error handling — add `--repo-root` override / `$GITHUB_WORKSPACE` fallback / clear error + exit 2. |
| 3239907373 | `run_pr19_solves.py:111` | `TimeoutExpired` record lacks `error` field — schema drift vs other failure modes. |
| 3241310088 | `parse_pr19_targets.py:48` | `path.read_text()` not guarded — `OSError` (permission/transient FS) surfaces as Python traceback. |
| 3241462774 | `run_pr19_solves.py:263` | `scratch_base.mkdir(...)` can raise `OSError` — unhandled traceback. |
| 3241462806 | `run_pr19_solves.py:326` | Final `write_text(json.dumps(results))` unguarded — `OSError` loses in-memory per-model results. |
| 3239091401 | `run_pr19_solves.py:91` | `passed` checks `rc + MODEL STATUS` but NOT `SOLVER STATUS` — abnormal solver termination silently marked pass. |

**Note:** comment **3238239775** (`gams` not on PATH → `FileNotFoundError`) is also relevant here as a subprocess-error-handling case, but it is assigned to §2.1 (Input validation) as its primary category — the canonical fix is `shutil.which('gams')` at startup, which is an input-presence check. Each comment is listed in exactly one primary category in §2 to keep the per-category counts and the §2.9 totals consistent.

### 2.6 Marker uniqueness (1 comment)

| ID | Path:line | Issue |
|---|---|---|
| 3241211963 | `pr19-emit-solve-validation.yml:96` | Upsert selector matches any comment containing 'PR19 Pre-Merge Solve Validation' — but that substring is also used by the results upsert, so toggling bypass label overwrites the wrong comment. Fix: per-type HTML-comment marker like `<!-- pr19-validation:bypass -->`. |

### 2.7 Logging visibility (14 comments)

This is the largest category — stale step comments, stale PR-description text, stale CHANGELOG entries, broken Markdown tables in PR comments, and missing columns for fields the gate depends on.

| ID | Path:line | Issue |
|---|---|---|
| 3239461942 | `pr19-emit-solve-validation.yml:230` | Setup-failure comment references `sha256sum -c` but install step uses explicit string-compare; readers can't find the diagnostic line. |
| 3239595444 | `pr19-emit-solve-validation.yml:172` | Step comment says hard-fail on `rc != 0 \|\| MODEL STATUS != 1`, but actual gate also requires `SOLVER STATUS == 1` — comment drift. |
| 3239907331 | `pr19-emit-solve-validation.yml:248` | PR comment table shows only `MODEL STATUS` but gate also checks `SOLVER STATUS` — `1 Optimal` ❌ rows are unexplainable from the PR thread. |
| 3239154087 | `SPRINT_LOG.md:1137` | Doc says workflow expected to fail on first run due to SHA256 placeholder, but workflow now pins a concrete SHA256. |
| 3239154105 | `CHANGELOG.md:12` | Changelog entry mentions `<TO BE FILLED IN BY FIRST CI RUN>` placeholder; workflow already pins the SHA256. |
| 3239461902 | `SPRINT_LOG.md:1092` | Deliverables table still describes `--soft-fail` flag and SHA256 placeholder — both are stale. |
| 3239461927 | `CHANGELOG.md:12` | Changelog still claims `--soft-fail` controls Pattern C; runner now derives behavior from `--tier soft-fail`. |
| 3240647489 | `run_pr19_solves.py:204` | PR description's smoke-test example still uses `--soft-fail`; runner no longer accepts it. |
| 3240647521 | `pr19-emit-solve-validation.yml:151` | PR description's "expected first-run failure" text contradicts current pinned-SHA256 state. |
| 3238239746 | `pr19-emit-solve-validation.yml:207` | Tier 0/1 results table header has unnamed 5th column — give it a name (e.g., `Pass`). |
| 3239091459 | `pr19-emit-solve-validation.yml:243` | Missing-results fallback row has 1 column but header has 5 — breaks Markdown table rendering on Pattern C skip. |
| 3239154063 | `pr19-emit-solve-validation.yml:244` | Same single-column-fallback-row issue restated in round 3. |
| 3241281026 | `CHANGELOG.md:12` | LOC counts in changelog drifted (`~50` / `~170` vs actual `~115` / `~324`) — fix or drop. |
| 3241281075 | `SPRINT_LOG.md:1092` | Same LOC-drift issue in the Sprint 26 deliverables table. |

### 2.8 Other (4 comments) — fold into the 7 categories above

| ID | Path:line | Issue | Folds into |
|---|---|---|---|
| 3238239730 | `pr19-emit-solve-validation.yml:120` | `GAMS_INSTALLER_SHA256` placeholder will always fail `sha256sum -c` → block all PRs by default. | Logging visibility (PR description / changelog drift) + Error handling (blocking-default red check). |
| 3239091445 | `pr19-emit-solve-validation.yml:170` | Restatement of the placeholder-SHA256 blocking-default issue. | Same as above. |
| 3239154045 | `run_pr19_solves.py:224` | `--tier soft-fail` and standalone `--soft-fail` flag inconsistency — running `--tier soft-fail` without `--soft-fail` still hard-fails. | CLI design / Input validation (consistency between related flags). |
| 3241310106 | `pr19-emit-solve-validation.yml:21` | Job `timeout-minutes: 12` < worst-case runtime (11 models × (reslim + 30s) + GAMS install + comment/artifact upload). | CI configuration / Error handling (timeout risk on regression). |

These 4 "other" comments are not assigned their own category in the checklist (the 7-category structure comes from the Sprint 26 retrospective). They're addressed indirectly through the existing categories: docs-drift items via §Logging visibility, blocking-by-default via §Error handling, and CLI consistency via §Input validation. The §2.9 totals table counts them in the "Other (folded)" row so the per-category counts above sum cleanly to 38 unique primary assignments + 4 cross-cutting = 42.

### 2.9 Category totals

Counts below match the row counts of the §2.1–§2.8 tables exactly. Each comment is assigned to **one** primary category in §2 (no double-counting); §2.5's note clarifies the single cross-listing case (3238239775 → §2.1).

| Category | Comments (primary assignment) | Checklist items in CONTRIBUTING.md |
|---|---|---|
| Input validation | 8 | 5 |
| Pagination | 2 | 3 |
| Fork tolerance | 1 | 4 |
| Schema validation | 6 | 5 |
| Error handling | 6 | 5 |
| Marker uniqueness | 1 | 4 |
| Logging visibility | 14 | 6 |
| **Subtotal (7 categories)** | **38** | **32** |
| Other (folded into above categories via §2.8) | 4 | — |
| **Total** | **42** | **32** |

The CONTRIBUTING.md checklist is **32 items**, exceeding the §Task 10 acceptance criterion of ≥25 items. Per-category item counts are 5, 3, 4, 5, 5, 4, 6 — six categories sit within the prescribed 3–5 range; **Logging visibility is the documented exception at 6 items** because it absorbed the most PR #1396 comments (14/42 primary-assignment) — see the matching note in `PREP_PLAN.md` §Task 10 Acceptance Criteria.

---

## 3. Per-Category Item Rationale

Each category's checklist items derive directly from the comment cluster above, with two kinds of items:

1. **Literal restatement** — addresses the exact issue the reviewer raised on PR #1396.
2. **Defense-in-depth extension** — generalizes the issue to related failure modes the same root cause would produce in a different file or workflow.

### Input validation (5 items)

| Checklist item | Derived from |
|---|---|
| Env-var presence check | (general best practice — no direct comment, but Sprint 26 PR #1396 used `${{ secrets.X }}` interpolation; a defensive baseline). |
| Path validation | (general; complements item 3 below). |
| Safe-pattern check on path components, both at parse time AND consumer | 3241094136 + 3241094187 (both literally about model-name validation; checklist generalizes to all path components and emphasizes defense-in-depth at consumers). |
| Numeric type + range + zero-vs-falsy | 3239091432, 3239154011 (int parse), 3239816472, 3239907399 (negative reslim), 3239713498 (`or` swallows 0). |
| Subprocess-target guard via `shutil.which` or `FileNotFoundError` catch | 3238239775 (gams not on PATH). |

### Pagination (3 items)

| Checklist item | Derived from |
|---|---|
| Every `*.list*` call paginates | 3241462665, 3241462739 (both about `issues.listComments`). |
| Marker-search loop continues across pages | 3241462665 (specifically the "marker not on page 1 ≠ marker doesn't exist" semantic). |
| Exhausted-pagination → explicit create-vs-update decision (no silent fallthrough to "create") | Defense-in-depth extension — Sprint 26 PR #1396 didn't have a duplicate-comment incident in practice, but the silent-fallthrough is the failure shape the reviewer flagged. |

### Fork tolerance (4 items)

| Checklist item | Derived from |
|---|---|
| Write-permission API calls guarded by fork-check or try/catch | 3241094201 (literally: `issues.createComment`/`updateComment` fail 403 on fork PRs). |
| Secret-reading steps guarded by skip-on-fork / skip-when-missing | Defense-in-depth — `${{ secrets.* }}` returns empty string on fork PRs (not an error), but downstream shell commands using the empty string fail late with opaque errors. |
| Check-run status as fallback signaling channel for fork PRs | Defense-in-depth — if PR comments are unavailable on forks, the workflow's main result must still be visible somewhere (the check status). |
| Explicit "skipped because PR is from a fork" message | Defense-in-depth — fork contributors should see a clear skip reason, not a 403. |

### Schema validation (5 items)

| Checklist item | Derived from |
|---|---|
| Top-level structure check | 3239816515 (`targets["tier_0_1"]` raises `KeyError` on missing top-level key). |
| Per-entry shape check (`isinstance(entry, dict)` + required keys + type) | 3241212011 (per-entry `entry["model"]` validation). |
| Enum-valued fields validated against allow-list; unknown values are hard errors | 3238239761, 3239091423, 3239154032 (three rounds of the same unknown-tier silent-drop concern — the multiple rounds make the case for explicit "hard error, not warning" guidance). |
| Numeric fields type-checked AND range-checked at consumer (defense in depth) | 3241310033 (hand-edited reslim could be string/float, raises `TypeError`); reinforces input-validation items. |
| Validation errors include field name + source location (file path + line number / entry index) | Defense-in-depth — Sprint 26 PR #1396 reviewers asked for "include line number" in multiple comments (3239091432, 3239154011, 3239816472). |

### Error handling (5 items)

| Checklist item | Derived from |
|---|---|
| Every `subprocess.run` has `FileNotFoundError` AND `TimeoutExpired` handlers, both returning same-shape structured records | 3238239775 (FileNotFoundError), 3239907373 (TimeoutExpired schema drift). |
| Every file-system call wrapped in `try/except OSError` with named-path error + exit 2 | 3241310088 (`read_text` OSError), 3241462774 (`mkdir` OSError), 3241462806 (final `write_text` OSError). |
| Git tooling has fallback path (`$GITHUB_WORKSPACE`, `Path(__file__).resolve()`, `--repo-root` override) | 3239595479 (`git rev-parse --show-toplevel` no error handling). |
| Workflow-level pass/fail computed from ALL gating fields, not just easiest-to-check | 3239091401 (gate must include SOLVER STATUS, not just MODEL STATUS). |
| Late-stage failures (final `write_text`) don't lose in-memory results — fallback to stderr, exit 2 | 3241462806 (literal: write_text after per-model work loses results). |

### Marker uniqueness (4 items)

| Checklist item | Derived from |
|---|---|
| Per-comment-type HTML marker (`<!-- pr19-validation:bypass -->` vs `<!-- pr19-validation:results -->`) | 3241211963 (literally: substring 'PR19 Pre-Merge Solve Validation' shared between two comment types). |
| Scratch dirs include `$GITHUB_RUN_ID` / `$GITHUB_RUN_ATTEMPT` | Defense-in-depth — concurrent runs (multiple commits to same PR, reruns) sharing `/tmp/scratch/<model>` would corrupt each other. |
| `actions/cache` keys include all variability dimensions | Defense-in-depth — common GitHub Actions failure mode. |
| `actions/upload-artifact` names unique within a run (must include matrix dimensions) | Defense-in-depth — GitHub returns 409 on the second upload, breaking matrix jobs late. |

### Logging visibility (6 items)

| Checklist item | Derived from |
|---|---|
| Every gating field rendered in PR comment summary table | 3239907331 (MODEL STATUS shown, SOLVER STATUS missing → unexplained ❌). |
| Markdown tables well-formed in success AND fallback paths | 3238239746 (unnamed 5th column header), 3239091459, 3239154063 (single-column fallback rows in 5-column tables). |
| Step-comment annotations match actual gate logic | 3239595444 (step comment vs actual gate drift on SOLVER STATUS). |
| PR description / CHANGELOG / SPRINT_LOG match current workflow state | 3239154087, 3239154105, 3239461902, 3239461927, 3240647489, 3240647521 (six instances of stale `--soft-fail` / SHA256-placeholder text), 3241281026, 3241281075 (LOC drift). |
| Setup-failure messages reference current log lines / commands | 3239461942 (`sha256sum -c` message vs actual string-compare implementation). |
| Sensitive values redacted via `core.setSecret(...)` and the redaction is smoke-tested | Defense-in-depth — Sprint 26 PR #1396 didn't have a token leak, but workflow logs are world-readable on public repos and this is the standard guard. |

---

## 4. Sample PR Self-Review (applied to a hypothetical Sprint 27 CI-workflow PR)

**Scenario:** A Sprint 27 PR adds a new workflow `.github/workflows/sprint27-mid-sprint-audit.yml` that invokes `scripts/sprint_audit/changed_emit_artifacts.py` (Prep Task 9) on a schedule, posts a markdown summary as a PR comment on every open PR, and uploads the audit output as an artifact.

The PR author runs through the checklist below before requesting review:

### Input validation
- [x] All required env vars checked — `GITHUB_TOKEN` (presence required for `gh api`); `GITHUB_RUN_ID` (used in scratch path) — both checked at workflow entry.
- [x] All file paths validated — script verifies repo root via `Path(__file__).resolve().parents[2]` with explicit `is_dir()` check before `cd`.
- [x] No string-to-path concatenation from external input — workflow doesn't accept user-supplied model names; pulls them from `git log`.
- [x] No numeric inputs (only flags `--since-date` / `--since-commit`); date validation delegated to `git log --since` semantics, SHA validation already implemented via `git rev-parse --verify`.
- [x] `git` and `gh` subprocess targets pre-checked via `shutil.which('git')` / `shutil.which('gh')` at workflow start; missing tool exits 2 with a clear error.

### Pagination
- [x] Comment upsert wraps `octokit.rest.issues.listComments` in `actions/github-script` with `octokit.paginate(octokit.rest.issues.listComments, {...})`, so pagination is handled automatically across all pages.
- [x] Marker-search continues across pages via `octokit.paginate` (same call as above).
- [x] On exhausted pagination, workflow logs "marker not found, creating new comment" before the `createComment` call.

### Fork tolerance
- [x] PR-comment upsert wrapped in `try/catch`; on 403, falls back to `core.warning("PR is from a fork; audit summary skipped — see check status and artifact")`.
- [x] No secrets used; workflow runs entirely with `GITHUB_TOKEN`.
- [x] Check-run status reports audit result via the workflow exit code (artifact upload always runs even if comment upsert fails).
- [x] Fork-PR skip reason explicit in the workflow log: "Skipped PR comment upsert: PR is from a fork (head.repo.fork=true)".

### Schema validation
- [x] N/A — workflow doesn't consume JSON/YAML input beyond `git log` output (which is already shape-checked by the audit script's existing `_run_git` wrapper).

### Error handling
- [x] `subprocess.run` of `git log` / `gh api` wrapped — `FileNotFoundError` and `TimeoutExpired` both handled; both return structured `{error: ..., exit_code: 2}` records.
- [x] `Path(...).write_text()` (the artifact upload's source file) wrapped in `try/except OSError`; falls back to stderr dump.
- [x] No `git rev-parse` needed (workflow runs in checkout; uses `$GITHUB_WORKSPACE`).
- [x] Pass/fail gates only on the audit script's exit code (script's own pass/fail logic was validated in PR #1410 / Prep Task 9).
- [x] Final `write_text(json.dumps(results))` for the artifact wrapped — on OSError dumps to stderr before exit.

### Marker uniqueness
- [x] PR-comment marker: `<!-- sprint27-audit:mid-sprint-summary -->` — distinct from `<!-- pr19-validation:bypass -->` and `<!-- pr19-validation:results -->`.
- [x] Scratch dir: `/tmp/sprint27-audit-${GITHUB_RUN_ID}/` — run-unique.
- [x] No `actions/cache` usage in this workflow (audit is fast; not worth caching).
- [x] `actions/upload-artifact` name: `sprint27-mid-sprint-audit-${{ github.run_id }}-${{ github.run_attempt }}` — unique per run+attempt.

### Logging visibility
- [x] PR comment table renders all fields the gate depends on (only one field: audit exit code → pass/fail emoji).
- [x] Fallback Markdown table on missing artifact has the same column count as the success path (just the emoji column with `_(audit failed; see workflow log)_`).
- [x] Step comments match actual gate logic — only one gate (`if: steps.audit.outcome == 'success'`).
- [x] PR description, CHANGELOG entry, and Sprint 27 plan doc match the workflow's actual current behavior (no stale `--soft-fail`-style flags introduced).
- [x] No setup-failure-message templates beyond the standard `core.setFailed("Audit script failed: ${output}")`.
- [x] No sensitive values logged; `GITHUB_TOKEN` flows only through `actions/github-script`'s implicit authentication, never echoed.

**Result:** 27 / 32 items checked (5 marked N/A with reason). Author requests review with the filled-in checklist in the PR description.

---

## 5. Quality Gate

```bash
make typecheck && make format && make lint && make test
```

Docs-only diff; suite runs against unchanged `src/` + `tests/` state.

- `make typecheck`: PASS
- `make format`: PASS
- `make lint`: PASS
- `make test`: PASS

---

## 6. Related Documents

- `CONTRIBUTING.md` §"CI Workflow PR Checklist (PR23, Sprint 27 Prep Task 10)" (the deliverable)
- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 10
- `docs/planning/EPIC_4/SPRINT_26/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently" §"PR23"
- Sprint 26 PR #1396 — GitHub PR link, 42 review comments, 11 rounds
- Companion CI rules: PR14 emit-artifact requirement (CONTRIBUTING.md), PR19 solve-time validation (`.github/workflows/pr19-emit-solve-validation.yml`), PR22 audit script (`scripts/sprint_audit/changed_emit_artifacts.py`)

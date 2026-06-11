# Contributing to nlp2mcp

Thank you for your interest in contributing to nlp2mcp! This document provides essential guidelines for contributing to the project.

---

## Quick Start

**For comprehensive development guidelines, see [docs/development/AGENTS.md](docs/development/AGENTS.md)**

That document contains detailed information about:
- Complete project structure and module organization
- Detailed coding standards and conventions
- Testing practices and patterns
- Build system and development workflow
- Sprint planning process

---

## Essential Rules

### Before You Contribute

1. **Python Version**: This project requires **Python 3.12+**
   - Uses modern type hints (`dict`, `list`, `X | None`)
   - Uses `strict=` parameter on `zip()` calls
   - No `from typing import Dict, List, Optional` needed

2. **Development Setup**:
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   make install-dev
   ```

3. **Before Every Commit**:
   ```bash
   make format   # Auto-format with black + ruff
   make lint     # Check types and style
   make test     # Run all tests (must pass)
   ```

---

## Code Style

### Naming Conventions
- **Functions/modules**: `snake_case` (e.g., `normalize_equation`, `parse_model`)
- **Classes**: `CapWords` (e.g., `ModelIR`, `EquationDef`, `VarRef`)
- **Constants**: `UPPER_CASE` (e.g., `INF`, `WRAPPER_NODES`)
- **Private/internal**: Leading underscore `_helper_function`

### Modern Python 3.12 Type Hints
```python
# ✅ Correct (Python 3.12+)
def process(items: dict[str, int]) -> list[str] | None:
    ...

# ❌ Old style (don't use)
from typing import Dict, List, Optional
def process(items: Dict[str, int]) -> Optional[List[str]]:
    ...
```

### Required Practices
- ✅ Type hints on all public functions
- ✅ Docstrings on all public classes and functions
- ✅ `strict=True` or `strict=False` on all `zip()` calls (no bare `zip()`)
- ✅ Use `@dataclass(frozen=True)` for immutable data structures
- ✅ Line length: 100 characters (Black default)

---

## Testing Guidelines

### Test Organization
- Tests mirror source structure: `tests/ad/` for `src/ad/`, etc.
- Test files: `test_<module>.py` 
- Test functions: `test_<specific_behavior>`

### Test Requirements
- **All tests must pass**: `make test` (currently 602 tests)
- **Add tests for new features**: Maintain >85% coverage
- **Use pytest fixtures**: See existing tests for patterns
- **Parametrize variants**: Use `@pytest.mark.parametrize`

### Example Test Pattern
```python
import pytest
from src.ir.parser import parse_model_file

def test_specific_behavior():
    """Test description in plain English."""
    model = parse_model_file('examples/simple_nlp.gms')
    assert model.equations
    assert len(model.variables) > 0

@pytest.mark.parametrize("input,expected", [
    ("x", "x"),
    ("x_1", "x_1"),
])
def test_multiple_cases(input, expected):
    assert process(input) == expected
```

---

## Development Workflow

### Making Changes

1. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or: fix/issue-description
   ```

2. **Make your changes**:
   - Follow code style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Verify quality**:
   ```bash
   make format    # Auto-format code
   make lint      # Check types and style
   make test      # Run all tests
   ```

4. **Commit**:
   ```bash
   git add .
   git commit -m "Brief description of changes
   
   - Detailed point 1
   - Detailed point 2
   
   Addresses: #issue-number (if applicable)"
   ```

5. **Push and create PR**:
   ```bash
   git push -u origin feature/your-feature-name
   # Then create Pull Request on GitHub
   ```

### CI/CD Requirements

All PRs must pass:
- ✅ All 602+ tests passing
- ✅ Type checking (mypy)
- ✅ Linting (ruff)
- ✅ Code formatting (black)

---

## Emit-Affecting PRs — Required `.gms` Artifact in Diff (PR14)

**Codified per Sprint 25 retrospective recommendation PR14 (reaffirmation of Sprint 24's PR14).**

### The rule

If your PR modifies any of the following, you **MUST** include at least one regenerated `_mcp.gms` artifact from an affected model in the PR diff, and reviewers **MUST** read the relevant section of the regenerated file:

- `src/emit/**/*.py`
- `src/kkt/stationarity.py`
- `src/kkt/complementarity.py`
- `src/ad/derivative_rules.py`
- `src/ad/constraint_jacobian.py`

### Why

Sprint 25 PR #1349 introduced a per-instance `.l` override emit-ordering bug that clobbered ~120 lines of `.l = expr` overrides in `clearlak_mcp.gms`. The bug **passed all unit tests + `gams action=c` compile-only validation** and was caught only by Copilot reading the regenerated `clearlak_mcp.gms` during PR #1360 review — a 5-minute manual scan that would have caught it at the original PR #1349 merge.

Unit tests + compile validation cannot reliably detect emit-shape regressions because:
- Unit tests assert on AST/IR structure or per-token strings, not on the cross-cutting interaction of multiple emit groups.
- `gams action=c` accepts emit ordering that's syntactically valid but semantically clobbers (e.g., a `.l = expr` override followed by a bulk init `.l = default`).

The companion automated check is **PR19** (Sprint 26 Task 8 design — pre-merge solve-time validation CI). PR19 catches a different failure mode (PATH-solve-time regressions on canary models) and does **not** replace human review of the emitted `.gms`.

### Regeneration command

```bash
# Identify an affected model. Tier 0/1 canaries are usually the easiest to read:
#   dispatch, quocge, partssupply, prolog, sparta, gussrisk, ps2_f, ps3_f, ship, splcge, paklive
# Or a Pattern C target (camcge / cesam2 / fawley / otpop) if your PR targets that work.

# Regenerate just the affected model:
mkdir -p data/gamslib/mcp
.venv/bin/python -m src.cli "data/gamslib/raw/<model>.gms" \
    -o "data/gamslib/mcp/<model>_mcp.gms" \
    --skip-convexity-check --quiet

# Or regenerate the entire pipeline (slow — ~2-3h, only if your PR has corpus-wide impact):
.venv/bin/python scripts/gamslib/run_full_test.py --quiet
```

The regenerated `data/gamslib/mcp/<model>_mcp.gms` file (or files) goes in the PR diff alongside your `src/` changes.

### What reviewers must do

1. **Read the relevant section** of the regenerated `_mcp.gms` — at minimum the variable bounds / init group + the equation block(s) your PR touches.
2. **Look for clobber patterns** — duplicate assignments where one silently overrides the other (e.g., `var.l(idx) = expr` followed by `var.l(idx) = 1.0`).
3. **Look for ordering bugs** — clamps applied AFTER explicit overrides (e.g., `v.l('h0') = 0` followed by `v.l(h) = min(max(..., 1e-6), ...)` — see #1374 rocket case).
4. **Spot-check stationarity emit shape** — for `src/kkt/stationarity.py` PRs, read the `stat_<var>` blocks for affected variables; look for spurious `Sum((...,), ...)` wraps or missing cross-terms (#1334 / #1335 patterns).

### Exception: refactor-only PRs (`byte-stable-refactor` label)

If your PR is a **pure refactor** that you have byte-diff-verified produces zero changes in the emitted `_mcp.gms` files across all currently-translating models, you may apply the **`byte-stable-refactor`** PR label to bypass this rule.

**Reviewer responsibility when the label is present:** verify the PR description includes:
- The byte-diff verification command actually run (e.g., `diff -r /tmp/pre-mcp /tmp/post-mcp`).
- The result (e.g., "0 diffs across 141 currently-translating models per `PYTHONHASHSEED=0`").
- A justification for why no `.gms` artifact is included.

The canonical Sprint 24/25 example: PR #1353's #1271 dispatcher refactor — collapsed `_loop_tree_to_gams_subst_dispatch` into `_loop_tree_to_gams(node, *, token_subst=None)`, removed ~140 LOC, byte-diff verified zero diffs across 141 currently-translating models. That PR would have qualified for `byte-stable-refactor` in the Task 10 design.

**Estimated exception frequency:** ~1 of 100 emit-affecting PRs based on the Sprint 24/25 PR-title survey. The exception exists for the genuine refactor case; do not use it to bypass the rule for functional changes.

### Companion: `skip-emit-solve-ci` label (PR19, Sprint 26 Task 8)

Note that `byte-stable-refactor` is **distinct from** the `skip-emit-solve-ci` label (PR19 design — Sprint 26 Task 8 `DESIGN_PR19_SOLVE_TIME_CI.md`). The two labels gate different things:

| Label | Gates | Sprint of origin |
|---|---|---|
| `byte-stable-refactor` | This PR14 rule (regenerated `.gms` artifact in diff) | Sprint 26 Task 10 (this rule) |
| `skip-emit-solve-ci` | The PR19 CI workflow (pre-merge PATH solve on canaries) | Sprint 26 Task 8 |

A pure refactor PR may need both labels; a functional emit change typically gets neither.

---

## CI Workflow PR Checklist (PR23, Sprint 27 Prep Task 10)

**Codified per Sprint 26 retrospective recommendation PR23.**

Sprint 26 PR #1396 (PR19 CI extension — `.github/workflows/pr19-emit-solve-validation.yml` plus `scripts/ci/parse_pr19_targets.py` and `scripts/ci/run_pr19_solves.py`) required **11 rounds and 42 Copilot review comments** to land cleanly. The feedback clustered into seven recurring categories. Running through this checklist before requesting review on a CI-workflow PR is expected to compress the review iteration count to ~3–4 rounds.

### Scope

This checklist applies to PRs whose diff touches **any** of:

- `.github/workflows/*.yml` (or `.github/workflows/*.yaml`) — includes reusable workflows, which live in the same directory under the same suffixes and are called via `workflow_call` from a top-level workflow.
- `scripts/ci/*` (any file under `scripts/ci/`)
- Action definitions under `.github/actions/*` — includes composite actions (the most common reusable-action style); the `action.yml` / `action.yaml` plus any companion scripts live here.

If your PR touches none of these, this checklist does not apply (use the PR14 emit-artifact rule above if relevant).

### How to use

1. **PR author** copy-pastes the seven category blocks below into the PR description (or a `CHECKLIST.md`-style scratch comment) and ticks each item before requesting review.
2. **Reviewer** treats any unchecked item as an open question. An item that does not apply should be checked with a one-line `N/A — <reason>` annotation rather than left unchecked.

### Input validation

Every input — environment variable, CLI flag, file path, JSON/YAML field, target-list annotation — must fail fast on bad data with a concrete error message and exit code 2 (not a Python traceback or shell error). One of the larger clusters of Sprint 26 PR #1396 review comments fell here (see `docs/planning/EPIC_4/SPRINT_27/PR23_CHECKLIST_DESIGN.md` §2.1 for the authoritative per-category count and the per-comment table).

- [ ] All required environment variables are checked for presence via `os.environ.get("X")` followed by an explicit `None`-check that prints a clear stderr message and exits 2 — NOT raw `os.environ["X"]` (which raises `KeyError` and produces a Python traceback, contradicting the "no tracebacks" guidance above). If you must use `os.environ["X"]`, wrap it in `try/except KeyError` that converts the exception to the same clean-error + exit-2 path.
- [ ] All file paths and directory paths from user input are validated (existence, type, absolute-vs-relative as expected) before use, with errors that name the offending path.
- [ ] String inputs that become filesystem path components (model names, scratch-dir suffixes, artifact names) are validated against a safe pattern (e.g., `^[A-Za-z0-9_.-]+$`) and reject `..`, path separators, whitespace, and absolute-path prefixes. **Defense in depth:** validate both at parse time AND at the consumer that builds the path.
- [ ] Numeric inputs (`reslim`, `timeout`, `--limit N`) are validated for type AND range — `int()` parsing is wrapped in `try/except ValueError`, and downstream values are checked for non-negativity / minimum-value constraints. Zero-or-falsy distinction is explicit (`x is None`, not `x or default`).
- [ ] Subprocess targets that may be absent on the runner (`gams`, `git`, custom tools) are guarded — either pre-check with `shutil.which(...)` or catch `FileNotFoundError` from `subprocess.run` and return a structured failure record with exit code 2.

### Pagination

GitHub REST and `gh` CLI list endpoints are paginated with a default page size that is often smaller than real-world PR / comment / run / artifact counts. A workflow that calls `issues.listComments` (or any `*.list*` endpoint) on a long-lived PR will silently miss results past the first page. Sprint 26 PR #1396 produced 2 review comments in this category (both about `issues.listComments` for marker-based comment upsert).

- [ ] Every `*.list*` API call (issues, comments, runs, artifacts, pulls, reviews, …) either passes an explicit `per_page` AND paginates until a sentinel is found, OR uses the API's pagination helper (`octokit.paginate`; for shell scripts use `gh api --paginate` to stream pages, or `gh api --paginate --slurp` to aggregate all pages into a single JSON array for `jq` to consume in one shot).
- [ ] When the workflow searches a list for a marker (e.g., "find the existing PR comment with this header"), the search keeps paginating until either the marker is found or pagination is exhausted — finding nothing on page 1 is NOT the same as "marker does not exist".
- [ ] When pagination is exhausted without finding the marker, the workflow makes the **create vs update** decision explicitly (and logs which path it took) — a silent fallthrough to "create" produces duplicate comments on long-lived PRs.

### Fork tolerance

`pull_request` workflows running on fork-originating PRs operate with a read-only `GITHUB_TOKEN` and no access to repository secrets. Calls that work on same-repo PRs (commenting, labeling, dispatching, accessing secrets) commonly return 403 from forks and will fail the workflow if not guarded. Sprint 26 PR #1396 produced 1 review comment in this category (the PR-comment upsert calls had no fork-PR guard).

- [ ] Any API call that requires write permission (`issues.createComment`, `issues.updateComment`, `pulls.createReview`, labeling, dispatch) is guarded by either (a) an early `if: github.event.pull_request.head.repo.fork == false` step condition, OR (b) a `try/catch` that downgrades to `core.warning` so the rest of the workflow still completes.
- [ ] Any step that reads a repository secret (`${{ secrets.* }}`) has an explicit "skip-on-fork" or "skip-when-secret-missing" guard rather than failing late inside a shell command with an opaque error.
- [ ] If the workflow's main result (e.g., solve validation) must still report status on fork PRs, the **check-run status** (set via the workflow's exit code or via `actions/github-script` calling `checks.create`) is the fallback signaling channel — not the PR comment. Document the fallback in the PR description for the reviewer.
- [ ] Error messages from skipped/degraded steps explicitly say "skipped because PR is from a fork" rather than appearing as a generic 403 — fork contributors should not see a confusing failure.

### Schema validation

JSON / YAML inputs consumed by `scripts/ci/*` are frequently hand-edited (target lists, override files, status reports) and may bypass the upstream parser that wrote them. Every consumer must validate per-entry shape — type, required keys, value types — and exit 2 with an actionable error rather than raising `KeyError` / `TypeError` from deep in the code. Sprint 26 PR #1396 produced multiple review comments here, split between target-list / results-JSON consumer issues and the parser's "unknown tier" silent-drop (see `docs/planning/EPIC_4/SPRINT_27/PR23_CHECKLIST_DESIGN.md` §2.4 for the authoritative per-category count and the per-comment table).

- [ ] The top-level structure of every JSON / YAML input is checked (`isinstance(data, dict)`, required top-level keys present) before any indexing. Missing top-level keys produce a clear stderr message and exit code 2.
- [ ] Each list entry is shape-checked before field access — `isinstance(entry, dict) and "model" in entry and isinstance(entry["model"], str)` — and malformed entries produce a clear error naming the offending entry index/line.
- [ ] Enum-valued fields (`tier`, `status`, etc.) are validated against the explicit allow-list of known values. Unknown values produce a hard error with exit code 2 — they MUST NOT silently drop the entry or downgrade to a warning, because typos (`tier=patternc` vs `tier=pattern-c`) silently reduce coverage.
- [ ] Numeric fields in the JSON / YAML are type-checked AND range-checked at the consumer (not just at the parser that wrote the file) — `reslim` must be `int >= 0`, etc. Defense in depth against hand-edits that bypass the parser.
- [ ] When validation fails, the error message includes both the field name AND the source location (file path + line number if available, or entry index in the JSON array).

### Error handling

Every step that calls a subprocess, file-system operation, network resource, or external tool must wrap the call in error handling that produces a structured failure record (for downstream JSON consumers) AND an actionable stderr message (for the human reading the workflow log). Sprint 26 PR #1396 produced one of the larger review-comment clusters here — `FileNotFoundError`, `OSError`, `subprocess.TimeoutExpired`, and missing-error-field cases that crashed with tracebacks or produced inconsistent JSON (see `docs/planning/EPIC_4/SPRINT_27/PR23_CHECKLIST_DESIGN.md` §2.5 for the authoritative per-category count and the per-comment table; §2.5 also documents the single cross-listing case for the `gams` `FileNotFoundError` comment, which is assigned to §2.1 Input validation as its primary category).

- [ ] Every `subprocess.run([...])` call has explicit `FileNotFoundError` handling AND `subprocess.TimeoutExpired` handling. Both branches return a structured failure record with the same shape as the success record (no missing fields, no schema drift).
- [ ] Every `Path(...).read_text()` / `write_text()` / `.mkdir(...)` is wrapped in `try/except OSError`. The handler prints a concrete error naming the path and exits with code 2.
- [ ] Every `git rev-parse` (or other git-tooling call used for path/SHA discovery) has a fallback path — `$GITHUB_WORKSPACE`, `Path(__file__).resolve().parents[N]`, or a `--repo-root` CLI override — and a clear error when neither succeeds.
- [ ] Exit codes are propagated through `subprocess.run(..., check=False)` consumers: rc != 0 from a downstream tool is captured in the structured result, not swallowed. Workflow-level pass/fail is computed from the full set of structured fields (e.g., `rc == 0 AND MODEL_STATUS == 1 AND SOLVER_STATUS == 1`), not just the easiest-to-check field.
- [ ] Failures that happen AFTER per-entry work has completed (e.g., the final `write_text(json.dumps(results))`) are handled in a way that does not lose the in-memory results — either retry, or print results to stderr as a fallback, before exiting 2.

### Marker uniqueness

Concurrent runs of the same workflow (multiple commits to the same PR; parallel `matrix` jobs; reruns after a fix) MUST NOT collide on shared filesystem paths, cache keys, artifact names, or PR-comment marker substrings. Sprint 26 PR #1396 produced 1 review comment in this category (PR-comment marker substring matched across two distinct comment types). The remaining items below are defense-in-depth extensions.

- [ ] PR-comment upserts use a **unique HTML-comment marker per comment type** (e.g., `<!-- pr19-validation:bypass -->` vs `<!-- pr19-validation:results -->`) — not a substring match on the visible heading text, which can drift or collide.
- [ ] Scratch directory names include `$GITHUB_RUN_ID` (or another run-unique token like `$GITHUB_RUN_ATTEMPT`) so concurrent runs of the same workflow do not stomp each other's `/tmp/scratch/<model>` subdirectories.
- [ ] `actions/cache` keys include all dimensions that should produce a fresh cache (`os`, `matrix.*`, `hashFiles('lockfile')`, workflow version) — never a static string that would silently share a stale cache across unrelated runs.
- [ ] `actions/upload-artifact` artifact names are unique within a workflow run — if a job runs in a `matrix`, the artifact name must include the matrix dimensions (otherwise GitHub returns 409 on the second upload and the workflow fails late).

### Logging visibility

The workflow log and the PR-comment summary are the primary debugging surfaces for failures. Each pass/fail signal that the workflow enforces MUST be visible in both places, with no silent gaps between "what the gate checks" and "what the comment says". **This was the largest review-comment cluster on Sprint 26 PR #1396** — stale step-comments, stale PR-description text, table-rendering bugs, missing columns for fields the gate depends on, and LOC counts in changelogs that drifted from reality (see `docs/planning/EPIC_4/SPRINT_27/PR23_CHECKLIST_DESIGN.md` §2.7 for the authoritative per-category count and the per-comment table; the size of this cluster is why the matching CONTRIBUTING.md checklist below has 6 items rather than the 3–5 prescribed for other categories).

- [ ] **Every field that the pass/fail logic depends on** is rendered in the PR-comment summary table (or other user-visible output). If the gate checks `rc + MODEL STATUS + SOLVER STATUS`, all three appear as columns — never let the table show only two so failures look unexplained.
- [ ] Markdown tables in PR comments are well-formed in **all** rendering paths — both the success path AND every fallback path (e.g., when an upstream step failed and the JSON results file is missing, the fallback row has the same column count as the header).
- [ ] Step-comment annotations (`# This step hard-fails when ...`) match the actual gate logic implemented downstream. When you change the gate, grep for the old condition in step comments and PR-description text and update both.
- [ ] PR description text, CHANGELOG entries, and SPRINT_LOG deliverable tables match the actual workflow / script state. Common drift sources: placeholder values that were later pinned (`<SHA256-TBD>`), CLI flags that were renamed or merged into other flags (`--soft-fail` → `--tier soft-fail`), and LOC counts that grew during review iteration.
- [ ] Setup-failure messages reference **current** log lines / commands. When you change an install or validation step, search the workflow's failure-comment template for the old command/marker (`sha256sum -c`, etc.) and update the message to point at the new diagnostic output.
- [ ] Sensitive values (tokens, installer URLs that embed credentials, signed-URL secrets) are redacted from log output via `core.setSecret(...)` or equivalent — and the redaction is exercised in a smoke test, not just trusted from the masked-string convention.

### Related

- Sprint 26 PR #1396 review history (42 comments across 11 rounds — input for this checklist).
- Sprint 27 Prep Task 10 design doc: `docs/planning/EPIC_4/SPRINT_27/PR23_CHECKLIST_DESIGN.md` (per-category rationale + sample PR self-review).
- Companion CI-workflow rule: PR19 emit-solve validation labels (above) and PR22 audit script (above).

---

## Emit-PR `.gms` Diff Workflow (PR22, Sprint 27 Prep Task 9)

**Codified per Sprint 26 retrospective recommendation PR22.**

The companion automation to the PR14 rule above. The PR14 rule says *"include a regenerated `.gms` artifact from an affected model"*; PR22 helps you and reviewers enumerate **which** artifacts are affected by an upstream `src/` change, and powers the mid-sprint retest comparison surface.

### Script

`scripts/sprint_audit/changed_emit_artifacts.py` scans `git log` for changes under `data/gamslib/mcp/` matching the emit-artifact suffixes `*_mcp.gms` and `*_mcp_presolve.gms`, grouped by triggering commit. Three output formats (`text`, `markdown`, `json`) and two report-header modes (`pr14`, `retest`).

### Per-PR usage (PR14 companion)

Before opening an emit-affecting PR, list every `.gms` artifact your branch has regenerated since branching off `main`:

```bash
# Get the PR base SHA (usually the merge-base with main):
BASE_SHA=$(git merge-base main HEAD)

.venv/bin/python scripts/sprint_audit/changed_emit_artifacts.py \
    --since-commit "$BASE_SHA" --format markdown --mode pr14
```

Paste the markdown output into the PR description under a `## Emit artifacts touched` heading. Reviewers use it as the checklist for PR14 §"What reviewers must do".

### Mid-sprint retest usage

At each mid-sprint retest checkpoint, generate the comparison surface relative to the Sprint Day 0 anchor commit (recorded in `docs/planning/EPIC_4/SPRINT_<N>/PLAN.md` Day 0):

```bash
SPRINT_DAY0=<the recorded Day 0 SHA>

.venv/bin/python scripts/sprint_audit/changed_emit_artifacts.py \
    --since-commit "$SPRINT_DAY0" --format markdown --mode retest \
    > /tmp/sprint_retest_surface.md
```

Paste `/tmp/sprint_retest_surface.md` into the retest entry in `SPRINT_LOG.md`. This replaces the Sprint 26 practice of manually maintaining the retest model list in a frozen `PLAN_PROMPTS.md` (Day 12 staleness incident).

### Why two flags (`--since-date` vs `--since-commit`)

`git log --since <DATE>` is date-only — it does not accept commit SHAs. The script exposes two distinct flags rather than one overloaded `--since`:

| Flag | When to use |
|---|---|
| `--since-date "2026-04-22"` | Quick ad-hoc lookups; OK if cross-day commit boundary doesn't matter. |
| `--since-commit <SHA>` | **Preferred for mid-sprint retests** — commit boundaries are unambiguous, eliminating timestamp-edge cases. |

### Exit codes

- `0` — success (zero or more commits found).
- `2` — invalid arguments (e.g., bad `--since-commit` SHA, both flags set, neither flag set).

### Related

- This rule's companion: `## Emit-Affecting PRs — Required .gms Artifact in Diff (PR14)` above.
- Design document: `docs/planning/EPIC_4/SPRINT_27/PR22_SCRIPT_DESIGN.md`.

---

## Phase 0 Acceptance Gates (PR20, Sprint 27 Prep Task 2)

### The hard rule

**Any issue whose Phase 1 design touches `src/ad/`, `src/kkt/`, or `src/emit/` MUST have a `## Phase 0: Acceptance Gate` section in its `docs/issues/ISSUE_<N>_*.md` file BEFORE any `src/` commit lands for that issue.**

The Phase 0 section must contain exactly these 4 subsections, each rendered as a markdown `###` heading (do NOT use bold text or `####` — verification grep matches the literal `### <name>` form):

- `### Hand-Derived KKT Shape` — formal Lagrangian + stationarity / primal-feasibility / complementarity equations for the target equation(s)
- `### Expected Emit Pattern` — what the regenerated `<model>_mcp.gms` should contain (by equation name + index pattern). **This is the prep-doc *hypothesis*, not an established fix surface** — under PR24 (below) the actual `file:line` surface is established by a Day-0 trace and confirmed before any `src/` change.
- `### Verification Methodology` — explicit byte-comparison or pattern-match command(s) to run against the regenerated emit. **The standard Case-(a/b/c) emit-bug-vs-non-convexity discriminator is the KKT-residual harness — `.venv/bin/python scripts/diagnostics/kkt_residual.py <model.gms>` (PR27).** Emit-touching PRs must also pass the golden-staleness check (PR26).
- `### PROCEED/REPLAN Signal` — binary criteria for whether Phase 1 `src/` implementation may begin. **Must include a `Traced Fix-Surface (Day-0)` line** citing the `file:line` surface established by the Day-0 trace plus the trace command/evidence (PR24); a PROCEED that cites only the prep-doc surface is invalid.

### Why this exists

Unit tests, integration tests, and byte-stability gates are **insufficient** to catch alias-AD pipeline architectural-drift regressions. Sprint 26 had two incidents proving this:

- **PR #1379 (Phase A consolidated zero-offset builder, Sprint 26 Day 1):** shipped through PR19's CI target list with all quality gates GREEN, then PR #1399 reviewer-driven retest discovered the new gate predicate had regressed 15 non-target models with `path_syntax_error`. Filed as #1398 with the prep-task PR20 codification + PR19 target-list widening as structural mitigations.
- **PR #1394 (#1335 in-place scalar-eq fix, Sprint 26 Day 9):** shipped with `make typecheck && make format && make lint && make test` clean, but reviewer hand-derived the expected KKT shape and identified that the emit's `stat_p(tt)` body was structurally wrong (would have produced wrong solver behavior). Rolled back during PR review; reclassified as #1393 + #1335 in-place reopen.

Both incidents prove: **only hand-derived KKT comparison reliably surfaces architectural-drift regressions that GREEN quality gates miss.**

### Exception scope

Phase 0 is NOT required for changes that touch ONLY:

- `scripts/**` (pipeline / CI / audit scripts)
- `tests/**` (test-only changes; new test cases without `src/` changes)
- `docs/**` (documentation, planning docs, retrospectives)
- `.github/**` (CI workflows)
- `data/**` (regenerated artifacts; status JSON updates)

A PR that touches BOTH `src/{ad,kkt,emit}/` AND any of the exempted paths still requires Phase 0 for the `src/` portion.

### Workflow

1. **File / re-open the issue** with the bug description, reproducer, and investigation pointers.
2. **Author the `## Phase 0: Acceptance Gate` section** in `docs/issues/ISSUE_<N>_*.md` with the 4 required subsections. Use existing Phase 0 sections (e.g., `docs/issues/ISSUE_1356_*.md` from Sprint 27 Prep Task 2) as format reference.
3. **Run the Verification Methodology commands** against a prototype patch (model-name-guarded to avoid regression risk) BEFORE writing the production fix. Capture the PROCEED / REPLAN signal in the issue.
4. **If PROCEED:** proceed to Phase 1 (`src/` implementation) with the hand-derived KKT shape as the acceptance reference. Cite Phase 0 in the PR description.
5. **If REPLAN:** either revise the Phase 0 hand-derivation (if it was wrong), or rescope the issue (e.g., file a successor issue with a different fix-surface diagnosis). Do NOT commit `src/` changes against a REPLAN'd Phase 0.

### Reviewer expectations

PR reviewers for `src/{ad,kkt,emit}/`-touching PRs MUST:

- Check that the linked issue has a `## Phase 0: Acceptance Gate` section
- Verify the PR description references the Phase 0 PROCEED signal (or explicitly explains why it doesn't apply — e.g., exception-scope follow-on cleanup that doesn't change emit shape)
- Run the Verification Methodology commands locally and confirm the emit shape matches the Expected Emit Pattern

A PR missing Phase 0 should be blocked by the reviewer until Phase 0 is authored, NOT merged with a "follow-on TODO" note.

### Related

- Sprint 26 retrospective §"What We'd Do Differently" PR20 codification rationale: `docs/planning/EPIC_4/SPRINT_26/SPRINT_RETROSPECTIVE.md`
- Sprint 27 Prep Task 2 (the codification of this rule): `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 2

---

## Day-0 Traced Fix-Surface (PR24) + Projection Discipline (PR25) (Sprint 28 Prep Task 3)

These two rules **extend** the Phase 0 Acceptance Gate (PR20) and the PR14/PR19/PR22 emit-artifact discipline; they do not replace them. They were codified after Sprint 27, where the prep-doc fix surface was **wrong 4×** (Days 0/6/11/12 — the real surfaces were `src/kkt/stationarity.py`, `src/ir/ast.py`, and the emit restore pass, NOT the AD sites the prep named) and the Day-0 "+6 firm Match" projection over-counted three `path_syntax_error → model_infeasible` bucket-forward moves (fawley/otpop/camcge) as Solve/Match gains.

### PR24 — Day-0 Traced Fix-Surface (hard rule)

**The prep doc records the symptom and a minimal reproducer. The fix surface (`file:line`) is established by a Day-0 trace at sprint start and is NEVER carried as fact from the prep doc. A Phase-0 PROCEED signal MUST cite the *traced* surface, with the trace command/evidence recorded.**

- The prep-doc / issue-doc `### Expected Emit Pattern` is a **hypothesis**, not an established surface.
- At sprint Day 0, run a trace to establish the actual `file:line`: instrument the candidate code paths, emit the target `<model>_mcp.gms`, locate the offending row, and identify which code path builds it. The KKT-residual harness (PR27) is the standard tool for confirming the offending residual.
- The Phase-0 `### PROCEED/REPLAN Signal` subsection MUST contain a **`Traced Fix-Surface (Day-0)`** line: the confirmed `file:line` + the trace command + the evidence (KKT-residual harness output or instrumented-log excerpt). A PROCEED that cites only the prep-doc surface is invalid and must be blocked by the reviewer.
- This **strengthens** PR20 rather than replacing it: PR20 still requires the hand-derived KKT shape and the 4-subsection gate; PR24 only adds that the surface named in the gate is the *traced* one (not the prep-doc guess).

### PR25 — Projection Discipline (genuine gain vs bucket-forward)

**Every Solve/Match projection — Day-0 and at every checkpoint — labels each delta as a genuine bucket-to-success transition or a bucket-forward move within the failure set; only genuine gains count toward sprint targets. Projections must show both tallies.**

- **Genuine gain** = a bucket-to-success transition: a failure bucket → `model_optimal` (Solve credit), or `model_optimal`/mismatch → match (Match credit).
- **Bucket-forward** = a move within the failure set (e.g., `path_syntax_error → model_infeasible`): real progress, but **not** target credit.
- Only genuine gains are tallied toward the Solve / Match targets; bucket-forward moves are reported separately as "progress, not target credit."
- **Rationale:** the Sprint 27 Day-0 "+6 firm Match" over-counted fawley/otpop/camcge, which only moved `path_syntax_error → model_infeasible` (bucket-forward) and yielded no Solve/Match. The canonical Sprint 28 application is `docs/planning/EPIC_4/SPRINT_28/BASELINE_METRICS.md` §3 (PR25 projection table).

### Related

- Sprint 27 retrospective §"What We'd Do Differently" #1 (fix surfaces) + #2 (projections): `docs/planning/EPIC_4/SPRINT_27/SPRINT_RETROSPECTIVE.md`
- Sprint 28 Prep Task 3 (the codification of these rules): `docs/planning/EPIC_4/SPRINT_28/PREP_PLAN.md` §Task 3
- PR26 (golden-staleness CI check) + PR27 (KKT-residual harness) — delivered as Sprint 28 Priorities 8 and 9; referenced from the Phase-0 `### Verification Methodology` template above.

---

## Project Structure

```
nlp2mcp/
├── src/                   # Source code
│   ├── ad/                # Automatic differentiation
│   ├── emit/              # GAMS MCP code generation
│   ├── gams/              # Parser (Lark grammar)
│   ├── ir/                # Intermediate representation
│   ├── kkt/               # KKT system assembly
│   └── utils/             # Utilities
├── tests/                 # Test suite (mirrors src/)
│   ├── unit/              # Fast, isolated tests
│   ├── integration/       # Cross-module tests
│   ├── e2e/               # End-to-end pipeline tests
│   └── validation/        # Mathematical correctness
├── examples/              # Sample GAMS NLP models
├── docs/                  # Documentation
│   ├── ad/                # AD module documentation
│   ├── architecture/      # System architecture
│   ├── emit/              # Code generation docs
│   ├── kkt/               # KKT assembly docs
│   ├── planning/          # Sprint plans & retrospectives
│   └── development/       # Development guidelines (AGENTS.md)
└── scripts/               # Development scripts
```

---

## Sprint Planning Process

This project follows a structured sprint planning process:

1. **Planning Phase**: Each sprint begins with detailed planning
   - Review PROJECT_PLAN.md for sprint scope
   - Create SPRINT_X/PLAN.md with day-by-day breakdown
   - Conduct planning reviews to identify risks
   - Create PREP_PLAN.md with pre-sprint tasks

2. **Execution Phase**: Follow the sprint plan
   - Daily progress tracking
   - Mid-sprint checkpoints (Days 3, 6, 8)
   - Integration health checks
   - Continuous testing

3. **Retrospective Phase**: Learn and improve
   - Document what went well / needs improvement
   - Create action items for next sprint
   - Update metrics and statistics

See [docs/planning/EPIC_1/README.md](docs/planning/EPIC_1/README.md) for sprint summaries and retrospectives.

---

## Getting Help

- **Documentation**: Start with [README.md](README.md) and [docs/](docs/)
- **Development Guidelines**: See [docs/development/AGENTS.md](docs/development/AGENTS.md)
- **System Architecture**: See [docs/architecture/SYSTEM_ARCHITECTURE.md](docs/architecture/SYSTEM_ARCHITECTURE.md)
- **Issues**: Check [GitHub Issues](https://github.com/jeffreyhorn/nlp2mcp/issues)

---

## Code of Conduct

- Be respectful and constructive
- Focus on technical merit
- Help others learn and improve
- Follow professional standards

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Current Status**: Sprint 3 Complete (602 tests passing, 89% coverage)  
**Active Development**: Sprint 4 Preparation Phase

For detailed development guidelines, workflows, and patterns, please read:
📖 **[docs/development/AGENTS.md](docs/development/AGENTS.md)**

# Design: Pre-Merge Solve-Time Validation CI Extension (PR19)

**Date:** 2026-05-08
**Task:** Sprint 26 Prep Task 8 (Design Pre-Merge Solve-Time Validation CI)
**Branch:** `planning/sprint26-task8`
**Status:** Design only — workflow file lands during Sprint 26 execution.

---

## Background

Sprint 25's PR #1308 (Pattern C launch fix) passed all unit tests and `gams action=c` compile-only validation, but produced a **locally-infeasible MCP at full PATH solve**. This was caught only via the Day 14 final pipeline retest, leading to the same-sprint #1351 rollback. Sprint 25 retrospective recommendation **PR19** codifies the mitigation:

> Structural gates that change emit shape should require a full PATH solve (or at minimum, a `model_optimal_presolve` round-trip) on the target model BEFORE merge — not just unit + compile-only validation.

Sprint 26's Priority 1 (Pattern C generalization) is structurally similar. PR19 is the codified pre-merge solve-time validation that catches this failure mode.

---

## Constraint: GAMS is not currently installed in CI

The repo's existing CI workflows (`ci.yml`, `gamslib-regression.yml`, `lint.yml`, `performance-check.yml`, `nightly.yml`) do not install GAMS. The existing `tests/integration/test_pipeline_determinism.py` harness only invokes the Python CLI as a subprocess and compares emitted MCP bytes — it does **not** spawn GAMS at all. The closest thing to a GAMS-invoking validation harness is `scripts/gamslib/test_solve.py::solve_mcp` (a developer-machine pipeline script, not a CI test — and it runs a full PATH solve via `reslim=...` + `Solve ... using MCP`, not a compile-only check), and Sprint 25's `DESIGN_ALIAS_AD_ROLLOUT.md` §6.3 explicitly notes "CI does not install GAMS".

**PR19 fundamentally requires GAMS in CI.** This design proposes **GAMS demo install** as the path forward — the demo edition is free, has variable / equation / nonzero limits that all 11 Tier 0/1 canary models fit within (largest is `quocge` at 158 equations / 158 variables / 671 nonzeros — well under the 300 / 300 / 2000 demo cap), and adds ~90s install overhead per CI run.

If the GAMS demo install proves problematic during Sprint 26 implementation, the fallback is a self-hosted runner with a full GAMS license — but that introduces infrastructure overhead and is out of scope for the prep task. PR19 implementation in Sprint 26 should attempt the demo path first.

---

## Trigger Conditions

The PR19 workflow runs on `pull_request` only (not on `push: main` — main should already be validated, and re-running the slow PATH solve on every main push is wasteful).

### Trigger file patterns

```yaml
paths:
  - "src/emit/**/*.py"
  - "src/kkt/stationarity.py"
  - "src/kkt/complementarity.py"
  - "src/ad/derivative_rules.py"
  - "src/ad/constraint_jacobian.py"
  - "scripts/ci/parse_pr19_targets.py"
  - "scripts/ci/run_pr19_solves.py"
  - ".github/workflows/pr19-emit-solve-validation.yml"
  - ".github/path-solve-ci-targets.txt"
```

**Rationale for each:**

- `src/emit/**/*.py` — direct emit-shape changes (per PR19 origin).
- `src/kkt/stationarity.py` — Sprint 26 Priority 1 fix-site for Pattern C generalization (camcge / cesam2 work). Also #1334 fix-site (`_add_indexed_jacobian_terms` per Task 7 correction).
- `src/kkt/complementarity.py` — #1357 / #1356 fix-site for comp_up subset/superset domain widening (Sprint 27 carryforward, but adding now since the trigger surface should be stable).
- `src/ad/derivative_rules.py` — `_diff_sum` and related AD-rule changes (#1335 lives upstream of this in `constraint_jacobian.py`, but `derivative_rules.py` directly shapes the emit too).
- `src/ad/constraint_jacobian.py` — #1335 fix-site (`if eq_domain:` scalar-equation gate at `:986` + `:1107` per Task 7 finding).
- `scripts/ci/parse_pr19_targets.py` + `scripts/ci/run_pr19_solves.py` — the workflow's helper scripts. If a PR changes either script without touching the workflow YAML, the workflow needs to re-run so script regressions don't merge unnoticed (e.g., a parser bug that silently drops Pattern C targets, or a solve-runner bug that swallows non-zero exit codes).
- `.github/workflows/pr19-emit-solve-validation.yml` — workflow self-changes need to re-validate.
- `.github/path-solve-ci-targets.txt` — target-list changes need to re-validate.

### PR-label exception

Refactor-only PRs that don't change emit semantics can opt out via the `skip-emit-solve-ci` PR label (plain text, no brackets — consistent with the planned `byte-stable-refactor` label from Task 10). When the label is present, the workflow takes an **early-success bypass path**: subsequent solve steps are gated `if: steps.check-label.outputs.skip != 'true'`, the workflow exits 0 (reports as success in the Actions UI; GitHub Actions does not provide a separate "skipped" status for label-gated workflow bodies), and a dedicated PR-comment step posts a visible bypass notice so reviewers see the skip in the PR conversation, not just the Actions tab.

**Reviewer responsibility:** if the PR adds the `skip-emit-solve-ci` label, reviewers must verify that byte-diff regression tests cover the change before merge. Sprint 25's `#1271` dispatcher refactor is the canonical example: 140 LOC removed, byte-diff verified zero diffs across 141 translating models — `skip-emit-solve-ci` would be appropriate there.

---

## Target Model List

**Planned file path:** `.github/path-solve-ci-targets.txt` (to be committed during Sprint 26 implementation alongside the workflow YAML — this PR is design-only and does NOT add the file).
**Format:** One model per line. Optional inline annotation `# tier=<0|1|pattern-c>`. Blank lines and lines starting with `#` are ignored. Example:

```
# Tier 0/1 canaries — hard-fail on regression (per Sprint 25 PR12 byte-stability harness).
# These models all reach MODEL STATUS 1 (Optimal) on current main and are tracked
# byte-stable across PYTHONHASHSEED values per BASELINE_METRICS.md §6.
dispatch         # tier=0
quocge           # tier=1
partssupply      # tier=1
prolog           # tier=1
sparta           # tier=1
gussrisk         # tier=1
ps2_f            # tier=1
ps3_f            # tier=1
ship             # tier=1
splcge           # tier=1
paklive          # tier=1

# Pattern C target models — soft-fail (informational only). Currently fail at compile
# with $141 / $171 cascades; expected to pass once Sprint 26 Priority 1 lands the
# Pattern C generalization. Once they pass, promote to tier=1 (hard-fail).
camcge           # tier=pattern-c
cesam2           # tier=pattern-c
fawley           # tier=pattern-c
otpop            # tier=pattern-c
```

### Per-tier semantics

| Tier | Models (n) | Failure handling | Rationale |
|---|---|---|---|
| `0` | 1 (`dispatch`) | **Hard-fail** | The canonical canary — minimum complexity, fast solve, byte-stable in all 5 PR12 harness configurations. Any regression here is high-signal. |
| `1` | 10 (per Sprint 25 SPRINT_LOG.md Day 0) | **Hard-fail** | Tier 1 alias-using and matching canaries; covered by PR12 harness; all reach MODEL STATUS 1 (Optimal) on current main. |
| `pattern-c` | 4 (Sprint 26 Priority 1 targets) | **Soft-fail** (warning + PR comment, exit 0) | Currently fail at compile with `$141` / `$171` cascades. Soft-fail provides a per-model status signal during the Sprint 26 fix work without blocking unrelated PRs. Once a model starts passing, promote to `tier=1`. |

### Why this list, not all 142 in-scope models

Per Unknown 6.2 research, the 11 Tier 0/1 canaries are the right hard-fail surface because:
- **Sprint 25 PR12 harness already enforces byte-stability** on these models — a PATH-solve regression is the natural complement.
- **Total ~15s sum of local PATH solves** (see §"Local Timing Verification" below) — well within the per-model 30s budget × 11 models = 330s worst case.
- **Adding all 142 in-scope models would add ~7-15min CI time** (assuming average 3-7s per model × 142) and substantially inflate PR latency for marginal additional signal — most non-canary in-scope models have not historically caught emit regressions early. Sprint 26 can revisit if Priority 1 work shows otherwise.

The 4 Pattern C target models are added as **soft-fail informational** signal: when a Pattern C fix lands, the workflow output documents which target model's compile / solve passed for the first time. This becomes pre-merge evidence for the Sprint 26 Priority 1 acceptance criteria.

---

## PATH Timeout

**Per-model timeout: 30 seconds.** Set via the `reslim=30` GAMS option on the solve invocation. Run with `cwd=` set to the repo root and `ScrDir=` redirecting only the scratch files (this mirrors `scripts/gamslib/test_solve.py::solve_mcp` per Sprint 25 #1345/#1346/#1347 fixes — the repo-relative `$include "data/gamslib/raw/<model>.gms"` line in `--nlp-presolve`-emitted MCPs requires the working directory to be the repo root):

```bash
# Run from repo root; redirect only scratch files via ScrDir.
# Do NOT set curdir= — it would break the repo-relative `$include` resolution
# in any presolve-variant MCPs that reach this list in the future.
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"
gams "data/gamslib/mcp/${m}_mcp.gms" lo=0 reslim=30 \
  ScrDir=/tmp/pr19-scratch/$m \
  o=/tmp/pr19-scratch/$m/${m}_mcp.lst
```

(None of the 15 currently-listed target models — 11 Tier 0/1 canaries + 4 Pattern C target models — use `$include`. The `cwd=$REPO_ROOT` + `ScrDir=` recipe is preserved for future-proofing in case a `_presolve.gms` variant joins the target list.)

### Local timing verification (current main, 2026-05-08)

Per Unknown 6.1 research:

| Model | rc | Wall time | MODEL STATUS |
|---|---|---|---|
| dispatch | 0 | 4.26s | 1 Optimal |
| quocge | 0 | 1.44s | 1 Optimal |
| partssupply | 0 | 1.03s | 1 Optimal |
| prolog | 0 | 1.17s | 1 Optimal |
| sparta | 0 | 1.01s | 1 Optimal |
| gussrisk | 0 | 1.03s | 1 Optimal |
| ps2_f | 0 | 1.14s | 1 Optimal |
| ps3_f | 0 | 1.08s | 1 Optimal |
| ship | 0 | 1.05s | 1 Optimal |
| splcge | 0 | 1.05s | 1 Optimal |
| paklive | 0 | 1.01s | 1 Optimal |
| camcge | 2 | 0.55s | (compile error `$141`, fast-fail) |
| cesam2 | 2 | 0.58s | (compile error `$141`, fast-fail) |
| fawley | 2 | 0.56s | (compile error `$171`, fast-fail) |
| otpop | 2 | 0.54s | (compile error `$141`, fast-fail) |

Sum of Tier 0/1 wall times: **15.27s**. Timing run details:

- **Repo commit:** `4b65f4b9` (current `main` after PR #1371 merge, 2026-05-08)
- **GAMS version:** 53.1.0 (build 6a03d3b9 — internal GAMS build hash, not a git commit)
- **Machine:** macOS / DEX-DEG x86 64bit

### CI overhead estimate

| Component | Time (CI worst case) |
|---|---|
| GAMS demo install | ~90s |
| Repo checkout + Python setup | ~30s (cached) |
| Sequential PATH solves (11 canaries × 30s budget) | ≤ 330s |
| Pattern C fast-fail compile (4 × ~5s) | ≤ 20s |
| Result aggregation + PR comment | ≤ 10s |
| **Total** | **≤ ~8 minutes** |

Realistic mid-case (assuming CI is ~2× slower than local): 11 × ~3s + 4 × ~1s + ~130s overhead = ~167s ≈ **~3 min**. Within budget; comparable to existing `ci.yml` which runs ~3-4min for the test job.

### Why 30s, not 10s or 60s

- **7× margin over reference machine local times** (largest canary = dispatch at 4.26s; 30s / 4.26s ≈ 7×). Smaller canaries (sparta / paklive ≈ 1.01s) get ~30× margin.
- **Avoids flakiness** from CI machine variance — Unknown 6.1 risk.
- **Catches cases where a regression makes a previously-fast solve hang or thrash** — exactly the failure mode PR19 is designed to catch (the Pattern C launch fix made the launch MCP locally infeasible, which would have manifested as a PATH solve that runs longer than usual or returns MODEL STATUS 5).

If Sprint 26 implementation finds 30s is too tight on a specific model (e.g., if `paklive` starts running closer to 25s due to CI hardware variance), the per-model budget can be made configurable via the target-list file annotation (e.g., `paklive  # tier=1 reslim=60`).

---

## Failure Handling

### Hard-fail (Tier 0 / Tier 1 canaries — 11 models)

For each Tier 0/1 model, the workflow asserts:

1. **GAMS exit code = 0** (no compile errors).
2. **MODEL STATUS = 1 (Optimal)** in the `.lst` file.
3. **SOLVER STATUS = 1 (Normal Completion)**.

Any other state on a Tier 0/1 model fails the workflow. Reviewers must investigate before merge.

### Soft-fail (Pattern C target models — 4 models)

For each Pattern C target model, the workflow records the same 3 properties but does **not** fail the workflow on a non-Optimal result. Instead:

- A warning annotation (`::warning::`) is added to the GitHub Actions UI.
- A PR comment summarizes per-model status (per `gamslib-regression.yml`'s pattern of using `actions/github-script@v7`).
- The workflow exit code is 0 if all Tier 0/1 models pass, regardless of Pattern C target status.

**Promotion mechanism:** when a Pattern C model starts passing (e.g., once Sprint 26 lands the camcge fix), update `.github/path-solve-ci-targets.txt` to change `camcge  # tier=pattern-c` → `camcge  # tier=1`. The next PR will hard-fail if camcge regresses, which is the desired post-fix behavior.

### PR comment format

```markdown
## 🧪 PR19 Pre-Merge Solve Validation Results

**Trigger:** files changed under `src/emit/`, `src/kkt/stationarity.py`, ...
**Run:** [123456] (3m 24s)

### Tier 0/1 canaries (hard-fail surface) — 11/11 ✅

| Model | rc | Time | MODEL STATUS |
|---|---|---|---|
| dispatch | 0 | 4.5s | 1 Optimal ✅ |
| quocge | 0 | 1.6s | 1 Optimal ✅ |
| ... | ... | ... | ... |

### Pattern C target models (soft-fail / informational) — 0/4 passing

| Model | rc | Time | MODEL STATUS | Note |
|---|---|---|---|---|
| camcge | 2 | 0.6s | (compile error $141) | ⚠ expected pre-fix |
| cesam2 | 2 | 0.6s | (compile error $141) | ⚠ expected pre-fix |
| fawley | 2 | 0.6s | (compile error $171) | ⚠ expected pre-fix |
| otpop  | 2 | 0.5s | (compile error $141) | ⚠ expected pre-fix |

**Overall:** ✅ PASS (Tier 0/1 all green; 0 Pattern C regressions detected).
```

---

## Draft Workflow YAML

**File:** `.github/workflows/pr19-emit-solve-validation.yml` (to be committed during Sprint 26 implementation)

```yaml
name: PR19 Pre-Merge Solve-Time Validation

on:
  pull_request:
    branches: [main]
    paths:
      - "src/emit/**/*.py"
      - "src/kkt/stationarity.py"
      - "src/kkt/complementarity.py"
      - "src/ad/derivative_rules.py"
      - "src/ad/constraint_jacobian.py"
      - "scripts/ci/parse_pr19_targets.py"
      - "scripts/ci/run_pr19_solves.py"
      - ".github/workflows/pr19-emit-solve-validation.yml"
      - ".github/path-solve-ci-targets.txt"

jobs:
  emit-solve-validation:
    name: PR19 emit solve validation
    runs-on: ubuntu-latest
    timeout-minutes: 12

    permissions:
      contents: read
      pull-requests: write

    steps:
      - name: Check skip-emit-solve-ci label
        id: check-label
        uses: actions/github-script@v7
        with:
          script: |
            const labels = context.payload.pull_request.labels.map(l => l.name);
            const skip = labels.includes('skip-emit-solve-ci');
            core.setOutput('skip', skip ? 'true' : 'false');
            if (skip) {
              core.notice('PR has `skip-emit-solve-ci` label — bypassing PR19 solve validation.');
            }

      - name: Post bypass notice to PR
        if: steps.check-label.outputs.skip == 'true'
        uses: actions/github-script@v7
        with:
          # Build the body via an array + `.join('\n')` (NOT a template literal)
          # so YAML-block indentation never bleeds into the rendered Markdown.
          # Markdown treats lines that start with 4+ spaces as code blocks, which
          # would render the table / headers as a literal code block if a
          # multi-line template literal were used inside the indented `script:` block.
          script: |
            const body = [
              '## 🧪 PR19 Pre-Merge Solve Validation — BYPASSED',
              '',
              'PR has the `skip-emit-solve-ci` label — solve validation bypassed.',
              '',
              '**Reviewer responsibility:** verify that byte-diff regression tests cover the change before merge. If the PR turns out to alter emit shape, remove the label and re-run.',
            ].join('\n');
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: body,
            });

      - name: Skip remaining steps when label present
        if: steps.check-label.outputs.skip == 'true'
        run: |
          echo "PR labeled skip-emit-solve-ci; PR19 solve validation bypassed."
          exit 0

      - uses: actions/checkout@v4
        if: steps.check-label.outputs.skip != 'true'

      - name: Set up Python 3.12
        if: steps.check-label.outputs.skip != 'true'
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Install GAMS demo
        if: steps.check-label.outputs.skip != 'true'
        env:
          # Pin installer URL + expected SHA256. Sprint 26 implementation must
          # capture the actual SHA256 for the pinned 53.1.0 installer (e.g.,
          # `sha256sum linux_x64_64_sfx.exe` after the first manual download)
          # and store it here. Bumping GAMS version requires updating BOTH the
          # URL and the checksum — the workflow refuses to execute an installer
          # whose hash doesn't match, mitigating supply-chain risk if the
          # CloudFront endpoint is compromised or the file is replaced upstream.
          GAMS_INSTALLER_URL: "https://d37drm4t2jghv5.cloudfront.net/distributions/53.1.0/linux/linux_x64_64_sfx.exe"
          GAMS_INSTALLER_SHA256: "<TO BE FILLED IN BY SPRINT 26 IMPLEMENTATION>"
        run: |
          # Download + verify GAMS demo edition. Refuses to run the installer
          # if the SHA256 doesn't match the pinned value. Silent-install flags
          # (-q -d) are per gams.com/download docs (Sprint 26 implementation
          # must verify the current installer name + flags).
          curl -fSL -o /tmp/gams-installer.exe "$GAMS_INSTALLER_URL"
          echo "$GAMS_INSTALLER_SHA256  /tmp/gams-installer.exe" | sha256sum -c -
          chmod +x /tmp/gams-installer.exe
          mkdir -p $HOME/gams
          /tmp/gams-installer.exe -q -d $HOME/gams
          echo "$HOME/gams/gams53.1_linux_x64_64_sfx" >> $GITHUB_PATH
          gams --version

      - name: Read target list
        if: steps.check-label.outputs.skip != 'true'
        id: targets
        run: |
          # Parse .github/path-solve-ci-targets.txt into two lists:
          # - tier_0_1 (hard-fail): tier=0 and tier=1 entries
          # - pattern_c (soft-fail): tier=pattern-c entries
          # Format per design doc: "<model>   # tier=<0|1|pattern-c> [reslim=<N>]"
          python3 scripts/ci/parse_pr19_targets.py \
            .github/path-solve-ci-targets.txt \
            > /tmp/pr19-targets.json
          cat /tmp/pr19-targets.json

      - name: Run PATH solves (Tier 0/1 — hard-fail)
        if: steps.check-label.outputs.skip != 'true'
        id: solve-canaries
        run: |
          # Iterate the tier_0_1 list, run gams reslim=30, capture exit code +
          # MODEL STATUS + SOLVER STATUS, accumulate into /tmp/pr19-results.json.
          # Hard-fail (exit 1) if any model has rc != 0 or MODEL STATUS != 1.
          python3 scripts/ci/run_pr19_solves.py \
            --targets /tmp/pr19-targets.json \
            --tier hard-fail \
            --output /tmp/pr19-results-tier01.json \
            --reslim 30 \
            --scratch-base /tmp/pr19-scratch
          # Exit code propagates from the script.

      - name: Run PATH solves (Pattern C — soft-fail / informational)
        if: steps.check-label.outputs.skip != 'true' && always()
        id: solve-pattern-c
        run: |
          # Iterate the pattern_c list. Always exit 0 — record results only.
          python3 scripts/ci/run_pr19_solves.py \
            --targets /tmp/pr19-targets.json \
            --tier soft-fail \
            --output /tmp/pr19-results-patternc.json \
            --reslim 30 \
            --scratch-base /tmp/pr19-scratch \
            --soft-fail

      - name: Post PR comment with per-model status
        if: steps.check-label.outputs.skip != 'true' && always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const tier01 = JSON.parse(fs.readFileSync('/tmp/pr19-results-tier01.json', 'utf8'));
            const patternC = JSON.parse(fs.readFileSync('/tmp/pr19-results-patternc.json', 'utf8'));

            const renderRow = (m) => `| ${m.model} | ${m.rc} | ${m.wall_time}s | ${m.model_status} ${m.passed ? '✅' : '❌'} |`;
            const tier01Rows = tier01.results.map(renderRow).join('\n');
            const patternCRows = patternC.results.map(m =>
              `| ${m.model} | ${m.rc} | ${m.wall_time}s | ${m.model_status} | ${m.passed ? '✅' : '⚠ expected pre-fix'} |`
            ).join('\n');

            const tier01Pass = tier01.results.filter(m => m.passed).length;
            const patternCPass = patternC.results.filter(m => m.passed).length;

            const overall = tier01Pass === tier01.results.length
              ? '✅ PASS (Tier 0/1 all green)'
              : '❌ FAIL (Tier 0/1 regression)';

            // Build the body line-by-line so we don't depend on template-literal
            // indentation. Markdown treats lines that start with 4+ spaces as
            // code blocks — a multi-line template literal embedded in a
            // YAML-indented `script:` block would silently fold the table /
            // headers into a literal code block.
            const body = [
              '## 🧪 PR19 Pre-Merge Solve Validation Results',
              '',
              '**Trigger:** files changed under `src/emit/`, `src/kkt/stationarity.py`, ...',
              '',
              `### Tier 0/1 canaries (hard-fail surface) — ${tier01Pass}/${tier01.results.length}`,
              '',
              '| Model | rc | Time | MODEL STATUS |',
              '|---|---|---|---|',
              tier01Rows,
              '',
              `### Pattern C target models (soft-fail / informational) — ${patternCPass}/${patternC.results.length}`,
              '',
              '| Model | rc | Time | MODEL STATUS | Note |',
              '|---|---|---|---|---|',
              patternCRows,
              '',
              `**Overall:** ${overall}`,
            ].join('\n');

            // Find existing comment (per gamslib-regression.yml pattern)
            const { data: comments } = await github.rest.issues.listComments({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
            });
            const botComment = comments.find(c =>
              c.user.type === 'Bot' && c.body.includes('PR19 Pre-Merge Solve Validation Results')
            );
            if (botComment) {
              await github.rest.issues.updateComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                comment_id: botComment.id,
                body: body
              });
            } else {
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.issue.number,
                body: body
              });
            }

      - name: Upload solve artifacts
        if: steps.check-label.outputs.skip != 'true' && always()
        uses: actions/upload-artifact@v4
        with:
          name: pr19-solve-results
          path: |
            /tmp/pr19-results-tier01.json
            /tmp/pr19-results-patternc.json
            /tmp/pr19-scratch/*/*.lst
          retention-days: 30
```

### Helper scripts referenced

Two helper scripts (to be implemented during Sprint 26 execution, not part of this design task):

- **`scripts/ci/parse_pr19_targets.py`** — parses `.github/path-solve-ci-targets.txt` into JSON (`{tier_0_1: [...], pattern_c: [...]}`). ~30 LOC.
- **`scripts/ci/run_pr19_solves.py`** — iterates a target list, invokes `gams ... reslim=30` with `cwd=$REPO_ROOT` + `ScrDir=<tmpdir>` (mirroring `scripts/gamslib/test_solve.py::solve_mcp` per Sprint 25 #1345/#1346/#1347 — required so any future presolve-variant MCP's repo-relative `$include` resolves), captures exit code + MODEL STATUS + SOLVER STATUS from `.lst`, writes JSON results. Hard-fail exit when `--soft-fail` flag is absent. ~80 LOC.

These scripts are local-runnable for developer testing (no CI dependency).

---

## Existing CI Survey

Existing workflows (none of which install GAMS):

| File | Triggers | Purpose | Runtime |
|---|---|---|---|
| `ci.yml` | push main / PR | Fast + full pytest with coverage | ~3-4min |
| `lint.yml` | push main / PR | ruff + mypy + black | ~30s each (parallel) |
| `performance-check.yml` | PR | Fast-suite timing budget (45s limit) | ~1min |
| `gamslib-regression.yml` | PR (path-filtered) + weekly cron | GAMSLib parse-rate regression | ~5-10min |
| `nightly.yml` | nightly cron | Full corpus determinism | ~30min |
| `publish-pypi.yml` | release tag | PyPI publish | n/a |

PR19 fits naturally alongside `gamslib-regression.yml` (PR + path-filtered + matrix-style design). Recent `ci.yml` PR runs averaged 155-175s; PR19 adds ~3-8min to PR latency for emit-affecting PRs only.

---

## Test Plan (for Sprint 26 implementation)

Once the workflow file lands during Sprint 26:

1. **Smoke test**: open a no-op PR touching `src/emit/__init__.py` (whitespace change). Verify the workflow fires, runs all 11 canaries to MODEL STATUS 1, and posts a PR comment.
2. **Skip-label test**: add `skip-emit-solve-ci` label to the same PR. Verify the workflow short-circuits with the bypass message.
3. **Hard-fail injection test**: open a PR that introduces a known regression in `src/emit/expr_to_gams.py` (e.g., add `+ 1` to a numeric emit). Verify the workflow fails and the PR comment shows the failing canary.
4. **Pattern C soft-fail test**: open a PR that doesn't change Pattern C semantics. Verify the 4 Pattern C target models show in the soft-fail table with `⚠ expected pre-fix` status, and the workflow exits 0.

---

## Open Questions for Sprint 26 Implementation

These don't block the design but are worth flagging for the implementer:

1. **GAMS demo installer URL stability + checksum capture**: the URL pattern in the draft YAML (`d37drm4t2jghv5.cloudfront.net/.../linux_x64_64_sfx.exe`) was current at design time. If the URL changes between now and Sprint 26 execution, the implementer must verify against `gams.com/download` docs. **The `GAMS_INSTALLER_SHA256` env var in the workflow is a placeholder** (`<TO BE FILLED IN BY SPRINT 26 IMPLEMENTATION>`) — the implementer must run `sha256sum` against the pinned installer once and store the resulting hex digest. After that, any version bump requires re-capturing the checksum (the workflow's `sha256sum -c -` step refuses to execute an installer whose hash doesn't match, mitigating supply-chain risk if CloudFront is compromised or the file is replaced upstream).

2. **GAMS demo license activation**: some GAMS distributions require a license file even for demo. If the bare installer doesn't ship a default demo license, the workflow may need an additional step to install `gamslice.txt`. This is testable during the smoke-test step above.

3. **Caching the GAMS install across CI runs**: the install adds ~90s. Caching `$HOME/gams/` via `actions/cache` would eliminate this on cache hit. Implementer to verify whether the demo-license file would be valid across cache hits.

4. **Behavior on out-of-tree solver runtime errors**: if PATH itself crashes on a canary (rare but possible), the script should distinguish "PATH crash" from "MODEL STATUS regression" in the PR comment. Currently both would surface as "Tier 0/1 fail" — fine for v1, refinable later.

---

## Acceptance Criteria (per PREP_PLAN.md §Task 8)

- [x] Trigger file patterns documented (§Trigger Conditions)
- [x] Target model list designed / specified (≥ Pattern C 4 + ≥ 3 Tier 0 canaries — design specifies 11 + 4 for `.github/path-solve-ci-targets.txt`; the file itself is committed during Sprint 26 implementation alongside the workflow YAML, per the design-only scope of this PR)
- [x] PATH timeout policy documented (default 30s, configurable via target-list annotation)
- [x] Failure handling policy documented (hard-fail Tier 0/1; soft-fail Pattern C)
- [x] CI overhead estimate documented (~3-8min for emit-affecting PRs; within PR latency budget)

---

## Related Documents

- `docs/planning/EPIC_4/SPRINT_25/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently" #3 (PR19 origin)
- `docs/planning/EPIC_4/SPRINT_25/SPRINT_LOG.md` Day 0 (Tier 0/1 canary list)
- `docs/planning/EPIC_4/SPRINT_25/DESIGN_ALIAS_AD_ROLLOUT.md` §6.3 (CI does not install GAMS — constraint flagged)
- `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` §Task 8 (this task)
- `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` §Unknowns 6.1, 6.2 (verified by this task)

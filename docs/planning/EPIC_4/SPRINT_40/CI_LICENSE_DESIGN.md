# Sprint 40 CI License-Isolation Design (Prep Task 4)

**Measured at:** `c8f769c4` (`main`) · **Date:** 2026-10-13/14 · **Inputs:** `LICENSE_PROBE.md` (Task 3)

**Bottom line.** The `main`-only environment policy works exactly as designed — verified in a throwaway repository, with the attack case (a branch carrying its own copy of the workflow) refused on `push`, `pull_request` and `workflow_dispatch`. **But the license itself cannot reach CI safely today:** it is evaluation-grade and node-locked in shape (Task 3), so a GitHub-hosted runner is very unlikely to validate it; and the self-hosted fallback cannot be made "never eligible for PR-controlled code" on a **personal-account** repository. **Recommendation for Sprint 40: the licensed tier stays local-only** (the owner's machine), audited by Task 5's per-row `license_edition`; `licensed-solve.yml` below is the design to adopt **if** GAMS provides a CI-usable license (or the repo moves to an organization).

---

## 1. Workflow inventory (from the files, parsed as YAML)

Two different questions, kept apart: does a workflow **trigger automatically on a PR**, and **can it run code from a non-default branch at all**? The second is wider. A `workflow_dispatch` runs **whatever ref the dispatcher selects**, including an unmerged same-repository branch, and every workflow here uses an unqualified `actions/checkout` (no `ref:` override), which checks out that selected ref. A `schedule` run always uses the default branch.

| workflow | triggers, with **every** branch / path / type filter (verbatim from the YAML) | in-job filtering | GAMS | secrets | auto PR trigger | can run non-default-branch code |
|---|---|---|---|---|---|---|
| `ci.yml` | `push` (branches: main) · `pull_request` (branches: main) | — | no | — | yes | yes — PR head |
| `gamslib-regression.yml` | `pull_request` (paths: `src/gams/grammar.lark`, `src/gams/parser.py`, `src/ir/parser.py`, `src/ir/symbols.py`, `src/ir/ast.py`, `scripts/ingest_gamslib.py`, `scripts/check_parse_rate_regression.py`, `.github/workflows/gamslib-regression.yml`) · `schedule` · `workflow_dispatch` | — | no | — | yes (path-filtered) | yes — PR head; any dispatched ref |
| `golden-staleness.yml` | `pull_request` (branches: main) | decides internally which goldens are in scope | no | — | yes | yes — PR head |
| `lint.yml` | `push` (branches: main) · `pull_request` (branches: main) | — | no | — | yes | yes — PR head |
| `nightly.yml` | `schedule` · `workflow_dispatch` | — | no | — | no | **yes — any dispatched ref** (schedule runs `main`) |
| `performance-check.yml` | `pull_request` (no filters) | — | no | — | yes | yes — PR head |
| `phase0-gate.yml` | `pull_request` (branches: main) | decides internally whether the PR needs a Phase-0 doc | no | — | yes | yes — PR head (runs the PR's own `check_phase0_doc.py`) |
| **`pr19-emit-solve-validation.yml`** | **`pull_request`** (branches: main; paths: `src/emit/**/*.py`, `src/kkt/stationarity.py`, `src/kkt/complementarity.py`, `src/ad/derivative_rules.py`, `src/ad/constraint_jacobian.py`, `scripts/ci/parse_pr19_targets.py`, `scripts/ci/run_pr19_solves.py`, `.github/workflows/pr19-emit-solve-validation.yml`, `.github/path-solve-ci-targets.txt`) | `skip-emit-solve-ci` label bypass | **yes** (54.2.1 demo) | — | yes (path-filtered) | yes — PR head |
| **`presolve-divergence.yml`** | **`pull_request`** (branches: main; paths: `src/emit/emit_gams.py`, `src/emit/original_symbols.py`, `scripts/diagnostics/check_presolve_divergence.py`, `scripts/diagnostics/presolve_divergence_allowlist.txt`, `.github/workflows/presolve-divergence.yml`) | `skip-presolve-divergence` label bypass — every step after the label check, checkout and GAMS install included, is guarded by `steps.skip.outputs.skip != 'true'`, so a labelled PR runs no GAMS at all | **yes** (54.2.1 demo) | — | yes (path-filtered) | yes — PR head |
| `publish-pypi.yml` | `release` (types: published) · `workflow_dispatch` | — | no | **`PYPI_API_TOKEN`, `TEST_PYPI_API_TOKEN`** (repository secrets, no environment) | no | **yes, two ways, both in the job that receives the publishing secrets:** any **dispatched** ref; and on `release: published`, the **release tag's commit** — which need not be on `main` |

**Two install GAMS, eight do not** — re-derived, matching Task 2's count. **Both GAMS-installing workflows trigger only on `pull_request` (to `main`, path-filtered) and run PR-controlled code** — so neither may ever hold the license. **`pull_request_target` appears nowhere in `.github/`.** *(An earlier regex-based pass mis-read `golden-staleness.yml` as also triggering on `push` and missed `publish-pypi.yml`'s `release`; the YAML parse above is authoritative.)*

**Pre-existing exposure, found while inventorying — not GAMS-related:** `publish-pypi.yml` keeps the PyPI tokens as **repository** secrets and checks out its triggering ref unqualified. Two paths reach those secrets with code that may not be on `main`: a `workflow_dispatch` on any branch, and a `release: published` whose tag points at a commit off `main`. **What does and does not close it:**

- **A protected environment is required in every variant.** Put the publish job behind an environment, and keep the credentials there: the tokens as **environment** secrets, or — for PyPI trusted publishing — the trusted publisher configured **with that environment name**. Trusted publishing alone does **not** close it: PyPI matches the publisher by repository, workflow file and (optionally) environment, not by ref, so without a required environment a branch copy of the workflow would still be accepted.
- **"Admit release tags" is not enough on its own:** a tag-pattern policy proves the ref is a tag, not that the tag points at a reviewed commit on `main`. Either **verify the commit is on `main`**, or add **governance that excludes untrusted tag commits** — required reviewers on the environment, plus tag protection (a ruleset) so only maintainers can create release tags. The verification has three parts, and each is needed:
  - **The environment must admit the release tag pattern** (e.g. `v*`), not `main` only. On a `release` event the ref the environment checks is the **tag**, so a `main`-only policy would refuse every release run. A dispatch should be refused outright, or admitted from `main` only.
  - **The checkout has to fetch `main`.** `actions/checkout` fetches one commit by default (`fetch-depth: 1`), so `origin/main` isn't there to compare against. Use `fetch-depth: 0`, or run `git fetch --no-tags origin main` before the check.
  - **Fail closed on the ancestry check, immediately after checkout and fetch, before any tagged code runs:** `git merge-base --is-ancestor "$GITHUB_SHA" origin/main || { echo "::error::release commit is not on main"; exit 1; }`. A missing `origin/main` also exits non-zero, so a fetch failure blocks publishing rather than passing it. Running the check only "before the step that receives credentials" is **too late** for today's workflow. Its single `build-and-publish` job grants `id-token: write` at **job** scope and runs the tagged code (dependency install, tests, linters, build) before publishing. That code could request an OIDC token itself, or leave a process running to watch a later step's credentials.
  - **Split the job (safer, and recommended):** a **secretless build job** (no environment, no `id-token`, `contents: read`) checks out, verifies ancestry, tests and builds, then uploads `dist/` as an artifact. A separate **publish job** (`needs: build`, the protected environment, `id-token: write` only here) downloads the artifact and publishes it **without checking out or running any repository code**. Tagged code then never shares a job with the credentials.

Recorded for the owner (§7); out of this task's scope to change.

## 2. Demo-motivated exclusions

- **No target list or tier excludes a model by size.** `.github/path-solve-ci-targets.txt` (30 entries) and the PR19 tier definitions carry no demo, license or row-count rule; `presolve-divergence.yml` scans the **40** presolve goldens, none of them gated.
- **Instead, the demo limit is *masked*:** six MCP-gated cohort members sit in PR19's **Pattern-C soft-fail** tier — **`egypt`, `ferts`, `shale`, `sroute`, `srpchase`, `tfordy`** (sized 1,531–5,702 rows by Task 2). On the demo they can **never** pass: GAMS refuses them, `run_pr19_solves.py` sees a non-zero exit with no `MODEL STATUS`, and records an ordinary failure — informational only, because the tier is soft. **A license refusal is indistinguishable from a real emit failure in PR19's output today.** → PR-side change in §6; licensed coverage in §3.

## 3. `licensed-solve.yml` — design (adopt only once a CI-usable license exists; see §5)

```yaml
name: licensed-solve
on:
  push:            { branches: [main] }
  schedule:        [{ cron: "0 6 * * *" }]
  workflow_dispatch:
permissions: { contents: read }
jobs:
  licensed:
    runs-on: ubuntu-latest            # GitHub-hosted: a fresh VM per job
    environment: gams-licensed        # main-only deployment-branch policy (§4)
    steps:
      - uses: actions/checkout@v4     # the triggering ref: main (push/dispatch) or the default branch
                                      # (schedule); a dispatch from any other ref is refused by the
                                      # environment before the job starts (verified in §4)
      - name: Install GAMS            # same pinned installer + SHA-256 guard as today
        run: |
          …                                         # download, verify SHA-256, install
          echo "$GAMS_DIR" >> "$GITHUB_PATH"
          echo "GAMS_DIR=$GAMS_DIR" >> "$GITHUB_ENV"  # persist: a shell variable does NOT survive
                                                      # into later steps -- without this, the license
                                                      # and cleanup steps would target /gamslice.txt
      - name: Install license (masked, never echoed)
        env: { GAMS_LICENSE: "${{ secrets.GAMS_LICENSE }}" }
        run: |
          while IFS= read -r l; do [ -n "$l" ] && echo "::add-mask::$l"; done <<< "$GAMS_LICENSE"
          umask 077; printf '%s\n' "$GAMS_LICENSE" > "$GAMS_DIR/gamslice.txt"
          grep -v '^[[:space:]]*$' "$GAMS_DIR/gamslice.txt" > "$RUNNER_TEMP/lic-patterns.txt"
                                      # the ONE pattern file, at a FIXED path -- a second secret copy,
                                      # so the cleanup step removes it too
      - name: Edition check (classification only -- never raw audit or header output)
        run: …   # tiny probe, ALL output to $RUNNER_TEMP/out/ (stdout+stderr redirected, lo=2 log to
                 # file, o= listing there); scan_local (below) BEFORE printing anything; then print only
                 # "edition=licensed|demo" via Task 3's regex; fail unless licensed
      - name: Licensed solves
        run: …   # coverage below; same rule: every GAMS/pipeline command writes to $RUNNER_TEMP/out/,
                 # nothing streams to the Actions log; scan_local gates any summary line that is printed
      - name: Scan before upload (gate)
        if: always()                    # run on failure too -- that is when output most needs checking
        run: …   # scan_local over everything under $RUNNER_TEMP/out/ that an upload step would ship;
                 # FAIL on a match, and the upload step runs only if this one succeeded; tolerate an
                 # absent license/pattern file (install may have failed) by reporting "nothing to scan";
                 # positive control: scan_local on $GAMS_DIR/gamslice.txt must
                 # return rc 0 (hit) -- quiet, so the license lines themselves are never printed
      # scan_local PATH... = QUIET fixed-string match, so nothing it matches is ever printed:
      #   grep -rqF -f "$RUNNER_TEMP/lic-patterns.txt" -- "$@" >/dev/null 2>&1; rc=$?
      #   rc 0 = MATCH -> fail the gate (and print only "license text found", never the line or file
      #   content); rc 1 = clean -> pass; rc >= 2 = scan error -> FAIL CLOSED.
      # This matters most for the positive control: run against gamslice.txt it matches every line,
      # and a plain `grep -F -f` would print the raw license lines to the Actions log, leaving
      # masking as the only protection. Only the verdict ("hit" / "no hit") is printed.
      # It catches VERBATIM secret lines only -- not transformed header text (e.g. the licensee
      # or node fields GAMS reformats into a .lst/.log header); those are kept out by capture-and-
      # classify ordering, not by this scan (Task 3's own scan is likewise LIMITED). It cannot scan
      # the Actions log itself: job logs stream off the runner as they are written and are not
      # downloadable until the job ends, so a later step never sees them. The log is protected by
      # never writing raw output to it, not by scanning it after the fact.
      - name: Remove the license (always)
        if: always()
        run: |
          rm -f "$RUNNER_TEMP/lic-patterns.txt"   # first, and independent of GAMS_DIR
          [ -n "${GAMS_DIR:-}" ] || { echo "::warning::GAMS_DIR unset -- install failed before persisting it"; exit 0; }
          rm -f "$GAMS_DIR/gamslice.txt"
          # every copy listed: the license file and the pattern file. Neither may outlive the job --
          # on a self-hosted runner (§5) a survivor would be readable by the next job.
```

- **Coverage:** both gated populations (`BASELINE_RECONFIRMATION.md` §3 — the 11 MCP-gated models and the 9 in-scope NLP-gated ones) and PR19's six gated soft-fail targets (§2).
- **Never `pull_request_target` with a PR-head checkout** — it runs with the base repository's secrets while executing the PR's code, the standard exfiltration pattern. This workflow has no PR trigger at all.
- **Secrets:** `GAMS_LICENSE` stored **in the `gams-licensed` environment only**, never as a repository secret (a repository secret is available to every workflow, including PR-triggered ones).
- **Logs and artifacts:** no raw `gams audit`, `.lst` or `.log` license header in any job log or uploaded artifact — a CI log is a published artifact. **Ordering is the control:** every command's output goes to local files first, and only the classification (`edition=…`) and summaries derived from it reach the log — raw listings and logs are never printed. A post-hoc "scan the logs" step is not possible, since the log has already left the runner. The two scanning layers are narrower than that: masking (`::add-mask::`) and `scan_local` both catch **verbatim** secret lines only. Neither catches transformed header text (the licensee or node fields as GAMS reformats them); **capture-and-classify ordering is what keeps those out**, not the scan.

## 4. Branch-policy verification — throwaway repository

**Setup:** throwaway public repository `jeffreyhorn/nlp2mcp-envpolicy-probe-20261013` (public: on the free plan, environment branch policies are enforced only for public repositories); environment `gams-licensed` with a custom deployment-branch policy admitting **`main` only**; environment secret `DUMMY_LICENSE` holding a 25-character dummy (never the real license). Probe workflow on `workflow_dispatch`, `push` (all branches) and `pull_request`, with `environment: gams-licensed`, printing only whether the secret is reachable and its length.

**Attack case:** a branch `attacker` carrying **its own copy** of the workflow — the shape of a contributor branch that modifies `licensed-solve.yml`.

| event | ref | result |
|---|---|---|
| `push` | `main` | job ran — `SECRET_REACHABLE len=25` (**positive control**) |
| `workflow_dispatch` | `main` | job ran — `SECRET_REACHABLE len=25` (twice) |
| `push` | `attacker` | **refused** — *Branch "attacker" is not allowed to deploy to gams-licensed due to environment protection rules.* |
| `pull_request` (same-repo PR from `attacker`) | `refs/pull/1/merge` | **refused** — *Branch "refs/pull/1/merge" is not allowed to deploy …* |
| `workflow_dispatch` | `attacker` | **refused** — *Branch "attacker" is not allowed to deploy …* (twice) |

**Finding:** the `main`-only environment refuses every non-`main` ref before the job starts, and admits `main`. *(A measurement slip, recorded: the first reading reported the `main` runs as `SECRET_EMPTY` because the extraction matched the run log's echo of the script text, which contains that literal. Re-read from the actual output lines, every `main` run reached the secret. The positive control did its job — it is why the slip was caught rather than reported.)*

**Clean-up:** the dummy secret and the environment were deleted, the probe PR closed, and the repository **archived**. **It is not yet deleted:** the `gh` token lacks the `delete_repo` scope (`HTTP 403 … needs the "delete_repo" scope`) — an owner action (§7).

## 5. Hosted vs self-hosted runners

- **GitHub-hosted (preferred, if the license allows):** each job gets a fresh VM, discarded afterwards — the right isolation. **But Task 3 found the license node-locked in shape** (its run-time header carries node, memory and core-count fields; evaluation edition, expires 2027-09-21), so it will very likely **not validate** on a runner. This was **not** tested — installing the real license in any CI before the owner's decision would itself be the exposure this design prevents. → **Owner question for GAMS** (§7).
- **Self-hosted on the licensed machine — not acceptable as the repository stands.** Two independent reasons:
  1. **A runner cannot be restricted to one workflow on a personal-account repository.** Restricting a self-hosted runner to *selected workflows* is a **runner-group** setting, which GitHub offers to **organizations** (and enterprises); `jeffreyhorn/nlp2mcp` is owned by a **user**. So any workflow on any branch — a same-repo PR branch, or a fork PR once approved — can target the runner's labels and execute PR-controlled code on it. *(Per GitHub's runner-group documentation; GitHub also advises against self-hosted runners on public repositories.)*
  2. **The environment does not protect a license that lives on the machine.** On the licensed node the license is a file in the user's home directory; a job running there can read it directly, whatever the environment's branch policy. The policy guards the *secret*, not the disk.
- **Recommendation for Sprint 40: the licensed tier stays local-only** — run on the owner's machine, through the throwaway-worktree + retention-patch procedure, with Task 5's per-row `license_edition` making every licensed row auditable after the fact. **Revisit when either changes:** GAMS provides a license usable on hosted runners (→ adopt §3 as designed), or the repository moves to an organization (→ a dedicated, ephemeral self-hosted runner in a runner group whose *selected workflows* entry is pinned to the trusted ref, `<org>/nlp2mcp/.github/workflows/licensed-solve.yml@refs/heads/main`, with the always-run cleanup). **The `@refs/heads/main` pin is required, not optional:** a branch copy of the workflow has the same `.github/workflows/licensed-solve.yml` path (the §4 attack case), so a path-only entry would admit it to the licensed runner.

## 6. PR-side change (both GAMS-installing workflows)

- **Rename** the step from *"Install GAMS demo"* to *"Install GAMS (demo edition)"* and keep the pinned installer and its SHA-256 guard.
- **Replace the raw `gams audit lo=2` print** with an **edition classification only** (`edition=demo` / `edition=licensed`, from Task 3's regex on a tiny probe listing). Raw audit output can carry the licensee, license ID, license path and node fields; a CI log is published.
- **Skip with a notice, not a failure, when the demo refuses a model** *(to implement in P1 — `run_pr19_solves.py` has no refusal detection today and records these runs as ordinary failures)*: detect the refusal line (`**** The model exceeds the demo license limits …`) in `run_pr19_solves.py` and report the model as *skipped — over the demo ceiling* (a `::notice::`), so PR19's six gated targets stop masquerading as emit failures. Their licensed coverage moves to the licensed tier (local-only for now).
- **No secrets** in either workflow — already true; keep it so.

### The detection trade-off, stated

Keeping the license out of PR jobs means **no PR can be checked against a model over the demo ceiling**. With `licensed-solve.yml` (§3), a PR that breaks a large model is caught **after merge**, on the next push to `main`, the nightly schedule, or a dispatch. With the **local-only** recommendation (§5) it is later still: **only when the owner next runs the licensed tier**. The mitigations are: PR19 keeps hard-failing on its demo-sized Tier 0/1 canaries; the PR-side *skipped — over the demo ceiling* notice (above) makes the gap visible on every PR instead of hiding it as a soft failure; and Task 12 should schedule a licensed re-run of both gated populations at each sprint checkpoint, so a large-model regression is at most one checkpoint old.

## 7. Owner checklist (for Task 6, decision 3)

1. **License terms (GAMS):** may this evaluation license be used on GitHub-hosted ephemeral runners, or is it bound to this machine? If bound, can GAMS provide a CI-usable license?
2. **Runner model:** accept **local-only** licensed runs for Sprint 40 (recommended), or move the repository to an organization to enable a self-hosted runner group restricted to `licensed-solve.yml@refs/heads/main` (pinned to the ref, not just the path; §5).
3. **Environment (only if a CI-usable license arrives):** create `gams-licensed` with a **`main`-only** deployment-branch policy; decide whether it **requires reviewers**.
4. **Secret placement:** store `GAMS_LICENSE` **in the environment only** — never as a repository secret.
5. **System-directory demo file:** replace it with the full license (Task 3's recommendation), so a different user or `HOME` cannot silently fall back to the demo.
6. **PyPI publishing (pre-existing, not GAMS):** put the publish job behind a **protected environment in every variant** — tokens as environment secrets, or a trusted publisher configured **with that environment** (trusted publishing without it still accepts a branch copy of the workflow). Then either publish **from `main`**, with the ancestry check immediately after checkout and before any tagged code runs, or add reviewer + tag-protection governance so an untrusted tag commit cannot publish. In either case, split build (secretless) from publish (environment + `id-token: write`, runs no repository code). Today one job holds `id-token: write` while it runs the tagged code's tests (§1). Today both a dispatch on any branch and a release from an off-`main` tag run unreviewed code with the tokens (§1).
7. **Delete the throwaway repository:** `gh auth refresh -h github.com -s delete_repo && gh repo delete jeffreyhorn/nlp2mcp-envpolicy-probe-20261013 --yes` (it is archived and holds no secret or environment).

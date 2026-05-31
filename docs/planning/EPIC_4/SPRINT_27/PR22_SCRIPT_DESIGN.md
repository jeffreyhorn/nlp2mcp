# Sprint 27 Prep Task 9: PR22 Mid-Sprint Audit Script — Design + Validation

**Status:** ✅ COMPLETE
**Date:** 2026-05-30
**Owner:** Prep Task 9
**Codifies:** Sprint 26 retrospective recommendation **PR22**
**Resolves:** KNOWN_UNKNOWNS §Unknown 9.3 (cross-sprint timestamp-ambiguity handling)

---

## 1. Purpose

Automate generation of the **PR14 review list** (per-PR scope) and the **mid-sprint retest comparison surface** (sprint-scope) directly from `git log`, replacing the Sprint 26 practice of hand-curating these lists in a frozen `PLAN_PROMPTS.md` document.

The Sprint 26 Day 12 PLAN_PROMPTS.md staleness incident exposed the failure mode: late-sprint emit changes (Day 13 #1398 regeneration sweep across 15 models, and Day 1 launch Phase A landing) were not reflected in the frozen Day 0 prompts, so mid-sprint retests and PR14 reviews could miss them. Scanning `git log` at invocation time eliminates the prompt-staleness vector.

---

## 2. Design Decisions

### 2.1 CLI — two mutually exclusive flags

| Flag | Backed by | Semantics |
|---|---|---|
| `--since-date <DATE>` | `git log --since <DATE>` | Date-based; accepts ISO-8601 (`"2026-04-22"`) or relative (`"2 days ago"`). Subject to same-day commit-boundary ambiguity. |
| `--since-commit <SHA>` | `git log <SHA>..HEAD` | Commit-based; SHA validated via `git rev-parse --verify`. Recommended for mid-sprint retests because commit boundaries are unambiguous. |

**Why two flags, not one overloaded `--since`?** `git log --since` is date-only — it doesn't accept SHAs. A single `--since` accepting both forms would have to internally dispatch on "looks like a SHA?" heuristics, which is fragile. Two distinct flags surface the date-vs-commit choice in the CLI signature itself.

**Resolution of KU 9.3 (cross-sprint timestamp ambiguity):** `--since-commit` is the structural mitigation. The recommended Sprint 27 mid-sprint workflow is to record the Sprint Day 0 commit SHA in `PLAN.md` Day 0 (Task 11) and pass it to `--since-commit`, eliminating timestamp-boundary ambiguity entirely.

### 2.2 Output modes

| `--format` | Use case |
|---|---|
| `text` (default) | Quick human inspection in the terminal. |
| `markdown` | Drop into a retest report or PR comment. |
| `json` | Downstream tooling (e.g., feeding the retest list into `run_full_test.py --model`). |

### 2.3 Report-header mode

| `--mode` | Header label |
|---|---|
| `retest` (default) | `# Mid-sprint retest surface` |
| `pr14` | `# PR14 review list` |

`--mode` is purely a label hint; the diff-detection logic is the same in both modes (both scan the same path with the same suffix filter).

### 2.4 Pathspec — directory, not glob

The script passes `'data/gamslib/mcp/'` (directory pathspec) to `git log`, not `'data/gamslib/mcp/*_mcp.gms'` (glob pathspec). Two reasons:

1. **argv-list `subprocess.run` bypasses shell glob expansion** — `*` would be passed to git literally.
2. **Git's interpretation of unadorned `*` pathspecs is not reliable across versions / `core.literalPathspecs` settings.** The portable alternative is the explicit `:(glob)` pathspec-magic prefix, but the directory pathspec + Python-side suffix filter is simpler and equivalent.

The `_mcp.gms` / `_mcp_presolve.gms` suffix filter is applied in Python after parsing `git log` output (`scripts/sprint_audit/changed_emit_artifacts.py:153`).

### 2.5 git log format — SHA-only, separate subject pass

The custom `--pretty=format:COMMIT:%H` is intentionally **SHA-only**, not `COMMIT:%H%n%s`. Including the subject inline would emit a non-path line per commit that the parser would misclassify as a changed file path. Subjects are fetched in a second `git log --no-walk --pretty=format:'%H %s' <sha>...` pass keyed by SHA (`scripts/sprint_audit/changed_emit_artifacts.py:178`).

### 2.6 Commit SHA validation

`--since-commit <SHA>` is validated via `git rev-parse --verify <sha>^{commit}` before constructing the revision range. An invalid SHA produces a clear stderr message and exit code 2 — no obscure `git log` errors leak to the user (`scripts/sprint_audit/changed_emit_artifacts.py:96`).

---

## 3. Implementation Summary

**Path:** `scripts/sprint_audit/changed_emit_artifacts.py` (executable; ~340 lines)

| Component | Location | Purpose |
|---|---|---|
| `EMIT_DIR` / `EMIT_SUFFIXES` | `:70-71` | Constants: `"data/gamslib/mcp/"` and `("_mcp.gms", "_mcp_presolve.gms")`. |
| `CommitGroup` | `:74-80` | Frozen dataclass: `sha`, `subject`, `files: tuple[str, ...]`. |
| `_run_git` | `:83-93` | Thin `subprocess.run` wrapper; pinned `cwd=` to repo root via `Path(__file__).resolve().parents[2]`. |
| `validate_commit_sha` | `:96-112` | `git rev-parse --verify <sha>^{commit}`; on failure prints clear error and `SystemExit(2)`. |
| `collect_changed_artifacts` | `:115-175` | Main scan: builds argv per mode, parses `COMMIT:<sha>` + name-only output, filters by suffix, attaches subjects. |
| `_fetch_subjects` | `:178-190` | Separate `git log --no-walk` pass for subjects keyed by SHA. |
| `format_text` / `format_markdown` / `format_json` | `:193-262` | Three output formatters; all consume the same `list[CommitGroup]`. |
| `build_arg_parser` | `:265-318` | argparse with mutually exclusive `--since-date` / `--since-commit` group. |
| `main` | `:321-339` | Wires CLI args → collect → format → stdout. |

**Dependencies:** standard library only (`argparse`, `json`, `subprocess`, `sys`, `dataclasses`, `pathlib`).

---

## 4. Validation Results

Dry-run against Sprint 26 history. Sprint 26 Day 0 anchor SHA = `0d8446d23223cc9e77fa8c6c6d72665a1a134f16` (resolved via `git rev-list -1 --before="2026-04-23" main`).

### 4.1 Date-based dry-run

```bash
.venv/bin/python scripts/sprint_audit/changed_emit_artifacts.py \
    --since-date "2026-04-22"
```

Output summary: 19 commits, 209 emit changes, 103 unique paths.

### 4.2 Commit-based dry-run (recommended path)

```bash
.venv/bin/python scripts/sprint_audit/changed_emit_artifacts.py \
    --since-commit 0d8446d23223cc9e77fa8c6c6d72665a1a134f16
```

Output summary: **identical to the date-based run** for this range (19 commits, 209 changes, 103 unique paths). Both modes produce the same Sprint 26 surface — the difference matters only at the precise sprint boundary (within a single day).

### 4.3 Key commits surfaced (acceptance criteria)

| Commit | Date | Files matched | Sprint 26 milestone |
|---|---|---|---|
| `e0be4fb16e8b` | 2026-05-14 | 16 (15 #1398-affected `*_mcp.gms` + `launch_mcp_presolve.gms`) | Day 13 final retest + #1398 sweep |
| `8d4cc4acc59c` | 2026-05-11 | 1 (`launch_mcp.gms`) | Day 1 Phase A landing |
| `16966a21b4ef` | 2026-05-03 | (Sprint 25 #1351 launch rollback) | Sprint 25, surfaced because the date window starts before Sprint 26 |

**All 15 #1398-affected models present** in the Day 13 commit: `qdemo7`, `egypt`, `ferts`, `shale`, `sambal`, `qsambal`, `harker`, `tfordy`, `dinam`, `ganges`, `gangesx`, `fawley`, `srpchase`, `sroute`, `turkpow`. **Launch present** in both Day 1 (`launch_mcp.gms`) and Day 13 (`launch_mcp_presolve.gms`).

**#1400 (`scripts/gamslib/*` path-relativization) is intentionally absent** — it's not an emit artifact and falls outside `data/gamslib/mcp/`. This is by design, not a missing case.

### 4.4 Error handling

```bash
$ .venv/bin/python scripts/sprint_audit/changed_emit_artifacts.py --since-commit "deadbeefcafe1234"
error: --since-commit 'deadbeefcafe1234' is not a valid commit SHA in this repository (git rev-parse exit 128)
fatal: Needed a single revision
# exit=2
```

Invalid SHA produces a clear message + non-zero exit. Missing required flag (neither `--since-date` nor `--since-commit`) produces argparse's standard usage error.

---

## 5. CONTRIBUTING.md Integration

A new top-level section `## Emit-PR .gms Diff Workflow (PR22 audit script)` is added immediately after the existing `## Emit-Affecting PRs — Required .gms Artifact in Diff (PR14)` section. The new section:

1. Names the script and its location.
2. Documents the two invocation modes (`--since-date`, `--since-commit`) with examples.
3. Cross-references the PR14 rule (PR14 says "include a regenerated `.gms` artifact"; PR22 helps the PR author and reviewer enumerate which models are affected by the upstream `src/` changes).
4. Documents the mid-sprint retest workflow (Day 0 SHA → `--since-commit` → markdown output → paste into retest report).

---

## 6. Quality Gate

```bash
make typecheck && make format && make lint && make test
```

- `make typecheck`: PASS (no issues in 98 src files)
- `make format`: PASS (377 files left unchanged after black; ruff import sort clean)
- `make lint`: PASS (no issues in 98 src files; black --check clean)
- `make test`: PASS (full Python suite)

Additionally, since the Makefile gate covers `src/` + `tests/` only, the new script was checked directly:

```bash
.venv/bin/python -m black scripts/sprint_audit/changed_emit_artifacts.py
.venv/bin/python -m ruff check scripts/sprint_audit/changed_emit_artifacts.py
.venv/bin/python -m mypy scripts/sprint_audit/changed_emit_artifacts.py
```

All three clean.

---

## 7. Sprint 27 Day 0 Handoff

1. **Task 11 owner records the Sprint 27 Day 0 commit SHA** in `docs/planning/EPIC_4/SPRINT_27/PLAN.md` Day 0 entry. This SHA is the canonical `--since-commit` anchor for the rest of the sprint.
2. **Mid-sprint retest workflow:**
   ```bash
   SPRINT27_DAY0=$(grep -E '^- \*\*Day 0 anchor SHA:\*\* `[a-f0-9]+`' \
       docs/planning/EPIC_4/SPRINT_27/PLAN.md | awk -F'`' '{print $2}')
   .venv/bin/python scripts/sprint_audit/changed_emit_artifacts.py \
       --since-commit "$SPRINT27_DAY0" --format markdown --mode retest \
       > /tmp/sprint27_retest_surface.md
   ```
   Paste `/tmp/sprint27_retest_surface.md` into the relevant `SPRINT_LOG.md` retest entry.
3. **PR14 workflow** — for each emit-affecting PR, the author runs:
   ```bash
   .venv/bin/python scripts/sprint_audit/changed_emit_artifacts.py \
       --since-commit <PR-base-sha> --format markdown --mode pr14
   ```
   Pastes the output into the PR description to disclose all touched emit artifacts.

---

## 8. Related Documents

- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 9
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` §Unknown 9.3
- `docs/planning/EPIC_4/SPRINT_26/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently" §"PR22"
- `docs/planning/EPIC_4/SPRINT_26/SPRINT_LOG.md` Day 12 (PLAN_PROMPTS.md staleness incident)
- `CONTRIBUTING.md` §"Emit-Affecting PRs — Required `.gms` Artifact in Diff (PR14)" (companion rule)
- `CONTRIBUTING.md` §"Emit-PR `.gms` Diff Workflow (PR22 audit script)" (this script's invocation guide)

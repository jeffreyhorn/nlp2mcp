# Design: Byte-Stability Determinism Tests (PR12)

**Status:** ✅ DESIGN COMPLETE
**Date:** 2026-04-21
**Owner:** Prep Task 10
**Target implementation:** Sprint 25 Day 1–2
**Tracking issue:** #1283 (reference bug)

---

## 1. Purpose

Design the CI-enforced byte-stability regression-test infrastructure (PR12) — a test harness that runs the nlp2mcp pipeline under multiple `PYTHONHASHSEED` values and asserts byte-identical `.gms` output across seed runs. The harness catches `#1283`-class parser / emission non-determinism **in CI**, not via reviewer inspection of diffs.

Sprint 24 discovered #1283 only because a reviewer happened to see corrupt values on a Day-13 `chenery_mcp.gms` review. Without PR12, other `#1283`-class bugs will silently affect metrics and only surface when the produced output happens to be read by a human. PR12 flips the default from "human inspection catches it" to "CI catches it."

---

## 2. Scope Decision: **Option C (both per-commit Option A and nightly Option B)**

### Rationale

- **Option A alone** (5-model per-commit) gives high-confidence early warning on the known reproducer and a representative fixture cross-section. Fast enough to run per-commit (~60s wall-clock).
- **Option B alone** (full-pipeline nightly) catches silent corruption in the long tail — e.g., `indus89` or other multi-row-label tables where the bug is currently masked downstream — but its ~4h30m wall-clock rules out per-commit CI.
- **Option C** gets the best of both: fast per-commit gate + nightly broad-scope guard.

Task 3 (`INVESTIGATION_PARSER_NON_DETERMINISM.md`) identified 4 corpus models potentially affected by the `table_row` → `simple_label` ambiguity: `chenery` (confirmed 65% corruption rate), `clearlak`, `indus`, `indus89`. Only `chenery` currently manifests at the comparison layer; the others are silent. Per-commit fixtures cover `chenery`; nightly broad-scope catches the three silent ones.

### What Option C is **not**

- Not an alternative to landing the Option D grammar fix (`_resolve_ambiguities()` patch in `src/ir/parser.py`); the Option D fix is required **first** so the test passes on green baseline.
- Not a replacement for golden-file regression tests; those track intentional output changes. PR12 specifically guards against **unintentional** output changes across identical inputs.
- Not a performance benchmark; no wall-clock assertions.

---

## 3. Statistical Analysis (Unknown 6.2)

KU 6.2 asked: with what seed sample size can we hit ≥95% confidence of catching a `#1283`-class bug that corrupts a fraction `p` of runs?

Under the binomial model, the probability of **missing** a bug (all N seeds produce correct output) is `(1 - p)^N`. Confidence of detection = `1 - (1 - p)^N`.

| Per-seed corruption rate `p` | N=3   | N=5   | N=7   | N=10  |
|------------------------------|-------|-------|-------|-------|
| **0.33** (KU 6.2 assumption) | 69.9% | 86.5% | 93.9% | 98.2% |
| **0.50** (median case)       | 87.5% | 96.9% | 99.2% | 99.9% |
| **0.65** (observed on chenery per Task 3) | 95.7% | 99.5% | 99.94% | 99.997% |

**Corrections to KU 6.2:**

- The original KU 6.2 cited a ~33% corruption rate from Sprint 24 Day 13 (small-sample observation from 3 back-to-back CLI runs). Task 3's formal 20-seed sweep measured the actual rate at **65%**.
- KU 6.2 also stated "≥95% confidence at 5 seeds" under the 33% assumption — this is an arithmetic error (5 seeds at p=0.33 gives 86.5%, not ≥95%). At the observed p=0.65 rate, 5 seeds gives 99.5%, so the practical claim holds under the measured data.
- Corrected statement: **5 seeds deliver ≥95% confidence iff per-seed corruption rate `p` ≥ 0.45**. At the observed p=0.65 this is met with margin; under the pessimistic-assumption p=0.33 it is not met (would need N=8 for ≥95%).

**Design choice:** 5 fixed seeds for per-commit (Option A) — sufficient at observed rate, and the extra two seeds from N=7 hedge for pessimistic p=0.33 are not free (5 models × 7 seeds = 35 translations per CI run vs 25). Nightly full-pipeline (Option B) re-validates at two seeds across the 143-model corpus, amortizing the seed budget across corpus scope instead of seed count.

---

## 4. Fixture Set (Option A, 5 models)

| Model           | Role                               | Rationale |
|-----------------|------------------------------------|-----------|
| **`chenery`**   | Primary reproducer                 | Task 3 confirmed 65% corruption rate; must be byte-stable after Option D fix lands |
| **`indus89`**   | Silent-corruption guard            | Task 3 flagged as potentially affected by the same `table_row` ambiguity; currently downstream-failing so corruption is silent until the Option D fix lands |
| **`abel`**      | Framework sanity                   | Simplest convex NLP (3 vars, 2 eqs, translate ≈ 3s); confirms the test harness works on non-#1283 code paths so false positives are caught |
| **`partssupply`** | Alias-heavy + emitter coverage   | Sprint 24 PR #1264 landed dispatcher handlers here; exercises `$ifThen`, `dollar_cond`, `yes_cond` emit paths alongside alias differentiation — broadest downstream coverage per fixture-minute |
| **`ps2_f`**     | PS-family alias tier-1 canary      | Task 2 audit classifies `ps2_f` as an alias-using matching canary (Tier 1); catches any seed-dependent drift in `_alias_match` / `_same_root_set` logic |

**Why not 10 fixtures?** Each extra fixture roughly doubles the per-seed cost (full translate, not just parse). 5 × 5 = 25 translations ≈ 60s fits within the 5-minute fast-suite budget (~1.5 min currently headroom per Sprint 24 CI tuning). 10 fixtures would push into 2 minutes just for this single test — not worth it given the nightly Option B already covers broader corpus scope.

**Why `indus89` specifically over `clearlak` or `indus`?** Task 3 lists four potentially-affected models; `indus89` has the largest multi-row-label table and therefore the highest a priori chance of triggering a rare ambiguity class. `clearlak` is tracked separately as a Sprint 25 Priority 2 item (#1291, emitter ordering) — coupling would create false-positive noise.

---

## 5. Seed Set

### Per-commit (Option A)

- **Fixed seeds: 0, 1, 42, 12345, 99999**
- Rationale: reproducibility for CI + local debugging. A failing seed can be re-invoked deterministically. Per §3, this hits 99.5% confidence at the observed p=0.65 corruption rate on chenery.
- Listed in a module-level constant `FAST_SEEDS` in the test file so the test body is data-driven via `pytest.mark.parametrize`.

### Nightly (Option B)

- **Two seeds: 0 and 99999** (endpoints of the fixed per-commit set; two distinct fixed seeds for comparison).
- Rationale: two is the arithmetic minimum for a comparison, and we're running the full 143-model corpus — amortizing scope across seed count makes more sense than amortizing seed count across scope. Expected wall-clock: ~4h30m (2 × 2h15m baseline).

### Why not random seeds?

Random-per-run seeds would theoretically broaden coverage across a large seed space, but:

- Per-seed corruption rate is high (0.33–0.65); the marginal seed beyond N=5 is low-value on a known bug.
- Flaky-seed debugging requires reproducibility — a failing random seed must be reported and pinned by the test harness, which adds complexity.
- The test is **guarding an invariant**, not discovering new bugs. Fixed seeds keep the failure mode boring and predictable.

A random-seed rotation harness can be added later as a Sprint-26 nice-to-have if we find the fixed set produces stale coverage.

---

## 6. Assertion Design

### Per-seed assertion

Each `(model, seed)` pair produces an MCP `.gms` output file via the subprocess invocation in §7. The test reads that file as **raw bytes** (`Path.read_bytes()`, which returns the on-disk bytes without decoding — the file content happens to be UTF-8 text, but the assertion never decodes it). The test asserts that for a given model, every seed produces a byte-identical result to the first seed:

```python
outputs: dict[int, bytes] = {seed: translate_to_bytes(model, seed) for seed in FAST_SEEDS}
reference = outputs[FAST_SEEDS[0]]
for seed, out in outputs.items():
    assert out == reference, _format_determinism_failure(model, FAST_SEEDS[0], seed, reference, out)
```

Here `translate_to_bytes(model, seed)` is the helper that runs the subprocess from §7 and returns `Path(output_path).read_bytes()` — so the comparison is consistently byte-level throughout.

### Failure-diagnostic format

On mismatch, the test dumps:

1. Model name + reference seed (always `FAST_SEEDS[0]`) + failing seed.
2. Line count diff on the decoded text (`len(reference.decode("utf-8").splitlines())` vs `len(failing.decode("utf-8").splitlines())`).
3. First N diff lines via `difflib.unified_diff` on the decoded text (capped at 40 lines to keep CI log readable; the full raw bytes are written to an artifact file under `tests/artifacts/determinism/` for post-mortem review).
4. The commit SHA (`os.environ.get("GITHUB_SHA", "local")`) to help bisect across commits.

### What counts as a match

- Byte-identical: compare encoded bytes, e.g. `reference.encode("utf-8") == other.encode("utf-8")` (equivalently, read the output file via `Path(output_path).read_bytes()` and compare directly).
- Whitespace-sensitive: trailing whitespace / newlines matter. #1283-class bugs can manifest as reordered lines, so whitespace normalization would mask real bugs.
- UTF-8 consistent: `emit_gams_mcp` output is UTF-8 text and may include non-ASCII characters in comments (e.g., `∇`, `⊥`, `≥` when `add_comments` is enabled), so comparisons should be done as UTF-8 bytes (or directly via `Path.read_bytes()`), avoiding any text normalization.

---

## 7. CI Integration Plan

### New pytest marker

Register a `determinism` marker in `pyproject.toml` under `[tool.pytest.ini_options] markers = [...]`:

```toml
markers = [
    "unit: ...",
    "integration: ...",
    "e2e: ...",
    "validation: ...",
    "slow: ...",
    "determinism: Byte-stability regression tests across PYTHONHASHSEED values (PR12)",
]
```

**Follows existing precedent** — `unit`, `integration`, `e2e`, `validation`, `slow` markers are all registered this way. `--strict-markers` is already enabled, so unregistered markers would fail loudly.

### New test file

- **Path:** `tests/integration/test_pipeline_determinism.py`
- **Classes:** `TestDeterminismFast` (Option A, per-commit) and `TestDeterminismFull` (Option B, nightly-only).
- **Markers:**
  - `TestDeterminismFast`: `@pytest.mark.integration` + `@pytest.mark.determinism` (runs in fast suite).
  - `TestDeterminismFull`: `@pytest.mark.slow` + `@pytest.mark.determinism` (excluded from fast suite).

### Subprocess invocation

Seeds must be set via `PYTHONHASHSEED` environment variable **before** Python startup, so the test cannot `os.environ["PYTHONHASHSEED"] = ...` and then reuse the current interpreter. Each translation runs as a subprocess and writes MCP output to a `.gms` file via `-o <path>` (the actual `src.cli` MCP-output option; `src.cli` does not have a `--format` flag for MCP output — `--format` is reserved for diagnostics only):

```python
env = os.environ.copy()
env["PYTHONHASHSEED"] = str(seed)
with tempfile.TemporaryDirectory() as tmpdir:
    output_path = Path(tmpdir) / "model.gms"
    subprocess.run(
        [sys.executable, "-m", "src.cli", model_path, "-o", str(output_path)],
        env=env, capture_output=True, text=True, check=True,
    )
    output_bytes = output_path.read_bytes()
```

### CI workflow wiring

**Fast suite (existing `.github/workflows/ci.yml` step "Run fast test suite"):**

- No change needed — `pytest -m "not slow"` already picks up `TestDeterminismFast` because it is not `slow`-marked.
- Expected added wall-clock: **~60s** (5 models × 5 seeds × ~2.5s/translate). Within the 5-minute `timeout-minutes` budget (Sprint 24 headroom ≈ 1.5 min).

**Nightly workflow (new file `.github/workflows/nightly.yml`):**

```yaml
name: Nightly determinism sweep
on:
  schedule:
    - cron: "17 7 * * *"  # 07:17 UTC daily
  workflow_dispatch:      # manual trigger
jobs:
  determinism-full:
    runs-on: ubuntu-latest
    timeout-minutes: 360
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"
      - run: pip install -e ".[dev]"
      - run: pytest -m "slow and determinism" -v --tb=short tests/integration/test_pipeline_determinism.py
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: determinism-diffs
          path: tests/artifacts/determinism/
          retention-days: 30
```

- `17 7 * * *` avoids the top-of-hour cron storm.
- `workflow_dispatch` lets a human rerun on-demand when Option D lands or a regression is suspected.
- Failure uploads the full diff artifact (`tests/artifacts/determinism/`) for post-mortem review.

### Implementation risk & mitigations

- **Risk:** subprocess startup overhead inflates wall-clock. Mitigation: use `pytest-xdist` (`-n auto`) — each `(model, seed)` pair parallelizes independently since they're pure-function reads.
- **Risk:** the CLI entry point used for GAMS MCP emission (via `-o <path>`) may not be the exact emit-entry-point in use. Mitigation: verify during Day 1 implementation; if the CLI wraps additional logic, bypass the CLI by constructing `ModelIR → emit_gams_mcp` directly in-process per seed (subprocess still needed to isolate `PYTHONHASHSEED`).
- **Risk:** #1283 is not fully fixed by Option D before the test lands, causing red CI on day 1. Mitigation: **the test MUST land after the Option D fix**; Sprint 25 Day 1 order is (1) Option D grammar fix, (2) PR12 test. This is enforced in the Day 1 prompts.

---

## 8. Verification of Unknown 6.2

- **Priority:** Low (KU 6.2 original classification correct).
- **Status:** ✅ VERIFIED (Prep Task 10, 2026-04-21).
- **Finding:** 5 fixed seeds is the right per-commit choice; the KU 6.2 "~7 seeds for 95% at 33%" claim was arithmetically slightly off (actual answer: ~8 seeds at 33%), but the observed corruption rate (65% per Task 3) makes 5 seeds comfortably sufficient (99.5% confidence). Rotating random seeds deferred; use fixed seeds for reproducibility.
- **CI budget check:** per-commit added cost ≈ 60s, fits in the 5-min fast-suite budget; nightly ≈ 4h30m, fits in a 6h timeout-minutes allowance on a dedicated workflow.
- **Decision:** Option C — 5-seed × 5-model per-commit + 2-seed × 143-model nightly.

---

## 9. Acceptance Criteria

- [x] Scope decision made with rationale → §2 (Option C)
- [x] ≥ 5 fixture models selected → §4 (chenery, indus89, abel, partssupply, ps2_f)
- [x] Seed set defined → §5 (`FAST_SEEDS = [0, 1, 42, 12345, 99999]`; nightly `[0, 99999]`)
- [x] CI integration plan ready for Sprint 25 Day 2 implementation → §7 (test file path, marker, workflow YAML drafted)
- [x] Unknown 6.2 verified and updated → §8 + `KNOWN_UNKNOWNS.md`

---

## 10. Related Documents

- `INVESTIGATION_PARSER_NON_DETERMINISM.md` (Task 3) — root-cause analysis + Option D fix design.
- `BASELINE_METRICS.md` §6 (Task 9) — the 3 committed MCP artifacts (`chenery`, `indus`, `turkey`) flagged advisory-only until PR12 enforces determinism.
- `PREP_PLAN.md` §Task 10 — this task's specification.
- `KNOWN_UNKNOWNS.md` §Unknown 6.2 — verification results.
- Sprint 24 retrospective §New Recommendations PR12 — source of the requirement.

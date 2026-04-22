"""Byte-stability regression tests (PR12 / issue #1283).

Runs the nlp2mcp CLI under multiple `PYTHONHASHSEED` values for a fixed set of
fixture models, and asserts that every seed produces byte-identical `.gms`
output. Catches `#1283`-class parser / emission non-determinism in CI instead
of via manual reviewer inspection.

Usage:
- Per-commit (fast): `pytest -m "integration and determinism"`
  Runs `TestDeterminismFast` — 5 fixture models × 5 fixed seeds.
- Nightly (slow): `pytest -m "slow and determinism"`
  Runs `TestDeterminismFull` — the full 143-model convex corpus × 2 seeds.

See `docs/planning/EPIC_4/SPRINT_25/DESIGN_DETERMINISM_TESTS.md` for the full
scope / fixture / seed-set rationale.
"""

from __future__ import annotations

import difflib
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_ROOT / "data" / "gamslib" / "raw"
ARTIFACT_DIR = REPO_ROOT / "tests" / "artifacts" / "determinism"

# Per-commit fixtures — all with baseline translate time <10s so the
# parametrized 5-seed sweep stays within the ~60s fast-suite budget.
#
# `DESIGN_DETERMINISM_TESTS.md` §4 originally proposed `indus89` as the
# "silent-corruption guard" (second most likely to trigger the #1283
# `table_row` / `simple_label` / `dotted_label` ambiguity), but:
#
#   - `indus89` is out-of-scope (`convexity.status = error`) — CLI exits
#     nonzero, so we can't compare bytes across seeds.
#   - `indus` is in-scope but baseline translate time is 101s, far above
#     the per-commit budget. Same for `clearlak` at 323s.
#
# Silent-corruption coverage is therefore deferred to `TestDeterminismFull`'s
# nightly full-corpus sweep (2 seeds × 135 translating models) which catches
# any #1283-class regression on `indus`, `clearlak`, or `indus89` (when
# upstream convexity status changes).
FAST_FIXTURES: tuple[str, ...] = ("chenery", "abel", "partssupply", "ps2_f", "himmel11")
FAST_SEEDS: tuple[int, ...] = (0, 1, 42, 12345, 99999)

NIGHTLY_SEEDS: tuple[int, ...] = (0, 99999)


def _translate_to_bytes(model: str, seed: int) -> bytes:
    """Run `python -m src.cli <model>.gms -o <tmp>` under PYTHONHASHSEED=seed.

    Returns the raw bytes of the emitted MCP file (via `Path.read_bytes()`) —
    no decoding, no text normalization.

    Raises `FileNotFoundError` when the raw model is absent. Callers invoking
    this from a worker thread must convert that to a pytest skip/fail in the
    main thread — `pytest.skip()` raised from a worker thread propagates as a
    regular exception and errors the test instead of skipping cleanly.
    """
    raw_path = RAW_DIR / f"{model}.gms"
    if not raw_path.is_file():
        raise FileNotFoundError(f"raw/{model}.gms not present (data/gamslib/raw/ is gitignored)")

    env = os.environ.copy()
    env["PYTHONHASHSEED"] = str(seed)
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / f"{model}_mcp.gms"
        subprocess.run(
            [
                sys.executable,
                "-m",
                "src.cli",
                str(raw_path),
                "-o",
                str(output_path),
                "--skip-convexity-check",
            ],
            env=env,
            capture_output=True,
            text=True,
            check=True,
            timeout=300,
        )
        return output_path.read_bytes()


def _format_determinism_failure(
    model: str,
    reference_seed: int,
    failing_seed: int,
    reference: bytes,
    failing: bytes,
) -> str:
    """Human-readable diff + artifact dump for a byte mismatch.

    Dumps:
    - model name + both seeds
    - line-count comparison
    - first 40 lines of `difflib.unified_diff` on the decoded text
    - the commit SHA (for bisect)
    - full raw bytes to `tests/artifacts/determinism/<model>_seed<N>.gms`
    """
    ref_text = reference.decode("utf-8", errors="replace")
    fail_text = failing.decode("utf-8", errors="replace")
    ref_lines = ref_text.splitlines(keepends=True)
    fail_lines = fail_text.splitlines(keepends=True)

    diff_iter = difflib.unified_diff(
        ref_lines,
        fail_lines,
        fromfile=f"{model} seed={reference_seed}",
        tofile=f"{model} seed={failing_seed}",
        n=3,
    )
    diff_lines = list(diff_iter)[:40]

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    ref_path = ARTIFACT_DIR / f"{model}_seed{reference_seed}.gms"
    fail_path = ARTIFACT_DIR / f"{model}_seed{failing_seed}.gms"
    ref_path.write_bytes(reference)
    fail_path.write_bytes(failing)

    commit_sha = os.environ.get("GITHUB_SHA", "local")

    return (
        f"\nDeterminism regression on {model} at commit {commit_sha}\n"
        f"  reference seed: {reference_seed} ({len(ref_lines)} lines, {len(reference)} bytes)\n"
        f"  failing seed:   {failing_seed} ({len(fail_lines)} lines, {len(failing)} bytes)\n"
        f"  artifacts:      {ref_path} vs {fail_path}\n"
        f"\n" + "".join(diff_lines)
    )


@pytest.mark.integration
@pytest.mark.determinism
class TestDeterminismFast:
    """Per-commit byte-stability sweep: 5 fixtures × 5 seeds ≈ 60s wall-clock.

    Each fixture model is translated under `FAST_SEEDS` and every output is
    asserted byte-identical to the `FAST_SEEDS[0]` output. A single failing
    (model, seed) pair dumps the first-differing diff plus raw-bytes artifacts
    and reports the commit SHA for bisecting.
    """

    @pytest.mark.parametrize("model", FAST_FIXTURES)
    def test_byte_stability_across_hash_seeds(self, model: str) -> None:
        # Precheck fixture presence on the main thread — `pytest.skip()` raised
        # from a ThreadPoolExecutor worker propagates as a regular exception and
        # errors the test instead of cleanly skipping.
        raw_path = RAW_DIR / f"{model}.gms"
        if not raw_path.is_file():
            pytest.skip(f"raw/{model}.gms not present (data/gamslib/raw/ is gitignored)")

        # Run seeds in parallel threads so the CLI-startup overhead (~15s of
        # module imports + parser construction per subprocess) amortizes across
        # cores. Combined with pytest-xdist fanout across models, 5 fixtures ×
        # 5 seeds = 25 concurrent subprocesses.
        with ThreadPoolExecutor(max_workers=len(FAST_SEEDS)) as pool:
            outputs: dict[int, bytes] = dict(
                zip(
                    FAST_SEEDS,
                    pool.map(lambda s: _translate_to_bytes(model, s), FAST_SEEDS),
                    strict=True,
                )
            )
        reference = outputs[FAST_SEEDS[0]]
        for seed, out in outputs.items():
            if seed == FAST_SEEDS[0]:
                continue
            assert out == reference, _format_determinism_failure(
                model, FAST_SEEDS[0], seed, reference, out
            )


@pytest.mark.slow
@pytest.mark.determinism
class TestDeterminismFull:
    """Nightly full-corpus byte-stability sweep: 143-model × 2 seeds ≈ 4h30m.

    Scheduled via `.github/workflows/nightly.yml` (cron "17 7 * * *"). Excluded
    from the fast suite because the 143-model cross-product exceeds the 5-minute
    per-commit CI budget.
    """

    @staticmethod
    def _convex_models() -> list[str]:
        """Enumerate the 143 convex in-scope models from the frozen baseline status."""
        status_path = REPO_ROOT / "data" / "gamslib" / "gamslib_status.json"
        if not status_path.is_file():
            pytest.skip("data/gamslib/gamslib_status.json not present")
        data = json.loads(status_path.read_text())
        return sorted(
            e["model_id"]
            for e in data["models"]
            if (e.get("convexity") or {}).get("status") in ("likely_convex", "verified_convex")
        )

    def test_full_corpus_byte_stability(self) -> None:
        models = self._convex_models()
        if not models:
            pytest.skip("no convex in-scope models found in status JSON")

        # Translate failures are out-of-scope for determinism — only compare
        # models that successfully translate. Record and skip. `FileNotFoundError`
        # covers missing raw fixtures (e.g., a runner with an incomplete corpus);
        # `TimeoutExpired` covers models that exceed the 300s per-seed timeout
        # on slower runners (both raised by `_translate_to_bytes`).
        translate_failures = (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            FileNotFoundError,
        )
        failures: list[tuple[str, str]] = []
        for model in models:
            try:
                ref = _translate_to_bytes(model, NIGHTLY_SEEDS[0])
            except translate_failures as e:
                failures.append((model, f"ref seed {NIGHTLY_SEEDS[0]} translate failed: {e}"))
                continue
            for seed in NIGHTLY_SEEDS[1:]:
                try:
                    other = _translate_to_bytes(model, seed)
                except translate_failures as e:
                    failures.append((model, f"seed {seed} translate failed: {e}"))
                    continue
                if other != ref:
                    failures.append(
                        (
                            model,
                            _format_determinism_failure(model, NIGHTLY_SEEDS[0], seed, ref, other),
                        )
                    )

        if failures:
            header = f"\n{len(failures)} determinism failures across {len(models)} models:\n\n"
            body = "\n\n---\n\n".join(f"## {m}\n{detail}" for m, detail in failures)
            pytest.fail(header + body)

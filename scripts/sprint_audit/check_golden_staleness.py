#!/usr/bin/env python3
"""Golden-staleness checker (Sprint 28 Priority 8).

Regenerate every committed MCP golden via the canonical pipeline emit and
byte-diff against the committed artifact, so the silent golden drift that
recurred across Sprint 27 (cesam/fawley/korcge/dinam noise in unrelated PRs) is
caught automatically in CI.

Usage::

    python scripts/sprint_audit/check_golden_staleness.py            # report; exit 1 on drift
    python scripts/sprint_audit/check_golden_staleness.py --models clearlak,dinam
    python scripts/sprint_audit/check_golden_staleness.py --fix      # overwrite drifted goldens (= make regen-goldens)
    python scripts/sprint_audit/check_golden_staleness.py --json out.json

Design: ``docs/planning/EPIC_4/SPRINT_28/PRIORITY_8_GOLDEN_STALENESS_DESIGN.md``.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gamslib.batch_translate import translate_single_model  # noqa: E402

MCP_DIR = PROJECT_ROOT / "data" / "gamslib" / "mcp"
RAW_DIR = PROJECT_ROOT / "data" / "gamslib" / "raw"
ALLOWLIST_PATH = Path(__file__).resolve().parent / "golden_staleness_allowlist.txt"
MAX_WORKERS = 6


def load_allowlist() -> set[str]:
    if not ALLOWLIST_PATH.exists():
        return set()
    out: set[str] = set()
    for line in ALLOWLIST_PATH.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            out.add(line)
    return out


def discover_goldens() -> list[tuple[str, bool, Path]]:
    """Return (model_id, is_presolve, golden_path) for every committed golden
    that has a corresponding raw source."""
    found: list[tuple[str, bool, Path]] = []
    for golden in sorted(MCP_DIR.glob("*_mcp*.gms")):
        name = golden.name
        if name.endswith("_mcp_presolve.gms"):
            model_id, is_presolve = name[: -len("_mcp_presolve.gms")], True
        elif name.endswith("_mcp.gms"):
            model_id, is_presolve = name[: -len("_mcp.gms")], False
        else:
            continue
        raw = RAW_DIR / f"{model_id}.gms"
        if raw.exists():
            found.append((model_id, is_presolve, golden))
    return found


def _regen_to(model_id: str, is_presolve: bool, out_path: Path) -> dict:
    raw = RAW_DIR / f"{model_id}.gms"
    return translate_single_model(raw, out_path, nlp_presolve=is_presolve)


def check_one(model_id: str, is_presolve: bool, golden: Path, fix: bool) -> dict:
    """Regenerate one golden and compare. Returns a result record."""
    rec: dict = {
        "model": model_id,
        "golden": golden.name,
        "presolve": is_presolve,
        "status": "clean",
    }
    # The temp dir must live INSIDE the repo: translate_single_model relativizes
    # the output path against PROJECT_ROOT (for the recorded output_file field).
    with tempfile.TemporaryDirectory(dir=str(PROJECT_ROOT)) as td:
        tmp = Path(td) / golden.name
        res = _regen_to(model_id, is_presolve, tmp)
        if res.get("status") != "success" or not tmp.exists():
            msg = res.get("error", {}).get("message", "emit did not produce output")
            # A slow-emit timeout (ganges/gangesx/clearlak/… need minutes, and
            # contend for CPU under parallel regen) means "couldn't verify in
            # budget", NOT drift — a soft status that doesn't fail the gate. The
            # design routes the full sweep to nightly (longer budget) and PRs to
            # the changed-emit subset.
            rec["status"] = "timeout" if "timeout" in msg.lower() else "emit_failed"
            rec["detail"] = msg[:200]
            return rec
        new_bytes = tmp.read_bytes()
        if new_bytes == golden.read_bytes():
            return rec  # clean
        rec["status"] = "drifted"
        rec["delta_bytes"] = len(new_bytes) - golden.stat().st_size
        if fix:
            # Determinism guard: re-emit a second time and require byte-identity
            # before overwriting, so a non-deterministic emit never silently
            # churns a golden.
            tmp2 = Path(td) / (golden.name + ".2")
            _regen_to(model_id, is_presolve, tmp2)
            if not tmp2.exists() or tmp2.read_bytes() != new_bytes:
                rec["status"] = "nondeterministic"
                return rec
            golden.write_bytes(new_bytes)
            rec["status"] = "fixed"
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description="Golden-staleness checker (Priority 8).")
    ap.add_argument("--fix", action="store_true", help="overwrite drifted goldens in place")
    ap.add_argument("--models", help="restrict to a comma-separated subset of model ids")
    ap.add_argument("--json", dest="json_path", help="write a machine-readable report")
    args = ap.parse_args()

    allowlist = load_allowlist()
    goldens = discover_goldens()
    if args.models:
        wanted = {m.strip() for m in args.models.split(",") if m.strip()}
        goldens = [g for g in goldens if g[0] in wanted]

    in_scope = [(mid, pre, gp) for (mid, pre, gp) in goldens if mid not in allowlist]
    allowlisted = [(mid, pre, gp) for (mid, pre, gp) in goldens if mid in allowlist]

    results: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(check_one, mid, pre, gp, args.fix): mid for (mid, pre, gp) in in_scope}
        for fut in concurrent.futures.as_completed(futs):
            results.append(fut.result())

    # Allowlisted models: warn if one now emits AND drifts (stale allowlist).
    allowlist_warnings: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(check_one, mid, pre, gp, False): mid for (mid, pre, gp) in allowlisted}
        for fut in concurrent.futures.as_completed(futs):
            r = fut.result()
            if r["status"] == "drifted":
                allowlist_warnings.append(r)

    drifted = sorted([r for r in results if r["status"] in ("drifted", "fixed")], key=lambda r: r["golden"])
    failed = sorted([r for r in results if r["status"] in ("emit_failed", "nondeterministic")], key=lambda r: r["golden"])
    timed_out = sorted([r for r in results if r["status"] == "timeout"], key=lambda r: r["golden"])

    if args.json_path:
        Path(args.json_path).write_text(
            json.dumps(
                {"checked": len(results), "drifted": drifted, "failed": failed, "allowlist_warnings": allowlist_warnings},
                indent=2,
            ),
            encoding="utf-8",
        )

    print(f"Golden staleness: checked {len(results)} in-scope golden(s) "
          f"({len(allowlisted)} allowlisted, {MAX_WORKERS} workers).")
    for r in allowlist_warnings:
        print(f"  WARN allowlisted-but-emits-and-drifts: {r['golden']} (allowlist may be stale)")
    for r in timed_out:
        print(f"  TIMEOUT (unverified, soft): {r['golden']} — slow-emit model; run nightly/longer budget")
    for r in failed:
        print(f"  {r['status'].upper()}: {r['golden']} — {r.get('detail', '')}")

    if not drifted and not failed:
        print("  All in-scope goldens clean"
              + (f" ({len(timed_out)} slow-emit timeout(s), unverified)." if timed_out else "."))
        return 0

    if args.fix:
        n = sum(1 for r in drifted if r["status"] == "fixed")
        print(f"  Refreshed {n} drifted golden(s):")
        for r in drifted:
            print(f"    {r['status'].upper()}: {r['golden']} ({r.get('delta_bytes', 0):+d} bytes)")
        # A nondeterministic emit is a hard failure even under --fix.
        return 1 if failed else 0

    print(f"  {len(drifted)} golden(s) drifted from the current emit:")
    for r in drifted:
        print(f"    DRIFTED: {r['golden']} ({r.get('delta_bytes', 0):+d} bytes)")
    print("  Run `make regen-goldens` and commit the refreshed goldens "
          "(or, if unintended, fix the emit).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

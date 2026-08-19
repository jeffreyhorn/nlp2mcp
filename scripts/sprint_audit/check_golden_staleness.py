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

Leak gate (Sprint 37 Prep Task 3) — assert that an intentional emit change
touches ONLY the model(s) it was designed for::

    python scripts/sprint_audit/check_golden_staleness.py --expect-drift markov
    make leak-check MODEL=markov

``--expect-drift`` turns the checker from "did anything drift?" into "did
*exactly* the intended set drift?", which is the question a shared-function
change (``_add_indexed_jacobian_terms``) actually needs answered. Without it the
remediation path (``make regen-goldens``) refreshes *every* drifted golden, so a
fix that leaks onto unrelated models launders the leak into the goldens and the
gate goes green — the Sprint-36 markov failure mode (the 6-model cohort missed
cesam/ferts/sroute).

Design: ``docs/planning/EPIC_4/SPRINT_28/PRIORITY_8_GOLDEN_STALENESS_DESIGN.md``
(base gate) and ``docs/planning/EPIC_4/SPRINT_37/LEAK_HARNESS_DESIGN.md``
(the ``--expect-drift`` leak gate).
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
# Sprint 37 Day 9: lowered 6 -> 3. At 6 the sweep's verdict is LOAD-DEPENDENT:
# the same command produced 4, then 2, then 0 timeouts across three runs on
# Day 2, because `ganges`/`clearlak` emit in 259-293 s standalone and the
# per-model budget is a hardcoded 600 s (`scripts/gamslib/batch_translate.py`),
# so under 6-way contention they exceed it and the gate reports UNVERIFIED
# rather than clean. That is not a false PASS — `--expect-drift` correctly
# refuses to certify an unverified sweep — but it makes a REQUIRED check fail
# open on a busy machine, and every Sprint-37 gate run needed this override
# applied by hand. At 3 workers the sweep completed with ZERO timeouts on every
# attempt (Days 2, 4, 6, 9). The wall-clock cost is modest: the sweep is bounded
# by its slowest single model, not by total work.
MAX_WORKERS = 3


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


def classify_missing_expected(
    missing: list[str],
    corpus_models: set[str],
    allowlisted_models: set[str],
) -> tuple[list[str], list[str], list[str]]:
    """Split "expected to drift but did not" into its three causes (Sprint 38 P6b).

    They have **opposite meanings** and were previously all reported as
    ``NO-OP: … the fix did not change the emit`` — a *correctness* claim:

    * ``no_golden``   — the model has no golden in the corpus, so it was never
      compared. This says nothing about the emit. ``sarf`` is the standing case:
      ``make leak-check MODEL=sarf`` reported that its fix did not change the
      emit, on a run that never looked at sarf.
    * ``allowlisted`` — the model HAS a golden but sits in the allowlist, so it
      was skipped. Also not a statement about the emit.
    * ``no_op``       — the model has a golden, was compared, and was
      byte-identical. This is the genuine no-op fix.

    All three still fail the gate (an unmet expectation is unmet either way), but
    conflating them sends an engineer to debug an emit that was never swept.

    Returns ``(no_golden, allowlisted, no_op)``; the three partition ``missing``.
    """
    no_golden = sorted(m for m in missing if m not in corpus_models)
    allowlisted = sorted(m for m in missing if m in allowlisted_models)
    no_op = sorted(
        m for m in missing if m in corpus_models and m not in allowlisted_models
    )
    return no_golden, allowlisted, no_op


def main() -> int:
    ap = argparse.ArgumentParser(description="Golden-staleness checker (Priority 8).")
    ap.add_argument("--fix", action="store_true", help="overwrite drifted goldens in place")
    ap.add_argument("--models", help="restrict to a comma-separated subset of model ids")
    ap.add_argument("--json", dest="json_path", help="write a machine-readable report")
    ap.add_argument(
        "--expect-drift",
        dest="expect_drift",
        help=(
            "leak gate: comma-separated model ids expected to drift. Passes only if "
            "EXACTLY that set drifted (an unexpected drift is a LEAK; a missing one is a "
            "NO-OP fix). Unverified (timed-out) goldens void the leak claim unless "
            "--allow-unverified. With --fix, only expected models are refreshed."
        ),
    )
    ap.add_argument(
        "--allow-unverified",
        action="store_true",
        help="under --expect-drift, do not fail on timed-out (unverified) goldens",
    )
    ap.add_argument(
        "--min-scope",
        dest="min_scope",
        type=int,
        help=(
            "coverage floor: fail if fewer than N committed goldens are discoverable. "
            "discover_goldens() silently drops any golden whose raw source is absent, "
            "so a partial corpus yields a narrower sweep that still reports PASS. "
            "Use in CI to assert the corpus was actually provisioned."
        ),
    )
    args = ap.parse_args()

    expected: set[str] = set()
    if args.expect_drift is not None:
        expected = {m.strip() for m in args.expect_drift.split(",") if m.strip()}
        if not expected:
            # An empty value would silently disable the leak gate while leaving
            # --fix unrestricted (i.e. plain `make regen-goldens` laundering) —
            # exactly the failure mode this gate exists to prevent. Refuse.
            print(
                "ERROR: --expect-drift was given but names no model "
                f"(got {args.expect_drift!r}). Pass at least one model id, "
                "e.g. --expect-drift markov.",
                file=sys.stderr,
            )
            return 2

    # A leak claim is only as wide as the sweep: --models restricts which goldens
    # are compared, so drift outside that subset is invisible. The combination is
    # allowed (it is how the gate is iterated on), but the verdict is labelled a
    # SUBSET claim and must never read as full-corpus.
    subset_scope = bool(expected and args.models)

    allowlist = load_allowlist()
    goldens = discover_goldens()

    # Coverage floor, asserted on DISCOVERY (before --models narrowing): a golden
    # whose raw source is absent is dropped by discover_goldens() without comment,
    # so an under-provisioned corpus produces a narrower sweep that still reports
    # PASS. That is the same "unverified is not clean" failure --expect-drift
    # guards against, one level earlier — and it is invisible in the summary,
    # which reports the count it happened to check rather than the count it should
    # have. A floor (not an equality) so adding goldens never trips it.
    if args.min_scope is not None and len(goldens) < args.min_scope:
        have = {mid for (mid, _pre, _gp) in goldens}
        missing = sorted(
            {
                p.name[: -len("_mcp_presolve.gms")]
                if p.name.endswith("_mcp_presolve.gms")
                else p.name[: -len("_mcp.gms")]
                for p in MCP_DIR.glob("*_mcp*.gms")
            }
            - have
        )
        print(
            f"ERROR: coverage floor not met — discovered {len(goldens)} golden(s), "
            f"expected at least {args.min_scope}. The sweep would silently skip "
            f"{len(missing)} model(s) whose raw source is absent from "
            f"{RAW_DIR}/, and still report PASS.\n"
            f"  missing raw source: {', '.join(missing) if missing else '(none)'}\n"
            "  Provision the corpus (scripts/download_gamslib_raw.sh --all) or "
            "lower --min-scope deliberately.",
            file=sys.stderr,
        )
        return 2

    if args.models:
        wanted = {m.strip() for m in args.models.split(",") if m.strip()}
        goldens = [g for g in goldens if g[0] in wanted]

    in_scope = [(mid, pre, gp) for (mid, pre, gp) in goldens if mid not in allowlist]
    allowlisted = [(mid, pre, gp) for (mid, pre, gp) in goldens if mid in allowlist]

    results: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        # Under --expect-drift, --fix refreshes ONLY the expected models: an
        # unexpected drift is a leak to be surfaced, never a golden to rewrite.
        futs = {
            ex.submit(
                check_one, mid, pre, gp, args.fix and (not expected or mid in expected)
            ): mid
            for (mid, pre, gp) in in_scope
        }
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

    drifted = sorted(
        [r for r in results if r["status"] in ("drifted", "fixed")], key=lambda r: r["golden"]
    )
    failed = sorted(
        [r for r in results if r["status"] in ("emit_failed", "nondeterministic")],
        key=lambda r: r["golden"],
    )
    timed_out = sorted([r for r in results if r["status"] == "timeout"], key=lambda r: r["golden"])

    drifted_models = {r["model"] for r in drifted}
    leaked = sorted(drifted_models - expected) if expected else []
    missing = sorted(expected - drifted_models) if expected else []

    no_golden, skipped_allowlisted, no_op = classify_missing_expected(
        missing,
        corpus_models={mid for (mid, _pre, _gp) in goldens},
        allowlisted_models={mid for (mid, _pre, _gp) in allowlisted},
    )

    # Everything that narrows what this run actually compared. Each entry
    # downgrades a PASS from a full-corpus claim to a partial one — the verdict
    # line gets pasted as Phase-0 evidence, so it must never overstate
    # byte-identity over goldens that were skipped or never compared.
    claim_caveats: list[str] = []
    if subset_scope:
        claim_caveats.append(
            f"--models restricted the sweep to {len(results)} of the in-scope goldens; "
            "drift outside that subset was not checked"
        )
    if expected and timed_out and args.allow_unverified:
        claim_caveats.append(
            f"{len(timed_out)} golden(s) timed out and were accepted unverified via "
            f"--allow-unverified ({', '.join(r['golden'] for r in timed_out)}); "
            "they were never compared"
        )

    if args.json_path:
        Path(args.json_path).write_text(
            json.dumps(
                {
                    "checked": len(results),
                    "drifted": drifted,
                    "failed": failed,
                    "allowlist_warnings": allowlist_warnings,
                    **(
                        {
                            "expected_drift": sorted(expected),
                            "leaked": leaked,
                            "missing_expected": missing,
                            "missing_no_golden": no_golden,
                            "missing_allowlisted": skipped_allowlisted,
                            "missing_no_op": no_op,
                            "unverified": [r["golden"] for r in timed_out],
                            # "full-corpus" only when nothing narrowed the sweep;
                            # "partial" when a --models subset and/or goldens
                            # accepted unverified mean byte-identity is not
                            # asserted corpus-wide.
                            "leak_claim_scope": ("partial" if claim_caveats else "full-corpus"),
                            "claim_caveats": claim_caveats,
                        }
                        if expected
                        else {}
                    ),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    print(
        f"Golden staleness: checked {len(results)} in-scope golden(s) "
        f"({len(allowlisted)} allowlisted, {MAX_WORKERS} workers)."
    )
    for r in allowlist_warnings:
        print(f"  WARN allowlisted-but-emits-and-drifts: {r['golden']} (allowlist may be stale)")
    for r in timed_out:
        print(
            f"  TIMEOUT (unverified, soft): {r['golden']} — slow-emit model; run nightly/longer budget"
        )
    for r in failed:
        print(f"  {r['status'].upper()}: {r['golden']} — {r.get('detail', '')}")

    # ---- Leak gate (--expect-drift): did EXACTLY the intended set drift? ----
    if expected:
        if subset_scope:
            print(
                f"  WARNING: --models restricted this sweep to {len(results)} golden(s); "
                "drift outside that subset is NOT checked, so this cannot support a "
                "full-corpus leak claim."
            )
        for r in drifted:
            tag = "EXPECTED" if r["model"] in expected else "LEAK"
            print(f"    {tag} DRIFT: {r['golden']} ({r.get('delta_bytes', 0):+d} bytes)")
        ok = not leaked and not missing and not failed
        # A leak claim cannot be made over goldens that were never verified.
        unverified_blocks = bool(timed_out) and not args.allow_unverified
        if leaked:
            print(
                f"  LEAK: {len(leaked)} unexpected model(s) drifted: {', '.join(leaked)}\n"
                "  The change is NOT confined to its target — do NOT run `make regen-goldens` "
                "(that would launder the leak into the goldens). Narrow the predicate."
            )
        if no_op:
            print(
                f"  NO-OP: expected drift on {', '.join(no_op)} but the emit was byte-identical "
                "— the fix did not change the emit."
            )
        if skipped_allowlisted:
            print(
                f"  ALLOWLISTED: expected drift on {', '.join(skipped_allowlisted)}, but that "
                "model is in golden_staleness_allowlist.txt, so it was never compared. Remove "
                "it from the allowlist to gate it, or drop it from --expect-drift."
            )
        if no_golden:
            print(
                f"  NO-GOLDEN: expected drift on {', '.join(no_golden)}, but that model has NO "
                "golden in the corpus, so this sweep never compared it. This is NOT a statement "
                "about the emit — the gate is being asked about a model outside its scope.\n"
                "  For a model with no golden the correct gate is `make check-goldens` (zero "
                "drift across the corpus) PLUS the model newly producing a golden."
            )
        if unverified_blocks:
            print(
                f"  UNVERIFIED: {len(timed_out)} golden(s) timed out — the leak claim is "
                "inconclusive. Re-run with the nightly/full budget (or --allow-unverified "
                "to accept a partial claim)."
            )
        if ok and not unverified_blocks:
            # A leak claim is only as strong as what was actually compared. Any
            # gap (a --models subset, or timed-out goldens waved through with
            # --allow-unverified) downgrades the verdict — this line gets pasted
            # as Phase-0 evidence, so it must never overstate byte-identity.
            if claim_caveats:
                print(
                    f"  LEAK GATE PASS (PARTIAL — NOT a full-corpus leak claim): exactly the "
                    f"expected model(s) drifted ({', '.join(sorted(expected))}) among the "
                    f"goldens that were actually compared."
                )
                for c in claim_caveats:
                    print(f"    caveat: {c}")
                print(
                    "    Byte-identity is NOT asserted for the models above. Re-run the full "
                    "sweep (no --models, full budget, no --allow-unverified) for the Phase-0 gate."
                )
            else:
                print(
                    f"  LEAK GATE PASS: exactly the expected model(s) drifted "
                    f"({', '.join(sorted(expected))}); all other in-scope goldens byte-identical."
                )
            return 0
        return 1

    if not drifted and not failed:
        print(
            "  All in-scope goldens clean"
            + (f" ({len(timed_out)} slow-emit timeout(s), unverified)." if timed_out else ".")
        )
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
    print(
        "  Run `make regen-goldens` and commit the refreshed goldens "
        "(or, if unintended, fix the emit)."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

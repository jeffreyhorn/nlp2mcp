#!/usr/bin/env python3
"""Did the MCP actually solve, or did only the embedded NLP?

A ``--nlp-presolve`` emit warm-starts by running the original model inside the
generated file, then solves the MCP and reads the objective back::

    $include "data/gamslib/raw/<model>.gms"   * solves the NLP, sets <objvar>.l
    Solve mcp_model using MCP;                 * if this ABORTS, .l is untouched
    nlp2mcp_obj_val = <objvar>.l;              * still the NLP's own answer

On a **successful** run that listing therefore holds *two or more* solve
summaries — the embedded source's, then ours. **The failing case holds only
one**, and that asymmetry is the whole point: an MCP that aborts before its
solve never emits a summary at all, so the listing looks exactly like a
single-solve run whose one status happens to be someone else's.

**If the MCP solve aborts, the objective read returns the NLP's own value and
the comparison matches itself.** The recorded status is wrong the same way:
``parse_gams_listing`` takes the *last* ``MODEL STATUS`` in the listing, which
is the NLP's when the MCP produced none.

`weapons` is the discovered instance (Sprint 38 Day 9): one solve summary in the
whole listing (the embedded NLP's, MS-2 @ 1735.5696), the MCP aborted with
``EXECERROR = 1`` — yet the DB recorded ``model_optimal_presolve`` + match at
that same 1735.5696.

**The discriminator is per-solve attribution, not a global grep.** Every status
line in a GAMS listing belongs to the solve summary above it::

                   S O L V E      S U M M A R Y

         MODEL   mcp_model
         TYPE    MCP
         SOLVER  PATH                FROM LINE  1124

    **** SOLVER STATUS     1 Normal Completion
    **** MODEL STATUS      1 Optimal

So the question "did the MCP produce its own MODEL STATUS?" is answered by
finding a summary that is ``TYPE MCP`` **for our emitted model** and which
carries a ``MODEL STATUS`` — see ``EMITTED_MCP_MODEL`` for why the model name
matters and ``TYPE`` alone is not enough.

**Attribution is not success, and the verdicts keep them apart:**

===================  ===========================================================
``MCP-SOLVED``       our MCP reported MS-1/MS-2 — a usable answer
``MCP-FAILED``       our MCP reported a status, but a failing one (MS-4, MS-5…)
``EMBEDDED-ONLY``    **spurious** — only a non-emitted solve reported a status,
                     so the warm-start value is what gets read back
``MCP-NO-STATUS``    our MCP block exists but reported nothing — indeterminate
``NO-SOLVE``         no recognised solve at all — indeterminate
``ERROR``            could not be run — indeterminate
===================  ===========================================================

The three indeterminate verdicts are distinct on purpose. Folding them into the
spurious bucket would report "the embedded model solved and ours did not" when
*nothing* solved — a fabricated finding of exactly the kind this script exists
to catch.

``EMBEDDED-ONLY`` is named for provenance rather than model type: the population
includes LP, QCP and DNLP sources, so "NLP-ONLY" would misreport the solve kind
on a quarter of it.

**Deliberately NOT keyed on ``EXECERROR``.** `check_presolve_divergence.py`'s
first branch treats any execution error as an *embedded-NLP* divergence, which
is how weapons — whose embedded NLP solved perfectly — got reported against the
wrong side. An abort tells you *something* failed, not *which model*.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json"

#: The model name our emitter always uses — verified uniform across all 39
#: committed presolve goldens.
#:
#: **`TYPE MCP` alone is NOT a safe test.** Two raw corpus sources solve an MCP
#: of their own (`cesam.gms`, `spatequ.gms`), and a presolve emit `$include`s the
#: raw source — so their listings carry a `TYPE MCP` summary that is *not* ours.
#: Neither is in the presolve+match population today, but keying on the model
#: name costs nothing and stops the check reading a foreign MCP solve as proof
#: that ours ran.
EMITTED_MCP_MODEL = "mcp_model"

#: Indentation is optional throughout. Real GAMS listings indent these lines,
#: but attribution must not depend on that: a column-0 header (the shape
#: `scripts/gamslib/test_solve.py` already accepts, and that
#: `tests/gamslib/test_test_solve.py` exercises) would otherwise parse as
#: **zero** summaries and report a perfectly good run as ``NO-SOLVE``.
_SUMMARY_HEADER = re.compile(r"^[ \t]*S O L V E {6}S U M M A R Y\s*$", re.MULTILINE)
_MODEL_LINE = re.compile(r"^[ \t]*MODEL\s+(\S+)", re.MULTILINE)
_TYPE_LINE = re.compile(r"^[ \t]*TYPE\s+(\S+)", re.MULTILINE)
_SOLVER_LINE = re.compile(r"^[ \t]*SOLVER\s+(\S+)", re.MULTILINE)
_SOLVER_STATUS = re.compile(r"^\*\*\*\* SOLVER STATUS\s+(\d+)\s*(.*?)$", re.MULTILINE)
_MODEL_STATUS = re.compile(r"^\*\*\*\* MODEL STATUS\s+(\d+)\s*(.*?)$", re.MULTILINE)


@dataclass
class SolveSummary:
    """One ``S O L V E   S U M M A R Y`` block and the statuses beneath it."""

    model: str | None
    type: str | None
    solver: str | None
    solver_status: int | None
    model_status: int | None
    model_status_text: str | None

    @property
    def is_mcp(self) -> bool:
        """An MCP-typed solve — ours or the raw model's own."""
        return (self.type or "").upper() == "MCP"

    @property
    def is_emitted_mcp(self) -> bool:
        """An MCP-typed solve of *our* generated model."""
        return self.is_mcp and self.model == EMITTED_MCP_MODEL


def parse_solve_summaries(lst_content: str) -> list[SolveSummary]:
    """Split a GAMS listing into solve summaries, each owning its status lines.

    Attribution is positional: a status line belongs to the nearest summary
    header *above* it. That is the whole point — a listing-wide search for
    ``MODEL STATUS`` cannot tell you which model produced it.
    """
    starts = [m.start() for m in _SUMMARY_HEADER.finditer(lst_content)]
    summaries: list[SolveSummary] = []

    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(lst_content)
        block = lst_content[start:end]

        # The header fields sit in the first few lines; the statuses follow.
        model = _MODEL_LINE.search(block)
        type_ = _TYPE_LINE.search(block)
        solver = _SOLVER_LINE.search(block)
        sstat = _SOLVER_STATUS.search(block)
        mstat = _MODEL_STATUS.search(block)

        summaries.append(
            SolveSummary(
                model=model.group(1) if model else None,
                type=type_.group(1) if type_ else None,
                solver=solver.group(1) if solver else None,
                solver_status=int(sstat.group(1)) if sstat else None,
                model_status=int(mstat.group(1)) if mstat else None,
                model_status_text=mstat.group(2).strip() if mstat else None,
            )
        )

    return summaries


#: GAMS MODEL STATUS values that mean the solve produced a usable answer.
#: PATH reports **1 Optimal** for a solved complementarity problem; 2 is
#: CONOPT's "Locally Optimal". Anything else (4 Infeasible, 5 Locally
#: Infeasible, 6 Intermediate Infeasible, …) is a failure.
_SUCCESS_MODEL_STATUS = frozenset({1, 2})

#: GAMS SOLVER STATUS 1 = "Normal Completion". Required alongside the model
#: status, matching `scripts/gamslib/test_solve.py`'s solve gate.
_NORMAL_COMPLETION = 1

#: Model ids become filesystem path components (`<raw>/<id>.gms`,
#: `<workdir>/<id>_mcp_presolve.gms`). Validated against the repository's safe
#: pattern so a `../` or a separator cannot escape either directory — and
#: validated at BOTH the CLI boundary and the consumer that builds the path,
#: per CONTRIBUTING's defense-in-depth rule.
_SAFE_MODEL_ID = re.compile(r"^[A-Za-z0-9_.-]+$")


def _is_safe_model_id(model_id: str) -> bool:
    """Reject anything that could traverse out of the directories we build."""
    return bool(_SAFE_MODEL_ID.match(model_id)) and model_id not in {".", ".."}


#: Verdicts that conclude nothing. Counted as failures of the *check*, never as
#: evidence either way about the model.
_INDETERMINATE_VERDICTS = frozenset({"ERROR", "NO-SOLVE", "MCP-NO-STATUS"})


@dataclass
class Attribution:
    """Whether a listing shows the MCP solving in its own right."""

    model_id: str
    summaries: list[SolveSummary] = field(default_factory=list)
    error: str | None = None
    #: GAMS's own exit code, recorded for transparency. **Deliberately not used
    #: to invalidate a listing:** `weapons` — the whole finding — exits **3**
    #: (`USER ERROR(S) ENCOUNTERED`) precisely *because* its MCP aborted. Keying
    #: on it would discard the case this script was written to detect.
    gams_returncode: int | None = None

    @property
    def mcp_summaries(self) -> list[SolveSummary]:
        """Solves of *our* emitted MCP — not a raw source's own MCP solve."""
        return [s for s in self.summaries if s.is_emitted_mcp]

    @property
    def foreign_mcp_summaries(self) -> list[SolveSummary]:
        """MCP solves belonging to the included raw model (`cesam`, `spatequ`).

        Surfaced rather than ignored: if one of these ever appears it means the
        listing has an MCP status that must NOT be read as ours.
        """
        return [s for s in self.summaries if s.is_mcp and not s.is_emitted_mcp]

    @property
    def embedded_summaries(self) -> list[SolveSummary]:
        """Every solve that is not our emitted MCP.

        Named for its *provenance*, not its model type: the population includes
        LP (`marco`, `paperco`, `tforss`), QCP (`cpack`, `qsambal`), DNLP
        (`maxmin`) and mixed (`robustlp`) sources, so calling this "the NLP" would
        misreport the solve kind on a quarter of the corpus.
        """
        return [s for s in self.summaries if not s.is_emitted_mcp]

    @property
    def mcp_produced_status(self) -> bool:
        """**Attribution only:** *our* MCP reported a MODEL STATUS.

        ⚠ This says the status belongs to our model — **not** that the solve
        succeeded. Keep it separate from the verdict: an MCP that returns MS-4
        has been attributed and has still not produced a usable answer.
        """
        return any(s.model_status is not None for s in self.mcp_summaries)

    @property
    def mcp_succeeded(self) -> bool:
        """Our MCP produced a usable answer — **both** statuses must be good.

        Matches the repository's existing solve gate
        (`scripts/gamslib/test_solve.py`: ``solver_status == 1 and model_status
        in (1, 2)``). MODEL STATUS alone is not enough: a solver that hits a
        resource or iteration limit can report a stale-but-plausible model
        status alongside SOLVER STATUS 3/4, and that is not a solved model.
        """
        return any(
            s.solver_status == _NORMAL_COMPLETION and s.model_status in _SUCCESS_MODEL_STATUS
            for s in self.mcp_summaries
        )

    @property
    def embedded_produced_status(self) -> bool:
        """Some non-emitted solve reported a status — the value a warm start leaves behind."""
        return any(s.model_status is not None for s in self.embedded_summaries)

    @property
    def verdict(self) -> str:
        """One of six outcomes. Only ``EMBEDDED-ONLY`` means *spurious*.

        The three indeterminate verdicts are deliberately distinct rather than
        folded into the spurious bucket: reporting "the embedded model solved and
        ours did not" when *nothing* solved would be a fabricated finding, which
        is the same error this script exists to catch.
        """
        if self.error:
            return "ERROR"
        if self.mcp_produced_status:
            return "MCP-SOLVED" if self.mcp_succeeded else "MCP-FAILED"
        if self.mcp_summaries:
            # Our MCP block exists but reported nothing — GAMS emits the header
            # during generation, so a solver that dies before reporting lands
            # here. Not attributable either way.
            return "MCP-NO-STATUS"
        if self.embedded_produced_status:
            # The spurious case: a status exists for the warm start to read back,
            # and it is not ours.
            return "EMBEDDED-ONLY"
        return "NO-SOLVE"

    @property
    def is_spurious(self) -> bool:
        """A recorded match that cannot have come from our MCP."""
        return self.verdict == "EMBEDDED-ONLY"

    @property
    def is_indeterminate(self) -> bool:
        """Nothing can be concluded — must not be silently counted as a pass."""
        return self.verdict in _INDETERMINATE_VERDICTS

    def as_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "verdict": self.verdict,
            "mcp_produced_status": self.mcp_produced_status,
            "mcp_succeeded": self.mcp_succeeded,
            "gams_returncode": self.gams_returncode,
            "n_summaries": len(self.summaries),
            "n_mcp_summaries": len(self.mcp_summaries),
            "n_foreign_mcp_summaries": len(self.foreign_mcp_summaries),
            "summaries": [
                {
                    "model": s.model,
                    "type": s.type,
                    "solver": s.solver,
                    "solver_status": s.solver_status,
                    "model_status": s.model_status,
                    "model_status_text": s.model_status_text,
                }
                for s in self.summaries
            ],
            "error": self.error,
        }


class InputError(Exception):
    """Bad input — reported with a concrete message and exit code 2, never a traceback."""


def presolve_match_models(db_path: Path = DB_PATH) -> list[str]:
    """Every model recorded ``model_optimal_presolve`` **and** match.

    The DB is hand-editable, so its shape is checked before it is indexed: a
    malformed file must produce an actionable error, not a ``KeyError`` from
    inside a list comprehension.
    """
    try:
        raw = db_path.read_text()
    except OSError as exc:
        raise InputError(f"cannot read results DB {db_path}: {exc}") from exc

    try:
        db = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InputError(f"results DB {db_path} is not valid JSON: {exc}") from exc

    if not isinstance(db, dict):
        raise InputError(f"results DB {db_path} must be a JSON object, got {type(db).__name__}")
    models = db.get("models")
    if not isinstance(models, list):
        raise InputError(f"results DB {db_path} has no top-level 'models' list")

    out = []
    for i, m in enumerate(models):
        if not isinstance(m, dict):
            raise InputError(f"{db_path}: models[{i}] must be an object, got {type(m).__name__}")
        model_id = m.get("model_id")
        solve = m.get("mcp_solve") or {}
        cmp_ = m.get("solution_comparison") or {}
        if not isinstance(solve, dict) or not isinstance(cmp_, dict):
            raise InputError(
                f"{db_path}: models[{i}] has a malformed mcp_solve/solution_comparison"
            )
        if (
            solve.get("outcome_category") == "model_optimal_presolve"
            and cmp_.get("comparison_status") == "match"
        ):
            if not isinstance(model_id, str) or not model_id:
                raise InputError(f"{db_path}: models[{i}] has a missing or non-string 'model_id'")
            if not _is_safe_model_id(model_id):
                raise InputError(f"{db_path}: models[{i}] has an unsafe model_id {model_id!r}")
            out.append(model_id)
    return sorted(out)


def find_gams() -> str | None:
    """Locate GAMS the way the rest of the repo does.

    Versioned install paths are preferred over a bare ``PATH`` lookup — mirrors
    `scripts/gamslib/test_solve.py`, where the comment explains why: a `PATH`
    entry may point at an older version whose time-limited license has expired.
    ``Current`` follows whatever version was installed last.
    """
    for candidate in (
        "/Library/Frameworks/GAMS.framework/Versions/Current/Resources/gams",
        "/opt/gams/gams",
        "C:\\GAMS\\win64\\gams.exe",
    ):
        if Path(candidate).exists():
            return candidate
    return shutil.which("gams")


def run_one(model_id: str, workdir: Path, reslim: int = 300) -> Attribution:
    """Emit ``--nlp-presolve`` for one model, run GAMS, and attribute the solves.

    GAMS runs with ``cwd`` at the project root — the emitted
    ``$include "data/gamslib/raw/<id>.gms"`` is repo-relative — while every
    scratch artifact goes to ``workdir``. Never run GAMS *from* the repo root
    without ``ScrDir``: Sprint 37 Day 9 swept the scratch files into a commit.

    ``workdir`` **must already be absolute** (``main`` resolves it): the paths
    below are handed to subprocesses whose ``cwd`` is ``PROJECT_ROOT``, so a
    relative one would have the child write somewhere the parent never looks.
    """
    # Defense in depth: `main` validates too, but this is the consumer that
    # actually builds the paths, and it is importable on its own.
    if not _is_safe_model_id(model_id):
        return Attribution(model_id, error=f"unsafe model id {model_id!r}")

    raw = PROJECT_ROOT / "data" / "gamslib" / "raw" / f"{model_id}.gms"
    if not raw.exists():
        return Attribution(model_id, error=f"raw source absent: {raw}")

    emitted = workdir / f"{model_id}_mcp_presolve.gms"
    lst = workdir / f"{model_id}.lst"

    try:
        emit = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.cli",
                str(raw.relative_to(PROJECT_ROOT)),
                "--nlp-presolve",
                "-o",
                str(emitted),
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        # One slow translation must not abort the whole sweep before it can
        # write its report — `sarf` alone runs for ~28 minutes.
        return Attribution(model_id, error="emit timeout after 600s")
    except OSError as exc:
        # A missing/unexecutable interpreter is one model's problem, not the
        # sweep's: return a structured indeterminate result and carry on.
        return Attribution(model_id, error=f"emit could not be launched: {exc}")

    if emit.returncode != 0 or not emitted.exists():
        return Attribution(model_id, error=f"emit failed (rc={emit.returncode})")

    gams = find_gams()
    if not gams:
        return Attribution(model_id, error="gams executable not found")

    # Never let a previous run's listing answer for this one. If GAMS dies
    # before writing (licensing, startup), a stale file would be parsed as this
    # run's result — a status attributed to the wrong invocation, which is the
    # very defect this script exists to detect, one level up.
    try:
        lst.unlink(missing_ok=True)
    except OSError as exc:
        return Attribution(model_id, error=f"cannot clear stale listing {lst}: {exc}")

    try:
        with tempfile.TemporaryDirectory(dir=str(workdir)) as scr:
            try:
                proc = subprocess.run(
                    [
                        gams,
                        str(emitted),
                        f"o={lst}",
                        "lo=2",
                        f"reslim={reslim}",
                        f"ScrDir={scr}",
                    ],
                    capture_output=True,
                    text=True,
                    cwd=str(PROJECT_ROOT),
                    timeout=reslim + 120,
                )
            except subprocess.TimeoutExpired:
                return Attribution(model_id, error=f"GAMS timeout after {reslim}s")
            except OSError as exc:
                # `find_gams` returned a path that is gone, a directory, or not
                # executable. One runner problem, not a dead sweep.
                return Attribution(model_id, error=f"GAMS could not be launched ({gams}): {exc}")
    except OSError as exc:
        return Attribution(model_id, error=f"cannot create scratch dir under {workdir}: {exc}")

    if not lst.exists():
        return Attribution(model_id, error=f"no listing produced (gams rc={proc.returncode})")

    try:
        content = lst.read_text(errors="replace")
    except OSError as exc:
        return Attribution(model_id, error=f"cannot read listing {lst}: {exc}")

    return Attribution(
        model_id,
        summaries=parse_solve_summaries(content),
        gams_returncode=proc.returncode,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--models",
        help="comma-separated model ids (default: every presolve+match row in the DB)",
    )
    ap.add_argument("--workdir", default=None, help="where to keep emits and listings")
    ap.add_argument("--reslim", type=int, default=300, help="GAMS resource limit, seconds (> 0)")
    ap.add_argument("--json", dest="json_out", help="write the full record here")
    ap.add_argument(
        "--allow-empty",
        action="store_true",
        help=(
            "permit a selection of zero models. The run then CERTIFIES NOTHING — "
            "use only when an empty selection is the expected state."
        ),
    )
    args = ap.parse_args(argv)

    # Range, not just type: `reslim` is handed to GAMS and also derives the
    # subprocess timeout (`reslim + 120`), where a negative would be nonsense.
    if args.reslim <= 0:
        print(
            f"ERROR: --reslim must be a positive number of seconds, got {args.reslim}",
            file=sys.stderr,
        )
        return 2

    try:
        if args.models:
            models = [m.strip() for m in args.models.split(",") if m.strip()]
            unsafe = [m for m in models if not _is_safe_model_id(m)]
            if unsafe:
                raise InputError(
                    "unsafe model id(s) "
                    + ", ".join(repr(m) for m in unsafe)
                    + " — must match [A-Za-z0-9_.-]+ (no separators, no '..')"
                )
        else:
            models = presolve_match_models()
    except InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    # An empty selection is NOT a pass. Every bucket would be empty, the
    # partition assertion would hold vacuously, and the run would exit 0 having
    # checked nothing — which is exactly how an unprovisioned or stale DB turns
    # into a green report. Same rule as `run_full_test.py --resolve-changed`.
    if not models:
        if not args.allow_empty:
            source = "--models" if args.models else f"{DB_PATH} (model_optimal_presolve + match)"
            print(
                f"ERROR: selection is empty — nothing to audit from {source}.\n"
                "       An empty run certifies nothing. Pass --allow-empty if that is expected.",
                file=sys.stderr,
            )
            return 2
        print("WARNING: selection is empty; this run CERTIFIES NOTHING.", file=sys.stderr)

    # Resolve before use: these paths are handed to subprocesses running with
    # `cwd=PROJECT_ROOT`, so a relative --workdir would send the child's output
    # somewhere the parent never looks.
    try:
        workdir = (
            Path(args.workdir).resolve()
            if args.workdir
            else Path(tempfile.mkdtemp(prefix="mcp_attr_"))
        )
        workdir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"ERROR: cannot create workdir {args.workdir!r}: {exc}", file=sys.stderr)
        return 2

    results: list[Attribution] = []
    for i, mid in enumerate(models, 1):
        res = run_one(mid, workdir, reslim=args.reslim)
        results.append(res)
        detail = ", ".join(
            f"{s.model}/{s.type}"
            + (f" MS-{s.model_status}" if s.model_status is not None else " (no status)")
            for s in res.summaries
        )
        print(
            f"[{i:>2}/{len(models)}] {mid:<12} {res.verdict:<14} " f"{res.error or detail}",
            flush=True,
        )

    spurious = [r for r in results if r.is_spurious]
    indeterminate = [r for r in results if r.is_indeterminate]
    mcp_failed = [r for r in results if r.verdict == "MCP-FAILED"]
    solved = [r for r in results if r.verdict == "MCP-SOLVED"]

    print()
    print(f"Checked {len(results)} model(s) recorded model_optimal_presolve + match.")
    print(f"  our MCP solved (MS-1/MS-2)          : {len(solved)}")
    print(f"  our MCP ran but FAILED              : {len(mcp_failed)}")
    print(f"  ONLY an embedded solve reported     : {len(spurious)}")
    print(f"  could not be determined             : {len(indeterminate)}")

    # Every result lands in exactly one bucket, asserted rather than assumed —
    # a verdict added later must not fall through the reporting unnoticed.
    assert len(solved) + len(mcp_failed) + len(spurious) + len(indeterminate) == len(results)

    if spurious:
        print()
        print("SPURIOUS MATCHES — the recorded objective is the embedded solve's own value:")
        for r in spurious:
            print(f"  {r.model_id}")
    if mcp_failed:
        print()
        print("MCP RAN AND FAILED — attributed, but not a usable answer:")
        for r in mcp_failed:
            statuses = ", ".join(f"MS-{s.model_status}" for s in r.mcp_summaries)
            print(f"  {r.model_id} ({statuses})")
    if indeterminate:
        print()
        print("INDETERMINATE — the check concluded nothing for these:")
        for r in indeterminate:
            print(f"  {r.model_id} [{r.verdict}] {r.error or ''}".rstrip())

    if args.json_out:
        report = json.dumps(
            {
                "checked": len(results),
                "spurious": [r.model_id for r in spurious],
                "mcp_failed": [r.model_id for r in mcp_failed],
                "indeterminate": [r.model_id for r in indeterminate],
                "results": [r.as_dict() for r in results],
            },
            indent=2,
        )
        try:
            Path(args.json_out).write_text(report)
        except OSError as exc:
            # This runs AFTER every GAMS solve. Losing hours of work to an
            # unwritable path would be absurd — dump to stderr, then exit 2.
            print(f"ERROR: cannot write report to {args.json_out}: {exc}", file=sys.stderr)
            print("--- report follows on stderr so the run is not lost ---", file=sys.stderr)
            print(report, file=sys.stderr)
            return 2

    # Exit non-zero when a determination FAILED — including a listing with no
    # recognised solve at all, which concludes nothing and must not exit 0.
    # A spurious match is a FINDING to report, not this script's failure.
    return 1 if indeterminate else 0


if __name__ == "__main__":
    raise SystemExit(main())

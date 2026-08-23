"""A `MODEL STATUS` belongs to the solve above it, not to the listing.

Sprint 38 Day 10. A ``--nlp-presolve`` emit runs the original model inside the
generated file before solving the MCP, so a **successful** run's listing holds
two or more solve summaries. **When the MCP aborts it holds only one** — the
embedded source's — because an MCP that dies before its solve emits no summary
at all. The listing is then indistinguishable, to a global search, from a
single-solve run; anything that greps for ``MODEL STATUS`` reports the embedded
model's status as the MCP's.

`weapons` is the real instance: its listing has exactly ONE summary (the NLP's,
MS-2 @ 1735.5696), the MCP aborted with ``EXECERROR = 1``, and the DB recorded
``model_optimal_presolve`` + match at 1735.5696.

**`_WEAPONS` and `_TWOCGE` are verbatim excerpts of real GAMS 54.2.1 listings**,
not hand-written approximations of what a listing looks like — a parser test
built only from idealised fixtures proves that the parser matches the author's
mental model of the format, and nothing more. They carry the two cases the
audit turns on, so they are the ones that must be real.

The smaller fixtures further down (`infeasible`, `truncated`, `foreign`,
`lp_source`, the column-0 header) are **synthetic**: each isolates one edge case
that does not occur in the current corpus, so there is no real listing to quote.
They are labelled as such at each use.
"""

from pathlib import Path

import pytest

from scripts.sprint_audit.check_mcp_solve_attribution import (
    Attribution,
    parse_solve_summaries,
)

#: Verbatim from `weapons`'s listing — the ONLY solve summary it contains,
#: followed by the MCP abort that produced no summary of its own.
_WEAPONS = """
               S O L V E      S U M M A R Y

     MODEL   war                 OBJECTIVE  tetd
     TYPE    NLP                 DIRECTION  MAXIMIZE
     SOLVER  CONOPT              FROM LINE  138

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      2 Locally Optimal
**** OBJECTIVE VALUE             1735.5696

 RESOURCE USAGE, LIMIT          0.071       300.000
 ITERATION COUNT, LIMIT        11    2147483647

**** MCP pair comp_minw.lam_minw has unmatched equation
**** SOLVE from line 238 ABORTED, EXECERROR = 1
**** USER ERROR(S) ENCOUNTERED
"""

#: Verbatim from `twocge`'s listing — the raw model solves twice, then the MCP.
_TWOCGE = """
               S O L V E      S U M M A R Y

     MODEL   twocge              OBJECTIVE  SW
     TYPE    NLP                 DIRECTION  MAXIMIZE
     SOLVER  CONOPT              FROM LINE  634

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      2 Locally Optimal
**** OBJECTIVE VALUE               55.5085


               S O L V E      S U M M A R Y

     MODEL   twocge              OBJECTIVE  SW
     TYPE    NLP                 DIRECTION  MAXIMIZE
     SOLVER  CONOPT              FROM LINE  641

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      2 Locally Optimal
**** OBJECTIVE VALUE               56.7778


               S O L V E      S U M M A R Y

     MODEL   mcp_model
     TYPE    MCP
     SOLVER  PATH                FROM LINE  1124

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal
"""


@pytest.mark.unit
def test_weapons_listing_is_EMBEDDED_ONLY_despite_holding_a_model_status():
    """The discriminating case: a status is present, but not the MCP's.

    Any check that greps the listing for ``MODEL STATUS`` calls this MCP-SOLVED.
    """
    summaries = parse_solve_summaries(_WEAPONS)
    attribution = Attribution("weapons", summaries=summaries)

    assert len(summaries) == 1, f"weapons has exactly one solve summary, got {summaries}"
    assert summaries[0].type == "NLP"
    assert summaries[0].model_status == 2, "the status present is the embedded NLP's"

    assert attribution.mcp_summaries == [], "there is no MCP-typed solve at all"
    assert not attribution.mcp_produced_status
    assert attribution.verdict == "EMBEDDED-ONLY"
    assert attribution.is_spurious, "this is the spurious case the audit reports"
    assert not attribution.is_indeterminate, "it is a finding, not a failed determination"


@pytest.mark.unit
def test_a_nonzero_gams_returncode_does_NOT_invalidate_the_finding():
    """weapons exits 3 *because* its MCP aborted — the rc is the symptom.

    Treating a nonzero GAMS exit as an untrustworthy listing would discard the
    only spurious match in the corpus. It is recorded, never acted on.
    """
    attribution = Attribution(
        "weapons", summaries=parse_solve_summaries(_WEAPONS), gams_returncode=3
    )

    assert attribution.gams_returncode == 3
    assert attribution.verdict == "EMBEDDED-ONLY", "the rc must not change the verdict"
    assert attribution.as_dict()["gams_returncode"] == 3, "but it must be reported"


@pytest.mark.unit
def test_an_attributed_but_FAILING_mcp_is_not_MCP_SOLVED():
    """A status proves attribution, not success.

    An MCP that returns MS-4 leaves the warm-started `.l` values in place just as
    an abort does, so counting it as solved would launder a failure into a match.
    """
    # SYNTHETIC — no corpus model currently emits an MCP reporting MS-4, so
    # there is no real listing to quote for this case.
    infeasible = """
               S O L V E      S U M M A R Y

     MODEL   mcp_model
     TYPE    MCP
     SOLVER  PATH                FROM LINE  1124

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      4 Infeasible
"""
    attribution = Attribution("camcge-like", summaries=parse_solve_summaries(infeasible))

    assert attribution.mcp_produced_status, "the status IS ours — attribution succeeded"
    assert not attribution.mcp_succeeded, "...but MS-4 is not a usable answer"
    assert attribution.verdict == "MCP-FAILED"
    assert not attribution.is_spurious, "our MCP did run; nothing was read back from a warm start"


@pytest.mark.unit
def test_twocge_listing_attributes_the_MCP_status_to_the_MCP():
    """Three solves; only the third is ours, and only its status counts."""
    summaries = parse_solve_summaries(_TWOCGE)
    attribution = Attribution("twocge", summaries=summaries)

    assert [s.type for s in summaries] == ["NLP", "NLP", "MCP"]
    assert [s.model for s in summaries] == ["twocge", "twocge", "mcp_model"]

    (mcp,) = attribution.mcp_summaries
    assert mcp.solver == "PATH"
    assert mcp.model_status == 1
    assert attribution.verdict == "MCP-SOLVED"


@pytest.mark.unit
def test_the_LAST_status_in_a_listing_is_not_the_MCPs():
    """Pin the defect this exists to catch, on both fixtures at once.

    `parse_gams_listing` takes the last ``MODEL STATUS`` in the file. On twocge
    that happens to be right; on weapons it silently yields the NLP's MS-2. The
    two fixtures therefore disagree about whether "last" is a safe rule — which
    is precisely why attribution has to be positional.
    """
    weapons_last = parse_solve_summaries(_WEAPONS)[-1]
    twocge_last = parse_solve_summaries(_TWOCGE)[-1]

    assert twocge_last.is_mcp, "on twocge the last solve IS the MCP — the rule looks fine"
    assert not weapons_last.is_mcp, (
        "on weapons the last solve is the embedded NLP, so 'take the last MODEL "
        "STATUS' reports an NLP status as the MCP's"
    )


@pytest.mark.unit
def test_a_summary_without_a_status_does_not_count_as_solved():
    """An MCP summary that reported no status must not read as MCP-SOLVED.

    GAMS emits the header during model generation; a solver that dies before
    reporting leaves the block statusless.
    """
    # SYNTHETIC — a solver dying between the header and its status has not
    # been observed in this corpus.
    truncated = """
               S O L V E      S U M M A R Y

     MODEL   mcp_model
     TYPE    MCP
     SOLVER  PATH                FROM LINE  1124

"""
    attribution = Attribution("truncated", summaries=parse_solve_summaries(truncated))

    assert len(attribution.mcp_summaries) == 1, "the MCP block is present..."
    assert attribution.mcp_summaries[0].model_status is None, "...but reported no status"
    assert not attribution.mcp_produced_status

    # And it must NOT be reported as spurious: no embedded solve reported a
    # status either, so there is nothing a warm start could have read back.
    # Claiming "only the embedded model solved" here would invent a finding.
    assert attribution.verdict == "MCP-NO-STATUS"
    assert not attribution.is_spurious
    assert attribution.is_indeterminate


@pytest.mark.unit
def test_a_raw_models_OWN_mcp_solve_is_not_ours():
    """`TYPE MCP` alone is not enough — two raw sources solve an MCP themselves.

    `cesam.gms` and `spatequ.gms` contain their own `using MCP` solve, and a
    presolve emit `$include`s the raw source. Reading that summary as ours would
    reinstate the very bug this script exists to catch, one level up.
    """
    # SYNTHETIC — modelled on `spatequ`/`cesam`, which do solve their own MCP,
    # but neither is in the presolve+match population, so no real listing exists.
    foreign = """
               S O L V E      S U M M A R Y

     MODEL   spatequ             OBJECTIVE
     TYPE    MCP
     SOLVER  PATH                FROM LINE  95

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal
"""
    attribution = Attribution("spatequ-like", summaries=parse_solve_summaries(foreign))

    (summary,) = attribution.summaries
    assert summary.is_mcp, "it IS an MCP solve..."
    assert not summary.is_emitted_mcp, "...but it is the raw model's, not ours"

    assert attribution.mcp_summaries == [], "so it must not count toward our MCP"
    assert len(attribution.foreign_mcp_summaries) == 1, "and it must be surfaced, not dropped"
    assert not attribution.mcp_produced_status

    # It IS spurious: a status exists for the warm start to read back, and it is
    # not ours. The label is provenance-based, which is why it stays correct even
    # though the other solve is itself an MCP.
    assert attribution.verdict == "EMBEDDED-ONLY"
    assert attribution.is_spurious


@pytest.mark.unit
def test_the_spurious_label_does_not_assert_the_solve_KIND():
    """The population is not all NLP — `marco`/`paperco`/`tforss` are LPs.

    A verdict literally named "NLP-ONLY" would misreport the solve kind on the
    LP, QCP and DNLP sources in the sweep, so the label is provenance-based and
    the *type* is carried on the summary instead.
    """
    # SYNTHETIC — shaped after `marco`'s embedded LP solve.
    lp_source = """
               S O L V E      S U M M A R Y

     MODEL   oil                 OBJECTIVE  profit
     TYPE    LP                  DIRECTION  MAXIMIZE
     SOLVER  CPLEX               FROM LINE  120

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal
"""
    attribution = Attribution("marco-like", summaries=parse_solve_summaries(lp_source))

    assert attribution.verdict == "EMBEDDED-ONLY", "provenance, not model type"
    assert attribution.embedded_summaries[0].type == "LP", "the kind is preserved, not asserted"
    assert "NLP" not in attribution.verdict


@pytest.mark.unit
def test_empty_listing_is_NO_SOLVE_and_counts_as_indeterminate():
    """No solve at all is distinct from 'the embedded model solved, ours did not'.

    It must also be *indeterminate*: a listing with nothing in it concludes
    nothing, so it cannot silently pass through the totals and exit 0.
    """
    attribution = Attribution("empty", summaries=parse_solve_summaries("no solves here"))

    assert attribution.summaries == []
    assert attribution.verdict == "NO-SOLVE"
    assert not attribution.is_spurious
    assert attribution.is_indeterminate, "must be counted as a failed determination"


@pytest.mark.unit
def test_a_bad_SOLVER_status_is_not_a_solved_MCP():
    """MODEL STATUS alone is not the gate — SOLVER STATUS must be 1 too.

    Mirrors `scripts/gamslib/test_solve.py`'s own solve gate. A solver that hits
    a resource limit can report a stale-but-plausible MODEL STATUS beside
    SOLVER STATUS 3, and that is not a solved model.
    """
    # SYNTHETIC — every MCP in the current sweep reports SOLVER STATUS 1, so
    # this combination has no real listing to quote.
    resource_interrupt = """
               S O L V E      S U M M A R Y

     MODEL   mcp_model
     TYPE    MCP
     SOLVER  PATH                FROM LINE  1124

**** SOLVER STATUS     3 Resource Interrupt
**** MODEL STATUS      1 Optimal
"""
    attribution = Attribution("limit-hit", summaries=parse_solve_summaries(resource_interrupt))

    assert attribution.mcp_produced_status, "the status is ours — attribution succeeded"
    assert not attribution.mcp_succeeded, "SOLVER STATUS 3 disqualifies it despite MS-1"
    assert attribution.verdict == "MCP-FAILED"


@pytest.mark.unit
def test_a_column_zero_summary_header_still_parses():
    """Attribution must not depend on indentation.

    `scripts/gamslib/test_solve.py` already accepts an unindented header, and
    `tests/gamslib/test_test_solve.py` exercises that shape. Requiring leading
    whitespace would parse such a listing as ZERO summaries and report a
    perfectly good run as NO-SOLVE.
    """
    # SYNTHETIC — real GAMS 54.2.1 listings indent, but the repo's own fixtures
    # do not, and a formatting detail must not decide attribution.
    unindented = """
S O L V E      S U M M A R Y

MODEL   mcp_model
TYPE    MCP
SOLVER  PATH                FROM LINE  1124

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal
"""
    attribution = Attribution("flush-left", summaries=parse_solve_summaries(unindented))

    assert len(attribution.summaries) == 1, "the header must parse without indentation"
    assert attribution.verdict == "MCP-SOLVED"


@pytest.mark.unit
@pytest.mark.parametrize(
    "model_id",
    ["../escape", "a/b", "..", ".", "with space", "abs\\path", ""],
)
def test_unsafe_model_ids_are_rejected(model_id):
    """Model ids become path components, so they are validated before use.

    `run_one` builds both `data/gamslib/raw/<id>.gms` and
    `<workdir>/<id>_mcp_presolve.gms`; a separator or `..` escapes either one.
    """
    from scripts.sprint_audit.check_mcp_solve_attribution import _is_safe_model_id

    assert not _is_safe_model_id(model_id), f"{model_id!r} must be rejected"


@pytest.mark.unit
def test_ordinary_model_ids_are_accepted():
    """The guard must not reject the corpus it exists to audit."""
    from scripts.sprint_audit.check_mcp_solve_attribution import _is_safe_model_id

    for model_id in ("weapons", "twocge", "ps2_f_s", "ps10_s_mn", "mathopt1", "cclinpts"):
        assert _is_safe_model_id(model_id), f"{model_id!r} is a real corpus model"


@pytest.mark.unit
def test_indented_status_lines_still_attach_to_their_summary():
    """The status patterns must tolerate indentation like the header ones do.

    An otherwise valid listing with indented ``****`` lines would otherwise yield
    a *statusless* summary — reported as MCP-NO-STATUS or, worse, as spurious.
    """
    # SYNTHETIC — GAMS 54.2.1 writes these flush left; this pins that the parser
    # does not depend on that, consistently with the header patterns.
    indented = """
    S O L V E      S U M M A R Y

    MODEL   mcp_model
    TYPE    MCP
    SOLVER  PATH                FROM LINE  1124

    **** SOLVER STATUS     1 Normal Completion
    **** MODEL STATUS      1 Optimal
"""
    attribution = Attribution("indented", summaries=parse_solve_summaries(indented))

    (summary,) = attribution.summaries
    assert summary.solver_status == 1, "indented SOLVER STATUS must be picked up"
    assert summary.model_status == 1, "indented MODEL STATUS must be picked up"
    assert attribution.verdict == "MCP-SOLVED"


@pytest.mark.unit
@pytest.mark.parametrize("model_id", ["weapons\n", "weapons\r\n", "\nweapons", "weapons\t"])
def test_model_ids_with_trailing_whitespace_are_rejected(model_id):
    """`$` matches before a final newline, so the guard uses `\\Z` + `fullmatch`.

    `"weapons\\n"` passing a check whose whole purpose is to reject whitespace
    would be a silent hole in a path guard.
    """
    from scripts.sprint_audit.check_mcp_solve_attribution import _is_safe_model_id

    assert not _is_safe_model_id(model_id), f"{model_id!r} must be rejected"


# ---------------------------------------------------------------------------
# `run_one`'s subprocess/filesystem path.
#
# The parser tests above never touch it, so its timeout, OSError and
# output-path handling could regress silently. These drive it with mocked
# subprocesses: no GAMS, no translation, no corpus.
# ---------------------------------------------------------------------------


@pytest.fixture
def _raw_source(monkeypatch, tmp_path):
    """Point PROJECT_ROOT at a tmp tree holding one raw model."""
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    raw_dir = tmp_path / "data" / "gamslib" / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "demo.gms").write_text("* a stand-in for a real GAMS model\n")
    monkeypatch.setattr(mod, "PROJECT_ROOT", tmp_path)
    return tmp_path


def _completed(returncode=0, stdout="", stderr=""):
    import subprocess

    return subprocess.CompletedProcess(
        args=["x"], returncode=returncode, stdout=stdout, stderr=stderr
    )


@pytest.mark.unit
def test_run_one_happy_path_parses_the_listing_it_just_wrote(_raw_source, tmp_path, monkeypatch):
    """A successful emit + GAMS run is attributed from the fresh listing."""
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    workdir = tmp_path / "wd"
    workdir.mkdir()
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if "src.cli" in cmd:
            (workdir / "demo_mcp_presolve.gms").write_text("* emitted\n")
        else:
            (workdir / "demo.lst").write_text(_TWOCGE)
        return _completed()

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    monkeypatch.setattr(mod, "find_gams", lambda: "/fake/gams")

    result = mod.run_one("demo", workdir)

    assert result.error is None, result.error
    assert result.verdict == "MCP-SOLVED"
    assert result.gams_returncode == 0
    assert len(calls) == 2, "one translation, one GAMS run"


@pytest.mark.unit
def test_run_one_reports_a_stale_listing_is_removed_before_gams(_raw_source, tmp_path, monkeypatch):
    """A previous run's listing must not answer for this one.

    Here GAMS "fails" without writing, so if the stale file survived it would be
    parsed as this run's result and report a solved MCP.
    """
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    workdir = tmp_path / "wd"
    workdir.mkdir()
    (workdir / "demo.lst").write_text(_TWOCGE)  # a stale MCP-SOLVED listing

    def fake_run(cmd, **kwargs):
        if "src.cli" in cmd:
            (workdir / "demo_mcp_presolve.gms").write_text("* emitted\n")
            return _completed()
        return _completed(returncode=3, stderr="*** licensing failure")

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    monkeypatch.setattr(mod, "find_gams", lambda: "/fake/gams")

    result = mod.run_one("demo", workdir)

    assert result.verdict == "ERROR", "no listing means nothing can be concluded"
    assert "no listing produced" in (result.error or "")
    assert "licensing failure" in (result.error or ""), "GAMS output must reach the error"


@pytest.mark.unit
def test_run_one_emit_timeout_is_a_structured_result_not_an_exception(
    _raw_source, tmp_path, monkeypatch
):
    """A hung translation must not abort the sweep before it can report."""
    import subprocess

    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    def fake_run(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=600)

    monkeypatch.setattr(mod.subprocess, "run", fake_run)

    result = mod.run_one("demo", tmp_path)

    assert result.verdict == "ERROR"
    assert "emit timeout" in (result.error or "")


@pytest.mark.unit
def test_run_one_gams_launch_OSError_is_a_structured_result(_raw_source, tmp_path, monkeypatch):
    """A vanished or non-executable GAMS binary is one model's problem."""
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    workdir = tmp_path / "wd"
    workdir.mkdir()

    def fake_run(cmd, **kwargs):
        if "src.cli" in cmd:
            (workdir / "demo_mcp_presolve.gms").write_text("* emitted\n")
            return _completed()
        raise OSError(13, "Permission denied")

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    monkeypatch.setattr(mod, "find_gams", lambda: "/fake/gams")

    result = mod.run_one("demo", workdir)

    assert result.verdict == "ERROR"
    assert "could not be launched" in (result.error or "")


@pytest.mark.unit
def test_run_one_gams_timeout_reports_the_WALL_CLOCK_limit(_raw_source, tmp_path, monkeypatch):
    """The message must name the limit that actually fired, not GAMS's reslim.

    They differ by the 120 s launch allowance; quoting the smaller one makes a
    harness timeout look like a solver limit.
    """
    import subprocess

    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    workdir = tmp_path / "wd"
    workdir.mkdir()

    def fake_run(cmd, **kwargs):
        if "src.cli" in cmd:
            (workdir / "demo_mcp_presolve.gms").write_text("* emitted\n")
            return _completed()
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=420)

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    monkeypatch.setattr(mod, "find_gams", lambda: "/fake/gams")

    result = mod.run_one("demo", workdir, reslim=300)

    assert "420s" in (result.error or ""), f"must name the real limit, got {result.error!r}"
    assert "reslim=300" in (result.error or ""), "and still report GAMS's own reslim"


@pytest.mark.unit
def test_run_one_emit_failure_carries_the_translation_output(_raw_source, tmp_path, monkeypatch):
    """`emit failed (rc=1)` alone is not actionable."""
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    def fake_run(cmd, **kwargs):
        return _completed(returncode=1, stderr="ParseError: unexpected token at line 12")

    monkeypatch.setattr(mod.subprocess, "run", fake_run)

    result = mod.run_one("demo", tmp_path)

    assert result.verdict == "ERROR"
    assert "ParseError" in (result.error or ""), "the translator's own message must survive"


@pytest.mark.unit
def test_run_one_distinguishes_silent_emit_from_failed_emit(_raw_source, tmp_path, monkeypatch):
    """rc=0 but no output file points at the path, not the model."""
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    monkeypatch.setattr(mod.subprocess, "run", lambda cmd, **kw: _completed())

    result = mod.run_one("demo", tmp_path)

    assert result.verdict == "ERROR"
    assert "wrote no file" in (result.error or "")


@pytest.mark.unit
def test_run_one_names_the_provisioning_command_when_the_corpus_is_absent(tmp_path, monkeypatch):
    """`data/gamslib/raw/*.gms` is gitignored, so this is the common first failure."""
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    monkeypatch.setattr(mod, "PROJECT_ROOT", tmp_path)

    result = mod.run_one("demo", tmp_path)

    assert result.verdict == "ERROR"
    assert "download_gamslib_raw.sh" in (result.error or ""), "tell the caller how to fix it"


@pytest.mark.unit
def test_run_one_rejects_an_unsafe_id_without_touching_the_filesystem(tmp_path, monkeypatch):
    """Defense in depth — `run_one` is importable and callable on its own."""
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    def explode(*a, **k):  # pragma: no cover - must never run
        raise AssertionError("no subprocess may run for an unsafe id")

    monkeypatch.setattr(mod.subprocess, "run", explode)

    result = mod.run_one("../escape", tmp_path)

    assert result.verdict == "ERROR"
    assert "unsafe model id" in (result.error or "")


# ---------------------------------------------------------------------------
# `main` — the CLI selection, validation and exit-code branches.
#
# Nothing above calls it, so the selection logic and every exit path could
# regress while the unit tests stayed green.
# ---------------------------------------------------------------------------


def _write_db(tmp_path, rows):
    """A **schema-valid** results DB.

    `schema.json` requires the top-level `schema_version` as well as `models`;
    a fixture missing it is not the repository's DB contract and cannot
    exercise validation of it.
    """
    import json

    db = tmp_path / "db.json"
    db.write_text(json.dumps({"schema_version": "2.2.1", "models": rows}))
    return db


def _row(model_id, outcome="model_optimal_presolve", comparison="match"):
    """A schema-valid row.

    ``mcp_solve.status`` is REQUIRED by ``data/gamslib/schema.json`` even though
    the selection predicate never reads it, so the fixture must carry it — a
    fixture that omits a required field cannot exercise the validation.
    """
    return {
        "model_id": model_id,
        # `model_name` and `gamslib_type` are required per entry.
        "model_name": f"{model_id} test model",
        "gamslib_type": "NLP",
        "mcp_solve": {"status": "success", "outcome_category": outcome},
        "solution_comparison": {"comparison_status": comparison},
    }


@pytest.mark.unit
def test_main_default_selection_reads_the_db_cohort(tmp_path, monkeypatch, capsys):
    """No --models ⇒ every presolve+match row, and the heading says so."""
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    db = _write_db(tmp_path, [_row("alpha"), _row("beta"), _row("gamma", comparison="mismatch")])
    monkeypatch.setattr(mod, "DB_PATH", db)
    monkeypatch.setattr(mod, "find_gams", lambda: "/fake/gams")
    seen = []
    monkeypatch.setattr(
        mod,
        "run_one",
        lambda mid, wd, **kw: seen.append(mid)
        or Attribution(mid, summaries=parse_solve_summaries(_TWOCGE)),
    )

    rc = mod.main(["--workdir", str(tmp_path / "wd")])

    assert rc == 0
    assert seen == ["alpha", "beta"], "the mismatch row is not in the cohort"
    assert "recorded model_optimal_presolve + match" in capsys.readouterr().out


@pytest.mark.unit
def test_main_explicit_selection_does_not_claim_the_db_population(tmp_path, monkeypatch, capsys):
    """`--models camcge` audits what was named — not the presolve+match cohort."""
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    monkeypatch.setattr(mod, "find_gams", lambda: "/fake/gams")
    monkeypatch.setattr(
        mod,
        "run_one",
        lambda mid, wd, **kw: Attribution(mid, summaries=parse_solve_summaries(_TWOCGE)),
    )

    rc = mod.main(["--models", "anything", "--workdir", str(tmp_path / "wd")])
    out = capsys.readouterr().out

    assert rc == 0
    assert "named explicitly via --models" in out
    assert "recorded model_optimal_presolve + match" not in out, "that claim would be false here"


@pytest.mark.unit
def test_main_empty_explicit_selection_does_not_fall_back_to_the_cohort(
    tmp_path, monkeypatch, capsys
):
    """`--models ""` is an empty selection, not an omitted flag."""
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    db = _write_db(tmp_path, [_row("alpha")])
    monkeypatch.setattr(mod, "DB_PATH", db)

    def explode(*a, **k):  # pragma: no cover - must never run
        raise AssertionError("an empty --models must not audit the DB cohort")

    monkeypatch.setattr(mod, "run_one", explode)

    rc = mod.main(["--models", "", "--workdir", str(tmp_path / "wd")])

    assert rc == 2
    assert "selection is empty" in capsys.readouterr().err


@pytest.mark.unit
def test_main_allow_empty_says_it_certifies_nothing(tmp_path, monkeypatch, capsys):
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    monkeypatch.setattr(mod, "find_gams", lambda: "/fake/gams")

    rc = mod.main(["--models", "", "--allow-empty", "--workdir", str(tmp_path / "wd")])

    assert rc == 0
    assert "CERTIFIES NOTHING" in capsys.readouterr().err


@pytest.mark.unit
def test_main_exits_1_when_an_mcp_ran_and_FAILED(tmp_path, monkeypatch):
    """A disproven match must not look like a passing audit."""
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    failed = """
               S O L V E      S U M M A R Y

     MODEL   mcp_model
     TYPE    MCP
     SOLVER  PATH                FROM LINE  1

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      4 Infeasible
"""
    monkeypatch.setattr(mod, "find_gams", lambda: "/fake/gams")
    monkeypatch.setattr(
        mod,
        "run_one",
        lambda mid, wd, **kw: Attribution(mid, summaries=parse_solve_summaries(failed)),
    )

    rc = mod.main(["--models", "x", "--workdir", str(tmp_path / "wd")])

    assert rc == 1, "MCP-FAILED must be a nonzero exit"


@pytest.mark.unit
def test_main_exits_0_on_a_spurious_finding(tmp_path, monkeypatch):
    """The finding the audit exists to produce is not a tool failure."""
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    monkeypatch.setattr(mod, "find_gams", lambda: "/fake/gams")
    monkeypatch.setattr(
        mod,
        "run_one",
        lambda mid, wd, **kw: Attribution(mid, summaries=parse_solve_summaries(_WEAPONS)),
    )

    rc = mod.main(["--models", "weapons", "--workdir", str(tmp_path / "wd")])

    assert rc == 0


@pytest.mark.unit
def test_main_fails_fast_when_gams_is_missing(tmp_path, monkeypatch, capsys):
    """No translation may run when the dependency is absent."""
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    monkeypatch.setattr(mod, "find_gams", lambda: None)

    def explode(*a, **k):  # pragma: no cover - must never run
        raise AssertionError("no model may be processed without GAMS")

    monkeypatch.setattr(mod, "run_one", explode)

    rc = mod.main(["--models", "x", "--workdir", str(tmp_path / "wd")])

    assert rc == 2
    assert "gams executable not found" in capsys.readouterr().err


@pytest.mark.unit
def test_main_rejects_a_negative_reslim(tmp_path, capsys):
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    assert mod.main(["--models", "x", "--reslim", "-5", "--workdir", str(tmp_path)]) == 2
    assert "--reslim must be >= 0" in capsys.readouterr().err


@pytest.mark.unit
def test_main_gives_each_invocation_its_own_scratch_dir(tmp_path, monkeypatch, capsys):
    """Two runs sharing --workdir must not share artifact paths.

    Deterministic `<model>.gms` / `<model>.lst` names mean concurrent runs would
    unlink and overwrite each other's files, and could attribute the OTHER
    invocation's listing — this script's own bug, one level up.
    """
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    monkeypatch.setattr(mod, "find_gams", lambda: "/fake/gams")
    dirs = []
    monkeypatch.setattr(
        mod,
        "run_one",
        lambda mid, wd, **kw: dirs.append(wd)
        or Attribution(mid, summaries=parse_solve_summaries(_TWOCGE)),
    )

    shared = str(tmp_path / "shared")
    mod.main(["--models", "x", "--workdir", shared])
    mod.main(["--models", "x", "--workdir", shared])

    assert len(dirs) == 2
    assert dirs[0] != dirs[1], f"both invocations used {dirs[0]}"
    assert all(d.name.startswith("run-") for d in dirs)
    assert "artifacts:" in capsys.readouterr().out, "the run dir must be discoverable"


@pytest.mark.unit
def test_main_reports_a_malformed_db_rather_than_raising(tmp_path, monkeypatch, capsys):
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    row = _row("ok")
    row["mcp_solve"] = []
    db = _write_db(tmp_path, [row])
    monkeypatch.setattr(mod, "DB_PATH", db)

    rc = mod.main(["--workdir", str(tmp_path / "wd")])

    assert rc == 2
    err = capsys.readouterr().err
    assert "malformed" in err and "list" in err, err


@pytest.mark.unit
def test_db_validation_covers_rows_outside_the_selection(tmp_path):
    """A bad id on a NON-matching row must still be an error.

    Validating only inside the predicate let a corrupted DB quietly drop a model
    from the cohort while the function advertised per-entry validation.
    """
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    db = _write_db(tmp_path, [_row("good"), _row("../evil", comparison="mismatch")])

    with pytest.raises(mod.InputError, match="unsafe model_id"):
        mod.presolve_match_models(db)


@pytest.mark.unit
def test_find_gams_resolves_through_which_not_exists(monkeypatch):
    """A candidate must be an EXECUTABLE FILE, not merely a path that exists.

    `Path.exists()` accepts a directory or a non-executable, and returning one
    defeats the fail-fast preflight: `main` would believe GAMS is available and
    run every (sometimes multi-minute) translation before each model hit the
    same OSError.
    """
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    # `shutil.which` is what performs the executability check. Stub it away and
    # nothing may resolve — even though the macOS candidate path exists on this
    # machine, which is precisely what an `exists()`-based lookup would return.
    monkeypatch.setattr(mod.shutil, "which", lambda _p: None)

    assert mod.find_gams() is None


@pytest.mark.unit
def test_run_one_clears_a_stale_EMIT_before_translating(tmp_path, monkeypatch):
    """The emit target is cleared for the same reason the listing is.

    If a later `src.cli` returns 0 without recreating its output, a surviving
    file makes `emitted.exists()` succeed and GAMS runs the PREVIOUS model's
    translation — the audit then attributes an older model's listing.
    """
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    raw_dir = tmp_path / "data" / "gamslib" / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "demo.gms").write_text("* stand-in\n")
    monkeypatch.setattr(mod, "PROJECT_ROOT", tmp_path)

    workdir = tmp_path / "wd"
    workdir.mkdir()
    stale = workdir / "demo_mcp_presolve.gms"
    stale.write_text("* a PREVIOUS model's translation\n")

    # `src.cli` "succeeds" but writes nothing — the exact regression shape.
    monkeypatch.setattr(mod.subprocess, "run", lambda cmd, **kw: _completed())
    monkeypatch.setattr(mod, "find_gams", lambda: "/fake/gams")

    result = mod.run_one("demo", workdir)

    assert not stale.exists(), "the stale emit must have been removed"
    assert result.verdict == "ERROR"
    assert "wrote no file" in (result.error or ""), (
        "with the stale file cleared, the silent-emit check is meaningful; " f"got {result.error!r}"
    )


@pytest.mark.unit
def test_outcome_allowlist_matches_the_schema():
    """The allow-list must mirror the SCHEMA's field enum, not the producer's union.

    `error_taxonomy.SOLVE_OUTCOME_CATEGORIES` spans several fields: it omits the
    schema-valid `permanent_exclusion` and includes seven `compare_*` values that
    are invalid for `outcome_category`. Mirroring it was wrong in both
    directions.
    """
    import json

    from scripts.sprint_audit.check_mcp_solve_attribution import (
        _SOLVE_OUTCOME_CATEGORIES,
        PROJECT_ROOT,
    )

    schema = json.loads((PROJECT_ROOT / "data" / "gamslib" / "schema.json").read_text())
    declared = schema["definitions"]["solve_outcome_category"]["enum"]

    assert _SOLVE_OUTCOME_CATEGORIES == frozenset(declared), (
        "the outcome allow-list has drifted from "
        "data/gamslib/schema.json definitions.solve_outcome_category"
    )


@pytest.mark.unit
def test_permanent_exclusion_is_accepted_and_compare_values_are_not():
    """Both directions of the round-7 bug, pinned explicitly."""
    from scripts.sprint_audit.check_mcp_solve_attribution import _outcome_is_known

    assert _outcome_is_known("permanent_exclusion"), "schema-valid; rejecting it aborts the audit"
    assert not _outcome_is_known("compare_objective_match"), "not valid for this field"


@pytest.mark.unit
@pytest.mark.parametrize(
    "field,value",
    [
        ("outcome", "model_optimal_presolvee"),
        ("outcome", "not_a_category"),
        ("status", "matc"),
        ("status", "MATCH"),
    ],
)
def test_a_typo_in_a_db_enum_is_an_error_not_a_silent_drop(tmp_path, field, value):
    """Comparing only against the wanted pair hides typos.

    `model_optimal_presolvee` would simply not equal the target, the row would
    vanish from the cohort, and the audit would report a confident result over a
    quietly incomplete population.
    """
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    row = _row("typo")
    if field == "outcome":
        row["mcp_solve"]["outcome_category"] = value
    else:
        row["solution_comparison"]["comparison_status"] = value
    db = _write_db(tmp_path, [row])

    with pytest.raises(mod.InputError, match="unknown"):
        mod.presolve_match_models(db)


@pytest.mark.unit
def test_model_optimal_presolve_is_a_schema_value_not_a_suffix_trick(tmp_path):
    """The schema lists `model_optimal_presolve` itself, so no stripping is needed.

    An earlier revision accepted an arbitrary `<base>_presolve`, which admitted
    values the DB contract does not permit.
    """
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    assert "model_optimal_presolve" in mod._SOLVE_OUTCOME_CATEGORIES
    assert mod.presolve_match_models(_write_db(tmp_path, [_row("ok")])) == ["ok"]

    with pytest.raises(mod.InputError, match="unknown"):
        mod.presolve_match_models(
            _write_db(tmp_path, [_row("x", outcome="model_infeasible_presolve")])
        )


@pytest.mark.unit
def test_embedded_status_comes_from_the_LAST_source_solve():
    """An early success followed by a statusless final solve is INDETERMINATE.

    The warm-start value is set by the solve immediately before our MCP. With
    `any()`, this listing would be reported as a spurious match — a finding
    invented out of a run that established nothing.
    """
    # SYNTHETIC — shaped after `harker`/`mathopt4`, which run several source
    # solves before the MCP.
    early_then_statusless = """
               S O L V E      S U M M A R Y

     MODEL   src                 OBJECTIVE  z
     TYPE    NLP                 DIRECTION  MINIMIZE
     SOLVER  CONOPT              FROM LINE  10

**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      2 Locally Optimal


               S O L V E      S U M M A R Y

     MODEL   src                 OBJECTIVE  z
     TYPE    NLP                 DIRECTION  MINIMIZE
     SOLVER  CONOPT              FROM LINE  20

"""
    attribution = Attribution(
        "late-failure", summaries=parse_solve_summaries(early_then_statusless)
    )

    assert len(attribution.embedded_summaries) == 2
    assert attribution.embedded_summaries[0].model_status == 2, "an EARLIER solve did report"
    assert attribution.embedded_summaries[-1].model_status is None, "the LAST one did not"

    assert not attribution.embedded_produced_status, "the last source solve is what counts"
    assert attribution.verdict == "NO-SOLVE"
    assert not attribution.is_spurious, "reporting a spurious match here would invent a finding"
    assert attribution.is_indeterminate


@pytest.mark.unit
def test_explicit_selection_does_not_call_a_result_a_spurious_MATCH(tmp_path, monkeypatch, capsys):
    """`--models` audits arbitrary models, which were never claimed to match.

    The attribution verdict is unchanged; only the "spurious match" framing is
    withheld, because there is no recorded match for it to contradict.
    """
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    monkeypatch.setattr(mod, "find_gams", lambda: "/fake/gams")
    monkeypatch.setattr(
        mod,
        "run_one",
        lambda mid, wd, **kw: Attribution(mid, summaries=parse_solve_summaries(_WEAPONS)),
    )
    out_json = tmp_path / "r.json"

    rc = mod.main(
        ["--models", "anything", "--workdir", str(tmp_path / "wd"), "--json", str(out_json)]
    )
    out = capsys.readouterr().out

    assert rc == 0
    assert "EMBEDDED-ONLY — our MCP produced no status of its own" in out
    assert "SPURIOUS MATCHES" not in out, "no recorded match exists to be spurious"

    import json as _json

    record = _json.loads(out_json.read_text())
    assert record["selection"] == "explicit"
    assert record["embedded_only"] == ["anything"], "the verdict is still reported"
    assert record["spurious"] == [], "but not as a spurious match"


@pytest.mark.unit
def test_db_cohort_selection_DOES_call_it_a_spurious_match(tmp_path, monkeypatch, capsys):
    """The counterpart: for the recorded cohort the framing is correct."""
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    monkeypatch.setattr(mod, "DB_PATH", _write_db(tmp_path, [_row("weapons")]))
    monkeypatch.setattr(mod, "find_gams", lambda: "/fake/gams")
    monkeypatch.setattr(
        mod,
        "run_one",
        lambda mid, wd, **kw: Attribution(mid, summaries=parse_solve_summaries(_WEAPONS)),
    )

    rc = mod.main(["--workdir", str(tmp_path / "wd")])
    out = capsys.readouterr().out

    assert rc == 0
    assert "SPURIOUS MATCHES" in out


@pytest.mark.unit
def test_main_rejects_an_empty_workdir(tmp_path, capsys):
    """`--workdir ""` must not be read as omitted."""
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    assert mod.main(["--models", "x", "--workdir", ""]) == 2
    assert "empty path" in capsys.readouterr().err


@pytest.mark.unit
@pytest.mark.parametrize("kind", ["directory", "missing-parent"])
def test_main_preflights_the_json_destination_before_the_sweep(tmp_path, monkeypatch, capsys, kind):
    """A bad --json path must fail before hours of solves, not after."""
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    monkeypatch.setattr(mod, "find_gams", lambda: "/fake/gams")

    def explode(*a, **k):  # pragma: no cover - must never run
        raise AssertionError("the sweep must not start with an unusable --json path")

    monkeypatch.setattr(mod, "run_one", explode)

    target = str(tmp_path) if kind == "directory" else str(tmp_path / "nope" / "r.json")
    rc = mod.main(["--models", "x", "--workdir", str(tmp_path / "wd"), "--json", target])

    assert rc == 2
    assert "--json" in capsys.readouterr().err


@pytest.mark.unit
def test_find_gams_returns_an_absolute_path(monkeypatch):
    """A relative `PATH` entry would validate here and fail under cwd=PROJECT_ROOT."""
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    monkeypatch.setattr(mod.shutil, "which", lambda p: "relative/gams" if p == "gams" else None)

    found = mod.find_gams()

    assert found is not None
    assert Path(found).is_absolute(), f"expected an absolute path, got {found!r}"


@pytest.mark.unit
def test_comparison_status_allowlist_matches_the_schema():
    """The allow-list must come from schema.json, not from today's DB contents.

    An earlier revision omitted `error` because no current row uses it — which
    would have rejected a perfectly valid row as an unknown enum. This test is
    the guard against deriving an allow-list from observed data again.
    """
    import json

    from scripts.sprint_audit.check_mcp_solve_attribution import (
        _COMPARISON_STATUSES,
        PROJECT_ROOT,
    )

    schema = json.loads((PROJECT_ROOT / "data" / "gamslib" / "schema.json").read_text())
    declared = schema["definitions"]["solution_comparison_result"]["properties"][
        "comparison_status"
    ]["enum"]

    assert _COMPARISON_STATUSES == frozenset(
        declared
    ), "the comparison_status allow-list has drifted from data/gamslib/schema.json"


@pytest.mark.unit
def test_mcp_solve_status_allowlist_matches_the_schema():
    import json

    from scripts.sprint_audit.check_mcp_solve_attribution import (
        _MCP_SOLVE_STATUSES,
        PROJECT_ROOT,
    )

    schema = json.loads((PROJECT_ROOT / "data" / "gamslib" / "schema.json").read_text())
    declared = schema["definitions"]["mcp_solve_result"]["properties"]["status"]["enum"]

    assert _MCP_SOLVE_STATUSES == frozenset(declared)


@pytest.mark.unit
def test_comparison_status_error_is_accepted(tmp_path):
    """`error` is declared valid, so a row using it must not be rejected."""
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    row = _row("errored", comparison="error")
    db = _write_db(tmp_path, [_row("ok"), row])

    assert mod.presolve_match_models(db) == ["ok"], "the errored row is excluded, not rejected"


@pytest.mark.unit
def test_a_row_missing_the_required_mcp_solve_status_is_rejected(tmp_path):
    """`status` is required by the schema even though our predicate never reads it.

    Validating only the fields we consume is how an incomplete cohort goes
    unnoticed.
    """
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    row = _row("bad")
    del row["mcp_solve"]["status"]
    db = _write_db(tmp_path, [row])

    with pytest.raises(mod.InputError, match="mcp_solve.status"):
        mod.presolve_match_models(db)


@pytest.mark.unit
def test_a_solution_comparison_without_its_required_status_is_rejected(tmp_path):
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    row = _row("bad")
    row["solution_comparison"] = {}
    db = _write_db(tmp_path, [row])

    with pytest.raises(mod.InputError, match="comparison_status"):
        mod.presolve_match_models(db)


@pytest.mark.unit
def test_main_rejects_an_empty_json_path(tmp_path, capsys):
    """`--json ""` must not read as an omitted flag.

    Silently writing no report and exiting 0 is inconsistent with the explicit
    handling already given to `--models` and `--workdir`.
    """
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    assert mod.main(["--models", "x", "--workdir", str(tmp_path / "wd"), "--json", ""]) == 2
    assert "--json was given an empty path" in capsys.readouterr().err


@pytest.mark.unit
def test_the_failed_list_shows_the_solver_status_too(tmp_path, monkeypatch, capsys):
    """A SOLVER STATUS 3 / MODEL STATUS 1 run must not print a bare "(MS-1)".

    The success gate requires solver_status == 1, so without it the reader sees
    a failure labelled with an apparently successful model status and no reason.
    """
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    resource_interrupt = """
               S O L V E      S U M M A R Y

     MODEL   mcp_model
     TYPE    MCP
     SOLVER  PATH                FROM LINE  1

**** SOLVER STATUS     3 Resource Interrupt
**** MODEL STATUS      1 Optimal
"""
    monkeypatch.setattr(mod, "find_gams", lambda: "/fake/gams")
    monkeypatch.setattr(
        mod,
        "run_one",
        lambda mid, wd, **kw: Attribution(mid, summaries=parse_solve_summaries(resource_interrupt)),
    )

    mod.main(["--models", "x", "--workdir", str(tmp_path / "wd")])
    out = capsys.readouterr().out

    assert "solver 3/MS-1" in out, f"the solver status must be visible; got:\n{out}"


@pytest.mark.unit
def test_the_report_is_also_written_per_run(tmp_path, monkeypatch, capsys):
    """`--json` is a caller-chosen path, so two runs could target the same file.

    The run-local copy means no invocation's result is lost to the other.
    """
    import json as _json

    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    monkeypatch.setattr(mod, "find_gams", lambda: "/fake/gams")
    monkeypatch.setattr(
        mod,
        "run_one",
        lambda mid, wd, **kw: Attribution(mid, summaries=parse_solve_summaries(_TWOCGE)),
    )

    shared_json = tmp_path / "shared.json"
    mod.main(["--models", "x", "--workdir", str(tmp_path / "wd"), "--json", str(shared_json)])
    run_line = [ln for ln in capsys.readouterr().out.splitlines() if ln.startswith("artifacts:")]

    assert run_line, "the run dir must be announced"
    run_dir = Path(run_line[0].split("artifacts:", 1)[1].strip())
    per_run = run_dir / "attribution.json"

    assert per_run.is_file(), "a per-run copy must exist alongside the shared --json"
    assert _json.loads(per_run.read_text()) == _json.loads(shared_json.read_text())


@pytest.mark.unit
def test_reslim_zero_is_accepted(tmp_path, monkeypatch):
    """CONTRIBUTING defines reslim as `int >= 0`, and GAMS accepts 0.

    `scripts/ci/run_pr19_solves.py` accepts zero too, so rejecting it made this
    CLI inconsistent with the repository contract.
    """
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    monkeypatch.setattr(mod, "find_gams", lambda: "/fake/gams")
    monkeypatch.setattr(
        mod,
        "run_one",
        lambda mid, wd, **kw: Attribution(mid, summaries=parse_solve_summaries(_TWOCGE)),
    )

    assert mod.main(["--models", "x", "--reslim", "0", "--workdir", str(tmp_path / "wd")]) == 0


@pytest.mark.unit
def test_run_one_guards_reslim_at_its_own_boundary(tmp_path, monkeypatch):
    """`run_one` is importable and callable directly, bypassing `main`'s check.

    The value reaches GAMS *and* derives the wall-clock timeout, so a direct
    caller must get a structured error rather than an invalid run.
    """
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    def explode(*a, **k):  # pragma: no cover - must never run
        raise AssertionError("no subprocess may run with a negative reslim")

    monkeypatch.setattr(mod.subprocess, "run", explode)

    result = mod.run_one("demo", tmp_path, reslim=-1)

    assert result.verdict == "ERROR"
    assert "reslim must be >= 0" in (result.error or "")


@pytest.mark.unit
def test_a_db_without_schema_version_is_rejected(tmp_path):
    """`schema_version` is required top-level; a bare {"models": [...]} is not the contract."""
    import json

    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    db = tmp_path / "db.json"
    db.write_text(json.dumps({"models": [_row("ok")]}))

    with pytest.raises(mod.InputError, match="schema_version"):
        mod.presolve_match_models(db)


@pytest.mark.unit
@pytest.mark.parametrize("missing", ["model_name", "gamslib_type"])
def test_a_row_missing_a_required_entry_key_is_rejected(tmp_path, missing):
    """Required per-entry keys are validated even though the predicate ignores them."""
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    row = _row("ok")
    del row[missing]

    with pytest.raises(mod.InputError, match=missing):
        mod.presolve_match_models(_write_db(tmp_path, [row]))


@pytest.mark.unit
def test_the_emitted_model_name_is_pinned_not_inherited(tmp_path, monkeypatch):
    """Attribution recognises only `mcp_model`, so the emit must pin it.

    Relying on `src.cli`'s default means a change there would silently strip
    every genuine MCP solve of its matching summary.
    """
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    raw_dir = tmp_path / "data" / "gamslib" / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "demo.gms").write_text("* stand-in\n")
    monkeypatch.setattr(mod, "PROJECT_ROOT", tmp_path)

    seen = {}

    def fake_run(cmd, **kw):
        if "src.cli" in cmd:
            seen["cmd"] = cmd
            (tmp_path / "demo_mcp_presolve.gms").write_text("* emitted\n")
        else:
            (tmp_path / "demo.lst").write_text(_TWOCGE)
        return _completed()

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    monkeypatch.setattr(mod, "find_gams", lambda: "/fake/gams")

    mod.run_one("demo", tmp_path)

    cmd = seen["cmd"]
    assert "--model-name" in cmd, f"the model name must be pinned; got {cmd}"
    assert cmd[cmd.index("--model-name") + 1] == mod.EMITTED_MCP_MODEL


@pytest.mark.unit
def test_a_read_only_json_destination_fails_before_the_sweep(tmp_path, monkeypatch, capsys):
    """Existence is not writability.

    A read-only parent passed the old `is_dir()` check, so the failure was
    deferred until after every model had been solved.
    """
    import scripts.sprint_audit.check_mcp_solve_attribution as mod

    readonly = tmp_path / "ro"
    readonly.mkdir()
    readonly.chmod(0o500)

    monkeypatch.setattr(mod, "find_gams", lambda: "/fake/gams")

    def explode(*a, **k):  # pragma: no cover - must never run
        raise AssertionError("the sweep must not start with an unwritable --json path")

    monkeypatch.setattr(mod, "run_one", explode)

    try:
        rc = mod.main(
            ["--models", "x", "--workdir", str(tmp_path / "wd"), "--json", str(readonly / "r.json")]
        )
        assert rc == 2
        assert "--json" in capsys.readouterr().err
    finally:
        readonly.chmod(0o700)

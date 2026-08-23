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

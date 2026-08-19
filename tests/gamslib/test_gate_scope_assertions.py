"""Sprint 38 P6b — the two gate-scope narrowing modes, and their assertions.

Both modes are *false-negative generators*: the check silently narrows what it
measures, then reports a verdict that reads as health. That is worse than no
check, because it is quoted as evidence.

Each test below is written as **fail-before / pass-after**: it asserts the
property the fix establishes, and would have failed on the pre-fix code. The
pre-fix behaviour is stated in each docstring so the regression is legible
without digging through history.

Mode 1 — ``run_full_test.py --resolve-changed`` selects via
``git diff <since>..HEAD``:
  * an empty selection returned ``verdict: GO`` (it measured nothing);
  * uncommitted goldens are invisible by construction, which produced a real
    false GO in Sprint 37.

Mode 2 — ``check_golden_staleness.py --expect-drift`` reported a model that
never got compared as ``NO-OP: … the fix did not change the emit``, which is a
correctness claim about a run that never looked at it (the standing ``sarf``
case: sarf has no golden).
"""

from __future__ import annotations

import argparse
from typing import Any

import pytest

from scripts.gamslib.run_full_test import run_resolve_changed


def _args(**over: Any) -> argparse.Namespace:
    """A --resolve-changed argv namespace with the defaults the CLI would supply."""
    base: dict[str, Any] = {
        "since_commit": "deadbeef",
        "resolve_changed": True,
        "only_parse": False,
        "only_translate": False,
        "only_solve": False,
        "json": False,
        "quiet": True,
        "dry_run": False,
        "min_scope": None,
        "allow_empty": False,
    }
    base.update(over)
    return argparse.Namespace(**base)


class TestResolveChangedEmptySelection:
    """An empty selection must not read as health.

    FAIL-BEFORE: the pre-fix code returned ``{"verdict": "GO", "note": "no emit
    goldens changed since …"}`` and exited 0 — a checkpoint that measured zero
    models certifying the tree.
    """

    def test_empty_selection_is_an_error_not_a_go(self, monkeypatch):
        monkeypatch.setattr(
            "scripts.gamslib.run_full_test._uncommitted_golden_model_ids", lambda: []
        )
        monkeypatch.setattr(
            "scripts.gamslib.run_full_test._changed_golden_model_ids", lambda since: []
        )
        result = run_resolve_changed(_args())

        assert "error" in result, "an empty selection must not produce a verdict at all"
        assert result.get("verdict") != "GO"
        assert "measured NOTHING" in result["error"]

    def test_allow_empty_opts_in_and_says_it_certifies_nothing(self, monkeypatch):
        """The legitimate empty case (a docs-only day) stays available — explicitly."""
        monkeypatch.setattr(
            "scripts.gamslib.run_full_test._uncommitted_golden_model_ids", lambda: []
        )
        monkeypatch.setattr(
            "scripts.gamslib.run_full_test._changed_golden_model_ids", lambda since: []
        )
        result = run_resolve_changed(_args(allow_empty=True))

        assert result.get("verdict") == "GO"
        assert result.get("empty_selection") is True
        # The GO must carry its own disclaimer: this is what stops it being
        # pasted into a sprint doc as evidence of a healthy corpus.
        assert "certifies nothing" in result["note"].lower()


class TestResolveChangedUncommittedGoldens:
    """Uncommitted goldens are invisible to the selector — refuse, don't certify.

    FAIL-BEFORE: selection is ``git diff <since>..HEAD``, so a regenerated but
    uncommitted golden was silently omitted and the checkpoint reported GO
    without ever re-solving it. This is the Sprint-37 false GO.
    """

    def test_uncommitted_goldens_block_the_checkpoint(self, monkeypatch):
        monkeypatch.setattr(
            "scripts.gamslib.run_full_test._uncommitted_golden_model_ids",
            lambda: ["markov", "prolog"],
        )
        monkeypatch.setattr(
            "scripts.gamslib.run_full_test._changed_golden_model_ids",
            lambda since: ["fawley"],
        )
        result = run_resolve_changed(_args())

        assert "error" in result
        assert "INVISIBLE" in result["error"]
        assert "markov" in result["error"] and "prolog" in result["error"]

    def test_blocks_even_when_the_committed_selection_is_non_empty(self, monkeypatch):
        """The dangerous shape: a plausible-looking GO over the wrong set.

        A non-empty committed selection makes the run look like it did real work,
        which is exactly why the uncommitted set must be checked independently
        rather than only when the selection is empty.
        """
        monkeypatch.setattr(
            "scripts.gamslib.run_full_test._uncommitted_golden_model_ids",
            lambda: ["sarf"],
        )
        monkeypatch.setattr(
            "scripts.gamslib.run_full_test._changed_golden_model_ids",
            lambda since: ["ganges", "gangesx", "korcge"],
        )
        result = run_resolve_changed(_args())
        assert "error" in result and "sarf" in result["error"]


class TestResolveChangedMinScope:
    """A silently narrowed selection still reported GO — assert the count."""

    def test_below_min_scope_is_an_error(self, monkeypatch):
        monkeypatch.setattr(
            "scripts.gamslib.run_full_test._uncommitted_golden_model_ids", lambda: []
        )
        monkeypatch.setattr(
            "scripts.gamslib.run_full_test._changed_golden_model_ids",
            lambda since: ["ganges"],
        )
        result = run_resolve_changed(_args(min_scope=3))

        assert "error" in result
        assert "--min-scope 3" in result["error"]
        assert "narrowed silently" in result["error"]

    def test_at_or_above_min_scope_proceeds_past_the_assertion(self, monkeypatch):
        """A floor, not an equality — selecting more than expected must not trip it."""
        monkeypatch.setattr(
            "scripts.gamslib.run_full_test._uncommitted_golden_model_ids", lambda: []
        )
        monkeypatch.setattr(
            "scripts.gamslib.run_full_test._changed_golden_model_ids",
            lambda since: ["ganges", "gangesx", "korcge", "prolog"],
        )
        result = run_resolve_changed(_args(min_scope=3, dry_run=True))

        assert "error" not in result
        assert result["changed_models"] == ["ganges", "gangesx", "korcge", "prolog"]


class TestUncommittedGoldenDetection:
    """The porcelain parse itself — it decides whether the assertion can fire."""

    def test_parses_modified_and_untracked_entries(self, monkeypatch):
        import subprocess

        porcelain = (
            " M data/gamslib/mcp/markov_mcp.gms\n"
            "?? data/gamslib/mcp/newmodel_mcp.gms\n"
            " M data/gamslib/mcp/rocket_mcp_presolve.gms\n"
            " M src/emit/emit_gams.py\n"
        )

        def fake_run(*a, **kw):
            return subprocess.CompletedProcess(a, 0, stdout=porcelain, stderr="")

        monkeypatch.setattr(subprocess, "run", fake_run)
        from scripts.gamslib.run_full_test import _uncommitted_golden_model_ids

        got = _uncommitted_golden_model_ids()
        # Presolve goldens map to their model id; non-golden paths are ignored.
        assert got == ["markov", "newmodel", "rocket"]

    def test_git_failure_does_not_fabricate_a_clean_tree(self, monkeypatch):
        """If git is unavailable the helper returns empty — documented, not silent.

        The caller cannot establish scope in that case; this test pins the
        behaviour so a future change does not turn an unavailable check into a
        confident pass.
        """
        import subprocess

        def boom(*a, **kw):
            raise FileNotFoundError("git not found")

        monkeypatch.setattr(subprocess, "run", boom)
        from scripts.gamslib.run_full_test import _uncommitted_golden_model_ids

        assert _uncommitted_golden_model_ids() == []


class TestExpectDriftMissingClassification:
    """`NO-OP` vs `NO-GOLDEN` vs `ALLOWLISTED` — same symptom, opposite meanings.

    FAIL-BEFORE: all three printed ``NO-OP: … the fix did not change the emit``,
    a correctness claim about the emit. For ``sarf`` — which has no golden at all
    — that sends an engineer to debug an emit the sweep never compared.
    """

    @staticmethod
    def _classify(
        expected: set[str],
        drifted: set[str],
        discovered: set[str],
        allow: set[str],
        swept: set[str] | None = None,
    ):
        """Call the SHIPPED classifier — deliberately not a local mirror.

        A test that re-implements the logic it is checking proves only that two
        copies agree; it would pass against the pre-fix code, which is exactly
        the "verify a component, assert a system property" defect P6b exists to
        catch. Importing the real function makes this fail-before.

        ``swept`` defaults to everything discovered that is not allowlisted —
        i.e. no ``--models`` narrowing.
        """
        from scripts.sprint_audit.check_golden_staleness import classify_missing_expected

        return classify_missing_expected(
            sorted(expected - drifted),
            discovered_models=discovered,
            swept_models=discovered - allow if swept is None else swept,
            allowlisted_models=allow,
        )

    def test_model_with_no_golden_is_not_reported_as_a_no_op(self):
        no_golden, excluded, allowlisted, no_op = self._classify(
            expected={"sarf"}, drifted=set(), discovered={"markov", "fawley"}, allow=set()
        )
        assert no_golden == ["sarf"], "sarf has no golden — it was never compared"
        assert no_op == [], "must NOT claim the emit was byte-identical"
        assert allowlisted == [] and excluded == []

    def test_allowlisted_model_is_distinguished_from_having_no_golden(self):
        """It HAS a golden — it was skipped. Reporting 'no golden' would be wrong."""
        no_golden, excluded, allowlisted, no_op = self._classify(
            expected={"indus"},
            drifted=set(),
            discovered={"indus", "markov"},
            allow={"indus"},
        )
        assert allowlisted == ["indus"]
        assert no_golden == [] and no_op == [] and excluded == []

    def test_genuine_no_op_still_reported_as_no_op(self):
        """The real case must survive: compared, in scope, byte-identical."""
        no_golden, excluded, allowlisted, no_op = self._classify(
            expected={"markov"}, drifted=set(), discovered={"markov"}, allow=set()
        )
        assert no_op == ["markov"]
        assert no_golden == [] and allowlisted == [] and excluded == []

    def test_model_excluded_by_models_is_not_reported_as_no_golden(self):
        """A `--models` subset is a property of the INVOCATION, not of the corpus.

        FAIL-BEFORE (of the review fix): `corpus_models` was derived from the
        already-filtered golden list, so a model the user excluded via `--models`
        was reported as "has NO golden in the corpus" — a corpus claim that is
        factually false, and the same misattribution this classifier exists to
        prevent, one level up.
        """
        no_golden, excluded, allowlisted, no_op = self._classify(
            expected={"fawley"},
            drifted=set(),
            discovered={"fawley", "markov"},
            allow=set(),
            swept={"markov"},  # --models markov
        )
        assert excluded == ["fawley"], "it HAS a golden; --models filtered it out"
        assert no_golden == [], "must not claim the corpus lacks a golden for it"
        assert no_op == [] and allowlisted == []

    def test_the_four_classes_partition_missing(self):
        """No expected-but-undrifted model may fall through OR land in two classes.

        Precedence is load-bearing: an allowlisted model is also absent from the
        swept set, so `allowlisted` must be decided before `excluded`.
        """
        expected = {"sarf", "indus", "markov", "fawley", "prolog"}
        discovered = {"indus", "markov", "fawley", "prolog"}
        allow = {"indus"}
        swept = {"markov", "prolog"}  # fawley excluded by --models
        no_golden, excluded, allowlisted, no_op = self._classify(
            expected, {"prolog"}, discovered, allow, swept=swept
        )
        classes = [set(no_golden), set(excluded), set(allowlisted), set(no_op)]
        union = set().union(*classes)
        assert union == {"sarf", "indus", "markov", "fawley"}, "nothing may fall through"
        total = sum(len(c) for c in classes)
        assert total == len(union), "classes must be disjoint — no model in two"
        assert (no_golden, excluded, allowlisted, no_op) == (
            ["sarf"],
            ["fawley"],
            ["indus"],
            ["markov"],
        )


class TestKpiBlockDerivation:
    """P6a — the KPI helper must derive from the DB, never carry constants."""

    @staticmethod
    def _db():
        def m(mid, conv, translate, outcome, compare):
            return {
                "model_id": mid,
                "convexity": {"status": conv},
                "nlp2mcp_parse": {"status": "success"},
                "nlp2mcp_translate": {"status": translate},
                "mcp_solve": {"outcome_category": outcome},
                "solution_comparison": {"comparison_status": compare},
            }

        return {
            "models": [
                m("a", "verified_convex", "success", "model_optimal", "match"),
                m("b", "likely_convex", "success", "model_optimal_presolve", "match"),
                m("c", "likely_convex", "success", "model_infeasible", "not_tested"),
                m("d", "verified_convex", "failure", "path_syntax_error", None),
                # non_convex: outside the candidate corpus, but counts in all-219
                m("e", "non_convex", "success", "model_optimal", "match"),
            ]
        }

    def test_candidate_scope_excludes_non_convex(self):
        from scripts.sprint_audit.kpi_block import compute_kpis

        k = compute_kpis(self._db())
        assert k["candidates"] == 4, "non_convex models are outside the KPI corpus"
        assert k["total_models"] == 5

    def test_match_splits_cold_and_presolve(self):
        from scripts.sprint_audit.kpi_block import compute_kpis

        k = compute_kpis(self._db())
        assert (k["match"], k["match_cold"], k["match_presolve"]) == (2, 1, 1)

    def test_all_219_match_spans_the_whole_corpus(self):
        """The one figure that is NOT candidate-scoped — it includes non_convex."""
        from scripts.sprint_audit.kpi_block import compute_kpis

        k = compute_kpis(self._db())
        assert k["all_219_match"] == 3

    def test_solve_counts_the_presolve_retry(self):
        from scripts.sprint_audit.kpi_block import compute_kpis

        k = compute_kpis(self._db())
        assert k["solve"] == 2

    def test_mechanical_count_is_labelled_not_the_floor(self):
        """The mechanical count must be emitted, and must never be called the floor.

        A `Match − (presolve ∧ match)` count looks authoritative and is wrong —
        the "cold emit byte-identical to pre-fix" qualifier lives only in the
        hand-maintained partition.
        """
        from scripts.sprint_audit.kpi_block import _render_markdown, compute_kpis

        k = compute_kpis(self._db())
        assert k["mechanical_cold_match_count"] == k["match_cold"]
        rendered = _render_markdown(k, "abc1234", dirty=False)
        assert "NOT derivable from the DB" in rendered
        assert "not** the floor" in rendered

    def test_render_carries_the_commit(self):
        from scripts.sprint_audit.kpi_block import _render_line, _render_markdown, compute_kpis

        k = compute_kpis(self._db())
        assert "abc1234" in _render_markdown(k, "abc1234", dirty=False)
        assert "abc1234" in _render_line(k, "abc1234", dirty=False)

    def test_dirty_check_targets_the_db_actually_read(self, tmp_path, monkeypatch):
        """`--db` must be honoured: never report on a file that produced no figures.

        FAIL-BEFORE (of the review fix): `_dirty_db()` always stat-ed the default
        DATABASE_PATH, so pointing `--db` elsewhere produced a dirtiness verdict
        about an unrelated file.
        """
        import subprocess

        from scripts.sprint_audit import kpi_block

        seen: list[list[str]] = []

        def fake_run(cmd, *a, **kw):
            seen.append(list(cmd))
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        monkeypatch.setattr(subprocess, "run", fake_run)
        alt = kpi_block.PROJECT_ROOT / "data" / "gamslib" / "alt_db.json"
        kpi_block._dirty_db(alt)
        assert seen and seen[-1][-1].endswith(
            "alt_db.json"
        ), "the dirty check must name the DB that was actually read"

    def test_dirty_check_makes_no_claim_for_a_db_outside_the_repo(self, tmp_path):
        """git cannot speak to it — return False rather than guess."""
        from scripts.sprint_audit.kpi_block import _dirty_db

        outside = tmp_path / "elsewhere.json"
        outside.write_text("{}")
        assert _dirty_db(outside) is False

    def test_dirty_db_is_flagged_in_both_renderings(self):
        """A block derived from an uncommitted DB is not reproducible from its SHA."""
        from scripts.sprint_audit.kpi_block import _render_line, _render_markdown, compute_kpis

        k = compute_kpis(self._db())
        assert "uncommitted" in _render_markdown(k, "abc1234", dirty=True)
        assert "uncommitted" in _render_line(k, "abc1234", dirty=True).lower()


@pytest.mark.parametrize(
    "path,expected",
    [
        ("data/gamslib/mcp/markov_mcp.gms", "markov"),
        ("data/gamslib/mcp/rocket_mcp_presolve.gms", "rocket"),
        ("src/emit/emit_gams.py", None),
    ],
)
def test_golden_path_mapping_unchanged(path, expected):
    """Guard the mapping both assertions depend on."""
    from scripts.gamslib.run_full_test import _model_id_from_golden_path

    assert _model_id_from_golden_path(path) == expected

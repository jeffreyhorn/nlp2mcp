"""Sprint 39 P8-8a/8b — the added-only Phase-0 requirements.

Two new requirements apply to a Phase-0 doc a PR **adds**:

* **8a** a ``**Layer:**`` metadata line — the gate must name the layer it targets;
* **8b** a ``### Nearest Existing Mechanism`` subsection that records **why the
  nearest mechanism does not apply**, not merely that one was found.

⚠ WHY ADDED-ONLY, AND WHY THAT IS THE LOAD-BEARING PART OF THE DESIGN.
Making these unconditional would retroactively fail **all 39** currently
conforming issue docs (measured 2026-09-06). A gate that goes red on untouched
history gets switched off, and a switched-off gate protects nothing. So the
requirement is scoped to `status == "added"`, which `pulls.listFiles` already
reports and the workflow previously discarded.

⚠ WHY 8b DEMANDS A REASON RATHER THAN A NAME. This sprint is the worked example.
ISSUE_1714's Day-1 trace found the nearest mechanism existed for **three**
neighbouring populations (Pattern-C members B-1/B-2/B-3) and still did not cover
dyncge — each requires a single-index ``Sum``. A field recording only "B-2 is
nearest" would have aimed the fix at B-2 and produced either a corpus-wide leak
(measured: 10 goldens against a zero-drift baseline) or dead code. The reason is
the content that carries the weight.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# ⚠ Load by spec and RESTORE sys.path — do not `sys.path.insert` at module level.
# An earlier revision did, and it broke
# `test_check_doc_figures.py::test_the_module_works_after_its_sys_path_entry_is_removed`,
# a probe that exists precisely to catch this leak. Same pattern, and the same
# reason, as that file and `tests/unit/test_presolve_divergence_classify.py`:
# a module-level path mutation leaks import-resolution order into the whole
# pytest run and causes order-dependent failures elsewhere.
_SPEC = importlib.util.spec_from_file_location(
    "check_phase0_doc",
    PROJECT_ROOT / "scripts" / "sprint_audit" / "check_phase0_doc.py",
)
assert _SPEC and _SPEC.loader
_mod = importlib.util.module_from_spec(_SPEC)
sys.modules["check_phase0_doc"] = _mod
_saved_sys_path = list(sys.path)
try:
    _SPEC.loader.exec_module(_mod)
finally:
    sys.path[:] = _saved_sys_path

missing_for_added = _mod.missing_for_added
missing_subsections = _mod.missing_subsections

_BASE = """\
**Layer:** **KKT / stationarity** — `src/kkt/stationarity.py` ~123–456

## Phase 0: Acceptance Gate

### Hand-Derived KKT Shape
derived by hand.

### Expected Emit Pattern
the shape.

### Nearest Existing Mechanism
{nearest}

### Verification Methodology
1. fail-before.

### PROCEED/REPLAN Signal
PROCEED if ...
"""

WITH_REASON = _BASE.format(
    nearest=(
        "B-2 is nearest by body shape, but it **does not apply**: it requires a "
        "single-index `Sum` and this shape binds two coordinates."
    )
)
NAME_ONLY = _BASE.format(nearest="B-2 is the nearest existing mechanism.")
NO_SUBSECTION = _BASE.replace("### Nearest Existing Mechanism\n{nearest}\n\n", "").format(
    nearest=""
)
NO_LAYER = WITH_REASON.replace(
    "**Layer:** **KKT / stationarity** — `src/kkt/stationarity.py` ~123–456\n", ""
)


@pytest.mark.unit
def test_conforming_added_doc_passes_both_new_requirements():
    assert missing_subsections(WITH_REASON) == []
    assert missing_for_added(WITH_REASON) == []


@pytest.mark.unit
def test_added_doc_without_the_nearest_mechanism_subsection_fails():
    """8b fail-before."""
    assert missing_subsections(NO_SUBSECTION) == [], "the base 4 must still be satisfied"
    assert "Nearest Existing Mechanism" in " ".join(missing_for_added(NO_SUBSECTION))


@pytest.mark.unit
def test_added_doc_that_only_NAMES_a_mechanism_fails():
    """8b's actual point: naming one is not enough — the *why not* is required.

    This is the case that distinguishes the requirement from a box-tick, and the
    one the sprint itself would have failed.
    """
    assert missing_subsections(NAME_ONLY) == []
    problems = " ".join(missing_for_added(NAME_ONLY))
    assert "Nearest Existing Mechanism" in problems
    assert "does not apply" in problems, f"expected a reason-missing diagnosis, got: {problems}"


@pytest.mark.unit
def test_added_doc_without_a_layer_field_fails():
    """8a fail-before."""
    assert missing_subsections(NO_LAYER) == []
    assert "**Layer:** metadata line" in missing_for_added(NO_LAYER)


@pytest.mark.unit
def test_the_new_requirements_do_not_apply_to_existing_docs():
    """⚠ NEGATIVE CONTROL — the whole reason the requirement is added-only.

    A doc that satisfies the base four but has neither new field must remain
    conforming under `missing_subsections`, which is what runs for a *modified*
    doc. Without this, the gate would fail all 39 existing issue docs.
    """
    legacy = NO_LAYER.replace(
        "### Nearest Existing Mechanism\n"
        "B-2 is nearest by body shape, but it **does not apply**: it requires a "
        "single-index `Sum` and this shape binds two coordinates.\n\n",
        "",
    )
    assert missing_subsections(legacy) == [], (
        "an existing doc with the base four subsections must stay conforming; "
        "the new requirements are added-only by design"
    )
    assert missing_for_added(legacy) != [], "…while an ADDED doc in that state must fail"


@pytest.mark.unit
def test_every_existing_issue_doc_still_conforms():
    """The measured claim behind the design, asserted rather than recalled."""
    issues = PROJECT_ROOT / "docs" / "issues"
    # ⚠ glob, NOT rglob — this must match the SCOPE the gate itself uses.
    # `check_phase0_doc` resolves docs with a non-recursive
    # `ISSUES_DIR.glob("ISSUE_<n>_*.md")`, so archived docs under
    # `docs/issues/finished/` and `docs/issues/completed/` are deliberately out
    # of scope: they are history, and `check_doc_figures` excludes them for the
    # same reason. An earlier revision of this test used rglob and flagged
    # `ISSUE_1455` (archived Sprint 28) — a doc the gate never inspects. A test
    # asserting a WIDER scope than the thing it checks reports false failures.
    docs = sorted(issues.glob("ISSUE_*.md"))
    if not docs:
        pytest.skip("no issue docs present")
    broken = [
        d.name
        for d in docs
        if "Phase 0: Acceptance Gate" in d.read_text(encoding="utf-8")
        and missing_subsections(d.read_text(encoding="utf-8"))
    ]
    assert broken == [], f"these live docs would newly fail the base gate: {broken}"


# A document carrying TWO acceptance gates -- one issue, two independent levers,
# each with its own criteria. The second gate holds the added-only fields.
TWO_GATES = """\
**Layer:** **AD / differentiation** — `src/ad/ad_core.py`

## Phase 0: Acceptance Gate

### Hand-Derived KKT Shape
first gate.

### Expected Emit Pattern
first gate.

### Verification Methodology
first gate.

### PROCEED/REPLAN Signal
first gate.

## Phase 0: Acceptance Gate — the second lever

### Nearest Existing Mechanism
The first gate's narrowing is nearest, but it **does not apply**: it changes the
column count, not the per-column cost.

### Hand-Derived KKT Shape
unchanged — this is a performance change.

### Expected Emit Pattern
byte-identical corpus-wide.

### Verification Methodology
call-count fail-before.

### PROCEED/REPLAN Signal
PROCEED if byte-identical.
"""


@pytest.mark.unit
def test_a_second_phase0_gate_is_not_invisible():
    """⚠ MULTI-GATE guard — found by being the rule's own first customer.

    `phase0_subsections` and `subsection_body` both used `PHASE0_HEADING.search`,
    which stops at the FIRST Phase-0 heading. A document carrying a second
    acceptance gate had that gate ignored entirely: its
    `### Nearest Existing Mechanism` was reported missing, and once found, its
    body was reported as recording no reason -- because the body was never read.

    That is worse than not checking at all: the gate reported a specific, wrong
    reason. Both functions now scan every Phase-0 section (Sprint 39 Day 8).
    """
    assert missing_subsections(TWO_GATES) == []
    assert missing_for_added(TWO_GATES) == [], (
        "the second gate's Nearest Existing Mechanism (and its 'does not apply' "
        "reason) must be seen; reading only the first gate makes this fail"
    )

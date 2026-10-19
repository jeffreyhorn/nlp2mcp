"""``floor_tracker.py`` and the license-unlocked ledger (Sprint 40 P1, Decision 1 = B).

The ledger's one job is to make an unearned match VISIBLE without letting it
MOVE the floor. So the central property is negative: adding a ledger entry must
change the report and must not change ``compute_floor``. The validation rules
are the owner's answer:

* cold matches only (a presolve-only match stays under the existing rule);
* never in both the counted ``entries`` and the ledger.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
_SPEC = importlib.util.spec_from_file_location(
    "floor_tracker", PROJECT_ROOT / "scripts" / "sprint_audit" / "floor_tracker.py"
)
assert _SPEC and _SPEC.loader
ft = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(ft)

COMMITTED = json.loads((PROJECT_ROOT / "data" / "floor_provenance.json").read_text())


def _ledger_entry(model: str = "tfordy", limb: str = "license-unlocked-cold-match") -> dict:
    return {
        "model_id": model,
        "limb": limb,
        "since_sprint": 40,
        "evidence": "licensed cold MCP matches the NLP reference (batch <sha>)",
        "pr": "0000",
    }


def test_the_committed_file_has_an_empty_ledger_and_floor_75() -> None:
    assert COMMITTED["license_unlocked"] == []
    assert ft.compute_floor(COMMITTED) == COMMITTED["expected_floor"] == 75
    assert ft.validate_entries(COMMITTED) == []


def test_a_ledger_entry_never_moves_the_floor() -> None:
    prov = copy.deepcopy(COMMITTED)
    before = ft.compute_floor(prov)
    prov["license_unlocked"] = [_ledger_entry("tfordy"), _ledger_entry("turkey")]
    assert ft.compute_floor(prov) == before
    assert len(ft.license_unlocked(prov)) == 2
    assert ft.validate_entries(prov) == []


def test_only_cold_matches_enter_the_ledger() -> None:
    prov = copy.deepcopy(COMMITTED)
    prov["license_unlocked"] = [_ledger_entry(limb="license-unlocked-presolve-match")]
    problems = ft.validate_entries(prov)
    assert any("COLD matches only" in p for p in problems), problems


def test_a_model_is_never_both_counted_and_in_the_ledger() -> None:
    prov = copy.deepcopy(COMMITTED)
    counted = prov["entries"][0]["model_id"]
    prov["license_unlocked"] = [_ledger_entry(counted)]
    assert any("never both" in p for p in ft.validate_entries(prov))


def test_ledger_entries_need_the_same_audit_fields_and_no_duplicates() -> None:
    prov = copy.deepcopy(COMMITTED)
    bad = _ledger_entry()
    del bad["evidence"]
    prov["license_unlocked"] = [bad, _ledger_entry("x"), _ledger_entry("x")]
    problems = ft.validate_entries(prov)
    assert any("missing 'evidence'" in p for p in problems)
    assert any("duplicate" in p for p in problems)


def test_a_pre_sprint_40_file_without_a_ledger_still_works() -> None:
    prov = copy.deepcopy(COMMITTED)
    del prov["license_unlocked"]
    assert ft.license_unlocked(prov) == []
    assert ft.compute_floor(prov) == 75


def _run(tmp_path: Path, prov: dict, *args: str) -> subprocess.CompletedProcess:
    f = tmp_path / "prov.json"
    f.write_text(json.dumps(prov))
    return subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts/sprint_audit/floor_tracker.py"),
            "--provenance",
            str(f),
            *args,
        ],
        capture_output=True,
        text=True,
    )


def test_the_report_states_the_ledger_beside_the_floor(tmp_path) -> None:
    prov = copy.deepcopy(COMMITTED)
    prov["license_unlocked"] = [_ledger_entry("tfordy")]
    out = _run(tmp_path, prov)
    assert out.returncode == 0, out.stderr
    assert "Genuine floor: 75 (+1 license-unlocked, not counted)" in out.stdout
    assert "tfordy" in out.stdout and "NOT COUNTED" in out.stdout
    js = json.loads(_run(tmp_path, prov, "--json").stdout)
    assert (js["floor"], js["license_unlocked_not_counted"]) == (75, 1)


def test_an_invalid_ledger_fails_the_tracker(tmp_path) -> None:
    prov = copy.deepcopy(COMMITTED)
    prov["license_unlocked"] = [_ledger_entry(limb="presolve-match-genuine")]
    assert _run(tmp_path, prov).returncode == 1

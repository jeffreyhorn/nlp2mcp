# Sprint 35 — Day 1 Progress Notes (P4 `$141` + `$145` banked-root re-apply)

**Day:** 1 (Priority 4, roots 1–2) · **Date:** 2026-07-25 · **Owner:** Sprint 35 execution
**Day-0 code anchor:** `78ceaead` (S34 close) · **Branch:** `planning/sprint35-day1-p4-banked-roots`
**Status: ✅ roots 1–2 applied and verified — but BANKED at Day 3 (see `DAY3_P4_BANK_CARRYFORWARD.md`).** Steps 1–2 recover no bucket alone; the all-three-roots landing then hit a **4th root (`$66`, cold)** and a **5th blocker (`rPower` embedded-NLP `$onMultiR` divergence, presolve)**, so ganges/gangesx do **not** recover. Per "no bucket → no `src/`", **all `src/` (incl. this `$141`/`$145` change) was reverted** — this branch is now **docs-only**, a bank/carryforward record. The verified `$141`/`$145` patches remain in git history (`a8ff626c`) + §1 below for the Sprint-36 dedicated recovery effort.

---

## 1. What landed (`src/`)

Two roots of the P4 sequence, both in `src/emit/original_symbols.py` (`emit_post_assignment_na_cleanup`), per `GANGES_RECOVERY_DESIGN.md` §1/§2:

- **`$141`** — a new skip for params whose assignment references a variable attribute (`.l`/`.m`/…). Helper `_param_assignment_references_varref_attr` (+ its recursive `_expr_contains_varref_attr`), mirroring `_param_assignment_has_division:137`. These are **presolve-gated calibration params** (e.g. `adst(i) = dst.l(i)/…`): emitted only under `--nlp-presolve`, so in the **cold** MCP the param is declared-but-unassigned and the NA-cleanup guard reads an unassigned symbol → GAMS `$141`.
- **`$145`** — a skip for params whose domain contains the universal set `*` (e.g. `series(*,years)`). `*` is a valid *declaration* placeholder but not a valid *assignment/`$`-guard* index, so the emitted guard is structurally malformed → GAMS `$145`. Such `*`-domain data tables are not the NA source #1322 targets anyway.

Diff: **44 insertions, one file** (2 helpers + 2 loop skips). No other `src/` touched. `VarRef.attribute` is `src/ir/ast.py:53`; `VarRef` already imported at module scope.

## 2. Verification (LIVE — re-emit + `gams a=c` compile)

Re-emitted **ganges** and **gangesx** with the fix (`.venv/bin/python -m src.cli`, ~200 s each) and compiled:

| Model | `$141` | `$145` | `$149` | total errors | lines | compiles? |
|---|---|---|---|---|---|---|
| ganges (Day-0 golden) | 15 | 3 | 9 | 51 | 1375 | ✗ |
| **ganges (+`$141`+`$145`)** | **0** | **0** | **9** | **22** | 1359 | ✗ (still `$149`×9) |
| gangesx (Day-0 golden) | 15 | 3 | 9 | 51 | 1375 | ✗ |
| **gangesx (+`$141`+`$145`)** | **0** | **0** | **9** | **22** | 1359 | ✗ (still `$149`×9) |

**Exactly the design's predicted mid-sequence state** (`GANGES_RECOVERY_DESIGN.md` §Central result, row "+`$141`+`$145`"): `$141`×15 → 0, `$145`×3 → 0, `$149`×9 remain, both models still `path_syntax_error`. The `$300`/`$257` in the residual 22 are downstream cascades of the 9 `$149`.

**⚠ No bucket move — and that is correct.** The S34 multi-root finding is re-proven on the current tree: fixing `$141`+`$145` alone recovers nothing; ganges/gangesx stay `path_syntax_error` until `$149` lands (Day 3). A mid-sequence flat KPI is the expected state, not a failure.

## 3. Determinism ✅ ×3

ganges emit is **byte-identical** under `PYTHONHASHSEED ∈ {0,1,42}` (all 1359 lines; `diff -q` clean across all three). The full ×3-on-every-changed-golden sweep runs at the shipping landing (Day 3–4).

## 4. Quality gate (Python touched)

`make typecheck` ✅ (mypy: no issues, 99 files) · `make format` ✅ (ruff import-sort + black: 0 changes) · `make lint` ✅ · `make test` ✅ (see PR). The 13 existing NA-cleanup tests (`test_na_cleanup_emission`, `test_gtm_bounds_guard`, `test_gtm_na_cleanup`) pass — gtm's params divide but reference no `.l` and have no `*`-domain, so the new skips don't touch them.

## 5. Not done on Day 1 (deferred to the shipping landing, Day 3–4) — by design

- **Golden regeneration is NOT committed here.** The `$141` fix is *general* — it also drops the (no-op) cleanup guard on the `.l`-calibration collateral models (chakra, dinam, gancnsx, prolog, saras, senstran, shale, tfordy, turkey, indus — **not** the data-calibrated CGE cluster), golden-byte drift with 0 bucket change. Regenerating those now — only to regenerate again after `$149` — would churn the WIP twice. They regenerate **once**, scoped (`check_golden_staleness.py --models … --fix`, never the unscoped `make regen-goldens`), at the all-three-roots landing.
- **`--resolve-changed` GO** — run at the landing (it enumerates the exact collateral drift set against `78ceaead`).

### ⚠ Golden-staleness CI finding → this branch is HELD as a draft (Option B)

An earlier draft of this note claimed the stale goldens were "CI-safe." **That was wrong.** The PR26 **golden-staleness CI job** (`scripts/sprint_audit/check_golden_staleness.py`, distinct from the `slow`/skip-if-absent golden-comparison *tests*) always runs on `src/emit/` changes: it re-emits every in-scope golden and byte-diffs it, and it **hard-fails** on `ganges_mcp.gms` + `gangesx_mcp.gms` drift (−888 bytes each); `indus_mcp.gms` also drifts but is allowlisted (WARN only). So a standalone `$141`+`$145` PR **cannot be CI-green** without committing 0-bucket golden churn — exactly what the "no bucket → no `src/`" rule forbids ("ship as one coherent landing, or not at all"). **Resolution (Option B):** PR #1617 is converted to a **draft** and the branch is **held**. The `$141`+`$145` code + the unit tests stay here; `$149` lands Day 3; the goldens regenerate **once** (now *compiling*) at the all-three-roots landing, when the real (non-draft) PR opens. Red golden-staleness CI on the draft is expected and correct until then.

## 6. Next (Day 2)

`$149` `/tmp` control BEFORE `src/` — the sole live REPLAN gate: prototype the `_diff_prod:3276` correction, reproduce Task 4's hand-derived `stat_pc` cross-term, drive ganges's 9 `$149` → 0, and confirm the 18-model prod-in-stationarity regression set stays byte-identical (lmp2 most sensitive). REPLAN exit if it can't be made surgical → bank all three (this branch's `$141`+`$145` included), reallocate to P6/P7.

---

**Document Status:** ✅ Complete — Sprint 35 Day 1 (WIP checkpoint)
**Last Updated:** 2026-07-25
**Owner:** Sprint 35 Execution Team

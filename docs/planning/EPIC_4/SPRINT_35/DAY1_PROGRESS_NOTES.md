# Sprint 35 — Day 1 Progress Notes (P4 `$141` + `$145` banked-root re-apply)

**Day:** 1 (Priority 4, roots 1–2) · **Date:** 2026-07-25 · **Owner:** Sprint 35 execution
**Day-0 code anchor:** `78ceaead` (S34 close) · **Branch:** `planning/sprint35-day1-p4-banked-roots`
**Status: ✅ roots 1–2 applied and verified — WIP, NOT YET SHIPPED.** Steps 1–2 recover **no bucket** on their own (the expected mid-sequence state); they ship only with `$149` (Day 3–4) as one coherent P4 landing, or all three bank. Per the "no bucket → no `src/`" rule, this branch does **not** merge to main standalone.

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

- **Golden regeneration is NOT committed here.** The `$141` fix is *general* — it also drops the (no-op) cleanup guard on ~9 `.l`-calibration collateral models (chakra, dinam, gancnsx, prolog, saras, senstran, shale, tfordy, turkey — **not** the data-calibrated CGE cluster), golden-byte drift with 0 bucket change. Regenerating those now — only to regenerate again after `$149` — would churn the WIP twice. They regenerate **once**, scoped (`check_golden_staleness.py --models … --fix`, never the unscoped `make regen-goldens`), at the all-three-roots landing. So the committed ganges/gangesx/collateral goldens are intentionally stale on this branch (CI-safe: the golden-comparison tests are `slow`/skip-if-absent and excluded from the default gate).
- **`--resolve-changed` GO** — run at the landing (it enumerates the exact collateral drift set against `78ceaead`).

## 6. Next (Day 2)

`$149` `/tmp` control BEFORE `src/` — the sole live REPLAN gate: prototype the `_diff_prod:3276` correction, reproduce Task 4's hand-derived `stat_pc` cross-term, drive ganges's 9 `$149` → 0, and confirm the 18-model prod-in-stationarity regression set stays byte-identical (lmp2 most sensitive). REPLAN exit if it can't be made surgical → bank all three (this branch's `$141`+`$145` included), reallocate to P6/P7.

---

**Document Status:** ✅ Complete — Sprint 35 Day 1 (WIP checkpoint)
**Last Updated:** 2026-07-25
**Owner:** Sprint 35 Execution Team

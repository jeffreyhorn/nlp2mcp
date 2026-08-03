# Sprint 35 — Day 6 (P6 part 1): turkey `$161` recovery + GAMS-path test-infra fix

**Day:** 6 (Priority 6 — residual failure-cohort, part 1) · **Date:** 2026-08-03 · **Owner:** Sprint 35 execution
**Branch:** `planning/sprint35-day6-p6-cohort-1`
**Two deliverables:** (A) turkey `$161` emit-recovery (P6) + (B) the GAMS-path test-infra fix that root-caused the 22 local solve-test failures (freed-budget reallocation, per the sprint's Day-3 P4-bank slack).

---

## A. turkey `$161` — a genuine P6 emit-recovery (compile-verified)

### Root (one real root; the rest are cascades)

turkey's `ao` set is a **domain-less 2-D set**: `ao /grains.wheat, oil-crops.sunflower, .../` (declared with no `ao(ctp,crop)` domain). The set-declaration emit computes `domain_arity = len(domain) or 1 = 1`, so it treats members as 1-D and **whole-quotes** any member that needs quoting: `oil-crops.sunflower` → `'oil-crops.sunflower'` (a 1-D string). That collides with the sibling **unquoted 2-D tuples** (`grains.wheat`) → GAMS **`$161` "Conflicting dimensions in element"** (×6). turkey's `$141`×1 (`nlp2mcp_obj_val = cps.l`) and `$257`×1 are **cascades** of the `$161` failure — they clear with it.

### Fix (`src/emit/original_symbols.py`)

`_infer_domainless_tuple_arity(members)` infers the tuple arity of a **domain-less** set from its members: it returns N > 1 only when every member splits into the same N dot-components and **each component is identifier-like** (`_TUPLE_COMPONENT_PATTERN`, must start with a letter/underscore). `_format_set_declaration` uses it to route domain-less dotted-tuple sets through the existing per-component quoting path → `'oil-crops'.sunflower`. The strict guard keeps genuine 1-D labels whose dot is part of a number (`4.5`, `.9`, `-.005`) whole.

**The wrong first attempt (recorded — PR-review discipline):** I first put the split in `_sanitize_set_element` with a naive `element.split(".")`. That function is **shared with the parameter-data emit path**, and the naive split mangled turkpow's `mdatat` numeric-decimal labels (`'lignite-3'.'4.5'` → `'lignite-3'.'4'.'5'`, `'.9'` → `..'9'`) → **introduced** `$161` in turkpow. Reverted; the correct fix is dimension-aware and lives in the **domain-less-set path** only, not the shared sanitizer.

### Verification (local emit + compile; surgical)

- **turkey compiles clean** (`gams a=c`, GAMS 54): `$161`/`$141`/`$257` → **0**. Emit is `'oil-crops'.sunflower` (correct 2-D tuple); clean tuples (`grains.wheat`) unchanged.
- **Corpus-wide surgical:** full golden-staleness (163 goldens) → **only `turkey_mcp.gms` drifts** (+0 bytes). turkpow byte-identical (the first-attempt regression is gone). Golden regenerated (scoped `--fix`).
- **Determinism ✅ ×3** (`PYTHONHASHSEED {0,1,42}`); 4 new unit tests + 208 existing set-element/quoting tests pass.

### The bucket verdict is a TESTBED step (not local)

turkey's MCP is **3,866 equations / 3,753 variables** — over the local GAMS demo's 1000-row solve limit — so turkey's **solve + match** (the actual `path_syntax_error → model_optimal + match`, +1 Solve/Match, 108→109 off the flat branch) must be confirmed in the **licensed testbed** that builds the DB. Locally, only the compile-recovery is verifiable. **Compile-clean-but-not-yet-solve-verified** is the honest status.

### dinam / indus — not recovered (heavily multi-root, as Task 4 anticipated)

- **dinam:** `$140`×5 · `$8`×3 · `$149`×3 · `$37`×2 · `$171`×2 · `$141`×1 — 6 distinct root codes.
- **indus:** `$141`×8 · `$140`×5 · `$130`×4 · `$409`×3 · `$149`×3 · `$148`×2 · `$767`/`$408`/`$36`×1 — 9 codes.

Neither recovers without clearing its whole multi-root set (a large multi-fix effort, out of scope). turkey was the tractable one (single root + cascades).

---

## B. The 22 local solve-test failures — root-caused + fixed (GAMS-path)

**Symptom:** `make test` showed **22 failures**, all `test_gamslib_match` / `test_gamslib_solve` (+ `test_kkt_residual_e2e`, `test_gams_check`) with `MCP solve failed: no_solve_summary` — on small non-dotted-tuple models (trnsport, himmel16, rbrock, …) unrelated to the turkey change. They **passed on Day 1** (GAMS 53 valid); they fail now (GAMS 53 expired 2026-07-29, GAMS 54 installed).

**Root cause — three GAMS resolvers, all reaching the expired v53:**
1. `solve_mcp` (`scripts/gamslib/test_solve.py`) and `kkt_residual.py` **hardcode a path list that tries `Versions/53` FIRST**. v53 is expired but still on disk, so `Path(...).exists()` picks it → the solve fails with a licensing error and emits no `S O L V E   S U M M A R Y` → the parser returns `no_solve_summary`. (Prepending v54 to `PATH` didn't help — the hardcoded list never reaches `shutil.which`.) *(20 of the 22 failures.)*
2. `tests/integration/test_nlp_presolve.py` (the 2 bearing tests) invokes a **bare `["gams", …]`** subprocess → `PATH` → the expired v53 first → no `MODEL STATUS` line → the "Locally Infeasible" assertion sees `[]`. *(the last 2.)*

`Versions/Current` is a symlink → **54** (the valid install); `find_gams_executable()` (`src/validation/gams_check.py`) already picks the newest numeric version.

**Fix:**
- `test_solve.py`, `kkt_residual.py` — prefer `Versions/Current` over any hardcoded version number (`Current` tracks the active licensed install and can't go stale to an expired pin).
- `test_nlp_presolve.py` — route the two bearing subprocess calls through `find_gams_executable() or "gams"` instead of a bare `"gams"`.

**Verification:** `make test` went **22 failed → 0**. Sampled failing tests (trnsport, himmel16, rbrock, both bearing) — which failed identically on clean main — now pass. **CI (Linux) was never affected** (no macOS framework path → falls through to `shutil.which`).

**Note (environment):** this is a macOS-local issue. CI (Linux) has no `/Library/Frameworks/GAMS.framework` path, so it falls through to `shutil.which("gams")` and was never affected.

---

## Deliverables

- `src/emit/original_symbols.py` — `_infer_domainless_tuple_arity` + domain-less-set per-part quoting (turkey `$161`).
- `tests/unit/emit/test_original_symbols.py` — 4 new tests (helper + domain-less 2-D set emit).
- `data/gamslib/mcp/turkey_mcp.gms` — regenerated golden (per-part quoting).
- `scripts/gamslib/test_solve.py`, `scripts/diagnostics/kkt_residual.py` — prefer `Versions/Current` over the stale hardcoded `Versions/53`.
- `tests/integration/test_nlp_presolve.py` — route the 2 bearing solves through `find_gams_executable()` instead of a bare `"gams"`. (Full `make test`: 22 failed → 0.)

---

**Document Status:** ✅ Complete — Sprint 35 Day 6 (turkey compile-recovery + GAMS-path test-infra fix)
**Last Updated:** 2026-08-03
**Owner:** Sprint 35 Execution Team

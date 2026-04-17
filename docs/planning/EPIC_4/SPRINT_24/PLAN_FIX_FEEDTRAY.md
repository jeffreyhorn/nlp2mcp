# Plan: Properly Exclude `feedtray` (MINLP) From the nlp2mcp Pipeline

**Goal:** Recognize `feedtray` as an MINLP, mark it as such in the
GAMSlib status database, and ensure the nlp2mcp pipeline (parse,
translate, solve) refuses to process it. nlp2mcp targets continuous
NLP→MCP transformation; MINLPs are categorically out of scope and
must not be silently translated. This plan also generalizes the
exclusion gate so any future MINLP/MIP model in the corpus is
filtered for the same reason.

**Related issue references:** Sprint 24 model audit — `feedtray` shows
contradictory database state: `gamslib_type: "NLP"` (cataloged) and
`convexity.status: "excluded"` with reason *"Model uses MINLP solve
(binary variable yf); discrete models are not suitable for KKT/MCP
transformation"* — yet `nlp2mcp_parse.status: "success"`,
`nlp2mcp_translate.status: "success"`, `mcp_solve.status: "failure"
(path_syntax_error)`. The translate-success / solve-failure pair are
**stale artifacts** from a pre-gate pipeline run; they should never
have been produced.

**Estimated effort:** 2–3 hours (database hygiene + a small guard in
the translator + status JSON sweep).
**Models affected:** `feedtray` is the immediate case; the same gate
catches every other GAMSlib MINLP/MIP/MIQCP that may otherwise leak
into translate/solve attempts.
**Out-of-scope by policy:** No relaxation, no fixed-binary
substitution, no MPEC re-encoding. MINLP stays MINLP and stays out.

---

## Pre-fix State

`feedtray` (GAMSlib SEQ=122, "Optimum Feed Plate Location") is a
distillation-column MINLP: 7 ideal stages, binary indicators `yf(i)`
selecting which candidate tray (`floc = 2..8`) receives the feed.
Source contains `Binary Variable yf(i);` and
`solve column using minlp maximizing zf;`.

| Field in `data/gamslib/gamslib_status.json → feedtray` | Current value | Should be |
|--|--|--|
| `gamslib_type` | `"NLP"` (catalog says NLP) | `"MINLP"` — the source is MINLP regardless of catalog |
| `convexity.status` | `"excluded"` | `"excluded"` ✅ |
| `convexity.error` | "Model uses MINLP solve (binary variable yf)…" | unchanged ✅ |
| `nlp2mcp_parse.status` | `"success"` (stale, 2026-02-25) | absent / `"skipped_minlp"` |
| `nlp2mcp_translate.status` | `"success"` (stale) | absent / `"skipped_minlp"` |
| `mcp_solve.status` | `"failure"` (`path_syntax_error`) | absent / `"skipped_minlp"` |
| `solution_comparison` | `"not_tested"` | absent / `"skipped_minlp"` |

Verified locally:

```bash
$ .venv/bin/python -m src.cli data/gamslib/raw/feedtray.gms -o /tmp/feedtray_mcp.gms
✓ Generated MCP: /tmp/feedtray_mcp.gms        # ← should NOT happen for an MINLP
$ gams /tmp/feedtray_mcp.gms lo=3
*** Error  65  Discrete variables can only appear in MIP, RMIP, MINLP,
                RMINLP, MIQCP, RMIQCP, MPEC, RMPEC problems.
*** Error 256  Error(s) in analyzing solve statement.
```

Today, the only thing stopping the *batch* pipeline from re-processing
`feedtray` is that `batch_parse.get_candidate_models()` filters to
`convexity.status ∈ {"verified_convex", "likely_convex"}` (see
`scripts/gamslib/batch_parse.py:280–283`). That gate is correct but
load-bearing — there is **no second line of defense** at the
translator. A direct CLI invocation
(`python -m src.cli data/gamslib/raw/feedtray.gms ...`) bypasses the
gate entirely and emits an MCP file that GAMS will refuse to compile.

The IR knows enough to gate: `parser._handle_solve()` records
`model.solve_type` from the `using <solver>` clause (parser.py:3588),
and `VariableDef.kind` carries `VarKind.BINARY | INTEGER | SOS1 | SOS2`
(symbols.py:32–40). Either signal is a sufficient MINLP/MIP detector.

---

## Why "Just Exclude" Is The Right Answer

nlp2mcp's transformation rests on the KKT conditions of a smooth
continuous program. Discrete variables break that foundation in
multiple ways at once:

- **Stationarity (∇L = 0)** is undefined at integer points; the
  primal–dual MCP characterization is for the continuous relaxation
  of a smooth NLP, not for the discrete program.
- **PATH (the MCP solver)** rejects discrete variables outright
  (GAMS Error 65) — there is no solver-side path forward.
- **Relaxing binaries to `[0,1]`** silently changes the problem.
  A "matched" objective from a relaxation is a false-positive in the
  pipeline metrics and would corrupt the corpus's solve-rate signal.
- **Project scope.** The corpus is curated for continuous NLP/QCP/LP
  candidates. MINLP/MIP belongs to a different translator class
  (e.g., logical-MPEC reformulations), which is not what this project
  builds.

Therefore: detect, mark, exclude. No translation, no solve attempt,
no comparison.

---

## Issue 1: Stale Pipeline Artifacts For An Excluded Model

### Root Cause

`feedtray`'s entry in `gamslib_status.json` carries `nlp2mcp_parse`,
`nlp2mcp_translate`, `mcp_solve`, and `solution_comparison` blocks
generated *before* the convexity gate was tightened. They are stale
and misleading: they suggest the model is in some intermediate
"translatable but not solvable" state, when in fact it should never
have been touched at all.

### Fix Strategy

Sweep `data/gamslib/gamslib_status.json` and, for every model with
`convexity.status == "excluded"`:

- Replace `nlp2mcp_parse`, `nlp2mcp_translate`, `mcp_solve`,
  `solution_comparison` with a single `pipeline_status` block:

  ```json
  "pipeline_status": {
    "status": "skipped",
    "reason": "minlp_out_of_scope",   // or "infeasible_nlp", etc.
    "marked_date": "2026-04-16T...Z",
    "details": "<copy of convexity.error>"
  }
  ```

  Keep the original `convexity` block intact for provenance.

- Update `gamslib_type` only when the catalog disagrees with the
  source (feedtray: `"NLP"` → `"MINLP"`). Add an
  `original_gamslib_type` field to preserve the catalog value for
  audit.

### Files

| File | Change |
|------|--------|
| `data/gamslib/gamslib_status.json` | Schema 2.1.0 → 2.2.0; new `pipeline_status` block for excluded models; correct `gamslib_type` where source disagrees with catalog |
| `scripts/gamslib/migrate_schema_v2.2.0.py` (new) | One-shot migration that re-derives `gamslib_type` from the parsed source's `solve … using …` clause and writes `pipeline_status: skipped/minlp_out_of_scope` for excluded models |
| `scripts/gamslib/db_manager.py` | Recognize the new `pipeline_status` block in queries and reports |
| `scripts/gamslib/generate_download_report.py` | Surface MINLP-excluded count separately from "failure" |

---

## Issue 2: Translator Has No Defense-in-Depth Against MINLP Input

### Root Cause

`src/cli.py` and the translator modules (`src/kkt/`, `src/emit/`)
trust the caller. There is no early "is this an MINLP?" check, so a
direct CLI call on `feedtray.gms` happily produces an MCP file with a
`Binary Variables` block that GAMS rejects.

The IR signals are already there:

- `model.solve_type` populated in `parser._handle_solve()`
  (parser.py:3588) — values include `"NLP"`, `"DNLP"`, `"MINLP"`,
  `"MIP"`, `"LP"`, `"QCP"`, `"RMINLP"`, `"RMIP"`.
- `model.variables[*].kind ∈ {BINARY, INTEGER, SOS1, SOS2}` at
  symbols.py:32–40.

Either is sufficient; checking both makes the gate robust against:

- Models that declare `Binary` vars but use `solve … using rminlp`
  (so `solve_type` looks safe-ish).
- Models that use `solve … using minlp` even when no binaries appear
  in the IR (e.g., binaries hidden behind `$ifthen` macros).

### Fix Strategy

Add a `validate_continuous(model_ir) -> None` check at the
NLP→MCP entry point. The check:

1. Compute `discrete_vars = [v for v in model_ir.variables.values()
   if v.kind in {VarKind.BINARY, VarKind.INTEGER, VarKind.SOS1,
   VarKind.SOS2}]`.
2. Compute `discrete_solve = (model_ir.solve_type or "").upper() in
   {"MIP", "MINLP", "MIQCP", "RMIP", "RMINLP", "RMIQCP"}`.
3. If either is true, raise a typed exception
   `MINLPNotSupportedError(discrete_vars=[...],
   solve_type=...)` with a clear message.

Wire the check into:

- `src/cli.py` — catch the exception, print a one-line diagnostic
  including the variable names, and exit with a distinct non-zero
  code (e.g., `EXIT_MINLP_OUT_OF_SCOPE = 3`) so callers can
  distinguish from compile/parse errors.
- `scripts/gamslib/batch_translate.py` — catch and record
  `pipeline_status: skipped/minlp_out_of_scope` rather than letting
  the translator crash.

Provide an opt-in escape hatch only for testing/development:
`--allow-discrete` flag that downgrades the error to a warning. The
flag is not for production use; it exists so the test suite can still
exercise the "what happens if someone forces MINLP through" path
without sprinkling try/except around the translator core.

### Files

| File | Change |
|------|--------|
| `src/translate/validate.py` (new) | `validate_continuous(model_ir)` and `MINLPNotSupportedError` |
| `src/cli.py` | Call `validate_continuous(...)` before KKT/emit; map the exception to `EXIT_MINLP_OUT_OF_SCOPE`; honor `--allow-discrete` |
| `scripts/gamslib/batch_translate.py` | Catch the exception, record `pipeline_status: skipped` |
| `tests/unit/translate/test_validate_continuous.py` (new) | Synthetic minimal IRs covering: BINARY var, INTEGER var, SOS1 set, `solve_type=MINLP` with no discrete vars, plain NLP (no error) |

---

## Issue 3: Convexity Verifier Already Excludes — Tighten The Reason String

### Root Cause

`scripts/gamslib/verify_convexity.py:334` excludes any model with
`gamslib_type ∉ {"LP", "NLP", "QCP"}` with the message
`"Model type {model_type} excluded from corpus"`. This catches MINLP
correctly, but the reason string is generic: it doesn't tell
downstream consumers *why* (out-of-scope vs infeasible vs license).

### Fix Strategy

Replace the generic "excluded from corpus" with a specific reason
keyword (`minlp_out_of_scope`, `mip_out_of_scope`,
`miqcp_out_of_scope`, etc.). This becomes the canonical taxonomy that
`pipeline_status.reason` (from Issue 1) and `MINLPNotSupportedError`
(from Issue 2) reuse — one source of truth for exclusion reasons.

### Files

| File | Change |
|------|--------|
| `scripts/gamslib/verify_convexity.py` | Map model-type → reason keyword; emit on the `convexity.reason` field |
| `scripts/gamslib/error_taxonomy.py` | Add the exclusion-reason enum |

---

## Phase Plan

### Phase 0 — Audit Current State (30 min)

1. Run a one-off script that walks `gamslib_status.json` and reports:
   - Models where `convexity.status == "excluded"` *and* downstream
     pipeline blocks (`nlp2mcp_parse`, `nlp2mcp_translate`,
     `mcp_solve`) are populated. Expected: feedtray + similar
     stragglers.
   - Models where the cataloged `gamslib_type` ∈ `{"NLP", "QCP"}`
     but the source contains `Binary Variable(s)` / `Integer
     Variable(s)` / `solve … using minlp|mip|...`. These are the
     mis-cataloged MINLPs hiding behind the `gamslib_type` filter.
2. Save the audit list as `docs/planning/EPIC_4/SPRINT_24/AUDIT_MINLP_LEAKAGE.md`.

### Phase 1 — Translator Guard (1 h)

1. Implement `validate_continuous()` and `MINLPNotSupportedError`.
2. Wire into `src/cli.py` with the new exit code.
3. Add unit tests covering all four discrete `VarKind`s + the
   `solve_type ∈ {MIP, MINLP, ...}` paths.
4. Run `make test` — expect the translator to start refusing any
   MINLP fixture (none of the existing pipeline tests should hit
   this, but verify).

### Phase 2 — Status JSON Migration (45 min)

1. Write `migrate_schema_v2.2.0.py` (mirroring the
   `migrate_schema_v2.1.0.py` pattern):
   - For every excluded model: replace pipeline-stage blocks with the
     unified `pipeline_status: skipped` block.
   - For every model where source-derived MINLP signal disagrees with
     `gamslib_type`: rewrite `gamslib_type` and stash original under
     `original_gamslib_type`.
   - Bump `schema_version` to `2.2.0`; update `updated_date`.
2. Apply to `data/gamslib/gamslib_status.json`.
3. Update `scripts/gamslib/db_manager.py` and reporting scripts to
   consume the new field.

### Phase 3 — Verify Hygiene (30 min)

```bash
# Direct CLI now refuses to translate feedtray
.venv/bin/python -m src.cli data/gamslib/raw/feedtray.gms -o /tmp/x.gms
echo "exit=$?"
# Expected: exit=3 (EXIT_MINLP_OUT_OF_SCOPE) and a clear message naming `yf`

# Batch pipeline records skip without producing an MCP file
.venv/bin/python scripts/gamslib/batch_translate.py --model feedtray
# Expected: feedtray reported as skipped/minlp_out_of_scope; no /tmp file

# JSON entry is clean
python -c "
import json
db = json.load(open('data/gamslib/gamslib_status.json'))
ft = next(m for m in db['models'] if m['model_id'] == 'feedtray')
assert 'nlp2mcp_parse' not in ft
assert 'nlp2mcp_translate' not in ft
assert 'mcp_solve' not in ft
assert ft['pipeline_status']['status'] == 'skipped'
assert ft['pipeline_status']['reason'] == 'minlp_out_of_scope'
assert ft['gamslib_type'] == 'MINLP'
print('OK')
"

# No regressions in the test suite
make test
```

### Phase 4 — Pipeline Retest & Sprint Log (15 min)

1. `.venv/bin/python scripts/gamslib/run_full_test.py --only-parse --quiet`
   — confirm parse/translate/solve metrics unchanged for the in-scope
   models; MINLP models now contribute to a separate "skipped" tally.
2. Update `docs/planning/EPIC_4/SPRINT_24/SPRINT_LOG.md` with the
   audit numbers and the schema bump.

---

## Success Criteria

- [ ] Direct `python -m src.cli ... feedtray.gms` refuses to emit an
      MCP file and exits with `EXIT_MINLP_OUT_OF_SCOPE` (3),
      printing a clear diagnostic naming `yf` and `solve_type=MINLP`.
- [ ] `data/gamslib/gamslib_status.json → feedtray` has:
      `gamslib_type: "MINLP"`, `original_gamslib_type: "NLP"`,
      `pipeline_status.status: "skipped"`,
      `pipeline_status.reason: "minlp_out_of_scope"`,
      and no `nlp2mcp_parse` / `nlp2mcp_translate` / `mcp_solve`
      blocks.
- [ ] All other excluded MINLP/MIP models in the corpus have the same
      structure (consistency sweep).
- [ ] `verify_convexity.py` emits `reason: minlp_out_of_scope` (or the
      appropriate keyword) for any non-LP/NLP/QCP model.
- [ ] Pipeline metrics report MINLP-skipped models in their own
      bucket, not as failures.
- [ ] `make test` passes; no pipeline-stage regressions on in-scope
      models.

---

## Recommended Fix Order

1. **Phase 0** — audit and quantify the leakage scope. Without this,
   the schema migration risks missing siblings.
2. **Phase 1** — translator guard. Cheap, defense-in-depth, blocks
   all future leaks regardless of how the input arrives.
3. **Phase 2** — status JSON migration. Cleans up the existing
   stragglers in one pass.
4. **Phase 3** — verify hygiene end-to-end.
5. **Phase 4** — pipeline retest, sprint log entry.

---

## Risks and Open Questions

- **Catalog disagreement.** GAMSlib catalogs feedtray as `"NLP"` even
  though the source is MINLP. The audit (Phase 0) will surface
  similar mis-cataloged models. Trusting the *source* over the
  *catalog* is the right policy — record both for traceability.
- **Schema bump.** Going to `2.2.0` is a database-format change.
  Make sure `db_manager.py` and any consumers handle both 2.1 and
  2.2 during the transition (or run the migration eagerly on load).
- **Hidden discrete variables.** `Binary Variable yf(i);` is easy to
  detect statically. SOS sets and `$ifthen`-gated discrete blocks may
  evade an IR-only check. The combined gate (IR `VarKind` *or*
  `solve_type`) covers the realistic cases; SOS-via-macro remains a
  theoretical gap to revisit if it shows up in the corpus.
- **No relaxation, period.** This plan deliberately omits any binary
  relaxation, fixed-binary substitution, or MPEC re-encoding path.
  Those are different translator classes and are not in scope for
  nlp2mcp.

---

## Related

- `scripts/gamslib/verify_convexity.py:334` — existing exclusion
  gate that already correctly classifies non-LP/NLP/QCP as `excluded`.
- `scripts/gamslib/batch_parse.py:280–283` — pre-existing convexity
  filter that the batch pipeline relies on; this plan adds a second
  line of defense at the translator itself.
- `src/ir/parser.py:3588` — `model.solve_type` capture that the new
  guard reads.
- `src/ir/symbols.py:32–40` — `VarKind` enum used by the new guard.
- Other in-corpus MINLPs (to be enumerated by Phase 0 audit) get the
  same treatment via the same migration; feedtray is the pilot, not
  the only target.

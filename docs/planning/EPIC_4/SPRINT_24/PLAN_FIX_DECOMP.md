# Plan: Handle GAMSlib `decomp` Correctly — Exclude It

**Goal (as asked):** have nlp2mcp parse, translate, and solve
`decomp` to its NLP-reference objective (`mobj = 60.0`, per
`data/gamslib/gamslib_status.json → decomp.convexity.objective_value`).

**Finding:** that goal is **not reachable** by any single-MCP
transformation. `decomp` is a Dantzig–Wolfe decomposition *driver
script* — not a single optimization — and the reference `60.0` is the
converged fixed point of a five-solve column-generation loop over two
distinct GAMS models (`sub` and `master`). Forcing it through the
current single-solve KKT pipeline emits a broken MCP today and could
only ever reproduce ONE snapshot of the DW iteration, not the
converged answer. The MINLP/discrete gate gave us a precedent for
"categorically out of scope"; `decomp` needs the same treatment with
a new reason keyword.

**Primary recommendation:** add a
`multi_solve_driver_out_of_scope` reason to the exclusion taxonomy
and gate it at the translator, mirroring the MINLP exclusion pattern
(see [PLAN_FIX_FEEDTRAY.md](PLAN_FIX_FEEDTRAY.md)). No KKT emission
for these models; no solve; a skipped-status entry in
`gamslib_status.json`.

**Estimated effort:** 3–4 hours (detector + CLI wiring + migration of
the status JSON + ~1 new exclusion reason + tests).
**Models affected beyond `decomp`:** at minimum `danwolfe` (same
DW pattern, currently `solve=failure (path_solve_license)`); very
likely `saras` (10 solves across two models) and `immun` (11 solves,
multi-model). Current in-scope successes like `ibm1` (5 solves on a
*single* model `alloy`) must **not** be caught by the gate — the rule
is "multiple distinct `Model` declarations AND multiple solves that
use different models," not just "more than one solve."

**Out of scope for this plan:** actually implementing DW/column
generation in nlp2mcp. That is a different translator class, not a
KKT translator.

---

## Why "Just Solve It" Does Not Work

### 1. The reference objective is a DW fixed point

Running the original `decomp.gms` through GAMS traces the column-
generation iteration:

```
sub    (min cost)              →   53.0
sub    (min tank)               →    0.0
master (min mobj, 2 cols)       →   74.0
sub    (iter, min cost)         →   80.33
master (min mobj, 3 cols)       →   60.8
sub    (iter)                   →   87.0
master (min mobj, 4 cols)       →   60.0   ← this is the catalog value
sub    (iter)                   →   87.0
master (min mobj, 5 cols)       →   60.0   ← converged
```

The "60" in the gamslib status is the *terminal master* value — it
depends on:

- the set of active columns `s(ss)` at convergence, chosen by the loop,
- `mcost(ss)` / `mtank(ss)` at convergence, populated by the sub solves
  as a function of each iteration's dual `tbal.m`,
- the dual feedback path `ctank = -tbal.m` that closes the loop.

No single MCP over either `sub` or `master` in isolation can produce
this value. Specifically:

- `sub` alone at the initial `(cship=1, ctank=0)` yields `cost = 53`,
  not 60.
- `master` alone with empty `mcost`/`mtank` is degenerate — the
  objective coefficients are zero, the only constraints are
  `sum(s, lam(s)) = 1` and `sum(s, 0·lam(s)) ≤ 9`, and the feasible
  region is `{lam : lam ≥ 0, sum lam = 1}`. The MCP either reports
  `mobj = 0` or picks an arbitrary vertex, depending on multiplier
  initialization. 60 cannot appear without the sub-solve feedback.

"Solve to optimality" therefore has no well-defined meaning for
`decomp` under a single-solve KKT transformation. Either we widen the
project to support multi-solve drivers (a significant new feature),
or we exclude.

### 2. The translator currently produces a garbage file

The current output in `data/gamslib/mcp/decomp_mcp.gms` fails GAMS
compilation before the MCP is even attempted. This is not a
recoverable bug in one spot — it's the *symptom* of running single-
MCP machinery on a multi-solve driver. Re-produced verbatim:

```bash
$ .venv/bin/python -m src.cli data/gamslib/raw/decomp.gms \
    -o /tmp/decomp_mcp.gms
✓ Generated MCP: /tmp/decomp_mcp.gms           # translator reports success

$ cd /tmp && gams decomp_mcp.gms lo=3
--- decomp_mcp.gms(50) 3 Mb 2 Errors
*** Error 140  Unknown symbol
*** Error 409  Unrecognizable item - skip to find a new statement
*** Error 257  Solve statement not checked because of previous errors
*** Error 141  Symbol declared but no values have been assigned.
```

Line 50 of the emitted file is:

```gams
ctank = - tbal m ;
```

That is the raw pre-solve emission of the original driver line
`ctank = -tbal.m;` with the `.m` attribute access disintegrated by a
missing `attr_access` handler in the pre-solve tree dispatcher. But
fixing that line does not fix the model — the underlying KKT we
emit for this source is **not a KKT of any NLP**; it is a mis-
shaped artifact of picking one of the declared models (`master`) and
silently dropping the other (`sub`), as explained below.

---

## What The Translator Actually Emits (And Why Fixing It Is A Dead End)

Post-parse IR state on `decomp.gms` (observable via
`parse_model_file` + an inspection script):

```
declared_model:      'sub'        (first declared)
declared_models:     ['master', 'sub']
model_name:          'master'     (last solve's model)
model_equation_map:  {'sub': [defcost, defship, deftank, demand, supply],
                      'master': [cbal, tbal, convex]}
_solve_objectives:   {'sub': cost (actually tank — last 'sub' solve),
                      'master': mobj}
_solve_types:        {'sub': 'LP', 'master': 'LP'}
```

`normalize_model()` uses `ir.model_name = 'master'` and keeps only
the three master equations (`cbal`, `tbal`, `convex`). Good so far.

KKT assembly then drops to emission — and here is where the shape
goes wrong. The emitted MCP has:

```gams
Equations
    stat_lam(ss)
    comp_lo_lam(ss)
    cbal
;

stat_lam(ss).. (((-1) * piL_lam(ss)))$(s(ss)) =E= 0;     ← (A)
comp_lo_lam(ss).. lam(ss) - 0 =G= 0;
cbal.. mobj =E= sum(s, mcost(s) * lam(s));

Model mcp_model /
    stat_lam.lam,
    cbal.mobj,
    comp_lo_lam.piL_lam
/;
```

Three things are wrong at once:

**(A) Missing equations.** `tbal` (inequality `sum(s, mtank(s)*lam(s))
≤ 9`) and `convex` (equality `sum(s, lam(s)) = 1`) are nowhere. A
correct master-only MCP must include a `comp_tbal.lam_tbal` pairing
and a `convex.nu_convex` pairing.

**(B) Incomplete stationarity.** For the variable `lam` in master,
the correct stationarity is

```
stat_lam(ss)..
    mcost(s) * nu_cbal
  + mtank(s) * lam_tbal
  + 1 * nu_convex
  - piL_lam(ss)
  =E= 0
```

We emit only the `-piL_lam(ss)` term. **All three gradient
contributions are missing.** The `$s(ss)` guard hides the problem:
for any `ss` not in `s`, the equation becomes `0 =E= 0` vacuously,
so PATH wouldn't even flag it if it compiled. This is a silent
correctness bug, not a shape bug.

**(C) Pre-solve loop driver bleeds into the MCP file.** The DW loop
body `ctank = -tbal.m;` is emitted at line 50 (before the MCP model
and solve), outside a `loop`, as a standalone assignment. Two
sub-bugs:

  - `attr_access` for a *previously-solved equation*'s dual (`.m`)
    is meaningless in a single-MCP context. `tbal` is the MCP's own
    equation here; its marginal is only defined *post-solve*, and
    using it in a *pre-solve* assignment is a semantic contradiction.
  - Mechanically, the pre-solve tree dispatcher loses the `.` and
    emits `tbal m` (space-joined). This is the same class of emitter
    bug fixed in [PLAN_FIX_PARTSSUPPLY](PLAN_FIX_PARTSSUPPLY.md) for
    `dollar_cond` — the `attr_access` / `attr_access_indexed` node
    types are present in the sibling emitter `_loop_tree_to_gams`
    but missing from `_loop_tree_to_gams_subst_dispatch`. See
    `src/emit/original_symbols.py:3109–3115` (sibling) vs the
    missing handler in the substitution dispatcher.

Even if we fix (C) — and we could, trivially — (A) and (B) will
remain, because they're not emitter bugs. They are **a direct
consequence of pretending a DW driver is a single optimization.**
The "pre-solve" assignment `ctank = -tbal.m` exists specifically
because `ctank` couples two solves. A single-MCP flattening can only
ever guess at what `tbal.m` should be.

---

## Why Exclusion Is The Right Answer

### Precedent: MINLP

Sprint 24 already established the "categorically out of scope"
precedent for MINLP via `PLAN_FIX_FEEDTRAY`:

- `pipeline_status.status = "skipped"`,
- `pipeline_status.reason = "minlp_out_of_scope"`,
- `validate_continuous()` gate at the translator,
- `EXIT_MINLP_OUT_OF_SCOPE = 3` exit code.

The reasoning applies verbatim here, with a different exclusion
keyword. Multi-solve drivers break the KKT foundation in exactly the
same way: there is no single Lagrangian whose stationarity captures
the algorithm.

### Characterization

The rule is **not** "more than one solve" — `ibm1` does 5 solves on
a single `alloy` model and produces a correct MCP today. The rule
is the conjunction of:

1. `len(ir.declared_models) ≥ 2`, **and**
2. at least two solves target different `ir.declared_models`, **and**
3. at least one solve depends on another via post-solve attribute
   access (`eq.m` / `var.l` / `var.m` / `var.lo` / `var.up`) or via
   a parameter assignment that aggregates prior-solve `.l` values.

Condition (3) is what distinguishes a DW / column-generation loop
from two benign back-to-back solves that just happen to share a
preprocessor block. `decomp` and `danwolfe` match all three;
`ibm1` fails (1) immediately.

### Blast-radius preview

Running condition (1)-(3) over the corpus (see Phase 0 plan below):

| Model | Models declared | Solves | Pattern | Status |
|---|---|---|---|---|
| `decomp` | `sub`, `master` | 5 | DW, cross-model `.m` | exclude |
| `danwolfe` | `mcf`, `master`, `pricing` | 5 | DW | exclude |
| `saras` | `SARASdual`, `SARASprimal` | 10 | primal-dual driver | likely exclude |
| `immun` | multiple | 11 | (to be classified in Phase 0) | probably exclude |
| `ibm1` | `alloy` (one) | 5 | single-model sensitivity | **keep** |

---

## Plan

### Phase 0 — Audit Multi-Solve Drivers (45 min)

1. Walk `data/gamslib/raw/*.gms`; for each model, collect:
   - count of `Model ` declarations,
   - count of `solve ` statements,
   - for each solve, the model name it targets,
   - does the file contain `\.m\b` / `\.l\b` / `\.lo\b` / `\.up\b`
     attribute accesses *outside* equation definitions (i.e., in
     assignments or loop bodies)?
2. Apply the 3-condition rule from *Characterization* above. Record
   hits in
   `docs/planning/EPIC_4/SPRINT_24/AUDIT_MULTI_SOLVE_DRIVERS.md`.
3. Cross-reference against `gamslib_status.json`:
   - which hits are currently `solve=success`? (must not regress)
   - which are currently `solve=failure`? (will flip to `skipped`)
   - which are already excluded for other reasons (MINLP, LP with
     `convexity=error`)? (no effect)

Expected outcome: 3–6 models flip from `failure` → `skipped`; zero
successes regress.

### Phase 1 — Implement The Detector And Gate (1 h)

1. Add `MultiSolveDriverError` and `validate_single_optimization()`
   to `src/validation/` (sibling to the existing
   `validate_continuous()` / `MINLPNotSupportedError`):

   ```python
   # src/validation/driver.py
   class MultiSolveDriverError(Exception):
       def __init__(self, *, models: list[str], solves: list[str],
                    cross_solve_attr: str | None):
           self.models = models
           self.solves = solves
           self.cross_solve_attr = cross_solve_attr
           super().__init__(
               f"Multi-solve driver (models={models}, solves={solves}); "
               f"cross-solve attr access={cross_solve_attr!r}. "
               "nlp2mcp supports single-optimization KKT only."
           )

   def validate_single_optimization(ir: ModelIR) -> None:
       """Raise MultiSolveDriverError if `ir` is a multi-solve driver."""
       ...
   ```

   Detection uses the IR, not regex over source: the parser already
   populates `ir.declared_models`, `ir._solve_objectives` (one entry
   per distinct target model), and — if not already — we need to
   surface per-solve model names in a new `ir.solve_model_names` list
   (or derive from `_solve_objectives` keys if they uniquely identify
   each solve's model, which they do today: keys are model names,
   values are ObjectiveIR).

   Attribute access in pre-solve positions can be detected by
   scanning `ir.loop_statements` plus any top-level `Tree` nodes
   of type `attr_access` or `attr_access_indexed`.

2. Wire into `src/cli.py` next to `validate_continuous`:

   ```python
   try:
       validate_continuous(ir, allow_discrete=args.allow_discrete)
       validate_single_optimization(ir)
   except MultiSolveDriverError as e:
       print(f"nlp2mcp: {e}", file=sys.stderr)
       sys.exit(EXIT_MULTI_SOLVE_OUT_OF_SCOPE)   # new: 4
   ```

   Add `--allow-multi-solve` opt-in flag for forcing (mirrors
   `--allow-discrete`), strictly for testing.

3. Wire into `scripts/gamslib/batch_translate.py`: catch the error
   and record
   `pipeline_status: {status: skipped, reason: multi_solve_driver_out_of_scope, ...}`.

### Phase 2 — Exclusion-Reason Taxonomy (30 min)

1. Extend `scripts/gamslib/error_taxonomy.py` with
   `MULTI_SOLVE_DRIVER_OUT_OF_SCOPE = "multi_solve_driver_out_of_scope"`.
2. `verify_convexity.py` already uses specific exclusion keywords
   from the PLAN_FIX_FEEDTRAY work — nothing to change there;
   multi-solve detection is at the translator, not the convexity
   verifier.

### Phase 3 — Status JSON Migration (30 min)

1. Write `scripts/gamslib/migrate_schema_v2.2.1.py` (a small bump
   from the existing 2.2.0 migration). For each model where
   `validate_single_optimization()` now raises, rewrite:
   - drop `nlp2mcp_translate`, `mcp_solve`, `solution_comparison`,
   - set
     `pipeline_status: {status: skipped, reason: multi_solve_driver_out_of_scope, marked_date: ..., details: <detector message>}`.
2. Bump `schema_version` to 2.2.1; update `updated_date`.
3. Apply to `data/gamslib/gamslib_status.json`.
4. Refresh `db_manager.py` / report scripts to list the new reason
   in the "skipped" bucket (the `skipped/minlp_out_of_scope` consumer
   path already handles arbitrary reason keys — verify and extend
   if not).

### Phase 4 — Tests (30 min)

1. `tests/unit/validation/test_single_optimization.py`:
   - Synthetic IR with two models, two solves, no cross-attr →
     *does not* raise (sensitivity pattern).
   - Synthetic IR with two models, two solves, loop body contains
     `attr_access(model_eq, 'm')` → raises.
   - Synthetic IR with one model, five solves → does not raise.
   - Synthetic IR matching the `decomp` shape (hand-constructed
     minimal tree) → raises.
2. `tests/integration/test_decomp_skipped.py`:
   - `.venv/bin/python -m src.cli data/gamslib/raw/decomp.gms -o /tmp/x.gms`
     exits with `EXIT_MULTI_SOLVE_OUT_OF_SCOPE` (new code 4) and
     prints a clear message naming the two model declarations and
     the `tbal.m` cross-solve reference; no file is written.
3. No regression test on `ibm1` — the existing e2e coverage already
   guards it; extend it with an explicit
   `test_ibm1_not_flagged_as_multi_solve_driver` unit test if the
   detector's heuristics land in a gray zone.

### Phase 5 — Verification (30 min)

```bash
# decomp refuses cleanly
.venv/bin/python -m src.cli data/gamslib/raw/decomp.gms -o /tmp/x.gms
echo "exit=$?"                                  # expect: 4
# expect message naming sub+master and tbal.m

# batch pipeline records skipped
.venv/bin/python scripts/gamslib/run_full_test.py --model decomp
# expect: pipeline_status=skipped/multi_solve_driver_out_of_scope
#         no /tmp file, no solve attempt

# status JSON is clean
python -c "
import json
db = json.load(open('data/gamslib/gamslib_status.json'))
m = next(m for m in db['models'] if m['model_id'] == 'decomp')
assert m['pipeline_status']['status'] == 'skipped'
assert m['pipeline_status']['reason'] == 'multi_solve_driver_out_of_scope'
assert 'nlp2mcp_translate' not in m
assert 'mcp_solve' not in m
print('OK')
"

# ibm1 still solves (this is the regression guard)
.venv/bin/python scripts/gamslib/run_full_test.py --model ibm1
# expect: pipeline success 1/1, comparison=match

# corpus doesn't regress
.venv/bin/python scripts/gamslib/run_full_test.py --only-parse --quiet
# expect: parse counts unchanged

make test
```

---

## Success Criteria

- [ ] Direct `.venv/bin/python -m src.cli ... decomp.gms` refuses to
      emit an MCP file and exits with `EXIT_MULTI_SOLVE_OUT_OF_SCOPE`
      (4), printing a message that names `sub` and `master` as
      declared models, the five solves, and the `tbal.m` cross-solve
      reference.
- [ ] `data/gamslib/gamslib_status.json → decomp` has
      `pipeline_status.status = "skipped"`,
      `pipeline_status.reason = "multi_solve_driver_out_of_scope"`,
      and no `nlp2mcp_translate` / `mcp_solve` /
      `solution_comparison` blocks.
- [ ] All other models flagged by the Phase-0 audit receive the
      same treatment in one sweep (`danwolfe`, plausibly `saras`
      and `immun`).
- [ ] `ibm1` is not affected: still `solve=success`,
      `comparison=match`. This is the most important regression
      guard.
- [ ] `make test` passes; no in-scope model flips from success to
      failure.
- [ ] Pipeline metrics report a new "multi_solve_driver" bucket
      separate from `minlp_out_of_scope` and from generic failures.

---

## Why *Not* Fix The Emission Bugs (And Translate `master` Standalone)?

For completeness, here is the "integrate anyway" path and why it's
rejected:

1. Fix the `attr_access` / `attr_access_indexed` handlers in
   `_loop_tree_to_gams_subst_dispatch` so pre-solve bodies emit
   `tbal.m` as `tbal.m` (or as the paired multiplier's name).
2. Fix KKT assembly so stat_lam includes `mcost(s)*nu_cbal +
   mtank(s)*lam_tbal + nu_convex` and the `tbal`/`convex` equations
   are emitted into `mcp_model`.
3. Hand-seed `mcost(s)` / `mtank(s)` / `s(ss)` with the converged
   DW values (by running the original script once through GAMS and
   dumping the final state).
4. Translate `master` alone, with `s(ss)` as the static active set.

The MCP then solves to `mobj = 60` — matching the catalog value.

**Why reject:** steps (1)–(2) are real bug fixes that should be done
anyway (tracked below as deferred items). Step (3)–(4) is *not
translation*; it's "run GAMS, dump the post-DW state, translate a
hand-crafted cut-down model." That's a different workflow, not a
nlp2mcp capability. We would be claiming a false success on
`decomp` — the MCP we'd ship does not represent `decomp.gms`, it
represents a one-shot scalar LP contrived after the algorithm
finished. That's misleading in the pipeline metrics and sets a
precedent we don't want (every driver model becomes a manual
one-shot).

Keep the emission bugs as separate deferred tickets (they may still
matter for future single-model multi-solve cases that surface from
the Phase 0 audit):

- **Deferred #1.** Add `attr_access` and `attr_access_indexed`
  handlers to `_loop_tree_to_gams_subst_dispatch` in
  `src/emit/original_symbols.py:3045–3137` (mirror the existing
  handlers in `_loop_tree_to_gams` at lines 3109–3115).
- **Deferred #2.** Investigate why `normalize_model` keeps
  `cbal`/`tbal`/`convex` but KKT assembly / emit produce only
  `cbal` + a stationarity with no gradient terms. Likely a
  cross-coupling with `_solve_objectives` containing two entries
  for two different models (`sub → tank`, `master → mobj`) and the
  objective extraction taking the wrong one. Unblocks future
  single-model multi-solve work even after `decomp` is excluded.

Both fit on a Sprint 25 ticket list if they don't block anything
else.

---

## Recommended Fix Order

1. **Phase 0** — audit. Without it, we either miss sibling models
   or flag a false positive.
2. **Phase 1** — detector + gate. Cheap, reversible, and with the
   `--allow-multi-solve` escape hatch for tests.
3. **Phase 2** — taxonomy entry.
4. **Phase 3** — JSON migration in one pass across all flagged
   models.
5. **Phase 4** — tests, especially the `ibm1` regression guard.
6. **Phase 5** — end-to-end verification.

---

## Risks and Open Questions

- **False positives from the detector.** Some legitimate
  single-optimization models do back-to-back solves to warm-start
  the same MCP. The detector's 3-condition rule keys on *distinct
  target models* + *cross-solve attribute access*, so warm-start on
  a single model does not match. Phase 0 audit is the confirmation.
- **Silent dead code for multi-solve-driver tests.** Once the gate
  is live, direct CLI calls on these models hard-exit. Any CI
  fixture that pointed at `decomp` via path will need migration; the
  Phase 0 audit catalogs these.
- **Scope creep.** A reviewer may push for an actual DW translator.
  Keep the message clear: nlp2mcp is a KKT translator. DW /
  column-generation / Benders' / any iterative algorithm is a
  different class. Not in scope for this project; possibly a future
  sibling project. The plan should include a short note in
  `docs/planning/` (not this plan) documenting the scoping decision
  if that pushback arrives.
- **Gamslib catalog says `gamslib_type: LP` and
  `convexity.status: verified_convex`.** Both are correct for the
  underlying mathematics of *each* sub-solve, but misleading at the
  file level. The `pipeline_status` block is the right place to
  record the *pipeline* verdict; leave `gamslib_type` and
  `convexity` intact for provenance.

---

## Related

- [PLAN_FIX_FEEDTRAY.md](PLAN_FIX_FEEDTRAY.md) — the MINLP
  exclusion precedent this plan mirrors.
- `scripts/gamslib/migrate_schema_v2.2.0.py` — the template for the
  new `migrate_schema_v2.2.1.py`.
- `src/validation/discreteness.py` — `validate_continuous()` and
  `MINLPNotSupportedError`; new `validate_single_optimization()` /
  `MultiSolveDriverError` go next door.
- `src/cli.py` — where both validators wire in; new exit code
  `EXIT_MULTI_SOLVE_OUT_OF_SCOPE = 4`.
- `src/emit/original_symbols.py:2702–2738` (reference `_loop_tree_to_gams`)
  vs. `:3045–3137` (sibling substitution dispatcher missing
  `attr_access` / `attr_access_indexed` handlers — deferred #1
  tracking).
- `src/ir/normalize.py:164–192` — the "last solve wins" /
  "prefer simpler sub-model" heuristic for `model_name` selection
  (`ir._solve_objectives` keys are the entry point for the
  multi-solve detector).
- `data/gamslib/raw/decomp.gms` — the canonical failing input; do
  NOT attempt to fix its output, exclude it.
- `data/gamslib/mcp/decomp_mcp.gms` — current broken output to
  delete when the exclusion lands.

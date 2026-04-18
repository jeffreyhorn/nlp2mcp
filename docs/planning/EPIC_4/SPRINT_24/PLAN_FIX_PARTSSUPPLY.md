# Plan: Make `partssupply` Parse, Translate, and Solve To Optimality

**Goal:** End-to-end success of the nlp2mcp pipeline on GAMSlib
`partssupply` (SEQ=404, "Parts Supply Problem"): parse the source,
emit a GAMS-valid MCP file, and have PATH return a solution whose
`Util.l` matches the original NLP's optimum (≈ 0.9167 for the default
scenario `--nsupplier=2 --nsamples=1 --modweight=0`).

**Status today:** parse ✓, translate "✓" (file emitted) but the
emitted file is **not GAMS-valid** — it fails compilation at line 55
with Error 445 ("More than one operator in a row") before the solve
is even checked. In addition, the preprocessor silently takes the
wrong `$ifThen/$elseIf/$else` branch, so even if the 445 were fixed
the MCP would solve a different NLP (`theta = ord(i)/card(i)` from
the `$else` fallback) than the one the GAMSlib driver intends
(`theta = {0.2, 0.3}` from the `$elseIf %nsupplier% == 2` branch).

**Estimated effort:** 3–4 hours (two localized bug fixes + tests +
pipeline retest).
**Models affected beyond `partssupply`:** both bugs are general.
Any model that uses
- `$ifThen / $elseIf` (as distinct from the single-line `$if`), or
- A `$`-conditional inside a pre-solve loop body

will see identical failures. Fixing here pays off across the corpus;
the audit in Phase 0 quantifies the blast radius.

**Out of scope:** MINLP/MIP exclusion (handled by
[PLAN_FIX_FEEDTRAY.md](PLAN_FIX_FEEDTRAY.md)); multi-sample Monte
Carlo mode (`--nsamples > 1`) — the default driver picks
`nsamples=1` which takes a single deterministic sample; we only need
that path for the solve-to-optimality success criterion.

---

## Pre-fix Reproduction

```bash
# 1) Translate.  Succeeds textually; emits MCP file.
.venv/bin/python -m src.cli data/gamslib/raw/partssupply.gms \
    -o /tmp/partssupply_mcp.gms
# ⚠️  Convexity Warnings: W301 (rev is nonlinear equality)
# ✓ Generated MCP: /tmp/partssupply_mcp.gms

# 2) Compile with GAMS.  Fails at line 55.
cd /tmp && gams partssupply_mcp.gms lo=3
# *** Error 445 in /tmp/partssupply_mcp.gms
#     More than one operator in a row. You need to use parenthesis
#       ...  sum(i$not x, ..)   ->  sum(i$(not x),..)
# *** Error 257 ... Solve statement not checked because of previous errors
# *** Error 141 ... Symbol declared but no values have been assigned (nlp2mcp_obj_val)
```

The offending emitted line (file line 55):

```gams
icweight(i) = theta(i) $ not 0 + 1 - theta(i) + sqr(theta(i)) $ 0 ;
```

The original source (post macro expansion, with default
`%modweight%=0`):

```gams
icweight(i) = theta(i)$(not 0) + (1 - theta(i) + sqr(theta(i)))$(0);
```

The translator has **stripped two pairs of parentheses**:

1. `$(not 0)` → `$ not 0` — GAMS reads `not 0 + 1 - theta(i) + ...`
   as a single broken expression (`not` cannot be adjacent to `+`).
2. `(1 - theta(i) + sqr(theta(i)))$(0)` → `1 - theta(i) + sqr(theta(i)) $ 0`
   — the grouping around the LHS of the `$` is gone, so parsing
   associates `sqr(theta(i)) $ 0` where `(1-theta+sqr(theta))` was
   intended.

Observed in `partssupply_mcp.lst` lines 55 / 445 error point.
Confirmed by re-running `gams` on the file.

---

## Pre-fix Reproduction (Semantic Bug)

The generated MCP file also mis-initializes `theta` and `p`:

```gams
theta(i) = ord(i) / card(i);    // from $else fallback — wrong
p(i)     = 1      / card(i);    // from $else fallback — wrong
```

For `%nsupplier%=2` the correct branch is `$elseIf %nsupplier% == 2`,
which sets `theta = {0.2, 0.3}` via `Parameter theta(i) / 1 0.2, 2 0.3 /`
(and analogously for `p`). Running the original NLP under GAMS
yields `Util.l = 0.9167`; running the **paren-fixed** MCP (theta still
wrong) yields `Util.l = 0.297` — the model is feasible and PATH
returns a KKT point, but of a *different* NLP. A "matched solve" is
therefore not just about GAMS-compiling the file; it requires the
right-branch `theta` and `p`.

Confirmed by inspecting the preprocessor output
(`preprocess_text(src)`):

```gams
* [Conditional: $ifThen 2 == 1]
* [Conditional: $if 0 == 0 Parameter theta(i) / 1 0.2 /;]
* [Conditional: $if 0 == 1 Parameter theta(i) / 1 0.3 /;]
* [Excluded: Parameter p(i) / 1 1 /;]
* [Conditional: $elseIf 2 == 2]
* [Excluded: Parameter]         ← should be LIVE (condition is true)
   * [Excluded: theta(i) / 1 0.2, 2 0.3 /]
   * [Excluded: p(i)     / 1 0.2, 2 0.8 /;]
* [Conditional: $elseIf 2 == 3]
...
* [Conditional: $else]
theta(i) = ord(i)/card(i);      ← emitted, but should be DEAD
p(i)     =      1/card(i);
* [Conditional: $endIf]
```

Every `$ifThen/$elseIf` block is marked "Excluded" (i.e., evaluated
to false), and the `$else` falls through. This is backwards.

---

## Issue 1: Tree-Emitter For Pre-Solve Assignments Drops `$`-Parens

### Root Cause

`src/emit/original_symbols.py` has two sibling tree-to-GAMS
emitters:

- `_loop_tree_to_gams(node)` — used when emitting whole `loop` blocks
  back to GAMS text. Handles `dollar_cond` and `dollar_cond_paren`
  with dedicated cases (lines 2702–2711):

  ```python
  # dollar_cond: term $ term
  if data == "dollar_cond":
      lhs = _loop_tree_to_gams(node.children[0])
      rhs = _loop_tree_to_gams(node.children[1])
      return f"{lhs}${rhs}"
  # dollar_cond_paren: term $ (expr) or term $ [expr]
  if data == "dollar_cond_paren":
      lhs = _loop_tree_to_gams(node.children[0])
      rhs = _loop_tree_to_gams(node.children[1])
      return f"{lhs}$({rhs})"
  ```

- `_loop_tree_to_gams_subst_dispatch(node, subst)` — the variant
  called by `emit_pre_solve_param_assignments()` (line 2991) when it
  needs to emit the pre-solve parameter assignments of a
  `loop(t, ...; solve ...)` block with the loop index `t` substituted
  by a literal. It has handlers for `binop`, `unaryop`, `condition`,
  `assign`, `expr`, etc. — **but not for `dollar_cond` or
  `dollar_cond_paren`** (lines 3047–3137).

Consequence: when a `$`-conditional lives in a pre-solve assignment,
the substitution emitter falls through to the generic
`" ".join(emit(c) for c in node.children)` on the last line of
`_loop_tree_to_gams_subst_dispatch` (line 3137). That joins
`term DOLLAR term` children with spaces and silently discards the
silent `"("` / `")"` tokens that `dollar_cond_paren` consumed during
parsing. Result: `theta(i)$(not 0)` becomes `theta(i) $ not 0`, and
`(1 - theta(i) + sqr(theta(i)))$(0)` becomes
`1 - theta(i) + sqr(theta(i)) $ 0`.

### Why The Main `expr_to_gams` Path Is Not Used Here

`src/emit/expr_to_gams.py:656–673` already renders `DollarConditional`
IR nodes correctly, always wrapping the condition in `(...)` (Issue
#1003). The pre-solve parameter assignment path, however, operates
on the **raw Lark parse tree** (it needs to preserve arbitrary
statement shapes including `$`-conditional assigns, `sum`/`prod`
domains, etc., without round-tripping through IR), so it never sees
the `DollarConditional` IR node. This is by design — but the tree
emitter needs feature parity with `_loop_tree_to_gams` for the
`$`-condition cases.

### Fix Strategy

Add the two missing handlers to
`_loop_tree_to_gams_subst_dispatch`, mirroring the implementation in
`_loop_tree_to_gams`:

```python
# dollar_cond: term $ term  →  term${term}
if data == "dollar_cond":
    lhs = _tree_to_gams_subst(node.children[0], subst)
    rhs = _tree_to_gams_subst(node.children[1], subst)
    return f"{lhs}${rhs}"

# dollar_cond_paren: term $ (expr) / term $ [expr]  →  term$(expr)
if data == "dollar_cond_paren":
    lhs = _tree_to_gams_subst(node.children[0], subst)
    rhs = _tree_to_gams_subst(node.children[1], subst)
    return f"{lhs}$({rhs})"
```

Place before the generic `binop`/`unaryop`/fallback joins so the
specific rule names win. Also consider factoring `_loop_tree_to_gams`
and `_loop_tree_to_gams_subst_dispatch` — they are 90% identical —
but a defensive refactor is out of scope for this plan; the minimal
fix is two copy-paste handlers.

**Also audit for related silent-token losses.** The same dispatcher
lacks handlers for `bracket_expr` and `brace_expr` (the `[...]` /
`{...}` atom variants at grammar lines 774–775). `_loop_tree_to_gams`
has them at lines 2713–2717. If any pre-solve assignment uses
bracket/brace expressions, the same "parens lost" bug reappears.
Add those while fixing Issue 1.

Missing handlers to add (all already present in
`_loop_tree_to_gams`):

| Rule | Emit pattern |
|---|---|
| `dollar_cond` | `{lhs}${rhs}` |
| `dollar_cond_paren` | `{lhs}$({rhs})` |
| `bracket_expr` | `[{inner}]` |
| `brace_expr` | `{{{inner}}}` |
| `yes_cond` / `no_cond` | `yes{cond}` / `no{cond}` |
| `yes_value` / `no_value` | `yes` / `no` |

### Files

| File | Change |
|---|---|
| `src/emit/original_symbols.py` | Add the six missing rule handlers to `_loop_tree_to_gams_subst_dispatch` (around line 3116, before the `binop`/`unaryop` clause). |
| `tests/unit/emit/test_pre_solve_dollar_condition.py` (new) | Unit test: synthesize a minimal `ModelIR` with a `loop(t, p(i)=pt(i,t); icw(i) = a(i)$(c1) + (1-a(i))$(c2); solve m...)` and assert that `emit_pre_solve_param_assignments(ir)` produces `a(i)$(c1) + (1-a(i))$(c2)` — parens preserved around both condition and LHS-group. Cover `dollar_cond`, `dollar_cond_paren`, `bracket_expr` variants. |
| `tests/integration/translate/test_partssupply_translate.py` (new) | Integration test: translate `partssupply.gms`, grep the output for `"$ not"` / `"$ 0 ;"` patterns and fail if present; assert the `icweight(i) = ...` line parses under GAMS (e.g., run `gams --error-check-only` if available, otherwise string-level shape assertion). |

---

## Issue 2: Preprocessor Fails On `$ifThen` / `$elseIf`

### Root Cause

`src/ir/preprocessor.py`:

- **`process_conditionals()` at lines 205–308** recognizes the
  directive boundaries (`startswith("$if")`, `startswith("$elseif")`,
  etc.), so `$ifThen 2 == 1` *is* pushed onto the conditional stack
  as a block-style `$if`.

- **`_evaluate_if_condition()` at lines 404–496** is what fails. Its
  regexes all begin with `\$if\s+…` (three literal characters + a
  mandatory space). Crucially:

  - `$ifThen 2 == 1` — the 4th char is `T` (from `ifThen`), not
    whitespace. **No regex matches. Function returns `False`** (the
    conservative default at line 496).
  - Normalization at line 425 is `re.sub(r"^\$if[ie]", "$if", ...)`
    — it only handles `$ifI` / `$ifE`, not `$ifThen`.

  Every `$ifThen`/`$ifThenI`/`$ifThenE` block therefore evaluates to
  `False` regardless of its condition.

- **`$elseIf` handling at line 270** uses a case-sensitive
  `stripped.replace("$elseif", "$if", 1)`. The source text retains
  its original case (`$elseIf`), so the replace is a no-op. The
  resulting string is then passed to `_evaluate_if_condition`, which
  fails to match any pattern starting with `$elseIf` and returns
  `False`. Every `$elseIf` in mixed-case form (which is what GAMSlib
  authors typically write) also evaluates to `False`.

Combined effect on `partssupply.gms`:
- `$ifThen %nsupplier% == 1` → False (regex never matches)
- `$elseIf %nsupplier% == 2` → False (regex + case-sensitive replace)
- `$elseIf %nsupplier% == 3` → False (same)
- `$else` → fires (because no earlier branch "matched"), emitting
  the `ord(i)/card(i)` fallback

…exactly the pattern seen in the preprocessor dump above.

### Fix Strategy

Two surgical changes, both in `src/ir/preprocessor.py`:

1. **Normalize `$ifThen` → `$if` before evaluation** in
   `_evaluate_if_condition` (and in `process_conditionals`
   wherever the directive text is matched). Extend the existing
   normalization at line 425:

   ```python
   # Normalize $ifI, $ifE, $ifThen, $ifThenI, $ifThenE to $if
   stripped = re.sub(
       r"^\$if(?:then)?[ie]?",
       "$if",
       stripped,
       count=1,
       flags=re.IGNORECASE,
   )
   ```

   The same normalization must also apply where directive boundaries
   are detected so that an inline `$ifThen cond stmt` is handled in
   parity with an inline `$if cond stmt`. In practice `$ifThen` is
   always block-style (`$endIf`-closed), so block-mode is the common
   path, but the normalization should be symmetric to avoid a
   surprise later.

2. **Make the `$elseif` replace case-insensitive** at line 270:

   ```python
   # Replace the directive keyword regardless of author casing
   # (GAMSlib sources use $elseIf, $elseif, $ELSEIF, etc.)
   rewritten = re.sub(
       r"^\$elseif",
       "$if",
       stripped,
       count=1,
       flags=re.IGNORECASE,
   )
   new_condition = _evaluate_if_condition(rewritten, macros)
   ```

Semantics after the fix, under default `%nsupplier%=2 %modweight%=0`:

- `$ifThen %nsupplier% == 1` → `$if 2 == 1` → `False` ✓
- `$elseIf %nsupplier% == 2` → `$if 2 == 2` → `True` ✓ — **this
  branch now emits** `Parameter theta(i) / 1 0.2, 2 0.3 /` and
  `p(i) / 1 0.2, 2 0.8 /`.
- `$elseIf %nsupplier% == 3` → `$if 2 == 3` → `False` ✓
- `$else` → `not (False or True or False)` → `False` ✓ — fallback
  correctly skipped.

### Files

| File | Change |
|---|---|
| `src/ir/preprocessor.py` | Extend normalization regex at line 425 to `\$if(?:then)?[ie]?`; rewrite line 270 to use case-insensitive `re.sub` for `$elseif` → `$if`. Add a targeted test covering mixed-case `$ifThen` / `$elseIf`. |
| `tests/unit/ir/test_preprocessor_conditionals.py` | New tests: a 3-way `$ifThen/$elseIf/$else` block picks each branch correctly; a mixed-case `$elseIf` matches; a `$ifThenI`/`$ifThenE` block evaluates; the `$else` fallback only fires when no prior branch matched. |

---

## Issue 3 (Follow-up, Low Priority): Dead-Parameter Declarations In Output

### Observation

The generated MCP also declares several parameters that come from
the *post-solve* analysis section of `partssupply.gms` and are never
used in the MCP:

```gams
Parameters
    MN_lic(t)
    MN_lic2(t)
    Util_gap(t)
    F(i,t)
    noMHRC0(i,t)
    noMHRC(t)
```

After fixing Issues 1 and 2 the model solves; these declarations are
harmless (they consume zero memory at solve time), but they are
noise. They flow in because
`emit_original_parameters()`/`emit_interleaved_params_and_sets()`
emits every parameter in `model_ir.params`, not only the ones
reachable from the KKT equations + pre-solve assignments.

### Fix Strategy (Defer — Not Required For Success Criteria)

Add a liveness pass: parameters not transitively referenced by any
emitted equation, pre-solve assignment, or bound are dropped. This
is a general cleanup and risks over-pruning (e.g., parameters whose
only use is an initialization side-effect); treat it as a separate
ticket (new `src/emit/liveness.py`) and ship `partssupply` success
without it. Called out here only so the leftover declarations are
explained, not ignored.

---

## Phase Plan

### Phase 0 — Blast-Radius Audit (30 min)

1. `grep -rn '\$ifThen\|\$elseIf' data/gamslib/raw/ | wc -l`
   — count affected models.
2. For each hit, run `.venv/bin/python -c "from
   src.ir.preprocessor import preprocess_text; print(preprocess_text(open(<path>).read()))"`
   and diff against the expected post-conditional text (hand-verify a
   handful). Expected: every model using `$ifThen`/`$elseIf`
   currently takes the `$else` branch, so expect systematic miscompiles.
3. Record findings in
   `docs/planning/EPIC_4/SPRINT_24/AUDIT_IFTHEN_MISCOMPILE.md`
   (file names + severity: wrong-branch vs no-branch vs benign).

Rationale: Issue 2 is a general preprocessor bug, not a partssupply-
only bug. The audit quantifies which other corpus models will start
compiling correctly once it's fixed, and whether any of them break
(e.g., a model that happened to work because its `$else` branch was
accidentally compatible with the unreachable `$ifThen` branch — low
probability but real).

### Phase 1 — Fix Issue 1 (Tree-Emitter Parity) (1 h)

1. Edit `src/emit/original_symbols.py`
   `_loop_tree_to_gams_subst_dispatch`: add the six missing handlers
   (`dollar_cond`, `dollar_cond_paren`, `bracket_expr`, `brace_expr`,
   `yes_cond`/`no_cond`, `yes_value`/`no_value`).
2. Add unit tests for each added rule (`tests/unit/emit/
   test_pre_solve_dollar_condition.py`).
3. `make test` — expect green.
4. Rerun partssupply: confirm the emitted line 55 becomes
   `icweight(i) = theta(i)$(not 0) + (1 - theta(i) + sqr(theta(i)))$(0) ;`.
5. GAMS-compile the emitted file. Expect GAMS to accept line 55; the
   run will **still fail** at the solve because the theta/p are from
   the wrong `$else` branch → feasible but a different NLP's KKT
   (`Util.l ≈ 0.297`). That's the fingerprint of Issue 2 remaining.

### Phase 2 — Fix Issue 2 (Preprocessor `$ifThen`/`$elseIf`) (45 min)

1. Edit `src/ir/preprocessor.py`:
   - Extend normalization regex to accept `$ifThen`/`$ifThenI`/
     `$ifThenE` (line 425).
   - Case-insensitive `$elseif` → `$if` rewrite (line 270).
2. Add/extend `tests/unit/ir/test_preprocessor_conditionals.py`.
3. `make test` — watch for regressions in any model that currently
   "works" because it was hitting the `$else` fallback (surfaced in
   Phase 0 audit).
4. Rerun partssupply translate.
5. GAMS-compile and solve: expect `Util.l ≈ 0.917`, matching the
   NLP's 0.9167 within PATH tolerance.

### Phase 3 — End-to-End Verification (30 min)

```bash
# Translate
.venv/bin/python -m src.cli data/gamslib/raw/partssupply.gms \
    -o /tmp/partssupply_mcp.gms
echo "exit=$?"   # expect 0

# Compile + solve
cd /tmp && gams partssupply_mcp.gms lo=3
# expect: "** EXIT - solution found." and "nlp2mcp_obj_val = 0.917"

# Compare to NLP baseline
cp /Users/jeff/experiments/nlp2mcp/data/gamslib/raw/partssupply.gms \
   /tmp/partssupply_nlp.gms
gams /tmp/partssupply_nlp.gms lo=3
grep -E 'OBJECTIVE VALUE|Util.*maker' /tmp/partssupply_nlp.lst
# expect: 0.9167 for both m and m_mn solves
```

Numerical tolerance: require `|Util_MCP - Util_NLP| ≤ 1e-3` (PATH
default convergence is 1e-6; 1e-3 is slack for the
solve-comparison fixture).

### Phase 4 — Corpus Retest (45 min)

1. `.venv/bin/python scripts/gamslib/run_full_test.py --only-parse --quiet`
   — expect parse count unchanged (this plan does not touch the
   grammar).
2. Run the translate + solve batch and record:
   - Models that flipped from fail → success (e.g., partssupply).
   - Models that previously hit the accidental `$else` branch and
     now reach a different one — review each for correctness
     against the NLP baseline.
3. Update `data/gamslib/gamslib_status.json` for any flipped models
   (translate status, solve status, solution_comparison).
4. Append entry to `docs/planning/EPIC_4/SPRINT_24/SPRINT_LOG.md`.

---

## Success Criteria

- [ ] **Parse.**
  `.venv/bin/python -m src.cli data/gamslib/raw/partssupply.gms -o /tmp/x.gms`
  exits 0 and produces a file with no `$ not` / `sqr(...) $ 0`
  bigrams.
- [ ] **Translate — GAMS-valid output.** `gams /tmp/x.gms lo=3`
  compiles without any Error 445 or downstream Error 257/141.
- [ ] **Translate — correct theta/p.** The emitted MCP contains
  `Parameter theta(i) / '1' 0.2, '2' 0.3 /` (or equivalent
  initialization) and `p(i) / '1' 0.2, '2' 0.8 /` from the
  `$elseIf %nsupplier% == 2` branch, not from the `$else` fallback.
- [ ] **Solve — PATH converges.** The GAMS run prints
  `** EXIT - solution found.` with residual ≤ 1e-6.
- [ ] **Solve — matches NLP.** `nlp2mcp_obj_val` is within 1e-3 of
  the NLP `Util.l` solved on the same source
  (`0.917 ≈ 0.9167`, within `1e-3`).
- [ ] **Regression-safe.** `make test` passes. Phase-0 audit models
  are all re-run; no model that previously matched NLP objective
  regresses to a mismatch.
- [ ] **Unit tests.** New tests cover `dollar_cond`/`dollar_cond_paren`
  in `_loop_tree_to_gams_subst_dispatch` and the
  `$ifThen`/`$elseIf` (mixed-case) paths in
  `_evaluate_if_condition` / `process_conditionals`.

---

## Recommended Fix Order

1. **Phase 0** — audit `$ifThen`/`$elseIf` usage in the corpus.
   Without this, Phase 2 can silently change the behavior of other
   models (good news: probably for the better) without us knowing.
2. **Phase 1** — Issue 1 first. It is local to the emitter, has the
   tighter blast radius, and lets us confirm GAMS accepts the file
   before tackling the preprocessor.
3. **Phase 2** — Issue 2. Once the emitter is clean, we can cleanly
   observe the semantic fix through objective-value equality with
   the NLP baseline.
4. **Phase 3** — end-to-end verify on partssupply.
5. **Phase 4** — corpus retest + status JSON sweep + SPRINT_LOG.

---

## Risks and Open Questions

- **Phase-0 surprises.** Any GAMSlib model currently "working" by
  accidentally hitting the `$else` fallback will change behavior
  once Issue 2 is fixed. Expect a few solve-objective shifts in the
  corpus; each flipped model needs a spot-check against the NLP
  baseline. If the new objective matches the NLP's (and the old one
  did not), that's a win — update the status JSON. If it's the
  reverse, we have an unrelated lurking bug and need a second
  ticket.
- **`$ifThen` vs inline `$if`.** `$ifThen` is *always* block-style
  (requires `$endIf`); `$if` can be either. The normalization fix
  intentionally keeps the post-normalized string as `$if …`, which
  is fine for block-mode evaluation. The inline detection path
  (`_split_inline_if`) already uses `$if[ie]?` and will never see a
  real `$ifThen` on a one-liner in practice, but adding the same
  `(?:then)?` to the inline regex is a cheap safeguard against
  pathological inputs.
- **Refactor deferred.** `_loop_tree_to_gams` and
  `_loop_tree_to_gams_subst_dispatch` are near-duplicates; the
  right answer is a single dispatcher parameterized by a token
  rewrite map, but that's a Sprint-25 cleanup. Shipping the
  six-handler copy-paste now is the lower-risk path.
- **Post-solve parameters (Issue 3).** Not fixed here; documented so
  the leftover `MN_lic`/`F`/`noMHRC0` declarations in the emitted
  file are explained, not mysterious.
- **Monte Carlo mode (`--nsamples > 1`).** Out of scope. The default
  driver uses `nsamples=1` so `pt(i,t) = p(i)` after the
  `loop(t, pt(i,t)=uniform(0,1))` step collapses to a single
  deterministic sample. The multi-sample path would require the
  translator to handle a true loop-of-solves (one MCP per sample),
  which is a separate project (tracked elsewhere as the
  "multi-solve loop" workstream).
- **Convexity warning W301.** The translator emits a nonlinear-
  equality warning on `rev(i).. b(i) =e= sqrt(x(i))`. This is a
  heuristic false-positive for partssupply in the sense that the
  equation has a unique smooth solution under the bounds
  (`x.lo=0.0001`), and PATH handles it. Do not suppress the
  warning; success criteria explicitly allow W301 as a warning, not
  an error.

---

## Related

- `src/emit/original_symbols.py:2702-2711` — `_loop_tree_to_gams`
  reference implementation for `dollar_cond` / `dollar_cond_paren`
  (what to mirror into the sibling dispatcher).
- `src/emit/original_symbols.py:3047-3137` — the sibling dispatcher
  that is missing the handlers.
- `src/emit/original_symbols.py:2991` —
  `emit_pre_solve_param_assignments`, the caller that triggers the
  buggy emission path for `partssupply`.
- `src/emit/expr_to_gams.py:656-673` — correct `DollarConditional`
  emission via the IR path (for reference — proves parens are
  mandatory for GAMS compatibility).
- `src/ir/preprocessor.py:149-308` — `process_conditionals` (where
  case-insensitive `$elseif` replace goes).
- `src/ir/preprocessor.py:404-496` — `_evaluate_if_condition` (where
  `$ifThen` normalization goes).
- `src/gams/gams_grammar.lark:738-741` — `dollar_expr` grammar rule
  with silent `"("` / `")"` tokens — the reason the tree emitter
  must re-insert parens explicitly.
- `data/gamslib/raw/partssupply.gms` — the canonical failing input.
- `data/gamslib/mcp/partssupply_mcp.gms` / `partssupply_mcp.lst` —
  current broken output and GAMS error log (ground-truth snapshot
  to check against after the fix).
- [PLAN_FIX_FEEDTRAY.md](PLAN_FIX_FEEDTRAY.md) — companion plan for
  MINLP exclusion; orthogonal to this one but uses the same
  pattern.

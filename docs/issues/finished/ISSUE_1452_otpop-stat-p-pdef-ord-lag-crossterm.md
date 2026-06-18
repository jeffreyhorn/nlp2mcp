# otpop `stat_p`: `pdef` `ord(n)-1` cross-term wrong — `sum(n,alpha(n))` instead of per-lead weight

**GitHub Issue:** [#1452](https://github.com/jeffreyhorn/nlp2mcp/issues/1452)
**Status:** **RESOLVED — Sprint 28 Day 7 follow-on (2026-06-18).** otpop now **MATCHES** (full-pipeline compare_match, MCP MS 1, pi = 4217.7978) — this completes otpop's **+1 Solve / +1 Match** (with #1393 + #1335 + #1449). *(Prior: OPEN — the last gate.)*
**Severity:** Medium — produced a wrong KKT cross-term; otpop solved but mismatched (pi 3160.86 vs NLP 4217.7978).
**Affected models:** otpop (confirmed); likely any model with `var(tt - (ord(n)-1))` adaptive-expectations / distributed-lag structure.

## RESOLUTION (2026-06-18) — pin the offset-driving set's element (Approach A)

`src/kkt/stationarity.py`, `_add_indexed_jacobian_terms`. New helpers `_offset_driving_sets(eq_def, var_name, model_ir)` + `_collect_ord_call_sets` detect the sets whose `ord(s)` drives an index offset of the differentiated variable in the **source** equation (otpop `pdef`: `p(tt-(ord(n)-1))` → `{n}`). For such sets, the `sum(n)` was already expanded into per-lead offset groups (#1081), so the per-group coefficient `alpha` is a *single* offset-determined element — NOT a free sum index. The fix builds a filtered `deriv_element_to_set` (the element→set map passed to `_replace_indices_in_expr` at ~line 6177) that **drops entries whose set is offset-driving**, so `alpha('1')`/`alpha('2')`/`alpha('3')` stay concrete and are not re-symbolized to `alpha(n)` + re-summed. Result: `stat_p(tt)` emits the per-lead weights `-(0.5·nu_pdef(tt) + 0.3·nu_pdef(tt+1)$… + 0.2·nu_pdef(tt+2)$…)`. Cached per `(equation, variable)`.

**Why this gate (vs the `ord(e)-1 == offset_key` correlation the plan suggested):** keying off the source-equation structure (`var` referenced with an `ord(s)`-dependent offset) is tighter — it fires ONLY for genuine `ord`-driven lag/lead shapes and never disturbs a generic `sum(j, beta(j)*x(i))` whose `j` is a real free index (those equations have no `ord(j)` in the variable's offset, so `_offset_driving_sets` returns `∅` and the existing free-index path is untouched).

**Verification:** `stat_p(tt)` per-lead weights correct (cold + presolve emit); otpop `--nlp-presolve` MCP solves **MS 1 Optimal in 0 PATH iterations** at the warm start; `run_full_test --model otpop` → **compare_match 1/1**. (The KKT-residual harness still prints CASE_B at the *boundary* rows `stat_p(1974)` / `stat_x(1990)` — a harness limitation: it does not transfer the active bound multipliers `piL_p`/`x_fx` that absorb those rows' residual at the boundary; the authoritative full-pipeline comparison and the 0-iteration MS-1 solve both confirm the match.)

**Blast radius (full corpus regen + targeted re-translate of every model with an `ord`-near-offset idiom):** **two** cold goldens change — `otpop` (the target) and **`tabora`** — and both are *corrections*. tabora's `wb`/`lw`/`ttb` are distributed-lag constraints `…sum(a, yv(a)*v(t-ord(a)))` (and `v(t+(card(t)-ord(a)))`), the same shape as otpop's `pdef`; `stat_v` previously emitted `sum(a, yv(a)*mult(t±k))` (the *total* yield at every lead) and now emits the per-lead pinned `yv("a0k")*mult(t±k)` (the single element with `ord(a)=k`). tabora compiles clean (`a=c`, 0 errors); it is `path_solve_license` in CI so there is no Solve/Match metric change, but the emitted KKT is now correct. All other `ord`-idiom candidates (clearlak, dinam, hhfair, imsl, qabel, sparta, tfordy) regenerate byte-identical; sddp/torsion have no committed golden.

## How it surfaced

With #1393 + #1335 + #1449 landed, otpop's `--nlp-presolve` now **compiles and solves (MCP MS 1 Optimal)**, the embedded NLP warm-starts correctly (4217.7978), and the KKT-residual harness finally runs on otpop. Its verdict:

```
verdict: CASE_B — emit_bug   (dual transfer CONSISTENT, dual scale 307)
max-residual row: stat_p(1983)  rel 1.16   (raw -358)
top rows: stat_p(1980), (1981), (1982), (1983), (1984)   — the middle years
```

The MCP converges to pi = 3160.86, not the NLP's 4217.7978.

## Root cause

```
pdef(tt)..  pd(tt) =e= sum(n, alpha(n) * p(tt - (ord(n) - 1)));   ! n=1*3, alpha=(.5,.3,.2)
```
So `pd(tt) = 0.5·p(tt) + 0.3·p(tt-1) + 0.2·p(tt-2)`, and `p(tt)` appears in `pdef(tt)` (coef `alpha('1')`), `pdef(tt+1)` (`alpha('2')`), `pdef(tt+2)` (`alpha('3')`). Correct `stat_p(tt)` cross-term:
```
- ( 0.5·nu_pdef(tt) + 0.3·nu_pdef(tt+1) + 0.2·nu_pdef(tt+2) )
```

Emitted (cold + presolve golden):
```
sum(n, ((-1)*alpha(n)) * nu_pdef(tt))
  + sum(n, ((-1)*alpha(n)) * nu_pdef(tt+1))$(ord(tt) <= card(tt)-1)
  + sum(n, ((-1)*alpha(n)) * nu_pdef(tt+2))$(ord(tt) <= card(tt)-2)
```
= `sum(n, alpha(n)) = 1.0` applied to **each** lead — the `n`-sum is mixed with the lead offset, so every lead gets the *total* weight (1.0) instead of its *specific* weight `alpha(n)`.

## Localization (2026-06-18) — the AD is correct; the bug is the stationarity re-symbolization

The constraint Jacobian is **right**:
```
∂pdef('1983')/∂p('1983') = -alpha(1)   (lead 0)
∂pdef('1984')/∂p('1983') = -alpha(2)   (lead +1)
∂pdef('1985')/∂p('1983') = -alpha(3)   (lead +2)
```
So #1081 expansion + AD produce the correct per-instance derivatives — the specific element `alpha('1')`/`alpha('2')`/`alpha('3')` at each lead.

The bug is in **`_add_indexed_jacobian_terms`** (`src/kkt/stationarity.py`), which groups the per-instance entries by lead offset (`_compute_index_offset_key` → offsets 0/+1/+2 — correct) and then **re-symbolizes the per-group coefficient wrongly**: the offset-0 group has the constant coefficient `alpha('1')`, but the re-symbolization treats the alpha-domain element `'1'` as an *uncontrolled index*, maps it to the symbolic `n`, and wraps it in `sum(n, …)` → `sum(n, alpha(n))` (= 1.0). Same mechanism as [[ISSUE_1393]] (a concrete index wrongly summed), but in the **indexed-constraint branch** rather than the scalar branch.

**Correct re-symbolization** — either keep the per-group constant element (`-alpha('1')·nu_pdef(tt)`, `-alpha('2')·nu_pdef(tt+1)`, `-alpha('3')·nu_pdef(tt+2)`), or, equivalently, a single `sum(n, (-1)·alpha(n)·nu_pdef(tt+(ord(n)-1)))`. The offset (lead) determines the alpha element; it must not be summed over.

### Exact fix surface (2026-06-18)

`src/kkt/stationarity.py`, in `_add_indexed_jacobian_terms`, the offset-group re-symbolization at **`indexed_deriv = _replace_indices_in_expr(derivative, var_domain, constraint_element_to_set, …)` (~line 6177)**. For the offset-0 group `derivative = -alpha('1')`; `constraint_element_to_set` maps the alpha-domain element `'1'` → its set `n`, so `alpha('1')` → `alpha(n)`, and downstream the now-uncontrolled `n` is wrapped in `sum(n, …)`. The element `'1'` is **offset-determined** (the group's `offset_key` is 0 and `ord('1')-1 = 0`), so it must be pinned, not re-symbolized to the iterator. A correct, tightly-gated fix must detect that a coefficient's param-index element correlates with the group's `offset_key` (via `ord(elem)-1 == offset`) and keep the concrete element (or emit the single `sum(n, alpha(n)·nu(tt+(ord(n)-1)))` form), **without** disturbing genuine uncontrolled-index sums.

**Risk:** `_replace_indices_in_expr` / `_add_indexed_jacobian_terms` is the shared cross-term path for every model — the fix needs a tight gate + full-corpus golden regression. Recommended as a focused task (this is the 4th distinct otpop AD bug, comparable in depth to #1393/#1335).

Same family as the offset-handling work in [[ISSUE_1393]] / [[ISSUE_1335]] / [[ISSUE_1224]], for an `ord(<sum-index>)-1` offset in an indexed equality.

## Implementation Plan (for the follow-on task — self-contained)

Prereqs: #1449 must be merged to `main` (it makes otpop's presolve compile/solve and unblocks the harness). Branch from `main` (e.g. `planning/sprintNN-1452-pdef-crossterm`). Requires the gitignored corpus (`data/gamslib/raw/otpop.gms`) + a local GAMS/CONOPT/PATH.

### Phase 0 — reproduce + confirm the surface (do NOT trust this doc's line numbers blindly; re-trace)

1. **See the wrong emit (cold golden, no GAMS needed):**
   ```bash
   grep -oE "stat_p\(tt\)\.\.[^;]*" data/gamslib/mcp/otpop_mcp.gms | grep -oE "sum\(n, \(\(-1\) \* alpha\(n\)\) \* nu_pdef\(tt[^)]*\)\)"
   ```
   Expect the three `sum(n, ((-1)*alpha(n))*nu_pdef(tt+k))` terms (the bug).

2. **Confirm the AD Jacobian is already correct** (the fix is NOT here):
   ```python
   from src.ir.parser import parse_model_file; from src.ir.normalize import normalize_model
   from src.ad.constraint_jacobian import compute_constraint_jacobian
   m = parse_model_file("data/gamslib/raw/otpop.gms"); ne,_ = normalize_model(m)
   J_h,_ = compute_constraint_jacobian(m, ne)
   J_h.get_derivative_by_names("pdef", ("1984",), "p", ("1983",))  # -> Unary(-, ParamRef(alpha(2)))
   ```
   `∂pdef('1983'|'1984'|'1985')/∂p('1983')` = `-alpha(1)|-alpha(2)|-alpha(3)` (per-lead, correct).

3. **Harness baseline** (post-#1449): `.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/otpop.gms --tol 1e-3` → `CASE_B`, dual transfer CONSISTENT, max-residual `stat_p(1983)` (raw ≈ −358), top rows `stat_p(1980..1984)`. otpop presolve MCP solves MS 1 at **pi=3160.86** (not 4217.7978).

### Phase 1 — the fix (`_add_indexed_jacobian_terms`, `src/kkt/stationarity.py`)

The offset-group loop (search `for offset_key, group_entries in offset_groups.items()`, ~line 5888) re-symbolizes each group's representative `derivative` via `indexed_deriv = _replace_indices_in_expr(derivative, var_domain, constraint_element_to_set, …)` (~line 6177). For the offset-0 group of `(pdef, p)`, `derivative = -alpha('1')`; `constraint_element_to_set` maps the alpha-domain element `'1'` → set `n`, so `alpha('1')` → `alpha(n)`, then the now-uncontrolled `n` is summed (the wrapping is the same machinery as the scalar branch's `if uncontrolled:` block, which [[ISSUE_1393]] fixed at ~line 6859).

**Fix direction (tightly gated):** for an offset group whose representative coefficient contains a `ParamRef` whose index element is **offset-determined** — i.e. an element `e` of some set `s` with `ord(e) - 1 == offset_key[pos]` (the lag/lead arithmetic that produced the group) — **pin that element** instead of re-symbolizing it to `s` + summing. Equivalently, recognize the pattern and emit the single consolidated `sum(n, (-1)·alpha(n)·nu_pdef(tt+(ord(n)-1)))`.

Two candidate implementations (pick after a prototype proves per-instance correctness, per PR24):
- **(A) Pin-the-element:** before/inside `_replace_indices_in_expr`, exclude `constraint_element_to_set` entries for elements whose `ord(e)-1` equals the group's `offset_key` at the relevant position, so they stay concrete. Cleanest if the correlation is detectable from `offset_key` + the element's `ord`. Keeps the 3 enumerated lead terms but with the correct concrete weights.
- **(B) Consolidate-to-symbolic-sum:** detect that the variable's reference in the source equation uses an `ord(<inner-sum-index>)`-dependent offset (`p(tt-(ord(n)-1))`) and emit one `sum(n, …·nu(tt+(ord(n)-1)))` rather than enumerating. Closer to the source structure; larger change.

Start with **(A)** — smaller blast radius.

Key references:
- `_add_indexed_jacobian_terms` offset-group loop + `_replace_indices_in_expr` call (~6177).
- `_compute_index_offset_key` (~4679) — produces `offset_key` (the lead, here from `ord(n)-1`).
- `constraint_element_to_set` — built upstream in the same function; the map that turns `'1'`→`n`.
- The scalar-branch precedent for "uncontrolled index wrongly summed": [[ISSUE_1393]] fix at the `if uncontrolled:` block (~6859) — same class, different branch.
- `_diff_sum` cardinality/offset helpers in `src/ad/derivative_rules.py` (#1335) for how symbolic `ord`/offset is resolved elsewhere.

### Phase 2 — verify + regress

1. Regenerate otpop to `/tmp` (never grep the committed golden):
   ```bash
   .venv/bin/python -m src.cli data/gamslib/raw/otpop.gms -o /tmp/otpop_mcp.gms --skip-convexity-check --quiet
   grep -oE "stat_p\(tt\)\.\.[^;]*" /tmp/otpop_mcp.gms
   ```
   Expect the per-lead weights (`alpha('1')`/`alpha('2')`/`alpha('3')` at tt/tt+1/tt+2), **no `sum(n, alpha(n))`**.
2. Harness: `kkt_residual.py data/gamslib/raw/otpop.gms` → **CASE_A** (residual at `stat_p(1980–1984)` → 0).
3. otpop `--nlp-presolve` MCP solves **MS 1, pi ≈ 4217.7978** (the match — run from the repo root so the `$include` resolves). This completes otpop's **+1 Solve / +1 Match** (with #1393 + #1335 + #1449).
4. **Blast radius (mandatory — shared path):** regenerate all 153 `*_mcp.gms` goldens, diff vs committed; every change must be the correct per-lead-weight collapse and solve-equivalent (GAMS-solve the changed ones). Regenerate affected presolve goldens too. Run `make test` + `make typecheck/format/lint`.
5. Add a regression test (mirror `tests/integration/emit/test_1335_zdef_time_reversal_crossterm.py`): assert otpop `stat_p(tt)` contains the per-lead weights and **not** `sum(n, alpha(n)) * nu_pdef`.

### Useful facts already established (don't re-derive)

- otpop is **convex** (DB `likely_convex`; standalone NLP reaches 4217.7978 from every start). So the correct MCP KKT solution is unique = 4217.7978; a fixed `stat_p` should make PATH land there from the warm start.
- Dual transfer is CONSISTENT (harness) — not a sign/scale issue.
- `alpha = (0.5, 0.3, 0.2)` for `n = 1*3`; `pd(tt) = sum(n, alpha(n)·p(tt-(ord(n)-1)))`.

## Acceptance

`stat_p(tt)` emits the per-lead weights (`0.5·nu_pdef(tt) + 0.3·nu_pdef(tt+1) + 0.2·nu_pdef(tt+2)`); the harness residual at `stat_p(1980–1984)` → 0; otpop's presolve MCP matches the NLP (`pi ≈ 4217.7978`, MS 1) — completing otpop's +1 Solve/+1 Match. No corpus golden regressions (solve-equivalent for any other changed model).

## Related

- [[ISSUE_1393]], [[ISSUE_1335]] — the other two otpop `stat_p`/`stat_x` cross-term fixes (kdef, zdef).
- [[ISSUE_1449]] — the presolve `$184`/warm-start fix that unblocked the harness and surfaced this.

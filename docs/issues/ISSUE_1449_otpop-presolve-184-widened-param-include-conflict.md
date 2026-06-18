# otpop `--nlp-presolve` compile fails (`$184`): domain-widened params conflict with `$include` source declaration

**GitHub Issue:** [#1449](https://github.com/jeffreyhorn/nlp2mcp/issues/1449)
**Status:** **`$184` FIXED — Sprint 28 Day 7 follow-on (2026-06-17).** otpop's `--nlp-presolve` now compiles (presolve-only companion params; see RESOLUTION). **otpop's match is still NOT realized** — a *second*, distinct blocker (an embedded-NLP **convergence** divergence — NOT a state leak) was uncovered once the presolve compiled. See "Second blocker (#1439 class)" below. *(Prior: OPEN — blocks otpop's +1 Match.)*

## RESOLUTION — `$184` fixed (Sprint 28 Day 7 follow-on, 2026-06-17)

**Fix (`src/emit/emit_gams.py`, presolve-only):** under `--nlp-presolve`, declare domain-widened source params at their **source (subset) domain** — matching the `$include` so the two declarations agree — and emit a `<p>__pw` **companion** parameter at the widened (parent) domain *after* the `$include`, populated from the source param (`db__pw(t) = db(t)`). The MCP equation **bodies** are rewired to reference the companion (`db(tt)` → `db__pw(tt)`). The cold (non-presolve) emit is unchanged. Three small wirings: pass empty widenings to `emit_original_parameters` under presolve; `_emit_widened_param_companions` after the `$include`; `_rename_widened_params_to_companions` on the equation-definition text.

**Blast radius:** of the 11 presolve goldens, **10 are byte-identical**; only `fawley` changes (the only other model with param widenings) — still MODEL STATUS 5 (its pre-existing infeasibility; no functional regression). Cold otpop byte-identical. otpop's `--nlp-presolve` compiles clean.

## Second blocker (#1439 class) — embedded-NLP convergence divergence (NOT a state leak)

With the `$184` gone, otpop's presolve compiles but **still doesn't match**: the embedded `$include`d NLP converges to a **wrong local optimum** (pi = −29.77 / 48059 vs standalone **4217.80**; `x` interior at 18.55 vs at its upper bound; `p` at its floor vs interior). Exhaustive diffing of the embedded vs standalone NLP shows **everything feeding the solve is byte-identical**: all data params & scalars, all sets (`t`/`tt`/`th`/`tp`), all variable bounds (`.lo`/`.up`), the starting point (`x.l`=0, `p.l`=1 before the first solve), and the solver (both CONOPT). So this is **NOT a gateable pre-`$include` state leak** — with identical inputs and solver, it is **CONOPT path-sensitivity** in the non-convex model, triggered by the larger surrounding `$onMultiR $include` context (equation ordering / solver workspace nudging CONOPT into a different basin).

**Implication:** otpop's match is not unblocked by `$184` alone. Realistic fixes are different in kind and uncertain:
- **Warm-start the embedded NLP** to the global basin (the model computes `xtr`/`ptr` trial values but never assigns `x.l`/`p.l`) — but the NLP solves run *inside* the `$include`, so the presolve emit cannot inject `x.l` before them without changing how the source is included.
- **Deterministic/global solver options** for the embedded NLP — uncertain, demo-license-limited.
- **Architecture B** (external NLP solve → GDX `loadpoint`, no `$include`) — sidesteps the `$onMultiR` context but is a warm-start architecture change (the harness and `run_full_test` are built on Architecture A).

Tracked as the remaining gate to otpop's +1 Solve/+1 Match. The [[ISSUE_1335]] AD fix is hand-derivation-verified; residual-verification via the harness is also gated on this (the harness reuses the presolve emit).
**Severity:** Medium — blocks the warm-start match path AND the KKT-residual harness for any model with domain-widened params under `--nlp-presolve`.
**Class:** Same family as #1439 (korcge) — embedded-NLP-`$include`-diverges.
**Affected models:** otpop (confirmed); any `--nlp-presolve` model with a subset-domain param widened to its parent (camcge, korcge likely).

## Root cause

The MCP emit **domain-widens** subset-domain params to their parent set when referenced in a parent-domain stationarity equation (`src/kkt/stationarity.py:_detect_symbol_domain_widenings`). otpop: `db`, `del` (declared `(t)`, `t ⊂ tt`) are widened to `(tt)` because `stat_p(tt)` references `db(tt)`. This widening is **mandatory** — a `$(t(tt))`-guarded `db(tt)` with `db` declared over `t` is a `$171` domain violation (verified; GAMS domain-checks statically, the `$` guard doesn't help).

The `--nlp-presolve` emit then `$include`s the raw source (to solve the NLP for warm-start duals), which re-declares `db(t)`. GAMS rejects `db(tt)` + `db(t)` as `$184 Domain list redefined` under **both** `$onMulti` and `$onMultiR` (verified). The two declarations cannot coexist.

Issue #1330 fixed the analogous conflict for **equations** (`$318`) by mirroring the source's scalar declaration (`templates.py:_preferred_decl_domain`). Equations broadcast (scalar decl + indexed body); **params do not**, so that fix does not transfer.

## Why it is not a quick "tt→t" fix

- Widening to `tt` is mandatory for the MCP body (`$171` otherwise).
- `t`/`tt` cannot coexist (`$184`).

## Candidate fixes (all non-trivial; pick once the widening/`$include` tension is decided)

1. **Separate widened companion symbol in the presolve path** — don't pre-declare the widened param; after `$include`, emit `db_w(tt); db_w(t)=db(t);` and rename `db`→`db_w` in the MCP body for widened params (presolve only). Localized to the presolve emit; regression surface across all `--nlp-presolve` models with widened params. *(Least-broad of the three; recommended starting point.)*
2. **Restructure subset-equation→parent-stationarity cross-terms to the `sameas`-sum form** (like [[ISSUE_1335]]'s kdef), eliminating the widening. Cleaner conceptually; broad stationarity-emit change, high regression risk.
3. **Architecture B warm-start** (cold MCP + GDX `loadpoint`, no `$include`) — sidesteps `$184`, but the harness and `run_full_test` are built on Architecture A (presolve `$include`).

## Impact

- otpop `--nlp-presolve` does not compile → no warm-start match; harness can't verify otpop.
- otpop's +1 Solve/+1 Match (post-#1393 + #1335) is **bucket-forward, not realized**, gated on this.

## Acceptance

otpop `--nlp-presolve` compiles clean; the KKT-residual harness runs on otpop and reports `stat_p` residual → 0 at the NLP KKT point (confirming #1335); otpop's presolve MCP matches the NLP (`pi ≈ 4217.80`, MS 1).

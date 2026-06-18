# otpop `--nlp-presolve` compile fails (`$184`): domain-widened params conflict with `$include` source declaration

**GitHub Issue:** [#1449](https://github.com/jeffreyhorn/nlp2mcp/issues/1449)
**Status:** **RESOLVED — Sprint 28 Day 7 follow-on (2026-06-18).** otpop's `--nlp-presolve` now **compiles and solves (MCP MODEL STATUS 1 Optimal)**, and the KKT-residual harness runs on otpop (this issue had blocked it). The remaining otpop **+1 Match** is gated on a separate, newly-found AD bug — the `pdef` `ord(n)-1` cross-term (**#1452**), cleanly localized by the now-working harness. *(Prior: OPEN — blocks otpop's +1 Match.)*

> **Correction (2026-06-18):** an earlier revision of this doc claimed the post-`$184` divergence was "CONOPT path-sensitivity in a non-convex model, NOT a state leak." **That was wrong.** otpop is convex (the convexity DB says `likely_convex`; standalone otpop reaches 4217.7978 from every starting point tried). The divergence was a real bug — a state leak in *this fix's own first revision* (see RESOLUTION). Corrected below.

## Phase 0: Acceptance Gate

> **Scope note:** #1449 is a **presolve-emit *infrastructure*** fix (declaration/companion/var-fix-state under `--nlp-presolve`), not a new KKT *cross-term* derivation — the otpop cross-terms are #1393 (kdef), #1335 (zdef), #1452 (pdef). The acceptance gate below is framed accordingly: the "KKT shape" is the *structural* invariant the presolve emit must preserve so the embedded NLP and the MCP each see the correct model; verification is compile + solve + the harness running at all. Included to satisfy the CONTRIBUTING.md Phase-0 rule for `src/emit/` changes.

### Hand-Derived KKT Shape

For a subset-domain param `db(t)` (`t ⊂ tt`) used in a parent-domain stationarity row, the correct MCP has two *distinct* references that must NOT be conflated:
- **Stationarity (parent index):** `stat_p(tt) ← … + ((-1)·(db(tt)·p(tt)**(-a)·(-a)/p(tt)))·nu_dem(tt)$(t(tt)) + …` — references `db` at the **parent** index `tt`, so `db` must be visible over `tt`.
- **Original constraint (subset index):** `dem(t).. d(t) =e= db(t)·p(t)**(-a)` — references `db` at the **subset** index `t`; this same equation is solved by the embedded `$include` NLP and MUST be left algebraically untouched.
- **Boundary fix as complementarity:** for an element fixed in the source (`x.fx(th)=x74`) that is *also* in the stationarity domain (`x('1974')`, `1974 ∈ th ∩ t`), the MCP fixes it via the active equation `x_fx_1974.. x('1974') - 29.4 =e= 0` (paired with `nu_x_fx_1974`) — so `x('1974')` must be **free** (not `.fx`'d) when the MCP solves.

### Expected Emit Pattern

Regenerated `otpop_mcp_presolve.gms` must contain, after the `$onMultiR $include … $offMulti`:
- `Parameter db__pw(tt);` and `db__pw(t) = db(t);` (companion at the widened domain; **only** for params referenced at the parent index — not `del`/`xb`, which are over-widened but subset-only).
- `stat_p(tt).. … db__pw(tt) … ;` (parent-index reference rewritten to the companion) and **no bare `db(tt)`** in any `stat_*` row.
- `dem(t).. d(t) =E= db(t) * …;` — the original equation keeps `db(t)` (NOT `db__pw`).
- `x.lo('1974') = 0;  x.up('1974') = +inf;` after the `$include` (Layer-4 unfix), so `x_fx_1974` is matched.
- The source param declared at its subset domain so it agrees with the `$include` → **no `$184`**.

### Verification Methodology

```bash
# Regenerate to a temp path (never grep the committed golden), then check structure:
.venv/bin/python -m src.cli data/gamslib/raw/otpop.gms -o /tmp/otpop_ps.gms --nlp-presolve --skip-convexity-check --quiet
grep -E "Parameter db__pw\(tt\);" /tmp/otpop_ps.gms                       # companion present
grep -oE "stat_p\(tt\)\.\.[^;]*" /tmp/otpop_ps.gms | grep -q "db__pw(tt)" # stat_p uses companion
grep -oE "^dem\(t\)\.\.[^;]*"   /tmp/otpop_ps.gms | grep -q "db(t)"       # dem keeps db(t)
# Compile + solve from the REPO ROOT (so the $include resolves):
gams /tmp/otpop_ps.gms lo=2     # expect 0 errors, no EXECERROR; MCP MODEL STATUS 1 Optimal
# KKT-residual harness must RUN (it was blocked by this $184); for #1449 the gate is
# "harness runs + presolve solves MS 1". (Its CASE_B verdict at stat_p(1980–1984) is
# the SEPARATE #1452 gate, not #1449.)
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/otpop.gms --tol 1e-3
```
Blast radius: regenerate all 11 `*_mcp_presolve.gms` goldens + diff (only `chain`/`fawley`/`rocket` change; objective-equivalent — `chain` 6.9590 unchanged, `rocket` EXECERROR→MS 5 repaired) and confirm the cold `*_mcp.gms` goldens are byte-identical (the fix is presolve-gated). `make test` green.

### PROCEED/REPLAN Signal

**PROCEED** when: (a) otpop `--nlp-presolve` compiles with 0 GAMS errors and the MCP solves MODEL STATUS 1 Optimal; (b) the embedded `$include` NLP reaches the standalone optimum (`pi = 4217.7978`) — confirming no state leak corrupts it; (c) the KKT-residual harness runs on otpop; (d) cold emit byte-identical and no presolve-golden objective regressions. **REPLAN** if the embedded NLP diverges from standalone (indicates a residual state leak — as the first revision had).

**Traced Fix-Surface (Day-0):** established by bisection, not the prep hypothesis — truncating the presolve emit after `$offMulti` (NLP-solves only) yields the correct `pi=4217.7978`, while including the MCP equation block flips it to garbage, isolating the leak to the emit. Surfaces, all in `src/emit/emit_gams.py`: (1) `_rewrite_widened_param_refs` (parent-index-only rewrite — the over-rename of `dem`'s `db(t)` was the leak, since GAMS binds an equation's algebra to its last `..` def globally); (2) `_emit_widened_param_companions` (companion decls after the `$include`); (3) `_emit_presolve_fx_unfix` (Layer-4 var-fix unfix); wired in the main emit flow gated on `presolve_include_emitted`. Trace evidence: the embedded-NLP objective bisection above + the harness `dual transfer CONSISTENT` (rules out a dual-transfer bug).

## RESOLUTION — `$184` fixed + otpop presolve solves (Sprint 28 Day 7 follow-on, 2026-06-18)

`src/emit/emit_gams.py`, presolve-only. Three coupled fixes:

1. **Widened-param companions ($184).** Under `--nlp-presolve`, declare domain-widened source params at their **source (subset) domain** (so they agree with the `$include`), and emit a `<p>__pw` **companion** at the widened domain *after* the `$include* (`db__pw(t)=db(t)`). Only params actually referenced at their **parent-set index** (`db(tt)` in a stationarity row) get a companion + body rewrite (`db(tt)`→`db__pw(tt)`); `del`/`xb`/`pcr`, which are over-widened but only ever referenced at the subset index, get neither.

2. **Parent-index-only rewrite (the real divergence bug).** The body rewrite is restricted to **parent-index** references. The first revision renamed *all* references, including the re-emitted ORIGINAL equation `dem(t).. … db(t) …` → `db__pw(t)`. Because GAMS binds an equation's algebra to its **last `..` definition globally** (not by execution order), that silently switched the embedded `$include` NLP's `dem` to use `db__pw`, which is **0** when the NLP solves — corrupting the NLP to a garbage optimum (pi=−29.77 instead of 4217.80) and a bad warm-start. Keeping subset-index references (`db(t)`) intact fixes it; the embedded NLP now correctly reaches 4217.7978.

3. **Layer 4 — var-fix leak (`_emit_presolve_fx_unfix`).** The `$include` executes the source's `var.fx(idx)=val` (run to warm-start the NLP), fixing columns that the MCP instead fixes via an active `_fx_` complementarity equation (otpop's `x('1974')`, in both `th` and `t`). PATH then drops the fixed column and the `_fx_` row is unmatched → the MCP solve aborts (EXECERROR). After the `$include`, restore those elements to a free bound; the `_fx_` equation pins the value, so the relaxed bound is inert. This also **repairs `rocket`'s presolve golden**, which was committed with this exact EXECERROR.

**Result:** otpop `--nlp-presolve` compiles, the embedded NLP reaches 4217.7978, and the **MCP solves MS 1 Optimal**. otpop does not *match* yet — it solves to pi=3160.86 because of **#1452** (the `pdef` cross-term) — but the harness now runs and pins that precisely (CASE_B, residual at `stat_p(1980–1984)`).

**Blast radius:** cold emit byte-identical (presolve-gated). Of the 11 presolve goldens, 8 byte-identical; `chain` (objective unchanged 6.9590, only an internal `nu_x_fx` dual now properly matched), `fawley` (no companions; MS 5, unchanged), `rocket` (EXECERROR → MS 5, **repaired**). No objective regressions.

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

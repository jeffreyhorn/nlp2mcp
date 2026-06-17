# otpop `--nlp-presolve` compile fails (`$184`): domain-widened params conflict with `$include` source declaration

**GitHub Issue:** [#1449](https://github.com/jeffreyhorn/nlp2mcp/issues/1449)
**Status:** OPEN — filed Sprint 28 Day 7 (2026-06-17). Blocks otpop's +1 Match (the [[ISSUE_1335]] AD fix is correct but otpop can only match warm-started, which needs presolve to compile).
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

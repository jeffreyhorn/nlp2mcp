# Sprint 33 — Day 11: P6 failure-cohort — sample recovered (+1 Solve / +1 Match / +1 genuine floor)

**Date:** 2026-07-17 · **Day:** 11 · **Branch:** `planning/sprint33-day11-p6-cohort`
**Disposition: the sprint's first bucket move.** A genuine emit-correctness fix in the `path_syntax_error` cohort recovers **sample**: `path_syntax_error → model_optimal + match`. **+1 Solve (107→108), +1 Match (92→93), +1 genuine floor (74→75)** — hitting the Sprint-33 genuine-floor ≥ 75 target. Emit-touching `src/` change; full quality gate passed.

---

## 1. The bug — a `.l` init referencing a pruned variable

`sample.gms` declares two models — `sample` (original formulation, uses `n`) and `sampler` (reciprocal formulation, uses `nr`) — and solves both; nlp2mcp translates the **last solve** (`sampler`), so `n` (used only by the non-translated `cbal`/`vbal`) is **pruned** from the MCP. But the emit carried over the source calibration init `c.l = sum(h, data(h,"cost")*n.l(h))` (c's `l_expr`): its LHS `c` is in the MCP, but its **RHS references the pruned `n`** → `$140 Unknown symbol` at compile (`path_syntax_error`).

## 2. The fix (`src/emit/emit_gams.py`)

In the variable-init pass, an expression `.l` init is now **skipped when it references a variable absent from the MCP**:
- `_declared_mcp_vars = {name.removeprefix("stat_").lower() for name in kkt.stationarity}` — the variables that actually get a stationarity equation (i.e. are declared). This is **narrower than `kkt.referenced_variables`**, which walks *all* equations (including the non-translated `cbal`/`vbal`, so it wrongly includes `n`).
- The scalar `l_expr` case skips the init iff its `.l`-refs (`_collect_varref_names`, which returns **only** `.l` variable references — not params/sets) are not a subset of `_declared_mcp_vars`.

The fix only ever **removes** an init line that would reference an undeclared symbol — it cannot alter a correct emit.

## 3. Result (confirmed via the pipeline)

- sample re-emits clean, **compiles + solves MODEL STATUS 1 Optimal**, MCP objective **726.679 = the NLP optimum (726.6794)** → **match**.
- `run_full_test.py --model sample`: **Solve success 1/1, Match 1/1**; DB updated (`path_syntax_error → model_optimal`, comparison `match`).
- sample is `likely_convex` → a 142-corpus **candidate**, so this moves the headline buckets: **Solve 108, Match 93, genuine floor 75** (a genuine cold-emit fix — the corrected *cold* MCP matches; not a presolve/methodology gain).

## 4. No-regression + blast radius

- **Blast radius = sample only.** The fix removes a line only when a `.l` init references a pruned variable. A currently-passing model's golden compiles + solves, so it has no such line → **cannot regress**. `git status` after re-emitting confirms only `sample_mcp.gms` changed; a bounded re-emit of a dozen passing `.l`-init models shows **no golden change**.
- **The other cohort members are a *different* root.** ganges/gangesx (the only other committed goldens with the `.l = …X.l` shape) reference **declared** variables (`id`/`dst`/`invtot`/`savg`/`marg` all have `stat_` equations) → the guard does not fire → their goldens are **unchanged**. Their `path_syntax_error` is `$141/$145/$149` (declared-but-no-values / set-control on bound-clamp + parameter-assignment lines), **not** sample's `$140` — a separate bug banked for a follow-up.
- **Quality gate:** `make typecheck` ✓, `make format` ✓, `make lint` ✓, `make test` → **5034 passed** (the lone failure, `test_validate_simple_nlp_golden`, **passes in isolation** and serially — a known xdist parallel-flake, not a regression).

## 5. agreste (the other P6 candidate) — banked

agreste is a **single model solved twice** (`solve agreste maximizing yfarm using lp` at lines 294/298, with `phi = 0` between — a scenario driver), translating the last solve. Its CASE_B `stat_sales` rel 2.0 is a deeper harness-scope diagnosis (genuine factor-of-2 dropped-gradient vs driver artifact) — **not** the `path_syntax_error` root; banked for a focused follow-up (no in-sprint src change).

## 6. KPI impact

**The sprint moves off flat-KPI.** After P1/P3/P2 resolved with no in-sprint bucket (mine REPLAN, fawley H-b, sarf REPLAN), P6 delivers the first genuine gain: **Solve 107→108, Match 92→93, genuine floor 74→75, model_infeasible unchanged 7, path_syntax_error 8→7.** The genuine-floor ≥ 75 Sprint-33 target is **met** via a real cold-emit correction. Determinism/`--resolve-changed` re-confirmed clean (blast radius sample-only).

---
**Document Created:** 2026-07-17 · **Owner:** Sprint 33 execution (Day 11) · sample +1 Solve/+1 Match/+1 genuine floor.

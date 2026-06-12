# korcge `--nlp-presolve`: it/in assignments + deferred `.fx` fixups emitted before the `$include` run with `.l=0` → EXECERROR=5

**GitHub Issue:** [#1439](https://github.com/jeffreyhorn/nlp2mcp/issues/1439)
**Status:** OPEN — filed Sprint 28 Day 0 (2026-06-12). Latent emit bug in the `--nlp-presolve` path; **not a pipeline blocker** (korcge solves via the non-presolve file).
**Severity:** Low–Medium — the `--nlp-presolve` variant for korcge aborts at runtime, but korcge's pipeline solve uses the non-presolve `korcge_mcp.gms` (MODEL STATUS 1 Optimal), so no metric is affected. Belongs to the embedded-NLP-divergence bug class.
**Date:** 2026-06-12
**Last Updated:** 2026-06-12 (filed)
**Affected Models:** korcge (confirmed); likely other CGE-style models with `it`/`in` subset-membership + `.l`-dependent `.fx` fixups under `--nlp-presolve`.
**Found:** Sprint 28 Day 0 golden refresh (PR #1438) — the reviewer (Copilot) identified the ordering; an empirical run confirmed the abort.

## Symptom

```bash
gams data/gamslib/mcp/korcge_mcp_presolve.gms lo=2
# **** SOLVE from line 651 ABORTED, EXECERROR = 5
```

## Mechanism

`--nlp-presolve` deliberately skips the MCP-side `.l` initialization (the #1330 var-init-skip — the `$include`d NLP solve is supposed to provide the warm-start levels). But the emit places the `it`/`in` subset-membership assignments and the `.l`-dependent `.fx` bound-fixups **above** the `$include`, so they execute with `.l = 0`:

```
197: it(i) = yes$(e.l(i) or m.l(i));          # e.l/m.l = 0 → it computed EMPTY
198: in(i) = (not it(i));                     # → in all-true
208: k.fx(i) = k.l(i);                        # fix k/ls/mps to .l = 0
209: ls.fx(lc) = ls.l(lc);
213: mps.fx(hh) = mps.l(hh);
224: $include "data/gamslib/raw/korcge.gms"   # NLP solve sets the real levels — too late
496: e.fx(i)$(not (it(i))) = 0;               # not it(i) all-true → fixes e/m/pe/pm to 0
```

With `it` empty and the variables fixed to `0`, the `$(it(i))`-guarded stationarity rows (`stat_e`, `stat_m`, `stat_pd`, …) evaluate terms like `1 / xxd(i)` and `m(i) ** ((-1) * rhoc(i))` with `xxd = 0` / `m = 0` → division by zero / `0 ** negative` → **EXECERROR = 5**.

## Fix direction (Day-0-trace hypothesis — PR24; not yet implemented)

Move the `it`/`in` set assignments **and** the deferred `.l`-dependent `.fx` bound-fixups to **after** the `$include`, so they reflect the NLP solution levels rather than `.l = 0`. (Equivalently: emit them below the `$include` block under `--nlp-presolve`.) The exact emit site is in the `--nlp-presolve` ordering logic (`src/emit/emit_gams.py`) and is to be pinned by a trace before any `src/` change.

## Scope / impact

- **Not a pipeline blocker.** korcge's actual solve uses the **non-presolve** `korcge_mcp.gms` (`mcp_file_used = None`) → **MODEL STATUS 1 Optimal**. The `--nlp-presolve` variant is not used for korcge's metrics.
- **Not a regression** from the PR #1438 Day-0 golden refresh: the pre-refresh committed presolve golden was already broken (MODEL STATUS 5 Locally Infeasible, from an older emit); current emit aborts (EXECERROR=5). The refresh faithfully reproduced current emit.
- Distinct from the **cesam** presolve observation raised in the same review: cesam's empty `nu_*` transfer is **benign** (cesam's presolve MCP solves to MODEL STATUS 1 Optimal anyway) — no issue filed for cesam.

## Related

- **#1330** camcge — var-init-skip-under-presolve (round 3); same `--nlp-presolve` family.
- **#1378** launch — double-applied self-ref param under `$onMultiR`.
- **#1424** camshape — dynamic-subset blanket corruption under presolve.
- Sprint 28 Priority 10 divergence detector: `docs/planning/EPIC_4/SPRINT_28/PRIORITY_10_DIVERGENCE_PROPERTY_TESTS_DESIGN.md` (the embedded-vs-standalone-NLP divergence class this belongs to).

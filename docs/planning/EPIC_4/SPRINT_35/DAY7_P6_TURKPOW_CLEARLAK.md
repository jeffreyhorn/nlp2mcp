# Sprint 35 — Day 7 (P6 part 2): turkpow / clearlak — characterized, DEFER (heavily multi-root)

**Day:** 7 (Priority 6, residual failure-cohort part 2) · **Date:** 2026-08-03 · **Owner:** Sprint 35 execution
**Branch:** `planning/sprint35-day7-p6-cohort-2` · **Toolchain:** GAMS 54.2.1 (compile-only `a=c`; version-stable)
**Outcome: no recovery — DEFER both.** Unlike turkey (Day 6, one tractable `$161` quoting root with cascades), turkpow and clearlak are **heavily multi-root with *deep* dominant roots** (parser table-parse; dynamic-set-computation emit). No bounded whole-root-set fix exists this sprint — the expected **flat P6** (the second bucket source, a-priori hard per Task 4).

---

## turkpow — 5 root codes; dominant root = a ragged-Table parse bug (deep)

Live compile (GAMS 54.2.1): `$170`×6 · `$171`×5 · `$149`×1 · `$141`×1 · `$257`×1 (cascade) — 14 errors.

- **`$170`/`$171` "Domain violation for element/set" (dominant, 11 of 14):** the `Table mdatat(m,labels)` for thermal plants is **ragged** — e.g. `lignite-3`/`lignite-2`/`nuclear` have a **blank `initcap`** cell, shifting their columns. The parse mis-aligns those rows, so data *values* (`.9`, `-.005`, `4.5`, `-.01`, `30`, `inf`) are captured as **`labels` members** that aren't in the declared `labels` set (`initcap avail opcost opcost-g capcost capcost-g life maxcap`) → domain violation. This is a **fixed-width GAMS-Table column-alignment parse bug on blank cells** (parser-level, `src/gams/gams_grammar.lark` + `src/ir/parser.py`), pre-existing in the committed `turkpow_mcp.gms` golden. *(It is the same malformed `'lignite-3'.'4.5'` data the Day-6 turkey first-attempt tripped on.)*
- **`$149` "Uncontrolled set entered as constant"** — Task 4: turkpow's `$149` is a `stat_zt(m,v,b,t)` lag-KKT `sum(t__kkt,…)`, a *different* construct from the ganges product-rule `$149`.
- **`$141`** — a declared-but-unassigned calibration param.

**Verdict:** the dominant root is a deep parser table-parse bug; even if fixed, `$149`+`$141` remain (no recovery from one fix). Not bounded-tractable. **DEFER.**

## clearlak — dominant root = uninitialized dynamic/computed sets (deep)

Live compile: `$352`×4 · `$141`×2 · `$149`×1 · `$257`×1 (cascade) — 8 errors. clearlak is a **scenario-tree** model (`n /n1*n121/`, `parent`/`child` aliases).

- **`$352` "Set has not been initialized" (dominant):** the tree-structure sets are **computed** in the source — `leaf(n)$(ord(n) > …) = yes`, `anc(child,parent)$(floor(…)=ord(parent)) = yes`, and `nprob(n)` via `loop(anc(child,parent), nprob(child) = …*nprob(parent))`. The cold MCP emit does **not reproduce these set/parameter computations**, so `leaf`/`nn`/`anc` are referenced (`sum(leaf, nprob(leaf))`, `snprob(nn) = nprob(nn)`) while **uninitialized** → `$352`. This is the **dynamic/computed-set emit class** (the emit must reproduce the `$`-conditional set assignments + the tree `loop`), deep and structural.
- **`$149` / `$141`** — downstream of the same uninitialized-sets/tree-computation gap.

**Verdict:** the dominant root is dynamic-set-computation emit (deep); `$149`/`$141` trace to the same structural gap. Not a bounded quoting-style fix. **DEFER.**

## Why neither is turkey

turkey recovered because its **one real root** (`$161`, a per-part-quoting bug in `_format_set_declaration`) was a bounded, localized emit fix whose companions (`$141`/`$257`) were pure cascades that cleared with it. turkpow and clearlak have **multiple independent roots**, and their *dominant* ones are **parser-/emit-architecture** issues (ragged-Table parsing; dynamic-set computation) — not bounded, and not cascade-clearing. This matches Task 4's "heavily multi-root, a-priori hard" for the whole dinam/indus/turkpow/clearlak sub-cohort. dinam/indus (Day 6) are the same story (6 and 9 root codes).

## Sprint-36 carryforward (P6 residual cohort)

Each is a *dedicated* effort, not a sprint-day fix:
- **turkpow:** fix the ragged-`Table` fixed-width parse (blank-cell column alignment) → then re-triage `$149` (lag-KKT) + `$141`.
- **clearlak:** emit the computed dynamic sets/parameters (`$`-conditional set membership + the `nprob` tree `loop`) in the cold MCP → then re-triage `$149`/`$141`.
- **dinam/indus:** their own multi-root sets (`$140`/`$8`/`$37`/`$171`; `$130`/`$409`/`$148`), per Day-6's Task-4 catalog.

**No `--resolve-changed` / golden change** — Day 7 is docs-only (characterization); no `src/` touched, no bucket move. P6's realistic contribution this sprint was **turkey's compile-recovery** (Day 6, +1 pending the v54 testbed solve); turkpow/clearlak/dinam/indus stay `path_syntax_error`.

---

**Document Status:** ✅ Complete — Sprint 35 Day 7 (P6 part 2: characterized + deferred)
**Last Updated:** 2026-08-03
**Owner:** Sprint 35 Execution Team

# ganges/gangesx P2 — Cascade Re-Verification & Recovery Sequencing (Prep Task 5)

**Date:** 2026-08-10 · **Branch:** `planning/sprint37-task5` · **Scope:** docs/analysis-only — a scratch `src/` cascade prototype was applied for measurement and **reverted** (`src/` byte-identical to `main`; `stationarity.py`/`derivative_rules.py` byte-identical to the anchor `78ceaead`).

**One line:** the cascade fixes re-verify on current `main` (cold: only `$66` remains; presolve: compiles **clean, rc=0**) — and the two terminals are **both re-characterized, both corrections to the bank**. `$66` is a *bounded* fix the bank mis-specified (its proposed zero-default would silently change the model's mathematics), and **`rPower` is NOT the deep #1378/#1424 class at all** — it is a bounded emit-**ordering** bug, eliminated in two independent `/tmp` controls. The genuine deep blocker sits one level *behind* it: with `rPower` gone, the embedded NLP solves **MS-5 Locally Infeasible** where the raw source solves **MS-2 @ 6395.5444**.

Reference: `SPRINT_36/DAY8_P4_GANGES_BANK.md`, `SPRINT_36/GANGES_RECOVERY_SEQUENCING.md`, `SPRINT_35/DAY3_P4_BANK_CARRYFORWARD.md` §5. Measurements: GAMS 54.2.1, `/tmp/gng/`.

---

## 1. Cascade fixes — RE-VERIFIED on current `main` (both paths)

Applied to scratch `src/`: `$141`/`$145` from git `a8ff626c` **with the corrected helper** (`_expr_contains_varref_attribute`, the PR-#1617 catch — not the divergent `children()`-only variant), plus the `$149` `_diff_prod` §5 patch (inserted at `derivative_rules.py:3410`, exactly the banked surface).

| path | result |
|---|---|
| **ganges cold** (`a=c`) | `$141`/`$145`/`$149` → **0**. Only **`$66`** remains (+ the `$256`/`$257` solve-check artifacts). Reproduces S36 Day-8 exactly. |
| **ganges presolve** (`a=c`) | **rc=0 — compiles completely clean.** No `$NNN` at all (the calibration assignments *are* emitted under presolve, so no `$66`). |
| **gangesx cold** (`a=c`) | identical — `$141`/`$145`/`$149` → 0, the **same 16 `$66`** symbols |
| **gangesx presolve** (`a=c`) | identical — **rc=0 clean**; full run reproduces `rPower` at the same emitted structure (block `:478`, `ls.fx` guard `:484`, `$include` `:515`) |

**Both models measured** (the mandatory per-model protocol), not extrapolated. Emit cost re-measured: ganges **293 s** cold / **284 s** presolve; gangesx **259 s** / **262 s** (the banked ~335 s, same order).

## 2. `$66` (cold terminal) — 16 symbols, and the bank's proposed fix is WRONG

**Exactly 16 unassigned symbols**, from the listing's MCP error block:

```
stat_ax      → deltax      stat_deprec  → aid        stat_exscale → aex
stat_invtot  → adst        stat_ls      → as, deltas stat_lw      → av, deltav
stat_m       → aq, deltaq  stat_n       → az, deltaz stat_nd      → an, deltan
stat_nm      → pnm00       fddef        → cg
```

**The decisive question — are these computable cold?** Yes. Every `.l` value feeding them is **data-initialized** (`ganges.gms:557–745`, from the `stock`/`dat` tables and constants: `ls.l(i)=stock("self-empl",i)*100`, `pk.l(i)=dat("return-cap",i)/k(i)`, …), and **the only `solve` is at line 1150 — *after* the entire calibration block (598–746)**. So the calibration parameters depend on *pre-solve* data, not on a solution.

Confirmed in the emitted artifacts: the cold MCP **does** carry the `.l` inputs (`ls.l` ×14, `pk.l` ×10, `s.l` ×49, `lw.l` ×10, `id.l` ×3, `dst.l` ×2) but **not** the calibration assignments (`deltas/as/aid/adst/deltax/aex` — 0 occurrences each). nlp2mcp drops them purely because they *syntactically* reference a `.l` attribute.

> **Correction to the bank.** `SPRINT_36/GANGES_RECOVERY_SEQUENCING.md` §3 step 3 proposed "a default cold assignment, e.g. `param(domain) = 0`". That would be **wrong**: `as`, `deltas`, `av`, `deltav`, … are CES/LES **share and scale** parameters; zeroing them degenerates the production functions, so the cold MCP would compile while encoding a *different model* than the NLP — it could not legitimately match. The correct fix is to **emit the real assignments cold** (their inputs are present), not to default them.

### A second cold blocker the bank did not carry: `ac(i+2,r)`

With the `$149` fix applied, the emitted cold MCP **still contains `ac(i+2,r)`** in `stat_pc(i)`:

```
stat_pc(i).. nu_pcdet(i) + sum(r, (-1)*ch(i,r)*nu_cpidet(r)) + sum(r, (-1)*(pop(r)*ac(i+2,r)) …
```

`ac(i,r)` is a **data Table** (`ganges.gms:211`), so it is assigned cold — the `+2` is a spurious index offset (the same `_compute_index_offset_key` misattribution family as markov's `σ=sp`). It **compiles**, so it is invisible to the `$NNN` protocol, but it corrupts `stat_pc` → a **match-correctness** blocker that survives the `$66` fix. DAY2 flagged it ("the `$149` fix does not touch it"); this task confirms it is still present on current `main`.

**⇒ the cold path needs `$66` *and* `ac(i+2,r)`, not `$66` alone.**

## 3. `rPower` (presolve terminal) — NOT the deep class; a bounded ordering bug

The bank recorded `rPower` as "the #1378/#1424 embedded-NLP-divergence deep class … the `.l`-based power calibrations re-run non-idempotently under `$onMultiR`". **The measured root is different and far more tractable.**

**Reproduced first** (full run, generation): `**** Exec Error at line 2325: rPower: FUNC DOMAIN: x**y, x=0,y<0` → `SOLVE from line 1665 ABORTED, EXECERROR = 1`, with `**** Evaluation error(s) in equation "prods(...)"` for **cons-good, cap-good, int-good, service**.

**The failing object is the equation, not a calibration assignment:**
```
prods(i).. s(i) =e= as(i)*(deltas(i)*k(i)**(-rhos(i)) + ((1-deltas(i))*ls(i)**(-rhos(i)))$(not si(i)))**(-1/rhos(i));
```
`ls` is a **variable**; GAMS evaluates `ls(i)**(-rhos(i))` at its current *level* during generation. The level is 0 → `0**negative` → `rPower`. (`pub-infr` is excluded by `$(not si(i))`; `agricult` is the `sa` subset handled separately — exactly the 4 observed failures.)

**Why is the level 0?** nlp2mcp hoists the source's `.l`-dependent bound statements into a *"Deferred Variable Bounds (depend on `.l` values)"* block, and emits that block **before** the `$include` that establishes those `.l` values:

| | source `ganges.gms` | emitted presolve MCP |
|---|---|---|
| `ls.l(i) = stock("self-empl",i)*100` | line **593** | inside the `$include` (line **515**) |
| `ls.fx(i)$(not ls.l(i)) = 0` | line **1071** (*after* 593 ✔) | line **484** (*before* 515 ✘) |

At MCP line 484 `ls.l` is still 0 for **every** sector, so the guard fires universally and fixes `ls` to 0 — then `prods(i)` evaluates `0**(-rhos)`.

### Two independent `/tmp` controls both eliminate it

| control | change to the emitted MCP | result |
|---|---|---|
| **A — move** | deferred-bounds block relocated to *after* `$offMulti` | **rPower GONE**, rc 3 → **0** |
| **B — skip** | deferred-bounds block **deleted** (the `$include` already supplies these statements) | **rPower GONE**, rc 3 → **0** |

Control **B** is the recommended shape: under `--nlp-presolve` the `$include` re-executes the source's own bound statements at the right point, so re-emitting them is redundant — precisely analogous to the existing **Issue #1378 self-referencing-assignment skip** (`original_symbols.py:1832–1848`), which skips statements the `$include` already applies.

**The emitter already has both halves of this pattern.** It skips `$include`-supplied statements (#1378) *and* it already emits a **post-`$include` correction pass** — the *"#1449 (Layer 4): unfix elements fixed by the source `$include`…"* block (visible at `gangesx_presolve.gms:741`), which relaxes bounds the include set. So neither control invents new machinery: **B** extends the #1378 skip, **A** extends the #1449 post-include placement. That is what makes this a *bounded* fix rather than a research problem.

## 4. The real deep blocker, one level behind `rPower`

With `rPower` removed (both controls, identical outcome):

| model | status |
|---|---|
| **raw `ganges.gms` standalone** (reference) | **MS-2 Locally Optimal @ 6395.5444** ✔ (matches DAY8) |
| **embedded `ganges0`** (inside the presolve MCP) | **MS-5 Locally Infeasible @ −386785.5017** |
| `mcp_model` (PATH, warm-started from that) | **MS-4 Infeasible** |

The embedded NLP diverges from the identical standalone model. **This** — not `rPower` — is the genuine #1378/#1424 embedded-NLP-divergence class, and it is the 6th blocker. `rPower` was masking it, exactly the cascade's "each root masks the next" behaviour.

## 5. Recovery sequence (atomic) + per-step Phase-0 gates

| # | fix | path | gate |
|---|---|---|---|
| 1 | `$141`+`$145` (corrected helper) + `$149` (`_diff_prod` §5) | both | per-model `a=c` → assert `$141`/`$145`/`$149` = 0 (**verified, §1**) |
| 2 | `$66` — emit the calibration assignments cold (**not** a zero default) | cold | `a=c` → `$66` = 0; **and** the emitted values equal the presolve ones |
| 3 | `ac(i+2,r)` — the `stat_pc` index-offset misattribution | cold | the offset gone; `kkt_residual.py ganges` → CASE_A |
| 4 | `rPower` — skip the deferred `.l`-bound block under presolve (control B) | presolve | full run → no `rPower`; **verified, §3** |
| 5 | embedded-NLP divergence (MS-5 vs MS-2) | presolve | embedded `ganges0` reaches **MS-2 @ 6395.5444** |
| 6 | goldens + determinism ×3 + `--resolve-changed` | both | nightly slot (~35 min emit); `make leak-check`-style byte discipline |

**Atomicity holds:** the cold bucket needs 1+2+3; the presolve bucket needs 1+4+5. A partial landing churns the ganges/gangesx goldens (~9 collateral calibration goldens too) for **0 bucket** — the same prohibition that banked S35 and S36.

## 6. Bounded P2 outcome

**Realistic in-sprint outcome: 0 bucket** — unchanged from the bank, but for a *different and better-understood* reason.

- Two of the five blockers are now **bounded and specified** (`$66` emit-the-assignments; `rPower` skip-the-deferred-block, control-verified).
- Two are **not**: `ac(i+2,r)` (an index-offset misattribution in the shared offset machinery — the same family P1 markov is fixing, so it may benefit from that work) and the **embedded-NLP MS-5 divergence** (the genuine deep class, now correctly located).
- **+2 requires all five.** The honest target for a dedicated effort is *"land 1+2+4 (verified/bounded), then attack 3 and 5"*, with 3 plausibly riding on the P1 offset work.

**`$149` spillover (Unknown 2.4):** the `_diff_prod` fix is general — it removes the `$149` blocker from **dinam/indus/turkpow/clearlak** as well. Necessary-not-sufficient: each carries other roots (turkpow ragged `Table`, clearlak dynamic sets, dinam/indus `$140`+`$149`). Flagged for P6's residual cohort.

---

## 7. Known-Unknown dispositions

| Unknown | Verdict | Basis |
|---|---|---|
| **2.2** `$66` bounded vs deeper; the `ac(i+2,r)` match risk | ✅ VERIFIED — **bounded, but the bank's fix was wrong, and there is a second cold blocker** | §2 — 16 symbols enumerated; all `.l` inputs data-initialized with the only `solve` *after* the calibration block ⇒ computable cold, so **emit the assignments** (a zero default would change the model's mathematics). `ac(i+2,r)` **still present** in `stat_pc(i)` with `$149` applied ⇒ a second, match-correctness cold blocker. |
| **2.3** `rPower` tractable vs the deep #1378/#1424 class | ✅ VERIFIED — **it is NOT the deep class; the deep class is one level behind it** | §3–§4 — root is an emit **ordering** bug (deferred `.l`-dependent bounds emitted before the `$include` that sets those `.l`s ⇒ `ls` fixed to 0 ⇒ `prods(i)`'s `ls**(-rhos)` = `0**negative`). Eliminated by **two** independent controls (move / delete), rc 3→0. Behind it: embedded `ganges0` **MS-5** vs raw standalone **MS-2 @ 6395.5444** — the genuine divergence. |
| **2.4** atomic +2-or-0; `$149` unblocks the residual cohort | ✅ VERIFIED | §5–§6 — cold needs `$66`+`ac(i+2,r)`, presolve needs `rPower`+the MS-5 divergence; a partial churns goldens for 0 bucket. The general `$149` fix removes that blocker from dinam/indus/turkpow/clearlak (necessary-not-sufficient). |

---

**Document Status:** ✅ Complete — Sprint 37 Prep Task 5 (ganges/gangesx cascade re-verification + recovery sequencing).
**Last Updated:** 2026-08-10 · **Owner:** Sprint 37 execution team

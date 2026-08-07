# Sprint 36 — ganges/gangesx P4 ≥5-Blocker Cascade Re-Verification & Recovery Sequencing (Prep Task 6)

**Date:** 2026-08-07 · **Owner:** Sprint 36 execution team · **Branch:** `planning/sprint36-task6` · **Scope:** docs/analysis-only (measurements + git/DB checks; no `src/` change).
**Outcome: the ≥5-blocker cascade re-confirms on current `main` — the `$141`/`$145`/`$149` cascade starting point reproduces (measured cold-MCP compile), the banked fix surfaces are unchanged, and the `$66`/`rPower` terminals are structural to the (byte-stable) emit + source. The banked `$149` `_diff_prod` fix + the correct `$141` helper apply cleanly. Recovery is a real ≥5-blocker (both the cold path via `$66` and the presolve path via `rPower` must be solved) → an ordered plan with per-fix `--resolve-changed` gates + a nightly slow-golden regen; the honest disposition (a dedicated deep effort, likely 0 in-sprint bucket) is unchanged.** Verifies Unknowns 4.1, 4.2, 4.3, 4.4, 4.5, 6.3.

Reference: `../SPRINT_35/DAY3_P4_BANK_CARRYFORWARD.md` (the ≥5-blocker bank + the §5 `$149` patch), `../SPRINT_35/GANGES_RECOVERY_DESIGN.md`, `../SPRINT_35/GANGES_149_PRODUCT_RULE_ANALYSIS.md`. Code: `_diff_prod` (`src/ad/derivative_rules.py:3276`), `_expr_contains_varref_attribute` (`src/emit/original_symbols.py:1392`).

---

## 1. Cascade re-verification (Unknown 4.3)

The 5-blocker cascade (`../SPRINT_35/DAY3_P4_BANK_CARRYFORWARD.md` §1):

| # | blocker | path | root | status |
|---|---|---|---|---|
| 1 | `$141` ×15 | cold + presolve | NA-cleanup guard over presolve-gated `.l`-calibration params | banked (Day-1, git `a8ff626c`) |
| 2 | `$145` ×3 | cold + presolve | NA-cleanup over a universal-set (`*`-domain) param | banked (Day-1) |
| 3 | `$149` ×9 | cold + presolve | cross-index product-rule leaks the prod bound `j` free | banked (Day-2/3, `_diff_prod` §5 patch) |
| 4 | **`$66` ×1** | **cold** | calibration params (`adst`/`aid`/`aex`/`deltax`/`as`/`deltas`/`av`/`deltav`) presolve-gated → unassigned in the cold MCP but referenced in `stat_ax`/`stat_invtot` | the 4th root |
| 5 | **`rPower`** | **presolve** | the presolve emit `$include`s the source under `$onMultiR`; the re-included `ganges0` NLP hits `x**y, x=0, y<0` at generation (the embedded-NLP-diverges class #1378/#1424) | the 5th blocker |

**Re-measured on current `main` (this task):** emitting `ganges.gms` (335s — minutes-scale) and compiling the cold MCP under GAMS 54.2.1 reproduces the documented cascade starting point:
```
$NNN error codes in cold-MCP compile: {'141': 15, '145': 1, '149': 1, '257': 1}
```
`$141`×15 matches the DAY3 count exactly; `$145`/`$149` also appear (fewer than DAY3's ×3/×9 because on the *unfixed* emit the `$141` errors abort compilation early — the "each root masks the next" behavior the DAY3 protocol documented, which is why the per-model fix-then-recount protocol is mandatory); `$257` is the `$66`-cascade artifact DAY3 noted. **The cascade is present and starts at the documented blockers.**

**The `$66`/`rPower` terminals are structural to the byte-stable inputs:** `ganges.gms` (59,311 bytes) is unchanged, and it carries the power operations (`deltas(i)$ls.l(i) = …**(1/sigmas(i))`, `as = …**(-rhos(i))`, `deltav = …**(1/sigmav(i))` — the `rPower` triggers) and the presolve-gated calibration params (`aid`/`adst`/`deltax` at `:347–351`, the `$66` roots). Since the emit code is byte-unchanged over the relevant paths (§2) and the source is unchanged, the DAY3 live cascade (`$141`/`$145`/`$149` → `$66` cold → `rPower` presolve) reproduces on identical inputs. **The pipeline seal is unchanged:** `run_full_test.py` triggers the presolve retry only on a cold STATUS-5 / spurious mismatch, **not** on a cold `path_syntax_error` — so the cold path needs `$66` (to compile → STATUS 5 → retry) **and** the presolve path needs `rPower`; a single-path fix cannot recover ganges.

## 2. Banked fix-surface integrity (Unknowns 4.1, 4.2)

- **`$149` (Unknown 4.1):** `src/ad/derivative_rules.py` is **byte-unchanged since the anchor `78ceaead`** (`git diff` empty), and `_diff_prod` is present at `:3276` (with the collapse-branch machinery `_sum_should_collapse` `:2947`, `_apply_index_substitution` `:3154`). So the banked §5 patch (rebind the collapsed prod-dummy → the original wrt index) still applies to the unchanged surface. Its correctness/surgicality was proven at S35 (ganges `$149` 9→0; lmp2/camcge byte-identical; the full golden-staleness scan showed only ganges/gangesx/prolog drift). ✅ applies cleanly.
- **`$141` helper (Unknown 4.2):** the existing `_expr_contains_varref_attribute` is present at `src/emit/original_symbols.py:1392` (it traverses `VarRef`/`ParamRef`/`MultiplierRef` indices); the buggy proposed `_expr_contains_varref_attr` is **absent**. The Day-1 `$141`/`$145` fixes are preserved in git at `a8ff626c` ("[WIP, not shipped]"). **Re-apply must delegate to `_expr_contains_varref_attribute`** (the PR-#1617 review catch: the Day-1 `_expr_contains_varref_attr` missed attributed `VarRef`s inside index exprs). ✅ correct helper confirmed.

## 3. Ordered recovery sequence (per-fix `--resolve-changed` gates)

A dedicated ganges/gangesx recovery effort applies the fixes in dependency order, `--resolve-changed`-gating each so no unrelated golden churns:

1. **`$141` + `$145`** (re-apply from `a8ff626c`, with the `$141` helper corrected to `_expr_contains_varref_attribute`) → `gams a=c` recount (expect `$141`/`$145` → 0); `--resolve-changed --since <S36-open>` GO (ganges/gangesx + the `prolog` −3-byte collateral drift; nothing else).
2. **`$149`** (`_diff_prod` §5 patch) → recount (expect `$149` → 0); golden-staleness clean (only ganges/gangesx/prolog drift; the 17 non-collateral prod-in-stationarity models byte-identical).
3. **`$66`** (cold): define the presolve-gated calibration params in the cold MCP (a default cold assignment, e.g. `param(domain) = 0`) so `stat_ax`/`stat_invtot` stop erroring → cold compiles → (best case) STATUS 5 → the presolve retry fires. Watch the `ac(i+2,r)` value artifact (a *match*-correctness risk, Task-4 §5.2 of the S35 design).
4. **`rPower`** (presolve): the embedded-NLP-diverges investigation (#1378/#1424 family) — the gating blocker for the presolve path; a separate deep bug class (the re-included `ganges0` hits a power-domain error the standalone NLP does not; raw `ganges.gms` NLP solves fine standalone, MS-2 @ 6395.5444).
5. **Regenerate the slow goldens + determinism ×3** (§4), then the final `--resolve-changed` GO.

**Atomicity note:** the cold recovery needs `$141`+`$145`+`$149`+`$66` together (each masks the next); the presolve recovery additionally needs `rPower`. A partial landing recovers 0 bucket (the S35 outcome) — this is why the S35 attempt banked rather than shipped churn.

## 4. Slow-golden regeneration budget (Unknown 4.4)

**Measured: the ganges emit is 335s (~5.6 min)** (gangesx is comparable — a sibling CGE). Regenerating the ganges/gangesx goldens + a determinism ×3 `{0,1,42}` re-emit is **~6 × 5.6 min ≈ 35 min of emit** — well beyond an inline `make test` / CI-PR budget (the S35 ship-blocker: "slow-emit CGE goldens un-regenerable in the CI budget"). **Budget slot: a nightly / dedicated regeneration step** (not the PR gate), followed by the `--resolve-changed` GO. This is affordable in a dedicated recovery effort (unlike the S35 in-sprint CI budget) — so 4.4 is a *scheduling* requirement, not a blocker.

## 5. Cross-track: the `$149` unblock + the residual cohort (Unknowns 4.5, 6.3)

- **Unknown 4.5 — the `$149` fix unblocks the `$149` half of dinam/indus/turkpow/clearlak:** the `$149` `_diff_prod` fix is **general** (it repairs the cross-index CES/LES product-rule wherever it fires, not a ganges special-case), and the S35 golden-staleness scan proved it surgical (no non-collateral prod-in-stationarity model drifts). All four (dinam/indus/turkpow/clearlak) share the CES/LES prod-in-stationarity pattern (DB: all `path_syntax_error`, unchanged). So the fix removes their `$149` blocker — **but each carries *other* roots** (§6.3), so `$149` removal is necessary-not-sufficient for their recovery. Design-level VERIFIED; the per-model `$149`-removal recount is a recovery-time step.
- **Unknown 6.3 — residual cohort roots still accurate:** the DB shows dinam/indus/turkpow/clearlak all still `translate=success` / `path_syntax_error` (unchanged). The DAY7 characterization holds structurally (source + emit unchanged): **turkpow** = a ragged fixed-width `Table mdatat` parse bug; **clearlak** = uninitialized dynamic/computed sets; **dinam/indus** = `$140`+`$149` multi-root. None is bounded-tractable like turkey's single quoting root; the `$149` fix (§4.5) reduces but does not eliminate their blocker set. Design-level VERIFIED; per-model recounts at recovery. Ref: `../SPRINT_35/DAY7_P6_TURKPOW_CLEARLAK.md`.

## 6. Go / No-Go + disposition

**GO to carry the recovery spec** — the cascade + fix surfaces re-confirm; the banked `$149`/`$141` fixes apply cleanly; the ordered sequence + the nightly regen budget are specified. **Disposition unchanged (the honest S35 call):** ganges/gangesx recovery is a **≥5-blocker dedicated deep effort** — the cold path (`$66`) + the presolve path (`rPower`, a separate embedded-NLP-divergence bug class) must **both** be solved, and a partial landing churns goldens for 0 bucket. The realistic in-sprint outcome is **+2 Solve/Match/floor if both paths land, else 0** (the P4-flat branch).

**REPLAN triggers:** the `$66` cold assignment surfaces the `ac(i+2,r)` match artifact (a *correctness* risk, not just compile); the `rPower` embedded-NLP divergence proves as hard as the #1378/#1424 precedents; or a sixth blocker surfaces after `$66`/`rPower` (the per-model protocol's job). Any → ganges/gangesx stay `path_syntax_error` (Solve 108); the de-risked hand-off is this doc + the S35 banked patches (`a8ff626c` + the `_diff_prod` §5 patch). **Budget: 16–22h; schedule so the `rPower` deep blocker (the likely REPLAN) surfaces early, not on Day 12.**

---

**Document Status:** ✅ Complete — Sprint 36 Prep Task 6 (ganges cascade re-verification + recovery sequencing; GO, disposition unchanged)
**Last Updated:** 2026-08-07
**Owner:** Sprint 36 Execution Team

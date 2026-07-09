# Sprint 31 — Reusable-Tooling Readiness Audit

**Task:** Sprint 31 Prep Task 8
**Date:** 2026-07-09
**Owner:** Development team (tooling)
**Scope:** audit only — read-only tool runs (emit, harness, git-diff, file reads); no `src/` change.

---

## 0. Executive summary

The Sprint-28–30 diagnostic + regression tooling **covers every Sprint-31 model class**; Sprint 31 reuses it rather than rebuilding. The only **minimal extension** is the **head-offset property fixture** (`tests/fixtures/head_offset_ir_roundtrip.gms`, a clean one-file add from Task 3's round-trip spec — the P7 deliverable). Two operational notes: (a) the KKT-residual harness's cold/embedded-NLP solve is slow on the CES-heavy CGE/obj-grad models (hhfair, camcge) — use the standing `--gdx <pre-solved NLP>` / `--no-cold-start` flags; (b) sarf currently has **no committed emit golden** (it is a `translate_failure`), so `--resolve-changed` won't select sarf until its golden is first committed when the P4 symbolic emit lands.

| Tool | Sprint-31 coverage | Status |
|---|---|---|
| KKT-residual harness (`kkt_residual.py`) | scores P1 (mine), P2 (polygon), P3 (camcge), P5 (hhfair) shapes | ✅ ready (slow-NLP → `--gdx`) |
| `--force` scaffold (`forcing.py`) | homotopy/multistart/optfile levers + PATH optfile for rocket (P6) | ✅ ready |
| AD property catalog (`test_ad_crossterm_shapes.py`) | `shape8` = P2 gate; `shape9` = robert; head-offset fixture = the 1 new add (P7) | ✅ ready + 1 fixture to add |
| golden-staleness + `--resolve-changed` | git-diffs `data/gamslib/mcp/` — catches mine/polygon/camcge/hhfair emit changes | ✅ ready (sarf golden gap note) |
| presolve-divergence detector (`check_presolve_divergence.py`) | hard-fails only on `$onMultiR` corruption; head-offset/Walras MCP changes soft-classify | ✅ ready (no false hard-fail) |

---

## Tool 1 — KKT-residual harness (`scripts/diagnostics/kkt_residual.py`)

**Coverage: scores every Sprint-31 emit-touching shape** (Case-a/b/c verdict + `max_residual_row` localization + the §2 dual-transfer self-check):

| Priority | Model | Harness verdict (source) |
|---|---|---|
| P1 head-offset | mine | **CASE_B**, `stat_x(4,1,1)` rel 1.33, dual-transfer CONSISTENT (`ISSUE_1443` Day-0) |
| P2 offset-alias | polygon | **CASE_B**, `stat_theta(i12)` rel 0.492, CONSISTENT — **re-run this sprint (Task 4)**, byte-identical to Day-0 |
| P3 dual-consistent-Walras | camcge | **CASE_B** `stat_mps` (a fix-multiplier-transfer artifact) + cold **MS-4 singular at iter 0** (the structural-singularity fingerprint, `ISSUE_1330`) |
| P5 obj-grad | hhfair | **CASE_B**, `stat_u` (residual −2·CES_grad) (`ISSUE_1236` Day-4) |

So the harness produces an actionable verdict for the head-offset cross-term shape (P1), the dual-consistent Walras prototype (P3), and the obj-grad reduction (P5) — the three the audit must confirm. The polygon re-run this sprint (Task 4) demonstrates current-tree readiness.

**Operational caveat (not a gap):** the harness embeds an NLP presolve + a cold solve; on the CES-heavy models (hhfair, camcge) these are slow (multi-minute). The standing flags handle it: **`--gdx <NLP.gdx>`** (skip the embedded solve, load a pre-solved NLP KKT point) and **`--no-cold-start`** (skip the a-vs-c split for a fast residual-only read), plus `--tol` / `--json`. For P3 camcge the harness verdict must be corroborated with the cold-solve control experiment (the `/tmp` dual-consistent prototype, Task 5) because the `stat_mps` CASE_B is a transfer artifact, not the operative bug — the same "single-point residual is misleading for structural/objective-defining shapes" lesson the harness carries.

---

## Tool 2 — `--force` solution-forcing scaffold (`src/emit/forcing.py` + `config.py` + `cli.py`)

**Coverage: takes the rocket (P6) continuation/reformulation levers.** `FORCING_STRATEGIES = ("homotopy", "multistart", "optfile")` (config `force_strategy`; CLI `--force`); `emit_forcing_scaffold` emits:

- **`optfile`** — a PATH `path.opt` (`proximal_perturbation 1e-2` + `merit_function normal`) + `<model>.optfile = 1` + force the MCP solver to PATH.
- **`homotopy`** — a `proximal_perturbation` continuation `mu: large → 0` (rewritten per step via a GAMS put file).
- **`multistart`** — re-solve from N perturbed `.l` starts, keep the first MS 1/2.

These are exactly the emittable-GAMS forcing levers P6 exhausts (the `1/ht²`/`1/m²` Jacobian reformulation is a separate model-rewrite the scaffold's continuation wraps). The scaffold provides the *plumbing*; its optfile structure + the Sprint-30 forcing-survey results (`NONCONVEX_FORCING_SURVEY.md` §4) **feed the PATH-consultation input** (the concrete option-set/regularization-schedule question for the renumbered Sprint 32). The `--force` entry point is stable and inherited by the Sprint-32 consultation work.

---

## Tool 3 — AD cross-term property catalog (`tests/integration/emit/test_ad_crossterm_shapes.py` + `tests/fixtures/crossterm_shapes/`)

**Coverage: 9 shape fixtures present** (`shape1`–`shape9`). The two Sprint-31-relevant guards:

- **`shape8_offset_alias_successor`** — **strict-xfail** (`strict=True`), the **P2 completion gate**: its assertion (`x(i+1)*1$(j(i))` **and** `x(i-1)*1$(j(i-1))` in `stat_x(i)`) passes once the coupled offset-alias fix lands; dropping the xfail is the P2 gate (Task 4).
- **`shape9_objgrad_subset_boundary`** — robert's objective-gradient boundary-term guard (landed Sprint 30); confirms the property-test pattern for the objective-defining-intermediate-variable family (P5-adjacent).

**The one new add (P7):** the **head-offset round-trip fixture** `tests/fixtures/head_offset_ir_roundtrip.gms` (Task 3 §4 spec) — a mine-shaped model whose parse→normalize output asserts `head_domain_offsets[1] == IndexOffset('l', Const(1.0), False)`. **Note:** this is a *parse-round-trip* fixture (it guards the P1 IR plumbing at the parse layer), distinct from the *emit-shape* `crossterm_shapes/` fixtures (which assert a `stat_*` row) — it lives in `tests/fixtures/` with its own always-run parse test, not in the `crossterm_shapes/` catalog. A clean one-file add once P1's IR plumbing lands.

---

## Tool 4 — golden-staleness gate + `--resolve-changed` checkpoint re-solve

**Coverage: the changed-golden detector git-diffs `data/gamslib/mcp/`.** `_changed_golden_model_ids(since_commit)` (`run_full_test.py:1087`) runs `git diff --name-only <SHA>..HEAD -- data/gamslib/mcp/` → the changed model ids; `run_resolve_changed` (`:1169`, requires `--since-commit`) re-solves each and diffs its bucket against the committed DB. The Sprint-31 anchor is the Sprint-30 close **`ea4191dc`** (BASELINE_METRICS §"Checkpoint anchor").

**The Sprint-31 emit sites all produce goldens the diff catches** (each model has a committed `data/gamslib/mcp/<m>_mcp.gms` [+ `_mcp_presolve.gms`]):

| Emit site | Model(s) | Golden present? |
|---|---|---|
| head-offset core (`comp_pr`/`_emit_nlp_presolve`/`stat_x`) | mine | ✅ `mine_mcp.gms` |
| `_add_indexed_jacobian_terms` second-index | polygon | ✅ `polygon_mcp.gms` |
| dual-consistent Walras redefinition | camcge | ✅ `camcge_mcp.gms` |
| ν_objective obj-grad reduction | hhfair (+ irscge/lrgcge/moncge) | ✅ `hhfair_mcp.gms` (+ CGE goldens) |
| sarf symbolic runtime-guard emit | **sarf** | ⚠️ **NONE** (sarf is `translate_failure` — no committed golden yet) |

**sarf golden-gap note (feeds P4 + Task 9):** because sarf has no committed golden, `--resolve-changed` cannot select it until the P4 symbolic emit **first produces + commits** `sarf_mcp.gms`. So the P4 landing must (a) commit the new sarf golden, then (b) rely on the full-pipeline retest (not `--resolve-changed`) for the *first* sarf verification; thereafter `--resolve-changed` guards it. This is a sequencing note, not a tool gap.

---

## Tool 5 — presolve-divergence detector (`scripts/diagnostics/check_presolve_divergence.py`)

**Coverage: hard-fails (exit 1) ONLY on unambiguous `$onMultiR` corruption** — a GAMS abort (korcge #1439 EXECERROR), an embedded NLP that is infeasible/non-optimal while the standalone NLP is optimal, or an embedded run producing no objective. Everything else **soft-classifies** (no false hard-fail).

**Sprint-31 relevance:** the head-offset presolve dual transfer (P1) and the camcge dual-consistent transform (P3) touch the `--nlp-presolve` path. The detector gates on the **embedded NLP**, not the MCP — and for both P1 and P3 the embedded/standalone NLP solves optimally (mine is a convex LP; camcge's NLP is MODEL STATUS 2 at 191.7346), so the detector **soft-classifies** (no false hard-fail from the MCP-side head-offset/Walras changes). Same finding as Sprint 30. No extension needed.

---

## 4.2 — emit-budget timing tooling (sarf O(constraints) gate)

**Tooling: `/usr/bin/time -p .venv/bin/python -m src.cli data/gamslib/raw/sarf.gms -o /tmp/sarf_mcp.gms`** is the emit-budget timing method; the golden byte-diff + a `grep -c '^stat_task'` row-count check confirms O(constraints) vs O(instances). **A read-only run this sprint confirmed sarf's current emit exceeds a 2-minute wall clock and produces no golden** — i.e. the translate_failure / combinatorial-blow-up that the P4 symbolic re-emit must avoid. So the **timing tooling is ready**; the **empirical O(constraints) result** (does the symbolic re-emit translate sub-budget with an O(constraints) `stat_task` row count) is the in-sprint **Task 9 / P4** check — Unknown 4.2 stays 🔍 INCOMPLETE at the fix-outcome layer.

---

## Minimal-extension list (feeds Task 9 + P7)

1. **Head-offset property fixture (P7, before P1 lands):** add `tests/fixtures/head_offset_ir_roundtrip.gms` + its always-run parse test (Task 3 §4 spec). Clean one-file add; guards the P1 IR plumbing at the parse layer.
2. **sarf golden sequencing (P4):** the P4 landing must commit the new `sarf_mcp.gms` golden and use the full retest for sarf's *first* verification (`--resolve-changed` can't select a model with no committed golden). Sequencing note, not a code change.
3. **Slow-NLP harness caveat (P3/P5, operational):** use `--gdx <NLP.gdx>` / `--no-cold-start` for hhfair/camcge harness runs (multi-minute embedded solves). Standing flags — no extension.

**No blocking tool gap.** Every reused tool scores/guards its Sprint-31 class; the single deliverable is the P7 head-offset fixture, and the two notes are sequencing/operational.

---

## Unknowns resolved

- **4.2 (sarf emit-budget timing): tooling ready; fix-outcome 🔍 pending Task 9/P4.** The `/usr/bin/time` + CLI + `stat_task` row-count method measures the O(constraints)-vs-O(instances) budget; a read-only run confirmed sarf's current emit exceeds 2 min / no golden (the translate_failure the re-emit must avoid). The empirical O(constraints) result is the Task-9 check — Unknown 4.2 stays INCOMPLETE at the fix layer, with the timing tooling confirmed here.
- **6.1 (`--force` scaffold entry): ✅ VERIFIED.** The scaffold takes the rocket homotopy/multistart/optfile levers (+ the PATH optfile) and its structure + the Sprint-30 forcing survey feed the PATH-consultation input; the `--force` entry point is stable and inherited by Sprint 32.
- **7.1 (property-fixture readiness): ✅ VERIFIED.** `shape8_offset_alias_successor` is the strict-xfail P2 completion gate; `shape9` is robert; the head-offset round-trip fixture (Task 3 §4) is a clean one-file P7 add (a parse-round-trip fixture, distinct from the emit-shape `crossterm_shapes/` catalog).
- **7.3 (`--resolve-changed` checkpoint coverage): ✅ VERIFIED.** The changed-golden detector git-diffs `data/gamslib/mcp/` (anchor `ea4191dc`) and catches the emit changes for mine/polygon/camcge/hhfair (+ the CGE cluster); **sarf has no committed golden yet** (translate_failure) → the P4 landing commits its golden + uses the full retest for the first sarf verification (a sequencing note).

---

## Appendix — evidence

- **Tools present (read-only):** `kkt_residual.py`, `check_presolve_divergence.py`, `check_golden_staleness.py`, `changed_emit_artifacts.py`, `run_full_test.py` (`--resolve-changed`/`_changed_golden_model_ids`), `src/emit/forcing.py` (+ `config.py:47` `force_strategy`, `cli.py:207` `--force`).
- **`--force` levers (read-only, `forcing.py`):** `FORCING_STRATEGIES = ("homotopy", "multistart", "optfile")`; optfile emits `path.opt` (`proximal_perturbation` + `merit_function`) + `.optfile = 1`.
- **Property catalog (read-only):** `tests/fixtures/crossterm_shapes/shape1..9.gms`; `shape8` `strict=True` xfail; `shape9` robert.
- **Golden paths (read-only):** `mine_mcp.gms` / `polygon_mcp.gms` / `camcge_mcp.gms` / `hhfair_mcp.gms` present; **no `sarf_mcp.gms`** (translate_failure).
- **sarf emit timing (read-only):** `src.cli` emit on sarf exceeds a 2-minute wall clock, no golden produced (the combinatorial blow-up the P4 O(constraints) re-emit must avoid).
- **Harness verdicts:** polygon CASE_B 0.492 (re-run Task 4, this sprint); mine CASE_B 1.33 / camcge CASE_B+singular / hhfair CASE_B `stat_u` (banked `ISSUE_1443`/`1330`/`1236`).
- No `src/` or golden change; all runs read-only.

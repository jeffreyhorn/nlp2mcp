# Sprint 35 → Sprint 36 Carryforwards

Each item is a **de-risked, control-confirmed, precisely-pinned** hand-off — a specification, not an open question. Anchor: S35 close (`07cbe669`); code/DB byte-unchanged since S34 close `78ceaead` (0 bucket move all sprint). Sprint-35 headline stayed **FLAT: Solve 108 / Match 93 / genuine floor 75** (the honest bimodal projection's flat branch; every deep track refuted or banked).

**The one live upside is markov (§1) — the sprint's only bucket-relevant lever (+1 genuine floor), fully diagnosed with a leak-gated attempt already de-risking half the fix.** turkey (§7) is a second, testbed-gated upside.

---

## 1. markov — `stat_z` diagonal-Kronecker emit bug (NEW, Day 11) — a +1 genuine-floor lever

**Status:** banked Day 11; a leak-gated `src/` landing was **attempted and reverted** (two-part fix confirmed). This is the **only bucket-relevant lever surfaced in Sprint 35**.

markov is a `verified_convex` **methodology** match today (`model_optimal_presolve`; `BASELINE_METRICS.md:134`) because its cold emit is wrong: the KKT-residual control (PR27) = **`CASE_B` emit_bug, `max|stat_z|` rel 13.3**. A correct cold emit ⇒ `CASE_A` ⇒ cold `model_optimal` ⇒ **genuine floor 75→76 (+1)**. markov is tiny (2 vars / 3 eqns) ⇒ fully local, **no testbed gate**. Archaeology: the correct form was **never emitted** (test red from birth, hidden by `pytest.mark.slow`).

**Two-part fix (both required; §6 of the hand-off derives them):**
1. **Diagonal-Kronecker split** — *implemented + verified* (residual 13.3→1.55). The diagonal is its own single-key offset group `(0,0,999)`, so #1110's within-group split can't fire; a NEW gated split (`_extract_additive_constant` + a determined-index multiplier) emits it as a direct `(1 − b·pi(s,i,s,i,sp))·nu_constr(s,i)`.
2. **Off-diagonal `σ=sp` enumeration** — the deeper blocker: the multiplier index equals an *independent* variable index (`σ=sp`, the var's 3rd), which the offset machinery can't represent (it expresses σ as offsets from `s`, the 1st index) → 44 spurious groups. This is the cohort-risky rewrite.

**Hand-off:** a dedicated markov effort in `_add_indexed_jacobian_terms` with the full 2-D-cohort regression harness (cesam2/camcge/ps2/ps3/polygon — the fawley Day-9 leak precedent). Gates: `kkt_residual` → `CASE_A`; golden-staleness (only markov drifts); cold re-solve `model_optimal`; the `slow` test flips red→green (decide its marker *with* the fix). Full diagnosis + implementer-ready spec: `DAY11_MARKOV_DIAGONAL_LEVER.md`.

## 2. rocket — PATH author consultation (#1462)

**Status:** `model_infeasible`, **CASE_C_OBJDEF** — a forcing problem, re-confirmed live (dual CONSISTENT; the sign flip stays **BANNED**). Emit is correct at the NLP point; every emittable lever (PATH options, μ-continuation, multistart, division-by-var reformulation) stays MS-5.

**Hand-off:** submit the FINALIZED, renumbered input (`SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` — renumbered S33→S36 ×11 targets, authoring preserved) to the PATH authors; the recommended option-set plugs into the existing `--force homotopy` scaffold. +1 Solve is **consultation-conditional**. `SPRINT_36/CONSULTATION_BUNDLE.md` §1.

## 3. mine — primal-degenerate-LP consultation (#1443)

**Status:** `model_infeasible`, `x.m=0`-degenerate boundary — four-times-carried, REPLAN'd in S35 prep. No emit-side dual architecture supplies the +16000 the degenerate boundary needs; the whole keying/pairing space is **value-invariant** (S34 proved H_dual value-invariant); the `x.up=inf` measurement error stays **BANNED**.

**Hand-off:** pose the primal-degenerate-LP question — *how does a warm KKT point of a primal-degenerate LP reconcile into an MCP when the degenerate boundary is not emit-reachable?* The only non-invariant lever is an LP-side reformulation (out of emit scope). **0 emit bucket.** `SPRINT_36/CONSULTATION_BUNDLE.md` §2 + `MINE_DUAL_ARCHITECTURE_DESIGN.md`.

## 4. fawley — two hand-offs: constraint-index-diagonal correctness fix + `--force` survey (#1111/#1112)

**Status:** H-b, re-confirmed Day 0 (`CASE_B`, `stat_bq` 0.973; `stat_trans(tr-2)` rel 1.00 the emit-correct harness max). Day-9 `/tmp` control **verified** the correctness fix (qsb/pbal `$(sameas(cfq__,cf))` drives `max|stat_bq|` **473.4→1.14e-13**), but the general `src/` predicate **leaked onto markov #1110** → DEFER.

**Hand-off (two parts):**
- **Correctness fix** — a dedicated effort needing a **derivative-structure discriminator** (not a surface-pattern predicate) to separate fawley's constraint-index-diagonal from the #1110 multi-pattern; lands with the `shape_fawley_2d_second_index` fixture. 0 bucket (H-b). `DAY9_P3_FAWLEY_CONTROL_DEFER.md`.
- **+Solve** — a **`--force`/continuation survey**: the MCP stays MS-5 @ 4399.557 vs LP opt 2899.25; the divergence is non-emit (`stat_trans(tr-2)`). The floor +1 is forcing-contingent. `SPRINT_36/CONSULTATION_BUNDLE.md` §3.

## 5. sarf — dedicated symbolic `stat_task` emit effort (#1385)

**Status:** REPLAN'd (scope/risk; design sound). The blow-up is `enumerate_variable_instances` materializing 369K `task` columns; it is **foundational** (the `col_to_var` index the whole Jacobian→gradient→stationarity flow iterates for all 142 models), so making `task` symbolic is a **coordinated corpus-wide re-architecture** — atomic, 20–28 h, for +1 Translate (the lowest-leverage bucket). The 398 active columns are not statically enumerable (`taskposs` runtime-computed). The measured baseline is **> 303 s and non-terminating** (killed at a 300 s cap).

**Hand-off:** a dedicated effort with a full-corpus regression harness; the acceptance gate is **O(active=398), not O(369K)** (single-digit-second emit), atomic S1/S2/S3 + `task.fx`, 141 byte-identical goldens, no set-name-literal indices. `SARF_SYMBOLIC_EMIT_DESIGN.md` + `PHASE_0_ACCEPTANCE_GATES.md`.

## 6. P4 ganges/gangesx — ≥5-blocker cascade recovery bundle (#1443 family)

**Status:** BANKED Day 3. The per-model protocol surfaced a **≥5-blocker cascade**: `$141`/`$145`/`$149` fixed → **`$66`** (cold, presolve-gated calibration params unassigned-but-referenced) → **`rPower`** (presolve `$onMultiR` re-runs `ganges0`, aborts `x**y, x=0, y<0` — the embedded-NLP-diverges class; raw ganges NLP solves fine standalone). Neither path recovers → no bucket.

**Hand-off:** a dedicated ganges-recovery effort re-applies the verified surgical `$149` `_diff_prod` fix (rebind the collapsed prod-dummy → the original wrt index; cross-index case) — **use the existing `_expr_contains_varref_attribute` for the `$141` helper** (the proposed `_expr_contains_varref_attr` is buggy, PR-review catch) — and tackles `$66`/`rPower` (can afford the slow CGE golden regen). `DAY3_P4_BANK_CARRYFORWARD.md` + `GANGES_RECOVERY_DESIGN.md` + `GANGES_149_PRODUCT_RULE_ANALYSIS.md`.

## 7. P6 turkey — compile-recovery landed; +1 Solve/Match pending a v54 testbed re-solve

**Status:** LANDED Day 6 (`$161` domain-less 2-D-set arity-inference fix, `_infer_domainless_tuple_arity` gated on `not set_def.domain`). Checkpoint 2 confirmed it works: freshly emitted, turkey **no longer `path_syntax_error`** — it compiles clean and reaches PATH, blocked only by `path_solve_license` (the 1000-row demo limit; turkey's MCP is 3,866 rows).

**Hand-off:** a **testbed/CI re-solve under GAMS 54** to realize the +1 (Solve + Match). This is the only landed-src upside pending; it needs a licensed >1000-row solve. `DAY6_P6_TURKEY_AND_TESTFIX.md`.

## 8. P6 residual cohort — turkpow / clearlak / dinam / indus (heavily multi-root, DEFER)

**Status:** characterized Day 7, no recovery (6/9 root codes each). **turkpow** = a ragged fixed-width `Table mdatat` parse bug (blank `initcap` mis-align → data values become invalid `labels` members). **clearlak** = uninitialized dynamic/computed sets (scenario-tree `leaf$()=yes` not reproduced cold). dinam/indus = `$140`+`$149` multi-root. None is bounded-tractable (unlike turkey's single quoting root).

**Hand-off:** dedicated per-model efforts (the multi-root discipline holds — verify per-model). `DAY7_P6_TURKPOW_CLEARLAK.md`.

## 9. camcge — dual-consistent Walras numéraire (#1330 → Epic 5, NOT Sprint 36)

**Status:** Epic-5-deferred Day 8. The S1∧S2∧S3 detector fires only camcge (cold MS-4 @ omega 191.7346; four CGE siblings cold MS-1). The full Walras-law dual redefinition is Epic-5 research; the banked price-pin variant reaches the correct primal but stays MS-4. The Case-c sign flip + `x.up=inf` stay **BANNED**.

**Hand-off (Epic 5, not Sprint 36):** the per-model-numéraire recipe + the residual-singularity characterization + the detector. `DAY8_P5_CAMCGE_SPRINT36.md`.

## 10. GAMS v53→v54 transition — baseline review + two follow-ups

**Status:** the pinned CI GAMS demo 53.1.0 license expired ~2026-07-29 (Day 6); CI/local bumped to **54.2.1**. GAMS 54 is stricter and does not solve identically to 53.

**Hand-offs** (`FOLLOWUPS_GAMS54_TRANSITION.md`):
- **v53→v54 baseline review** — the 108/93/75 baseline + the DB were built under GAMS 53; re-solve the corpus under 54 and diff buckets (5 OBJ-GAPs already noted: agreste/cesam/chain/fawley/rocket). Decide the canonical validation version. **This is the Day-13 retest's GAMS-version axis (see staging doc).**
- **robustlp NA coefficients** — GAMS 54 rejects the NA matrix coeffs (#1322 class) that 53 tolerated; allowlisted (WARN); the real fix eliminates the NA in the emit, then de-allowlists.
- **markov `slow`-test disposition** — RESOLVED to the §1 lever; the assertion is correct, decide the `slow`/`xfail` marker *with* the §1 fix.

---

## Banked follow-ons (not Sprint-36-primary)

- **Case-c family** (cesam/lnts/hhfair/CGE-cluster) — `case_c_objdef`, `nu_obj = ±1`; the objective-gradient sign flip is **BANNED** (control-refuted 4×). Forcing, not emit.
- **The residual `path_syntax_error` cohort per-model roots** — each characterized; verify per-model (the multi-root discipline holds).

---

**Document Status:** ✅ Draft — Sprint 35 Day 12 (Sprint-36 carryforwards + Day-13 retest staged separately)
**Last Updated:** 2026-08-04
**Owner:** Sprint 35 Execution Team → Sprint 36

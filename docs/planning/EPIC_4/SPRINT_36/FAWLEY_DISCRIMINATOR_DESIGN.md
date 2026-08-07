# Sprint 36 — fawley P3 Derivative-Structure Discriminator Design (Prep Task 4)

**Date:** 2026-08-06 · **Owner:** Sprint 36 execution team · **Branch:** `planning/sprint36-task4` · **Scope:** docs/analysis-only (no `src/` change — evidence gathered from the committed goldens).
**Outcome: the derivative-structure discriminator that the S35 Day-9 surface-pattern predicate lacked is specified and empirically grounded — "fire the constraint-index-diagonal `sameas(cfq__,cf)` guard only when the summed constraint index is ABSENT from the derivative coefficient." It cleanly distinguishes fawley's true constraint-index-diagonal from markov's #1110 off-diagonal, and co-exists with the Task-3 markov change by a disjoint firing condition. GO with a REPLAN exit (H-b: +1 floor contingent on a cold match; +Solve is a forcing hand-off).** Verifies Unknowns 3.1, 3.2.

Reference: `../SPRINT_35/DAY9_P3_FAWLEY_CONTROL_DEFER.md` (the leak), `../SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md` (the constraint-index-diagonal predicate + the fixture + H-b), `MARKOV_OFFDIAGONAL_DESIGN.md` (Task 3 — the co-existing markov change), `CONSULTATION_BUNDLE.md` §3 (the +Solve `--force` survey). Code: `_add_indexed_jacobian_terms` + `_derivative_structure_key` (`src/kkt/stationarity.py:5861+ / :5475`).

---

## 1. The leak surface — why the S35 Day-9 predicate over-fired on markov (Unknown 3.1)

S35 Day 9 added `_constraint_index_diagonal_guards` — a **surface/positional** predicate: fire the `$(sameas(cfq__,cf))` guard when "the summed multiplier index is a constraint-domain index occupying the *variable's* stat position." It was **correct for fawley** (`stat_bq` → all three guards, `max|stat_bq|` → 1.14e-13) but **leaked onto markov** — it added a wrong `$(sameas(j,i))` to markov's `constr` term, breaking `test_markov_stationarity_has_correction_term`.

**Root of the leak:** the predicate checked the *positional orientation* (a constraint index sitting in the variable's stat position) but **not whether the derivative actually depends on that index**. markov's `constr(σ,τ)` shares the surface orientation (τ=`j` sits in the variable's `i` position) but its off-diagonal derivative `−b·pi(s,i,σ,τ,sp)` **genuinely depends on the pairing** (via `pi`), so restricting it to the diagonal with `sameas(j,i)` is semantically wrong. A surface predicate cannot see this.

## 2. The derivative-structure discriminator (Unknown 3.1)

**The distinguishing structural fact — confirmed from the committed goldens:**

| | derivative coefficient (verbatim from the golden) | summed constraint index in the coefficient? | additive `Const`? |
|---|---|---|---|
| **fawley `qsb`** | `prop(c,s) * sum(m$(ms(m,s)), char(c,m)) * 1$(bposs(cf,c))` | **NO** — `cfq__` appears only in `nu_qsb(cfq__,l,s)` + the guards `$(cfq(cfq__))$(specs(cfq__,l,s))` | no |
| **fawley `pbal`** | `(-1) * (char(c,m) * 1$(bposs(cf,c)))` | **NO** — `cfq__` only in `nu_pbal(cfq__,m)` + guards | no |
| **markov off-diagonal** | `(-1) * (b * pi(s,i,s,i-1,s__kkt2))` | **YES** — `s__kkt2` is `pi`'s 3rd arg | no (`−b·pi`) |
| **markov diagonal** | `1 - b * pi(s,i,s,i,s__kkt1)` | YES (`s__kkt1` in `pi`) | **YES** (`1 − …`) |

**Discriminator:** *fire the constraint-index-diagonal `$(sameas(cfq__,cf))` guard only when the summed constraint index (`cfq__`) is **absent from the derivative coefficient** — i.e., it appears **only** in the multiplier reference and the domain-condition guards, not in the coefficient AST.*

- **fawley:** `cfq__` absent from the coefficient ⇒ the sum over `cfq__` repeats the *same* coefficient ⇒ a pure over-count the diagonal guard corrects. ✅ fire.
- **markov off-diagonal:** the summed index (`s__kkt2`) is *in* the coefficient (via `pi`) ⇒ the sum ranges over *distinct* values (a genuine sum, not an over-count) ⇒ a `sameas` guard would wrongly restrict it. ❌ don't fire.

**Implementation:** a predicate `_summed_index_only_in_multiplier(deriv_coeff, summed_idx)` = `summed_idx not in _collect_free_indices(deriv_coeff)` (the coefficient with the `MultiplierRef` and its `$` guards stripped). This is a **derivative-structure** test, not a positional one — exactly the refinement the S35 surface predicate lacked. It layers on top of the existing constraint-index-diagonal orientation check (`../SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md` §2): orientation gates *where* to look; the absence-from-coefficient test gates *whether the diagonal is real*.

## 3. Co-existence with the Task-3 markov change (Unknown 3.2)

Both the markov Part-2 change and the fawley discriminator live in `_add_indexed_jacobian_terms`. They fire on **disjoint** structural signatures — the joint change-surface map:

| Term | additive `Const` in deriv? | summed idx in coeff? | index-collision | Mechanism (branch) | Emits |
|---|---|---|---|---|---|
| **markov diagonal** (`(0,0,999)`) | **YES** (`1−b·pi`) | yes (`pi`) | Kronecker `σ=s,τ=i` | **Task-3 Part-1** `_kronecker_diag_correction` | direct `+nu_constr(s,i)` |
| **markov off-diagonal** (44 groups) | no | **yes** (`pi`) | `σ=sp` (alias, later exact-name pos) | **Task-3 Mechanism C** `_offdiag_independent_correction` | `−b·sum(j, pi·nu_constr(sp,j))` |
| **fawley qsb/pbal** | no | **NO** | `cfq=cf` (constraint's own index in var stat pos, **same set**) | **Task-4 discriminator** | `$(sameas(cfq__,cf))` guard |

**The `summed-index-in-coefficient` test alone separates fawley from every markov term:** markov's terms **all** carry the summed index in the coefficient (via `pi`) and/or an additive `Const`; fawley's qsb/pbal carry it in **neither**. So:
- the fawley discriminator **never fires on any markov term** (markov's coefficient always contains the summed index) — this *is* the fix for the S35 leak;
- the Task-3 markov mechanisms (gated on the additive `Const` for Part-1, and the `σ=sp` alias-collision for Mechanism C) **never fire on fawley** (no additive `Const`, no independent-index alias collision — `cfq` is `bq`'s own second index, a same-set diagonal).

**Non-overlapping by construction ⇒ no interaction.** Recommended land order: markov (Task 3) first, then fawley (Task 4), with a golden-staleness gate between them confirming each drifts only its own model. Both are additive gated branches — neither touches the shared `_compute_index_offset_key` matcher.

## 4. Phase-0 control + leak-freedom gate

**Phase-0 `/tmp` control (pre-`src/`, per `../SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md` §5):** hand-apply `$(sameas(cfq__,cf))` to fawley's emitted `stat_bq` qsb/pbal terms, re-run `kkt_residual.py fawley`, require **`max|stat_bq| → 0`** (machine zero, scoped to `stat_bq` — the emit-correct `stat_trans(tr-2)` H-b residual is *excluded* from the gate). Re-confirmed live in Task 2 (`stat_bq` rel 0.973 baseline; the goldens byte-identical to the Day-9 tree, so the 473→1.14e-13 hand-edit reproduces).

**Leak-freedom gate (Unknown 3.2):** `check_golden_staleness.py` after the `src/` change must show **only fawley drifts** — **markov** (the Day-9 leak target) **+ the 2-D cohort** (cesam2/camcge/ps2_f_s/ps2_s/ps3_s_gic/polygon) byte-identical. The discriminator is leak-free by construction (§3), but the empirical run is the confirmation. Cost caveat: the cohort + fawley emits are minutes-scale → a nightly/async or per-model diff, not an inline `make test` step. The `shape_fawley_2d_second_index` fixture (a fast synthetic, `test_ad_crossterm_shapes.py` pattern) lands *with* the fix (`../SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md` §6; catalogued in Task 9).

## 5. The +Solve hand-off (H-b — not an in-sprint P3 gain)

fawley is **H-b** (re-confirmed Task 2: the harness max is the emit-correct `stat_trans(tr-2)` rel 1.00, a *non-emit* divergence; the MCP solves MS-5 @ 4399.557 vs LP opt 2899.25 even with `stat_bq` closed). So the P3 correctness fix yields **0 Solve/floor without forcing** — the +1 genuine floor is contingent on fawley **cold-matching**, which H-b precludes. The +Solve is a **`--force`/continuation survey** (`CONSULTATION_BUNDLE.md` §3), scoped in Task 8, *not* an in-sprint P3 deliverable.

## 6. Go / No-Go + REPLAN exit

**GO** — the discriminator is precise (a single derivative-structure test), empirically grounded (both goldens), leak-free by construction, and co-exists disjointly with the Task-3 markov change. The Phase-0 `max|stat_bq|→0` control is local-ish (fawley emit minutes-scale but the control is a one-shot hand-edit + warm-start).
- **The correctness fix ships** (the leak-free `sameas` guard + the `shape_fawley_2d_second_index` fixture) — a genuine cross-term correction, **+1 genuine floor only if fawley cold-matches** (H-b ⇒ contingent).
- **REPLAN exit:** if the golden-staleness gate shows any markov/cohort drift, DEFER again (the S35 discipline) — but §3 argues this cannot happen (the summed-index-in-coefficient test is disjoint from every markov/cohort signature). If fawley does not cold-match (expected, H-b), the +Solve hands to the Task-8 `--force` survey — **0 in-sprint bucket is the expected P3 outcome**; the value is the shipped correctness fix + the fixture.
- **Budget fit:** within the P3 12–18h budget (the predicate + the coefficient-freedom test + the `/tmp` control + the fixture + the leak gate).

---

**Document Status:** ✅ Complete — Sprint 36 Prep Task 4 (fawley derivative-structure discriminator; GO with REPLAN exit)
**Last Updated:** 2026-08-06
**Owner:** Sprint 36 Execution Team

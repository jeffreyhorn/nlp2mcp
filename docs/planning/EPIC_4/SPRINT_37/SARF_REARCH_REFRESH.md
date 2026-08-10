# sarf P5 — Symbolic-Emit Re-Architecture Design Refresh (Prep Task 7)

**Date:** 2026-08-10 · **Branch:** `planning/sprint37-task7` · **Scope:** docs/analysis-only — measurements + a `/tmp` GAMS compile; **no `src/` change**.

**One line:** every premise of the banked design re-confirms on current `main`, and two things are **sharper than the bank**: the O(active) guarded emit is now verified at sarf's **real 369,024 scale** (the Sprint-36 check used a synthetic 54-cell analogue), and the corpus-safety gate is **inverted for sarf** — `make leak-check MODEL=sarf` **cannot work**, because sarf has no golden to drift.

Reference: `SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md` (the 3-site / 6-call-site / 7-term design), `SPRINT_36/SARF_DESIGN_REFRESH.md`, `SPRINT_36/DAY6_SARF_BANK.md`, `SPRINT_37/LEAK_HARNESS_DESIGN.md` (the P7 harness).

---

## 1. Blow-up re-measured (current `main`)

**Measured this task (2026-08-10):** `.venv/bin/python -m src.cli data/gamslib/raw/sarf.gms` — **still running at a 330 s cap without completing** ⇒ `>330s / NON-TERMINATING at cap (330.2s)`. Identical in kind to the S35 (">303 s, killed, no output") and S36 (">303 s / non-terminating") baselines: **no improvement, no regression**. The emit remains non-terminating in any pipeline budget (the harness timeout is 600 s), which is why sarf is `translate_failure`.

**Counts re-verified live from `sarf.gms`** (not carried forward): `|t|` = **24** (`01*24`), `|mn|` = **31**, `|g|` = **16** ⇒ `task(g,t,mn,mn)` declares **16 · 24 · 31 · 31 = 369,024** columns. Active = `taskposs(g,t) ∧ tech(g,m,n)` = **398**, both **runtime-computed** — so the fix genuinely cannot be "statically enumerate only the 398".

## 2. "3 sites" vs "6 call sites" — not a contradiction

The banked docs use both numbers; they measure different things, and conflating them would mis-scope the work:

| | count | meaning |
|---|---|---|
| **Materialization sites** | **3** (S1/S2/S3) | where the 369K columns are actually built — the surfaces the re-arch must short-circuit |
| **Corpus-safety surface** | **6** | every `enumerate_variable_instances` call site — traversed by *all 142 models*, so all six must be provably unperturbed |

**Re-located live on current `main`** (excluding the definition, imports and docstrings):

| # | call site | role |
|---|---|---|
| 1 | `src/ad/index_mapping.py:634` (`build_index_mapping`) | builds `col_to_var` — **S2** |
| 2 | `src/ad/constraint_jacobian.py:78` (`_precompute_variable_instances`) | feeds the per-column Jacobian diff — **S1** |
| 3 | `src/ad/gradient.py:287` | objective-gradient consumer |
| 4 | `src/ad/gradient.py:453` | objective-gradient consumer |
| 5 | `src/kkt/complementarity.py:367` | complementarity pairing consumer |
| 6 | `src/kkt/complementarity.py:512` | complementarity pairing consumer |

Definition at `src/ad/index_mapping.py:327`. **S3** is `stationarity.py`'s per-column `stat_task` emission (a consumer of the same column set, not a separate `enumerate_variable_instances` call). All three materialization-site files (`constraint_jacobian.py`, `index_mapping.py`, `stationarity.py`) are **byte-unchanged since the anchor `78ceaead`** — so the banked design's code surfaces are intact and **no fourth site** has appeared.

## 3. O(active) guarded emit — verified at sarf's REAL scale (Unknown 5.2)

Sprint 36 verified the shape on a *synthetic* 3·2·3·3 = 54-cell model (ncart 54 → nactive 4). That establishes the mechanism but not that it holds at the size that actually breaks. Re-ran under **GAMS 54.2.1** with sarf's **actual cardinalities**:

```gams
Set g /g1*g16/, t /t1*t24/, mn /mn1*mn31/;   Alias (mn,m),(mn,n);
stat_task(g,t,m,n)$taskposs(g,t).. 1 - cost*tech(g,m,n) =e= 0;
task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0;
```

| quantity | value | meaning |
|---|---|---|
| `ncart` = `card(g)·card(t)·card(mn)²` | **369,024** | **exactly sarf's declared Cartesian** — what an unguarded emit materializes |
| `ndomain` = `sum((g,t,m,n)$taskposs(g,t), 1)` | 46,128 | what `stat_task$taskposs` actually instantiates (an 8× cut from the guard alone) |
| `nactive` = `sum(…$(taskposs ∧ tech), 1)` | 96 | the live set after the per-term `$tech` guard + `task.fx` |

**Compiles clean at full scale — `rc=0`, 0 errors.** (The synthetic `taskposs`/`tech` here are denser than sarf's real ones, so 46,128/96 are upper bounds on the analogues of sarf's 398; the point is the *scaling behaviour*, which holds.) ⇒ **the guarded shape is valid GAMS 54 at 369,024 and instantiates O(guard), not O(Cartesian).** The parametric emit's remaining job is to *produce* this shape without materializing the 369K instances.

## 4. The corpus-safety gate is INVERTED for sarf (Unknown 5.3)

The banked design says the re-arch "is not landable without the full-corpus regression harness (the byte-stable proof the symbolic-branch predicate is sarf-only)". That harness now exists (Prep Task 3: `make leak-check MODEL=<id>`, `--expect-drift`). **But it cannot be used in the standard form for sarf:**

- `sarf` has **no committed golden** — `data/gamslib/mcp/` contains **0** sarf files, because its emit never completes (`nlp2mcp_translate: failure`, `mcp_solve: None`).
- So `--expect-drift sarf` would find sarf among the *expected* set but never among the *drifted* set, and report **`NO-OP: expected drift on sarf but the emit was byte-identical`** → exit 1. The gate would fail for a reason that has nothing to do with correctness.

**The correct gate for sarf is the inverse assertion:**

| model | gate | assertion |
|---|---|---|
| markov (P1), fawley (P4) | `make leak-check MODEL=<id>` | *exactly* that model drifts |
| **sarf (P5)** | **`make check-goldens`** (the base gate, exit 0 iff nothing drifted) | **ZERO of the 163 goldens drift** — the symbolic-branch predicate fires on no existing model — **plus** sarf newly *produces* a golden (163 → 164) |

This is the precise form of "the predicate is sarf-only": since sarf contributes no golden, its corpus-safety proof is entirely the **absence** of drift elsewhere. Recording it matters because running the P1/P4 recipe here would produce a confusing false failure.

**Ordering (for the Task-11 schedule):** sarf must be sequenced **after** the P7 harness work, and its gate is `make check-goldens`, not `leak-check`. The harness itself already exists on `main`, so the precondition is satisfied *today* — the remaining P7 dependency is only the CI wiring, not the instrument.

## 5. Phase-0 gate (PR20)

1. **Timing** — the re-emit completes in **single-digit seconds** (O(active=398)/O(constraints); the srpchase ~2.9 s reference). *A partial improvement that does not cross the threshold is a REPLAN, not progress.* Baseline: §1.
2. **Correctness** — the emitted `stat_task` matches the banked **7-term** derivation term-for-term (tbal ×2, labor, equipb1, equipb2, acost3, `task.lo`). A silently-wrong `stat_task` is the worst failure mode, so this is the correctness anchor.
3. **Corpus safety** — `make check-goldens` reports **zero drift** across all 163 (§4), and sarf newly emits a golden; determinism ×3 `{0,1,42}` byte-identical; `--resolve-changed` GO.
4. **No set-name-literal indices** — `grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` empty (the reverted Sprint-26 `nu_slack("srn")` anti-pattern).
5. **Atomicity** — the 2-D constraint gate + the S1/S2/S3 short-circuit + the parametric `stat_task` + `task.fx` land in **one change**; a partial landing yields an inconsistent MCP (multipliers with no stationarity coupling).

## 6. Disposition + REPLAN exit

**Unchanged: a 20–28 h atomic, foundational re-architecture for the lowest-leverage bucket (+1 Translate, moving neither Solve nor Match)** — the fifth consecutive deferral (S32→S33→S34→S35→S36). Everything needed to implement it exists; the case against doing it in-sprint is risk/reward, not readiness.

**Standing REPLAN triggers:** a fourth materialization site surfaces; the parametric emit re-triggers the timeout; any non-byte-stable golden on an unrelated model (the predicate fired on a 142nd variable); or a determinism break. Any → sarf stays `translate_failure` (Translate 135).

**Budget note:** at 20–28 h this is the sprint's largest single track; schedule it so a REPLAN (its most likely outcome) surfaces early.

---

## 7. Known-Unknown dispositions

| Unknown | Verdict | Basis |
|---|---|---|
| **5.2** the O(active=398) guarded emit passes GAMS-54 instantiation | ✅ VERIFIED — **at real scale**, strengthening the S36 result | §3 — compiled under GAMS 54.2.1 with sarf's actual cardinalities: `ncart` = **369,024** (exactly sarf's Cartesian), clean `rc=0`, and instantiation restricted to the guard domain (46,128) then the live set (96). S36 had shown this only on a 54-cell analogue. |
| **5.3** the re-arch can land against the full-corpus regression harness (P7 precondition + ordering) | ✅ VERIFIED — **with a correction: the gate is inverted for sarf** | §4 — the harness exists on `main` (Task 3), so the precondition is met. **But `make leak-check MODEL=sarf` cannot work**: sarf has **no golden** (0 files; `translate: failure`), so `--expect-drift sarf` reports `NO-OP` and fails for a non-correctness reason. sarf's gate is **`make check-goldens` — ZERO drift across the 163 — plus sarf newly producing a golden**. Ordering: sarf after the P7 CI wiring; the instrument itself is already available. |

---

**Document Status:** ✅ Complete — Sprint 37 Prep Task 7 (sarf re-arch design refresh; GO to carry, disposition unchanged).
**Last Updated:** 2026-08-10 · **Owner:** Sprint 37 execution team

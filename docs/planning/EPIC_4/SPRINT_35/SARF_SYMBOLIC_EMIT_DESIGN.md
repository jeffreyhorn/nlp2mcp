# Sprint 35 — sarf #1385 Symbolic/Parametric Emit-Mode Re-Architecture Design (Priority 2)

**Prep Task:** 7 (High) · **Date:** 2026-07-24 · **Owner:** Sprint 35 prep (AD/emit specialist)
**Day-0 code anchor:** `78ceaead` (S34 close) · **Measurement tree:** `5709cba0` (`main` at the S35 prep Task-6 merge) — docs-only ahead of the anchor, `src/`/`scripts/` byte-identical
**Scope:** docs/design only — re-confirms the three enumeration sites + counts (live), designs the symbolic-column concept, makes the **corpus-safety argument explicit** (all 6 `enumerate_variable_instances` call sites), specifies the parametric cross-term path + the guarded emit + the **measured** tractability gate + the full-corpus regression harness, and returns the honest in-sprint disposition. **No `src/` change.**

> **Disposition: DEFER / REPLAN to a dedicated symbolic-emit effort — the fourth consecutive scope/risk deferral (S32 → S33 → S34 → S35), now with the corpus-safety surface fully enumerated and the tractability baseline measured.** The design is **sound and complete** — it can now articulate the corpus-safety argument (§3) and the regression harness (§7), so it *is* implementable by a dedicated effort. But the in-sprint risk/reward is unchanged: a 20–28 h from-scratch re-architecture of the foundational AD column-index → Jacobian → gradient → stationarity flow (exercised by **all 142 models**), atomic (no safe partial), for the **lowest-leverage KPI** (+1 Translate, moving neither Solve nor Match). With P1 (mine) also REPLAN'd in prep (Task 6), the sprint's freed budget is best concentrated on **P4** (the designated bucket mover). Ship the complete de-risked spec, not the code; P2's 20–28 h → **P4/P6/P7**.

---

## Executive summary

sarf's `task(g,t,mn,mn)` variable declares **369,024 = 16·24·31·31** columns (g=16 agricultural tasks, t=24 fortnights, mn=31 implements+power-sources); only **398** are active (`taskposs(g,t) ∧ tech(g,m,n)`, both runtime-computed from data). The emit materializes all 369,024 at three sites, and the translate **does not terminate** — measured this task: **> 303 s and killed** (no output), consistent with the pipeline `translate_failure` (the 600 s harness timeout).

| Site | Locus (re-confirmed live, 2026-07-24) | What materializes |
|---|---|---|
| **S1** `acost3` body-diff | `compute_constraint_jacobian` per-column loop (`src/ad/constraint_jacobian.py:1002–1013`, differentiating `acost3.. cost = sum((g,t,m,n)$taskposs, oc·task)` per column) | 369K Jacobian entries |
| **S2** variable-column enumeration | `enumerate_variable_instances` (`src/ad/index_mapping.py:327`), called from `build_index_mapping` (`:634`, builds `col_to_var`) and `_precompute_variable_instances` (`src/ad/constraint_jacobian.py:78`) | 369K columns |
| **S3** variable stationarity | `src/kkt/stationarity.py` materializes `stat_task(g,t,m,n)` per Cartesian column | 369K rows |
| variable-blowup gate | **none** — the only blow-up gate is `_is_blowup_dynamic_subset_equation` (`src/ad/index_mapping.py:402`), which gates **equations** (srpchase's 1-D shape), not **variables** | absent |

The banked S33 7-term `stat_task` derivation (§4) is complete and verified; the S34 Day-6 assessment re-confirmed the foundational nature. **What this task adds:** (1) a **measured** tractability baseline (> 303 s, non-terminating — stronger than the design's ">75 s"); (2) the **explicit corpus-safety argument** — all **6** call sites of `enumerate_variable_instances` enumerated, and the symbolic-column change designed as a **branch gated on a runtime-blow-up predicate no other model's variable meets**, so the 141 byte-stable models traverse literally unchanged code; (3) the **full-corpus regression harness** that must *prove* that predicate is sarf-only.

**The design is now shippable-to-a-dedicated-effort. The in-sprint call is DEFER.**

---

## §1. Three-site + count re-confirmation (Unknown 2.1)

**Counts (live):** `g` = 16 (plough … transport), `t` = 24 (`01*24`), `mn` = 31 (5 power sources + 3 harvesters + 23 implements). `task(g,t,mn,mn)` ⇒ **16·24·31·31 = 369,024** declared columns. Active = `taskposs(g,t) ∧ tech(g,m,n)` = **398**, both runtime-computed (`sarf.gms:371` `taskposs(g,t) = sum((c,s), yes$treq(g,t,c,s))`; `tech` is a data Table) — **not statically enumerable**, so the fix genuinely cannot be "enumerate only the 398."

**The three sites are still the complete set** (S34 Day 6 found no fourth; re-confirmed this task):
- **S1** — `constraint_jacobian.py:1002–1013` iterates `for var_indices in var_instances: differentiate_expr(constraint_expr, var_name, var_indices, …)` over the per-variable instance cache, differentiating `acost3` (and every constraint) against each of `task`'s 369K columns.
- **S2** — `enumerate_variable_instances` (`index_mapping.py:327`) is the source of those instances, called from `build_index_mapping:634` (→ `col_to_var`) and `_precompute_variable_instances` (`constraint_jacobian.py:78`).
- **S3** — `stationarity.py` emits `stat_task(g,t,m,n)` per column from the per-instance Jacobian entries.

**Measured failure mode (this task):** the emit runs **> 303 s without completing** (killed at a 300 s cap; no `sarf_mcp.gms` produced). The log shows the loop iterating with `UserWarning: … taskposs … cannot be evaluated statically … Including unevaluable instances by default` — i.e. the runtime-gated conditions can't prune at compile time, so the full Cartesian is walked. This is a *stronger* baseline than the design's ">75 s": the emit is **non-terminating in any pipeline budget**.

**No fourth site** — the objective-gradient (`gradient.py`) and complementarity (`complementarity.py`) call sites also enumerate `task`, but they consume the same `enumerate_variable_instances` output; they are not *additional* materialization loci, they are additional *consumers* of the column set (which is why the corpus-safety surface is 6 call sites, §3).

---

## §2. The symbolic-column concept (Unknown 2.3)

Today a variable is a **list of enumerated instances** (`enumerate_variable_instances` → `list[tuple[str,...]]`), and `col_to_var` maps one column-id per instance. A **symbolic column** represents `task` as **a single guarded domain expression** — `(domain = (g,t,m,n), guard = taskposs(g,t) ∧ tech(g,m,n))` — rather than 369K enumerated tuples. Concretely:

- `col_to_var` gains a symbolic entry: one column-id keyed to `("task", <symbolic-domain-with-guard>)` instead of 369,024 concrete entries. Downstream, the symbolic column is **never expanded** — the Jacobian/gradient/stationarity carry `task`'s contribution **parametrically** (§4), and GAMS instantiates the 398 live rows at runtime from the emitted guard.
- The `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0` companion fixes the 368,626 vacuous columns so the emitted MCP is square under matching (the fixed columns' `stat_task` rows drop; the mine non-`d` precedent).

The symbolic column is **flagged by a predicate**, not by name (§3): a variable is symbolic iff it would materialize O(large) columns via a **runtime-gated active subset** — sarf's `task` is the only such variable in the corpus, but the predicate must be *structural*, not a hard-coded `"task"`.

---

## §3. Corpus-safety argument — the 141 other models stay byte-identical (Unknown 2.3, the load-bearing analysis)

`enumerate_variable_instances` is foundational: it feeds the column index that the **entire AD flow** iterates, for **all 142 models**. The design must not perturb the 141 non-sarf models. **All six call sites** (the complete corpus-safety surface, enumerated live):

| # | Call site | Role | Traversed by |
|---|---|---|---|
| 1 | `src/ad/index_mapping.py:634` (`build_index_mapping`) | builds `col_to_var` — the column index | **every model** |
| 2 | `src/ad/constraint_jacobian.py:78` (`_precompute_variable_instances`) | the per-constraint per-column Jacobian diff (S1) | **every model** |
| 3 | `src/ad/gradient.py:287` | objective-gradient enumeration | models with the var in the objective |
| 4 | `src/ad/gradient.py:453` | objective-gradient (second path) | models with the var in the objective |
| 5 | `src/kkt/complementarity.py:367` | complementarity pairing | **every model** |
| 6 | `src/kkt/complementarity.py:512` | complementarity (second path) | **every model** |

**The safety design: a symbolic branch gated on a runtime-blow-up predicate.** The change is *not* to `enumerate_variable_instances`'s enumeration logic (that would risk all 142 models' ordering). It is a **branch, taken only when a variable is flagged symbolic**, that returns the symbolic representation instead of enumerating; all non-flagged variables hit the **unchanged** enumeration path. Because:

1. **The predicate is structural and sarf-only-by-construction.** A variable is symbolic iff its declared Cartesian exceeds a threshold **and** its active subset is a runtime-computed guard (`taskposs∧tech`) that the emit cannot statically prune. No other corpus variable has this shape (verified against the corpus at the harness level; the regression harness §7 *proves* it). So on the 141 other models the predicate is **false for every variable**, and all six call sites execute **literally the same code** they do today.
2. **`col_to_var` ordering is preserved for the 141.** `build_index_mapping` sorts by variable name then indices; if no variable is flagged symbolic, the column numbering is byte-identical. (For sarf itself, `task` collapsing to one symbolic column *does* renumber sarf's own columns — that is sarf's own MCP, and acceptable.)
3. **Determinism (PR12) is preserved** because the symbolic branch is deterministic (a fixed guarded representation) and the enumerated branch is unchanged (the existing lexicographic sort).

**The residual risk this argument cannot fully discharge in prep:** the predicate must be *provably* false on all 141 models, and "at the harness level" is not "byte-proven." That proof is the full-corpus regression harness (§7) — 141 byte-identical goldens + determinism ×3 — which is why the design is **not landable without that harness**, and why a rushed in-sprint attempt is the risk the last three sprints declined.

---

## §4. Parametric cross-term path vs the banked 7-term derivation (Unknown 2.4)

Because the symbolic column is never expanded, `task`'s cross-terms cannot come from per-instance Jacobian entries — they come from a **new parametric path**: differentiate each constraint body **once, parametrically in `(g,t,m,n)`**, and inject the guarded term into `stat_task`. The target is the banked S33 7-term form (re-verified term-for-term against the constraint bodies, no changes needed):

```gams
task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0;   * fix the 368,626 vacuous columns

stat_task(g,t,m,n)$taskposs(g,t)..
    - (nu_tbal(g,t))$tech(g,m,n)                                                                  * [1] tbal
    + (tadj(g)*nu_tbal(g,t))$(sameas(g,'harvest-c') and sameas(m,'cotton-p') and sameas(n,'self-prop'))  * [2] tbal harvest-c adj
    + tech(g,m,n)*lam_labor(t)                                                                    * [3] labor balance
    + (tech(g,m,n)*lam_equipb1(m,t))$equipposs(m,t)                                               * [4] equipb1
    + (tech(g,m,n)*lam_equipb2(n,t))$equipposs(n,t)                                               * [5] equipb2
    + oc(g,m,n)*nu_acost3                                                                         * [6] acost3 (S1)
    - piL_task(g,t,m,n)  =E= 0;                                                                   * [7] lower bound
```

**Re-derivation check (this task):** all 7 terms verified against `sarf.gms` — `tbal` (`:426`, terms 1–2 with the `tadj` harvest-c adjustment `:424/:428`), the labor balance (`:439` term 3), `equipb1`/`equipb2` (`:412–413`, terms 4–5), `acost3` (`:454` term 6, the S1 parametric ∂), and `task.lo = 0` (term 7). **Every multiplier is indexed by the stat equation's own domain** (`nu_tbal(g,t)`, `lam_labor(t)`, `lam_equipb1(m,t)`, `lam_equipb2(n,t)`, `nu_acost3`, `piL_task(g,t,m,n)`) — **no quoted-set-name (set-name-literal) indices**, the guard against the reverted Sprint-26 `243fe578` `nu_slack("srn")` anti-pattern. The compile-clean scan `grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` must return nothing.

**A silently-wrong `stat_task` is the worst failure mode** on this track — the KPI (+1 Translate) would move while correctness regresses and no timing gate catches it. The 7-term re-derivation is therefore the design's correctness anchor; the fix surface (`constraint_jacobian.py` S1 short-circuit + `index_mapping.py` S2/S3 short-circuit + `stationarity.py` the parametric path) is a **hypothesis** to re-trace at implementation.

---

## §5. Guarded emit → exactly 398 live rows (Unknown 2.5)

The emitted MCP has `stat_task(g,t,m,n)$taskposs(g,t)` with per-term `$tech`/`$equipposs`/`sameas` guards, plus `task.fx(...)$(not (taskposs(g,t) and tech(g,m,n))) = 0`. GAMS instantiates the **398** rows where `taskposs∧tech` holds; the 368,626 fixed columns drop under MCP matching. The `$(not active)` fixing guard **exactly complements** the `$taskposs∧$tech`-active set, so the square-system count is `variables − fixed = active = 398`. Verification at landing: compile `sarf_mcp.gms` and assert exactly 398 `stat_task` rows and a square MCP.

---

## §6. Tractability gate (PR20) — MEASURED baseline (Unknown 2.2)

- **Measured current baseline (this task, 2026-07-24):** the emit runs **> 303 s and does not complete** (`.venv/bin/python -m src.cli data/gamslib/raw/sarf.gms`, killed at a 300 s cap; no output). The pipeline records `translate_failure` (the 600 s harness timeout). *This is the O(369K) cost.*
- **Pass threshold:** the symbolic re-emit must complete in **single-digit seconds** — O(active = 398) / O(constraints), the srpchase ~2.9 s reference. Measurement method: `/usr/bin/time -p .venv/bin/python -m src.cli data/gamslib/raw/sarf.gms -o sarf_mcp.gms`, `real` seconds, on a clean tree.
- **Pre-classification (PR20):** a **partial improvement that does not cross the threshold is a REPLAN, not progress.** If the parametric emit still takes minutes (an unexpected residual materialization site), or improves 303 s → e.g. 90 s but still exceeds the pipeline budget, that is a **failed** gate — sarf stays `translate_failure` and the track REPLANs. There is no "faster but still failing" partial credit.

> The post-change figure is an **in-sprint executed result** — this prep records only the *measured baseline* (> 303 s) and the *threshold* (seconds); the actual post-change timing is DESIGN-SPECIFIED.

---

## §7. Full-corpus regression harness (Unknowns 2.2, 2.3) — the shippability gate

The change touches the foundational AD flow, so it is **not shippable without proving corpus-safety byte-for-byte**:

1. **Atomic landing.** The 2-D constraint gate + the S1/S2/S3 short-circuit + the parametric `stat_task` (and every `stat_*` the short-circuited constraints touch) + `task.fx` land in **one change**. The gate makes `tbal`/`equipb1`/`equipb2` enumerate **zero** instances, so their `Jᵀ·λ` contributions to `stat_task` **must** come from the parametric path — a partial landing is an inconsistent MCP (multipliers with no stationarity coupling).
2. **141 byte-identical goldens.** Every non-sarf golden under `data/gamslib/mcp/` must be **byte-unchanged** — the proof that the symbolic-column predicate is sarf-only (§3). `--resolve-changed --since-commit 78ceaead` must report **sarf as the only changed golden** (sarf is `translate_failure` today, so its first successful emit *creates* `sarf_mcp.gms`).
3. **Determinism ×3** `PYTHONHASHSEED {0,1,42}` on the new `sarf_mcp.gms` (PR12).
4. **The 7-term + anti-pattern scan** (§4): `stat_task` matches the banked form term-by-term; the set-name-literal grep returns nothing.
5. **A shape13 property fixture** — a synthetic multi-dim variable with a runtime-gated active subset, asserting the emitted `stat_*` is parametric (one guarded row, not per-instance), fail-before/pass-after (the P7 catalog entry, Task 3).

---

## §8. REPLAN exit + disposition (Unknown 2.5)

**In-sprint disposition: DEFER / REPLAN to a dedicated symbolic-emit effort.** The design is complete and now *can* articulate the corpus-safety argument (§3) and the regression harness (§7) — so, unlike a refuted track, it is **implementable by a dedicated effort**. But the in-sprint call is unchanged from S32/S33/S34:

- **Reward = the lowest-leverage KPI:** +1 Translate (135 → 136), moving **neither Solve nor Match**.
- **Risk = corpus-wide, atomic, foundational:** a 20–28 h re-architecture of the `enumerate_variable_instances` → column-index → Jacobian → gradient → stationarity flow (all 6 call sites, all 142 models), where a mis-step regresses the 135 byte-stable models — the 4×-failed Sprint-26 path. No safe partial.
- **Budget context:** P1 (mine) also REPLAN'd in prep (Task 6), so the sprint's freed budget (P1 18–24 h + P2 20–28 h) is best concentrated on **P4** (ganges/gangesx, the designated bucket mover — +2 Solve/Match) + P6/P7, not on a foundational rewrite for +1 Translate.

**Explicit REPLAN triggers** (for a future dedicated effort, or if attempted in-sprint against advice): a **fourth enumeration site** surfaces; the parametric emit **re-triggers the timeout** (an unexpected residual materialization); **any non-byte-stable golden** on an unrelated model (the §3 predicate fires on a 142nd variable); or a **determinism break**. Any of these → sarf stays `translate_failure` (Translate 135); the de-risked hand-off is this document (the measured baseline, the 6-call-site corpus-safety surface, the 7-term derivation, the atomicity spec, the regression harness).

**Freed budget:** P2's 20–28 h → **P4** first, then P6/P7.

---

## §9. Known Unknowns verified by this task

- **Unknown 2.1** — ✅ **VERIFIED.** The three sites (S1 `constraint_jacobian.py:1002–1013`, S2 `enumerate_variable_instances` at `index_mapping.py:634` + `constraint_jacobian.py:78`, S3 `stationarity.py`) are re-confirmed live and complete; no fourth materialization site (the gradient/complementarity sites are additional *consumers* of the same column set, not new loci). Counts re-verified: 16·24·31·31 = 369,024 declared / 398 active.
- **Unknown 2.2** — ✅ **VERIFIED (baseline); DESIGN-SPECIFIED (post-change).** The current emit is **measured at > 303 s, non-terminating** (killed at a 300 s cap, no output) — the O(369K) cost, consistent with `translate_failure`. The pass threshold (single-digit seconds, O(active)) and the "partial improvement = REPLAN" pre-classification are specified; the post-change timing is an in-sprint result.
- **Unknown 2.3** — ✅ **VERIFIED.** The symbolic-column concept is designed (a guarded domain expression, one `col_to_var` entry) and the **corpus-safety argument is explicit**: all 6 `enumerate_variable_instances` call sites enumerated, and the change designed as a symbolic branch gated on a runtime-blow-up predicate that is sarf-only-by-construction, keeping the 141 other models' `col_to_var` byte-identical with determinism preserved. The residual "provably sarf-only" claim is discharged by the §7 harness (141 byte-identical goldens).
- **Unknown 2.4** — ✅ **VERIFIED.** The parametric cross-term path is designed against the banked 7-term `stat_task`, re-verified term-for-term against the `sarf.gms` constraint bodies, with every multiplier over the stat domain and **no set-name-literal indices**. (No term failed re-derivation — the banked form is correct.)
- **Unknown 2.5** — ✅ **VERIFIED.** The guarded emit (`stat_task$taskposs` + `task.fx$(not active)` + MCP matching) yields exactly the 398 live rows (the `$(not active)` fixing exactly complements the active set); the full-corpus regression harness + the shape13 fixture + determinism ×3 are specified.

**Handed to Task 10 (Phase-0 gate):** the O(active) tractability gate (measured baseline > 303 s → threshold seconds; partial-improvement-is-REPLAN), the 141-byte-identical-golden corpus-safety gate, the 7-term + anti-pattern scan, determinism ×3, atomic landing. **Handed to Task 11 (projection):** P2 = **+1 Translate (135 → 136) if it lands, but DEFER'd in-sprint** (foundational/atomic/lowest-leverage); its 20–28 h reallocates to P4/P6/P7. **Handed to Task 12 (schedule):** P2 needs no in-sprint execution slot; the freed budget front-loads P4.

---

**Document Status:** ✅ Complete — Sprint 35 Prep Task 7 (design complete; in-sprint DEFER)
**Last Updated:** 2026-07-24
**Owner:** Sprint 35 Planning Team

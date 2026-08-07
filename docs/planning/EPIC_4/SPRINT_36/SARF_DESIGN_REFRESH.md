# Sprint 36 — sarf P2 Symbolic-Emit Subsystem Design Refresh (Prep Task 5)

**Date:** 2026-08-07 · **Owner:** Sprint 36 execution team · **Branch:** `planning/sprint36-task5` · **Scope:** docs/analysis-only (measurements only; no `src/` change).
**Outcome: the banked S35 design (`../SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md` + `PHASE_0_ACCEPTANCE_GATES.md`) applies UNCHANGED — every premise re-confirms on current `main`: the blow-up is still >303s / non-terminating; the 3 sites + counts (369,024 declared / 398 active) hold; the 7-term derivation's constraint bodies are present; and the O(active) guarded-emit shape compiles clean + instantiates O(active), not O(Cartesian), under GAMS 54.2.1. GO to carry the design as-is (a 20–28h atomic re-architecture with the standing REPLAN triggers).** Verifies Unknowns 2.1, 2.2, 2.3, 2.4.

Reference: `../SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md` (the 3-site + 6-call-site + 7-term design), `../SPRINT_35/PHASE_0_ACCEPTANCE_GATES.md` (the O(active) timing gate). Code: `enumerate_variable_instances` (`src/ad/index_mapping.py:327`), the S1/S2/S3 sites (`constraint_jacobian.py`, `index_mapping.py`, `stationarity.py`).

---

## 1. Blow-up re-measured (Unknown 2.1)

**Timing (this task, 2026-08-07):** `.venv/bin/python -m src.cli data/gamslib/raw/sarf.gms` — **still running at a 330s cap without completing** ⇒ **>303s / non-terminating CONFIRMED** (the O(369K) failure). Identical to the S35 baseline (`SARF_SYMBOLIC_EMIT_DESIGN.md` §6: ">303s, killed, no output"). No improvement, no regression — the emit remains non-terminating in any pipeline budget.

**Counts re-verified (live from `sarf.gms`):** `g` = 16, `t` = 24 (`01*24`), `mn` = 31 (5 power sources + 3 harvesters + 23 implements). `task(g,t,mn,mn)` ⇒ **16·24·31·31 = 369,024** declared columns. Active = `taskposs(g,t) ∧ tech(g,m,n)`, both runtime-computed (`sarf.gms:371`, `tech` a data Table) — **not statically enumerable** (the fix genuinely cannot be "enumerate only the 398").

**The 3 sites re-confirmed + code-surface integrity:** `src/ad/constraint_jacobian.py`, `src/ad/index_mapping.py`, `src/kkt/stationarity.py` are all **byte-unchanged since the anchor `78ceaead`** (`git diff` empty); `enumerate_variable_instances` present at `index_mapping.py:327`. So the S1 (`constraint_jacobian.py` per-column diff), S2 (`enumerate_variable_instances` via `build_index_mapping`/`_precompute_variable_instances`), S3 (`stationarity.py` per-column `stat_task`) surfaces are unchanged. No fourth materialization site (the gradient/complementarity call sites are additional *consumers* of the same column set, per the design).

## 2. O(active=398) guarded-emit — compiles + instantiates correctly under GAMS 54 (Unknown 2.2)

A minimal `/tmp` fragment mirroring the design's guarded-emit shape was compiled under **GAMS 54.2.1** (`Versions/54/Resources/gams`):
```gams
stat_task(g,t,m,n)$taskposs(g,t).. 1 - cost*tech(g,m,n) =e= 0;   * the guarded stationarity equation
task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0;        * fix the vacuous columns
```
**Result — compiles clean (no `****` errors) and GAMS natively prunes the instantiation:**

| quantity | value (synthetic 3·2·3·3) | meaning |
|---|---|---|
| `ncart` = `card(g)·card(t)·card(mn)²` | **54** | the full Cartesian (the 369K analogue) — what an *unguarded* emit materializes |
| `ndomain` = `sum((g,t,m,n)$taskposs(g,t), 1)` | **18** | what `stat_task$taskposs(g,t)` **actually instantiates** — GAMS restricts to the taskposs-active domain |
| `nactive` = `sum(…$(taskposs and tech), 1)` | **4** | the taskposs∧tech live set (the 398 analogue), after the per-term `$tech` guards + `task.fx` |

So GAMS's `$`-conditioned equation instantiation is confirmed: `stat_task(g,t,m,n)$taskposs(g,t)` scales **O(taskposs-active), not O(Cartesian)** (18 ≪ 54), and the per-term `$tech`/`$equipposs` guards + `task.fx$(not active)=0` reduce to the fully-active set (4, the 398 analogue). For sarf this is the difference between 369,024 and ~398. **The guarded-emit shape is valid GAMS 54 and achieves O(active) by construction** — the parametric emit's remaining job is to *produce* this shape from the symbolic column without materializing the 369K instances (the S1/S2/S3 short-circuit, §4 of the banked design).

## 3. 7-term `stat_task` derivation re-validated (Unknown 2.3)

The seven constraint bodies the derivation differentiates are all present in `sarf.gms` and structurally unchanged:

| term | constraint (current `sarf.gms`) | banked ref |
|---|---|---|
| 1–2 | `tbal(g,t)$taskposs(g,t)..` (`:426`) + the `tadj` harvest-c adjustment | §4 tbal |
| 3 | `labor(t)..` (`:438`) | §4 labor |
| 4 | `equipb1(m,t)$equipposs(m,t)..` (`:442`) | §4 equipb1 |
| 5 | `equipb2(n,t)$equipposs(n,t)..` (`:445`) | §4 equipb2 |
| 6 | `acost3.. cost("operating") =e= sum((g,t,m,n)$taskposs(g,t), oc(g,m,n)·task(g,t,m,n))` (`:454`) | §4 acost3 (the S1 parametric ∂) |
| 7 | `task.lo = 0` | §4 |

(Line numbers drifted a few lines vs the S35 doc's `:412–413`/`:439` for equipb/labor — the raw source is the gitignored corpus, minor cosmetic shift — but the constraint *structures* are identical.) **Every multiplier is indexed by the stat equation's own domain** (`nu_tbal(g,t)`, `lam_labor(t)`, `lam_equipb1(m,t)`, `lam_equipb2(n,t)`, `nu_acost3`, `piL_task(g,t,m,n)`) — **no set-name-literal (quoted-set-name) indices** (the reverted Sprint-26 `nu_slack("srn")` anti-pattern). The banked 7-term form applies unchanged; a silently-wrong `stat_task` remains the worst failure mode, so the 7-term match is the correctness anchor at landing.

## 4. Phase-0 timing gate + regression harness re-confirmed (Unknowns 2.2, 2.4)

- **Timing gate (PR20):** the re-emit must complete in **single-digit seconds** — O(active=398)/O(constraints), the srpchase ~2.9s reference. **Measured baseline this task: >303s / non-terminating** (§1). *A partial improvement that does not cross the threshold is a REPLAN, not progress* (no "faster but still failing" credit). The post-change timing is an in-sprint executed result (DESIGN-SPECIFIED here).
- **No set-name-literal indices (Unknown 2.4):** the 7-term form uses own-domain multipliers (§3) → the landing scan `grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` must be empty. Design-level VERIFIED; the empirical scan runs at landing (needs the emitted golden).
- **Determinism ×3 + byte-stable golden (Unknown 2.4):** the full-corpus regression harness — 141 byte-identical goldens + determinism ×3 `{0,1,42}` + `--resolve-changed` GO — is the shippability gate (the corpus-safety proof that the symbolic-branch predicate is sarf-only). These are **landing gates** (they need the fix's output); the design specifies them. Design-level VERIFIED; empirical at landing.
- **Atomicity:** the 2-D constraint gate + S1/S2/S3 short-circuit + the parametric `stat_task` + `task.fx` land in **one change** (a partial landing = an inconsistent MCP — multipliers with no stationarity coupling).

## 5. Go / No-Go + REPLAN exit

**GO to carry the banked design UNCHANGED** — every premise re-confirms: blow-up >303s (measured), counts + 3 sites + code surfaces unchanged, 7-term derivation intact, O(active) guarded emit valid + instantiation-confirmed under GAMS 54. No refresh edit to the S35 design is required.

**Disposition unchanged (the honest S35 call):** sarf is a **20–28h atomic, foundational re-architecture** of the `enumerate_variable_instances` → column-index → Jacobian → gradient → stationarity flow (6 call sites, 142 models) for the **lowest-leverage bucket (+1 Translate)** — the 4×-failed Sprint-26 path, no safe partial. It is **not landable without the full-corpus regression harness** (the byte-stable proof that the symbolic-branch predicate is sarf-only).

**Standing REPLAN triggers** (carry to a dedicated effort, or if attempted in-sprint against advice): a 4th enumeration site surfaces; the parametric emit re-triggers the timeout; any non-byte-stable golden on an unrelated model (the predicate fires on a 142nd variable); or a determinism break. Any → sarf stays `translate_failure` (Translate 135); the de-risked hand-off is the S35 design + this refresh (measured baseline, 6-call-site corpus-safety surface, 7-term derivation, atomicity spec, regression harness).

**Budget note:** at 20–28h this is the sprint's **largest single track**; schedule it so a REPLAN (its most likely outcome) surfaces early, not on Day 12.

---

**Document Status:** ✅ Complete — Sprint 36 Prep Task 5 (sarf design refresh; GO, design applies unchanged)
**Last Updated:** 2026-08-07
**Owner:** Sprint 36 Execution Team

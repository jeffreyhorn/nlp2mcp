# rocket #1462 + hhfair/CGE #1236 — PATH-Consultation Submission + Case-c Forcing Plan

**Prep Task:** 7 (Priority 5) · **Date:** 2026-07-16 · **Owner:** Sprint 33 prep (solver/KKT specialist)
**Status:** design complete — **PROCEED (hand-off + forcing survey).** rocket's PATH-consultation input is FINALIZED (Sprint 32); this plan defines the **Sprint-34 submission mechanism** + the `--force` lever survey for the Case-c family. Any +Solve/+Match is **conditional** (forcing/consultation-dependent), not a firm KPI. **The objective-gradient sign flip stays BANNED.**

> **PR24 discipline:** validated read-only (DB status + the banked harness re-confirm); no `src/` change. The `--force` survey is an in-sprint exercise; this document plans it.

---

## 1. Case-c scope guard — re-confirmed (Unknown 5.3)

The Case-c family, from the current DB:

| Model | outcome | MS | cmp | Case-c signature | forcing target |
|---|---|---|---|---|---|
| **rocket** | model_infeasible | **5** | not_tested | boundary rows `stat_ht(h0)`/`stat_ht(h50)`/`stat_step` (move with the warm-start value); interior near tol; dual CONSISTENT | +Solve (MS-5 → MS-1) |
| **hhfair** | model_optimal | 1 | **mismatch** | `stat_u` (objective-defining intermediate var; `obj = prod(u**ufact)`); cold 72.147 ≠ NLP 87.159 (spurious local optimum) | +Match (mismatch → global) |
| **irscge** | model_optimal_presolve | 1 | match (methodology) | `stat_xp` (`UU = prod(Xp**alpha)`); cold 25.5085 ≠ match 26.0914 | methodology → genuine cold-match |
| **lrgcge** | model_optimal_presolve | 1 | match (methodology) | `stat_xp`; same | methodology → genuine |
| **moncge** | model_optimal_presolve | 1 | match (methodology) | `stat_xp`; same | methodology → genuine |

- **rocket** — the harness residual concentrates on the discretized-optimal-control **boundary** rows (`stat_ht(h0)` 1.00, `stat_step` 0.50, `stat_ht(h50)` 0.44) that move with the warm-start value; the interior is near tolerance; dual-transfer CONSISTENT (closure 1.53e-10). Re-confirmed on the current tree at the Sprint-32 Day-9 finalization; the emit is unchanged since (DB byte-unchanged), and the DB confirms rocket MS-5. **A forcing problem, not an emit bug.**
- **hhfair + CGE cluster** — the residual concentrates on the **objective-defining intermediate variable** (`stat_u` / `stat_xp`), where `nu_obj = ±1` (no free multiplier to correct it); D1∧D2∧D3 hold → `case_c_objdef` (ISSUE_1236 CLOSED, S32). The cold solve sits at a non-global local optimum of a non-convex model; the match is reachable only via the presolve warm-start.

**The sign flip is BANNED** (control-refuted 4× S30–S31: hhfair 72.147 → 22.144 *worse*; the CGE-cluster ν_objective reduction inert since `nu_obj=±1`). **No Day-1 sign-flip attempt** — do not re-litigate it.

## 2. rocket PATH-consultation submission mechanism (Unknown 5.1)

The rocket input (`SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`, **FINALIZED**) is submission-ready — three self-contained parts:
1. **The concrete question (§3):** which PATH option-set / regularization schedule / reformulation forces convergence for the discretized optimal-control MCP — with the division-by-variable reformulation as a *ruled-out* candidate (targeting the intrinsic structure, not the Jacobian conditioning).
2. **The ruled-out-lever survey (§2):** PATH options (best INFES 382), μ-continuation, multistart, division-by-variable reformulation — all MS-5, so the authors don't re-suggest them.
3. **The reproducible case:** `python -m src.cli data/gamslib/raw/rocket.gms -o rocket_mcp_presolve.gms --nlp-presolve; gams rocket_mcp_presolve.gms` → MS-5 from the embedded NLP optimum; the `--force homotopy` scaffold adds the μ-continuation driver + optfile.

**Submission mechanism (the Sprint-34 hand-off):** the packaged input feeds the **Sprint 34** ("PATH Author Consultation & Solution Forcing") sprint — Sprint 33 **submits** it (a self-contained artifact: the question + survey + reproducible case + the `--force` scaffold), and Sprint 34 conducts the author back-and-forth. A recommended option-set/schedule from the authors plugs into the `--force {homotopy,optfile}` scaffold. **What is handed off:** the FINALIZED doc (as the consultation brief) + the two-command reproducer + the scaffold-emitted `rocket_mcp_forced.gms`. **To whom:** the Sprint-34 PATH-author consultation task (Michael Ferris / Steven Dirkse — External Dependencies).

## 3. The `--force` lever survey plan (Unknown 5.2)

Exercise `--force [homotopy|multistart|optfile]` across the Case-c family. **"A lever crosses"** = the model reaches its **global** optimum at MS-1 (rocket: MS-5 → MS-1 = +Solve; hhfair: mismatch → the 87.159 global = +Match; CGE cluster: a genuine **cold** match at 26.0914, converting methodology → genuine floor). **"Banked"** = no lever crosses → the model stays documented Case-c (fed to the consultation / left as methodology).

| Model | Most-promising lever | Rationale | Expected outcome |
|---|---|---|---|
| **rocket** | (survey **exhausted**) | homotopy/multistart/optfile all MS-5 (banked); warm-from-NLP-optimum already fails, so multistart is a priori unpromising | **banked → Sprint-34 consultation**; no in-sprint +Solve |
| **hhfair** | **multistart** | MS-1 at a *spurious* local optimum (72.147); a multi-start `.l`-perturbation loop could find the 87.159 global (non-convex CES+bilinear) | conditional +Match if a start crosses; else banked Case-c |
| **irscge/lrgcge/moncge** | **multistart** | match via presolve (methodology); a cold multistart reaching the 26.0914 global would convert methodology → genuine floor | conditional +genuine-floor if a start crosses; else stays methodology |

**Survey discipline:** every candidate is re-confirmed Case-c (residual clean at the NLP point) **before** forcing (keeps them forcing problems, not latent emit bugs, §1); the sign flip is not exercised. The survey is **read-only forcing** (no emit change) — the `--force` scaffold only adds a solver driver/optfile, not an emit transform.

## 4. Sizing + the conditional-KPI note

**8–12 h:**
- Submit the rocket consultation input to the Sprint-34 hand-off + package the reproducer/scaffold artifact (~2–3 h).
- The `--force` (multistart-primary) survey across hhfair + irscge/lrgcge/moncge + a rocket re-confirm — run, record "crosses vs banked", assert `modelstat` on each (~4–6 h).
- Document the outcomes (any +Match/+genuine-floor cross; else the banked Case-c survey for the consultation) + determinism on any changed result (~2–3 h).

**Conditional-KPI note:** **no firm KPI.** rocket's +1 Solve is conditional on the Sprint-34 consultation (survey exhausted). Any hhfair +Match or CGE-cluster methodology→genuine conversion is conditional on a `--force` lever crossing a non-convex model's global optimum — a priori unpromising (warm-from-optimum already fails for rocket; the CGE cold optima are spurious). The realistic modal outcome is **banked Case-c** (the family stays documented non-convex, no bucket move); the value is the clean Sprint-34 hand-off + the exhaustive forcing survey.

## 5. Outcome for the Known Unknowns

| Unknown | Verdict | Finding |
|---|---|---|
| **5.1** | ✅ VERIFIED | The rocket PATH-consultation input is FINALIZED + submission-ready (concrete question + ruled-out-lever survey + reproducible case + `--force` scaffold). The Sprint-34 hand-off mechanism is defined: Sprint 33 submits the self-contained brief; Sprint 34 conducts the author consultation; a recommended option-set plugs into the scaffold. |
| **5.2** | ✅ VERIFIED (design-level) | The `--force` (homotopy/multistart/optfile) survey is planned across the Case-c family with the "lever crosses" (global MS-1) vs "banked" criteria. rocket's survey is **exhausted** (all MS-5 → banked); hhfair/CGE multistart is the only untried avenue (conditional, a priori unpromising). The actual run is the in-sprint P5 exercise, not this docs-only prep. |
| **5.3** | ✅ VERIFIED | Each family member's residual is clean at the NLP point (Case-c, not an emit bug): rocket's boundary signature + the hhfair/CGE `case_c_objdef` signature (`nu_obj=±1`), dual-transfer CONSISTENT. **The sign flip stays BANNED** (control-refuted 4×); no re-litigation. |

---
**Document Created:** 2026-07-16 · **Owner:** Sprint 33 prep (solver/KKT specialist)

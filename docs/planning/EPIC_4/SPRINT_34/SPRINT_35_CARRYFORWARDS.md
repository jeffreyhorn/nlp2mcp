# Sprint 34 → Sprint 35 Carryforwards

Each item is a **de-risked, control-confirmed, precisely-pinned** hand-off — a specification, not an open question. Anchor: S34 close (this branch); code/DB byte-unchanged since S33 close `750803b2`.

## 1. mine — head-offset dual subsystem (P1, #1443)

**Status:** REPLAN'd Day 1 (H3′). The cold-MS-1 control refuted H_dual: mine's head-offset dual boundary is **`x.m=0`-degenerate**, and no keying-invariant emit change reaches cold MS-1 (the reframed gate — harder than a warm-residual check on a degenerate LP). **Hand-off:** a dual-architecture rethink of the head-offset transfer, not a single-site fix; the `x.up=inf` measurement error stays **BANNED**. `DAY1_PROGRESS_NOTES.md`.

## 2. sarf — symbolic `stat_task` emit mode (P2, #1385)

**Status:** REPLAN'd Day 6 (scope/risk; design sound). The blow-up is `enumerate_variable_instances` materializing 369,024 `task` columns; it is **foundational** (builds the `col_to_var` index the whole Jacobian→gradient→stationarity flow iterates for all 142 models), so making `task` symbolic is a **coordinated corpus-wide re-architecture** (a new parametric cross-term path), atomic, **20–28 h**, for the lowest-leverage bucket (+1 Translate). The 398 active columns are not statically enumerable (`taskposs` runtime-computed). **Hand-off:** a dedicated effort with a full-corpus regression harness. `DAY6_PROGRESS_NOTES.md`.

## 3. fawley — qsb/pbal constraint-index-diagonal `sameas` correction (P3, #1111/#1112)

**Status:** DEFER'd Day 5 (risk/reward; H-b, not a correctness REPLAN). The genuine fix is a **constraint-index-diagonal** change in the ~1430-line `_add_indexed_jacobian_terms` (a dozen `sameas` paths, shared with mbal/cesam2/camcge/ps2). It closes `stat_bq` 473→18.468 (genuine), but fawley is **H-b**: sameas + all bound-transfers → warm residual ~0 yet the MCP still solves **MS-5 @ 4399.557** (LP opt 2899.25) — a non-emit divergence. **Hand-off:** a dedicated effort + a 2-D-cohort regression harness; the +Solve is a **forcing tail** (not emit), the floor +1 contingent on forcing. `DAY5_PROGRESS_NOTES.md`.

## 4. P6 `$141` NaN-cleanup fix + the ganges `$149` CES/LES AD bug (banked)

**Status:** re-triaged Day 11; the cohort is deeply multi-root (three independent roots). **Banked, verified:** the `$141` fix — skip `.l`-attribute-referencing (calibration) params in `emit_post_assignment_na_cleanup` (a proposed `_param_assignment_references_varref_attr` helper mirroring `_param_assignment_has_division`) — removes ganges's 15 `$141`; reverted because it recovers 0 bucket and its slow-emit CGE goldens are un-regenerable in the CI budget. **The blocker hand-off:** `$149` = an **uncontrolled index in the stationarity emit** — ganges `stat_pc`'s CES/LES `prod(j, (pc(j)/pc00(j))**ac(j,r))` derivative w.r.t. `pc(i)` leaves a free `j` — a **deep AD-core product-rule bug** that gates ganges/gangesx/dinam/indus/turkpow/clearlak; plus `$145` (a universal-set `*`-domain NaN-cleanup gap) and turkey's `$161` (dotted-tuple set-declaration emit). A dedicated ganges-recovery effort re-applies the `$141` fix + tackles `$145`/`$149` (and can afford the slow golden regen). `DAY11_PROGRESS_NOTES.md`.

## 5. camcge — dual-consistent Walras numéraire (#1330 → Epic 5)

**Status:** Epic-5-deferred Day 10. The S1∧S2∧S3 detector cohort is confirmed (fires only camcge: cold MS-4 @ omega 191.7346; the four CGE siblings cold MS-1). The full Walras-law dual redefinition (keep the redundant market's multiplier available while making the reduced system full-rank) is Epic-5 research — the banked price-pin variant reaches the correct primal but stays MS-4 (INFES on gdp/depreq/hhsaveq/gruse), and 3+ sprints of prep failed to reach MS-1. **Hand-off (Epic 5):** the numéraire recipe + the residual-singularity characterization + the detector. `DAY10_PROGRESS_NOTES.md`.

## 6. rocket — the FINALIZED PATH-consultation input (→ Sprint-35 consultation)

**Status:** submitted Day 10. Case-c re-confirmed (CASE_C_OBJDEF, boundary signature, dual CONSISTENT — a forcing problem, not an emit bug; the sign flip stays **BANNED**). The FINALIZED input (`SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` — the concrete question + the ruled-out-lever survey + the two-command reproducer) feeds the **Sprint-35 "PATH Author Consultation & Solution Forcing"** sprint. The `--force` survey is exhausted (all MS-5); the +1 Solve is Sprint-35-conditional. `DAY10_PROGRESS_NOTES.md`.

## Banked follow-ons (not Sprint-35-primary)

- **Case-c family** (cesam/lnts/hhfair/CGE-cluster) — `case_c_objdef`, `nu_obj = ±1`; no free multiplier; the objective-gradient sign flip is **BANNED** (control-refuted 4×). Documented non-convex; residuals clean at the NLP point (forcing, not emit).
- **The residual `path_syntax_error` cohort per-model roots** (dinam/indus `$140`+`$149`; turkpow/clearlak `$149`+`$171`; turkey `$161`) — each characterized Day 11; verify per-model (the multi-root discipline holds).

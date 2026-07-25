# Sprint 35 Phase-0 Acceptance Gates (PR20 + PR24 + PR27)

**Prep Task:** 10 (Critical, on the critical path) · **Date:** 2026-07-24 · **Owner:** Sprint 35 prep (gates/discipline)
**Day-0 code anchor:** `78ceaead` (S34 close — the `--resolve-changed` baseline for every gate) · **Measurement tree:** `5efd0c9c` (`main` at the S35 prep Task-9 merge)
**Scope:** docs-only — consolidates the per-track PROCEED/REPLAN gates for the five Sprint-35 priorities into one index. The authoritative per-track detail lives in each Task-4–9 design doc; this is the single-page gate index + the control-experiment discipline.

> **The defining shape of Sprint 35's gates: four of the five tracks are already REPLAN'd/DEFER'd/Epic-5-deferred IN PREP** (P1 mine, P2 sarf, P5 camcge/rocket), and P3 fawley is a correctness-only landing with **0 bucket** (H-b). **P4 (ganges/gangesx) is the sole live PROCEED gate** — the one track that can move a bucket. So most gates below record their exit as **taken in prep** (the control-first discipline surfacing the disposition *before* Day 0, better than S34's Day-1/Day-5 surfacing), and the P4 per-root gate is the active one the sprint executes.

---

## 0. The standing discipline (why these gates exist)

- **PR20 — a tractability/emit-budget gate where performance is the failure mode** (P2 sarf: the gate is a *timing* threshold, not a residual).
- **PR24 — the banked fix surface is a Day-0-re-confirm hypothesis, not fact.** S32/S33/S34 REPLAN'd/deferred every deep track after a control refuted the banked premise. Each gate frames its fix surface as a hypothesis re-confirmed in the Task-4–9 designs.
- **PR27 — the `/tmp` control runs BEFORE any high-blast-radius `src/` change.** Every emit gate's PROCEED precondition is a `/tmp` control that must pass first.
- **Assert `modelstat` before reading an objective off a solve** (the S31 measurement-error lesson: relaxing `x.up=inf` read the embedded LP and produced 34 spurious unmatched-var errors). Every warm/cold solve step asserts `mcp_model.modelstat` before any objective read. **`x.up=inf` is BANNED** (mine). **The objective-gradient sign flip is BANNED** (the Case-c family, control-refuted 4×).
- **No bucket → no `src/`** (§2): a correctness fix that moves no bucket does not ship if it churns un-regenerable goldens — with the **S34-P4 exception** (fast, regenerable goldens + `--resolve-changed` GO) written out for P4's expected use (§2).

---

## 1. Per-track gates (P1–P5)

### P1 — mine Head-Offset Dual Subsystem (#1443) — **REPLAN'd IN PREP (exit taken)**

- **Disposition:** **REPLAN — decided in prep** (Task 6, `MINE_DUAL_ARCHITECTURE_DESIGN.md`). No emit-side dual architecture can supply the +16000 the `x.m = 0`-degenerate boundary requires; the whole keying/pairing candidate space is value-invariant (S34 proved H_dual value-invariant on the cold solve), and the only non-invariant lever (an LP-side reformulation) is out of emit scope. mine is a **primal-degenerate LP whose warm KKT point is not MCP-reconcilable by emit**.
- **The gate (pre-refuted — recorded for the record):** the PROCEED precondition would be a `/tmp` control driving the warm residual → 0 at **all** bound-active `stat_x` rows AND leaving interior rows unchanged at 0, **then** cold/presolve **MS-1 @ 17500** (`modelstat` asserted; `x.up=inf` BANNED). **The gate is the *cold* solve, NOT the warm residual `N → 0`** (un-hittable by a value-invariant keying/pairing change). **No candidate reaches this gate** — the reachability screen (Task 6 §3) rejected all four before any `/tmp` control was warranted; the S34 Day-1 control already refuted the strongest candidate (H_dual).
- **Exit (taken):** mine stays `model_infeasible`; **no `src/`**; hand to the **Sprint-36 PATH consultation** (the primal-degenerate-LP question); the 18–24 h P1 budget → **P4** first, then P6/P7. **0 in-sprint bucket / 0 floor.**

### P2 — sarf Symbolic/Parametric `stat_task` Emit Mode (#1385) — **DEFER'd IN PREP (exit taken)**

- **Disposition:** **DEFER — decided in prep** (Task 7, `SARF_SYMBOLIC_EMIT_DESIGN.md`). The design is complete and shippable-to-a-dedicated-effort, but the in-sprint risk/reward is unchanged from S32/S33/S34: a 20–28 h from-scratch re-architecture of the foundational AD column-index → Jacobian → gradient → stationarity flow (all 142 models, atomic, no safe partial) for the **lowest-leverage KPI** (+1 Translate).
- **The gate (a TIMING gate, PR20 — specified, not executed):** the symbolic re-emit must be **O(active = 398), not O(369K)** — timed `sarf_mcp.gms` emission in **single-digit seconds** (the srpchase ~2.9 s O(active) reference). **Measured baseline this sprint: > 303 s and non-terminating** (Task 7 — killed at a 300 s cap, no output; the current O(369K) failure). **Partial improvement that does not cross the threshold = REPLAN, not progress** (no "faster but still failing" credit). Plus: `stat_task` matches the banked 7-term derivation with **no set-name-literal indices** (`grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` = empty); **atomic** landing (S1/S2/S3 + `task.fx` in one change — a re-emit without cross-terms = an inconsistent MCP); **141 byte-identical goldens** + determinism ×3 `{0,1,42}`; `--resolve-changed --since-commit 78ceaead` GO (sarf the only changed golden).
- **Exit (taken):** sarf stays `translate_failure` (Translate 135); **no `src/`**; the design hands to a dedicated symbolic-emit effort; the 20–28 h P2 budget → **P4/P6/P7**. **0 in-sprint bucket.** In-sprint REPLAN triggers (for a future effort): a 4th enumeration site, a determinism break, any non-byte-stable unrelated golden, or a re-triggered timeout.

### P3 — fawley Constraint-Index-Diagonal Correction + Forcing (#1111/#1112) — **PROCEED (correctness-only, 0 bucket)**

- **Disposition:** **PROCEED for correctness IF leak-free** (Task 8, `FAWLEY_DIAGONAL_DESIGN.md`) — but **0 in-sprint bucket** (H-b, re-confirmed + strengthened). The +Solve is a **P5/Sprint-36 forcing hand-off**, not a P3 deliverable.
- **PROCEED precondition (PR24/PR27 `/tmp` before `src/`, `modelstat` asserted):** the constraint-index-diagonal `$(sameas(cfq__,cf))` guard on the `qsb`/`pbal` terms must drive **`max|stat_bq| → 0`** (machine zero) in a `/tmp` control — **NOT** the 96% partial (473 → 18.468; post-P4 the 18.468 cc-dist residue is expected already handled, so → 0). **The gate is scoped to `max|stat_bq|`**, not the harness's global max residual (which retains the emit-correct `stat_trans(tr-2)` non-emit residual — Task 8's re-measurement finding). Fix surface: the constraint-index-diagonal predicate in `_add_indexed_jacobian_terms` (`src/kkt/stationarity.py:5861`), distinct from #1049 (`:7176`, variable-heavier) and #1110/#1111 (variable-index diagonal) — a **hypothesis** to re-trace. **Leak-free:** **no mbal-term change**, the 1-D core (polygon/ps2_s/ps3_s_gic) byte-identical, and the 2-D cohort (cesam2/camcge/ps2_f_s/ps2_s/ps3_s_gic/polygon) byte-identical; `--resolve-changed --since-commit 78ceaead` GO with fawley the only changed golden.
- **REPLAN exit (gate leak):** any mbal-term or 2-D-cohort/1-D-core change, or `max|stat_bq|` not reaching 0 → DEFER again (a dedicated effort + the 2-D-cohort harness); budget → P4. **The +Solve is explicitly out of P3 scope** (H-b → the Sprint-36 `--force` survey); the +1 genuine floor is contingent on a cold match, which H-b precludes without forcing.

### P4 — ganges/gangesx Multi-Root Recovery — **PROCEED (the sole live bucket gate)**

- **Disposition:** **PROCEED (per-root sequence)** — the sprint's designated best-shot mover (Task 5 `GANGES_RECOVERY_DESIGN.md` + Task 4 `GANGES_149_PRODUCT_RULE_ANALYSIS.md`). Target **+2 Solve / +2 Match / −2 path_syntax_error** (+2 genuine floor if ganges/gangesx cold-match). **`$149` is a code, not a root — only ganges/gangesx are product-rule beneficiaries** (Task 4; dinam/indus/turkpow/clearlak are P6 residual).
- **PROCEED precondition — a PER-ROOT gate sequence** (`$141` → `$145` → `$149`, each individually `--resolve-changed`-gated, all shipping as one coherent P4 landing; `modelstat` asserted at every solve):
  1. **`$141`** — re-apply the banked-and-verified fix (`_param_assignment_references_varref_attr` skip in `emit_post_assignment_na_cleanup`, `src/emit/original_symbols.py:152`, mirroring `_param_assignment_has_division:137`); **verified this sprint to remove all 15 `$141`** (Task 5, scratch re-emit). Collateral: ~9 `.l`-calibration models regenerate (chakra/dinam/gancnsx/prolog/saras/senstran/shale/tfordy/turkey; NOT the data-calibrated CGE cluster) — golden-byte drift, no bucket change.
  2. **`$145`** — the universal-set (`*`-domain) skip (`if any(d == "*" for d in param_def.domain): continue` in the same cleanup loop); independent of `$141` (verified: the `$141`-only re-emit leaves `$145×3`).
  3. **`$149`** — the AD-layer product-rule fix (`src/ad/derivative_rules.py:_diff_prod:3276` + the emit-alias contract, Task 4 — **NOT** the prior's `stationarity.py:_add_indexed_jacobian_terms` surface, refuted). **`/tmp` control BEFORE `src/`:** the correction must reproduce Task 4's **hand-derived `stat_pc` cross-term** `prod(j,(pc(j)/pc00(j))**ac(j,r)) * ac(i,r)/pc(i)` (`i` controlled, no free `j`) and drive ganges's 9 `$149` → 0, **without perturbing the 18-model prod-in-stationarity regression set** (lmp2 most sensitive — the name-match case the collapsed `_diff_prod` branch relies on must stay byte-identical).
- **The per-model verification protocol (encoded into the gate so it cannot be skipped under time pressure)** — for **ganges and gangesx independently** (never inferred from one another; the exact assumption S34 got wrong): emit → compile (`gams a=c`) → **count residual `$NNN` by code (assert 0)** → translate → solve (cold AND presolve, `modelstat` asserted) → bucket → match classification (cold-match = genuine floor; presolve-only = methodology). **Compile-clean-but-not-solving is NOT a recovery** (it is `path_syntax_error → model_infeasible`, a different bucket) — report it as such.
- **⚠️ No bucket moves until all three roots land** (Task 5, empirically proven: the `$141`-only re-emit leaves `$145×3 + $149×9`). A mid-sequence flat KPI is the **expected** state, not a failure. The goldens regenerate per Task 3's **measured** budget (scoped `check_golden_staleness.py --models ganges,gangesx,clearlak,turkpow,…`, ~8.2 min for the slow four; fits a normal ≤ 12 h day) + determinism ×3.
- **REPLAN exit:** the `$149` `_diff_prod` correction cannot be made surgical against the 18-model regression set → **bank all three** (steps 1–2 alone = 0 bucket + golden churn, exactly the S34-banked outcome — no `src/` ships) and reallocate P4's budget to P6/P7.

### P5 — camcge Dual-Consistent Walras (#1330 → Epic 5) + rocket PATH (#1462 → Sprint 36) — **Epic-5-deferred / hand-off (exit taken)**

- **Disposition:** **camcge Epic-5-deferred; rocket a Sprint-36 hand-off** (Task 9, `CAMCGE_ROCKET_PLAN.md`). **0 in-sprint bucket.**
- **camcge gate (the Epic-5 `/tmp` gate — DESIGN-SPECIFIED, expected MS-4):** the `/tmp` prototype of the **full** dual-consistent redefinition (keep every market-clearing row + the consumption-weighted numéraire + the Walras-law dual redefinition) must reach **MS-1 at omega 191.7346** (`modelstat` asserted), verified against the KKT **dual** (not just the primal). The **S1∧S2∧S3 detector** must flag **only** camcge (S3 = cold-MCP-singular-at-iter-0; the four CGE siblings pass through cold MS-1 — DB-confirmed; the S34 P4 change touched no sibling golden). **Expected outcome: MS-4** (the price-pin variant + 3+ sprints of variants all stayed MS-4 at the correct primal, INFES on gdp/depreq/hhsaveq/gruse), so the **per-model-numéraire declaration is the documented Epic-5 fallback**. **camcge is explicitly excluded from the in-sprint Solve target.**
- **rocket gate:** **no solve gate** — a hand-off. Re-confirm the residual is **clean at the NLP point** (CASE_C_OBJDEF; `stat_ht(h0)`/`stat_ht(h50)`/`stat_step` boundary signature; dual CONSISTENT closure 1.53e-10 — re-confirmed live, Task 9) so rocket stays a *forcing* problem; the sign flip is not exercised (BANNED). The FINALIZED input submits to **Sprint 36** (with the "Sprint 33"/"Sprint 35" labels retargeted — Task 9's renumbering fix); mine + fawley bundle into the same Sprint-36 package.
- **Exit (taken):** camcge → Epic 5; rocket → Sprint 36. No `src/`; 0 in-sprint bucket / 0 floor.

---

## 2. Cross-cutting gates

Every emit-touching PR (in Sprint 35, only **P4** and — if it lands — **P3** touch `src/`) must pass:

- **Determinism ×3** — byte-identical emit under `PYTHONHASHSEED ∈ {0,1,42}` (PR12), on every changed golden.
- **Golden-staleness check** (PR26) — `scripts/sprint_audit/check_golden_staleness.py`; for P4 use the **scoped** `--models ganges,gangesx,clearlak,turkpow,<collateral>` invocation (Task 3), **never** the unscoped 170-golden `make regen-goldens` (its contention caused the S34 soft-timeout).
- **Presolve-divergence detector** — `scripts/diagnostics/check_presolve_divergence.py`.
- **`--resolve-changed --since-commit 78ceaead`** — the S34-close anchor; GO means every *unchanged* golden retains its bucket (the changed goldens are exactly the track's own). **NB the anchor advances from S34's `750803b2`** (the P4 sense-aware bound-transfer + 11 presolve goldens landed in that window; Task 2).
- **`kkt_residual.py`** (PR27) — the Case-(a/b/c) verdict engine every gate cites.

### The "no bucket → no `src/`" rule + the S34-P4 exception (written out for P4's expected use)

**Rule:** a correctness fix that moves **no bucket** does not ship if it would leave stale/un-regenerable goldens. This banked the S34 `$141` fix (0 bucket + slow-emit CGE goldens judged un-regenerable). **The S34-P4 exception:** a 0-bucket correctness fix **may** ship if its goldens are **fast + regenerable + `--resolve-changed` GO** (the S34 P4 sense-aware bound-transfer shipped under this exception).

**P4 is expected to invoke this rule at every step:** steps 1 (`$141`) and 2 (`$145`) move **no bucket alone** (Task 5, proven), and they touch collateral goldens — so they **do not ship on their own**. They ship **only** as part of the all-three-roots landing that recovers ganges/gangesx (a real bucket move). If `$149` REPLANs (step 3 not surgical), steps 1–2 are **banked, not shipped** — exactly the S34 outcome, now with the difference that Task 3 **measured** the goldens as regenerable (~8.2 min scoped), so the *exception* is satisfiable if a bucket move materializes. The rule's discriminator for P4: **does the full three-root landing move ganges/gangesx out of `path_syntax_error`?** If yes → ship (goldens regenerable, `--resolve-changed` GO). If no → bank all three.

---

## 3. Gate summary table

| Track | Model | Disposition | PROCEED precondition (control-before-`src/`) | Exit |
|---|---|---|---|---|
| **P1** | mine (#1443) | **REPLAN'd in prep** | (pre-refuted) cold MCP MS-1 @ 17500, `modelstat`, `x.up=inf` BANNED — no candidate reaches it (whole keying/pairing space value-invariant) | → Sprint-36 consultation; 18–24 h → P4/P6/P7; 0 bucket |
| **P2** | sarf (#1385) | **DEFER'd in prep** | (timing, PR20) O(active=398) seconds, not the **measured > 303 s**; partial improvement = REPLAN; 141 byte-stable + det ×3 + atomic | → dedicated effort; 20–28 h → P4/P6/P7; 0 bucket |
| **P3** | fawley (#1111/#1112) | **PROCEED (correctness, 0 bucket)** | max `stat_bq` residual → 0 (not the 96% partial; scoped to `stat_bq`); no mbal/1-D/2-D-cohort change; GO | gate leak → DEFER; **+Solve → Sprint-36 forcing (H-b)**; floor forcing-contingent |
| **P4** | ganges/gangesx | **PROCEED (the live bucket gate)** | **per-root** `$141`→`$145`→`$149`, each `--resolve-changed`-gated; `$149` `/tmp` vs the hand-derived cross-term + the 18-model regression set; **per-model** protocol encoded; **no bucket until all 3 land** | `$149` not surgical → bank all 3 (no `src/`); → P6/P7 |
| **P5** | camcge (#1330) / rocket (#1462) | **Epic-5-deferred / Sprint-36 hand-off** | camcge `/tmp` MS-1 @ 191.7346 (dual side) — **expected MS-4** → per-model-numéraire Epic-5 fallback; rocket clean-at-NLP (no solve gate) | camcge → Epic 5; rocket → Sprint 36; 0 bucket |

**Cross-cutting:** every gate cites `kkt_residual.py` (PR27); every emit-touching PR passes golden-staleness (PR26) + presolve-divergence + **`--resolve-changed --since-commit 78ceaead`** + determinism ×3. **`modelstat` asserted before every objective read; `x.up=inf` BANNED (mine); the objective-gradient sign flip BANNED (Case-c).** **Only P4 (and P3 if it lands leak-free) touch `src/`; P1/P2/P5 ship no `src/`.**

---

## 4. Known-Unknowns dispositions (gate-layer contributions)

Task 10 **contributes** to these unknowns via the gate design; the primary owner of each remains its per-track design task.

| Unknown | Gate | Contribution |
|---|---|---|
| **1.2** | mine H_dual → cold MS-1 | The gate is **pre-refuted** (P1) — no candidate reaches the cold-MS-1-@-17500 gate; the exit (Sprint-36 consultation) is taken. Primary: Task 6. |
| **2.2** | sarf O(active) / no timeout re-trigger | The **timing** gate is specified (O(active=398), the **measured > 303 s** baseline, partial-improvement-is-REPLAN); the DEFER exit is taken. Primary: Task 7. |
| **3.1** | fawley max `stat_bq` residual → 0 | The gate requires **→ 0** (not the 96% partial), scoped to `stat_bq`, `modelstat` asserted, no mbal/cohort leak; +Solve out of scope (H-b). Primary: Task 8. |
| **4.3** | `$149` product-rule correction | The P4 `$149` step is gated on a `/tmp` control vs Task 4's **hand-derived cross-term** + the 18-model regression set (`_diff_prod`, not `stationarity.py`); part of the per-root sequence. Primary: Task 4. |
| **5.1** | camcge dual-consistent Walras `/tmp`-to-MS-1 | The camcge gate is the Epic-5 `/tmp` MS-1 @ 191.7346 prototype (dual side) + the detector; **expected MS-4 → per-model-numéraire Epic-5 fallback**. Primary: Task 9. |

---

**Document Status:** ✅ Complete — Sprint 35 Prep Task 10
**Last Updated:** 2026-07-24
**Owner:** Sprint 35 Planning Team

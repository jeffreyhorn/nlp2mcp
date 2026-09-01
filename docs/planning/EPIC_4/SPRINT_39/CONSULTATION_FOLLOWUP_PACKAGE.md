# Consultation Reply-Integration & Follow-Up Package (P6)

**Sprint 39 Prep Task 9** · **Measured at:** `84656666`, GAMS **54.2.1** / PATH **5.2.01** · **Authored:** 2026-09-01
**Date gate:** **2026-09-09.** Cannot be pulled earlier.

> **⚠ Two findings that change how P6 should be executed.** The three banked figures all reproduce — but **they come from different emits**, and the package never said which, so a reply saying *"try X"* has no unambiguous file to try it on. And the license cohort is in far worse shape than the `ferts` caveat implies: **7 of its 11 members carry the Sprint-39 Task-7 defect shape, and 2 have live violations in their committed goldens today.**

---

## 1. Status: no reply (Unknown 6.1)

Checked **2026-09-01**. The last comment on each thread is my own send record of 2026-08-26.

| issue | state | last comment |
|---|---|---|
| **#1462** rocket | OPEN | 2026-08-26, `jeffreyhorn` — "Consultation SENT" |
| **#1443** mine / LP-degeneracy | OPEN | 2026-08-26, `jeffreyhorn` — "LP-degeneracy question POSED" |

**Six days elapsed of the fourteen** to the gate. Nothing to integrate yet, and nothing that requires a decision before 2026-09-09.

## 2. Re-measured figures (all three threads)

Every figure re-derived from a scratch directory at `84656666`. **All three banked figures reproduce.**

| thread | emit measured | solver status | model status | iterations | eval errors |
|---|---|---|---|---|---|
| **rocket** | **`_mcp_presolve`** | 1 Normal Completion | **5 Locally Infeasible** | **9,241** | 0 |
| rocket | `_mcp` (cold) | 1 Normal Completion | 5 Locally Infeasible | **16,024** | 0 |
| **agreste** | **`_mcp` (cold)** | 1 Normal Completion | **5 Locally Infeasible** | **9,734** | 0 |
| agreste | `_mcp_presolve` | 1 Normal Completion | 5 Locally Infeasible | 7,000 | 0 |
| **mine** | **`_mcp` (cold)** | 1 Normal Completion | **5 Locally Infeasible** | **10,662** | 0 |

**⚠ The banked figures come from different emits, and the sent package did not say so.** rocket's 9,241 is its **presolve** emit; agreste's 9,734 and mine's 10,662 are **cold**. rocket's cold emit runs to 16,024 iterations — a figure that appears nowhere and would look like a contradiction to anyone re-measuring. **Any reply must be applied to the emit its figure came from**, and §4 names that per thread.

**rocket's `stat_step` residual claim reproduces exactly** — three of PATH's four final norms:

| final norm | value | equation |
|---|---|---|
| Inf-Norm of Complementarity | 4.8575e-02 | **`stat_step`** |
| Inf-Norm of Normal Map | 6.1601e-02 | `stat_d(h37)` |
| Inf-Norm of Minimum Map | 4.8575e-02 | **`stat_step`** |
| Inf-Norm of Fischer Function | 9.3636e-02 | **`stat_step`** |

NLP references, unchanged: rocket **1.0128** (`likely_convex`), agreste **17706.43** (`verified_convex`), mine **17500.0** (`verified_convex`).

## 3. The follow-up comment — ready to post on 2026-09-09

**Post as a comment on #1462, and a one-line cross-reference on #1443.** Send the email to the same three recipients.

> **Follow-up — 2026-09-09**
>
> Following up on the consultation sent 2026-08-26 (rocket non-convergence, the LP-degeneracy question on `agreste`/`mine`, and the license-capacity ask). No reply has arrived; this is a courtesy bump, not a resubmission.
>
> Nothing has changed on our side. All three fingerprints were re-measured on 2026-09-01 against GAMS 54.2.1 / PATH 5.2.01 and reproduce exactly: rocket `MODEL STATUS 5` after 9,241 iterations with 0 evaluation errors and the residual concentrated on `stat_step` under three of PATH's four final norms; `agreste` `MODEL STATUS 5` after 9,734 iterations; `mine` after 10,662. Both `agreste` and `mine` are verified-convex LPs, which is what makes a *locally* infeasible termination worth asking about.
>
> If any of the three is better directed elsewhere, or if there is a preferred channel, please say so and I will re-route it. Otherwise I will assume the timing is simply inconvenient and check back later.
>
> Happy to supply the emitted `.gms`, the full `.lst`, or a reduced reproducer for any thread.

**⚠ Why this wording, checked against the failure mode.** The consultation slipped **five sprints**, and each slip came from **re-opening the send decision** — asking again whether to send, to whom, in what form. This draft:

- **states the send as a completed fact** and never asks whether it should have happened;
- **offers re-routing, not reconsideration** — "if better directed elsewhere" is a request for information, not a reopening;
- **carries no deadline or escalation**, so it cannot fail and trigger another decision;
- **ends by relieving the recipient of obligation**, which is what makes it postable without a follow-up decision behind it.

**Do not add**: a summary of the original question (it is one scroll up), a restatement of why it matters, or a proposal to change the recipient list. Each of those re-opens the decision.

## 4. Reply-integration checklist, per thread

### 4a. rocket → the `--force` scaffold

**Verified on current `main`:** `--force {none,homotopy,multistart,optfile}` is live at `src/cli.py:208`, dispatched at `:488`, emitted by `src/emit/forcing.py:41`.

| reply shape | where it lands |
|---|---|
| a concrete **`optfile`** / option set | `forcing.py:64–80`, the `optfile` branch. Today it hardcodes `proximal_perturbation 1e-2` + `merit_function normal` |
| a **regularization / continuation schedule** | `forcing.py:105` (`else:  # homotopy`), the schedule literal at `:121–122`. Today `mu` steps `1e3 → 1e2 → 1e1 → 1.0 → 1e-1 → 1e-2 → 0` over `m1*m7` |
| a **named reformulation class** | not a scaffold change — a new issue against `src/kkt/`, with rocket's Phase-0 gate |

**⚠ The scaffold takes a strategy, not option values.** There is no CLI path for "use *these* numbers": `emit_forcing_scaffold(strategy, model_name, add_comments)` takes no option payload, and the literals above are in the emitter. **Integrating a recommended option set is a source edit, not a flag** — small, but it is `src/` work with a quality gate, not a config change. Budget it as such.

**Apply it to `rocket_mcp_presolve.gms`** — that is the emit the 9,241-iteration figure came from.

### 4b. license grant → one `--only-solve` batch

See §5. **Do not run the batch blind** — the pre-flight there is now load-bearing.

### 4c. agreste / mine LP-degeneracy answer

`mine` has an owning issue (**#1443**). **`agreste` does not** — see §6. An actionable answer arriving for agreste needs an issue authored first, which is why §6 pre-drafts its gate.

### 4d. ⚠ A non-actionable reply

An **actionable** reply is a concrete option set / `optfile`, a regularization or continuation schedule, or a named reformulation class. A diagnosis without one of those three does not unblock rocket.

**The response to a non-actionable reply is to record it and close the thread's dependence on it** — *not* to iterate:

1. Post the reply verbatim on the owning issue, with a one-line note on which of the three actionable forms it lacks.
2. **Do not send a clarifying question.** That re-opens the decision this package exists to keep closed, and a clarification round has no date gate to bound it.
3. Mark the thread **answered but not actionable**, and let the priority close on that basis. A diagnosis that names the mechanism still has value banked against a future sprint even when it moves nothing now.
4. **rocket's +1 does not become "at risk"** — it was never a projection (§7).

## 5. The 11-model cohort re-test procedure

**Cohort confirmed at 11** (`outcome_category == "path_solve_license"`), unchanged: `egypt`, `ferts`, `glider`, `robot`, `shale`, `sroute`, `srpchase`, `tabora`, `tfordy`, `tricp`, `turkey`. All carry `solver_version: None` — rejected at *generation*, so **PATH never ran on any of them**. All 11 have a cold golden; **none has a presolve golden.**

### ⚠ `ferts` is not the exception — it is the pattern

The caveat as banked is that *"`ferts`'s emit was silently wrong until S38 D11, so 'a golden exists' has never meant 'the golden is correct'"*. Sprint-39 Task 7 lets that be made specific, and it is worse than the caveat implies:

| finding | cohort members |
|---|---|
| carry a **repeated-symbol declared domain** (the Task-7 defect class) | **7 of 11** — `egypt`, `ferts`, `shale`, `sroute`, `srpchase`, `tfordy`, `tricp` |
| carry a **live P2 violation in the committed golden today** | **2 of 11** — `egypt` (`1$(tranc(rp,rp))`), `shale` (`1$(ts(tf,tf))`) |
| **unknown** — the Task-7 census could not parse it inside 120 s | **1** — `turkey` |

Both live violations are the elec shape: a guard that is **identically false**, silently dropping a term. Neither has ever been executed by a solve.

### The procedure

```bash
# STAGE 0 — pre-flight, costs no license capacity. Run it FIRST.
#   P2 over the cohort's goldens: ~2 s, no GAMS.
OUT=/tmp/p6 .venv/bin/python docs/planning/EPIC_4/SPRINT_39/artifacts/property2.py
#   Expect egypt and shale to appear. A member that appears is NOT
#   disqualified — it is flagged, and its result must be read knowing the
#   emit carries a defect signature.

# STAGE 1 — the batch, one pass, no retries.
.venv/bin/python scripts/gamslib/run_full_test.py --only-solve \
  --models egypt,ferts,glider,robot,shale,sroute,srpchase,tabora,tfordy,tricp,turkey

# STAGE 2 — attribution on every member that reports a match.
.venv/bin/python scripts/sprint_audit/check_mcp_solve_attribution.py --models <matched ids>
```

**Stage 2 is not optional.** These are the first solves these emits have ever had, and `weapons` established that a golden can pass every static review and still not run. A first-ever match is exactly the case where a spurious one is most plausible.

**⚠ A per-model sanity check before spending capacity is warranted, and Stage 0 is its cheap form.** It costs seconds and no license, and it already knows two members are suspect. A full per-model review is not warranted — the batch is one pass, and a failure costs nothing that a projection depends on (§7).

## 6. `agreste` has no owning issue (Unknown 6.3)

**#1068 is CLOSED** (2026-03-13) and describes a **different defect**: *"MCP structurally infeasible — missing Jacobian terms and alias handling bug"*. Today's fingerprint is not structural infeasibility — it is a **verified-convex LP terminating `Locally Infeasible` after 9,734 iterations with 0 evaluation errors**, which is the structurally odd thing the consultation asks about. A search over all issues returns only #1443 and #1462 (both by cross-reference) and the closed #1068.

**So the assumption holds: agreste needs a new issue if an actionable reply arrives.**

**File it only if a reply arrives** (Q4). A pre-emptive issue whose Phase-0 gate depends on an unknown answer would be a gate asserting nothing — and Sprint 38 already showed that a doc written before its measurement rots.

**Its gate, pre-drafted so filing is fast:**

- **Fail-before:** `agreste_mcp.gms` → `SOLVER STATUS 1` / `MODEL STATUS 5` / **9,734** iterations / 0 evaluation errors (reproduced 2026-09-01 at `84656666`).
- **Pass-after:** `MODEL STATUS 1` or `2`, and the objective within tolerance of the NLP's **17706.43**. ⚠ *Assert `modelstat` before reading any objective.*
- **Negative control:** `mine` (**#1443**) must not drift — it is the same question, and a fix that moves both is a different, larger finding than a fix that moves one.
- **Leak gate:** `make check-goldens` clean; drift on `agreste` alone.

**⚠ Q5 — the same gap exists for `cesam`.** It has **six issues, all CLOSED** (#733, #807, #864, #874, #878, #881) and **none open** — every one an emit defect from Sprints 20–27, none about solver behaviour. `indus` (#1461 byte-reproducibility, #931 iswnm) and `dinam` (#926 compilation errors) have open issues that describe **different defects**, so neither would own an LP-degeneracy answer either. **`mine` and `rocket` are the only two banked threads with a genuine owner.**

## 7. Projection discipline

**Neither of these is a Sprint-39 projection, and neither may enter an acceptance criterion:**

- **rocket's +1** is contingent on a reply that may not arrive and, if it arrives, may not be actionable.
- **the cohort's +11** is a *ceiling*, contingent on a license grant that is a purchasing decision, not engineering — and §5 now shows the ceiling is optimistic on its own terms, since 2 of the 11 carry a live emit defect.

**Both are excluded from projections and neither is written off.** If either lands, it is reported as an **unprojected gain** with its contingency named — not as a plan met.

---

**Document Status:** ✅ Complete — Sprint 39 Prep Task 9. **Revisit before 2026-09-09**; §1 is the only section that can go stale.
**Last Updated:** 2026-09-01

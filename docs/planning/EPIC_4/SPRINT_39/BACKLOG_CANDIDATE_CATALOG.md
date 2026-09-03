# Emit-Backlog Candidate Catalog — refreshed (P10)

**Sprint 39 Prep Task 11** · **Measured at:** `00f7a105` · **2026-09-02**

> **⚠ Headline: the selection rule yields fewer qualifiers than P10 needs, and the ones that qualify are already owned by deep tracks.** But Sprint-39 prep has produced a *better* absorber than the backlog sweep — see §5.

---

## 1. The population, re-derived

**Non-solving** = a convex candidate whose `mcp_solve.status != "success"`. This is Task 2's definition and it reconciles exactly: **31**.

| outcome category | count |
|---|---|
| `path_solve_license` | 11 |
| `model_infeasible` | 7 |
| no `mcp_solve` record (translate failed) | 7 |
| `path_syntax_error` | 6 |
| **total** | **31** |

**Owning issues: 30 of 31.** `robot` has none — it is in the license-gated cohort (routed here by Task 2, and unchanged).

**⚠ Phase-0 gates: 8 of 31, up from Sprint 38's 0 of 5.** `sarf` (#1385), `camcge` (#1330), `fawley` (#1111), `lnts` (#1694), `mine` (#1224), `rocket` (#1462), `tricp` (#1062), `ganges` (#1667). **Four of those eight were authored during Sprint-39 prep**, which is the P7-gates-P8 sequencing from Sprint 38 paying off a sprint later.

## 2. The selection rule, applied

**A model enters the sweep only with a reproduced fingerprint *and* a named fix surface. Anything needing a new diagnosis is banked, not started.** Unchanged, because it worked.

| model | fingerprint reproduced? | fix surface named? | verdict |
|---|---|---|---|
| **lnts** | ✅ S39 Task 5 — MS-4 at iteration 0, all four criteria, runtime-confirmed | ✅ `emit_gams.py:3121` (Task 5 **refuted** the banked `:3060–61` surface and named the real one) | **qualifies — but owned by P3** |
| **mine** | ✅ S39 Task 9 — MS-5 after **10,662** iterations, 0 eval errors | ✅ #1443 — head-domain-offset equation mis-emits KKT beyond the `stat_x` cross-term | **qualifies** |
| **dyncge** | ✅ S39 Task 4 — `CASE_B`, max rel **6.22e-02** at `stat_pf(CAP,SRV)` | ✅ `stationarity.py` ~7107–7131, the #1081 dim-mismatch branch | qualifies, **but it SOLVES** — not in the 31, and owned by P2 |
| **sarf** | ✅ S39 Task 6 — does not terminate at a 900 s cap | ⚠ named but **refuted** — the four sites are 0.5 % of wall-clock | owned by P4; surface is the open question |
| **rocket** | ✅ S39 Task 9 — MS-5 after **9,241** iterations (presolve emit) | ❌ awaiting the consultation | **banked** |
| **agreste** | ✅ S39 Task 9 — MS-5 after **9,734** iterations, verified-convex LP | ❌ none; **and no open owning issue** (#1068 is closed, different defect) | **banked** |
| **cesam** | ❌ not reproduced | ❌ new diagnosis — same MS-4-at-0 *signature* as lnts but **0 `_fx_` equations**, so lnts's mechanism cannot apply | **banked** |
| `indus` | ❌ | ❌ 31 errors across 7 families — broad, not bounded | **banked** |
| `dinam` | ❌ (as a `path_syntax_error`) | ❌ 22 errors | **banked** — but see §3 |
| `turkpow` | ❌ | ❌ | **banked** — but see §3 |
| `clearlak` | ❌ | ❌ | **banked** |
| the 11 license-gated | ❌ **not reproducible** — PATH never ran; `solver_version: None` | — | **structurally excluded** |

**⚠ A shared signature is not a shared mechanism** — `cesam` is the standing example, and it is why it stays banked rather than being batched with lnts.

### ⚠ Two do-not-start markers

**`agreste` is posed to the PATH authors — check #1443 before any local work.** Its LP-degeneracy question rides the consultation sent 2026-08-26, and Task 9 re-measured its fingerprint (MS-5 after 9,734 iterations, verified-convex LP) for exactly that reply. Starting a local diagnosis before the **2026-09-09** gate risks duplicating whatever comes back. It also has **no open owning issue** — #1068 is closed and describes a *different* defect (structural infeasibility, not a converged-then-infeasible LP) — so an actionable reply needs an issue authored first; Task 9 §6 pre-drafts its gate for that.

**⚠ Do NOT re-open the ganges rebind site.** #1668's **direction 1 is a measured no-op** (265 fires, zero residual; `prolog` drifts −3 bytes in the full sweep) and **direction 2's information is absent** — ganges and `prolog` are *locally indistinguishable* there. Confirmed unchanged for this sprint: **`git log 9ab2c0c3..HEAD -- src/` returns zero commits**, so the site is byte-identical to its Sprint-38 state. See Unknown 10.2, now **closed as unreachable**.

## 3. Cross-check against Task 7's positional-domain survey

**Four of the 31 are instances of the positional-domain class**, by Task 7's P2 property over the committed goldens:

| model | emitted violation | backlog status |
|---|---|---|
| `dinam` | `1$(ts2(te,te))` | `path_syntax_error` |
| `egypt` | `1$(tranc(rp,rp))` | `path_solve_license` |
| `shale` | `1$(ts(tf,tf))` | `path_solve_license` |
| `turkpow` | `1$(vs(v,v))`, `1$(vs(t__kkt1,t__kkt1))` | `path_syntax_error` |

**This does not move any of them into the shortlist, and the reason matters.** Task 7 gives each a *named fix surface* — the repeated-index guard — but the defect it names is **not the one blocking the model**. `dinam` and `turkpow` fail to compile; `egypt` and `shale` never reach PATH. Fixing the P2 violation leaves all four exactly where they are.

**What it does establish** is that these are **second, latent defects in models we already cannot solve** — so when their primary blocker is cleared, they will not be correct. That is worth knowing before a licence grant is spent (see the Task 9 package §5, which now gates the cohort batch on exactly this).

## 4. ⚠ 10.1's assumption is at risk

The rule yields **two** strict qualifiers, `lnts` and `mine` — but:

- **`lnts` is P3's deep track**, not P10 filler. Counting it toward P10 would be double-booking the same work.
- **`mine` is the only unclaimed qualifier**, and #1443 is simultaneously one of the two consultation threads. Starting local work on it before the 2026-09-09 gate risks duplicating whatever a reply proposes.

**So P10's independent pool is effectively one model, and that one is date-entangled.** The deliverable "≥2 backlog models recovered or re-triaged" is **not supportable from the backlog as it stands**.

## 5. What absorbs P10's 12–16 h instead

**Land Task 7's P2 property as a gate, and work its six flagged models.** This is a better fit for P10 than the backlog sweep, on P10's own criteria:

| P10 requirement | how this meets it |
|---|---|
| reproduced fingerprint | **the violations are in committed goldens today** — 9 across 6 models, reproducible in under 3 s with no GAMS |
| named fix surface | Task 7 §2's catalog: 21 sites, 4 `NEEDS A GUARD`, ranked by measured blast radius |
| bounded, not open-ended | a fixed list of 6 models and 4 sites, not a diagnosis |
| 0-bucket by design | **3 of the 6 are already `mcp_solve: failure`**, `nonsharp` is convexity-`excluded`, `gussrisk`'s instance is latent |
| slack-absorbing | decomposes to one model per unit; stops cleanly at any point |

**And it has a fail-before that the backlog sweep does not**: land the property first, watch it fail on the six, fix, watch it pass. Task 7's §6 recommends exactly this ordering.

**⚠ Two of the six are `egypt` and `shale` — both license-gated.** Their fix is verifiable by the property and by golden re-emission, but **not** by a solve. That is a real limit and it is why this is 0-bucket work, not a Solve-mover.

---

**Document Status:** ✅ Complete — Sprint 39 Prep Task 11
**Last Updated:** 2026-09-02

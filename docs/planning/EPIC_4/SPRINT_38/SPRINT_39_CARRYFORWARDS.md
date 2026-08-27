# Sprint 39 — Carryforwards from Sprint 38

**From:** Sprint 38 close, `8e32be09`, 2026-08-26 · **Toolchain:** GAMS **54.2.1** / PATH **5.2.01**
**Baseline for Sprint 39:** Solve **111** · Match **96** (65 cold + 31 presolve) · Translate **135** · mi **7** · pse **6** · `path_solve_terminated` **0** · `path_solve_license` **11** · all-219 **99** · genuine floor **73** *(pending the §1 decision)*

> Every figure here is derived at `8e32be09`. **Anything quoted in a Sprint-39 doc must carry its commit** — Sprint 38 shipped a five-times-carried consultation package whose own failure description had gone stale (§7), and Sprint 37 closed with a refuted figure in its log.

---

## 1. ⚠ OWNER DECISION REQUIRED — is the genuine floor 73 or 75?

**The tracker reports 73** (baseline 73 + 0 entries) and that is the number of record. **The written definition appears to owe two entries.**

`twocge` (D9) and `elec` (D12) both had their **cold emit changed** by a real fix, both now match, both are inside the 142. The definition classifies *methodology* as "cold emit **byte-identical** to pre-fix" — neither is. Both were **aborting before the fix**, so each match is attributable to the emit change rather than to a solver effect, and the precedent model named in the definition (`polygon`) has the identical DB shape today.

**Day 9 applied the wrong test** — "matched via the presolve retry ⇒ methodology" — when the definition turns on whether the *cold emit* changed. Day 12 inherited that reasoning.

**Recommendation: add both entries → floor 75.** Deliberately not applied at close: the plan pre-registered flat-73, and a +2 discovered by the closer in the direction the closer would prefer needs an owner's eye. **Sprint 39 cannot report a floor movement until this is settled**, because its own baseline depends on it.

**Bounded next step:** owner confirms or rejects; if confirmed, append two entries to `data/floor_provenance.json` with `limb: presolve-match-genuine` and re-run `floor_tracker.py`.

## 2. dyncge — a second, independent emit defect (NEW, needs its own issue)

Fixing #1693's empty-pair abort revealed a defect it had been **masking**.

| | |
|---|---|
| Harness | `kkt_residual.py data/gamslib/raw/dyncge.gms` → **`CASE_B — emit_bug`** |
| Max relative residual | **6.22e-02** at `stat_pf(CAP,SRV)` (tol 1e-3) |
| Top rows | `stat_pf(CAP,SRV)` · `stat_pq(HMN)` · `stat_pf(LAB,SRV)` · `stat_pf(LAB,HMN)` · `stat_pf(CAP,LMN)` |
| Consequence | cold MCP solves `MODEL STATUS 1 Optimal` @ **381401.119** vs NLP **539570.5027** — **29.3 % mismatch** |
| Presolve retry | also fails to match (`0/1`) — so there is **no spurious match** to adjudicate |

**Solve +1 is genuine and banked; Match is 0 and is not claimed.** The residual points at the `pf`/`pq` block, **not** at `eqpf2` — this is a new diagnosis, **not** a widening of #1693.

**Bounded next step:** file an issue with a Phase-0 gate; the fingerprint above is reproducible today and needs no archaeology.

## 3. lnts — never reached (Day 12 budget)

Day 12's budget went to elec and dyncge. lnts was not started.

**Stated hypothesis, untraced:** two `.fx` mechanisms act on the same cells — the correct one emits `y_fx_y2_h50.. y("y2","h50") - 5 =E= 0`, while a blanket pruned-instance zeroing fires on exactly those cells, giving `y.lo = y.up = 0` against equations demanding **5** and **45** ⇒ **MS-4 at iteration 0**. Fix surface named as the `fix_rhs = "0"` fallback in `emit_gams.py`.

**⚠ Treat the fix surface as a hypothesis, and re-trace it from `stationarity.py` / the AD entry points outward.** Three of Sprint 38's four P8 gates were wrong about the *layer* (§7). Confirm with a **runtime bound probe**, not a source read.

## 4. P2 sarf — emit-preserving, KPI undelivered

The referenced-instance filter is **in `main` and emit-preserving** (leak gate clean over 163 at the time). But sarf still does not complete: **killed at 28 m 40 s against a ≤300 s gate**, so **+1 Translate is not delivered**.

**Bounded next step:** the remaining cost is at **four call sites the Day-7 change deliberately did not touch** — located, not suspected. The generalisable lesson from Day 7 is recorded: *narrowing a loop's body does not help if the narrowing itself is O(the thing you removed).*

## 5. P1 ganges — REPLAN'd, and closed as unreachable at the rebind site

**Do not re-open at the `$149` rebind site.** Both directions of #1668 are closed on measurement, not on opinion:

- **Direction 1 is a no-op** — 265 fires across 3 models, **zero residual**. The issue's premise ("rewrites the variable but not the parameter") is false; both go through the same substitution.
- **Direction 2 is not expressible** — ganges and `prolog` are *locally indistinguishable* at the site.

The asymmetry is manufactured **downstream**, in the positional re-symbolization against the declared domain. **Unknown 1.5 carries** (does a general `$149` fix unblock dinam/indus/turkpow/clearlak) — it was never measurable this sprint, because measuring an unpatched tree restates the failure rather than answering the question.

## 6. ⏰ Consultation follow-up — due 2026-09-09

Sent 2026-08-26 to `ferris@cs.wisc.edu`, `steve@gams.com`, `sdirkse@gams.com`. Tracked on **#1462** (rocket + send record) and **#1443** (the mine/agreste question). Three threads carried: rocket, the **11-model license-capacity ask**, and **agreste + mine reframed as one question**.

**If no reply by 2026-09-09:** post a follow-up comment and treat rocket's +1 Solve as consultation-gated for planning — **without re-opening the send decision.** Re-opening it is what produced five carries.

**An actionable reply is:** a concrete option set / `optfile`, a regularization or continuation schedule, or a named reformulation class. A diagnosis without one of those three does not unblock rocket.

## 7. Standing process findings — carry these into Sprint 39's prep

1. **Three of the four P8 gates were wrong about the LAYER** — tricp (D11), elec (D12), dyncge (D12): **two consecutive days**. tricp and elec under-scoped, naming `emit_gams.py` for defects decided upstream in AD/KKT (elec's one gate covered two separate defects in two files). dyncge **over**-scoped — demanding "new logic" for a diagonal-triviality test that had existed since #942 and was merely applied to the wrong population. **`twocge` (D9) traced correctly**, so this is a strong tendency, not a universal law. **Corollary worth acting on: before writing new emit logic, check whether the logic already exists for a different population.**
2. **A repeated symbol in a DECLARATION domain is safe until something resolves an index "positionally against the declared domain."** Bit twice in two days — `slp(n,n)` as a variable domain (tricp), `Set ut(i,i)` as a set domain (elec). **Audit the remaining positional-vs-declared-domain resolutions in `stationarity.py`.**
3. **Re-measure at the moment of USE, not only at authoring.** The consultation package's failure description had gone stale over five carries; prep re-verified the conclusion and stamped the toolchain, but not the description.
4. **An internal planning doc is not an external deliverable.** Sending one requires a separate extract, not a trim — sprint numbering, deferral history, and internal classifier labels (`emit_bug`) all mislead an outside reader.
5. **`weapons` remains a spurious presolve match.** Match 96 is overstated by 1. Reported, not corrected — a systemic remedy covers it and the 13 dangling `mcp_file_used` rows together, or neither.
6. **The presolve-golden adoption rule, post-`weapons`:** adopt only if `check_mcp_solve_attribution.py` reports `MCP-SOLVED`, **and** `check_presolve_divergence.py --model X` passes, **and** the DB's `mcp_file_used` actually references it. Day 12 adopted `elec`'s on that basis and declined `dyncge`'s.

## 8. Banked, not started — rejected candidates stay rejected

- **agreste** — the highest-value bank. An **LP**, `verified_convex`, NLP MS-1 @ 17706.43, whose MCP PATH declares **MS-5 Locally Infeasible after 9,734 iterations**. A *locally* infeasible pure LCP is structurally odd. **Now also posed to the PATH authors** (§6), so a reply may arrive before any local work starts.
- **cesam** — new diagnosis required. MS-4 at 0 iterations, the same signature as lnts, but **checked not assumed**: it has **0 `_fx_` equations**, so lnts's mechanism cannot apply.
- **indus** (31 errors spanning 7 families), **dinam** (22), **turkpow**, **clearlak** — broad, not bounded, or structurally excluded.
- **camcge** — Epic-5 scoped. MS-4 against a *correct* NLP optimum is structural rank-deficiency, not an emit defect. **The drop-row variant stays BANNED**: it is *primal-correct* and breaks the MCP dual silently.

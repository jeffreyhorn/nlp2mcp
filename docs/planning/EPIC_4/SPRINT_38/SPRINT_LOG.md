# Sprint 38 — Sprint Log

**Weeks 41–42 · Days 0–13 · Closed 2026-08-26**
**Anchor:** `8cffec29` (S37 close) · **S38 close:** `8e32be09` · **Solver:** GAMS **54.2.1** / PATH **5.2.01**

---

## 1. Headline

All figures derived at execution time (`scripts/sprint_audit/kpi_block.py`); the S37 column is derived from the DB **as committed at `8cffec29`**, not quoted from the S37 log.

| KPI | S37 close | S38 close | Δ |
|---|---|---|---|
| Parse (219) | 142 | **142** | — |
| Translate | 135 | **135** | — |
| **Solve** (142 candidates) | 108 | **111** | **+3** |
| **Match** | 94 | **96** | **+2** |
| &nbsp;&nbsp;cold-optimal match | 65 | **65** | — |
| &nbsp;&nbsp;presolve match | 29 | **31** | **+2** |
| **genuine floor** (provenance file) | 73 | **73** | — *(⚠ see §6 — arguably 75)* |
| model_infeasible | 7 | **7** | — |
| `path_syntax_error` | 6 | **6** | — |
| **`path_solve_terminated`** | **4** | **0** | **−4 — category emptied** |
| `path_solve_license` | 10 | **11** | +1 |
| all-219 Match | 97 | **99** | +2 |

**The sprint's result is that an entire failure category was cleared.** `path_solve_terminated` held four models at S37 close; it holds none now — and they went to **four different destinations**, which is the part a single delta hides:

| model | day | from | to | Match |
|---|---|---|---|---|
| **twocge** (#1331) | 9 | `path_solve_terminated` | `model_optimal_presolve` | **match** |
| **tricp** (#1062) | 11 | `path_solve_terminated` | `path_solve_license` | not tested |
| **elec** (#983/#1325) | 12 | `path_solve_terminated` | `model_optimal_presolve` | **match** |
| **dyncge** (#1693) | 12 | `path_solve_terminated` | `model_optimal` | **mismatch** |

Only two of the four produced a Match. **tricp's fix is complete and verified but its MCP then exceeded the demo license** (387 → 1,255 rows), so it moved sideways into the license-gated cohort. **dyncge's fix is also complete, and it exposed a second, independent defect underneath** — the abort had been masking it (§7).

**⚠ `model_infeasible` did not rise to 9, and `path_syntax_error` did not fall to 4.** Close rule #2 pre-registered that lateral move as the shape of P1 working. **P1 was REPLAN'd on Day 1**, so the cascade never ran and both figures are unchanged at 7 and 6. Reporting the rule as unmet rather than silently dropping it: the rule was correct, its precondition did not occur.

**DB byte-status:** the DB **changed**, on Days 9, 11 and 12 — four model rows in total, each a bucket move persisted by the pipeline runner rather than by hand.

## 2. Close gates

| gate | result |
|---|---|
| Full pipeline retest, **≥3 `PYTHONHASHSEED`** (0 / 1 / 42) | ✅ **PASS ×3** — all 186 in-scope goldens byte-identical under every seed (§3) |
| Genuine floor from the **provenance file**, never by hand | ✅ tracker reports **73** = baseline 73 + 0 entries |
| Every figure derived at execution time | ✅ — the S37 comparison column is re-derived from the DB at `8cffec29` |
| Three-gate firm-landing rule applied per landing | ✅ §5 |

## 3. Determinism retest — ✅ PASS ×3

Full-corpus emit regeneration and byte-comparison against every committed golden, under three `PYTHONHASHSEED` values:

```
=== PYTHONHASHSEED=0 ===
Golden staleness: checked 186 in-scope golden(s) (7 allowlisted, 3 workers).
  All in-scope goldens clean.
=== PYTHONHASHSEED=1 ===
Golden staleness: checked 186 in-scope golden(s) (7 allowlisted, 3 workers).
  All in-scope goldens clean.
=== PYTHONHASHSEED=42 ===
Golden staleness: checked 186 in-scope golden(s) (7 allowlisted, 3 workers).
  All in-scope goldens clean.
```

**Every emit is byte-identical to its committed golden under all three seeds.** Scope is **186**, up from 163 at sprint start — Day 8 adopted 22 Tier-1 presolve goldens and Day 12 added `elec`'s. **The gate covers 23 more models than it did at S37 close**, which is the more meaningful number than the pass itself.

## 4. Day-by-day

| day | work | outcome |
|---|---|---|
| 0 | Baseline re-confirm, GO/NO-GO, P3 staged | **CONDITIONAL GO** — condition (d) failed ⇒ scoped as a NO-GO for **P1 as a landing track**, not for the sprint |
| 1 | P1 ganges direction-C control | **REPLAN** — #1668 direction 1 is a **no-op** (265 fires, zero residual); direction 2's information is absent at the site |
| 2–3 | P7 Phase-0 backfill | **CLOSED** — census 24 → 30; four gates authored; 2 issues filed |
| 4 | P6a KPI helper + P6b gate-scope assertions | both narrowing modes reproduced live and fixed |
| 5 | Checkpoint 1 | **GO** (with `--allow-empty`; the re-anchor had not yet landed) |
| 6 | P2 counter-only probe | **PROCEED** — 369,024 → 24/136 per row |
| 7 | P2 referenced-instance filter + P6c floor tracker | 🔶 **emit-preserving but the KPI is NOT delivered** — sarf killed at 28 m 40 s against a ≤300 s gate |
| 8 | Presolve-golden adoption | 22 Tier-1 goldens adopted; scope 163 → 185 |
| 9 | P4 close, P6d re-anchor, **P8 twocge** | **first bucket move** — Solve +1, Match +1 |
| 10 | Checkpoint 2 + the spurious-match investigation | **GO 22/22**; **exactly 1 of 33 presolve matches is spurious (`weapons`)** |
| 11 | P5 close + **P8 tricp** | tricp fixed (0 bucket); **Unknown 5.1 closed as procurement** |
| 12 | **P8 elec + dyncge** | Solve +2, Match +1; `path_solve_terminated` → 0 |
| 12* | **P3 consultation SENT** | after five carries; both human actions complete |
| 13 | Final retest + closeout | this document |

## 5. Firm landings — the three-gate rule applied

Close rule #1: a track is a **firm landing** only with (a) a per-model Phase-0 gate pass, (b) an **unqualified** full-corpus leak-gate pass, and (c) the change in `main`.

| track | (a) gate | (b) leak gate | (c) in main | verdict |
|---|---|---|---|---|
| **twocge #1331** (D9) | ✅ | ✅ PASS, exactly twocge | ✅ | **FIRM** |
| **tricp #1062** (D11) | ✅ | ✅ PASS at 185, exactly tricp + ferts | ✅ | **FIRM** |
| **elec #983/#1325** (D12) | ✅ | ✅ PASS at 185, exactly elec | ✅ | **FIRM** |
| **dyncge #1693** (D12) | ✅ | ✅ PASS at 186, exactly dyncge | ✅ | **FIRM** |
| **P2 sarf** (D7) | ❌ **gate NOT MET** (28 m 40 s vs ≤300 s) | ✅ clean over 163 | ✅ | **CARRYFORWARD** — the change is emit-preserving and in `main`, but its KPI is undelivered. Bounded next step: the four untouched call sites, located not suspected. |
| **P1 ganges** (D1) | — | — | — | **REPLAN** — no landing attempted |

**Four firm landings, one carryforward with a bounded next step, one REPLAN.** Both drifting models on Day 11 (`tricp` + `ferts`) were **declared before the gate ran**, not read off it afterwards.

## 6. ⚠ The floor: the tracker says 73, and the written definition argues 75

**Reported figure: 73**, from `data/floor_provenance.json` (baseline 73 + 0 entries), per close rule #3. **This is the number of record.**

**But the operational definition appears to owe two entries, and this needs an owner decision.** The definition is:

> *methodology* = cold emit **byte-identical to pre-fix**, matches only via warm-start; *genuine* = a real emit fix **changed the cold emit** — a model that matches only via the presolve warm-start is **still genuine** if the fix changed its cold emit (the polygon/ps2 precedent).

Against that test:

| model | cold emit changed? | matches? | in 142? | verdict under the definition |
|---|---|---|---|---|
| **twocge** | ✅ `twocge_mcp.gms` gained 2 `.fx` guard lines (D9, `204f35ac`) | ✅ | ✅ | **genuine** |
| **elec** | ✅ `elec_mcp.gms` drifted −12 bytes (D12, leak gate) | ✅ | ✅ | **genuine** |

Both were **aborting before the fix** — no solve at all — so each match is unambiguously attributable to the emit change, not to a solver effect. The precedent model named in the definition (`polygon`) carries the identical DB shape today: `likely_convex` + `model_optimal_presolve` + `match`.

**Day 9 recorded twocge as methodology using the wrong test** — "it matched via the presolve retry" — but the definition turns on whether the *cold emit* changed, not on how the match was obtained. Day 12 inherited that reasoning for elec.

**Why this is flagged rather than applied.** The plan pre-registered the floor flat at 73 in every acceptance column, and the S36 retrospective records that pressure to produce a floor gain caused a reverted landing. A +2 discovered by the closer, at close, in the direction the closer would prefer, is exactly the shape that deserves an owner's eye rather than a self-approved edit. **Recommendation: add both entries, taking the floor to 75.** The evidence is in §5 (both are firm landings) and above.

## 7. Findings the KPIs do not carry

- **`weapons` is a spurious presolve match** (Day 10) — its MCP aborted and the objective read back the embedded NLP's own answer. **Match 96 is therefore overstated by 1.** Reported, not corrected: 1 of 33 checked, cold matches unaffected, floor unaffected either way.
- **dyncge has a second, independent emit defect** that the empty-pair abort was masking. `kkt_residual.py` → **`CASE_B — emit_bug`**, max relative **6.22e-02**. It now solves to `MODEL STATUS 1 Optimal` at **381401.119** against the NLP's **539570.5027** — a 29.3 % mismatch. **Solve +1 is genuine; Match is 0 and is not claimed.**
- **Three of the four P8 gates were wrong about the *layer*** — tricp (D11), elec (D12), dyncge (D12), i.e. **two consecutive days**, not three. tricp and elec under-scoped, naming the emitter for defects decided upstream in AD/KKT (elec's single gate covered two separate defects in two files); dyncge **over**-scoped, demanding "new logic" for a diagonal-triviality test that had existed since #942 and was merely applied to the wrong population. **The fourth gate, `twocge` (D9), was accurate** — it named `emit_gams.py` §3 and the fix landed there.
- **A five-times-carried package rots in place.** At send time, `CONSULTATION_DECISION_BRIEF.md` §5's failure description (`EXIT — other error`) **no longer reproduced**; rocket now completes normally to MS-5 after 9,241 iterations. Prep had re-verified the *conclusion* and stamped the toolchain, but not the *description*.

## 8. Carryforwards → Sprint 39

See `SPRINT_39_CARRYFORWARDS.md`.

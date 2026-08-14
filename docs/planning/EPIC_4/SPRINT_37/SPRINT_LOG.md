# Sprint 37 — Sprint Log

**Weeks 39–40 · Days 0–13 · Closed 2026-08-13**
**Anchor:** `78ceaead` (S34 close) · **S36 close:** `935d94b7` · **Solver:** GAMS **54.2.1** (re-pinned Day 9)

---

## 1. Headline

| KPI | S36 close | S37 close | Δ |
|---|---|---|---|
| Parse (219) | 142 | **142** | — |
| Translate | 135 | **135** | — |
| **Solve** (142 candidates) | 108 | **108** | — |
| **Match** | 93 | **94** | **+1** |
|   cold-optimal match | 63 | **65** | **+2** |
|   presolve match | 30 | **29** | **−1** |
| **genuine floor** | 75 | **76** | **+1** |
| model_infeasible | 7 | **7** | — |
| `path_syntax_error` | 7 | **6** | −1 |
| `path_solve_license` | 9 | **10** | +1 |
| all-219 Match | 96 | **97** | +1 |

**The genuine floor advanced for the first time since Sprint 33.** Three consecutive sprints (34, 35, 36) closed modal-flat at 75; markov's `σ=sp` discriminator moved it to **76**.

**The +1 Match and the +1 floor are different models and different causes** — a distinction the row would otherwise blur:

- **floor +1 = markov** (P1), a real emit fix. Its cold emit changed, the cold MCP now solves, and the DB row moved `model_optimal_presolve` → `model_optimal` with the match retained. Methodology → genuine.
- **Match +1 = hhfair**, a **v54 solver effect** with byte-identical emit. It is a *methodology* match (+1 Match, **+0 floor**), and it was neither planned nor worked on.

**The partition moved by three models, not one** — worth spelling out, because `+2 cold / −1 presolve` nets to `+1 Match` and hides two of them:

| model | move | cold | presolve | floor |
|---|---|---|---|---|
| **markov** (P1, Day 3) | `presolve+match` → `optimal+match` | +1 | −1 | **+1** (methodology → genuine) |
| **robert** (Day 9) | `presolve+match` → `optimal+match` | +1 | −1 | **+0** — a **stale-row correction**, not a gain: robert has counted toward the floor since **S30** under the "a fix changed the cold emit" limb, and the DB was merely five sprints behind. Counting it again would double-count. |
| **hhfair** (Day 9) | `optimal+mismatch` → `presolve+match` | — | +1 | **+0** (v54 effect, methodology) |

Only markov is a Sprint-37 *achievement*; the other two are the DB catching up to reality and a free solver upgrade.

**DB byte-status:** the DB **changed**, and this is the first sprint since S33 where it did. Two persisting writes: Day 3 (markov's row, the floor advance) and Day 9 (the v54 re-baseline + provenance). Saying "flat" of this sprint would be wrong; every prior sprint's byte-unchanged DB is what made *their* flatness a measurement.

## 2. Close gates

| gate | result |
|---|---|
| Determinism ×3 `PYTHONHASHSEED {0,1,42}` | ✅ markov, fawley, chenery, robert, hhfair — byte-identical ×3, **and every one equal to its committed golden** (zero emit drift) |
| `--resolve-changed --since-commit 78ceaead` | ✅ **GO** |
| `make check-goldens` (163 in-scope) | ✅ **all clean**, 0 timeouts |
| PR25 floor recompute | ✅ **76** — resolved, not contingent |

markov md5 `c0115f45944aad0fb33310235a0780da` · fawley `5244fe1cb23f5251e3b37cc3e8792371`.

## 3. Day-by-day

| day | track | outcome |
|---|---|---|
| **0** | kickoff | ✅ GO. Baseline recomputed exactly; all four banked fingerprints reproduced live. **The P3 consultation send was not done and could not be** — the bundle names no recipient. Owner-assigned. |
| **1** | P1 markov control | ✅ PROCEED. `/tmp`-only; the patch was reverted. The gate that killed this in S36 — the full-corpus leak gate — passed **unqualified** over 163 goldens, and the 4 previously-unverified timeouts went to **0**, including `ferts` (an S36 leak). |
| **2** | P1 markov landing | ✅ **LANDED** (+259 in `stationarity.py`). Emit byte-identical to Day 1's control. `--resolve-changed` independently confirmed the methodology→genuine shift. |
| **3** | P1 markov fixtures | ✅ Floor **76** confirmed by PR25 recompute. First persisting DB write since the anchor. An integration test **red since March** went green; `nightly.yml` gained a step that actually reaches it. |
| **4** | P2 ganges | 🔶 **REPLAN**. All four cascade fixes work — `rc=2` → `rc=0` on both models, zero `$NNN`. The leak gate refused it: `$149` drifts `prolog` (a live match) and **cannot be dropped**. Filed **#1668**, `ISSUE_1667`. |
| **5** | Checkpoint 1 + `$66` | ✅ GO. `$66` turns out to be **Issue #1289**, open since Sprint 25 with **no Phase-0 section** — never implementable under CONTRIBUTING, cascade or not. P2 → STOP. OBJ-GAP set corrected 5 → **8**. |
| **6** | P4 fawley (pulled fwd) | ✅ **LANDED** (+54). `make leak-check MODEL=fawley` → unqualified **PASS**, clearing a gate blocked since S35. **0 bucket by construction.** |
| **7** | P5 sarf (pulled fwd) | 🔶 **DEFER**, on measured grounds. Profiling showed per-column differentiation dominates; the cheap memoization was implemented, measured at **~5%** against **~66×** needed, and reverted. `ISSUE_1385` Phase-0 authored. |
| **8** | prompt staleness sweep | 6 corrections to Days 8–13; Days 0–7 byte-identical. |
| **9** | P7 infra + P6 v54 re-baseline | ✅ **RE-PIN to GAMS 54.2.1**, zero Regressions. Three movers classified three ways (2 stale-entry corrections, 1 v54 effect). Phase-0 CI gate + `--min-scope` landed. |
| **10** | Checkpoint 2 + P3 camcge | ✅ GO ×3. **`solver_version` was a broken *read*** — the regex had never matched, which is why two sprints of "populate it" instructions failed. New per-row `mcp_solve.gams_version` on 135 rows. camcge reproduced every predicted figure → **Epic 5**. |
| **11–12** | — | free (P5 deferred Day 7) |
| **13** | closeout | this document |

## 4. Firm landings — the three-gate rule applied

A track is a **firm landing** only if it passed all three gates: Phase-0 doc → fixture → leak gate.

| track | Phase-0 | fixture | leak gate | verdict |
|---|---|---|---|---|
| **P1 markov** `σ=sp` discriminator | `ISSUE_1110` ✅ | ✅ 3 corpus-free | ✅ PASS ×163 | **FIRM — the +1 floor** |
| **P4 fawley** constraint-index-diagonal | `ISSUE_1111` ✅ | ✅ 3 incl. negative control | ✅ PASS | **FIRM — 0 bucket** |
| **P7** infra (4 gates) | n/a | ✅ | n/a | **FIRM** |
| **P2 ganges** cascade | `ISSUE_1667` ✅ | — | ❌ **blocked by #1668** | **CARRYFORWARD** |

The rule was pre-registered against fawley as the expected mislabelling; fawley passed on Day 6 and the rule bound the **ganges** cascade instead. It is verified-working code that cannot land — the distinction the rule exists to preserve.

## 5. `src/` — 2 landings, 1 file, +311

Both in `src/kkt/stationarity.py`. Nothing else in `src/` was touched all sprint.

- **markov** — a gated additive early-out (`_try_build_sigma_sp_crossterm` + three helpers) for the off-diagonal `σ=sp` case where the multiplier index is an independent variable index. Refuses to fire on conditioned constraints; rejects candidates whose index elements are not pairwise distinct.
- **fawley** — a binding in the "truly disjoint by NAME" branch requiring a subset-parent relation **and** that the coefficient *references the parent*. Two prior attempts failed because they only ever **subtracted**; this one added a **positive** requirement.

`_compute_index_offset_key` — the shared cohort-leak surface — was deliberately left untouched.

## 6. Infrastructure (P7) — four gates that did not exist at sprint start

| gate | before | after |
|---|---|---|
| golden-staleness | path-filtered, **could not be a required check** | required; runs on every PR and decides internally; `--min-scope 170` asserted on **discovery** |
| Phase-0 doc | convention in CONTRIBUTING, **1 of 3 recent emit PRs complied** | CI gate, calibrated to fail #1620/#1596 and pass #1647/#1665/#1671 |
| leak-gate reliability | 6 workers → **4/2/0 timeouts** across runs, load-dependent | default 3 workers, 0 timeouts |
| per-row solver provenance | `solver_version` null on all 219 rows | `solver_version` **fixed** (broken regex) + new `mcp_solve.gams_version` on 135 rows |

A path-filtered required check blocks a PR forever at *"Expected — waiting for status to be reported"*. That correction was applied twice: to golden-staleness, then to the new Phase-0 gate.

## 7. Carryforwards → Sprint 38

**Full detail: [`SPRINT_38_CARRYFORWARDS.md`](SPRINT_38_CARRYFORWARDS.md)** — the file Sprint 38's prep picks up, matching the S33→S37 convention. Summary below; each carries the **bounded next step**, not the track name.

- **P2 ganges** — the cascade is verified working (`rc=0`, both models). **Next step:** re-scope `$149`'s rebind so it cannot fire on `prolog` — the over-fire is in the *rebind predicate*, not the fix; `$149` is load-bearing and cannot be dropped. **#1668** + `ISSUE_1667`; `$66`/`ISSUE_1289` needs a Phase-0 section before it is implementable at all. **0 bucket** — the prep-era "+2 or 0" was refuted on Days 4–5: the 6th blocker (embedded `ganges0` MS-5 vs standalone MS-2 @ 6395.5444) is untouched and `mcp_model` stays MS-4, so a fully clean cascade buys only the lateral `path_syntax_error → model_infeasible` (pse 6 → 4, mi 7 → 9). A genuine +2 additionally needs the #1378/#1424 embedded-divergence class, which is not scoped.
- **P5 sarf** — **next step:** the O(active) atomic re-arch at all three sites (20–28 h). Measured: constant-factor fixes are dead (~5% vs ~66× needed). `ISSUE_1385`. **+1 Translate.**
- **P3 rocket/mine** — the consultation bundle is finalized and **UNSENT**. **Next step:** a human names a recipient and channel. Not executable by the execution agent, and it has now carried across three sprints on that basis.
- **camcge** — Epic 5, per-model numéraire. The three-part Walras redefinition has been refuted across 3+ sprints; **drop-row remains BANNED**.
- **turkey** — +1 Solve/Match, license-gated (3,866-row MCP vs the 1000-row demo limit). Needs a licensed testbed.
- **The 36 presolve goldens** — arguably the fix for the 153-cold/17-presolve coverage asymmetry, but adopting them must be a **deliberate, reviewed** change. Generating references and committing them in one unreviewed step is how a gate stops being a gate.

---

**Document Status:** ✅ Complete — Sprint 37 close (floor **75 → 76**, the first advance since S33).
**Last Updated:** 2026-08-13 · **Owner:** Sprint 37 execution team

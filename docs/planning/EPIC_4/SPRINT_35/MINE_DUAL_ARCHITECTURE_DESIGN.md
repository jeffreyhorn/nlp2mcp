# Sprint 35 — mine #1443 Head-Offset Dual-Architecture Design (Priority 1)

**Prep Task:** 6 (Critical, near-critical path) · **Date:** 2026-07-24 · **Owner:** Sprint 35 prep (KKT/emit specialist)
**Day-0 code anchor:** `78ceaead` (S34 close) · **Measurement tree:** `edc9f70e` (`main` at the S35 prep Task-5 merge) — docs-only ahead of the anchor, `src/`/`scripts/` byte-identical
**Scope:** docs/design only — re-confirms the Day-0 fingerprint (live), formalizes the degeneracy, scores four candidate dual architectures on reachability, and returns a **REPLAN recommendation**. **No `src/` change.**

> **Disposition: REPLAN before Day 1.** No emit-side dual architecture can supply the +16000 the `x.m = 0`-degenerate boundary requires. mine is a **primal-degenerate LP whose warm KKT point is not MCP-reconcilable by any emit reformulation**; it hands to the **Sprint-36 PATH-author consultation** as the canonical instance of that class. The 18–24 h P1 budget frees to **P4** (the designated best shot) + P6/P7. Per the task's own framing, an honest REPLAN-before-Day-1 is the *successful* outcome for a four-times-carried track — it prevents a fifth 18–24 h hypothesis on an exhausted lever.

---

## Executive summary

mine (#1443) is **four-times-carried** (S32 → S33 → S34 → S35), and each sprint refuted the then-current hypothesis with a control **before** shipping anything:

| Sprint | Hypothesis | Refuted by |
|---|---|---|
| S32 | 5th-coupling `N`-derivation | control — the `N` sign was a control-caught error |
| S33 | H1 head-label re-keying | `/tmp` control: **value-invariant on the warm residual** (22 → 22 rows, `d_N = d_Nh1`) |
| S34 | H_dual head-anchored re-keying | `/tmp` cold-MS-1 control: **value-invariant on the cold solve too** — the head-anchored prototype compiled with 0 errors but is **scalar-identical to baseline** (both cold MS-5, profit 16747.0723, 51 INFES) |
| **S35** | *this task* | **reachability analysis: the entire emit-side keying/pairing space is value-invariant (S34), and the only non-invariant lever is an LP-side reformulation, which is out of emit scope = the PATH-consultation question** |

The decisive prior fact, established by S34 Day 1: **re-anchoring the precedence dual's complementarity — `comp_pr` + `lam_pr` + `stat_x` *together* — to any label produces the identical scalar MCP**, because each `(inequality ⊥ dual)` pair is the same physical pair relabeled `l ↔ l+1`. So *any* candidate that only moves where the dual lives is value-invariant by construction. The four candidates the sprint plan enumerates are screened against this: three (a/b/c) live inside that exhausted keying/pairing space (or break MCP squareness); the fourth (d) changes the LP primal and is therefore not an emit transform.

**The reachability test each candidate must pass** (from the formal degeneracy, §2): supply a **+16000** contribution at the bound-active `stat_x(3,1,1)` row **without** (i) the objective-gradient sign flip (**BANNED**, control-refuted ≥ 4×), (ii) a bound multiplier (`x.m = 0` ⇒ `piU = piL = 0` structurally), or (iii) altering the LP primal (out of emit scope). **No candidate passes.**

---

## §1. Day-0 re-confirm (the fingerprint holds — live)

`scripts/diagnostics/kkt_residual.py data/gamslib/raw/mine.gms` on the live tree (2026-07-24):

```
verdict: CASE_B  — emit_bug
dual scale: 1.35e+04
dual transfer: CONSISTENT (max comp infeas 0.00e+00 rel, max equality residual 0.00e+00 raw)
max-residual row: stat_x(3,1,1)   rel = 2.37e+00  (raw -3.20e+04)
```

The **max row and its magnitude are byte-for-byte the S33/S34 fingerprint** (`stat_x(3,1,1)` rel 2.37, raw −32000, dual scale 1.35e4, dual CONSISTENT). Confirmations:

- **mine is `model_infeasible` (cold MCP MS 5)** at Day 0 (Task 2 `BASELINE_METRICS.md` §5); the cold solve genuinely fails, not merely a warm residual.
- **The S34 P4 sense-aware bound-transfer did not perturb mine's cold emit** — its emit md5 is `a394cbc3…`, identical to the S34 Day-0 record (Task 2 §2.4). mine's `piU_x`/`piL_x` transfer is unaffected because `x.m = 0` (nothing to transfer), so P4's MAXIMIZE `abs(var.m)` change is a no-op on mine.
- **`modelstat` asserted; `x.up=inf` BANNED** (the S31 measurement-error lesson).

> **A new corroborating observation.** The **secondary** residual rows shifted between the S34 run and this one — S34: `stat_x(1,3,1)` 1.07, `stat_x(4,1,1)` 0.815; now: `stat_x(1,3,1)` 2.00, `stat_x(4,1,1)` 1.33 — while the **max row is invariant** (2.37 / −32000) and the verdict unchanged (CASE_B, dual CONSISTENT). This is exactly the signature of a **primal-degenerate LP**: the boundary has *multiple optimal dual solutions*, so the NLP solve lands on different degenerate vertices across runs and the secondary duals move, but the structural boundary gap does not. The shifting secondary rows are *additional evidence* for the degeneracy diagnosis, not noise to explain away.

---

## §2. The degeneracy, formalized (Unknowns 1.1, 1.3)

### 2.1 The residual is the pit's top edge — 22 rows on the `c`-boundary

The nonzero residual is confined to 22 rows on the `c`-boundary (`ord(l)+ord(i) = card` / `= card+1`) and the `d\c` ring, 0 at interior rows (S33 §3.1, re-confirmed). The max row is `stat_x(3,1,1)`.

### 2.2 The max row, term-by-term (dual scale 1.35e4)

At `stat_x(3,1,1)` — `x` upper-bound-active, `x.m = 0` (the NLP puts the binding entirely into the precedence duals):

| Term | value | source |
|---|---:|---|
| `dbg_obj` | −16000 | objective gradient `(-1)(conc·value/100 − cost)` |
| `dbg_t2` (lag) | −16000 | `−sum(k, lam_pr(k,2,1,1)$c(2,1,1))` = `−Σ_k abs(pr.m(k,3,1,1))` |
| `dbg_bnd` | 0 | `piL = piU = 0` (`x.m = 0` ⇒ **no bound multiplier**) |
| **`dbg_N`** | **−32000** | obj + lag (both negative — they **add**) |

**To close, the row needs `+16000`.** But (structurally): the lag coefficient is `−1` with `lam_pr ≥ 0` ⇒ the lag term is `≤ 0` and cannot become `+16000` without the **banned** objective-gradient sign flip; and `x.m = 0` ⇒ there is **no bound multiplier** to absorb the gap. This is the S33 §3.2 / S34 Day-1 finding, re-stated.

### 2.3 Why it is a *dual-architecture* gap, not a cross-term bug

The NLP KKT stationarity for `x(3,1,1)` (LP; the precedence constraint `g = x(2,·) − x(3,1,1) ≥ 0`, `∂g/∂x(3,1,1) = −1`, multiplier `λ = Σ_k pr.m(k,3,1,1) ≥ 0`): `∂f/∂x − λ·∂g/∂x = −16000 + λ = 0 ⇒ λ = 16000`. The emit builds the MCP stationarity term for this same appearance as `+λ·∂g/∂x = −λ` (min-convention `F(x) = ∂f + Σλ∂g`), i.e. `−16000`. **The head-placed precedence dual enters the two stationarity forms with opposite orientation at the boundary, and because `x.m = 0` there is no bound multiplier to reconcile them.** The cross-term is *algebraically correct* (verified from scratch in S33 §3) — the issue is *where the head-placed dual's complementarity is anchored*, and the `x.m = 0` degeneracy leaves the emitted square MCP no feasible stationary point at the boundary (hence cold MS-5, not merely a warm residual).

**LP framing (why it is closable in principle, and by what):** mine is an **LP**, so the NLP optimum *is* the MCP optimum. The boundary rows are **primal-degenerate** (`x` at a bound, `x.m = 0`, the shadow value pushed entirely into the precedence duals). Closing the boundary requires representing that degeneracy — which needs either a bound multiplier (absent) or a different *primal* structure (an LP-side change). **No relabeling of the dual can create the missing +16000**, because the scalar system is invariant under relabeling (S34).

---

## §3. Candidate architectures, scored on reachability (Unknowns 1.1, 1.2)

Each candidate must pass the §2 reachability test: supply `+16000` at `stat_x(3,1,1)` without the banned sign flip, without a bound multiplier (`x.m = 0`), and without altering the LP primal. **All four fail.**

### (a) Explicit head-offset dual variable paired at the shifted label — ❌ REJECTED

Introduce a fresh `lam_pr` at the head label `(k,l+1,i,j)` with its own complementarity. **Refuted two ways:** (1) if it complements the *same* precedence inequality, it is the H_dual re-anchoring S34 proved **value-invariant** (the scalar MCP is unchanged — same `(inequality ⊥ dual)` pair, relabeled); (2) if it is a genuinely *new* free dual with no complementary inequality, the MCP becomes **non-square** (more multipliers than constraints) — not a valid MCP. There is no third option: a dual must either complement an existing inequality (→ value-invariant) or lack one (→ non-square). **Cannot supply +16000.**

### (b) Precedence-constraint reformulation so its dual lands at the base label — ❌ REJECTED

Re-declare `pr(k,l+1,i,j)` at the base label `(k,l,i,j)`. The inequality content is identical (`x(l,i+li,j+lj) ≥ x(l+1,i,j)`), so the dual is the same physical dual and complementarity is the same pair — a **relabeling**, hence **value-invariant** (the same class as H1/H_dual, which S33/S34 refuted). **Cannot supply +16000.**

### (c) Augmented complementarity pairing keeping both labels' multipliers live — ❌ REJECTED

Keep both `lam_pr(head)` and `lam_pr(body)` live simultaneously. This **double-counts** the precedence dual (one physical constraint, two multipliers) → the MCP is over-determined (non-square / rank-deficient) and either fails to solve or forces one multiplier to 0, collapsing to case (a)/(b). Structurally, doubling the dual would put `−2λ` in the row, i.e. `−32000` at the boundary — *worse*, not `+16000`. **Cannot supply +16000; breaks squareness.**

### (d) LP-side reformulation upstream of emit — ❌ REJECTED (out of emit scope = the consultation question)

Reformulate the LP so the boundary is not primal-degenerate — e.g. a lexicographic/perturbation anti-degeneracy transform, or splitting the degenerate variable — so a bound multiplier exists to absorb the +16000. This is the **only** lever that is *not* value-invariant, because it changes the scalar system at the primal level. **But it changes the LP being solved.** nlp2mcp's contract is to emit an MCP equivalent to the *source* model; an emit-time primal reformulation would (i) solve a different model, or (ii) be an *exact* anti-degeneracy transform, which is a **solver-side / algorithmic** concern (how PATH handles a primal-degenerate square system), **not an emit transform**. This is precisely the PATH-author question: *how should a square MCP represent a primal-degenerate LP whose shadow price lives entirely in a constraint dual with no complementary bound?* **Out of emit scope → the Sprint-36 consultation.**

### Scoring summary

| Candidate | Non-invariant? | Square MCP? | Supplies +16000 w/o sign-flip / bound-mult / primal change? | Verdict |
|---|:---:|:---:|:---:|---|
| (a) explicit head-offset dual var | No (or non-square) | ✗ | ✗ | **REJECTED** |
| (b) precedence re-declaration at base label | No (relabeling) | ✓ | ✗ | **REJECTED** |
| (c) both labels' multipliers live | No | ✗ (double-count) | ✗ | **REJECTED** |
| (d) LP-side reformulation | **Yes** | ✓ | only by changing the primal | **REJECTED (out of emit scope → consultation)** |

**No candidate survives.** The emit-side keying/pairing space is exhausted (S34), and the one non-invariant lever (d) is not an emit transform. There is no fifth emit hypothesis to design.

---

## §4. IR sufficiency (Unknown 1.4) — confirmed, but moot given the REPLAN

`EquationDef.head_domain_offsets` (the S31 IR foundation) exists and is populated in `src/ir/parser.py`; it is **consumed in the emit/KKT layer** (`src/emit/emit_gams.py` — 7 hits incl. `head_offset_marginal_index_map`) but is **NOT consumed by the stationarity cross-term path** (`src/kkt/stationarity.py` — **0 hits**, re-confirmed live 2026-07-24). Had a candidate survived §3, this IR would be its natural carrier and the work would be *wiring the existing IR into `_try_build_param_offset_crossterm`* (`src/kkt/stationarity.py:5712`) rather than adding an IR capability. **The IR is sufficient; there is simply no reachable architecture to carry.** This confirms the S34 finding and does not change the REPLAN.

---

## §5. What the `/tmp` control would have been (spec only — the gate is already refuted)

Had a candidate survived §3, its pre-`src/` `/tmp` control (PR24/PR27) would be:

1. Re-run the Day-1 term-by-term `stat_x` decomposition **from the repo root** — reproduce the 22-row `dbg_N` (obj −16000, lag −16000, bnd 0, N −32000). *(Already re-confirmed at the harness level, §1.)*
2. Emit the reconciled MCP; require the warm residual → 0 at **all** bound-active rows AND unchanged (0) at interior rows.
3. Cold/presolve solve; require **MS-1 @ 17500**, `modelstat` asserted; no srpchase / head-offset-cohort regression.

> **The gate is the cold solve, NOT the warm residual `N → 0`.** Because any keying/pairing change is value-invariant (S34), a warm `N → 0` check is un-hittable by this class of fix and is the *wrong* diagnostic — the structural change is what the cold solve reflects. **This is why H_dual could compile cleanly yet fail: it drove nothing because the scalar system was unchanged.** For S35, **no candidate reaches step 2** — the reachability screen (§3) rejects all four before any `/tmp` control is warranted. The S34 Day-1 control already executed this gate for the strongest candidate (H_dual) and refuted it.

---

## §6. REPLAN recommendation + disposition (Unknown 1.5)

**REPLAN — decided in prep, before Day 1.** No emit-side dual architecture can drive mine's cold MCP to MS-1 @ 17500; the boundary is a genuine **primal-degeneracy** the emitted square MCP cannot represent without a bound multiplier (absent) or a sign flip (banned). Every keying/pairing candidate is value-invariant (S34); the only non-invariant lever changes the LP primal and is out of emit scope.

**Disposition — hand to the Sprint-36 PATH-author consultation.** mine is the canonical instance of the class the S34 design named: *an LP whose warm KKT point is not MCP-reconcilable by emit reformulation, because the primal is degenerate at the optimum and the shadow price lives entirely in a constraint dual with no complementary bound.* This is a concrete, well-characterized question for Ferris/Dirkse (alongside rocket's Case-c question): **how should a square MCP represent a primal-degenerate LP boundary?** The de-risked hand-off is this document + `SPRINT_34/DAY1_PROGRESS_NOTES.md` (the executed H_dual control) + `SPRINT_34/MINE_DUAL_SUBSYSTEM_DESIGN.md` + the four-sprint refutation chain.

- **mine stays `model_infeasible`.** No `src/` shipped (the Nth control-first mine disposition — zero broken code, matching S31/S32/S33/S34).
- **Budget reallocation:** the P1 18–24 h → **P4** (ganges/gangesx, the designated best-remaining-shot — Task 5's three-root recovery) first, then **P6/P7**. Surfacing the REPLAN in **prep** (not on Day 3) is strictly better than S34's Day-1 surfacing: the P4 track can plan against the full freed budget from Day 0.
- **Not a "deeper architecture" carry.** S32 → S35 have now refuted the 5th-coupling, H1, and H_dual, and this task screens the *entire* remaining emit-side candidate space to zero. Carrying mine a fifth time as an *emit* track would repeat a refuted allocation; the honest next step is the consultation, not a fifth hypothesis.

**Standing BANs restated:** the objective-gradient sign flip is **BANNED** (control-refuted ≥ 4×); `x.up=inf` as a measurement device is **BANNED** (the S31 error). Neither is reconsidered here.

---

## §7. Known Unknowns verified by this task

- **Unknown 1.1** — ✅ **VERIFIED (negative): the `x.m = 0` boundary is NOT reachable by any emit-side dual architecture.** All four candidates fail the reachability test (§3): (a)/(b)/(c) are value-invariant (S34's keying/pairing space) or break MCP squareness; (d) changes the LP primal and is out of emit scope. The degeneracy is formalized (§2) and corroborated by the shifting secondary residual rows (§1, multiple optimal dual solutions of the degenerate LP).
- **Unknown 1.2** — ❌ **WRONG / REFUTED (→ REPLAN).** The hypothesis "a head-offset dual reconciliation drives the cold MCP to MS-1 @ 17500" is refuted for every candidate in the emit-side space (§3) — extending S34 Day-1's H_dual refutation to the whole space. No candidate reaches the `/tmp` cold-MS-1 gate; the disposition is the Sprint-36 PATH consultation (§6). *(Not DESIGN-SPECIFIED: there is no surviving candidate whose control is deferred — the space is screened to zero.)*
- **Unknown 1.3** — ✅ **VERIFIED** (Task-6 addendum to Task 2's Day-0-bucket block). Live harness re-confirms CASE_B `stat_x(3,1,1)` rel 2.37 / raw −32000, dual scale 1.35e4, dual CONSISTENT; the +16000 gap and the 22-row `c`-boundary breadth hold; the S34 P4 change did not perturb mine's cold emit (md5 `a394cbc3…`). New: the secondary rows shift run-to-run (degeneracy signature), the max row does not.
- **Unknown 1.4** — ✅ **VERIFIED (moot given the REPLAN).** `head_domain_offsets` exists, is consumed in `emit_gams.py` (7 hits) but not in `stationarity.py` (0 hits, re-confirmed live). It would carry a surviving candidate; none survives, so it is not wired. IR is sufficient, not the blocker.
- **Unknown 1.5** — ✅ **VERIFIED.** REPLAN recommended **in prep**; disposition = Sprint-36 PATH consultation (the primal-degenerate-LP question); freed 18–24 h → P4 first, then P6/P7. mine is four-times-carried with the entire emit-side space now screened to zero — a fifth emit hypothesis is the least defensible allocation; the consultation is the honest next step.

**Handed to Task 11 (projection):** P1 contributes **0 in-sprint Solve / 0 genuine floor** (REPLAN'd in prep); its 18–24 h reallocates to P4/P6/P7. **Handed to Task 9 (rocket consultation plan):** mine joins rocket as a second concrete Sprint-36 PATH-consultation question (the primal-degenerate-LP class). **Handed to Task 12 (schedule):** P1 needs no Day-1–5 execution slot; the freed budget front-loads P4.

---

**Document Status:** ✅ Complete — Sprint 35 Prep Task 6 (REPLAN recommendation)
**Last Updated:** 2026-07-24
**Owner:** Sprint 35 Planning Team

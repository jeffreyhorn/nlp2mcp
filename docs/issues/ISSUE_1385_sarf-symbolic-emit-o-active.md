# ISSUE #1385 — sarf: O(369K) column materialization; the emit never terminates

**Status:** 🔵 PHASE-0 AUTHORED (Sprint 37 Day 7) — **implementation NOT started.** The track is a 20–28 h atomic re-architecture; this document is its acceptance gate, which P5 has never had.
**Sprint:** 37 (P5) · **Prep:** Task 7 · **Design:** `docs/planning/EPIC_4/SPRINT_37/SARF_REARCH_REFRESH.md`

## Problem

`sarf.gms` declares `task(g,t,mn,mn)` with `|g|`=16, `|t|`=24, `|mn|`=31 ⇒ **369,024** declared columns. Only **398** are active (`taskposs(g,t) ∧ tech(g,m,n)`), and **both filters are runtime-computed**, so the active set cannot be statically enumerated. The emit is non-terminating in any pipeline budget (measured `>330 s` at cap, Sprint 35/36/37), so sarf is `translate_failure`.

## Phase 0: Acceptance Gate

### Hand-Derived KKT Shape

Not a KKT-correctness defect — the emitted shape is *right*, there is simply too much of it. The formal object is the **cardinality** of the emitted stationarity system.

For the 4-D variable `task(g,t,m,n)` the stationarity row is one per column:

```
stat_task(g,t,m,n)..  ∂f/∂task(g,t,m,n) + Σ_j [∂h_j/∂task(g,t,m,n) · ν_j] − piL_task(g,t,m,n) = 0
```

The emitted system must be **O(active)**, not O(Cartesian):

| quantity | value |
|---|---|
| declared Cartesian `card(g)·card(t)·card(mn)²` | **369,024** |
| `$taskposs(g,t)` guard domain | 46,128 (an 8× cut from the guard alone) |
| active after `∧ tech(g,m,n)` + `task.fx` | **398** |
| ratio | **927×** |

The guarded form is **valid GAMS 54 at full scale** — compiled `rc=0`, 0 errors, at `ncart` = 369,024 (Task 7 §3, at sarf's real cardinalities rather than a 54-cell analogue):

```gams
stat_task(g,t,m,n)$taskposs(g,t)..  1 - cost*tech(g,m,n) =e= 0;
task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0;
```

The correctness anchor is the banked **7-term** `stat_task` derivation (tbal ×2, labor, equipb1, equipb2, acost3, `task.lo`). A silently-wrong `stat_task` is the worst available failure mode here, because the model currently produces no golden at all to diff against.

### Expected Emit Pattern

`sarf_mcp.gms` exists (it does not today), completes in **single-digit seconds**, and contains a **parametric** `stat_task` carrying the `$taskposs`/`$tech` guards rather than 369,024 enumerated rows.

```bash
test -f data/gamslib/mcp/sarf_mcp.gms || echo "FAIL: no golden produced"
# no set-name-literal indices (the reverted Sprint-26 nu_slack("srn") anti-pattern)
grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' data/gamslib/mcp/sarf_mcp.gms && echo "FAIL: literal indices"
```

**This is the prep-doc hypothesis** (PR24); the traced surfaces are below.

### Verification Methodology

1. **Timing — the defining gate.** The re-emit completes in **single-digit seconds** (baseline: `>330 s` non-terminating; the srpchase ~2.9 s reference). *A partial improvement that does not cross the threshold is a REPLAN, not progress* — see the profile below for why.
2. **Correctness.** The emitted `stat_task` matches the banked 7-term derivation term-for-term.
3. **Corpus safety — the gate is INVERTED for sarf.** Use **`make check-goldens`** (exit 0 iff nothing drifted), **not** `make leak-check MODEL=sarf`. sarf has **no committed golden**, so `--expect-drift sarf` finds it in the *expected* set but never in the *drifted* set and reports `NO-OP` → exit 1, failing for a reason unrelated to correctness (Task 7 §4). The assertion is: **zero of the 163 goldens drift** *and* sarf newly produces one (163 → 164).
   ⚠ Run at **reduced parallelism (3 workers)**: at the default 6, slow-emit models exceed the hardcoded 600 s budget (`batch_translate.py:265`) and the verdict is `UNVERIFIED` rather than clean (Sprint 37 Day 2).
4. **Determinism** ×3 `{0,1,42}`, byte-identical.
5. **KKT-residual harness** — *not applicable until an emit exists*; run it once sarf produces one.

### PROCEED/REPLAN Signal

**PROCEED** iff the emit completes in single-digit seconds, `stat_task` matches the 7-term derivation, `make check-goldens` shows **zero** drift across 163 while sarf newly produces a golden, and determinism ×3 holds.

**Traced Fix-Surface (Day-0):** three materialization sites, all re-located on current `main`:

| site | `file:line` | role |
|---|---|---|
| **S1** | `src/ad/constraint_jacobian.py:78` (`_precompute_variable_instances`) | feeds the per-column Jacobian diff |
| **S2** | `src/ad/index_mapping.py:634` (`build_index_mapping`) | builds `col_to_var` |
| **S3** | `src/kkt/stationarity.py` | per-column `stat_task` emission (a consumer of the same column set, not a separate `enumerate_variable_instances` call) |

Materializer definition: `src/ad/index_mapping.py:327` (`enumerate_variable_instances`).

**Corpus-safety surface is wider than the fix surface: six call sites**, traversed by all 142 models, all of which must be provably unperturbed — `index_mapping.py:634`, `constraint_jacobian.py:78`, `gradient.py:287`, `gradient.py:453`, `complementarity.py:367`, `complementarity.py:512`.

**Precedent to extend, not invent:** `index_mapping.py:400` (`_is_blowup_dynamic_subset_equation`, Sprint 27 #1385) already implements a "detect a blow-up shape and short-circuit" gate for **srpchase** — a *different* shape (1-D dynamic subset of a large parent, single set-membership condition, 2-D-set Cartesian-sum body) and a different axis (*equation* enumeration, not *variable*). It is a structural precedent with an explicitly documented SCOPE caveat, not a partial solution to sarf.

**REPLAN** on any of: the parametric emit re-triggers the timeout; a **fourth** materialization site surfaces; any unrelated golden drifts; determinism breaks.

### Bucket / KPI (expected: +1 Translate only)

sarf is `translate_failure`. Success moves **Translate 135 → 136** and nothing else — it does not move Solve or Match, since the resulting MCP has never been solved. This is the **lowest-leverage** bucket in the sprint, which is why it must never displace a Solve/Match track.

### Regression guard

A fixture asserting that a variable whose declared Cartesian greatly exceeds its active set emits a **parametric** guarded `stat_` row rather than enumerated instances — fail-before/pass-after, corpus-free (`SPRINT_37/P7_INFRA_CATALOG.md` §1; a `pytest.skip`-guarded fixture on `raw/sarf.gms` would be inert in CI). ⚠ sarf itself cannot be the fixture model: at 369,024 columns the *fail-before* state does not terminate.

## Profile — where the time actually goes (Sprint 37 Day 7, new)

Capped at 180 s on current `main`, `compute_constraint_jacobian` accounts for **137 s**:

| function | calls | cum |
|---|---|---|
| `differentiate_expr` | 6,189,439 (761,897 primitive) | 121.6 s |
| `_diff_sum` | 1,154,628 | 104.5 s |
| `_is_concrete_instance_of` | 5,796,109 | 59.0 s |
| `simplify` | 10,486,266 | 49.7 s |
| `resolve_set_members` | 4,618,097 | 29.0 s |
| `CaseInsensitiveDict.__contains__` | 16,210,454 | 26.8 s |

**The blow-up is per-column differentiation, not the enumeration itself.** ~762 K top-level `differentiate_expr` calls in 180 s, against **398** columns that matter.

### A constant-factor fix was tried and is NOT sufficient — measured

`_is_concrete_instance_of` calls `resolve_set_members` on **every** invocation (5.8 M times), rebuilding the member list and linearly scanning it. Memoizing it (scratch, then reverted):

| | baseline | memoized |
|---|---|---|
| `resolve_set_members` | 4.6 M calls, 29.0 s | **out of the top-14** |
| `_is_concrete_instance_of` | 59.0 s | 39.7 s |
| `CaseInsensitiveDict.__contains__` | 16.2 M, 26.8 s | 7.5 M, 14.8 s |
| **top-level differentiations in 180 s** | **761,897** | **802,108** |

**~5 % more throughput. The bottleneck simply moved to `simplify` and `_diff_sum`.**

sarf needs `>330 s → single-digit seconds`, i.e. **~66×**. A 5 % constant-factor win cannot close that; the **927×** column ratio is where the headroom is. **This confirms the design's premise empirically: only the O(active) re-architecture can work.** Recorded so the cheap optimization is not re-attempted as a shortcut.

## References

- `docs/planning/EPIC_4/SPRINT_37/SARF_REARCH_REFRESH.md` — the design refresh (Task 7)
- `docs/planning/EPIC_4/SPRINT_36/DAY6_SARF_BANK.md`, `SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md` — the banked 3-site / 6-call-site / 7-term design
- `src/ad/index_mapping.py:400` — the srpchase #1385 gate (structural precedent)

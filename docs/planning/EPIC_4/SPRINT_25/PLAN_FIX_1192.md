# Plan to Fix #1192 — gtm Runtime Division by Zero in Stationarity Equations

**GitHub Issue:** [#1192](https://github.com/jeffreyhorn/nlp2mcp/issues/1192)
**Doc:** `docs/issues/ISSUE_1192_gtm-runtime-division-by-zero.md`
**Affected models (1192 directly):** gtm
**Adjacent models that may benefit from same fix family:** lmp2 (#1243), camcge (#1245), elec (#983), and possibly bdef-class infeasibilities in other CGE models.
**Goal:** Promote gtm from `path_solve_terminated` (EXECERROR=3) to `model_optimal` and verify match against the NLP reference.

---

## 1. Root-Cause Summary (verified 2026-04-28)

The gtm benefit equation contains `supb(i) * log((supc(i) - s(i)) / supc(i))`. The
NLP solves this by setting `s.up(i) = 0.99 * supc(i)` and relying on GAMS to
skip equation evaluation when `s.up = s.lo = 0`. Three regions
(`mexico`, `alberta-bc`, `atlantic`) have empty `sdat(i, "limit")` cells, so
`supc(i) = 0` after `supc(i) = sdat(i, "limit")` and is **not** rewritten by
the `supc(i)$(supc(i) = inf) = 100` line (which only matches `inf`, not `0`).
Both `supb(i)` and `supa(i)` end up as `NA` for those three regions because
their assignments contain `1/(supc(i) - q1)` and `supb/(supc - q1)` factors.

### What blows up in the emitted MCP

The current emission at `data/gamslib/mcp/gtm_mcp.gms:155`:

```
stat_s(i).. supa(i) - supb(i) * 1 / ((supc(i) - s(i)) / supc(i)) * supc(i) * (-1) / sqr(supc(i))
            - lam_sb(i) - piL_s(i) + piU_s(i) =E= 0;
```

For the three zero-`supc` regions:
- `(supc(i) - s(i)) / supc(i)` is `0/0` → undefined.
- `sqr(supc(i)) = 0` is in a denominator.
- `supb(i) = NA` and `supa(i) = NA` propagate NA into the equation.

GAMS aborts model generation with EXECERROR=3 because these are evaluated
during the listing pass, before PATH ever sees the model.

`bdef` (the original benefit equation, line 172) has the same `log((supc-s)/supc)` issue.
The NLP escapes it because GAMS skips equation evaluation for fixed variables; the MCP
does not, because no fix is applied at MCP emit time.

---

## 2. Fix Approaches Considered

### Option A — Per-equation `$onUndf` directive (rejected)

Wrap the stationarity block (and `bdef`) in `$onUndf … $offUndf`. Pros: 1-line
emitter change. Cons: makes UNDF/NA equations valid in GAMS but PATH may still
choke on the resulting NA Jacobian rows; turns a deterministic abort into a
solver-dependent failure mode. **Does not fix the underlying mathematical
inconsistency.**

### Option B — Model-specific variable initialization (rejected)

The issue doc suggests `s.l(i) = sdat(i, "ref-q1")`. For mexico, `ref-q1 = 0.5`
but `s.up(i) = 0.99 * supc(i) = 0` clamps it back to 0; stationarity still
evaluates a derivative containing `1/supc(i) = 1/0`. **Does not address the
zero-denominator parameter.**

### Option C — Parameter-value-aware conditional stationarity (rejected as scope-too-large)

Detect at IR/emit time that `stat_s(i)` references `1/supc(i)` (or
`1/sqr(supc(i))`) and emit `stat_s(i)$(supc(i) <> 0)`. Requires expression
analysis to identify denominator parameters, plus tracking which parameters can
be zero in source. Generic but ~1.5 days of work and high regression surface.
**Defer to Sprint 26 if Option D doesn't carry.**

### Option D — Variable-bounds-aware conditional stationarity (RECOMMENDED)

The cleanest invariant that captures the gtm pathology and generalizes to
related issues:

> If a variable `v` has `v.up(d) ≤ v.lo(d)` for some index `d` (i.e., `v(d)`
> is effectively fixed), the stationarity equation `stat_v(d)` is degenerate
> for that index and should be skipped at runtime via a `$(v.up(d) - v.lo(d) > eps)`
> guard. The variable becomes complementary with itself via the existing
> `comp_lo_v` / `comp_up_v` pair (or trivially fixed) and PATH does not need
> the stationarity row.

For gtm: `s.up(i) = 0.99 * supc(i)` evaluates to 0 for the three regions, so
`s.up(i) - s.lo(i) = 0 - 0 = 0`, the guard fires, and `stat_s(i)` is skipped
for those instances. PATH gets a well-defined model.

For `bdef` (the original equation, which also has the log-of-0/0 issue): the
NLP itself relies on GAMS' "fixed variable skip equation evaluation" semantics.
We can replicate this at MCP emit time by emitting `s.fx(i)$(s.up(i) - s.lo(i) <= eps) = 0;`
for any variable with parameter-dependent bounds, BEFORE the equations are listed.
GAMS will then skip evaluation of `bdef` for the fixed indices.

**Why this generalizes:**
- **#1243 (lmp2):** if we ensure `y.l(p) > 0` via init AND condition stationarity on `y.up(p) > y.lo(p) + eps`, the `1/y(p)` derivative is well-defined for non-fixed instances and skipped for fixed ones.
- **#1245 (camcge):** non-traded elements have `pd(i) = 0`, but the variable that's actually fixed is the corresponding traded subset's price; the bounds-based guard catches this if `pd.up = pd.lo = 0` (need to verify).
- **#983 (elec):** distance-zero pairs would need the same guard pattern.

The bounds-based guard is **GAMS-native**, **parameter-agnostic** (no symbolic
analysis required), and aligns with how the NLP expects fixed variables to be
treated.

### Option E — Hybrid: Option D + targeted denominator guard (FALLBACK)

If Option D alone doesn't unblock gtm because PATH still rejects the model
(e.g., due to NA in `bdef`), add the bdef-side guard: condition the original
benefit-summation term on the same parameter:

```
bdef..  benefit =e=
   sum(j, dema(j) * d(j) ** demb(j))
   - sum(i$(supc(i) <> 0), supa(i)*s(i) - supb(i)*log((supc(i)-s(i))/supc(i)))
   - sum((i,j)$ij(i,j), utc(i,j)*x(i,j));
```

This is more invasive (rewrites the source equation) and requires either
detecting "denominator parameters" in the body or accepting a one-off rewrite
for gtm. **Use only if Option D is insufficient on a Tier-0 retest.**

---

## 3. Recommended Implementation: Option D

### 3.1 Overview

Add an emitter pass that, for every primal variable `v` with parameter-dependent
upper or lower bounds, generates two lines into the MCP output:

1. **Variable-fix line** in the existing variable-bounds section:
   ```
   v.fx(d)$(v.up(d) - v.lo(d) <= 1e-10) = v.lo(d);
   ```
   This forces GAMS to skip equation evaluation involving `v(d)` for those indices.

2. **Stationarity guard** in the existing `stationarity_conditions` machinery
   (`src/kkt/stationarity.py:1206-1219`): wrap the stationarity body in a
   `DollarConditional` with the same `v.up(d) - v.lo(d) > 1e-10` condition.

Both pieces plug into existing infrastructure:
- `kkt.stationarity_conditions[var_name]` already exists for per-variable access conditions (Issue #1147/#1160).
- The `_emit_fix_inactive` block at `src/emit/emit_gams.py:1899-2229` already emits `.fx(d)$(...) = ...` lines for inactive multipliers.

### 3.2 Code Sites

| File | Function | Change |
|------|----------|--------|
| `src/kkt/stationarity.py` | new `_build_bounds_guard(var_def, model_ir)` helper | Build `v.up(d) - v.lo(d) > 1e-10` condition expression for a `VariableDef` whose bounds reference parameters (not hard-coded constants). |
| `src/kkt/stationarity.py` | inside the loop at line ~1145 (per-variable stationarity build) | Combine the bounds-guard with the existing `access_cond` and store in `kkt.stationarity_conditions[var_name]`. |
| `src/emit/emit_gams.py` | new `_emit_bounds_guard_fixings` near the existing variable-bounds emission (~line 1500) | For each variable in the bounds-guard set, emit `var.fx(d)$(var.up(d) - var.lo(d) <= 1e-10) = var.lo(d);` BEFORE the equations section. |

### 3.3 Detection criterion: "parameter-dependent bounds"

A variable `v` is in scope for the bounds-guard fix iff:
1. `v.up_expr` or `v.lo_expr` is set (i.e., the bound is an expression, not a numeric constant), OR
2. `v.up_map` or `v.lo_map` contains at least one entry where the expression is a `ParamRef` or arithmetic involving a `ParamRef`.

For gtm, `s.up(i) = 0.99 * supc(i)` qualifies because `supc(i)` is a `ParamRef`.

For variables with only static numeric bounds (e.g., `x.up = 1.0`), the guard is unnecessary — those bounds can't surprise us at runtime.

### 3.4 Tolerance choice

Use `1e-10` as the equality threshold for `v.up(d) - v.lo(d)`. This avoids:
- Spurious fires when `v.up = v.lo = 0` for genuinely fixed variables (matches exactly).
- False negatives when bounds are computed with floating-point arithmetic (e.g., `0.99 * 0.0 = 0.0` is exact, but `0.99 * tiny_value` might round).

If 1e-10 turns out to suppress legitimate stationarity rows, fall back to exact equality (`v.up(d) - v.lo(d) <= 0`) at risk of edge-case FP issues.

---

## 4. Test Plan

### 4.1 New unit test — `tests/unit/kkt/test_bounds_guard_stationarity.py`

Three cases, all using small synthetic inline GAMS:

1. **Variable with parameter-dependent upper bound that can be zero:**
   - Source has `Parameter cap(i) /a 0, b 1, c 2/; x.up(i) = cap(i);`
   - Assert emitted MCP contains `x.fx(i)$(x.up(i) - x.lo(i) <= 1e-10) = x.lo(i);`
   - Assert `stat_x(i)` body is wrapped in `$(x.up(i) - x.lo(i) > 1e-10)` (or equivalent).

2. **Variable with static numeric bounds (negative case):**
   - Source has `x.up = 1.0;`
   - Assert emitted MCP does NOT contain a bounds-guard fix line for `x`.

3. **Variable with parameter-dependent bound on positive variable:**
   - Same as case 1 but `Positive Variable x(i);` so `x.lo(i) = 0` is implicit.
   - Assert emitted MCP guard works correctly when only `up` is parameter-dependent.

### 4.2 Integration test — `tests/integration/emit/test_gtm_bounds_guard.py`

```
@pytest.mark.integration
def test_gtm_no_div_by_zero_in_stationarity():
    src = "data/gamslib/raw/gtm.gms"
    if not os.path.exists(src):
        pytest.skip("gamslib gitignored on this runner.")
    output = _emit_mcp_for(src)
    # Three zero-supc regions must have a bounds-guard fix
    assert "s.fx(i)$(s.up(i) - s.lo(i) <= 1e-10)" in output
    # stat_s(i) must be conditioned
    assert any("stat_s" in line and ("$(s.up(i) - s.lo(i)" in line or "$(s.up - s.lo" in line)
               for line in output.splitlines())
```

### 4.3 Pipeline retest

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --model gtm --quiet
```

Acceptance criterion: `Solve: 1 (100.0%)` and `Match: 1 (100.0%)` (or
`model_optimal` outcome at minimum).

### 4.4 Regression sweep

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --solve-success --quiet
```

Acceptance criterion: 0 NEW translate failures and 0 NEW solve regressions
versus the post-Day-10 baseline (Match 54, Solve 106).

Particular attention to other models with parameter-dependent bounds:
- `bearing` (presolve-class)
- `lmp2` (already terminated; should be unaffected)
- `camcge` (already terminated; should be unaffected — separate root cause)
- `harker`, `china`, `turkey` (mismatch class — verify no change in objective)

---

## 5. Time Estimate

| Phase | Work | Hours |
|-------|------|-------|
| 1. Setup | branch, reproduce, verify gtm currently aborts at EXECERROR=3 | 0.25 |
| 2. Helper function | `_build_bounds_guard` in `stationarity.py` (param-dependent detection + condition expression construction) | 1.0 |
| 3. Emitter wiring | fix-line emission near existing variable-bounds section + thread into stationarity-condition machinery | 1.5 |
| 4. Unit tests | 3 synthetic cases in `tests/unit/kkt/test_bounds_guard_stationarity.py` | 1.0 |
| 5. Integration test | gtm-specific test in `tests/integration/emit/test_gtm_bounds_guard.py` | 0.5 |
| 6. gtm validation | re-emit, GAMS compile check, PATH solve, NLP-vs-MCP comparison | 0.75 |
| 7. Regression sweep | full-corpus solve-success retest, diagnose any flake/regression | 1.0 |
| 8. Quality checks | `make typecheck && make format && make lint && make test` | 0.5 |
| 9. PR + review | open PR, address Copilot review (~1 round expected) | 1.0 |
| **Total** | **~7.5 hours (best case 6h, worst case 9h)** | |

**Within Sprint 25 budget.** Fits a single working day. If gtm doesn't promote
to `match` after Option D (e.g., still infeasible due to bdef NA), pivot to
**Option E** as a same-PR follow-up — adds 2–3h.

---

## 6. Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| **Bounds-guard breaks Tier-0 canaries** that have legitimately fixed variables expected to participate in stationarity | Medium | The guard fires only when `v.up - v.lo ≤ 1e-10`; legitimately fixed vars (set via `var.fx(...) =`) generate per-index `lo_map[d] == up_map[d]`, which would also be skipped — but those models don't generate stationarity for them today (handled via `kkt.stationarity_conditions`). Dry-run the guard on the Tier-0 set first; if any Tier-0 model regresses, narrow the criterion to "parameter-dependent bound only" (skip the guard for static `var.fx`). |
| **PATH chokes on the conditional-stationarity form** (e.g., requires `=E=` rows for every column) | Low | The MCP convention is that fixed variables don't need a stationarity row — they're complementary with their own bound multiplier. If PATH does require a row, fall back to emitting a trivial `0 =E= 0` for the skipped indices instead of suppressing entirely. |
| **`bdef` still aborts** because GAMS evaluates it during model listing even with `s.fx = 0` | Medium | The NLP already proves this works in GAMS (`s.up = 0.99 * supc = 0` makes the var fixed and the equation skipped). If MCP behaves differently, add Option E (denominator-aware $-condition on the bdef sum body). |
| **`v.up_expr` detection misses some IR shapes** (e.g., bound set via assignment in pre-solve code rather than declaration) | Medium | Audit the gtm IR explicitly; if `s.up(i) = 0.99 * supc(i)` is in the pre-solve assignment block (`emit_pre_solve_param_assignments`) rather than `var_def.up_expr`, route the detection through `var_def.up_map` populated by the parameter-assignment pass, OR compute the guard condition from the `s.up`/`s.lo` GAMS attributes at runtime regardless of source IR shape (which is what Option D does anyway — the condition references `s.up(i)` directly, not the underlying `supc(i)`). |
| **Tolerance 1e-10 is wrong** | Low | Tolerance is a one-line tweak; 1e-12 or 0 are safe alternatives if the corpus reveals a problem. |
| **Regression: a model whose bounds happen to satisfy `up - lo < 1e-10` for some index but the stationarity is still mathematically meaningful (e.g., a soft-fixed initial guess)** | Low | This is structurally equivalent to a fixed variable — KKT theory says those don't need stationarity rows. If a corpus model surprises us, document it and tighten the guard to also require parameter-dependent bound (not literal numeric `up = lo`). |

---

## 7. Out-of-scope (deferred to follow-up issues)

- **Generic denominator-parameter detection (Option C):** Defer to Sprint 26 if Option D doesn't carry the related issues (#1243, #1245, #983).
- **Re-emit stale checked-in MCP artifacts** for any models whose emitted output changes: out of scope; queue for the post-Sprint-25 housekeeping PR mentioned in `ISSUE_FIX_OPPORTUNITIES.md`.
- **`$onUndf` directive support:** Not needed for this fix; if a future model genuinely requires it, file separately.

---

## 8. PR Title and Branch

- **Branch:** `sprint25-fix-1192-gtm-bounds-guard`
- **PR title:** `Sprint 25: Fix #1192 — gtm runtime div-by-zero via parameter-bounded variable guard`
- **PR body:** standard structure (Summary / Root cause / Fix / Test plan / Refs).
- **Closes:** #1192. Mentions but does not close #1243 / #1245 / #983 (those need separate verification post-Option-D).

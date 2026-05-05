# camcge: PATH $141 on Phantom IndexOffset `nu_ieq(i±N)` / `nu_actp(i±N)` References in Stationarity

**GitHub Issue:** [#1354](https://github.com/jeffreyhorn/nlp2mcp/issues/1354)
**Status:** OPEN — Sprint 26 carryforward (filed Sprint 25 Day 13)
**Severity:** Medium — model translates cleanly but PATH compilation fails with `Compilation error(s)`; user gets no MCP solution
**Date:** 2026-05-05
**Last Updated:** 2026-05-05
**Affected Models:** camcge (confirmed); likely related to #1355 (cesam2) — same Pattern C variant family

---

## Problem Summary

camcge translate succeeds (post-#1245), but the emitted MCP fails GAMS compilation with **3 `$141` errors** ("Symbol declared but no values have been assigned"). All three originate in stationarity equations that emit per-offset enumerations of `nu_<eq>(i±N)` for offsets that the source equation never actually realizes.

Pre-Sprint-25 baseline: `path_solve_terminated` (translate failed). Post-Sprint-25 (Day 11 retest): `path_syntax_error` — one of the four bucket additions during Sprint 25 (see SPRINT_LOG.md Day 11 §"Revised Checkpoint 2 evaluation").

---

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/camcge.gms \
  -o /tmp/camcge_mcp.gms --skip-convexity-check --quiet
gams /tmp/camcge_mcp.gms lo=2

# *** Error 141 in /tmp/camcge_mcp.gms (lines 525, 543, 557, 744, 747)
# *** Status: Compilation error(s)
```

---

## Buggy Emit — `stat_dk(i)` (line 525)

```gams
stat_dk(i).. pk(i) * nu_prodinv(i) + ((-1) * imat(i,i)) * nu_ieq(i)
  + (((-1) * imat(i-1,i)) * nu_ieq(i-1))$(ord(i) > 1)
  + (((-1) * imat(i+6,i)) * nu_ieq(i+6))$(ord(i) <= card(i) - 6)
  + (((-1) * imat(i+3,i)) * nu_ieq(i+3))$(ord(i) <= card(i) - 3)
  + (((-1) * imat(i+4,i)) * nu_ieq(i+4))$(ord(i) <= card(i) - 4)
  + ... (i±N for N = 1..10) ...
  =E= 0;
```

`nu_ieq` is the multiplier for the `ieq` equation. The source `ieq(i)` only references `imat(i,i)` (the diagonal) — so `nu_ieq(i+1)`, `nu_ieq(i-7)`, etc. are referenced by stationarity but never **defined** by any equation declaration, triggering `$141`.

`stat_dst(i)` and `stat_p(i)` exhibit the same shape on `nu_prodinv(i±N)`, `nu_actp(i±N)`, `nu_pkdef(i±N)`. `stat_xd(i)` (line 557) similarly references `nu_inteq(i±N)` for offsets that `inteq(i).. =e= io(i,i) * x(i) ...` never realizes.

---

## Likely Root Cause

This is the **launch-shaped phantom-offset enumeration** (see `docs/planning/EPIC_4/SPRINT_25/DAY5_PATTERN_A_INVESTIGATION.md`) appearing on a CGE model. Day 6 PR #1308 narrowed the Pattern C gate (`src/kkt/stationarity.py`) to launch's specific shape (alias-conditional `$ge(ss, s)` sums); camcge's `imat(i,j)` is also alias-shaped (the second `j` index gets unified with `i` and then enumerated ±N), but the gate did not catch it because the source body has no `$ge(...)`-type alias-conditional guard — it has plain `imat(i,j)` SAM-coefficient references.

In other words: the AD layer is treating the second index of `imat(i,j)` as an alias of `i` and then exploding the assembly into a per-offset `nu_<eq>(i+N)` enumeration where, for each N, only one offset is actually present in the source equation.

---

## Where to Fix

`src/kkt/stationarity.py` — generalize the Pattern C gate to detect plain-alias enumeration (no `$cond` filter required) and consolidate the per-offset emission into a single domain-scoped sum:

```gams
sum(j$(domain_filter), imat(j,i) * nu_ieq(j))
```

scoped to the equation's declared domain.

Care is needed not to regress the working Day 6 launch fix (`#1306` / `#1307`) or the Tier 0/1 canary set (which currently emits these structures byte-identically to baseline for non-affected models like quocge / prolog / irscge — verified by Day 7 cohort sweep at `DAY7_COHORT_SWEEP.md` Task 1, 54/54 PASS).

---

## Tests to Add

- **Unit test** in `tests/unit/kkt/`: minimal `ModelIR` with a scalar / indexed equation `ieq(i).. = imat(i,i) * dk(i)`, with `dk` declared on `(i,)` and `imat(i,j)` declared on `(i,j)`. Assert that `stat_dk(i)` body has no `nu_ieq(i±N)` references for `N != 0`, OR consolidates them into a single domain-scoped sum.
- **Integration test** in `tests/integration/emit/`: assert camcge's emitted `stat_dk` / `stat_dst` / `stat_p` / `stat_xd` have no `nu_<eq>(i+N)$(ord(i) <= card(i) - N)` substring for `N >= 1`.
- **Pipeline check**: after fix, camcge moves out of `path_syntax_error` (likely into `model_infeasible` per #1330 / #1324, or solves directly).

---

## Files Involved

- `src/kkt/stationarity.py` — Pattern C gate (the launch-shaped narrowing was added in PR #1308; needs widening)
- `src/ad/constraint_jacobian.py` — alias unification path that produces the per-offset enumeration
- `data/gamslib/raw/camcge.gms` — primary integration test source
- `data/gamslib/mcp/camcge_mcp.gms` — current buggy emit (regenerated each run)

---

## Estimated Effort

**6–10h** for the gate generalization itself, plus a corpus regression sweep across the 54-model matching set (the Pattern C gate broadening risks regressions on any alias-shaped sum; expect to run the byte-diff harness from `DAY7_COHORT_SWEEP.md` Task 1 before/after).

---

## Related

- **#1245** (CLOSED) — unblocked translate; surfaced this issue.
- **#871, #1320, #1322** (camcge stationarity fixes — none addressed phantom IndexOffset).
- **#1306 / #1307** — Pattern C Bug #1 / Bug #2 on launch (same shape family, narrower fingerprint).
- **#1330 / #1324** — other open camcge issues (different bucket: `model_infeasible` and div-by-zero).
- **#1355** (cesam2) — same Pattern C variant family on `nu_COLSUM(i±N)` in `stat_tsam`.

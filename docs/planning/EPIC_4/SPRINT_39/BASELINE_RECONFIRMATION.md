# Sprint 39 Prep Task 2 — Baseline Reconfirmation

**Measured at:** `a8669ad6` (main, 2026-08-27) · **Toolchain:** GAMS **54.2.1** / PATH **5.2.01**
**Method:** every figure below was **re-derived by running a command at this commit**, not read from a document. All GAMS runs were performed from `/tmp/s39t2/`; the repo root is byte-clean afterwards (`git status --porcelain` → 0 entries).

> **Why this task exists.** Sprint 38 proved twice that a banked figure is a liability: a Day-8 prompt sweep corrected six stale figures and was re-staled by that same sprint's Day-9 re-baseline within 24 h, and a five-sprint-old consultation package described a failure mode that no longer reproduced. Prep had re-verified the *conclusion* and stamped the toolchain — but not the *description*.

---

## 1. Verdict summary

| # | figure | verdict | command |
|---|---|---|---|
| 1 | KPI block (Solve 111 · Match 96 = 65+31 · Translate 135 · mi 7 · pse 6 · all-219 99 · Parse 142) | ✅ **REPRODUCED** | `scripts/sprint_audit/kpi_block.py` |
| 2 | Genuine floor **73** = baseline 73 + 0 entries | ✅ **REPRODUCED** | `scripts/sprint_audit/floor_tracker.py` |
| 3 | `path_solve_terminated` **0** | ✅ **REPRODUCED** | DB count over the 142 candidates |
| 4 | `path_solve_license` **11** | ✅ **REPRODUCED** | DB count |
| 5 | dyncge `CASE_B`, **6.22e-02** at `stat_pf(CAP,SRV)`, 5 top rows | ✅ **REPRODUCED** | `scripts/diagnostics/kkt_residual.py` |
| 6 | dyncge cold MCP **MS-1 @ 381401.119** vs NLP **539570.5027** (29.3 %) | ✅ **REPRODUCED** | DB `solution_comparison` |
| 7 | lnts **MS-4 at iteration 0**; fresh emit byte-identical to golden; `5` / `45` | ✅ **REPRODUCED** | fresh emit + `gams` in scratch |
| 8 | agreste **MS-5 after 9,734** iters · mine **MS-5 after 10,662** | ✅ **REPRODUCED** | live `gams` on each committed golden |
| 9 | agreste NLP **MS-1 @ 17706.43** · mine NLP **MS-1 @ 17500.0** | ✅ **REPRODUCED** (with a caveat, §3.1) | live `gams` on each raw source |
| 10 | `weapons` still the **only** spurious presolve match | ✅ **REPRODUCED** (full population) | `check_mcp_solve_attribution.py`, all 34 |
| 11 | dangling `mcp_file_used` rows = **14** (13 + `weapons`) | ✅ **REPRODUCED** | DB scan over presolve rows |
| 12 | four sarf call sites at `gradient.py:287/453`, `complementarity.py:367/512` | ✅ **REPRODUCED** (exact lines) | `grep -n "enumerate_variable_instances(var_def"` |
| 13 | sarf killed at **28 m 40 s** vs the ≤300 s gate | 🔶 **CLAIM REPRODUCED, FIGURE NOT REPRODUCIBLE** (§3.2) | capped translate, 1900 s |
| 14 | leak-gate **186** in-scope, **7** allowlisted, all clean; `--min-scope` on discovery | ✅ **REPRODUCED** | `check_golden_staleness.py` |

**No baseline figure was found to be wrong.** Every headline KPI and every banked fingerprint reproduced. One banked figure (sarf's 28 m 40 s) turns out **not to be a reproducible quantity at all** — §3.3. The corrections below are to the *prep plan's own verification machinery*, to *population definitions*, and to one *cost-attribution assumption*, not to the baseline.

---

## 2. Corrections — each routed to a named owner

### 2.1 ⚠ PREP_PLAN's own check for the four sarf call sites verifies the wrong thing → **Task 6 (P4)**

`PREP_PLAN.md` Task 6's Verification block runs:

```bash
grep -E -n "referenced-instance|_is_concrete_instance_of|resolve_set_members" \
  src/ad/constraint_jacobian.py src/ad/index_mapping.py src/kkt/stationarity.py
```

**None of those are the four call sites.** Sprint 38 Day 7 recorded them as `src/ad/gradient.py:287` and `:453`, and `src/kkt/complementarity.py:367` and `:512`, checked with `grep -n "enumerate_variable_instances(var_def" src/ad/gradient.py src/kkt/complementarity.py` (`DAY7_SARF_GATE_P6C.md` §4).

The snippet's own comment claims it must not suppress errors "because these files moved in Sprint 38" — which inverts the situation:

| file | commits since the Day-7 anchor `949a4587` |
|---|---|
| `src/ad/gradient.py` | **0** |
| `src/kkt/complementarity.py` | **0** |
| `src/kkt/stationarity.py` | 2 |
| `src/emit/emit_gams.py` | 4 |

It greps the files that *did* churn and never touches the two that hold the sites. The real check passes cleanly — all four sites are at their **exact recorded line numbers** — but the plan would not have told anyone that. **Routed to Task 6**, which owns Unknown 4.1, and the snippet should be replaced with the Day-7 form.

### 2.2 Four different presolve-population counts, all correct → **Task 8 (P7)**

These are distinct populations and must not be "reconciled" into one another:

| count | meaning |
|---|---|
| **48** | DB rows with `outcome_category == model_optimal_presolve` (all 219) |
| **40** | `*_mcp_presolve.gms` goldens on disk |
| **34** | presolve **∧ match** (all 219) — the attribution tool's scope |
| **31** | presolve ∧ match ∧ convex candidate — the KPI block's "presolve" line |
| **14** | of the 48, those whose recorded `mcp_file_used` path no longer exists |

P7's remedy is scoped to "all 14 rows or none". **Routed to Task 8** so the remedy names which population it covers.

### 2.3 sarf's hot path is **equation**-instance enumeration, not the four **variable**-instance sites → **Task 6 (P4)**

The four banked call sites are all `enumerate_variable_instances(var_def, …)`. A live capped run tells a different story about where the time goes: at the cap the process is inside **`enumerate_equation_instances`**, reached from `src/ad/constraint_jacobian.py:947`, `:1117` and `:1424`, emitting a stream of

```
Failed to evaluate condition SetMembershipTest(equipposs, (SymbolRef(n), SymbolRef(t)))
  … the set has no concrete members at compile time. Including unevaluable instances by default.
```

So a set-membership condition that cannot be resolved statically causes the enumerator to **include every instance by default** — a combinatorial expansion, in a different function and a different file from the four recorded sites.

**This does not refute the banked attribution** (Day 6/7 measured the variable-instance sites and the filter was emit-preserving), but it means the four sites cannot be assumed to be the whole cost. **Routed to Task 6**, which owns Unknown 4.2 — *"do the four sites actually account for the bulk of the remaining wall-clock?"* This is direct evidence that the answer may be **no**, and 4.2 should be treated as genuinely open rather than a formality.

### 2.4 `robot` has no owning issue doc → **Task 11 (P10)**

Of the 31 non-solving convex candidates, 30 have an owning `ISSUE_*.md`; **`robot`** does not. It is in the 11-model `license-gated` cohort. **Routed to Task 11**, which owns the backlog-catalog refresh.

---

## 3. Notes that change how a figure should be read

### 3.1 agreste's raw source runs **two** solves

Re-deriving agreste's NLP objective prints **two** optimal solves: `16277.4895`, then `17706.4300`. The banked figure is the **second**. A naive "read the objective off the listing" that takes the first match gets a different number and would look like a contradiction. (This is the same class as the standing rule *"always assert `modelstat` before reading an objective off a solve"*.)

### 3.2 sarf's "28 m 40 s" is a **kill time**, not a property of the model

The claim reproduces in the sense that matters: **sarf does not terminate.** A capped translate ran **1900 s (31 m 40 s)** — longer than the banked kill — and was still enumerating, with **no output file produced**. That is ~**6.3×** the ≤300 s gate, so the gate is unambiguously not met.

But **the number itself is not reproducible and should stop being quoted as though it were.** "28 m 40 s" is when a Day-7 operator chose to kill the process, not a duration sarf converges to. Re-running produces whatever cap you set. Future documents should say *"exceeds the ≤300 s gate by at least 6×; does not terminate"* and cite a cap, not a figure.

> **⚠ Methodology failure inside this task, recorded because it is the exact class this task exists to catch.** My first capped run reported `COMPLETED (SystemExit)`. It had not completed. The CLI catches the injected `TimeoutError` and exits via `SystemExit(1)`, and my harness's `except SystemExit:` branch printed "COMPLETED" — so a cap-hit was rendered as a success. It was caught only because the elapsed time (1901 s) sat suspiciously against the 1900 s alarm and the output directory was empty. **A harness that cannot distinguish "finished" from "was stopped" produces exactly the banked-figure problem this task exists to prevent.** The corrected run asserts on the output artifact, not on the exception type.

### 3.3 Unknown 1.1 — twocge and elec are **not symmetric**, and this bears on the floor decision

Both cold goldens changed at their landing commits, and both models were `path_solve_terminated` with `solver_version: None` beforehand (aborted before PATH ran), so neither match can be a solver effect. The full-population attribution run independently confirms both now produce **their own** `MCP MS-1` rather than reading back the embedded NLP's answer. That much is symmetric.

**The nature of the two cold changes is not:**

| model | cold diff | what changed |
|---|---|---|
| **twocge** (`204f35ac`) | +10 / −0 | a comment block plus **two `nu_*.fx(...)` guard lines** — the change is *entirely* within the `_fx_` multiplier-fixing region |
| **elec** (`82b91c94`) | +3 / −3 | the **stationarity equations themselves** — `sum(j, sum(j__$(ut(i,i)), …))` → `sum(j__$(ut(i,j__)), …)`, i.e. the always-false diagonal guard replaced by the correct one and a spurious outer sum removed |

Unknown 1.1's research question 5 asks whether either change "is confined to a `_fx_`-only region that a reviewer might reasonably call a methodology artifact". **For twocge the answer is yes; for elec it is emphatically no.** The Sprint 38 retrospective argued both qualify on the identical ground ("both had their cold emit changed"). That is true but under-describes twocge, whose entire cold delta is `.fx` lines.

**This does not decide P1** — it is Task 3's decision, and this task deliberately does not make it. It narrows it: the floor is **73, 74, or 75**, and the 74 case (elec qualifies, twocge does not) is a live reading that the Sprint 38 close did not consider.

---

## 4. Evidence index

| figure | evidence |
|---|---|
| KPI / floor | `/tmp/s39t2/kpi.txt`, `/tmp/s39t2/floor.txt` — both self-report `derived at a8669ad6` |
| terminated / license | `/tmp/s39t2/terminated.txt` |
| dyncge | `/tmp/s39t2/dyncge.txt` |
| lnts | `/tmp/s39t2/lnts/lnts_mcp.lst` |
| agreste / mine MCP | `/tmp/s39t2/agreste_mine.txt` |
| agreste / mine NLP | `/tmp/s39t2/nlp.txt` |
| attribution (34) | `/tmp/s39t2/attr.txt` |
| dangling rows | `/tmp/s39t2/dangling.txt` |
| non-solving population | `/tmp/s39t2/u101.txt` |
| sarf | `/tmp/s39t2/sarf.txt` |
| leak gate | `/tmp/s39t2/leakgate.txt` |

---

**Document Status:** ✅ COMPLETE — Sprint 39 Prep Task 2
**Last Updated:** 2026-08-27

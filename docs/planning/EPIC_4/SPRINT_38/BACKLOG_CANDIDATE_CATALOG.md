# Sprint 38 Prep Task 10 — Emit-Backlog Candidate Catalog & Selection-Rule Dry Run (P8)

**Date:** 2026-08-18 · **Branch:** `planning/sprint38-task10` · **Measured at:** `32a839d5` · **Toolchain:** GAMS **54.2.1** / PATH **5.2.01** · **Scope:** measurement + catalog. No `src/`, DB or golden change.

**Verdict: ✅ P8 CLEARS ITS ≥2 THRESHOLD WITH ROOM — 5 of 11 candidates satisfy the pre-registered rule. But NONE is eligible today, because not one of them has a Phase-0 gate.** P7 and P8 are therefore **not independent tracks**: P7 is P8's prerequisite, and Task 9's Tier 1 needs re-ordering to match the shortlist below.

**A second finding, produced by this task tripping the trap it was told to guard against:** the static co-occurrence pattern for the lnts defect matches **6 models, of which 5 solve fine — an 83 % false-positive rate.** Only a runtime bound probe discriminates. §4 derives the operational criterion from that.

---

## 1. The candidate pool — 11 models

Query: `outcome_category ∈ {path_solve_terminated, path_syntax_error, model_infeasible}`, minus the deep tracks (`ganges`, `gangesx`, `sarf`, `camcge`, `turkey`, `rocket`, `mine`, `fawley`, `markov`).

The pool is **17 models; 6 are deep-track**, leaving **11**. All 11 **have committed goldens** — emit succeeds for every one of them, so every failure below is at GAMS-compile, GAMS-execution, or PATH stage, never at translate.

| model | outcome category | NLP reference | owning issue doc(s) | Phase-0 gate |
|---|---|---|---|---|
| twocge | `path_solve_terminated` | MS-2 | #906 #970 #1251 #1277 #1278 #1331 | ❌ none |
| tricp | `path_solve_terminated` | MS-2 | #933 #1062 | ❌ none |
| elec | `path_solve_terminated` | MS-2 | #983 #1325 | ❌ none |
| dyncge | `path_solve_terminated` | MS-2 @ 539570.5027 | **— none —** | ❌ none |
| lnts | `model_infeasible` | MS-2 @ 0.5547 | **— none —** | ❌ none |
| agreste | `model_infeasible` | **MS-1 @ 17706.43 (LP)** | **— none —** | ❌ none |
| cesam | `model_infeasible` | MS-1 @ 0.0096 | **— none —** | ❌ none |
| indus | `path_syntax_error` | — | **— none —** | ❌ none |
| dinam | `path_syntax_error` | — | #926 | ❌ none |
| turkpow | `path_syntax_error` | — | #1292 #1316 | ❌ none |
| clearlak | `path_syntax_error` | — | #1291 | ❌ none |

**Two things the table says that the DB does not.**

**The DB's own category names mislead on 4 of 11.** `path_solve_terminated` reads as *"PATH ran and gave up"*. It did not: dyncge, elec, tricp and twocge all carry **`solver_version: None`** and abort at **GAMS execution**, before PATH is invoked at all. Their real terminal states are `SOLVE ... ABORTED, EXECERROR = n`. Anyone budgeting these as solver-tuning work would be budgeting the wrong thing — they are emit defects.

**5 of the 11 have no owning issue doc whatsoever** — agreste, cesam, lnts, dyncge, indus. Their DB error messages are the generic `Parse error: compilation_error` / `no_solve_summary` / `Model: Infeasible (status 4)`, which carry **no fingerprint at all**. For these the DB tells you a model failed and nothing about why; the fingerprint had to be reproduced from scratch.

## 2. The selection-rule dry run

**Pre-registered rule:** a model enters the sweep only if it has a **reproduced fingerprint** AND a **named fix surface**. Anything requiring a new diagnosis is **banked, not started**.

### 2.1 Eligible on the pre-registered rule — 5

| # | model | reproduced fingerprint (mechanism, not pattern) | terminal state | named fix surface |
|---|---|---|---|---|
| 1 | **twocge** | **8** × `MCP pair <e>.<nu> has empty equation but associated variable is NOT fixed`, over **2 distinct pairs** — `eqpw.nu_eqpw`, `eqw.nu_eqw` | `SOLVE from line 692 ABORTED, EXECERROR = 8` | **#1331**, which names both pairs exactly |
| 2 | **tricp** | **108** × `Unmatched variable not free or fixed` | `SOLVE from line 205 ABORTED, EXECERROR = 108` | **#1062** (unmatched slp/sln variables) |
| 3 | **elec** | `Exec Error at line 99/100/101: division by zero (0)`, then **30** × `Evaluation error(s) in equation "stat_x(iN)"` | `SOLVE from line 133 ABORTED, EXECERROR = 3` | **#983** / **#1325** (pairwise distance zero) |
| 4 | **dyncge** | **4** × empty-equation-unfixed on **1** pair — `eqpf2.nu_eqpf2` | `SOLVE from line 569 ABORTED, EXECERROR = 4` | **#1331's mechanism**, via twocge — **but no doc of its own** |
| 5 | **lnts** | **NEW — found in this task.** `y.lo = y.up = 0` at `('y2','h50')` and `('y3','h50')` while equations `y_fx_y2_h50` / `y_fx_y3_h50` demand **5** and **45**. A hard contradiction. | **MS-4 Infeasible at ITERATION COUNT 0** | the pruned-instance `.fx` zeroing in `emit_gams.py` (§3) — **no doc of its own** |

**5 eligible against a threshold of 2. Unknown 8.1 is ✅ VERIFIED, and comfortably.**

### 2.2 Rejected — 6, with reasons

| model | rejection reason |
|---|---|
| **agreste** | **New diagnosis required.** MS-5 *Locally Infeasible* after **9,734 PATH iterations** — it reaches PATH and fails numerically, so there is no compile-stage fingerprint to name. No issue doc. **Bank — and flag it as the highest-value banked item:** agreste is `gamslib_type: LP`, `verified_convex`, NLP **MS-1 @ 17706.43**. An LP-derived MCP is a pure LCP; *locally* infeasible is a structurally odd verdict for one, which makes it a promising future diagnosis rather than a dead end. |
| **cesam** | **New diagnosis required.** MS-4 at **0 iterations** — the same signature as lnts, so it was **checked, not assumed**: cesam's emit has **0 `_fx_` equations**, so lnts's contradiction mechanism cannot apply. Different defect; bank. |
| **indus** | **New diagnosis required, and untested per Unknown 1.5.** **31 errors**, spanning `$130` (division not defined for a set), `$140`, `$141`, `$148`, `$149`, `$408`, `$409` — a broad compile failure, not a bounded one. No issue doc. |
| **dinam** | **Untested per Unknown 1.5.** **22 errors** — `$140`×4, `$8`×2, `$171`×2, `$257`. Task 4 established the `$149` cascade has **no landable fix yet**, and 1.5 directs that these be treated as **untested, not pending-unblock**. |
| **turkpow** | **Structurally excluded** by the pre-registered exclusion (ragged `Table mdatat`), and **untested per 1.5**. **14 errors**, including `$149`. |
| **clearlak** | **Structurally excluded** by the pre-registered exclusion (dynamic sets). **8 errors** — `$352`, `$141`, `$257`. |

**Note on the four `$149`-family rejections.** The prompt permits including turkpow and clearlak *if P1's `$149` fix demonstrably unblocks their half*. It does not: Unknown 1.2 found no landable fix, and **1.5 explicitly instructs Task 10 to treat these four as untested rather than pending-unblock.** Counting them would have inflated the pool with models whose unblocking is contingent on a track that has already REPLAN'd.

## 3. The lnts defect — the one new candidate, and its fix surface

**What the emitter does with `.fx`.** A scalar `.fx` at specific labels becomes an **equation + multiplier pair**:

```gams
y_fx_y2_h50.. y("y2","h50") - 5 =E= 0;      *  paired with nu_y_fx_y2_h50
y_fx_y3_h50.. y("y3","h50") - 45 =E= 0;
```

That is the correct design, and the values *are* preserved. **The defect is a second, independent mechanism acting on the same cells** — pruned instances outside the active domain are blanket-zeroed:

```gams
y.fx(c,h)$(not ((ord(c) <= card(c) - 2) and (ord(h) <= card(h) - 1))) = 0;
```

With `card(c) = 4` and `card(h) = 51`, `h50` has `ord(h) = 51`, so `ord(h) <= 50` is false and the guard fires **on exactly the cells the `_fx_` equations constrain**. The variable is pinned to 0 while an equation demands 5 and 45 — PATH declares **MS-4 at iteration 0**, which is the signature of a contradiction found during setup rather than a numerical failure.

**Verified by runtime probe, not by reading the source** (`display y.lo, y.up` immediately before the solve):

```
VARIABLE y.Lo   y2 → h50  0.000        VARIABLE y.Up   y2 → h50  0.000
                y3 → all  0.000                        y3 → all  0.000
```

**Fix surface:** the pruned-instance `.fx` zeroing in `src/emit/emit_gams.py` — the `fix_rhs = "0"` fallback path (around **2952**, with an analogous site near **3012**), which must **skip index tuples that already carry a `<var>_fx_<labels>` equation**. This is structurally the same shape as the Sprint-33 P6 fix, where an emit path had to be taught to skip instances another mechanism already owned.

**⚠ The line numbers above are a hypothesis, not a finding.** The standing cross-sprint lesson is that prep-doc `file:line` fix surfaces were wrong ~4× in Sprint 27. **Day 0 must trace from the emitted line to the producing site** rather than trusting these.

## 4. Unknown 8.2 — the operational criterion, derived from a false positive this task produced

**The prompt's warning is that a fingerprint match can be a false positive** — Sprint 37 Day 0 reported *"✓ `$141` helper `_expr_contains_varref_attribute` present"* when that function had come from `25feacd3`, an unrelated cesam fix (#881) with a near-identical name. Matching the string proved a *component* existed; it was reported as the *cascade* being in place.

**The same trap fired twice inside this task.** Both are recorded because they are what makes the criterion below concrete rather than a slogan.

**(a) A grep that matched the emitter's own comment.** `grep -c 'division by zero'` returns **1** for dyncge, twocge and tricp. None of them has a division-by-zero error. The hit is a **comment in the generated MCP source**:

```
* Initialize variables to avoid division by zero during model generation.
```

A `.lst` file contains the **echoed source as well as the diagnostics**, so an unanchored substring search over it reads the model's own text as evidence about the model's behaviour. Only elec has the real thing — `**** Exec Error at line 99: division by zero (0)`.

**(b) A structural pattern with an 83 % false-positive rate.** Having found lnts's mechanism, the natural next step is to size its reach by scanning for the co-occurrence — a variable carrying **both** a `_fx_` equation and a blanket pruned zeroing. That matches **6 models**:

| model | outcome | verdict |
|---|---|---|
| **lnts** | `model_infeasible` | ✅ the true positive |
| catmix | `model_optimal_presolve` | ❌ false positive |
| otpop | `model_optimal` | ❌ false positive |
| springchain | `model_optimal` | ❌ false positive |
| ganges | `path_syntax_error` | ❌ false positive (and deep-track) |
| gangesx | `path_syntax_error` | ❌ false positive (and deep-track) |

Tightening the pattern to *"and the `_fx_` equation has a **nonzero** RHS"* does **not** help — catmix (`x1` = 1), otpop (`x` = 29.4) and springchain (`x` = 2) all still match. **The discriminator is whether the pruning guard actually covers the fixed tuple, which is a runtime property of `ord`/`card` against the model's own set sizes and cannot be read off the source.** A probe on otpop confirms it directly: `x.lo` is unset at `1974` and `x.up = 32.25` — never zeroed — and the model is **MS-1 Optimal**.

**So: 1 true positive in 6. The static pattern is wrong 5 times out of 6.**

**(c) A third, quieter case — marker counting.** For all four compile-error models, GAMS's own total exceeds the printed `****  $NNN` marker lines **even with zero truncation notices**:

| model | `**** N ERROR(S)` | printed marker lines | truncation notices |
|---|---|---|---|
| clearlak | **8** | 5 | 0 |
| dinam | **22** | 9 | 0 |
| indus | **31** | 25 | 0 |
| turkpow | **14** | 5 | 0 |

This is the Sprint-38 Task-2 lesson generalised: the `$141` retraction was attributed to listing *truncation*, but marker counting undercounts **even when nothing is truncated**, because one printed line can carry several codes. **Read GAMS's own `**** N ERROR(S)` line. Always.**

### 4.1 The operational criterion

**A fingerprint is REPRODUCED only if all four hold:**

1. **The evidence is a GAMS diagnostic, not echoed source.** Match anchored `^\*\*\*\*` listing lines. A `.lst` contains the model's own text; an unanchored substring search over it cannot distinguish the two — trap (a).
2. **A terminal state is asserted**, not just a message: `MODEL STATUS n`, `SOLVE ... ABORTED, EXECERROR = n`, or `**** N ERROR(S)` read from GAMS's own line — never a marker or line count — trap (c).
3. **The mechanism is observed, not inferred from structure.** Where the defect is a runtime property (a guard firing, a bound collapsing), it must be **probed at runtime** — `display var.lo, var.up` before the solve. A source-level pattern is a *hypothesis to test*, and here it was wrong 5 times in 6 — trap (b).
4. **A negative control passes.** At least one model that matches the pattern but does **not** exhibit the defect is probed and shown clean (otpop, above). Without it, a pattern with an 83 % false-positive rate looks like a finding.

**Does the rule as written admit pattern matches?** **Yes — that is the gap.** *"Reproduced fingerprint"* is silent on what counts as reproduction, and every trap above satisfies a plain reading of it. The four criteria are the amendment.

**Every §2.1 entry carries its reproduction command** (§6), and each was run for this catalog rather than quoted from a prior sprint.

## 5. What this means for the sprint — P7 gates P8

**Not one of the 11 candidates has a Phase-0 gate, and 5 have no issue doc at all.** Under Task 9's criterion — an issue without a gate is not implementable under CONTRIBUTING §392–447 — **zero candidates are eligible today**, despite five satisfying the pre-registered rule.

**This makes P7 and P8 a sequence, not two parallel slack items**, which neither priority currently states.

### 5.1 A correction to Task 9's Tier 1

Task 9 built Tier 1 from the *then-assumed* P8 pool. Measured against the actual pool it is wrong in both directions:

| | |
|---|---|
| **Correctly in Tier 1** | twocge (#1331 specifically), tricp (#1062), elec (#983/#1325) |
| **Wrongly prioritised** | **clearlak #1291** and **turkpow #1316** — both **structurally excluded** from P8. Gating them buys P8 nothing; they should drop to Tier 3 priority. |
| **Missing entirely** | **dyncge** and **lnts** — both eligible on the rule, and **neither has an issue doc to gate**. They need a doc *created*, which is more work than gating an existing one. |

**Recommended P7 ordering, which is also P8's shortlist:**

1. **#1331** (twocge) — gate an existing doc; the mechanism is already named
2. **#1062** (tricp) — gate an existing doc
3. **#983 / #1325** (elec) — gate an existing doc
4. **dyncge** — **create** a doc; mechanism shared with #1331, so it can borrow that shape
5. **lnts** — **create** a doc; §3 supplies the KKT shape and the expected emit pattern

**Budget note.** P8 is 12–16 h and P7 8–10 h. Three gates plus two new docs is a real fraction of P7's budget, and it must be spent **before** P8 can start on any of them. If the sprint wants P8 to produce a landing, **P7's first block should be exactly this list** rather than a general backfill sweep.

### 5.2 Honest statement of what P8 is worth

**All five eligible candidates are `path_solve_terminated` / `model_infeasible` models whose emit already succeeds.** A fix moves a model from "aborts at GAMS execution" toward a solve; whether it then *matches* is a separate question none of these has evidence for. **P8's realistic claim is Translate-stable, Solve-uncertain, Match-unclaimed** — worth doing as a slack absorber, not worth putting in a KPI projection. Consistent with Sprint 38 being deliberately not floor-targeted.

## 6. Reproduction

```bash
# Pool query
.venv/bin/python -c "
import json; d=json.load(open('data/gamslib/gamslib_status.json'))
DEEP={'ganges','gangesx','sarf','camcge','turkey','rocket','mine','fawley','markov'}
POOL={'path_solve_terminated','path_syntax_error','model_infeasible'}
for m in d['models']:
    oc=(m.get('mcp_solve') or {}).get('outcome_category')
    if oc in POOL and m['model_id'] not in DEEP: print(m['model_id'], oc)"

# Per-candidate fingerprint — run from a SCRATCH directory, never the repo root
#   (S37 Day 9: GAMS writes scratch files to cwd; a git add -A there swept 20 artifacts)
mkdir -p /tmp/t10/<model> && cd /tmp/t10/<model>
cp <repo>/data/gamslib/mcp/<model>_mcp.gms .
gams <model>_mcp.gms lo=0 errmsg=1

# Criterion 1+2: anchored diagnostics and a terminal state — NOT a marker count
grep -E '^\*\*\*\* [0-9]+ ERROR\(S\)|^\*\*\*\* (MODEL|SOLVER) STATUS|ABORTED, EXECERROR' <model>_mcp.lst

# Criterion 3: the runtime probe (lnts) — insert before the SOLVE, not before the
#   "Solve Statement" comment header
python3 - <<'EOF'
s=open('probe.gms').read(); i=s.index('Solve mcp_model using MCP;')
open('probe.gms','w').write(s[:i]+'display "PROBE", y.lo, y.up;\n\n'+s[i:])
EOF
gams probe.gms lo=0 errmsg=1 && grep -A6 'VARIABLE y.Lo' probe.lst

# Criterion 4: the negative control — otpop matches the pattern and is MS-1 Optimal
```

---

**Document Status:** ✅ Complete — Sprint 38 Prep Task 10. **8.1 ✅ VERIFIED** (**5 eligible** on the pre-registered rule against a threshold of 2 — but **0 eligible** once Task 9's Phase-0 criterion is applied, so **P7 gates P8**) · **8.2 ✅ VERIFIED** (the rule **does** admit pattern matches; four-part operational criterion derived from **three** false positives this task produced, one of them **83 % wrong**).
**Last Updated:** 2026-08-18 · **Owner:** Sprint 38 execution team

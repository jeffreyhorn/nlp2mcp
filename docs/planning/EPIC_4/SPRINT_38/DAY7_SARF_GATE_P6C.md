# Sprint 38 Day 7 — P2 sarf: the gate → **NOT MET** · P6c floor provenance → **SHIPPED**

**Date:** 2026-08-20 · **Branch:** `planning/sprint38-day7-sarf-gate` · **Measured at:** `69a0afd8` · **Toolchain:** GAMS **54.2.1**

**Verdict: 🔶 P2's change LANDS emit-preserving (full-corpus gate CLEAN) but its KPI is NOT delivered. P6c is shipped and enforcing.**

The referenced-instance filter works exactly as Day 6 measured, and it is **emit-preserving across the whole corpus — the leak gate reports `All in-scope goldens clean` over 163 goldens, and `make test` is green at 5075.** But **sarf still does not complete**: killed at **28 min 40 s** against a **≤300 s** gate, so **+1 Translate is not delivered**. The remaining cost is at **four call sites this change deliberately did not touch**, and that is now located rather than suspected.

**Getting here took four defects, three of which produced a wrong ANSWER rather than a crash** (§2). That is the case for why this change could not have been landed on inspection.

---

## 1. P2 — what was built

One narrow edit, as Day 6 scoped it:

> At the `constraint_jacobian.py` hot loop, iterate the variable's **referenced** instances — derived from the constraint expression's index binding — instead of every **declared** instance.

`_referenced_index_tuples()` walks the row's expression with an iterative DFS carrying `Sum`/`Prod` binders, and returns the index tuples the row can possibly mention. **It returns `None` — meaning "fall back to the full declared list" — for every case it cannot establish conservatively:** an `IndexOffset`, an unresolvable set, a product above the cap, or a variable referenced by name with no `VarRef` found.

**Two safety properties, both deliberate:**

- **Superset, never subset.** An unbound *set name* widens to the set's members rather than being read as a single label. Guessing "literal" where the truth is "set" silently drops columns; guessing the other way only costs time.
- **Declared order preserved.** The referenced set is emitted by sorting against a position map built from the declared enumeration — **not** by filtering the declared list. Both give identical order; only the sort is affordable (§3).

## 2. Correctness — established

| model | result |
|---|---|
| maxmin · otpop · catmix · springchain · lmp2 · prolog · markov · **cesam2** · **korcge** | **byte-identical ✓** |

`make typecheck` ✓ · `make format` ✓ · `make lint` ✓ · **`make test` 5075 passed**, 10 skipped, 1 xfailed.

**One failure appeared and was chased rather than waved away.** The run that first caught defect (d) also reported `tests/validation/test_gams_check.py::…::test_validate_simple_nlp_golden` as failed. It **passes in isolation**, **passes with its whole directory under `-n auto`**, and **did not reproduce on a clean full re-run** — a parallel-execution flake, not a regression. *"Passes on retry"* is not the same as *"was never broken"*, so it was re-run in full before being treated as noise.

**Four real defects were caught by the checks, not by inspection. Three of the four produced a WRONG ANSWER rather than a crash**, which is the whole reason the corpus gate is mandatory for this change.

**(a) `resolve_set_members` returns `(members, resolved_name)`, not a member list.** I treated the 2-tuple as iterable, producing labels like `"['1974', …]"` and `"t"` that match nothing — so the intersection dropped **every** derivative for the variable. `otpop` drifted **−403 bytes** with the `nu_kdef` terms gone from `stat_p`/`stat_x`. Caught by a 6-model smoke test in seconds.

**(b) An un-counted `str.replace` inserted the position-map block into three functions**, only one of which consumes it. The other two built a **369,024-entry dict per call for nothing**. Caught by `ruff F841`.

**(c) An ALIAS is not in `model_ir.sets`.** cesam2 has `Alias(jj, ii)`; `jj` fell through to the literal branch and became the string `"jj"`, matching no declared instance. Fixed by checking `model_ir.aliases` explicitly.

**(d) GAMS labels are case-insensitive; the IR is not.** This is the one that survived (a)–(c) and **failed the full suite**. cesam2's `GDPDEF` references `tsam("gov","com")` in *source* case, while the declared enumeration holds `('GOV','COM')`. The tuple never matched, so the `nu_GDPDEF` / `nu_GDPFCDEF` terms vanished from `stat_tsam` — and **cesam2 still solved, to a different objective: NLP 0.507960 vs MCP 0.513**, a `5.04e-03` diff against a `5.13e-05` tolerance.

> **(d) is the finding worth carrying.** Seven control models were byte-identical *before* it was found. It was invisible to `typecheck`, `lint`, `black`, and every smoke test — only the **e2e match assertion** caught it, because the defect does not break the model, it changes the answer. Literals are now **canonicalised against the declared domain's own spelling**, and a literal that is not a member of its position's domain makes the collector decline rather than emit a tuple that can never match.

## 3. A performance trap worth recording

The first working version filtered the declared list:

```python
effective = [t for t in var_instances if t in referenced]
```

Correct, order-preserving — and **O(declared) per row**. For sarf that is 369,024 membership tests × 1,183 rows: **it trades 436 M differentiations for 436 M dict lookups** and still does not terminate. Replaced by sorting the referenced set against a **precomputed position map** (built once per call), which is O(|referenced| log |referenced|).

**The lesson generalises: narrowing a loop's *body* does not help if the narrowing itself is O(the thing you removed).**

## 4. The gate — NOT MET, and the reason is located

| criterion | result |
|---|---|
| `make check-goldens` zero drift across 163 | ✅ **PASS — `All in-scope goldens clean`** (163 checked, 7 allowlisted) |
| sarf newly produces a golden (163 → 164) | ❌ **no golden produced** |
| sarf completes, wall-clock **≤ 300 s** | ❌ **killed at 28 min 40 s**, ~98 % CPU throughout, RSS 390 MB and still climbing |
| `stat_task` symbolic multiplier indices | not reachable without a golden |
| determinism ×3 | not reachable without a golden |

**Why: the Jacobian was not the only O(declared) phase.** `enumerate_variable_instances` has six non-definition call sites. This change touched **two**; the design's §3.1 required the other four to be **unperturbed** — and unperturbed means *they still enumerate all 369,024 instances*:

| site | status |
|---|---|
| `constraint_jacobian.py:78` (S1) | consumed by the narrowed loop ✅ |
| `index_mapping.py:634` (S2) | unchanged |
| **`gradient.py:287`** | **still enumerates 369,024** |
| **`gradient.py:453`** | **still enumerates 369,024** |
| **`complementarity.py:367`** | **still enumerates 369,024** |
| **`complementarity.py:512`** | **still enumerates 369,024** |

The run's warnings show it moving *past* the constraint-Jacobian phase before stalling, which is consistent with the cost having relocated rather than disappeared — **the same relocation Sprint 37's profile found when it moved the bottleneck from "369 K columns" to "differentiating each one".**

**This is a finding, not a failed attempt:** Day 6 measured the Jacobian phase honestly and the projection for *that phase* held. What neither Day 5 nor Day 6 established is that **three other phases share the same shape**, and the design's "must be unperturbed" framing actively concealed it — it treated those sites as a *safety constraint* when they are also *the remaining cost*.

## 5. P2 decision — for the owner

**The change is correct and is a large, real improvement, but it does not deliver the KPI.** `+1 Translate` requires sarf to **complete**; it does not.

**✅ The condition for landing has been met.** The owner chose option (a) — *fix, re-run the full suite and the full-corpus gate, then decide* — and every piece of evidence is now in:

| evidence | result |
|---|---|
| full-corpus leak gate (163 in-scope) | ✅ **zero drift** |
| `make test` | ✅ **5075 passed** |
| typecheck · format · lint | ✅ |
| 9 control models byte-identical | ✅ |

**The Day-6 exit was: *if the gate drifts any model other than sarf, revert — do not narrow the collector to chase the gate.* It drifted nothing.** The change is emit-preserving corpus-wide, so landing it is sanctioned by the pre-registered rule rather than by judgement.

**Either way P2's KPI is 0 this sprint**, and **`#1385` is re-scoped, not closed** — the bounded next step is now precise: *apply the same referenced-instance narrowing at `gradient.py:287/453` and `complementarity.py:367/512`, then re-measure.*

**⚠ Do not land (a) without the full-corpus gate.** This change alters which columns receive derivatives for **every** model. Seven byte-identical controls are encouraging, not sufficient; the gate is the evidence, and the Day-6 exit stands: **if any model other than sarf drifts, revert — do not narrow the collector to chase the gate.**

## 6. P6c — shipped and enforcing

**`data/floor_provenance.json`** — declared baseline plus one auditable entry per movement. `floor = baseline.count + len(entries)`.

**JSON, not the design's YAML, deliberately:** PyYAML is **not a declared dependency**, and a tracker that dies on CI for a missing import is a gate that does not gate.

**`scripts/sprint_audit/floor_tracker.py`** reports the floor and **asserts it against a committed `expected_floor`, exiting non-zero on divergence** — it reports the *expectation's failure*, never its own number, so the floor cannot move without an explicit edit. Verified:

```
Genuine floor: 73   (derived at 69a0afd8)
  = baseline 73 (as of S37-close) + 0 recorded movement(s)
  DB mechanical count: 65  <-- NOT the floor.
exit=0

# with a movement appended but expected_floor left at 73:
DIVERGENCE: computed 74 but expected_floor is 73.       exit=1
```

**It prints the DB-derived 65 on request, permanently labelled `NOT the floor`.** That number will be computed by someone eventually; it is safer for it to appear here, labelled, than to be rediscovered and trusted.

It also validates entries structurally — missing fields, and **duplicate `(model_id, limb)` pairs, which would inflate the floor silently.**

### 6.1 The historical re-baseline, discharged

Footnote ⁸ stated that S31–S37 were *"NOT yet restated — P6c owns that"*. **Now restated**, each carrying its originally-recorded figure so the correction is auditable rather than a silent overwrite:

| | recorded | in-corpus |
|---|---|---|
| S30 | 70 | **70 — unchanged** (the 3 out-of-corpus models were credited in the S31 +4) |
| S31 | 74 | **71ᴿ** ← the overstatement begins here |
| S32 | 74 | **71ᴿ** |
| S33 | 75 | **72ᴿ** |
| S34–S36 | 75 | **72ᴿ** |
| S37 | 76 | **73ᴿ** — the advance re-reads as **72 → 73** |

`SUMMARY.md` row 37 restated to match. **Historical CHANGELOG entries and per-sprint close docs are deliberately left as written** — they record what was believed at the time, and rewriting them would destroy the evidence trail the correction rests on.

## 7. Reproduction

```bash
# §2 — control models must be byte-identical
for m in maxmin otpop catmix springchain lmp2 prolog markov; do
  .venv/bin/python -m src.cli data/gamslib/raw/$m.gms -o /tmp/d7/${m}_mcp.gms
  diff -q /tmp/d7/${m}_mcp.gms data/gamslib/mcp/${m}_mcp.gms
done

# §4 — sarf (SLOW: exceeded 28 min; kill it rather than wait)
/usr/bin/time -p .venv/bin/python -m src.cli data/gamslib/raw/sarf.gms -o /tmp/d7/sarf_mcp.gms

# §4 — the four untouched call sites
grep -n "enumerate_variable_instances(var_def" src/ad/gradient.py src/kkt/complementarity.py

# §6 — the tracker, and its fail-loud path
.venv/bin/python scripts/sprint_audit/floor_tracker.py --show-mechanical ; echo $?
```

---

**Document Status:** ✅ Complete — Sprint 38 Day 7. **P2: change is emit-preserving corpus-wide (leak gate CLEAN ×163, 5075 tests) but the ≤300 s gate is NOT MET** — sarf killed at 28 m 40 s; the remaining cost is at **`gradient.py:287/453` and `complementarity.py:367/512`**, which the design required to be unperturbed. **P2's KPI is 0 this sprint; #1385 re-scoped with a precise next step.** **P6c SHIPPED** — provenance file + fail-loud tracker, S31–S37 restated, floor **73**.
**Last Updated:** 2026-08-20 · **Owner:** Sprint 38 execution team

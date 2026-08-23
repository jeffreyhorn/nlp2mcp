# Sprint 38 Day 9 — P4 close · P6d re-anchor · P8 day 1: **twocge lands, +1 Solve / +1 Match**

**Date:** 2026-08-21 · **Branch:** `planning/sprint38-day9-reanchor-phase0` · **Measured at:** `30be3c05` · **Toolchain:** GAMS **54.2.1** / PATH **5.2.01**

**Verdict: ✅ Sprint 38's FIRST bucket move — and it came from P8, the slack absorber.** `twocge` goes `path_solve_terminated` → **`model_optimal_presolve` + match**: **Solve 108 → 109, Match 94 → 95, all-219 97 → 98.**

**The genuine floor does NOT move.** twocge matched via the **presolve retry**, which this project counts as *methodology*, not genuine. Cold-match stays **65**; the floor stays **73** and `floor_provenance.json` gets no entry.

---

## 1. P4 close + P6d re-anchor — one checkpoint does both

**The design's premise changed, in a useful way.** `MEASUREMENT_INTEGRITY_DESIGN` §5 measured the S37-close anchor as selecting **0 models**, which is why 6d was made *conditional on 6b*: re-anchoring would leave the checkpoint **vacuous** — passing while checking nothing. **Day 8's adoption changed that.**

| anchor | | selects (measured at `30be3c05`) |
|---|---|---|
| `78ceaead` | S34 close — the current, four-sprint-stale anchor | **41** |
| `935d94b7` | S36 close | 24 |
| **`8cffec29`** | **S37 close — the candidate** | **22** |

The 22 are exactly Day 8's newly adopted presolve goldens, so **the first checkpoint at the new anchor doubles as P4's close verification** — it re-solves those 22 and checks their buckets are unchanged.

```
mode: resolve-changed | since: 8cffec29
changed_models: 22 | verdict: GO | rows: 22 | bucket moves: 0
```

Run with **`--min-scope 22`**, so a silently narrowed selection would have failed loudly rather than reporting GO over a subset. **6b is what makes that assertion available**, and the ordering constraint held.

**Cost of re-anchoring, stated:** the S34→S37 drift (now 41 models) stops being re-verified on every checkpoint. That drift is *settled* — each sprint's close confirmed it — so the cost is re-verification of history, not loss of signal.

## 2. P8 — twocge #1331

### 2.1 Fail-before, re-reproduced

```
**** MCP pair eqw.nu_eqw   has empty equation but associated variable is NOT fixed   ×4
**** MCP pair eqpw.nu_eqpw has empty equation but associated variable is NOT fixed   ×4
**** SOLVE from line 692 ABORTED, EXECERROR = 8
gams rc=3
```

### 2.2 The fix — lift a whole-body condition, and only when it is safe to

The emitter already fixes an equality's multiplier where the equation is conditioned away, but it read **only the condition on the equation head**:

```gams
eqpw(i,r,rr)$(ord(r) <> ord(rr))..  pwe(i,r) - pwm(i,rr) =e= 0;   -- handled
eqpw(i,r,rr)..  (pwe(i,r) - pwm(i,rr))$(ord(r) <> ord(rr)) =e= 0; -- twocge: NOT handled
```

The two are semantically identical — the row is empty on the diagonal either way — but the second leaves `eq_def.condition is None`, so the loop skipped it and the emitted model contained **zero** `nu_*.fx(` guards.

**The safety condition is the whole design.** A body condition is liftable **only when it spans the entire side and the other side is zero**:

> If the other side were a non-zero constant, a false condition gives `0 =e= 5` — an **infeasible** row, not an empty one. Fixing the multiplier there would **silently discard a real (if unsatisfiable) constraint** rather than tidy an absent one.

`_whole_body_condition()` therefore returns the condition only for `(expr)$c =e= 0` (either side), and `None` otherwise.

### 2.3 Pass-after

```gams
nu_eqpw.fx(i,r,rr)$(not (ord(r) <> ord(rr))) = 0;
nu_eqw.fx(i,r,rr) $(not (ord(r) <> ord(rr))) = 0;
```

| | before | after |
|---|---|---|
| `gams rc` | 3 | **0** |
| empty-pair messages | 8 | **0** |
| model status | aborted, `EXECERROR = 8` | **MODEL STATUS 1 Optimal** |
| golden | — | **+347 bytes** |

**This exceeds the gate's own expectation.** `ISSUE_1331`'s Phase-0 gate claimed only that clearing the abort would let twocge *reach* PATH, with solve and match **unclaimed**. It solves, and it matches.

### 2.4 The bucket move — and the reading I nearly got wrong

**Pipeline verdict** (`run_full_test.py --model twocge`, its own solve+compare — not a hand comparison):

```
outcome_category : model_optimal_presolve
model_status     : 1 Optimal
objective_value  : 56.7778
comparison_status: match      (diff=0.00e+00, tol=1.14e-01)
```

**⚠ My first, hand-rolled comparison would have reported the wrong reference.** Reading the MCP's objective (55.5085) against the raw model's `SW.l` looked like a match — but **raw twocge contains two solves**, a base case at **55.5085** (line 360) and a counterfactual at **56.7778** (line 367). `SW.l` holds the second. The MCP reproduces the **counterfactual**, which is what the pipeline compares against, and the agreement is exact (`diff=0.00e+00`).

Both readings said "match", so the conclusion would have survived — **but by luck, not method**. The authoritative comparison is the pipeline's, and it is the one recorded.

### 2.5 KPI impact — precise about what did NOT move

| | before | after |
|---|---|---|
| Solve | 108 | **109** |
| Match | 94 | **95** |
| — cold | 65 | **65 (unchanged)** |
| — presolve | 29 | **30** |
| all-219 Match | 97 | **98** |
| `path_solve_terminated` | 4 | **3** |
| **genuine floor** | **73** | **73 — NO CHANGE** |

**twocge matched via the presolve retry**, so under this project's definition it is a **methodology** match, not a genuine one: the cold emit does not reproduce the NLP solution on its own. **`floor_provenance.json` gets no entry, and the floor tracker still reports 73.**

That distinction is the whole reason P6c exists. A mechanical count would have registered this as a floor movement; the provenance file correctly does not.

## 3. Verification

| check | result |
|---|---|
| `make typecheck` · `format` · `lint` | ✅ |
| `make test` | ✅ **5075 passed**, 10 skipped, 1 xfailed |
| 8 control models byte-identical (incl. camcge, cesam2, korcge) | ✅ |
| **leak gate, 186 in-scope** (185 after the §6 revert) | ✅ **all clean** — see §5 (the first run was UNVERIFIED) |
| P4-close checkpoint, 22 models | ✅ **GO, 0 bucket moves** |

**The leak gate is the decisive check, and 8 byte-identical controls are not a substitute for it.** This fix changes emit for *any* equality carrying a whole-body condition against a zero side — a shape that is not confined to twocge. Day 7's case-sensitivity defect was invisible to seven byte-identical controls and surfaced only in the full sweep; the same reasoning applies here.

**⚠ Scope note, and it moved twice in one day.** P4 adopted 22 goldens on Day 8 (163 → **185**); twocge's new **presolve** golden added one (→ **186**, discovered 193); then **`weapons_mcp_presolve.gms` was reverted** (§6), taking it back to **185** (discovered 192). **The leak gate below was run at 186, i.e. with weapons present** — removing a golden cannot introduce drift in the others, so that result subsumes the 185-scope corpus. Any reader comparing against a 163-, 185- or 186-scope run is comparing different sweeps, so each result here states the scope it was measured at.

## 4. The DB was written mid-sprint — deliberately

`run_full_test.py --model twocge` **persists** (unlike the `--resolve-changed` checkpoint, which snapshots and restores). The row is a real measured result, and there is precedent: Sprint 37 wrote the markov row on Day 3.

**It is committed rather than suppressed**, because the Day-10 checkpoint would otherwise report a state that is not true. The Day-13 retest re-solves everything and remains authoritative.

## 5. Results — and the first run was inconclusive, not clean

**Final, unqualified:**

```
Golden staleness: checked 186 in-scope golden(s) (7 allowlisted, 3 workers).
  All in-scope goldens clean.
```

**Zero drift across 186** ⇒ the fix altered **no model other than twocge**. That is the leak claim.

### 5.1 The first run said something weaker, and both signals needed unpacking

```
checked 186 in-scope golden(s)
  TIMEOUT (unverified, soft): turkpow_mcp.gms — slow-emit model
  NO-OP: expected drift on twocge but the emit was byte-identical
  UNVERIFIED: 1 golden(s) timed out — the leak claim is inconclusive.
```

**The `NO-OP` was not a failed fix.** `run_full_test.py --model twocge` **persists goldens** (unlike the `--resolve-changed` checkpoint, which snapshots and restores), so it had already written the post-fix `twocge_mcp.gms` *and created a brand-new `twocge_mcp_presolve.gms`* — twocge now solves via the presolve retry, so it acquires a presolve golden. The gate compared fresh emit against an already-updated golden and correctly reported no drift.

**That also explains the count: 186 in-scope, not the 185 this document was drafted against.** Discovered went **192 → 193**. Any reader comparing against Day 8's 185 is comparing a corpus one golden smaller.

**The `UNVERIFIED` was the real blocker, and it was not waived.** turkpow timed out under 3-way parallelism. Verified **alone** it is clean — but that is a *composed* claim across two runs, and **close rule 1 states that a `PARTIAL`/unqualified-failure verdict fails**. Passing `--allow-unverified` would have been exactly the self-granted exception that rule exists to prevent. The sweep was re-run on a quiet system instead, and turkpow verified within budget.

**Worth carrying:** turkpow is **not allowlisted** and is a known slow-emit model. It verifies at 3 workers on a quiet machine and times out under load — so a leak claim made while other work is running can be inconclusive for reasons that have nothing to do with the change under test.

## 6. `weapons`' presolve golden — REVERTED (owner decision, 2026-08-21)

**Day 8 adopted `weapons_mcp_presolve.gms`; this PR removes it.** Adopting it brought weapons into the **presolve-divergence** check's scope, where it fails CI. Reverting restores the pre-Day-8 state for that one model and prejudges nothing.

**My Day-8 review protocol had a gap.** It checked the warm-start block, agreement with the DB row, the NA-guard and determinism ×3 — but **never that the presolve emit actually runs**. weapons passes every one of those and still aborts.

**What the emit actually does** (run with `cwd` at the repo root, so the `$include` resolves):

| | |
|---|---|
| embedded `$include` NLP | **solves correctly** — MS-2 @ **1735.5696**, matching the reference |
| `Solve mcp_model using MCP` (line 238) | **ABORTED, `EXECERROR = 1`** — no `MODEL STATUS` produced |

**The CI message misattributes it.** `check_presolve_divergence.py`'s first branch returns *"embedded presolve run aborted (EXECERROR) — the `$include` re-run diverged"* for **any** `EXECERROR`. Here the **embedded NLP was fine** and the **MCP** aborted, so the diagnosis points at the wrong half of the file. Recorded for Day 10.

### 6.1 `mcp_file_used` now dangles for weapons — but it already dangled for 13 others

Review flagged that weapons' DB row still carries `mcp_file_used: "data/gamslib/mcp/weapons_mcp_presolve.gms"`, a file this PR deletes. **True, and the fix is not weapons-specific.**

`mcp_file_used` records the presolve artifact the solve **generated and used** (`run_full_test.py:954`, written from `presolve_path` at the moment of the retry). Whether that path *also* happens to be a committed golden is a separate question, settled later by whether anyone adopted it. So the field dangles for every model that solved via presolve without an adopted golden:

| | count |
|---|---|
| rows with `outcome_category: model_optimal_presolve` | **47** |
| of those, `mcp_file_used` points at a **non-existent** file | **14** |
| — pre-existing, and **exactly Day 8's Tier 2** | **13** |
| — added by this PR's weapons revert | **1** |

The 13 are `aircraft`, `apl1p`, `apl1pca`, `china`, `circle`, `imsl`, `lmp2`, `prodsp2`, `ps10_s_mn`, `ps5_s_mn`, `senstran`, `spatequ`, `trig` — precisely the models Day 8 **deliberately did not adopt**. weapons joins an existing class; it does not create one.

**Why weapons' row is NOT edited here.** Both suggested remedies are wrong in this context:

- **Re-classifying `outcome_category` away from `model_optimal_presolve`** would **prejudge Day 10's investigation**, which exists to determine whether these presolve rows are trustworthy at all — and it would move Solve/Match on an assumption rather than a measurement.
- **Removing `mcp_file_used` for weapons alone** would make it **inconsistent with 13 identical peers**, trading a visible dangling pointer for an invisible special case.

**Routed to Day 10**, whose P8 slot is already *"are these presolve rows trustworthy?"* — the dangling-pointer census is the same population, measured the same way. **A systemic fix, if one is wanted, belongs there and covers all 14.**

**And it exposed something larger, which is now Day 10's P8 slot.** The listing contains **exactly one `MODEL STATUS`** — the embedded NLP's. The MCP produced none. Yet the DB records `model_optimal_presolve` + **match** @ 1735.5696, and a fresh pipeline run reproduces it. The mechanism appears to be:

```gams
$include "…/weapons.gms"      * solves the NLP, sets tetd.l
Solve mcp_model using MCP;     * ABORTS — tetd.l untouched
nlp2mcp_obj_val = tetd.l;      * still the NLP's own answer
```

**If the MCP aborts, the objective read returns the NLP's warm-started value and the comparison matches itself.** Whether that affects other presolve models is **measured on Day 10**, not asserted here. **Cold matches cannot be affected — there is no warm start to read back — so the genuine floor of 73 is not at risk either way.**

## 7. Reproduction

```bash
# §1 — anchor selections
for a in 78ceaead 935d94b7 8cffec29; do
  echo -n "$a: "; git diff --name-only $a..HEAD -- data/gamslib/mcp/ \
    | sed 's|.*/||;s|_mcp_presolve.gms||;s|_mcp.gms||' | sort -u | wc -l
done

# §1 — the re-anchored checkpoint, with the scope asserted
.venv/bin/python scripts/gamslib/run_full_test.py \
  --resolve-changed --since-commit 8cffec29 --min-scope 22 --json

# §2 — twocge fail-before / pass-after (from a scratch directory)
gams twocge_mcp.gms lo=0 errmsg=1
grep -c "has empty equation but associated variable is NOT fixed" twocge_mcp.lst

# §2.4 — use the PIPELINE's comparison, not a hand-rolled one:
#   raw twocge has TWO solves (55.5085 base, 56.7778 counterfactual)
.venv/bin/python scripts/gamslib/run_full_test.py --model twocge

# §3 — the decisive gate (run at 186 in-scope; 185 after the weapons revert, §6)
.venv/bin/python scripts/sprint_audit/check_golden_staleness.py --expect-drift twocge
```

---

**Document Status:** Sprint 38 Day 9. **P4 closed** (22 models re-solved, 0 bucket moves) · **P6d re-anchored to `8cffec29`** — no longer vacuous, since Day 8's adoption gives it 22 models to measure · **P8 landed twocge #1331: Solve 108 → 109, Match 94 → 95**, the sprint's first bucket move. **The genuine floor stays 73** — a presolve match is methodology, not genuine.
**Last Updated:** 2026-08-21 · **Owner:** Sprint 38 execution team

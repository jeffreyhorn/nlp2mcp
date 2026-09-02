# Floor-Classification Decision Brief (Sprint 39 P1)

**For:** the owner, Day 0 · **Prepared:** Sprint 39 Prep Task 3, 2026-08-29 · **Measured at:** `8a5a88bc`
**Question:** is the genuine floor **73**, **74**, or **75**?
**Status:** decision NOT taken here. This assembles the evidence, the counter-arguments, and the exact edit each answer implies.

> **The shape of the decision changed during preparation.** The plan and the carryforwards frame this as "73 or 75". Two measurements move it: the counter-argument the plan proposed for 73 is **refuted**, and a distinction the plan did not anticipate makes **74** a live reading. See §3.

---

## 1. What is not in dispute

Both models were re-verified from git and from live runs, not from prose.

| | twocge | elec |
|---|---|---|
| cold golden changed at its landing commit | ✅ `204f35ac`, **+10 / −0** | ✅ `82b91c94`, **+3 / −3** |
| state **before** the fix | `path_solve_terminated`, `solver_version: None` | `path_solve_terminated`, `solver_version: None` |
| state today | `model_optimal_presolve` + **match** | `model_optimal_presolve` + **match** |
| its MCP produces its **own** status | ✅ (attribution run, 34-model population) | ✅ |

`solver_version: None` means each **aborted before PATH ran**. Neither match can therefore be a solver effect or a toolchain artifact, and neither is the `weapons`-style read-back of the embedded NLP's own answer — the full-population attribution run puts both in the "our MCP solved" limb.

**So for both models the written definition's first clause is satisfied: a real emit fix changed the cold emit.**

---

## 2. What the cold emits actually do (measured, not inferred)

Each cold golden was run standalone from a scratch directory, with `display nlp2mcp_obj_val` appended:

| model | cold MODEL STATUS | cold objective | NLP reference | cold match? |
|---|---|---|---|---|
| **twocge** | **1 Optimal** | **55.508** | 56.7778 | ✗ (−2.2 %) |
| **elec** | **1 Optimal** | **244.624** | 243.8128 | ✗ (+0.33 %) |
| **polygon** *(the precedent)* | **5 Locally Infeasible** | — | 0.7797 | ✗ |

This is the fact that explains the DB rows. Both cold emits now *solve* — that is what the fixes bought — but they converge on a **different KKT point** than the NLP optimum, so `_cold_objective_mismatches_nlp` fires and the pipeline retries with the presolve warm start, which matches.

**That is precisely the situation the definition's second clause describes:** *"still genuine if it matches only via the presolve warm-start."*

---

## 3. The counter-arguments, stated fairly

### 3.1 The case for **73** — and why its stated basis fails

The plan's proposed case is that the "still genuine" clause was written for the **polygon/ps2 non-convex** shape, which twocge may not fit. **Checked, and it does not hold:**

| model | convexity | in the 142-model corpus? |
|---|---|---|
| `polygon` | **`likely_convex`** | ✅ yes |
| `twocge` | `likely_convex` | ✅ yes |
| `elec` | `likely_convex` | ✅ yes |
| `ps2_f_s`, `ps2_s`, `ps3_s_gic` | `non_convex` | ❌ **no** |

The precedent is usually written "polygon/ps2", which reads as one non-convex family. It is not. **`polygon` — the only in-corpus member, and the one the definition actually names — is `likely_convex`, exactly like twocge and elec.** The `non_convex` members are `ps2_*`/`ps3_*`, which are the three **out-of-corpus** models the 2026-08-18 re-baseline *removed* (76 → 73) precisely because they were out of scope.

So the convexity distinction cannot separate twocge from the precedent: on convexity, corpus membership, DB outcome and cold-solve failure, twocge and polygon are the same shape.

**A residual case for 73 does exist**, and it is not about convexity: one may hold that *any* model matching only via warm start is methodology, full stop. But that reading **contradicts the written definition**, which explicitly admits the warm-start case as genuine — so taking it means amending the definition, not applying it.

### 3.2 The case for **74** — the distinction the plan did not anticipate

The two cold changes are **not of the same kind**:

| model | what changed in the cold emit |
|---|---|
| **elec** | the **stationarity equations themselves** — `sum(j, sum(j__$(ut(i,i)), …))` → `sum(j__$(ut(i,j__)), …)`; an always-false diagonal guard replaced, and a spurious outer sum removed. A wrong derivative made right. |
| **twocge** | a comment block plus **two `nu_*.fx(...)` guard lines** — `nu_eqpw.fx(i,r,rr)$(not (ord(r) <> ord(rr))) = 0;` and the same for `nu_eqw`. The entire delta is multiplier-fixing for excluded instances. |

**For 74:** elec corrected the mathematics; twocge added MCP-matching *bookkeeping* — fixing multipliers on instances the pairing excludes. One can argue that is a methodological requirement of the MCP encoding rather than a correctness fix, and so is exactly what "methodology" was meant to name.

**Against 74:** those two `.fx` lines are **load-bearing**. Before them twocge aborted (`path_solve_terminated`, no solver); after them it reaches `MODEL STATUS 1`. They are not cosmetic and not byte-identical churn — they *are* the fix. And the definition's methodology test is "cold emit **byte-identical** to pre-fix", which twocge fails.

### 3.3 The case for **75**

Both satisfy the definition as written, on every operative clause: cold emit changed (not byte-identical), model was aborting beforehand, the MCP produces its own status, and the match arrives via the warm start — the case the definition explicitly admits as genuine, with `polygon` as the in-corpus precedent of identical shape.

---

## 4. Is there a third qualifying model? **No.**

Swept every **cold** golden (`*_mcp.gms`, excluding `_presolve`) changed between the baseline anchor `8cffec29` (S37-close) and `9ab2c0c3` (S38-close) — the only period the baseline does not already absorb:

| model | cold changed | pre-fix | today | qualifies? |
|---|---|---|---|---|
| `twocge` | `204f35ac` | `path_solve_terminated` | `model_optimal_presolve` + match | **candidate** |
| `elec` | `82b91c94` | `path_solve_terminated` | `model_optimal_presolve` + match | **candidate** |
| `dyncge` | `82b91c94` | `path_solve_terminated` | `model_optimal` + **mismatch** | ✗ — does not match (the `CASE_B` defect) |
| `tricp` | `45926422` | `path_solve_terminated` | `path_solve_license` | ✗ **today** — see below |
| `ferts` | `45926422` | `path_solve_license` | `path_solve_license` | ✗ — untestable before and after |

**⚠ `tricp` is a conditional future candidate.** Its cold emit changed, it *was* aborting, and the abort is gone — it is blocked only by **capacity** (387 → 1,255 rows, past the demo 1000-row nonlinear limit), not correctness. If the license ask on #1462 succeeds and tricp then matches, it qualifies on the same terms and the floor moves again. **The answer taken today should be recorded as "of the models testable today".**

**Two limits on this sweep, both structural:**

1. **`polygon` has no provenance entry.** `entries` is `[]`; the baseline is a single opaque count of 73. So the precedent the definition names **cannot be audited** — its classification as genuine survives only in prose. That does not make it wrong; it means "polygon set the precedent" is an argument from documentation, not from the provenance file.
2. **A pre-S38 misclassification is not addressable.** The file's own README states the floor "cannot be RECONSTRUCTED" (three derivations give 65, 93, 76), that only 14 of the 76 were ever attributable by name, and that the baseline "is never re-litigated". If the wrong test was applied before Sprint 38, that is invisible and out of scope by design.

Because the sweep found no third instance, **the decision keeps its "append N entries" shape** and does not become "the classification needs re-deriving".

---

## 5. The exact edit each answer implies

### If **73** (no change)
Nothing to edit. Record the decision and the reasoning in `SPRINT_LOG.md`; Sprint 39 opens on 73. **If the reasoning is "warm-start matches are never genuine", the definition itself must be amended** — otherwise the next sprint re-opens this with the same evidence.

### If **74** (elec only) or **75** (both)
Append to `data/floor_provenance.json` → `entries`, **and update `expected_floor` in the same change** (the tracker exits non-zero on divergence — it is designed to fail if a figure moves without its provenance):

```json
{
  "model_id": "elec",
  "limb": "presolve-match-genuine",
  "since_sprint": 38,
  "evidence": "cold emit changed at 82b91c94 (+3/-3): stationarity equations corrected — always-false ut(i,i) diagonal guard replaced by ut(i,j__), spurious outer sum removed. Was path_solve_terminated (solver_version: None, aborting before PATH); now model_optimal_presolve + match. Cold emit reaches MS-1 @ 244.624 vs NLP 243.8128, so the match arrives via the presolve warm start.",
  "pr": "1704"
}
```

```json
{
  "model_id": "twocge",
  "limb": "presolve-match-genuine",
  "since_sprint": 38,
  "evidence": "cold emit changed at 204f35ac (+10/-0): two nu_*.fx guard lines fixing multipliers for MCP-excluded instances. Was path_solve_terminated (solver_version: None, aborting before PATH); now model_optimal_presolve + match. Cold emit reaches MS-1 @ 55.508 vs NLP 56.7778, so the match arrives via the presolve warm start.",
  "pr": "1703"
}
```

`expected_floor`: `73` → **`74`** (elec only) or **`75`** (both).

**Downstream re-baselining** (all four sites, in the same change):

| file | what |
|---|---|
| `data/floor_provenance.json` | the entries above + `expected_floor` |
| `docs/planning/EPIC_4/SUMMARY.md` | row 38's `floor 73 (FLAT as reported — ⚠ arguably 75, owner decision open)` → the decided figure, and row 39's framing of the open decision |
| `docs/planning/EPIC_4/PROJECT_PLAN.md` | the Sprint 39 entry's P1 deliverable text, which currently pre-supposes "re-baselined to **75**" |
| `docs/planning/EPIC_4/SPRINT_39/PREP_PLAN.md` | Task 3's Result, and any acceptance criterion quoting a floor |

> `SUMMARY.md` and `PROJECT_PLAN.md` are **live docs** for `make check-doc-figures`, and `genuine floor` is one of its 11 facts. Once `floor_provenance.json` changes, the check flags any *touched* line still citing the old number — so run it after the edit rather than relying on a manual sweep.

---

## 6. Sprint 39's acceptance criteria under each answer

| | **73** | **74** | **75** |
|---|---|---|---|
| Sprint 39 opens at | 73 | 74 | 75 |
| "no floor regression" means | ≥ 73 | ≥ 74 | ≥ 75 |
| P1's own deliverable | a written decision + a definition amendment (§5) | decision + 1 entry | decision + 2 entries |
| Is a floor *movement* reportable this sprint? | yes, from 73 | yes, from 74 | yes, from 75 |
| Effect on the S38 close record | S38 stays flat | S38 re-reads **73 → 74** | S38 re-reads **73 → 75** |

**Unchanged under all three:** Solve 111, Match 96, Translate 135 — the floor is a separate partition and no bucket moves. **Match may still fall to 95** if P7 reclassifies `weapons`; that is a correction, not a regression, and is independent of this decision.

---

## 7. What this brief does not do

It does not decide. Sprint 38 pre-registered the floor flat at 73, and a +1/+2 discovered by the closer, at close, in the direction the closer would prefer, is exactly the shape a process built on *"an unqualified pass or it is not a landing"* should refuse to self-approve. The measurements above are offered so the decision can be made on evidence rather than on the prose that produced the original mis-classification.

---

**Document Status:** ✅ Complete — Sprint 39 Prep Task 3
**Last Updated:** 2026-08-29

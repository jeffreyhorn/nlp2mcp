# Process-Infrastructure Spec — 8a–8d (P8)

**Sprint 39 Prep Task 11** · **Measured at:** `00f7a105` · **2026-09-02**

The four findings from the Sprint-38 retrospective §7, specified to the point where each can be implemented and tested. **A template change without a test is a suggestion**, so every item below carries a fail-before.

---

## 8a — record the LAYER in a Phase-0 gate, not just `file:line` (Unknown 8.1)

### The motivating incident

**Three of Sprint 38's four gates named the wrong layer**, in their own words:

| gate | named | actually was |
|---|---|---|
| **tricp** #1062 | "the stationarity **head-domain** emission in `src/emit/emit_gams.py`" | a **pre-differentiation IR pass** — `src/kkt/repeated_domain.py`, wired into `cli.py` as step 2.7 |
| **elec** #1325 | `src/emit/emit_gams.py`, variable-initialization emission | **two** defects: `src/ad/derivative_rules.py` `_diff_sum` **and** `src/kkt/stationarity.py` — the doc's own heading reads *"named the wrong layer, twice over"* |
| **dyncge** #1693 | see 8b — it named a layer but asserted the wrong thing about it | — |
| **twocge** #1331 | `src/kkt/assemble.py` + `src/emit/emit_gams.py` | correct as authored |

A `file:line` is a hypothesis that gets *more* wrong as the tree moves; a **layer** is a claim about where the defect lives in the pipeline, and it is falsifiable on Day 0 by a trace rather than after an implementation.

### ⚠ The assumption in 8.1 is wrong on its own numbers

8.1 assumes the field can be added "without invalidating the ~30 gates authored across Sprints 37–38". **Dry-run over the repo: there are 60 Phase-0 gates, and 59 lack a Layer field.** A hard assertion breaks a **required CI status check** on every PR that touches an old gate doc.

```
  gates found                     : 60
  already carry a **Layer:** line : 1   ['ISSUE_1714_dyncge-phantom-indexoffset-stat-pf.md']
  HARD assertion would FAIL       : 59 of 60   <- breaks a required check
  ADDED-only assertion would FAIL : 0 of 60
```

### The spec

**Scope it to added docs. "New" is mechanically determinable and needs no heuristic.**

`.github/workflows/phase0-gate.yml` already collects the PR's files with `github.rest.pulls.listFiles`, whose response carries a **`status`** field (`added` / `modified` / `removed` / `renamed`). Today the workflow writes `f.filename` alone. Writing `f.status + "\t" + f.filename` gives `check_phase0_doc.py` exactly the distinction it needs.

- **Field:** a `**Layer:** <value>` line in the document header, *outside* the `## Phase 0: Acceptance Gate` section.
- **Vocabulary:** `parser` · `IR` · `AD` · `KKT` · `emit` · `pipeline`, compound values allowed with `+`.
  **All four Sprint-38 defects map** — verified: tricp → `IR`, elec → `AD + KKT`, dyncge → `KKT`, twocge → `KKT + emit`. Compound is **required**, not optional: elec and twocge each spanned two layers, and a single-valued field would have forced a false choice. `pipeline` exists for tricp's shape — a pass wired into `cli.py` rather than living inside one stage.
- **Assertion:** a doc whose status is `added` **and** which contains `## Phase 0: Acceptance Gate` must carry a `**Layer:**` line whose value parses into the vocabulary.
- **Rollout:** hard assertion immediately. No warning phase is needed **because the added-only scoping already makes it a no-op on every existing doc** — measured, not assumed.

**⚠ Q4 — no interaction with the existing structural rule.** The checker requires the four canonical `###` subsections to sit *directly* under the `##` header, and any intervening `##` terminates the section. The Layer line is a `**bold**` field in the header block, before the `##`, so it cannot break that rule. `ISSUE_1714` already places it there and passes today.

### Fail-before test

1. A fixture doc with `status=added`, a Phase-0 gate, and **no** Layer line → the check **fails**.
2. The same doc **with** `**Layer:** KKT` → passes.
3. **Negative control:** the same doc with `status=modified` and no Layer line → **passes** (the scoping is what makes this safe; a test that omits it would not detect a hard-assertion regression).
4. A doc with `**Layer:** frobnicator` → fails on vocabulary.
5. **Mutation requirement:** revert the scoping to hard-assert, and test 3 must fail.

## 8b — check whether the logic already exists for another POPULATION (Unknown 8.2)

### The motivating incident

**dyncge #1693's gate asserted new logic was required, and was wrong:**

> *"Detecting this case requires recognising that the equation's LHS and RHS become the same expression under an index identification … which is **new logic rather than a widened condition-lift**."*

The doc now carries its own refutation: the logic **existed in section 2c since #942** and had only ever been applied to *inequalities*. Reusing it inherited its hardening history instead of starting one.

### ⚠ Retro-applied to all four Sprint-38 gates

The 8.2 test is explicit: *a check that would have fired on all four is too broad; one that fires on none is useless.* As a **required template field** it is answered on all four — so the discriminating measure is whether it would have **changed the outcome**:

| gate | what the doc says about existing mechanisms | outcome if the check had been required |
|---|---|---|
| **tricp** #1062 | *"the emitter **already has `__`-aliasing machinery** … so the fix applies existing capability rather than adding a mechanism"* | **already answered, voluntarily** — no change |
| **twocge** #1331 | *"New block **analogous to the #1053 multiplier-widening block**"* | **already answered, voluntarily** — no change |
| **elec** #1325 | silent; the fix was two independent defects, no analogous mechanism existed | fires, answered *"none"* — no change |
| **dyncge** #1693 | asserted **new logic** was needed | **⚠ CAUGHT** — the check forces naming the nearest existing mechanism, and section 2c is exactly that |

**Two of four had already done this unprompted**, which is the strongest argument that the question is natural rather than bureaucratic — it is not new work, it is making an existing habit non-optional. It would have changed the outcome on **exactly one**, the one it exists for. **Q4 answered: no false friction on tricp**, whose gate answered it and still (correctly) needed a new pass.

### The spec

- **Home:** the **Phase-0 template**, not CONTRIBUTING and not the PR checklist. It must be answered when the gate is *authored* — by the time a PR exists the implementation choice is made.
- **Form** — a required line, answerable in one sentence, and **"none" is a valid answer**:

  > **Nearest existing mechanism:** `<file:symbol>` — `<what population it currently serves>` — **reused** / **not applicable because …**

- **Why this form:** it cannot be answered "yes" vacuously. Naming a *file and symbol* and *its current population* is the work; noticing that section 2c served inequalities is precisely what would have prevented dyncge's assertion.

### Fail-before test

Assert the field is **required in the template** and that `check_phase0_doc.py` rejects a gate without it — same added-only scoping as 8a. **The retro-application above is the evidence that it discriminates**; a unit test cannot establish that, and pretending otherwise would be the "green test proves nothing" failure this repo has already shipped three times.

## 8c — stop pre-registering close rules against UNSTARTED tracks (Unknown 8.3)

### The motivating incident

Sprint 38's close rule #2 was written around P1's cascade. **P1 was REPLAN'd on Day 1.** A sound rule then went unmet for reasons unconnected to the close, and the closeout had to explain a miss that was not one.

### The spec — and the escape-hatch test

Each pre-registered close rule carries an explicit **precondition**, so *unmet* is distinguishable from *missed*:

> **Rule:** `<the assertion>`
> **Precondition:** `<the track state this rule presumes>`
> **If the precondition fails:** the rule is **VOID, not unmet** — and the closeout records which precondition failed and why.

**Q5 — the escape-hatch risk is real, so the rule is constrained:**

1. **A precondition may only reference a track's *start* state, never its outcome.** "P1 landed" is forbidden; "P1 was started" is allowed. An outcome-conditioned rule is a rule that excuses its own failure.
2. **Preconditions are fixed at pre-registration** and cannot be added or edited after Day 0. A precondition invented at close is an excuse.
3. **A voided rule is reported, not dropped** — the closeout states the rule, the precondition, and the fact it did not apply.

**Applied to Sprint 39's two pre-registered close rules:**

| rule | precondition | escape-hatch check |
|---|---|---|
| `path_solve_terminated` **maintains 0** | **none** — it is a corpus-wide invariant, independent of every track | ✅ cannot be voided, therefore cannot be gamed |
| **Match may fall to 95**, reported as a correction | **P7 started** | ✅ references a *start*, not an outcome. If P7 is never started, Match stays 96 and the rule is void — which is correct, not an excuse |

**Note the asymmetry:** the first rule takes **no** precondition. If every rule needed one, the mechanism would be an escape hatch by construction. That one of two needs none is the evidence it is not.

## 8d — re-derive a carried package's EVIDENCE at use time, not only its conclusion

### The motivating incident

The rocket consultation was carried five sprints. Prep re-verified its *conclusion* (still MS-5) and stamped the toolchain — but not its *failure description*, which had become wrong: `EXIT — other error` had become `Normal Completion` + MS-5 after 9,241 iterations. **The conclusion survived; the evidence rotted underneath it.**

**Corollary, from the same incident:** an internal planning doc is not an external deliverable. The package sent to the PATH authors needed a separate extract, not a link to a sprint doc.

### The spec (CONTRIBUTING rule)

> **Carrying a package across a sprint boundary.** Before a banked package is *used* — sent, implemented, or quoted — re-derive **every figure in it**, not just the verdict it supports. Record the commit and toolchain each figure was measured at.
>
> **The test is: could this figure be wrong while the conclusion stays right?** If yes, it must be re-measured. A conclusion that survives is not evidence that its supporting numbers did.
>
> **And an internal planning doc is not an external deliverable.** Anything leaving the repo gets a written extract, so the audience is not asked to read around sprint bookkeeping.

**This is already load-bearing in Sprint 39.** Task 9 re-measured all three consultation threads and found the banked figures reproduce **but come from different emits** — rocket's 9,241 is its presolve emit, agreste's 9,734 and mine's 10,662 are cold. The conclusion ("all three still fail") was right; the package could not say which file to apply a fix to. **That is 8d catching something, in prep, before the 2026-09-09 gate.**

### Fail-before test

Not mechanizable, and saying so is the honest answer. **The enforcement is the Task-9 shape**: a carried package's re-measurement is a *deliverable* of the task that uses it, with each figure carrying its commit — which is checkable in review. `make check-doc-figures` already enforces the adjacent property for the 11 facts it derives; extending it to arbitrary banked figures would require those figures to have machine-derivable sources, which they do not.

---

**Document Status:** ✅ Complete — Sprint 39 Prep Task 11
**Last Updated:** 2026-09-02

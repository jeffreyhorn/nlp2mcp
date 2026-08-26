# Sprint 38 — Retrospective

**Weeks 41–42 · Closed 2026-08-26 at `8e32be09`** · Anchor `8cffec29`

---

## 1. What the sprint actually did

**It cleared a failure category.** `path_solve_terminated` held four models at S37 close and holds none now: `Solve 108 → 111`, `Match 94 → 96`, `all-219 97 → 99`. Three of the four were fixed by real emit changes; the fourth (`tricp`) was fixed and then hit the demo licence wall.

**It was not floor-targeted, and the plan said so in every acceptance column.** That was the right call: it removed the pressure that produced Sprint 36's reverted landing attempt, and the sprint still produced the largest bucket movement since Sprint 28.

**The irony is that it may have moved the floor anyway** — §4.

## 2. The thing worth generalising: gates got the LAYER wrong, three days running

Four Phase-0 gates named a fix surface. **All four were wrong, and in two different directions.**

| day | model | gate said | actually |
|---|---|---|---|
| 11 | tricp | head-domain emission in `emit_gams.py` | `domain=var_def.domain` in `stationarity.py` — **and the body is built positionally from the same tuple**, so a head-only rename would still bind `n` twice. The collapse also reached *back* before KKT assembly, corrupting the objective gradient. Fix: a **pre-differentiation IR pass**. |
| 12 | elec | "the stationarity term-assembly" | **two** defects: one in `src/ad/derivative_rules.py` (upstream of stationarity entirely), one in a *different function* of `stationarity.py`. |
| 12 | dyncge | "requires **new logic** rather than a widened condition-lift" | **over**-scoped — section 2c had performed exactly that diagonal-triviality test since #942; it was only ever *applied to inequalities*. |

**Three under-scoped by naming the emitter for defects decided upstream; one over-scoped by demanding new machinery for logic that already existed.** The standing rule ("prep-doc `file:line` fix-surfaces are hypotheses") held, but it under-describes the failure: the error was not the *line*, it was the *layer*.

**Two operational corollaries, both cheap:**

1. **Re-trace from `stationarity.py` and the AD entry points outward, not from the emitter inward.** The emitter is where a defect becomes *visible*, which is why it keeps getting named, and rarely where it is *decided*.
2. **Before writing new emit logic, check whether the logic exists for a different population.** dyncge cost ~40 lines of extraction instead of a new mechanism, and inherited three issues' worth of hardening for free.

## 3. A defect class that bit twice in two days from different angles

**A repeated symbol in a *declaration* domain is harmless until something resolves an index "positionally against the declared domain."**

- **tricp** — `slp(n,n)` as a **variable** domain. GAMS declares the full `n × n` product, but an equation *definition* with a repeated controlling index binds to the same element ⇒ the head generated **zero rows** ⇒ 108 unmatched columns.
- **elec** — `Set ut(i,i)` as a **set** domain. `_replace_indices_in_expr` resolved a bound sum index positionally against it, and since both declared positions are `i`, the guard collapsed to `ut(i,i)` — the diagonal of a *strictly upper-triangular* set, identically false, **silently dropping half the gradient**.

Neither produced a crash at the point of the defect; both produced a wrong answer that surfaced far away. **The remaining positional-vs-declared-domain resolutions in `stationarity.py` are worth an audit** — that is a bounded, well-specified piece of work and it is in the carryforwards.

## 4. The floor question, and why it is being handed up rather than decided

Two models — `twocge` and `elec` — had their **cold emit changed** by a real fix, both now match, and both were **aborting beforehand**, so neither match is a solver effect. The written definition classifies *methodology* as "cold emit **byte-identical** to pre-fix". Neither is. **Under the definition as written, the floor is 75, not 73.**

**Day 9 recorded twocge as methodology using the wrong test** — "it matched via the presolve retry". The definition turns on whether the *cold emit* changed, not on how the match was obtained; the precedent model it names (`polygon`) has the identical DB shape today. Day 12 inherited that reasoning for elec without re-checking it.

**Why it was not simply applied at close.** The plan pre-registered flat-73. A +2 discovered by the closer, at close, in the direction the closer would prefer, is precisely the shape that a process designed around *"an unqualified pass or it is not a landing"* should refuse to self-approve. So the close reports **73 from the provenance file** — which is what close rule #3 mandates — and flags the discrepancy as the first item in the carryforwards.

**The honest reading is that the floor rule worked and the classification did not.** P6c's provenance file did exactly its job: it made the floor auditable enough that a mis-classification was *findable*. Under the old hand-partition this would have been invisible.

## 5. What went well

- **Every landing was leak-gated unqualified** — four PASSes at 185/185/186/186, and on Day 11 **both** drifting models were declared *before* the gate ran rather than rationalised after.
- **The residual harness earned its keep three times.** `CASE_A` is what separated elec's fix from a coincidence; `CASE_B` is what stopped dyncge being booked as a Match; `CASE_C_OBJDEF` is what corrected rocket's own consultation document.
- **Day 10's spurious-match investigation reported a finding rather than a correction.** One of 33 presolve matches is spurious; it was measured, scoped ("cold matches unaffected, floor unaffected either way"), and handed to the owner un-edited. That is the discipline working.
- **The consultation went out after five carries.** The blocker was never technical — it was that no one had named a recipient.

## 6. What did not

- **P1 ganges consumed Day 0 and Day 1 and produced no landing** — correctly, since #1668 direction 1 is a measured no-op and direction 2's information is absent at the site. But close rule #2 was written around P1's cascade, so a pre-registered rule went unmet because its precondition never occurred. **Pre-registering a rule against a track that has already been carried four times is a bet, and this one lost.**
- **P2 sarf landed emit-preserving but undelivered** — 28 m 40 s against a ≤300 s gate. The change is correct and in `main`; the KPI is not. Called a carryforward with a bounded next step, not a partial win.
- **lnts was never reached.** Day 12's budget went to elec and dyncge, both of which ran long because each turned out to be two defects rather than one.
- **A five-times-carried package rotted in place.** At send time the prepared failure description no longer reproduced. Prep had re-verified the *conclusion* and stamped the toolchain — but not the *description*. **Re-measure at the moment of use, not only at authoring.**

## 7. Process changes to carry into Sprint 39 prep

1. **Trace fix surfaces from the AD/KKT entry points outward**, and record the *layer* in the gate, not just the file:line.
2. **Add a "does this logic already exist for another population?" check** before authoring new emit logic.
3. **Audit the positional-vs-declared-domain resolutions** in `stationarity.py` — a known defect class with two instances in two days.
4. **Stop pre-registering close rules against unstarted carryforward tracks.** Rule #2 was sound and unmet for reasons that had nothing to do with the close.
5. **Re-derive a carried package's evidence at send/use time**, not only its conclusion.

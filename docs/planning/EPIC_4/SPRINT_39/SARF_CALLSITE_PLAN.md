# sarf's Four Call Sites — Cost Attribution & Atomicity Plan (P4)

**Sprint 39 Prep Task 6** · **Measured at:** `6b58d0ca`, GAMS **54.2.1** · **Authored:** 2026-08-31

> **⚠ Headline: the premise behind P4's 20–28 h estimate does not survive measurement.** The four call sites are still exactly where Sprint 38 Day 7 recorded them — and they account for **0.5 %** of wall-clock, not the bulk. One of the four is **dead code in the translate path**. This is reported now, before the sprint, because it changes the estimate.

---

## 1. The four sites — located by symbol (Unknown 4.1 ✅)

| site | enclosing function | status |
|---|---|---|
| `src/ad/gradient.py:287` | `compute_objective_gradient` | at recorded line |
| `src/ad/gradient.py:453` | `compute_gradient_for_expression` | at recorded line — **but see §4** |
| `src/kkt/complementarity.py:367` | `build_complementarity_pairs` | at recorded line |
| `src/kkt/complementarity.py:512` | `build_complementarity_pairs` | at recorded line |

Neither file has changed since the Day-7 anchor `949a4587` (**0** commits each), so the "located, not suspected" claim holds *for location*. `stationarity.py` (2 commits) and `emit_gams.py` (4) did change, but hold none of the four.

**There are six callers of `enumerate_variable_instances`, not four.** The other two — `src/ad/constraint_jacobian.py:80` and `src/ad/index_mapping.py:634` — are the ones the Day-7 referenced-instance filter already covers. That is consistent with "four *untouched* sites", but the phrase is easy to misread as "four sites total".

## 2. Cost attribution — by measurement (Unknown 4.2 ❌ **WRONG**)

Capped profile, 900 s, `cProfile`, sarf did **not** finish:

| frame | cumulative | % | ncalls |
|---|---|---|---|
| `compute_constraint_jacobian` | **637.9 s** | **70.9 %** | 1 |
| `differentiate_expr` | 572.2 s | 63.6 % | 1,031,810 |
| `_diff_binary` | 565.4 s | 62.8 % | 1,031,810 |
| `_compute_inequality_jacobian` | 532.7 s | 59.2 % | 1 |
| `_diff_sum` | 513.6 s | 57.1 % | 1,641,023 |
| `_is_concrete_instance_of` | 306.2 s | 34.0 % | **13,344,770** |
| `resolve_set_members` | 165.0 s | 18.3 % | **13,348,120** |
| `compute_objective_gradient` | 156.9 s | 17.4 % | 1 |
| **`enumerate_variable_instances`** | **4.4 s** | **0.5 %** | **40** |

**The four sites are enumeration points costing 0.5 % across 40 calls. The cost is differentiation.** `build_complementarity_pairs` does not appear in the top twelve at all.

**⚠ The correction routed here by Task 2 is also wrong, and its failure mode is worth keeping.** Task 2 reported the hot path as `enumerate_equation_instances`; at this cap it costs **0.329 s over 82 calls — 0.04 %**. Task 2's cap was shorter, and the run was still *inside* equation enumeration when it stopped, so the deepest live frame read as the cost. **A capped profile's top frame tells you where the run is, not where the time goes**; a cumulative attribution needs the phase to have completed, or a cap chosen past it. Both the original assumption and its correction placed the cost at an *enumeration* function. Neither did.

**The charitable reading — that the four *emit* the instances later differentiated — does not hold either.** `compute_constraint_jacobian` (70.9 %) takes its columns from `constraint_jacobian.py:80`'s `var_instances_cache`, which is **not** one of the four and which the Day-7 filter already narrows (`_REFERENCED_TUPLE_CAP = 200_000`; sarf's worst row is 51,840, so the filter does engage). Narrowing the four would leave the dominant path untouched.

**What the four could still reach:** `compute_objective_gradient` at 17.4 %. That is the honest upper bound on P4's lever as currently scoped — assuming the whole of it were eliminable, which it is not.

**Per-column vs per-row.** The prompt asks to keep these apart, and the measurement does: the blow-up is per-**column** differentiation *inside* the Jacobian (1,183 rows × columns), reached through `_diff_sum`. The 1,183 rows are untouched by the O(active) argument and remain a floor on the work.

## 3. The O(active) projection (Unknown 4.3 🔶 **PARTIALLY WRONG**)

Claimed: 1,183 rows × 398 active columns = **470,834** differentiations at **3,343/s** ⇒ **141 s**. The arithmetic is correct.

**The rate survives.** Measured 1,031,810 `differentiate_expr` calls in 900 s = **1,146/s profiled**. `cProfile` typically costs 2–4×, which brackets the claim:

| assumed overhead | implied true rate | time for 470,834 diffs |
|---|---|---|
| 2× | 2,293/s | 205 s |
| **3×** | **3,439/s** | **137 s** |
| 4× | 4,586/s | 103 s |

**The scope premise does not survive.** The run performed **1,031,810** differentiations — **2.2× the projection's entire budget** — and had not finished. So the code today does not differentiate only 470,834 times; the 398-active-column figure describes a state the narrowing is meant to *produce*, not one it has been shown to reach.

**Consequence for the ≤300 s gate:** the gate was revised to 300 s *because of* this projection (owner decision, 2026-08-18). The projection's rate is intact, so the gate's headroom is intact **if** the narrowing achieves 398 active columns. That conditional has never been tested, and it is the whole estimate.

## 4. ⚠ One of the four sites is dead code in the translate path

`gradient.py:453` sits in **`compute_gradient_for_expression`**, whose only references are its own docstring example and `tests/integration/ad/test_gradient.py`. **No production caller.**

Verified independently by instrumenting all four sites and running a translate: it never fires (§5).

So P4's lever is **three live sites**, not four — and narrowing the dead one changes nothing at any size.

## 5. Surrogate fixture (Unknown 4.4 🔶 **PARTIALLY WRONG**)

**sarf cannot be its own fixture** — at 369,024 declared `task` columns (99.96 % of its 369,165 total) the fail-before state does not terminate.

A corpus-free surrogate was **built and verified**, not merely specified — `task(g,t,mn,mn)` at 2×3×4×4 = **96** columns, preserving sarf's shape (4-D variable with a **repeated declaration index**, driven by an objective and an inequality):

```gams
Set g / g1*g2 /, t / t1*t3 /, mn / m1*m4 /;
Alias (mn, mn2);
Variable task(g,t,mn,mn), emply(t), profit;
Positive Variable task, emply;

* per-element bound OVERRIDES — required to reach complementarity.py:367 / :512
task.lo('g1','t1','m1','m1') = 0.5;
task.up('g1','t1','m1','m2') = 9.0;
emply.lo('t1') = 0.25;
emply.up('t2') = 8.0;

Equation objdef, cap(t), link(g,t);
objdef..    profit =e= sum((g,t,mn,mn2), task(g,t,mn,mn2)) - sum(t, emply(t));
cap(t)..    sum((g,mn,mn2), task(g,t,mn,mn2)) =l= 10 * emply(t);
link(g,t).. sum((mn,mn2), task(g,t,mn,mn2)) =g= 1;
```

**The two-line declaration form is valid GAMS, and that was checked rather than assumed.** Review flagged `Variable task(...)` followed by `Positive Variable task, emply` as a probable symbol-redefinition error. It is not: re-typing an already-declared variable is legal, and **GAMS 54.2.1 compiles this file with 0 compilation errors** (`COMPILATION TIME = 0.005 SECONDS`, no `$` codes). nlp2mcp reads it the same way — the emit declares `Variables profit;` and `Positive Variables task(g,t,mn,mn__), emply(t), …`, so the re-typing is carried through, not dropped.

**What the surrogate is for, stated precisely.** It is a **translate-path** fixture: the assertion is on the *emit*, and on which of the four sites execute while producing it. It is deliberately **not** a solve fixture — as an NLP it is **unbounded** (`MODEL STATUS 3`, CONOPT reaching infinity on `task`), because `cap(t)` ties `sum(task)` to `10·emply(t)` while only `emply.up('t2')` is bounded. That is irrelevant to the fixture's purpose and is recorded here so "built and verified" is not read as "solves cleanly end to end".

Instrumented site coverage:

| site | hits | note |
|---|---|---|
| `gradient.py:287` | 3 | |
| `complementarity.py:367` | 2 | needs per-element `.lo` overrides — a first surrogate without them missed it |
| `complementarity.py:512` | 2 | needs per-element `.up` overrides |
| `gradient.py:453` | **0** | **unreachable — dead code (§4)** |

**"Hits all four" is unachievable by construction, not by fixture design.** Three of four is the maximum, and that is a property of the code rather than of the surrogate.

**Scope 186 → 187:** unchanged as a target — it depends on sarf newly producing a golden, which depends on the ≤300 s gate being met.

## 6. Atomicity plan

**The unit.** All narrowing of live enumeration sites must land together with the Jacobian-side column selection. A partial landing produces an **inconsistent MCP**, not partial progress: if `compute_objective_gradient` narrows to active columns while `compute_constraint_jacobian` retains declared columns, the gradient vector and the Jacobian are indexed over **different column sets**, and the emitted stationarity rows pair multipliers against columns that the other half never created. That is a silently wrong model, not a slow one.

**Corpus-safety sites that must be provably unperturbed** — every remaining caller of `enumerate_variable_instances`:

- `src/ad/index_mapping.py:634` (`build_index_mapping`) — assigns `col_id`s; changing its enumeration renumbers **every** column in **every** model
- `src/ad/constraint_jacobian.py:80` — the Day-7 filter's own cache
- the two live complementarity sites, if the narrowing does not include them

**Proof obligation:** `make check-goldens` at full scope, clean, **plus** sarf newly producing a golden. `make leak-check MODEL=sarf` reports `NO-OP` because sarf has no golden — it is not the gate.

**The Day-7 trap, not to be rediscovered:** the first narrowing attempt **traded 436 M differentiations for 436 M dict lookups** and still did not terminate. *Narrowing a loop's body does not help if the narrowing is itself O(the thing removed).* Any candidate must be costed against that.

## 7. Restated Phase-0 gate

| criterion | requirement |
|---|---|
| wall-clock | **≤ 300 s** on a nightly slot |
| golden | byte-stable; sarf newly produces one (scope **186 → 187**) |
| symbolic indices | no set-name-literal multiplier index — see below, **and run its positive control** |
| determinism | ×3 `PYTHONHASHSEED`, byte-identical |
| leak gate | `make check-goldens` full scope clean |
| fail-before | capped translate does not terminate (**confirmed at 900 s**) |

### The symbolic-index check, and why it is not in the table

⚠ **This command must not live in a table cell.** An earlier revision of this document put it there and escaped the alternation to stop the pipe from splitting the cell — producing `grep -E 'nu_…\("\|lam_…\("'`. In ERE `\|` is a **literal pipe**, so the pattern no longer means "nu\_ *or* lam\_"; it means the single string `nu_x("|lam_y("`. Verified: against a line containing both `nu_eqfoo("AGR")` and `lam_bar("LAB")` the escaped form exits **1** and prints nothing — the gate reports "empty" and **passes on the exact defect it exists to catch**. Every other copy of this check in the repo (`PROJECT_PLAN.md`, `SPRINT_32`–`SPRINT_34`) has the correct unescaped form; only the table cell was corrupted, **by the act of putting it in a table**.

```bash
# The check. Must print nothing.
grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms

# POSITIVE CONTROL — run this FIRST, every time. It must print the line.
# A silent grep is indistinguishable from a broken grep, which is how the
# escaped form survived: "empty" looked like a pass.
printf 'stat_x(i).. nu_eqfoo("AGR") + lam_bar("LAB") =E= 0;\n' \
  | grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("'
```

The failure this guards is the Sprint-26 `nu_slack("srn")` regression (commit `243fe578`).

**REPLAN exit — timeout re-trigger.** If a candidate narrowing still exceeds 300 s, **stop and re-attribute rather than iterating**. §2 shows the dominant path is one the Day-7 change already touched, so a second timeout is evidence the lever is in `compute_constraint_jacobian`/`_diff_sum`, not in enumeration — a different piece of work with a different estimate, and it should be re-scoped rather than absorbed.

## 8. What this means for P4's estimate

P4 is Sprint 39's **only KPI mover** (+1 Translate → 136), and its 20–28 h assumed the remaining cost was located at four sites. Measurement says those sites are 0.5 % of wall-clock, one of them is dead, and 70.9 % sits in a path Day 7 already changed.

**This is a finding for the owner, not a decision taken here.** The options — re-scope P4 onto the differentiation path, keep it as scoped with a much smaller expected gain, or defer — differ in cost and in KPI consequence, and the sprint's only KPI mover is not something prep should silently re-aim.

---

**Document Status:** ✅ Complete — Sprint 39 Prep Task 6
**Last Updated:** 2026-08-31
